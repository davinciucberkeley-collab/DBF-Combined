"""F1 power distribution: main disconnect, wire gauges with derating, voltage drop, sensing, UBEC, protection.

Run:  python -I redesign/team/F1/power.py      -> claims.json, data/derating.csv, data/gauge_sweep.csv
Then: python -I redesign/team/F1/draw_schematic.py ; python -I redesign/proofs/build_graph.py

Wire model (CALC-F1-WIRES), per metre of conductor, Python standard library only:
  R(T) = rho_Cu * k_strand / A_awg * (1 + alpha (T - 20))                     IEC 60028 annealed copper
  steady:   I^2 R(T) = h(T) * pi * OD * (T - T_amb)                           solved by iteration
  h = f_enc * f_pair * (h_conv Churchill-Chu horizontal cylinder + h_rad, eps 0.9)
  transient: C' dT/dt = I(t)^2 R(T) - h pi OD (T - T_amb),  C' = m_Cu c_Cu + m_sil c_sil, dt 0.25 s
  short runs (main jumpers, bundled sections): 1-D fin, ends held at the terminal / open-run temperature,
            theta_mid = theta_inf - (theta_inf - theta_end) / cosh(m L / 2),  m = sqrt(h pi OD / (k_Cu A))
The mission current profile (CL-F1-PROFILE) is built from E2's pessimistic phase claims (CR-E2-19) with short
punches inserted after each transition (limited 100 A normal case, 120 A unlimited / 51.6 A single-ESC fault case).
R4 (2026-11-10): F2 harness re-run (ESC leads 0.475-0.620 m), power-board link check (CALC-F1-PMOD).
R3 (2026-11-09): routed ESC lengths from F2 (CR-F2-02), 10 AWG main jumpers from subsystems/power (PWR-R1), limits
from P:electrical.* (D-56), servo stall 1.4 A (CR-D6-06), mass from CL-PWR-MASS-NONPACK (D-48).
"""
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proofs"))
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/power/params.json"])

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
kit.assumption("ASM-F1-GROUND", "Ground phase before take-off",
               "[duration s, pack current A] armed on the ground (FC, RX, GPS, servos idle)",
               basis="E2's pessimistic budget ground row (team/E2/ENERGY.md); E2 emits no claim for it. It does not "
                     "move any wire result (0.4 A)", value=[180, 0.41], unit="s,A", status="UNVERIFIED")
kit.assumption("ASM-F1-PUNCH", "Short-time current cases",
               "durations: limited full-throttle punch 5 s, unlimited momentary 5 s, single-ESC asymmetric burst 2 s",
               basis="P:electrical.peak_current_a says < 5 s; a single motor at full throttle while the others are low "
                     "(yaw/roll saturation) lasts about one control correction; F4 to confirm from SITL",
               value=[5.0, 5.0, 2.0], unit="s", status="PROPOSED")
kit.assumption("ASM-F1-GAUGES", "Chosen gauges",
               "AWG for [ESC power lead, ESC alternative checked, UBEC feed, UBEC servo bus]; the main jumper gauge "
               "is P:power.jumper_awg (10 AWG, PWR-R1)",
               basis="F1 choice; the alternative (18 AWG) is computed to answer CR-A3-06", value=[16, 18, 20, 20],
               unit="AWG", status="PROPOSED")
kit.assumption("ASM-F1-LENGTHS", "Conductor lengths, one way, not routed by F2",
               "[UBEC feed incl. fuse pigtails, UBEC to servo bus] per conductor; main jumpers come from "
               "P:power.jumper_len_m and ESC leads from F2's CL-F2-ESC-LEN-*",
               basis="pod layout subsystems/power/SPEC.md: fuse under the cradle, UBEC in the right channel",
               value=[0.15, 0.35], unit="m", status="PROPOSED")
kit.assumption("ASM-F1-BUNDLE", "Short bundled ESC-lead sections (F2 routing, CR-F2-02)",
               "[name, length m, cooling factor] for sections where more than one pair shares a passage",
               basis="F2: LR/LL pairs together through the P1 straw (~0.05 m) and two twisted pairs stacked 8 mm in the "
                     "pod crossing (~0.09 m). Factor = fraction of free-air convection + radiation kept: straw "
                     "enclosed in foam 0.3 (four conductors, little radiation out), pod crossing 0.6 (twisted 0.85 x "
                     "stacked ~0.7). Judgement, conservative; T-F1-WIRE-HEAT checks the straw",
               value=[["P1 straw, LR + LL pairs", 0.05, 0.3], ["pod crossing, 2 twisted pairs stacked", 0.09, 0.6]],
               unit="-,m,-", status="UNVERIFIED", cites=["SRC-F1-INCROPERA"])
kit.assumption("ASM-F1-WIRE-OD", "Silicone wire outside diameter by gauge",
               "[AWG, OD mm] for high-strand silicone hobby wire",
               basis="typical maker tables (BNTECHGO, Turnigy) +/-0.2 mm; measure the reel",
               value=[[8, 6.0], [10, 4.8], [12, 4.0], [14, 3.2], [16, 2.6], [18, 2.0], [20, 1.7], [22, 1.4], [28, 0.9]],
               unit="AWG,mm", status="UNVERIFIED")
kit.assumption("ASM-F1-COOLING", "Cooling derates",
               "[f_pod, f_channel, f_pair, emissivity]: f_pod 1.0 in the vented pod (still air); f_channel 0.75 "
               "for a lead in a tape-covered surface groove in the wing; f_pair 0.85 for a twisted +/- pair "
               "(pod only; in the wing + and - lie in two grooves 5 mm apart, f 1.0); silicone emissivity 0.9",
               basis="engineering judgement: a covered groove halves convection but keeps radiation to the tape and "
                     "foam (~0.75 overall); a twisted pair shields ~15 % of each conductor's surface. Prop wash over "
                     "the wing in hover is not credited. T-F1-WIRE-HEAT measures it",
               value=[1.0, 0.75, 0.85, 0.9], unit="-", status="UNVERIFIED", cites=["SRC-F1-INCROPERA"])
kit.assumption("ASM-F1-R-CONTACT", "Contact resistance per mated contact",
               "AS150U contact 0.8 mOhm (two in the path)",
               basis="reseller values 0.40 and <= 0.8 mOhm; the larger is used", value=0.0008, unit="ohm",
               status="UNVERIFIED", cites=["SRC-J1-AS150U"])
kit.assumption("ASM-F1-R-BOARD", "Current shunt, board copper and solder joints",
               "0.6 mOhm in the common path (sensor shunt ~0.25, copper and four solder joints ~0.35)",
               basis="typical 0.2-0.3 mOhm hobby PDB shunts; measured by T-F1-DROP", value=0.0006, unit="ohm",
               status="UNVERIFIED")
kit.assumption("ASM-F1-SERVO-STALL", "Servo stall current 1.4 A at 6 V",
               "per elevon servo, Savox SH-0255MG+ (D6), rated 4.8-6.0 V (not HV)",
               basis="D6 CR-D6-06: retailer data 1.2 A at 4.8 V / 1.4 A at 6.0 V (was 1.3 A class value); measured "
                     "by T-F1-SERVO-STALL on the delivered servos",
               value=1.4, unit="A", status="UNVERIFIED", cites=["SRC-D6-SH0255-STALL"])
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


def fin_mid_rise(i, w, ta, cool, length, theta_end, k_cu):
    """Mid-length rise above ambient of a short run whose ends sit at ambient + theta_end (1-D fin)."""
    th = theta_end + 1.0
    for _ in range(200):
        ts = ta + th
        g = h_total(ts, ta, w["od"], *cool) * math.pi * w["od"]           # W/m/K to ambient
        q = i * i * w["r20"] * (1 + ALPHA * (ts - 20))                      # W/m
        m = math.sqrt(g / (k_cu * w["a"]))
        th_inf = q / g
        new = th_inf - (th_inf - theta_end) / math.cosh(m * length / 2)
        th = 0.5 * th + 0.5 * new
    return th


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
@kit.calc("CALC-F1-PROFILE", title="Pessimistic mission current profile from E2's phase claims",
          equation="table [phase, t_phase, I_phase] in flight order (ground, climb, hover, transition forward, cruise, "
                   "back-transition, descent)",
          inputs={"ground": "ASM-F1-GROUND",
                  "i_climb": "CL-E2-I-CLIMB-PESS", "t_climb": "CL-E2-T-CLIMB-PESS",
                  "i_hover": "CL-E2-HOVER-I-GATE", "t_hover": "CL-E2-T-HOVER-PESS",
                  "i_fwd": "CL-E2-I-TRANS-FWD-PESS", "t_fwd": "CL-E2-T-TRANS-FWD-PESS",
                  "i_cruise": "CL-E2-CRUISE-I-PESS", "t_cruise": "CL-E2-T-CRUISE-PESS",
                  "i_back": "CL-E2-I-TRANS-BACK-PESS", "t_back": "CL-E2-T-TRANS-BACK-PESS",
                  "i_desc": "CL-E2-I-DESCENT-PESS", "t_desc": "CL-E2-T-DESCENT-PESS"},
          units={"i_climb": "A", "i_hover": "A", "i_fwd": "A", "i_cruise": "A", "i_back": "A", "i_desc": "A",
                 "t_climb": "s", "t_hover": "s", "t_fwd": "s", "t_cruise": "s", "t_back": "s", "t_desc": "s"})
def mission_profile(ground, i_climb, t_climb, i_hover, t_hover, i_fwd, t_fwd, i_cruise, t_cruise, i_back, t_back,
                    i_desc, t_desc):
    return {"profile": [["ground", ground[0], ground[1]], ["climb 0-50 m", t_climb, i_climb],
                        ["hover", t_hover, i_hover], ["transition forward", t_fwd, i_fwd],
                        ["cruise", t_cruise, i_cruise], ["back-transition", t_back, i_back],
                        ["descent", t_desc, i_desc]]}


@kit.calc("CALC-F1-I-DESIGN", title="Design currents for the pack path",
          equation="I_cont = max(I_hover, I_cruise, P_vclimb / V_nom) ; I_short = max profile phase <= 60 s ; "
                   "I_req = k I",
          inputs={"i_hover": "CL-E2-HOVER-I-GATE", "i_cruise": "CL-E2-CRUISE-I-PESS", "p_climb": "CL-B1-VCLIMB-P",
                  "v": "P:battery.v_nom", "k": "P:requirements.disconnect_factor", "profile": "CL-F1-PROFILE",
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
                   "split s, applied to every branch); R_ext = R_common + 1/sum(1/R_branch_i); "
                   "drop = I R_common + I_esc R_branch,max",
          inputs={"i_cont": "CL-F1-I-CONT", "profile": "CL-F1-PROFILE", "punch": "ASM-F1-PUNCH",
                  "gauges": "ASM-F1-GAUGES", "lengths": "ASM-F1-LENGTHS", "od": "ASM-F1-WIRE-OD",
                  "g_main": "P:power.jumper_awg", "l_main": "P:power.jumper_len_m", "k_cu": "P:power.k_cu_w_mk",
                  "l_ur": "CL-F2-ESC-LEN-UR", "l_ul": "CL-F2-ESC-LEN-UL", "l_lr": "CL-F2-ESC-LEN-LR",
                  "l_ll": "CL-F2-ESC-LEN-LL", "bundle": "ASM-F1-BUNDLE",
                  "cool": "ASM-F1-COOLING", "amb": "P:env.ambient_design_c", "n": "P:propulsion.n_motors",
                  "split": "P:requirements.hover_split_max", "ilim": "P:performance.full_throttle_current_a",
                  "ipeak": "P:electrical.peak_current_a", "i_esc_lim": "P:propulsion.current_max_per_motor_a",
                  "i_esc_asym": "CL-E1-IMAX-168-55", "r_contact": "ASM-F1-R-CONTACT", "r_board": "ASM-F1-R-BOARD",
                  "v": "P:battery.v_nom", "i_servo_bus": "CL-F1-SERVO-STALL-BUS", "ubec_eta_in": "ASM-F1-UBEC-IN"},
          units={"ilim": "A", "ipeak": "A", "i_esc_lim": "A", "v": "V", "l_main": "m", "k_cu": "W/m/K",
                 "l_ur": "m", "l_ul": "m", "l_lr": "m", "l_ll": "m"})
def wires(i_cont, profile, punch, gauges, lengths, od, g_main, l_main, k_cu, l_ur, l_ul, l_lr, l_ll, bundle, cool,
          amb, n, split, ilim, ipeak, i_esc_lim, i_esc_asym, r_contact, r_board, v, i_servo_bus, ubec_eta_in):
    ta = max(amb)
    share = 2 * split / (1 + split) / n
    t_lim, t_mom, t_asym = punch
    g_esc, g_esc_alt, g_feed, g_bus = gauges
    l_feed, l_bus = lengths
    l_esc = [l_ur, l_ul, l_lr, l_ll]
    f_pod, f_chan, f_pair, eps = cool
    cools = {"main": (f_pod, f_pair, eps), "esc": (f_chan, 1.0, eps), "esc18": (f_chan, 1.0, eps),
             "feed": (f_pod, f_pair, eps), "bus": (f_chan, 1.0, eps)}
    out = {}
    runs = {"main": (int(g_main), sum(l_main), 1.0, ilim, ipeak, t_mom),
            "esc": (g_esc, max(l_esc), share, i_esc_lim, i_esc_asym, t_asym),
            "esc18": (g_esc_alt, max(l_esc), share, i_esc_lim, i_esc_asym, t_asym)}
    for key, (g, length, scale, i_norm, i_fault, t_fault) in runs.items():
        w = wire_props(g, od)
        cool = cools[key]
        i_c = i_cont * scale
        out[f"{key}_awg"] = g
        out[f"{key}_len_m"] = length
        out[f"{key}_i_cont_a"] = i_c
        out[f"{key}_rise_long_c"] = steady_rise(i_c, w, ta, cool)          # long wire, no end conduction
        out[f"{key}_rise_c"] = out[f"{key}_rise_long_c"]
        out[f"{key}_peak_normal_c"] = profile_peak(_segments(profile, True, t_lim, i_norm, scale), w, ta, cool)
        out[f"{key}_peak_fault_c"] = profile_peak(_segments(profile, True, t_fault, i_fault, scale), w, ta, cool)
        t_hot = ta + out[f"{key}_rise_c"]
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (t_hot - 20)) * 1e3
        out[f"{key}_mass_g"] = 2 * (length if key == "main" else sum(l_esc)) * w["mass_gpm"]
        out[f"{key}_od_mm"] = w["od"] * 1e3
        out[f"{key}_gpm"] = w["mass_gpm"]
    # main jumpers: each <= 0.05 m between soldered terminals, so the rise above the terminals is a fin result.
    # The long-wire value (main_rise_long_c) is kept as the bound if a jumper were ever made long.
    wm = wire_props(int(g_main), od)
    out["main_rise_c"] = fin_mid_rise(i_cont, wm, ta, cools["main"], max(l_main), 0.0, k_cu)
    # ESC branches: loop resistance per routed length, parallel equivalent
    we = wire_props(g_esc, od)
    t_esc = ta + out["esc_rise_c"]
    r_br = [2 * L * we["r20"] * (1 + ALPHA * (t_esc - 20)) for L in l_esc]
    out["esc_r_loop_max_mohm"] = max(r_br) * 1e3
    out["esc_r_loop_min_mohm"] = min(r_br) * 1e3
    out["esc_len_total_m"] = sum(l_esc)
    # bundled sections: fin with ends at the open-run (groove) rise; peak without axial credit
    for k, (name, lb, fb) in enumerate(bundle):
        cb = (fb, 1.0, eps)
        out[f"bundle{k}_rise_c"] = fin_mid_rise(i_cont * share, we, ta, cb, lb, out["esc_rise_c"], k_cu)
        out[f"bundle{k}_rise_long_c"] = steady_rise(i_cont * share, we, ta, cb)
        out[f"bundle{k}_peak_fault_c"] = profile_peak(_segments(profile, True, t_asym, i_esc_asym, share), we, ta, cb)
    out["bundle_rise_max_c"] = max(out[f"bundle{k}_rise_c"] for k in range(len(bundle)))
    out["bundle_peak_max_c"] = max(out[f"bundle{k}_peak_fault_c"] for k in range(len(bundle)))
    # UBEC feed and servo bus: steady at their worst continuous current (servo stall)
    i_feed = i_servo_bus * 6.0 / (ubec_eta_in * v)
    for key, g, length, i in (("feed", g_feed, l_feed, i_feed), ("bus", g_bus, l_bus, i_servo_bus)):
        w = wire_props(g, od)
        cool = cools[key]
        out[f"{key}_awg"], out[f"{key}_i_cont_a"], out[f"{key}_len_m"] = g, i, length
        out[f"{key}_rise_c"] = steady_rise(i, w, ta, cool)
        out[f"{key}_mass_g"] = 2 * length * w["mass_gpm"]
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (ta + out[f"{key}_rise_c"] - 20)) * 1e3
    # resistance pack terminals -> ESC pads, as one equivalent common resistance (four branches in parallel)
    r_common = 2 * r_contact + r_board + out["main_r_loop_mohm"] * 1e-3
    out["r_common_mohm"] = r_common * 1e3
    out["r_ext_mohm"] = (r_common + 1 / sum(1 / r for r in r_br)) * 1e3
    out["drop_cont_pct"] = 100 * (i_cont * r_common + i_cont * share * max(r_br)) / v
    out["drop_peak_pct"] = 100 * (ilim * r_common + i_esc_lim * max(r_br)) / v
    out["main_loss_w_cont"] = i_cont ** 2 * r_common
    r_per_m = 2 * we["r20"] * (1 + ALPHA * (t_esc - 20))                   # loop Ohm per metre of route
    out["esc_len_allow_m"] = (0.05 * v - ilim * r_common) / (i_esc_lim * r_per_m)
    return out


kit.assumption("ASM-F1-UBEC-IN", "UBEC efficiency 0.85", "switching UBEC, 4S in, 6 V out",
               basis="typical buck converter at 1-5 A", value=0.85, unit="-", status="PROPOSED")

kit.assumption("ASM-F1-PACKLEAD", "Pack's own leads: gauge and length after re-termination",
               "[assumed maker gauge AWG, alternative gauge AWG, length one way m]",
               basis="the Ovonic listing does not give the lead gauge (open the product sheet / measure); 4S 6500 "
                     "130C packs ship with 10 or 12 AWG. Length: D2 CR-D2-07 needs >= 90 mm from the pack aft face to "
                     "the parked connector; cut to 0.10 m when the AS150U is fitted",
               value=[10, 12, 0.10], unit="AWG,AWG,m", status="UNVERIFIED", cites=["SRC-OVONIC-4S6500"])
@kit.calc("CALC-F1-PACKLEAD", title="Pack's own leads: steady and mission-peak rise",
          equation="same wire model as CALC-F1-WIRES, pod still air, side-by-side pair (f_pair)",
          inputs={"i_cont": "CL-F1-I-CONT", "lead": "ASM-F1-PACKLEAD", "profile": "CL-F1-PROFILE",
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


@kit.calc("CALC-F1-MASS", title="Power mass excluding the pack, against the allocation left after the pack",
          equation="m = CL-PWR-MASS-NONPACK (PWR-R1 parts: AS150U half + 10 AWG jumpers, power board, bus board, UBEC, "
                   "frame, fuse, 4 caps); budget = allocation - pack",
          inputs={"nonpack": "CL-PWR-MASS-NONPACK", "alloc": "P:mass.allocation_g.power", "pack": "P:battery.mass_kg"},
          units={"nonpack": "g", "alloc": "g", "pack": "kg"})
def power_mass(nonpack, alloc, pack):
    return {"mass_g": nonpack, "budget_g": alloc - pack * 1000}


@kit.calc("CALC-F1-PMOD", title="Power-board link (JST-GH 6, 28 AWG): 5 V conductor heating",
          equation="same steady wire model as CALC-F1-WIRES, 28 AWG, pod still air, f_pair for the 6-way cable; "
                   "I_5V = CL-F3-5V-REQ (2 x the FC 5 V load); stall case = CL-F1-SERVO-STALL-BUS",
          inputs={"i_5v": "CL-F3-5V-REQ", "i_stall": "CL-F1-SERVO-STALL-BUS", "od": "ASM-F1-WIRE-OD",
                  "cool": "ASM-F1-COOLING", "amb": "P:env.ambient_design_c"},
          units={"i_5v": "A", "i_stall": "A", "amb": "degC"})
def pmod(i_5v, i_stall, od, cool, amb):
    ta = max(amb)
    w = wire_props(28, od)
    c = (cool[0], cool[2], cool[3])
    return {"rise_5v_c": steady_rise(i_5v, w, ta, c), "rise_stall_c": steady_rise(i_stall, w, ta, c)}


# ---------------------------------------------------------------- claims: currents and disconnect
kit.claim("CL-F1-PROFILE", "Mission current profile used for wire heating (E2 pessimistic phases)",
          calc="CALC-F1-PROFILE", output="profile", unit="s,A", parts=PARTS_MAIN,
          how="Phase means of BAT.Curr on the full-mission log (T-E2-MISSION-LOG) inside E2's +/-15 %.",
          note="Replaces ASM-F1-PROFILE (copied table, retired in R3) per CR-E2-19.")
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
SHORT = "P:electrical.wire_temp_rise_short_max_c"
kit.claim("CL-F1-MAIN-RISE", "Main jumpers 10 AWG (<= 0.05 m), steady rise above their terminals", calc=W,
          output="main_rise_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=PARTS_MAIN,
          how="T-F1-WIRE-HEAT: 30 A through the built stack in the closed pod mock-up, 10 min, thermocouples at the "
              "W-MAIN-2 mid-point and at both solder joints; mid minus joint <= 10 degC.",
          note="Fin result with convection; agrees with CL-PWR-JUMPER-RISE (conduction only). The terminals sit at "
               "the AS150U / pack-lead / board temperature (CL-F1-PACKLEAD-RISE, T-F1-CONN-HEAT). A long 10 AWG run "
               "would rise CL-F1-MAIN-RISE-LONG: never extend the jumpers.")
kit.claim("CL-F1-MAIN-RISE-LONG", "Main path 10 AWG, long-wire steady rise (bound, not the design case)", calc=W,
          output="main_rise_long_c", unit="degC", parts=PARTS_MAIN,
          how="Not tested: shows why the jumpers stay <= 0.05 m (above the 10 degC limit if run long).")
kit.claim("CL-F1-MAIN-PEAK", "Main path, peak rise over the mission with 120 A punches (long-wire, conservative)",
          calc=W, output="main_peak_fault_c", unit="degC", limit=("<=", SHORT), verifies=["R-DISCONNECT"],
          parts=PARTS_MAIN, how="Log the jumper temperature over a full flight profile on the stand (T-F1-WIRE-HEAT).")
kit.claim("CL-F1-MAIN-MASS", "Main jumper wire mass (two conductors, both jumpers)", calc=W, output="main_mass_g",
          unit="g", parts=PARTS_MAIN, how="Weigh the finished jumpers.",
          note="Booked inside CL-PWR-MASS-NONPACK (PWR-002); listed here for the derating table only.")
kit.claim("CL-F1-ESC-RISE", "ESC lead 16 AWG, steady rise at the heavier pair's hover share (open groove run)",
          calc=W, output="esc_rise_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=ESC_IDS,
          how="T-F1-WIRE-HEAT: 8.4 A through a 0.65 m 16 AWG pair in a taped XPS groove mock-up, 10 min.")
kit.claim("CL-F1-ESC-PEAK", "ESC lead 16 AWG, peak rise with 51.6 A single-ESC bursts", calc=W,
          output="esc_peak_fault_c", unit="degC", limit=("<=", SHORT), verifies=["R-DISCONNECT"],
          parts=ESC_IDS, how="Same rig: profile replay incl. 2 s at 50 A.")
kit.claim("CL-F1-BUNDLE-RISE", "ESC leads in the bundled sections (P1 straw, pod crossing), steady rise", calc=W,
          output="bundle_rise_max_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=ESC_IDS,
          how="T-F1-WIRE-HEAT: two 16 AWG pairs at 8.4 A each through a 50 mm straw in XPS, thermocouple at the "
              "straw mid-point, 10 min.",
          note="Answer to CR-F2-02: both bundles accepted; axial conduction to the open run carries most of the "
               "extra heat over sections this short.")
kit.claim("CL-F1-BUNDLE-PEAK", "Bundled sections, peak rise with 51.6 A bursts (no axial credit, conservative)",
          calc=W, output="bundle_peak_max_c", unit="degC", limit=("<=", SHORT), verifies=["R-DISCONNECT"],
          parts=ESC_IDS, how="Same straw rig, profile replay incl. 2 s at 50 A.")
kit.claim("CL-F1-ESC18-RISE", "ESC lead 18 AWG alternative, steady rise (rejected)", calc=W, output="esc18_rise_c",
          unit="degC", parts=ESC_IDS, how="Same rig with 18 AWG if A3 asks again.",
          note="Answer to CR-A3-06: above the 10 degC limit, so 18 AWG is not used; 16 AWG stays.")
kit.claim("CL-F1-ESC-MASS", "ESC power leads, 4 pairs at F2's routed lengths", calc=W, output="esc_mass_g", unit="g",
          parts=ESC_IDS, how="Weigh the four cut pairs before soldering.",
          note="Harness mass is F2's (HRN-101/102, CL-F2-MASS); F2 reads the per-metre value CL-F1-W16-GPM "
               "instead of dividing this by 4.0 m (CR-F1-23).")
kit.claim("CL-F1-ESC-LEN-ALLOW", "Longest 16 AWG ESC lead that keeps the 100 A drop <= 5 %", calc=W,
          output="esc_len_allow_m", unit="m", limit=(">=", "CL-F2-ESC-LEN-MAX"), parts=ESC_IDS,
          how="F2 cut list: every ESC lead <= this length (CR-F1-25); T-F1-DROP on the longest branch.",
          note="R3: LR routed at 0.650 m is 7 mm over; trim its service loop or use 14 AWG on LR only.")
kit.claim("CL-F1-W16-GPM", "16 AWG silicone wire mass per metre of one conductor", calc=W, output="esc_gpm",
          unit="g/m", parts=ESC_IDS, how="Weigh 1 m of the delivered reel.")
kit.claim("CL-F1-PACKLEAD-RISE", "Pack's own leads (10 AWG assumed), steady rise at the continuous current",
          calc="CALC-F1-PACKLEAD", output="lead_rise_c", unit="degC", limit=("<=", "P:electrical.pack_lead_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=["PWR-001"],
          how="Read the lead gauge on the delivered pack (printed on the silicone); T-F1-WIRE-HEAT: 30 A for 10 min "
              "from the pack in the pod mock-up, thermocouple mid-lead.",
          note="12 AWG leads would rise ~28 degC (CL-F1-PACKLEAD12-RISE): buy packs with >= 10 AWG leads (CR-F1-14).")
kit.claim("CL-F1-PACKLEAD-PEAK", "Pack's own leads (10 AWG), mission peak with 120 A punches",
          calc="CALC-F1-PACKLEAD", output="lead_peak_fault_c", unit="degC", limit=("<=", SHORT),
          verifies=["R-DISCONNECT"], parts=["PWR-001"], how="Same rig, profile replay.")
kit.claim("CL-F1-PACKLEAD12-RISE", "Pack's own leads if 12 AWG, steady rise (not accepted)",
          calc="CALC-F1-PACKLEAD", output="lead_alt_rise_c", unit="degC", parts=["PWR-001"],
          how="Only if the delivered pack has 12 AWG leads: same heat run; above 20 degC the pack is returned.",
          note="above P:electrical.pack_lead_rise_max_c 20 degC: a 12 AWG pack is not accepted.")
kit.claim("CL-F1-FEED-RISE", "UBEC feed 20 AWG, steady rise at servo stall", calc=W, output="feed_rise_c",
          unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), parts=["PWR-005"],
          how="Bench: both servos stalled 60 s, touch-probe the feed.")
kit.claim("CL-F1-BUS-RISE", "Servo bus 20 AWG, steady rise at both servos stalled", calc=W, output="bus_rise_c",
          unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"), parts=["PWR-005"],
          how="Same bench run.")
kit.claim("CL-F1-R-EXT", "Resistance pack terminals to ESC pads (equivalent, hot)", calc=W, output="r_ext_mohm",
          unit="mOhm", parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP: 20 A load step, read pack-terminal and ESC-pad voltages with one meter.",
          note="R4: F2 routed ESC lengths 0.475-0.620 m and 10 AWG jumpers; P:electrical.r_ext_mohm follows (CR-F1-24).")
kit.claim("CL-F1-DROP-CONT", "Voltage drop pack to the farthest ESC at the continuous current", calc=W,
          output="drop_cont_pct", unit="%", limit=("<=", 2.0), parts=PARTS_MAIN + ESC_IDS, how="T-F1-DROP at 30 A.")
kit.claim("CL-F1-DROP-PEAK", "Voltage drop pack to the farthest ESC at the 100 A limiter", calc=W,
          output="drop_peak_pct", unit="%", limit=("<=", 5.0), parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP scaled; stand log at full throttle.")

# ---------------------------------------------------------------- claims: avionics supply, sensing, mass
kit.claim("CL-F1-SERVO-BEC-REQ", "Servo supply rating required", calc="CALC-F1-SERVO-BEC", output="i_req_a",
          unit="A", verifies=["R-AVIONICS-POWER"], parts=["PWR-005"],
          how="T-F1-SERVO-STALL: measure each servo's stall current at 6 V; re-run with the measured value.",
          note="5.6 A with D6's 1.4 A stall (CR-D6-06) > the 4.5 A carried for the CoreWing servo BEC "
               "(CL-F3-SERVO-BEC): the UBEC stays. The drop rule (<= 1.1 A per servo) is not met.")
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
          how="Weigh each item on arrival (T-PWR-ARRIVAL); A3 replaces the EST rows.",
          note="D-48: power 648 g incl. the CoreWing power board (28 g EST; one retailer lists the PDB board alone at "
               "11.4 g, kept at 28 until weighed).")
kit.claim("CL-F1-POWER-BUDGET", "Power allocation left after the pack", calc="CALC-F1-MASS", output="budget_g",
          unit="g", how="P:mass.allocation_g.power minus P:battery.mass_kg; follows A1's allocation.")

kit.claim("CL-F1-PMOD-RISE", "Power-board link 28 AWG 5 V conductor, steady rise at 2 x FC 5 V load",
          calc="CALC-F1-PMOD", output="rise_5v_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          how="T-F1-SERVO-STALL: meter in the 5 V line of the GH link while the FC, GPS, RX and airspeed run.")
kit.claim("CL-F1-PMOD-SERVO-RISE", "Power-board link if servo stall current ran through it (not accepted)",
          calc="CALC-F1-PMOD", output="rise_stall_c", unit="degC", parts=["PWR-003", "PWR-005"],
          how="Continuity check on the built stack: FC servo-rail + to the power-board Vx pad open (no path).",
          note="above P:electrical.wire_temp_rise_max_c: the servo rail is fed by the UBEC only and the CoreWing "
               "Vx must not reach the FC servo rail through the link (CR-F1-29). Also above the ~1 A per JST-GH pin.")

# ---------------------------------------------------------------- tests
kit.test("T-F1-WIRE-HEAT", "Wire heat runs", verifies=["CL-F1-MAIN-RISE", "CL-F1-MAIN-PEAK", "CL-F1-ESC-RISE",
                                                         "CL-F1-ESC-PEAK", "CL-F1-BUNDLE-RISE", "CL-F1-BUNDLE-PEAK",
                                                         "CL-F1-PACKLEAD-RISE",
                                                         "CL-F1-PACKLEAD-PEAK"],
         procedure="Bench supply (>= 40 A) + load; built power stack (10 AWG jumpers) in a closed pod mock-up at 30 A, "
                   "16 AWG pair in a taped XPS groove at 8.4 A, two pairs through a 50 mm straw at 8.4 A each, each "
                   "10 min; K-type thermocouples mid-lead under foam tape; then 50 A for 2 s on the 16 AWG. Pass: "
                   "rise <= 10 degC steady (jumpers: above their joints), <= 30 degC peak, pack leads <= 20 degC.")
kit.test("T-F1-CONN-HEAT", "AS150U heat run", verifies=["CL-F1-AS150U-CONT"],
         procedure="38 A for 10 min through a mated pair; IR thermometer on the housing; rise <= 30 degC.")
kit.test("T-F1-DROP", "Path resistance", verifies=["CL-F1-R-EXT", "CL-F1-DROP-CONT", "CL-F1-DROP-PEAK"],
         procedure="20 A load step from the pack; meter across pack terminals and across one ESC's pads; "
                   "R = dV/dI. Pass: drop <= 2 % at 30 A.")
kit.test("T-F1-SENSOR-CAL", "Current sensor calibration", verifies=["CL-F1-ILIM-WORST", "CL-F1-SENSOR-CONT"],
         procedure="Clamp meter on the main lead at 5, 15, 25, 30 A (motors on the restrained frame); set "
                   "BATT_AMP_PERVLT so BAT.Curr is within 5 %; record the value for F4.")
kit.test("T-F1-SERVO-STALL", "Servo stall current and rail voltage", verifies=["CL-F1-SERVO-BEC-REQ", "CL-F1-PMOD-RISE",
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
    """data/derating.csv (current, length, gauge, drop, temperature) and data/gauge_sweep.csv, under __main__ only."""
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(exist_ok=True)
    v = kit.value("P:battery.v_nom")
    rows = [("run", "awg", "len_m", "i_cont_a", "rise_cont_c", "peak_normal_c", "peak_fault_c", "r_loop_mohm",
             "drop_cont_pct", "mass_g")]
    for k in ("main", "esc", "esc18", "feed", "bus"):
        rl = out.get(f"{k}_r_loop_mohm", float("nan"))
        rows.append((k, out[f"{k}_awg"], round(out[f"{k}_len_m"], 3), round(out[f"{k}_i_cont_a"], 2),
                     round(out[f"{k}_rise_c"], 1), round(out.get(f"{k}_peak_normal_c", float("nan")), 1),
                     round(out.get(f"{k}_peak_fault_c", float("nan")), 1), round(rl, 2),
                     round(100 * out[f"{k}_i_cont_a"] * rl * 1e-3 / v, 3), round(out[f"{k}_mass_g"], 1)))
    for k, (name, lb, fb) in enumerate(kit.value("ASM-F1-BUNDLE")):
        rows.append((f"bundle: {name}", out["esc_awg"], lb, round(out["esc_i_cont_a"], 2),
                     round(out[f"bundle{k}_rise_c"], 1), float("nan"), round(out[f"bundle{k}_peak_fault_c"], 1),
                     float("nan"), float("nan"), float("nan")))
    pl = kit.nodes["CALC-F1-PACKLEAD"]["outputs"]
    i_c = round(out["main_i_cont_a"], 2)
    for k, name in (("lead", "packlead"), ("lead_alt", "packlead12")):
        rows.append((name, pl[f"{k}_awg"], kit.value("ASM-F1-PACKLEAD")[2], i_c, round(pl[f"{k}_rise_c"], 1),
                     float("nan"), round(pl[f"{k}_peak_fault_c"], 1), round(pl[f"{k}_r_loop_mohm"], 2),
                     round(100 * i_c * pl[f"{k}_r_loop_mohm"] * 1e-3 / v, 3), float("nan")))
    with open(d / "derating.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    od = kit.value("ASM-F1-WIRE-OD")
    f_pod, f_chan, f_pair, eps = kit.value("ASM-F1-COOLING")
    ta = max(kit.value("P:env.ambient_design_c"))
    pod, chan = (f_pod, f_pair, eps), (f_chan, 1.0, eps)
    i_tr = max(a for _, s_, a in kit.value("CL-F1-PROFILE") if s_ <= 60)
    i_esc_lim = kit.value("P:propulsion.current_max_per_motor_a")
    cases = [("pack path, continuous", out["main_i_cont_a"], pod),
             (f"pack path, transition {i_tr:.1f} A if held", i_tr, pod),
             ("ESC lead, hover share", out["esc_i_cont_a"], chan),
             (f"ESC lead, limiter {i_esc_lim:.1f} A if held", i_esc_lim, chan)]
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
