"""E2 cost re-check 2026-11-14 (D-180): ONE flight pack = CNHL LiHV 4S 6000 120C hard case EC5 (479 +/- 5 g listed).
Imports energy_claims.py (reads params.json, writes nothing) and runs the mission, BATT_LOW, heat and sag checks at the
gate mass with B1's closure_final cruise level (198.3 W incl. avionics and turbulator; pessimistic 272.6 W).
Run: python -I redesign/team/E2/cost_recheck_2026-11-14.py"""
import importlib.util, json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ec", HERE / "energy_claims.py")
ec = importlib.util.module_from_spec(spec); spec.loader.exec_module(ec)
kit = ec.kit
kit._run("CALC-E2-BUDGET-V17")
iv = kit.nodes["CALC-E2-BUDGET-V17"]["input_values"]
kw = {k: v for k, v in iv.items() if k not in ("m_b", "m_p", "p17", "turb")}
m_p = iv["m_p"]
B1 = json.load(open(HERE.parents[0] / "B1" / "round-2026-11-14" / "closure_final_results.json"))
P_BASE = B1["cruise"]["turbulator"]["P_W"]; P_PESS = B1["cruise"]["turbulator"]["P_pess_W"]
print(f"gate {m_p} kg; B1 closure_final level {P_BASE:.1f} W base, {P_PESS:.1f} W pess (incl. avionics + turbulator)")

def run(label, ah, kg_listed, tol_kg, p_base=P_BASE, p_pess=P_PESS, r_cell=None, r_ext=None, pack_m=None):
    k2 = dict(kw, ah=ah)
    if r_cell is not None: k2["r_cell"] = r_cell
    if r_ext is not None: k2["r_ext"] = r_ext
    # level power carried = B1 level x circuit 1.05 (E2 convention); budget() is linear in p_scale
    def at(pess, target_w):
        pcw = ec.budget(m_p, pess, p_scale=1.0, **k2)["cruise_w"]
        return ec.budget(m_p, pess, p_scale=target_w * ec.kit.nodes["CALC-E2-BUDGET-V17"]["input_values"]["aero"]["circuit"] / pcw, **k2)
    pess = at(True, p_pess); base = at(False, p_base)
    # force cruise power to the B1 level x circuit
    fs = ec.failsafe_rows(pess["phases"], ah, k2["reserve"], k2["cap_frac"], k2["prof"]["landing_hover_s"], k2["goaround"])
    ht = ec.heat(pess["phases"], k2["r_cell"], k2["cells"], k2["cold"], pack_m or (kg_listed + 0.004), kw_amb)
    return dict(label=label, cruise_w_base=round(base["cruise_w"], 1), cruise_w_pess=round(pess["cruise_w"], 1),
                cruise_a_pess=round(pess["cruise_a"], 2), hover_a_pess=round(pess["hover_a"], 1),
                imax_phase=round(pess["i_max_phase_a"], 1), low_mah=fs["low_mah"], crt_mah=fs["crt_mah"],
                to_low_min=round(fs["cruise_to_low_min"], 2), land_left_mah=round(fs["land_left_mah"]),
                t_end_cold=round(ht["t_end_cold_c"], 1), t_end_hot=round(ht["t_end_hot_c"], 1),
                mass_worst_g=round((kg_listed + tol_kg) * 1000, 1))
kit._run("CALC-E2-HEAT"); kw_amb = kit.nodes["CALC-E2-HEAT"]["input_values"]["amb"]
accept = kit.nodes["CL-A3-PACK-ACCEPT"]["value"] if "CL-A3-PACK-ACCEPT" in kit.nodes and "value" in kit.nodes["CL-A3-PACK-ACCEPT"] else None
print("pack accept line (A3 node):", accept)
print("ref Gens Ace 414 g:", json.dumps(run("Gens Ace Shorty", 6.0, 0.410, 0.010, pack_m=0.414)))
print("CNHL Shorty 130C (415.5 g + 4 g pigtails, tol 10 g EST), B1 198.3 W:", json.dumps(run("CNHL Shorty", 6.0, 0.4195, 0.010, pack_m=0.4195)))
print("CNHL 6000 EC5, B1 198.3 W:", json.dumps(run("CNHL 6000", 6.0, 0.479, 0.005)))
print("CNHL with E2 old level 219 W (params 205 + 14, conservative):", json.dumps(run("CNHL 6000 @219", 6.0, 0.479, 0.005, p_base=219, p_pess=219*272.6/198.3)))
print("CNHL, IR 20 % worse (4.56 mOhm/group):", json.dumps(run("CNHL IR+20%", 6.0, 0.479, 0.005, r_cell=ec.kit.nodes["CALC-E2-BUDGET-V17"]["input_values"]["r_cell"]*1.2)))
print("CNHL, r_ext +1.5 mOhm (12 AWG leads, F1 to confirm):", json.dumps(run("CNHL 12AWG", 6.0, 0.479, 0.005, r_ext=kw["r_ext"] + 1.5)))
print("params r_ext", kw["r_ext"], "r_cell", kw["r_cell"], "cold", kw["cold"], "cap_frac", kw["cap_frac"])
