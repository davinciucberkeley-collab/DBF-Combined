"""Run ONE stress job of sim_fin.py into the shared cache (R5: lets every mesh level run in its own process).
python -I run_job.py <side> <level 1|2|3|G> <variant drawn|proposed>; then python -I ../sim_fin.py collects the cache."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

side, lv, var = sys.argv[1], sys.argv[2], sys.argv[3]
lv = lv if lv == "G" else int(lv)
kit = S.kit
t0 = time.time()
kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-FACE"]["inputs"].items()}
g, k = S._split(kw)
S.su2_quarter(g, k, side, lv, var)
print("JOB DONE", side, lv, var, round(time.time() - t0), flush=True)
