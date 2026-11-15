"""C5 closure round 2026-11-14: foot capacity against mass, and the honest replace mark.

Run:  python -I redesign/team/C5/cr1114/mass_sweep.py      -> cr1114/out/mass_sweep.json  (thread caps 4)

Physics unchanged: team/C5/sim/landing_sim3d.py simulate() on the live inputs (L.inputs()). Overrides in-script only:
  * mass m (I scaled by m / m_A3, CG unchanged: the added mass is put at the CG, EST);
  * plateau scale k_F on both cartridge types (1.00 nominal; 0.90 = the low end of the "flat within ~10 %" band of
    ASM-D5-CART-PLATEAU, the pessimistic side for stroke; 1.10 = the high side for the load factor);
  * pre-set d0 (a cartridge worn to the replace mark): the piston starts d0 in, so the stroke left to the rim is
    s_av - d0 and the aircraft stands d0 lower. Implemented by s_av -> s_av - d0 and x_g -> x_g - d0 with the CG
    unchanged (the crusher is history-free once yielded: same plateau, same elastic reload ramp).
Cases:
  A. hard landing envelope: sink requirements.landing_sink_ms (1.2), lift ASM-C1-LAND-LIFT, tilt 0-10 deg in 24
     azimuths (landing_sim3d.disc_cases), masses 2.60 ... 2.90 kg, k_F 1.00 and 0.90;
  B. drift: 10 deg boundary attitudes x 8 drift directions, 0.3 m/s, sink 1.2 and 0.5, t_end 1.2 s, 2.65 / 2.70 kg;
  C. normal landing: sink ASM-D5-NORMAL-SINK (0.5), tilt 0 / 2.5 / 5 deg, 24 azimuths. Permanent set per foot in
     D5's convention (CALC-D5-CRUSH, elastic strain ASM-D5-XPS-ELASTIC-STRAIN): set = s_max - eps_y L/4 - eps_e L/2
     (energy on the foot F (s_max - s_y/2) minus the elastic energy F eps_e L/2, over F), which reproduces D5's level
     value; the simulator's own plastic state sp is recorded alongside.
"""
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
import landing_sim3d as L  # noqa: E402

RED = HERE.parents[2]
MASSES = (2.60, 2.65, 2.70, 2.75, 2.80, 2.90)
KF = (1.00, 0.90)


def _node(i):
    for f in RED.glob("team/*/claims*.json"):
        for n in json.loads(f.read_text("utf-8")).get("nodes", []):
            if n["id"] == i:
                return n["value"]
    raise KeyError(i)


def variant(inp, k_F=1.0, d0=0.0):
    v = dict(inp)
    v["F_up"], v["F_lo"] = inp["F_up"] * k_F, inp["F_lo"] * k_F
    v["s_av"] = inp["s_av"] - d0
    v["x_g"] = inp["x_g"] - d0          # worn: the piston already sits d0 in, so the aircraft stands d0 lower
    return v


def main():
    t0 = time.time()
    inp = L.inputs()
    usable = inp["s_av"] - inp["guard"]
    eps_e = _node("ASM-D5-XPS-ELASTIC-STRAIN")
    v_norm = _node("ASM-D5-NORMAL-SINK")
    el_sim = inp["eps_y"] * inp["L_cart"] / 4          # s_y / 2
    el_d5 = eps_e * inp["L_cart"] / 2
    out = {"inputs": {k: inp[k] for k in ("m_a3", "m_pred", "m_gate", "m_light", "F_up", "F_lo", "s_av", "guard",
                                          "L_cart", "eps_y", "lam", "mu", "v_sink", "err", "x_cg", "z_cg", "y_cg")},
           "usable_m": usable, "eps_e": eps_e, "v_normal": v_norm}

    # A. hard envelope vs mass and plateau
    A = {}
    for kF in KF:
        iv = variant(inp, kF)
        cs, tags = [], []
        for m in MASSES:
            c = L.disc_cases(iv, m, m / inp["m_a3"], inp["lam"], inp["v_sink"])
            cs += c
            tags += [m] * len(c)
        r = L.simulate(iv, cs)
        for m in MASSES:
            idx = [i for i, t in enumerate(tags) if t == m]
            sub = {k: [r[k][i] for i in idx] for k in r}
            cc = [cs[i] for i in idx]
            s = L.summarise(cc, sub)
            lvl = [i for i, c in enumerate(cc) if c["theta"] == 0 and c["phi"] == 0][0]
            row = {"stroke_max_m": s["stroke_max_m"], "stroke_level_m": max(sub["s_max"][lvl]),
                   "n_max": s["n_peak_max"], "n_level": sub["n_peak"][lvl], "side_1ms_N": s["side_1ms_max_N"],
                   "tip_min_m": s["tip_min_m"], "tilt_max_deg": s["tilt_max_deg"], "tipped": s["tipped"],
                   "worst_case": {k: s["worst_case"][k] for k in ("theta", "phi")},
                   "margin_new_m": usable - s["stroke_max_m"]}
            A["%.2f/%.2f" % (kF, m)] = row
            print("A kF %.2f m %.2f  stroke %.2f mm (level %.2f)  n %.2f (level %.2f)  side %.1f N  tip %.4f  "
                  "margin %.2f mm  (%.0f s)" % (kF, m, row["stroke_max_m"] * 1e3, row["stroke_level_m"] * 1e3,
                                               row["n_max"], row["n_level"], row["side_1ms_N"], row["tip_min_m"],
                                               row["margin_new_m"] * 1e3, time.time() - t0), flush=True)
    out["hard"] = A

    # A2. load factor at the lightest mass, high plateau (+10 %): the C1 / C3 / C4 side of the band
    nl = {}
    for kF in (1.0, 1.1):
        iv = variant(inp, kF)
        c = L.disc_cases(iv, inp["m_light"], inp["m_light"] / inp["m_a3"], inp["lam"], inp["v_sink"])
        r = L.simulate(iv, c)
        nl["%.2f" % kF] = {"n_max": max(r["n_peak"]), "n_level": r["n_peak"][0], "m": inp["m_light"]}
        print("A2 light kF %.2f n %.3f level %.3f" % (kF, nl["%.2f" % kF]["n_max"], nl["%.2f" % kF]["n_level"]),
              flush=True)
    out["light_n"] = nl

    # B. drift at 2.65 / 2.70, nominal plateau
    e = inp["err"]
    atts = [(e * math.cos(k * math.pi / 4), e * math.sin(k * math.pi / 4)) for k in range(8)]
    dirs = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]
    B = {}
    for m in (2.65, 2.70):
        cs = [dict(m=m, I_scale=m / inp["m_a3"], theta=a, phi=b, v_sink=vs, lam=inp["lam"],
                   drift=(inp["v_td"] * dx, inp["v_td"] * dy)) for vs in (inp["v_sink"], inp["v_normal"])
              for (a, b) in atts for (dx, dy) in dirs]
        r = L.simulate(inp, cs, t_end=1.2)
        s = L.summarise(cs, r)
        B["%.2f" % m] = {"stroke_max_m": s["stroke_max_m"], "side_1ms_N": s["side_1ms_max_N"], "tipped": s["tipped"],
                         "tilt_max_deg": s["tilt_max_deg"], "n_max": s["n_peak_max"]}
        print("B drift m %.2f  stroke %.2f mm  side %.1f N  tipped %d  tilt %.1f  (%.0f s)" % (
            m, s["stroke_max_m"] * 1e3, s["side_1ms_max_N"], s["tipped"], s["tilt_max_deg"], time.time() - t0),
            flush=True)
    out["drift"] = B

    # C. normal landings: set per foot
    C = {}
    for m in (inp["m_a3"], 2.60, 2.65, 2.70):
        cs = L.disc_cases(inp, m, m / inp["m_a3"], inp["lam"], v_norm, mags=(0.0, 2.5, 5.0))
        r = L.simulate(inp, cs)
        rows = {}
        for mag in (0.0, 2.5, 5.0):
            idx = [i for i, c in enumerate(cs) if abs(math.hypot(c["theta"], c["phi"]) - mag) < 1e-6]
            smax = max(max(r["s_max"][i]) for i in idx)
            set_d5 = max(0.0, smax - el_sim - el_d5)
            sp = max(max(r["sp_end"][i]) for i in idx)
            # mean set per foot over the four feet, worst azimuth (what the stack loses on average)
            mean = max(sum(max(0.0, x - el_sim - el_d5) for x in r["s_max"][i]) / 4 for i in idx)
            rows["%.1f" % mag] = {"stroke_max_m": smax, "set_worst_foot_m": set_d5, "set_mean_m": mean,
                                  "sp_sim_m": sp}
        C["%.4f" % m] = rows
        print("C normal m %.3f  %s  (%.0f s)" % (m, {k: round(v["set_worst_foot_m"] * 1e3, 3) for k, v in rows.items()},
                                                 time.time() - t0), flush=True)
    out["normal"] = C

    # D. worn cartridge check: hard envelope with the cartridge pre-set to a candidate mark, pessimistic plateau
    D = {}
    for d0 in (0.0, 0.003, 0.006, 0.007):
        iv = variant(inp, 0.90, d0)
        cs, tags = [], []
        for m in (2.60, 2.65, 2.70):
            c = L.disc_cases(iv, m, m / inp["m_a3"], inp["lam"], inp["v_sink"])
            cs += c
            tags += [m] * len(c)
        r = L.simulate(iv, cs)
        for m in (2.60, 2.65, 2.70):
            idx = [i for i, t in enumerate(tags) if t == m]
            smax = max(max(r["s_max"][i]) for i in idx)
            D["%.3f/%.2f" % (d0, m)] = {"stroke_from_mark_m": smax, "left_m": (inp["s_av"] - d0 - inp["guard"]) - smax,
                                        "side_1ms_N": max(max(r["side_1ms"][i]) for i in idx),
                                        "tip_min_m": min(r["tip_min"][i] for i in idx),
                                        "strike_tilt_deg": min([math.hypot(cs[i]["theta"], cs[i]["phi"]) for i in idx
                                                                if r["tip_min"][i] < 0] or [99.0])}
            print("D mark %.1f mm  m %.2f  stroke from mark %.2f mm  left beyond guard %.2f mm  strike %.1f deg" % (
                d0 * 1e3, m, smax * 1e3, D["%.3f/%.2f" % (d0, m)]["left_m"] * 1e3,
                D["%.3f/%.2f" % (d0, m)]["strike_tilt_deg"]), flush=True)
    out["worn"] = D
    out["runtime_s"] = time.time() - t0
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "mass_sweep.json").write_text(json.dumps(out, indent=1))
    print("wrote mass_sweep.json in %.0f s" % out["runtime_s"])


if __name__ == "__main__":
    main()
