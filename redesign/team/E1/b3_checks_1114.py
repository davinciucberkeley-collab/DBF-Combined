"""E1 design round 2026-11-14: B3's 9 deg cant / face_ahead 12 mm and the 1.4 W transition-entry thrust.

Run:  python -I redesign/team/E1/b3_checks_1114.py  -> b3_checks_1114.json beside this file + printed table
Uses design_round_1114.py (fast limiter, same equations as propulsion.py). Static thrust (V = 0): the pitch-over
starts from hover, and inflow lowers thrust per rpm, so this is the entry point, not the whole manoeuvre.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design_round_1114 as d  # noqa: E402
p = d.p

out = {}
# ---- 1. 9 deg cant, face_ahead 0.012
gi = dict(d.k.nodes["CALC-E1-TIP-GAP"]["input_values"], cant=9.0, ahead=0.012)
tg = p.tip_gap(**gi)
out["gap_9deg_12mm"] = {"gap_m": tg["gap_m"], "ahead_needed_m": tg["ahead_needed_m"]}
tw9 = {}
for pr in ("11x5.5MR", "11x5.5E"):
    for L in (73.0, 95.0, 100.0):
        for b in (1, 2):
            for st in ("fresh", "worst"):
                q = d.lim(pr, st, b, L, 9.0)
                tw9[f"{pr}_L{L:g}_b{b}_{st}"] = {"tw": q["tw"], "Iw": q["I_m_A"]}
out["tw_9deg"] = tw9

# ---- 2. transition entry at 1.4 W (total thrust vector; per motor along its canted axis)
W = d.m * d.g
res = {}
for c in (7.0, 9.0):
    T = 1.4 * W / (d.n * math.cos(math.radians(c)))
    for pr in ("11x5.5MR", "11x5.5E"):
        rpm = p.bisect(lambda r: p.prop_tp(pr, r, 0.0, d.rho, d.kT, d.kP)[0] - T, 1000.0, 20000.0)
        for chem, rg in (("lipo", None), ("li", d.LI["r_grp"]), ("li", d.LI["r_grp_max"])):
            for st in ("fresh", "worst"):
                for b in (1, 2):
                    voc, r, rmk = d.states(chem, rg)[st]
                    rmk = d.rm2 if b == 2 else rmk
                    q = d.point(pr, rpm, voc, r, rmk)
                    key = f"{c:g}deg_{pr}_{chem}{'' if rg is None else '%.1f' % (rg * 1000)}_{st}_b{b}"
                    res[key] = None if q is None else {
                        "T_per_motor_gf": T / d.g * 1000, "rpm": rpm, "I_wind_A": q["I_m_A"], "I_esc_A": q["I_bat_A"],
                        "I_pack_A": q["Ipack"], "V_bus": q["Vbus"], "duty": q["duty"], "reachable": q["duty"] <= 1.0}
out["transition_1p4W"] = res

if __name__ == "__main__":
    def cl(o):
        if isinstance(o, dict):
            return {a: cl(b) for a, b in o.items()}
        return round(o, 4) if isinstance(o, float) else o
    out = cl(out)
    (HERE / "b3_checks_1114.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["gap_9deg_12mm"]))
    for kk, v in out["tw_9deg"].items():
        print(kk, v)
    for kk, v in out["transition_1p4W"].items():
        print(kk, v and {a: v[a] for a in ("T_per_motor_gf", "I_wind_A", "I_pack_A", "V_bus", "duty")})
