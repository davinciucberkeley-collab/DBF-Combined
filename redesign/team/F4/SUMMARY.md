# F4 — flight-control software

Status `PROPOSED`, revision F4-R1, 2026-11-09. Deliverables in `subsystems/flight-software/`: `K09L.param` (116
lines, every line commented), `SPEC.md` (map, transition, failsafes), `SITL-PLAN.md` (15 cases incl. motor-failure
injection), `TUNING-PLAN.md`, `params.json`. Check: `python -I redesign/team/F4/fsw_check.py` → lint OK, mirror OK,
19 claims, none failing; `build_graph.py` shows no F4 error (B1/B3 drift is theirs).

## Forwarded requests, resolved

| Request | Set | Unit | Claim | Status |
|---|---|---|---|---|
| `Q_M_BAT_CURR_MAX`, `_VOLT_MAX/MIN` (CR-E1-08) | 100, 16.8 / 13.2; TC 1 s | A, V | R-ESC-CURRENT | `UNVERIFIED` |
| Output cap ~0.85 from rpm (CR-B4-06a) | `Q_M_SPIN_MAX` 0.84; FW `THR_MAX` 75 + yaw 0.0875 | — | `CL-F4-SPIN-MAX`, `CL-F4-FW-ACT-MAX` (+1 %) | `UNVERIFIED` (range 0.9–1.0 documented) |
| `AIRSPEED_CRUISE` 16, `ARSPD_FBW_MIN` (D-21), `MAX` ≤ 20 | 16, `AIRSPEED_MIN` 15, `AIRSPEED_MAX` 18 (4.5+ names) | m/s | `CL-F4-ARSPD-MIN-FACTOR` 1.26, `-CRUISE-TRANS` 1.03, `-MAX-VA` | `UNVERIFIED` (B3 R1 stall pending) |
| `Q_TAILSIT_RAT_FW` 20 | **12** (CR-B1-12 supersedes; 20 on fresh packs after logs) | °/s | B1 peak 0.76 sagged | `UNVERIFIED` |
| `Q_WP_SPEED_DN` ≤ 150, `Q_LAND_SPEED` 50 | `Q_WP_SPD_DN` 1.2, `Q_PILOT_SPD_DN` 1.2 (default would be 2.5), `Q_LAND_FINAL_SPD` 0.5; legacy cm/s lines kept | m/s | `CL-F4-DESCENT` +36 % vs VRS 1.88 | `UNVERIFIED` |
| `BATT_LOW_MAH` 2600 / `CRT` 1300 / `ARM_VOLT` 16.4 | **2 700** (E2's live claim, CR-E2-13) / 1 300 / 16.4 | mAh, V | `CL-F4-BATT-LOW`, `-CRT` | `PROPOSED` |
| Harmonic notch on ESC rpm | mode 3, 70 Hz, harmonics 1–3, bdshot on outputs 1–4 | Hz | `CL-F4-NOTCH-LOW` 1.29, `-TOP` 0.94 | `UNVERIFIED` |
| FW yaw by differential thrust (CR-B3-04, CR-J1-05) | `RUDD_DT_GAIN` 35, `YAW2SRV_DAMP` 0.1, `THR_MIN` 10 | % | `CL-F4-RUDD-DT-REQ` 31.8 % | `UNVERIFIED` |
| `Q_WVANE_ENABLE` 1 | 1, gain 1 | — | — | `PROPOSED` |
| No airspeed gain scheduling in the pitch-over | `Q_TAILSIT_GSCMSK` 1; hand-over 20° above horizon | — | — | `PROPOSED` |
| Motor map (CR-A4-12, CR-B4-04) | LR M1 CCW · UL M2 CCW · LL M3 CW · UR M4 CW (seen from nose) | — | `CL-F4-MOTOR-MAP-ERR` 0 | `CHECKED` (calc), bench `UNVERIFIED` |
| Body rates ≤ 3 rad/s (CR-C1-08) | max 150 °/s | rad/s | `CL-F4-BODY-RATE` 2.62 | `UNVERIFIED` |
| SITL plan with motor failure (CR-E1-08) | S11: `SIM_ENGINE_FAIL` + `SIM_ENGINE_MUL` 0 | — | T-F4-SITL-MOTOR-OUT | `UNVERIFIED` (no SITL) |

## Findings others depend on

| Finding | Effect |
|---|---|
| Copter frame of a tailsitter: forward = belly, so the *lower* motors are ArduPilot's front pair | wiring and props follow the map, not intuition |
| In FW the tailsitter writes throttle straight to the motors (`output_motor_mask`), bypassing `Q_M_SPIN_MAX` and the current limiter | rpm cap in FW is `THR_MAX`; SITL S4 confirms |
| FW differential thrust is symmetric about throttle; it cannot raise one side only | B3's "raise one side" is not available without Lua (CR-F4-02) |
| `AIRSPEED_MIN/MAX` are integers | 15 m/s needs B3's R1 Vs ≤ 12.5 m/s |
| Default pilot descent in QHOVER is 2.5 m/s, above VRS onset | set to 1.2 m/s |

## Open

CR-F4-01…10 filed (B3 ×2, E1/D3, F2, F3, E1/H1, A1, E2, A2, H2/H3). 50 parameter names wait for SITL S1 on the
installed build. Nothing has flown or run in SITL: all behaviour `UNVERIFIED`.
