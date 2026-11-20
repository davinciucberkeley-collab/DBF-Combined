"""Concept A arm + motor-cup structural checks (STRUCTURES, QP-5 'are the arms good enough for flight').
Reproduce: python -I arm_cup_checks.py   (stdlib only; prints markdown and writes arm_cup_checks.md next to this file)
Covers: motor cup CGE-003 (screws, head pull-through, plate, sleeve, bond) at max thrust + motor torque + 1P, and at prop strike;
arm tip hard-landing / tip-over; fatigue of arm tube, hub-socket bond, cup bond, cup screws; arm tip deflection and thrust-line tilt;
tap-test thresholds.  Geometry is READ from cad/amodel/wing.py and propulsion.py (constants copied below with the line they come from).
Labels: V vendor/repo file, CALC computed here, EST estimate (flagged), '-' unknown.  Factors as structures_a.py: KF 1.5x1.15, KP KF x1.25."""
import math, os, sys

HERE = r"C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/structures"; T076 = os.path.dirname(os.path.abspath(__file__))
G = 9.81
KF = 1.5 * 1.15
KP = KF * 1.25
OUT = []


def P(s=""):
    print(s); OUT.append(s)


def ms(allow, stress):
    return allow / stress - 1


def rate(m):
    return "PASS" if m >= 0.15 else ("MARGINAL" if m >= 0 else "FAIL")


ROWS = []


def row(item, load, value, allow, m, note=""):
    ROWS.append((item, load, value, allow, m, note))


def mrow(item, load, stress_mpa, allow_mpa, note=""):
    m = ms(allow_mpa, stress_mpa)
    row(item, load, f"{stress_mpa:.2f} MPa", f"{allow_mpa:.1f} MPa", m, note)


# ---------------------------------------------------------------- geometry (m)  [wing.py L31-32, L575-584; propulsion.py L28-43]
ARM_OD, ARM_ID, L_ARM = 0.012, 0.010, 0.246            # wing.py ARM_OD/ID; 12 x 10 tube, thrust lever 0.246 m (task / iter2_margins)
# T-073 R3 (D-216 s4 R3, lightened cup) flags.  DEFAULT = the CAD of 2026-11-19 (output identical to the committed arm_cup_checks.md).
#   --r3      T-070 spec as written: boss plate 5 mm only at the 4 screw bosses, 3 mm web elsewhere (incl. the two +y cantilever tabs), sleeve wall 3.5 -> 2.5 mm (OD 17.2) except at the screw-head pockets.
#   --r3fix   same, but the +y cantilever region (y 3.5 .. 16.5) keeps the full 5 mm plate (what S2 needs); web 3 mm only outboard of the screw pattern / -y side.
# Tab geometry of the 3 mm web is a T-073 ASSUMPTION (not drawn): two cantilever tabs 9 mm wide each at |z| 3.5 .. 12.5 reaching the +y bosses.
R3 = "--r3" in sys.argv or "--r3fix" in sys.argv; R3FIX = "--r3fix" in sys.argv
PLATE_T, PLATE_W = 0.005, 0.033                        # wing.py L575: prism x -0.012 .. -0.007, _rrect(0.0165, 0.0165, 0.006)
SLV_RO, SLV_RI, SLV_Y0, SLV_Y1 = 0.0095, 0.006, -0.025, 0.0035
SLV_RO_POCKET = SLV_RO                                    # screw-head pocket region keeps the full wall in R3
WEB_T, TAB_W_TOT = PLATE_T, None                          # web thickness (junction / S2 shear) and cantilever tab width (None = full net section)
if R3:
    SLV_RO = SLV_RI + 0.0025                               # wall 3.5 -> 2.5 mm
    WEB_T = 0.003
    if not R3FIX: TAB_W_TOT = 0.018                        # 2 tabs x 9 mm, 3 mm thick   # wing.py L576: tube Y from -0.025 length 0.0285, ro 0.0095, ri 6.0 mm
PAT_Y, PAT_Z = 0.019, 0.016                            # CUP_PAT
HOLE_D = 0.0029                                        # 2.9 mm clearance (ISO 273 medium M2.5), wing.py L579
HEAD_D, HEAD_K = 0.0045, 0.0025                        # propulsion.py _m25_screw ISO 4762 M2.5 dk 4.5, k 2.5
EMBED = 0.025                                          # arm in cup sleeve 25 mm (wing.py L431)
ENG, ENG_MIN = 0.0030, 0.0020                          # thread engagement in the motor base, propulsion.py STACK eng=3.0, mineng=2.0 (base ring 3.5 EST)
X_PROP = 0.047                                         # prop mid-plane above the arm axis: flange top 43.0 + half APC hub 4.3 (propulsion.py X_FLANGE_TOP, HUB_T_P) EST
LEV = X_PROP - 0.012                                   # lever of a transverse prop force above the motor base face (plate front face x -12 mm)
R_B = 0.08                                             # effective radius of a blade strike force, EST (APC 9x4.5: R 114 mm tip)
R_PAT = math.hypot(PAT_Y / 2, PAT_Z / 2)

# arm tube section
I_ARM = math.pi / 64 * (ARM_OD ** 4 - ARM_ID ** 4)
Z_ARM = I_ARM / (ARM_OD / 2)
E_NOM, E_KD = 70e9, 61e9                               # iter3_run.md corners (kd 61, nom 70, hi 90 GPa)
EI_NOM, EI_KD = E_NOM * I_ARM, E_KD * I_ARM

# ---------------------------------------------------------------- loads
# Thrust and shaft torque from the APC 9x4.5MR static table (prop_a.py T dict), x0.93 derate (prop_a.py DER)
TAB = {9000: (8.746, 113.149), 10000: (10.830, 154.758)}
def tp(n):
    f = (n - 9000) / 1000
    return tuple(TAB[9000][i] + f * (TAB[10000][i] - TAB[9000][i]) for i in (0, 1))
N_CAP, N_UNC = 9349.0, 10142.0                         # prop_a.py output: duty 0.90 and 1.00, fresh pack
T_CAP = 0.898 * G                                      # 8.81 N: prop_a.py 898 gf x0.93 = structures_run.md T_cap
T_UNC = 1.058 * G                                      # 10.38 N: prop_a.py 1058 gf x0.93 (uncapped fault)
Q_CAP = tp(N_CAP)[1] / (N_CAP * 2 * math.pi / 60)      # shaft torque = P/omega (APC power, same rpm)
Q_UNC = tp(N_UNC)[1] / (N_UNC * 2 * math.pi / 60) if N_UNC <= 10000 else (154.758 + (N_UNC - 10000) / 1000 * (205.680 - 154.758)) / (N_UNC * 2 * math.pi / 60)
T_HOV = 0.404 * G * 0.93 / 0.93                        # prop_a.py hover 1.5 kg: 404 gf per motor (already the real thrust)
U_UNB = 1.0e-6                                         # 1 g mm per rotor, iter3_run.md EST (ISO G16 prop would be 0.27 g mm)
F_STRIKE = 30.0                                        # N, prop strike (structures_a.py, iter2_margins.md EST)
M_STRIKE_HUB = F_STRIKE * 0.2762                       # 8.29 N m couple at the hub (structures_run.md)

# material allowables (structures_a.py L16-L20; all EST until coupons)
CF_SIG = 350e6
PETG_BEAR, PETG_ILAY = 20e6, 9.5e6
BOND_TAU = 2.0e6
STEEL_SIG = 450e6                                      # structures_a.py allowable for M3 screw tension (EST); M2.5 same class assumed
AL_THREAD_TAU = 0.6 * 150e6                            # structures_a.py L222: aluminium base thread strip allowable (EST; base alloy not published)
A_S25 = 3.39e-6                                        # M2.5 tensile stress area, ISO 898-1 (V: standard value 3.39 mm2)
A_HEAD = math.pi / 4 * (HEAD_D ** 2 - HOLE_D ** 2)     # head bearing annulus on the plate rear face

P("# Arm and motor-cup checks (concept A)")
P("")
P("Reproduce: `python -I redesign/qp/A/structures/arm_cup_checks.py`. Limit loads x factors as `structures_a.py` (KF 1.725 on CF/metal, KP 2.156 on printed/bonded). Allowables are the repo's EST values (structures_a.py L16-20; coupons not yet run).")
P("")
P("## 0. Inputs")
P(f"- Arm 12x10 CFRP: I {I_ARM*1e12:.0f} mm4, Z {Z_ARM*1e9:.1f} mm3, EI {EI_NOM:.1f} N m2 (E 70 GPa nom; kd 61 GPa gives {EI_KD:.1f}); lever to the motor axis {L_ARM*1e3:.0f} mm.")
P(f"- Thrust at the 0.90 spin cap {T_CAP:.2f} N / shaft torque {Q_CAP*1e3:.0f} N mm (prop_a.py: APC 9x4.5MR PER3 table, {N_CAP:.0f} rpm, P = {tp(N_CAP)[1]:.0f} W, Q = P/omega); uncapped fault {T_UNC:.2f} N / {Q_UNC*1e3:.0f} N mm at {N_UNC:.0f} rpm (structures_a.py: the 0.153 N m value). Hover {T_HOV:.2f} N per motor (prop_a.py, 1.50 kg).")
P(f"- 1P unbalance 1 g mm (iter3_run.md EST): force {U_UNB*(N_CAP*2*math.pi/60)**2:.2f} N at the cap rpm, {U_UNB*(7600*2*math.pi/60)**2:.2f} N at cruise 7,600 rpm.")
P("- Cup (wing.py L575-584): plate 33 x 33 x 5 mm (corner R 6), 4 holes 2.9 mm on 19 x 16; arm sleeve OD 19.2 / ID 12.2 (0.1 mm epoxy gap, D-198) / 28.5 mm long (y -25 .. +3.5) + a 1.0 mm wall lead collar y 3.5 .. 8.8 and a 4.8 mm lead hole through the plate at y 5.5 mm (D-198; net plate section 30.3 x 5 mm at the sleeve end); 25 mm embed, epoxy. **There are no screw bosses and no nut: the screws are M2.5x8 SHCS with heads on the plate REAR face, threading 3 mm into the tapped aluminium motor base** (propulsion.py `_m25_screw`, E-PRP STACK eng 3.0). The motor is pulled away from the plate by thrust, so the head bears on the PETG (pull-through) and the thread is loaded in tension.")
P(f"- Strike (structures_a.py: 30 N EST): S1 axial 30 N along the shaft; S2 transverse 30 N at the prop plane {X_PROP*1e3:.0f} mm above the arm axis ({LEV*1e3:.0f} mm above the motor base face, EST); S3 tangential blade stop, torque {F_STRIKE*R_B:.1f} N m about the shaft (r {R_B*1e3:.0f} mm EST). The repo's existing 7.4 N m arm-root number assumes force only; S3 adds the blade offset to the arm-root moment (arm row below).")
P("")

# ---------------------------------------------------------------- (a) operating: max thrust + torque + 1P
T, Q = T_CAP, Q_CAP
F1 = U_UNB * (N_CAP * 2 * math.pi / 60) ** 2
P_screw_T = T / 4 * 2.0                                # tension per screw, x2 prying allowance (structures_a.py s6 convention)
P_screw_1P = F1 * LEV / (4 * PAT_Z / 2) / 1.0          # 1P radial force at the prop plane -> moment on the pattern, worst screw (couple over 16 mm, 4 screws)
P_op = P_screw_T + P_screw_1P
mrow("Cup screw M2.5 tension (4 screws), thrust 8.8 N x2 prying + 1P", f"{T:.1f} N + 1P {F1:.2f} N: {P_op:.1f} N/screw", P_op * KF / A_S25 / 1e6, STEEL_SIG / 1e6, "steel allowable EST")
mrow("Thread strip in tapped Al motor base, 3.0 mm engagement (2.0 min)", f"{P_op:.1f} N/screw", P_op * KF / (math.pi * 2.2e-3 * ENG_MIN * 0.5) / 1e6, AL_THREAD_TAU / 1e6, "base alloy and thread depth not published (EST); min engagement used")
mrow("Head pull-through: PETG bearing under the 4.5 mm head (annulus 9.3 mm2)", f"{P_op:.1f} N/screw", P_op * KP / A_HEAD / 1e6, PETG_BEAR / 1e6, "no counterbore, no washer")
A_PUNCH = math.pi * HEAD_D * PLATE_T
mrow("Plate punching shear round the head (pi x 4.5 x 5 mm), cross-layer allowable", f"{P_op:.1f} N/screw", P_op * KP / A_PUNCH / 1e6, PETG_ILAY / 1e6, "printed with the shaft axis up: layer plane = plate plane (EST); worst case interlayer allowable used")
# plate cantilever beyond the sleeve end (y +3.5 .. +9.5): two +y screws, 6 mm lever; section 33 x 5
M_pl = 2 * P_op * (PAT_Y / 2 - SLV_Y1)
LEAD_CHORD = 2 * (0.0024 ** 2 - (0.0055 - 0.0035) ** 2) ** 0.5       # D-198: 4.8 mm lead hole at y 5.5 mm; its chord at the sleeve end plane y 3.5 mm = 2.66 mm (wing.py PH_HOLE_R, PH_Y)
Z_pl = ((PLATE_W - LEAD_CHORD) * PLATE_T ** 2 / 6) if TAB_W_TOT is None else (TAB_W_TOT * WEB_T ** 2 / 6)                       # net section at the sleeve end plane (the governing section of the 6 mm cantilever)
mrow("Plate bending, cantilever 6 mm past the sleeve end (2 screws, net section 30.3 x 5 mm after the D-198 lead hole)", f"{M_pl*1e3:.0f} N mm", M_pl * KP / Z_pl / 1e6, PETG_ILAY / 1e6, "plate in bending uses the interlayer allowable (worst)")
# motor torque on the screws: shear/bearing on 2 screws (friction ignored), 3x worst-case sharing
V_Q = Q / (4 * R_PAT) * 2.0
mrow("Hole bearing, motor torque 0.130 N m shared on 2 of 4 screws (hole 2.9 x 5 mm)", f"{V_Q:.1f} N/screw", V_Q * KP / (HOLE_D * PLATE_T) / 1e6, PETG_BEAR / 1e6, "friction of the clamped base ignored")
# bond under thrust + torque at the free end of the sleeve (load at the arm tip: shear + moment pair)
tau_T = T * KP / (math.pi * ARM_OD * EMBED)            # transverse shear flux from the thrust (arm end load)
pair_Q = (Q / 0.025)                                   # shaft torque is a bending moment on the arm axis; pair over the embed (structures iter2 convention)
tau_Q = pair_Q * KP / (0.5 * math.pi * ARM_OD * EMBED)
mrow("Cup-to-arm bond (25 mm embed, 12 mm tube), thrust shear + torque couple", f"{T:.1f} N, {Q*1e3:.0f} N mm", math.hypot(tau_T, tau_Q) / 1e6, BOND_TAU / 1e6, "end-loaded sleeve: no thrust couple (thrust line passes through the arm axis); allowable E-FIN-13 EST")
# sleeve wall at the mouth under the torque couple (6 mm patch)
mrow("Sleeve wall hoop at the mouth, torque couple (%.1f mm wall, 6 mm bearing patch)" % ((SLV_RO - SLV_RI) * 1e3), f"{pair_Q:.0f} N", 2 * pair_Q * KP / (math.pi * 0.006) / (SLV_RO - SLV_RI) / 1e6, PETG_BEAR / 1e6, "same ring model as qp5_checks s2")
# junction plate-sleeve crest
A_JUN = 0.0128 * 0.020
mrow("Plate-to-sleeve crest junction (12.8 x 20 mm strip), tension from thrust", f"{T:.1f} N", T * KP / A_JUN / 1e6, PETG_ILAY / 1e6, "")
# uncapped fault case
P_unc = T_UNC / 4 * 2.0
mrow("FAULT uncapped (10.4 N): head pull-through", f"{P_unc:.1f} N/screw", P_unc * KP / A_HEAD / 1e6, PETG_BEAR / 1e6, "ESC cap failed; ultimate factors kept")

# ---------------------------------------------------------------- (b) prop strike
# S1 axial 30 N
Ps1 = F_STRIKE / 4 * 2.0
mrow("Strike S1 axial 30 N: head pull-through", f"{Ps1:.1f} N/screw", Ps1 * KP / A_HEAD / 1e6, PETG_BEAR / 1e6, "")
# S2 transverse 30 N at the prop plane: moment on the screw group about y or z; plus hover thrust share
M_s2 = F_STRIKE * LEV
Ps2_y = M_s2 / (4 * PAT_Z / 2)                         # moment about the arm (y) axis: screws at z +-8 take +-P
Ps2_z = M_s2 / (4 * PAT_Y / 2)                         # moment about z: screws at y +-9.5
Ps2 = Ps2_y + T_HOV / 4
mrow("Strike S2 transverse 30 N (35 mm above base face): worst screw tension, + hover thrust share", f"{M_s2*1e3:.0f} N mm -> {Ps2:.1f} N/screw", Ps2 * KP / A_HEAD / 1e6, PETG_BEAR / 1e6, "head pull-through; a blade force along z loads the 16 mm axis")
mrow("Strike S2: M2.5 screw tension", f"{Ps2:.1f} N/screw", Ps2 * KF / A_S25 / 1e6, STEEL_SIG / 1e6, "")
mrow("Strike S2: thread strip, 2.0 mm min engagement", f"{Ps2:.1f} N/screw", Ps2 * KF / (math.pi * 2.2e-3 * ENG_MIN * 0.5) / 1e6, AL_THREAD_TAU / 1e6, "")
M_pl2 = 2 * Ps2 * (PAT_Y / 2 - SLV_Y1)
mrow("Strike S2: plate cantilever bending beyond the sleeve end", f"{M_pl2*1e3:.0f} N mm", M_pl2 * KP / Z_pl / 1e6, PETG_ILAY / 1e6, "")
# S3 tangential: shaft torque F*r on screws (shear, 2 of 4), torsion on the sleeve (F x lever to arm axis), arm tip moment F r
Q_s = F_STRIKE * R_B
V_s3 = Q_s / (4 * R_PAT) * 2.0
mrow("Strike S3 blade stop: hole bearing, torque 2.4 N m on 2 of 4 screws", f"{V_s3:.0f} N/screw", V_s3 * KP / (HOLE_D * PLATE_T) / 1e6, PETG_BEAR / 1e6, "")
mrow("Strike S3: M2.5 screw shear (shank, 2 screws), single shear", f"{V_s3:.0f} N/screw", V_s3 * KF / A_S25 / 1e6, 0.6 * STEEL_SIG / 1e6, "friction of the clamped base would share this load")
tau_tors = F_STRIKE * X_PROP * KP / (2 * math.pi * (ARM_OD / 2) ** 2 * EMBED)
tau_pair = (Q_s / 0.025) * KP / (0.5 * math.pi * ARM_OD * EMBED)
mrow("Strike S2/S3: cup-to-arm bond, torsion 30 N x 47 mm + torque couple 2.4 N m / 25 mm", f"{F_STRIKE*X_PROP:.2f} N m + {Q_s:.1f} N m", math.hypot(tau_tors, tau_pair) / 1e6, BOND_TAU / 1e6, "vector sum of the two shear flows (EST convention of iter2_margins s1)")
mrow("Strike S3: sleeve wall hoop at the mouth (couple 96 N, 6 mm patch)", f"{Q_s/0.025:.0f} N", 2 * (Q_s / 0.025) * KP / (math.pi * 0.006) / (SLV_RO - SLV_RI) / 1e6, PETG_BEAR / 1e6, "")
mrow("Strike S2: plate-to-sleeve junction, in-plane shear into the crest (20 x %.0f mm)" % (WEB_T * 1e3), "30 N", F_STRIKE * KP / (0.020 * WEB_T) / 1e6, PETG_ILAY / 1e6, "")
# arm root with blade offset
M_arm_S3 = F_STRIKE * (L_ARM + R_B)
mrow("Arm 12x10 root bending, strike force at the blade (lever 0.246 + 0.080 m)", f"{M_arm_S3:.1f} N m", M_arm_S3 * KF / Z_ARM / 1e6, CF_SIG / 1e6, "iter2_margins.md uses 7.4 N m (no blade offset): +1.41; this is the worse case")
M_arm_thr = T_CAP * L_ARM
mrow("Arm 12x10 root bending, thrust at the cap, combined with torque (vector)", f"{math.hypot(M_arm_thr, Q):.2f} N m", math.hypot(M_arm_thr, Q) * KF / Z_ARM / 1e6, CF_SIG / 1e6, "iter2_margins.md 2.17 N m; adds the torque out of plane")

# ---------------------------------------------------------------- (c) tip-over / hard landing on the arm tips
# Tip-over from the balance point about the narrow-axis foot line (landing_a.py: feet z +-0.18, CG 0.275 above feet, tip angle 33.2 deg)
h_cg, z_cg = 0.275, 0.18
h_peak = math.hypot(h_cg, z_cg)
u_p, v_p = 0.42, 0.156 + 0.114 - z_cg                  # prop blade tip above ground and outboard of the pivot (arm station z 0.156 + R 0.114)
th_hit = math.degrees(math.atan2(u_p, v_p))
h_hit = h_cg * math.cos(math.radians(th_hit)) + z_cg * math.sin(math.radians(th_hit))
E_fall = 1.46 * G * (h_peak - h_hit)
k_arm = 3 * EI_KD / L_ARM ** 3
d_arm = math.sqrt(2 * (E_fall / 2) / k_arm)            # two arm tips share the energy
F_arm = k_arm * d_arm
M_ti = F_arm * L_ARM
mrow("Tip-over damage case, rigid ground, no prop crush: arm bending (2 tips share 1.36 J; NO ultimate factor)", f"F {F_arm:.0f} N, {M_ti:.1f} N m", M_ti / Z_ARM / 1e6, CF_SIG / 1e6, "blades (hit at %.0f deg of tip) are the fuse, so this is an upper bound; CG drop %.0f mm, E %.2f J" % (th_hit, (h_peak - h_hit) * 1e3, E_fall))
Pti = F_arm * LEV / (4 * PAT_Z / 2)
mrow("Tip-over case: cup head pull-through at that force (no factor)", f"{Pti:.0f} N/screw", Pti / A_HEAD / 1e6, PETG_BEAR / 1e6, "same upper bound")

# ---------------------------------------------------------------- (d) fatigue
F_SORTIE_S = 5 * 60                                    # EST flight seconds per sortie (BATT_LOW 4.78 min max, MISSION.md)
N_SORTIES = 25 * 2                                     # 22 mornings (SCHEDULE-A.md / H2 s6) + F04 redo 3 = 25 mornings x 2 sorties
T_BENCH = 60 * 60                                      # EST thrust stand / tether / bench runs, s
T_LIFE = 2.0 * (N_SORTIES * F_SORTIE_S + T_BENCH)      # x2 life factor
HZ_1P = 0.65 * 6272 / 60 + 0.35 * 7450 / 60            # hover / cruise time split EST
N_1P = T_LIFE * HZ_1P
N_2P = 2 * N_1P
N_CAPCYC = 20 * N_SORTIES * 2                          # 20 pulses to the cap per sortie EST, x2
N_CTRL = 2 * N_SORTIES * 180 * 10                       # control activity 10 Hz over 180 s hover per sortie, x2
KD_CF, KD_PETG, KD_BOND = 0.40, 0.20, 0.30             # fatigue endurance knock-down on the STATIC allowable, 1e7 cycles: EST (see s5)
DAF = 1 / (1 - (1 / 1.2) ** 2)                         # dynamic factor at the iter3 20 % separation rule, undamped: 3.3
F1_c = U_UNB * (7600 * 2 * math.pi / 60) ** 2
M_1P = F1_c * L_ARM * DAF
M_ctl = 0.25 * T_HOV * L_ARM                           # +-25 % thrust modulation by the rate loop, EST
M_amp = M_1P + M_ctl
sig_a = M_amp / Z_ARM
sig_m = T_HOV * L_ARM / Z_ARM
mrow("FATIGUE arm tube bending amplitude: 1P %.2f N m x DAF 3.3 + control +-25%% thrust (limit, no factor)" % M_1P, f"M_a {M_amp:.2f} N m, mean {sig_m/1e6:.0f} MPa, N1P {N_1P:.1e}", sig_a / 1e6, KD_CF * CF_SIG / 1e6, "endurance = 0.40 x 350 MPa EST")
# hub socket bond fatigue (pair = M/0.025)
tau_hub_a = (M_amp / 0.025) / (0.5 * math.pi * ARM_OD * EMBED)
mrow("FATIGUE hub-socket bond, amplitude couple M_a/25 mm", f"{M_amp/0.025:.0f} N", tau_hub_a / 1e6, KD_BOND * BOND_TAU / 1e6, "endurance 0.30 x 2.0 MPa EST")
tau_hub_cap = (T_CAP * L_ARM / 0.025) / (0.5 * math.pi * ARM_OD * EMBED)
mrow("FATIGUE hub-socket bond, 0 -> cap thrust cycles (%.0f cycles), range" % N_CAPCYC, f"{T_CAP*L_ARM/0.025:.0f} N", tau_hub_cap / 1e6, 0.55 * BOND_TAU / 1e6, "allowable 0.55 x static at ~1e3-1e4 cycles EST")
N_wall = 2 * (M_amp / 0.025) / (math.pi * 0.006)       # N/mm... in N/m, 6 mm patch
sig_wall_a = N_wall / 0.002
mrow("FATIGUE hub arm-socket wall (2.0 mm, D-196), hoop amplitude, 6 mm patch", f"{M_amp/0.025:.0f} N", sig_wall_a / 1e6, KD_PETG * PETG_BEAR / 1e6, "endurance 0.20 x 20 MPa = 4 MPa EST")
N_wall_cap = 2 * (T_CAP * L_ARM / 0.025) / (math.pi * 0.006) / 0.002
mrow("FATIGUE hub arm-socket wall, 0 -> cap thrust cycles, 6 mm patch", f"{T_CAP*L_ARM/0.025:.0f} N", N_wall_cap / 1e6, 0.5 * PETG_BEAR / 1e6, "0.5 x static at ~1e3-1e4 cycles EST; the l = 12 mm patch halves it")
# cup
tau_cup_a = (F1_c * DAF * 0.0 + M_ctl / 0.025 * 0 + (F1_c * DAF * LEV) / 0.025) / (0.5 * math.pi * ARM_OD * EMBED) + 0.25 * Q / 0.025 / (0.5 * math.pi * ARM_OD * EMBED)
mrow("FATIGUE cup-to-arm bond, 1P couple + torque ripple", f"1P {F1_c*DAF:.2f} N at 47 mm", tau_cup_a / 1e6, KD_BOND * BOND_TAU / 1e6, "")
P_scr_a = (F1_c * DAF * LEV / (4 * PAT_Z / 2)) + 0.25 * T_HOV / 4 * 2
mrow("FATIGUE cup head pull-through (PETG), amplitude per screw", f"{P_scr_a:.1f} N", P_scr_a / A_HEAD / 1e6, KD_PETG * PETG_BEAR / 1e6, "")
mrow("FATIGUE cup plate cantilever bending, amplitude", f"{2*P_scr_a*0.006*1e3:.0f} N mm", 2 * P_scr_a * (PAT_Y / 2 - SLV_Y1) / Z_pl / 1e6, KD_PETG * PETG_ILAY / 1e6, "interlayer endurance 0.20 x 9.5 MPa")
Pm = T_CAP / 4 * 2
mrow("FATIGUE M2.5 screw, amplitude (joint stiffness share 0.25 of the load; preload not published)", f"{P_scr_a:.1f} N", 0.25 * P_scr_a / A_S25 / 1e6, 0.25 * 0.5 * STEEL_SIG / 1e6, "loosening, not fatigue, is the risk: threadlocker + bench retorque")

# ---------------------------------------------------------------- (e) tip deflection
def tip(T_, EI_, L=L_ARM):
    d = T_ * L ** 3 / (3 * EI_); th = T_ * L ** 2 / (2 * EI_); return d, th
defl = {}
for name, T_ in (("hover", T_HOV), ("cap", T_CAP), ("uncapped", T_UNC)):
    for en, EI_ in (("nom", EI_NOM), ("kd", EI_KD)):
        defl[(name, en)] = tip(T_, EI_)
th_Q = Q_CAP * L_ARM / EI_KD
d_cap, th_cap = defl[("cap", "kd")]
row("Arm tip deflection at the cap (kd E 61 GPa, cantilever, rigid hub)", f"{T_CAP:.1f} N", f"{d_cap*1e3:.2f} mm", "- (info)", float("nan"), "nom E 70: %.2f mm" % (defl[("cap", "nom")][0] * 1e3))
row("Thrust-line tilt at the cap: arm slope + torque slope (kd), toward the hub", f"{T_CAP:.1f} N + {Q_CAP*1e3:.0f} N mm", f"{math.degrees(th_cap):.2f} + {math.degrees(th_Q):.2f} deg", "- (no limit in the repo; info)", float("nan"), "lateral thrust %.3f N per motor (0.8 %% of thrust), same sense on the 4 arms (toward the hub): no net force, a symmetric trim of the 17 deg cant" % (T_CAP * math.sin(th_cap)))
row("Same at hover thrust", f"{T_HOV:.2f} N", f"{defl[('hover','kd')][0]*1e3:.2f} mm, {math.degrees(defl[('hover','kd')][1]):.2f} deg", "-", float("nan"), "SITL cant 17 deg: the hover tilt is a trim shift of the lever arm, not a controls problem")

# ---------------------------------------------------------------- (f) tap-test model
m_tip = 0.0883                                          # landing_a.py ITEMS: 88.26 g per arm station (motor 65 + prop + cup + adapter)
m_arm = math.pi / 4 * (ARM_OD ** 2 - ARM_ID ** 2) * L_ARM * 1600
def f_cant(EI_):
    k = 3 * EI_ / L_ARM ** 3
    return math.sqrt(k / (m_tip + 0.2357 * m_arm)) / (2 * math.pi)
f_nom, f_kd = f_cant(EI_NOM), f_cant(EI_KD)

# ---------------------------------------------------------------- geometric sanity: screw heads vs the sleeve wall (CAD read-only)
def head_overlap():
    n_in = n_tot = 0
    import itertools
    for sy in (1, -1):
        for sz in (1, -1):
            cy, cz = sy * PAT_Y / 2, sz * PAT_Z / 2
            for i in range(40):
                for j in range(40):
                    dy = (i / 39 - 0.5) * HEAD_D; dz = (j / 39 - 0.5) * HEAD_D
                    if dy * dy + dz * dz > (HEAD_D / 2) ** 2:
                        continue
                    for k in range(6):
                        x = -0.007 + k / 5 * HEAD_K          # head x range -7 .. -4.5 mm (rear of plate)
                        y, z = cy + dy, cz + dz
                        n_tot += 1
                        r = math.hypot(x, z)
                        if SLV_Y0 <= y <= SLV_Y1 and SLV_RI <= r <= SLV_RO_POCKET:
                            n_in += 1
    return n_in / n_tot
ov = head_overlap()
row("CAD observation: screw heads vs sleeve wall (head envelope x -7..-4.5 mm, 4.5 mm dia) ", "geometry", f"{ov*100:.0f} % of head volume inside the sleeve wall", "0 %", float("nan"), "heads of the two y = -9.5 screws lie in the printed sleeve; see ARMS.md")

# ---------------------------------------------------------------- output
P("## 1. Table")
P("| Item | Load | Stress / value | Allowable | MS | Result |")
P("|---|---|---|---|---|---|")
worst = {}
for item, load, val, al, m, note in ROWS:
    if m != m:
        res = "INFO" if "CAD observation" not in item else "FLAG"
        P(f"| {item} | {load} | {val} | {al} | | {res}{(' (' + note + ')') if note else ''} |")
    else:
        P(f"| {item} | {load} | {val} | {al} | {m:+.2f} | {rate(m)}{(' (' + note + ')') if note else ''} |")
    if m == m:
        worst[item] = m
P("")
P("## 2. Counts and fatigue basis")
P(f"- Sorties: 22 flight mornings (H2 plan s6; SCHEDULE-A.md) + 3 for the F04 redo = 25 mornings x 2 sorties = {N_SORTIES}; {F_SORTIE_S/60:.0f} min flown per sortie (EST, BATT_LOW budget 4.78 min, MISSION.md s4); thrust stand and tether {T_BENCH/60:.0f} min (EST). Life = 2 x ({N_SORTIES*F_SORTIE_S/3600:.1f} h + {T_BENCH/3600:.1f} h) = {T_LIFE/3600:.1f} h.")
P(f"- 1P {HZ_1P:.0f} Hz mean: {N_1P:.1e} cycles; 2P {N_2P:.1e}; 0 -> cap thrust pulses {N_CAPCYC} (EST 20 per sortie); control-loop thrust cycles {N_CTRL:.1e} (10 Hz over 180 s hover, EST).")
P(f"- Dynamic factor {DAF:.1f}: iter3_run.md separates strongly coupled modes by 1.2 from 1P/2P (84-304 Hz excluded); the 3.3 is the undamped response at that edge, so conservative for the arm modes at 34-46 Hz which sit BELOW 1P (isolation, factor < 1).")
P("- Endurance knock-downs (EST; see s5 sources): CFRP 0.40 of the static allowable, printed PETG 0.20, epoxy bond 0.30, all at 1e7 cycles with the limit load (no 1.5 or 1.15), and 0.5-0.55 at 1e3-1e4 cycles.")
P("")
P("## 3. Arm tip deflection and thrust line")
P("| Case | EI (N m2) | tip deflection (mm) | slope (deg) |")
P("|---|---|---|---|")
for (name, en), (d, th) in defl.items():
    P(f"| {name} {({'hover': T_HOV, 'cap': T_CAP, 'uncapped': T_UNC}[name]):.2f} N, {en} | {EI_NOM if en == 'nom' else EI_KD:.1f} | {d*1e3:.2f} | {math.degrees(th):.2f} |")
P(f"\nSlope under the cap thrust rotates the shaft toward the hub (the arm tip drops in the thrust direction, so its tangent tilts inward): thrust line tilt {math.degrees(th_cap):.2f} deg + {math.degrees(th_Q):.2f} deg from the torque slope = {math.degrees(th_cap+th_Q):.2f} deg (kd). This is rigid-hub, cantilever: the iter3 FE (hub and bridge compliance included) gives the arm modes. Printed hub socket and bond compliance add rotation: EST +0.1-0.3 deg, measured by the tap test below.")
P("")
P("## 4. Tap-test thresholds (bench)")
P(f"- Arm cantilevered in the finished cage, hammer at the motor, accelerometer or phone audio FFT: ideal rigid-hub first mode {f_nom:.0f} Hz (E 70) / {f_kd:.0f} Hz (E 61), tip mass {m_tip*1e3:.0f} g (landing_a.py item) + 0.2357 x arm {m_arm*1e3:.1f} g. The iter3 FE arm-dominant modes with hub and bridge compliance: kd 35.5-43.6, nom 38.0-46.0, hi 33.8-45.9 Hz (iter3_run.md).")
P("- Accept 32-50 Hz per arm (FE envelope, rounded). Below 32 Hz: socket bond or hub wall soft, stop. Above 50 Hz: the arm is stiffer than the FE hi corner (check the tube wall). The four arms must agree within 8 % (a loose bond or a short embed shows as a low outlier). Any arm above 84 Hz or between 84 and 304 Hz is a repeat measurement before flight.")
P(f"- Static tip-deflection test: clamp the cage at the hub, hang 0.90 kg (8.8 N) at the motor axis: deflection must lie in {defl[('cap','nom')][0]*1e3:.1f}-{d_cap*1e3*1.15:.1f} mm; more than 1.6 mm means the socket or tube is soft.")
P("")
P("## 5. Fatigue sources (checked 2026-11-15)")
P("Searches found no single design value; the knock-downs above are EST, set at or below these loose references:")
P("- CFRP: notched or impact-damaged carbon/epoxy fatigue limit about 55 % of UTS at 1e6 cycles (https://www.degruyterbrill.com/document/doi/10.1515/secm-2020-0037/html and the TU Delft AS4/8552 thesis, https://repository.tudelft.nl/file/File_b5b35b1d-36fb-408f-b792-879c810979b5); 0.40 used on the already-knocked 350 MPa allowable.")
P("- Printed polymers: fatigue limits 7-25 % of static strength for ASA, PC, Nylon 12 (https://api.crossref.org/works/10.3390/polym18020302, snippet; PETG value not read; MDPI PETG S-N paper https://www.mdpi.com/2504-477X/5/3/76 not read in full); 0.20 used on the 20 MPa bearing allowable, 0.20 on the 9.5 MPa interlayer allowable.")
P("- Epoxy bond: lap-joint fatigue strength about 50 % of static at 1e6 cycles (SMC adherend study, https://www.scinapse.io/papers/3012459098 and related); 0.30 used at 1e7 on the 2.0 MPa allowable.")
open(os.path.join(T076, "arm_cup_checks_t076_r3fix.md" if R3FIX else "arm_cup_checks_t076_other.md"), "w").write("\n".join(OUT) + "\n")

# one number set for claims (printed last, read by gen_params_a.py as stored values)
if __name__ == "__main__":
    ks = sorted(worst.items(), key=lambda kv: kv[1])[:6]
    print("\nWorst six MS:")
    for k, v in ks: print(f"  {v:+.2f}  {k[:100]}")
