"""E1 D-173: motor search for the APC 11x8E / 11x8EP at 10 deg cant and the 2.64 kg gate.

Run:  python -I redesign/team/E1/motor_select_173.py   -> team/E1/motor_select_173.json (nothing else written)

Station model = propulsion.py's (station / full_throttle / limited / tip_gap), unchanged. Motor data from the makers'
pages, checked 2026-11-14 (review/CLOSURE-ROUND-2026-11-14/E1.md section D-173, table of sources).

Prop factors for the 11x8E. Two published calibrations disagree, so every claim is taken at the worse of the two:
  "x2814": kT, kP fitted to the SunnySky X2814 V3 KV900 maker row "APC 11x8, 14.8 V, 45.5 A, 2320 gf, 10221 rpm"
           (sunnyskyusa.com/products/sunnysky-x2814): kT from thrust at the measured rpm (supply-independent); kP from
           the shaft torque the winding current gives at duty ~1, Q = (I - I0) / Kt (also supply-independent)
  "x3108": propulsion.py's kT 1.039 / kP 1.240 (X3108S KV900 + APC 11x4.7SF rows, ASM-E1-CAL-TRANSFER)
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import propulsion as p  # noqa: E402

N = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
IV = N["CALC-E1-WORST"]["input_values"]
TG = dict(N["CALC-E1-TIP-GAP"]["input_values"])
m_gate, g, rho, cant = IV["m"], IV["g"], IV["rho"], IV["cant"]
kdl = N["CALC-E1-HOVER"]["input_values"]["kdl"]
V = N["CALC-E1-CRUISE-V17"]["input_values"]["V"]
D_cruise = N["CL-E1-CRUISE-DRAG"]["value"] + 0.262                 # + B2 trip device drag (B2.md B2C-3)
rx = N["CALC-E1-REXT-ALLOW"]["input_values"]["r_ext"] / 1000.0
cc = math.cos(math.radians(cant))
W = m_gate * g
fresh = (16.8, 4 * 0.004 + rx)
worst = (4 * 3.73, 4 * 0.004 * 1.5 + rx)
tol, band, tc = 0.011, 0.10, 0.00393
ESC_CONT, ESC_BURST = 45.0, 55.0                                   # LANRC BLHeli_S 45 A (55 A 10 s), BOM B02
RPM_CAP = 6016.0                                                   # C4 D-161 option A

rows = []
with open(HERE / "data" / "apc_per3_11x8E.csv", encoding="utf-8") as f:
    for line in f:
        if not (line.startswith("#") or line.startswith("rpm")):
            rows.append([float(v) for v in line.strip().split(",")[:4]])
p.PROPS["11x8E"] = {"static": {int(r[0]): (r[2], r[3]) for r in rows if r[1] == 0.0},
                    "J": [[r[1], r[2], r[3]] for r in rows if int(r[0]) == 6000], "mass_g": 22.96}
p.PROP_D["11x8E"] = 0.2794
PR = "11x8E"

# --- calibration on the X2814 V3 maker row
CAL = {"rpm": 10221.0, "gf": 2320.0, "A": 45.5, "kv": 900.0, "i0": 1.2}
T1, P1, _ = p.prop_tp(PR, CAL["rpm"], 0.0, rho, 1.0, 1.0)
kT_x = CAL["gf"] * 9.80665e-3 / T1
Q = (CAL["A"] - CAL["i0"]) * 60.0 / (2 * math.pi * CAL["kv"])
kP_x = Q * CAL["rpm"] * 2 * math.pi / 60.0 / P1
FACTORS = {"x2814": (kT_x, kP_x), "x3108": (N["CL-E1-KT"]["value"], N["CL-E1-KP"]["value"])}

# --- candidates (maker data, see E1.md D-173): Kv, R_m ohm, I0 A, rated A, rating s, mass g (as listed),
#     body length mm (mount face to bell top, for the stack), price USD, ESC adapter note
MOTORS = {
    "SunnySky X2814 V3 KV900": dict(kv=900, rm=0.0336, i0=1.2, irate=50.0, dur="30 s", mass=108.0, body=36.0,
                                     price=39.99),
    "SunnySky X2814 KV900 (black X)": dict(kv=900, rm=0.052, i0=0.7, irate=40.0, dur="30 s", mass=108.0, body=36.0,
                                           price=29.99),
    "SunnySky V3508 KV700": dict(kv=700, rm=0.092, i0=0.7, irate=32.0, dur="30 s", mass=97.0, body=20.0, price=42.99),
    "T-Motor MN3510 KV700": dict(kv=700, rm=0.050, i0=0.5, irate=25.0, dur="180 s", mass=118.0, body=28.5,
                                 price=79.90),
    "SunnySky X3108S KV900 (today)": dict(kv=900, rm=0.086, i0=0.9, irate=25.0, dur="30 s", mass=81.0, body=26.5,
                                          price=24.99),
}


def lim(mo, kT, kP, rm, case, il, dmax=1.0):
    s = p.full_throttle(PR, 0.0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, case[0], case[1], 1.0, 4,
                        duty_max=dmax)
    if 4 * s["I_bat_A"] + 1.0 <= il:
        return s
    lo, hi = 0.3, dmax
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        t = p.full_throttle(PR, 0.0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, case[0], case[1], 1.0, 4,
                            duty_max=mid)
        if 4 * t["I_bat_A"] + 1.0 > il:
            hi = mid
        else:
            lo = mid
    return p.full_throttle(PR, 0.0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, case[0], case[1], 1.0, 4,
                           duty_max=lo)


def single(mo, kT, kP, rm, d, others):
    """One motor at duty d, three at thrust `others`, fresh pack; bus solved."""
    v = 16.8
    for _ in range(80):
        h = p.at_thrust(PR, others, 0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, v)
        r = p.bisect(lambda x: p.station(PR, x, 0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, v)["duty"] - d,
                     300, 25000)
        s = p.station(PR, r, 0, rho, kT, kP, mo["kv"], rm, mo["i0"], 0.010, 0.5, v)
        vn = 16.8 - fresh[1] * (s["I_bat_A"] + 3 * h["I_bat_A"] + 1.0)
        if abs(vn - v) < 1e-6:
            break
        v = 0.5 * (v + vn)
    return s


def tw(s, mass=None):
    return 4 * s["T_N"] * cc / ((mass or m_gate) * g)


Th = W * kdl / (4 * cc)
out = {"factors": {k: list(v) for k, v in FACTORS.items()}, "D_cruise_N": D_cruise}
for name, mo in MOTORS.items():
    r = {"mass_g": mo["mass"], "price": mo["price"], "rating": f'{mo["irate"]} A / {mo["dur"]}',
         "torque_rated_Nm": mo["irate"] * 60 / (2 * math.pi * mo["kv"])}
    per = {}
    for fk, (kT, kP) in FACTORS.items():
        q = {}
        rmb_hi, rmb_lo = mo["rm"] * (1 + band), mo["rm"] * (1 - band)
        # limiter: least pack current with fresh band-edge T/W >= 2.0 (sensor low), set 1.5 % above its sensor edge
        f_ok = lambda il: tw(lim(mo, kT, kP, rmb_hi, fresh, il * (1 - tol))) - 2.0
        unl = lim(mo, kT, kP, rmb_hi, fresh, 1e9)
        if tw(unl) < 2.0:
            q["ilim_A"] = None
            q["tw_fresh_unlimited"] = tw(unl)
            per[fk] = q
            continue
        lo = p.bisect(f_ok, 30.0, 4 * unl["I_bat_A"] + 1.0, n=30)
        il = math.ceil(lo * 1.015 * 2) / 2
        q["ilim_A"] = il
        f = lim(mo, kT, kP, rmb_hi, fresh, il * (1 - tol))
        w = lim(mo, kT, kP, p.r_hot(rmb_hi, tc, 80), worst, il * (1 - tol))
        hi = lim(mo, kT, kP, rmb_lo, fresh, il * (1 + tol))
        q.update(tw_fresh_band=tw(f), tw_worst_band=tw(w), I_wind_limiter_A=hi["I_m_A"], I_esc_limiter_A=hi["I_bat_A"])
        # single-motor transient without any spin cap (duty 1), fresh pack, R_m -10 %, others at hover / 0.3 hover
        s1, s2 = single(mo, kT, kP, rmb_lo, 1.0, Th), single(mo, kT, kP, rmb_lo, 1.0, 0.3 * Th)
        q.update(single_I_wind_A=max(s1["I_m_A"], s2["I_m_A"]), single_I_esc_A=max(s1["I_bat_A"], s2["I_bat_A"]))
        # static cap holding the ESC continuous rating and the winding rating (worse of the two "others" cases)
        cap_lim = lambda d: max(single(mo, kT, kP, rmb_lo, d, 0.3 * Th)["I_bat_A"] - ESC_CONT,
                                single(mo, kT, kP, rmb_lo, d, 0.3 * Th)["I_m_A"] - mo["irate"])
        cap = 1.0 if cap_lim(1.0) <= 0 else math.floor(p.bisect(cap_lim, 0.3, 1.0, n=30) * 100) / 100
        q["static_cap"] = cap
        fc = lim(mo, kT, kP, rmb_hi, fresh, il * (1 - tol), dmax=cap)
        wc = lim(mo, kT, kP, p.r_hot(rmb_hi, tc, 80), worst, il * (1 - tol), dmax=cap)
        lc = lim(mo, kT, kP, p.r_hot(rmb_hi, tc, 80), (4 * 3.60, worst[1]), il * (1 - tol), dmax=cap)
        q.update(tw_fresh_band_cap=tw(fc), tw_worst_band_cap=tw(wc), tw_360_band_cap=tw(lc))
        q["m_max_kg"] = min(4 * fc["T_N"] * cc / (2.0 * g), 4 * wc["T_N"] * cc / (1.6 * g))
        # hover, cruise, rpm (nominal R_m, warm winding as propulsion.py)
        h = p.at_thrust(PR, Th, 0.0, rho, kT, kP, mo["kv"], p.r_hot(mo["rm"], tc, 50), mo["i0"], 0.010, 0.5, 14.8)
        c = p.at_thrust(PR, D_cruise / (4 * cc), V, rho, kT, kP, mo["kv"], p.r_hot(mo["rm"], tc, 40), mo["i0"], 0.010,
                        0.5, 14.8)
        q.update(hover_rpm=h["rpm"], hover_I_pack_A=4 * h["I_bat_A"] + 1.0, hover_W=4 * h["P_bat_W"],
                 hover_I_wind_A=h["I_m_A"], cruise_rpm=c["rpm"], cruise_W=4 * c["P_bat_W"],
                 full_rpm_fresh=unl["rpm"], full_rpm_limiter=f["rpm"])
        per[fk] = q
    r["cases"] = per
    st = list(TG["st"])
    st[0] = mo["body"] / 1000.0
    tg = dict(TG, st=st, ahead=0.014)
    r["tip_gap_m"] = p.tip_gap(**tg)["gap_m"]
    out[name] = r

(HERE / "motor_select_173.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
