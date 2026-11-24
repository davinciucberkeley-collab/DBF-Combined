"""design_loop: the agent design loop (spec 8.2) as a thin CLI over the existing concept A scripts.

    python -I tools/design_loop/cli.py list-params
    python -I tools/design_loop/cli.py run --set pack_capacity_ah=3.3 [--set part_mass:PWR-001=285 ...] [--name NAME]
                                           [--evidence-dir DIR] [--keep-work] [--fail-on-regression]

One `run` = load design (copy of the committed files into a run folder) -> baseline checks -> change parameter(s) in the copy ->
re-run checks -> interpret -> compare with the baseline -> save the changed design -> write evidence.json + evidence.md.
The committed design files are never modified (hashes are checked before and after). All file knowledge lives in the adapter
(adapter_concept_a.py by default; `--adapter adapter_<schema>` swaps it for the team schema, T-034). Exit codes: 0 loop completed,
1 a check step crashed or (with --fail-on-regression) a PASS turned into FAIL, 2 bad usage. Stdlib only.
"""
import argparse
import hashlib
import importlib
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GUARD = ["redesign/qp/A/params-A.json", "redesign/qp/A/proofs/out/graph.json", "redesign/qp/A/cad/model/mass_budget.json",
         "redesign/qp/A/cad/model/power/interfaces.json", "redesign/qp/A/cad/model/cage/interfaces.json",
         "redesign/qp/A/BOM-A.csv", "redesign/qp/A/sitl/cad_mass.json"]


def sha(p):
    f = REPO / p
    return hashlib.sha256(f.read_bytes()).hexdigest()[:16] if f.exists() else None


def fmt(m):
    v = m["value"]
    if isinstance(v, float):
        v = f"{v:.4g}" if abs(v) < 1000 else f"{v:.1f}"
    return f"{v} {m['unit'] or ''}".strip() if v not in (None, "-") else "-"


def verdict(m):
    return {True: "PASS", False: "FAIL", None: "-"}[m["pass"]]


def compare(base, var):
    rows, flips = [], []
    for k in sorted(set(base) | set(var)):
        b, v = base.get(k), var.get(k)
        if not b or not v:
            rows.append({"id": k, "note": "only in " + ("baseline" if b else "variant")})
            continue
        changed = (b["value"] != v["value"]) or (b["pass"] != v["pass"])
        if not changed:
            continue
        r = {"id": k, "title": v["title"], "category": v["category"], "limit": v["limit"], "before": fmt(b), "after": fmt(v),
             "before_verdict": verdict(b), "after_verdict": verdict(v), "margin_before": b["margin"], "margin_after": v["margin"]}
        if isinstance(b["margin"], (int, float)) and isinstance(v["margin"], (int, float)):
            r["margin_delta"] = v["margin"] - b["margin"]
        rows.append(r)
        if b["pass"] != v["pass"]:
            flips.append(r)
    return rows, flips


def interpret(rows, flips, base, var, key_metrics):
    lines = []
    for r in flips:
        word = "REGRESSION" if r["before_verdict"] == "PASS" else "IMPROVEMENT"
        lines.append(f"{word}: {r['id']} {r['before_verdict']} -> {r['after_verdict']} ({r['before']} -> {r['after']}, limit {r['limit']}) "
                     f"[{r['category']}]")
    if not flips:
        lines.append("No claim changed PASS/FAIL state.")
    movers = sorted((r for r in rows if "margin_delta" in r and r["margin_delta"]), key=lambda r: -abs(r["margin_delta"]))[:5]
    for r in movers:
        if r not in flips:
            lines.append(f"Margin {r['id']}: {r['margin_before']:.3g} -> {r['margin_after']:.3g} ({r['before']} -> {r['after']}) [{r['category']}]")
    nb = sum(1 for m in base.values() if m["pass"] is False)
    nv = sum(1 for m in var.values() if m["pass"] is False)
    lines.append(f"Failing metrics: {nb} baseline -> {nv} variant (of {sum(1 for m in var.values() if m['pass'] is not None)} judged).")
    lines.append("All claim values inherit the EST / UNVERIFIED status of their inputs (see params-A.json); a PASS here is a "
                 "re-computation, not a flight or bench result. Stored FEA / SITL / gate results are read, not re-run.")
    return lines


def md_table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def write_md(path, ev):
    L = [f"# Design loop evidence: {ev['name']}", "", f"Adapter `{ev['adapter']}`, started {ev['started']}, wall {ev['wall_s']} s. "
         "Category labels per CLAUDE.md (interference, kinematics, rigid-body dynamics, FEA, CFD, flight dynamics, illustrative).", "",
         "## Change applied (to a copy; the committed design is untouched)", ""]
    L.append(md_table(["change", "old", "new", "unit", "note"], [[c["change"], c["old"], c["new"], c["unit"], c["note"]] for c in ev["changes"]]))
    L += ["", f"Committed files unchanged after the run: **{ev['committed_unchanged']}** (sha256 prefix check of {len(ev['guard_hashes_before'])} files).",
          f"Baseline reproduces the committed claims graph: **{ev['baseline_matches_committed']['match']}** "
          f"({ev['baseline_matches_committed']['n_diff']} differing claim values).", "", "## Steps", ""]
    L.append(md_table(["phase", "step", "exit", "wall s"], [[ph, s["step"], s["exit"], s["wall_s"]] for ph in ("baseline", "variant") for s in ev["steps"][ph]]))
    L += ["", "(`build_graph --strict` exits 1 when any claim fails: that is a result, not a crash.)", "", "## Headline metrics", ""]
    keys = [k for k in ev["key_metrics"] if k in ev["variant"]]
    L.append(md_table(["metric", "category", "limit", "baseline", "", "variant", ""],
                      [[k, ev["variant"][k]["category"], ev["variant"][k]["limit"], fmt(ev["baseline"][k]), verdict(ev["baseline"][k]),
                        fmt(ev["variant"][k]), verdict(ev["variant"][k])] for k in keys]))
    L += ["", "## Interpretation", ""] + [f"- {x}" for x in ev["interpretation"]]
    L += ["", f"## All changed metrics ({len(ev['deltas'])})", ""]
    L.append(md_table(["id", "category", "limit", "before", "after", "verdict"],
                      [[r["id"], r.get("category", ""), r.get("limit", ""), r.get("before", ""), r.get("after", ""),
                        f"{r.get('before_verdict','')} -> {r.get('after_verdict','')}" if "before_verdict" in r else r.get("note", "")] for r in ev["deltas"]]))
    L += ["", "## Reproduce", "", "```", ev["command"], "```", ""]
    Path(path).write_text("\n".join(L), encoding="utf-8")


def cmd_run(a, ad):
    t0 = time.time()
    changes = ad.parse_changes(a.set)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = a.name or ts
    run_dir = Path(a.runs_dir) / f"{ts}-{name}" if a.runs_dir else HERE / "runs" / f"{ts}-{name}"
    work = run_dir / "work"
    ev_dir = Path(a.evidence_dir) if a.evidence_dir else run_dir
    ev_dir.mkdir(parents=True, exist_ok=True)
    before = {p: sha(p) for p in GUARD}

    # 1 load
    n = ad.stage(REPO, work)
    print(f"load: staged {n} files into {work}")
    # 2 baseline (same pipeline, no change)
    base = ad.run_checks(work, None)
    # 3 change + 4 run tests
    var = ad.run_checks(work, changes)
    for ph, r in (("baseline", base), ("variant", var)):
        bad = [s for s in r["steps"] if s["exit"] and s["step"] not in ("build_graph --strict", "merge_check")]
        if bad or not r["metrics"]:
            print(f"FAILED {ph}: {bad or 'no metrics'}", file=sys.stderr)
            return 1
    # 5 interpret + compare
    committed = REPO / "redesign/qp/A/proofs/out/graph.json"
    mism = []
    if committed.exists() and hasattr(ad, "read_claims"):
        cm = ad.read_claims(committed)
        mism = [k for k, m in cm.items() if k in base["metrics"] and (m["value"], m["pass"]) != (base["metrics"][k]["value"], base["metrics"][k]["pass"])]
    rows, flips = compare(base["metrics"], var["metrics"])
    interp = interpret(rows, flips, base["metrics"], var["metrics"], ad.KEY_METRICS)
    # 6 save the changed design (changed files only) + evidence
    design_dir = ev_dir / "variant_design"
    design_dir.mkdir(exist_ok=True)
    wr = work / "redesign" / "qp" / "A"
    for rel in ("params-A.json",):
        shutil.copy2(wr / rel, design_dir / rel)
    for f in sorted((wr / "cad" / "model").glob("*/interfaces.json")):
        orig = REPO / f.relative_to(work)
        if orig.read_bytes() != f.read_bytes() and json.loads(orig.read_text(encoding="utf-8")) != json.loads(f.read_text(encoding="utf-8")):
            shutil.copy2(f, design_dir / (f.parent.name + "_interfaces.json"))
    after = {p: sha(p) for p in GUARD}
    ev = {"task": "T-035 / R-INT-02", "name": name, "adapter": ad.ADAPTER_NAME, "started": ts, "wall_s": round(time.time() - t0, 1),
          "command": "python -I tools/design_loop/cli.py run " + " ".join(f"--set {s}" for s in a.set) + f" --name {name}",
          "changes": var["changes"], "steps": {"baseline": base["steps"], "variant": var["steps"]},
          "baseline": base["metrics"], "variant": var["metrics"], "key_metrics": ad.KEY_METRICS, "deltas": rows,
          "pass_fail_flips": [{k: r[k] for k in ("id", "before_verdict", "after_verdict", "before", "after", "category")} for r in flips],
          "interpretation": interp, "guard_hashes_before": before, "guard_hashes_after": after, "committed_unchanged": before == after,
          "baseline_matches_committed": {"match": not mism, "n_diff": len(mism), "ids": mism[:20]},
          "saved_design_dir": str(design_dir.relative_to(REPO)) if design_dir.is_relative_to(REPO) else str(design_dir)}
    (ev_dir / "evidence.json").write_text(json.dumps(ev, indent=1, default=str), encoding="utf-8")
    write_md(ev_dir / "evidence.md", ev)
    if not a.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    print(f"evidence: {ev_dir / 'evidence.json'} and evidence.md  (wall {ev['wall_s']} s)")
    print("changes: " + "; ".join(f"{c['change']} {c['old']} -> {c['new']}" for c in var["changes"]))
    for k in ad.KEY_METRICS:
        if k in var["metrics"]:
            print(f"  {k:20s} {fmt(base['metrics'][k]):>14s} {verdict(base['metrics'][k])} -> {fmt(var['metrics'][k]):>14s} {verdict(var['metrics'][k])}")
    for x in interp[:4]:
        print("  " + x)
    if not ev["committed_unchanged"]:
        print("ERROR: a committed file changed", file=sys.stderr)
        return 1
    return 1 if (a.fail_on_regression and any(r["before_verdict"] == "PASS" for r in flips)) else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--adapter", default="adapter_concept_a", help="parameter adapter module (default: concept A)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-params", help="parameters the adapter can change")
    r = sub.add_parser("run", help="load, baseline, change, test, compare, save, evidence")
    r.add_argument("--set", action="append", default=[], help="name=value, repeatable (see list-params); none = identity run")
    r.add_argument("--name", help="run name (folder suffix)")
    r.add_argument("--runs-dir", help="parent of the run folder (default tools/design_loop/runs, git-ignored)")
    r.add_argument("--evidence-dir", help="write evidence.json/.md and variant_design/ here instead of the run folder")
    r.add_argument("--keep-work", action="store_true", help="keep the staged working copy (about 35 MB)")
    r.add_argument("--fail-on-regression", action="store_true", help="exit 1 if any PASS turns into FAIL")
    a = ap.parse_args(argv)
    ad = importlib.import_module(a.adapter)
    if a.cmd == "list-params":
        for k, v in ad.list_parameters().items():
            print(f"{k}\n    {v}")
        return 0
    try:
        return cmd_run(a, ad)
    except (ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
