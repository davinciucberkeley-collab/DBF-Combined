"""F5 SITL check of the timed transition switch (stage A: logic only, ArduPilot's stock quadplane-copter_tailsitter).

The EdgeTX logic of TRANSITION-SWITCH.md (transition_switch.Pocket) runs here at 10 ms steps of SIM time and its CH3,
CH5, CH6 and CH9 outputs are sent to SITL as RC_CHANNELS_OVERRIDE, so the firmware sees the same pulses the RP3 V2
would deliver (CH3 1500 + 5.12 x %). Nothing here is a K09-L number except the logic and the timing.

Use (environment variable SCR = folder holding sitl/ArduPlane.elf, src/quadplane*.parm and a run folder whose
eeprom.bin already holds K09L.param with the stage-A SIM overrides of team/F4/sitl/RESULTS.md):
    $SCR/venv/Scripts/python -I redesign/team/F5/transition_sitl.py <rundir>
Writes <rundir>/f5_transition.json and prints the PASS / FAIL lines. Instance -I7 (TCP 5830), so it does not collide
with another SITL on 5760.

Cases, one flight: arm in QHOVER, climb to 50 m, hover 60 s (hover learning), read Q_M_THST_HOVER, pick the stick step
and override % (transition_switch.setting_table), QSTABILIZE with the stick at mid, then
  A  flip SC down (nominal), stick held at mid; pitch-over; then CRUISE (SB mid), back-transition SC up -> QHOVER
  B  same, stick moved to 30 % 0.5 s after the FBWA command and to 100 % 1.5 s later (firmware must ignore it to 70 deg)
  C  flip SC down then up after 1.0 s (abort in the pre-climb): no FBWA
  D  SB mid (QHOVER) and flip SC down: nothing happens (the start needs QSTABILIZE)
"""
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import transition_switch as ts  # noqa: E402
from pymavlink import mavutil, DFReader  # noqa: E402

SCR = os.environ["SCR"]
RUN = Path(sys.argv[1])
INST = 7
RC = (988, 2012, 30)
R_DESIGN = 1.285
FLTMODE = {"FLTMODE1": 17, "FLTMODE2": 5, "FLTMODE3": 7, "FLTMODE4": 18, "FLTMODE5": 11, "FLTMODE6": 19}
MODE_NUM = {17: "QSTABILIZE", 5: "FBWA", 7: "CRUISE", 18: "QHOVER", 11: "RTL", 19: "QLOITER", 20: "QLAND", 21: "QRTL"}


def start():
    env = dict(os.environ)
    env["PATH"] = os.path.join(SCR, "sitl") + os.pathsep + env["PATH"]
    args = [os.path.join(SCR, "sitl", "ArduPlane.elf"), "--model", "quadplane-copter_tailsitter", "--defaults",
            os.path.join(SCR, "src", "quadplane.parm") + "," + os.path.join(SCR, "src", "quadplane-copter_tailsitter.parm"),
            "--home", "37.9150,-122.3340,5,0", "--speedup", "1", "-I%d" % INST]
    log = open(RUN / "sitl.log", "ab")
    p = subprocess.Popen(args, cwd=str(RUN), env=env, stdout=log, stderr=log)
    time.sleep(3)
    m = mavutil.mavlink_connection("tcp:127.0.0.1:%d" % (5760 + 10 * INST), source_system=255)
    m.wait_heartbeat(timeout=60)
    return p, m


st = {"t": 0.0, "mode": None, "armed": False, "alt": 0.0, "pitch": 0.0, "as": 0.0, "text": []}
rc = [1500, 1500, 988, 1500, 988, 1167, 1500, 1500, 988]
last_send = [0.0]


def pump(m, block=0.01):
    if time.time() - last_send[0] > 0.02:
        m.mav.rc_channels_override_send(m.target_system, m.target_component, *[int(round(v)) for v in rc[:8]],
                                        int(round(rc[8])), *([0] * 9))
        last_send[0] = time.time()
    msg = m.recv_match(blocking=True, timeout=block)
    if msg is None:
        return
    t = msg.get_type()
    if t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system:
        st["mode"] = MODE_NUM.get(msg.custom_mode, msg.custom_mode)
        st["armed"] = bool(msg.base_mode & 128)
    elif t == "ATTITUDE":
        st["t"] = msg.time_boot_ms / 1000.0
        st["pitch"] = math.degrees(msg.pitch)
    elif t == "GLOBAL_POSITION_INT":
        st["alt"] = msg.relative_alt / 1000.0
    elif t == "VFR_HUD":
        st["as"] = msg.airspeed
    elif t == "STATUSTEXT":
        st["text"].append((round(st["t"], 2), msg.text))


def run(m, dur, cond=None):
    t0, w0 = st["t"], time.time()
    while st["t"] - t0 < dur and time.time() - w0 < dur * 4 + 30:
        pump(m)
        if cond and cond():
            return True
    return False


def setp(m, name, val):
    for _ in range(5):
        m.mav.param_set_send(m.target_system, m.target_component, name.encode(), float(val),
                             mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        t0 = time.time()
        while time.time() - t0 < 2:
            msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.5)
            if msg and msg.param_id == name:
                return msg.param_value
    return None


def getp(m, name):
    for _ in range(5):
        m.mav.param_request_read_send(m.target_system, m.target_component, name.encode(), -1)
        t0 = time.time()
        while time.time() - t0 < 2:
            msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.5)
            if msg and msg.param_id == name:
                return msg.param_value
    return None


def pct2pwm(p):
    return 1500.0 + 5.12 * p


def drive(m, tx, inputs, dur, events=(), marks=None):
    """Step the EdgeTX model at 10 ms of sim time; events: [(t_rel, {input: value})]."""
    t0 = st["t"]
    ev = sorted(events)
    sim_ms = 0
    w0 = time.time()
    while sim_ms <= dur * 1000 and time.time() - w0 < dur * 4 + 30:
        pump(m, 0.005)
        while sim_ms <= (st["t"] - t0) * 1000:
            while ev and ev[0][0] * 1000 <= sim_ms:
                inputs.update(ev.pop(0)[1])
            ch3, ch5, ch6, ch9 = tx.step(**inputs)
            rc[2], rc[4], rc[5], rc[8] = pct2pwm(ch3), pct2pwm(ch5), pct2pwm(ch6), pct2pwm(ch9)
            if marks is not None:
                marks.append((round(t0 + sim_ms / 1000.0, 2), ch3, ch6, dict(tx.L)))
            sim_ms += 10


def main():
    p, m = start()
    res = {"cases": {}, "text": []}
    try:
        for i in range(0, 13):
            m.mav.request_data_stream_send(m.target_system, m.target_component, i, 25, 1)
        for k, v in dict(SIM_BATT_VOLTAGE=16.8, SIM_RC_FAIL=1, RC3_MIN=RC[0], RC3_MAX=RC[1], RC3_DZ=RC[2],
                         RC3_TRIM=RC[0], Q_THROTTLE_EXPO=0.2, FENCE_ALT_MAX=900, FENCE_RADIUS=5000, Q_M_HOVER_LEARN=2, Q_A_ANGLE_BOOST=0, LOG_DISARMED=0,
                         **FLTMODE).items():
            res.setdefault("params_set", {})[k] = setp(m, k, v)
        run(m, 40)
        m.mav.command_long_send(m.target_system, m.target_component, 241, 0, 0, 0, 1, 0, 0, 0, 0)
        run(m, 10)
        # model, inputs as the Pocket
        inp = dict(sa=0, sb=0, sc=-1, sd=0, thr=-100)       # SB mid = QHOVER for the take-off
        tx = ts.Pocket(override_pct=37)
        drive(m, tx, inp, 3)
        res["mode_at_power_up"] = st["mode"]
        inp["sa"] = 1
        drive(m, tx, inp, 6)
        res["armed"] = st["armed"]
        if not st["armed"]:
            m.mav.command_long_send(m.target_system, m.target_component, 400, 0, 1, 0, 0, 0, 0, 0, 0)
            run(m, 5)
        inp["thr"] = 70
        t0 = st["t"]
        while st["alt"] < 50 and st["t"] - t0 < 120:
            drive(m, tx, inp, 1)
        inp["thr"] = 0
        drive(m, tx, inp, 60)                                # hover learning (time constant 10 s)
        th = getp(m, "Q_M_THST_HOVER")
        w = json.loads((HERE.parents[0] / "B3" / "results" / "closure1114.json").read_text(encoding="utf-8"))
        r_lo, r_hi = ts.r_window(R_DESIGN, w["design"]["T0_low_edge"], w["design"]["T0_high_edge"],
                                 w["window"]["rate12_w04"]["T0_lo"], w["window"]["rate12_w04"]["T0_hi"])
        row = ts.setting_table(R_DESIGN, r_lo, r_hi, RC, th_lo=round(th, 4), th_hi=round(th, 4), step=0.005)[0]
        if row["q_throttle_expo"] != 0.2:
            setp(m, "Q_THROTTLE_EXPO", row["q_throttle_expo"])
        res["theta_h_sitl"] = th
        res["setting"] = row
        target = row["throttle_in"]

        def one(name, events, dur, sb0=-1):
            nonlocal tx
            tx = ts.Pocket(override_pct=row["edgetx_override_pct"])
            inp.update(sa=1, sb=sb0, sc=-1, sd=0, thr=0)
            drive(m, tx, inp, 6)                              # settle in the starting Q mode, stick at mid
            marks = []
            t_flip = st["t"] + 1.0
            drive(m, tx, inp, dur, events=[(1.0, {"sc": 1})] + list(events), marks=marks)
            res["cases"][name] = {"t_flip_sim": t_flip, "mode_end": st["mode"],
                                  "tx_changes": [(a, b, c) for (a, b, c, _), prev in zip(marks[1:], marks)
                                                 if (b, c) != (prev[1], prev[2])]}

        one("A_nominal", [(5.0, {"sb": 0}), (25.0, {"sc": -1})], 45.0)
        inp.update(sb=0)
        drive(m, tx, inp, 15)
        one("B_stick_moves", [(1.0 + 0.9 + 0.5, {"thr": -40}), (1.0 + 0.9 + 2.0, {"thr": 100}),
                              (1.0 + 0.9 + 3.5, {"thr": 0}), (25.0, {"sc": -1})], 45.0)
        drive(m, tx, inp, 15)
        one("C_abort", [(2.0, {"sc": -1})], 8.0)
        one("D_from_qhover", [(3.0, {"sc": -1})], 8.0, sb0=0)
        inp.update(sa=1, sb=0, sc=-1, thr=-100)
        m.mav.command_long_send(m.target_system, m.target_component, 176, 0, 1, 20, 0, 0, 0, 0, 0)   # QLAND
        run(m, 120, lambda: not st["armed"])
        inp["sa"] = 0
        drive(m, tx, inp, 3)
        res["text"] = st["text"][-60:]
        res["target_throttle_in"] = target
    finally:
        json.dump(res, open(RUN / "f5_transition.json", "w"), indent=1)
        try:
            m.close()
        except Exception:
            pass
        p.terminate()
        try:
            p.wait(10)
        except Exception:
            p.kill()
    analyse_log(res)


def analyse_log(res):
    logs = sorted((RUN / "logs").glob("*.BIN"), key=lambda f: f.stat().st_mtime)
    log = DFReader.DFReader_binary(str(logs[-1]))
    rcin, modes, qtun, att, msgs = [], [], [], [], []
    while True:
        msg = log.recv_match(type=["RCIN", "MODE", "QTUN", "ATT", "MSG"])
        if msg is None:
            break
        t = msg.TimeUS * 1e-6
        ty = msg.get_type()
        if ty == "RCIN":
            rcin.append((t, msg.C3, msg.C6))
        elif ty == "MODE":
            modes.append((t, MODE_NUM.get(msg.ModeNum, msg.ModeNum)))
        elif ty == "QTUN":
            qtun.append((t, msg.ThI, msg.ThO, msg.ThH, getattr(msg, "Trn", None)))
        elif ty == "ATT":
            att.append((t, msg.Pitch))
        elif ty == "MSG":
            msgs.append((round(t, 2), msg.Message))
    target = res["target_throttle_in"]
    ov_pwm = pct2pwm(res["setting"]["edgetx_override_pct"])
    out = {"modes": modes, "lines": [], "msgs": [x for x in msgs if any(k in x[1] for k in ("ransition", "ence", "denied", "ailsafe"))]}
    # each override episode in RCIN.C3
    eps, on = [], None
    for t, c3, c6 in rcin:
        if abs(c3 - ov_pwm) <= 3 and on is None:
            on = t
        elif abs(c3 - ov_pwm) > 3 and on is not None:
            eps.append((on, t))
            on = None
    out["override_episodes"] = eps
    for (a, b) in eps:
        m_in = [x for x in modes if a - 0.05 <= x[0] <= b + 0.05]
        mode_before = [x for x in modes if x[0] < a]
        mb = mode_before[-1][1] if mode_before else None
        fb = next((x[0] for x in m_in if x[1] == "FBWA"), None)
        q = [x for x in qtun if a + 0.1 <= x[0] <= (fb or b) - 0.02]
        e = {"start": a, "end": b, "mode_before": mb, "fbwa_at": fb,
             "hold_qstab_s": (fb - a) if fb else None, "release_after_fbwa_s": (b - fb) if fb else None,
             "ThI_preclimb_min": min(x[1] for x in q) if q else None, "ThI_preclimb_max": max(x[1] for x in q) if q else None,
             "ThH": q[-1][3] if q else None}
        if fb:
            pa = [(t, pch) for t, pch in att if fb - 0.5 <= t <= fb + 12]
            e["att_pitch_at_fbwa"] = pa[0][1] if pa else None
            e["att_pitch_range"] = [min(x[1] for x in pa), max(x[1] for x in pa)] if pa else None
            done = next((t for t, txt in msgs if t > fb and "Transition FW done" in txt), None)
            e["t_fw_done_after_fbwa_s"] = (done - fb) if done else None
            qh = [x for x in qtun if fb + 0.05 <= x[0] <= (done or fb + 3.0) - 0.05]
            e["ThI_hold_min"] = min(x[1] for x in qh) if qh else None
            e["ThI_hold_max"] = max(x[1] for x in qh) if qh else None
            e["qtun_samples_hold"] = len(qh)
        out["lines"].append(e)
    res["log"] = out
    json.dump(res, open(RUN / "f5_transition.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("text",)}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "log":
        analyse_log(json.load(open(RUN / "f5_transition.json")))
    else:
        main()
