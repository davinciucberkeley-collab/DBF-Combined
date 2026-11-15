"""B1 final re-run 2026-11-14 (closure round). Writes only closure_final_results.json beside this file.

Hardware basis (params.json, D-173/D-174): SunnySky X2814 V3 KV900 + APC 11x8E/EP, 2.70 kg gate, cant 10 deg, limiter 80 A,
Gens Ace LiHV 4S (17.4 V full), THR_MAX 41 with FWD_BAT compensation (F4 D-174). Prop table = B4's PER3 11x8E block with E1's
calibrated factors kT / kP (team/E1/claims.json CL-E1-KT / CL-E1-KP) through team/B4/props.py (read-only import).
Aero = B1's as-designed polar (team/B1/claims.verify.json CALC-B1V-CRUISE: CD0 0.0577, k 0.1042, trim 1.02) + B2's lower-surface
turbulator dCD0 +0.0040 (CL-B2C-TRIP-DCD, EST; B1's 1.10 tape factor already carries ~0.0007 of it, so this is conservative).
Parts:
  1. cruise power at 17 m/s, 2.70 kg, base and pessimistic, with and without the turbulator
  2. pitch-over / transition with the firmware's held throttle (B3 CL-1): T = T0 x lapse(V) from the mode change to
     Q_TAILSIT_ANGLE, T0 = B3's entry band edges; thrust fraction against E1's worst-state T/W
  3. fixed-wing climb at THR_MAX 41 with FWD_BAT compensation, fresh 17.4 V and sagged 3.6 V/cell packs, against TECS_CLMB_MAX 3
Run:  python -I redesign/team/B1/round-2026-11-14/closure_final.py
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1 = HERE.parent
TEAM = B1.parent
sys.path.insert(0, str(TEAM.parent / "proofs"))
sys.path.insert(0, str(B1))
sys.path.insert(0, str(TEAM / "B4"))
import performance as perf  # noqa: E402  (B1 helpers; main guarded)
import props as pp  # noqa: E402  (B4: 11x8E with E1's factors; main guarded)

DEG = math.pi / 180


def nodes(p):
    return {n["id"]: n for n in json.load(open(p, encoding="utf-8"))["nodes"]}


PAR = json.load(open(TEAM.parent / "params" / "params.json", encoding="utf-8"))
FSW = json.load(open(TEAM.parent / "subsystems" / "flight-software" / "params.json", encoding="utf-8"))


def pv(*path):
    d = PAR
    for k in path:
        d = d[k]
    return d["value"]


def fv(key):
    d = FSW["fsw"][key] if "fsw" in FSW else FSW[key]
    return d["value"]


N = nodes(B1 / "claims.verify.json")
E1 = nodes(TEAM / "E1/claims.json")
B2 = nodes(TEAM / "B2/sim/claims.sim.json")
B3 = nodes(TEAM / "B3/claims.json")
ci = dict(N["CALC-B1V-CRUISE"]["input_values"])
ti = dict(N["CALC-B1V-TRANSITION"]["input_values"])
ai = N["CALC-B1V-AERO"]["input_values"]

g, rho, S = pv("env", "g_ms2"), pv("env", "rho_kgm3"), ci["S"]
M = pv("requirements", "mtow_gate_kg")                    # 2.70
CANT = pv("propulsion", "stations", "cant_deg")           # 10
VC = pv("performance", "cruise_ms")                       # 17
n, D = 4, pv("propulsion", "prop_diameter_m")
CD0_ASD, K_BASE, K_PESS, TRIM = ci["cd0"], ci["k"], ci["k_pess"], ci["trim"]
D_TRIP = B2["CL-B2C-TRIP-DCD"]["value"]                   # +0.0040 (EST)
PESS = ci["pess"]                                         # cd0 x 1.3, prop eta x 0.85, (1.1)
AV, ESC_ETA = ci["av"], ci["esc"]                         # 6 W avionics, ESC 0.95 (B1 chain)
MOT = (E1["ASM-E1-KV"]["value"], E1["ASM-E1-RM"]["value"], E1["ASM-E1-I0"]["value"])   # X2814 V3 (E1 D-173)
KT, KP = pp.KT_E1, pp.KP_E1

# --- prop table [J, Ct, Cp] at 6000 rpm with E1's factors (B4 helper), same format as performance.PROP_TABLE
tab = []
for r in sorted((r for r in pp.DATA["11x8E"] if r["rpm"] == 6000.0), key=lambda r: r["J"]):
    tab.append([r["J"], KT * r["Ct"], KP * r["Cp"]])
out = {"_note": "B1 final re-run (closure_final.py), 2.70 kg, X2814 V3 + APC 11x8E, E1 kT/kP, EST where marked",
       "inputs": {"m_kg": M, "cant_deg": CANT, "V_ms": VC, "cd0_as_designed": CD0_ASD, "k": K_BASE, "k_pess": K_PESS,
                  "trim": TRIM, "dcd0_turbulator": D_TRIP, "kT": KT, "kP": KP, "motor_kv_rm_i0": MOT,
                  "esc_eta": ESC_ETA, "avionics_w": AV, "pess": PESS}}


def cruise(V, cd0, k, pess=False, mass=M, kcal=1.0):
    c0, kk, ef = (cd0 * PESS[0], K_PESS, PESS[1]) if pess else (cd0, k, 1.0)
    return perf.cruise_point(V, mass, g, rho, S, c0, kk, TRIM, n, tab, MOT, kcal, D, ESC_ETA, AV, ef, CANT)


# ---------------------------------------------------------------- 1. cruise power
c1 = {}
for lab, cd0 in (("no_turbulator", CD0_ASD), ("turbulator", CD0_ASD + D_TRIP)):
    b, w = cruise(VC, cd0, K_BASE), cruise(VC, cd0, K_BASE, True)
    c1[lab] = {"cd0": cd0, "P_W": b["p_el_w"], "P_pess_W": w["p_el_w"], "drag_N": b["drag_n"], "LD_eff": M * g / b["drag_n"],
               "J": b["J"], "rpm": b["rpm"], "eta_prop": b["eta_prop"], "t_prop_N": b["t_prop_n"], "CL": b["cl"],
               "drag_pess_N": w["drag_n"], "rpm_pess": w["rpm"]}
c1["delta_turbulator_W"] = c1["turbulator"]["P_W"] - c1["no_turbulator"]["P_W"]
c1["delta_turbulator_N"] = c1["turbulator"]["drag_N"] - c1["no_turbulator"]["drag_N"]
c1["sweep"] = {f"{V:g}": {"P_W": cruise(V, CD0_ASD + D_TRIP, K_BASE, mass=M)["p_el_w"],
                          "P_pess_W": cruise(V, CD0_ASD + D_TRIP, K_BASE, True, mass=M)["p_el_w"]} for V in (16, 17, 18)}
c1["kcal_1p13_sensitivity_W"] = cruise(VC, CD0_ASD + D_TRIP, K_BASE, kcal=ci["kcal"])["p_el_w"]
c1["at_2p64kg_W"] = cruise(VC, CD0_ASD + D_TRIP, K_BASE, mass=2.64)["p_el_w"]
out["cruise"] = c1

# ---------------------------------------------------------------- 2. pitch-over with the held throttle
tw_worst = E1["CL-E1-TW-WORST-RBAND"]["value"]             # worst-state T/W at the gate, band edge (E1: axial thrust / W)
tw_fresh = E1["CL-E1-TW-FRESH-RBAND"]["value"]
T0_hi, T0_lo = B3["CL-B3-TRANS-T0-HIGH"]["value"], B3["CL-B3-TRANS-T0-LOW"]["value"]
vs_trip = B2["CL-B2R3-VS-GATE-FWD-TURB"]["value"]
clmax = 2 * M * g / (rho * S * vs_trip ** 2)
aero = perf.aero_from(ti["cla"], ti["a0"], clmax, CD0_ASD + D_TRIP, ti["k"], ti["cd90"])
W = M * g
tmax_total = tw_worst * W / math.cos(CANT * DEG)          # thrust magnitude, worst state
th_hover = W * pv("propulsion", "download_factor") / 4 / math.cos(CANT * DEG)
rpm_h = pp.rpm_for_thrust("11x8E", th_hover, 0.0, rho)
n_h = rpm_h / 60.0
ct0 = perf.prop_ct(tab, 0.0)


def lapse(Va):
    """Thrust / static thrust at fixed (hover) rpm, from the 11x8E table: Ct(J)/Ct(0), J = Va / (n D)."""
    return perf.prop_ct(tab, Va / (n_h * D)) / ct0


T_HOLD = B3["ASM-B3-TRANS-T0"]["value"][1]                  # B3 entry procedure: pre-climb hold (1.0 s after the final re-run)


def pitchover(T0_W, t_hold=T_HOLD, rate=12.0, ang=70.0, v_assist=14.0, dt=0.005, w_credit=True):
    """Firmware law (B3 section 1.2): throttle frozen at T0 from the mode change to Q_TAILSIT_ANGLE, then the plane
    controller. Pre-climb hold at T0 from B3's ASM-B3-TRANS-T0. 2-D point mass with B1's aero; pitch ramp RAT_FW."""
    T0 = min(T0_W * W, tmax_total)
    u = 0.0
    w = (T0_W - 1.0) * g * t_hold if w_credit else 0.0
    h = 0.5 * (T0_W - 1.0) * g * t_hold ** 2 if w_credit else 0.0
    th, t = 90.0, 0.0
    phase, v_done, t_done = "po", None, None
    h_max = h_min = h
    tf_max = 0.0
    t_vt = t_vc = None
    while t < 30.0:
        V = math.hypot(u, w)
        gam = math.atan2(w, u) / DEG if V > 0.05 else 0.0
        a = th - gam
        cl, cd = aero(a)
        q = 0.5 * rho * V * V * S
        L, Dr = q * cl, q * cd
        lx, lz = -L * math.sin(gam * DEG), L * math.cos(gam * DEG)
        dx, dz = -Dr * math.cos(gam * DEG), -Dr * math.sin(gam * DEG)
        va = max(0.0, V * math.cos(a * DEG))
        tmax_v = tmax_total * lapse(va)
        c, s = math.cos(th * DEG), math.sin(th * DEG)
        if phase == "po":
            T = min(T0 * lapse(va), tmax_v)
            th_cmd = 90.0 - rate * t
            if 90.0 - th > ang:
                phase, v_done, t_done = "fw", V, t
        if phase == "fw":
            if V < v_assist:
                T = min(max((m_ * (g + 0.0) - lz - dz) / max(s, 0.05), 0.0), tmax_v)      # copter-assisted altitude hold
            else:
                T = min(max(M * 0.8 * (VC - V) - lx - dx, 0.0) / max(c, 0.05), tmax_v)
            q2 = 0.5 * rho * (u * u + w * w) * S
            th_req, aa = 90.0, ti["a0"] * 0 - 1.0
            while aa < 90.0:
                if q2 * aero(aa)[0] + 0.8 * tmax_v * math.sin(aa * DEG) >= W:
                    th_req = aa
                    break
                aa += 0.5
            th_cmd = max(90.0 - rate * t, th_req)
        tf_max = max(tf_max, T / tmax_total)
        ax = (T * c + lx + dx) / M
        az = (T * s + lz + dz) / M - g
        u += ax * dt
        w += az * dt
        h += w * dt
        th += max(-rate * dt, min(rate * dt, th_cmd - th))
        t += dt
        h_max, h_min = max(h_max, h), min(h_min, h)
        Vn = math.hypot(u, w)
        if t_vt is None and Vn >= pv("requirements", "transition_factor") * vs_trip:
            t_vt = t
        if t_vc is None and Vn >= VC - 0.3:
            t_vc = t
        if t_vc is not None and t > t_vc + 1.0:
            break
    return {"T0_W": T0_W, "T0_N": T0, "V_at_handover_ms": v_done, "t_handover_s": t_done, "t_to_1p3Vs_s": t_vt,
            "t_to_cruise_s": t_vc, "alt_gain_max_m": h_max, "alt_min_m": h_min, "thrust_frac_max_of_worst": tf_max,
            "V_end": math.hypot(u, w)}


m_ = M
po = {"low_edge": pitchover(T0_lo), "high_edge": pitchover(T0_hi), "low_edge_no_preclimb": pitchover(T0_lo, w_credit=False)}
po["frac_entry_vs_E1_worst_TW"] = T0_hi / tw_worst                       # B3 / F4 convention (no cos(cant) credit)
po["frac_entry_vs_E1_worst_thrust_magnitude"] = T0_hi / (tw_worst / math.cos(CANT * DEG))
po["frac_entry_vs_B3_params_tmax_sag"] = B3["CL-B3-TRANS-ENTRY-FRAC-SAG"]["value"]
po["E1_worst_TW_band_edge"] = tw_worst
po["E1_fresh_TW_band_edge"] = tw_fresh
po["T0_W_hi_lo"] = [T0_hi, T0_lo]
po["clmax_used"] = clmax
po["vs_trip_fwd_ms"] = vs_trip
po["hover_rpm"] = rpm_h
po["pre_climb_hold_s"] = T_HOLD
po["lapse_at_12ms"] = lapse(12.0)
po["control_reserve_limit"] = 0.80
out["pitchover"] = po

# ---------------------------------------------------------------- 3. fixed-wing climb at THR_MAX 41 with FWD_BAT compensation
thr = fv("thr_max_pct") / 100.0
vfwd = fv("fwd_bat_volt_max_v")
vrest_low, vload_low = 14.4, 13.9                                   # 3.6 V/cell resting; F4 D-174 loaded bus
r_hot = MOT[1] * (1 + 0.00393 * 55) + 0.010
mot_hot = pp.Motor(MOT[0], MOT[2], r_hot)
cl_ = {}
for lab, duty, vbus in (("fresh_17p4V", thr, vfwd), ("sagged_3p6Vpc", thr * vfwd / vrest_low, vload_low)):
    rpm = mot_hot.full_throttle_rpm("11x8E", duty * vbus, VC, rho)
    T = pp.thrust_power("11x8E", rpm, VC, rho)[0]
    row = {}
    for mass_lab, mass in (("2.70kg", M),):
        for cd_lab, cd0 in (("turbulator", CD0_ASD + D_TRIP), ("no_turbulator", CD0_ASD)):
            clv = 2 * mass * g / (rho * VC * VC * S)
            drag = 0.5 * rho * VC * VC * S * (cd0 + K_BASE * clv * clv) * TRIM
            thrust_ax = 4 * T * math.cos(CANT * DEG)
            roc = (thrust_ax - drag) * VC / (mass * g)
            row[f"{mass_lab}_{cd_lab}"] = {"drag_N": drag, "thrust_axial_N": thrust_ax, "ROC_ms": roc}
    cl_[lab] = {"output": duty, "bus_V": vbus, "rpm": rpm, "thrust_per_motor_N": T, **row}
dp = cruise(VC, CD0_ASD + D_TRIP, K_BASE, True)
clv = 2 * M * g / (rho * VC * VC * S)
drag_p = 0.5 * rho * VC * VC * S * (CD0_ASD * PESS[0] + K_PESS * clv * clv) * TRIM
for lab in cl_:
    T = cl_[lab]["thrust_per_motor_N"]
    cl_[lab]["ROC_pess_drag_ms"] = (4 * T * math.cos(CANT * DEG) - drag_p) * VC / W
cl_["TECS_CLMB_MAX_ms"] = 3.0
cl_["F4_est_sagged_ms"] = 2.9
out["climb"] = cl_
(HERE / "closure_final_results.json").write_text(json.dumps(out, indent=1, default=float) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("cruise", "pitchover", "climb")}, indent=1, default=float)[:6000])
