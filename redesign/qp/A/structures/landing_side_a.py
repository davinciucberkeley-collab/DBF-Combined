"""T-064 landing side-load capacity and sensitivity (rigid-body dynamics + hand-calculation part capacities).  python -I landing_side_a.py
Imports landing_a.py (same folder).  Prints: (1) part capacities against the worst simulated foot loads, (2) pad-friction sweep with the mu at which the
rib-root RF reaches 1, (3) plateau sweep, (4) touchdown-envelope cases taken from the SITL touchdown records.  Labels: EST allowables (no coupon), CALC.
Run time about 3 min."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing_a as L
KP = 1.5*1.15*1.25
def row(name, kw, Fp=30.0, mu=L.MU):
    r = L.simulate(Fp=Fp, mu=mu, **kw)
    return r
CASES = [("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)),
         ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2))]
print("## 1. Part capacity at the worst simulated foot load (30 N plateau, mu 0.40), RF = capacity / demand, factors as structures_a.py")
r = row("worst", CASES[1][1]); fn, side = r['F'].max(), r['side'].max()
res = math.hypot(fn, side)
print(f"worst foot: normal {fn:.1f} N, side {side:.1f} N (resultant {res:.1f} N); both maxima taken as simultaneous (conservative)")
print(f"- shoe bond on fin corner, 1,500 mm2, allowable 0.1 MPa (C6 paper/foam value EST): {res*KP/1.5e-3/1e3:.1f} kPa -> RF {0.1e6/(res*KP/1.5e-3):.2f}")
brg = 2*side*KP/(0.065*0.0233); print(f"- foam bearing at the fin slot (65 x 23 mm, both feet {side:.1f} N), allowable 120 kPa EST: {brg/1e3:.1f} kPa -> RF {120e3/brg:.2f}")
Mfin = side*0.18; sig_f = Mfin/(2*0.1e-3*0.12*7.55e-3)*1.5*1.15
print(f"- fin skin 0.1 mm CFRP bending at the root, M = {side:.1f} x 0.18 = {Mfin:.2f} N m (structures_a.py s6 geometry), allowable 450 MPa EST: {sig_f/1e6:.1f} MPa -> RF {450e6/sig_f:.1f}")
Tq = 0.18; Fcap_t = L.TAU_RIB*L.RIB_J/((L.RIB_OD/2)*L.KF_RIB)/Tq
print(f"- rib torsion alone, ONE foot loaded sideways, lever 0.18 m, 30 MPa EST: capacity {Fcap_t:.1f} N per foot (structures_a.py s6 row: 15 N gives RF 1.60); at 41.3 MPa (Tap Plastics pultruded shear sheet, checked 2026-11-18, test method not stated): {41.3e6*L.RIB_J/((L.RIB_OD/2)*L.KF_RIB)/Tq:.1f} N")
Fcap_b = L.SIG_RIB*L.RIB_Z/L.KF_RIB/(2*(0.30-L.RIB_X0)); print(f"- rib root bending alone, both feet sideways, arm {0.30-L.RIB_X0:.4f} m, 350 MPa EST: capacity {Fcap_b:.1f} N per foot")
print("- rib root, combined bending + torsion + axial, all four feet resolved in the body frame each time step (landing_a.py): see the RF column below; minimum is the governing number")
print("\n## 2. Pad friction sweep (30 N plateau): side load per foot N / rib RF")
mus = (0.30, 0.40, 0.50, 0.60, 0.70)
tab = {}
for name, kw in CASES:
    out = []
    for m in mus:
        q = row(name, kw, mu=m); out.append((m, q['side'].max(), q['rib_rf'], q['F'].max(), q['tilt_end'], q['dmax_mm'].max()))
    tab[name] = out
    print(f"{name:28s} " + "  ".join(f"mu {m:.2f}: {s:5.1f} N RF {rf:5.2f}" for m, s, rf, fn_, t, d in out))
for name, out in tab.items():
    cr = [(out[i], out[i+1]) for i in range(len(out)-1) if out[i][2] >= 1.0 > out[i+1][2]]
    if cr:
        a, b = cr[0]; mu1 = a[0] + (a[2]-1.0)/(a[2]-b[2])*(b[0]-a[0]); print(f"mu at RF = 1 (linear interp.) {name}: {mu1:.2f}")
    else:
        print(f"RF stays {'>= 1' if out[-1][2] >= 1 else '< 1'} over mu 0.30-0.70: {name} (RF at 0.70 = {out[-1][2]:.2f})")
print("\n## 3. Plateau sweep at mu 0.40 (foot geometry lever: pad area x 0.17 MPa): worst stroke / n / side / rib RF over the four cases + hard narrow + drift")
allc = CASES + [("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)), ("hard level", dict(v_sink=1.2))]
for Fp in (24.0, 27.0, 30.0):
    rs = [row(n, kw, Fp=Fp) for n, kw in allc]
    print(f"Fp {Fp:4.0f} N: stroke {max(q['dmax_mm'].max() for q in rs):5.1f} mm  n {max(q['n_peak'] for q in rs):5.2f}  side {max(q['side'].max() for q in rs):5.1f} N  rib RF min {min(q['rib_rf'] for q in rs):5.2f}  tilt_end max {max(q['tilt_end'] for q in rs):.1f}")
print("\n## 4. Touchdown envelopes: controlled (SITL touchdown records, 29 runs) and stated structural limits")
env = [("SITL max: sink .35, lat .52 (x), lean 0", dict(v_sink=0.35, drift=0.52, drift_dir=0.0)),
       ("SITL max: sink .35, lat .52 (y), lean 0", dict(v_sink=0.35, drift=0.52, drift_dir=math.pi/2)),
       ("SITL lean 29 narrow, sink .35, lat .52 (x)", dict(v_sink=0.35, th_n=29.1, drift=0.52, drift_dir=0.0)),
       ("SITL lean 29 wide, sink .35, lat .52 (y)", dict(v_sink=0.35, th_w=29.1, drift=0.52, drift_dir=math.pi/2)),
       ("SITL lean 19 wide, sink .35, lat .52 (y)", dict(v_sink=0.35, th_w=18.8, drift=0.52, drift_dir=math.pi/2))]
for n, kw in env:
    q = row(n, kw)
    print(f"{n:44s} stroke {q['dmax_mm'].max():5.1f} mm  n {q['n_peak']:.2f}  Fmax {q['F'].max():5.1f} N  side {q['side'].max():5.1f} N  tilt_end {q['tilt_end']:5.1f}  drift {q['drift_end']*1e3:4.0f} mm  rib RF {q['rib_rf']:.2f}")
