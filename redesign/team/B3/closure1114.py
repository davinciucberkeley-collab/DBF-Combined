"""B3 closure round 2026-11-14 (review/CLOSURE-ROUND-2026-11-14/B3.md): R-TRANSITION entry window.

A2 (closure §2.3) finds that the D-149 entry at 1.4 W static gives CL-B1-TRANS-THRUST 1.4 / 1.7456 = 0.802 against
the 0.80 control reserve at the sagged pack (thrust_max_per_motor 1.309 kg x voltage_sag 0.867 x 4 / 2.6 kg). This
script finds the entry thrust window in which BOTH pass with margin at the pessimistic end:
  - B1: T0 / (n Tmax sag) <= 0.80 (ASM-B1-CTRL-RESERVE), at the gate mass (largest fraction for a given T0/W);
  - B3: CL-B3-TRANS-PITCH-USE <= 0.60 (ASM-B3-TRANS-USE-MAX), the time-domain pitch-over (flight_models.pitchover_td,
    the same function CALC-B3-TRANS-TD stores), at the forward CG and on the conservative prop slope;
  - CL-B3-TRANS-V-HANDOVER >= the tripped forward-CG stall (CL-B2R3-VS-GATE-FWD-TURB);
  - CL-B3-TRANS-GUST2-T0 <= 1.0 and CL-B3-TRANS-LOWER-MOTOR >= 0.
It also sweeps the firmware settings that shape the pitch-over (Q_TAILSIT_RAT_FW, Q_TAILSIT_ANGLE), the attitude
loop (wn), the CG, the prop slope and the mass, so the chosen point is shown to pass at the pessimistic corner.

Throttle mapping (ArduPilot Plane-4.7.2, read 2026-11-14): Tailsitter_Transition::update, state ANGLE_WAIT_FW,
set_throttle_out(MAX(get_throttle_hover(), get_throttle_in()), true, 0) and AC_AttitudeControl_Multi::set_throttle_out
stores _throttle_in = throttle_in, so the entry throttle is held to Q_TAILSIT_ANGLE. Angle boost: the tailsitter
defaults table sets Q_A_ANGLE_BOOST 0. Thrust-linearised throttle with battery-voltage compensation: thrust / W =
dl x throttle / theta_h, where theta_h is the hover throttle (learnt, or fixed). EST: the thrust curve expo is
replaced from the stand (Q_M_THST_EXPO).

Reads team/B3/claims.json (input values stored by sc_analysis.py). Writes team/B3/results/closure1114.json only.
Run (from the repo root):  python -I redesign/team/B3/closure1114.py
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flight_models as FM  # noqa: E402

N = {n["id"]: n for n in json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["nodes"]}
t = N["CALC-B3-TRANS-TD"]["input_values"]

m, g, rho = t["m"], t["g"], t["rho"]
W = m * g
A_disk = math.pi * t["D"] ** 2 / 4
k_bemt = t["dHdi"] / (t["cna"] * A_disk * 0.5 * rho * t["v_inc"] ** 2)
TW_SAG = t["n"] * t["tmax"] * t["sag"] / m          # 1.7456: sagged T/W at the gate mass (A2 §2.3)
FRAC_MAX = 0.80                                      # ASM-B1-CTRL-RESERVE
USE_MAX = 0.60                                       # ASM-B3-TRANS-USE-MAX
VS_TRIP = t["vs_trip"]
RATE0, ANG0, VAS0 = t["fsw"]
WN0, ZETA0 = t["loop"]


def ptd(mass=m):
    return {"m": mass, "g": g, "rho": rho, "S": t["S"], "c": t["c"], "b": t["b"], "e": t["e"],
            "a0": math.radians(t["a0"]), "CLa": t["CLa"], "clmax": t["clmax"], "cd0": t["cd0"], "cn90": t["cn90"],
            "n": t["n"], "D": t["D"], "x_prop": t["x_prop"], "cna": t["cna"], "cm_ac": t["cm_np_thin"] + t["dcm"],
            "xnp": t["xnp"], "dl": t["dl"], "tmax": t["tmax"] * g * t["sag"], "z": t["z"], "dfrac": t["dfrac"],
            "Iyy": t["Iyy"] * mass / t["m_basic"],
            "Vp": t["v_inc"] * math.cos(math.radians(45)) / (1 - t["T_I45"]), "Cmd_ref": t["Cmd_ref"],
            "CLd": t["CLd"], "xref": t["xref"], "eta": t["eta"], "lo": t["lo"], "li": t["li"], "va": t["va"],
            "slop": t["slop"], "fpost": t["fpost"]}


def run(tw, x=None, rate=RATE0, ang=ANG0, vas=VAS0, wn=WN0, zeta=ZETA0, kp=None, mass=m, w0=0.0):
    x = t["x_fwd"] if x is None else x
    kp = k_bemt if kp is None else kp
    p = ptd(mass)
    r = FM.pitchover_td(p, x, T0_W=tw, rate=rate, ang_done=ang, v_assist=vas, wn=wn, zeta=zeta, kprop=kp, w0=w0)
    r2 = FM.pitchover_td(p, x, T0_W=tw, rate=rate, ang_done=ang, v_assist=vas, wn=wn, zeta=zeta, kprop=kp,
                         gust_w=2.0, w0=w0)
    return {"T0_W": tw, "use": round(max(r["max_trim_only_pitchover"], r["peak_fw_assist"]), 4),
            "use_po": round(r["max_trim_only_pitchover"], 4), "use_fwA": round(r["peak_fw_assist"], 4),
            "V_done": r["V_done"], "gust2": r2["peak_use30_gust"],
            "lower_N": round(r["lower_motor_N_at_peak"], 3) if r["lower_motor_N_at_peak"] is not None else None,
            "dh": r["alt_change_m"], "t_done": r["t_done_s"],
            "frac_sag_gate": round(tw * mass / m / TW_SAG, 4),
            "passes": (max(r["max_trim_only_pitchover"], r["peak_fw_assist"]) <= USE_MAX and r2["peak_use30_gust"] <= 1.0
                       and r["V_done"] is not None and r["V_done"] >= VS_TRIP)}


out = {"_note": "B3 closure round 2026-11-14 (review/CLOSURE-ROUND-2026-11-14/B3.md). EST: model values are "
                "UNVERIFIED until SITL stage B and the twin.",
       "tw_sag_gate": TW_SAG, "k_prop_bemt": k_bemt, "T0_max_for_frac_0p80": FRAC_MAX * TW_SAG}

# 1. basis sweep, forward CG, BEMT slope, firmware of record
grid = [round(1.20 + 0.01 * i, 2) for i in range(21)]
out["sweep_basis"] = [run(tw) for tw in grid]
# T0 at which the trim use reaches 0.60 (pass line) and 0.50 (design margin), by bisection on the basis case


def t0_for(use_target, **kw):
    lo, hi = 1.06, 1.43
    if run(hi, **kw)["use"] > use_target:
        return None
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if run(mid, **kw)["use"] > use_target:
            lo = mid
        else:
            hi = mid
    return round(hi, 4)


out["T0_min_use_0p60_basis"] = t0_for(USE_MAX)
out["T0_min_use_0p50_basis"] = t0_for(0.50)

# 2. pessimistic corners for the low-thrust side (pitch use), from a steady hover (w0 = 0)
corners = {
    "basis_fwd_bemt": {},
    "ribner_slope": {"kp": 1.0},
    "target_cg": {"x": t["x_t"]},
    "wn4": {"wn": 4.0}, "wn10": {"wn": 10.0},
    "rate8": {"rate": 8.0}, "rate10": {"rate": 10.0}, "rate14": {"rate": 14.0}, "rate16": {"rate": 16.0},
    "ang60": {"ang": 60.0}, "ang75": {"ang": 75.0},
    "mass_pred_2p544": {"mass": 2.544},
    "assist_15": {"vas": 15.0},
}
out["corners"] = {}
for tw in (1.33,):
    for k, kw in corners.items():
        out["corners"][f"{k}_T{tw}"] = run(tw, **kw)
out["T0_min_use_0p60_by_corner"] = {k: t0_for(USE_MAX, **kw) for k, kw in corners.items()}


# 3. Entry window: lowest T0/W at which ALL of use <= 0.60, gust2 <= 1.0 and V_done >= the tripped stall pass, for
#    the pitch-over rate (Q_TAILSIT_RAT_FW) and the vertical speed at the mode change (w0, from a pre-climb hold at
#    the entry throttle in QSTABILIZE). Upper end: T0/W <= 0.80 x TW_SAG (CL-B1-TRANS-THRUST at the sagged pack).
def t_lo(**kw):
    lo, hi = 1.10, FRAC_MAX * TW_SAG
    if not run(hi, **kw)["passes"]:
        return None
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        if run(mid, **kw)["passes"]:
            hi = mid
        else:
            lo = mid
    return round(hi, 4)


out["window"] = {}
for rate in (10.0, 12.0):
    for w0 in (0.0, 3.0, 4.0):
        out["window"][f"rate{rate:.0f}_w0{w0:.0f}"] = {"T0_lo": t_lo(rate=rate, w0=w0),
                                                       "T0_hi": round(FRAC_MAX * TW_SAG, 4)}

# 4. Design point (closure round). Entry setting r = throttle_in / learnt hover throttle (theta_h). Thrust-linearised
#    throttle with battery-voltage compensation: static thrust / W = dl_true x r x (1 +/- e_lin). Pessimistic band:
#    dl_true from B4's models (1.025, CL-B4-SIM-DOWNLOAD) to the params key (1.06, kept until T-B4-INSTALLED); e_lin
#    +/- 2 % EST (thrust-curve fit between hover and entry throttle). w0 credited from a pre-climb hold at the entry
#    throttle in QSTABILIZE: 0.8 x the ideal (T0 - dl) g t, for drag in the edge-on climb and the switch delay.
DES = {"rate": 12.0, "ang": 70.0, "r": 1.285, "dl_lo": 1.025, "dl_hi": t["dl"], "e_lin": 0.02, "w0": 4.0,
       "hold_s": 2.0}
T_nom = DES["dl_hi"] * DES["r"]
lo_t = DES["dl_lo"] * DES["r"] * (1 - DES["e_lin"])
hi_t = DES["dl_hi"] * DES["r"] * (1 + DES["e_lin"])
w0_lo = 0.8 * (lo_t - DES["dl_lo"]) * g * DES["hold_s"]           # least vertical speed at the mode change
w0_hi = (hi_t - 1.0) * g * DES["hold_s"]                          # most (no download, no drag): altitude bound
out["design"] = dict(DES, T0_nominal=round(T_nom, 4), T0_low_edge=round(lo_t, 4), T0_high_edge=round(hi_t, 4),
                     throttle_in_at_theta_h_0p49=round(DES["r"] * 0.49, 4),
                     frac_nominal=round(T_nom / TW_SAG, 4), frac_high_edge=round(hi_t / TW_SAG, 4),
                     w0_credit_check=round(w0_lo, 2), w0_max=round(w0_hi, 2),
                     preclimb_height_max_m=round(0.5 * (hi_t - 1.0) * g * DES["hold_s"] ** 2, 1))
for tag, tw, w0 in (("nominal", T_nom, DES["w0"]), ("low_edge", lo_t, DES["w0"]), ("high_edge", hi_t, DES["w0"]),
                    ("high_edge_w0max", hi_t, w0_hi), ("low_edge_w0zero", lo_t, 0.0),
                    ("nominal_w0zero", T_nom, 0.0)):
    out["design"][tag] = run(tw, rate=DES["rate"], ang=DES["ang"], w0=w0)
    out["design"][tag + "_ribner"] = run(tw, rate=DES["rate"], ang=DES["ang"], w0=w0, kp=1.0)
    out["design"][tag + "_wn4"] = run(tw, rate=DES["rate"], ang=DES["ang"], w0=w0, wn=4.0)
    out["design"][tag + "_wn10"] = run(tw, rate=DES["rate"], ang=DES["ang"], w0=w0, wn=10.0)
    out["design"][tag + "_m2544"] = run(tw, rate=DES["rate"], ang=DES["ang"], w0=w0, mass=2.544)
edge_rows = {k: v for k, v in out["design"].items() if isinstance(v, dict) and "w0zero" not in k}
out["design"]["worst_over_edges"] = {
    "use_max": max(v["use"] for v in edge_rows.values()),
    "gust2_max": max(v["gust2"] for v in edge_rows.values()),
    "V_done_min": min(v["V_done"] for v in edge_rows.values()),
    "lower_N_min": min(v["lower_N"] for v in edge_rows.values()),
    "dh_max_incl_preclimb_m": round(max(v["dh"] for v in edge_rows.values()) + out["design"]["preclimb_height_max_m"], 1),
    "frac_max": max(v["frac_sag_gate"] for v in edge_rows.values()),
    "all_pass": all(v["passes"] for v in edge_rows.values())}
out["window"]["rate12_w05"] = {"T0_lo": t_lo(rate=12.0, w0=5.0), "T0_hi": round(FRAC_MAX * TW_SAG, 4)}
# Q_TAILSIT_ANGLE 75 was tried (V_done +1 m/s) and rejected: the longer VTOL phase raises CL-B3-TRANS-GUST2-T0
# above 1.0 at the high-thrust edge (1.004-1.031, closure round run 2026-11-14)

(HERE / "results" / "closure1114.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

print("TW_sag %.4f  T0 max for 0.80: %.4f  k_bemt %.3f" % (TW_SAG, FRAC_MAX * TW_SAG, k_bemt))
print("T0 for use 0.60 (basis) %s ; for 0.50 %s" % (out["T0_min_use_0p60_basis"], out["T0_min_use_0p50_basis"]))
for r in out["sweep_basis"]:
    print("  ", r)
print("T0 for 0.60 by corner (w0 0):")
for k, v in out["T0_min_use_0p60_by_corner"].items():
    print("   %-18s %s" % (k, v))
for k, r in out["corners"].items():
    print("  %-26s use %.3f (po %.3f fwA %.3f) Vdone %s gust2 %.3f lowerN %s dh %.1f frac %.3f" % (
        k, r["use"], r["use_po"], r["use_fwA"], r["V_done"], r["gust2"], r["lower_N"], r["dh"], r["frac_sag_gate"]))
print("window [T0_lo all-pass, T0_hi frac 0.80]:")
for k, v in out["window"].items():
    print("   %-14s %s" % (k, v))
print("design:")
for k, v in out["design"].items():
    print("   %-28s %s" % (k, v))
