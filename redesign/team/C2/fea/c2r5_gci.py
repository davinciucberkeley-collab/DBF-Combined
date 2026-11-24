"""C2-R5: Celik et al. (2008) three-grid GCI of the corner measures from out/c2r5/measures.json.
Run: python -I redesign/team/C2/fea/c2r5_gci.py <tag_L1> <tag_L2> <tag_L3>"""
import json, math, sys
from pathlib import Path
from scipy.optimize import brentq

M = json.loads((Path(__file__).resolve().parent / "out" / "c2r5" / "measures.json").read_text())


def gci(f1, f2, f3, h1, h2, h3):          # 1 = fine
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0:
        return 0.0, float("nan")
    s = math.copysign(1, e32 / e21)
    def F(p):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        return p - abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
    try:
        p = brentq(F, 0.05, 20)
    except ValueError:
        p = float("nan")
    if p != p:
        return float("nan"), p
    ea = abs((f1 - f2) / f1)
    return 1.25 * ea / (r21 ** p - 1), p


if __name__ == "__main__":
    t1, t2, t3 = sys.argv[1:4]          # coarse, medium, fine
    for k in ("s1", "s3", "tau"):
        for meas in ("peak", "avg1", "vm_1.78"):
            f = [M[t]["foam"][k][meas] * 1.5 / 1e3 for t in (t1, t2, t3)]
            h = [M[t]["h_m"] for t in (t1, t2, t3)]
            g, p = gci(f[2], f[1], f[0], h[2], h[1], h[0])
            print(f"{k:4s} {meas:8s} L1 {f[0]:7.1f} L2 {f[1]:7.1f} L3 {f[2]:7.1f} kPa ult   p {p:6.2f}  GCI_fine {g:.3f}")
