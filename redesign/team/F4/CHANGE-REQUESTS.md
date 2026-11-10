# F4 change requests

R4b (2026-11-09) adds CR-F4-18 … 20, closes CR-F4-11 (D-52, D3 publishes −1) and CR-F4-17 (graph builds), and answers
CR-D5-21, CR-D6-09, CR-F3-20, CR-A2-14, CR-A3-23 (second table at the end). R4 added CR-F4-15 … 17. R3 added CR-F4-11 … 14;
CR-F4-01 … 10 stand as filed in R1 (status column).

| Id | To | What | Why (numbers) | Status |
|---|---|---|---|---|
| CR-F4-18 | **H3** (cc H2, D5, C5) | Flight card, landing: **QLAND (or RTL ending in QLAND) for the last 6 m**, or at most ¼ down stick in QHOVER/QLOITER. `Q_LAND_FINAL_SPD` is now 0.3 m/s below `Q_LAND_FINAL_ALT` 6 m (CR-D5-21), but it only governs QLAND and the end of RTL/QRTL; in QHOVER/QLOITER full down stick is `Q_PILOT_SPD_DN` 1.2 m/s. RC9 cut at contact unchanged (CR-F4-14) | D5: ≤ 0.32 m/s leaves no set in the cartridges (`CL-D5-V-NO-SET`), 0.5 m/s sets 1.28 mm per landing, 1.2 m/s is a hard landing. `CL-F4-LAND-SPD` 0.30 ≤ 0.32 (+6 %); about +8 s per landing | new |
| CR-F4-19 | **F3** (cc A3) | Re-run `CALC-F3-OFFSETS` on the R4 layout (it still holds GPS (0.080, 0, 0.169), giving (−0.027, 0, −0.169)) and take **z_cg from A3's model, +0.018 m**, not `cg.z_target_m` 0. Confirm the IMU centre z: F4 reads "board 4 mm higher" as IMU z 0.035 → **0.039 m**. F4 has set `INS_POS1/2` (0.062, 0.046, −0.021), `GPS1_POS` (−0.023, 0, −0.160) m FRD from CG (0.0522, 0, 0.018) | ArduPilot offsets are from the CG: using z 0 puts both 18 mm off. `CL-F4-SENSOR-POS-ERR` 0.2 mm (rounding). A3: please publish a CG-z claim (today only `CL-A3-CG-Z-RANGE`) so F3 and F4 cite one number | new |
| CR-F4-20 | **D6** (cc H1) | (a) Publish the TE-down servo angle as a claim (`CALC-D6-KIN.theta_dn_deg` −42.87°; F4 reads it through `ASM-F4-THETA-DN`). (b) T-D6-THROW: confirm the SH-0255MG+ turns ≥ ±45° over 1000–2000 µs, and the sense (right servo: higher pulse = TE up, left mirrored). Starting ends: **L 1003 / 1500 / 1976 µs reversed, R 1024 / 1500 / 1997 µs** | Span 497 µs of the 500 µs D6 assumes (`CL-F4-ELEVON-PWM-SPAN`, +0.6 %): if the servo turns less than 45° per 500 µs, the TE-up end needs a pulse beyond 1000/2000 µs (most servos accept 900–2100; D6 to say) | new |
| CR-F4-15 | **A1, C1** (cc B2, D6, H2) | Take CR-C1-20's recommended option: **F4 caps fixed-wing `THR_MAX` at 70 %** (was 75). Keep `requirements.vd_ms` 27.2 and n⁺ 3.4. Close CR-B1-17 with option (b) | Output ≤ 0.704 whichever FW output path the build uses (pass-through 0.700, thrust curve 0.704), 7 750 rpm on a fresh pack (≤ 7 950, `CL-F4-FW-RPM-CAP` +3 %), level speed **21.3 m/s ≤ 21.8** = 27.2 / 1.25 (`CL-F4-VLEVEL-VH` 0.98, +2 %). Margin rests on `ASM-F4-RPM-LIN` (VMAX ∝ rpm) and is shown by the step-6c level leg. AIRSPEED_MAX 18 stays reachable (`CL-F4-VLEVEL` 21.3) | new |
| CR-F4-16 | B1 | Confirm with your prop model: level speed at **7 750 rpm** (fresh pack, base drag) and FW climb rate at 70 % throttle on a sagged pack (0.76). F4 reads 21.3 m/s by scaling `CL-B1-VMAX` 25.68 by 7 750 / 9 350 | `CL-F4-VLEVEL` uses a linear scaling; your table (7 950 → 21.8, 8 000 → 21.9) agrees within 0.1 m/s | new |
| CR-F4-17 | proof-chain tooling (cc A2) | `proofs/build_graph.py` stops with `OverflowError` in `proofkit.fmt()` when a DRIFT message formats an infinite value (`int(inf)`). Guard `fmt()` for non-finite floats | R4b: the graph builds again and lists no F4 error or drift | closed |
| CR-F4-11 | **D3** (cc B4, E1, A1) | **Cant sense is reversed.** Set `fin_detail.mount.cant_sense_UR` = **−1**, or keep the prints and fit **print B on UR and LL, print A on UL and LR** (no reprint). Required: UR thrust side component along −t = (0, +0.511, −0.860), i.e. prop end leans outboard and toward the wing plane; same rule at every station | UR and LL are CW seen from the nose (AP motors 4 and 3); their reaction torque on the frame is −x, so the cant force must give τx < 0 at UR; +t gives τx > 0. With +1 the 7° cant (0.045 m effective arm) cancels and exceeds the prop torque (0.020 m): hover yaw reverses. `CL-F4-CANT-SENSE-D3` = −1 (`FAILS`), `CALC-F4-MOTOR-MAP` `d3_sense_needed` −1 | new |
| CR-F4-12 | A1, C1, B2 (cc D6) | The "≤ 1/3 travel at VD" half of the D-29 schedule cannot be enforced in ArduPilot Plane: no airspeed-dependent surface limit, no Lua on the F405. F4 holds the schedule by envelope: no raw-stick FW mode, `PTCH_LIM_MIN_DEG` −10 (steady idle dive 17.8 m/s, 20.1 at L/D 7.16, ≤ VA 20.5), `THR_MAX` 75 (level ≤ 0.89 VH), `AIRSPEED_MAX` 18. Accept this, or size the hinge/servo for full travel at VD (5.9 kgf·cm, CR-C1-15) | `CL-F4-VDIVE-VA`, `CL-F4-VLEVEL-VH`; speed scaler gives × 0.59 at VD (`CL-F4-SCALER-VD`), not × 0.33 | new |
| CR-F4-13 | F5 | `RC_OPTIONS` set to **8480**, not 8448: bit 5 (throttle-at-zero arming check, the firmware default) kept; bits 8 + 13 as asked. All other CR-F5-01 lines applied (`RC5_OPTION` 153, `FLTMODE_CH` 6, `RC8_OPTION` 0, `RC9_OPTION` 31, `SERIAL6_PROTOCOL` 23, `RSSI_TYPE` 3, `FS_GCS_ENABL` 0, `FS_SHORT_TIMEOUT` 1.5) | a VTOL should not arm with throttle up | new |
| CR-F4-14 | H2, H3 (cc C5, D5) | Flight card, landing: final 0.5 m/s, wingtip into wind (the FC turns it, `Q_WVANE_LAND` 3); **flip the RC9 cut at contact**; do not wait for auto-disarm (≥ 5 s at the lower motor limit in ArduPilot). Log 20 twin touchdowns: contact (IMU) → RCOU minimum ≤ 0.5 s (T-F4-TD-CUT). Never select MANUAL/ACRO/STABILIZE from the GCS | `CL-F4-TD-CUT` 0.46 s (0.25 reaction assumed) | new |
| CR-F4-01 | B3 | Trimmed stall at R1 geometry; `AIRSPEED_MIN` integer | B3 published `CL-B3-VS-TRIM` 11.90 m/s; `AIRSPEED_MIN` now 16 (D-36) | closed |
| CR-F4-02 | B3 | Symmetric FW differential thrust | CR-B3-15: yaw damping now optional (Cn_β > 0) | closed |
| CR-F4-03 | E1, D3 | Station → motor → rotation → prop map; add the adapter thread (LH on CW: LL, UR) | E1 asked the thread (CR-E1-21), now in `params.json#fsw.motor_map`; cant part closed by D-52 | closed |
| CR-F4-04 | F2 | `signal.fc_port` on `E-HRN-24…29`: UR 4, UL 2, LR 1, LL 3, elevon L 5, R 6 | unchanged; F3 confirmed the timer groups (CR-F3-02) | open |
| CR-F4-05 | F3 | Board, bdshot, gyro rate, airspeed address | answered by CR-F3-02; all values in `K09L.param` §2, §6, §8, §12 | closed |
| CR-F4-06 | E1, H1 | Stand test of the rpm cap; magnet count. Stand overlay now in `subsystems/flight-software/K09L-STAND.param` (CR-H1-04). No Lua: if the build clamps `Q_M_SPIN_MAX` to 0.9, the cap must come from the ESC (Bluejay max-throttle setting) | `CL-F4-SPIN-MAX` 0.84 ≤ 0.849 | open |
| CR-F4-07 | A1 | Thrust cap | accepted (D-29) | closed |
| CR-F4-08 | E2 | `BATT_LOW_MAH` | R4: set to 2 600 per CR-E2-20 (`CL-F4-BATT-LOW` 2 600 ≥ 2 600) | closed |
| CR-F4-09 | A2 | `R-FSW-PARAMS` evidence: 67 of 155 unique names matched to source, 88 wait for SITL S1 on the 4.7.x tag; 6 LEGACY duplicates | `fsw_check.py` output | open |
| CR-F4-10 | H2, H3 | Transition at 12 °/s until logs show peak ≤ 0.7; motor-out = throttle cut, glide | B1 to re-check at sag 0.76 (D-35) | open |

## Requests to F4 answered in R4

| Request | From | Done in R4 |
|---|---|---|
| CR-E2-20 | E2 | `BATT_LOW_MAH` 2 600 (was 2 700); `BATT_CRT_MAH` 1 300, `BATT_FS_VOLTSRC` 1, `Q_M_BAT_VOLT_MIN` 13.2 kept |
| CR-B1-17 / CR-C1-20 | B1, C1 | `THR_MAX` 70 (CR-F4-15); claims `CL-F4-VLEVEL-VH`, `-VLEVEL`, `-FW-RPM-CAP`; `Q_M_SPIN_MIN` 0.15 and `Q_M_THST_EXPO` 0.65 stated (calc inputs) |
| CR-B1-12 rev 3 | B1 | `Q_TAILSIT_RAT_FW` 12; at most 15 after the cold-pack stand run (TUNING-PLAN step 9); SITL S4 at 12 / 16 °/s |
| CR-B3-19 | B3 | crossover ceilings 4.5 / 4.5 / 2.4 Hz in `CALC-F4-XOVER`; P ceilings 0.34 / 0.14 / 0.94, yaw D 0 (TUNING-PLAN step 4); thrust-lag test `T-F4-THRUST-LAG` in step 2; `INS_GYRO_FILTER` 40 kept |
| CR-B4-16 | B4 | spin map kept; hanging yaw test `T-F4-HANG-YAW` as TUNING-PLAN step 1b |
| CR-H1-18 | H1 | `K09L-STAND.param`: `INS_LOG_BAT_OPT` 1 (sensor rate), `INS_LOG_BAT_MASK` 1; rate read back from the log (`UNVERIFIED` on this board) |
| CR-I1-16 | I1 | Yes: the first fixed-wing tune (FBWA hand-launch, step 6) runs with `ARSPD_TYPE` 0 on the synthetic estimate; no CRUISE/AUTO/RTL in fixed wing until the sensor is fitted. Tailsitter transition completion is angle-based (`Q_TAILSIT_ANGLE`), so it does not need the sensor; `Q_ASSIST_SPEED` and TECS do. Buy the MS4525DO before the first transition |
| CR-A4-12 | A4 | output ports unchanged and equal to `signal.fc_port` on `E-HRN-24…29` (CR-F4-04) |

## Requests to F4 answered in R4b

| Request | From | Done in R4b |
|---|---|---|
| CR-D5-21 | D5 | `Q_LAND_FINAL_SPD` 0.3 m/s, LEGACY `Q_LAND_SPEED` 30 cm/s, `Q_LAND_FINAL_ALT` 6 m stated; claim `CL-F4-LAND-SPD` 0.30 ≤ `CL-D5-V-NO-SET` 0.32; flight-card follow-up CR-F4-18 |
| CR-D6-09 | D6 | `SERVO5/6_MIN/TRIM/MAX/REVERSED` per side from `CALC-D6-KIN` (+44.7° up, −42.9° down, 11.1 µs/°): L 1003/1500/1976 rev, R 1024/1500/1997; `MIXING_GAIN` 0.5 stated (`CL-F4-MIX-PITCH` 0.88); CR-F4-12 envelope kept; final values from T-D6-THROW (CR-F4-20) |
| CR-F3-20 | F3 | `GPS1_POS` (−0.023, 0, −0.160), `INS_POS1/2` (0.062, 0.046, −0.021) m from CG (0.0522, 0, 0.018); `CALC-F4-SENSOR-POS`; CG-z difference raised as CR-F4-19 |
| CR-A2-14 | A2 | `CL-F4-BAT-CURR-MAX` is now calc-backed (`CALC-F4-BAT-CURR`, 100 ≤ `P:performance.full_throttle_current_a` 100) plus `CL-F4-BAT-CURR-MOTOR` 25 ≤ 25 A; both verified by H1's `T-H1-RESTRAINED-RUN` |
| CR-A3-23 | A3 | re-run on A3's roll-up as read at 2026-11-09 evening (A3 was still re-running: split 1.214 → 1.216, Iyy 0.0423 → 0.0449): `CL-F4-SPLIT-OUT` 0.671 ≤ 0.84; Ixx 0.174 / Iyy 0.0449 / Izz 0.168 kg·m² → crossover 1.04 / 2.44 / 1.01 Hz, P ceilings 0.35 / 0.148 / 0.95 (TUNING-PLAN keeps the lower 0.34 / 0.14 / 0.94); no F4 error or drift in `build_graph.py` |
| CR-H1-18 | H1 | flight file now also logs raw IMU at sensor rate (`INS_LOG_BAT_OPT` 5 = sensor rate + pre/post filter); stand overlay keeps 1 |
| CR-B3-19 | B3 | ceilings 4.5 / 4.5 / 2.4 Hz written into `K09L.param` as holding "until T-C2-TAP-TEST" |
| CR-B4-16a | B4 | spin map unchanged with the corrected cant (D-52); `CL-F4-CANT-SENSE-D3` +1 |
| D-50 / CR-F4-15 | A1 | `THR_MAX` 70 kept (accepted); envelope-held schedule (CR-F4-12) kept |
