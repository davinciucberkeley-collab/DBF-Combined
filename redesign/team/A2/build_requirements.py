"""build_requirements.py (A2, systems engineer): one inventory -> three outputs.

    python -I redesign/team/A2/build_requirements.py            # writes claims.json, rebuilds the proof graph,
                                                                 # writes REQUIREMENTS.md and VERIFICATION-MATRIX.md
    python -I redesign/team/A2/build_requirements.py --no-graph # skip build_graph.py (use the graph.json on disk)

Reads  team/A2/requirements.json   (A2's inventory: every requirement row, owner, method, evidence; A2's limits)
       params/claims.json          (A1's shared R-... nodes: title and text are read from there, never copied)
       proofs/out/graph.json       (statuses computed by build_graph.py; rebuilt here unless --no-graph)
Writes team/A2/claims.json         (new R-... requirement nodes + ASM-A2-... limit nodes for the proof chain)
       team/A2/REQUIREMENTS.md     (the requirement set, by group)
       team/A2/VERIFICATION-MATRIX.md (requirement -> owner -> method -> evidence -> status)

Exit 1 when the inventory is inconsistent (duplicate id, unknown shared id, a P1-P25 line with no requirement,
a requirement in the graph that has no row here, a method letter outside A/I/T/D) or build_graph.py fails.
Standard library only.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
REPO = REDESIGN.parent
INVENTORY = HERE / "requirements.json"
SHARED = REDESIGN / "params" / "claims.json"
GRAPH = REDESIGN / "proofs" / "out" / "graph.json"
BUILD_GRAPH = REDESIGN / "proofs" / "build_graph.py"
METHODS = {"A": "analysis", "I": "inspection", "T": "test", "D": "demonstration"}
RANK = {"UNVERIFIED": 0, "PROPOSED": 1, "CHECKED": 2, "VERIFIED": 3}
P_IDS = [f"P{i}" for i in range(1, 26)]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


# ----------------------------------------------------------------------------- validate
def validate(inv, shared):
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
    for sid in shared_req:
        if sid not in ids:
            errors.append(f"{sid} is defined in {rel(SHARED)} but has no row in {rel(INVENTORY)}")
    covered = {p for r in rows for p in r["p"]}
    for p in P_IDS:
        if p not in covered:
            errors.append(f"{p} maps to no requirement")
    lim_ids = [l["id"] for l in inv["limits"]]
    for i in lim_ids:
        if lim_ids.count(i) > 1:
            errors.append(f"duplicate limit id {i}")
    all_ids = set(ids) | set(lim_ids) | {n["id"] for n in shared["nodes"]}
    for r in rows:
        for tok in r["source"].replace(",", ";").split(";"):
            tok = tok.strip()
            if tok.startswith("ASM-A2-") and tok not in lim_ids:
                errors.append(f"{r['id']}: source names unknown limit {tok}")
    for l in inv["limits"]:
        for c in l.get("cites", []):
            if c not in all_ids:
                errors.append(f"{l['id']}: cites unknown id {c}")
    return errors, shared_req


# ----------------------------------------------------------------------------- claims.json
def write_claims(inv):
    nodes = []
    for r in inv["requirements"]:
        if "text" not in r:
            continue
        nodes.append({"id": r["id"], "type": "requirement", "title": r["title"], "text": r["text"], "ref": r["ref"],
                      "note": f"{'/'.join(r['p'])}; owner {r['owner']}; method {r['method']}; see team/A2/REQUIREMENTS.md"})
    for l in inv["limits"]:
        n = {"id": l["id"], "type": "assumption", "title": l["title"], "text": l["text"], "basis": l["basis"],
             "value": l["value"], "unit": l["unit"], "status": "PROPOSED",
             "note": f"A2 limit; proposed params.json key requirements.{l['param'].split('.', 1)[1]} (CR-A2-01)"}
        if l.get("cites"):
            n["cites"] = l["cites"]
        nodes.append(n)
    doc = {"schema": "proofs/1",
           "generated_by": "redesign/team/A2/build_requirements.py from team/A2/requirements.json (do not edit by hand)",
           "nodes": nodes}
    (HERE / "claims.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(nodes)


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


def code(s):
    return f"`{s}`" if s else "—"


def method_words(m):
    return " + ".join(METHODS[x] for x in m.split("+"))


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
def write_requirements(inv, shared_req, gs):
    rows = inv["requirements"]
    n_shared = sum(1 for r in rows if "text" not in r)
    n_new = len(rows) - n_shared
    L = []
    L.append("# Requirements — K09-L quad tailsitter\n")
    L.append(f"Status: `PROPOSED` requirement set (A2, {inv['date']}), re-derived from `config-study/REQUIREMENTS-PROPOSED.md` "
             f"P1–P25 for the configuration in `CONFIGURATION.md`. {len(rows)} requirements: {n_shared} shared ids from "
             f"`params/claims.json` (A1) and {n_new} added in `team/A2/claims.json`. Every one has an owner, a value with a "
             f"source, and a verification method. Status per requirement: `VERIFICATION-MATRIX.md`. "
             f"Generated by `team/A2/build_requirements.py` from `team/A2/requirements.json` — edit the JSON, not this file.\n")
    L.append("## How to read\n")
    L.append("| Column | Meaning |\n|---|---|")
    L.append("| ID | Proof-chain requirement id. A claim closes it by naming it in `verifies`. |")
    L.append("| P | The P1–P25 line(s) of `REQUIREMENTS-PROPOSED.md` it comes from. |")
    L.append("| Value · Unit | What a claim is tested against; `—` for text requirements (closed by inspection or demonstration). |")
    L.append("| Source | Where the number lives: a `params.json` key, an `ASM-A2-…` limit (A2's `PROPOSED` number, table at the end), or a decision file. |")
    L.append("| Owner · Method | Role that writes the claim; A analysis · I inspection · T test · D demonstration. Support roles: the matrix. |\n")
    L.append("## How a role closes a requirement\n")
    L.append("- Numeric: `kit.claim(..., limit={'op': '<=', 'ref': 'P:requirements.…'} or 'ASM-A2-…', verifies=['R-…'], how=…)` "
             "→ `CHECKED` when the calculation re-runs with checked inputs and the margin is ≥ 0.")
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
                title, text = r["title"], r["text"]
            else:
                title, text = shared_req[r["id"]]["title"], shared_req[r["id"]]["text"]
            L.append(f"| `{r['id']}` | {' '.join(r['p'])} | **{esc(title)}.** {esc(text)} | {esc(r['value'])} | "
                     f"{esc(r['unit']) or '—'} | {esc(r['source'])} | {r['owner']} | {r['method']} |")
        L.append("")
    L.append("## P1–P25 → requirement ids\n")
    L.append("| P | Requirement ids |\n|---|---|")
    for p in P_IDS:
        ids = [r["id"] for r in rows if p in r["p"]]
        L.append(f"| {p} | {' '.join(f'`{i}`' for i in ids)} |")
    L.append("")
    L.append("## Numbers added by A2 (`PROPOSED`, nodes `ASM-A2-…` in `team/A2/claims.json`)\n")
    L.append("Claims may reference these as `limit.ref` or inputs today. CR-A2-01 asks A1 to adopt each as the `params.json` key "
             "shown; the owning role re-derives the value and the node then cites the parameter instead.\n")
    L.append("| Id | Value | Unit | Proposed `params.json` key | Basis |\n|---|---|---|---|---|")
    for l in inv["limits"]:
        L.append(f"| `{l['id']}` | {l['value']} | {l['unit'] if l['unit'] != '-' else '—'} | `{l['param']}` | {esc(l['basis'])} |")
    L.append("")
    L.append("## Differences from REQUIREMENTS-PROPOSED.md\n")
    L.append("| P | Proposed text | This set | Why |\n|---|---|---|---|")
    L.append("| P6 | fin height 0.40 m | 0.38 m (2 × `fins.half_height_m` 0.19) | `params.json` is the source of truth; 0.40 m is the fin *chord*. A1 to confirm (CR-A2-02) |")
    L.append("| P14 | ≥ 3 packs | 2 flight packs (`battery.n_packs`); a third is the first reserve purchase after the first logged transition | Tie-break decision §5.1 |")
    L.append("| P16 | airspeed sensor optional | fitted (`R-CONFIG`, `R-AIRSPEED`) | Tie-break decision §5.1 conditions the probability claim on it |")
    L.append("| P2 | planned reserve ≥ $150 | ≥ $309 pessimistic (`R-RESERVE`) and ≥ $150 planned | Gate 1 of the tie-break is the binding rule |")
    L.append("| P13 | full throttle ≈ 30 A per motor | ≤ 36 A at 14.8 V and ≤ 45 A at 16.8 V measured (`R-ESC-CURRENT`) | 30 A is the 14.8 V table; a full pack is 16.8 V and the ESC is rated 45 A continuous |")
    L.append("| P8 | 8 m/s gust \"survive-and-land\" | `R-GUST-LEAN`: lean ≤ `Q_A_ANGLE_MAX` − 5° with thrust headroom ≥ 1.3; landing upright in 8 m/s is not required (flight card 5 m/s) | The 8 m/s lean (36°) is within 1° of the 37° tip-over angle: a landing in a gust may tip, and the feet (`R-LANDING-IMPACT`) take it |")
    L.append("| — | no structural requirements in P1–P25 | `R-LOADS`, `R-STRUCT-MARGIN`, `R-FIN-TUBE-JOINT`, `R-VIBRATION`, `R-PACK-RETENTION`, `R-LANDING-IMPACT` | The structures roles (C1–C6) need numbers to size against |")
    L.append("| — | no control-authority numbers | `R-HOVER-AUTHORITY`, `R-CRUISE-AUTHORITY`, `R-SERVO-TORQUE`, `R-AIRSPEED`, `R-COMPASS`, `R-RC-LINK` | B3, D6, F3, F5 need pass/fail values |")
    L.append("")
    (HERE / "REQUIREMENTS.md").write_text("\n".join(L), encoding="utf-8")


# ----------------------------------------------------------------------------- VERIFICATION-MATRIX.md
def write_matrix(inv, shared_req, gs, graph_meta, graph_ok):
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
             f"(graph built {gen}, {'OK' if graph_ok else 'with errors'}). Status is computed by `proofs/build_graph.py` from the claims "
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
    L.append("## How to verify this matrix\n")
    L.append("1. `python -I redesign/proofs/build_graph.py` must print `OK` (the statuses above come from its `graph.json`).")
    L.append("2. `python -I redesign/team/A2/build_requirements.py` must exit 0: every P1–P25 line maps to a requirement, every "
             "`R-…` id in the graph has a row, no id is defined twice.")
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
    errors, shared_req = validate(inv, shared)
    if errors:
        print("INVENTORY ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    n_nodes = write_claims(inv)
    print(f"claims.json: {n_nodes} nodes ({sum(1 for r in inv['requirements'] if 'text' in r)} requirements, {len(inv['limits'])} limits)")

    graph_ok = True
    if not a.no_graph:
        res = subprocess.run([sys.executable, "-I", str(BUILD_GRAPH)], cwd=str(REPO), capture_output=True, text=True)
        print(res.stdout.strip())
        if res.returncode != 0:
            graph_ok = False
            print(res.stderr.strip())
            print(f"build_graph.py exited {res.returncode}")
    graph = load(GRAPH) if GRAPH.exists() else {"nodes": [], "edges": [], "meta": {}}
    gs = graph_status(graph)
    extra = [rid for rid in gs if rid not in {r["id"] for r in inv["requirements"]}]
    if extra:
        print("requirement ids in the graph with no matrix row (add them to requirements.json): " + ", ".join(extra))

    write_requirements(inv, shared_req, gs)
    counts, covered, fails = write_matrix(inv, shared_req, gs, graph.get("meta", {}), graph_ok)
    print(f"REQUIREMENTS.md: {len(inv['requirements'])} requirements in {len(inv['groups'])} groups; "
          f"VERIFICATION-MATRIX.md: {covered} with a claim; " + ", ".join(f"{k} {v}" for k, v in counts.items())
          + f"; fails {len(fails)}")
    return 0 if graph_ok and not extra else 1


if __name__ == "__main__":
    sys.exit(main())
