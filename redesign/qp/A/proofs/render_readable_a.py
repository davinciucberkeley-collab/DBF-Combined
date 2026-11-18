"""Join out/graph.json with explain_a.py and write the readable proof chain for concept A (presentation only).

    python -I redesign/qp/A/proofs/render_readable_a.py        # run_all.py calls this after the strict build

Writes (beside graph.json, in redesign/qp/A/proofs/out/):
  READABLE.md   one page: how to read, status words, glossary, then every claim as a card (6 parts) grouped by system
  readable.js   window.PROOF_READABLE = {...}, the same cards as data for the Explorer's Guide pages
Reads only; changes no number. Every value on a card comes from graph.json; the arithmetic is evaluated here from the stored
inputs and compared with the stored result, and a disagreement is printed as a WARNING and shown on the card.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import explain_a as X  # noqa: E402

OUT = HERE / "out"
GRAPH = json.loads((OUT / "graph.json").read_text(encoding="utf-8"))
BY = {n["id"]: n for n in GRAPH["nodes"]}
OPS = {"<=": "≤", ">=": "≥"}
warnings = []


# ------------------------------------------------------------------ number formatting
def f_in(v):
    if isinstance(v, bool) or v is None:
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if v == int(v) and abs(v) < 1e9 else f"{v:.6g}"
    return str(v)


def f_out(v):
    if isinstance(v, bool) or v is None:
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if v == int(v) and abs(v) < 1e9 else f"{v:.5g}"
    return str(v)


def unit_txt(u):
    return "" if not u or u == "-" else u


def with_unit(s, u):
    return (s + " " + unit_txt(u)).strip()


# ------------------------------------------------------------------ expressions -> readable arithmetic
def pretty(expr):
    s = re.sub(r"math\.(\w+)\(math\.radians\(([^()]+)\)\)", r"\1(\2°)", expr)
    s = s.replace("math.pi", "π").replace("math.", "")
    s = s.replace("**", "^").replace("*", " × ")
    s = re.sub(r"\s*/\s*", " / ", s)
    return re.sub(r"\s+", " ", s).strip()


def substitute(expr, env):
    """Put the values into the expression text (names -> numbers), keep function names."""
    if " for " in expr:
        return None
    def rep(m):
        t = m.group(0)
        if t in env and not (m.start() > 0 and expr[m.start() - 1] == "."):
            v = env[t]
            if isinstance(v, (list, tuple)):
                return "[" + ", ".join(f_in(x) for x in v) + "]" if v and not isinstance(v[0], (list, tuple)) else t
            s = f_in(v)
            return f"({s})" if s.startswith("-") else s
        return t
    return pretty(re.sub(r"[A-Za-z_]\w*", rep, expr))


def run_steps(steps, env0):
    """[(name, expr, unit, label)] -> list of dict rows; env grows with each step."""
    env = dict(env0)
    g = {"math": math, "min": min, "max": max, "sum": sum, "abs": abs, "sorted": sorted, "zip": zip, "__builtins__": {}}
    rows = []
    for name, expr, unit, label in steps:
        val = eval(expr, g, dict(env))
        env[name] = val
        sub = substitute(expr, env0 | {k: v for k, v in env.items() if k != name})
        rows.append({"name": name, "label": label, "symbolic": pretty(expr), "sub": sub, "value": f_out(val), "raw": val, "unit": unit_txt(unit)})
    return rows


# ------------------------------------------------------------------ graph helpers
def source_of(ref_ids):
    out = []
    for s in [ref_ids] if isinstance(ref_ids, str) else (ref_ids or []):
        n = BY.get(s)
        if n:
            out.append({"id": s, "title": n.get("title", s), "url": n.get("url"), "where": n.get("where"), "checked": n.get("checked")})
        else:
            out.append({"id": s, "title": s, "url": None, "where": None, "checked": None})
    return out


def input_row(arg, ref, calc, sym):
    node = BY.get(ref, {})
    val = (calc.get("input_values") or {}).get(arg, node.get("value"))
    unit = (calc.get("units") or {}).get(arg) or node.get("unit")
    flags, src, kind = [], [], "number"
    if node.get("type") == "parameter":
        src = source_of(node.get("source"))
        if node.get("status") == "UNVERIFIED":
            flags.append("ESTIMATE / UNVERIFIED: not yet measured or confirmed")
        meaning = sym.get(arg) or ""
        note = node.get("note", "")
    elif node.get("type") == "assumption":
        kind, meaning, note = "assumption", sym.get(arg) or node.get("title", ""), node.get("basis", "")
        flags.append("ASSUMPTION" + (": unverified estimate" if node.get("status") == "UNVERIFIED" else ""))
        src = source_of(None)
    elif node.get("type") == "claim":
        kind, meaning, note = "claim", sym.get(arg) or node.get("title", ""), "result of the claim: " + node.get("title", ref)
        if node.get("status") == "UNVERIFIED":
            flags.append("result of an UNVERIFIED claim")
    else:
        meaning, note = sym.get(arg, ""), ""
    return {"sym": arg, "meaning": meaning, "value": f_in(val) if not isinstance(val, list) else None, "raw": val, "unit": unit_txt(unit), "label": node.get("title", ref) if node.get("type") != "parameter" else None,
            "ref": ref, "kind": kind, "sources": src, "note": note, "flags": flags, "is_list": isinstance(val, list), "n_rows": len(val) if isinstance(val, list) else 0}


def tables(card_inputs, tab):
    out = []
    for r in card_inputs:
        if r["is_list"] and isinstance(r["raw"], list):
            cols, labels = tab.get(r["sym"], (None, None))
            rows = r["raw"] if r["raw"] and isinstance(r["raw"][0], (list, tuple)) else [[x] for x in r["raw"]]
            if labels and len(labels) != len(rows):
                labels = None
            out.append({"sym": r["sym"], "columns": cols or [], "labels": labels or [], "rows": [[f_in(x) for x in row] for row in rows]})
    return out


def plain_result(c, lim_val, margin, ms):
    v = c["value"]
    if not c.get("limit"):
        return None
    op = c["limit"]["op"]
    if ms:
        pct = 100 * (1 + v)
        if v >= 0:
            return (f"MS = {v:+.2f} means the part can carry {1 + v:.2f} × the design load before reaching its allowable, "
                    f"so it is using {100 / (1 + v):.0f} % of what it can carry (utilisation {1 / (1 + v):.2f}). The design load already includes the factor of safety.")
        return f"MS = {v:+.2f} is negative: the part would exceed its allowable at the design load. This is a FAIL."
    if margin is None:
        return None
    word = "under" if op == "<=" else "over"
    if lim_val == 0:
        return f"The result is {f_out(v)} against a limit of 0 and the margin is the distance to zero ({margin:+.3g}); the sign decides pass or fail."
    gap = abs(v - lim_val)
    ok = margin >= 0
    if ok:
        return f"Passes. The result is {abs(margin) * 100:.2g} % {word} the limit ({gap:.2g} {unit_txt(c['unit'])} to spare)." if op == "<=" else \
               f"Passes. The result is {abs(margin) * 100:.2g} % {'above' if op == '>=' else 'under'} the limit ({gap:.2g} {unit_txt(c['unit'])} to spare)."
    return f"FAILS. The result is {abs(margin) * 100:.2g} % on the wrong side of the limit ({gap:.2g} {unit_txt(c['unit'])} short)."


dependents = {}
for n in GRAPH["nodes"]:
    if n["type"] == "calculation":
        for ref in n["inputs"].values():
            dependents.setdefault(ref, set()).add(n["id"])
calc_claims = {}
for n in GRAPH["nodes"]:
    if n["type"] == "claim" and n.get("calc"):
        calc_claims.setdefault(n["calc"], []).append(n)


def users_of_claim(cid):
    res = []
    for k in dependents.get(cid, []):
        for c in calc_claims.get(k, []):
            res.append(c["title"])
    return sorted(set(res))


tests_by_claim = {}
for e in GRAPH["edges"]:
    if e["type"] == "verifies" and e["source"].startswith("T-"):
        tests_by_claim.setdefault(e["target"], []).append(BY[e["source"]])


def margin_txt(c, lv):
    m = c.get("margin")
    if m is None:
        return None
    if lv in (0, 0.0):
        return f"{m:+.3g}"
    return f"{m:+.2%}" if abs(m) < 0.01 else f"{m:+.1%}"


def build_card(c):
    ex = X.E[c["id"]]
    calc = BY.get(c.get("calc"), {})
    ms = ex.get("ms")
    sym = {**ex.get("sym", {})}
    inputs = [input_row(a, r, calc, sym) for a, r in (calc.get("inputs") or {}).items()]
    env = dict(calc.get("outputs") or {}) | dict(calc.get("input_values") or {})
    steps, check, ms_row = None, None, None
    if ex.get("steps"):
        try:
            steps = run_steps(ex["steps"], env)
        except Exception as e:  # noqa: BLE001
            warnings.append(f"{c['id']}: steps failed ({e})")
        if steps:
            last = steps[-1]["raw"]
            ok = abs(last - c["value"]) <= 1e-6 * max(1.0, abs(c["value"]))
            check = {"computed": f_out(last), "stored": f_out(c["value"]), "ok": ok}
            if not ok:
                warnings.append(f"{c['id']}: hand arithmetic {last} != stored {c['value']}")
    if ms:
        st, al, un, load = ms
        val = al / st - 1
        dec = len(f_in(st).split(".")[1]) if "." in f_in(st) else 0
        half = 0.5 * 10 ** -dec                       # the stress is printed rounded: allow its rounding band
        lo, hi = al / (st + half) - 1, al / (st - half) - 1
        agree = lo - 0.01 <= c["value"] <= hi + 0.01
        ms_row = {"stress": f_in(st), "allow": f_in(al), "unit": un, "load": load, "computed": f"{val:.3f}", "range": f"{lo:.2f} to {hi:.2f}", "stored": f_out(c["value"]), "ok": agree,
                  "note": ex.get("note", "")}
        if not agree:
            warnings.append(f"{c['id']}: stress {st} / allowable {al} gives MS {val:.3f}, stored {c['value']} (transcribed numbers or file out of date)")
    lim = c.get("limit")
    lv = None if not lim else (lim.get("value") if lim.get("value") is not None else lim.get("resolved"))
    limit = None
    if lim:
        ref = lim.get("ref")
        rn = BY.get(ref, {}) if ref else {}
        limit = {"op": OPS[lim["op"]], "value": f_out(lv), "unit": unit_txt(c["unit"]),
                 "from": (rn.get("title") if rn.get("type") == "claim" else (rn.get("note") or ref)) if ref else "fixed in the claim",
                 "sources": source_of(rn.get("source")) if rn.get("type") == "parameter" else [], "why": ex.get("limit_why", "")}
    reqs = []
    for rid in c.get("verifies", []):
        r = BY.get(rid)
        if r:
            reqs.append({"id": rid, "title": r["title"], "text": r.get("text", "")})
    why_status = []
    for r in inputs:
        for fl in r["flags"]:
            why_status.append(f"{r['sym']}: {fl}" + (f" ({r['meaning']})" if r["meaning"] else ""))
    for a in c.get("assumes", []) or calc.get("assumes", []) or []:
        an = BY.get(a)
        if an:
            why_status.append(f"assumption: {an['title']}")
    tests = [{"id": t["id"], "title": t["title"], "state": t.get("state", ""), "procedure": t.get("procedure", "")} for t in tests_by_claim.get(c["id"], [])]
    stored_only = not ex.get("steps") and not ms
    card = {
        "id": c["id"], "title": c["title"], "group": ex["g"], "status": c["status"], "calc": calc.get("id"), "unit": unit_txt(c["unit"]),
        "why": ex["why"], "formula": ex.get("formula", ""), "tex": X.TEX.get(c["id"], ""), "symbols": [{"sym": k, "meaning": v} for k, v in sym.items()],
        "inputs": inputs, "tables": tables(inputs, ex.get("tab", {})), "steps": steps, "check": check, "ms": ms_row,
        "method": ex.get("method", []), "via": ex.get("via", ""), "via_note": ex.get("via_note", ""), "stored_only": stored_only,
        "value": f_out(c["value"]), "limit": limit,
        "margin": margin_txt(c, lv),
        "passes": None if c.get("margin") is None else c["margin"] >= 0,
        "plain": plain_result(c, lv, c.get("margin"), bool(ms)) or (("No pass / fail limit: this number feeds " + "; ".join(users_of_claim(c["id"])) + ".") if users_of_claim(c["id"]) else "No pass / fail limit: informational."),
        "status_words": dict(X.STATUS_WORDS).get(c["status"], ""), "why_status": why_status, "reasons": c.get("reasons", []),
        "reqs": reqs, "real": ex.get("real", ""), "tests": tests, "how": c.get("how", ""), "parts": c.get("parts", []), "equation_raw": calc.get("equation", ""),
        "defined_in": c.get("defined_in", ""), "script": calc.get("script", ""),
    }
    return card


def main():
    claims = [n for n in GRAPH["nodes"] if n["type"] == "claim"]
    missing = [c["id"] for c in claims if c["id"] not in X.E]
    extra = [k for k in X.E if k not in BY]
    if missing:
        warnings.append("claims with no plain-English entry (they keep the generic card): " + ", ".join(missing))
    if extra:
        warnings.append("explain_a entries for claims that no longer exist: " + ", ".join(extra))
    cards = {}
    for c in claims:
        if c["id"] in X.E:
            cards[c["id"]] = build_card(c)
        else:   # generic fallback so a new claim still appears
            X.E[c["id"]] = dict(g="mass" if False else "struct", why="(no plain-English text written for this claim yet) " + c["title"], formula=(BY.get(c.get("calc"), {}).get("equation") or ""))
            cards[c["id"]] = build_card(c)
            cards[c["id"]]["group"] = "other"
    order = [g[0] for g in X.GROUPS]
    groups = []
    for gid, title, blurb in X.GROUPS:
        ids = [cid for cid, k in cards.items() if k["group"] == gid]
        groups.append({"id": gid, "title": title, "blurb": blurb, "claims": ids, "pass": sum(1 for i in ids if cards[i]["passes"] is not False), "n": len(ids)})
    others = [cid for cid, k in cards.items() if k["group"] == "other"]
    if others:
        groups.append({"id": "other", "title": "Other claims (no plain-English text yet)", "blurb": "", "claims": others, "pass": len(others), "n": len(others)})
    reqs = {}
    for r in [n for n in GRAPH["nodes"] if n["type"] == "requirement"]:
        ids = [cid for cid, k in cards.items() if r["id"] in [q["id"] for q in k["reqs"]]]
        ids.sort(key=lambda i: (order.index(cards[i]["group"]) if cards[i]["group"] in order else 99))
        reqs[r["id"]] = {"id": r["id"], "title": r["title"], "text": r.get("text", ""), "plain": X.REQ_PLAIN.get(r["id"], ""), "claims": ids}
    nplain = [k for k, v in reqs.items() if not v["plain"]]
    if nplain:
        warnings.append("requirements with no plain statement: " + ", ".join(nplain))
    data = {"generated": GRAPH["meta"].get("generated", ""), "intro": X.INTRO, "howto": [{"t": a, "d": b} for a, b in X.HOWTO], "status_words": [{"t": a, "d": b} for a, b in X.STATUS_WORDS],
            "number_rules": X.NUMBER_RULES, "glossary": [{"t": a, "d": b, "s": s} for a, b, s in X.GLOSSARY], "groups": groups, "claims": cards, "reqs": reqs}
    (OUT / "readable.js").write_text("// generated by render_readable_a.py; do not edit\nwindow.PROOF_READABLE = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    (OUT / "READABLE.md").write_text(to_md(data), encoding="utf-8")
    n_calc = sum(1 for k in cards.values() if k["steps"] or k["ms"])
    print(f"readable: {len(cards)} claims in {len(groups)} groups; {n_calc} with arithmetic shown, {len(cards) - n_calc} stored/method-only")
    for w in warnings:
        print("WARNING:", w)


# ------------------------------------------------------------------ markdown
def md_src(sources):
    return "; ".join((f"[{s['title']}](../../../../../{s['url']})" if s.get("url") and not s["url"].startswith("http") else (f"[{s['title']}]({s['url']})" if s.get("url") else s["title"])) + (f" ({s['where']})" if s.get("where") else "") for s in sources)


def md_card(k):
    L = [f"#### {k['title']}", f"`{k['id']}` · status **{k['status']}**", ""]
    L += ["**1. What is being checked.** " + k["why"], ""]
    L += ["**2. The formula.**", ""]
    L += [f"$$ {k['tex']} $$" if k["tex"] else f"`{k['formula']}`" if k["formula"] else "—", ""]
    if k["tex"] and k["formula"]:
        L += [f"In words: {k['formula']}", ""]
    if k["symbols"]:
        L += ["| Symbol | Means |", "|---|---|"] + [f"| `{s['sym']}` | {s['meaning']} |" for s in k["symbols"]] + [""]
    if k["via"]:
        L += [f"This number is a stored result, not recomputed in this chain. It comes from: {k['via']}." + (" " + k["via_note"] if k["via_note"] else ""), ""]
    L += ["**3. The inputs.**", "", "| Input | Value | Unit | Where it came from | Status |", "|---|---|---|---|---|"]
    for r in k["inputs"]:
        val = r["value"] if not r["is_list"] else f"table, {r['n_rows']} rows (below)"
        src = md_src(r["sources"]) or (r["label"] or "")
        L.append(f"| `{r['sym']}` {('— ' + r['meaning']) if r['meaning'] else ''} | {val} | {r['unit']} | {src} | {'; '.join(r['flags']) or 'sourced'} |")
    L.append("")
    for t in k["tables"]:
        cols = (["row"] if t["labels"] else []) + (t["columns"] or [f"c{i + 1}" for i in range(len(t["rows"][0]))])
        L += [f"Table `{t['sym']}`:", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for i, row in enumerate(t["rows"]):
            L.append("| " + " | ".join(([t["labels"][i]] if t["labels"] else []) + row) + " |")
        L.append("")
    L += ["**4. The arithmetic.**", ""]
    if k["steps"]:
        for s in k["steps"]:
            L.append(f"- {s['label']}: `{s['name']} = {s['symbolic']}`" + (f" = `{s['sub']}`" if s["sub"] else "") + f" = **{s['value']} {s['unit']}**".rstrip())
        L.append("")
        L.append(("Recomputed here: matches the stored value " if k["check"]["ok"] else "WARNING recomputed value differs from the stored one: ") + f"{k['check']['computed']} vs {k['check']['stored']}.")
    elif k["ms"]:
        m = k["ms"]
        L.append(f"- Load: {m['load']}.")
        L.append(f"- MS = allowable / stress - 1 = {m['allow']} / {m['stress']} - 1 = **{m['computed']}** (stored {m['stored']}; {'agrees to the printed rounding' if m['ok'] else 'DOES NOT AGREE: see note'}).")
        L.append(f"- Stress and allowable ({m['unit']}) are copied from the cited structures file, not part of the strict chain.")
        if m["note"]:
            L.append(f"- Note: {m['note']}")
    else:
        L.append("- " + (" ".join(k["method"]) if k["method"] else "This value is read from the stored report named above; nothing to substitute."))
    L.append("")
    L += ["**5. Result against the limit.**", ""]
    lim = k["limit"]
    L.append(f"- Result: **{k['value']} {k['unit']}**" + (f", limit {lim['op']} {lim['value']} {lim['unit']}" if lim else "") + (f", margin **{k['margin']}**" if k["margin"] else ""))
    if lim:
        L.append(f"- Limit comes from: {lim['from']}." + (f" {lim['why']}" if lim["why"] else ""))
    L.append("- " + k["plain"])
    L.append(f"- Status {k['status']}: {k['status_words']}")
    for w in k["why_status"][:8]:
        L.append(f"  - {w}")
    if k["reqs"]:
        L.append("- Verifies: " + "; ".join(f"{r['id']} {r['title']}" for r in k["reqs"]))
    L += ["", "**6. How to check it in real life.** " + (k["real"] or "—")]
    for t in k["tests"]:
        L.append(f"- Planned test `{t['id']}` ({t['state']}): {t['title']}. {t['procedure']}")
    L.append("")
    return L


def to_md(d):
    L = ["# Concept A proof chain, readable edition", "",
         f"Generated by `python -I redesign/qp/A/proofs/render_readable_a.py` from out/graph.json and explain_a.py ({d['generated']}). Do not edit; edit explain_a.py. Presentation only: no number or limit here is defined by this file.", ""]
    L += ["## How to read this", ""] + d["intro"] + [""] + [f"{i + 1}. **{h['t']}.** {h['d']}" for i, h in enumerate(d["howto"])] + ["", "### Status words", ""]
    L += [f"- **{s['t']}**: {s['d']}" for s in d["status_words"]] + ["", "### About the numbers", ""] + [f"- {r}" for r in d["number_rules"]] + ["", "## Contents", ""]
    for g in d["groups"]:
        L.append(f"- [{g['title']}](#{re.sub(r'[^a-z0-9 -]', '', g['title'].lower()).replace(' ', '-')}) ({g['n']} claims)")
    L += ["- [Glossary](#glossary)", ""]
    for g in d["groups"]:
        L += [f"## {g['title']}", "", g["blurb"], ""]
        for cid in g["claims"]:
            L += md_card(d["claims"][cid])
    L += ["## Glossary", "", "| Term | Meaning |", "|---|---|"] + [f"| **{t['t']}** | {t['d']} |" for t in d["glossary"]]
    return "\n".join(L) + "\n"


main()
