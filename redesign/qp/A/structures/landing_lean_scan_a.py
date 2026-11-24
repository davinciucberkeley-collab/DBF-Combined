"""T-064r F2/F4: narrow-axis lean x lateral-speed tip-over scan on the CAD ground plane and CG (rigid-body dynamics, landing_a.py).
python -I landing_lean_scan_a.py [--legacy] [--dt 2e-4] > out.txt
Case: sink 0.34 m/s (largest peak sink in the last second of the 29 SITL touchdown records), plateau 30 N, mu 0.40, lean about body y (narrow axis, tips about a
fin-tip pad), lateral speed along the lean axis.  Four sign combinations: lean sign +/- (toward +z / -z of the body, CG z offset is +6.4 mm) x lateral
travel in the same direction as the lean ('with') or against it ('against').  Foot contact point: 'ctr' pad centre z 0.177, 'edge' outer pad edge z 0.183
(a foam pad rolling over its outer edge is the physical pivot; the centre is the conservative reading).  Tipped = end tilt > 45 deg.
No thrust or control after 0.6 s (landing_a.py convention): this is the pessimistic bound; SITL (a_plant.py) adds artificial angular damping."""
import math, sys, os
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing_a as L
DT = 2e-4
if "--dt" in sys.argv: DT = float(sys.argv[sys.argv.index("--dt")+1])
LATS = (0.0, 0.16, 0.30, 0.40, 0.52, 0.60, 0.70)
LEANS = tuple(range(0, 26, 2))
def run(a):
    sg, mode, foot, lat, lean = a
    zf = L.geom()['z_foot'] if foot == 'ctr' else L.geom()['z_edge']
    dd = (0.0 if sg > 0 else math.pi) if mode == 'with' else (math.pi if sg > 0 else 0.0)
    q = L.simulate(Fp=30.0, v_sink=0.34, th_n=lean*sg, drift=lat, drift_dir=dd, dt=DT, T=1.2, z_foot=zf)
    return a, q['tilt_end'], q['n_peak'], q['side'].max()
if __name__ == "__main__":
    jobs = [(sg, mode, foot, lat, lean) for sg in (1, -1) for mode in ('with', 'against') for foot in ('ctr', 'edge') for lat in LATS for lean in LEANS]
    with Pool() as p: res = p.map(run, jobs, chunksize=4)
    R = {r[0]: r for r in res}
    print(f"# geometry {'legacy' if L.LEGACY else 'CAD'}, dt {DT}, T 1.2 s, sink 0.34, Fp 30 N, mu 0.40; tipped = end tilt > 45 deg; entries = largest lean (deg, grid step 2) that stays upright from 0 upward")
    print("sign mode    foot  " + "  ".join(f"lat {l:.2f}" for l in LATS))
    for sg in (1, -1):
        for mode in ('with', 'against'):
            for foot in ('ctr', 'edge'):
                row = []
                for lat in LATS:
                    ok = [l for l in LEANS if all(R[(sg, mode, foot, lat, k)][1] < 45 for k in LEANS if k <= l)]
                    mx = max(ok) if ok else -1
                    row.append(">=24" if mx == LEANS[-1] else f"{mx:4d}")
                print(f"{sg:+d}   {mode:8s} {foot:5s} " + "      ".join(row))
    print("\n# raw: sign mode foot lat lean tilt_end n_peak side_N")
    for k in jobs: print(*k, f"{R[k][1]:.1f} {R[k][2]:.2f} {R[k][3]:.1f}")
