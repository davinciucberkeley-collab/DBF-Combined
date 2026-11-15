# Small quadplane: first tests (QP-1, H1 ground test)

Status `PROPOSED`, 2026-11-14. Owner H1. Nothing is run or bought. Requirements: `REQUIREMENTS-QP.md` (QP-xx). Paths relative to `redesign/`. `EST` = estimate, `—` = unknown, `U` = price or spec from a snippet.
Purpose: buy down risk **before the main order** (airframe parts, second packs, spares), in the order the restudy sets: floor and test items first, airframe parts by mid-December (`config-study/RESTUDY-2026-11-14.md` section 4). The dates below are proposals for the team to confirm; the 15 Dec order date is K09-L's (CR-A1-42) and not re-derived.

## 0. Order and what each test buys

| # | Test | Buys down | Spend before it | Window (proposal) | Carries over from K09-L |
|---|---|---|---|---|---|
| QP1-1 | SITL QuadPlane setup and first runs | transition and assist logic, motor-out behaviour, param names, pilot hours | $0 | start now; 10 h total before first hover | `SITL-PLAN.md` install steps, F4 name check, `PILOT-LOG.md` |
| QP1-2 | Motor / prop bench thrust test (4 lift + 1 pusher candidates) | hover T/W, mass gate, hover throttle and current, pack C-rate, motor thermal; picks prop and motor | 5 motors, ESCs, 2-3 prop sizes, test gear (restudy floor), one 4S pack | as parts arrive; before 15 Dec | GT-01 / GT-02 / GT-04 rig and method, adapted |
| QP1-3 | Pack test (weigh, capacity, IR) | energy, sag, and so the T/W on the worst pack state | the pack and charger (floor items) | on arrival, before QP1-2 70-100 % steps | GT-05, adapted |
| QP1-4 | CG / balance | CG range, pack travel, lift-centroid offset | first parts | weigh as parts arrive; breadboard before ordering wing and booms | GT-06 / GT-07, adapted |
| QP1-5 | Boom sample tap and bend test | boom stiffness and vibration (QP-P16) | one sample boom tube (cost `—`) | before the boom size is ordered | GT-16 / GT-18, adapted |
| QP1-6 | Bench electrics, props off; RC range check | arm/kill, motor map and spin direction, failsafes, link | none beyond the floor | before any props-on run, again before first flight | GT-12, GT-14 unchanged |

Rule: a test that fails is repeated or sent to its owner, never waived (K09-L house rule, `H2/FLIGHT-TEST-PLAN.md` section 7).

## QP1-1 SITL QuadPlane setup

K09-L's native-Windows install carries unchanged (`subsystems/flight-software/SITL-PLAN.md`, steps 1-4): ArduPilot's Cygwin `ArduPlane.elf` set from `firmware.ardupilot.org/Tools/MissionPlanner/sitl/PlaneStable/`, Python venv with pymavlink, Mission Planner or QGC on TCP 127.0.0.1:5760. Changes for a plain quadplane:

| Item | Value |
|---|---|
| Model | `--model quadplane` with `--defaults quadplane.parm` (`quadplane.parm` is in the Plane-4.7.2 `default_params` folder per SITL-PLAN step 2). The frame name `quadplane` is `UNVERIFIED` until checked in `Tools/autotest/pysim/vehicleinfo.py` of the tag, as K09-L did for the tailsitter |
| Parameter file | `QP.param` (new, from CARRY-OVER.md section 1); load twice with a reboot between (enable-gated groups), compare; never save a SITL file over it |
| Name check | every name in `QP.param` against `team/F4/ap_plane_param_names_4.7.1.txt` (5,721 names; refresh from the flashed tag) with the `names` check pattern of `team/F4/fsw_check.py` |
| Firmware | ArduPlane 4.7.2 stable or later (K09-L's flashed tag) |
| Stage A (now) | the stock model: logic only (modes, failsafes, output map, transitions). Not for gains or margins |
| Stage B | stock model with QP-B mass and aero; **not written** (same gap as K09-L); aero numbers `—` |

| Run | What | Pass (logic) |
|---|---|---|
| S1 | Load, reboot, read back | 0 name misses; values read back equal |
| S2 | Output map disarmed: motor test A-D, pusher, surfaces | each channel on the planned output and direction |
| S3 | QSTABILIZE, QHOVER, QLOITER hover, VTOL takeoff to 50 m | holds position; no raw modes at start (`INITIAL_MODE` a Q mode) |
| S4 | Auto mission: VTOL takeoff, forward transition, 300 m racetrack at 15 m/s 30 deg bank, back-transition, QLAND | completes; transition at airspeed >= 1.3 Vs of the sim model; far point <= fence |
| S5 | Slow to `Q_ASSIST_SPEED` in FBWA | lift motors engage above the sim stall (QP-P9 window) |
| S6 | **Motor-out**: one lift motor failed (a) in hover, (b) during transition, (c) lift motors parked in cruise before back-transition; pusher failed in cruise | outcome recorded for each; expected (a) loss of control; (c) and pusher-out per QP-P15. The SITL failure parameter name is looked up in the SITL parameter list, not recalled |
| S7 | Airspeed sensor failed | no speed-based assist on synthetic airspeed; mode and failsafe per QP-P9 |
| S8 | RC loss in a Q mode; `BATT_LOW` and `BATT_CRT`; fence breach | QLAND / QRTL as planned (QP-P21) |
| S9 | 5 m/s steady, 8 m/s gust (SITL wind parameters) | holds position; lean <= `Q_A_ANGLE_MAX` - 5 deg |

Hours: log to `team/H2/PILOT-LOG.md` format; 10 h minimum (QP-D9) including S6.

## QP1-2 Motor / prop bench thrust test

**Candidates (restudy, `EST`):** lift SunnySky X2212 KV980 with 9 and 10 in props (maker row `U`: 870 g at 11.1 V, 13.2 A on a 10x4.7, flymod.net snippet); pusher a 2212 class motor with 9x6. The motor datasheet, ESC rating and bolt pattern are `—` until read.

**Rig: reuse the K09-L stand (GT-01) with changes.**

| Item | K09-L (GT-01) | Quadplane |
|---|---|---|
| Thrust axis | horizontal axle in two 608 bearings pushing the 20 kgf bar cell (I1 `G06`), torque arm 0.100 m on the 1 kgf cell (`G12`) | same; mount plate re-printed for the motor pattern (`—`) |
| Range needed | 2.69 kgf | about 1.5 kgf (1.25 x `EST` 1.0 kgf plus margin); 20 kgf cell is 7 % used |
| Resolution | 2 sigma <= 0.005 thrust | **tighten**: hover is 0.47 kgf, 0.5 % is 2.4 g, so 2 sigma noise from the 60 s zero step <= 2 g; if it fails, average 5 s per point and report U95. Purchase of a smaller cell is not assumed |
| Signal | FC with `K09L-STAND.param` overlay | FC with `QP-STAND.param` overlay (current limiter, rpm telemetry); a servo tester is the fallback |
| Safety rules, calibration steps 2-5, thermocouples | GT-01 rules | unchanged (H1 plan "Rules for every props-on card": nobody in the prop plane +/-30 deg, kill <= 1 s, full steps <= 2 s then >= 60 s idle, pack in a bag, thrust corrected to rho 1.225) |
| Jacobs bench supply | needed 44.6 A at K09-L | recompute: one motor, peak `—` A; if above the supply, use a flight pack for 70-100 % |

**Method (GT-02 adapted).**
1. Incoming check of all 5 motors: mass, bolt pattern, lead length, Rm (2.00 A, four-wire, corrected to 25 C), I0 and Kv at 10 V no prop (template `team/H1/templates/motor_incoming.csv`).
2. Stand run per prop (9x4.7 and 10x4.7, then pusher 9x6): 0 to 100 % in 10 % steps, 3 s each, mean of last 2 s; 0-60 % on a held supply, 70-100 % on a pack with V logged at the ESC; hover point 60 s at 0.47 kgf; ten 10 to 100 % punches (< 50 ms); repeat at the worst pack state (rest 3.73 V/cell, after QP1-3 discharge). Log with `team/H1/templates/stand_run.csv` (rpm from ESC telemetry, V, I, can and ESC temperature, rho).
3. Thermal: 5 min hold at hover thrust, then 1 min at 100 %; record can and ESC temperatures.

**Pass lines (all derived here from QP-B, `EST` where noted).**

| Pass | Limit | Basis |
|---|---|---|
| Lift thrust at 100 %, fresh pack, rho 1.225 | **>= 0.94 kgf** per motor (T/W 2.0 at 1.88 kg: 2.0 x 1.88 / 4) | QP-P2; restudy `EST` 1.0 kgf |
| Lift thrust at 100 %, pack at 20 % rest 3.73 V/cell | **>= 0.75 kgf** (T/W 1.6) | QP-P2, `hover_tw_min_sag` |
| Output (throttle fraction) giving 0.47 kgf | **<= 0.625** | 1 / 1.6 |
| Electrical power at 0.47 kgf | <= 79 W per motor (restudy 277 W / 4 = 69 W, +15 %); else rerun restudy energy | QP-D6, `hover_current_tol` |
| Peak current at 100 % | <= 80 % of ESC continuous rating and within maker motor limit (both `—`: read before the run); abort if above | QP-P19 |
| Motor can / ESC temperature | stop at the maker limit; interim stop at 80 C can (`EST`, protects magnet glue) | QP-P19 |
| Spread over the 4 flight motors | Kv <= 3 %, Rm <= 10 %, I0 <= 20 %; else fit the spare | GT-02 2a |
| Pusher static thrust | **>= 0.47 kgf** (0.25 W at 1.88 kg) | QP-P8 |
| Rig | zero drift <= 0.5 % start to end; linearity <= 0.5 % FS | GT-01 |

**Decision rule.** All lift lines pass: the prop with the lower hover power at 0.47 kgf wins, and the mass gate is set from the measured row (QP-P1). A lift line fails: A1 chooses between a larger prop, a higher-KV or larger motor, or a lower mass; the order of airframe parts waits. Pusher fails: change prop pitch or motor before the booms are cut.

## QP1-3 Pack test

CNHL 4S 3000 mAh (356 g listing, price `—`, restudy `U`). One row per pack in `team/E2/pack_log.csv` (columns: mass, size, lead exit, cell volts, capacity, IR at 25 C and 10 C).

1. Arrival: cell volts, mass with leads (1 g scale), dimensions.
2. Charge 1C, rest 1 h; IR by a step on the stand at 25 C.
3. Capacity to 3.5 V/cell under load with the watt meter, at about 1C; then a loaded run at about hover current (18.7 A = 277 W / 14.8 V, `EST`) for 3 min, noting sag and temperature. Handling per `team/H3/BATTERY-PROCEDURE.md`.

| Pass | Limit | Basis |
|---|---|---|
| Mass with leads | <= listing + 5 g (361 g) | QP-D4 |
| Capacity at 1C | **>= 2.76 Ah** (92 % of 3.0) | `pack_capacity_min_frac` |
| IR, whole pack, 25 C | **<= 15 mOhm** (`EST`: 6 % of 14.8 V sag at 58 A, full-thrust current of 4 x 214 W at 14.8 V; 58 A and 214 W from the restudy hover power scaled by T^1.5, `EST`) | QP-P2, QP-P19 |
| Cell spread on arrival | <= 0.02 V | GT-05 |
| Temperature after the hover-current run | at or under the BATTERY-PROCEDURE limit (read it there) | H3 |

## QP1-4 CG / balance

Method of GT-06 / GT-07 with the K09-L templates `team/H1/templates/weigh.csv` and `cg.csv`; same two-station formula x = x1 + (x2 - x1) W2 / (W1 + W2), lateral by left/right scales, height by the tilt method.

1. **Weigh every part on arrival** (0.1 g where possible), at the planned allocation (A3-style roll-up, `—`): this is the first mass-gate check and costs nothing.
2. **Breadboard before the order:** tape the real motors, ESCs, FC, GPS, pack and servos to a stick or foam board at the planned stations (booms, wing root) and balance on two pins: confirms the pack slide range is enough.
3. **Aircraft:** two scales under the wing at known stations, each pack position, lateral and height.

| Pass | Limit | Basis |
|---|---|---|
| x inside the cruise range (>= 5 % chord ahead of the neutral point, aft limit from it) | marks `—` until aero gives the neutral point | QP-P5 |
| Jig U95 in x | <= 25 % of the half-range of the window (K09-L: 0.6 mm of 2.4 mm) | `CL-H1-CG-U95` rule |
| Lateral y | <= 5 mm | `cg_lateral_max_m` |
| CG offset d from the lift-motor centroid | **<= 0.111 a** (arm a `—`) | QP-P4, ratio 1.25 |
| Pack slide range covers the CG spread of the 10 % growth case | `—` | derived at the breadboard |

## QP1-5 Boom sample tap and bend test

Method of GT-16 (bend with two lasers, torsion) and GT-18 (tap test, FC raw IMU >= 935 Hz, `INS_LOG_BAT_OPT` 5): clamp a sample boom with a dummy motor and prop mass at the end; tap, read the mode from the IMU FFT; bend at 1.25 x max motor thrust.

| Pass | Limit | Basis |
|---|---|---|
| Each mode vs 1P / 2P over hover-to-max rpm (1P about 130 Hz, 2P about 260 Hz, `EST`; measured rpm from QP1-2) | >= 20 % away | QP-P16 |
| Thrust-axis rotation at 1.25 x max motor thrust | <= 3 deg (`EST`) | QP-P16 |

## QP1-6 Bench electrics and RC range

GT-12 props off (arm, kill <= 1 s, motor map and direction, failsafes, `T-F5-BENCH`) and GT-14 range (`team/F5/RANGE-TEST.md`: >= 105 m walked, LQ >= 0.9, RSSI >= -93.8 dBm at 25 mW, 8 positions) carry **unchanged**; run before any props-on card with a full airframe.

## What does not carry

K09-L tests tied to the fin-tip stance and pitch-over do not apply: GT-03 fin swirl, GT-09 fin / foot / pod proofs, GT-10 foot drops, GT-11 tilt board, GT-15 coupons for fin and foot, GT-17 mount stiffness (the booms' QP1-5 replaces it), the elevon and transition-switch bench items. `team/H1/ground_tests.py` and its 96 claims are K09-L numbers: not re-run for the quadplane; QP claims are `—` until a QP claims file exists.
