"""T-071b Part B step 3: pad-outboard tip sizing (T-068 D2): static edge angle toward the CG side (A-P9 >= 30 deg, target edge >= 30.5 deg) and the dynamic lean scan, at mu 0.30 and 0.40.
    python -I landing_tip_b.py > out.txt     (about 3 min, multiprocessing)
Category: rigid-body dynamics (landing_a.simulate, same model as landing_tip_options_a.py) + static geometry.  Illustrative screening, not a design decision.
Static: atan((z_edge - cg_z) / (x_ground - cg_x)); the pivot is the pad's outer edge on the CG side (T-068 s4 definition), the pad-centre value is the conservative bound.
CG: redesign/qp/A/sitl/cad_mass.json (CAD, 1.273 kg); the post-T-067 CG is not available ('-').  Pad: 12 mm in z (electrical.py), D2 = centre z 0.189 (edge 0.195), ground plane x 0.3415 (pad 34 mm long, D3 cup)."""
import sys, os, math
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import landing_a as L
g = L.cad_geom(); cg = g['cg']
VAR = [("CAD as drawn (x 0.3375, pad centre z 0.177, edge 0.183)", dict(xg=g['x_foot'], zc=g['z_foot'])),
       ("T-068 D2 (x 0.3415, pad centre z 0.189, edge 0.195)", dict(xg=0.3415, zc=0.189)),
       ("D2 + 3 mm more track (edge 0.198)", dict(xg=0.3415, zc=0.192)),
       ("D2 and CG z centred (0): sensitivity to the unmeasured CG z", dict(xg=0.3415, zc=0.189, cgz=0.0))]
MUS = (0.40, 0.30)
LATS = (0.16, 0.40, 0.52, 0.70); LEANS = tuple(range(0, 31, 2))
def stat(v):
    cz = v.get('cgz', cg[2]); h = v['xg']-cg[0]
    return [math.degrees(math.atan2(v['zc']+0.006-cz, h)), math.degrees(math.atan2(v['zc']-cz, h))]
def job(a):
    vi, mu, lat, lean = a; v = VAR[vi][1]
    c = [cg[0], cg[1], v.get('cgz', cg[2])]
    q = L.simulate(Fp=30.0, v_sink=0.34, th_n=lean, drift=lat, drift_dir=0.0, dt=2e-4, T=1.2, z_foot=v['zc'], x_foot=v['xg'], mu=mu, cg_override=c)
    return a, q['tilt_end']
if __name__ == "__main__":
    print("# T-071b step 3: tip sizing.  CAD CG x %.2f mm, z %.2f mm (cad_mass.json), pad half height 6 mm, sink 0.34 m/s, plateau 30 N, lean toward the CG side (narrow axis), tilt_end < 45 deg = stays up" % (cg[0]*1e3, cg[2]*1e3))
    print("variant | static edge toward CG side (deg) | static pad centre (deg) | max upright lean (deg, grid 2) at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s for mu 0.40 || mu 0.30")
    jobs = [(vi, mu, lat, ln) for vi in range(len(VAR)) for mu in MUS for lat in LATS for ln in LEANS]
    with Pool() as p: R = dict(p.map(job, jobs, chunksize=4))
    for vi, (n, v) in enumerate(VAR):
        s = stat(v); cols = []
        for mu in MUS:
            ths = []
            for lat in LATS:
                ok = [l for l in LEANS if all(R[(vi, mu, lat, k)] < 45 for k in LEANS if k <= l)]; ths.append(max(ok) if ok else -1)
            cols.append(" / ".join(f">={LEANS[-1]}" if t == LEANS[-1] else str(t) for t in ths))
        print(f"{n:62s} | {s[0]:5.2f} | {s[1]:5.2f} | {cols[0]} || {cols[1]}")
