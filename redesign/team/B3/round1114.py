"""B3 design round 2026-11-14 (wave 1 analysis; wave 2: cant read from params, model moved to
flight_models.pitchover_td and the stored claims CALC-B3-TRANSITION / CALC-B3-TRANS-TD): the two B3 fails.

  1. CL-B3-HOVER-YAW-WTIP-20 (1.32 vs >= 1.5): cant sweep, cost of cant, other levers.
  2. CL-B3-TRANS-PITCH-USE (0.91 vs <= 0.60): quasi-steady re-check, hub-term sign, and a time-domain
     longitudinal pitch-over model that follows ArduPilot's tailsitter forward transition
     (ArduPlane/tailsitter.cpp, tag Plane-4.7.2: nav pitch ramped at Q_TAILSIT_RAT_FW, throttle held at
     MAX(hover throttle, throttle in), VTOL control until |pitch| > Q_TAILSIT_ANGLE).

Reads only. Inputs are the resolved input values that sc_analysis.py stored in team/B3/claims.json (calc nodes
CALC-B3-HOVER-WTIP, CALC-B3-TRANSITION, CALC-B3-HOVER), B4's claims.sim.json and E1's CALC-E1-TIP-GAP inputs.
E1's tip-gap function is loaded from team/E1/propulsion.py by AST (only that function, the module is not run).
Writes team/B3/results/round1114.json. Nothing shared is edited.

Run (from the repo root):  python -I redesign/team/B3/round1114.py
"""
import ast
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # redesign/
sys.path.insert(0, str(HERE))
import flight_models as FM  # noqa: E402

DEG = math.pi / 180


def nodes(path):
    return {n["id"]: n for n in json.loads((ROOT / path).read_text(encoding="utf-8"))["nodes"]}


B3 = nodes("team/B3/claims.json")
B4S = nodes("team/B4/sim/claims.sim.json")
E1 = nodes("team/E1/claims.json")
IW = B3["CALC-B3-HOVER-WTIP"]["input_values"]
IT = B3["CALC-B3-TRANSITION"]["input_values"]
IH = B3["CALC-B3-HOVER"]["input_values"]
IE = E1["CALC-E1-TIP-GAP"]["input_values"]

# ------------------------------------------------------------------------------------------- E1 tip gap (AST)
src = (ROOT / "team/E1/propulsion.py").read_text(encoding="utf-8")
mod = ast.parse(src)
fns = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in ("_tip_gap", "tip_gap")]
for f in fns:
    f.decorator_list = []
ns = {"math": math}
exec(compile(ast.Module(body=fns, type_ignores=[]), "E1_tip_gap", "exec"), ns)
tip_gap = ns["tip_gap"]

out = {"_note": "B3 design round 2026-11-14; see review/DESIGN-ROUND-2026-11-14/B3.md. EST throughout (models are "
                "UNVERIFIED until the twin / SITL stage B)."}

# =========================================================================================== PART 1: hover yaw
w = IW
Th = w["m"] * w["g"] * w["dl"] / 4
dT = w["dfrac"] * Th
kq_iso = w["Qh"] / Th
rr = math.hypot(w["y"], w["z"])
ixx = w["Ixx"] * w["m"] / w["m_basic"]


def m_wing(beta, V):
    q, b = 0.5 * w["rho"] * V * V, beta * DEG
    return q * w["S"] * ((math.pi / 2) * (w["c"] / w["b"]) * math.sin(b) * math.cos(b) * w["arm"][0] * w["b"]
                         + w["cdc"] * math.sin(b) ** 2 * w["arm"][1] * w["b"])


def m_ctrl(cant, dfrac=None):
    d = (dfrac if dfrac is not None else w["dfrac"]) * Th
    return 4 * d * (kq_iso * w["swirl_lo"] + rr * math.sin(cant * DEG))


def ratio20(cant, V=None):
    return m_ctrl(cant) / m_wing(20.0, V or w["Vw"])


# reproduce the claim at the cant of record (read from params through claims.json; D-146: 9 deg)
CANT0 = w["cant"]
out["cant_of_record_deg"] = CANT0
out["yaw_repro_ratio20_params"] = ratio20(CANT0)
out["yaw_repro_ratio20_7"] = ratio20(7.0)
out["yaw_repro_ratio20_10"] = ratio20(10.0)
# cant for exactly 1.5
lo, hi = 0.0, 15.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if ratio20(mid) < w["fac"] else (lo, mid)
out["yaw_cant_for_1p5_deg"] = hi

# tip gap at 7 deg with the carried face_ahead (reproduce E1 26.1 mm)
sweep = []
for cant in (7.0, 8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0):
    e = dict(IE, cant=cant)
    tg = tip_gap(**e)
    sweep.append({
        "cant_deg": cant,
        "ratio_20deg_5": round(ratio20(cant), 3),
        "ratio_20deg_5_minus10pct_model": round(ratio20(cant) / 1.10, 3),
        "ratio_10deg_gust": round(m_ctrl(cant) / m_wing(10.0, w["Vg"]), 3),
        "M_ctrl_Nm": round(m_ctrl(cant), 4),
        "acc_yaw_rads2": round(m_ctrl(cant) / ixx, 3),
        "axial_thrust_loss_vs_0": round(1 - math.cos(cant * DEG), 5),
        "axial_thrust_loss_vs_params": round(1 - math.cos(cant * DEG) / math.cos(CANT0 * DEG), 5),
        "motor_thrust_hover_N": round(Th / math.cos(cant * DEG), 4),
        "cos_ratio_vs_params": round(math.cos(cant * DEG) / math.cos(CANT0 * DEG), 5),
        "tip_gap_mm_at_carried_face": round(tg["gap_m"] * 1000, 2),
        "face_ahead_needed_mm": round(tg["ahead_needed_m"] * 1000, 1),
        "stack_add_mm": round(tg["stack_add_m"] * 1000, 1),
    })
out["yaw_cant_sweep"] = sweep
# differential needed at the cant of record for 1.5 (information: the requirement text forbids raising it)
out["yaw_dfrac_needed_at_params"] = w["dfrac"] * w["fac"] / ratio20(CANT0)
out["yaw_M_wing_20_5_Nm"] = m_wing(20.0, w["Vw"])

# =========================================================================================== PART 2: transition
t = IT
m, g, rho, S, c, b = t["m"], t["g"], t["rho"], t["S"], t["c"], t["b"]
AR = b * b / S
k_ind = 1 / (math.pi * t["e"] * AR)
a0 = t["a0"] * DEG
W = m * g
Th_t = W * t["dl"] / 4
m_cap = lambda dfrac: 2 * (dfrac * Th_t) * (2 * t["z"])   # as CALC-B3-HOVER / -TRANSITION: dT = dfrac x hover thrust
M30 = m_cap(0.30)
out["m_cap30_Nm"] = M30
Iyy = IH["Iyy"] * IH["m"] / IH["m_basic"]
out["Iyy_kgm2"] = Iyy
cm_ac = t["cm_np_thin"] + t["dcm"]
A_disk = math.pi * t["D"] ** 2 / 4
H_hov, H_max, v_inc = t["h_hov"], t["h_max"], t["v_inc"]
V_INC = IT["v_inc"]                              # B4's incidence speed (ASM-B3-B4-INC-V; 17.0 since B4 wave 2)
dHdi = B4S["CL-B4-SIM-DH-DI"]["value"]           # N/rad per prop at V_INC, hover rpm (BEMT)
T_I45 = B4S["CL-B4-SIM-T-I45"]["value"]          # thrust / static at 45 deg inflow, V_INC, fixed rpm
Vp = V_INC * math.cos(45 * DEG) / (1 - T_I45)    # EST linear axial-inflow thrust lapse T/T0 = 1 - Va/Vp
out["thrust_lapse_Vp_ms"] = Vp
# Ribner per-prop slope at V_INC vs B4 BEMT dH/di: the ratio scales the prop term for the low bound
rib_slope_15p6 = t["cna"] * A_disk * 0.5 * rho * V_INC ** 2
out["prop_slope_ribner_N_per_rad"] = rib_slope_15p6
out["prop_slope_bemt_N_per_rad"] = dHdi
k_prop_lo = dHdi / rib_slope_15p6


def aero_moment(V, alpha, x_cg, kprop=1.0, hforce=0.0):
    """Wing + prop pitch moment about the CG, nose-up +, same model as FM.transition_point. hforce: extra
    in-plane prop force per prop (B4), applied with its physical sign (same sense as the Ribner normal force,
    props ahead of the CG: nose-up)."""
    if V < 0.05:
        return 0.0, 0.0, 0.0
    q = 0.5 * rho * V * V
    al = max(min(alpha, math.pi / 2), -10 * DEG)
    cl, cd, cn, post, a_s = FM.wing_coeffs(al, t["CLa"], a0, t["clmax"], t["cd0"], k_ind, t["cn90"])
    if not post:
        Cm = cm_ac - cl * (t["xnp"] - x_cg) / c
    else:
        xcp = 0.25 + 0.25 * (al - a_s) / (math.pi / 2 - a_s)
        Cm = -cn * (xcp * c - x_cg) / c
    Np = kprop * t["n"] * t["cna"] * A_disk * q * math.sin(al) * math.cos(al)
    Np = max(Np, t["n"] * hforce)
    return q * S * c * Cm + Np * (x_cg - t["x_prop"]), cl, cd


def elevon_moment(V, alpha, x_cg, defl, fpost_flat=None):
    """Elevon pitch moment available at defl deg (D6 losses), effectiveness as ASM-B3-ELEVON-POST (linear from
    the stall to 90 deg) or a flat post-stall factor."""
    cmd = (t["Cmd_ref"] + t["CLd"] * (x_cg - t["xref"]) / c) * t["eta"] * (1 - max(t["lo"], t["li"]) * (V / t["va"]) ** 2)
    a_s = a0 + t["clmax"] / t["CLa"]
    if alpha <= a_s:
        f = 1.0
    elif fpost_flat is not None:
        f = fpost_flat
    else:
        f = 1.0 - (1.0 - t["fpost"]) * (alpha - a_s) / (math.pi / 2 - a_s)
    return abs(cmd) * max(defl - t["slop"], 0.0) * f * 0.5 * rho * V * V * S * c


# ---- 2a. quasi-steady re-check (reproduce 0.909 / 0.83) and the hub-term sign
qs = []
for tag, x in (("fwd", t["x_fwd"]), ("ff_band_fwd", 0.0453), ("target", t["x_t"]), ("aft", 0.05133)):
    for V in (8.0, 9.0, 10.0, 10.5, 11.0, 11.5):
        r = FM.transition_point(V, m, g, rho, S, c, x, t["xnp"], cm_ac, t["CLa"], a0, t["clmax"], t["cd0"], k_ind,
                                t["cn90"], t["n"], t["D"], t["x_prop"], t["cna"], t["tmax"] * g * t["sag"], t["z"],
                                0.0, t["dl"], 0.0, 0.0, t["fpost"])
        al = r["alpha_deg"] * DEG
        hub = t["n"] * H_hov * min(1.0, V / v_inc) * abs(x - t["x_prop"])
        Mrib, _, _ = aero_moment(V, al, x)
        Mlo, _, _ = aero_moment(V, al, x, kprop=k_prop_lo)
        Mh, _, _ = aero_moment(V, al, x, hforce=H_hov * min(1.0, V / v_inc))
        qs.append({"cg": tag, "x_cg": x, "V": V, "alpha_deg": round(r["alpha_deg"], 1),
                   "use_carried_hub_added": round((abs(r["M_aero_Nm"]) + hub) / M30, 3),
                   "use_ribner": round(abs(Mrib) / M30, 3),
                   "use_bemt_slope_low": round(abs(Mlo) / M30, 3),
                   "use_hforce_signed": round(abs(Mh) / M30, 3)})
out["quasi_steady"] = qs


# ---- 2b. time-domain pitch-over
PTD = {"m": m, "g": g, "rho": rho, "S": S, "c": c, "b": b, "e": t["e"], "a0": a0, "CLa": t["CLa"],
       "clmax": t["clmax"], "cd0": t["cd0"], "cn90": t["cn90"], "n": t["n"], "D": t["D"], "x_prop": t["x_prop"],
       "cna": t["cna"], "cm_ac": cm_ac, "xnp": t["xnp"], "dl": t["dl"], "tmax": t["tmax"] * g * t["sag"], "z": t["z"],
       "dfrac": 0.30, "Iyy": Iyy, "Vp": Vp, "Cmd_ref": t["Cmd_ref"], "CLd": t["CLd"], "xref": t["xref"],
       "eta": t["eta"], "lo": t["lo"], "li": t["li"], "va": t["va"], "slop": t["slop"], "fpost": t["fpost"]}


def simulate(x_cg, rate=12.0, T0_W=None, wn=6.0, zeta=1.0, kprop=1.0, alt_hold=False, ang_done=70.0, v_assist=14.0):
    """Wave-2: the model now lives in flight_models.pitchover_td (the stored claim CALC-B3-TRANS-TD uses it too)."""
    return FM.pitchover_td(PTD, x_cg, T0_W=T0_W, rate=rate, ang_done=ang_done, v_assist=v_assist, wn=wn, zeta=zeta,
                           kprop=kprop, alt_hold=alt_hold, keep_hist=True)


cases = {}
X = {"fwd": t["x_fwd"], "x0420": 0.0420, "ff_fwd": 0.0453, "ff_aft": 0.0465, "target": t["x_t"], "aft": 0.05133}
for xk, xv in X.items():
    cases[f"ap_hoverthr_r12_{xk}"] = simulate(xv)
    cases[f"b1_althold_r12_{xk}"] = simulate(xv, alt_hold=True)
for r in (8.0, 16.0, 20.0, 25.0, 30.0):
    for xk, xv in X.items():
        cases[f"ap_hoverthr_r{r:.0f}_{xk}"] = simulate(xv, rate=r)
for ang in (50.0, 60.0):
    cases[f"ap_hoverthr_r12_fwd_ang{ang:.0f}"] = simulate(t["x_fwd"], ang_done=ang)
    cases[f"ap_hoverthr_r20_fwd_ang{ang:.0f}"] = simulate(t["x_fwd"], rate=20.0, ang_done=ang)
for tw in (1.15, 1.2, 1.25, 1.3, 1.4, 1.6):
    for xk in ("fwd", "ff_fwd", "target"):
        cases[f"ap_T0W{tw}_r12_{xk}"] = simulate(X[xk], T0_W=tw)
cases["ap_T0W1.3_r12_fwd_bemtprop"] = simulate(t["x_fwd"], T0_W=1.3, kprop=k_prop_lo)
cases["ap_T0W1.3_r16_fwd"] = simulate(t["x_fwd"], T0_W=1.3, rate=16.0)
for wn in (4.0, 10.0):
    cases[f"ap_hoverthr_r12_fwd_wn{wn:.0f}"] = simulate(t["x_fwd"], wn=wn)
cases["ap_hoverthr_r12_fwd_bemtprop"] = simulate(t["x_fwd"], kprop=k_prop_lo)
cases["ap_hoverthr_r20_fwd_bemtprop"] = simulate(t["x_fwd"], rate=20.0, kprop=k_prop_lo)
cases["b1_althold_r12_fwd_bemtprop"] = simulate(t["x_fwd"], alt_hold=True, kprop=k_prop_lo)

summ = {}
for kname, cs in cases.items():
    p = cs["peak"]
    summ[kname] = {"peak_use30": p["use"], "at_t": p["t"], "V": p["V"], "alpha": p["alpha_deg"], "theta": p["theta_deg"],
                   "phase": p["phase"], "M_aero": p["M_aero"], "M_dyn": p["M_dyn"],
                   "sustained_0p5s": cs["sustained_0p5s_use30"], "t_above_0p60_s": cs["t_above_0p60_s"],
                   "t_above_0p80_s": cs["t_above_0p80_s"], "peak_with_gust3": cs["peak_use30_gust"],
                   "peak_elev_cons": cs["peak_use30_elev_cons"], "t_done_s": cs["t_done_s"],
                   "peak_pitchover": cs["peak_pitchover"], "sustained_pitchover": cs["sustained_pitchover"],
                   "V_done": cs["V_done"], "trim_only_po": round(cs["max_trim_only_pitchover"], 3),
                   "lower_motor_N": round(cs["lower_motor_N_at_peak"], 2) if cs["lower_motor_N_at_peak"] is not None else None,
                   "peak_fw_assist": cs["peak_fw_assist"], "t_fw_assist_gt0p60": cs["t_fw_assist_above_0p60_s"],
                   "t_stalled_fw": cs["t_stalled_fw_s"],
                   "alt_change_m": cs["alt_change_m"], "V_end": cs["V_end"], "t_end": cs["t_end"]}
out["td_summary"] = summ
out["td_hist_ap_hoverthr_r12_fwd"] = cases["ap_hoverthr_r12_fwd"]["hist"]
out["td_hist_b1_althold_r12_fwd"] = cases["b1_althold_r12_fwd"]["hist"]
out["td_hist_ap_T0W1.3_r12_fwd"] = cases["ap_T0W1.3_r12_fwd"]["hist"]

# ---- 2c. reserve that the 0.60 is meant to hold, derived at the quasi-steady worst point (fwd, 11 m/s level)
r = FM.transition_point(11.0, m, g, rho, S, c, t["x_fwd"], t["xnp"], cm_ac, t["CLa"], a0, t["clmax"], t["cd0"], k_ind,
                        t["cn90"], t["n"], t["D"], t["x_prop"], t["cna"], t["tmax"] * g * t["sag"], t["z"], 0.0,
                        t["dl"], 0.0, 0.0, t["fpost"])
al = r["alpha_deg"] * DEG
M0 = aero_moment(11.0, al, t["x_fwd"])[0]
res = {}
for gw in (2.0, 3.0):
    da = math.atan(gw / 11.0)
    res[f"gust_{gw:.0f}ms_Nm"] = max(abs(aero_moment(11.0, al + da, t["x_fwd"])[0] - M0),
                                     abs(aero_moment(11.0, al - da, t["x_fwd"])[0] - M0))
res["rate_reserve_Nm"] = IH["amin"] * Iyy             # R-HOVER-AUTHORITY floor 2.0 rad/s2 on the pitch axis
res["reserve_3ms_frac_of_cap30"] = (res["gust_3ms_Nm"] + res["rate_reserve_Nm"]) / M30
res["reserve_2ms_frac_of_cap30"] = (res["gust_2ms_Nm"] + res["rate_reserve_Nm"]) / M30
out["reserve_at_qs_worst"] = res

# ---- 2d. differential caps that pass 0.60 for given trims (information)
out["cap_for_0p60"] = {k: v["peak_use30"] * 0.30 / 0.60 for k, v in summ.items()}

(HERE / "results" / "round1114.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

# ------------------------------------------------------------------------------------------- print
print("yaw: cant %.1f ratio20 %.3f (@7 %.3f @10 %.3f) ; cant for 1.5: %.2f deg ; dfrac needed: %.3f" % (
    CANT0, out["yaw_repro_ratio20_params"], out["yaw_repro_ratio20_7"], out["yaw_repro_ratio20_10"],
    out["yaw_cant_for_1p5_deg"], out["yaw_dfrac_needed_at_params"]))
for s in sweep:
    print("  ", s)
print("M30 %.4f Iyy %.4f Vp %.2f rib %.3f bemt %.3f" % (M30, Iyy, Vp, rib_slope_15p6, dHdi))
for row in qs:
    print("  qs", row)
print("reserve", res)
for kname, s in summ.items():
    print("%-30s po %.3f trim %.3f sus %.3f | Vdone %s lowerN %s | fwA %.3f tfw>.6 %.2f stall %.2f | dh %.1f tdone %.2f" % (
        kname, s["peak_pitchover"], s["trim_only_po"], s["sustained_pitchover"], s["V_done"], s["lower_motor_N"],
        s["peak_fw_assist"], s["t_fw_assist_gt0p60"], s["t_stalled_fw"], s["alt_change_m"], s["t_done_s"] or -1))
