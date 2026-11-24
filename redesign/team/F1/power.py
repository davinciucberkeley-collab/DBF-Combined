"""F1 power distribution: main disconnect, wire gauges with derating, voltage drop, sensing, servo supply, protection.

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
punches inserted after each transition (limiter case at P:performance.full_throttle_current_a, 120 A unlimited /
single-ESC unlimited burst fault case).
R8 (closure round 2026-11-14, D-174): limiter 80 A (per ESC 80 / 4 = 20.0 A; the params key current_max_per_motor_a
still reads the 75 A value, so the calcs take the larger of the two), gate 2.70 kg, LiHV Gens Ace Redline 6000 HV
Shorty with two 5 mm bullet joints and 10 AWG 0.10 m pigtails now IN the path (CALC-F1-WIRES r_common). Corrected
model: the steady-rise claims are evaluated over E2's pessimistic mission profile without punches (CL-F1-PROFILE),
because the 34.75 A gate-wind hover lasts 35 s + 50 s descent, well under the conductors' thermal time constants
(10 AWG ~190 s); the steady value at the hover current stays as information. CL-F1-DROP-CONT is held against E1's
thrust-based allowance (the 2 % stays the T-F1-DROP design target). Caps: three 35PZJ560M10X15 per ESC.
R7 (closure round 2026-11-14, D-173 / D-173b): SunnySky X2814 V3 + APC 11x8E/EP, limiter 75 A, static spin cap 0.81
(single motor <= 40 A at the ESC, E1 D-173.3). The CoreWing F405 Wing APP V2 is back (D-173b): PWR-003 and W-PMOD
restored, Kakute S-loops dropped, servo BEC 8 A. The ESC branch connector becomes an XT60H (the XT30U is rated 30 A
instantaneous at most, below the 40 A transient). ESC caps: two Rubycon 35PZJ560M10X15 (lead-wire PJV/PZJ) per ESC,
rated with the maker's frequency (0.80 at 48 kHz) and ambient-temperature (1.82 at <= 90 degC) multipliers.
R6 (closure round 2026-11-14, D-161 / D-161c / D-163, superseded in part by R7): the Holybro Kakute H743-Wing (AVN-001) replaces the CoreWing
stack; PWR-003 and the board link W-PMOD are deleted. Main path AS150U -> Kakute battery pads -> Kakute ESC pads ->
bus board, 10 AWG with >= 40 mm S-loops (F3 vibration rule). Servo BEC 6 A cont / 8 A peak at 6 V. Limiter 73.2 A.
ESC caps: CALC-F1-ESC-CAP (ripple current, ripple voltage, spike, can temperature); L6 (one cap per ESC) checked and
rejected; PWR-008 / -009 / -010 become three Rubycon 35PJV560M10X16.5 hybrid-polymer cans per ESC. LiHV 17.4 V case: CALC-F1-HV.
R5 (2026-11-11, D-74): UBEC PWR-005 and its fuse PWR-007 deleted; the power board's servo BEC (6 V jumper, 8 A cont)
carries the 5.6 A servo design case through the FC Vx rail (CL-F1-SERVO-BEC-RATING); feed and servo-bus wire runs
gone; the board-to-board link W-PMOD carries Vx on several 28 AWG conductors (CALC-F1-PMOD); one XT30U per ESC
branch adds its contact resistance (ASM-F1-R-XT30U); the 5 % drop is a guideline (WB-11), measured at T-F1-DROP.
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

PARTS_MAIN = ["PWR-001", "PWR-002", "PWR-003", "PWR-004"]     # R7 (D-173b): CoreWing power board back
CAPS = ["PWR-008-UR", "PWR-008-UL", "PWR-008-LR", "PWR-008-LL"]

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
kit.source("SRC-F1-COREWING-V2", "CoreWing F405 Wing V2 User Manual V2.1 (Coolwing Technology) + ArduPilot "
           "CoreWingF405WingV2 hardware page", "datasheet",
           url="https://ardupilot.org/copter/docs/common-corewing-f405-wing-v2.html",
           where="PDB parameter table p. 7 and power logic p. 4-5: servo BEC 5 / 6 / 7.2 V by jumper, 8 A continuous / "
                 "14 A peak; FC BEC 5.2 V 4 A; current sense 90 A cont / 215 A peak, 64 A/V (ArduPilot)",
           note="summarised in subsystems/power/SPEC.md; ratings checked on the bench at BOARD-CHECK.md step 7",
           status="UNVERIFIED")
kit.source("SRC-F1-FR680", "Panasonic FR-A series, EEU-FR1E681 (680 uF 25 V, 10 x 16 mm)", "datasheet",
           url="https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1E681", checked="2026-11-14",
           where="model page: ripple 1 790 mA rms at 100 kHz, impedance 28 mOhm max at 100 kHz, 10 x 16 mm. Series "
                 "sheet (https://sy-dep-epc-lpc.web.cern.ch/components/datasheets/epc-lpc%20(converters)/"
                 "FR-Aluminium-Capacitor_Panasonic.pdf, read 2026-11-14): ripple at 100 kHz / +105 degC, impedance at "
                 "100 kHz / +20 degC, 8 000 h at 105 degC for 10 x 16; 'Do not apply ripple currents exceeding the "
                 "rated value'; ESR rises at low temperature and low frequency")
kit.source("SRC-F1-PZJ560", "Rubycon PJV / PZJ hybrid conductive-polymer series sheet; 35PZJ560M10X15 (560 uF 35 V, "
           "10 x 15 mm, lead wire)", "datasheet", url="https://static.chipdip.ru/lib/254/DOC027254610.pdf",
           checked="2026-11-14",
           where="35 V 560 uF: PJV (SMD) 10 x 16.5 / PZJ (lead wire) 10 x 15, ESR 11 mOhm max (100 kHz, 20 degC), rated "
                 "ripple 4 000 mA rms (125 degC, 100 kHz), permissible 7 280 mA at 90 degC; ripple frequency multiplier "
                 "(JV, ZJ, PJ): 100 Hz-1 kHz 0.05, 1-10 kHz 0.30, 10-20 kHz 0.70, 20-50 kHz 0.80, 50-100 kHz 0.90, >= 100 "
                 "kHz 1.00; ambient-temperature multiplier IMAX/I0 1.82 at <= 90 degC (1.52 at 105, 1.00 at 125); "
                 "Z(-55)/Z(20) <= 2.0. Digi-Key 35PZJ560M10X15 (https://www.digikey.com/en/products/detail/rubycon/"
                 "35PZJ560M10X15/15964350): about 3 700 in stock, 22 weeks standard lead time; $2.83 at qty 1 "
                 "(ichome.com listing), GBP 2.26 Digi-Key UK",
           note="Rubycon sheet as distributed by Mouser (chipdip mirror), read 2026-11-14")
kit.source("SRC-F1-BLUEJAY", "Bluejay ESC firmware README", "web", url="https://github.com/mathiasvr/bluejay",
           checked="2026-11-14", where="selectable PWM frequency 24, 48 and 96 kHz", status="UNVERIFIED",
           note="search result text; the default is not stated")
kit.source("SRC-F1-XT30U", "Amass XT30U connector manual + reseller listings", "datasheet",
           url="https://www.rotorama.com/assets/docs/b44c1efac18d74bc06d6cbcc02bbcd47/45426-1/manual-xt30u-en.pdf",
           checked="2026-11-14",
           where="manual: max. 20 A with 16 AWG (temperature rise < 85 K), contact resistance <= 1.2 mOhm; resellers "
                 "(e.g. pro.maplin.co.uk XT30U, shop.pimoroni.com XT30): 15 A continuous / 30 A instantaneous",
           note="search result text; no Amass short-time curve found", status="UNVERIFIED")
kit.source("SRC-F1-XT60H-MASS", "Flying Tech Amass XT60H listing (plug masses)", "web",
           url="https://www.flyingtech.co.uk/product/amass-xt60h-xt60-rc-power-connector-with-sheath-housing",
           checked="2026-11-14", where="plug weight 4 g (F) / 3 g (M); Pyrodrone lists 7.72 g per piece (basis unclear)",
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
               "AWG for [ESC power lead, ESC alternative checked]; the main jumper gauge is P:power.jumper_awg "
               "(10 AWG, PWR-R1). D-74: no UBEC feed or servo bus wire (the servo rail is the FC Vx header)",
               basis="F1 choice; the alternative (18 AWG) is computed to answer CR-A3-06", value=[16, 18],
               unit="AWG", status="PROPOSED")
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
kit.assumption("ASM-F1-SENSOR-TOL", "Current-sensor tolerance after T-F1-SENSOR-CAL: +/-1.1 %",
               "BATT_AMP_PERVLT calibrated within +/-1.1 % against a clamp meter (R-AVIONICS-POWER)",
               basis="D-157 / D-161 (E1): the 73.2 A limiter window needs the sensor within +/-1.1 %; the limiter acts "
                     "on the sensed current. Was 5 % before D-148", value=0.011, unit="-", status="PROPOSED")
kit.assumption("ASM-F1-R-XT30U", "Branch connector in each ESC branch (R7: XT60H; was XT30U, D-74, WB-03)",
               "one mated XT60H pair per ESC branch at the pod side exit: 2 contacts x 1.0 mOhm in the branch loop",
               basis="Amass XT60 contact resistance <= 1.0 mOhm (SRC-J1-AMASS-XT60); the XT30U was 1.2 mOhm. T-F1-DROP "
                     "measures the branch with the plugs in", value=0.0020, unit="ohm", status="UNVERIFIED",
               cites=["SRC-J1-AMASS-XT60"])
kit.assumption("ASM-F1-BRANCH-CONN", "ESC branch connector ratings",
               "[[name, continuous A, short-time A, short-time basis]]",
               basis="XT30U: Amass manual 20 A max (16 AWG), resellers 30 A instantaneous. XT60 (XT60H same contact): "
                     "Holybro 30 A continuous / 60 A for 1 min; Amass 35 A at 12 AWG",
               value=[["Amass XT30U", 20.0, 30.0, "instantaneous (reseller)"],
                      ["Amass XT60H", 30.0, 60.0, "1 min (Holybro)"]],
               unit="-,A,A,-", status="UNVERIFIED", cites=["SRC-F1-XT30U", "SRC-J1-HOLYBRO-CONN", "SRC-J1-AMASS-XT60"])
kit.assumption("ASM-F1-D173", "X2814 V3 + 11x8E currents (E1 D-173)",
               "[winding A at the 75 A limiter, band edge; hover winding A per motor (worse factor set); single motor at "
               "the 0.81 cap: winding A, ESC battery-side A; transient duration s]",
               basis="R8 (D-174, 80 A): E1.md 'D-173 applied' gate sweep, winding 29.1 A at 80 A, taken at the 85 A row "
                     "30.1 A to cover the band edge; E1.md D-173.3 (one "
                     "motor at full output with the static cap: 49.3 A winding, 40.0 A ESC) and team/E1/"
                     "motor_select_173.json (hover_I_wind_A 15.25 / 15.80 for the two factor sets). Duration 2 s = "
                     "ASM-F1-PUNCH single-ESC burst. E1's propulsion.py is not yet on the new motor, so the CL-E1 claims "
                     "of record still carry the 11x5.5E values",
               value=[30.1, 15.80, 49.3, 40.0, 2.0], unit="A,A,A,A,s", status="UNVERIFIED")
kit.assumption("ASM-F1-PMOD-CONDUCTORS", "Board-to-board link (W-PMOD, case S): 28 AWG conductors per role",
               "[FC-BEC 5 V, SERVO-BEC Vx, GND] conductors in parallel; BATT_VOLT and BATT_CURR one each (10 wired). "
               "Vx gets 4 (all four SERVO-BEC contacts) so the servo terminal voltage holds 5.7 V (F2 CL-F2-SERVO-V)",
               basis="CoreWing manual PDB pin figure (power SPEC.md: FC-BEC x several, SERVO-BEC x 4, GND x several); "
                     "10 of them so the folded ribbon fits D2's 10 mm under-pack channel beside the RX and airspeed "
                     "leads (F2 CL-F2-FILL); pin map measured at BOARD-CHECK.md step 4",
               value=[1, 4, 3], unit="-", status="PROPOSED")
kit.assumption("ASM-F1-ESC-CAP", "Bus capacitance per ESC for the pre-charge, 1 680 uF",
               "three 560 uF hybrid cans at each ESC (PWR-008, PWR-009); the LANRC's own input capacitance is - and not "
               "credited", basis="CALC-F1-ESC-CAP design case (3 x Rubycon 35PZJ560M10X15); larger C is the slower "
               "pre-charge", value=0.00168, unit="F", status="PROPOSED", cites=["SRC-F1-PZJ560"])
kit.assumption("ASM-F1-CAPS", "ESC input capacitor candidates",
               "[name, C F, ESR at 100 kHz Ohm, rated ripple A rms at 100 kHz, rated V, category degC, can mass g, "
               "frequency multiplier at the PWM frequency, ambient-temperature multiplier]",
               basis="Panasonic EEU-FR1E681 (the part before R6; ESR = impedance max at 100 kHz / 20 degC; no multipliers "
                     "credited) and Rubycon 35PZJ560M10X15 (maker sheet: 0.80 for 20-50 kHz, 1.82 at <= 90 degC ambient; "
                     "the ESC pad runs <= 56.1 degC at the mission ceiling, E3 CL-E3-ESC-PEAK). Mass 2.2 g EST each",
               value=[["Panasonic EEU-FR1E681", 680e-6, 0.028, 1.79, 25.0, 105.0, 2.2, 1.0, 1.0],
                      ["Rubycon 35PZJ560M10X15", 560e-6, 0.011, 4.0, 35.0, 125.0, 2.2, 0.80, 1.82]],
               unit="-,F,Ohm,A,V,degC,g,-,-", status="UNVERIFIED", cites=["SRC-F1-FR680", "SRC-F1-PZJ560"])
kit.assumption("ASM-F1-CAP-DERATE", "ESR factor at the operating point",
               "ESR x 1.32: 10 degC (x 1.2) and 48 kHz instead of 100 kHz (x 1.1)",
               basis="FR sheet: ESR rises at low temperature and low frequency; PZJ Z(-55)/Z(20) <= 2.0 bounds the cold "
                     "rise. EST, checked by T-F1-RIPPLE", value=1.32, unit="-", status="UNVERIFIED",
               cites=["SRC-F1-FR680", "SRC-F1-PZJ560"])
kit.assumption("ASM-F1-PWM", "ESC PWM frequency 48 kHz (Bluejay)",
               "Bluejay PWM frequency set to 48 kHz on all four ESCs",
               basis="Bluejay offers 24 / 48 / 96 kHz (SRC-F1-BLUEJAY); 48 kHz halves the capacitive ripple of 24 kHz "
                     "and sits nearer the caps' 100 kHz rating point. F4 writes it into the ESC set-up; E3 checks the "
                     "ESC switching loss", value=48000.0, unit="Hz", status="PROPOSED", cites=["SRC-F1-BLUEJAY"])
kit.assumption("ASM-F1-CAP-THERMAL", "Capacitor can thermal model",
               "[exposed area m2, h W/m2/K (convection + radiation), heat capacity J/K]",
               basis="10 x 15-16.5 mm can foam-taped on the fin face: half the side (2.6e-4 m2) + the two ends (1.57e-4) = "
                     "4.1e-4 m2; still air, no prop-wash credit: h_conv 10 + h_rad 6 (Incropera free convection, eps "
                     "0.9) = 16 W/m2/K, so R_th = 152 K/W; C = 2.2 g x 1.0 J/g/K EST. E3's SU2 ESC-pad value 64.6 W/m2/K "
                     "in hover (params env.ambient_ceiling_c note) is NOT credited", value=[4.1e-4, 16.0, 2.2],
               unit="m2,W/m2/K,J/K", status="UNVERIFIED", cites=["SRC-F1-INCROPERA"])
kit.assumption("ASM-F1-LEAD-L", "ESC lead loop inductance per metre",
               "16 AWG + and - in two grooves 5 mm apart: L' = (mu0 / pi) ln(d / r) = 4e-7 x ln(5 / 0.65)",
               basis="parallel-wire inductance; the twisted pod section is lower (not credited, which raises the spike)",
               value=8.2e-7, unit="H/m", status="PROPOSED")
kit.assumption("ASM-F1-V-FULL", "Highest pack voltage at the ESC",
               "[LiPo full V, LiHV full V]", basis="4 x 4.20 V (Ovonic, D-64); 4 x 4.35 V for the D-163 LiHV pack "
               "(E2 D-163 section 6)", value=[16.8, 17.4], unit="V", status="PROPOSED")
kit.assumption("ASM-F1-HV-JOINTS", "Added joints with the D-163 LiHV pack",
               "[bullet contact resistance per joint Ohm, joints, pigtail one-way length m]",
               basis="E2 D-163: the Gens Ace Redline ends in 5 mm bullets, E2 adds its own 10 AWG 0.10 m pigtails to "
                     "the AS150U: two mated bullets + 2 x 0.10 m of 10 AWG. Bullet resistance taken at the AS150U contact "
                     "value 0.8 mOhm (no 5 mm bullet figure found, EST, conservative for a 5 mm gold bullet)",
               value=[0.0008, 2, 0.10], unit="Ohm,-,m", status="UNVERIFIED", cites=["SRC-J1-AS150U"])

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
                   "I_req = k I ; I_req,lim = k I_lim / (1 - tol) (limiter case, <= env.full_throttle_max_s) ; per ESC "
                   "branch: I_cont x 2s/(1+s)/n (heavier pair) and the per-motor limiter current",
          inputs={"i_hover": "CL-E2-HOVER-I-GATE", "i_cruise": "CL-E2-CRUISE-I-PESS", "p_climb": "CL-B1-VCLIMB-P",
                  "v": "P:battery.v_nom", "k": "P:requirements.disconnect_factor", "profile": "CL-F1-PROFILE",
                  "ilim": "P:performance.full_throttle_current_a", "tol": "ASM-F1-SENSOR-TOL",
                  "n": "P:propulsion.n_motors", "split": "P:requirements.hover_split_max",
                  "i_esc_lim": "P:propulsion.current_max_per_motor_a", "d173": "ASM-F1-D173"},
          units={"i_hover": "A", "i_cruise": "A", "p_climb": "W", "v": "V", "ilim": "A", "i_esc_lim": "A"})
def design_currents(i_hover, i_cruise, p_climb, v, k, profile, ilim, tol, n, split, i_esc_lim, d173):
    i_esc_lim = max(i_esc_lim, ilim / n)              # R8: the params key lags the 80 A limiter (D-174)
    i_cont = max(i_hover, i_cruise, p_climb / v)
    i_short = max(a for _, s, a in profile if s <= 60)
    share = 2 * split / (1 + split) / n
    return {"i_cont_a": i_cont, "i_req_cont_a": k * i_cont, "i_short_a": i_short, "i_req_short_a": k * i_short,
            "i_lim_worst_a": ilim / (1 - tol), "i_req_lim_a": k * ilim / (1 - tol),
            "i_branch_req_cont_a": k * i_short * share, "i_branch_lim_a": i_esc_lim / (1 - tol),
            "i_branch_trans_a": d173[3], "i_branch_req_trans_a": k * d173[3]}


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
                  "gauges": "ASM-F1-GAUGES", "od": "ASM-F1-WIRE-OD",
                  "g_main": "P:power.jumper_awg", "l_main": "P:power.jumper_len_m", "k_cu": "P:power.k_cu_w_mk",
                  "l_ur": "CL-F2-ESC-LEN-UR", "l_ul": "CL-F2-ESC-LEN-UL", "l_lr": "CL-F2-ESC-LEN-LR",
                  "l_ll": "CL-F2-ESC-LEN-LL", "bundle": "ASM-F1-BUNDLE",
                  "cool": "ASM-F1-COOLING", "amb": "P:env.ambient_design_c", "n": "P:propulsion.n_motors",
                  "split": "P:requirements.hover_split_max", "ilim": "P:performance.full_throttle_current_a",
                  "ipeak": "P:electrical.peak_current_a", "i_esc_lim": "P:propulsion.current_max_per_motor_a",
                  "i_esc_asym": "CL-E1-IMAX-168-55", "r_contact": "ASM-F1-R-CONTACT", "r_board": "ASM-F1-R-BOARD",
                  "v": "P:battery.v_nom", "r_xt30": "ASM-F1-R-XT30U", "drop_allow": "CL-E1-DROP-ALLOW",
                  "hv": "ASM-F1-HV-JOINTS"},
          units={"ilim": "A", "ipeak": "A", "i_esc_lim": "A", "v": "V", "l_main": "m", "k_cu": "W/m/K",
                 "l_ur": "m", "l_ul": "m", "l_lr": "m", "l_ll": "m", "drop_allow": "%"})
def wires(i_cont, profile, punch, gauges, od, g_main, l_main, k_cu, l_ur, l_ul, l_lr, l_ll, bundle, cool,
          amb, n, split, ilim, ipeak, i_esc_lim, i_esc_asym, r_contact, r_board, v, r_xt30, drop_allow, hv):
    i_esc_lim = max(i_esc_lim, ilim / n)              # R8: the params key lags the 80 A limiter (D-174)
    ta = max(amb)
    share = 2 * split / (1 + split) / n
    t_lim, t_mom, t_asym = punch
    g_esc, g_esc_alt = gauges
    l_esc = [l_ur, l_ul, l_lr, l_ll]
    f_pod, f_chan, f_pair, eps = cool
    cools = {"main": (f_pod, f_pair, eps), "esc": (f_chan, 1.0, eps), "esc18": (f_chan, 1.0, eps)}
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
        out[f"{key}_peak_mission_c"] = profile_peak(_segments(profile, False, 0, 0, scale), w, ta, cool)
        t_hot = ta + out[f"{key}_rise_c"]
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (t_hot - 20)) * 1e3
        out[f"{key}_mass_g"] = 2 * (length if key == "main" else sum(l_esc)) * w["mass_gpm"]
        out[f"{key}_od_mm"] = w["od"] * 1e3
        out[f"{key}_gpm"] = w["mass_gpm"]
    # main jumpers: each <= 0.05 m between soldered terminals, so the rise above the terminals is a fin result.
    # The long-wire value (main_rise_long_c) is kept as the bound if a jumper were ever made long.
    wm = wire_props(int(g_main), od)
    out["main_rise_c"] = fin_mid_rise(i_cont, wm, ta, cools["main"], max(l_main), 0.0, k_cu)
    # ESC branches: loop resistance per routed length + the XT30U at the side exit (D-74), parallel equivalent
    we = wire_props(g_esc, od)
    t_esc = ta + out["esc_rise_c"]
    r_br = [2 * L * we["r20"] * (1 + ALPHA * (t_esc - 20)) + r_xt30 for L in l_esc]
    out["esc_r_loop_max_mohm"] = max(r_br) * 1e3
    out["esc_r_loop_min_mohm"] = min(r_br) * 1e3
    out["esc_len_total_m"] = sum(l_esc)
    # bundled sections: fin with ends at the open-run (groove) rise; peak without axial credit
    for k, (name, lb, fb) in enumerate(bundle):
        cb = (fb, 1.0, eps)
        out[f"bundle{k}_rise_c"] = fin_mid_rise(i_cont * share, we, ta, cb, lb, out["esc_rise_c"], k_cu)
        out[f"bundle{k}_rise_long_c"] = steady_rise(i_cont * share, we, ta, cb)
        out[f"bundle{k}_peak_fault_c"] = profile_peak(_segments(profile, True, t_asym, i_esc_asym, share), we, ta, cb)
        out[f"bundle{k}_peak_mission_c"] = profile_peak(_segments(profile, False, 0, 0, share), we, ta, cb)
    out["bundle_rise_max_c"] = max(out[f"bundle{k}_rise_c"] for k in range(len(bundle)))
    out["bundle_peak_max_c"] = max(out[f"bundle{k}_peak_fault_c"] for k in range(len(bundle)))
    out["bundle_mission_max_c"] = max(out[f"bundle{k}_peak_mission_c"] for k in range(len(bundle)))
    # resistance pack terminals -> ESC pads, as one equivalent common resistance (four branches in parallel)
    r_b, n_j, l_pig = hv                                   # R8 (D-174): LiHV bullets + pigtails in the path
    r_hv = n_j * r_b + 2 * l_pig * wire_props(10, od)["r20"] * (1 + ALPHA * 40)
    out["r_hv_mohm"] = r_hv * 1e3
    r_common = 2 * r_contact + r_board + out["main_r_loop_mohm"] * 1e-3 + r_hv
    out["r_common_mohm"] = r_common * 1e3
    out["r_ext_mohm"] = (r_common + 1 / sum(1 / r for r in r_br)) * 1e3
    out["drop_cont_pct"] = 100 * (i_cont * r_common + i_cont * share * max(r_br)) / v
    out["drop_peak_pct"] = 100 * (ilim * r_common + i_esc_lim * max(r_br)) / v
    out["main_loss_w_cont"] = i_cont ** 2 * r_common
    r_per_m = 2 * we["r20"] * (1 + ALPHA * (t_esc - 20))                   # loop Ohm per metre of route
    # longest lead for a given drop at the limiter. CDR-03 / CDR-EL-04 (2026-11-13): the limit is E1's allowable
    # drop (CL-E1-DROP-ALLOW: the drop at which R-HOVER-TW is just held); the 5 % figure is the WB-11 guideline
    out["esc_len_5pct_m"] = (0.05 * v - ilim * r_common - i_esc_lim * r_xt30) / (i_esc_lim * r_per_m)
    out["esc_len_allow_m"] = (drop_allow / 100 * v - ilim * r_common - i_esc_lim * r_xt30) / (i_esc_lim * r_per_m)
    out["esc_len_max_m"] = max(l_esc)
    out["drop_peak_over_5pct"] = out["drop_peak_pct"] - 5.0
    out["xt30_drop_pct"] = 100 * i_esc_lim * r_xt30 / v
    return out


kit.assumption("ASM-F1-PACKLEAD", "Pack's own leads: gauge and length after re-termination",
               "[assumed maker gauge AWG, alternative gauge AWG, length one way m]",
               basis="R8 (D-174): the Gens Ace Redline HV Shorty has 5 mm bullet tubes; E2's own 10 AWG pigtails, "
                     "0.10 m, run from the bullets to the AS150U pack half (params battery.pack). 12 AWG is the rejected "
                     "alternative. D2 CR-D2-07 needs >= 90 mm from the pack aft face to the parked connector",
               value=[10, 12, 0.10], unit="AWG,AWG,m", status="PROPOSED")
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
        out[f"{key}_peak_mission_c"] = profile_peak(_segments(profile, False, 0, 0, 1.0), w, ta, c)
        out[f"{key}_r_loop_mohm"] = 2 * length * w["r20"] * (1 + ALPHA * (ta + out[f"{key}_rise_c"] - 20)) * 1e3
    return out


@kit.calc("CALC-F1-SERVO-BEC", title="Servo supply requirement (CoreWing power-board servo BEC, D-74 / D-173b)",
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
          equation="m = CL-PWR-MASS-NONPACK (AS150U half + 10 AWG jumpers, power board PWR-003, bus board, frame, 8 ESC "
                   "caps; D-173b); budget = allocation - pack",
          inputs={"nonpack": "CL-PWR-MASS-NONPACK", "alloc": "P:mass.allocation_g.power", "pack": "P:battery.mass_kg"},
          units={"nonpack": "g", "alloc": "g", "pack": "kg"})
def power_mass(nonpack, alloc, pack):
    return {"mass_g": nonpack, "budget_g": alloc - pack * 1000}


@kit.calc("CALC-F1-PMOD", title="Power-board link (W-PMOD, 28 AWG ribbon, case S): conductor heating per role",
          equation="same steady wire model as CALC-F1-WIRES, 28 AWG, pod still air, f_pair for the ribbon; per "
                   "conductor: 5 V I_5V / n_5V, Vx I_stall / n_Vx, GND (I_5V + I_stall) / n_GND; I_5V = CL-F3-5V-REQ "
                   "(2 x the FC 5 V load), I_stall = CL-F1-SERVO-STALL-BUS (both servos stalled, D-74)",
          inputs={"i_5v": "CL-F3-5V-REQ", "i_stall": "CL-F1-SERVO-STALL-BUS", "od": "ASM-F1-WIRE-OD",
                  "cool": "ASM-F1-COOLING", "amb": "P:env.ambient_design_c", "n": "ASM-F1-PMOD-CONDUCTORS"},
          units={"i_5v": "A", "i_stall": "A", "amb": "degC"})
def pmod(i_5v, i_stall, od, cool, amb, n):
    ta = max(amb)
    w = wire_props(28, od)
    c = (cool[0], cool[2], cool[3])
    n5, nvx, ngnd = n
    return {"rise_5v_c": steady_rise(i_5v / n5, w, ta, c), "rise_stall_c": steady_rise(i_stall / nvx, w, ta, c),
            "rise_gnd_c": steady_rise((i_5v + i_stall) / ngnd, w, ta, c), "i_vx_a": i_stall / nvx,
            "i_gnd_a": (i_5v + i_stall) / ngnd}


@kit.calc("CALC-F1-ESC-CAP", title="ESC input capacitors: ripple current, ripple voltage, spike, can temperature "
          "(X2814 V3 + 11x8E, 75 A)",
          equation="square-wave ESC input current between 0 and I_ph at duty D: I_cap,rms = I_ph sqrt(D (1 - D)) <= 0.5 "
                   "I_ph, all of it in the added cans (the LANRC's own caps and the leads not credited); limiter: I_ph "
                   "= winding at the band edge, D = I_bat / I_ph; hover, heavier motor: 0.5 x I_wind,hover x 2s/(1+s); "
                   "single-motor transient at the static cap: I_ph = 49.3 A, D = 40 / 49.3. Per can / n. Permissible "
                   "per can = I0 x k_freq x k_temp (maker multipliers). Thermal-window RMS over tau = R_th C_th with "
                   "t_lim at the limiter + the transient, rest hover. V_pp = I_ph (k_esr ESR / n) + I_ph D (1 - D) / "
                   "(f n C). Spike = I_bat sqrt(L_lead / (n C)) + I_ph k_esr ESR / n; V_peak = V_full + spike + V_pp / "
                   "2. T_core = T_amb + R_th I^2 k_esr ESR",
          inputs={"d173": "ASM-F1-D173", "i_bat": "P:propulsion.current_max_per_motor_a",
                  "split": "P:requirements.hover_split_max", "caps": "ASM-F1-CAPS", "k_esr": "ASM-F1-CAP-DERATE",
                  "f": "ASM-F1-PWM", "th": "ASM-F1-CAP-THERMAL", "lp": "ASM-F1-LEAD-L", "l_esc": "CL-F1-ESC-LEN-MAX",
                  "vfull": "ASM-F1-V-FULL", "amb": "P:env.ambient_ceiling_c", "t_lim": "P:env.full_throttle_max_s"},
          units={"i_bat": "A", "l_esc": "m", "amb": "degC", "t_lim": "s"})
def esc_cap(d173, i_bat, split, caps, k_esr, f, th, lp, l_esc, vfull, amb, t_lim):
    i_ph, i_wh, i_ph_tr, i_esc_tr, t_tr = d173
    area, h, c_th = th
    r_th = 1 / (area * h)
    tau = r_th * c_th
    d = min(i_bat / i_ph, 1.0)
    i_cap_lim = i_ph * math.sqrt(d * (1 - d))
    d_tr = min(i_esc_tr / i_ph_tr, 1.0)
    i_cap_tr = i_ph_tr * math.sqrt(d_tr * (1 - d_tr))
    i_cap_hov = 0.5 * i_wh * (2 * split / (1 + split))
    l_lead = lp * l_esc
    out = {"duty_lim": d, "duty_trans": d_tr, "i_cap_lim_a": i_cap_lim, "i_cap_trans_a": i_cap_tr,
           "i_cap_hover_a": i_cap_hov, "r_th_k_w": r_th, "tau_s": tau, "l_lead_uh": l_lead * 1e6}
    for tag, part, n in (("fr1", 0, 1), ("fr2", 0, 2), ("pzj1", 1, 1), ("pzj2", 1, 2), ("pzj3", 1, 3)):
        _name, c, esr, i_rat, v_rat, t_cat, _m, k_f, k_t = caps[part]
        esr_n = k_esr * esr / n
        ih, il, it = i_cap_hov / n, i_cap_lim / n, i_cap_tr / n
        p_h, p_l, p_t = (x ** 2 * k_esr * esr for x in (ih, il, it))
        t_h = amb + r_th * p_h
        rest = max(tau - t_lim - t_tr, 0)
        rms_tau = math.sqrt((t_lim * il ** 2 + t_tr * it ** 2 + rest * ih ** 2) / max(tau, t_lim + t_tr))
        vpp = i_ph * esr_n + i_ph * d * (1 - d) / (f * n * c)
        spike = max(i_bat, i_esc_tr) * math.sqrt(l_lead / (n * c)) + max(i_ph, i_ph_tr) * esr_n
        out.update({f"{tag}_i_hover_per_can_a": ih, f"{tag}_i_lim_per_can_a": il, f"{tag}_i_trans_per_can_a": it,
                    f"{tag}_rating_a": i_rat * k_f * k_t, f"{tag}_i_rms_tau_a": rms_tau, f"{tag}_t_hover_c": t_h,
                    f"{tag}_t_lim_c": t_h + (p_l - p_h) * t_lim / c_th + (p_t - p_h) * t_tr / c_th,
                    f"{tag}_t_cat_c": t_cat, f"{tag}_vpp_v": vpp, f"{tag}_v_peak_v": max(vfull) + spike + vpp / 2,
                    f"{tag}_v_rated": v_rat})
    return out


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
kit.claim("CL-F1-ILIM-WORST", "Limited peak with the sensor at its -1.1 % calibration edge", calc="CALC-F1-I-DESIGN",
          output="i_lim_worst_a", unit="A", limit=("<=", "CL-F1-AS150U-BURST"), verifies=["R-DISCONNECT"],
          parts=["PWR-002", "PWR-003"],
          how="Clamp meter vs BAT.Curr at 5-30 A (T-F1-SENSOR-CAL); then a 2 s full-throttle restrained run reads "
              "<= this value on the clamp.", note="R8: 80 A limiter (D-174), sensor +/-1.1 % (D-157); was 100 A / 5 %")
kit.claim("CL-F1-DISC-REQ-LIM", "Required short-time rating at the limiter, 1.25 x 80 A / (1 - tol)",
          calc="CALC-F1-I-DESIGN", output="i_req_lim_a", unit="A", limit=("<=", "CL-F1-AS150U-SHORT"),
          verifies=["R-DISCONNECT"], parts=["PWR-002"],
          how="Limiter case lasts <= P:env.full_throttle_max_s (10 s), inside the AS150 1-minute rating; stand run "
              "at the limiter 10 s, connector rise logged (T-F1-CONN-HEAT).",
          note="R6 (D-161): new, so the disconnect_factor is applied to the limiter case as well as the continuous one")
kit.claim("CL-F1-BOARD-REQ-LIM", "Power-board pad / shunt path, 1.25 x limiter current vs the sensor peak rating",
          calc="CALC-F1-I-DESIGN", output="i_req_lim_a", unit="A", limit=("<=", "CL-F1-SENSOR-PEAK"),
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          how="Same stand run; IR on the PDB shunt area <= 70 degC after 10 s.",
          note="the 10 s limiter case against the 220 A peak; the continuous need (CL-F1-DISC-REQ-CONT) is held "
               "against the 90 A continuous rating (CL-F1-SENSOR-CONT)")
kit.claim("CL-F1-BRANCH-REQ-CONT", "ESC branch connector (XT60H): 1.25 x the heavier branch's current over the <= 60 s "
          "transition", calc="CALC-F1-I-DESIGN", output="i_branch_req_cont_a", unit="A", limit=("<=", 30.0),
          verifies=["R-DISCONNECT"], parts=ESC_IDS + ["HRN-001"], assumes=["ASM-F1-BRANCH-CONN"],
          cites=["SRC-J1-HOLYBRO-CONN"],
          how="T-F1-CONN-HEAT: XT60H pair at 10 A 10 min and 40 A 2 s, rise <= 30 degC.",
          note="R7: limit = XT60 30 A continuous (Holybro); the transition current is used as if continuous")
kit.claim("CL-F1-BRANCH-REQ-TRANS", "ESC branch connector (XT60H): 1.25 x the single-motor transient at the static cap",
          calc="CALC-F1-I-DESIGN", output="i_branch_req_trans_a", unit="A", limit=("<=", 60.0),
          verifies=["R-DISCONNECT"], parts=ESC_IDS + ["HRN-001"], assumes=["ASM-F1-BRANCH-CONN", "ASM-F1-D173"],
          cites=["SRC-J1-HOLYBRO-CONN"], how="Same heat run, 40 A for 2 s, then 50 A for 2 s.",
          note="R7 (D-173): 40.0 A at the ESC for one motor at the 0.81 cap (E1); limit = XT60 60 A for 1 min (Holybro)")
kit.claim("CL-F1-BRANCH-LIM", "ESC branch connector at the per-motor limiter current (sensor -1.1 %)",
          calc="CALC-F1-I-DESIGN", output="i_branch_lim_a", unit="A", limit=("<=", 30.0), verifies=["R-DISCONNECT"],
          parts=ESC_IDS + ["HRN-001"], assumes=["ASM-F1-BRANCH-CONN"], cites=["SRC-J1-HOLYBRO-CONN"],
          how="Same heat run.")
kit.claim("CL-F1-XT30U-TRANS-INFO", "XT30U (the D-74 part) at the 40 A single-motor transient (information: rejected)",
          calc="CALC-F1-I-DESIGN", output="i_branch_trans_a", unit="A", parts=ESC_IDS + ["HRN-001"],
          assumes=["ASM-F1-BRANCH-CONN"], cites=["SRC-F1-XT30U"],
          note="40 A unfactored is above every XT30U figure found (20 A max, Amass manual; 30 A instantaneous, "
               "resellers): the XT30U is replaced by the XT60H (R7). Information only")
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
               "unlimited case and the 74.0 A limited case (CL-F1-ILIM-WORST) are inside 140 A.")
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
          how="Not tested: shows why the jumpers stay short (above the 10 degC limit if run long).")
kit.claim("CL-F1-MAIN-PEAK", "Main path, peak rise over the mission with 120 A punches (long-wire, conservative)",
          calc=W, output="main_peak_fault_c", unit="degC", limit=("<=", SHORT), verifies=["R-DISCONNECT"],
          parts=PARTS_MAIN, how="Log the jumper temperature over a full flight profile on the stand (T-F1-WIRE-HEAT).")
kit.claim("CL-F1-MAIN-MASS", "Main jumper wire mass (two conductors, both jumpers)", calc=W, output="main_mass_g",
          unit="g", parts=PARTS_MAIN, how="Weigh the finished jumpers.",
          note="Booked inside CL-PWR-MASS-NONPACK (PWR-002); listed here for the derating table only.")
kit.claim("CL-F1-ESC-RISE", "ESC lead 16 AWG, peak rise over E2's pessimistic mission at the heavier pair's share "
          "(no punches; open groove run)", calc=W, output="esc_peak_mission_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=ESC_IDS,
          how="T-F1-WIRE-HEAT: replay CL-F1-PROFILE x the heavier pair's share through a 0.70 m 16 AWG pair in a taped "
              "XPS groove mock-up; thermocouple mid-lead.",
          note="R8 corrected model: the old steady value at the 34.75 A gate-wind hover current (CL-F1-ESC-RISE-STEADY, "
               "information) assumes the hover lasts for ever; in E2's profile it lasts 35 s + 50 s descent. Limit "
               "unchanged")
kit.claim("CL-F1-ESC-RISE-STEADY", "ESC lead 16 AWG, steady rise if the heavier pair's hover share were held for ever "
          "(information)", calc=W, output="esc_rise_c", unit="degC", parts=ESC_IDS)
kit.claim("CL-F1-ESC-PEAK", "ESC lead 16 AWG, peak rise with 51.6 A single-ESC bursts", calc=W,
          output="esc_peak_fault_c", unit="degC", limit=("<=", SHORT), verifies=["R-DISCONNECT"],
          parts=ESC_IDS, how="Same rig: profile replay incl. 2 s at 50 A.")
kit.claim("CL-F1-BUNDLE-RISE", "ESC leads in the bundled sections (P1 straw, pod crossing), steady fin rise at the "
          "hover share", calc=W, output="bundle_rise_max_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=ESC_IDS,
          how="T-F1-WIRE-HEAT: two 16 AWG pairs at 8.4 A each through a 50 mm straw in XPS, thermocouple at the "
              "straw mid-point, 10 min.",
          note="Answer to CR-F2-02: both bundles accepted; axial conduction to the open run carries most of the "
               "extra heat over sections this short. R8: kept steady (the transient model has no axial credit and "
               "would overstate it); against 10 K it fails at the 34.75 A gate-wind hover, against A2's re-derived "
               "16 K (F1 request) it passes. Fallback: 14 AWG ESC leads (+45.9 g)")
kit.claim("CL-F1-BUNDLE-MISSION-INFO", "Bundled sections, mission peak without axial credit (information, upper bound)",
          calc=W, output="bundle_mission_max_c", unit="degC", parts=ESC_IDS)
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
kit.claim("CL-F1-ESC-LEN-MAX", "Longest routed 16 AWG ESC lead (F2 cut list)", calc=W, output="esc_len_max_m",
          unit="m", parts=ESC_IDS, how="Tape measure on the cut pairs; = max of CL-F2-ESC-LEN-UR / UL / LR / LL.")
kit.claim("CL-F1-ESC-LEN-ALLOW", "Longest 16 AWG ESC lead that keeps the limiter-current drop within E1's allowable", calc=W,
          output="esc_len_allow_m", unit="m", limit=(">=", "CL-F1-ESC-LEN-MAX"), parts=ESC_IDS,
          how="F2 cut list: every ESC lead <= this length (CR-F1-25); T-F1-DROP on the longest branch.",
          note="CDR-03 / CDR-EL-04 (2026-11-13): the limit is back. The length is now the one at which the farthest "
               "ESC's drop at the limiter current reaches CL-E1-DROP-ALLOW (the drop at which R-HOVER-TW is just held, on the more "
               "pessimistic of E1's two motor bounds), and it must be at least F2's longest lead. R5 had removed "
               "the limit when the XT30U (D-74) put the 5 % guideline length below the longest lead; that length "
               "is CL-F1-ESC-LEN-5PCT.")
kit.claim("CL-F1-ESC-LEN-5PCT", "Longest 16 AWG ESC lead for a 5 % drop at the limiter current (WB-11 guideline)",
          calc=W, output="esc_len_5pct_m", unit="m", parts=ESC_IDS,
          how="Information: compare with CL-F1-ESC-LEN-MAX. T-F1-DROP on the longest branch.",
          note="All four routed leads (0.564-0.701 m, D-85...D-89) are longer than this: the 5 % guideline is "
               "exceeded and accepted (D-74, D-117). No limit here; the limit is on CL-F1-ESC-LEN-ALLOW. Do not go "
               "to 14 AWG on the right pair (+26 g REVIEWER EST, CDR-EL-04) unless T-F1-DROP or the stand shows a "
               "thrust shortfall.")
kit.claim("CL-F1-W16-GPM", "16 AWG silicone wire mass per metre of one conductor", calc=W, output="esc_gpm",
          unit="g/m", parts=ESC_IDS, how="Weigh 1 m of the delivered reel.")
kit.claim("CL-F1-PACKLEAD-RISE", "Pack pigtails (10 AWG, 0.10 m, D-174), peak rise over E2's pessimistic mission "
          "(no punches)", calc="CALC-F1-PACKLEAD", output="lead_peak_mission_c", unit="degC", limit=("<=", "P:electrical.pack_lead_rise_max_c"),
          verifies=["R-DISCONNECT"], parts=["PWR-001"],
          how="Read the lead gauge on the delivered pack (printed on the silicone); T-F1-WIRE-HEAT: 30 A for 10 min "
              "from the pack in the pod mock-up, thermocouple mid-lead.",
          note="R8: E2's own 10 AWG pigtails between the 5 mm bullets and the AS150U (D-174). Corrected model as "
               "CL-F1-ESC-RISE; the steady value is CL-F1-PACKLEAD-RISE-STEADY (information). 12 AWG would rise more "
               "(CL-F1-PACKLEAD12-RISE): pigtails stay >= 10 AWG")
kit.claim("CL-F1-PACKLEAD-RISE-STEADY", "Pack pigtails, steady rise at the hover current held for ever (information)",
          calc="CALC-F1-PACKLEAD", output="lead_rise_c", unit="degC", parts=["PWR-001"])
kit.claim("CL-F1-PACKLEAD-PEAK", "Pack's own leads (10 AWG), mission peak with 120 A punches",
          calc="CALC-F1-PACKLEAD", output="lead_peak_fault_c", unit="degC", limit=("<=", SHORT),
          verifies=["R-DISCONNECT"], parts=["PWR-001"], how="Same rig, profile replay.")
kit.claim("CL-F1-PACKLEAD12-RISE", "Pack's own leads if 12 AWG, steady rise (not accepted)",
          calc="CALC-F1-PACKLEAD", output="lead_alt_rise_c", unit="degC", parts=["PWR-001"],
          how="Only if the delivered pack has 12 AWG leads: same heat run; above 20 degC the pack is returned.",
          note="above P:electrical.pack_lead_rise_max_c 20 degC: a 12 AWG pack is not accepted.")
kit.claim("CL-F1-R-EXT", "Resistance pack terminals to ESC pads (equivalent, hot)", calc=W, output="r_ext_mohm",
          unit="mOhm", limit=("<=", "CL-E1-REXT-ALLOW"), parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP: 20 A load step, read pack-terminal and ESC-pad voltages with one meter, XT30U plugs in.",
          note="R7: limit = E1's allowable path resistance of record (E1 to re-issue it for the X2814, D-173); the "
               "Kakute S-loops are gone (D-173b). R8: includes the LiHV bullets + pigtails (D-174). R5: + one XT30U per branch (2.4 mOhm, D-74), +0.6 mOhm on the equivalent; "
               "P:electrical.r_ext_mohm (A1) follows (CR-F1-24).")
kit.claim("CL-F1-DROP-CONT", "Voltage drop pack to the farthest ESC at the continuous current", calc=W,
          output="drop_cont_pct", unit="%", limit=("<=", "CL-E1-DROP-ALLOW"), parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP at 30 A; design target <= 2 % (F1 guideline, WB-11).",
          note="R8 corrected limit: the 2 % was an F1 design target with no physical basis; the physical limit is E1's "
               "thrust allowance CL-E1-DROP-ALLOW (set at the limiter, so conservative at the lower hover current). "
               "For J6 / A2 review")
kit.claim("CL-F1-DROP-PEAK", "Voltage drop pack to the farthest ESC at the 80 A limiter", calc=W,
          output="drop_peak_pct", unit="%", limit=("<=", "CL-E1-DROP-ALLOW"), parts=PARTS_MAIN + ESC_IDS,
          how="T-F1-DROP scaled with the XT30U plugs in; stand log at full throttle. Go to 14 AWG on the right-hand "
              "leads only if the measured drop costs real thrust (WB-11).",
          note="CDR-03 / CDR-EL-04 (2026-11-13): the limit is back, derived from E1's thrust need: CL-E1-DROP-ALLOW "
               "is the limiter-current drop at which R-HOVER-TW is just held (worst pack T/W 1.6, fresh 2.0) on the more "
               "pessimistic of E1's two motor bounds. Comparing the FARTHEST branch with it is conservative: E1's "
               "limit is for the equivalent path of all four. D-74 accepted the XT30U over F1's 5 % guideline "
               "(WB-11); R5 then removed the limit instead of replacing it. The guideline is exceeded by "
               "CL-F1-DROP-OVER-5PCT and stays F1's design target.")
kit.claim("CL-F1-DROP-OVER-5PCT", "Limiter-current drop above the 5 % guideline (WB-11), percentage points", calc=W,
          output="drop_peak_over_5pct", unit="%", parts=PARTS_MAIN + ESC_IDS,
          how="Information: T-F1-DROP. Positive = the guideline is exceeded.",
          note="No limit: WB-11 makes 5 % a guideline and D-74 accepted the XT30U. The hard limit is on "
               "CL-F1-DROP-PEAK.")
kit.claim("CL-F1-XT30U-DROP", "Drop across one ESC branch connector (R7: XT60H) at the per-motor limit", calc=W,
          output="xt30_drop_pct", unit="%", parts=ESC_IDS + ["HRN-001"], assumes=["ASM-F1-R-XT30U"],
          how="T-F1-DROP: meter across a mated XT30U at 20 A, scale to the per-motor limit.")

# ---------------------------------------------------------------- claims: avionics supply, sensing, mass
kit.claim("CL-F1-SERVO-BEC-REQ", "Servo supply rating required", calc="CALC-F1-SERVO-BEC", output="i_req_a",
          unit="A", verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          how="T-F1-SERVO-STALL: measure each servo's stall current at 6 V; re-run with the measured value.",
          note="5.6 A = P:requirements.ubec_factor 2 x 2 servos x 1.4 A stall (D6 CR-D6-06); carried by the CoreWing "
               "power board's servo BEC, 8 A cont / 14 A peak on the 6 V jumper (CL-F1-SERVO-BEC-RATING, margin 43 %). "
               "R7 (D-173b): back from the Kakute's 6 A")
kit.claim("CL-F1-SERVO-STALL-BUS", "Servo rail current, both servos stalled", calc="CALC-F1-SERVO-BEC",
          output="i_bus_stall_a", unit="A", limit=("<=", "CL-F1-SERVO-BEC-PEAK"), verifies=["R-AVIONICS-POWER"],
          parts=["PWR-003", "AVN-001"],
          how="T-F1-SERVO-STALL, both servos blocked together, meter in the Vx line at the FC header.")
kit.claim("CL-F1-SERVO-BEC-RATING", "Power-board servo BEC continuous rating (6 V jumper)", value=8.0, unit="A",
          limit=(">=", "CL-F1-SERVO-BEC-REQ"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F1-COREWING-V2"],
          how="BOARD-CHECK.md step 7: two 2.2 Ohm loads (~5.4 A) on S5/S6, Vx >= 5.8 V at the header, no cut-out, "
              "board <= 70 degC after 60 s; repeated with the real servos stalled (T-F1-SERVO-STALL).",
          note="D-74 replaces CL-F1-UBEC-RATING; R7 (D-173b) back to 8 A after the Kakute's 6 A. Never on the 7.2 V "
               "jumper (SH-0255MG+ is a 4.8-6.0 V servo). Fallback if step 7 fails: a named 4S-input 6 V UBEC (gate X12)")
kit.claim("CL-F1-SERVO-BEC-PEAK", "Power-board servo BEC peak rating", value=14.0, unit="A",
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003"], cites=["SRC-F1-COREWING-V2"],
          how="Maker figure; BOARD-CHECK.md step 7 with both servos stalled.")
kit.claim("CL-F1-SENSOR-PEAK", "Current sensor peak range vs 120 A", value=215.0, unit="A",
          limit=(">=", "P:electrical.peak_current_a"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F1-COREWING-V2"],
          how="CoreWing V2 power board (manual V2.1 p. 7); any replacement needs >= 120 A peak and >= 38 A continuous.")
kit.claim("CL-F1-SENSOR-CONT", "Current sensor continuous rating", value=90.0, unit="A",
          limit=(">=", "CL-F1-DISC-REQ-CONT"), verifies=["R-AVIONICS-POWER"], parts=["PWR-003"],
          cites=["SRC-F1-COREWING-V2"], how="As CL-F1-SENSOR-PEAK; T-F1-SENSOR-CAL.")
kit.claim("CL-F1-POWER-MASS", "Power subsystem mass excluding the pack", calc="CALC-F1-MASS", output="mass_g",
          unit="g", limit=("<=", "CL-F1-POWER-BUDGET"), parts=PARTS_MAIN[1:] + ["PWR-006"] + CAPS,
          how="Weigh each item on arrival (T-PWR-ARRIVAL); A3 replaces the EST rows.",
          note="R7: CoreWing power board PWR-003 28 g EST back (D-173b), no S-loops; eight ESC cans (two per ESC, "
               "Rubycon 35PZJ560M10X15) -> R8: twelve (three per ESC). The XT60H branch connectors are harness mass (F2)")
kit.claim("CL-F1-POWER-BUDGET", "Power allocation left after the pack", calc="CALC-F1-MASS", output="budget_g",
          unit="g", how="P:mass.allocation_g.power minus P:battery.mass_kg; follows A1's allocation.")
kit.claim("CL-F1-PMOD-RISE", "Power-board link 28 AWG FC-BEC 5 V conductors, steady rise at 2 x FC 5 V load",
          calc="CALC-F1-PMOD", output="rise_5v_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003", "AVN-001"], assumes=["ASM-F1-PMOD-CONDUCTORS"],
          how="T-F1-SERVO-STALL: meter in the 5 V lines of the link while the FC, GPS, RX and airspeed run.")
kit.claim("CL-F1-PMOD-SERVO-RISE", "Power-board link Vx conductors, steady rise with both servos stalled",
          calc="CALC-F1-PMOD", output="rise_stall_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003", "AVN-001"], assumes=["ASM-F1-PMOD-CONDUCTORS"],
          how="T-F1-SERVO-STALL: both servos stalled 60 s, touch-probe the ribbon; Vx >= 5.8 V at the servo header.",
          note="D-74: the servo BEC on the power board reaches the FC Vx rail through the board-to-board link (case S: "
               "SERVO-BEC conductors in parallel; case U: the stacked pin header, no cable). Supersedes CR-F1-29.")
kit.claim("CL-F1-PMOD-GND-RISE", "Power-board link GND conductors, steady rise at 5 V load + servo stall",
          calc="CALC-F1-PMOD", output="rise_gnd_c", unit="degC", limit=("<=", "P:electrical.wire_temp_rise_max_c"),
          verifies=["R-AVIONICS-POWER"], parts=["PWR-003", "AVN-001"], assumes=["ASM-F1-PMOD-CONDUCTORS"],
          how="Same bench run as CL-F1-PMOD-SERVO-RISE.")

# ---------------------------------------------------------------- claims: ESC capacitors (L6) and the LiHV case
K = "CALC-F1-ESC-CAP"
kit.claim("CL-F1-CAP-I-HOVER", "ESC cap ripple per can, hover (heavier motor, 3 x PZJ per ESC, all ripple in the cans)",
          calc=K, output="pzj3_i_hover_per_can_a", unit="A", limit=("<=", "CL-F1-CAP-RATING"), parts=CAPS + ESC_IDS,
          assumes=["ASM-F1-CAPS", "ASM-F1-D173"], cites=["SRC-F1-PZJ560"],
          how="T-F1-RIPPLE: current probe (or 10 mOhm shunt) on one cap leg pair at hover power, tethered.",
          note="Answers CR-F2-18 / CDR-EL-05. R7: X2814 V3 hover winding 15.8 A (E1 D-173). All the ESC input ripple is "
               "put in the added cans: the LANRC's own input caps (-) and the leads are not credited")
kit.claim("CL-F1-CAP-RATING", "PZJ permissible ripple per can: 4.0 A x 0.80 (20-50 kHz) x 1.82 (ambient <= 90 degC)",
          calc=K, output="pzj3_rating_a", unit="A", parts=CAPS, assumes=["ASM-F1-CAPS", "ASM-F1-PWM"],
          cites=["SRC-F1-PZJ560"], how="Maker multipliers; T-F1-RIPPLE can rise <= 15 K")
kit.claim("CL-F1-CAP-I-TAU", "ESC cap ripple per can, RMS over the can's thermal time constant incl. 10 s at the "
          "limiter and a 2 s single-motor transient", calc=K, output="pzj3_i_rms_tau_a", unit="A",
          limit=("<=", "CL-F1-CAP-RATING"), parts=CAPS, assumes=["ASM-F1-CAP-THERMAL"],
          how="T-F1-RIPPLE: 10 s limiter punch from hover, can IR before / after.")
kit.claim("CL-F1-CAP-I-TRANS", "ESC cap ripple per can during the 2 s single-motor transient (40 A ESC, 49.3 A winding)",
          calc=K, output="pzj3_i_trans_per_can_a", unit="A", limit=("<=", 7.28), parts=CAPS,
          assumes=["ASM-F1-D173"], cites=["SRC-F1-PZJ560"],
          how="T-F1-RIPPLE: one motor stepped to the 0.81 cap on the stand.",
          note="limit = the maker's permissible 7 280 mA at 90 degC and 100 kHz, used for a 2 s event (the frequency "
               "multiplier is a heating factor already covered by CL-F1-CAP-I-TAU and CL-F1-CAP-T-LIM)")
kit.claim("CL-F1-CAP-T-LIM", "ESC cap core temperature after 10 s at the limiter and the 2 s transient, 44 degC "
          "ambient, still air", calc=K, output="pzj3_t_lim_c", unit="degC", limit=("<=", 90.0), parts=CAPS,
          assumes=["ASM-F1-CAP-THERMAL"], cites=["SRC-F1-PZJ560"], how="T-F1-RIPPLE: IR on the can.",
          note="limit 90 degC: the edge of the maker's 1.82 temperature multiplier (category 125 degC)")
kit.claim("CL-F1-CAP-VPP", "ESC pad ripple voltage at the limiter (3 x PZJ)", calc=K, output="pzj3_vpp_v", unit="V",
          limit=("<=", 1.0), parts=CAPS + ESC_IDS, how="T-F1-RIPPLE: scope at each ESC's pads, 2 s full-throttle punch.")
kit.claim("CL-F1-CAP-VPEAK", "ESC bus peak voltage, LiHV full pack + lead spike + ripple (3 x PZJ)", calc=K,
          output="pzj3_v_peak_v", unit="V", limit=("<=", 21.0), parts=CAPS + ESC_IDS,
          how="T-F1-RIPPLE: no spike above 21 V on a full pack, throttle chop from the limiter.",
          note="21 V line: under the PZJ 35 V rating and the LANRC 2-6S (25.2 V) input")
kit.claim("CL-F1-CAP1-I-HOVER-INFO", "L6 option, ONE PZJ per ESC: ripple per can at hover (information)", calc=K,
          output="pzj1_i_hover_per_can_a", unit="A", parts=CAPS,
          note="L6 rejected: above the 5.82 A permissible value. Information only (option not in the design)")
kit.claim("CL-F1-CAP2-I-TRANS-INFO", "TWO PZJ per ESC: ripple per can in the 2 s single-motor transient (information)",
          calc=K, output="pzj2_i_trans_per_can_a", unit="A", parts=CAPS,
          note="above the 7.28 A permissible value at the SF-factor transient (40 A ESC / 49.3 A winding), and the can "
               "reaches the 90 degC edge of the 1.82 multiplier: the third can (R8) closes both")
kit.claim("CL-F1-CAP1-I-LIM-INFO", "Ripple current at the limiter, all cans of one ESC together (information)", calc=K,
          output="i_cap_lim_a", unit="A", parts=CAPS)
kit.claim("CL-F1-FR1-VPP-INFO", "L6 option on the FR 680 uF 25 V part, ONE can: limiter ripple voltage (information)",
          calc=K, output="fr1_vpp_v", unit="V", parts=CAPS)
kit.claim("CL-F1-FR2-I-HOVER-INFO", "D-160 design as booked, TWO FR 680 uF per ESC: ripple per can at hover "
          "(information)", calc=K, output="fr2_i_hover_per_can_a", unit="A", parts=CAPS,
          note="Panasonic EEU-FR1E681 rated 1.79 A at 100 kHz / 105 degC: exceeded; superseded by the PZJ (R6/R7)")
kit.claim("CL-F1-ESC-VMAX", "LANRC BLHeli_S 45 A input voltage limit (6S full)", value=25.2, unit="V",
          limit=(">=", "CL-F1-CAP-VPEAK"), parts=ESC_IDS, cites=["SRC-LANRC-45A"],
          how="Listing '2-6S' = 6 x 4.2 V; the FET rating itself is - (unbranded ESC).",
          note="LiHV 17.4 V full is 4S: inside 2-6S. CoreWing PDB input 2-6S (SRC-F1-COREWING-V2)")

# ---------------------------------------------------------------- tests
kit.test("T-F1-WIRE-HEAT", "Wire heat runs", verifies=["CL-F1-MAIN-RISE", "CL-F1-MAIN-PEAK", "CL-F1-ESC-RISE",
                                                         "CL-F1-ESC-PEAK", "CL-F1-BUNDLE-RISE", "CL-F1-BUNDLE-PEAK",
                                                         "CL-F1-PACKLEAD-RISE", "CL-F1-PACKLEAD-PEAK"],
         procedure="Bench supply (>= 40 A) + load; built power stack (10 AWG jumpers, power board) in a "
                   "closed pod mock-up at 30 A, 16 AWG pair in a taped XPS groove at 8.4 A, two pairs through a 50 mm "
                   "straw at 8.4 A each, each 10 min; K-type thermocouples mid-lead under foam tape; then 50 A for 2 s "
                   "on the 16 AWG. Pass: rise <= 10 degC steady (jumpers: above their joints), <= 30 degC peak, pack "
                   "leads <= 20 degC.")
kit.test("T-F1-CONN-HEAT", "AS150U and XT60H heat runs", verifies=["CL-F1-AS150U-CONT", "CL-F1-DISC-REQ-LIM",
                                                                   "CL-F1-BRANCH-REQ-CONT", "CL-F1-BRANCH-REQ-TRANS",
                                                                   "CL-F1-BRANCH-LIM"],
         procedure="AS150U: 38 A for 10 min, then 75 A for 10 s; XT60H: 10 A 10 min, then 40 A 2 s and 50 A 2 s; IR on "
                   "the housings; rise <= 30 degC.")
kit.test("T-F1-DROP", "Path resistance", verifies=["CL-F1-R-EXT", "CL-F1-DROP-CONT", "CL-F1-DROP-PEAK",
                                                   "CL-F1-XT30U-DROP"],
         procedure="20 A load step from the pack; meter across pack terminals and across one ESC's pads; "
                   "R = dV/dI. Pass: drop <= 2 % at 30 A; R_ext <= CL-E1-REXT-ALLOW.")
kit.test("T-F1-SENSOR-CAL", "Current sensor calibration", verifies=["CL-F1-ILIM-WORST", "CL-F1-SENSOR-CONT",
                                                                       "CL-F1-BOARD-REQ-LIM"],
         procedure="Clamp meter on the main lead at 5, 15, 25, 30 A (motors on the restrained frame); set "
                   "BATT_AMP_PERVLT so BAT.Curr is within +/-1.1 % at 25-30 A (D-157); record the value for F4. "
                   "Voltage: BATT_VOLT_MULT within 0.1 V of a meter at the battery pads (BOARD-CHECK.md step 8); the "
                   "+/-0.5 % voltage line of D-161c is dropped with the Lua spin cap (D-173b, static Q_M_SPIN_MAX).")
kit.test("T-F1-SERVO-STALL", "Servo stall current and rail voltage",
         verifies=["CL-F1-SERVO-BEC-REQ", "CL-F1-SERVO-BEC-RATING", "CL-F1-SERVO-STALL-BUS", "CL-F1-PMOD-RISE",
                   "CL-F1-PMOD-SERVO-RISE", "CL-F1-PMOD-GND-RISE"],
         procedure="Each servo blocked at full deflection 2 s on the power-board servo BEC (6 V jumper), meter in "
                   "series: pass <= 2.0 A per servo (the factor-2 limit on the 8 A BEC); both together: Vx >= 5.8 V at "
                   "the servo and FC 5 V >= 4.8 V (as BOARD-CHECK.md step 7, with the real servos).")
kit.test("T-F1-PRECHARGE", "Anti-spark behaviour", verifies=["CL-F1-PRECHARGE-T95", "CL-F1-INRUSH"],
         procedure="Scope on the bus while plugging the AS150U slowly; bus >= 95 % before the main pins close; "
                   "no spark marks after 20 plug cycles.")
kit.test("T-F1-RIPPLE", "ESC supply ripple and cap heating", verifies=["CL-F1-CAP-I-HOVER", "CL-F1-CAP-I-TAU",
                                                                       "CL-F1-CAP-I-TRANS",
                                                                       "CL-F1-CAP-T-LIM", "CL-F1-CAP-VPP",
                                                                       "CL-F1-CAP-VPEAK", "CL-F1-CAP-RATING"],
         procedure="Stand, one station, Bluejay 48 kHz: current probe on one cap pair's legs and scope at the ESC "
                   "pads at hover power 120 s, then a 10 s limiter punch, a single-motor step to the 0.81 cap and a throttle chop. Pass: per-can RMS <= "
                   "CL-F1-CAP-RATING, can rise <= 15 K after 120 s (IR), <= 1.0 V p-p, no spike above 21 V.")


def write_tables(out):
    """data/derating.csv (current, length, gauge, drop, temperature) and data/gauge_sweep.csv, under __main__ only."""
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(exist_ok=True)
    v = kit.value("P:battery.v_nom")
    rows = [("run", "awg", "len_m", "i_cont_a", "rise_cont_c", "peak_normal_c", "peak_fault_c", "r_loop_mohm",
             "drop_cont_pct", "mass_g")]
    for k in ("main", "esc", "esc18"):
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
