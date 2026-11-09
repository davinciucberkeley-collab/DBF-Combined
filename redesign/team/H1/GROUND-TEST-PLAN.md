# Ground test plan — K09-L

Owner H1 (ground test engineer). Status `PROPOSED`, revision H1-R1, 2026-11-09. Inputs re-read on this date:
`params/params.json` (A1-R2), `README.md`, `MASS-CG.md` (A3-R3). Every pass line below is a claim in
`team/H1/claims.json` (from `ground_tests.py`) or an owner's claim; re-run `python -I redesign/team/H1/ground_tests.py`
after any parameter change. The tests themselves (`T-…` ids) belong to the role that owns the claim they verify.
H1 builds the rigs, runs the cards, writes the logs, and the owner marks the test `run` with this card's log as evidence.

## Campaign order

One stand campaign on the early-order hardware (~20 Nov), finished before the mid-December order. Then the
build-phase tests on the real aircraft, in the order `R-TEST-ORDER` needs them (stand → weigh-in → tethered hover).

| Card | What | Tests run (owner) | Needs | Window |
|---|---|---|---|---|
| GT-01 | Stand build and calibration | `T-H1-STAND-CAL` (H1) | cells, HX711 ×2, Arduino, bearings, plywood | week of 23 Nov |
| GT-02 | Stand campaign, one station, isolated | `T-E1-MOTOR-RM` `T-E1-STAND` (E1), `T-B4-STAND` (B4), `T-C1-THRUST-FRESH` (C1), `T-A1-THRUST-STATION` (A1), `T-E2-IR` (E2) | 5 motors, 2 ESCs, 11×5.5MR + 11×4.5MR pairs, 2 packs | 25 Nov – 5 Dec |
| GT-03 | Installed run and fin swirl | `T-B4-INSTALLED` `T-B4-YAW` (B4) | 22 mm tube offcut, foam board, 0.32 m S5010 strip | 1 – 8 Dec |
| GT-04 | Motor, ESC and connector thermal | `T-J1-XT60-HEAT` (J1); evidence for `R-THERMAL`, `CL-E1-HOVER-DT` | IR thermometer, K thermocouple | with GT-02 |
| GT-05 | Pack weigh, capacity, IR at 25 and 10 °C | `T-E2-WEIGH` `T-E2-CAPACITY` `T-E2-IR` (E2) | scale, calipers, watt meter, fridge | on arrival |
| GT-06 | Weigh parts and the built aircraft | `T-A3-WEIGH-PARTS` (A3), `T-A1-WEIGH` (A1) | two 5 kg × 1 g scales, check mass | as parts arrive; build end |
| GT-07 | CG balance (x, y, z) | `T-B3-CG-BALANCE` (B3), `T-A3-CG-BALANCE` (A3), `T-A5-CG-BALANCE` (A5) | CG jig (two pin bridges) | build end |
| GT-08 | Wing proof load | `T-C1-WING-PROOF` (C1) | sandbags, pod cradle, dial gauge | first finished wing |
| GT-09 | Station, fin and tube loads; tap test | `T-C1-STATION-PROOF` (C1), `T-J1-TUBE-BEND` `T-J1-TAP-TEST` (J1) | weights, spring scale, phone accelerometer | first fin assembly |
| GT-10 | Pack retention and foot drop | `R-PACK-RETENTION` pull, `T-C1-FOOT-DROP` (C1) | 680 g pack dummy, 10 kg spring scale | build end |
| GT-11 | Tip-over board | `R-TIPOVER`, `CL-C1-TIPOVER-WITH-FOOT` | hinged board, inclinometer app | build end |
| GT-12 | Controls and bench electrics, props off | `T-B2-HINGE` (B2), `R-ARM-KILL`, `R-FAILSAFES`, `R-AVIONICS-POWER` | servo load weights, multimeter | before GT-13 |
| GT-13 | Restrained four-motor run | `R-ESC-CURRENT` limiter, `R-COMPASS` compassmot, `R-VIBRATION` bench VIBE | restraint table, `T-H1-RESTRAINT-PULL` | before tethered hover |
| GT-14 | RC range check | `R-FAILSAFES` RC loss, range at reduced power | second person, 100 m tape or GPS | before every first flight of the day |

## Rules for every props-on card

| Rule | Value | Source |
|---|---|---|
| Nobody in the prop plane ±30°; operator behind the stand, in line with the axis | — | H3 prop safety (`R-ARM-KILL`) |
| Arm switch and a hard kill (pack disconnect within reach) on every run | stop ≤ 1 s | `P:requirements.estop_time_max_s` |
| Full-throttle steps on a 16.8 V pack held ≤ 2 s, then ≥ 60 s at idle | step ≤ 55 A | `CL-H1-STEP-I` 51.6 A vs `ASM-H1-ESC-BURST` |
| Bench supply only up to its rating; 70–100 % steps on a flight pack with V logged at the ESC | ≥ 44.6 A to hold 14.8 V | `CL-H1-SUPPLY-REQ` |
| LiPo: never charge below 10 °C or above 45 °C; cold pack bagged; LiPo sack and sand bucket on the bench | — | H3 battery procedure |
| Stand leads 12 AWG, XT60 at the stand; prop ≥ 1 D (0.28 m) from any upstream surface, ≥ 5 D clear downstream | — | stand practice |
| Every run logs ambient T, pressure and RH; thrust corrected to ρ = 1.225 kg/m³ | T_corr = T × 1.225/ρ | `P:env.rho_kgm3` |

## Evidence files (CR-A2-10)

A2's verification matrix checks `team/H1/claims.json` (this folder; exists). Raw data from each card goes to
`team/H1/logs/<test id>_<YYYYMMDD>.csv` (columns from `team/H1/templates/`), photos to
`team/H1/logs/<test id>_<YYYYMMDD>_NN.jpg`. Pack rows go to **E2's** `team/E2/pack_log.csv` (CR-E2-09). Part masses
go to `team/H1/logs/T-A3-WEIGH-PARTS_<date>.csv`; the owner copies each into its `parts.csv` / `interfaces.json`.
The owner then sets its `kit.test(..., state="run", result=…, measured=…, evidence=<log path>)` and re-runs.

## Card format

Every card has the same blocks, in this order. A card fits one printed page.

| Block | Content |
|---|---|
| Header | card id · title · tests run · requirement · status word |
| Setup | figure id (spec in *Figures and animations*), rig, instruments with range/resolution |
| Before | preconditions, calibration, safety stop items |
| Steps | numbered; each step names the value to record and the log column |
| Pass / fail | one row per criterion: measured quantity, limit, source claim; guard band stated |
| On fail | who gets the change request and what they re-run |

## GT-01 Stand build and calibration

Tests `T-H1-STAND-CAL`. Figure `FIG H1-01`.

| Item | Spec | Source |
|---|---|---|
| Thrust axis | motor mount on a horizontal axle in two 608 bearings; axle pushes a 20 kgf bar cell through a ball tip | `ASM-H1-THRUST-CELL` |
| Thrust range needed | 2.69 kgf (1.25 × 21.1 N) vs 20 kgf rated | `CL-H1-THRUST-CELL-REQ` |
| Torque | mount free to rotate about the shaft axis on the bearings; 0.100 m arm presses a 1 kgf bar cell | `ASM-H1-TORQUE-CELL` |
| Torque range needed | 0.54 kgf at the arm (1.25 × 0.42 N·m) vs 1 kgf rated; hover reads 115 gf | `CL-H1-TORQUE-CELL-REQ`, `CL-H1-TORQUE-F-HOVER` |
| Resolution | thrust noise 0.15 % of hover (need ≤ 0.5 %), torque 0.43 % (need ≤ 2 %) | `CL-H1-THRUST-RES`, `CL-H1-TORQUE-RES` |
| rpm | ESC telemetry (Bluejay bidirectional DShot through the FC log) and an optical tach cross-check at 3 points | CR-B4-09 |
| V, I | FC power module at the ESC input + a 100 A watt meter in series (cross-check) | `R-AVIONICS-POWER` ±5 % |
| Signal | the flight controller with F4's parameter file (motor test), so output cap and limiter are as flown | CR-H1-04 |

1. Build on 18 mm plywood clamped to a bench; prop axis 0.5 m above the bench, blowing away from the cells.
2. Hang 0.5, 1.0, 2.0, 2.5 kg on the thrust axis by a cord over the axis line (no pulley); record counts → `cal_thrust`.
3. Hang 50, 100, 200, 500 g at the 0.100 m arm mark; record → `cal_torque`.
4. 60 s at zero load on both cells, 80 SPS; record the 2σ noise.
5. Repeat steps 2–4 at the end of every session.

| Pass | Limit | Claim |
|---|---|---|
| Linearity, thrust cell | ≤ 0.5 % FS of the 2.5 kg span | `CL-H1-THRUST-CELL-REQ` |
| Linearity, torque cell | ≤ 1 % FS | `CL-H1-TORQUE-CELL-REQ` |
| 2σ noise / hover value | ≤ 0.005 thrust, ≤ 0.02 torque | `CL-H1-THRUST-RES`, `CL-H1-TORQUE-RES` |
| Start/end calibration drift | ≤ 0.5 % | session valid |

On fail: shield the HX711 leads, shorten them, re-seat the cell; a session that fails step 5 is repeated.

## GT-02 Stand campaign, one station, isolated

Tests `T-E1-MOTOR-RM`, `T-E1-STAND`, `T-B4-STAND`, `T-C1-THRUST-FRESH`, `T-A1-THRUST-STATION`, `T-E2-IR`
(load-step part). CRs CR-E1-11, CR-B4-09, CR-B1-16, CR-C1-07, CR-B1-06. Figure `FIG H1-01`.

**2a Incoming check, all 5 motors and the ESCs (`T-E1-MOTOR-RM`).**

1. Weigh motor, ESC, prop, adapter set, screws (0.1 g scale) → `logs/T-E1-MOTOR-RM_<date>.csv`.
2. Calipers: base bolt pattern, screw-hole depth, lead length, body length, adapter base and post.
3. Rm: 2.00 A from the bench supply through two phases (line-to-line), read the drop at the motor leads with a
   separate meter (4-wire); three phase pairs; record winding temperature; correct to 25 °C with 0.393 %/K.
4. I0 and Kv: no prop, 10.0 V, 30 s warm-up, read current and rpm; Kv = rpm / (V − I0·Rm).

| Pass (accept for flight) | Limit | Source |
|---|---|---|
| Rm, line-to-line at 25 °C | 86 mΩ ± 20 % (69–103 mΩ) | `ASM-E1-RM` (E1 confirms line-to-line, CR-H1-05) |
| I0 at 10 V | 0.9 A ± 30 % | `ASM-E1-I0` |
| Kv | 900 rpm/V ± 5 % | `ASM-E1-KV` |
| Spread across the 4 flight motors | Kv ≤ 3 %, Rm ≤ 10 %, I0 ≤ 20 % | any motor failure is fatal (`CONFIGURATION.md`); fit the spare instead of an outlier |

On fail: E1 replaces `ASM-E1-RM` / `-I0` with the measured mean and re-runs `propulsion.py`; an outlier motor goes
to the spares box.

**2b A/B sweep, 11×5.5MR vs 11×4.5MR (`T-E1-STAND`, `T-B4-STAND`).** Same motor, same ESC, same pack state.

1. Order A B B A (two runs each), props balanced, same nut torque (1.5 N·m, `ASM-C1-PROP-NUT-TORQUE`).
2. 0 → 100 % throttle in 10 % steps, 3 s per step, mean of the last 2 s: thrust, torque, rpm, V, I, throttle.
   0–60 % on the held 14.8 V supply; 70–100 % on a flight pack at 15.2 ± 0.1 V rest, V logged.
3. Hover point: 60 s at 690 gf (B1 calibration point, `CL-B1-KCAL`; B4 hover 6.76 N): g/W, torque, rpm, can T.
4. Ten 10 → 100 % punches (< 50 ms ramp): no desync, no ESC reset (CR-E1-11).

| Pass | Limit | Source |
|---|---|---|
| Repeatability, A vs A at the hover point | ≤ 1 % power | needed to resolve 1.9 % (`CL-B1-HOVER-PROP-RATIO` 1.019) |
| Hover pack power, chosen prop, × 4 | report vs 343 W (5.5MR) / 333 W (4.5MR) | `CL-B4-HOVER-W`, `-OLD` |
| Hover torque | report vs 0.113 N·m | `CL-B4-HOVER-Q` |
| Full-throttle rpm, 5.5MR, 14.8 V | ≤ 9 545 rpm cap | `CL-B4-RPM-MAX` |
| Punch test | 10 of 10 clean | `CL-E1-MAKER-SUPPLY` |

Decision rule (E1/B4 decide, H1 reports): keep the 11×5.5MR unless the 4.5MR gives ≥ 3 % lower hover power at equal
thrust **and** ≥ 1.38 kgf at the limiter share. On fail of repeatability: re-mount, re-balance, repeat.

**2c B1 points (CR-B1-16).** Static at 690 gf; full throttle at 14.0 V; full throttle at 13.6 V with the per-motor
limiter share active (25 A). Report rpm against `CL-B1-NMAX-SAG` 116.9 rev/s (7 015 rpm).

**2d Peak thrust and torque, fresh 16.8 V pack (`T-C1-THRUST-FRESH`, CR-C1-07).** Replaces
`requirements.thrust_limit_per_motor_n` (17.8 N).

1. Pack charged to 4.20 V/cell, rested 10 min, 25 ± 3 °C.
2. FC output cap as in F4's file, limiter disabled (unlimited case): step 10 → 100 % for 2 s; three steps, 60 s apart.
3. Repeat with `Q_M_BAT_CURR_MAX` set to 25 A (one motor's share of 100 A) to measure the limited thrust.
4. Record peak thrust, peak torque, peak current, rpm, V at the ESC.

| Pass | Limit | Source |
|---|---|---|
| Peak thrust, unlimited, at the cap | ≤ 21.1 N (C1 limit thrust); measured value goes to A1 | `CL-C1-T-LIMIT`, CR-H1-01 |
| Peak torque | ≤ 0.42 N·m | `CL-C1-MOTOR-TORQUE` |
| Peak current, unlimited, 16.8 V | ≤ 55 A (abort above) | `CL-H1-STEP-I` 51.6 A predicted |
| Limited thrust, fresh pack (T/W 2.0 incl. download 1.06) | ≥ 1.378 kgf | `CL-H1-T-PASS-FRESH` → `R-HOVER-TW` |
| Per-motor current with the limiter | ≤ 25 A | `R-ESC-CURRENT` (b), `CL-E1-ILIM-I` |

On fail: peak > 21.1 N → C1 re-runs every load case with the measured value (A1 updates the parameter);
limited thrust < 1.378 kgf → E1/A1 (`R-HOVER-TW` fails; prop or limiter decision).

**2e Worst pack state (`T-A1-THRUST-STATION` sag case, `T-E2-IR`).**

1. Pack discharged on the stand to 3.60 V/cell rest (20 %), bagged, 1 h in a fridge to 10 ± 2 °C (probe on the pack).
2. Rest voltage; 20 A step for 2 s: R = ΔV/ΔI per cell → `pack_log.csv` `ir_mohm_cell_10c`.
3. Full throttle with the limiter share for 2 s: thrust, V.

| Pass | Limit | Source |
|---|---|---|
| Full-throttle thrust, 3.6 V/cell, 10 °C | ≥ 1.102 kgf (T/W 1.6) | `CL-H1-T-PASS-SAG` → `R-HOVER-TW` |
| IR at 10 °C | ≤ 7.5 mΩ/cell | `CL-H1-PACK-IR10-MAX` |

## GT-03 Installed run and fin swirl

Tests `T-B4-INSTALLED`, `T-B4-YAW`. Figure `FIG H1-02`, animation `ANIM H1-A3`.

Mock-up mounted **on the measuring carriage** (the cell then reads net thrust, which is what the aircraft feels):
22 mm tube with its face 39 mm behind the prop plane; a 0.275 m-chord foam-board half-fin (4.8 mm, two layers) from
the tube aft; a 0.32 m S5010 wing strip whose crest sits 28 mm below the disc edge, LE 5 mm behind the prop plane.

1. Configurations, each at equal rpm (hover 5 400 rpm, `CL-B4-HOVER-RPM`, and 7 000 rpm): bare · tube · tube + fin ·
   tube + fin + strip. Order randomised, bare repeated last.
2. Repeat tube + fin + strip with the mock-up bolted to the bench instead of the carriage: separates rotor thrust
   change from download.
3. Torque at hover thrust with and without the fin (`T-B4-YAW`).

| Pass | Limit | Source |
|---|---|---|
| Download factor (bare / installed net thrust at equal rpm) | ≤ 1.06 | `CL-B4-DOWNLOAD`, `P:propulsion.download_factor` |
| Yaw torque with fin / without | report vs 0.48 | `CL-B4-YAW` |
| Wool tufts on the strip upper surface | no tuft driven by the slipstream | `CL-B4-WING-GAP` |

On fail: download > 1.06 → A1 updates `propulsion.download_factor`; E1 and B1 re-run T/W.

## GT-04 Motor, ESC and connector thermal

Evidence for `R-THERMAL`, `CL-E1-HOVER-DT`; runs `T-J1-XT60-HEAT`. ESC taped to the half-fin mock-up in the wash, as installed.

1. 120 s at hover thrust (690 gf) then 10 s at the limiter share (25 A), then 60 s hover; ambient logged.
2. IR on the can (matte tape spot), ESC FETs and the XT60 within 10 s of stop; thermocouple on the can during the run.
3. `T-J1-XT60-HEAT`: 37 A through a mated XT60 pair for 10 min on the stand (pack), thermocouple on the pins.

| Pass | Limit | Source |
|---|---|---|
| Motor can rise above ambient | ≤ 50 K (predicted 21 K) | `CL-E1-HOVER-DT` |
| ESC case | ≤ 80 °C at 30 °C ambient (scaled) | `R-THERMAL` (E3 to confirm the line, CR-H1-06) |
| XT60 rise at 37 A, 10 min | ≤ 60 K | `T-J1-XT60-HEAT` |
| Main lead rise at hover current | ≤ 10 K | `P:electrical.wire_temp_rise_max_c` |

On fail: E3 re-runs the heat balance with the measured rise; the field-ambient ceiling on the flight card moves.

## GT-05 Packs: weigh, capacity, IR

Tests `T-E2-WEIGH`, `T-E2-CAPACITY`, `T-E2-IR`. One row per pack (`E2-P1`, `E2-P2`) in `team/E2/pack_log.csv`.

1. On arrival: storage-voltage check per cell (balance lead), mass on a 1 g scale incl. leads, L × W × H incl. lead exit.
2. Charge 1C; rest 1 h; IR by a 20 A step on the stand at 25 °C (GT-02 method).
3. Capacity: discharge through the stand at ~6.5 A to 3.5 V/cell under load, watt meter mAh.
4. Recharge to storage; IR at 10 °C in GT-02e.

| Pass | Limit | Source |
|---|---|---|
| Mass incl. leads | ≤ 680 g (carried 550 g) | `CL-E2-PACK-MASS`; A3 re-runs with the value |
| Fits the pod bay | ≤ 160 × 52 × 53 mm | `README.md` pod bay |
| Capacity at 1C | ≥ 5.98 Ah | `CL-H1-PACK-CAP-MIN` (`P:requirements.pack_capacity_min_frac`) |
| IR at 25 °C | ≤ 5 mΩ/cell | `T-E2-IR` |
| Cell spread on arrival | ≤ 0.02 V | H3 battery procedure |

On fail: a pack failing capacity or IR is not a flight pack; E2 re-runs the energy budget.

## GT-06 Mass

Tests `T-A3-WEIGH-PARTS`, `T-A1-WEIGH`.

1. Calibrate both scales with the 2.000 kg check mass, 10 readings each (`T-H1-SCALE-CAL`).
2. Every bought part on arrival, every made part when finished → log, `mass_g` per unit.
3. Ready to fly: pack in, props on, pitot boom on, straps closed. Three readings, aircraft re-placed between them.

| Pass | Limit | Source |
|---|---|---|
| Scale U95 | ≤ 5.2 g; ≤ 10 % of A3's gate margin | `CL-H1-WEIGH-U95`, `CL-H1-WEIGH-U-FRAC` |
| Ready-to-fly mass (mean) | ≤ 2.595 kg (gate − U95) | `CL-H1-WEIGH-ACCEPT` → `R-MASS-GATE` |
| Each subsystem vs allocation | ≤ `mass.allocation_g.*` | `R-MASS-ALLOC` (A3) |

On fail: A3 re-runs the roll-up; A1 releases reserve or orders the cut list.

## GT-07 CG balance

Tests `T-B3-CG-BALANCE`, `T-A3-CG-BALANCE`, `T-A5-CG-BALANCE`. Figure `FIG H1-03`.

Jig: two bridges, one on each scale; padded pins under the wing outboard of the fins at |y| = 0.45 m, front pins at
x = 0.010 m, rear pins at x = 0.230 m (ahead of the elevon hinge), wing raised ≥ 0.25 m so the lower motors clear.

1. Ready to fly, cruise attitude, elevons neutral. Read W1 (front), W2 (rear). x = 0.010 + 0.220 · W2 / (W1 + W2).
2. y: roll the jig 90° (pins under the LE and TE at the root, one scale per side) or balance on a knife edge at
   y = 0; |y| ≤ 5 mm.
3. z: raise the rear bridge by h = 60 mm, re-read; z from the shift of the reaction (tilt method).
4. Draw the B3 limits and the measured x at both fin roots (B3's marks).
5. Repeat with the pack slid ±30 mm (trim range check).

| Pass | Limit | Source |
|---|---|---|
| Jig U95 in x | ≤ 0.6 mm; ≤ 0.5 × half-range | `CL-H1-CG-U95`, `CL-H1-CG-U-FRAC` |
| x, guard-banded | 0.0406 ≤ x ≤ 0.0484 m | `CL-H1-CG-ACCEPT-FWD`, `-AFT` → `R-CG-RANGE` |
| y | ≤ 0.005 m | `P:requirements.cg_lateral_max_m` |
| z | −0.02 … +0.03 m | `P:cg.z_range_m` |

On fail: slide the pack (0.26 mm CG per mm, `CALC-A3-CG`); outside the slide range → A3/A1 (ballast counts in the gate).

## GT-08 Wing proof load

Test `T-C1-WING-PROOF`. Figure `FIG H1-04`. Interim loads from C1 ultimate / 1.5 until C1 issues the whiffletree (CR-H1-03).

1. Wing upside-down, supported on a cradle at the pod and root (y ±0.07 m), fins and motors fitted or dummy masses.
2. Sandbags on a padded spanwise pad at y = ±0.328 m: 25 %, 50 %, 75 %, 100 % of 28.5 N per side (2.90 kg), 30 s each.
3. Tip deflection at each step (ruler on a fixed stand); unload; read again after 5 min.

| Pass | Limit | Source |
|---|---|---|
| No crack, skin wrinkle, spar-slot bond line or core crush | visual + tap | `R-STRUCT-MARGIN` |
| Tip deflection at 100 % | ≤ 28.8 mm | `CL-H1-WING-DEFL-MAX` (`requirements.spar_deflection_max` × b/2) |
| Permanent set after 5 min | ≤ 1 mm | proof practice |

On fail: stop; C2 re-sizes the spar slot / skin. Ultimate (1.5 ×) only on a sacrificial test core, never on the flight wing.

## GT-09 Station, fin and tube loads; tap test

Tests `T-C1-STATION-PROOF`, `T-J1-TUBE-BEND`, `T-J1-TAP-TEST`. Figure `FIG H1-05`.

1. `T-J1-TUBE-BEND` on a spare tube before bonding: span 0.8 m, centre load in 0.5 kg steps to 4 kg, dial gauge.
2. Station proof: wing held at the spar; hang 19.6 N (2.0 kg) from each motor mount in −x and in y; then 46.0 N
   (4.69 kg) side load at the motor station in y; 30 s each.
3. Tap test: half-fin assembly clamped at the through-core block; tap the motor; phone accelerometer at ≥ 400 Hz
   (or FC raw IMU); FFT.

| Pass | Limit | Source |
|---|---|---|
| Mount proof, no slip or crack | 19.6 N held 30 s | `CL-H1-MOUNT-PROOF-F` |
| Fin + tube proof, no permanent set | 46.0 N held 30 s | `CL-H1-FIN-PROOF-F` |
| First mode outside 72–374 Hz (or damping recorded) | ≥ 20 % separation | `CL-J1-TUBE-MODE-SEP` → `R-VIBRATION` |
| Tube modulus | report E; replaces `ASM-J1-E-TUBE` | `CL-J1-TUBE-F1` |

On fail: C4 re-sizes the clip/fin bond (the bare tube already fails separation, so the fin must stiffen it).

## GT-10 Pack retention and foot drop

| Step | Pass | Source |
|---|---|---|
| 680 g pack **dummy** (plywood + sand, never a LiPo) strapped as flown; spring scale pull in ±x, ±y, +z | holds 85 N, slip ≤ 5 mm, hatch closed | `CL-H1-PACK-PULL-F` → `R-PACK-RETENTION` |
| `T-C1-FOOT-DROP`: 0.115 m free drop on the feet (1.5 m/s), level, then 10° tilted; accelerometer at the CG | n ≤ 6; damage only in the feet; foot replaced ≤ 10 min | `CL-C1-N-LAND-STROKE-MIN`, `R-LANDING-IMPACT` |

First drops with a 2.6 kg dummy on one fin (C1's option), then the aircraft without pack (dummy mass), never with a LiPo.

## GT-11 Tip-over board

Figure `FIG H1-06`, animation `ANIM H1-A1`. Aircraft standing on its four feet, ready to fly mass (pack dummy), on a
hinged 1.2 × 0.6 m board with sandpaper; hinge parallel to the narrow axis (the 0.38 m foot pair).

1. Raise the board slowly (≈ 2°/s) with a strap; phone inclinometer on the board; a second person ready to catch.
2. Record the angle when the uphill feet lift. Three runs each way; then the wide axis.

| Pass | Limit | Source |
|---|---|---|
| Narrow-axis tip angle (mean of 3) | ≥ 30° | `P:requirements.tipover_min_deg`, `CL-C1-TIPOVER-WITH-FOOT` → `R-TIPOVER` |
| Feet do not slide before lifting | no slide | `CL-C1-STANCE-MU-REQ` |

## GT-12 Controls and bench electrics, props off

| Step | Pass | Source |
|---|---|---|
| Motor test in the GCS: order UR UL LR LL and rotation direction match F4's output map | all four correct | `R-FSW-PARAMS` |
| Motor cant: angle gauge on each mount | 3.0 ± 0.5°, direction per station | `P:propulsion.stations.cant_deg` |
| Elevon throws, both panels per side, protractor at the TE | ±25° ± 2°; inboard and outboard within 2° | `P:wing.elevon.deflection_deg` |
| Elevon directions in FBWA and in QHOVER (pitch, roll stick and attitude) | correct sense in both modes | F4 file, `ANIM H1-A2` |
| `T-B2-HINGE`: weight for the hinge moment at the panel mid-chord, ±25° | servo holds, linkage does not slip | `CL-B2-SERVO-TORQUE-REQ` → `R-SERVO-TORQUE` |
| Both servos stalled, FC rail voltage | ≥ 4.8 V | `R-AVIONICS-POWER` |
| BAT.Curr vs meter at 5 A and 20 A (stand) | ±5 % | `R-AVIONICS-POWER` |
| Arm refused with a failed check; emergency stop switch to zero rpm in the log | stop ≤ 1 s | `R-ARM-KILL` |
| Transmitter off → failsafe action; low-voltage simulated → return / land | action as in F4's file | `R-FAILSAFES` |

## GT-13 Restrained four-motor run

Figure `FIG H1-07`. Aircraft on its feet on a 18 mm plywood table, strapped at the four fin roots to eye bolts.
Before the run, `T-H1-RESTRAINT-PULL`: each strap pulled to 29.4 N (total 117.7 N = 2 × (4 × 21.1 N − 25.5 N)).

| Step | Pass | Source |
|---|---|---|
| Full throttle 2 s in QSTABILIZE, fresh pack | BAT.Curr ≤ 100 A | `R-ESC-CURRENT` (a), `P:performance.full_throttle_current_a` |
| compassmot, throttle to hover current (27 A) | interference ≤ 30 % | `R-COMPASS` |
| GPS mast to the nearest main power lead (ruler) | ≥ 0.10 m | `P:requirements.gps_mast_clearance_m` |
| 30 s at hover throttle, VIBE log | < 30 m/s², Clip 0 (indicative; H2 confirms in hover) | `R-VIBRATION` |
| HDOP before arming (outdoors) | ≤ 1.2 | `P:requirements.hdop_max` |

## GT-14 RC range check

1. ELRS at 10 mW (Lua), telemetry LQ on the transmitter; aircraft on its feet, props off, motors armed in a safe test mode.
2. Walk to 100 m line of sight; wiggle sticks; check servo response; switch the transmitter off at 100 m.

| Pass | Limit | Source |
|---|---|---|
| LQ at 100 m, 10 mW | ≥ 90 % | `P:requirements.rc_lq_min`, `P:requirements.range_check_min_m` |
| Failsafe on transmitter off | QLAND/QRTL as set | `R-FAILSAFES` |

## Figures and animations

Rendered by `redesign/blender/` from the CAD geometry, styled per `design-system/BLENDER-STYLE.md`: act parts orange,
built parts real material, context ghosted; callout numbers = card step numbers. Animations 3–10 s loops, ≤ 1080p,
< 3 MB MP4 H.264 (+ WebM if small), poster PNG for print, autoplay-muted-loop with controls. Still where a still is enough.

| Id | Kind | Shows | Act (orange) | Camera | Callouts |
|---|---|---|---|---|---|
| `FIG H1-01` | still | thrust stand, isolated, with arrows for thrust and torque paths | axle, both cells, torque arm | iso 35°, 50 mm | 1 thrust cell, 2 torque arm 100 mm, 3 tach, 4 watt meter, 5 kill |
| `FIG H1-02` | still | installed mock-up on the carriage, side view | tube, half-fin, wing strip | side, ortho | 39 mm tube gap, 28 mm crest gap, 0.275 m chord, 5 mm LE |
| `FIG H1-03` | still | CG jig with aircraft, two scales | pin bridges, scales | front-iso 30° | x1 0.010, x2 0.230, \|y\| 0.45, ≥ 0.25 m clearance |
| `FIG H1-04` | still | wing proof: cradle, sandbag pads | pads, sandbags | front, low | y 0.328 m, deflection ruler |
| `FIG H1-05` | still | station proof hang, −x and y | weights, cords | iso | 19.6 N, 46.0 N |
| `FIG H1-06` | still | tip-over board at 30° | board, strap | side along the hinge | angle arc 30°, catch person zone |
| `FIG H1-07` | still | restrained four-motor table | straps, eye bolts | iso 45°, high | strap 29.4 N each, keep-out ±30° |
| `ANIM H1-A1` | 6 s loop | board raises 0 → 32°, uphill feet lift at 30°, holds | board, lifting feet | as `FIG H1-06` | live angle readout |
| `ANIM H1-A2` | 8 s loop | pitch stick then roll stick in FBWA, then QHOVER: elevon panels move, arrows give the expected sense | elevon panels | rear-iso 30° | mode label, stick icon |
| `ANIM H1-A3` | 8 s loop | the four mock-up configurations swap in (bare → tube → fin → strip) | the part being added | as `FIG H1-02` | config name, net thrust ratio placeholder |

## Rig parts and cost (EST, not flying mass)

| Item | Qty | EST $ | Note |
|---|---|---|---|
| 20 kgf bar cell + HX711 | 1 | 10 | thrust |
| 1 kgf bar cell + HX711 | 1 | 8 | torque |
| Arduino Nano (or team spare) | 1 | 0–20 | logs both cells over USB |
| 608 bearings, M8 rod, plywood, fasteners | — | 15 | stand frame |
| 100 A watt meter | 1 | 20 | V, I, mAh cross-check |
| Optical tachometer | 1 | 20 | rpm cross-check |
| 5 kg × 1 g scales | 2 | 30 | weigh and CG jig |
| IR thermometer, K thermocouple meter | 1 each | 30 | thermal (may be borrowed from Jacobs) |
| 10 kg spring scale, sandbags, straps, eye bolts | — | 20 | proof, retention, restraint |
| 11×4.5MR/MRP pair for the A/B | 1 | 8 | CR-E1-11 |
| **Total** | | **≈ 160–180** | CR-H1-02 to A1: count against the $2 000? |
