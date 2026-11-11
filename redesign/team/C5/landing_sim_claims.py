"""C5 simulation rounds: proof-chain claims from the 3-D touchdown simulation and the shoe FEA.

Run (after the simulations):  python -I redesign/team/C5/landing_sim_claims.py      -> claims.sim.json
The simulations are too slow to re-run inside build_graph (minutes, not < 1 s), so each one writes a JSON record
(sim/out/sim3d.json, sim/out/sink_sweep.json, sim/out/side_check.json, sim/out/fea_shoe*.json). This script turns the
records into assumptions (`ASM-C5-SIM3D-*`, `ASM-C5-FEA-*`, status PROPOSED: simulation output, not test evidence) and
re-runs cheap calculations on them: margins against the live limits, the stress at the live side load (the FEA is
linear), and a staleness check that compares the inputs each simulation recorded with the current node values
(CL-C5-SIM-INPUTS-STALE must be 0; if it is not, re-run sim/landing_sim3d.py, sim/sink_sweep.py, sim/side_check.py,
then this script).

C5-R6 (2026-11-10, after D-62 / D-64 / D-65): the 6-DOF envelope runs at requirements.landing_sink_ms (1.2 m/s) with a
lightest-mass case (546 g pack) and a mu 0.5 pad envelope; the design side load stays the D-65 value (39.3 N limit /
59.0 N ultimate, ASM-C5-SIDE-DESIGN-D65) and the run checks that it still bounds the envelope; the shoe FEA is run on
the D-65 stack (sleeve end wall 2.0 mm, rim 3.0 mm, inside fillet R 1.0 mm, engagement 25 mm; sim/run_d65.sh). The
C5-S1 FEA of the as-drawn D5-R5 shoe is kept as a record (claims *-R5, no limits).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/landing/params.json"],
             out="claims.sim.json")
P = "P:"
OUT = HERE / "sim" / "out"
SIM = json.loads((OUT / "sim3d.json").read_text("utf-8"))
SINK = json.loads((OUT / "sink_sweep.json").read_text("utf-8"))
SIDE = json.loads((OUT / "side_check.json").read_text("utf-8"))
DRIFT = json.loads((OUT / "drift_sweep.json").read_text("utf-8"))
TESTH = json.loads((OUT / "test_height.json").read_text("utf-8"))
FEA = json.loads((OUT / "fea_shoe.json").read_text("utf-8"))                       # C5-S1: as-drawn D5-R5 shoe
D65_TAG = "_v_engage25_rim_t3_w2_rin1"
FEA65 = json.loads((OUT / ("fea_shoe%s.json" % D65_TAG)).read_text("utf-8"))         # C5-R6: D-65 decision stack
R6_TAG = "_v_engage25_fy20.9_fz11_lip2.8_rim_t2.8_ws1.2_rin1"
FEAR6 = json.loads((OUT / ("fea_shoe%s.json" % R6_TAG)).read_text("utf-8"))         # C5-R6: D5's R6 stack
FEET = (["GER-00%d-%s" % (n, s) for n in (1, 2, 4) for s in ("UR", "UL", "LR", "LL")]
        + ["GER-003-UR", "GER-003-UL", "GER-008-LR", "GER-008-LL"])
SHOES = ["GER-001-%s" % s for s in ("UR", "UL", "LR", "LL")]

# ---------------------------------------------------------------- simulation records -> assumptions
inp = SIM["inputs"]
V = inp["v_sink"]
env = SIM["hard_envelope"]
gate = env["gate"]
lad = SIM["dt_ladder"]
dts = sorted(lad, key=float)
fine, base = lad[dts[0]], lad["4e-05"]
stroke_dt_err = abs(base["stroke_m"] - fine["stroke_m"])
USABLE = inp["s_av"] - inp["guard"]
# sustained side load over every envelope case (any mass) that stays inside the usable stroke, plus the sink-sweep
# rows at or below the requirement sink (bottomed cases are a stroke failure first)
side_env = max(r[4] for k in env for r in env[k]["rows"] if r[2] <= USABLE)
side_req = max([side_env] + [x["side_N"] for k in SINK for x in SINK[k]["rows"]
                             if x["stroke_m"] <= USABLE and x["v"] <= V + 1e-9]
               + [x["side_N"] for k in DRIFT for x in DRIFT[k]["rows"] if x["stroke_m"] <= USABLE])
side_nodrift = max([side_env] + [x["side_N"] for k in SINK for x in SINK[k]["rows"]
                                 if x["stroke_m"] <= USABLE and x["v"] <= V + 1e-9])
side_sweep_all = max([side_env] + [x["side_N"] for k in SINK for x in SINK[k]["rows"] if x["stroke_m"] <= USABLE])
mu05 = SIM["hard_envelope_mu05_gate"]
side_mu05 = max(r[4] for r in mu05["rows"] if r[2] <= USABLE)


def _bottom_tilt(rows):
    bad = [math.hypot(r[0], r[1]) for r in rows if r[2] > USABLE]
    return min(bad) if bad else max(math.hypot(r[0], r[1]) for r in rows)


def _axes(rows):
    return max(r[2] for r in rows if abs(r[0]) < 1e-9 or abs(r[1]) < 1e-9)


def _level(rows):
    return [r for r in rows if r[0] == 0 and r[1] == 0][0]


W = SIM["wind"]
vk = "%.1f" % V
v_b = min(W["broadside/lull/0.5"]["v_limit_ms"], W["broadside/lull/%s" % vk]["v_limit_ms"])
v_s = min(W["spanwise/lull/0.5"]["v_limit_ms"], W["spanwise/lull/%s" % vk]["v_limit_ms"])
strike = min((env[k]["strike_tilt_min_deg"] for k in env if env[k]["strike_tilt_min_deg"] is not None), default=99.0)
SIM_INPUT_IDS = {"m_gate": P + "requirements.mtow_gate_kg", "m_a3": "CL-A3-MASS-BASIC", "m_pred": "CL-A3-MASS-PREDICTED",
                 "F_up": "CL-D5-F-PLATEAU-UPPER", "F_lo": "CL-D5-F-PLATEAU-LOWER", "s_av": "CL-D5-STROKE-AVAIL",
                 "lam": "ASM-C1-LAND-LIFT", "mu": "ASM-D5-PAD-MU", "z_cg": "CL-C5-CG-Z-R1", "v_td": "ASM-C5-TD-DRIFT",
                 "L_cart": "CL-D5-CART-LEN", "v_sink": P + "requirements.landing_sink_ms", "x_cg_h": "CL-C5-CG-H-R1"}
_snap = dict(inp, x_cg_h=inp["x_g"] - inp["x_cg"])
REC = "sim/out/sim3d.json (sim/landing_sim3d.py C5-R6, %.0f s run, sink %.1f m/s)" % (SIM["runtime_s"], V)

kit.assumption("ASM-C5-SIM3D-STROKE", "3-D sim: worst stroke, 10 deg envelope, gate mass",
               "Largest foot stroke in the design landing (sink requirements.landing_sink_ms, lift 2/3 W) over every "
               "touchdown tilt <= 10 deg in any direction (2.5 deg x 24 azimuths), at the 2.6 kg gate mass (A3-R6a "
               "inertia scaled), CG at the D-62 target", basis=REC + "; dt 40 us, dt ladder to 5 us changes it by "
               "%.3f mm" % (stroke_dt_err * 1000), value=gate["stroke_max_m"], unit="m")
kit.assumption("ASM-C5-SIM3D-STROKE-AXES", "3-D sim: worst stroke, pitch-only or roll-only",
               "As ASM-C5-SIM3D-STROKE, touchdown tilt about one stance axis only (the planar model's cases)",
               basis=REC, value=_axes(gate["rows"]), unit="m")
kit.assumption("ASM-C5-SIM3D-STROKE-A3", "3-D sim: worst stroke at the A3 basic mass",
               "As ASM-C5-SIM3D-STROKE at the as-designed A3-R6a basic mass 2.322 kg", basis=REC,
               value=env["A3 basic"]["stroke_max_m"], unit="m")
kit.assumption("ASM-C5-SIM3D-BOTTOM-TILT", "3-D sim: tilt that uses up the stroke",
               "Smallest touchdown tilt magnitude (2.5 deg steps, any direction, design sink, gate mass) at which a "
               "foot passes the usable stroke; when no case inside the 10 deg envelope bottoms, the largest tilt "
               "simulated (10 deg)", basis=REC, value=_bottom_tilt(gate["rows"]), unit="deg")
kit.assumption("ASM-C5-SIM3D-V-SINK-10", "3-D sim: sink speed limit at 10 deg",
               "Largest sink speed (0.1 m/s steps, 0.8-1.3) at which a 10 deg touchdown in any of 24 directions stays "
               "inside the usable stroke, gate mass", basis="sim/out/sink_sweep.json (sim/sink_sweep.py, C5-R6)",
               value=SINK["gate"]["v_max_ms"], unit="m/s")
kit.assumption("ASM-C5-SIM3D-N", "3-D sim: peak load factor, level, A3 basic mass",
               "Peak crusher force on the airframe / weight, level design landing at the as-designed A3-R6a basic "
               "mass with the 550 g pack", basis=REC, value=_level(env["A3 basic"]["rows"])[3], unit="-")
kit.assumption("ASM-C5-SIM3D-N-LIGHT", "3-D sim: peak load factor, level, lightest flying mass",
               "As ASM-C5-SIM3D-N at A3-R6a basic with the D-64 546 g pack (the lightest flying mass; the crush "
               "plateau is fixed, so n rises as the mass falls)", basis=REC + "; m = %.4f kg" % inp["m_light"],
               value=_level(env["lightest"]["rows"])[3], unit="-")
kit.assumption("ASM-C5-SIM3D-N-ENV", "3-D sim: peak load factor anywhere in the envelope, lightest mass",
               "Largest CG load factor over the whole 10 deg envelope at the lightest mass (tilted cases included)",
               basis=REC, value=env["lightest"]["n_peak_max"], unit="-")
kit.assumption("ASM-C5-SIM3D-SIDE", "3-D sim: sustained foot side load at the design sink",
               "Largest transverse (side) load on one foot, 1 ms filtered, over every design-envelope case (4 masses), "
               "every sink-sweep row at or below the design sink and every drift-sweep row (0.3 m/s drift, 10 deg) "
               "that stays inside the usable stroke, mu 0.7",
               basis=REC + " + sim/out/drift_sweep.json; without drift %.2f N; sink sweep to 1.3 m/s %.2f N; the "
               "unfiltered peak includes the 0.2 ms piston-mass impact on the pad (%.1f N)"
               % (side_nodrift, side_sweep_all, max(env[k]["side_peak_max_N"] for k in env)),
               value=side_req, unit="N")
kit.assumption("ASM-C5-SIDE-DESIGN-D65", "Design foot side load (limit), D-65 basis rounded up to cover drift",
               "Limit side load per foot that D5, C4/D3 and C1 design to (CHANGE-LOG D-65, CR-C5-16)",
               basis="C5-S1 6-DOF 39.30 N (1.5 m/s envelope + sink sweep, no drift) adopted by D-65; C5-R6 adds the "
                     "0.3 m/s drift landings, 39.44 N (+0.4 %, sim/out/drift_sweep.json), so C5 rounds the basis up "
                     "to 39.5 N (ultimate 59.25 N; was 39.3 / 59.0, CR-C5-16 update). Held fixed between runs so "
                     "the downstream roles do not drift; CL-C5-SIM3D-SIDE-12 checks every run against it",
               value=39.5, unit="N", status="PROPOSED")
kit.assumption("ASM-C5-SIM3D-SIDE-MU05", "3-D sim: sustained foot side load, pad mu 0.5",
               "As ASM-C5-SIM3D-SIDE over the gate-mass 10 deg envelope with a pad face of mu 0.5 on the landing mat",
               basis=REC + "; governing single case re-run in side_check.py: %.1f N" % SIDE["sens"]["mu 0.5"]["side_1ms_N"],
               value=side_mu05, unit="N")
kit.assumption("ASM-C5-SIM3D-STRIKE-TILT", "3-D sim: wingtip strike onset tilt",
               "Smallest touchdown tilt (design sink, any direction, any mass) at which the wingtip TE corner reaches "
               "the ground", basis=REC + " (wingtip contact itself not modelled: the corner cap GER-007 takes it)",
               value=strike, unit="deg")
kit.assumption("ASM-C5-SIM3D-V-BROADSIDE", "3-D sim: broadside landing wind limit",
               "Largest wind (0.5 m/s steps) for which a touchdown tilted by the hover lean + 10 deg toward the narrow "
               "pod-side pad line, drifting 0.3 m/s toward it, does not tip; wind gone at touchdown (lull), sink "
               "0.5 m/s and the design sink, A3 basic mass", basis=REC, value=v_b, unit="m/s")
kit.assumption("ASM-C5-SIM3D-V-SPANWISE", "3-D sim: span-into-wind landing wind limit",
               "As ASM-C5-SIM3D-V-BROADSIDE, lean and error toward a wide (fin) pad line",
               basis=REC + " (12 m/s is the top of the sweep)", value=v_s, unit="m/s")
kit.assumption("ASM-C5-SIM3D-DRIFT-TIPS", "3-D sim: drift cases that tip",
               "Number of the 128 drift cases (0.3 m/s, 8 directions x 8 tilts of 10 deg x 2 sinks) that tip over",
               basis=REC, value=float(SIM["drift"]["tipped"]), unit="-")
kit.assumption("ASM-C5-SIM3D-V-SINK-DRIFT", "3-D sim: sink speed limit at 10 deg with 0.3 m/s drift",
               "Largest sink speed (0.1 m/s steps) at which a 10 deg touchdown (8 attitudes) drifting 0.3 m/s in 8 "
               "directions stays inside the usable stroke, gate mass",
               basis="sim/out/drift_sweep.json (sim/drift_sweep.py, C5-R6): 1.2 m/s gives %.1f mm at the gate, %.1f mm "
                     "at A3 predicted" % (1000 * DRIFT["gate"]["rows"][-1]["stroke_m"],
                                          1000 * DRIFT["A3 predicted"]["rows"][-1]["stroke_m"]),
               value=DRIFT["gate"]["v_max_ms"], unit="m/s")
kit.assumption("ASM-C5-TEST-CORNER-H", "3-D sim: free-drop height for the 10 deg corner drop",
               "Largest pad-to-floor free-drop height (no rotor lift, 5 mm steps) at which a 10 deg touchdown in any "
               "of 24 directions stays inside the usable stroke, gate mass",
               basis="sim/out/test_height.json (sim/test_height.py, C5-R6): 50 mm gives %.1f mm, 55 mm %.1f mm"
                     % (1000 * TESTH["rows"][4]["stroke_m"], 1000 * TESTH["rows"][5]["stroke_m"]),
               value=TESTH["h_max_m"], unit="m")
kit.assumption("ASM-C5-PILOT-SPD-DN", "Pilot-commanded descent speed limit C5 asks of F4",
               "Q_PILOT_SPD_DN that keeps a drifting 10 deg touchdown inside the stroke with one 0.1 m/s step in hand",
               basis="CR-C5-23 (C5-R6); F4 holds Q_PILOT_SPD_DN <= 1.2 m/s today (D-65); replace with F4 value",
               value=1.0, unit="m/s", status="PROPOSED")
kit.assumption("ASM-C5-SIM3D-INPUTS", "3-D sim: input snapshot",
               "Input values the simulation ran with, in the order of the CALC-C5-SIM-STALE inputs",
               basis=REC, value=[_snap[k] for k in SIM_INPUT_IDS], unit="-")


def _k(fea, case, zone):
    """Stress per newton of lip reaction: Richardson value if the three levels converge monotonically, else the
    finest level x (1 + its relative change)."""
    c = fea["convergence"]["%s|%s" % (case, zone)]
    R = fea["inputs"]["R_lip_N"]
    if c["monotone"] and c["f_ext"] is not None and c["p"] and 0.5 < c["p"] < 4.5:
        return c["f_ext"] / R, c["gci_fine"]
    f = c["values"]
    return f[-1] * (1 + abs(f[-1] - f[-2]) / f[-1]) / R, abs(f[-1] - f[-2]) / f[-1]


# governing zone: the rim body (modelled fillets, no sharp corner). The +z "aft box" peak sits on the clamp edge
# at the fin TE (x 320, |y| 5.8-5.9, floor underside) and grows with refinement (singular): reported, not used.
K_GOV = max(((_k(FEA, c, z)[0], c, z) for c in ("+y", "+z") for z in ("rim",)))
lever = FEA["inputs"]["R_lip_N"] / FEA["inputs"]["F_side_ult_N"]
kit.assumption("ASM-C5-FEA-K-SHOE", "Shoe FEA (as-drawn D5-R5): von Mises per newton of lip reaction",
               "Governing von Mises stress in the as-drawn printed shoe GER-001 (wall 1.6, rim 2.4, inside corner "
               "R 0.4 mm, engagement 20 mm) per newton of tine lip reaction at the sleeve end: case %s, zone %s"
               % (K_GOV[1], K_GOV[2]),
               basis="sim/out/fea_shoe.json (C5-S1: sim/fea_shoe.py + SU2 8.5 ELASTICITY, trilinear hexahedra, 3 levels "
                     "h 0.4 / 0.32 / 0.267 mm, Richardson; verification strip vs beam theory)",
               value=K_GOV[0], unit="MPa/N")
kit.assumption("ASM-C5-FEA-LEVER", "Shoe FEA (as-drawn): lip reaction per newton of side load",
               "D5's tine lever R / F = (a + e) / (e + eps_y L_cart) for the as-drawn stack",
               basis="CALC-D5-SIDE geometry, recomputed in sim/fea_shoe.py", value=lever, unit="-")

ZONES = ("rim", "window strips")      # governing zones; the clamp edge at the fin TE (aft box, leg end) is singular


def _stack(fea, tag):
    gov = max(((_k(fea, c, z)[0], c, z, _k(fea, c, z)[1]) for c in ("+y", "+z") for z in ZONES))
    R = fea["inputs"]["R_lip_N"]
    edge = max(max(fea["convergence"]["%s|%s" % (c, z)]["values"][-1] for z in ("aft box", "whole shoe"))
               for c in ("+y", "+z")) / R
    return gov, R / fea["inputs"]["F_side_ult_N"], edge


STACKS = {"D65": (FEA65, D65_TAG, "D-65 decision stack (sleeve walls 2.0 mm, rim 3.0 mm, inside fillet R 1.0 mm, "
                                  "engagement 25 mm, long snap windows of R5)", "sim/run_d65.sh"),
          "D5R6": (FEAR6, R6_TAG, "D5-R6 stack (subsystems/landing/params.json 15:12: sleeve walls 1.2 mm, rim 2.8 mm "
                                  "= lip, inside fillet R 1.0 mm, engagement 25 mm, cartridge 20.9 x 11.0 mm, short "
                                  "snap windows; legs meshed at the sleeve wall)", "sim/run_d5r6.sh")}
for _sid, (_fea, _tag, _txt, _sh) in STACKS.items():
    _gov, _lev, _edge = _stack(_fea, _tag)
    kit.assumption("ASM-C5-FEA-K-SHOE-%s" % _sid, "Shoe FEA (%s): von Mises per newton of lip reaction" % _sid,
                   "Governing von Mises stress in the %s per newton of tine lip reaction, rim body and window strips "
                   "(case %s, zone %s). The clamp-edge peak at the fin TE (bonded floor / leg end, a boundary-condition "
                   "edge) is reported only: %.3f MPa/N at the finest level" % (_txt, _gov[1], _gov[2], _edge),
                   basis="sim/out/fea_shoe%s.json (C5-R6: %s, SU2 8.5 ELASTICITY, hexahedra, 3 levels h 0.4 / 0.32 / "
                         "0.267 mm, Richardson where monotone, else finest x (1 + last change); %.2f %%)"
                         % (_tag, _sh, 100 * (_gov[3] or 0.0)),
                   value=_gov[0], unit="MPa/N")
    kit.assumption("ASM-C5-FEA-LEVER-%s" % _sid, "Shoe FEA (%s): lip reaction per newton of side load" % _sid,
                   "D5's tine lever R / F = (a + e) / (e + eps_y L_cart) for the %s" % _txt,
                   basis="landing.stack() geometry with C5's overrides, recomputed in sim/fea_shoe.py", value=_lev,
                   unit="-")
    kit.assumption("ASM-C5-FEA-GCI-%s" % _sid, "Shoe FEA (%s): grid error of the governing zone" % _sid,
                   "Fine-grid GCI (Roache, Fs 1.25) or the last-level relative change of the governing stress",
                   basis="as ASM-C5-FEA-K-SHOE-%s" % _sid, value=_gov[3] if _gov[3] is not None else 1.0, unit="-")
    kit.assumption("ASM-C5-FEA-K-EDGE-%s" % _sid, "Shoe FEA (%s): clamp-edge peak per newton of lip reaction" % _sid,
                   "Largest von Mises at the bonded-floor / leg end at the fin TE (x 320 mm), finest level; a "
                   "boundary-condition edge in linear FEA, so it is reported, not used for the RF",
                   basis="sim/out/fea_shoe%s.json" % _tag, value=_edge, unit="MPa/N")


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-C5-SIM3D", title="3-D touchdown simulation results against the live limits",
          inputs={"s": "ASM-C5-SIM3D-STROKE", "n": "ASM-C5-SIM3D-N", "n_l": "ASM-C5-SIM3D-N-LIGHT",
                  "n_env": "ASM-C5-SIM3D-N-ENV", "s_ax": "ASM-C5-SIM3D-STROKE-AXES",
                  "s_a3": "ASM-C5-SIM3D-STROKE-A3", "bt": "ASM-C5-SIM3D-BOTTOM-TILT", "v10": "ASM-C5-SIM3D-V-SINK-10",
                  "side": "ASM-C5-SIM3D-SIDE", "side_d": "ASM-C5-SIDE-DESIGN-D65", "side_mu": "ASM-C5-SIM3D-SIDE-MU05",
                  "strike": "ASM-C5-SIM3D-STRIKE-TILT", "vb": "ASM-C5-SIM3D-V-BROADSIDE",
                  "vs": "ASM-C5-SIM3D-V-SPANWISE", "tips": "ASM-C5-SIM3D-DRIFT-TIPS",
                  "v_dr": "ASM-C5-SIM3D-V-SINK-DRIFT", "h_t": "ASM-C5-TEST-CORNER-H",
                  "side_hand": "CL-C5-FOOT-SIDE-LOAD", "s_hand": "CL-C5-DYN-PAIR-CUR", "vb_hand": "CL-C5-V-LAND-BROADSIDE",
                  "k_ult": P + "requirements.safety_factor_ult"},
          units={"s": "m", "s_ax": "m", "s_a3": "m", "bt": "deg", "v10": "m/s", "side": "N", "side_d": "N", "v_dr": "m/s",
                 "h_t": "m",
                 "side_mu": "N", "strike": "deg", "vb": "m/s", "vs": "m/s", "side_hand": "N", "s_hand": "m",
                 "vb_hand": "m/s"},
          equation="results of sim/landing_sim3d.py (6-DOF rigid body, 4 elastic-plastic piston feet, 16 pad corners "
                   "with Coulomb friction) ; ratios to the planar / hand values ; design side load = D-65 value ; "
                   "ultimate = k_ult x side")
def sim3d(s, n, n_l, n_env, s_ax, s_a3, bt, v10, side, side_d, side_mu, strike, vb, vs, tips, v_dr, h_t, side_hand,
          s_hand, vb_hand, k_ult):
    return {"stroke_m": s, "stroke_axes_m": s_ax, "stroke_a3_m": s_a3, "bottom_tilt_deg": bt, "v_sink_10_ms": v10,
            "n": n, "n_light": n_l, "n_env_light": n_env, "side_N": side_d, "side_ult_N": k_ult * side_d,
            "side_run_N": side, "side_mu05_N": side_mu, "side_mu05_ult_N": k_ult * side_mu,
            "side_vs_hand": side / side_hand, "stroke_vs_planar": s / s_hand, "strike_tilt_deg": strike,
            "v_broadside_ms": vb, "v_broadside_vs_hand": vb / vb_hand, "v_spanwise_ms": vs, "drift_tips": tips,
            "v_sink_drift_ms": v_dr, "test_corner_h_m": h_t}


STALE_IN = {"snap": "ASM-C5-SIM3D-INPUTS"}
STALE_IN.update({k: v for k, v in SIM_INPUT_IDS.items()})


@kit.calc("CALC-C5-SIM-STALE", title="Simulation inputs still current", inputs=STALE_IN,
          equation="count of inputs whose current value differs from the snapshot the simulation ran with (rel 1e-6)")
def stale(snap, **now):
    keys = list(SIM_INPUT_IDS)
    bad = [k for k, v in zip(keys, snap) if abs(now[k] - v) > 1e-6 * max(1.0, abs(v))]
    return {"stale_count": float(len(bad)), "stale_inputs": bad}


@kit.calc("CALC-C5-FEA-SHOE", title="As-drawn shoe GER-001 (D5-R5) stress under the landing side load, C5-S1 record",
          inputs={"k": "ASM-C5-FEA-K-SHOE", "lever": "ASM-C5-FEA-LEVER", "side_d": "ASM-C5-SIDE-DESIGN-D65",
                  "side_hand": "CL-C5-FOOT-SIDE-LOAD", "k_ult": P + "requirements.safety_factor_ult",
                  "allow": "ASM-D5-PETG-SIGMA", "sf_d5": "CL-D5-SIDE-RIM-SF"},
          units={"k": "MPa/N", "side_d": "N", "side_hand": "N", "allow": "Pa"},
          equation="sigma = k x lever x k_ult x F_side (linear FEA) ; SF = allow / sigma ; F_side = hand or the D-65 "
                   "design value ; side load the shoe can take at SF 1 = allow / (k lever k_ult) ; FEA / beam = "
                   "sigma(D5 basis) / (allow / SF_D5)")
def fea_shoe(k, lever, side_d, side_hand, k_ult, allow, sf_d5):
    a = allow / 1e6
    s_hand = k * lever * k_ult * side_hand
    s_d = k * lever * k_ult * side_d
    return {"sigma_hand_MPa": s_hand, "sf_hand": a / s_hand, "sigma_design_MPa": s_d, "sf_design": a / s_d,
            "sf_d5_beam": sf_d5, "side_capacity_N": a / (k * lever * k_ult)}


def _shoe(k, lever, side_d, side_run, side_mu, k_ult, allow, gci, k_edge):
    a = allow / 1e6
    s_d = k * lever * k_ult * side_d
    return {"sigma_design_MPa": s_d, "rf_design": a / s_d, "rf_design_gci": a / s_d / (1 + gci),
            "rf_run": a / (k * lever * k_ult * side_run), "rf_mu05": a / (k * lever * k_ult * side_mu),
            "side_capacity_N": a / (k * lever * k_ult), "side_ult_N": k_ult * side_d,
            "sigma_edge_MPa": k_edge * lever * k_ult * side_d, "rf_edge": a / (k_edge * lever * k_ult * side_d)}


def _shoe_in(sid):
    return {"k": "ASM-C5-FEA-K-SHOE-%s" % sid, "lever": "ASM-C5-FEA-LEVER-%s" % sid,
            "side_d": "ASM-C5-SIDE-DESIGN-D65", "side_run": "ASM-C5-SIM3D-SIDE", "side_mu": "ASM-C5-SIM3D-SIDE-MU05",
            "k_ult": P + "requirements.safety_factor_ult", "allow": "ASM-D5-PETG-SIGMA",
            "gci": "ASM-C5-FEA-GCI-%s" % sid, "k_edge": "ASM-C5-FEA-K-EDGE-%s" % sid}


_SHOE_UNITS = {"k": "MPa/N", "k_edge": "MPa/N", "side_d": "N", "side_run": "N", "side_mu": "N", "allow": "Pa"}
_SHOE_EQ = ("sigma = k x lever x k_ult x F (linear FEA) ; RF = allow / sigma ; F = design side load (39.5 N limit, "
            "59.25 N ult), this run's envelope value, or the mu 0.5 pad option ; RF with the grid error = RF / (1 + "
            "GCI) ; capacity at RF 1 (limit) = allow / (k lever k_ult) ; clamp-edge RF reported with k_edge")


@kit.calc("CALC-C5-FEA-SHOE-D5R6", title="D5-R6 shoe GER-001 under the design side load (C5 SU2 FEA, linear)",
          inputs=_shoe_in("D5R6"), units=_SHOE_UNITS, equation=_SHOE_EQ)
def fea_shoe_d5r6(k, lever, side_d, side_run, side_mu, k_ult, allow, gci, k_edge):
    return _shoe(k, lever, side_d, side_run, side_mu, k_ult, allow, gci, k_edge)


@kit.calc("CALC-C5-FEA-SHOE-D65", title="D-65 decision shoe GER-001 under the design side load (C5 SU2 FEA, linear)",
          inputs=_shoe_in("D65"), units=_SHOE_UNITS, equation=_SHOE_EQ)
def fea_shoe_d65(k, lever, side_d, side_run, side_mu, k_ult, allow, gci, k_edge):
    return _shoe(k, lever, side_d, side_run, side_mu, k_ult, allow, gci, k_edge)


# ---------------------------------------------------------------- claims
kit.claim("CL-C5-SIM3D-STROKE", "3-D sim worst foot stroke, design sink, 10 deg any direction, gate mass",
          calc="CALC-C5-SIM3D", output="stroke_m",
          unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="C5-R6: 1.2 m/s (D-65) with the D-62 CG; 0.1 mm inside the usable stroke at the 2.6 kg gate, 2.4 mm at "
               "A3's predicted 2.436 kg. Cross-checks CL-C5-DYN-PAIR-CUR (planar) with 6 DOF, friction, combined "
               "pitch + roll and pad edges",
          how="T-C5-AIRCRAFT-DROP corner drops (tilted board), flange-to-rim gap before and after.")
kit.claim("CL-C5-SIM3D-N", "3-D sim load factor, level, as-designed A3-R6a basic mass", calc="CALC-C5-SIM3D",
          output="n", unit="-", limit=("<=", P + "requirements.landing_n_design"), verifies=["R-LANDING-IMPACT"],
          parts=FEET,
          note="n = 4 x 37.5 N / (2.32 kg g) = 6.59, set by the crush plateau, not by the sink speed (D-65 raised "
               "landing_n_design to 6.6)",
          how="T-C5-AIRCRAFT-DROP accelerometer at the CG, 100 Hz low-pass, at the weighed mass.")
kit.claim("CL-C5-SIM3D-N-LIGHT", "3-D sim load factor, level, lightest flying mass (546 g pack)",
          calc="CALC-C5-SIM3D", output="n_light", unit="-", limit=("<=", P + "requirements.landing_n_design"),
          verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="the D-64 lightest pack takes 4 g off A3-R6a basic: n reaches the 6.6 limit to the second decimal. "
               "Holds only while the flying mass stays >= 2.317 kg; the R5 additions (about +21 g, ASM-A1-R5-ADDED-G) "
               "give about 0.06 back",
          how="T-C5-AIRCRAFT-DROP at the lightest weighed configuration.")
kit.claim("CL-C5-SIM3D-N-ENV", "3-D sim load factor, worst of the 10 deg envelope, lightest mass", calc="CALC-C5-SIM3D",
          output="n_env_light", unit="-", limit=("<=", P + "requirements.landing_n_design"), parts=FEET,
          how="As CL-C5-SIM3D-N-LIGHT, tilted drops.")
kit.claim("CL-C5-SIM3D-STROKE-AXES", "3-D sim worst stroke, pitch-only or roll-only", calc="CALC-C5-SIM3D",
          output="stroke_axes_m", unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), parts=FEET,
          how="T-C5-AIRCRAFT-DROP pitch and roll drops.")
kit.claim("CL-C5-SIM3D-STROKE-A3", "3-D sim worst stroke at the A3 basic mass", calc="CALC-C5-SIM3D",
          output="stroke_a3_m", unit="m", limit=("<=", "CL-D5-STROKE-USABLE"), parts=FEET,
          how="As CL-C5-SIM3D-STROKE at the weighed mass.")
kit.claim("CL-C5-SIM3D-BOTTOM-TILT", "Touchdown tilt that uses up the foot stroke (design sink, gate mass)",
          calc="CALC-C5-SIM3D", output="bottom_tilt_deg", unit="deg",
          limit=(">=", P + "requirements.landing_attitude_err_deg"), verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="C5-R6 at 1.2 m/s: no case inside the 10 deg envelope reaches the usable stroke (value = largest tilt "
               "simulated); at 1.5 m/s it was 5.0 deg (C5-S1)",
          how="T-C5-AIRCRAFT-DROP corner drop at 10 deg diagonal at the 1.2 m/s-equivalent height (run on the rig first).")
kit.claim("CL-C5-SIM3D-V-SINK-10", "Sink speed limit for 10 deg in any direction (gate mass)", calc="CALC-C5-SIM3D",
          output="v_sink_10_ms", unit="m/s", limit=(">=", P + "requirements.landing_sink_ms"), parts=FEET,
          note="0.1 m/s steps: the 1.2 m/s requirement is the last step that holds (0 % margin at the gate mass)",
          how="As CL-C5-SIM3D-BOTTOM-TILT.")
kit.claim("CL-C5-SIM3D-SIDE-LOAD", "Design foot side load (limit), D-65", calc="CALC-C5-SIM3D",
          output="side_N", unit="N", parts=FEET,
          note="D-65 design value (C5-S1 6-DOF, mu 0.7): replaces CL-C5-FOOT-SIDE-LOAD in D5, C4/D3 and C1 (CR-C5-16). "
               "Pads scrub at mu 0.7 while the aircraft rotates over the first foot. CL-C5-SIM3D-SIDE-12 checks that "
               "the 1.2 m/s envelope stays inside it",
          how="T-D5-SIDE at the ultimate of this value; T-C5-AIRCRAFT-DROP with a side-load witness (crack check).")
kit.claim("CL-C5-SIM3D-SIDE-ULT", "Design foot side load, ultimate (D-65)", calc="CALC-C5-SIM3D", output="side_ult_N",
          unit="N", parts=FEET, how="T-D5-SIDE.")
kit.claim("CL-C5-SIM3D-SIDE-12", "3-D sim sustained foot side load, 1.2 m/s envelope (4 masses, mu 0.7)",
          calc="CALC-C5-SIM3D", output="side_run_N", unit="N", limit=("<=", "CL-C5-SIM3D-SIDE-LOAD"),
          verifies=["R-LANDING-IMPACT"], parts=FEET,
          note="the scrub load saturates near mu x plateau + tilt component, so it barely depends on the sink speed",
          how="As CL-C5-SIM3D-SIDE-LOAD.")
kit.claim("CL-C5-SIM3D-SIDE-MU05", "3-D sim foot side load with a mu 0.5 pad face (option), limit",
          calc="CALC-C5-SIM3D", output="side_mu05_N", unit="N", limit=("<=", "CL-C5-SIM3D-SIDE-LOAD"), parts=FEET,
          note="option for D5 (CR-C5-16): a pad face with mu <= 0.5 on the landing mat (e.g. PTFE / UHMW tape over "
               "the neoprene) cuts the side load by a quarter; the parked-slide and drift checks then use mu 0.5",
          how="T-D5-PAD-MU on the chosen pad face and the landing mat (tilt board, 5 pulls); <= 0.5 to adopt it.")
kit.claim("CL-C5-SIM3D-SIDE-MU05-ULT", "Foot side load with a mu 0.5 pad face, ultimate", calc="CALC-C5-SIM3D",
          output="side_mu05_ult_N", unit="N", parts=FEET, how="T-D5-SIDE.")
kit.claim("CL-C5-SIM3D-STRIKE-TILT", "Touchdown tilt that grounds the wingtip TE corner", calc="CALC-C5-SIM3D",
          output="strike_tilt_deg", unit="deg", limit=(">=", P + "requirements.landing_attitude_err_deg"),
          parts=["GER-007-R", "GER-007-L"],
          note="FAILS by design intent: inside the 10 deg envelope a mostly-roll touchdown crushes the low fin's "
               "feet far enough for the wingtip TE corner to touch; the TPU corner cap (CR-C5-04) is the protection",
          how="T-C5-AIRCRAFT-DROP roll drop: witness tape on the corner caps.")
kit.claim("CL-C5-SIM3D-V-BROADSIDE", "3-D sim broadside landing wind limit", calc="CALC-C5-SIM3D",
          output="v_broadside_ms", unit="m/s", limit=(">=", P + "requirements.wind_limit_ms"), verifies=["R-WIND"],
          note="dynamic re-check of CL-C5-V-LAND-BROADSIDE (static, pivot stuck): crushing feet, friction, sink. "
               "FAILS: land with a wingtip into the wind (CR-C5-05, rule S1)",
          how="Landing practice in measured wind (H2), anemometer; count tip-overs.")
kit.claim("CL-C5-SIM3D-V-SPANWISE", "3-D sim span-into-wind landing wind limit", calc="CALC-C5-SIM3D",
          output="v_spanwise_ms", unit="m/s", limit=(">=", P + "requirements.gust_survive_ms"), verifies=["R-WIND"],
          how="As above, wingtip into the wind.")
kit.claim("CL-C5-SIM3D-DRIFT-TIPS", "Drift landings that tip (0.3 m/s, 10 deg)", calc="CALC-C5-SIM3D",
          output="drift_tips", unit="-", limit=("<=", 0.0), verifies=["R-TIPOVER"],
          how="T-C5-DRIFT-LOG landings: no tip-over in the first 20.")
kit.claim("CL-C5-SIM3D-V-SINK-DRIFT", "Sink speed limit for 10 deg with 0.3 m/s touchdown drift (gate mass)",
          calc="CALC-C5-SIM3D", output="v_sink_drift_ms", unit="m/s", limit=(">=", "ASM-C5-PILOT-SPD-DN"),
          parts=FEET,
          note="the D-65 requirement (1.2 m/s at 10 deg) has no drift; a pilot down-stick landing in QLOITER also "
               "drifts. 1.2 m/s + 10 deg + 0.3 m/s bottoms a foot (38.1 mm at the gate), 1.1 m/s holds. C5 asks F4 "
               "for Q_PILOT_SPD_DN 1.0 m/s (CR-C5-23)",
          how="T-C5-DRIFT-LOG: touchdown sink and ground speed in the twin hard-landing logs.")
kit.claim("CL-C5-TEST-CORNER-H", "Free-drop height for the 10 deg corner drops of T-C5-AIRCRAFT-DROP",
          calc="CALC-C5-SIM3D", output="test_corner_h_m", unit="m",
          note="without rotor lift a 10 deg corner drop from the 73 mm (1.2 m/s) height bottoms a foot; run the "
               "corner drops at 45 mm (31.0 mm modelled) and compare each foot stroke with the model re-run",
          how="Release height pad-to-floor.")
kit.claim("CL-C5-SIM-INPUTS-STALE", "Simulation inputs changed since the run", calc="CALC-C5-SIM-STALE",
          output="stale_count", unit="-", limit=("<=", 0.0),
          how="Re-run sim/landing_sim3d.py, sim/sink_sweep.py, sim/side_check.py, then this script, whenever this is > 0.")

kit.claim("CL-C5-FEA-SHOE-SF", "Shoe GER-001 reserve factor at the design side load (59.25 N ult), D5-R6 stack",
          calc="CALC-C5-FEA-SHOE-D5R6", output="rf_design", unit="-", limit=(">=", 1.0),
          verifies=["R-LANDING-IMPACT"], parts=SHOES,
          note="C5-R6: C5's independent SU2 FEA of D5's R6 stack (walls 1.2, rim 2.8, R 1.0, engagement 25 mm) on 3 "
               "meshes, rim body / window strips; D5 has not yet re-published CALC-D5-SIDE, so the R6 numbers enter "
               "as overrides (CR-C5-20). Was 0.22 on the as-drawn D5-R5 shoe (CL-C5-FEA-SHOE-SF-R5)",
          how="T-C5-SHOE-SIDE-FAIL on the R6 shoe: failure load >= 59.25 N at the pad, both axes.")
kit.claim("CL-C5-FEA-SHOE-SF-GCI", "D5-R6 shoe reserve factor with the grid error taken off",
          calc="CALC-C5-FEA-SHOE-D5R6", output="rf_design_gci", unit="-", limit=(">=", 1.0), parts=SHOES,
          how="As CL-C5-FEA-SHOE-SF.")
kit.claim("CL-C5-FEA-SHOE-SF-MU05", "D5-R6 shoe reserve factor with the mu 0.5 pad option",
          calc="CALC-C5-FEA-SHOE-D5R6", output="rf_mu05", unit="-", limit=(">=", 1.0), parts=SHOES,
          how="As CL-C5-FEA-SHOE-SF.")
kit.claim("CL-C5-FEA-SHOE-SF-EDGE", "D5-R6 shoe: reserve factor at the clamp edge (fin TE), reported",
          calc="CALC-C5-FEA-SHOE-D5R6", output="rf_edge", unit="-", parts=SHOES,
          note="boundary-condition edge of the bonded floor / legs at the fin TE: linear FEA cannot resolve it, so "
               "it does not set the RF; below 1 it points at where T-C5-SHOE-SIDE-FAIL may crack first (CR-C5-20: "
               "a fillet or taper at the leg / floor end)",
          how="T-C5-SHOE-SIDE-FAIL: note whether the crack starts at the fin TE.")
kit.claim("CL-C5-FEA-SIDE-CAPACITY-D5R6", "Limit side load the D5-R6 shoe takes at RF 1",
          calc="CALC-C5-FEA-SHOE-D5R6", output="side_capacity_N", unit="N", limit=(">=", "CL-C5-SIM3D-SIDE-LOAD"),
          parts=SHOES, how="T-C5-SHOE-SIDE-FAIL: failure load / 1.5.")
kit.claim("CL-C5-FEA-SHOE-SF-D65", "D-65 decision shoe reserve factor at 59.25 N ult (record)",
          calc="CALC-C5-FEA-SHOE-D65", output="rf_design", unit="-", limit=(">=", 1.0), parts=SHOES,
          note="the geometry D-65 wrote down (walls 2.0, rim 3.0, R 1.0, engagement 25 mm, R5 long windows); D5-R6 "
               "builds a lighter variant, checked in CL-C5-FEA-SHOE-SF",
          how="As CL-C5-FEA-SHOE-SF.")
kit.claim("CL-C5-FEA-SIDE-CAPACITY-D65", "Limit side load the D-65 decision shoe takes at RF 1 (record)",
          calc="CALC-C5-FEA-SHOE-D65", output="side_capacity_N", unit="N", parts=SHOES, how="As above.")
kit.claim("CL-C5-FEA-SHOE-SF-R5", "As-drawn D5-R5 shoe reserve factor at the D-65 design side load (record)",
          calc="CALC-C5-FEA-SHOE", output="sf_design", unit="-", parts=SHOES,
          note="C5-S1 record, superseded by the D-65 stack (CL-C5-FEA-SHOE-SF); no limit: the part is not built",
          how="None: superseded.")
kit.claim("CL-C5-FEA-SHOE-SF-HAND", "As-drawn D5-R5 shoe reserve factor at D5's hand side-load basis (record)",
          calc="CALC-C5-FEA-SHOE", output="sf_hand", unit="-", parts=SHOES,
          note="C5-S1 record (0.38 at D5's 34.4 N ult basis); the live CL-C5-FOOT-SIDE-LOAD moves with the sink "
               "speed, so this re-computes; superseded by D-65",
          how="None: superseded.")
kit.claim("CL-C5-FEA-SIDE-CAPACITY", "Limit side load the as-drawn D5-R5 shoe takes at RF 1 (record)",
          calc="CALC-C5-FEA-SHOE", output="side_capacity_N", unit="N", parts=SHOES, how="None: superseded.")

kit.test("T-C5-SHOE-SIDE-FAIL", "Shoe side load to failure", verifies=["CL-C5-FEA-SIDE-CAPACITY-D5R6", "CL-C5-FEA-SHOE-SF"],
         procedure="Two shoes as D5 builds them (R6: walls 1.2, rim 2.8, R 1.0 inside fillets, 25 mm engagement, "
                   "layers along the sleeve axis) bonded on stepped foam-board offcuts (as T-D5-PROOF), insert pushed 4.5 mm in; load "
                   "the pad sideways along +y on one, +z on the other, in 5 N steps to failure; record the load and "
                   "where it cracks (rim, window end, roof, fin TE). Pass: failure load >= 59.25 N (1.5 x CL-C5-SIM3D-SIDE-LOAD) "
                   "on both.")

if __name__ == "__main__":
    kit.write()
