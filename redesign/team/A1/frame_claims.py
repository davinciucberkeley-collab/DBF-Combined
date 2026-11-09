"""A1 chief engineer: frame-level claims for the K09-L quad tailsitter.

Run:  python -I redesign/team/A1/frame_claims.py
Writes claims.json beside this file (proof chain) and redesign/params/mass_budget.json (read by
interfaces/merge_check.py, fusion/check.py and the viewer) from the allocations in params/params.json,
so the budget has one source. Every number below is a pure function of params.json ids: change the
parameter, re-run this script, and build_graph.py confirms nothing drifted.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ---------------------------------------------------------------- assumptions this frame rests on
kit.assumption("ASM-A1-CLMAX", "CLmax 0.9 of the reflexed wing (SUPERSEDED)",
               "The MH 45-type reflexed section with elevons neutral reaches CLmax = 0.9 at Re ~3e5",
               basis="config-study card ESTIMATE. SUPERSEDED 2026-11-09 by B2's trimmed CLmax 0.80 (CL-B2-CLMAX-DESIGN, "
                     "S5010, SM 5 %), which CALC-A1-STALL now reads; the node stays only until B1, B3 and C1 re-point "
                     "their inputs (CHANGE-LOG D-02)", value=0.9, unit="-", status="UNVERIFIED",
               cites=["SRC-K09-CARD"])
kit.assumption("ASM-A1-WALL", "Box wall and lining 25 mm per side",
               "The transport box loses 25 mm per side to plywood/corrugated wall plus foam lining",
               basis="1/4 in ply + ~18 mm foam; D7 re-derives with the real box", value=0.025, unit="m",
               cites=["SRC-K09-REVIEW"])


# ---------------------------------------------------------------- geometry
@kit.calc("CALC-A1-WING", title="Wing area and aspect ratio", equation="S = b c ; AR = b^2 / S",
          inputs={"b": P + "wing.span_m", "c": P + "wing.chord_m"}, units={"b": "m", "c": "m"})
def wing_geometry(b, c):
    S = b * c
    return {"S_m2": S, "AR": b * b / S}


@kit.calc("CALC-A1-ELEVON", title="Elevon area fraction",
          equation="A = 2 (span_in + span_out) f c ; frac = A / S",
          inputs={"f": P + "wing.elevon.chord_frac", "yin": P + "wing.elevon.inboard_y_m",
                  "yout": P + "wing.elevon.outboard_y_m", "c": P + "wing.chord_m", "S": "CL-A1-WING-AREA"},
          units={"yin": "m", "yout": "m", "c": "m", "S": "m2"})
def elevon_area(f, yin, yout, c, S):
    span = (yin[1] - yin[0]) + (yout[1] - yout[0])
    A = 2 * span * f * c
    return {"A_m2": A, "frac": A / S}


@kit.calc("CALC-A1-PROP-CLEAR", title="Prop clearances",
          equation="gap_vert = 2 z_m - D ; gap_lat = 2 y_m - D ; gap_tip = b/2 - y_m - D/2 ; "
                   "gap_tube = (x_mount - r_tube) - x_prop ; gap_wing = z_m - D/2 - t_c c / 2 ; min of the five",
          inputs={"D": P + "propulsion.prop_diameter_m", "y": P + "propulsion.stations.y_m",
                  "z": P + "propulsion.stations.z_m", "b": P + "wing.span_m",
                  "x_mount": P + "propulsion.stations.x_mount_m", "x_prop": P + "propulsion.stations.x_prop_plane_m",
                  "tube_od": P + "fins.tube.od_m", "t_c": P + "wing.t_c", "c": P + "wing.chord_m"},
          units={"D": "m", "y": "m", "z": "m", "b": "m", "x_mount": "m", "x_prop": "m", "tube_od": "m", "c": "m"})
def prop_clearances(D, y, z, b, x_mount, x_prop, tube_od, t_c, c):
    gaps = {"gap_vertical_pair_m": 2 * z - D, "gap_lateral_pair_m": 2 * y - D,
            "gap_to_wingtip_m": b / 2 - y - D / 2, "gap_to_tube_face_m": (x_mount - tube_od / 2) - x_prop,
            "gap_disc_to_wing_plane_m": z - D / 2 - t_c * c / 2}     # disc edge above the wing's max thickness
    gaps["gap_min_m"] = min(gaps.values())
    return gaps


@kit.calc("CALC-A1-TIPOVER", title="Stance tip-over angles",
          equation="h = c - x_cg + foot ; narrow = atan(z_fin / h) ; wide = atan(y_fin / h)",
          inputs={"c": P + "wing.chord_m", "x_cg": P + "cg.x_target_m", "foot": P + "cg.foot_height_m",
                  "z_fin": P + "fins.half_height_m", "y_fin": P + "fins.y_m"},
          units={"c": "m", "x_cg": "m", "foot": "m", "z_fin": "m", "y_fin": "m"})
def tipover(c, x_cg, foot, z_fin, y_fin):
    h = c - x_cg + foot
    return {"cg_height_m": h, "narrow_deg": math.degrees(math.atan(z_fin / h)),
            "wide_deg": math.degrees(math.atan(y_fin / h)), "footprint_m": [2 * y_fin, 2 * z_fin]}


@kit.calc("CALC-A1-BOX", title="Box fit", assumes=["ASM-A1-WALL"],
          equation="internal = external - 2 wall ; slack = internal - envelope (sorted largest first)",
          inputs={"ext": P + "requirements.box_external_m", "wall": "ASM-A1-WALL",
                  "env": P + "transport.envelope_props_off_m"}, units={"ext": "m", "wall": "m", "env": "m"})
def box_fit(ext, wall, env):
    inner = sorted((e - 2 * wall for e in ext), reverse=True)
    envs = sorted(env, reverse=True)
    slack = [i - e for i, e in zip(inner, envs)]
    return {"internal_m": inner, "slack_m": slack, "slack_min_m": min(slack)}


# ---------------------------------------------------------------- mass and the gate cases
ALLOC = ["wing", "fins", "pod", "landing", "propulsion", "power", "avionics", "harness", "mechanisms"]


@kit.calc("CALC-A1-MASS-SIZED", title="Sized mass and A1 reserve from the allocations",
          equation="alloc = sum(allocations) ; sized = alloc + growth_allowance + build_overrun ; "
                   "reserve_cover = growth_reserve - (growth_allowance + build_overrun) ; "
                   "gate_check = gate - alloc - growth_reserve",
          inputs={**{k: f"{P}mass.allocation_g.{k}" for k in ALLOC}, "reserve": P + "mass.growth_reserve_g",
                  "growth_kg": P + "requirements.growth_allowance_kg", "overrun_kg": P + "requirements.build_overrun_kg",
                  "gate_kg": P + "requirements.mtow_gate_kg"},
          units={**{k: "g" for k in ALLOC + ["reserve"]}, "growth_kg": "kg", "overrun_kg": "kg", "gate_kg": "kg"})
def sized_mass(reserve, growth_kg, overrun_kg, gate_kg, **alloc):
    s = sum(alloc.values())
    planned = 1000.0 * (growth_kg + overrun_kg)
    return {"allocated_g": s, "sized_kg": (s + planned) / 1000.0, "reserve_cover_g": reserve - planned,
            "gate_check_g": 1000.0 * gate_kg - s - reserve}


@kit.calc("CALC-A1-HOVER-TW", title="Hover T/W at the gate and sized mass",
          equation="T/W = n T_max / m ; sag case x voltage_sag ; DL = m g / (n pi D^2/4)",
          inputs={"n": P + "propulsion.n_motors", "t_max": P + "propulsion.thrust_max_per_motor_kg",
                  "m_gate": P + "requirements.mtow_gate_kg", "m_sized": "CL-A1-MASS-SIZED",
                  "sag": P + "propulsion.voltage_sag", "D": P + "propulsion.prop_diameter_m",
                  "g": P + "env.g_ms2"},
          units={"t_max": "kg", "m_gate": "kg", "m_sized": "kg", "D": "m", "g": "m/s2"})
def hover_tw(n, t_max, m_gate, m_sized, sag, D, g):
    disk = n * math.pi * D * D / 4
    return {"tw_gate": n * t_max / m_gate, "tw_gate_sag": sag * n * t_max / m_gate,
            "tw_sized": n * t_max / m_sized, "disk_loading_gate_Nm2": m_gate * g / disk}


@kit.calc("CALC-A1-STALL", title="Stall and transition speed at the gate",
          equation="Vs = sqrt(2 m g / (rho S CLmax_trimmed)) ; Vt = k Vs",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "clmax": "CL-B2-CLMAX-DESIGN", "k": P + "requirements.transition_factor"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "S": "m2"})
def stall(m, g, rho, S, clmax, k):
    vs = math.sqrt(2 * m * g / (rho * S * clmax))
    return {"vs_ms": vs, "vt_ms": k * vs, "wing_loading_Nm2": m * g / S}


@kit.calc("CALC-A1-RESERVE", title="Budget reserve, pessimistic", equation="reserve = budget - spend_pess",
          inputs={"budget": P + "requirements.budget_usd", "spend": P + "cost.spend_pessimistic_usd"},
          units={"budget": "USD", "spend": "USD"}, output="reserve_usd")
def reserve(budget, spend):
    return budget - spend


# ---------------------------------------------------------------- claims (what the numbers mean)
kit.claim("CL-A1-WING-AREA", "Wing reference area", calc="CALC-A1-WING", output="S_m2", unit="m2",
          verifies=["R-CONFIG"], how="Measure the hot-wired core: span x chord.")
kit.claim("CL-A1-WING-AR", "Aspect ratio", calc="CALC-A1-WING", output="AR", unit="-",
          how="Follows from the measured span and chord.")
kit.claim("CL-A1-ELEVON-FRAC", "Elevon area fraction", calc="CALC-A1-ELEVON", output="frac", unit="-",
          limit=(">=", 0.15), verifies=["R-ELEVON-AREA"],
          how="Measure the cut elevon panels; B3 confirms authority with AVL and the foam-board twin (upper bound 0.25 is checked by B3).")
kit.claim("CL-A1-PROP-CLEAR", "Minimum prop clearance", calc="CALC-A1-PROP-CLEAR", output="gap_min_m", unit="m",
          limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"],
          how="Fusion interference check (A5) then a ruler on the built aircraft: prop tip to tube face, to the other prop, to the wing tip.")
kit.claim("CL-A1-TIPOVER", "Tip-over angle, narrow axis", calc="CALC-A1-TIPOVER", output="narrow_deg", unit="deg",
          limit=(">=", P + "requirements.tipover_min_deg"), verifies=["R-TIPOVER"],
          how="Stand the aircraft on a tilting board (C5 test): record the angle at which it tips about the fin axis.")
kit.claim("CL-A1-BOX-FIT", "Aircraft fits the box", calc="CALC-A1-BOX", output="slack_min_m", unit="m",
          limit=(">=", 0.0), verifies=["R-TRANSPORT"],
          how="Place the props-off aircraft in the built box on its cradles; lid closes without touching fins or tubes (D7).")
kit.claim("CL-A1-MASS-SIZED", "Sized take-off mass (allocations + planned growth + overrun)", calc="CALC-A1-MASS-SIZED",
          output="sized_kg", unit="kg", limit=("<=", P + "requirements.mtow_gate_kg"), verifies=["R-MASS-GATE"],
          how="A3 roll-up of every parts.csv against MASS-CG.md (CL-A3-MASS-PREDICTED is the maturity-based prediction); weigh the built aircraft with pack (H1).")
kit.claim("CL-A1-RESERVE-COVERS", "A1 mass reserve covers the planned growth and overrun", calc="CALC-A1-MASS-SIZED",
          output="reserve_cover_g", unit="g", limit=(">=", 0.0), verifies=["R-MASS-GATE"],
          how="growth_reserve_g in params.json minus (250 g growth allowance + 100 g build overrun); A3's maturity growth (CL-A3-GATE-MARGIN) is the stricter check.")
kit.claim("CL-A1-ALLOC-GATE", "Allocations plus reserve equal the gate", calc="CALC-A1-MASS-SIZED",
          output="gate_check_g", unit="g", limit=(">=", 0.0), verifies=["R-MASS-GATE"],
          how="2 600 - sum(allocation_g) - growth_reserve_g must be >= 0; A1 re-runs this script after any allocation change.")
kit.claim("CL-A1-HOVER-TW-GATE", "Hover T/W at the 2.6 kg gate", calc="CALC-A1-HOVER-TW", output="tw_gate", unit="-",
          limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"],
          how="Thrust stand, one station, 11x5.5MR on a fresh pack with the 100 A limiter (24.8 A per motor): thrust >= 1.3 kgf gives T/W 2.0 at 2.6 kg (H1, T-E1-STAND).")
kit.claim("CL-A1-HOVER-TW-SAG", "Hover T/W at the gate, worst pack state", calc="CALC-A1-HOVER-TW", output="tw_gate_sag", unit="-",
          limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"],
          how="Thrust-stand run on a pack at 20 % charge after a cold soak at 10 degC (E2 T-E2-IR), or the fresh value x CL-E2-SAG-F-WORST.")
kit.claim("CL-A1-STALL-GATE", "Stall speed at the gate", calc="CALC-A1-STALL", output="vs_ms", unit="m/s",
          limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="Trimmed CLmax from B2 (CL-B2-CLMAX-DESIGN); flight test: slow-flight stall in FBWA at altitude with airspeed logged (H2, T-B2-STALL).")
kit.claim("CL-A1-TRANSITION-GATE", "Transition speed at the gate", calc="CALC-A1-STALL", output="vt_ms", unit="m/s",
          limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="Cruise 16 m/s (B1) against 1.3 x the trimmed stall; log airspeed at 'Transition FW done' (F4/H2). Closed by D-01: chord 0.32 and cruise 16 m/s.")
kit.claim("CL-A1-RESERVE", "Pessimistic reserve at order", calc="CALC-A1-RESERVE", output="reserve_usd", unit="USD",
          limit=(">=", P + "requirements.crash_cost_usd"), verifies=["R-RESERVE", "R-BUDGET"],
          how="I1 re-prices the BOM at order time; reserve = 2 000 - spend, pessimistic column.")

kit.test("T-A1-WEIGH", "Weigh the assembled aircraft", verifies=["CL-A1-MASS-SIZED"], state="planned",
         procedure="Pack in, props on, 5 kg scale with 1 g resolution; record with the pack's own mass (H1).")
kit.test("T-A1-THRUST-STATION", "Thrust stand, one station", verifies=["CL-A1-HOVER-TW-GATE", "CL-A1-HOVER-TW-SAG"],
         state="planned", procedure="X3108S + 11x5.5MR on the 20 kg load cell (A/B with the 11x4.5MR), fresh pack then a 20 % pack at 10 degC, 0-100 % in 10 % steps, log gf, A, V and rpm (T-E1-STAND, T-B4-STAND).")


def write_mass_budget(kit, path):
    """redesign/params/mass_budget.json from the allocations (one source: params.json)."""
    alloc = {k: kit.value(f"{P}mass.allocation_g.{k}") for k in ALLOC}
    growth = kit.value(P + "mass.growth_reserve_g")
    gate_g = round(kit.value(P + "requirements.mtow_gate_kg") * 1000)
    planned_g = round(1000 * (kit.value(P + "requirements.growth_allowance_kg") + kit.value(P + "requirements.build_overrun_kg")))
    doc = {
        "_note": "Written by redesign/team/A1/frame_claims.py from params/params.json#mass.allocation_g; do not edit by hand. "
                 "limit_g is the hard as-built gate (P4). Allocations are flying mass per subsystem folder; growth_reserve_g "
                 "(= limit - allocations) is held by A1 for growth by maturity and the first-build overrun; sized_g = "
                 "allocations + the planned 250 g growth + 100 g overrun. A3 refines allocations in MASS-CG.md through a "
                 "change request to A1.",
        "limit_g": gate_g,
        "sized_g": sum(alloc.values()) + planned_g,
        "growth_reserve_g": growth,
        "allocations_g": alloc,
        "cg_x_m": list(kit.value(P + "cg.x_range_m")),
        "cg_z_m": list(kit.value(P + "cg.z_range_m")),
    }
    Path(path).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return doc


if __name__ == "__main__":
    kit.write()
    b = write_mass_budget(kit, HERE.parents[1] / "params" / "mass_budget.json")
    print(f"mass_budget.json: limit {b['limit_g']} g, allocated {sum(b['allocations_g'].values())} g, "
          f"sized {b['sized_g']} g, margin to gate {b['limit_g'] - b['sized_g']} g")
