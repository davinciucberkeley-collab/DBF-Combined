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
kit.assumption("ASM-F5-FS-SHORT", "ArduPilot FS_SHORT_TIMEOUT 1.5 s", "Plane short RC failsafe after 1.5 s of no RC "
               "input (default, kept by K09L.param)", basis="redesign/subsystems/flight-software/K09L.param section 10",
               value=1.5, unit="s")
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
          equation="t_switch = (aux_slots + 1) / rate / LQ; t_fs = t_elrs + FS_SHORT_TIMEOUT",
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
                   "Planner; every channel moves the right way; ch 9 latency from the log.")
kit.test("T-F5-FS-BENCH", "Bench RC failsafe, props off", verifies=["CL-F5-FS-TIME"],
         procedure="Armed in QSTABILIZE, FBWA and CRUISE in turn (props off, tied down), TX off: QLAND in Q modes, "
                   "circle then RTL at 5 s in FW; time from TX off to the FS message <= 2.5 s.")
kit.test("T-F5-RANGE", "Ground range check, two attitudes", verifies=["CL-F5-RC-RSSI-REQ", "CL-F5-RC-RSSI-PRED"],
         procedure="25 mW, 150 Hz; aircraft 1 m above ground on a stand, motors spinning props-off at 20 %; at "
                   "100 m read 1RSS/2RSS/RQly for 4 headings in hover attitude and 4 in cruise attitude.")
kit.test("T-F5-FLIGHT-LINK", "In-flight link log review", verifies=["CL-F5-LINK-MARGIN"],
         procedure="After each flight: plot RSSI and RXLQ vs distance from home (DataFlash RSSI msg, EdgeTX SD log); "
                   "min LQ >= 0.9, min RSSI >= -102 dBm at the farthest point.")

if __name__ == "__main__":
    kit.write()
    write_ground()
