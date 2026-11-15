"""Collect the C4 round 2026-11-14 option runs from the sim cache: three-mesh station modes, Richardson, GCI,
separation for each rpm set (as CALC-C4-SIM-MODES: extrapolated f1 + the next two station modes of L3).
python -I collect.py -> out/modes_summary.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE))
import fin_structures_d3 as d3  # noqa: E402
import sim_fin as S  # noqa: E402
from opts import CASES, RPM_SETS, modal_inputs  # noqa: E402


def sep(fs, rpm):
    pts = d3.forcing(*rpm)
    return min(abs(f / v - 1) for f in fs for v in pts.values())


def nearest(fs, rpm):
    pts = d3.forcing(*rpm)
    return min(((abs(f / v - 1), n, round(v, 1)) for f in fs for n, v in pts.items()))


def lv_modes(case, side, lv):
    g, k, a3, _ = modal_inputs(case)
    f = S.CACHE / (S._key("modes", {"g": g, "k": k, "side": side, "level": lv, "a3": a3}) + ".json")
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    return [x for x, ke, kind in r["modes"] if ke >= 0.10], [kind for x, ke, kind in r["modes"] if ke >= 0.10], r


out = {}
for case in CASES:
    if case.endswith("_c10"):
        continue
    res = {}
    for side in ("lower", "upper"):
        lvls = [lv_modes(case, side, lv) for lv in (1, 2, 3)]
        if any(x is None for x in lvls):
            res[side] = {"levels": [None if x is None else round(x[0][0], 2) for x in lvls]}
            continue
        f1 = [x[0][0] for x in lvls]
        p, ext, gci = S.richardson(f1, 2 ** 0.5)
        st3 = lvls[2][0]
        res[side] = {"f1": [round(v, 2) for v in f1], "ext": ext, "gci": gci, "order": p,
                     "ndof": [x[2]["n_dof"] for x in lvls], "kinds_L3": lvls[2][1][:3],
                     "next_L3": [round(v, 1) for v in st3[1:3]],
                     "sep": {n: sep([ext] + st3[1:3], r) for n, r in RPM_SETS.items()},
                     "nearest": {n: nearest([ext] + st3[1:3], r) for n, r in RPM_SETS.items()}}
    if all("sep" in res.get(s, {}) for s in ("lower", "upper")):
        res["sep_min"] = {n: min(res[s]["sep"][n] for s in ("lower", "upper")) for n in RPM_SETS}
        res["f1_min"] = min(res[s]["ext"] for s in ("lower", "upper"))
    l2 = lv_modes(case, "lower", 2)
    if l2:
        res["lower_L2"] = l2[0][0]
    out[case] = res
base_l2 = out["base"].get("lower_L2")
for case, r in out.items():
    if "lower_L2" in r and base_l2:
        r["gain_L2_lower"] = r["lower_L2"] / base_l2 - 1
        r["f1_lo_ext_by_gain"] = 228.67671317681624 * (1 + r["gain_L2_lower"])
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "modes_summary.json").write_text(json.dumps(out, indent=1, default=float))
for case, r in out.items():
    print(case, {s: (round(r[s]["ext"], 2), round(r[s]["gci"], 4)) if "ext" in r.get(s, {}) else r.get(s)
                 for s in ("lower", "upper")},
          {n: round(v, 3) for n, v in r.get("sep_min", {}).items()}, round(r.get("gain_L2_lower", 0), 4))
