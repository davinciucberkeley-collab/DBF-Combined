"""E1 design round 2026-11-14 (wave 1, analysis only): limiter value, prop choice, motor cant, Li-ion pack.

Run:  python -I redesign/team/E1/design_round_1114.py   -> design_round_1114.json beside this file + printed tables
Imports propulsion.py's model and its resolved inputs; writes nothing outside team/E1/ (no claims, params or shared
file). Props 11x5.5E and 11x7E: B4's transcriptions of the APC PER3 files (team/B4/data/apc_per3_11x55E.csv,
apc_per3_11x7E.csv), same format as propulsion.PROPS (static rows, J sweep of the 6000 rpm block).

Fast limiter (same equations as propulsion.limited, solved in rpm instead of duty): at a static rpm the station's
battery power P_st = V_m I_m + I_m^2 R_esc + P_esc0 does not depend on the bus; the pack then satisfies
(V_ocv - R I_p)(I_p - I_avn) = n P_st (smaller root), duty = (V_m + I_m R_esc) / V_bus. The operating point is the
highest rpm with I_p <= I_lim and duty <= 1. Checked against propulsion.limited at start (printed).
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import propulsion as p  # noqa: E402

k = p.kit


def load_b4(name):
    rows = []
    with open(HERE.parent / "B4" / "data" / name, encoding="utf-8") as f:
        for r in csv.reader(x for x in f if not x.startswith("#")):
            if r[0] != "rpm":
                rows.append([float(v) for v in r])
    return {"static": {int(r[0]): (r[2], r[3]) for r in rows if r[1] == 0.0},
            "J": [[r[1], r[2], r[3]] for r in rows if int(r[0]) == 6000], "mass_g": 23.0}


p.PROPS["11x5.5E"] = load_b4("apc_per3_11x55E.csv")
p.PROPS["11x7E"] = load_b4("apc_per3_11x7E.csv")
p.PROP_D["11x5.5E"] = p.PROP_D["11x7E"] = 0.2794
PROPS = ["11x5.5MR", "11x4.5MR", "11x5.5E", "11x7E"]

k._run("CALC-E1-WORST")
k._run("CALC-E1-BOUND2")
W_ = k.nodes["CALC-E1-WORST"]["input_values"]
B2 = k.nodes["CALC-E1-BOUND2"]["input_values"]
m, g, n, rho, cant, cells = W_["m"], W_["g"], W_["n"], W_["rho"], W_["cant"], W_["cells"]
kP, kT, kv, rm, i0, esc, pack = W_["kP"], W_["kT"], W_["kv"], W_["rm"], W_["i0"], W_["esc"], W_["pack"]
tc, state, ocv20, r_cell, cold = W_["tc"], W_["state"], W_["ocv20"], W_["r_cell"], W_["cold"]
rx = W_["r_ext"] / 1000.0
rm2 = B2["reff"] - esc[0]
rm_hot = p.r_hot(rm, tc[0], state[0])
I_AVN = pack[1]
I_RATE, TW_MIN, TW_SAG = 25.0, 2.0, 1.6

# Li-ion 4S2P P45B (E2.md section 1.5 inputs, EST; datasheet max DCIR 13.8 mOhm/cell -> 6.9 mOhm per 2P group)
LI = {"ocv_full": 4.20, "ocv20": 3.45, "ocv_fs": 3.30, "r_grp": 0.006, "r_grp_max": 0.0069, "cold": 2.0}


def states(chem="lipo", r_grp=None):
    if chem == "lipo":
        return {"fresh": (cells * 4.20, cells * r_cell + rx, rm),
                "res20_warm": (cells * ocv20, cells * r_cell + rx, rm_hot),
                "worst": (cells * ocv20, cells * r_cell * cold + rx, rm_hot),
                "land_cold": (cells * state[1], cells * r_cell * cold + rx, rm_hot)}
    rg = r_grp or LI["r_grp"]
    return {"fresh": (cells * LI["ocv_full"], cells * rg + rx, rm),
            "res20_warm": (cells * LI["ocv20"], cells * rg + rx, rm_hot),
            "worst": (cells * LI["ocv20"], cells * rg * LI["cold"] + rx, rm_hot),
            "land_cold": (cells * LI["ocv_fs"], cells * rg * LI["cold"] + rx, rm_hot)}


def point(prop, rpm, voc, r, rmk):
    T, Ps, _ = p.prop_tp(prop, rpm, 0.0, rho, kT, kP)
    i_m, v_m, p_m = p.motor_point(rpm, Ps, kv, rmk, i0)
    p_st = p_m + i_m * i_m * esc[0] + esc[1]
    # (voc - r Ip)(Ip - Iavn) = n p_st  ->  r Ip^2 - (voc + r Iavn) Ip + (voc Iavn + n p_st) = 0
    b = voc + r * I_AVN
    disc = b * b - 4 * r * (voc * I_AVN + n * p_st)
    if disc < 0:
        return None
    ip = (b - math.sqrt(disc)) / (2 * r) if r > 0 else I_AVN + n * p_st / voc
    v = voc - r * ip
    return {"T_N": T, "I_m_A": i_m, "Ipack": ip, "Vbus": v, "duty": (v_m + i_m * esc[0]) / v,
            "I_bat_A": p_st / v, "rpm": rpm}


def lim(prop, st, bound, L, c=cant, chem="lipo", r_grp=None):
    voc, r, rmk = states(chem, r_grp)[st]
    rmk = rm2 if bound == 2 else rmk

    def ok(rpm):
        q = point(prop, rpm, voc, r, rmk)
        return q is not None and q["Ipack"] <= L and q["duty"] <= 1.0
    lo, hi = 1000.0, 20000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    q = point(prop, lo, voc, r, rmk)
    q["tw"] = n * q["T_N"] * math.cos(math.radians(c)) / (m * g)
    q["T_gf"] = q["T_N"] / g * 1000
    q["limited"] = q["duty"] < 0.999
    return q


def solve_L(fn, target, lo=30.0, hi=200.0):
    flo, fhi = fn(lo) - target, fn(hi) - target
    if flo * fhi > 0:
        return None
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if (fn(mid) - target) * flo > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def window(prop, c=cant, chem="lipo", r_grp=None):
    res = {}
    for b in (1, 2):
        sts = list(states(chem, r_grp))
        l25 = [solve_L(lambda L, s=s: lim(prop, s, b, L, c, chem, r_grp)["I_m_A"], I_RATE) for s in sts]
        l25v = [x for x in l25 if x is not None]
        lf = solve_L(lambda L: lim(prop, "fresh", b, L, c, chem, r_grp)["tw"], TW_MIN)
        lw = solve_L(lambda L: lim(prop, "worst", b, L, c, chem, r_grp)["tw"], TW_SAG)
        lmax = min(l25v) if l25v else None
        need = [x for x in (lf, lw)]
        lmin = None if None in need else max(need)
        res[f"b{b}"] = {"L_max_25A": lmax, "binding_25A_state": sts[l25.index(lmax)] if lmax else None,
                        "L_min_tw_fresh": lf, "L_min_tw_worst": lw,
                        "tw_fresh_unlim": lim(prop, "fresh", b, 1e4, c, chem, r_grp)["tw"],
                        "tw_worst_unlim": lim(prop, "worst", b, 1e4, c, chem, r_grp)["tw"],
                        "I_wind_fresh_unlim": lim(prop, "fresh", b, 1e4, c, chem, r_grp)["I_m_A"],
                        "feasible": (lmin is not None) and (lmax is None or lmin <= lmax)}
    return res


def thrust_at_iwind(prop, i_w):
    def f(rpm):
        T, Ps, _ = p.prop_tp(prop, rpm, 0.0, rho, kT, kP)
        return p.motor_point(rpm, Ps, kv, rm, i0)[0] - i_w
    rpm = p.bisect(f, 1000.0, 20000.0)
    return p.prop_tp(prop, rpm, 0.0, rho, kT, kP)[0], rpm


def tw_of(prop, T, c=cant):
    return n * T * math.cos(math.radians(c)) / (m * g)


out = {"inputs": {"cant": cant, "r_ext_ohm": rx, "rm2_ohm": rm2, "rm_hot_ohm": rm_hot, "li_ion": LI}}

# check the fast limiter against the repo model (CALC-E1-WORST / -BOUND2 at 100 A)
wo, bo = k.nodes["CALC-E1-WORST"]["outputs"], k.nodes["CALC-E1-BOUND2"]["outputs"]
chk = {"fresh_b1_tw": (lim("11x5.5MR", "fresh", 1, 100)["tw"], wo["tw_fresh"]),
       "fresh_b1_Iw": (lim("11x5.5MR", "fresh", 1, 100)["I_m_A"], wo["I_wind_fresh_A"]),
       "worst_b1_tw": (lim("11x5.5MR", "worst", 1, 100)["tw"], wo["tw_worst"]),
       "worst_b1_Iw": (lim("11x5.5MR", "worst", 1, 100)["I_m_A"], wo["I_wind_worst_A"]),
       "fresh_b2_tw": (lim("11x5.5MR", "fresh", 2, 100)["tw"], bo["tw_fresh"]),
       "worst_b2_tw": (lim("11x5.5MR", "worst", 2, 100)["tw"], bo["tw_worst"]),
       "ilim25": (solve_L(lambda L: lim("11x5.5MR", "fresh", 1, L)["I_m_A"], 25.0),
                  k._run("CALC-E1-ILIM-25")["ilim_a"])}
out["check_vs_repo"] = chk

# ---------------------------------------------------------------- 1. limiter sweep, 11x5.5MR, LiPo, both bounds
sweep = []
for L in (60, 65, 68, 70, 71, 72, 75, 80, 85, 90, 95, 100):
    row = {"L": L}
    for b in (1, 2):
        for st in states():
            q = lim("11x5.5MR", st, b, L)
            row[f"b{b}_{st}"] = {"tw": q["tw"], "Iw": q["I_m_A"], "Ip": q["Ipack"], "V": q["Vbus"], "duty": q["duty"]}
    sweep.append(row)
out["sweep_55MR_lipo"] = sweep
T25, rpm25 = thrust_at_iwind("11x5.5MR", I_RATE)
out["cap_25A_55MR"] = {"T_gf": T25 / g * 1000, "rpm": rpm25, "tw": tw_of("11x5.5MR", T25)}
out["T_need_fresh_gf"] = TW_MIN * m * 1000 / (n * math.cos(math.radians(cant)))
out["T_need_worst_gf"] = TW_SAG * m * 1000 / (n * math.cos(math.radians(cant)))

# ---------------------------------------------------------------- 2. props
k._run("CALC-E1-HOVER")
k._run("CALC-E1-CRUISE-V17")
hv = k.nodes["CALC-E1-HOVER"]["outputs"]
ci = k.nodes["CALC-E1-CRUISE-V17"]["input_values"]
P17_repo = k.nodes["CALC-E1-CRUISE-V17"]["outputs"]["P_total_55_W"]
D17 = p.cruise_drag(17.0, ci["m"], ci["g"], ci["rho"], ci["S"], ci["cd0"], ci["k"], ci["trim"])
T_h = hv["T_per_motor_N"]
props = {}
for pr in PROPS:
    h = p.at_thrust(pr, T_h, 0.0, rho, kT, kP, kv, p.r_hot(rm, tc[0], 50.0), i0, esc[0], esc[1], 14.8)
    c17 = p.at_thrust(pr, D17 / n, 17.0, rho, 1.0, kP, kv, p.r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
    t25, r25 = thrust_at_iwind(pr, I_RATE)
    tf, _ = thrust_at_iwind(pr, I_RATE)
    row = {"hover_rpm": h["rpm"], "hover_I_bat_A": h["I_bat_A"], "hover_I_wind_A": h["I_m_A"],
           "hover_pack_A": n * h["I_bat_A"], "hover_W": n * h["P_bat_W"],
           "cruise17_W": n * c17["P_bat_W"], "cruise17_A_148": n * c17["I_bat_A"], "cruise17_J": c17["J"],
           "cruise17_eta_prop": D17 / n * 17.0 / c17["P_shaft_W"],
           "cruise17_eta_tot": D17 / n * 17.0 / c17["P_bat_W"], "cruise17_rpm": c17["rpm"],
           "T_at_25A_gf": t25 / g * 1000, "rpm_at_25A": r25, "tw_cap_25A": tw_of(pr, t25),
           "I_wind_at_T_need_fresh": None}
    # winding current at the thrust T/W 2.0 needs (bound-independent)
    Tn = TW_MIN * m * g / (n * math.cos(math.radians(cant)))
    rpm_n = p.bisect(lambda r: p.prop_tp(pr, r, 0.0, rho, kT, kP)[0] - Tn, 1000.0, 20000.0)
    row["I_wind_at_T_need_fresh"] = p.motor_point(rpm_n, p.prop_tp(pr, rpm_n, 0.0, rho, kT, kP)[1], kv, rm, i0)[0]
    for b in (1, 2):
        for st in ("fresh", "worst"):
            q = lim(pr, st, b, 100.0)
            row[f"L100_b{b}_{st}"] = {"tw": q["tw"], "Iw": q["I_m_A"]}
    row["window_lipo"] = window(pr)
    L1 = row["window_lipo"]["b1"]["L_max_25A"]
    row["L1"] = L1
    for b in (1, 2):
        for st in ("fresh", "worst"):
            q = lim(pr, st, b, L1)
            row[f"atL1_b{b}_{st}"] = {"tw": q["tw"], "Iw": q["I_m_A"], "Ip": q["Ipack"]}
    props[pr] = row
out["props"] = props
out["D17_N"] = D17
out["P17_repo_W"] = P17_repo

# E2's pessimistic 17 m/s budget per prop (E2's own budget_v17, corrected counter not applied: E2 owns it).
# Cruise: E1 17 m/s power x (prop / MR ratio of this script) ; hover: x the prop's hover power ratio
sys.path.insert(0, str(HERE.parent / "E2"))
try:
    import energy_claims as e2  # noqa: E402
    e2.kit._run("CALC-E2-BUDGET-V17")
    iv = dict(e2.kit.nodes["CALC-E2-BUDGET-V17"]["input_values"])
    base_hover = e2.hover_bus_w
    e2r = {}
    for pr in PROPS:
        hr = props[pr]["hover_W"] / props["11x5.5MR"]["hover_W"]
        cr = props[pr]["cruise17_W"] / props["11x5.5MR"]["cruise17_W"]
        e2.hover_bus_w = lambda *a, _hr=hr, **kw: base_hover(*a, **kw) * _hr
        kw = dict(iv)
        kw["p17"] = P17_repo * cr
        r = e2.budget_v17(**kw)
        e2r[pr] = {"hover_ratio": hr, "cruise_ratio": cr, "p17_w": kw["p17"], "cruise_w_pess": r["cruise_w_pess"],
                   "cruise_a_pess": r["cruise_a_pess"], "low_mah": r["low_mah"], "to_low_min": r["cruise_to_low_min"]}
    e2.hover_bus_w = base_hover
    out["e2_v17_lipo_repo_counter"] = e2r
except Exception as ex:  # noqa: BLE001
    out["e2_error"] = repr(ex)

# ---------------------------------------------------------------- 3. cant (11x5.5MR, LiPo)
k._run("CALC-E1-TIP-GAP")
gi = k.nodes["CALC-E1-TIP-GAP"]["input_values"]
cants = {}
for c in (5.0, 7.0, 8.0, 8.5, 9.0, 10.0):
    Th = m * g * 1.06 / (n * math.cos(math.radians(c)))
    h = p.at_thrust("11x5.5MR", Th, 0.0, rho, kT, kP, kv, p.r_hot(rm, tc[0], 50.0), i0, esc[0], esc[1], 14.8)
    tg = p.tip_gap(**dict(gi, cant=c))
    w = window("11x5.5MR", c)
    cants[c] = {"T_hover_N": Th, "hover_pack_A": n * h["I_bat_A"], "hover_W": n * h["P_bat_W"],
                "hover_I_wind_A": h["I_m_A"], "tw_cap_25A": tw_of("11x5.5MR", T25, c),
                "tw_fresh_L100": lim("11x5.5MR", "fresh", 1, 100, c)["tw"],
                "tw_worst_L100": lim("11x5.5MR", "worst", 1, 100, c)["tw"],
                "tw_worst_b2_L100": lim("11x5.5MR", "worst", 2, 100, c)["tw"],
                "window": w, "gap_tube_m": tg["gap_m"], "ahead_needed_m": tg["ahead_needed_m"],
                "gap_sense_plus_m": tg["gap_sense_plus_m"]}
out["cant"] = cants

# ---------------------------------------------------------------- 4. Li-ion 4S2P P45B
li = {}
for rg in (LI["r_grp"], LI["r_grp_max"]):
    for pr in ("11x5.5MR", "11x5.5E"):
        key = f"{pr}_rgrp{rg*1000:.1f}"
        row = {"window": window(pr, chem="li", r_grp=rg)}
        for L in (45.0, 71.07, 90.0, 100.0):
            for b in (1, 2):
                for st in states("li", rg):
                    q = lim(pr, st, b, L, chem="li", r_grp=rg)
                    row[f"L{L:g}_b{b}_{st}"] = {"tw": q["tw"], "Iw": q["I_m_A"], "Ip": q["Ipack"], "V": q["Vbus"]}
        li[key] = row
out["li_ion"] = li


def clean(o):
    if isinstance(o, dict):
        return {str(a): clean(b) for a, b in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, float):
        return None if math.isinf(o) else round(o, 4)
    return o


if __name__ == "__main__":
    res = clean(out)
    (HERE / "design_round_1114.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
