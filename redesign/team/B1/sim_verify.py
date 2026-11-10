"""B1 verification round: whole-aircraft performance on the as-designed geometry and masses, with the drag and lift
taken from the simulations instead of the rev 3 hand estimates.

Inputs
  as-designed mass and CG   A3 roll-up claims CL-A3-MASS-BASIC (2.322 kg), CL-A3-MASS-PREDICTED (2.436 kg, growth
                            included), CL-A3-CG-X-PRED; the 2.6 kg gate is kept as the upper bound.
  wing                      AVL (trimmed, A3 CG, wing + fins) + XFOIL strip profile drag: P:b1sim.wing.* / .avl.*
                            (team/B1/vlm_xfoil.py), fitted CD_wing = A + K CL^2 over CL 0.3-0.7.
  fins and motor tubes      SU2 2-D RANS section drag (team/B1/cfd_sections.py): P:b1sim.cfd.fin_a_cd (tube +
                            board) over the tube length, fin_b_cd (bare board) over the rest of the fin height.
  everything else           unchanged rev 3 build-up (motors, pod, pod front, braces, collars, interference factor,
                            tape-seam factor) and the rev 3 prop/motor chain (performance.py helpers).
  fixed-wing rpm            F4's THR_MAX 70 % (CL-F4-FW-RPM-CAP, 7 749 rpm fresh pack).
Every calculation is a pure function of its named inputs and reuses the helpers in performance.py.

Run (after cfd_sections.py, vlm_xfoil.py, sim_to_params.py):  python -I redesign/team/B1/sim_verify.py
Writes claims.verify.json, sim/sim_verify_results.json and the FIG B1-03 ... B1-06 SVGs.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
sys.path.insert(0, str(HERE))
import proofkit as pk  # noqa: E402
import performance as perf  # noqa: E402  (pure helpers; its own Kit is not written)

kit = pk.Kit(__file__, params=["../../params/params.json", "../B2/params.json", "params.json"],
             out="claims.verify.json")
P = "P:"
DEG = math.pi / 180.0

kit.source("SRC-B1-SIM-CFD", "B1 2-D RANS runs of the fin and wing sections (SU2 8.5, SA)", "file",
           where="team/B1/sim/cfd/<case>_L<1-3>/ (case.cfg, history.csv, surface_flow.csv, su2.log); "
                 "summary sim/cfd/cfd_results.json; script team/B1/cfd_sections.py",
           note="three grids per section, refinement ratio sqrt(2) in every size; GCI after Celik et al. 2008")
kit.source("SRC-B1-SIM-VLMXF", "B1 AVL + XFOIL runs on the as-designed wing", "file",
           where="team/B1/sim/vlm_xfoil/ (AVL decks, FT/FS/ST files, XFOIL polars); summary "
                 "sim/vlm_xfoil_results.json; script team/B1/vlm_xfoil.py",
           note="AVL 3 lattices, XFOIL 160/240/320 panels")
kit.assumption("ASM-B1V-CFD-2D", "Fin drag from 2-D section RANS",
               "Each fin's zero-lift drag is the SU2 2-D section Cd (fully turbulent SA, 16 m/s) times its chord, "
               "over the tube length for the tube + board section and over the rest of the fin height for the bare "
               "board; the rev 3 interference factor 1.15 is kept on top for the root and tip junctions",
               basis="the board edges are square (laser- or knife-cut foam board, fins SPEC) and trip the boundary "
                     "layer, so fully turbulent SA is the right model on the fins; tip and root 3-D effects are small "
                     "at h/c 0.76 per half-fin and stay inside the 1.15 factor; 3 mm epoxy fillet at the tube-board "
                     "joint (fins.fin.le_gap_m filled), board edges sharp. Re 3.0e5",
               value=[1.15], unit="-", status="PROPOSED", cites=["SRC-B1-SIM-CFD"])
kit.assumption("ASM-B1V-LIGHT-PACK", "Lightest flying mass below the A3 basic mass",
               "The lightest flying configuration is the A3 basic mass with the 503 g pack instead of the 550 g pack, "
               "47 g lighter; it sets the hover wind lean and the parked tip-over wind",
               basis="team/A3/rollup/rollup.json pack_cases 503/550 (A3-R6a)", value=47.0, unit="g",
               status="PROPOSED")


# ------------------------------------------------------------------ calculations
@kit.calc("CALC-B1V-AERO", title="As-designed drag polar from AVL + XFOIL (wing) and SU2 (fins)",
          equation="CD0 = IF [A_fit f_rough + n_f c_f (Cd_A L_tube + Cd_B (2 h_f - L_tube)) + n CdA_m + pod + pod_front "
                   "+ braces + collars] / S ; k = K_fit (AVL CDi + XFOIL lift-dependent profile, trimmed) ; "
                   "k_pess = 1/(pi AR e_params) ; alpha0_trim = alpha_cruise - CL_cruise / CLa",
          inputs={"b": P + "wing.span_m", "c": P + "wing.chord_m", "tc": P + "wing.t_c", "e_pess": P + "wing.oswald_e",
                  "a_fit": P + "b1sim.wing.cd0_fit", "k_fit": P + "b1sim.wing.k_fit", "rough": "ASM-B1-WING-ROUGH",
                  "cla": P + "b1sim.avl.cla_per_rad", "a_cr": P + "b1sim.avl.alpha_cruise_deg",
                  "m": "CL-A3-MASS-PREDICTED", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "vc": "ASM-B1-VCRUISE", "cd_a": P + "b1sim.cfd.fin_a_cd", "cd_b": P + "b1sim.cfd.fin_b_cd",
                  "fin_h": P + "fins.half_height_m", "fin_c": P + "fins.chord_m", "tube_l": P + "fins.tube.length_m",
                  "tube_d": P + "fins.tube.od_m", "pod": P + "pod.size_m", "n": P + "propulsion.n_motors",
                  "drag": "ASM-B1-DRAG", "addons": "ASM-B1-DRAG-ADDONS", "podf": "ASM-B1-POD-FRONT",
                  "clmax": "CL-B1V-CLMAX", "cd0_hand": "CL-B1-CD0", "k_hand": "CL-B1-K"},
          units={"b": "m", "c": "m", "fin_h": "m", "fin_c": "m", "tube_l": "m", "tube_d": "m", "pod": "m",
                 "cla": "1/rad", "a_cr": "deg", "m": "kg", "g": "m/s2", "rho": "kg/m3", "vc": "m/s"},
          assumes=["ASM-B1V-CFD-2D", "ASM-B1-DRAG", "ASM-B1-WING-ROUGH", "ASM-B1-DRAG-ADDONS", "ASM-B1-POD-FRONT"],
          cites=["SRC-B1-SIM-CFD", "SRC-B1-SIM-VLMXF"])
def aero_asdesigned(b, c, tc, e_pess, a_fit, k_fit, rough, cla, a_cr, m, g, rho, vc, cd_a, cd_b, fin_h, fin_c, tube_l,
                    tube_d, pod, n, drag, addons, podf, clmax, cd0_hand, k_hand):
    cf_b, ff_f, cd_tube, cda_m, ff_pod, interf = drag
    nb, lb, wb, cdb, nc, dc, hc, cdc = addons
    cd_front, w_ref = podf
    S = b * c
    AR = b * b / S
    tl = min(tube_l, 2 * fin_h)
    parts = {
        "wing": a_fit * rough,
        "fins_and_tubes": 2 * fin_c * (cd_a * tl + cd_b * (2 * fin_h - tl)) / S,
        "motors": n * cda_m / S,
        "pod": cf_b * ff_pod * 2 * (pod[0] * pod[1] + pod[0] * pod[2] + pod[1] * pod[2]) / S,
        "pod_front": cd_front * max(0.0, pod[1] - w_ref) * pod[2] / S,
        "braces": nb * cdb * wb * lb / S,
        "collars": nc * (cdc * dc - cd_tube * tube_d) * hc / S,
    }
    hand_fins = cf_b * ff_f * 2.0 * (1.0 + 0.2 * tc) * (2 * 2 * fin_h * fin_c) / S + 2 * cd_tube * tube_d * tube_l / S
    cd0 = interf * sum(parts.values())
    cl_cr = 2 * m * g / (rho * vc * vc * S)
    return {"cd0": cd0, "k": k_fit, "k_pess": 1.0 / (math.pi * AR * e_pess), "e_equiv": 1 / (math.pi * AR * k_fit),
            "cd0_parts": [round(interf * parts[p], 6) for p in parts], "cd0_parts_names": list(parts),
            "fins_cd0_hand": interf * hand_fins, "fins_cd0_sim": interf * parts["fins_and_tubes"],
            "fins_ratio_sim_hand": parts["fins_and_tubes"] / hand_fins,
            "d_cd0_vs_hand_pct": 100 * (cd0 / cd0_hand - 1), "d_k_vs_hand_pct": 100 * (k_fit / k_hand - 1),
            "cla_per_rad": cla, "alpha0_trim_deg": a_cr - cl_cr / cla / DEG,
            "alpha_stall_deg": a_cr - cl_cr / cla / DEG + clmax / cla / DEG,
            "ld_max": 1 / (2 * math.sqrt(cd0 * k_fit)), "cl_cruise_pred": cl_cr}


@kit.calc("CALC-B1V-STALL", title="Stall and transition speeds, as designed",
          equation="SM = (Xnp_B2 - x_cg,A3)/c ; CLmax_B2 = interp(SM, B2 CLmax(SM)) ; CLmax = min(CLmax_B1 sim, CLmax_B2) ; "
                   "Vs = sqrt(2 m g/(rho S CLmax)) at m_basic, m_pred, m_gate ; Vt = 1.3 Vs",
          inputs={"m_b": "CL-A3-MASS-BASIC", "m_p": "CL-A3-MASS-PREDICTED", "m_g": P + "requirements.mtow_gate_kg",
                  "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA",
                  "cl_sim": P + "b1sim.wing.clmax_trim", "tab": P + "b2.avl.clmax_vs_sm", "xnp": P + "b2.avl.xnp_m",
                  "xcg": "CL-A3-CG-X-PRED", "c": P + "wing.chord_m", "kt": P + "requirements.transition_factor",
                  "vs_hand": "CL-B1-VS-GATE"},
          units={"m_b": "kg", "m_p": "kg", "m_g": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "xnp": "m",
                 "xcg": "m", "c": "m", "vs_hand": "m/s"},
          cites=["SRC-B1-SIM-VLMXF", "SRC-B2-AVL"])
def stall_asdesigned(m_b, m_p, m_g, g, rho, S, cl_sim, tab, xnp, xcg, c, kt, vs_hand):
    sm = (xnp - xcg) / c
    xs, ys = [r[0] for r in tab], [r[1] for r in tab]
    i = max(j for j in range(len(xs) - 1) if xs[j] <= sm or j == 0)
    cl_b2 = ys[i] + (ys[i + 1] - ys[i]) * (sm - xs[i]) / (xs[i + 1] - xs[i])
    clmax = min(cl_sim, cl_b2)
    vs = lambda m: math.sqrt(2 * m * g / (rho * S * clmax))
    return {"sm_a3": sm, "clmax_b2_at_a3": cl_b2, "clmax_sim": cl_sim, "clmax": clmax,
            "vs_basic_ms": vs(m_b), "vs_pred_ms": vs(m_p), "vs_gate_ms": vs(m_g), "vt_pred_ms": kt * vs(m_p),
            "vt_gate_ms": kt * vs(m_g), "d_vs_gate_vs_hand_pct": 100 * (vs(m_g) / vs_hand - 1),
            "vs_gate_sim_clmax_ms": math.sqrt(2 * m_g * g / (rho * S * cl_sim))}


HOVER_IN = {"table": P + "propulsion.thrust_table_g_w", "dl": P + "propulsion.download_factor",
            "n": P + "propulsion.n_motors", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W", "E": P + "battery.energy_wh",
            "v": P + "battery.v_nom", "res": P + "requirements.energy_reserve_frac",
            "t_max_kg": P + "propulsion.thrust_max_per_motor_kg", "sag": P + "propulsion.voltage_sag",
            "pess": "ASM-B1-PESS", "tab": "ASM-B1-PROP", "tab_ref": "ASM-B1-PROP-REF", "kv": "ASM-E1-KV",
            "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "D": P + "propulsion.prop_diameter_m", "rho": P + "env.rho_kgm3",
            "g": P + "env.g_ms2"}
HOVER_UNITS = {"av": "W", "E": "Wh", "v": "V", "t_max_kg": "kg", "D": "m", "rho": "kg/m3", "g": "m/s2"}


@kit.calc("CALC-B1V-HOVER", title="Hover at the as-designed mass, canted motors",
          equation="m_eff = m / cos(cant) ; P, I, throttle, T/W as CALC-B1-HOVER at m_eff ; "
                   "T/W fresh = n T_max cos(cant) / (m g DL)",
          inputs={"m_p": "CL-A3-MASS-PREDICTED", "m_b": "CL-A3-MASS-BASIC", "m_g": P + "requirements.mtow_gate_kg",
                  "cant": P + "propulsion.stations.cant_deg", **HOVER_IN},
          units={"m_p": "kg", "m_b": "kg", "m_g": "kg", "cant": "deg", **HOVER_UNITS},
          assumes=["ASM-B1-ESC", "ASM-B1-AVIONICS-W", "ASM-B1-PESS"])
def hover_asdesigned(m_p, m_b, m_g, cant, table, dl, n, esc, av, E, v, res, t_max_kg, sag, pess, tab, tab_ref, kv,
                     rm, i0, D, rho, g):
    cc = math.cos(cant * DEG)
    h = perf.hover(m_p / cc, m_b / cc, table, dl, n, esc, av, E, v, res, t_max_kg, sag, pess, tab, tab_ref, kv, rm,
                   i0, D, rho, g)
    hg = perf.hover(m_g / cc, m_g / cc, table, dl, n, esc, av, E, v, res, t_max_kg, sag, pess, tab, tab_ref, kv, rm,
                    i0, D, rho, g)
    return {"p_pred_w": h["p_gate_w"], "p_basic_w": h["p_sized_w"], "p_pred_pess_w": h["p_gate_pess_w"],
            "i_pred_a": h["i_gate_a"], "p_gate_cant_w": hg["p_gate_w"],
            "throttle_pred_sag": h["throttle_frac_gate_sag"], "tw_pred_sag": h["tw_gate_sag_download"],
            "tw_pred_fresh": n * t_max_kg * cc / (m_p * dl), "throttle_gate_sag": hg["throttle_frac_gate_sag"],
            "hover_only_pred_min": h["hover_only_gate_min"]}


CR_IN = {"g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA", "cd0": "CL-B1V-CD0",
         "k": "CL-B1V-K", "k_pess": "CL-B1-K-PESS", "trim": "ASM-B1-TRIM", "n": P + "propulsion.n_motors",
         "tab": "ASM-B1-PROP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "kcal": "CL-B1-KCAL",
         "D": P + "propulsion.prop_diameter_m", "esc": "ASM-B1-ESC", "av": "ASM-B1-AVIONICS-W"}
CR_UNITS = {"g": "m/s2", "rho": "kg/m3", "S": "m2", "D": "m", "av": "W"}


@kit.calc("CALC-B1V-CRUISE", title="Cruise at 16 m/s, as-designed mass and drag",
          equation="as CALC-B1-CRUISE with m = A3 predicted, CD0 and k from CALC-B1V-AERO ; also at the 2.6 kg gate ; "
                   "sweep 14-20 m/s",
          inputs={"m": "CL-A3-MASS-PREDICTED", "m_g": P + "requirements.mtow_gate_kg", **CR_IN,
                  "vc": "ASM-B1-VCRUISE", "pess": "ASM-B1-PESS", "v": P + "battery.v_nom"},
          units={"m": "kg", "m_g": "kg", **CR_UNITS, "vc": "m/s", "v": "V"},
          assumes=["ASM-B1-TRIM", "ASM-B1-PESS", "ASM-B1-VCRUISE"])
def cruise_asdesigned(m, m_g, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, pess, v):
    c = perf.cruise(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, pess, v)
    cg_ = perf.cruise(m_g, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, pess, v)
    motor = (kv, rm, i0)
    rows = []
    for v10 in range(140, 201, 5):
        V = v10 / 10
        b_ = perf.cruise_point(V, m, g, rho, S, cd0, k, trim, n, tab, motor, kcal, D, esc, av)
        w_ = perf.cruise_point(V, m, g, rho, S, cd0 * pess[0], k_pess, trim, n, tab, motor, kcal, D, esc, av, pess[1])
        rows.append([V, round(b_["p_el_w"], 1), round(w_["p_el_w"], 1), round(b_["drag_n"], 3)])
    return {"p_el_w": c["p_el_w"], "p_el_pess_w": c["p_el_pess_w"], "drag_n": c["drag_n"], "ld": c["ld"],
            "i_a": c["i_a"], "rpm": c["rpm"], "eta_prop": c["eta_prop"], "p_el_gate_w": cg_["p_el_w"],
            "drag_gate_n": cg_["drag_n"], "rows_V_P_Ppess_D": rows}


@kit.calc("CALC-B1V-TRANSITION", title="Corridor and pitch-over, as designed",
          equation="CALC-B1-CORRIDOR and CALC-B1-PITCHOVER with m = A3 predicted, CLa, trimmed alpha0, CLmax_trim, "
                   "CD0, k as designed; Vs from CALC-B1V-STALL",
          inputs={"m": "CL-A3-MASS-PREDICTED", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA",
                  "cla": P + "b1sim.avl.cla_per_rad", "a0": "CL-B1V-ALPHA0-TRIM", "clmax": "CL-B1V-CLMAX",
                  "cd0": "CL-B1V-CD0", "k": "CL-B1V-K", "cd90": "ASM-B1-CD90", "n": P + "propulsion.n_motors",
                  "tab": "ASM-B1-PROP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "kcal": "CL-B1-KCAL",
                  "nmax": "CL-B1-NMAX-SAG", "D": P + "propulsion.prop_diameter_m", "esc": "ASM-B1-ESC",
                  "av": "ASM-B1-AVIONICS-W", "frac": "ASM-B1-CTRL-RESERVE", "trans": "ASM-B1-TRANS",
                  "vs": "CL-B1V-VS-PRED", "vc": "ASM-B1-VCRUISE", "kt": P + "requirements.transition_factor",
                  "dl": P + "propulsion.download_factor"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2", "cla": "1/rad", "a0": "deg", "D": "m", "av": "W",
                 "nmax": "rev/s", "vs": "m/s", "vc": "m/s"},
          assumes=["ASM-B1-TRANS", "ASM-B1-CD90", "ASM-B1-CTRL-RESERVE"])
def transition_asdesigned(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av, frac,
                          trans, vs, vc, kt, dl):
    po = perf.simulate_pitchover(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc,
                                 av, frac, trans, vs, vc, kt)
    co = perf.corridor(m, g, rho, S, cla, a0, clmax, cd0, k, cd90, n, tab, kv, rm, i0, kcal, nmax, D, esc, av, frac,
                       dl, vc)
    s = po["summary"]
    return {"t_to_vt_s": s["t_to_vt_s"], "alt_loss_m": s["alt_loss_m"], "thrust_frac_max": s["thrust_frac_max"],
            "energy_wh": s["energy_wh"], "corr_thrust_frac_max": co["thrust_frac_max"], "corr_p_peak_w": co["p_peak_w"],
            "v_wingborne_ms": co["v_wing_unstalled_ms"], "corridor_rows": co["rows_V_th_thlo_TW_Tfrac_P_stalled"]}


@kit.calc("CALC-B1V-MISSION", title="Mission: 2 min hover, two transitions, cruise; as designed",
          equation="E_c = E (1 - res) - P_h t_h - E_tr (1 + back) ; t = E_c / P_cruise ; "
                   "pess: (P_h t_h + E_tr (1 + back)) x 1.10 and P_cruise,pess",
          inputs={"E": P + "battery.energy_wh", "res": P + "requirements.energy_reserve_frac",
                  "p_h": "CL-B1V-HOVER-P", "t_h": P + "requirements.hover_time_min", "e_tr": "CL-B1V-TRANS-ENERGY",
                  "trans": "ASM-B1-TRANS", "p_c": "CL-B1V-CRUISE-P", "p_cp": "CL-B1V-CRUISE-P-PESS",
                  "pess": "ASM-B1-PESS", "vc": "ASM-B1-VCRUISE", "t_hand": "CL-B1-CRUISE-TIME"},
          units={"E": "Wh", "p_h": "W", "t_h": "min", "e_tr": "Wh", "p_c": "W", "p_cp": "W", "vc": "m/s",
                 "t_hand": "min"},
          assumes=["ASM-B1-TRANS", "ASM-B1-PESS"])
def mission_asdesigned(E, res, p_h, t_h, e_tr, trans, p_c, p_cp, pess, vc, t_hand):
    use = E * (1 - res)
    fixed = p_h * t_h / 60 + e_tr * (1 + trans[2])
    t = (use - fixed) / p_c * 60
    return {"t_cruise_min": t, "t_cruise_pess_min": (use - fixed * pess[2]) / p_cp * 60, "e_cruise_wh": use - fixed,
            "range_km": t * 60 * vc / 1000, "d_t_vs_hand_pct": 100 * (t / t_hand - 1)}


@kit.calc("CALC-B1V-SPEED", title="Top level speed at F4's fixed-wing throttle cap and FW climb, as designed",
          equation="CALC-B1-CLIMB with m = A3 predicted, as-designed CD0 and k, rpm cap = CL-F4-FW-RPM-CAP (THR_MAX 70 %) ; "
                   "VH / (VD / 1.25) <= 1 ; also at the 9 350 rpm VTOL cap",
          inputs={"m": "CL-A3-MASS-PREDICTED", **CR_IN, "vc": "ASM-B1-VCRUISE", "frac": "ASM-B1-CTRL-RESERVE",
                  "dl": P + "propulsion.download_factor", "rpm_fw": "CL-F4-FW-RPM-CAP", "rpm_cap": P + "propulsion.rpm_max",
                  "i_lim": P + "propulsion.current_max_per_motor_a", "vterm": "ASM-B1-VTERM", "pess": "ASM-B1-PESS",
                  "vd": P + "requirements.vd_ms"},
          units={"m": "kg", **CR_UNITS, "vc": "m/s", "rpm_fw": "rpm", "rpm_cap": "rpm", "i_lim": "A", "vterm": "V",
                 "vd": "m/s"},
          assumes=["ASM-B1-VTERM", "ASM-B1-CTRL-RESERVE", "ASM-B1-PESS"])
def speed_asdesigned(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, frac, dl, rpm_fw,
                     rpm_cap, i_lim, vterm, pess, vd):
    fw = perf.climb(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, 1.0, dl, rpm_fw,
                    i_lim, vterm, pess)
    vt = perf.climb(m, g, rho, S, cd0, k, k_pess, trim, n, tab, kv, rm, i0, kcal, D, esc, av, vc, frac, dl, rpm_cap,
                    i_lim, vterm, pess)
    return {"vh_fw_cap_ms": fw["v_max_level_ms"], "vh_ratio_vd": fw["v_max_level_ms"] * 1.25 / vd,
            "vmax_fw_sag_ms": fw["v_max_sag_ms"], "roc_fw_cap_ms": fw["roc_fw_max_ms"],
            "vh_vtol_cap_ms": vt["v_max_level_ms"], "vh_nocap_ms": vt["v_max_nocap_ms"],
            "p_vclimb_w": vt["p_vclimb_2p5_w"]}


@kit.calc("CALC-B1V-WIND", title="Wind limits at the lightest flying mass",
          equation="CALC-B1-WIND with m = A3 basic - 47 g (503 g pack): lean = atan(q S CD90 / W) ; "
                   "tip-over wind with m_min = the same mass",
          inputs={"m_b": "CL-A3-MASS-BASIC", "light": "ASM-B1V-LIGHT-PACK", "g": P + "env.g_ms2",
                  "rho": P + "env.rho_kgm3", "S": "CL-A1-WING-AREA", "cd90": "ASM-B1-CD90", "tip": "CL-A1-TIPOVER",
                  "err": "ASM-B1-LAND-ERR", "z_fin": P + "fins.half_height_m", "c": P + "wing.chord_m",
                  "foot": P + "cg.foot_height_m", "tw_sag": "CL-B1V-HOVER-TW-SAG", "frac": "ASM-B1-CTRL-RESERVE",
                  "vw": P + "requirements.wind_limit_ms", "vg": P + "requirements.gust_survive_ms",
                  "vc": "ASM-B1-VCRUISE"},
          units={"m_b": "kg", "light": "g", "g": "m/s2", "rho": "kg/m3", "S": "m2", "tip": "deg", "err": "deg",
                 "z_fin": "m", "c": "m", "foot": "m", "vw": "m/s", "vg": "m/s", "vc": "m/s"},
          assumes=["ASM-B1V-LIGHT-PACK", "ASM-B1-CD90", "ASM-B1-LAND-ERR"])
def wind_asdesigned(m_b, light, g, rho, S, cd90, tip, err, z_fin, c, foot, tw_sag, frac, vw, vg, vc):
    m = m_b - light / 1000.0
    w = perf.wind(m, m, 0.0, g, rho, S, cd90, tip, err, z_fin, c, foot, tw_sag, frac, vw, vg, vc)
    return {"m_light_kg": m, "lean_5ms_deg": w["lean_5ms_deg"], "lean_allowed_deg": w["lean_allowed_deg"],
            "v_hover_max_ms": w["v_hover_max_ms"], "thrust_frac_8ms": w["thrust_frac_8ms"],
            "v_ground_tip_ms": w["v_ground_tip_ms"]}


@kit.calc("CALC-B1V-CONV", title="Numerical uncertainty of the simulations",
          equation="GCI_fine (Celik 2008, Fs 1.25) for SU2 cd ; 3-level spread for AVL e and XFOIL cd ; "
                   "SU2 SA vs XFOIL tripped S5010 cd at alpha 2.5 deg",
          inputs={"ga": P + "b1sim.cfd.fin_a_gci_pct", "gb": P + "b1sim.cfd.fin_b_gci_pct",
                  "gw": P + "b1sim.cfd.s5010_gci_pct", "avl": P + "b1sim.avl.lattice_spread_pct",
                  "xf": P + "b1sim.xfoil.panel_spread_pct", "cd_su2": P + "b1sim.cfd.s5010_cd_sa",
                  "cd_trip": P + "b1sim.xfoil.cd_trip_a2p5", "cd_free": P + "b1sim.xfoil.cd_free_a2p5",
                  "cl_su2": P + "b1sim.cfd.s5010_cl_sa", "cl_trip": P + "b1sim.xfoil.cl_trip_a2p5"},
          units={"ga": "%", "gb": "%", "gw": "%", "avl": "%", "xf": "%"}, cites=["SRC-B1-SIM-CFD", "SRC-B1-SIM-VLMXF"])
def convergence(ga, gb, gw, avl, xf, cd_su2, cd_trip, cd_free, cl_su2, cl_trip):
    return {"gci_max_pct": max(ga, gb, gw), "avl_spread_pct": avl, "xfoil_spread_pct": xf,
            "su2_vs_xfoil_trip_cd_pct": 100 * (cd_su2 / cd_trip - 1), "su2_vs_xfoil_trip_cl_pct": 100 * (cl_su2 / cl_trip - 1),
            "trip_over_free_cd": cd_trip / cd_free}


# ------------------------------------------------------------------ claims
def C(id, title, calc, out, unit, how, limit=None, verifies=(), **kw):
    kit.claim(id, title, calc=calc, output=out, unit=unit, limit=limit, verifies=list(verifies), how=how, **kw)


SIMHOW = "Re-run team/B1/vlm_xfoil.py and cfd_sections.py; flight: cruise power legs at 14/16/18 m/s (T-B1-CRUISE-POWER)."
C("CL-B1V-CD0", "Zero-lift drag coefficient, as designed (sim)", "CALC-B1V-AERO", "cd0", "-", SIMHOW)
C("CL-B1V-K", "Lift-dependent drag factor, trimmed AVL + XFOIL", "CALC-B1V-AERO", "k", "-", SIMHOW)
C("CL-B1V-FIN-RATIO", "Fin + tube drag, SU2 over the hand estimate", "CALC-B1V-AERO", "fins_ratio_sim_hand", "-",
  "Re-run cfd_sections.py; flight: the cruise power test cannot separate it, a fin-off glide comparison on the twin can.")
C("CL-B1V-ALPHA0-TRIM", "Trimmed zero-lift angle, as designed", "CALC-B1V-AERO", "alpha0_trim_deg", "deg",
  "AVL trim at the A3 CG; flight: pitch vs airspeed in level cruise (H2).")
C("CL-B1V-LDMAX", "Maximum L/D, as designed", "CALC-B1V-AERO", "ld_max", "-", "Glide test (H2).")
C("CL-B1V-CLMAX", "Trimmed CLmax used: lower of B1 critical-section and B2 at the A3 static margin", "CALC-B1V-STALL",
  "clmax", "-", "Slow-flight stall (T-B2-STALL); B2 owns the CLmax, B1's run is the cross-check.")
C("CL-B1V-CLMAX-SIM", "Trimmed CLmax, B1 AVL + XFOIL critical section at the A3 CG", "CALC-B1V-STALL", "clmax_sim",
  "-", "As CL-B1V-CLMAX.")
C("CL-B1V-SM-A3", "Static margin at the A3 predicted CG, B2 neutral point", "CALC-B1V-STALL", "sm_a3", "-",
  "B3's CG/NP analysis; CG jig on the built aircraft.", limit=(">=", P + "requirements.static_margin_min"))
C("CL-B1V-VS-PRED", "Stall speed at the A3 predicted mass", "CALC-B1V-STALL", "vs_pred_ms", "m/s",
  "Slow-flight stall at the weighed mass with airspeed logged (T-B2-STALL).",
  limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"])
C("CL-B1V-VS-GATE", "Stall speed at the 2.6 kg gate, sim CLmax at the A3 CG", "CALC-B1V-STALL", "vs_gate_ms", "m/s",
  "As CL-B1V-VS-PRED with ballast to 2.6 kg.", limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"])
C("CL-B1V-VT-PRED", "1.3 Vs at the predicted mass", "CALC-B1V-STALL", "vt_pred_ms", "m/s",
  "Airspeed at 'Transition done' in the log (F4/H2).", limit=("<=", "ASM-B1-VCRUISE"), verifies=["R-TRANSITION"])
C("CL-B1V-VT-GATE", "1.3 Vs at the 2.6 kg gate", "CALC-B1V-STALL", "vt_gate_ms", "m/s",
  "As CL-B1V-VT-PRED.", limit=("<=", "ASM-B1-VCRUISE"), verifies=["R-TRANSITION"])
C("CL-B1V-HOVER-P", "Hover power at the predicted mass, 7 deg cant", "CALC-B1V-HOVER", "p_pred_w", "W",
  "Tethered hover at the weighed mass (T-B1-TETHER-HOVER).")
C("CL-B1V-HOVER-THROTTLE", "Hover thrust fraction, sagged pack, predicted mass", "CALC-B1V-HOVER",
  "throttle_pred_sag", "-", "Learned hover throttle in the log (F4/H2).", limit=("<=", 0.6), verifies=["R-HOVER-TW"])
C("CL-B1V-HOVER-TW-SAG", "Hover T/W, sag, download and cant, predicted mass", "CALC-B1V-HOVER", "tw_pred_sag", "-",
  "Thrust stand at 14.0 V (H1).", limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"])
C("CL-B1V-HOVER-TW", "Hover T/W, fresh pack, download and cant, predicted mass", "CALC-B1V-HOVER", "tw_pred_fresh",
  "-", "Thrust stand at 16.0 V (H1).", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"])
C("CL-B1V-CRUISE-P", "Cruise power, 16 m/s, predicted mass, sim drag", "CALC-B1V-CRUISE", "p_el_w", "W",
  "T-B1-CRUISE-POWER at the weighed mass.", verifies=["R-MISSION"])
C("CL-B1V-CRUISE-P-PESS", "Cruise power, pessimistic, predicted mass", "CALC-B1V-CRUISE", "p_el_pess_w", "W",
  "As CL-B1V-CRUISE-P.")
C("CL-B1V-CRUISE-P-GATE", "Cruise power at 2.6 kg with sim drag", "CALC-B1V-CRUISE", "p_el_gate_w", "W",
  "As CL-B1V-CRUISE-P with ballast.")
C("CL-B1V-CRUISE-DRAG", "Cruise drag, 16 m/s, predicted mass", "CALC-B1V-CRUISE", "drag_n", "N", SIMHOW)
C("CL-B1V-CRUISE-LD", "Cruise L/D, predicted mass", "CALC-B1V-CRUISE", "ld", "-", SIMHOW)
C("CL-B1V-CRUISE-I", "Cruise current, predicted mass", "CALC-B1V-CRUISE", "i_a", "A", "Current sensor in cruise (H2).")
C("CL-B1V-TRANS-THRUST", "Pitch-over peak thrust fraction, as designed", "CALC-B1V-TRANSITION", "thrust_frac_max",
  "-", "Throttle output in the transition log (T-B1-TRANSITION-LOG).", limit=("<=", "ASM-B1-CTRL-RESERVE"),
  verifies=["R-TRANSITION"])
C("CL-B1V-TRANS-ALT-LOSS", "Pitch-over altitude loss, as designed", "CALC-B1V-TRANSITION", "alt_loss_m", "m",
  "Baro altitude in the transition log (T-B1-TRANSITION-LOG).", limit=("<=", 10.0), verifies=["R-TRANSITION"])
C("CL-B1V-TRANS-TIME", "Pitch-over time to 1.3 Vs, as designed", "CALC-B1V-TRANSITION", "t_to_vt_s", "s",
  "F4 SITL, then the log.")
C("CL-B1V-TRANS-ENERGY", "Energy of one pitch-over, as designed", "CALC-B1V-TRANSITION", "energy_wh", "Wh",
  "Integrate pack W over the transition in the log.")
C("CL-B1V-CORR-THRUST", "Peak steady thrust fraction in the corridor", "CALC-B1V-TRANSITION", "corr_thrust_frac_max",
  "-", "As CL-B1V-TRANS-THRUST.", limit=("<=", "ASM-B1-CTRL-RESERVE"), verifies=["R-TRANSITION"])
C("CL-B1V-CRUISE-TIME", "Cruise after 2 min hover, as designed", "CALC-B1V-MISSION", "t_cruise_min", "min",
  "Fly the mission profile at the weighed mass; land with >= 20 % (H2).",
  limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"])
C("CL-B1V-CRUISE-TIME-PESS", "Cruise after 2 min hover, pessimistic, as designed", "CALC-B1V-MISSION",
  "t_cruise_pess_min", "min", "As CL-B1V-CRUISE-TIME.", limit=(">=", P + "requirements.cruise_time_min"),
  verifies=["R-MISSION"])
C("CL-B1V-VH-FW", "Top level speed at THR_MAX 70 %, as designed (C1's VH)", "CALC-B1V-SPEED", "vh_fw_cap_ms", "m/s",
  "Full-throttle FBWA level run on a fresh pack with rpm telemetry, after the VD loads case is cleared (H2).",
  limit=(">=", 18.0))
C("CL-B1V-VH-RATIO", "VH x 1.25 over VD 27.2 m/s", "CALC-B1V-SPEED", "vh_ratio_vd", "-",
  "As CL-B1V-VH-FW; C1 holds VD = 27.2 m/s while this stays <= 1.", limit=("<=", 1.0))
C("CL-B1V-ROC-FW", "FW climb at 16 m/s, THR_MAX 70 %, worst pack", "CALC-B1V-SPEED", "roc_fw_cap_ms", "m/s",
  "FBWA full-throttle climb at 16 m/s (H2); F4 sets TECS_CLMB_MAX below it.", limit=(">=", 3.0))
C("CL-B1V-WIND-HOVER-MAX", "Wind for a safe fin-tip landing, lightest mass", "CALC-B1V-WIND", "v_hover_max_ms", "m/s",
  "QLOITER in measured wind at the lightest pack (H2).", limit=(">=", P + "requirements.wind_limit_ms"),
  verifies=["R-WIND"])
C("CL-B1V-GROUND-TIP-WIND", "Wind that tips the parked aircraft, lightest mass", "CALC-B1V-WIND", "v_ground_tip_ms",
  "m/s", "Tilt-board angle (C5) and a fan test (H3).", limit=(">=", P + "requirements.gust_survive_ms"),
  verifies=["R-WIND", "R-TIPOVER"])
C("CL-B1V-GUST-8-THRUST", "Thrust fraction holding the 8 m/s lean, lightest mass", "CALC-B1V-WIND",
  "thrust_frac_8ms", "-", "Thrust stand T/W (H1) and the lean in the logs.", limit=("<=", "ASM-B1-CTRL-RESERVE"),
  verifies=["R-WIND"])
C("CL-B1V-GCI-MAX", "Largest SU2 fine-grid GCI on cd (3 sections)", "CALC-B1V-CONV", "gci_max_pct", "%",
  "Re-run cfd_sections.py; add a 4th level if it exceeds 10 %.", limit=("<=", 10.0))
C("CL-B1V-SU2-XFOIL-CD", "SU2 SA vs XFOIL tripped cd, S5010 alpha 2.5 deg", "CALC-B1V-CONV",
  "su2_vs_xfoil_trip_cd_pct", "%", "Cross-code check; both fully turbulent.")


# ------------------------------------------------------------------ report outputs (not part of the chain)
INK, INK2, INK3, AX, GRID, ACC, FAIL = "#121619", "#4B5563", "#6B7280", "#9AA4B1", "#E3E7ED", "#1F5FC7", "#B42323"


def _style(plt):
    plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": AX,
                         "axes.labelcolor": INK2, "xtick.color": INK3, "ytick.color": INK3, "axes.grid": True,
                         "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none", "figure.facecolor": "white",
                         "axes.facecolor": "white", "legend.frameon": False})


def figures(res):
    try:
        import matplotlib
    except ImportError:                       # python -I hides the user site where matplotlib's deps live
        import site
        sys.path.append(site.getusersitepackages())
        import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    PNG = HERE / "sim" / "png"                # raster copies for print and quick review
    PNG.mkdir(parents=True, exist_ok=True)
    cfd = json.loads((HERE / "sim" / "cfd" / "cfd_results.json").read_text())
    vx = json.loads((HERE / "sim" / "vlm_xfoil_results.json").read_text())
    # FIG B1-03 grid convergence
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.2))
    for case, lab in (("finA", "fin, tube + board"), ("finB", "fin, bare board"), ("s5010", "S5010, SA, 2.5°")):
        L = cfd["cases"][case]
        h = [1 / math.sqrt(L[f"L{i}"]["cells"]) for i in (1, 2, 3)]
        cd = [L[f"L{i}"]["cd"] for i in (1, 2, 3)]
        g = cfd["gci"][case]["cd"]
        col = ACC if case == "finA" else (INK2 if case == "finB" else AX)
        axs[0].plot(h, cd, "o-", color=col, lw=1.5, ms=4, label=f"{lab}  GCI {g['gci_fine_pct']:.1f} %")
        if g.get("p"):
            axs[0].plot([0], [g["f_ext"]], "x", color=col, ms=6)
    axs[0].set_xlim(left=0); axs[0].set_xlabel("1/√cells"); axs[0].set_ylabel("section cd (on own chord)")
    axs[0].set_title("SU2 2-D RANS, 3 grids", loc="left", fontsize=9, color=INK)
    axs[0].legend(fontsize=7, loc="upper left")
    ac = vx["avl_convergence"]
    n = [ac[f"L{i}"]["n_strips_half"] for i in (1, 2, 3)]
    axs[1].plot(n, [ac[f"L{i}"]["e"] for i in (1, 2, 3)], "o-", color=ACC, lw=1.5, ms=4, label="span efficiency e")
    ax2 = axs[1].twinx(); ax2.grid(False)
    ax2.plot(n, [ac[f"L{i}"]["elevon_deg"] for i in (1, 2, 3)], "s--", color=INK3, lw=1, ms=4, label="trim elevon")
    ax2.set_ylabel("trim elevon (deg)", color=INK3); ax2.spines["right"].set_visible(True)
    axs[1].set_xlabel("spanwise strips per half wing"); axs[1].set_ylabel("e (AVL, Trefftz)")
    axs[1].set_title("AVL, 3 lattices, cruise trim", loc="left", fontsize=9, color=INK)
    pc = vx["xfoil_panel_convergence"]
    ks = sorted(pc, key=int)
    axs[2].plot([int(k) for k in ks], [1e4 * pc[k]["cd_at_cl"] for k in ks], "o-", color=ACC, lw=1.5, ms=4)
    axs[2].set_xlabel("XFOIL panels"); axs[2].set_ylabel("cd at cruise cl (counts)")
    axs[2].set_title("XFOIL, 3 panel counts, Ncrit 9", loc="left", fontsize=9, color=INK)
    fig.tight_layout(); fig.savefig(HERE / "fig-b1-convergence.svg"); fig.savefig(PNG / "fig-b1-convergence.png", dpi=110); plt.close(fig)
    # FIG B1-04 drag breakdown, hand rev 3 vs as designed (CD0 x S, m2)
    S = 0.368
    hand_names = ["wing", "fins", "motor tubes", "motors", "pod", "pod front", "braces", "collars"]
    hand = [x * S * 1e4 for x in res["hand_parts"]]
    sim = res["aero"]["cd0_parts"]
    sim_d = {"wing": sim[0], "fins + tubes": sim[1], "motors": sim[2], "pod": sim[3], "pod front": sim[4],
             "braces": sim[5], "collars": sim[6]}
    hand_d = {"wing": hand[0] / S / 1e4, "fins + tubes": (hand[1] + hand[2]) / S / 1e4, "motors": hand[3] / S / 1e4,
              "pod": hand[4] / S / 1e4, "pod front": hand[5] / S / 1e4, "braces": hand[6] / S / 1e4,
              "collars": hand[7] / S / 1e4}
    labels = list(sim_d)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    y = range(len(labels))
    ax.barh([i + 0.18 for i in y], [hand_d[k] * 1e4 for k in labels], 0.34, color=AX, label="rev 3 hand estimate")
    ax.barh([i - 0.18 for i in y], [sim_d[k] * 1e4 for k in labels], 0.34, color=ACC, label="as designed (sim)")
    for i, k in enumerate(labels):
        ax.text(sim_d[k] * 1e4 + 3, i - 0.18, f"{sim_d[k] * 1e4:.0f}", va="center", fontsize=7, color=INK,
                family="IBM Plex Mono")
    ax.set_yticks(list(y)); ax.set_yticklabels(labels); ax.invert_yaxis()
    ax.set_xlabel("zero-lift drag, CD0 counts on S = 0.368 m² (incl. interference 1.15)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(f"CD0 {res['hand_cd0'] * 1e4:.0f} → {res['aero']['cd0'] * 1e4:.0f} counts", loc="left",
                 fontsize=10, color=INK)
    fig.tight_layout(); fig.savefig(HERE / "fig-b1-drag-breakdown.svg"); fig.savefig(PNG / "fig-b1-drag-breakdown.png", dpi=110); plt.close(fig)
    # FIG B1-05 cruise power vs speed
    fig, ax = plt.subplots(figsize=(7, 3.4))
    hr = res["hand_sweep"]
    ax.plot([r[0] for r in hr], [r[1] for r in hr], "-", color=AX, lw=1.5, label="rev 3 hand, 2.6 kg")
    ax.plot([r[0] for r in hr], [r[2] for r in hr], "--", color=AX, lw=1, label="rev 3 hand, pessimistic")
    sr = res["cruise"]["rows_V_P_Ppess_D"]
    ax.plot([r[0] for r in sr], [r[1] for r in sr], "-", color=ACC, lw=2, label="as designed, 2.436 kg")
    ax.plot([r[0] for r in sr], [r[2] for r in sr], "--", color=ACC, lw=1, label="as designed, pessimistic")
    ax.axvline(16, color=INK3, lw=0.8); ax.text(16.05, ax.get_ylim()[0] + 5, "cruise 16 m/s", fontsize=7, color=INK3)
    ax.axvline(res["stall"]["vt_gate_ms"], color=INK3, lw=0.8, ls=":")
    ax.text(res["stall"]["vt_gate_ms"] - 0.05, ax.get_ylim()[0] + 5, "1.3 Vs at 2.6 kg", fontsize=7, color=INK3,
            ha="right")
    ax.set_xlabel("airspeed (m/s)"); ax.set_ylabel("electrical power (W)"); ax.legend(fontsize=7, loc="upper left")
    ax.set_title("Cruise power: hand estimate vs as designed", loc="left", fontsize=10, color=INK)
    fig.tight_layout(); fig.savefig(HERE / "fig-b1-cruise-power.svg"); fig.savefig(PNG / "fig-b1-cruise-power.png", dpi=110); plt.close(fig)
    # FIG B1-06 requirement margins
    m = res["margins"]
    fig, ax = plt.subplots(figsize=(7, 0.32 * len(m) + 0.9))
    for i, (lab, val) in enumerate(m):
        ax.barh(i, 100 * val, 0.6, color=ACC if val >= 0 else FAIL)
        ax.text(100 * val + (2 if val >= 0 else -2), i, f"{100 * val:+.0f} %", va="center",
                ha="left" if val >= 0 else "right", fontsize=7, color=INK, family="IBM Plex Mono")
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(range(len(m))); ax.set_yticklabels([x[0] for x in m], fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("margin against the requirement (%)")
    ax.set_title("As-designed margins", loc="left", fontsize=10, color=INK)
    fig.tight_layout(); fig.savefig(HERE / "fig-b1-margins.svg"); fig.savefig(PNG / "fig-b1-margins.png", dpi=110); plt.close(fig)


if __name__ == "__main__":
    kit.write()
    N = kit.nodes
    out = lambda c: N[c]["outputs"]
    hand = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
    prev = json.loads((HERE / "performance_results.json").read_text(encoding="utf-8"))
    res = {"aero": out("CALC-B1V-AERO"), "stall": out("CALC-B1V-STALL"), "hover": out("CALC-B1V-HOVER"),
           "cruise": out("CALC-B1V-CRUISE"), "mission": out("CALC-B1V-MISSION"), "speed": out("CALC-B1V-SPEED"),
           "wind": out("CALC-B1V-WIND"), "conv": out("CALC-B1V-CONV"),
           "transition": {k: v for k, v in out("CALC-B1V-TRANSITION").items() if k != "corridor_rows"},
           "corridor_rows": out("CALC-B1V-TRANSITION")["corridor_rows"],
           "hand_parts": hand["CALC-B1-AERO"]["outputs"]["cd0_parts"], "hand_cd0": hand["CL-B1-CD0"]["value"],
           "hand_sweep": [[r[0], r[1], r[2]] for r in prev["sweep"]] if "sweep" in prev else
           [[r[0], r[1], r[2]] for r in hand["CALC-B1-SWEEP"]["outputs"]["rows_V_P_Ppess_eta_t_tpess"]]}
    lim = lambda cid: N[cid]
    margins = []
    for cid, lab in (("CL-B1V-VS-PRED", "stall, predicted mass"), ("CL-B1V-VS-GATE", "stall, 2.6 kg gate"),
                     ("CL-B1V-VT-GATE", "1.3 Vs ≤ cruise, gate"), ("CL-B1V-HOVER-TW", "hover T/W fresh ≥ 2.0"),
                     ("CL-B1V-HOVER-TW-SAG", "hover T/W sagged ≥ 1.6"), ("CL-B1V-HOVER-THROTTLE", "hover throttle ≤ 0.60"),
                     ("CL-B1V-TRANS-THRUST", "pitch-over thrust ≤ 0.80"), ("CL-B1V-CRUISE-TIME", "cruise time ≥ 5 min"),
                     ("CL-B1V-CRUISE-TIME-PESS", "cruise time pess. ≥ 5 min"), ("CL-B1V-VH-RATIO", "1.25 VH ≤ VD"),
                     ("CL-B1V-WIND-HOVER-MAX", "landing wind ≥ 5 m/s"),
                     ("CL-B1V-GROUND-TIP-WIND", "parked tip-over ≥ 8 m/s"), ("CL-B1V-GUST-8-THRUST", "8 m/s lean thrust ≤ 0.80")):
        n = N[cid]
        lv = n["limit"].get("value")
        lv = kit.value(n["limit"]["ref"]) if lv is None else lv
        margins.append((lab, pk.margin(n["value"], lv, n["limit"]["op"])))
    res["margins"] = margins
    (HERE / "sim" / "sim_verify_results.json").write_text(json.dumps(res, indent=1, default=float))
    figures(res)
    print("sim/sim_verify_results.json and fig-b1-convergence/-drag-breakdown/-cruise-power/-margins.svg written")
