"""C5 closure round 2026-11-14: check of the proposed foot ("design B") against every C5 3-D landing case.

Run:  python -I redesign/team/C5/cr1114/design_b.py      -> cr1114/out/design_b.json  (thread caps 4)

Design B (C5 proposal to D5; D5 owns the geometry): stroke_max 38 -> 43 mm, piston engagement 25 -> 30 mm, so
L_cart = 2 stroke + engage + 1 mm (CALC-D5-GEOM) = 102 -> 117 mm and the sleeve +10 mm; foot height 48 -> 53 mm
(TE 10 mm off the ground at full stroke, D-30 rule kept); replace mark 3 -> 6 mm. Plateau, section, pad, mu unchanged.
Physics unchanged (landing_sim3d.simulate); overrides: s_av + 5 mm, x_g + 5 mm (CG height + 5 mm), L_cart + 15 mm,
mass and inertia as stated per case; the +EST 6 g of the longer feet is added to every mass.
Cases at k_F 0.90 (low plateau) and 1.00:
  hard envelope (1.2 m/s, 10 deg any direction) from a cartridge worn to the mark (stance d0 lower, s_av - d0) with
  d0 = mark + one level normal set, at 2.60 / 2.65 / 2.70 kg and the lightest mass (n);
  normal 0.5 m/s set, level and 2.5 deg; drift (0.3 m/s, 10 deg) at 2.70; wind heading cases 0 / 150 / 180 / 210 at
  A3 basic.
"""
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE))
import landing_sim3d as L  # noqa: E402
from mass_sweep import _node  # noqa: E402

DS, DE, MARK = 0.005, 0.005, 0.006
DM = 0.0062           # kg, EST: 4 feet x (sleeve 0.095 + tine 0.053 g/mm) x 10 mm + cartridge 0.0045 g/mm x 15 mm x 4


def variant(inp, k_F=1.0, d0=0.0):
    v = dict(inp)
    v["F_up"], v["F_lo"] = inp["F_up"] * k_F, inp["F_lo"] * k_F
    v["L_cart"] = inp["L_cart"] + 2 * DS + DE
    v["s_av"] = inp["s_av"] + DS - d0
    v["x_g"] = inp["x_g"] + DS - d0
    return v


def main():
    t0 = time.time()
    inp = L.inputs()
    eps_e = _node("ASM-D5-XPS-ELASTIC-STRAIN")
    v_n = _node("ASM-D5-NORMAL-SINK")
    out = {"dS": DS, "dE": DE, "mark": MARK, "dm": DM, "m_a3": inp["m_a3"], "rows": {}}
    masses = (2.60, 2.65, 2.70)
    for kF in (0.90, 1.00):
        iv = variant(inp, kF)
        el = iv["eps_y"] * iv["L_cart"] / 4 + eps_e * iv["L_cart"] / 2
        usable0 = iv["s_av"] - iv["guard"]
        # normal set
        cs, tag = [], []
        for m in masses:
            c = L.disc_cases(iv, m + DM, (m + DM) / inp["m_a3"], inp["lam"], v_n, mags=(0.0, 2.5))
            cs += c
            tag += [(m, round(math.hypot(x["theta"], x["phi"]), 3)) for x in c]
        r = L.simulate(iv, cs)
        sets = {m: {a: max(0.0, max(max(r["s_max"][i]) for i, t in enumerate(tag) if t == (m, a)) - el)
                    for a in (0.0, 2.5)} for m in masses}
        for m in masses:
            d0 = MARK + sets[m][0.0]
            ivw = variant(inp, kF, d0)
            c = L.disc_cases(ivw, m + DM, (m + DM) / inp["m_a3"], inp["lam"], inp["v_sink"])
            rh = L.simulate(ivw, c)
            hard = max(max(x) for x in rh["s_max"])
            strike = min([math.hypot(x["theta"], x["phi"]) for x, tm in zip(c, rh["tip_min"]) if tm < 0] or [99.0])
            row = {"set_level_m": sets[m][0.0], "set_2p5_m": sets[m][2.5], "d0_m": d0, "hard_from_worn_m": hard,
                   "left_beyond_guard_m": (ivw["s_av"] - ivw["guard"]) - hard, "left_to_rim_m": ivw["s_av"] - hard,
                   "landings": MARK / sets[m][0.0], "landings_2p5": MARK / sets[m][2.5],
                   "left_after_2p5_m": (usable0 - MARK - sets[m][2.5]) - hard,
                   "n_max": max(rh["n_peak"]), "side_1ms_N": max(max(x) for x in rh["side_1ms"]),
                   "strike_tilt_worn_deg": strike}
            # fresh cartridge for the strike / stroke of record
            c2 = L.disc_cases(iv, m + DM, (m + DM) / inp["m_a3"], inp["lam"], inp["v_sink"])
            rf = L.simulate(iv, c2)
            row["hard_fresh_m"] = max(max(x) for x in rf["s_max"])
            row["margin_fresh_m"] = usable0 - row["hard_fresh_m"]
            row["strike_tilt_fresh_deg"] = min([math.hypot(x["theta"], x["phi"]) for x, tm in
                                                zip(c2, rf["tip_min"]) if tm < 0] or [99.0])
            out["rows"]["%.2f/%.2f" % (kF, m)] = row
            print("kF %.2f m %.2f  set %.2f / %.2f mm  landings %.2f  hard(worn) %.2f  left>guard %.2f  "
                  "after 2.5deg TD %.2f  fresh %.2f (margin %.2f)  n %.2f  side %.1f  strike worn/fresh %.1f/%.1f  "
                  "(%.0f s)" % (kF, m, sets[m][0.0] * 1e3, sets[m][2.5] * 1e3, row["landings"], hard * 1e3,
                                row["left_beyond_guard_m"] * 1e3, row["left_after_2p5_m"] * 1e3,
                                row["hard_fresh_m"] * 1e3, row["margin_fresh_m"] * 1e3, row["n_max"],
                                row["side_1ms_N"], strike, row["strike_tilt_fresh_deg"], time.time() - t0), flush=True)
    # load factor, lightest mass, fresh, nominal and +10 % plateau
    for kF in (1.0, 1.1):
        iv = variant(inp, kF)
        ml = inp["m_light"] + DM
        c = L.disc_cases(iv, ml, ml / inp["m_a3"], inp["lam"], inp["v_sink"])
        r = L.simulate(iv, c)
        out["n_light_%.2f" % kF] = {"n_max": max(r["n_peak"]), "n_level": r["n_peak"][0], "m": ml}
        print("light kF %.2f n %.3f level %.3f" % (kF, max(r["n_peak"]), r["n_peak"][0]), flush=True)
    # drift at 2.70, low plateau, fresh
    e = inp["err"]
    iv = variant(inp, 0.90)
    atts = [(e * math.cos(k * math.pi / 4), e * math.sin(k * math.pi / 4)) for k in range(8)]
    dirs = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]
    m = 2.70 + DM
    cs = [dict(m=m, I_scale=m / inp["m_a3"], theta=a, phi=b, v_sink=vs, lam=inp["lam"],
               drift=(inp["v_td"] * dx, inp["v_td"] * dy)) for vs in (inp["v_sink"], inp["v_normal"])
          for (a, b) in atts for (dx, dy) in dirs]
    r = L.simulate(iv, cs, t_end=1.2)
    s = L.summarise(cs, r)
    out["drift_270_kF090"] = {"stroke_max_m": s["stroke_max_m"], "usable_m": iv["s_av"] - iv["guard"],
                              "tipped": s["tipped"], "side_1ms_N": s["side_1ms_max_N"]}
    print("drift 2.70 kF0.9 stroke %.2f / usable %.1f  tipped %d side %.1f" % (
        s["stroke_max_m"] * 1e3, (iv["s_av"] - iv["guard"]) * 1e3, s["tipped"], s["side_1ms_max_N"]), flush=True)
    # wind, A3 basic + DM, nominal plateau, fresh
    iv = variant(inp, 1.0)
    W = {}
    for az in (0.0, 150.0, 180.0, 210.0):
        cs, keys = L.heading_cases(iv, inp["m_a3"] + DM, L.HEADING_V, az)
        r = L.simulate(iv, cs, t_end=2.0)
        tab = {}
        for i, (k, V, tilt) in enumerate(keys):
            tab.setdefault(k, []).append((V, bool(r["tipped"][i])))
        lim = {}
        for k, rows in tab.items():
            first = next((j for j, x in enumerate(rows) if x[1]), None)
            lim[k] = rows[-1][0] if first is None else (rows[first - 1][0] if first > 0 else 0.0)
        W["%.0f" % az] = {"lull": min(v for k, v in lim.items() if k.startswith("lull")), "all": min(lim.values())}
    out["wind"] = W
    print("wind", W, flush=True)
    out["runtime_s"] = time.time() - t0
    (HERE / "out" / "design_b.json").write_text(json.dumps(out, indent=1))
    print("wrote design_b.json in %.0f s" % out["runtime_s"])


if __name__ == "__main__":
    main()
