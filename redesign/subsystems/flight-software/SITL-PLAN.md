# flight-software — SITL plan

Revision F4-R4c, 2026-11-10. Status `UNVERIFIED`: ArduPilot SITL is not installed on the design machine; nothing below has run. Owner F4; the
pilot's ≥ 10 h (`R-PILOT`, `P:requirements.sitl_hours_min`) run on the same set-up after S1–S13 pass.

## Set-up

| Item | Value | Status |
|---|---|---|
| Build | ArduPlane 4.7.x stable, the tag flashed on the CoreWing F405 Wing V2 (D-33) | — |
| Stage A model | `sim_vehicle.py -v ArduPlane -f quadplane-copter_tailsitter --add-param-file=K09L.param` | frame name `UNVERIFIED` (check `Tools/autotest/pysim/vehicleinfo.py`) |
| Stage A use | logic only: modes, failsafes, output map, transition sequence. Not for gains or margins | — |
| Stage B model | JSON SITL backend (`-f JSON`) driven by a Python model from B3's aero table (`team/B3/results/sc_results.json`, CR-B3-04e), E1 thrust/torque per output, 7° cant in the sense of SPEC.md, 2.6 kg, inertia from A3, one torsion mode 11.7–14.9 Hz (C2) | to write after install |
| Wind | `SIM_WIND_SPD` 0 / 5 / 8 m/s, `SIM_WIND_TURB` 1 | — |
| Sagged pack | battery model loaded to thrust factor 0.76 (D-35) | parameter names to confirm |
| Logs kept | `.bin` + one line per case in `team/F4/sitl/RESULTS.md` (case, build, pass/fail, numbers) | — |

## Cases

| # | Case | How | Pass |
|---|---|---|---|
| S1 | Name check | load `K09L.param`, then `K09L-STAND.param`; `param show` each name; Mission Planner compare | only LEGACY names unknown (6 at most); `Q_M_SPIN_MAX` 0.84, `AIRSPEED_MIN` 16, `THR_MAX` 70, `Q_LAND_FINAL_SPD` 0.3, `SERVO5/6_MIN/MAX` read back; pre-arm clean; move the 88 unmatched names into `CHECKED_NAMES` |
| S2 | Output map | QuadPlane motor test A–D, `SERVO1–6_FUNCTION`; tilt the model in QSTABILIZE | A=LR, B=UR, C=UL, D=LL; belly-forward tilt speeds up the upper pair |
| S3 | Hover | QLOITER 2 min at 0 / 5 / 8 m/s wind | position ±1 m at 5 m/s; lean ≤ 20°; no motor at 0.84 for > 1 s |
| S4 | Pitch-over, FW output path | FBWA at 50 m, `Q_TAILSIT_RAT_FW` 12 / 16, fresh and sagged pack (CR-B1-12 rev 3); then FBWA full throttle with full rudder | altitude loss ≤ 10 m; peak motor output < 0.84 at 12 °/s sagged (B1: 0.70 × cap); airspeed ≥ 15.5 m/s within 15 s; RCOU at `THR_MAX` 70 = 0.70 (pass-through) or 0.704 (thrust curve): record which, update `ASM-F4-FW-PASSTHRU`; ≤ 0.79 with full rudder |
| S5 | Back-transition | QHOVER from 16 m/s, `Q_TAILSIT_RAT_VT` 20 / 30 / 50, `Q_TAILSIT_THR_VT` 49 / 55 | no tumble; height loss ≤ 10 m; nose-up moment held (B3 ≤ 1.0 N·m, stage B) |
| S6 | FW yaw | FBWA rudder doublet, `RUDD_DT_GAIN` 0 / 20 / 35 | yaw rate damped in < 2 cycles at 35 (stage B with Cn_β from B3) |
| S7 | RC loss | `SIM_RC_FAIL` 1 in QLOITER, pitch-over, cruise, back-transition | QLAND / continue / RTL at 5 s, as SPEC.md; nothing else |
| S8 | Battery | start at 3 000 mAh used; then 5 300 | low → RTL → back-transition at home → land; critical → QLAND; low while hovering < 50 m: record what RTL does (if it pitches over, `BATT_FS_LOW_ACT` → 6 Loiter-to-QLand) |
| S9 | Geofence | climb past 110 m; fly past 250 m, in FW and in QLOITER | breach action fires within 2 s; recorded Q-mode behaviour |
| S10 | GPS / EKF | `SIM_GPS1_ENABLE` 0 (or `SIM_GPS_DISABLE` 1) in QLOITER and in cruise | QLAND in Q mode; pilot recovers in QSTABILIZE; FBWA flyable in cruise |
| S11 | **Motor failure** | `SIM_ENGINE_FAIL` = bit of one motor, `SIM_ENGINE_MUL` 0; each motor; in hover at 30 m, mid pitch-over, cruise at 16 m/s | cruise: procedure (throttle cut, FBWA glide, belly land) keeps wings level, sink rate logged; hover / pitch-over: record time to loss of control (expected fatal, CONFIGURATION.md) |
| S12 | Transition fail | `SIM_ARSPD_FAIL` or a 20 m/s headwind so 13 m/s is not reached | QRTL at 15 s |
| S13 | E-stop | RC9 high from each mode, and at touchdown in QLAND/QHOVER | motor outputs at minimum ≤ 1 s (`R-ARM-KILL`); at touchdown RCOU to minimum in the same loop |
| S14 | Airspeed failure in cruise | `SIM_ARSPD_FAIL` 1 | synthetic airspeed, no stall, RTL possible |
| S15 | Pilot hours | QSTABILIZE recovery from a failed transition, landings in 5 m/s | 10 h logged with this file (`R-PILOT`) |
| S16 | Dive and level speed | FBWA full-down stick, idle and full throttle, 30 s; FBWB full throttle (stage B, prop model from B4) | dive airspeed ≤ 20.5 m/s (`CL-F4-VDIVE-VA`); level ≤ 21.8 m/s at ≤ 7 950 rpm (`CL-F4-VLEVEL-VH`, `-FW-RPM-CAP`) |
| S17 | Landing heading, descent, single-motor burst | QLAND from 20 m in 5 m/s crosswind; motor test one output at full for 2 s | lands wingtip into wind (`Q_WVANE_LAND` 3); descent ≤ 0.3 m/s below 6 m (`CL-F4-LAND-SPD`); one output at full ≤ 2 s, none in any mode (CR-F1-10) |

`SIM_ENGINE_FAIL` ("Engine Fail Mask") and `SIM_ENGINE_MUL` ("Engine failure thrust scaler") are in the current
Plane parameter list (checked 2026-11-09); which motor index each bit maps to is confirmed in S11 before the runs.
