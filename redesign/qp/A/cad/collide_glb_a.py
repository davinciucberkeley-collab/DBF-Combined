"""collide_glb_a.py - the exported-model (GLB) collision gate for concept A (collide.py --glb equivalent, D-88).
Builds the concept A job (same as collide_a.py, static pose, own output folder) and runs collide_glb_a_blender.py in Blender on the
exported GLB: every part exactly as the Explorer shows it, booleans baked in, NO cutter honoured, plus the wire-end rules.
    python -I redesign/qp/A/cad/collide_glb_a.py [--glb redesign/site/assets/concept-a.glb] [--tol-mm 0.05] [--out DIR] [--blender EXE]
Exit 0 only with 0 part pairs > tol, 0 unseated wire ends and 0 bad wire entries (no exemptions). Report: <out>/glb_report.json, glb.log.
Every overlapping pair is classified by the wrapper as EXPORT ARTEFACT (every overlap sample lies in a CAD cutter) or REAL CLASH.
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
for p in (os.path.join(REDESIGN, 'collision'), os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces'),
          os.path.join(REDESIGN, 'manufacturing')):
    sys.path.insert(0, p)
import collide                       # noqa: E402
import build_all                     # noqa: E402
from backends.stub_backend import StubBackend   # noqa: E402


def build_job(out):
    ctx, graph, results = build_all.build(StubBackend(), os.path.join(HERE, 'model'), os.path.join(HERE, 'model', 'modules.txt'),
                                          log=lambda *x: None)
    bad = [r for r in results if not r[2]]
    if bad:
        sys.exit('modules failed: %s' % bad)
    comps, _skipped = collide.jobs_for(ctx, False)
    wires = []
    for w in ctx.wires:
        e = graph.edges.get(w.edge, {})
        blk = e.get('wire', {}) if isinstance(e.get('wire'), dict) else {}
        wires.append({'id': w.edge, 'ends': [e.get('part_a'), e.get('part_b')], 'inline': [],
                      'bend': blk.get('bend_radius_mm', 5 * w.dia * 1000) / 1000.0,
                      'strands': [[[list(p) for p in line], d] for line, d in (w.strands or [(w.points, w.dia)])]})
    job = {'comps': comps, 'wires': wires, 'poses': [], 'report_mm': 0.005, 'audit': False}
    jp = os.path.join(out, '_job_glb.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(job, f)
    return jp, len(comps), len(wires)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glb', default=os.path.join(REDESIGN, 'site', 'assets', 'concept-a.glb'))
    ap.add_argument('--blender')
    ap.add_argument('--tol-mm', type=float, default=0.05)
    ap.add_argument('--out', default=os.path.join(HERE, 'out', 'glb'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    blender = collide.find_blender(a.blender)
    t0 = time.time()
    jp, nc, nw = build_job(a.out)
    print('job: %d parts, %d wires (%.0f s)' % (nc, nw, time.time() - t0))
    gp = os.path.join(a.out, 'glb_report.json')
    if os.path.exists(gp):
        os.remove(gp)
    q = subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1', '-P',
                        os.path.join(HERE, 'collide_glb_a_blender.py'), '--', jp, a.glb, gp, str(a.tol_mm)],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    with open(os.path.join(a.out, 'glb.log'), 'w', encoding='utf-8') as f:
        f.write(q.stdout + '\n----- stderr\n' + q.stderr)
    if q.returncode != 0 or not os.path.exists(gp):
        sys.exit('collide_glb_a: Blender run failed (exit %s); see %s' % (q.returncode, os.path.join(a.out, 'glb.log')))
    with open(gp, encoding='utf-8') as f:
        r = json.load(f)
    pairs = [h for h in r['hits'] if h['depth_mm'] > a.tol_mm]
    art = [h for h in pairs if h.get('class') == 'EXPORT ARTEFACT']
    print('  GLB: part pairs penetrate > %g mm: %d (export artefact %d, real clash %d)' % (a.tol_mm, len(pairs), len(art), len(pairs) - len(art)))
    print('  GLB: wire ends not seated: %d' % len(r['wire_ends']))
    print('  GLB: bad wire entries: %d' % len(r['entries']))
    err = len(pairs) + len(r['wire_ends']) + len(r['entries'])
    print('collide_glb_a: %s (%d part bodies, %d wire strands, %.0f s)' % ('PASS' if not err else 'FAIL, %d' % err, r['bodies'],
          r['wire_strands'], time.time() - t0))
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main())
