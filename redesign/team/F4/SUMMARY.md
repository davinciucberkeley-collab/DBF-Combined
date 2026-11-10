# F4 — flight-control software

Status `PROPOSED`, revision **F4-R3**, 2026-11-09. Deliverables in `subsystems/flight-software/`: `K09L.param` (149
lines, every line commented; ArduPlane 4.7.x on the CoreWing F405 Wing V2), `K09L-STAND.param` (stand overlay),
`SPEC.md`, `SITL-PLAN.md` (17 cases), `TUNING-PLAN.md`, `params.json`. Check: `python -I redesign/team/F4/fsw_check.py`
→ lint OK on both files, mirror OK, 30 claims, one with a negative margin (D3 cant sense, below); `build_graph.py`
reports no F4 error. Nothing loaded, flown or run in SITL: every behaviour `UNVERIFIED`.

## CR-A1-36 items, resolved

| Item | Set | Unit | Claim (value) | Status |
|---|---|---|---|---|
| `AIRSPEED_MIN` 15.6 (D-36) | **16**: the parameter is an integer (`AP_Int16`, checked in source) | m/s | `CL-F4-ARSPD-MIN-FLOOR` 16 ≥ 15.6 | `UNVERIFIED` (upstream stall) |
| `Q_TAILSIT_RAT_FW` | 12 until B1 re-checks at sag 0.76 | °/s | — | `UNVERIFIED` |
| Elevon schedule to VD 27.2 | no FW raw-stick mode; `PTCH_LIM_MIN_DEG` −10 (was −15); `TECS_SINK_MAX` 2.5 | °, m/s | `CL-F4-VDIVE-VA` 17.8 ≤ 20.5 | `UNVERIFIED` |
| `AIRSPEED_MAX` 18, `ARSPD_FBW_MAX` ≤ 22 | 18 (`ARSPD_FBW_MAX` is its pre-4.5 name) | m/s | `CL-F4-ARSPD-MAX-CAP` +18 % | `UNVERIFIED` |
| `THR_MAX` so level speed < VH | 75 | % | `CL-F4-VLEVEL-VH` 0.89 | `UNVERIFIED` |
| Rate-loop crossover ≤ 5 Hz | roll / pitch / yaw 1.1 / 2.6 / 1.0; P ceilings 0.38 / 0.15 / 1.9 in TUNING-PLAN | Hz | `CL-F4-XOVER-*` | `UNVERIFIED` |
| Gyro low-pass ≥ 2 × from 12 Hz | `INS_GYRO_FILTER` 40, `Q_A_RAT_RLL/PIT_FLTD` 32 against the 14.9 Hz band top | Hz | `CL-F4-FILT-SEP` 2.15 | `PROPOSED` |
| Notch on ESC rpm | mode 3, `INS_HNTCH_REF` 1 (added: 0 freezes it), 70 Hz, harmonics 1–3 | Hz | `CL-F4-NOTCH-LOW` 1.28, `-TOP` 0.94 | `UNVERIFIED` |
| Cant sense A/B at 7° vs the map | **D3's sense is reversed** → CR-F4-11 | — | `CL-F4-CANT-SENSE-D3` −1 (**FAILS**) | `CHECKED` (calc) |
| Spin-min ≤ 0.5 s after touchdown | RC9 cut at contact (auto-disarm needs ≥ 5 s in ArduPilot) | s | `CL-F4-TD-CUT` 0.46 | `UNVERIFIED` |
| Wingtip-into-wind landing | `Q_WVANE_LAND` 3, `Q_WVANE_TAKEOFF` 3 (side into wind) | — | — | `PROPOSED` |
| `ARSPD_TYPE` 1 (MS4525DO) | 1, `ARSPD_BUS` 0, `ARSPD_TUBE_ORDR` 2 | — | — | `PROPOSED` |
| ELRS map (CR-F5-01) | arm ch 5, modes ch 6, e-stop ch 9, `SERIAL6_PROTOCOL` 23, `RSSI_TYPE` 3, `RC_OPTIONS` 8480, `FS_GCS_ENABL` 0 | — | — | `PROPOSED` |
| LH adapters on CW motors | LL and UR (outputs 3, 4); in `params.json#fsw.motor_map` | — | — | `PROPOSED` |
| `Q_M_BAT_CURR_MAX` 100 (CR-A2-14) | 100, `Q_M_BAT_IDX` 0, TC 1 s | A | `CL-F4-BAT-CURR-MAX` → R-ESC-CURRENT, R-FSW-PARAMS | `PROPOSED` |

Also applied: CR-F3-02 board lines (`AHRS_ORIENTATION`, battery scaling 11.05 / 64, sensor offsets, SERIAL5 GPS),
CR-H1-04 stand overlay (25 A), CR-E3-05 (no mode demands sustained full throttle), CR-D5-09 (0.5 m/s final).

## Findings others depend on

| Finding | Effect |
|---|---|
| D3's printed cant gives UR thrust along +t; the map needs −t | hover yaw would reverse on first spin-up; swap prints (CR-F4-11) |
| ArduPilot has no airspeed-scheduled surface limit; no Lua on the F405 | ≤ 1/3 at VD held only by the envelope (CR-F4-12) |
| Steady idle dive at −15° pitch reaches 26 m/s (near VD); at −10°, 17.8–20.1 m/s | pitch floor −10° |
| Quadplane land detector: motors at lower limit ≥ 5 s before disarm | touchdown cut is a pilot action (CR-F4-14) |
| Upstream claims re-run differently from their stored values (A3 inertia, B1 L/D, VMAX) | F4 numbers follow the re-run; the dive is 20.1 m/s on B1's stored L/D 7.16, still ≤ 20.5 |

## Open

CR-F4-11 … 14 new (D3, A1/C1/B2, F5, H2/H3); CR-F4-03/04/06/09/10 open. 76 of 143 names wait for SITL S1 on the 4.7.x tag.
