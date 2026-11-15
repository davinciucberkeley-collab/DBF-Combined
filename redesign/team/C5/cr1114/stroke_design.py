"""C5 closure round 2026-11-14: foot stroke sizing for an honest replace mark at gate masses 2.60-2.70 kg.

Run:  python -I redesign/team/C5/cr1114/stroke_design.py    -> cr1114/out/stroke_design.json  (thread caps 4)

Physics unchanged (team/C5/sim/landing_sim3d.py simulate(), live inputs). In-script overrides only:
  * stroke growth dS (D5 CALC-D5-GEOM: L_cart = 2 stroke + engage + 1 mm, so L_cart grows 2 dS; the foot height grows
    dS to keep the 10 mm TE clearance at full stroke): s_av + dS, x_g + dS (CG height + dS), L_cart + 2 dS;
  * plateau scale k_F (0.90 = the low end of ASM-D5-CART-PLATEAU's "flat within ~10 %": more stroke, more set);
  * mass m (I scaled with m, CG unchanged, EST).
Per (dS, m):
  hard   = worst stroke, 1.2 m/s, 10 deg any direction (disc_cases), k_F 0.90, from a fresh cartridge (a worn start
           gives 0.3-0.7 mm less, mass_sweep.json D, so fresh is the conservative side);
  set_n  = worst-foot permanent set of one normal touchdown (ASM-D5-NORMAL-SINK 0.5 m/s), D5's convention
           (set = s_max - eps_y L/4 - eps_e L/2), tilt 0 (level, D5's basis) and 2.5 deg (24 azimuths), k_F 0.90;
  sortie rule (closure): inspection only between sorties, 2 touchdowns per sortie (ASM-C5-TD-PER-SORTIE). A foot just
           short of its mark starts a sortie; one normal touchdown, then the hard landing, must fit:
           mark_max = (s_av - guard) - set_n - hard ;  landings per cartridge = mark / set_n (>= 2).
Also: wind tip-over at the belly heading (az 150 / 180 / 210, A3 basic mass) for the chosen dS, since the CG rises.
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

DS = (0.0, 0.005, 0.010, 0.015)
MASSES = (2.60, 2.65, 2.70)


def variant(inp, dS=0.0, k_F=1.0):
    v = dict(inp)
    v["F_up"], v["F_lo"] = inp["F_up"] * k_F, inp["F_lo"] * k_F
    v["s_av"] = inp["s_av"] + dS
    v["x_g"] = inp["x_g"] + dS
    v["L_cart"] = inp["L_cart"] + 2 * dS
    return v


def main():
    t0 = time.time()
    inp = L.inputs()
    eps_e = _node("ASM-D5-XPS-ELASTIC-STRAIN")
    v_n = _node("ASM-D5-NORMAL-SINK")
    out = {"m_a3": inp["m_a3"], "s_av": inp["s_av"], "guard": inp["guard"], "L_cart": inp["L_cart"], "rows": {}}
    for dS in DS:
        for kF in (0.90, 1.00):
            iv = variant(inp, dS, kF)
            el = iv["eps_y"] * iv["L_cart"] / 4 + eps_e * iv["L_cart"] / 2
            cs, tag = [], []
            for m in MASSES:
                c = L.disc_cases(iv, m, m / inp["m_a3"], inp["lam"], inp["v_sink"])
                cs += c
                tag += [("hard", m, None, None)] * len(c)
                for vs in (v_n, 0.3):
                    c = L.disc_cases(iv, m, m / inp["m_a3"], inp["lam"], vs, mags=(0.0, 2.5))
                    cs += c
                    tag += [("normal", m, vs, round(math.hypot(x["theta"], x["phi"]), 3)) for x in c]
            r = L.simulate(iv, cs)
            usable = iv["s_av"] - iv["guard"]
            for m in MASSES:
                hard = max(max(r["s_max"][i]) for i, t in enumerate(tag) if t[0] == "hard" and t[1] == m)
                strike = min([math.hypot(cs[i]["theta"], cs[i]["phi"]) for i, t in enumerate(tag)
                              if t[0] == "hard" and t[1] == m and r["tip_min"][i] < 0] or [99.0])
                setn = {}
                for vs in (v_n, 0.3):
                    for a in (0.0, 2.5):
                        sm = max(max(r["s_max"][i]) for i, t in enumerate(tag)
                                 if t[0] == "normal" and t[1] == m and t[2] == vs and t[3] == a)
                        setn["%.1f/%.1f" % (vs, a)] = max(0.0, sm - el)
                row = {"usable_m": usable, "hard_m": hard, "strike_tilt_deg": strike, "set_m": setn}
                for a in (0.0, 2.5):
                    s1 = setn["%.1f/%.1f" % (v_n, a)]
                    mk = usable - s1 - hard
                    row["mark_max_%.1f_m" % a] = mk
                    row["landings_%.1f" % a] = mk / s1 if s1 > 0 else float("inf")
                out["rows"]["%.3f/%.2f/%.2f" % (dS, kF, m)] = row
                print("dS %2.0f mm kF %.2f m %.2f  hard %.2f  usable %.1f  set0 %.2f set2.5 %.2f (0.3: %.2f/%.2f)  "
                      "mark_max %.2f/%.2f  landings %.2f/%.2f  strike %.1f  (%.0f s)" % (
                          dS * 1e3, kF, m, hard * 1e3, usable * 1e3, setn["%.1f/0.0" % v_n] * 1e3,
                          setn["%.1f/2.5" % v_n] * 1e3, setn["0.3/0.0"] * 1e3, setn["0.3/2.5"] * 1e3,
                          row["mark_max_0.0_m"] * 1e3, row["mark_max_2.5_m"] * 1e3, row["landings_0.0"],
                          row["landings_2.5"], strike, time.time() - t0), flush=True)
    # belly-heading wind tip-over with the taller foot (A3 basic mass, nominal plateau)
    W = {}
    for dS in (0.0, 0.010, 0.015):
        iv = variant(inp, dS, 1.0)
        res = {}
        for az in (150.0, 180.0, 210.0, 0.0):
            cs, keys = L.heading_cases(iv, inp["m_a3"], L.HEADING_V, az)
            r = L.simulate(iv, cs, t_end=2.0)
            tab = {}
            for i, (k, V, tilt) in enumerate(keys):
                tab.setdefault(k, []).append((V, bool(r["tipped"][i])))
            lim = {}
            for k, rows in tab.items():
                first = next((j for j, x in enumerate(rows) if x[1]), None)
                lim[k] = rows[-1][0] if first is None else (rows[first - 1][0] if first > 0 else 0.0)
            res["%.0f" % az] = {"lull": min(v for k, v in lim.items() if k.startswith("lull")), "all": min(lim.values())}
        W["%.3f" % dS] = res
        print("wind dS %2.0f mm: %s  (%.0f s)" % (dS * 1e3, res, time.time() - t0), flush=True)
    out["wind"] = W
    out["runtime_s"] = time.time() - t0
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "stroke_design.json").write_text(json.dumps(out, indent=1))
    print("wrote stroke_design.json in %.0f s" % out["runtime_s"])


if __name__ == "__main__":
    main()
