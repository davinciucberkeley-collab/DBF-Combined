"""C5: convergence and contact-model sensitivity of the sustained foot side load on the governing non-bottomed case.
Run after landing_sim3d.py:  python -I redesign/team/C5/sim/side_check.py  -> out/side_check.json (about 2 min)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import landing_sim3d as L  # noqa: E402

S = json.loads((HERE / "out" / "sim3d.json").read_text())
inp = L.inputs()
us = inp["s_av"] - inp["guard"]
rows = [r for r in S["hard_envelope"]["gate"]["rows"] if r[2] <= us]
r = max(rows, key=lambda r: r[4])
m = inp["m_gate"]
case = dict(m=m, I_scale=m / inp["m_a3"], theta=r[0], phi=r[1], v_sink=inp["v_sink"], lam=inp["lam"])
out = {"case": case, "dt": {}, "sens": {}}
for dt in (8e-5, 4e-5, 2e-5, 1e-5):
    x = L.simulate(inp, [case], dt=dt)
    out["dt"][str(dt)] = {"side_1ms_N": max(x["side_1ms"][0]), "stroke_m": max(x["s_max"][0])}
for name, kw in (("k_pad x0.5", dict(k_pad=L.K_PAD / 2)), ("k_pad x2", dict(k_pad=L.K_PAD * 2)),
                 ("m_piston x2", dict(m_f=2 * inp["m_piston"])), ("eps_v x0.5", dict(eps_v=L.EPS_V / 2)),
                 ("mu 0.5", None)):
    c = dict(case, mu=0.5) if kw is None else case
    x = L.simulate(inp, [c], **(kw or {}))
    out["sens"][name] = {"side_1ms_N": max(x["side_1ms"][0]), "stroke_m": max(x["s_max"][0])}
print(json.dumps(out, indent=1))
(HERE / "out" / "side_check.json").write_text(json.dumps(out, indent=1))
