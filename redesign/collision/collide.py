"""collide.py - mesh-level interference check: no two parts of K09-L may occupy the same space ("phasing"), so the
assembly can go into a rigid-body physics simulator as it is. Runs Blender 4.2 in the background.

    python -I redesign/collision/collide.py              # flight assembly, static pose, plus elevon sweep
    python -I redesign/collision/collide.py --transport  # also the aircraft in its transport box (ground items)
    python -I redesign/collision/collide.py --blender PATH --tol-mm 0.05

What it proves (for the stub-backend geometry, the same bodies the GLB and the shop STLs are made from):
  * every pair of DIFFERENT parts whose bodies penetrate each other deeper than --tol-mm is listed with the depth,
    where, and the bodies involved. Depth = the deepest point of either surface inside the other solid, sampled on
    every triangle where the two surfaces cross (15 points per triangle). Faces that only touch (bond lines, seated
    hardware) measure ~0 and pass: contact, not penetration, is what a rigid-body physics engine needs. The default
    0.05 mm absorbs the chord error of two tessellations of one curved bonded face (a skin on its core).
  * a body wholly inside a body of another part (no surface crossing) is caught by a point-in-mesh test.
  * elevon sweep: every revolute joint with limits is turned to each limit and the moved parts are re-checked against
    everything that did not move (the elevon panel group swings about its hinge).
Bodies of the SAME part may overlap (they are united into one solid); mass proxies (harness bundles, drawn as
nothing) and wires (centre lines) are not solids and are skipped.
Does NOT prove: the real Fusion kernel geometry (UNVERIFIED-IN-FUSION), clearance margins (a 0.05 mm gap passes),
or the four-bar pushrod / servo-arm path through the sweep (they are held at neutral and listed as not swept).

Writes redesign/collision/out/REPORT.md and report.json. Exit 1 when any overlap is above the tolerance.
"""
import argparse
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
for _p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'manufacturing')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cad_source as cs           # noqa: E402

DEFAULT_BLENDER = 'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe'   # inputs/SIM-TOOLS.md


def find_blender(arg):
    for c in (arg, os.environ.get('BLENDER'), shutil.which('blender'), DEFAULT_BLENDER):
        if c and os.path.exists(c):
            return c
    sys.exit('collide: Blender not found (pass --blender PATH or set BLENDER)')


def rot_about(axis, origin, deg):
    """4x4 row-major rotation by deg about the line through origin along axis (Rodrigues)."""
    n = math.sqrt(sum(a * a for a in axis))
    ux, uy, uz = (a / n for a in axis)
    c, s, C = math.cos(math.radians(deg)), math.sin(math.radians(deg)), 1 - math.cos(math.radians(deg))
    R = [[c + ux * ux * C, ux * uy * C - uz * s, ux * uz * C + uy * s],
         [uy * ux * C + uz * s, c + uy * uy * C, uy * uz * C - ux * s],
         [uz * ux * C - uy * s, uz * uy * C + ux * s, c + uz * uz * C]]
    o = origin
    t = [o[i] - sum(R[i][j] * o[j] for j in range(3)) for i in range(3)]
    return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]], [0, 0, 0, 1]]


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def axis_vec(ax):
    if isinstance(ax, str):
        return {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}[ax.upper()]
    return tuple(ax)


MOVE_VIA = ('CT-EPOXY', 'CT-CA', 'CT-HW-SEATED', 'CT-M2-SCREW-PLASTIC', 'CT-TAPE-FOAM')   # bonds that carry motion
# flexible parts: they bend with a joint instead of moving rigidly; a rigid-body simulator represents them by the joint
# itself (the hinge tape IS the elevon hinge, E-WNG-04..07). Held out of the sweep pairs and listed.
FLEXIBLE = ('MEC-010-',)


def moving_groups(ctx, edges):
    """Revolute joints with limits -> (joint, parts that turn with part a). A part turns with a when it is joined to a
    (or to a part already turning) by a rigid joint or a bonded / seated edge, unless it also has an edge to the
    fixed part b (a hinge tape, the skin): that part bridges the joint and is held out (listed as linked)."""
    nb = {}
    for j in ctx.joints:
        if j.kind == 'rigid':
            nb.setdefault(j.a, set()).add(j.b)
            nb.setdefault(j.b, set()).add(j.a)
    touch = {}
    for e in edges.values():
        a, b = e.get('part_a'), e.get('part_b')
        touch.setdefault(a, set()).add(b)
        touch.setdefault(b, set()).add(a)
        if e.get('via') in MOVE_VIA:
            nb.setdefault(a, set()).add(b)
            nb.setdefault(b, set()).add(a)
    out = []
    for j in ctx.joints:
        if j.kind != 'revolute' or not j.limits:
            continue
        grp, todo = {j.a}, [j.a]
        while todo:
            p = todo.pop()
            for q in nb.get(p, ()):
                if q in grp or q == j.b or j.b in touch.get(q, ()):
                    continue
                grp.add(q)
                todo.append(q)
        out.append((j, grp))
    return out


def jobs_for(ctx, include_ground):
    comps, skipped = [], []
    for pid, comp in sorted(ctx.components.items()):
        if comp.proxy or not comp.shapes:
            skipped.append((pid, 'mass proxy' if comp.proxy else 'no bodies'))
            continue
        if not comp.flight and not include_ground:
            continue
        comps.append({'id': pid, 'sub': comp.subsystem, 'flight': bool(comp.flight), 'matrix': comp.matrix(),
                      'bodies': [cs.shape_to_json(s) for s in comp.shapes],
                      'cuts': [[cs.shape_to_json(s), M] for s, M in comp.world_cuts()]})
    return comps, skipped


def poses(ctx, comps, edges):
    """Static pose, then every limited revolute joint at its lower limit together, then at its upper limit (the
    elevon panels of one side are bridged and move as one; the two sides are far apart). Each pose:
    (name, {part: 4x4 world matrix}, {part: 4x4 motion}, moved, linked)."""
    by_id = {c['id']: c for c in comps}
    out = [('static', {}, {}, None, None)]
    groups = moving_groups(ctx, edges)
    if not groups:
        return out
    moved_all = set().union(*(g for _j, g in groups))
    # parts joined to a moving group from outside it (pushrod clevis on the horn, hinge tape, skin) follow a path
    # this check does not model: held out of the pose's pairs and listed
    linked = sorted({q for e in edges.values() for p, q in ((e.get('part_a'), e.get('part_b')),
                                                            (e.get('part_b'), e.get('part_a')))
                     if p in moved_all and q not in moved_all and q in by_id
                     and q not in {j.b for j, _g in groups}}
                    | {q for jj in ctx.joints for p, q in ((jj.a, jj.b), (jj.b, jj.a))
                       if p in moved_all and q not in moved_all and q in by_id and q not in {j.b for j, _g in groups}}
                    | {p for p in by_id if p.startswith(FLEXIBLE)})
    for side in (0, 1):
        over, motion, names = {}, {}, []
        for j, grp in groups:
            lim = float(j.limits[side])
            R = rot_about(axis_vec(j.axis), j.origin, lim)
            names.append('%s %+g' % (j.edge, lim))
            for p in grp:
                if p in by_id:
                    over[p], motion[p] = matmul(R, by_id[p]['matrix']), R
        out.append(('elevons at %s limit (%s)' % ('lower' if side == 0 else 'upper', ', '.join(names)), over,
                    motion, sorted(over), linked))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender')
    ap.add_argument('--transport', action='store_true', help='also check ground items (box, cradles) in place')
    ap.add_argument('--tol-mm', type=float, default=0.05, help='penetration depth reported as an error (mm)')
    ap.add_argument('--no-sweep', action='store_true')
    ap.add_argument('--audit-wires', action='store_true', help='per-wire clash list by route segment (report.json)')
    ap.add_argument('--out', default=os.path.join(HERE, 'out'))
    ap.add_argument('--job-only', action='store_true', help='write out/_job.json (parts + drawn wires) and stop')
    ap.add_argument('--glb', nargs='?', const=os.path.join(REDESIGN, 'blender', 'out', 'aircraft', 'glb', 'assembly.glb'),
                    help='also run the gate on the EXPORTED model (collide_glb_blender.py, about 8 min): every part '
                         'as the 3-D explorer shows it, cuts baked in, no cutter honoured, plus the wire-entry rule')
    a = ap.parse_args()
    blender = None if a.job_only else find_blender(a.blender)
    os.makedirs(a.out, exist_ok=True)
    import build_all
    from backends.stub_backend import StubBackend
    ctx, graph, results = build_all.build(StubBackend(), *build_all.roots(False), log=lambda *x: None)
    bad = [r for r in results if not r[2]]
    if bad:
        sys.exit('collide: CAD modules failed: %s' % ', '.join('%s/%s' % (r[0], r[1]) for r in bad))
    comps, skipped = jobs_for(ctx, a.transport)
    wires = []
    inline = {}                                       # wire edge -> parts fitted in-line on it (harness cad.*.wire)
    hp = os.path.join(REDESIGN, 'subsystems', 'harness', 'params.json')
    if os.path.exists(hp):
        with open(hp, encoding='utf-8') as f:
            cad = json.load(f).get('harness', {}).get('cad', {})
        for tab in cad.values():
            for pid, v in (tab.get('value') or {}).items() if isinstance(tab.get('value'), dict) else ():
                if isinstance(v, dict) and v.get('wire'):
                    inline.setdefault(v['wire'], []).append(pid)
    for w in ctx.wires:                               # drawn exactly as the GLB draws them (blender_backend.wire)
        e = graph.edges.get(w.edge, {})
        blk = e.get('wire', {}) if isinstance(e.get('wire'), dict) else {}
        wires.append({'id': w.edge, 'ends': [e.get('part_a'), e.get('part_b')], 'inline': inline.get(w.edge, []),
                      'bend': blk.get('bend_radius_mm', 5 * w.dia * 1000) / 1000.0,
                      'strands': [[[list(p) for p in line], d] for line, d in (w.strands or [(w.points, w.dia)])]})
    P = poses(ctx, comps, graph.edges) if not a.no_sweep else [('static', {}, {}, None, None)]
    job = {'comps': comps, 'wires': wires, 'poses': [{'name': n, 'over': o, 'R': R, 'moved': m, 'skip_with': k}
                                     for n, o, R, m, k in P], 'report_mm': min(0.01, a.tol_mm / 2), 'audit': a.audit_wires}
    jp = os.path.join(a.out, '_job.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(job, f)
    if a.job_only:
        print('collide: job written, %d parts, %d wires: %s' % (len(comps), len(wires), jp))
        return
    rp = os.path.join(a.out, 'report.json')
    if os.path.exists(rp):
        os.remove(rp)
    t0 = time.time()
    p = subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P',
                        os.path.join(HERE, 'collide_blender.py'), '--', jp, rp],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    with open(os.path.join(a.out, 'blender.log'), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n----- stderr\n' + p.stderr)
    if p.returncode != 0 or not os.path.exists(rp):
        sys.exit('collide: Blender run failed (exit %s); see %s' % (p.returncode, os.path.join(a.out, 'blender.log')))
    with open(rp, encoding='utf-8') as f:
        rep = json.load(f)
    rep['skipped'] = skipped
    rep['kinks'] = kinks(wires)
    rep['seconds'] = round(time.time() - t0, 1)
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, sort_keys=True)
    write_md(rep, a, os.path.join(a.out, 'REPORT.md'))
    errs = [h for pz in rep['poses'] for h in pz['hits'] if h['depth_mm'] > a.tol_mm] + rep.get('wire_ends', [])         + rep.get('kinks', [])
    for pz in rep['poses']:
        n = sum(1 for h in pz['hits'] if h['depth_mm'] > a.tol_mm)
        print('  %-48s %4d part pairs penetrate > %g mm' % (pz['name'][:48], n, a.tol_mm))
    print('  %-48s %4d' % ('wire ends not seated in a part', len(rep.get('wire_ends', []))))
    print('  %-48s %4d' % ('wire bends tighter than the wire (folds)', len(rep.get('kinks', []))))
    if a.glb:                                         # D-88: the exported GLB, as shown
        gp = os.path.join(a.out, 'glb_report.json')
        q = subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P',
                            os.path.join(HERE, 'collide_glb_blender.py'), '--', jp, a.glb, gp],
                           capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        with open(os.path.join(a.out, 'glb.log'), 'w', encoding='utf-8') as f:
            f.write(q.stdout + '\n----- stderr\n' + q.stderr)
        if q.returncode != 0 or not os.path.exists(gp):
            sys.exit('collide: GLB run failed (exit %s); see %s' % (q.returncode, os.path.join(a.out, 'glb.log')))
        with open(gp, encoding='utf-8') as f:
            gr = json.load(f)
        gerr = [h for h in gr['hits'] if h['depth_mm'] > a.tol_mm] + gr['wire_ends'] + gr['entries']
        print('  %-48s %4d' % ('GLB: part pairs penetrate > %g mm' % a.tol_mm,
                               sum(1 for h in gr['hits'] if h['depth_mm'] > a.tol_mm)))
        print('  %-48s %4d' % ('GLB: wire ends not seated', len(gr['wire_ends'])))
        print('  %-48s %4d' % ('GLB: wires not entering square / on a face', len(gr['entries'])))
        errs += gerr
        rep['glb'] = {'errors': len(gerr), 'report': os.path.relpath(gp, REDESIGN)}
    print('collide: %s (%d bodies in %d parts, %d poses, %.0f s); report %s'
          % ('PASS' if not errs else 'FAIL, %d overlaps / loose ends' % len(errs), rep['bodies'], rep['parts'], len(rep['poses']),
             rep['seconds'], os.path.relpath(os.path.join(a.out, 'REPORT.md'), os.getcwd())))
    sys.exit(1 if errs else 0)


def kinks(wires):
    """D-87: a drawn bend tighter than the strand's own radius makes the tube fold through itself (a wire phasing
    through itself). Same rounding as blender_backend.fillet_polyline: radius = the declared bend radius, never
    more than 45 % of either segment; the effective radius t / tan(theta/2) must be >= the strand radius."""
    bad = []
    for w in wires:
        R = w['bend']
        for k, (line, d) in enumerate(w['strands']):
            r = d / 2
            for i in range(1, len(line) - 1):
                a, b, c = line[i - 1], line[i], line[i + 1]
                d1, d2 = [b[j] - a[j] for j in range(3)], [c[j] - b[j] for j in range(3)]
                n1, n2 = math.hypot(*d1), math.hypot(*d2)
                if n1 < 1e-9 or n2 < 1e-9:
                    continue
                ang = math.acos(max(-1.0, min(1.0, sum(d1[j] * d2[j] for j in range(3)) / n1 / n2)))
                if ang < 1e-3:
                    continue
                t = min(R * math.tan(ang / 2), 0.45 * n1, 0.45 * n2)
                reff = t / math.tan(ang / 2)
                if reff < r:
                    bad.append({'wire': w['id'], 'strand': k, 'at_mm': [round(v * 1000, 1) for v in b],
                                'bend_mm': round(reff * 1000, 2), 'radius_mm': round(r * 1000, 2)})
    return bad


def write_md(rep, a, path):
    L = ['# Interference check (no parts phasing)', '',
         'Generated by `collision/collide.py` on %s from the stub-backend CAD (the geometry the GLB and the shop STLs '
         'are made from). Depth = how far a point of one part lies inside a different part (deepest sampled point); '
         'touching faces measure ~0 and pass. Error threshold %g mm; listed from %g mm.'
         % (datetime.date.today().isoformat(), a.tol_mm, min(0.01, a.tol_mm / 2)), '',
         '**%s.** %d bodies in %d parts; %d poses (static + each elevon joint at each limit); %.0f s. Wire ends not '
         'seated in a part: %d.'
         % ('PASS' if not any(h['depth_mm'] > a.tol_mm for pz in rep['poses'] for h in pz['hits'])
            and not rep.get('wire_ends') and not rep.get('kinks') else 'FAIL',
            rep['bodies'], rep['parts'], len(rep['poses']), rep['seconds'], len(rep.get('wire_ends', []))), '']
    if rep.get('kinks'):
        L += ['## Wire bends tighter than the wire', '', '| Wire | Strand | At (x, y, z) mm | Bend radius mm | Wire '
              'radius mm |', '|---|---|---|---|---|'] + ['| %s | %d | %s | %.2f | %.2f |' % (
                  k['wire'], k['strand'], ', '.join('%.1f' % v for v in k['at_mm']), k['bend_mm'], k['radius_mm'])
                  for k in rep['kinks']] + ['']
    if rep.get('wire_ends'):
        L += ['## Wire ends not seated', '', '| Wire | Strand | End (x, y, z) mm | Gap mm | Its parts |',
              '|---|---|---|---|---|'] + ['| %s | %d | %s | %s | %s |' % (
                  e['wire'], e['strand'], ', '.join('%.1f' % v for v in e['end_mm']),
                  '-' if e['gap_mm'] is None else '%.2f' % e['gap_mm'], ', '.join(e['hosts']))
                  for e in rep['wire_ends']] + ['']
    for pz in rep['poses']:
        hits = sorted(pz['hits'], key=lambda h: -h['depth_mm'])
        L += ['## %s' % pz['name'], '']
        if pz.get('moved'):
            L += ['Moved: %s.' % ', '.join(pz['moved']), '']
        if pz.get('not_swept_against'):
            L += ['Not checked against the moved parts (linkage path not modelled): %s.'
                  % ', '.join(pz['not_swept_against']), '']
        if not hits:
            L += ['No overlaps.', '']
            continue
        L += ['| Part A | Part B | Depth mm | At (x, y, z) mm | Deepest bodies | Result |', '|---|---|---|---|---|---|']
        for h in hits:
            L.append('| %s | %s | %.3f | %s | %s | %s |' % (
                h['a'], h['b'], h['depth_mm'], ', '.join('%.1f' % v for v in h['at_mm']),
                '; '.join(h['bodies'][:2]) + (' ...' if len(h['bodies']) > 2 else ''),
                'FAIL' if h['depth_mm'] > a.tol_mm else 'below tol'))
        L.append('')
    if rep.get('skipped'):
        L += ['## Not checked', '', 'Not solids: ' + ', '.join('%s (%s)' % s for s in rep['skipped']) + '. Wires '
              '(centre lines) are not solids. The pushrods and servo arms stay at neutral in the sweep (four-bar path '
              'not modelled here).', '']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))


if __name__ == '__main__':
    main()
