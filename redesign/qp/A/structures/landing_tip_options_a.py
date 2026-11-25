"""T-064r ladder support: static tip-over (A-P9 >= 30 deg) and dynamic lean threshold for foot-track / CG variants (illustrative screening).  python -I landing_tip_options_a.py
Static: atan((z_edge - cg_z toward the CG side) / (x_ground - cg_x)).  Dynamic: narrow-axis lean x lateral speed (lean and travel toward +z, the CG side), sink 0.34, mu 0.40, 30 N, as landing_lean_scan_a.py,
foot contact at the pad centre (z_foot).  Variants: track +dz (pad z shifted outward by dz, i.e. fin tube longer / shoe plate wider), CG z centred, CG moved aft by dx."""
import sys, os, math
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import landing_a as L
g = L.cad_geom(); cg = g['cg']; xg = g['x_foot']
def stat(dz=0.0, cgz=None, dx=0.0, dxg=0.0):
    cz = cg[2] if cgz is None else cgz; h = xg+dxg-(cg[0]+dx)
    return [math.degrees(math.atan2(g['z_edge']+dz-cz, h)), math.degrees(math.atan2(g['z_foot']+dz-cz, h))]
VAR = [("CAD as drawn", dict()), ("track +6 mm (pad edge z 0.189)", dict(dz=0.006)), ("track +10 mm", dict(dz=0.010)), ("track +13 mm (31 deg)", dict(dz=0.013)),
       ("CG z centred (0)", dict(cgz=0.0)), ("CG z centred and track +3 mm", dict(cgz=0.0, dz=0.003)), ("CG 10 mm aft", dict(dx=0.010)), ("ground plane 6 mm forward (pad 24 mm long, stroke -6 mm)", dict(dxg=-0.006)),
       ("track +6 mm and CG 5 mm aft", dict(dz=0.006, dx=0.005))]
LATS = (0.16, 0.40, 0.52, 0.70); LEANS = tuple(range(0, 31, 2))
def job(a):
    vi, lat, lean = a; kw = VAR[vi][1]
    q = L.simulate(Fp=30.0, v_sink=0.34, th_n=lean, drift=lat, drift_dir=0.0, dt=2e-4, T=1.2, z_foot=g['z_foot']+kw.get('dz', 0.0),
                   x_foot=xg+kw.get('dxg', 0.0), cg_override=[cg[0]+kw.get('dx', 0.0), cg[1], cg[2] if kw.get('cgz') is None else kw['cgz']])
    return a, q['tilt_end']
if __name__ == "__main__":
    print("variant | static edge toward CG side (deg) | static pad centre | max upright lean at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s (deg, grid 2)")
    jobs = [(vi, lat, ln) for vi in range(len(VAR)) for lat in LATS for ln in LEANS]
    with Pool() as p: R = dict(p.map(job, jobs, chunksize=4))
    for vi, (n, kw) in enumerate(VAR):
        s = stat(**kw); ths = []
        for lat in LATS:
            ok = [l for l in LEANS if all(R[(vi, lat, k)] < 45 for k in LEANS if k <= l)]; ths.append(max(ok) if ok else -1)
        print(f"{n:55s} | {s[0]:5.2f} | {s[1]:5.2f} | " + " / ".join(f">={LEANS[-1]}" if t == LEANS[-1] else str(t) for t in ths))
