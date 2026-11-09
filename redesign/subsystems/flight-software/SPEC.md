# flight-software (FSW)

ArduPilot Plane tailsitter set-up for K09-L: parameter file, output map, transition logic, failsafes, tuning and SITL
plans. Owner F4. No parts. Status `PROPOSED`, revision F4-R1, 2026-11-09. Not loaded on any board and not run in SITL
(SITL is not installed): every flight behaviour below is `UNVERIFIED`. Re-check: `python -I redesign/team/F4/fsw_check.py`.

| File | What |
|---|---|
| `K09L.param` | the parameter file (116 lines, each under a comment; load with Mission Planner or MAVProxy) |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal; the motor map |
| `SITL-PLAN.md` · `TUNING-PLAN.md` | 15 SITL cases incl. motor-failure injection · bench → stand → hover → FW → transition order |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Frame | `Q_TAILSIT_ENABLE` 1, `Q_FRAME_CLASS` 1, `Q_FRAME_TYPE` 1, `Q_TAILSIT_MOTMX` 15 | — | R-FSW-PARAMS | `PROPOSED` |
| `Q_OPTIONS` | 262 400 (bit 18 arm in VTOL only, bit 8 motors-only assist) | — | J1, guide-tailsitter | `PROPOSED` |
| Motor output cap, Q modes / FW incl. yaw differential | 0.84 / 0.8375 (≤ 0.849 for 9 350 rpm) | — | `CL-F4-SPIN-MAX`, `CL-F4-FW-ACT-MAX` | `UNVERIFIED` |
| Pack-current limiter, time constant | 100 / 1 | A / s | CR-E1-08, `CL-C1-T-CAP` | `UNVERIFIED` |
| Battery compensation | 16.8 / 13.2 | V | CR-E1-08 | `PROPOSED` |
| `AIRSPEED_MIN` / `CRUISE` / `MAX` | 15 / 16 / 18 | m/s | `CL-F4-ARSPD-MIN-FACTOR` 1.26 Vs, `CL-F4-CRUISE-TRANS` 1.03, `CL-F4-ARSPD-MAX-VA` | `UNVERIFIED` (D-21) |
| Pitch-over / pitch-up rate | 12 / 30 | °/s | CR-B1-12 (peak thrust 0.76 sagged) | `UNVERIFIED` |
| Plane controller takes over | 20° above horizon (`Q_TAILSIT_ANGLE` 70) | ° | CR-B4-06d | `PROPOSED` |
| Copter assist below | 13 m/s or 15 m height | m/s, m | CR-B1-12 | `PROPOSED` |
| Descent: auto, pilot, final | 1.2, 1.2, 0.5 (VRS onset 1.88) | m/s | `CL-F4-DESCENT` +36 % | `UNVERIFIED` |
| Body-rate limits, Q / FW | 120·120·90 / 150·100·100 (≤ 172) | °/s | `CL-F4-BODY-RATE` +13 % | `UNVERIFIED` |
| FW yaw: `RUDD_DT_GAIN`, needed | 35 / 31.8 | % | `CL-F4-RUDD-DT-REQ` +9 % | `UNVERIFIED` |
| Harmonic notch | ESC rpm, from 70 Hz, harmonics 1–3 | Hz | `CL-F4-NOTCH-LOW`, `-TOP` | `UNVERIFIED` |
| `BATT_LOW_MAH` → RTL / `BATT_CRT_MAH` → QLAND / `BATT_ARM_VOLT` | 2 700 / 1 300 / 16.4 | mAh, V | `CL-F4-BATT-LOW`, `-CRT` | `PROPOSED` |
| Geofence: ceiling, circle | 110 (≤ 121.9), 250 | m | `CL-F4-FENCE-ALT`, `-RADIUS` | `CHECKED` |

## Motor and output map

Hover copter frame (what ArduPilot mixes in): **forward = belly (−z), right = right wing (+y), down = tail (+x)**;
"seen from the nose" = looking aft along +x = from above in hover. Diagonals share a sense (UR + LL, UL + LR).

| FC out | Function | AP motor | Station | Copter position | Rotation seen from nose / from behind | Prop | Motor-test letter | Harness edge |
|---|---|---|---|---|---|---|---|---|
| 1 | 33 Motor1 | 1 | `LR` | front-right | CCW / CW | 11×5.5MR | A | `E-HRN-26` |
| 2 | 34 Motor2 | 2 | `UL` | back-left | CCW / CW | 11×5.5MR | C | `E-HRN-25` |
| 3 | 35 Motor3 | 3 | `LL` | front-left | CW / CCW | 11×5.5MRP | D | `E-HRN-27` |
| 4 | 36 Motor4 | 4 | `UR` | back-right | CW / CCW | 11×5.5MRP | B | `E-HRN-24` |
| 5 / 6 | 77 / 78 | — | elevon L / R | — | — | — | — | `E-HRN-28` / `-29` |

**Cant sense (D3, CR-B4-04).** Each motor tilts 3° about the radial line from the x-axis to the motor; the prop end
of every shaft leans **toward the wing plane (0.86) and outboard (0.51)**: unit (y, z) LR (+0.51, +0.86), UR (+0.51,
−0.86), LL (−0.51, +0.86), UL (−0.51, −0.86). The side force then turns the airframe with the prop's reaction
torque; net side force 0 (`CL-F4-CANT-NET-FORCE`). UR = LR mirrored in the wing plane, LL = LR mirrored in XZ.
FC ports 1–6 assume motors on DShot-capable timer groups with no servo; F3 confirms on the chosen board.

## Transition logic and limits

| Phase | Enter by | Controller | Ends when | Limits / abort |
|---|---|---|---|---|
| Hover | arm in QSTABILIZE/QHOVER/QLOITER | copter, throttle gain scaling | pilot selects FBWA/CRUISE/AUTO at ≥ 50 m | lean 30°, descent 1.2 m/s, weathervane belly into wind |
| Pitch-over | FBWA selected | copter, nose down 12 °/s | nose 20° above horizon (≈ 5.8 s) | `Q_TRANS_FAIL` 15 s → QRTL; any Q mode aborts |
| Assisted FW | angle reached | plane + motors-only copter assist | airspeed > 13 m/s and attitude error < 30° | TECS to 16 m/s; R-TRANSITION met when airspeed ≥ 15.5 |
| Cruise | — | plane; yaw by L/R differential thrust | pilot selects a Q mode, RTL ends at home | 15–18 m/s, bank 45°, pitch +20/−15°, throttle 10–75 % |
| Back-transition | Q mode or QRTL | plane pitch-up 30 °/s, throttle 55 % | nose at `Q_TAILSIT_ANGLE` | then copter hover, land at 0.5 m/s below 6 m |

No gain scheduling on airspeed during the pitch-over: `Q_TAILSIT_GSCMSK` 1 (throttle). FW gains scale on airspeed
only after hand-over, at ≤ 20° AoA (`SCALING_SPEED` 16).

## Failsafes

| Event | Trigger | In a Q mode | In FW | SITL |
|---|---|---|---|---|
| RC loss | no CRSF frames 1.5 s / 5 s | QLAND (`Q_OPTIONS` bit 5 off) | continue AUTO, else circle → RTL at 5 s | S7 |
| Battery low / critical | 2 700 / 1 300 mAh left, or 14.0 / 13.6 V sag-compensated | RTL → QRTL landing / QLAND | RTL (FW home, back-transition, land) / QLAND | S8 |
| Transition fail | 15 s | QRTL | — | S12 |
| Geofence | 110 m AGL or 250 m from home | RTL (build behaviour recorded) | RTL | S9 |
| GPS / EKF | EKF variance > 0.8 | QLAND without position hold; pilot takes QSTABILIZE | FBWA by pilot; no GPS failsafe in Plane | S10 |
| E-stop | RC9 switch | all motors off ≤ 1 s | same | S13 |
| Motor failure | — | not survivable in hover | throttle cut, FBWA glide, belly land (CR-E1-08) | S11 |

## Interfaces

| To | What | Edge |
|---|---|---|
| F3 avionics | board, bdshot firmware, timer groups, I²C airspeed address, `AHRS_ORIENTATION`, `BATT_VOLT_MULT`/`AMP_PERVLT` | `E-HRN-24…32` |
| F2 harness | `signal.fc_port` = FC out column above | `E-HRN-24…29` |
| E1 / D3 | rotation, prop type, cant sense per station | `E-PRP-05…08` |
| F5 | mode switch ch 5, arm ch 8, e-stop ch 9, CRSF failsafe = no frames | `E-HRN-31` |

## Open issues

| Issue | Owner |
|---|---|
| `Q_M_SPIN_MAX` 0.84 is below the documented 0.9–1.0 range; if the build clamps it, the cap moves to the ESC or a Lua limit | F4 (S1), H1 |
| `AIRSPEED_MIN` rests on A1's 11.86 m/s; B3's R0 trimmed stall 12.73 m/s gives 1.18 Vs (`FAIL`) | B3 (R1 re-run, D-21) |
| FW differential is symmetric about throttle; B3 asked one side raised (yaw ratio 1.38 vs 2) | B3, F4 |
| 50 parameter names still to match on the installed build; 3 LEGACY duplicates | F4 (S1) |

## How to verify

`python -I redesign/team/F4/fsw_check.py` (lint, mirror check, motor map, 19 claims) → SITL-PLAN.md S1–S15 →
TUNING-PLAN.md bench steps (props off) → stand rpm cap → tethered hover.
