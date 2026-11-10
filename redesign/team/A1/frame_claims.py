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


@kit.calc("CALC-A1-TIPOVER", title="Stance tip-over angles toward the pod side (narrow axis) and the wing tip",
          equation="h = c - x_cg + foot ; narrow = atan((z_pad - z_cg) / h) ; wide = atan(y_fin / h) ; "
                   "corner bound at x_cg = x_range[0], z_cg = z_range[1]; target at x_target, z_cg = z_target_a3",
          inputs={"c": P + "wing.chord_m", "x_range": P + "cg.x_range_m", "x_target": P + "cg.x_target_m",
                  "z_range": P + "cg.z_range_m", "foot": P + "cg.foot_height_m",
                  "z_pad": "CL-D5-CONTACT-Z", "y_fin": P + "fins.y_m"},
          units={"c": "m", "x_range": "m", "x_target": "m", "z_range": "m", "foot": "m", "z_pad": "m", "y_fin": "m"})
def tipover(c, x_range, x_target, z_range, foot, z_pad, y_fin):
    # CHANGE-LOG D-30 (C5 CR-C5-01, D5 CR-D5-01): pivot = pad contact z (splayed feet), CG height above the
    # chord plane subtracted (the pod side is +z), worst flying CG = forward limit and the top of the z range.
    h_corner = c - x_range[0] + foot
    h_target = c - x_target + foot
    return {"cg_height_corner_m": h_corner, "cg_height_target_m": h_target,
            "narrow_corner_deg": math.degrees(math.atan((z_pad - z_range[1]) / h_corner)),
            "narrow_target_deg": math.degrees(math.atan(z_pad / h_target)),
            "wide_corner_deg": math.degrees(math.atan(y_fin / h_corner)),
            "footprint_m": [2 * y_fin, 2 * z_pad]}


@kit.calc("CALC-A1-BOX", title="Box fit", assumes=["ASM-A1-WALL"],
          equation="internal = external - 2 wall ; slack = internal - envelope (sorted largest first)",
          inputs={"ext": P + "requirements.box_external_m", "wall": "ASM-A1-WALL",
                  "env": P + "transport.envelope_props_off_m"}, units={"ext": "m", "wall": "m", "env": "m"})
def box_fit(ext, wall, env):
    inner = sorted((e - 2 * wall for e in ext), reverse=True)
    envs = sorted(env, reverse=True)
    slack = [i - e for i, e in zip(inner, envs)]
    return {"internal_m": inner, "slack_m": slack, "slack_min_m": min(slack)}


# ---------------------------------------------------------------- CG range vs the B3 claims (D-24 closed D-17)
@kit.calc("CALC-A1-CG-RANGE", title="params cg range sits inside B3's R1 claims and holds the pack-centred CG",
          equation="fwd_ok = x_range[0] - x_fwd ; aft_ok = x_aft - x_range[1] ; "
                   "centred_fwd = cg_centred - x_range[0] ; centred_aft = x_range[1] - cg_centred ; sm_aft = (x_np - x_range[1]) / c",
          inputs={"x_range": P + "cg.x_range_m", "x_fwd": "CL-B3-CG-FWD", "x_aft": "CL-B3-CG-AFT",
                  "cg_centred": "CL-B3-CG-CENTRED-AFT", "x_np": "CL-B3-XNP", "c": P + "wing.chord_m",
                  "sm_min": P + "requirements.static_margin_min"},
          units={"x_range": "m", "x_fwd": "m", "x_aft": "m", "cg_centred": "m", "x_np": "m", "c": "m"})
def cg_range(x_range, x_fwd, x_aft, cg_centred, x_np, c, sm_min):
    # CL-B3-CG-CENTRED-AFT is B3's aft margin (m) of the pack-centred CG; recover the CG itself from the aft limit.
    cg = x_aft - cg_centred
    return {"fwd_inside_m": x_range[0] - x_fwd, "aft_inside_m": x_aft - x_range[1],
            "cg_pack_centred_m": cg, "centred_fwd_margin_m": cg - x_range[0],
            "centred_aft_margin_m": x_range[1] - cg, "sm_at_aft_limit": (x_np - x_range[1]) / c - sm_min}


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
kit.claim("CL-A1-TIPOVER", "Tip-over angle toward the pod side, worst flying CG corner (forward limit, z +0.03)",
          calc="CALC-A1-TIPOVER", output="narrow_corner_deg", unit="deg",
          limit=(">=", P + "requirements.tipover_min_deg"), verifies=["R-TIPOVER"], parts=["GER-001-UR", "GER-001-UL", "GER-001-LR", "GER-001-LL"],
          note="D-30: frame-level corner bound with D5's pad contact z (CL-D5-CONTACT-Z); C5's CL-C5-TIPOVER-WORST (32.4 deg) is the claim of record.",
          how="Stand the aircraft on a tilting board with the pack at the forward limit (C5 T-C5-TIPOVER / H1 GT-10): record the angle at which it tips toward the pod.")
kit.claim("CL-A1-TIPOVER-TARGET", "Tip-over angle toward the pod side at the CG target, z_cg 0",
          calc="CALC-A1-TIPOVER", output="narrow_target_deg", unit="deg",
          how="As CL-A1-TIPOVER with the pack at the target station; compare with C5's CL-C5-TIPOVER-R1 (32.8 deg, z_cg 0.017).")
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
          note="D-35: voltage_sag 0.76 is E2's limiter-consistent factor (CL-E2-SAG-F-WORST); E1's CL-E1-TW-WORST 2.18 (factor 0.854) is the other bound until the two publish one claim.",
          how="Thrust-stand run on a pack at 3.6 V/cell after a cold soak at 10 degC (H1 GT-02, pass line CL-H1-T-PASS-SAG >= 1.102 kgf), or the fresh value x CL-E2-SAG-F-WORST.")
kit.claim("CL-A1-STALL-GATE", "Stall speed at the gate", calc="CALC-A1-STALL", output="vs_ms", unit="m/s",
          limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="Trimmed CLmax from B2 (CL-B2-CLMAX-DESIGN); flight test: slow-flight stall in FBWA at altitude with airspeed logged (H2, T-B2-STALL).")
kit.claim("CL-A1-TRANSITION-GATE", "Transition speed at the gate", calc="CALC-A1-STALL", output="vt_ms", unit="m/s",
          limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="Cruise 16 m/s (B1) against 1.3 x the trimmed stall; log airspeed at 'Transition FW done' (F4/H2). Closed by D-01: chord 0.32 and cruise 16 m/s.")
kit.claim("CL-A1-RESERVE", "Pessimistic reserve at order", calc="CALC-A1-RESERVE", output="reserve_usd", unit="USD",
          limit=(">=", P + "requirements.crash_cost_usd"), verifies=["R-RESERVE", "R-BUDGET"],
          how="I1 re-prices the BOM at order time; reserve = 2 000 - spend, pessimistic column.")

kit.claim("CL-A1-CG-RANGE-FWD", "params cg.x_range_m forward end is inside B3's R1 forward limit",
          calc="CALC-A1-CG-RANGE", output="fwd_inside_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          note="D-24 (closes D-17): params carry B3's range rounded inward; recomputes when B3 re-runs for the 7 deg cant and 0.21 m fins.",
          how="Re-run after any B3 publish; the built aircraft is balanced at both marks (T-A3-CG-BALANCE, H1 GT-07).")
kit.claim("CL-A1-CG-RANGE-AFT", "params cg.x_range_m aft end is inside B3's R1 aft limit (SM 5 %)",
          calc="CALC-A1-CG-RANGE", output="aft_inside_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE", "R-STATIC-MARGIN"],
          how="As CL-A1-CG-RANGE-FWD; static margin at the aft mark from the twin's glide tests (T-B3-TWIN-NP).")
kit.claim("CL-A1-CG-CENTRED", "Pack centred in the pod at x_le -0.105 layout: CG margin to the forward end of the range",
          calc="CALC-A1-CG-RANGE", output="centred_fwd_margin_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          note="D-24: the pod stays; A3 sets the pack nominal centroid to x -0.001 m (4 mm aft of the old pod centre) and D2 lays the bay for it.",
          how="A3 roll-up at the R3 allocations (CL-A3-CG-X-RANGE); balance test with the pack at the nominal station.")

kit.test("T-A1-WEIGH","Weigh the assembled aircraft", verifies=["CL-A1-MASS-SIZED"], state="planned",
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
                 "allocations + requirements.growth_allowance_kg + requirements.build_overrun_kg (D-38: 170 + 100 g). "
                 "A3 refines allocations in MASS-CG.md through a change request to A1.",
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
