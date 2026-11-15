# flight-software — SITL plan

Revision F4-R7, 2026-11-14 (design round: S4c for D-149, S21 for D-152, S1 / S8 / S17 values). R6, 2026-11-13 (CDR fix round, CDR-07). Status: **SITL runs natively on the design machine** (no WSL). S1, the
S2 output map and first hover / transition / RC-loss runs are done on the stock tailsitter model (stage A, logic only):
`team/F4/sitl/RESULTS.md`. Everything else is `UNVERIFIED`. Stage B (K09-L aero) is not written. Owner F4; the pilot's
≥ 10 h (`R-PILOT`, `P:requirements.sitl_hours_min`) run on the same set-up after S1–S13 pass; about 0.75 h of logic runs so far.

## Install (Windows, as run on 2026-11-13; about 15 minutes)

Native, no administrator rights, no WSL. The binary is ArduPilot's own Cygwin build that Mission Planner downloads.

1. Make a folder, e.g. `C:\sitl\bin`. Download into it from `https://firmware.ardupilot.org/Tools/MissionPlanner/sitl/PlaneStable/`:
   `ArduPlane.elf`, `cygwin1.dll`, `cyggcc_s-1.dll`, `cyggcc_s-seh-1.dll`, `cygstdc++-6.dll`, `cygatomic-1.dll`, `cyggomp-1.dll`,
   `cygiconv-2.dll`, `cygintl-8.dll`, `cygquadmath-0.dll`, `cygssp-0.dll`, and `git.txt` (the commit it was built from: record it
   in `RESULTS.md`; on 2026-11-13 it was 4.7.3-beta1, the flight stable is 4.7.2).
2. Download `quadplane.parm` and `quadplane-copter_tailsitter.parm` from
   `https://raw.githubusercontent.com/ArduPilot/ardupilot/Plane-4.7.2/Tools/autotest/default_params/` into `C:\sitl\defaults`.
3. Python 3 (any 3.10+): `python -m venv C:\sitl\venv` then `C:\sitl\venv\Scripts\python -m pip install pymavlink` (2.4.50 used). Mission
   Planner or QGroundControl can be used instead of pymavlink for hand flying (connect TCP 127.0.0.1:5760).
4. Start, from an empty run folder (it holds `eeprom.bin` and `logs/`), with `C:\sitl\bin` on `PATH`:
   `ArduPlane.elf --model quadplane-copter_tailsitter --defaults C:\sitl\defaults\quadplane.parm,C:\sitl\defaults\quadplane-copter_tailsitter.parm --home 37.9150,-122.3340,5,0 --speedup 1 -I0`
   (add `--wipe` for a clean parameter store). It waits for a TCP connection on port 5760.
5. Load `K09L.param` (Mission Planner: Config > Full Parameter List > Load from file > Write), reboot SITL, load again
   (parameter groups that an enable switch opens, `BATT_*` and `INS_HNTCH_*`, only take values on the second pass), reboot, compare.
6. Apply the SIM-only overrides listed in `team/F4/sitl/RESULTS.md` (battery scaling, `ARSPD_TYPE` 2; for flight on the stock model
   also the output map and `Q_FRAME_TYPE` 0). Never save a parameter file from SITL over `K09L.param`.

If WSL is preferred (needs administrator rights and a reboot; not done on this machine): `wsl --install -d Ubuntu-22.04`; in Ubuntu
`git clone --recurse-submodules https://github.com/ArduPilot/ardupilot`, `git checkout Plane-4.7.2`, `git submodule update --init --recursive`,
`Tools/environment_install/install-prereqs-ubuntu.sh -y`, `. ~/.profile`, then
`Tools/autotest/sim_vehicle.py -v ArduPlane -f quadplane-copter_tailsitter --add-param-file=<path>/K09L.param --console --map`
(ArduPilot dev docs, "Setting up SITL on Windows 10 or 11 using WSL", https://ardupilot.org/dev/docs/building-setup-windows10_new.html, URL not re-read this session).

## Set-up

| Item | Value | Status |
|---|---|---|
| Build | ArduPlane 4.7.2 stable or later, the tag flashed on the CoreWing F405 Wing V2 (D-33; the board entered ArduPilot in 4.7.2) | SITL run so far: 4.7.3-beta1 |
| Stage A model | `--model quadplane-copter_tailsitter` (frame name confirmed in `Tools/autotest/pysim/vehicleinfo.py`, tag `Plane-4.7.2`) | runs. The stock model has motors on outputs 5–8 in a plus frame and aileron / elevator surfaces: K09-L's output map is checked disarmed (S2), flight uses the SIM-only map in `RESULTS.md` |
| Stage A use | logic only: modes, failsafes, output map, transition sequence. Not for gains or margins | — |
| Stage B model | JSON SITL backend (`-f JSON`) driven by a Python model from B3's aero table (`team/B3/results/sc_results.json`, CR-B3-04e), E1 thrust/torque per output, 7° cant in the sense of SPEC.md, 2.6 kg, inertia from A3, one torsion mode 11.7–14.9 Hz (C2) | to write after install |
| Wind | `SIM_WIND_SPD` 0 / 5 / 8 m/s, `SIM_WIND_TURB` 1 | — |
| Sagged pack | battery model loaded to thrust factor 0.76 (D-35) | parameter names to confirm |
| Logs kept | `.bin` + one line per case in `team/F4/sitl/RESULTS.md` (case, build, pass/fail, numbers) | — |

## Cases

| # | Case | How | Pass |
|---|---|---|---|
| S1 | Name check (**run 2026-11-13: pass**, 156 of 158 names accepted, `SERVO_BLH_BDMASK` / `_POLES` board-only; offline check in `fsw_check.py`) | load `K09L.param`, then `K09L-STAND.param`; `param show` each name; Mission Planner compare | no unknown name except the two board-only ones; `Q_M_SPIN_MAX` 0.84, `AIRSPEED_MIN` 17, `Q_M_BAT_CURR_MAX` 70.2, `BATT_LOW_MAH` 3 100, `Q_WVANE_LAND` 1, `THR_MAX` 60, `Q_A_ANGLE_BOOST` 0, `Q_ASSIST_ALT` / `ANGLE` 0, `BATT_FS_LOW_ACT` 6, `Q_M_BAT_CURR_MAX` 73.2, `Q_LAND_FINAL_SPD` 0.3, `Q_PILOT_SPD_DN` 1.0, `SERVO5/6_MIN/MAX` read back; each of the six mode-switch positions shows QSTABILIZE / QHOVER / QLOITER / FBWA / CRUISE / RTL, boot mode QSTABILIZE (R-SPIRAL); confirm `RCn_OPTION` 51 / 52 are the MANUAL / ACRO switches on this tag; pre-arm clean. `RCn_OPTION` 51 / 52 still to confirm as the MANUAL / ACRO switches on this tag |
| S1b | Mode switch, R9 slot order (CR-F5-15 / -16) | CH6 pulses 1 167 / 1 295 / 1 423 / 1 556 / 1 684 / 1 817 µs | modes 17 / 5 / 7 / 18 / 11 / 19 (QSTABILIZE, FBWA, CRUISE, QHOVER, RTL, QLOITER); boot 17 |
| S2 | Output map (**run 2026-11-13: A–D pass**; the tilt check cannot be done on the stock plus-frame model, bench step 1 does it) | QuadPlane motor test A–D, `SERVO1–6_FUNCTION`; tilt the model in QSTABILIZE | A=LR, B=UR, C=UL, D=LL; belly-forward tilt speeds up the upper pair |
| S3 | Hover | QLOITER 2 min at 0 / 5 / 8 m/s wind | 95 % of logged position samples within 1 m of the hold point over the 2 min run at 5 m/s (was "±1 m"; C-09, G-08, CR-132423 p. 49, `review/NASA-CR-132423-COMPLIANCE.md`); lean ≤ 20°; no motor at 0.84 for > 1 s |
| S3b | Velocity-loop crossover (stage B) | QLOITER, 1 m/s velocity-demand step; read the velocity-loop crossover from the log; repeat tethered (TUNING-PLAN.md step 4/5) (C-09, G-09, CR-132423 p. 61) | crossover ≤ 1/6 of the attitude crossover = ≤ 1.0 rad/s at the 1.0 Hz roll loop (`CL-F4-XOVER-RLL`); if it fails lower `Q_P_VELXY_P` / `Q_P_POSXY_P` and record them in `K09L.param` (C-06); parameter names to confirm on the 4.7.x tag in S1 |
| S4 | Pitch-over, FW output path | FBWA at 50 m, entered per S4c (transition switch: 1.285 θh, 1.0 s pre-climb (L06 0.9 s)), `Q_TAILSIT_RAT_FW` 12 / 16, fresh and sagged pack; then FBWA full throttle with full rudder | height gain ≤ 50 m; peak motor output < 0.84; airspeed ≥ 15.5 m/s within 15 s; RCOU at `THR_MAX` 60 = 0.60 (pass-through, source-read, `ASM-F4-FW-PASSTHRU` CHECKED); 0.6875 with full rudder |
| S4c | **Forward-transition throttle hold (B3 closure, F5 CR-F5-16; logic, stage A)** | driven by F5's `team/F5/transition_sitl.py` (F5 runs it; F5 run 2026-11-14: cases A–D pass) and F4's own `s8.py` stick-move case | ThI / ThH in the pre-climb 1.2769–1.2919; QSTABILIZE with the override 2.0–2.4 s; ThI held within 0.01 of entry to 70°; release ≥ 0.5 s after FBWA; `Q_A_ANGLE_BOOST` reads 0. A `throttle_in` reset would contradict the source reading: B3 re-opens its claim with the log |
| S5 | Back-transition (stage A run 2026-11-13 on the stock model: height gain 64 / 93 / 125 m at 50 / 30 / 20 °/s, not a K09-L number) | QHOVER from 16, 17 and 18 m/s, `Q_TAILSIT_RAT_VT` 20 / 30 / 50, `Q_TAILSIT_THR_VT` 49 / 55, **stage B with B3's post-stall table** (CDR-AE-03) | no tumble; **height gain ≤ 15 m, no motor at its floor for > 0.5 s** (CDR-07; was "height loss ≤ 10 m"); peak pitch-rate error and upper / lower RCOU split logged; if it fails lower `Q_TAILSIT_RAT_VT` to 20 only if the stage B trend agrees (stage A shows a slower pitch-up balloons more) |
| S6 | FW yaw | FBWA rudder doublet, `RUDD_DT_GAIN` 0 / 20 / 35 | yaw rate damped in < 2 cycles at 35 (stage B with Cn_β from B3) |
| S7 | RC loss (**Q-mode and RTL parts run 2026-11-13: QLAND 1.0–1.15 s after the last frame; long failsafe → RTL 4 s later in fixed wing**) | `SIM_RC_FAIL` 1 in QLOITER, pitch-over, cruise, back-transition | Q modes: QLAND ≤ 3 s after the last frame (`RC_FS_TIMEOUT` 1.0 s, `CL-F4-RC-FS-QLAND`); FW: circle, RTL at 5 s, as SPEC.md; nothing else. Still to run: FBWA / CRUISE (circle), pitch-over, back-transition |
| S8 | Battery, from a hover mode and from FW | `BATT_CAPACITY` 5 980; trigger LOW by voltage (`SIM_BATT_VOLTAGE` 13.7 < `BATT_LOW_VOLT` 14.0) in QLOITER at 60 m (above `Q_RTL_ALT`), then in CRUISE; critical at 13.5 V | **hover: `BATT_FS_LOW_ACT` 6 → QLAND, no forward transition (pitch stays in the hover band)**; control run with 1 → RTL and a pitch-over (why 6); FW: LOITER down to 50 m, then QLAND; critical → QLAND. Run 2026-11-14 (stage A): RESULTS.md |
| S9 | Geofence | climb past 110 m in QLOITER and in FW; fly past 250 m in FW | breach at `FENCE_ALT_MAX` 110 (`FENCE_MARGIN` 10 is a notice only, H2 / AC_Fence.cpp 4.7); action within 2 s; in a Q mode RTL starts a forward transition at max(hover, `throttle_in`) (no Q-mode fence action in Plane): recorded, bounded by `CL-B3-TRANS-PITCH-USE-HOVERTHR`. Polygon / exclusion zones (C-10, G-04, CR-132423 p. 54) with `FENCE_TYPE` 7: corners read back and plotted first; exclusion support on this board: — |
| S22 | Q-assist triggers (CR-C1-40 residual) | FBWA at 18 m/s; roll to 60° and pitch to −20° beyond the limits by RC override for 2 s; then FBWA at 12 m/s (below `Q_ASSIST_SPEED` 14) | with `Q_ASSIST_ANGLE` / `ALT` 0: no "Angle assist" / "Alt assist" message and RCOU stays on the FW mixer at 18 m/s; at 12 m/s speed assist engages (information). Control run with the default 30°: the message appears (proves the path) |
| S23 | Spin-cap script (D-161c) | **Withdrawn (D-173b)**; run 2026-11-14 kept as a record in RESULTS.md | — |
| S10 | GPS / EKF | `SIM_GPS1_ENABLE` 0 (or `SIM_GPS_DISABLE` 1) in QLOITER and in cruise | QLAND in Q mode; pilot recovers in QSTABILIZE; FBWA flyable in cruise |
| S11 | **Motor failure** | `SIM_ENGINE_FAIL` = bit of one motor, `SIM_ENGINE_MUL` 0; each motor; in hover at 30 m, mid pitch-over, cruise at 16 m/s | cruise: procedure (throttle cut, FBWA glide, belly land) keeps wings level, sink rate logged; hover / pitch-over: record time to loss of control (expected fatal, CONFIGURATION.md) |
| S12 | Transition fail | `SIM_ARSPD_FAIL` or a 20 m/s headwind so 13 m/s is not reached | QRTL at 15 s |
| S13 | E-stop | RC9 high from each mode, and at touchdown in QLAND/QHOVER | motor outputs at minimum ≤ 1 s (`R-ARM-KILL`); at touchdown RCOU to minimum in the same loop |
| S14 | Airspeed failure in cruise | `SIM_ARSPD_FAIL` 1 | synthetic airspeed, no stall, RTL possible |
| S15 | Pilot hours | QSTABILIZE recovery from a failed transition, landings in 5 m/s | 10 h logged with this file (`R-PILOT`) |
| S16 | Dive and level speed | FBWA full-down stick, idle and full throttle, 30 s; FBWB full throttle (stage B, prop model from B4) | dive airspeed ≤ 20.5 m/s (`CL-F4-VDIVE-VA`); level ≤ 21.8 m/s at ≤ 7 950 rpm (`CL-F4-VLEVEL-VH`, `-FW-RPM-CAP`) |
| S17 | Landing heading, descent, single-motor burst | QLAND from 20 m; motor test one output at full for 2 s | landing heading: see S21; descent ≤ 0.3 m/s below 6 m (`CL-F4-LAND-SPD`); QHOVER full down stick from 10 m to the ground: CRt ≥ −1.2 m/s at contact (`CL-F4-TOUCHDOWN-SINK`, stage B only for the overshoot); one output at full ≤ 2 s, none in any mode (CR-F1-10) |
| S18 | RTL VTOL approach (C-08, G-01, G-07, CR-132423 p. 35, 38-39, 172) | RTL from 200 m with `Q_RTL_MODE` 2, `Q_RTL_ALT` 50, `Q_FW_LND_APR_RAD` 60, `Q_TRANS_DECEL` 2.0, in 5 m/s wind from N, E, S and W | back-transition heading within ±45° of into-wind (EST); overshoot past home logged (64 m stop from 16 m/s is the EST); height loss ≤ 10 m; names `Q_RTL_MODE`, `Q_FW_LND_APR_RAD`, `Q_TRANS_DECEL` read back in S1 |

| S21 | **Landing heading, belly into the wind (D-152, C5 M2)** | `SIM_WIND_SPD` 5, `SIM_WIND_TURB` 1 (then 0), wind from the side of the start heading (`SIM_WIND_DIR` = start heading ± 90°); also start with the pod face (+z) to the wind (wind from start heading + 180°); QLOITER at 20 m, then QLAND to the ground; repeat QRTL from 200 m; no pilot yaw input. Stage A for the logic, stage B for the K09-L numbers | the belly (−z, copter nose) faces the wind within **±30°** from 6 m (`Q_LAND_FINAL_ALT`) through land-detect, every sample of `ATT.Yaw` against the wind direction (`XKF2` wind estimate and `SIM_WIND_DIR`); no turn through pod-face-to-wind below 6 m; log the yaw error at contact for C5. Also confirm in the log that the land override is the one applied (yaw target differs between `Q_WVANE_ENABLE` 1 and `Q_WVANE_LAND` set to 3 in one control run). **S21b (D-156):** same wind, AUTO mission with a VTOL_TAKEOFF to 20 m, started pod face to the wind: above the take-off height gate the belly turns to within ±30° of the wind and holds it to the end of the take-off (same control run with `Q_WVANE_TAKEOFF` 3) |
| S19 | Throttle step in cruise (CDR-AE-11, stage B) | FBWA at 16 m/s, throttle 30 → 70 % in one step, thrust line 18.5 mm below the CG in the model | pitch stays inside the FBWA limits (+20 / −10°), peak pitch excursion logged (B3: 1.9° of elevon equivalent, `CL-B3-THRUST-LINE-DELEV-THRMAX` 3.4° at full) |
| S20 | Hover yaw, wingtip into wind (CDR-AE-04, stage B) | QHOVER, `SIM_WIND_SPD` 5 then 8, heading held with a wingtip into wind, yaw steps ±10 / ±20° | heading returns; diagonal-pair RCOU spread ≤ 30 % at 5 m/s (B3: ratio 3.2 at 10°, 1.3 at 20°; saturates at 25° in 5 m/s and 12° in 8 m/s) |

`SIM_ENGINE_FAIL` ("Engine Fail Mask") and `SIM_ENGINE_MUL` ("Engine failure thrust scaler") are in the current
Plane parameter list (checked 2026-11-09) and in the SITL build (read 2026-11-13); `SIM_GPS_DISABLE` is not: use
`SIM_GPS1_ENABLE` 0 in S10. Which motor index each bit maps to is confirmed in S11 before the runs.
