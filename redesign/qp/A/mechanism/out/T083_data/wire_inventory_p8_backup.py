"""wire_inventory.py - every wire / strand of the concept A CAD with its length by enclosure class (D-198, CLAUDE.md exposed-wiring rule).
    python -I redesign/qp/A/cad/wire_inventory.py [path/to/cad_dir_with_a_model.py]   (default: this folder)  -> prints a table, writes out/wire_inventory.json
Classes (per 1 mm sample of each segment): ARM  = inside the cup collar / arm bore (enclosed by the carbon tube and printed cup),
RACE = inside a printed phase-lead raceway / hub conduit (D-199), GROOVE = in a foam-core channel (servo grooves, phase-lead ditch),
COVER = under the bay cover AVN-008, EXPOSED = everything else. Also prints the minimum bend radius of each bundle centre line (rule: >= 4 mm).
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


PH_ST = {'E-HRN-02': 'UR', 'E-HRN-03': 'UL', 'E-HRN-04': 'LR', 'E-HRN-05': 'LL'}


def classify(eid, pts):
    out = {'ARM': 0.0, 'RACE': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
    phase = eid in PH_ST
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = seg_len(a, b)
        n = max(1, int(round(L / 0.001)))
        for k in range(n):
            f = (k + 0.5) / n
            mid = [a[j] + (b[j] - a[j]) * f for j in range(3)]
            cls = 'EXPOSED'
            if NEW:
                enc = m.enclosure_class(mid) if hasattr(m, 'enclosure_class') else None
                if phase:
                    ph = math.radians(m.PHI[PH_ST[eid]])    # arm-frame distance along the arm of the point
                    ya = mid[1] * math.cos(ph) + mid[2] * math.sin(ph)
                    if enc == 'ARM' or (ya > m.R_M - 0.030 and mid[0] < -0.05 and not enc):
                        cls = 'ARM'                       # in the arm tube bore / its 4.8 mm exit hole (D-202), or in the cup collar (carbon tube and printed cup)
                    elif enc:
                        cls = 'RACE' if enc == 'RACE' else 'GROOVE'
                    elif m.cov_interior(mid):                # T-022 Q4: bay cover or RX hood (was the box test COV_X0 < x < COV_X1, |y| < COV_Y, z < roof)
                        cls = 'COVER'
                elif eid in ('E-HRN-07', 'E-HRN-08') and mid[2] < m.zu(mid[0]) - 0.0003 and mid[0] > m.COV_X0 and mid[0] < 0.1250:
                    cls = 'GROOVE'
                elif eid == 'E-HRN-11' and mid[2] < m.zu(mid[0]) - 0.0003:
                    cls = 'GROOVE'                        # D-208: airspeed I2C lead in its core groove and the board pocket
                elif m.cov_interior(mid):                # T-022 Q4: bay cover or RX hood (was the box test COV_X0 < x < COV_X1, |y| < COV_Y, z < roof)
                    cls = 'COVER'
            out[cls] += L / n
    return out


def min_bend(pts):
    """Smallest bend radius (m) of the dense centre line: circumradius of consecutive point triples (arcs are sampled every ~9 deg)."""
    worst = 9.0
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
        if min(ab, bc) < 1e-6:
            continue
        v1, v2 = [b[j] - a[j] for j in range(3)], [c[j] - a[j] for j in range(3)]
        cr = [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]
        area2 = math.sqrt(sum(x * x for x in cr))
        if area2 < 1e-12:
            continue
        worst = min(worst, ab * bc * ca / (2 * area2))
    return worst


def main():
    ctx, graph, results = build_all.build(StubBackend(), os.path.join(CAD, 'model'), os.path.join(CAD, 'model', 'modules.txt'), log=lambda *a: None)
    rows, tot = [], {'ARM': 0.0, 'RACE': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
    for w in ctx.wires:
        strands = w.strands or [(w.points, w.dia)]
        acc = {'ARM': 0.0, 'RACE': 0.0, 'GROOVE': 0.0, 'COVER': 0.0, 'EXPOSED': 0.0}
        for line, d in strands:
            c = classify(w.edge, line)
            for k in acc:
                acc[k] += c[k]
        n = len(strands)
        rows.append(dict(edge=w.edge, strands=n, dia_mm=round(strands[0][1] * 1000, 2), **{k.lower() + '_m': round(v / n, 4) for k, v in acc.items()},
                         total_m=round(sum(acc.values()) / n, 4), min_bend_mm=round(min_bend(w.points) * 1000, 2), total_strand_m=round(sum(acc.values()), 3)))
        for k in tot:
            tot[k] += acc[k]
    print('%-9s %3s %6s %8s %8s %8s %8s %8s %8s %7s' % ('edge', 'str', 'd mm', 'ARM m', 'RACE', 'GROOVE', 'COVER', 'EXPOSED', 'total', 'bend mm'))
    for r in rows:
        print('%-9s %3d %6.2f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %7.2f' % (r['edge'], r['strands'], r['dia_mm'], r['arm_m'], r['race_m'], r['groove_m'], r['cover_m'], r['exposed_m'], r['total_m'], r['min_bend_mm']))
    print('strand-metres (all strands): ' + ', '.join('%s %.3f' % (k, v) for k, v in tot.items()) + '; total %.3f' % sum(tot.values()))
    if CAD == HERE:
        json.dump(dict(rows=rows, totals_strand_m=tot), open(os.path.join(HERE, 'out', 'wire_inventory.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
