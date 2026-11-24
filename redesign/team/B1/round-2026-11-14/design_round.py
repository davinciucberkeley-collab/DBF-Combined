"""B1 design round 2026-11-14 (R-MISSION speed side, R-TRANSITION speed side). Writes only beside this file.

Reuses the team/B1 helpers (performance.py, main guarded) and the input values saved in team/B1/claims.verify.json
(CALC-B1V-CRUISE, -AERO, -TRANSITION: as-designed CD0 0.0580, k 0.1042 = e 0.85 per ASM-B1-E-BASE), evaluated at the
2.6 kg gate. Nothing here edits params or another role's files.
  1. power vs speed 11-22 m/s, base / pessimistic, with the 7 and 10 deg cant cos-loss on thrust (EST)
  2. pack-power loss chain at 16 and 17 m/s and the reconciliation with E2's 406 W (CALC-E2-BUDGET-V17)
  3. best-endurance (min P) and best-range (min P/V) speeds
  4. fin-edge drag and prop options at 17 m/s against E2's pessimistic BATT_LOW time (two capacity counts)
  5. corridor and pitch-over at the gate for B2's forward-CG stall cases (clean, tripped) and the aft case
Run:  python -I redesign/team/B1/round-2026-11-14/design_round.py   (after xf_fin_edges.py)
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1 = HERE.parent
sys.path.insert(0, str(B1.parents[1] / "proofs"))
sys.path.insert(0, str(B1))
import performance as perf  # noqa: E402


def nodes(p):
    return {n["id"]: n for n in json.load(open(p, encoding="utf-8"))["nodes"]}


N = nodes(B1 / "claims.verify.json")
B2 = nodes(B1.parent / "B2/sim/claims.sim.json")
E2 = nodes(B1.parent / "E2/claims.json")
B4 = nodes(B1.parent / "B4/claims.json")
E1 = nodes(B1.parent / "E1/claims.json")
XF = json.load(open(HERE / "xf_fin_edges_results.json", encoding="utf-8"))["cases"]
ci = dict(N["CALC-B1V-CRUISE"]["input_values"])
ai = N["CALC-B1V-AERO"]["input_values"]
ti = dict(N["CALC-B1V-TRANSITION"]["input_values"])
M = ci["m_g"]                                       # 2.6 kg gate (requirements.mtow_gate_kg)
MOT = (ci["kv"], ci["rm"], ci["i0"])
PESS = ci["pess"]
VN = ci["v"]
out = {"_note": "Written by design_round.py (B1, 2026-11-14). Gate mass 2.6 kg. EST where marked in B1.md."}


def point(V, cd0=None, pess=False, cant=0.0, prop_ratio=1.0, detail=False):
    cd0 = ci["cd0"] if cd0 is None else cd0
    c0, k, eta_f = (cd0 * PESS[0], ci["k_pess"], PESS[1]) if pess else (cd0, ci["k"], 1.0)
    W = M * ci["g"]
    cl = 2 * W / (ci["rho"] * V * V * ci["S"])
    drag = 0.5 * ci["rho"] * V * V * ci["S"] * (c0 + k * cl * cl) * ci["trim"]
    thrust = drag / math.cos(math.radians(cant))
    rps, ps, eta = perf.prop_operating_point(ci["tab"], thrust / ci["n"], V, ci["D"], ci["rho"])
    ps /= eta_f
    pm = perf.motor_input_w(ps, rps, MOT)
    p_el = (ci["n"] * ci["kcal"] * pm / ci["esc"] + ci["av"]) * prop_ratio
    r = {"cl": cl, "ld": cl / (c0 + k * cl * cl), "drag_n": drag, "t_prop_n": thrust / ci["n"], "J": V / (rps * ci["D"]),
         "rpm": rps * 60, "eta_prop": eta * eta_f, "p_el_w": p_el}
    if detail:
        r.update({"P_thrust_W": thrust * V, "P_shaft_W": ci["n"] * ps, "P_motor_in_W": ci["n"] * pm,
                  "P_motor_in_cal_W": ci["n"] * pm * ci["kcal"], "P_esc_in_W": ci["n"] * pm * ci["kcal"] / ci["esc"],
                  "eta_motor": ps / pm})
    return r


# 1. sweep
cols = ["V", "CL", "L/D", "drag_N", "T_per_prop_N", "J", "rpm", "eta_prop", "P_W", "P_cant7_W", "P_cant10_W",
        "P_pess_W", "P_pess_cant7_W", "I_A", "I_pess_A", "P_over_V_J_per_m"]
rows = []
for v10 in range(110, 221, 5):
    V = v10 / 10
    b, w = point(V), point(V, pess=True)
    rows.append([V, round(b["cl"], 3), round(b["ld"], 2), round(b["drag_n"], 3), round(b["t_prop_n"], 3),
                 round(b["J"], 3), round(b["rpm"]), round(b["eta_prop"], 3), round(b["p_el_w"], 1),
                 round(point(V, cant=7)["p_el_w"], 1), round(point(V, cant=10)["p_el_w"], 1), round(w["p_el_w"], 1),
                 round(point(V, pess=True, cant=7)["p_el_w"], 1),
                 round(b["p_el_w"] / VN, 2), round(w["p_el_w"] / VN, 2), round(b["p_el_w"] / V, 2)])
out["sweep_cols"], out["sweep"] = cols, rows

# 2. loss chain and reconciliation with E2
e2 = E2["CALC-E2-BUDGET-V17"]
e2i, e2o = e2["input_values"], e2["outputs"]
k_e1 = (E1["CL-E1-CRUISE-P-55-V17"]["value"] + ci["av"]) / point(17, cant=0)["p_el_w"]     # E1 chain / B1 chain at 17
chain = {}
for V in (16.0, 17.0):
    b = point(V, cant=7, detail=True)
    w = point(V, pess=True, cant=7, detail=True)
    b0 = point(V)["p_el_w"]
    w0 = point(V, pess=True)["p_el_w"]
    chain[f"{V:.0f}"] = {"base": b, "pess": w, "base_nocant_W": b0, "pess_nocant_W": w0,
                         "E2_equiv_W": w0 * k_e1 * e2i["aero"]["circuit"]}
out["chain"] = chain
out["reconcile_406"] = {"B1_pess_17_gate_W": point(17, pess=True)["p_el_w"], "k_E1_over_B1_17": k_e1,
                        "circuit": e2i["aero"]["circuit"],
                        "product_W": point(17, pess=True)["p_el_w"] * k_e1 * e2i["aero"]["circuit"],
                        "E2_cruise_w_pess": e2o["cruise_w_pess"],
                        "E2_k": e2o["k"], "B1V_pess_16_pred_W": e2i["pc_p"], "B1V_base_16_gate_W": e2i["pc_b"]}


# 3. best speeds
def argmin(f, lo=10.0, hi=22.0):
    return min(((v / 100, f(v / 100)) for v in range(int(lo * 100), int(hi * 100) + 1)), key=lambda t: t[1])


cd0, k = ci["cd0"], ci["k"]
vmd = math.sqrt(2 * M * ci["g"] / (ci["rho"] * ci["S"])) * (k / cd0) ** 0.25
out["best"] = {
    "aero_v_min_drag_ms": vmd, "aero_v_min_power_ms": vmd / 3 ** 0.25, "ld_max": 0.5 / math.sqrt(cd0 * k),
    "chain_v_min_P_10_22": argmin(lambda V: point(V)["p_el_w"]),
    "chain_v_min_P_over_V_10_22": argmin(lambda V: point(V)["p_el_w"] / V),
    "chain_v_min_P_over_V_pess": argmin(lambda V: point(V, pess=True)["p_el_w"] / V),
    "dP_dV_at_17_W_per_ms": point(17.5)["p_el_w"] - point(16.5)["p_el_w"],
}
# speed at which E2's pessimistic pack power (B1 pess x k_E1 x circuit, 7 deg cant) equals 315 W
f315 = lambda V: point(V, pess=True, cant=7)["p_el_w"] * k_e1 * e2i["aero"]["circuit"] - 315.0
lo, hi = 12.0, 17.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if f315(mid) < 0 else (lo, mid)
out["best"]["v_for_E2_315W_ms"] = lo
f315b = lambda V: point(V, pess=True, cant=7)["p_el_w"] * e2i["aero"]["circuit"] - 315.0
lo, hi = 12.0, 17.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if f315b(mid) < 0 else (lo, mid)
out["best"]["v_for_315W_B1chain_ms"] = lo

# 4. options at 17 m/s against E2's BATT_LOW time; both capacity counts (E2.md: 4.676 min as claimed, 3.61 corrected)
I0 = e2o["cruise_a_pess"]
ah_claimed = I0 * e2o["cruise_to_low_min"] / 60
ah_corr = I0 * 3.61 / 60                              # E2.md table, 'Today, corrected'
xb = {kk: XF[kk][0]["cd"] for kk in XF}               # alpha 0
d_te = xb["blunt_320000"] - xb["bevel55_320000"]
d_le = ai["cd_b"] - xb["blunt_320000"]                # SU2 square board - XFOIL round-LE board (cross-tool, EST)
IF, S, cf, h, tl = ai["drag"][5], ci["S"], ai["fin_c"], ai["fin_h"], ai["tube_l"]
dF1 = IF * 2 * cf * d_te * 2 * h / S
dF2 = dF1 + IF * 2 * cf * d_le * (2 * h - tl) / S
ratio_e = B4["CL-B4-AB-CRUISE-RATIO-E-17"]["value"]
p0 = point(17, pess=True)["p_el_w"]                   # E2's 406 W corresponds to this (no cant in either chain)
opts = {}
for name, c0, pr, cant, V in [("baseline 17 (11x5.5MR, square fin edges, no cant)", cd0, 1.0, 0, 17),
                              ("baseline 17 with 7 deg cant cos-loss", cd0, 1.0, 7, 17),
                              ("cant 10 deg (B3 option)", cd0, 1.0, 10, 17),
                              ("F1 fin TE bevel", cd0 - dF1, 1.0, 7, 17),
                              ("F2 fin TE bevel + round LE above the tube", cd0 - dF2, 1.0, 7, 17),
                              ("P1 11x5.5E/EP (B4 ratio)", cd0, ratio_e, 7, 17),
                              ("P1 + F1", cd0 - dF1, ratio_e, 7, 17),
                              ("P1 + F1 + cant 10", cd0 - dF1, ratio_e, 10, 17),
                              ("16 m/s, 7 deg cant", cd0, 1.0, 7, 16),
                              ("16 m/s, P1 + F1", cd0 - dF1, ratio_e, 7, 16)]:
    w = point(V, c0, True, cant, pr)["p_el_w"]
    b = point(V, c0, False, cant, pr)["p_el_w"]
    i = I0 * w / p0
    opts[name] = {"V": V, "cd0": c0, "P_W": b, "P_pess_W": w, "d_pess_pct": 100 * (w / p0 - 1),
                  "E2_P_pess_W": e2o["cruise_w_pess"] * w / p0, "E2_I_pess_A": i,
                  "E2_to_low_claimed_min": ah_claimed / i * 60, "E2_to_low_corrected_min": ah_corr / i * 60}
out["options"] = {"d_cd_te": d_te, "d_cd_le": d_le, "dCD0_F1": dF1, "dCD0_F2": dF2, "ah_claimed": ah_claimed,
                  "ah_corrected": ah_corr, "rows": opts}
for s in (16.0, 17.0):
    b = point(s)
    out[f"gate_{s:.0f}"] = {"P_W": b["p_el_w"], "drag_N": b["drag_n"], "ld_eff": M * ci["g"] / b["drag_n"],
                            "P_pess_W": point(s, pess=True)["p_el_w"], "drag_pess_N": point(s, pess=True)["drag_n"],
                            "T_per_prop_N": b["t_prop_n"], "J": b["J"], "rpm": b["rpm"]}

# 5. corridor at the gate, B2's CG cases
KC = ("m", "g", "rho", "S", "cla", "a0", "clmax", "cd0", "k", "cd90", "n", "tab", "kv", "rm", "i0", "kcal", "nmax",
      "D", "esc", "av", "frac", "dl", "vc")
KP = ("m", "g", "rho", "S", "cla", "a0", "clmax", "cd0", "k", "cd90", "n", "tab", "kv", "rm", "i0", "kcal", "nmax",
      "D", "esc", "av", "frac", "trans", "vs", "vc", "kt")
corr = {}
for cid in ("CL-B2R3-VS-GATE-FWD", "CL-B2R3-VS-GATE-FWD-TURB", "CL-B2R3-VS-GATE-AFT"):
    vs = B2[cid]["value"]
    clmax = 2 * M * ci["g"] / (ci["rho"] * ci["S"] * vs * vs)
    for vc in (16.0, 17.0, 18.0):
        tv = dict(ti, m=M, clmax=clmax, vc=vc, vs=vs)
        co = perf.corridor(**{kk: tv[kk] for kk in KC})
        po = perf.simulate_pitchover(**{kk: tv[kk] for kk in KP})["summary"]
        rv = [r for r in co["rows_V_th_thlo_TW_Tfrac_P_stalled"] if r[0] == int(vc)]
        corr[f"{cid}@{vc:.0f}"] = {"vs": vs, "clmax": clmax, "vt": 1.3 * vs, "margin_ms": vc - 1.3 * vs,
                                   "margin_pct": 100 * (vc / (1.3 * vs) - 1), "corr_tfrac_max": co["thrust_frac_max"],
                                   "v_wingborne": co["v_wing_unstalled_ms"], "row_at_vc": rv[0] if rv else None,
                                   "po": po}
    corr[f"{cid}_rows"] = perf.corridor(**{kk: dict(ti, m=M, clmax=clmax, vc=17.0, vs=vs)[kk] for kk in KC})[
        "rows_V_th_thlo_TW_Tfrac_P_stalled"]
out["corridor"] = corr
(HERE / "design_round_results.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")

if __name__ == "__main__":
    print(json.dumps({kk: out[kk] for kk in ("best", "gate_16", "gate_17", "reconcile_406")}, indent=1))
    for V, c in chain.items():
        print(V, {kk: round(v, 3) for kk, v in c["base"].items()}, "\n  pess", {kk: round(v, 3) for kk, v in c["pess"].items()},
              "\n  nocant", round(c["base_nocant_W"], 1), round(c["pess_nocant_W"], 1), "E2-equiv", round(c["E2_equiv_W"], 1))
    for kk, v in opts.items():
        print(f"{kk:50s} P {v['P_W']:6.1f} pess {v['P_pess_W']:6.1f} ({v['d_pess_pct']:+5.1f} %) E2W {v['E2_P_pess_W']:5.1f} "
              f"I {v['E2_I_pess_A']:5.2f} to_low {v['E2_to_low_claimed_min']:.2f} / corr {v['E2_to_low_corrected_min']:.2f}")
    print("dCD0 F1 %.5f F2 %.5f d_te %.5f d_le %.5f" % (dF1, dF2, d_te, d_le))
    for kk, v in corr.items():
        if not kk.endswith("_rows"):
            print(kk, "Vt %.2f margin %.2f m/s %.1f%% Tfrac %.3f | po t_vt %.2f t_vc %.2f Tfrac %.3f E %.3f alt %.2f" % (
                v["vt"], v["margin_ms"], v["margin_pct"], v["corr_tfrac_max"], v["po"]["t_to_vt_s"],
                v["po"]["t_to_cruise_s"], v["po"]["thrust_frac_max"], v["po"]["energy_wh"], v["po"]["alt_loss_m"]),
                v["row_at_vc"])
