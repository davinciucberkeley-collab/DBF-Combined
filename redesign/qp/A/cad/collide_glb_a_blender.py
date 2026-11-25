"""collide_glb_a_blender.py - runs INSIDE Blender: collision/collide_glb_blender.py (unmodified, imported) on the concept A GLB with
  1. the a_collide_blender orientation fix: a body whose signed volume is negative is reversed before it is built (an inside-out
     body reports no point inside it, so an overlap would go undetected);
  2. every overlapping pair classified: all overlap samples (surface points of one part deeper than tol inside the other, and not in a
     wire's terminal) are tested against the pair's CAD cutters (job 'cuts'; same CUT_TOL as collide_blender.removed). All covered =
     EXPORT ARTEFACT (the boolean that should have removed the material is missing in the GLB); any uncovered = REAL CLASH;
  3. the concept A wire-entry rule (see ENTRY RULE below) in place of the K09-L square-entry rule.
    blender -b --factory-startup -P collide_glb_a_blender.py -- <_job_glb.json> <assembly.glb> <out.json> [tol_mm]

ENTRY RULE (concept A). Source: collide_blender.py D-86 / D-89 (WIRE_END_MM 6 mm, TERMINATION names) and the concept A harness
(qp/A/cad/amodel/electrical.py: leads are soldered to pads / cups on the ESC, FC and servo, or crimped into JST-GH / XT30 housings;
none is a push-through square entry). For each strand end lying in one of its terminal parts' solids:
  (a) the strand runs at most WIRE_END_MM (6 mm) past the point where it first enters that solid (D-86);
  (b) its END lies in, or within the strand radius + END_SEAT_MM (0.5 mm, D-86, as end_seats) of, a CAD body of that part whose name
      matches collide_blender.TERMINATION (solder pad, cup, joint, plug, socket, header, housing, lead exit, ...; D-89, the rule
      collide_a applies per body). The GLB has one united solid per part, so the named bodies come from the job. Bare board or
      case is not a termination.
  The K09-L 'square to the face, flat ring' test is not applied: a lead lapped onto a solder pad or into a cup does not arrive square.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'collision')
sys.path.insert(0, COLL)
import bmesh                           # noqa: E402
import bpy                             # noqa: E402
import collide_glb_blender as g        # noqa: E402  (also installs the GLB depth / penetration functions into cb)
from mathutils import Matrix           # noqa: E402

cb = g.cb
FLIPPED = []
_OrigBody = cb.Body


class Body(_OrigBody):
    def __init__(self, pid, idx, name, ob):
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.transform(ob.matrix_world)
        neg = bm.calc_volume(signed=True) < 0
        bm.free()
        if neg:
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
            bm.to_mesh(ob.data)
            bm.free()
            FLIPPED.append(name)
        super().__init__(pid, idx, name, ob)


cb.Body = Body


def covered(p, cutters):
    for c in cutters:
        if not all(c.lo[i] - cb.CUT_TOL_MM <= p[i] <= c.hi[i] + cb.CUT_TOL_MM for i in range(3)):
            continue
        loc, _n, _i, d = c.bvh.find_nearest(p)
        if loc is not None and (d <= cb.CUT_TOL_MM or cb.depth_inside(p, c) > 0):
            return True
    return False


def cutters_of(comp, col):
    out = []
    for k, (s, Mc) in enumerate(comp.get('cuts') or []):
        ob = cb.bm_._body('%s cut%d' % (comp['id'], k), s, Matrix(Mc), col, 0.0)
        if len(ob.data.vertices):
            c = _OrigBody(comp['id'], -1 - k, s.get('name') or 'cut %d' % k, ob)
            c.cutters = []
            out.append(c)
    return out


def overlap_points(a, b, tol):
    """Every sampled surface point of one body deeper than tol inside the other (same samples and exclusions as g.penetration)."""
    pts = []
    ov = a.bvh.overlap(b.bvh)
    for src, dst, ids in ((a, b, {i for i, _j in ov}), (b, a, {j for _i, j in ov})):
        for i in ids:
            t = src.tris[i]
            nrm = (t[1] - t[0]).cross(t[2] - t[0])
            if nrm.length == 0:
                continue
            nrm.normalize()
            for p in cb.tri_samples(t):
                d = g.depth_inside(p, dst)
                if d > tol and not cb.at_terminal(p, a, b) and (getattr(src, 'wire', False) or g.parity_inside(p - nrm * g.BACK_MM, src)):
                    pts.append((p, d))
    return pts


def classify(hits, bodies, comps, tol):
    col = bpy.data.collections.new('cutters')
    bpy.context.scene.collection.children.link(col)
    cache = {}
    byp = {}
    for b in bodies:
        byp.setdefault(b.pid, []).append(b)
    for h in hits:
        if h['depth_mm'] <= tol:
            continue
        pids = (h['a'], h['b'])
        cuts = []
        for pid in pids:
            if pid not in cache:
                cache[pid] = cutters_of(comps[pid], col) if pid in comps else []
            cuts += cache[pid]
        n = nc = 0
        worst = (0.0, None)
        for x in byp.get(pids[0], []):
            for y in byp.get(pids[1], []):
                if not cb.boxes_overlap(x, y):
                    continue
                for p, d in overlap_points(x, y, tol):
                    n += 1
                    if covered(p, cuts):
                        nc += 1
                    elif d > worst[0]:
                        worst = (d, p)
        h['samples'] = n
        h['samples_in_cutters'] = nc
        h['cutters_of_pair'] = len(cuts)
        if n and nc == n:
            h['class'] = 'EXPORT ARTEFACT'
        else:
            h['class'] = 'REAL CLASH'
            h['uncovered_depth_mm'] = round(worst[0], 3)
            h['uncovered_at_mm'] = [round(c, 2) for c in worst[1]] if worst[1] is not None else None


def entry_check_a(wires, solids, term_bodies):
    byp = {}
    for b in solids:
        byp.setdefault(b.pid, []).append(b)
    bad = []
    for w in wires:
        hosts = set(w.terms) | {i.split(':')[0] for i in w.inline}
        for k, e in enumerate((w.ends[0], w.ends[1])):
            host = None
            for pid in hosts:
                for b in byp.get(pid, []):
                    if all(b.lo[i] - 0.01 <= e[i] <= b.hi[i] + 0.01 for i in range(3)) and cb.inside(e, b):
                        host = b
                        break
                if host:
                    break
            if host is None:
                continue
            line = w.line
            seq = line if k == 1 else list(reversed(line))
            cross = None
            for a_, b_ in zip(reversed(seq[:-1]), reversed(seq[1:])):
                if not cb.inside(a_, host):
                    lo_, hi_ = a_.copy(), b_.copy()
                    for _ in range(30):
                        m = (lo_ + hi_) / 2
                        if cb.inside(m, host):
                            hi_ = m
                        else:
                            lo_ = m
                    cross = (lo_ + hi_) / 2
                    break
            why = []
            if cross is None:
                why.append('the whole strand lies inside %s' % host.pid)
                cross = e
            else:
                depth = (e - cross).length
                if depth > cb.WIRE_END_MM + 0.01 and host.pid in w.terms:
                    why.append('runs %.1f mm into %s (limit %.0f)' % (depth, host.pid, cb.WIRE_END_MM))
            ds = []
            for t in term_bodies.get(host.pid, []):
                if all(t.lo[i] <= e[i] <= t.hi[i] for i in range(3)) and cb.inside(e, t):
                    ds.append(0.0)
                    continue
                r = t.bvh.find_nearest(e)
                if r[0] is not None:
                    ds.append(r[3])
            dmin = min(ds) if ds else None
            lim = w.r + cb.END_SEAT_MM
            if host.pid in w.terms and (dmin is None or dmin > lim):
                why.append('ends %s %s from the nearest termination body (limit %.2f mm; %d termination bodies)' % (
                    host.pid, 'none' if dmin is None else '%.2f mm' % dmin, lim, len(ds)))
            if why:
                bad.append({'wire': w.pid, 'strand': w.idx, 'end_mm': [round(c, 1) for c in e], 'part': host.pid,
                            'at_mm': [round(c, 1) for c in cross], 'why': '; '.join(why)})
    return bad


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    tol = float(argv[3]) if len(argv) > 3 else 0.05
    job = json.load(open(argv[0], encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=argv[1])
    col = bpy.data.collections.new('wires')
    bpy.context.scene.collection.children.link(col)
    comps = {c['id']: c for c in job['comps']}
    solids = g.part_bodies(col, set(comps))
    wires = cb.make_wires(job.get('wires', []), col)
    import blender_backend as bbk
    lines = {}
    for wj in job.get('wires', []):
        for k, (line, dia) in enumerate(wj['strands']):
            lines[(wj['id'], k)] = [v * 1000.0 for v in bbk.fillet_polyline([tuple(p) for p in line], wj['bend'])]
    for w in wires:
        w.line = lines[(w.pid, w.idx)]
    tcol = bpy.data.collections.new('terms')
    bpy.context.scene.collection.children.link(tcol)
    term_bodies = {}
    for pid in {t for w in wires for t in w.terms}:
        c = comps.get(pid)
        for i, s in enumerate(c['bodies'] if c else []):
            if cb.TERMINATION.search(s.get('name') or ''):
                ob = cb.bm_.body_object('%s#t%d' % (pid, i), s, Matrix(c['matrix']), tcol)
                if len(ob.data.vertices):
                    term_bodies.setdefault(pid, []).append(_OrigBody(pid, i, s.get('name'), ob))
    print('collide-glb-a: %d part bodies (%d reversed: inside-out), %d wire strands' % (len(solids), len(FLIPPED), len(wires)))
    hits = cb.check(cb.sweep_pairs(solids + wires), job['report_mm'])
    classify(hits, solids + wires, comps, tol)
    rep = {'bodies': len(solids), 'wire_strands': len(wires), 'reversed_bodies': FLIPPED, 'glb': argv[1], 'tol_mm': tol,
           'hits': hits, 'wire_ends': cb.end_seats(wires, solids, inside_fn=g.parity_inside),
           'entries': entry_check_a(wires, solids, term_bodies)}
    with open(argv[2], 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    over = [h for h in hits if h['depth_mm'] > tol]
    print('collide-glb-a: %d overlapping pairs (%d artefact, %d real), %d unseated ends, %d bad entries' % (
        len(over), sum(1 for h in over if h.get('class') == 'EXPORT ARTEFACT'), sum(1 for h in over if h.get('class') != 'EXPORT ARTEFACT'),
        len(rep['wire_ends']), len(rep['entries'])))


if __name__ == '__main__':
    main()
