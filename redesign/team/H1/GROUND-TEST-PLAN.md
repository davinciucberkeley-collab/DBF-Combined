# Ground test plan — K09-L

Owner H1 (ground test engineer). Status `PROPOSED`, revision H1-R2, 2026-11-09. Inputs re-read on this date:
`params/params.json` (A1-R3), `README.md`, `MASS-CG.md` (A3-R4), and the `claims.json` test nodes of A1, A3, A5, B2–B4,
C1–C6, D5, E1–E3, F1, F3–F5, J1. Every pass line below is a claim in `team/H1/claims.json` (from `ground_tests.py`)
or an owner's claim. Re-run `python -I redesign/team/H1/ground_tests.py` after any parameter change. The tests
(`T-…` ids) belong to the role that owns the claim they verify. H1 builds the rigs, runs the cards and writes the
logs, and the owner marks the test `run` with the H1 log as evidence.

R2 changes (CR-A1-41 and the requests it collects): GT-02d against the 21.1 N parameter with a guard band, GT-02e
cold pack with a guard band, GT-04 with E3's lines and the 600 s step, GT-08 on C1's four-pad whiffletree, GT-12
with F3/F5 bench tests, GT-14 = `T-F5-RANGE` at 25 mW, and four new cards: GT-15 coupons, GT-16 tube tests (Aloft,
by 10 Dec), GT-17 mount stiffness, GT-18 tap tests. Test gear: one new purchase (I1 line G12, $17.00); everything else
is borrowed. The borrow list is at the end.

## Campaign order

| Card | What | Tests run (owner) | Window |
|---|---|---|---|
| GT-01 | Stand build and calibration | `T-H1-STAND-CAL`, `T-H1-RIG-CHECK` (H1) | 23–25 Nov |
| GT-02 | Stand campaign, one station | `T-E1-MOTOR-RM` `T-E1-STAND` (E1), `T-B4-STAND` (B4), `T-C1-THRUST-FRESH` (C1), `T-A1-THRUST-STATION` (A1), `T-E2-IR` (E2) | 25 Nov – 5 Dec |
| GT-03 | Installed run, fin swirl | `T-B4-INSTALLED` `T-B4-YAW` (B4) | 1 – 8 Dec |
| GT-04 | Motor, ESC, wire and connector thermal | `T-E3-MOTOR-TAU` `T-E3-ESC-PAD` (E3), `T-F1-WIRE-HEAT` `T-F1-CONN-HEAT` (F1) | with GT-02, ≤ 8 Dec |
| GT-05 | Packs: weigh, capacity, IR | `T-E2-WEIGH` `T-E2-CAPACITY` `T-E2-IR` (E2) | on arrival |
| GT-16 | Tube bend and torsion (Aloft `W03`) | `T-C4-TUBE-BEND` (= `T-J1-TUBE-BEND`), `T-C4-TUBE-TORSION` (C4) | tube arrives ~27 Nov; **result to I1 by 10 Dec** |
| GT-17 | Mount rocking stiffness | `T-C4-MOUNT-STIFF` (C4), `T-C6-CANT-SEAT` `T-C6-PROPNUT` (C6) | first printed ASA mount (Dec) |
| GT-15 | Coupons | C2, C3, C4, C6, D5 coupon tests (table in GT-15) | first prints and foam, Dec – 16 Jan |
| GT-06 | Weigh parts and aircraft | `T-A3-WEIGH-PARTS` (A3), `T-A1-WEIGH` (A1) | as parts arrive; build end |
| GT-07 | CG balance | `T-B3-CG-BALANCE` (B3), `T-A3-CG-BALANCE` (A3), `T-A5-CG-BALANCE` (A5) | build end |
| GT-08 | Wing proof and twist | `T-C1-WING-PROOF` (C1), `T-C2-WING-PROOF` `T-C2-TWIST` (C2) | first finished wing |
| GT-09 | Station, fin, block and pod proofs | `T-C1-STATION-PROOF` (C1), `T-C4-FIN-PROOF` `T-C4-BLOCK-PROOF` (C4), `T-C3-POD-PROOF` (C3), `T-D5-PROOF` `T-D5-SIDE` (D5) | first fin quarter, first pod |
| GT-18 | Tap tests | `T-C4-TAP-D3` (C4), `T-C2-TAP-TEST` (C2), `T-C4-PROP-SWING` (C4) | finished wing, props on |
| GT-10 | Pack retention, foot drops | `T-H1-PACK-PULL` (H1), `T-C5-FOOT-RIG` `T-C5-AIRCRAFT-DROP` (C5), `T-D5-REPLACE` (D5) | build end |
| GT-11 | Tilt board | `T-C5-TILT-BOARD` (C5) | build end |
| GT-12 | Bench electrics and controls, props off | `T-H1-ARM-KILL` (H1), `T-B2-HINGE` (B2), `T-F3-FW-LOAD` `T-F3-I2C-SCAN` `T-F3-5V` (F3), `T-F5-BENCH` `T-F5-FS-BENCH` (F5), `T-F1-SERVO-STALL` `T-F1-SENSOR-CAL` `T-F1-PRECHARGE` (F1) | before GT-13 |
| GT-13 | Restrained four-motor run | `T-H1-RESTRAINT-PULL` `T-H1-RESTRAINED-RUN` (H1), `T-F3-COMPASSMOT` (F3), `T-F1-RIPPLE` (F1) | before tethered hover |
| GT-14 | RC range check | `T-F5-RANGE` (F5) | before the first flight; then each flying day |

Tethered-hover tests (`T-F3-VIBE`, `T-F3-HDOP`, `T-E1-HOVER-LOG`, `T-C5-DRIFT-LOG`) are H2's; the flight-card items
from D-40, D-42 and C5's S1–S8 are H3's (CR-A1-41).

## Rules for every props-on card

| Rule | Value | Source |
|---|---|---|
| Nobody in the prop plane ±30°; operator behind the stand, in line with the axis | — | H3 prop safety |
| Arm switch and a hard kill (pack disconnect within reach) on every run | stop ≤ 1 s | `P:requirements.estop_time_max_s` |
| Full-throttle steps on a 16.8 V pack held ≤ 2 s, then ≥ 60 s at idle; abort above 55 A | 51.6 A predicted | `CL-H1-STEP-I`, `P:propulsion.esc_burst_a` |
| Jacobs bench supply only to its rating; 70–100 % steps on a flight pack with V logged at the ESC | ≥ 44.6 A to hold 14.8 V | `CL-H1-SUPPLY-REQ` |
| LiPo: charge 10–45 °C only; cold pack bagged; LiPo sack and sand bucket on the bench | — | H3 battery procedure |
| Leads 12 AWG; prop ≥ 1 D (0.28 m) from any upstream surface, ≥ 5 D clear downstream | — | stand practice |
| Log ambient T, pressure, RH; thrust corrected to ρ = 1.225 kg/m³ | T_corr = T × 1.225/ρ | `P:env.rho_kgm3` |

## Evidence files

Raw data `team/H1/logs/<test id>_<YYYYMMDD>.csv` (columns from `team/H1/templates/`), photos
`…_<YYYYMMDD>_NN.jpg`. Pack rows go to E2's `team/E2/pack_log.csv`; part masses to
`logs/T-A3-WEIGH-PARTS_<date>.csv`. The owner then sets `kit.test(..., state="run", result=…, measured=…,
evidence=<log path>)` and re-runs. A2's ids (CR-A2-25) are used unchanged.

## Card format

| Block | Content |
|---|---|
| Header | card id · title · tests run · requirement · status word |
| Setup | figure id (spec at the end), rig, instruments with range and resolution |
| Before | preconditions, calibration, safety stop items |
| Steps | numbered; each names the value and the log column |
| Pass / fail | one row per criterion: measured quantity, limit, claim; guard band stated |
| On fail | who gets the change request and what they re-run |

## GT-01 Stand build and calibration

Tests `T-H1-STAND-CAL`, `T-H1-RIG-CHECK`. Figure `FIG H1-01`.

| Item | Spec | Source |
|---|---|---|
| Thrust axis | mount on a horizontal axle in two 608 bearings; axle pushes the 20 kgf bar cell (I1 `G06`) | `ASM-H1-THRUST-CELL` |
| Thrust range needed | 2.69 kgf (1.25 × 21.1 N) vs 20 kgf | `CL-H1-THRUST-CELL-REQ` |
| Torque | 0.100 m arm on the 1 kgf bar cell (I1 `G12`) | `ASM-H1-TORQUE-CELL` |
| Torque range needed | 0.536 kgf vs 1 kgf; hover reads 116 gf | `CL-H1-TORQUE-CELL-REQ`, `CL-H1-TORQUE-F-HOVER` |
| Resolution | thrust 0.14 % of hover (need ≤ 0.5 %), torque 0.43 % (need ≤ 2 %) | `CL-H1-THRUST-RES`, `CL-H1-TORQUE-RES` |
| Thrust U95 after calibration | 0.123 N (0.5 % of the 2.5 kgf span) | `CL-H1-T-U95` |
| rpm | Bluejay bidirectional DShot via the FC log; phone audio FFT of blade pass at 3 points as a cross-check | CR-B4-09 |
| V, I | FC power module + the `G04` watt meter in series | `R-AVIONICS-POWER` ±5 % |
| Signal | FC with F4's `K09L-STAND.param` overlay (cap 0.84, 25 A limiter share) | CR-F4-06 |

1. 18 mm plywood clamped to the bench; prop axis 0.5 m up, blowing away from the cells.
2. Hang 0.5, 1.0, 2.0, 2.5 kg on the thrust axis by a cord on the axis line → `cal_thrust`.
3. Hang 50, 100, 200, 500 g at the 0.100 m arm mark → `cal_torque`.
4. 60 s zero load on both cells, 80 SPS; 2σ noise.
5. Repeat 2–4 at the end of every session.
6. `T-H1-RIG-CHECK`: optical-lever shim step, caliper on a 1.00 mm gauge block, 200 Hz tone on the FC raw IMU,
   phone inclinometer on a 30° printed wedge.

| Pass | Limit | Claim |
|---|---|---|
| Linearity, thrust / torque | ≤ 0.5 % / ≤ 1 % FS | `CL-H1-THRUST-CELL-REQ`, `-TORQUE-CELL-REQ` |
| 2σ noise / hover value | ≤ 0.005 thrust, ≤ 0.02 torque | `CL-H1-THRUST-RES`, `-TORQUE-RES` |
| Start/end drift | ≤ 0.5 % | `ASM-H1-CAL-U` |
| FC raw IMU rate | ≥ 935 Hz (tone found in the right FFT bin) | `CL-H1-TAP-FS-REQ` |

On fail: shield and shorten the HX711 leads, re-seat the cell; a session failing step 5 is repeated.

## GT-02 Stand campaign, one station, isolated

Figure `FIG H1-01`. CR-E1-11, CR-B4-09, CR-B1-16, CR-C1-07, CR-A1-41.

**2a Incoming check, 5 motors and the ESCs (`T-E1-MOTOR-RM`).** Weigh (0.1 g), calipers (bolt pattern, hole depth,
lead length, adapter). Rm: 2.00 A from the Jacobs bench supply line-to-line, 4-wire, three pairs, corrected to 25 °C
at 0.393 %/K. I0 and Kv at 10.0 V no prop.

| Pass | Limit | Source |
|---|---|---|
| Rm line-to-line, 25 °C | 86 mΩ ± 20 % | `ASM-E1-RM` (CR-H1-05) |
| I0 at 10 V / Kv | 0.9 A ± 30 % / 900 rpm/V ± 5 % | `ASM-E1-I0`, `ASM-E1-KV` |
| Spread, 4 flight motors | Kv ≤ 3 %, Rm ≤ 10 %, I0 ≤ 20 % | fit the spare instead of an outlier |

**2b A/B, 11×5.5MR vs 11×4.5MR (`T-E1-STAND`, `T-B4-STAND`).** Order A B B A; nut 1.5 N·m; 0 → 100 % in 10 % steps,
3 s each, mean of the last 2 s. 0–60 % on the held 14.8 V supply; 70–100 % on a pack at 15.2 ± 0.1 V rest. Hover
point 60 s at 690 gf. Ten 10 → 100 % punches (< 50 ms).

| Pass | Limit | Source |
|---|---|---|
| Repeatability A vs A at hover | ≤ 1 % power | resolves `CL-B1-HOVER-PROP-RATIO` 1.019 |
| Hover torque | report vs 0.114 N·m | `CL-B4-HOVER-Q` |
| Full-throttle rpm, 14.8 V | ≤ 9 545 rpm | `CL-B4-RPM-MAX` 9 319 |
| Punch test | 10 of 10 clean | `CL-E1-MAKER-SUPPLY` |

**2c B1 points (CR-B1-16).** Static at 690 gf; full throttle at 14.0 V and at 13.6 V with the 25 A share; rpm vs
`CL-B1-NMAX-SAG`.

**2d Peak thrust at the F4 cap, fresh 16.8 V pack (`T-C1-THRUST-FRESH`, CR-C1-07, CR-H1-01).**

1. Pack 4.20 V/cell, rested 10 min, 25 ± 3 °C; `K09L-STAND.param` loaded (Q_M_SPIN_MAX 0.84), limiter off.
2. Step 10 → 100 % for 2 s; three steps 60 s apart. Peak thrust, torque, current, rpm, V at the ESC.
3. Limiter share on (`Q_M_BAT_CURR_MAX` 25 A for one station): three steps; thrust and current.

| Pass | Limit | Claim |
|---|---|---|
| Peak thrust, max of 3, ρ-corrected | ≤ **20.98 N** pass; 20.98–21.1 N retest with 5 more steps; > 21.1 N fail | `CL-H1-T-PEAK-ACCEPT` (21.1 N − U95 0.12 N), `P:requirements.thrust_limit_per_motor_n` |
| Peak torque | ≤ 0.42 N·m | `CL-C1-MOTOR-TORQUE` |
| Peak current, unlimited | ≤ 55 A (abort) | `CL-H1-STEP-I` 51.6 A |
| Limited thrust, fresh | ≥ **1.391 kgf** | `CL-H1-T-FRESH-ACCEPT` (1.378 + U95) → `R-HOVER-TW` |
| Per-motor current, limiter on | ≤ 25 A | `CL-E1-ILIM-I` 24.75 A |

The prediction (`CL-C1-T-CAP` 21.08 N) sits inside the 0.12 N guard band, so a retest is likely. Whatever the
result, A1 sets `requirements.thrust_limit_per_motor_n` to the measured peak rounded up to 0.5 N (CR-H1-01); above
21.1 N, C1 re-runs every load case first. Limited thrust below 1.391 kgf → E1/A1 (`R-HOVER-TW`).

**2e Cold pack, 3.6 V/cell at 10 °C (`T-A1-THRUST-STATION` sag case, `T-E2-IR`).**

1. Discharge on the stand to 3.60 V/cell rest; bag; fridge 1 h to 10 ± 2 °C (thermocouple on the pack).
2. Rest V; 20 A step 2 s: R = ΔV/ΔI per cell → `pack_log.csv` `ir_mohm_cell_10c`.
3. Full throttle, limiter share on, 2 s: thrust, V. Repeat once after 60 s.

| Pass | Limit | Claim |
|---|---|---|
| Full-throttle thrust, cold 20 % pack | ≥ **1.115 kgf** (predicted 1.231) | `CL-H1-T-SAG-ACCEPT` (1.102 + U95) → `CL-H1-T-PASS-SAG`, `R-HOVER-TW` |
| IR at 10 °C | ≤ 7.5 mΩ/cell | `CL-H1-PACK-IR10-MAX` |

On fail: E2 and E1 replace `propulsion.voltage_sag` (0.76) with the measured ratio; A1 decides prop or limiter.

## GT-03 Installed run and fin swirl

Tests `T-B4-INSTALLED`, `T-B4-YAW` (B4's R3 procedure). Figure `FIG H1-02`, animation `ANIM H1-A3`. Mock-up on the
measuring carriage: printed 7° canted mount on a 22 mm tube cut to the R3 end (0.172 m from the chord plane), collars
with ears, one 10 × 3 mm brace to a dummy anchor, ESC dummy 8 × 28 × 46 mm on the pad, two-layer 0.21 m half-fin,
0.32 m S5010 strip. Measure the blade-tip gap over the tube by hand first.

1. Equal rpm (hover 5 416 rpm, `CL-B4-HOVER-RPM`; and 7 000 rpm): full mock-up, then remove brace + ESC, then the
   fin, then the strip; bare repeated last. Then full mock-up bolted to the bench (rotor vs download split).
2. `T-B4-YAW`: torque and fin side force at hover thrust, 7° mount then a 0° mount.

| Pass | Limit | Source |
|---|---|---|
| Download factor (bare / installed net thrust, equal rpm) | ≤ 1.06 | `CL-B4-DOWNLOAD`, `P:propulsion.download_factor` |
| Yaw factor | report vs `CL-B4-YAW` | B4 |
| Tufts on the strip | none driven by the slipstream | `CL-B4-WING-GAP` |

On fail: A1 updates `propulsion.download_factor`; E1 and B1 re-run T/W.

## GT-04 Motor, ESC, wire and connector thermal

Tests `T-E3-MOTOR-TAU`, `T-E3-ESC-PAD` (E3, CR-E3-06), `T-F1-WIRE-HEAT`, `T-F1-CONN-HEAT` (F1). The XT60 run
`T-J1-XT60-HEAT` is retired: F1's AS150U replaced the XT60. Instruments: 3 K-type bead probes (I1 `G12`) read on a
borrowed DMM with a K input (else I1 gated `X09`, $15); `G05` IR thermometer on matte-tape spots. Readings every 5 s
by filming the meter display.

1. Real printed ASA mount on the stand, 11×5.5MR, 14.8 V. Probes: stator (through the base vent), base-to-mount
   interface, ESC FETs under the heat-shrink. ESC strapped on the half-fin pad mock-up at x 0.101 m, 0.072 m from
   the axis, FET side out, in the wash; tuft on the pad.
2. **600 s at hover power (~100 W bus)**, log every 5 s (fit T = T∞ − (T∞ − T₀) e^(−t/τ); R_th = (T∞ − T_amb)/loss).
3. 30 s at 24.8 A (limiter share), then stop; IR on the can, FETs and connectors within 10 s.
4. Report each value as a rise above the ambient at the start, and as T₃₀ = T_meas − T_amb + 30 °C.
5. F1: 8 AWG pigtail in a closed pod mock-up at 30 A and the 16 AWG pair in a taped XPS channel at 8.4 A, 10 min
   each, probe mid-lead under 10 mm of foam tape; then 50 A for 2 s on the 16 AWG; AS150U pair 38 A 10 min.

| Pass | Limit | Claim |
|---|---|---|
| ESC FET-side rise at the end of step 3 | ≤ **33 K** | `CL-E3-GT04-ESC-RISE` |
| Motor can rise at the end of step 3 | ≤ **38 K** | `CL-E3-GT04-MOTOR-RISE` |
| Hard stop (abort the run) | ESC T₃₀ ≤ 70 °C, motor T₃₀ ≤ 80 °C | CR-E3-06 |
| Motor R_th / mount base at hover from 30 °C | ≤ 1.5 K/W / < 83 °C (ASA) | `T-E3-MOTOR-TAU` |
| ESC steady at hover from 30 °C | ≤ 70 °C | `T-E3-ESC-PAD` |
| Wire rise steady / peak | ≤ 10 K / ≤ 30 K | `T-F1-WIRE-HEAT` |
| AS150U rise, 38 A 10 min | ≤ 30 K | `T-F1-CONN-HEAT` |

On fail: E3 re-runs the heat balance with the measured R_th and wake factor; the field-ambient ceiling moves.

## GT-05 Packs: weigh, capacity, IR

Tests `T-E2-WEIGH`, `T-E2-CAPACITY`, `T-E2-IR`. One row per pack in `team/E2/pack_log.csv`.

1. Arrival: cell voltages, mass incl. leads (1 g), L × W × H incl. lead exit.
2. Charge 1C, rest 1 h; IR by a 20 A step on the stand at 25 °C.
3. Capacity: discharge through the stand at ~6.5 A to 3.5 V/cell under load, `G04` watt meter mAh.

| Pass | Limit | Source |
|---|---|---|
| Mass incl. leads | ≤ 680 g | `CL-E2-PACK-MASS`; A3 re-runs |
| Fits the pod bay | ≤ 160 × 52 × 53 mm | `README.md` |
| Capacity at 1C | ≥ 5.98 Ah | `CL-H1-PACK-CAP-MIN` |
| IR at 25 °C / spread on arrival | ≤ 5 mΩ/cell / ≤ 0.02 V | `T-E2-IR`, H3 |

## GT-06 Mass

Tests `T-A3-WEIGH-PARTS`, `T-A1-WEIGH`. Scale calibration `T-H1-SCALE-CAL` (2.000 kg check mass, 10 readings).

| Pass | Limit | Claim |
|---|---|---|
| Scale U95 | ≤ 5.2 g; ≤ 10 % of A3's 107 g margin | `CL-H1-WEIGH-U95`, `-U-FRAC` (4.9 %) |
| Ready-to-fly mass (mean of 3) | ≤ 2.595 kg | `CL-H1-WEIGH-ACCEPT` → `R-MASS-GATE` |
| Each subsystem | ≤ its allocation | `R-MASS-ALLOC` (A3) |

## GT-07 CG balance

Tests `T-B3-CG-BALANCE`, `T-A3-CG-BALANCE`, `T-A5-CG-BALANCE`. Figure `FIG H1-03`. Pins under the wing at
|y| 0.45 m (patch kept free, CR-H1-08), front x = 0.010 m, rear x = 0.230 m; wing ≥ 0.25 m up.
x = 0.010 + 0.220 · W2 / (W1 + W2). With one scale only: front pins on a fixed knife edge, W from GT-06.

| Pass | Limit | Claim |
|---|---|---|
| Jig U95 in x | ≤ 0.6 mm (25 % of the half-range) | `CL-H1-CG-U95`, `-U-FRAC` |
| x, guard-banded | **0.0506 ≤ x ≤ 0.0544 m** | `CL-H1-CG-ACCEPT-FWD`, `-AFT` → `R-CG-RANGE` (`P:cg.x_range_m` 0.050–0.055) |
| y / z | ≤ 0.005 m / −0.02 … +0.03 m | `P:requirements.cg_lateral_max_m`, `P:cg.z_range_m` |

On fail: slide the pack; outside the slide range → A3/A1.

## GT-08 Wing proof and twist

Figure `FIG H1-04`. `T-C1-WING-PROOF` on C1's whiffletree (CR-H1-03 answered; `team/C1/data/whiffletree.json`).

1. Aircraft inverted, supported under the pod (|y| ≤ 0.07 m), half-fins hanging free.
2. Four 40 × 40 mm pads per side over the spar line (x 0.08 m); sandbags weighed to ±5 g, applied in 25 % steps:

| Pad (per side) | y | Mass at limit | Claim |
|---|---|---|---|
| 1 | 0.120 m | 1.012 kg | `CL-H1-WP-M1` |
| 2 | 0.260 m | 0.814 kg | `CL-H1-WP-M2` |
| 3 | 0.355 m | 0.478 kg | `CL-H1-WP-M3` |
| 4 | 0.465 m | 0.652 kg | `CL-H1-WP-M4` (pad 4 only in C1's JSON, CR-H1-09) |
| Total | centroid 0.273 m | 28.99 N | `CL-H1-WING-PROOF-P` = `CL-C1-PROOF-P-SIDE-LIM` |

3. Hold 3 s at 100 %; tip deflection at each step (ruler on a fixed stand); unload; read again after 5 min.
4. `T-C2-TWIST`: pod clamped, 0.3 m lever on the right block, 1 kg (2.9 N·m), inclinometer at the block and tip.
5. `T-C2-WING-PROOF` (C2's outer-moment case 2 × 25 N per side over |y| 0.33–0.50, and 51 N at one upper tube end):
   **held** until C1 and C2 agree one limit case (CR-H1-13); it is 1.7 × C1's per-side total.

| Pass | Limit | Claim |
|---|---|---|
| No crack, wrinkle, bond-line or core crush | visual + tap | `R-STRUCT-MARGIN` |
| Tip deflection at 100 % | ≤ 28.8 mm | `CL-H1-WING-DEFL-MAX` |
| Permanent set after 5 min | ≤ 0.5 mm | C2 |
| Torsional stiffness | GJ ≥ 25 N·m² | `T-C2-TWIST` |

Ultimate (1.5 ×) only on a sacrificial core.

## GT-09 Station, fin, block, pod and foot proofs

Figure `FIG H1-05`. Loads hung by water jugs (weighed) or through the GT-15 lever frame.

| Test | Load | Pass | Article |
|---|---|---|---|
| `T-C1-STATION-PROOF` | 20.9 N (2.13 kg) at each mount in −x and y; 40.7 N (4.15 kg) at the station in y | no slip, crack or set | flight fins (`CL-H1-MOUNT-PROOF-F`, `-FIN-PROOF-F`) |
| `T-C4-FIN-PROOF` | 1.5 × L4 at the foot (49 N along + 25 N across), then 1.5 × G2 (77 N lateral at the tube end) | no crack or face wrinkle; foot deflection logged | **first fin quarter as a test article** (ultimate level) |
| `T-C4-BLOCK-PROOF` | 18 kg at 0.17 m (30 N·m) for 1 min | no creak, no bond-line crack | block on a spar stub in a 0.15 m core offcut |
| `T-C3-POD-PROOF` | dummy 680 g pack; pull down 64 N, up/aft/side 85 N, 10 s each | no crease at bond edges, nose, wall tops | built pod on the wing |
| `T-D5-PROOF` / `T-D5-SIDE` | 88 N along x at the pad edge, 3 s / 32 N in y then z with the insert 4 mm in | no bond or flange crack; insert still slides | shoe on a two-layer board offcut |

On fail: C4/C6/C3/D5 re-size the part named; the flight article is not proof-loaded again until re-built.

## GT-10 Pack retention and foot drops

| Test | Pass | Source |
|---|---|---|
| `T-H1-PACK-PULL`: 680 g **dummy** strapped as flown; 85 N in ±x, ±y, +z | holds 10 s, slip ≤ 5 mm, hatch closed | `CL-H1-PACK-PULL-F` → `R-PACK-RETENTION` |
| `T-C5-FOOT-RIG`: one foot under a 0.65 kg sled (0.68 / 0.62 kg for U / L), 0.115 m, 3 drops | stroke ≤ 29 mm, peak ≤ 6.0 g, no shoe crack | C5 |
| `T-C5-AIRCRAFT-DROP` (= `T-C1-FOOT-DROP`): sandbag pack, 2.6 kg, FC IMU ≥ 1 kHz; level 0.115 m ×2, then pitch 4°, roll 8° at 0.093 m | CG ≤ 6.0 g, strokes ≤ 35 mm and within 3 mm of the model | `R-LANDING-IMPACT` |
| `T-D5-REPLACE`: one student, field kit, crushed insert swapped | ≤ 10 min | `CL-D5-REPLACE-TIME` |

Never a LiPo in a pull or drop.

## GT-11 Tilt board

`T-C5-TILT-BOARD`. Figure `FIG H1-06`, `ANIM H1-A1`. 0.6 × 0.8 m board faced with landing-mat rubber, 6 mm stop
strip behind the pads on the hinge side; pack in, then at the forward stop, then out; four directions × 3.

| Pass | Limit | Source |
|---|---|---|
| Pod-side tip angle | ≥ 30° and within 1.5° of `CL-C5-TIPOVER-R1` | `P:requirements.tipover_min_deg` → `R-TIPOVER` |

## GT-12 Bench electrics and controls, props off

| Step | Pass | Source |
|---|---|---|
| `T-F3-FW-LOAD`: stable Plane 4.7.x, Q_ENABLE, Q_TAILSIT_ENABLE, SERVO_BLH_BDMASK 15; SD log | parameters present, rpm telemetry on all 4 | F3 |
| `T-F3-I2C-SCAN`: boot with GPS and airspeed on | SPL06, QMC5883, MS4525 listed; pitot blow raises airspeed, baro does not jump | `CL-F3-I2C-CLASH` |
| `T-F3-5V`: 16.8 V bench supply through a meter, all avionics on | 5 V rail current ≤ F3's line | `CL-F3-5V-REQ` |
| `T-F5-BENCH`: ELRS 3.x, FCC, model match, channel map | every channel correct | F5 |
| `T-F5-FS-BENCH`: TX off in QSTABILIZE, FBWA, CRUISE (tied down) | QLAND in Q modes, RTL in FW; FS message ≤ 2.5 s | `CL-F5-FS-TIME` |
| Motor test order UR UL LR LL, rotation | all four correct | `R-FSW-PARAMS` |
| Motor cant, angle gauge on each mount | **7.0 ± 0.5°**, sense per station | `P:propulsion.stations.cant_deg` |
| Elevon throws / directions in FBWA and QHOVER | ±25° ± 2°; correct sense (`ANIM H1-A2`) | `P:wing.elevon.deflection_deg` |
| `T-B2-HINGE`: 0.257 N·m at the panel mid-chord, ±25° | holds, no slip | `CL-B2-HINGE-MOMENT` |
| `T-F1-SERVO-STALL` | servo rail ≥ 5.8 V, FC 5 V ≥ 4.8 V | F1 |
| `T-F1-SENSOR-CAL` (on GT-13's frame) | BAT.Curr within 5 % at 5/15/25/30 A | F1 |
| `T-F1-PRECHARGE`: Jacobs scope on the bus, 20 plug cycles | bus ≥ 95 % before main pins | F1 |
| `T-H1-ARM-KILL`: arm refused per failed check; kill at 50 % throttle, 5 trials | switch to zero output ≤ **0.9 s** in the log | `CL-H1-ESTOP-ACCEPT` |

## GT-13 Restrained four-motor run

Figure `FIG H1-07`. Aircraft on its feet on an 18 mm plywood table, strapped at the four root eyes (D3, CR-H1-08).

| Step | Pass | Source |
|---|---|---|
| `T-H1-RESTRAINT-PULL`: each strap to 29.5 N (total 117.8 N) | no slip at the anchor | `CL-H1-RESTRAINT-PER-TIE` |
| `T-H1-RESTRAINED-RUN`: full throttle 2 s, QSTABILIZE, fresh pack | BAT.Curr ≤ 100 A; per-motor ≤ 25 A; output ≤ 0.84 | `CL-F4-BAT-CURR-MAX`, `CL-E1-ILIM-I`, `CL-F4-SPIN-MAX` |
| `T-F1-RIPPLE`: scope at each ESC's pads during the punch | ≤ 1.0 V p-p, no spike > 21 V | F1 |
| `T-F3-COMPASSMOT` to hover throttle | interference ≤ 30 % | `CL-F3-COMPASS-RATIO` |
| GPS mast to nearest power lead | ≥ 0.10 m | `P:requirements.gps_mast_clearance_m` |

## GT-14 RC range check (`T-F5-RANGE`)

CR-F5-05 replaces the old 10 mW card (the Pocket's lowest setting is 25 mW).

1. TX 25 mW, 150 Hz; aircraft 1 m up on a stand; motors spinning props-off at 20 %.
2. Walk to **≥ 105 m** line of sight (100 m + phone-GPS U95). Read 1RSS, 2RSS, RQly for 4 headings in hover
   attitude and 4 in cruise attitude.

| Pass | Limit | Claim |
|---|---|---|
| Distance | ≥ 105 m | `CL-H1-RANGE-WALK` |
| LQ, every position | ≥ 0.9 | `P:requirements.rc_lq_min` |
| Better of 1RSS/2RSS, every position | ≥ **−93.8 dBm** (predicted −82.2) | `P:requirements.rc_rssi_check_min_dbm`, `CL-F5-RC-RSSI-REQ` |
| No failsafe | none | `R-RC-LINK` |

## GT-15 Coupons

Lever frame: 6:1 (coupon 0.10 m, jugs 0.60 m), water jugs ≤ 20 kg, capacity 1 177 N vs 1 135 N needed
(`CL-H1-LEVER-CAP`, `-NEED`; `T-H1-LEVER-CAL`: 2.000 kg balances 0.333 kg within 2 %). Fill the jug slowly from a
hose; weigh it after failure. Compression coupons on the 20 kgf cell under the Jacobs drill press. Record every
failure load and mode; allowable = owner's rule (mean − 2 s, or 0.5 × mean).

| Test (owner) | Specimens | Rig | Pass | Window |
|---|---|---|---|---|
| `T-C2-XPS-COUPON` (C2) | 100 mm cube; 300 × 40 × 30 mm strips bare and taped | scale; 3-point bend on jugs | E and strength recorded | foam arrives (Dec) |
| `T-C3-BOND-COUPON` (C3) | 3 PETG pads on F-250, 3 on board (flat-wise); 3 lap shears | lever | foam or paper failure | Dec |
| `T-C3-STOP-PUSH` (C3) | 60 mm tray offcut, 3.0 mm stop, 1.5 mm guides | lever, 50 mm block at 12 mm | 90 N stop, 85 N guide; set < 0.5 mm | first tray print |
| `T-C4-BOARD-COUPON` (C4) | 3 × 50 × 300 mm per layer count | 4-point bend, span 250 mm | allowable and D recorded | Dec |
| `T-C6-LAP-PETG` (C6) | 5 PETG-CF + 5 ASA-CF lap shears | lever | ≥ 2.0 MPa | ASA spool (Dec) |
| `T-C6-BOARD-LAP` (C6) | 5 shear + 5 flat-wise tabs | lever | modes recorded | Dec |
| `T-C6-XPS-PULL` (C6) | 10 pucks Ø30 mm | lever | allowables recorded | Dec |
| `T-C6-BOARD-CORNER` (C6) | 2 U-sections | jugs | ≥ 43 N | Dec |
| `T-C6-INSERT` (C6) | 3 inserts | lever | ≥ 300 N each | first POD-002 print |
| `T-C6-STRIP-ANCHOR` (C6) | collar tail + strip pair | lever | ≥ 908 N (C6's calc; text says 700 N, CR-H1-12) | first collar |
| `T-C6-HEAD-CREEP` (C6) | ASA plate, 4 × M3 at 0.20 N·m | 70 °C, 2 h: sealed bag in a water bath with a probe (no oven needed) | breakaway ≥ 0.15 N·m | first mount |
| `T-D5-COUPON` (D5) | 3 type-U + 3 type-L cartridge pairs | drill press over the 20 kgf cell (need 5.1 kgf, `CL-H1-D5-CELL-REQ`), 40 mm at < 10 mm/s, every 2 mm | U 34.5–38.5 N, L 29.5–33.0 N, U/L 1.15–1.19 (U95 0.006, `CL-H1-D5-RATIO-U`), peak ≤ 1.15 × plateau, flat to 40 mm | first cartridges |
| `T-D5-PAD-MU` (D5) | foot with pad, 0.65 kg | tilt board faced with paver / shingle / mat; 5 runs each | slip angle ≥ **35.3°** (μ 0.70 + U95) | first pads |

Torque checks (0.20 N·m) without a torque driver: 2.0 N on a spring scale at 0.10 m on the hex key.

## GT-16 Tube bend and torsion (Aloft `W03`) — result to I1 by 10 Dec

`T-C4-TUBE-BEND` (= `T-J1-TUBE-BEND`), `T-C4-TUBE-TORSION`, CR-C4-21, CR-I1-08. Run on arrival (~27 Nov); weigh first.

1. Span 0.80 m on two 22 mm dowels; printed saddle at mid-span; 0.5 kg steps to 4.0 kg and back.
2. Deflection: dial indicator (borrowed) or caliper depth rod against a fixed bar (U95 0.03 mm).
3. E = F L³ / (48 I δ) from the slope of 8 steps, I = 3.645 × 10⁻⁹ m⁴ (`CALC-H1-BEND`).
4. Torsion: 0.40 m clamped in printed V-blocks, 0.30 m lever, 0.5–2 kg, laser spot on a wall 3 m away;
   G = T L / (J θ), J = 7.29 × 10⁻⁹ m⁴.

| Pass | Limit | Claim |
|---|---|---|
| Deflection at 4.0 kg (E ≥ 70 GPa) | ≤ **1.61 mm** (1.64 mm at 70 GPa − U95) | `CL-H1-TUBE-DEFL-ACCEPT` |
| Peak stress | 23.7 MPa (tube stays usable as the spare) | `CL-H1-TUBE-SIGMA` |
| E read uncertainty | 1.8 % | `CL-H1-TUBE-E-U` |
| G | report vs 3–10 GPa | `ASM-C4-G-TUBE-LO`, `-HI` |

Pass → I1 orders `W04` from Aloft. Fail or no result by 10 Dec → overseas tube, order by 15 Dec (I1). C4 replaces
its E/G assumptions with the measured values either way.

## GT-17 Mount rocking stiffness

`T-C4-MOUNT-STIFF`, with `T-C6-CANT-SEAT` and `T-C6-PROPNUT` on the same first ASA mount. Figure `FIG H1-08`.

C4's readout (two 0.01 mm dial gauges at 0.5 kg) sees 8.7 µm at the pass stiffness, under one division
(`CL-H1-MSTIFF-DIAL-UM`), so GT-17 uses an optical lever (CR-H1-10).

1. Motor clamped in the mount on a 60 mm tube stub in a vice. Mirror on the can side, second mirror on the collar;
   laser spots on mm paper 3.0 m away.
2. 0.5, 1.0, 1.5 kg over a cord at the prop nut, in y and then in z (1.5 kg = 70 % of the mount proof load,
   `CL-H1-MSTIFF-LOAD-FRAC`). Measure the arm a (nut to collar) with calipers; sizing used a = 0.053 m.
3. θ = (spot_can − spot_collar) / (2 L); k = F a / θ from the slope.

| Pass | Limit | Claim |
|---|---|---|
| Net spot travel at 1.5 kg, y and z | ≤ **4.69 mm** (5.19 mm at k_req 905 N·m/rad − 0.5 mm read); 1.57 mm expected at 3 000 | `CL-H1-MSTIFF-SPOT-ACCEPT` → `CL-C4-D3-MOUNT-K-REQ` |
| k uncertainty at the pass line | 9.6 % | `CL-H1-MSTIFF-U` |
| `T-C6-CANT-SEAT` | ≥ 6 turns from first bite; 0.05 mm feeler does not enter | C6 |
| `T-C6-PROPNUT`: 1.5 N·m on/off × 10 | witness line and lip cap unmoved | C6 |

## GT-18 Tap tests

`T-C4-TAP-D3`, `T-C2-TAP-TEST`, `T-C4-PROP-SWING`. Acquisition: FC raw IMU ≥ 1 000 Hz (need 935 Hz,
`CL-H1-TAP-FS-REQ`). A ~400 Hz phone app reads only to 160 Hz (`CL-H1-TAP-PHONE-MAX`): use it for C2's 12–22 Hz wing
modes only (CR-H1-11). 4 s records (0.25 Hz bins), 5 taps per direction, averaged.

Windows (± `P:requirements.vibration_sep_frac` 0.2, `CALC-H1-TAP`):

| Order | Hover 5 416 rpm | Cruise 5 894 rpm | Cap 9 350 rpm |
|---|---|---|---|
| 1P | 90.3 Hz (72.2–108.3) | 98.2 Hz (78.6–117.9) | 155.8 Hz (124.7–187.0) |
| 2P | 180.5 Hz (144.4–216.6) | 196.5 Hz (157.2–235.8) | 311.7 Hz (249.3–374.0) |

1. `T-C4-TAP-D3`: finished wing on foam blocks, props on; tap each bell in y and z; FFT to 450 Hz.
2. `T-C2-TAP-TEST`: aircraft on bungees (free-free); phone at the pod and a fin tip for the wing modes, FC IMU for
   the rest; tap a can fore-aft and a fin tip sideways.
3. `T-C4-PROP-SWING`: bifilar, two 0.5 m threads at the blade tips, 20 swings.

| Pass | Limit | Claim |
|---|---|---|
| Fin-station f1, each quarter | outside 1P hover, 2P hover and 2P cruise windows (record of `R-VIBRATION` a); predicted 273–281 Hz | `CL-C4-D3-SEP`, `-F1-UP`, `-F1-LO` |
| Cap windows (1P/2P at 9 350 rpm) | advisory; a mode inside → F4 harmonic notch | `CL-C4-D3-SEP-BAND` |
| Wing modes (12–15 Hz antisym., ~22 Hz sym.) | model within 15 %; damped or inside the rpm notch | `CL-C2-F-TORSION-ANTI`, `-SYM` → `R-VIBRATION` (b) |

## Figures and animations

Rendered by `redesign/blender/` from the CAD, per `design-system/BLENDER-STYLE.md`: act parts orange, built parts
real material, context ghosted; callout numbers = card step numbers. Loops 3–10 s, ≤ 1080p, < 3 MB MP4 H.264 with a
poster PNG; autoplay-muted-loop with controls.

| Id | Kind | Shows | Act (orange) | Camera | Callouts |
|---|---|---|---|---|---|
| `FIG H1-01` | still | thrust stand with thrust and torque paths | axle, both cells, torque arm | iso 35°, 50 mm | 1 thrust cell, 2 arm 100 mm, 3 FC, 4 watt meter, 5 kill |
| `FIG H1-02` | still | R3 installed mock-up on the carriage | tube, collars, brace, ESC dummy, half-fin, strip | side, ortho | tube end 0.172 m, 7° mount, 0.21 m half-fin |
| `FIG H1-03` | still | CG jig, two scales | pin bridges, scales | front-iso 30° | x 0.010 / 0.230, \|y\| 0.45, ≥ 0.25 m |
| `FIG H1-04` | still | inverted wing on the pod support, 4-pad whiffletree | pads, bars, sandbags | front, low | y 0.12 / 0.26 / 0.355 / 0.465, masses |
| `FIG H1-05` | still | station and fin proof hangs | jugs, cords | iso | 20.9 N, 40.7 N |
| `FIG H1-06` | still | tilt board at 30° | board, stop strip | along the hinge | angle arc, catch zone |
| `FIG H1-07` | still | restrained table | straps, root eyes | iso 45°, high | 29.5 N each, keep-out ±30° |
| `FIG H1-08` | still | mount-stiffness optical lever | mirrors, cord, weight | plan view | L 3.0 m, a, spot pair |
| `FIG H1-09` | still | coupon lever frame 6:1 | lever, jug, coupon | side, ortho | 0.10 / 0.60 m, pivot |
| `ANIM H1-A1` | 6 s loop | board 0 → 32°, pads lift at 30° | board, lifting feet | as `FIG H1-06` | live angle |
| `ANIM H1-A2` | 8 s loop | pitch then roll stick in FBWA, then QHOVER; elevons move | elevon panels | rear-iso 30° | mode, stick icon |
| `ANIM H1-A3` | 8 s loop | mock-up parts removed one by one | the part being removed | as `FIG H1-02` | config name |

## Test gear: bought and borrowed (CR-A1-39, D-39)

Bought new for ground test: I1 line `G12` only, $17.00 pre-tax (1 kgf bar cell + HX711, 5 K-type probes), checked
by `CL-I1-GROUNDTEST-BOUGHT` ≤ $20. Already in the baseline BOM: `G04` watt meter, `G05` IR thermometer, `G06` 20 kgf
cell + HX711 + Nano, `B04` 11×4.5MR props. Everything else is borrowed:

| Item | Card | Lender | Status | Fallback (cost) |
|---|---|---|---|---|
| Bench power supply (Rm at 2 A; I0 at 10 V; `T-F3-5V`) | GT-02a, GT-12 | Jacobs Electronics Lab, studio 110 (in-lab use) | `CHECKED` listed (`SRC-H1-JACOBS-EQUIP`) | flight pack + meter ($0) |
| Multimeters ×2 (4-wire Rm, rails) | GT-02a, GT-12 | Jacobs Electronics Lab | `CHECKED` listed | team `G09` |
| Oscilloscope (`T-F1-PRECHARGE`, `-RIPPLE`) | GT-12, GT-13 | Jacobs Electronics Lab | `CHECKED` listed | run in the lab |
| Saleae logic analyzer (I²C / DShot debug) | GT-12 | Jacobs Electronics Lab | `CHECKED` listed | — |
| Drill press (D5 crush) | GT-15 | Jacobs woodshop (Delta variable speed) or metal shop (Clausing) | `CHECKED` listed | hand screw press on the bench ($0) |
| K-type reader | GT-04 | a Jacobs DMM with a K input | `UNVERIFIED` (ask) | I1 gated `X09` $15 |
| Dial indicator + magnetic base | GT-16 | Jacobs metal shop hand tools | `UNVERIFIED` (ask) | digital calipers (team or Jacobs) |
| Digital calipers, 0.1 g scale | GT-02a, GT-16 | team members / Jacobs | `UNVERIFIED` (ask) | — |
| Two 5 kg × 1 g scales | GT-06, GT-07 | team members' kitchen scales | `UNVERIFIED` (ask) | one scale + knife edge ($0) |
| Plywood, 2×4 lever, 608 bearings, M8 rod | GT-01, GT-15 | Jacobs scrap bin, team spares | `UNVERIFIED` (ask) | `H01` hardware share |
| Spring/luggage scale 0–50 kg | GT-09, GT-10, GT-13 | team | `UNVERIFIED` | lever frame + jugs ($0) |
| Laser pointer, small mirrors | GT-16, GT-17 | team | `UNVERIFIED` | $3 left under the $20 line |
| Fridge (cold pack, bagged), water jugs, sand, bungees, phone apps | GT-02e, GT-15, GT-18 | team | — | — |

Ask Jacobs staff (jacobsinstitute@berkeley.edu, 510-664-7564) by 18 Nov, before the stand build week; record the
answers in this table.
