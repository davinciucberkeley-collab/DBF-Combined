"""E2 design round 2026-11-14 (wave 1): CL-E2-CRUISE-TO-LOW-PESS-V17 levers with in-script overrides.
Imports energy_claims.py and calls its budget(); writes nothing (no kit.write). Run: python -I redesign/team/E2/levers_2026-11-14.py"""
import importlib.util, math, sys, json
SRC = r"C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\team\E2\energy_claims.py"
spec = importlib.util.spec_from_file_location("ec", SRC); ec = importlib.util.module_from_spec(spec); spec.loader.exec_module(ec)
kit = ec.kit
out = kit._run("CALC-E2-BUDGET-V17"); iv = kit.nodes["CALC-E2-BUDGET-V17"]["input_values"]
print("repo V17:", {k: round(out[k], 4) for k in ("k","cruise_w_pess","cruise_a_pess","low_mah","cruise_to_low_min","cruise_min_pess")})
kw = {k: v for k, v in iv.items() if k not in ("m_b", "m_p", "p17")}
m_p, p17 = iv["m_p"], iv["p17"]

def run(label, cruise_x=1.0, hover_x=1.0, ah=None, cap_frac=None, counter="nameplate", reserve_basis="nameplate",
        round_to=100, ret_s=60, land_hover_s=30, p17_override=None, quiet=False):
    k2 = dict(kw)
    if ah is not None: k2["ah"] = ah
    if cap_frac is not None: k2["cap_frac"] = cap_frac
    A = k2["ah"]; cf = k2["cap_frac"]; res = k2["reserve"]
    pp = p17 if p17_override is None else p17_override
    k = (pp + k2["avn"]) / k2["pc_b"] * cruise_x
    # hover factor: scale the table power via hmargin (pessimistic multiplier on hover)
    k2["hmargin"] = k2["hmargin"] * hover_x
    pess = ec.budget(m_p, True, p_scale=k, **k2)
    rows = {r[0]: r for r in pess["phases"]}
    I = rows["cruise"][3]
    need = rows["back-transition"][4] + rows["descent 50-0 m"][4] + I * ret_s / 3600 + rows["hover (mission)"][3] * land_hover_s / 3600
    c_true = A * cf
    base_cnt = A if counter == "nameplate" else c_true            # BATT_CAPACITY setting
    r_ah = A * res if reserve_basis == "nameplate" else c_true * res
    low = math.ceil((r_ah + need) * 1000 / round_to) * round_to / 1000
    before = sum(rows[x][4] for x in ("ground, armed checks", "climb 0-50 m", "hover (mission)", "transition forward"))
    trig_consumed = base_cnt - low
    to_low = (trig_consumed - before) / I * 60
    # true charge left after the landing following a BATT_LOW at the far point
    left_true = c_true - trig_consumed - need
    to20 = (c_true - A * res - pess["ah_fixed"]) / I * 60
    r = dict(label=label, P_cruise_W=round(pess["cruise_w"], 1), I_cruise_A=round(I, 2), need_mAh=round(need*1000),
             LOW_mAh=round(low*1000), before_mAh=round(before*1000), to_low_min=round(to_low, 3),
             to_20pct_min=round(to20, 3), left_after_land_mAh=round(left_true*1000),
             left_pct_nameplate=round(100*left_true/A, 1))
    if not quiet: print(json.dumps(r))
    return r

print("\n# A. reproduce and the BATT_LOW direction")
run("A0 repo model (counter = nameplate 6500, LOW ceil 100)")

r = run("A0", quiet=True)
I = r["I_cruise_A"]; print("A1 with LOW 2600 instead of 2700: to_low =", round(r["to_low_min"] + 0.1 / I * 60, 3), "min (need not covered)")
run("A2 LOW rounded up to 10 mAh, not 100", round_to=10)
print("\n# B. counter base = the pessimistic pack (BATT_CAPACITY = measured, ENERGY.md s4)")
run("B0 BATT_CAPACITY = 0.92 x 6500 = 5980", counter="true")
run("B1 as B0, reserve = 20 % of usable (R-MISSION how-text 0.8 x usable)", counter="true", reserve_basis="usable")
print("\n# C. props (B4 ratios, 17 m/s): 11x5.5E/EP cruise x0.909 hover x1.003 ; 11x7E x0.767 / x1.060")
for cnt in ("nameplate", "true"):
    run(f"C1 11x5.5E counter={cnt}", cruise_x=0.909, hover_x=1.003, counter=cnt)
    run(f"C2 11x7E (no EP pair) counter={cnt}", cruise_x=0.767, hover_x=1.060, counter=cnt)
print("\n# D. pack capacity (same model, cruise/hover at the gate mass)")
for ah in (6.5, 6.75, 7.0, 7.2, 7.5, 8.0, 9.0):
    run(f"D 4S {ah} Ah, counter=true", ah=ah, counter="true")
print("\n# E. acceptance floor tightened (capacity_min_frac)")
for cf in (0.92, 0.95, 0.97, 1.00):
    run(f"E floor {cf}, counter=true", cap_frac=cf, counter="true")
print("\n# F. combos")
for cf in (0.92, 0.95, 0.97):
    run(f"F 11x5.5E + floor {cf}", cruise_x=0.909, hover_x=1.003, cap_frac=cf, counter="true")
    run(f"F 11x7E + floor {cf}", cruise_x=0.767, hover_x=1.060, cap_frac=cf, counter="true")
for ah in (7.0, 7.5, 8.0):
    run(f"F 11x5.5E + {ah} Ah", cruise_x=0.909, hover_x=1.003, ah=ah, counter="true")
print("\n# G. what cruise factor gives exactly 5.0 min (counter=true, floor 0.92, 6.5 Ah)")
lo, hi = 0.3, 1.0
for _ in range(50):
    mid = (lo + hi) / 2
    if run("", cruise_x=mid, counter="true", quiet=True)["to_low_min"] >= 5.0: lo = mid
    else: hi = mid
print("cruise factor for 5.0 min:", round(lo, 4), "-> P", run("", cruise_x=lo, counter="true", quiet=True)["P_cruise_W"], "W")
lo, hi = 0.3, 1.0
for _ in range(50):
    mid = (lo + hi) / 2
    if run("", cruise_x=mid, counter="nameplate", quiet=True)["to_low_min"] >= 5.0: lo = mid
    else: hi = mid
print("cruise factor for 5.0 min, nameplate counter:", round(lo, 4))
for ah in [x/10 for x in range(65, 121)]:
    if run("", ah=ah, counter="true", quiet=True)["to_low_min"] >= 5.0:
        print("Ah for 5.0 min (counter true, 11x5.5MR):", ah); break
for ah in [x/10 for x in range(65, 121)]:
    if run("", ah=ah, cruise_x=0.909, hover_x=1.003, counter="true", quiet=True)["to_low_min"] >= 5.0:
        print("Ah for 5.0 min (counter true, 11x5.5E):", ah); break
print("\n# H. 16 m/s claims, counter corrected (for the record)")
for cid in ("CALC-E2-FAILSAFE", "CALC-E2-BUDGET-240"):
    print(cid, {k: round(v, 3) for k, v in kit._run(cid).items() if isinstance(v, float)})
print("\n# I. Li-ion 4S2P 21700 9 Ah (P45B class) sensitivity, EST: (OCV avg V/cell, R per series group ohm, cold factor)")
for ocv, rc, cold in ((3.70, 0.004, 1.5), (3.55, 0.005, 2.0), (3.50, 0.006, 2.0)):
    kw["ocv"], kw["r_cell"], kw["cold"] = ocv, rc, cold
    run(f"I Li-ion 9 Ah ocv {ocv} r {rc} cold {cold}, 11x5.5MR", ah=9.0, counter="true")
    run(f"I Li-ion 9 Ah ocv {ocv} r {rc} cold {cold}, 11x5.5E", ah=9.0, cruise_x=0.909, hover_x=1.003, counter="true")
