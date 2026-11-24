"""C4 round 2026-11-14: re-run every calc of fin_structures_d3.py (shell/beam model: fin, mount, collar margins)
with the tube inputs overridden in memory. Does not write claims.d3.json.
python -I d3_opts.py <case>  -> out/d3_<case>.json (claim id -> value, limit, pass)"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import fin_structures_d3 as d3  # noqa: E402
from opts import CASES  # noqa: E402

case = sys.argv[1]
kit = d3.kit
c = CASES[case]
over = {}
gmap = {"od": "P:fins.tube.od_m", "idd": "P:fins.tube.id_m", "mu": "P:wing.spar.mass_per_m_kgm"}
for n, v in c.get("g", {}).items():
    if n in gmap:
        over[gmap[n]] = v
for n, v in c.get("k", {}).items():
    over[{"E": "ASM-J1-E-TUBE", "G": "ASM-C4-G-TUBE"}[n]] = v
over.update(c.get("params", {}))
for ref, v in over.items():
    if ref not in kit._params:
        print("note: not a param key of d3, injected:", ref)
    kit._params[ref] = {"value": v}
t0 = time.time()
for nid, n in kit.nodes.items():
    if n["type"] == "calculation":
        kit._run(nid)
out = {}
for nid, n in kit.nodes.items():
    if n["type"] != "claim" or "calc" not in n:
        continue
    v = kit.nodes[n["calc"]]["outputs"].get(n["output"])
    lim = n.get("limit")
    ok = None
    if lim and isinstance(v, (int, float)):
        lv = lim.get("value", None)
        lv = kit.value(lim["ref"]) if lv is None else lv
        ok = v >= lv if lim["op"] == ">=" else v <= lv
        lim = [lim["op"], lv]
    out[nid] = {"value": v, "limit": lim, "pass": ok}
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / f"d3_{case}.json").write_text(json.dumps({"case": case, "override": over, "claims": out},
                                                           indent=1, default=float))
print("D3 done", case, round(time.time() - t0), "s", flush=True)
