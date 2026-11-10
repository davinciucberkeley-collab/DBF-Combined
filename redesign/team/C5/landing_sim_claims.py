"""C5 simulation round: proof-chain claims from the 3-D touchdown simulation and the shoe FEA.

Run (after the simulations):  python -I redesign/team/C5/landing_sim_claims.py      -> claims.sim.json
The simulations are too slow to re-run inside build_graph (minutes, not < 1 s), so each one writes a JSON record
(sim/out/sim3d.json, sim/out/fea_shoe.json). This script turns the records into assumptions (`ASM-C5-SIM3D-*`,
`ASM-C5-FEA-*`, status PROPOSED: simulation output, not test evidence) and re-runs cheap calculations on them:
margins against the live limits, the stress at the live side load (the FEA is linear), and a staleness check that
compares the inputs each simulation recorded with the current node values (CL-C5-SIM-INPUTS-STALE must be 0; if it
is not, re-run the simulations: sim/landing_sim3d.py, sim/run_fea.sh, then this script).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/landing/params.json"],
             out="claims.sim.json")
P = "P:"
SIM = json.loads((HERE / "sim" / "out" / "sim3d.json").read_text("utf-8"))
FEA = json.loads((HERE / "sim" / "out" / "fea_shoe.json").read_text("utf-8"))
FEET = (["GER-00%d-%s" % (n, s) for n in (1, 2, 4) for s in ("UR", "UL", "LR", "LL")]
        + ["GER-003-UR", "GER-003-UL", "GER-008-LR", "GER-008-LL"])
SHOES = ["GER-001-%s" % s for s in ("UR", "UL", "LR", "LL")]

# ---------------------------------------------------------------- simulation records -> assumptions
env = SIM["hard_envelope"]
gate = env["gate"]
lad = SIM["dt_ladder"]
dts = sorted(lad, key=float)
fine, base = lad[dts[0]], lad["4e-05"]
stroke_dt_err = abs(base["stroke_m"] - fine["stroke_m"])
USABLE = SIM["inputs"]["s_av"] - SIM["inputs"]["guard"]
# sustained side load over every envelope case that stays inside the usable stroke (bottomed cases are a stroke
# failure first; their side load is set by the rim-stop stiffness, see the sensitivity table)
side_all = max(r[4] for k in env for r in env[k]["rows"] if r[2] <= USABLE)
SINK = json.loads((HERE / "sim" / "out" / "sink_sweep.json").read_text("utf-8"))
side_all = max([side_all] + [x["side_N"] for k in SINK for x in SINK[k]["rows"] if x["stroke_m"] <= USABLE])


def _bottom_tilt(rows):
    import math
    bad = [math.hypot(r[0], r[1]) for r in rows if r[2] > USABLE]
    return min(bad) if bad else 99.0


def _axes(rows):
    return max(r[2] for r in rows if abs(r[0]) < 1e-9 or abs(r[1]) < 1e-9)
W = SIM["wind"]
v_b = min(W["broadside/lull/0.5"]["v_limit_ms"], W["broadside/lull/1.5"]["v_limit_ms"])
v_s = min(W["spanwise/lull/0.5"]["v_limit_ms"], W["spanwise/lull/1.5"]["v_limit_ms"])
strike = min((env[k]["strike_tilt_min_deg"] for k in env if env[k]["strike_tilt_min_deg"] is not None), default=99.0)
inp = SIM["inputs"]
SIM_INPUT_IDS = {"m_gate": P + "requirements.mtow_gate_kg", "m_a3": "CL-A3-MASS-BASIC", "m_pred": "CL-A3-MASS-PREDICTED",
                 "F_up": "CL-D5-F-PLATEAU-UPPER", "F_lo": "CL-D5-F-PLATEAU-LOWER", "s_av": "CL-D5-STROKE-AVAIL",
                 "lam": "ASM-C1-LAND-LIFT", "mu": "ASM-D5-PAD-MU", "z_cg": "CL-C5-CG-Z-R1", "v_td": "ASM-C5-TD-DRIFT",
                 "L_cart": "CL-D5-CART-LEN"}
REC = "sim/out/sim3d.json (sim/landing_sim3d.py, %.0f s run)" % SIM["runtime_s"]

kit.assumption("ASM-C5-SIM3D-STROKE", "3-D sim: worst stroke, 10 deg envelope",
               "Largest foot stroke in the 1.5 m/s design landing (lift 2/3 W) over every touchdown tilt <= 10 deg in "
               "any direction, at the 2.6 kg gate mass (A3-R6a inertia scaled)", basis=REC + "; dt 40 us, dt ladder "
               "to 5 us changes it by %.2f mm" % (stroke_dt_err * 1000), value=gate["stroke_max_m"], unit="m")
kit.assumption("ASM-C5-SIM3D-STROKE-AXES", "3-D sim: worst stroke, pitch-only or roll-only",
               "As ASM-C5-SIM3D-STROKE, touchdown tilt about one stance axis only (the planar model's cases)",
               basis=REC, value=_axes(gate["rows"]), unit="m")
kit.assumption("ASM-C5-SIM3D-STROKE-A3", "3-D sim: worst stroke at the A3 basic mass",
               "As ASM-C5-SIM3D-STROKE at the as-designed A3-R6a basic mass 2.322 kg", basis=REC,
               value=env["A3 basic"]["stroke_max_m"], unit="m")
kit.assumption("ASM-C5-SIM3D-BOTTOM-TILT", "3-D sim: tilt that uses up the stroke",
               "Smallest touchdown tilt magnitude (2.5 deg steps, any direction, 1.5 m/s, gate mass) at which a foot "
               "passes the usable stroke", basis=REC, value=_bottom_tilt(gate["rows"]), unit="deg")
kit.assumption("ASM-C5-SIM3D-V-SINK-10", "3-D sim: sink speed limit at 10 deg",
               "Largest sink speed (0.1 m/s steps) at which a 10 deg touchdown in any of 24 directions stays inside "
               "the usable stroke, gate mass", basis="sim/out/sink_sweep.json (sim/sink_sweep.py)",
               value=SINK["gate"]["v_max_ms"], unit="m/s")
kit.assumption("ASM-C5-SIM3D-N", "3-D sim: peak load factor, level, A3 basic mass",
               "Peak crusher force on the airframe / weight, level 1.5 m/s landing at the as-designed A3-R6a basic "
               "mass (the lightest flying mass: the plateau was sized at the 2.6 kg gate)",
               basis=REC, value=[r for r in env["A3 basic"]["rows"] if r[0] == 0 and r[1] == 0][0][3], unit="-")
kit.assumption("ASM-C5-SIM3D-SIDE", "3-D sim: sustained foot side load",
               "Largest transverse (side) load on one foot, 1 ms filtered, over every design-envelope and sink-sweep case "
               "that stays inside the usable stroke, mu 0.7", basis=REC + "; the unfiltered peak includes the 0.2 ms piston-mass "
               "impact on the pad (%.1f N)" % max(env[k]["side_peak_max_N"] for k in env), value=side_all, unit="N")
kit.assumption("ASM-C5-SIM3D-STRIKE-TILT", "3-D sim: wingtip strike onset tilt",
               "Smallest touchdown tilt (1.5 m/s, any direction) at which the wingtip TE corner reaches the ground",
               basis=REC + " (wingtip contact itself not modelled: the corner cap GER-007 takes it)",
               value=strike, unit="deg")
kit.assumption("ASM-C5-SIM3D-V-BROADSIDE", "3-D sim: broadside landing wind limit",
               "Largest wind (0.5 m/s steps) for which a touchdown tilted by the hover lean + 10 deg toward the narrow "
               "pod-side pad line, drifting 0.3 m/s toward it, does not tip; wind gone at touchdown (lull), sink "
               "0.5 and 1.5 m/s, A3 basic mass", basis=REC, value=v_b, unit="m/s")
kit.assumption("ASM-C5-SIM3D-V-SPANWISE", "3-D sim: span-into-wind landing wind limit",
               "As ASM-C5-SIM3D-V-BROADSIDE, lean and error toward a wide (fin) pad line",
               basis=REC + " (12 m/s is the top of the sweep)", value=v_s, unit="m/s")
kit.assumption("ASM-C5-SIM3D-DRIFT-TIPS", "3-D sim: drift cases that tip",
               "Number of the 128 drift cases (0.3 m/s, 8 directions x 8 tilts of 10 deg x 2 sinks) that tip over",
               basis=REC, value=float(SIM["drift"]["tipped"]), unit="-")
kit.assumption("ASM-C5-SIM3D-INPUTS", "3-D sim: input snapshot",
               "Input values the simulation ran with, in the order of the CALC-C5-SIM-STALE inputs",
               basis=REC, value=[inp[k] for k in SIM_INPUT_IDS], unit="-")

conv = FEA["convergence"]
fin = FEA["levels"]


def _k(case, zone):
    """Stress per newton of lip reaction: Richardson value if the three levels converge monotonically, else the
    finest level x (1 + its relative change)."""
    c = conv["%s|%s" % (case, zone)]
    R = FEA["inputs"]["R_lip_N"]
    if c["monotone"] and c["f_ext"] is not None and c["p"] and 0.5 < c["p"] < 4:
        return c["f_ext"] / R, c["gci_fine"]
    f = c["values"]
    return f[-1] * (1 + abs(f[-1] - f[-2]) / f[-1]) / R, abs(f[-1] - f[-2]) / f[-1]


# governing zone: the rim body (modelled fillets, no sharp corner). The +z "aft box" peak sits on the clamp edge
# at the fin TE (x 320, |y| 5.8-5.9, floor underside) and grows with refinement (singular): reported, not used.
K_GOV = max(((_k(c, z)[0], c, z) for c in ("+y", "+z") for z in ("rim",)))
lever = FEA["inputs"]["R_lip_N"] / FEA["inputs"]["F_side_ult_N"]
kit.assumption("ASM-C5-FEA-K-SHOE", "Shoe FEA: von Mises per newton of lip reaction",
               "Governing von Mises stress in the printed shoe GER-001 per newton of tine lip reaction at the sleeve "
               "end, away from sharp corners (rim body >= 1 mm from the rim step, aft box >= 1 mm from the window "
               "end): case %s, zone %s" % (K_GOV[1], K_GOV[2]),
               basis="sim/out/fea_shoe.json (sim/fea_shoe.py + SU2 8.5 ELASTICITY, trilinear hexahedra, 3 levels "
                     "h 0.4 / 0.32 / 0.267 mm, Richardson; verification strip vs beam theory)",
               value=K_GOV[0], unit="MPa/N")
kit.assumption("ASM-C5-FEA-LEVER", "Shoe FEA: lip reaction per newton of side load",
               "D5's tine lever R / F = (a + e) / (e + eps_y L_cart) for the as-designed stack",
               basis="CALC-D5-SIDE geometry, recomputed in sim/fea_shoe.py", value=lever, unit="-")


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-C5-SIM3D", title="3-D touchdown simulation results against the live limits",
          inputs={"s": "ASM-C5-SIM3D-STROKE", "n": "ASM-C5-SIM3D-N", "s_ax": "ASM-C5-SIM3D-STROKE-AXES",
                  "s_a3": "ASM-C5-SIM3D-STROKE-A3", "bt": "ASM-C5-SIM3D-BOTTOM-TILT", "v10": "ASM-C5-SIM3D-V-SINK-10", "side": "ASM-C5-SIM3D-SIDE",
                  "strike": "ASM-C5-SIM3D-STRIKE-TILT", "vb": "ASM-C5-SIM3D-V-BROADSIDE",
                  "vs": "ASM-C5-SIM3D-V-SPANWISE", "tips": "ASM-C5-SIM3D-DRIFT-TIPS",
                  "side_hand": "CL-C5-FOOT-SIDE-LOAD", "s_hand": "CL-C5-DYN-PAIR-CUR", "vb_hand": "CL-C5-V-LAND-BROADSIDE",
                  "k_ult": P + "requirements.safety_factor_ult"},
          units={"s": "m", "s_ax": "m", "s_a3": "m", "bt": "deg", "v10": "m/s", "side": "N", "strike": "deg", "vb": "m/s", "vs": "m/s", "side_hand": "N", "s_hand": "m",
                 "vb_hand": "m/s"},
          equation="results of sim/landing_sim3d.py (6-DOF rigid body, 4 elastic-plastic piston feet, 16 pad corners "
                   "with Coulomb friction) ; ratios to the planar / hand values ; ultimate side load = k_ult x side")
def sim3d(s, n, s_ax, s_a3, bt, v10, side, strike, vb, vs, tips, side_hand, s_hand, vb_hand, k_ult):
    return {"stroke_m": s, "stroke_axes_m": s_ax, "stroke_a3_m": s_a3, "bottom_tilt_deg": bt, "v_sink_10_ms": v10, "n": n, "side_N": side, "side_ult_N": k_ult * side, "side_vs_hand": side / side_hand,
            "stroke_vs_planar": s / s_hand, "strike_tilt_deg": strike, "v_broadside_ms": vb,
            "v_broadside_vs_hand": vb / vb_hand, "v_spanwise_ms": vs, "drift_tips": tips}


STALE_IN = {"snap": "ASM-C5-SIM3D-INPUTS"}
STALE_IN.update({k: v for k, v in SIM_INPUT_IDS.items()})


@kit.calc("CALC-C5-SIM-STALE", title="Simulation inputs still current", inputs=STALE_IN,
          equation="count of inputs whose current value differs from the snapshot the simulation ran with (rel 1e-6)")
def stale(snap, **now):
    keys = list(SIM_INPUT_IDS)
    bad = [k for k, v in zip(keys, snap) if abs(now[k] - v) > 1e-6 * max(1.0, abs(v))]
    return {"stale_count": float(len(bad)), "stale_inputs": bad}


@kit.calc("CALC-C5-FEA-SHOE", title="Shoe GER-001 stress under the landing side load (SU2 FEA, linear)",
          inputs={"k": "ASM-C5-FEA-K-SHOE", "lever": "ASM-C5-FEA-LEVER", "side_sim": "ASM-C5-SIM3D-SIDE",
                  "side_hand": "CL-C5-FOOT-SIDE-LOAD", "k_ult": P + "requirements.safety_factor_ult",
                  "allow": "ASM-D5-PETG-SIGMA", "sf_d5": "CL-D5-SIDE-RIM-SF"},
          units={"k": "MPa/N", "side_sim": "N", "side_hand": "N", "allow": "Pa"},
          equation="sigma = k x lever x k_ult x F_side (linear FEA) ; SF = allow / sigma ; F_side = hand (C5-R5, "
                   "D5's basis) or 3-D sim ; side load the shoe can take at SF 1 = allow / (k lever k_ult)")
def fea_shoe(k, lever, side_sim, side_hand, k_ult, allow, sf_d5):
    a = allow / 1e6
    s_hand = k * lever * k_ult * side_hand
    s_sim = k * lever * k_ult * side_sim
    return {"sigma_hand_MPa": s_hand, "sf_hand": a / s_hand, "sigma_sim_MPa": s_sim, "sf_sim": a / s_sim,
            "sf_d5_beam": sf_d5, "fea_over_beam": s_hand / (a / sf_d5),
            "side_capacity_N": a / (k * lever * k_ult)}


# ---------------------------------------------------------------- claims
kit.claim("CL-C5-SIM3D-STROKE", "3-D sim worst foot stroke, 10 deg any direction", calc="CALC-C5-SIM3D", output="stroke_m",
          unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="cross-checks CL-C5-DYN-PAIR-CUR (planar) with 6 DOF, friction, combined pitch + roll and pad edges",
          how="T-C5-AIRCRAFT-DROP corner drops (tilted board), flange-to-rim gap before and after.")
kit.claim("CL-C5-SIM3D-N", "3-D sim load factor at the as-designed mass", calc="CALC-C5-SIM3D", output="n", unit="-",
          limit=("<=", P + "requirements.landing_n_design"), verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="FAILS: n = 4 x 37.5 N / (2.32 kg g) = 6.6; the plateau was sized for n 5.88 at the 2.6 kg gate",
          how="T-C5-AIRCRAFT-DROP accelerometer at the CG, 100 Hz low-pass, at the weighed mass.")
kit.claim("CL-C5-SIM3D-STROKE-AXES", "3-D sim worst stroke, pitch-only or roll-only", calc="CALC-C5-SIM3D",
          output="stroke_axes_m", unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP pitch and roll drops.")
kit.claim("CL-C5-SIM3D-STROKE-A3", "3-D sim worst stroke at the A3 basic mass", calc="CALC-C5-SIM3D",
          output="stroke_a3_m", unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), parts=FEET,
          how="As CL-C5-SIM3D-STROKE at the weighed mass.")
kit.claim("CL-C5-SIM3D-BOTTOM-TILT", "Touchdown tilt that uses up the foot stroke", calc="CALC-C5-SIM3D",
          output="bottom_tilt_deg", unit="deg", limit=(">=", P + "requirements.landing_attitude_err_deg"),
          verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="a diagonal touchdown lands on one foot, which takes the energy alone and reaches the rim stop",
          how="T-C5-AIRCRAFT-DROP corner drop at 7.5 deg diagonal (expected to bottom; do it on the rig, 0.65 kg).")
kit.claim("CL-C5-SIM3D-V-SINK-10", "Sink speed limit for 10 deg in any direction", calc="CALC-C5-SIM3D",
          output="v_sink_10_ms", unit="m/s", limit=(">=", P + "requirements.landing_sink_ms"), parts=FEET,
          note="FAILS against 1.5 m/s; holds at 1.2 m/s (CR-C5-17)", how="As CL-C5-SIM3D-BOTTOM-TILT.")
kit.claim("CL-C5-SIM3D-SIDE-LOAD", "3-D sim sustained foot side load (limit)", calc="CALC-C5-SIM3D",
          output="side_N", unit="N", limit=("<=", "CL-C5-FOOT-SIDE-LOAD"), parts=FEET,
          note="FAILS against the hand value that D5 (CALC-D5-SIDE) and D3/C4 (root fillet) use: pads scrub at mu "
               "0.7 while the aircraft rotates over the first pad pair, so the side load approaches mu x plateau "
               "plus the tilt component. Replaces CL-C5-FOOT-SIDE-LOAD as the design side load (CR-C5-16)",
          how="T-D5-SIDE at the ultimate of this value; T-C5-AIRCRAFT-DROP with a side-load witness (crack check).")
kit.claim("CL-C5-SIM3D-SIDE-ULT", "3-D sim foot side load, ultimate", calc="CALC-C5-SIM3D", output="side_ult_N",
          unit="N", parts=FEET, how="T-D5-SIDE.")
kit.claim("CL-C5-SIM3D-STRIKE-TILT", "Touchdown tilt that grounds the wingtip TE corner", calc="CALC-C5-SIM3D",
          output="strike_tilt_deg", unit="deg", limit=(">=", P + "requirements.landing_attitude_err_deg"),
          parts=["GER-007-R", "GER-007-L"],
          note="FAILS by design intent: inside the 10 deg envelope a mostly-roll touchdown crushes the low fin's "
               "feet far enough for the wingtip TE corner to touch; the TPU corner cap (CR-C5-04) is the protection",
          how="T-C5-AIRCRAFT-DROP roll drop: witness tape on the corner caps.")
kit.claim("CL-C5-SIM3D-V-BROADSIDE", "3-D sim broadside landing wind limit", calc="CALC-C5-SIM3D",
          output="v_broadside_ms", unit="m/s", limit=(">=", P + "requirements.wind_limit_ms"), verifies=["R-WIND"],
          note="dynamic re-check of CL-C5-V-LAND-BROADSIDE (static, pivot stuck): crushing feet, friction, sink",
          how="Landing practice in measured wind (H2), anemometer; count tip-overs.")
kit.claim("CL-C5-SIM3D-V-SPANWISE", "3-D sim span-into-wind landing wind limit", calc="CALC-C5-SIM3D",
          output="v_spanwise_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"), verifies=["R-WIND"],
          how="As above, wingtip into the wind.")
kit.claim("CL-C5-SIM3D-DRIFT-TIPS", "Drift landings that tip (0.3 m/s, 10 deg)", calc="CALC-C5-SIM3D",
          output="drift_tips", unit="-", limit=("<=", 0.0), verifies=["R-TIPOVER"],
          how="T-C5-DRIFT-LOG landings: no tip-over in the first 20.")
kit.claim("CL-C5-SIM-INPUTS-STALE", "Simulation inputs changed since the run", calc="CALC-C5-SIM-STALE",
          output="stale_count", unit="-", limit=("<=", 0.0),
          how="Re-run sim/landing_sim3d.py and sim/run_fea.sh, then this script, whenever this is > 0.")
kit.claim("CL-C5-FEA-SHOE-SF-HAND", "Shoe FEA reserve factor at D5's side-load basis", calc="CALC-C5-FEA-SHOE",
          output="sf_hand", unit="-", limit=(">=", 1.0), parts=SHOES,
          note="same load as CL-D5-SIDE-RIM-SF (beam, 1.05); the FEA includes the snap windows, the free roof and "
               "the sleeve past the fin TE",
          how="T-D5-SIDE (35 N at the pad, both axes): no crack at the rim or the window ends.")
kit.claim("CL-C5-FEA-SHOE-SF", "Shoe FEA reserve factor at the 3-D sim side load", calc="CALC-C5-FEA-SHOE",
          output="sf_sim", unit="-", limit=(">=", 1.0), verifies=["R-LANDING-IMPACT"], parts=SHOES,
          how="T-D5-SIDE at 1.5 x CL-C5-SIM3D-SIDE-LOAD.")
kit.claim("CL-C5-FEA-OVER-BEAM", "Shoe stress, FEA / D5 beam model", calc="CALC-C5-FEA-SHOE", output="fea_over_beam",
          unit="-", parts=SHOES, how="Compare T-D5-SIDE strain-gauge or failure load with both.")
kit.claim("CL-C5-FEA-SIDE-CAPACITY", "Side load the as-designed shoe takes at RF 1", calc="CALC-C5-FEA-SHOE",
          output="side_capacity_N", unit="N", parts=SHOES, how="T-D5-SIDE load to failure on a spare shoe.")

kit.test("T-C5-SHOE-SIDE-FAIL", "Shoe side load to failure", verifies=["CL-C5-FEA-SIDE-CAPACITY", "CL-C5-FEA-SHOE-SF"],
         procedure="Spare shoe bonded on a stepped foam-board offcut (as T-D5-PROOF), insert pushed 4.5 mm in; load the "
                   "pad sideways along +y, then a second shoe along +z, in 5 N steps to failure; record the load and "
                   "where it cracks (rim, window end, roof). Pass: failure load >= 1.5 x CL-C5-SIM3D-SIDE-LOAD.")

if __name__ == "__main__":
    kit.write()
