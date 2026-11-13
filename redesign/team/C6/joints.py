"""C6 joints and fasteners: sizing checks for every fastened and bonded joint of K09-L. Emits claims.json.

    python -I redesign/team/C6/joints.py        then   python -I redesign/proofs/build_graph.py

Revision C6-R5 (params A1-R5; D-68 / D-70 as drawn by D3-R5: pins 2.5 mm at 15 mm, station collar 13 mm, block
vertical edges R 3 mm; C4's frozen R4 set CL-C4-D3-* read directly from team/C4/claims.d3.json; C1 claims and
data/envelope.json read live (the R4 hand copies of the envelope drifted after C1's D-65 re-run); D5 R5 bond block
CL-D5-BOND-SF / -AREA; F1 power frame E-PWR-03 at 0.08 N m, still open with F1).
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
kit.assumption("ASM-C6-CF-BEARING", "Pultruded CF strip pin bearing 100 MPa", "Bearing allowable of a 1 mm "
               "pultruded CF strip on a bonded pin", "UD pultrusions split at ~200-300 MPa pin bearing; half, and the "
               "pin is bonded in (no clearance); T-C4-FIN-PROOF with pins fitted", 100e6, "Pa", status="UNVERIFIED")
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
# loads from C1 data/envelope.json, read live (C6-R5): the R4 hand copies drifted when C1 re-ran for D-65
import json as _json                                                     # noqa: E402
_ENVD = _json.loads((ROOT / ENV).read_text(encoding="utf-8"))
_JM = _ENVD["joints"]["J-MOTOR"]["M_res_Nm"]
_JZ = _ENVD["joints"]["J-FIN"]["Mz_Nm"]
_JY = _ENVD["joints"]["J-FIN"]["My_Nm"]
_AV = _ENVD["other"]["crash_ultimate"]["avionics_N_any_axis"]
kit.assumption("ASM-C6-MOTOR-M-ULT", f"Motor-to-mount moment {_JM['ultimate']:.3f} N m (ult)", "Ultimate moment at "
               "the motor base (no cant side force; C1 does not model the cant)",
               f"{ENV}#joints.J-MOTOR.M_res_Nm.ultimate ({_JM.get('case', '')}; read live)", _JM["ultimate"], "N m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MZ-ULT", f"Fin group torsion about the tube {_JZ['ultimate']:.2f} N m (ult)", "Ultimate Mz "
               "of the fin group at the wing", f"{ENV}#joints.J-FIN.Mz_Nm.ultimate ({_JZ.get('case', '')}; read live)",
               _JZ["ultimate"], "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-FIN-MY-ULT", f"Fin group torsion about the spar {_JY['ultimate']:.2f} N m (ult)", "Ultimate My "
               "of the fin group at the wing", f"{ENV}#joints.J-FIN.My_Nm.ultimate ({_JY.get('case', '')}; read live)",
               _JY["ultimate"], "N m", status="UNVERIFIED")
kit.assumption("ASM-C6-STRIP-L", "Edge strip length 229 mm", "Length of one edge strip from the collar tail to the "
               "square tip (pin count only)", "team/D3/CHANGE-REQUESTS.md CR-D3-18 (R3 square tip, strips end at "
               "x 0.280); D3 R4 E-FIN-21 strip 224 mm", 0.224, "m", status="PROPOSED")
kit.assumption("ASM-C6-BLOCK-LX", "Through-core block plan length 69.3 mm", "Chordwise length of the block and its core "
               "pocket (tube socket + spar saddle)", "subsystems/wing/SPEC.md through-core block pocket x 0.0279-0.0972 "
               "(E-FIN-49...52); README.md block 69 x 36 mm", 0.0693, "m", status="PROPOSED")
kit.assumption("ASM-C6-TAIL-NET-A", "Collar tail net section 95 mm2", "Effective PETG area carrying one strip's "
               "force along the two-face tail: walls 1.2 mm + cap 1.2 mm + tongue at 0.45 fill",
               "team/D3/CHANGE-REQUESTS.md CR-D3-17 (D3 estimate); T-C6-STRIP-ANCHOR fails the tail or the bond",
               95e-6, "m2", status="UNVERIFIED")
kit.assumption("ASM-C6-AVN-CRASH", f"Avionics crash load {_AV:.2f} N", "Ultimate crash load of an avionics item, "
               "any axis (used for the power frame on its inserts and the FC on its gel pads)",
               f"{ENV}#other.crash_ultimate.avionics_N_any_axis (read live)", _AV, "N", status="UNVERIFIED")
kit.assumption("ASM-C6-PWR-UNPLUG", "AS150U unplug pull 50 N on the power frame, 18 mm above the inserts, 25 mm "
               "screw pattern", "Hand pull that separates the AS150U pair, carried by the frame cradle if the pilot "
               "does not hold the cradle; lever = connector axis above the insert faces; pattern = boss spacing",
               "team/F1/CHANGE-REQUESTS.md CR-F1-20 (F1 estimate: 18 N tension per screw); "
               "subsystems/power/interfaces.json E-PWR-03 notes (25 mm pattern)", [50.0, 0.018, 0.025], "N, m, m",
               status="UNVERIFIED")
kit.assumption("ASM-C6-PA66-SIGMA", "PA66 screw allowable 50 MPa", "Tensile / von Mises allowable of a moulded PA66 "
               "M3 screw at 50 % RH, room temperature, used for the one-time installation stress and service tension",
               "PA66 dry ~80 MPa, conditioned ~50-60 MPa (typical datasheet range for unfilled PA66); the "
               "conditioned value is taken. Replaced by T-C6-NYLON-TORQUE", 50e6, "Pa", status="UNVERIFIED")
kit.assumption("ASM-C6-THREAD-SHARE", "Thread share of tightening torque 0.5", "Fraction of the applied torque that "
               "twists the screw shank (thread friction + pitch); the rest is head friction",
               "VDI 2230 split, typical 0.4-0.6 for a pan head on a washer", 0.5, "-", status="PROPOSED")
kit.assumption("ASM-C6-NYLON-MU", "Friction nylon washer / PETG deck / nylon spacer 0.25", "Friction coefficient in "
               "the clamped power-frame stack", "PA66 on PETG, dry, typical 0.25-0.4; lower end taken", 0.25, "-",
               status="UNVERIFIED")
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


@kit.calc("CALC-C6-PWR-FRAME", title="Power frame PWR-006 on 4 x M3x18 PA66 into brass heat-set inserts (E-PWR-03)",
          inputs={"L": "P:joints.pwr_frame.screw_len_m", "stack": "P:joints.pwr_frame.stack_m",
                  "bore": "P:joints.pwr_frame.bore_depth_m", "sp": "P:joints.pwr_frame.spacer_m",
                  "d": "P:joints.m3_d_m", "p": "P:joints.m3_pitch_m",
                  "kmin": "P:requirements.thread_engagement_insert_min", "Li": "P:joints.insert_len_m",
                  "T": "P:joints.torque.nylon_m3_nm", "K": "ASM-C6-NUT-FACTOR", "share": "ASM-C6-THREAD-SHARE",
                  "s_pa": "ASM-C6-PA66-SIGMA", "mu": "ASM-C6-NYLON-MU", "un": "ASM-C6-PWR-UNPLUG",
                  "Fc": "ASM-C6-AVN-CRASH", "cap": "ASM-C6-INSERT-PULL", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR"},
          equation="e = L - stack >= kmin d (D-41), e <= insert length, bore >= e + 0.5 mm; preload P = T/(K d); "
                   "install von Mises = sqrt((P/As)^2 + 3 (16 share T/(pi d3^3))^2), As = pi/4 ((d2+d3)/2)^2; "
                   "unplug design k = sf ff pf: tension per screw F_t = k F a/(2 s), shear V = k F; tension RF = "
                   "s_pa As/(P + F_t); slip RF = 4 mu P / V (and at 50 % preload after nylon creep); if it slips the "
                   "spacer bends as a guided column: M = (V/4) L_sp/2, sigma = M (OD/2)/I_tube; insert RF = "
                   "pull-out / max(P + F_t, Fc ff pf)")
def pwr_frame(L, stack, bore, sp, d, p, kmin, Li, T, K, share, s_pa, mu, un, Fc, cap, sf, ff, pf):
    e = L - stack
    d2, d3 = d - 0.6495 * p, d - 1.2269 * p
    As = math.pi / 4 * ((d2 + d3) / 2) ** 2
    P = T / (K * d)
    sig, tau = P / As, 16 * share * T / (math.pi * d3 ** 3)
    vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
    F, a, s = un
    k = sf * ff * pf
    Ft, V = k * F * a / (2 * s), k * F
    od, idd, lsp = sp
    I = math.pi / 64 * (od ** 4 - idd ** 4)
    sig_sp = (V / 4) * lsp / 2 * (od / 2) / I
    return {"engage_m": e, "rf_engage": e / (kmin * d), "rf_insert_len": Li / e, "tip_clear_m": bore - e,
            "rf_bore": bore / (e + 0.0005), "preload_n": P, "install_vm_mpa": vm / 1e6, "rf_install": s_pa / vm,
            "rf_install_at_0p2": s_pa / math.sqrt((sig * 0.2 / T) ** 2 + 3 * (tau * 0.2 / T) ** 2),
            "tension_design_n": Ft, "shear_design_n": V, "rf_tension": s_pa * As / (P + Ft),
            "rf_slip": 4 * mu * P / V, "rf_slip_relaxed": 4 * mu * 0.5 * P / V, "spacer_mpa": sig_sp / 1e6,
            "rf_spacer": s_pa / sig_sp, "rf_pull": cap / max(P + Ft, Fc * ff * pf),
            "scale_n_at_50mm": T / 0.05}


# ----------------------------------------------------------------------------- bonded joints, fins
@kit.calc("CALC-C6-TUBE-BONDS", title="Tube-in-block, block-on-spar and station-collar bonds",
          inputs={"od": "P:fins.tube.od_m", "core": "ASM-C4-CORE-T-TUBE", "boss": "P:fin_detail.boss.height_m",
                  "Ls": "P:fin_detail.block.width_m", "Lc": "P:fin_detail.station_collar.height_m",
                  "Tz": "ASM-C6-FIN-MZ-ULT", "Ty": "ASM-C6-FIN-MY-ULT",
                  "Tc1": "CL-C1-FINHALF-T-LIM", "Tc4": "CL-C4-D3-COLLAR-T", "Fb": "CL-C4-D3-BRACE-F",
                  "h12": "P:joints.collar_alt_h_m", "h13": "P:joints.collar_min_h_m",
                  "hc": "P:joints.collar_cond_h_m", "h15": "P:joints.collar_prop_h_m", "tau_c": "P:joints.collar_cond_tau_pa",
                  "sf": "P:requirements.safety_factor_ult", "ff": "ASM-C1-FITTING-FACTOR",
                  "pf": "ASM-C1-PRINTED-FACTOR", "tau": "ASM-C4-BOND-SHEAR"},
          equation="tau = T / (2 pi r^2 L), T = T_ult ff pf; spar OD = tube OD (22 mm); tube bore L = core + 2 bosses; "
                   "collar (CR-C4-23): T_lim = max(C1 J-FINHALF section torsion, C4 FE collar torsion); tau = T_lim sf "
                   "ff pf / (2 pi r^2 h) + F_brace pf / (pi d h) (F_brace already x 1.5 x 1.15); "
                   "h_req = (T/(2 pi r^2) + F/(pi d)) / tau; D-70 condition: 12 mm only at tau_c = 0.5 x 4.1 MPa "
                   "coupon mean")
def tube_bonds(od, core, boss, Ls, Lc, Tz, Ty, Tc1, Tc4, Fb, h12, h13, hc, h15, tau_c, sf, ff, pf, tau):
    r = od / 2
    k = 2 * math.pi * r ** 2
    Lb = core + 2 * boss
    T_tb, T_bs = Tz * ff * pf, Ty * ff * pf
    T_lim = max(Tc1, Tc4)
    T_c = T_lim * sf * ff * pf
    F = Fb * pf
    q = T_c / k + F / (math.pi * od)                                   # N/m of collar height
    return {"T_tb_design_nm": T_tb, "T_bs_design_nm": T_bs,
            "L_bore_m": Lb, "area_bore_mm2": 2 * math.pi * r * Lb * 1e6, "rf_tube_block": tau * k * Lb / T_tb,
            "area_spar_mm2": 2 * math.pi * r * Ls * 1e6, "rf_block_spar": tau * k * Ls / T_bs,
            "area_collar_mm2": 2 * math.pi * r * Lc * 1e6, "T_collar_lim_nm": T_lim,
            "collar_c1_governs": 1.0 if Tc1 >= Tc4 else 0.0,
            "T_collar_design_nm": T_c, "F_brace_design_n": F, "tau_collar_mpa": q / Lc / 1e6,
            "rf_collar": tau * Lc / q, "rf_collar_alt": tau * h12 / q, "rf_collar_min": tau * h13 / q, "L_collar_req_m": q / tau,
            "rf_collar_cond12": tau_c * hc / q, "rf_collar_prop": tau * h15 / q, "tau_req_12_mpa": q / hc / 1e6}


@kit.calc("CALC-C6-STRIP", title="Edge-strip anchorage in the station collar and strip-to-board shear flow",
          inputs={"s_cf": "ASM-C4-CF-SIGMA", "F": "CL-C4-D3-STRIP-END-F", "q_lim": "CL-C4-D3-STRIP-Q",
                  "Pp": "CL-C4-D3-STRIP-PIN-F", "w": "P:fin_detail.edge_strip.w_m",
                  "t": "P:fin_detail.edge_strip.t_m", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR",
                  "tail": "P:fin_detail.station_collar.tail_m", "gap": "P:fin_detail.fin.le_gap_m",
                  "n_now": "P:joints.strip_bonded_faces_now", "tau": "ASM-C4-BOND-SHEAR",
                  "A_net": "ASM-C6-TAIL-NET-A", "s_pet": "ASM-C4-PETG-TENSILE",
                  "kd": "ASM-C6-FOAM-KD", "tau_b": "ASM-D5-BOND-TAU", "tb": "P:fins.board_t_m",
                  "nl": "P:fins.layers", "dp": "P:fin_detail.edge_strip.pin_d_m",
                  "pp": "P:fin_detail.edge_strip.pin_pitch_m", "pp_new": "P:joints.pin_pitch_prop_m",
                  "Ls": "ASM-C6-STRIP-L", "tau_pin": "ASM-C6-PIN-TAU",
                  "dp2": "P:joints.pin_d_prop_m", "pp_alt": "P:joints.pin_pitch_alt_m",
                  "d_alt": "P:joints.pin_d_alt_m", "s_brg": "ASM-C6-CF-BEARING"},
          equation="C4 R3 FE (CR-C4-23): F = strip force per face at the collar end, design; anchor tau = "
                   "F/(n w (tail - gap)); L_req = F/(2 w tau); tail net section sigma = F / A_net vs PETG; paper face "
                   "if unpinned: tau = q_lim sf ff pf / w vs kd tau_board; pins carry the whole shear flow: "
                   "P = C4 pin force at the drawn pitch, shear P/(pi d^2/4), bending (pin loaded at the strip, "
                   "reacted at the board mid-plane, bound) 32 P (n tb + t)/2 / (pi d^3); at another pitch "
                   "P' = P pitch'/pitch; D-70 (drawn since D3-R5): d = d' = 2.5 mm at 15 mm; fallback d_alt 2 mm at "
                   "pitch_alt; max pitch for the drawn d = pitch x RF(d), and for d_alt likewise; strip bearing "
                   "P'/(d' t) vs CF bearing; strip net section at the pin F/((w - d') t) vs CF")
def strip(s_cf, F, q_lim, Pp, w, t, sf, ff, pf, tail, gap, n_now, tau, A_net, s_pet, kd, tau_b, tb, nl, dp, pp,
          pp_new, Ls, tau_pin, dp2, pp_alt, d_alt, s_brg):
    emb = tail - gap
    q = q_lim * sf * ff * pf

    def pin_rf(P, d=dp):
        sh = tau_pin * math.pi * d ** 2 / 4 / P
        sig = 32 * P * (nl * tb + t) / 2 / (math.pi * d ** 3)
        return min(sh, s_cf / sig), sh, s_cf / sig
    rf_p, rf_sh, rf_b = pin_rf(Pp)
    P2 = Pp * pp_new / pp
    P3 = Pp * pp_alt / pp
    return {"F_design_n": F, "embed_m": emb, "rf_anchor": tau * n_now * w * emb / F, "L_req_m": F / (2 * w * tau),
            "tail_net_mpa": F / A_net / 1e6, "rf_tail_net": s_pet * A_net / F, "q_design_npm": q,
            "tau_face_mpa": q / w / 1e6, "rf_face": kd * tau_b / (q / w), "pin_load_n": Pp, "rf_pin_shear": rf_sh,
            "rf_pin_bend": rf_b, "rf_pin": rf_p, "pin_load_prop_n": P2, "rf_pin_prop": pin_rf(P2, dp2)[0],
            "rf_pin_prop_shear": pin_rf(P2, dp2)[1], "rf_pin_alt": pin_rf(P3, d_alt)[0], "pin_load_alt_n": P3,
            "pitch_max_d_m": pp * rf_p, "pitch_max_dalt_m": pp * pin_rf(Pp, d_alt)[0],
 "rf_pin_bearing": s_brg * dp2 * t / P2,
            "rf_strip_net_pin": s_cf * (w - dp2) * t / F,
            "pin_len_m": nl * tb + 2 * t, "pins_per_strip_pair": math.ceil(Ls / pp),
            "pins_per_strip_pair_prop": math.ceil(Ls / pp_new),
            "pins_per_strip_pair_alt": math.ceil(Ls / pp_alt)}


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


@kit.calc("CALC-C6-BLOCK-POCKET", title="Through-core block in its core pocket with R 3 mm vertical edges (D-68)",
          inputs={"r": "P:fin_detail.block.edge_r_m", "w": "P:fin_detail.block.width_m", "Lx": "ASM-C6-BLOCK-LX",
                  "bl": "P:joints.bondline_max_m", "leg": "P:joints.pocket_bead_leg_m",
                  "gcc": "P:fin_detail.fin.root_fillet.gcc", "nb": "P:joints.pocket_beads_per_block"},
          equation="plan perimeter square 2 (Lx + w), rounded 2 (Lx + w) - 8 r + 2 pi r (wall bond area scales with it); "
                   "a square-cut pocket leaves (sqrt 2 - 1) r of void on each corner diagonal; a pocket radius R_p "
                   "seats the block with a corner gap (sqrt 2 - 1)(R_p - r) for R_p >= r (R_p < r rides on the "
                   "corners), so r <= R_p <= r + bl/(sqrt 2 - 1); bead = nb x Lx of leg^2/2 section at gcc, two blocks")
def block_pocket(r, w, Lx, bl, leg, gcc, nb):
    k = math.sqrt(2) - 1
    p0 = 2 * (Lx + w)
    p1 = p0 - 8 * r + 2 * math.pi * r
    return {"perim_square_m": p0, "perim_round_m": p1, "wall_area_ratio": p1 / p0, "gap_square_m": k * r,
            "rf_square_fit": bl / (k * r), "Rp_min_m": r, "Rp_max_m": r + bl / k,
            "bead_mass_g": 2 * nb * Lx * leg ** 2 / 2 * gcc * 1e6, "bead_len_per_block_m": nb * Lx}


@kit.calc("CALC-C6-FIN-SCALE", title="Bounding estimate: C4's frozen R4 fin joint loads scaled to C1's D-65 torsion",
          inputs={"T1": "CL-C1-FINHALF-T-WINGPLANE-LIM", "T4": "CL-C4-D3-SEC-T-L4", "F": "CL-C4-D3-STRIP-END-F",
                  "ra": "CL-C6-STRIP-ANCHOR-RF", "rt": "CL-C6-STRIP-TAIL-NET-RF", "rp": "CL-C6-STRIP-PIN-RF",
                  "pmax": "CL-C6-STRIP-PIN-PITCH-MAX", "Lreq": "CL-C6-STRIP-EMBED-REQ", "A_net": "ASM-C6-TAIL-NET-A"},
          equation="k = C1 wing-plane half-fin torsion now / the C4 FE wing-plane torsion its R4 set was solved at "
                   "(C4 checked them equal then, CL-C4-D3-SEC-T-VS-C1); the foot side load drives both the torsion and "
                   "the strip couple, so strip force, pin force and the collar-tail demand scale with k (linear FE): "
                   "F' = k F, RF' = RF / k, pitch_max' = pitch_max / k, L_req' = k L_req, tail net area needed "
                   "= k A_net / RF_tail; H1 frame >= 1.25 F'. Estimate only, replaced by C4's re-run")
def fin_scale(T1, T4, F, ra, rt, rp, pmax, Lreq, A_net):
    k = T1 / T4
    return {"k": k, "F_strip_n": k * F, "rf_anchor": ra / k, "rf_tail_net": rt / k, "rf_pin": rp / k,
            "pitch_max_m": pmax / k, "L_req_m": k * Lreq, "A_net_req_m2": k * A_net / rt, "frame_n": 1.25 * k * F}


# ----------------------------------------------------------------------------- D-81 clocking dog (D-94)
kit.source("SRC-C6-ASA-TDS", "Push Plastic ASA technical data sheet", "datasheet",
           url="https://cdn.shopify.com/s/files/1/0260/7421/files/Push_Plastic_ASA_Technical_Data_sheet.pdf",
           checked="2026-11-13",
           where="mechanical table: tensile stress at yield 36.5 MPa, at break 30.5 MPa, flexural 62.2 MPa, flexural "
                 "modulus 1 948 MPa (ASTM D638 / D790, values marked * on the sheet)")
kit.assumption("ASM-C6-ASA-YIELD", "ASA tensile yield 36.5 MPa (filament datasheet)", "Upper bound of the printed "
               "ASA strength used to bound the clocking dog's break torque from above (a fuse must not be stronger "
               "than designed)", "SRC-C6-ASA-TDS tensile stress at yield 36.5 MPa (checked 2026-11-13)",
               value=36.5e6, unit="Pa", status="UNVERIFIED", cites=["SRC-C6-ASA-TDS"])
kit.assumption("ASM-C6-ASA-INTERLAYER", "ASA interlayer shear 0.5 x the in-layer von Mises shear", "Lower bound of "
               "the dog's shear strength: the dog's shear plane is a layer plane (mount printed collar axis vertical)",
               "C4/C6 practice for printed parts (ASM-C4-PETG-TENSILE takes 50 % of the Z yield); EST until "
               "T-C6-DOG-SHEAR", value=0.5, unit="-", status="UNVERIFIED")


@kit.calc("CALC-C6-DOG", title="Clocking dog under the mount collar (D-81): fuse torque bounds and hold",
          inputs={"kw": "P:fin_detail.mount.key_w_m", "od": "P:fins.tube.od_m", "gap": "P:fin_detail.bond_gap_m",
                  "ring": "P:fin_detail.station_collar.ring_wall_m", "cw": "P:fin_detail.mount.collar_wall_m",
                  "T_slip": "P:fin_detail.mount.slip_torque_nm", "s_y": "ASM-C6-ASA-YIELD",
                  "k_il": "ASM-C6-ASA-INTERLAYER", "T_tw": "CL-C4-D3-MOUNT-TWIST", "tau": "ASM-C4-BOND-SHEAR",
                  "Lc": "P:fin_detail.station_collar.height_m", "core": "ASM-C4-CORE-T-TUBE",
                  "boss": "P:fin_detail.boss.height_m"},
          equation="dog shear plane at the notch top: A = w_key x (min(r_col, r_ring) - r_b), r_b = od/2 + gap, mean "
                   "radius r_m = r_b + radial/2; break torque upper bound T_hi = (s_y / sqrt 3) A r_m (in-layer von "
                   "Mises, yield), lower bound T_lo = k_il T_hi (layer plane); fuse T_fuse = T_slip + T_hi (D-23: the "
                   "clamp slips at T_slip, then the dog shears); downstream capacities at the C4 bond allowable: station "
                   "collar on the tube tau 2 pi r^2 L_c, tube in block tau 2 pi r^2 (core + 2 boss); RF_fuse = "
                   "min(capacity) / T_fuse; hold if the clamp is lost: RF_hold = T_lo / T_twist (C4 design twist)")
def dog(kw, od, gap, ring, cw, T_slip, s_y, k_il, T_tw, tau, Lc, core, boss):
    r_b = od / 2 + gap
    radial = min(ring, cw)
    A = kw * radial
    r_m = r_b + radial / 2
    T_hi = s_y / math.sqrt(3) * A * r_m
    T_lo = k_il * T_hi
    T_f = T_slip + T_hi
    k = 2 * math.pi * (od / 2) ** 2
    cap_collar, cap_block = tau * k * Lc, tau * k * (core + 2 * boss)
    return {"area_mm2": A * 1e6, "r_m_m": r_m, "T_dog_hi_nm": T_hi, "T_dog_lo_nm": T_lo, "T_fuse_nm": T_f,
            "cap_collar_nm": cap_collar, "cap_block_nm": cap_block,
            "rf_fuse": min(cap_collar, cap_block) / T_f, "rf_hold": T_lo / T_tw, "dog_share": T_hi / T_f}


def _rf_dog(cid, title, calc, out, parts, how):
    kit.claim(cid, title, calc=calc, output=out, unit="-", limit=(">=", 1.0), verifies=R_SM, parts=parts, how=how)


kit.claim("CL-C6-DOG-FUSE-T", "Torque to turn the mount on the tube with the clocking dog (slip + dog break, upper "
          "bound)", calc="CALC-C6-DOG", output="T_fuse_nm", unit="N m", verifies=R_SM, parts=MOUNTS + COLLARS,
          how="T-C6-DOG-SHEAR: two printed mounts on a tube stub with a bonded station collar, pinch bolt at the "
              "T-D3-SLIP setting, torque wrench / luggage scale on a 100 mm arm until the mount turns; record the peak")
_rf_dog("CL-C6-DOG-FUSE-RF", "Weakest downstream torsion capacity (station collar or tube-in-block bond) / mount fuse "
   "torque with the dog (D-23 holds: the mount gives first)", "CALC-C6-DOG", "rf_fuse", MOUNTS + COLLARS + TUBES,
   "T-C6-DOG-SHEAR; witness marks on the station collar after T-C4-FIN-PROOF")
_rf_dog("CL-C6-DOG-HOLD-RF", "Dog alone holds the 7 deg cant twist if the clamp is lost (lower bound)", "CALC-C6-DOG",
   "rf_hold", MOUNTS + COLLARS, "T-C6-DOG-SHEAR lower result; pinch bolt check every 10 flights")
kit.test("T-C6-DOG-SHEAR", "Clocking dog shear-out on a tube stub", verifies=["CL-C6-DOG-FUSE-T", "CL-C6-DOG-FUSE-RF",
         "CL-C6-DOG-HOLD-RF"], procedure="Two D-91 mounts, each on a 60 mm tube stub with a 22 mm PETG station collar "
         "bonded under it (dog in the notch). Pinch bolt set to the T-D3-SLIP 2.5 N m. Load a 100 mm arm with a luggage "
         "scale until the mount turns; record the peak torque and whether the dog sheared. Pass: peak <= "
         "CL-C6-DOG-FUSE-T x 1.1 and the dog piece shears, not the collar bond (no witness-mark movement)")


# ----------------------------------------------------------------------------- bonds into foam and foam board
@kit.calc("CALC-C6-FOAM-BONDS", title="Foot shoe and fin root bonds at the C6 allowables",
          inputs={"kd": "ASM-C6-FOAM-KD", "sf_d5": "CL-D5-BOND-SF", "A_d5": "CL-D5-BOND-AREA",
                  "tau_b": "ASM-D5-BOND-TAU", "rf_d3": "CL-D3-ROOT-FILLET-RF", "s_xps": "ASM-D3-XPS-TENSILE",
                  "leg0": "P:fin_detail.fin.root_fillet.leg_m", "leg1": "P:joints.root_fillet_leg_m", "tb": "P:fins.board_t_m",
                  "nl": "P:fins.layers"},
          equation="foot shoe (CR-D5-24): D5 now sizes at the C6 allowable kd tau_board, so RF = SF_D5; design load "
                   "= kd tau A / SF; fin root RF = RF_D3 x (C6 XPS allowable / D3's 0.25 MPa) = RF_D3 kd; with leg "
                   "l': x l'(n tb + l') / (l (n tb + l)) (fillet couple capacity, CALC-D3-ROOT)")
def foam_bonds(kd, sf_d5, A_d5, tau_b, rf_d3, s_xps, leg0, leg1, tb, nl):
    tf = nl * tb
    return {"rf_foot": sf_d5, "foot_area_mm2": A_d5 * 1e6, "foot_design_n": kd * tau_b * A_d5 / sf_d5,
            "rf_root": rf_d3 * kd, "rf_root_prop": rf_d3 * kd * leg1 * (tf + leg1) / (leg0 * (tf + leg0)),
            "leg_req_m": (-tf + math.sqrt(tf ** 2 + 4 * leg0 * (tf + leg0) / (rf_d3 * kd))) / 2,
            "allow_xps_mpa": kd * s_xps / 1e6}


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
          inputs={"Mh": "CL-B2-HINGE-MOMENT", "arm": "ASM-C6-HORN-ARM", "V": "P:requirements.vd_ms",
                  "Vb": "ASM-C6-B2-HINGE-V", "sf": "P:requirements.safety_factor_ult",
                  "ff": "ASM-C1-FITTING-FACTOR", "pf": "ASM-C1-PRINTED-FACTOR", "kd": "ASM-C6-FOAM-KD",
                  "s_xps": "ASM-D3-XPS-TENSILE"},
          equation="F = Mh/arm (V_D/V_B2)^2 sf ff pf, V_D = requirements.vd_ms 27.2 m/s (D-50: VD held by the "
                   "fixed-wing throttle cap; full deflection at VD is conservative vs F4's schedule, D-29); "
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


def _rec(cid, title, calc, out, parts, how, ver=R_SM, unit="-"):
    """D-90: a superseded collar height kept as a record (no limit; the drawn 22 mm is CL-C6-COLLAR-RF)."""
    kit.claim(cid, title + " (record, D-90 draws 22 mm)", calc=calc, output=out, unit=unit, verifies=ver, parts=parts,
              how=how)


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
PWR = ["PWR-006", "POD-002"]
rf("CL-C6-PWR-ENGAGE-RF", "Power-frame M3x18 PA66 engagement in the heat-set insert / 1.5 d (E-PWR-03)",
   "CALC-C6-PWR-FRAME", "rf_engage", PWR, "Build check: stack 0.5 + 2.0 + 10.0 mm measured with calipers; the screw "
   "runs in by hand >= 9 turns (4.5 mm) before the head seats", ver=R_JS)
rf("CL-C6-PWR-BORE-RF", "Insert bore depth / (engagement + 0.5 mm): the M3x18 tip does not bottom", "CALC-C6-PWR-FRAME",
   "rf_bore", PWR, "D2 bore 4.0 x 6.5 mm; head seats on the washer with no gap (0.05 mm feeler)", ver=R_JS)
rf("CL-C6-PWR-INSERT-LEN-RF", "Insert length / engagement: the screw stays inside the brass", "CALC-C6-PWR-FRAME",
   "rf_insert_len", PWR, "Same build check", ver=R_JS)
rf("CL-C6-PWR-INSTALL-RF", "PA66 M3 installation stress (tension + shank torsion) at the C6 torque 0.08 N m",
   "CALC-C6-PWR-FRAME", "rf_install", PWR, "T-C6-NYLON-TORQUE: 5 PA66 M3x18 into inserts, torque to failure on a "
   "luggage scale; C6 torque <= 0.5 x mean failure torque")
rf("CL-C6-PWR-TENSION-RF", "PA66 screw tension: capacity / (preload + 50 N unplug moment, design)",
   "CALC-C6-PWR-FRAME", "rf_tension", PWR, "T-C6-NYLON-TORQUE; first assembly: pull the AS150U apart 10 times, "
   "witness marks unmoved")
rf("CL-C6-PWR-SLIP-RF", "Power-frame clamp friction / unplug shear (design, full preload)", "CALC-C6-PWR-FRAME",
   "rf_slip", PWR, "First assembly: 10 unplug pulls, frame witness line unmoved")
rf("CL-C6-PWR-SPACER-RF", "Nylon spacer bending if the clamp has crept and slips (guided column)",
   "CALC-C6-PWR-FRAME", "rf_spacer", PWR, "Every 10 flights: frame does not rock by hand; re-snug to 0.08 N m")
rf("CL-C6-INSERT-PULL-RF", "Heat-set insert pull-out / (preload + unplug tension) or crash", "CALC-C6-PWR-FRAME",
   "rf_pull", PWR, "T-C6-INSERT: pull 3 inserts from a boss printed on the 0.8 mm plate bonded to board")
rf("CL-C6-TUBE-BLOCK-RF", "Tube-in-block bond, fin torsion", "CALC-C6-TUBE-BONDS", "rf_tube_block",
   TUBES + BLOCKS, "T-C6-LAP-PETG (allowable) and C4 T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-BLOCK-SPAR-RF", "Block-on-spar bond, torsion about the spar", "CALC-C6-TUBE-BONDS", "rf_block_spar",
   BLOCKS + ["WNG-002"], "T-C6-LAP-PETG and T-C4-BLOCK-PROOF", ver=R_SM + R_FT)
rf("CL-C6-COLLAR-RF", "Station collar bond at the drawn height (22 mm since D-90): max(C1, C4) torsion + brace shear",
   "CALC-C6-TUBE-BONDS", "rf_collar", COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF (1.5 x L4) with the collar "
   "witness-marked", ver=R_SM + R_FT)
_rec("CL-C6-COLLAR-RF-13MM", "Station collar bond at 13 mm (CR-C6-32, D-70); equals the drawn value since D3-R5", "CALC-C6-TUBE-BONDS",
   "rf_collar_min", COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF with the collar witness-marked", ver=R_SM + R_FT)
_rec("CL-C6-COLLAR-RF-16MM", "Station collar bond at the 16 mm fallback (R3 ring), same case", "CALC-C6-TUBE-BONDS",
   "rf_collar_alt", COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF with the collar witness-marked", ver=R_SM + R_FT)
_rec("CL-C6-COLLAR-RF-15MM", "Station collar bond at the drawn height (was 15 mm, CR-C6-36)",
   "CALC-C6-TUBE-BONDS", "rf_collar", COLLARS + TUBES, "T-C6-LAP-PETG; T-C4-FIN-PROOF with the collar witness-marked", ver=R_SM + R_FT)
rf("CL-C6-COLLAR-RF-PROP", "Station collar bond at the C6-R5 proposal (joints.collar_prop_h_m, 22 mm, CR-C6-37), "
   "same case", "CALC-C6-TUBE-BONDS", "rf_collar_prop", COLLARS + TUBES,
   "T-C6-LAP-PETG; T-C4-FIN-PROOF with the collar witness-marked", ver=R_SM + R_FT)
_rec("CL-C6-COLLAR-RF-12MM-COND", "Station collar at 12 mm under the D-70 condition (T-C6-LAP-PETG mean >= 4.1 MPa, "
   "allowable 2.05 MPa), same case", "CALC-C6-TUBE-BONDS", "rf_collar_cond12", COLLARS + TUBES,
   "T-C6-LAP-PETG mean; print 12 mm collars only if this claim passes on the measured allowable", ver=R_SM + R_FT)
kit.claim("CL-C6-COLLAR-L-REQ", "Station collar bond height needed for max(C1, C4) torsion + brace shear",
          calc="CALC-C6-TUBE-BONDS", output="L_collar_req_m", unit="m",
          limit=("<=", "P:fin_detail.station_collar.height_m"), verifies=R_SM + R_FT, parts=COLLARS,
          how="D3 keeps fin_detail.station_collar.height_m >= this; T-C4-FIN-PROOF")
kit.claim("CL-C6-STRIP-ANCHOR-F", "Edge-strip anchor design force per strip (pass line of T-C6-STRIP-ANCHOR, for H1)",
          calc="CALC-C6-STRIP", output="F_design_n", unit="N", verifies=R_SM + R_FT, parts=STRIPS + COLLARS,
          how="H1 sizes the lever frame to >= this (CR-H1-12); C4 FE CL-C4-D3-STRIP-END-F is the source")
rf("CL-C6-STRIP-ANCHOR-RF", "Edge-strip end in the 40 mm two-face collar tail (R3)", "CALC-C6-STRIP",
   "rf_anchor", STRIPS + COLLARS, "T-C6-STRIP-ANCHOR: pull one strip out of a printed tail coupon", ver=R_SM + R_FT)
kit.claim("CL-C6-STRIP-EMBED-REQ", "Edge-strip embedment needed, both faces on PETG", calc="CALC-C6-STRIP",
          output="L_req_m", unit="m", limit=("<=", "P:fin_detail.station_collar.tail_m"), verifies=R_SM + R_FT,
          parts=COLLARS, how="T-C6-STRIP-ANCHOR on the 40 mm two-face tail")
rf("CL-C6-STRIP-TAIL-NET-RF", "Collar tail net section in tension, one strip's force (D3 area estimate)",
   "CALC-C6-STRIP", "rf_tail_net", COLLARS, f"T-C6-STRIP-ANCHOR: the tail must not break before {kit.value('CL-C4-D3-STRIP-END-F'):.0f} N",
   ver=R_SM + R_FT)
kit.claim("CL-C6-STRIP-FACE-RF", "Edge-strip shear flow onto the board paper face if unpinned (why the pins exist; "
          "no limit: R3 carries the pins)", calc="CALC-C6-STRIP", output="rf_face", unit="-", verifies=R_SM,
          parts=STRIPS + HALVES, how="T-C6-BOARD-LAP (allowable); C4 FE CL-C4-D3-STRIP-Q (= C4 MS -0.77)")
rf("CL-C6-STRIP-PIN-RF", "Through-pins as drawn (2.5 mm at 15 mm pitch since D3-R5, D-70) at C4's FE pin force, "
   "weaker of shear and bending (bending bound: reaction at the board mid-plane)", "CALC-C6-STRIP", "rf_pin",
   STRIPS + HALVES, "T-C4-FIN-PROOF with pins fitted; no strip lift at the tip", ver=R_SM)
rf("CL-C6-STRIP-PIN-RF-PROP", "Through-pins 2.5 mm at 15 mm (CR-C6-31); equals the drawn value since D3-R5", "CALC-C6-STRIP",
   "rf_pin_prop", STRIPS + HALVES, "T-C4-FIN-PROOF with 2.5 mm pins fitted", ver=R_SM)
rf("CL-C6-STRIP-PIN-RF-ALT", "Through-pins 2 mm at 9 mm pitch (CR-C6-31 fallback)", "CALC-C6-STRIP", "rf_pin_alt",
   STRIPS + HALVES, "T-C4-FIN-PROOF with pins fitted at 9 mm", ver=R_SM)
kit.claim("CL-C6-STRIP-PIN-PITCH-MAX", "Largest pitch for the drawn 2.5 mm pins at C4's shear flow (bending bound)",
          calc="CALC-C6-STRIP", output="pitch_max_d_m", unit="m",
          limit=(">=", "P:fin_detail.edge_strip.pin_pitch_m"), verifies=R_SM, parts=STRIPS + HALVES,
          how="D3 keeps fin_detail.edge_strip.pin_pitch_m <= this")
kit.claim("CL-C6-STRIP-PIN-PITCH-MAX-ALT", "Largest pitch for 2 mm fallback pins at C4's shear flow (bending bound)",
          calc="CALC-C6-STRIP", output="pitch_max_dalt_m", unit="m",
          limit=(">=", "P:joints.pin_pitch_alt_m"), verifies=R_SM, parts=STRIPS + HALVES,
          how="Only if 2.5 mm rod cannot be bought: 2 mm pins at <= this pitch")
rf("CL-C6-STRIP-PIN-BRG-RF", "Strip bearing on a 2.5 mm pin (CR-C6-31)", "CALC-C6-STRIP", "rf_pin_bearing",
   STRIPS, "T-C4-FIN-PROOF: no strip split at a pin hole", ver=R_SM)
rf("CL-C6-STRIP-NET-PIN-RF", "Strip net section at a 2.5 mm pin hole under the collar-end force", "CALC-C6-STRIP",
   "rf_strip_net_pin", STRIPS, "T-C4-FIN-PROOF", ver=R_SM)
rf("CL-C6-BRACE-END-RF", "Brace ends bonded in the ear and anchor slots", "CALC-C6-BRACE", "rf_end",
   [f"FIN-009-{s}" for s in ST] + COLLARS + [f"FIN-010-{s}" for s in ST], "T-C6-LAP-PETG; T-C4-FIN-PROOF (G2)",
   ver=R_SM + R_FT)
rf("CL-C6-ANCHOR-PULL-RF", "Brace anchor saddle pull-off from the spar", "CALC-C6-BRACE", "rf_anchor",
   [f"FIN-010-{s}" for s in ST] + ["WNG-002"], "T-C4-FIN-PROOF (G2 in tension on the brace)", ver=R_SM + R_FT)
rf("CL-C6-FOOT-SHOE-RF", "Foot shoe bond on the fin tip, 1 350 mm2 at the C6 board allowable (CR-D5-24)",
   "CALC-C6-FOAM-BONDS", "rf_foot", [f"GER-001-{s}" for s in ST] + HALVES, "T-C6-BOARD-LAP; T-C1-FOOT-DROP")
kit.claim("CL-C6-FIN-ROOT-RF", "Half-fin root fillet on XPS at the C6 foam allowable, as drawn (D-92: 10 / 13 mm "
          "cove, no strength credit; record)", calc="CALC-C6-FOAM-BONDS", output="rf_root", unit="-", verifies=R_SM,
          parts=HALVES + ["WNG-001"], how="none: D-92 sizes the fin with the root free (CL-C4-D3-MS-FACE-ROOT-FREE)",
          note="D-92: the fillet carries 0.8 % of the L4 root moment intact (CL-C4-D3-FILLET-L4-SHARE); the 15 mm fail-safe "
               "fillet read RF 0.80 and was withdrawn; the root is a sealing cove")
kit.claim("CL-C6-FIN-ROOT-RF-PROP", "Root fillet at the C6 leg (joints.root_fillet_leg_m), record after D-92",
          calc="CALC-C6-FOAM-BONDS", output="rf_root_prop", unit="-", verifies=R_SM, parts=HALVES + ["WNG-001"],
          how="none (record)")
rf("CL-C6-POD-WING-RF", "Pod shell bond on the core, design envelope (1 / C3 interaction at C6-confirmed allowables)",
   "CALC-C6-POD-ALLOW", "rf_pod_design", ["POD-001", "WNG-001"], "T-C6-XPS-PULL (tension and shear); C3 pod proof")
rf("CL-C6-POD-CRASH-RF", "Pod shell bond on the core, 12.75 g crash", "CALC-C6-POD-ALLOW", "rf_pod_crash",
   ["POD-001", "WNG-001"], "T-C6-XPS-PULL", ver=["R-PACK-RETENTION"])
rf("CL-C6-POD-TRAY-RF", "Tray-to-floor bond flat-wise at the C6 board allowable (0.05 MPa)", "CALC-C6-POD-ALLOW",
   "rf_tray", POD, "T-C6-BOARD-LAP flat-wise pulls", ver=["R-PACK-RETENTION"])
kit.claim("CL-C6-POD-FLOOR-RF", "Floor-to-side-wall glue line under the front strap without the fillet (record: why "
          "the 6 mm fillet exists; no limit since CR-C6-17 was adopted)", calc="CALC-C6-POD-ALLOW", output="rf_floor",
          unit="-", verifies=["R-PACK-RETENTION"], parts=["POD-001"],
          how="T-C6-BOARD-CORNER: strap pull on a board corner coupon without the fillet")
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
kit.claim("CL-C6-FIN-LOAD-SCALE", "C1 D-65 half-fin torsion / torsion of C4's frozen R4 fin set (how stale C4's set is)",
          calc="CALC-C6-FIN-SCALE", output="k", unit="-", verifies=R_SM, parts=STRIPS + COLLARS,
          how="C4 re-runs fin_structures_d3.py / sim_fin.py on the D-65 side load; then k = 1 and the -EST claims retire")
rf("CL-C6-STRIP-ANCHOR-RF-EST", "Edge-strip anchor in the 40 mm tail at C4's force scaled by k (estimate)",
   "CALC-C6-FIN-SCALE", "rf_anchor", STRIPS + COLLARS, "C4 re-run; T-C6-STRIP-ANCHOR", ver=R_SM + R_FT)
rf("CL-C6-STRIP-TAIL-NET-RF-EST", "Collar tail net section at C4's force scaled by k (estimate)", "CALC-C6-FIN-SCALE",
   "rf_tail_net", COLLARS, "C4 re-run; T-C6-STRIP-ANCHOR", ver=R_SM + R_FT)
rf("CL-C6-STRIP-PIN-RF-EST", "Drawn 2.5 mm pins at 15 mm at C4's pin force scaled by k (estimate)", "CALC-C6-FIN-SCALE",
   "rf_pin", STRIPS + HALVES, "C4 re-run; T-C4-FIN-PROOF", ver=R_SM)
kit.claim("CL-C6-STRIP-PIN-PITCH-MAX-EST", "Largest 2.5 mm pin pitch at C4's pin force scaled by k (estimate)",
          calc="CALC-C6-FIN-SCALE", output="pitch_max_m", unit="m", limit=(">=", "P:fin_detail.edge_strip.pin_pitch_m"),
          verifies=R_SM, parts=STRIPS + HALVES, how="C4 re-run; D3 holds the pin drilling until then")
kit.claim("CL-C6-STRIP-ANCHOR-F-EST", "Edge-strip anchor design force scaled by k (estimate; H1 frame >= 1.25 x)",
          calc="CALC-C6-FIN-SCALE", output="F_strip_n", unit="N", verifies=R_SM + R_FT, parts=STRIPS + COLLARS,
          how="H1 builds the T-C6-STRIP-ANCHOR frame to 1.25 x this until C4 re-runs")
kit.claim("CL-C6-POCKET-WALL-AREA-RATIO", "Block-pocket wall bond area with R 3 mm vertical edges / square block (D-68)",
          calc="CALC-C6-BLOCK-POCKET", output="wall_area_ratio", unit="-", verifies=R_SM, parts=BLOCKS + ["WNG-001"],
          how="Geometry; no C6 RF credits the wall bond (the bore bonds carry the block), so the 2.5 % loss changes "
              "no C6 margin")
kit.claim("CL-C6-POCKET-SQUARE-GAP", "Corner void if the pocket is left square round the R 3 mm block",
          calc="CALC-C6-BLOCK-POCKET", output="gap_square_m", unit="m", verifies=R_SM, parts=BLOCKS + ["WNG-001"],
          how="Record (no limit): 1.24 mm > the 0.5 mm bond line, so a square-cut pocket is not accepted; D1 cuts "
              "R 3.0-4.2 mm corners (CL-C6-POCKET-R-MAX) or packs the corners with microballoon mix before the block")
kit.claim("CL-C6-POCKET-R-MAX", "Largest pocket corner radius that keeps the corner gap within the bond line",
          calc="CALC-C6-BLOCK-POCKET", output="Rp_max_m", unit="m", limit=(">=", "P:fin_detail.block.edge_r_m"),
          verifies=R_SM, parts=BLOCKS + ["WNG-001"],
          how="D1 corner template between R 3.0 and this; dry-fit with the feeler before bonding")
kit.claim("CL-C6-POCKET-BEAD-MASS", "Microballoon beads along the pocket edges, both surfaces, two blocks (D-68)",
          calc="CALC-C6-BLOCK-POCKET", output="bead_mass_g", unit="g", verifies=R_SM, parts=BLOCKS + ["WNG-001"],
          how="Weigh the mix used (T-D3-WEIGH density); inside the wing's 18 g cushion (D-68)")
kit.claim("CL-C6-SNAP-L-MIN", "Foot snap-hook finger length for 2 % strain", calc="CALC-C6-SNAP", output="value",
          unit="m", verifies=R_JS, parts=[f"GER-002-{s}" for s in ST],
          how="D5 shows the free finger length >= this in the CAD; 20 insert swaps on one printed piston, no crack")

# ----------------------------------------------------------------------------- tests (H1 runs them with the first prints)
kit.test("T-C6-LAP-PETG", "Epoxy lap shear on abraded PETG, ASA and CF",
         ["CL-C6-TUBE-BLOCK-RF", "CL-C6-BLOCK-SPAR-RF", "CL-C6-COLLAR-RF", "CL-C6-COLLAR-RF-13MM", "CL-C6-COLLAR-RF-16MM",
          "CL-C6-COLLAR-RF-12MM-COND", "CL-C6-COLLAR-RF-15MM", "CL-C6-COLLAR-RF-PROP",
          "CL-C6-BRACE-END-RF", "CL-C6-STRIP-ANCHOR-RF"],
         procedure="5 single-lap coupons each: PETG-CF and ASA-CF tube offcut, 25 x 12.5 mm overlap, 120 grit + "
                   "IPA, 30 min epoxy, 24 h cure (+ 4 h at 50 degC for the ASA set); hang water jugs on a luggage "
                   "scale to failure. Allowable = mean x 0.5; pass >= 2.0 MPa (ASM-C4-BOND-SHEAR); >= 4.1 MPa mean releases the 12 mm collar (D-70)")
kit.test("T-C6-BOARD-LAP", "Epoxy on paper-faced foam board, shear and flat-wise",
         ["CL-C6-FOOT-SHOE-RF", "CL-C6-STRIP-FACE-RF", "CL-C6-POD-TRAY-RF"],
         procedure="5 PETG tabs 20 x 20 mm bonded on a scuffed board face pulled in shear, 5 pulled flat-wise; "
                   "record the failure mode (paper peels vs epoxy). Allowables = 0.5 x mean (replace ASM-D5-BOND-TAU "
                   "x KD and ASM-C6-BOARD-FLAT-TYP x KD)")
kit.test("T-C6-XPS-PULL", "Flat-wise pull and shear of epoxy pucks on XPS",
         ["CL-C6-FIN-ROOT-RF", "CL-C6-FIN-ROOT-RF-PROP", "CL-C6-POD-WING-RF", "CL-C6-POD-CRASH-RF", "CL-C6-LINK-BOND-AREA-MIN"],
         procedure="10 printed pucks 30 mm dia bonded with microballoon epoxy on hot-wire-cut F-250 offcut: 5 pulled "
                   "normal to the face, 5 pushed sideways; allowables = 0.5 x mean (replace ASM-D3-XPS-TENSILE and "
                   "ASM-C6-XPS-SHEAR-TYP x KD)")
kit.test("T-C6-BOARD-CORNER", "Pod floor-to-wall corner under a strap pull", ["CL-C6-POD-FLOOR-RF",
                                                                               "CL-C6-POD-FLOOR-RF-PROP"],
         procedure="Two 100 mm long board U-sections (floor + two walls) glued edge-to-face as D2 builds the pod, "
                   "one with the 6 mm fillets; pull a 20 mm strap off the floor with water jugs; pass >= 43 N (C3 "
                   "per-strap design load: 85 N crash / 2 straps)")
kit.test("T-C6-INSERT", "Heat-set insert pull-out", ["CL-C6-INSERT-PULL-RF"],
         procedure="3 inserts in 7 mm bosses printed on a 0.8 mm plate as POD-002 (same settings), plate bonded to a "
                   "foam-board offcut; steel M3 screw + washer, pull to failure; pass >= 300 N each or, if the plate "
                   "peels off the board first, record that load for D2 (unplug moment path, CR-C6-27)")
kit.test("T-C6-NYLON-TORQUE", "PA66 M3x18 torque to failure in a brass insert",
         ["CL-C6-PWR-INSTALL-RF", "CL-C6-PWR-TENSION-RF"],
         procedure="5 PA66 M3x18 from the bought batch through a 12.5 mm nylon/PETG stack into an insert; hex key + "
                   "luggage scale 50 mm out, raise slowly to failure; pass: mean failure torque >= 2 x 0.08 N m "
                   "(>= 3.2 N on the scale). Repeat one at 0.08 N m, 48 h, re-check breakaway >= 0.04 N m (creep)")
kit.test("T-C6-HEAD-CREEP", "Motor screw creep on a hot printed plate", ["CL-C6-MOTOR-HEAD-RF"],
         procedure="Printed ASA mount plate on an aluminium block with 4 x M3x8 at 0.20 N m, "
                   "2 h at 70 degC (oven), cool, breakaway torque >= 0.15 N m on all four")
kit.test("T-C6-CANT-SEAT", "Motor screws on the 7 deg canted mount", ["CL-C6-CANT-ENGAGE", "CL-C6-MOTOR-STRIP-RF"],
         procedure="First printed mount A, holes drilled square to the canted face to the motor's pattern; fit the "
                   "motor; 4 x M3x8 at 0.20 N m; count turns from first bite (>= 6 = 3.0 mm, <= probed depth - 0.5) "
                   "and check a 0.05 mm feeler does not enter under any head")
kit.test("T-C6-STRIP-ANCHOR", "Edge-strip pull-out from the collar tail",
         ["CL-C6-STRIP-ANCHOR-F", "CL-C6-STRIP-ANCHOR-RF", "CL-C6-STRIP-EMBED-REQ", "CL-C6-STRIP-TAIL-NET-RF"],
         procedure="Print the 40 mm two-face station collar (ring + tail) alone; bond a 10 x 1 strip pair in it as "
                   "built (board offcut as the tongue spacer); pull ONE strip along its axis on H1's lever frame "
                   f"with the ring held on a 22 mm mandrel; pass >= CL-C6-STRIP-ANCHOR-F "
                   f"({kit.value('CL-C4-D3-STRIP-END-F'):.0f} N) with neither the bond "
                   "nor the tail failing. Record the failure mode")
kit.test("T-C6-PROPNUT", "Prop-nut torque on a finished mount", ["CL-C6-MOUNT-ROCK-RF", "CL-C6-MOUNT-HOOP-RF"],
         procedure="Bell held by hand, prop nut to 1.5 N m and off 10 times; collar witness line and lip cap unmoved")

if __name__ == "__main__":
    kit.write()
