"""H1 ground test engineer: rig sizing and pass/fail thresholds for the K09-L ground test campaign.

Run:  python -I redesign/team/H1/ground_tests.py      -> claims.json beside this file
Then: python -I redesign/proofs/build_graph.py         -> confirms nothing drifted

What this script owns (one paragraph). The numbers a ground test needs before it can run and that other roles
read: the load-cell and torque-cell ranges and resolution the thrust stand must have (from C1's limit thrust and
torque, B4's hover point), the current the stand harness and ESC see on a 16.8 V full-throttle step (E1), the
isolated-stand thrust that passes R-HOVER-TW (A2 requirement, gate mass, download factor), the weigh and CG-balance
uncertainty against A3's gate margin and B3's CG range (guard bands), the proof loads to hang (C1 ultimate / 1.5),
the tie-down force for the four-motor restrained run, and the pack acceptance lines (A2, E2). Procedures and the
cards that use these numbers are in GROUND-TEST-PLAN.md. Every input is a node id; nothing is typed twice.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ---------------------------------------------------------------- sources
kit.source("SRC-H1-HX711", "Avia Semiconductor HX711 24-bit load-cell ADC datasheet", kind="datasheet",
           url="https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf",
           where="p.1-2: 10/80 SPS, gain 128 = +/-20 mV full scale; noise is set by the cell and wiring, so the "
                 "1 g (20 kg cell) and 0.5 g (1 kg cell) noise used here are assumptions confirmed by T-H1-STAND-CAL",
           status="UNVERIFIED")
kit.source("SRC-H1-ELRS-RANGE", "ExpressLRS: range and power settings (pre-flight range check at reduced power)",
           kind="web", url="https://www.expresslrs.org/quick-start/transmitters/tx-prep/",
           where="power levels 10-250 mW selectable in the Lua script; LQ shown in telemetry", status="UNVERIFIED")
kit.source("SRC-H1-COMPASSMOT", "ArduPilot: compass-motor calibration (compassmot)", kind="web",
           url="https://ardupilot.org/copter/docs/common-compass-setup-advanced.html#compassmot-compensation-for-interference-from-the-power-wires-escs-and-motors",
           where="interference < 30 % acceptable, 31-60 % grey zone, > 60 % unacceptable", status="UNVERIFIED")

# ---------------------------------------------------------------- assumptions (rig hardware choices)
kit.assumption("ASM-H1-THRUST-CELL", "Thrust cell 20 kgf bar cell + HX711", "Bar load cell rated 20 kgf on the "
               "thrust axis, read by an HX711 at 80 SPS; noise +/-1 gf after averaging 8 samples.",
               basis="E1 CR-E1-11 asks for a 20 kg cell + HX711; 1 gf noise is typical of a shielded 20 kg bar cell",
               value={"cap_kgf": 20.0, "noise_gf": 1.0}, unit="kgf,gf", status="UNVERIFIED",
               cites=["SRC-H1-HX711"])
kit.assumption("ASM-H1-TORQUE-CELL", "Torque cell 1 kgf bar cell at 100 mm arm", "Motor mount on a bearing axle "
               "coaxial with the shaft; reaction torque restrained by an arm of 0.100 m pressing a 1 kgf bar cell "
               "(second HX711); noise +/-0.5 gf.",
               basis="B4 CR-B4-09 asks for a torque cell; a lever on a bar cell is the cheapest stand design that "
                     "separates torque from thrust",
               value={"cap_kgf": 1.0, "arm_m": 0.100, "noise_gf": 0.5}, unit="kgf,m,gf", status="UNVERIFIED",
               cites=["SRC-H1-HX711"])
kit.assumption("ASM-H1-RANGE-FACTOR", "Cell range >= 1.25 x the largest expected load", "Each cell's rated "
               "capacity covers 1.25 x the peak load it should see, so an over-prediction of 25 % does not "
               "overload it.", basis="common instrumentation practice (load at <= 80 % of rated capacity)",
               value=1.25, unit="-")
kit.assumption("ASM-H1-SCALE", "Two 5 kg x 1 g scales, 0.1 % after calibration", "Two identical kitchen/shipping "
               "scales, 5 kg capacity, 1 g display step, calibrated against a 2.000 kg check mass (water in a "
               "sealed bottle weighed on the Jacobs lab balance) to +/-0.1 % of reading.",
               basis="1 g step is what A1 (T-A1-WEIGH) and A3 (T-A3-WEIGH-PARTS) specify; 0.1 % after a check-mass "
                     "calibration is conservative for strain-gauge scales",
               value={"res_g": 1.0, "cal_frac": 0.001}, unit="g,-", status="UNVERIFIED")
kit.assumption("ASM-H1-CG-JIG", "CG jig: two pin pairs 0.220 m apart in x", "Two bridges, one per scale, each "
               "with two padded pins under the wing outboard of the fins (|y| = 0.45 m): front pins at x = 0.010 m, "
               "rear pins at x = 0.230 m (ahead of the elevon hinge). Pin x set with a steel rule and square to "
               "+/-0.5 mm.", basis="the lower half-fins and lower motors block any support inboard of |y| 0.34 m; "
               "the rear pins must stay off the elevons (hinge x 0.2496 m)",
               value={"x1_m": 0.010, "x2_m": 0.230, "pos_tol_m": 0.0005}, unit="m", status="PROPOSED")
kit.assumption("ASM-H1-RESTRAINT-SF", "Tie-down factor 2.0", "The restrained-frame run (four motors, props on) "
               "is tied down for 2.0 x the net upward force if the limiter fails and all four motors reach "
               "C1's limit thrust.", basis="props-on bench runs are the highest-energy ground test; 2.0 covers a "
               "snatch load on a slack strap", value=2.0, unit="-")
kit.assumption("ASM-H1-ESC-BURST", "ESC 55 A for 10 s", "LANRC BLHeli_S 45 A ESC burst rating 55 A for 10 s; "
               "a full-throttle step on the stand is held <= 2 s.", basis="params.json#propulsion.esc listing text",
               value=55.0, unit="A", status="UNVERIFIED", cites=["SRC-LANRC-45A"])
kit.assumption("ASM-H1-RES-MAX", "Thrust and torque resolution <= 0.5 % / 2 % of hover", "The A/B prop "
               "comparison must resolve B1's 1.9 % hover-power difference (CL-B1-HOVER-PROP-RATIO 1.019): "
               "thrust noise <= 0.5 % of hover thrust, torque noise <= 2 % of hover torque.",
               basis="resolution 4 x finer than the difference to detect", value={"thrust": 0.005, "torque": 0.02},
               unit="-")


# ---------------------------------------------------------------- 1. thrust stand range and resolution
@kit.calc("CALC-H1-STAND", equation="F_req = k T_lim / g ; Ftq_req = k Q_lim / (arm g) ; "
          "res_T = noise_T / (T_h/g) ; res_Q = noise_Q g arm / Q_h",
          inputs={"t_lim": "CL-C1-T-LIMIT", "q_lim": "CL-C1-MOTOR-TORQUE", "t_hover": "CL-B4-HOVER-T",
                  "q_hover": "CL-B4-HOVER-Q", "k": "ASM-H1-RANGE-FACTOR", "cell": "ASM-H1-THRUST-CELL",
                  "tq": "ASM-H1-TORQUE-CELL", "g": P + "env.g_ms2"},
          units={"g": "m/s2"})
def stand_range(t_lim, q_lim, t_hover, q_hover, k, cell, tq, g):
    gf = g / 1000.0                                            # N per gram-force
    return {"thrust_cap_req_kgf": k * t_lim / g,
            "torque_cell_req_kgf": k * q_lim / tq["arm_m"] / g,
            "thrust_res_frac": cell["noise_gf"] * gf / t_hover,
            "torque_res_frac": tq["noise_gf"] * gf * tq["arm_m"] / q_hover,
            "torque_force_hover_gf": q_hover / tq["arm_m"] / gf}


@kit.calc("CALC-H1-LIMITS", equation="limits read from the rig assumptions",
          inputs={"cell": "ASM-H1-THRUST-CELL", "tq": "ASM-H1-TORQUE-CELL", "res": "ASM-H1-RES-MAX"})
def rig_limits(cell, tq, res):
    return {"thrust_cap_kgf": cell["cap_kgf"], "torque_cap_kgf": tq["cap_kgf"],
            "thrust_res_max": res["thrust"], "torque_res_max": res["torque"]}


kit.claim("CL-H1-THRUST-CAP", "Thrust cell rating", calc="CALC-H1-LIMITS", output="thrust_cap_kgf", unit="kgf",
          how="Cell label and calibration T-H1-STAND-CAL.")
kit.claim("CL-H1-TORQUE-CAP", "Torque cell rating", calc="CALC-H1-LIMITS", output="torque_cap_kgf", unit="kgf",
          how="Cell label and calibration T-H1-STAND-CAL.")
kit.claim("CL-H1-THRUST-RES-MAX", "Thrust resolution needed", calc="CALC-H1-LIMITS", output="thrust_res_max",
          unit="-", how="From ASM-H1-RES-MAX (A/B prop comparison).")
kit.claim("CL-H1-TORQUE-RES-MAX", "Torque resolution needed", calc="CALC-H1-LIMITS", output="torque_res_max",
          unit="-", how="From ASM-H1-RES-MAX (A/B prop comparison).")
kit.claim("CL-H1-THRUST-CELL-REQ", "Thrust cell range needed", calc="CALC-H1-STAND", output="thrust_cap_req_kgf",
          unit="kgf", limit=("<=", "CL-H1-THRUST-CAP"),
          how="T-H1-STAND-CAL: hang 0.5, 1.0, 2.0, 2.5 kg on the thrust axis; linear within 0.5 % FS.")
kit.claim("CL-H1-TORQUE-CELL-REQ", "Torque cell range needed", calc="CALC-H1-STAND", output="torque_cell_req_kgf",
          unit="kgf", limit=("<=", "CL-H1-TORQUE-CAP"),
          how="T-H1-STAND-CAL: 50, 100, 200, 500 g at the 0.100 m arm; linear within 1 % FS.")
kit.claim("CL-H1-THRUST-RES", "Thrust noise / hover thrust", calc="CALC-H1-STAND", output="thrust_res_frac",
          unit="-", limit=("<=", "CL-H1-THRUST-RES-MAX"),
          how="T-H1-STAND-CAL: 60 s of zero-load samples, 2 sigma noise; repeat at 690 gf hanging mass.")
kit.claim("CL-H1-TORQUE-RES", "Torque noise / hover torque", calc="CALC-H1-STAND", output="torque_res_frac",
          unit="-", limit=("<=", "CL-H1-TORQUE-RES-MAX"),
          how="T-H1-STAND-CAL: 60 s of zero-load samples on the torque cell, 2 sigma noise.")
kit.claim("CL-H1-TORQUE-F-HOVER", "Torque-cell force at hover", calc="CALC-H1-STAND", output="torque_force_hover_gf",
          unit="gf", how="Read on the stand at 690 gf thrust (T-B4-STAND).")


# ---------------------------------------------------------------- 2. stand current: supply and full-throttle step
@kit.calc("CALC-H1-CURRENT", equation="I_supply = 1.05 I_max(14.8 V) ; I_step = I_max(16.8 V, unlimited)",
          inputs={"i148": "CL-E1-IMAX-148-55", "i168": "CL-E1-IMAX-168-55"})
def stand_current(i148, i168):
    return {"supply_req_a": 1.05 * i148, "step_a": i168}


kit.claim("CL-H1-SUPPLY-REQ", "Bench supply current for 14.8 V sweeps", calc="CALC-H1-CURRENT",
          output="supply_req_a", unit="A",
          how="Supply label; if it cannot hold 14.8 V at this current, run 70-100 % steps on a flight pack and log V.")
kit.claim("CL-H1-STEP-I", "Unlimited 16.8 V full-throttle step current", calc="CALC-H1-CURRENT", output="step_a",
          unit="A", limit=("<=", "ASM-H1-ESC-BURST"),
          how="T-C1-THRUST-FRESH logs it; hold the step <= 2 s; abort above 55 A.")


# ---------------------------------------------------------------- 3. pass lines for R-HOVER-TW on the isolated stand
@kit.calc("CALC-H1-TW-PASS", equation="T_pass = TW m g k_dl / (n g) [kgf] ; T_pred_sag = T_max x sag",
          inputs={"tw": P + "requirements.hover_tw_min", "tw_sag": P + "requirements.hover_tw_min_sag",
                  "m": P + "requirements.mtow_gate_kg", "k_dl": P + "propulsion.download_factor",
                  "n": P + "propulsion.n_motors", "t_max": P + "propulsion.thrust_max_per_motor_kg",
                  "sag": P + "propulsion.voltage_sag"},
          units={"m": "kg", "t_max": "kg"})
def tw_pass(tw, tw_sag, m, k_dl, n, t_max, sag):
    return {"pass_fresh_kgf": tw * m * k_dl / n, "pass_sag_kgf": tw_sag * m * k_dl / n,
            "pred_sag_kgf": t_max * sag, "pred_fresh_kgf": t_max}


kit.claim("CL-H1-T-PRED-FRESH", "Predicted thrust, limiter, fresh", calc="CALC-H1-TW-PASS", output="pred_fresh_kgf",
          unit="kgf", how="E1 CL-E1-ILIM-TW-FRESH via params; measured by T-A1-THRUST-STATION.")
kit.claim("CL-H1-T-PRED-SAG", "Predicted thrust, worst pack state", calc="CALC-H1-TW-PASS", output="pred_sag_kgf",
          unit="kgf", how="params.json thrust_max x voltage_sag; measured on a 3.6 V/cell 10 degC pack.")
kit.claim("CL-H1-T-PASS-FRESH", "Stand pass line, fresh pack (T/W 2.0)", calc="CALC-H1-TW-PASS",
          output="pass_fresh_kgf", unit="kgf", limit=("<=", "CL-H1-T-PRED-FRESH"),
          how="Card GT-02d: isolated full-throttle thrust at the per-motor limiter share (25 A) on a "
              "16.8 V pack must be >= CL-H1-T-FRESH-ACCEPT.")
kit.claim("CL-H1-T-PASS-SAG", "Stand pass line, worst pack (T/W 1.6)", calc="CALC-H1-TW-PASS",
          output="pass_sag_kgf", unit="kgf", limit=("<=", "CL-H1-T-PRED-SAG"),
          how="Card GT-02e: full-throttle thrust on a 3.6 V/cell (20 %) pack at 10 degC must be >= CL-H1-T-SAG-ACCEPT.")


# ---------------------------------------------------------------- 3b. guard bands on the stand pass lines (CR-A1-41)
kit.assumption("ASM-H1-CAL-U", "Calibrated thrust-cell U95 = 0.5 % of the 2.5 kgf calibration span",
               "After T-H1-STAND-CAL the thrust reading is within 0.5 % of the 2.5 kgf dead-weight span (12.5 gf) "
               "anywhere in that span, including drift between the start and end calibration.",
               basis="GT-01 pass lines: linearity <= 0.5 % FS and start/end drift <= 0.5 %", value=0.005, unit="-")
kit.assumption("ASM-H1-CAL-SPAN", "Thrust-cell calibration span 2.5 kgf", "Dead weights 0.5/1.0/2.0/2.5 kg on the "
               "thrust axis (GT-01 step 2); the top weight covers 1.25 x the 21.1 N limit thrust (2.69 kgf) within 7 %.",
               basis="largest water-jug/dead-weight set that can be hung on the axle cord safely", value=2.5, unit="kgf")


@kit.calc("CALC-H1-GUARD", equation="U = u_cal span ; T_peak_acc = T_lim - U g ; T_fresh_acc = T_pass_fresh + U ; "
          "T_sag_acc = T_pass_sag + U",
          inputs={"u": "ASM-H1-CAL-U", "span": "ASM-H1-CAL-SPAN", "t_lim": P + "requirements.thrust_limit_per_motor_n",
                  "pf": "CL-H1-T-PASS-FRESH", "ps": "CL-H1-T-PASS-SAG", "g": P + "env.g_ms2"},
          units={"t_lim": "N", "g": "m/s2"})
def guard(u, span, t_lim, pf, ps, g):
    u_kgf = u * span
    return {"u_kgf": u_kgf, "u_n": u_kgf * g, "peak_accept_n": t_lim - u_kgf * g,
            "fresh_accept_kgf": pf + u_kgf, "sag_accept_kgf": ps + u_kgf}


kit.claim("CL-H1-T-U95", "Thrust-cell U95 after calibration", calc="CALC-H1-GUARD", output="u_n", unit="N",
          how="T-H1-STAND-CAL: linearity and drift of the 2.5 kg dead-weight set.")
kit.claim("CL-H1-T-PEAK-ACCEPT", "GT-02d peak-thrust acceptance (limit thrust minus U95)", calc="CALC-H1-GUARD",
          output="peak_accept_n", unit="N",
          how="Card GT-02d: max of 3 unlimited steps at the F4 cap, rho-corrected, <= this value passes; between this "
              "and 21.1 N is a retest (5 more steps); above 21.1 N C1 re-runs the loads (CR-H1-01).")
kit.claim("CL-H1-T-FRESH-ACCEPT", "GT-02d limited-thrust acceptance, fresh pack", calc="CALC-H1-GUARD",
          output="fresh_accept_kgf", unit="kgf", limit=("<=", "CL-H1-T-PRED-FRESH"),
          how="Card GT-02d step 3: thrust with the 25 A per-motor limiter share >= this value.")
kit.claim("CL-H1-T-SAG-ACCEPT", "GT-02e cold-pack acceptance, 3.6 V/cell at 10 degC", calc="CALC-H1-GUARD",
          output="sag_accept_kgf", unit="kgf", limit=("<=", "CL-H1-T-PRED-SAG"),
          how="Card GT-02e: full-throttle thrust with the limiter share on the cold 20 % pack >= this value.")


# ---------------------------------------------------------------- 4. weigh and CG measurement uncertainty
@kit.calc("CALC-H1-WEIGH", equation="U95 = 2 sqrt((res/sqrt12)^2 + (cal m)^2) ; frac = U95 / gate margin",
          inputs={"scale": "ASM-H1-SCALE", "m": P + "requirements.mtow_gate_kg", "margin": "CL-A3-GATE-MARGIN"},
          units={"m": "kg"})
def weigh_unc(scale, m, margin):
    u95_g = 2.0 * math.sqrt((scale["res_g"] / math.sqrt(12.0)) ** 2 + (scale["cal_frac"] * m * 1000.0) ** 2)
    return {"u95_g": u95_g, "u_frac": u95_g / (margin * 1000.0), "accept_max_kg": m - u95_g / 1000.0}


kit.claim("CL-H1-WEIGH-U95", "Weigh uncertainty (95 %)", calc="CALC-H1-WEIGH", output="u95_g", unit="g",
          how="T-H1-SCALE-CAL: weigh the 2.000 kg check mass 10 times on each scale.")
kit.claim("CL-H1-WEIGH-U-FRAC", "Weigh uncertainty / A3 gate margin", calc="CALC-H1-WEIGH", output="u_frac",
          unit="-", limit=("<=", 0.10), how="Re-run after A3 updates CL-A3-GATE-MARGIN.")
kit.claim("CL-H1-WEIGH-ACCEPT", "Weigh-in acceptance line (guard-banded)", calc="CALC-H1-WEIGH",
          output="accept_max_kg", unit="kg",
          how="Card GT-06: ready-to-fly mass must read <= this value (gate minus U95).")


@kit.calc("CALC-H1-CG", equation="x = x1 + d W2/W ; U95 = 2 sqrt(e^2 + (W2/W sqrt2 e)^2 + (d sqrt2 u_W / W)^2)",
          inputs={"jig": "ASM-H1-CG-JIG", "scale": "ASM-H1-SCALE", "m": P + "requirements.mtow_gate_kg",
                  "xr": P + "cg.x_range_m", "xt": P + "cg.x_target_m"},
          units={"m": "kg", "xr": "m", "xt": "m"})
def cg_unc(jig, scale, m, xr, xt):
    d = jig["x2_m"] - jig["x1_m"]
    w = m * 1000.0
    w2_frac = (xt - jig["x1_m"]) / d
    u_w = math.sqrt((scale["res_g"] / math.sqrt(12.0)) ** 2 + (scale["cal_frac"] * w * w2_frac) ** 2)
    e = jig["pos_tol_m"] / math.sqrt(3.0)                     # uniform +/-tol
    u95 = 2.0 * math.sqrt(e ** 2 + (w2_frac * math.sqrt(2.0) * e) ** 2 + (d * math.sqrt(2.0) * u_w / w) ** 2)
    half = (xr[1] - xr[0]) / 2.0
    return {"u95_m": u95, "u_frac_half_range": u95 / half, "accept_fwd_m": xr[0] + u95, "accept_aft_m": xr[1] - u95,
            "w2_frac": w2_frac}


kit.claim("CL-H1-CG-U95", "CG-x uncertainty on the two-scale jig (95 %)", calc="CALC-H1-CG", output="u95_m",
          unit="m", how="T-H1-SCALE-CAL: place a 1.000 kg mass at a ruled x on the empty jig, recover x within U95.")
kit.claim("CL-H1-CG-U-FRAC", "CG uncertainty / half the CG range", calc="CALC-H1-CG", output="u_frac_half_range",
          unit="-", limit=("<=", 0.5), how="Re-run after B3 changes cg.x_range_m.")
kit.claim("CL-H1-CG-ACCEPT-FWD", "CG acceptance, forward line (guard-banded)", calc="CALC-H1-CG",
          output="accept_fwd_m", unit="m", how="Card GT-07: measured x must be >= this value.")
kit.claim("CL-H1-CG-ACCEPT-AFT", "CG acceptance, aft line (guard-banded)", calc="CALC-H1-CG",
          output="accept_aft_m", unit="m", how="Card GT-07: measured x must be <= this value.")


# ---------------------------------------------------------------- 5. proof loads (limit = ultimate / 1.5)
# R3: the wing proof uses C1's four-pad tree at LIMIT with all four pads, the relief pull and the outboard step 2 read
# as C1 claims (CR-C1-30, CR-C1-27; pad 4 is now a claim, so ASM-H1-PAD4-Y is retired). The pad masses are what the
# card hangs. Mount and fin loads stay ultimate / 1.5.
@kit.calc("CALC-H1-PROOF", equation="m_i = P_i,lim / g at y_i (C1 tree) ; sum_err = |sum P_i - P_side| / P_side ; "
          "y_c = sum P_i y_i / sum P_i ; m_R = R / g ; step 2: m_3', m_4' = P'_3,4 / g ; hanger = 2 sum P_i ; "
          "d_max = k b/2 ; F_mount = F_ult/SF ; F_fin = M_fin_ult / (SF z_station)",
          inputs={"p1": "CL-C1-PROOF-P1-LIM", "p2": "CL-C1-PROOF-P2-LIM", "p3": "CL-C1-PROOF-P3-LIM",
                  "p4": "CL-C1-PROOF-P4-LIM", "y1": "CL-C1-PROOF-Y1", "y2": "CL-C1-PROOF-Y2", "y3": "CL-C1-PROOF-Y3",
                  "y4": "CL-C1-PROOF-Y4", "p_side": "CL-C1-PROOF-P-SIDE-LIM", "r": "CL-C1-PROOF-R-LIM",
                  "s2p3": "CL-C1-PROOF-OUT-P3-LIM", "s2p4": "CL-C1-PROOF-OUT-P4-LIM",
                  "sf": P + "requirements.safety_factor_ult",
                  "k_def": P + "requirements.spar_deflection_max", "b": P + "wing.span_m",
                  "f_mount_ult": "CL-C1-MOUNT-F-ULT", "m_fin_ult": "CL-C1-FINHALF-MB-ULT",
                  "z_st": P + "propulsion.stations.z_m", "f_pack": "CL-C1-PACK-CRASH-LOAD", "g": P + "env.g_ms2"},
          units={"b": "m", "z_st": "m", "g": "m/s2"})
def proof_loads(p1, p2, p3, p4, y1, y2, y3, y4, p_side, r, s2p3, s2p4, sf, k_def, b, f_mount_ult, m_fin_ult, z_st,
                f_pack, g):
    s = p1 + p2 + p3 + p4
    f_fin = m_fin_ult / sf / z_st
    return {"wing_p_n": s, "wing_p_kg": s / g, "wing_y_m": (p1 * y1 + p2 * y2 + p3 * y3 + p4 * y4) / s,
            "sum_err": abs(s - p_side) / p_side, "hanger_n": 2.0 * s,
            "pad1_kg": p1 / g, "pad2_kg": p2 / g, "pad3_kg": p3 / g, "pad4_kg": p4 / g,
            "relief_kg": r / g, "s2_pad3_kg": s2p3 / g, "s2_pad4_kg": s2p4 / g,
            "wing_defl_max_m": k_def * b / 2.0,
            "mount_f_n": f_mount_ult / sf, "mount_f_kg": f_mount_ult / sf / g,
            "fin_f_n": f_fin, "fin_f_kg": f_fin / g, "pack_pull_n": f_pack, "pack_pull_kg": f_pack / g}


kit.claim("CL-H1-WING-PROOF-P", "Wing proof load per side (limit, sum of C1's four pads)", calc="CALC-H1-PROOF",
          output="wing_p_n", unit="N", parts=["WNG-001"],
          how="Card GT-08 step 1: four padded sandbags per side at CL-C1-PROOF-Y1..Y4, masses CL-H1-WP-M1..M4.")
kit.claim("CL-H1-WP-SUM-ERR", "Pad sum vs C1's per-side total (consistency of C1's published pads)",
          calc="CALC-H1-PROOF", output="sum_err", unit="-", limit=("<=", 0.005),
          how="Re-run after C1 re-publishes; a mismatch means a pad or the total moved without the other.")
kit.claim("CL-H1-WING-PROOF-Y", "Wing proof load centroid per side", calc="CALC-H1-PROOF", output="wing_y_m", unit="m",
          limit=("<=", 0.575), how="Moment centroid of C1's pads; equals CL-C1-PROOF-PIVOT-Y.")
kit.claim("CL-H1-WP-HANGER", "Whiffletree hanger load, both sides (if the tree is used)", calc="CALC-H1-PROOF",
          output="hanger_n", unit="N", how="Card GT-08 option B: bucket of sand at the hanger, tree mass counted in it.")
kit.claim("CL-H1-WP-M1", "Wing proof pad 1 mass per side (limit)", calc="CALC-H1-PROOF", output="pad1_kg", unit="kg",
          how="Card GT-08: weigh each sandbag on the calibrated 1 g scale to +/-5 g.")
kit.claim("CL-H1-WP-M2", "Wing proof pad 2 mass per side (limit)", calc="CALC-H1-PROOF", output="pad2_kg", unit="kg",
          how="Card GT-08: weigh each sandbag on the calibrated 1 g scale to +/-5 g.")
kit.claim("CL-H1-WP-M3", "Wing proof pad 3 mass per side (limit)", calc="CALC-H1-PROOF", output="pad3_kg", unit="kg",
          how="Card GT-08: weigh each sandbag on the calibrated 1 g scale to +/-5 g.")
kit.claim("CL-H1-WP-M4", "Wing proof pad 4 mass per side (limit; C1 claim CL-C1-PROOF-P4-LIM)", calc="CALC-H1-PROOF",
          output="pad4_kg", unit="kg", how="Card GT-08: weigh each sandbag on the calibrated 1 g scale to +/-5 g.")
kit.claim("CL-H1-WP-RELIEF-M", "Relief counterweight at each motor tube (limit, upward over a pulley)",
          calc="CALC-H1-PROOF", output="relief_kg", unit="kg",
          how="Card GT-08 step 1: ball-bearing pulley; spring-scale check of the sling tension within 3 % before loading.")
kit.claim("CL-H1-WP-S2-M3", "Step 2 (outboard, V-block at y 0.32 m): pad 3 mass (limit)", calc="CALC-H1-PROOF",
          output="s2_pad3_kg", unit="kg", how="Card GT-08 step 2, each side in turn (CR-C1-27).")
kit.claim("CL-H1-WP-S2-M4", "Step 2 (outboard, V-block at y 0.32 m): pad 4 mass (limit)", calc="CALC-H1-PROOF",
          output="s2_pad4_kg", unit="kg", how="Card GT-08 step 2, each side in turn (CR-C1-27).")
kit.claim("CL-H1-WING-DEFL-MAX", "Tip deflection allowed at limit", calc="CALC-H1-PROOF", output="wing_defl_max_m",
          unit="m", how="Card GT-08: dial gauge or ruler at the tip; and no permanent set after unloading.")
kit.claim("CL-H1-MOUNT-PROOF-F", "Motor-mount proof load (limit)", calc="CALC-H1-PROOF", output="mount_f_n",
          unit="N", how="Card GT-09: hang from each mount in -x and in y.")
kit.claim("CL-H1-FIN-PROOF-F", "Fin + tube proof load at the station (limit)", calc="CALC-H1-PROOF",
          output="fin_f_n", unit="N", how="Card GT-09: hang at the motor station, side-load in y, wing held at the spar.")
kit.claim("CL-H1-PACK-PULL-F", "Pack retention pull (ultimate, dummy pack)", calc="CALC-H1-PROOF",
          output="pack_pull_n", unit="N",
          how="Card GT-10: pack-size dummy at the heaviest GT-05 pack mass; pulled in x, y, z to this value.")


# ---------------------------------------------------------------- 6. four-motor restrained run
@kit.calc("CALC-H1-RESTRAINT", equation="F_tie = SF (n T_lim - m g)",
          inputs={"n": P + "propulsion.n_motors", "t_lim": "CL-C1-T-LIMIT", "m": P + "requirements.mtow_gate_kg",
                  "g": P + "env.g_ms2", "sf": "ASM-H1-RESTRAINT-SF"},
          units={"m": "kg", "g": "m/s2"})
def restraint(n, t_lim, m, g, sf):
    f = sf * (n * t_lim - m * g)
    return {"tie_n": f, "tie_kg": f / g, "per_tie_n": f / 4.0}


kit.claim("CL-H1-RESTRAINT-F", "Tie-down force, restrained four-motor run", calc="CALC-H1-RESTRAINT",
          output="tie_n", unit="N", how="T-H1-RESTRAINT-PULL: pull each of the 4 straps to the per-strap value.")
kit.claim("CL-H1-RESTRAINT-PER-TIE", "Tie-down force per strap (4 straps)", calc="CALC-H1-RESTRAINT",
          output="per_tie_n", unit="N", how="Spring scale on each strap before the run.")


# ---------------------------------------------------------------- 7. pack acceptance lines
@kit.calc("CALC-H1-PACK", equation="C_min = frac C_nom ; R_10C = R_25C k_cold",
          inputs={"c": P + "battery.capacity_ah", "frac": P + "requirements.pack_capacity_min_frac",
                  "r": "ASM-E2-R-CELL", "k_cold": "ASM-E2-COLD-R"},
          units={"c": "Ah"})
def pack_lines(c, frac, r, k_cold):
    return {"cap_min_ah": c * frac, "ir25_max_mohm": 5.0, "ir10_max_mohm": 5.0 * k_cold,
            "ir25_expect_mohm": r * 1000.0, "ir10_expect_mohm": r * 1000.0 * k_cold}


kit.claim("CL-H1-PACK-CAP-MIN", "Pack capacity acceptance (1C to 3.5 V/cell)", calc="CALC-H1-PACK",
          output="cap_min_ah", unit="Ah", how="Card GT-05 (T-E2-CAPACITY); pack_log.csv capacity_mah.")
kit.claim("CL-H1-PACK-IR10-MAX", "Pack IR acceptance at 10 degC", calc="CALC-H1-PACK", output="ir10_max_mohm",
          unit="mOhm/cell",
          how="Card GT-05 (T-E2-IR): E2's 5 mOhm/cell at 25 degC x the cold factor; pack_log.csv ir_mohm_cell_10c.")


# ---------------------------------------------------------------- 8. R2 rigs for the structures and avionics tests (CR-A1-41)
kit.source("SRC-H1-JACOBS-EQUIP", "Jacobs Institute, UC Berkeley: Labs and equipment", kind="web",
           url="https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/",
           where="Electronics Lab (studio 110): soldering irons, oscilloscopes and power supplies, multi-meters, Saleae "
                 "logic analyzer, heat guns. Woodshop: Delta variable-speed drill press, band saw, table saw. Metal shop: "
                 "Clausing drill press, Bailey 20-ton press, hand tools. No tool-lending list on the page; use in the "
                 "lab is with a Maker Pass. Read 2026-11-09.", status="CHECKED")
kit.assumption("ASM-H1-OPTLEVER", "Mount-stiffness rig: optical lever and load steps",
               "T-C4-MOUNT-STIFF read by a laser pointer reflected off a 10 mm mirror bonded to the motor can, onto "
               "mm paper on a wall L = 5.0 m away (spot moves 2 theta L); a second mirror on the collar subtracts tube "
               "and stub rotation. Spot centre read to +/-0.3 mm from a tripod phone photo against a 1 mm grid. Loads "
               "0.5, 1.0, 1.5 kg at the prop nut. For comparison, C4's two dial gauges (0.01 mm) are 0.030 m apart.",
               basis="optical lever is the standard way to read sub-milliradian rotations without a fine gauge; "
                     "R3: wall 3.0 -> 5.0 m (a corridor) and photo read-out, because C4's need rose to ~1 970 N m/rad "
                     "(15:01 re-publish) and the spot shrinks with it; laser pointer and mirror are team-owned",
               value={"L_m": 5.0, "read_mm": 0.3, "load_kg": [0.5, 1.0, 1.5], "dial_res_mm": 0.01,
                      "gauge_s_m": 0.030}, unit="m,mm,kg,mm,m")
kit.assumption("ASM-H1-MSTIFF-PASS", "Mount rocking-stiffness pass level: floor 1 100 N m/rad (both axes)",
               "GT-17 passes a mount whose measured rocking stiffness is >= max(1 100, CL-C4-D3-MOUNT-K-REQ) about y "
               "and about z.",
               basis="CR-C4-41 set 1 100 over C4's 1 030; C4's 15:01 re-publish raised the need above that floor, so "
                     "the card follows the live claim and the floor only stops it falling below CR-C4-41",
               value=1100.0, unit="N m/rad")


@kit.calc("CALC-H1-MOUNT-STIFF", equation="k_pass = max(k_floor, k_req) ; a = x_mount - x_prop ; theta = F a / k_pass ; "
          "spot = 2 theta L ; u_k = read / spot_pass ; dial = theta(0.5 kg) s",
          inputs={"k_floor": "ASM-H1-MSTIFF-PASS", "k_req": "CL-C4-D3-MOUNT-K-REQ", "k_nom": "ASM-C4-MOUNT-K-ROCK",
                  "xm": P + "propulsion.stations.x_mount_m", "xp": P + "propulsion.stations.x_prop_plane_m",
                  "rig": "ASM-H1-OPTLEVER", "f_proof": "CL-H1-MOUNT-PROOF-F", "g": P + "env.g_ms2"},
          units={"xm": "m", "xp": "m", "g": "m/s2"})
def mount_stiff(k_floor, k_req, k_nom, xm, xp, rig, f_proof, g):
    k_pass = max(k_floor, k_req)
    a = xm - xp                                                # load point no closer than the prop plane: least signal
    f_max = max(rig["load_kg"]) * g
    th_pass = f_max * a / k_pass
    th_nom = f_max * a / k_nom
    spot_pass = 2.0 * th_pass * rig["L_m"] * 1000.0
    th_dial = min(rig["load_kg"]) * g * a / k_pass
    return {"k_pass": k_pass, "arm_m": a, "spot_pass_mm": spot_pass,
            "spot_nom_mm": 2.0 * th_nom * rig["L_m"] * 1000.0,
            "spot_accept_mm": spot_pass - rig["read_mm"], "u_k_frac": rig["read_mm"] / spot_pass,
            "dial_diff_um": th_dial * rig["gauge_s_m"] * 1e6, "load_frac": f_max / f_proof,
            "nom_over_pass": k_nom / k_pass}


kit.claim("CL-H1-MSTIFF-K-PASS", "GT-17 rocking-stiffness pass level", calc="CALC-H1-MOUNT-STIFF", output="k_pass",
          unit="N m/rad", limit=(">=", "CL-C4-D3-MOUNT-K-REQ"),
          how="CR-C4-41; re-run whenever C4 re-publishes CL-C4-D3-MOUNT-K-REQ.")
kit.claim("CL-H1-MSTIFF-SPOT-ACCEPT", "T-C4-MOUNT-STIFF acceptance: spot travel at 1.5 kg (can minus collar)",
          calc="CALC-H1-MOUNT-STIFF", output="spot_accept_mm", unit="mm",
          how="Card GT-17: net spot travel at 1.5 kg <= this value in y and in z passes k >= CL-H1-MSTIFF-K-PASS.")
kit.claim("CL-H1-MSTIFF-SPOT-NOM", "Spot travel expected at C4's rocking-stiffness estimate", calc="CALC-H1-MOUNT-STIFF",
          output="spot_nom_mm", unit="mm", how="Informational: what the mount as estimated reads on GT-17.")
kit.claim("CL-H1-MSTIFF-NOM-RATIO", "C4's stiffness estimate / GT-17 pass level", calc="CALC-H1-MOUNT-STIFF",
          output="nom_over_pass", unit="-",
          how="Informational: below 1 the mount as estimated is expected to fail GT-17 (CR-H1-24 to C4).")
kit.claim("CL-H1-MSTIFF-U", "Mount stiffness relative U95 at the pass line", calc="CALC-H1-MOUNT-STIFF",
          output="u_k_frac", unit="-", limit=("<=", 0.10), how="T-H1-RIG-CHECK: read a 1.00 mm shim step on the wall.")
kit.claim("CL-H1-MSTIFF-DIAL-UM", "Dial-gauge difference at C4's 0.5 kg load, at the pass stiffness",
          calc="CALC-H1-MOUNT-STIFF", output="dial_diff_um", unit="um",
          how="Informational: below one 10 um division, so C4's dial-gauge readout cannot resolve the pass line "
              "(CR-H1-10); GT-17 uses the optical lever.")
kit.claim("CL-H1-MSTIFF-LOAD-FRAC", "Largest mount-stiffness load / mount proof load", calc="CALC-H1-MOUNT-STIFF",
          output="load_frac", unit="-", limit=("<=", 0.8), how="Load steps set in ASM-H1-OPTLEVER.")

kit.assumption("ASM-H1-TAP", "Tap-test acquisition", "FFT of FC raw IMU (INS_LOG_BAT_MASK, batch sampler) at "
               "1 000 Hz or more; the sampling rate must be >= 2.5 x the highest frequency to be read (anti-alias "
               "margin). A phone accelerometer app (typically ~400 Hz) is used only for the wing modes below 80 Hz.",
               basis="Nyquist 2 x plus a 25 % roll-off margin of the IMU's digital low-pass",
               value={"fs_fc_hz": 1000.0, "fs_phone_hz": 400.0, "k_fs": 2.5}, unit="Hz,Hz,-", status="UNVERIFIED")


@kit.calc("CALC-H1-TAP", equation="f_op = n/60 x {1, 2} at hover, cruise, cap ; window = f_op (1 +/- s) ; "
          "fs_req = k max(f_pred, top window)",
          inputs={"n_h": "CL-B4-HOVER-RPM", "n_c": "CL-B4-CRUISE-RPM", "n_cap": P + "propulsion.rpm_max",
                  "s": P + "requirements.vibration_sep_frac", "f_up": "CL-C4-D3-F1-UP", "f_lo": "CL-C4-D3-F1-LO",
                  "acq": "ASM-H1-TAP"},
          units={"n_cap": "rpm"})
def tap(n_h, n_c, n_cap, s, f_up, f_lo, acq):
    rows = []
    for name, n in (("hover", n_h), ("cruise", n_c), ("cap", n_cap)):
        for h in (1, 2):
            f = n / 60.0 * h
            rows.append([f"{h}P {name}", round(f, 1), round(f * (1 - s), 1), round(f * (1 + s), 1)])
    top = max(r[3] for r in rows)
    fs_req = acq["k_fs"] * max(top, f_up, f_lo)
    return {"windows": rows, "top_hz": top, "fs_req_hz": fs_req, "fs_fc_hz": acq["fs_fc_hz"],
            "phone_max_hz": acq["fs_phone_hz"] / acq["k_fs"]}


kit.claim("CL-H1-TAP-FS-FC", "FC raw-IMU sampling rate used for tap tests", calc="CALC-H1-TAP", output="fs_fc_hz",
          unit="Hz", how="F4/F3 log setting; confirm in the .bin header (T-H1-RIG-CHECK).")
kit.claim("CL-H1-TAP-FS-REQ", "Tap-test sampling rate needed", calc="CALC-H1-TAP", output="fs_req_hz", unit="Hz",
          limit=("<=", "CL-H1-TAP-FS-FC"),
          how="T-H1-RIG-CHECK: log a 200 Hz tuning-fork / phone-speaker tone on the FC raw IMU and find it in the FFT.")
kit.claim("CL-H1-TAP-PHONE-MAX", "Highest frequency a ~400 Hz phone accelerometer reads", calc="CALC-H1-TAP",
          output="phone_max_hz", unit="Hz",
          how="Informational: the fin-station modes (~273-281 Hz) and 2P at the cap (312 Hz) are above it (CR-H1-11).")

kit.assumption("ASM-H1-BEND", "Tube bend rig", "Span 0.80 m on two 22 mm dowels, centre load 0.5-4.0 kg through a "
               "printed 22 mm saddle; deflection by a dial indicator on a magnetic base (0.01 mm) if Jacobs lends one, "
               "else a digital caliper depth rod against a fixed reference bar (0.02 mm read, +/-0.03 mm U95).",
               basis="C4's T-C4-TUBE-BEND procedure; caliper fallback from the borrow list",
               value={"span_m": 0.80, "load_kg": 4.0, "u_defl_mm": 0.03}, unit="m,kg,mm")


@kit.calc("CALC-H1-BEND", equation="I = pi/64 (D^4 - d^4) ; delta = F L^3 / (48 E I) ; sigma = F L D / (8 I) ; "
          "u_E = u_delta / delta",
          inputs={"od": P + "fins.tube.od_m", "idm": P + "fins.tube.id_m", "e_lo": "ASM-C4-E-TUBE-LO",
                  "rig": "ASM-H1-BEND", "g": P + "env.g_ms2"},
          units={"od": "m", "idm": "m", "g": "m/s2"})
def bend(od, idm, e_lo, rig, g):
    i = math.pi / 64.0 * (od ** 4 - idm ** 4)
    f = rig["load_kg"] * g
    d = f * rig["span_m"] ** 3 / (48.0 * e_lo * i)
    return {"I_m4": i, "defl_elo_mm": d * 1000.0, "defl_accept_mm": d * 1000.0 - rig["u_defl_mm"],
            "sigma_mpa": f * rig["span_m"] * od / (8.0 * i) / 1e6, "u_e_frac": rig["u_defl_mm"] / (d * 1000.0)}


kit.claim("CL-H1-TUBE-DEFL-ACCEPT", "Aloft tube bend acceptance: centre deflection at 4 kg (E >= 70 GPa)",
          calc="CALC-H1-BEND", output="defl_accept_mm", unit="mm", parts=["WNG-002"],
          how="Card GT-16 (T-C4-TUBE-BEND on BOM line W03 by 10 Dec): slope of 8 load steps; deflection at 4 kg <= "
              "this value passes; result to I1 (CR-I1-08) and C4.")
kit.claim("CL-H1-TUBE-SIGMA", "Bend-test peak stress at 4 kg", calc="CALC-H1-BEND", output="sigma_mpa", unit="MPa",
          limit=("<=", 100.0), how="Far below any CF tube strength: the spare tube stays usable after the test.")
kit.claim("CL-H1-TUBE-E-U", "Tube modulus relative U95 from the deflection read", calc="CALC-H1-BEND",
          output="u_e_frac", unit="-", limit=("<=", 0.05), how="T-H1-RIG-CHECK: read a 1.00 mm gauge block.")

# R3 (CR-C2-15): torsion stiffness GJ on the same specimen, read between two lasers clamped on the tube so grip slip
# in the V-blocks drops out; plus a ring-crush coupon from the offcut for the hoop (transverse) modulus C2's FEA uses.
kit.assumption("ASM-H1-TORSION", "Tube torsion rig: two lasers 0.30 m apart, 0.30 m lever, 2.0 kg",
               "0.40 m of the bend specimen clamped in printed V-blocks at one end; a 0.30 m lever clamped at the "
               "other end loaded 0.5-2.0 kg in 0.5 kg steps, both senses. Two laser pointers in printed clamps on the "
               "tube 0.30 m apart (gauge length) throw spots on a wall 3.0 m away; twist over the gauge length = "
               "atan(s2/L) - atan(s1/L). Spots read to +/-1 mm.",
               basis="the relative twist between two stations removes grip slip and lever-clamp rotation, which "
                     "dominate a single-laser reading on a printed grip",
               value={"lever_m": 0.30, "load_kg": 2.0, "gauge_m": 0.30, "wall_m": 3.0, "read_mm": 1.0},
               unit="m,kg,m,m,mm")
kit.assumption("ASM-H1-RING", "Ring-crush coupon for the tube hoop modulus",
               "A 20 mm long ring cut from the tube offcut, crushed between flat plates on the 20 kgf cell under the "
               "Jacobs drill press to 20 N in 4 N steps; diametral deflection by dial indicator (0.01 mm) on the "
               "upper plate. Thin-ring result: delta = 0.1488 P R^3 / (E_hoop I), I = b t^3 / 12.",
               basis="Roark, thin circular ring under diametral load (case of two opposite point loads); a standard "
                     "way to get the hoop modulus of a wound tube without a strain gauge",
               value={"b_m": 0.020, "p_n": 20.0, "dial_mm": 0.01}, unit="m,N,mm", status="UNVERIFIED")


@kit.calc("CALC-H1-TORSION", equation="J = pi/32 (D^4 - d^4) ; T = m g l ; dtheta = T L_g / (G J) ; "
          "s = L_w dtheta ; u_GJ = sqrt2 read / s(G_hi) ; tau = T (D/2) / J ; ring: R = (D+d)/4, t = (D-d)/2, "
          "I = b t^3/12, delta = 0.1488 P R^3 / (E_t I), sigma = 0.318 P R (t/2) / I",
          inputs={"od": P + "fins.tube.od_m", "idm": P + "fins.tube.id_m", "g_lo": "ASM-C4-G-TUBE-LO",
                  "g_nom": "ASM-C4-G-TUBE", "g_hi": "ASM-C4-G-TUBE-HI", "e_t": "ASM-C2-TUBE-ET",
                  "rig": "ASM-H1-TORSION", "ring": "ASM-H1-RING", "g": P + "env.g_ms2"},
          units={"od": "m", "idm": "m", "g": "m/s2"})
def torsion(od, idm, g_lo, g_nom, g_hi, e_t, rig, ring, g):
    j = math.pi / 32.0 * (od ** 4 - idm ** 4)
    t = rig["load_kg"] * g * rig["lever_m"]
    dth = {k: t * rig["gauge_m"] / (gg * j) for k, gg in (("lo", g_lo), ("nom", g_nom), ("hi", g_hi))}
    s_hi = rig["wall_m"] * dth["hi"] * 1000.0
    r = (od + idm) / 4.0
    tw = (od - idm) / 2.0
    i_r = ring["b_m"] * tw ** 3 / 12.0
    delta = 0.1488 * ring["p_n"] * r ** 3 / (e_t * i_r)
    return {"J_m4": j, "torque_nm": t, "gj_lo": g_lo * j, "gj_nom": g_nom * j,
            "dtheta_lo_deg": math.degrees(dth["lo"]), "spot_hi_mm": s_hi,
            "u_gj": math.sqrt(2.0) * rig["read_mm"] / s_hi, "tau_mpa": t * (od / 2.0) / j / 1e6,
            "ring_defl_mm": delta * 1000.0, "ring_u": math.sqrt(2.0) * ring["dial_mm"] / (delta * 1000.0),
            "ring_sigma_mpa": 0.318 * ring["p_n"] * r * (tw / 2.0) / i_r / 1e6}


kit.claim("CL-H1-TORS-GJ-LO", "Tube GJ at C4's low corner (G 3 GPa)", calc="CALC-H1-TORSION", output="gj_lo",
          unit="N m2", parts=["WNG-002"],
          how="Card GT-16 step 4 (T-C4-TUBE-TORSION, CR-C2-15): measured GJ = T L_g / dtheta from the slope of 4 "
              "steps, both senses; report GJ and G = GJ / J; >= this value keeps C4's low corner conservative.")
kit.claim("CL-H1-TORS-U", "GJ relative U95 at the stiffest corner (G 10 GPa, smallest spot)", calc="CALC-H1-TORSION",
          output="u_gj", unit="-", limit=("<=", 0.05), how="T-H1-RIG-CHECK: both lasers on a 1.00 mm shim step.")
kit.claim("CL-H1-TORS-TAU", "Torsion-test peak shear stress at 2.0 kg", calc="CALC-H1-TORSION", output="tau_mpa",
          unit="MPa", limit=("<=", 30.0), how="Far below any CF tube shear strength: the spare tube stays usable.")
kit.claim("CL-H1-RING-DEFL", "Ring-crush deflection at 20 N for E_hoop 8 GPa", calc="CALC-H1-TORSION",
          output="ring_defl_mm", unit="mm",
          how="Card GT-16 step 5: E_hoop = 0.1488 P R^3 / (delta I) from the slope; to C2 for ASM-C2-TUBE-ET.")
kit.claim("CL-H1-RING-U", "Ring-crush E_hoop relative U95 (dial read)", calc="CALC-H1-TORSION", output="ring_u",
          unit="-", limit=("<=", 0.10), how="Borrowed 0.01 mm dial indicator; a caliper cannot read this.")
kit.claim("CL-H1-RING-SIGMA", "Ring-crush peak bending stress at 20 N", calc="CALC-H1-TORSION",
          output="ring_sigma_mpa", unit="MPa", limit=("<=", 100.0), how="Elastic: the ring is not damaged.")

# R3 (CR-C6-33, CR-C6-39): the strip anchor now needs a 15:1 lever; the same lever keeps a 9:1 hole for small coupons.
kit.assumption("ASM-H1-LEVER", "Coupon lever frame 15:1 / 9:1, water jugs to 20 kg", "2x4 (38 x 89 mm) lever 1.0 m "
               "long on an M8 pivot; coupon clevis at 0.060 m (15:1) or 0.100 m (9:1) from the pivot, jug hook at "
               "0.900 m. Pivot and both clevis holes in a pair of 3 mm steel side plates 40 x 200 mm, each plate held "
               "to the lever by 4 x M6 through-bolts; lever tare balanced by a counterweight on the short side. "
               "Water filled slowly from a hose; jug weighed after failure.",
               basis="CR-C6-39 asks >= 2 660 N for the strip anchor; 15:1 x 20 kg = 2 940 N. The 9:1 hole keeps "
                     "resolution for the 40-300 N coupons. Steel plates because bare wood across the grain does not "
                     "carry the pivot bearing (CALC-H1-LEVER)",
               value={"arm_jug_m": 0.90, "arm_hi_m": 0.060, "arm_lo_m": 0.100, "jug_max_kg": 20.0, "b_m": 0.038,
                      "h_m": 0.089, "bolt_m": 0.008, "plate_t_m": 0.003, "n_m6": 4, "m6_m": 0.006},
               unit="m,m,m,kg,m,m,m,m,-,m")
kit.assumption("ASM-H1-WOOD", "Construction lumber allowables (Douglas fir-larch No. 2)", "Bending 6.0 MPa, "
               "compression perpendicular to grain 4.3 MPa (bolt bearing across the grain).",
               basis="NDS supplement reference design values for DF-L No. 2 (Fb 900 psi, Fc-perp 625 psi), rounded "
                     "down", value={"fb_mpa": 6.0, "fcp_mpa": 4.3}, unit="MPa", status="UNVERIFIED")


@kit.calc("CALC-H1-LEVER", equation="F_cap = (a_jug / a_coupon) m_jug g ; F_need,15 = 1.25 max(F_anchor, F_anchor,est, "
          "F_insert) ; F_need,9 = 1.25 F_anchor ; sigma = m_jug g a_jug / (b h^2/6) ; F_pivot = F_cap + m_jug g ; "
          "p_wood = F_pivot / (d b) ; p_plate = F_pivot / (2 d t) ; p_m6 = F_pivot / (n d6 b)",
          inputs={"lev": "ASM-H1-LEVER", "f_strip": "CL-C6-STRIP-ANCHOR-F", "f_est": "CL-C6-STRIP-ANCHOR-F-EST",
                  "f_ins": "ASM-C6-INSERT-PULL", "k": "ASM-H1-RANGE-FACTOR", "g": P + "env.g_ms2"},
          units={"g": "m/s2"})
def lever(lev, f_strip, f_est, f_ins, k, g):
    w = lev["jug_max_kg"] * g
    cap_hi = lev["arm_jug_m"] / lev["arm_hi_m"] * w
    f_piv = cap_hi + w
    return {"cap_n": cap_hi, "cap9_n": lev["arm_jug_m"] / lev["arm_lo_m"] * w,
            "need_n": k * max(f_strip, f_est, f_ins), "need9_n": k * f_strip,
            "sigma_mpa": w * lev["arm_jug_m"] / (lev["b_m"] * lev["h_m"] ** 2 / 6.0) / 1e6,
            "wood_brg_mpa": f_piv / (lev["bolt_m"] * lev["b_m"]) / 1e6,
            "plate_brg_mpa": f_piv / (2.0 * lev["bolt_m"] * lev["plate_t_m"]) / 1e6,
            "m6_brg_mpa": f_piv / (lev["n_m6"] * lev["m6_m"] * lev["b_m"]) / 1e6}


kit.claim("CL-H1-LEVER-CAP", "Coupon lever capacity, 15:1 hole", calc="CALC-H1-LEVER", output="cap_n", unit="N",
          how="T-H1-LEVER-CAL: 3.000 kg check mass at the 15:1 clevis balances 0.200 kg at the jug hook within 2 %.")
kit.claim("CL-H1-LEVER-NEED", "Coupon load the 15:1 hole must reach (1.25 x strip anchor estimate, CR-C6-39)",
          calc="CALC-H1-LEVER", output="need_n", unit="N", limit=("<=", "CL-H1-LEVER-CAP"),
          how="Re-run when C6/C4 change the anchor force.")
kit.claim("CL-H1-LEVER-CAP9", "Coupon lever capacity, 9:1 hole", calc="CALC-H1-LEVER", output="cap9_n", unit="N",
          how="T-H1-LEVER-CAL: 2.000 kg at the 9:1 clevis balances 0.222 kg within 2 %.")
kit.claim("CL-H1-LEVER-NEED9", "Load the 9:1 hole must reach (1.25 x CL-C6-STRIP-ANCHOR-F, CR-C6-33)",
          calc="CALC-H1-LEVER", output="need9_n", unit="N", limit=("<=", "CL-H1-LEVER-CAP9"),
          how="CR-C6-33 frame line (>= 1 560 N at C4 R4); the anchor runs on the 15:1 hole regardless.")
kit.claim("CL-H1-LEVER-SIGMA", "Lever bending stress at full jug", calc="CALC-H1-LEVER", output="sigma_mpa",
          unit="MPa", limit=("<=", 6.0), how="ASM-H1-WOOD Fb; inspect the 2x4 for knots at the plates.")
kit.claim("CL-H1-LEVER-WOOD-BRG", "Pivot bearing on bare wood (why the steel plates are required)",
          calc="CALC-H1-LEVER", output="wood_brg_mpa", unit="MPa",
          how="Informational: above 4.3 MPa across the grain, so the M8 never bears on the wood directly.")
kit.claim("CL-H1-LEVER-PLATE-BRG", "Pivot bearing on the two 3 mm steel plates", calc="CALC-H1-LEVER",
          output="plate_brg_mpa", unit="MPa", limit=("<=", 150.0), how="Mild steel; holes drilled, not punched.")
kit.claim("CL-H1-LEVER-M6-BRG", "Plate-to-lever M6 bolt bearing on the wood across the grain", calc="CALC-H1-LEVER",
          output="m6_brg_mpa", unit="MPa", limit=("<=", 4.3), how="ASM-H1-WOOD Fc-perp; washers both sides.")


@kit.calc("CALC-H1-D5", equation="F_req = k F_peak,U / g [kgf] ; u_ratio = sqrt2 U_cell / F_plateau,L ; "
          "theta_acc = atan(mu) + u_theta",
          inputs={"f_pk": "CL-D5-F-PEAK-UPPER", "f_l": "CL-D5-F-PLATEAU-LOWER", "k": "ASM-H1-RANGE-FACTOR",
                  "u_t": "CL-H1-T-U95", "mu": "ASM-D5-PAD-MU", "inc": "ASM-H1-INCLINO", "g": P + "env.g_ms2"},
          units={"g": "m/s2"})
def d5(f_pk, f_l, k, u_t, mu, inc, g):
    return {"cell_req_kgf": k * f_pk / g, "ratio_u": math.sqrt(2.0) * u_t / f_l,
            "mu_angle_deg": math.degrees(math.atan(mu)), "mu_accept_deg": math.degrees(math.atan(mu)) + inc}


kit.assumption("ASM-H1-INCLINO", "Phone inclinometer U95 0.3 deg on a tilt board", "Phone level app on the board "
               "face, zeroed on the flat board, read at the moment of slip from video; U95 0.3 deg.",
               basis="typical phone MEMS inclinometer after a two-way zero", value=0.3, unit="deg", status="UNVERIFIED")
kit.claim("CL-H1-D5-CELL-REQ", "Thrust cell range needed for the D5 crush coupon", calc="CALC-H1-D5",
          output="cell_req_kgf", unit="kgf", limit=("<=", "CL-H1-THRUST-CAP"),
          how="Card GT-15 D5 block: the 20 kgf cell under the drill-press table carries the crush.")
kit.claim("CL-H1-D5-RATIO-U", "U95 of the U/L plateau ratio", calc="CALC-H1-D5", output="ratio_u", unit="-",
          limit=("<=", 0.01), how="Against D5's bias tolerance 0.01 (CL-D5-BIAS-ERR); from T-H1-STAND-CAL.")
kit.claim("CL-H1-MU-ANGLE-ACCEPT", "T-D5-PAD-MU acceptance slip angle (mu 0.7 + U95)", calc="CALC-H1-D5",
          output="mu_accept_deg", unit="deg",
          how="Card GT-15: mean slip angle of 5 runs per surface >= this value passes mu >= 0.7.")

kit.assumption("ASM-H1-GPS-U", "Phone GPS distance U95 5 m", "Distance to the 100 m point from two phone GPS fixes "
               "(or a pace count checked against a 30 m tape); U95 5 m.", basis="consumer GPS open-sky CEP",
               value=5.0, unit="m", status="UNVERIFIED")
kit.assumption("ASM-H1-LOG-DT", "Output log step 0.1 s", "RCOU / ESC rpm are read from the DataFlash log at "
               "10 Hz or faster; the stop time is resolved to 0.1 s.", basis="ArduPilot default log rates",
               value=0.1, unit="s", status="UNVERIFIED")


@kit.calc("CALC-H1-FIELD", equation="d_walk = d_min + U_gps ; t_stop_acc = t_max - dt_log",
          inputs={"d": P + "requirements.range_check_min_m", "u": "ASM-H1-GPS-U",
                  "t": P + "requirements.estop_time_max_s", "dt": "ASM-H1-LOG-DT"},
          units={"d": "m", "t": "s"})
def field(d, u, t, dt):
    return {"walk_m": d + u, "stop_accept_s": t - dt}


kit.claim("CL-H1-RANGE-WALK", "T-F5-RANGE walk-out distance (guard-banded)", calc="CALC-H1-FIELD", output="walk_m",
          unit="m", how="Card GT-14: read RSSI/LQ at >= this distance, 25 mW, 8 positions; pass LQ >= 0.9 and "
          "best RSSI >= P:requirements.rc_rssi_check_min_dbm (-93.8 dBm) in every position.")
kit.claim("CL-H1-ESTOP-ACCEPT", "Arm/kill acceptance: switch to zero output in the log", calc="CALC-H1-FIELD",
          output="stop_accept_s", unit="s", how="Card GT-12 (T-H1-ARM-KILL): <= this value from the switch edge "
          "to all RCOU at the disarmed value, 5 trials.")


# ---------------------------------------------------------------- 9. R3: fin proof instrumentation (CR-C4-36, CR-C4-38)
kit.assumption("ASM-H1-FP-PRED", "C4's 3-D predictions at the two gauge sites, 1.0 x L4 (limit)",
               "Paper face 5 mm below the shoe leg edge at x ~0.30 m: 3.4-4.3 MPa at E_face 4 GPa; CF edge strip 10 mm "
               "forward of the collar cheek: 88 MPa at E 110 GPa.",
               basis="team/C4/CHANGE-REQUESTS.md CR-C4-38 (S1 3-D FE, shoe as drawn); not yet published as claims",
               value={"face_mpa": [3.4, 4.3], "e_face_gpa": 4.0, "strip_mpa": 88.0, "e_strip_gpa": 110.0},
               unit="MPa,GPa,MPa,GPa", status="UNVERIFIED")
kit.assumption("ASM-H1-SG", "Strain-gauge read-out: half bridge (active + dummy) on an HX711 at reduced excitation",
               "350 ohm foil gauges, gauge factor 2.0 +/-1 %, grid 3 x 2.5 mm (I1 G13). Each active gauge is paired "
               "with a dummy gauge bonded on an unloaded offcut of the same material beside the article (temperature "
               "compensation), completed by two 350 ohm 0.1 % resistors; one HX711 per bridge (G06 and G12 boards), "
               "channel A gain 128. The HX711's 4.3 V excitation is dropped to the bridge through 1.5 kohm in each "
               "lead (self-heating on paper over foam). Noise 0.1 uV rms after averaging (2 x the datasheet's "
               "50 nV at 10 SPS for the leads). Shunt calibration: 100 kohm across the dummy arm.",
               basis="Vishay TN-502 self-heating guidance: <= 0.05 W/in2 (78 W/m2) on poor heat sinks such as "
                     "plastics and foam laminates; a dummy gauge on the same substrate cancels apparent strain",
               value={"gf": 2.0, "r_ohm": 350.0, "grid_m2": 7.5e-6, "v_hx_v": 4.3, "r_series_ohm": 1500.0,
                      "noise_v": 1.0e-7, "r_shunt_ohm": 100000.0, "p_dens_max_wm2": 78.0},
               unit="-,ohm,m2,V,ohm,V,ohm,W/m2", status="UNVERIFIED", cites=["SRC-H1-HX711"])
kit.assumption("ASM-H1-SG-STACK", "Gauge + adhesive stiffness vs the paper face (reinforcement estimate)",
               "Polyimide carrier 25 um at 3 GPa plus 10 um cyanoacrylate at 3 GPa, constantan foil 5 um at 160 GPa "
               "over half the grid; foam-board paper face 0.20 mm at 4 GPa.",
               basis="typical foil-gauge construction; face thickness from a caliper read of the board (to confirm)",
               value={"et_gauge_npm": 3e9 * 35e-6 + 160e9 * 5e-6 * 0.5, "et_face_npm": 4e9 * 0.20e-3},
               unit="N/m", status="UNVERIFIED")
kit.assumption("ASM-H1-DIAL", "Dial indicator 25 mm travel, 0.01 mm", "Borrowed long-travel dial indicator on a "
               "magnetic base clamped to the test frame, plunger on the shoe pad along the L4 resultant.",
               basis="Jacobs metal shop hand tools (to ask); fallback caliper depth rod 0.02 mm", value=25.0, unit="mm",
               status="UNVERIFIED")


@kit.calc("CALC-H1-FINPROOF", equation="eps = sigma / E ; V_b = V_hx R / (R + 2 R_s) ; V_out = V_b GF eps / 4 ; "
          "eps_res = 4 (2 noise) / (GF V_b) ; P_g = (V_b/2)^2 / R / A_grid ; eps_shunt = R / (GF (R + R_sh)) ; "
          "d_split = sqrt(d_3D d_shell) ; travel_req = 1.25 d_shell (dial to 1.0 x; rule above) ; reinf = Et_g / Et_face",
          inputs={"pred": "ASM-H1-FP-PRED", "sg": "ASM-H1-SG", "stack": "ASM-H1-SG-STACK", "dial": "ASM-H1-DIAL",
                  "d3": "CL-C4-SIM-FOOT-DEFL", "dsh": "CL-C4-D3-FOOT-DEFL", "sf": P + "requirements.safety_factor_ult"})
def finproof(pred, sg, stack, dial, d3, dsh, sf):
    e_f = pred["e_face_gpa"] * 1e9
    eps_face = [s * 1e6 / e_f for s in pred["face_mpa"]]
    eps_strip = pred["strip_mpa"] * 1e6 / (pred["e_strip_gpa"] * 1e9)
    vb = sg["v_hx_v"] * sg["r_ohm"] / (sg["r_ohm"] + 2.0 * sg["r_series_ohm"])
    vb_bare = sg["v_hx_v"]
    res = 4.0 * 2.0 * sg["noise_v"] / (sg["gf"] * vb)
    pd = (vb / 2.0) ** 2 / sg["r_ohm"] / sg["grid_m2"]
    pd_bare = (vb_bare / 2.0) ** 2 / sg["r_ohm"] / sg["grid_m2"]
    return {"eps_face_lim_ue": [e * 1e6 for e in eps_face], "eps_face_ult_ue": sf * eps_face[1] * 1e6,
            "eps_strip_lim_ue": eps_strip * 1e6, "eps_strip_ult_ue": sf * eps_strip * 1e6,
            "vb_v": vb, "v_face_ult_uv": vb * sg["gf"] * sf * eps_face[1] / 4.0 * 1e6,
            "res_frac": res / eps_face[0], "res_ue": res * 1e6, "p_dens_wm2": pd, "p_dens_bare_wm2": pd_bare,
            "shunt_ue": sg["r_ohm"] / (sg["gf"] * (sg["r_ohm"] + sg["r_shunt_ohm"])) * 1e6,
            "d_split_mm": math.sqrt(d3 * dsh) * 1000.0, "d3_mm": d3 * 1000.0, "dsh_mm": dsh * 1000.0,
            "travel_req_mm": 1.25 * dsh * 1000.0, "travel_mm": dial, "d_shell_ult_mm": sf * dsh * 1000.0,
            "reinf": stack["et_gauge_npm"] / stack["et_face_npm"]}


kit.claim("CL-H1-FP-EPS-FACE-ULT", "Face gauge strain predicted at 1.5 x L4 (upper end of C4's band)",
          calc="CALC-H1-FINPROOF", output="eps_face_ult_ue", unit="ue",
          how="Card GT-09 FP step 4; the limit-level reading (step 3) is the one compared with C4.")
kit.claim("CL-H1-FP-EPS-STRIP-LIM", "Strip gauge strain predicted at 1.0 x L4", calc="CALC-H1-FINPROOF",
          output="eps_strip_lim_ue", unit="ue", how="Card GT-09 FP step 3 (CR-C4-38).")
kit.claim("CL-H1-SG-RES-FRAC", "Gauge 2-sigma resolution / smallest predicted limit strain", calc="CALC-H1-FINPROOF",
          output="res_frac", unit="-", limit=("<=", 0.01),
          how="T-H1-RIG-CHECK: 60 s zero record on each bridge, then the shunt step.")
kit.claim("CL-H1-SG-PDENS", "Gauge self-heating power density at the reduced excitation", calc="CALC-H1-FINPROOF",
          output="p_dens_wm2", unit="W/m2", limit=("<=", 78.0),
          how="Zero drift <= 5 ue over 10 min with the article unloaded (T-H1-RIG-CHECK).")
kit.claim("CL-H1-SG-PDENS-BARE", "Self-heating with the HX711's 4.3 V straight on the bridge (why the 1.5 kohm leads)",
          calc="CALC-H1-FINPROOF", output="p_dens_bare_wm2", unit="W/m2",
          how="Informational: 20 x over the foam-laminate guidance; the reading would drift as the face warms.")
kit.claim("CL-H1-SG-SHUNT", "Shunt-calibration step (100 kohm across the dummy arm)", calc="CALC-H1-FINPROOF",
          output="shunt_ue", unit="ue", how="Card GT-09 FP step 1: each bridge reads this within 1 % before loading.")
kit.claim("CL-H1-SG-REINF", "Gauge stack / paper-face membrane stiffness (reinforcement estimate)",
          calc="CALC-H1-FINPROOF", output="reinf", unit="-",
          how="Informational: the face gauge reads low by up to ~1/(1+ratio); its factor comes from a gauged "
              "T-C4-BOARD-COUPON in 4-point bend (GT-15), not from this estimate.")
kit.claim("CL-H1-FP-DEFL-SPLIT", "Pad deflection at 1.0 x L4 that splits the 3-D and shell predictions",
          calc="CALC-H1-FINPROOF", output="d_split_mm", unit="mm",
          how="Card GT-09 FP step 3: geometric mean of the two predictions (model errors are multiplicative); below "
              "it, the 3-D load path (strips clamped in the cheeks) is the one built.")
kit.claim("CL-H1-FP-TRAVEL-REQ", "Dial travel needed to the 1.0 x step (1.25 x the shell pad deflection at limit)",
          calc="CALC-H1-FINPROOF", output="travel_req_mm", unit="mm", limit=("<=", "ASM-H1-DIAL"),
          how="Borrowed 25 mm indicator, removed before the 1.5 x step; above 1.0 x a steel rule on a fixed bar "
              "(0.5 mm) reads the pad.")
kit.claim("CL-H1-FP-DEFL-SHELL-ULT", "Pad deflection at 1.5 x L4 if the shell path is right", calc="CALC-H1-FINPROOF",
          output="d_shell_ult_mm", unit="mm", how="Informational: sizes the rule and the frame clearance.")


# ---------------------------------------------------------------- 10. R3: ESC film coefficient on a heated dummy (CR-E3-17)
kit.assumption("ASM-H1-ESC-DUMMY", "Heated aluminium ESC dummy for T-E3-ESC-PAD-CFD",
               "45 x 20 x 6 mm aluminium block (14.6 g), a 10 ohm 5 W resistor in a 3 mm slot run at 3.0 W (5.5 V, "
               "power from V and I on two DMMs, +/-1 %), painted matte black (emissivity 0.90 +/- 0.05, as heat-"
               "shrink), on 3 mm XPS (k 0.033 W/m K +/- 10 %) in place of the hook-and-loop so the height above the "
               "pad stays the same, held by the flight strap (same 320 mm2 covered). Thermocouple 1 in a hole at the "
               "block centre, thermocouple 2 on the pad under the XPS, thermocouple 3 in the inflow; same spool, "
               "zero offset checked at ambient (differential +/-0.3 K). Exposed area +/-2.5 % (strap edges).",
               basis="CR-E3-17 (E3's rig) with the conduction path made measurable; solid aluminium is isothermal "
                     "(Bi < 0.01)",
               value={"p_w": 3.0, "l_m": 0.045, "w_m": 0.020, "h_m": 0.006, "eps": 0.90, "rho": 2700.0, "cp": 900.0,
                      "t_k": 313.0, "k_xps": 0.033, "t_xps_m": 0.003, "u_dt_k": 0.3, "u_p": 0.01, "u_a": 0.025,
                      "u_kxps": 0.10, "u_eps": 0.05, "u_fit": 0.005},
               unit="W,m,m,m,-,kg/m3,J/kg K,K,W/m K,m,K,-,-,-,-,-", status="UNVERIFIED")
kit.assumption("ASM-H1-AIR", "Air at 300 K", "nu 15.89e-6 m2/s, k 0.0263 W/m K, Pr 0.707.",
               basis="Incropera Table A.4 (as E3)", value={"nu": 15.89e-6, "k": 0.0263, "pr": 0.707},
               unit="m2/s,W/m K,-", cites=["SRC-E3-INCROPERA"])


@kit.calc("CALC-H1-ESC-CFD", equation="h_lam = 0.664 Re^0.5 Pr^1/3 k/L, Re = U L/nu ; h_pass = h_lam sqrt(f_design) ; "
          "A = L w + 2 h (L + w) - A_strap ; h_r = 4 eps sigma T^3 ; G = k_xps L w / t ; dT = P / (A (h + h_r) + G) ; "
          "tau = m c / (A (h + h_r) + G) ; u_h = rss(dT, P, A, conduction, radiation, fit) ; f_acc = f_d (1 + u_h)^2",
          inputs={"feq": "CL-E3-CFD-FEQ", "u": "CL-E3-CFD-U", "h_exp": "CL-E3-CFD-H-HOV", "strap": "ASM-E3-ESC-STRAP",
                  "d": "ASM-H1-ESC-DUMMY", "air": "ASM-H1-AIR"})
def esc_cfd(feq, u, h_exp, strap, d, air):
    sigma = 5.670e-8
    re = u[0] * d["l_m"] / air["nu"]
    h_lam = 0.664 * re ** 0.5 * air["pr"] ** (1.0 / 3.0) * air["k"] / d["l_m"]
    h_pass = h_lam * math.sqrt(feq[0])
    a = d["l_m"] * d["w_m"] + 2.0 * d["h_m"] * (d["l_m"] + d["w_m"]) - strap
    h_r = 4.0 * d["eps"] * sigma * d["t_k"] ** 3
    g_c = d["k_xps"] * d["l_m"] * d["w_m"] / d["t_xps_m"]
    mc = d["rho"] * d["l_m"] * d["w_m"] * d["h_m"] * d["cp"]
    ua_pass = a * (h_pass + h_r) + g_c
    dt_pass = d["p_w"] / ua_pass
    dt_exp = d["p_w"] / (a * (h_exp + h_r) + g_c)
    q_conv = a * h_pass                                          # shares of the loss at the pass line
    u_h = math.sqrt((d["u_dt_k"] / dt_pass) ** 2 + d["u_p"] ** 2 + d["u_a"] ** 2
                    + (d["u_kxps"] * g_c / q_conv) ** 2 + (d["u_eps"] / d["eps"] * a * h_r / q_conv) ** 2
                    + d["u_fit"] ** 2)
    tau = mc / ua_pass
    return {"h_lam": h_lam, "h_pass": h_pass, "area_m2": a, "dt_pass_k": dt_pass, "dt_exp_k": dt_exp,
            "cond_share": g_c / ua_pass, "tau_s": tau, "run_s": 5.0 * tau, "u_h": u_h,
            "f_accept": feq[0] * (1.0 + u_h) ** 2, "f_design": feq[0]}


kit.claim("CL-H1-ESCCFD-H-PASS", "Film coefficient at the pass line (f = CL-E3-CFD-FEQ design hover)",
          calc="CALC-H1-ESC-CFD", output="h_pass", unit="W/m2 K", parts=["PRP-002-UR", "FIN-007-UR"],
          how="Card GT-04 step 2b: h = (P - G dT_xps - A h_r dT) / (A dT) at steady state.")
kit.claim("CL-H1-ESCCFD-DT-PASS", "Dummy rise above inflow at the pass line, 3.0 W", calc="CALC-H1-ESC-CFD",
          output="dt_pass_k", unit="K", limit=("<=", 53.0),
          how="Limit: 30 degC lab + rise stays under the ASA pad's 83 degC (HDT 93 - 10 K).")
kit.claim("CL-H1-ESCCFD-DT-EXP", "Dummy rise expected at E3's CFD film (SST, fine grid)", calc="CALC-H1-ESC-CFD",
          output="dt_exp_k", unit="K", how="Informational: what a CFD-consistent run reads.")
kit.claim("CL-H1-ESCCFD-RUN", "Hover-power hold needed to reach steady state (5 tau)", calc="CALC-H1-ESC-CFD",
          output="run_s", unit="s",
          how="Card GT-04 step 2b holds hover thrust this long; E3's ~5 min is about 2 tau (CR-H1-21).")
kit.claim("CL-H1-ESCCFD-U-H", "Film coefficient relative U95 on the dummy", calc="CALC-H1-ESC-CFD", output="u_h",
          unit="-", limit=("<=", 0.05), how="T-H1-RIG-CHECK: thermocouple zero offsets at ambient; DMM checks.")
kit.claim("CL-H1-ESCCFD-F-ACCEPT", "T-E3-ESC-PAD-CFD acceptance: f_meas (guard-banded)", calc="CALC-H1-ESC-CFD",
          output="f_accept", unit="-",
          how="Card GT-04 step 2b: f_meas = (h_meas / h_lam)^2 >= this value passes CL-E3-CFD-FEQ (design hover).")


# ---------------------------------------------------------------- 11. R3: D5 side load and C3 pod brackets
@kit.calc("CALC-H1-SIDE-POD", equation="m = F / g ; SF_rim(F) = SF_rim(35 N) x 35 / F (linear)",
          inputs={"f_side": "CL-C1-FOOT-SIDE-DESIGN-ULT", "sf_rim": "CL-D5-SIDE-RIM-SF",
                  "f_pod": "CL-C3-FEA-SADDLE-TIES", "g": P + "env.g_ms2"},
          units={"g": "m/s2"})
def side_pod(f_side, sf_rim, f_pod, g):
    return {"side_n": f_side, "side_kg": f_side / g, "rim_sf_at_side": sf_rim * 35.0 / f_side,
            "pod_n": f_pod, "pod_kg": f_pod / g}


kit.claim("CL-H1-D5-SIDE-F", "T-D5-SIDE load at the pad (ultimate basis, CL-C1-FOOT-SIDE-DESIGN-ULT)",
          calc="CALC-H1-SIDE-POD", output="side_n", unit="N", parts=["GER-001-UR", "GER-002-UR"],
          how="Card GT-09: jugs over a pulley, along y then z, insert pushed 4 mm in; 3 s hold.")
kit.claim("CL-H1-D5-SIDE-RIM-SF", "D5 rim SF scaled from its 35 N basis to the 59 N test load", calc="CALC-H1-SIDE-POD",
          output="rim_sf_at_side", unit="-",
          how="Informational: D5's CL-D5-SIDE-RIM-SF is still on 35 N; at 59 N the drawn rim is expected to crack "
              "unless D5's CR-A1-65 shoe is the one tested (CR-H1-22).")
kit.claim("CL-H1-POD-BRACKET-F", "T-C3-POD-PROOF bracket load along +x and -z (CR-C3-20)", calc="CALC-H1-SIDE-POD",
          output="pod_n", unit="N", parts=["POD-007"],
          how="Card GT-09: strap round each handle-foot bracket, jugs over a pulley; 25 % steps, 10 s hold.")


# ---------------------------------------------------------------- tests of the rig itself (the campaign tests are owned by E1, B4, C1, E2, A1, A3, B3)
kit.test("T-H1-STAND-CAL", "Thrust stand calibration and noise",
         ["CL-H1-THRUST-CELL-REQ", "CL-H1-TORQUE-CELL-REQ", "CL-H1-THRUST-RES", "CL-H1-TORQUE-RES"],
         procedure="Card GT-01: dead weights 0.5/1.0/2.0/2.5 kg on the thrust axis via a pulley-free hook, "
                   "50/100/200/500 g at the 0.100 m torque arm; 60 s zero-load noise; before and after every session.",
         evidence="redesign/team/H1/logs/T-H1-STAND-CAL.csv")
kit.test("T-H1-SCALE-CAL", "Scale and CG-jig calibration",
         ["CL-H1-WEIGH-U95", "CL-H1-WEIGH-U-FRAC", "CL-H1-CG-U95", "CL-H1-CG-U-FRAC"],
         procedure="Card GT-06/07: 2.000 kg check mass 10 times per scale; 1.000 kg at a ruled x on the jig, "
                   "recover x; record in logs/T-H1-SCALE-CAL.csv.",
         evidence="redesign/team/H1/logs/T-H1-SCALE-CAL.csv")
kit.test("T-H1-RESTRAINT-PULL", "Restraint pull before props-on runs", ["CL-H1-RESTRAINT-F", "CL-H1-RESTRAINT-PER-TIE"],
         procedure="Card GT-13: spring scale (or the lever frame) on each strap to the per-strap force, no slip at "
                   "the table anchor.",
         evidence="redesign/team/H1/logs/T-H1-RESTRAINT-PULL.csv")
kit.test("T-H1-RESTRAINED-RUN", "Restrained four-motor run (CR-A2-25)",
         ["CL-E1-ILIM-I", "CL-F4-SPIN-MAX", "CL-F4-BAT-CURR-MAX", "CL-H1-RESTRAINT-F"],
         procedure="Card GT-13: aircraft strapped at the four root eyes after T-H1-RESTRAINT-PULL; fresh pack; "
                   "QSTABILIZE, 2 s full throttle: BAT.Curr <= 100 A, each ESC rpm <= the cap (Q_M_SPIN_MAX 0.84), "
                   "per-motor current <= 25 A from ESC telemetry; then 30 s at hover throttle for compassmot (T-F3-COMPASSMOT).",
         evidence="redesign/team/H1/logs/T-H1-RESTRAINED-RUN.csv")
kit.test("T-H1-PACK-PULL", "Pack retention pull with a dummy pack (GT-10)", ["CL-H1-PACK-PULL-F"],
         procedure="Card GT-10: pack-size plywood/sand dummy at the heaviest GT-05 pack mass, strapped as flown; pull "
                   "CL-H1-PACK-PULL-F in +-x, +-y, +z with jugs over a pulley or a luggage scale, 10 s each; slip "
                   "<= 5 mm, hatch stays closed. Never a LiPo.",
         evidence="redesign/team/H1/logs/T-H1-PACK-PULL.csv")
kit.test("T-H1-ARM-KILL", "Arm refusal and kill switch, props off (GT-12)", ["CL-H1-ESTOP-ACCEPT"],
         procedure="Card GT-12: arm refused with each failed pre-arm check; kill switch at 50 % throttle, 5 trials, "
                   "switch edge to all RCOU at disarm in the log <= CL-H1-ESTOP-ACCEPT.",
         evidence="redesign/team/H1/logs/T-H1-ARM-KILL.csv")
kit.test("T-H1-LEVER-CAL", "Coupon lever calibration, both holes",
         ["CL-H1-LEVER-CAP", "CL-H1-LEVER-NEED", "CL-H1-LEVER-CAP9", "CL-H1-LEVER-NEED9", "CL-H1-LEVER-SIGMA",
          "CL-H1-LEVER-PLATE-BRG", "CL-H1-LEVER-M6-BRG"],
         procedure="Card GT-15 step 0: tare the lever with the short-side counterweight (jug hook empty, lever level); "
                   "3.000 kg check mass at the 15:1 clevis, balance with water at the jug hook, ratio = 3.000 / jug "
                   "mass, 3x, within 2 % of 15.0; same with 2.000 kg at the 9:1 clevis, within 2 % of 9.0. Then a "
                   "20 kg jug on the 15:1 hole against a steel bar coupon for 60 s: no crack at the plates, no bolt "
                   "set.", evidence="redesign/team/H1/logs/T-H1-LEVER-CAL.csv")
kit.test("T-H1-RIG-CHECK", "Readout checks: optical lever, tube deflection and twist, tap acquisition, inclinometer, "
         "strain-gauge bridges, ESC-dummy thermocouples",
         ["CL-H1-MSTIFF-U", "CL-H1-TUBE-E-U", "CL-H1-TORS-U", "CL-H1-RING-U", "CL-H1-TAP-FS-REQ", "CL-H1-D5-RATIO-U",
          "CL-H1-D5-CELL-REQ", "CL-H1-SG-RES-FRAC", "CL-H1-SG-PDENS", "CL-H1-SG-SHUNT", "CL-H1-ESCCFD-U-H"],
         procedure="Optical lever: 1.00 mm shim under the mirror base edge, spot step matches 2 L t/b; both torsion "
                   "lasers on the same shim; caliper or dial on a 1.00 mm gauge block; FC raw IMU logs a 200 Hz "
                   "phone-speaker tone at the right bin; phone inclinometer against a 30 deg printed wedge; each gauge "
                   "bridge: 60 s zero (2 sigma), 10 min drift <= 5 ue unloaded, shunt step within 1 % of "
                   "CL-H1-SG-SHUNT; three thermocouples together in still air read within 0.3 K.",
         evidence="redesign/team/H1/logs/T-H1-RIG-CHECK.csv")


if __name__ == "__main__":
    kit.write()
