# flight-software (FSW)

ArduPilot Plane tailsitter set-up for K09-L: parameter file, output map, transition logic, elevon schedule,
failsafes, tuning and SITL plans. Owner F4. No parts. Status `PROPOSED`, revision F4-R5, 2026-11-10 (D-65, D-66, D-71, D-62 CG). Firmware
ArduPlane 4.7.x stable on the CoreWing F405 Wing V2 (D-33, no Lua). Not loaded on any board and not run in SITL
(SITL is not installed): every flight behaviour below is `UNVERIFIED`. Re-check: `python -I redesign/team/F4/fsw_check.py`.

| File | What |
|---|---|
| `K09L.param` | the parameter file (161 lines incl. 6 LEGACY duplicates, each under a comment) |
| `K09L-STAND.param` | thrust-stand overlay (CR-H1-04, CR-H1-18): limiter 25 A, fence off, log disarmed, raw-IMU batch log at sensor rate; load after `K09L.param` |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal; the motor map |
| `SITL-PLAN.md` · `TUNING-PLAN.md` | 17 SITL cases incl. motor failure · bench → stand → hover → FW → transition order |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Frame | `Q_TAILSIT_ENABLE` 1, `Q_FRAME_CLASS` 1, `Q_FRAME_TYPE` 1, `Q_TAILSIT_MOTMX` 15 | — | R-FSW-PARAMS | `PROPOSED` |
| `Q_OPTIONS` | 262 400 (bit 18 arm in VTOL only, bit 8 motors-only assist) | — | J1, guide-tailsitter | `PROPOSED` |
| Motor output cap, Q / FW incl. yaw | 0.84 / 0.79 (≤ 0.849 for 9 350 rpm) | — | `CL-F4-SPIN-MAX`, `-FW-ACT-MAX` | `UNVERIFIED` |
| FW throttle cap `THR_MAX` → rpm → level speed | 70 → 7 750 (≤ 7 950) → 21.3 (≤ 21.8 = VD/1.25) | %, rpm, m/s | `CL-F4-FW-RPM-CAP`, `-VLEVEL-VH` 0.98 (CR-B1-17 b, CR-C1-20) | `UNVERIFIED` |
| Pack-current limiter, battery index, TC; per motor | 100 / 0 / 1; 25 | A, —, s; A | `CL-F4-BAT-CURR-MAX` ≤ 100, `-MOTOR` ≤ 25 (CR-A2-14; verified by `T-H1-RESTRAINED-RUN`) | `PROPOSED` |
| `AIRSPEED_MIN` / `CRUISE` / `MAX` | 16 / 16 / 18 (MIN is an integer: 15.6 → 16). D-71: not frozen until `T-B2-STALL`; then ceil(1.3 × measured stall); 16 holds to a measured 12.31 m/s | m/s | `CL-F4-ARSPD-MIN-D71` ≥ 15.59 (1.3 × 11.99 at the forward CG, +3 %), `-FLOOR` ≥ 15.6, `-MAX-CAP` ≤ 22 | `UNVERIFIED` (stall by test) |
| FW pitch limits / `TECS_SINK_MAX` | +20, −10 / 2.5 | °, m/s | `CL-F4-VDIVE-VA` 17.8 ≤ 20.5 | `UNVERIFIED` |
| Pitch-over / pitch-up rate | 12 (≤ 15 after the sag-0.76 stand run) / 30 | °/s | CR-B1-12 rev 3: peak thrust 0.70 at 12 °/s, sag 0.76 | `UNVERIFIED` |
| Hover rate-loop crossover roll / pitch / yaw | 1.0 / 2.4 / 1.0 (ceilings 4.5 / 4.5 / 2.4 until T-C2-TAP-TEST, CR-B3-19) | Hz | `CL-F4-XOVER-*` (A3-R5 inertia) | `UNVERIFIED` |
| Gyro LPF / D-term LPF | 40 / 32 (≥ 2 × 14.9) | Hz | `CL-F4-FILT-SEP` 2.15 | `PROPOSED` |
| Harmonic notch | ESC rpm, from 70 Hz, harmonics 1–3, `INS_HNTCH_REF` 1 | Hz | `CL-F4-NOTCH-LOW`, `-TOP` | `UNVERIFIED` |
| Descent auto (ends at 6 m) / pilot full stick / final (below 6 m) | 1.2 / **1.0** / **0.3** (VRS onset 1.88; hard landing 1.2 at ≤ 10°, D-65; cartridges take ≤ 0.32 without set, CR-D5-21) | m/s | `CL-F4-DESCENT` ≤ 1.88, `CL-F4-TOUCHDOWN-SINK` 1.0 ≤ 1.2 (+17 %), `CL-F4-LAND-SPD` 0.3 ≤ 0.32 | `UNVERIFIED` |
| Elevon servo ends L / R (trim 1500, ±25° at the TE) | 1003–1976 rev / 1024–1997 (starting values; T-D6-THROW sets them) | µs | `CL-F4-ELEVON-PWM-ERR`, `-SPAN` 497 ≤ 500 (CR-D6-09) | `PROPOSED` |
| `MIXING_GAIN` → pure-pitch travel | 0.5 → 12.5 (trimmed CLmax needs 11.0) | —, ° | `CL-F4-MIX-PITCH` 0.88 | `UNVERIFIED` |
| `INS_POS1/2` / `GPS1_POS` (FRD from the D-62 CG x 0.0490, z 0.0185) | (0.059, 0.046, −0.0205) / (−0.026, 0, −0.1595) | m | `CL-F4-SENSOR-POS-ERR` 0 ≤ 2 mm (F3's points per CR-F3-20; F3 re-runs, CR-F4-19) | `UNVERIFIED` |
| Touchdown to motors stopped (RC9 cut) | 0.46 (≤ 0.5) | s | `CL-F4-TD-CUT` | `UNVERIFIED` |
| `BATT_LOW_MAH` → RTL / `BATT_CRT_MAH` → QLAND | 2 600 / 1 300 (CR-E2-20) | mAh | `CL-F4-BATT-LOW`, `-CRT` | `PROPOSED` |
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
| 5 / 6 | 77 / 78 | — | elevon L (reversed) / R | — | — | — | — | — | `E-HRN-28` / `-29` |

**Cant sense at 7° (D-52, closed CR-F4-11).** For the side force to add to each motor's reaction torque the prop end
of every shaft leans **toward the wing plane (0.86) and outboard (0.51)**: UR thrust side component along (y, z) =
(+0.51, −0.86) = **−t** in D3's notation, `cant_sense_UR` −1 (D3 now publishes −1; `CL-F4-CANT-SENSE-D3` +1, agrees).
With the R3 sense the hover yaw arm would have been 0.020 − 0.045 = −0.025 m (yaw reversed). The spin map above is
unchanged (CR-B4-16a). Check by eye before first spin-up: look at UR from the nose; its prop end leans right and down;
then the hanging yaw test (TUNING-PLAN step 1b).

## Transition logic and limits

| Phase | Enter by | Controller | Ends when | Limits / abort |
|---|---|---|---|---|
| Hover | arm in QSTABILIZE/QHOVER/QLOITER | copter, throttle gain scaling | pilot selects FBWA/CRUISE at ≥ 50 m | lean 30°, descent 1.0 m/s pilot / 1.2 auto, belly into wind |
| Pitch-over | FBWA selected | copter, nose down 12 °/s | nose 20° above horizon (≈ 5.8 s) | `Q_TRANS_FAIL` 15 s → QRTL; any Q mode aborts |
| Assisted FW | angle reached | plane + motors-only assist | airspeed > 13 m/s, attitude error < 30° | TECS to 16 m/s |
| Cruise | — | plane; yaw damping by L/R differential | pilot selects a Q mode (heading into wind only, ±45° EST, C-13); RTL (`Q_RTL_MODE` 2, was 1: circle down to `Q_RTL_ALT` 50 m at `Q_FW_LND_APR_RAD` 60 m, `Q_TRANS_DECEL` 2.0, then into-wind back-transition and QRTL) | 16–18 m/s, bank 45°, pitch +20/−10°, throttle 10–70 % |
| Back-transition | Q mode or QRTL | plane pitch-up 30 °/s, throttle 55 % | nose at `Q_TAILSIT_ANGLE` | copter hover; landing wingtip into wind, 0.3 m/s below 6 m. Pilot-flown back-transition only heading into wind (select QHOVER within ±45° of the wind, EST); RTL back-transitions into wind via `Q_RTL_MODE` 2; no downwind approach (C-13, G-01; CR-132423 p. 35, 38-39, 172; `review/NASA-CR-132423-COMPLIANCE.md`); SITL S18 |

## Elevon deflection schedule (D-29: full travel to VA 20.5 m/s, ≤ 1/3 at VD 27.2 m/s)

ArduPilot has no airspeed-dependent surface limit, and Lua (which could add one) is not on the F405. The schedule is
held by keeping the aircraft below VA in every fixed-wing mode:

| Barrier | Setting | Result | Claim |
|---|---|---|---|
| No raw-stick mode (D-50; R-SPIRAL, D-66) | `FLTMODE1-6` 17 / 18 / 19 / 5 / 7 / 11 (QSTAB, QHOVER, QLOITER, FBWA, CRUISE, RTL), boot 17; never MANUAL 0, STABILIZE 2, TRAINING 3, ACRO 4, QACRO 23; no RC aux switch selects one | every surface command passes the attitude limits and the roll loop holds the bank, so spiral t2 3.3–3.5 s is harmless | `CL-F4-NO-RAW-MODES` 0 |
| Dive | `PTCH_LIM_MIN_DEG` −10 | steady idle dive 17.8 m/s (20.1 at L/D 7.16); at −15° it would be 26 m/s | `CL-F4-VDIVE-VA` ≤ 20.5 |
| Level, full throttle | `THR_MAX` 70 | output ≤ 0.704 either FW output path, 7 750 rpm, level ≤ 21.3 m/s ≤ 21.8 (the VH that VD 27.2 assumes) | `CL-F4-VLEVEL-VH`, `-FW-RPM-CAP` |
| Autopilot speed | `AIRSPEED_MAX` 18 (≤ 22, the old `ARSPD_FBW_MAX`) | TECS never targets above 18 | `CL-F4-ARSPD-MAX-CAP` |
| Speed scaler | `SCALING_SPEED` 16 | demand per unit error × 0.78 at VA, × 0.59 at VD (not ≤ 1/3) | `CL-F4-SCALER-VD` (information) |

Above VA only after a loss of control; the ≤ 1/3 at VD is then not enforced (CR-F4-12 to A1/C1/B2).

## Failsafes

| Event | Trigger | In a Q mode | In FW | SITL |
|---|---|---|---|---|
| RC loss (ELRS/CRSF on SERIAL6) | no frames 1.5 s / 5 s | QLAND (`Q_OPTIONS` bit 5 off) | continue AUTO, else circle → RTL at 5 s | S7 |
| GCS loss | — | off (`FS_GCS_ENABL` 0: telemetry rides the RC link) | off | — |
| Battery low / critical | 2 600 / 1 300 mAh left, or 14.0 / 13.6 V sag-compensated | RTL → VTOL landing / QLAND | same | S8 |
| Transition fail | 15 s | QRTL | — | S12 |
| Geofence | 110 m AGL or 250 m from home | RTL (build behaviour recorded) | RTL | S9 |
| GPS / EKF | EKF variance > 0.8 | QLAND without position hold; pilot takes QSTABILIZE | FBWA by pilot | S10 |
| E-stop | RC9 switch | all motors off ≤ 1 s | same | S13 |
| Motor failure | — | not survivable in hover | throttle cut, FBWA glide, belly land | S11 |

No mode or failsafe commands sustained full throttle (CR-E3-05): climb is rate-limited in Q modes, FW is capped at 70 %.

## Landing (CR-C5-05, CR-D5-09)

Weathervane turns a **wingtip into wind** for take-off and landing (`Q_WVANE_TAKEOFF`/`LAND` 3) and belly into wind
elsewhere (`Q_WVANE_ENABLE` 1). Final descent **0.3 m/s below 6 m** (`Q_LAND_FINAL_SPD`, `Q_LAND_FINAL_ALT`; CR-D5-21:
under 0.32 m/s the pre-crushed cartridges return the energy elastically, at 0.5 they set 1.28 mm per landing) with the
velocity controller holding thrust to contact; about 8 s longer than at 0.5. The parameter governs QLAND and the end
of RTL/QRTL only: a pilot landing in QHOVER/QLOITER descends at the stick rate (up to `Q_PILOT_SPD_DN` 1.0 m/s, R5;
D-65 designs the feet for 1.2 m/s at ≤ 10°, `CL-F4-TOUCHDOWN-SINK`), so the flight card asks for **QLAND for the last
6 m** or ≤ ¼ down stick (CR-F4-18 to H3). **QSTABILIZE has no climb-rate loop**: throttle is direct, so the sink at
contact is whatever the pilot flies; the card bars landing in QSTABILIZE except to recover (CR-F4-21).
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
| ≤ 1/3 at VD not enforceable in firmware; schedule held by envelope | A1, C1, B2 (CR-F4-12) |
| `Q_M_SPIN_MAX` 0.84 under the documented 0.9–1.0 range; ESC-side cap is the only fallback (no Lua) | F4 (S1), H1 |
| FW output path (pass-through vs thrust curve) not settled from source; caps use the higher | F4 (SITL S4) |
| `THR_MAX` 70 holds VD 27.2 only if A1 accepts the cap (CR-C1-20 option) | A1, C1 (CR-F4-15) |
| 88 names still to match on the 4.7.x tag; 6 LEGACY duplicates | F4 (S1) |
| Elevon servo ends are starting values from D6's linkage and an assumed ±45° per 1000–2000 µs servo; span 497 of 500 µs | D6, H1 (T-D6-THROW) |
| Sensor offsets follow the D-62 CG (0.0490, 0, 0.0185) on F3's R4 points; F3's `CALC-F3-OFFSETS` still uses (0.0522, 0, 0) and the R3 GPS point; the D-62 bay move may move the mast | F3 (CR-F4-19) |
| `AIRSPEED_MIN` 16 is not frozen: set from `T-B2-STALL` (D-71); a measured stall > 12.31 m/s raises it and `AIRSPEED_CRUISE` to 17 | B2, H2, F4 |

## How to verify

`python -I redesign/team/F4/fsw_check.py` (lint of both files, mirror check, RC-option mode check, motor map, 43 claims) → SITL-PLAN.md
S1–S17 → TUNING-PLAN.md bench steps (props off) → stand rpm cap → tethered hover.
