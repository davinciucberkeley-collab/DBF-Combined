"""B3 final re-run 2026-11-14 (closure round): hover duty against Q_TAILSIT_THR_VT, entry fraction on E1's worst-state T/W,
static margin over the CG range with the turbulator. Writes results/final_rerun.json only.

Reads (read-only): params.json, subsystems/flight-software/params.json, team/B4/props.py (X2814 V3 + APC 11x8E with E1's kT / kP),
team/B4/claims.json (hover rpm, torque), team/E1/claims.json (motor constants, worst-state T/W), team/B3/claims.json
(entry band T0), results/d163.json (neutral point, tripped).
Run:  python -I redesign/team/B3/final_rerun.py   (after sc_analysis.py, d163.py)
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
sys.path.insert(0, str(TEAM / "B4"))
sys.path.insert(0, str(TEAM.parent / "proofs"))
import props as pp  # noqa: E402


def nodes(p):
    return {n["id"]: n for n in json.load(open(p, encoding="utf-8"))["nodes"]}


PAR = json.load(open(TEAM.parent / "params" / "params.json", encoding="utf-8"))
FSW = json.load(open(TEAM.parent / "subsystems" / "flight-software" / "params.json", encoding="utf-8"))
B4, E1, B3 = nodes(TEAM / "B4/claims.json"), nodes(TEAM / "E1/claims.json"), nodes(HERE / "claims.json")
D163 = json.load(open(HERE / "results" / "d163.json", encoding="utf-8"))
pv = lambda *p: __import__("functools").reduce(lambda d, k: d[k], p, PAR)["value"]
fs = FSW["fsw"] if "fsw" in FSW else FSW

m = pv("requirements", "mtow_gate_kg")
c = pv("wing", "chord_m")
x_fwd, x_aft = pv("cg", "x_range_m")
kv, rm, i0 = (E1[k]["value"] for k in ("ASM-E1-KV", "ASM-E1-RM", "ASM-E1-I0"))
esc_r, esc_w = E1["ASM-E1-ESC"]["value"]
pack_r, av_a = E1["ASM-E1-PACK"]["value"]
rho, g = pv("env", "rho_kgm3"), pv("env", "g_ms2")
cant = pv("propulsion", "stations", "cant_deg")
kdl = pv("propulsion", "download_factor")
out = {"_note": "B3 final re-run, EST where marked; hover duty from B4's X2814 + 11x8E model (E1 kT/kP), pack R from E1 ASM-E1-PACK"}

# ------------------------------------------------------------ hover duty at the gate, three pack states
T = kdl * m * g / 4 / math.cos(math.radians(cant))
rpm = pp.rpm_for_thrust("11x8E", T, 0.0, rho)
Pw = pp.thrust_power("11x8E", rpm, 0.0, rho)[1]
Q = Pw / (2 * math.pi * rpm / 60)
kt = 60 / (2 * math.pi * kv)
Im = Q / kt + i0
v_term = rpm / kv + Im * (rm + esc_r)                     # terminal voltage per motor, 25 degC winding
hov = {"rpm": rpm, "T_per_prop_N": T, "Q_Nm": Q, "I_motor_A": Im, "V_terminal_V": v_term}
vmax_ref = fs["fwd_bat_volt_max_v"]["value"]
rows = {}
for lab, ocv in (("fresh_17p4V", 17.4), ("mid_15p2V", 15.2), ("low_14p4V", 14.4)):
    vb = ocv
    for _ in range(60):
        duty = v_term / vb
        ip = 4 * duty * Im + av_a
        vb = ocv - ip * pack_r
    rows[lab] = {"duty": duty, "bus_V": vb, "pack_A": ip, "THR_VT_over_duty": 0.55 / duty}
hov["pack_states"] = rows
hov["compensated_throttle_ref_17p4V"] = v_term / vmax_ref        # Q_M_BAT_VOLT_MAX = 17.4 basis
hov["THR_VT_over_compensated_hover"] = 0.55 / hov["compensated_throttle_ref_17p4V"]
hov["Q_TAILSIT_THR_VT"] = 0.55
hov["Q_M_THST_HOVER_param"] = 0.49
out["hover_duty"] = hov

# ------------------------------------------------------------ entry fraction on E1's worst-state T/W
tw_w = E1["CL-E1-TW-WORST-RBAND"]["value"]
t_hi = B3["CL-B3-TRANS-T0-HIGH"]["value"]
out["entry"] = {"T0_W_high": t_hi, "T0_W_low": B3["CL-B3-TRANS-T0-LOW"]["value"], "E1_worst_TW_band_edge": tw_w,
                "frac_E1": t_hi / tw_w, "frac_E1_thrust_magnitude": t_hi / (tw_w / math.cos(math.radians(cant))),
                "frac_B3_params_formula": B3["CL-B3-TRANS-ENTRY-FRAC-SAG"]["value"], "limit": 0.80,
                "params_tmax_kg": pv("propulsion", "thrust_max_per_motor_kg"), "params_sag": pv("propulsion", "voltage_sag")}

# ------------------------------------------------------------ static margin over the CG range, tripped (design state) and free
cases = D163["cg_cases"]
sm = {}
for lab in ("tripped", "model_of_record", "free_transition"):
    xnp = cases[lab]["xnp"]
    sm[lab] = {"xnp_m": xnp, "SM_fwd": (xnp - x_fwd) / c, "SM_aft": (xnp - x_aft) / c, "x_aft_sm5_m": cases[lab]["x_aft_sm5"],
               "aft_limit_margin_mm": 1000 * (cases[lab]["x_aft_sm5"] - x_aft), "binding_speed": cases[lab]["binding_speed"]}
sm["cg_range_m"] = [x_fwd, x_aft]
sm["x_fwd_stall_trim_m"] = D163["chamfer"]["after"]["x_fwd"]
sm["fwd_margin_mm"] = 1000 * (x_fwd - D163["chamfer"]["after"]["x_fwd"])
sm["sm_min_required"] = pv("requirements", "static_margin_min")
out["static_margin"] = sm
(HERE / "results" / "final_rerun.json").write_text(json.dumps(out, indent=1, default=float) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1, default=float))
