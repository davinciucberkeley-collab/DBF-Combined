"""Compare L4 face results (hex8 quarter) base vs a case, per available level. python -I face_cmp.py <case>"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parent / "sim")); sys.path.insert(0, str(HERE))
import sim_fin as S
from opts import face_inputs
out = {}
for case in ("base", sys.argv[1]):
    g, k = face_inputs(case)
    for side, lv, var in [("upper", 1, "drawn"), ("upper", 2, "drawn"), ("upper", 3, "drawn"), ("upper", 1, "proposed"),
                          ("upper", 2, "proposed"), ("upper", 3, "proposed"), ("upper", "G", "drawn"),
                          ("lower", 2, "drawn"), ("lower", 2, "proposed")]:
        h, hl = S.STRESS_LEVELS[lv]
        key = {"g": g, "k": k, "side": side, "level": lv, "variant": var, "su2": False}
        f = S.CACHE / (S._key("su2q", key) + ".json")
        if not f.exists():
            continue
        r = json.loads(f.read_text())["L4"]
        out[f"{case} {side} L{lv} {var}"] = {q: max(r[s][q] for s in "+-") for q in
                                             ("hotspot_lim", "far_lim", "strip_lim", "foot_defl")}
for n, v in out.items():
    print(n, {q: round(x * (1e3 if q == "foot_defl" else 1e-6), 3) for q, x in v.items()})
(HERE / "out" / f"face_{sys.argv[1]}.json").write_text(json.dumps(out, indent=1))
