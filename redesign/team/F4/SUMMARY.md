# F4 — flight-control software

Status `PROPOSED`, revision **F4-R4c**, 2026-11-10. Firmware ArduPlane 4.7.x stable on the CoreWing F405 Wing V2
(D-33, no Lua), `Q_TAILSIT_ENABLE` 1, copter Quad-X mixing on the four fin motors, two elevons. ArduPilot, not PX4:
the chosen board has an ArduPilot target and no PX4 target, and ArduPilot gives copter-motor tailsitter mixing,
differential-thrust yaw in fixed wing and an ESC-rpm notch over bidirectional DShot. Nothing has been loaded, flown or
run in SITL (SITL is not installed), so every flight behaviour is `UNVERIFIED`.

## Deliverables (`redesign/subsystems/flight-software/`)

| File | What |
|---|---|
| `K09L.param` | 161 parameter lines (155 unique + 6 LEGACY duplicates for older builds), a comment above every one |
| `K09L-STAND.param` | thrust-stand overlay: 25 A limiter, fence off, log disarmed, raw-IMU batch log at sensor rate |
| `SPEC.md` | key numbers, motor/output map, transition logic and limits, elevon schedule, failsafes, landing |
| `TUNING-PLAN.md` | 12 steps: bench → hanging yaw → stand → hover → FW tune → dive / level legs → transition |
| `SITL-PLAN.md` | 17 cases incl. RC / battery / fence / GPS / motor-out / e-stop; status `UNVERIFIED` |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal |

## R4b changes (action items)

| Item | Was → now | Unit | Claim (value, margin) | Status |
|---|---|---|---|---|
| `THR_MAX` (D-50, CR-F4-15 accepted) | 70 kept | % | `CL-F4-VLEVEL-VH` 0.98 (+2 %) | `UNVERIFIED` |
| `Q_LAND_FINAL_SPD` / LEGACY `Q_LAND_SPEED` (CR-D5-21) | 0.5 / 50 → **0.3 / 30**; `Q_LAND_FINAL_ALT` 6 stated | m/s, cm/s, m | `CL-F4-LAND-SPD` 0.30 ≤ 0.32 (+6 %) | `UNVERIFIED` |
| `BATT_LOW_MAH` (CR-E2-20) | 2 600 kept | mAh | `CL-F4-BATT-LOW` (0 %) | `PROPOSED` |
| `RC_OPTIONS` | 8 480 kept | — | — | `PROPOSED` |
| Crossover ceilings until T-C2-TAP-TEST (CR-B3-19) | written into the file: pitch ≤ 4.5, yaw ≤ 2.4 | Hz | `CL-F4-XOVER-*` 1.04 / 2.44 / 1.01 | `UNVERIFIED` |
| `SERVO5/6_MIN/TRIM/MAX/REVERSED` (CR-D6-09) | unset → L 1003/1500/1976 rev, R 1024/1500/1997 | µs | `CL-F4-ELEVON-PWM-ERR` 0.3 ≤ 1.5; `-SPAN` 497 ≤ 500 (+0.6 %) | `PROPOSED` |
| `MIXING_GAIN` (new, default stated) | 0.5 → pure pitch 12.5° | — | `CL-F4-MIX-PITCH` 0.88 (+12 %) | `UNVERIFIED` |
| `GPS1_POS` (CR-F3-20, CG x 0.0522, z 0.0185) | (−0.036, 0, −0.169) → **(−0.023, 0, −0.1595)** (R4c: z −0.160 → −0.1595) | m | `CL-F4-SENSOR-POS-ERR` 0.2 mm ≤ 2 mm | `UNVERIFIED` |
| `INS_POS1/2` (same CG) | (0.054, 0.046, −0.035) → **(0.062, 0.046, −0.0205)** (R4c: z −0.021 → −0.0205) | m | same | `UNVERIFIED` |
| Raw-IMU log (CR-H1-18) | flight file `INS_LOG_BAT_OPT` 4 → **5** (sensor rate + pre/post); stand 1 | — | ≥ 935 Hz read from the log | `UNVERIFIED` |
| `Q_M_BAT_CURR_MAX` claim (CR-A2-14) | value-only → calc-backed | A | `CL-F4-BAT-CURR-MAX` 100 ≤ 100; `-MOTOR` 25 ≤ 25 | `PROPOSED` |
| Cant sense (D-52) | D3 −1 published; spin map kept (CR-B4-16a) | — | `CL-F4-CANT-SENSE-D3` **+1** (was −1 `FAILS`) | `MODELLED` |
| Re-run on A3 split / inertia (R4c, A3 roll-up 2026-11-10 04:35) | split **1.2158**; Ixx 0.1732 / Iyy **0.0442** / Izz 0.1679 kg·m²; CG z 0.0185 m | — | `CL-F4-SPLIT-OUT` 0.671 ≤ 0.84 (+20 %); crossover 1.04 / **2.48** / 1.01 Hz (+77 / +45 / +58 %); P ceilings 0.347 / 0.145 / 0.947 (TUNING-PLAN keeps 0.34 / 0.14 / 0.94) | `MODELLED` |

## Check

`python -I redesign/team/F4/fsw_check.py`: lint is OK on both files and the params.json mirror matches.
**40 claims, none negative.** Thinnest margins: `CL-F4-BAT-CURR-MAX` / `-MOTOR` / `-BATT-LOW` / `-BATT-CRT` at 0 %, which is
expected because these are set equal to their limits. `CL-F4-ELEVON-PWM-SPAN` +0.6 %, `CL-F4-SPIN-MAX` +1 %,
`CL-F4-VLEVEL-VH` +2 %. 67 of the 155 unique names are matched to ArduPilot source; the other 88 wait for SITL S1 on
the 4.7.x tag. R4c (2026-11-10): the 7 F4 drifts were `CALC-F4-XOVER` (6 outputs) and `CALC-F4-SPLIT`, stale because
A3 rewrote split and inertia after F4's last run. Re-run at 04:38 on A3's 04:35 roll-up, then `proofs/build_graph.py`
rebuilt: **0 F4 errors or drifts**, 2 F4 claims `CHECKED`, 38 `UNVERIFIED` (await tests). The 633 graph errors left
belong to other roles. A3 is still re-running, so re-run `fsw_check.py` before each graph build.
`ASM-F4-CG-Z` now reads 0.0185 m from `CALC-A3-CG` `cg_m[2]` (MASS-CG.md rounds it to +0.019 basic, +0.018 predicted).

## Findings others depend on

| Finding | Effect |
|---|---|
| `Q_LAND_FINAL_SPD` covers QLAND and the end of RTL only. A pilot landing in QHOVER/QLOITER descends at the stick rate (up to 1.2 m/s) | the flight card must say QLAND for the last 6 m (CR-F4-18 to H3) |
| F3's offsets use CG z 0, but A3's model puts the CG at +0.0185 m | F4 uses +0.0185. F3 should re-run, and A3 should publish a CG-z claim (CR-F4-19) |
| B3's forward CG limit is now 0.0509 m (`CL-B3-CG-FWD`), and `cg.x_target_m` is still 0.0522 | no F4 change: the offsets follow `P:cg.x_target_m`, and A3's basic CG is 0.0522 today |
| The elevon ends use 497 of the 500 µs that D6 assumes for ±45° | if the servo turns less than 45°, the TE-up end needs a pulse outside 1000–2000 µs (CR-F4-20 to D6) |
| With `MIXING_GAIN` 0.5, pure pitch gives 12.5°, which equals B3's half-travel trim limit | trimmed CLmax needs 11.0° (`CL-B3-DELTA-STALL`), leaving 12 % margin |
| ArduPilot has no airspeed-scheduled surface limit and the F405 has no Lua | the ≤ 1/3 travel at VD is held by the envelope only (CR-F4-12, accepted at D-50) |

## Open

R4c closes CR-F4-12 and CR-F4-15 (both accepted, D-50). Still open: CR-F4-04, -06, -09, -10, -14, -16, -18, -19
(CG z now 0.0185), -20.
