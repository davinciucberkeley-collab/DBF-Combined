"""collide_a.py - collision/collide.py applied to the concept A model (redesign/qp/A/cad/model). Same job format, same Blender
checker (collide_blender.py, unmodified): part-pair penetration > tol, containment, elevon sweep at both limits, wire ends on a
termination, wire folds. K09-L tree untouched; output in qp/A/cad/out/.
    python -I redesign/qp/A/cad/collide_a.py [--no-sweep] [--tol-mm 0.05] [--job-only]
    python -I redesign/qp/A/cad/collide_a.py --linkage-poses [--angles -21,-20,...,21] [--zj mid,lo,hi] [--tag NAME]   (T-020: arm, keeper,
        rod and elevon group at their kinematic pose per angle, all parts in; own report files out/report_<tag>.json, REPORT_<tag>.md)
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
COLL = os.path.join(REDESIGN, 'collision')
for p in (COLL, os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces'), os.path.join(REDESIGN, 'manufacturing')):
    sys.path.insert(0, p)
import collide                       # noqa: E402  (K09-L helpers, imported not modified)
import build_all                     # noqa: E402
from backends.stub_backend import StubBackend   # noqa: E402

MODEL = os.path.join(HERE, 'model')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender')
    ap.add_argument('--tol-mm', type=float, default=0.05)
    ap.add_argument('--no-sweep', action='store_true')
    ap.add_argument('--job-only', action='store_true')
    ap.add_argument('--linkage-poses', action='store_true', help='T-020 mode: rod, arm, keeper and elevon group posed by the linkage kinematics')
    ap.add_argument('--angles', help='comma list of elevon angles (deg) for --linkage-poses')
    ap.add_argument('--zj', default='mid', help='Z-bend joint states for --linkage-poses: comma list of mid, lo, hi')
    ap.add_argument('--pin-with', default='rod', choices=('rod', 'horn'), help='--linkage-poses: which part the clevis pin MEC-005 moves with')
    ap.add_argument('--tag', default='linkage_poses', help='report name stem for --linkage-poses')
    a = ap.parse_args()
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    ctx, graph, results = build_all.build(StubBackend(), MODEL, os.path.join(MODEL, 'modules.txt'), log=lambda *x: None)
    bad = [r for r in results if not r[2]]
    if bad:
        sys.exit('modules failed: %s' % bad)
    comps, skipped = collide.jobs_for(ctx, False)
    wires = []
    for w in ctx.wires:
        e = graph.edges.get(w.edge, {})
        blk = e.get('wire', {}) if isinstance(e.get('wire'), dict) else {}
        wires.append({'id': w.edge, 'ends': [e.get('part_a'), e.get('part_b')], 'inline': [],
                      'bend': blk.get('bend_radius_mm', 5 * w.dia * 1000) / 1000.0,
                      'strands': [[[list(p) for p in line], d] for line, d in (w.strands or [(w.points, w.dia)])]})
    if a.linkage_poses:
        return linkage_mode(a, out, ctx, graph, comps, wires)
    P = collide.poses(ctx, comps, graph.edges) if not a.no_sweep else [('static', {}, {}, None, None)]
    job = {'comps': comps, 'wires': wires, 'poses': [{'name': n, 'over': o, 'R': R, 'moved': m, 'skip_with': k}
                                                     for n, o, R, m, k in P], 'report_mm': min(0.01, a.tol_mm / 2), 'audit': False}
    jp = os.path.join(out, '_job.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(job, f)
    if a.job_only:
        print('job written: %d parts, %d wires' % (len(comps), len(wires)))
        return 0
    blender = collide.find_blender(a.blender)
    rp = os.path.join(out, 'report.json')
    if os.path.exists(rp):
        os.remove(rp)
    t0 = time.time()
    p = subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P',
                        os.path.join(HERE, 'a_collide_blender.py'), '--', jp, rp], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    with open(os.path.join(out, 'blender.log'), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n----- stderr\n' + p.stderr)
    if p.returncode != 0 or not os.path.exists(rp):
        sys.exit('Blender run failed (exit %s); see out/blender.log' % p.returncode)
    with open(rp, encoding='utf-8') as f:
        rep = json.load(f)
    rep['skipped'] = skipped
    rep['kinks'] = collide.kinks(wires)
    rep['seconds'] = round(time.time() - t0, 1)
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, sort_keys=True)
    collide.write_md(rep, a, os.path.join(out, 'REPORT.md'))
    errs = [h for pz in rep['poses'] for h in pz['hits'] if h['depth_mm'] > a.tol_mm] + rep.get('wire_ends', []) + rep.get('kinks', [])
    for pz in rep['poses']:
        n = sum(1 for h in pz['hits'] if h['depth_mm'] > a.tol_mm)
        print('  %-48s %4d part pairs penetrate > %g mm' % (pz['name'][:48], n, a.tol_mm))
    print('  wire ends not on a termination: %d; wire folds: %d' % (len(rep.get('wire_ends', [])), len(rep.get('kinks', []))))
    print('collide_a: %s (%d bodies in %d parts, %d poses, %.0f s)' % ('PASS' if not errs else 'FAIL, %d' % len(errs),
          rep['bodies'], rep['parts'], len(rep['poses']), rep['seconds']))
    return 1 if errs else 0


def linkage_mode(a, out, ctx, graph, comps, wires):
    """--linkage-poses: separate job / report / log names, the default outputs (report.json, REPORT.md, _job.json, blender.log) are not touched."""
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'mechanism'))
    import linkage_core as kin
    import linkage_poses_a as lp
    angles = [float(x) for x in a.angles.split(',')] if a.angles else lp.DEFAULT_ANGLES
    states = [x.strip() for x in a.zj.split(',')]
    P, err = lp.build_poses(ctx, comps, graph.edges, angles, states, collide, kin, a.pin_with)
    print('  self-checks (max error, m): %s' % ', '.join('%s %.2e' % kv for kv in err.items()))
    if max(err.values()) > 1e-9:
        sys.exit('linkage poses do not reproduce the kinematic points: %s' % err)
    job = {'comps': comps, 'wires': wires, 'poses': P, 'report_mm': min(0.01, a.tol_mm / 2), 'audit': False}
    jp = os.path.join(out, '_job_%s.json' % a.tag)
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(job, f)
    if a.job_only:
        print('job written: %d parts, %d poses: %s' % (len(comps), len(P), jp))
        return 0
    blender = collide.find_blender(a.blender)
    rp = os.path.join(out, 'report_%s.json' % a.tag)
    if os.path.exists(rp):
        os.remove(rp)
    t0 = time.time()
    p = subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P', os.path.join(HERE, 'a_linkage_blender.py'), '--', jp, rp],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    with open(os.path.join(out, 'blender_%s.log' % a.tag), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n----- stderr\n' + p.stderr)
    if p.returncode != 0 or not os.path.exists(rp):
        sys.exit('Blender run failed (exit %s); see out/blender_%s.log' % (p.returncode, a.tag))
    with open(rp, encoding='utf-8') as f:
        rep = json.load(f)
    rep['kinks'] = collide.kinks(wires)
    rep['seconds'] = round(time.time() - t0, 1)
    rep['tol_mm'] = a.tol_mm
    rep['angles'], rep['states'] = angles, states
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, sort_keys=True)
    lp.write_md(rep, os.path.join(out, 'REPORT_%s.md' % a.tag), a.tol_mm)
    errs = [h for pz in rep['poses'] for h in pz['hits'] if h['depth_mm'] > a.tol_mm] + rep.get('wire_ends', []) + rep.get('kinks', [])
    for pz in rep['poses']:
        n = sum(1 for h in pz['hits'] if h['depth_mm'] > a.tol_mm)
        print('  %-48s %4d part pairs penetrate > %g mm' % (pz['name'][:48], n, a.tol_mm))
    print('  wire ends not on a termination: %d; wire folds: %d' % (len(rep.get('wire_ends', [])), len(rep.get('kinks', []))))
    print('collide_a --linkage-poses: %s (%d bodies in %d parts, %d poses, %.0f s)' % ('PASS' if not errs else 'FAIL, %d' % len(errs),
          rep['bodies'], rep['parts'], len(rep['poses']), rep['seconds']))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
