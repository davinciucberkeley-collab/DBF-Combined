"""T-064r F8: name and read the SITL touchdown records.  python -I landing_sitl_records_a.py
Glob: redesign/qp/A/sitl/runs/*/sum.json (this script's ../sitl/runs).  Per file two key spellings are read: 'landing' (dict, one touchdown) and 'land' (dict of cases,
each a dict with the same fields).  Fields: lateral_speed_ms, lean_deg_at_touch, sink_peak_last1s_ms, sink_ms, tipped_over, wind, wfrom, mass."""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
def records():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "..", "sitl", "runs", "*", "sum.json"))):
        d = json.load(open(f)); run = os.path.basename(os.path.dirname(f))
        if isinstance(d.get("landing"), dict) and "lateral_speed_ms" in d["landing"]: out.append((run, "landing", d["landing"]))
        if "lateral_speed_ms" in d: out.append((run, "toplevel", d))
    return out
if __name__ == "__main__":
    r = records()
    print(f"{len(r)} records with lateral_speed_ms: {sum(1 for x in r if x[1]=='landing')} under key 'landing', {sum(1 for x in r if x[1]!='landing')} at the top level")
    for key, lab in (("lateral_speed_ms", "lateral speed m/s"), ("sink_peak_last1s_ms", "peak sink last 1 s m/s"), ("lean_deg_at_touch", "lean at touch deg")):
        v = [(x[2].get(key), x[0], x[1]) for x in r if x[2].get(key) is not None]
        print(f"max {lab}: {max(v)[0]} ({max(v)[1]} {max(v)[2]}), n = {len(v)}")
    print("tipped_over true:", [x[0] for x in r if x[2].get("tipped_over")])
    print("run | key | lean | lateral | sink peak | tipped")
    for x in r: print(x[0], x[1], x[2].get("lean_deg_at_touch"), x[2].get("lateral_speed_ms"), x[2].get("sink_peak_last1s_ms"), x[2].get("tipped_over"))
