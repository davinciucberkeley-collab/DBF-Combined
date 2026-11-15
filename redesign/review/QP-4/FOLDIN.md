# QP-4 fold-in (A1 integration: A2 / I1 / F3), concept A, 2026-11-15

Executes QP-3 BOARD s7.2 #1 (one-truth fold-in) and bench conditions s7.1 #1, #2, #4. Nothing bought, built or flown; SITL, FE and CAD were **not** re-run; no git. Labels: `V` vendor page read, `CALC`, `EST`, `—` unknown. Paths relative to `redesign/qp/A/`.

## 1. One truth: what changed (BOARD s1 item 10 and s3)

| Board item | File(s) edited | Now says |
|---|---|---|
| Elevon y 0.04-0.34, +-20 deg (s1 item 3) | `sitl/a_aero.py` (EL_Y0/Y1, EL_MAX), `sitl/a_plant.py` comment, `sitl/fu_level.py`, `sitl/fwd_checks.py` (labels), REQUIREMENTS A-P11; CAD already had it (`cad/a_model.py`) | one geometry everywhere; SITL plant needs a re-run (s5) |
| Cruise rpm 7,300-7,600 (item 2) | `structures/structures_a.py` (cruise 7,450 mid), `structures/iter2_eval.py` (RPM_CRUISE; D-185 sweep 6,000-10,500 rpm in 250 steps plus cruise points), `structures/iter2_run.py` (text, limits now computed: LO_LIM / HI_LIM from the bands), MISSION s1, A-P10 | 8,900-10,500 withdrawn |
| Leg 150 m, fence 240 (items 7) | `mission_gate_a.py` (flown leg 150, requirement time kept on the 300 m reference lap), MISSION s2, A.param comment, REQUIREMENTS A-P24 | lap 36.5 s, far point 126 m, any-direction 220 m vs 240 m (20 m margin), 5.2 laps |
| D-185 | REQUIREMENTS A-P10 rewritten (coupling >= 0.5 = "strongly"; forced response U 1.0 g mm, FC <= 30 m/s2, three corners, full-rpm sweep; rate-band GM >= 2 + tap test +-20 %; VIBE < 30; balancing <= 0.3 g mm fallback); `iter2_eval.py` threshold `STRONG` 0.5; MASS-GATE and `mission_gate_a.py` structure 473 g frozen (191 / 119 / 122 / 40) | as ruled |
| D-186 | `A.param`: THR_MAX 68 + FWD_BAT 16.8/13.2 (already there; condition note added), VD 24 (`structures_a.py`, A-P13), gains / RAT_VT 24 / LOITER 40 / GYRO_FILTER 60 / CLMB_MAX 2 already present; **FC hard-mounted** (A.param comment, `cad/a_model.py` GEL 5 mm -> 1.5 mm foam tape, part AVN-007 renamed, `cad/a_assembly_plan.py`, A-P25); **notch**: `INS_HNTCH_MODE` 3 -> 1 (throttle), REF 0.42, FREQ 70 -> 105, BW 35 -> 40 (hover 1P 100-119 Hz); `SERVO_BLH_BDMASK` 15 -> 0 until M4; `Q_WVANE` 3 kept, **conditional** (A.param, MISSION s3, A-P8a) | as ruled; notch values are my starting numbers from the 1P band, final from the first FFT |
| MASS-GATE stale (460 / 70 / 24.8) | `MASS-GATE.md`, `mission_gate_a.py` | structure 473 g, fins 119, predicted **1,396 g** (script: basic 1,206 + growth 141.6 + overrun 48; CAD itemised 1,392; the board's 1,392 is the CAD figure), headroom 104 g to gate / 44 g to the 1.44 target; capped window +-8.1 %; CG = CAD 16.2 mm, pack to x <= -3 mm gives 20.0 mm (CALC), 4.0 mm forward limit withdrawn |
| A-P8a, A-P10, A-P13, A-P24, MISSION s3 | REQUIREMENTS-A.md, MISSION.md | done above; A-P13 "not computed" replaced by iter-2 margins, flutter still `—` |
| R04 scheduled (item 6) | `BOM-A.csv`, `bom_a.py`, SCHEDULE-A.md | R04 removed, CFRP risk retired, O1 row rewritten, R4 trigger 18 Feb |

Mass cascade: predicted 1.381 -> 1.396 kg moved the MISSION tables (hover 197 W, 20.97 Wh, margin 1.17x, 4.71 min before BATT_LOW) and A-P6 stall numbers (Vs 11.76, 1.3 Vs 15.29); gate-mass numbers unchanged.

## 2. BOM and the G7 test (`python -I bom_a.py`)

BOM-A.csv: R04 removed; R02 2 -> 1 x 16x14; new R08 3 x 12x10 ($12.26 `V`), R09 1 x 14x12 ($15.34, search snippet, `unverified`), R10 1 x 6x4.5 ($4.40 `V`) per STRUCTURES iter. 2; bench lines B01 SunnySky ($15.99), B02 Holybro props ($12.99), B03 1 kgf cell ($17 `EST`), B04 fixture ($15 `EST`), B05 SparkFun ship-group carrier ($0; the cell and HX711 are priced in G02). `bom_a.py`: SparkFun $8.00 shipping group, G7 line, crash reserve now carries the full tube set (R02 + R08-R10 = $83.98, not R02 + R04 = $67.46: the old reserve under-covered the tubes).

| | Value |
|---|---|
| Goods / spend / reserve | 1,243.53 / 1,431.12 / 329.64 |
| **Total** | **$1,760.76** (QP-3 board estimate $1,753.14; the +$7.6 is the full-tube reserve) |
| **+30 % margin on 11 unverified lines** | **+$126.36** |
| Growth absorbed | 17 % |
| **G7** (margin >= $100 and total <= $1,800) | **PASS** (margin $26 above the line, total $39 below) |

R5 ($1,750) is replaced by G7 as ruled. No cut is needed. If a new line must be absorbed, the smallest honest cuts, in order: G05 anemometer $25 x 1.1025 = $27.56 (borrow one); second charger bag W03 qty 2 -> 1 ($8.39); B04 fixture to Jacobs scrap ($16.54). Together $52.5 would restore +$179. Not applied (D-J6-3 is the team's call).

## 3. Compatibility checks (pages read 2026-11-15; none answers either question fully)

**3a. TBS M10Q GPS to the Kakute F405 Wing Mini GPS port: NOT confirmed, and the premise of a "GPS port" is not supported.**
- RMRC M10Q page (https://www.readymaderc.com/products/details/86501-tbs-m10q-gps-receiver-with-glonass, 2026-11-15): $19.76, In Stock; the page lists 5 V, 4,800-921,600 baud, and **no connector, pin count or cable**. KiwiQuads' M10Q page (https://www.kiwiquads.co.nz/product/tbs-m10q-gps-glonass-module/, 2026-11-15) also gives none. A search snippet suggested the M10N family uses a 1.00 mm 4-pin connector (`—`, not a TBS page).
- Holybro docs, Kakute F405 Wing Mini overview and pinout (https://docs.holybro.com/autopilot/kakute-f405-wing-mini/pinout, https://docs.holybro.com/autopilot/kakute-f405-wing-mini/overview, 2026-11-15): UARTs are listed as **solder pad pairs** (T1/R1, T2/R2, T3/R3, T5/R5, T6/R6; R3 inverted); the only JST-SH 6-pin named is the **USB extension board**. No GPS connector appears. The RMRC page (https://www.readymaderc.com/products/details/87184-holybro-kakute-f405-wing-mini-flight-controller) says the same: five UARTs, no GPS port, no cable list.
- Result: the BOM note "JST-SH 6-pin ASSUMED" is wrong as written. Plan: **solder** the M10Q's leads (or a pigtail) to a free UART pad pair (5 V, GND, TX, RX; the compass is I2C on the I2C2 SCL/SDA pads); which UART ArduPilot's board file maps to GPS is `—` (the ArduPilot wiki page for this board returned 404; hwdef not found). Cost $0, 30 min at Jacobs. Needed before Order 1: ask RMRC (support@readymaderc.com, +1 740-936-4500, per the fetched page) what connector the M10Q ships with, or accept soldering. V04 stays in Order 1 (stock risk) with this caveat.

**3b. Bidirectional DShot (SpeedyBee BLS 35A Mini V2 + Kakute): NOT confirmed; use the throttle-notch fallback.**
- SpeedyBee page (https://www.readymaderc.com/products/details/86873-speedybee-bls-35a-mini-v2-20x20-4-in-1-esc, 2026-11-15): firmware **BLHeli_S J-H-40**, protocols DShot300 / 600; no mention of bidirectional DShot or Bluejay.
- ArduPilot DShot ESCs page (https://ardupilot.org/plane/docs/common-dshot-escs.html, 2026-11-15): "Bi-directional DShot is only supported on BLHeli32/AM32 ESCs" (page text as fetched; the wiki's BiDirectional section was cut off in the fetch). ArduPilot forum reports (search result, https://discuss.ardupilot.org/t/bi-directional-dshot-support/70210, 2026-11-15) say stock BLHeli_S lacks it and Bluejay on BLHeli_S works from v0.19 (forum, not official).
- Holybro pages say ArduPilot 4.5.6+ (https://docs.holybro.com/autopilot/kakute-f405-wing-mini/overview) and nothing on DShot; which Kakute outputs can do bidirectional is `—`.
- Result: stock P04 cannot be assumed to give rpm. A.param is set to the throttle-referenced notch (MODE 1) and BDMASK 0; M4 stays on the list. If M4 needs Bluejay, that is a firmware flash on a bought board (risk: bricking the only board), so try it on the bench only after M1-M3. The ESC page also shows no AM32 alternative in stock; the O3 Tekko32 (AM32, bidirectional capable per AM32 family, page silent) was dropped by the board on cost ($49.55).

## 4. Order 1 (`ORDER-1.csv`)

24 lines. Contents: bench parts (B01, B02, B03, B04, G01-G04, SparkFun cell + HX711), concept-neutral avionics and power (V01, V02, V03, V05, W01-W06), stock-risk lines (P01 motors, P02 props, P04 ESC, V04 GPS, R03 PETG). **Excluded**: R04 (removed), tubes R02 / R08-R10, servos M01 / M02, foam R01, epoxy / CA R05 / R07, struts R06, anemometer G05 (all main order or borrowed).

| | $ |
|---|---|
| Goods 827.91 + tax 84.86 + shipping `EST` 55.13 (RMRC 15, T-Motor, Amazon, Prusa 10.71 each, SparkFun 8) | **967.90** with 2 MN2212 |
| +3 MN2212 (3 x 46.90 x 1.1025, same shipment) | +155.12 |
| **Order 1, all 5 motors** | **1,123.02** |

T-Motor: ask for stock and lead time for 5 x MN2212 V2.0 KV780 (store contact; ask also whether the order ships free express at >= $200 as the page text says, not relied on). **If no answer by 2026-12-04, Order 1 buys all 5.** I did not send anything (no message sent on the user's behalf). Three lines (B03, B04, the Amazon part of G02) are `EST` prices and not read; Order 1 is therefore an estimate +-$15.

## 5. What needs a re-run (not done here)

1. **SITL**, as-drawn aircraft (BOARD 7.2 #2): elevon y 0.04-0.34 / +-20 deg now in `a_aero.py`; still to set: CAD CG (16.2 mm, then post-pack-move 20-24), inertias, prop plane 121 mm; transition, back-transition at 0 / 45 / 90 deg, cruise trim, roll rate, weathervane in turbulence, fence during QLAND. Elevon servo scaling in A.param (SERVO5/6 MIN/MAX) is a bench item.
2. **FE / structures**: `iter2_run.py` and `iter2_eval.py` (sweep, cruise 7,300-7,600, strong >= 0.5; `iter2_run.md` / `iter2_margins.md` / `structures_run.md` are stale), `structures_a.py` at VD 24 (gust n, hinge loads). Flutter / divergence estimate (G8) is new work. Not run because instructions forbid it and iter2_run overwrites its report.
3. **CAD gates** (`build_a.py`, `collide_a.py`, assembly sweep): FC now 3.5 mm lower on foam tape; pack move and tray slot (7.2 #2).
4. `fu_cage.py` gain-margin re-check once the tap test or hard mount changes the IMU stiffness; `fu_level.py` re-run for the VD 24 table and elevon stop.
5. `mission_gate_a.py` was re-run (it only prints; output cited above). `bom_a.py` was re-run.

## 6. Left alone, still stale

QP-3 reports (BOARD, COST-SCHEDULE, SITL-FLIGHT, STRUCTURES, CAD) are the review record and keep their old numbers. `bench/ORDER-LIST.csv` and `bench/order_total.py` are superseded by `ORDER-1.csv` (they still list O3 and O12, both dropped). `bench/bench_analysis.py` still uses 9545-era sample rpm in its synthetic rows. `sitl/runs/**` outputs reflect the old elevon, CG and rpm. `Q_WVANE` and the 4 flying-mornings commitment remain conditions, not facts.
