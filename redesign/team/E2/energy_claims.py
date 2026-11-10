"""E2 battery / energy engineer: pack selection, energy budget per mission phase, voltage sag, charging and
test-day pack count for the K09-L quad tailsitter.

Run:  python -I redesign/team/E2/energy_claims.py        -> claims.json beside this file
Then: python -I redesign/proofs/build_graph.py           -> confirms nothing drifted

Method (one paragraph). The budget is kept in amp-hours, because that is what the flight controller's current
sensor counts (BATT_CAPACITY / BATT_LOW_MAH). For each phase the bus power P (W) is converted to pack current
with a Thevenin pack model, I = (Voc - sqrt(Voc^2 - 4 R P)) / (2 R), so voltage sag costs capacity. Hover power
comes from the maker's thrust table (linear through zero below the first row, as the K09 review did), with the
fin/tube download factor and the ESC loss; climb uses momentum theory; cruise uses the K09 drag build-up with
the review's corrected propulsive efficiencies. The 20 % reserve is 20 % of nameplate and is never planned
into. Two cases: BASE (sized mass, new pack, calm, warm) and PESSIMISTIC (2.6 kg gate, 92 % capacity, wind and
control margin on hover, CD0 x 1.3, eta_prop 0.35, longer transitions, cold pack). Every input is a node id.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ---------------------------------------------------------------- sources
kit.source("SRC-E2-OVONIC-LISTINGS", "Ovonic 4S 6500 hard-case listings (mass, size)", kind="web",
           url="https://us.ovonicshop.com/products/ovonic-50c-14-8v-6500mah-4s1p-hardcase-14-deans-lipo-battery",
           where="search results 2026-11-09 (pages rate-limited, not opened): Ovonic 50C 6500 4S hard case 522 g, "
                 "139 x 47 x 49 mm (us.ovonicshop.com); Ovonic 120C 6500 4S 551 g, 135 x 46 x 49 mm (ampow.com); "
                 "130C 6500 4S 545 g, 138 x 47 x 47.5 mm (rccaraction.com, Muchmore); 130C 2-pack 680 g, "
                 "157 x 48 x 43 mm, XT60 + JST-XH (rcdrone.top)",
           note="none of these is the exact 130C XT60 SKU the BOM buys; weigh and measure the first pack (T-E2-WEIGH)",
           status="UNVERIFIED")
kit.source("SRC-E2-OVONIC-120C-EC5", "Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5, 2-pack (named SKU, D-58)",
           kind="web", url="https://www.ampow.com/products/2-pack-ovonic-4s-6500mah-120c-lipo-hardcase-ec5-1-8-rc-car",
           checked="2026-11-10",
           where="product page read 2026-11-10: 6500 mAh, 120C, net weight 551 g (+/-5 g) per piece, 135 x 46 x 49 mm "
                 "(+/-3 mm), EC5 plug, JST-XHR-5P balance, 2 packs, in stock, EUR 98.69 shown (EU storefront; "
                 "another snippet EUR 113.30). Lead gauge not stated on the page: the EC5 contact takes 8-10 AWG, so "
                 "10 AWG is inferred, not read",
           note="checked = mass, size, plug and balance lead compared with the page; the lead gauge and the US price "
                "are confirmed by I1 at order (photo or seller answer) and by E2 on arrival (T-E2-WEIGH step 3a)")
kit.source("SRC-E2-TATTU-6750", "Tattu 4S 6750 mAh 25C LiPo, XT90 (fallback SKU)", kind="web",
           url="https://www.gensace.de/tattu-6750mah-14-8v-25c-4s1p-lipo-battery-with-xt90.html",
           where="search results 2026-11-10 (page not opened): net weight 605 g (+/-10 g), wire gauge 10#, XT90, "
                 "about 138 x 42 x 44 mm; NextFPV USD 74 sale / 83 list per pack, stock 'contact us'; Grepow 620 g",
           status="UNVERIFIED")
kit.source("SRC-E2-HTRC-C150", "HTRC C150 150 W AC/DC balance charger", kind="web",
           url="https://www.amazon.com/dp/B0H4QLJYHY",
           where="config-study/cards/K09/cost.csv ground line ($56.99, 2026-11-01); 150 W AC rating from the BOM line",
           note="maximum charge current and IR-measurement function not confirmed: read the manual on arrival",
           status="UNVERIFIED")
kit.source("SRC-E2-FAA-PACKSAFE", "FAA PackSafe: lithium batteries", kind="web",
           url="https://www.faa.gov/hazmat/packsafe/lithium-batteries",
           where="spare lithium-ion/polymer batteries <= 100 Wh: carry-on only, no airline approval needed",
           status="UNVERIFIED")
kit.source("SRC-E2-ARDUPILOT-BATT", "ArduPilot battery failsafe parameters", kind="web",
           url="https://ardupilot.org/plane/docs/apms-failsafe-function.html",
           where="BATT_LOW_MAH / BATT_CRT_MAH / BATT_LOW_VOLT / BATT_CRT_VOLT / BATT_FS_VOLTSRC; capacity counter "
                 "assumes a full pack at boot", status="UNVERIFIED")

# ---------------------------------------------------------------- assumptions
A = kit.assumption
A("ASM-E2-ESC-EFF", "ESC efficiency 0.95", "Bus power = motor input power / 0.95",
  basis="K09 sizing.py ESC_EFF; the maker table is probably measured at the supply already, so this is conservative "
        "(REVIEW section 3)", value=0.95, unit="-", status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])
A("ASM-E2-AVIONICS-W", "Avionics + servos 6 W", "FC, GPS, RX, airspeed, UBEC loss and two micro servos draw 6 W",
  basis="K09 card 5 W had no servos; +1 W for two micro servos holding trim. F1/F3 replace with the bench current",
  value=6.0, unit="W", status="UNVERIFIED", cites=["SRC-K09-CARD"])
A("ASM-E2-OCV-AVG", "Average open-circuit voltage 3.70 V/cell", "Mean OCV between 100 % and 20 % state of charge",
  basis="LiPo OCV curve averages ~3.80 V over 100-20 %; 3.70 V nameplate is used (conservative ~3 %)",
  value=3.70, unit="V", cites=["SRC-OVONIC-4S6500"])
A("ASM-E2-OCV-20", "OCV at 20 % charge 3.73 V/cell", "Resting voltage at the 20 % reserve line",
  basis="typical LiPo rest curve (3.73-3.75 V at 20 %); measured on the first discharge test (T-E2-CAPACITY)",
  value=3.73, unit="V", status="UNVERIFIED")
A("ASM-E2-R-CELL", "Cell resistance 4.0 mOhm at 25 degC", "DC internal resistance per cell of a new 4S 6500 hard-case pack",
  basis="hobby 6000-6500 mAh packs measure 2.5-5 mOhm/cell new; C-rating labels (130C) are not physical. "
        "Measure with a load step (T-E2-IR)", value=0.0040, unit="ohm", status="UNVERIFIED")
R_EXT_MIRROR_OHM = 0.0065     # = P:electrical.r_ext_mohm / 1000 (CL-F1-R-EXT); checked against params in __main__
A("ASM-E2-R-EXT", "Pack lead, connector and harness 6.5 mOhm (mirror of params electrical.r_ext_mohm)",
  "Series resistance between the cells and the ESC power pads, hot: F1's CL-F1-R-EXT via params "
  "electrical.r_ext_mohm (D-32)",
  basis="E2's own calcs read P:electrical.r_ext_mohm directly. This id is kept only for the calcs of other roles that "
        "still read it (E1 CALC-E1-WORST, E3, H1), so they re-run on 6.5 instead of the old 3 mOhm; it retires when "
        "they re-point to the parameter (CR-E2-17). energy_claims.py stops if the two ever differ. Was 3 mOhm "
        "(E2 estimate before F1's harness model)",
  value=R_EXT_MIRROR_OHM, unit="ohm", status="UNVERIFIED", cites=["CL-F1-R-EXT"])
A("ASM-E2-COLD-R", "Cold-pack resistance factor 1.5", "Cell resistance at 10 degC = 1.5 x the 25 degC value",
  basis="LiPo IR roughly doubles from 25 to 0 degC; 10 degC is the bottom of params env.ambient_design_c "
        "(March-April 07:00 at RFS). Keeping packs in the car cabin removes most of it", value=1.5, unit="-",
  status="UNVERIFIED")
A("ASM-E2-HOVER-MARGIN", "Hover wind/control factor 1.10 (pessimistic)",
  "Hover power in 5 m/s wind with station-keeping activity = 1.10 x calm hover power",
  basis="16 deg lean at 5 m/s needs T/cos = 1.04 W; P ~ T^1.5 gives +6 %; +4 % for attitude-control activity. "
        "Replace with the twin's logged hover current", value=1.10, unit="-", status="UNVERIFIED",
  cites=["SRC-K09-REVIEW"])
A("ASM-E2-PROFILE", "Mission profile timings",
  "Ground 180 s at avionics power; climb and descent between 0 and 50 m AGL at 2.0 / 1.0 m/s; forward and back "
  "transitions 10 s at 1.4 / 1.3 x hover power (pessimistic 20 s each); 120 s hover; cruise to the reserve line",
  basis="R-TEST-ORDER transition at >= 50 m AGL; ArduPilot Q_PILOT_SPD_UP default 2.5 m/s, land 1 m/s; tailsitter "
        "pitch-over is a few seconds at high throttle (J1 evidence); doubled for the pessimistic case",
  value={"ground_s": 180, "alt_m": 50, "climb_ms": 2.0, "descent_ms": 1.0, "hover_s": 120,
         "trans_s": [10, 20], "trans_fwd_factor": 1.4, "trans_back_factor": 1.3}, unit="-", status="PROPOSED")
A("ASM-E2-CRUISE-AERO", "Cruise mass scaling, circuit factor and independent cross-check model",
  "The cruise power LEVEL is B1's (CL-B1-CRUISE-P / -P-PESS, level flight at the gate, avionics included). This "
  "E2 drag model (CD0 0.0593, x1.3 pessimistic, e from params, eta_prop 0.47 / 0.35, eta_motor 0.72, trim 1.05) "
  "only scales B1's power from the gate to another mass, and is reported as a cross-check. The turning (circuit) "
  "factor 1.05 multiplies B1's level-flight power",
  basis="K09 sizing.json CD0 build-up; REVIEW section 4 corrected efficiencies; circuits inside one RFS sub-field "
        "spend about half the time in 30 deg banks (induced drag x1.33). CR-E2-08: B1 owns cruise power; E2 "
        "follows B1's claims through the proof chain (re-run this script after every B1 re-run)",
  value={"cd0": 0.0593, "cd0_pess": 1.3, "eta_prop": [0.47, 0.35], "eta_motor": 0.72, "trim": 1.05,
         "circuit": 1.05}, unit="-", status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])
A("ASM-E2-PACK-CANDIDATES", "4S pack candidates [name, Ah, kg, continuous A]",
  "Candidate flight packs, all 4S LiPo (KV900 motors fix 4S), plus one Li-ion option",
  basis="Admiral 4000: Motion RC listing 386 g. 5000 and 8000: typical hard-case class masses (EST). 6500: "
        "params battery.mass_kg. Li-ion 4S2P 21700 (P45B class, 9 Ah, 90 A cont): 8 x 70 g + 60 g. "
        "Continuous A = realistic cell limit, not the label C",
  value=[["Admiral 4S 4000 LiPo", 4.0, 0.386, 120.0], ["4S 5000 hard-case LiPo (EST)", 5.0, 0.46, 150.0],
         ["Ovonic 4S 6500 120C hard case EC5 (named, 551 g listed)", 6.5, 0.55, 195.0],
         ["Tattu 4S 6750 25C XT90 (605 g listed)", 6.75, 0.605, 168.75],
         ["Ovonic 4S 6500 130C XT60 (680 g listed, 12 AWG)", 6.5, 0.68, 195.0],
         ["4S 8000 hard-case LiPo (EST)", 8.0, 0.70, 240.0],
         ["Li-ion 4S2P 21700 9 Ah (EST)", 9.0, 0.62, 90.0]], unit="-", status="UNVERIFIED",
  cites=["SRC-E2-OVONIC-120C-EC5", "SRC-E2-TATTU-6750", "SRC-E2-OVONIC-LISTINGS", "SRC-K09-CARD"])
A("ASM-E2-PACK-SKU", "Named flight-pack SKU (D-58): listed data",
  "Ovonic 14.8V 120C 4S 6500 mAh hard case, EC5, 2-pack: 0.551 kg +/- 0.005 per pack, 135 x 46 x 49 mm +/- 3 mm, "
  "factory discharge leads 10 AWG (inferred from the EC5 plug), JST-XH 5-pin balance lead",
  basis="SRC-E2-OVONIC-120C-EC5 read 2026-11-10. The 120C label is not a physical continuous rating; the real limit "
        "is the cell IR (ASM-E2-R-CELL, T-E2-IR). Re-terminated EC5 -> AS150U on arrival as before (D-32)",
  value={"mass_kg": 0.551, "mass_tol_kg": 0.005, "size_m": [0.135, 0.046, 0.049], "size_tol_m": 0.003,
         "lead_awg": 10}, unit="-", status="UNVERIFIED", cites=["SRC-E2-OVONIC-120C-EC5"])
A("ASM-E2-PACK-LIMITS", "Pack acceptance limits (D-58, D-15, CR-F1-14)",
  "Pack mass <= 0.601 kg (D-58: the mass above which the first-build overrun is no longer covered; A3-R6 re-ran it "
  "to 0.613 kg, the stricter D-58 value is used); body fits the D2 bay 0.160 x 0.052 x 0.053 m (D-15); discharge "
  "leads 10 AWG or heavier (AWG number <= 10, CR-F1-14, CL-F1-PACKLEAD12-RISE)",
  basis="params/CHANGE-LOG.md D-58, D-15; MASS-CG.md A3-R6 (covered up to 613 g); F1 pack-lead rise rule "
        "electrical.pack_lead_rise_max_c 20 K (12 AWG 28.4 K)",
  value={"mass_max_kg": 0.601, "bay_m": [0.160, 0.052, 0.053], "awg_max": 10}, unit="-", status="PROPOSED")
A("ASM-E2-TESTDAY", "Test-day window and turnaround",
  "Flying window 180 min (07:00-10:00 flight card); 20 min on the ground between sorties (log check, feet and "
  "prop inspection, pack swap, re-brief); one fully charged pack per sortie; no charging at the field",
  basis="R-SITE flight card; CONFIGURATION.md morning-only; RFS mains power not confirmed, and P21 forbids car "
        "charging", value={"window_min": 180, "turnaround_min": 20}, unit="-", status="PROPOSED")
A("ASM-E2-CHARGE", "Charge profile", "CC at min(1C, charger W / 16.8 V) to ~85 % state of charge, then CV for 20 min",
  basis="standard LiPo CC-CV; 1C is the maker's normal charge rate for hobby packs", value={"cc_end_soc": 0.85,
  "cv_min": 20, "c_max": 1.0}, unit="-", status="PROPOSED")


# ---------------------------------------------------------------- helpers (pure)
def pack_current(p_w, voc, r):
    """Pack current for bus power p_w with a Thevenin source (voc, r)."""
    disc = voc * voc - 4 * r * p_w
    if disc < 0:
        raise ValueError("power beyond the pack's maximum transfer")
    return (voc - math.sqrt(disc)) / (2 * r)


def table_power(table, thrust_g):
    """Motor input W per motor; linear through zero below the first row (conservative, REVIEW section 3)."""
    rows = sorted(table)
    if thrust_g <= rows[0][0]:
        return rows[0][1] * thrust_g / rows[0][0]
    for (g0, w0), (g1, w1) in zip(rows, rows[1:]):
        if thrust_g <= g1:
            return w0 + (w1 - w0) * (thrust_g - g0) / (g1 - g0)
    return rows[-1][1]


def hover_bus_w(m_kg, n, table, download, esc, avn):
    return n * table_power(table, m_kg * 1000 * download / n) / esc + avn


def climb_factor(m_kg, g, rho, n, D, vc):
    """P_climb / P_hover from momentum theory: vc/(2 vh) + sqrt((vc/(2 vh))^2 + 1)."""
    vh = math.sqrt(m_kg * g / n / (2 * rho * math.pi * D * D / 4))
    x = vc / (2 * vh)
    return x + math.sqrt(x * x + 1)


def cruise_bus_w(m_kg, g, rho, S, b, e, V, cd0, eta_p, eta_m, trim, circuit, avn):
    W = m_kg * g
    cl = 2 * W / (rho * V * V * S)
    cd = cd0 + cl * cl / (math.pi * b * b / S * e)
    D = 0.5 * rho * V * V * S * cd
    return D * V * trim * circuit / (eta_p * eta_m) + avn


PHASE_KEYS = {"ground, armed checks": "ground", "climb 0-50 m": "climb", "hover (mission)": "hover",
              "transition forward": "trans_fwd", "back-transition": "trans_back", "descent 50-0 m": "descent",
              "cruise": "cruise"}


def budget(m_kg, pess, *, n, table, download, esc, avn, g, rho, D, S, b, e, V, cells, ah, ocv, r_cell, r_ext,
           cold, hmargin, prof, aero, cap_frac, reserve, pc_b, pc_p, m_ref, p_scale=1.0):
    """Phase table [name, s, W, A, Ah] and the cruise time to the reserve line. r_ext in mOhm (params unit)."""
    k = 1 if pess else 0
    r_ext = r_ext / 1000.0
    r = cells * r_cell * (cold if pess else 1.0) + r_ext
    voc = cells * ocv
    ph = hover_bus_w(m_kg, n, table, download, esc, avn) * (hmargin if pess else 1.0)
    alt = prof["alt_m"]
    phases = [
        ("ground, armed checks", prof["ground_s"], avn),
        ("climb 0-50 m", alt / prof["climb_ms"], ph * climb_factor(m_kg, g, rho, n, D, prof["climb_ms"])),
        ("hover (mission)", prof["hover_s"], ph),
        ("transition forward", prof["trans_s"][k], ph * prof["trans_fwd_factor"]),
        ("back-transition", prof["trans_s"][k], ph * prof["trans_back_factor"]),
        ("descent 50-0 m", alt / prof["descent_ms"], ph),
    ]
    rows, ah_fixed = [], 0.0
    for name, t, p in phases:
        i = pack_current(p, voc, r)
        rows.append([name, t, p, i, i * t / 3600])
        ah_fixed += i * t / 3600
    cd0 = aero["cd0"] * (aero["cd0_pess"] if pess else 1.0)

    def e2_model(mm):                               # level flight, no circuit factor (B1's basis)
        return cruise_bus_w(mm, g, rho, S, b, e, V, cd0, aero["eta_prop"][k], aero["eta_motor"], aero["trim"],
                            1.0, avn)
    # B1's level-flight power at the gate, scaled to this mass by the E2 drag model, x circuit factor
    pc = (pc_p if pess else pc_b) * p_scale * aero["circuit"] * e2_model(m_kg) / e2_model(m_ref)
    pc_e2 = e2_model(m_kg) * aero["circuit"]
    ic = pack_current(pc, voc, r)
    ah_avail = ah * (cap_frac if pess else 1.0) - ah * reserve      # reserve = 20 % of nameplate, never planned in
    ah_cruise = ah_avail - ah_fixed
    rows.append(["cruise", ah_cruise / ic * 3600, pc, ic, ah_cruise])
    ih = pack_current(ph, voc, r)
    out = {"phases": rows, "cruise_min": ah_cruise / ic * 60, "ah_fixed": ah_fixed, "ah_avail": ah_avail,
           "hover_w": ph, "hover_a": ih, "cruise_w": pc, "cruise_a": ic, "cruise_w_e2_model": pc_e2,
           "hover_only_min": (ah_avail - rows[0][4]) / ih * 60,
           "flight_min": (sum(x[1] for x in rows) - prof["ground_s"]) / 60, "r_pack": r}
    for name, t, _, i, _ in rows:                   # flat per-phase outputs, so each can be a claim (CR-F1-04)
        out[f"i_{PHASE_KEYS[name]}_a"] = i
        out[f"t_{PHASE_KEYS[name]}_s"] = t
    out["i_max_phase_a"] = max(x[3] for x in rows)
    return out


COMMON = {"n": P + "propulsion.n_motors", "table": P + "propulsion.thrust_table_g_w",
          "download": P + "propulsion.download_factor", "esc": "ASM-E2-ESC-EFF", "avn": "ASM-E2-AVIONICS-W",
          "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "D": P + "propulsion.prop_diameter_m",
          "S": "CL-A1-WING-AREA", "b": P + "wing.span_m", "e": P + "wing.oswald_e", "V": P + "performance.cruise_ms",
          "cells": P + "battery.cells_s", "ah": P + "battery.capacity_ah", "ocv": "ASM-E2-OCV-AVG",
          "r_cell": "ASM-E2-R-CELL", "r_ext": P + "electrical.r_ext_mohm", "cold": "ASM-E2-COLD-R",
          "hmargin": "ASM-E2-HOVER-MARGIN", "prof": "ASM-E2-PROFILE", "aero": "ASM-E2-CRUISE-AERO",
          "cap_frac": P + "requirements.pack_capacity_min_frac", "reserve": P + "requirements.energy_reserve_frac",
          "pc_b": "CL-B1-CRUISE-P", "pc_p": "CL-B1-CRUISE-P-PESS", "m_ref": P + "requirements.mtow_gate_kg"}
CU = {"g": "m/s2", "rho": "kg/m3", "D": "m", "S": "m2", "b": "m", "V": "m/s", "ah": "Ah", "ocv": "V",
      "r_cell": "ohm", "r_ext": "mOhm", "pc_b": "W", "pc_p": "W", "m_ref": "kg"}
ASSUMES = ["ASM-E2-ESC-EFF", "ASM-E2-AVIONICS-W", "ASM-E2-OCV-AVG", "ASM-E2-R-CELL",
           "ASM-E2-PROFILE", "ASM-E2-CRUISE-AERO"]


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-E2-BUDGET-BASE", title="Energy budget per phase, base case (sized mass)", assumes=ASSUMES,
          equation="I = (Voc - sqrt(Voc^2 - 4 R P)) / (2 R) per phase ; Ah = I t ; "
                   "P_cruise = P_B1(gate) x circuit x P_E2(m) / P_E2(gate) ; "
                   "t_cruise = (C - 0.2 C - sum Ah_fixed) / I_cruise",
          inputs={"m": "CL-A1-MASS-SIZED", **COMMON}, units={"m": "kg", **CU})
def budget_base(m, **kw):
    r = budget(m, False, **kw)
    return {k: v for k, v in r.items()}


@kit.calc("CALC-E2-BUDGET-PESS", title="Energy budget per phase, pessimistic (2.6 kg gate)",
          assumes=ASSUMES + ["ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN"],
          equation="as base, with m = gate, C x 0.92, R x 1.5 (10 degC), P_hover x 1.10, P_cruise = B1 pessimistic "
                   "(CD0 x 1.3, eta_prop x 0.85) x circuit, 20 s transitions",
          inputs={"m": P + "requirements.mtow_gate_kg", **COMMON}, units={"m": "kg", **CU})
def budget_pess(m, **kw):
    return budget(m, True, **kw)


@kit.calc("CALC-E2-SAG", title="Bus voltage at the 100 A limiter vs pack state; bracket on the thrust factor",
          equation="V_bus = Voc - R I_lim (limiter binds when I_unlim(V) = n I_148 (V/14.8)^2 > I_lim) ; "
                   "thrust factor worst/fresh bracketed by (V_w/V_f) (thrust prop. to power) and (V_w/V_f)^(2/3) "
                   "(ideal rotor at fixed current) ; old rule (V/V_tab)^2 kept for the record (unlimited motor) ; "
                   "bracket margin = min(f_E1 - lower, upper - f_E1)",
          inputs={"cells": P + "battery.cells_s", "i_lim": P + "performance.full_throttle_current_a",
                  "i148": "CL-E1-IMAX-148-55", "n": P + "propulsion.n_motors", "ocv20": "ASM-E2-OCV-20",
                  "r_cell": "ASM-E2-R-CELL", "r_ext": P + "electrical.r_ext_mohm", "cold": "ASM-E2-COLD-R",
                  "ah": P + "battery.capacity_ah", "f_e1": "CL-E1-SAG-FACTOR"},
          units={"i_lim": "A", "i148": "A", "ocv20": "V", "r_cell": "ohm", "r_ext": "mOhm", "ah": "Ah"},
          assumes=["ASM-E2-OCV-20", "ASM-E2-R-CELL", "ASM-E2-COLD-R"])
def sag(cells, i_lim, i148, n, ocv20, r_cell, r_ext, cold, ah, f_e1):
    r_ext = r_ext / 1000.0
    cases = {"full_warm": (cells * 4.20, cells * r_cell + r_ext),
             "res20_warm": (cells * ocv20, cells * r_cell + r_ext),
             "res20_cold": (cells * ocv20, cells * r_cell * cold + r_ext)}
    out = {}
    for k, (voc, r) in cases.items():
        v = voc - r * i_lim
        out[f"v_{k}"] = v
        out[f"r_{k}_ohm"] = r
        out[f"i_unlim_{k}"] = n * i148 * (v / 14.8) ** 2      # four motors at full duty; prop load I ~ V^2
        out[f"limiter_binds_{k}"] = 1.0 if out[f"i_unlim_{k}"] > i_lim else 0.0
    ratio = out["v_res20_cold"] / out["v_full_warm"]
    out["f_lower_thrust_prop_v"] = ratio
    out["f_upper_ideal_rotor"] = ratio ** (2.0 / 3.0)
    out["f_old_v2_rule"] = (out["v_res20_cold"] / 14.8) ** 2   # D-06 / E2-R2 rule: double-counts under the limiter
    out["f_e1"] = f_e1
    out["e1_bracket_margin"] = min(f_e1 - ratio, ratio ** (2.0 / 3.0) - f_e1)
    out["e1_exponent"] = math.log(f_e1) / math.log(ratio)
    out["c_peak"] = i_lim / ah
    out["sag_v_per_cell_worst"] = (cells * ocv20 - out["v_res20_cold"]) / cells
    out["v_cell_worst_loaded"] = out["v_res20_cold"] / cells
    return out


@kit.calc("CALC-E2-HEAT", title="Pack self-heating over the pessimistic mission, cold and hot mornings",
          equation="Q = sum(I^2 R t) over phases ; dT = Q / (m c) (adiabatic, c = 1000 J/kg K) ; "
                   "T_end = T_amb + dT ; cold: 10 degC, R x 1.5 ; hot: 30 degC, R x 1.0",
          inputs={"b": "CL-E2-BUDGET-PESS-TABLE", "r_cell": "ASM-E2-R-CELL", "cells": P + "battery.cells_s",
                  "cold": "ASM-E2-COLD-R", "m": P + "battery.mass_kg", "amb": P + "env.ambient_design_c"},
          units={"r_cell": "ohm", "m": "kg", "amb": "degC"}, assumes=["ASM-E2-R-CELL", "ASM-E2-COLD-R"])
def heat(b, r_cell, cells, cold, m, amb):
    out = {}
    for case, t_amb, f in (("cold", amb[0], cold), ("hot", amb[1], 1.0)):
        r = cells * r_cell * f                     # cell resistance only (leads heat the harness, not the pack)
        q = sum(row[3] ** 2 * r * row[1] for row in b)
        out[f"dT_{case}_k"] = q / (m * 1000.0)
        out[f"t_end_{case}_c"] = t_amb + q / (m * 1000.0)
        out[f"p_hover_{case}_w"] = b[2][3] ** 2 * r
    out["t_end_max_c"] = max(out["t_end_cold_c"], out["t_end_hot_c"])
    return out


@kit.calc("CALC-E2-PACK-TRADE", title="Pack trade: candidates against the gate and the pessimistic mission",
          equation="m = m_sized - m_pack_baseline + m_cand ; pessimistic at m + (gate - m_sized) ; pass = m <= gate AND t_cruise_pess >= 5 min AND "
                   "I_cont >= I_full",
          inputs={"cands": "ASM-E2-PACK-CANDIDATES", "m_sized": "CL-A1-MASS-SIZED", "m_pack": P + "battery.mass_kg",
                  "gate": P + "requirements.mtow_gate_kg", "t_req": P + "requirements.cruise_time_min",
                  "i_full": P + "performance.full_throttle_current_a", **{k: v for k, v in COMMON.items() if k != "ah"}},
          units={"m_sized": "kg", "m_pack": "kg", "gate": "kg", "t_req": "min", "i_full": "A",
                 **{k: v for k, v in CU.items() if k != "ah"}},
          assumes=["ASM-E2-PACK-CANDIDATES"] + ASSUMES)
def pack_trade(cands, m_sized, m_pack, gate, t_req, i_full, **kw):
    rows, best = [], None
    for name, ah, kg, icont in cands:
        m = m_sized - m_pack + kg
        base = budget(m, False, ah=ah, **kw)["cruise_min"]
        pess = budget(m + (gate - m_sized), True, ah=ah, **kw)["cruise_min"]      # same growth to the gate
        ok = m <= gate + 1e-9 and pess >= t_req and icont >= i_full
        rows.append([name, ah, kg, round(m, 3), round(base, 1), round(pess, 1), icont, ok])
        if ok and (best is None or ah > best[1]):
            best = rows[-1]
    return {"table": rows, "largest_passing_ah": best[1], "largest_passing": best[0]}


@kit.calc("CALC-E2-FAILSAFE", title="Battery failsafe thresholds for the flight controller",
          equation="CRT_MAH = reserve C ; LOW_MAH = CRT + Ah(back-transition + descent + 60 s return cruise + "
                   "30 s landing hover), pessimistic currents, rounded up to 100 mAh",
          inputs={"b": "CL-E2-BUDGET-PESS-TABLE", "ah": P + "battery.capacity_ah",
                  "reserve": P + "requirements.energy_reserve_frac"}, units={"ah": "Ah"})
def failsafe(b, ah, reserve):
    return failsafe_rows(b, ah, reserve)


def failsafe_rows(b, ah, reserve):
    rows = {r[0]: r for r in b}
    need = rows["back-transition"][4] + rows["descent 50-0 m"][4] + rows["cruise"][3] * 60 / 3600 \
        + rows["hover (mission)"][3] * 30 / 3600
    crt = math.ceil(ah * reserve * 10) * 100
    low = math.ceil((ah * reserve + need) * 10) * 100
    before = sum(rows[k][4] for k in ("ground, armed checks", "climb 0-50 m", "hover (mission)", "transition forward"))
    to_low = (ah - low / 1000 - before) / rows["cruise"][3] * 60       # counter reads nameplate mAh
    return {"crt_mah": crt, "low_mah": low, "land_need_mah": need * 1000, "cruise_to_low_min": to_low}


@kit.calc("CALC-E2-TESTDAY", title="Sorties per test day and charge time",
          equation="sorties_window = floor(window / (t_flight + t_turn)) ; sorties = min(packs, window) (D-12: 2) ; "
                   "window used = sorties t_flight + (sorties - 1) t_turn ; "
                   "t_charge = (0.85 - 0.20) C / I_cc + t_cv ; I_cc = min(1C, P_chg / 16.8 V)",
          inputs={"b": "CL-E2-BUDGET-BASE-TABLE", "td": "ASM-E2-TESTDAY", "n_packs": P + "battery.n_packs",
                  "ah": P + "battery.capacity_ah", "cells": P + "battery.cells_s", "chg": "ASM-E2-CHARGE",
                  "p_chg": "ASM-E2-CHARGER-W", "reserve": P + "requirements.energy_reserve_frac"},
          units={"ah": "Ah", "p_chg": "W"}, assumes=["ASM-E2-TESTDAY", "ASM-E2-CHARGE"])
def testday(b, td, n_packs, ah, cells, chg, p_chg, reserve):
    t_flight = sum(r[1] for r in b) / 60
    window = math.floor(td["window_min"] / (t_flight + td["turnaround_min"]))
    i_cc = min(chg["c_max"] * ah, p_chg / (cells * 4.2))
    t_chg = (chg["cc_end_soc"] - reserve) * ah / i_cc * 60 + chg["cv_min"]
    planned = min(n_packs, window)
    return {"t_sortie_min": t_flight, "sorties_window": window, "sorties_current_packs": planned,
            "window_used_min": planned * t_flight + (planned - 1) * td["turnaround_min"],
            "packs_to_fill_window": window, "charge_min_per_pack": t_chg,
            "charge_h_current_packs": n_packs * t_chg / 60, "charge_h_4_packs": 4 * t_chg / 60,
            "i_cc_a": i_cc}


A("ASM-E2-CHARGER-W", "Charger output 150 W", "HTRC C150 delivers 150 W into one pack on AC",
  basis="BOM line 'HTRC C150 charger 150 W AC'; output vs input rating to confirm from the manual",
  value=150.0, unit="W", status="UNVERIFIED", cites=["SRC-E2-HTRC-C150"])


@kit.calc("CALC-E2-SKU-CHECK", title="Named pack SKU against the D-58 mass line, the bay and the lead rule",
          equation="m_worst = m_listed + tol ; mass margin = m_max - m_worst ; bay clearance = min_i(bay_i - "
                   "(size_i + tol)) (pack length along the bay) ; lead AWG number <= awg_max",
          inputs={"sku": "ASM-E2-PACK-SKU", "lim": "ASM-E2-PACK-LIMITS"}, assumes=["ASM-E2-PACK-SKU",
          "ASM-E2-PACK-LIMITS"])
def sku_check(sku, lim):
    worst = sku["mass_kg"] + sku["mass_tol_kg"]
    clear = [b - (s + sku["size_tol_m"]) for b, s in zip(lim["bay_m"], sku["size_m"])]
    return {"mass_worst_kg": worst, "mass_margin_kg": lim["mass_max_kg"] - worst, "bay_clear_min_m": min(clear),
            "bay_clear_m": clear, "lead_awg": sku["lead_awg"], "awg_max": lim["awg_max"]}


@kit.calc("CALC-E2-BUDGET-240", title="Budget sensitivity at the params cruise power (E1 240 W, D-49 / D-13 rule)",
          assumes=ASSUMES + ["ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN"],
          equation="as CALC-E2-BUDGET-BASE / -PESS with B1's level cruise power x k, k = P_params / P_B1 "
                   "(base 240 / 227.8 W; pessimistic B1 300.6 W x the same k) ; BATT_LOW count as CALC-E2-FAILSAFE",
          inputs={"m_b": "CL-A1-MASS-SIZED", "m_p": P + "requirements.mtow_gate_kg",
                  "p_par": P + "performance.cruise_power_w", **COMMON},
          units={"m_b": "kg", "m_p": "kg", "p_par": "W", **CU})
def budget_240(m_b, m_p, p_par, **kw):
    k = p_par / kw["pc_b"]
    base = budget(m_b, False, p_scale=k, **kw)
    pess = budget(m_p, True, p_scale=k, **kw)
    fs = failsafe_rows(pess["phases"], kw["ah"], kw["reserve"])
    return {"k": k, "cruise_min_base": base["cruise_min"], "cruise_min_pess": pess["cruise_min"],
            "cruise_w_base": base["cruise_w"], "cruise_w_pess": pess["cruise_w"], "cruise_a_pess": pess["cruise_a"],
            "low_mah": fs["low_mah"], "cruise_to_low_min": fs["cruise_to_low_min"]}


# ---------------------------------------------------------------- claims
def table_out(calc, title):
    return dict(calc=calc, output="phases", unit="-", how=f"{title}: compare each row with the DataFlash log "
                "(BAT.Curr, BAT.CurrTot) of a full mission; rows within +/-15 %.")


kit.claim("CL-E2-BUDGET-BASE-TABLE", "Phase table, base [phase, s, W, A, Ah]",
          **table_out("CALC-E2-BUDGET-BASE", "Base phase table"))
kit.claim("CL-E2-BUDGET-PESS-TABLE", "Phase table, pessimistic [phase, s, W, A, Ah]",
          **table_out("CALC-E2-BUDGET-PESS", "Pessimistic phase table"))
kit.claim("CL-E2-CRUISE-MIN-BASE", "Cruise after 2 min hover to the 20 % line, base", calc="CALC-E2-BUDGET-BASE",
          output="cruise_min", unit="min", limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="Full-mission flight (R-TEST-ORDER gate 9): land when BAT.CurrTot reaches 80 % of 6 500 mAh; logged "
              "cruise time >= this value.")
kit.claim("CL-E2-CRUISE-MIN-PESS", "Cruise after 2 min hover to the 20 % line, pessimistic",
          calc="CALC-E2-BUDGET-PESS", output="cruise_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="Same flight; also re-run this script with the twin's logged hover and cruise currents in place of the "
              "model (ASM-E2-HOVER-MARGIN, ASM-E2-CRUISE-AERO).")
kit.claim("CL-E2-HOVER-ONLY-MIN-PESS", "Hover-only sortie to the 20 % line, pessimistic",
          calc="CALC-E2-BUDGET-PESS", output="hover_only_min", unit="min",
          limit=(">=", P + "requirements.hover_time_min"),
          how="Tethered hover (R-TEST-ORDER gate 3): log BAT.CurrTot vs time; minutes to 5 200 mAh >= this value.")
kit.claim("CL-E2-HOVER-I-GATE", "Hover pack current at the gate, 5 m/s wind", calc="CALC-E2-BUDGET-PESS",
          output="hover_a", unit="A",
          how="Tethered hover at gate mass (ballast) with the 150 A watt meter; F1 sizes wires and the disconnect on it.")
kit.claim("CL-E2-CRUISE-I-PESS", "Cruise pack current, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="cruise_a", unit="A", how="Fixed-wing tune flights: mean BAT.Curr in level cruise at 16 m/s.")
PHASE_CLAIMS = [("climb", "Climb 0-50 m at 2 m/s"), ("trans_fwd", "Forward transition"),
                ("trans_back", "Back-transition"), ("descent", "Descent 50-0 m at 1 m/s")]
for key, label in PHASE_CLAIMS:
    tag = key.upper().replace("_", "-")
    kit.claim(f"CL-E2-I-{tag}-PESS", f"{label}: pack current, pessimistic (gate, 10 degC)",
              calc="CALC-E2-BUDGET-PESS", output=f"i_{key}_a", unit="A",
              how="DataFlash BAT.Curr mean over the phase on the full-mission log (T-E2-MISSION-LOG), within +/-15 %; "
                  "F1 sizes harness heating on the phase profile (ASM-F1-PROFILE).")
    kit.claim(f"CL-E2-T-{tag}-PESS", f"{label}: duration, pessimistic", calc="CALC-E2-BUDGET-PESS",
              output=f"t_{key}_s", unit="s", how="Phase duration on the full-mission log (MODE and QTUN messages).")
kit.claim("CL-E2-T-HOVER-PESS", "Mission hover: duration", calc="CALC-E2-BUDGET-PESS", output="t_hover_s", unit="s",
          how="Phase duration on the full-mission log.")
kit.claim("CL-E2-T-CRUISE-PESS", "Cruise to the 20 % line: duration, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="t_cruise_s", unit="s", how="As CL-E2-CRUISE-MIN-PESS x 60.")
kit.claim("CL-E2-I-MAX-PHASE-PESS", "Highest mission-phase pack current, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="i_max_phase_a", unit="A", limit=("<=", P + "performance.full_throttle_current_a"),
          how="Largest phase-mean BAT.Curr on the full-mission log; stays under the 100 A limiter.")
kit.claim("CL-E2-C-PEAK", "Peak discharge rate, all motors full", calc="CALC-E2-SAG", output="c_peak", unit="1/h",
          limit=("<=", 25.0),
          how="Limiter 100 A = 15.4C (unlimited momentary 120 A = 18.5C); any hobby 6500 pack with IR <= 5 mOhm/cell carries it (T-E2-IR). "
              "Limit 25C = realistic continuous rating of a hard-case pack labelled 100C+.")
kit.claim("CL-E2-SAG-BRACKET", "E1's worst/fresh thrust factor lies inside E2's physical bracket (D-35)",
          calc="CALC-E2-SAG", output="e1_bracket_margin", unit="-", limit=(">=", 0.0),
          note="D-35 resolved: E2 adopts E1's station model (CL-E1-SAG-FACTOR, CL-E1-TW-WORST) as the one worst-state "
               "claim. The limiter binds in every pack state, so the pack current is fixed at 100 A and thrust "
               "follows power (lower bound, thrust ~ V) or the ideal rotor (upper, ~ V^(2/3)); E1 lies between. "
               "Retires CL-E2-SAG-F-WORST and CL-E2-TW-SAG-WORST (the (V/14.8)^2 rule counted the sag twice)",
          how="T-E1-STAND fresh and worst-state runs: measured thrust ratio between the measured bus-voltage ratio "
              "and its 2/3 power.")
kit.claim("CL-E2-LIMITER-BINDS-WORST", "Unlimited pack current at 20 % charge, 10 degC (limiter still binds)",
          calc="CALC-E2-SAG", output="i_unlim_res20_cold", unit="A",
          limit=(">=", P + "performance.full_throttle_current_a"),
          how="Same stand run with Q_M_BAT_CURR_MAX disabled for one 1 s punch (props on the stand only): pack "
              "current at full duty above 100 A. If it is not, the V^2 rule applies below the limiter and D-35 "
              "re-opens.")
kit.claim("CL-E2-V-BUS-WORST", "Bus voltage at 100 A, 20 % charge, 10 degC pack", calc="CALC-E2-SAG",
          output="v_res20_cold", unit="V",
          how="Logged BAT.Volt during a full-throttle punch on the cold-pack stand run (T-E2-IR); F4 sets "
              "BATT_FS_VOLTSRC 1 (sag-compensated) and Q_M_BAT_VOLT_MIN below it.")
kit.claim("CL-E2-SAG-V-WORST", "Cell sag at 120 A, 20 % charge, 10 degC", calc="CALC-E2-SAG",
          output="sag_v_per_cell_worst", unit="V",
          how="Load-step IR test (T-E2-IR) scaled to 100 A; F4 uses it for BATT_FS_VOLTSRC 1 and Q_M_BAT_VOLT_MIN.")
kit.claim("CL-E2-PACK-T-END", "Pack temperature at landing, worst morning (adiabatic)", calc="CALC-E2-HEAT",
          output="t_end_max_c", unit="degC", limit=("<=", 50.0), verifies=["R-THERMAL"],
          how="IR thermometer on the pack face at landing; E3 adds the pod's heat path. 50 degC leaves 10 K to the "
              "usual 60 degC LiPo discharge limit.")
kit.claim("CL-E2-PACK-HEAT-HOVER", "Pack internal heat in hover, cold pack", calc="CALC-E2-HEAT",
          output="p_hover_cold_w", unit="W", how="E3 input; check by I^2 R from the measured IR and hover current.")
kit.claim("CL-E2-PACK-LARGEST", "Largest candidate pack passing gate, mission and current", calc="CALC-E2-PACK-TRADE",
          output="largest_passing_ah", unit="Ah", limit=(">=", P + "battery.capacity_ah"),
          how="Re-run with the weighed pack masses; the 6.5 Ah choice stands while it is the largest passing pack.")
kit.claim("CL-E2-BATT-CRT-MAH", "BATT_CRT_MAH (critical: QLAND)", calc="CALC-E2-FAILSAFE", output="crt_mah",
          unit="mAh", verifies=["R-FAILSAFES"],
          how="SITL and bench (props off): set BATT_CAPACITY 6500, inject current, confirm QLAND at this count.")
kit.claim("CL-E2-BATT-LOW-MAH", "BATT_LOW_MAH (low: QRTL)", calc="CALC-E2-FAILSAFE", output="low_mah", unit="mAh",
          verifies=["R-FAILSAFES"], how="Same bench test: QRTL at this count; landing then ends above BATT_CRT_MAH.")
kit.claim("CL-E2-CRUISE-TO-LOW-PESS", "Mission cruise before BATT_LOW triggers, pessimistic currents",
          calc="CALC-E2-FAILSAFE", output="cruise_to_low_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="SITL with the logged currents: QRTL must not trigger before 5 min of cruise.")
kit.claim("CL-E2-SORTIES-WINDOW", "Full-mission sorties the 3 h window allows", calc="CALC-E2-TESTDAY",
          output="sorties_window", unit="-", how="Count logged sorties on the first full test day; I2 plans on it.")
kit.claim("CL-E2-SORTIES-PACKS", "Sorties per day with the packs on order", calc="CALC-E2-TESTDAY",
          output="sorties_current_packs", unit="-", how="= min(packs owned, window); one full pack per sortie.")
kit.claim("CL-E2-CHARGE-MIN", "Charge time per pack from the 20 % line", calc="CALC-E2-TESTDAY",
          output="charge_min_per_pack", unit="min", how="Time the first charge on the HTRC C150 (T-E2-CAPACITY).")
kit.claim("CL-E2-CHARGE-H-4", "Attended charge time for 4 packs, one port", calc="CALC-E2-TESTDAY",
          output="charge_h_4_packs", unit="h", limit=("<=", 5.0),
          how="Sum of logged charge times after a test day; must fit one attended afternoon (<= 5 h).")
kit.claim("CL-E2-WINDOW-USED", "Window minutes used by the planned sorties (2 packs, D-12)", calc="CALC-E2-TESTDAY",
          output="window_used_min", unit="min", limit=("<=", 180.0),
          how="Log take-off and landing times on the first test day; I2 plans the day on it.")
kit.claim("CL-E2-SKU-MASS-MARGIN", "Named pack (listed mass + tolerance) under the D-58 line of 601 g",
          calc="CALC-E2-SKU-CHECK", output="mass_margin_kg", unit="kg", limit=(">=", 0.0), verifies=["R-PACK-MASS"],
          parts=["PWR-001"],
          how="T-E2-WEIGH: every pack <= 0.601 kg on a 1 g scale, leads included (pack_log.csv).")
kit.claim("CL-E2-SKU-BAY-CLEAR", "Named pack body (listed + 3 mm) inside the D2 bay, tightest axis",
          calc="CALC-E2-SKU-CHECK", output="bay_clear_min_m", unit="m", limit=(">=", 0.0), parts=["PWR-001"],
          how="T-E2-WEIGH step 3: calipers L x W x H against the bay 160 x 52 x 53 mm; lead exit routed per D2.")
kit.claim("CL-E2-SKU-LEAD-AWG", "Named pack discharge-lead gauge (AWG number)", calc="CALC-E2-SKU-CHECK",
          output="lead_awg", unit="-", limit=("<=", 10.0), parts=["PWR-001"],
          note="10 AWG inferred from the EC5 plug (the page does not state it); I1 confirms at order, E2 on arrival",
          how="T-E2-WEIGH step 3a: read the print on the lead insulation, or strip 5 mm of the cut-off end at "
              "re-termination and measure the bundle (10 AWG ~2.6 mm, 12 AWG ~2.1 mm).")
kit.claim("CL-E2-CRUISE-MIN-BASE-240", "Cruise after 2 min hover, base, at the params' 240 W (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_min_base", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"),
          how="As CL-E2-CRUISE-MIN-BASE; the first tune flight's logged cruise current decides between B1 and E1.")
kit.claim("CL-E2-CRUISE-MIN-PESS-240", "Cruise after 2 min hover, pessimistic, at the params' 240 W (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_min_pess", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), how="As CL-E2-CRUISE-MIN-PESS.")
kit.claim("CL-E2-CRUISE-TO-LOW-PESS-240", "Cruise before BATT_LOW (2600 mAh), pessimistic, at 240 W (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_to_low_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"),
          how="SITL with the logged currents, as CL-E2-CRUISE-TO-LOW-PESS.")


# ---------------------------------------------------------------- measured packs (T-E2-WEIGH)
def read_pack_log(path):
    """Rows of pack_log.csv with a mass entered; empty until the ~20 Nov order arrives."""
    import csv
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("mass_g") or "").strip()]


PACK_LOG = HERE / "pack_log.csv"
WEIGHED = read_pack_log(PACK_LOG)
PACK_ACCEPT_KG = 0.601      # D-58: above 601 g the first-build overrun is not covered (= ASM-E2-PACK-LIMITS)
if WEIGHED:
    m_meas = max(float(r["mass_g"]) for r in WEIGHED) / 1000.0
    kit.claim("CL-E2-PACK-MASS", "Flight pack mass, heaviest weighed pack", value=m_meas, unit="kg",
              limit=("<=", PACK_ACCEPT_KG), verifies=["R-PACK-MASS"], cites=["SRC-E2-OVONIC-LISTINGS"],
              how="Weighed on arrival (T-E2-WEIGH, pack_log.csv). A3 replaces the 550 g line with this value; "
                  "A1 may then set checked on SRC-OVONIC-4S6500.")
    kit.test("T-E2-WEIGH", "Weigh and measure every pack on arrival", verifies=["CL-E2-PACK-MASS", "CL-E2-SKU-MASS-MARGIN", "CL-E2-SKU-BAY-CLEAR", "CL-E2-SKU-LEAD-AWG"], state="run",
             result="pass" if m_meas <= PACK_ACCEPT_KG else "fail", measured=m_meas,
             date=max(r.get("received", "") for r in WEIGHED), evidence="redesign/team/E2/pack_log.csv",
             procedure="1 g scale, calipers L x W x H incl. lead exit; one row per pack in pack_log.csv.")
else:
    kit.claim("CL-E2-PACK-MASS", "Flight pack mass carried in the budget (not yet weighed)", value=0.55, unit="kg",
              limit=("<=", PACK_ACCEPT_KG), verifies=["R-PACK-MASS"], status="UNVERIFIED",
              cites=["SRC-E2-OVONIC-120C-EC5", "SRC-E2-OVONIC-LISTINGS"],
              note="named SKU (D-58): Ovonic 120C 4S 6500 hard case EC5, listed 551 +/- 5 g; 0.55 kg stays the "
                   "carried value until weighed",
              how="Weigh each pack on arrival on a 1 g scale (T-E2-WEIGH) and enter it in pack_log.csv, then re-run. "
                  "Accept <= 0.601 kg (D-58); 0.551-0.601 kg: A3 replaces the 550 g line; 0.602-0.613 kg: A1 "
                  "decides (A3-R6 still covers the overrun to 613 g); > 0.613 kg: return the pair.")
    kit.test("T-E2-WEIGH", "Weigh and measure every pack on arrival", verifies=["CL-E2-PACK-MASS", "CL-E2-SKU-MASS-MARGIN", "CL-E2-SKU-BAY-CLEAR", "CL-E2-SKU-LEAD-AWG"], state="planned",
             procedure="1 g scale; calipers L x W x H incl. lead exit; one row per pack (E2-P1, E2-P2) in "
                       "redesign/team/E2/pack_log.csv, then re-run this script and build_graph.py.")
kit.test("T-E2-CAPACITY", "Discharge capacity test at 1C", verifies=["CL-E2-CRUISE-MIN-PESS", "CL-E2-CHARGE-MIN"],
         state="planned", procedure="Charger discharge mode is limited in power: discharge through the thrust stand "
         "at ~6.5 A to 3.5 V/cell under load, log mAh with the watt meter; pass >= 6.0 Ah (R-PACK-MASS).")
kit.test("T-E2-IR", "Pack resistance by load step", verifies=["CL-E2-SAG-BRACKET", "CL-E2-V-BUS-WORST", "CL-E2-SAG-V-WORST", "CL-E2-C-PEAK"],
         state="planned", procedure="Thrust stand, one motor: rest voltage, then 20 A step; R = dV / dI after 2 s; "
         "repeat at 10 degC (pack 1 h in a fridge, bagged). Pass <= 5 mOhm/cell at 25 degC.")
kit.test("T-E2-MISSION-LOG", "Full-mission current log", verifies=["CL-E2-CRUISE-MIN-BASE", "CL-E2-HOVER-I-GATE",
         "CL-E2-CRUISE-I-PESS", "CL-E2-PACK-T-END", "CL-E2-I-CLIMB-PESS", "CL-E2-I-TRANS-FWD-PESS",
         "CL-E2-I-TRANS-BACK-PESS", "CL-E2-I-DESCENT-PESS", "CL-E2-I-MAX-PHASE-PESS"], state="planned",
         procedure="DataFlash BAT messages; IR thermometer on pack before/after; compare row by row with the phase table.")


if __name__ == "__main__":
    r_param = kit.value(P + "electrical.r_ext_mohm") / 1000.0
    if abs(r_param - R_EXT_MIRROR_OHM) > 1e-9:
        raise SystemExit(f"ASM-E2-R-EXT mirror {R_EXT_MIRROR_OHM} ohm != params electrical.r_ext_mohm {r_param} ohm: "
                         "update R_EXT_MIRROR_OHM and re-run")
    kit.write()
    for cid in ("CALC-E2-BUDGET-BASE", "CALC-E2-BUDGET-PESS"):
        o = kit.nodes[cid]["outputs"]
        print(f"\n{cid}: R_pack {o['r_pack']*1000:.1f} mOhm, hover {o['hover_w']:.0f} W / {o['hover_a']:.1f} A, "
              f"cruise {o['cruise_w']:.0f} W / {o['cruise_a']:.1f} A, avail {o['ah_avail']:.2f} Ah")
        for name, t, p, i, ah in o["phases"]:
            print(f"  {name:<22} {t:7.0f} s {p:6.0f} W {i:6.1f} A {ah*1000:6.0f} mAh")
        print(f"  cruise {o['cruise_min']:.1f} min, hover-only {o['hover_only_min']:.1f} min, flight {o['flight_min']:.1f} min")
    print("\nSAG", {k: round(v, 3) for k, v in kit.nodes["CALC-E2-SAG"]["outputs"].items()})
    print("HEAT", {k: round(v, 2) for k, v in kit.nodes["CALC-E2-HEAT"]["outputs"].items()})
    for r in kit.nodes["CALC-E2-PACK-TRADE"]["outputs"]["table"]:
        print("TRADE", r)
    print("FAILSAFE", kit.nodes["CALC-E2-FAILSAFE"]["outputs"])
    print("TESTDAY", {k: round(v, 2) for k, v in kit.nodes["CALC-E2-TESTDAY"]["outputs"].items()})
    for cid in ("CALC-E2-BUDGET-BASE", "CALC-E2-BUDGET-PESS"):
        print(cid, "E2 cross-check cruise W", round(kit.nodes[cid]["outputs"]["cruise_w_e2_model"], 1))
    print("SKU", kit.nodes["CALC-E2-SKU-CHECK"]["outputs"])
    print("AT 240 W", {k: round(v, 3) for k, v in kit.nodes["CALC-E2-BUDGET-240"]["outputs"].items()})
    print("PACK LOG", f"{len(WEIGHED)} weighed pack(s)" if WEIGHED else "no pack weighed yet (order ~20 Nov)")
