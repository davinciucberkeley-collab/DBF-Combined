# F5 RC range-test procedure (`T-F5-RANGE`, H1 card GT-14)

Revision F5-R3, 2026-11-13. Status `PROPOSED`; not run (no radio, receiver or aircraft exists yet). Owner F5, run by H1 (ground) and H2 (daily). Requirement `R-RC-LINK` (`team/A2/REQUIREMENTS.md`).
Numbers come from [`RC-LINK.md`](RC-LINK.md) (link budget, settings), [`rc_link.py`](rc_link.py) / `claims.json` and H1's card `GT-14` in `../H1/GROUND-TEST-PLAN.md`; this file is the step-by-step procedure and the log form.
The test proves that the real airframe, antennas and wiring leave at least 10 dB of fade margin at the 500 m line-of-sight limit, without flying 500 m.

## 1. What passes

| Pass line | Limit | Claim / source |
|---|---|---|
| Distance walked (line of sight) | **>= 105 m** (100 m plus the phone-GPS U95 error) | `CL-H1-RANGE-WALK`; GT-14 |
| Link quality (RQly) at every position | **>= 0.9** (90 %) | `requirements.rc_lq_min` |
| Better of 1RSS and 2RSS at every position | **>= -93.8 dBm** (predicted -82.2 dBm) | `requirements.rc_rssi_check_min_dbm`, `CL-F5-RC-RSSI-REQ` |
| Failsafe | none triggers | `R-RC-LINK` |
| Positions | 4 headings x 2 aircraft attitudes = **8 positions** | `RC-LINK.md` test table |

Derivation of the RSSI line (`RC-LINK.md`): receiver sensitivity -112 dBm at 150 Hz; required fade margin 10 dB at 515 m and 100 mW; the check is at 25 mW (-6 dB) and 100 m:
-112 + 10 + 20 log10(515 / 100) - 6 = -112 + 10 + 14.2 - 6 = -93.8 dBm. A pass proves the margin with the real airframe losses (16 dB assumed: airframe 8, polarisation 3, body and multipath 5).

## 2. Equipment and set-up

| Item | Spec | Source |
|---|---|---|
| Transmitter | RadioMaster Pocket, ELRS 2.4 GHz **FCC** version, EdgeTX model K09L | `R01`; `RC-LINK.md` |
| Receiver | RadioMaster RP3 V2, FCC version, two 150 mm U.FL T-antennas (A vertical through the hatch, B along -x out of the nose) | `A03`, `A06` |
| TX settings for the check | **25 mW**, 150 Hz, telemetry ratio 1:4, switch mode Wide, model match on | `RC-LINK.md` link settings; `CR-F5-05` |
| Aircraft | the real aircraft or the twin, **1 m above the ground on a non-metal stand** (wooden or PVC), nose-up (hover attitude) or nose-level (cruise attitude); **motors turning with props off at 20 %** | GT-14 |
| Distance | a measured 100 m line (tape or wheel) or phone GPS; the operator walks to >= 105 m | GT-14 |
| Telemetry | Pocket screen showing 1RSS, 2RSS, RQly (Yaapu script or the EdgeTX telemetry page) | `RC-LINK.md` ground station |
| Safety | **props removed**; aircraft tied to the stand; pack unplugged first when anything is touched; second person at the aircraft with the e-stop plug reachable; nobody in the prop plane | `../H1/GROUND-TEST-PLAN.md` rules; `../H3/BATTERY-PROCEDURE.md` |
| Weather / site | RFS or an open field; no metal fence or vehicle within a few metres of the aircraft | - |

## 3. Procedure (one operator walking, one at the aircraft)

1. **Before starting.** Confirm the ELRS firmware major version is the same on TX and RX and the domain is FCC (`T-F5-BENCH`). Note the TX power now; set **25 mW**. Note the firmware versions and the loaded `K09L.param` sha in the log.
2. Put the aircraft on the stand in the **hover attitude**, 1 m up, hatch closed as for flight, antennas in place. Fit nothing on the props. Plug the pack in only after the TX is on.
3. Bring the link up at 1 m from the aircraft: read 1RSS, 2RSS, RQly (expect strong RSSI, LQ 100). Start the motors props-off at 20 % from the RC (QSTABILIZE, arm switch SA) and keep them running through the walk; stop and re-arm if a failsafe triggers and log it as a fail.
4. Walk away on **heading 1** to the measured 100 m mark and beyond to **105 m**. Hold the TX at chest height, antenna as in normal use, **facing the aircraft**; do not shield it with the body. At 105 m wait 10 s and read the **worst** 1RSS, 2RSS and RQly over those 10 s. Log it.
5. Return. Repeat on **headings 2, 3, 4** (spread around the aircraft: for example 0, 90, 180, 270 deg relative to the nose; use the same marks every day).
6. Rotate the aircraft to the **cruise attitude** (nose level, as it flies in cruise), 1 m up. Repeat steps 3-5 on the 4 headings.
7. Stop the motors, disarm, **pull the pack**, fit the TX power back to the flight setting (**100 mW fixed**, `RC-LINK.md`), re-check the bind with the aircraft close.
8. Evaluate the log: every one of the 8 rows needs LQ >= 0.9, better of 1RSS and 2RSS >= -93.8 dBm and no failsafe. Write the result in the log header.
9. File `team/H1/logs/T-F5-RANGE_<YYYYMMDD>.csv` (columns below) and note the result in the next change request to F5 / A2. `kit.test("T-F5-RANGE", ..., state="run", result=..., measured=..., evidence=<log>)` is set by the owner (H1's pattern).

## 4. Log form

`team/F5/templates/range_log.csv` columns: `test_id, date, aircraft, attitude, heading_deg, distance_m, tx_power_mw, packet_rate_hz, rssi1_dbm, rssi2_dbm, best_rssi_dbm, rqly_pct, failsafe, pass, firmware_tx, firmware_rx, params_sha, wind_ms, notes`.

| Position | Attitude | Heading | Distance m | 1RSS dBm | 2RSS dBm | Best dBm | LQ % | Failsafe | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1-4 | hover | - | - | - | - | - | - | - | - |
| 5-8 | cruise | - | - | - | - | - | - | - | - |

## 5. If it fails

| Symptom | Likely cause | Action (owner) |
|---|---|---|
| One attitude fails, the other passes | an antenna element shadowed by carbon or the pack in that attitude | move the antenna (clearance >= 31 mm from carbon, pack, ESC leads: `CL-F5-ANT-CLEAR`); D2, F3 |
| 1RSS good, 2RSS poor (or the reverse) | one antenna damaged, kinked or too close to wiring | swap antennas, check the U.FL seat; F3 |
| Both poor in all positions | interference from the ESCs or DShot leads, or a 2.4 GHz source nearby | repeat with motors off; repeat elsewhere; reroute RX leads >= 50 mm from power leads (`RC-LINK.md` receiver installation); F2, F3 |
| LQ drops but RSSI is fine | packet-rate or interference problem | check domain and rate; try 250 Hz then back; F5 |
| Failsafe on motor start | brown-out of the RX (5 V rail) | RX on the FC 5 V rail, not the servo rail (CR-F5-02); `T-F3-5V`; F1, F3 |
| Result is marginal (within 3 dB of the line) | model is optimistic | do not fly beyond the 250 m geofence until the in-flight log review passes; tell A1 |

A failed range check **blocks the first flight** (`../H3/FLIGHT-CARD.md` limit 15). The aircraft is not flown until the cause is found and the test is repeated and passes.

## 6. Daily check and in-flight check

| Check | When | Pass |
|---|---|---|
| Short range check | first flight of each flying day, 25 mW, 100 m, one heading per attitude | LQ >= 0.9, no failsafe (`RC-LINK.md`) |
| `T-F5-FLIGHT-LINK` | every flight, from the DataFlash `RSSI` message (RSSI, RXLQ) in Mission Planner or UAVLogViewer, and the EdgeTX SD log | LQ >= 0.9 and RSSI >= -102 dBm at the farthest point; fixed-wing flights reach the 250 m fence |
| `T-F5-FS-BENCH` (separate card) | arrival bench, props off, tied down | QLAND in Q modes; circle then RTL in FW; <= 2.5 s |
| In-flight RC loss (H2 decides, later) | QHOVER at 15 m over the pad, TX off 3 s, after QLAND is proven | QLAND starts, pilot recovers on TX on |

Daily power setting: after the 25 mW check, return to **100 mW fixed** for the flight (`RC-LINK.md`); the flight row records the power used.

## 7. Legal reminder

2.4 GHz ISM, licence-free under 47 CFR 15.247; fly ELRS FCC firmware at its certified power, never an "unlocked" build; conducted power <= 1 W, EIRP <= 36 dBm; nothing else transmits (`RC-LINK.md` legal table).
