# flight-software — tuning plan

Order follows CONFIGURATION.md (twin first, fixed-wing tune before any transition) and the ArduPilot tailsitter
tuning guide. Each step has a stop condition; a failed step is repeated, not skipped. Owner F4 with H1/H2.

| Step | Where | What | Parameters touched | Done when |
|---|---|---|---|---|
| 1 | bench, **props off** | load `K09L.param`; motor test A–D; elevon directions in FBWA and QSTABILIZE; failsafes with the transmitter off and a bench supply | `SERVOn_REVERSED`, `SERVO5/6_MIN/MAX/TRIM` for ±25° | map as SPEC.md; elevons move the right way; RC loss → QLAND shown in the HUD |
| 2 | thrust stand (H1), one station | full stick in QSTABILIZE, fresh pack; ESC rpm telemetry | `Q_M_SPIN_MAX`, `Q_M_SPIN_MIN`/`ARM` (from the stand), `SERVO_BLH_POLES` | rpm ≤ 9 350; pack ≤ 100 A on four motors (R-ESC-CURRENT) |
| 3 | twin / tethered hover | hover 60 s, log `INS_LOG_BAT`; set notch from the FFT | `INS_HNTCH_*`, `Q_M_THST_HOVER` (learnt) | no gyro peak at 1P/2P; VIBE < 30 m/s², Clip 0 |
| 4 | tethered hover | sharp pitch and yaw stick inputs → feed-forward from log, then D and P by oscillate-and-halve; QAUTOTUNE roll only | `Q_A_RAT_*` | no oscillation; yaw holds in 5 m/s fan or wind |
| 5 | free hover | QLOITER, landings at 0.5 m/s | `Q_WVANE_GAIN`, `Q_LOIT_*` if needed | hold within 1 m in 5 m/s (R-TWIN) |
| 6 | hand-launch, FBWA | plain flying wing, motors as throttle; AUTOTUNE pitch then roll; trim elevons (expect −6.8° up at 15 m/s) | `RLL_RATE_*`, `PTCH_RATE_*`, `TRIM`, `YAW2SRV_DAMP`, `RUDD_DT_GAIN` | yaw doublet damped (T-B3-YAW-DOUBLET); TECS holds 16 m/s |
| 7 | transition at ≥ 50 m | FBWA from QHOVER, 12 °/s, morning ≤ 5 m/s; abort to QHOVER on any doubt | `Q_TAILSIT_RAT_FW`, `Q_TAILSIT_ANGLE` | ≥ 15.5 m/s, height loss ≤ 10 m (T-B1-TRANSITION-LOG) |
| 8 | back-transition at ≥ 50 m | QHOVER from cruise | `Q_TAILSIT_RAT_VT`, `Q_TAILSIT_THR_VT` | no tumble, height loss ≤ 10 m |
| 9 | fresh-pack flights | raise `Q_TAILSIT_RAT_FW` to 20 °/s only if step-7 logs show peak output ≤ 0.7 | `Q_TAILSIT_RAT_FW` | B1's 0.59 fresh-pack fraction confirmed |

Rules: one parameter change per flight; every change logged with the log number in `team/F4/sitl/RESULTS.md` or the
flight log; the parameter file is re-saved and re-checked (`fsw_check.py`) after each session.
