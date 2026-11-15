# flight-software (FSW)

ArduPilot Plane tailsitter set-up for K09-L: parameter file, output map, transition logic, elevon schedule,
failsafes, tuning and SITL plans. Owner F4. No parts. Status `PROPOSED`, revision **F4-R11, 2026-11-14** (D-174: 80 A, LiHV 17.4 V, `THR_MAX` 41, `BATT_*` for the Shorty. R10 D-173: X2814 V3 + 11×8E, spin 0.81, 75 A, `THR_MAX` 42 + FWD_BAT; D-173b CoreWing, Lua withdrawn. R9: D-161b/c Lua spin cap on the Kakute H743-Wing, provisional; CR-F5-15/16; `BATT_LOW_MAH` 3 000. R8: CR-C1-40, B3 entry design, E2 / H2-4, D-161; R7 design round D-145 … D-157; R6 2026-11-13, CDR fix round, D-120 … D-126;
R5: D-65, D-66, D-71, D-62 CG). Firmware ArduPlane **4.7.2 stable or later** on the CoreWing F405 Wing V2 (D-33, no Lua; the board
entered ArduPilot in 4.7.2). Not loaded on any board. Loaded, read back and flown on the stock tailsitter model in SITL on 2026-11-13
(`team/F4/sitl/RESULTS.md`, logic only): flight behaviour on K09-L stays `UNVERIFIED`. Re-check: `python -I redesign/team/F4/fsw_check.py`.

**R11 in one table (D-174, `F4.md` D-174).** "Before" is R10.

| Item | Before | Now | Source |
|---|---|---|---|
| `Q_M_BAT_CURR_MAX` | 75 | **80 A** | A1 D-174 |
| Pack voltages (Gens Ace LiHV 4S 6000 HV Shorty) | LiPo 16.8 V full | `Q_M_BAT_VOLT_MAX` / `FWD_BAT_VOLT_MAX` **17.4**; `BATT_LOW_VOLT` / `CRT_VOLT` **14.4 / 14.0** (EST); `BATT_ARM_VOLT` **17.0** (EST) | D-174, E2 |
| `THR_MAX` | 42 | **41** (VH output 0.414 at 17.4 V, 2.70 kg; `CL-F4-VLEVEL-VH` 0.989) | F4 D-174 |
| `BATT_CAPACITY` / `BATT_LOW_MAH` / `BATT_CRT_MAH` | 5 980 / 3 200 / 1 300 | **5 520** placeholder / **3 000 / 1 200** | E2 D-173 Shorty |

**R10 in one table (D-173 / D-173b, `F4.md` D-173).** "Before" is R9.

| Item | Before | Now | Source |
|---|---|---|---|
| Motor / prop | X3108S KV900 + 11×5.5E/EP | **SunnySky X2814 V3 KV900 + APC 11×8E/EP** | A1 D-173, E1 D-173 |
| `Q_M_SPIN_MAX` | 0.746 + Lua schedule | **0.81 fixed** (one motor at full output, fresh pack: 49.3 A winding ≤ 50, 40.0 A ESC ≤ 45) | E1 D-173 |
| `Q_M_BAT_CURR_MAX` | 73.2 A | **75 A** | D-173 |
| Flight controller, scripting | Kakute H743-Wing + `k09l_spincap.lua` | **CoreWing F405 Wing V2**, no `SCR_*` lines; script archived (`archive/D-161c/`); CoreWing board lines restored (GPS SERIAL5, CRSF SERIAL6, 11.05 / 64, two IMUs) | D-173b |
| `Q_M_BAT_VOLT_MAX` / `MIN` | 0 / 13.2 | **16.8 / 13.2** (built-in compensation back on: nothing else scales for voltage with a fixed cap) | F4 D-173 |
| `THR_MAX` | 60 | **42** + **`FWD_BAT_VOLT_MAX` 16.8 / `_MIN` 13.2 / `FWD_BAT_IDX` 0**: 11×8E at 60 % would fly ≈ 30 m/s; 0.42 ≤ 0.429 for VH (`EST`); the compensation lifts the cap on a sagged pack (19.8 m/s ≥ 18, climb ≥ 3.0 m/s) | F4 D-173 (`CL-F4-VLEVEL-VH` 0.979) |
| Notch | inputs B4 5.5E rpm | E1 D-173.4: lowest steady 1P 81.7 Hz (≥ 1.1 × 70), highest 9 964 rpm (2P 332 Hz); `INS_HNTCH_*` unchanged | `CL-F4-NOTCH-LOW` 1.17, `-TOP` 0.66 |
| `BATT_LOW_MAH` | 3 000 | **3 200** (E2's live claim; 3 000 / CRT 1 200 if the Gens Ace Shorty is adopted) | E2 D-173 |

**R9 in one table (closure round 2026-11-14, `F4.md` D-161c).** "Before" is R8.

| Item | Before | Now | Source |
|---|---|---|---|
| Flight controller | CoreWing F405 Wing V2 (no Lua) | **Holybro Kakute H743-Wing, target `KakuteH7-Wing`** (Lua in the official 4.7.2 build), PROVISIONAL on A1 option C | F3 closure, A1 D-161b |
| `Q_M_SPIN_MAX` | 0.84 fixed | **saved 0.746; in flight `scripts/k09l_spincap.lua` sets min(0.93, 11.2 V / V_bus) at 10 Hz**; any fault → 0.746 and no arming | E1 D-161 spin cap §5; SITL D-161c |
| `Q_M_BAT_VOLT_MAX` | 16.8 (built-in compensation) | **0 (off)**: the schedule is itself a 1/V compensation; with both on the learnt hover drifted −14 % over the sweep, with it off +3.8 % | SITL D-161c |
| `SCR_ENABLE` / `SCR_HEAP_SIZE` / `SCR_USER1` / `SCR_LD_CHECKSUM` / `SCR_RUN_CHECKSUM` | — | 1 / 102 400 / 0 (test hook) / set at the board check | D-161c |
| Board lines | CoreWing: GPS SERIAL5, CRSF SERIAL6, `BATT_VOLT_MULT` 11.05, `BATT_AMP_PERVLT` 64, two IMU positions | Kakute: GPS **SERIAL3**, CRSF SERIAL6 with **`BRD_ALT_CONFIG` 1**, `SERIAL5_PROTOCOL` −1, **18.18 / 36.6**, **one IMU** at (0.087, −0.046, −0.0315) m FRD | F3 closure §5, Kakute hwdef |
| `FLTMODE1`–`6` | 17 / 18 / 19 / 5 / 7 / 11 | **17 / 5 / 7 / 18 / 11 / 19** (Q modes at 988 / 1 500 / 2 012 µs; FW slots only behind the radio latch) | CR-F5-15 |
| `RC3_MIN` / `MAX` / `TRIM` / `DZ`; `RC6/7/8/10/11/12_OPTION` | radio calibration | **988 / 2 012 / 988 / 30**; all 0 stated | CR-F5-15 |
| `BATT_LOW_MAH` | 3 100 | **3 000** | E2 closure (model correction) |

**R8 in one table (closure round 2026-11-14, `review/CLOSURE-ROUND-2026-11-14/F4.md`).** "Before" is R7.

| Item | Before | Now | Source |
|---|---|---|---|
| `PTCH2SRV_RMAX_UP` / `_DN` | 100 / 100 °/s | **35 / 20 °/s** (n at VD 3.12 ≤ 3.4, −1.21 ≥ −1.5) | CR-C1-40; `CL-F4-PTCH-RMAX-UP` / `-DN` |
| `THR_MAX` | 70 % | **60 %** (FW output pass-through, read from source: 0.60 ≤ 0.611 for VH 21.8 m/s on B4's in-flight model; 70 gives 24.9 m/s) | CR-B4-31 (B4 withdrew its rpm reason; F4 keeps 60 for the VH / VD basis); `CL-F4-VLEVEL-VH` 0.982 |
| `Q_ASSIST_ALT` / `Q_ASSIST_ANGLE` | 15 m / 30° (default) | **0 / 0** (only the speed trigger, 14 m/s, stays) | CR-C1-40 residual: the motors-only assist bypasses the 35 °/s clamp through the copter rate loop; `CL-F4-QASSIST-TRIGGERS` 0 |
| Forward-transition entry | QSTABILIZE, `throttle_in` ≥ 0.65 | **SC down from QSTABILIZE with the stick > 40 %: the radio holds CH3 at 1.285 θh for 0.9 s (FC hold 1.08–1.38 s; B3 pre-climb hold 1.0 s), then sends FBWA; the override releases ≥ 0.5 s after FBWA** (B3 closure, F5 CR-F5-16, `team/F5/TRANSITION-SWITCH.md`); `Q_A_ANGLE_BOOST` **0 (must be set: Quad frame class default is 1)**, `Q_TRANSITION_MS` 11 667, `Q_TAILSIT_ANG_VT` 0, `Q_THROTTLE_EXPO` 0.2, `Q_M_HOVER_LEARN` 2 stated | B3 §1.4; `CL-F4-ANGLE-BOOST`, `-TRANS-MS-RATE` |
| `BATT_LOW_MAH` / `BATT_FS_LOW_ACT` | 2 700 / 1 RTL | **3 100 / 6 Loiter-to-QLand** (from a Q mode straight to QLAND; RTL would pitch over outside 90 m / 50 m) | E2, H2-4, B3 §2; `CL-F4-BATT-LOW`, `CL-F4-FS-Q-PITCHOVER`; SITL S8 |
| `Q_M_BAT_CURR_MAX` | 70.2 A | **73.2 A** (D-161, 11×5.5E/EP props) | A1 D-161; `CL-F4-BAT-CURR-MAX` 73.2 ≤ 73.2 |
| `INS_HNTCH_HMNCS` | 7 (1P–3P) | **3 (1P, 2P)**: with the uncapped E props 3P reaches 514 Hz > 500 Hz Nyquist | `CL-F4-NOTCH-TOP` 0.69 |
| `Q_M_SPIN_MAX` | 0.84 | 0.84 held in R8 (no Lua on the CoreWing); R9: scheduled by script | — |

**R7 in one table (design round 2026-11-14, `review/DESIGN-ROUND-2026-11-14/A1.md`).** "Before" is R6.

| Item | Before | Now | Source |
|---|---|---|---|
| `Q_M_BAT_CURR_MAX` | 100 A | **70.2 A** (D-157; R8: 73.2, D-161); valid only after `T-F1-SENSOR-CAL` ±1.1 % at 70–75 A | D-148, D-157; `CL-F4-BAT-CURR-MAX` 70.2 ≤ 70.2 |
| `BATT_CAPACITY` / `BATT_LOW_MAH` | 6 500 / 2 600 | **5 980 placeholder** (0.92 × 6 500; set the lowest measured `T-E2-CAPACITY` of the packs flown) / **2 700** | D-154; `CL-F4-BATT-LOW` 2 700 ≥ `CL-E2-BATT-LOW-MAH-V17` 2 700 |
| `AIRSPEED_MIN` / `CRUISE` / `MAX` | 17 / 17 / 18 | unchanged; now equal to `performance.transition_min_ms` / `cruise_ms` 17 | D-145; `CL-F4-ARSPD-MIN-FLOOR` 17 ≥ 17 |
| `Q_ASSIST_SPEED` | 14 | unchanged (1.08 × tripped Vs 12.94; ArduPilot guidance `AIRSPEED_MIN` − 3) | B1 note, D-145 |
| Forward-transition entry | FBWA from QHOVER at hover throttle | **from QSTABILIZE at `throttle_in` ≥ 0.65 (1.4 W)**; no parameter exists for it (R8 replaces it with B3's switch design) | D-149, B3 §2.4 |
| `Q_WVANE_LAND` / `Q_WVANE_TAKEOFF` | 3 / 3 (wingtip into wind) | **1 / 1 (belly into wind; D-152 / D-156)**; `Q_WVANE_HGT_MIN` / `VELZ_MAX` / `SPD_MAX` 0 stated; SITL S21 | D-152, C5 |

**R6 in one table (CDR-07, -14, -15, -16, -26).** "Before" is R5.

| Item | Before | Now | Source |
|---|---|---|---|
| Parameter names matched to the firmware | 67 of 155 (88 waiting for SITL) | **158 of 158** in the published 4.7.1 list; 156 read back in SITL, 2 (`SERVO_BLH_BDMASK`, `_POLES`) board-only | `fsw_check.py` name check; `RESULTS.md` S1 |
| Names that were wrong for 4.7 | `FS_SHORT_TIMEOUT`; 6 LEGACY duplicates; the board's `Q_A_ACCEL_Y_MAX` | `RC_FS_TIMEOUT` 1.0; LEGACY lines deleted; `Q_A_ACC_Y_MAX` 135 deg/s/s | ArduPlane ReleaseNotes, tag `Plane-4.7.2` (PR 30350, 31441, 32192) |
| `MIXING_GAIN` → pure-pitch travel | 0.5 → 12.5° | **0.65 → 16.25°** (full pitch leaves 8.75° of roll) | B9, D-120 |
| `AIRSPEED_MIN` / `CRUISE` / `STALL` / `SCALING_SPEED` / `Q_ASSIST_SPEED` | 16 / 16 / 12 / 16 / 13 | **17 / 17 / 13 / 17 / 14** (tripped stall 12.85–12.94 m/s is the baseline; 17 holds to 13.07) | B6, D-122; `CL-F4-ARSPD-MIN-TRIP` +1 % |
| Yaw acceleration limit | firmware default | 135 deg/s/s = 2.36 rad/s², 85 % of 2.79 | D-123; `CL-F4-YAW-ACC-SET` 0.846 ≤ 0.85 |
| RC loss → QLAND in a Q mode | "1.5 s / 5 s" | **about 1.2 s** (`RC_FS_TIMEOUT` 1.0 + debounce); SITL 1.0–1.15 s. Receiver must be on "No Pulses" | D-124; `CL-F4-RC-FS-QLAND` 1.2 ≤ 3 s |
| `THR_MAX` | 70 | 70, with a 55 → 70 ladder on the first full-throttle legs (two models disagree: 21.3 vs 24.8 m/s) | D-125; TUNING-PLAN 6c |

| File | What |
|---|---|
| `K09L.param` | the parameter file (158 parameters, each under a comment; no LEGACY duplicates since R6) |
| `K09L-STAND.param` | thrust-stand overlay (CR-H1-04, CR-H1-18): limiter 25 A, fence off, log disarmed, raw-IMU batch log at sensor rate; load after `K09L.param` |
| `params.json` | the numbers claims read (`P:fsw.*`), mirrored from `K09L.param` and checked equal; the motor map |
| `SITL-PLAN.md` · `TUNING-PLAN.md` | 17 SITL cases incl. motor failure · bench → stand → hover → FW → transition order |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Frame | `Q_TAILSIT_ENABLE` 1, `Q_FRAME_CLASS` 1, `Q_FRAME_TYPE` 1, `Q_TAILSIT_MOTMX` 15 | — | R-FSW-PARAMS | `PROPOSED` |
| `Q_OPTIONS` | 262 400 (bit 18 arm in VTOL only, bit 8 motors-only assist) | — | J1, guide-tailsitter | `PROPOSED` |
| Motor output cap, Q / FW incl. yaw | 0.84 / 0.6875 (no rpm cap needed with the E props, `CL-B4-SPIN-MAX` 1.0, `CL-B4-FW-CAP-VD` 1.0) | — | `CL-F4-SPIN-MAX`, `-FW-ACT-MAX` | `UNVERIFIED` |
| FW throttle cap `THR_MAX` → output for VH → level speed on a 3.6 V/cell pack | 60 → 0.60 ≤ 0.611 (VH 21.8 = VD/1.25, B4 in-flight model) → 18.25 ≥ `AIRSPEED_MAX` 18 | %, —, m/s | `CL-F4-VLEVEL-VH` 0.982, `CL-F4-VLEVEL` +1 % | `UNVERIFIED` |
| Pack-current limiter, battery index, TC; per motor | 73.2 (D-161) / 0 / 1; 18.3 | A, —, s; A | `CL-F4-BAT-CURR-MAX` ≤ 73.2 (`performance.full_throttle_current_a`; `T-F1-SENSOR-CAL` first), `-MOTOR` ≤ 25 (CR-A2-14; verified by `T-H1-RESTRAINED-RUN`) | `PROPOSED` |
| `AIRSPEED_MIN` / `CRUISE` / `MAX` | **17 / 17 / 18** (B6: tripped stall is the baseline). Not frozen until `T-B2-STALL`; then ceil(1.3 × measured stall); 17 holds to a measured 13.07 m/s, the second fallback 18 / 18 / 20 to 13.85 | m/s | `CL-F4-ARSPD-MIN-TRIP` 17 ≥ 16.82 (+1 %), `-D71` ≥ 15.70, `-FLOOR` ≥ 15.6, `-MAX-CAP` ≤ 22 | `UNVERIFIED` (stall by test) |
| FW pitch limits / `TECS_SINK_MAX` | +20, −10 / 2.5 | °, m/s | `CL-F4-VDIVE-VA` 17.8 ≤ 20.5 | `UNVERIFIED` |
| Pitch-over / pitch-up rate | 12 (≤ 15 after the sag-0.76 stand run) / 30 | °/s | CR-B1-12 rev 3; C1 `CL-C1-N-REACH-VT` 2.82 at 30 | `UNVERIFIED` |
| FW pitch-rate caps up / down; roll | 35 / 20; 150 | °/s | `CL-F4-PTCH-RMAX-UP` ≤ 39.66, `-DN` ≤ 24.79 (C1), `-TURN` 23.4 needed | `PROPOSED` |
| Hover rate-loop crossover roll / pitch / yaw | 1.0 / 2.4 / 1.0 (ceilings 4.5 / 4.5 / 2.4 until T-C2-TAP-TEST, CR-B3-19) | Hz | `CL-F4-XOVER-*` (A3-R5 inertia) | `UNVERIFIED` |
| Gyro LPF / D-term LPF | 40 / 32 (≥ 2 × 14.9) | Hz | `CL-F4-FILT-SEP` 2.15 | `PROPOSED` |
| Harmonic notch | ESC rpm, from 70 Hz, harmonics 1–3, `INS_HNTCH_REF` 1 | Hz | `CL-F4-NOTCH-LOW`, `-TOP` | `UNVERIFIED` |
| Descent auto (ends at 6 m) / pilot full stick / final (below 6 m) | 1.2 / **1.0** / **0.3** (VRS onset 1.88; hard landing 1.2 at ≤ 10°, D-65; cartridges take ≤ 0.32 without set, CR-D5-21) | m/s | `CL-F4-DESCENT` ≤ 1.88, `CL-F4-TOUCHDOWN-SINK` 1.0 ≤ 1.2 (+17 %), `CL-F4-LAND-SPD` 0.3 ≤ 0.32 | `UNVERIFIED` |
| Elevon servo ends L / R (trim 1500, ±25° at the TE) | 1003–1976 rev / 1024–1997 (starting values; T-D6-THROW sets them) | µs | `CL-F4-ELEVON-PWM-ERR`, `-SPAN` 497 ≤ 500 (CR-D6-09) | `PROPOSED` |
| `MIXING_GAIN` → pure-pitch travel | 0.65 → 16.25 (trimmed CLmax needs 10.9 at the CG target; the forward CG limit 0.0393 m uses all of it) | —, ° | `CL-F4-MIX-PITCH` 0.67 | `UNVERIFIED` |
| `INS_POS1/2` / `GPS1_POS` (FRD from the D-62 CG x 0.0490, z 0.0185) | (0.059, 0.046, −0.0205) / (−0.026, 0, −0.1595) | m | `CL-F4-SENSOR-POS-ERR` 0 ≤ 2 mm (F3's points per CR-F3-20; F3 re-runs, CR-F4-19) | `UNVERIFIED` |
| Touchdown to motors stopped (RC9 cut) | 0.46 (≤ 0.5) | s | `CL-F4-TD-CUT` | `UNVERIFIED` |
| `BATT_CAPACITY` / `BATT_LOW_MAH` → RTL / `BATT_CRT_MAH` → QLAND | 5 980 placeholder (lowest measured `T-E2-CAPACITY`) / 3 100 / 1 300 (E2 closure, H2-4) | mAh | `CL-F4-BATT-LOW` ≥ `CL-E2-BATT-LOW-MAH-V17`, `-CRT` | `PROPOSED` |
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
| Hover | arm in QSTABILIZE/QHOVER/QLOITER | copter, throttle gain scaling | at 50 m (≤ 55): **SC down from QSTABILIZE with the stick > 40 %: the radio holds CH3 at 1.285 θh for 0.9 s (FC hold 1.08–1.38 s; B3 pre-climb hold 1.0 s), then sends FBWA; the override releases ≥ 0.5 s after FBWA** (B3 closure, F5 CR-F5-16, `team/F5/TRANSITION-SWITCH.md`); FBWA / CRUISE / RTL never by the plain mode switch from a Q mode (F5 latch) | lean 30°, descent 1.0 m/s pilot / 1.2 auto, belly into wind |
| Pitch-over | FBWA selected | copter, nose down 12 °/s; throttle frozen at max(hover, entry `throttle_in`), stick not read (`tailsitter.cpp` `ANGLE_WAIT_FW`, tag Plane-4.7.2, read 2026-11-14) | nose 20° above horizon (≈ 5.8 s) | `Q_TRANS_FAIL` 15 s → QRTL; any Q mode aborts |
| Assisted FW | angle reached | plane + motors-only assist (speed trigger only: `Q_ASSIST_SPEED` 14; ALT and ANGLE off) | airspeed > 14 m/s | TECS to 17 m/s |
| Cruise | — | plane; yaw damping by L/R differential | pilot selects a Q mode (heading into wind only, ±45° EST, C-13); RTL (`Q_RTL_MODE` 2, was 1: circle down to `Q_RTL_ALT` 50 m at `Q_FW_LND_APR_RAD` 60 m, `Q_TRANS_DECEL` 2.0, then into-wind back-transition and QRTL) | 17–18 m/s, bank 45°, pitch +20/−10° at ≤ 35 / 20 °/s, throttle 10–60 % |
| Back-transition | Q mode or QRTL | plane pitch-up 30 °/s, throttle 55 % | nose at `Q_TAILSIT_ANGLE` | copter hover; landing belly into the wind (never pod face), 0.3 m/s below 6 m. Pilot-flown back-transition only heading into wind (select QHOVER within ±45° of the wind, EST); RTL back-transitions into wind via `Q_RTL_MODE` 2; no downwind approach (C-13, G-01; CR-132423 p. 35, 38-39, 172; `review/NASA-CR-132423-COMPLIANCE.md`); SITL S18 |

## Elevon deflection schedule (D-29: full travel to VA 20.5 m/s, ≤ 1/3 at VD 27.2 m/s)

ArduPilot has no airspeed-dependent surface limit, and Lua (which could add one) is not on the F405. The schedule is
held by keeping the aircraft below VA in every fixed-wing mode:

| Barrier | Setting | Result | Claim |
|---|---|---|---|
| No raw-stick mode (D-50; R-SPIRAL, D-66) | `FLTMODE1-6` 17 / 18 / 19 / 5 / 7 / 11 (QSTAB, QHOVER, QLOITER, FBWA, CRUISE, RTL), boot 17; never MANUAL 0, STABILIZE 2, TRAINING 3, ACRO 4, QACRO 23; no RC aux switch selects one | every surface command passes the attitude limits and the roll loop holds the bank, so spiral t2 3.3–3.5 s is harmless | `CL-F4-NO-RAW-MODES` 0 |
| Dive | `PTCH_LIM_MIN_DEG` −10 | steady idle dive 17.8 m/s (20.1 at L/D 7.16); at −15° it would be 26 m/s | `CL-F4-VDIVE-VA` ≤ 20.5 |
| Level, full throttle | `THR_MAX` 60 | output 0.60 (pass-through, source-read) ≤ 0.611 that reaches 21.8 m/s (the VH that VD 27.2 assumes) on B4's in-flight model | `CL-F4-VLEVEL-VH` 0.982 |
| Autopilot speed | `AIRSPEED_MAX` 18 (≤ 22, the old `ARSPD_FBW_MAX`) | TECS never targets above 18 | `CL-F4-ARSPD-MAX-CAP` |
| Speed scaler | `SCALING_SPEED` 16 | demand per unit error × 0.78 at VA, × 0.59 at VD (not ≤ 1/3) | `CL-F4-SCALER-VD` (information) |

Above VA only after a loss of control; the ≤ 1/3 at VD is then not enforced (CR-F4-12 to A1/C1/B2).

## Failsafes

| Event | Trigger | In a Q mode | In FW | SITL |
|---|---|---|---|---|
| RC loss (ELRS/CRSF on SERIAL6; receiver failsafe mode **No Pulses**) | no valid frame for `RC_FS_TIMEOUT` 1.0 s (+ 0.2 s debounce) = short event; `FS_LONG_TIMEOUT` 5 s = long event | **QLAND at the short event, about 1.2 s** (`Q_OPTIONS` bit 5 off; SITL 1.0–1.15 s). It does not wait for the long timer, so `FS_LONG_TIMEOUT` stays 5 | continue AUTO, else circle → RTL at 5 s | S7 (Q part run) |
| GCS loss | — | off (`FS_GCS_ENABL` 0: telemetry rides the RC link) | off | — |
| Battery low / critical | 3 100 / 1 300 mAh left of `BATT_CAPACITY` (measured, D-154), or 14.0 / 13.6 V sag-compensated | low: **QLAND at once** (`BATT_FS_LOW_ACT` 6; no forward transition) / critical: QLAND | low: loiter down to `Q_RTL_ALT` 50 m, then QLAND there; pilot may select RTL (slot 6) for the into-wind approach / QLAND | S8 (run 2026-11-14) |
| Transition fail | 15 s | QRTL | — | S12 |
| Geofence | 110 m AGL (breach at `FENCE_ALT_MAX`; `FENCE_MARGIN` is a notice) or 250 m from home | RTL → forward transition at max(hover, `throttle_in`): no Q-mode fence action exists in Plane; bounded double fault (`CL-B3-TRANS-PITCH-USE-HOVERTHR` 0.848 ≤ 1.0) | RTL | S9 (run 2026-11-14) |
| GPS / EKF | EKF variance > 0.8 | QLAND without position hold; pilot takes QSTABILIZE | FBWA by pilot | S10 |
| E-stop | RC9 switch | all motors off ≤ 1 s | same | S13 |
| Motor failure | — | not survivable in hover | throttle cut, FBWA glide, belly land | S11 |

No mode or failsafe commands sustained full throttle (CR-E3-05): climb is rate-limited in Q modes, FW is capped at 60 %.

## Landing (CR-C5-05, CR-D5-09)

Weathervane turns the **belly (−z) into the wind** for landing (`Q_WVANE_LAND` 1, D-152; C5: 5.3 m/s lull limit, 5.7 at
±30° heading error, against 4.5 m/s with the pod face to the wind) and elsewhere (`Q_WVANE_ENABLE` 1); `Q_WVANE_TAKEOFF` 1 (D-156, was 3)
acts only in AUTO VTOL take-offs. Weathervaning runs only in QLOITER, QLAND, QRTL and AUTO, stops while the pilot gives yaw
input, and with `Q_WVANE_HGT_MIN` / `VELZ_MAX` / `SPD_MAX` 0 it runs down to the ground (AC_WeatherVane.cpp and quadplane.cpp,
tag Plane-4.7.1, read 2026-11-14). Flight-card rule (H3): **"land belly into the wind, never pod face to the wind"**; SITL S21.
Forward-transition entry (B3 closure, replaces D-149): **SC down from QSTABILIZE with the stick > 40 %: the radio holds CH3 at 1.285 θh for 0.9 s (FC hold 1.08–1.38 s; B3 pre-climb hold 1.0 s), then sends FBWA; the override releases ≥ 0.5 s after FBWA** (B3 closure, F5 CR-F5-16, `team/F5/TRANSITION-SWITCH.md`). ArduPilot has no forward-transition
throttle parameter (`Q_TAILSIT_THR_VT` is back-transition only); the firmware holds max(hover, entry `throttle_in`) to 70°
(source-read, SITL S4c confirms). D-128's 40 % differential applies to the 8 m/s hover gust only and is not a parameter. Final descent **0.3 m/s below 6 m** (`Q_LAND_FINAL_SPD`, `Q_LAND_FINAL_ALT`; CR-D5-21:
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
| `THR_MAX` 42 rests on F4's 11×8E level-speed estimate (0.429 for VH); B4 confirms with `props.py`. A LiHV pack (E2 D-173) needs `FWD_BAT_VOLT_MAX` 17.4 and `THR_MAX` 41 | B4, E2, A1, F4 |
| FW output path: **settled, pass-through** (tailsitter.cpp output() → output_motor_mask, tag Plane-4.7.2); SITL S4 confirms RCOU | F4 |
| `THR_MAX` 60 holds VD 27.2 (VH 21.8) on B4's model; B4 withdrew its rpm reason, so the VH basis alone sets it | A1, C1, B4 |
| `SERVO_BLH_BDMASK`, `SERVO_BLH_POLES` are in the 4.7.1 list but not in the SITL build: read back on the board | F3, F4 (`T-F3-FW-LOAD`) |
| `THR_MAX` 60: level speed confirmed by the TUNING-PLAN 6c ladder 50 → 55 → 60 (stop at > 21.0 m/s) | F4, B4, H2 |
| Landing heading is belly into the wind (`Q_WVANE_LAND` 1, D-152) until SITL S21 and B3's weathervane-stability check; `Q_WVANE_TAKEOFF` 1 (D-156, AUTO take-off only), same SITL S21 | F4, B3 |
| Forward transition: the held entry throttle is read from source; SITL S4c confirms (pass lines in SITL-PLAN) | F4, B3 |
| A geofence breach while hovering starts a forward transition (no Q-mode fence action in Plane) | B3, J6 (F4.md §4) |
| Elevon servo ends are starting values from D6's linkage and an assumed ±45° per 1000–2000 µs servo; span 497 of 500 µs | D6, H1 (T-D6-THROW) |
| Sensor offsets follow the D-62 CG (0.0490, 0, 0.0185) on F3's R4 points; F3's `CALC-F3-OFFSETS` still uses (0.0522, 0, 0) and the R3 GPS point; the D-62 bay move may move the mast | F3 (CR-F4-19) |
| `AIRSPEED_MIN` 17 is not frozen: set from `T-B2-STALL` (D-71); 16 only if A1 also moves `transition_min_ms` (D-145) | B2, H2, F4, A1 |

## How to verify

`python -I redesign/team/F4/fsw_check.py` (lint of both files, mirror check, RC-option mode check, motor map, 43 claims) → SITL-PLAN.md
S1–S17 → TUNING-PLAN.md bench steps (props off) → stand rpm cap → tethered hover.

## Firmware build check (CDR-07 b, read 2026-11-13)

Source: `https://firmware.ardupilot.org/Plane/stable/CoreWingF405WingV2/` (`firmware-version.txt` "4.7.2-FIRMWARE_VERSION_TYPE_OFFICIAL",
`git-version.txt` commit `fb773567`, `features.txt` 410 lines, `arduplane.apj` 869 022 bytes) and the board's `hwdef.dat` / `README.md` at
tag `Plane-4.7.2` (`libraries/AP_HAL_ChibiOS/hwdef/CoreWingF405WingV2/`). A leading `!` in `features.txt` means "not in this build".

| K09-L needs | In the 4.7.2 build? | Evidence |
|---|---|---|
| QuadPlane, tailsitter | **yes** | `HAL_QUADPLANE_ENABLED`; tailsitter has no separate switch (it is part of the QuadPlane code); `AP_MOTORS_FRAME_QUAD_ENABLED`; `QAUTOTUNE_ENABLED` |
| Bidirectional DShot on outputs 1–4 | **yes** | `hwdef.dat`: `PWM(1)` and `PWM(3)` carry `BIDIR`; README: "PWM outputs 1 to 4 additionally support bi-directional DShot". Groups: 1–2, 3–4, 5–7, 8–10, 11–12: the elevons on 5–6 are their own group, so PWM there does not clash with DShot on 1–4. No `features.txt` line exists for DShot or BLHeli (—) |
| ESC rpm telemetry and the rpm notch | **yes** | `AP_RPM_ESC_TELEM_ENABLED`, `AP_INERTIALSENSOR_HARMONICNOTCH_ENABLED`, `AP_RPM_HARMONICNOTCH_ENABLED`; `!HAL_GYROFFT_ENABLED` (FFT notch absent: not used) |
| Raw-IMU batch log | **yes** | `AP_INERTIALSENSOR_BATCHSAMPLER_ENABLED` |
| ELRS / CRSF receiver and telemetry | **yes** | `AP_RCPROTOCOL_CRSF_ENABLED`, `HAL_CRSF_TELEM_ENABLED`, `AP_RSSI_ENABLED`; `DEFAULT_SERIAL6_PROTOCOL SerialProtocol_RCIN` |
| Compass driver | **yes, both variants** | `AP_COMPASS_QMC5883L_ENABLED`, `AP_COMPASS_QMC5883P_ENABLED` (hwdef turns the P on); also IST8310, HMC5843, LIS3MDL, RM3100; `COMPASS_CAL_ENABLED` |
| Airspeed MS4525DO | **yes** | `AP_AIRSPEED_MS4525_ENABLED` (also MS5525, ASP5033, SDP3X, analog) |
| Geofence | **yes** | `AP_FENCE_ENABLED`; `!AC_POLYFENCE_CIRCLE_INT_SUPPORT_ENABLED`, `!AC_POLYFENCE_FENCE_POINT_PROTOCOL_SUPPORT` (the old fence-point protocol is out; upload the polygon as mission-type fence items, S9 checks) |
| EKF3, u-blox GPS, logging, OSD | **yes** | `HAL_NAVEKF3_AVAILABLE`, `AP_GPS_UBLOX_ENABLED`, `HAL_LOGGING_ENABLED`, `OSD_ENABLED` |
| Lua scripting | no (as assumed, D-33) | `!AP_SCRIPTING_ENABLED` |

Board support for the CoreWing F405 Wing V2 is listed under "Changes from 4.7.1" in `ArduPlane/ReleaseNotes.txt` (PR 33717): there is no
4.6 or 4.7.0 / 4.7.1 firmware for it. Nothing K09-L needs is missing, so the SpeedyBee fallback FC is not triggered by the feature list.
Still to do on the board (`T-F3-FW-LOAD`): flash, load `K09L.param`, read back all 158 names, spin with bdshot telemetry.
