"""wire_inventory.py - every wire / strand of the concept A CAD with its length by enclosure class (D-198, CLAUDE.md exposed-wiring rule).
    python -I redesign/qp/A/cad/wire_inventory.py [path/to/cad_dir_with_a_model.py]   (default: this folder)  -> prints a table, writes out/wire_inventory.json
Classes (per segment, by its midpoint): ARM  = inside the cup collar / arm bore (enclosed by the carbon tube and printed cup),
GROOVE = in a foam-core channel under the skin, COVER = under the bay cover AVN-008, EXPOSED = everything else.
Lengths are polyline lengths of the strand centre lines as registered in the CAD (sharp corners; the drawn fillets are 1-3 % shorter)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
sys.path.insert(0, CAD)
sys.dont_write_bytecode = True
import a_model as m                    # noqa: E402
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(REDESIGN, 'fusion'), os.path.join(REDESIGN, 'interfaces')):
    sys.path.insert(0, p)
import build_all                       # noqa: E402
from backends.stub_backend import StubBackend   # noqa: E402

MODEL = os.path.join(HERE, 'model')
NEW = hasattr(m, 'COV_X0')


def seg_len(a, b):
    return math.dist(a, b)


def roof(x):
    o = m.cov_outer()
    for (x0, z0), (x1, z1) in zip(o, o[1:]):
        if x0 <= x <= x1 and x1 > x0:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return 0.0


def classify(eid, pts):
    out = {'ARM': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        mid = [(a[k] + b[k]) / 2 for k in range(3)]
        L = seg_len(a, b)
        cls = 'EXPOSED'
        if NEW:
            if eid in ('E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05') and i <= 4:
                cls = 'ARM'
            elif eid in ('E-HRN-07', 'E-HRN-08') and i >= 3:
                cls = 'GROOVE' if i <= len(pts) - 3 else 'EXPOSED'
            elif m.COV_X0 < mid[0] < m.COV_X1 and abs(mid[1]) < m.COV_Y and mid[2] < roof(mid[0]):
                cls = 'COVER'
        out[cls] += L
    return out


def main():
    ctx, graph, results = build_all.build(StubBackend(), os.path.join(CAD, 'model'), os.path.join(CAD, 'model', 'modules.txt'), log=lambda *a: None)
    rows, tot = [], {'ARM': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
    for w in ctx.wires:
        strands = w.strands or [(w.points, w.dia)]
        acc = {'ARM': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
        for line, d in strands:
            c = classify(w.edge, line)
            for k in acc:
                acc[k] += c[k]
        n = len(strands)
        rows.append(dict(edge=w.edge, strands=n, dia_mm=round(strands[0][1] * 1000, 2), **{k.lower() + '_m': round(v / n, 4) for k, v in acc.items()},
                         total_m=round(sum(acc.values()) / n, 4), total_strand_m=round(sum(acc.values()), 3)))
        for k in tot:
            tot[k] += acc[k]
    print('%-9s %3s %6s %8s %8s %8s %8s %8s' % ('edge', 'str', 'd mm', 'ARM m', 'GROOVE', 'COVER', 'EXPOSED', 'total'))
    for r in rows:
        print('%-9s %3d %6.2f %8.3f %8.3f %8.3f %8.3f %8.3f' % (r['edge'], r['strands'], r['dia_mm'], r['arm_m'], r['groove_m'], r['cover_m'], r['exposed_m'], r['total_m']))
    print('strand-metres (all strands): ' + ', '.join('%s %.3f' % (k, v) for k, v in tot.items()) + '; total %.3f' % sum(tot.values()))
    if CAD == HERE:
        json.dump(dict(rows=rows, totals_strand_m=tot), open(os.path.join(HERE, 'out', 'wire_inventory.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
