"""T-097: collect landing_a.py outputs and SITL summaries into T097_results.json (case, metric, value, limit, pass) and plots.
usage (from anywhere):  python -I t097_collect.py        (landing txt files and sitl runs must exist; needs matplotlib)
Category labels: landing = rigid-body dynamics; SITL = flight dynamics."""
import json, os, re, subprocess, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, ".."))
SITL = os.path.abspath(os.path.join(HERE, "..", "..", "..", "sitl"))
rows = []

def add(analysis, category, case, metric, value, limit, op, note=""):
    if value is None: ok = False
    elif op == "<=": ok = value <= limit
    elif op == ">=": ok = value >= limit
    elif op == "<": ok = value < limit
    elif op == "==": ok = value == limit
    else: ok = None
    rows.append(dict(analysis=analysis, category=category, case=case, metric=metric, value=value, limit=f"{op} {limit}", **{"pass": (None if ok is None else bool(ok))}, note=note))

# ---------------------------------------------------------------- landing
LAND = {"cad_1881_p30": "AR-014 current: 1.881 kg CAD mass model, plateau 30 N", "cad_1881_p45": "AR-014 current: 1.881 kg CAD mass model, plateau 45 N",
        "items_1881_p30": "sensitivity: ITEMS roll-up scaled to 1.881 kg, plateau 30 N", "items_150_p30_cadgeom": "old mass list 1.50 kg on the current CAD geometry, plateau 30 N",
        "legacy_150_p30": "AR-008 reproduction (GEOM_LEGACY, 1.50 kg), plateau 30 N"}
land_all = {}
for tag, label in LAND.items():
    t = open(os.path.join(HERE, f"landing_{tag}.txt")).read()
    st = {k: float(v) for k, v in re.findall(r"'(tip_narrow_edge_toward_cg|tip_narrow|v_tip_parked|restore_ratio_5ms)': (?:np\.float64\()?([\d.eE+-]+)", t)}
    cases = {}
    for ln in t.splitlines():
        m = re.match(r"(.{28}) stroke max\s+([\d.]+) mm\s+n ([\d.]+)\s+Fmax\s+([\d.]+) N\s+side\s+([\d.]+) N\s+tilt_end\s+([\d.]+)\s+drift\s+(\d+) mm\s+set ([\d.]+)\s+rib RF ([\d.]+)", ln)
        if m: cases[m.group(1).strip()] = dict(stroke_mm=float(m.group(2)), n_g=float(m.group(3)), Fmax_N=float(m.group(4)), side_N=float(m.group(5)), tilt_deg=float(m.group(6)), drift_mm=int(m.group(7)), set_mm=float(m.group(8)), rib_rf=float(m.group(9)))
    land_all[tag] = dict(label=label, static=st, cases=cases)
    if not tag.startswith(("cad_", "items_1881")): continue
    ana = "AR-014" if tag.startswith("cad_") else "AR-014-sens"
    add(ana, "rigid-body dynamics", tag, "static tip-over, edge toward CG (deg)", round(st["tip_narrow_edge_toward_cg"], 2), 30.5, ">=", "A-P9 target 30.5 deg (D-233); 30 deg floor of AR-008")
    add(ana, "rigid-body dynamics", tag, "static tip-over, narrow axis (deg)", round(st["tip_narrow"], 2), 30.0, ">=", "")
    for cn, c in cases.items():
        cid = f"{tag}/{cn}"
        add(ana, "rigid-body dynamics", cid, "foam stroke (mm)", c["stroke_mm"], 20.0, "<=", "usable stroke 20 mm (EST)")
        add(ana, "rigid-body dynamics", cid, "peak load factor (g)", c["n_g"], 12.0, "<=", "A-P5 12 g")
        add(ana, "rigid-body dynamics", cid, "end tilt (deg)", c["tilt_deg"], 3.0, "<=", "no tip-over line")
        add(ana, "rigid-body dynamics", cid, "rib-root RF (min over run)", c["rib_rf"], 1.0, ">=", "AR-012 capacity check, EST allowables; the 0.15-margin project rule would want 1.15")
        add(ana, "rigid-body dynamics", cid, "side load per foot (N)", c["side_N"], None, "info", "14 N cap withdrawn (AR-012); reported, judged through rib RF")

# ---------------------------------------------------------------- SITL
SIT = {"T097_Z5": "Z5_gb0 case, A.param, no Lua", "T097_Z5_lua": "Z5_gb0 case + spin_cap.lua + battery monitor", "T097_T074": "T-074 r 1.33 transition, no monitor", "T097_T074_lua": "T-074 r 1.33 + Lua + battery monitor (T-076 configuration)"}
sit_all = {}
for tag, label in SIT.items():
    p = os.path.join(SITL, "runs", tag, "sum.json")
    if not os.path.exists(p): continue
    s = json.load(open(p)); sit_all[tag] = dict(label=label, sum=s)
    add("AR-015", "flight dynamics", tag, "peak altitude (m) from 50 m start", s.get("alt_peak_abs"), 110.0, "<", "fence 110 m")
    add("AR-015", "flight dynamics", tag, "max climb gain (m)", s.get("alt_max_gain"), 60.0, "<", "CL-B3-TRANS-CLIMB 60 m")
    add("AR-015", "flight dynamics", tag, "time to 1.3 Vs after mode change (s)", s.get("t_to_1.3Vs_s"), 15.0, "<=", "1.3 Vs = %s m/s at this mass; None = never reached" % s.get("v13"))
    add("AR-015", "flight dynamics", tag, "time at 0.90 cap run (s)", s.get("t_cap_run_s"), 1.0, "<=", "")
    add("AR-015", "flight dynamics", tag, "time with a motor >= 0.85 (s)", s.get("t_ge85_s"), 1.0, "<=", "")
    for b in (15, 20, 25):
        add("AR-015", "flight dynamics", tag, f"elevon pitch use of {b} deg", s.get(f"pitch_use_{b}"), 0.60, "<=", "pass line 0.60; governing basis (15/20/25 deg) undecided (AR-010 open item 5)")
    add("AR-015", "flight dynamics", tag, "elevon saturated time (s)", s.get("t_elevon_sat_s"), 1.0, "<=", "info line, EST")
    add("AR-015", "flight dynamics", tag, "touch in flight", int(bool(s.get("touch_in_flight"))), 0, "==", "")
    if "landing" in s:
        l = s["landing"]
        add("AR-015", "flight dynamics", tag, "QLAND touchdown sink (m/s)", None if l.get("sink_peak_last1s_ms") is None else l["sink_peak_last1s_ms"], 1.2, "<=", "")
        add("AR-015", "flight dynamics", tag, "tipped over after QLAND", int(bool(l.get("tipped_over"))), 0, "==", "")
    if "back" in s:
        add("AR-015", "flight dynamics", tag, "back-transition lean max in descent (deg)", s["back"].get("lean_max_in_descent"), None, "info", "no pass line stated")

json.dump(dict(task="T-097", generated="2026-11-23", rows=rows, landing_raw=land_all, sitl_raw={k: v["sum"] for k, v in sit_all.items()}), open(os.path.join(OUT, "T097_results.json"), "w"), indent=1)
print("rows", len(rows), "fails", sum(1 for r in rows if r["pass"] is False))
