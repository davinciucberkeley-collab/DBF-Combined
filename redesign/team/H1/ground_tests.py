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
          how="Card GT-02 step 6: isolated full-throttle thrust at the per-motor limiter share (25 A) on a "
              "16.8 V pack must be >= this value.")
kit.claim("CL-H1-T-PASS-SAG", "Stand pass line, worst pack (T/W 1.6)", calc="CALC-H1-TW-PASS",
          output="pass_sag_kgf", unit="kgf", limit=("<=", "CL-H1-T-PRED-SAG"),
          how="Card GT-02 step 8: full-throttle thrust on a 3.6 V/cell (20 %) pack at 10 degC must be >= this value.")


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
@kit.calc("CALC-H1-PROOF", equation="P = V_ult/SF at y = Mx_ult/V_ult ; d_max = k b/2 ; F_mount = F_ult/SF ; "
          "F_fin = M_fin_ult / (SF z_station)",
          inputs={"v_ult": "CL-C1-WING-SHEAR-ULT", "mx_ult": "CL-C1-SPAR-MX-ULT", "sf": P + "requirements.safety_factor_ult",
                  "k_def": P + "requirements.spar_deflection_max", "b": P + "wing.span_m",
                  "f_mount_ult": "CL-C1-MOUNT-F-ULT", "m_fin_ult": "CL-C1-FINHALF-MB-ULT",
                  "z_st": P + "propulsion.stations.z_m", "f_pack": "CL-C1-PACK-CRASH-LOAD", "g": P + "env.g_ms2"},
          units={"b": "m", "z_st": "m", "g": "m/s2"})
def proof_loads(v_ult, mx_ult, sf, k_def, b, f_mount_ult, m_fin_ult, z_st, f_pack, g):
    p = v_ult / sf
    f_fin = m_fin_ult / sf / z_st
    return {"wing_p_n": p, "wing_p_kg": p / g, "wing_y_m": mx_ult / v_ult, "wing_defl_max_m": k_def * b / 2.0,
            "mount_f_n": f_mount_ult / sf, "mount_f_kg": f_mount_ult / sf / g,
            "fin_f_n": f_fin, "fin_f_kg": f_fin / g, "pack_pull_n": f_pack, "pack_pull_kg": f_pack / g}


kit.claim("CL-H1-WING-PROOF-P", "Wing proof load per side (limit)", calc="CALC-H1-PROOF", output="wing_p_n",
          unit="N", parts=["WNG-001"], how="Card GT-08: sandbag at y = CL-H1-WING-PROOF-Y each side; "
          "C1 confirms the load points (CR-H1-03).")
kit.claim("CL-H1-WING-PROOF-Y", "Wing proof load station", calc="CALC-H1-PROOF", output="wing_y_m", unit="m",
          limit=("<=", 0.575), how="Equivalent point that reproduces root flap moment and shear.")
kit.claim("CL-H1-WING-DEFL-MAX", "Tip deflection allowed at limit", calc="CALC-H1-PROOF", output="wing_defl_max_m",
          unit="m", how="Card GT-08: dial gauge or ruler at the tip; and no permanent set after unloading.")
kit.claim("CL-H1-MOUNT-PROOF-F", "Motor-mount proof load (limit)", calc="CALC-H1-PROOF", output="mount_f_n",
          unit="N", how="Card GT-09: hang from each mount in -x and in y.")
kit.claim("CL-H1-FIN-PROOF-F", "Fin + tube proof load at the station (limit)", calc="CALC-H1-PROOF",
          output="fin_f_n", unit="N", how="Card GT-09: hang at the motor station, side-load in y, wing held at the spar.")
kit.claim("CL-H1-PACK-PULL-F", "Pack retention pull (ultimate, dummy pack)", calc="CALC-H1-PROOF",
          output="pack_pull_n", unit="N", how="Card GT-10: spring scale on a 680 g pack dummy in x, y, z.")


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
         procedure="Card GT-03: spring scale on each strap to the per-strap force, no slip at the table anchor.",
         evidence="redesign/team/H1/logs/T-H1-RESTRAINT-PULL.csv")


if __name__ == "__main__":
    kit.write()
