# Foam-board twin test report (`R-TWIN`): TEMPLATE

Revision H2-R1, 2026-11-13. Status: **template, nothing flown**. Copy this file's tables into one report per twin campaign, fill every cell from the logs in `logs/`, keep unmeasured cells as `-`.
Pass lines come from `R-TWIN` and `R-TEST-ORDER` (`team/A2/REQUIREMENTS.md`) and gate 1 of [`FLIGHT-TEST-PLAN.md`](FLIGHT-TEST-PLAN.md). A failed or missing line is reported as `FAIL` or `NOT RUN`, never rounded into a pass.

## 1. Header

| Field | Value |
|---|---|
| Report id / revision | TWIN-R_ |
| Dates of flights | - |
| Site, sub-field, flight-request id, post-flight report filed (date) | - |
| Pilot, spotter, logger, safety lead | - |
| Aircraft | twin id; mass (kg); CG x, z (m); wing area (m2); elevon area (fraction of wing) |
| Propulsion as flown | motor, ESC, prop (11x4.5MR or 11x5.5MR), pack id and mass, `K09L.param` sha |
| Differences from K09-L that change a result | - (list: foam-board wing, no fins, no tubes, mass, CG, inertia) |
| Software | ArduPilot Plane version; `K09L.param` revision; params changed during the campaign with the log number each |

## 2. Gate table (fill one row per line; sources: gate 1 of the plan)

| # | Line | Pass line | Measured | Unit | Log (`logs/<id>_<date>`) | Result |
|---|---|---|---|---|---|---|
| 1a | Bench: motor map, directions, elevons | all right | - | - | `T-F4-BENCH-MAP`, `T-F5-BENCH` | - |
| 1b | Hanging yaw test | frame yaws -x then +x | - | - | `T-F4-HANG-YAW` | - |
| 1c | Hover, calm: position hold | <= 1 | - | m | - | - |
| 1c | Hover lean | <= 20 | - | deg | - | - |
| 1c | Hover current | 27 +/- 0.15 x 27 (= 22.95 to 31.05) | - | A | `T-E1-HOVER-LOG` | - |
| 1c | VIBE max / clip | < 30 / 0 | - | m/s2 | `T-F3-VIBE` | - |
| 1d | Hover at 5 m/s measured: position hold | <= 1 | - | m | `T-B3-HOVER-WIND` | - |
| 1d | Lean, motor output band | <= 20 deg; 10 % to 85 % | - | deg, % | - | - |
| 1e | QLOITER at >= 30 m: hold | <= 1 | - | m | - | - |
| 1f | Neutral point Xnp | from elevon trim vs CL (slope 0) | - | m | `T-B3-TWIN-NP` | - |
| 1g | Stall speed Vs (mean of 3) | <= 12.0 | - | m/s | `T-B2-STALL` | - |
| 1h | Yaw doublet: return within 2 s | yes | - | s | `T-B3-YAW-DOUBLET` | - |
| 1i | Transition speed | >= 15.5 and >= 1.3 Vs | - | m/s | `T-B1-TRANSITION-LOG` | - |
| 1i | Height loss in transition | <= 10 | - | m | - | - |
| 1i | Laps flown, back-transition | 2 laps + back-transition | - | - | - | - |
| 1i | Cruise current | about 16.2 | - | A | `T-B1-CRUISE-POWER` | - |
| 1j | Touchdown ground speed, 95th percentile (20 landings) | <= 0.3 | - | m/s | `T-C5-DRIFT-LOG` | - |
| 1j | Throttle out within 0.5 s of contact | <= 0.71 hover | - | - | `T-F4-TD-CUT` | - |
| 1k | Dive airspeed | <= 20.5 | - | m/s | `T-F4-DIVE` | - |
| - | Elevon size that gives clean FBWA authority | recorded | - | fraction | - | - |

## 3. What the twin says about the real aircraft (fill after the table)

| Quantity | Model value (claim) | Twin measured | Transfer note (what differs) | Goes to |
|---|---|---|---|---|
| Stall speed | `CL-B2-STALL-GATE` | - | - | B2, F4 (`AIRSPEED_MIN`) |
| Transition speed and height loss | `CL-B1-TRANS-ALT-LOSS` | - | - | B1, F4 |
| Hover current and throttle | `CL-E1-HOVER-I-55` | - | - | E1, E2 |
| Hover pitch-trim split | `CL-A3-HOVER-SPLIT` (1.216 vs 1.25) | - | - | A3, B3 |
| Neutral point | `CL-B3-XNP` | - | - | B3 |
| Wind authority at 5 m/s | `CL-B3-HOVER-PITCH-RATIO` | - | - | B3, A1 |
| Link quality in flight | `CL-F5-LINK-MARGIN` | - | - | F5 |

## 4. Anomalies, crashes, repairs

| # | Flight | What happened | Log | Cause (if known) | Repair, time, cost | Open item |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | - |

## 5. Verdict (H2 signs; A1 decides)

| Item | Entry |
|---|---|
| Gate 1 result | PASS / FAIL / NOT RUN |
| Lines failed or not run | - |
| Recommendation for the 15 Dec order | order / hold / reverse (K11 planform test, then K01-lean, per `CONFIGURATION.md`) |
| Signed (H2) / date | - |
| Decision (A1) / date | - |

## 6. Attachments

Flight rows (`logs/*.csv`), `.bin` paths, wind log (`../H3/WIND-RFS.md`), photos, parameter diff.
