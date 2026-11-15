"""Print the case table (markdown) from runs/*/result.json and a pass / marginal / fail per case.
Limits (EST, stated in SITL-A.md): lean <= 40 deg (Q_A_ANGLE_MAX 45 - 5 deg margin); motor at the 0.90 cap for one run <= 1.0 s;
motor at the floor (<= 0.16) one run <= 0.5 s; yaw error <= 10 deg; diagonal-pair spread <= 30 % marginal, > 40 % fail (40 % of mean throttle = the sizing's 30 % thrust differential); position error: K09-L S3 line 1 m (95 %) is shown, not gated."""
import glob, json, os
H = os.path.dirname(os.path.abspath(__file__))
ORDER = ["w0", "b3", "b5", "b7", "e3", "e5", "e7", "d3", "d5", "d7", "gb", "ge", "tb", "m137b", "m137e", "t20_5", "t20_7", "d7c16", "b5pos"]
def verdict(s):
    if s is None: return "NO DATA"
    fail = []; marg = []
    if s["lean_max"] > 40: fail.append("lean")
    elif s["lean_max"] > 36: marg.append("lean")
    if s["t_cap_run_s"] > 1.0: fail.append("cap")
    elif s["t_cap_s"] > 0.0: marg.append("cap")
    if s["t_floor_run_s"] > 0.5: fail.append("floor")
    elif s["t_floor_s"] > 0.0: marg.append("floor")
    if s["yaw_err_max"] > 10: fail.append("yaw")
    elif s["yaw_err_max"] > 5: marg.append("yaw")
    if s["diag_spread_max"] > 0.40: fail.append("spread")          # 0.40 = the sizing's authority line (30 % thrust differential, both ways)
    elif s["diag_spread_max"] > 0.30: marg.append("spread")        # 0.30 = K09-L S20 line
    if fail: return "FAIL (" + ",".join(fail) + ")"
    if marg: return "MARGINAL (" + ",".join(marg) + ")"
    return "PASS"
print("| case | wind | lean max / mean | u max | s at cap (run) | u min / s at floor | yaw err max / rms | pos err max / rms / last-20 mean | spread max | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|")
for tag in ORDER:
    f = os.path.join(H, "runs", tag, "result.json")
    if not os.path.exists(f): continue
    r = json.load(open(f)); s = r["summary"]; c = r["cfg"]
    if s is None: print(f"| {tag} | - | no data |"); continue
    print(f"| {tag} | {c['wind']:.0f} from {c['wind_from_deg']:.0f}, m {c['mass']}"
          f"{', gust +%.0f' % c['gust'] if c['gust'] else ''}{', turb %.1f' % c['turb'] if c['turb'] else ''} | {s['lean_max']} / {s['lean_mean']} | {s['u_max']} | "
          f"{s['t_cap_s']} ({s['t_cap_run_s']}) | {s['u_min']} / {s['t_floor_s']} | {s['yaw_err_max']} / {s['yaw_err_rms']} | "
          f"{s['pos_err_max']} / {s['pos_err_rms']} / {s['pos_err_last20_mean']} | {s['diag_spread_max']} | {verdict(s)} |")
