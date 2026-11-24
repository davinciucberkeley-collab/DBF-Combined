"""F4 follow-up 4: cruise battery-failsafe geometry from a battC run.  python fu_batt.py tag [tag ...]
Reports from the trigger (marks.t_fail): time to QLAND, to touchdown, max horizontal distance from the trigger point, the part of it along the outward (pre-trigger track) direction,
energy (Wh) trigger -> touchdown from the plant's pack integral, altitude when QLAND starts."""
import csv, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def run(tag):
    r = json.load(open(os.path.join(HERE, "runs", tag, "result.json"))); mk = r.get("marks") or r["mk"]
    rows = list(csv.DictReader(open(os.path.join(HERE, "runs", tag, "case.fwd.csv"))))
    t0 = mk["t_fail"]; i0 = next(i for i, x in enumerate(rows) if float(x["t"]) >= t0)
    p0 = (float(rows[i0]["pn"]), float(rows[i0]["pe"])); pb = (float(rows[i0 - 40]["pn"]), float(rows[i0 - 40]["pe"]))
    hx = (p0[0] - pb[0], p0[1] - pb[1]); hn = math.hypot(*hx); hx = (hx[0] / hn, hx[1] / hn)
    ev = {e[1]: e[0] for e in r["events"]}
    tq = next((e[0] for e in r["events"] if "QLAND" in e[1].upper() or "Q LAND" in e[1].upper()), None)
    tl = next((e[0] for e in r["events"] if "Land complete" in e[1]), float(rows[-1]["t"]))
    seg = [x for x in rows[i0:] if float(x["t"]) <= tl]
    dmax = max(math.hypot(float(x["pn"]) - p0[0], float(x["pe"]) - p0[1]) for x in seg)
    out = max((float(x["pn"]) - p0[0]) * hx[0] + (float(x["pe"]) - p0[1]) * hx[1] for x in seg)
    wh = float(seg[-1]["wh"]) - float(rows[i0]["wh"])
    modes = [m for m in r.get("modes", []) if m[0] >= t0 - 1]
    return dict(tag=tag, t_fail=round(t0, 1), modes=modes[:5], t_touch_s=round(tl - t0, 1), max_dist_from_trigger_m=round(dmax, 0), max_outward_m=round(out, 0), Wh=round(wh, 2),
                alt_trigger=round(float(rows[i0]["alt"]), 0), events=[e for e in r["events"] if e[0] >= t0 - 1][:8])
if __name__ == "__main__":
    for t in sys.argv[1:]: print(run(t))
