"""proofkit: let an analysis script record its claims while it computes them.

Usage (full example: examples/power/analysis.py; format: SCHEMA.md):

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "proofs"))   # redesign/proofs
    import proofkit as pk

    kit = pk.Kit(__file__, params=["../../params/params.json"])        # paths relative to this script

    @kit.calc("CALC-AERO-STALL", equation="Vs = sqrt(2 m g / (rho S CLmax))",
              inputs={"m": "CL-MASS-MTOW", "S": "P:wing.area_m2", "CLmax": "ASM-AERO-CLMAX", "rho": "P:env.rho"},
              units={"m": "kg", "S": "m2", "rho": "kg/m3", "Vs": "m/s"})
    def stall_speed(m, S, CLmax, rho):
        return {"Vs": (2 * m * 9.80665 / (rho * S * CLmax)) ** 0.5}

    kit.claim("CL-AERO-STALL", "Stall speed at MTOW", calc="CALC-AERO-STALL", output="Vs", unit="m/s",
              limit=("<=", "P:requirements.stall_max"), verifies=["R-STALL"], parts=["WNG-001"],
              how="Re-run this script; flight test: slow-flight stall at MTOW.")

    if __name__ == "__main__":
        kit.write()          # runs every calc, fills values, writes claims.json beside the script

Rules: the calculation function is plain Python of its named inputs only (no file reads, no globals that change),
because build_graph.py imports the script and calls it again to confirm the stored numbers. Keep the script's
top level free of side effects: do the work under `if __name__ == "__main__":`.
Standard library only.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

SCHEMA = "proofs/1"
STATUSES = ("UNVERIFIED", "PROPOSED", "CHECKED", "VERIFIED")      # worst -> best
NODE_TYPES = ("requirement", "claim", "calculation", "parameter", "source", "assumption", "test", "part")


class ProofError(Exception):
    """Anything that must stop the build (drift, bad reference, unit mismatch)."""


# ---------------------------------------------------------------- paths
def redesign_root(start):
    """Walk up from `start` to the folder named 'redesign'."""
    p = Path(start).resolve()
    for q in [p, *p.parents]:
        if q.name == "redesign":
            return q
    raise ProofError(f"{start} is not inside a 'redesign' folder")


def repo_rel(path):
    """Repo-relative POSIX path (repo root = parent of redesign/)."""
    path = Path(path).resolve()
    return path.relative_to(redesign_root(path).parent).as_posix()


# ---------------------------------------------------------------- params.json
def flatten_params(data, file_label):
    """params.json -> {"P:<dotted.key>": parameter node}.

    A leaf is either a bare value (number, string, list) or an object with a "value" key and optional
    "unit", "source", "status", "note". Objects without "value" are groups. Keys starting with "_" are comments.
    """
    out = {}

    def walk(d, prefix):
        for k, v in d.items():
            if k.startswith("_"):
                continue
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict) and "value" not in v:
                walk(v, key)
                continue
            node = {"id": f"P:{key}", "type": "parameter", "title": key, "file": file_label}
            if isinstance(v, dict):
                node.update({f: v[f] for f in ("value", "unit", "source", "status", "note") if f in v})
            else:
                node["value"] = v
            out[node["id"]] = node

    walk(data, "")
    return out


def load_params(path):
    path = Path(path).resolve()
    return flatten_params(json.loads(path.read_text(encoding="utf-8")), repo_rel(path))


# ---------------------------------------------------------------- numbers
def close(a, b, tol):
    """Relative comparison that also handles lists (tables) and non-numbers."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=tol, abs_tol=1e-12)
    return a == b


def fmt(v, unit=""):
    """4 significant figures; tables shown as their size."""
    if isinstance(v, bool) or v is None:
        s = str(v)
    elif isinstance(v, (int, float)):
        s = f"{v:.4g}" if v != int(v) or abs(v) >= 1e5 else str(int(v))
    elif isinstance(v, list):
        s = f"table ({len(v)} rows)"
    else:
        s = str(v)
    return f"{s} {unit}".strip() if unit and unit != "-" else s


def margin(value, limit_value, op):
    """Signed margin; negative = fails.

    Limit not 0: a fraction of the limit, (value - limit) / |limit| for ">=", (limit - value) / |limit| for "<=".
    Limit 0 (margins of safety, clearances, counts): a fraction of 0 does not exist, so the margin is the signed
    distance to the limit in the claim's own unit: value for ">= 0", -value for "<= 0". The sign alone decides
    pass / fail in both cases. (CDR-03, 2026-11-13: a limit of 0 used to return None, so the fail was not counted.)
    """
    if not isinstance(value, (int, float)) or not isinstance(limit_value, (int, float)) \
            or math.isnan(value) or math.isnan(limit_value):
        return None
    d = (value - limit_value) if op == ">=" else (limit_value - value)
    return (d / abs(limit_value) if limit_value != 0 else d) + 0.0        # + 0.0 turns -0.0 into 0.0


def margin_text(m, limit_value, unit="", digits=0):
    """A margin as text: a percentage, or for a limit of 0 the signed distance in the claim's unit ("-0.74 abs")."""
    if m is None:
        return ""
    if limit_value == 0:
        return f"{m:+.3g}" + (f" {unit}" if unit and unit != "-" else "") + " abs"
    return f"{m:+.{digits}%}"


# ---------------------------------------------------------------- calling a calculation
_modules = {}


def load_function(script, function, repo_root):
    """Import `script` (repo-relative) without running its __main__ block and return `function`."""
    path = (Path(repo_root) / script).resolve()
    if path not in _modules:
        if not path.exists():
            raise ProofError(f"script not found: {script}")
        spec = importlib.util.spec_from_file_location(f"_proofcalc_{len(_modules)}", path)
        mod = importlib.util.module_from_spec(spec)
        for extra in (str(path.parent), str(Path(__file__).resolve().parent)):
            if extra not in sys.path:
                sys.path.insert(0, extra)
        spec.loader.exec_module(mod)
        _modules[path] = mod
    fn = getattr(_modules[path], function, None)
    if fn is None:
        raise ProofError(f"{script} has no function {function}()")
    return getattr(fn, "__wrapped_calc__", fn)


def call_calc(calc, value_of, repo_root):
    """Run one calculation node. value_of(node_id) -> value. Returns ({output: value}, {arg: value used})."""
    used = {arg: value_of(ref) for arg, ref in calc["inputs"].items()}
    result = load_function(calc["script"], calc["function"], repo_root)(**used)
    if not isinstance(result, dict):
        names = list(calc.get("outputs") or {}) or ["value"]
        if len(names) != 1:
            raise ProofError(f"{calc['id']}: function returned one value but declares outputs {names}")
        result = {names[0]: result}
    return result, used


# ---------------------------------------------------------------- the Kit an analysis script uses
class Kit:
    """Collects the nodes one analysis script emits and writes them to claims.json."""

    def __init__(self, script_file, params=(), out=None):
        self.script = Path(script_file).resolve()
        self.repo_root = redesign_root(self.script).parent
        self.out = self.script.parent / out if out else self.script.with_name("claims.json")   # out: relative to the script
        self.param_files = list(params)
        self.nodes = {}            # id -> node, in declaration order
        self._funcs = {}           # calc id -> python function
        self._params = {}
        for p in self.param_files:
            self._params.update(load_params(self.script.parent / p))
        self._others = None        # claims from other claims.json files, loaded on first unknown reference

    # ---- declarations (each returns the node dict) ----
    def _add(self, node):
        if node["id"] in self.nodes:
            raise ProofError(f"duplicate id {node['id']} in {self.script.name}")
        self.nodes[node["id"]] = {k: v for k, v in node.items() if v not in (None, [], {})}
        return self.nodes[node["id"]]

    def requirement(self, id, title, text, ref=None, cites=()):
        return self._add({"id": id, "type": "requirement", "title": title, "text": text, "ref": ref, "cites": list(cites)})

    def source(self, id, title, kind, url=None, checked=None, where=None, note=None, status=None):
        return self._add({"id": id, "type": "source", "title": title, "kind": kind, "url": url, "checked": checked,
                          "where": where, "note": note, "status": status})

    def assumption(self, id, title, text, basis, value=None, unit=None, status="PROPOSED", cites=()):
        return self._add({"id": id, "type": "assumption", "title": title, "text": text, "basis": basis, "value": value,
                          "unit": unit, "status": status, "cites": list(cites)})

    def test(self, id, title, verifies, state="planned", procedure=None, result=None, measured=None, date=None,
             evidence=None, note=None):
        return self._add({"id": id, "type": "test", "title": title, "verifies": list(verifies), "state": state,
                          "procedure": procedure, "result": result, "measured": measured, "date": date,
                          "evidence": evidence, "note": note})

    def calc(self, id, inputs, equation=None, units=None, title=None, tol=None, assumes=(), cites=(), output="value"):
        """Decorator: register a calculation. The function returns {output name: value}, or one number that is
        stored under `output`. The function stays callable as normal Python."""
        def wrap(fn):
            self._add({"id": id, "type": "calculation", "title": title or fn.__name__.replace("_", " "),
                       "script": self.script.relative_to(self.repo_root).as_posix(), "function": fn.__name__,
                       "equation": equation, "inputs": dict(inputs), "units": dict(units or {}), "tol": tol,
                       "assumes": list(assumes), "cites": list(cites), "outputs": {}, "_output": output})
            self._funcs[id] = fn
            return fn
        return wrap

    def claim(self, id, title, calc=None, output=None, unit="-", limit=None, verifies=(), parts=(), how=None,
              assumes=(), cites=(), value=None, status=None, note=None):
        """limit = (">=" | "<=", number or node id). Without calc the claim is PROPOSED and needs value=."""
        lim = None
        if limit:
            op, v = limit
            lim = {"op": op, "ref": v} if isinstance(v, str) else {"op": op, "value": v}
        return self._add({"id": id, "type": "claim", "title": title, "calc": calc, "output": output, "unit": unit,
                          "limit": lim, "verifies": list(verifies), "parts": list(parts), "how": how,
                          "assumes": list(assumes), "cites": list(cites), "value": value, "status": status,
                          "note": note})

    # ---- evaluation ----
    def _other_claims(self):
        if self._others is None:
            self._others = {}
            for f in sorted(redesign_root(self.script).rglob("claims*.json")):
                if f.resolve() == self.out.resolve() or "out" in f.parts:
                    continue
                for n in json.loads(f.read_text(encoding="utf-8")).get("nodes", []):
                    self._others[n["id"]] = n
        return self._others

    def value(self, ref):
        """Current value of a node id (computing a local claim's calculation if needed)."""
        if ref in self._params:
            return self._params[ref]["value"]
        node = self.nodes.get(ref)
        if node is None:
            node = self._other_claims().get(ref)
            if node is None:
                raise ProofError(f"{self.script.name}: unknown reference {ref}")
            return node["value"]
        if node["type"] == "claim" and "calc" in node:
            return self._run(node["calc"])[node["output"]]
        if "value" not in node:
            raise ProofError(f"{ref} has no value")
        return node["value"]

    def _run(self, calc_id, _stack=()):
        calc = self.nodes[calc_id]
        if calc.get("_done"):
            return calc["outputs"]
        if calc_id in _stack:
            raise ProofError(f"calculation cycle: {' -> '.join(_stack + (calc_id,))}")
        used = {arg: self.value(ref) for arg, ref in calc["inputs"].items()}
        res = self._funcs[calc_id](**used)
        if not isinstance(res, dict):
            res = {calc["_output"]: res}
        calc["outputs"], calc["input_values"], calc["_done"] = res, used, True
        return res

    def write(self, quiet=False):
        """Run every calculation, fill claim values and write claims.json. Returns the path."""
        for nid, n in self.nodes.items():
            if n["type"] == "calculation":
                self._run(nid)
        lines = []
        for n in self.nodes.values():
            if n["type"] != "claim":
                continue
            if "calc" in n:
                if n["calc"] not in self.nodes:
                    raise ProofError(f"{n['id']}: calc {n['calc']} is not declared in this script")
                outs = self.nodes[n["calc"]]["outputs"]
                if n.get("output") not in outs:
                    raise ProofError(f"{n['id']}: output '{n.get('output')}' not in {sorted(outs)}")
                n["value"] = outs[n["output"]]
            if "value" not in n:
                raise ProofError(f"{n['id']}: no calc and no value")
            m = None
            if n.get("limit"):
                lv = n["limit"].get("value", None)
                lv = self.value(n["limit"]["ref"]) if lv is None else lv
                m = margin(n["value"], lv, n["limit"]["op"])
            lines.append(f"  {n['id']:<22} {fmt(n['value'], n['unit']):>14}"
                         + (f"   margin {margin_text(m, lv, n['unit'])}" if m is not None else "")
                         + ("   FAILS" if m is not None and m < 0 else ""))
        for n in self.nodes.values():
            n.pop("_done", None)
            n.pop("_output", None)
        doc = {"schema": SCHEMA, "generated_by": self.script.relative_to(self.repo_root).as_posix(),
               "params": self.param_files, "nodes": list(self.nodes.values())}
        self.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if not quiet:
            print(f"{repo_rel(self.out)}: {sum(n['type'] == 'claim' for n in self.nodes.values())} claims")
            print("\n".join(lines))
        return self.out
