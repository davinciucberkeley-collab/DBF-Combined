"""C5 design round 2026-11-14: broadside landing-wind levers on the 6-DOF touchdown model (sim/landing_sim3d.py).

Run:  python -I redesign/team/C5/dr1114/broadside_levers.py [quick]   -> dr1114/out/broadside_levers.json
Uses the live inputs (landing_sim3d.inputs()) and the unchanged physics (landing_sim3d.simulate()). Levers are applied
as in-script overrides only; no shared file is edited:
  * stance: pad pivot edge z_outer moved outboard, on the +z (pod-side) feet only or on all four (asymmetric geometry
    patched in here; landing_sim3d.geometry() is symmetric);
  * pad face friction mu (<= 0.40 cap, D-105);
  * touchdown drift ASM-C5-TD-DRIFT (0.3 m/s) and sink rate;
  * heading: lean azimuth, i.e. which face the wind blows on (0 deg = pod (+z) face to the wind = the claim's case,
    180 deg = belly (-z) face to the wind, 90 deg = wingtip to the wind).
The wind cases copy landing_sim3d.main() section 3: touchdown tilt = lean(V) + err toward the pad line, drift v_td the
same way, lull (wind gone) and steady wind, sink 0.5 and requirements.landing_sink_ms.
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
import landing_sim3d as L  # noqa: E402

_geometry0 = L.geometry
PATCH = {"dz_pos": 0.0, "dz_neg": 0.0}


def geometry(inp, m, I_scale=1.0):
    """landing_sim3d.geometry with the +z and -z pad pivot edges moved outboard by dz_pos / dz_neg (pad size kept)."""
    g = _geometry0(inp, m, I_scale)
    feet, corners = g["feet"].copy(), g["corners"].copy()
    for f, sz in enumerate((1, 1, -1, -1)):                     # UR, UL, LR, LL
        d = PATCH["dz_pos"] if sz > 0 else PATCH["dz_neg"]
        feet[f, 2] += sz * d
        corners[f, :, 2] += sz * d
    g["feet"], g["corners"] = feet, corners
    return g


L.geometry = geometry


def cases_for(inp, m, Vs, az_deg=0.0, mu=None, drift=None, sinks=None, modes=("lull", "steady")):
    """Wind cases as landing_sim3d.main() section 3 (broadside), lean toward azimuth az from the +z pad line.
    Lean is computed with the full broadside area at every azimuth (conservative off the pure broadside)."""
    S_b = inp["span"] * inp["chord"]
    vtd = inp["v_td"] if drift is None else drift
    sinks = sinks or (inp["v_normal"], inp["v_sink"])
    a = math.radians(az_deg)
    out, keys = [], []
    for mode in modes:
        for vs in sinks:
            for V in Vs:
                tilt = L.lean_deg(inp, V, S_b, m) + inp["err"]
                D = 0.5 * inp["rho"] * V * V * S_b * inp["cd90"] if mode == "steady" else 0.0
                # +theta lowers the +z feet (world +X); +phi rotates about world X; a lean toward world -Y is phi > 0
                c = dict(m=m, I_scale=m / inp["m_a3"], theta=tilt * math.cos(a), phi=tilt * math.sin(a), v_sink=vs,
                         lam=inp["lam"], drift=(vtd * math.cos(a), -vtd * math.sin(a)),
                         wind=(-D * math.cos(a), D * math.sin(a)))
                if mu is not None:
                    c["mu"] = mu
                out.append(c)
                keys.append(("%s/%.1f" % (mode, vs), V, tilt))
    return out, keys


def limits(res, keys):
    tab = {}
    for i, (k, V, tilt) in enumerate(keys):
        tab.setdefault(k, []).append((V, tilt, bool(res["tipped"][i]), res["tilt_max"][i]))
    out = {}
    for k, rows in tab.items():
        first = next((j for j, r in enumerate(rows) if r[2]), None)
        vlim = rows[-1][0] if first is None else (rows[first - 1][0] if first > 0 else 0.0)
        out[k] = {"v_limit_ms": vlim, "tilt_tip_deg": None if first is None else rows[first][1],
                  "tilt_hold_deg": rows[first - 1][1] if first else rows[-1][1]}
    lull = [out[k]["v_limit_ms"] for k in out if k.startswith("lull")]
    return {"by_mode": out, "v_claim_ms": min(lull), "v_all_ms": min(v["v_limit_ms"] for v in out.values())}


def run(inp, m, label, Vs, dt, **kw):
    t0 = time.time()
    geo = kw.pop("geo", {})
    PATCH.update({"dz_pos": 0.0, "dz_neg": 0.0}, **geo)
    cs, keys = cases_for(inp, m, Vs, **kw)
    res = L.simulate(inp, cs, dt=dt, t_end=2.0)
    r = limits(res, keys)
    r.update(label=label, geo=dict(PATCH), kw={k: v for k, v in kw.items()}, dt=dt, runtime_s=time.time() - t0)
    print("%-38s claim %.2f  all %.2f   %s  (%.0f s)" % (label, r["v_claim_ms"], r["v_all_ms"],
          {k: v["v_limit_ms"] for k, v in r["by_mode"].items()}, r["runtime_s"]), flush=True)
    return r


def main():
    quick = "quick" in sys.argv
    inp = L.inputs()
    m = inp["m_a3"]                                   # the claim's mass (A3 basic, as landing_sim3d section 3)
    dt = 8e-5 if quick else 4e-5
    Vs = [round(3.5 + 0.1 * k, 2) for k in range(36)]  # 3.5 .. 7.0 m/s, 0.1 m/s grid (claim grid is 0.5)
    out = {"inputs": {k: v for k, v in inp.items() if k != "planar"}, "mass_kg": m, "dt": dt, "runs": []}
    R = out["runs"]
    R.append(run(inp, m, "baseline", Vs, dt))
    for dz in (0.010, 0.020, 0.030):
        R.append(run(inp, m, "stance +z feet +%d mm" % (dz * 1e3), Vs, dt, geo={"dz_pos": dz}))
    for mu in (0.30, 0.20, 0.10):
        R.append(run(inp, m, "pad mu %.2f" % mu, Vs, dt, mu=mu))
    for d in (0.15, 0.0):
        R.append(run(inp, m, "drift %.2f m/s" % d, Vs, dt, drift=d))
    R.append(run(inp, m, "sink 0.3 m/s", Vs, dt, sinks=(0.3,)))
    for az in (180.0, 150.0, 120.0, 90.0, 60.0, 30.0):
        R.append(run(inp, m, "heading: lean azimuth %d deg" % az, Vs, dt, az_deg=az))
    (HERE / "out" / ("broadside_levers%s.json" % ("_quick" if quick else ""))).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
