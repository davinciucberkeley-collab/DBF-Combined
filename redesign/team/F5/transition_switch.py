"""F5: timed transition switch on the RadioMaster Pocket (EdgeTX) for K09-L (B3 closure round 2026-11-14, CL-4).

Run:  python -I redesign/team/F5/transition_switch.py         -> prints the tables, writes results/transition.json
      (rc_link.py imports the functions below for the CL-F5-TRANS-* claims)

What the switch does (TRANSITION-SWITCH.md): SC flipped down from QSTABILIZE, armed, stick above 40 %
  -> CH3 overridden to the value that makes ArduPilot's QSTABILIZE throttle_in = 1.285 x learnt hover throttle
  -> after the logical-switch delay the flight-mode channel CH6 goes to the FBWA slot (forward transition)
  -> the override is released 1.2 s after the FBWA command, the throttle returns to the stick.
FBWA (and CRUISE, RTL) exist only after that sequence; no plain switch position selects a fixed-wing mode.

Firmware facts used (ArduPilot tag Plane-4.7.2, read 2026-11-14, links in rc_link.py sources):
  quadplane.cpp  get_pilot_throttle(): throttle_in = channel_throttle->get_control_in() / get_range(), then
                 throttle_curve(get_throttle_hover(), Q_THROTTLE_EXPO, throttle_in) when Q_THROTTLE_EXPO > 0
  RC_Channel.h   control_in is int16_t; radio.cpp set_range(100) -> the stick reaches QSTABILIZE in 1 % steps
  RC_Channel.cpp pwm_to_range_dz: (pwm - (RC3_MIN + RC3_DZ)) * 100 / (RC3_MAX - (RC3_MIN + RC3_DZ)), truncated to int16
  radio.cpp      channel_throttle->set_default_dead_zone(30)
  AP_Math.cpp    throttle_curve(), expo_curve() (copied below)
  RC_Channel.cpp read_6pos_switch thresholds 1231/1361/1491/1621/1750 us; SWITCH_DEBOUNCE_TIME_MS 200
  Plane.cpp      read_mode_switch scheduled at 7 Hz; read_radio at 50 Hz
EdgeTX facts used (EdgeTX tag v2.11.3, read 2026-11-14): logical-switch delay/duration and sticky/edge state are
  stepped by logicalSwitchesTimerTick() every 0.1 s (mixer.cpp, switches.cpp); a delay restarts if the condition drops
  (switches.cpp DurationAndDelayProcessing); Override CHx bypasses the output limits and sets calc100toRESX(value),
  value an integer -100..100 (mixer.cpp applyLimits, functions.cpp).
"""
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- ArduPilot functions (verbatim logic, AP_Math.cpp)


def expo_curve(alpha, x):
    return (1.0 - alpha) * x + alpha * x * x * x


def throttle_curve(thr_mid, alpha, thr_in):
    alpha2 = min(max(alpha + 1.25 * (1.0 - alpha) * (0.5 - thr_mid) / 0.5, 0.0), 1.0)
    if thr_in < 0.5:
        t = -1.0 + thr_in / 0.5                      # linear_interpolate(-1, 0, thr_in, 0, 0.5)
        return thr_mid * (1.0 + expo_curve(alpha, t))  # linear_interpolate(0, thr_mid, e, -1, 0)
    t = (thr_in - 0.5) / 0.5
    return thr_mid + (1.0 - thr_mid) * expo_curve(alpha2, t)


def control_in(pwm, rc_min, rc_max, dz):
    """RC_Channel::pwm_to_range_dz for range 100, then the int16_t truncation of control_in."""
    r = min(max(pwm, rc_min), rc_max)
    lo = rc_min + dz
    return int(100.0 * (r - lo) / (rc_max - lo)) if r > lo else 0


def pilot_throttle(theta_h, alpha, k):
    """QuadPlane::get_pilot_throttle for control_in = k (0..100)."""
    s = k / 100.0
    return throttle_curve(theta_h, alpha, s) if alpha > 0 else s


# ---------------------------------------------------------------- 1. entry throttle realisation


def r_window(r_design, t0_low_design, t0_high_design, t0_lo_window, t0_hi_window):
    """Ratio window that keeps B3's band edges inside B3's physical window (scales linearly with r)."""
    return r_design * t0_lo_window / t0_low_design, r_design * t0_hi_window / t0_high_design


def theta_band(k, alpha, r_lo, r_hi, lo=0.30, hi=0.75):
    """Learnt-hover-throttle band over which a fixed stick k realises r inside [r_lo, r_hi]."""
    pts = [lo + i * 0.0001 for i in range(int((hi - lo) / 0.0001) + 1)]
    ok = [th for th in pts if r_lo <= pilot_throttle(th, alpha, k) / th <= r_hi]
    return (min(ok), max(ok)) if ok else (None, None)


def solve_alpha(theta_h, k, r):
    f = lambda a: pilot_throttle(theta_h, a, k) / theta_h - r
    a, b = 0.0001, 1.0
    if f(a) * f(b) > 0:
        return None
    for _ in range(60):
        m = 0.5 * (a + b)
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


def edgetx_pct(pwm):
    """EdgeTX channel % for a CRSF pulse: +-100 % = 1500 +- 512 us (CRSF 172..1811, ArduPilot CRSF decoder)."""
    return (pwm - 1500.0) / 5.12


def best_override(k, rc_min, rc_max, dz):
    """Integer EdgeTX override % whose pulse lands deepest inside ArduPilot's control_in bin k."""
    lo = rc_min + dz
    span = rc_max - lo
    b0, b1 = lo + k * span / 100.0, lo + (k + 1) * span / 100.0
    best = None
    for pct in range(-100, 101):
        pwm = 1500.0 + 5.12 * pct
        if b0 <= pwm < b1:
            m = min(pwm - b0, b1 - pwm)
            if best is None or m > best[2]:
                best = (pct, pwm, m)
    return {"bin_us": [b0, b1], "pct": best[0], "pwm_us": best[1], "margin_us": best[2]} if best else None


def setting_table(r, r_lo, r_hi, rc, alpha0=0.2, th_lo=0.40, th_hi=0.60, step=0.005, tol=0.0025):
    """Per learnt theta_h: stick k, EdgeTX override %, Q_THROTTLE_EXPO. Keeps the default 0.2 when the nearest stick
    step lands within +-tol of r (leaves room for in-flight drift of theta_h); otherwise solves Q_THROTTLE_EXPO so that
    the nearest step gives r exactly."""
    rows = []
    n = int(round((th_hi - th_lo) / step))
    for i in range(n + 1):
        th = round(th_lo + i * step, 4)
        k = min(range(50, 100), key=lambda kk: abs(pilot_throttle(th, alpha0, kk) / th - r))
        rr = pilot_throttle(th, alpha0, k) / th
        alpha = alpha0
        if not (r_lo <= rr <= r_hi and abs(rr / r - 1) <= tol):
            alpha = None
            for kk in sorted(range(50, 100), key=lambda kk: abs(kk - k)):
                a = solve_alpha(th, kk, r)
                if a is not None:
                    k, alpha = kk, round(a, 3)
                    break
            rr = pilot_throttle(th, alpha, k) / th
        ov = best_override(k, *rc)
        rows.append({"theta_h": th, "k_pct_ap": k, "q_throttle_expo": alpha, "throttle_in": pilot_throttle(th, alpha, k),
                     "r": rr, "r_err_pct": 100 * (rr / r - 1), "edgetx_override_pct": ov["pct"],
                     "pwm_us": ov["pwm_us"], "bin_margin_us": ov["margin_us"]})
    return rows


# ---------------------------------------------------------------- 2. timing (TX logic -> ELRS -> ArduPilot)


def timing(d_fbwa, d_release, t_sw6, t_pkt=1 / 150.0, tick=0.1, f_mode=7.0, debounce=0.2):
    """Bounds of the interval the FC spends in QSTABILIZE with the override, and of the release margin after FBWA.
    d_*: EdgeTX logical-switch delays (s); the 0.1 s tick makes each delay effective in [d - 0.1, d].
    t_sw6: worst ELRS latency of CH6 (Wide round robin, CL-F5-SWITCH-LATENCY); CH3 is in every packet."""
    per = 1.0 / f_mode
    n = math.ceil(debounce / per)                 # reads after the first one that sees the new position
    deb_lo, deb_hi = n * per, (n + 1) * per        # first read 0..per after arrival, accepted n reads later
    ch3_lo, ch3_hi = t_pkt, 2 * t_pkt
    ch6_lo, ch6_hi = t_pkt, t_sw6
    hold_lo = (d_fbwa - tick) + ch6_lo + deb_lo - ch3_hi
    hold_hi = d_fbwa + ch6_hi + deb_hi - ch3_lo
    rel_lo = (d_release - tick) + ch3_lo - (ch6_hi + deb_hi)
    rel_hi = d_release + ch3_hi - (ch6_lo + deb_lo)
    return {"hold_min_s": hold_lo, "hold_max_s": hold_hi, "release_after_fbwa_min_s": rel_lo,
            "release_after_fbwa_max_s": rel_hi, "mode_latency_s": [ch6_lo + deb_lo, ch6_hi + deb_hi]}


# ---------------------------------------------------------------- 3. EdgeTX logic model and property check

# ArduPilot FLTMODE slots requested from F4 (CR-F5-15): Q modes at -100 %, 0 % and +100 %
SLOT_PCT = {1: -65, 2: -40, 3: -15, 4: 11, 5: 36, 6: 62}
SLOT_MODE = {1: "QSTABILIZE", 2: "FBWA", 3: "CRUISE", 4: "QHOVER", 5: "RTL", 6: "QLOITER"}
MODE_PCT = {SLOT_MODE[s]: SLOT_PCT[s] for s in SLOT_PCT}
FW = {"FBWA", "CRUISE", "RTL"}


def slot_of_pwm(pwm):
    for i, edge in enumerate((1231, 1361, 1491, 1621, 1750)):
        if pwm < edge:
            return i + 1
    return 6


def pct_to_pwm(p):
    return 1500.0 + 5.12 * p


class Pocket:
    """EdgeTX model K09L: the logical switches, special function and CH3/CH6 mixes of TRANSITION-SWITCH.md.
    Mixer every 10 ms; sticky, edge and delay timers on the 0.1 s tick (switches.cpp)."""

    def __init__(self, override_pct, d_fbwa=0.9, d_release=1.2, thr_guard=-20):
        self.ov, self.d6, self.d7, self.g = override_pct, int(round(d_fbwa * 10)), int(round(d_release * 10)), thr_guard
        self.L = {i: False for i in range(1, 16)}
        self.sc_down = False
        self.st05 = {"state": 0, "last": 0}
        self.st13 = {"state": 0, "last": 0}
        self.e03 = {"dur": 0, "out": False}
        self.d = {6: [0, 0], 7: [0, 0]}          # [timerState 0 start/1 delay/2 enable, timer]
        self.sb_last, self.d12 = None, 0
        self.ms = 0

    # inputs: sa 0 up / 1 down (armed); sb, sc -1 up, 0 mid, 1 down; thr stick -100..100
    def _comb(self, sa, sb, sc, thr):
        L = self.L
        self.sc_down = sc == 1
        L[1] = thr > self.g                                   # a>x  Thr > -20 (stick above 40 %)
        L[2] = sc == 1 and sa == 1                            # AND  SC-down, SA-down
        L[3] = self.e03["out"]                                # Edge SC-down rising, T1 0.0, T2 <<
        L[14] = sa == 1 and not self.st13["state"]            # AND  SA-down, !L13
        L[15] = sb == -1 and L[14]                            # AND  SB-up, L14
        L[4] = L[3] and L[1] and L[15]                        # AND  L03, L01; AND-switch L15
        L[5] = bool(self.st05["state"])                       # Stky V1 L04, V2 !L02
        for i, src, dly in ((6, L[5] and sa == 1, self.d6), (7, None, self.d7)):
            if i == 7:
                src = L[6] and sa == 1
            ts = self.d[i]
            if src:
                if ts[0] == 0:
                    ts[0], ts[1] = 1, dly
                if ts[0] == 1 and ts[1] == 0:
                    ts[0] = 2
                L[i] = ts[0] == 2
            else:
                ts[0], ts[1] = 0, 0
                L[i] = False
        L[8] = L[5] and not L[7]                              # AND  L05, !L07  -> SF1 Override CH3
        L[9] = L[6] and sb == 0                               # AND  L06, SB-mid -> CRUISE
        L[10] = L[6] and sb == 1                              # AND  L06, SB-down -> RTL
        if self.sb_last is None:
            self.sb_last = sb
        if abs(sb - self.sb_last) * 100 > 50:                 # |d|>x SB, 50 (true for 0.1 s)
            self.sb_last, self.d12 = sb, 10
        L[12] = self.d12 > 0
        L[11] = L[12] and not L[6]                            # AND  L12, !L06 (SB moved outside FW)
        L[13] = bool(self.st13["state"])                      # Stky V1 L06, V2 L11

    @staticmethod
    def _sticky(s, v1, v2):
        now = v2 if s["state"] else v1
        before = s["last"]
        if now != before:
            s["last"] ^= 1
            if not before:
                s["state"] ^= 1

    def tick(self):                                           # every 0.1 s, LS index order
        self.e03["out"] = False
        if self.sc_down:
            if self.e03["dur"] == 0:
                self.e03["out"] = True
            self.e03["dur"] += 1
        else:
            self.e03["dur"] = 0
        self.L[3] = self.e03["out"]
        self.L[4] = self.L[3] and self.L[1] and self.L[15]
        self._sticky(self.st05, self.L[4], not self.L[2])
        self._sticky(self.st13, self.L[6], self.L[11])
        for i in (6, 7):
            if self.d[i][1] > 0:
                self.d[i][1] -= 1

    def step(self, sa, sb, sc, sd, thr):
        """One 10 ms mixer cycle. Returns (ch3 %, ch5 %, ch6 %, ch9 %)."""
        if self.ms % 100 == 0:
            self._comb(sa, sb, sc, thr)
            self.tick()
        self._comb(sa, sb, sc, thr)
        self.d12 = max(0, self.d12 - 1)
        self.ms += 10
        L = self.L
        ch3 = self.ov if L[8] else thr                        # SF1 Override CH3 when L08
        ch6 = MODE_PCT["QSTABILIZE"]                          # 1 MAX -65 (always)
        if sb == 0:
            ch6 = MODE_PCT["QHOVER"]                          # 2 REPL SB-mid
        if sb == 1:
            ch6 = MODE_PCT["QLOITER"]                         # 3 REPL SB-down
        if L[13]:
            ch6 = MODE_PCT["QHOVER"]                          # 4 REPL L13 (after back-transition)
        if L[5]:
            ch6 = MODE_PCT["QSTABILIZE"]                      # 5 REPL L05 (sequence: QSTABILIZE pre-climb)
        if L[6]:
            ch6 = MODE_PCT["FBWA"]                            # 6 REPL L06
        if L[9]:
            ch6 = MODE_PCT["CRUISE"]                          # 7 REPL L09
        if L[10]:
            ch6 = MODE_PCT["RTL"]                             # 8 REPL L10
        ch5 = 100 if sa == 1 else -100
        ch9 = 100 if sd == 1 else -100
        return ch3, ch5, ch6, ch9


def fuzz(override_pct, n_runs=400, seconds=120, seed=1):
    """Random switch / stick histories (biased toward real flight sequences). Checks, every 10 ms:
    P1 CH6 commands a fixed-wing slot only while L06 holds, and L06 only after a valid start (SC flipped down while
       armed, SB up, not in the forced-QHOVER state, stick > 40 %) followed by >= delay - 0.1 s of override in QSTABILIZE;
    P2 the override is on only inside a started sequence and ends >= release delay - 0.1 s after the FBWA command;
    P3 CH6 is always one of the six slot centres (never 0 %, never an end point)."""
    rng = random.Random(seed)
    viol, seqs, fw_ms = [], 0, 0
    for run in range(n_runs):
        tx = Pocket(override_pct)
        sa, sb, sc, sd, thr = 0, -1, -1, 1, -100
        t_next, t = 0, 0
        l2_rise, l6_t, ov_on_t = None, None, None
        prev_l2, prev_l5, prev_l6 = False, False, False
        while t < seconds * 1000:
            if t >= t_next:
                c = rng.random()
                if c < 0.18:
                    sa = 1 - sa
                elif c < 0.40:
                    sb = rng.choice((-1, 0, 1))
                elif c < 0.65:
                    sc = rng.choice((-1, 0, 1, 1))
                elif c < 0.70:
                    sd = 1 - sd
                else:
                    thr = rng.choice((-100, -60, -21, -19, 0, 20, 60, 100))
                t_next = t + rng.choice((20, 50, 100, 300, 1000, 2500, 4000))
            ch3, ch5, ch6, ch9 = tx.step(sa, sb, sc, sd, thr)
            L = tx.L
            if ch6 not in SLOT_PCT.values():
                viol.append((run, t, "P3 ch6 %d" % ch6))
            if sc == 1 and not prev_l2:
                l2_rise = t
            if L[5] and not prev_l5:
                if not (L[2] and l2_rise is not None and t - l2_rise <= 100 and thr > -20 and sb == -1 and sa == 1):
                    viol.append((run, t, "P1 latch without a valid start"))
            mode = SLOT_MODE[slot_of_pwm(pct_to_pwm(ch6))]
            if mode in FW:
                fw_ms += 10
                if not L[6]:
                    viol.append((run, t, "P1 FW slot without L06"))
            if L[6] and not prev_l6:
                seqs += 1
                l6_t = t
                if ov_on_t is None or t - ov_on_t < (tx.d6 - 1) * 100:
                    viol.append((run, t, "P1 FBWA before %.1f s of override" % ((tx.d6 - 1) / 10)))
            if not L[6]:
                l6_t = None
            if ch3 == override_pct and L[8]:
                if ov_on_t is None:
                    ov_on_t = t
                if not L[5]:
                    viol.append((run, t, "P2 override outside a sequence"))
                if l6_t is not None and t - l6_t > tx.d7 * 100:
                    viol.append((run, t, "P2 override held past the release delay"))
            else:
                if ov_on_t is not None and l6_t is not None and t - l6_t < (tx.d7 - 1) * 100:
                    viol.append((run, t, "P2 override released early"))
                ov_on_t = None
            if L[5] and not L[6] and ch6 != MODE_PCT["QSTABILIZE"]:
                viol.append((run, t, "P1 pre-climb not in QSTABILIZE"))
            prev_l2, prev_l5, prev_l6 = sc == 1, L[5], L[6]
            t += 10
    return {"runs": n_runs, "seconds_each": seconds, "sequences_completed": seqs, "fw_time_s": fw_ms / 1000.0,
            "violations": len(viol), "first_violations": viol[:10]}


def scripted(override_pct):
    """The nominal sequence and the aborts, as a time line of TX outputs (for the SITL driver and the bench)."""
    cases = {}

    def run(events, dur=8.0):
        tx = Pocket(override_pct)
        s = dict(sa=1, sb=-1, sc=-1, sd=1, thr=2)
        out, t, ev = [], 0, sorted(events)
        while t <= dur * 1000:
            while ev and ev[0][0] * 1000 <= t:
                s.update(ev.pop(0)[1])
            ch3, ch5, ch6, ch9 = tx.step(**s)
            out.append((t / 1000.0, ch3, ch6))
            t += 10
        chg = [out[0]] + [o for a, o in zip(out, out[1:]) if (o[1], o[2]) != (a[1], a[2])]
        return [(round(a, 2), b, SLOT_MODE[slot_of_pwm(pct_to_pwm(c))]) for a, b, c in chg]

    cases["nominal"] = run([(1.0, {"sc": 1})])
    cases["abort_in_preclimb"] = run([(1.0, {"sc": 1}), (1.5, {"sc": -1})])
    cases["stick_low_at_flip"] = run([(0.5, {"thr": -60}), (1.0, {"sc": 1}), (2.0, {"thr": 2})])
    cases["from_qhover"] = run([(0.5, {"sb": 0}), (1.0, {"sc": 1})])
    cases["back_transition"] = run([(1.0, {"sc": 1}), (5.0, {"sb": 0}), (6.0, {"sc": -1}), (8.0, {"sb": -1})], dur=9.0)
    cases["disarmed_flip"] = run([(0.5, {"sa": 0}), (1.0, {"sc": 1}), (1.5, {"sa": 1})])
    return cases


# ---------------------------------------------------------------- main
DESIGN = dict(r=1.285, theta_h=0.49, alpha=0.2, k=67, rc=(988, 2012, 30), d_fbwa=0.9, d_release=1.2)


def analyse(r, t0_low, t0_high, t0_lo_w, t0_hi_w, theta_h, alpha, k, rc, d_fbwa, d_release, t_sw6):
    r_lo, r_hi = r_window(r, t0_low, t0_high, t0_lo_w, t0_hi_w)
    thr = pilot_throttle(theta_h, alpha, k)
    band = theta_band(k, alpha, r_lo, r_hi)
    ov = best_override(k, *rc)
    tm = timing(d_fbwa, d_release, t_sw6)
    step = (pilot_throttle(theta_h, alpha, k + 1) - thr) / theta_h
    return {"r_lo": r_lo, "r_hi": r_hi, "throttle_in": thr, "r_real": thr / theta_h, "r_step_per_pct": step,
            "theta_band": band, "theta_tol_minus": theta_h - band[0], "theta_tol_plus": band[1] - theta_h,
            "override": ov, "ap_control_in_check": control_in(round(ov["pwm_us"]), *rc), **tm}


if __name__ == "__main__":
    b3 = json.loads((HERE.parents[0] / "B3" / "results" / "closure1114.json").read_text(encoding="utf-8"))
    w = b3["window"]["rate12_w04"]
    dz = b3["design"]
    res = analyse(DESIGN["r"], dz["T0_low_edge"], dz["T0_high_edge"], w["T0_lo"], w["T0_hi"], DESIGN["theta_h"],
                  DESIGN["alpha"], DESIGN["k"], DESIGN["rc"], DESIGN["d_fbwa"], DESIGN["d_release"], 0.0593)
    table = setting_table(DESIGN["r"], res["r_lo"], res["r_hi"], DESIGN["rc"])
    fz = fuzz(res["override"]["pct"])
    sc = scripted(res["override"]["pct"])
    out = {"design": DESIGN, "analysis": res, "table": table, "fuzz": fz, "scripted": sc}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "transition.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))
    print("theta_h  k  expo   thr_in  r       err%   EdgeTX%  pwm     margin_us")
    for row in table[::2]:
        print("%.3f  %d  %-5s  %.4f  %.4f  %+.2f  %4d     %.1f  %.1f" % (
            row["theta_h"], row["k_pct_ap"], row["q_throttle_expo"], row["throttle_in"], row["r"], row["r_err_pct"],
            row["edgetx_override_pct"], row["pwm_us"], row["bin_margin_us"]))
    print("fuzz:", {k: v for k, v in fz.items() if k != "first_violations"}, fz["first_violations"][:3])
    for k, v in sc.items():
        print(k, v)
