"""A bench analysis: turns stand logs into pass/fail lines.
   python -I bench_analysis.py LOG.csv [LOG2.csv ...]
   python -I bench_analysis.py --selftest   (synthetic data from the maker table; checks the script only)
stdlib only. Columns: DATASHEET-TEMPLATE.csv. condition: zero_start | zero_end | fresh | sag | hold.
Every limit carries its source; EST = estimate. Rows are grouped by (motor, prop). Exit 1 if any FAIL.
"""
import csv, math, sys, tempfile, os

G = 9.80665
# ---- limits (source) ----------------------------------------------------------------------------
GATE_KG = 1.47                      # D-190 mass gate (was 1.50, BOARD C5): +-5 % window holds to 1.478 kg at cant 17
CANT = math.radians(17)             # D-189 (was 16 in D-184, 14 in BOARD C1): arm x1.2 + cant 17 deg
N_MOT = 4
TW_FRESH, TW_SAG = 2.0, 1.6         # BOARD s2 gates
T_FRESH = TW_FRESH * GATE_KG * 1000 / (N_MOT * math.cos(CANT))   # 769 gf per motor at 1.47 kg, cant 17
T_SAG = TW_SAG * GATE_KG * 1000 / (N_MOT * math.cos(CANT))       # 615 gf per motor at 1.47 kg, cant 17
T_R3 = 1201.0                       # BOARD R3 derate 0.93 x 1292 gf (APC 9x4.5MR model, one motor on the stand, 16.8 V; D-183)
# D-183: the T9545 is sold out; prop is APC 9x4.5MR (CW) / 9x4.5MRP (CCW). MAKER = model rows, NOT maker data: APC PER3_9x45MR.dat
# static rows (https://www.apcprop.com/files/PER3_9x45MR.dat, 2026-11-14) through Kv 780, Rm 0.173, I0 0.5 A (EST), one motor on a
# 16.8 V pack with R 30 mohm EST, throttle = duty (linear-voltage EST).  Tuple = (gf, bus A, rpm).  prop_a.py rebuilds it.
MAKER = {50: (378, 2.4, 5875), 65: (612, 4.8, 7451), 75: (789, 7.0, 8456), 85: (981, 9.6, 9420), 100: (1292, 14.6, 10792)}  # A = BUS current (watt meter) = phase A x duty
RPM100 = MAKER[100][2]
MN_I_MAX = 13.0                     # maker: 13 A / 180 s
SPIN_MAX_I = 10.9                   # prop_a.py: bus A of one motor at the 0.90 duty cap (12.1 A phase), three at hover, 1.50 kg, fresh
T_HOVER = 396.0                     # hover thrust per motor at the 1.47 kg gate: 1470 / (4 cos 17 x 0.97), prop_a.py (404 gf at 1.50 kg, 402 at cant 16)
P_HOVER = 47.6 / 0.98 * 1.15       # prop_a.py (cant 17, 1.47 kg) motor input 47.6 W at x0.93 derate, /0.98 ESC, +15 % (TEST-PLAN-QP1 hover_current_tol) = 55.9 W
# Yaw: SIZING-A s4 authority = 1.2 x (cant term + Q); cant term 0.201 N m (EST), wind moment 0.178 N m.
# ratio >= 1.5  <=>  Q >= 1.5 x 0.178 / 1.2 - 0.201/1.2 ... computed below from these two numbers.
# D-184 / D-189 (review/QP-2/WIND.md s5, review/QP-4/CLAIMS-FIX.md s2): arm x1.2 and cant 17 deg: cant term 0.201 x 1.2 x sin17/sin14 = 0.291 N m (EST); authority at +-0.10 throttle
#   = cant term + 1.2 Q (model Q 59.7 N mm: 0.291 + 0.072 = 0.363; at cant 16 it was 0.3465, WIND.md about 0.35 with Q = 65).  Pass line 0.35 N m, fail line 0.30 (5 m/s card reopened).
CANT_TERM, WIND_M = 0.201 * 1.2 * math.sin(math.radians(17)) / math.sin(math.radians(14)), 0.178
Q_MIN_NMM = 55.0                    # WIND.md s5: the rotor-reaction pass line Q >= 55 N mm stays
AUTH_PASS, AUTH_FAIL = 0.35, 0.30   # N m yaw authority at +-0.10 throttle, WIND.md s5
V_SAG = 13.6                        # prop_a.py: 4 motors saturated, pack at 3.73 V/cell rest, R 30 mohm EST
D_IN = {"9545": 9.5, "9045": 9.0, "1045": 10.0, "9x45MR": 9.0, "APC9x45MR": 9.0}
CT_BAND = (0.10, 0.125)             # APC 9x4.5MR static CT 0.114-0.118 (PER3 file); band is EST
R1_T, R1_I = 1100.0, 25.0           # BOARD R1; X2212 page 25 A / 30 s
R1_SAG = 872.0                      # 1.6 x 2180 g / 4 (BOARD s1 item 2 mass) EST
ZERO_DRIFT = 0.005                  # H1 GT-01
CAN_STOP = 80.0                     # TEST-PLAN-QP1 interim stop


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def rho(r):
    t, p, rh = f(r["ambient_c"]), f(r["pressure_hpa"]), f(r["rh_pct"]) or 0.0
    if t is None or p is None:
        return 1.225
    es = 6.1078 * 10 ** (7.5 * t / (t + 237.3)) * 100
    pv = rh / 100 * es
    pd = p * 100 - pv
    T = t + 273.15
    return pd / (287.05 * T) + pv / (461.5 * T)


def load(paths):
    out = []
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if not r.get("run"):
                    continue
                r["_rho"] = rho(r)
                T = f(r["thrust_gf"])
                r["_T"] = None if T is None else T * 1.225 / r["_rho"]   # H1: T_corr = T x 1.225/rho
                for k in ("throttle_pct", "hold_s", "torque_gf_100mm", "rpm_telem", "rpm_audio", "v_esc", "i_a", "can_c", "esc_c"):
                    r["_" + k] = f(r.get(k))
                out.append(r)
    return out


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def at(rows, cond, thr):
    return [r for r in rows if r["condition"] == cond and r["_throttle_pct"] is not None and abs(r["_throttle_pct"] - thr) < 0.5]


def interp(x, xs, ys):
    pts = sorted((a, b) for a, b in zip(xs, ys) if a is not None and b is not None)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1 and x1 > x0:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def rd(x, n=0):
    return "-" if x is None else f"{x:.{n}f}"


lines = []


def line(tag, name, value, limit, ok, src):
    res = "NOT RUN" if ok is None else ("PASS" if ok else "FAIL")
    lines.append((tag, res, name, value, limit, src))


def analyse(key, rows):
    motor, prop = key
    fresh = [r for r in rows if r["condition"] == "fresh"]
    sag = [r for r in rows if r["condition"] == "sag"]
    r100 = at(rows, "fresh", 100)
    T100 = mean([r["_T"] for r in r100])
    I100 = mean([r["_i_a"] for r in r100])
    V100 = mean([r["_v_esc"] for r in r100])
    tag = f"{motor}+{prop}"
    zs, ze = at(rows, "zero_start", 0), at(rows, "zero_end", 0)
    if zs and ze and T100:
        d = abs(mean([r["_T"] for r in ze]) - mean([r["_T"] for r in zs]))
        line(tag, "Zero drift start to end", f"{d:.1f} gf = {100*d/T100:.2f} % of 100 % thrust", f"<= {100*ZERO_DRIFT:.1f} %", d <= ZERO_DRIFT * T100, "H1 GT-01")
    else:
        line(tag, "Zero drift start to end", "no zero_start / zero_end rows", "<= 0.5 %", None, "H1 GT-01")
    mx = max([r["_can_c"] or 0 for r in rows])
    line(tag, "Can temperature never above stop", f"max {mx:.0f} C", f"<= {CAN_STOP:.0f} C", mx <= CAN_STOP, "TEST-PLAN-QP1 QP-P19")

    if motor.upper().startswith("MN2212"):
        line(tag, "Fresh thrust 100 % >= T/W 2.0 at 1.47 kg gate", f"{rd(T100)} gf", f">= {T_FRESH:.0f} gf", None if T100 is None else T100 >= T_FRESH, "BOARD C5; 2.0 x 1470 / (4 cos 17)")
        line(tag, "Fresh thrust 100 % >= 1201 gf (R3)", f"{rd(T100)} gf", f">= {T_R3:.0f} gf", None if T100 is None else T100 >= T_R3, "BOARD R3 (0.93 x APC model 1292); fail = resize once")
        if sag and at(rows, "sag", 100):
            Ts = mean([r["_T"] for r in at(rows, "sag", 100)])
            Vs = mean([r["_v_esc"] for r in at(rows, "sag", 100)])
            line(tag, "Sag thrust 100 % (pack at 20 % rest, 3.73 V/cell) >= T/W 1.6", f"{rd(Ts)} gf at {rd(Vs,2)} V", f">= {T_SAG:.0f} gf", None if Ts is None else Ts >= T_SAG, "BOARD C5; 1.6 x 1470 / (4 cos 17)")
        elif T100 and V100:
            est = T100 * (V_SAG / V100) ** 2 * 0.97
            line(tag, "Sag thrust ESTIMATED from fresh (T ~ V^2, hot x0.97); a sag-pack run replaces it", f"{est:.0f} gf at {V_SAG} V", f">= {T_SAG:.0f} gf", est >= T_SAG, "SIZING-A s3 (EST)")
        else:
            line(tag, "Sag thrust", "no data", f">= {T_SAG:.0f} gf", None, "BOARD C5")
        if T100:
            line(tag, "Prop derate: measured / APC-model 1292 gf at 100 % (one-motor stand)", f"{T100/MAKER[100][0]:.3f}", ">= 0.93 (1201 / 1292)", T100 / MAKER[100][0] >= 0.93, "APC model; BOARD R3")
            for thr in (50, 65, 75, 85):
                T = mean([r["_T"] for r in at(rows, "fresh", thr)])
                if T:
                    line(tag, f"  row {thr} %: measured / model {MAKER[thr][0]} gf", f"{T/MAKER[thr][0]:.3f}", "info", True, "APC model")
        thr_x = [r["_throttle_pct"] for r in fresh]
        Tx = [r["_T"] for r in fresh]
        pw = [(r["_v_esc"] * r["_i_a"]) if r["_v_esc"] and r["_i_a"] else None for r in fresh]
        ix = [r["_i_a"] for r in fresh]
        hov = interp(T_HOVER, Tx, thr_x) if Tx else None
        if hov is not None:
            P = interp(hov, thr_x, pw)
            I = interp(hov, thr_x, ix)
            line(tag, f"Hover point {T_HOVER:.0f} gf: throttle {hov:.0f} %, current {rd(I,2)} A", f"{rd(P,1)} W", f"<= {P_HOVER:.1f} W (model +15 %)", None if P is None else P <= P_HOVER, "prop_a.py (EST)")
        else:
            line(tag, "Hover point", "thrust rows do not bracket 396 gf", "", None, "SIZING-A s3")
        line(tag, "One-motor full-duty current, 100 % fresh 16.8 V", f"{rd(I100,1)} A", f"<= {MN_I_MAX} A (maker 13 A / 180 s; prop_a.py predicts 14.6 on the stand, over: the 0.90 cap is the fix)", None if I100 is None else I100 <= MN_I_MAX, "maker page; prop_a.py")
        I90 = mean([r["_i_a"] for r in at(rows, "fresh", 90)] + [r["_i_a"] for r in at(rows, "hold", 90)])
        line(tag, "Current at 90 % (Q_M_SPIN_MAX 0.90 cap)", f"{rd(I90,1)} A", f"<= {MN_I_MAX} A (sizing {SPIN_MAX_I})", None if I90 is None else I90 <= MN_I_MAX, "prop_a.py")
        hold = [r for r in rows if r["condition"] == "hold" and (r["_hold_s"] or 0) >= 180]
        if hold:
            ih = max(r["_i_a"] or 0 for r in hold)
            ch = max(r["_can_c"] or 0 for r in hold)
            line(tag, "180 s hold at 90 %: peak current, can temp", f"{ih:.1f} A, {ch:.0f} C", f"<= {MN_I_MAX} A and <= {CAN_STOP:.0f} C", ih <= MN_I_MAX and ch <= CAN_STOP, "maker 13 A / 180 s; QP-P19")
        else:
            line(tag, "180 s hold at 90 %: peak current, can temp", "no hold row with hold_s >= 180", f"<= {MN_I_MAX} A", None, "maker 13 A / 180 s")
        D = D_IN.get(prop, 9.5) * 0.0254
        te = mean([r["_rpm_telem"] for r in r100])
        au = mean([r["_rpm_audio"] for r in r100])
        rpm = te or au
        if rpm and T100:
            n = rpm / 60
            CT = (T100 / 1000 * G) / (r100[0]["_rho"] * n * n * D ** 4)
            line(tag, f"rpm at 100 % ({'telemetry' if te else 'audio'}) vs APC model {RPM100}", f"{rpm:.0f} rpm ({100*(rpm-RPM100)/RPM100:+.1f} %)", "info", True, "APC model")
            line(tag, "Static CT from measured thrust and rpm", f"{CT:.3f}", f"{CT_BAND[0]}-{CT_BAND[1]} (EST band)", CT_BAND[0] <= CT <= CT_BAND[1], "APC PER3 static CT 0.115")
            if te and au:
                line(tag, "Telemetry vs audio-FFT rpm", f"{100*(te-au)/au:+.1f} %", "within 3 %", abs(te - au) / au <= 0.03, "H1 GT-01 cross-check")
            line(tag, "Model rpm within 5 % of measured (FAIL = model or I0 is wrong)", f"{abs(rpm-RPM100)/RPM100*100:.1f} % apart", "<= 5 %", abs(rpm - RPM100) / RPM100 <= 0.05, "prop_a.py (EST)")
        else:
            line(tag, "rpm column check", "no rpm at 100 %", "", None, "SIZING-A s3")
        tq = [(r["_T"], r["_torque_gf_100mm"]) for r in fresh if r["_torque_gf_100mm"] is not None and r["_T"]]
        Qgf = interp(T_HOVER, [a for a, b in tq], [b for a, b in tq]) if tq else None
        if Qgf is not None:
            Q = Qgf / 1000 * G * 0.100 * 1000
            line(tag, f"Rotor reaction torque Q at {T_HOVER:.0f} gf (prop_a.py predicts 58-60 N mm; sizing EST 65)", f"{Q:.1f} N mm; Q/T {Q/(T_HOVER/1000*G):.1f} mm", f">= {Q_MIN_NMM:.0f} N mm", Q >= Q_MIN_NMM, "SIZING-A s4 with the D-184 cant term (WIND.md s5)")
            ratio = (CANT_TERM + 1.2 * Q / 1000) / WIND_M
            line(tag, f"Hover yaw ratio rebuilt with measured Q (cant term {CANT_TERM:.3f} N m at arm 1.2 / cant 17 stays EST)", f"{ratio:.2f}", ">= 1.5", ratio >= 1.5, "SIZING-A s4; hanging test still decides arm and Cd")
            auth = CANT_TERM + 1.2 * Q / 1000
            line(tag, f"Yaw authority at +-0.10 throttle from measured Q (fail < {AUTH_FAIL}: 5 m/s card reopened; model Q 59.7 N mm gives 0.363)", f"{auth:.3f} N m", f">= {AUTH_PASS} N m", auth >= AUTH_PASS, "WIND.md s5; the hanging yaw test at cant 16, arm 0.228 m is the real measurement")
        else:
            line(tag, "Rotor reaction torque Q", "no torque_gf_100mm rows bracketing 396 gf", f">= {Q_MIN_NMM:.0f} N mm", None, "SIZING-A s4")
    else:
        line(tag, "R1 price of the motor", "15.99 (ORDER-LIST O5)", "<= $25", True, "BOARD R1")
        line(tag, "R1 fresh thrust 100 % on 4S", f"{rd(T100)} gf", f">= {R1_T:.0f} gf", None if T100 is None else T100 >= R1_T, "BOARD R1 / s4")
        line(tag, "R1 peak current within maker 25 A / 30 s (hold <= 10 s)", f"{rd(I100,1)} A", f"<= {R1_I} A", None if I100 is None else I100 <= R1_I, "RMRC X2212 page")
        if sag and at(rows, "sag", 100):
            Ts = mean([r["_T"] for r in at(rows, "sag", 100)])
            line(tag, "R1 sag thrust (EST target for B at 2.18 kg)", f"{rd(Ts)} gf", f">= {R1_SAG:.0f} gf", None if Ts is None else Ts >= R1_SAG, "BOARD s1 item 2 (EST)")
        else:
            line(tag, "R1 sag thrust", "no sag run", f">= {R1_SAG:.0f} gf", None, "BOARD s1 item 2 (EST)")
        line(tag, "R1 second half: B re-priced margin at +30 % >= $150", "not a bench quantity: cost owner re-runs bom_qp1.py", ">= $150", None, "BOARD R1")


def main(argv):
    if "--selftest" in argv:
        path = os.path.join(tempfile.mkdtemp(), "selftest.csv")
        hdr = "test_id,date,run,condition,motor,prop,esc,throttle_pct,hold_s,thrust_gf,torque_gf_100mm,rpm_telem,rpm_audio,v_esc,i_a,can_c,esc_c,ambient_c,pressure_hpa,rh_pct,notes\n"
        rows = [hdr, "S,d,1,zero_start,MN2212,9545,e,0,5,0.5,0,0,0,16.8,0,25,25,20,1013,50,\n",
                "S,d,1,zero_end,MN2212,9545,e,0,5,1.0,0,0,0,16.8,0,25,25,20,1013,50,\n"]
        for thr, (T, I, rpm) in MAKER.items():
            rows.append(f"S,d,1,fresh,MN2212,9545,e,{thr},3,{T*0.96:.0f},{T*0.96*0.15:.1f},{rpm*0.88:.0f},{rpm*0.88:.0f},16.2,{I*1.05:.1f},40,45,20,1013,50,\n")
        rows.append("S,d,2,fresh,MN2212,9545,e,90,3,1030,,8900,8900,16.2,11.4,40,45,20,1013,50,\n")
        rows.append("S,d,3,hold,MN2212,9545,e,90,180,1030,,8900,8900,16.0,11.4,70,60,20,1013,50,\n")
        rows.append("S,d,4,sag,MN2212,9545,e,100,2,800,,8700,8700,13.6,11.5,55,55,20,1013,50,\n")
        rows.append("S,d,1,fresh,X2212,1045,e,100,2,1180,,0,0,16.2,17.5,40,45,20,1013,50,\n")
        with open(path, "w") as fh:
            fh.write("".join(rows))
        argv = [path]
    rows = load([a for a in argv if not a.startswith("--")])
    groups = {}
    for r in rows:
        groups.setdefault((r["motor"], r["prop"]), []).append(r)
    for k, v in groups.items():
        analyse(k, v)
    print("| Config | Result | Check | Measured | Limit | Source |\n|---|---|---|---|---|---|")
    for l in lines:
        print("| " + " | ".join(l) + " |")
    nf = sum(1 for l in lines if l[1] == "FAIL")
    nn = sum(1 for l in lines if l[1] == "NOT RUN")
    npass = sum(1 for l in lines if l[1] == "PASS")
    print(f"\n{npass} PASS, {nf} FAIL, {nn} NOT RUN")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
