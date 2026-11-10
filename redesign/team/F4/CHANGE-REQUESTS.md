# F4 change requests

R3 (2026-11-09) adds CR-F4-11 … 14. CR-F4-01 … 10 stand as filed in R1 (status column).

| Id | To | What | Why (numbers) | Status |
|---|---|---|---|---|
| CR-F4-11 | **D3** (cc B4, E1, A1) | **Cant sense is reversed.** Set `fin_detail.mount.cant_sense_UR` = **−1**, or keep the prints and fit **print B on UR and LL, print A on UL and LR** (no reprint). Required: UR thrust side component along −t = (0, +0.511, −0.860), i.e. prop end leans outboard and toward the wing plane; same rule at every station | UR and LL are CW seen from the nose (AP motors 4 and 3); their reaction torque on the frame is −x, so the cant force must give τx < 0 at UR; +t gives τx > 0. With +1 the 7° cant (0.045 m effective arm) cancels and exceeds the prop torque (0.020 m): hover yaw reverses. `CL-F4-CANT-SENSE-D3` = −1 (`FAILS`), `CALC-F4-MOTOR-MAP` `d3_sense_needed` −1 | new |
| CR-F4-12 | A1, C1, B2 (cc D6) | The "≤ 1/3 travel at VD" half of the D-29 schedule cannot be enforced in ArduPilot Plane: no airspeed-dependent surface limit, no Lua on the F405. F4 holds the schedule by envelope: no raw-stick FW mode, `PTCH_LIM_MIN_DEG` −10 (steady idle dive 17.8 m/s, 20.1 at L/D 7.16, ≤ VA 20.5), `THR_MAX` 75 (level ≤ 0.89 VH), `AIRSPEED_MAX` 18. Accept this, or size the hinge/servo for full travel at VD (5.9 kgf·cm, CR-C1-15) | `CL-F4-VDIVE-VA`, `CL-F4-VLEVEL-VH`; speed scaler gives × 0.59 at VD (`CL-F4-SCALER-VD`), not × 0.33 | new |
| CR-F4-13 | F5 | `RC_OPTIONS` set to **8480**, not 8448: bit 5 (throttle-at-zero arming check, the firmware default) kept; bits 8 + 13 as asked. All other CR-F5-01 lines applied (`RC5_OPTION` 153, `FLTMODE_CH` 6, `RC8_OPTION` 0, `RC9_OPTION` 31, `SERIAL6_PROTOCOL` 23, `RSSI_TYPE` 3, `FS_GCS_ENABL` 0, `FS_SHORT_TIMEOUT` 1.5) | a VTOL should not arm with throttle up | new |
| CR-F4-14 | H2, H3 (cc C5, D5) | Flight card, landing: final 0.5 m/s, wingtip into wind (the FC turns it, `Q_WVANE_LAND` 3); **flip the RC9 cut at contact**; do not wait for auto-disarm (≥ 5 s at the lower motor limit in ArduPilot). Log 20 twin touchdowns: contact (IMU) → RCOU minimum ≤ 0.5 s (T-F4-TD-CUT). Never select MANUAL/ACRO/STABILIZE from the GCS | `CL-F4-TD-CUT` 0.46 s (0.25 reaction assumed) | new |
| CR-F4-01 | B3 | Trimmed stall at R1 geometry; `AIRSPEED_MIN` integer | B3 published `CL-B3-VS-TRIM` 11.90 m/s; `AIRSPEED_MIN` now 16 (D-36) | closed |
| CR-F4-02 | B3 | Symmetric FW differential thrust | CR-B3-15: yaw damping now optional (Cn_β > 0) | closed |
| CR-F4-03 | E1, D3 | Station → motor → rotation → prop map; add the adapter thread (LH on CW: LL, UR) | E1 asked the thread (CR-E1-21), now in `params.json#fsw.motor_map`; cant part superseded by CR-F4-11 | open (cant) |
| CR-F4-04 | F2 | `signal.fc_port` on `E-HRN-24…29`: UR 4, UL 2, LR 1, LL 3, elevon L 5, R 6 | unchanged; F3 confirmed the timer groups (CR-F3-02) | open |
| CR-F4-05 | F3 | Board, bdshot, gyro rate, airspeed address | answered by CR-F3-02; all values in `K09L.param` §2, §6, §8, §12 | closed |
| CR-F4-06 | E1, H1 | Stand test of the rpm cap; magnet count. Stand overlay now in `subsystems/flight-software/K09L-STAND.param` (CR-H1-04). No Lua: if the build clamps `Q_M_SPIN_MAX` to 0.9, the cap must come from the ESC (Bluejay max-throttle setting) | `CL-F4-SPIN-MAX` 0.84 ≤ 0.849 | open |
| CR-F4-07 | A1 | Thrust cap | accepted (D-29) | closed |
| CR-F4-08 | E2 | `BATT_LOW_MAH` | E2's claim is 2 700 mAh; matches | closed |
| CR-F4-09 | A2 | `R-FSW-PARAMS` evidence: 67 of 143 names matched to source, 76 wait for SITL S1 on the 4.7.x tag; 6 LEGACY duplicates | `fsw_check.py` output | open |
| CR-F4-10 | H2, H3 | Transition at 12 °/s until logs show peak ≤ 0.7; motor-out = throttle cut, glide | B1 to re-check at sag 0.76 (D-35) | open |
