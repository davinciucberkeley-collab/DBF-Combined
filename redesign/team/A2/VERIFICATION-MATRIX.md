# Verification matrix — K09-L quad tailsitter

Generated 2026-11-09 17:40 UTC by `team/A2/build_requirements.py` from `team/A2/requirements.json` and `proofs/out/graph.json` (graph built 2026-11-09 17:40 UTC, with errors in other roles scripts). Status is computed by `proofs/build_graph.py` from the claims that name each requirement in `verifies`; nobody types it. Re-run: `python -I redesign/team/A2/build_requirements.py`.

## Summary

| Requirements | With ≥ 1 claim | `VERIFIED` | `CHECKED` | `PROPOSED` | `UNVERIFIED` | `FAIL` |
|---|---|---|---|---|---|---|
| 58 | 27 | 0 | 3 | 1 | 54 | 11 |

Failing now: `R-MISSION` (CL-B1-CRUISE-P is UNVERIFIED; CL-B1-CRUISE-TIME is UNVERIFIED; CL-B1-CRUISE-TIME-PESS is UNVERIFIED; CL-E1-CRUISE-P-55 is UNVERIFIED; CL-E2-CRUISE-MIN-BASE is UNVERIFIED; CL-E2-CRUISE-MIN-PESS is UNVERIFIED; CL-E2-CRUISE-TO-LOW-PESS: FAILS: margin -7.3% (4.636 min vs >= 5 min)), `R-STALL` (CL-A1-STALL-GATE is UNVERIFIED; CL-B1-VS-GATE is UNVERIFIED; CL-B1-VS-SIZED is UNVERIFIED; CL-B2-STALL-GATE is UNVERIFIED; CL-B2-STALL-GATE-FWD: FAILS: margin -0.5% (12.06 m/s vs <= 12 m/s); CL-B3-VS-TRIM: FAILS: margin -6.1% (12.73 m/s vs <= 12 m/s)), `R-TRANSITION` (CL-A1-TRANSITION-GATE is UNVERIFIED; CL-B1-VT-GATE is UNVERIFIED; CL-B1-CORR-THRUST is UNVERIFIED; CL-B1-TRANS-ALT-LOSS is UNVERIFIED; CL-B1-TRANS-THRUST is UNVERIFIED; CL-B2-TRANSITION-GATE is UNVERIFIED; CL-B2-TRANSITION-GATE-FWD is UNVERIFIED; CL-B3-VT-TRIM: FAILS: margin -3.4% (16.55 m/s vs <= 16 m/s); CL-B3-TRANS-PITCH-USE is UNVERIFIED; CL-E1-CORRIDOR-45 is UNVERIFIED; CL-E1-CORRIDOR-55 is UNVERIFIED), `R-STATIC-MARGIN` (CL-A5-LAYOUT-CG-X: FAILS: margin -8.3% (0.05307 m vs <= 0.049 m); CL-B3-SM-TARGET is UNVERIFIED), `R-WIND` (CL-B1-LEAN-5MS is UNVERIFIED; CL-B1-WIND-HOVER-MAX is UNVERIFIED; CL-B1-GUST-8-THRUST is UNVERIFIED; CL-B1-GROUND-TIP-WIND is UNVERIFIED; CL-B3-HOVER-PITCH-RATIO is UNVERIFIED; CL-B3-HOVER-ROLL-RATIO is UNVERIFIED; CL-B3-HOVER-YAW-RATIO: FAILS: margin -46.1% (1.079 vs >= 2); CL-B3-HOVER-YAW-RATIO-CANT is UNVERIFIED), `R-ESC-CURRENT` (CL-E1-HOVER-I is UNVERIFIED; CL-E1-HOVER-I-55 is UNVERIFIED; CL-E1-IMAX-148: FAILS: margin -3.5% (37.25 A vs <= 36 A); CL-E1-IMAX-168: FAILS: margin -1.3% (45.57 A vs <= 45 A); CL-E1-IMAX-168-55: FAILS: margin -14.6% (51.56 A vs <= 45 A); CL-E1-IMAX-148-55: FAILS: margin -17.9% (42.43 A vs <= 36 A); CL-E1-ILIM-I is UNVERIFIED), `R-LOADS` (CL-C1-T-CAP: FAILS: margin -18.4% (21.08 N vs <= 17.8 N); CL-C1-T-LIMIT is UNVERIFIED; CL-C1-VD: FAILS: margin -21.5% (27.21 m/s vs <= 22.4 m/s); CL-C1-N-LIMIT-POS: FAILS: margin -10.5% (3.316 vs <= 3); CL-C1-N-LIMIT-NEG is UNVERIFIED; CL-C1-GUST-N-POS: FAILS: margin -10.5% (3.316 vs <= 3); CL-C1-SPAR-MB-ULT is UNVERIFIED; CL-C1-SPAR-MX-ULT is UNVERIFIED; CL-C1-SPAR-MZ-ULT is UNVERIFIED; CL-C1-WING-TORSION-ULT is UNVERIFIED; CL-C1-WING-SHEAR-ULT is UNVERIFIED; CL-C1-FINJOINT-F-ULT is UNVERIFIED; CL-C1-FINJOINT-M-ULT is UNVERIFIED; CL-C1-FINJOINT-M-DESIGN is UNVERIFIED; CL-C1-FINHALF-MB-ULT is UNVERIFIED; CL-C1-MOUNT-F-ULT is UNVERIFIED; CL-C1-MOUNT-M-ULT is UNVERIFIED; CL-C1-MOTOR-F-ULT is UNVERIFIED; CL-C1-POD-F-ULT is UNVERIFIED; CL-C1-FOOT-F-ULT is UNVERIFIED; CL-C1-TRANSPORT-N-ALLOW is UNVERIFIED; CL-C1-FINJOINT-M-FLIGHT-LIM is UNVERIFIED; CL-C1-DROP-HEIGHT-ALLOW is UNVERIFIED; CL-C1-CRADLE-STROKE-REQ is UNVERIFIED; CL-D7-CRADLE-STROKE is UNVERIFIED; CL-D7-DROP-N is UNVERIFIED), `R-VIBRATION` (CL-J1-TUBE-MODE-SEP: FAILS: margin -91.4% (0.0172 vs >= 0.2)), `R-LANDING-IMPACT` (CL-C1-N-LAND-STROKE-MIN: FAILS: margin -1.1% (6.069 vs <= 6); CL-C1-WINGTIP-STRIKE-ANGLE is UNVERIFIED), `R-DISCONNECT` (CL-J1-DISCONNECT-REQ is UNVERIFIED; CL-J1-DISCONNECT-REQ-PESS is UNVERIFIED; CL-J1-XT60-CONT-PESS: FAILS: margin -6.3% (35 A vs >= 37.36 A); CL-J1-XT60-BURST: FAILS: margin -50.0% (60 A vs >= 120 A)), `R-TRANSPORT` (CL-D7-CRADLE-STROKE is UNVERIFIED; CL-D7-DROP-N is UNVERIFIED; CL-D7-BOX-H-REQ is UNVERIFIED; CL-D7-TUBE-CLEAR-DROP is UNVERIFIED; CL-D7-SIDE-CLEAR is UNVERIFIED; CL-D7-TIP-PAD-GAP is UNVERIFIED; CL-D7-A1-BOX-DROP-ALLOW: FAILS: margin -41.5% (0.1755 m vs >= 0.3 m); CL-D7-LOADED-MASS is UNVERIFIED).

Method: A analysis · I inspection · T test · D demonstration. On disk: evidence files that exist today / listed. `UNVERIFIED (no claim)` means the owner has not yet emitted a claim naming the id.

## Matrix

| ID | Title | Owner | Support | Method | Evidence | On disk | Claims | Margin | Status |
|---|---|---|---|---|---|---|---|---|---|
| `R-CONFIG` | Configuration K09-L | A1 | A4 | I | `README.md` `team/A1/claims.json` | 2/2 | `CL-A1-WING-AREA` | — | `CHECKED` |
| `R-MISSION` | Mission endurance | B1 | E2 H2 | A+T | `team/B1/claims.json` `team/E2/claims.json` `team/H2/logs/` | 2/3 | `CL-B1-CRUISE-P` `CL-B1-CRUISE-TIME` `CL-B1-CRUISE-TIME-PESS` `CL-E1-CRUISE-P-55` `CL-E2-CRUISE-MIN-BASE` `CL-E2-CRUISE-MIN-PESS` `CL-E2-CRUISE-TO-LOW-PESS` | -7 % | `UNVERIFIED` `FAIL` |
| `R-ENVELOPE` | Props-off envelope | A5 | D1 D3 | A+I | `fusion/check.py` `team/A5/claims.json` | 2/2 | — | — | `UNVERIFIED` (no claim) |
| `R-STALL` | Stall speed | B2 | B1 H2 | A+T | `team/B2/claims.json` `team/A1/claims.json` `team/H2/logs/` | 2/3 | `CL-A1-STALL-GATE` `CL-B1-VS-GATE` `CL-B1-VS-SIZED` `CL-B2-STALL-GATE` `CL-B2-STALL-GATE-FWD` `CL-B3-VS-TRIM` | -6 % | `UNVERIFIED` `FAIL` |
| `R-TRANSITION` | Transition speed | B1 | F4 H2 | A+T | `team/B1/claims.json` `team/H2/logs/` | 1/2 | `CL-A1-TRANSITION-GATE` `CL-B1-VT-GATE` `CL-B1-CORR-THRUST` `CL-B1-TRANS-ALT-LOSS` `CL-B1-TRANS-THRUST` `CL-B2-TRANSITION-GATE` `CL-B2-TRANSITION-GATE-FWD` `CL-B3-VT-TRIM` `CL-B3-TRANS-PITCH-USE` `CL-E1-CORRIDOR-45` `CL-E1-CORRIDOR-55` | -3 % | `UNVERIFIED` `FAIL` |
| `R-MASS-GATE` | Mass gate 2.6 kg | A3 | H1 | A+T | `MASS-CG.md` `team/A1/claims.json` `team/H1/claims.json` | 2/3 | `CL-A1-MASS-SIZED` `CL-A1-RESERVE-COVERS` `CL-A1-ALLOC-GATE` `CL-A3-MASS-BASIC` `CL-A3-MASS-PREDICTED` `CL-A3-GATE-MARGIN` | +2 % | `UNVERIFIED` |
| `R-MASS-ALLOC` | Subsystem mass allocations | A3 | all designers | A+T | `MASS-CG.md` `team/A3/claims.json` | 2/2 | `CL-A3-ALLOC-WORST` | +0 % | `UNVERIFIED` |
| `R-CG-RANGE` | As-built CG range | A3 | B3 H1 | A+T | `MASS-CG.md` `team/A3/claims.json` `team/H1/claims.json` | 2/3 | `CL-A3-CG-X-RANGE` `CL-A3-CG-Z-RANGE` | +53 % | `UNVERIFIED` |
| `R-HOVER-SPLIT` | Hover pitch-trim thrust split | A3 | B3 F4 H2 | A+T | `MASS-CG.md` `team/A3/claims.json` `team/H2/logs/` | 2/3 | — | — | `UNVERIFIED` (no claim) |
| `R-STATIC-MARGIN` | Static margin | B3 | H2 | A+T | `team/B3/claims.json` `team/H2/logs/` | 1/2 | `CL-A5-LAYOUT-CG-X` `CL-B3-SM-TARGET` | -8 % | `UNVERIFIED` `FAIL` |
| `R-HOVER-TW` | Hover thrust-to-weight | E1 | H1 | A+T | `team/E1/claims.json` `team/A1/claims.json` `team/H1/claims.json` | 2/3 | `CL-A1-HOVER-TW-GATE` `CL-A1-HOVER-TW-SAG` `CL-B1-HOVER-THROTTLE` `CL-B1-HOVER-TW-SAG` `CL-B4-TW-CAP` `CL-E1-TW-TABLE` `CL-E1-ILIM-TW-FRESH` `CL-E1-TW-WORST` `CL-E2-TW-SAG-WORST` | +2 % | `UNVERIFIED` |
| `R-WIND` | Wind | B1 | H2 H3 | A+D | `team/B1/claims.json` `team/H2/logs/` | 1/2 | `CL-B1-LEAN-5MS` `CL-B1-WIND-HOVER-MAX` `CL-B1-GUST-8-THRUST` `CL-B1-GROUND-TIP-WIND` `CL-B3-HOVER-PITCH-RATIO` `CL-B3-HOVER-ROLL-RATIO` `CL-B3-HOVER-YAW-RATIO` `CL-B3-HOVER-YAW-RATIO-CANT` `CL-D5-PAD-MU` | -46 % | `UNVERIFIED` `FAIL` |
| `R-GUST-LEAN` | 8 m/s gust survive-and-land | B1 | F4 | A | `team/B1/claims.json` `subsystems/flight-software/params/` | 1/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TIPOVER` | Stance tip-over | C5 | H1 | A+T | `team/C5/claims.json` `team/A1/claims.json` `team/H1/claims.json` | 1/3 | `CL-A1-TIPOVER` `CL-B1-GROUND-TIP-WIND` `CL-C1-TIPOVER-WITH-FOOT` `CL-D5-TIPOVER-NARROW` | +2 % | `UNVERIFIED` |
| `R-DIRECTIONAL` | Directional stability in cruise | B3 | J1 H2 | A+T | `team/B3/claims.json` `team/J1/claims.json` `team/H2/logs/` | 2/3 | `CL-J1-FIN-YAW-ARM` | — | `UNVERIFIED` |
| `R-HOVER-AUTHORITY` | Hover control authority | B3 | A3 H2 | A+D | `team/B3/claims.json` `team/H2/logs/` | 1/2 | — | — | `UNVERIFIED` (no claim) |
| `R-CRUISE-AUTHORITY` | Elevon authority in cruise | B3 | B2 H2 | A+T | `team/B3/claims.json` `team/H2/logs/` | 1/2 | — | — | `UNVERIFIED` (no claim) |
| `R-ELEVON-AREA` | Elevon area | B3 | D1 H2 | A+D | `team/A1/claims.json` `team/B3/claims.json` `team/H2/logs/` | 2/3 | `CL-A1-ELEVON-FRAC` `CL-A5-ELEVON-GAP-MIN` `CL-B3-ELEVON-FRAC-MAX` | +15 % | `UNVERIFIED` |
| `R-SERVO-TORQUE` | Elevon servo torque | D6 | B2 H1 | A+T | `team/B2/claims.json` `subsystems/mechanisms/SPEC.md` `team/H1/claims.json` | 1/3 | — | — | `UNVERIFIED` (no claim) |
| `R-PROP-CLEAR` | Prop clearance | D3 | B4 A5 | A+I | `team/A1/claims.json` `fusion/check.py` `subsystems/fins/SPEC.md` | 2/3 | `CL-A1-PROP-CLEAR` `CL-B4-GAP-V` | +38 % | `UNVERIFIED` |
| `R-AIRSPEED` | Airspeed sensor placement and accuracy | F3 | B4 H2 | A+T | `subsystems/avionics/SPEC.md` `team/B4/claims.json` `team/H2/logs/` | 1/3 | — | — | `UNVERIFIED` (no claim) |
| `R-ESC-CURRENT` | Motor and ESC current with the pack-current limiter | E1 | F4 F1 H1 | I+A+T | `subsystems/flight-software/params/` `team/E1/claims.json` `team/H1/claims.json` | 1/3 | `CL-E1-HOVER-I` `CL-E1-HOVER-I-55` `CL-E1-IMAX-148` `CL-E1-IMAX-168` `CL-E1-IMAX-168-55` `CL-E1-IMAX-148-55` `CL-E1-ILIM-I` | -18 % | `UNVERIFIED` `FAIL` |
| `R-PACK-MASS` | Flight pack mass and capacity | E2 | A3 | T | `team/E2/claims.json` | 1/1 | `CL-E2-PACK-MASS` | +19 % | `PROPOSED` |
| `R-THERMAL` | Thermal limits | E3 | H1 H2 | A+T | `team/E3/claims.json` `team/H1/claims.json` | 0/2 | `CL-E1-HOVER-DT` `CL-E2-PACK-T-END` | +10 % | `UNVERIFIED` |
| `R-LOADS` | Load cases defined | C1 | B1 C5 | A | `team/C1/LOADS.md` `team/C1/claims.json` | 2/2 | `CL-C1-T-CAP` `CL-C1-T-LIMIT` `CL-C1-VD` `CL-C1-N-LIMIT-POS` `CL-C1-N-LIMIT-NEG` `CL-C1-GUST-N-POS` `CL-C1-SPAR-MB-ULT` `CL-C1-SPAR-MX-ULT` `CL-C1-SPAR-MZ-ULT` `CL-C1-WING-TORSION-ULT` `CL-C1-WING-SHEAR-ULT` `CL-C1-FINJOINT-F-ULT` `CL-C1-FINJOINT-M-ULT` `CL-C1-FINJOINT-M-DESIGN` `CL-C1-FINHALF-MB-ULT` `CL-C1-MOUNT-F-ULT` `CL-C1-MOUNT-M-ULT` `CL-C1-MOTOR-F-ULT` `CL-C1-POD-F-ULT` `CL-C1-FOOT-F-ULT` `CL-C1-TRANSPORT-N-ALLOW` `CL-C1-FINJOINT-M-FLIGHT-LIM` `CL-C1-DROP-HEIGHT-ALLOW` `CL-C1-CRADLE-STROKE-REQ` `CL-D7-CRADLE-STROKE` `CL-D7-DROP-N` | -21 % | `UNVERIFIED` `FAIL` |
| `R-STRUCT-MARGIN` | Structural margins | C2 | C3 C4 C5 C6 H1 | A+T | `team/C2/claims.json` `team/C3/claims.json` `team/C4/claims.json` `team/C5/claims.json` `team/C6/claims.json` `team/H1/claims.json` | 0/6 | — | — | `UNVERIFIED` (no claim) |
| `R-FIN-TUBE-JOINT` | Fin-tube-block joint | C4 | D3 C6 G3 | A+I | `subsystems/fins/SPEC.md` `team/C4/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-VIBRATION` | Motor-tube vibration | C4 | E1 H1 H2 | A+T | `team/C4/claims.json` `team/H1/claims.json` `team/H2/logs/` | 0/3 | `CL-J1-TUBE-MODE-SEP` | -91 % | `UNVERIFIED` `FAIL` |
| `R-PACK-RETENTION` | Pack retained in a crash | C3 | D2 H1 | A+T | `subsystems/pod/SPEC.md` `team/C3/claims.json` `team/H1/claims.json` | 0/3 | `CL-C1-CRASH-N` `CL-C1-PACK-CRASH-LOAD` | +6 % | `UNVERIFIED` |
| `R-LANDING-IMPACT` | Fin-tip landing | C5 | D5 H1 | A+T | `subsystems/landing/SPEC.md` `team/C5/claims.json` `team/H1/claims.json` | 0/3 | `CL-C1-N-LAND-STROKE-MIN` `CL-C1-WINGTIP-STRIKE-ANGLE` | -1 % | `UNVERIFIED` `FAIL` |
| `R-DISCONNECT` | Connectors carry the current | F1 | E1 H1 | A+T | `subsystems/power/SPEC.md` `team/F1/claims.json` `team/H1/claims.json` | 0/3 | `CL-J1-DISCONNECT-REQ` `CL-J1-DISCONNECT-REQ-PESS` `CL-J1-XT60-CONT` `CL-J1-XT60-CONT-PESS` `CL-J1-XT60-BURST` `CL-J1-AS150U-CONT` `CL-J1-AS150U-BURST` | -50 % | `UNVERIFIED` `FAIL` |
| `R-AVIONICS-POWER` | Avionics power | F1 | F3 H1 | A+T | `subsystems/power/SPEC.md` `team/F1/claims.json` `team/H1/claims.json` | 0/3 | — | — | `UNVERIFIED` (no claim) |
| `R-HARNESS-INSTALL` | Wiring is an installation | F2 | A4 | I | `subsystems/harness/SPEC.md` `subsystems/harness/interfaces.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FC-STABLE` | Stable autopilot build | F3 | F4 | I+D | `subsystems/avionics/SPEC.md` `team/F3/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FSW-PARAMS` | Tailsitter parameter file | F4 | E1 H1 | I+D | `subsystems/flight-software/SPEC.md` `subsystems/flight-software/params/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-ARM-KILL` | Arming and emergency stop | F4 | H1 H3 | T | `subsystems/flight-software/SPEC.md` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-FAILSAFES` | Failsafes and geofence | F4 | H1 H3 | T+D | `subsystems/flight-software/SPEC.md` `subsystems/flight-software/SITL-PLAN.md` `team/H1/claims.json` | 0/3 | `CL-E2-BATT-CRT-MAH` `CL-E2-BATT-LOW-MAH` | — | `UNVERIFIED` |
| `R-RC-LINK` | RC link and telemetry | F5 | H2 | T | `team/F5/claims.json` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-COMPASS` | Compass and GPS | F3 | F2 H1 | T+I | `subsystems/avionics/SPEC.md` `team/H1/claims.json` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TRANSPORT` | One-piece transport | D7 | C1 A1 | A+D | `team/A1/claims.json` `subsystems/transport/SPEC.md` | 1/2 | `CL-A1-BOX-FIT` `CL-A4-FIELD-DISCONNECTS` `CL-D5-BOX-SLACK` `CL-D7-CRADLE-STROKE` `CL-D7-DROP-N` `CL-D7-BOX-H-REQ` `CL-D7-TUBE-CLEAR-DROP` `CL-D7-SIDE-CLEAR` `CL-D7-TIP-PAD-GAP` `CL-D7-A1-BOX-DROP-ALLOW` `CL-D7-LOADED-MASS` | -42 % | `UNVERIFIED` `FAIL` |
| `R-FIELD-SETUP` | Field set-up time | D7 | G4 E1 | D | `subsystems/transport/SPEC.md` `subsystems/transport/BUILD.md` | 0/2 | `CL-D7-SETUP-MIN` | +12 % | `UNVERIFIED` |
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
| `R-BATT-HANDLING` | Battery handling | H3 | E2 | I | `team/H3/BATTERY-PROCEDURE.md` `team/E2/claims.json` | 1/2 | — | — | `UNVERIFIED` (no claim) |
| `R-PILOT` | Pilot readiness | H2 | F4 | I | `team/H2/PILOT-LOG.md` `subsystems/flight-software/SITL-PLAN.md` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TWIN` | Foam-board twin gate | H2 | F4 B3 E1 | D | `team/H2/TWIN-REPORT.md` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-TEST-ORDER` | Test gates in order | H2 | H1 H3 | D | `team/H2/FLIGHT-TEST-PLAN.md` `team/H2/logs/` | 0/2 | — | — | `UNVERIFIED` (no claim) |
| `R-WIND-MEASURE` | RFS wind measured | H3 | B1 | T | `team/H3/WIND-RFS.md` | 0/1 | — | — | `UNVERIFIED` (no claim) |

## By owner

| Owner | Requirements | Open (no claim yet) |
|---|---|---|
| A1 | `R-CONFIG` | — |
| A3 | `R-MASS-GATE` `R-MASS-ALLOC` `R-CG-RANGE` `R-HOVER-SPLIT` | `R-HOVER-SPLIT` |
| A4 | `R-NO-FLOATING` | `R-NO-FLOATING` |
| A5 | `R-ENVELOPE` | `R-ENVELOPE` |
| B1 | `R-MISSION` `R-TRANSITION` `R-WIND` `R-GUST-LEAN` | `R-GUST-LEAN` |
| B2 | `R-STALL` | — |
| B3 | `R-STATIC-MARGIN` `R-DIRECTIONAL` `R-HOVER-AUTHORITY` `R-CRUISE-AUTHORITY` `R-ELEVON-AREA` | `R-HOVER-AUTHORITY` `R-CRUISE-AUTHORITY` |
| C1 | `R-LOADS` | — |
| C2 | `R-STRUCT-MARGIN` | `R-STRUCT-MARGIN` |
| C3 | `R-PACK-RETENTION` | — |
| C4 | `R-FIN-TUBE-JOINT` `R-VIBRATION` | `R-FIN-TUBE-JOINT` |
| C5 | `R-TIPOVER` `R-LANDING-IMPACT` | — |
| C6 | `R-JOINT-STACK` | `R-JOINT-STACK` |
| D3 | `R-PROP-CLEAR` | — |
| D6 | `R-SERVO-TORQUE` | `R-SERVO-TORQUE` |
| D7 | `R-TRANSPORT` `R-FIELD-SETUP` `R-CAR-FIT` | `R-CAR-FIT` |
| E1 | `R-HOVER-TW` `R-ESC-CURRENT` | — |
| E2 | `R-PACK-MASS` | — |
| E3 | `R-THERMAL` | — |
| F1 | `R-DISCONNECT` `R-AVIONICS-POWER` | `R-AVIONICS-POWER` |
| F2 | `R-HARNESS-INSTALL` | `R-HARNESS-INSTALL` |
| F3 | `R-AIRSPEED` `R-FC-STABLE` `R-COMPASS` | `R-AIRSPEED` `R-FC-STABLE` `R-COMPASS` |
| F4 | `R-FSW-PARAMS` `R-ARM-KILL` `R-FAILSAFES` | `R-FSW-PARAMS` `R-ARM-KILL` |
| F5 | `R-RC-LINK` | `R-RC-LINK` |
| G1 | `R-PROCESS` `R-CRASH-REPAIR` | `R-PROCESS` `R-CRASH-REPAIR` |
| H2 | `R-PILOT` `R-TWIN` `R-TEST-ORDER` | `R-PILOT` `R-TWIN` `R-TEST-ORDER` |
| H3 | `R-LEGAL` `R-SITE` `R-BATT-HANDLING` `R-WIND-MEASURE` | `R-LEGAL` `R-SITE` `R-BATT-HANDLING` `R-WIND-MEASURE` |
| I1 | `R-BUDGET` `R-RESERVE` | — |
| I2 | `R-BUILD-HOURS` `R-SCHEDULE` | `R-BUILD-HOURS` `R-SCHEDULE` |
| J2 | `R-PROOF-BUILD` | `R-PROOF-BUILD` |

## Retired limit ids still cited

These scripts cite an `ASM-A2-…` id that was retired by D-14. A2 emits a thin alias (value copied from `params.json`) so they build; each owner points at the `P:requirements.<key>` instead, then the alias goes.

| Retired id | Point at | Files |
|---|---|---|
| `ASM-A2-SERVO-TORQUE-FACTOR` | `P:requirements.servo_torque_factor` | `redesign/team/B2/claims.json` `redesign/team/B2/wing_claims.py` |
| `ASM-A2-PACK-CAPACITY-FRAC` | `P:requirements.pack_capacity_min_frac` | `redesign/team/E2/claims.json` `redesign/team/E2/energy_claims.py` |

## How to verify this matrix

1. `python -I redesign/proofs/build_graph.py` must print `OK` (the statuses above come from its `graph.json`).
2. `python -I redesign/team/A2/build_requirements.py` must exit 0: every P1–P25 line maps to a requirement, every `R-…` id in the graph has a row, no id is defined twice, every `{P:key}` and source key exists in `params.json`, no row names a retired limit.
3. Before CDR every row has ≥ 1 claim; before first flight `build_graph.py --strict` passes (`R-PROOF-BUILD`).
