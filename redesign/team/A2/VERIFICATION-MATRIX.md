# Verification matrix — K09-L quad tailsitter

Generated 2026-11-09 12:53 UTC by `team/A2/build_requirements.py` from `team/A2/requirements.json` and `proofs/out/graph.json` (graph built 2026-11-09 12:53 UTC, OK). Status is computed by `proofs/build_graph.py` from the claims that name each requirement in `verifies`; nobody types it. Re-run: `python -I redesign/team/A2/build_requirements.py`.

## Summary

| Requirements | With ≥ 1 claim | `VERIFIED` | `CHECKED` | `PROPOSED` | `UNVERIFIED` | `FAIL` |
|---|---|---|---|---|---|---|
| 57 | 13 | 0 | 5 | 1 | 51 | 4 |

Failing now: `R-TRANSITION` (CL-A1-TRANSITION-GATE: FAILS: margin -0.3% (15.05 m/s vs <= 15 m/s)), `R-MASS-GATE` (CL-A3-MASS-BASIC is UNVERIFIED; CL-A3-MASS-PREDICTED is UNVERIFIED; CL-A3-GATE-MARGIN: FAILS: margin -18.4% (0.08162 kg vs >= 0.1 kg)), `R-STATIC-MARGIN` (CL-A3-CG-X-RANGE: FAILS: margin -126.2% (2.262 vs <= 1); CL-A3-CG-Z-RANGE is UNVERIFIED; CL-A5-LAYOUT-CG-X: FAILS: margin -18.2% (0.03679 m vs >= 0.045 m); CL-J1-SM-TRIMMABLE: FAILS: margin -45.9% (0.02704 vs >= 0.05)), `R-DISCONNECT` (CL-J1-XT60-CONT is PROPOSED; CL-J1-XT60-BURST: FAILS: margin -50.0% (60 A vs >= 120 A); CL-J1-AS150U-CONT is PROPOSED; CL-J1-AS150U-BURST is PROPOSED).

Method: A analysis · I inspection · T test · D demonstration. On disk: evidence files that exist today / listed. `UNVERIFIED (no claim)` means the owner has not yet emitted a claim naming the id.

## Matrix

| ID | Title | Owner | Support | Method | Evidence | On disk | Claims | Margin | Status |
|---|---|---|---|---|---|---|---|---|---|
| `R-CONFIG` | Configuration K09-L | A1 | A4 | I | `README.md` `team/A1/claims.json` | 2/2 | `CL-A1-WING-AREA` | — | `CHECKED` |
| `R-MISSION` | Mission endurance | B1 | E2 H2 | A+T | `team/B1/claims.json` `team/E2/claims.json` `team/H2/logs/` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-ENVELOPE` | Props-off envelope | A5 | D1 D3 | A+I | `fusion/check.py` `team/A5/claims.json` | 2/2 | — | — | `UNVERIFIED` (no claim) |
| `R-STALL` | Stall speed | B2 | B1 H2 | A+T | `team/B2/claims.json` `team/A1/claims.json` `team/H2/logs/` | 1/3 | `CL-A1-STALL-GATE` | +4 % | `UNVERIFIED` |
| `R-TRANSITION` | Transition speed | B1 | F4 H2 | A+T | `team/B1/claims.json` `team/H2/logs/` | 0/2 | `CL-A1-TRANSITION-GATE` | -0 % | `UNVERIFIED` `FAIL` |
| `R-MASS-GATE` | Mass gate 2.6 kg | A3 | H1 | A+T | `MASS-CG.md` `team/A1/claims.json` `team/H1/claims.json` | 2/3 | `CL-A1-MASS-SIZED` `CL-A3-MASS-BASIC` `CL-A3-MASS-PREDICTED` `CL-A3-GATE-MARGIN` | -18 % | `UNVERIFIED` `FAIL` |
| `R-MASS-ALLOC` | Subsystem mass allocations | A3 | all designers | A+T | `MASS-CG.md` `team/A3/claims.json` | 2/2 | — | — | `UNVERIFIED` (no claim) |
| `R-CG-RANGE` | As-built CG range | A3 | B3 H1 | A+T | `MASS-CG.md` `team/A3/claims.json` `team/H1/claims.json` | 2/3 | — | — | `UNVERIFIED` (no claim) |
| `R-STATIC-MARGIN` | Static margin | B3 | H2 | A+T | `team/B3/claims.json` `team/H2/logs/` | 0/2 | `CL-A3-CG-X-RANGE` `CL-A3-CG-Z-RANGE` `CL-A5-LAYOUT-CG-X` `CL-J1-SM-TRIMMABLE` | -126 % | `UNVERIFIED` `FAIL` |
| `R-HOVER-TW` | Hover thrust-to-weight | E1 | H1 | A+T | `team/E1/claims.json` `team/A1/claims.json` `team/H1/claims.json` | 1/3 | `CL-A1-HOVER-TW-GATE` `CL-A1-HOVER-TW-SAG` | +22 % | `UNVERIFIED` |
| `R-WIND` | Wind | B1 | H2 H3 | A+D | `team/B1/claims.json` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-GUST-LEAN` | 8 m/s gust survive-and-land | B1 | F4 | A | `team/B1/claims.json` `subsystems/flight-software/params/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TIPOVER` | Stance tip-over | C5 | H1 | A+T | `team/C5/claims.json` `team/A1/claims.json` `team/H1/claims.json` | 1/3 | `CL-A1-TIPOVER` | +24 % | `CHECKED` |
| `R-DIRECTIONAL` | Directional stability in cruise | B3 | J1 H2 | A+T | `team/B3/claims.json` `team/J1/claims.json` `team/H2/logs/` | 1/3 | — | — | `UNVERIFIED` (no claim) |
| `R-HOVER-AUTHORITY` | Hover control authority | B3 | A3 H2 | A+D | `team/B3/claims.json` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-CRUISE-AUTHORITY` | Elevon authority in cruise | B3 | B2 H2 | A+T | `team/B3/claims.json` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-ELEVON-AREA` | Elevon area | B3 | D1 H2 | A+D | `team/A1/claims.json` `team/B3/claims.json` `team/H2/logs/` | 1/3 | `CL-A1-ELEVON-FRAC` `CL-A5-ELEVON-GAP-MIN` | +15 % | `UNVERIFIED` |
| `R-SERVO-TORQUE` | Elevon servo torque | D6 | B2 H1 | A+T | `team/B2/claims.json` `subsystems/mechanisms/SPEC.md` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-PROP-CLEAR` | Prop clearance | D3 | B4 A5 | A+I | `team/A1/claims.json` `fusion/check.py` `subsystems/fins/SPEC.md` | 2/3 | `CL-A1-PROP-CLEAR` | +56 % | `UNVERIFIED` |
| `R-AIRSPEED` | Airspeed sensor placement and accuracy | F3 | B4 H2 | A+T | `subsystems/avionics/SPEC.md` `team/B4/claims.json` `team/H2/logs/` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-ESC-CURRENT` | Motor and ESC current | E1 | F1 H1 | A+T | `team/E1/claims.json` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-PACK-MASS` | Flight pack mass and capacity | E2 | A3 | T | `team/E2/claims.json` | 0/1 | — | — | `UNVERIFIED` (no claim) |
| `R-THERMAL` | Thermal limits | E3 | H1 H2 | A+T | `team/E3/claims.json` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-LOADS` | Load cases defined | C1 | B1 C5 | A | `team/C1/LOADS.md` `team/C1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-STRUCT-MARGIN` | Structural margins | C2 | C3 C4 C5 C6 H1 | A+T | `team/C2/claims.json` `team/C3/claims.json` `team/C4/claims.json` `team/C5/claims.json` `team/C6/claims.json` `team/H1/claims.json` | 0/6 | — | — | `UNVERIFIED` (no claim) |
| `R-FIN-TUBE-JOINT` | Fin-tube-saddle joint | C4 | D3 C6 G3 | A+I | `subsystems/fins/SPEC.md` `team/C4/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-VIBRATION` | Motor-tube vibration | C4 | E1 H1 H2 | A+T | `team/C4/claims.json` `team/H1/claims.json` `team/H2/logs/` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-PACK-RETENTION` | Pack retained in a crash | C3 | D2 H1 | A+T | `subsystems/pod/SPEC.md` `team/C3/claims.json` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-LANDING-IMPACT` | Fin-tip landing | C5 | D5 H1 | A+T | `subsystems/landing/SPEC.md` `team/C5/claims.json` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-DISCONNECT` | Connectors carry the current | F1 | E1 H1 | A+T | `subsystems/power/SPEC.md` `team/F1/claims.json` `team/H1/claims.json` | 0/3 | `CL-J1-DISCONNECT-REQ` `CL-J1-XT60-CONT` `CL-J1-XT60-BURST` `CL-J1-AS150U-CONT` `CL-J1-AS150U-BURST` | -50 % | `PROPOSED` `FAIL` |
| `R-AVIONICS-POWER` | Avionics power | F1 | F3 H1 | A+T | `subsystems/power/SPEC.md` `team/F1/claims.json` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-HARNESS-INSTALL` | Wiring is an installation | F2 | A4 | I | `subsystems/harness/SPEC.md` `subsystems/harness/interfaces.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FC-STABLE` | Stable autopilot build | F3 | F4 | I+D | `subsystems/avionics/SPEC.md` `team/F3/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FSW-PARAMS` | Tailsitter parameter file | F4 | E1 H1 | I+D | `subsystems/flight-software/SPEC.md` `subsystems/flight-software/params/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-ARM-KILL` | Arming and emergency stop | F4 | H1 H3 | T | `subsystems/flight-software/SPEC.md` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FAILSAFES` | Failsafes and geofence | F4 | H1 H3 | T+D | `subsystems/flight-software/SPEC.md` `subsystems/flight-software/SITL-PLAN.md` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-RC-LINK` | RC link and telemetry | F5 | H2 | T | `team/F5/claims.json` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-COMPASS` | Compass and GPS | F3 | F2 H1 | T+I | `subsystems/avionics/SPEC.md` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TRANSPORT` | One-piece transport | D7 | C1 A1 | A+D | `team/A1/claims.json` `subsystems/transport/SPEC.md` | 1/2 | `CL-A1-BOX-FIT` `CL-A4-FIELD-DISCONNECTS` | +0 % | `CHECKED` |
| `R-FIELD-SETUP` | Field set-up time | D7 | G4 E1 | D | `subsystems/transport/SPEC.md` `subsystems/transport/BUILD.md` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-CAR-FIT` | Box fits two cars | D7 | A1 | D | `subsystems/transport/SPEC.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |
| `R-PROCESS` | Build processes | G1 | G2 G3 | I | `team/G1/PROCESS-PLAN.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |
| `R-BUILD-HOURS` | Build hours | I2 | G4 | A+D | `team/I2/SCHEDULE.md` `team/G4/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-SCHEDULE` | Milestones | I2 | I1 H3 | I | `team/I2/SCHEDULE.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |
| `R-CRASH-REPAIR` | Crash repair | G1 | I1 G2 | I+D | `team/G1/PROCESS-PLAN.md` `team/I1/BOM.csv` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-BUDGET` | Budget $2 000 | I1 | A1 | A | `team/I1/BOM.csv` `team/A1/claims.json` | 1/2 | `CL-A1-RESERVE` | +4 % | `CHECKED` |
| `R-RESERVE` | Crash reserve | I1 | A1 | A | `team/I1/BOM.csv` `team/A1/claims.json` | 1/2 | `CL-A1-RESERVE` | +4 % | `CHECKED` |
| `R-NO-FLOATING` | Every part connected | A4 | A5 | A | `interfaces/REPORT.md` `fusion/check.py` | 2/2 | — | — | `UNVERIFIED` (no claim) |
| `R-JOINT-STACK` | Joint stacks | C6 | A4 G4 | I | `team/C6/JOINTS.md` `interfaces/interfaces.json` | 1/2 | — | — | `UNVERIFIED` (no claim) |
| `R-PROOF-BUILD` | Proof chain builds | J2 | A2 | A | `proofs/out/CHAIN.md` `team/A2/VERIFICATION-MATRIX.md` | 2/2 | — | — | `UNVERIFIED` (no claim) |
| `R-LEGAL` | FAA and university compliance | H3 | A1 | I | `team/H3/COMPLIANCE.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |
| `R-SITE` | Site rules and flight card | H3 | H2 | I+D | `team/H3/FLIGHT-CARD.md` `team/H3/COMPLIANCE.md` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-BATT-HANDLING` | Battery handling | H3 | E2 | I | `team/H3/BATTERY-PROCEDURE.md` `team/E2/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-PILOT` | Pilot readiness | H2 | F4 | I | `team/H2/PILOT-LOG.md` `subsystems/flight-software/SITL-PLAN.md` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TWIN` | Foam-board twin gate | H2 | F4 B3 E1 | D | `team/H2/TWIN-REPORT.md` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TEST-ORDER` | Test gates in order | H2 | H1 H3 | D | `team/H2/FLIGHT-TEST-PLAN.md` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-WIND-MEASURE` | RFS wind measured | H3 | B1 | T | `team/H3/WIND-RFS.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |

## By owner

| Owner | Requirements | Open (no claim yet) |
|---|---|---|
| A1 | `R-CONFIG` | — |
| A3 | `R-MASS-GATE` `R-MASS-ALLOC` `R-CG-RANGE` | `R-MASS-ALLOC` `R-CG-RANGE` |
| A4 | `R-NO-FLOATING` | `R-NO-FLOATING` |
| A5 | `R-ENVELOPE` | `R-ENVELOPE` |
| B1 | `R-MISSION` `R-TRANSITION` `R-WIND` `R-GUST-LEAN` | `R-MISSION` `R-WIND` `R-GUST-LEAN` |
| B2 | `R-STALL` | — |
| B3 | `R-STATIC-MARGIN` `R-DIRECTIONAL` `R-HOVER-AUTHORITY` `R-CRUISE-AUTHORITY` `R-ELEVON-AREA` | `R-DIRECTIONAL` `R-HOVER-AUTHORITY` `R-CRUISE-AUTHORITY` |
| C1 | `R-LOADS` | `R-LOADS` |
| C2 | `R-STRUCT-MARGIN` | `R-STRUCT-MARGIN` |
| C3 | `R-PACK-RETENTION` | `R-PACK-RETENTION` |
| C4 | `R-FIN-TUBE-JOINT` `R-VIBRATION` | `R-FIN-TUBE-JOINT` `R-VIBRATION` |
| C5 | `R-TIPOVER` `R-LANDING-IMPACT` | `R-LANDING-IMPACT` |
| C6 | `R-JOINT-STACK` | `R-JOINT-STACK` |
| D3 | `R-PROP-CLEAR` | — |
| D6 | `R-SERVO-TORQUE` | `R-SERVO-TORQUE` |
| D7 | `R-TRANSPORT` `R-FIELD-SETUP` `R-CAR-FIT` | `R-FIELD-SETUP` `R-CAR-FIT` |
| E1 | `R-HOVER-TW` `R-ESC-CURRENT` | `R-ESC-CURRENT` |
| E2 | `R-PACK-MASS` | `R-PACK-MASS` |
| E3 | `R-THERMAL` | `R-THERMAL` |
| F1 | `R-DISCONNECT` `R-AVIONICS-POWER` | `R-AVIONICS-POWER` |
| F2 | `R-HARNESS-INSTALL` | `R-HARNESS-INSTALL` |
| F3 | `R-AIRSPEED` `R-FC-STABLE` `R-COMPASS` | `R-AIRSPEED` `R-FC-STABLE` `R-COMPASS` |
| F4 | `R-FSW-PARAMS` `R-ARM-KILL` `R-FAILSAFES` | `R-FSW-PARAMS` `R-ARM-KILL` `R-FAILSAFES` |
| F5 | `R-RC-LINK` | `R-RC-LINK` |
| G1 | `R-PROCESS` `R-CRASH-REPAIR` | `R-PROCESS` `R-CRASH-REPAIR` |
| H2 | `R-PILOT` `R-TWIN` `R-TEST-ORDER` | `R-PILOT` `R-TWIN` `R-TEST-ORDER` |
| H3 | `R-LEGAL` `R-SITE` `R-BATT-HANDLING` `R-WIND-MEASURE` | `R-LEGAL` `R-SITE` `R-BATT-HANDLING` `R-WIND-MEASURE` |
| I1 | `R-BUDGET` `R-RESERVE` | — |
| I2 | `R-BUILD-HOURS` `R-SCHEDULE` | `R-BUILD-HOURS` `R-SCHEDULE` |
| J2 | `R-PROOF-BUILD` | `R-PROOF-BUILD` |

## How to verify this matrix

1. `python -I redesign/proofs/build_graph.py` must print `OK` (the statuses above come from its `graph.json`).
2. `python -I redesign/team/A2/build_requirements.py` must exit 0: every P1–P25 line maps to a requirement, every `R-…` id in the graph has a row, no id is defined twice.
3. Before CDR every row has ≥ 1 claim; before first flight `build_graph.py --strict` passes (`R-PROOF-BUILD`).
