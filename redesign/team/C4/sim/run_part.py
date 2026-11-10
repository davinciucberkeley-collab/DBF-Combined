"""Run one part of sim_fin.py into the shared cache (lets the three slow parts run in parallel).
python -I run_part.py stress | su2 | modes ; then python -I ../sim_fin.py collects everything from the cache."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

part = sys.argv[1]
kit = S.kit
t0 = time.time()
if part in ("stress", "su2"):
    kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-FACE"]["inputs"].items()}
    g, k = S._split(kw)
    if part == "su2":
        S.su2_quarter(g, k, "upper", 1, "drawn")
    else:
        jobs = [("upper", 1, "proposed"), ("upper", 2, "drawn"), ("upper", 2, "proposed"), ("lower", 2, "drawn"),
                ("lower", 2, "proposed"), ("upper", 3, "drawn"), ("upper", 3, "proposed"), ("upper", "G", "drawn")]
        for side, lv, var in jobs:
            S.su2_quarter(g, k, side, lv, var)
            print("done", side, lv, var, round(time.time() - t0), flush=True)
elif part == "modes":
    kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
    S.modes3d(**kw)
print("PART DONE", part, round(time.time() - t0), flush=True)
