# Ground test plan — K09-L

Owner H1 (ground test engineer). Status `PROPOSED`, revision **H1-R3**, 2026-11-10. Inputs re-read on this date:
`params/params.json` (A1-R5), `README.md`, `MASS-CG.md` (A1-R5 over A3-R6a), and the claim files of A1, A3, B3, C1
(R4, 14:37 publish), C2, C3 (R3), C4 (`claims.d3.json`, `claims.sim.json`), C6 (R5b), D5, E3 (`sim/claims.json`), I1.
Every pass line below is a claim in `team/H1/claims.json` (from `ground_tests.py`) or an owner's claim. Re-run
`python -I redesign/team/H1/ground_tests.py` after any parameter change. The tests (`T-…` ids) belong to the role that
owns the claim they verify. H1 builds the rigs, runs the cards and writes the logs, and the owner marks the test `run`
with the H1 log as evidence.

**R3 changes.** GT-09 fin proof on the as-drawn article with two strain-gauge bridges and a 25 mm dial (CR-C4-36,
CR-C4-38). GT-17 pass level ≥ max(1 100, `CL-C4-D3-MOUNT-K-REQ`), 1 966 N·m/rad at C4's 15:01 re-publish, with the wall moved to 5.0 m (CR-C4-41). GT-15 lever rebuilt 15:1 / 9:1 with steel
pivot plates, ≥ 2 942 N (CR-C6-33, CR-C6-39). `T-C3-STOP-PUSH` on bonded tray pieces, and `T-C3-POD-PROOF` + 200 N on the
foot brackets (CR-C3-20). GT-16 adds GJ between two lasers and a ring-crush coupon for the hoop modulus (CR-C2-15).
GT-04 step 2b, `T-E3-ESC-PAD-CFD`, on a heated dummy, held 10.3 min (CR-E3-17). GT-08 uses C1's R4 pad table, relief
pull and step 2 (CR-C1-30, CR-C1-27). GT-07 balance marks at 0.0466 / 0.0514 m. `T-D5-SIDE` at 59.0 N ultimate. Test
gear: bought `G12` $17.00 and `G13` $9.00 (gauges); the rest is borrowed. **Jacobs Hall's written yes for the
soldering kit and hot-wire gear is due before 20 Nov (D-72).** The request is ready to send:
`team/H1/JACOBS-LOAN-REQUEST.md`.

## Campaign order

| Card | What | Tests run (owner) | Window |
|---|---|---|---|
| GT-01 | Stand build and calibration | `T-H1-STAND-CAL`, `T-H1-RIG-CHECK` (H1) | 23–25 Nov |
| GT-02 | Stand campaign, one station | `T-E1-MOTOR-RM` `T-E1-STAND` (E1), `T-B4-STAND` (B4), `T-C1-THRUST-FRESH` (C1), `T-A1-THRUST-STATION` (A1), `T-E2-IR` (E2) | 25 Nov – 5 Dec |
| GT-03 | Installed run, fin swirl | `T-B4-INSTALLED` `T-B4-YAW` (B4) | 1 – 8 Dec |
| GT-04 | Motor, ESC, wire and connector thermal | `T-E3-MOTOR-TAU` `T-E3-ESC-PAD` `T-E3-ESC-PAD-CFD` (E3), `T-F1-WIRE-HEAT` `T-F1-CONN-HEAT` (F1) | with GT-02, ≤ 8 Dec |
| GT-05 | Packs: weigh, capacity, IR | `T-E2-WEIGH` `T-E2-CAPACITY` `T-E2-IR` (E2) | on arrival |
| GT-16 | Tube bend, torsion (GJ) and ring crush (Aloft `W03`) | `T-C4-TUBE-BEND` (= `T-J1-TUBE-BEND`), `T-C4-TUBE-TORSION` (C4); E_hoop to C2 | tube arrives ~27 Nov; **result to I1 by 10 Dec** |
| GT-17 | Mount rocking stiffness | `T-C4-MOUNT-STIFF` (C4), `T-C6-CANT-SEAT` `T-C6-PROPNUT` (C6) | first printed ASA mount (Dec) |
| GT-15 | Coupons | C2, C3, C4, C6, D5 coupon tests (table in GT-15) | first prints and foam, Dec – 16 Jan |
| GT-06 | Weigh parts and aircraft | `T-A3-WEIGH-PARTS` (A3), `T-A1-WEIGH` (A1) | as parts arrive; build end |
| GT-07 | CG balance | `T-B3-CG-BALANCE` (B3), `T-A3-CG-BALANCE` (A3), `T-A5-CG-BALANCE` (A5) | build end |
| GT-08 | Wing proof (steps 1 and 2) and twist | `T-C1-WING-PROOF` (C1), `T-C2-TWIST` (C2); `T-C2-WING-PROOF` withdrawn (CR-C1-27) | first finished wing |
| GT-09 | Station, fin, block, pod and foot proofs | `T-C1-STATION-PROOF` (C1), `T-C4-FIN-PROOF` `T-C4-BLOCK-PROOF` (C4), `T-C3-POD-PROOF` (C3), `T-D5-PROOF` `T-D5-SIDE` (D5) | fin test article (Dec), first pod |
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
6. `T-H1-RIG-CHECK`: optical-lever shim step (and both torsion lasers), caliper or dial on a 1.00 mm gauge block, 200 Hz
   tone on the FC raw IMU, phone inclinometer on a 30° printed wedge, each strain-gauge bridge (60 s zero, 10 min drift
   ≤ 5 µε, shunt step 1 744 µε within 1 %), three thermocouples together in still air within 0.3 K.

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
| Full-throttle thrust, cold 20 % pack | ≥ **1.115 kgf** (predicted 1.379 at sag 0.851) | `CL-H1-T-SAG-ACCEPT` (1.102 + U95) → `CL-H1-T-PASS-SAG`, `R-HOVER-TW` |
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
borrowed DMM with a K input (else I1 gated `X09`, $16.54); `G05` IR thermometer on matte-tape spots. Readings every 5 s
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

**2b `T-E3-ESC-PAD-CFD` (E3, CR-E3-17): film coefficient on a heated dummy.** Figure `FIG H1-11`. Same half-fin
mock-up, 22 mm tube and ASA pad behind the stand prop; the ESC replaced by a 45 × 20 × 6 mm aluminium dummy
(`ASM-H1-ESC-DUMMY`): a 10 Ω 5 W resistor in a slot, run at 3.0 W (V and I on two DMMs), painted matte black (ε 0.90),
on 3 mm XPS in place of the hook-and-loop (same height above the pad), held by the flight strap. Thermocouples:
TC1 in the block, TC2 on the pad under the XPS, TC3 in the inflow 30 mm ahead of the pad.

1. Stand at **hover thrust** (`CL-B4-HOVER-T`, 690 gf), not a throttle %, so the slipstream matches the CFD inflow
   (10.9 m/s, `CL-E3-CFD-U`).
2. Hold **≥ 620 s** (5 τ, `CL-H1-ESCCFD-RUN`; E3's ≈ 5 min is about 2 τ). Log TC1–TC3, V, I every 5 s; fit
   T = T∞ − (T∞ − T₀) e^(−t/τ) on the last 300 s.
3. h = (P − G·(T1 − T2) − A·h_r·(T1 − T3)) / (A·(T1 − T3)), with A = 1 360 mm², G = k_XPS·L·w / t, h_r = 4εσT³;
   f_meas = (h / h_lam)², h_lam = 60.7 W/m²·K (laminar flat plate at 10.9 m/s over 45 mm). The XPS path carries
   about 9 % of the 3 W; TC2 measures it, so the ±10 % on k_XPS costs only 0.9 % on h.

| Pass | Limit | Claim |
|---|---|---|
| f_meas, design hover | ≥ **1.205** (1.131 + U95 3.2 % on h); h ≥ 64.6 W/m²·K before the guard band | `CL-H1-ESCCFD-F-ACCEPT` → `CL-E3-CFD-FEQ` |
| Dummy rise at 3.0 W | 28.2 K at the pass line; 22.7 K expected at the SST film | `CL-H1-ESCCFD-DT-PASS`, `-DT-EXP` |
| Steady before reading | dT/dt < 0.1 K/min | `CL-H1-ESCCFD-RUN` |

On fail: E3 re-runs the heat balance with the measured R_th and wake factor; the field-ambient ceiling moves.

## GT-05 Packs: weigh, capacity, IR

Tests `T-E2-WEIGH`, `T-E2-CAPACITY`, `T-E2-IR`. One row per pack in `team/E2/pack_log.csv`.

1. Arrival: cell voltages, mass incl. leads (1 g), L × W × H incl. lead exit.
2. Charge 1C, rest 1 h; IR by a 20 A step on the stand at 25 °C.
3. Capacity: discharge through the stand at ~6.5 A to 3.5 V/cell under load, `G04` watt meter mAh.

| Pass | Limit | Source |
|---|---|---|
| Mass incl. leads | ≤ `CL-E2-PACK-ACCEPT-KG` (0.593 kg today; 551 g expected) | `CL-E2-PACK-MASS`; A3 re-runs |
| Fits the pod bay | ≤ 160 × 52 × 53 mm | `README.md` |
| Capacity at 1C | ≥ 5.98 Ah | `CL-H1-PACK-CAP-MIN` |
| IR at 25 °C / spread on arrival | ≤ 5 mΩ/cell / ≤ 0.02 V | `T-E2-IR`, H3 |

## GT-06 Mass

Tests `T-A3-WEIGH-PARTS`, `T-A1-WEIGH`. Scale calibration `T-H1-SCALE-CAL` (2.000 kg check mass, 10 readings).

| Pass | Limit | Claim |
|---|---|---|
| Scale U95 | ≤ 5.2 g; ≤ 10 % of A3's 139 g margin | `CL-H1-WEIGH-U95`, `-U-FRAC` (3.8 %) |
| Ready-to-fly mass (mean of 3) | ≤ 2.595 kg | `CL-H1-WEIGH-ACCEPT` → `R-MASS-GATE` |
| Each subsystem | ≤ its allocation | `R-MASS-ALLOC` (A3) |

## GT-07 CG balance

Tests `T-B3-CG-BALANCE`, `T-A3-CG-BALANCE`, `T-A5-CG-BALANCE`. Figure `FIG H1-03`. Pins under the wing at
|y| 0.45 m (patch kept free, CR-H1-08), front x = 0.010 m, rear x = 0.230 m; wing ≥ 0.25 m up.
x = 0.010 + 0.220 · W2 / (W1 + W2). With one scale only: front pins on a fixed knife edge, W from GT-06.

**Balance marks (B3's `T-B3-CG-BALANCE`).** Draw two lines across both fin roots, square to the chord, with a steel
rule from the leading edge at **x = 0.0466 m** (forward limit) and **x = 0.0514 m** (aft limit) (`P:cg.x_range_m`,
D-62, B3 V1). They are the never-fly-outside lines for the field fingertip check. The jig reading is the acceptance:
it must sit inside the guard-banded window below, which is 0.6 mm inside each mark. Pack station from A3's live
`CALC-A3-CG` on the day (CR-A3-27). Predicted 0.0490 (target) / 0.0503 with the 551 g pack.

| Pass | Limit | Claim |
|---|---|---|
| Jig U95 in x | ≤ 0.6 mm (25 % of the half-range) | `CL-H1-CG-U95`, `-U-FRAC` |
| x, guard-banded (jig) | **0.0472 ≤ x ≤ 0.0508 m** | `CL-H1-CG-ACCEPT-FWD`, `-AFT` → `R-CG-RANGE` (`P:cg.x_range_m` 0.0466–0.0514) |
| Fingertip balance at the marks (field) | between the 0.0466 and 0.0514 lines | `T-B3-CG-BALANCE` |
| y / z | ≤ 0.005 m / 0.010 … 0.025 m | `P:requirements.cg_lateral_max_m`, `P:cg.z_range_m` |

On fail: slide the pack (2 mm spacer steps, 12 mm aft travel); outside the slide range → A3/A1. Aft of the aft
line with a light pack: lead tape behind the nose (about 13 g per mm, `MASS-CG.md`).

## GT-08 Wing proof and twist

Figure `FIG H1-04`. `T-C1-WING-PROOF`, the one wing limit proof (CR-C1-27, CR-C1-30), on C1's R4 tree
(`team/C1/data/whiffletree.json`, case F1-PULLUP-VD/MC-C; step 2 F7-ROLLPULL-VA/MC-C). Every mass below is read live
from C1's claims; the pads already subtract the aircraft's own weight when inverted.

1. Aircraft inverted, supported under the pod (|y| ≤ 0.07 m), half-fins hanging free. Dial or ruler stand at each tip.
2. **Step 1, both sides together.** Four 40 × 40 mm pads per side over the spar line (x 0.08 m). Option A (used):
   one sandbag stack per pad, made of four bags each weighed to ±5 g, so each 25 % step is one bag per pad. Option B:
   C1's tree (bars A, B, C and the top bar) with a sand bucket at the hanger; the tree's own mass counts in the load.
   Relief: a sling on each motor tube at the wing plane, over a ball-bearing pulley, to a counterweight; check the
   sling tension with the spring scale within 3 % before the first step.

| Item (per side) | y | Limit load | Mass | Claim |
|---|---|---|---|---|
| Pad 1 | 0.120 m | 9.01 N | **0.919 kg** | `CL-H1-WP-M1` ← `CL-C1-PROOF-P1-LIM` |
| Pad 2 | 0.250 m | 5.14 N | **0.524 kg** | `CL-H1-WP-M2` ← `-P2-LIM` |
| Pad 3 | 0.355 m | 4.44 N | **0.453 kg** | `CL-H1-WP-M3` ← `-P3-LIM` |
| Pad 4 | 0.465 m | 6.01 N | **0.613 kg** | `CL-H1-WP-M4` ← `-P4-LIM` (now a C1 claim) |
| Sum, centroid | 0.274 m | 24.60 N (C1's total, error 0.0 %) | 2.508 kg | `CL-H1-WING-PROOF-P`, `-Y`, `CL-H1-WP-SUM-ERR` |
| Relief, upward at each tube | 0.320 m | 19.92 N | **2.031 kg** | `CL-H1-WP-RELIEF-M` ← `CL-C1-PROOF-R-LIM` |
| Hanger (option B, both sides) | 0 | 49.2 N | — | `CL-H1-WP-HANGER` |

3. Steps 25 / 50 / 75 / 100 %, relief applied in proportion before each pad step. Hold 3 s at 100 %; tip deflection at
   each step; unload; read again after 5 min.
4. **Step 2, outboard, one side at a time** (CR-C1-27; C2's set-up, C1's loads). Padded V-block under the spar at
   y 0.320 m (`CL-C1-PROOF-OUT-SUPPORT-Y`), pod support removed from that side's load path; pads 3 and 4 only:

| Item | y | Limit load | Mass | Claim |
|---|---|---|---|---|
| Pad 3 | 0.355 m | 4.90 N | **0.499 kg** | `CL-H1-WP-S2-M3` ← `CL-C1-PROOF-OUT-P3-LIM` |
| Pad 4 | 0.465 m | 16.10 N | **1.642 kg** | `CL-H1-WP-S2-M4` ← `CL-C1-PROOF-OUT-P4-LIM` |

5. `T-C2-TWIST`: pod clamped, 0.3 m lever on the right block, 1 kg (2.9 N·m), inclinometer at the block and tip.
   `T-C2-WING-PROOF` is withdrawn (CR-C1-27); its 51 N tube-end hang is `T-C1-STATION-PROOF` (GT-09).

| Pass | Limit | Claim |
|---|---|---|
| No crack, wrinkle, bond-line or core crush, steps 1 and 2 | visual + tap | `R-STRUCT-MARGIN` |
| Tip deflection at 100 %, step 1 | ≤ 28.8 mm | `CL-H1-WING-DEFL-MAX` |
| Permanent set after 5 min | ≤ 0.5 mm | C2 |
| Torsional stiffness | GJ ≥ 25 N·m² | `T-C2-TWIST` |

C1's claims (14:37 publish) supersede the numbers in CR-C1-30's text (pad 2 7.66 → 5.14 N, relief 19.40 → 19.92 N,
step 2 4.85 / 15.85 → 4.90 / 16.10 N); the card reads the claims (CR-H1-20). Ultimate (1.5 ×) only on a
sacrificial core.

## GT-09 Station, fin, block, pod and foot proofs

Figure `FIG H1-05` (hangs), `FIG H1-10` (fin test article). Loads hung by weighed water jugs over ball-bearing
pulleys or through the GT-15 lever frame. Every load in 25 % steps, inspected between steps.

| Test | Load | Pass | Article |
|---|---|---|---|
| `T-C1-STATION-PROOF` | 21.1 N (2.15 kg) at each mount in −x and y; 57.3 N (5.84 kg) at the station in y; G2 step: 42.2 N (4.30 kg) at the UR upper tube end, wing held under the pod (CR-C1-27) | no slip, crack or set | flight fins, limit (`CL-H1-MOUNT-PROOF-F`, `-FIN-PROOF-F`) |
| `T-C4-FIN-PROOF` | card below: 1.0 × then 1.5 × L4, G2, G3 | card below | **test-article lower quarter, D5 shoe as drawn** |
| `T-C4-BLOCK-PROOF` | 18 kg at 0.17 m (30 N·m) for 1 min | no creak, no bond-line crack | block on a spar stub in a 0.15 m core offcut |
| `T-C3-POD-PROOF` (a) | pack-size dummy strapped in; down 64 N, up / aft / side 85 N, 10 s each (C3's 1.5 × design) | no crease at bond edges, nose, wall tops | built pod on the wing |
| `T-C3-POD-PROOF` (b), CR-C3-20 | **199.6 N (20.35 kg)** on each handle-foot bracket, along +x (aft), then along −z; strap round the bracket, jugs over a pulley; 10 s | no crease at the recess-step corner, no bracket peel, set < 0.5 mm | same pod, brackets bonded 24 h (`CL-H1-POD-BRACKET-F` ← `CL-C3-FEA-SADDLE-TIES`) |
| `T-D5-PROOF` | 88 N along x at the pad edge, 3 s | no bond or flange crack | shoe on a two-layer board offcut |
| `T-D5-SIDE` | **59.0 N (6.01 kg)** at the pad along y, then z, insert 4 mm in, 3 s (`CL-H1-D5-SIDE-F` ← `CL-C1-FOOT-SIDE-DESIGN-ULT`, ultimate) | no crack at the rim or tine; insert still slides | same specimen, the CR-A1-65 shoe (wall 2.0, rim 3.0, 1.0 mm fillet) |

`T-D5-SIDE` was 35 N (D5's old 22.8 N × 1.5 basis). At 59.0 N D5's drawn rim scales to SF 0.62
(`CL-H1-D5-SIDE-RIM-SF`), so the test is run on the CR-A1-65 shoe only; D5 re-runs `CL-D5-SIDE-*` at 59.0 N first
(CR-H1-22). `T-C3-POD-PROOF` (b) is C3's crash force on a flight pod: stop at the first audible crack, and the pod is
re-built if anything creases (CR-H1-23).

### `T-C4-FIN-PROOF`: as-drawn test article, two gauge bridges and a dial (CR-C4-36, CR-C4-38)

Article (C4's procedure, D5 shoe **as drawn**: legs 7 mm, 8 mm collar cheeks bonded over both strip ends, not the
extended cheeks of CR-C4-30). One lower quarter built with flight processes and never flown; LE fillet left unbonded.
The result decides CR-C4-30: pass keeps the drawn shoe (≈ 16 g saved); fail fits the extended cheeks to |z| 0.171 m.

| Instrument | Where | Read-out | Claim |
|---|---|---|---|
| Gauge F (face) | paper face, 5 mm below the shoe leg edge, x ≈ 0.30 m, grid along the fin span | half bridge with a dummy gauge on an unloaded two-layer offcut beside the article; HX711 (`G06` board), 1.5 kΩ in each excitation lead (bridge 0.45 V) | `ASM-H1-SG`, `CL-H1-SG-PDENS` 19 W/m² (≤ 78) |
| Gauge S (strip) | CF edge strip, 10 mm forward of the collar cheek, along the strip | same, dummy on a strip offcut; HX711 (`G12` board) | `CL-H1-SG-RES-FRAC` 0.1 % |
| Dial | shoe pad, along the L4 resultant, magnetic base on the test frame; removed before the 1.5 × step | 25 mm travel, 0.01 mm | `CL-H1-FP-TRAVEL-REQ` 23.6 mm to 1.0 × |
| Rule | steel rule on a fixed bar at the pad, for the 1.5 × step | 0.5 mm | `CL-H1-FP-DEFL-SHELL-ULT` 28.3 mm if the shell is right |
| Face-gauge factor | gauge on a `T-C4-BOARD-COUPON` in 4-point bend (GT-15), strain known from beam theory | k_face = ε_beam / ε_gauge; the stack is 0.63 × the face membrane stiffness, so expect k > 1 | `CL-H1-SG-REINF` |

Without the 1.5 kΩ leads the HX711's 4.3 V puts 1 760 W/m² into each grid on foam (`CL-H1-SG-PDENS-BARE`), and the
reading drifts as the face warms.

1. Gauges bonded 24 h (cyanoacrylate kit `G13`), leads strain-relieved. Warm up 10 min; zero. Shunt each bridge
   (100 kΩ across the dummy arm): reads 1 744 µε ± 1 % (`CL-H1-SG-SHUNT`).
2. Load path: one cord along the L4 resultant (49 N along + 34 N across at 1.5 × → 59.6 N at 34.8° from the "along" axis,
   6.08 kg; at 1.0 × 39.8 N, 4.05 kg), both senses; G2 77 N lateral at the tube end (7.85 kg); G3 35 N on the dummy
   can toward the wing (3.57 kg). Loads at 1.5 × limit are C4's procedure values.
3. **L4 to 1.0 × (limit)** in 25 % steps, 30 s hold, gauges and dial at each step. This is the comparison point.
4. Unload, re-zero check (≤ 10 µε), then **L4 to 1.5 ×** in 25 % steps; then G2 and G3 to 1.5 ×, both senses.

| At 1.0 × L4 | 3-D prediction (C4 S1) | Shell (C4 R4) | Decision |
|---|---|---|---|
| Face strain, gauge F × k_face | 850–1 075 µε (3.4–4.3 MPa at 4 GPa) | higher (board carries 1.06 × the moment) | > 1.25 × 1 075 µε → shell path, C4 re-runs |
| Strip strain, gauge S | 800 µε (88 MPa at 110 GPa) | lower (strips unloaded) | < 0.5 × 800 µε → strips not clamped |
| Pad deflection | 3.70 mm | 18.86 mm (C4 R5 shell) | ≤ **8.36 mm** (geometric mean) → 3-D path (`CL-H1-FP-DEFL-SPLIT`) |

| Pass at 1.5 × (C4) | Limit | Claim |
|---|---|---|
| No crack, face wrinkle, strip lift, pin push-out, shoe or cheek debond | visual + tap after each step | `CL-C4-D3-MS-FACE`, `CL-C4-SIM-MS-FACE-DRAWN` |
| Face strain at 1.5 × | report vs 1 612 µε (`CL-H1-FP-EPS-FACE-ULT`) | C4 |
| Gauges back to zero after unload | ≤ 20 µε | no set |

On fail: C4/C6/C3/D5 re-size the part named; a flight article is not proof-loaded again until re-built.

## GT-10 Pack retention and foot drops

| Test | Pass | Source |
|---|---|---|
| `T-H1-PACK-PULL`: pack-size **dummy** at the heaviest GT-05 pack mass, strapped as flown; **73.8 N** (7.52 kg) in ±x, ±y, +z | holds 10 s, slip ≤ 5 mm, hatch closed | `CL-H1-PACK-PULL-F` ← `CL-C1-PACK-CRASH-LOAD` → `R-PACK-RETENTION` |
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
Strap direction (CDR-27): each cord runs down from its eye along the aircraft x axis (vertical on the table) to an
anchor no more than 0.3 m outboard of the point below the eye, so the cord is within 30° of x and never pulls the
eye inboard or along the span. The eye bond is checked for that pull (`CL-C6-EYE-BOND-RF`, `-RF-SPLAY`); the load
case is C1 `G4-RESTRAINED` (`CL-C1-G4-TIE-LIM`, two of four cords carrying everything). Before the first run,
`T-D3-EYE-BONDED` has passed on two bonded eyes (58.8 N along x and 30° outboard).

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

Lever frame (R3, CR-C6-33 and CR-C6-39; figure `FIG H1-09`, `ASM-H1-LEVER`): 2×4 lever 1.0 m on an M8 pivot, jug
hook at 0.900 m, three coupon clevis holes at **0.045 m (20:1, added by CDR-28)**, **0.060 m (15:1)** and
**0.100 m (9:1)**. Pivot and the clevis holes go through a pair of 3 mm steel side plates 40 × 200 mm, each held to
the lever by **6 × M6** through-bolts with washers (4 would bear on the wood at 4.5 MPa with the 20:1 hole loaded). A
bare M8 in the wood would bear at 13.6 MPa across the grain, against 4.3 MPa allowed (`CL-H1-LEVER-WOOD-BRG`). Short-
side counterweight tares the lever. Water jugs ≤ 20 kg, filled slowly from a hose and weighed after failure.

| Item | Value | Claim |
|---|---|---|
| Capacity 20:1 / strip-anchor design force (`CL-C6-STRIP-ANCHOR-F` 1 399 N at the D-105 side-load cap) | **3 923 N / 1 399 N = 2.80** (≥ 1.5, so the coupon is taken to failure) | `CL-H1-LEVER-CAP20`, `-FAIL-HEADROOM` |
| Capacity 15:1 / needed (1.25 × 1 400 N) | 2 942 / 1 750 N | `CL-H1-LEVER-CAP`, `-NEED` (+41 %) |
| Capacity 9:1 | 1 765 N (40–300 N coupons; its strip-anchor need is retired, CDR-28) | `CL-H1-LEVER-CAP9` |
| Lever bending at full jug | 3.5 MPa (≤ 6.0) | `CL-H1-LEVER-SIGMA` |
| Pivot on the steel plates / M6 bolts on the wood | 86 MPa (≤ 150) / 3.0 MPa (≤ 4.3) | `CL-H1-LEVER-PLATE-BRG`, `-M6-BRG` |
| Calibration | 4.000 kg at 20:1 balances 0.200 kg, 3.000 kg at 15:1 balances 0.200 kg, 2.000 kg at 9:1 balances 0.222 kg, within 2 %; 20 kg proof on a steel bar for 60 s | `T-H1-LEVER-CAL` |

Compression and push coupons on the 20 kgf cell under the Jacobs drill press. Record every failure load and mode;
allowable = owner's rule (mean − 2 s, or 0.5 × mean). A 3.9 kN failure stores energy in the cord: catch strap under
the jugs, face shields, nobody under the long arm.

| Test (owner) | Specimens | Rig | Pass | Window |
|---|---|---|---|---|
| `T-C2-XPS-COUPON` (C2) | 100 mm cube; 300 × 40 × 30 mm strips bare and taped | scale; 3-point bend on jugs | E and strength recorded | foam arrives (Dec) |
| `T-C3-BOND-COUPON` (C3) | 3 PETG pads on F-250, 3 on board (flat-wise); 3 lap shears | lever | foam or paper failure | Dec |
| `T-C3-STOP-PUSH` (C3, CR-C3-20) | tray **rear piece with the strut** on a handle-bridge offcut, and the **front piece** with its 1 mm bed and a nose-wall offcut, each **epoxied to a foam-board floor offcut as built** (24 h); flight print settings | 50 × 50 mm block on the 20 kgf cell under the drill press: aft (+x) at 16 mm above the tray to 90 N; forward (−x) at 13 mm to 85 N; guide 85 N over 60 mm. Then one to failure on the 9:1 lever | no crack, no board peel or delamination at the tray edge, set < 0.5 mm; failure mode recorded | first tray print |
| `T-C4-BOARD-COUPON` (C4) | 3 × 50 × 300 mm per layer count | 4-point bend, span 250 mm | allowable and D recorded | Dec |
| `T-C6-LAP-PETG` (C6) | 5 PETG-CF + 5 ASA-CF lap shears | lever | ≥ 2.0 MPa | ASA spool (Dec) |
| `T-C6-BOARD-LAP` (C6) | 5 shear + 5 flat-wise tabs | lever | modes recorded | Dec |
| `T-C6-XPS-PULL` (C6) | 10 pucks Ø30 mm | lever | allowables recorded | Dec |
| `T-C6-BOARD-CORNER` (C6) | 2 U-sections | jugs | ≥ 43 N | Dec |
| `T-C6-INSERT` (C6) | 3 inserts | lever | ≥ 300 N each | first POD-002 print |
| `T-C6-STRIP-ANCHOR` (C6) | 40 mm two-face collar (ring + tail), strip pair bonded as built, ring on a 22 mm steel mandrel; pull ONE strip along its axis | **20:1 hole** | ≥ `CL-C6-STRIP-ANCHOR-F` (1 399 N at the D-105 cap; read the claim on the day, not this table) with neither bond nor tail failing; then to failure, printed tail and tow-lashed tail side by side (CDR-02): failure load / design force is the measured RF | early-cart stock, before the order |
| `T-C6-HEAD-CREEP` (C6) | ASA plate, 4 × M3 at 0.20 N·m | 70 °C, 2 h: sealed bag in a water bath with a probe (no oven needed) | breakaway ≥ 0.15 N·m | first mount |
| `T-D5-COUPON` (D5) | 3 type-U + 3 type-L cartridge pairs | drill press over the 20 kgf cell (need 5.1 kgf, `CL-H1-D5-CELL-REQ`), 40 mm at < 10 mm/s, every 2 mm | U 34.5–38.5 N, L 29.5–33.0 N, U/L 1.15–1.19 (U95 0.006, `CL-H1-D5-RATIO-U`), peak ≤ 1.15 × plateau, flat to 40 mm | first cartridges |
| `T-D5-PAD-MU` (D5) | foot with the faced pad, 0.65 kg | incline board covered with the landing mat; 5 runs dry, 5 with the mat damp | every run slides at or below **21.5°** (μ ≤ 0.40 less U95; D-105, CDR decision B1). The test is now an upper bound: the pad face caps the foot side load at 24.5 N | pad sheet, before the order |
| `T-D5-SIDE` (D5) | every flight shoe, unbonded, on a stepped offcut; one bonded sample per printed batch | cord and jug at the pad, +y then +z | each flight shoe holds **28.2 N** (1.15 × limit) 3 s with no crack; the batch sample fails at or above **45.9 N** | every shoe batch |
| `T-D3-EYE-BONDED` (C6 / D3) | two FIN-013 eyes bonded on a printed boss | spring scale along x, and 30° outboard | 58.8 N held 10 s, witness line unmoved; then to failure | first block print |

Torque checks (0.20 N·m) without a torque driver: 2.0 N on a spring scale at 0.10 m on the hex key.

## GT-16 Tube bend and torsion (Aloft `W03`) — result to I1 by 10 Dec

`T-C4-TUBE-BEND` (= `T-J1-TUBE-BEND`), `T-C4-TUBE-TORSION` with GJ (CR-C2-15), CR-C4-21, CR-I1-08. Run on arrival
(~27 Nov); weigh first. One specimen gives C4 E and G, and C2 the three values its 3-D FEA assumes
(`ASM-C2-TUBE-ET`: E axial 70 GPa, G 3 GPa, E hoop 8 GPa). The pass lines of this card are C4's live claims
`CL-C4-D3-TUBE-E-REQ` and `-G-REQ` (CDR-19): read `CL-H1-TUBE-E-PASS` / `-G-PASS` on the day, not this table.

1. Span 0.80 m on two 22 mm dowels; printed saddle at mid-span; 0.5 kg steps to 4.0 kg and back.
2. Deflection: dial indicator (borrowed) or caliper depth rod against a fixed bar (U95 0.03 mm).
3. E = F L³ / (48 I δ) from the slope of 8 steps, I = 3.645 × 10⁻⁹ m⁴ (`CALC-H1-BEND`).
4. **Torsion (GJ).** 0.40 m clamped in printed V-blocks, 0.30 m lever clamped at the far end, 0.5–2.0 kg in 0.5 kg
   steps, both senses (T up to 5.88 N·m). Two laser pointers in printed clamps on the tube **0.30 m apart**; spots on
   a wall 3.0 m away, read to ±1 mm. Twist over the gauge length Δθ = atan(s₂/L) − atan(s₁/L), so grip slip and
   lever-clamp rotation drop out. GJ = T L_g / Δθ from the slope; G = GJ / J, J = 7.29 × 10⁻⁹ m⁴.
5. **Ring crush (E_hoop).** 20 mm ring cut from the offcut; flat plates on the 20 kgf cell under the drill press,
   4 N steps to 20 N; dial (0.01 mm) on the upper plate. E_hoop = 0.1488 P R³ / (δ I), R = 10.5 mm, I = b t³/12.

| Pass | Limit | Claim |
|---|---|---|
| Deflection at 4.0 kg (E ≥ **78.6 GPa**, `CL-C4-D3-TUBE-E-REQ`) | ≤ **1.43 mm** (1.46 mm at 78.6 GPa − U95); 1.61 mm was the old 70 GPa line | `CL-H1-TUBE-E-PASS`, `CL-H1-TUBE-DEFL-ACCEPT` |
| Peak stress | 23.7 MPa (tube stays usable as the spare) | `CL-H1-TUBE-SIGMA` |
| E read uncertainty | 1.8 % | `CL-H1-TUBE-E-U` |
| GJ (both senses agree within 5 %) | ≥ **31.4 N·m²** (G ≥ **4.31 GPa**, `CL-C4-D3-TUBE-G-REQ`): twist over the 0.30 m gauge ≤ **3.22°** at 2.0 kg. Below it the ±45° fallback tube is ordered. 21.9 N·m² (G 3 GPa) was C4's low corner only | `CL-H1-TUBE-G-PASS`, `CL-H1-TORS-GJ-PASS`, `-TWIST-PASS`, `CL-H1-TORS-GJ-LO` |
| GJ read uncertainty (G 10 GPa, 73 mm spot difference) | 1.9 % | `CL-H1-TORS-U` |
| Torsion peak shear | 8.9 MPa (≤ 30, tube stays usable) | `CL-H1-TORS-TAU` |
| Ring δ at 20 N / E_hoop uncertainty | 0.26 mm at 8 GPa / 5.5 % | `CL-H1-RING-DEFL`, `-U` |

Pass → I1 orders `W04` from Aloft. Fail or no result by 10 Dec → overseas tube, order by 15 Dec (I1). C4 replaces
its E/G assumptions, and C2 its `ASM-C2-TUBE-ET` G and hoop values, with the measured values either way.

## GT-17 Mount rocking stiffness

`T-C4-MOUNT-STIFF`, with `T-C6-CANT-SEAT` and `T-C6-PROPNUT` on the same first ASA mount. Figure `FIG H1-08`.

Pass level **≥ max(1 100, `CL-C4-D3-MOUNT-K-REQ`) about both rocking axes**: 1 100 is CR-C4-41's floor. C4's
claim is **1 642 N·m/rad** today (2026-11-13, D-91 mount with the D-89c cheek); the card reads the claim on the day.
C4's estimate of the mount as drawn is 2 259 N·m/rad (`CL-C4-D3-MOUNT-K-EST`, × 1.38 of the pass level). C4's readout
(two 0.01 mm dial gauges at 0.5 kg) sees 5.2 µm at the pass stiffness, under one division (`CL-H1-MSTIFF-DIAL-UM`),
so GT-17 uses an optical lever (CR-H1-10).

1. Motor clamped in the mount on a 60 mm tube stub in a vice. Mirror on the can side, second mirror on the collar;
   laser spots on mm paper **5.0 m** away (a corridor). Tripod phone photo of the paper at each step; the spot
   centre is read against the 1 mm grid to ±0.3 mm.
2. 0.5, 1.0, 1.7 kg over a cord at the prop nut, in y and then in z (top step raised from 1.5 kg by CDR-28;
   1.7 kg = 79 % of the mount proof load,
   `CL-H1-MSTIFF-LOAD-FRAC`). Measure the arm a (nut to collar) with calipers; sizing used a = 0.0577 m.
3. θ = (spot_can − spot_collar) / (2 L); k = F a / θ from the slope.

| Pass | Limit | Claim |
|---|---|---|
| Net spot travel at 1.7 kg, y and z | ≤ **5.56 mm** (5.86 mm at 1 642 N·m/rad − 0.3 mm read) | `CL-H1-MSTIFF-SPOT-ACCEPT` → `CL-H1-MSTIFF-K-PASS` = `CL-C4-D3-MOUNT-K-REQ` |
| k uncertainty at the pass line | 5.1 % (≤ 10 %) | `CL-H1-MSTIFF-U` |
| `T-C6-CANT-SEAT` | ≥ 6 turns from first bite; 0.05 mm feeler does not enter | C6 |
| `T-C6-PROPNUT`: 1.5 N·m on/off × 10 | witness line and lip cap unmoved | C6 |

## GT-18 Tap tests

`T-C4-TAP-D3`, `T-C2-TAP-TEST`, `T-C4-PROP-SWING`. Acquisition: FC raw IMU ≥ 1 000 Hz (need 935 Hz,
`CL-H1-TAP-FS-REQ`). A ~400 Hz phone app reads only to 160 Hz (`CL-H1-TAP-PHONE-MAX`): use it for C2's 12–22 Hz wing
modes only (CR-H1-11). 4 s records (0.25 Hz bins), 5 taps per direction, averaged.

Windows (± `P:requirements.vibration_sep_frac` 0.2, `CALC-H1-TAP`):

| Order | Hover 5 416 rpm | Cruise 5 946 rpm | Cap 9 350 rpm |
|---|---|---|---|
| 1P | 90.3 Hz (72.2–108.3) | 99.1 Hz (79.3–118.9) | 155.8 Hz (124.7–187.0) |
| 2P | 180.5 Hz (144.4–216.6) | 198.2 Hz (158.6–237.8) | 311.7 Hz (249.3–374.0) |

1. `T-C4-TAP-D3`: finished wing on foam blocks, props on; tap each bell in y and z; FFT to 450 Hz. Then tap the
   centre of each half-fin board panel (CR-C4-38) with the FC on that quarter's station; record the panel mode.
2. `T-C2-TAP-TEST`: aircraft on bungees (free-free); phone at the pod and a fin tip for the wing modes, FC IMU for
   the rest; tap a can fore-aft and a fin tip sideways.
3. `T-C4-PROP-SWING`: bifilar, two 0.5 m threads at the blade tips, 20 swings.

| Pass | Limit | Claim |
|---|---|---|
| Fin-station f1, each quarter | outside 1P hover, 2P hover and 2P cruise windows (record of `R-VIBRATION` a); predicted 255.5 Hz lower / 262.4 Hz upper (3-D, C4 S1) | `CL-C4-SIM-F1-LO`, `-UP`, `CL-C4-D3-SEP` |
| Board panel mode (centre tap) | report vs 71–73 Hz predicted, inside the 1P hover window; C4 judges it on station KE < 4 % | `CL-C4-D3-PANEL` (CR-C4-38) |
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
| `FIG H1-04` | still, two panels | step 1: inverted wing on the pod support, 4 pad stacks per side, relief slings over pulleys; step 2: V-block at y 0.32, pads 3 and 4 | pad stacks, slings, V-block | front, low | y 0.12 / 0.25 / 0.355 / 0.465, relief at 0.32, masses from GT-08 |
| `FIG H1-05` | still | station, G2, pod-bracket and D5 side hangs | jugs, cords, pulleys | iso | 21.1 N, 57.3 N, 42.2 N, 199.6 N, 59.0 N |
| `FIG H1-06` | still | tilt board at 30° | board, stop strip | along the hinge | angle arc, catch zone |
| `FIG H1-07` | still | restrained table | straps, root eyes | iso 45°, high | 29.5 N each, keep-out ±30° |
| `FIG H1-08` | still | mount-stiffness optical lever | mirrors, cord, weight | plan view | L 5.0 m, a 0.0577 m, spot pair, phone on tripod |
| `FIG H1-09` | still | coupon lever frame 15:1 / 9:1, strip-anchor coupon on the mandrel | lever, steel side plates, jug, coupon | side, ortho, plus a plate detail | 0.060 / 0.100 / 0.900 m, pivot M8, 4 × M6, catch strap |
| `FIG H1-10` | still | fin test article on the frame: L4 cord along the resultant, dial on the pad, gauges F and S with their dummies | cord, dial, gauge grids (enlarged inset) | iso 35°, plus a face-on inset of the shoe | gauge F 5 mm below the leg edge at x 0.30; gauge S 10 mm ahead of the cheek; 34.8° cord |
| `FIG H1-11` | still | ESC dummy on the half-fin pad behind the stand prop | dummy, XPS, TC1–TC3 | side, ortho, section through the pad | 45 × 20 × 6 mm, 3 mm XPS, TC positions, 30 mm inflow probe |
| `FIG H1-12` | still | tube torsion (two lasers) and ring crush | lasers, lever, ring, plates | iso | L_g 0.30 m, wall 3.0 m, lever 0.30 m; ring 20 mm |
| `ANIM H1-A1` | 6 s loop | board 0 → 32°, pads lift at 30° | board, lifting feet | as `FIG H1-06` | live angle |
| `ANIM H1-A2` | 8 s loop | pitch then roll stick in FBWA, then QHOVER; elevons move | elevon panels | rear-iso 30° | mode, stick icon |
| `ANIM H1-A3` | 8 s loop | mock-up parts removed one by one | the part being removed | as `FIG H1-02` | config name |
| `ANIM H1-A4` | 8 s loop | fin test article: L4 cord loads in 25 % steps to 1.0 ×, deflection × 10 exaggerated, dial needle and two strain bars rise; then 1.5 × | the fin quarter (deformed), cord, dial | as `FIG H1-10` | load %, predicted vs split line 8.36 mm |

## Test gear: bought and borrowed (CR-A1-39, D-39, D-72)

Bought new for ground test: I1 lines `G12` $17.00 (1 kgf bar cell + HX711, 5 K-type probes) and `G13` $9.00 (foil
gauges + cyanoacrylate kit, CR-C4-38): $26.00, $6 over the D-39 $20 line (`CL-I1-GROUNDTEST-BOUGHT`; A1's decision).
Already in the baseline BOM: `G04` watt meter, `G05` IR thermometer, `G06` 20 kgf cell + HX711 + Nano, `B04` 11×4.5MR
props. Everything else is borrowed.

**Jacobs Maker Pass (rewritten 2026-11-13, `T-I1-BORROW`).** The owner pays the Maker Pass outside the budget. It is drop-in, in-lab access, not equipment loans
(https://jacobsinstitute.berkeley.edu/making-at-jacobs/, checked 2026-11-13), so nothing below is taken home. The soldering kit lines `G07`–`G09` are deleted from the BOM (the
Electronics Lab has the stations and meters); `G10` flux and wick is a gated fallback (`X10`). The hot-wire gear (`G11`, `H05`, $62.54) is **bought**: Jacobs lists no hot-wire cutter
(https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/, checked 2026-11-13). Remaining questions for staff: `team/H1/JACOBS-LOAN-REQUEST.md`. No purchase waits on the answers.

| Item | Card | Lender | Status | Fallback (cost) |
|---|---|---|---|---|
| **Soldering station, solder (in lab)** | build, GT-09 gauge leads | Jacobs Electronics Lab, covered by the pass | `CHECKED` listed 2026-11-13 (solder provided; flux and wick not stated) | I1 `X10` $16.54 (flux, wick) |
| **Hot-wire foam cutter gear (30 V supply, Ni80 wire, bow)** | practice cores Dec, build Jan | **bought** (`G11`, `H05`, 20 Nov order); not on the Jacobs list | n/a | $62.54 in the committed order |
| Bench power supply (Rm at 2 A; I0 at 10 V; `T-F3-5V`) | GT-02a, GT-12 | Jacobs Electronics Lab, studio 110 (in-lab use) | `CHECKED` listed (`SRC-H1-JACOBS-EQUIP`) | flight pack + meter ($0) |
| Multimeters ×2 (4-wire Rm, rails; V and I for the ESC dummy) | GT-02a, GT-04, GT-12 | Jacobs Electronics Lab (in-lab) | `CHECKED` listed 2026-11-13 | a team-owned meter ($0 assumed; the old `G09` line is deleted) |
| Oscilloscope (`T-F1-PRECHARGE`, `-RIPPLE`) | GT-12, GT-13 | Jacobs Electronics Lab | `CHECKED` listed | run in the lab |
| Saleae logic analyzer (I²C / DShot debug) | GT-12 | Jacobs Electronics Lab | `CHECKED` listed | — |
| 350 Ω 0.1 % resistors ×4, 1.5 kΩ ×4, 100 kΩ ×2, 10 Ω 5 W ×1 | GT-09, GT-04 | Jacobs Electronics Lab parts stock | `UNVERIFIED` (ask) | ≈ $5 `EST` (A1) |
| Drill press (D5 crush, ring crush, stop push) | GT-15, GT-16 | Jacobs woodshop (Delta variable speed) or metal shop (Clausing) | `CHECKED` listed | hand screw press on the bench ($0) |
| K-type reader (3 channels for the ESC dummy) | GT-04 | a Jacobs DMM with a K input | `UNVERIFIED` (ask) | I1 gated `X09` $16.54 |
| **Dial indicator 25 mm travel** + magnetic base | GT-09, GT-16 | Jacobs metal shop hand tools | `UNVERIFIED` (ask) | 10 mm dial re-zeroed at 1.0 ×; caliper depth rod for GT-16 |
| Two 3 mm steel plates 40 × 200 mm, M8 and M6 bolts | GT-15 | Jacobs metal shop scrap | `UNVERIFIED` (ask) | `H01` hardware share |
| 22 mm steel mandrel (strip-anchor ring) | GT-15 | metal shop scrap / bolt with tape | `UNVERIFIED` | printed sleeve on an M20 bolt |
| Digital calipers, 0.1 g scale | GT-02a, GT-16 | team members / Jacobs | `UNVERIFIED` (ask) | — |
| Two 5 kg × 1 g scales | GT-06, GT-07 | team members' kitchen scales | `UNVERIFIED` (ask) | one scale + knife edge ($0) |
| Plywood, 2×4 lever, 608 bearings, M8 rod | GT-01, GT-15 | Jacobs scrap bin, team spares | `UNVERIFIED` (ask) | `H01` hardware share |
| Spring/luggage scale 0–50 kg, ball-bearing pulleys ×3 | GT-08, GT-09, GT-10, GT-13 | team | `UNVERIFIED` | lever frame + jugs ($0) |
| Laser pointers ×3, small mirrors | GT-16, GT-17 | team | `UNVERIFIED` | $3 `EST` |
| Fridge (cold pack, bagged), water jugs 2 × 10 L, sand, bungees, phone apps, matte black paint, 3 mm XPS | GT-02e, GT-04, GT-15, GT-18 | team | — | — |

Record each answer in this table (status → `CHECKED` with the date and the staff name).
