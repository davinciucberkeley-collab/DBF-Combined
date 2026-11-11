"""C5-R6: free-drop (no rotor lift) height for the aircraft corner drop of T-C5-AIRCRAFT-DROP: the largest pad-to-floor
height at which a 10 deg touchdown in any of 24 directions stays inside the usable stroke, gate mass, D-62 CG.
Run:  python -I redesign/team/C5/sim/test_height.py  -> out/test_height.json (about 2 min)."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import landing_sim3d as L  # noqa: E402

inp = L.inputs()
us = inp["s_av"] - inp["guard"]
m = inp["m_gate"]
hs = [0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060, 0.065, 0.0734]
cs = []
for h in hs:
    cs += L.disc_cases(inp, m, m / inp["m_a3"], 0.0, math.sqrt(2 * L.G0 * h), mags=(inp["err"],), n_az=24)
r = L.simulate(inp, cs)
rows = []
for i, h in enumerate(hs):
    sub = range(24 * i, 24 * i + 24)
    rows.append({"h_m": h, "stroke_m": max(max(r["s_max"][j]) for j in sub), "n": max(r["n_peak"][j] for j in sub)})
ok = [x["h_m"] for x in rows if x["stroke_m"] <= us]
out = {"rows": rows, "h_max_m": max(ok) if ok else None, "usable_m": us}
print(json.dumps(out, indent=1))
(HERE / "out" / "test_height.json").write_text(json.dumps(out, indent=1))
