"""Summarise run_fwd.py runs (QP-3). usage: python fwd_sum.py <tag> [<tag> ...]   -> one JSON line each, plus runs/<tag>/sum.json.
Pass lines are the F4 / B3 lines stated in SITL-FLIGHT.md section 1 (EST, ours); they are applied here only to label."""
import csv, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

def load(tag):
    d = os.path.join(HERE, "runs", tag)
    rows = list(csv.DictReader(open(os.path.join(d, "case.fwd.csv"))))
    f = {k: [float(r[k]) for r in rows] for k in rows[0]}
    res = json.load(open(os.path.join(d, "result.json")))
    return f, res

def idx(ts, t0):
    for i, t in enumerate(ts):
        if t >= t0: return i
    return len(ts) - 1

def runlen(flags, dt=0.05):
    best = cur = 0
    for x in flags:
        cur = cur + 1 if x else 0; best = max(best, cur)
    return best * dt

def vs_mission(m): return 11.70 * math.sqrt(m / 1.381)       # MISSION.md s1 (CLmax 0.75, rho 1.20)

def trans(f, res):
    mk = res["marks"]; m = res["mass"]; T = f["t"]
    out = dict(case="trans", mass=m, wind=res["cfg"]["wind"], wfrom=res["cfg"]["wind_from_deg"], r=res["entry"]["r_target"] if res.get("entry") else None)
    if "t_fbwa" not in mk: out["verdict"] = "no entry"; return out
    i0, i1 = idx(T, mk["t_qstab"]), idx(T, mk["t_fbwa"])
    ife = idx(T, mk["t_fwdone"]) if mk.get("t_fwdone") else None
    ic = idx(T, mk["t_cruise_mode"]); iend = idx(T, mk["t_cruise_end"])
    alt0 = f["alt"][i0]; seg = range(i0, ic)
    out["alt0"] = round(alt0, 1)
    out["alt_gain_at_handover"] = round(f["alt"][ife] - alt0, 1) if ife else None
    out["alt_max_gain"] = round(max(f["alt"][i0:iend]) - alt0, 1); out["alt_min_loss"] = round(min(f["alt"][i0:iend]) - alt0, 1)
    out["alt_peak_abs"] = round(max(f["alt"][i0:iend]), 1)
    v13 = 1.3 * vs_mission(m)
    out["v13"] = round(v13, 2)
    t13 = next((T[i] - mk["t_fbwa"] for i in range(i1, iend) if f["V"][i] >= v13), None)
    out["t_to_1.3Vs_s"] = None if t13 is None else round(t13, 1)
    vh = f["V"][ife] if ife else None
    out["V_at_handover"] = None if vh is None else round(vh, 1)
    de = [0.5 * (f["dl"][i] + f["dr"][i]) for i in range(i1, iend)]; dr = [0.5 * abs(f["dl"][i] - f["dr"][i]) for i in range(i1, iend)]
    out["pitch_use_15"] = round(max(abs(x) for x in de) / 15.0, 2); out["pitch_use_25"] = round(max(abs(x) for x in de) / 25.0, 2); out["pitch_use_20"] = round(max(abs(x) for x in de) / 20.0, 2)
    out["elevon_max_deg"] = round(max(max(abs(f["dl"][i]), abs(f["dr"][i])) for i in range(i1, iend)), 1)
    out["t_elevon_sat_s"] = round(sum(0.05 for i in range(i1, iend) if max(abs(f["dl"][i]), abs(f["dr"][i])) >= 19.5), 2)
    um = [max(f["u1"][i], f["u2"][i], f["u3"][i], f["u4"][i]) for i in range(i0, iend)]
    out["u_max"] = round(max(um), 3); out["t_cap_run_s"] = round(runlen([u >= 0.895 for u in um]), 2); out["t_ge85_s"] = round(sum(0.05 for u in um if u >= 0.85), 2)
    out["I_pack_peak_A"] = round(max(f["ipack"][i0:iend]), 1); out["I_motor_peak_A"] = round(max(max(f["i%d" % k][i0:iend]) for k in (1, 2, 3, 4)), 1)
    out["hinge_peak_Nm"] = round(max(f["hinge"][i0:iend]), 4)
    out["pitch_max"] = round(max(f["pitch"][i1:iend]), 1); out["roll_max_abs_after_fwdone"] = round(max(abs(x) for x in f["roll"][ife or i1:iend]), 1)
    out["alpha_max"] = round(max(f["alpha"][i1:iend]), 1); out["nz_max"] = round(max(f["nz"][i0:iend]), 2)
    out["V_end"] = round(sum(f["V"][iend - 20:iend]) / 20, 1); out["alt_end"] = round(f["alt"][iend], 1)
    out["roll_end_abs"] = round(max(abs(x) for x in f["roll"][iend - 40:iend]), 1); out["touch_in_flight"] = any(x > 0 for x in f["touch"][i1:iend])
    out["crossed_fence_110"] = max(f["alt"][i0:iend]) > 110.0
    out["t_fwdone_s"] = None if not ife else round(T[ife] - mk["t_fbwa"], 1)
    out["Wh_to_cruise"] = round(f["wh"][iend] - f["wh"][i0], 2)
    out["P_cruise_end_W"] = round(sum(f["ipack"][iend - 20:iend]) / 20 * sum(f["vbus"][iend - 20:iend]) / 20, 0)
    return out

def landing(f, res, t0, label):
    T = f["t"]; i0 = idx(T, t0)
    out = dict(case=label, mass=res["mass"], wind=res["cfg"]["wind"], wfrom=res["cfg"]["wind_from_deg"])
    it = next((i for i in range(i0, len(T)) if f["touch"][i] > 0), None)
    if it is None: out["touchdown"] = None; return out
    out["t_touch"] = T[it]
    out["sink_ms"] = round(-f["vu"][it], 2); out["sink_peak_last1s_ms"] = round(max(-f["vu"][j] for j in range(max(i0, it - 20), it + 1)), 2)
    out["lean_deg_at_touch"] = round(90 - f["pitch"][it], 1); out["lateral_speed_ms"] = round(math.hypot(f["vn"][it], f["ve"][it]), 2)
    out["drift_m_from_qland_start"] = round(math.hypot(f["pn"][it] - f["pn"][i0], f["pe"][it] - f["pe"][i0]), 1)
    j = min(len(T) - 1, it + 100)
    out["lean_max_next5s"] = round(max(90 - f["pitch"][k] for k in range(it, j + 1)), 1); out["lean_final"] = round(90 - f["pitch"][-1], 1)
    out["tipped_over"] = out["lean_final"] > 60.0
    out["u_max_descent"] = round(max(max(f["u1"][k], f["u2"][k], f["u3"][k], f["u4"][k]) for k in range(i0, it)), 3)
    return out

def takeoff(f, res):
    T = f["t"]; mk = res["marks"]; i0 = idx(T, mk["t_throttle"])
    out = dict(case="takeoff", mass=res["mass"], wind=res["cfg"]["wind"], wfrom=res["cfg"]["wind_from_deg"])
    il = next((i for i in range(i0, len(T)) if f["touch"][i] == 0 and f["alt"][i] > f["alt"][i0] + 0.3), None)
    if il is None: out["liftoff"] = None; return out
    i12 = idx(T, mk["t_12m"])
    out["t_to_liftoff_s"] = round(T[il] - mk["t_throttle"], 1); out["t_to_12m_s"] = round(T[i12] - mk["t_throttle"], 1)
    out["lean_max_deg"] = round(max(90 - f["pitch"][k] for k in range(i0, i12)), 1)
    out["lean_max_first3s_deg"] = round(max(90 - f["pitch"][k] for k in range(il, min(len(T) - 1, il + 60))), 1)
    out["drift_at_12m_m"] = round(math.hypot(f["pn"][i12] - f["pn"][i0], f["pe"][i12] - f["pe"][i0]), 1)
    out["u_max"] = round(max(max(f["u1"][k], f["u2"][k], f["u3"][k], f["u4"][k]) for k in range(i0, i12)), 3)
    out["t_cap_run_s"] = round(runlen([max(f["u1"][k], f["u2"][k], f["u3"][k], f["u4"][k]) >= 0.895 for k in range(i0, i12)]), 2)
    out["sliding_or_tipped_before_liftoff"] = max(90 - f["pitch"][k] for k in range(i0, il)) > 25 if il > i0 else False
    out["heading_change_deg"] = round(((f["hdg_belly"][i12] - f["hdg_belly"][i0] + 180) % 360) - 180, 1)
    return out

def fail(f, res):
    T = f["t"]; mk = res["marks"]; tf = mk["t_fail"]; i0 = idx(T, tf)
    out = dict(case=res["case"], mass=res["mass"], t_fail=round(tf, 1), alt_fail=round(f["alt"][i0], 1))
    after = [e for e in res["modes"] if e[0] >= tf - 0.01]
    out["modes_after"] = after[:8]
    out["events_after"] = [e for e in res["events"] if e[0] >= tf - 0.5][:10]
    it = next((i for i in range(i0, len(T)) if f["touch"][i] > 0), None)
    if it is not None:
        out["t_touch_after_s"] = round(T[it] - tf, 1); out["sink_ms"] = round(-f["vu"][it], 2); out["lean_at_touch"] = round(90 - f["pitch"][it], 1)
        out["speed_at_touch_ms"] = round(math.sqrt(f["vn"][it] ** 2 + f["ve"][it] ** 2 + f["vu"][it] ** 2), 1)
        out["lean_final"] = round(90 - f["pitch"][-1], 1)
    out["alt_min_after"] = round(min(f["alt"][i0:]), 1); out["roll_max_abs_after"] = round(max(abs(x) for x in f["roll"][i0:]), 0)
    ml = [e for e in after if e[1] in ("QLAND", "QRTL", "RTL")]
    out["t_to_mode_s"] = round(ml[0][0] - tf, 2) if ml else None
    out["u_max_after"] = round(max(max(f["u1"][k], f["u2"][k], f["u3"][k], f["u4"][k]) for k in range(i0, len(T))), 3)
    out["V_max_after"] = round(max(f["V"][i0:]), 1); out["pitch_range_after"] = [round(min(f["pitch"][i0:]), 0), round(max(f["pitch"][i0:]), 0)]
    return out

def summarize(tag):
    f, res = load(tag); c = res["case"]
    # vertical speed column is 'vu' (up positive)
    if c == "trans":
        o = trans(f, res)
        if res["marks"].get("t_qland"):
            o["landing"] = landing(f, res, res["marks"]["t_qland"], "chain-landing")
            o["back"] = dict(modes=[e for e in res["modes"] if e[0] >= res["marks"]["t_back"] - 0.1][:6])
            ib = idx(f["t"], res["marks"]["t_back"]); iq = idx(f["t"], res["marks"]["t_qland"])
            o["back"].update(alt_max_after_switch=round(max(f["alt"][ib:iq]), 1), alt_min_after_switch=round(min(f["alt"][ib:iq]), 1), alt_at_switch=round(f["alt"][ib], 1),
                             lean_max_in_descent=round(max(90 - f["pitch"][k] for k in range(idx(f["t"], res["marks"]["t_back"] + 10.0), iq)), 1),
                             u_max=round(max(max(f["u1"][k], f["u2"][k], f["u3"][k], f["u4"][k]) for k in range(ib, iq)), 3))
            if res["marks"].get("t_yaw0"): o["back"]["yaw_turn_deg"] = round(((f["hdg_belly"][iq] - f["hdg_belly"][idx(f["t"], res["marks"]["t_yaw0"])] + 180) % 360) - 180, 0)
            o["back"]["hdg_belly_at_qland"] = round(f["hdg_belly"][iq], 0)
    elif c == "roll":
        o = trans(f, res); mk = res["marks"]; T = f["t"]; ia, ib = idx(T, mk["t_roll0"]), idx(T, mk["t_roll3"])
        pr = [math.degrees(f["p"][i]) for i in range(ia, ib)]; el = [0.5 * abs(f["dl"][i] - f["dr"][i]) for i in range(ia, ib)]
        o["roll"] = dict(p_peak_deg_s=round(max(abs(x) for x in pr), 0), diff_elevon_peak_deg=round(max(el), 1), roll_peak_deg=round(max(abs(f["roll"][i] - 180.0 if abs(f["roll"][i]) > 90 else f["roll"][i]) for i in range(ia, ib)), 0),
                         elevon_max_deg=round(max(max(abs(f["dl"][i]), abs(f["dr"][i])) for i in range(ia, ib)), 1), alt_min=round(min(f["alt"][ia:ib]), 1), V_min=round(min(f["V"][ia:ib]), 1))
    elif c == "wvane":
        T = f["t"]; ia, ib = idx(T, mk_ := res["marks"]["t_wv0"]), idx(T, res["marks"]["t_wv1"])
        h = [f["hdg_belly"][i] for i in range(ia, ib)]
        def unwrap(a):
            out = [a[0]]
            for x in a[1:]: out.append(out[-1] + ((x - out[-1] + 180) % 360) - 180)
            return out
        hu = unwrap(h); n = len(hu); tail = hu[n // 2:]; med = sorted(tail)[len(tail) // 2]
        lean = [90 - f["pitch"][i] for i in range(ia, ib)]
        o = dict(case="wvane", mass=res["mass"], wind=res["cfg"]["wind"], wfrom=res["cfg"]["wind_from_deg"], turb=res["cfg"]["turb"], seed=res["cfg"]["seed"],
                 hdg_start=round(hu[0], 0), hdg_settled_median=round(med, 1), hdg_exc_after_half_deg=round(max(abs(x - med) for x in tail), 1),
                 hdg_exc_peak_to_peak_after_half=round(max(tail) - min(tail), 1), edge_on_err_deg=round(abs(((med - res["cfg"]["wind_from_deg"]) % 180) - 90), 1),
                 hdg_exc_last_third=round(max(abs(x - med) for x in hu[2 * n // 3:]), 1), lean_mean_last_third=round(sum(lean[2 * n // 3:]) / (n - 2 * n // 3), 1), lean_max=round(max(lean), 1))
    elif c == "land": o = landing(f, res, res["marks"]["t_qland"], "land")
    elif c == "takeoff": o = takeoff(f, res)
    else: o = fail(f, res)
    if c in ("battC", "rcC", "moC"):
        o["pre"] = trans(f, res); o["fail"] = fail(f, res)
    o["tag"] = tag
    json.dump(o, open(os.path.join(HERE, "runs", tag, "sum.json"), "w"), indent=1)
    return o

if __name__ == "__main__":
    for t in sys.argv[1:]:
        try: print(json.dumps(summarize(t)))
        except Exception as e: print(json.dumps(dict(tag=t, error=repr(e))))
