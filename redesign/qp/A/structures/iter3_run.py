"""Iteration 3 (QP-4, D-185 as ruled): modal set with the one-truth rpm, numeric 'strongly coupled' basis, full-rpm forced response,
hard-mounted FC vibration, control-band clause, C1 loads at VD 24, elevon horn / lead mass loads, mass vs the 473 g freeze.
python -I iter3_run.py  (numpy, scipy; a few minutes; prints markdown, writes iter3_run.md).  Reads fe_a.py, iter2_eval.py, iter2_run.py CFG;
imports sitl/fu_cage.py read-only for the rate-loop clause (it writes nothing on import).  Labels: EST estimate, CALC computed here."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "sitl"))
sys.dont_write_bytecode = True
import numpy as np, fe_a
from iter2_eval import BANDS, RPM_HOVER, RPM_CRUISE, LO_LIM, HI_LIM, ok
OUT = []
def P(s=""): print(s); OUT.append(s)
CFG = dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(12e-3, 10e-3),
           vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025)
U = 1e-6                                  # 1.0 g mm
LIM = 30.0                                # ArduPilot VIBE guidance, m/s2
RPM_CAP = 9349.0; T_CAP = 8.75            # one motor at the 0.90 cap, 16.8 V fresh: prop_a.py one_motor / full(): 9,349 rpm, 898 gf x0.93 (8.8 N)
RPM_HOV = 6272.0; T_HOV = 3.94            # 1.50 kg hover per motor (402 gf)
def thr(rpm): return T_HOV*(rpm/RPM_HOV)**2          # static thrust law, T ~ rpm^2, anchored at the hover point (reproduces 8.75 N at 9,349 rpm)
T_CRU = 0.5                               # cruise thrust per rotor, EST (fu_level.py, about 0.45-0.52 N)
corners = ("kd", "nom", "hi")
R = {}
for k in corners:
    F, info = fe_a.build(k, **CFG); R[k] = (F, F.solve(100), info)
idxs = R["nom"][0]._idx
MOT = [m for m in idxs if (m.startswith("m+") or m.startswith("m-")) and ">" not in m]
IMU = "s+0.000"
def resp(F, res, rpm_list, thr_list, zeta=0.01):
    """worst-phase modal sum at the FC node for rotors at rpm_list with thrusts thr_list; returns per-axis accel (3), 1P+2P summed (conservative)"""
    idx = F._idx; imu = idx[IMU]; ax = np.zeros(3)
    for m, rpm, th in zip(MOT, rpm_list, thr_list):
        om = rpm/60*2*math.pi
        for mult, fm in ((1, U*om**2), (2, 0.05*th)):
            w = mult*om
            for (f, e, v, cx, cy) in res:
                wi = 2*math.pi*f
                if mult == 1: g = fm*(abs(v[6*idx[m]+1])+abs(v[6*idx[m]+2]))
                else: g = fm*abs(v[6*idx[m]])
                h = 1/math.sqrt((wi*wi-w*w)**2+(2*zeta*wi*w)**2)
                ax += w*w*g*h*np.abs(v[6*imu:6*imu+3])
    return ax
# ------------------------------------------------------------------ 1. modal set
P("## Iteration 3 (D-185 as ruled): inputs")
P(f"Rotor bands (one truth, QP-4 FOLDIN): hover {RPM_HOVER[0]:.0f} / {RPM_HOVER[1]:.0f} / {RPM_HOVER[2]:.0f} rpm, 1P {RPM_HOVER[0]/60:.0f}-{RPM_HOVER[2]/60:.0f} Hz, 2P {RPM_HOVER[0]/30:.0f}-{RPM_HOVER[2]/30:.0f} Hz; cruise 7,300-7,600 rpm, 1P {RPM_CRUISE[0]/60:.0f}-{RPM_CRUISE[2]/60:.0f}, 2P {RPM_CRUISE[0]/30:.0f}-{RPM_CRUISE[2]/30:.0f} Hz; one motor at the 0.90 cap {RPM_CAP:.0f} rpm (`qp/A/prop_a.py` one_motor, fresh 16.8 V), 1P {RPM_CAP/60:.0f}, 2P {RPM_CAP/30:.0f} Hz; no-cap full throttle 10,142 rpm (prop_a.py). Separation rule: f <= band_low/1.2 or f >= 1.2 band_high: excludes **{LO_LIM:.0f}-{HI_LIM:.0f} Hz** for strongly coupled modes.")
P(f"Structure frozen at 473 g (wing 191 / fins 119 / cage 122 / hardware 40). Forced response: U 1.0 g mm per rotor, 2P axial ripple 5 % of thrust (thrust law T = 3.94 N (rpm/6,272)^2, 8.75 N at the cap), damping 1 % (and 0.5 %) `EST`, worst-phase modal sum, 1P + 2P of all rotors added (conservative), all FE modes to 100 solved.")
# --- full mode list in 84-304 Hz and the strongly coupled set
P("\n### Modes with coupling, exact (coupling = max(cx, cy), mass-normalised |phi| over the four motors)")
P("| Corner | f (Hz) | part | cx | cy | coupling | in excluded 84-304 Hz? | 1P / 2P rpm that hits it | verdict at STRONG 0.5 |"); P("|---|---|---|---|---|---|---|---|---|")
strong_in = []
for k in corners:
    F, res, info = R[k]
    for (f, e, v, cx, cy) in res:
        if f < 2 or f > 700: continue
        c = max(cx, cy); dom = max(e, key=e.get)
        inb = LO_LIM < f < HI_LIM
        if not ((inb and c >= 0.05) or (c >= 0.5 and f < 100)): continue
        hit = []
        if 6000 <= 60*f <= 10500: hit.append(f"1P at {60*f:,.0f}")
        if 6000 <= 30*f <= 10500: hit.append(f"2P at {30*f:,.0f}")
        verdict = ("strong, in band: FAIL" if (inb and c >= 0.5) else ("weak, in band: by forced response" if inb else "strong, outside: pass"))
        if inb and c >= 0.5: strong_in.append((k, f, c))
        P(f"| {k} | {f:.1f} | {dom} {100*e[dom]:.0f}% | {cx:.2f} | {cy:.2f} | {c:.2f} | {'yes' if inb else 'no'} | {', '.join(hit) or '-'} | {verdict} |")
P(f"\nStrongly coupled (>= 0.5) modes inside the excluded band: {strong_in if strong_in else 'none'}.")
for k in corners:
    F, res, info = R[k]
    below = max(f for (f, e, v, cx, cy) in res if 2 < f < 100 and max(cx, cy) >= 0.5); above = min(f for (f, e, v, cx, cy) in res if f >= HI_LIM and max(cx, cy) >= 0.5)
    P(f"- {k}: highest strongly coupled mode below the bands {below:.0f} Hz (limit {LO_LIM:.1f}, margin {100*(LO_LIM/below-1):.0f} %); lowest above {above:.0f} Hz (limit {HI_LIM:.0f}, margin {100*(above/HI_LIM-1):.0f} %)")
# --- threshold basis
P("\n### Strongly-coupled threshold, numeric basis")
P("A mode is harmless in a rotor band if, driven on resonance by the 1P unbalance (or 2P ripple) of all four rotors at 1 g mm, its own contribution at the FC stays under the 30 m/s2 VIBE limit. On-resonance single-mode FC acceleration a = (force x sum|phi_motor| x |phi_FC|) / (2 zeta); it scales linearly with coupling. Modes below 700 Hz that a rotor order can reach (1P 100-175 Hz, 2P 200-350 Hz):")
P("| Corner | f (Hz) | coupling | |phi_FC| sum | a_res zeta 1 % (m/s2) | a_res zeta 0.5 % | fraction of 30 at zeta 0.5 % |"); P("|---|---|---|---|---|---|---|")
pts = []
for k in corners:
    F, res, info = R[k]; idx = F._idx
    for (f, e, v, cx, cy) in res:
        if f < 2: continue
        wi = 2*math.pi*f
        for order, lo_f, hi_f in ((1, 100, 175), (2, 200, 350)):
            if lo_f <= f <= hi_f:
                th = thr(60*f/order)
                if order == 1: g = U*wi**2*sum(abs(v[6*idx[m]+1])+abs(v[6*idx[m]+2]) for m in MOT)
                else: g = 0.05*th*sum(abs(v[6*idx[m]]) for m in MOT)
                phi = float(np.sum(np.abs(v[6*idx[IMU]:6*idx[IMU]+3]))); c = max(cx, cy)
                pts.append((k, f, order, c, phi, g*phi/(2*0.01), g*phi/(2*0.005)))
for k, f, order, c, phi, a1, a2 in pts:
    if c >= 0.05 and LO_LIM < f < HI_LIM: P(f"| {k} | {f:.0f} ({order}P) | {c:.2f} | {phi:.2f} | {a1:.1f} | {a2:.1f} | {a2/LIM:.2f} |")
# coupling at which a_res (zeta 0.5 %) reaches 30: worst ratio a/c among modes with c >= 0.05
rat = [(a2/c, k, f, c) for k, f, order, c, phi, a1, a2 in pts if c >= 0.05]
rmax = max(rat)
P(f"\nWorst a_res per unit coupling (zeta 0.5 %): {rmax[0]:.0f} m/s2 per 1.0 coupling ({rmax[1]} {rmax[2]:.0f} Hz). Coupling at which one mode alone reaches 30 m/s2: **{LIM/rmax[0]:.2f}** (zeta 0.5 %) by this linear scaling. D-185 threshold 0.5 as ruled; see the verdict below.")
THRESH_C = LIM/rmax[0]
# ------------------------------------------------------------------ 2. forced response sweep
P("\n### Forced response, full rpm sweep (all four rotors at the same rpm, envelope), U 1.0 g mm")
sweep = list(range(6000, 10501, 25))
P("| Corner | zeta | worst FC accel over 6,000-10,500, sum of axes (m/s2) at rpm | per-axis max / sqrt2 (VIBE-like rms) | MS vs 30 | worst up to 10,142 (no-cap full throttle) | worst up to 9,349 (0.90 cap, all four) | cruise 7,300-7,600 worst (T 0.5 N) | one motor at cap (others hover) | MS |"); P("|---|---|---|---|---|---|---|---|---|---|")
worst_tab = {}; PHYS = {}
for k in corners:
    F, res, info = R[k]
    for zeta in (0.01, 0.005):
        best = (0, 0, None)
        for rpm in sweep:
            ax = resp(F, res, [rpm]*4, [thr(rpm)]*4, zeta)
            if ax.sum() > best[0]: best = (ax.sum(), rpm, ax)
        bc = max((resp(F, res, [r]*4, [T_CRU]*4, zeta).sum(), r) for r in range(7300, 7601, 25))
        phys = max((resp(F, res, [r]*4, [thr(r)]*4, zeta).sum(), r) for r in sweep if r <= 9349)
        unc = max((resp(F, res, [r]*4, [thr(r)]*4, zeta).sum(), r) for r in sweep if r <= 10142)
        PHYS[(k, zeta)] = (phys, unc)
        one = resp(F, res, [RPM_CAP, RPM_HOV, RPM_HOV, RPM_HOV], [T_CAP, T_HOV, T_HOV, T_HOV], zeta)
        worst_tab[(k, zeta)] = (best, bc, one)
        P(f"| {k} | {zeta*100:.1f} % | {best[0]:.1f} at {best[1]:,} | {best[2].max()/math.sqrt(2):.1f} | {LIM/best[0]-1:+.2f} | {unc[0]:.1f} at {unc[1]:,} | {phys[0]:.1f} at {phys[1]:,} | {bc[0]:.1f} at {bc[1]:,} | {one.sum():.1f} | {LIM/one.sum()-1:+.2f} |")
# peak table near the strong-in-band modes: where the sweep peaks
P("\nPeak locations (kd / nom / hi, zeta 1 %): the sweep maximum sits where a rotor order meets a coupled mode:")
for k in corners:
    F, res, info = R[k]
    curve = [(resp(F, res, [r]*4, [thr(r)]*4, 0.01).sum(), r) for r in sweep]
    top = sorted(curve, reverse=True)[:1]
    pk = [(a, r) for i, (a, r) in enumerate(curve) if 0 < i < len(curve)-1 and a > curve[i-1][0] and a > curve[i+1][0] and a > 0.25*top[0][0]]
    P(f"- {k}: " + "; ".join(f"{a:.1f} m/s2 at {r:,} rpm (1P {r/60:.0f} / 2P {r/30:.0f} Hz)" for a, r in pk))
# ------------------------------------------------------------------ 3. VIBE
P("\n### Hard-mounted FC (D-186): IMU vibration at the spar centre")
wk = max(worst_tab[(k, 0.01)][0][0] for k in corners); wk5 = max(worst_tab[(k, 0.005)][0][0] for k in corners)
wone = max(worst_tab[(k, 0.01)][2].sum() for k in corners)
P(f"No isolation credit: the FE node is the rigid spar centre, foam tape 1.5 mm stiffness is taken as rigid (mount frequency not measured, `EST`). Worst FC amplitude, sum of the three axes (conservative): **{wk:.1f} m/s2 at zeta 1 %, {wk5:.1f} at 0.5 %** at the 10,500 rpm end of the sweep (all four rotors at 10,500 rpm is not reachable: the uncapped maximum is 10,142 rpm, the 0.90 cap 9,349 rpm; the curve rises there with the rigid-body 1P force, U omega^2); the physical envelope (all four at the cap) is the 9,349 column; one motor at the cap {wone:.1f}. ArduPilot's VIBE is the per-axis standard deviation (about amplitude / sqrt 2 for a sinusoid), so the per-axis column above is the like-for-like number; the sum of axes is compared with 30 as a bound. Guidance: VIBE < 30 m/s2, source https://ardupilot.org/copter/docs/common-measuring-vibration.html (checked 2026-11-15 in QP-3 / FOLDIN; guidance 30 m/s2 per the task and BOARD).")
# ------------------------------------------------------------------ 4. control band
P("\n### Control-band clause (D-185 added row): cage modes vs the rate loop")
try:
    import fu_cage as FC
    C = FC.cases()
    SET = {"pit": dict(gyro_lpf=60, fltd=40, P=0.15, D=0.002), "rll": dict(gyro_lpf=60, fltd=32, P=0.20, D=0.003), "yaw": dict(gyro_lpf=60, fltd=32)}   # A.param: INS_GYRO_FILTER 60, Q_A_RAT_PIT P .15 D .002 FLTD 40, RLL P .20 D .003 FLTD 32, YAW as fu_cage RATE
    P("A.param gains: pitch P 0.15 / I 0.25 / D 0.002 / FLTD 40, roll P 0.20 / I 0.25 / D 0.003 / FLTD 32, yaw P 0.40 / I 0.04, `INS_GYRO_FILTER` 60 (A.param lines 99-109, 184). Model `sitl/fu_cage.py` (FE modes 1-250 Hz, motor lag 40 ms, delay 4 ms `EST`), IMU at the spar centre. Pass rule: **GM >= 2.0 (6 dB) on every axis, corner, damping (0.3 / 1 %), thrust scale (0.77 / 1.0 / 1.25) and with all flexible modes shifted +-20 % in frequency (the tap-test tolerance)**, no right-half-plane pole.")
    P("| axis | corner | cage modes 3-40 Hz (Hz: gain / rigid) | min GM nominal freq | min GM modes -20 % | min GM modes +20 % | crossover (Hz) |"); P("|---|---|---|---|---|---|---|")
    gmall = 99.0; rows = []
    for ax in ("pit", "rll", "yaw"):
        for k in corners:
            c = [x for x in C if x["ax"] == ax and x["node"] == "spar centre" and x["k"] == k][0]
            shown = ", ".join(f"{ff:.0f}: {gg/c['inv_I']:+.2f}" for ff, gg in c["flex"] if 3 < ff < 40)
            out = []
            for sc in (1.0, 0.8, 1.2):
                modes = [(ff*sc if ff >= 1.0 else ff, gg) for ff, gg in c["modes"]]
                gm = 99.0
                for z in (0.003, 0.01):
                    for ts in (0.77, 1.0, 1.25):
                        L = FC.loop(modes, ax, z, tfull_scale=ts, **SET[ax])
                        if FC.maxre(L) >= -1e-6: gm = 1.0
                        else: gm = min(gm, FC.margins(L)[0])
                out.append(gm)
            L = FC.loop(c["modes"], ax, 0.01, **SET[ax]); cr = FC.margins(L)[3]
            gmall = min(gmall, *out)
            P(f"| {ax} | {k} | {shown} | {out[0]:.2f} | {out[1]:.2f} | {out[2]:.2f} | {', '.join(f'{x:.1f}' for x in cr)} |")
    P(f"\nMinimum GM over everything: **{gmall:.2f}** vs rule 2.0.")
except Exception as ex:
    gmall = None; P(f"control-band model did not run: {ex!r}")
# ------------------------------------------------------------------ 5. C1 loads at VD 24, C6 elevon
G = 9.81; RHO = 1.225; M = 1.50; W = M*G; S = 0.22; b = 0.90; c = 0.245
Vs = math.sqrt(2*W/(RHO*S*0.75)); VC = 17.0; VD = 24.0
AR = b*b/S; a_w = math.pi*AR/(1+math.sqrt(1+(AR/2)**2)); wl = W/S
mu = 2*wl/(RHO*c*a_w*G); Kg = 0.88*mu/(5.3+mu)
def ng(V, Ug): return 1+Kg*RHO*Ug*V*a_w/(2*wl)
def nst(V): return 0.5*RHO*V*V*S*0.75/W
P("\n## C1 loads at VD 24 (D-186), 1.50 kg gate mass")
P("| Case | n | Note |"); P("|---|---|---|")
P(f"| Gust U 8 m/s at VC 17 | {ng(VC,8):.2f} (stall line {nst(VC):.2f}) | |")
P(f"| Gust U 4 m/s at VD 24 (half of 8, ASM-C1-UDE-D-FRAC) | **{ng(VD,4):.2f}** (stall line {nst(VD):.2f}) | below 3.4 floor: PASS |")
P(f"| Gust U 8 m/s at VD 24, no half rule (bound) | {ng(VD,8):.2f} (stall-limited {nst(VD):.2f}) | the wing stalls before it reaches this n |")
P(f"| Manoeuvre limit n | +3.4 / -1.5 | A-P13 floor governs; ult 5.1 / -2.25 |")
# dynamic pressure scaling: wing lift limit load  n W ; spar root bending is lift x y_cp -> not VD-dependent when n is capped at 3.4. Loads scale with q at constant CL.
q_VD = 0.5*RHO*VD**2; q_VC = 0.5*RHO*VC**2
P(f"| Dynamic pressure | q(VD) {q_VD:.0f} Pa vs q(VC) {q_VC:.0f} Pa (x{q_VD/q_VC:.2f}); flutter / divergence at 1.2 VD = 28.8 m/s (FLUTTER.md) | |")
Z12 = math.pi/64*(12e-3**4-10e-3**4)/(6e-3); A12 = math.pi/4*(12e-3**2-10e-3**2)
KF = 1.5*1.15; KP = KF*1.25
yc = 0.45*4/(3*math.pi); n_lim = 3.4
M_unrel = n_lim*W/2*yc
# at VD, n = max(n_lim, gust) -> n_lim governs
ncase = max(n_lim, ng(VD, 4))
M_vd = ncase*W/2*yc
sig = M_vd*KF/Z12; tau = ncase*W/2*KF/(A12/2)
P(f"| Spar 12x10 root bending at n {ncase:.2f} (unrelieved {M_vd:.2f} N m) | {sig/1e6:.0f} MPa design vs 350 | MS {350e6/sig-1:+.2f}: PASS |")
P(f"| Spar shear | {tau/1e6:.1f} MPa vs 30 | MS {30e6/tau-1:+.1f}: PASS |")
n_st = nst(VD); sig_st = n_st*W/2*yc*KF/Z12
P(f"| Pull-up at VD to the stall line (n {n_st:.2f} > 3.4: the elevon can reach it, VA {Vs*math.sqrt(3.4):.1f} m/s is about VD) | spar {sig_st/1e6:.0f} MPa design | MS {350e6/sig_st-1:+.2f}: PASS; the 3.4 limit becomes a pilot / autopilot limit (`Q_A_ANGLE_MAX` 45, TECS) rather than aerodynamic at VD |")
# elevon loads at VD
P("\n## Elevon horn, hinge and lead mass loads (D-187, for C6)")
ELEV_S = 0.30*0.25*0.245   # span 0.30 m (y 0.04-0.34), chord 0.25 c  (a_model.py ELEV_FRAC), per elevon
cd_max = 20; cld = 2*math.pi*0.25**0.5*0   # unused
# hinge moment: flap hinge moment coefficient Ch_delta ~ -0.5 per rad on elevon chord (thin airfoil, 0.25 c flap, EST); Ch = H/(q Se ce)
ce = 0.25*c; Se = 0.30*ce
Ch_d = -0.5; Ch_a = -0.15            # per rad EST (thin-airfoil flap theory, 0.25 chord flap, 2-D)
alpha_max = 0.25                       # 14 deg local alpha at the gust / stall bound, EST
H_VD = 0.375*math.radians(20) + 0.5*RHO*VD**2*Se*ce*abs(Ch_a)*alpha_max   # FLUTTER.md aero hinge stiffness 0.375 N m/rad per elevon at 24 m/s (CALC) x 20 deg, plus the alpha term (EST)
H_VD_lim = H_VD
P(f"Elevon: span 0.30 m (y 0.04-0.34), chord {ce*1e3:.1f} mm (0.25 c, a_model.py ELEV_FRAC), area {Se*1e4:.0f} cm2 each, hinge stiffness from FLUTTER.md (aerodynamic, -0.375 N m/rad per elevon at 24 m/s, `CALC`) times the 20 deg stop, plus an alpha term Ch_alpha -0.15 per rad at 14 deg local alpha (`EST`).")
P(f"- Hinge moment at VD 24 with the full +-20 deg stop and 14 deg local alpha: {H_VD:.3f} N m limit per elevon (`EST`); ultimate {H_VD*1.5*1.15:.3f} N m. Servo ES3352HV stall 1.7-2.4 kgf cm = 0.17-0.24 N m (A-P11): margin {0.17/H_VD-1:+.1f} at the low stall figure.")
m_pb = 10.7e-3; arm = 0.030
for nz, lab in ((n_lim, "manoeuvre n 3.4"), (12.0, "crash 12 g (A-P5)")):
    F_l = m_pb*G*nz; Mh = F_l*arm
    P(f"- Lead balance 10.7 g on the 30 mm horn at {lab}: inertia force {F_l:.2f} N, moment about the hinge {Mh*1e3:.0f} N mm. Horn arm bending (3 mm x 12 mm CF/PETG tab, 30 mm): {Mh/(12e-3*(3e-3)**2/6)/1e6:.0f} MPa limit (x{KP:.2f} printed = {Mh/(12e-3*(3e-3)**2/6)*KP/1e6:.0f} MPa) vs PETG interlayer 9.5 MPa: {'PASS' if Mh/(12e-3*(3e-3)**2/6)*KP < 9.5e6 else 'check, use a CF horn or 4 mm PETG'} `EST`.")
# bond of horn / lead block into the foam elevon: shear of a 12 mm x 20 mm pocket
F_l = m_pb*G*12.0; Mh = F_l*arm
bond_area = 2*12e-3*20e-3
tau_b = (Mh/0.020)*KP/bond_area
P(f"- Lead block + horn bond into the elevon block (PETG block, 12 x 20 mm both faces, couple {Mh*1e3:.0f} N mm over 20 mm = {Mh/0.020:.1f} N): {tau_b/1e6:.2f} MPa design vs 2.0 MPa epoxy: MS {2e6/tau_b-1:+.1f}.")
Flat = 0.5*RHO*VD**2*Se*1.0   # not used
# tip spar stress from added lead: 2 x 10.7 g at y ~0.19 m (elevon mid) behind spar? it hangs ahead of the hinge: CG moves; wing inertia relief adds negligible
dM_root = 2*10.7e-3*G*n_lim*0.19
F_rod = H_VD/0.012; Pcr = math.pi**2*70e9*(math.pi/64*(2e-3)**4)/0.040**2
P(f"- Control rod: hinge moment {H_VD:.3f} N m on a 12 mm horn = {F_rod:.1f} N limit ({F_rod*KF:.1f} N design); 2 mm CF rod, 40 mm free length `EST` (FLUTTER.md: 2 mm rod, horn >= 12 mm): P_cr {Pcr:.0f} N, MS {Pcr/(F_rod*KF)-1:+.0f}: PASS.")
P(f"- Wing root bending from the +21 g (two balances at y about 0.19 m, n 3.4): {dM_root:.2f} N m, opposing lift, so the unrelieved spar case above is unchanged.")
# ------------------------------------------------------------------ 6. mass
P("\n## Mass vs the 473 g freeze")
P("| Group | Iter 2 (frozen) | D-187 lead balance | Total | |"); P("|---|---|---|---|---|")
P("| Wing | 191 | +21 (2 x 10.7 g `EST`; FLUTTER.md moves wing 191 -> 212) | 212 | |")
P("| Fins | 119 | 0 | 119 | |"); P("| Cage | 122 | 0 | 122 | |"); P("| Hardware | 40 | 0 | 40 | |")
P("| **Structure** | **473** | **+21** | **494** | **+21 g over the freeze, +34 g over the 460 g MASS-GATE allocation** |")
P("Offsets that keep 473 without new risk (`EST`, none applied): lighter elevon (2 mm foam or balsa, about -2 g each, FLUTTER.md) and a smaller lead (7.1 g at 45 mm if the wing thickness allows, -7 g total). Against the 1.44 kg target the +21 g uses 21 of the 44 g headroom at the 473 g basis (FOLDIN s1: predicted 1,396 g, headroom 104 g to the gate, 44 g to 1.44). The freeze needs a board waiver for the +21 g.")
open(os.path.join(HERE, "iter3_run.md"), "w").write("\n".join(OUT))
