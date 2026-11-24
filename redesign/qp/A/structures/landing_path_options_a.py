"""T-064r ladder support: re-evaluate the landing_path_a.py checks with one change at a time (illustrative option screening, NOT a design decision).
python -I landing_path_options_a.py > out.txt     (about 4 min)   Category: rigid-body dynamics + hand-calculation part checks, illustrative screening.
Variants change module constants of landing_path_a (printed-part dimensions) or the sim inputs (mu, CG z).  Each prints the minimum RF over the 23 landing cases for: all rows,
and the rows grouped by part.  Mass deltas are EST solid PETG at RHO_PETG 1.27 g/cm3 (infill / shell factor unknown, '-')."""
import sys, os, math, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import landing_a as L
import landing_path_a as P
CASES = P.cases(False)
def run(mu=0.40, cgz=None):
    out = []
    for n, kw in CASES:
        q = L.simulate(Fp=30.0, dt=2e-4, T=1.5, trace=True, mu=mu, cg_override=(None if cgz is None else [L.geom()['cg'][0], L.geom()['cg'][1], cgz]), **kw)
        out.append((n, q['trace'].reshape(-1, 4, 3)))
    return out
def evaluate(traces):
    allrf = {}
    for n, FBt in traces:
        for key, (lab, a) in P.checks(FBt).items(): allrf.setdefault(key, []).append((float(a.min()), n))
    return {k: min(v) for k, v in allrf.items()}
def group(res):
    g = {}
    for k, (rf, n) in res.items(): g.setdefault(k.split(' ')[0], []).append((rf, k, n))
    return {kk: min(v) for kk, v in g.items()}
def show(name, res, extra=""):
    g = group(res); worst = min(res.items(), key=lambda kv: kv[1][0])
    firm = min(((rf, k) for k, (rf, n) in res.items() if 'peel' not in k and not k.startswith('P1 ')))
    print(f"\n### {name} {extra}\nmin all rows {worst[1][0]:.2f} ({worst[0][:60]}); min excluding peel and PSA rows {firm[0]:.2f} ({firm[1][:60]})")
    print("by part: " + "  ".join(f"{k} {v[0]:.2f}" for k, v in sorted(g.items(), key=lambda kv: int(''.join(c for c in kv[0] if c.isdigit())))))
def setdims(**kw):
    saved = {k: getattr(P, k) for k in kw}
    for k, v in kw.items(): setattr(P, k, v)
    return saved
if __name__ == "__main__":
    base = run(); show("V0 baseline CAD (mu 0.40, CG z 6.4 mm)", evaluate(base))
    # dimension variants on the baseline traces
    s = setdims(SAD_X1=0.1105); show("V2a saddle socket 20 -> 40 mm long (x 0.0665-0.1105); EST +5.3 g per saddle solid", evaluate(base)); setdims(**s)
    s = setdims(SAD_X1=0.1105, SAD_W=0.024); show("V2b saddle socket 40 mm long and 24 mm square; EST +9.5 g per saddle solid", evaluate(base)); setdims(**s)
    s = setdims(BLK_X0=0.2150, BLK_W=0.024); show("V3 root-block socket 71 mm long (x 0.215-0.286) and 24 mm square; EST +10 g per block solid", evaluate(base)); setdims(**s)
    s = setdims(SAD_X1=0.1105, SAD_W=0.024, BLK_X0=0.2150); P.BLK_W = 0.024; show("V2b+V3 together", evaluate(base)); setdims(**s); P.BLK_W = 0.019
    for mu in (0.30, 0.25):
        t = run(mu=mu); show(f"V1 pad face mu {mu:.2f} (UHMW-PE-class face, mu is the assumption; EST +0.2 g on four pads, K09-L D-105)", evaluate(t))
    t = run(cgz=0.0); show("V5 CG z centred (rearrange mass, CG z 0), mu 0.40", evaluate(t))
    t = run(mu=0.30, cgz=0.0); show("V6 mu 0.30 and CG z centred", evaluate(t))
