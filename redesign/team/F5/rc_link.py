"""F5 RC link, telemetry and ground station: link budget, range-check pass line, antenna clearance, e-stop latency.

Run:  python -I redesign/team/F5/rc_link.py      -> claims.json beside this file
Then: python -I redesign/proofs/build_graph.py   -> confirms nothing drifted

What this script owns. The 2.4 GHz ExpressLRS (ELRS) link between the RadioMaster Pocket (internal ELRS module) and
the RP3 V2 diversity receiver in the pod: uplink margin at the fence and at the VLOS limit (R-RC-LINK), the RSSI a
reduced-power ground range check must show to prove that margin (replaces the bare "100 m at 10 mW" line), the
antenna clearance to carbon, the worst-case latency of a switch channel (R-ARM-KILL e-stop) and the time from link
loss to the ArduPilot RC failsafe (R-FAILSAFES). Legal power is checked against 47 CFR 15.247. Free-space path loss
plus a lumped implementation loss is the model (Friis); the ground range check then measures the real loss.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
RX, TX = "AVN-003", "GND-001"
ANT_COST_USD = 6.0        # two 150 mm U.FL 2.4 GHz T-antennas, estimate from CR-F3-15 (I1 prices, CR-F5-11)
GND_TX_MASS_G = 330.0     # Pocket ~235 g + 2 x 18650 ~47 g: seller figures, UNVERIFIED (flight false, not rolled up)

# ---------------------------------------------------------------- sources
kit.source("SRC-F5-ELRS-SIGNAL", "ExpressLRS: Signal Health (sensitivity limit per packet rate)", kind="web",
           url="https://www.expresslrs.org/info/signal-health/", checked="2026-11-09",
           where="2.4 GHz table: 50 Hz -115, 100 Hz Full -112, 150 Hz -112, 250 Hz -108, 333 Hz Full -105, "
                 "500 Hz -105 dBm; RSSI alarm 5-10 dB above the limit")
kit.source("SRC-F5-AP-ELRS", "ArduPilot: Crossfire and ELRS RC systems", kind="web",
           url="https://ardupilot.org/copter/docs/common-tbs-rc.html", checked="2026-11-09",
           where="CRSF mode: SERIALx_PROTOCOL 23, RSSI_TYPE 3, RC_OPTIONS bit 13 (420 kbaud for ELRS), UART must have "
                 "DMA on F4/F7, TX must transmit before the RX powers up; MAVLink mode: SERIALx_PROTOCOL 2, "
                 "RSSI_TYPE 5, WiFi forwarding from the TX module")
kit.source("SRC-F5-ELRS-MAVLINK", "ExpressLRS: MAVLink mode (3.5+, TX Backpack 1.5+)", kind="web",
           url="https://www.expresslrs.org/software/mavlink/",
           where="ESP-based RX only; telemetry ratio fixed 1:2; internal TX modules reach the GCS through the TX "
                 "backpack WiFi. Read through a search summary only", status="UNVERIFIED")
kit.source("SRC-F5-POCKET", "RadioMaster Pocket user manual (ELRS version)", kind="datasheet",
           url="https://xcopter.com/download/Pocket_User_Manual.pdf",
           where="internal ELRS 25-250 mW (FCC), 100 mW at 500 Hz recommended; 2 x 18650 not included. Read through "
                 "a search summary; BOM line R01 names the 'Pocket Crush' variant: I1 confirms it is the same module",
           status="UNVERIFIED")
kit.source("SRC-F5-RP3V2", "RadioMaster RP3 V2 ELRS 2.4 GHz nano receiver (retailer listings)", kind="web",
           url="https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver",
           where="antenna diversity, two 65 mm T-antennas (UFL), telemetry up to 100 mW, TCXO, 5 V, CRSF, 4.6 g, "
                 "22 x 13 x 4 mm. Maker page returned 429; values from 3 retailer listings that agree",
           status="UNVERIFIED")
kit.source("SRC-F5-FCC-15247", "47 CFR 15.247, operation in 902-928, 2400-2483.5, 5725-5850 MHz", kind="standard",
           url="https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.247",
           where="(b)(1): 1 W conducted for FHSS in 2400-2483.5 MHz with >= 75 hopping channels; (b)(4): 6 dBi "
                 "antenna allowance, i.e. 36 dBm EIRP", status="UNVERIFIED")
kit.source("SRC-F5-FRIIS", "Free-space path loss, ITU-R P.525", kind="standard",
           url="https://www.itu.int/rec/R-REC-P.525/en",
           where="FSPL[dB] = 32.44 + 20 log10(f[MHz]) + 20 log10(d[km])", checked="2026-11-09")

# ---------------------------------------------------------------- assumptions (link settings and losses)
kit.assumption("ASM-F5-FREQ", "Centre of the 2.4 GHz ISM band", "Link frequency for path loss 2 440 MHz",
               basis="ELRS hops 2 400-2 480 MHz; path loss differs by < 0.3 dB across the band", value=2440.0,
               unit="MHz", cites=["SRC-F5-FRIIS"])
kit.assumption("ASM-F5-RATE", "ELRS 150 Hz LoRa, telemetry 1:4, Wide switches", "Packet rate 150 Hz, sensitivity "
               "-112 dBm; telemetry ratio 1:4 (37.5 Hz downlink for CRSF passthrough); switch mode Wide",
               basis="150 Hz gives 4 dB more margin than 250 Hz at a 6.7 ms frame, ample for a 2.6 kg wing; ArduPilot "
                     "passthrough wants >= 25 Hz telemetry (discuss.ardupilot.org CRSF thread)",
               value={"rate_hz": 150.0, "sens_dbm": -112.0, "aux_slots": 7}, unit="Hz,dBm,-",
               cites=["SRC-F5-ELRS-SIGNAL"])
kit.assumption("ASM-F5-POWER", "Flight TX power 100 mW fixed; check power 25 mW", "TX power fixed at 100 mW "
               "(20 dBm), dynamic power off; ground range check at the Pocket's lowest setting 25 mW (14 dBm)",
               basis="Pocket manual: 25-250 mW, 100 mW recommended; fixed power makes logs comparable flight to flight",
               value={"p_op_dbm": 20.0, "p_test_dbm": 13.98, "p_max_dbm": 23.98}, unit="dBm",
               status="UNVERIFIED", cites=["SRC-F5-POCKET"])
kit.assumption("ASM-F5-ANT-GAIN", "Antenna gains 0 dBi each end", "TX and RX antenna gain taken as 0 dBi "
               "(dipoles are ~2 dBi; nulls and cable loss eat it)", basis="conservative; the range check measures it",
               value={"g_tx_dbi": 0.0, "g_rx_dbi": 0.0, "g_tx_max_dbi": 2.15}, unit="dBi")
kit.assumption("ASM-F5-LOSS", "Implementation loss 16 dB", "Airframe shadowing by the pack, spar and tubes 8 dB, "
               "polarisation mismatch (the aircraft turns 90 deg at transition) 3 dB, pilot body and ground "
               "multipath 5 dB", basis="engineering estimate for a small UAV at < 120 m AGL; the ground range check "
                                       "in two attitudes replaces it with a measured value",
               value=16.0, unit="dB", status="UNVERIFIED")
kit.assumption("ASM-F5-MARGIN-MIN", "Fade margin >= 10 dB", "Required uplink margin above sensitivity at the "
               "design distance", basis="ELRS guidance warns 5-10 dB above the limit; 10 dB covers a deep fade and "
                                        "keeps the warning alarm above the failsafe point",
               value=10.0, unit="dB", cites=["SRC-F5-ELRS-SIGNAL"])
kit.assumption("ASM-F5-ELRS-LOSS-T", "ELRS link-loss detection 1.0 s", "Time from the last good uplink packet to "
               "the RX stopping CRSF channel frames", basis="ELRS disconnects after roughly 1 s without packets at "
                                                           "150 Hz; measured on the bench (T-F5-FS-BENCH)",
               value=1.0, unit="s", status="UNVERIFIED")
kit.assumption("ASM-F5-FS-SHORT", "ArduPilot RC_FS_TIMEOUT 1.0 s + 0.2 s debounce", "Plane 4.7 declares RC loss "
               "RC_FS_TIMEOUT (1.0 s, default, stated in K09L.param) after the last valid frame, plus 10 radio-task "
               "checks. FS_SHORT_TIMEOUT (1.5 s) no longer exists in 4.7 (CDR-26, D-124). Holds only with the receiver "
               "in failsafe mode No Pulses",
               basis="redesign/subsystems/flight-software/K09L.param section 10; team/F4/claims.json CL-F4-RC-FS-QLAND "
                     "1.2 s; SITL 2026-11-13: 1.0-1.15 s from the last frame to QLAND (team/F4/sitl/RESULTS.md)",
               value=1.2, unit="s")
kit.assumption("ASM-F5-ANT-CLEAR", "Antenna clearance >= lambda/4", "Active element of each RX antenna at least a "
               "quarter wavelength from carbon, the pack, ESC leads and the other antenna element",
               basis="common practice for dipoles near conductors (detuning, pattern null)", value=0.25, unit="-")

FT = 0.3048


def fspl_db(f_mhz, d_m):
    return 32.44 + 20 * math.log10(f_mhz) + 20 * math.log10(d_m / 1000.0)


# ---------------------------------------------------------------- 1. uplink budget at the VLOS limit
@kit.calc("CALC-F5-LINK", title="Uplink budget at the VLOS limit at 400 ft",
          equation="d = sqrt(vlos^2 + h^2); Prx = Ptx + Gtx + Grx - FSPL(f, d) - L; margin = Prx - S",
          inputs={"vlos": P + "requirements.vlos_max_m", "ceil_ft": P + "mission.ceiling_ft_agl",
                  "f": "ASM-F5-FREQ", "rate": "ASM-F5-RATE", "pw": "ASM-F5-POWER", "g": "ASM-F5-ANT-GAIN",
                  "loss": "ASM-F5-LOSS"},
          units={"vlos": "m", "ceil_ft": "ft"}, assumes=["ASM-F5-LOSS"], cites=["SRC-F5-FRIIS"])
def link_budget(vlos, ceil_ft, f, rate, pw, g, loss):
    d = math.hypot(vlos, ceil_ft * FT)
    prx = pw["p_op_dbm"] + g["g_tx_dbi"] + g["g_rx_dbi"] - fspl_db(f, d) - loss
    margin = prx - rate["sens_dbm"]
    # distance at which the margin would fall to zero (same losses)
    d0 = d * 10 ** (margin / 20.0)
    return {"d_slant_m": d, "fspl_db": fspl_db(f, d), "prx_dbm": prx, "margin_db": margin, "range_0db_m": d0}


# ---------------------------------------------------------------- 2. ground range check pass line
@kit.calc("CALC-F5-RANGECHECK", title="Ground range-check RSSI pass line",
          equation="RSSI_req = S + M + 20 log10(d_req / d_test) - (P_op - P_test); predicted = P_test - FSPL(d_test) - L",
          inputs={"d_req": "CL-F5-LINK-DIST", "d_test": P + "requirements.range_check_min_m", "f": "ASM-F5-FREQ",
                  "rate": "ASM-F5-RATE", "pw": "ASM-F5-POWER", "g": "ASM-F5-ANT-GAIN", "loss": "ASM-F5-LOSS",
                  "m": "ASM-F5-MARGIN-MIN"},
          units={"d_req": "m", "d_test": "m"})
def range_check(d_req, d_test, f, rate, pw, g, loss, m):
    req = rate["sens_dbm"] + m + 20 * math.log10(d_req / d_test) - (pw["p_op_dbm"] - pw["p_test_dbm"])
    pred = pw["p_test_dbm"] + g["g_tx_dbi"] + g["g_rx_dbi"] - fspl_db(f, d_test) - loss
    return {"rssi_req_dbm": req, "rssi_pred_dbm": pred, "pred_over_req_db": pred - req,
            "alarm_warn_dbm": rate["sens_dbm"] + m, "alarm_crit_dbm": rate["sens_dbm"] + 5.0}


# ---------------------------------------------------------------- 3. antenna clearance
@kit.calc("CALC-F5-ANT", title="Antenna clearance to conductors", equation="c_min = k * c0 / f",
          inputs={"f": "ASM-F5-FREQ", "k": "ASM-F5-ANT-CLEAR"}, output="clear_m")
def antenna_clearance(f, k):
    return k * 299_792_458.0 / (f * 1e6)


# ---------------------------------------------------------------- 4. switch-channel latency (e-stop) and failsafe time
@kit.calc("CALC-F5-LATENCY", title="Switch latency and RC-loss-to-failsafe time",
          equation="t_switch = (aux_slots + 1) / rate / LQ; t_fs = t_elrs + RC_FS_TIMEOUT + debounce",
          inputs={"rate": "ASM-F5-RATE", "lq": P + "requirements.rc_lq_min", "t_elrs": "ASM-F5-ELRS-LOSS-T",
                  "t_short": "ASM-F5-FS-SHORT"})
def latency(rate, lq, t_elrs, t_short):
    # Wide mode: one aux channel (ch6-12) per packet, round robin; +1 packet for the frame in flight;
    # dividing by LQ stretches it for lost packets at the worst accepted link quality
    t_sw = (rate["aux_slots"] + 1) / rate["rate_hz"] / lq
    return {"t_switch_s": t_sw, "t_failsafe_s": t_elrs + t_short}


# ---------------------------------------------------------------- 5. legal power
@kit.calc("CALC-F5-EIRP", title="Maximum EIRP the Pocket can radiate",
          equation="EIRP = P_max + G_tx,max", inputs={"pw": "ASM-F5-POWER", "g": "ASM-F5-ANT-GAIN"},
          cites=["SRC-F5-FCC-15247"], output="eirp_dbm")
def eirp(pw, g):
    return pw["p_max_dbm"] + g["g_tx_max_dbi"]


# ---------------------------------------------------------------- claims
kit.claim("CL-F5-LINK-DIST", "Design link distance (VLOS limit at the 400 ft ceiling)", calc="CALC-F5-LINK",
          output="d_slant_m", unit="m", verifies=["R-RC-LINK"], parts=[RX],
          how="Geometry: sqrt(500^2 + 121.9^2). The 250 m fence (F4) keeps flights inside 273 m slant.")
kit.claim("CL-F5-LINK-MARGIN", "Uplink fade margin at 100 mW, 150 Hz, at the VLOS limit", calc="CALC-F5-LINK",
          output="margin_db", unit="dB", limit=(">=", "ASM-F5-MARGIN-MIN"), verifies=["R-RC-LINK"], parts=[RX, TX],
          assumes=["ASM-F5-LOSS"],
          how="Flight logs (RSSI, RXLQ) at the farthest point of each fixed-wing flight: 1RSS/2RSS >= -102 dBm "
              "and LQ >= 0.9 (T-F5-FLIGHT-LINK); ground check T-F5-RANGE first.")
kit.claim("CL-F5-LINK-RANGE-0DB", "Range at which the modelled margin reaches 0 dB", calc="CALC-F5-LINK",
          output="range_0db_m", unit="m", limit=(">=", P + "requirements.vlos_max_m"), parts=[RX, TX],
          how="Information only: shows the VLOS limit, not the radio, bounds the operating radius.")
kit.claim("CL-F5-RC-RSSI-REQ", "Range check pass line: RX RSSI at 100 m, 25 mW", calc="CALC-F5-RANGECHECK",
          output="rssi_req_dbm", unit="dBm", verifies=["R-RC-LINK"], parts=[RX, TX],
          how="T-F5-RANGE: better of 1RSS/2RSS at 100 m, 25 mW, in both hover and cruise attitude, >= this value "
              "and LQ >= 0.9; this proves >= 10 dB margin at 515 m and 100 mW.")
kit.claim("CL-F5-RC-RSSI-PRED", "Predicted RX RSSI at the range check", calc="CALC-F5-RANGECHECK",
          output="rssi_pred_dbm", unit="dBm", limit=(">=", "CL-F5-RC-RSSI-REQ"), parts=[RX, TX],
          assumes=["ASM-F5-LOSS"], how="Compare with the measured RSSI in T-F5-RANGE; a shortfall means the 16 dB "
                                         "implementation loss is optimistic (move the antennas, CR to D2/F3).")
kit.claim("CL-F5-RSSI-WARN", "Transmitter RSSI warning alarm", calc="CALC-F5-RANGECHECK", output="alarm_warn_dbm",
          unit="dBm", parts=[TX], how="EdgeTX telemetry alarm on 1RSS; check it sounds when the TX is shielded.")
kit.claim("CL-F5-RSSI-CRIT", "Transmitter RSSI critical alarm", calc="CALC-F5-RANGECHECK", output="alarm_crit_dbm",
          unit="dBm", parts=[TX], how="EdgeTX telemetry alarm on 1RSS; 5 dB above the -112 dBm limit.")
kit.claim("CL-F5-ANT-CLEAR", "Minimum RX antenna clearance to carbon, pack and ESC leads", calc="CALC-F5-ANT",
          output="clear_m", unit="m", parts=[RX],
          how="Ruler on the installed pod: each 30 mm active element >= 31 mm from the CF spar, pack and power "
              "leads; one element vertical (z), one along x.")
kit.claim("CL-F5-SWITCH-LATENCY", "Worst-case switch-channel (e-stop ch 9) link latency", calc="CALC-F5-LATENCY",
          output="t_switch_s", unit="s", limit=("<=", 1.0), verifies=["R-ARM-KILL"], parts=[RX, TX],
          how="SITL S13 / bench: flip ch 9, read RCIN in the DataFlash log against the motor outputs (props off).")
kit.claim("CL-F5-FS-TIME", "Transmitter off to ArduPilot RC failsafe", calc="CALC-F5-LATENCY",
          output="t_failsafe_s", unit="s", verifies=["R-FAILSAFES"], parts=[RX],
          assumes=["ASM-F5-ELRS-LOSS-T"],
          how="T-F5-FS-BENCH: props off, armed in QSTABILIZE, switch the TX off; log time to the FS message.")
kit.claim("CL-F5-EIRP-MAX", "Pocket EIRP at its maximum setting", calc="CALC-F5-EIRP", output="eirp_dbm",
          unit="dBm", limit=("<=", 36.0), parts=[TX],
          how="47 CFR 15.247(b): 30 dBm conducted + 6 dBi = 36 dBm. Read the FCC ID on the Pocket and RP3 labels on "
              "arrival; keep the FCC (not LBT, not unlocked) ELRS regulatory domain.")
kit.claim("CL-F5-ADDED-COST", "RC, telemetry and GCS spend beyond BOM lines A03, R01, R02", value=ANT_COST_USD,
          unit="USD", parts=[TX, RX],
          how="BOM.csv: A03 $22.04 + R01 $71.65 + R02 $27.00 incl. tax = $120.69 already carried; the only addition "
              "is a pair of 150 mm U.FL 2.4 GHz T-antennas for the RP3 V2 (CR-F3-15: stock 65 mm leads do not reach "
              "the hatch-top and nose tubes). I1 prices it at order (CR-F5-11). Telemetry rides on the ELRS link and "
              "the GCS is Mission Planner on a team laptop (no purchase).",
          note="Estimate from CR-F3-15 (~$6), UNVERIFIED until I1 fetches a listing. The pessimistic reserve is "
               "$312.99 vs the $309 crash (+$3.99, D-57), so A1 pulls I1's first lever (borrow the soldering kit, "
               "+$94.82). A 915 MHz SiK pair (~$35-60) stays out")

# ---------------------------------------------------------------- 6. timed transition switch (B3 CL-4, D-149 replacement)
# TRANSITION-SWITCH.md; functions in transition_switch.py (same folder)
sys.path.insert(0, str(HERE))
import transition_switch as tsw  # noqa: E402

kit.source("SRC-F5-AP-THRCURVE", "ArduPilot Plane-4.7.2: pilot throttle path in QSTABILIZE", kind="web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/ArduPlane/quadplane.cpp",
           checked="2026-11-14",
           where="get_pilot_throttle(): control_in / get_range(), then throttle_curve(get_throttle_hover(), "
                 "Q_THROTTLE_EXPO, .); AP_Math.cpp throttle_curve/expo_curve; RC_Channel.h 'int16_t control_in'; "
                 "radio.cpp channel_throttle->set_range(100), set_default_dead_zone(30); RC_Channel.cpp "
                 "pwm_to_range_dz. So QSTABILIZE throttle moves in 1 % stick steps")
kit.source("SRC-F5-AP-MODESW", "ArduPilot Plane-4.7.2: flight-mode switch read", kind="web",
           url="https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/libraries/RC_Channel/RC_Channel.cpp",
           checked="2026-11-14",
           where="read_6pos_switch: < 1231 / 1361 / 1491 / 1621 / 1750 us -> positions 1-6; debounce_completed with "
                 "SWITCH_DEBOUNCE_TIME_MS 200; Plane.cpp schedules read_mode_switch at 7 Hz, read_radio at 50 Hz")
kit.source("SRC-F5-EDGETX-LS", "EdgeTX v2.11.3 source and B&W manual: logical switches, override, mixes", kind="web",
           url="https://raw.githubusercontent.com/EdgeTX/edgetx/v2.11.3/radio/src/switches.cpp", checked="2026-11-14",
           where="switches.cpp: delay/duration and sticky/edge stepped by logicalSwitchesTimerTick every 0.1 s "
                 "(mixer.cpp), a delay restarts when the condition drops; mixer.cpp applyLimits: Override CHx returns "
                 "calc100toRESX(value) before limits; MLTPX_REPL replaces the lines above. Manual pages "
                 "https://manual.edgetx.org/bw-radios/model-select/logical-switches, .../special-functions, "
                 ".../inputs-mixes-and-outputs/mixes.md (read 2026-11-14)")
kit.assumption("ASM-F5-TRANS-WINDOW", "B3 physical window for the static entry T0/W (12 deg/s, w0 4 m/s)",
               "Lowest T0/W that passes use, gust and handover with a 4 m/s pre-climb, and highest T0/W that keeps "
               "the sagged-pack fraction <= 0.80", basis="team/B3/results/closure1114.json window.rate12_w04 "
                                                       "(B3 closure report section 1.3)",
               value=[1.2827, 1.3968], unit="-")
kit.assumption("ASM-F5-TRANS-RC3", "Throttle channel calibration RC3_MIN 988, RC3_MAX 2012, RC3_DZ 30",
               "EdgeTX -100 / +100 % over CRSF reach ArduPilot as 988 / 2012 us; dead zone is Plane's default 30 us. "
               "F4 states them in K09L.param (CR-F5-15) so the override lands in a known control_in step",
               basis="ArduPilot CRSF decoder (CRSF 172..1811 -> 988..2012 us); radio.cpp set_default_dead_zone(30)",
               value=[988, 2012, 30], unit="us", cites=["SRC-F5-AP-THRCURVE"])
kit.assumption("ASM-F5-TRANS-CHAIN", "Pulse error EdgeTX -> CRSF -> ELRS 10-bit -> ArduPilot <= 2 us",
               "Ch 1-4 travel at 10 bit in every ELRS packet (~1 us per step) plus the 0.625 us CRSF step and "
               "rounding", basis="estimate (EST); T-F5-TRANS-BENCH reads the RCIN value", value=2.0, unit="us",
               status="UNVERIFIED")
kit.assumption("ASM-F5-TRANS-SET", "Transition switch setting: stick step 67 %, Q_THROTTLE_EXPO 0.2, delays 0.9 / 1.2 s (D-181 pre-climb 1.0 s, B3 closure)",
               "Override CH3 so control_in = 67 at theta_h 0.49 (E1 hover duty, K09L.param Q_M_THST_HOVER start "
               "value); FBWA command 0.9 s after the latch; override released 1.2 s after the FBWA command",
               basis="transition_switch.py setting_table and timing(); re-picked from the table if the learnt "
                     "Q_M_THST_HOVER leaves the band (TRANSITION-SWITCH.md section 4)",
               value={"theta_h": 0.49, "k": 67, "alpha": 0.2, "d_fbwa": 0.9, "d_release": 1.2}, unit="-,%,-,s,s")


@kit.calc("CALC-F5-TRANS", title="Transition switch: entry throttle realised in QSTABILIZE, timing at the FC",
          equation="throttle_in = throttle_curve(theta_h, alpha, k/100); r = throttle_in/theta_h; "
                   "r_lo,hi = r_B3 x window_lo,hi / band_low,high; hold = d - 0.1 + ch6 + debounce(7 Hz, 0.2 s) - ch3",
          inputs={"t0": "ASM-B3-TRANS-T0", "t0_low": "CL-B3-TRANS-T0-LOW", "t0_high": "CL-B3-TRANS-T0-HIGH",
                  "win": "ASM-F5-TRANS-WINDOW", "rc3": "ASM-F5-TRANS-RC3", "s": "ASM-F5-TRANS-SET",
                  "t_sw": "CL-F5-SWITCH-LATENCY"},
          assumes=["ASM-F5-TRANS-CHAIN"], cites=["SRC-F5-AP-THRCURVE", "SRC-F5-AP-MODESW", "SRC-F5-EDGETX-LS"])
def transition_switch(t0, t0_low, t0_high, win, rc3, s, t_sw):
    a = tsw.analyse(t0[0], t0_low, t0_high, win[0], win[1], s["theta_h"], s["alpha"], s["k"], tuple(rc3),
                    s["d_fbwa"], s["d_release"], t_sw)
    fz = tsw.fuzz(a["override"]["pct"], n_runs=200, seconds=120)
    return {"throttle_in": a["throttle_in"], "r_real": a["r_real"], "r_lo": a["r_lo"], "r_hi": a["r_hi"],
            "r_step_pct": 100 * a["r_step_per_pct"] / a["r_real"], "theta_lo": a["theta_band"][0], "theta_hi": a["theta_band"][1],
            "override_pct": a["override"]["pct"], "pwm_margin_us": a["override"]["margin_us"],
            "hold_min_s": a["hold_min_s"], "hold_max_s": a["hold_max_s"],
            "release_min_s": a["release_after_fbwa_min_s"], "fuzz_violations": fz["violations"],
            "fuzz_sequences": fz["sequences_completed"],
            "fw_slots_at_neutral_or_ends": sum(tsw.SLOT_MODE[tsw.slot_of_pwm(p)] in tsw.FW for p in (988, 1500, 2012))}


kit.claim("CL-F5-TRANS-THR-IN", "QSTABILIZE throttle_in under the CH3 override (theta_h 0.49)", calc="CALC-F5-TRANS",
          output="throttle_in", unit="-", parts=[TX],
          how="SITL (transition_sitl.py) and T-F5-TRANS-BENCH: QTUN.ThI during the pre-climb.")
kit.claim("CL-F5-TRANS-R-REAL-LO", "Realised entry ratio throttle_in / theta_h, against B3's low window edge",
          calc="CALC-F5-TRANS", output="r_real", unit="-", limit=(">=", "CL-F5-TRANS-R-LO"), parts=[TX],
          how="Ratio of QTUN.ThI to QTUN.ThH in the pre-climb (SITL, bench, every transition log).")
kit.claim("CL-F5-TRANS-R-REAL-HI", "Realised entry ratio throttle_in / theta_h, against B3's high window edge",
          calc="CALC-F5-TRANS", output="r_real", unit="-", limit=("<=", "CL-F5-TRANS-R-HI"), parts=[TX],
          how="As -LO.")
kit.claim("CL-F5-TRANS-R-LO", "Lowest entry ratio that keeps B3's low band edge in the window", calc="CALC-F5-TRANS",
          output="r_lo", unit="-", how="1.285 x 1.2827 / 1.2908 (B3 window and band).")
kit.claim("CL-F5-TRANS-R-HI", "Highest entry ratio that keeps B3's high band edge in the window", calc="CALC-F5-TRANS",
          output="r_hi", unit="-", how="1.285 x 1.3968 / 1.3893.")
kit.claim("CL-F5-TRANS-R-STEP", "Entry-ratio change per 1 % stick step (ArduPilot control_in is an integer)",
          calc="CALC-F5-TRANS", output="r_step_pct", unit="%",
          how="Information: one step (1.39 %) is wider than the window (1.17 %), so the stick step is picked per "
              "theta_h and Q_THROTTLE_EXPO fills the gaps (table in TRANSITION-SWITCH.md).")
kit.claim("CL-F5-TRANS-THETA-LO", "Lowest learnt hover throttle the 67 % setting covers", calc="CALC-F5-TRANS",
          output="theta_lo", unit="-", how="Pre-flight: read Q_M_THST_HOVER; outside the band pick the table row.")
kit.claim("CL-F5-TRANS-THETA-HI", "Highest learnt hover throttle the 67 % setting covers", calc="CALC-F5-TRANS",
          output="theta_hi", unit="-", how="As -LO.")
kit.claim("CL-F5-TRANS-PWM-MARGIN", "Override pulse distance to the edge of its ArduPilot control_in step",
          calc="CALC-F5-TRANS", output="pwm_margin_us", unit="us", limit=(">=", "ASM-F5-TRANS-CHAIN"), parts=[TX, RX],
          how="T-F5-TRANS-BENCH: Mission Planner RC3 reads the predicted pulse within 2 us.")
kit.claim("CL-F5-TRANS-HOLD-MIN", "Shortest time the FC spends in QSTABILIZE with the override before FBWA",
          calc="CALC-F5-TRANS", output="hold_min_s", unit="s", limit=(">=", 1.0), parts=[TX],
          how="SITL and bench: RCIN.C3 step to MODE FBWA in the DataFlash log.")
kit.claim("CL-F5-TRANS-HOLD-MAX", "Longest QSTABILIZE override time before FBWA (B3 to check its pre-climb model)",
          calc="CALC-F5-TRANS", output="hold_max_s", unit="s", parts=[TX],
          how="Information for B3 (request CL-F5-B3): B3 closure hold 1.0 s: FC hold 1.08-1.38 s; B3 checks CL-B3-TRANS-CLIMB at 1.38 s (< 60 m).")
kit.claim("CL-F5-TRANS-RELEASE", "Override release after FBWA is active at the FC", calc="CALC-F5-TRANS",
          output="release_min_s", unit="s", limit=(">=", 0.5), parts=[TX],
          how="SITL and bench: MODE FBWA to the RCIN.C3 step back to the stick.")
kit.claim("CL-F5-TRANS-NO-DIRECT-FW", "Fixed-wing slot commanded outside the timed sequence (logic model, random "
          "switch histories)", calc="CALC-F5-TRANS", output="fuzz_violations", unit="count", limit=("<=", 0),
          parts=[TX], how="EdgeTX Companion simulator and T-F5-TRANS-BENCH channel monitor: every SB/SC/SA "
                          "position and order; FBWA only after SC flipped down from QSTABILIZE, armed, stick > 40 %.")
kit.claim("CL-F5-TRANS-NEUTRAL-Q", "Fixed-wing modes at 988 / 1500 / 2012 us with the requested FLTMODE order",
          calc="CALC-F5-TRANS", output="fw_slots_at_neutral_or_ends", unit="count", limit=("<=", 0), parts=[TX],
          how="SITL S1b with FLTMODE1-6 = 17, 5, 7, 18, 11, 19: 988 / 1500 / 2012 us read QSTABILIZE / QHOVER / QLOITER.")
kit.test("T-F5-TRANS-BENCH", "Transition switch bench test, props off",
         verifies=["CL-F5-TRANS-PWM-MARGIN", "CL-F5-TRANS-HOLD-MIN", "CL-F5-TRANS-RELEASE", "CL-F5-TRANS-NO-DIRECT-FW"],
         procedure="TRANSITION-SWITCH.md section 6: EdgeTX Companion first, then the radio with the FC on USB, props "
                   "off, aircraft tied down: switch matrix, RC3 pulse, armed sequence with DataFlash log, aborts.")
kit.test("T-F5-TRANS-SITL", "Transition switch SITL check (stage A, logic)",
         verifies=["CL-F5-TRANS-THR-IN", "CL-F5-TRANS-R-REAL-LO", "CL-F5-TRANS-R-REAL-HI", "CL-F5-TRANS-HOLD-MIN",
                   "CL-F5-TRANS-RELEASE"],
         procedure="python -I redesign/team/F5/transition_sitl.py <rundir> with the EdgeTX logic model driving "
                   "RC_CHANNELS_OVERRIDE at 10 ms of sim time (TRANSITION-SWITCH.md section 7).")

# ---------------------------------------------------------------- ground subsystem declaration (GND, D-46, CR-A4-30/45)
# F5 owns subsystem `ground` (README table). The transmitter is the only ground part with an interface: the radio
# link E-AVN-09 (GND-001 -> AVN-003) that F3 declares in avionics. The laptop (Mission Planner) is team-owned and
# joined by a USB cable on the bench only, so it is not a part. Mass is the seller figure for the record (flight
# false: excluded from the roll-up); the CG stays null while PROPOSED (nothing in the box locates it, D7).
GND_PARTS = [
    {"id": TX, "name": "RC transmitter RadioMaster Pocket (Crush), internal ELRS 2.4 GHz FCC, with 2 x 18650 cells",
     "subsystem": "ground", "status": "PROPOSED", "mass_g": GND_TX_MASS_G, "material": "electronics (bought)",
     "cg_xyz_m": None, "make_or_buy": "buy", "flight": False,
     "qty": 1, "process": "bought; ELRS 3.x FCC domain, EdgeTX model K09L (model match on)",
     "unit_cost_usd": 64.99 + 24.49, "vendor": "RadioMaster (I1 BOM R01) + GetFPV 18650 2-pack (R02)",
     "notes": "radio link E-AVN-09 to AVN-003 (declared by avionics, acknowledged here); 25-250 mW, flown at 100 mW "
              "fixed, range check at 25 mW (T-F5-RANGE); no electrical role (battery inside, no harness wire); "
              "mass about 0.33 kg incl. cells: seller figure, UNVERIFIED, weigh on arrival (T-F5-BENCH)"},
]
GND_ACKS = ["E-AVN-09"]


def write_ground():
    root = HERE.parents[1] / "subsystems" / "ground"
    root.mkdir(parents=True, exist_ok=True)
    keys = ("id", "name", "subsystem", "status", "mass_g", "material", "cg_xyz_m", "make_or_buy", "flight", "notes")
    doc = {"schema": "dbf-interfaces/1", "subsystem": "ground",
           "_note": "GENERATED by redesign/team/F5/rc_link.py (F5 owns `ground`, README; CR-A4-30/45). Edit the "
                    "script, not this file. Every part flight false. GND-001 is part_a of the radio edge E-AVN-09, "
                    "which avionics declares (CT-ELRS-RF, method radio: no wire block, no electrical role).",
           "parts": [{k: p[k] for k in keys} for p in GND_PARTS],
           "edges": [], "acknowledges": GND_ACKS}
    (root / "interfaces.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    with open(root / "parts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part_id", "name", "qty", "make_or_buy", "process", "material", "mass_g", "unit_cost_usd",
                    "vendor_or_file", "notes"])
        for p in GND_PARTS:
            w.writerow([p["id"], p["name"], p["qty"], p["make_or_buy"], p["process"], p["material"], p["mass_g"],
                        "%.2f" % p["unit_cost_usd"], p["vendor"], "flight: false; " + p["notes"]])
    print("wrote", root / "interfaces.json", "and parts.csv")

# ---------------------------------------------------------------- tests
kit.test("T-F5-BENCH", "Arrival bench: versions, bind, model match, channel map", verifies=["CL-F5-SWITCH-LATENCY"],
         procedure="ELRS TX and RX on the same major version (3.x), FCC domain; binding phrase set (kept off the "
                   "repo); model match on, K09-L and twin have different model ids; RC calibration in Mission "
                   "Planner; every channel moves the right way; ch 9 latency from the log. CDR-26: open the "
                   "receiver's ELRS web UI (or the ELRS Lua, 'Other Devices'), set failsafe mode to 'No Pulses', "
                   "save, power-cycle and read it back; then, props off, TX off: Mission Planner shows 'Throttle "
                   "failsafe on' and the RC inputs freeze (they must not jump to preset values).")
kit.test("T-F5-FS-BENCH", "Bench RC failsafe, props off", verifies=["CL-F5-FS-TIME"],
         procedure="Armed in QSTABILIZE, FBWA and CRUISE in turn (props off, tied down), TX off: QLAND in Q modes, "
                   "circle then RTL at 5 s in FW; time from TX off to the FS message <= 2.5 s (model: 1.0 s ELRS + 1.2 s). "
                   "In QHOVER the mode must read QLAND within 3 s of TX off (CL-F4-RC-FS-QLAND); if the receiver "
                   "is not on No Pulses no failsafe appears at all: stop and fix the receiver setting.")
kit.test("T-F5-RANGE", "Ground range check, two attitudes", verifies=["CL-F5-RC-RSSI-REQ", "CL-F5-RC-RSSI-PRED"],
         procedure="25 mW, 150 Hz; aircraft 1 m above ground on a stand, motors spinning props-off at 20 %; at "
                   "100 m read 1RSS/2RSS/RQly for 4 headings in hover attitude and 4 in cruise attitude.")
kit.test("T-F5-FLIGHT-LINK", "In-flight link log review", verifies=["CL-F5-LINK-MARGIN"],
         procedure="After each flight: plot RSSI and RXLQ vs distance from home (DataFlash RSSI msg, EdgeTX SD log); "
                   "min LQ >= 0.9, min RSSI >= -102 dBm at the farthest point.")

if __name__ == "__main__":
    kit.write()
    write_ground()
