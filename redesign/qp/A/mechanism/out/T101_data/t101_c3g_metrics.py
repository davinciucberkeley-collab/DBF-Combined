"""T-101 U-B: C3G metrics from the plant csv (case.fwd.csv) and the SITL dataflash log (ATT, RCOU) of a T101C3* run.
usage: <venv python> t101_c3g_metrics.py <tag> [<tag> ...]  -> T101_data/c3g_metrics.json (+ print). Window: from the cruise-event start t0 = t_c3g0 (C3G) or t_cruise_mode + 1.2 s (baseline), 3.0 s (the doublet) and +1.0 s recovery.
Elevon: dl = SERVO5 (left), dr = SERVO6 (right), deg, + = plant sign; the per-side stops are +-20 deg, the PWM-range clip of A.param is +19.04 / -19.88 (SERVO5) and -19.04 / +19.88 (SERVO6) (SITL runs SERVO5/6 MIN/MAX 1000/2000, so the plant clip is the 20 deg stop only)."""
import csv, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SITL = os.path.abspath(os.path.join(HERE, "..", "..", "..", "sitl"))
from pymavlink import DFReader
out = {}
for tag in sys.argv[1:]:
    d = os.path.join(SITL, "runs", tag); rows = list(csv.DictReader(open(os.path.join(d, "case.fwd.csv")))); f = {k: [float(r[k]) for r in rows] for k in rows[0]}
    res = json.load(open(os.path.join(d, "result.json"))); mk = res["marks"]; T = f["t"]
    t0 = mk["t_c3g0"] if "t_c3g0" in mk else mk["t_cruise_mode"] + 1.2; t1 = t0 + 3.0; t2 = t1 + 1.0
    tc = mk["t_cruise_mode"]; ife = mk["t_fwdone"]
    def sel(a, b): return [i for i in range(len(T)) if a <= T[i] <= b]
    I3, I4, Ic, Ipre = sel(t0, t1), sel(t0, t2), sel(ife, mk["t_cruise_end"]), sel(ife, t0)
    dl, dr = f["dl"], f["dr"]; mean = [0.5 * (a + b) for a, b in zip(dl, dr)]; diff = [0.5 * (a - b) for a, b in zip(dl, dr)]
    pk = lambda x, I: max(abs(x[i]) for i in I)
    r = dict(tag=tag, window_s=[round(t0, 3), round(t1, 3), round(t2, 3)],
             peak_left_deg=round(pk(dl, Ic), 2), peak_right_deg=round(pk(dr, Ic), 2), peak_left_events_deg=round(pk(dl, I4), 2), peak_right_events_deg=round(pk(dr, I4), 2),
             peak_left_signed=[round(min(dl[i] for i in Ic), 2), round(max(dl[i] for i in Ic), 2)], peak_right_signed=[round(min(dr[i] for i in Ic), 2), round(max(dr[i] for i in Ic), 2)],
             mean_elevon_peak_deg=round(pk(mean, Ic), 2), mean_elevon_peak_before_events_deg=round(pk(mean, Ipre), 2), mean_elevon_peak_events_deg=round(pk(mean, I4), 2),
             diff_elevon_peak_events_deg=round(pk(diff, I4), 2),
             t_sat_20_s=round(0.05 * sum(1 for i in Ic if max(abs(dl[i]), abs(dr[i])) >= 19.95), 2), t_sat_19p04_s=round(0.05 * sum(1 for i in Ic if max(abs(dl[i]), abs(dr[i])) >= 19.04), 2),
             t_sat_20_left_s=round(0.05 * sum(1 for i in Ic if abs(dl[i]) >= 19.95), 2), t_sat_20_right_s=round(0.05 * sum(1 for i in Ic if abs(dr[i]) >= 19.95), 2),
             p_peak_degs=round(pk(f["p"], I4), 1), p_peak_pos_degs=round(max(f["p"][i] for i in I4), 1), p_peak_neg_degs=round(min(f["p"][i] for i in I4), 1), roll_peak_deg=round(pk(f["roll"], I4), 1),
             pitch_peak_events_deg=round(max(f["pitch"][i] for i in I4), 1), V_min_events=round(min(f["V"][i] for i in I4), 2), alpha_max_events=round(max(f["alpha"][i] for i in I4), 1), nz_max_events=round(max(f["nz"][i] for i in I4), 2))
    lg = DFReader.DFReader_binary(os.path.join(d, "logs", "00000001.BIN"), zero_time_base=False); att = []; rcou = []
    while True:
        m = lg.recv_match(type=["ATT", "RCOU"])
        if m is None: break
        if m.get_type() == "ATT": att.append((m.TimeUS / 1e6, m.DesRoll, m.Roll, m.DesPitch, m.Pitch))
        else: rcou.append((m.TimeUS / 1e6, m.C5, m.C6))
    for nm, a, b in (("events", t0, t1), ("events_plus_recovery", t0, t2)):
        W = [x for x in att if a <= x[0] <= b]
        er = [x[2] - x[1] for x in W]; ep = [x[4] - x[3] for x in W]
        r["att_" + nm] = dict(n=len(W), roll_err_peak_deg=round(max(abs(e) for e in er), 1), roll_err_rms_deg=round(math.sqrt(sum(e * e for e in er) / len(er)), 1),
                              pitch_err_peak_deg=round(max(abs(e) for e in ep), 1), pitch_err_rms_deg=round(math.sqrt(sum(e * e for e in ep) / len(ep)), 1),
                              des_roll_range=[round(min(x[1] for x in W), 1), round(max(x[1] for x in W), 1)], des_pitch_range=[round(min(x[3] for x in W), 1), round(max(x[3] for x in W), 1)])
    Wr = [x for x in rcou if t0 <= x[0] <= t2]
    r["rcou_events_pwm"] = dict(c5=[min(x[1] for x in Wr), max(x[1] for x in Wr)], c6=[min(x[2] for x in Wr), max(x[2] for x in Wr)],
                               t_c5_or_c6_at_pwm_limit_s=round(sum(1 for x in Wr if x[1] <= 1001 or x[1] >= 1999 or x[2] <= 1001 or x[2] >= 1999) * (t2 - t0) / max(1, len(Wr)), 2))
    out[tag] = r
json.dump(out, open(os.path.join(HERE, "c3g_metrics.json"), "w"), indent=1); print(json.dumps(out, indent=1))
