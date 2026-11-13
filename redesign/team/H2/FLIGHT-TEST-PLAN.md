# H2 flight-test plan: K09-L (twin first, build-up, envelope expansion)

Revision H2-R1, 2026-11-13. Status `PROPOSED`; nothing in this file has been flown. Owner H2 (flight test engineer). Requirements: `R-TEST-ORDER`, `R-TWIN`, `R-PILOT` (`team/A2/REQUIREMENTS.md`).
Companions: [`TWIN-REPORT.md`](TWIN-REPORT.md) (twin report template) · [`PILOT-LOG.md`](PILOT-LOG.md) · [`templates/flight_log.csv`](templates/flight_log.csv) · [`../H3/FLIGHT-CARD.md`](../H3/FLIGHT-CARD.md) (limits, go/no-go) ·
[`../H3/COMPLIANCE.md`](../H3/COMPLIANCE.md) · [`../H3/BATTERY-PROCEDURE.md`](../H3/BATTERY-PROCEDURE.md) · [`../F5/RANGE-TEST.md`](../F5/RANGE-TEST.md) · [`../../subsystems/flight-software/TUNING-PLAN.md`](../../subsystems/flight-software/TUNING-PLAN.md) (F4: parameters touched per step) ·
[`../H1/GROUND-TEST-PLAN.md`](../H1/GROUND-TEST-PLAN.md) (ground gates) · [`../I2/SCHEDULE.md`](../I2/SCHEDULE.md) (dates).

## 1. Principles

| Rule | Why | Source |
|---|---|---|
| **Gates in order, none skipped.** A gate passes only when its pass lines are met in a logged flight (`logs/<test id>_<date>.csv` + `.bin`) | `R-TEST-ORDER` | `team/A2/REQUIREMENTS.md` |
| **Twin first** on the real motors, FC and pack: cheap airframe, the same software and a pitch-over | `CONFIGURATION.md` mandatory de-risking 1 and 2 | `CONFIGURATION.md` |
| **Fixed-wing tune as a plain flying wing before any transition** | de-risking 2 | `CONFIGURATION.md`, `TUNING-PLAN.md` steps 6-6d |
| **One parameter change per flight**, logged with the log number; gains above the step-4 ceilings or `THR_MAX` above 70 need a new F4 revision, not a field change | F4 rule | `TUNING-PLAN.md` |
| **Flights only inside the flight card**: mean wind <= 5 m/s, gust <= 8 m/s, 07:00-10:00, RFS yellow sub-fields 1-4, <= 400 ft AGL, VLOS <= 500 m, spotter, request >= 7 business days ahead (RFS 72 h), post-flight report within 3 business days | `R-SITE`, UC policy | `../H3/FLIGHT-CARD.md`, `../H3/COMPLIANCE.md` |
| **H3 gives go/no-go on the day**; the pilot can always say no | `R-TEST-ORDER` | `../H3/FLIGHT-CARD.md` |
| **One fully charged pack per sortie**; a part-used pack is never re-flown on the same day | E2 rule | `team/E2/ENERGY.md` section 4 |
| **A failed gate is repeated or sent back to its owner, never waived.** The owner re-runs the analysis, A1 decides | house rule | this plan, section 7 |

## 2. Crew and roles per flight day

| Role | Duty | Notes |
|---|---|---|
| Pilot (P4 holds it) | stick, mode switch, e-stop on switch SD (ch 9) | **named by the team (`HANDOFF.md` H6)**; has the SITL hours (`PILOT-LOG.md`); TRUST certificate and AMA membership (`R-LEGAL`) |
| Spotter | keeps eyes on the aircraft and the area; keeps non-participants out of the operations area | required by UC policy at RFS |
| Logger | writes the flight row, reads the Pocket telemetry voice calls, times flights, notes wind | `templates/flight_log.csv` |
| Safety lead (H3) | go/no-go from the flight card, packs and LiPo bag, extinguisher or sand, first aid | no role doubles with the pilot |

## 3. Before every flight day (checklist order)

1. Flight card limits met by the forecast and by **the handheld anemometer on site** (2 m, 3 readings 1 min apart; `../H3/WIND-RFS.md` method). RCMC1 real-time page as the second check.
2. Packs charged the afternoon before (4.20 V per cell only for flying mornings), logged, inspected for puffing (`../H3/BATTERY-PROCEDURE.md`); weighed once on arrival (`T-E2-WEIGH`, accept <= 592.6 g each, `CL-A1-PACK-ACCEPT`).
3. Parameter file checked: `python -I redesign/team/F4/fsw_check.py`; sha of the loaded `K09L.param` written to the flight row.
4. Field set-up from the box checklist (`subsystems/transport/CHECKLIST.md`, <= 5 min, `R-FIELD-SETUP`), **TX on before the pack plug**, arm only from the RC switch, e-stop checked, hatch closed <= 2 min before take-off (`BUILD-GUIDE.md` stage 12).
5. Range check on the first flight of each day: 25 mW, 100 m, one heading per attitude, LQ >= 0.9, no failsafe (`../F5/RANGE-TEST.md` daily check).
6. Briefing: abort words ("abort" = QHOVER if in FW, e-stop only if airborne and uncontrollable over a clear area), landing area, wind direction (wingtip into the wind for touchdown, C5 rule S2), who calls the e-stop.

## 4. Gates

The ids in the Tests column are the repo's planned tests (`kit.test` in the owner's script); this plan does not add a test, it fixes when each is run and what passes. Claim ids are the proof-chain nodes the evidence feeds.
`FAIL` entries in the proof graph (`PROOFS.md`) are inputs, not exceptions: a gate pass overwrites a model number with a measured one.

### Gate 0. Pilot readiness (`R-PILOT`) and ground gates

| Pass line | Evidence | Source |
|---|---|---|
| >= 10 h of SITL on the tailsitter model with the team's parameter file, **including QSTABILIZE recovery from a failed transition** | `PILOT-LOG.md` rows; F4 SITL results `team/F4/sitl/RESULTS.md` | `R-PILOT`, `subsystems/flight-software/SITL-PLAN.md` |
| Stick time on the twin or a small quad before the first XPS hover | `PILOT-LOG.md` | `R-PILOT` |
| Ground gates before any twin flight that uses the K09-L stand data: GT-12 bench (props off): arm, kill, failsafes; GT-14 range check | `team/H1/logs/`, `../F5/RANGE-TEST.md` | `R-ARM-KILL`, `R-RC-LINK` |

### Gate 1. Foam-board twin (`R-TWIN`) before the 15 Dec order

The twin is the $40 foam-board build (Box Kite guide, `CONFIGURATION.md`) on the real motors, FC and pack. Its report is [`TWIN-REPORT.md`](TWIN-REPORT.md). Flight order: bench and tie-down, hanging yaw test (`T-F4-HANG-YAW`), tethered hover, free hover, glides, stall, transition, back-transition.

| # | Flight | Pass lines | Tests, claims |
|---|---|---|---|
| 1a | Tied-down props-off, then props-on at the stand: motor map, directions, elevons | all channels right (`T-F5-BENCH`); motor test A=LR, B=UR, C=UL, D=LL (F4 SITL S2) | `T-F4-BENCH-MAP`, `T-F5-BENCH` |
| 1b | Hanging yaw test, motors UR+LL at 15 % then UL+LR | frame yaws the way of the reaction torque (-x, then +x); else stop: cant prints swapped (CR-F4-11) | `T-F4-HANG-YAW` |
| 1c | Tethered, then free hover, calm | position held **within 1 m**; logged lean <= 20 deg; hover current within +/-0.15 x 27 A of 27 A (`requirements.hover_current_tol`); VIBE < 30 m/s2, clip 0 | `R-TWIN`, `T-F3-VIBE`, `T-E1-HOVER-LOG` |
| 1d | Hover in a **5 m/s** fan or breeze (measured) | as 1c; **no motor output above 85 % or below 10 %** (RCOU) | `R-TWIN`, `R-WIND`, `T-B3-HOVER-WIND` |
| 1e | QLOITER at >= 30 m, calm | altitude hold and position within 1 m | `R-TWIN` |
| 1f | FBWA glides at three speeds, two pack positions | neutral point Xnp from elevon trim vs CL (slope 0) | `T-B3-TWIN-NP`, `CL-B3-XNP` |
| 1g | Slow-flight stalls at >= 50 m, 0.5 m/s per s deceleration, three times | Vs = mean airspeed at the break, **<= 12.0 m/s** (`requirements.stall_max_ms`); F4 sets `AIRSPEED_MIN` = ceil(1.3 x Vs) | `T-B2-STALL`, `CL-B2-STALL-GATE`, `R-STALL` |
| 1h | FW yaw doublet at 1.3 Vs, 50 m, CG on the aft mark | heading and sideslip return within 2 s, yaw-rate oscillation decays | `T-B3-YAW-DOUBLET`, `R-DIRECTIONAL` |
| 1i | Transition at >= 1.3 Vs, **two laps and a back-transition** | at >= 50 m, calm, FBWA from QHOVER at 12 deg/s; height loss <= 10 m; transition >= 15.5 m/s; cruise current near 16.2 A; elevon size for clean FBWA authority recorded | `R-TWIN`, `T-B1-TRANSITION-LOG`, `T-B1-CRUISE-POWER`, `R-TRANSITION` |
| 1j | Landing practice, 20 landings | 95th percentile ground speed at contact <= 0.3 m/s; throttle out <= 0.71 hover within 0.5 s of contact | `T-C5-DRIFT-LOG`, `T-F4-TD-CUT` |
| 1k | FBWA full-down stick, idle, 20 s at >= 80 m | airspeed <= 20.5 m/s | `T-F4-DIVE` |

**Twin gate result.** Pass = 1c, 1d, 1e, 1i, and 1g measured. A wind fail (1d) triggers the K11 planform test, then the K01 fallback (`CONFIGURATION.md`, `R-TWIN`): H2 reports to A1 the same day, and the 15 Dec order waits for A1's word (`HANDOFF.md` H1).

### Gate 2. Thrust stand, one station (ground, H1)

`R-HOVER-TW`: GT-02 results (`T-E1-STAND`, `T-A1-THRUST-STATION`). H2 uses its numbers for the hover throttle and current expectations; not a flight.

### Gate 3. XPS aircraft: weigh-in and tethered hover

| Pass lines | Tests, claims |
|---|---|
| Weigh-in: <= 2.6 kg with each pack; CG inside the marks 46.6 / 51.4 mm with each pack **(if aft of 51.4 mm do not fly it)** | `R-MASS-GATE`, `R-CG-RANGE`, `T-A1-WEIGH`, `T-A3-CG-BALANCE` |
| Tethered hover 60 s at 1 m, ballast to 2.6 kg: hover current within +/-0.15 x 27 A of that value; limiter verified (stand: 25 A, `K09L-STAND.param`) | `R-HOVER-TW`, `R-ESC-CURRENT`, `T-B1-TETHER-HOVER`, `T-E1-HOVER-LOG` |
| VIBE < 30 m/s2 each axis, clip 0, FFT peaks at 1P and 2P noted, notch set (`INS_HNTCH_*`) | `R-VIBRATION`, `T-F3-VIBE` |
| Compass interference <= 30 % at hover current | `R-COMPASS`, `T-F3-COMPASSMOT` |
| GPS: 3D fix, HDOP <= 1.2 at 3 min with the aircraft standing | `T-F3-HDOP` |
| Restraint pull and restrained four-motor run done (H1 GT-13) | `T-H1-RESTRAINT-PULL`, `T-H1-RESTRAINED-RUN` |

### Gate 4. Free hover and landing practice (QHOVER / QLOITER)

| Pass lines | Tests, claims |
|---|---|
| Position within 1 m in 5 m/s; lean <= 20 deg; no motor above 0.84 for > 1 s (F4 S3) | `R-WIND`, `R-HOVER-AUTHORITY`, `T-B3-HOVER-WIND` |
| Landings wingtip into the wind with QLAND for the last 6 m (0.3 m/s); 20 logged touchdowns: ground speed 95th percentile <= 0.3 m/s; RC9 cut at contact | `R-TIPOVER`, `R-LANDING-IMPACT`, `T-C5-DRIFT-LOG`, `T-F4-TD-CUT` |
| One QHOVER full-down-stick descent from 10 m to 2 m on the twin to read the overshoot over `Q_PILOT_SPD_DN` 1.0 | <= 1.2 m/s (D-65) |
| Hover pitch-trim thrust split | measured vs 1.216 predicted (limit 1.25): `R-HOVER-SPLIT`, `CL-A3-HOVER-SPLIT` |

### Gate 5. Fixed-wing tune as a plain flying wing

| Pass lines | Tests, claims |
|---|---|
| Hand-launch, FBWA, motors as throttle; AUTOTUNE pitch then roll within the ceilings in `TUNING-PLAN.md` step 4/6; trim elevons (expect -6.1 deg at 16 m/s) | `R-CRUISE-AUTHORITY` |
| Before the airspeed sensor is bought (gate `X08`): `ARSPD_TYPE` 0, **FBWA only** (no CRUISE / AUTO / RTL in fixed wing) | `TUNING-PLAN.md` step 6; CR-I1-16 |
| Dive: FBWA full-down stick, idle, 20 s at >= 80 m: airspeed <= 20.5 m/s. Full-throttle level leg at >= 60 m, fresh pack: <= 21.8 m/s, ESC rpm <= 7 950, each motor RCOU <= 0.79 with rudder | `T-F4-DIVE`; `TUNING-PLAN.md` 6b, 6c |
| Slow-flight stall **on K09-L** at 2.6 kg and the forward CG (0.0466 m): Vs <= 12.0 m/s; F4 sets `AIRSPEED_MIN`, `AIRSPEED_STALL`, `AIRSPEED_CRUISE` | `T-B2-STALL`, `R-STALL` |
| Airspeed calibration (after `X08`): reciprocal legs at 16 m/s, error within the requirement | `T-F3-ARSPD-CAL`, `R-AIRSPEED` |
| Cruise polar: 60 s legs at 14, 16, 18 m/s both ways, calm morning | `T-B1-CRUISE-POWER`, `R-MISSION` |

### Gate 6. First transition at >= 50 m (QSTABILIZE recovery rehearsed)

| Pass lines | Tests, claims |
|---|---|
| Rehearse in SITL and in the hover: QSTABILIZE/QHOVER recovery from a failed transition (`PILOT-LOG.md`) | `R-PILOT` |
| At >= 50 m AGL, calm, morning <= 5 m/s: FBWA from QHOVER at 12 deg/s (`Q_TAILSIT_RAT_FW`); abort to QHOVER on any doubt | `R-TRANSITION`, `T-B1-TRANSITION-LOG` |
| Result: transition at >= 15.5 m/s, height loss <= 10 m; peak motor output logged (<= 0.77 of full for a raise to 15 deg/s later) | `CL-B1-TRANS-ALT-LOSS`, `TUNING-PLAN.md` step 7, 9 |

### Gate 7. Back-transition at altitude

| Pass lines | Tests |
|---|---|
| QHOVER from cruise at >= 50 m: no tumble, height loss <= 10 m | `TUNING-PLAN.md` step 8, SITL S5 |

### Gate 8. Landing practice in calm air

Same pass lines as gate 4 for the aircraft after a back-transition: 20 touchdowns, wingtip into the wind, ground speed 95th percentile <= 0.3 m/s (`T-C5-DRIFT-LOG`).

### Gate 9. Full mission (`R-MISSION`)

| Pass lines | Tests |
|---|---|
| Vertical take-off, transition, cruise, back-transition, vertical landing, 2 min hover total and 5 min cruise, energy reserve 20 % (`requirements.hover_time_min`, `cruise_time_min`, `energy_reserve_frac`) | `T-E2-MISSION-LOG`, `T-E3-MISSION`, `R-MISSION` |
| Link: LQ >= 0.9, RSSI >= -102 dBm out to the geofence radius (250 m) in the logs | `T-F5-FLIGHT-LINK`, `R-RC-LINK` |
| Temperatures after the first missions within +/-8 K of the E3 model | `T-E3-MISSION`, `R-THERMAL` |

## 5. Abort and recovery rules

| Condition | Action | Source |
|---|---|---|
| Wind above the card (mean > 5 or gust > 8 m/s) | no flight; lay the aircraft flat, pack out, mat | `../H3/FLIGHT-CARD.md`, C5 S5/S6 |
| Link lost | Q modes: QLAND in place; FW: circle, RTL at 5 s, then QRTL; failsafe time <= 2.5 s | `../F5/RC-LINK.md`, `K09L.param` `FS_*` |
| Battery low (2 600 mAh remaining or 14.0 V) / critical (1 300 mAh remaining or 13.6 V) | low: RTL; critical: QLAND (`BATT_FS_LOW_ACT 1`, `BATT_FS_CRT_ACT 4`); land at once on low when hovering | `K09L.param` lines `BATT_*` |
| Geofence: 110 m altitude, 250 m radius | breach action fires; the pilot is already inside it | `K09L.param` `FENCE_*` |
| Any doubt in transition | QHOVER | `TUNING-PLAN.md` step 7 |
| Uncontrollable and clear area | e-stop (switch SD, `RC9_OPTION 31`) | `R-ARM-KILL` |
| After any tip-over or hard landing | disarm, pull the plug from behind the pod, check witness marks, feet, hinges, cheeks; spin each motor by hand; replace props | `BUILD-GUIDE.md` stage 12; C5 S8 |

## 6. Cadence and dates

Dates are `../I2/SCHEDULE.md`: twin flights 8-13 Dec (before the 15 Dec order), first tethered hover from 22 Feb (build week 5), free hover to early March, fixed-wing tune to mid-March, first transition mid-March,
crash-repair block 21-31 Mar, round trips in April, full missions to 28 Apr. A flying week has 5.0-5.7 usable mornings on average (`config-study/tiebreak/DECISION.md`); plan 2 flight mornings per week per gate and request
RFS windows in blocks 8 business days ahead (`../H3/COMPLIANCE.md`).

## 7. Failure handling

| Event | H2 action | Decision by |
|---|---|---|
| Twin misses the 5 m/s hover or cannot transition before 15 Dec | report to A1 with the logs the same day; hold the order | A1 (`HANDOFF.md` H1; reverse to K01-lean per `CONFIGURATION.md`) |
| Stall on K09-L above 12.0 m/s | F4 raises `AIRSPEED_MIN`; B2/B1 re-run; A1 decides whether the transition margin holds | A1, B1, B2 |
| Crash | pull the plug, log, photograph, repair per `../G1/PROCESS-PLAN.md` section 6; no new flight until the cause is in the log | H2 + owner |
| Any gate fails twice | stop flying, owner analysis, change request | A1 |

## 8. Evidence and claims

`R-TWIN`, `R-TEST-ORDER` and `R-PILOT` have **no claim yet** (`team/A2/VERIFICATION-MATRIX.md`). This plan does not create one: when the twin report and the first logs exist, H2 emits `kit.test(..., state="run", result=..., evidence=<log path>)`
entries in its own script (H1's pattern, `team/H1/GROUND-TEST-PLAN.md` "Evidence files") and A2 adds the claim ids. Until then the evidence is `logs/` + `TWIN-REPORT.md`.
