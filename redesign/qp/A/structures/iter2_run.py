"""Iteration 2 (QP-3): soft cage with stiff pitch bridge, 12x10 spar, CF-strip fins.  python -I iter2_run.py (numpy, scipy; ~1 min; prints markdown, writes iter2_run.md)"""
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, fe_a
from iter2_eval import *
CFG = dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(12e-3, 10e-3),
           vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025)
OUT = []
def P(s=""): print(s); OUT.append(s)
def tube(od, id_):
    I = math.pi/64*(od**4-id_**4); return math.pi/4*(od**2-id_**2), I, I/(od/2)
G = 9.81; KF = 1.5*1.15; KP = KF*1.25
def ms(a, s): return a/s-1
def rate(m): return "PASS" if m >= 0.15 else ("MARGINAL" if m >= 0 else "FAIL")
A12, I12, Z12 = tube(12e-3, 10e-3); A14, I14, Z14 = tube(14e-3, 12e-3); A6, I6, Z6 = tube(6e-3, 4.5e-3)
rho = 1600.0
# ---------------- mass
m = {}
m["Wing: XPS core"] = 95.3; m["Wing: spar 12x10 x 0.90 m"] = A12*rho*0.90*1e3; m["Wing: tape skin"] = 24.2
m["Wing: 4 PETG plugs + 2 elevon blocks"] = 14.0; m["Wing: epoxy EST"] = 8.0
A16, I16, Z16 = tube(16e-3, 14e-3)
m["Fins: 2 fin spar tubes 16x14 x 0.36 m (aft edge, foot on the end)"] = 2*A16*rho*0.36*1e3
m["Fins: XPS fairing 3 mm (both)"] = 2*0.0432*3e-3*30*1e3
m["Fins: tape skins 55 g/m2"] = 4*0.0432*55; m["Fins: 4 foot shoes (PETG 2 + EVA 0.5)"] = 10.0
m["Fins: 2 root blocks (PETG)"] = 8.0; m["Fins: 2 rib tubes 14x12 x 0.227 m"] = 2*A14*rho*0.227*1e3
m["Cage: 4 arms 12x10 x 0.245 m"] = 4*A12*rho*0.245*1e3; m["Cage: PETG hub"] = 16.0
m["Cage: bridge 12x10 x 0.16 m"] = A12*rho*0.16*1e3; m["Cage: 2 struts 6x4.5 x 0.33 m"] = 2*A6*rho*0.33*1e3
m["Cage: 3 saddles (PETG; rib saddles 60 mm wide)"] = 8.0; m["Cage: 4 motor cups (PETG)"] = 16.0; m["Cage: socket epoxy EST"] = 6.0
m["Hardware: screws, nuts, fillets, paint EST"] = 40.0
alloc = {"Wing": 220, "Fins": 70, "Cage": 135, "Hardware": 35}
grp = {k: sum(v for n, v in m.items() if n.startswith(k)) for k in alloc}
P("### Mass vs allocation (g)"); P("| Group | Iter 2 | Iter 1 | MASS-GATE |"); P("|---|---|---|---|")
it1 = {"Wing": 209, "Fins": 121, "Cage": 122, "Hardware": 40}
for k in alloc: P(f"| {k} | {grp[k]:.0f} | {it1[k]} | {alloc[k]} |")
P(f"| **Total** | **{sum(grp.values()):.0f}** | 492 | 460 |")
for n, v in m.items(): P(f"|   {n} | {v:.1f} | | |")
# ---------------- modes
r = evaluate("final", **CFG)
P("\n### Rotor bands and rpm source")
P(f"Hover 6,018 / 6,272 / 7,151 rpm (1.381 kg / 1.50 kg / 8 m/s lean at 1.3 W): `qp/A/prop_a.py` hover() at derate 0.93, lean scaled by sqrt(1.3). 1P {RPM_HOVER[0]/60:.0f}-{RPM_HOVER[2]/60:.0f} Hz, 2P {RPM_HOVER[0]/30:.0f}-{RPM_HOVER[2]/30:.0f} Hz. Cruise 7,300-7,600 rpm (QP-3 BOARD s1 item 2: `sitl/fu_level.py` with the APC V > 0 data; the 8,900-10,500 EST band is withdrawn): 1P {RPM_CRUISE[0]/60:.0f}-{RPM_CRUISE[2]/60:.0f}, 2P {RPM_CRUISE[0]/30:.0f}-{RPM_CRUISE[2]/30:.0f} Hz. Rule: f <= band_low/1.2 or f >= 1.2 x band_high for all four. That excludes **{LO_LIM:.0f}-{HI_LIM:.0f} Hz** for strongly coupled modes (coupling >= 0.5, D-185).")
P("\n### Modes with motor coupling >= 0.3, plus the fin and every mode in the excluded band with coupling >= 0.1 (coupling = mass-normalised |phi| summed at the four motors; arm modes 2.7-3.4)")
P("| Corner | f (Hz) | part | coupling | vs bands |"); P("|---|---|---|---|---|")
nweak = {}
for k in ("kd", "nom", "hi"):
    F, res, info = r[k]
    for (f, e, v, cx, cy) in res:
        c = float(max(cx, cy)); dom = max(e, key=e.get)
        show = (f > 2 and f < 700 and ((c >= 0.3 and (f < 100 or c >= 0.3)) or e.get("fin", 0) > 0.5 or (LO_LIM < f < HI_LIM and c >= 0.1)))
        if show and f < 700:
            if ok(f): st = "pass"
            else:
                st = f"in band, coupling {c:.1f}"; nweak.setdefault(k, []).append((round(f), c))
            if f < 100 or not ok(f) or e.get("fin", 0) > 0.5: P(f"| {k} | {f:.0f} | {dom} {100*e[dom]:.0f}% | {c:.1f} | {st} |")
P("\nSmallest margin among strongly coupled modes (>= 0.5): see the lowest-frequency rows; the highest strongly coupled mode below the bands and the lowest above them per corner:")
for k in ("kd", "nom", "hi"):
    F, res, info = r[k]
    below = max([f for (f, e, v, cx, cy) in res if 2 < f < 100 and max(cx, cy) >= 0.5]); above = min([f for (f, e, v, cx, cy) in res if f >= HI_LIM and max(cx, cy) >= 0.5])
    P(f"- {k}: highest coupled mode below the bands {below:.0f} Hz (limit {LO_LIM:.1f}, margin {100*(LO_LIM/below-1):.0f} %); lowest above {above:.0f} Hz (limit {HI_LIM:.0f})")
P("\n### Forced response, no balancing credit (U 1.0 g mm per rotor EST; ISO G16 prop alone 0.27; 2P ripple 5 % of thrust EST; damping 1 % EST); worst over the D-185 sweep 6,000-10,500 rpm in 250 rpm steps plus the hover and cruise (7,300 / 7,450 / 7,600) points, all three corners; FC acceleration vs 30 m/s2")
for k in ("kd", "nom", "hi"): P(f"- {k}: {float(r['acc'][k]):.1f} m/s2, MS {30/float(r['acc'][k])-1:+.2f}")
# ---------------- static hub rotation
def hubrot(kind):
    F, res, info = r[kind]; idx = F._idx; N = len(idx); K = F._K
    fixed = list(range(6*idx["s+0.000"], 6*idx["s+0.000"]+6)); free = [q for q in range(6*N) if q not in fixed]
    def solve(fx):
        f = np.zeros(6*N)
        for sy in (1, -1):
            for sz in (1, -1):
                nd = idx[f"m{sy:+d}{sz:+d}"]; f[6*nd:6*nd+3] += fx(sy, sz)
        u = np.zeros(6*N); u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free]); h = idx["hub"]
        return math.degrees(u[6*h+4]), math.degrees(u[6*h+3]), 1e3*np.linalg.norm(u[6*h:6*h+3])
    Tdif = 2.44/(4*0.156)
    pitch = solve(lambda sy, sz: np.array([sz*Tdif, 0, 0]))
    t = 0.35/(4*0.2763)
    yaw = solve(lambda sy, sz: np.array([0, -sz*0.156/0.2763*t, sy*0.228/0.2763*t]))
    return pitch, yaw
for k in ("kd", "nom"):
    p, y = hubrot(k)
    P(f"\nStatic cage rotation vs the spar centre ({k}): pure pitch moment 2.44 N m: {p[0]:.2f} deg (iteration 1: 2.0 deg); yaw/roll about the thrust axis, 0.35 N m: {y[1]:.2f} deg")
open("iter2_run.md", "w").write("\n".join(OUT))
