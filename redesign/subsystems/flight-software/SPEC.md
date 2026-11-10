# flight-software (FSW)

ArduPilot Plane tailsitter set-up for K09-L: parameter file, output map, transition logic, elevon schedule,
failsafes, tuning and SITL plans. Owner F4. No parts. Status `PROPOSED`, revision F4-R3, 2026-11-09. Firmware
ArduPlane 4.7.x stable on the CoreWing F405 Wing V2 (D-33, no Lua). Not loaded on any board and not run in SITL
(SITL is not installed): every flight behaviour below is `UNVERIFIED`. Re-check: `python -I redesign/team/F4/fsw_check.py`.

| File | What |
|---|---|
| `K09L.param` | the parameter file (149 lines incl. 6 LEGACY duplicates, each under a comment) |
| `K09L-STAND.param` | thrust-stand overlay (CR-H1-04): limiter 25 A, fence off, log disarmed; load after `K09L.param` |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal; the motor map |
| `SITL-PLAN.md` · `TUNING-PLAN.md` | 17 SITL cases incl. motor failure · bench → stand → hover → FW → transition order |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Frame | `Q_TAILSIT_ENABLE` 1, `Q_FRAME_CLASS` 1, `Q_FRAME_TYPE` 1, `Q_TAILSIT_MOTMX` 15 | — | R-FSW-PARAMS | `PROPOSED` |
| `Q_OPTIONS` | 262 400 (bit 18 arm in VTOL only, bit 8 motors-only assist) | — | J1, guide-tailsitter | `PROPOSED` |
| Motor output cap, Q / FW incl. yaw | 0.84 / 0.8375 (≤ 0.849 for 9 350 rpm) | — | `CL-F4-SPIN-MAX`, `-FW-ACT-MAX` | `UNVERIFIED` |
| Pack-current limiter, battery index, TC | 100 / 0 / 1 | A, —, s | `CL-F4-BAT-CURR-MAX` (CR-A2-14) | `PROPOSED` |
| `AIRSPEED_MIN` / `CRUISE` / `MAX` | 16 / 16 / 18 (MIN is an integer: 15.6 → 16) | m/s | `CL-F4-ARSPD-MIN-FLOOR` ≥ 15.6, `-MAX-CAP` ≤ 22 | `UNVERIFIED` (upstream stall) |
| FW pitch limits / `TECS_SINK_MAX` | +20, −10 / 2.5 | °, m/s | `CL-F4-VDIVE-VA` 17.8 ≤ 20.5 | `UNVERIFIED` |
| Pitch-over / pitch-up rate | 12 / 30 | °/s | CR-B1-12; B1 re-check at sag 0.76 pending | `UNVERIFIED` |
| Hover rate-loop crossover roll / pitch / yaw | 1.1 / 2.6 / 1.0 (ceiling 5) | Hz | `CL-F4-XOVER-*` | `UNVERIFIED` |
| Gyro LPF / D-term LPF | 40 / 32 (≥ 2 × 14.9) | Hz | `CL-F4-FILT-SEP` 2.15 | `PROPOSED` |
| Harmonic notch | ESC rpm, from 70 Hz, harmonics 1–3, `INS_HNTCH_REF` 1 | Hz | `CL-F4-NOTCH-LOW`, `-TOP` | `UNVERIFIED` |
| Descent auto / pilot / final | 1.2 / 1.2 / 0.5 (VRS onset 1.88) | m/s | `CL-F4-DESCENT` | `UNVERIFIED` |
| Touchdown to motors stopped (RC9 cut) | 0.46 (≤ 0.5) | s | `CL-F4-TD-CUT` | `UNVERIFIED` |
| `BATT_LOW_MAH` → RTL / `BATT_CRT_MAH` → QLAND | 2 700 / 1 300 | mAh | `CL-F4-BATT-LOW`, `-CRT` | `PROPOSED` |
| Geofence ceiling, circle | 110 (≤ 121.9), 250 | m | `CL-F4-FENCE-*` | `CHECKED` |

## Motor and output map

Hover copter frame: **forward = belly (−z), right = right wing (+y), down = tail (+x)**; "seen from the nose" =
from the prop side = from above in hover. Diagonals share a sense (UR + LL CW, UL + LR CCW).

| FC out | Function | AP motor | Station | Copter position | Rotation from nose | Prop | Adapter thread | Test letter | Harness |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 33 | 1 | `LR` | front-right | CCW | 11×5.5MR | RH | A | `E-HRN-26` |
| 2 | 34 | 2 | `UL` | back-left | CCW | 11×5.5MR | RH | C | `E-HRN-25` |
| 3 | 35 | 3 | `LL` | front-left | CW | 11×5.5MRP | **LH** | D | `E-HRN-27` |
| 4 | 36 | 4 | `UR` | back-right | CW | 11×5.5MRP | **LH** | B | `E-HRN-24` |
| 5 / 6 | 77 / 78 | — | elevon L / R | — | — | — | — | — | `E-HRN-28` / `-29` |

**Cant sense at 7° (CR-D3-07): D3's prints are reversed.** For the side force to add to each motor's reaction torque
the prop end of every shaft must lean **toward the wing plane (0.86) and outboard (0.51)**: UR thrust side component
along (y, z) = (+0.51, −0.86) = **−t** in D3's notation. D3's print A gives UR +t (`cant_sense_UR` +1). With it, the
cant moment opposes the prop torque: hover yaw arm 0.020 − 0.045 = −0.025 m, so **hover yaw would be reversed on
first spin-up**. Fix: UR and LL take print B, UL and LR print A, or `cant_sense_UR` −1 (CR-F4-11; `CL-F4-CANT-SENSE-D3`
`FAILS` until then). Check by eye before first spin-up: look at UR from the nose; its prop end leans right and down.

## Transition logic and limits

| Phase | Enter by | Controller | Ends when | Limits / abort |
|---|---|---|---|---|
| Hover | arm in QSTABILIZE/QHOVER/QLOITER | copter, throttle gain scaling | pilot selects FBWA/CRUISE at ≥ 50 m | lean 30°, descent 1.2 m/s, belly into wind |
| Pitch-over | FBWA selected | copter, nose down 12 °/s | nose 20° above horizon (≈ 5.8 s) | `Q_TRANS_FAIL` 15 s → QRTL; any Q mode aborts |
| Assisted FW | angle reached | plane + motors-only assist | airspeed > 13 m/s, attitude error < 30° | TECS to 16 m/s |
| Cruise | — | plane; yaw damping by L/R differential | pilot selects a Q mode; RTL ends at home | 16–18 m/s, bank 45°, pitch +20/−10°, throttle 10–75 % |
| Back-transition | Q mode or QRTL | plane pitch-up 30 °/s, throttle 55 % | nose at `Q_TAILSIT_ANGLE` | copter hover; landing wingtip into wind, 0.5 m/s |

## Elevon deflection schedule (D-29: full travel to VA 20.5 m/s, ≤ 1/3 at VD 27.2 m/s)

ArduPilot has no airspeed-dependent surface limit, and Lua (which could add one) is not on the F405. The schedule is
held by keeping the aircraft below VA in every fixed-wing mode:

| Barrier | Setting | Result | Claim |
|---|---|---|---|
| No raw-stick FW mode | modes: QSTAB, QHOVER, QLOITER, FBWA, CRUISE, RTL; no MANUAL/ACRO/STABILIZE | every FW surface command passes the attitude limits | — |
| Dive | `PTCH_LIM_MIN_DEG` −10 | steady idle dive 17.8 m/s (20.1 at L/D 7.16); at −15° it would be 26 m/s | `CL-F4-VDIVE-VA` ≤ 20.5 |
| Level, full throttle | `THR_MAX` 75 | ≤ 0.89 VH | `CL-F4-VLEVEL-VH` |
| Autopilot speed | `AIRSPEED_MAX` 18 (≤ 22, the old `ARSPD_FBW_MAX`) | TECS never targets above 18 | `CL-F4-ARSPD-MAX-CAP` |
| Speed scaler | `SCALING_SPEED` 16 | demand per unit error × 0.78 at VA, × 0.59 at VD (not ≤ 1/3) | `CL-F4-SCALER-VD` (information) |

Above VA only after a loss of control; the ≤ 1/3 at VD is then not enforced (CR-F4-12 to A1/C1/B2).

## Failsafes

| Event | Trigger | In a Q mode | In FW | SITL |
|---|---|---|---|---|
| RC loss (ELRS/CRSF on SERIAL6) | no frames 1.5 s / 5 s | QLAND (`Q_OPTIONS` bit 5 off) | continue AUTO, else circle → RTL at 5 s | S7 |
| GCS loss | — | off (`FS_GCS_ENABL` 0: telemetry rides the RC link) | off | — |
| Battery low / critical | 2 700 / 1 300 mAh left, or 14.0 / 13.6 V sag-compensated | RTL → VTOL landing / QLAND | same | S8 |
| Transition fail | 15 s | QRTL | — | S12 |
| Geofence | 110 m AGL or 250 m from home | RTL (build behaviour recorded) | RTL | S9 |
| GPS / EKF | EKF variance > 0.8 | QLAND without position hold; pilot takes QSTABILIZE | FBWA by pilot | S10 |
| E-stop | RC9 switch | all motors off ≤ 1 s | same | S13 |
| Motor failure | — | not survivable in hover | throttle cut, FBWA glide, belly land | S11 |

No mode or failsafe commands sustained full throttle (CR-E3-05): climb is rate-limited in Q modes, FW is capped at 75 %.

## Landing (CR-C5-05, CR-D5-09)

Weathervane turns a **wingtip into wind** for take-off and landing (`Q_WVANE_TAKEOFF`/`LAND` 3) and belly into wind
elsewhere (`Q_WVANE_ENABLE` 1). Final descent 0.5 m/s with the velocity controller holding thrust to contact.
ArduPilot's land detector disarms only after the motors sit at their lower limit for ≥ 5 s (4 s + 1 s, quadplane.cpp),
so it cannot meet 0.5 s: **the pilot flips the RC9 cut at contact** (0.25 s reaction + 0.059 s link + 0.15 s spin-down
= 0.46 s, `CL-F4-TD-CUT`); the land detector is the backup. Flight-card line: CR-F4-14.

## Interfaces

| To | What | Edge |
|---|---|---|
| F3 avionics | outputs 1–4 bdshot, 5–6 PWM; MS4525DO 0x28; `AHRS_ORIENTATION` 0; sensor offsets; battery scaling | `E-HRN-24…32` |
| F2 harness | `signal.fc_port` = FC out column above | `E-HRN-24…29` |
| E1 / D3 | rotation, prop, adapter thread, cant print per station | `E-PRP-05…08` |
| F5 | arm ch 5, modes ch 6, e-stop/touchdown cut ch 9, CRSF on SERIAL6, RSSI from CRSF | `E-HRN-31` |

## Open issues

| Issue | Owner |
|---|---|
| D3 cant prints reversed (`CL-F4-CANT-SENSE-D3` `FAILS`) | D3 (CR-F4-11) |
| ≤ 1/3 at VD not enforceable in firmware; schedule held by envelope | A1, C1, B2 (CR-F4-12) |
| `Q_M_SPIN_MAX` 0.84 under the documented 0.9–1.0 range; ESC-side cap is the only fallback (no Lua) | F4 (S1), H1 |
| `Q_TAILSIT_RAT_FW` 12 rests on B1's sag-0.72 check; B1 re-checks at 0.76 | B1 |
| 76 names still to match on the 4.7.x tag; 6 LEGACY duplicates | F4 (S1) |

## How to verify

`python -I redesign/team/F4/fsw_check.py` (lint of both files, mirror check, motor map, 30 claims) → SITL-PLAN.md
S1–S17 → TUNING-PLAN.md bench steps (props off) → stand rpm cap → tethered hover.
