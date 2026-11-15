"""C5 closure round 2026-11-14: cartridge life and the honest replace mark on the LIVE foot (3-D sim record).

Run after landing_sim3d.py:  python -I redesign/team/C5/cr1114/cart_life.py   -> cr1114/out/cart_life.json (~1 min)
landing_sim_claims.py turns it into CL-C5-LANDINGS-PER-CARTRIDGE and CL-C5-MARK-HONEST-MARGIN.

Model (physics unchanged, landing_sim3d.simulate on L.inputs(); plateau k_F 0.90 = low end of ASM-D5-CART-PLATEAU's
~10 % band, the pessimistic side for both set and stroke; 1.00 kept for information):
  set_n  = worst-foot permanent set of one level normal touchdown (ASM-D5-NORMAL-SINK 0.5 m/s, lift ASM-C1-LAND-LIFT),
           D5's convention (CALC-D5-CRUSH): set = s_max - eps_y L/4 - eps_e L/2. The 3-D value is larger than D5's
           symmetric hand value because the CG sits toward the upper (pod-side) pair and the weight term is included;
  hard   = worst stroke of the 1.2 m/s / 10 deg envelope from a cartridge worn to mark + set_n (stance that much lower,
           stroke to the rim that much shorter);
  sortie rule: feet are inspected only between sorties (ASM-C5-TD-PER-SORTIE touchdowns per sortie). A foot just short
           of its mark starts a sortie, takes one normal touchdown, then the hard landing:
           honest margin = (s_av - guard) - mark - set_n - hard >= 0 ; landings per cartridge = mark / set_n.
Masses: the gate (requirements.mtow_gate_kg) and 2.65 / 2.70 kg for information. +2.5 deg normal touchdown kept as a
sensitivity row.
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

RED = HERE.parents[2]


def main():
    t0 = time.time()
    inp = L.inputs()
    Lp = json.loads((RED / "subsystems" / "landing" / "params.json").read_text("utf-8"))
    mark = L._param(Lp, "landing.piston.replace_mark_m")
    eps_e = _node("ASM-D5-XPS-ELASTIC-STRAIN")
    v_n = _node("ASM-D5-NORMAL-SINK")
    el = inp["eps_y"] * inp["L_cart"] / 4 + eps_e * inp["L_cart"] / 2
    usable = inp["s_av"] - inp["guard"]
    snap = {"m_gate": inp["m_gate"], "mark": mark, "s_av": inp["s_av"], "L_cart": inp["L_cart"], "F_up": inp["F_up"],
            "F_lo": inp["F_lo"], "m_a3": inp["m_a3"], "z_cg": inp["z_cg"], "x_cg_h": inp["x_g"] - inp["x_cg"]}
    out = {"snapshot": snap, "usable_m": usable, "rows": {}}
    for kF in (0.90, 1.00):
        iv = dict(inp, F_up=inp["F_up"] * kF, F_lo=inp["F_lo"] * kF)
        for m in (inp["m_gate"], 2.65, 2.70):
            c = L.disc_cases(iv, m, m / inp["m_a3"], inp["lam"], v_n, mags=(0.0, 2.5))
            r = L.simulate(iv, c)
            s0 = max(r["s_max"][0])
            s25 = max(max(x) for x in r["s_max"][1:])
            set0, set25 = max(0.0, s0 - el), max(0.0, s25 - el)
            d0 = mark + set0
            ivw = dict(iv, s_av=inp["s_av"] - d0, x_g=inp["x_g"] - d0)
            ch = L.disc_cases(ivw, m, m / inp["m_a3"], inp["lam"], inp["v_sink"])
            rh = L.simulate(ivw, ch)
            hard = max(max(x) for x in rh["s_max"])
            row = {"m": m, "set_level_m": set0, "set_2p5_m": set25, "hard_worn_m": hard,
                   "landings": mark / set0 if set0 > 0 else float("inf"),
                   "honest_margin_m": usable - mark - set0 - hard,
                   "honest_margin_after_2p5_m": usable - mark - set25 - hard,
                   "mark_max_m": usable - set0 - hard}
            out["rows"]["%.2f/%.3f" % (kF, m)] = row
            print("kF %.2f m %.3f  set %.2f (2.5deg %.2f) mm  hard from worn %.2f mm  landings %.2f  honest margin "
                  "%.2f mm  mark_max %.2f mm  (%.0f s)" % (kF, m, set0 * 1e3, set25 * 1e3, hard * 1e3, row["landings"],
                                                         row["honest_margin_m"] * 1e3, row["mark_max_m"] * 1e3,
                                                         time.time() - t0), flush=True)
    out["runtime_s"] = time.time() - t0
    (HERE / "out" / "cart_life.json").write_text(json.dumps(out, indent=1))
    print("wrote cart_life.json in %.0f s" % out["runtime_s"])


if __name__ == "__main__":
    main()
