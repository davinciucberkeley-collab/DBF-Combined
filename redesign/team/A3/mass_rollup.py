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
               "CAD 5 %, WEIGHED 1 %. An item may override (the pack carries 24 % to reach the 680 g listing).",
               basis="Maturity-based allowance after AIAA S-120A (mass properties control); percentages are A3's "
                     "choice for a student foam build, ESTIMATE", value={"EST": 20, "CALC": 10, "DATASHEET": 5,
                                                                         "CAD": 5, "WEIGHED": 1}, unit="%")
kit.assumption("ASM-A3-PACK-SLIDE", "Pack fore-aft trim travel", "The pack can be strapped anywhere within +/- this "
               "distance of its nominal station without re-building the pod",
               basis="params.json pod.x_le_m note: D2 provides +/-0.03 m", value=0.03, unit="m",
               cites=["SRC-K09-CARD"])
kit.assumption("ASM-A3-PACK-RANGE", "Pack mass range from listings", "Ovonic 4S 6500 listings give 503 to 680 g",
               basis="config-study/cards/K09/REVIEW.md section 2; weigh on arrival", value=[503.0, 680.0], unit="g",
               status="UNVERIFIED", cites=["SRC-K09-REVIEW", "SRC-OVONIC-4S6500"])


# ------------------------------------------------------------------ pure calculations (re-run by build_graph)
def _rows(items):
    return [dict(zip(COLS, r)) for r in items]


def _growth(r, mga):
    return (r["growth_pct"] if r["growth_pct"] is not None else mga[r["maturity"]]) / 100.0


@kit.calc("CALC-A3-MASS", title="Mass roll-up against allocations and the gate", assumes=["ASM-A3-MGA"],
          equation="basic = sum m_i ; predicted = sum m_i (1 + MGA_i) ; margin = gate - predicted ; "
                   "overrun_s = basic_s - alloc_s",
          inputs={"items": P + ITEMS_KEY, "mga": "ASM-A3-MGA", "gate_kg": P + "requirements.mtow_gate_kg",
                  **{k: f"{P}mass.allocation_g.{k}" for k in SUBSYSTEMS}, "growth_g": P + "mass.growth_reserve_g"},
          units={"gate_kg": "kg", **{k: "g" for k in SUBSYSTEMS}, "growth_g": "g"})
def mass_rollup(items, mga, gate_kg, growth_g, **alloc):
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
    return {"basic_kg": basic / 1000, "predicted_kg": pred / 1000, "mga_kg": (pred - basic) / 1000,
            "gate_margin_kg": gate_kg - pred / 1000, "allocated_g": float(sum(alloc.values())),
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
          assumes=["ASM-A3-MGA", "ASM-A3-PACK-SLIDE", "ASM-A3-PACK-RANGE"],
          equation="cg = sum m_i r_i / sum m_i ; x_pack_req = (x_t M - (M x_cg - m_p x_p)) / m_p ; "
                   "split = (z_m + z_cg) / (z_m - z_cg) ; h_stance = c - x_cg + foot ; "
                   "fwd_room = (x_pack - L_pack/2) - x_pod_le ; "
                   "range_use = |x - mid| / half-range ; shift_req(group) = (x_t - x_cg) M / m_group",
          inputs={"items": P + ITEMS_KEY, "mga": "ASM-A3-MGA", "x_rng": P + "cg.x_range_m", "z_rng": P + "cg.z_range_m",
                  "x_t": P + "cg.x_target_m", "z_m": P + "propulsion.stations.z_m", "c": P + "wing.chord_m",
                  "te": P + "wing.te_x_m", "pack": P + "battery.size_m", "slide": "ASM-A3-PACK-SLIDE",
                  "foot": P + "cg.foot_height_m", "pack_rng": "ASM-A3-PACK-RANGE", "pod_le": P + "pod.x_le_m"},
          units={"x_rng": "m", "z_rng": "m", "x_t": "m", "z_m": "m", "c": "m", "te": "m", "pack": "m", "slide": "m",
                 "foot": "m", "pack_rng": "g", "pod_le": "m"})
def cg_cases(items, mga, x_rng, z_rng, x_t, z_m, c, te, pack, slide, foot, pack_rng, pod_le):
    rows = _rows(items)
    packs = [r for r in rows if r["discipline"] == "energy"]
    m, cg = _cg(rows)
    _, cg_pred = _cg(rows, lambda r: r["mass_g"] * (1 + _growth(r, mga)))
    mp = sum(r["mass_g"] for r in packs)
    xp = sum(r["mass_g"] * r["x"] for r in packs) / mp
    m_e, cg_e = _cg([r for r in rows if r["discipline"] != "energy"])
    x_req = (x_t * m - (m * cg[0] - mp * xp)) / mp
    trim = [(m * cg[0] + mp * d) / m for d in (-slide, slide)]

    def x_for_pack(mass):                                     # pack mass changes at the same station
        return (m * cg[0] - mp * xp + mass * xp) / (m - mp + mass)
    zc = cg[2]
    grp = [r for r in rows if r["subsystem"] in ("pod", "power", "avionics")]
    m_grp = sum(r["mass_g"] for r in grp)
    fwd = [r for r in rows if r["x"] < 0 and r["subsystem"] in ("fins", "propulsion", "harness", "landing")]
    m_fwd = sum(r["mass_g"] for r in fwd)
    return {"mass_g": m, "cg_m": cg, "cg_pred_m": cg_pred, "cg_x_frac_chord": cg[0] / c,
            "cg_x_range_use": abs(cg[0] - (x_rng[0] + x_rng[1]) / 2) / ((x_rng[1] - x_rng[0]) / 2),
            "cg_z_range_use": abs(zc - (z_rng[0] + z_rng[1]) / 2) / ((z_rng[1] - z_rng[0]) / 2),
            "pod_group_shift_req_m": (x_t - cg[0]) * m / m_grp, "pod_group_mass_g": m_grp,
            "stations_shift_req_m": (x_t - cg[0]) * m / m_fwd, "stations_mass_g": m_fwd,
            "dxcg_dx": {"pack": mp / m, "pod_group": m_grp / m, "stations": m_fwd / m},

            "cg_empty_m": cg_e, "empty_mass_g": m_e, "pack_x_m": xp, "pack_mass_g": mp,
            "pack_x_req_m": x_req, "pack_shift_req_m": x_req - xp,
            "pack_aft_room_m": te - (x_req + pack[0] / 2),           # >= 0: the pack still ends ahead of the TE
            "pack_fwd_room_m": (xp - pack[0] / 2) - pod_le,          # pack fore face to pod nose (outside skin)
            "cg_x_trim_range_m": trim, "cg_x_pack_light_heavy_m": [x_for_pack(pack_rng[0]), x_for_pack(pack_rng[1])],
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
kit.claim("CL-A3-GATE-MARGIN", "Gate margin after growth covers the first-build overrun", calc="CALC-A3-MASS",
          output="gate_margin_kg", unit="kg", limit=(">=", P + "requirements.build_overrun_kg"),
          verifies=["R-MASS-GATE"],
          how="2.6 kg minus the predicted mass must stay >= the 0.10 kg first-build overrun; weigh the first core and fin.")
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
kit.claim("CL-A3-PACK-FWD-ROOM", "Pack fore face to pod nose at the nominal pack station (outside skin)",
          calc="CALC-A3-CG", output="pack_fwd_room_m", unit="m", limit=(">=", 0.0),
          how="D2 pod drawing: pack fore face behind the inside of the pod nose wall; lead exit at the aft end.")
kit.claim("CL-A3-CG-Z-RANGE", "CG z position in the allowable range, |z - mid| / half-range",
          calc="CALC-A3-CG", output="cg_z_range_use", unit="-", limit=("<=", 1.0), verifies=["R-CG-RANGE"],
          how="Balance the aircraft on its side (z axis vertical) on a knife edge.")
kit.claim("CL-A3-HOVER-SPLIT", "Hover pitch-trim thrust split upper/lower", calc="CALC-A3-CG", output="hover_split",
          unit="-", limit=("<=", P + "requirements.hover_split_max"),
          how="Tethered hover log: mean upper vs lower motor outputs (F4/H2).")
kit.claim("CL-A3-IXX", "Roll inertia about the CG (cruise x)", calc="CALC-A3-INERTIA", output="Ixx", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")
kit.claim("CL-A3-IYY", "Pitch inertia about the CG (cruise y)", calc="CALC-A3-INERTIA", output="Iyy", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")
kit.claim("CL-A3-IZZ", "Yaw inertia about the CG (cruise z)", calc="CALC-A3-INERTIA", output="Izz", unit="kg m2",
          how="Bifilar pendulum (T-A3-SWING).")

kit.test("T-A3-WEIGH-PARTS", "Weigh every bought part and the first core and fin",
         verifies=["CL-A3-MASS-PREDICTED", "CL-A3-GATE-MARGIN"], state="planned",
         procedure="1 g kitchen scale; record in the owner's interfaces.json status VERIFIED and mass_g; pack first.")
kit.test("T-A3-CG-BALANCE", "CG balance", verifies=["CL-A3-CG-X-RANGE", "CL-A3-PACK-X-REQ", "CL-A3-CG-Z-RANGE"],
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
    """mass_model.csv / mass_estimate.csv -> {item_id: [instance rows]}."""
    out = {}
    for r in read_csv(path):
        q, sym = int(float(r["qty"])), (r.get("sym") or "-").strip()
        pos = instances(sym, *(num(r[k], params, used) for k in ("x_m", "y_m", "z_m")))
        if q % len(pos):
            raise SystemExit(f"{path.name} {r['item_id']}: qty {q} is not a multiple of sym '{sym}'")
        m = num(r["mass_g"], params, used)
        dims = [num(r[k], params, used) for k in ("lx_m", "ly_m", "lz_m")]
        gp = r.get("growth_pct", "").strip()
        rows = []
        for p in pos:
            for _ in range(q // len(pos)):
                rows.append([r["item_id"], r["subsystem"], r["discipline"], round(m, 3),
                             *(round(v, 5) for v in p), *(round(v, 5) for v in dims),
                             r["maturity"].strip(), float(gp) if gp else None, source])
        out[r["item_id"]] = rows
    return out


def subsystem_parts(sub_dir, model_cg, warn):
    """parts.csv (+ interfaces.json positions) -> instance rows, or None if there is no parts.csv."""
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
        try:
            q = int(float(r.get("qty") or 1))
        except ValueError:
            q = 1
        try:
            m = float(r.get("mass_g"))
        except (TypeError, ValueError):
            warn(f"{src} {pid}: no mass_g, counted as 0 g")
            m = 0.0
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
        else:
            warn(f"{pid}: no cg_xyz_m in interfaces.json; using the A3 model centroid of '{sub}'")
            pos = [model_cg.get(sub, [0.0, 0.0, 0.0])] * q
        status = (inst[0].get("status") if inst else "PROPOSED") or "PROPOSED"
        mat = STATUS_MAT.get(status) or ("DATASHEET" if (r.get("make_or_buy") or "").strip() == "buy" else "EST")
        disc = "energy" if sub == "power" and "LiPo" in (r.get("material") or "") + (r.get("name") or "") \
            else PREFIX_DISC.get(pid[:3], "structure")
        for p in pos:
            rows.append([pid, sub, disc, round(m, 3), *(round(v, 5) for v in p), 0.0, 0.0, 0.0, mat, None, src])
    return rows


def gather(params):
    """All flying items, one row per instance, plus a log of what came from where."""
    used, log = set(), {"warnings": [], "sources": {}}
    warn = log["warnings"].append
    model = model_rows(HERE / "mass_model.csv", params, used, pk.repo_rel(HERE / "mass_model.csv"))
    for est in sorted(RED.glob("team/*/mass_estimate.csv")):
        if est.parent.name == "A3":
            continue
        for iid, rows in model_rows(est, params, used, pk.repo_rel(est)).items():
            if iid in model:
                warn(f"{iid}: A3 model row replaced by {pk.repo_rel(est)}")
            model[iid] = rows
    flat = [r for rows in model.values() for r in rows]
    model_cg = {}
    for s in {r[1] for r in flat}:
        rs = [r for r in flat if r[1] == s]
        mm = sum(r[3] for r in rs)
        model_cg[s] = [sum(r[3] * r[4 + i] for r in rs) / mm for i in range(3)]
    items = []
    subs_dirs = sorted(d for d in (RED / "subsystems").glob("*") if d.is_dir()) if (RED / "subsystems").exists() else []
    from_parts = set()
    for d in subs_dirs:
        if d.name in GROUND:
            continue
        rows = subsystem_parts(d, model_cg, warn)
        if rows is None:
            continue
        from_parts.add(d.name)
        est_g = sum(r[3] for r in flat if r[1] == d.name)
        got_g = sum(r[3] for r in rows)
        if got_g < 0.9 * est_g:
            warn(f"{d.name}: parts.csv totals {got_g:.0f} g, A3 estimate {est_g:.0f} g: missing parts or masses?")
        items += rows
    for s in sorted({r[1] for r in flat} | from_parts):
        log["sources"][s] = f"redesign/subsystems/{s}/parts.csv" if s in from_parts else \
            ", ".join(sorted({r[12] for r in flat if r[1] == s}))
    items += [r for r in flat if r[1] not in from_parts]
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
          "| Discipline | Basic g | Predicted g | Share |", "|---|---|---|---|"]
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
          f"| Pack slid ±{kit.value('ASM-A3-PACK-SLIDE'):.2f} m | {C['cg_x_trim_range_m'][0]:.3f} … "
          f"{C['cg_x_trim_range_m'][1]:.3f} | | | {ok(xr[0] <= C['cg_x_trim_range_m'][1])} |",
          f"| Pack 503 / 680 g at the same station | {C['cg_x_pack_light_heavy_m'][0]:.3f} / "
          f"{C['cg_x_pack_light_heavy_m'][1]:.3f} | | | `UNVERIFIED` |",
          f"| No pack (handling) | {cge[0]:.3f} ({cge[0] / c:.1%}) | {cge[1]:+.4f} | {cge[2]:+.3f} | — |", "",
          "| CG result | Value | Unit | Source |", "|---|---|---|---|",
          f"| Pack centroid now / needed for x = {xt:.3f} m | {C['pack_x_m']:.3f} / {C['pack_x_req_m']:.3f} | m | "
          f"`CL-A3-PACK-X-REQ` |",
          f"| Pack shift still needed for the target (+ aft) | {round(C['pack_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| or the whole pod group ({C['pod_group_mass_g']:.0f} g: pod, power, avionics) by | "
          f"{round(C['pod_group_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| or the motor stations (everything ahead of the LE, {C['stations_mass_g']:.0f} g) by | "
          f"{round(C['stations_shift_req_m'] * 1000) + 0:+d} | mm | `CALC-A3-CG` |",
          f"| Pack aft face to wing TE at that station | {C['pack_aft_room_m'] * 1000:.0f} | mm | `CL-A3-PACK-AFT-ROOM` |",
          f"| CG shift per mm moved: pack / pod group / stations | {C['dxcg_dx']['pack']:.2f} / "
          f"{C['dxcg_dx']['pod_group']:.2f} / {C['dxcg_dx']['stations']:.2f} | mm/mm | `CALC-A3-CG` |",
          f"| Pack fore face to pod nose (outside skin) at the nominal station | {C['pack_fwd_room_m'] * 1000:.0f} | mm | "
          f"`CL-A3-PACK-FWD-ROOM` |",
          f"| Hover trim split upper/lower pair (limit {kit.value('P:requirements.hover_split_max'):.2f}, D-18) | "
          f"{C['hover_split']:.3f} | — | `CL-A3-HOVER-SPLIT` |",
          f"| CG height above the feet in the stance | {C['stance_cg_height_m']:.3f} | m | `CALC-A3-CG` |", "",
          "| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |",
          "|---|---|---|---|---|---|",
          f"| Basic, take-off | {I['Ixx']:.4f} | {I['Iyy']:.4f} | {I['Izz']:.4f} | {I['Ixz']:+.4f} | kg·m² |",
          f"| Radius of gyration | {I['k_m'][0]:.3f} | {I['k_m'][1]:.3f} | {I['k_m'][2]:.3f} | | m |", ""]
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
         "sources": log["sources"], "warnings": log["warnings"]}, indent=1) + "\n", encoding="utf-8")

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
          f"{M['gate_margin_kg'] * 1000:+.0f} g; CG x {C['cg_m'][0]:.3f} m ({C['cg_x_frac_chord']:.1%} c), "
          f"z {C['cg_m'][2]:+.3f} m; pack needs x {C['pack_x_req_m']:.3f} m; "
          f"I = {I['Ixx']:.4f} / {I['Iyy']:.4f} / {I['Izz']:.4f} kg m2")
    for w in log["warnings"]:
        print("  warning:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
