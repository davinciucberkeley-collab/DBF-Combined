"""QP-3 forward-flight SITL driver for concept A: ArduPlane SITL (JSON backend) + a_plant.py in fwd=1 mode (APC prop, full-alpha wing, elevons, fins).
usage: run_fwd.py <tag> case=<name> [key=value ...]        (venv python with pymavlink; env SCR as for run_case.py)
cases: trans    hover to 50 m, entry (held throttle, pre-climb, FBWA), cruise, optional chain=1: back-transition into wind, descent, QLAND
       land     hover at 20 m, QLAND (wind and heading from the keys)
       takeoff  wind from t=5 s, arm, climb in QHOVER to 12 m
       battH / battC   battery low in hover / in cruise;  rcH / rcC  RC loss in hover / cruise;  moH / moC  motor 1 out in hover / cruise
keys: fw_hold(s, FBWA override held after "Transition FW done", default 3.0, T-101) mass wind from(deg, wind FROM; belly = 0 = the flight direction) turb gust seed r(entry T/W, default window centre) preclimb(s, 1.0) vrest slip inst
      speedup  chain  yawcmd(s of full yaw stick to go edge-on after the back-transition, default 0) es5 es6 tmax P:NAME=VALUE (SITL param override)
Outputs: runs/<tag>/ (fwd.csv from the plant, result.json) and one line in results_fwd.jsonl."""
import json, math, os, subprocess, sys, time
from pymavlink import mavutil

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import a_aero as AE
SCR = os.environ["SCR"]; SITL = os.path.join(SCR, "sitl")
tag = sys.argv[1]
kv = dict(a.split("=", 1) for a in sys.argv[2:] if not a.startswith("P:"))
pov = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("P:"))
case = kv.get("case", "trans"); MASS = float(kv.get("mass", 1.50)); INST = int(kv.get("inst", 0))
run = os.path.join(HERE, "runs", tag); os.makedirs(run, exist_ok=True)
for f in os.listdir(run):
    if f in ("eeprom.bin", "mav.parm", "cmd.json") or f.endswith(".log") or f.endswith(".csv") or f.endswith(".events.json"):
        try: os.remove(os.path.join(run, f))
        except OSError: pass

# ---------------------------------------------------------------- parameters: A.param minus board-only lines, plus SIM-only overrides
PARAM = os.path.join(HERE, "..", "A.param")
SKIP = ["SERVO_BLH", "SERVO_DSHOT", "SERIAL", "RSSI", "INS_HNTCH", "INS_LOG", "BATT_", "ARSPD_", "COMPASS", "INS_POS", "GPS1_POS", "AHRS_ORIENTATION",
        "RC9_OPTION", "RC5_OPTION", "RC_OPTIONS", "FLTMODE_CH", "FLTMODE", "Q_M_PWM_TYPE", "BRD_", "INITIAL_MODE"]
batt_case = case in ("battH", "battC")
rc_case = case in ("rcH", "rcC")
KEEP = ("BATT_FS_", "BATT_LOW", "BATT_CRT", "BATT_CAPACITY") if batt_case else ()
d = {}
for ln in open(PARAM, encoding="utf-8"):
    s = ln.strip()
    if not s or s.startswith("#") or "," not in s: continue
    k, v = [x.strip() for x in s.split(",", 1)]
    if any(k.startswith(p) for p in SKIP) and not any(k.startswith(p) for p in KEEP): continue
    d[k] = v
over = dict(Q_M_PWM_TYPE=0, BATT_MONITOR=4 if batt_case else 0, ARSPD_TYPE=100, ARSPD_USE=1, ARSPD_AUTOCAL=0, ARMING_CHECK=0, FLTMODE_CH=6, FLTMODE1=17, FLTMODE2=5,
            FLTMODE3=7, FLTMODE4=18, FLTMODE5=11, FLTMODE6=19, SERVO5_MIN=1000, SERVO5_MAX=2000, SERVO6_MIN=1000, SERVO6_MAX=2000, SIM_SPEEDUP=1, FENCE_ENABLE=0,
            THR_FAILSAFE=1 if rc_case else 0, FS_GCS_ENABL=0, SIM_RC_FAIL=0, RNGFND1_TYPE=0, EK3_ENABLE=1)
if batt_case: over.update(BATT_VOLT_MULT=10.1, BATT_AMP_PERVLT=17, SIM_BATT_VOLTAGE=16.8, BATT_ARM_VOLT=0)
over.update(pov)
d.update({k: str(v) for k, v in over.items()})
dfile = os.path.join(run, "A_sitl.parm")
open(dfile, "w").write("\n".join(f"{k} {v}" for k, v in d.items()) + "\n")
P = lambda k, dflt: float(d.get(k, dflt))
SPIN_MIN, SPIN_MAX, EXPO_T, THEXPO = P("Q_M_SPIN_MIN", 0.15), P("Q_M_SPIN_MAX", 0.9), P("Q_M_THST_EXPO", 0.55), P("Q_THROTTLE_EXPO", 0.2)
RC3 = (P("RC3_MIN", 988), P("RC3_MAX", 2012), P("RC3_DZ", 30))

# ---------------------------------------------------------------- plant config
W_N = MASS * 9.81
vrest = float(kv.get("vrest", 14.92))
wind = float(kv.get("wind", 0.0)); wfrom = float(kv.get("from", 0.0))
cfg = dict(out=os.path.join(run, "case"), fwd=1, mass=MASS, cant_deg=float(kv.get("cant", 17.0)), arm=1.2, wind=wind, wind_from_deg=wfrom, gust=float(kv.get("gust", 0)) if case != "trans" else 0.0,
           gust_at=float(kv.get("gust_at", 20)), turb=float(kv.get("turb", 0)), seed=int(kv.get("seed", 1)), inst=INST, vrest=vrest, slip=float(kv.get("slip", 0)),
           es5=float(kv.get("es5", 1)), es6=float(kv.get("es6", -1)), cmd_file=os.path.join(run, "cmd.json"), max_t=float(kv.get("tmax", 900)),
           wind_alt=float(kv.get("wind_alt", 40.0)))
if case == "takeoff": cfg["wind_t0"] = 5.0
if case == "land": cfg["wind_alt"] = 14.0
if "elv_scale" in kv: cfg["elv_scale"] = float(kv["elv_scale"])
if "cg" in kv: cfg["cg_aft"] = float(kv["cg"]) * 1e-3     # CG aft of the LE, mm (pack trim ends), re-references the aero arms (a_aero.set_cg)

# ---- static thrust model for the entry throttle (same functions the plant uses)
CANT = math.radians(float(kv.get("cant", 17.0)))   # D-195: was 16 (D-189 moved the cant to 17)
HOT = 0.97 if vrest < 15.5 else 1.0
def static(u):
    vb = vrest
    for _ in range(20):
        rpm, T, Q, I = AE.motor(u * vb, 0.0); ib = u * vb * I / 0.98 / vb
        vb = vrest - 0.030 * (4 * ib + 0.5)
    return 4 * T * AE.DER * AE.DOWNLOAD * HOT * math.cos(CANT), vb, 4 * ib + 0.5
def u_for_ratio(r):
    lo, hi = 0.05, 1.0
    for _ in range(40):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if static(m)[0] < r * W_N else (lo, m)
    return 0.5 * (lo + hi)
def throttle_curve(thr_mid, alpha, x):
    def expo(a, t): return (1 - a) * t + a * t ** 3
    a2 = min(max(alpha + 1.25 * (1 - alpha) * (0.5 - thr_mid) / 0.5, 0), 1)
    if x < 0.5: return thr_mid * (1 + expo(alpha, -1 + 2 * x))
    x = x
    return thr_mid + (1 - thr_mid) * expo(a2, 2 * x - 1)
def stick_for(u_out, thr_mid):
    """plant duty u -> mixer actuator -> thrust-space throttle -> stick PWM (QSTABILIZE, Q_M_THST_EXPO / Q_THROTTLE_EXPO of A.param)."""
    a = min(max((u_out - SPIN_MIN) / (SPIN_MAX - SPIN_MIN), 0), 1)
    t = EXPO_T * a * a + (1 - EXPO_T) * a
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if throttle_curve(thr_mid, THEXPO, m) < t else (lo, m)
    x = 0.5 * (lo + hi); lo_pwm = RC3[0] + RC3[2]
    return int(round(lo_pwm + x * (RC3[1] - lo_pwm)))
def window(m):
    """entry window of MASS-GATE / D184: low edge 1.33 W, high edge 0.80 x T/W at the 0.90 cap (sag state)."""
    tw_cap = static(0.90)[0] / W_N
    return 1.33, 0.80 * tw_cap

# ---------------------------------------------------------------- start plant + SITL
plant = subprocess.Popen([sys.executable, os.path.join(HERE, "a_plant.py"), json.dumps(cfg)], stdout=open(os.path.join(run, "plant.log"), "w"), stderr=subprocess.STDOUT)
time.sleep(1.5)
env = dict(os.environ); env["PATH"] = SITL + os.pathsep + env["PATH"]
args = [os.path.join(SITL, "ArduPlane.elf"), "--model", "JSON:127.0.0.1", "--defaults", os.path.join(SCR, "src", "quadplane.parm") + "," + dfile,
        "--home", "37.9150,-122.3340,5,0", "--speedup", kv.get("speedup", "6"), "--wipe", "-I%d" % INST]
sitl = subprocess.Popen(args, cwd=run, env=env, stdout=open(os.path.join(run, "sitl.log"), "ab"), stderr=subprocess.STDOUT)
time.sleep(2)
m = mavutil.mavlink_connection("tcp:127.0.0.1:%d" % (5760 + 10 * INST), source_system=255)
m.wait_heartbeat(timeout=60)
for i in range(13): m.mav.request_data_stream_send(m.target_system, m.target_component, i, 10, 1)
rc = [1500, 1500, 1000, 1500, 1000, 1556, 1500, 1500, 1000]
st = dict(alt=0.0, armed=False, mode=None, t=0.0, asp=0.0, gs=0.0, pitch=0.0, thr=0.0)
events = []; last = [0.0]; send_rc = [True]
MODES = {17: "QSTAB", 5: "FBWA", 7: "CRUISE", 18: "QHOVER", 11: "RTL", 19: "QLOITER", 20: "QLAND", 21: "QRTL", 6: "RTL?", 0: "MANUAL", 2: "STAB"}
mode_log = []
def pump(block=0.02):
    if send_rc[0] and time.time() - last[0] > 0.04:
        m.mav.rc_channels_override_send(m.target_system, m.target_component, *rc[:8], rc[8], *([0] * 9)); last[0] = time.time()
    msg = m.recv_match(blocking=True, timeout=block)
    if msg is None: return
    t = msg.get_type()
    if t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system:
        if msg.custom_mode != st["mode"]: mode_log.append((round(st["t"], 2), MODES.get(msg.custom_mode, msg.custom_mode)))
        st["mode"] = msg.custom_mode; st["armed"] = bool(msg.base_mode & 128)
    elif t == "GLOBAL_POSITION_INT": st["alt"] = msg.relative_alt / 1000.0
    elif t == "ATTITUDE": st["t"] = msg.time_boot_ms / 1000.0; st["pitch"] = math.degrees(msg.pitch)
    elif t == "VFR_HUD": st["asp"] = msg.airspeed; st["gs"] = msg.groundspeed; st["thr"] = msg.throttle
    elif t == "STATUSTEXT": events.append([round(st["t"], 2), msg.text])
def run_for(sec, cond=None, wall=1500):
    t0 = st["t"]; w0 = time.time()
    while st["t"] - t0 < sec and time.time() - w0 < wall and plant.poll() is None:
        pump()
        if cond and cond(): return True
    return False
def seen(sub, since=0.0): return any(sub in e[1] and e[0] >= since for e in events)
def getp(name):
    for _ in range(3):
        m.mav.param_request_read_send(m.target_system, m.target_component, name.encode(), -1)
        t0 = time.time()
        while time.time() - t0 < 2:
            msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
            if msg and msg.param_id == name: return msg.param_value
    return None
def setp(name, v):
    m.mav.param_set_send(m.target_system, m.target_component, name.encode(), float(v), 9); time.sleep(0.2)
def cmd(**kw):
    c = {}
    try: c = json.load(open(os.path.join(run, "cmd.json")))
    except Exception: pass
    c.update(kw); json.dump(c, open(os.path.join(run, "cmd.json"), "w")); os.utime(os.path.join(run, "cmd.json"), None)

QSTAB, FBWA, CRZ, QHOV, RTLm, QLOI = 1100, 1300, 1425, 1556, 1685, 1817
res = dict(tag=tag, args=sys.argv[2:], case=case, mass=MASS, cfg=cfg, marks={})
mk = res["marks"]
def hover_setup(alt_goal, hold=40.0):
    run_for(30)
    m.mav.command_long_send(m.target_system, m.target_component, 400, 0, 1, 21196, 0, 0, 0, 0, 0)
    run_for(5, lambda: st["armed"])
    rc[5] = QHOV; run_for(3)
    mk["t_armed"] = st["t"]; res["armed"] = st["armed"]
    rc[2] = 1850
    ok = run_for(150, lambda: st["alt"] >= alt_goal - 1.0); res["reached_alt"] = ok
    rc[2] = 1500; rc[5] = QLOI; mk["t_climb_done"] = st["t"]        # position hold in QLOITER (a pilot would hold position)
    run_for(hold)
    res["thst_hover"] = getp("Q_M_THST_HOVER")
try:
    if case in ("trans", "battC", "rcC", "moC", "roll"):
        ALT0 = float(kv.get("alt0", 50.0))
        hover_setup(ALT0, hold=float(kv.get("hold", 45)))
        thm = res["thst_hover"] or 0.42
        lo, hi = window(MASS); r = float(kv["r"]) if "r" in kv else 0.5 * (lo + hi)
        if "k09" in kv: thr_in = float(kv["k09"]) * thm; u_out = None
        u_out = u_for_ratio(r); stick = stick_for(u_out, thm)
        res["entry"] = dict(r_target=r, window=[lo, hi], u_out=u_out, stick=stick, th_hover=thm, static_T_over_W=static(u_out)[0] / W_N, u_cap_ratio=static(0.9)[0] / W_N)
        # make sure the wind has arrived and settled
        run_for(max(0.0, 5.0))
        pre = float(kv.get("preclimb", 1.0))
        rc[2] = stick; rc[5] = QSTAB; mk["t_qstab"] = st["t"]; mk["alt_qstab"] = st["alt"]
        run_for(pre)
        rc[5] = FBWA; mk["t_fbwa"] = st["t"]; mk["alt_fbwa"] = st["alt"]
        if float(kv.get("gust", 0)) and case == "trans": cmd(gust=float(kv["gust"]))      # 1-cos gust, 2 s, peak 2 s after the mode change
        t_fw = st["t"]
        ok = run_for(30, lambda: seen("Transition FW done", t_fw)); mk["t_fwdone"] = st["t"] if ok else None
        run_for(float(kv.get("fw_hold", 3.0)))               # override held 3 s after the handover (T-101: key fw_hold, default unchanged)
        rc[5] = CRZ; rc[2] = 1500; mk["t_cruise_mode"] = st["t"]
        if "cthr" in kv: setp("THR_MIN", kv["cthr"]); setp("THR_MAX", kv["cthr"])      # F4 follow-up: pin the cruise throttle (percent) to read the duty it maps to
        run_for(float(kv.get("cruise_s", 25)))
        mk["t_cruise_end"] = st["t"]
        if case == "trans" and kv.get("chain", "0") == "1":
            mk["t_back"] = st["t"]; rc[5] = QLOI; rc[2] = 1500
            run_for(20, lambda: seen("Transition", mk["t_back"]) and False)
            if "wv_after" in kv: setp("Q_WVANE_GAIN", 1); setp("Q_WVANE_SPD_MAX", 2); setp("Q_WVANE_ENABLE", kv["wv_after"]); mk["t_wv"] = st["t"]     # F4 follow-up: weathervane (3 = side into wind) switched on after the back-transition
            yc = float(kv.get("yawcmd", 0))
            if yc: rc[3] = 1950 if yc > 0 else 1050; mk["t_yaw0"] = st["t"]; run_for(abs(yc)); rc[3] = 1500
            run_for(8)
            mk["t_desc0"] = st["t"]
            m.mav.command_long_send(m.target_system, m.target_component, 176, 0, 1, 20, 0, 0, 0, 0, 0)   # QLAND (descent 1.2 m/s, final 0.3 m/s below 6 m)
            mk["t_qland"] = st["t"]
            run_for(220, lambda: seen("Land complete") or (st["alt"] < 0.4 and not st["armed"]))
            run_for(6)
        if case == "roll":                                    # QP-4: FBWA roll steps in cruise (right, left), peak roll rate from the plant csv (p)
            rc[2] = int(kv.get("rollthr", 1500))                 # D-195: FBWA throttle stick, to hold 17 m/s through the steps (default 1500 decelerates to 14.5 m/s)
            rc[5] = FBWA; run_for(2); mk["t_roll0"] = st["t"]
            rc[0] = 1900; run_for(3); mk["t_roll1"] = st["t"]; rc[0] = 1100; run_for(4); mk["t_roll2"] = st["t"]; rc[0] = 1500; run_for(4)
            mk["t_roll3"] = st["t"]
        if case == "battC":
            mk["t_fail"] = st["t"]; setp("BATT_LOW_MAH", 5975); run_for(150, lambda: seen("Land complete"))
        if case == "rcC":
            mk["t_fail"] = st["t"]; send_rc[0] = False; setp("SIM_RC_FAIL", 1); run_for(180, lambda: seen("Land complete"))
        if case == "moC":
            mk["t_fail"] = st["t"]; cmd(motor_out=0); run_for(10)
            if kv.get("land", "0") == "1": rc[5] = QLOI; mk["t_back_fail"] = st["t"]; run_for(40)
            else: run_for(15)
    elif case in ("battH", "rcH", "moH"):
        hover_setup(float(kv.get("alt0", 50.0)), hold=float(kv.get("hold", 35)))
        mk["t_fail"] = st["t"]; mk["alt_fail"] = st["alt"]
        if case == "battH": setp("BATT_LOW_MAH", 5975); run_for(120, lambda: seen("Land complete"))
        if case == "rcH": send_rc[0] = False; setp("SIM_RC_FAIL", 1); run_for(120, lambda: seen("Land complete"))
        if case == "moH": cmd(motor_out=0); run_for(25)
    elif case == "wvane":                                      # QP-4: hover in wind + turbulence with Q_WVANE (A.param), heading from the plant csv
        hover_setup(float(kv.get("alt0", 50.0)), hold=float(kv.get("hold", 10)))
        mk["t_wv0"] = st["t"]; run_for(float(kv.get("wv_s", 100))); mk["t_wv1"] = st["t"]
    elif case == "land":
        hover_setup(20.0, hold=float(kv.get("hold", 25)))
        mk["t_qland"] = st["t"]
        yc = float(kv.get("yawcmd", 0))
        run_for(8)
        m.mav.command_long_send(m.target_system, m.target_component, 176, 0, 1, 20, 0, 0, 0, 0, 0)   # QLAND
        run_for(90, lambda: seen("Land complete") or (st["alt"] < 0.4 and not st["armed"])); run_for(6)
    elif case == "takeoff":
        run_for(30)
        m.mav.command_long_send(m.target_system, m.target_component, 400, 0, 1, 21196, 0, 0, 0, 0, 0)
        run_for(5, lambda: st["armed"]); rc[5] = QLOI; run_for(3); res["armed"] = st["armed"]
        mk["t_throttle"] = st["t"]; rc[2] = 1850
        res["reached_alt"] = run_for(60, lambda: st["alt"] >= 12.0); mk["t_12m"] = st["t"]
        rc[2] = 1500; run_for(10)
finally:
    res["events"] = events; res["modes"] = mode_log
    send_rc[0] = False
    try: m.close()
    except Exception: pass
    sitl.terminate()
    try: sitl.wait(10)
    except Exception: sitl.kill()
    try: plant.wait(timeout=30)
    except Exception: plant.kill()
    json.dump(res, open(os.path.join(run, "result.json"), "w"), indent=1, default=str)
    print(json.dumps(dict(tag=tag, mk=mk, entry=res.get("entry"), modes=mode_log[-12:]), default=str))
