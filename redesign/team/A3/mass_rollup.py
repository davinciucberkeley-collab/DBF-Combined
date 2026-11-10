"""A3 mass-properties engineer: live mass, CG and inertia roll-up for the K09-L quad tailsitter.

Run (from the repo root):
    python -I redesign/team/A3/mass_rollup.py            # roll up, write claims + reports, refresh MASS-CG.md
    python -I redesign/team/A3/mass_rollup.py --check    # exit 1 if the stored roll-up is stale (CI / phase gate)
then  python -I redesign/proofs/build_graph.py

Sources, in precedence order (whole subsystem at a time, so nothing is counted twice):
  1. redesign/subsystems/<key>/parts.csv   designer's part list. mass_g is PER UNIT; line mass = qty x mass_g.
     Positions from the same folder's interfaces.json (cg_xyz_m per instance; id == part_id or part_id-<suffix>).
     Status from interfaces.json: VERIFIED -> WEIGHED, CHECKED/MODELLED -> CAD, PROPOSED -> DATASHEET (buy) / EST.
     Subsystem `transport` and parts with "flight": false are ground items and are never counted.
  2. redesign/team/<role>/mass_estimate.csv  any role's estimate, same columns as team/A3/mass_model.csv;
     replaces an A3 model row with the same item_id, adds new item_ids. Ignored for a subsystem once 1 exists.
  3. redesign/team/A3/mass_model.csv        A3 bottom-up estimate (cells starting '=' are expressions of P:keys).

Outputs (all generated; do not edit by hand):
  team/A3/rollup/mass_items.json   the merged item table as a params file (input of the proof calcs)
  team/A3/claims.json              proof-chain claims (proofkit)
  team/A3/rollup/ROLLUP.md         every item with its source, mass, growth and position
  team/A3/rollup/rollup.json       totals, CG cases, inertia (for the viewer / other scripts)
  redesign/MASS-CG.md              the block between the 'rollup:begin' and 'rollup:end' markers
Python 3 standard library only.
"""
import argparse
import ast
import csv
import json
import math
import operator
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RED = HERE.parents[1]                                       # redesign/
sys.path.insert(0, str(RED / "proofs"))
import proofkit as pk  # noqa: E402

ITEMS_FILE = HERE / "rollup" / "mass_items.json"
ITEMS_KEY = "a3.rollup.items"
SUBSYSTEMS = ["wing", "fins", "pod", "landing", "propulsion", "power", "avionics", "harness", "mechanisms"]
GROUND = {"transport"}                                      # flight: false by definition
DISCIPLINES = ["structure", "propulsion", "energy", "electrical", "avionics", "controls"]
PREFIX_DISC = {"WNG": "structure", "FIN": "structure", "POD": "structure", "GER": "structure",
               "PRP": "propulsion", "PWR": "electrical", "AVN": "avionics", "HRN": "electrical", "MEC": "controls"}
STATUS_MAT = {"VERIFIED": "WEIGHED", "CHECKED": "CAD", "MODELLED": "CAD"}
COLS = ["id", "subsystem", "discipline", "mass_g", "x", "y", "z", "lx", "ly", "lz", "maturity", "growth_pct",
        "source"]                                           # one row per physical instance

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ------------------------------------------------------------------ assumptions
kit.assumption("ASM-A3-MGA", "Mass growth allowance by maturity",
               "Growth added to each item's basic mass by how it was obtained: EST 20 %, CALC 10 %, DATASHEET 5 %, "
               "CAD 5 %, WEIGHED 1 %. An item may override. The pack carries 0 %: its listing spread is not growth "
               "but a bounding case, reported separately at 503 / 550 / 680 g (ASM-A3-PACK-RANGE).",
               basis="Maturity-based allowance after AIAA S-120A (mass properties control); percentages are A3's "
                     "choice for a student foam build, ESTIMATE", value={"EST": 20, "CALC": 10, "DATASHEET": 5,
                                                                         "CAD": 5, "WEIGHED": 1}, unit="%")
kit.assumption("ASM-A3-PACK-SLIDE", "Pack fore-aft trim travel from its nominal station",
               "Printed U-spacers behind the pack (0-22 mm in 2 mm steps, POD-008); the nominal 550 g pack flies "
               "the 8 mm spacer, so the pack can go 8 mm aft (no spacer) or up to 14 mm forward (22 mm of "
               "spacers), the forward travel further limited by the crush stack (ASM-A3-NOSE-STACK)",
               basis="subsystems/pod/params.json spacer_set_m, spacer_flown_m, aft_stop_x_m 0.077 (D2-R3)",
               value=[-0.014, 0.008], unit="m", status="PROPOSED")
kit.assumption("ASM-A3-PACK-RANGE", "Pack mass range from listings", "Ovonic 4S 6500 listings give 503 to 680 g",
               basis="config-study/cards/K09/REVIEW.md section 2; weigh on arrival", value=[503.0, 680.0], unit="g",
               status="UNVERIFIED", cites=["SRC-K09-REVIEW", "SRC-OVONIC-4S6500"])
kit.assumption("ASM-A3-NOSE-STACK", "Length from the pod nose to the most forward pack fore face",
               "Pod nose -0.115 to the forward-stop aft face -0.1002 (14.8 mm: nose block, 3 mm stop) + XPS F-250 "
               "crush block >= 24.3 mm + 1.5 mm PETG spreader = 40.6 mm",
               basis="subsystems/pod/params.json fwd_stop_x_m -0.1002 (D2-R3, D-25); crush block C5 CR-C5-02, "
                     "spreader_t_m 0.0015", value=0.0406, unit="m")


# ------------------------------------------------------------------ pure calculations (re-run by build_graph)
def _rows(items):
    return [dict(zip(COLS, r)) for r in items]


def _growth(r, mga):
    return (r["growth_pct"] if r["growth_pct"] is not None else mga[r["maturity"]]) / 100.0


@kit.calc("CALC-A3-MASS", title="Mass roll-up against allocations and the gate",
          assumes=["ASM-A3-MGA", "ASM-A3-PACK-RANGE"],
          equation="basic = sum m_i ; predicted = sum m_i (1 + MGA_i) ; margin = gate - predicted ; "
                   "margin(pack m) = gate - (predicted - m_pack,carried + m) ; overrun_s = basic_s - alloc_s",
          inputs={"items": P + ITEMS_KEY, "mga": "ASM-A3-MGA", "gate_kg": P + "requirements.mtow_gate_kg",
                  **{k: f"{P}mass.allocation_g.{k}" for k in SUBSYSTEMS}, "growth_g": P + "mass.growth_reserve_g",
                  "pack_rng": "ASM-A3-PACK-RANGE"},
          units={"gate_kg": "kg", **{k: "g" for k in SUBSYSTEMS}, "growth_g": "g", "pack_rng": "g"})
def mass_rollup(items, mga, gate_kg, growth_g, pack_rng, **alloc):
    rows = _rows(items)
    by_sub, by_disc = {}, {}
    for r in rows:
        g = _growth(r, mga)
        for table, key in ((by_sub, r["subsystem"]), (by_disc, r["discipline"])):
            t = table.setdefault(key, [0.0, 0.0])
            t[0] += r["mass_g"]
            t[1] += r["mass_g"] * (1 + g)
    basic = sum(v[0] for v in by_sub.values())
    pred = sum(v[1] for v in by_sub.values())
    subs = [[k, float(alloc.get(k, 0)), round(by_sub.get(k, [0, 0])[0], 1), round(by_sub.get(k, [0, 0])[1], 1)]
            for k in SUBSYSTEMS + sorted(set(by_sub) - set(SUBSYSTEMS))]
    worst = max(subs, key=lambda s: s[2] / s[1] if s[1] else float("inf"))
    mp_pred = sum(r["mass_g"] * (1 + _growth(r, mga)) for r in rows if r["discipline"] == "energy")

    def pred_with(pack_g):                                    # same aircraft, pack of this (weighed) mass
        return (pred - mp_pred + pack_g) / 1000
    return {"basic_kg": basic / 1000, "predicted_kg": pred / 1000, "mga_kg": (pred - basic) / 1000,
            "pack_carried_g": by_disc.get("energy", [0, 0])[0],
            "predicted_pack_light_kg": pred_with(pack_rng[0]), "predicted_pack_heavy_kg": pred_with(pack_rng[1]),
            "gate_margin_kg": gate_kg - pred / 1000,
            "gate_margin_pack_light_kg": gate_kg - pred_with(pack_rng[0]),
            "gate_margin_pack_heavy_kg": gate_kg - pred_with(pack_rng[1]),
            "allocated_g": float(sum(alloc.values())),
            "a1_sized_kg": (sum(alloc.values()) + growth_g) / 1000,
            "by_subsystem_g": subs,                                  # [name, alloc, basic, predicted]
            "by_discipline_g": [[k, round(by_disc.get(k, [0, 0])[0], 1), round(by_disc.get(k, [0, 0])[1], 1)]
                                for k in DISCIPLINES + sorted(set(by_disc) - set(DISCIPLINES))],
            "worst_alloc_ratio": worst[2] / worst[1] if worst[1] else float("inf"),
            "worst_alloc_subsystem": worst[0], "overrun_total_g": sum(max(0.0, s[2] - s[1]) for s in subs)}


def _cg(rows, w=None):
    w = w or (lambda r: r["mass_g"])
    m = sum(w(r) for r in rows)
    return m, [sum(w(r) * r[a] for r in rows) / m for a in "xyz"]


@kit.calc("CALC-A3-CG", title="CG cases, pack station for the target, hover trim split",
          assumes=["ASM-A3-MGA", "ASM-A3-PACK-SLIDE", "ASM-A3-PACK-RANGE", "ASM-A3-NOSE-STACK"],
          equation="cg = sum m_i r_i / sum m_i ; x_pack_req = (x_t M - (M x_cg - m_p x_p)) / m_p ; "
                   "split = (z_m + z_cg) / (z_m - z_cg) ; h_stance = c - x_cg + foot ; "
                   "fwd_room = (x_pack - L_pack/2) - x_pod_le - nose_stack ; "
                   "range_use = |x - mid| / half-range ; shift_req(group) = (x_t - x_cg) M / m_group ; "
                   "trim(pack m) = slide that brings x_cg(m) into range",
          inputs={"items": P + ITEMS_KEY, "mga": "ASM-A3-MGA", "x_rng": P + "cg.x_range_m", "z_rng": P + "cg.z_range_m",
                  "x_t": P + "cg.x_target_m", "z_m": P + "propulsion.stations.z_m", "c": P + "wing.chord_m",
                  "te": P + "wing.te_x_m", "pack": P + "battery.size_m", "slide": "ASM-A3-PACK-SLIDE",
                  "foot": P + "cg.foot_height_m", "pack_rng": "ASM-A3-PACK-RANGE", "pod_le": P + "pod.x_le_m",
                  "nose": "ASM-A3-NOSE-STACK", "y_max": P + "requirements.cg_lateral_max_m"},
          units={"x_rng": "m", "z_rng": "m", "x_t": "m", "z_m": "m", "c": "m", "te": "m", "pack": "m", "slide": "m",
                 "foot": "m", "pack_rng": "g", "pod_le": "m", "nose": "m", "y_max": "m"})
def cg_cases(items, mga, x_rng, z_rng, x_t, z_m, c, te, pack, slide, foot, pack_rng, pod_le, nose, y_max):
    rows = _rows(items)
    packs = [r for r in rows if r["discipline"] == "energy"]
    m, cg = _cg(rows)
    _, cg_pred = _cg(rows, lambda r: r["mass_g"] * (1 + _growth(r, mga)))
    mp = sum(r["mass_g"] for r in packs)
    xp = sum(r["mass_g"] * r["x"] for r in packs) / mp
    m_e, cg_e = _cg([r for r in rows if r["discipline"] != "energy"])
    x_req = (x_t * m - (m * cg[0] - mp * xp)) / mp
    x_fwd_lim = pod_le + nose + pack[0] / 2                  # most forward pack centroid the crush stack allows
    sl = [max(slide[0], x_fwd_lim - xp), slide[1]]            # travel from nominal, clamped by the crush stack
    trim = [(m * cg[0] + mp * d) / m for d in sl]

    def x_for_pack(mass, d=0.0):                              # pack of this mass at nominal + d
        return (m * cg[0] - mp * xp + mass * (xp + d)) / (m - mp + mass)

    def trim_for(mass):                                       # smallest aft slide that reaches the forward limit
        if x_for_pack(mass) >= x_rng[0]:
            return 0.0
        return (x_rng[0] * (m - mp + mass) - (m * cg[0] - mp * xp)) / mass - xp
    zc = cg[2]
    grp = [r for r in rows if r["subsystem"] in ("pod", "power", "avionics")]
    m_grp = sum(r["mass_g"] for r in grp)
    fwd = [r for r in rows if r["subsystem"] == "propulsion"]   # the four motor stations
    m_fwd = sum(r["mass_g"] for r in fwd)
    packs_cases = {}
    for mass in (pack_rng[0], mp, pack_rng[1]):
        d = trim_for(mass)
        packs_cases[f"{mass:.0f}"] = {"x_cg_nominal_m": x_for_pack(mass), "trim_aft_m": d,
                                      "x_cg_trimmed_m": x_for_pack(mass, d),
                                      "trim_ok": sl[0] <= d <= sl[1] and x_for_pack(mass, d) <= x_rng[1]}
    for mass, v in zip((pack_rng[0], mp, pack_rng[1]), packs_cases.values()):
        if v["x_cg_nominal_m"] > x_rng[1]:                    # aft of the range: a forward slide is needed
            v["trim_aft_m"] = (x_rng[1] * (m - mp + mass) - (m * cg[0] - mp * xp)) / mass - xp
            v["x_cg_trimmed_m"] = x_for_pack(mass, v["trim_aft_m"])
            v["trim_ok"] = sl[0] <= v["trim_aft_m"]

    # slide needed beyond the travel the bay gives (0 = every listed pack can be trimmed into the range)
    trim_short = max(max(0.0, v["trim_aft_m"] - sl[1], sl[0] - v["trim_aft_m"]) for v in packs_cases.values())
    return {"mass_g": m, "cg_m": cg, "cg_pred_m": cg_pred, "cg_x_frac_chord": cg[0] / c,
            "cg_x_range_use": abs(cg[0] - (x_rng[0] + x_rng[1]) / 2) / ((x_rng[1] - x_rng[0]) / 2),
            "cg_z_range_use": abs(zc - (z_rng[0] + z_rng[1]) / 2) / ((z_rng[1] - z_rng[0]) / 2),
            "pod_group_shift_req_m": (x_t - cg[0]) * m / m_grp, "pod_group_mass_g": m_grp,
            "stations_shift_req_m": (x_t - cg[0]) * m / m_fwd, "stations_mass_g": m_fwd,
            "dxcg_dx": {"pack": mp / m, "pod_group": m_grp / m, "stations": m_fwd / m},

            "cg_empty_m": cg_e, "empty_mass_g": m_e, "pack_x_m": xp, "pack_mass_g": mp,
            "pack_x_req_m": x_req, "pack_shift_req_m": x_req - xp,
            "pack_aft_room_m": te - (x_req + pack[0] / 2),           # >= 0: the pack still ends ahead of the TE
            "pack_fwd_room_m": (xp - pack[0] / 2) - pod_le - nose,   # room left after the crush stack and nose wall
            "cg_x_trim_range_m": trim, "cg_x_pack_light_heavy_m": [x_for_pack(pack_rng[0]), x_for_pack(pack_rng[1])],
            "pack_cases": packs_cases, "pack_slide_eff_m": sl, "pack_trim_shortfall_m": trim_short, "pack_x_fwd_limit_m": x_fwd_lim,
            "cg_y_use": abs(cg[1]) / y_max,
            "hover_split": (z_m + zc) / (z_m - zc), "stance_cg_height_m": c - cg[0] + foot}


@kit.calc("CALC-A3-INERTIA", title="Inertia tensor about the CG (aircraft frame)",
          equation="I = sum m_i (|r_i|^2 E - r_i r_i^T) + box self-inertia m/12 (b^2 + c^2) ; r_i from the CG",
          inputs={"items": P + ITEMS_KEY})
def inertia(items):
    rows = _rows(items)
    m, cg = _cg(rows)
    I = [[0.0] * 3 for _ in range(3)]
    for r in rows:
        mk = r["mass_g"] / 1000
        d = [r["x"] - cg[0], r["y"] - cg[1], r["z"] - cg[2]]
        L = [r["lx"], r["ly"], r["lz"]]
        for i in range(3):
            for j in range(3):
                I[i][j] += mk * ((d[0] ** 2 + d[1] ** 2 + d[2] ** 2) * (i == j) - d[i] * d[j])
            a, b = [k for k in range(3) if k != i]
            I[i][i] += mk * (L[a] ** 2 + L[b] ** 2) / 12
    mk = m / 1000
    return {"Ixx": I[0][0], "Iyy": I[1][1], "Izz": I[2][2], "Ixy": -I[0][1], "Ixz": -I[0][2], "Iyz": -I[1][2],
            "k_m": [math.sqrt(I[i][i] / mk) for i in range(3)]}


# ------------------------------------------------------------------ claims
kit.claim("CL-A3-MASS-BASIC", "Take-off mass, basic estimate (no growth)", calc="CALC-A3-MASS", output="basic_kg",
          unit="kg", limit=("<=", P + "requirements.mtow_gate_kg"), verifies=["R-MASS-GATE"],
          how="Re-run mass_rollup.py on the parts.csv files; weigh the assembled aircraft with pack (T-A1-WEIGH).")
kit.claim("CL-A3-MASS-PREDICTED", "Take-off mass, predicted (basic + growth by maturity)", calc="CALC-A3-MASS",
          output="predicted_kg", unit="kg", limit=("<=", P + "requirements.mtow_gate_kg"), verifies=["R-MASS-GATE"],
          how="Same roll-up; growth shrinks as items move EST -> CAD -> WEIGHED. Weigh every bought part on arrival.")
kit.claim("CL-A3-GATE-MARGIN", "Gate margin after growth covers the first-build overrun (550 g pack as carried)",
          calc="CALC-A3-MASS", output="gate_margin_kg", unit="kg", limit=(">=", P + "requirements.build_overrun_kg"),
          verifies=["R-MASS-GATE"],
          how="2.6 kg minus the predicted mass must stay >= the 0.10 kg first-build overrun; weigh the pack, the first "
              "core and fin (T-A3-WEIGH-PARTS).")
kit.claim("CL-A3-GATE-MARGIN-680", "Gate margin after growth with the heaviest listed pack (680 g)",
          calc="CALC-A3-MASS", output="gate_margin_pack_heavy_kg", unit="kg",
          limit=(">=", P + "requirements.build_overrun_kg"), verifies=["R-MASS-GATE", "R-PACK-MASS"],
          how="Same roll-up with the pack line at 680 g; settled by weighing the first pack (E2, ~1 Dec).")
kit.claim("CL-A3-GATE-MARGIN-503", "Gate margin after growth with the lightest listed pack (503 g)",
          calc="CALC-A3-MASS", output="gate_margin_pack_light_kg", unit="kg",
          limit=(">=", P + "requirements.build_overrun_kg"), verifies=["R-MASS-GATE"],
          how="Same roll-up with the pack line at 503 g.")
kit.claim("CL-A3-ALLOC-WORST", "Worst subsystem basic mass / its A1 allocation", calc="CALC-A3-MASS",
          output="worst_alloc_ratio", unit="-", limit=("<=", 1.0), verifies=["R-MASS-ALLOC"],
          how="ROLLUP.md subsystem table; A1 re-allocates through CR-A3-01.")
kit.claim("CL-A3-CG-X", "CG x at take-off, current layout", calc="CALC-A3-CG", output="cg_x_frac_chord", unit="-",
          how="Balance on two knife edges under the spar line (T-A3-CG-BALANCE).")
kit.claim("CL-A3-CG-X-RANGE", "CG x position in the allowable range, |x - mid| / half-range",
          calc="CALC-A3-CG", output="cg_x_range_use", unit="-", limit=("<=", 1.0), verifies=["R-CG-RANGE"],
          how="CG balance with pack at its station; B3 confirms the range from AVL.")
kit.claim("CL-A3-PACK-X-REQ", "Pack centroid station that puts the CG on target", calc="CALC-A3-CG",
          output="pack_x_req_m", unit="m",
          how="Strap the pack at this x and balance (T-A3-CG-BALANCE); D2 places the pod around it.")
kit.claim("CL-A3-PACK-AFT-ROOM", "Pack at the required station still ends ahead of the TE", calc="CALC-A3-CG",
          output="pack_aft_room_m", unit="m", limit=(">=", 0.0),
          how="D2 pod drawing: pack aft face x <= wing TE.")
kit.claim("CL-A3-PACK-FWD-ROOM", "Forward pack travel left at the nominal station after the nose block, stop and crush stack",
          calc="CALC-A3-CG", output="pack_fwd_room_m", unit="m", limit=(">=", 0.0),
          how="D2 pod drawing: crush block, spreader and nose wall fit between the pod nose and the pack fore face.")
kit.claim("CL-A3-PACK-TRIM", "Pack slide the 503-680 g listings need beyond the bay's trim travel",
          calc="CALC-A3-CG", output="pack_trim_shortfall_m", unit="m", limit=("<=", 0.0), verifies=["R-CG-RANGE"],
          how="Balance with the first pack (T-A3-CG-BALANCE); fit spacers POD-008 until the CG is inside the range.")
kit.claim("CL-A3-CG-Y", "Lateral CG offset / allowed lateral offset", calc="CALC-A3-CG", output="cg_y_use", unit="-",
          limit=("<=", 1.0), verifies=["R-CG-RANGE"],
          how="Balance on a knife edge along the x axis (T-A3-CG-BALANCE); P4 trim ballast inside the gate if needed.")
kit.claim("CL-A3-CG-Z-RANGE", "CG z position in the allowable range, |z - mid| / half-range",
          calc="CALC-A3-CG", output="cg_z_range_use", unit="-", limit=("<=", 1.0), verifies=["R-CG-RANGE"],
          how="Balance the aircraft on its side (z axis vertical) on a knife edge.")
kit.claim("CL-A3-HOVER-SPLIT", "Hover pitch-trim thrust split upper/lower", calc="CALC-A3-CG", output="hover_split",
          unit="-", limit=("<=", P + "requirements.hover_split_max"), verifies=["R-HOVER-SPLIT"],
          how="Tethered hover log: mean upper vs lower motor outputs (F4/H2).")
kit.claim("CL-A3-IXX", "Roll inertia about the CG (cruise x)", calc="CALC-A3-INERTIA", output="Ixx", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")
kit.claim("CL-A3-IYY", "Pitch inertia about the CG (cruise y)", calc="CALC-A3-INERTIA", output="Iyy", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")
kit.claim("CL-A3-IZZ", "Yaw inertia about the CG (cruise z)", calc="CALC-A3-INERTIA", output="Izz", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")

kit.test("T-A3-WEIGH-PARTS", "Weigh every bought part and the first core and fin",
         verifies=["CL-A3-MASS-PREDICTED", "CL-A3-GATE-MARGIN", "CL-A3-GATE-MARGIN-680",
                   "CL-A3-GATE-MARGIN-503"], state="planned",
         procedure="1 g kitchen scale; record in the owner's interfaces.json status VERIFIED and mass_g; pack first.")
kit.test("T-A3-CG-BALANCE", "CG balance", verifies=["CL-A3-CG-X-RANGE", "CL-A3-PACK-X-REQ", "CL-A3-CG-Z-RANGE",
                                                    "CL-A3-PACK-TRIM", "CL-A3-CG-Y"],
         state="planned", procedure="Two knife edges (or two scales) under the wing at known x; ready to fly, props on.")
kit.test("T-A3-SWING", "Bifilar pendulum inertia", verifies=["CL-A3-IXX", "CL-A3-IYY", "CL-A3-IZZ"], state="planned",
         procedure="Two 1.5 m strings, 0.30 m apart, about each axis; I = m g d^2 T^2 / (16 pi^2 L).")


# ------------------------------------------------------------------ gathering the items (not a calc: reads files)
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def evaluate(expr, params, used):
    """'=P:a.b*2-P:c[0]' -> number. Only + - * / ** ( ) [i] and P:keys; records the keys used."""
    src, names = expr.lstrip("="), {}
    out, i = [], 0
    while i < len(src):
        if src.startswith("P:", i):
            j = i + 2
            while j < len(src) and (src[j].isalnum() or src[j] in "._"):
                j += 1
            key = "P:" + src[i + 2:j].rstrip(".")
            name = f"_p{len(names)}"
            names[name] = key
            out.append(name)
            i = j
        else:
            out.append(src[i])
            i += 1

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and n.id in names:
            key = names[n.id]
            if key not in params:
                raise SystemExit(f"unknown parameter {key} in {expr}")
            used.add(key)
            return params[key]["value"]
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Subscript):
            return ev(n.value)[ev(n.slice)]
        raise SystemExit(f"unsupported expression {expr}")
    return float(ev(ast.parse("".join(out), mode="eval")))


def num(cell, params, used):
    cell = (cell or "").strip()
    if cell.startswith("="):
        return evaluate(cell, params, used)
    return float(cell) if cell else 0.0


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]


def instances(sym, x, y, z):
    return {"-": [(x, y, z)], "y": [(x, y, z), (x, -y, z)], "z": [(x, y, z), (x, y, -z)],
            "yz": [(x, y, z), (x, -y, z), (x, y, -z), (x, -y, -z)]}[sym or "-"]


def model_rows(path, params, used, source):
    """mass_model.csv / mass_estimate.csv -> {item_id: {"rows": [instance rows], "part_ids": [...], "adder": bool}}.

    Optional columns: part_ids (';'-separated parts.csv ids that take their positions from this row's instances
    when interfaces.json gives none) and with_parts ('y': an A3 adder kept beside the designer's parts.csv for an
    item the designer's list does not carry yet; dropped automatically once parts.csv lists the same id)."""
    out = {}
    for r in read_csv(path):
        q, sym = int(float(r["qty"])), (r.get("sym") or "-").strip()
        pos = instances(sym, *(num(r[k], params, used) for k in ("x_m", "y_m", "z_m")))
        if q % len(pos):
            raise SystemExit(f"{path.name} {r['item_id']}: qty {q} is not a multiple of sym '{sym}'")
        m = num(r["mass_g"], params, used)
        dims = [num(r[k], params, used) for k in ("lx_m", "ly_m", "lz_m")]
        gp = (r.get("growth_pct") or "").strip()
        rows = []
        for p in pos:
            for _ in range(q // len(pos)):
                rows.append([r["item_id"], r["subsystem"], r["discipline"], round(m, 3),
                             *(round(v, 5) for v in p), *(round(v, 5) for v in dims),
                             r["maturity"].strip(), float(gp) if gp else None, source])
        out[r["item_id"]] = {"rows": rows, "part_ids": [x.strip() for x in (r.get("part_ids") or "").split(";")
                                                         if x.strip()],
                             "adder": (r.get("with_parts") or "").strip().lower() in ("y", "yes", "1")}
    return out


GROUND_WORDS = ("not flying", "ground spare", "not on the aircraft")


def read_overrides():
    """team/A3/overrides.csv: part_id -> {x_m, y_m, z_m (blank = keep), maturity (blank = keep), reason}."""
    f = HERE / "overrides.csv"
    out = {}
    if f.exists():
        for r in read_csv(f):
            out[r["part_id"].strip()] = {k: (r.get(k) or "").strip() for k in ("x_m", "y_m", "z_m", "maturity",
                                                                               "reason")}
    return out


def subsystem_parts(sub_dir, model_cg, model_pos, overrides, warn, log):
    """parts.csv (+ interfaces.json positions) -> instance rows, or None if there is no parts.csv.

    Position precedence: interfaces.json cg_xyz_m per instance; else the instances of the A3 model row whose
    part_ids names this part (repeated qty / n times); else the A3 model centroid of the subsystem (warned).
    Zero-mass lines (fasteners or consumables whose mass the designer put inside another part) carry no mass and
    need no position. Lines with no interface node whose notes say they do not fly are ground items."""
    pc = sub_dir / "parts.csv"
    if not pc.exists():
        return None
    sub = sub_dir.name
    iface = {}
    ij = sub_dir / "interfaces.json"
    if ij.exists():
        for p in json.loads(ij.read_text(encoding="utf-8")).get("parts", []):
            iface[p["id"]] = p
    rows, src = [], pk.repo_rel(pc)
    for r in read_csv(pc):
        pid = r.get("part_id", "").strip()
        if not pid:
            continue
        inst = [p for k, p in iface.items() if k == pid or k.startswith(pid + "-")]
        if any(p.get("flight") is False for p in inst):
            continue
        text = " ".join((r.get(k) or "") for k in ("name", "notes", "vendor_or_file")).lower()
        if not inst and any(w in text for w in GROUND_WORDS):
            log["ground"].append(f"{pid} ({src}): {r.get('name', '').strip()}")
            continue
        try:
            q = int(float(r.get("qty") or 1))
        except ValueError:
            q = 1
        try:
            m = float(r.get("mass_g"))
        except (TypeError, ValueError):
            warn(f"{src} {pid}: no mass_g, counted as 0 g")
            m = 0.0
        if m == 0.0:
            log["zero_mass"].append(pid)
            continue
        if inst and all(p.get("mass_g") is not None for p in inst):
            itot = sum(float(p["mass_g"]) for p in inst)
            if abs(itot - q * m) > 0.5 + 0.01 * itot:
                hint = " (mass_g looks like a line total)" if abs(itot - m) < 0.5 and q > 1 else ""
                warn(f"{pid}: parts.csv {q} x {m:g} g = {q * m:g} g, interfaces.json {itot:g} g{hint}")
        cgs = [p["cg_xyz_m"] for p in inst if p.get("cg_xyz_m")]
        if len(cgs) == q:
            pos = cgs
        elif len(cgs) >= 1:
            warn(f"{pid}: {len(cgs)} positions for qty {q}; using their mean for all")
            pos = [[sum(c[i] for c in cgs) / len(cgs) for i in range(3)]] * q
        elif pid in model_pos and q % len(model_pos[pid][1]) == 0:
            iid, mp = model_pos[pid]
            pos = [p for p in mp for _ in range(q // len(mp))]
            log["positions_from_model"].append(f"{pid} <- {iid}")
        else:
            warn(f"{pid}: no cg_xyz_m in interfaces.json and no A3 model row maps it; using the A3 model centroid "
                 f"of '{sub}'")
            pos = [model_cg.get(sub, [0.0, 0.0, 0.0])] * q
        status = (inst[0].get("status") if inst else "PROPOSED") or "PROPOSED"
        mat = STATUS_MAT.get(status) or ("DATASHEET" if (r.get("make_or_buy") or "").strip() == "buy" else "EST")
        ov = overrides.get(pid)
        if ov:
            pos = [[float(ov[k]) if ov[k] else p[i] for i, k in enumerate(("x_m", "y_m", "z_m"))] for p in pos]
            mat = ov["maturity"] or mat
            log["overrides"].append(f"{pid}: {ov['reason']}")
        disc = "energy" if sub == "power" and "LiPo" in (r.get("material") or "") + (r.get("name") or "") \
            else PREFIX_DISC.get(pid[:3], "structure")
        for p in pos:
            rows.append([pid, sub, disc, round(m, 3), *(round(v, 5) for v in p), 0.0, 0.0, 0.0, mat, None, src])
    return rows


def budget_check(params, warn):
    """params.json#mass.allocation_g must equal A1's params/mass_budget.json (the published budget)."""
    f = RED / "params" / "mass_budget.json"
    if not f.exists():
        warn("params/mass_budget.json missing: allocations read from params.json only")
        return None
    b = json.loads(f.read_text(encoding="utf-8"))
    for k in SUBSYSTEMS:
        pv = params.get(f"P:mass.allocation_g.{k}", {}).get("value")
        if pv != b["allocations_g"].get(k):
            warn(f"allocation {k}: params.json {pv} g, mass_budget.json {b['allocations_g'].get(k)} g")
    if params["P:mass.growth_reserve_g"]["value"] != b["growth_reserve_g"]:
        warn("growth reserve differs between params.json and mass_budget.json")
    if abs(params["P:requirements.mtow_gate_kg"]["value"] * 1000 - b["limit_g"]) > 0.5:
        warn("gate differs between params.json and mass_budget.json")
    return {"allocations_g": b["allocations_g"], "growth_reserve_g": b["growth_reserve_g"], "limit_g": b["limit_g"]}


def gather(params):
    """All flying items, one row per instance, plus a log of what came from where."""
    used = set()
    log = {"warnings": [], "sources": {}, "ground": [], "zero_mass": [], "positions_from_model": [],
           "overrides": [], "adders": []}
    warn = log["warnings"].append
    log["budget"] = budget_check(params, warn)
    model = model_rows(HERE / "mass_model.csv", params, used, pk.repo_rel(HERE / "mass_model.csv"))
    for est in sorted(RED.glob("team/*/mass_estimate.csv")):
        if est.parent.name == "A3":
            continue
        for iid, it in model_rows(est, params, used, pk.repo_rel(est)).items():
            if iid in model:
                warn(f"{iid}: A3 model row replaced by {pk.repo_rel(est)}")
            model[iid] = it
    flat = [r for it in model.values() if not it["adder"] for r in it["rows"]]
    model_cg = {}
    for s in {r[1] for r in flat}:
        rs = [r for r in flat if r[1] == s]
        mm = sum(r[3] for r in rs)
        model_cg[s] = [sum(r[3] * r[4 + i] for r in rs) / mm for i in range(3)]
    model_pos = {pid: (iid, [r[4:7] for r in it["rows"]]) for iid, it in model.items() for pid in it["part_ids"]}
    overrides = read_overrides()
    items = []
    subs_dirs = sorted(d for d in (RED / "subsystems").glob("*") if d.is_dir()) if (RED / "subsystems").exists() else []
    from_parts, part_ids = set(), set()
    for d in subs_dirs:
        if d.name in GROUND:
            continue
        rows = subsystem_parts(d, model_cg, model_pos, overrides, warn, log)
        if rows is None:
            continue
        from_parts.add(d.name)
        part_ids |= {r[0] for r in rows}
        est_g = sum(r[3] for r in flat if r[1] == d.name)
        got_g = sum(r[3] for r in rows)
        if got_g < 0.9 * est_g:
            warn(f"{d.name}: parts.csv totals {got_g:.0f} g, A3 estimate {est_g:.0f} g: missing parts or masses?")
        items += rows
    for iid, it in model.items():
        if not it["adder"] or not it["rows"]:
            continue
        sub = it["rows"][0][1]
        if sub not in from_parts:
            items += it["rows"]                       # no parts.csv yet: an adder is an ordinary model row
        elif iid in part_ids:
            warn(f"{iid}: A3 adder dropped, {sub}/parts.csv now lists it")
        else:
            items += it["rows"]
            log["adders"].append(f"{iid} ({sub}, {sum(r[3] for r in it['rows']):.1f} g)")
    items += [r for r in flat if r[1] not in from_parts]
    for s in sorted({r[1] for r in items}, key=lambda s: SUBSYSTEMS.index(s) if s in SUBSYSTEMS else 99):
        log["sources"][s] = ", ".join(sorted({r[12] for r in items if r[1] == s}))
    items.sort(key=lambda r: (SUBSYSTEMS.index(r[1]) if r[1] in SUBSYSTEMS else 99, r[0]))
    log["params_used"] = sorted(used)
    return items, log


def items_doc(items, log):
    srcs = sorted({r[12] for r in items})
    return {"_note": "GENERATED by redesign/team/A3/mass_rollup.py; do not edit. One row per physical instance: "
                     + ", ".join(COLS) + " (g, m, aircraft frame). Re-run the script after any parts.csv, "
                     "mass_estimate.csv, mass_model.csv or params.json change.",
            "a3": {"rollup": {"items": {"value": items, "unit": "-", "source": "; ".join(srcs),
                                        "status": "CHECKED" if all(r[10] == "WEIGHED" for r in items) else "UNVERIFIED",
                                        "note": "params used: " + ", ".join(log["params_used"])}}}}


# ------------------------------------------------------------------ reports
def fmt_g(v):
    return f"{v:,.0f}".replace(",", " ")


def report(kit, items, log):
    M = kit.nodes["CALC-A3-MASS"]["outputs"]
    C = kit.nodes["CALC-A3-CG"]["outputs"]
    I = kit.nodes["CALC-A3-INERTIA"]["outputs"]
    gate = kit.value(P + "requirements.mtow_gate_kg") * 1000
    xr, zr, xt = kit.value(P + "cg.x_range_m"), kit.value(P + "cg.z_range_m"), kit.value(P + "cg.x_target_m")
    c = kit.value(P + "wing.chord_m")
    ok = lambda v: "`CHECKED`" if v else "`FAIL`"  # noqa: E731
    L = ["<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->", "",
         "### Live roll-up", "",
         f"Sources: {'; '.join(f'`{s}` ← {v}' for s, v in log['sources'].items())}.", "",
         "| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |",
         "|---|---|---|---|---|---|"]
    for name, alloc, basic, pred in M["by_subsystem_g"]:
        L.append(f"| {name} | {fmt_g(alloc)} | {fmt_g(basic)} | {fmt_g(pred)} | {basic - alloc:+.0f} | "
                 f"{'`PROPOSED`' if basic <= alloc else '`FAIL`'} |")
    L += [f"| **total** | **{fmt_g(gate)}** | **{fmt_g(M['basic_kg'] * 1000)}** | "
          f"**{fmt_g(M['predicted_kg'] * 1000)}** | allocated {fmt_g(M['allocated_g'])} + growth "
          f"{fmt_g(M['a1_sized_kg'] * 1000 - M['allocated_g'])} | gate margin "
          f"{M['gate_margin_kg'] * 1000:+.0f} g |", "",
          "| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | "
          "Overrun to cover g | Claim | Status |", "|---|---|---|---|---|---|---|"]
    ovr = kit.value(P + "requirements.build_overrun_kg") * 1000
    for lbl, pg, pr, mg, cl in (
            ("lightest listing", kit.value("ASM-A3-PACK-RANGE")[0], M["predicted_pack_light_kg"],
             M["gate_margin_pack_light_kg"], "CL-A3-GATE-MARGIN-503"),
            ("as carried (`battery.mass_kg`)", M["pack_carried_g"], M["predicted_kg"], M["gate_margin_kg"],
             "CL-A3-GATE-MARGIN"),
            ("heaviest listing", kit.value("ASM-A3-PACK-RANGE")[1], M["predicted_pack_heavy_kg"],
             M["gate_margin_pack_heavy_kg"], "CL-A3-GATE-MARGIN-680")):
        L.append(f"| {lbl} | {pg:.0f} | {fmt_g(pr * 1000)} | {mg * 1000:+.0f} | {ovr:.0f} | `{cl}` | "
                 f"{'`MODELLED`' if mg * 1000 >= ovr else '`FAIL`'} |")
    L += ["", "| Discipline | Basic g | Predicted g | Share |", "|---|---|---|---|"]
    for name, basic, pred in M["by_discipline_g"]:
        L.append(f"| {name} | {fmt_g(basic)} | {fmt_g(pred)} | {basic / (M['basic_kg'] * 10):.0f} % |")
    cg, cgp, cge = C["cg_m"], C["cg_pred_m"], C["cg_empty_m"]
    L += ["", "| CG case | x m (% chord) | y m | z m | Status |", "|---|---|---|---|---|",
          f"| Allowable (A1/B3) | {xr[0]:.3f}–{xr[1]:.3f} ({xr[0] / c:.0%}–{xr[1] / c:.0%}) | ±0.005 | "
          f"{zr[0]:+.3f}…{zr[1]:+.3f} | `PROPOSED` |",
          f"| Take-off, basic | {cg[0]:.3f} ({cg[0] / c:.1%}) | {cg[1]:+.4f} | {cg[2]:+.3f} | "
          f"{ok(C['cg_x_range_use'] <= 1 and C['cg_z_range_use'] <= 1)} |",
          f"| Take-off, predicted (growth pro rata) | {cgp[0]:.3f} ({cgp[0] / c:.1%}) | {cgp[1]:+.4f} | {cgp[2]:+.3f} | "
          f"{ok(xr[0] <= cgp[0] <= xr[1])} |",
          f"| Pack slid {C['pack_slide_eff_m'][0] * 1000:+.1f} … "
          f"{C['pack_slide_eff_m'][1] * 1000:+.1f} mm (spacers, crush stack) | {C['cg_x_trim_range_m'][0]:.4f} … "
          f"{C['cg_x_trim_range_m'][1]:.4f} | | | — |",
          *[f"| Pack {k} g: nominal station → slid {v['trim_aft_m'] * 1000:+.1f} mm (+ aft) | "
            f"{v['x_cg_nominal_m']:.4f} → {v['x_cg_trimmed_m']:.4f} | | | {ok(v['trim_ok'])} |"
            for k, v in C["pack_cases"].items()],
          f"| No pack (handling) | {cge[0]:.3f} ({cge[0] / c:.1%}) | {cge[1]:+.4f} | {cge[2]:+.3f} | — |", "",
          "| CG result | Value | Unit | Source |", "|---|---|---|---|",
          f"| Pack centroid now / needed for x = {xt:.3f} m | {C['pack_x_m']:.3f} / {C['pack_x_req_m']:.3f} | m | "
          f"`CL-A3-PACK-X-REQ` |",
          f"| Pack shift still needed for the target (+ aft) | {round(C['pack_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| or the whole pod group ({C['pod_group_mass_g']:.0f} g: pod, power, avionics) by | "
          f"{round(C['pod_group_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| or the four motor stations (propulsion, {C['stations_mass_g']:.0f} g) by | "
          f"{round(C['stations_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| Pack aft face to wing TE at that station | {C['pack_aft_room_m'] * 1000:.0f} | mm | `CL-A3-PACK-AFT-ROOM` |",
          f"| CG shift per mm moved: pack / pod group / stations | {C['dxcg_dx']['pack']:.2f} / "
          f"{C['dxcg_dx']['pod_group']:.2f} / {C['dxcg_dx']['stations']:.2f} | mm/mm | `CALC-A3-CG` |",
          f"| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | {C['pack_fwd_room_m'] * 1000:.0f} | mm | "
          f"`CL-A3-PACK-FWD-ROOM` |",
          f"| Hover trim split upper/lower pair (limit {kit.value('P:requirements.hover_split_max'):.2f}, D-18) | "
          f"{C['hover_split']:.3f} | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |",
          f"| Pack slide needed for 503–680 g beyond the trim travel | {C['pack_trim_shortfall_m'] * 1000:.1f} | mm | "
          f"`CL-A3-PACK-TRIM` |",
          f"| Most forward pack centroid the nose stack allows | {C['pack_x_fwd_limit_m']:.4f} | m | `CALC-A3-CG` |",
          f"| Lateral CG offset / allowed {kit.value(P + 'requirements.cg_lateral_max_m') * 1000:.0f} mm | "
          f"{C['cg_y_use']:.2f} ({cg[1] * 1000:+.1f} mm) | — | `CL-A3-CG-Y` |",
          f"| CG height above the feet in the stance | {C['stance_cg_height_m']:.3f} | m | `CALC-A3-CG` |", "",
          "| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |",
          "|---|---|---|---|---|---|",
          f"| Basic, take-off | {I['Ixx']:.4f} | {I['Iyy']:.4f} | {I['Izz']:.4f} | {I['Ixz']:+.4f} | kg·m² |",
          f"| Radius of gyration | {I['k_m'][0]:.3f} | {I['k_m'][1]:.3f} | {I['k_m'][2]:.3f} | | m |", ""]
    if log.get("budget"):
        b = log["budget"]
        L += [f"Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` "
              f"({fmt_g(sum(b['allocations_g'].values()))} g + reserve {b['growth_reserve_g']} g = "
              f"{fmt_g(b['limit_g'])} g).", ""]
    for key, head in (("adders", "A3 adders kept beside a designer's parts.csv (items the list does not carry yet)"),
                      ("overrides", "A3 position / maturity overrides (`team/A3/overrides.csv`)"),
                      ("positions_from_model", "Positions taken from the A3 model (no interfaces.json node)"),
                      ("ground", "Excluded as ground items (no interface node, notes say not flying)")):
        if log.get(key):
            L += [f"{head}: " + "; ".join(log[key]) + ".", ""]
    if log.get("zero_mass"):
        L += [f"Zero-mass lines (mass carried inside another part): {', '.join(log['zero_mass'])}.", ""]
    if log["warnings"]:
        L += ["Roll-up warnings:", ""] + [f"- {w}" for w in log["warnings"]] + [""]
    L += ["<!-- rollup:end -->"]
    block = "\n".join(L)

    # ROLLUP.md: every item
    R = ["# A3 live mass roll-up (generated)", "", f"Run `python -I redesign/team/A3/mass_rollup.py`. "
         f"{len(items)} instances, basic {M['basic_kg'] * 1000:.0f} g, predicted {M['predicted_kg'] * 1000:.0f} g, "
         f"gate {gate:.0f} g.", "", block.split("\n", 2)[2].replace("<!-- rollup:end -->", ""), "",
         "## Items (one row per instance)", "",
         "| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    mga = kit.value("ASM-A3-MGA")
    for r in _rows(items):
        R.append(f"| `{r['id']}` | {r['subsystem']} | {r['discipline']} | {r['mass_g']:.1f} | {r['x']:+.3f} | "
                 f"{r['y']:+.3f} | {r['z']:+.3f} | {r['maturity']} | {_growth(r, mga) * 100:.0f} | `{r['source']}` |")
    (HERE / "rollup" / "ROLLUP.md").write_text("\n".join(R) + "\n", encoding="utf-8")
    (HERE / "rollup" / "rollup.json").write_text(json.dumps(
        {"_note": "GENERATED by team/A3/mass_rollup.py", "mass": M, "cg": C, "inertia_kgm2": I,
         "sources": log["sources"], "log": log}, indent=1) + "\n", encoding="utf-8")

    doc = RED / "MASS-CG.md"
    if doc.exists():
        t = doc.read_text(encoding="utf-8")
        a, b = t.find("<!-- rollup:begin"), t.find("<!-- rollup:end -->")
        if a >= 0 and b > a:
            doc.write_text(t[:a] + block + t[b + len("<!-- rollup:end -->"):], encoding="utf-8")
    return M, C, I


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if rollup/mass_items.json is stale")
    a = ap.parse_args()
    params = kit._params
    items, log = gather(params)
    doc = items_doc(items, log)
    if a.check:
        old = json.loads(ITEMS_FILE.read_text(encoding="utf-8")) if ITEMS_FILE.exists() else None
        stale = old is None or old["a3"]["rollup"]["items"]["value"] != json.loads(json.dumps(items))
        print("mass roll-up is STALE: re-run mass_rollup.py" if stale else "mass roll-up is current")
        return 1 if stale else 0
    ITEMS_FILE.parent.mkdir(exist_ok=True)
    ITEMS_FILE.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    rel = "rollup/mass_items.json"
    kit.param_files.append(rel)
    kit._params.update(pk.load_params(HERE / rel))
    kit.write()
    M, C, I = report(kit, items, log)
    print(f"basic {M['basic_kg'] * 1000:.0f} g, predicted {M['predicted_kg'] * 1000:.0f} g, gate margin "
          f"{M['gate_margin_kg'] * 1000:+.0f} g (503 g pack {M['gate_margin_pack_light_kg'] * 1000:+.0f}, 680 g pack "
          f"{M['gate_margin_pack_heavy_kg'] * 1000:+.0f}); CG x {C['cg_m'][0]:.3f} m ({C['cg_x_frac_chord']:.1%} c), "
          f"z {C['cg_m'][2]:+.3f} m; pack needs x {C['pack_x_req_m']:.3f} m; "
          f"I = {I['Ixx']:.4f} / {I['Iyy']:.4f} / {I['Izz']:.4f} kg m2")
    for w in log["warnings"]:
        print("  warning:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
