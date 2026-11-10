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
kit.assumption("ASM-A1-WALL", "Box wall stack 12.5 mm per side along the chord",
               "The transport box loses 12.5 mm per side along the chord: 4 mm corrugated shell at both ends plus the "
               "1/2 in PE nose pad (D7-R4 stack after D-62: 4 + 4 + 12.7 = 20.7 mm over two sides); the span and height "
               "faces lose 4 mm plus the cradle and pillar preloads, less than this",
               basis="D7 CL-D7-NOSE-GAP (12.95 mm at the 0.498 m envelope with a 3/4 in pad); D-62 moves the nose 10 mm and "
                     "the pad goes to 1/2 in (CR-A1-66). Was 25 mm (R0 guess: 1/4 in ply + 18 mm foam)",
               value=0.0125, unit="m", cites=["SRC-K09-REVIEW"])
kit.assumption("ASM-A1-A3-PACK-X", "Pack station A3's current roll-up carries",
               "The pack centroid x at which A3's published CL-A3-CG-X and CL-A3-MASS-BASIC were rolled up",
               basis="A3-R6a (2026-11-10) rolled the carried pack at the D-47 datum -0.022 m. D-62 moves the datum to "
                     "-0.032 m; until A3 re-runs on D2's R6 bay this assumption recovers the empty-aircraft moment from "
                     "A3's numbers. Set it equal to pod.pack_x_nominal_m (and retire it) once A3 has re-run",
               value=-0.022, unit="m", status="UNVERIFIED", cites=["SRC-K09-REVIEW"])
kit.assumption("ASM-A1-STACK-DX", "Aircraft CG shift from D-61 not yet in A3's roll-up",
               "D-61 moves the four motor stacks (motor, adapter, prop, nut; about 108 g each) 5 mm forward "
               "(face_ahead_m 0.0025 -> 0.0075): about -0.9 mm on the take-off CG",
               basis="E1 CR-E1-44 estimate (4 x 108 g x 5 mm / 2 322 g = 0.93 mm). Set to 0 once A3 re-runs on E1's "
                     "D-61 centroids", value=-0.0009, unit="m", status="UNVERIFIED", cites=["SRC-K09-REVIEW"])
kit.assumption("ASM-A1-PACK-CASES-G", "Pack masses the frame checks (D-64)",
               "Lightest and heaviest flight pack the CG and gate checks run with: the Ovonic 120C EC5 listing minus "
               "its tolerance (546 g) and the acceptance line A1 set in D-64 (590 g; CALC-A1-PACK-ACCEPT gives the exact "
               "figure from A3's gate margin)",
               basis="E2 CR-E2-24: listing 551 +/- 5 g. D-64 retires the 503 / 680 g bounding listings of D-58/D-59 as "
                     "flight cases; A3 updates ASM-A3-PACK-RANGE to the same pair", value=[546.0, 590.0], unit="g",
               status="PROPOSED", cites=["SRC-E2-OVONIC-120C-EC5"])
kit.assumption("ASM-A1-R5-ADDED-G", "Flying mass added by the R5 decisions, not yet in A3's roll-up",
               "C3's pod fixes +13.9 g EST (CR-C3-14/-15/-16), D-62 nose shell +2 g, C6 pins 2.5 mm +1.5 g and collar "
               "13 mm +0.6 g, D3's sealing bead -1.6 g, C5's shoe sleeve fix +5 g EST (CR-C5-18): +21.4 g",
               basis="D-63; set to 0 once D2, D3 and D5 publish and A3 re-runs", value=21.4, unit="g",
               status="UNVERIFIED", cites=["SRC-K09-REVIEW"])


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
@kit.calc("CALC-A1-CG-RANGE", title="params cg range sits inside B3's V1 claims (CG height included) and holds the target",
          equation="fwd_ok = x_range[0] - x_fwd ; aft_ok = x_aft - x_range[1] ; width = x_range[1] - x_range[0] ; "
                   "target_fwd = x_t - x_range[0] ; target_aft = x_range[1] - x_t ; sm_aft = (x_np - x_range[1]) / c - sm_min",
          inputs={"x_range": P + "cg.x_range_m", "x_fwd": "CL-B3-V-CG-FWD", "x_aft": "CL-B3-V-CG-AFT-ENV",
                  "x_t": P + "cg.x_target_m", "x_np": "CL-B3-V-XNP-ENV", "c": P + "wing.chord_m",
                  "sm_min": P + "requirements.static_margin_min"},
          units={"x_range": "m", "x_fwd": "m", "x_aft": "m", "x_t": "m", "x_np": "m", "c": "m"})
def cg_range(x_range, x_fwd, x_aft, x_t, x_np, c, sm_min):
    # D-62: B3's V1 limits carry the take-off CG height (cg.z_target_m); the R4 ids CL-B3-CG-FWD/-AFT (z = 0) are
    # superseded. The old pack-centred check (CL-B3-CG-CENTRED-AFT, B3 R3) is retired: CALC-A1-PACK-CASES checks
    # every pack against the range on A3's live roll-up.
    return {"fwd_inside_m": x_range[0] - x_fwd, "aft_inside_m": x_aft - x_range[1],
            "width_m": x_range[1] - x_range[0], "target_fwd_margin_m": x_t - x_range[0],
            "target_aft_margin_m": x_range[1] - x_t, "sm_at_aft_limit": (x_np - x_range[1]) / c - sm_min}


@kit.calc("CALC-A1-PACK-CASES", title="CG per weighed pack at its D-60 flight station in the D-62 bay",
          assumes=["ASM-A3-NOSE-STACK", "ASM-A1-A3-PACK-X", "ASM-A1-STACK-DX", "ASM-A1-PACK-CASES-G"],
          equation="x_cg = CL-A3-CG-X * c + dx_stack ; dx = CL-A3-CG-X-PRED - CL-A3-CG-X * c ; M_e x_e = M x_cg - m_p x_a3 "
                   "(A3 rolls the carried pack at x_a3) ; x_fwd = x_pod_le + nose + L/2 ; x_aft = x_nom + aft_travel ; "
                   "g(m) = dx M / (M_e + m) ; x_p(m) = x_aft - k step, k >= 0 the whole step that puts the mid of basic "
                   "and predicted CG, x_cg(m) + g(m)/2, nearest x_t, x_p >= x_fwd ; "
                   "x_cg(m) = (M_e x_e + m x_p) / (M_e + m) ; x_pred = x_cg + g(m) ; "
                   "fwd margin = min x_cg - x_range[0] ; aft margin = x_range[1] - max x_pred ; "
                   "ballast(nose) = (M_e + m) excess / (x_pred - x_pod_le)",
          inputs={"M_kg": "CL-A3-MASS-BASIC", "cg_frac": "CL-A3-CG-X", "x_pred_a3": "CL-A3-CG-X-PRED",
                  "c": P + "wing.chord_m", "x_t": P + "cg.x_target_m", "mp_kg": P + "battery.mass_kg",
                  "x_rng": P + "cg.x_range_m", "pod_le": P + "pod.x_le_m", "pack": P + "battery.size_m",
                  "nose": "ASM-A3-NOSE-STACK", "x_nom": P + "pod.pack_x_nominal_m",
                  "aft_travel": P + "pod.pack_aft_travel_m", "step": P + "pod.pack_spacer_step_m",
                  "pack_rng": "ASM-A1-PACK-CASES-G", "x_a3": "ASM-A1-A3-PACK-X", "dx_stack": "ASM-A1-STACK-DX"},
          units={"M_kg": "kg", "c": "m", "x_pred_a3": "m", "x_t": "m", "mp_kg": "kg", "x_rng": "m", "pod_le": "m",
                 "pack": "m", "nose": "m", "x_nom": "m", "aft_travel": "m", "step": "m", "pack_rng": "g", "x_a3": "m",
                 "dx_stack": "m"})
def pack_cases(M_kg, cg_frac, x_pred_a3, c, x_t, mp_kg, x_rng, pod_le, pack, nose, x_nom, aft_travel, step,
               pack_rng, x_a3, dx_stack):
    # D-60. The empty-aircraft moment comes from A3's published CG and mass with the carried pack at the station A3
    # rolled it at (ASM-A1-A3-PACK-X; equal to pod.pack_x_nominal_m once A3 re-runs on the D-62 bay). It no longer
    # inverts CL-A3-PACK-X-REQ: that claim is computed on A3's copy of cg.x_target_m, so a target change made the
    # inversion wrong until A3 re-ran. Growth by maturity is A3's own CL-A3-CG-X-PRED. D-61's 5 mm stack move
    # enters as ASM-A1-STACK-DX until A3 re-runs on E1's centroids. Each weighed pack flies at the whole spacer step
    # that puts the middle of its basic-to-predicted CG band nearest the target, never ahead of the crush stack:
    # basic is the forward-limit case and predicted the aft-limit case, so the band is centred on B3's target.
    # D-64: the packs checked are the SKU listing minus tolerance, the carried mass and the acceptance line.
    M, mp = M_kg * 1000.0, mp_kg * 1000.0
    x_cg = cg_frac * c + dx_stack
    dx_growth = x_pred_a3 - cg_frac * c
    Me = M - mp
    mom_e = M * x_cg - mp * x_a3
    x_fwd = pod_le + nose + pack[0] / 2.0
    x_aft = x_nom + aft_travel
    k_max = int((x_aft - x_fwd) / step + 1e-9)
    cases = {}
    for m in (pack_rng[0], mp, pack_rng[1]):
        g = dx_growth * M / (Me + m)
        want = ((x_t - g / 2.0) * (Me + m) - mom_e) / m
        k = min(max(round((x_aft - want) / step), 0), k_max)
        xp = x_aft - k * step
        xb = (mom_e + m * xp) / (Me + m)
        xpred = xb + g
        excess = max(0.0, xpred - x_rng[1])
        cases[f"{m:.0f}"] = {"spacer_m": k * step, "station_m": xp, "cg_basic_m": xb, "cg_pred_m": xpred,
                             "nose_ballast_g": (Me + m) * excess / (xpred - pod_le)}
    st = [v["station_m"] for v in cases.values()]
    return {"growth_dx_m": dx_growth, "empty_x_m": mom_e / Me, "pack_x_fwd_limit_m": x_fwd, "pack_x_aft_limit_m": x_aft,
            "fwd_room_nominal_m": x_nom - x_fwd, "travel_left_fwd_m": min(st) - x_fwd,
            "cases": cases,
            "fwd_margin_min_m": min(v["cg_basic_m"] for v in cases.values()) - x_rng[0],
            "aft_margin_pred_min_m": x_rng[1] - max(v["cg_pred_m"] for v in cases.values()),
            "aft_margin_basic_min_m": x_rng[1] - max(v["cg_basic_m"] for v in cases.values()),
            "nose_ballast_max_g": max(v["nose_ballast_g"] for v in cases.values()),
            "ballast_g_per_mm": (Me + mp) * 0.001 / (x_t - pod_le)}


@kit.calc("CALC-A1-PACK-ACCEPT", title="Heaviest flight pack the first-build overrun still covers (D-64 acceptance line)",
          assumes=["ASM-A1-R5-ADDED-G", "ASM-A1-PACK-CASES-G"],
          equation="accept = m_pack + gate_margin - overrun - added ; margin_sku = accept - (sku_min + 10)",
          inputs={"m_pack_kg": P + "battery.mass_kg", "gate_margin_kg": "CL-A3-GATE-MARGIN",
                  "overrun_kg": P + "requirements.build_overrun_kg", "added_g": "ASM-A1-R5-ADDED-G",
                  "sku_g": "ASM-A1-PACK-CASES-G"},
          units={"m_pack_kg": "kg", "gate_margin_kg": "kg", "overrun_kg": "kg", "added_g": "g", "sku_g": "g"})
def pack_accept(m_pack_kg, gate_margin_kg, overrun_kg, added_g, sku_g):
    # CL-A3-GATE-MARGIN is the predicted gate margin (growth by maturity applied) with the carried pack; a heavier
    # pack eats it gram for gram (A3 carries the pack at 0 % growth). The SKU's listed maximum is 551 + 5 = 556 g.
    accept = m_pack_kg * 1000.0 + gate_margin_kg * 1000.0 - overrun_kg * 1000.0 - added_g
    return {"accept_g": accept, "margin_to_sku_max_g": accept - (sku_g[0] + 10.0)}


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
    planned = round(1000.0 * (growth_kg + overrun_kg), 6)          # whole grams: no float-dust negative margin
    return {"allocated_g": s, "sized_kg": (s + planned) / 1000.0, "reserve_cover_g": round(reserve - planned, 6),
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
kit.claim("CL-A1-PROP-CLEAR", "Minimum prop clearance (frame bound: disc edge to the wing plane)", calc="CALC-A1-PROP-CLEAR", output="gap_min_m", unit="m",
          limit=(">=", P + "requirements.prop_clearance_min_m"), verifies=["R-PROP-CLEAR"],
          note="D-61: this frame bound (uncanted disc, hub mid-plane) is not the governing clearance. The claims of record are E1's "
               "CL-E1-TIP-GAP-TUBE / B4's CL-B4-GAP-TUBE-ENV (blade swept volume to the CF motor tube at the 7 deg cant: 21.1 mm at "
               "face_ahead 2.5 mm, 26.1 mm at the D-61 7.5 mm, CL-E1-TIP-GAP-AT-75) and B4's CL-B4-TIP-WING (34.2 mm to the upper skin).",
          how="check.py hull keep-out test (A5) on D3's R5 mount, then a 25 mm printed gauge on the built aircraft between the blade tip and the tube (T-B4-INSTALLED).")
kit.claim("CL-A1-TIPOVER", "Tip-over angle toward the pod side, worst flying CG corner (forward limit, top of cg.z_range_m)",
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
          how="growth_reserve_g in params.json minus (growth allowance + 100 g build overrun; D-63: 114 + 100 = 214 g, 0 g free); A3's maturity growth (CL-A3-GATE-MARGIN) is the stricter check.")
kit.claim("CL-A1-ALLOC-GATE", "Allocations plus reserve equal the gate", calc="CALC-A1-MASS-SIZED",
          output="gate_check_g", unit="g", limit=(">=", 0.0), verifies=["R-MASS-GATE"],
          how="2 600 - sum(allocation_g) - growth_reserve_g must be >= 0; A1 re-runs this script after any allocation change.")
kit.claim("CL-A1-HOVER-TW-GATE", "Hover T/W at the 2.6 kg gate", calc="CALC-A1-HOVER-TW", output="tw_gate", unit="-",
          limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"],
          how="Thrust stand, one station, 11x5.5MR on a fresh pack with the 100 A limiter (24.8 A per motor): thrust >= 1.3 kgf gives T/W 2.0 at 2.6 kg (H1, T-E1-STAND).")
kit.claim("CL-A1-HOVER-TW-SAG", "Hover T/W at the gate, worst pack state", calc="CALC-A1-HOVER-TW", output="tw_gate_sag", unit="-",
          limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"],
          note="D-49: voltage_sag 0.851 is the one E1/E2 calculation (CALC-E1-WORST on E2's cell data and F1's r_ext 6.5 mOhm, CL-E1-SAG-FACTOR; CL-E1-TW-WORST 2.12); was 0.76 (D-35).",
          how="Thrust-stand run on a pack at 3.6 V/cell after a cold soak at 10 degC (H1 GT-02, pass line CL-H1-T-PASS-SAG >= 1.102 kgf), or the fresh value x CL-E1-SAG-FACTOR (CL-E1-TW-WORST).")
kit.claim("CL-A1-STALL-GATE", "Stall speed at the gate", calc="CALC-A1-STALL", output="vs_ms", unit="m/s",
          limit=("<=", P + "requirements.stall_max_ms"), verifies=["R-STALL"],
          how="Trimmed CLmax from B2 (CL-B2-CLMAX-DESIGN); flight test: slow-flight stall in FBWA at altitude with airspeed logged (H2, T-B2-STALL).")
kit.claim("CL-A1-TRANSITION-GATE", "Transition speed at the gate", calc="CALC-A1-STALL", output="vt_ms", unit="m/s",
          limit=("<=", P + "performance.cruise_ms"), verifies=["R-TRANSITION"],
          how="Cruise 16 m/s (B1) against 1.3 x the trimmed stall; log airspeed at 'Transition FW done' (F4/H2). Closed by D-01: chord 0.32 and cruise 16 m/s.")
kit.claim("CL-A1-RESERVE", "Pessimistic reserve at order", calc="CALC-A1-RESERVE", output="reserve_usd", unit="USD",
          limit=(">=", P + "requirements.crash_cost_usd"), verifies=["R-RESERVE", "R-BUDGET"],
          how="I1 re-prices the BOM at order time; reserve = 2 000 - spend, pessimistic column.")

kit.claim("CL-A1-CG-RANGE-FWD", "params cg.x_range_m forward end is inside B3's V1 forward limit (trim at the stall, CG height included)",
          calc="CALC-A1-CG-RANGE", output="fwd_inside_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          note="D-62 (CR-B3-25): params carry B3's V1 range rounded inward to 0.1 mm, [0.0466, 0.0514]; the take-off CG 18.5 mm above the chord plane moves the effective NP 3.4 mm forward at 1.3 Vs, so the whole range slides 4.3 mm forward at the same width (4.8 mm). Was [0.0509, 0.0548] (D-60, B3 R4 at z = 0), [0.050, 0.0549] (D-47).",
          how="Re-run after any B3 publish; the built aircraft is balanced at both marks (T-A3-CG-BALANCE, H1 GT-07).")
kit.claim("CL-A1-CG-RANGE-AFT", "params cg.x_range_m aft end is inside B3's V1 aft limit (SM 5 % at 1.3 Vs, CG height included)",
          calc="CALC-A1-CG-RANGE", output="aft_inside_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE", "R-STATIC-MARGIN"],
          how="As CL-A1-CG-RANGE-FWD; static margin at the aft mark from the twin's glide tests (T-B3-TWIN-NP).")
kit.claim("CL-A1-CG-WIDTH", "Width of the CG range between the balance marks",
          calc="CALC-A1-CG-RANGE", output="width_m", unit="m", limit=(">=", 0.004), verifies=["R-CG-RANGE"],
          note="B3's CL-B3-V-CG-WIDTH-ENV 4.85 mm on the unrounded limits; the full D6 free-play band (not half) would take it to 3.3 mm (CR-B3-23: D6 centres each servo in its band).",
          how="Distance between the two marks on the fin roots.")
kit.claim("CL-A1-CG-TARGET-IN", "CG target sits inside the range with the smaller of its two margins",
          calc="CALC-A1-CG-RANGE", output="target_fwd_margin_m", unit="m", limit=(">=", 0.002), verifies=["R-CG-RANGE"],
          note="D-62: target 0.0490 = range mid (2.4 mm to each mark); replaces CL-A1-CG-CENTRED (B3's R3 pack-centred CG, retired with CL-B3-CG-CENTRED-AFT).",
          how="Balance the built aircraft with the carried pack at its flight-card station: the CG mark falls between the two limit marks.")
kit.claim("CL-A1-PACK-STATION", "Lightest pack at its D-60 station: forward travel left to the crush stack",
          calc="CALC-A1-PACK-CASES", output="travel_left_fwd_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          parts=["PWR-001", "POD-008"], assumes=["ASM-A3-NOSE-STACK"],
          note="D-62 bay: most forward centroid = pod.x_le_m (-0.140) + 34.6 mm + L/2 = -0.0379 m for the 135 mm Ovonic EC5 pack (D-64); "
               "the no-spacer station is -0.020 (aft stop 0.050). A1-R4a (D-59) had -0.0254 / -0.010 in the D-47 bay.",
          how="D2 re-lays the bay (CR-A1-62); T-A3-CG-BALANCE with each pack at its flight-card station.")
kit.claim("CL-A1-PACK-CG-FWD", "Every pack (546 / 550 / 590 g, D-64) at its D-60 station: basic CG margin to the forward limit",
          calc="CALC-A1-PACK-CASES", output="fwd_margin_min_m", unit="m", limit=(">=", 0.0), verifies=["R-CG-RANGE"],
          parts=["PWR-001", "POD-008"],
          note="Worst case is the heaviest pack at the no-spacer station (nominal + pod.pack_aft_travel_m 12 mm, D-59/D-60); growth moves the "
               "CG aft, so basic is the forward-limit case. D-62 estimate on A3-R6a with ASM-A1-A3-PACK-X and ASM-A1-STACK-DX; A3 re-runs on D2's R6 bay.",
          how="T-A3-CG-BALANCE / H1 GT-07 with each weighed pack at its flight-card station.")
kit.claim("CL-A1-PACK-CG-AFT", "Every pack at its D-60 station: predicted CG (growth by maturity) margin to the aft limit",
          calc="CALC-A1-PACK-CASES", output="aft_margin_pred_min_m", unit="m", limit=(">=", 0.0),
          verifies=["R-CG-RANGE", "R-STATIC-MARGIN"], parts=["PWR-001", "POD-008"],
          note="D-62: worst case is the lightest pack (546 g) at or near the crush stack; growth is A3's CL-A3-CG-X-PRED scaled by mass. The 503 g listing is no longer a flight case (D-64).",
          how="T-A3-CG-BALANCE on the built aircraft; never fly aft of the aft mark (B3).")
kit.claim("CL-A1-NOSE-BALLAST", "Nose ballast the predicted CG needs with the worst pack (D-59 cap 10 g, D-60 rule)",
          calc="CALC-A1-PACK-CASES", output="nose_ballast_max_g", unit="g", limit=("<=", 10.0), verifies=["R-CG-RANGE"],
          note="About 13 g per mm of CG at the pod nose, from the A1 reserve; beyond 10 g A1 re-opens the station.",
          how="Balance the built aircraft; add lead tape behind the nose block until the CG is 0.5 mm ahead of the aft mark; weigh it.")
kit.claim("CL-A1-PACK-ACCEPT", "Heaviest flight pack the 100 g first-build overrun still covers (D-64 acceptance line)",
          calc="CALC-A1-PACK-ACCEPT", output="accept_g", unit="g", limit=(">=", 556.0), verifies=["R-MASS-GATE", "R-PACK-MASS"],
          parts=["PWR-001"],
          note="D-64: replaces the D-58/D-59 lines (601 -> 631 g on the old bounding listings). The Ovonic 120C EC5 lists 551 +/- 5 g, so the limit here is its maximum 556 g; E2's PACK_ACCEPT_KG and the T-E2-WEIGH pass line follow this claim. A3 publishes the same figure from its roll-up (CL-A3-GATE-MARGIN) once D2, D3 and D5 deliver the R5 parts.",
          how="Weigh each pack on arrival (T-E2-WEIGH, 1 g scale); a pack above this line is returned or the first build must come in under its allocations.")

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
                 "allocations + requirements.growth_allowance_kg + requirements.build_overrun_kg (D-63: 114 + 100 g). "
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
