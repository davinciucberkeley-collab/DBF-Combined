"""C6 joints and fasteners: sizing checks for every fastened and bonded joint of K09-L. Emits claims.json.

    python -I redesign/team/C6/joints.py        then   python -I redesign/proofs/build_graph.py

Loads are C1's (claims CL-C1-*, or C1 data/envelope.json values entered as ASM-C6-* with the file as basis).
Every check is a reserve factor RF = allowable / applied at the design load; RF >= 1.0 passes (margin = RF - 1).
Design load = ultimate (1.5 x limit) x fitting factor 1.15, x printed/bonded factor 1.25 for anything printed or
bonded (C1 LOADS.md). Python 3 standard library only.
"""
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]                     # redesign/
sys.path.insert(0, str(ROOT / "proofs"))
import proofkit as pk                                                  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json",
                               "../../subsystems/landing/params.json", "params.json"])

R_SM, R_JS, R_FT = ["R-STRUCT-MARGIN"], ["R-JOINT-STACK"], ["R-FIN-TUBE-JOINT"]
ST = ["UR", "UL", "LR", "LL"]
MOTORS = [f"PRP-001-{s}" for s in ST]
MOUNTS = [f"FIN-003-{s}" for s in ST]
COLLARS = [f"FIN-008-{s}" for s in ST]
BLOCKS = ["FIN-004-R", "FIN-004-L"]
TUBES = ["FIN-002-R", "FIN-002-L"]
HALVES = ["FIN-001-RU", "FIN-001-RD", "FIN-001-LU", "FIN-001-LD"]
STRIPS = [f"FIN-011-{h}{s}" for h in ("RU", "RD", "LU", "LD") for s in ("O", "I")]
ENV = "team/C1/data/envelope.json"

# ----------------------------------------------------------------------------- assumptions (allowables, loads)
kit.assumption("ASM-C6-FOAM-KD", "Foam bond knock-down 0.5", "Design allowable of an epoxy bond into XPS or onto "
               "paper-faced foam board = 0.5 x the typical cohesive strength of the foam or of the paper-to-core "
               "interface", "cut-surface damage, dust, sun-heated foam and coupon scatter; replaced by "
               "0.5 x the mean of T-C6-XPS-PULL / T-C6-BOARD-LAP", 0.5, "-", status="UNVERIFIED")
kit.assumption("ASM-C6-PEEL", "Epoxy tension/peel on PETG or CF 1.0 MPa", "Flatwise tension allowable of a 30 min "
               "epoxy bond on abraded PETG or CF", "0.5 x the 2 MPa lap-shear allowable (ASM-C4-BOND-SHEAR): "
               "peel concentrates at the bond edge", 1.0e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-C6-HEAD-BEARING", "Printed plate under a screw head 30 MPa", "Sustained bearing stress allowed "
               "under an M3 head on printed PETG or ASA at up to 70 degC (creep-limited)",
               "about 0.5 x room-temperature compressive yield (~60 MPa); the motor base runs at 66 degC "
               "(E3 CR-E3-01); T-C6-HEAD-CREEP", 30e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-C6-NUT-FACTOR", "Nut factor K 0.2", "T = K F d for M3 A2 screws, dry or with Loctite 243",
               "VDI 2230 / Shigley typical 0.15-0.30", 0.2, "-", status="PROPOSED")
kit.assumption("ASM-C6-AL-SHEAR", "Motor base thread shear 160 MPa", "Shear yield of the motor base aluminium "
               "(6061-T6 assumed: 0.58 x 276 MPa)", "maker does not publish the alloy", 160e6, "Pa",
               status="UNVERIFIED")
kit.assumption("ASM-C6-INSERT-PULL", "Heat-set insert pull-out 300 N", "Design pull-out of one M3 x 5.7 mm brass "
               "heat-set insert in PETG", "~0.4 x the 700-1 000 N measured in published PLA/PETG tests "
               "(CNC Kitchen insert tests); T-C6-INSERT", 300.0, "N", status="UNVERIFIED")
kit.assumption("ASM-C6-PIN-TAU", "CF rod transverse shear 50 MPa", "Transverse shear allowable of a 2 mm pultruded "
               "CF rod", "typical pultruded rod 60-90 MPa interlaminar/transverse, knocked down", 50e6, "Pa",
               status="UNVERIFIED")
kit.assumption("ASM-C6-SNAP-STRAIN", "Snap-hook strain 2 %", "Maximum bending strain of a printed PETG snap hook "
               "that is flexed at every foot-insert swap", "PETG yield strain ~4-5 %; half for repeated use and "
               "layer lines", 0.02, "-", status="PROPOSED")
kit.assumption("ASM-C6-E1-TORQUE", "Motor screw torque in PRP-005: 0.5 N m", "Torque currently written in "
               "propulsion PRP-005 and fins E-FIN-61..64", "subsystems/propulsion/parts.csv, "
               "subsystems/fins/interfaces.json", 0.5, "N m", status="PROPOSED")
kit.assumption("ASM-C6-MOTOR-M-ULT", "Motor-to-mount moment 0.848 N m (ult)", "Ultimate moment at the motor base",
               f"{ENV}#joints.J-MOTOR.M_res_Nm.ultimate (T3 flare, lower pair)", 0.848, "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MZ-ULT", "Fin group torsion about the tube 7.26 N m (ult)", "Ultimate Mz of the fin "
               "group at the wing", f"{ENV}#joints.J-FIN.Mz_Nm.ultimate (L4 corner)", 7.262, "N m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MY-ULT", "Fin group torsion about the spar 6.72 N m (ult)", "Ultimate My of the fin "
               "group at the wing", f"{ENV}#joints.J-FIN.My_Nm.ultimate (L4 corner)", 6.7165, "N m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-FINHALF-MZ-ULT", "Half-fin torsion about the tube 7.94 N m (ult)", "Ultimate Mz of one "
               "half-fin + tube at the wing plane", f"{ENV}#joints.J-FINHALF.Mz_Nm.ultimate (L4 corner)", 7.941,
               "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-C4-COLLAR-T", "C4 collar torsion 9.3 N m (limit)", "Tube torsion at the block face in L4 "
               "that C4 says the station collar passes into the tube", "team/C4/BOOM-STRUCTURES.md, strength "
               "section; differs from C1's half-fin Mz 5.29 N m limit (CR-C6-03)", 9.3, "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-STRIP-L", "Edge strip length 264 mm", "Length of one edge strip from the collar to the foot",
               "team/C4/BOOM-STRUCTURES.md mass table (8 strips 10 x 1 x 264 mm)", 0.264, "m", status="PROPOSED")
kit.assumption("ASM-C6-BRACE-F", "Brace design force 142 N", "Brace axial force at design (ultimate x 1.15), G2",
               "team/C4 CALC-C4-STATIC-1L strut_comp_design_n (C4 model, 10 x 2 brace); C4 re-runs with D3's "
               "10 x 3 brace (CR-D3-10)", 142.0, "N", status="UNVERIFIED")
kit.assumption("ASM-C6-POD-M-ULT", "Pod-to-wing moment 3.51 N m (ult)", "Ultimate moment at the pod bond",
               f"{ENV}#joints.J-POD.M_res_Nm.ultimate (L1)", 3.506, "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-POD-AREA", "Pod bond area 10 014 mm2", "Bonded footprint of the pod shell on the core",
               "subsystems/pod/interfaces.json E-POD-01 bond.area_mm2", 0.010014, "m2", status="PROPOSED")
kit.assumption("ASM-C6-AVN-CRASH", "Avionics crash load 9.4 N", "Ultimate crash load of the avionics group, any axis",
               f"{ENV}#crash_ultimate.avionics_N_any_axis (75 g x 12.75 g)", 9.375, "N", status="UNVERIFIED")
kit.assumption("ASM-C6-B2-HINGE-V", "B2 hinge moment speed 19.5 m/s", "Speed at which CL-B2-HINGE-MOMENT was "
               "computed", "team/C1/CHANGE-REQUESTS.md CR-C1-15", 19.5, "m/s", status="PROPOSED")
kit.assumption("ASM-C6-HORN-ARM", "Horn arm 12 mm", "Control-horn hole radius used for the pushrod force",
               "team/B2/WING-AERO.md (pushrod force, 12 mm horn arm)", 0.012, "m", status="PROPOSED")


# ----------------------------------------------------------------------------- fastened joints
@kit.calc("CALC-C6-MOTOR-SCREW", title="Motor to mount: 4 x M3x8 into the motor base",
          inputs={"T": "P:joints.torque.motor_screw_nm", "T_e1": "ASM-C6-E1-TORQUE", "K": "ASM-C6-NUT-FACTOR",
                  "d": "P:joints.m3_d_m", "dh": "P:fin_detail.mount.head_d_m",
                  "dhole": "P:fin_detail.mount.screw_hole_d_m", "s_allow": "ASM-C6-HEAD-BEARING",
                  "F_ult": "CL-C1-MOTOR-F-ULT", "M_ult": "ASM-C6-MOTOR-M-ULT", "ff": "ASM-C1-FITTING-FACTOR",
                  "pat": "P:fin_detail.mount.bolt_pattern_m", "Le": "CL-D3-SCREW-ENGAGE",
                  "tau_al": "ASM-C6-AL-SHEAR"},
          equation="P = T/(K d); head bearing = P / (pi/4 (dh^2 - dhole^2)); screw tension F_t = ff (F/4 + M/s_min); "
                   "separation RF = P / F_t; thread strip = 0.5 pi d Le tau_Al")
def motor_screw(T, T_e1, K, d, dh, dhole, s_allow, F_ult, M_ult, ff, pat, Le, tau_al):
    a_head = math.pi / 4 * (dh ** 2 - dhole ** 2)
    P = T / (K * d)
    P_e1 = T_e1 / (K * d)
    F_t = ff * (F_ult / 4 + M_ult / min(pat))
    strip = 0.5 * math.pi * d * Le * tau_al
    return {"preload_n": P, "head_mpa": P / a_head / 1e6, "rf_head": s_allow / (P / a_head),
            "head_mpa_e1": P_e1 / a_head / 1e6, "rf_head_e1": s_allow / (P_e1 / a_head),
            "tension_n": F_t, "rf_sep": P / F_t, "strip_n": strip, "rf_strip": strip / F_t}


@kit.calc("CALC-C6-PINCH", title="Motor-mount slit collar: M3x16 + nyloc, rocking under the prop-nut torque",
          inputs={"L": "P:joints.pinch_screw_len_m", "ear": "P:fin_detail.mount.ear_t_m",
                  "slit": "P:fin_detail.mount.slit_m", "wt": "P:joints.washer_t_m", "nw": "P:joints.pinch_washers",
                  "nh": "P:joints.nyloc_h_m", "p": "P:joints.m3_pitch_m",
                  "nthr": "P:joints.nyloc_protrusion_min_threads", "Ts": "P:fin_detail.mount.slip_torque_nm",
                  "mu": "P:fin_detail.mount.mu_petg_cf", "od": "P:fins.tube.od_m", "id": "P:fins.tube.id_m",
                  "K": "ASM-C6-NUT-FACTOR", "d": "P:joints.m3_d_m", "Tprop": "ASM-C1-PROP-NUT-TORQUE",
                  "sf": "P:requirements.safety_factor_ult", "ff": "ASM-C1-FITTING-FACTOR",
                  "pf": "ASM-C1-PRINTED-FACTOR", "grip": "P:fin_detail.mount.grip_m",
                  "s_b": "ASM-C4-PETG-BEARING", "s_cf": "ASM-C4-CF-SIGMA"},
          equation="protrusion = L - (2 ear + slit + nw wt); needed nyloc h + n p; clamp N = Ts/(mu pi r), "
                   "bolt torque = K N d; rocking bearing p = 6 M/(od grip^2), M = Tprop sf ff pf; "
                   "tube hoop = p r / t")
def pinch(L, ear, slit, wt, nw, nh, p, nthr, Ts, mu, od, id, K, d, Tprop, sf, ff, pf, grip, s_b, s_cf):
    grip_stack = 2 * ear + slit + nw * wt
    prot = L - grip_stack
    need = nh + nthr * p
    r = od / 2
    N = Ts / (mu * math.pi * r)
    M = Tprop * sf * ff * pf
    pb = 6 * M / (od * grip ** 2)
    hoop = pb * r / ((od - id) / 2)
    return {"grip_stack_m": grip_stack, "protrusion_m": prot, "protrusion_need_m": need, "rf_engage": prot / need,
            "clamp_n": N, "bolt_torque_nm": K * N * d, "M_design_nm": M, "bearing_mpa": pb / 1e6,
            "rf_rock": s_b / pb, "hoop_mpa": hoop / 1e6, "rf_hoop": s_cf / hoop}


@kit.calc("CALC-C6-INSERT", title="FC on M3 heat-set inserts: engagement and pull-out",
          inputs={"L": "P:joints.fc_screw_len_m", "stack": "P:joints.fc_stack_m", "d": "P:joints.m3_d_m",
                  "kmin": "P:joints.insert_engage_min_d", "Li": "P:joints.insert_len_m",
                  "F": "ASM-C6-AVN-CRASH", "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "cap": "ASM-C6-INSERT-PULL"},
          equation="engagement = L - stack >= kmin d; blind hole >= engagement + 0.5 mm; "
                   "RF = pull-out / (F ff pf), whole avionics crash load on one insert")
def insert(L, stack, d, kmin, Li, F, ff, pf, cap):
    e = L - stack
    return {"engage_m": e, "rf_engage": e / (kmin * d), "hole_depth_m": max(e, Li) + 0.0005,
            "rf_pull": cap / (F * ff * pf)}


# ----------------------------------------------------------------------------- bonded joints, fins
@kit.calc("CALC-C6-TUBE-BONDS", title="Tube-in-block, block-on-spar and station-collar bonds in torsion",
          inputs={"od": "P:fins.tube.od_m", "core": "ASM-C4-CORE-T-TUBE", "boss": "P:fin_detail.boss.height_m",
                  "Ls": "P:fin_detail.block.width_m", "Lc": "P:fin_detail.station_collar.height_m",
                  "Tz": "ASM-C6-FIN-MZ-ULT", "Ty": "ASM-C6-FIN-MY-ULT", "Th": "ASM-C6-FINHALF-MZ-ULT",
                  "Tc4": "ASM-C6-C4-COLLAR-T", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "tau": "ASM-C4-BOND-SHEAR"},
          equation="tau = T / (2 pi r^2 L), T = T_ult ff pf; spar OD = tube OD (22 mm); "
                   "tube bore L = core + 2 bosses; L_req = T / (2 pi r^2 tau)")
def tube_bonds(od, core, boss, Ls, Lc, Tz, Ty, Th, Tc4, sf, ff, pf, tau):
    r = od / 2
    k = 2 * math.pi * r ** 2
    Lb = core + 2 * boss
    T_tb, T_bs, T_c = Tz * ff * pf, Ty * ff * pf, Th * ff * pf
    T_c4 = Tc4 * sf * ff * pf
    return {"L_bore_m": Lb, "area_bore_mm2": 2 * math.pi * r * Lb * 1e6, "rf_tube_block": tau * k * Lb / T_tb,
            "area_spar_mm2": 2 * math.pi * r * Ls * 1e6, "rf_block_spar": tau * k * Ls / T_bs,
            "area_collar_mm2": 2 * math.pi * r * Lc * 1e6, "rf_collar": tau * k * Lc / T_c,
            "rf_collar_c4": tau * k * Lc / T_c4, "L_collar_req_c4_m": T_c4 / (k * tau)}


@kit.calc("CALC-C6-STRIP", title="Edge-strip anchorage in the station collar and strip-to-board shear flow",
          inputs={"s_cf": "ASM-C4-CF-SIGMA", "ms": "CL-C4-MS-EDGE", "w": "P:fin_detail.edge_strip.w_m",
                  "t": "P:fin_detail.edge_strip.t_m", "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "tail": "P:fin_detail.station_collar.tail_m", "n_now": "P:joints.strip_bonded_faces_now",
                  "n_p": "P:joints.strip_bonded_faces_prop", "L_p": "P:joints.strip_embed_prop_m",
                  "tau": "ASM-C4-BOND-SHEAR", "Ls": "ASM-C6-STRIP-L", "kd": "ASM-C6-FOAM-KD",
                  "tau_b": "ASM-D5-BOND-TAU", "tb": "P:fins.board_t_m", "dp": "P:joints.pin_d_m",
                  "pp": "P:joints.pin_pitch_m", "tau_pin": "ASM-C6-PIN-TAU"},
          equation="F = sigma_ult w t ff pf, sigma_ult = sigma_allow/(1+MS_edge); anchor tau = F/(n w L); "
                   "L_req = F/(2 w tau); shear flow q = F/L_strip onto the paper face, tau = q/w vs kd tau_board; "
                   "pins: P = q pitch, shear P/(pi d^2/4), bending 32 P (tb+t)/2 / (pi d^3)")
def strip(s_cf, ms, w, t, ff, pf, tail, n_now, n_p, L_p, tau, Ls, kd, tau_b, tb, dp, pp, tau_pin):
    s_ult = s_cf / (1 + ms)
    F = s_ult * w * t * ff * pf
    q = F / Ls
    P = q * pp
    rf_sh = tau_pin * math.pi * dp ** 2 / 4 / P
    sig = 32 * P * (tb + t) / 2 / (math.pi * dp ** 3)
    return {"F_design_n": F, "rf_anchor_now": tau * n_now * w * tail / F, "L_req_m": F / (2 * w * tau),
            "rf_anchor_prop": tau * n_p * w * L_p / F, "q_npm": q, "tau_face_mpa": q / w / 1e6,
            "rf_face": kd * tau_b / (q / w), "pin_load_n": P, "rf_pin_shear": rf_sh, "rf_pin_bend": s_cf / sig,
            "rf_pin": min(rf_sh, s_cf / sig), "pins_per_strip_pair": math.ceil(Ls / pp)}


@kit.calc("CALC-C6-BRACE", title="Brace ends in their slots and the anchor on the spar",
          inputs={"F": "ASM-C6-BRACE-F", "pf": "ASM-C1-PRINTED-FACTOR", "w": "P:fin_detail.brace.w_m",
                  "t": "P:fin_detail.brace.t_m", "e": "P:fin_detail.brace.engage_m",
                  "ax": "P:fin_detail.anchor.len_x_m", "ay": "P:fin_detail.anchor.len_y_m",
                  "tau": "ASM-C4-BOND-SHEAR", "peel": "ASM-C6-PEEL"},
          equation="end bond tau = F pf / (2 (w+t) e); anchor pull-off sigma = F pf / (ax ay), whole brace force normal")
def brace(F, pf, w, t, e, ax, ay, tau, peel):
    Fd = F * pf
    return {"F_design_n": Fd, "rf_end": tau * 2 * (w + t) * e / Fd, "rf_anchor": peel * ax * ay / Fd}


# ----------------------------------------------------------------------------- bonds into foam and foam board
@kit.calc("CALC-C6-FOAM-BONDS", title="Bonds into XPS and onto paper-faced board at the C6 allowables",
          inputs={"kd": "ASM-C6-FOAM-KD", "sf_d5": "CL-D5-BOND-SF", "rf_d3": "CL-D3-ROOT-FILLET-RF",
                  "F": "CL-C1-POD-F-ULT", "M": "ASM-C6-POD-M-ULT", "A": "ASM-C6-POD-AREA", "b": "ASM-D2-POD-WIDTH",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "s_xps": "ASM-D3-XPS-TENSILE"},
          equation="foot shoe RF = SF_D5 kd (D5 used the undiscounted 0.20 MPa); fin root RF = RF_D3 kd; "
                   "pod: sigma = F ff pf / A + 6 M ff pf / (b Leff^2), Leff = A/b, vs kd sigma_XPS")
def foam_bonds(kd, sf_d5, rf_d3, F, M, A, b, ff, pf, s_xps):
    Leff = A / b
    sig = F * ff * pf / A + 6 * M * ff * pf / (b * Leff ** 2)
    return {"rf_foot": sf_d5 * kd, "rf_root": rf_d3 * kd, "allow_xps_mpa": kd * s_xps / 1e6,
            "pod_sigma_kpa": sig / 1e3, "rf_pod": kd * s_xps / sig}


@kit.calc("CALC-C6-LINKAGE", title="Servo frame and control horn: minimum bond area into XPS",
          inputs={"Mh": "CL-B2-HINGE-MOMENT", "arm": "ASM-C6-HORN-ARM", "V": "CL-C1-VD-ENV",
                  "Vb": "ASM-C6-B2-HINGE-V", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "kd": "ASM-C6-FOAM-KD",
                  "s_xps": "ASM-D3-XPS-TENSILE"},
          equation="F = Mh/arm (V_D/V_B2)^2 sf ff pf; A_min = F / (kd sigma_XPS)")
def linkage(Mh, arm, V, Vb, sf, ff, pf, kd, s_xps):
    F = Mh / arm * (V / Vb) ** 2 * sf * ff * pf
    return {"F_design_n": F, "A_min_mm2": F / (kd * s_xps) * 1e6}


@kit.calc("CALC-C6-SNAP", title="Foot piston snap hook: minimum finger length",
          inputs={"t": "P:landing.wall_t_m", "y": "P:landing.piston.hook_protrusion_m", "eps": "ASM-C6-SNAP-STRAIN"},
          equation="cantilever snap fit eps = 1.5 t y / L^2  ->  L_min = sqrt(1.5 t y / eps)")
def snap(t, y, eps):
    return math.sqrt(1.5 * t * y / eps)


# ----------------------------------------------------------------------------- claims
def rf(cid, title, calc, out, parts, how, ver=R_SM, unit="-"):
    kit.claim(cid, title, calc=calc, output=out, unit=unit, limit=(">=", 1.0), verifies=ver, parts=parts, how=how)


rf("CL-C6-MOTOR-HEAD-RF", "Motor screw head bearing on the printed plate at 0.20 N m", "CALC-C6-MOTOR-SCREW",
   "rf_head", MOUNTS, "T-C6-HEAD-CREEP: 4 screws at 0.20 N m on a printed plate, 2 h at 70 degC, witness lines "
   "unmoved and breakaway torque >= 0.15 N m")
rf("CL-C6-MOTOR-SEP-RF", "Motor screw preload / design tension (no gapping)", "CALC-C6-MOTOR-SCREW", "rf_sep",
   MOTORS + MOUNTS, "Witness line across each screw head and plate; tap test after T-H1 thrust-stand runs")
rf("CL-C6-MOTOR-STRIP-RF", "Motor-base thread strip / design tension", "CALC-C6-MOTOR-SCREW", "rf_strip", MOTORS,
   "Probe the motor hole depth on arrival (E1 T-E1-MOTOR-RM); engagement >= 3.0 mm (CL-D3-SCREW-ENGAGE)")
rf("CL-C6-PINCH-ENGAGE-RF", "Mount pinch bolt: protrusion past the grip / nyloc need", "CALC-C6-PINCH", "rf_engage",
   MOUNTS, "Build check: >= 2 threads visible past each nyloc (BUILD step for the mounts)", ver=R_JS)
kit.claim("CL-C6-PINCH-TORQUE", "Mount pinch bolt torque that gives the 2.5 N m slip (estimate)", calc="CALC-C6-PINCH",
          output="bolt_torque_nm", unit="N m", limit=("<=", "P:joints.torque.printed_max_nm"), verifies=R_JS,
          parts=MOUNTS, how="T-D3-SLIP sets the bolt by the slip force (85-100 N at the can); a torque above "
                            "0.4 N m to reach it means the collar bore is oversize: reprint")
rf("CL-C6-MOUNT-ROCK-RF", "Mount collar bearing under 3.2 N m prop-nut torque (CR-C1-11)", "CALC-C6-PINCH",
   "rf_rock", MOUNTS + TUBES, "T-C6-PROPNUT: 1.5 N m on the prop nut with the bell held, 10 cycles; collar "
   "witness line and lip cap unmoved", ver=R_SM + R_FT)
rf("CL-C6-MOUNT-HOOP-RF", "Tube wall hoop stress under the rocking collar", "CALC-C6-PINCH", "rf_hoop", TUBES,
   "Same as T-C6-PROPNUT; inspect the tube end for crazing", ver=R_SM + R_FT)
rf("CL-C6-FC-ENGAGE-RF", "FC screw engagement in the heat-set insert / 1.5 d", "CALC-C6-INSERT", "rf_engage",
   ["AVN-001", "POD-002"], "F3 measures the board + grommet stack; screw runs in by hand >= 4.5 mm", ver=R_JS)
rf("CL-C6-INSERT-PULL-RF", "Heat-set insert pull-out / avionics crash load", "CALC-C6-INSERT", "rf_pull",
   ["POD-002", "AVN-001"], "T-C6-INSERT: pull 3 inserts from a printed coupon boss")
rf("CL-C6-TUBE-BLOCK-RF", "Tube-in-block bond, fin torsion", "CALC-C6-TUBE-BONDS", "rf_tube_block",
   TUBES + BLOCKS, "T-C6-LAP-PETG (allowable) and C4 T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-BLOCK-SPAR-RF", "Block-on-spar bond, torsion about the spar", "CALC-C6-TUBE-BONDS", "rf_block_spar",
   BLOCKS + ["WNG-002"], "T-C6-LAP-PETG and T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-COLLAR-RF", "Station collar bond on the tube, half-fin torsion (C1)", "CALC-C6-TUBE-BONDS", "rf_collar",
   COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF (1.5 x L4) with the collar witness-marked", ver=R_SM + R_FT)
kit.claim("CL-C6-COLLAR-L-REQ", "Station collar bond length needed for C4's 9.3 N m tube torsion",
          calc="CALC-C6-TUBE-BONDS", output="L_collar_req_c4_m", unit="m",
          limit=("<=", "P:fin_detail.station_collar.height_m"), verifies=R_SM + R_FT, parts=COLLARS,
          how="C4 and C1 agree the collar torsion (CR-C6-03); D3 sets the collar height to at least this")
rf("CL-C6-STRIP-ANCHOR-RF", "Edge-strip end in the collar tail, as drawn (20 mm, one PETG face)", "CALC-C6-STRIP",
   "rf_anchor_now", STRIPS + COLLARS, "T-C6-STRIP-ANCHOR: pull a strip out of a printed tail coupon",
   ver=R_SM + R_FT)
kit.claim("CL-C6-STRIP-EMBED-REQ", "Edge-strip embedment needed, both faces on PETG", calc="CALC-C6-STRIP",
          output="L_req_m", unit="m", limit=("<=", "P:joints.strip_embed_prop_m"), verifies=R_SM + R_FT,
          parts=COLLARS, how="T-C6-STRIP-ANCHOR on the 40 mm two-face tail (CR-C6-01)")
rf("CL-C6-STRIP-ANCHOR-RF-PROP", "Edge-strip anchorage with the CR-C6-01 tail (40 mm, two faces)", "CALC-C6-STRIP",
   "rf_anchor_prop", STRIPS + COLLARS, "T-C6-STRIP-ANCHOR", ver=R_SM + R_FT)
rf("CL-C6-STRIP-FACE-RF", "Edge-strip shear flow onto the board paper face, no pins", "CALC-C6-STRIP", "rf_face",
   STRIPS + HALVES, "T-C6-BOARD-LAP (allowable); C4 confirms the shear flow in its FE (CR-C6-02)", ver=R_SM)
rf("CL-C6-STRIP-PIN-RF", "Through-pins tying the strip pair (CR-C6-02), weaker of shear and bending",
   "CALC-C6-STRIP", "rf_pin", STRIPS + HALVES, "T-C4-FIN-PROOF with pins fitted; no strip lift at the tip", ver=R_SM)
rf("CL-C6-BRACE-END-RF", "Brace ends bonded in the ear and anchor slots", "CALC-C6-BRACE", "rf_end",
   [f"FIN-009-{s}" for s in ST] + COLLARS + [f"FIN-010-{s}" for s in ST], "T-C6-LAP-PETG; T-C4-FIN-PROOF (G2)",
   ver=R_SM + R_FT)
rf("CL-C6-ANCHOR-PULL-RF", "Brace anchor pull-off from the spar", "CALC-C6-BRACE", "rf_anchor",
   [f"FIN-010-{s}" for s in ST] + ["WNG-002"], "T-C4-FIN-PROOF (G2 in tension on the brace)", ver=R_SM + R_FT)
rf("CL-C6-FOOT-SHOE-RF", "Foot shoe bond on the fin tip at the C6 board allowable", "CALC-C6-FOAM-BONDS",
   "rf_foot", [f"GER-001-{s}" for s in ST] + HALVES, "T-C6-BOARD-LAP; T-C1-FOOT-DROP")
rf("CL-C6-FIN-ROOT-RF", "Half-fin root fillet on XPS at the C6 foam allowable", "CALC-C6-FOAM-BONDS", "rf_root",
   HALVES + ["WNG-001"], "T-C6-XPS-PULL; D3 T-D3-ROOT side pull", ver=R_SM + R_FT)
rf("CL-C6-POD-WING-RF", "Pod shell bond on the core at the C6 foam allowable", "CALC-C6-FOAM-BONDS", "rf_pod",
   ["POD-001", "WNG-001"], "T-C6-XPS-PULL; C3 pod proof")
kit.claim("CL-C6-LINK-BOND-AREA-MIN", "Minimum bond area into XPS for a servo frame or a control horn",
          calc="CALC-C6-LINKAGE", output="A_min_mm2", unit="mm2", verifies=R_SM,
          parts=["MEC-008-L", "MEC-008-R", "MEC-004-L", "MEC-004-R"],
          how="D6 shows the bonded area of each part >= this; T-C6-XPS-PULL")
kit.claim("CL-C6-SNAP-L-MIN", "Foot snap-hook finger length for 2 % strain", calc="CALC-C6-SNAP", output="value",
          unit="m", verifies=R_JS, parts=[f"GER-002-{s}" for s in ST],
          how="D5 shows the free finger length >= this in the CAD; 20 insert swaps on one printed piston, no crack")

# ----------------------------------------------------------------------------- tests
kit.test("T-C6-LAP-PETG", "Epoxy lap shear on abraded PETG and CF",
         ["CL-C6-TUBE-BLOCK-RF", "CL-C6-BLOCK-SPAR-RF", "CL-C6-COLLAR-RF", "CL-C6-BRACE-END-RF",
          "CL-C6-STRIP-ANCHOR-RF-PROP"],
         procedure="5 single-lap coupons each: PETG-PETG and PETG-CF tube offcut, 25 x 12.5 mm overlap, 120 grit + "
                   "IPA, 30 min epoxy, 24 h cure; hang water jugs on a luggage scale to failure. Allowable = mean x 0.5; "
                   "pass >= 2.0 MPa (ASM-C4-BOND-SHEAR)")
kit.test("T-C6-BOARD-LAP", "Epoxy on paper-faced foam board", ["CL-C6-FOOT-SHOE-RF", "CL-C6-STRIP-FACE-RF"],
         procedure="5 PETG tabs 20 x 20 mm bonded on a scuffed board face, pull in shear to failure; record the "
                   "failure mode (paper peels vs epoxy). Allowable = 0.5 x mean (replaces ASM-D5-BOND-TAU x KD)")
kit.test("T-C6-XPS-PULL", "Flatwise pull of an epoxy puck on XPS", ["CL-C6-FIN-ROOT-RF", "CL-C6-POD-WING-RF",
                                                                    "CL-C6-LINK-BOND-AREA-MIN"],
         procedure="5 printed pucks 30 mm dia bonded with microballoon epoxy on hot-wire-cut F-250 offcut, pull "
                   "normal to the face; allowable = 0.5 x mean (replaces ASM-D3-XPS-TENSILE x KD)")
kit.test("T-C6-INSERT", "Heat-set insert pull-out", ["CL-C6-INSERT-PULL-RF"],
         procedure="3 inserts in a printed boss (same settings as POD-002), M3 screw + washer, pull to failure; "
                   "pass >= 300 N each")
kit.test("T-C6-HEAD-CREEP", "Motor screw creep on a hot printed plate", ["CL-C6-MOTOR-HEAD-RF"],
         procedure="Printed mount plate (final material) on an aluminium block with 4 x M3x8 at 0.20 N m, "
                   "2 h at 70 degC (oven), cool, breakaway torque >= 0.15 N m on all four")
kit.test("T-C6-STRIP-ANCHOR", "Edge-strip pull-out from the collar tail", ["CL-C6-STRIP-ANCHOR-RF",
                                                                           "CL-C6-STRIP-ANCHOR-RF-PROP"],
         procedure="Print the station collar tail alone; bond a 10 x 1 strip in it as built; pull along the strip "
                   "with water jugs; pass >= 1 350 N (design force)")
kit.test("T-C6-PROPNUT", "Prop-nut torque on a finished mount", ["CL-C6-MOUNT-ROCK-RF", "CL-C6-MOUNT-HOOP-RF"],
         procedure="Bell held by hand, prop nut to 1.5 N m and off 10 times; collar witness line and lip cap unmoved")

if __name__ == "__main__":
    kit.write()
