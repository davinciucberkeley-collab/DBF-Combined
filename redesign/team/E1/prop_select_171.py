"""E1 D-171: prop re-selection against C4's rpm ceiling (cruise and hover <= 6 016 rpm) and the E1 limits.

Run:  python -I redesign/team/E1/prop_select_171.py   -> team/E1/prop_select_171.json (nothing else written)

Uses propulsion.py's station model unchanged (kT, kP fitted on the maker's 11x4.7 rows, ASM-E1-CAL-TRANSFER).
Props: 11x5.5E (flight prop since D-161, B4 file), 11x7E (B4 file; no 11x7EP exists), 11x8E (E1 file data/, the
11x8EP exists). Conditions read from params: gate mass, cant, limiter, download factor, B1 drag via CL-E1-CRUISE-DRAG
plus B2's tripped-wing device drag 0.262 N (review/CLOSURE-ROUND-2026-11-14/B2.md, B2C-3: +14.0 W at 17 m/s).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import propulsion as p  # noqa: E402

N = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}   # E1 claims of record
IV = N["CALC-E1-WORST"]["input_values"]             # resolved params of record (same run)
HV = N["CALC-E1-HOVER"]["input_values"]
CV = N["CALC-E1-CRUISE-V17"]["input_values"]
RX = N["CALC-E1-REXT-ALLOW"]["input_values"]


def load(path, mass):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("rpm"):
                continue
            rows.append([float(v) for v in line.strip().split(",")[:4]])
    return {"static": {int(r[0]): (r[2], r[3]) for r in rows if r[1] == 0.0},
            "J": [[r[1], r[2], r[3]] for r in rows if int(r[0]) == 6000], "mass_g": mass}


p.PROPS["11x7E"] = load(HERE.parent / "B4" / "data" / "apc_per3_11x7E.csv", 22.96)
p.PROPS["11x8E"] = load(HERE / "data" / "apc_per3_11x8E.csv", 22.96)
p.PROP_D["11x7E"] = p.PROP_D["11x8E"] = 0.2794

m, g, rho, cant, ilim = IV["m"], IV["g"], IV["rho"], IV["cant"], IV["ilim"]
kdl = HV["kdl"]
V = CV["V"]
cc = math.cos(math.radians(cant))
kT, kP = N["CL-E1-KT"]["value"], N["CL-E1-KP"]["value"]
kv, rm, i0 = 900.0, 0.086, 0.9
esc = (0.010, 0.5)
D_cruise = N["CL-E1-CRUISE-DRAG"]["value"] + 0.262          # B1 drag + B2 trip device drag
W = m * g
rx = RX["r_ext"] / 1000.0
fresh = (16.8, 4 * 0.004 + rx)
worst = (4 * 3.73, 4 * 0.004 * 1.5 + rx)
tol, band = 0.011, 0.10
RPM_CAP = 6016.0                                             # C4 D-161 option A

out = {"inputs": {"m": m, "cant": cant, "ilim": ilim, "V": V, "D_cruise_N": D_cruise, "kdl": kdl}}
for pr in ("11x5.5E", "11x7E", "11x8E"):
    Th = W * kdl / (4 * cc)
    h = p.at_thrust(pr, Th, 0.0, rho, kT, kP, kv, p.r_hot(rm, 0.00393, 50.0), i0, esc[0], esc[1], 14.8)
    c = p.at_thrust(pr, D_cruise / (4 * cc), V, rho, kT, kP, kv, p.r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
    # thrust at 25 A winding (static): rpm-only, independent of bus and R_m
    r25 = p.bisect(lambda r: p.station(pr, r, 0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], 15.0)["I_m_A"] - 25.0,
                   2000, 15000)
    T25 = p.station(pr, r25, 0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], 15.0)["T_N"]
    f = p.limited(pr, rho, kT, kP, kv, rm * (1 + band), i0, esc, fresh[0], fresh[1], 1.0, 4, ilim * (1 - tol))
    w = p.limited(pr, rho, kT, kP, kv, p.r_hot(rm * (1 + band), 0.00393, 80.0), i0, esc, worst[0], worst[1], 1.0, 4,
                  ilim * (1 - tol))
    hi = p.limited(pr, rho, kT, kP, kv, rm * (1 - band), i0, esc, fresh[0], fresh[1], 1.0, 4, ilim * (1 + tol))
    out[pr] = {"hover_rpm": h["rpm"], "hover_I_pack_A": 4 * h["I_bat_A"] + 1.0, "hover_W": 4 * h["P_bat_W"],
               "cruise_rpm": c["rpm"], "cruise_J": c["J"], "cruise_W": 4 * c["P_bat_W"],
               "cruise_eta_prop": D_cruise * V / (4 * c["P_shaft_W"]),
               "rpm_25A": r25, "tw_at_25A": 4 * T25 * cc / W,
               "tw_fresh_band": 4 * f["T_N"] * cc / W, "I_wind_fresh_band_A": f["I_m_A"],
               "tw_worst_band": 4 * w["T_N"] * cc / W, "I_wind_hi_band_A": hi["I_m_A"],
               "pass_cruise_rpm": c["rpm"] <= RPM_CAP, "pass_hover_rpm": h["rpm"] <= RPM_CAP,
               "pass_tw_at_25A": 4 * T25 * cc / W >= 2.0}

(HERE / "prop_select_171.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
