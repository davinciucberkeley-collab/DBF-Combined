"""C5: largest sink speed for which a 10 deg touchdown in ANY direction stays inside the usable stroke, per mass.
Run after landing_sim3d.py:  python -I redesign/team/C5/sim/sink_sweep.py  -> out/sink_sweep.json (about 5 min)."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import landing_sim3d as L  # noqa: E402

inp = L.inputs()
usable = inp["s_av"] - inp["guard"]
out = {}
for tag, m in (("A3 basic", inp["m_a3"]), ("gate", inp["m_gate"])):
    cs, vs = [], [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
    for v in vs:
        cs += L.disc_cases(inp, m, m / inp["m_a3"], inp["lam"], v, mags=(inp["err"],), n_az=24)
    r = L.simulate(inp, cs)
    rows = []
    for i, v in enumerate(vs):
        sub = range(24 * i, 24 * i + 24)
        rows.append({"v": v, "stroke_m": max(max(r["s_max"][j]) for j in sub),
                     "n": max(r["n_peak"][j] for j in sub), "side_N": max(max(r["side_1ms"][j]) for j in sub)})
    ok = [x["v"] for x in rows if x["stroke_m"] <= usable]
    out[tag] = {"rows": rows, "v_max_ms": max(ok) if ok else None}
    print(tag, rows, "v_max", out[tag]["v_max_ms"], flush=True)
(HERE / "out" / "sink_sweep.json").write_text(json.dumps(out, indent=1))
