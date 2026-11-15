"""C5 design round 2026-11-14: confirm the candidate broadside levers at the production time step (dt 40 us).
Run:  python -I redesign/team/C5/dr1114/confirm.py  -> dr1114/out/confirm.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import broadside_levers as B  # noqa: E402

L = B.L
inp = L.inputs()
m = inp["m_a3"]
Vs = [round(4.0 + 0.1 * k, 2) for k in range(26)]       # 4.0 .. 6.5 m/s
runs = [B.run(inp, m, "baseline", Vs, 4e-5),
        B.run(inp, m, "stance +z feet +25 mm", Vs, 4e-5, geo={"dz_pos": 0.025}),
        B.run(inp, m, "stance +z feet +30 mm", Vs, 4e-5, geo={"dz_pos": 0.030}),
        B.run(inp, m, "heading: belly to wind (az 180)", Vs, 4e-5, az_deg=180.0),
        B.run(inp, m, "heading: belly to wind -30 deg (az 150)", Vs, 4e-5, az_deg=150.0),
        B.run(inp, m, "heading: belly to wind +30 deg (az 210)", Vs, 4e-5, az_deg=210.0),
        B.run(inp, m, "drift 0.15 m/s", Vs, 4e-5, drift=0.15),
        B.run(inp, inp["m_gate"], "belly to wind, gate mass 2.6 kg", Vs, 4e-5, az_deg=180.0),
        B.run(inp, inp["m_gate"], "baseline, gate mass 2.6 kg", Vs, 4e-5)]
(HERE / "out" / "confirm.json").write_text(json.dumps({"mass_kg": m, "runs": runs}, indent=1))
