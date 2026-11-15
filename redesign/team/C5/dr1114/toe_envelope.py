"""C5 design round 2026-11-14: does a +z pad toe-out change the hard-landing envelope (stroke, side load, n)?
Run:  python -I redesign/team/C5/dr1114/toe_envelope.py  -> dr1114/out/toe_envelope.json
Gate mass, sink requirements.landing_sink_ms, tilt <= err in 24 directions (landing_sim3d.disc_cases), mu 0.40,
for dz_pos 0 / 20 / 25 mm (pivot edge of the two +z feet moved outboard)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import broadside_levers as B  # noqa: E402  (patches landing_sim3d.geometry)

L = B.L
inp = L.inputs()
m = inp["m_gate"]
out = {}
for dz in (0.0, 0.020, 0.025):
    B.PATCH.update(dz_pos=dz, dz_neg=0.0)
    cs = L.disc_cases(inp, m, m / inp["m_a3"], inp["lam"], inp["v_sink"])
    r = L.simulate(inp, cs)
    s = L.summarise(cs, r)
    out["%.0f mm" % (dz * 1e3)] = {k: s[k] for k in ("stroke_max_m", "n_peak_max", "side_1ms_max_N", "side_peak_max_N",
                                                    "tip_min_m", "tilt_max_deg", "tipped")}
    print(dz, out["%.0f mm" % (dz * 1e3)], flush=True)
(HERE / "out" / "toe_envelope.json").write_text(json.dumps(out, indent=1))
