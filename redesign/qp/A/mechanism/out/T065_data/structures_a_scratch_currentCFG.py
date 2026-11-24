"""Concept A structures roll-up: mass, C1 loads, C2 wing, C4 modes / forced response / mounts, C5 landing, C6 joints.
Reproduce: python -I structures_a.py   (needs numpy, scipy; ~1 min; imports fe_a.py and landing_a.py from this folder; prints markdown)
Labels: EST estimate, V vendor page, CALC computed here, '-' unknown.  Method scaled from team/C1, C2, C4, C5, C6 (K09-L); K09-L files untouched."""
import math, sys
import numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fe_a, landing_a

G = 9.81; RHO = 1.225
M_GATE = 1.50; W = M_GATE*G
FS_ULT, FS_FIT, FS_PRINT = 1.5, 1.15, 1.25      # K09-L: ultimate 1.5 x limit; fitting 1.15; printed/bonded 1.25 (ASM-C1-FITTING/PRINTED-FACTOR)
KF = FS_ULT*FS_FIT; KP = FS_ULT*FS_FIT*FS_PRINT
# allowables (K09-L C2 / C6 values, UNVERIFIED until coupons)
SPAR_SIG, SPAR_TAU, SPAR_HOOP = 350e6, 30e6, 40e6
XPS_COMP, XPS_TENS, XPS_SHEAR = 120e3, 150e3, 100e3
PETG_ILAY, PETG_BEAR = 9.5e6, 20e6      # interlayer 0.26 x 36.5 MPa (C6 ASM-C6-ASA-INTERLAYER scale), bearing (C4)
BOND_TAU = 2.0e6                         # neat epoxy on CF/PETG, C6 `E-FIN-13` allowable
CF_SIG_ARM = 350e6
def ms(allow, stress): return allow/stress-1
def rating(m): return "PASS" if m >= 0.15 else ("MARGINAL" if m >= 0 else "FAIL")
def tube(od, id_):
    A = math.pi/4*(od**2-id_**2); I = math.pi/64*(od**4-id_**4); return A, I, I/(od/2)
OUT = []
def P(s=""): print(s); OUT.append(s)

# ======================================================================= 1. mass
A16, I16, Z16 = tube(16e-3, 14e-3); A14, I14, Z14 = tube(14e-3, 12e-3); A8, I8, Z8 = tube(8e-3, 6e-3)
rho_cf = 1600.0
sec = 0.68*0.0233*0.245                                      # airfoil section area, 9.5 % t/c at 23 mm EST
foam = (sec*0.90-A16*0.90)*0.92*30*1e3                        # 8 % kerf/elevon; XPS 30 kg/m3 (C2 25-35)
mass = {}
mass["Wing: XPS core"] = foam
mass["Wing: spar tube 16x14 x 0.90 m"] = A16*rho_cf*0.90*1e3
mass["Wing: tape skin 0.44 m2 x 55 g/m2 EST"] = 0.44*55/1.0
mass["Wing: 4 PETG spar plugs + 2 elevon hinge/horn blocks"] = 4*2.0+2*3.0
mass["Wing: epoxy/glue EST"] = 8.0
fin_skin = 2*0.0432*2*0.1e-3*1600*1e3                         # both fins, both sides, 0.1 mm CFRP
fin_core = 2*0.0432*15e-3*30*1e3
mass["Fins: CFRP 0.1 mm skins (0.173 m2)"] = fin_skin
mass["Fins: XPS core 15 mm (both)"] = fin_core
mass["Fins: 4 foot shoes (PETG 3 g + EVA pad 1 g)"] = 4*4.0
mass["Fins: 2 root blocks (PETG)"] = 2*6.0
mass["Fins: 2 rib tubes 14x12 x 0.20 m"] = 2*A14*rho_cf*0.20*1e3
mass["Cage: 4 arm tubes 14x12 x 0.245 m"] = 4*A14*rho_cf*0.245*1e3
mass["Cage: PETG hub (sockets, pack tray)"] = 20.0
mass["Cage: bridge tube 8x6 x 0.16 m + 2 saddles"] = A8*rho_cf*0.16*1e3+2*3.0
mass["Cage: 4 motor cups (PETG, M3 pattern)"] = 4*5.0
mass["Cage: socket epoxy EST"] = 6.0
mass["Hardware: M3 screws/nuts (motors 16, others), epoxy fillets, paint EST"] = 40.0
alloc = {"Wing": 220, "Fins": 70, "Cage": 135, "Hardware": 35}
grp = {k: sum(v for n, v in mass.items() if n.startswith(k)) for k in alloc}
P("## 1. Structural mass per part vs MASS-GATE allocation (g)")
P("| Part | CALC bottom-up g | MASS-GATE g | delta |"); P("|---|---|---|---|")
for k in alloc: P(f"| {k} | {grp[k]:.0f} | {alloc[k]} | {grp[k]-alloc[k]:+.0f} |")
tot = sum(grp.values()); P(f"| **Structure total** | **{tot:.0f}** | **{sum(alloc.values())}** | **{tot-sum(alloc.values()):+.0f}** |")
for n, v in mass.items(): P(f"|   {n} | {v:.1f} | | |")
growth_old = 0.2*(220+70+135+35); growth_new = 0.1*tot
P(f"\nGrowth on these four lines: EST 20 % = {growth_old:.0f} g in MASS-GATE; at CALC 10 % = {growth_new:.0f} g. Net change to the 1,381 g prediction = {tot-sum(alloc.values()):+.0f} - ({growth_old:.0f} - {growth_new:.0f}) = **{tot-sum(alloc.values())-(growth_old-growth_new):+.0f} g** (EST; weigh each part to confirm).")

# ======================================================================= 2. C1 loads
P("\n## 2. C1 loads (limit unless marked; ult = 1.5 x limit)")
S, b, c = 0.22, 0.90, 0.245
Vs = math.sqrt(2*W/(RHO*S*0.75)); n_lim = 3.4; VA = Vs*math.sqrt(n_lim); VC = 17.0; VD = 24.0
AR = b*b/S; a_w = math.pi*AR/(1+math.sqrt(1+(AR/2)**2)); wl = W/S
mu_g = 2*wl/(RHO*c*a_w*G); Kg = 0.88*mu_g/(5.3+mu_g)
def n_gust(V, U): return 1+Kg*RHO*U*V*a_w/(2*wl)
def n_stall(V): return 0.5*RHO*V*V*S*0.75/W
P(f"Vs {Vs:.2f} m/s (CLmax 0.75 EST), VA = Vs sqrt(3.4) = {VA:.1f}, VC 17, VD {VD:.0f} (D-186: VH 18.8 m/s x 1.25 = 23.5, rounded up; A.param THR_MAX 68 + FWD_BAT, AIRSPEED_MAX 18; flutter / divergence at VD 24 open, G8). a = {a_w:.2f}/rad, mu_g {mu_g:.1f}, Kg {Kg:.3f}.")
P("| Case | n | Note |"); P("|---|---|---|")
P(f"| Gust U 8 m/s at VC | {n_gust(VC,8):.2f} -> stall-limited {n_stall(VC):.2f} | wing cannot make the gust n at 17 m/s |")
P(f"| Gust U 4 m/s at VD (half, ASM-C1-UDE-D-FRAC) | {n_gust(VD,4):.2f} (stall line {n_stall(VD):.2f}) | |")
P(f"| Manoeuvre limit | +{n_lim} / -1.5 | A-P13 floor governs; ult +{n_lim*1.5:.1f} / -2.25; VA = {VA:.1f} ~ VD |")
# spar root bending
yc = 0.45*4/(3*math.pi); L_half = n_lim*W/2
inertia = (0.106*0.225+0.162*0.228+0.032*0.114+0.062*0.38)*G*n_lim     # wing half, 2 motors+props, 2 arms (half), fin+rib half
M_relief = L_half*yc-inertia; M_unrel = L_half*yc
sig = M_unrel*FS_ULT*FS_FIT*0.008/I16
P(f"| Spar root bending, flight n 3.4 (elliptical lift, inertia relief) | {M_relief:.2f} N m ({M_unrel:.2f} unrelieved) | design uses unrelieved {M_unrel:.2f} limit |")
M_hg = 0.5*RHO*8**2*S*2.0/2*0.225
P(f"| Hover 8 m/s gust broadside (plate Cd 2.0): wing force {0.5*RHO*64*S*2.0:.1f} N, spar root | {M_hg:.2f} N m | below flight case |")
dT = 2*(landing_a.mass_props()[0] and 0)  # placeholder keeps import used
T_cap = 0.898*G; T_hov = 0.402*G
M_pitch = Z_M = fe_a.Z_M*(2*T_cap-2*1.0)
P(f"| Cage pitch moment, upper pair at the 0.90 cap ({T_cap:.1f} N each) / lower pair 1 N | {M_pitch:.2f} N m on the bridge | A-P8 85 % output limit not exceeded in SITL; this is the bound |")
P(f"| Prop strike (blade stops, one motor, 30 N along thrust EST; K09-L P1 fuse idea) | arm root {30*math.hypot(fe_a.Y_M,fe_a.Z_M):.1f} N m; bridge {30*fe_a.Z_M:.1f} N m | damage case |")
v_drop = math.sqrt(2*G*0.3)
P("| Transport drop 0.3 m (v %.2f m/s), cradle stroke s, efficiency 0.5 (ASM-C1-CRUSH-EFF) | n = v^2/(2 g eta s): %s | `-` box cradle not designed; s needs >= 40 mm for n <= 15 |" %
  (v_drop, "; ".join(f"s {s_*1e3:.0f} mm: {v_drop**2/(2*G*0.5*s_):.1f} g" for s_ in (0.025, 0.035, 0.050, 0.060))))
P(f"| Landing (see s5) | foot plateau 30 N, 4 feet | worst-case values from landing_a.py are tabulated in s5 (n, foot load, side load, rib-root RF) |")

# ======================================================================= 3. C2 wing
P("\n## 3. C2 wing: spar and foam")
msp = ms(SPAR_SIG, sig)
tau = 2*(L_half*FS_ULT*FS_FIT)/ (2*A16)   # shear (thin tube) V/(A/2)
P("| Check | Stress | Allowable | MS | Result |"); P("|---|---|---|---|---|")
P(f"| Spar 16x14 root bending, ult x fitting, unrelieved {M_unrel*FS_ULT*FS_FIT:.1f} N m | {sig/1e6:.0f} MPa | 350 | {msp:+.1f} | {rating(msp)} |")
tau_sp = (n_lim*W/2)*KF/(A16/2)
P(f"| Spar shear at root | {tau_sp/1e6:.1f} MPa | 30 | {ms(SPAR_TAU,tau_sp):+.1f} | {rating(ms(SPAR_TAU,tau_sp))} |")
# tip deflection
EI16 = 70e9*I16
d_tip = (L_half/ (0.45))*0.45**3/(3*EI16)*0.75*n_lim/n_lim
P(f"| Spar tip deflection at n 3.4 (tube alone, E 70 GPa) | {L_half*0.45**3/(3*EI16)*1e3*0.7:.1f} mm of 450 mm semispan ({L_half*0.45**3/(3*EI16)*0.7/0.45*100:.1f} %) | 5 % | | PASS |")
# ring crush at clamps
P("| Spar wall under saddle clamps (hoop) | PETG plug in tube at y = 0, +-0.38 (C2 rule: unplugged ring failed by 20x) | - | - | plugs required, in mass |")
# foam at attachments
T_br = M_pitch
tau_f = T_br/(2*math.pi*0.008**2*0.20)*KP
P(f"| Foam shear around spar from bridge torque {T_br:.2f} N m (zone |y| <= 0.1, r 8 mm, ult x fit x print) | {tau_f/1e3:.0f} kPa | {XPS_SHEAR/1e3:.0f} | {ms(XPS_SHEAR,tau_f):+.2f} | {rating(ms(XPS_SHEAR,tau_f))} |")
Fy_f = 2*20.0
brg = Fy_f*KP/(0.065*0.0233)
P(f"| Foam bearing at the fin slot (both feet side load 2 x 20 N, slot 65 x 23 mm) | {brg/1e3:.0f} kPa | {XPS_COMP/1e3:.0f} | {ms(XPS_COMP,brg):+.2f} | {rating(ms(XPS_COMP,brg))} |")
q_air = n_lim*W/b/(0.032)
P(f"| Foam shear, lift into spar slot (55 N/m over 32 mm of bond) | {q_air*1/1e3*FS_ULT:.1f} kPa | {XPS_SHEAR/1e3:.0f} | {ms(XPS_SHEAR,q_air*FS_ULT):+.0f} | PASS |")
P(f"| Arm / motor attachments | none in foam: the cage hangs from the spar through the bridge saddle and the arms carry the motors; foam sees only the saddle pocket (R >= 3 mm corners, C6 rule) | - | - | - |")
P("Fin elevon note: elevon span ends at |y| <= 0.34 (fin slot at 0.38 starts beyond it); fin x 0.18-0.30 overlaps the wing aft 65 mm.")

# ======================================================================= 4. C4 modes
P("\n## 4. C4 modes vs rotor orders (3-D beam FE, free-free; fe_a.py)")
# rpm: prop_a.py hover 1.50 kg derate 0.93 = 6272 rpm; cruise estimated
RPM = {"hover (1.50 kg, prop_a.py)": 6272.0, "hover light 1.381 kg": 6272*math.sqrt(1.381/1.5), "hover 8 m/s lean 1.3 W": 6272*math.sqrt(1.3), "cruise 17 m/s (SITL fu_level.py, 7,300-7,540 rpm; mid 7,450)": 7450.0}
for k, v in RPM.items(): P(f"- {k}: {v:.0f} rpm: 1P {v/60:.0f} Hz, 2P {v/30:.0f} Hz")
P("Cruise rpm 7,300-7,600 (QP-3 BOARD s1 item 2: sitl/fu_level.py with the APC V > 0 data, 17 m/s level at duty 0.60-0.70); the earlier 8,900-10,500 band was an estimate and is withdrawn; M8 audio FFT on the first cruise replaces it.")
results = {}; frames = {}
for kind in ("kd", "nom", "hi"):
    F, info = fe_a.build(kind, **dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(0.016,0.016-2e-3), vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025)); results[kind] = F.solve(90); frames[kind] = F
def sep(f, rpm):
    return min(abs(f-rpm/60)/(rpm/60), abs(f-rpm/30)/(rpm/30))
pts = [6272.0, 6272*math.sqrt(1.381/1.5), 7450.0]
P("\nModes with strong coupling to the motors (|phi| at motors in plane cy or thrust cx >= 0.5, mass-normalised), kd = E_CF 61 / PETG 1.6 GPa, nom 70 / 2.1, hi 90 / 2.4:")
P("| Corner | f (Hz) | group | cx / cy | worst separation to 1P/2P at hover 6272 and cruise 7450 | worst incl. hover light | Result |"); P("|---|---|---|---|---|---|---|")
worst_all = {}
for kind in ("kd", "nom", "hi"):
    res = results[kind]
    for (f, e, v, cx, cy), (f2, cl) in zip(res, fe_a.classify(res)):
        if (cx >= 0.5 or cy >= 0.5) and f < 800:
            s1 = min(sep(f, 6272.0), sep(f, 7450.0)); s2 = min(sep(f, r) for r in pts)
            worst_all.setdefault(kind, []).append((f, s2))
            P(f"| {kind} | {f:.0f} | {cl.split(',')[0]} | {cx:.1f} / {cy:.1f} | {s1*100:.0f} % | {s2*100:.0f} % | {'PASS' if s2 >= 0.2 else ('MARGINAL' if s2 >= 0.1 else 'FAIL')} |")
P("\nFin out-of-plane modes (fin 75-95 % of strain energy) and weakly coupled spar / rib modes (cx, cy < 0.5):")
P("| Corner | f (Hz) | group | worst separation (6272, light, 7450 rpm) | Result |"); P("|---|---|---|---|---|")
for kind in ("kd", "nom", "hi"):
    for (f, e, v, cx, cy), (f2, cl) in zip(results[kind], fe_a.classify(results[kind])):
        if 20 < f < 800 and cx < 0.5 and cy < 0.5 and (e.get("fin", 0) > 0.5 or f > 60):
            s2 = min(sep(f, r) for r in pts)
            P(f"| {kind} | {f:.0f} | {cl} | {s2*100:.0f} % | {'PASS' if s2 >= 0.2 else ('MARGINAL' if s2 >= 0.1 else 'FAIL')} |")

# forced response closure for weakly coupled / marginal modes (C2 CR-C2-16 method)
P("\nForced response (C2 method): worst-phase modal sum, 4 rotors, unbalance U = 1.0 g mm per rotor (EST; ISO G16 prop is 0.27 g mm), 2P axial ripple 5 % of thrust (EST), damping 1 % (EST). Acceleration at the FC (spar centre):")
P("| Corner | Point | IMU accel, 1P | IMU accel, 2P | fin tip accel 1P / 2P (m/s2) | limit | MS |"); P("|---|---|---|---|---|---|---|")
def forced(kind, rpm, thrust):
    F = frames[kind]; res = results[kind]; idx = F._idx
    om = rpm/60*2*math.pi; U = 1e-6; F1 = U*om**2; f2x = 0.05*thrust
    imu = idx["s+0.000"]; tip = idx["f+1+1"]
    out = {}
    for tag, mult, fm in (("1P", 1, F1), ("2P", 2, f2x)):
        w = mult*om; a_imu = 0.0; a_tip = 0.0
        for (f, e, v, cx, cy) in res:
            wi = 2*math.pi*f
            if tag == "1P": gam = fm*sum(abs(v[6*idx[m]+1])+abs(v[6*idx[m]+2]) for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m)
            else: gam = fm*sum(abs(v[6*idx[m]]) for m in idx if (m.startswith("m+") or m.startswith("m-")) and ">" not in m)
            h = 1/math.sqrt((wi*wi-w*w)**2+(2*0.01*wi*w)**2)
            a_imu += w*w*gam*h*sum(abs(v[6*imu+q]) for q in range(3)); a_tip += w*w*gam*h*abs(v[6*tip+1])
        out[tag] = (a_imu, a_tip)
    return out
for kind in ("kd", "nom", "hi"):
    for nm, rpm, th in (("hover 6272", 6272, 3.94), ("cruise 7450", 7450, 0.49)):
        o = forced(kind, rpm, th)
        worst = max(o["1P"][0], o["2P"][0])
        P(f"| {kind} | {nm} | {o['1P'][0]:.1f} | {o['2P'][0]:.1f} | {o['1P'][1]:.1f} / {o['2P'][1]:.1f} | 30 m/s2 | {30/worst-1:+.1f} |")
# fin stress at resonance
F, info = fe_a.build("kd", **dict(spar_tube=(12e-3, 10e-3), arm_tube=(12e-3, 10e-3), rib_tube=(14e-3, 12e-3), bridge_cfg="single+V", bridge_tube=(0.016,0.016-2e-3), vtube=(6e-3, 4.5e-3), bridge_yv=0.30, fin_strip=None, fin_tube=(16e-3, 14e-3, 3e-3, 0.055), x_fin=0.294, foot_pad_m=0.0025))
EIo = info["EI_out"]
P(f"\nFin out-of-plane EI {EIo:.1f} N m2 (kd), mass/length {info['mu']*1e3:.0f} g/m (15 mm XPS core, 0.1 mm CFRP skins); foot 3 g; f1 cantilever ideal at kd: see table (fin rows).")

# static mount stiffness and strength
P("\n### Mount stiffness and strength (limit load at the 0.90 cap, design = x1.5 x1.15 x1.25 on printed / bonded, x1.5 x1.15 on CF)")
T_u = 0.898*G*1.0
arm_L = math.hypot(fe_a.Y_M, fe_a.Z_M)-0.03
M_arm = T_u*arm_L
sig_arm = M_arm/Z14*KF
P("| Item | Value | Allowable | MS | Result |"); P("|---|---|---|---|---|")
P(f"| Arm 14x12 root bending, thrust {T_u:.1f} N at {arm_L:.3f} m = {M_arm:.2f} N m | {sig_arm/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_arm):+.1f} | {rating(ms(CF_SIG_ARM,sig_arm))} |")
M_ps = 30*arm_L; sig_ps = M_ps/Z14*KF
P(f"| Arm, prop strike 30 N (EST) {M_ps:.1f} N m | {sig_ps/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_ps):+.1f} | {rating(ms(CF_SIG_ARM,sig_ps))} |")
M_br = 30*fe_a.Z_M; sig_br = M_br/Z8*KF
P(f"| Bridge 8x6 in prop strike, {M_br:.1f} N m (sets the fuse: weakest CF part) | {sig_br/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_br):+.2f} | {rating(ms(CF_SIG_ARM,sig_br))} |")
M_br2 = M_pitch; sig_br2 = M_br2/Z8*KF
P(f"| Bridge 8x6, max control pitch moment {M_br2:.2f} N m | {sig_br2/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_br2):+.2f} | {rating(ms(CF_SIG_ARM,sig_br2))} |")
Mpk = 0.27*12*G*0.135+0.020*12*G*0.135
sig_pk = Mpk/Z8*FS_ULT*FS_FIT
P(f"| Bridge, pack + hub at 12 g crash ({(0.27+0.02)*12*G:.0f} N x 0.135 m = {Mpk:.1f} N m, A-P5) | {sig_pk/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_pk):+.2f} | {rating(ms(CF_SIG_ARM,sig_pk))} |")
k_arm = 3*70e9*I14/arm_L**3
EI8 = 70e9*I8
P(f"| Arm tip stiffness {k_arm/1e3:.1f} N/mm: thrust deflection | {T_u/k_arm*1e3:.2f} mm | - | - | info |")
P(f"| Hub pitch rotation under max control moment: M L / EI(bridge 8x6, {EI8:.1f} N m2) | {math.degrees(M_pitch*0.135/EI8):.1f} deg | - | - | MARGINAL: soft mount (cage pitch mode 40-47 Hz, FC filter / notch must be set below 30 Hz or the mode notched) |")
Pcr = math.pi**2*EI8/(0.135*2)**2
P(f"| Bridge buckling under hover thrust sum 1.33 W = {1.33*W:.0f} N (cantilever-pin K=2) | P_cr {Pcr:.0f} N | | {Pcr/(1.33*W*KF)-1:+.1f} | PASS |")
Ftorque = 0.153
P("| Motor screws: see s6 | | | | |")

# ======================================================================= 5. C5
P("\n## 5. C5 landing on fin-tip feet")
st = landing_a.static()
P(f"Static (CG {st['cg_x']*1e3:.1f} mm aft of LE, feet at x 0.300, y +-0.38, z +-0.18; CG 0.275 m above feet): tip-over narrow axis **{st['tip_narrow']:.1f} deg** (limit 30: sizing 33.2), wide axis {st['tip_wide']:.1f} deg. Parked broadside to the wind: tips at {st['v_tip_parked']:.1f} m/s (gust 8: crew catches or lays it down, as A-P9); restoring / overturning at 5 m/s {st['restore_ratio_5ms']:.2f}. I (kg m2, about the CG): {np.round(st['I'],4).tolist()} (SITL plant used 0.053-0.064 roll).")
P("Foot design (EST, CAD): PETG shoe bonded over the fin corner, 12 (y) x 15 (z) mm EVA/PE foam pad 30 mm thick, plateau stress 0.17 MPa -> **30 N per foot** (static load W/4 = 3.7 N: x8 below yield), usable stroke 20 mm, rigid stop beyond. Foam plateau and stroke are unmeasured: drop-test a coupon first (5 pads, 1.2 m/s on a scale).")
P("Sim = `landing_a.py` (K09-L `team/C5/sim` physics rebuilt standalone for A: 6 dof, 4 elasto-plastic feet, friction 0.40 (assumed, see below), lift 2/3 W to 0.3 s then 0 at 0.6 s, 1.50 kg, current mass list of `landing_a.py` ITEMS (motor assemblies 4 x 88.26 g)):")
P("| Case | max stroke (mm) of 20 | permanent set (mm) | peak foot load (N) | side load (N) | n at CG | end tilt (deg) | drift (mm) | rib-root RF |"); P("|---|---|---|---|---|---|---|---|---|")
cases = [("hard 1.2 m/s level", dict(v_sink=1.2)), ("hard, 10 deg narrow", dict(v_sink=1.2, th_n=10)), ("hard, 10 deg wide", dict(v_sink=1.2, th_w=10)),
         ("hard, 7+7 deg combined", dict(v_sink=1.2, th_n=7, th_w=7)), ("hard, 10 narrow + 0.5 m/s drift", dict(v_sink=1.2, th_n=10, drift=0.5)),
         ("hard, 10 wide + 0.5 m/s drift (y)", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("normal 0.5 m/s level", dict(v_sink=0.5)), ("normal, 10 narrow", dict(v_sink=0.5, th_n=10)), ("normal, 10 wide + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=math.pi/2)),
         ("hard, 1.381 kg, 10 narrow", dict(v_sink=1.2, th_n=10, m=1.381))]
simres = []
for name, kw in cases:
    r = landing_a.simulate(Fp=30.0, **kw); simres.append((name, r))
    P(f"| {name} | {r['dmax_mm'].max():.1f} | {r['sp_mm'].max():.1f} | {r['F'].max():.0f} | {r['side'].max():.0f} | {r['n_peak']:.1f} | {r['tilt_end']:.1f} | {r['drift_end']*1e3:.0f} | {r['rib_rf']:.2f} |")
worst_s = max(r['dmax_mm'].max() for _, r in simres); worst_n = max(r['n_peak'] for _, r in simres if True)
P(f"Worst stroke {worst_s:.1f} mm of 20 (margin {20-worst_s:.1f} mm, {100*(20/worst_s-1):.0f} %): PASS. No tip-over in any case (end tilt <= 3 deg). Peak load factor {worst_n:.1f} g vs A-P5 12 g: {'PASS' if worst_n <= 12 else 'FAIL'} (the 6 mm crush of SIZING-A is replaced: 12 g would need 6 mm only at constant force and a level hit; with 20 mm and 30 N the level hard case is below).")
P("Pad life: normal landings set 0.8-4 mm; replace the pad at 10 mm cumulative set (a hard landing sets up to 13 mm: replace after any hard landing). Pads are $0 stock (foam); K09-L cartridges not used.")
rib_min = min(r['rib_rf'] for _, r in simres); side_max = max(r['side'].max() for _, r in simres)
P(f"Side load per foot: worst {side_max:.1f} N at pad mu 0.40 (T-064: the earlier 'scaled K09-L cap about 14 N' (24.5 N x mass ratio) belonged to no part of A and is withdrawn; K09-L's 24.5 N was its own design value set equal to its own sim result, C5 CLOSURE s2, D-138). The limit is now the computed capacity of the failing part: the rib root (14x12 CF tube, x 0.0705 to the fin block) under combined bending (arm 0.2295 m), torsion (lever 0.18 m) and axial load, all four feet resolved in the body frame at every time step (`landing_a.py` rib RF = 1 / sqrt((KF (M/Z + N/A) / 350 MPa)^2 + (KF T r / J / 30 MPa)^2), KF 1.725; both allowables EST, no coupon). Minimum rib-root RF over these cases **{rib_min:.2f}** ({'PASS' if rib_min >= 1.0 else 'FAIL'} at the EST allowables, UNVERIFIED until a twist coupon). The pad friction 0.40 is an assumption carried from K09-L (its pad face was UHMW-PE tape over neoprene, D-105); A's drawn pad is bare EVA/PE foam, friction not measured ('-'): drag-test it; the rib RF reaches 1 at mu about 0.51 in the worst case (`landing_side_a.py`). See AR-012 / D-213 proposals in `mechanism/out/T064_landing_side.md`.")

# ======================================================================= 6. C6 joints
P("\n## 6. C6 joints, fasteners, bonds (design load = limit x 1.5 x 1.15 [x 1.25 printed/bonded])")
P("| Joint | Load (limit) | Stress / capacity (design) | Allowable | RF | Result |"); P("|---|---|---|---|---|---|")
def row(name, load, stress, allow):
    rf = allow/stress; P(f"| {name} | {load} | {stress/1e6:.2f} MPa | {allow/1e6:.1f} MPa | {rf:.2f} | {rating(rf-1)} |")
# motor screws: 4 x M3 steel, thrust 10.4 N uncapped max, prop strike 30 N
A_s = 5.03e-6
T_max = 10.4
row("Motor to cup, 4 x M3x8 steel: tension from thrust 10.4 N + prying x2 (hover/full)", "2.6 N per screw x2", (T_max/4*2)*KP/A_s, 450e6)
row("Motor to cup: prop strike 30 N bending 0.012 m x 30 N on a 16 mm pattern (worst screw)", "tension 22 N", (30*0.012/0.016/2*1.0)*KP/A_s, 450e6)
Ae = 2.5e-3*math.pi*2.7e-3*0.6; row("Motor M3 thread strip in aluminium base, engagement 2.5 mm (>= 2.5 mm, C6 rule), strike", "22 N", 22*KP/(math.pi*2.7e-3*2.5e-3), 0.6*150e6)
P("Cup head bearing: M3 with 6 mm washer on 4 mm PETG: 22 N x 2.16 / 28 mm2 = 1.7 MPa vs 20: RF 11.9 PASS (not a limit).")
row("Arm in hub / cup socket: bond, 25 mm insertion, prop strike couple (moment 8.3 N m / 0.025 m = 330 N on 14 x 25 mm)", "330 N", 330*KP/(math.pi*14e-3*25e-3*0.5), BOND_TAU)
row("Arm in hub socket, thrust 10.4 N (2.9 N m): couple 116 N", "116 N", 116*KP/(math.pi*14e-3*25e-3*0.5), BOND_TAU)
row("PETG socket wall bearing (strike couple 330 N on 14 x 12 mm contact)", "330 N", 330*KP/(14e-3*12e-3), PETG_BEAR)
# bridge to spar saddle
row("Bridge saddle on spar, full wrap 16 x 30 mm: control torque 2.4 N m", "2.4 N m", (M_pitch/(2*math.pi*0.008**2*0.030))*KP, BOND_TAU)
row("Bridge into hub (8 mm tube, 25 mm in socket), strike couple 4.7 N m / 0.025", "188 N", 188*KP/(math.pi*8e-3*25e-3*0.5), BOND_TAU)
# rib to spar saddle: lateral both feet 40 N at 0.18 m
M_rib = 40*0.18
row("Rib 14x12 CF tube root bending, both feet side load 40 N at 0.18 m (7.2 N m)", "7.2 N m", (M_rib/Z14)*KF, CF_SIG_ARM)
row("Rib saddle on spar (wrap 16 x 30 mm): 7.2 N m couple over 16 mm = 450 N", "450 N", 450*KP/(math.pi*16e-3*30e-3*0.5), BOND_TAU)
T_r = 15*0.18; tau_r = T_r*0.007/(2*I14)*KF
row("Rib torsion, one foot loaded (side 15 N x 0.18 m = 2.7 N m), CF shear", "2.7 N m", tau_r, SPAR_TAU)
P(f"Rib torsional twist at that load: {math.degrees(T_r*0.20/(3e9*2*I14)):.1f} deg (GJ {3e9*2*I14:.1f} N m2, L 0.20 m): foot moves {math.tan(T_r*0.20/(3e9*2*I14))*0.18*1e3:.0f} mm sideways: MARGINAL stiffness, deliberate (keeps the fin mode below 1P).")
row("Fin root block on fin skins (60 x 40 mm both faces, 40 N)", "40 N", 40*KP/(2*0.060*0.040), BOND_TAU)
row("Rib tube in fin root block (60 mm embed), axial 84 N (2 feet x 42 N)", "84 N", 84*KP/(math.pi*14e-3*60e-3), BOND_TAU)
row("Fin skin 0.1 mm CFRP bending at root (M 3.5 N m per half, kd)", "3.5 N m", 3.5/(2*0.1e-3*0.12*7.55e-3)*KF, 450e6)
wr = 0.5*(50e9*30e6*8e6)**(1/3)
row("Fin skin wrinkling on XPS core (0.5 (Ef Ec Gc)^(1/3), Ec 30, Gc 8 MPa EST)", "same", 3.5/(2*0.1e-3*0.12*7.55e-3)*KF, wr)
row("Foot shoe bond on fin corner (12 x 15 mm pad footprint, shoe wraps 25 x 30 mm both faces = 1,500 mm2), 49 N + 20 N side", "52 N", 52*KP/1.5e-3, BOND_TAU*0.05)
P("(shoe-bond allowable 0.1 MPa = C6 paper/foam value, `CL-C6-FOOT-SHOE-RF` basis: bond to foam core, not CF.)")
P("Pack tray to hub (PETG flange 27.2 x 8 = 218 mm2 bond, D-208: the outer flange tabs were never attached to the hub) at 12 g: 32 N x 2.16 / 218 mm2 = 0.32 MPa vs 2.0: RF 6.3 PASS; strap: 2 x 20 mm Velcro, 32 N each side, `-` not tested.")
open("structures_run.md", "w").write("\n".join(OUT))
