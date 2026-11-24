"""T-101: summarise candidate SITL runs (fwd_sum.py output) against the T-097 limits into ../T101_results.json and print a table.
usage: python -I t101_collect.py [--merge] C1 [C2 ...]   (category: flight dynamics). Baseline = T097 runs.
--merge (T-101 U-B) keeps the entries already in ../T101_results.json and updates only the named candidates; C3G (tag T101C3G_T074) adds the c3g_metrics.json block (t101_c3g_metrics.py)."""
import json, os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); SITL = os.path.abspath(os.path.join(HERE, "..", "..", "..", "sitl")); OUT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, SITL)
import subprocess
LIM = [("alt_peak_abs", "<", 110.0), ("alt_max_gain", "<", 60.0), ("t_to_1.3Vs_s", "<=", 15.0), ("t_cap_run_s", "<=", 1.0), ("t_ge85_s", "<=", 1.0), ("pitch_use_15", "<=", 0.60), ("t_elevon_sat_s", "<=", 1.0)]
def ok(v, op, l): return v is not None and {"<": v < l, "<=": v <= l}[op]
MERGE = "--merge" in sys.argv; ARGS = [a for a in sys.argv[1:] if a != "--merge"]
res = json.load(open(os.path.join(OUT, "T101_results.json")))["runs"] if MERGE else {}
for cand in ["T097"] + ARGS:
    pre = "T097" if cand == "T097" else "T101" + cand
    for suf in ("Z5", "Z5_lua", "T074", "T074_lua"):
        tag = f"{pre}_{suf}"; p = os.path.join(SITL, "runs", tag, "sum.json")
        if not os.path.exists(p): continue
        s = json.load(open(p)); r = dict(sum=s, checks={})
        for k, op, l in LIM: r["checks"][k] = dict(value=s.get(k), limit=f"{op} {l}", **{"pass": bool(ok(s.get(k), op, l))})
        r["checks"]["touch_in_flight"] = dict(value=int(s.get("touch_in_flight", 0)), limit="== 0", **{"pass": not s.get("touch_in_flight")})
        if "landing" in s:
            L = s["landing"]; r["checks"]["qland_sink_peak"] = dict(value=L.get("sink_peak_last1s_ms"), limit="<= 1.2", **{"pass": bool(ok(L.get("sink_peak_last1s_ms"), "<=", 1.2))})
            r["checks"]["tipped_over"] = dict(value=int(bool(L.get("tipped_over"))), limit="== 0", **{"pass": not L.get("tipped_over")})
        if cand == "C3G" and os.path.exists(os.path.join(HERE, "c3g_metrics.json")): r["c3g_metrics"] = json.load(open(os.path.join(HERE, "c3g_metrics.json"))).get(tag)
        r["all_pass"] = all(c["pass"] for c in r["checks"].values()); res[tag] = r
        print(f"{tag:22s} pu15 {s.get('pitch_use_15')} el {s.get('elevon_max_deg')} peak {s.get('alt_peak_abs')} gain {s.get('alt_max_gain')} t13 {s.get('t_to_1.3Vs_s')} umax {s.get('u_max')} Ipk {s.get('I_pack_peak_A')} V_end {s.get('V_end')} all_pass {r['all_pass']}" + (f" fails {[k for k,c in r['checks'].items() if not c['pass']]}" if not r["all_pass"] else ""))
        d = os.path.join(HERE, f"sitl_{tag}")
        if cand != "T097": os.makedirs(d, exist_ok=True); [shutil.copy(os.path.join(SITL, "runs", tag, f), d) for f in ("sum.json", "result.json", "A_sitl.parm") if os.path.exists(os.path.join(SITL, "runs", tag, f))]
        if cand != "T097" and (suf == "Z5" or cand == "C3G") and os.path.exists(os.path.join(SITL, "runs", tag, "case.fwd.csv")): shutil.copy(os.path.join(SITL, "runs", tag, "case.fwd.csv"), d)
json.dump(dict(task="T-101", generated="2026-11-24" if MERGE else "2026-11-23", category="flight dynamics", runs=res), open(os.path.join(OUT, "T101_results.json"), "w"), indent=1)
