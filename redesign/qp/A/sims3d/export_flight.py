"""T-105 unit 1: export SITL flight runs to 10 Hz JSON for the 3-D viewer.   python -I export_flight.py [run ...]   (default: the 16 runs below)
Reads redesign/qp/A/sitl/runs/<run>/{case.fwd.csv, case.events.json, result.json}; pass/fail lines from mechanism/out/T101_results.json (all 16 runs;
T097 rows also in T097_results.json AR-015); pitch-use scalars from sitl/fwd_sum.py (trans(), no files written there).
Writes sims3d/out/flight_<run>.json.  Read-only on the sitl and mechanism folders."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.normpath(os.path.join(HERE, ".."))
SITL = os.path.join(A, "sitl"); sys.path.insert(0, SITL)
import fwd_sum                                   # noqa: E402  (module has no import-time side effects)
OUT = os.path.join(HERE, "out")
RUNS = [r + s for r in ("T097", "T101C1", "T101C2", "T101C3", "T101A1") for s in ("_T074", "_T074_lua", "_Z5", "_Z5_lua")] + ["T101A1RQ4_T074"]   # A1 = D-255 adopted
RATE_HZ = 10.0
SD = lambda x: round(float(x), 3)                # 3 decimals
FIELDS = [("t", "t"), ("pn", "pn"), ("pe", "pe"), ("alt", "alt"), ("pitch", "pitch"), ("roll", "roll"), ("hdg_nose", "hdg_nose"), ("dl", "dl"), ("dr", "dr"),
          ("th1", "th1"), ("th2", "th2"), ("th3", "th3"), ("th4", "th4"), ("V", "V"), ("alpha", "alpha"), ("touch", "touch")]
CONV = dict(
    source="a_plant.py (euler_rpy, step, fwd_loads) and a_aero.py (airframe) in redesign/qp/A/sitl; csv writer at a_plant.py 'frows.append'",
    time="t = plant clock, s (starts at 0.05 s); 10 Hz = the first plant sample at or after each 0.1 s tick (plant log rate about 19.7 Hz)",
    world_frame="NED. pn = north (m, +N), pe = east (m, +E) from the start point (pos[0], pos[1]); alt = up from the ground plane at the start, m (= -pos[2]). Hover start alt 0.314 m = fin feet on ground.",
    body_frame="FRD in cruise attitude: x nose (chord), y right wing, z belly. Hover = nose up (x_b up); copter forward = +z_b (belly), copter right = +y_b, copter down = -x_b (tail).",
    pitch_deg="pitch = asin(-x_b.z_world(down)) = angle of the nose above the horizon, deg: +90 = nose straight up (the hover / tailsitter stance), 0 = level cruise, +90 -> 0 in the forward transition.",
    roll_deg="roll = atan2(y_b.z, z_b.z), deg, about the nose axis; 0 = upright cruise, +ve = right wing down. Undefined (jumps 0/180) in hover at pitch 90 (gimbal): use only once pitch < ~80.",
    hdg_nose_deg="atan2(x_b.east, x_b.north), deg from north, clockwise; the nose heading. Undefined (0/180 jumps) while pitch is near 90; hdg_belly (not exported) is the copter-forward heading used in hover.",
    elevons_deg="dl = left elevon (-y wing, SERVO5), dr = right elevon (+y wing, SERVO6): checked in a_aero.airframe (Mx += EL_Y*FzR - EL_Y*FzL). Trailing edge DOWN positive, deg. Plant stops +-20 deg (EL_MAX), rate 300 deg/s, lag 0.04 s. (Servo pulse sign es5 = +1, es6 = -1.)",
    th1_4_N="thrust of motors 1..4 in N (after DOWNLOAD and HOT factors), the plant 'thr' list; motor positions/spin from a_plant mpos/mspin, X layout +-0.19 m y, +-0.13 m z.",
    V_ms="airspeed magnitude in the x-z body plane, sqrt(u^2+w^2) m/s (DG V, wind-relative)", alpha_deg="atan2(w, u) of the wind-relative velocity in body axes, deg; +ve = relative wind from below the nose",
    touch="number of the four fin-foot contact points below ground (0-4); 0 = airborne",
    pitch_use_15="per-sample |0.5(dl+dr)|/15 deg: mean elevon deflection as a share of 15 deg, the AR-015 / fwd_sum definition; _scalar holds the max over t_fbwa..t_cruise_end (fwd_sum.trans)",
    events="case.events.json is [] in every run (the plant logs events only when a cmd_file is used); marks / modes / events come from result.json (t = plant clock, mark times = driver clock st['t'])")


def downsample(T):
    idx, nxt = [], 0.0
    for i, t in enumerate(T):
        if t >= nxt - 1e-9:
            idx.append(i); nxt = (int(t * RATE_HZ + 1e-9) + 1) / RATE_HZ
    if idx[-1] != len(T) - 1: idx.append(len(T) - 1)
    return idx


def export(run, t101, t097):
    d = os.path.join(SITL, "runs", run)
    rows = list(csv.DictReader(open(os.path.join(d, "case.fwd.csv"))))
    f = {k: [float(r[k]) for r in rows] for k in rows[0]}
    res = json.load(open(os.path.join(d, "result.json")))
    ev = json.load(open(os.path.join(d, "case.events.json")))
    idx = downsample(f["t"])
    data = {name: [SD(f[col][i]) for i in idx] for name, col in FIELDS}
    data["touch"] = [int(f["touch"][i]) for i in idx]
    data["pitch_use_15"] = [SD(abs(0.5 * (f["dl"][i] + f["dr"][i])) / 15.0) for i in idx]
    s = fwd_sum.trans(f, res)
    if run in t101["runs"]:
        r = t101["runs"][run]
    else:   # D-255 / AM-068: adopted A1 runs are not in T101_results.json; lines from fwd_sum.trans (pitch use <= 0.60 for the plain cases, elevon below the 20 deg stop for the gust + roll case)
        gust = "RQ" in run
        lines = {"elevon_below_stop": dict(value=s["elevon_max_deg"], limit="< 20 deg", ok=s["elevon_max_deg"] < 19.9)}
        if not gust: lines["pitch_use_15"] = dict(value=s["pitch_use_15"], limit="<= 0.60", ok=s["pitch_use_15"] <= 0.60)
        r = dict(all_pass=all(v["ok"] for v in lines.values()), checks=lines)
    meta = dict(run=run, mass_kg=res["mass"], setup=dict(args=res["args"], case=res["case"], cfg={k: v for k, v in res["cfg"].items() if k != "out"}, entry=res.get("entry"), thst_hover=res.get("thst_hover")),
                lua=run.endswith("_lua"), rate_hz=RATE_HZ, n_samples=len(idx), n_source_samples=len(rows), duration_s=f["t"][-1],
                pass_fail=dict(source=("mechanism/out/T101_results.json runs[run].checks (result.json itself carries no pass/fail)" if run in t101["runs"] else "sitl/fwd_sum.py trans() lines for the D-255 A1 runs (CHANGE-LOG D-255)"), all_pass=r["all_pass"],
                               lines={k: dict(v) for k, v in r["checks"].items()},
                               ar015_rows=[dict(metric=x["metric"], value=x["value"], limit=x["limit"], **{"pass": x["pass"]}) for x in t097 if x["case"] == run]),
                pitch_use_scalar=dict(pitch_use_15=s["pitch_use_15"], pitch_use_20=s["pitch_use_20"], pitch_use_25=s["pitch_use_25"], elevon_max_deg=s["elevon_max_deg"], window="t_fbwa .. t_cruise_end"),
                summary={k: s[k] for k in ("alt_peak_abs", "alt_max_gain", "t_to_1.3Vs_s", "V_at_handover", "u_max", "hinge_peak_Nm", "alpha_max", "nz_max") if k in s},
                conventions=CONV, fields=[n for n, _ in FIELDS] + ["pitch_use_15"])
    events = dict(source_case_events_json=ev, marks=res["marks"], modes=[list(m) for m in res["modes"]], events=[list(e) for e in res["events"]])
    out = dict(meta=meta, events=events, **data)
    p = os.path.join(OUT, "flight_%s.json" % run)
    json.dump(out, open(p, "w"), separators=(",", ":"))
    return p, os.path.getsize(p)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    t101 = json.load(open(os.path.join(A, "mechanism", "out", "T101_results.json")))
    t097 = [x for x in json.load(open(os.path.join(A, "mechanism", "out", "T097_results.json")))["rows"] if x["analysis"] == "AR-015"]
    for run in (sys.argv[1:] or RUNS):
        p, n = export(run, t101, t097)
        print("%s  %.1f KB" % (p, n / 1024))
