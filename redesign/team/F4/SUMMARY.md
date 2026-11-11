# F4 — flight-control software

Status `PROPOSED`, revision **F4-R5**, 2026-11-10. Firmware ArduPlane 4.7.x stable on the CoreWing F405 Wing V2
(D-33, no Lua), `Q_TAILSIT_ENABLE` 1, copter Quad-X mixing on the four fin motors, two elevons. ArduPilot, not PX4:
the chosen board has an ArduPilot target and no PX4 target, and ArduPilot gives copter-motor tailsitter mixing,
differential-thrust yaw in fixed wing and an ESC-rpm notch over bidirectional DShot. Nothing has been loaded, flown or
run in SITL (SITL is not installed), so every flight behaviour is `UNVERIFIED`.

## Deliverables (`redesign/subsystems/flight-software/`)

| File | What |
|---|---|
| `K09L.param` | 161 parameter lines (155 unique + 6 LEGACY duplicates for older builds), a comment above every one; R5 values |
| `K09L-STAND.param` | thrust-stand overlay: 25 A limiter, fence off, log disarmed, raw-IMU batch log at sensor rate |
| `SPEC.md` | key numbers, motor/output map, transition logic and limits, elevon schedule, failsafes, landing |
| `TUNING-PLAN.md` | 12 steps: bench → hanging yaw → stand → hover → FW tune → dive / level legs → transition |
| `SITL-PLAN.md` | 17 cases incl. RC / battery / fence / GPS / motor-out / e-stop; status `UNVERIFIED` |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal |

## R5 changes (A1-R5 action items: D-65, D-66, D-71, D-62)

| Item | Was → now | Unit | Claim (value vs limit, margin) | Status |
|---|---|---|---|---|
| `Q_PILOT_SPD_DN` / LEGACY `Q_PILOT_SPEED_DN` (D-65) | 1.2 / 120 → **1.0 / 100**: full down stick in QHOVER/QLOITER is the design hard landing; 0.2 m/s kept for loop overshoot, no rangefinder, ground effect | m/s, cm/s | new `CL-F4-TOUCHDOWN-SINK` 1.0 ≤ `landing_sink_ms` 1.2 (+17 %), verifies `R-LANDING-IMPACT` (CR-A2-31b) | `UNVERIFIED` |
| `Q_LAND_FINAL_SPD` / `Q_LAND_SPEED` (D-65) | 0.3 m/s / 30 cm/s kept (= 0.3 m/s) | m/s | `CL-F4-LAND-SPD` 0.30 ≤ 0.32 (+6 %) | `UNVERIFIED` |
| `Q_WP_SPD_DN` | 1.2 kept: ends at `Q_LAND_FINAL_ALT` 6 m, never reaches the ground | m/s | `CL-F4-DESCENT` 1.2 ≤ VRS 1.88 (+36 %) | `UNVERIFIED` |
| `FLTMODE1-6`, `INITIAL_MODE` (D-66, A2 worded `R-SPIRAL`) | 17 / 18 / 19 / 5 / 7 / 11, boot 17 kept: all roll-stabilised; lint also bars any `RCn_OPTION` 51 / 52 (MANUAL / ACRO switch) | — | new `CL-F4-NO-RAW-MODES` 0 ≤ 0 (no MANUAL 0, STABILIZE 2, TRAINING 3, ACRO 4, QACRO 23), verifies `R-SPIRAL` (CR-A2-31a) | `CHECKED` (lint) |
| `AIRSPEED_MIN` (old `ARSPD_FBW_MIN`, D-71) | 16 kept, **not frozen**: after `T-B2-STALL` set ceil(1.3 × measured trimmed stall); 16 holds to 12.31 m/s; TUNING-PLAN step 6d, before any transition | m/s | new `CL-F4-ARSPD-MIN-D71` 16 ≥ 1.3 × 11.99 = 15.59 (`CL-B2R3-VTR-GATE-FWD`, +3 %) | `UNVERIFIED` (by test) |
| `INS_POS1/2`, `GPS1_POS` (D-62 CG) | X 0.062 → **0.059**, GPS X −0.023 → **−0.026**; Z −0.0205 / −0.1595 kept; CG now read from `P:cg.x_target_m` 0.0490 and `P:cg.z_target_m` 0.0185 (A3's `CL-A3-CG-Z` 0.0186; `ASM-F4-CG-Z` retired) | m | `CL-F4-SENSOR-POS-ERR` 0 ≤ 2 mm (was 3.2 mm `FAILS` on the R5 keys before the reset) | `UNVERIFIED` (F3 has not re-run `CALC-F3-OFFSETS`, CR-F4-19) |
| Re-run on the R5 keys | A3 14:30 roll-up (CG 0.0485, 0, 0.0186), B3 / B2 R5 claims | — | 43 claims, none negative; crossover 1.03 / 2.36 / 1.01 Hz; split output 0.672; `CL-F4-MIX-PITCH` 0.84 (+16 %) | `MODELLED` |

## Check

`python -I redesign/team/F4/fsw_check.py` (R5, 2026-11-10 ~14:50, on A3's 14:30 roll-up and the A1-R5 keys): lint OK on
both files (every line commented, no duplicates, LEGACY pairs equal, no `RCn_OPTION` that selects MANUAL / ACRO), and
the params.json mirror matches (new keys `fsw.fltmodes`, `fsw.initial_mode`). **43 claims, none negative.** Before
the R5 reset, `CL-F4-SENSOR-POS-ERR` read 3.2 mm `FAILS` against the D-62 CG; now 0. Thinnest margins: `-BAT-CURR-MAX`
/ `-MOTOR` / `-BATT-LOW` / `-BATT-CRT` 0 % (set equal to their limits), `-ELEVON-PWM-SPAN` +0.6 %, `-SPIN-MAX` +1 %,
`-VLEVEL-VH` +2 %, `-ARSPD-MIN-D71` +3 %. 67 of 155 unique names are matched to source; 88 wait for SITL S1.
`proofs/build_graph.py` was started after the run and had not finished when this file was written: the graph result is
`UNVERIFIED` for R5. Every new reference (`CL-B2R3-VTR-GATE-FWD`, `P:requirements.landing_sink_ms`, `R-SPIRAL`,
`R-LANDING-IMPACT`, `R-STALL`, `R-TRANSITION`) resolves to an existing id.

## Findings others depend on

| Finding | Effect |
|---|---|
| `Q_LAND_FINAL_SPD` covers QLAND and the end of RTL only. In QHOVER/QLOITER the pilot descends at the stick rate (now ≤ 1.0 m/s) | the flight card says QLAND for the last 6 m (CR-F4-18 to H3) |
| QSTABILIZE has no climb-rate loop, so throttle is direct and the sink at contact is not limited | no landing in QSTABILIZE except to recover (CR-F4-21 to H3). D-65's 1.2 m/s covers only the altitude-holding modes |
| F3's `CALC-F3-OFFSETS` still uses CG (0.0522, 0, 0) and the R3 GPS point | F4 sets the offsets from the D-62 CG on F3's R4 points. F3 should re-run and say whether the D-62 bay move moved the mast (CR-F4-19) |
| `AIRSPEED_MIN` 16 only holds while the measured stall is ≤ 12.31 m/s | if `T-B2-STALL` measures more, MIN and CRUISE both go to 17. B2 needs to publish the measured stall as a claim (CR-F4-22) |
| A2's `R-LANDING-IMPACT` text cites `CL-F4-DESCENT` | that claim's limit is VRS 1.88 m/s. The touchdown claim is `CL-F4-TOUCHDOWN-SINK` (CR-F4-23 to A2) |
| The elevon ends use 497 of the 500 µs that D6 assumes for ±45° | see CR-F4-20 to D6 |
| ArduPilot has no airspeed-scheduled surface limit and the F405 has no Lua | the ≤ 1/3 travel at VD is held by the envelope (D-50) |

## Open

R5 answers CR-A2-31 (a, b) and the A1-R5 F4 row. It adds CR-F4-21 (H3), -22 (B2), -23 (A2). Still open: CR-F4-04, -06,
-09, -10, -14, -16, -18, -19, -20 to -23.
