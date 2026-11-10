"""Sensitivity of the L4 tip results to the collar-tail tongue modulus (ASM-C4-SIM-TAIL-E), mesh level 1, hex8 only.
python -I sens_tail.py -> out/sens_tail.json"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

S.SU2_LEVELS = ()
kit = S.kit
kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-FACE"]["inputs"].items()}
g, k = S._split(kw)
out = {}
for e in (1e7, 2e8, 1e9, 2e9):
    for var in ("drawn", "proposed"):
        r = S.su2_quarter(g, dict(k, e_tail=e), "upper", 1, var)
        out[f"{var}_{e:.0e}"] = {s: {q: r["L4"][s][q] for q in ("hotspot_lim", "peak_lim", "far_lim", "strip_lim",
                                                                 "foot_defl")} for s in "+-"}
        print(var, e, {q: round(v, 5) for q, v in out[f"{var}_{e:.0e}"]["+"].items()}, flush=True)
(S.OUT / "sens_tail.json").write_text(json.dumps(out, indent=1))
