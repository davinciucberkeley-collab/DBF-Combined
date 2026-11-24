"""Concept A proof chain, part 1: mass, CG, thrust-to-weight, transition window, mission, stall, wind, yaw, roll.

Calculations re-compute from params-A.json (prop_a.py / mission_gate_a.py arithmetic, parameterised). Results that only a heavy
simulation produces (SITL roll rate, wind lean, motor peak) are read from the stored report through a `read_value` calculation:
the value is a parameter whose source is that report; nothing is re-run.
Run via run_all.py (or: python -I claims_a1_flight.py).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs"))     # redesign/proofs
import proofkit as pk  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from claimhelp_a import make_stored, pin, read_value  # noqa: E402,F401

kit = pk.Kit(__file__, params=["../params-A.json"], out="claims.a1_flight.json")


stored = make_stored(kit)


# ================================================================ propulsion model (prop_a.py, parameterised)
def _prop(tab, n):
    ks = sorted(tab, key=lambda r: r[0])
    n = max(ks[0][0], min(ks[-1][0], n))
    for a, b in zip(ks, ks[1:]):
        if a[0] <= n <= b[0]:
            f = (n - a[0]) / (b[0] - a[0])
            return a[1] + f * (b[1] - a[1]), a[2] + f * (b[2] - a[2])


def _run(tab, kv, rm, i0, vm):
    """motor terminal voltage -> (rpm, I, thrust N, shaft W)"""
    kt = 60 / (2 * math.pi * kv)
    lo, hi = 3000.0, 12000.0
    for _ in range(60):
        n = (lo + hi) / 2
        th, pw = _prop(tab, n)
        q = pw / (n * 2 * math.pi / 60)
        v = n / kv + (q / kt + i0) * rm
        lo, hi = (n, hi) if v < vm else (lo, n)
    n = (lo + hi) / 2
    th, pw = _prop(tab, n)
    q = pw / (n * 2 * math.pi / 60)
    return n, q / kt + i0, th, pw


def _full(tab, kv, rm, i0, rp, vrest, duty):
    """four motors saturated at `duty`, pack drop through rp"""
    lo, hi = 3.0, vrest
    for _ in range(50):
        vb = (lo + hi) / 2
        i = _run(tab, kv, rm, i0, vb * duty)[1]
        lo, hi = (vb, hi) if vrest - 4 * i * rp > vb else (lo, vb)
    return _run(tab, kv, rm, i0, vb * duty) + (vb,)


def _hover(tab, kv, rm, i0, m, der, cant, dl, eff, cm, g):
    """(gf per motor, rpm, A per motor, motor W, pack W incl. margins, pack A, motor volts)"""
    t = m * g / (4 * math.cos(math.radians(cant)) * dl) / der
    lo, hi = 3.0, 16.0
    for _ in range(60):
        vm = (lo + hi) / 2
        lo, hi = (vm, hi) if _run(tab, kv, rm, i0, vm)[2] < t else (lo, vm)
    n, i, th, pw = _run(tab, kv, rm, i0, vm)
    pin_ = vm * i / eff * cm
    return t * der / g * 1000, n, i, vm * i, 4 * pin_, 4 * pin_ / 14.8, vm


PROP = pin("prop", "apc_table", "kv", "rm_ohm", "i0_a", "rp_ohm", "derate", "cant_deg", "download", "hot_sag", "spin_cap", "v_fresh", "v_sag_rest")


# ================================================================ mass
@kit.calc("CALC-A-MASS-PRED", equation="m = basic_CAD x growth_factor + overrun_frac x gate   (MASS-GATE s7)",
          inputs={"basic": "P:mass.basic_cad_kg", "gf": "P:mass.growth_factor", "over": "P:mass.overrun_frac", "gate": "P:req.mass_gate_kg"},
          units={"basic": "kg", "gate": "kg"}, output="m_kg")
def mass_pred(basic, gf, over, gate):
    return basic * gf + over * gate


@kit.calc("CALC-A-MASS-ITEM", equation="m = (sum of item g x (1 + maturity growth) + overrun) / 1000   (mission_gate_a.py items)",
          inputs={"items": "P:mass.itemised_g_growth", "over": "P:mass.overrun_frac", "gate": "P:req.mass_gate_kg"},
          units={"gate": "kg"}, output="m_kg")
def mass_itemised(items, over, gate):
    base = sum(g for g, _ in items)
    growth = sum(g * k for g, k in items)
    return (base + growth) / 1000 + over * gate


@kit.calc("CALC-A-CUTS", equation="X = cuts - (target - m_pred) / growth_factor   (grams of the EST cuts that must be real)",
          inputs={"cuts": "P:mass.est_cuts_g", "target": "P:req.mass_target_kg", "m": "CL-A-MASS-PRED", "gf": "P:mass.growth_factor"},
          units={"target": "kg", "m": "kg"}, assumes=["ASM-A-CUTS"], output="x_g")
def cuts_required(cuts, target, m, gf):
    return cuts - (target - m) * 1000 / gf


@kit.calc("CALC-A-STRUCT", equation="structure = wing + fins + feet + hardware + cage (CAD groups, with the EST cuts)",
          inputs={"g": "P:mass.structure_groups_g"}, output="g")
def structure_mass(g):
    return sum(g)


kit.claim("CL-A-MASS-PRED", "Predicted take-off mass (CAD basic x growth + overrun)", calc="CALC-A-MASS-PRED", output="m_kg", unit="kg",
          limit=("<=", "P:req.mass_target_kg"), verifies=["A-D3"], parts=["WNG-001", "WNG-002", "PWR-001", "CGE-001", "FIN-001-R", "FIN-001-L"],
          how="Weigh-in (T-A-WEIGH): weigh foam, printed parts and epoxy first, then the aircraft with pack; predicted 1.881 kg EST at D-240 (CAD basic 1,641.0 g x growth + overrun, MASS-GATE.md; 1,423.9 g was the MASS-GATE s7 value at D-195).")
kit.claim("CL-A-MASS-ITEM", "Predicted mass, itemised growth by maturity (cross-check)", calc="CALC-A-MASS-ITEM", output="m_kg", unit="kg",
          limit=("<=", "P:req.mass_target_kg"), verifies=["A-D3"], how="python -I qp/A/mission_gate_a.py prints the itemised roll-up (1,449 g at D-195, superseded; MASS-GATE.md has the current tally); both methods must stay <= 1.470 kg (D-208).")
kit.claim("CL-A-MASS-GATE-ROOM", "Predicted mass against the 1.47 kg gate", calc="CALC-A-MASS-PRED", output="m_kg", unit="kg",
          limit=("<=", "P:req.mass_gate_kg"), verifies=["A-P1"], how="As-built weigh-in <= 1.47 kg (D-190, MASS-GATE s8); the +-5 % window holds to 1.478 kg.")
kit.claim("CL-A-MASS-USER", "Predicted mass against the 25 kg user cap", calc="CALC-A-MASS-PRED", output="m_kg", unit="kg",
          limit=("<=", "P:req.mass_user_max_kg"), verifies=["A-U5"], how="Weigh-in.")
kit.claim("CL-A-CUTS-REQUIRED", "EST cuts that must be real for <= 1.470 kg", calc="CALC-A-CUTS", output="x_g", unit="g",
          limit=("<=", "P:mass.est_cuts_g"), verifies=["A-D3"], assumes=["ASM-A-CUTS"],
          how="Weigh a FOAMULAR 150 block, a printed cup / hub, an epoxy joint (M11, BOARD QP-4 s1); >= 27.2 g of the 41.6 g must be real. Lead fallback 15.6 -> 12.8 g already applied (D-205).")
kit.claim("CL-A-STRUCT-MASS", "Structure mass (CAD groups, with the EST cuts)", calc="CALC-A-STRUCT", output="g", unit="g",
          limit=("<=", "P:req.structure_ceiling_g"), verifies=["A-D3"], assumes=["ASM-A-CUTS"],
          how="Weigh the airframe groups (wing, fins, feet, hardware, cage); ceiling 494 g, about 521 g without the cuts (FIXES2 s4).")


# ================================================================ CG, static margin
@kit.calc("CALC-A-CG-TRIM", equation="ends = CG - m_pack x trim_fwd / m_basic, CG + m_pack x trim / m_basic", inputs={"cg": "P:mass.cg_x_mm", "pack": "P:mass.pack_g", "trim": "P:mass.pack_trim_mm", "trim_fwd": "P:mass.pack_trim_fwd_mm",
                                                                                                "basic": "P:mass.basic_cad_kg"}, units={"cg": "mm", "basic": "kg"})
def cg_trim(cg, pack, trim, trim_fwd, basic):
    s = pack * trim / (basic * 1000)
    sf = pack * trim_fwd / (basic * 1000)
    return {"shift_mm": s, "fwd_mm": cg - sf, "aft_mm": cg + s}


@kit.calc("CALC-A-SM", equation="SM = (NP - CG) / chord x 100", inputs={"np": "ASM-A-NP", "cg": "P:mass.cg_x_mm", "c": "P:cg.chord_mm"}, units={"cg": "mm", "c": "mm"},
          assumes=["ASM-A-NP"], output="sm_pct")
def static_margin(np, cg, c):
    return (np - cg) / c * 100


stored("CL-A-CG", "CG aft of the leading edge, CAD as drawn", "P:mass.cg_x_mm", "mm", limit=(">=", "P:req.cg_lo_mm"), verifies=["A-P4"],
       parts=["PWR-001", "CGE-008", "WNG-001", "WNG-002"], how="CG breadboard (M5): hang the built aircraft, weigh on two knife edges; trim the pack +-10 mm.",
       equation="CG from sitl/cad_mass.json (CAD centroids of every part); read, not recomputed")
stored("CL-A-CG-HI", "CG aft limit of the design band", "P:mass.cg_x_mm", "mm", limit=("<=", "P:req.cg_hi_mm"), verifies=["A-P4"], parts=["PWR-001", "CGE-008"],
       how="CG breadboard (M5); band 19-26 mm (D-195), hard aft limit 28.5 mm.", equation="CG from sitl/cad_mass.json; read, not recomputed")
kit.claim("CL-A-CG-TRIM-AFT", "CG at the aft end of the pack trim travel", calc="CALC-A-CG-TRIM", output="aft_mm", unit="mm",
          limit=("<=", "P:req.cg_hard_aft_mm"), verifies=["A-P4"], parts=["PWR-001", "CGE-008"], how="Slide the pack to the aft slot stop and re-measure CG (M5).")
kit.claim("CL-A-CG-TRIM-FWD", "CG at the forward end of the pack trim travel", calc="CALC-A-CG-TRIM", output="fwd_mm", unit="mm",
          limit=(">=", "P:req.cg_lo_mm"), verifies=["A-P4"], parts=["PWR-001", "CGE-008"], how="Slide the pack to the forward slot stop and re-measure CG (M5).")
kit.claim("CL-A-SM", "Static margin at the CAD CG", calc="CALC-A-SM", output="sm_pct", unit="% chord", limit=(">=", "P:req.sm_min_pct"), verifies=["A-P4"],
          assumes=["ASM-A-NP"], parts=["WNG-001"], how="Measure NP on the built aircraft (M5, M6); SM >= 5 % chord.")
stored("CL-A-CG-LATERAL", "Lateral CG offset (CAD)", "P:mass.cg_y_mm", "mm", limit=("<=", "P:req.cg_lateral_max_mm"), verifies=["A-P4"],
       how="Hang the built aircraft on its spar centre; lateral CG <= 5 mm.", equation="cg_y from sitl/cad_mass.json; read, not recomputed")


# ================================================================ thrust-to-weight and the transition window (mission_gate_a.py)
def _tw(tab, kv, rm, i0, rp, der, cant, hot, spin_cap, v_fresh, v_sag_rest, g, lo, hi_frac, m):
    th = {}
    for tag, vr in (("fresh", v_fresh), ("sag", v_sag_rest)):
        for duty in (1.0, spin_cap):
            t_ = _full(tab, kv, rm, i0, rp, vr, duty)[2]
            th[(tag, duty)] = 4 * t_ / g * 1000 * (hot if tag == "sag" else 1.0) * der * math.cos(math.radians(cant))
    r = {k: v / (m * 1000) for k, v in th.items()}
    win = lambda tw: 100 * (hi_frac * tw - lo) / (hi_frac * tw + lo)
    return {"fresh_cap": r[("fresh", spin_cap)], "sag_cap": r[("sag", spin_cap)], "fresh_unc": r[("fresh", 1.0)], "sag_unc": r[("sag", 1.0)],
            "window_cap_pct": win(r[("sag", spin_cap)]), "window_unc_pct": win(r[("sag", 1.0)]), "sag_cap_gf": th[("sag", spin_cap)]}


TW_IN = dict(**PROP, g="P:env.g_ms2", lo="P:req.entry_low_w", hi_frac="P:req.entry_high_frac")
def tw_at(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, hot_sag, spin_cap, v_fresh, v_sag_rest, g, lo, hi_frac, m):
    return _tw(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, hot_sag, spin_cap, v_fresh, v_sag_rest, g, lo, hi_frac, m)


kit.calc("CALC-A-TW-GATE", equation="T/W = 4 T(duty) cos(cant) x derate x hot / (m g), prop_a.py model; window = (0.80 TWsag - 1.33)/(0.80 TWsag + 1.33)",
         inputs=dict(TW_IN, m="P:req.mass_gate_kg"), units={"m": "kg"})(tw_at)
kit.calc("CALC-A-TW-PRED", equation="same, at the predicted mass", inputs=dict(TW_IN, m="CL-A-MASS-PRED"), units={"m": "kg"})(tw_at)

TW_HOW = "Bench thrust stand (M1): fresh >= 780 gf and sag >= 624 gf per motor with the 0.90 cap (bench_analysis.py); model uses APC static data x 0.93 derate (a guess until M1)."
kit.claim("CL-A-TW-FRESH-GATE", "Hover T/W fresh at the 1.47 kg gate (0.90 cap)", calc="CALC-A-TW-GATE", output="fresh_cap", unit="-",
          limit=(">=", "P:req.tw_fresh_min"), verifies=["A-P1", "A-P2"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL", "PRP-002-UR", "PRP-002-UL", "PRP-002-LR", "PRP-002-LL"], how=TW_HOW)
kit.claim("CL-A-TW-SAG-GATE", "Hover T/W sagged pack at the 1.47 kg gate (0.90 cap)", calc="CALC-A-TW-GATE", output="sag_cap", unit="-",
          limit=(">=", "P:req.tw_sag_min"), verifies=["A-P1", "A-P2"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL", "PWR-001"], how=TW_HOW)
kit.claim("CL-A-TW-FRESH-PRED", "Hover T/W fresh at the predicted mass (0.90 cap)", calc="CALC-A-TW-PRED", output="fresh_cap", unit="-",
          limit=(">=", "P:req.tw_fresh_min"), verifies=["A-P2"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"], how=TW_HOW)
kit.claim("CL-A-TW-SAG-PRED", "Hover T/W sagged pack at the predicted mass (0.90 cap)", calc="CALC-A-TW-PRED", output="sag_cap", unit="-",
          limit=(">=", "P:req.tw_sag_min"), verifies=["A-P2"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL", "PWR-001"], how=TW_HOW)
kit.claim("CL-A-WINDOW-PRED", "Transition entry window at the predicted mass (0.90 cap)", calc="CALC-A-TW-PRED", output="window_cap_pct", unit="%",
          limit=(">=", "P:req.window_min_pct"), verifies=["A-P3"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"],
          how="C3 time-domain pitch-over run at the as-weighed mass (T-A-C3-PITCHOVER); the window uses 1.33 W low and 0.80 x T/W sag high.")
kit.claim("CL-A-WINDOW-GATE", "Transition entry window at the 1.47 kg gate (0.90 cap)", calc="CALC-A-TW-GATE", output="window_cap_pct", unit="%",
          limit=(">=", "P:req.window_min_pct"), verifies=["A-P3"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"],
          how="C3 run at the as-weighed mass; MASS-GATE s8: +-5 % holds to 1.478 kg at cant 17, gate 1.47 kg.",
          note="D-190 (CLAIMS-FIX s1): the gate was 1.50 kg (window +-4.3 % at cant 17); lowered to 1.47 kg so the window floor holds at the gate. Heavier analyses at 1.50 kg stay conservative.")


@kit.calc("CALC-A-WINDOW-MASS", equation="m_max = 0.93-derated sag thrust (0.90 cap) x 0.80 / (1.33 (1+w)/(1-w)), w = 5 %",
          inputs=dict(PROP, g="P:env.g_ms2", lo="P:req.entry_low_w", hi_frac="P:req.entry_high_frac", w="P:req.window_min_pct"), output="m_kg")
def window_mass(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, hot_sag, spin_cap, v_fresh, v_sag_rest, g, lo, hi_frac, w):
    th = _tw(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, hot_sag, spin_cap, v_fresh, v_sag_rest, g, lo, hi_frac, 1.0)["sag_cap_gf"]
    w = w / 100
    return th * hi_frac / (lo * (1 + w) / (1 - w)) / 1000


kit.claim("CL-A-WINDOW-MASS", "Largest mass with a +-5 % window (0.90 cap)", calc="CALC-A-WINDOW-MASS", output="m_kg", unit="kg",
          limit=(">=", "CL-A-MASS-PRED"), verifies=["A-P3"], how="MASS-GATE s8: 1.478 kg capped at cant 17; bench M1 thrust replaces the 0.93 derate.")


# ================================================================ motor current, ESC
def _one_motor(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, spin_cap, v_fresh, g, m, duty):
    ih = _hover(apc_table, kv, rm_ohm, i0_a, m, 1.0, cant_deg, download, 0.98, 1.10, g)
    vb = v_fresh
    for _ in range(30):
        i = _run(apc_table, kv, rm_ohm, i0_a, vb * duty)[1]
        ipack = i * duty + 3 * ih[2] * ih[6] / vb
        vb = v_fresh - rp_ohm * ipack
    return i


MOT_IN = dict(**pin("prop", "apc_table", "kv", "rm_ohm", "i0_a", "rp_ohm", "derate", "cant_deg", "download", "spin_cap", "v_fresh"), g="P:env.g_ms2",
              m="P:prop.hover_mass_ref_kg")
@kit.calc("CALC-A-MOTOR-I", equation="phase current of one motor at the duty cap with the other three at hover, 1.50 kg, fresh pack (prop_a.py one_motor)",
          inputs=dict(MOT_IN, duty="P:prop.spin_cap"), units={"m": "kg"}, output="i_a")
def motor_current_capped(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, spin_cap, v_fresh, g, m, duty):
    return _one_motor(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, spin_cap, v_fresh, g, m, duty)


@kit.calc("CALC-A-ESC-REQ", equation="I_req = 1.25 x peak one-motor current with no cap (full duty, three at hover, 1.50 kg, fresh)",
          inputs=dict(MOT_IN, factor="P:req.connector_factor"), units={"m": "kg"}, output="i_a")
def esc_required(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, spin_cap, v_fresh, g, m, factor):
    return factor * _one_motor(apc_table, kv, rm_ohm, i0_a, rp_ohm, derate, cant_deg, download, spin_cap, v_fresh, g, m, 1.0)


kit.claim("CL-A-MOTOR-I", "One motor at the 0.90 spin cap, winding current", calc="CALC-A-MOTOR-I", output="i_a", unit="A",
          limit=("<=", "P:req.motor_rating_a"), verifies=["A-P16"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL", "PRP-003"],
          how="Bench M2: one motor at duty 0.90 for 180 s, phase A <= 13 A, can <= 80 C. Without Q_M_SPIN_MAX 0.90 the same case is 14.3 A (prop_a.py).")
kit.claim("CL-A-ESC-I", "ESC channel and connector current required (1.25 x uncapped peak)", calc="CALC-A-ESC-REQ", output="i_a", unit="A",
          limit=("<=", "P:req.esc_rating_a"), verifies=["A-P16"], parts=["PRP-003"], how="Compare the SpeedyBee BLS 35A Mini V2 page (35 A continuous per channel) with 1.25 x 14.3 A.")


# ================================================================ mission: cruise time, energy to BATT_LOW, fence
@kit.calc("CALC-A-CRUISE-NEED", equation="R = V^2 / (g tan(bank)); lap = 2 L_ref + 2 pi R; need = settle + (laps + go-around + run-in) x lap / V",
          inputs={"v": "P:mission.cruise_ms", "g": "P:env.g_ms2", "bank": "P:mission.bank_deg", "leg": "P:mission.leg_ref_m", "settle": "P:mission.settle_s",
                  "laps": "P:mission.laps", "ga": "P:mission.goaround_laps", "runin": "P:mission.runin_laps"})
def cruise_need(v, g, bank, leg, settle, laps, ga, runin):
    r = v * v / (g * math.tan(math.radians(bank)))
    tl = (2 * leg + 2 * math.pi * r) / v
    return {"need_s": settle + (laps + ga + runin) * tl, "radius_m": r, "lap_s": tl}


@kit.calc("CALC-A-ENDURANCE", equation="t = (E_usable - E_hover - E_trans - E_climb) / P_cruise; E_usable = Ah x V x 0.90 x 0.80; hover and cruise power from the prop model and the (m / 1.37) scalings",
          inputs=dict(**pin("prop", "apc_table", "kv", "rm_ohm", "i0_a", "derate", "cant_deg", "download", "esc_eff", "ctrl_margin"), g="P:env.g_ms2", m="CL-A-MASS-PRED",
                      **pin("mission", "pack_ah", "pack_v", "floor_frac", "reserve_frac", "hover_s", "trans_wh_ref", "climb_wh_ref", "cruise_w_ref", "ref_mass_kg", "trans_exp", "cruise_exp")),
          units={"m": "kg"})
def endurance(apc_table, kv, rm_ohm, i0_a, derate, cant_deg, download, esc_eff, ctrl_margin, g, m, pack_ah, pack_v, floor_frac, reserve_frac, hover_s,
              trans_wh_ref, climb_wh_ref, cruise_w_ref, ref_mass_kg, trans_exp, cruise_exp):
    usable = pack_ah * pack_v * floor_frac * reserve_frac
    ph = _hover(apc_table, kv, rm_ohm, i0_a, m, derate, cant_deg, download, esc_eff, ctrl_margin, g)[4]
    eh, etr, ecl = ph * hover_s / 3600, trans_wh_ref * (m / ref_mass_kg) ** trans_exp, climb_wh_ref * (m / ref_mass_kg)
    pc = cruise_w_ref * (m / ref_mass_kg) ** cruise_exp
    return {"cruise_s": (usable - eh - etr - ecl) / pc * 3600, "usable_wh": usable, "hover_w": ph, "cruise_w": pc}


@kit.calc("CALC-A-FENCE", equation="bound = L/2 + R + run-out (any direction after cruise BATT_LOW)",
          inputs={"leg": "P:mission.leg_m", "r": "CL-A-CRUISE-RADIUS", "runout": "P:mission.runout_m"}, units={"r": "m"}, output="bound_m")
def fence_bound(leg, r, runout):
    return leg / 2 + r + runout


kit.claim("CL-A-CRUISE-NEED", "Cruise time the mission needs (300 m reference lap)", calc="CALC-A-CRUISE-NEED", output="need_s", unit="s",
          limit=("<=", 210.0), verifies=["A-D2"], how="Flight card 4b: settle 15 s, 2 laps, 1 go-around, run-in <= 1/2 lap at the cruise speed (18 m/s, D-255); requirement 3.5 min = 210 s (A-D2).",
          note="limit 210 s = the 3.5 min requirement of A-D2 / MISSION s2")
kit.claim("CL-A-CRUISE-RADIUS", "Turn radius at the cruise speed (18 m/s, D-255), 30 deg bank", calc="CALC-A-CRUISE-NEED", output="radius_m", unit="m", how="R = V^2 / (g tan 30) = 57.2 m at 18 m/s (51.0 m at 17 m/s, MISSION s2).")
kit.claim("CL-A-CRUISE-AVAIL", "Cruise time to BATT_LOW at the predicted mass", calc="CALC-A-ENDURANCE", output="cruise_s", unit="s",
          limit=(">=", "CL-A-CRUISE-NEED"), verifies=["A-D2"], parts=["PWR-001", "PRP-003"],
          how="Log a full-mission flight with power module (F06): BATT_LOW remaining >= 644 mAh of 2300 at the end; MISSION.md s4 energy table; power constants are EST (eta_p 0.26 x 0.76).")
kit.claim("CL-A-FENCE", "Any-direction bound after a cruise BATT_LOW", calc="CALC-A-FENCE", output="bound_m", unit="m",
          limit=("<=", "P:req.fence_bound_m"), verifies=["A-P24"], how="Flight card: racetrack leg 150 m, fence 250 m with FENCE_MARGIN 10 m; run-out 94 m is EST (MISSION s2).")


# ================================================================ stall
@kit.calc("CALC-A-STALL", equation="1.3 Vs = 1.3 sqrt(2 m g / (rho S CLmax)) at the gate mass", assumes=["ASM-A-CLMAX"],
          inputs={"m": "P:req.mass_gate_kg", "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3", "s": "P:mission.s_m2", "cl": "ASM-A-CLMAX", "k": "P:req.cruise_ratio"},
          units={"m": "kg", "rho": "kg/m3", "s": "m2"})
def stall(m, g, rho, s, cl, k):
    vs = math.sqrt(2 * m * g / (rho * s * cl))
    return {"vs_ms": vs, "k_vs_ms": k * vs}


kit.claim("CL-A-STALL", "1.3 x clean stall speed at the 1.47 kg gate", calc="CALC-A-STALL", output="k_vs_ms", unit="m/s",
          limit=("<=", "P:mission.cruise_ms"), verifies=["A-P6"], assumes=["ASM-A-CLMAX"], parts=["WNG-001"],
          how="Measured stall on the first cruise sorties (T-A-FIRST-CRUISE) replaces CLmax 0.75; 12.07 m/s stall, 15.69 m/s at 1.3 Vs at 1.47 kg (12.19 / 15.85 at 1.50 kg, MISSION s1).")


@kit.calc("CALC-A-STALL-PRED", equation="1.3 Vs = 1.3 sqrt(2 m g / (rho S CLmax)) at the predicted mass; rho 1.20 (MISSION s1), g 9.807, S 0.22 m2, CLmax 0.75 EST (ISA rho 1.225 gives 17.56 m/s at 1.881 kg, T-084; the project basis is 1.20)", assumes=["ASM-A-CLMAX"],
          inputs={"m": "CL-A-MASS-PRED", "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3", "s": "P:mission.s_m2", "cl": "ASM-A-CLMAX", "k": "P:req.cruise_ratio"},
          units={"m": "kg", "rho": "kg/m3", "s": "m2"})
def stall_pred(m, g, rho, s, cl, k):
    vs = math.sqrt(2 * m * g / (rho * s * cl))
    return {"vs_ms": vs, "k_vs_ms": k * vs}


kit.claim("CL-A-STALL-PRED", "1.3 x clean stall speed at the predicted take-off mass", calc="CALC-A-STALL-PRED", output="k_vs_ms", unit="m/s",
          limit=("<=", "P:mission.cruise_ms"), verifies=["A-P6"], assumes=["ASM-A-CLMAX"], parts=["WNG-001"],
          how="FAIL on the estimate (AM-011: physics checks apply at the predicted mass). Gated by TP-11 (TEST-PLAN-O4B): the measured stall (T-A-FIRST-CRUISE) must give CLmax >= 0.81 at this mass; D-255: cruise raised to 18 m/s for the elevon trim (T-101), so 17.74 m/s now passes with 0.26 m/s (1.4 %) on CLmax 0.75 EST; the measured stall (TP-11, CLmax >= 0.81 at this mass for a 17 m/s basis) still decides it (A-P6).")


# ================================================================ hover yaw authority
@kit.calc("CALC-A-YAW", equation="authority = 0.201 x 1.2 x sin(17)/sin(14) + 1.2 Q   (cant term + 1.2 x rotor reaction), D184.md / bench_analysis.py",
          inputs=pin("yaw", "cant_term_ref_nm", "arm_factor", "cant_deg", "cant_ref_deg", "q_model_nmm", "q_gain"), units={"q_model_nmm": "N mm"}, output="n_m")
def yaw_authority(cant_term_ref_nm, arm_factor, cant_deg, cant_ref_deg, q_model_nmm, q_gain):
    return (cant_term_ref_nm * arm_factor * math.sin(math.radians(cant_deg)) / math.sin(math.radians(cant_ref_deg))
            + q_gain * q_model_nmm / 1000)


kit.claim("CL-A-YAW-MODEL", "Hover yaw authority (model) at +-0.10 throttle", calc="CALC-A-YAW", output="n_m", unit="N m",
          limit=(">=", "P:req.yaw_pass_nm"), verifies=["A-P7"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL", "CGE-002-A", "CGE-002-B"],
          how="Hanging yaw test (M3) on the bench: >= 0.35 N m go; 0.30-0.35 go with the 4 m/s card; < 0.30 R2.",
          note="D-189 (CLAIMS-FIX s2): at cant 16 the model gave 0.3465 (marginally under 0.35); cant 17 gives 0.363. The bench (M3) is still the test.")
kit.claim("CL-A-YAW-R2", "Hover yaw authority (model) against the R2 floor", calc="CALC-A-YAW", output="n_m", unit="N m",
          limit=(">=", "P:req.yaw_r2_nm"), verifies=["A-P7"], how="Hanging yaw test (M3); below 0.30 N m the 5 m/s card is reopened (R2).")
stored("CL-A-YAW-Q", "Rotor reaction Q (model)", "P:yaw.q_model_nmm", "N mm", limit=(">=", "P:req.yaw_q_min_nmm"), verifies=["A-P7"],
       how="Measure Q on the bench thrust stand with torque (M1): >= 55 N mm.", equation="Q from D184.md (model); read, not recomputed")


# ================================================================ wind, SITL results read from the stored reports
stored("CL-A-WIND-LEAN", "Belly-on hover lean at 5 m/s (SITL max)", "P:sim.lean_belly_5ms_deg", "deg", limit=("<=", "P:req.lean_max_deg"), verifies=["A-P8"], parts=["WNG-001"],
       how="Tethered hover with the wing edge into the wind (M9); the heading rule keeps the belly out of the wind above 3 m/s.",
       equation="SITL case AP8_belly5 (D-258: 5 m/s belly-on, 1 m/s turbulence, 1.881 kg, X2216 hover model, ArduPlane 4.7.3-beta1 JSON backend; mechanism/out/T101_data/sitl_batch_AP8.txt); read, not re-run (was QP-2 SITL.md s70)")
stored("CL-A-WIND-OUTPUT", "Longest time any motor is at or above 0.85 output, 4 m/s turbulence hover (SITL, 1.881 kg predicted, X2216, worst pack; D-258)", "P:sim.wind_ge85_s", "s",
       limit=("<=", "P:req.motor_ge85_s_max"), verifies=["A-P8"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"],
       how="Log motor outputs in the tethered turbulence hover (M9) at <= 4 m/s mean: no motor above 0.85 for more than 0.5 s, none at the 0.90 cap.",
       note="D-258 (2026-11-24): re-run at 1.881 kg with the X2216 hover model: 0 s >= 0.85 in all seven, peak 0.738-0.761. History: D-192 (CLAIMS-FIX s3): the old claim read the 0.87 peak of the BASE airframe at 1.23 kg; at the 1.47 kg gate on the worst pack the 5 m/s peak is 0.89-0.90 (0.5-1.9 s above 0.85, cap touched), so the hover limit is 4 m/s (peak 0.83-0.873, <= 0.20 s above 0.85) and the line is stated as a duration. Peak 0.873 is reported, not a limit.",
       equation="SITL turbulence cases AP8_h* (D-258: run_case.py x2216_hover=1, 1.881 kg, CG 23.49 mm, A.param, arm 1.2, cant 17; mechanism/out/T101_data/sitl_batch_AP8.txt); read, not re-run (was N4_* / R5_h*)")
stored("CL-A-WIND-CAP", "Time any motor is at full output (the 0.90 cap line), 4 m/s turbulence hover (SITL, 1.881 kg, X2216, worst pack; D-258)", "P:sim.wind_cap_s", "s",
       limit=("<=", "P:req.motor_cap_s_max"), verifies=["A-P8"], parts=["PRP-001-UR", "PRP-001-UL", "PRP-001-LR", "PRP-001-LL"],
       how="Log motor outputs in the tethered turbulence hover (M9): no sample at the cap.", equation="same seven SITL runs; read, not re-run")
stored("CL-A-TIPOVER", "Static tip-over angle on the fin tips", "P:sim.tipover_deg", "deg", limit=(">=", "P:req.tipover_min_deg"), verifies=["A-P9"],
       parts=["GER-001-UR", "GER-001-UL", "GER-001-LR", "GER-001-LL", "FIN-001-R", "FIN-001-L"], how="Tilt test of the built aircraft on its feet (CG 20-26 mm): tips over at >= 30 deg.",
       equation="SIZING-A s4 geometry (feet 0.36 m apart, CG 0.275 m above); read, not recomputed")


# ================================================================ roll, pitch use
stored("CL-A-ROLL-141", "Peak roll rate in SITL at cruise speed, 1.455 kg (D-195 target mass)", "P:sim.roll_141_degs", "deg/s", limit=(">=", "P:req.roll_min_degs"), verifies=["A-P11"], parts=["WNG-006-R", "WNG-006-L"],
       how="Measure the roll rate on the first cruise (M8 extended); the surface is at its 20 deg stop at the peak, +3-5 % is smaller than the EST aero error.",
       equation="SITL case=roll, run R5_rt65 (6,126 / 57.3), D-195; read, not re-run")
stored("CL-A-ROLL-GATE", "Peak roll rate in SITL at cruise speed, 1.47 kg (the gate)", "P:sim.roll_150_degs", "deg/s", limit=(">=", "P:req.roll_min_degs"), verifies=["A-P11"], parts=["WNG-006-R", "WNG-006-L"],
       how="Measure the roll rate on the first cruise (T-A-FIRST-CRUISE).", equation="SITL case=roll, run R5_rt65g, D-195; read, not re-run")


stored("CL-A-PITCH-USE", "Elevon pitch use in transition (share of the 15 deg basis; the 0.60 line is 9 deg)", "P:sim.pitch_use_15_worst", "-", limit=("<=", "P:req.pitch_use_max"), verifies=["A-P11"], parts=["WNG-006-R", "WNG-006-L"],
       how="D-245: the standing line is 0.60 of 15 deg (SITL-FLIGHT.md l.25), worst C3 case 0.651 (0.554 / 0.571 / 0.651 / 0.605, AR-017) against 0.60, so FAIL, open pending the reserve derivation (D-251); the old 0.69-0.79 was the T-097 baseline (AR-015) before C3 controls (AR-010 item 5). Fix path is the ladder from rung 1 (controls: lower the entry pitch-rate demand), then a SITL rerun; a 20 deg basis is not used (no A-specific roll / gust reserve derivation; review round 10 98-4). First transition flight logs the elevon commands.",
       equation="SITL (ArduPlane, 6-DOF plant) transition runs T-097, pitch_use_15 in sum.json; read, not re-run")


if __name__ == "__main__":
    kit.write()
