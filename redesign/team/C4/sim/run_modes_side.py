"""Run the station-mode ladder of ONE side into the shared cache (lets the two sides run in parallel).
python -I run_modes_side.py upper | lower ; then python -I ../sim_fin.py collects everything from the cache."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

side = sys.argv[1]
kit = S.kit
kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-MODES"]["inputs"].items()}
g = {n: kw[n] for n in S.GEOM}
k = {n: kw[n] for n in S.MATS}
k.update({n: g[n] for n in ("e_face", "e_core", "g_core", "e_strip")})
for n in ("e_tail", "e_link", "e_shoe", "glue", "leg_depth", "collar_len", "z0_prop", "tail_len", "tongue_depth"):
    k[n] = kw[n]
k["leg_depth"] = S.LEG_STIFF
k["t_face"] = g["t_face"]
t0 = time.time()
for lv in (1, 2, 3):
    S.modes_level(g, k, side, lv, kw["a3"])
    print("done", side, lv, round(time.time() - t0), flush=True)
