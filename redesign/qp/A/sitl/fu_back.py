"""F4 follow-up 3: back-transition metrics from a run's case.fwd.csv + result.json (cases with chain=1).  python fu_back.py tag [tag ...]
Reports: entry airspeed at the switch, alt balloon above the switch altitude, motor duty peak and seconds at / above the 0.895 cap, seconds above 0.85, time to pitch-up complete, time to 3 m/s."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def run(tag):
    r = json.load(open(os.path.join(HERE, "runs", tag, "result.json"))); mk = r.get("marks") or r["mk"]
    rows = list(csv.DictReader(open(os.path.join(HERE, "runs", tag, "case.fwd.csv"))))
    t0 = mk["t_back"]; tq = mk.get("t_qland", t0 + 40)
    seg = [x for x in rows if t0 <= float(x["t"]) <= t0 + 25]
    dt = float(rows[1]["t"]) - float(rows[0]["t"])
    um = [max(float(x["u%d" % i]) for i in range(1, 5)) for x in seg]
    cap = 0.0; run_ = 0.0; best = 0.0
    for u in um:
        if u >= 0.895: run_ += dt; best = max(best, run_)
        else: run_ = 0.0
    a0 = float(seg[0]["alt"]); amax = max(float(x["alt"]) for x in seg)
    v0 = float(seg[0]["V"]); t3 = next((float(x["t"]) - t0 for x in seg if float(x["V"]) < 3.0 and float(x["t"]) - t0 > 2), None)
    tp = next((float(x["t"]) - t0 for x in seg if float(x["pitch"]) > 70), None)   # pitch > 70 deg = past the tilt-angle in the hover direction
    import math
    s3 = next((x for x in seg if float(x['V']) < 3.0 and float(x['t']) - t0 > 2), seg[-1])
    dist = math.hypot(float(s3['pn']) - float(seg[0]['pn']), float(s3['pe']) - float(seg[0]['pe']))
    return dict(tag=tag, dist_to_3ms_m=round(dist, 0), V_switch=round(v0, 1), balloon_m=round(amax - a0, 1), u_max=round(max(um), 3), s_cap_run=round(best, 2), s_cap_total=round(sum(dt for u in um if u >= 0.895), 2),
                s_ge85=round(sum(dt for u in um if u >= 0.85), 2), t_pitchup_s=None if tp is None else round(tp, 1), t_to_3ms_s=None if t3 is None else round(t3, 1),
                lean_max_after=max(90 - float(x["pitch"]) for x in rows if t0 + 10 <= float(x["t"]) <= tq))
if __name__ == "__main__":
    for t in sys.argv[1:]: print(run(t))
