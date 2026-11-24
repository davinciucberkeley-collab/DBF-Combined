"""E1 propulsion engineer: motor / ESC / prop model and margins for the K09-L quad tailsitter.

Run:  python -I redesign/team/E1/propulsion.py      -> claims.json beside this file + a printed report. Writes
                                                       nothing outside team/E1/: the propulsion parts list is
                                                       printed and compared with the file, not written (CDR-29)
      python -I redesign/team/E1/propulsion.py --write-parts
                                                    -> also rewrites subsystems/propulsion/parts.csv and then runs
                                                       C6's fastener_parts.py, which patches subsystems/*/parts.csv
                                                       and interfaces.json. Only the propulsion owner, on purpose
      python -I redesign/team/E1/plots.py           -> FIG PRP-01 / PRP-02 SVGs (reads this module)

Model (one station = pack share + ESC + SunnySky X3108S KV900 + APC prop), pure standard library:
  prop    T = kT Ct(J) rho n^2 D^4 ,  P = kP Cp(J) rho n^3 D^5         APC PER3 blade-element data (tables below)
  motor   V_m = w / Kv + I_m R_m ,  I_m = Q / Kt + I0 ,  Kt = 1 / Kv   (SI units, Kv in rad/s/V)
  ESC     V_m = d V_bus - I_m R_esc ,  P_bat = V_m I_m + I_m^2 R_esc + P_esc0
  pack    V_bus = V_ocv - R_pack * (sum of station battery currents + avionics)
kT and kP are fitted to the maker's own X3108S KV900 + APC 11x4.7 table (rows 5-12 A) against the PER3 file of that
same prop (CALC-E1-CAL). The fitted factors are then applied to the 11x4.5MR / 11x5.5MR PER3 files
(ASM-E1-CAL-TRANSFER). The H1 thrust stand replaces all of this (T-E1-STAND).

Two readings of the maker's rows above 12 A were carried since CDR-05 (2026-11-13). Rev 10 (closure round 2026-11-14)
rejects the second: the maker's own 11.1 V full-throttle rows rule it out (CALC-E1-BOUND2-CHECK), so its claims are
information only and R-HOVER-TW is verified on the first bound, the station the maker's stated R_m describes:
  first bound  (this model)   the maker's supply sagged, so the rows above 12 A were not at 14.8 V (CL-E1-MAKER-SUPPLY)
  second bound (CALC-E1-BOUND2) the rows are true 14.8 V full-throttle points: the station then behaves as if it had
               the series resistance that reproduces the top row (CL-E1-R-EFF-MAKER), and thrust at a low bus is lower
Motor current is judged in the WINDING (I_m = I_bat / duty at the limiter), not at the battery (CDR-AE-02, decision B7).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json", "../../subsystems/fins/params.json",
                              "../../subsystems/propulsion/params.json"])
P = "P:"
ST = ["UR", "UL", "LR", "LL"]                               # = params.json#propulsion.stations.ids
MOTORS = [f"PRP-001-{s}" for s in ST]                      # instance ids (interfaces SCHEMA, CR-A1-32)
ESCS = [f"PRP-002-{s}" for s in ST]
PROPS_ID = [f"PRP-003-{s}" for s in ST]
ADAPTERS = [f"PRP-004-{s}" for s in ST]
STATION = MOTORS + ESCS + PROPS_ID + ADAPTERS
# F4 motor map (subsystems/flight-software/SPEC.md, K09L.param): rotation seen from the nose = from the prop side.
# Prop drag makes the prop lag the shaft, so a CW motor needs a LH-thread post for the nut to self-tighten.
ROT = {"UR": "CW", "LL": "CW", "UL": "CCW", "LR": "CCW"}
PROP_SKU = {"CW": "11x8EP (LP11080EP)", "CCW": "11x8E (LP11080E)"}
THREAD = {"CW": "LH", "CCW": "RH"}

# ================================================================== catalogue data (verbatim, cited)
# SunnySky X3108S KV900 + APC "1147" (11x4.7), 14.8 V: [battery A, thrust gf, rpm, input W]; 94 degC after the 30 A row.
# Read from the maker's data image 2026-11-09 (SRC-E1-X3108S-DATA).
MAKER_1147 = [
    [1, 230, 2914, 15], [2, 340, 3575, 30], [3, 440, 4071, 44], [4, 530, 4451, 59], [5, 610, 4705, 74],
    [6, 690, 4970, 89], [7, 750, 5228, 104], [8, 810, 5400, 118], [9, 870, 5588, 133], [10, 920, 5777, 148],
    [12, 1010, 6034, 178], [14, 1110, 6317, 207], [16, 1190, 6530, 237], [18, 1260, 6720, 266],
    [20, 1330, 6940, 296], [23, 1410, 7140, 340], [26, 1490, 7300, 385], [30, 1580, 7500, 447]]
MAKER_TEMP_C = 94.0          # maker's temperature column at the 30 A row
# Closure round 2026-11-14 (rev 10): the maker's FULL-THROTTLE rows ("Full throttle temperature" column, last row of
# each prop block) from all three data images, read 2026-11-14 (SRC-E1-X3108S-DATA, SRC-E1-X3108S-DATA-111):
# [prop, volts as labelled, battery A, rpm, thrust gf, full-throttle temperature degC]. 14.8 / 11.1 V are the 4S / 3S
# LiPo nominal ratings (3.70 V/cell) and the W column is volts x amps, so the labels are not measured bus voltages.
MAKER_FT = [["10x3.8", 14.8, 27, 8780, 1530, 85], ["11x4.7", 14.8, 30, 7500, 1580, 94],
            ["10x3.8", 11.1, 18, 7457, 1090, 56], ["11x4.7", 11.1, 22, 6600, 1250, 62],
            ["12x3.8", 11.1, 25, 5760, 1250, 83]]
CAL_ROWS_A = (5, 12)         # rows used for the fit. The W column is 14.8 V x A with A in whole-amp steps, so rows
                             # < 5 A carry > 10 % rounding error. Rows > 12 A are NOT discarded (CDR-05): the fit
                             # reads them as taken at a sagging supply (CL-E1-MAKER-SUPPLY, first bound) and
                             # CALC-E1-CAL / CALC-E1-BOUND2 carry them as true 14.8 V points (second bound)

# APC PER3 files (apcprop.com/files/PER3_<size>.dat, v2022-0915), read 2026-11-09 (SRC-E1-APC-PER3).
# static: {rpm: (Ct0, Cp0)};  J-curve: 6000 rpm block [J, Ct, Cp] (scaled to other rpm by the static ratio).
PROPS = {
    "11x4.7SF": {"static": {1000: (.1250, .0492), 2000: (.1252, .0482), 3000: (.1254, .0477), 4000: (.1256, .0475),
                            5000: (.1259, .0474), 6000: (.1263, .0473), 7000: (.1267, .0474), 8000: (.1272, .0475),
                            9000: (.1278, .0477), 10000: (.1285, .0480), 11000: (.1292, .0483), 12000: (.1300, .0487)},
                 "J": None, "mass_g": None},
    "11x4.5MR": {"static": {4000: (.0966, .0345), 5000: (.0968, .0339), 6000: (.0971, .0335), 7000: (.0974, .0333),
                            8000: (.0978, .0331), 9000: (.0982, .0331), 10000: (.0987, .0330), 11000: (.0992, .0331),
                            12000: (.0999, .0332)},
                 "J": [[0.0, .0971, .0335], [.0188, .0952, .0336], [.0376, .0931, .0336], [.0564, .0909, .0336],
                       [.0752, .0887, .0335], [.0940, .0863, .0334], [.1128, .0838, .0332], [.1316, .0813, .0330],
                       [.1504, .0786, .0327], [.1692, .0758, .0324], [.1880, .0728, .0320], [.2069, .0698, .0315],
                       [.2257, .0666, .0310], [.2445, .0634, .0304], [.2633, .0600, .0297], [.2821, .0564, .0290],
                       [.3009, .0528, .0281], [.3197, .0491, .0273], [.3385, .0453, .0263], [.3573, .0415, .0253],
                       [.3761, .0375, .0242], [.3949, .0335, .0230], [.4137, .0294, .0217], [.4325, .0253, .0204],
                       [.4513, .0211, .0191], [.4701, .0169, .0176], [.4889, .0127, .0161], [.5077, .0084, .0145],
                       [.5265, .0042, .0129], [.5453, .0000, .0112]],
                 "mass_g": 17.0},
    "11x5.5MR": {"static": {4000: (.1116, .0428), 6000: (.1121, .0418), 8000: (.1129, .0413), 10000: (.1138, .0413)},
                 "J": [[0.0, .1121, .0418], [.0223, .1103, .0420], [.0446, .1083, .0423], [.0668, .1061, .0425],
                       [.0891, .1038, .0426], [.1114, .1013, .0426], [.1337, .0987, .0426], [.1560, .0959, .0424],
                       [.1782, .0930, .0422], [.2005, .0898, .0419], [.2228, .0865, .0414], [.2451, .0830, .0409],
                       [.2674, .0794, .0402], [.2896, .0756, .0394], [.3119, .0716, .0385], [.3342, .0674, .0374],
                       [.3565, .0630, .0363], [.3788, .0585, .0349], [.4010, .0539, .0335], [.4233, .0491, .0320],
                       [.4456, .0443, .0303], [.4679, .0393, .0285], [.4902, .0343, .0267], [.5124, .0292, .0247],
                       [.5347, .0241, .0226], [.5570, .0189, .0204], [.5793, .0137, .0181], [.6016, .0085, .0157],
                       [.6238, .0034, .0133]],
                 "mass_g": 17.0},
    "12x4.5MR": {"static": {4000: (.0900, .0308), 6000: (.0906, .0300), 8000: (.0914, .0297), 10000: (.0924, .0297)},
                 "J": [[0.0, .0906, .0300], [.0176, .0887, .0300], [.0353, .0867, .0300], [.0529, .0846, .0299],
                       [.0705, .0824, .0298], [.0881, .0802, .0297], [.1058, .0778, .0295], [.1234, .0753, .0293],
                       [.1410, .0728, .0290], [.1587, .0701, .0287], [.1763, .0673, .0283], [.1939, .0645, .0279],
                       [.2116, .0615, .0274], [.2292, .0584, .0269], [.2468, .0552, .0263], [.2644, .0520, .0256],
                       [.2821, .0486, .0249], [.2997, .0452, .0241], [.3173, .0417, .0233], [.3350, .0381, .0224],
                       [.3526, .0345, .0215], [.3702, .0308, .0205], [.3879, .0270, .0194], [.4055, .0232, .0182],
                       [.4231, .0194, .0171], [.4407, .0155, .0158], [.4584, .0116, .0145], [.4760, .0077, .0131],
                       [.4936, .0038, .0117], [.5113, -.0001, .0103]],
                 "mass_g": None},
}
PROP_D = {"11x4.7SF": 0.2794, "11x4.5MR": 0.2794, "11x5.5MR": 0.2794, "12x4.5MR": 0.3048, "11x5.5E": 0.2794}


def _load_b4_per3(name, mass_g):
    """B4's transcription of an APC PER3 file (team/B4/data/<name>): static rows (J = 0) and the 6000 rpm J block."""
    rows = []
    with open(HERE.parent / "B4" / "data" / name, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("rpm"):
                continue
            rows.append([float(v) for v in line.strip().split(",")])
    return {"static": {int(r[0]): (r[2], r[3]) for r in rows if r[1] == 0.0},
            "J": [[r[1], r[2], r[3]] for r in rows if int(r[0]) == 6000], "mass_g": mass_g}


# D-161 (closure round 2026-11-14): the flight prop is the APC 11x5.5E / 11x5.5EP (PER3_11x55E.dat via B4's file,
# 0.81 oz = 22.96 g, SRC-E1-APC-E-PAGES). The MR stays in PROPS as the comparison case.
PROPS["11x5.5E"] = _load_b4_per3("apc_per3_11x55E.csv", 22.96)


def _load_e1_per3(name, mass_g):
    """E1's own transcription (team/E1/data/<name>): columns rpm, J, Ct, Cp."""
    rows = []
    with open(HERE / "data" / name, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("rpm"):
                continue
            rows.append([float(v) for v in line.strip().split(",")[:4]])
    return {"static": {int(r[0]): (r[2], r[3]) for r in rows if r[1] == 0.0},
            "J": [[r[1], r[2], r[3]] for r in rows if int(r[0]) == 6000], "mass_g": mass_g}


# D-173 (closure round 2026-11-14): flight prop APC 11x8E / 11x8EP on the SunnySky X2814 V3 KV900
# (PER3_11x8E.dat, team/E1/data/apc_per3_11x8E.csv). The 11x5.5E (D-161) stays as a comparison.
PROPS["11x8E"] = _load_e1_per3("apc_per3_11x8E.csv", 22.96)
PROP_D["11x8E"] = 0.2794
DESIGN = "11x8E"
# the 11x8 maker row of the flight motor (SRC-E1-X2814-V3): APC 11x8, 14.8 V, 45.5 A, 2 320 gf, 10 221 rpm
X2814_11X8_ROW = {"rpm": 10221.0, "gf": 2320.0, "A": 45.5, "W": 673.4}
CANDIDATES = ["11x4.5MR", "11x5.5MR", "12x4.5MR"]


# ================================================================== sources and assumptions
kit.source("SRC-E1-X3108S-DATA", "SunnySky X3108S KV900 data image (11x4.7 and 10x3.8 at 14.8 V)", "datasheet",
           url="https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg",
           checked="2026-11-09", where="table APC1147 14.8 V, 18 rows, temperature 94 degC at 30 A",
           note="full table transcribed into MAKER_1147 in propulsion.py; product page "
                "https://sunnyskyusa.com/products/sunnysky-x3108s-motors returned HTTP 429 on 2026-11-09, "
                "price $24.99 from docs/research/budget-lift.md (seen 2026-11-01)")
kit.source("SRC-E1-X3108S-DATA-111", "SunnySky X3108S KV900 maker data images 1 and 2 (spec header, 11.1 V tables)",
           "datasheet", url="https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_1.jpg",
           checked="2026-11-14",
           where="Data_1: maker spec header (stator 31 x 8 mm, 12N14P, Kv 900, no-load current 0.9 A at 10 V, motor "
                 "resistance 86 mOhm, max continuous current 25 A / 30 s, max continuous power 370 W, 81 g, 3-4S, "
                 "recommended props APC 10x3.8, 11x4.7, 12x3.8) and table APC1038 at 11.1 V (top row 18 A, 1 090 gf, "
                 "7 457 rpm, 56 degC); Data_2 (same path, _Data_2.jpg): APC1147 at 11.1 V (top row 22 A, 1 250 gf, "
                 "6 600 rpm, 62 degC) and APC1238 at 11.1 V (top row 25 A, 1 250 gf, 5 760 rpm, 83 degC). The "
                 "temperature column is headed 'Full throttle temperature' and is filled on the last row of each block",
           note="the maker's own statement of R_m and I0 (until rev 10 only retailer listings were cited); the 11.1 V "
                "full-throttle rows are the published data that rule out the second bound (CALC-E1-BOUND2-CHECK)")
kit.source("SRC-E1-X3108S-SPEC", "SunnySky X3108S KV900 retailer spec (Robu)", "listing",
           url="https://robu.in/?p=1569817", where="Kv 900, R 86 mOhm, I0 0.9 A at 10 V, 25 A / 30 s, 370 W, 81 g, 3-4S",
           note="single retailer source (search snippet 2026-11-09; page 403 to direct fetch): Rm and I0 are "
                "UNVERIFIED until measured on arrival (T-E1-MOTOR-RM)", status="UNVERIFIED")
kit.source("SRC-E1-X3108S-HIMODEL", "SunnySky X3108S KV900 retailer spec (HiModel, SKU X3108SK9)", "listing",
           url="https://www.himodel.com/electric/SUNNYSKY_X3108S_KV900_Outrunner_Brushless_Motor_for_Multirotor.html",
           checked="2026-11-09",
           where="R 86 mOhm, I0 0.9 A at 10 V, 25 A / 30 s, 370 W, 81 g, OD 37.8 mm, shaft 4 mm, body length 26.5 mm, "
                 "overall shaft 33 mm; box: 1 prop adaptor + 1 prop holding-down disk; no bolt pattern, lead length "
                 "or wire gauge published",
           note="second independent listing for R and I0 (agrees with Robu); geekbuying swaps body and shaft length")
kit.source("SRC-E1-SPCNC-ADAPTER", "Small Parts CNC aluminium prop adapter set for 4114-class motors", "listing",
           url="https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct", checked="2026-11-09",
           where="lists SunnySky X3108S KV720/KV900 as compatible: 4 mm shaft, 4 x M3 on a 12 mm hole spacing in the "
                 "bell; M6x1 post 15.2 mm, base 6.35 mm, pilot bore 4 mm x 8.5 mm, 3.0 g; 2 RH + 2 LH thread, 16 x M3x4 "
                 "SHCS, M6 nuts and washers; $23.95 per set, out of stock 2026-11-09",
           note="design basis for the prop stack; the adapter in the motor box is used if it measures the same")
kit.source("SRC-E1-APC-PER3", "APC PER3 performance files 11x4.5MR, 11x5.5MR, 12x4.5MR, 11x4.7SF", "datasheet",
           url="https://www.apcprop.com/files/PER3_11x45MR.dat", checked="2026-11-09",
           where="static rows per rpm and the 6000 rpm J-sweep; also PER3_11x55MR.dat, PER3_12x45MR.dat, PER3_11x47SF.dat",
           note="blade-element prediction by the maker, not a measurement: calibrated against SRC-E1-X3108S-DATA")
kit.source("SRC-E1-APC-PAGES", "APC 11x4.5MR/MRP and 11x5.5MR/MRP product pages", "listing",
           url="https://www.apcprop.com/product/11x5-5mr/", checked="2026-11-09",
           where="LP11045MR / LP11045MRP / LP11055MR / LP11055MRP: $3.83 each, 0.60 oz (17 g), 1/4 in bore, "
                 "LPAR06E rings not included; 11x5.5MR hub diameter 0.65 in, hub thickness 0.35 in (re-read 2026-11-09)")
kit.source("SRC-E1-APC-E-PAGES", "APC 11x5.5E / 11x5.5EP product pages and APC rpm limits", "listing",
           url="https://www.apcprop.com/product/11x5-5e/", checked="2026-11-14",
           where="LP11055E and LP11055EP (https://www.apcprop.com/product/11x5-5ep/): $4.17 each, 0.81 oz (22.96 g), "
                 "hub 0.80 in dia x 0.41 in (10.41 mm), 1/4 in bore; stock not stated. RPM limits "
                 "(https://www.apcprop.com/technical-information/rpm-limits/): Thin Electric (E) 150 000 / D(in), "
                 "MR 105 000 / D(in)",
           note="D-161: the flight prop. PER3 file https://www.apcprop.com/files/PER3_11x55E.dat (B4 transcription "
                "team/B4/data/apc_per3_11x55E.csv, read 2026-11-09)")
kit.source("SRC-E1-NUT-ISO4035", "M6x1 thin hex nut ISO 4035 / DIN 439B, A4 stainless, 3.2 mm (Zoro Select 50-pack)", "listing",
           url="https://www.zoro.com/zoro-select-m6-100-plain-finish-a4-stainless-steel-thin-jam-hex-nuts-50-pk-jn9xx00600-050p1/i/G1015734",
           checked="2026-11-14", where="height 3.20 mm, 10 mm across flats, $9.59 per 50 (search snippet; page not opened)",
           note="D-161: replaces the 5.2 mm ISO 4032 nut so the thicker E hub keeps full nut engagement")
kit.source("SRC-E1-X2814-V3", "SunnySky X2814 V3 KV900: maker spec, test table and drawing", "datasheet",
           url="https://sunnyskyusa.com/products/sunnysky-x2814", checked="2026-11-14",
           where="KV900: stator 28 x 14 mm, rotor 35 mm, body 36 mm, 12N14P, 3-4S, I0 1.2 A at 10 V, R 33.6 mOhm, "
                 "50 A / 30 s, 680 W, 108 g; test table APC 11x8 at 14.8 V: 45.5 A, 2 320 gf, 673.4 W, 10 221 rpm, "
                 "94 degC after 3 min; $39.99, available. Drawing "
                 "https://cdn.shopify.com/s/files/1/2024/0305/files/X2814.jpg: shaft 4 mm, bell 3 x M2.5x0.45 depth "
                 "3.5 on 15 mm; base 4 x M3x0.5 depth 3.0 on 19 and 25 mm; leads 110 mm; prop adapter M6x1 (CW / "
                 "CCW thread), Ø6 pilot, 3 x Ø2.7 on 15 mm, overall 30 mm, thread 16 mm, 23.5 mm to the base face; "
                 "washer Ø17.8 x 2.5; spinner nut M6 (14.5 mm thread depth); cross mount 44 mm",
           note="D-173 flight motor. Whether the 108 g includes the 110 mm leads, and whether the adapter set is in "
                "the box, are - (weigh and check on arrival)")
kit.source("SRC-E1-APC-8E-PAGES", "APC 11x8E / 11x8EP product pages and PER3 file", "listing",
           url="https://www.apcprop.com/product/11x8e/", checked="2026-11-14",
           where="LP11080E and LP11080EP (https://www.apcprop.com/product/11x8ep/): $4.17, 0.81 oz, hub 0.80 x 0.41 "
                 "in, 1/4 in bore; PER3 https://www.apcprop.com/files/PER3_11x8E.dat (v2022-0915)")
kit.source("SRC-E1-TEKKO32", "Holybro Tekko32 F4 45A single ESC (AM32), ReadyMadeRC", "listing",
           url="https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32",
           checked="2026-11-09", where="$22.50, 45 A cont, 2-6S, AM32, current sensor, 5.8 g, 16 AWG; backorder to Dec 2026")

kit.assumption("ASM-E1-KV", "Motor Kv 900 rpm/V", "X3108S KV900 speed constant", basis="maker name and listing; the "
               "maker table's rpm at low throttle is consistent with it (CALC-E1-CAL residuals)", value=900.0,
               unit="rpm/V", cites=["SRC-E1-X3108S-SPEC", "SRC-E1-X3108S-DATA"])
kit.assumption("ASM-E1-CAL-RM", "Calibration motor (X3108S KV900) winding resistance 86 mOhm",
               "used only to fit kT, kP and the bound checks on the X3108S maker rows (CALC-E1-CAL, -BOUND2-CHECK)",
               basis="maker spec header SRC-E1-X3108S-DATA-111", value=0.086, unit="ohm", status="UNVERIFIED",
               cites=["SRC-E1-X3108S-DATA-111"])
kit.assumption("ASM-E1-CAL-I0", "Calibration motor (X3108S KV900) no-load current 0.9 A", "as ASM-E1-CAL-RM",
               basis="maker spec header SRC-E1-X3108S-DATA-111", value=0.9, unit="A", status="UNVERIFIED",
               cites=["SRC-E1-X3108S-DATA-111"])
kit.assumption("ASM-E1-RM-X3108", "(superseded) X3108S winding resistance 86 mOhm at 25 degC", "phase-to-phase resistance of the X3108S KV900",
               basis="the maker's spec header states 86 mOhm (SRC-E1-X3108S-DATA-111, rev 10) and two retailer "
                     "listings agree (Robu, HiModel); measure with a 4-wire milliohm method on arrival",
               value=0.086, unit="ohm", status="UNVERIFIED",
               cites=["SRC-E1-X3108S-DATA-111", "SRC-E1-X3108S-SPEC", "SRC-E1-X3108S-HIMODEL"])
kit.assumption("ASM-E1-RM", "Winding resistance 33.6 mOhm at 25 degC (X2814 V3 KV900, D-173)",
               "phase-to-phase resistance of the flight motor", basis="maker spec SRC-E1-X2814-V3; measure 4-wire on "
               "arrival (T-E1-MOTOR-RM), band ASM-E1-RM-BAND", value=0.0336, unit="ohm", status="UNVERIFIED",
               cites=["SRC-E1-X2814-V3"])
kit.assumption("ASM-E1-I0", "No-load current 1.2 A (X2814 V3 KV900 at 10 V, D-173)", "no-load current, used as speed-independent iron + friction loss",
               basis="maker spec at 10 V (~9 000 rpm) SRC-E1-X2814-V3; conservative below that speed (X3108S: 0.9 A)", value=1.2,
               unit="A", status="UNVERIFIED",
               cites=["SRC-E1-X2814-V3"])
kit.assumption("ASM-E1-ESC", "ESC loss 10 mOhm + 0.5 W", "ESC conduction path 10 mOhm (two FETs + leads) and 0.5 W fixed",
               basis="typical BLHeli_S 45 A FETs 3-4 mOhm each; the fit factor kP absorbs any error at the "
                     "calibration points", value=[0.010, 0.5], unit="ohm,W")
kit.assumption("ASM-E1-PACK", "Pack + harness 24 mOhm, avionics 1 A", "4S 6500 130C pack 20 mOhm (5 mOhm/cell, part-"
               "aged) plus 4 mOhm main lead and connector; avionics + servos 1 A from the bus",
               basis="E2 measures pack IR with the charger; F1 owns the harness resistance", value=[0.024, 1.0],
               unit="ohm,A", status="UNVERIFIED")
# Rev 3: E1's own calcs use the cell part below + F1's harness value P:electrical.r_ext_mohm (CR-F1-03). ASM-E1-PACK
# stays (unchanged) because B4's props.py reads it; CR-E1-26 asks B4 to move to the same two inputs.
kit.assumption("ASM-E1-PACK-CELLS", "Pack cells 20 mOhm, avionics 1 A", "4S 6500 130C pack, cells only: 4 x 5 mOhm "
               "(part-aged, 25 degC); avionics + servos 1 A from the bus. Harness from params electrical.r_ext_mohm",
               basis="E2's new-pack value is 4.0 mOhm/cell (ASM-E2-R-CELL); 5 mOhm/cell covers a season of cycling. "
                     "E2 measures pack IR by load step (T-E2-IR)", value=[0.020, 1.0], unit="ohm,A", status="UNVERIFIED")
kit.assumption("ASM-E1-OCV", "Pack OCV states", "open-circuit pack voltage: full 4.20, mid 3.80, low 3.60 V/cell (4S)",
               basis="3.60 V/cell OCV is the 20 % reserve point of a LiPo; the sag case uses it", value=[16.8, 15.2, 14.4],
               unit="V")
kit.assumption("ASM-E1-TCOPPER", "Copper 0.393 %/K, hot winding 80 degC", "R_m(T) = R_25 (1 + 0.00393 (T - 25)); "
               "thrust-limit cases use an 80 degC winding, current-limit cases 25 degC",
               basis="annealed copper coefficient; 80 degC = hot after a hover", value=[0.00393, 80.0], unit="1/K,degC")
kit.assumption("ASM-E1-CAL-TRANSFER", "PER3-to-measured factors transfer between APC 11 in props",
               "kT, kP fitted on the 11x4.7SF apply to the 11x4.5MR / 11x5.5MR / 11x5.5E PER3 data (the E, D-161, is the "
               "same thin-electric family as the SF the factors were fitted on)",
               basis="same maker, same code, same diameter; H1's thrust stand (T-E1-STAND) measures the fitted prop "
                     "directly and supersedes this", status="UNVERIFIED")
kit.assumption("ASM-E1-RTH", "Motor thermal resistance 1.0 K/W in own wash", "steady winding-to-ambient resistance of the "
               "X3108S in its own static prop wash", basis="maker's 94 degC at the 30 A row, 25 degC room, losses from this "
               "model (CALC-E1-CAL); the test was not steady, so the true value may be higher: E3 owns the thermal model",
               value=1.0, unit="K/W", status="UNVERIFIED", cites=["SRC-E1-X3108S-DATA"])
kit.assumption("ASM-E1-ILIM", "Pack-current limit = performance.full_throttle_current_a (70 A, D-148)",
               "ArduPilot Q_M_BAT_CURR_MAX = params performance.full_throttle_current_a caps the summed motor current "
               "(Q_M_BAT_CURR_TC 1 s). The calcs read the params key; the limiter acts on the power module's reading, "
               "so the model takes the sensor as exact and the sensor error is carried by ASM-E1-SENSOR-TOL",
               basis="D-148 (review/DESIGN-ROUND-2026-11-14/A1.md): 100 -> 70 A so the winding stays <= 25 A on the "
                     "first motor bound with the 11x5.5MR; the 93 A second-bound value is withdrawn in rev 10 "
                     "(ASM-E1-ILIM-B2). Rev 9 (wave 2): was a fixed 100 A in this assumption", unit="A")
kit.assumption("ASM-E1-VCELL-FULL", "Fresh pack 4.35 V/cell (LiHV, Gens Ace Shorty, full 17.4 V)",
               "open-circuit voltage of a fully charged 4S LiHV pack, used for the fresh one-motor transient and the fresh T/W "
               "cases of CALC-E1-SPIN-CAP (was 4.20 V/cell = 16.8 V)",
               basis="params.json#battery D-174: Gens Ace Redline 4S 6000 mAh HV Shorty, charge 4.35 V/cell (maker listing; "
                     "confirm on arrival); 17.4 V is the figure A1 gave", value=4.35, unit="V/cell", status="PROPOSED")
kit.assumption("ASM-E1-SPIN-MAX", "Q_M_SPIN_MAX 0.81 (static, D-173b, CoreWing, no Lua)",
               "fixed output ceiling of every motor; the duty of the ESC is taken equal to the output (Bluejay, linear)",
               basis="E1 D-173: holds the one-motor transient on a fresh pack inside 50 A winding and the ESC's 45 A; "
                     "F4 K09L.param", value=0.81, unit="-", status="PROPOSED")
kit.assumption("ASM-E1-SENSOR-TOL", "Pack-current sensor error +/-1.1 % after T-F1-SENSOR-CAL (D-157)",
               "the true pack current at the limiter lies within Q_M_BAT_CURR_MAX x (1 +/- tol); T-F1-SENSOR-CAL "
               "(before flight) shows the reading within this band at 70-75 A",
               basis="D-148 condition (A1.md): the 70 A value sits in the first-bound pass window only with this "
                     "calibration; uncalibrated the planning error is +/-5 % (ASM-F1-SENSOR-TOL). D-157 (E1 wave 2): "
                     "at 9 deg the first-bound window is 69.37-71.07 A, so the limiter is 70.2 A with +/-1.1 % "
                     "(D-148's +/-1.5 % at 70 A failed the T/W 2.0 edge)",
               value=0.011, unit="-", status="UNVERIFIED")
kit.assumption("ASM-E1-ILIM-B2", "Second-bound limiter value 93 A (D-148; withdrawn in rev 10, information only)",
               "Q_M_BAT_CURR_MAX = 93 A if T-E1-STAND reads the second motor bound (about 7 500 rpm on the 11x4.7 at a "
               "held 14.8 V, CL-E1-R-EFF-MAKER)",
               basis="E1 wave 1 (review/DESIGN-ROUND-2026-11-14/E1.md 1.4): second-bound pass window 91.5-94.8 A at "
                     "7 deg; A1 D-148 carries 93 A as the alternative. Information case only (CALC-E1-ILIM-COND)",
               value=93.0, unit="A")
kit.assumption("ASM-E1-V-FALLBACK", "Fallback cruise speed 17 m/s (D-96 c, CDR decision B6)",
               "AIRSPEED_MIN = AIRSPEED_CRUISE = 17 m/s: the planning case while the tripped stall (12.85 m/s) is "
               "the baseline, until T-B2-STALL",
               basis="params/CHANGE-LOG.md D-96 (c): 17 holds to a 13.07 m/s stall; review/CDR-2026-11-13/"
                     "CDR-SUMMARY.md decision B6 makes it the planning baseline. Since D-145 (2026-11-14) "
                     "performance.cruise_ms is 17 too, so CALC-E1-CRUISE and CALC-E1-CRUISE-V17 give the same point "
                     "(ratio_to_cruise 1.0); the id is kept because E2 and B1 read CL-E1-CRUISE-P-55-V17",
               value=17.0, unit="m/s")
kit.assumption("ASM-E1-BOUND2", "Second bound (rejected reading since rev 10, information only): the maker's top row "
               "is a true 14.8 V full-throttle point",
               "the maker's 30 A row (7 500 rpm, 1 580 gf, 11x4.7, 94 degC) was taken at 14.8 V at the ESC and "
               "100 % duty. The station then has an effective series resistance R_eff = (14.8 - w / Kv) / I_m at "
               "that row (winding at its 94 degC, ESC and everything the simple model leaves out), used unchanged "
               "at other bus voltages and with the 11x5.5MR",
               basis="CDR-AE-01 (review/CDR-2026-11-13/CDR-aero.md): the 'sagging supply' reading of the rows above "
                     "12 A has no evidence, so the rows are a second bound, not discarded data. A fixed series "
                     "resistance is the simplest model that reproduces the row; the reviewer's cruder rule "
                     "(full-throttle rpm proportional to bus voltage) is carried beside it as a sensitivity. "
                     "T-E1-STAND with a logged bus voltage decides between the bounds. REJECTED in the closure round "
                     "(2026-11-14, rev 10) by the maker's own published rows (CALC-E1-BOUND2-CHECK): (1) applied at the "
                     "maker's 11.1 V full-throttle row with the same 11x4.7 it predicts CL-E1-B2-MISS-111 less thrust "
                     "than the maker measured; (2) the five full-throttle rows, read as held-voltage points, need five "
                     "different station resistances (CL-E1-R-UB-SPREAD), which no fixed station has; (3) it puts "
                     "CL-E1-RM-NEEDED-B2 times the maker-stated winding resistance in the motor, and even the least "
                     "pessimistic held-voltage reading needs CL-E1-RM-NEEDED-MIN times. The volts column is the 4S / 3S "
                     "nominal rating, so the rows do not fix the voltage at the ESC; the resistance outside the motor "
                     "belongs to the maker's rig (supply, leads, ESC), which K09-L does not carry: its own pack, harness "
                     "and ESC are modelled separately (ASM-E1-PACK-CELLS, electrical.r_ext_mohm, ASM-E1-ESC)",
               status="UNVERIFIED", cites=["SRC-E1-X3108S-DATA", "SRC-E1-X3108S-DATA-111"])
kit.assumption("ASM-E1-V-STAND-LOW", "Low stand point: bus held at 11.9 V",
               "bench supply held at 11.9 V at the ESC pads for the worst-state full-throttle run of T-E1-STAND",
               basis="CDR condition B-7 / CDR-AE C1 (review/CDR-2026-11-13/CDR-SUMMARY.md): >= 1 060 gf at an 11.9 V "
                     "bus; 11.9 V is CALC-E1-WORST's worst-state bus on the first bound (11.85 V at r_ext 6.7 mOhm)",
               value=11.9, unit="V")
kit.assumption("ASM-E1-TRANS-MARGIN", "Transition thrust margin 1.3", "full thrust at every point of the level "
               "pitch-over corridor >= 1.3 x the thrust that holds level unaccelerated flight there",
               basis="0.3 g of surplus for acceleration and gusts; same headroom as ASM-A2-GUST-THRUST-HEADROOM",
               value=1.3, unit="-")
kit.assumption("ASM-E1-POSTSTALL", "Wing CL: linear to CLmax, flat plate after stall", "CL = a alpha up to CLmax "
               "(a = 2 pi AR/(AR+2)); above stall CN = 1.98 sin(alpha) (flat plate); prop wash on the wing ignored",
               basis="Hoerner flat-plate normal force; ignoring wash lift is conservative for thrust required; B1/B2 refine")
kit.assumption("ASM-E1-WORST-STATE", "Worst pack state for hover T/W", "the lowest pack state the aircraft is flown in: "
               "the 20 % reserve line (E2 ASM-E2-OCV-20), pack cold-soaked to 10 degC (E2 ASM-E2-COLD-R), windings hot "
               "(80 degC, after a hover), the limiter set (ASM-E1-ILIM); pack resistance = cells x R_cell x cold + R_ext (E2's model)",
               basis="one definition shared with E2 (CR-E2/E1 reconciliation 2026-11-09); the battery failsafe lands "
                     "the aircraft at the reserve line, so states below it are emergencies, reported as a sensitivity "
                     "(3.60 V/cell OCV)", value=[80.0, 3.60], unit="degC,V")
kit.assumption("ASM-E1-STACK", "Prop stack dimensions (D-173: X2814 V3 with its own adapter)", "D-173 values: body 36.0 mm "
               "(X2814 drawing), the maker's bolt-on adapter base 6.5 mm (30 - 23.5 on the drawing, EST), post 23.5 mm "
               "above the base (Ø6 pilot 7.5 + M6x1 thread 16), hub 10.41 mm (11x8E), washer 2.5 mm (Ø17.8, drawing), "
               "M6 spinner nut: needed engagement 6.0 mm = 1.0 d (its thread is 14.5 mm deep). Before D-173: motor body "
               "(mount face to bell top) 26.5 mm; bolt-on adapter "
               "base 6.35 mm, M6x1 post 15.2 mm above the base; prop hub 0.41 in = 10.41 mm (11x5.5E, D-161; was MR 8.89 mm); "
               "M6 washer 1.0 mm; M6 thin nut ISO 4035 3.2 mm (D-161; was ISO 4032 5.2 mm)",
               basis="HiModel listing (body), Small Parts CNC adapter drawing values, APC 11x5.5E page (hub), "
                     "ISO 4035 listing / ISO 7089 (nut, washer); measure the supplied adapter on arrival",
               value=[0.036, 0.0065, 0.0235, 0.01041, 0.0025, 0.006], unit="m", status="UNVERIFIED",
               cites=["SRC-E1-X3108S-HIMODEL", "SRC-E1-SPCNC-ADAPTER", "SRC-E1-APC-E-PAGES", "SRC-E1-NUT-ISO4035"])
kit.assumption("ASM-E1-MOUNT-SCREW", "Motor screw length and engagement window (D-173: X2814 base holes 3.0 mm deep)",
               "D-173: [length, e_min, e_max, washer] = M3x8, 2.5 mm (1.0 d rule, 5 threads), 2.5 mm (hole depth 3.0 on "
               "the X2814 drawing less 0.5 mm tip clearance), two ISO 7089 M3 washers 2 x 0.5 mm under each head. Before: M3x8 SHCS (A2 stainless, same size "
               "as the old design's F01), no washer; thread engagement in the motor base 2.5-3.5 mm (>= 5 threads, tip "
               "clear of the stator). The plate and pad heights under the head are D3's (P:fin_detail.mount.*)",
               basis="X3108S base thread depth is not published: 3.5 mm is a conservative limit for a 31 mm stator "
                     "base; probe the hole depth on arrival, the screw tip must stop >= 0.5 mm short of the bottom",
               value=[0.008, 0.0025, 0.0025, 0.0010], unit="m", status="UNVERIFIED")
kit.assumption("ASM-E1-PART-MASS", "Per-unit flying masses incl. leads, g", "motor with factory leads 81.0 (no bullets: "
               "harness HRN-E03); ESC stripped of its factory power leads (F2 solders its own 16 AWG to the pads, D-48, "
               "CR-F2-07) with signal lead and heat-shrink 7.6 (6.6 g bare board + 1.0 g; was 11.0 with 2 x 80 mm "
               "16 AWG); prop 22.96 (11x8E 0.81 oz, D-173); motor 108.0 (X2814 V3 as listed, D-173; X3108S was 81.0); bolt-on adapter 3.0 + 4 x M3x4 1.2 + M6 nut 1.9 + "
               "washer 0.6 = 6.7; 4 x M3x8 SHCS motor screws 3.2",
               basis="listings (81 g, 17 g, 3.0 g); ISO masses for screws, nuts, washers; the stripped ESC is EST "
                     "from the 6.6 g bare board (D-48, CR-A3-21: -3.4 g per ESC); weigh everything on arrival",
               value={"motor": 108.0, "esc": 7.6, "prop": 22.96, "adapter_nut": 6.7, "motor_screws": 3.2}, unit="g",
               status="UNVERIFIED", cites=["SRC-E1-X3108S-HIMODEL", "SRC-E1-APC-PAGES", "SRC-E1-SPCNC-ADAPTER"])


# ================================================================== the model (plain functions, reused by plots.py)
def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0] + (ys[1] - ys[0]) * (x - xs[0]) / (xs[1] - xs[0])
    for i in range(1, len(xs)):
        if x <= xs[i]:
            return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1] + (ys[-1] - ys[-2]) * (x - xs[-1]) / (xs[-1] - xs[-2])


def coeffs(prop, rpm, J=0.0):
    """Ct, Cp at rpm and advance ratio J (PER3; J-curve of the 6000 rpm block scaled by the static Re trend)."""
    st = PROPS[prop]["static"]
    rs = sorted(st)
    ct0 = interp(rpm, rs, [st[r][0] for r in rs])
    cp0 = interp(rpm, rs, [st[r][1] for r in rs])
    if J <= 0 or PROPS[prop]["J"] is None:
        return ct0, cp0
    tab = PROPS[prop]["J"]
    js = [r[0] for r in tab]
    ct = interp(J, js, [r[1] for r in tab]) * ct0 / tab[0][1]
    cp = interp(J, js, [r[2] for r in tab]) * cp0 / tab[0][2]
    return ct, cp


def prop_tp(prop, rpm, V, rho, kT, kP):
    """Thrust N and shaft power W of one prop at rpm and axial speed V."""
    D = PROP_D[prop]
    n = rpm / 60.0
    J = V / (n * D) if n > 0 else 0.0
    ct, cp = coeffs(prop, rpm, J)
    return kT * ct * rho * n * n * D ** 4, kP * cp * rho * n ** 3 * D ** 5, J


def motor_point(rpm, P_shaft, kv, rm, i0):
    """Motor current, terminal voltage, input power for a shaft power at rpm."""
    w = rpm * 2 * math.pi / 60.0
    kt = 1.0 / (kv * 2 * math.pi / 60.0)
    i_m = P_shaft / (kt * w) + i0 if w > 0 else i0
    v_m = w * kt + i_m * rm
    return i_m, v_m, v_m * i_m


def station(prop, rpm, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_bus):
    """Full station state at rpm: thrust, currents, powers, duty."""
    T, Ps, J = prop_tp(prop, rpm, V, rho, kT, kP)
    i_m, v_m, p_m = motor_point(rpm, Ps, kv, rm, i0)
    p_bat = p_m + i_m * i_m * r_esc + p_esc0
    duty = (v_m + i_m * r_esc) / v_bus
    return {"T_N": T, "P_shaft_W": Ps, "J": J, "I_m_A": i_m, "V_m_V": v_m, "P_motor_in_W": p_m,
            "P_bat_W": p_bat, "I_bat_A": p_bat / v_bus, "duty": duty, "rpm": rpm,
            "P_loss_motor_W": p_m - Ps, "P_loss_esc_W": i_m * i_m * r_esc + p_esc0}


def bisect(f, lo, hi, n=80):
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def at_thrust(prop, T_req, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_bus):
    rpm = bisect(lambda r: prop_tp(prop, r, V, rho, kT, kP)[0] - T_req, 500.0, 20000.0)
    return station(prop, rpm, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_bus)


def full_throttle(prop, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_ocv, r_pack, i_avn, n_mot, duty_max=1.0):
    """All n motors at full throttle on one pack: solve rpm with the bus sagging under the summed current."""
    v_bus = v_ocv
    for _ in range(60):
        rpm = bisect(lambda r: station(prop, r, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_bus)["duty"] - duty_max,
                     500.0, 25000.0)
        s = station(prop, rpm, V, rho, kT, kP, kv, rm, i0, r_esc, p_esc0, v_bus)
        v_new = v_ocv - r_pack * (n_mot * s["I_bat_A"] + i_avn)
        if abs(v_new - v_bus) < 1e-6:
            break
        v_bus = 0.5 * (v_bus + v_new)
    s["V_bus_V"] = v_bus
    return s


def r_hot(rm25, alpha, t):
    return rm25 * (1 + alpha * (t - 25.0))


def calibrate(rho, kv, rm, i0, esc):
    """Fit kT (thrust at measured rpm) and kP (battery power at measured rpm) to the maker rows <= CAL_MAX_A."""
    r_esc, p0 = esc
    rows = [r for r in MAKER_1147 if CAL_ROWS_A[0] <= r[0] <= CAL_ROWS_A[1]]
    kT = sum(r[1] * 9.80665e-3 / prop_tp("11x4.7SF", r[2], 0, rho, 1, 1)[0] for r in rows) / len(rows)

    def err(kP):
        return sum(station("11x4.7SF", r[2], 0, rho, kT, kP, kv, rm, i0, r_esc, p0, 14.8)["P_bat_W"] - r[3] for r in rows)
    kP = bisect(err, 0.5, 2.0)
    res = []
    for r in MAKER_1147:
        s = station("11x4.7SF", r[2], 0, rho, kT, kP, kv, rm, i0, r_esc, p0, 14.8)
        v_sup = s["V_m_V"] + s["I_m_A"] * r_esc            # supply needed at 100 % duty to reach the measured rpm
        w = r[2] * 2 * math.pi / 60.0
        res.append({"A": r[0], "T_err": s["T_N"] / (r[1] * 9.80665e-3) - 1, "P_err": s["P_bat_W"] / r[3] - 1,
                    "v_supply_min": v_sup, "loss_W": s["P_loss_motor_W"], "I_m_A": s["I_m_A"], "rpm": r[2],
                    # series resistance (winding + ESC + anything else) that puts this row at 14.8 V, 100 % duty
                    "r_eff_ohm": (14.8 - w / (kv * 2 * math.pi / 60.0)) / s["I_m_A"]})
    return kT, kP, res


# ================================================================== calculations (claims)
@kit.calc("CALC-E1-CAL", title="Fit PER3 to the maker's X3108S + 11x4.7 table",
          equation="kT = mean(T_meas / T_PER3(rpm)) ; kP: sum(P_bat,model(rpm) - P_meas) = 0 over rows 5-12 A ; "
                   "R_th = (94 - 25) / P_loss(30 A row) ; rows > 12 A (second bound): V_supply,min = V_m + I_m R_esc "
                   "at the measured rpm, R_eff = (14.8 - w / Kv) / I_m",
          inputs={"rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "rm": "ASM-E1-CAL-RM", "i0": "ASM-E1-CAL-I0", "esc": "ASM-E1-ESC"},
          units={"rho": "kg/m3", "kv": "rpm/V", "rm": "ohm", "i0": "A"},
          assumes=["ASM-E1-KV", "ASM-E1-CAL-RM", "ASM-E1-CAL-I0", "ASM-E1-ESC"], cites=["SRC-E1-X3108S-DATA", "SRC-E1-APC-PER3"])
def cal(rho, kv, rm, i0, esc):
    kT, kP, res = calibrate(rho, kv, rm, i0, esc)
    fit = [r for r in res if CAL_ROWS_A[0] <= r["A"] <= CAL_ROWS_A[1]]
    top = res[-1]
    hi = [r for r in res if r["A"] > CAL_ROWS_A[1]]            # the maker's rows above 12 A: recorded, not discarded
    return {"hi_rows": [[r["A"], r["rpm"], r["T_err"], r["P_err"], r["I_m_A"], r["v_supply_min"], r["r_eff_ohm"]]
                        for r in hi],
            "T_err_hi_max": max(abs(r["T_err"]) for r in hi), "P_err_hi_max": max(abs(r["P_err"]) for r in hi),
            "I_m_30A_A": top["I_m_A"], "r_eff_30A_ohm": top["r_eff_ohm"],
            "kT": kT, "kP": kP,
            "T_err_rms": math.sqrt(sum(r["T_err"] ** 2 for r in fit) / len(fit)),
            "P_err_rms": math.sqrt(sum(r["P_err"] ** 2 for r in fit) / len(fit)),
            "P_err_max": max(abs(r["P_err"]) for r in fit),
            "v_supply_30A": top["v_supply_min"], "loss_30A_W": top["loss_W"],
            "rth_KW": (MAKER_TEMP_C - 25.0) / top["loss_W"]}


@kit.calc("CALC-E1-CAL-11X8", title="PER3 11x8E factors fitted on the X2814 V3 maker row (APC 11x8, 14.8 V)",
          equation="kT = T_maker / T_PER3(rpm_maker) ; kP = Q w / P_PER3(rpm_maker), Q = (I_maker - I0) / Kt "
                   "(full throttle: winding = battery current; both independent of the maker's supply voltage)",
          inputs={"rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "i0": "ASM-E1-I0"},
          units={"rho": "kg/m3", "kv": "rpm/V", "i0": "A"},
          assumes=["ASM-E1-KV", "ASM-E1-I0"], cites=["SRC-E1-X2814-V3", "SRC-E1-APC-8E-PAGES"])
def cal_11x8(rho, kv, i0):
    r = X2814_11X8_ROW
    T1, P1, _ = prop_tp(DESIGN, r["rpm"], 0.0, rho, 1.0, 1.0)
    q = (r["A"] - i0) * 60.0 / (2 * math.pi * kv)
    return {"kT": r["gf"] * 9.80665e-3 / T1, "kP": q * r["rpm"] * 2 * math.pi / 60.0 / P1, "Q_Nm": q,
            "T_per3_gf": T1 / 9.80665e-3, "P_per3_W": P1}


@kit.calc("CALC-E1-HOVER", title="Hover operating point per motor, 11x4.5MR and 11x5.5E/EP",
          equation="T_m = m_gate g k_dl / (4 cos cant) ; solve rpm: T(rpm) = T_m ; I_bat, P_bat at V_bus = 14.8 V ; "
                   "g/W = T_m / g / P_bat ; dT_wind = R_th P_loss",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "kdl": P + "propulsion.download_factor",
                  "cant": P + "propulsion.stations.cant_deg",
                  "n": P + "propulsion.n_motors", "rho": P + "env.rho_kgm3", "kP": "CL-E1-KP", "kT": "CL-E1-KT",
                  "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "tc": "ASM-E1-TCOPPER",
                  "rth": "ASM-E1-RTH"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "cant": "deg"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E1-RTH"], cites=["SRC-E1-APC-PER3"])
def hover(m, g, kdl, cant, n, rho, kP, kT, kv, rm, i0, esc, tc, rth):
    T = m * g * kdl / (n * math.cos(math.radians(cant)))
    out = {"T_per_motor_N": T}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR")):
        rmh = r_hot(rm, tc[0], 50.0)
        s = at_thrust(prop, T, 0.0, rho, kT, kP, kv, rmh, i0, esc[0], esc[1], 14.8)
        out[f"rpm_{tag}"] = s["rpm"]
        out[f"I_bat_{tag}_A"] = s["I_bat_A"]
        out[f"I_m_{tag}_A"] = s["I_m_A"]
        out[f"P_total_{tag}_W"] = n * s["P_bat_W"]
        out[f"I_pack_{tag}_A"] = n * s["I_bat_A"]
        out[f"gW_{tag}"] = T / g * 1000 / s["P_bat_W"]
        out[f"loss_motor_{tag}_W"] = s["P_loss_motor_W"]
        out[f"loss_esc_{tag}_W"] = s["P_loss_esc_W"]
        out[f"dT_wind_{tag}_K"] = rth * s["P_loss_motor_W"]
        out[f"duty_{tag}"] = s["duty"]
    return out


@kit.calc("CALC-E1-FULL", title="Full-throttle static thrust and current, all four motors",
          equation="duty = Q_M_SPIN_MAX (D-173b: the fixed output ceiling; was 1) ; V_bus = V_ocv - R_pack (4 I_bat + I_avn) ; T/W = 4 T_max / (m_gate g) ; "
                   "cases: table basis (bus held 14.8 V, 25 degC), sag (OCV 14.4 V, R_pack, 80 degC), "
                   "current limits (bus held 14.8 / 16.8 V, 25 degC)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK-CELLS",
                  "rext": P + "electrical.r_ext_mohm", "ocv": "ASM-E1-OCV", "tc": "ASM-E1-TCOPPER",
                  "cap": "ASM-E1-SPIN-MAX"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "rext": "mOhm"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E1-PACK-CELLS", "ASM-E1-SPIN-MAX"], cites=["SRC-E1-APC-PER3"])
def full(m, g, n, rho, kP, kT, kv, rm, i0, esc, pack, rext, ocv, tc, cap):
    W = m * g
    pack = (pack[0] + rext / 1000.0, pack[1])
    out = {}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR"), ("12x4.5MR", "12")):
        a = (prop, 0.0, rho, kT, kP, kv)
        tb = full_throttle(*a, rm, i0, esc[0], esc[1], 14.8, 0.0, pack[1], n, duty_max=cap)
        sg = full_throttle(*a, r_hot(rm, tc[0], tc[1]), i0, esc[0], esc[1], ocv[2], pack[0], pack[1], n, duty_max=cap)
        hi = full_throttle(*a, rm, i0, esc[0], esc[1], 16.8, 0.0, pack[1], n, duty_max=cap)
        out[f"tw_table_{tag}"] = n * tb["T_N"] / W
        out[f"tw_sag_{tag}"] = n * sg["T_N"] / W
        out[f"Tmax_table_{tag}_gf"] = tb["T_N"] / g * 1000
        out[f"Tmax_sag_{tag}_gf"] = sg["T_N"] / g * 1000
        out[f"I_148_{tag}_A"] = tb["I_bat_A"]
        out[f"I_168_{tag}_A"] = hi["I_bat_A"]
        out[f"P_148_{tag}_W"] = tb["P_bat_W"]
        out[f"Ipack_sag_{tag}_A"] = n * sg["I_bat_A"] + pack[1]
        out[f"Ipack_fresh_{tag}_A"] = n * hi["I_bat_A"] + pack[1]   # bus held 16.8 V: upper bound, no pack sag
        out[f"Vbus_sag_{tag}_V"] = sg["V_bus_V"]
        out[f"rpm_148_{tag}"] = tb["rpm"]
        out[f"loss_148_{tag}_W"] = tb["P_loss_motor_W"]
    return out


def limited(prop, rho, kT, kP, kv, rm, i0, esc, v_ocv, r_pack, i_avn, n, i_lim):
    """Full throttle with ArduPilot's battery-current limiter: highest duty with pack current <= i_lim."""
    s = full_throttle(prop, 0.0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], v_ocv, r_pack, i_avn, n)
    if n * s["I_bat_A"] + i_avn <= i_lim:
        return s

    def f(d):
        t = full_throttle(prop, 0.0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], v_ocv, r_pack, i_avn, n, duty_max=d)
        return n * t["I_bat_A"] + i_avn - i_lim
    lo, hi = 0.3, 1.0                       # rev 9: f rises with duty; keep lo feasible (f <= 0), so the
    for _ in range(40):                     # returned pack current is never above i_lim by round-off (it was
        mid = 0.5 * (lo + hi)               # 70.00000000005 A at the 70 A limiter)
        if f(mid) <= 0:
            lo = mid
        else:
            hi = mid
    d = lo
    s = full_throttle(prop, 0.0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], v_ocv, r_pack, i_avn, n, duty_max=d)
    s["duty_max"] = d
    return s


@kit.calc("CALC-E1-LIMIT", title="Full throttle with the pack-current limiter Q_M_BAT_CURR_MAX",
          equation="largest duty with 4 I_bat + I_avn <= I_lim ; T/W = 4 T / (m_gate g) ; cases fresh (OCV 16.8 V, "
                   "25 degC) and low (OCV 14.4 V, 80 degC), with R_pack",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK-CELLS",
                  "rext": P + "electrical.r_ext_mohm", "ocv": "ASM-E1-OCV", "tc": "ASM-E1-TCOPPER", "ilim": P + "performance.full_throttle_current_a"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "ilim": "A", "rext": "mOhm"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E1-PACK-CELLS", "ASM-E1-ILIM"])
def limit_calc(m, g, n, rho, kP, kT, kv, rm, i0, esc, pack, rext, ocv, tc, ilim):
    W = m * g
    pack = (pack[0] + rext / 1000.0, pack[1])
    out = {}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR")):
        fr = limited(prop, rho, kT, kP, kv, rm, i0, esc, ocv[0], pack[0], pack[1], n, ilim)
        lo = limited(prop, rho, kT, kP, kv, r_hot(rm, tc[0], tc[1]), i0, esc, ocv[2], pack[0], pack[1], n, ilim)
        out[f"I_motor_fresh_{tag}_A"] = fr["I_bat_A"]           # battery side, per ESC input
        out[f"tw_fresh_{tag}"] = n * fr["T_N"] / W
        out[f"tw_low_{tag}"] = n * lo["T_N"] / W
        out[f"I_motor_low_{tag}_A"] = lo["I_bat_A"]
        out[f"Ipack_fresh_{tag}_A"] = n * fr["I_bat_A"] + pack[1]
        # CDR-05: the motor rating is a winding (phase) current. At duty d the ESC is a buck stage: I_m = I_bat / d
        # (less the ESC's own loss), so the winding carries more than the battery lead whenever d < 1
        out[f"I_wind_fresh_{tag}_A"] = fr["I_m_A"]
        out[f"I_wind_low_{tag}_A"] = lo["I_m_A"]
        out[f"duty_fresh_{tag}"] = fr["duty"]
        out[f"duty_low_{tag}"] = lo["duty"]
        out[f"loss_wind_fresh_{tag}_W"] = fr["P_loss_motor_W"]
    return out


@kit.calc("CALC-E1-ILIM-25", title="Pack-current limit that holds 25 A in the winding (11x5.5E/EP, fresh pack)",
          equation="solve I_lim: I_m(largest duty with 4 I_bat + I_avn <= I_lim) = I_rating ; "
                   "T/W = 4 T cos(cant) / (m_gate g) at that limit, fresh (4.20 V/cell, warm R, 25 degC winding)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "cant": P + "propulsion.stations.cant_deg", "cells": P + "battery.cells_s",
                  "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0",
                  "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK-CELLS", "r_cell": "ASM-E2-R-CELL",
                  "r_ext": P + "electrical.r_ext_mohm", "i_rate": P + "propulsion.motor_max_a"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "cant": "deg", "r_cell": "ohm", "r_ext": "mOhm", "i_rate": "A"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E2-R-CELL"])
def ilim_25(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, r_cell, r_ext, i_rate):
    r = cells * r_cell + r_ext / 1000.0
    voc = cells * 4.20

    def at(il):
        return limited(DESIGN, rho, kT, kP, kv, rm, i0, esc, voc, r, pack[1], n, il)
    il = bisect(lambda x: at(x)["I_m_A"] - i_rate, 40.0, 250.0, n=28)
    s = at(il)
    return {"ilim_a": il, "tw": n * s["T_N"] * math.cos(math.radians(cant)) / (m * g), "T_gf": s["T_N"] / g * 1000,
            "I_wind_A": s["I_m_A"], "I_bat_A": s["I_bat_A"]}


@kit.calc("CALC-E1-WORST", title="Hover T/W at the worst pack state (E1 station model + E2 pack model)",
          equation="R_pack = cells R_cell k_cold + R_ext ; V_ocv = cells OCV ; largest duty with 4 I_bat + I_avn <= I_lim "
                   "(station model, winding 80 degC) ; T/W = 4 T cos(cant) / (m_gate g) ; "
                   "f_sag = T_worst / T_fresh (fresh: 4.20 V/cell, warm R, 25 degC)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "cant": P + "propulsion.stations.cant_deg", "cells": P + "battery.cells_s",
                  "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0",
                  "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK-CELLS", "tc": "ASM-E1-TCOPPER", "ilim": P + "performance.full_throttle_current_a",
                  "state": "ASM-E1-WORST-STATE", "ocv20": "ASM-E2-OCV-20", "r_cell": "ASM-E2-R-CELL",
                  "r_ext": P + "electrical.r_ext_mohm", "cold": "ASM-E2-COLD-R"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "cant": "deg", "ilim": "A", "ocv20": "V", "r_cell": "ohm",
                 "r_ext": "mOhm"},
          assumes=["ASM-E1-WORST-STATE", "ASM-E1-CAL-TRANSFER", "ASM-E1-ILIM", "ASM-E2-OCV-20", "ASM-E2-R-CELL",
                   "ASM-E2-COLD-R"])
def worst(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, r_ext, cold):
    W = m * g
    r_ext = r_ext / 1000.0
    cc = math.cos(math.radians(cant))
    r_warm = cells * r_cell + r_ext
    r_cold = cells * r_cell * cold + r_ext
    rm_hot = r_hot(rm, tc[0], state[0])
    prop = DESIGN
    cases = {"fresh": (cells * 4.20, r_warm, rm), "res20_warm": (cells * ocv20, r_warm, rm_hot),
             "worst": (cells * ocv20, r_cold, rm_hot), "land_cold": (cells * state[1], r_cold, rm_hot)}
    out = {"r_pack_cold_ohm": r_cold, "r_pack_warm_ohm": r_warm}
    for k, (voc, r, rmk) in cases.items():
        s = limited(prop, rho, kT, kP, kv, rmk, i0, esc, voc, r, pack[1], n, ilim)
        out[f"tw_{k}"] = n * s["T_N"] * cc / W
        out[f"T_{k}_gf"] = s["T_N"] / g * 1000
        out[f"Vbus_{k}_V"] = s["V_bus_V"]
        out[f"Ipack_{k}_A"] = n * s["I_bat_A"] + pack[1]
        out[f"I_motor_{k}_A"] = s["I_bat_A"]
        out[f"I_wind_{k}_A"] = s["I_m_A"]                       # winding (phase) current, CDR-05
        out[f"limited_{k}"] = 1.0 if "duty_max" in s else 0.0
    out["f_sag"] = out["T_worst_gf"] / out["T_fresh_gf"]
    # closed-form cross-check: limiter binding in both states -> same pack current; static thrust ~ P^(2/3)
    # (momentum theory, fixed disc), P ~ V_bus I_lim, winding temperature ignored (so it bounds f_sag from above)
    v_f = cells * 4.20 - ilim * r_warm
    v_w = cells * ocv20 - ilim * r_cold
    out["f_sag_closed_form"] = (v_w / v_f) ** (2.0 / 3.0)
    out["f_sag_land"] = out["T_land_cold_gf"] / out["T_fresh_gf"]
    return out


WORST_IN = {"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
            "rho": P + "env.rho_kgm3", "cant": P + "propulsion.stations.cant_deg", "cells": P + "battery.cells_s",
            "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0",
            "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK-CELLS", "tc": "ASM-E1-TCOPPER", "ilim": P + "performance.full_throttle_current_a",
            "state": "ASM-E1-WORST-STATE", "ocv20": "ASM-E2-OCV-20", "r_cell": "ASM-E2-R-CELL", "cold": "ASM-E2-COLD-R"}
WORST_UNITS = {"m": "kg", "g": "m/s2", "rho": "kg/m3", "cant": "deg", "ilim": "A", "ocv20": "V", "r_cell": "ohm"}
WORST_ASM = ["ASM-E1-WORST-STATE", "ASM-E1-CAL-TRANSFER", "ASM-E1-ILIM", "ASM-E2-OCV-20", "ASM-E2-R-CELL",
             "ASM-E2-COLD-R"]


@kit.calc("CALC-E1-REXT-ALLOW", title="Path resistance and limiter voltage drop the thrust requirement allows",
          equation="R_allow (rev 10: first bound only; the second bound is information) = min over the two cases "
                   "(and, for information, over the two bounds) of the R_ext at which T/W_worst(R_ext) = "
                   "T/W_min,sag or T/W_fresh(R_ext) = T/W_min (bisection on the cases of CALC-E1-WORST and "
                   "CALC-E1-BOUND2), each bound at its own D-148 limiter (first: I_lim, second: I_b2) ; "
                   "drop_allow = 100 I_lim R_allow / V_nom (both bounds, information: 100 min(I_lim R_allow,1 , I_b2 R_allow,2) / V_nom) ; "
                   "thrust cost of the path = 1 - T_worst(R_ext) / T_worst(0)",
          inputs={**WORST_IN, "r_ext": P + "electrical.r_ext_mohm", "tw_min": P + "requirements.hover_tw_min",
                  "tw_sag": P + "requirements.hover_tw_min_sag", "v_nom": P + "battery.v_nom",
                  "reff": "CL-E1-R-EFF-MAKER", "ib2": "ASM-E1-ILIM-B2"},
          units={**WORST_UNITS, "r_ext": "mOhm", "v_nom": "V", "reff": "ohm", "ib2": "A"},
          assumes=WORST_ASM + ["ASM-E1-BOUND2", "ASM-E1-ILIM-B2"])
def rext_allow(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, cold,
               r_ext, tw_min, tw_sag, v_nom, reff, ib2):
    # rev 9 (wave 2, D-148): the limiter now depends on the bound (70 A first, 93 A second once T-E1-STAND reads
    # it), so each bound's allowance is taken at its own value. At 70 A the second bound fails R-HOVER-TW with no
    # path at all (CL-E1-TW-FRESH-B2), which would make this allowance 0 and say nothing about the path:
    # r_allow_b2_at_ilim_mohm keeps that reading visible
    W = m * g
    cc = math.cos(math.radians(cant))
    rm_hot = r_hot(rm, tc[0], state[0])
    rm2 = reff - esc[0]                                         # second bound, as CALC-E1-BOUND2

    def tw(case, rx, b2=False, il_=None):                       # rx in ohm
        if case == "worst":
            voc, r, rmk = cells * ocv20, cells * r_cell * cold + rx, (rm2 if b2 else rm_hot)
        else:
            voc, r, rmk = cells * 4.20, cells * r_cell + rx, (rm2 if b2 else rm)
        il = ilim if il_ is None else il_
        return n * limited(DESIGN, rho, kT, kP, kv, rmk, i0, esc, voc, r, pack[1], n, il)["T_N"] * cc / W

    def allow(case, need, b2, il=None):                         # 0 if the requirement fails even with no path
        il = il if il is not None else (ib2 if b2 else ilim)
        return (bisect(lambda rx: tw(case, rx, b2, il) - need, 0.0, 0.200, n=18)
                if tw(case, 0.0, b2, il) > need else 0.0)
    r_w, r_f = allow("worst", tw_sag, False), allow("fresh", tw_min, False)
    r_w2, r_f2 = allow("worst", tw_sag, True), allow("fresh", tw_min, True)
    r_b2_at_ilim = min(allow("worst", tw_sag, True, ilim), allow("fresh", tw_min, True, ilim))
    r_1, r_2 = min(r_w, r_f), min(r_w2, r_f2)
    r_a = r_1          # rev 10 (closure round): the second bound is a rejected reading (CALC-E1-BOUND2-CHECK), so the
    #                    allowance is the first bound's; r_2 stays an output for information (r_allow_b2_mohm)
    rx = r_ext / 1000.0
    t0, t1 = tw("worst", 0.0), tw("worst", rx)
    u0, u1 = tw("worst", 0.0, True, ib2), tw("worst", rx, True, ib2)
    return {"r_allow_worst_mohm": r_w * 1e3, "r_allow_fresh_mohm": r_f * 1e3, "r_allow_first_mohm": r_1 * 1e3,
            "r_allow_worst_b2_mohm": r_w2 * 1e3, "r_allow_fresh_b2_mohm": r_f2 * 1e3,
            "r_allow_b2_at_ilim_mohm": r_b2_at_ilim * 1e3,
            "r_allow_mohm": r_a * 1e3, "r_allow_b2_mohm": r_2 * 1e3, "drop_allow_pct": 100 * ilim * r_1 / v_nom,
            "drop_allow_both_pct": 100 * min(ilim * r_1, ib2 * r_2) / v_nom,
            "drop_allow_first_pct": 100 * ilim * r_1 / v_nom, "r_ext_use": rx / r_a if r_a > 0 else 1e9,
            "tw_worst_r0": t0, "thrust_cost_path": 1 - t1 / t0, "thrust_cost_path_b2": 1 - u1 / u0}


@kit.calc("CALC-E1-BOUND2", title="Second bound: the maker's rows above 12 A read as true 14.8 V points (11x5.5E/EP)",
          equation="R_eff from the maker's 30 A row (CALC-E1-CAL) replaces R_m + R_esc ; then as CALC-E1-WORST: "
                   "largest duty with 4 I_bat + I_avn <= I_lim, T/W = 4 T cos(cant) / (m_gate g) ; "
                   "sensitivity (CDR-AE-01 rule): rpm_full = rpm_full(14.8 V held) x V_bus / 14.8 ; stand point: bus "
                   "held at V_stand ; T_need = T/W_min,sag m / (4 cos cant)",
          inputs={**WORST_IN, "r_ext": P + "electrical.r_ext_mohm", "reff": "CL-E1-R-EFF-MAKER",
                  "tw_sag": P + "requirements.hover_tw_min_sag", "v_stand": "ASM-E1-V-STAND-LOW"},
          units={**WORST_UNITS, "r_ext": "mOhm", "reff": "ohm", "v_stand": "V"},
          assumes=WORST_ASM + ["ASM-E1-BOUND2", "ASM-E1-V-STAND-LOW"],
          cites=["SRC-E1-X3108S-DATA"])
def bound2(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, cold,
           r_ext, reff, tw_sag, v_stand):
    W = m * g
    cc = math.cos(math.radians(cant))
    rx = r_ext / 1000.0
    rm2 = reff - esc[0]                                         # the winding carries all of R_eff but the ESC's share
    prop = DESIGN
    cases = {"fresh": (cells * 4.20, cells * r_cell + rx), "worst": (cells * ocv20, cells * r_cell * cold + rx)}
    out = {"rm_eff_ohm": rm2}
    for k, (voc, r) in cases.items():
        s = limited(prop, rho, kT, kP, kv, rm2, i0, esc, voc, r, pack[1], n, ilim)
        out[f"tw_{k}"] = n * s["T_N"] * cc / W
        out[f"T_{k}_gf"] = s["T_N"] / g * 1000
        out[f"Vbus_{k}_V"] = s["V_bus_V"]
        out[f"rpm_{k}"] = s["rpm"]
        out[f"I_wind_{k}_A"] = s["I_m_A"]
        out[f"I_motor_{k}_A"] = s["I_bat_A"]
        out[f"limited_{k}"] = 1.0 if "duty_max" in s else 0.0
    # sensitivity, the reviewer's rule: full-throttle rpm goes with the bus voltage (no credit for the smaller
    # I R drop at the lower current). Reference = full throttle of this prop at a held 14.8 V on R_eff, no limiter
    ref = full_throttle(prop, 0.0, rho, kT, kP, kv, rm2, i0, esc[0], esc[1], 14.8, 0.0, pack[1], n)
    voc, r = cases["worst"]
    v = voc
    for _ in range(60):
        rpm = ref["rpm"] * v / 14.8
        s = station(prop, rpm, 0.0, rho, kT, kP, kv, rm2, i0, esc[0], esc[1], v)
        v_new = voc - r * (n * s["I_bat_A"] + pack[1])
        if abs(v_new - v) < 1e-7:
            break
        v = 0.5 * (v + v_new)
    out.update({"rpm_ref_148": ref["rpm"], "T_ref_148_gf": ref["T_N"] / g * 1000, "rpm_worst_prop": rpm,
                "Vbus_worst_prop_V": v, "T_worst_prop_gf": s["T_N"] / g * 1000, "tw_worst_prop": n * s["T_N"] * cc / W})
    # the stand point of CDR condition B-7: one station, bus HELD at v_stand (bench supply), full throttle
    held = limited(prop, rho, kT, kP, kv, rm2, i0, esc, v_stand, 0.0, pack[1], n, ilim)
    hp = station(prop, ref["rpm"] * v_stand / 14.8, 0.0, rho, kT, kP, kv, rm2, i0, esc[0], esc[1], v_stand)
    first = limited(prop, rho, kT, kP, kv, r_hot(rm, tc[0], state[0]), i0, esc, v_stand, 0.0, pack[1], n, ilim)
    out.update({"T_need_sag_gf": tw_sag * m * 1000 / (n * cc), "T_stand_gf": held["T_N"] / g * 1000,
                "rpm_stand": held["rpm"], "T_stand_prop_gf": hp["T_N"] / g * 1000, "rpm_stand_prop": hp["rpm"],
                "T_stand_first_gf": first["T_N"] / g * 1000, "rpm_stand_first": first["rpm"]})
    return out


@kit.calc("CALC-E1-BOUND2-CHECK", title="Second bound against every published full-throttle row of the maker",
          equation="held-voltage reading of a full-throttle row (duty <= 1, V_ESC = V_label): V_label d = w / Kv + I_m R, "
                   "I_m = I_bat / d - P_esc0 / V_label -> R <= R_ub = (V_label - w / Kv) / (I_bat - P_esc0 / V_label) "
                   "(maker numbers only, no prop model) ; spread = max R_ub / min R_ub (a fixed station has one R) ; "
                   "second bound at the 11.1 V 11x4.7 row: full throttle on R_eff (CALC-E1-BOUND2) at a held 11.1 V, "
                   "miss = 1 - T_pred / T_maker ; R_m needed = (R - R_esc) / R_m(T_row) with R_m(T) = R_25 (1 + a (T - 25)) ; "
                   "first bound at the same row: supply needed at duty 1 = V_m + I_m R_esc at the measured rpm",
          inputs={"rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "rm": "ASM-E1-CAL-RM", "i0": "ASM-E1-CAL-I0", "esc": "ASM-E1-ESC",
                  "kP": "CL-E1-KP-SF", "kT": "CL-E1-KT-SF", "tc": "ASM-E1-TCOPPER", "reff": "CL-E1-R-EFF-MAKER"},
          units={"rho": "kg/m3", "kv": "rpm/V", "rm": "ohm", "i0": "A", "reff": "ohm"},
          assumes=["ASM-E1-KV", "ASM-E1-CAL-RM", "ASM-E1-CAL-I0", "ASM-E1-ESC", "ASM-E1-TCOPPER"],
          cites=["SRC-E1-X3108S-DATA", "SRC-E1-X3108S-DATA-111", "SRC-E1-APC-PER3"])
def bound2_check(rho, kv, rm, i0, esc, kP, kT, reff, tc):
    rows = []
    for pr, v, a, rpm, gf, t in MAKER_FT:
        r_ub = (v - rpm / kv) / (a - esc[1] / v)
        code = float(pr.split("x")[0]) + float(pr.split("x")[1]) / 100.0      # 10x3.8 -> 10.038 (numeric for report)
        rows.append([code, v, a, rpm, r_ub, t, (r_ub - esc[0]) / r_hot(rm, tc[0], t)])
    r_min = min(rows, key=lambda r: r[4])
    # the second bound (R_eff of the 14.8 V 30 A row, winding share reff - R_esc) run at the 11.1 V 11x4.7 row
    b2 = full_throttle("11x4.7SF", 0.0, rho, kT, kP, kv, reff - esc[0], i0, esc[0], esc[1], 11.1, 0.0, 0.0, 1)
    ref = next(r for r in MAKER_FT if r[0] == "11x4.7" and r[1] == 11.1)
    # the first bound at the same row: the supply that the measured rpm needs at duty 1 (winding at the row's 62 degC)
    s1 = station("11x4.7SF", ref[3], 0.0, rho, kT, kP, kv, r_hot(rm, tc[0], ref[5]), i0, esc[0], esc[1], ref[1])
    return {"r_ub_rows": rows, "r_ub_min_ohm": r_min[4], "r_ub_max_ohm": max(r[4] for r in rows),
            "r_ub_spread": max(r[4] for r in rows) / r_min[4],
            "rm_needed_min": r_min[6],
            "rm_needed_b2": (reff - esc[0]) / r_hot(rm, tc[0], MAKER_TEMP_C),
            "b2_111_rpm": b2["rpm"], "b2_111_gf": b2["T_N"] / 9.80665e-3, "b2_111_A": b2["I_bat_A"],
            "maker_111_rpm": ref[3], "maker_111_gf": ref[4], "maker_111_A": ref[2],
            "b2_miss_111": 1 - b2["T_N"] / 9.80665e-3 / ref[4],
            "b1_supply_111_V": s1["V_m_V"] + s1["I_m_A"] * esc[0], "b1_T_111_gf": s1["T_N"] / 9.80665e-3,
            "b1_T_err_111": s1["T_N"] / 9.80665e-3 / ref[4] - 1}


@kit.calc("CALC-E1-STACK", title="Prop stack, prop-to-structure gap, nut and motor-screw engagement",
          equation="s = L_body + t_base + h_hub / 2 ; x_tip = L_body + t_base + L_post ; "
                   "e_nut = L_post - h_hub - t_washer - h_nut ; gap = face_ahead + s >= 0.14 D (B4) ; "
                   "e_screw = L_screw - t_plate (D3 R3: plate canted with the motor, uniform under every head)",
          inputs={"st": "ASM-E1-STACK", "sc": "ASM-E1-MOUNT-SCREW", "d3_stack": P + "fin_detail.mount.prop_stack_m",
                  "ahead": P + "fin_detail.mount.face_ahead_m", "D": P + "propulsion.prop_diameter_m",
                  "tp": P + "fin_detail.mount.plate_t_m", "ls": P + "fin_detail.mount.motor_screw_len_m"},
          units={"st": "m", "sc": "m", "d3_stack": "m", "ahead": "m", "D": "m", "tp": "m", "ls": "m"},
          assumes=["ASM-E1-STACK", "ASM-E1-MOUNT-SCREW"])
def stack(st, sc, d3_stack, ahead, D, tp, ls):
    body, base, post, hub, wash, nut = st
    _, e_min, e_max = sc[:3]
    wsh = sc[3] if len(sc) > 3 else 0.0                  # D-173: washers under the motor-screw heads
    s = body + base + hub / 2
    e = ls - tp - wsh
    return {"mount_to_prop_plane_m": s, "mount_to_hub_front_m": body + base + hub,
            "mount_to_post_tip_m": body + base + post, "hub_half_m": hub / 2,
            "stack_minus_d3_m": s - d3_stack,
            "gap_e1_m": ahead + s, "gap_ratio_e1": (ahead + s) / (0.14 * D),
            "ahead_needed_m": 0.14 * D - s,
            "nut_engagement_m": post - hub - wash, "nut_margin_m": round(post - hub - wash - nut, 9),
            "screw_engagement_m": e, "screw_margin_m": round(min(e - e_min, e_max - e), 9),
            "hole_depth_min_m": e + 0.0005,
            "seat_for_mid_window_m": ls - 0.5 * (e_min + e_max)}


@kit.calc("CALC-E1-MASS", title="Propulsion flying mass, four stations, per-unit masses incl. leads",
          equation="m = n (motor + ESC + prop + adapter and nut + motor screws)",
          inputs={"pm": "ASM-E1-PART-MASS", "n": P + "propulsion.n_motors"}, units={"pm": "g"},
          assumes=["ASM-E1-PART-MASS"])
def mass(pm, n):
    station = sum(pm.values())
    return {"station_g": station, "total_g": n * station,
            "total_ex_screws_g": n * (station - pm["motor_screws"])}


def cruise_drag(V, m, g, rho, S, cd0, k, trim):
    """B1's as-designed polar (rev 8: CL-B1V-CD0, CL-B1V-K from AVL + XFOIL + SU2 fins; ASM-B1-TRIM):
    D = q S (CD0 + k CL^2) trim (as CALC-B1V-CRUISE)."""
    cl = 2 * m * g / (rho * V * V * S)
    return 0.5 * rho * V * V * S * (cd0 + k * cl * cl) * trim


@kit.calc("CALC-E1-CRUISE", title="Cruise point on B1's polar: four props share the drag",
          equation="CL = 2W/(rho V^2 S) ; D = q S (CD0 + k CL^2) trim (B1's as-designed polar, = CALC-B1V-CRUISE "
                   "drag_gate_n) ; T_m = D / (4 cos cant) ; solve rpm: T(rpm, J) = T_m ; eta_prop = T V / P_shaft ; "
                   "eta_tot = T V / P_bat ; L/D_eff = W / D ; p_check = (P_55 + avionics) / B1 gate power",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "cd0": "CL-B1V-CD0", "k": "CL-B1V-K", "trim": "ASM-B1-TRIM",
                  "p_b1": "CL-B1V-CRUISE-P-GATE", "av": "ASM-B1-AVIONICS-W",
                  "V": P + "performance.cruise_ms", "n": P + "propulsion.n_motors", "kP": "CL-E1-KP", "kT": "CL-E1-KT",
                  "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC",
                  "cant": P + "propulsion.stations.cant_deg"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "V": "m/s", "S": "m2", "p_b1": "W", "av": "W", "cant": "deg"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-B1-TRIM"], cites=["SRC-E1-APC-PER3"])
def cruise(m, g, rho, S, cd0, k, trim, p_b1, av, V, n, kP, kT, kv, rm, i0, esc, cant):
    # rev 9 (wave 2, D-146): the canted axis puts T cos(cant) along the flight path; the tangential parts cancel
    # over the four stations. Inflow is taken as axial (V along the shaft; the 9 deg skew is not modelled)
    D = cruise_drag(V, m, g, rho, S, cd0, k, trim)
    T = D / (n * math.cos(math.radians(cant)))
    out = {"drag_N": D, "T_per_motor_N": T, "cd0": cd0, "k": k, "ld_eff": m * g / D}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR"), ("12x4.5MR", "12")):
        s = at_thrust(prop, T, V, rho, min(1.0, kT), kP, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
        out[f"J_{tag}"] = s["J"]
        out[f"rpm_{tag}"] = s["rpm"]
        out[f"eta_prop_{tag}"] = T * V / s["P_shaft_W"]
        out[f"eta_motor_{tag}"] = s["P_shaft_W"] / s["P_motor_in_W"]
        out[f"eta_tot_{tag}"] = D / n * V / s["P_bat_W"]          # useful power along the path
        out[f"P_total_{tag}_W"] = n * s["P_bat_W"]
        out[f"I_pack_{tag}_A"] = n * s["I_bat_A"]
        out[f"I_m_{tag}_A"] = s["I_m_A"]
        out[f"loss_motor_{tag}_W"] = s["P_loss_motor_W"]
        out[f"Q_{tag}_Nm"] = s["P_shaft_W"] / (s["rpm"] * 2 * math.pi / 60)
    out["p_check"] = (out["P_total_55_W"] + av) / p_b1          # E1 station model vs B1's chain on the same drag
    return out




@kit.calc("CALC-E1-CRUISE-V17", title="Cruise point at the 17 m/s fallback speed (D-96 c, B6), 11x5.5E/EP",
          equation="as CALC-E1-CRUISE at V = 17 m/s: D = q S (CD0 + k CL^2) trim ; T_m = D / (4 cos cant) ; "
                   "P = 4 P_bat(T_m, J) ; ratio = P(17) / P(cruise_ms)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "S": "CL-A1-WING-AREA", "cd0": "CL-B1V-CD0", "k": "CL-B1V-K", "trim": "ASM-B1-TRIM",
                  "V": "ASM-E1-V-FALLBACK", "p16": "CL-E1-CRUISE-P-55", "n": P + "propulsion.n_motors",
                  "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC",
                  "cant": P + "propulsion.stations.cant_deg"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "V": "m/s", "S": "m2", "p16": "W", "cant": "deg"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-B1-TRIM", "ASM-E1-V-FALLBACK"], cites=["SRC-E1-APC-PER3"])
def cruise_v17(m, g, rho, S, cd0, k, trim, V, p16, n, kP, kT, kv, rm, i0, esc, cant):
    D = cruise_drag(V, m, g, rho, S, cd0, k, trim)
    cc = math.cos(math.radians(cant))
    kt = min(1.0, kT)       # D-173: the 11x8E fit has kT < 1 (PER3 over-predicts thrust); never credit kT > 1 in flight
    s = at_thrust(DESIGN, D / (n * cc), V, rho, kt, kP, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
    s0 = at_thrust(DESIGN, D / n, V, rho, kt, kP, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
    return {"drag_N": D, "ld_eff": m * g / D, "P_total_55_W": n * s["P_bat_W"], "rpm_55": s["rpm"], "J_55": s["J"],
            "eta_tot_55": D / n * V / s["P_bat_W"], "ratio_to_cruise": n * s["P_bat_W"] / p16,
            "P_total_55_nocant_W": n * s0["P_bat_W"], "cant_cost": s["P_bat_W"] / s0["P_bat_W"] - 1}


def wing_cl_cd(alpha, cla, clmax, cd0, K):
    a_s = clmax / cla
    if alpha <= a_s:
        cl = cla * alpha
        return cl, cd0 + K * cl * cl
    cn = 1.98 * math.sin(alpha)
    return cn * math.cos(alpha), cd0 + cn * math.sin(alpha)


def corridor(prop, m, g, rho, S, b, cd0, k, trim, clmax, v_end, kT, kP, kv, rm, i0, esc, pack, ocv, n, steps=30):
    """Level pitch-over corridor: at each V find the body angle alpha (thrust axis above horizontal) that needs the
    least thrust for level unaccelerated flight, and the full thrust available there (axial inflow V cos alpha).
    Attached-flow polar = B1's trimmed polar (cd0 trim, k trim)."""
    AR = b * b / S
    cla = 2 * math.pi * AR / (AR + 2)
    K = k * trim
    cd0 = cd0 * trim
    W = m * g
    worst = None
    rows = []
    for i in range(steps + 1):
        V = v_end * i / steps
        q = 0.5 * rho * V * V
        best = None
        for k in range(1, 180):
            al = math.radians(k * 0.5)
            cl, cd = wing_cl_cd(al, cla, clmax, cd0, K)
            L, D = q * S * cl, q * S * cd
            # thrust along the body axis (angle al above the flight path): T sin al + L = W ; T cos al = D (+accel)
            # unknown T from the vertical equation; horizontal surplus T cos al - D must be >= 0 (level, accelerating)
            if L >= W:
                Treq = D / math.cos(al)
            else:
                Treq = max((W - L) / math.sin(al), D / math.cos(al))
            if best is None or Treq < best[0]:
                best = (Treq, al)
        Treq, al = best
        s = full_throttle(prop, V * math.cos(al), rho, 1.0, kP, kv, r_hot(rm, 0.00393, 80.0), i0, esc[0], esc[1],
                          ocv[2], pack[0], pack[1], n)
        ratio = n * s["T_N"] / Treq
        rows.append((V, math.degrees(al), Treq / W, ratio))
        if worst is None or ratio < worst[3]:
            worst = rows[-1]
    return worst, rows


@kit.calc("CALC-E1-CORRIDOR", title="Thrust margin along the level pitch-over corridor (sag case, 11x4.5MR and 11x5.5E/EP)",
          equation="min over V in [0, V_tr] of 4 T_full(V cos a, OCV 14.4 V, 80 degC) / T_req,min(V) ; "
                   "T_req from T sin a + L = W, T cos a >= D ; polar CL-B1V-CD0, CL-B1V-K, ASM-B1-TRIM (rev 8)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "b": P + "wing.span_m", "S": "CL-A1-WING-AREA", "cd0": "CL-B1V-CD0", "k": "CL-B1V-K",
                  "trim": "ASM-B1-TRIM", "clmax": P + "performance.clmax",
                  "vtr": P + "performance.transition_min_ms", "n": P + "propulsion.n_motors", "kP": "CL-E1-KP",
                  "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC",
                  "pack": "ASM-E1-PACK-CELLS", "rext": P + "electrical.r_ext_mohm", "ocv": "ASM-E1-OCV"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "vtr": "m/s", "b": "m", "S": "m2", "rext": "mOhm"},
          assumes=["ASM-E1-POSTSTALL", "ASM-E1-CAL-TRANSFER", "ASM-E1-PACK-CELLS", "ASM-B1-TRIM"])
def corridor_calc(m, g, rho, b, S, cd0, k, trim, clmax, vtr, n, kP, kv, rm, i0, esc, pack, rext, ocv):
    pack = (pack[0] + rext / 1000.0, pack[1])
    out = {}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR")):
        worst, _ = corridor(prop, m, g, rho, S, b, cd0, k, trim, clmax, vtr, 1.0, kP, kv, rm, i0, esc, pack, ocv, n)
        out[f"margin_{tag}"] = worst[3]
        out[f"V_worst_{tag}_ms"] = worst[0]
        out[f"Treq_over_W_{tag}"] = worst[2]
    return out


@kit.calc("CALC-E1-MOTOR-OUT", title="One motor out: what is left (11x5.5E/EP)",
          equation="hover: thrust/moment balance forces the diagonal partner to 0 -> 2 same-direction motors, "
                   "T/W_2 = 2 T_max,worst / W, unbalanced yaw torque = 2 Q_hover ; cruise: 2 motors carry D, "
                   "roll torque = 2 Q(T = D/2) for elevons to hold",
          inputs={"full": "CL-E1-TMAX-WORST", "m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2",
                  "rho": P + "env.rho_kgm3", "drag": "CL-E1-CRUISE-DRAG", "V": P + "performance.cruise_ms",
                  "T_h": "CL-E1-HOVER-T", "kP": "CL-E1-KP", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0",
                  "esc": "ASM-E1-ESC"},
          units={"full": "gf", "m": "kg", "g": "m/s2", "rho": "kg/m3", "drag": "N", "V": "m/s", "T_h": "N"},
          assumes=["ASM-E1-CAL-TRANSFER"])
def motor_out(full, m, g, rho, drag, V, T_h, kP, kv, rm, i0, esc):
    W = m * g
    pr = DESIGN
    sh = at_thrust(pr, T_h, 0.0, rho, 1.0, kP, kv, rm, i0, esc[0], esc[1], 14.8)
    q_h = sh["P_shaft_W"] / (sh["rpm"] * 2 * math.pi / 60)
    sc = at_thrust(pr, drag / 2, V, rho, 1.0, kP, kv, rm, i0, esc[0], esc[1], 14.8)
    q_c = sc["P_shaft_W"] / (sc["rpm"] * 2 * math.pi / 60)
    qs = []
    for f in (1.3, 0.7):
        t = at_thrust(pr, f * T_h, 0.0, rho, 1.0, kP, kv, rm, i0, esc[0], esc[1], 14.8)
        qs.append(t["P_shaft_W"] / (t["rpm"] * 2 * math.pi / 60))
    return {"tw_two_motors": 2 * full * g / 1000 / W, "yaw_torque_hover_Nm": 2 * q_h, "q_hover_per_motor_Nm": q_h,
            "yaw_diff30_Nm": 2 * (qs[0] - qs[1]),
            "roll_torque_cruise_Nm": 2 * q_c, "I_bat_cruise_2mot_A": sc["I_bat_A"],
            "P_cruise_2mot_W": 2 * sc["P_bat_W"]}


@kit.calc("CALC-E1-ILIM-COND", title="Limiter conditions: sensor band (first bound) and the 93 A second-bound case",
          equation="first bound, fresh case of CALC-E1-WORST: I_m(I_lim (1 + tol)) <= I_rating ; "
                   "R_m band (rev 10): R_m,lo: I_m(I_lim (1 + tol); R_m) = I_rating, R_m,hi: T/W(I_lim (1 - tol); R_m) = T/W_min ; "
                   "T/W(I_lim (1 - tol)) = 4 T cos(cant) / (m g) >= T/W_min ; window [I_lo, I_hi]: T/W(I_lo) = "
                   "T/W_min, I_m(I_hi) = I_rating ; tol_ok = min(I_hi / I_lim - 1, 1 - I_lo / I_lim) ; "
                   "second bound at I_b2 as CALC-E1-BOUND2 (and the first bound at I_b2 for the winding)",
          inputs={**WORST_IN, "r_ext": P + "electrical.r_ext_mohm", "reff": "CL-E1-R-EFF-MAKER",
                  "tol": "ASM-E1-SENSOR-TOL", "ib2": "ASM-E1-ILIM-B2", "tw_min": P + "requirements.hover_tw_min",
                  "tw_sag": P + "requirements.hover_tw_min_sag", "i_rate": P + "propulsion.motor_max_a",
                  "v_stand": "ASM-E1-V-STAND-LOW"},
          units={**WORST_UNITS, "r_ext": "mOhm", "reff": "ohm", "ib2": "A", "i_rate": "A", "v_stand": "V"},
          assumes=WORST_ASM + ["ASM-E1-SENSOR-TOL", "ASM-E1-ILIM-B2", "ASM-E1-BOUND2", "ASM-E1-V-STAND-LOW"])
def ilim_cond(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, cold,
              r_ext, reff, tol, ib2, tw_min, tw_sag, i_rate, v_stand):
    W = m * g
    cc = math.cos(math.radians(cant))
    rx = r_ext / 1000.0
    rm2 = reff - esc[0]
    rm_hot = r_hot(rm, tc[0], state[0])
    fresh = (cells * 4.20, cells * r_cell + rx)
    worst = (cells * ocv20, cells * r_cell * cold + rx)
    pr = DESIGN

    def at(il, case, rmk):
        return limited(pr, rho, kT, kP, kv, rmk, i0, esc, case[0], case[1], pack[1], n, il)

    def tw(s):
        return n * s["T_N"] * cc / W
    hi, lo = at(ilim * (1 + tol), fresh, rm), at(ilim * (1 - tol), fresh, rm)
    i_hi = bisect(lambda x: at(x, fresh, rm)["I_m_A"] - i_rate, 40.0, 250.0, n=30)
    i_lo = bisect(lambda x: tw(at(x, fresh, rm)) - tw_min, 40.0, 120.0, n=30)
    i_lo_sag = bisect(lambda x: tw(at(x, worst, rm_hot)) - tw_sag, 40.0, 120.0, n=30)
    f2, w2, f1 = at(ib2, fresh, rm2), at(ib2, worst, rm2), at(ib2, fresh, rm)
    st2 = limited(pr, rho, kT, kP, kv, rm2, i0, esc, v_stand, 0.0, pack[1], n, ib2)
    # rev 10 (closure round): the winding-resistance band this limiter and sensor band accept. A higher R_m moves the
    # whole window up (more pack current for the same rpm), a lower one down; the window width does not change
    rm_hi = bisect(lambda r: tw(at(ilim * (1 - tol), fresh, r)) - tw_min, 0.005, 0.160, n=22)
    rm_lo = bisect(lambda r: at(ilim * (1 + tol), fresh, r)["I_m_A"] - i_rate, 0.005, 0.160, n=22)
    return {"rm_ok_lo_mohm": rm_lo * 1e3, "rm_ok_hi_mohm": rm_hi * 1e3,"I_wind_sens_hi_A": hi["I_m_A"], "tw_fresh_sens_lo": tw(lo), "I_wind_sens_lo_A": lo["I_m_A"],
            "tw_fresh_sens_hi": tw(hi), "ilim_hi_a": i_hi, "ilim_lo_a": i_lo, "ilim_lo_sag_a": i_lo_sag,
            "tol_ok_hi": i_hi / ilim - 1, "tol_ok_lo": 1 - i_lo / ilim,
            "tol_ok": min(i_hi / ilim - 1, 1 - i_lo / ilim), "ilim_centre_a": 0.5 * (i_hi + i_lo),
            "tol_centre": (i_hi - i_lo) / (i_hi + i_lo),
            "I_wind_fresh_b2_ib2_A": f2["I_m_A"], "tw_fresh_b2_ib2": tw(f2), "tw_worst_b2_ib2": tw(w2),
            "I_wind_fresh_b1_ib2_A": f1["I_m_A"], "tw_fresh_b1_ib2": tw(f1), "T_stand_b2_ib2_gf": st2["T_N"] / g * 1000}


kit.assumption("ASM-E1-RM-BAND", "Winding-resistance design band +/-10 % about 86 mOhm (D-161)",
               "every R-HOVER-TW and R-ESC-CURRENT edge is checked with R_m(25 degC) anywhere in 86 mOhm x (1 +/- band): "
               "the low end with the sensor high for the winding current, the high end with the sensor low for T/W",
               basis="the maker publishes no tolerance (SRC-E1-X3108S-DATA-111: 86 mOhm, tolerance -); +10 % also covers a "
                     "winding 26 K above 25 degC at a fresh-pack full-throttle event (0.393 %/K). T-E1-MOTOR-RM (4-wire, "
                     "corrected to 25 degC) accepts a motor only inside 77.4-94.6 mOhm; the limiter band at 73.2 A "
                     "(CL-E1-ILIM-RM-LO / -HI) is wider than this", value=0.10, unit="-", status="PROPOSED")


@kit.calc("CALC-E1-MASS-LIMIT", title="Largest take-off mass that keeps every E1 limit, over the R_m band (D-161)",
          equation="T_f = T(fresh, I_lim (1 - tol), R_m (1 + band), 25 degC) ; T_w = T(worst state, I_lim (1 - tol), "
                   "R_m (1 + band) at 80 degC) ; m_max = min(n T_f cos(cant) / (T/W_min g), n T_w cos(cant) / "
                   "(T/W_min,sag g)) ; I_wind = I_m(fresh, I_lim (1 + tol), R_m (1 - band), 25 degC) <= I_rating "
                   "(independent of mass: the limiter fixes the current) ; T/W(m) = n T cos(cant) / (m g) at 2.60, 2.65, "
                   "2.70 kg and at cant 10 deg (B3 spare mounts)",
          inputs={**WORST_IN, "r_ext": P + "electrical.r_ext_mohm", "tol": "ASM-E1-SENSOR-TOL",
                  "tw_min": P + "requirements.hover_tw_min", "tw_sag": P + "requirements.hover_tw_min_sag",
                  "i_rate": P + "propulsion.motor_max_a", "band": "ASM-E1-RM-BAND"},
          units={**WORST_UNITS, "r_ext": "mOhm", "i_rate": "A"},
          assumes=WORST_ASM + ["ASM-E1-SENSOR-TOL", "ASM-E1-RM-BAND"])
def mass_limit(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, cold,
               r_ext, tol, tw_min, tw_sag, i_rate, band):
    rx = r_ext / 1000.0
    fresh = (cells * 4.20, cells * r_cell + rx)
    worst = (cells * ocv20, cells * r_cell * cold + rx)

    def at(il, case, rmk):
        return limited(DESIGN, rho, kT, kP, kv, rmk, i0, esc, case[0], case[1], pack[1], n, il)
    f = at(ilim * (1 - tol), fresh, rm * (1 + band))
    w = at(ilim * (1 - tol), worst, r_hot(rm * (1 + band), tc[0], state[0]))
    hi = at(ilim * (1 + tol), fresh, rm * (1 - band))
    nom_f, nom_w = at(ilim, fresh, rm), at(ilim, worst, r_hot(rm, tc[0], state[0]))
    out = {"T_fresh_band_gf": f["T_N"] / g * 1000, "T_worst_band_gf": w["T_N"] / g * 1000,
           "I_wind_band_A": hi["I_m_A"], "I_bat_band_A": hi["I_bat_A"]}
    for c_deg, ctag in ((cant, ""), (10.0, "_c10")):
        cc = math.cos(math.radians(c_deg))
        mf = n * f["T_N"] * cc / (tw_min * g)
        mw = n * w["T_N"] * cc / (tw_sag * g)
        out[f"m_max_fresh_kg{ctag}"] = mf
        out[f"m_max_worst_kg{ctag}"] = mw
        out[f"m_max_kg{ctag}"] = min(mf, mw)
        for mm in (m, 2.60, 2.65, 2.70):
            t = f"{mm:.2f}".replace(".", "")
            out[f"tw_fresh_band_{t}{ctag}"] = n * f["T_N"] * cc / (mm * g)
            out[f"tw_worst_band_{t}{ctag}"] = n * w["T_N"] * cc / (mm * g)
        out[f"tw_fresh_nom_gate{ctag}"] = n * nom_f["T_N"] * cc / (m * g)
        out[f"tw_worst_nom_gate{ctag}"] = n * nom_w["T_N"] * cc / (m * g)
        out[f"tw_fresh_band_gate{ctag}"] = n * f["T_N"] * cc / (m * g)
        out[f"tw_worst_band_gate{ctag}"] = n * w["T_N"] * cc / (m * g)
    return out


@kit.calc("CALC-E1-SPIN-CAP", title="One-motor transient at the spin cap, and the gate the limiters allow (D-173b)",
          equation="one motor at duty = Q_M_SPIN_MAX, three at hover thrust or 0.3 x hover, fresh pack, R_m (1 - band), "
                   "25 degC: I_wind, I_esc ; four motors at min(cap, limiter): fresh T/W at I_lim (1 - tol), R_m (1 + band) "
                   "; worst state the same with 80 degC ; m_max = min(n T_f cos / (T/W_min g), n T_w cos / (T/W_sag g)) "
                   "at limiters 75, 80, 85 A (and the B3 1.75 entry: n T_w cos / (1.75 g))",
          inputs={**WORST_IN, "r_ext": P + "electrical.r_ext_mohm", "tol": "ASM-E1-SENSOR-TOL",
                  "tw_min": P + "requirements.hover_tw_min", "tw_sag": P + "requirements.hover_tw_min_sag",
                  "i_rate": P + "propulsion.motor_max_a", "i_esc": P + "propulsion.esc_cont_a", "band": "ASM-E1-RM-BAND",
                  "cap": "ASM-E1-SPIN-MAX", "kdl": P + "propulsion.download_factor",
                  "vfull": "ASM-E1-VCELL-FULL"},
          units={**WORST_UNITS, "r_ext": "mOhm", "i_rate": "A", "i_esc": "A"},
          assumes=WORST_ASM + ["ASM-E1-SENSOR-TOL", "ASM-E1-RM-BAND", "ASM-E1-SPIN-MAX", "ASM-E1-VCELL-FULL"])
def spin_cap(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, cold,
             r_ext, tol, tw_min, tw_sag, i_rate, i_esc, band, cap, kdl, vfull):
    rx = r_ext / 1000.0
    cc = math.cos(math.radians(cant))
    fresh = (cells * vfull, cells * r_cell + rx)
    worst = (cells * ocv20, cells * r_cell * cold + rx)
    low = (cells * state[1], cells * r_cell * cold + rx)
    Th = m * g * kdl / (n * cc)

    def capped(rmk, case, il):
        s = full_throttle(DESIGN, 0.0, rho, kT, kP, kv, rmk, i0, esc[0], esc[1], case[0], case[1], pack[1], n,
                          duty_max=cap)
        if n * s["I_bat_A"] + pack[1] <= il:
            return s
        return limited(DESIGN, rho, kT, kP, kv, rmk, i0, esc, case[0], case[1], pack[1], n, il)

    def single(rmk, others):
        v = fresh[0]
        for _ in range(80):
            h = at_thrust(DESIGN, others, 0.0, rho, kT, kP, kv, rmk, i0, esc[0], esc[1], v)
            r = bisect(lambda x: station(DESIGN, x, 0.0, rho, kT, kP, kv, rmk, i0, esc[0], esc[1], v)["duty"] - cap,
                       300.0, 25000.0)
            s1 = station(DESIGN, r, 0.0, rho, kT, kP, kv, rmk, i0, esc[0], esc[1], v)
            vn = fresh[0] - fresh[1] * (s1["I_bat_A"] + (n - 1) * h["I_bat_A"] + pack[1])
            if abs(vn - v) < 1e-6:
                break
            v = 0.5 * (v + vn)
        return s1
    rlo, rhi = rm * (1 - band), rm * (1 + band)
    a, b = single(rlo, Th), single(rlo, 0.3 * Th)
    out = {"I_wind_single_A": (1 + tol) * max(a["I_m_A"], b["I_m_A"]),   # +tol: current-sensor / model band
           "I_esc_single_A": (1 + tol) * max(a["I_bat_A"], b["I_bat_A"]),
           "rpm_single": max(a["rpm"], b["rpm"])}
    for il, t in ((ilim, "lim"), (75.0, "75"), (80.0, "80"), (85.0, "85")):
        f = capped(rhi, fresh, il * (1 - tol))
        w = capped(r_hot(rhi, tc[0], state[0]), worst, il * (1 - tol))
        lo = capped(r_hot(rhi, tc[0], state[0]), low, il * (1 - tol))
        hi = capped(rlo, fresh, il * (1 + tol))
        mf, mw, m175 = (n * f["T_N"] * cc / (tw_min * g), n * w["T_N"] * cc / (tw_sag * g),
                        n * w["T_N"] * cc / (1.75 * g))
        out.update({f"tw_fresh_{t}": n * f["T_N"] * cc / (m * g), f"tw_worst_{t}": n * w["T_N"] * cc / (m * g),
                    f"tw_low360_{t}": n * lo["T_N"] * cc / (m * g), f"I_wind_lim_{t}_A": hi["I_m_A"],
                    f"I_esc_lim_{t}_A": hi["I_bat_A"], f"m_max_{t}_kg": min(mf, mw), f"m_max_175_{t}_kg": min(mf, m175),
                    f"rpm_full_{t}": f["rpm"]})
    return out


@kit.calc("CALC-E1-SENS", title="Lower bound: pure PER3 power (kP = 1)",
          equation="as CALC-E1-HOVER and CALC-E1-CRUISE with kP = 1, kT = 1 (cruise T_m = D / (n cos cant))",
          inputs={"Th": "CL-E1-HOVER-T", "Tc": "CL-E1-CRUISE-DRAG", "V": P + "performance.cruise_ms",
                  "n": P + "propulsion.n_motors", "rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "cant": P + "propulsion.stations.cant_deg"},
          units={"Th": "N", "Tc": "N", "V": "m/s", "rho": "kg/m3", "cant": "deg"})
def sens(Th, Tc, V, n, rho, kv, rm, i0, esc, cant):
    Tc = Tc / math.cos(math.radians(cant))
    out = {}
    for prop, tag in (("11x4.5MR", "45"), (DESIGN, "55"), ("11x5.5MR", "55MR")):
        h = at_thrust(prop, Th, 0.0, rho, 1.0, 1.0, kv, r_hot(rm, 0.00393, 50.0), i0, esc[0], esc[1], 14.8)
        c = at_thrust(prop, Tc / n, V, rho, 1.0, 1.0, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
        out[f"P_hover_{tag}_W"] = n * h["P_bat_W"]
        out[f"P_cruise_{tag}_W"] = n * c["P_bat_W"]
    return out


@kit.calc("CALC-E1-HOVER-I-BAND", title="Hover-current pass line from R-ESC-CURRENT (d)",
          equation="I_max = I_hover (1 + tol)", inputs={"i": P + "performance.hover_current_a",
                                                         "tol": P + "requirements.hover_current_tol"},
          units={"i": "A"})
def hover_i_band(i, tol):
    return {"i_max_a": i * (1 + tol), "i_min_a": i * (1 - tol)}


# ================================================================== claims
kit.claim("CL-E1-KT-SF", "PER3 thrust factor kT fitted on the X3108S + APC 11x4.7SF rows (sensitivity since D-173)",
          calc="CALC-E1-CAL", output="kT", unit="-",
          how="Re-run; compare with T-E1-STAND rows (thrust vs rpm) for the fitted prop.")
kit.claim("CL-E1-KP-SF", "PER3 power factor kP fitted on the X3108S + APC 11x4.7SF rows (sensitivity since D-173)",
          calc="CALC-E1-CAL", output="kP", unit="-",
          how="Re-run; the rms power error on the fitted rows is printed (CALC-E1-CAL P_err_rms).")
kit.claim("CL-E1-KT", "PER3 thrust factor kT for the 11x8E (fit on the flight motor's 11x8 row, D-173)",
          calc="CALC-E1-CAL-11X8", output="kT", unit="-",
          note="design factor since D-173; the SF fit (CL-E1-KT-SF) is the sensitivity. motor_select_173.py took "
               "each claim at the worse of the two",
          how="T-E1-STAND: thrust vs rpm on the 11x8E.")
kit.claim("CL-E1-KP", "PER3 power factor kP for the 11x8E (fit on the flight motor's 11x8 row, D-173)",
          calc="CALC-E1-CAL-11X8", output="kP", unit="-",
          how="T-E1-STAND: phase current vs rpm on the 11x8E (torque = (I - I0) / Kt).")
kit.claim("CL-E1-CAL-PERR", "Model power error on the maker rows", calc="CALC-E1-CAL", output="P_err_max", unit="-",
          limit=("<=", 0.10), how="Max |P_model / P_maker - 1| over the 7 rows 5-12 A; re-run the script.")
kit.claim("CL-E1-MAKER-SUPPLY", "Maker's supply at the 30 A row (inferred)", calc="CALC-E1-CAL", output="v_supply_30A",
          unit="V", note="the maker's 1 580 gf top row is reachable only with ~11 V at the motor: the table's 447 W is "
          "14.8 V x 30 A bookkeeping, not a measurement at 14.8 V",
          how="Thrust stand at a held 14.8 V bench supply: full-throttle rpm should exceed 7 500 (T-E1-STAND).")
kit.claim("CL-E1-HOVER-T", "Hover thrust per motor at the gate", calc="CALC-E1-HOVER", output="T_per_motor_N", unit="N",
          parts=MOTORS, how="m_gate g k_download / (4 cos cant); compare with the tethered-hover throttle and log.")
kit.claim("CL-E1-HOVER-I-MAX", "Hover-current pass line, 27 A + 15 %", calc="CALC-E1-HOVER-I-BAND", output="i_max_a",
          unit="A", how="Arithmetic on performance.hover_current_a and requirements.hover_current_tol (A2 CR-A2-13).")
kit.claim("CL-E1-HOVER-I", "Hover pack current, 11x4.5MR (stand A/B prop, not flown)", calc="CALC-E1-HOVER",
          output="I_pack_45_A", unit="A", limit=("<=", "CL-E1-HOVER-I-MAX"), parts=MOTORS,
          note="information since D-05: no requirement link",
          how="Thrust stand with the 11x4.5MR at hover thrust (T-E1-STAND A/B).")
kit.claim("CL-E1-HOVER-I-55", "Hover pack current, 11x5.5E/EP, 14.8 V", calc="CALC-E1-HOVER", output="I_pack_55_A",
          unit="A", limit=("<=", "CL-E1-HOVER-I-MAX"), verifies=["R-ESC-CURRENT"], parts=MOTORS + ESCS,
          how="Log battery current in a 30 s tethered hover at 2.6 kg: within 27 A +/- 15 % (R-ESC-CURRENT d).")
kit.claim("CL-E1-HOVER-GW", "Hover efficiency, 11x5.5E/EP", calc="CALC-E1-HOVER", output="gW_55", unit="gf/W",
          parts=MOTORS, how="Thrust stand: gf / W at the hover thrust per motor (T-E1-STAND).")
kit.claim("CL-E1-HOVER-DT", "Hover winding temperature rise, 11x5.5E/EP", calc="CALC-E1-HOVER", output="dT_wind_55_K",
          unit="K", limit=("<=", 50.0), verifies=["R-THERMAL"], parts=MOTORS,
          how="IR thermometer on the can after a 2 min tethered hover; E3 owns the limit (80 degC can at 30 degC ambient).")
kit.claim("CL-E1-TW-TABLE", "Hover T/W at the gate, 11x5.5E/EP, bus held 14.8 V, no limiter", calc="CALC-E1-FULL",
          output="tw_table_55", unit="-", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"],
          parts=MOTORS, how="Thrust stand at a held 14.8 V: full-throttle thrust per motor x 4 / 2.6 kg (T-E1-STAND).")
kit.claim("CL-E1-IMAX-148", "Full-throttle current per motor at 14.8 V, 11x4.5MR, no limiter", calc="CALC-E1-FULL",
          output="I_148_45_A", unit="A", parts=MOTORS + ESCS,
          note="information only since R-ESC-CURRENT A2-R1: unlimited 14.8 V is not a requirement (CR-A2-13)",
          how="Thrust stand at a held 14.8 V, 3 s full throttle, clamp meter on the ESC lead.")
kit.claim("CL-E1-IMAX-168", "Unlimited burst per motor at 16.8 V, 11x4.5MR", calc="CALC-E1-FULL",
          output="I_168_45_A", unit="A", limit=("<=", P + "propulsion.esc_burst_a"), parts=MOTORS + ESCS,
          note="stand A/B prop, not flown: no requirement link",
          how="Thrust stand on a fresh pack (16.8 V), 2 s full throttle.")
kit.claim("CL-E1-IMAX-168-55", "Unlimited burst per motor at 16.8 V, 11x5.5E/EP", calc="CALC-E1-FULL",
          output="I_168_55_A", unit="A", limit=("<=", P + "propulsion.esc_burst_a"), verifies=["R-ESC-CURRENT"],
          parts=MOTORS + ESCS, how="Thrust stand on a fresh pack (16.8 V), 2 s full throttle, no limiter "
                                   "(R-ESC-CURRENT c: <= 55 A, ESC 10 s rating).")
kit.claim("CL-E1-IMAX-148-55", "Full-throttle current per motor at 14.8 V, 11x5.5E/EP, no limiter", calc="CALC-E1-FULL",
          output="I_148_55_A", unit="A", parts=MOTORS + ESCS,
          note="information only since R-ESC-CURRENT A2-R1 (CR-A2-13)", how="As CL-E1-IMAX-148 with the 11x5.5MR.")
kit.claim("CL-E1-IPACK-PEAK", "Peak pack current, four motors, no limiter, low pack, 11x5.5E/EP", calc="CALC-E1-FULL",
          output="Ipack_sag_55_A", unit="A", limit=("<=", P + "electrical.peak_current_a"), parts=ESCS,
          note="wiring and disconnect design case if the limiter is not set; the bus-held 16.8 V upper bound is "
               "Ipack_fresh_55_A in CALC-E1-FULL. With the limiter the pack current is CL-E1-IPACK-LIM",
          how="Log on the stand with four motors on a flight pack, limiter off, 2 s.")
kit.claim("CL-E1-IPACK-LIM", "Pack current, four motors full throttle, at the limiter, fresh pack", calc="CALC-E1-LIMIT",
          output="Ipack_fresh_55_A", unit="A", limit=("<=", P + "performance.full_throttle_current_a"),
          verifies=["R-ESC-CURRENT"], parts=ESCS,
          note="equals Q_M_BAT_CURR_MAX by construction: the claim states the model honours the limiter; the bench "
               "run (R-ESC-CURRENT a) is the evidence. F1's sensor error (+5 %) is in CL-F1-ILIM-WORST",
          how="Bench: all four motors, props on, fresh pack, full throttle 2 s in QSTABILIZE on a restrained frame; "
              "dataflash BAT.Curr <= Q_M_BAT_CURR_MAX (70 A, D-148).")
kit.claim("CL-E1-ILIM-I", "Motor winding current at the pack-current limiter, fresh pack, 11x5.5E/EP (model)",
          calc="CALC-E1-WORST", output="I_wind_fresh_A", unit="A", limit=("<=", P + "propulsion.motor_max_a"),
          verifies=["R-ESC-CURRENT"], parts=MOTORS,
          note="CDR-05 (CDR-AE-02, decision B7): re-stated on the WINDING (phase) current. Until 2026-11-13 this id "
               "held the battery-side share of the limiter (24.75 A, now CL-E1-ILIM-I-BAT), which is not what the "
               "maker's 25 A / 30 s rating limits. At the limiter the ESC runs at a duty of about 0.83 (CALC-E1-LIMIT "
               "duty_fresh_55), so the winding carries about I_bat / duty. Fresh case of CALC-E1-WORST (4.20 V/cell, "
               "E2's cell resistance: the case behind the fresh T/W of 2.5); CALC-E1-LIMIT's older fresh case reads "
               "0.5 A less (I_wind_fresh_55_A). Rev 9 (wave 2, D-148): read at performance.full_throttle_current_a "
               "70 A (was 30.0 A at 100 A, FAIL). Holds only with the sensor inside ASM-E1-SENSOR-TOL "
               "(T-F1-SENSOR-CAL): the high side of that band is CL-E1-ILIM-I-SENS-HI. Second bound: "
               "CL-E1-ILIM-I-B2; the 93 A second-bound value is CALC-E1-ILIM-COND (information)",
          how="T-E1-STAND / GT-04: phase current with a clamp on one motor lead (true-RMS, or the ESC's phase-current "
              "telemetry) during the limiter run (70 A), with bell temperature; not the ESC input lead.")
kit.claim("CL-E1-ILIM-I-BAT", "Battery-side current per ESC at the limiter, fresh pack, 11x5.5E/EP",
          calc="CALC-E1-LIMIT", output="I_motor_fresh_55_A", unit="A", parts=ESCS,
          note="(limiter - 1 A avionics) / 4: what the ESC input lead, the XT30U and E3's bus-power input see. This "
               "is the number CL-E1-ILIM-I carried before CDR-05; it is not compared with the motor rating",
          how="Same bench run as CL-E1-IPACK-LIM; clamp meter on one ESC input lead.")
kit.claim("CL-E1-ILIM-I-WORST", "Motor winding current at the limiter, worst pack state, hot winding (model)",
          calc="CALC-E1-WORST", output="I_wind_worst_A", unit="A", limit=("<=", P + "propulsion.motor_max_a"),
          parts=MOTORS, note="20 % charge, 10 degC pack, 80 degC winding: the duty is close to 1, so the winding "
                             "current is close to the battery share; information beside CL-E1-ILIM-I",
          how="As CL-E1-ILIM-I on the worst-state pack of T-E1-STAND.")
kit.claim("CL-E1-R-EFF-MAKER", "Series resistance that puts the maker's 30 A row at 14.8 V (second bound)",
          calc="CALC-E1-CAL", output="r_eff_30A_ohm", unit="ohm", assumes=["ASM-E1-BOUND2"],
          note="first bound: R_m + R_esc = 0.096 ohm at 25 degC and the supply sagged to CL-E1-MAKER-SUPPLY; second "
               "bound: this value at a true 14.8 V. CALC-E1-CAL hi_rows lists every row above 12 A: [A, rpm, "
               "thrust error, power error, model winding A, supply needed V, R_eff ohm]",
          how="T-E1-STAND at a held, logged 14.8 V: full-throttle rpm 7 500 (this bound) or above 9 000 (first bound).")
kit.claim("CL-E1-CAL-TERR-HI", "Model thrust error on the maker's rows above 12 A (at the measured rpm)",
          calc="CALC-E1-CAL", output="T_err_hi_max", unit="-", limit=("<=", 0.05),
          note="the prop model holds on the 7 rows that were not fitted; what the two bounds dispute is the rpm "
               "reached at a given bus voltage, not thrust at a given rpm",
          how="Max |T_model / T_maker - 1| over the 7 rows 14-30 A; re-run the script.")
kit.claim("CL-E1-ILIM-I-B2", "Motor winding current at the limiter, fresh pack, second bound (information)",
          calc="CALC-E1-BOUND2", output="I_wind_fresh_A", unit="A",
          parts=MOTORS, note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "On the maker-row reading the limiter binds at a duty near 1, so the winding current is "
                             "close to the battery share: the two bounds bracket the phase current the stand will read",
          how="As CL-E1-ILIM-I.")
kit.claim("CL-E1-ILIM-FOR-25A", "Pack-current limit that holds 25 A in the winding, fresh pack (model)",
          calc="CALC-E1-ILIM-25", output="ilim_a", unit="A", parts=MOTORS,
          note="option (b) of CDR-AE-02 / decision B7: Q_M_BAT_CURR_MAX at about this value if the 30 s stand run "
               "at 100 A takes the bell above 80 degC. Applied by D-148 (70 A, inside this edge); F4 owns the "
               "parameter. Independent of the cant (winding current is set by axial thrust)",
          how="Stand: lower the limiter until the phase-current clamp reads 25 A on a fresh pack.")
kit.claim("CL-E1-ILIM-25A-TW", "Fresh-pack T/W with the winding held to 25 A (model)", calc="CALC-E1-ILIM-25",
          output="tw", unit="-", limit=(">=", P + "requirements.hover_tw_min"), parts=MOTORS,
          note="what the lower limiter of CL-E1-ILIM-FOR-25A leaves; cant included",
          how="Thrust stand at the limiter value of CL-E1-ILIM-FOR-25A.")
kit.claim("CL-E1-ILIM-TW-FRESH", "Axial thrust / weight with the limiter, fresh pack, 11x5.5E/EP (thrust basis)",
          calc="CALC-E1-LIMIT",
          output="tw_fresh_55", unit="-", limit=(">=", P + "requirements.hover_tw_min"), parts=MOTORS,
          note="rev 9 (wave 2): 4 T / W along the motor axes, NO cant term, because it is the thrust basis of "
               "performance.thrust_max_per_motor_kg (C1 loads, H1 stand lines). The R-HOVER-TW check with the "
               "cos(cant) loss is CL-E1-TW-FRESH; the verifies link moved there",
          how="Thrust stand on a fresh pack with the duty limit found on the bench.")
kit.claim("CL-E1-TW-FRESH", "Hover T/W at the gate, fresh pack, limiter, first bound, cant included",
          calc="CALC-E1-WORST", output="tw_fresh", unit="-", limit=(">=", P + "requirements.hover_tw_min"),
          verifies=["R-HOVER-TW"], parts=MOTORS,
          note="rev 9 (wave 2, D-146 / D-148): fresh case of CALC-E1-WORST (4.20 V/cell, E2 cell resistance, 25 degC "
               "winding) at performance.full_throttle_current_a, 4 T cos(cant) / (m_gate g). Sensor low side: "
               "CL-E1-TW-FRESH-SENS-LO",
          how="T-E1-STAND on a fresh pack at the limiter: thrust x 4 x cos(cant) / 2.6 kg.")
kit.claim("CL-E1-ILIM-I-SENS-HI", "Winding current if the true pack current is the limiter + sensor tolerance",
          calc="CALC-E1-ILIM-COND", output="I_wind_sens_hi_A", unit="A", limit=("<=", P + "propulsion.motor_max_a"),
          verifies=["R-ESC-CURRENT"], parts=MOTORS, assumes=["ASM-E1-SENSOR-TOL"],
          note="D-148 condition: limiter x (1 + ASM-E1-SENSOR-TOL), first bound, fresh. The 25 A edge in true pack "
               "current is CALC-E1-ILIM-COND ilim_hi_a (= CL-E1-ILIM-FOR-25A)",
          how="T-F1-SENSOR-CAL (sensor error at 70-75 A) and T-E1-STAND phase current at the limiter.")
kit.claim("CL-E1-TW-FRESH-SENS-LO", "Fresh T/W if the true pack current is the limiter - sensor tolerance",
          calc="CALC-E1-ILIM-COND", output="tw_fresh_sens_lo", unit="-", limit=(">=", P + "requirements.hover_tw_min"),
          verifies=["R-HOVER-TW"], parts=MOTORS, assumes=["ASM-E1-SENSOR-TOL"],
          note="D-148 condition, low side: limiter x (1 - ASM-E1-SENSOR-TOL), first bound, fresh, cant included. "
               "The T/W 2.0 edge in true pack current is CALC-E1-ILIM-COND ilim_lo_a; it rises about 0.3 A per "
               "degree of cant (E1.md 3.1), so the 9 deg window is narrower on this side than at 7 deg",
          how="T-F1-SENSOR-CAL and T-E1-STAND thrust at the limiter.")
kit.claim("CL-E1-ILIM-TOL-OK", "Sensor error the limiter value tolerates (first bound, both edges)",
          calc="CALC-E1-ILIM-COND", output="tol_ok", unit="-", limit=(">=", "ASM-E1-SENSOR-TOL"), parts=MOTORS,
          assumes=["ASM-E1-SENSOR-TOL"],
          note="min(ilim_hi / limiter - 1, 1 - ilim_lo / limiter). The window centre and its half-width are "
               "CALC-E1-ILIM-COND ilim_centre_a, tol_centre",
          how="Arithmetic on CALC-E1-ILIM-COND; T-F1-SENSOR-CAL must show the reading inside this band.")
kit.claim("CL-E1-TW-FRESH-B2-93A", "Fresh T/W, second bound, at the 93 A second-bound limiter (information)",
          calc="CALC-E1-ILIM-COND", output="tw_fresh_b2_ib2", unit="-", parts=MOTORS,
          assumes=["ASM-E1-ILIM-B2", "ASM-E1-BOUND2"],
          note="information row (D-148): what CL-E1-TW-FRESH-B2 becomes if T-E1-STAND reads the second bound and "
               "F4 sets 93 A. Same case: worst T/W tw_worst_b2_ib2, winding I_wind_fresh_b2_ib2_A; on the first "
               "bound 93 A gives I_wind_fresh_b1_ib2_A (fails 25 A), which is why 93 A follows the stand only",
          how="T-E1-STAND picks the bound; then the stand run at 93 A.")
kit.claim("CL-E1-CRUISE-DRAG", "Cruise drag at performance.cruise_ms (17 m/s, D-145), gate mass (B1 polar)", calc="CALC-E1-CRUISE", output="drag_N",
          unit="N", note="rev 8: B1's as-designed polar (CL-B1V-CD0 / -K, D-67); equals CALC-B1V-CRUISE drag_gate_n "
                         "4.51 N. Rev 2-7 on the hand polar (CL-B1-CRUISE-DRAG); was W / 5.6 from params",
          how="B1 owns the polar; cruise power test with known prop data (H2).")
kit.claim("CL-E1-CRUISE-LD-EFF", "Effective cruise L/D (W / trimmed drag)", calc="CALC-E1-CRUISE", output="ld_eff",
          unit="-", note="rev 9 (wave 2, D-145): at performance.cruise_ms 17 m/s; A1 copies it to "
                         "performance.ld_cruise (replaces B1's 5.19 if different). Rev 8 (D-67): on B1's as-designed polar CL-B1V-CD0 0.0579 / CL-B1V-K 0.0957 with the 2 % "
                         "trim, at the 2.6 kg gate (B1's 5.57 is at the 2.436 kg predicted mass). A1 copies it to "
                         "performance.ld_cruise. Was 6.2 on the hand polar (CL-B1-CD0 0.0515)",
          how="T-B1-CRUISE-POWER legs at 17 m/s: W / (eta_tot P_pack / V) from logged power, rpm and airspeed.")
kit.claim("CL-E1-CRUISE-P-45", "Cruise electrical power, 11x4.5MR (stand A/B prop, not flown)", calc="CALC-E1-CRUISE",
          output="P_total_45_W", unit="W", parts=MOTORS, note="comparison only since D-05; no requirement link",
          how="Log pack power in steady 15 m/s FBWA legs, both directions, calm morning.")
kit.claim("CL-E1-CRUISE-P-55", "Cruise electrical power, 11x5.5E/EP", calc="CALC-E1-CRUISE", output="P_total_55_W",
          unit="W", limit=("<=", P + "performance.cruise_power_w"), verifies=["R-MISSION"], parts=MOTORS + ESCS,
          note="propulsion only (no avionics); drag from B1's as-designed polar (CL-B1V-CD0, CL-B1V-K, ASM-B1-TRIM; "
               "rev 8, D-67; was CL-B1-CD0 / CL-B1-K), CR-A1-32. p_check = (this + 6 W) / CL-B1V-CRUISE-P-GATE. "
               "The params limit is B1's pack power incl. 6 W avionics, so the comparison is 6 W conservative for B1. "
               "Rev 8 FAIL: 246.0 W > 240 (E1 + 6 W avionics = 252.0 W, p_check 1.055 against B1's 238.9 W at the "
               "gate): same drag (4.51 N), E1's eta_tot 0.293 from APC PER3 with kP 1.24 vs B1's chain. Band "
               "200.2 (kP 1) - 246.0 W. D-13 carries the conservative one: CR-E1-51 asks A1 for cruise_power_w 252 "
               "(E2 re-runs) or cruise_ms 15 (213.9 + 6 = 220 W, 1.25 Vs at the gate). Rev 9 (wave 2, D-145 / "
               "D-146): at 17 m/s with T_m = D / (4 cos 9 deg); same point as CL-E1-CRUISE-P-55-V17",
          how="Log pack power in steady 17 m/s FBWA legs, both directions, calm morning; subtract the avionics draw.")
kit.claim("CL-E1-CRUISE-P-55-LO", "Cruise power lower bound (kP = 1), 11x5.5E/EP", calc="CALC-E1-SENS",
          output="P_cruise_55_W", unit="W", how="Bounds the band with CL-E1-CRUISE-P-55; flight log decides.")
kit.claim("CL-E1-CRUISE-P-45-LO", "Cruise power lower bound (kP = 1), 11x4.5MR", calc="CALC-E1-SENS",
          output="P_cruise_45_W", unit="W", how="Bounds the band with CL-E1-CRUISE-P-45; flight log decides.")
kit.claim("CL-E1-CRUISE-ETA-45", "Cruise prop efficiency, 11x4.5MR", calc="CALC-E1-CRUISE", output="eta_prop_45",
          unit="-", how="PER3 at J of the cruise point; check with logged rpm (bidirectional DShot) and power.")
kit.claim("CL-E1-CRUISE-ETA-55", "Cruise prop efficiency, 11x5.5E/EP", calc="CALC-E1-CRUISE", output="eta_prop_55",
          unit="-", how="As CL-E1-CRUISE-ETA-45.")
kit.claim("CL-E1-CORRIDOR-45", "Transition thrust margin, 11x4.5MR", calc="CALC-E1-CORRIDOR", output="margin_45",
          unit="-", limit=(">=", "ASM-E1-TRANS-MARGIN"), verifies=["R-TRANSITION"], parts=MOTORS,
          how="B1 replaces the wing model with AVL/XFOIL post-stall data; flight log of throttle during the first transition.")
kit.claim("CL-E1-CORRIDOR-55", "Transition thrust margin, 11x5.5E/EP", calc="CALC-E1-CORRIDOR", output="margin_55",
          unit="-", limit=(">=", "ASM-E1-TRANS-MARGIN"), verifies=["R-TRANSITION"], parts=MOTORS,
          how="As CL-E1-CORRIDOR-45.")
kit.claim("CL-E1-MOTOROUT-TW", "Hover T/W left on one diagonal pair", calc="CALC-E1-MOTOR-OUT", output="tw_two_motors",
          unit="-", parts=MOTORS, note="lift is there, yaw is not: both remaining props turn the same way",
          how="SITL motor-failure injection (F4); no flight test.")
kit.claim("CL-E1-HOVER-YAW", "Hover yaw moment from +/-30 % thrust differential", calc="CALC-E1-MOTOR-OUT",
          output="yaw_diff30_Nm", unit="N*m", parts=MOTORS,
          how="B3 uses it for R-HOVER-AUTHORITY (yaw); thrust stand torque arm or a yaw-step in tethered hover.")
kit.claim("CL-E1-MOTOROUT-ROLL", "Cruise roll torque, one motor out", calc="CALC-E1-MOTOR-OUT",
          output="roll_torque_cruise_Nm", unit="N*m", parts=MOTORS,
          how="B3 compares with elevon roll authority at 16 m/s (CR-E1-04).")

kit.claim("CL-E1-TW-WORST", "Hover T/W at the gate, worst pack state (one team claim, E1 + E2)", calc="CALC-E1-WORST",
          output="tw_worst", unit="-", limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"],
          parts=MOTORS, note="replaces CL-E1-TW-SAG, CL-E1-TW-SAG-55, CL-E1-ILIM-TW-LOW and, by agreement requested "
          "in CR-E1-15, CL-E2-TW-SAG-WORST: 11x5.5MR, 20 % charge, 10 degC pack, 80 degC winding, limiter "
          "performance.full_throttle_current_a (70 A since D-148; 100 A before), cos(cant) at 9 deg (D-146)",
          how="Thrust stand on a flight pack discharged to 3.73 V/cell rest and cold-soaked to 10 degC, motor warmed by "
              "a 2 min run at hover thrust, full throttle with the 25 A per-motor duty cap: thrust x 4 x cos(cant) / "
              "2.6 kg (T-E1-STAND).")
kit.claim("CL-E1-SAG-FACTOR", "Thrust factor worst / fresh with the limiter (replaces params voltage_sag)",
          calc="CALC-E1-WORST", output="f_sag", unit="-",
          note="CDR-05 (2026-11-13): on r_ext 7.9 mOhm (F1's routed leads, CL-F1-R-EXT 7.92); was 0.8508 at 6.7 "
               "(D-67) and 0.851 at 6.5 (the limiter holds 100 A in both states, so 1 mOhm moves V_bus by 0.1 V). "
               "To be applied to thrust_max_per_motor_kg (fresh pack, limiter); E2's 0.76 applied (V/14.8)^2 to "
               "that already current-limited thrust, which double-counts. Bounded above by CL-E1-SAG-XCHECK",
          how="Ratio of the two T-E1-STAND full-throttle runs: worst-state pack / fresh pack.")
kit.claim("CL-E1-SAG-XCHECK", "Sag factor, closed form (limiter, T ~ P^2/3)", calc="CALC-E1-WORST",
          output="f_sag_closed_form", unit="-",
          note="independent of the prop tables and the motor model: same pack current in both states, so P ~ V_bus "
               "and T ~ P^(2/3) for a static prop; ignores the hot winding, so it sits just above CL-E1-SAG-FACTOR",
          how="Hand calculation from the E2 pack assumptions and F1's r_ext; the T-E1-STAND ratio settles both.")
kit.claim("CL-E1-TMAX-WORST", "Full thrust per motor, worst pack state, 11x5.5E/EP", calc="CALC-E1-WORST",
          output="T_worst_gf", unit="gf", parts=MOTORS, how="As CL-E1-TW-WORST, per motor.")
kit.claim("CL-E1-TW-LAND-COLD", "Hover T/W below the reserve line (3.60 V/cell, cold), sensitivity",
          calc="CALC-E1-WORST", output="tw_land_cold", unit="-", limit=(">=", 1.3), parts=MOTORS,
          how="Same stand run on a pack at 3.60 V/cell rest; 1.3 is the emergency-landing floor, not R-HOVER-TW.")
kit.claim("CL-E1-TW-WORST-B2", "Hover T/W at the gate, worst pack state, second bound (information, rejected reading)",
          calc="CALC-E1-BOUND2", output="tw_worst", unit="-",
          parts=MOTORS, assumes=["ASM-E1-BOUND2"],
          note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "Was: CDR-05 (CDR-AE-01), the same case as CL-E1-TW-WORST with the series resistance "
               "CL-E1-R-EFF-MAKER, limit requirements.hover_tw_min_sag, verified R-HOVER-TW. R-HOVER-TW is verified "
               "by CL-E1-TW-WORST and CL-E1-TW-FRESH(-SENS-LO) on the physical station",
          how="T-E1-STAND at a logged 11.9 V bus: >= 1 060 gf per motor (CDR condition B-7).")
kit.claim("CL-E1-TW-FRESH-B2", "Hover T/W at the gate, fresh pack, limiter, second bound (information, rejected reading)",
          calc="CALC-E1-BOUND2", output="tw_fresh", unit="-",
          parts=MOTORS, assumes=["ASM-E1-BOUND2"],
          note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "Was (limit requirements.hover_tw_min, verified R-HOVER-TW): rev 9 (D-148): at the 70 A first-bound limiter this bound fails; it passes only with the 93 A "
               "value that D-148 sets if the stand reads this bound (CL-E1-TW-FRESH-B2-93A)",
          how="T-E1-STAND on a fresh pack at the limiter: >= 1 330 gf per motor (CDR condition B-7).")
kit.claim("CL-E1-TMAX-WORST-B2", "Full thrust per motor, worst pack state, second bound", calc="CALC-E1-BOUND2",
          output="T_worst_gf", unit="gf", parts=MOTORS, how="As CL-E1-TW-WORST-B2, per motor.")
kit.claim("CL-E1-TW-WORST-B2-PROP", "Worst-state T/W if full-throttle rpm goes with bus voltage (information, rejected reading)",
          calc="CALC-E1-BOUND2", output="tw_worst_prop", unit="-",
          parts=MOTORS, assumes=["ASM-E1-BOUND2"],
          note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "The rule CDR-AE-01 used: rpm = rpm(14.8 V) x V_bus / 14.8, with no credit for the smaller resistive "
               "drop at the lower current. Here the bus is solved with the pack model at the current this rpm "
               "draws (CALC-E1-BOUND2 Vbus_worst_prop_V, above 11.9 V because the limiter does not bind), and the "
               "reference rpm is this prop's own (rpm_ref_148). The reviewer's 1.44 (REVIEWER EST) held the bus at "
               "11.9 V and took 7 500 rpm + 3 %: that case is CL-E1-T-STAND-B2-PROP",
          how="T-E1-STAND on the worst-state flight pack.")
kit.claim("CL-E1-T-NEED-SAG", "Thrust per motor that gives the worst-state T/W of R-HOVER-TW", calc="CALC-E1-BOUND2",
          output="T_need_sag_gf", unit="gf", parts=MOTORS,
          note="requirements.hover_tw_min_sag x gate mass / (4 cos cant). The board's stand line is 1 060 gf "
               "(CDR condition B-7), 1 % above this",
          how="Arithmetic.")
kit.claim("CL-E1-T-STAND-B2", "Full thrust per motor at a held 11.9 V bus, second bound (information, rejected reading)",
          calc="CALC-E1-BOUND2", output="T_stand_gf", unit="gf", parts=MOTORS, assumes=["ASM-E1-BOUND2"],
          note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "Was limit >= CL-E1-T-NEED-SAG; the stand point with that limit is now CL-E1-T-STAND (first bound). The stand point of CDR condition B-7 predicted on the maker-row reading with a fixed series "
               "resistance; the first bound predicts CALC-E1-BOUND2 T_stand_first_gf",
          how="T-E1-STAND: full throttle, bench supply held at 11.9 V at the ESC pads, bus voltage logged.")
kit.claim("CL-E1-T-STAND-B2-PROP", "Full thrust per motor at a held 11.9 V bus if rpm goes with bus voltage (information, rejected reading)",
          calc="CALC-E1-BOUND2", output="T_stand_prop_gf", unit="gf", parts=MOTORS,
          assumes=["ASM-E1-BOUND2"],
          note="RE-CLASSED to information (closure round 2026-11-14, rev 10): the second bound is a rejected reading of the maker table (ASM-E1-BOUND2, CALC-E1-BOUND2-CHECK: CL-E1-B2-MISS-111, CL-E1-R-UB-SPREAD, CL-E1-RM-NEEDED-MIN). No limit, no requirement. " "Was limit >= CL-E1-T-NEED-SAG. CDR-AE-01's own case (REVIEWER EST 946 gf, T/W 1.44, from 7 500 rpm x 11.9 / 14.8 + 3 %); here the "
               "reference is this prop's full-throttle rpm on R_eff at 14.8 V (rpm_ref_148). The most pessimistic "
               "reading of the maker's table that E1 could build; rev 10: the maker's own 11.1 V full-throttle rows "
               "rule it out (CALC-E1-BOUND2-CHECK), so it is no longer a stand pass line",
          how="T-E1-STAND as CL-E1-T-STAND (confirmation only).")
kit.claim("CL-E1-T-STAND", "Full thrust per motor at a held 11.9 V bus, physical station (first bound)",
          calc="CALC-E1-BOUND2", output="T_stand_first_gf", unit="gf", limit=(">=", "CL-E1-T-NEED-SAG"), parts=MOTORS,
          note="rev 10 (closure round): the CDR condition B-7 stand point on the station model that the maker's data "
               "support (winding 80 degC, the limiter, bus held at ASM-E1-V-STAND-LOW). The board's line is "
               "1 060 gf; the requirement line is CL-E1-T-NEED-SAG. Replaces CL-E1-T-STAND-B2 as the pass line",
          how="T-E1-STAND: full throttle, bench supply held at 11.9 V at the ESC pads, bus voltage logged (confirmation).")
kit.claim("CL-E1-B2-MISS-111", "Second bound vs the maker's 11.1 V full-throttle row, 11x4.7: thrust it fails to reach",
          calc="CALC-E1-BOUND2-CHECK", output="b2_miss_111", unit="-", limit=(">=", 0.05),
          assumes=["ASM-E1-BOUND2"],
          note="1 - T(second bound, held 11.1 V, full throttle) / 1 250 gf (maker, SRC-E1-X3108S-DATA-111). The limit "
               "0.05 is the prop model's own tolerance on the maker rows (CL-E1-CAL-TERR-HI <= 0.05): a miss larger "
               "than that is the station model failing, not the prop. PASS means the second bound is falsified by "
               "the maker's published data (b2_111_rpm, b2_111_gf against maker_111_rpm, maker_111_gf)",
          how="Re-run the script; the inputs are the maker's published rows.")
kit.claim("CL-E1-R-UB-SPREAD", "Held-voltage reading: largest / smallest station resistance over the 5 full-throttle rows",
          calc="CALC-E1-BOUND2-CHECK", output="r_ub_spread", unit="-",
          note="information: a fixed station has one resistance (ratio 1). Rows: CALC-E1-BOUND2-CHECK r_ub_rows "
               "[prop code (10.038 = 10x3.8), V label, A, rpm, R_ub ohm, degC, R_m multiple]. Read with the supply sagging (first bound) the "
               "rows need no common resistance, only a supply at or below the label (CL-E1-B1-SUPPLY-111)",
          how="Arithmetic on the maker's rows.")
kit.claim("CL-E1-R-UB-MIN", "Largest station resistance any held-voltage reading of the maker rows allows",
          calc="CALC-E1-BOUND2-CHECK", output="r_ub_min_ohm", unit="ohm",
          note="information: the 10x3.8 11.1 V full-throttle row (18 A, 7 457 rpm) bounds it model-free. Compare "
               "CL-E1-R-EFF-MAKER (the second bound) and R_m + R_esc = 0.096 ohm (first bound, 25 degC)",
          how="Arithmetic on the maker's rows.")
kit.claim("CL-E1-RM-NEEDED-MIN", "Least winding resistance a held-voltage reading needs, x the maker's stated 86 mOhm",
          calc="CALC-E1-BOUND2-CHECK", output="rm_needed_min", unit="-",
          note="information: (CL-E1-R-UB-MIN - R_esc) / R_m at that row's full-throttle temperature. Any second "
               "bound puts at least this multiple of the maker-stated winding resistance (SRC-E1-X3108S-DATA-111) "
               "in the motor; T-E1-MOTOR-RM (4-wire, on arrival) confirms R_m",
          how="T-E1-MOTOR-RM on arrival (confirmation).")
kit.claim("CL-E1-RM-NEEDED-B2", "Winding resistance the second bound needs, x the maker's stated 86 mOhm (at 94 degC)",
          calc="CALC-E1-BOUND2-CHECK", output="rm_needed_b2", unit="-", assumes=["ASM-E1-BOUND2"],
          note="information: (CL-E1-R-EFF-MAKER - R_esc) / R_m(94 degC)", how="Arithmetic.")
kit.claim("CL-E1-B1-SUPPLY-111", "First bound: supply the maker's 11.1 V 11x4.7 full-throttle row needs at duty 1",
          calc="CALC-E1-BOUND2-CHECK", output="b1_supply_111_V", unit="V", limit=("<=", 11.1),
          note="the physical station (R_m 86 mOhm at 62 degC + ESC) reaches the measured 6 600 rpm with a supply at or "
               "below the 3S label, i.e. a loaded 3S pack: the first bound is consistent with the row. Its thrust "
               "at that rpm is within b1_T_err_111 of the maker's 1 250 gf",
          how="Arithmetic on the maker's row; T-E1-STAND at a held bus confirms.")
kit.claim("CL-E1-ILIM-RM-LO", "Lowest winding resistance the limiter and sensor band accept (fresh, 25 A edge)",
          calc="CALC-E1-ILIM-COND", output="rm_ok_lo_mohm", unit="mOhm", parts=MOTORS,
          note="information (rev 10): below this the winding exceeds 25 A at limiter x (1 + tol), fresh pack. "
               "The window moves about 0.18 A per mOhm of R_m",
          how="T-E1-MOTOR-RM on arrival.")
kit.claim("CL-E1-ILIM-RM-HI", "Highest winding resistance the limiter and sensor band accept (fresh, T/W 2.0 edge)",
          calc="CALC-E1-ILIM-COND", output="rm_ok_hi_mohm", unit="mOhm", parts=MOTORS,
          note="information (rev 10): above this the fresh T/W falls under 2.0 at limiter x (1 - tol). The band is "
               "narrower than a milliohm measurement of R_m resolves; review/CLOSURE-ROUND-2026-11-14/E1.md section 4",
          how="T-E1-MOTOR-RM on arrival.")
kit.claim("CL-E1-MTOW-TW-MAX", "Largest take-off mass at which every E1 T/W limit passes over the R_m band",
          calc="CALC-E1-MASS-LIMIT", output="m_max_kg", unit="kg", limit=(">=", P + "requirements.mtow_gate_kg"),
          parts=MOTORS, note="D-161: 11x5.5E/EP at the limiter, sensor at its low edge, R_m +10 % (ASM-E1-RM-BAND), "
                             "cant 9 deg. The fresh T/W 2.0 edge (m_max_fresh_kg) and the worst-state 1.6 edge "
                             "(m_max_worst_kg) are both outputs; at 10 deg cant: m_max_kg_c10",
          how="T-E1-STAND fresh and worst-state runs at the limiter; thrust x 4 cos(cant) / (T/W g).")
kit.claim("CL-E1-TW-FRESH-RBAND", "Fresh T/W at the gate, limiter - sensor tol, R_m +10 % (D-161)",
          calc="CALC-E1-MASS-LIMIT", output="tw_fresh_band_gate", unit="-", limit=(">=", P + "requirements.hover_tw_min"),
          verifies=["R-HOVER-TW"], parts=MOTORS, assumes=["ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"],
          how="T-E1-STAND on a fresh pack at the limiter.")
kit.claim("CL-E1-TW-WORST-RBAND", "Worst-state T/W at the gate, limiter - sensor tol, R_m +10 % hot (D-161)",
          calc="CALC-E1-MASS-LIMIT", output="tw_worst_band_gate", unit="-",
          limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"], parts=MOTORS,
          assumes=["ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"], how="As CL-E1-TW-WORST.")
kit.claim("CL-E1-ILIM-I-RBAND", "Winding current at limiter + sensor tol, fresh, R_m -10 % (D-161)",
          calc="CALC-E1-MASS-LIMIT", output="I_wind_band_A", unit="A", limit=("<=", P + "propulsion.motor_max_a"),
          verifies=["R-ESC-CURRENT"], parts=MOTORS, assumes=["ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"],
          how="T-E1-STAND / GT-04 phase current at the limiter.")
kit.claim("CL-E1-TW-FRESH-C10", "Fresh T/W at the gate with the 10 deg spare mounts, nominal R_m (information)",
          calc="CALC-E1-MASS-LIMIT", output="tw_fresh_nom_gate_c10", unit="-", parts=MOTORS,
          note="B3 found 1.995 on the MR at 10 deg; the band case is tw_fresh_band_gate_c10",
          how="As CL-E1-TW-FRESH with the 10 deg mount.")
kit.claim("CL-E1-TW-FRESH-RBAND-C10", "Fresh T/W at the gate with the 10 deg spare mounts, band edge",
          calc="CALC-E1-MASS-LIMIT", output="tw_fresh_band_gate_c10", unit="-",
          limit=(">=", P + "requirements.hover_tw_min"), parts=MOTORS, assumes=["ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"],
          how="As CL-E1-TW-FRESH-RBAND with the 10 deg mount.")
kit.claim("CL-E1-TW-WORST-RBAND-C10", "Worst-state T/W at the gate with the 10 deg spare mounts, band edge",
          calc="CALC-E1-MASS-LIMIT", output="tw_worst_band_gate_c10", unit="-",
          limit=(">=", P + "requirements.hover_tw_min_sag"), parts=MOTORS,
          assumes=["ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"], how="As CL-E1-TW-WORST-RBAND with the 10 deg mount.")
kit.claim("CL-E1-SPIN-I-WIND", "Winding current, one motor at Q_M_SPIN_MAX, others light, fresh pack, R_m -10 %",
          calc="CALC-E1-SPIN-CAP", output="I_wind_single_A", unit="A", limit=("<=", P + "propulsion.motor_max_a"),
          verifies=["R-ESC-CURRENT"], parts=MOTORS, assumes=["ASM-E1-SPIN-MAX", "ASM-E1-RM-BAND"],
          how="T-E1-STAND: one station at the cap on a fresh 17.4 V pack, phase current.")
kit.claim("CL-E1-SPIN-I-ESC", "ESC (battery-side) current, one motor at Q_M_SPIN_MAX, others light, fresh pack",
          calc="CALC-E1-SPIN-CAP", output="I_esc_single_A", unit="A", limit=("<=", P + "propulsion.esc_cont_a"),
          verifies=["R-ESC-CURRENT"], parts=MOTORS + ESCS, assumes=["ASM-E1-SPIN-MAX", "ASM-E1-RM-BAND"],
          how="As CL-E1-SPIN-I-WIND, ESC input current.")
kit.claim("CL-E1-TW-FRESH-CAP", "Fresh T/W at the gate with the spin cap and limiter - tol, R_m +10 %",
          calc="CALC-E1-SPIN-CAP", output="tw_fresh_lim", unit="-", limit=(">=", P + "requirements.hover_tw_min"),
          verifies=["R-HOVER-TW"], parts=MOTORS, assumes=["ASM-E1-SPIN-MAX", "ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"],
          how="T-E1-STAND fresh-pack run at the limiter with the cap set.")
kit.claim("CL-E1-TW-WORST-CAP", "Worst-state T/W at the gate with the spin cap and limiter - tol, R_m +10 % hot",
          calc="CALC-E1-SPIN-CAP", output="tw_worst_lim", unit="-", limit=(">=", 1.75), verifies=["R-HOVER-TW"],
          parts=MOTORS, assumes=["ASM-E1-SPIN-MAX", "ASM-E1-RM-BAND", "ASM-E1-SENSOR-TOL"],
          note="limit 1.75 = B3's sagged transition entry (D-149 / A2 2.3), above R-HOVER-TW's 1.6",
          how="As CL-E1-TW-WORST with the cap set.")
kit.claim("CL-E1-MTOW-CAP-75", "Largest take-off mass, every E1 T/W limit, spin cap and the live pack-current limiter (id kept; was 75 A)",
          calc="CALC-E1-SPIN-CAP", output="m_max_lim_kg", unit="kg", limit=(">=", P + "requirements.mtow_gate_kg"),
          parts=MOTORS, how="From CL-E1-TW-FRESH-CAP / -WORST-CAP.")
kit.claim("CL-E1-REXT-ALLOW", "Largest pack-to-ESC path resistance that keeps R-HOVER-TW (model)",
          calc="CALC-E1-REXT-ALLOW", output="r_allow_mohm", unit="mOhm", limit=(">=", P + "electrical.r_ext_mohm"),
          parts=MOTORS,
          note="the smallest of four: worst state T/W = requirements.hover_tw_min_sag and fresh T/W = requirements."
               "hover_tw_min, each on the first bound (CALC-E1-WORST's cases) and on the second (CALC-E1-BOUND2's). "
               "Rev 10 (closure round): the second bound is information (ASM-E1-BOUND2 rejected), so the value is the first "
               "bound's (r_allow_first_mohm); the second bound's r_allow_b2_mohm stays visible. Rev 9 (wave 2, D-148): "
               "each bound at its own limiter (first 70 A, second 93 A, ASM-E1-ILIM-B2); at 70 A on the second "
               "bound the allowance is r_allow_b2_at_ilim_mohm (0: R-HOVER-TW already fails there, "
               "CL-E1-TW-FRESH-B2)",
          how="Re-run after T-E1-STAND; T-F1-DROP measures the path.")
kit.claim("CL-E1-DROP-ALLOW", "Largest voltage drop at the limiter current, pack to ESC, that keeps R-HOVER-TW (limit for F1)",
          calc="CALC-E1-REXT-ALLOW", output="drop_allow_pct", unit="%", parts=MOTORS,
          note="= 100 x limiter (70 A, D-148; was 100 A) x CL-E1-REXT-ALLOW / battery.v_nom. F1 reads it as the limit of CL-F1-DROP-PEAK "
               "(CDR-03 / CDR-EL-04: the 5 % guideline had been removed, not met). The limiter keeps the pack "
               "current, so thrust falls slowly with path resistance (CL-E1-PATH-THRUST-COST) and this limit is "
               "above the 5 % guideline (WB-11), which stays F1's design target. First bound alone: "
               "drop_allow_first_pct",
          how="Re-run after T-E1-STAND.")
kit.claim("CL-E1-PATH-THRUST-COST", "Worst-state thrust lost to the pack-to-ESC path resistance (model)",
          calc="CALC-E1-REXT-ALLOW", output="thrust_cost_path", unit="-", parts=MOTORS,
          how="1 - T_worst(r_ext) / T_worst(0); CDR-EL-04 estimated the 6.7 -> 7.9 mOhm step at -1.6 % (REVIEWER EST, T ~ V^2).")
kit.claim("CL-E1-CRUISE-P-55-V17", "Cruise electrical power at 17 m/s (cruise_ms since D-145), 11x5.5E/EP (propulsion only)",
          calc="CALC-E1-CRUISE-V17", output="P_total_55_W", unit="W", parts=MOTORS + ESCS,
          note="D-96 (c) quoted 283 W from the CR-E1-51 sweep; this is the same point as a claim, so E2 can carry "
               "the fallback to BATT_LOW (CL-E2-CRUISE-TO-LOW-PESS-V17, CDR-05 / CDR-AE-09). Rev 9 (wave 2): "
               "cos(cant) term added (T_m = D / (4 cos cant), D-146 9 deg); the no-cant figure and the cost are "
               "CALC-E1-CRUISE-V17 P_total_55_nocant_W, cant_cost",
          how="Log pack power in steady 17 m/s FBWA legs, both directions; subtract the avionics draw.")
kit.claim("CL-E1-STACK-PROP-PLANE", "Mount face to prop mid-plane (hub centre)", calc="CALC-E1-STACK",
          output="mount_to_prop_plane_m", unit="m", parts=MOTORS + ADAPTERS + PROPS_ID,
          how="Calipers on the first assembled station (T-E1-MOTOR-RM): mount face to hub front face minus half the "
              "hub (8.9 / 2 mm).")
kit.claim("CL-E1-STACK-VS-D3", "E1 stack minus D3's 39 mm (fin_detail.mount.prop_stack_m)", calc="CALC-E1-STACK",
          output="stack_minus_d3_m", unit="m", parts=MOTORS,
          note="negative = the prop sits closer to the collar than D3's CAD assumes (D-28)",
          how="Same caliper measurement; D3 sets prop_stack_m to the measured value.")
kit.claim("CL-E1-PROP-GAP", "Prop plane to collar front with E1's stack / 0.14 D", calc="CALC-E1-STACK",
          output="gap_ratio_e1", unit="-", limit=(">=", 1.0), parts=MOTORS + PROPS_ID,
          note="rev 8: 1.15 with face_ahead 0.0075 (D-61). History: with E1's 37.3 mm stack and D3's 1 mm "
               "face_ahead the gap was below B4's 0.14 D (CR-E1-23)",
          how="Calipers on the built station: collar front to hub centre >= 0.14 D = 39.1 mm.")
kit.claim("CL-E1-AHEAD-NEEDED", "Motor face ahead of the collar needed for 0.14 D", calc="CALC-E1-STACK",
          output="ahead_needed_m", unit="m", parts=MOTORS,
          how="D3 sets fin_detail.mount.face_ahead_m to at least this (rounded up to 0.5 mm).")
kit.claim("CL-E1-STACK-POST-TIP", "Mount face to adapter post tip (rotating envelope end)", calc="CALC-E1-STACK",
          output="mount_to_post_tip_m", unit="m", parts=MOTORS, how="Calipers on the assembled station.")
kit.claim("CL-E1-NUT-ENGAGE", "M6 nut thread engagement margin over full nut height", calc="CALC-E1-STACK",
          output="nut_margin_m", unit="m", limit=(">=", 0.0), parts=ADAPTERS + PROPS_ID,
          how="Assemble prop, washer and nut: the post end must be flush with or proud of the nut face.")
kit.claim("CL-E1-SCREW-ENGAGE", "Motor screw engagement window, worst hole on the canted face", calc="CALC-E1-STACK",
          output="screw_margin_m", unit="m", limit=(">=", 0.0), parts=MOTORS,
          note="D3 R3 plate 4.5 mm, canted with the motor so every head bears flat: M3x8 engages 3.5 mm at every hole, "
               "the top of the window. Passes only if the base holes are >= 4.0 mm deep (CL-E1-HOLE-DEPTH-MIN)",
          how="Probe each base hole depth with a 2 mm drill shank; the M3x8 tip must stop >= 0.5 mm short of the bottom "
              "and engage >= 2.5 mm (T-E1-MOTOR-RM incoming check).")
kit.claim("CL-E1-HOLE-DEPTH-MIN", "Motor base thread depth needed for M3x8", calc="CALC-E1-STACK",
          output="hole_depth_min_m", unit="m", parts=MOTORS,
          note="engagement + 0.5 mm tip clearance; if the first motor's holes are shallower, D3 thickens the plate to "
               "CL-E1-SCREW-SEAT or E1 changes to M3x6 + 1 mm washer (CR-E1-24)",
          how="Probe each base hole with a 2 mm drill shank and calipers (T-E1-MOTOR-RM).")
kit.claim("CL-E1-SCREW-SEAT", "Plate under the head for mid-window engagement", calc="CALC-E1-STACK",
          output="seat_for_mid_window_m", unit="m", parts=MOTORS,
          note="plate thickness that gives 3.0 mm engagement with M3x8; the fallback if the holes are shallow",
          how="Calipers on the printed plate.")
kit.claim("CL-E1-MASS-PRP", "Propulsion flying mass, four stations incl. leads, adapters and motor screws",
          calc="CALC-E1-MASS", output="total_g", unit="g", limit=("<=", P + "mass.allocation_g.propulsion"),
          parts=STATION, how="Weigh each part on the 0.1 g scale on arrival (one of each), update ASM-E1-PART-MASS, re-run.")

# ================================================================== CAD stack (subsystems/propulsion, rev 4)
kit.assumption("ASM-E1-BLADE-HALF", "Prop axial half-extent about the mid-plane 10 mm (with coning)", "axial "
               "half-extent of the rotating APC 11 in MR disc about its mid-plane: -6 mm aft / +10 mm forward with "
               "coning (CR-E1-16), carried symmetric at 10 mm as the keep-out's blade term (k9.prop_keepout "
               "blade_half=0.010, CR-A5-21)", basis="CAD root section (14 mm chord at 48 deg) reaches 5.5 mm; "
               "forward coning of a thin-hub nylon prop at hover thrust EST 4 mm; was k09kit's 8 mm default",
               value=0.010, unit="m",
               status="UNVERIFIED")
kit.assumption("ASM-E1-ADAPTER-SCREW", "Adapter screws into the bell: strip model (D-173: 3 x M2.5, X2814 adapter)",
               "D-173 values: d 2.5 mm, engagement 2.5 mm (1.0 d), tightening 0.3 N m (EST, C6 to set), nut factor 0.2, "
               "150 MPa; the bell holes are M2.5x0.45 depth 3.5 (X2814 drawing). Before: d 3 mm; shortest engagement "
               "2.0 mm; tightening torque 0.5 N m (C6); nut factor 0.2; shear allowable of the bell alloy 150 MPa; "
               "stripping area 0.5 pi d L (internal thread, conservative)",
               basis="VDI 2230 short form; 6061-T6 shear ultimate 207 MPa taken down to 150 MPa for an unknown bell "
                     "alloy; measure the bell-top thread depth on arrival (T-E1-MOTOR-RM)",
               value=[0.0025, 0.0025, 0.3, 0.2, 150e6], unit="m,m,N m,-,Pa", status="UNVERIFIED",
               cites=["SRC-E1-X2814-V3"])


kit.assumption("ASM-E1-ADAPTER-FIT", "Adapter screw fit (D-173: X2814 adapter, flange 2.0 mm EST, M2.5x4 / M2.5x5, bell "
               "depth 3.5 mm); before: head-seat flange 1.5 mm, M3x4 / M3x5, tip clear 0.5 mm, "
               "rule 1.0 d", "the bolt-on adapter's counterbored flange leaves 1.5 mm of each screw above the bell top "
               "(M3x4 engages 2.5 mm, the declared E-PRP-01..04 value); candidate lengths 4 mm (vendor) and 5 mm; the "
               "screw tip must stop >= 0.5 mm short of the windings under the bell top; minimum engagement into metal "
               "1.0 d (D-41, C6)", basis="Small Parts CNC adapter listing (M3x4 supplied) and the 2.5 mm declared "
               "engagement; D-41 joint rule; flange to be measured with the adapter (T-E1-MOTOR-RM)",
               value=[0.0020, 0.004, 0.005, 0.0005, 1.0], unit="m,m,m,m,-", status="UNVERIFIED",
               cites=["SRC-E1-X2814-V3"])
kit.assumption("ASM-E1-ESC-STRAP", "ESC strap 1.5 mm thick, 10 mm band", "one 10 mm hook-and-loop strap (fins "
               "BUILD, E3 ASM-E3-ESC-STRAP) over the ESC's FET face: single layer 1.5 mm where it crosses the ESC; "
               "the overlap sits on the inboard face of the pad, not on the ESC",
               basis="typical 10 mm hook-and-loop cable tie 1.3-1.6 mm; the ESC body (45 x 20 x 6 mm in heat-shrink, "
                     "ASM-E3-ESC) bounds the 6.6 g 45 A BLHeli_S board, which generic listings give as 28.5 x 13 mm; "
                     "LANRC publishes no drawing. Stripped ESC: F2's 16 AWG solder joints sit on the pads under the "
                     "shrink, the signal lead leaves the aft end. Measure on arrival", value=[0.0015, 0.010], unit="m",
               status="UNVERIFIED")


@kit.calc("CALC-E1-ADAPTER-CHOICE", title="Prop adapter screws: M3x4 under deviation D-58 or M3x5 at the 1.0 d rule",
          equation="e_L = L - t_flange ; e_rule = k d ; thread needed (D-58) = e_M3x4 ; free depth for M3x5 = "
                   "e_M3x5 + tip clearance ; RF(e) = 0.5 pi d e tau / (T / (K d))",
          inputs={"a": "ASM-E1-ADAPTER-SCREW", "f": "ASM-E1-ADAPTER-FIT"},
          assumes=["ASM-E1-ADAPTER-SCREW", "ASM-E1-ADAPTER-FIT"])
def adapter_choice(a, f):
    d, _, T, K, tau = a
    fl, l4, l5, tip, k = f
    e4, e5, rule = l4 - fl, l5 - fl, k * d
    f_pre = T / (K * d)
    return {"e_m3x4_m": round(e4, 9), "e_m3x5_m": round(e5, 9), "e_rule_m": rule,
            "m3x5_margin_m": round(e5 - rule, 9), "m3x4_short_m": round(rule - e4, 9),
            "thread_needed_d58_m": round(e4, 9), "free_depth_m3x5_m": round(e5 + tip, 9),
            "rf_m3x4": 0.5 * math.pi * d * e4 * tau / f_pre, "rf_m3x5": 0.5 * math.pi * d * e5 * tau / f_pre}


@kit.calc("CALC-E1-ESC-ENV", title="ESC installed envelope on the fin pad (for B4's drag and wash, E3)",
          equation="h = h_body + t_strap ; w = w_body + 2 t_strap ; A_front = w h (strap band, seen along x)",
          inputs={"esc": "ASM-E3-ESC", "st": "ASM-E1-ESC-STRAP"}, units={"st": "m"},
          assumes=["ASM-E3-ESC", "ASM-E1-ESC-STRAP"])
def esc_env(esc, st):
    L, w, h = esc[0], esc[1], esc[2]
    t, band = st
    return {"len_m": L, "w_strap_m": w + 2 * t, "proud_max_m": h + t, "proud_body_m": h,
            "frontal_m2": (w + 2 * t) * (h + t), "strap_band_m": band}


@kit.calc("CALC-E1-CAD-STACK", title="Modelled station: canted prop plane, keep-out, ESC on the pad",
          equation="x_face = x_tube - od/2 - bond_gap - collar_wall - face_ahead ; x_hub = x_face - s cos(cant) ; "
                   "gap = (x_face + face_ahead) - x_hub ; dx_tip = D/2 sin(cant) + h_blade vs h_blade + clr ; "
                   "esc: pad_len / L_esc ; slot inner edge (pad_h/2 - edge - slot_z) / (w_esc/2)",
          inputs={"st": "ASM-E1-STACK", "xt": P + "fins.tube.x_m", "od": P + "fins.tube.od_m",
                  "bg": P + "fin_detail.bond_gap_m", "cw": P + "fin_detail.mount.collar_wall_m",
                  "ahead": P + "fin_detail.mount.face_ahead_m", "cant": P + "propulsion.stations.cant_deg",
                  "D": P + "propulsion.prop_diameter_m", "xp": P + "propulsion.stations.x_prop_plane_m",
                  "clr": P + "requirements.prop_clearance_min_m", "hb": "ASM-E1-BLADE-HALF", "esc": "ASM-E3-ESC",
                  "plen": P + "fin_detail.esc_pad.len_m", "ph": P + "fin_detail.esc_pad.h_m",
                  "slot": P + "fin_detail.esc_pad.slot_m", "edge": P + "fin_detail.esc_pad.slot_edge_m"},
          units={"st": "m", "xt": "m", "od": "m", "bg": "m", "cw": "m", "ahead": "m", "cant": "deg", "D": "m",
                 "xp": "m", "clr": "m", "hb": "m", "plen": "m", "ph": "m", "slot": "m", "edge": "m"},
          assumes=["ASM-E1-STACK", "ASM-E1-BLADE-HALF", "ASM-E3-ESC"])
def cad_stack(st, xt, od, bg, cw, ahead, cant, D, xp, clr, hb, esc, plen, ph, slot, edge):
    body, base, post, hub, wash, nut = st
    s = body + base + hub / 2
    c = math.radians(cant)
    x_face = xt - od / 2 - bg - cw - ahead
    x_hub = x_face - s * math.cos(c)
    gap = (x_face + ahead) - x_hub
    return {"x_face_m": x_face, "x_hub_m": x_hub, "hub_minus_datum_m": x_hub - xp, "gap_m": gap,
            "gap_ratio": gap / (0.14 * D), "dx_tip_m": D / 2 * math.sin(c) + hb, "ko_half_m": hb + clr,
            "esc_len_ratio": plen / esc[0],
            "esc_slot_ratio": (ph / 2 - edge - slot[1]) / (esc[1] / 2)}


@kit.calc("CALC-E1-ADAPTER-STRIP", title="Prop adapter M3x4 in the bell: thread strip vs tightening preload",
          equation="F_pre = T / (K d) ; F_strip = 0.5 pi d L tau ; RF = F_strip / F_pre",
          inputs={"a": "ASM-E1-ADAPTER-SCREW"}, assumes=["ASM-E1-ADAPTER-SCREW"])
def adapter_strip(a):
    d, L, T, K, tau = a
    f_pre = T / (K * d)
    f_strip = 0.5 * math.pi * d * L * tau
    return {"f_pre_n": f_pre, "f_strip_n": f_strip, "rf": f_strip / f_pre}


kit.assumption("ASM-E1-BLADE-ENV", "Prop swept envelope about the hub mid-plane: 10 mm forward, 6 mm aft",
               "axial extent of the rotating APC 11 in MR disc about its hub mid-plane, forward (thrust side, with "
               "coning) and aft: the real envelope behind ASM-E1-BLADE-HALF's symmetric 10 mm (CR-E1-16)",
               basis="CAD root section (14 mm chord at 48 deg) reaches 5.5 mm either side; the blades cone forward "
                     "under thrust (EST 4 mm at hover), never aft (no reverse thrust on K09-L)",
               value=[0.010, 0.006], unit="m", status="UNVERIFIED")


def _tip_gap(xt, r_t, len_t, yf, ys, zs, x_face, s, cant, sense, R, fwd, aft, n_phi=144, dz=0.0005):
    """Min distance (m) from the UR prop's swept volume (radius R, axial -fwd..+aft about the hub, aft = toward the
    wing) to the surface of the CF motor tube (z axis, centre (xt, yf), radius r_t, z 0..len_t/2). The station
    placement is the CAD module's (subsystems/propulsion/fusion/propulsion.py geometry(): D3's plate normal)."""
    n = math.hypot(ys, zs)
    tc = math.tan(math.radians(cant))
    ay, az = sense * tc * (-zs / n), sense * tc * (ys / n)
    nn = math.sqrt(1 + ay * ay + az * az)
    th = (-1 / nn, ay / nn, az / nn)                     # unit thrust direction (forward)
    hub = (x_face + s * th[0], ys + s * th[1], zs + s * th[2])
    best = 9.0
    for k in range(int(len_t / 2 / dz) + 1):
        z = k * dz
        for j in range(n_phi):
            ph = 2 * math.pi * j / n_phi
            p = (xt + r_t * math.cos(ph), yf + r_t * math.sin(ph), z)
            d = (p[0] - hub[0], p[1] - hub[1], p[2] - hub[2])
            t = -(d[0] * th[0] + d[1] * th[1] + d[2] * th[2])   # + aft of the mid-plane
            rr = math.sqrt(max(0.0, d[0] ** 2 + d[1] ** 2 + d[2] ** 2 - t * t))
            dt = max(0.0, -fwd - t, t - aft)
            g = dt if rr <= R else math.hypot(dt, rr - R)
            best = min(best, g)
    return best


@kit.calc("CALC-E1-TIP-GAP", title="Canted prop disc to the CF motor tube: true clearance and the face_ahead it needs",
          equation="hub = face + s t(cant, sense) ; gap = min over the tube surface of dist(point, disc volume "
                   "r <= D/2, -fwd <= axial <= +aft) ; face_ahead_needed: smallest face_ahead (0.5 mm steps) with "
                   "gap >= clr",
          inputs={"st": "ASM-E1-STACK", "env": "ASM-E1-BLADE-ENV", "hb": "ASM-E1-BLADE-HALF",
                  "xt": P + "fins.tube.x_m", "od": P + "fins.tube.od_m", "lt": P + "fins.tube.length_m",
                  "yf": P + "fins.y_m", "ys": P + "propulsion.stations.y_m", "zs": P + "propulsion.stations.z_m",
                  "bg": P + "fin_detail.bond_gap_m", "cw": P + "fin_detail.mount.collar_wall_m",
                  "ahead": P + "fin_detail.mount.face_ahead_m", "sense": P + "fin_detail.mount.cant_sense_UR",
                  "cant": P + "propulsion.stations.cant_deg", "D": P + "propulsion.prop_diameter_m",
                  "clr": P + "requirements.prop_clearance_min_m"},
          units={"st": "m", "env": "m", "hb": "m", "xt": "m", "od": "m", "lt": "m", "yf": "m", "ys": "m", "zs": "m",
                 "bg": "m", "cw": "m", "ahead": "m", "sense": "-", "cant": "deg", "D": "m", "clr": "m"},
          assumes=["ASM-E1-STACK", "ASM-E1-BLADE-ENV", "ASM-E1-BLADE-HALF"])
def tip_gap(st, env, hb, xt, od, lt, yf, ys, zs, bg, cw, ahead, sense, cant, D, clr):
    body, base, post, hub, wash, nut = st
    s = body + base + hub / 2
    fwd, aft = env
    x0 = xt - od / 2 - bg - cw                            # face at face_ahead = 0
    g = lambda a, af=aft, **kw: _tip_gap(xt, od / 2, lt, yf, ys, zs, x0 - a, s, cant, sense, D / 2, fwd, af, **kw)
    lo, hi = 0.0, ahead + 0.030                          # bisection on face_ahead from 0 (rev 8: from `ahead`, it
                                                         # returned the carried value once that passed)
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        if g(mid, n_phi=72, dz=0.001) >= clr:
            hi = mid
        else:
            lo = mid
    need = math.ceil(lo * 2000 - 1e-9) / 2000            # to 0.5 mm, confirmed on the full grid
    while g(need) < clr:
        need += 0.0005
    return {"gap_m": g(ahead), "gap_sym_m": g(ahead, af=hb),
            "gap_sense_plus_m": _tip_gap(xt, od / 2, lt, yf, ys, zs, x0 - ahead, s, cant, -sense, D / 2, fwd, aft),
            "gap_untilted_m": _tip_gap(xt, od / 2, lt, yf, ys, zs, x0 - ahead, s, 0.0, sense, D / 2, fwd, aft),
            "ahead_needed_m": round(need, 4), "gap_at_needed_m": g(need), "stack_add_m": round(need - ahead, 4),
            "gap_at_75_m": g(0.0075)}


kit.claim("CL-E1-TIP-GAP-TUBE", "Canted prop disc (-6 / +10 mm envelope) to the CF motor tube, true surface gap",
          calc="CALC-E1-TIP-GAP", output="gap_m", unit="m", limit=(">=", P + "requirements.prop_clearance_min_m"),
          verifies=["R-PROP-CLEAR"], parts=PROPS_ID + ["FIN-002-R", "FIN-002-L"],
          note="rev 9 (wave 2, D-146): 9 deg cant on D3's 12.0 mm mount (face_ahead read from "
               "subsystems/fins/params.json). Rev 8 (D-61): on D3's 7.5 mm mount 26.1 mm, PASS (+1.1 mm); was 21.1 mm FAIL at 2.5 mm. D-52 (cant "
               "sense -1) swings the wing-side blade tip aft over the tube (42.8 mm with sense +1, gap_sense_plus_m). "
               "Same finding as D3's CR-D3-26 (20.9 mm at 2.5 mm). The nearest tube point is at "
               "r 143.8 mm, 4 mm OUTBOARD of the 139.7 mm tip, 26.8 mm aft of the mid-plane: a tip-to-structure gap, "
               "so the mount chain is not exempted from KO-PROP and a hub-radius annulus would not remove it (rev 7). "
               "check.py 21.0 mm (hull), probe 21.2 mm (surface samples); every other flight part >= 25 mm "
               "(bore boss 25.4, tube plug 26.1, wing >= 33.5 mm)",
          how="Built station: printed 25 mm gauge between the blade trailing face at the tip and the tube, blade "
              "turned through the wing-side position (T-E1-MOTOR-RM).")
kit.claim("CL-E1-FACE-AHEAD-FOR-CLR", "Mount face_ahead that gives the 25 mm tube clearance (E1 envelope)",
          calc="CALC-E1-TIP-GAP", output="ahead_needed_m", unit="m", parts=PROPS_ID + ["FIN-003-UR"],
          note="rev 8: the least face_ahead (bisection from 0), so 1 mm under the carried 0.0075 (D-61). For A1's "
               "CR-D3-26 decision: E1 proposed 0.0075 m (CL-E1-TIP-GAP-AT-75, about "
               "+1 mm margin). Rev 7: with KO-PROP on E1's envelope and check.py's hull + distance test, check.py "
               "reports 0 keep-out errors at 0.0065 and 0.0075 and 4 (the tube, 24.5 mm) at 0.0060 (in-memory trials, "
               "team/E1/prop_clearance.json)",
          how="Recompute after any change to the stack, cant, cant sense or tube station.")
kit.claim("CL-E1-TIP-GAP-AT-75", "Prop disc to motor tube with face_ahead 0.0075 m (the D-61 mount; information)",
          calc="CALC-E1-TIP-GAP", output="gap_at_75_m", unit="m", parts=PROPS_ID + ["FIN-002-R", "FIN-002-L"],
          note="rev 9 (wave 2, D-146): information only, no limit. At the 9 deg cant the 7.5 mm mount puts the blade "
               "inside the 25 mm keep-out (this value); the flight mount is face_ahead 12.0 mm, CL-E1-TIP-GAP-TUBE. "
               "Rev 8: equals CL-E1-TIP-GAP-TUBE now that D3 carries 0.0075 (D-61). +5.0 mm of stack: prop plane x "
               "-0.0077 -> -0.01267 (CL-E1-CAD-HUB-X), hub 5 mm further from the collar "
               "(CL-E1-CAD-PROP-GAP rises); mount cheeks +5 mm (D3, C4 rocking stiffness)",
          how="As CL-E1-TIP-GAP-TUBE on the R5 mount.")

kit.claim("CL-E1-CAD-HUB-X", "Modelled prop hub centre x on the canted axis", calc="CALC-E1-CAD-STACK",
          output="x_hub_m", unit="m", parts=PROPS_ID,
          note="rev 8 (D-61, face_ahead 0.0075): -0.01267, datum DP-PROP / x_prop_plane_m -0.0127 (+0.03 mm). "
               "D3's CL-D3-X-PROP (same formula, face - 37.3 cos 7 deg) gives -0.01267 on the R5 mount: agrees to "
               "5 um (E1 stack 37.295 vs D3 37.3 mm). subsystems/propulsion/fusion/propulsion.py "
               "places the hub here; KO-PROP-<st> are registered on the modelled hub",
          how="python -I redesign/subsystems/propulsion/make_propulsion.py prints the same x; calipers on the built "
              "station (T-E1-MOTOR-RM).")
kit.claim("CL-E1-CAD-HUB-VS-DATUM", "Modelled hub minus datum DP-PROP", calc="CALC-E1-CAD-STACK",
          output="hub_minus_datum_m", unit="m", parts=PROPS_ID,
          note="positive = the real prop sits aft of the datum, closer to the mount collar (CR-E1-29)",
          how="As CL-E1-CAD-HUB-X.")
kit.claim("CL-E1-CAD-PROP-GAP", "Prop plane to collar front along x, canted stack / 0.14 D", calc="CALC-E1-CAD-STACK",
          output="gap_ratio", unit="-", limit=(">=", 1.0), parts=PROPS_ID + MOTORS,
          note="same finding as CL-E1-PROP-GAP with the 7 deg cant included; rev 8: 1.14 on the 7.5 mm mount "
               "(D-61; was 1.01 at 2.5 mm, D-51)",
          how="Calipers on the built station: collar front to hub centre >= 0.14 D = 39.1 mm.")
kit.claim("CL-E1-KO-TILT", "Blade tip axial (x) excursion of the 7 deg canted disc, incl. the blade half",
          calc="CALC-E1-CAD-STACK", output="dx_tip_m", unit="m", parts=PROPS_ID,
          note="information only since rev 5: KO-PROP-<st> is now the cylinder on the canted shaft axis "
               "(k9.prop_keepout rotate=rot, CR-A5-21), so this excursion is geometry inside the keep-out and the "
               "full 25 mm clearance is margin; check.py tests the tilted cylinder exactly. Since D-52 (sense -1) "
               "the wing-side tip swings aft, toward the motor tube: CL-E1-TIP-GAP-TUBE",
          how="Recompute from the CAD bounding box of PRP-003-<st> after any cant or prop change.")
@kit.calc("CALC-E1-KO-ENV", title="Prop keep-out KO-PROP-<st> on E1's swept envelope (rev 7)",
          equation="aft face = aft + clr ; fwd face = fwd + clr ; half = (fwd + aft)/2 + clr ; centre shift ahead "
                   "of the hub = (fwd - aft)/2 (k9.prop_keepout fwd=, aft=)",
          inputs={"env": "ASM-E1-BLADE-ENV", "clr": P + "requirements.prop_clearance_min_m"},
          units={"env": "m", "clr": "m"}, assumes=["ASM-E1-BLADE-ENV"])
def ko_env(env, clr):
    fwd, aft = env
    return {"ko_half_m": (fwd + aft) / 2 + clr, "ko_fwd_m": fwd + clr, "ko_aft_m": aft + clr,
            "ko_shift_m": (fwd - aft) / 2}


kit.claim("CL-E1-KO-HALF", "Prop keep-out axial half-length on the canted axis (swept envelope / 2 + clearance)",
          calc="CALC-E1-KO-ENV", output="ko_half_m", unit="m", parts=PROPS_ID,
          note="rev 7: KO-PROP-<st> is registered with fwd 0.010 / aft 0.006 (ASM-E1-BLADE-ENV, A5's CR-E1-45 "
               "arguments), radius D/2 + 25 mm, centred 2 mm ahead of the hub; was 35 mm symmetric "
               "(ASM-E1-BLADE-HALF), which placed 4 mm of non-existent blade aft of the disc. check.py reports "
               "the distance to the swept volume: rev 8, 0 keep-out errors on the 7.5 mm mount (was the CF motor "
               "tube at 21.0 mm on 2.5 mm, CL-E1-TIP-GAP-TUBE). "
               "The mount chain is NOT exempted: the tube's nearest point is 4 mm outboard of the tip, not behind the "
               "hub",
          how="python -I redesign/fusion/check.py (hull + distance) and python -I redesign/team/E1/prop_clearance.py "
              "(surface samples).")
kit.claim("CL-E1-KO-AFT", "Prop keep-out reach aft of the hub mid-plane (toward the mount, tube and wing)",
          calc="CALC-E1-KO-ENV", output="ko_aft_m", unit="m", parts=PROPS_ID,
          note="6 mm swept envelope (blade section at the root; at the tip about 1 mm of section plus 5 mm for aft "
               "deflection when windmilling in a throttle-cut descent) + 25 mm",
          how="Stand: photograph the tip against a scale at idle with 15 m/s blown across the disc (T-E1-STAND).")
kit.claim("CL-E1-KO-FWD", "Prop keep-out reach ahead of the hub mid-plane (with coning)",
          calc="CALC-E1-KO-ENV", output="ko_fwd_m", unit="m", parts=PROPS_ID,
          how="As CL-E1-KO-AFT at full throttle (coning forward).")
kit.claim("CL-E1-ESC-PAD-LEN", "D3's pad length / ESC length", calc="CALC-E1-CAD-STACK",
          output="esc_len_ratio", unit="-", limit=(">=", 1.0), parts=ESCS,
          how="Lay the ESC in heat-shrink on a printed pad before the strap is threaded.")
kit.claim("CL-E1-ESC-SLOT", "Strap-slot inner edge from the pad centre / ESC half-width", calc="CALC-E1-CAD-STACK",
          output="esc_slot_ratio", unit="-", limit=(">=", 1.0), parts=ESCS,
          note="the 20 mm ESC covers 1 mm of each 3 mm strap slot on the 28 mm pad; the strap then bends over the ESC "
               "edge inside the slot and cuts into the heat-shrink. D3: pad h 0.028 -> 0.031 m (CR-E1-30)",
          how="Thread the strap on a printed pad with the ESC in place: the strap must enter the slot beside the ESC.")
kit.claim("CL-E1-ESC-PROUD", "ESC envelope height proud of the pad at the strap band", calc="CALC-E1-ESC-ENV",
          output="proud_max_m", unit="m", parts=ESCS,
          note="for B4 (CR-B4-20): use 7.5 mm, not the 6.8 mm of ASM-B4-ESC; the body is 6.0 mm proud outside the "
               "10 mm strap band; length 45 mm along x, width 23 mm at the strap",
          how="T-E1-MOTOR-RM: calipers over the strapped ESC on a printed pad.")
kit.claim("CL-E1-ESC-FRONTAL", "ESC frontal area along x at the strap band", calc="CALC-E1-ESC-ENV",
          output="frontal_m2", unit="m2", parts=ESCS,
          note="23 x 7.5 mm bounding rectangle seen along x; the ESC long side lies along x on the pad",
          how="As CL-E1-ESC-PROUD.")
kit.claim("CL-E1-ADAPTER-M3X5-ENGAGE", "M3x5 adapter-screw engagement minus the 1.0 d rule", calc="CALC-E1-ADAPTER-CHOICE",
          output="m3x5_margin_m", unit="m", limit=(">=", 0.0), parts=ADAPTERS + MOTORS,
          note="the compliant option of CR-A4-43: valid only if the bell top has >= 3.0 mm of thread and >= "
               "CL-E1-ADAPTER-M3X5-DEPTH of free depth; otherwise M3x4 under D-58",
          how="T-E1-MOTOR-RM: depth gauge in a bell-top hole (thread length and free depth to the windings).")
kit.claim("CL-E1-ADAPTER-M3X5-DEPTH", "Free hole depth under the bell top needed for M3x5", calc="CALC-E1-ADAPTER-CHOICE",
          output="free_depth_m3x5_m", unit="m", parts=MOTORS,
          how="T-E1-MOTOR-RM: depth gauge from the bell-top face to the first obstruction in each of the 4 holes.")
kit.claim("CL-E1-ADAPTER-THREAD-D58", "Bell-top thread length that D-58 requires (M3x4 fully engaged)",
          calc="CALC-E1-ADAPTER-CHOICE", output="thread_needed_d58_m", unit="m", parts=MOTORS,
          note="D-58 grants the 2.0 mm minimum only if T-E1-MOTOR-RM measures at least this; below it the deviation "
               "lapses and the station is not flown (fallback: the motor-box adapter on its own screws, re-assessed)",
          how="T-E1-MOTOR-RM: thread length by a gauge screw turned in until it bottoms, minus the head seat.")
kit.claim("CL-E1-ADAPTER-RF-NOM", "Adapter screw thread strip RF at the declared 2.5 mm engagement",
          calc="CALC-E1-ADAPTER-CHOICE", output="rf_m3x4", unit="-", limit=(">=", P + "requirements.safety_factor_ult"),
          parts=ADAPTERS + MOTORS, how="As CL-E1-ADAPTER-STRIP.")
kit.claim("CL-E1-ADAPTER-STRIP", "Adapter screw thread strip at 2.0 mm engagement vs preload (RF)",
          calc="CALC-E1-ADAPTER-STRIP", output="rf", unit="-", limit=(">=", P + "requirements.safety_factor_ult"),
          parts=ADAPTERS + MOTORS,
          note="cites the 2.0 mm minimum in E-PRP-01..04 (below the 1.0 d rule of D-41); service loads are 14 N shear "
               "and 4 N axial per screw, so the tightening preload governs",
          how="T-E1-MOTOR-RM: measure the bell-top thread depth; torque one adapter to 0.5 N m and off 5 times, "
              "threads undamaged.")

kit.test("T-E1-STAND", "Thrust stand, one station, both candidate props", verifies=["CL-E1-TW-TABLE", "CL-E1-TW-WORST",
         "CL-E1-SAG-FACTOR", "CL-E1-IMAX-168-55", "CL-E1-HOVER-GW", "CL-E1-KT", "CL-E1-KP", "CL-E1-MAKER-SUPPLY",
         "CL-E1-ILIM-I", "CL-E1-ILIM-I-B2", "CL-E1-TW-WORST-B2", "CL-E1-TW-FRESH-B2", "CL-E1-TW-WORST-B2-PROP",
         "CL-E1-R-EFF-MAKER", "CL-E1-T-STAND-B2", "CL-E1-T-STAND-B2-PROP", "CL-E1-T-STAND"],
         procedure="H1 stand (20 kg cell + HX711), X3108S + LANRC 45 A, 11x4.5MR then 11x5.5MR; held 14.8 V bench supply "
                   "(>= 40 A) and then a flight pack; 10 % throttle steps to 100 %, 3 s each; log gf, A, V, rpm (optical "
                   "tach or ESC telemetry), can temperature; one 60 s run at 689 gf for g/W; ten 10 -> 100 % throttle "
                   "punches in < 50 ms with no desync. CDR-04 / CDR-05 additions: bus voltage logged at the ESC "
                   "pads on every run; full throttle at a held 14.6 V and 11.9 V bus (pass >= 1 330 gf and >= 1 060 gf); "
                   "phase current on one motor lead (clamp or ESC telemetry) at the limiter duty; one 30 s run at the "
                   "limiter with the bell temperature (pass <= 80 degC, else the limiter drops to CL-E1-ILIM-FOR-25A)")
kit.test("T-E1-MOTOR-RM", "Incoming check: resistance, no-load current, mass, bolt pattern, hole and thread depth",
         verifies=["CL-E1-KP", "CL-E1-MASS-PRP", "CL-E1-SCREW-ENGAGE", "CL-E1-STACK-PROP-PLANE", "CL-E1-PROP-GAP",
                   "CL-E1-ADAPTER-THREAD-D58", "CL-E1-ADAPTER-M3X5-DEPTH", "CL-E1-HOLE-DEPTH-MIN", "CL-E1-ESC-PROUD",
                   "CL-E1-TIP-GAP-TUBE"],
         procedure="Weigh motor, stripped ESC, prop, adapter set (0.1 g); calipers: base diameter (D3 needs >= 28 mm), "
                   "base bolt pattern (D3 prints 16 x 19 mm), base hole depth (>= 4.0 mm, CL-E1-HOLE-DEPTH-MIN), "
                   "bell-top thread length (>= 2.5 mm for D-58; >= 3.0 mm with >= 4.0 mm free depth -> M3x5, "
                   "CR-A4-43), adapter flange under the screw head, motor phase-lead length from the base (F2's "
                   "routed reach 0.121 m, CL-F2-PHASE-REACH: if the leads reach, no splice and F2 returns 12 g), "
                   "ESC strapped on a printed pad (height proud), body length, adapter base and post; on the first built "
                   "station a printed 25 mm gauge between the blade's aft face at the tip and the CF tube, blade turned "
                   "through the wing-side position (R-PROP-CLEAR); 4-wire: 2.00 A from a bench supply through two phases, read the voltage drop (R = V / I); no-load "
                   "current and rpm at 10.0 V without prop (Kv = rpm / (V - I0 R))")
kit.test("T-E1-HOVER-LOG", "Tethered hover current", verifies=["CL-E1-HOVER-I-55", "CL-E1-HOVER-DT"],
         procedure="XPS aircraft at 2.6 kg, 30 s tethered hover; pack current from the power module; can temperature "
                   "by IR at landing")


# ================================================================== report
def report():
    vals = {n["id"]: n for n in kit.nodes.values()}
    print("\n--- E1 propulsion summary ---")
    for cid in ("CALC-E1-CAL", "CALC-E1-HOVER", "CALC-E1-FULL", "CALC-E1-CRUISE", "CALC-E1-CORRIDOR", "CALC-E1-MOTOR-OUT",
                "CALC-E1-LIMIT", "CALC-E1-ILIM-25", "CALC-E1-SENS", "CALC-E1-WORST", "CALC-E1-BOUND2", "CALC-E1-BOUND2-CHECK",
                "CALC-E1-REXT-ALLOW", "CALC-E1-MASS-LIMIT", "CALC-E1-CRUISE-V17", "CALC-E1-STACK", "CALC-E1-MASS", "CALC-E1-HOVER-I-BAND"):
        print(cid)
        for k, v in vals[cid]["outputs"].items():
            if isinstance(v, list):                             # tables (CALC-E1-CAL hi_rows)
                print(f"   {k}")
                for row in v:
                    print("      " + "  ".join(f"{x:9.4g}" for x in row))
            else:
                print(f"   {k:<22} {v:10.4g}")


def write_parts(write=False):
    """Print-only unless write=True (CDR-29: an analysis re-run must not rewrite a shared file).
    redesign/subsystems/propulsion/parts.csv (assigned by A1, CR-A3-05): flown quantities, per-unit flying mass
    incl. leads from ASM-E1-PART-MASS, so A3's roll-up and CL-E1-MASS-PRP use one set of numbers. Rev 3: the four
    motor screws are booked inside PRP-001 (fins convention for fasteners: a 1xx line with mass 0), so qty = number
    of instance nodes in interfaces.json for every line that carries mass."""
    import csv
    pm = kit.nodes["ASM-E1-PART-MASS"]["value"]
    rows = [
        ["PRP-001", "Motor SunnySky X3108S KV900 (with its 4 x M3x8 mount screws)", 4, "buy", "-", "-",
         round(pm["motor"] + pm["motor_screws"], 2), 24.99, "https://sunnyskyusa.com/products/sunnysky-x3108s-motors",
         "81.0 g with factory leads, no bullets (HRN-E03) + 3.2 g screws (PRP-005); buy 5 (1 spare); base bolt "
         "pattern, hole depth and lead length not published: measure the first motor (T-E1-MOTOR-RM); UNVERIFIED"],
        ["PRP-002", "ESC LANRC BLHeli_S 45 A (55 A 10 s) 2-6S, Bluejay reflash", 4, "buy", "-", "-", pm["esc"], 7.50,
         "https://www.amazon.com/dp/B0D2HS4Y4J",
         "stripped: factory power leads removed, F2 solders 16 AWG to the pads (D-48); 6.6 g bare board + 1.0 g signal "
         "lead and shrink EST; envelope 45 x 23 x 7.5 mm at the strap (CL-E1-ESC-PROUD); 4-pack $30.00, buy 2 packs "
         "(4 spare); fallback Holybro Tekko32 F4 45A AM32 $22.50 (readymaderc.com); price UNVERIFIED"],
        ["PRP-003", "Prop APC 11x5.5E (LP11055E) on UL/LR, 11x5.5EP (LP11055EP) on UR/LL (D-161)", 4, "buy", "-",
         "glass-filled nylon", pm["prop"], 4.17, "https://www.apcprop.com/product/11x5-5e/",
         "rotation per F4's motor map (UR, LL CW from the nose = EP); hub 20.3 mm dia x 10.4 mm, 1/4 in bore, "
         "centred on the M6 post with an APC LPAR06E ring; M6 thin nut ISO 4035 3.2 mm; buy 6 E + 6 EP (2 + 2 "
         "fitted, 8 spare); no MR props bought (D-161)"],
        ["PRP-004", "Prop adapter, bolt-on M6x1 (LH on UR/LL, RH on UL/LR) + 4 x M3x4 SHCS + M6 nut ISO 4032 + washer",
         4, "buy", "-", "aluminium / steel", pm["adapter_nut"], 5.99,
         "https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct",
         "set of 4 (2 RH + 2 LH) $23.95, out of stock 2026-11-09; fallback: the adapter in each motor box (one thread "
         "hand) with Loctite 243 on the nut; LH thread on the CW motors so drag torque tightens the nut"],
        ["PRP-005", "Motor screw M3x8 SHCS ISO 4762 A2", 16, "buy", "-", "A2 stainless", 0, 0.10,
         "Bolt Depot (same size as the old design's F01)",
         "mass inside PRP-001 (0.8 g each); buy 20 (4 spare); joint stack in fins E-FIN-61..64 (D3 owns the edge); "
         "0.20 N m (C6 CR-C6-10) + Loctite 243 on the tip threads only; engagement 3.5 mm in the 2.5-3.5 mm "
         "window (CL-E1-SCREW-ENGAGE), hole depth probed on arrival"],
    ]
    out = HERE.parents[1] / "subsystems" / "propulsion" / "parts.csv"
    rel = out.relative_to(HERE.parents[2]).as_posix()
    total = sum(r[2] * r[6] for r in rows)
    if not write:
        # compare qty and mass with the file as it stands (C6's fastener_parts.py moves the screw mass out of
        # PRP-001 into its own hardware lines and tags the note [C6-HW], so a difference there is expected)
        have = {}
        if out.exists():
            with out.open(newline="", encoding="utf-8") as f:
                have = {r["part_id"]: r for r in csv.DictReader(f)}
        print(f"\n{rel}: NOT written (print-only; --write-parts rewrites it and runs C6's fastener_parts.py)")
        print(f"  E1's lines: {len(rows)}, {total:.1f} g flying")
        for r in rows:
            h = have.get(r[0])
            if h is None:
                state = "not in the file"
            else:
                same = int(float(h["qty"])) == r[2] and abs(float(h["mass_g"]) - float(r[6])) < 0.005
                state = "as in the file" if same else f"file has qty {h['qty']}, {h['mass_g']} g" + \
                    (" [C6-HW]" if "[C6-HW]" in h.get("notes", "") else "")
            print(f"  {r[0]}  qty {r[2]:>2}  {float(r[6]):6.2f} g  ${float(r[7]):6.2f}   {state}")
        return {r[0]: r for r in rows}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part_id", "name", "qty", "make_or_buy", "process", "material", "mass_g", "unit_cost_usd",
                    "vendor_or_file", "notes"])
        w.writerows(rows)
    print(f"{rel}: {len(rows)} lines, {total:.1f} g flying (written)")
    return {r[0]: r for r in rows}


if __name__ == "__main__":
    WRITE_PARTS = "--write-parts" in sys.argv   # CDR-29: default writes team/E1/claims.json only
    kit.write()
    write_parts(WRITE_PARTS)   # interfaces.json: python -I redesign/subsystems/propulsion/make_propulsion.py (rev 4)
    report()
    if WRITE_PARTS:             # C6 FASTENERS-CAD: write_parts() dropped the modelled fastener lines; C6 re-applies
        import os as _o, runpy as _r            # them (patches subsystems/*/parts.csv and interfaces.json)
        _r.run_path(_o.path.join(_o.path.abspath(__file__).rsplit(_o.sep + 'redesign' + _o.sep, 1)[0], 'redesign', 'team',
                                 'C6', 'fastener_parts.py'), run_name='c6_hook')['run']()
