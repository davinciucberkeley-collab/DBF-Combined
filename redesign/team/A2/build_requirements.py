"""build_requirements.py (A2, systems engineer): one inventory -> three outputs.

    python -I redesign/team/A2/build_requirements.py            # writes claims.json, rebuilds the proof graph,
                                                                 # writes REQUIREMENTS.md and VERIFICATION-MATRIX.md
    python -I redesign/team/A2/build_requirements.py --no-graph # skip build_graph.py (use the graph.json on disk)

Reads  team/A2/requirements.json   (A2's inventory: every requirement row, owner, method, evidence; retired limits)
       params/params.json          (every number: {P:dotted.key} in a row is replaced by the parameter's value)
       params/claims.json          (A1's shared R-... nodes: title and text are read from there, never copied)
       proofs/out/graph.json       (statuses computed by build_graph.py; rebuilt here unless --no-graph)
       team/*/claims.json, *.py    (scanned for scripts that still cite a retired ASM-A2-* id)
Writes team/A2/claims.json         (new R-... requirement nodes; alias nodes for retired limits still cited elsewhere)
       team/A2/REQUIREMENTS.md     (the requirement set, by group; the limits table read live from params.json)
       team/A2/VERIFICATION-MATRIX.md (requirement -> owner -> method -> evidence -> status)

Exit 1 when the inventory is inconsistent (duplicate id, unknown shared id, a P1-P25 line with no requirement,
a requirement in the graph that has no row here, a method letter outside A/I/T/D, a {P:key} or source key missing
from params.json, a row that still names a retired ASM-A2-* id) or when build_graph.py reports an error on an A2
node. Other roles' drift is printed and counted but does not fail A2's check. Standard library only.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
REPO = REDESIGN.parent
INVENTORY = HERE / "requirements.json"
PARAMS = REDESIGN / "params" / "params.json"
SHARED = REDESIGN / "params" / "claims.json"
GRAPH = REDESIGN / "proofs" / "out" / "graph.json"
BUILD_GRAPH = REDESIGN / "proofs" / "build_graph.py"
METHODS = {"A": "analysis", "I": "inspection", "T": "test", "D": "demonstration"}
RANK = {"UNVERIFIED": 0, "PROPOSED": 1, "CHECKED": 2, "VERIFIED": 3}
P_IDS = [f"P{i}" for i in range(1, 26)]
PLACEHOLDER = re.compile(r"\{P:([A-Za-z0-9_.]+)\}")
RETIRED_RE = re.compile(r"\bASM-A2-[A-Z0-9-]+\b")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


# ----------------------------------------------------------------------------- params
def flatten_params(d, prefix=""):
    """dotted key -> node. A dict with a 'value' key is a leaf; every container is also addressable."""
    out = {}
    for k, v in d.items():
        if k.startswith("_"):
            continue
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out[key] = v
            if "value" not in v:
                out.update(flatten_params(v, key + "."))
    return out


def fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        if float(v).is_integer():
            return str(int(v))
        return f"{v:.4g}"
    if isinstance(v, list):
        parts = [fmt(x) for x in v]
        return " x ".join(parts) if len(parts) == 3 else " to ".join(parts)
    return str(v)


def subst(s, params, errors, where):
    def one(m):
        key = m.group(1)
        node = params.get(key)
        if node is None or "value" not in node:
            errors.append(f"{where}: {{P:{key}}} is not a value in {rel(PARAMS)}")
            return f"{{P:{key}}}"
        return fmt(node["value"])
    return PLACEHOLDER.sub(one, s)


def source_keys(source):
    """'params.json#a.b, c, requirements.x; SRC-Y' -> ['a.b', 'a.c', 'requirements.x'] (bare tokens inherit the prefix)."""
    keys, prefix = [], None
    for tok in source.replace(";", ",").split(","):
        tok = tok.strip()
        if tok.startswith("params.json#"):
            tok = tok[len("params.json#"):]
        elif prefix is None or not re.fullmatch(r"[A-Za-z0-9_.]+", tok) or tok.startswith(("SRC-", "CL-", "ASM-", "R-")):
            prefix = None if not tok.startswith("params.json#") and "/" in tok else prefix
            continue
        tok = tok.split(" ")[0]
        if "." not in tok and prefix:
            tok = prefix + "." + tok
        keys.append(tok)
        prefix = tok.rsplit(".", 1)[0] if "." in tok else None
    return keys


# ----------------------------------------------------------------------------- validate
def validate(inv, shared, params):
    errors = []
    rows = inv["requirements"]
    ids = [r["id"] for r in rows]
    for i in ids:
        if ids.count(i) > 1:
            errors.append(f"duplicate row id {i}")
    shared_req = {n["id"]: n for n in shared["nodes"] if n["type"] == "requirement"}
    for r in rows:
        new = "text" in r
        if new and r["id"] in shared_req:
            errors.append(f"{r['id']}: has its own text but the id already exists in {rel(SHARED)} (duplicate)")
        if not new and r["id"] not in shared_req:
            errors.append(f"{r['id']}: no text here and not defined in {rel(SHARED)}")
        for m in r["method"].split("+"):
            if m not in METHODS:
                errors.append(f"{r['id']}: method {m!r} is not one of {sorted(METHODS)}")
        for k in ("group", "p", "owner", "evidence", "how", "value", "unit", "source"):
            if k not in r:
                errors.append(f"{r['id']}: missing field {k!r}")
        if r.get("group") not in inv["groups"]:
            errors.append(f"{r['id']}: unknown group {r.get('group')!r}")
        for k in ("text", "value", "how"):
            if k in r:
                if RETIRED_RE.search(r[k]):
                    errors.append(f"{r['id']}: {k} still names a retired ASM-A2-* id")
                subst(r[k], params, errors, f"{r['id']}.{k}")
        if RETIRED_RE.search(r["source"]):
            errors.append(f"{r['id']}: source still names a retired ASM-A2-* id; use params.json#requirements.<key>")
        for key in source_keys(r["source"]):
            if key not in params:
                errors.append(f"{r['id']}: source key {key!r} is not in {rel(PARAMS)}")
    for sid in shared_req:
        if sid not in ids:
            errors.append(f"{sid} is defined in {rel(SHARED)} but has no row in {rel(INVENTORY)}")
    covered = {p for r in rows for p in r["p"]}
    for p in P_IDS:
        if p not in covered:
            errors.append(f"{p} maps to no requirement")
    lim_ids = [l["id"] for l in inv["retired_limits"]]
    for i in lim_ids:
        if lim_ids.count(i) > 1:
            errors.append(f"duplicate retired limit id {i}")
    for l in inv["retired_limits"]:
        for key in [l["param"]] + l.get("also", []):
            if key not in params or "value" not in params[key]:
                errors.append(f"{l['id']}: adopted key {key!r} is not a value in {rel(PARAMS)} (D-14)")
    return errors, shared_req


# ----------------------------------------------------------------------------- external citations of retired ids
def node_refs(n):
    """Ids a proof node depends on: calc inputs, cites, assumes, limit.ref (a mention in free text does not count)."""
    refs = list((n.get("inputs") or {}).values()) + list(n.get("cites") or []) + list(n.get("assumes") or [])
    if (n.get("limit") or {}).get("ref"):
        refs.append(n["limit"]["ref"])
    return [r for r in refs if isinstance(r, str)]


def external_citations(inv):
    """retired id -> sorted repo-relative files (outside team/A2) whose proof nodes still depend on it.
    The claims.json is listed, plus the scripts beside it that name the id (where the fix goes)."""
    claim_files = [p for p in (REDESIGN / "team").glob("*/claims*.json") if p.parent.name != "A2"]
    claim_files += [p for p in (REDESIGN / "subsystems").rglob("claims*.json")]
    cited = {l["id"]: set() for l in inv["retired_limits"]}
    for f in claim_files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        hit = {r for n in doc.get("nodes", []) for r in node_refs(n) if r in cited}
        if not hit:
            continue
        scripts = [s for s in f.parent.glob("*.py")]
        for rid in hit:
            cited[rid].add(rel(f))
            for s in scripts:
                try:
                    if re.search(r"\b" + re.escape(rid) + r"\b", s.read_text(encoding="utf-8")):
                        cited[rid].add(rel(s))
                except (OSError, UnicodeDecodeError):
                    pass
    return {k: sorted(v) for k, v in cited.items()}


# ----------------------------------------------------------------------------- claims.json
def write_claims(inv, params, cited):
    nodes = []
    e = []
    for r in inv["requirements"]:
        if "text" not in r:
            continue
        nodes.append({"id": r["id"], "type": "requirement", "title": r["title"], "text": subst(r["text"], params, e, r["id"]),
                      "ref": r["ref"],
                      "note": f"{'/'.join(r['p'])}; owner {r['owner']}; method {r['method']}; see team/A2/REQUIREMENTS.md"})
    n_alias = 0
    for l in inv["retired_limits"]:
        who = cited.get(l["id"], [])
        if not who:
            continue
        p = params[l["param"]]
        nodes.append({"id": l["id"], "type": "assumption",
                      "title": f"RETIRED alias of P:{l['param']}",
                      "text": f"Retired {inv['date']} (CHANGE-LOG D-14): the limit lives in params.json#{l['param']}"
                              + (f" (and {', '.join(l['also'])})" if l.get("also") else "")
                              + ". This node only carries the parameter's value so the scripts that still cite it build; "
                              "they point at the P: id and A2 then deletes this node",
                      "basis": f"Value copied from params.json#{l['param']} by build_requirements.py at every run; cited by " + ", ".join(who),
                      "value": p["value"], "unit": p.get("unit", "-"), "status": "PROPOSED",
                      "cites": [f"P:{l['param']}"],
                      "note": "RETIRED; cite P:" + l["param"]})
        n_alias += 1
    doc = {"schema": "proofs/1",
           "generated_by": "redesign/team/A2/build_requirements.py from team/A2/requirements.json (do not edit by hand)",
           "nodes": nodes}
    (HERE / "claims.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(nodes) - n_alias, n_alias


# ----------------------------------------------------------------------------- graph
def graph_status(graph):
    """Per requirement: status, fails, claim ids, smallest margin, reasons."""
    nodes = {n["id"]: n for n in graph["nodes"]}
    out = {}
    for n in graph["nodes"]:
        if n["type"] != "requirement":
            continue
        claims = [nodes[e["source"]] for e in graph["edges"]
                  if e["type"] == "verifies" and e["target"] == n["id"] and nodes[e["source"]]["type"] == "claim"]
        margins = [c["margin"] for c in claims if c.get("margin") is not None]
        out[n["id"]] = {"status": n.get("status", "UNVERIFIED"), "fails": bool(n.get("fails")),
                        "claims": [c["id"] for c in claims], "margin": min(margins) if margins else None,
                        "reasons": n.get("reasons", [])}
    return out


# ----------------------------------------------------------------------------- markdown helpers
def esc(s):
    return str(s).replace("|", "\\|")


def status_cell(g):
    if g is None:
        return "`UNVERIFIED` (no graph)"
    s = f"`{g['status']}`"
    if g["fails"]:
        s += " `FAIL`"
    if not g["claims"]:
        s += " (no claim)"
    return s


def margin_cell(m):
    return "—" if m is None else f"{m * 100:+.0f} %"


# ----------------------------------------------------------------------------- REQUIREMENTS.md
def write_requirements(inv, shared_req, params, cited):
    rows = inv["requirements"]
    n_shared = sum(1 for r in rows if "text" not in r)
    n_new = len(rows) - n_shared
    e = []
    L = []
    L.append("# Requirements — K09-L quad tailsitter\n")
    L.append(f"Status: `PROPOSED` requirement set (A2, {inv['date']}, revision {inv.get('revision', '—')}), re-derived from "
             f"`config-study/REQUIREMENTS-PROPOSED.md` P1–P25 for the configuration in `CONFIGURATION.md`. {len(rows)} requirements: "
             f"{n_shared} shared ids from `params/claims.json` (A1) and {n_new} added in `team/A2/claims.json`. Every one has an owner, a "
             f"value with a source, and a verification method. Every number below is read from `params/params.json` at build time; "
             f"status per requirement: `VERIFICATION-MATRIX.md`. Generated by `team/A2/build_requirements.py` from "
             f"`team/A2/requirements.json` — edit the JSON, not this file.\n")
    L.append("## How to read\n")
    L.append("| Column | Meaning |\n|---|---|")
    L.append("| ID | Proof-chain requirement id. A claim closes it by naming it in `verifies`. |")
    L.append("| P | The P1–P25 line(s) of `REQUIREMENTS-PROPOSED.md` it comes from. |")
    L.append("| Value · Unit | What a claim is tested against; `—` for text requirements (closed by inspection or demonstration). |")
    L.append("| Source | The `params.json` key(s) that hold the number (`requirements.*` for limits, CHANGE-LOG D-14), or a decision file. |")
    L.append("| Owner · Method | Role that writes the claim; A analysis · I inspection · T test · D demonstration. Support roles: the matrix. |\n")
    L.append("## How a role closes a requirement\n")
    L.append("- Numeric: `kit.claim(..., limit=('<=', 'P:requirements.<key>'), verifies=['R-…'], how=…)` "
             "→ `CHECKED` when the calculation re-runs with checked inputs and the margin is ≥ 0. Never type the limit value.")
    L.append("- Tested: add `kit.test(..., verifies=['CL-…'], state='run', result='pass', measured=…, evidence=<file>)` → `VERIFIED`.")
    L.append("- Inspection or demonstration (text requirement): a claim with no calc (`value` 1, `unit` `-`, `status` `PROPOSED`) "
             "plus a test node whose `evidence` names the file in the matrix → `VERIFIED` when it has run and passed.")
    L.append("- Always give `how` and, for hardware, `parts` (ids from `interfaces.json`). Re-run your script after any parameter change.\n")
    for gkey, gname in inv["groups"].items():
        grows = [r for r in rows if r["group"] == gkey]
        if not grows:
            continue
        L.append(f"## {gname}\n")
        L.append("| ID | P | Requirement | Value | Unit | Source | Owner | Method |\n|---|---|---|---|---|---|---|---|")
        for r in grows:
            if "text" in r:
                title, text = r["title"], subst(r["text"], params, e, r["id"])
            else:
                title, text = shared_req[r["id"]]["title"], shared_req[r["id"]]["text"]
            L.append(f"| `{r['id']}` | {' '.join(r['p'])} | **{esc(title)}.** {esc(text)} | {esc(subst(r['value'], params, e, r['id']))} | "
                     f"{esc(r['unit']) or '—'} | {esc(r['source'])} | {r['owner']} | {r['method']} |")
        L.append("")
    L.append("## P1–P25 → requirement ids\n")
    L.append("| P | Requirement ids |\n|---|---|")
    for p in P_IDS:
        ids = [r["id"] for r in rows if p in r["p"]]
        L.append(f"| {p} | {' '.join(f'`{i}`' for i in ids)} |")
    L.append("")
    # ---- limits table, live from params.json#requirements.*
    used_by = {}
    for r in rows:
        for key in source_keys(r["source"]):
            used_by.setdefault(key, []).append(r["id"])
    L.append("## Limits: `params.json#requirements.*` (CHANGE-LOG D-14)\n")
    L.append("A1 adopted A2's 39 limits (CR-A2-01) and C1's five (CR-C1-06) as `requirements.*` keys. Claims cite "
             "`P:requirements.<key>`; the old `ASM-A2-…` nodes are retired (table after this one). Values below are read from "
             "`params.json` when this file is generated. A key used by no requirement row is flagged.\n")
    L.append("| Key | Value | Unit | Status | Source | Used by |\n|---|---|---|---|---|---|")
    unused = []
    for key, node in params.items():
        if not key.startswith("requirements.") or "value" not in node:
            continue
        who = used_by.get(key, [])
        if not who:
            unused.append(key)
        unit = node.get("unit", "-")
        L.append(f"| `{key.split('.', 1)[1]}` | {esc(fmt(node['value']))} | {esc(unit) if unit != '-' else '—'} | "
                 f"`{node.get('status', 'PROPOSED')}` | {esc(node.get('source', '—'))} | {' '.join(f'`{w}`' for w in who) or '**none**'} |")
    L.append("")
    L.append("## Retired `ASM-A2-…` ids\n")
    L.append("Each id below was A2's `PROPOSED` duplicate of a limit; the limit is now the `params.json` key. An id is still "
             "emitted (as a thin alias that carries the parameter's value and `cites` the parameter) only while another role's "
             "script names it; when the last citation goes, the alias goes. `—` means already gone.\n")
    L.append("| Retired id | `params.json` key | Still cited by |\n|---|---|---|")
    for l in inv["retired_limits"]:
        who = cited.get(l["id"], [])
        keys = [l["param"]] + l.get("also", [])
        L.append(f"| `{l['id']}` | {' '.join(f'`{k}`' for k in keys)} | {' '.join(f'`{w}`' for w in who) or '—'} |")
    L.append("")
    L.append("## Differences from REQUIREMENTS-PROPOSED.md\n")
    L.append("| P | Proposed text | This set | Why |\n|---|---|---|---|")
    L.append("| P6 | fin height 0.40 m | 0.38 m (2 × `fins.half_height_m` 0.19), confirmed D-15 | 0.40 m was the old fin *chord* |")
    L.append("| P6 / P9 | envelope 1.15 × 0.445 × 0.39 m; box 0.45 m high | envelope `transport.envelope_props_off_m` "
             f"({fmt(params['transport.envelope_props_off_m']['value'])} m, tube ends included); box `requirements.box_external_m` "
             f"({fmt(params['requirements.box_external_m']['value'])} m, D-16) | the tube ends (±0.21 m) set the height; `CL-A1-BOX-FIT` +25 mm at 0.50 m; D7 measures two cars |")
    L.append("| P14 | ≥ 3 packs | 2 flight packs (D-12); packs 3–4 only if the pessimistic reserve stays ≥ $309 + $87 | Tie-break §5.1, CHANGE-LOG D-12 |")
    L.append("| P16 | airspeed sensor optional | fitted (`R-CONFIG`, `R-AIRSPEED`) | Tie-break decision §5.1 conditions the probability claim on it |")
    L.append("| P2 | planned reserve ≥ $150 | ≥ $309 pessimistic (`R-RESERVE`) and ≥ $150 planned | Gate 1 of the tie-break is the binding rule |")
    L.append("| P13 | full throttle ≈ 30 A per motor, ESC 45 A | `R-ESC-CURRENT` around the 100 A pack-current limiter (`Q_M_BAT_CURR_MAX`): "
             "≤ 25 A per motor with the limiter, unlimited burst ≤ 55 A at 16.8 V (ESC 10 s rating), hover 27 A ± 15 % | "
             "unlimited full throttle on the 11×5.5MR is 42.4 / 51.6 A at 14.8 / 16.8 V and the motor is rated 25 A / 30 s: the limiter is the design case (CR-E1-07, A1 concurs, CR-A1-17) |")
    L.append("| P8 | 8 m/s gust \"survive-and-land\" | `R-GUST-LEAN`: lean ≤ `Q_A_ANGLE_MAX` − 5° with thrust headroom ≥ 1.3; landing upright in 8 m/s is not required (flight card 5 m/s) | The 8 m/s lean (34–36°) is within a few degrees of the tip-over angle: a landing in a gust may tip, and the feet (`R-LANDING-IMPACT`) take it |")
    L.append("| — | no hover-trim number | `R-HOVER-SPLIT`: upper/lower pair thrust ratio ≤ `requirements.hover_split_max` (D-18) | A3's roll-up gives 1.19; B3 allows 12.5 % of the pitch differential for trim |")
    L.append("| — | no structural requirements in P1–P25 | `R-LOADS`, `R-STRUCT-MARGIN`, `R-FIN-TUBE-JOINT`, `R-VIBRATION`, `R-PACK-RETENTION`, `R-LANDING-IMPACT` | The structures roles (C1–C6) need numbers to size against |")
    L.append("| — | no control-authority numbers | `R-HOVER-AUTHORITY`, `R-CRUISE-AUTHORITY`, `R-SERVO-TORQUE`, `R-AIRSPEED`, `R-COMPASS`, `R-RC-LINK` | B3, D6, F3, F5 need pass/fail values |")
    L.append("")
    (HERE / "REQUIREMENTS.md").write_text("\n".join(L), encoding="utf-8")
    return unused


# ----------------------------------------------------------------------------- VERIFICATION-MATRIX.md
def write_matrix(inv, shared_req, params, gs, graph_meta, graph_ok, cited):
    rows = inv["requirements"]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    counts = {k: 0 for k in RANK}
    fails, covered = [], 0
    for r in rows:
        g = gs.get(r["id"])
        st = g["status"] if g else "UNVERIFIED"
        counts[st] += 1
        if g and g["claims"]:
            covered += 1
        if g and g["fails"]:
            fails.append(r["id"])
    L = []
    L.append("# Verification matrix — K09-L quad tailsitter\n")
    gen = graph_meta.get("generated", "—") if graph_meta else "—"
    L.append(f"Generated {now} by `team/A2/build_requirements.py` from `team/A2/requirements.json` and `proofs/out/graph.json` "
             f"(graph built {gen}, {'OK' if graph_ok else 'with errors in other roles'' scripts'}). Status is computed by `proofs/build_graph.py` from the claims "
             f"that name each requirement in `verifies`; nobody types it. Re-run: `python -I redesign/team/A2/build_requirements.py`.\n")
    L.append("## Summary\n")
    L.append("| Requirements | With ≥ 1 claim | `VERIFIED` | `CHECKED` | `PROPOSED` | `UNVERIFIED` | `FAIL` |\n|---|---|---|---|---|---|---|")
    L.append(f"| {len(rows)} | {covered} | {counts['VERIFIED']} | {counts['CHECKED']} | {counts['PROPOSED']} | {counts['UNVERIFIED']} | {len(fails)} |\n")
    if fails:
        L.append("Failing now: " + ", ".join(f"`{f}` ({'; '.join(gs[f]['reasons'])})" for f in fails) + ".\n")
    L.append("Method: A analysis · I inspection · T test · D demonstration. On disk: evidence files that exist today / listed. "
             "`UNVERIFIED (no claim)` means the owner has not yet emitted a claim naming the id.\n")
    L.append("## Matrix\n")
    L.append("| ID | Title | Owner | Support | Method | Evidence | On disk | Claims | Margin | Status |\n|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        title = r["title"] if "text" in r else shared_req[r["id"]]["title"]
        g = gs.get(r["id"])
        ev = r["evidence"]
        present = sum(1 for e in ev if (REPO / e).exists())
        ev_cells = " ".join(f"`{e.removeprefix('redesign/')}`" for e in ev)
        claims = " ".join(f"`{c}`" for c in g["claims"]) if g and g["claims"] else "—"
        L.append(f"| `{r['id']}` | {esc(title)} | {r['owner']} | {' '.join(r.get('support', [])) or '—'} | {r['method']} | "
                 f"{ev_cells} | {present}/{len(ev)} | {claims} | {margin_cell(g['margin'] if g else None)} | {status_cell(g)} |")
    L.append("")
    L.append("## By owner\n")
    L.append("| Owner | Requirements | Open (no claim yet) |\n|---|---|---|")
    owners = {}
    for r in rows:
        owners.setdefault(r["owner"], []).append(r["id"])
    for o in sorted(owners):
        ids = owners[o]
        open_ids = [i for i in ids if not (gs.get(i) and gs[i]["claims"])]
        L.append(f"| {o} | {' '.join(f'`{i}`' for i in ids)} | {' '.join(f'`{i}`' for i in open_ids) or '—'} |")
    L.append("")
    alias = {k: v for k, v in cited.items() if v}
    L.append("## Retired limit ids still cited\n")
    if alias:
        L.append("These scripts cite an `ASM-A2-…` id that was retired by D-14. A2 emits a thin alias (value copied from "
                 "`params.json`) so they build; each owner points at the `P:requirements.<key>` instead, then the alias goes.\n")
        L.append("| Retired id | Point at | Files |\n|---|---|---|")
        for l in inv["retired_limits"]:
            if l["id"] in alias:
                L.append(f"| `{l['id']}` | `P:{l['param']}` | {' '.join(f'`{f}`' for f in alias[l['id']])} |")
    else:
        L.append("None: every retired `ASM-A2-…` id is gone from the graph.")
    L.append("")
    L.append("## How to verify this matrix\n")
    L.append("1. `python -I redesign/proofs/build_graph.py` must print `OK` (the statuses above come from its `graph.json`).")
    L.append("2. `python -I redesign/team/A2/build_requirements.py` must exit 0: every P1–P25 line maps to a requirement, every "
             "`R-…` id in the graph has a row, no id is defined twice, every `{P:key}` and source key exists in `params.json`, "
             "no row names a retired limit.")
    L.append("3. Before CDR every row has ≥ 1 claim; before first flight `build_graph.py --strict` passes (`R-PROOF-BUILD`).")
    L.append("")
    (HERE / "VERIFICATION-MATRIX.md").write_text("\n".join(L), encoding="utf-8")
    return counts, covered, fails


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-graph", action="store_true", help="do not run proofs/build_graph.py; use graph.json as is")
    a = ap.parse_args()

    inv, shared = load(INVENTORY), load(SHARED)
    params = flatten_params(load(PARAMS))
    errors, shared_req = validate(inv, shared, params)
    if errors:
        print("INVENTORY ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    cited = external_citations(inv)
    n_req, n_alias = write_claims(inv, params, cited)
    print(f"claims.json: {n_req} requirement nodes, {n_alias} retired-limit aliases still cited elsewhere "
          f"({len(inv['retired_limits']) - n_alias} of {len(inv['retired_limits'])} retired outright)")

    graph_ok, a2_errors, other_errors = True, [], 0
    if not a.no_graph:
        res = subprocess.run([sys.executable, "-I", str(BUILD_GRAPH)], cwd=str(REPO), capture_output=True, text=True)
        for line in (res.stdout + res.stderr).splitlines():
            if "ERROR" in line:
                if "A2-" in line or "team/A2" in line or "verifies unknown requirement" in line:
                    a2_errors.append(line.strip())
                else:
                    other_errors += 1
            elif line.strip().startswith(("redesign:", "status:", "OK", "FAILED")):
                print("  " + line.strip())
        if res.returncode != 0:
            graph_ok = False
            print(f"build_graph.py exited {res.returncode}: {other_errors} error(s) in other roles' scripts (drift; see CHAIN.md), "
                  f"{len(a2_errors)} on A2 nodes")
            for line in a2_errors:
                print("  " + line)
    graph = load(GRAPH) if GRAPH.exists() else {"nodes": [], "edges": [], "meta": {}}
    gs = graph_status(graph)
    extra = [rid for rid in gs if rid not in {r["id"] for r in inv["requirements"]}]
    if extra:
        print("requirement ids in the graph with no matrix row (add them to requirements.json): " + ", ".join(extra))

    unused = write_requirements(inv, shared_req, params, cited)
    if unused:
        print("params.json#requirements.* keys no requirement row uses: " + ", ".join(unused))
    counts, covered, fails = write_matrix(inv, shared_req, params, gs, graph.get("meta", {}), graph_ok, cited)
    print(f"REQUIREMENTS.md: {len(inv['requirements'])} requirements in {len(inv['groups'])} groups; "
          f"VERIFICATION-MATRIX.md: {covered} with a claim; " + ", ".join(f"{k} {v}" for k, v in counts.items())
          + f"; fails {len(fails)}")
    ok = not a2_errors and not extra
    print("A2 check: " + ("OK" if ok else "FAIL") + ("" if graph_ok else " (proof graph itself FAILED on other roles' drift)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
