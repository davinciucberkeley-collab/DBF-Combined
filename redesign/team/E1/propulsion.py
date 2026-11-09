"""E1 propulsion engineer: motor / ESC / prop model and margins for the K09-L quad tailsitter.

Run:  python -I redesign/team/E1/propulsion.py      -> claims.json beside this file + a printed report
      python -I redesign/team/E1/plots.py           -> FIG PRP-01 / PRP-02 SVGs (reads this module)

Model (one station = pack share + ESC + SunnySky X3108S KV900 + APC prop), pure standard library:
  prop    T = kT Ct(J) rho n^2 D^4 ,  P = kP Cp(J) rho n^3 D^5         APC PER3 blade-element data (tables below)
  motor   V_m = w / Kv + I_m R_m ,  I_m = Q / Kt + I0 ,  Kt = 1 / Kv   (SI units, Kv in rad/s/V)
  ESC     V_m = d V_bus - I_m R_esc ,  P_bat = V_m I_m + I_m^2 R_esc + P_esc0
  pack    V_bus = V_ocv - R_pack * (sum of station battery currents + avionics)
kT and kP are fitted to the maker's own X3108S KV900 + APC 11x4.7 table (rows <= 16 A, where the maker's supply
did not sag) against the PER3 file of that same prop (CALC-E1-CAL). The fitted factors are then applied to the
11x4.5MR / 11x5.5MR PER3 files (ASM-E1-CAL-TRANSFER). The H1 thrust stand replaces all of this (T-E1-STAND).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
MOTORS = ["PRP-901", "PRP-902", "PRP-903", "PRP-904"]       # skeleton ids UR UL LR LL (fusion/skeleton/propulsion)

# ================================================================== catalogue data (verbatim, cited)
# SunnySky X3108S KV900 + APC "1147" (11x4.7), 14.8 V: [battery A, thrust gf, rpm, input W]; 94 degC after the 30 A row.
# Read from the maker's data image 2026-11-09 (SRC-E1-X3108S-DATA).
MAKER_1147 = [
    [1, 230, 2914, 15], [2, 340, 3575, 30], [3, 440, 4071, 44], [4, 530, 4451, 59], [5, 610, 4705, 74],
    [6, 690, 4970, 89], [7, 750, 5228, 104], [8, 810, 5400, 118], [9, 870, 5588, 133], [10, 920, 5777, 148],
    [12, 1010, 6034, 178], [14, 1110, 6317, 207], [16, 1190, 6530, 237], [18, 1260, 6720, 266],
    [20, 1330, 6940, 296], [23, 1410, 7140, 340], [26, 1490, 7300, 385], [30, 1580, 7500, 447]]
MAKER_TEMP_C = 94.0          # maker's temperature column at the 30 A row
CAL_ROWS_A = (5, 12)         # rows used for the fit. The W column is 14.8 V x A with A in whole-amp steps, so rows
                             # < 5 A carry > 10 % rounding error and rows > 12 A are taken at a sagging supply
                             # (CL-E1-MAKER-SUPPLY); between them both errors are small

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
PROP_D = {"11x4.7SF": 0.2794, "11x4.5MR": 0.2794, "11x5.5MR": 0.2794, "12x4.5MR": 0.3048}
CANDIDATES = ["11x4.5MR", "11x5.5MR", "12x4.5MR"]


# ================================================================== sources and assumptions
kit.source("SRC-E1-X3108S-DATA", "SunnySky X3108S KV900 data image (11x4.7 and 10x3.8 at 14.8 V)", "datasheet",
           url="https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg",
           checked="2026-11-09", where="table APC1147 14.8 V, 18 rows, temperature 94 degC at 30 A",
           note="full table transcribed into MAKER_1147 in propulsion.py; product page "
                "https://sunnyskyusa.com/products/sunnysky-x3108s-motors returned HTTP 429 on 2026-11-09, "
                "price $24.99 from docs/research/budget-lift.md (seen 2026-11-01)")
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
kit.source("SRC-E1-TEKKO32", "Holybro Tekko32 F4 45A single ESC (AM32), ReadyMadeRC", "listing",
           url="https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32",
           checked="2026-11-09", where="$22.50, 45 A cont, 2-6S, AM32, current sensor, 5.8 g, 16 AWG; backorder to Dec 2026")

kit.assumption("ASM-E1-KV", "Motor Kv 900 rpm/V", "X3108S KV900 speed constant", basis="maker name and listing; the "
               "maker table's rpm at low throttle is consistent with it (CALC-E1-CAL residuals)", value=900.0,
               unit="rpm/V", cites=["SRC-E1-X3108S-SPEC", "SRC-E1-X3108S-DATA"])
kit.assumption("ASM-E1-RM", "Winding resistance 86 mOhm at 25 degC", "phase-to-phase resistance of the X3108S KV900",
               basis="two retailer listings agree (Robu, HiModel); measure with a 4-wire milliohm method on arrival",
               value=0.086, unit="ohm", status="UNVERIFIED", cites=["SRC-E1-X3108S-SPEC", "SRC-E1-X3108S-HIMODEL"])
kit.assumption("ASM-E1-I0", "No-load current 0.9 A", "no-load current, used as speed-independent iron + friction loss",
               basis="listing value at 10 V (~9 000 rpm), two listings agree: conservative below that speed", value=0.9,
               unit="A", status="UNVERIFIED", cites=["SRC-E1-X3108S-SPEC", "SRC-E1-X3108S-HIMODEL"])
kit.assumption("ASM-E1-ESC", "ESC loss 10 mOhm + 0.5 W", "ESC conduction path 10 mOhm (two FETs + leads) and 0.5 W fixed",
               basis="typical BLHeli_S 45 A FETs 3-4 mOhm each; the fit factor kP absorbs any error at the "
                     "calibration points", value=[0.010, 0.5], unit="ohm,W")
kit.assumption("ASM-E1-PACK", "Pack + harness 24 mOhm, avionics 1 A", "4S 6500 130C pack 20 mOhm (5 mOhm/cell, part-"
               "aged) plus 4 mOhm main lead and connector; avionics + servos 1 A from the bus",
               basis="E2 measures pack IR with the charger; F1 owns the harness resistance", value=[0.024, 1.0],
               unit="ohm,A", status="UNVERIFIED")
kit.assumption("ASM-E1-OCV", "Pack OCV states", "open-circuit pack voltage: full 4.20, mid 3.80, low 3.60 V/cell (4S)",
               basis="3.60 V/cell OCV is the 20 % reserve point of a LiPo; the sag case uses it", value=[16.8, 15.2, 14.4],
               unit="V")
kit.assumption("ASM-E1-TCOPPER", "Copper 0.393 %/K, hot winding 80 degC", "R_m(T) = R_25 (1 + 0.00393 (T - 25)); "
               "thrust-limit cases use an 80 degC winding, current-limit cases 25 degC",
               basis="annealed copper coefficient; 80 degC = hot after a hover", value=[0.00393, 80.0], unit="1/K,degC")
kit.assumption("ASM-E1-CAL-TRANSFER", "PER3-to-measured factors transfer between APC 11 in props",
               "kT, kP fitted on the 11x4.7SF apply to the 11x4.5MR / 11x5.5MR PER3 data",
               basis="same maker, same code, same diameter; H1's thrust stand (T-E1-STAND) measures the fitted prop "
                     "directly and supersedes this", status="UNVERIFIED")
kit.assumption("ASM-E1-RTH", "Motor thermal resistance 1.0 K/W in own wash", "steady winding-to-ambient resistance of the "
               "X3108S in its own static prop wash", basis="maker's 94 degC at the 30 A row, 25 degC room, losses from this "
               "model (CALC-E1-CAL); the test was not steady, so the true value may be higher: E3 owns the thermal model",
               value=1.0, unit="K/W", status="UNVERIFIED", cites=["SRC-E1-X3108S-DATA"])
kit.assumption("ASM-E1-ILIM", "Pack-current limit 100 A", "ArduPilot Q_M_BAT_CURR_MAX = 100 A (with the power "
               "module's current sensor calibrated) caps the summed motor current",
               basis="4 x 25 A = the X3108S's 25 A / 30 s rating; F4 sets it, F1 sizes wiring to it", value=100.0, unit="A")
kit.assumption("ASM-E1-TRANS-MARGIN", "Transition thrust margin 1.3", "full thrust at every point of the level "
               "pitch-over corridor >= 1.3 x the thrust that holds level unaccelerated flight there",
               basis="0.3 g of surplus for acceleration and gusts; same headroom as ASM-A2-GUST-THRUST-HEADROOM",
               value=1.3, unit="-")
kit.assumption("ASM-E1-POSTSTALL", "Wing CL: linear to CLmax, flat plate after stall", "CL = a alpha up to CLmax "
               "(a = 2 pi AR/(AR+2)); above stall CN = 1.98 sin(alpha) (flat plate); prop wash on the wing ignored",
               basis="Hoerner flat-plate normal force; ignoring wash lift is conservative for thrust required; B1/B2 refine")
kit.assumption("ASM-E1-WORST-STATE", "Worst pack state for hover T/W", "the lowest pack state the aircraft is flown in: "
               "the 20 % reserve line (E2 ASM-E2-OCV-20), pack cold-soaked to 10 degC (E2 ASM-E2-COLD-R), windings hot "
               "(80 degC, after a hover), 100 A limiter set; pack resistance = cells x R_cell x cold + R_ext (E2's model)",
               basis="one definition shared with E2 (CR-E2/E1 reconciliation 2026-11-09); the battery failsafe lands "
                     "the aircraft at the reserve line, so states below it are emergencies, reported as a sensitivity "
                     "(3.60 V/cell OCV)", value=[80.0, 3.60], unit="degC,V")
kit.assumption("ASM-E1-STACK", "Prop stack dimensions", "motor body (mount face to bell top) 26.5 mm; bolt-on adapter "
               "base 6.35 mm, M6x1 post 15.2 mm above the base; prop hub 0.35 in = 8.89 mm; M6 washer 1.0 mm; M6 hex "
               "nut ISO 4032 5.2 mm", basis="HiModel listing (body), Small Parts CNC adapter drawing values, APC 11x5.5MR "
               "page (hub), ISO 4032 / ISO 7089 (nut, washer); measure the supplied adapter on arrival",
               value=[0.0265, 0.00635, 0.0152, 0.00889, 0.0010, 0.0052], unit="m", status="UNVERIFIED",
               cites=["SRC-E1-X3108S-HIMODEL", "SRC-E1-SPCNC-ADAPTER", "SRC-E1-APC-PAGES"])
kit.assumption("ASM-E1-MOUNT-SCREW", "Motor-to-mount screw stack", "D3 mount plate 5.0 mm thick at the screw bosses, "
               "no washer, M3x8 SHCS (A2 stainless, same size as the old design's F01); thread engagement in the motor "
               "base 2.5-3.5 mm (>= 5 threads, tip clear of the stator)",
               basis="X3108S base thread depth is not published: 3.5 mm is a conservative limit for a 31 mm stator "
                     "base; probe the hole depth on arrival, the screw tip must stop >= 0.5 mm short of the bottom",
               value=[0.0050, 0.008, 0.0025, 0.0035], unit="m", status="UNVERIFIED")
kit.assumption("ASM-E1-PART-MASS", "Per-unit flying masses incl. leads, g", "motor with factory leads 81.0 (no bullets: "
               "harness HRN-E03); ESC with factory power and signal leads and heat-shrink 11.0 (6.6 g bare board + "
               "2 x 80 mm 16 AWG + signal lead + shrink); prop 17.0; bolt-on adapter 3.0 + 4 x M3x4 1.2 + M6 nut 1.9 + "
               "washer 0.6 = 6.7; 4 x M3x8 SHCS motor screws 3.2",
               basis="listings (81 g, 17 g, 3.0 g); ISO masses for screws, nuts, washers; the ESC with leads is EST "
                     "from the 6.6 g bare board and 14 g/m 16 AWG silicone (A3 HRN-E01); weigh everything on arrival",
               value={"motor": 81.0, "esc": 11.0, "prop": 17.0, "adapter_nut": 6.7, "motor_screws": 3.2}, unit="g",
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
        res.append({"A": r[0], "T_err": s["T_N"] / (r[1] * 9.80665e-3) - 1, "P_err": s["P_bat_W"] / r[3] - 1,
                    "v_supply_min": v_sup, "loss_W": s["P_loss_motor_W"]})
    return kT, kP, res


# ================================================================== calculations (claims)
@kit.calc("CALC-E1-CAL", title="Fit PER3 to the maker's X3108S + 11x4.7 table",
          equation="kT = mean(T_meas / T_PER3(rpm)) ; kP: sum(P_bat,model(rpm) - P_meas) = 0 over rows 5-12 A ; "
                   "R_th = (94 - 25) / P_loss(30 A row)",
          inputs={"rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC"},
          units={"rho": "kg/m3", "kv": "rpm/V", "rm": "ohm", "i0": "A"},
          assumes=["ASM-E1-KV", "ASM-E1-RM", "ASM-E1-I0", "ASM-E1-ESC"], cites=["SRC-E1-X3108S-DATA", "SRC-E1-APC-PER3"])
def cal(rho, kv, rm, i0, esc):
    kT, kP, res = calibrate(rho, kv, rm, i0, esc)
    fit = [r for r in res if CAL_ROWS_A[0] <= r["A"] <= CAL_ROWS_A[1]]
    top = res[-1]
    return {"kT": kT, "kP": kP,
            "T_err_rms": math.sqrt(sum(r["T_err"] ** 2 for r in fit) / len(fit)),
            "P_err_rms": math.sqrt(sum(r["P_err"] ** 2 for r in fit) / len(fit)),
            "P_err_max": max(abs(r["P_err"]) for r in fit),
            "v_supply_30A": top["v_supply_min"], "loss_30A_W": top["loss_W"],
            "rth_KW": (MAKER_TEMP_C - 25.0) / top["loss_W"]}


@kit.calc("CALC-E1-HOVER", title="Hover operating point per motor, 11x4.5MR and 11x5.5MR",
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
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55")):
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
          equation="duty = 1 ; V_bus = V_ocv - R_pack (4 I_bat + I_avn) ; T/W = 4 T_max / (m_gate g) ; "
                   "cases: table basis (bus held 14.8 V, 25 degC), sag (OCV 14.4 V, R_pack, 80 degC), "
                   "current limits (bus held 14.8 / 16.8 V, 25 degC)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK", "ocv": "ASM-E1-OCV",
                  "tc": "ASM-E1-TCOPPER"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E1-PACK"], cites=["SRC-E1-APC-PER3"])
def full(m, g, n, rho, kP, kT, kv, rm, i0, esc, pack, ocv, tc):
    W = m * g
    out = {}
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55"), ("12x4.5MR", "12")):
        a = (prop, 0.0, rho, kT, kP, kv)
        tb = full_throttle(*a, rm, i0, esc[0], esc[1], 14.8, 0.0, pack[1], n)
        sg = full_throttle(*a, r_hot(rm, tc[0], tc[1]), i0, esc[0], esc[1], ocv[2], pack[0], pack[1], n)
        hi = full_throttle(*a, rm, i0, esc[0], esc[1], 16.8, 0.0, pack[1], n)
        out[f"tw_table_{tag}"] = n * tb["T_N"] / W
        out[f"tw_sag_{tag}"] = n * sg["T_N"] / W
        out[f"Tmax_table_{tag}_gf"] = tb["T_N"] / g * 1000
        out[f"Tmax_sag_{tag}_gf"] = sg["T_N"] / g * 1000
        out[f"I_148_{tag}_A"] = tb["I_bat_A"]
        out[f"I_168_{tag}_A"] = hi["I_bat_A"]
        out[f"P_148_{tag}_W"] = tb["P_bat_W"]
        out[f"Ipack_sag_{tag}_A"] = n * sg["I_bat_A"] + pack[1]
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
    d = bisect(f, 0.3, 1.0, n=40)
    s = full_throttle(prop, 0.0, rho, kT, kP, kv, rm, i0, esc[0], esc[1], v_ocv, r_pack, i_avn, n, duty_max=d)
    s["duty_max"] = d
    return s


@kit.calc("CALC-E1-LIMIT", title="Full throttle with the pack-current limiter Q_M_BAT_CURR_MAX",
          equation="largest duty with 4 I_bat + I_avn <= I_lim ; T/W = 4 T / (m_gate g) ; cases fresh (OCV 16.8 V, "
                   "25 degC) and low (OCV 14.4 V, 80 degC), with R_pack",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK", "ocv": "ASM-E1-OCV",
                  "tc": "ASM-E1-TCOPPER", "ilim": "ASM-E1-ILIM"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "ilim": "A"},
          assumes=["ASM-E1-CAL-TRANSFER", "ASM-E1-PACK", "ASM-E1-ILIM"])
def limit_calc(m, g, n, rho, kP, kT, kv, rm, i0, esc, pack, ocv, tc, ilim):
    W = m * g
    out = {}
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55")):
        fr = limited(prop, rho, kT, kP, kv, rm, i0, esc, ocv[0], pack[0], pack[1], n, ilim)
        lo = limited(prop, rho, kT, kP, kv, r_hot(rm, tc[0], tc[1]), i0, esc, ocv[2], pack[0], pack[1], n, ilim)
        out[f"I_motor_fresh_{tag}_A"] = fr["I_bat_A"]
        out[f"tw_fresh_{tag}"] = n * fr["T_N"] / W
        out[f"tw_low_{tag}"] = n * lo["T_N"] / W
        out[f"I_motor_low_{tag}_A"] = lo["I_bat_A"]
    return out


@kit.calc("CALC-E1-WORST", title="Hover T/W at the worst pack state (E1 station model + E2 pack model)",
          equation="R_pack = cells R_cell k_cold + R_ext ; V_ocv = cells OCV ; largest duty with 4 I_bat + I_avn <= I_lim "
                   "(station model, winding 80 degC) ; T/W = 4 T cos(cant) / (m_gate g) ; "
                   "f_sag = T_worst / T_fresh (fresh: 4.20 V/cell, warm R, 25 degC)",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "n": P + "propulsion.n_motors",
                  "rho": P + "env.rho_kgm3", "cant": P + "propulsion.stations.cant_deg", "cells": P + "battery.cells_s",
                  "kP": "CL-E1-KP", "kT": "CL-E1-KT", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0",
                  "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK", "tc": "ASM-E1-TCOPPER", "ilim": "ASM-E1-ILIM",
                  "state": "ASM-E1-WORST-STATE", "ocv20": "ASM-E2-OCV-20", "r_cell": "ASM-E2-R-CELL",
                  "r_ext": "ASM-E2-R-EXT", "cold": "ASM-E2-COLD-R"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "cant": "deg", "ilim": "A", "ocv20": "V", "r_cell": "ohm",
                 "r_ext": "ohm"},
          assumes=["ASM-E1-WORST-STATE", "ASM-E1-CAL-TRANSFER", "ASM-E1-ILIM", "ASM-E2-OCV-20", "ASM-E2-R-CELL",
                   "ASM-E2-R-EXT", "ASM-E2-COLD-R"])
def worst(m, g, n, rho, cant, cells, kP, kT, kv, rm, i0, esc, pack, tc, ilim, state, ocv20, r_cell, r_ext, cold):
    W = m * g
    cc = math.cos(math.radians(cant))
    r_warm = cells * r_cell + r_ext
    r_cold = cells * r_cell * cold + r_ext
    rm_hot = r_hot(rm, tc[0], state[0])
    prop = "11x5.5MR"
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
        out[f"limited_{k}"] = 1.0 if "duty_max" in s else 0.0
    out["f_sag"] = out["T_worst_gf"] / out["T_fresh_gf"]
    out["f_sag_land"] = out["T_land_cold_gf"] / out["T_fresh_gf"]
    return out


@kit.calc("CALC-E1-STACK", title="Prop stack: mount face to prop plane, nut engagement, motor screws",
          equation="x_hub = L_body + t_base + h_hub / 2 ; x_tip = L_body + t_base + L_post ; "
                   "e_nut = L_post - h_hub - t_washer >= h_nut ; e_screw = L_screw - t_plate",
          inputs={"st": "ASM-E1-STACK", "sc": "ASM-E1-MOUNT-SCREW"}, assumes=["ASM-E1-STACK", "ASM-E1-MOUNT-SCREW"])
def stack(st, sc):
    body, base, post, hub, wash, nut = st
    t_plate, l_screw, e_min, e_max = sc
    return {"mount_to_prop_plane_m": body + base + hub / 2, "mount_to_hub_front_m": body + base + hub,
            "mount_to_post_tip_m": body + base + post, "hub_half_m": hub / 2,
            "nut_engagement_m": post - hub - wash, "nut_margin_m": post - hub - wash - nut,
            "screw_engagement_m": l_screw - t_plate, "screw_margin_m": min(l_screw - t_plate - e_min,
                                                                           e_max - (l_screw - t_plate))}


@kit.calc("CALC-E1-MASS", title="Propulsion flying mass, four stations, per-unit masses incl. leads",
          equation="m = n (motor + ESC + prop + adapter and nut + motor screws)",
          inputs={"pm": "ASM-E1-PART-MASS", "n": P + "propulsion.n_motors"}, units={"pm": "g"},
          assumes=["ASM-E1-PART-MASS"])
def mass(pm, n):
    station = sum(pm.values())
    return {"station_g": station, "total_g": n * station,
            "total_ex_screws_g": n * (station - pm["motor_screws"])}


def cruise_drag(V, m, g, rho, S, b, e, ld_ref, v_ref):
    """Parabolic polar anchored on the cruise L/D at v_ref (params): CD0 from that point, K = 1/(pi e AR)."""
    AR = b * b / S
    K = 1 / (math.pi * e * AR)
    W = m * g
    cl_ref = 2 * W / (rho * v_ref ** 2 * S)
    cd0 = cl_ref / ld_ref - K * cl_ref ** 2
    cl = 2 * W / (rho * V * V * S)
    return 0.5 * rho * V * V * S * (cd0 + K * cl * cl), cd0


@kit.calc("CALC-E1-CRUISE", title="Cruise point: four props share the drag at 15 m/s",
          equation="D = q S (CD0 + K CL^2), CD0 from L/D 5.9 at 15 m/s ; T_m = D / 4 ; solve rpm: T(rpm, J) = T_m ; "
                   "eta_prop = T V / P_shaft ; eta_tot = T V / P_bat",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "b": P + "wing.span_m", "c": P + "wing.chord_m", "e": P + "wing.oswald_e", "ld": P + "performance.ld_cruise",
                  "V": P + "performance.cruise_ms", "n": P + "propulsion.n_motors", "kP": "CL-E1-KP", "kT": "CL-E1-KT",
                  "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "V": "m/s", "b": "m", "c": "m"},
          assumes=["ASM-E1-CAL-TRANSFER"], cites=["SRC-E1-APC-PER3"])
def cruise(m, g, rho, b, c, e, ld, V, n, kP, kT, kv, rm, i0, esc):
    S = b * c
    D, cd0 = cruise_drag(V, m, g, rho, S, b, e, ld, V)
    T = D / n
    out = {"drag_N": D, "T_per_motor_N": T, "cd0": cd0}
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55"), ("12x4.5MR", "12")):
        s = at_thrust(prop, T, V, rho, 1.0, kP, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
        out[f"J_{tag}"] = s["J"]
        out[f"rpm_{tag}"] = s["rpm"]
        out[f"eta_prop_{tag}"] = T * V / s["P_shaft_W"]
        out[f"eta_motor_{tag}"] = s["P_shaft_W"] / s["P_motor_in_W"]
        out[f"eta_tot_{tag}"] = T * V / s["P_bat_W"]
        out[f"P_total_{tag}_W"] = n * s["P_bat_W"]
        out[f"I_pack_{tag}_A"] = n * s["I_bat_A"]
        out[f"I_m_{tag}_A"] = s["I_m_A"]
        out[f"loss_motor_{tag}_W"] = s["P_loss_motor_W"]
        out[f"Q_{tag}_Nm"] = s["P_shaft_W"] / (s["rpm"] * 2 * math.pi / 60)
    return out




def wing_cl_cd(alpha, cla, clmax, cd0, K):
    a_s = clmax / cla
    if alpha <= a_s:
        cl = cla * alpha
        return cl, cd0 + K * cl * cl
    cn = 1.98 * math.sin(alpha)
    return cn * math.cos(alpha), cd0 + cn * math.sin(alpha)


def corridor(prop, m, g, rho, S, b, e, ld, vref, clmax, v_end, kT, kP, kv, rm, i0, esc, pack, ocv, n, steps=30):
    """Level pitch-over corridor: at each V find the body angle alpha (thrust axis above horizontal) that needs the
    least thrust for level unaccelerated flight, and the full thrust available there (axial inflow V cos alpha)."""
    AR = b * b / S
    cla = 2 * math.pi * AR / (AR + 2)
    K = 1 / (math.pi * e * AR)
    W = m * g
    _, cd0 = cruise_drag(vref, m, g, rho, S, b, e, ld, vref)
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


@kit.calc("CALC-E1-CORRIDOR", title="Thrust margin along the level pitch-over corridor (sag case, 11x4.5MR and 11x5.5MR)",
          equation="min over V in [0, 1.3 Vs] of 4 T_full(V cos a, OCV 14.4 V, 80 degC) / T_req,min(V) ; "
                   "T_req from T sin a + L = W, T cos a >= D",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3",
                  "b": P + "wing.span_m", "c": P + "wing.chord_m", "e": P + "wing.oswald_e", "ld": P + "performance.ld_cruise",
                  "vref": P + "performance.cruise_ms", "clmax": P + "performance.clmax",
                  "vtr": P + "performance.transition_min_ms", "n": P + "propulsion.n_motors", "kP": "CL-E1-KP",
                  "kv": "ASM-E1-KV", "rm": "ASM-E1-RM", "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC", "pack": "ASM-E1-PACK",
                  "ocv": "ASM-E1-OCV"},
          units={"m": "kg", "g": "m/s2", "rho": "kg/m3", "vref": "m/s", "vtr": "m/s", "b": "m", "c": "m"},
          assumes=["ASM-E1-POSTSTALL", "ASM-E1-CAL-TRANSFER", "ASM-E1-PACK"])
def corridor_calc(m, g, rho, b, c, e, ld, vref, clmax, vtr, n, kP, kv, rm, i0, esc, pack, ocv):
    S = b * c
    out = {}
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55")):
        worst, _ = corridor(prop, m, g, rho, S, b, e, ld, vref, clmax, vtr, 1.0, kP, kv, rm, i0, esc, pack, ocv, n)
        out[f"margin_{tag}"] = worst[3]
        out[f"V_worst_{tag}_ms"] = worst[0]
        out[f"Treq_over_W_{tag}"] = worst[2]
    return out


@kit.calc("CALC-E1-MOTOR-OUT", title="One motor out: what is left (11x5.5MR)",
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
    pr = "11x5.5MR"
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


@kit.calc("CALC-E1-SENS", title="Lower bound: pure PER3 power (kP = 1)",
          equation="as CALC-E1-HOVER and CALC-E1-CRUISE with kP = 1, kT = 1",
          inputs={"Th": "CL-E1-HOVER-T", "Tc": "CL-E1-CRUISE-DRAG", "V": P + "performance.cruise_ms",
                  "n": P + "propulsion.n_motors", "rho": P + "env.rho_kgm3", "kv": "ASM-E1-KV", "rm": "ASM-E1-RM",
                  "i0": "ASM-E1-I0", "esc": "ASM-E1-ESC"},
          units={"Th": "N", "Tc": "N", "V": "m/s", "rho": "kg/m3"})
def sens(Th, Tc, V, n, rho, kv, rm, i0, esc):
    out = {}
    for prop, tag in (("11x4.5MR", "45"), ("11x5.5MR", "55")):
        h = at_thrust(prop, Th, 0.0, rho, 1.0, 1.0, kv, r_hot(rm, 0.00393, 50.0), i0, esc[0], esc[1], 14.8)
        c = at_thrust(prop, Tc / n, V, rho, 1.0, 1.0, kv, r_hot(rm, 0.00393, 40.0), i0, esc[0], esc[1], 14.8)
        out[f"P_hover_{tag}_W"] = n * h["P_bat_W"]
        out[f"P_cruise_{tag}_W"] = n * c["P_bat_W"]
    return out


# ================================================================== claims
kit.claim("CL-E1-KT", "PER3 thrust factor kT (fit)", calc="CALC-E1-CAL", output="kT", unit="-",
          how="Re-run; compare with T-E1-STAND rows (thrust vs rpm) for the fitted prop.")
kit.claim("CL-E1-KP", "PER3 power factor kP (fit)", calc="CALC-E1-CAL", output="kP", unit="-",
          how="Re-run; the rms power error on the fitted rows is printed (CALC-E1-CAL P_err_rms).")
kit.claim("CL-E1-CAL-PERR", "Model power error on the maker rows", calc="CALC-E1-CAL", output="P_err_max", unit="-",
          limit=("<=", 0.10), how="Max |P_model / P_maker - 1| over the 7 rows 5-12 A; re-run the script.")
kit.claim("CL-E1-MAKER-SUPPLY", "Maker's supply at the 30 A row (inferred)", calc="CALC-E1-CAL", output="v_supply_30A",
          unit="V", note="the maker's 1 580 gf top row is reachable only with ~11 V at the motor: the table's 447 W is "
          "14.8 V x 30 A bookkeeping, not a measurement at 14.8 V",
          how="Thrust stand at a held 14.8 V bench supply: full-throttle rpm should exceed 7 500 (T-E1-STAND).")
kit.claim("CL-E1-HOVER-T", "Hover thrust per motor at the gate", calc="CALC-E1-HOVER", output="T_per_motor_N", unit="N",
          parts=MOTORS, how="m_gate g k_download / 4; compare with the tethered-hover throttle and log.")
kit.claim("CL-E1-HOVER-I", "Hover pack current, 11x4.5MR, 14.8 V", calc="CALC-E1-HOVER", output="I_pack_45_A", unit="A",
          limit=("<=", 27.6), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="Log battery current in a 30 s tethered hover at 2.6 kg; within 24 A +/- 15 % (limit 27.6 A).")
kit.claim("CL-E1-HOVER-I-55", "Hover pack current, 11x5.5MR, 14.8 V", calc="CALC-E1-HOVER", output="I_pack_55_A",
          unit="A", limit=("<=", 27.6), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="As CL-E1-HOVER-I with the 11x5.5MR fitted.")
kit.claim("CL-E1-HOVER-GW", "Hover efficiency, 11x4.5MR", calc="CALC-E1-HOVER", output="gW_45", unit="gf/W",
          how="Thrust stand: gf / W at 689 gf (T-E1-STAND).")
kit.claim("CL-E1-HOVER-DT", "Hover winding temperature rise", calc="CALC-E1-HOVER", output="dT_wind_45_K", unit="K",
          limit=("<=", 50.0), verifies=["R-THERMAL"], parts=MOTORS,
          how="IR thermometer on the can after a 2 min tethered hover; E3 owns the limit (80 degC can at 30 degC ambient).")
kit.claim("CL-E1-TW-TABLE", "Hover T/W at the gate, 11x4.5MR, bus 14.8 V", calc="CALC-E1-FULL", output="tw_table_45",
          unit="-", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"], parts=MOTORS,
          how="Thrust stand at a held 14.8 V: full-throttle thrust >= 1 300 gf per motor (T-E1-STAND).")
kit.claim("CL-E1-IMAX-148", "Full-throttle current per motor at 14.8 V, 11x4.5MR", calc="CALC-E1-FULL",
          output="I_148_45_A", unit="A", limit=("<=", 36.0), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="Thrust stand at a held 14.8 V, 3 s full throttle, clamp meter on the ESC lead.")
kit.claim("CL-E1-IMAX-168", "Full-throttle current per motor at 16.8 V, 11x4.5MR", calc="CALC-E1-FULL",
          output="I_168_45_A", unit="A", limit=("<=", 45.0), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="Thrust stand on a fresh pack (16.8 V), 2 s full throttle.")
kit.claim("CL-E1-IMAX-168-55", "Full-throttle current per motor at 16.8 V, 11x5.5MR", calc="CALC-E1-FULL",
          output="I_168_55_A", unit="A", limit=("<=", 45.0), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="As CL-E1-IMAX-168 with the 11x5.5MR.")
kit.claim("CL-E1-IMAX-148-55", "Full-throttle current per motor at 14.8 V, 11x5.5MR", calc="CALC-E1-FULL",
          output="I_148_55_A", unit="A", limit=("<=", 36.0), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="As CL-E1-IMAX-148 with the 11x5.5MR.")
kit.claim("CL-E1-IPACK-PEAK", "Peak pack current, all four full throttle (sag case)", calc="CALC-E1-FULL",
          output="Ipack_sag_45_A", unit="A", parts=MOTORS,
          how="F1 sizes the disconnect and main leads on this (replaces params 120 A); log on the stand with 4 motors.")
kit.claim("CL-E1-ILIM-I", "Per-motor current with the 100 A limiter, fresh pack, 11x5.5MR", calc="CALC-E1-LIMIT",
          output="I_motor_fresh_55_A", unit="A", limit=("<=", 25.0), verifies=["R-ESC-CURRENT"], parts=MOTORS,
          how="Bench: all four motors, props on, fresh pack, full throttle 2 s in QSTABILIZE on a restrained frame; "
              "dataflash BAT.Curr <= 100 A.")
kit.claim("CL-E1-ILIM-TW-FRESH", "T/W with the limiter, fresh pack, 11x5.5MR", calc="CALC-E1-LIMIT",
          output="tw_fresh_55", unit="-", limit=(">=", P + "requirements.hover_tw_min"), verifies=["R-HOVER-TW"],
          parts=MOTORS, how="Thrust stand on a fresh pack with the duty limit found on the bench.")
kit.claim("CL-E1-CRUISE-DRAG", "Cruise drag at 15 m/s, gate mass", calc="CALC-E1-CRUISE", output="drag_N", unit="N",
          how="B1 owns the polar; this is W / (L/D) from params.json.")
kit.claim("CL-E1-CRUISE-P-45", "Cruise electrical power, 11x4.5MR (stand A/B prop, not flown)", calc="CALC-E1-CRUISE",
          output="P_total_45_W", unit="W", parts=MOTORS, note="comparison only since D-05; no requirement link",
          how="Log pack power in steady 15 m/s FBWA legs, both directions, calm morning.")
kit.claim("CL-E1-CRUISE-P-55", "Cruise electrical power, 11x5.5MR", calc="CALC-E1-CRUISE", output="P_total_55_W",
          unit="W", limit=("<=", P + "performance.cruise_power_w"), verifies=["R-MISSION"], parts=MOTORS,
          how="As CL-E1-CRUISE-P-45 with the 11x5.5MR.")
kit.claim("CL-E1-CRUISE-P-55-LO", "Cruise power lower bound (kP = 1), 11x5.5MR", calc="CALC-E1-SENS",
          output="P_cruise_55_W", unit="W", how="Bounds the band with CL-E1-CRUISE-P-55; flight log decides.")
kit.claim("CL-E1-CRUISE-P-45-LO", "Cruise power lower bound (kP = 1), 11x4.5MR", calc="CALC-E1-SENS",
          output="P_cruise_45_W", unit="W", how="Bounds the band with CL-E1-CRUISE-P-45; flight log decides.")
kit.claim("CL-E1-CRUISE-ETA-45", "Cruise prop efficiency, 11x4.5MR", calc="CALC-E1-CRUISE", output="eta_prop_45",
          unit="-", how="PER3 at J of the cruise point; check with logged rpm (bidirectional DShot) and power.")
kit.claim("CL-E1-CRUISE-ETA-55", "Cruise prop efficiency, 11x5.5MR", calc="CALC-E1-CRUISE", output="eta_prop_55",
          unit="-", how="As CL-E1-CRUISE-ETA-45.")
kit.claim("CL-E1-CORRIDOR-45", "Transition thrust margin, 11x4.5MR", calc="CALC-E1-CORRIDOR", output="margin_45",
          unit="-", limit=(">=", "ASM-E1-TRANS-MARGIN"), verifies=["R-TRANSITION"], parts=MOTORS,
          how="B1 replaces the wing model with AVL/XFOIL post-stall data; flight log of throttle during the first transition.")
kit.claim("CL-E1-CORRIDOR-55", "Transition thrust margin, 11x5.5MR", calc="CALC-E1-CORRIDOR", output="margin_55",
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
          how="B3 compares with elevon roll authority at 15 m/s (CR-E1-04).")

kit.claim("CL-E1-TW-WORST", "Hover T/W at the gate, worst pack state (one team claim, E1 + E2)", calc="CALC-E1-WORST",
          output="tw_worst", unit="-", limit=(">=", P + "requirements.hover_tw_min_sag"), verifies=["R-HOVER-TW"],
          parts=MOTORS, note="replaces CL-E1-TW-SAG, CL-E1-TW-SAG-55, CL-E1-ILIM-TW-LOW and, by agreement requested "
          "in CR-E1-15, CL-E2-TW-SAG-WORST: 11x5.5MR, 20 % charge, 10 degC pack, 80 degC winding, 100 A limiter",
          how="Thrust stand on a flight pack discharged to 3.73 V/cell rest and cold-soaked to 10 degC, motor warmed by "
              "a 2 min run at hover thrust, full throttle with the 25 A per-motor duty cap: thrust x 4 x cos 3 deg / "
              "2.6 kg (T-E1-STAND).")
kit.claim("CL-E1-SAG-FACTOR", "Thrust factor worst / fresh with the limiter (replaces params voltage_sag)",
          calc="CALC-E1-WORST", output="f_sag", unit="-",
          note="to be applied to thrust_max_per_motor_kg (fresh pack, limiter); E2's 0.76 applied (V/14.8)^2 to "
               "that already current-limited thrust, which double-counts",
          how="Ratio of the two T-E1-STAND full-throttle runs: worst-state pack / fresh pack.")
kit.claim("CL-E1-TMAX-WORST", "Full thrust per motor, worst pack state, 11x5.5MR", calc="CALC-E1-WORST",
          output="T_worst_gf", unit="gf", parts=MOTORS, how="As CL-E1-TW-WORST, per motor.")
kit.claim("CL-E1-TW-LAND-COLD", "Hover T/W below the reserve line (3.60 V/cell, cold), sensitivity",
          calc="CALC-E1-WORST", output="tw_land_cold", unit="-", limit=(">=", 1.3), parts=MOTORS,
          how="Same stand run on a pack at 3.60 V/cell rest; 1.3 is the emergency-landing floor, not R-HOVER-TW.")
kit.claim("CL-E1-STACK-PROP-PLANE", "Mount face to prop mid-plane (hub centre)", calc="CALC-E1-STACK",
          output="mount_to_prop_plane_m", unit="m", parts=MOTORS,
          how="Calipers on the assembled station: mount face to hub front face minus half the hub (8.9 / 2 mm).")
kit.claim("CL-E1-STACK-POST-TIP", "Mount face to adapter post tip (rotating envelope end)", calc="CALC-E1-STACK",
          output="mount_to_post_tip_m", unit="m", parts=MOTORS, how="Calipers on the assembled station.")
kit.claim("CL-E1-NUT-ENGAGE", "M6 nut thread engagement margin over full nut height", calc="CALC-E1-STACK",
          output="nut_margin_m", unit="m", limit=(">=", 0.0), parts=MOTORS,
          how="Assemble prop, washer and nut: the post end must be flush with or proud of the nut face.")
kit.claim("CL-E1-SCREW-ENGAGE", "Motor screw engagement inside the 2.5-3.5 mm window", calc="CALC-E1-STACK",
          output="screw_margin_m", unit="m", limit=(">=", 0.0), parts=MOTORS,
          how="Probe each base hole depth with a 2 mm drill shank; M3x8 through the 5.0 mm plate leaves the tip >= 0.5 mm "
              "short of the bottom (T-E1-MOTOR-RM incoming check).")
kit.claim("CL-E1-MASS-PRP", "Propulsion flying mass, four stations incl. leads, adapters and motor screws",
          calc="CALC-E1-MASS", output="total_g", unit="g", limit=("<=", P + "mass.allocation_g.propulsion"),
          parts=MOTORS, how="Weigh each part on the 0.1 g scale on arrival (one of each), update ASM-E1-PART-MASS, re-run.")

kit.test("T-E1-STAND", "Thrust stand, one station, both candidate props", verifies=["CL-E1-TW-TABLE", "CL-E1-TW-WORST",
         "CL-E1-IMAX-148", "CL-E1-IMAX-168", "CL-E1-HOVER-GW", "CL-E1-KT", "CL-E1-KP", "CL-E1-MAKER-SUPPLY"],
         procedure="H1 stand (20 kg cell + HX711), X3108S + LANRC 45 A, 11x4.5MR then 11x5.5MR; held 14.8 V bench supply "
                   "(>= 40 A) and then a flight pack; 10 % throttle steps to 100 %, 3 s each; log gf, A, V, rpm (optical "
                   "tach or ESC telemetry), can temperature; one 60 s run at 689 gf for g/W; ten 10 -> 100 % throttle "
                   "punches in < 50 ms with no desync")
kit.test("T-E1-MOTOR-RM", "Incoming check: resistance, no-load current, mass, bolt pattern, hole depth",
         verifies=["CL-E1-KP", "CL-E1-MASS-PRP", "CL-E1-SCREW-ENGAGE", "CL-E1-STACK-PROP-PLANE"],
         procedure="Weigh motor, ESC, prop, adapter set (0.1 g); calipers: base bolt pattern, hole depth, lead length, "
                   "body length, adapter base and post; 4-wire: 2.00 A from a bench supply through two phases, read the voltage drop (R = V / I); no-load "
                   "current and rpm at 10.0 V without prop (Kv = rpm / (V - I0 R))")
kit.test("T-E1-HOVER-LOG", "Tethered hover current", verifies=["CL-E1-HOVER-I", "CL-E1-HOVER-DT"],
         procedure="XPS aircraft at 2.6 kg, 30 s tethered hover; pack current from the power module; can temperature "
                   "by IR at landing")


# ================================================================== report
def report():
    vals = {n["id"]: n for n in kit.nodes.values()}
    print("\n--- E1 propulsion summary ---")
    for cid in ("CALC-E1-CAL", "CALC-E1-HOVER", "CALC-E1-FULL", "CALC-E1-CRUISE", "CALC-E1-CORRIDOR", "CALC-E1-MOTOR-OUT",
                "CALC-E1-LIMIT", "CALC-E1-SENS", "CALC-E1-WORST", "CALC-E1-STACK", "CALC-E1-MASS"):
        print(cid)
        for k, v in vals[cid]["outputs"].items():
            print(f"   {k:<22} {v:10.4g}")


def write_parts():
    """redesign/subsystems/propulsion/parts.csv (assigned by A1, CR-A3-05): flown quantities, per-unit flying mass
    incl. leads from ASM-E1-PART-MASS, so A3's roll-up and CL-E1-MASS-PRP use one set of numbers."""
    import csv
    pm = kit.nodes["ASM-E1-PART-MASS"]["value"]
    rows = [
        ["PRP-001", "Motor SunnySky X3108S KV900", 4, "buy", "-", "-", pm["motor"], 24.99,
         "https://sunnyskyusa.com/products/sunnysky-x3108s-motors",
         "mass incl. factory leads, no bullets (HRN-E03); buy 5 (1 spare); base bolt pattern and lead length not "
         "published: measure on arrival (T-E1-MOTOR-RM); UNVERIFIED"],
        ["PRP-002", "ESC LANRC BLHeli_S 45 A (55 A 10 s) 2-6S, Bluejay reflash", 4, "buy", "-", "-", pm["esc"], 7.50,
         "https://www.amazon.com/dp/B0D2HS4Y4J",
         "6.6 g bare board; mass with factory power/signal leads and heat-shrink is EST; 4-pack $30.00, buy 2 packs "
         "(4 spare); fallback Holybro Tekko32 F4 45A AM32 $22.50 (readymaderc.com); price UNVERIFIED"],
        ["PRP-003", "Prop APC 11x5.5MR (LP11055MR) / 11x5.5MRP (LP11055MRP)", 4, "buy", "-", "glass-filled nylon",
         pm["prop"], 3.83, "https://www.apcprop.com/product/11x5-5mr/",
         "2 MR + 2 MRP flown (diagonal pairs); hub 16.5 mm dia x 8.9 mm, 1/4 in bore, centre on the M6 post with an "
         "APC LPAR06E ring; buy 8 + 4 x 11x4.5MR/MRP for the stand A/B"],
        ["PRP-004", "Prop adapter, bolt-on M6x1 (RH or LH) + 4 x M3x4 SHCS + M6 nut ISO 4032 + M6 washer", 4, "buy",
         "-", "aluminium / steel", pm["adapter_nut"], 5.99,
         "https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct",
         "set of 4 (2 RH + 2 LH) $23.95, out of stock 2026-11-09; fallback: the adapter in each motor box (one thread "
         "hand) with Loctite 243 on the nut; LH thread on the CW motors so drag torque tightens the nut"],
        ["PRP-005", "Motor screw M3x8 SHCS ISO 4762 A2", 16, "buy", "-", "A2 stainless", round(pm["motor_screws"] / 4, 2),
         0.10, "Bolt Depot (same size as the old design's F01)",
         "4 per motor through the 5.0 mm printed mount plate, 3.0 mm engagement, Loctite 243, 0.5 N*m; "
         "screw-hole depth probed on arrival (CL-E1-SCREW-ENGAGE)"],
    ]
    out = HERE.parents[1] / "subsystems" / "propulsion" / "parts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part_id", "name", "qty", "make_or_buy", "process", "material", "mass_g", "unit_cost_usd",
                    "vendor_or_file", "notes"])
        w.writerows(rows)
    total = sum(r[2] * r[6] for r in rows)
    print(f"{out.relative_to(HERE.parents[2]).as_posix()}: {len(rows)} lines, {total:.1f} g flying")


if __name__ == "__main__":
    kit.write()
    write_parts()
    report()
