"""Run one A hover case: ArduPlane SITL (JSON backend) + a_plant.py, then summarise. Run with the venv python that has pymavlink.
usage: run_case.py <tag> [key=value ...]
  keys: wind (m/s) from (deg, wind FROM direction; belly faces 0) mass gust gust_at turb hold thrust_scale cant seed mode
        P:NAME=VALUE  -> override a parameter in the SITL defaults
Environment: SCR = folder holding sitl/ (ArduPlane.elf + cyg*.dll), src/quadplane.parm. Outputs in runs/<tag>/ next to this file."""
import json, math, os, subprocess, sys, time
from pymavlink import mavutil

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.environ["SCR"]
SITL = os.path.join(SCR, "sitl")
tag = sys.argv[1]
kv = dict(a.split("=", 1) for a in sys.argv[2:] if not a.startswith("P:"))
pov = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("P:"))
run = os.path.join(HERE, "runs", tag); os.makedirs(run, exist_ok=True)
for f in os.listdir(run):
    if f in ("eeprom.bin", "mav.parm") or f.endswith(".log"):
        try: os.remove(os.path.join(run, f))
        except OSError: pass

# ---- SITL defaults: A.param minus board-only names, plus SIM-only overrides (listed in SITL-A.md)
PARAM = os.path.join(HERE, "..", "A.param")
SKIP = ("SERVO_BLH", "SERVO_DSHOT", "SERIAL", "RSSI", "INS_HNTCH", "INS_LOG", "BATT_", "ARSPD_", "COMPASS", "INS_POS", "GPS1_POS",
        "AHRS_ORIENTATION", "RC9_OPTION", "RC5_OPTION", "RC_OPTIONS", "FLTMODE_CH", "FLTMODE", "Q_M_PWM_TYPE", "BRD_", "INITIAL_MODE")
lines = []
for ln in open(PARAM, encoding="utf-8"):
    s = ln.strip()
    if not s or s.startswith("#") or "," not in s: continue
    k, v = [x.strip() for x in s.split(",", 1)]
    if any(k.startswith(p) for p in SKIP): continue
    lines.append((k, v))
over = dict(Q_M_PWM_TYPE=0, BATT_MONITOR=0, ARSPD_TYPE=0, ARMING_CHECK=0, FLTMODE_CH=6, FLTMODE1=17, FLTMODE2=5, FLTMODE3=7, FLTMODE4=18,
            FLTMODE5=11, FLTMODE6=19, SERVO5_MIN=1000, SERVO5_MAX=2000, SERVO6_MIN=1000, SERVO6_MAX=2000, SIM_SPEEDUP=1, FENCE_ENABLE=0,
            THR_FAILSAFE=0, FS_GCS_ENABL=0, SIM_RC_FAIL=0, RNGFND1_TYPE=0, EK3_ENABLE=1)
over.update(pov)
d = {k: v for k, v in lines}; d.update({k: str(v) for k, v in over.items()})
dfile = os.path.join(run, "A_sitl.parm")
open(dfile, "w").write("\n".join(f"{k} {v}" for k, v in d.items()) + "\n")

cfg = dict(out=os.path.join(run, "case"), wind=float(kv.get("wind", 0)), wind_from_deg=float(kv.get("from", 0)), mass=float(kv.get("mass", 1.23)),
           gust=float(kv.get("gust", 0)), gust_at=float(kv.get("gust_at", 20)), turb=float(kv.get("turb", 0)), hold_s=float(kv.get("hold", 60)),
           thrust_scale=float(kv.get("thrust_scale", 0.767)), cant_deg=float(kv.get("cant", 14)), seed=int(kv.get("seed", 1)), arm=float(kv.get("arm", 1)), wing_s=float(kv.get("wing_s", 1)),
           fin_s=float(kv.get("fin_s", 1)), inst=int(kv.get("inst", 0)))
INST = int(kv.get("inst", 0))
plant = subprocess.Popen([sys.executable, os.path.join(HERE, "a_plant.py"), json.dumps(cfg)], stdout=open(os.path.join(run, "plant.log"), "w"),
                         stderr=subprocess.STDOUT)
time.sleep(1.0)
env = dict(os.environ); env["PATH"] = SITL + os.pathsep + env["PATH"]
args = [os.path.join(SITL, "ArduPlane.elf"), "--model", "JSON:127.0.0.1", "--defaults", os.path.join(SCR, "src", "quadplane.parm") + "," + dfile,
        "--home", "37.9150,-122.3340,5,0", "--speedup", kv.get("speedup", "8"), "--wipe", "-I%d" % INST]
sitl = subprocess.Popen(args, cwd=run, env=env, stdout=open(os.path.join(run, "sitl.log"), "ab"), stderr=subprocess.STDOUT)
time.sleep(2)
m = mavutil.mavlink_connection("tcp:127.0.0.1:%d" % (5760 + 10 * INST), source_system=255)
m.wait_heartbeat(timeout=60)
for i in range(13): m.mav.request_data_stream_send(m.target_system, m.target_component, i, 10, 1)
rc = [1500, 1500, 1000, 1500, 1000, 1167, 1500, 1500, 1000]
st = dict(alt=0.0, armed=False, mode=None, t=0.0)
events = []; last = [0.0]
def pump(block=0.02):
    if time.time() - last[0] > 0.04:
        m.mav.rc_channels_override_send(m.target_system, m.target_component, *rc[:8], rc[8], *([0] * 9)); last[0] = time.time()
    msg = m.recv_match(blocking=True, timeout=block)
    if msg is None: return
    t = msg.get_type()
    if t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system: st["mode"] = msg.custom_mode; st["armed"] = bool(msg.base_mode & 128)
    elif t == "GLOBAL_POSITION_INT": st["alt"] = msg.relative_alt / 1000.0
    elif t == "ATTITUDE": st["t"] = msg.time_boot_ms / 1000.0
    elif t == "STATUSTEXT": events.append([round(st["t"], 1), msg.text])
def run_for(sec, cond=None):
    t0 = st["t"]; w0 = time.time()
    while st["t"] - t0 < sec and time.time() - w0 < 900 and plant.poll() is None:
        pump()
        if cond and cond(): return True
    return False
res = dict(tag=tag, cfg=cfg, overrides=pov, events=events)
def getp(name):
    for _ in range(3):
        m.mav.param_request_read_send(m.target_system, m.target_component, name.encode(), -1)
        t0 = time.time()
        while time.time() - t0 < 2:
            msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
            if msg and msg.param_id == name: return msg.param_value
    return None
try:
    res["readback"] = {k: getp(k) for k in ("Q_ANGLE_MAX", "Q_A_ANGLE_MAX", "Q_LOIT_ANG_MAX", "Q_M_SPIN_MAX", "Q_M_THST_EXPO", "Q_A_RAT_RLL_P",
                                            "Q_A_RAT_YAW_P", "Q_FRAME_CLASS", "Q_TAILSIT_ENABLE", "Q_WVANE_ENABLE", "Q_A_ANGLE_BOOST", "Q_TAILSIT_DSKLD",
                                            "Q_P_NE_VEL_I", "Q_P_NE_VEL_IMAX", "Q_P_NE_VEL_D", "Q_P_ACC_XY_P", "Q_P_ACC_XY_I", "Q_PILOT_ACCEL", "Q_PILOT_SPD_UP", "Q_LOIT_ANG_MAX", "Q_P_NE_POS_P", "Q_P_NE_VEL_P", "Q_TAILSIT_MOTMX")}
    run_for(30)                                              # EKF settle
    m.mav.command_long_send(m.target_system, m.target_component, 400, 0, 1, 21196, 0, 0, 0, 0, 0)
    run_for(5, lambda: st["armed"])
    rc[5] = 1556; run_for(3)                                  # R9 slot 4 = QHOVER
    res["armed"] = st["armed"]; res["mode_after_arm"] = st["mode"]
    rc[2] = 1850                                              # climb
    ok = run_for(120, lambda: st["alt"] >= 19.0); res["reached_alt"] = ok
    rc[2] = 1500; run_for(3); rc[5] = int(kv.get("modepwm", 1817)); run_for(2)   # slot 6 = QLOITER
    res["mode_hold"] = st["mode"]
    while plant.poll() is None and time.time() < time.time() + 1:
        pump(0.05)
finally:
    try: plant.wait(timeout=5)
    except Exception: plant.kill()
    try: m.close()
    except Exception: pass
    sitl.terminate()
    try: sitl.wait(10)
    except Exception: sitl.kill()

# ---- summary from the plant's 20 Hz truth log
rows = []
try:
    for ln in open(cfg["out"] + ".csv").read().splitlines()[1:]:
        rows.append([float(x) for x in ln.split(",")])
except OSError: pass
if rows:
    CAP = 0.895; FLOOR = 0.16
    pre = [r for r in rows if r[0] < 0]; w = [r for r in rows if r[0] >= 8.0]
    def stat(xs): return (min(xs), max(xs), sum(xs) / len(xs)) if xs else (None, None, None)
    dt = 0.05
    umax = [max(r[6:10]) for r in w]; umin = [min(r[6:10]) for r in w]
    run_len = best = 0
    for u in umax:
        run_len = run_len + 1 if u >= CAP else 0; best = max(best, run_len)
    runf = bestf = 0
    for u in umin:
        runf = runf + 1 if u <= FLOOR else 0; bestf = max(bestf, runf)
    spread = [abs((r[6] + r[7]) / 2 - (r[8] + r[9]) / 2) / max(0.05, sum(r[6:10]) / 4) for r in w]
    ye = [abs(r[3]) for r in w]; pe = [r[4] for r in w]; ln_ = [r[2] for r in w]
    last20 = [r for r in w if r[0] >= w[-1][0] - 20]
    res["summary"] = dict(
        n=len(w), t_window=[w[0][0], w[-1][0]], wind_ms=round(max(r[1] for r in w), 2),
        lean_max=round(max(ln_), 1), lean_mean=round(sum(ln_) / len(ln_), 1), lean_pre=round(sum(r[2] for r in pre) / len(pre), 1) if pre else None,
        u_max=round(max(umax), 3), u_mean_max=round(sum(umax) / len(umax), 3), t_cap_s=round(sum(1 for u in umax if u >= CAP) * dt, 2),
        t_cap_run_s=round(best * dt, 2), t_ge85_s=round(sum(1 for u in umax if u >= 0.85) * dt, 2), u_min=round(min(umin), 3),
        t_floor_s=round(sum(1 for u in umin if u <= FLOOR) * dt, 2), t_floor_run_s=round(bestf * dt, 2),
        yaw_err_max=round(max(ye), 1), yaw_err_rms=round(math.sqrt(sum(x * x for x in ye) / len(ye)), 2),
        pos_err_max=round(max(pe), 2), pos_err_rms=round(math.sqrt(sum(x * x for x in pe) / len(pe)), 2),
        pos_err_last20_mean=round(sum(r[4] for r in last20) / len(last20), 2), alt_dev_max=round(max(abs(r[5]) for r in w), 2),
        diag_spread_max=round(max(spread), 3), diag_spread_mean=round(sum(spread) / len(spread), 3))
else:
    res["summary"] = None
json.dump(res, open(os.path.join(run, "result.json"), "w"), indent=1)
with open(os.path.join(HERE, "results.jsonl"), "a") as f:
    f.write(json.dumps(dict(tag=tag, args=sys.argv[2:], summary=res["summary"], armed=res.get("armed"), reached_alt=res.get("reached_alt"))) + "\n")
print(json.dumps(dict(tag=tag, args=sys.argv[2:], summary=res["summary"], armed=res.get("armed"), reached_alt=res.get("reached_alt"),
                      events=[e for e in events if "PreArm" in e[1] or "rror" in e[1] or "ailsafe" in e[1]][:8]), indent=0))
