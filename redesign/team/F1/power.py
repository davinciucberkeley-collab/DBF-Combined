"""F1 power distribution: main disconnect, wire gauges with derating, voltage drop, sensing, UBEC, protection.

Run:  python -I redesign/team/F1/power.py      -> claims.json, data/derating.csv, data/gauge_sweep.csv
Then: python -I redesign/team/F1/draw_schematic.py ; python -I redesign/proofs/build_graph.py

Wire model (CALC-F1-WIRES), per metre of conductor, Python standard library only:
  R(T) = rho_Cu * k_strand / A_awg * (1 + alpha (T - 20))                     IEC 60028 annealed copper
  steady:   I^2 R(T) = h(T) * pi * OD * (T - T_amb)                           solved by iteration
  h = f_enc * f_pair * (h_conv Churchill-Chu horizontal cylinder + h_rad, eps 0.9)
  transient: C' dT/dt = I(t)^2 R(T) - h pi OD (T - T_amb),  C' = m_Cu c_Cu + m_sil c_sil, dt 0.25 s
The mission current profile is E2's pessimistic phase table (ASM-F1-PROFILE) with short punches inserted after each
transition (limited 100 A in the normal case, 120 A unlimited / 51.6 A single-ESC in the fault case).
"""
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])

PARTS_MAIN = ["PWR-001", "PWR-002", "PWR-003", "PWR-004"]
ESC_IDS = ["PRP-002-UR", "PRP-002-UL", "PRP-002-LR", "PRP-002-LL"]

# ---------------------------------------------------------------- sources
kit.source("SRC-F1-AS150U-LCSC", "Amass AS150U-M.055 15 Ohm (LCSC datasheet listing)", "datasheet",
           url="https://lcsc.com/datasheet/lcsc_datasheet_2409041651_Changzhou-Amass-Elec-AS150U-M-055-15R_C30170236.pdf",
           where="part name gives the anti-spark pre-charge resistor, 15 Ohm",
           note="ratings not read from the PDF (search summary only); open before ordering", status="UNVERIFIED")
kit.source("SRC-F1-SPEEDYBEE-WING", "SpeedyBee F405 WING APP manual (EN)", "datasheet",
           url="https://www.kiwiquads.co.nz/wp-content/uploads/SpeedyBee_F405_WING_APP_Manual-EN.pdf",
           where="PDB board: current sensor 90 A continuous / 215 A peak, ArduPilot 50 A/V; servo BEC (Vx) 4.5 A "
                 "continuous / 5.5 A peak (spec sheet; manual says 5 A); FC BEC 5 V 2.4 A",
           note="search summary 2026-11-09, manual PDF not opened; candidate FC only (F3 decides)", status="UNVERIFIED")
kit.source("SRC-F1-EMAX-ES3054", "EMAX ES3054 / ES3054HV listings", "web",
           url="https://alofthobbies.com/products/emax-es3054-hv-servo-4-7kg-65-27-oz-in-13-sec-20-3-grams",
           where="17-20 g metal-gear servo, 3.5 kgf cm at 6 V; HV listing: max current 1.0 A (1.3 A high-torque "
                 "setting); no stall-current figure for the standard version",
           note="the class D6 is choosing from (>= 3.04 kgf cm, B2 CR-B2-05); stall current to be measured",
           status="UNVERIFIED")
kit.source("SRC-F1-IEC60028", "IEC 60028 international standard of resistance for copper", "standard",
           url="https://webstore.iec.ch/publication/1",
           where="annealed copper 1.7241e-8 Ohm m at 20 degC, alpha 0.00393 /K")
kit.source("SRC-F1-INCROPERA", "Incropera & DeWitt, Fundamentals of Heat and Mass Transfer, 6th ed., eq. 9.34",
           "book", where="Churchill-Chu correlation, free convection from a long horizontal cylinder")

# ---------------------------------------------------------------- assumptions
kit.assumption("ASM-F1-PROFILE", "Pessimistic mission current profile",
               "[phase, duration s, pack current A] at the 2.6 kg gate, 10 degC pack, from E2's CALC-E2-BUDGET-PESS "
               "phase table (team/E2/ENERGY.md)",
               basis="copied from E2's stored outputs 2026-11-09 (CR-E2-14): hover 29.9 A, transition 42.9 A for "
                     "20 s, cruise 29.8 A. E2 to emit the phases as claims so this link is live (CR-F1-04)",
               value=[["ground", 180, 0.41], ["climb 0-50 m", 25, 35.18], ["hover", 120, 29.89],
                      ["transition forward", 20, 42.92], ["cruise", 308, 29.78], ["back-transition", 20, 39.60],
                      ["descent", 50, 29.89]],
               unit="s,A", status="UNVERIFIED", cites=["SRC-K09-CARD"])
kit.assumption("ASM-F1-PUNCH", "Short-time current cases",
               "durations: limited full-throttle punch 5 s, unlimited momentary 5 s, single-ESC asymmetric burst 2 s",
               basis="P:electrical.peak_current_a says < 5 s; a single motor at full throttle while the others are low "
                     "(yaw/roll saturation) lasts about one control correction; F4 to confirm from SITL",
               value=[5.0, 5.0, 2.0], unit="s", status="PROPOSED")
kit.assumption("ASM-F1-GAUGES", "Chosen gauges",
               "AWG for [main pack path, ESC power lead, ESC alternative checked, UBEC feed, UBEC servo bus]",
               basis="F1 choice; the alternative (18 AWG) is computed to answer CR-A3-06", value=[8, 16, 18, 20, 20],
               unit="AWG", status="PROPOSED")
kit.assumption("ASM-F1-LENGTHS", "Conductor lengths, one way",
               "[main path pack plug to bus, ESC lead bus to ESC pads, UBEC feed, servo bus] per conductor",
               basis="pod: AS150U at the hatch, bus 0.12-0.15 m away; ESC lead 0.5 m = pod to fin at y 0.32 m plus "
                     "~0.13 m along the fin to the ESC pad (A3 mass model). F2 replaces with the routed lengths",
               value=[0.15, 0.50, 0.15, 0.35], unit="m", status="PROPOSED")
kit.assumption("ASM-F1-WIRE-OD", "Silicone wire outside diameter by gauge",
               "[AWG, OD mm] for high-strand silicone hobby wire",
               basis="typical maker tables (BNTECHGO, Turnigy) +/-0.2 mm; measure the reel",
               value=[[8, 6.0], [10, 4.8], [12, 4.0], [14, 3.2], [16, 2.6], [18, 2.0], [20, 1.7], [22, 1.4]],
               unit="AWG,mm", status="UNVERIFIED")
kit.assumption("ASM-F1-COOLING", "Cooling derates",
               "[f_pod, f_channel, f_pair, emissivity]: f_pod 1.0 in the vented pod (still air); f_channel 0.75 "
               "for a lead in a tape-covered surface groove in the wing; f_pair 0.85 for a twisted +/- pair "
               "(pod only; in the wing + and - lie in two grooves 5 mm apart, f 1.0); silicone emissivity 0.9",
               basis="engineering judgement: a covered groove halves convection but keeps radiation to the tape and "
                     "foam (~0.75 overall); a twisted pair shields ~15 % of each conductor's surface. Prop wash over "
                     "the wing in hover is not credited. T-F1-WIRE-HEAT measures it",
               value=[1.0, 0.75, 0.85, 0.9], unit="-", status="UNVERIFIED", cites=["SRC-F1-INCROPERA"])
kit.assumption("ASM-F1-TRANSIENT-LIMIT", "Short-time wire temperature rise limit 30 degC",
               "conductor rise <= 30 degC for any case shorter than 60 s",
               basis="keeps the conductor <= 60 degC at the 30 degC ambient ceiling: 14 degC under the XPS service "
                     "limit (~74 degC) and 20 degC under PETG Tg; silicone itself is rated 200 degC. P18's 10 degC "
                     "applies to the continuous current (CR-F1-01 asks A2 to state this)",
               value=30.0, unit="degC", status="PROPOSED")
kit.assumption("ASM-F1-R-CONTACT", "Contact resistance per mated contact",
               "AS150U contact 0.8 mOhm (two in the path)",
               basis="reseller values 0.40 and <= 0.8 mOhm; the larger is used", value=0.0008, unit="ohm",
               status="UNVERIFIED", cites=["SRC-J1-AS150U"])
kit.assumption("ASM-F1-R-BOARD", "Current shunt, board copper and solder joints",
               "0.6 mOhm in the common path (sensor shunt ~0.25, copper and four solder joints ~0.35)",
               basis="typical 0.2-0.3 mOhm hobby PDB shunts; measured by T-F1-DROP", value=0.0006, unit="ohm",
               status="UNVERIFIED")
kit.assumption("ASM-F1-SERVO-STALL", "Servo stall current 1.3 A at 6 V",
               "per elevon servo, 17-20 g metal-gear class", basis="ES3054HV listing max current 1.3 A; micro "
               "metal-gear servos 1.0-1.5 A; measured by T-F1-SERVO-STALL on the servo D6 picks",
               value=1.3, unit="A", status="UNVERIFIED", cites=["SRC-F1-EMAX-ES3054"])
kit.assumption("ASM-F1-SENSOR-TOL", "Current-sensor tolerance 5 %",
               "BATT_AMP_PERVLT calibrated within +/-5 % at 24-30 A (R-AVIONICS-POWER)",
               basis="requirement value; the 100 A limiter acts on the sensed current", value=0.05, unit="-",
               status="PROPOSED")
kit.assumption("ASM-F1-ESC-CAP", "Bus capacitance per ESC 1 000 uF",
               "LANRC 45 A input capacitor plus the added low-ESR 680 uF at each ESC (0.5 m leads)",
               basis="leads beyond ~0.15 m need added capacitance at the ESC; value = ripple practice, checked by "
                     "T-F1-RIPPLE", value=0.001, unit="F", status="PROPOSED")

# ---------------------------------------------------------------- constants (physics, not design numbers)
RHO_CU, ALPHA, K_STRAND = 1.7241e-8, 0.00393, 1.02           # IEC 60028; stranding lay factor
DENS_CU, C_CU, DENS_SIL, C_SIL = 8960.0, 385.0, 1150.0, 1200.0
SIGMA = 5.670e-8


def awg_area(n):
    d = 0.127e-3 * 92 ** ((36 - n) / 39)
    return math.pi / 4 * d * d


def h_total(ts, ta, od, f_enc, f_pair, eps):
    dt = max(ts - ta, 0.05)
    tf = (ts + ta) / 2 + 273.15
    nu, alph, k, pr = 1.6e-5, 2.25e-5, 0.0263, 0.71              # air ~30-40 degC
    ra = 9.81 / tf * dt * od ** 3 / (nu * alph)
    nu_d = (0.6 + 0.387 * ra ** (1 / 6) / (1 + (0.559 / pr) ** (9 / 16)) ** (8 / 27)) ** 2
    hc = nu_d * k / od
    hr = eps * SIGMA * ((ts + 273.15) ** 4 - (ta + 273.15) ** 4) / dt
    return f_enc * f_pair * (hc + hr)


def wire_props(awg, od_table):
    od = dict((int(a), m) for a, m in od_table)[awg] * 1e-3
    a = awg_area(awg)
    m_cu = a * DENS_CU
    m_sil = (math.pi / 4 * od * od - a / 0.9) * DENS_SIL          # conductor bundle fill ~0.9
    return {"od": od, "a": a, "r20": RHO_CU * K_STRAND / a, "c": m_cu * C_CU + m_sil * C_SIL,
            "mass_gpm": (m_cu + m_sil) * 1000}


def steady_rise(i, w, ta, cool):
    ts = ta + 1
    for _ in range(300):
        q = i * i * w["r20"] * (1 + ALPHA * (ts - 20))
        new = ta + q / (h_total(ts, ta, w["od"], *cool) * math.pi * w["od"])
        ts = 0.5 * ts + 0.5 * new
    return ts - ta


def profile_peak(segments, w, ta, cool, dt=0.25):
    t = ta
    peak = 0.0
    for dur, i in segments:
        steps = max(1, int(round(dur / dt)))
        for _ in range(steps):
            q = i * i * w["r20"] * (1 + ALPHA * (t - 20))
            loss = h_total(t, ta, w["od"], *cool) * math.pi * w["od"] * (t - ta)
            t += (q - loss) * dt / w["c"]
            peak = max(peak, t - ta)
    return peak


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-F1-I-DESIGN", title="Design currents for the pack path",
          equation="I_cont = max(I_hover, I_cruise, P_vclimb / V_nom) ; I_short = max profile phase <= 60 s ; "
                   "I_req = k I",
          inputs={"i_hover": "CL-E2-HOVER-I-GATE", "i_cruise": "CL-E2-CRUISE-I-PESS", "p_climb": "CL-B1-VCLIMB-P",
                  "v": "P:battery.v_nom", "k": "P:requirements.disconnect_factor", "profile": "ASM-F1-PROFILE",
                  "ilim": "P:performance.full_throttle_current_a", "tol": "ASM-F1-SENSOR-TOL"},
          units={"i_hover": "A", "i_cruise": "A", "p_climb": "W", "v": "V", "ilim": "A"})
def design_currents(i_hover, i_cruise, p_climb, v, k, profile, ilim, tol):
    i_cont = max(i_hover, i_cruise, p_climb / v)
    i_short = max(a for _, s, a in profile if s <= 60)
    return {"i_cont_a": i_cont, "i_req_cont_a": k * i_cont, "i_short_a": i_short, "i_req_short_a": k * i_short,
            "i_lim_worst_a": ilim / (1 - tol)}


def _segments(profile, kind, punch_t, i_punch, scale):
    seg = []
    for name, s, a in profile:
        seg.append((s, a * scale))
        if kind and "transition" in name:
            seg.append((punch_t, i_punch))
    return seg


@kit.calc("CALC-F1-WIRES", title="Wire derating: steady rise, mission-profile peak, drop, mass",
          equation="see module docstring; ESC lead current = I_pack / n x 2s/(1+s) (heavier pair at the hover "
                   "split s); drop = I (R_contacts + R_board + 2 L R'(T)) / V_nom",
          inputs={"i_cont": "CL-F1-I-CONT", "profile": "ASM-F1-PROFILE", "punch": "ASM-F1-PUNCH",
                  "gauges": "ASM-F1-GAUGES", "lengths": "ASM-F1-LENGTHS", "od": "ASM-F1-WIRE-OD",
                  "cool": "ASM-F1-COOLING", "amb": "P:env.ambient_design_c", "n": "P:propulsion.n_motors",
                  "split": "P:requirements.hover_split_max", "ilim": "P:performance.full_throttle_current_a",
                  "ipeak": "P:electrical.peak_current_a", "i_esc_lim": "P:propulsion.current_max_per_motor_a",
                  "i_esc_asym": "CL-E1-IMAX-168-55", "r_contact": "ASM-F1-R-CONTACT", "r_board": "ASM-F1-R-BOARD",
                  "v": "P:battery.v_nom", "i_servo_bus": "CL-F1-SERVO-STALL-BUS", "ubec_eta_in": "ASM-F1-UBEC-IN"},
          units={"ilim": "A", "ipeak": "A", "i_esc_lim": "A", "v": "V"})
def wires(i_cont, profile, punch, gauges, lengths, od, cool, amb, n, split, ilim, ipeak, i_esc_lim, i_esc_asym,
          r_contact, r_board, v, i_servo_bus, ubec_eta_in):
    ta = max(amb)
    share = 2 * split / (1 + split) / n
    t_lim, t_mom, t_asym = punch
    g_main, g_esc, g_esc_alt, g_feed, g_bus = gauges
    l_main, l_esc, l_feed, l_bus = lengths
    f_pod, f_chan, f_pair, eps = cool
    cools = {"main": (f_pod, f_pair, eps), "esc": (f_chan, 1.0, eps), "esc18": (f_chan, 1.0, eps),
             "feed": (f_pod, f_pair, eps), "bus": (f_chan, 1.0, eps)}
    out = {}
    runs = {"main": (g_main, l_main, 1.0, ilim, ipeak, t_mom),
            "esc": (g_esc, l_esc, share, i_esc_lim, i_esc_asym, t_asym),
            "esc18": (g_esc_alt, l_esc, share, i_esc_lim, i_esc_asym, t_asym)}
    for key, (g, length, scale, i_norm, i_fault, t_fault) in runs.items():
        w = wire_props(g, od)
        cool = cools[key]
        i_c = i_cont * scale
        out[f"{key}_awg"] = g
        out[f"{key}_i_cont_a"] = i_c
        out[f"{key}_rise_c"] = steady_rise(i_c, w, ta, cool)
        out[f"{key}_peak_normal_c"] = profile_peak(_segments(profile, True, t_lim, i_norm, scale), w, ta, cool)
        out[f"{key}_peak_fault_c"] = profile_peak(_segments(profile, True, t_fault, i_fault, scale), w, ta, cool)
        t_hot = ta + out[f"{key}_rise_c"]
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (t_hot - 20)) * 1e3
        out[f"{key}_mass_g"] = 2 * length * w["mass_gpm"] * (1 if key == "main" else n)
        out[f"{key}_od_mm"] = w["od"] * 1e3
    # UBEC feed and servo bus: steady at their worst continuous current (servo stall)
    i_feed = i_servo_bus * 6.0 / (ubec_eta_in * v)
    for key, g, length, i in (("feed", g_feed, l_feed, i_feed), ("bus", g_bus, l_bus, i_servo_bus)):
        w = wire_props(g, od)
        cool = cools[key]
        out[f"{key}_awg"], out[f"{key}_i_cont_a"] = g, i
        out[f"{key}_rise_c"] = steady_rise(i, w, ta, cool)
        out[f"{key}_mass_g"] = 2 * length * w["mass_gpm"]
    # resistance pack terminals -> ESC pads, as one equivalent common resistance (four branches in parallel)
    r_common = 2 * r_contact + r_board + out["main_r_loop_mohm"] * 1e-3
    r_branch = out["esc_r_loop_mohm"] * 1e-3
    out["r_ext_mohm"] = (r_common + r_branch / n) * 1e3
    out["drop_cont_pct"] = 100 * (i_cont * r_common + i_cont * share * r_branch) / v
    out["drop_peak_pct"] = 100 * (ilim * r_common + i_esc_lim * r_branch) / v
    out["main_loss_w_cont"] = i_cont ** 2 * r_common
    return out


kit.assumption("ASM-F1-UBEC-IN", "UBEC efficiency 0.85", "switching UBEC, 4S in, 6 V out",
               basis="typical buck converter at 1-5 A", value=0.85, unit="-", status="PROPOSED")

kit.assumption("ASM-F1-PACKLEAD", "Pack's own leads: gauge and length after re-termination",
               "[assumed maker gauge AWG, alternative gauge AWG, length one way m]",
               basis="the Ovonic listing does not give the lead gauge (open the product sheet / measure); 4S 6500 "
                     "130C packs ship with 10 or 12 AWG. Length: D2 CR-D2-07 needs >= 90 mm from the pack aft face to "
                     "the parked connector; cut to 0.10 m when the AS150U is fitted",
               value=[10, 12, 0.10], unit="AWG,AWG,m", status="UNVERIFIED", cites=["SRC-OVONIC-4S6500"])
kit.assumption("ASM-F1-PACKLEAD-LIMIT", "Pack lead steady rise limit 20 degC",
               "steady conductor rise <= 20 degC at the continuous design current for the pack's own leads",
               basis="the leads are bought with the pack and conduct heat into the cells: conductor <= 50 degC at the "
                     "30 degC ambient ceiling keeps the cell tabs under the 60 degC LiPo discharge limit. P18's 10 degC "
                     "applies to the aircraft-side wiring F1 sizes (CR-F1-15 asks A2 to state the scope)",
               value=20.0, unit="degC", status="PROPOSED")


@kit.calc("CALC-F1-PACKLEAD", title="Pack's own leads: steady and mission-peak rise",
          equation="same wire model as CALC-F1-WIRES, pod still air, side-by-side pair (f_pair)",
          inputs={"i_cont": "CL-F1-I-CONT", "lead": "ASM-F1-PACKLEAD", "profile": "ASM-F1-PROFILE",
                  "punch": "ASM-F1-PUNCH", "od": "ASM-F1-WIRE-OD", "cool": "ASM-F1-COOLING",
                  "amb": "P:env.ambient_design_c", "ipeak": "P:electrical.peak_current_a"},
          units={"amb": "degC", "ipeak": "A"})
def packlead(i_cont, lead, profile, punch, od, cool, amb, ipeak):
    ta = max(amb)
    f_pod, _, f_pair, eps = cool
    c = (f_pod, f_pair, eps)
    g, g_alt, length = lead
    out = {}
    for key, awg in (("lead", int(g)), ("lead_alt", int(g_alt))):
        w = wire_props(awg, od)
        out[f"{key}_awg"] = awg
        out[f"{key}_rise_c"] = steady_rise(i_cont, w, ta, c)
        out[f"{key}_peak_fault_c"] = profile_peak(_segments(profile, True, punch[1], ipeak, 1.0), w, ta, c)
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (ta + out[f"{key}_rise_c"] - 20)) * 1e3
    return out


@kit.calc("CALC-F1-SERVO-BEC", title="Servo supply requirement",
          equation="I_req = k_bec x n_servo x I_stall", inputs={"k": "P:requirements.ubec_factor",
                                                                "i_stall": "ASM-F1-SERVO-STALL"},
          units={"i_stall": "A"})
def servo_bec(k, i_stall):
    return {"i_req_a": k * 2 * i_stall, "i_bus_stall_a": 2 * i_stall}


@kit.calc("CALC-F1-PRECHARGE", title="Anti-spark pre-charge time",
          equation="tau = R_pre x n x C_esc ; 3 tau to 95 % ; I_inrush = V_full / R_pre",
          inputs={"n": "P:propulsion.n_motors", "c": "ASM-F1-ESC-CAP", "cells": "P:battery.cells_s"},
          units={"c": "F"})
def precharge(n, c, cells):
    r_pre = 15.0                                   # Ohm, AS150U-M.055 15R (SRC-F1-AS150U-LCSC)
    return {"t95_ms": 3 * r_pre * n * c * 1e3, "i_inrush_a": cells * 4.2 / r_pre}


MASS_ITEMS = [["AS150U aircraft half + heat-shrink", 10.0], ["bus PDB board (no sensor)", 6.0],
              ["UBEC 6 V >= 6 A", 13.0], ["mini blade fuse + holder", 3.0], ["4 x 680 uF caps", 8.0]]
kit.assumption("ASM-F1-MASS-ITEMS", "Power boxes masses (excluding the pack and the FC power board)",
               "[item, g]", basis="listing weights; weigh on arrival (A3)", value=MASS_ITEMS, unit="g",
               status="UNVERIFIED")


@kit.calc("CALC-F1-MASS", title="Power subsystem mass excluding the pack",
          equation="sum(items) + main path wire mass", inputs={"items": "ASM-F1-MASS-ITEMS",
                                                               "main_wire": "CL-F1-MAIN-MASS",
                                                               "alloc": "P:mass.allocation_g.power",
                                                               "pack": "P:battery.mass_kg"},
          units={"alloc": "g", "pack": "kg"})
def power_mass(items, main_wire, alloc, pack):
    return {"mass_g": sum(g for _, g in items) + main_wire, "budget_g": alloc - pack * 1000}


# ---------------------------------------------------------------- claims: currents and disconnect
kit.claim("CL-F1-I-CONT", "Continuous design current, pack path", calc="CALC-F1-I-DESIGN", output="i_cont_a",
          unit="A", parts=PARTS_MAIN, how="Mean BAT.Curr over a 60 s hover and a 60 s cruise segment at the gate "
          "mass (T-E2-MISSION-LOG); the larger must be <= this value.")
kit.claim("CL-F1-DISC-REQ-CONT", "Required disconnect continuous rating", calc="CALC-F1-I-DESIGN",
          output="i_req_cont_a", unit="A", verifies=["R-DISCONNECT"], parts=["PWR-002"],
          how="1.25 x CL-F1-I-CONT; re-run after any change to E2/B1 currents.")
kit.claim("CL-F1-DISC-REQ-SHORT", "Required disconnect short-time (<= 60 s) rating", calc="CALC-F1-I-DESIGN",
          output="i_req_short_a", unit="A", verifies=["R-DISCONNECT"], parts=["PWR-002"],
          how="1.25 x the transition current (20 s); logged in the first transitions (T-B1-TRANSITION-LOG).")
kit.claim("CL-F1-ILIM-WORST", "Limited peak with a 5 % sensor under-read", calc="CALC-F1-I-DESIGN",
          output="i_lim_worst_a", unit="A", limit=("<=", "CL-F1-AS150U-BURST"), verifies=["R-DISCONNECT"],
          parts=["PWR-002", "PWR-003"],
          how="Clamp meter vs BAT.Curr at 25-30 A (T-F1-SENSOR-CAL); then a 2 s full-throttle restrained run reads "
              "<= 100 A on the clamp.")
kit.claim("CL-F1-AS150U-CONT", "Main disconnect AS150U continuous rating", value=70.0, unit="A",
          limit=(">=", "CL-F1-DISC-REQ-CONT"), verifies=["R-DISCONNECT"], parts=["PWR-002"],
          cites=["SRC-J1-AS150U", "SRC-J1-HOLYBRO-CONN"],
          how="Open the Amass AS150U sheet before ordering; heat run 38 A for 10 min, connector rise <= 30 degC "
              "(T-F1-CONN-HEAT).",
          note="Decision for CR-A2-08, CR-A4-09, CR-J1-04: AS150U, not XT60. XT60 35 A (Amass) / 30 A (Holybro) is "
               "below the 37.7 A required here and has no cited rating >= 120 A for 5 s.")
kit.claim("CL-F1-AS150U-SHORT", "AS150 one-minute rating vs transition", value=150.0, unit="A",
          limit=(">=", "CL-F1-DISC-REQ-SHORT"), verifies=["R-DISCONNECT"], parts=["PWR-002"],
          cites=["SRC-J1-HOLYBRO-CONN"],
          how="Holybro table (AS150 75 A cont / 150 A 1 min); AS150U shares the 7 mm contact.")
kit.claim("CL-F1-AS150U-BURST", "Main disconnect momentary rating vs the 120 A case", value=140.0, unit="A",
          limit=(">=", "P:electrical.peak_current_a"), verifies=["R-DISCONNECT"], parts=["PWR-002"],
          cites=["SRC-J1-AS150U", "SRC-F1-AS150U-LCSC"],
          how="Maker sheet before ordering; inspect the pre-charge pin after every full-throttle stand run (forum "
              "melt report on the anti-spark contact).",
          note="Supersedes CL-J1-XT60-BURST (XT60 60 A / 1 min vs 120 A): the XT60 is not used; the 120 A < 5 s "
               "unlimited case and the 105 A limited case are inside 140 A.")
kit.claim("CL-F1-PRECHARGE-T95", "Anti-spark pre-charge time to 95 %", calc="CALC-F1-PRECHARGE", output="t95_ms",
          unit="ms", parts=["PWR-002"],
          how="Plug in slowly: hold at the first detent >= 0.5 s. Scope the bus while plugging (T-F1-PRECHARGE).")
kit.claim("CL-F1-INRUSH", "Pre-charge inrush current", calc="CALC-F1-PRECHARGE", output="i_inrush_a", unit="A",
          parts=["PWR-002"], how="Same scope trace: no visible spark at the main pins.")

# ---------------------------------------------------------------- claims: wires
W = "CALC-F1-WIRES"
kit.claim("CL-F1-MAIN-RISE", "Main path 8 AWG, steady rise at the continuous current", calc=W, output="main_rise_c",
          unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), verifies=["R-DISCONNECT"],
          parts=PARTS_MAIN, how="T-F1-WIRE-HEAT: 30 A through the pigtail in the closed pod for 10 min, "
          "thermocouple mid-lead, rise <= 10 degC.")
kit.claim("CL-F1-MAIN-PEAK", "Main path, peak rise over the mission with 120 A punches", calc=W,
          output="main_peak_fault_c", unit="degC", limit=("<=", "ASM-F1-TRANSIENT-LIMIT"), verifies=["R-DISCONNECT"],
          parts=PARTS_MAIN, how="Log the lead temperature over a full flight profile on the stand (T-F1-WIRE-HEAT).")
kit.claim("CL-F1-MAIN-MASS", "Main path wire mass (two conductors)", calc=W, output="main_mass_g", unit="g",
          parts=PARTS_MAIN, how="Weigh the finished pigtail.")
kit.claim("CL-F1-ESC-RISE", "ESC lead 16 AWG, steady rise at the heavier pair's hover share", calc=W,
          output="esc_rise_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=ESC_IDS,
          how="T-F1-WIRE-HEAT: 8.4 A through a 0.5 m 16 AWG twisted pair in a taped XPS channel mock-up, 10 min.")
kit.claim("CL-F1-ESC-PEAK", "ESC lead 16 AWG, peak rise with 51.6 A single-ESC bursts", calc=W,
          output="esc_peak_fault_c", unit="degC", limit=("<=", "ASM-F1-TRANSIENT-LIMIT"), verifies=["R-DISCONNECT"],
          parts=ESC_IDS, how="Same rig: profile replay incl. 2 s at 50 A.")
kit.claim("CL-F1-ESC18-RISE", "ESC lead 18 AWG alternative, steady rise (rejected)", calc=W, output="esc18_rise_c",
          unit="degC", parts=ESC_IDS, how="Same rig with 18 AWG if A3 asks again.",
          note="Answer to CR-A3-06: above the 10 degC limit, so 18 AWG is not used; 16 AWG stays (56 g).")
kit.claim("CL-F1-ESC-MASS", "ESC power leads, 4 pairs", calc=W, output="esc_mass_g", unit="g", parts=ESC_IDS,
          how="Weigh the four cut pairs before soldering.")
kit.claim("CL-F1-PACKLEAD-RISE", "Pack's own leads (10 AWG assumed), steady rise at the continuous current",
          calc="CALC-F1-PACKLEAD", output="lead_rise_c", unit="degC", limit=("<=", "ASM-F1-PACKLEAD-LIMIT"),
          verifies=["R-DISCONNECT"], parts=["PWR-001"],
          how="Read the lead gauge on the delivered pack (printed on the silicone); T-F1-WIRE-HEAT: 30 A for 10 min "
              "from the pack in the pod mock-up, thermocouple mid-lead.",
          note="12 AWG leads would rise ~28 degC (CL-F1-PACKLEAD12-RISE): buy packs with >= 10 AWG leads (CR-F1-14).")
kit.claim("CL-F1-PACKLEAD-PEAK", "Pack's own leads (10 AWG), mission peak with 120 A punches",
          calc="CALC-F1-PACKLEAD", output="lead_peak_fault_c", unit="degC", limit=("<=", "ASM-F1-TRANSIENT-LIMIT"),
          verifies=["R-DISCONNECT"], parts=["PWR-001"], how="Same rig, profile replay.")
kit.claim("CL-F1-PACKLEAD12-RISE", "Pack's own leads if 12 AWG, steady rise (not accepted)",
          calc="CALC-F1-PACKLEAD", output="lead_alt_rise_c", unit="degC", parts=["PWR-001"],
          how="Only if the delivered pack has 12 AWG leads: same heat run; above 20 degC the pack is returned.",
          note="above ASM-F1-PACKLEAD-LIMIT 20 degC: a 12 AWG pack is not accepted.")
kit.claim("CL-F1-FEED-RISE", "UBEC feed 20 AWG, steady rise at servo stall", calc=W, output="feed_rise_c",
          unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), parts=["PWR-005"],
          how="Bench: both servos stalled 60 s, touch-probe the feed.")
kit.claim("CL-F1-BUS-RISE", "Servo bus 20 AWG, steady rise at both servos stalled", calc=W, output="bus_rise_c",
          unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), parts=["PWR-005"],
          how="Same bench run.")
kit.claim("CL-F1-R-EXT", "Resistance pack terminals to ESC pads (equivalent, hot)", calc=W, output="r_ext_mohm",
          unit="mOhm", parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP: 20 A load step, read pack-terminal and ESC-pad voltages with one meter.",
          note="Replaces E2's ASM-E2-R-EXT 3 mOhm and E1's 4 mOhm (CR-F1-03).")
kit.claim("CL-F1-DROP-CONT", "Voltage drop pack to ESC at the continuous current", calc=W, output="drop_cont_pct",
          unit="%", limit=("<=", 2.0), parts=PARTS_MAIN + ESC_IDS, how="T-F1-DROP at 30 A.")
kit.claim("CL-F1-DROP-PEAK", "Voltage drop pack to ESC at the 100 A limiter", calc=W, output="drop_peak_pct",
          unit="%", limit=("<=", 5.0), parts=PARTS_MAIN + ESC_IDS, how="T-F1-DROP scaled; stand log at full throttle.")

# ---------------------------------------------------------------- claims: avionics supply, sensing, mass
kit.claim("CL-F1-SERVO-BEC-REQ", "Servo supply rating required", calc="CALC-F1-SERVO-BEC", output="i_req_a",
          unit="A", verifies=["R-AVIONICS-POWER"], parts=["PWR-005"],
          how="T-F1-SERVO-STALL: measure each servo's stall current at 6 V; re-run with the measured value.",
          note="> 4.5 A (SpeedyBee F405 Wing servo BEC, SRC-F1-SPEEDYBEE-WING): a UBEC is fitted. Drop it only if "
               "the measured stall current is <= 1.1 A per servo AND F3's FC servo BEC is >= 4.5 A continuous.")
kit.claim("CL-F1-SERVO-STALL-BUS", "Servo bus current, both servos stalled", calc="CALC-F1-SERVO-BEC",
          output="i_bus_stall_a", unit="A", verifies=["R-AVIONICS-POWER"], parts=["PWR-005"],
          how="T-F1-SERVO-STALL, both servos blocked together, meter in the UBEC output.")
kit.claim("CL-F1-UBEC-RATING", "UBEC continuous rating (6 V, >= 6 A class)", value=8.0, unit="A",
          limit=(">=", "CL-F1-SERVO-BEC-REQ"), verifies=["R-AVIONICS-POWER"], parts=["PWR-005"],
          how="Datasheet of the bought UBEC; bench both servos stalled: rail >= 4.8 V (5.8 V at the 6 V setting).",
          note="candidate Hobbywing UBEC 8A class; datasheet not yet opened (UNVERIFIED)")
kit.claim("CL-F1-SENSOR-PEAK", "Current sensor peak range vs 120 A", value=215.0, unit="A",
          limit=(">=", "P:electrical.peak_current_a"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F1-SPEEDYBEE-WING"],
          how="Candidate FC power board (F3 decides); any replacement needs >= 120 A peak and >= 38 A continuous.")
kit.claim("CL-F1-SENSOR-CONT", "Current sensor continuous rating", value=90.0, unit="A",
          limit=(">=", "CL-F1-DISC-REQ-CONT"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F1-SPEEDYBEE-WING"], how="As CL-F1-SENSOR-PEAK; T-F1-SENSOR-CAL.")
kit.claim("CL-F1-POWER-MASS", "Power subsystem mass excluding the pack", calc="CALC-F1-MASS", output="mass_g",
          unit="g", limit=("<=", "CL-F1-POWER-BUDGET"), parts=PARTS_MAIN + ["PWR-005"],
          how="Weigh each item on arrival; A3 replaces the EST rows.",
          note="over A3's 45 g by 24 g: 8 AWG main path (+12 g over 10 AWG, needed for the 10 degC rise) and the "
               "four ESC capacitors (8 g, not in A3's model). CR-F1-02 asks A1 for +25 g from the reserve.")
kit.claim("CL-F1-POWER-BUDGET", "Power allocation left after the pack", calc="CALC-F1-MASS", output="budget_g",
          unit="g", how="P:mass.allocation_g.power minus P:battery.mass_kg; follows A1's allocation.")

# ---------------------------------------------------------------- tests
kit.test("T-F1-WIRE-HEAT", "Wire heat runs", verifies=["CL-F1-MAIN-RISE", "CL-F1-MAIN-PEAK", "CL-F1-ESC-RISE",
                                                         "CL-F1-ESC-PEAK", "CL-F1-PACKLEAD-RISE",
                                                         "CL-F1-PACKLEAD-PEAK"],
         procedure="Bench supply (>= 40 A) + load; 8 AWG pigtail in a closed pod mock-up at 30 A, 16 AWG pair in a "
                   "taped XPS channel at 8.4 A, each 10 min; K-type thermocouple taped mid-lead under 10 mm of foam "
                   "tape; then 50 A for 2 s on the 16 AWG. Pass: rise <= 10 degC steady, <= 30 degC peak.")
kit.test("T-F1-CONN-HEAT", "AS150U heat run", verifies=["CL-F1-AS150U-CONT"],
         procedure="38 A for 10 min through a mated pair; IR thermometer on the housing; rise <= 30 degC.")
kit.test("T-F1-DROP", "Path resistance", verifies=["CL-F1-R-EXT", "CL-F1-DROP-CONT", "CL-F1-DROP-PEAK"],
         procedure="20 A load step from the pack; meter across pack terminals and across one ESC's pads; "
                   "R = dV/dI. Pass: drop <= 2 % at 30 A.")
kit.test("T-F1-SENSOR-CAL", "Current sensor calibration", verifies=["CL-F1-ILIM-WORST", "CL-F1-SENSOR-CONT"],
         procedure="Clamp meter on the main lead at 5, 15, 25, 30 A (motors on the restrained frame); set "
                   "BATT_AMP_PERVLT so BAT.Curr is within 5 %; record the value for F4.")
kit.test("T-F1-SERVO-STALL", "Servo stall current and rail voltage", verifies=["CL-F1-SERVO-BEC-REQ",
                                                                               "CL-F1-UBEC-RATING"],
         procedure="Each servo blocked at full deflection 2 s on the UBEC at 6 V, meter in series; both together: "
                   "rail >= 5.8 V at the servo and FC 5 V rail >= 4.8 V.")
kit.test("T-F1-PRECHARGE", "Anti-spark behaviour", verifies=["CL-F1-PRECHARGE-T95", "CL-F1-INRUSH"],
         procedure="Scope on the bus while plugging the AS150U slowly; bus >= 95 % before the main pins close; "
                   "no spark marks after 20 plug cycles.")
kit.test("T-F1-RIPPLE", "ESC supply ripple", verifies=["CL-F1-DROP-PEAK"],
         procedure="Scope at each ESC's pads, full-throttle 2 s punch on the stand: ripple <= 1.0 V p-p, no spikes "
                   "above 21 V (ESC caps 25 V).")


def write_tables(out):
    """data/derating.csv: the derating table POWER.md shows (written under __main__ only)."""
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(exist_ok=True)
    rows = [("run", "awg", "len_m", "i_cont_a", "rise_cont_c", "peak_normal_c", "peak_fault_c", "r_loop_mohm",
             "mass_g")]
    lens = {"main": 0.15, "esc": 0.5, "esc18": 0.5, "feed": 0.15, "bus": 0.35}
    for k in ("main", "esc", "esc18", "feed", "bus"):
        rows.append((k, out[f"{k}_awg"], lens[k], round(out[f"{k}_i_cont_a"], 2), round(out[f"{k}_rise_c"], 1),
                     round(out.get(f"{k}_peak_normal_c", float("nan")), 1),
                     round(out.get(f"{k}_peak_fault_c", float("nan")), 1),
                     round(out.get(f"{k}_r_loop_mohm", float("nan")), 2), round(out[f"{k}_mass_g"], 1)))
    pl = kit.nodes["CALC-F1-PACKLEAD"]["outputs"]
    i_c = round(out["main_i_cont_a"], 2)
    for k, name in (("lead", "packlead"), ("lead_alt", "packlead12")):
        rows.append((name, pl[f"{k}_awg"], kit.value("ASM-F1-PACKLEAD")[2], i_c, round(pl[f"{k}_rise_c"], 1),
                     float("nan"), round(pl[f"{k}_peak_fault_c"], 1), round(pl[f"{k}_r_loop_mohm"], 2), float("nan")))
    with open(d / "derating.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    # gauge sweep: steady rise at each run's continuous current for every gauge (the derating table)
    od = kit.value("ASM-F1-WIRE-OD")
    f_pod, f_chan, f_pair, eps = kit.value("ASM-F1-COOLING")
    ta = max(kit.value("P:env.ambient_design_c"))
    pod, chan = (f_pod, f_pair, eps), (f_chan, 1.0, eps)
    cases = [("pack path, continuous", out["main_i_cont_a"], pod),
             ("pack path, transition 42.9 A if held", 42.92, pod),
             ("ESC lead, hover share", out["esc_i_cont_a"], chan),
             ("ESC lead, limiter 24.8 A if held", 24.8, chan)]
    with open(d / "gauge_sweep.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["case", "i_a"] + [f"awg{g}_rise_c" for g in (8, 10, 12, 14, 16, 18, 20)])
        for name, i, cool in cases:
            wr.writerow([name, round(i, 2)] + [round(steady_rise(i, wire_props(g, od), ta, cool), 1)
                                               for g in (8, 10, 12, 14, 16, 18, 20)])
    print("wrote", d / "derating.csv", "and", d / "gauge_sweep.csv")


if __name__ == "__main__":
    kit.write()
    write_tables(kit.nodes["CALC-F1-WIRES"]["outputs"])
