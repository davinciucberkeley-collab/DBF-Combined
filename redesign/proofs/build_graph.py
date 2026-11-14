"""build_graph: merge every claims.json, re-run every calculation, write graph.json + CHAIN.md.

    python -I redesign/proofs/build_graph.py              # real build: redesign/**/claims*.json -> redesign/proofs/out/
    python -I redesign/proofs/build_graph.py --examples   # the demo aircraft -> redesign/proofs/examples/out/
    python -I redesign/proofs/build_graph.py --strict     # also fail on negative margins and requirements with no claim

Exit code 0 = every stored number re-computes; 1 = drift or a broken reference (each one printed).
Format and status rules: SCHEMA.md. Standard library only; runs in well under a second for hundreds of claims.
"""
import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True                  # importing analysis scripts must not leave __pycache__ folders
sys.path.insert(0, str(HERE))
import proofkit as pk  # noqa: E402

REDESIGN = HERE.parent
REPO = REDESIGN.parent
RANK = {s: i for i, s in enumerate(pk.STATUSES)}            # UNVERIFIED 0 < PROPOSED 1 < CHECKED 2 < VERIFIED 3
DEFAULT_PART_LINK = "../../viewer/index.html#part={id}"     # redesign/viewer/ (aircraft web viewer), from proofs/viewer/


class Build:
    def __init__(self, root, include_examples):
        self.root, self.include_examples = root, include_examples
        self.nodes, self.edges, self.errors, self.warnings = {}, [], [], []
        self.files = []

    # ------------------------------------------------------------------ load
    def _skip(self, f):
        rel = f.relative_to(self.root).parts
        return "out" in rel or "vendor" in rel or "node_modules" in rel or (not self.include_examples and f.is_relative_to(HERE / "examples"))

    def load(self):
        claim_files = sorted(f for pat in ("claims.json", "claims.*.json") for f in self.root.rglob(pat) if not self._skip(f))
        param_files = []
        if self.root == REDESIGN and (REDESIGN / "params" / "params.json").exists():     # the shared numbers
            param_files.append(REDESIGN / "params" / "params.json")
        for f in claim_files:
            doc = json.loads(f.read_text(encoding="utf-8"))
            if doc.get("schema") != pk.SCHEMA:
                self.errors.append(f"{pk.repo_rel(f)}: schema is {doc.get('schema')!r}, expected {pk.SCHEMA!r}")
            self.files.append(pk.repo_rel(f))
            param_files += [(f.parent / p).resolve() for p in doc.get("params", [])]
            for n in doc.get("nodes", []):
                self._put(dict(n, defined_in=pk.repo_rel(f)))
        for pf in dict.fromkeys(param_files):           # de-duplicate, keep order
            if not pf.exists():
                self.errors.append(f"params file not found: {pf}")
                continue
            for pid, p in pk.load_params(pf).items():
                old = self.nodes.get(pid)
                if old and not pk.close(old.get("value"), p.get("value"), 1e-12):
                    self.errors.append(f"{pid}: {old['file']} says {old.get('value')}, {p['file']} says {p.get('value')}")
                elif not old:
                    self.nodes[pid] = p
        self.part_names = self._load_parts()

    def _put(self, n):
        if n.get("type") not in pk.NODE_TYPES:
            self.errors.append(f"{n.get('id')}: unknown type {n.get('type')!r} ({n['defined_in']})")
        elif n["id"] in self.nodes:
            self.errors.append(f"duplicate id {n['id']} in {n['defined_in']} and {self.nodes[n['id']].get('defined_in')}")
        else:
            self.nodes[n["id"]] = n

    def _load_parts(self):
        """Part ids from any interfaces.json (tolerant: part_id keys, 'parts' lists, or nodes of type 'part')."""
        names = {}

        def walk(d, in_parts=False):
            if isinstance(d, dict):
                pid = d.get("part_id") or ((in_parts or d.get("type") == "part") and d.get("id"))
                if isinstance(pid, str):
                    names[pid] = d.get("name", "")
                for k, v in d.items():
                    walk(v, k == "parts")
            elif isinstance(d, list):
                for v in d:
                    walk(v, in_parts)

        for f in self.root.rglob("interfaces.json"):
            if not self._skip(f):
                walk(json.loads(f.read_text(encoding="utf-8")))
        return names

    # ------------------------------------------------------------------ references and edges
    def ref(self, frm, to, etype, field):
        """Record an edge 'to' <- 'frm' ... stored in evidence direction (supporter -> supported)."""
        if to not in self.nodes:
            self.errors.append(f"{frm}: {field} names unknown id {to!r}")
            return
        self.edges.append({"source": to, "target": frm, "type": etype})

    def link(self):
        for n in list(self.nodes.values()):
            nid, t = n["id"], n["type"]
            for c in n.get("cites", []):
                self.ref(nid, c, "cites", "cites")
            for a in n.get("assumes", []):
                self.ref(nid, a, "assumes", "assumes")
            if t == "parameter":
                srcs = n.get("source") or []
                for s in [srcs] if isinstance(srcs, str) else srcs:
                    if s in self.nodes:
                        self.ref(nid, s, "cites", "source")
            elif t == "calculation":
                for arg, r in n.get("inputs", {}).items():
                    self.ref(nid, r, "uses", f"inputs.{arg}")
            elif t == "claim":
                if not n.get("how"):
                    self.warnings.append(f"{nid}: no 'how' (how to verify) line")
                if n.get("calc"):
                    self.ref(nid, n["calc"], "derives-from", "calc")
                if (n.get("limit") or {}).get("ref"):
                    self.ref(nid, n["limit"]["ref"], "uses", "limit.ref")
                for r in n.get("verifies", []):
                    self.edges.append({"source": nid, "target": r, "type": "verifies"}) if r in self.nodes else \
                        self.errors.append(f"{nid}: verifies unknown requirement {r!r}")
                for p in n.get("parts", []):
                    if p not in self.nodes:
                        if p not in self.part_names:
                            self.warnings.append(f"{nid}: part {p} is not in any interfaces.json")
                        self.nodes[p] = {"id": p, "type": "part", "title": self.part_names.get(p) or p}
                    self.edges.append({"source": nid, "target": p, "type": "about"})
            elif t == "test":
                for c in n.get("verifies", []):
                    self.edges.append({"source": nid, "target": c, "type": "verifies"}) if c in self.nodes else \
                        self.errors.append(f"{nid}: verifies unknown claim {c!r}")
            elif t == "source" and not n.get("url") and n.get("kind") not in ("book", "standard", "test"):
                self.warnings.append(f"{nid}: source has no url")

    # ------------------------------------------------------------------ recompute
    def value_of(self, ref):
        n = self.nodes.get(ref)
        if n is None or "value" not in n:
            raise pk.ProofError(f"{ref} has no value" if n else f"unknown id {ref}")
        return n["value"]

    def recompute(self):
        for c in [n for n in self.nodes.values() if n["type"] == "calculation"]:
            cid, tol = c["id"], c.get("tol") or 1e-6
            for arg, unit in c.get("units", {}).items():          # cheap unit check (string compare)
                inp = self.nodes.get(c["inputs"].get(arg, ""))
                if inp and inp.get("unit") and inp["unit"] != unit:
                    self.errors.append(f"{cid}: input {arg} expects {unit}, {inp['id']} is in {inp['unit']}")
            try:
                got, used = pk.call_calc(c, self.value_of, REPO)
            except Exception as e:                                 # report and keep going: show every problem at once
                where = traceback.extract_tb(e.__traceback__)[-1]
                self.errors.append(f"{cid}: {c['script']}::{c['function']} failed: {type(e).__name__}: {e} "
                                   f"(line {where.lineno})")
                c["drift"] = True
                continue
            for name, stored in c.get("outputs", {}).items():
                if name not in got:
                    self.errors.append(f"{cid}: output {name} no longer returned by {c['function']}()")
                elif not pk.close(got[name], stored, tol):
                    changed = [f"{a} {pk.fmt(c['input_values'][a])} -> {pk.fmt(v)} ({c['inputs'][a]})"
                               for a, v in used.items()
                               if a in c.get("input_values", {}) and not pk.close(c["input_values"][a], v, 1e-12)]
                    self.errors.append(f"DRIFT {cid}.{name}: stored {pk.fmt(stored)}, re-runs to {pk.fmt(got[name])}. "
                                       f"Changed inputs: {'; '.join(changed) or 'none (the function changed)'}. "
                                       f"Re-run {c['script']}")
                    c["drift"] = True
            c["recomputed"] = got
        for n in self.nodes.values():
            if n["type"] == "claim" and n.get("calc") in self.nodes:
                stored = self.nodes[n["calc"]].get("outputs", {})
                if n.get("output") not in stored:
                    self.errors.append(f"{n['id']}: calc {n['calc']} has no output {n.get('output')!r}")
                elif not pk.close(stored[n["output"]], n.get("value"), 1e-9):
                    self.errors.append(f"DRIFT {n['id']}: value {pk.fmt(n.get('value'))} but {n['calc']}.{n['output']} "
                                       f"= {pk.fmt(stored[n['output']])}")

    # ------------------------------------------------------------------ status
    def incoming(self, nid, *types):
        return [self.nodes[e["source"]] for e in self.edges if e["target"] == nid and (not types or e["type"] in types)]

    def status(self):
        for n in self.nodes.values():
            n["reasons"], n["declared"] = [], n.pop("status", None)
        order = ["source", "parameter", "assumption", "test", "calculation", "claim", "requirement", "part"]
        memo = set()

        def visit(n):
            if n["id"] in memo:
                return n["status"]
            memo.add(n["id"])
            n["status"] = "UNVERIFIED"                            # provisional, also breaks cycles
            getattr(self, "_st_" + n["type"])(n, visit)
            return n["status"]

        for t in order:
            for n in self.nodes.values():
                if n["type"] == t:
                    visit(n)

    def _st_source(self, n, visit):
        if n["declared"] in RANK:
            n["status"] = n["declared"]
        elif n.get("kind") == "test" and n.get("checked"):
            n["status"] = "VERIFIED"
        elif n.get("checked"):
            n["status"] = "CHECKED"
        else:
            n["status"], n["reasons"] = "UNVERIFIED", ["value never compared with the source (no 'checked' date)"]

    def _st_parameter(self, n, visit):
        srcs = self.incoming(n["id"], "cites")
        if srcs:
            n["status"] = min((visit(s) for s in srcs), key=RANK.get)
            n["reasons"] = [f"cites {s['id']}, which is UNVERIFIED" for s in srcs if s["status"] == "UNVERIFIED"]
        elif n.get("source"):
            n["status"] = "PROPOSED"                               # a text basis: design choice, not evidence
        else:
            n["status"], n["reasons"] = "UNVERIFIED", ["no source"]
        if n["declared"] in RANK and RANK[n["declared"]] < RANK[n["status"]]:
            n["status"] = n["declared"]                            # an author may downgrade, never upgrade
            n["reasons"].append(f"marked {n['declared']} in {n['file']}" + (f": {n['note']}" if n.get("note") else ""))

    def _st_assumption(self, n, visit):
        n["status"] = n["declared"] if n["declared"] in ("PROPOSED", "UNVERIFIED") else "PROPOSED"
        if n["status"] == "UNVERIFIED":
            n["reasons"] = ["assumption marked UNVERIFIED by its author"]

    def _st_test(self, n, visit):
        if n.get("state") == "run" and n.get("result") == "pass":
            n["status"] = "VERIFIED"
        elif n.get("state") == "run":
            n["status"], n["fails"], n["reasons"] = "UNVERIFIED", True, [f"test result: {n.get('result')}"]
        else:
            n["status"] = "PROPOSED"

    def _st_calculation(self, n, visit):
        n["status"] = "UNVERIFIED" if n.get("drift") else "CHECKED"
        if n.get("drift"):
            n["reasons"] = ["does not re-run to its stored outputs (see build errors)"]

    def _st_claim(self, n, visit):
        reasons = []
        lim = n.get("limit")
        if lim:
            lv = lim.get("value")
            if lv is None and lim.get("ref") in self.nodes:
                lv = self.nodes[lim["ref"]].get("value")
            lim["resolved"] = lv
            n["margin"] = pk.margin(n.get("value"), lv, lim["op"])
            if lv == 0 and n["margin"] is not None:
                n["margin_abs"] = True                             # limit 0: the margin is a distance in the claim's unit
            if n["margin"] is not None and n["margin"] < 0:
                n["fails"] = True
                reasons.append(f"FAILS: margin {pk.margin_text(n['margin'], lv, n.get('unit'), 1)} "
                               f"({pk.fmt(n['value'], n.get('unit'))} vs {lim['op']} {pk.fmt(lv, n.get('unit'))})")
            elif n["margin"] is None and isinstance(lv, (int, float)):
                self.warnings.append(f"{n['id']}: has a limit, but its value {n.get('value')!r} is not a number, "
                                     f"so pass / fail is not judged")
        calc = self.nodes.get(n.get("calc"))
        if calc is None:
            status = "PROPOSED"                                    # a value with no calculation yet
        else:
            if visit(calc) == "UNVERIFIED":
                reasons.append(f"{calc['id']} does not re-run")
            for inp in self.incoming(calc["id"], "uses", "assumes", "cites") + self.incoming(n["id"], "uses", "assumes", "cites"):
                s = visit(inp)
                if inp["type"] == "claim" and s not in ("CHECKED", "VERIFIED"):
                    reasons.append(f"uses {inp['id']}, which is {s}")
                elif s == "UNVERIFIED":
                    reasons.append(f"uses {inp['id']}, which is UNVERIFIED" + (f" ({inp['reasons'][0]})" if inp.get("reasons") else ""))
            status = "UNVERIFIED" if reasons else "CHECKED"
        tests = self.incoming(n["id"], "verifies")
        passed = [t for t in tests if visit(t) == "VERIFIED"]
        if passed and not n.get("fails"):
            status = "VERIFIED"
            reasons = [r for r in reasons if r.startswith("FAILS")]
        for t in tests:
            if t.get("fails"):
                n["fails"] = True
                reasons.append(f"{t['id']} ran and failed")
                status = "UNVERIFIED"
        n["status"], n["reasons"] = status, reasons

    def _st_requirement(self, n, visit):
        claims = self.incoming(n["id"], "verifies")
        if not claims:
            n["status"], n["reasons"] = "UNVERIFIED", ["no claim verifies it"]
            return
        n["status"] = min((visit(c) for c in claims), key=RANK.get)
        n["fails"] = any(c.get("fails") for c in claims)
        n["reasons"] = [f"{c['id']}: {c['reasons'][0]}" if c.get("fails") else f"{c['id']} is {c['status']}"
                        for c in claims if c.get("fails") or (c["status"] == n["status"] and n["status"] != "VERIFIED")]

    def _st_part(self, n, visit):
        n["status"] = min((visit(c) for c in self.nodes.values() if c["type"] == "claim" and n["id"] in c.get("parts", [])),
                          key=RANK.get, default="PROPOSED")

    # ------------------------------------------------------------------ importance and chains
    def upstream(self, nid):
        """Everything this node rests on (evidence direction, excluding part links)."""
        seen, stack = set(), [nid]
        while stack:
            cur = stack.pop()
            for e in self.edges:
                if e["target"] == cur and e["type"] != "about" and e["source"] not in seen:
                    seen.add(e["source"])
                    stack.append(e["source"])
        return seen

    def importance(self):
        for n in self.nodes.values():
            n["importance"] = 0
        for n in self.nodes.values():
            if n["type"] == "claim":
                for u in self.upstream(n["id"]) | {n["id"]}:
                    self.nodes[u]["importance"] += 1
            elif n["type"] == "requirement":
                n["importance"] = 1 + sum(self.nodes[u]["type"] == "claim" for u in self.upstream(n["id"])) * 2
            elif n["type"] == "part":
                n["importance"] = sum(1 for e in self.edges if e["target"] == n["id"])

    # ------------------------------------------------------------------ output
    def graph(self, dataset, part_link):
        drop = {"declared", "recomputed"}
        nodes = [{k: v for k, v in n.items() if k not in drop and v not in (None, [], {})} for n in self.nodes.values()]
        counts = {"by_type": {}, "by_status": {}, "fails": sum(bool(n.get("fails")) for n in nodes)}
        for n in nodes:
            counts["by_type"][n["type"]] = counts["by_type"].get(n["type"], 0) + 1
            counts["by_status"][n["status"]] = counts["by_status"].get(n["status"], 0) + 1
        return {"schema": pk.SCHEMA,
                "meta": {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "dataset": dataset,
                         "ok": not self.errors, "errors": self.errors, "warnings": self.warnings, "counts": counts,
                         "files": self.files, "part_link": part_link, "statuses": list(pk.STATUSES)},
                "nodes": nodes, "edges": self.edges}

    def chain_md(self, dataset):
        N, out = self.nodes, []
        st = lambda n: f"**{n['status']}**" + (" **FAILS**" if n.get("fails") else "")
        reqs = sorted((n for n in N.values() if n["type"] == "requirement"), key=lambda n: n["id"])
        out += [f"# Proof chains ({dataset})", "",
                f"Generated by `python -I redesign/proofs/build_graph.py{' --examples' if dataset == 'examples' else ''}` "
                f"— do not edit. Read each section top to bottom: requirement ← claim ← calculation ← inputs ← sources.",
                "Status words: SCHEMA.md. Explore the same graph in 3-D: `redesign/proofs/viewer/index.html`.",
                "Parameter files: " + ", ".join(sorted({f"`{n['file']}`" for n in N.values() if n["type"] == "parameter"})), ""]
        if self.errors:
            out += ["> **BUILD FAILED** — the numbers below may be stale:", ""] + [f"> - {e}" for e in self.errors] + [""]
        out += ["| Requirement | Status | Claims | Smallest margin |", "|---|---|---|---|"]
        for r in reqs:
            cl = self.incoming(r["id"], "verifies")
            ms = [c["margin"] for c in cl if c.get("margin") is not None and not c.get("margin_abs")]
            zero = sum(1 for c in cl if c.get("margin_abs") and c["margin"] < 0)      # fails against a limit of 0
            txt = (f"{min(ms):+.0%}" if ms else "") + (f"{'; ' if ms else ''}{zero} below a limit of 0" if zero else "")
            out.append(f"| [{r['id']}](#{r['id'].lower()}) {r['title']} | {st(r)} | {len(cl)} | {txt or '—'} |")
        out.append("")

        def line(n):
            t, v = n["type"], lambda x: pk.fmt(x.get("value"), x.get("unit", ""))
            if t == "claim":
                lim = n.get("limit")
                limtxt = (f" (limit {lim['op']} {pk.fmt(lim.get('resolved'), n.get('unit'))}, "
                          f"margin {pk.margin_text(n['margin'], lim.get('resolved'), n.get('unit'))})") \
                    if lim and n.get("margin") is not None else ""
                return f"claim **{n['id']}** {n['title']} = **{v(n)}**{limtxt} — {st(n)}"
            if t == "calculation":
                eq = f": `{n['equation']}`" if n.get("equation") else ""
                return f"calc `{n['id']}` `{n['script']}::{n['function']}()`{eq} — {st(n)}"
            if t == "parameter":
                basis = f" ({n['source']})" if isinstance(n.get("source"), str) and n["source"] not in N else ""
                return f"param `{n['id']}` = {v(n)}{basis} — {st(n)}"
            if t == "source":
                link = f"[{n['title']}]({n['url']})" if n.get("url") else n["title"]
                chk = f", checked {n['checked']}" if n.get("checked") else ""
                return f"source `{n['id']}` {link}{', ' + n['where'] if n.get('where') else ''}{chk} — {st(n)}"
            if t == "assumption":
                val = f" = {v(n)}" if "value" in n else ""
                return f"assumption `{n['id']}` {n['text']}{val} (basis: {n['basis']}) — {st(n)}"
            if t == "test":
                res = (f", result {n['result']}" if n.get("result") else "") + (f", measured {n['measured']}" if n.get("measured") else "")
                return f"test `{n['id']}` {n['title']} ({n.get('state')}{res}) — {st(n)}"
            return f"{t} `{n['id']}`"

        # a claim's full chain is printed once: under the requirement it verifies (its "home"), else where first met
        home = {}
        for r in reqs:
            for c in self.incoming(r["id"], "verifies"):
                home.setdefault(c["id"], r["id"])
        expanded = set()

        def tree(n, depth, seen, label="", section=None):
            pad = "  " * depth
            if n["id"] in seen:
                out.append(f"{pad}- {label}`{n['id']}` (see above)")
                return
            seen.add(n["id"])
            if n["type"] == "claim" and depth > 0 and (home.get(n["id"], section) != section or n["id"] in expanded):
                where = home.get(n["id"])
                out.append(f"{pad}- {label}{line(n)} — chain under [{where}](#{where.lower()})" if where
                           else f"{pad}- {label}{line(n)} — chain printed above")
                return
            expanded.add(n["id"])
            out.append(f"{pad}- {label}{line(n)}")
            for r in n.get("reasons", []):
                out.append(f"{pad}  - ⚠ {r}")
            if n["type"] == "claim":
                if n.get("how"):
                    out.append(f"{pad}  - how to verify: {n['how']}")
                if n.get("parts"):
                    out.append(f"{pad}  - parts: {', '.join(n['parts'])}")
            if n["type"] == "calculation":
                for arg, ref in n["inputs"].items():
                    if ref in N:
                        tree(N[ref], depth + 1, seen, f"`{arg}` ← ", section)
                kids = self.incoming(n["id"], "assumes", "cites")
            else:
                kids = [k for k in self.incoming(n["id"], "derives-from", "uses", "assumes", "cites", "verifies")]
            for k in kids:
                tree(k, depth + 1, seen, "", section)

        for r in reqs:
            out += [f"## {r['id']}", "", f"**{r['title']}** — {r['text']} — {st(r)}"
                    + (f"  \nDefined in: {r['ref']}" if r.get("ref") else ""), ""]
            seen = {r["id"]}
            for c in self.incoming(r["id"], "verifies"):
                tree(c, 0, seen, "", r["id"])
            out.append("")
        loose = [n for n in N.values() if n["type"] == "claim" and not n.get("verifies")]
        if loose:
            out += ["## Claims not tied to a requirement", ""]
            seen = set()
            for c in loose:
                if c["id"] in expanded:
                    out.append(f"- {line(c)} — chain printed above")
                else:
                    tree(c, 0, seen)
        return "\n".join(out) + "\n"


def self_check(nodes):
    """Judge every claim a second way: plain comparison of value and limit, no margin arithmetic.

    A claim with a numeric value and a numeric limit must carry a margin, must be marked `fails` when the value is
    on the wrong side of the limit, and must not have a negative margin when it is on the right side. A mismatch
    is a build error. (CDR-03: the margin rule skipped limits of 0 and 15 violated claims were not counted.)"""
    num = lambda x: isinstance(x, (int, float)) and x == x
    bad = []
    for n in nodes:
        lim = n.get("limit") if n["type"] == "claim" else None
        v, lv = n.get("value"), (lim or {}).get("resolved")
        if not lim or not num(v) or not num(lv):
            continue
        violated = v < lv if lim["op"] == ">=" else v > lv
        if n.get("margin") is None:
            bad.append(f"SELF-CHECK {n['id']}: numeric value and limit but no margin")
        elif violated and not n.get("fails"):
            bad.append(f"SELF-CHECK {n['id']}: {pk.fmt(v)} violates {lim['op']} {pk.fmt(lv)} but is not marked FAILS")
        elif not violated and n["margin"] < 0:
            bad.append(f"SELF-CHECK {n['id']}: {pk.fmt(v)} meets {lim['op']} {pk.fmt(lv)} but has a negative margin")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--examples", action="store_true", help="build the demo aircraft in proofs/examples/")
    ap.add_argument("--root", type=Path, help="folder to scan for claims*.json (default: redesign/)")
    ap.add_argument("--out", type=Path, help="output folder (default: proofs/out or proofs/examples/out)")
    ap.add_argument("--strict", action="store_true", help="also fail on negative margins / requirements with no claim")
    ap.add_argument("--part-link", default=DEFAULT_PART_LINK, help="URL template for a part id, {id} is replaced")
    a = ap.parse_args(argv)

    root = (a.root or (HERE / "examples" if a.examples else REDESIGN)).resolve()
    out = (a.out or (HERE / "examples" / "out" if a.examples else HERE / "out")).resolve()
    dataset = "examples" if a.examples else "redesign"
    b = Build(root, include_examples=a.examples or (a.root is not None and root.is_relative_to(HERE / "examples")))
    b.load()
    b.link()
    b.recompute()
    b.status()
    b.importance()
    b.errors += self_check(b.nodes.values())
    if a.strict:
        b.errors += [f"STRICT {n['id']}: {n['reasons'][0]}" for n in b.nodes.values()
                     if n["type"] in ("claim", "requirement") and (n.get("fails") or "no claim verifies it" in n["reasons"])]
    g = b.graph(dataset, a.part_link)
    out.mkdir(parents=True, exist_ok=True)
    # meta.generated = when the GRAPH last changed: keep the old stamp when nothing else differs, so re-running
    # the build does not dirty the committed out/ files
    try:
        old = json.loads((out / "graph.json").read_text(encoding="utf-8"))
        if {k: v for k, v in old["meta"].items() if k != "generated"} == {k: v for k, v in g["meta"].items() if k != "generated"} \
                and old["nodes"] == g["nodes"] and old["edges"] == g["edges"]:
            g["meta"]["generated"] = old["meta"]["generated"]
    except (OSError, ValueError, KeyError):
        pass
    text = json.dumps(g, indent=1, ensure_ascii=False)
    (out / "graph.json").write_text(text + "\n", encoding="utf-8")
    (out / "graph.js").write_text(f"// generated by build_graph.py; lets viewer/index.html open from file://\n"
                                  f"window.PROOF_GRAPH = {text};\n", encoding="utf-8")
    (out / "CHAIN.md").write_text(b.chain_md(dataset), encoding="utf-8")

    c = g["meta"]["counts"]
    print(f"{dataset}: {len(b.files)} claims files, {len(g['nodes'])} nodes, {len(g['edges'])} edges -> {pk.repo_rel(out)}/")
    print("  status: " + ", ".join(f"{s} {c['by_status'].get(s, 0)}" for s in pk.STATUSES) + f"; fails {c['fails']}")
    for w in b.warnings:
        print("  warning:", w)
    for e in b.errors:
        print("  ERROR:", e, file=sys.stderr)
    print("FAILED" if b.errors else "OK: every stored number re-computes")
    return 1 if b.errors else 0


if __name__ == "__main__":
    sys.exit(main())
