"""Concept A structures roll-up, CURRENT geometry (T-066, 2026-11-22): mass, C1 loads, C2 wing, C4 modes / forced response / mounts, C5 landing, C6 carried rows.
Reproduce: python -I structures_a.py   (needs numpy, scipy; about 6 min, the landing sweep dominates; imports fe_a.py, landing_a.py, landing_mass_cad.py from this folder
and the CAD constants / part table from ../cad via a_model; writes structures_run.md next to this file; first run builds T066_data/cad_part_table_T066.json)
Categories (one per section): s1 geometry arithmetic (CAD declared masses); s2 and s3 hand calculation (C1 loads, C2 wing); s4 FEA-lite: 3-D Euler-Bernoulli beam frame
eigen-analysis + modal forced response (beam FE, NOT shell / solid FEA); s5 rigid-body dynamics (landing_a.simulate) + hand calculation (rib root); s6 carried-forward
rows of other records (not recomputed here).  Labels: EST estimate, V vendor page, CALC computed here, '-' unknown.
Basis: the committed CAD at commit ac983050 (D-226 saddle load path, D-227 / D-228 X2216 V3 880KV on APC 9x4.5MR, D-229 machined 6061 FIN-003 root fitting).
Method scaled from team/C1, C2, C4, C5, C6 (K09-L); K09-L files untouched."""
import math, sys, os, json, contextlib, io
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
# ---- landing_a reads these at import: predicted mass (T-083b tallied 1.873 kg), CAD part-table mass model, 25x23 rib (wing.py RIB_OD / RIB_ID) ----
M_PRED = 1.873                                  # kg, T-083b tallied predicted mass (redesign/qp/A/mechanism/out/T083b_report.md s0 row 6; basic 1.6275 kg x 1.1174 + 0.032 x 1.47 + 7.0 g undrawn shoe cups)
os.environ["LAND_MASS_KG"] = str(M_PRED); os.environ["LAND_MASS_MODEL"] = "cad"; os.environ["LAND_RIB_OD"] = "0.025"; os.environ["LAND_RIB_ID"] = "0.023"
import numpy as np
import fe_a, landing_a, landing_mass_cad as LM
sys.path.insert(0, os.path.join(QPA, "cad"))
with contextlib.redirect_stdout(io.StringIO()):
    import a_model as m                          # CAD constants and the part table (declared masses); import prints nothing of interest
    sys.path.insert(0, QPA); import prop_a as PA  # APC 9x4.5MR static rows + X2216 V3 880KV motor model (T-083), prints nothing at import
assert abs(m.RIB_OD - 0.025) < 1e-9 and abs(m.RIB_ID - 0.023) < 1e-9
CADMASS = json.load(open(os.path.join(QPA, "sitl", "cad_mass.json")))
OUT = []
def P(s=""): print(s); OUT.append(s)

G = 9.81; RHO = 1.225
M_GATE = 1.50                                   # kg, MASS-GATE.md limit, shown for reference only (T-083b: the gate is not relaxed; the build fails it)
W = M_PRED*G
FS_ULT, FS_FIT, FS_PRINT = 1.5, 1.15, 1.25      # K09-L: ultimate 1.5 x limit; fitting 1.15; printed/bonded 1.25 (ASM-C1-FITTING/PRINTED-FACTOR)
KF = FS_ULT*FS_FIT; KP = FS_ULT*FS_FIT*FS_PRINT # 1.725, 2.156 (T-083 / T-083b KF, KP)
DAF_WING, DAF_TUBE = 2.23, 1.97                 # D-223 (CHANGE-LOG D-223; T083_report.md s5.3): wing / bridge / rib / skin 2.23, arm tubes and bond 1.97; x1.5 floor stays
def daf(d): return max(d, 1.5)
# allowables (K09-L C2 / C6 values, UNVERIFIED until coupons)
SPAR_SIG, SPAR_TAU = 350e6, 30e6
XPS_COMP, XPS_TENS, XPS_SHEAR = 103e3, 129e3, 86e3   # foam_103.md: compressive 103 (V data sheet), tension 129 / shear 86 (EST, scaled 103/120); was 120 / 150 / 100
CF_SIG_ARM = 350e6
def ms(allow, stress): return allow/stress-1
def rating(v): return "PASS" if v >= 0.15 else ("MARGINAL" if v >= 0 else "FAIL")
def rrate(rf): return "PASS" if rf >= 1.0 else "FAIL"
def tube(od, id_):
    A = math.pi/4*(od**2-id_**2); I = math.pi/64*(od**4-id_**4); return A, I, I/(od/2)

# ======================================================================= current inputs, one place, every value with its source
SP = (m.SPAR_OD, m.SPAR_ID)                      # 12 x 10: wing.py / common.py SPAR_OD, SPAR_ID (iteration 2)
ARM = (0.012, 0.010)                             # arm tubes 12x10, two continuous tubes: common.py D-202 note (TUBE_*), wing.py TUBE_RO (6 mm) / TUBE_RI; part CGE-002-A/B "Arm tube 12x10 x 0.5525 m"
BR = (m.BR_OD, m.BR_ID)                          # bridge 16x14: wing.py BR_OD / BR_ID (D-206)
STR = (m.STRUT_OD, m.STRUT_ID)                   # struts 8x6 (T-077 p7 / D-225 condition); the ledger row's 6x4.5 is stale: wing.py STRUT_OD / STRUT_ID = 0.008 / 0.006
RIB = (m.RIB_OD, m.RIB_ID)                       # rib 25x23: wing.py RIB_OD / RIB_ID (T-077 p8, D-226 s3, AM-016)
FINT = (m.FIN_OD, m.FIN_ID)                      # fin tube 16x14: common.py FIN_OD / FIN_ID
Y_M, Z_M = m.YM, m.ZM                            # motor station 0.228 / 0.156: common.py YM, ZM
X_HUB = m.HUB[0]                                 # hub x -0.078: common.py HUB = -0.069 + CAGE_DX (-0.012 + T083_DX +0.003)
X_FIN = m.XFIN_T                                 # fin tube x 0.294: common.py XFIN_T
Y_FIN = m.YFIN; H_FIN = m.FIN_H                  # 0.38, 0.18: common.py
A_S, I_S, Z_S = tube(*SP); A_A, I_A, Z_A = tube(*ARM); A_B, I_B, Z_B = tube(*BR); A_V, I_V, Z_V = tube(*STR); A_R, I_R, Z_R = tube(*RIB); A_F, I_F, Z_F = tube(*FINT)
E_CF = 70e9                                      # nominal CF tube E (fe_a.E_CF['nom'], ASM-C2 low-corner value)
def mg(*pre, ex=()):
    return sum(p["mass_g"] for pid, p in m.PARTS.items() if pid.startswith(pre) and not pid.startswith(ex))
M_BASIC = sum(p["mass_g"] for p in m.PARTS.values())
P("> **Scope (T-066, 2026-11-22): re-baselined to the CURRENT concept A geometry** (CAD at commit ac983050; supersedes the T-065 note that this file held the QP-3 iteration-1 baseline). "
  f"Tubes: spar {SP[0]*1e3:.0f}x{SP[1]*1e3:.0f}, arms {ARM[0]*1e3:.0f}x{ARM[1]*1e3:.0f} continuous (D-202), bridge {BR[0]*1e3:.0f}x{BR[1]*1e3:.0f} + two {STR[0]*1e3:.0f}x{STR[1]*1e3:.0f} struts, rib {RIB[0]*1e3:.0f}x{RIB[1]*1e3:.0f} (D-226), fin tube {FINT[0]*1e3:.0f}x{FINT[1]*1e3:.0f}; "
  f"D-226 bulkheads / centre node / 3-ply skin, D-227 / D-228 X2216 V3 880KV on APC 9x4.5MR, D-229 6061 FIN-003 fitting. Mass {M_PRED} kg predicted (T-083b), CAD basic {M_BASIC/1000:.4f} kg "
  f"(cad_mass.json {CADMASS['mass_basic_kg']}). Demand and DAF of T-083 / T-083b reused (pad 36 N / 24 mm, 21 cases (landing_path_a.cases(False); the T-083 text says 23, the function returns 21) x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30; DAF {DAF_WING} wing, {DAF_TUBE} tubes). "
  "The ledger row's geometry list (arms 12x10, rib 14x12, bridge 16x14 + struts 6x4.5) is stale: the CAD has rib 25x23 and struts 8x6.")

# ======================================================================= 1. mass
P("\n## 1. Structural mass: CAD declared masses (geometry arithmetic; `a_model.PARTS`, 131 parts)")
groups = [("Wing (WNG: core, skins, bulkheads, spar, plugs, elevons, balance, caps, dampers)", ("WNG",)), ("Fins (FIN: tube, rib, 6061 root fitting, node, fairings) + feet (GER)", ("FIN", "GER")),
          ("Cage (CGE: hub, arm tubes, cups, doublers, pins, bridge, struts, clamps, centre node, tray)", ("CGE",)), ("Propulsion (PRP: motors, props, adapters, nuts, X-mounts, ESC)", ("PRP",)),
          ("Power (PWR: pack, straps, pad)", ("PWR",)), ("Avionics (AVN, HWC-001/003)", ("AVN", "HWC-001", "HWC-003")), ("Mechanisms (MEC, HWC-002)", ("MEC", "HWC-002")),
          ("Harness (HRN)", ("HRN",)), ("Hardware lump (HRD)", ("HRD",))]
P("| Group | CAD declared g | note |"); P("|---|---|---|")
tot = 0
for name, pre in groups:
    v = mg(*pre); tot += v; P(f"| {name} | {v:.1f} | |")
P(f"| **Total basic (CAD)** | **{tot:.1f}** | cad_mass.json mass_basic_kg {CADMASS['mass_basic_kg']*1000:.1f} g: {'match' if abs(tot-CADMASS['mass_basic_kg']*1000) < 0.5 else 'MISMATCH'} |")
pred_drawn = tot/1000*1.1174+0.032*1.47
P(f"\nPredicted = basic x 1.1174 + 0.032 x 1.47 (CALC-A-MASS-PRED, T083b_report.md s4.1): drawn {pred_drawn:.4f} kg; tallied (+7.0 g undrawn shoe cups EST, T-083b) {M_PRED} kg (used for all loads below). MASS-GATE limit {M_GATE} kg: the predicted mass exceeds it by {(M_PRED-M_GATE)*1000:.0f} g (gate not relaxed; build_a reports it, T-083b s6). "
  f"The old bottom-up roll-up (iteration-1 tubes, 'MASS-GATE allocation' column) is replaced by the CAD part table above; the structure-only groups (Wing + Fins + Cage + Hardware) are {mg('WNG')+mg('FIN','GER')+mg('CGE')+mg('HRD'):.0f} g against the frozen 473 g of iter3_run.md (+ D-187 balance lead 21 g = 494 g).")

# FE masses from the CAD part table (every value = a_model.PARTS declared mass)
FEIN = dict(
    wing_g=mg("WNG")+mg("CGE-007"),                                            # whole wing group (spar tube included: fe_a subtracts it for the spar beam) + the two strut clamps
    avionics_g=mg("AVN", "HWC-001", "HWC-003", "PRP-003", "HRN-001", "HRN-002", "HRD"),   # boards, ESC, harness remainder, hardware lump at the spar centre (EST placement)
    centre_extra_g=mg("CGE-006", "MEC", "HWC-002"),                            # 6061 centre node + servos / linkage at the spar centre (servos really at |y| 0.2: EST)
    pack_g=mg("PWR")+mg("CGE-008"),                                            # pack, straps, pad, tray plate at the hub
    hub_extra_g=mg("CGE-001", "CGE-009", "CGE-010", "HRN-003", "HRN-004"),     # machined hub, doublers, pins, raceways, conduits at the hub
    motor_g=(mg("PRP-001-UR")+mg("PRP-002-UR")+mg("PRP-004-UR")+mg("PRP-005-UR")+mg("PRP-006-UR")+mg("CGE-003-UR")),   # motor + prop + adapter + nut + X-mount + cup, one station
    foot_pad_m=(mg("GER-001-UR")+mg("GER-002-UR"))/1000.0,                      # shoe + pad per foot, kg
    root_g=(mg("FIN-003-R")+mg("FIN-005-R")+mg("FIN-009-R")+mg("FIN-006-R")+mg("FIN-010-R")),   # root fitting + node bulkheads + plates + rib fairings per fin side
)
FEKW = dict(spar_tube=SP, arm_tube=ARM, rib_tube=RIB, bridge_cfg="single+V", bridge_tube=BR, vtube=STR, bridge_yv=m.STRUT_E[1], fin_strip=None,
            fin_tube=(FINT[0], FINT[1], 3e-3, 0.055), x_fin=X_FIN, x_hub=X_HUB,
            wing_g=FEIN["wing_g"], avionics_g=FEIN["avionics_g"], centre_extra_g=FEIN["centre_extra_g"], pack_g=FEIN["pack_g"], hub_extra_g=FEIN["hub_extra_g"],
            motor_g=FEIN["motor_g"], foot_pad_m=FEIN["foot_pad_m"], root_g=FEIN["root_g"])
P("\nFE model inputs (all from the CAD part table, g): " + ", ".join(f"{k} {(v*1000 if k == 'foot_pad_m' else v):.2f}" for k, v in FEIN.items()) + f"; bridge_yv {m.STRUT_E[1]} (STRUT_E y), x_hub {X_HUB*1e3:.1f} mm, x_fin {X_FIN*1e3:.0f} mm, fin tube foam 3 mm + tape 55 g/m2 carried from the iteration-3 setup (EST).")

# ======================================================================= 2. C1 loads
P("\n## 2. C1 loads (hand calculation; limit unless marked; ult = 1.5 x limit; mass " + f"{M_PRED} kg)")
S, b, c = 0.22, m.B, m.C                         # wing area 0.22 m2 (landing_a.py / prop_a.py; MISSION), span 0.90, chord 0.245 (common.py B, C)
CLMAX = 0.75                                     # EST (A-P6 stall test open, T083_report.md s2.3)
Vs = math.sqrt(2*W/(RHO*S*CLMAX)); n_lim = 3.4; VA = Vs*math.sqrt(n_lim); VC = 17.0; VD = 24.0
AR = b*b/S; a_w = math.pi*AR/(1+math.sqrt(1+(AR/2)**2)); wl = W/S
mu_g = 2*wl/(RHO*c*a_w*G); Kg = 0.88*mu_g/(5.3+mu_g)
def n_gust(V, U): return 1+Kg*RHO*U*V*a_w/(2*wl)
def n_stall(V): return 0.5*RHO*V*V*S*CLMAX/W
P(f"Vs {Vs:.2f} m/s (CLmax {CLMAX} EST), VA = Vs sqrt(3.4) = {VA:.1f}, VC 17, VD {VD:.0f} (D-186). a = {a_w:.2f}/rad, mu_g {mu_g:.1f}, Kg {Kg:.3f}.")
P("| Case | n | Note |"); P("|---|---|---|")
P(f"| Gust U 8 m/s at VC | {n_gust(VC,8):.2f} -> stall-limited {n_stall(VC):.2f} | wing cannot make the gust n at 17 m/s |")
P(f"| Gust U 4 m/s at VD (half, ASM-C1-UDE-D-FRAC) | {n_gust(VD,4):.2f} (stall line {n_stall(VD):.2f}) | |")
P(f"| Manoeuvre limit | +{n_lim} / -1.5 | A-P13 floor governs; ult +{n_lim*1.5:.1f} / -2.25; VA = {VA:.1f} ~ VD |")
yc = 0.45*4/(3*math.pi); L_half = n_lim*W/2
wing_half_kg = FEIN["wing_g"]/2000.0; arm_half_kg = mg("CGE-002")/2000.0; fin_half_kg = mg("FIN", "GER")/2000.0
inertia = (wing_half_kg*0.225+2*FEIN["motor_g"]/1000*0.228+arm_half_kg*0.114+fin_half_kg*0.38)*G*n_lim     # same lumps as the iteration-1 formula, masses from the CAD table
M_relief = L_half*yc-inertia; M_unrel = L_half*yc
sig = M_unrel*FS_ULT*FS_FIT*(SP[0]/2)/I_S
P(f"| Spar root bending, flight n 3.4 (elliptical lift, inertia relief) | {M_relief:.2f} N m ({M_unrel:.2f} unrelieved) | design uses unrelieved {M_unrel:.2f} limit; relief lumps: wing half {wing_half_kg*1e3:.0f} g at 0.225, 2 motor assemblies {2*FEIN['motor_g']:.0f} g at 0.228, arm half {arm_half_kg*1e3:.0f} g at 0.114, fin / rib / feet half {fin_half_kg*1e3:.0f} g at 0.38 |")
M_hg = 0.5*RHO*8**2*S*2.0/2*0.225
P(f"| Hover 8 m/s gust broadside (plate Cd 2.0): wing force {0.5*RHO*64*S*2.0:.1f} N, spar root | {M_hg:.2f} N m | below flight case |")
T_CAP = 13.08                                    # N per motor at the 72 A pack limit, fresh, derate 0.93 (T083 t083_cup_checks.md, prop_a EST; was 0.898 x 9.81 = 8.8 N for the MN2212)
T_LOW = 1.0                                      # N, lower pair (carried from the iteration-1 row, EST)
M_pitch = Z_M*(2*T_CAP-2*T_LOW)
P(f"| Cage pitch moment, upper pair at the cap ({T_CAP} N each, T-083 s4) / lower pair {T_LOW} N | {M_pitch:.2f} N m on the bridge | the cap is the bound (A-P8 limit); hover thrust per motor {W/4:.2f} N |")
R_ARM = math.hypot(Y_M, Z_M)
P(f"| Prop strike (blade stops, one motor, 30 N along thrust EST; K09-L P1 fuse idea) | arm root {30*R_ARM:.1f} N m; bridge {30*Z_M:.1f} N m | damage case |")
v_drop = math.sqrt(2*G*0.3)
P("| Transport drop 0.3 m (v %.2f m/s), cradle stroke s, efficiency 0.5 (ASM-C1-CRUSH-EFF) | n = v^2/(2 g eta s): %s | `-` box cradle not designed; s needs >= 40 mm for n <= 15 |" %
  (v_drop, "; ".join(f"s {s_*1e3:.0f} mm: {v_drop**2/(2*G*0.5*s_):.1f} g" for s_ in (0.025, 0.035, 0.050, 0.060))))
P("| Landing (see s5) | foot plateau 36 N, 24 mm, 4 feet | worst-case values from landing_a.py are tabulated in s5 |")

# ======================================================================= 3. C2 wing
P(f"\n## 3. C2 wing: spar and foam (spar {SP[0]*1e3:.0f}x{SP[1]*1e3:.0f}, tube alone: the D-226 skin, bulkheads and foam stiffen it, none credited here)")
msp = ms(SPAR_SIG, sig)
P("| Check | Stress | Allowable | MS | Result |"); P("|---|---|---|---|---|")
P(f"| Spar root bending, ult x fitting, unrelieved {M_unrel*FS_ULT*FS_FIT:.1f} N m | {sig/1e6:.0f} MPa | 350 | {msp:+.2f} | {rating(msp)} |")
tau_sp = (n_lim*W/2)*KF/(A_S/2)
P(f"| Spar shear at root (V / (A/2), KF) | {tau_sp/1e6:.1f} MPa | 30 | {ms(SPAR_TAU,tau_sp):+.1f} | {rating(ms(SPAR_TAU,tau_sp))} |")
EI_S = E_CF*I_S
ys_ = np.linspace(0, 0.45, 2001); q0 = 4*L_half/(math.pi*0.45); qy = q0*np.sqrt(np.clip(1-(ys_/0.45)**2, 0, None))
d_ell = float(np.trapezoid(qy*ys_**2*(3*0.45-ys_)/(6*EI_S), ys_)) if hasattr(np, "trapezoid") else float(np.trapz(qy*ys_**2*(3*0.45-ys_)/(6*EI_S), ys_))
d_tip = L_half*0.45**3/(3*EI_S)
P(f"| Spar tip deflection at n 3.4, elliptical load (CALC, E 70 GPa, EI {EI_S:.1f} N m2, tube alone) | {d_ell*1e3:.1f} mm of 450 mm semispan ({d_ell/0.45*100:.1f} %) | 5 % (EST) | | {'PASS' if d_ell/0.45 <= 0.05 else 'FAIL'} |")
P(f"| Same, tip-load bound (all lift at the tip, not physical) | {d_tip*1e3:.1f} mm ({d_tip/0.45*100:.1f} %) | 5 % (EST) | | info (bound) |")
P("| Spar wall under the clamp / plug zones (hoop) | PETG plugs WNG-003..005 (1.42 g each, parts table) at y = 0, +-0.285 (strut clamp), +-0.38 (rib clamp): C2 rule (unplugged ring failed by 20x) | - | - | plugs in the mass table |")
T_br = M_pitch
tau_f = T_br/(2*math.pi*(SP[0]/2)**2*0.20)*KP
P(f"| Foam shear around the spar from the bridge moment {T_br:.2f} N m (zone |y| <= 0.1, r {SP[0]/2*1e3:.0f} mm, x KP): the iteration-1 row | {tau_f/1e3:.0f} kPa | {XPS_SHEAR/1e3:.0f} | {ms(XPS_SHEAR,tau_f):+.2f} | **NOT A LOAD PATH since D-226**: the centre node (CGE-006, sleeve slip-fit on the spar, not bonded) and the bulkheads take the centre torque; judged by the C1-C7 rows of T083b s6 (min 1.09 at zeta 0.05); value shown for the record, not counted |")
Fy_f = 2*20.0
brg = Fy_f*KP/(0.065*0.0233)
P(f"| Foam bearing at the fin slot (2 x 20 N side load, 65 x 23 mm, x KP): iteration-1 row | {brg/1e3:.0f} kPa | {XPS_COMP/1e3:.0f} | {ms(XPS_COMP,brg):+.2f} | {rating(ms(XPS_COMP,brg))}; the fin node is now the D-226 bulkhead + plates (rows N1-N6, T083b) so this is secondary |")
q_air = n_lim*W/b/(0.032)
P(f"| Foam shear, lift into spar slot (n 3.4, {M_PRED} kg, 32 mm of bond, x1.5) | {q_air*FS_ULT/1e3:.1f} kPa | {XPS_SHEAR/1e3:.0f} | {ms(XPS_SHEAR,q_air*FS_ULT):+.0f} | {rating(ms(XPS_SHEAR,q_air*FS_ULT))} |")
P("| Arm / motor attachments | none in foam: the cage hangs from the spar through the 6061 centre node (D-226) and the strut clamps; foam sees only the node pocket (R >= 3 mm corners, C6 rule) | - | - | - |")
P("Fin elevon note: elevon span y 0.04-0.35 (common.py ELEV_Y0 / ELEV_Y1); the fin tube plane is y 0.38 (inner flank of the rib 0.3705).")

# ======================================================================= 4. C4 modes
P("\n## 4. C4 modes vs rotor orders (FEA-lite: 3-D Euler-Bernoulli beam frame, free-free, fe_a.py; no shell or solid model)")
def _hov(mass, der): return PA.hover(mass, der)[1]
RPM_HOV_LO = _hov(M_PRED, 1.0); RPM_HOV = _hov(M_PRED, DER_ := PA.DER); RPM_LEAN = _hov(M_PRED*1.3, DER_)
RPM_CR = (7300.0, 7600.0)                        # EST carried from QP-3 BOARD s1 item 2 (sitl/fu_level.py, MN2212, 1.50 kg); NOT re-derived for the X2216 / 1.873 kg (limit, listed in the record)
RPM_FULL_FRESH = PA.full(16.8, 0.993)[0]         # all four at the 72 A pack limit duty 0.993, fresh (T083_report.md s2.1 row 'All four, fresh, at the 72 A pack limit': 11,358)
RPM_FULL_SAG = PA.full(3.73*4, 1.0)[0]           # all four duty 1.0, sag 14.92 V rest (T083 s2.1: 10,343)
RPM_MAX = 11415.0                                # PA.full(16.8, 1.0)[0]: fresh, duty 1.0, the sweep end (APC MR limit 11,667, T083_report.md s1)
RPM_MIN = 6000.0
RPM = {f"hover derate 1.0 ({M_PRED} kg, prop_a.py hover)": RPM_HOV_LO, f"hover derate {DER_} ({M_PRED} kg)": RPM_HOV, f"hover lean 1.3 W (8 m/s gust, derate {DER_})": RPM_LEAN,
       "cruise 17 m/s (QP-3, EST carried, mid)": sum(RPM_CR)/2, "all four at the 72 A limit, fresh": RPM_FULL_FRESH, "all four duty 1.0, sag 14.92 V": RPM_FULL_SAG}
for k, v in RPM.items(): P(f"- {k}: {v:.0f} rpm: 1P {v/60:.0f} Hz, 2P {v/30:.0f} Hz")
op = [RPM_HOV_LO, RPM_HOV, RPM_LEAN, RPM_CR[0], RPM_CR[1]]
BAND_LO, BAND_HI = min(op)/60/1.2, max(op)/30*1.2
P(f"Excluded band for strongly coupled modes (iter3 rule: f <= band_low / 1.2 or f >= 1.2 band_high over the hover and cruise rpm above): **{BAND_LO:.0f}-{BAND_HI:.0f} Hz** (iter3_run.md MN2212: 84-304 Hz). The capped / full-duty states ({RPM_FULL_SAG:.0f}-{RPM_FULL_FRESH:.0f} rpm, 1P {RPM_FULL_SAG/60:.0f}-{RPM_FULL_FRESH/60:.0f} Hz, 2P {RPM_FULL_SAG/30:.0f}-{RPM_FULL_FRESH/30:.0f} Hz) are transients judged by the forced-response sweep, as iter3 did for 9,349 / 10,142 rpm.")
results = {}; frames = {}; infos = {}
for kind in ("kd", "nom", "hi"):
    F, info = fe_a.build(kind, **FEKW); results[kind] = F.solve(130); frames[kind] = F; infos[kind] = info
F_ = frames["nom"]; mass_fe = sum(e[6]*np.linalg.norm(F_.n[e[1]]-F_.n[e[0]]) for e in F_.el)+sum(F_.mass.values())
P(f"FE model mass {mass_fe*1000:.0f} g vs CAD basic {M_BASIC:.0f} g (the model carries the declared masses; tubes by A x rho, lumps as above). Modes solved: {len(results['nom'])} per corner, highest {max(r[0] for r in results['nom']):.0f} Hz (nom).")
def sep(f, rpm): return min(abs(f-rpm/60)/(rpm/60), abs(f-rpm/30)/(rpm/30))
pts = [RPM_HOV_LO, RPM_HOV, RPM_LEAN, RPM_CR[0], RPM_CR[1]]
def rpm_hits(f):
    """rpm in [RPM_MIN, RPM_MAX] at which 1P or 2P equals f: list of (order, rpm)"""
    out = []
    for o, r in (("1P", 60*f), ("2P", 30*f)):
        if RPM_MIN <= r <= RPM_MAX: out.append((o, r))
    return out
def thrust_static(rpm): return PA.prop(rpm)[0]*PA.DER     # N per motor, APC static row x derate 0.93 (prop_a.prop; EST)
Uun = 1e-6; ZET = 0.005; ZET1 = 0.01
def modal_resp(kind, rpm, thrust, zeta, orders=("1P", "2P")):
    """worst-phase modal sum at the FC (spar centre): returns per-axis acceleration (3,) summed over modes and orders (conservative: all rotors in phase for the worst case)."""
    F = frames[kind]; res = results[kind]; idx = F._idx; imu = idx["s+0.000"]; om = rpm/60*2*math.pi
    mots = [mm_ for mm_ in idx if (mm_.startswith("m+") or mm_.startswith("m-")) and ">" not in mm_]
    a = np.zeros(3)
    for tag, mult, fm in (("1P", 1, Uun*om**2), ("2P", 2, 0.05*thrust)):
        if tag not in orders: continue
        w = mult*om
        for (f, e, v, cx, cy) in res:
            wi = 2*math.pi*f
            gam = fm*(sum(abs(v[6*idx[q]+1])+abs(v[6*idx[q]+2]) for q in mots) if tag == "1P" else sum(abs(v[6*idx[q]]) for q in mots))
            h = 1/math.sqrt((wi*wi-w*w)**2+(2*zeta*wi*w)**2)
            for q in range(3): a[q] += w*w*gam*h*abs(v[6*imu+q])
    return a
def mode_res(kind, mode, tag, zeta):
    """one mode on resonance: FC acceleration sum over axes (m/s2) when 1P (tag '1P', unbalance 1 g mm x 4 rotors in the worst phase) or 2P (5 % of the static thrust at that rpm) hits it"""
    F = frames[kind]; idx = F._idx; f, e, v, cx, cy = mode; imu = idx["s+0.000"]; wi = 2*math.pi*f
    mots = [mm_ for mm_ in idx if (mm_.startswith("m+") or mm_.startswith("m-")) and ">" not in mm_]
    if tag == "1P": fm = Uun*wi**2; gam = fm*sum(abs(v[6*idx[q]+1])+abs(v[6*idx[q]+2]) for q in mots)
    else:
        rpm = 30*f; fm = 0.05*thrust_static(rpm); gam = fm*sum(abs(v[6*idx[q]]) for q in mots)
    return gam/(2*zeta)*sum(abs(v[6*imu+q]) for q in range(3))
def verdict_sep(s): return 'PASS' if s >= 0.2 else ('MARGINAL' if s >= 0.1 else 'FAIL')
P("\nModes with strong coupling to the motors (|phi| at motors in plane cy or thrust cx >= 0.5, mass-normalised), kd = E_CF 61 GPa, nom 70, hi 90 (fe_a corners; the PETG moduli are unused because the FE has no printed beam any more):")
P("| Corner | f (Hz) | group | cx / cy (2 decimals) | worst separation to 1P / 2P at the five operating rpm | inside excluded band? | single-mode FC accel on resonance if a rotor order reaches it (m/s2, zeta 0.5 %, info) | Result |"); P("|---|---|---|---|---|---|---|---|")
strong_in_band = []
for kind in ("kd", "nom", "hi"):
    res = results[kind]
    for (f, e, v, cx, cy), (f2, cl) in zip(res, fe_a.classify(res)):
        if (cx >= 0.5 or cy >= 0.5) and f < 800:
            s2 = min(sep(f, r) for r in pts); inb = BAND_LO <= f <= BAND_HI
            if inb: strong_in_band.append((kind, f))
            hits = rpm_hits(f); a_ = max([mode_res(kind, (f, e, v, cx, cy), o, ZET) for o, r in hits] or [float('nan')])
            fr = "-" if a_ != a_ else f"{a_:.2f} ({a_/30:.3f} of 30)"
            P(f"| {kind} | {f:.0f} | {cl.split(',')[0]} | {cx:.2f} / {cy:.2f} | {s2*100:.0f} % | {'YES' if inb else 'no'} | {fr} | {'**FAIL** (strong by the 0.5 rule, in band; limit not relaxed)' if inb else 'PASS (strong, outside the band)'} |")
P(f"\nStrongly coupled modes inside the excluded band: {'none' if not strong_in_band else ', '.join(f'{k} {f:.0f} Hz' for k, f in strong_in_band)}.")
if strong_in_band:
    P("Reading of the FAIL rows: this is the spar mode that iter3_run.md listed as weak (coupling 0.45, 199-242 Hz). With the D-226 masses (centre node, bulkheads, 6061 hub) its coupling rose past the threshold (cy 0.52, table above) and the D-185 rule 'strongly coupled (>= 0.5) mode inside the excluded band' fails by definition; the rule is not relaxed here. Its single-mode forced response (column above) is far below 30 m/s2 and the full rpm sweep below passes, so the open question is the rule, not the vibration level: for the design owner (D-185 threshold ruling), not changed in this task.")
for kind in ("kd", "nom", "hi"):
    lo = max([f for (f, e, v, cx, cy) in results[kind] if (cx >= 0.5 or cy >= 0.5) and f < BAND_LO] or [0]); hi = min([f for (f, e, v, cx, cy) in results[kind] if (cx >= 0.5 or cy >= 0.5) and f > BAND_HI] or [float('nan')])
    P(f"- {kind}: highest strongly coupled mode below the band {lo:.0f} Hz (limit {BAND_LO:.0f}, margin {100*(BAND_LO/lo-1) if lo else float('nan'):.0f} %); lowest above the band {hi:.0f} Hz (limit {BAND_HI:.0f}, margin {100*(hi/BAND_HI-1):.0f} %)")
P("\nWeakly coupled modes (cx, cy < 0.5: fin out-of-plane, rib, spar, centre) 20-800 Hz. Each row carries its coupling and the FORCED-RESPONSE verdict (the 20 % separation screen is not the test for these, D-185 as ruled): single mode on resonance, zeta 0.5 % (EST), 4 rotors in the worst phase, U 1.0 g mm per rotor for 1P, 2P ripple 5 % of the static thrust at that rpm (EST); FC acceleration summed over the three axes (a bound on the per-axis VIBE, limit 30 m/s2, ardupilot.org/copter/docs/common-measuring-vibration.html, 2026-11-15):")
P("| Corner | f (Hz) | group | coupling max(cx, cy) (cx / cy) | rotor order reaches it in 6,000-11,415 rpm? | single-mode FC accel on resonance (m/s2) | fraction of 30 | separation to the five operating rpm | Verdict |"); P("|---|---|---|---|---|---|---|---|---|")
weak_rows = []
for kind in ("kd", "nom", "hi"):
    res = results[kind]
    for mode, (f2, cl) in zip(res, fe_a.classify(res)):
        f, e, v, cx, cy = mode
        if 20 < f < 800 and cx < 0.5 and cy < 0.5 and (e.get("fin", 0) > 0.5 or f > 60):
            s2 = min(sep(f, r) for r in pts); hits = rpm_hits(f)
            if hits:
                a = max(mode_res(kind, mode, o, ZET) for o, r in hits); hs = ", ".join(f"{o} at {r:,.0f} rpm" for o, r in hits)
                vd = "PASS by forced response" if a < 30 else "FAIL by forced response"
                weak_rows.append((kind, f, a))
            else: a = float('nan'); hs = "no (unreachable)"; vd = "PASS (no rotor order reaches it)"
            P(f"| {kind} | {f:.0f} | {cl} | {max(cx,cy):.2f} ({cx:.2f} / {cy:.2f}) | {hs} | {'-' if a != a else f'{a:.2f}'} | {'-' if a != a else f'{a/30:.3f}'} | {s2*100:.0f} % | {vd} |")
P("\nForced response, full rpm sweep (all four rotors at the same rpm, 1P + 2P of all rotors added, worst-phase modal sum, all modes solved above; static thrust law for the 2P term at every rpm = conservative in cruise). Hard-mounted FC (D-186): foam tape taken rigid (mount frequency not measured, EST):")
P("| Corner | zeta | worst FC accel 6,000-11,415 rpm, sum of axes (m/s2) at rpm | per-axis max / sqrt2 (VIBE-like) | MS vs 30 (sum of axes bound) | worst up to 10,343 rpm (all four duty 1.0, sag) | worst up to 9,349 rpm | cruise 7,300-7,600 (T 0.5 N EST) |"); P("|---|---|---|---|---|---|---|---|")
sweep = {}
rr = np.arange(RPM_MIN, RPM_MAX+1, 25.0)
for kind in ("kd", "nom", "hi"):
    for zt in (0.01, 0.005):
        A = np.array([modal_resp(kind, r, thrust_static(r), zt) for r in rr]); tot_ = A.sum(axis=1); k = int(np.argmax(tot_)); pa = A.max(axis=0).max()/math.sqrt(2)
        w1 = tot_[rr <= 10343].max(); k1 = int(np.argmax(np.where(rr <= 10343, tot_, 0))); w2 = tot_[rr <= 9349].max()
        cr = max(modal_resp(kind, r, 0.5, zt).sum() for r in np.arange(RPM_CR[0], RPM_CR[1]+1, 25.0))
        sweep[(kind, zt)] = (tot_[k], rr[k], pa)
        P(f"| {kind} | {zt*100:.1f} % | {tot_[k]:.1f} at {rr[k]:,.0f} | {pa:.1f} | {30/tot_[k]-1:+.2f} | {w1:.1f} at {rr[k1]:,.0f} | {w2:.1f} | {cr:.1f} |")
worst_sweep = max(v[0] for v in sweep.values()); worst_pa = max(v[2] for v in sweep.values())
P(f"Sweep verdict: worst sum-of-axes {worst_sweep:.1f} m/s2 (MS {30/worst_sweep-1:+.2f} vs 30 as a bound), worst per-axis rms-like {worst_pa:.1f} m/s2 (MS {30/worst_pa-1:+.2f}): {'PASS' if worst_sweep < 30 else ('PASS on the per-axis (VIBE-like) figure only; the sum-of-axes bound FAILS' if worst_pa < 30 else 'FAIL')}. Closes the T-083 open item 'extend the A-P10(b) sweep to 11,400 rpm' for the beam-FE model.")
P("\nNot re-run here (listed in T066_record.md): the control-band gain-margin clause of iter3_run.md (`sitl/fu_cage.py`) with the X2216 masses / inertias, and a tap test of the built cage.")
F, info = fe_a.build("kd", **FEKW)
P(f"\nFin out-of-plane EI {info['EI_out']:.1f} N m2 (kd, 16x14 tube), mass/length {info['mu']*1e3:.0f} g/m (tube + 3 mm foam fairing + tape); rib EI (25x23) {E_CF*I_R:.0f} N m2 (was 14x12: {E_CF*math.pi/64*(0.014**4-0.012**4):.0f}). D-202 arm crossing: arms modelled as four 12x10 beams meeting at one hub node (see limits in T066_record.md).")

# static mount stiffness and strength
P("\n### Mount stiffness and strength (limit load at the cap, design = x1.5 x1.15 x1.25 on printed / bonded, x1.5 x1.15 on CF)")
T_u = T_CAP
arm_L = R_ARM-0.03
M_arm = T_u*arm_L
sig_arm = M_arm/Z_A*KF
P("| Item | Value | Allowable | MS | Result |"); P("|---|---|---|---|---|")
P(f"| Arm 12x10 root bending, thrust {T_u:.2f} N at {arm_L:.3f} m = {M_arm:.2f} N m | {sig_arm/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_arm):+.2f} | {rating(ms(CF_SIG_ARM,sig_arm))} (T-083 cup checks: 63.38 MPa, MS +4.52 with torque) |")
M_ps = 30*(arm_L+0.080); sig_ps = M_ps/Z_A*KF
P(f"| Arm, prop strike 30 N (EST) at lever {arm_L:.3f} + 0.080 m = {M_ps:.1f} N m (lever as t083_cup_checks.md: MS +0.82) | {sig_ps/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_ps):+.2f} | {rating(ms(CF_SIG_ARM,sig_ps))} |")
M_br = 30*Z_M; sig_br = M_br/Z_B*KF
P(f"| Bridge 16x14 in prop strike, {M_br:.1f} N m | {sig_br/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_br):+.2f} | {rating(ms(CF_SIG_ARM,sig_br))} |")
M_br2 = M_pitch; sig_br2 = M_br2/Z_B*KF
P(f"| Bridge 16x14, max control pitch moment {M_br2:.2f} N m | {sig_br2/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_br2):+.2f} | {rating(ms(CF_SIG_ARM,sig_br2))} |")
m_pack_hub = (mg("PWR")+mg("CGE-008")+mg("CGE-001")+mg("CGE-009")+mg("CGE-010")+mg("HRN-003")+mg("HRN-004"))/1000.0
L_br = m.BR_X1-X_HUB                             # hub axis to the bridge end in the centre-node socket (EST lever; the struts are ignored: conservative)
Mpk = m_pack_hub*12*G*L_br
sig_pk = Mpk/Z_B*FS_ULT*FS_FIT
P(f"| Bridge, pack + hub + tray + doublers at 12 g crash ({m_pack_hub*1000:.0f} g x 12 g x {L_br:.4f} m = {Mpk:.1f} N m, A-P5), struts ignored | {sig_pk/1e6:.0f} MPa | 350 | {ms(CF_SIG_ARM,sig_pk):+.2f} | {rating(ms(CF_SIG_ARM,sig_pk))} |")
k_arm = 3*E_CF*I_A/arm_L**3
P(f"| Arm tip stiffness {k_arm/1e3:.1f} N/mm: thrust deflection | {T_u/k_arm*1e3:.2f} mm (T-083: 2.0 mm) | - | - | info |")
P(f"| Hub pitch rotation under the max control moment: M L / EI (bridge 16x14, {E_CF*I_B:.1f} N m2, bridge alone, no struts) | {math.degrees(M_pitch*(m.BR_X1-m.BR_X0)/(E_CF*I_B)):.1f} deg | - | - | info; soft-mount note of the iteration-1 row is superseded: the pitch mode is in the FE table above |")
Pcr = math.pi**2*E_CF*I_B/(L_br*2)**2; Psum = 4*T_CAP*math.cos(math.radians(m.CANT))
P(f"| Bridge buckling under the thrust sum at the cap 4 x {T_CAP} x cos 17 deg = {Psum:.0f} N (cantilever-pin K=2, L {L_br:.4f} m, x KF) | P_cr {Pcr:.0f} N | | {Pcr/(Psum*KF)-1:+.1f} | {rating(Pcr/(Psum*KF)-1)} |")
P("| Motor screws / X-mount / cup rows | carried from `mechanism/out/T083_data/t083_cup_checks.md` (X2216 on the X-mount, 4 x M3): min MS +0.46 (plate strip at the nut, -y bolts), all PASS | | +0.46 | PASS (carried, s6) |")

# ======================================================================= 5. C5
P("\n## 5. C5 landing on fin-tip feet (rigid-body dynamics + hand calculation)")
TABLE_T066 = os.path.join(HERE, "T066_data", "cad_part_table_T066.json")
if not os.path.exists(TABLE_T066):
    os.makedirs(os.path.dirname(TABLE_T066), exist_ok=True); LM.build_table(TABLE_T066)
LM.TABLE = TABLE_T066; LM._P = None
st = landing_a.static()
FP, SMAX = 36.0, 0.024                           # N plateau, m usable stroke (T083_report.md s5.2: the lowest round plateau with end tilt <= 3.0 deg and no bottoming at 1.912 kg)
cgx, cgz = landing_a.geom()["cg"][0], landing_a.geom()["cg"][2]
XF = 0.3415+1.5*(SMAX-0.020)                      # pad x: PAD_D2 x_foot 0.3415 (landing_path_a.PAD_D2) + 1.5 x (stroke - 20 mm) (t076d_step2_table.pad_geometry, D-222 s4.1)
ZF = math.tan(math.radians(30.5))*(XF-cgx)+cgz-0.006      # pad centre z: edge holds A-P9 30.5 deg, pad dz 12 mm
P(f"Static (drawn pads, CG {st['cg_x']*1e3:.2f} mm aft of LE from cad_mass.json, ground plane x {landing_a.geom()['x_foot']:.4f}): tip-over narrow axis **{st['tip_narrow']:.1f} deg: {'PASS' if st['tip_narrow'] >= 30 else 'FAIL'} vs A-P9 30 deg** (pre-existing: the drawn pads have not met A-P9 since T-083, T083_report.md s5.2 gives 29.48 at CG 24.41 mm; the analysis pad of D-222 s4.1 is designed for 30.5 and is not drawn), wide axis {st['tip_wide']:.1f} deg. Parked broadside to the wind: tips at {st['v_tip_parked']:.1f} m/s; restoring / overturning at 5 m/s {st['restore_ratio_5ms']:.2f}. I (kg m2, CAD part-table model scaled to {M_PRED} kg): {np.round(st['I'],4).tolist()}.")
P(f"Demand basis (T-083, reused): pad plateau {FP:.0f} N, usable stroke {SMAX*1e3:.0f} mm, pad x {XF:.4f} m, z {ZF:.4f} m (analysis pad of D-222 s4.1, not the drawn pad), mass {M_PRED} kg, CG from cad_mass.json ({cgx*1e3:.2f} mm), CAD part-table mass model rebuilt from the current CAD (`T066_data/cad_part_table_T066.json`, {len(LM.parts())} parts, basic {LM.basic_mass_kg():.4f} kg), friction mu 0.40 / 0.30, pad zeta 0.02 / 0.05 / 0.10 (EST, TP-3 measures it), dt 0.2 ms.")
S_ = math.pi/2
CASES = [("hard level", dict(v_sink=1.2)), ("hard 10 narrow", dict(v_sink=1.2, th_n=10)), ("hard 10 narrow neg", dict(v_sink=1.2, th_n=-10)),
         ("hard 10 wide", dict(v_sink=1.2, th_w=10)), ("hard 7/7 combo", dict(v_sink=1.2, th_n=7, th_w=7)),
         ("hard 10 narrow + drift .5", dict(v_sink=1.2, th_n=10, drift=0.5, drift_dir=0.0)), ("hard 10 wide + drift .5 y", dict(v_sink=1.2, th_w=10, drift=0.5, drift_dir=S_)),
         ("normal level .5", dict(v_sink=0.5)), ("normal 10 narrow .5", dict(v_sink=0.5, th_n=10)), ("normal 10 wide .5 + drift", dict(v_sink=0.5, th_w=10, drift=0.5, drift_dir=S_))]
for n_, lean, lat, sink in (("Tb_h5", 16.5, 0.09, 0.31), ("Ta_h5", 18.8, 0.11, 0.30), ("Z5_b45", 17.2, 0.21, 0.32), ("Lb_5e", 12.1, 0.45, 0.32), ("Z5_gb45", 11.0, 0.50, 0.32)):
    CASES.append((f"SITL {n_} wide (y drift)", dict(v_sink=sink, th_w=lean, drift=lat, drift_dir=S_)))
    CASES.append((f"SITL {n_} narrow (z drift)", dict(v_sink=sink, th_n=lean, drift=lat, drift_dir=0.0)))
CASES.append(("hard 16 wide + drift .5 y", dict(v_sink=1.2, th_w=16, drift=0.5, drift_dir=S_)))   # = landing_path_a.cases(False): 21 cases (the T-083 text says 23; same function, same stats as T083b s4.3)
P(f"Sim = `landing_a.py` (6 dof, 4 elasto-plastic feet, Coulomb friction, rotor lift 2/3 W to 0.3 s then 0 at 0.6 s), {len(CASES)} cases x 3 zeta x 2 mu = {len(CASES)*6} runs. Rib-root check: the 25x23 CF rib (OD {landing_a.RIB_OD*1e3:.0f} / ID {landing_a.RIB_ID*1e3:.0f} mm, root x {landing_a.RIB_X0*1e3:.1f} mm) under bending, torsion and axial load, all four feet resolved in the body frame at every step, RF = 1 / sqrt((KF (M/Z + N/A) / 350 MPa)^2 + (KF T r / J / 30 MPa)^2), KF {KF:.3f}, both allowables EST (no coupon); the RB value is then divided by the DAF {DAF_WING} (D-223 wing / rib; x1.5 floor stays).")
allres = {}
for zeta in (0.02, 0.05, 0.10):
    for mu in (0.40, 0.30):
        for name, kw in CASES:
            allres[(zeta, mu, name)] = landing_a.simulate(m=M_PRED, Fp=FP, s_max=SMAX, zeta=zeta, mu=mu, dt=2e-4, T=1.5, x_foot=XF, z_foot=ZF, **kw)
P("\nTable at pad zeta 0.05, mu 0.40 (the iteration-1 basis):")
P("| Case | max stroke (mm) of 24 | permanent set (mm) | peak foot load (N) | side load (N) | n at CG | end tilt (deg) | drift (mm) | rib-root RF, rigid-body | rib-root RF x2.23 |"); P("|---|---|---|---|---|---|---|---|---|---|")
for name, kw in CASES:
    r = allres[(0.05, 0.40, name)]
    P(f"| {name} | {r['dmax_mm'].max():.1f} | {r['sp_mm'].max():.1f} | {r['F'].max():.0f} | {r['side'].max():.0f} | {r['n_peak']:.1f} | {r['tilt_end']:.1f} | {r['drift_end']*1e3:.0f} | {r['rib_rf']:.2f} | {r['rib_rf']/daf(DAF_WING):.2f} |")
P("\nEnvelope over all 21 cases, by pad zeta and friction:")
P("| zeta | mu | worst stroke (mm) of 24 | worst end tilt (deg, limit 3.0) | peak n (g, A-P5 limit 12) | peak foot load (N) | worst side load (N) | min rib-root RF (RB) | min rib-root RF x2.23 | verdict |"); P("|---|---|---|---|---|---|---|---|---|---|")
env = {}
for zeta in (0.02, 0.05, 0.10):
    for mu in (0.40, 0.30):
        rs = [allres[(zeta, mu, n_)] for n_, _ in CASES]
        stroke = max(r['dmax_mm'].max() for r in rs); tilt = max(r['tilt_end'] for r in rs); nn = max(r['n_peak'] for r in rs); ff = max(r['F'].max() for r in rs); sd = max(r['side'].max() for r in rs)
        rf = min(r['rib_rf'] for r in rs); env[(zeta, mu)] = (stroke, tilt, nn, rf)
        vd = []
        if stroke > 24: vd.append("pad bottoms")
        if tilt > 3.0: vd.append("tilt > 3.0")
        if nn > 12: vd.append("n > 12 g (A-P5)")
        if rf/daf(DAF_WING) < 1.0: vd.append("rib-root RF < 1 at x2.23")
        P(f"| {zeta} | {mu} | {stroke:.1f} | {tilt:.2f} | {nn:.1f} | {ff:.0f} | {sd:.0f} | {rf:.2f} | {rf/daf(DAF_WING):.2f} | {'PASS' if not vd else 'FAIL: ' + '; '.join(vd)} |")
P(f"\nRib-root RF at x2.23 (this file, rib 25x23 hand row) vs T-083 R1 / R2 rows: T-083 min 1.16 at zeta 0.05 and 1.06 over all zeta (rib at the node exit x 176 and at the root-fitting mouth); T-083b sensitivity at 1.873 kg: 1.12-1.13. This row is the rib at x 70.5 mm with feet resolved about the rib root, a different station, so the numbers are compared, not equated. Pad life: normal landings set the permanent set shown above; replace the pad at 10 mm cumulative set (EST carried from iteration 1; the pad is specified by its dynamic force, D-222).")
P(f"Side load per foot: worst {max(r['side'].max() for r in allres.values()):.1f} N at mu 0.40 / 0.30 (pad friction is an assumption, not measured: drag-test the EVA/PE pad, TP-3). Limits: pad plateau, stroke, zeta and friction are specification values pending the bench drop test; the drawn pad is not the analysis pad (T083_report.md s5.2).")

# ======================================================================= 6. carried rows
P("\n## 6. C6 joints, fasteners, bonds: CARRIED FORWARD from the records that replaced the iteration-1 hand rows (not recomputed here)")
P("The iteration-1 rows of this section judged the PETG hub, PETG saddles, PETG root block, 0.1 mm CFRP fin skins, M3 motor screws and the PETG pack-tray flange. None of those parts exists in the current CAD (CGE-001 is a machined 6061 hub, D-220 / D-221; the D-226 centre node CGE-006 and bulkheads replace the saddles; FIN-003 is a 6061 fitting, D-229; the fin is a 16x14 tube + foam fairing; the motors sit on the SunnySky X-mount, T-083; the tray CGE-008 is a 1.2 mm windowed plate, T-077). Re-running the old formulas on parts that are not drawn would give no information, so each row is replaced by the judging record's value (all at KF 1.725 / KP 2.156, x2.23 on the T-083 demand unless stated; EST allowables except where marked V):")
P("| Joint / part | Judging record | Min RF or MS (pad zeta 0.02 / 0.05 / 0.10 unless one value) | Basis | Verdict |"); P("|---|---|---|---|---|")
carried = [
 ("FIN-003 6061 root fitting (ring, plug, plate, bonds Q1-Q8)", "T083b_report.md s3", "RF 1.21 (zeta <= 0.05), 1.40 (0.02), 0.89 (0.10)", "T-083 demand, x2.23, 6061 yield 240 MPa", "PASS zeta <= 0.05; **FAIL at 0.10 (0.89)**; integrity-class peel rows 0.15-0.16 (outside the RF minimum, T-069 F-3, TP-4)"),
 ("Whole D-226 cell, rib, bridge, strut, R4 clamp at the new 1.873 kg / CG 22.26 mm", "T083b_report.md s4.3", "min 1.09 (R4 junction, zeta 0.05); zeta 0.10 min 0.66 (C3)", "sensitivity re-run of the T-083 demand", "PASS zeta <= 0.05; **FAIL at 0.10**"),
 ("Centre node CGE-006 + bulkheads WNG-013 (C1-C7)", "T083_report.md s5.3 / strength_table_t083.md (1.913 kg)", "RF 1.16 (0.02) / 1.18 (0.05) / **0.66 (0.10, C3 flange bond)**", "x2.23", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Fin node FIN-005 / FIN-009 / straps (N1-N6)", "same", "RF 1.24 / **1.11** / 0.83 (N3, N4a)", "x2.23", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Rib FIN-002 25x23 (R1, R2)", "same", "RF 1.14 / 1.16 / 1.06", "x2.23, tau 30 MPa EST", "PASS all zeta"),
 ("Skin WNG-011 + WNG-014 (3 plies) K1-K3", "same", "RF 1.32 / 1.16 / 0.76 (K1), 0.87 (K2)", "x2.23, S 70 MPa lower bound EST", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Wing section P15 / P16", "same", "RF 1.39 / 1.23 / 0.80 (P15 foam shear)", "x2.23", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Bridge CGE-004 16x14 (B1 bending at the socket mouth)", "same", "RF 1.39 / 1.21 / 0.93", "x2.23", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Strut CGE-005 8x6 + R4 clamp CGE-007", "same + strut_clamp_t083.md; T083b s4.3", "RF 1.40 / 1.13 (1.09 at 1.873 kg) / 0.87-0.90", "x2.23", "PASS zeta <= 0.05; FAIL at 0.10"),
 ("Motor mount + cup rows (X-mount, M3, plate strip, cup-to-arm bond)", "T083_report.md s4, t083_cup_checks.md", "MS +0.46 (plate strip at the nut)", "limit x KF / KP, strike 30 N EST, cap 13.08 N", "PASS"),
 ("Arm tubes, arm bond, hub sockets and sleeves (landing, DAF 1.97)", "T083_report.md s5; hub FEA (fea_hub.py runs d209 / d210)", "see those records; G1 arm-tube B axial RF 0.94 passes only if measured pad zeta < about 0.088 (D-223)", "DAF 1.97 on the arm tubes", "see the record"),
]
for a_ in carried: P("| " + " | ".join(a_) + " |")
P("\nSummary of the carried landing rows: every class-RF row passes at pad zeta <= 0.05 (min 1.09); at zeta 0.10 nine row groups fail (min 0.66) and A-P5 12 g is exceeded (12.7 g). The pad zeta is an EST until the TP-3 drop test; this is a test gap, not a design change made here.")
open(os.path.join(HERE, "structures_run.md"), "w").write("\n".join(OUT))
