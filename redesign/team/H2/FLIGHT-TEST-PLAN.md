# H2 flight-test plan: K09-L (twin first, build-up, envelope expansion)

Revision H2-R2, 2026-11-14 (closure round, `review/CLOSURE-ROUND-2026-11-14/H2.md`: gate 9 pass line 3.5 min on the racetrack (D-160), gate 5 legs that fit the 250 m fence, touchdowns per sortie, forward transition by the transition switch from 50–55 m (B3), A2's M1 / M2 logged, belly into the wind (D-152); checks in [`plan_checks.py`](plan_checks.py)). R1, 2026-11-13. Status `PROPOSED`; nothing in this file has been flown. Owner H2 (flight test engineer). Requirements: `R-TEST-ORDER`, `R-TWIN`, `R-PILOT` (`team/A2/REQUIREMENTS.md`).
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
6. Briefing: abort words ("abort" = QHOVER if in FW, e-stop only if airborne and uncontrollable over a clear area), landing area, wind direction (**belly into the wind** for touchdown, never pod face to the wind: D-152, `TUNING-PLAN.md` step 5; replaces the R1 "wingtip into the wind"), who calls the e-stop, the racetrack straight for the day's wind (section 4a), and the touchdown count for the sortie (section 4a).

## 4. Gates

The ids in the Tests column are the repo's planned tests (`kit.test` in the owner's script); this plan does not add a test, it fixes when each is run and what passes. Claim ids are the proof-chain nodes the evidence feeds.
`FAIL` entries in the proof graph (`PROOFS.md`) are inputs, not exceptions: a gate pass overwrites a model number with a measured one.

### 4a. Rules that apply to every gate (R2)

**Touchdowns per sortie: at most 2** = 1 landing + at most 1 go-around touchdown (a touch-and-go counts as one). This is the number C5 checks `CL-C5-LANDINGS-PER-CARTRIDGE` against (2.61 normal landings per cartridge, graph 2026-11-14 23:26 → +31 %; A2 closure §2.5). Landing-practice gates (4, 8, twin 1j) collect their 20 touchdowns over ≥ 10 sorties, never more than 2 in one sortie. At every turnaround (20 min, `ASM-E2-TESTDAY`) the logger reads the flange gap on each foot (C5 "how") and the feet are swapped (≤ 10 min, `requirements.foot_replace_max_min`) when any gap is at the replace mark. A third touchdown in one sortie (second go-around) is not flown: land at the alternate spot (`../H3/FLIGHT-CARD.md` §4b).

**Forward transition (B3 closure §1.3–1.4, CL-5):** start at **50 m AGL (≤ 55 m)**, in QSTABILIZE, belly into the wind; **only by the transition switch** (throttle override 1.285 × learnt θh, 2.0 s pre-climb, then FBWA; F5 CL-4), never by the mode switch, never from QHOVER / QLOITER. **No AUTO forward transitions** (no AUTO, no mission VTOL take-off into FW). The climb is ≤ 49.5 m (`CL-B3-TRANS-CLIMB`, high edge): top 99.5 m from 50 m, 104.5 m from 55 m, under the 110 m `FENCE_ALT_MAX` (the breach test uses the raw limit; `FENCE_MARGIN` 10 only raises a margin notice, `AC_Fence.cpp` `check_fence_alt_max`, ArduPilot-4.7 branch, read 2026-11-14) and the 122 m (400 ft) ceiling. Aim for 50 m; 55 m is the most.

**Racetrack (gates 1i, 5, 9).** Centred on home, straights along the wind, 17 m/s, ≤ 30° bank. The straight is set from the mean wind measured at the briefing so that one lap stays ≤ 54.2 s (A2's lap) and the far point ≤ 201 m (`plan_checks.py`; ground-fixed track, turn radius from the fastest ground speed V + w):

| Mean wind, m/s | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Straight, m | 300 | 270 | 250 | 220 | 190 | 150 |
| Lap, s | 54.2 | 53.1 | 53.6 | 53.5 | 53.7 | 53.1 |
| Far point, m | 201.0 | 192.2 | 188.8 | 180.6 | 172.9 | 160.5 |
| The fixed 300 m track would lap, s | 54.2 | 56.6 | 59.6 | 63.2 | 67.4 | **72.5** |

The fixed 300 m track at 5 m/s laps in 72.5 s, above A2's 68 s fail line for M2, and its far point is 235.5 m (14.5 m inside the fence). So the straight follows the wind.

**Measurements A2 asked for (A2 closure M1, M2): logged on every sortie that has the phase**, in the flight row (`templates/flight_log.csv`, R2 columns) with stopwatch times checked against `BAT.CurrTot` and the mode-change log:

| # | Item | Logged on | Pass / action line (A2) |
|---|---|---|---|
| M1a | Hold at 50 m before the transition, s (QLOITER + attitude check) | twin 1i, gate 4 profile sortie, gates 6, 9 | ≤ 35 s budget; > 60 s → A2 (cruise to `BATT_LOW` 3.79 min); > 77 s fails R-MISSION |
| M1b | Go-around hover, s (climb ≥ 10 m, re-position, re-try) | twin 1j, gates 4, 8, 9 | ≤ 40 s (`requirements.goaround_hover_s`); > 40 s → E2 re-checks `BATT_LOW` (60 s gives 4.02 min) |
| M1c | Landing hover, s (from 6 m to contact, incl. QLAND final) | every landing | ≤ 30 s budget (A2 §2.1) |
| M1d | mAh used in each of M1a–c | same | against E2's phase table ±15 % (`T-E2-MISSION-LOG`) |
| M2 | Lap time on the racetrack at 17 m/s, s, with the straight and the wind | twin 1i (information: twin speed differs), gate 5, gate 9 | ≤ 55.7 s pass; 55.7–68 s → A2 re-derives; > 68 s fails R-MISSION |

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
| 1i | Transition at >= 1.3 Vs, **two laps and a back-transition** | from 50 m (≤ 55 m) by the transition switch (section 4a), calm, 12 deg/s; held throttle = 1.285 θh ± 0.01 to 70°; handover airspeed ≥ 1.3 Vs; climb ≤ 50 m; cruise current near 16.2 A; elevon size for clean FBWA authority recorded; **M1a hold and M2 lap time logged** (section 4a) | `R-TWIN`, `T-B1-TRANSITION-LOG`, `T-B1-CRUISE-POWER`, `R-TRANSITION` |
| 1j | Landing practice, 20 landings, belly into the wind, ≤ 2 touchdowns per sortie | 95th percentile ground speed at contact <= 0.3 m/s; throttle out <= 0.71 hover within 0.5 s of contact; **M1b go-around and M1c landing hover times logged** | `T-C5-DRIFT-LOG`, `T-F4-TD-CUT` |
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
| Landings belly into the wind (D-152) with QLAND for the last 6 m (0.3 m/s); 20 logged touchdowns over ≥ 10 sorties (≤ 2 per sortie, section 4a), flange gap read at each turnaround: ground speed 95th percentile <= 0.3 m/s; RC9 cut at contact | `R-TIPOVER`, `R-LANDING-IMPACT`, `T-C5-DRIFT-LOG`, `T-F4-TD-CUT`, `CL-C5-LANDINGS-PER-CARTRIDGE` |
| **Mission-profile hover rehearsal** (one sortie, QLOITER): climb to 50 m at 2 m/s, hold, descend at 1 m/s, one go-around, landing. Log M1a–M1d (section 4a) | A2 M1; `R-MISSION` (hold ≤ 77 s, go-around ≤ 40 s, landing hover ≤ 30 s) |
| One QHOVER full-down-stick descent from 10 m to 2 m on the twin to read the overshoot over `Q_PILOT_SPD_DN` 1.0 | <= 1.2 m/s (D-65) |
| Hover pitch-trim thrust split | measured vs 1.216 predicted (limit 1.25): `R-HOVER-SPLIT`, `CL-A3-HOVER-SPLIT` |

### Gate 5. Fixed-wing tune as a plain flying wing

| Pass lines | Tests, claims |
|---|---|
| **Launch (open, request to A2 / A1, section 4a of `H2.md`):** K09-L cannot be hand-launched: it stalls near 12 m/s (`requirements.stall_max_ms` 12.0) and `config-study/tiebreak/DECISION.md` §5.3 item 1 moves the hand-launch FW tune to the twin (gate 1f–1h). It also cannot land as a plain wing (props at the fin-tube ends). Proposed: on K09-L every gate-5 sortie is a vertical take-off, a gate-6 transition, the tune items, and a gate-7 back-transition, so gates 6–7 are flown first on the twin's tune and gate 5 follows. Until A1 decides, the gate order is as written in `R-TEST-ORDER` | `R-TEST-ORDER` |
| FBWA, motors as throttle; AUTOTUNE pitch then roll within the ceilings in `TUNING-PLAN.md` step 4/6; trim elevons (expect -6.1 deg at 16 m/s) | `R-CRUISE-AUTHORITY` |
| Before the airspeed sensor is bought (gate `X08`): `ARSPD_TYPE` 0, **FBWA only** (no CRUISE / AUTO / RTL in fixed wing) | `TUNING-PLAN.md` step 6; CR-I1-16 |
| Dive: FBWA full-down stick, idle, 20 s at >= 80 m: airspeed <= 20.5 m/s. Full-throttle level leg at >= 60 m, fresh pack: <= 21.8 m/s, ESC rpm <= 7 950, each motor RCOU <= 0.79 with rudder (R1 values; `propulsion.rpm_max` is now 13 360 (D-161) and B4 may relax `THR_MAX`: these lines follow F4's next `TUNING-PLAN.md` revision) | `T-F4-DIVE`; `TUNING-PLAN.md` 6b, 6c |
| Slow-flight stall **on K09-L** at 2.6 kg and the forward CG (0.0466 m): Vs <= 12.0 m/s; F4 sets `AIRSPEED_MIN`, `AIRSPEED_STALL`, `AIRSPEED_CRUISE` | `T-B2-STALL`, `R-STALL` |
| Airspeed calibration (after `X08`): reciprocal straight legs at 16 m/s on the 200 m racetrack below, error within the requirement | `T-F3-ARSPD-CAL`, `R-AIRSPEED` |
| Cruise polar: **timed straight legs on a 200 m-straight racetrack** centred on home, straights along the wind, 3 laps at each of 14, 16, 18 m/s (3 legs each way; the data window is the straight only, turns excluded). Leg 14.3 / 12.5 / 11.1 s in calm (≤ 20 s); far point at the 5 m/s card limit 163.8 / 177.9 / 193.4 m (turn radius from V + 5 m/s at 30°), so ≥ 56.6 m inside the 250 m fence (`plan_checks.py`). Replaces R1's 60 s legs (840–1 080 m, longer than the 500 m fence diameter) | `T-B1-CRUISE-POWER`, `R-MISSION` |
| **M2 lap time:** 2 laps at 17 m/s on the racetrack with the straight for the day's wind (section 4a); lap time, straight and wind logged | A2 M2: ≤ 55.7 s pass, > 68 s fails `R-MISSION` |

### Gate 6. First transition at >= 50 m (QSTABILIZE recovery rehearsed)

| Pass lines | Tests, claims |
|---|---|
| Rehearse in SITL and in the hover: QSTABILIZE/QHOVER recovery from a failed transition (`PILOT-LOG.md`) | `R-PILOT` |
| At **50 m AGL (≤ 55 m)**, calm, morning <= 5 m/s, after SITL S4c confirms B3's pass lines: steady QSTABILIZE hover belly into the wind, M1a hold logged, then **the transition switch** (override 1.285 θh, 2.0 s pre-climb, FBWA; 12 deg/s, `Q_TAILSIT_RAT_FW`). Never the mode switch, never from QHOVER / QLOITER, no AUTO. Abort to QHOVER on any doubt | `R-TRANSITION`, `T-B1-TRANSITION-LOG`, B3 closure §1.4 |
| Result (B3 closure M5): commanded throttle = 1.285 θh ± 0.01 from the mode change to 70°; trim use ≤ 0.60; handover airspeed at "Transition FW done" ≥ 12.94 m/s; climb ≤ 50 m (top < 110 m fence); peak motor output and BAT.Curr (≤ `Q_M_BAT_CURR_MAX` as loaded: 73.2 A, D-161 / `performance.full_throttle_current_a`; was 70.2) logged. Replaces R1's "≥ 15.5 m/s, height loss ≤ 10 m" (the D-149 entry climbs, B3 CL-1) | `CL-B3-TRANS-PITCH-USE`, `CL-B3-TRANS-V-HANDOVER`, `CL-B3-TRANS-CLIMB`, `TUNING-PLAN.md` step 7, 9 |

### Gate 7. Back-transition at altitude

| Pass lines | Tests |
|---|---|
| QHOVER from cruise at >= 50 m: no tumble, height loss <= 10 m | `TUNING-PLAN.md` step 8, SITL S5 |

### Gate 8. Landing practice in calm air

Same pass lines as gate 4 for the aircraft after a back-transition: 20 touchdowns over ≥ 10 sorties (≤ 2 per sortie), belly into the wind, ground speed 95th percentile <= 0.3 m/s (`T-C5-DRIFT-LOG`); M1b and M1c logged on each.

### Gate 9. Full mission (`R-MISSION`)

| Pass lines | Tests |
|---|---|
| Vertical take-off, transition (section 4a), cruise, back-transition into the wind, vertical landing. **≥ 3.5 min cruise on the racetrack (2 laps + 1 go-around lap; straight for the day's wind, section 4a) before `BATT_LOW`** (`requirements.cruise_time_min` 3.5, D-160); total hover-mode time ≤ 3.0 min incl. one 40 s go-around (`hover_time_min`, `goaround_hover_s`); ≤ 2 touchdowns; land with ≥ 20 % by the pack's mAh count (`energy_reserve_frac`). M1a–d and M2 logged | `T-E2-MISSION-LOG`, `T-E3-MISSION`, `R-MISSION` |
| Link: LQ >= 0.9, RSSI >= -102 dBm out to the geofence radius (250 m) in the logs | `T-F5-FLIGHT-LINK`, `R-RC-LINK` |
| Temperatures after the first missions within +/-8 K of the E3 model | `T-E3-MISSION`, `R-THERMAL` |

## 5. Abort and recovery rules

| Condition | Action | Source |
|---|---|---|
| Wind above the card (mean > 5 or gust > 8 m/s) | no flight; lay the aircraft flat, pack out, mat | `../H3/FLIGHT-CARD.md`, C5 S5/S6 |
| Link lost | Q modes: QLAND in place; FW: circle, RTL at 5 s, then QRTL; failsafe time <= 2.5 s | `../F5/RC-LINK.md`, `K09L.param` `FS_*` |
| Battery low (**3 100 mAh** remaining or 14.0 V; `K09L.param` l.306 still reads 2 700 until F4 loads E2's value) / critical (1 300 mAh remaining or 13.6 V) | low in FW: RTL; critical: QLAND (`BATT_FS_LOW_ACT 1`, `BATT_FS_CRT_ACT 4`). **In a Q mode the pilot lands at once; the RTL action must not pitch the aircraft over from hover.** Until F4's SITL S8 shows that a low-battery or fence action from a Q mode ends in QLAND / QRTL with no forward transition, hover-only sorties are timed to land before `BATT_LOW` (logger calls at 2 900 mAh used: 0.92 × 6 500 − 3 100 = 2 880 mAh, the worn-pack floor `pack_capacity_min_frac`, EST) | `K09L.param` `BATT_*`; `../H3/FLIGHT-CARD.md` §4; B3 closure CL-3 |
| Geofence: 110 m altitude, 250 m radius | breach action fires; the pilot is already inside it | `K09L.param` `FENCE_*` |
| Any doubt in transition | QHOVER | `TUNING-PLAN.md` step 7 |
| Uncontrollable and clear area | e-stop (switch SD, `RC9_OPTION 31`) | `R-ARM-KILL` |
| After any tip-over or hard landing | disarm, pull the plug from behind the pod, check witness marks, feet, hinges, cheeks; spin each motor by hand; replace props | `BUILD-GUIDE.md` stage 12; C5 S8 |

## 6. Cadence and dates

Dates are `../I2/SCHEDULE.md` (I2-R2): twin flights 8-13 Dec (before the 15 Dec order); F01 first tethered hover 12-14 Feb (build week 4; latest allowed 24 Feb, week 6, A2 closure §2.5; without lever S3 about 22 Feb, still inside); F02 free hover and landing practice 15-22 Feb; F03 fixed-wing tune 23 Feb-3 Mar; F04 first transition and back-transition 4-10 Mar; CR1 crash-repair loop 11-21 Mar; F05 round trips and landing practice 22 Mar-2 Apr; F06 full missions 3-18 Apr; 12 d slack to 30 Apr with CR1 inside. If A1 accepts the gate-5 launch change, F04 and F03 swap places in the same 16 days.

Flight mornings needed against those blocks (`plan_checks.py`; 2 sorties per morning, `CL-E2-SORTIES-PACKS`; usable mornings 5.0 per 7 days, the Mar-Apr low end, `config-study/tiebreak/DECISION.md` l.68; February: —, not measured):

| Block | Gates | Mornings needed (EST) | Usable in the block |
|---|---|---|---|
| F01 | 3 | 2 | 2.1 |
| F02 | 4 | 5 (20 touchdowns at ≤ 2 per sortie) | 5.7 |
| F03 | 5 | 4 | 6.4 |
| F04 | 6-7 | 3 | 5.0 |
| F05 | 7-8 | 5 (20 touchdowns) | 8.6 |
| F06 | 9 | 3 | 11.4 |

F01 and F02 are the tight ones (0.1 and 0.7 mornings spare). A lost February morning moves into the 12 d slack. Request RFS windows in blocks 8 business days ahead (`../H3/COMPLIANCE.md`).

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
