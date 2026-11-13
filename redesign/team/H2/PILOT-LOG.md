# Pilot readiness log (`R-PILOT`): TEMPLATE

Revision H2-R1, 2026-11-13. Status: **empty; the pilot is not named** (`HANDOFF.md` H6). Requirement (`team/A2/REQUIREMENTS.md`): the designated pilot logs >= 10 h of ArduPilot SITL on the tailsitter model with the team's
parameter file, including QSTABILIZE recovery from a failed transition, plus stick time on the foam-board twin or a small quad, before the first XPS hover (`requirements.sitl_hours_min` = 10 h). SITL cases are `subsystems/flight-software/SITL-PLAN.md`
(S1-S13; results `team/F4/sitl/RESULTS.md`). SITL is not installed yet (`SITL-PLAN.md` status).

## Pilot

| Field | Value |
|---|---|
| Name | - |
| TRUST certificate (date, where filed) | - |
| AMA membership number and expiry | - |
| UC Drone Program registration | - |
| Simulator / stick used | - |

## Hours

| Date | Block | Hours | Build / params sha | Exercise (SITL case, twin flight or small-quad stick time) | Result | Log file |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | - |

Running total SITL hours: **0 of 10**. Stick hours on the twin or a small quad: **0**.

## Mandatory exercises (tick when done, with the log)

| # | Exercise | Done | Log |
|---|---|---|---|
| 1 | QSTABILIZE recovery from a failed transition (SITL S4 with a forced abort) | - | - |
| 2 | Pitch-over at 12 and 16 deg/s on a sagged pack (`T-F4-SITL-TRANSITION`) | - | - |
| 3 | Back-transition at 20 / 30 / 50 deg/s | - | - |
| 4 | RC loss in QLOITER, pitch-over, cruise, back-transition (S7) | - | - |
| 5 | Battery low and critical failsafes (S8), geofence (S9) | - | - |
| 6 | Motor-out in hover, pitch-over and cruise (`T-F4-SITL-MOTOR-OUT`): learn the e-stop decision | - | - |
| 7 | 20 landings in QLAND / QLOITER at 0 / 5 / 8 m/s wind | - | - |
| 8 | Twin or small-quad hovering, calm and breezy | - | - |

Sign-off: pilot / H2 / date: - . The first XPS hover (`FLIGHT-TEST-PLAN.md` gate 3 and 4) does not start without this signed line.
