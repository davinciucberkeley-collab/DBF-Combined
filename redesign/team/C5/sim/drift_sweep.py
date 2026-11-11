"""C5-R6: hard landing with touchdown drift. Largest sink speed at which a 10 deg touchdown (8 attitudes) drifting
ASM-C5-TD-DRIFT (0.3 m/s) in 8 directions stays inside the usable stroke, gate and A3-predicted mass.
Run after landing_sim3d.py:  python -I redesign/team/C5/sim/drift_sweep.py  -> out/drift_sweep.json (a few minutes)."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import landing_sim3d as L  # noqa: E402

inp = L.inputs()
us = inp["s_av"] - inp["guard"]
e = inp["err"]
atts = [(e * math.cos(k * math.pi / 4), e * math.sin(k * math.pi / 4)) for k in range(8)]
dirs = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]
out = {}
for tag, m in (("A3 predicted", inp["m_pred"]), ("gate", inp["m_gate"])):
    vs = [0.9, 1.0, 1.1, 1.2]
    cs = [dict(m=m, I_scale=m / inp["m_a3"], theta=a, phi=b, v_sink=v, lam=inp["lam"],
               drift=(inp["v_td"] * dx, inp["v_td"] * dy)) for v in vs for (a, b) in atts for (dx, dy) in dirs]
    r = L.simulate(inp, cs, t_end=0.4)
    rows = []
    for i, v in enumerate(vs):
        sub = range(64 * i, 64 * i + 64)
        rows.append({"v": v, "stroke_m": max(max(r["s_max"][j]) for j in sub),
                     "n": max(r["n_peak"][j] for j in sub), "side_N": max(max(r["side_1ms"][j]) for j in sub)})
    ok = [x["v"] for x in rows if x["stroke_m"] <= us]
    out[tag] = {"rows": rows, "v_max_ms": max(ok) if ok else None}
    print(tag, rows, "v_max", out[tag]["v_max_ms"], flush=True)
(HERE / "out" / "drift_sweep.json").write_text(json.dumps(out, indent=1))
