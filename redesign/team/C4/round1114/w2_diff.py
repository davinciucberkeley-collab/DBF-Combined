"""C4 wave 2: claim values before (copy of the claims files at wave-2 start) -> now, with limits and pass flags.
python -I w2_diff.py <before_dir>   (compares claims.d3.json and claims.sim.json beside team/C4)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
before = Path(sys.argv[1])
for f in ("claims.d3.json", "claims.sim.json"):
    a = {n["id"]: n for n in json.loads((before / f).read_text(encoding="utf-8"))["nodes"] if n["type"] == "claim"}
    b = {n["id"]: n for n in json.loads((HERE.parent / f).read_text(encoding="utf-8"))["nodes"] if n["type"] == "claim"}
    print("==", f)
    for cid in b:
        vb = b[cid].get("value")
        va = a.get(cid, {}).get("value")
        if not isinstance(vb, (int, float)):
            continue
        if isinstance(va, (int, float)) and abs(vb - va) <= 1e-4 * max(abs(va), 1e-12):
            continue
        lim = b[cid].get("limit") or {}
        lv = lim.get("resolved", lim.get("value", lim.get("ref")))
        print(f"{cid:40s} {va!s:>24.10} -> {vb:<14.6g} {lim.get('op', '')} {lv!s:.10}")
