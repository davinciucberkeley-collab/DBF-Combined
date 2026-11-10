"""C6 joints and fasteners: sizing checks for every fastened and bonded joint of K09-L. Emits claims.json.

    python -I redesign/team/C6/joints.py        then   python -I redesign/proofs/build_graph.py

Revision C6-R2 (params A1-R3, C1 envelope re-run at R3, C4 R3 claims CL-C4-D3-*).
Loads are C1's (claims CL-C1-*, or C1 data/envelope.json values entered as ASM-C6-* with the file as basis) and C4's
fin model (CL-C4-D3-*). The 7 deg motor cant (D-27) is not in C1's cases: C6 adds its side component here.
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
HALVES = [f"FIN-001-{s}" for s in ST]                                  # D-26 ids
STRIPS = [f"FIN-011-{s}{f}" for s in ST for f in ("O", "I")]
POD = ["POD-001", "POD-002"]
ENV = "team/C1/data/envelope.json"

# ----------------------------------------------------------------------------- assumptions (allowables, loads)
kit.assumption("ASM-C6-FOAM-KD", "Foam bond knock-down 0.5", "Design allowable of an epoxy bond into XPS or onto "
               "paper-faced foam board = 0.5 x the typical cohesive strength of the foam or of the paper-to-core "
               "interface", "cut-surface damage, dust, sun-heated foam and coupon scatter; replaced by "
               "0.5 x the mean of T-C6-XPS-PULL / T-C6-BOARD-LAP", 0.5, "-", status="UNVERIFIED")
kit.assumption("ASM-C6-PEEL", "Epoxy tension/peel on PETG or CF 1.0 MPa", "Flatwise tension allowable of a 30 min "
               "epoxy bond on abraded PETG, ASA or CF", "0.5 x the 2 MPa lap-shear allowable (ASM-C4-BOND-SHEAR): "
               "peel concentrates at the bond edge (= C4's ASM-C4-PEEL-KD)", 1.0e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-C6-HEAD-BEARING", "Printed plate under a screw head 30 MPa", "Sustained bearing stress allowed "
               "under an M3 head on printed ASA (D-42) or PETG at up to 70 degC (creep-limited)",
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
kit.assumption("ASM-C6-XPS-SHEAR-TYP", "XPS shear strength 0.20 MPa (typical)", "Typical shear strength of F-250 "
               "class XPS (cohesive foam failure next to an epoxy line)", "not on the F-250 TDS; 25 psi XPS "
               "0.20-0.25 MPa, lower end taken (C3 ASM-C3-XPS-SHEAR basis); T-C6-XPS-PULL shear coupons", 0.20e6,
               "Pa", status="UNVERIFIED")
kit.assumption("ASM-C6-BOARD-FLAT-TYP", "Foam-board paper-to-core flat-wise tension 0.10 MPa (typical)",
               "Typical flat-wise tension at which the paper face of 4.8 mm paper-faced board lifts off the core",
               "estimate: paper peels before the PS core fails; half the 0.20 MPa paper-face shear (ASM-D5-BOND-TAU) "
               "because flat-wise loading peels the face; T-C6-BOARD-LAP flat-wise pulls", 0.10e6, "Pa",
               status="UNVERIFIED")
# loads from C1 data/envelope.json (R3 re-run)
kit.assumption("ASM-C6-MOTOR-M-ULT", "Motor-to-mount moment 0.849 N m (ult)", "Ultimate moment at the motor base "
               "(no cant side force; C1 does not model the cant)",
               f"{ENV}#joints.J-MOTOR.M_res_Nm.ultimate (T3 flare, lower pair)", 0.8488, "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MZ-ULT", "Fin group torsion about the tube 6.77 N m (ult)", "Ultimate Mz of the fin "
               "group at the wing", f"{ENV}#joints.J-FIN.Mz_Nm.ultimate (L4 corner)", 6.766, "N m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MY-ULT", "Fin group torsion about the spar 6.74 N m (ult)", "Ultimate My of the fin "
               "group at the wing", f"{ENV}#joints.J-FIN.My_Nm.ultimate (L4 corner)", 6.7409, "N m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-FINHALF-MZ-ULT", "Half-fin torsion about the tube 7.39 N m (ult)", "Ultimate Mz of one "
               "half-fin + tube at the wing plane", f"{ENV}#joints.J-FINHALF.Mz_Nm.ultimate (L4 corner)", 7.3909,
               "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-C4-COLLAR-T", "Collar sizing torsion 9.3 N m (limit, C4 R2)", "Tube torsion the station "
               "collar passes into the tube; the largest of C1 J-FINHALF Mz 4.93 N m limit, C4 R2 9.3 N m and C4 R3 "
               "3.46 N m (CALC-C4-D3-STATIC collar_t_lim_nm)",
               "team/C4/BOOM-STRUCTURES.md R2 strength section; CHANGE-LOG forward row CR-C6-03: C6 sizes to C4's "
               "until C1 and C4 agree", 9.3, "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-STRIP-L", "Edge strip length 264 mm", "Length of one edge strip from the collar to the foot",
               "team/C4/BOOM-STRUCTURES.md R2 mass table (8 strips 10 x 1 x 264 mm); the R3 top edge is ~277 mm, "
               "so 264 mm over-states the average shear flow by 5 %", 0.264, "m", status="PROPOSED")
kit.assumption("ASM-C6-AVN-CRASH", "Avionics crash load 10.0 N", "Ultimate crash load of an avionics item, any axis "
               "(used for the PDB on its inserts and the FC on its gel pads)",
               f"{ENV}#other.crash_ultimate.avionics_N_any_axis", 10.0, "N", status="UNVERIFIED")
kit.assumption("ASM-C6-B2-HINGE-V", "B2 hinge moment speed 19.5 m/s", "Speed at which CL-B2-HINGE-MOMENT was "
               "computed", "team/C1/CHANGE-REQUESTS.md CR-C1-15", 19.5, "m/s", status="PROPOSED")
kit.assumption("ASM-C6-HORN-ARM", "Horn arm 12 mm", "Control-horn hole radius used for the pushrod force",
               "team/B2/WING-AERO.md (pushrod force, 12 mm horn arm)", 0.012, "m", status="PROPOSED")


# ----------------------------------------------------------------------------- fastened joints
@kit.calc("CALC-C6-MOTOR-SCREW", title="Motor to mount: 4 x M3x8 into the motor base, incl. the 7 deg cant side load",
          inputs={"T": "P:joints.torque.motor_screw_nm", "T_e1": "ASM-C6-E1-TORQUE", "K": "ASM-C6-NUT-FACTOR",
                  "d": "P:joints.m3_d_m", "dh": "P:fin_detail.mount.head_d_m",
                  "dhole": "P:fin_detail.mount.screw_hole_d_m", "s_allow": "ASM-C6-HEAD-BEARING",
                  "F_ult": "CL-C1-MOTOR-F-ULT", "M_ult": "ASM-C6-MOTOR-M-ULT", "ff": "ASM-C1-FITTING-FACTOR",
                  "pat": "P:fin_detail.mount.bolt_pattern_m", "Le": "P:fin_detail.mount.plate_t_m",
                  "Ls": "P:fin_detail.mount.motor_screw_len_m", "tau_al": "ASM-C6-AL-SHEAR",
                  "Tlim": "P:requirements.thrust_limit_per_motor_n", "cant": "P:propulsion.stations.cant_deg",
                  "arm": "P:fin_detail.mount.prop_stack_m", "sf": "P:requirements.safety_factor_ult"},
          equation="P = T/(K d); head bearing = P / (pi/4 (dh^2 - dhole^2)); cant side moment M_s = T_lim sin(cant) "
                   "arm sf; screw tension F_t = ff (F/4 + (M + M_s)/s_min); separation RF = P / F_t; "
                   "thread strip = 0.5 pi d e tau_Al with e = L_screw - plate (R3 canted plate, uniform grip)")
def motor_screw(T, T_e1, K, d, dh, dhole, s_allow, F_ult, M_ult, ff, pat, Le, Ls, tau_al, Tlim, cant, arm, sf):
    a_head = math.pi / 4 * (dh ** 2 - dhole ** 2)
    P = T / (K * d)
    P_e1 = T_e1 / (K * d)
    side = Tlim * math.sin(math.radians(cant))
    M_s = side * arm * sf
    F_t = ff * (F_ult / 4 + (M_ult + M_s) / min(pat))
    e = Ls - Le
    strip = 0.5 * math.pi * d * e * tau_al
    return {"preload_n": P, "head_mpa": P / a_head / 1e6, "rf_head": s_allow / (P / a_head),
            "head_mpa_e1": P_e1 / a_head / 1e6, "rf_head_e1": s_allow / (P_e1 / a_head),
            "side_lim_n": side, "M_side_ult_nm": M_s, "tension_n": F_t, "rf_sep": P / F_t, "engage_m": e,
            "strip_n": strip, "rf_strip": strip / F_t}


@kit.calc("CALC-C6-CANT-SEAT", title="Motor screws on the 7 deg canted plate: engagement and head seating",
          inputs={"Ls": "P:fin_detail.mount.motor_screw_len_m", "tp": "P:fin_detail.mount.plate_t_m",
                  "pat": "P:fin_detail.mount.bolt_pattern_m", "cant": "P:propulsion.stations.cant_deg",
                  "ym": "P:propulsion.stations.y_m", "zm": "P:propulsion.stations.z_m",
                  "dhole": "P:fin_detail.mount.screw_hole_d_m", "d": "P:joints.m3_d_m"},
          equation="R3 (D3): whole plate canted, faces parallel to the motor face, holes drilled square to the face -> "
                   "engagement = L - plate at every hole; for record, the R2 layout (flat plate, canted 2 mm pads) "
                   "would give L - (2.5 + 2 + tan(cant) max|t . hole|) and allow a screw lean of only "
                   "atan((d_hole - d)/4.5 mm) against the cant")
def cant_seat(Ls, tp, pat, cant, ym, zm, dhole, d):
    n = math.hypot(ym, zm)
    dmax = max(abs(-zm / n * pat[0] / 2), abs(ym / n * pat[1] / 2))
    rise = math.tan(math.radians(cant)) * dmax
    return {"engage_m": Ls - tp, "engage_r2_m": Ls - (0.0045 + rise),
            "tilt_allow_r2_deg": math.degrees(math.atan((dhole - d) / 0.0045)), "rise_r2_m": rise}


@kit.calc("CALC-C6-MOUNT-SIDE", title="Mount collar on the tube under the 7 deg cant side force",
          inputs={"Tlim": "P:requirements.thrust_limit_per_motor_n", "cant": "P:propulsion.stations.cant_deg",
                  "ym": "P:propulsion.stations.y_m", "zm": "P:propulsion.stations.z_m",
                  "xt": "P:propulsion.stations.x_mount_m", "xp": "P:propulsion.stations.x_prop_plane_m",
                  "Ts": "P:fin_detail.mount.slip_torque_nm", "od": "P:fins.tube.od_m",
                  "sf": "P:requirements.safety_factor_ult", "ff": "ASM-C1-FITTING-FACTOR",
                  "pf": "ASM-C1-PRINTED-FACTOR"},
          equation="side S = T_lim sin(cant) along t = x_hat x r_hat = (0, -z/r, y/r); tube torsion Mz = S z/r "
                   "(x_tube - x_prop); axial along the tube S y/r; design x sf ff pf; slip capacity Ts (torsion), "
                   "Ts/(od/2) (axial, same friction)")
def mount_side(Tlim, cant, ym, zm, xt, xp, Ts, od, sf, ff, pf):
    S = Tlim * math.sin(math.radians(cant))
    n = math.hypot(ym, zm)
    k = sf * ff * pf
    mz = S * zm / n * (xt - xp)
    fax = S * ym / n
    return {"side_lim_n": S, "mz_lim_nm": mz, "fax_lim_n": fax, "rf_slip_torsion": Ts / (mz * k),
            "rf_slip_axial": Ts / (od / 2) / (fax * k), "side_frac": math.sin(math.radians(cant))}


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


@kit.calc("CALC-C6-INSERT", title="Bus PDB on M3 heat-set inserts: engagement and pull-out",
          inputs={"L": "P:joints.pdb_screw_len_m", "stack": "P:joints.pdb_stack_m", "d": "P:joints.m3_d_m",
                  "kmin": "P:requirements.thread_engagement_insert_min", "Li": "P:joints.insert_len_m",
                  "F": "ASM-C6-AVN-CRASH", "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "cap": "ASM-C6-INSERT-PULL"},
          equation="engagement = L - stack >= kmin d (D-41); blind hole >= engagement + 0.5 mm; "
                   "RF = pull-out / (F ff pf), whole crash load on one insert")
def insert(L, stack, d, kmin, Li, F, ff, pf, cap):
    e = L - stack
    return {"engage_m": e, "rf_engage": e / (kmin * d), "hole_depth_m": max(e, Li) + 0.0005,
            "rf_pull": cap / (F * ff * pf)}


# ----------------------------------------------------------------------------- bonded joints, fins
@kit.calc("CALC-C6-TUBE-BONDS", title="Tube-in-block, block-on-spar and station-collar bonds",
          inputs={"od": "P:fins.tube.od_m", "core": "ASM-C4-CORE-T-TUBE", "boss": "P:fin_detail.boss.height_m",
                  "Ls": "P:fin_detail.block.width_m", "Lc": "P:fin_detail.station_collar.height_m",
                  "Tz": "ASM-C6-FIN-MZ-ULT", "Ty": "ASM-C6-FIN-MY-ULT",
                  "Th": "ASM-C6-FINHALF-MZ-ULT", "Tc4": "ASM-C6-C4-COLLAR-T", "Fb": "CL-C4-D3-BRACE-F",
                  "sf": "P:requirements.safety_factor_ult", "ff": "ASM-C1-FITTING-FACTOR",
                  "pf": "ASM-C1-PRINTED-FACTOR", "tau": "ASM-C4-BOND-SHEAR"},
          equation="tau = T / (2 pi r^2 L), T = T_ult ff pf; spar OD = tube OD (22 mm); tube bore L = core + 2 bosses; "
                   "collar sizing (C4 method): tau = T_c4 sf ff pf / (2 pi r^2 h) + F_brace pf / (pi d h); "
                   "h_req = (T/(2 pi r^2) + F/(pi d)) / tau")
def tube_bonds(od, core, boss, Ls, Lc, Tz, Ty, Th, Tc4, Fb, sf, ff, pf, tau):
    r = od / 2
    k = 2 * math.pi * r ** 2
    Lb = core + 2 * boss
    T_tb, T_bs, T_c = Tz * ff * pf, Ty * ff * pf, Th * ff * pf
    T_c4 = Tc4 * sf * ff * pf
    F = Fb * pf
    q = T_c4 / k + F / (math.pi * od)                                  # N/m of collar height
    return {"T_tb_design_nm": T_tb, "T_bs_design_nm": T_bs,
            "L_bore_m": Lb, "area_bore_mm2": 2 * math.pi * r * Lb * 1e6, "rf_tube_block": tau * k * Lb / T_tb,
            "area_spar_mm2": 2 * math.pi * r * Ls * 1e6, "rf_block_spar": tau * k * Ls / T_bs,
            "area_collar_mm2": 2 * math.pi * r * Lc * 1e6, "T_c1_design_nm": T_c, "T_c4_design_nm": T_c4,
            "F_brace_design_n": F, "rf_collar": tau * k * Lc / T_c, "tau_collar_c4_mpa": q / Lc / 1e6,
            "rf_collar_c4": tau * Lc / q, "rf_collar_c4_12mm": tau * 0.012 / q, "L_collar_req_m": q / tau}


@kit.calc("CALC-C6-STRIP", title="Edge-strip anchorage in the station collar and strip-to-board shear flow",
          inputs={"s_cf": "ASM-C4-CF-SIGMA", "ms": "CL-C4-D3-MS-EDGE", "w": "P:fin_detail.edge_strip.w_m",
                  "t": "P:fin_detail.edge_strip.t_m", "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "tail": "P:fin_detail.station_collar.tail_m", "n_now": "P:joints.strip_bonded_faces_now",
                  "tau": "ASM-C4-BOND-SHEAR", "Ls": "ASM-C6-STRIP-L", "kd": "ASM-C6-FOAM-KD",
                  "tau_b": "ASM-D5-BOND-TAU", "tb": "P:fins.board_t_m", "nl": "P:fins.layers",
                  "dp": "P:fin_detail.edge_strip.pin_d_m", "pp": "P:fin_detail.edge_strip.pin_pitch_m",
                  "tau_pin": "ASM-C6-PIN-TAU"},
          equation="F = sigma_ult w t ff pf, sigma_ult = sigma_allow/(1+MS_edge) (C4 R3, two layers); anchor tau = "
                   "F/(n w L); L_req = F/(2 w tau); shear flow q = F/L_strip onto the paper face, tau = q/w vs kd "
                   "tau_board; pins through both layers: P = q pitch, shear P/(pi d^2/4), bending 32 P (n tb + t)/2 "
                   "/ (pi d^3)")
def strip(s_cf, ms, w, t, ff, pf, tail, n_now, tau, Ls, kd, tau_b, tb, nl, dp, pp, tau_pin):
    s_ult = s_cf / (1 + ms)
    F = s_ult * w * t * ff * pf
    q = F / Ls
    P = q * pp
    rf_sh = tau_pin * math.pi * dp ** 2 / 4 / P
    sig = 32 * P * (nl * tb + t) / 2 / (math.pi * dp ** 3)
    return {"F_design_n": F, "rf_anchor": tau * n_now * w * tail / F, "L_req_m": F / (2 * w * tau),
            "rf_anchor_r2": tau * 1 * w * 0.020 / F, "q_npm": q, "tau_face_mpa": q / w / 1e6,
            "rf_face": kd * tau_b / (q / w), "pin_load_n": P, "rf_pin_shear": rf_sh, "rf_pin_bend": s_cf / sig,
            "rf_pin": min(rf_sh, s_cf / sig), "pin_len_m": nl * tb + 2 * t, "pins_per_strip_pair": math.ceil(Ls / pp)}


@kit.calc("CALC-C6-BRACE", title="Brace ends in their slots and the anchor saddle on the spar",
          inputs={"F": "CL-C4-D3-BRACE-F", "pf": "ASM-C1-PRINTED-FACTOR", "w": "P:fin_detail.brace.w_m",
                  "t": "P:fin_detail.brace.t_m", "e": "P:fin_detail.brace.engage_m",
                  "ay": "P:fin_detail.anchor.len_y_m", "ds": "P:wing.spar.od_m",
                  "tau": "ASM-C4-BOND-SHEAR", "peel": "ASM-C6-PEEL"},
          equation="F_d = F (C4 R3, incl. 1.5 x 1.15) x pf; end bond tau = F_d / (2 (w+t) e); anchor saddle contact "
                   "= len_y x (pi d_spar / 4) (90 deg wrap, C4 method), sigma = F_d / A vs peel")
def brace(F, pf, w, t, e, ay, ds, tau, peel):
    Fd = F * pf
    A = ay * math.pi * ds / 4
    return {"F_design_n": Fd, "rf_end": tau * 2 * (w + t) * e / Fd, "anchor_area_mm2": A * 1e6,
            "rf_anchor": peel * A / Fd}


# ----------------------------------------------------------------------------- bonds into foam and foam board
@kit.calc("CALC-C6-FOAM-BONDS", title="Foot shoe and fin root bonds at the C6 allowables",
          inputs={"kd": "ASM-C6-FOAM-KD", "sf_d5": "CL-D5-BOND-SF", "rf_d3": "CL-D3-ROOT-FILLET-RF",
                  "s_xps": "ASM-D3-XPS-TENSILE"},
          equation="foot shoe RF = SF_D5 kd (D5 used the undiscounted 0.20 MPa); fin root RF = RF_D3 kd")
def foam_bonds(kd, sf_d5, rf_d3, s_xps):
    return {"rf_foot": sf_d5 * kd, "rf_root": rf_d3 * kd, "allow_xps_mpa": kd * s_xps / 1e6}


@kit.calc("CALC-C6-POD-ALLOW", title="Pod joint allowables owned by C6 (CR-C3-05) and C3's pod joints re-checked",
          inputs={"kd": "ASM-C6-FOAM-KD", "s_xps": "ASM-D3-XPS-TENSILE", "t_xps": "ASM-C6-XPS-SHEAR-TYP",
                  "tau_b": "ASM-D5-BOND-TAU", "f_b": "ASM-C6-BOARD-FLAT-TYP", "c3_sa": "ASM-D2-XPS-ALLOW",
                  "c3_ta": "ASM-C3-XPS-SHEAR", "c3_fb": "ASM-C3-FB-FLAT", "Rd": "CL-C3-BOND-R-DESIGN",
                  "Rc": "CL-C3-BOND-R-CRASH", "tray": "CL-C3-TRAY-FLAT", "glue": "CL-C3-FLOOR-GLUE",
                  "hatch": "CL-C3-HATCH-TAB", "hl": "ASM-C3-HL", "tb": "P:fins.board_t_m",
                  "leg": "P:joints.fillet_leg_m"},
          equation="C6 design allowable = kd x typical; C3 pod bond uses sigma_a = ASM-D2-XPS-ALLOW <= C6 and "
                   "tau_a = min(ASM-C3-XPS-SHEAR, ASM-D5-BOND-TAU) = C6, so RF = 1/R (conservative); tray flat RF = "
                   "kd f_b / sigma; floor glue RF = kd tau_b / sigma, with a fillet the glue width t -> t + leg; "
                   "hatch tab RF = HL tension / demand")
def pod_allow(kd, s_xps, t_xps, tau_b, f_b, c3_sa, c3_ta, c3_fb, Rd, Rc, tray, glue, hatch, hl, tb, leg):
    xt, xs, ps, bf = kd * s_xps, kd * t_xps, kd * tau_b, kd * f_b
    return {"xps_tension_mpa": xt / 1e6, "xps_shear_mpa": xs / 1e6, "paper_shear_mpa": ps / 1e6,
            "board_flat_mpa": bf / 1e6, "c3_over_c6_xps_t": c3_sa / xt, "c3_over_c6_xps_s": c3_ta / xs,
            "c3_over_c6_board_flat": c3_fb / bf, "c3_over_c6_paper_s": tau_b / ps,
            "rf_pod_design": 1 / Rd, "rf_pod_crash": 1 / Rc, "rf_tray": bf / tray, "rf_floor": ps / glue,
            "rf_floor_prop": ps * (tb + leg) / tb / glue, "rf_hatch": hl[1] / hatch}


@kit.calc("CALC-C6-LINKAGE", title="Servo frame and control horn: minimum bond area into XPS",
          inputs={"Mh": "CL-B2-HINGE-MOMENT", "arm": "ASM-C6-HORN-ARM", "V": "CL-C1-VD-ENV",
                  "Vb": "ASM-C6-B2-HINGE-V", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "kd": "ASM-C6-FOAM-KD",
                  "s_xps": "ASM-D3-XPS-TENSILE"},
          equation="F = Mh/arm (V_D/V_B2)^2 sf ff pf (full deflection at VD: conservative vs F4's schedule, D-29); "
                   "A_min = F / (kd sigma_XPS)")
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
   "rf_head", MOUNTS, "T-C6-HEAD-CREEP: 4 screws at 0.20 N m on a printed ASA plate, 2 h at 70 degC, witness lines "
   "unmoved and breakaway torque >= 0.15 N m")
rf("CL-C6-MOTOR-SEP-RF", "Motor screw preload / design tension incl. 7 deg cant side moment (no gapping)",
   "CALC-C6-MOTOR-SCREW", "rf_sep", MOTORS + MOUNTS,
   "Witness line across each screw head and plate; tap test after T-H1 thrust-stand runs")
rf("CL-C6-MOTOR-STRIP-RF", "Motor-base thread strip / design tension (3.5 mm engagement, canted plate)",
   "CALC-C6-MOTOR-SCREW", "rf_strip", MOTORS,
   "Probe the motor hole depth on arrival (E1 T-E1-MOTOR-RM); engagement >= 3.0 mm")
kit.claim("CL-C6-CANT-ENGAGE", "Motor-screw engagement on the 7 deg canted plate (R3, every hole)",
          calc="CALC-C6-CANT-SEAT", output="engage_m", unit="m", limit=(">=", 0.003), verifies=R_JS,
          parts=MOUNTS + MOTORS, how="T-C6-CANT-SEAT: all four heads flat (0.05 mm feeler), >= 6 turns from first bite",
          note="limit = requirements.thread_engagement_min 1.0 x d into metal (D-41)")
rf("CL-C6-MOUNT-SIDE-SLIP-RF", "Mount slip torque / tube torsion from the 7 deg side force (design)",
   "CALC-C6-MOUNT-SIDE", "rf_slip_torsion", MOUNTS + TUBES, "T-D3-SLIP setting; witness line after GT runs",
   ver=R_SM + R_FT)
rf("CL-C6-MOUNT-SIDE-AXIAL-RF", "Mount clamp axial friction / 7 deg side force along the tube (design)",
   "CALC-C6-MOUNT-SIDE", "rf_slip_axial", MOUNTS + TUBES, "Lip cap seated after GT runs; witness line", ver=R_SM + R_FT)
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
rf("CL-C6-PDB-ENGAGE-RF", "PDB screw engagement in the heat-set insert / 1.5 d", "CALC-C6-INSERT", "rf_engage",
   ["POD-002"], "F1 measures the PCB + spacer stack; screw runs in by hand >= 4.5 mm", ver=R_JS)
rf("CL-C6-INSERT-PULL-RF", "Heat-set insert pull-out / avionics crash load", "CALC-C6-INSERT", "rf_pull",
   ["POD-002"], "T-C6-INSERT: pull 3 inserts from a printed coupon boss")
rf("CL-C6-TUBE-BLOCK-RF", "Tube-in-block bond, fin torsion", "CALC-C6-TUBE-BONDS", "rf_tube_block",
   TUBES + BLOCKS, "T-C6-LAP-PETG (allowable) and C4 T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-BLOCK-SPAR-RF", "Block-on-spar bond, torsion about the spar", "CALC-C6-TUBE-BONDS", "rf_block_spar",
   BLOCKS + ["WNG-002"], "T-C6-LAP-PETG and T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-COLLAR-RF", "Station collar bond (12 mm as drawn), C1 half-fin torsion", "CALC-C6-TUBE-BONDS", "rf_collar",
   COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF (1.5 x L4) with the collar witness-marked", ver=R_SM + R_FT)
rf("CL-C6-COLLAR-RF-C4", "Station collar bond (16 mm, R3), C4 9.3 N m + brace shear (sizing case)",
   "CALC-C6-TUBE-BONDS", "rf_collar_c4", COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF with the collar "
   "witness-marked", ver=R_SM + R_FT)
kit.claim("CL-C6-COLLAR-L-REQ", "Station collar bond height needed for 9.3 N m + brace shear",
          calc="CALC-C6-TUBE-BONDS", output="L_collar_req_m", unit="m",
          limit=("<=", "P:fin_detail.station_collar.height_m"), verifies=R_SM + R_FT, parts=COLLARS,
          how="D3 keeps fin_detail.station_collar.height_m >= this; C1 and C4 agree the torsion (CR-C6-03)")
rf("CL-C6-STRIP-ANCHOR-RF", "Edge-strip end in the 40 mm two-face collar tail (R3)", "CALC-C6-STRIP",
   "rf_anchor", STRIPS + COLLARS, "T-C6-STRIP-ANCHOR: pull a strip out of a printed tail coupon", ver=R_SM + R_FT)
kit.claim("CL-C6-STRIP-EMBED-REQ", "Edge-strip embedment needed, both faces on PETG", calc="CALC-C6-STRIP",
          output="L_req_m", unit="m", limit=("<=", "P:fin_detail.station_collar.tail_m"), verifies=R_SM + R_FT,
          parts=COLLARS, how="T-C6-STRIP-ANCHOR on the 40 mm two-face tail")
kit.claim("CL-C6-STRIP-FACE-RF", "Edge-strip shear flow onto the board paper face if unpinned (why the pins exist; "
          "no limit: R3 carries the pins)", calc="CALC-C6-STRIP", output="rf_face", unit="-", verifies=R_SM,
          parts=STRIPS + HALVES, how="T-C6-BOARD-LAP (allowable); C4 confirms the shear flow in its FE (CR-C6-02)")
rf("CL-C6-STRIP-PIN-RF", "Through-pins tying the strip pair through two layers (CR-C6-02), weaker of shear and "
   "bending", "CALC-C6-STRIP", "rf_pin", STRIPS + HALVES, "T-C4-FIN-PROOF with pins fitted; no strip lift at the tip",
   ver=R_SM)
rf("CL-C6-BRACE-END-RF", "Brace ends bonded in the ear and anchor slots", "CALC-C6-BRACE", "rf_end",
   [f"FIN-009-{s}" for s in ST] + COLLARS + [f"FIN-010-{s}" for s in ST], "T-C6-LAP-PETG; T-C4-FIN-PROOF (G2)",
   ver=R_SM + R_FT)
rf("CL-C6-ANCHOR-PULL-RF", "Brace anchor saddle pull-off from the spar", "CALC-C6-BRACE", "rf_anchor",
   [f"FIN-010-{s}" for s in ST] + ["WNG-002"], "T-C4-FIN-PROOF (G2 in tension on the brace)", ver=R_SM + R_FT)
rf("CL-C6-FOOT-SHOE-RF", "Foot shoe bond on the fin tip at the C6 board allowable", "CALC-C6-FOAM-BONDS",
   "rf_foot", [f"GER-001-{s}" for s in ST] + HALVES, "T-C6-BOARD-LAP; T-C1-FOOT-DROP")
rf("CL-C6-FIN-ROOT-RF", "Half-fin root fillet on XPS at the C6 foam allowable", "CALC-C6-FOAM-BONDS", "rf_root",
   HALVES + ["WNG-001"], "T-C6-XPS-PULL; D3 T-D3-ROOT side pull", ver=R_SM + R_FT)
rf("CL-C6-POD-WING-RF", "Pod shell bond on the core, design envelope (1 / C3 interaction at C6-confirmed allowables)",
   "CALC-C6-POD-ALLOW", "rf_pod_design", ["POD-001", "WNG-001"], "T-C6-XPS-PULL (tension and shear); C3 pod proof")
rf("CL-C6-POD-CRASH-RF", "Pod shell bond on the core, 12.75 g crash", "CALC-C6-POD-ALLOW", "rf_pod_crash",
   ["POD-001", "WNG-001"], "T-C6-XPS-PULL", ver=["R-PACK-RETENTION"])
rf("CL-C6-POD-TRAY-RF", "Tray-to-floor bond flat-wise at the C6 board allowable (0.05 MPa)", "CALC-C6-POD-ALLOW",
   "rf_tray", POD, "T-C6-BOARD-LAP flat-wise pulls", ver=["R-PACK-RETENTION"])
rf("CL-C6-POD-FLOOR-RF", "Floor-to-side-wall glue line under the front strap at the C6 paper allowable (as drawn)",
   "CALC-C6-POD-ALLOW", "rf_floor", ["POD-001"], "T-C6-BOARD-CORNER: strap pull on a board corner coupon",
   ver=["R-PACK-RETENTION"])
rf("CL-C6-POD-FLOOR-RF-PROP", "Same glue line with a 6 mm microballoon fillet over the strap zone (CR-C6-17)",
   "CALC-C6-POD-ALLOW", "rf_floor_prop", ["POD-001"], "T-C6-BOARD-CORNER with the fillet", ver=["R-PACK-RETENTION"])
rf("CL-C6-POD-HATCH-RF", "Hatch latch hook-and-loop tension / VD suction demand", "CALC-C6-POD-ALLOW", "rf_hatch",
   ["POD-003"], "Spring scale on the closed hatch (C3 CL-C3-HATCH-TAB); T-D2-STRAP-PULL")
kit.claim("CL-C6-POD-ALLOW-RATIO", "Largest C3 pod-bond allowable / C6 allowable (XPS tension and shear)",
          calc="CALC-C6-POD-ALLOW", output="c3_over_c6_xps_t", unit="-", limit=("<=", 1.0), verifies=R_SM,
          parts=["POD-001"], how="T-C6-XPS-PULL replaces both numbers")
kit.claim("CL-C6-LINK-BOND-AREA-MIN", "Minimum bond area into XPS for a servo frame or a control horn",
          calc="CALC-C6-LINKAGE", output="A_min_mm2", unit="mm2", verifies=R_SM,
          parts=["MEC-008-L", "MEC-008-R", "MEC-004-L", "MEC-004-R"],
          how="D6 shows the bonded area of each part >= this; T-C6-XPS-PULL")
kit.claim("CL-C6-SNAP-L-MIN", "Foot snap-hook finger length for 2 % strain", calc="CALC-C6-SNAP", output="value",
          unit="m", verifies=R_JS, parts=[f"GER-002-{s}" for s in ST],
          how="D5 shows the free finger length >= this in the CAD; 20 insert swaps on one printed piston, no crack")

# ----------------------------------------------------------------------------- tests (H1 runs them with the first prints)
kit.test("T-C6-LAP-PETG", "Epoxy lap shear on abraded PETG, ASA and CF",
         ["CL-C6-TUBE-BLOCK-RF", "CL-C6-BLOCK-SPAR-RF", "CL-C6-COLLAR-RF", "CL-C6-COLLAR-RF-C4",
          "CL-C6-BRACE-END-RF", "CL-C6-STRIP-ANCHOR-RF"],
         procedure="5 single-lap coupons each: PETG-CF and ASA-CF tube offcut, 25 x 12.5 mm overlap, 120 grit + "
                   "IPA, 30 min epoxy, 24 h cure (+ 4 h at 50 degC for the ASA set); hang water jugs on a luggage "
                   "scale to failure. Allowable = mean x 0.5; pass >= 2.0 MPa (ASM-C4-BOND-SHEAR)")
kit.test("T-C6-BOARD-LAP", "Epoxy on paper-faced foam board, shear and flat-wise",
         ["CL-C6-FOOT-SHOE-RF", "CL-C6-STRIP-FACE-RF", "CL-C6-POD-TRAY-RF"],
         procedure="5 PETG tabs 20 x 20 mm bonded on a scuffed board face pulled in shear, 5 pulled flat-wise; "
                   "record the failure mode (paper peels vs epoxy). Allowables = 0.5 x mean (replace ASM-D5-BOND-TAU "
                   "x KD and ASM-C6-BOARD-FLAT-TYP x KD)")
kit.test("T-C6-XPS-PULL", "Flat-wise pull and shear of epoxy pucks on XPS",
         ["CL-C6-FIN-ROOT-RF", "CL-C6-POD-WING-RF", "CL-C6-POD-CRASH-RF", "CL-C6-LINK-BOND-AREA-MIN"],
         procedure="10 printed pucks 30 mm dia bonded with microballoon epoxy on hot-wire-cut F-250 offcut: 5 pulled "
                   "normal to the face, 5 pushed sideways; allowables = 0.5 x mean (replace ASM-D3-XPS-TENSILE and "
                   "ASM-C6-XPS-SHEAR-TYP x KD)")
kit.test("T-C6-BOARD-CORNER", "Pod floor-to-wall corner under a strap pull", ["CL-C6-POD-FLOOR-RF",
                                                                               "CL-C6-POD-FLOOR-RF-PROP"],
         procedure="Two 100 mm long board U-sections (floor + two walls) glued edge-to-face as D2 builds the pod, "
                   "one with the 6 mm fillets; pull a 20 mm strap off the floor with water jugs; pass >= 43 N (C3 "
                   "per-strap design load: 85 N crash / 2 straps)")
kit.test("T-C6-INSERT", "Heat-set insert pull-out", ["CL-C6-INSERT-PULL-RF"],
         procedure="3 inserts in a printed boss (same settings as POD-002), M3 screw + washer, pull to failure; "
                   "pass >= 300 N each")
kit.test("T-C6-HEAD-CREEP", "Motor screw creep on a hot printed plate", ["CL-C6-MOTOR-HEAD-RF"],
         procedure="Printed ASA mount plate on an aluminium block with 4 x M3x8 at 0.20 N m, "
                   "2 h at 70 degC (oven), cool, breakaway torque >= 0.15 N m on all four")
kit.test("T-C6-CANT-SEAT", "Motor screws on the 7 deg canted mount", ["CL-C6-CANT-ENGAGE", "CL-C6-MOTOR-STRIP-RF"],
         procedure="First printed mount A, holes drilled square to the canted face to the motor's pattern; fit the "
                   "motor; 4 x M3x8 at 0.20 N m; count turns from first bite (>= 6 = 3.0 mm, <= probed depth - 0.5) "
                   "and check a 0.05 mm feeler does not enter under any head")
kit.test("T-C6-STRIP-ANCHOR", "Edge-strip pull-out from the collar tail", ["CL-C6-STRIP-ANCHOR-RF",
                                                                           "CL-C6-STRIP-EMBED-REQ"],
         procedure="Print the 40 mm two-face station collar tail alone; bond a 10 x 1 strip pair in "
                   "it as built; pull along the strip with water jugs; pass >= F_design_n of CALC-C6-STRIP (700 N)")
kit.test("T-C6-PROPNUT", "Prop-nut torque on a finished mount", ["CL-C6-MOUNT-ROCK-RF", "CL-C6-MOUNT-HOOP-RF"],
         procedure="Bell held by hand, prop nut to 1.5 N m and off 10 times; collar witness line and lip cap unmoved")

if __name__ == "__main__":
    kit.write()
