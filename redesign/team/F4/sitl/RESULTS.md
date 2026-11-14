# F4 SITL results

Owner F4. First entries 2026-11-13 (CDR fix round, stream S3, CDR-07). One line per case. Status of everything here:
**stage A, logic only**. The simulated airframe is ArduPilot's stock `quadplane-copter_tailsitter` model, not K09-L:
it is far over-powered and has its own aerodynamics, so no gain, margin, height or time below is a K09-L number.
Stage B (JSON backend with B3's aero table) is not written.

## Set-up used

| Item | Value | Source |
|---|---|---|
| Machine | Windows 11, no WSL (`wsl --status`: not installed) | this session |
| SITL binary | `ArduPlane.elf` + ten `cyg*.dll`, ArduPilot's Cygwin build for Mission Planner, folder `PlaneStable` | https://firmware.ardupilot.org/Tools/MissionPlanner/sitl/PlaneStable/ (read 2026-11-13) |
| Build | `git.txt`: commit `bf693f31`, "Plane: version to 4.7.3-beta1" (the folder is named `PlaneStable`; flight stable is 4.7.2). `ArduPlane.elf` sha256 `de67d448…935aacc`, 10 978 634 bytes | same folder, `git.txt` |
| Model and defaults | `--model quadplane-copter_tailsitter --defaults quadplane.parm,quadplane-copter_tailsitter.parm` (both from tag `Plane-4.7.2`, `Tools/autotest/default_params/`) | `Tools/autotest/pysim/vehicleinfo.py`, tag `Plane-4.7.2` |
| Driver | pymavlink 2.4.50 in a virtual environment, TCP 5760, RC by `RC_CHANNELS_OVERRIDE`, speed-up 4–5 | scripts kept outside the repo (scratch); steps in `SITL-PLAN.md` "Install" |
| Parameter file | `subsystems/flight-software/K09L.param` (R5 for S1 run 1, R6 values re-checked by `fsw_check.py`), then `K09L-STAND.param` names | — |

SIM-only overrides (needed because the stock model is wired and sized differently; none goes into `K09L.param`):

| Override | Why |
|---|---|
| `SIM_BATT_VOLTAGE` 16.8, `BATT_VOLT_MULT` 10.1, `BATT_AMP_PERVLT` 17 | the simulated analog pins use SITL's scaling; with K09-L's 11.05 / 64 the pack reads 18.4 V and drains 3.8 × too fast |
| `ARSPD_TYPE` 2 | SITL has no MS4525 on I2C bus 0 ("MS4525[0]: no sensor found"); analog sensor used |
| `SIM_RC_FAIL` 1 | no RC pulses under the MAVLink overrides, so stopping the overrides is a link loss |
| Flight runs only: `SERVO1–8_FUNCTION` 4 / 19 / 70 / 21 / 33 / 34 / 35 / 36, `Q_FRAME_TYPE` 0, `SERVO5/6_MIN/MAX` 1000 / 2000, `SERVO5_REVERSED` 0, `Q_M_PWM_TYPE` 0 | the stock model reads motors on outputs 5–8 in a plus frame and surfaces on 1, 2, 4. With K09-L's map (motors 1–4, X frame, elevons 5–6) the model cannot leave the ground ("SIM Hit ground" repeatedly) |
| Back-transition sweep only: `FENCE_ALT_MAX` 900, `FENCE_RADIUS` 5000 | the stock model climbs 77 m in the pitch-over and breaches the 110 m fence |

## Cases

| # | Case | Result | Pass? |
|---|---|---|---|
| S1 | Name check, load and read back after a reboot | Build has 1 580 parameters before `Q_`/`BATT`/`INS_HNTCH` groups open, 1 614 after. R5 file (163 names): 154 accepted and read back equal after two reboots; **9 unknown**: `FS_SHORT_TIMEOUT` (removed in 4.7), `Q_WP_SPEED_DN`, `Q_PILOT_SPEED_DN`, `Q_LAND_SPEED`, `GPS_POS1_X/Y/Z` (the six LEGACY lines), `SERVO_BLH_BDMASK`, `SERVO_BLH_POLES` (not in the SITL build). R6 file (158 names) removes the first seven: **156 accepted, 2 board-only**. `Q_A_ACC_Y_MAX` exists (stock value 122.87 deg/s/s), `Q_A_ACCEL_Y_MAX` does not; `RC_FS_TIMEOUT` exists (1.0), `Q_P_NE_VEL_P` / `Q_P_NE_POS_P` exist (0.7 / 0.5), `Q_P_VELXY_P` / `Q_P_POSXY_P` do not. `Q_M_SPIN_MAX` 0.84 is kept (documented range 0.9–1.0, not clamped). `AIRSPEED_MIN`, `THR_MAX` 70, `Q_LAND_FINAL_SPD` 0.3, `Q_PILOT_SPD_DN` 1.0, `SERVO5/6_MIN/MAX`, `Q_RTL_MODE` 2, `Q_FW_LND_APR_RAD` 60, `Q_TRANS_DECEL` 2.0 read back. All five `K09L-STAND.param` names known. Boot mode 17 (QSTABILIZE). `SIM_ENGINE_FAIL`, `SIM_ENGINE_MUL`, `SIM_RC_FAIL`, `SIM_WIND_SPD`, `SIM_WIND_TURB`, `SIM_ARSPD_FAIL`, `SIM_GPS1_ENABLE` exist; `SIM_GPS_DISABLE` does not. Pre-arm: only the SIM items above (battery below `BATT_ARM_VOLT` until `SIM_BATT_VOLTAGE` is raised; airspeed needs calibration) | **pass**, with 2 names left for the board (`T-F3-FW-LOAD`) |
| S1b | Mode switch, K09-L values | channel 6 at 1100 / 1295 / 1425 / 1555 / 1685 / 1900 µs → modes 17 / 18 / 19 / 5 / 7 / 11 (QSTABILIZE, QHOVER, QLOITER, FBWA, CRUISE, RTL) | pass |
| S1c | Arming | RC5 high (`RC5_OPTION` 153) arms in QHOVER with throttle low; `RC9` low reports "MotorEStop LOW" at boot | pass |
| S2 | Output map, **K09-L's own map and X frame**, disarmed motor test at 40 % | A → output 1 (LR), B → output 4 (UR), C → output 2 (UL), D → output 3 (LL); test order 1, 4, 2, 3 as `SPEC.md` | **pass** |
| S2b | Hover, stock airframe with K09-L's rate gains and limits | climb to 50 m in 30.3 s at 2.2 m/s (stick 85 %); QHOVER 20 s: height 51.48–51.81 m band ≤ 0.06 m, lean ≤ 0.1°; stick steps give +19° pitch, +22° roll, +27° yaw in 1 s, each on its own axis | pass (logic). "Belly-forward tilt speeds up the upper pair" **not checked**: the stock model is a plus frame, so the pairing differs; bench step 1 checks it |
| S4a | Forward transition, FBWA at 35–50 % stick, 12 °/s | "Transition FW done" 5.8 s after FBWA; 13 m/s at 4.6–5.0 s; CRUISE holds 16.9 m/s (set 16 at the time). The stock model **climbs 77–98 m** in the pitch-over | logic pass; height not a K09-L number |
| S5a | Back-transition from CRUISE at 17 m/s to QHOVER, `Q_TAILSIT_THR_VT` 55, stock airframe | `Q_TAILSIT_RAT_VT` 50 / 30 / 20 °/s: height gain **63.7 / 92.6 / 124.9 m**, groundspeed < 2 m/s after 3.6 / 3.9 / 5.4 s, motors at their lowest output for ≤ 0.3 / 0.5 / 0.7 s, no tumble | **not a pass / fail for K09-L** (stock model). Transferable: the slower the pitch-up, the larger the balloon (the wing stays lifting longer). CDR-AE-03's ≤ 15 m line needs stage B |
| S7a | RC loss in QHOVER (overrides stopped, no pulses underneath) | mode → QLAND **1.0 / 1.15 / 1.1 s** after the last frame ("RC Short Failsafe: switched to QLand"); the long event 4 s later changes nothing. QLAND descent 1.22 m/s (`Q_WP_SPD_DN` 1.2), 0.30 m/s below 5 m (`Q_LAND_FINAL_SPD`), "Land complete" and disarm | **pass** (≤ 3 s, `CL-F4-RC-FS-QLAND`) |
| S7b | RC loss in RTL / fixed wing | "RC Short Failsafe On" (no mode change in RTL), "RC Long Failsafe On: switched to RTL" 4.0–4.2 s later | pass |
| S9a | Altitude fence 110 m in FBWA | "Max Alt fence breached", RTL; while the recovery is active **the mode switch is refused** ("Mode change to Cruise denied, in fence recovery") | pass; the refusal goes on the flight card (CR-F4-25 to H3) |
| S18a | RTL with `Q_RTL_MODE` 2 | "Selected an approach path", "Starting VTOL land approach path", back-transition, position hold, "Weathervane Active: side in", descent, "Land final started", touchdown at 0.30 m/s, disarm 6 s later | logic pass, no wind set |

Simulated time flown: 6 runs of about 370–510 s = about 0.75 h (logic only; counts toward `R-PILOT` only if A2 accepts
stage A hours).

## Not run

S3 (wind), S3b, S4 (sagged pack, RCOU at `THR_MAX`), S5 on K09-L aero, S6, S8, S9 polygon, S10–S17, S19, all of stage B.
