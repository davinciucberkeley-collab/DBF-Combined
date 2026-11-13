# NASA CR-132423 compliance: does K09-L follow "Navigation and guidance requirements for commercial VTOL operations"?

Review pass on branch `redesign/v1`, 2026-11-13. Source document: Hoffman, Hollister and Howell, *Navigation and
Guidance Requirements for Commercial VTOL Operations*, NASA CR-132423, Aerospace Systems Inc., 1974, NTRS 19740021980
(https://ntrs.nasa.gov/citations/19740021980, scanned PDF without a text layer, read page by page as images on
2026-11-13). Design checked: `redesign/subsystems/flight-software/` revision F4-R5 (`K09L.param`, `SPEC.md`,
`SITL-PLAN.md`, `TUNING-PLAN.md`), `subsystems/avionics/SPEC.md` (F3-R2), `team/F3`, `team/F4`, `team/F5/RC-LINK.md`,
`team/H1/GROUND-TEST-PLAN.md`, `team/A2/REQUIREMENTS.md`, `params/params.json`, `STATUS.md`. Nothing was flown, run in
SITL or bench-tested for this review. "CR p. N" is the report's printed page number. Numbers I worked out are marked
**EST** with the formula shown. Unknowns are "—". No other repo file was edited.

## 1. What the report is, and how far it applies

CR-132423 is a 1974 NASA Langley contractor study of the navigation and guidance a **manned, passenger-carrying commercial
helicopter or compound helicopter** (20–100 seats, 180–250 kt; CR p. 9, Table 2) would need to fly **IFR** on
inter-city "Zulu" airways and terminal "Tango" routes in the 1980s Northeast Corridor, independently of CTOL traffic and
of ATC (CR p. 23–24, 34–35, 171). It sets requirements for RNAV, VORTAC/DME/Loran/Omega/MLS navaids, a Kalman-filter
INS hybrid, a traffic-situation display and collision avoidance, and it proposes VTOL precision-approach categories and
a quantitative requirements table (Table 11, CR p. 56). K09-L is a 2.6 kg electric quad tailsitter (`R-CONFIG`,
`R-MASS-GATE` in `team/A2/REQUIREMENTS.md`) flown VLOS ≤ 500 m by a student pilot with a spotter at an RC field under
14 CFR Part 107 (`R-SITE`, `R-LEGAL`). Most of the report does **not** transfer: ATC and airway structure, IFR weather
minima and approach categories, VORTAC/DME/Omega/MLS hardware, multi-aircraft terminal capacity, noise abatement over
cities, passenger ride comfort and airline economics. What **does** transfer, in scaled form, is the physics and the
operating logic: the **decelerating, into-wind approach and the spiral descent** (CR p. 8, 35, 38–39, 172), the
**vortex-ring limit on descent rate** (CR p. 19–20), **attitude-stabilised, velocity-command control in hover**
(CR p. 21–22, 60–61, 118), **navigation accuracy at touchdown expressed statistically** (CR p. 49, 58–60), the
**loop-bandwidth / update-rate hierarchy** (CR p. 60–61), **hybrid GPS-inertial navigation and its failure modes**
(CR p. 62–63, 91–96), **an autopilot-plus-independent-monitor redundancy level** (CR p. 56, 60), **obstacle clearance
surfaces and temporary obstructions** (CR p. 42, 57–58, 166–167), **a missed-approach procedure for every approach**
(CR p. 33, 39), **gust and wind effects** (CR p. 22, 126), and **pilot proficiency, workload and fatigue**
(CR p. 27, 168–169).

> **Scope note for the integrator.** The task brief describes an 8–15 kg lift + cruise aircraft with a pusher. The
> design under `redesign/` is not that: `R-CONFIG` is a quad tailsitter with no pusher, and `R-MASS-GATE` is 2.6 kg.
> This review checks the design as it stands in `redesign/`. Root `CLAUDE.md` and `DECISIONS.md` own that conflict;
> this file does not pick a side.

## 2. Verdict

K09-L **mostly follows CR-132423 where it applies.** Its descent rates sit inside the vortex-ring boundary. It flies only
attitude-stabilised modes. It uses a GPS-inertial hybrid with an EKF failsafe, keeps a pilot with an e-stop as the
independent monitor, and holds its airspeed error under the report's air-data assumption. **The gaps are in the
approach and in field procedure, not in hardware.** Five matter:

1. **RTL ignores the wind.** `Q_RTL_MODE 1` back-transitions over home on whatever heading RTL arrives on, possibly
   downwind. It then hovers down 50 m vertically. The report rules out downwind approaches and recommends a spiral
   descent ending into wind (CR p. 35, 38–39, 172). ArduPilot's `Q_RTL_MODE 2` "VTOL approach" does exactly that.
2. **No missed-approach or go-around procedure, and no alternate landing spot.** The report requires one for every
   approach (CR p. 33, 39).
3. **No landing zone, approach sector or obstacle survey,** and the fence polygon is not yet uploaded (`FENCE_TYPE 3`).
   The report sets obstacle-clearance surfaces, pad clearances and a re-check for temporary obstructions
   (CR p. 42, 56–59, 166–167).
4. **The hover velocity loop is unchecked against the slow attitude loop.** The report's guidance hierarchy has the
   attitude loop at about 6 rad/s and the velocity loop below 1 rad/s (CR p. 61). K09-L's roll attitude crossover is
   only 1.0 Hz, yet `Q_P_VELXY_*` is left at the firmware defaults with no check.
5. **Touchdown state is not specified or measured.** There is no limit on horizontal speed at contact, no check of
   baro drift against the 6 m final-descent switch, and no check of vertical-speed accuracy at 0.3 m/s (CR p. 59–60).

No finding needs new hardware or money. Two change parameters now (`Q_RTL_MODE`, `Q_RTL_ALT`, plus the new
`Q_FW_LND_APR_RAD` / `Q_TRANS_DECEL` lines). The rest are SITL cases, tuning-plan pass lines and flight-card items for
H3, whose card does not exist yet (`STATUS.md` "H3 flight card … not done").

| Requirements extracted | COMPLIES | GAP | N/A | Distinct gaps (changes) |
|---|---|---|---|---|
| 62 | 30 | 22 | 10 | 14 (G-01 … G-14) |

COMPLIES means the design or plan meets the scaled requirement on paper. Every flight behaviour behind it is still
`UNVERIFIED`, because `K09L.param` has not been loaded or run (`subsystems/flight-software/SPEC.md` header).

## 3. Requirements matrix

Applies: **yes** = transfers as stated; **scaled** = transfers once sized to a 2.6 kg VLOS aircraft; **no** = does
not transfer (reason given). Repo paths are relative to `redesign/`.

### 3.1 Operational constraints (§2.1–2.2)

| ID | CR page | Requirement as stated (paraphrased; numbers verbatim) | Applies? | K09-L equivalent and source | Status |
|---|---|---|---|---|---|
| N-01 | p. 8; p. 18 Fig. 7 | Approach to landing is a **decelerating** flight path, curved in two planes; a vertical leg (up to 1000 ft) may be used at take-off and landing | scaled: the tailsitter decelerates by its pitch-up flare and finishes on a vertical leg | Forward flight to home → back-transition (`Q_TAILSIT_RAT_VT` 30 °/s, `Q_TAILSIT_THR_VT` 55) → vertical descent at `Q_WP_SPD_DN` 1.2 m/s, final 0.3 m/s below 6 m (`K09L.param` §4–5; `SPEC.md` transition table) | COMPLIES |
| N-02 | p. 8 | Fully automatic approach from **any azimuth**, with the pilot as monitor-manager | scaled | RTL → QRTL and QLAND are automatic (`Q_RTL_MODE` 1, `BATT_FS_*`, `FS_LONG_ACTN` 1). The approach azimuth is not chosen, though: see N-19 | COMPLIES (azimuth: see N-19) |
| N-03 | p. 9 Fig. 2 | Rotor lift falls with airspeed; the wing takes over (rotor + wing) | scaled: transition speed band | Motor assist below `Q_ASSIST_SPEED` 13 m/s (1.09 Vs); transition ends at > 13 m/s with TECS climbing to 16 m/s ≥ 1.3 Vs (`R-TRANSITION`; `SPEC.md` transition table) | COMPLIES |
| N-04 | p. 16 | Take-off and landing are the critical phases: limit time spent in high-power, low-speed flight and near the terminal | scaled: hover energy | Hover budget ≥ 2 min inside `R-MISSION` with a 20 % reserve; `BATT_LOW_MAH` 2 600 → RTL, `BATT_CRT_MAH` 1 300 → QLAND (`K09L.param` §9). RTL still hovers down 50 m: see N-21 | COMPLIES |
| N-05 | p. 16–18 Figs. 6–7 | Noise footprint: steeper approaches (6° → 18° shrinks the area ×3) and vertical segments | no: RFS sub-field, no noise-sensitive area in the repo | — | N/A |
| N-06 | p. 16 | Higher sink rates leave less margin: they need more pilot proficiency, or better guidance and control | yes | Climb-rate-controlled Q modes; pilot sink limited to `Q_PILOT_SPD_DN` 1.0 m/s; flight card asks for QLAND for the last 6 m (`SPEC.md` Landing; CR-F4-18). QSTABILIZE barred for landing (CR-F4-21) | COMPLIES |
| N-07 | p. 18–19 Fig. 8 | Large flight-path-angle deviations (around ±10°) in a descent to hover show the need for better terminal guidance | scaled: back-transition | Back-transition height loss ≤ 10 m, no tumble: SITL S5 and `TUNING-PLAN.md` step 8 | COMPLIES (`UNVERIFIED`) |
| N-08 | p. 19 Eq. (1) | tan γ = D/L − V̇/(g cos γ): descent angle and deceleration trade against each other; the approach must fix both | scaled | FW descent capped by `TECS_SINK_MAX` 2.5 m/s at 16 m/s (γ = asin(2.5/16) = **9.0°**, EST). The deceleration used to plan the VTOL stop (`Q_TRANS_DECEL`) is not stated in `K09L.param`. Its firmware default is 2.0 m/s² (ArduPilot `ArduPlane/quadplane.cpp`, master, checked 2026-11-13), giving a 16²/(2 × 2.0) = **64 m** stopping distance (EST) | GAP (G-07) |
| N-09 | p. 19–20 Fig. 9 | Descent rate limited by the **vortex-ring state**: 15 % mean-to-peak thrust fluctuation region; principal limit on (D/L)max | yes | v_h 6.71 m/s, VRS onset 0.28 v_h ≈ 1.88 m/s (`team/B4/SUMMARY.md` l.109, `ASM-B4-VRS`). Fig. 9 read at vertical descent: the 15 % region starts near 0.3 v_h ≈ 2.0 m/s (EST, read from the figure). Auto 1.2 (64 % of onset), pilot 1.0, final 0.3 m/s (`K09L.param` l.134, 141, 147) | COMPLIES |
| N-10 | p. 19 | Autorotation not used in IFR (descent rates too high) | no: electric multirotor, no autorotation | Single motor failure in hover is "not survivable" (`SPEC.md` failsafes; SITL S11). A configuration decision, outside this report's scope | N/A |
| N-11 | p. 20–22 Eqs. (2)–(4) | Without attitude stabilisation, horizontal displacement grows as t⁴, too hard on a steep descent; attitude stabilisation reduces it to t²; gusts and building turbulence make it worse | yes | Only attitude-stabilised modes: `FLTMODE1-6` 17/18/19/5/7/11, `INITIAL_MODE` 17, no raw-stick mode (`CL-F4-NO-RAW-MODES`) | COMPLIES |
| N-12 | p. 22 | Gusting winds and turbulence complicate low-speed control: operate inside a stated wind limit | scaled | `R-WIND` 5 m/s steady, 8 m/s gust survive-and-land. The landing wind margin is thin: 5.4 vs 5.0 m/s (`STATUS.md` thin margins). `R-WIND-MEASURE` not done; flight card not written | GAP (G-11) |
| N-13 | p. 22–23 | Economy: operate independently of CTOL in adverse weather, with schedule reliability | no: no schedule, VFR only | — | N/A |
| N-14 | p. 23–24, 40, 97, 167 | Provide your own separation from other traffic (traffic information or CAS); low-altitude VFR encounters need a proximity alert | scaled: VLOS see-and-avoid by pilot and spotter | `R-SITE` requires a spotter. No traffic-call or abort procedure is written (H3 card missing). No ADS-B receiver (none in the BOM) | GAP (G-12) |

### 3.2 IFR operations and procedures (§2.3–2.4)

| ID | CR page | Requirement as stated | Applies? | K09-L equivalent and source | Status |
|---|---|---|---|---|---|
| N-15 | p. 24–30 | IFR certification, RNAV airways, Decca/FTMS routes | no: VLOS Part 107 | — | N/A |
| N-16 | p. 27 | Pilot IFR proficiency is the barrier; a realistic simulator at reasonable cost is needed | scaled: tailsitter skill | `R-PILOT` ≥ 10 h ArduPilot SITL on the team's parameter file, including QSTABILIZE recovery, before the first XPS hover. SITL not installed; pilot not named (`STATUS.md` issue 10) | COMPLIES (plan; not done) |
| N-17 | p. 32–33 Table 6 | VTOL approach categories I–IIIc by ceiling and RVR | no: VFR only | — | N/A |
| N-18 | p. 32–33; p. 39 Fig. 19 | **Every approach needs a missed-approach procedure**, used before the MAP for traffic, loss of navigation or communication, emergencies, or pad conditions. Hover-in-place is not a good missed approach (fuel, obstacles); an alternate final leg / alternate pad is provided | scaled | No go-around or abort-landing procedure, and no alternate landing spot, in `SPEC.md`, `TUNING-PLAN.md` or any flight card (H3 card missing) | GAP (G-02) |
| N-19 | p. 35; p. 172 | Crosswind approaches are acceptable; **downwind approaches are not** (vortex ring); at least two approach directions per site | yes | Hover landing turns a wingtip into wind (`Q_WVANE_LAND` 3). The fixed-wing arrival and back-transition heading is not controlled: `Q_RTL_MODE` 1 changes to QRTL within `RTL_RADIUS` of home on whatever heading it arrives on (ArduPilot `Q_RTL_MODE` description, checked 2026-11-13). Manual back-transitions have no heading rule | GAP (G-01) |
| N-20 | p. 35–36 Fig. 16 | Enroute obstruction clearance: MOCA 500 ft above obstacles within ±2 nm, tapering to 0 at ±3 nm | scaled: minimum altitude for wing-borne flight over the field | Transitions ≥ 50 m (`transition_alt_min_m`), `RTL_ALTITUDE` 50, `Q_ASSIST_ALT` 15. No obstacle heights are surveyed, so the 50 m margin is unknown (—) | GAP (G-03) |
| N-21 | p. 38–39; p. 172; p. 174 | **Spiral descent approach**: has the advantages of a vertical descent, but holds airspeed, uses less power, avoids the vortex ring, accepts any arrival direction and keeps a missed-approach leg | scaled | `Q_RTL_MODE` 1: back-transition at `RTL_ALTITUDE` 50 m, then a 50 m hover descent at 1.2 m/s (≈ 42 s of hover power, EST = 50 / 1.2). No wing-borne spiral down | GAP (G-01) |
| N-22 | p. 165 Table 29 | Flight-tested spirals: bank 9–30°, descent 500–1000 fpm (2.5–5.1 m/s), 60–80 kt | scaled | A loiter at `RTL_RADIUS` 60 m and 16 m/s needs bank atan(16²/(9.81 × 60)) = **23.5°** (EST), inside 9–30°. Sink ≤ `TECS_SINK_MAX` 2.5 m/s, the low end of the table | COMPLIES (once G-01 makes RTL spiral) |
| N-23 | p. 42; p. 45; p. 57–58 Fig. 24 | Near the landing site, **approach clearance surfaces** set a minimum approach angle (10° clears most sites; 12° max at B-2); primary and secondary areas and a missed-approach surface | scaled | No landing zone, approach sector or clearance surface is defined anywhere in `redesign/` (search 2026-11-13: no "landing zone", "obstacle" or "approach sector" in any SPEC, plan or card) | GAP (G-03) |
| N-24 | p. 45 | Narrow approach corridors (about ±300 ft lateral) | scaled: a transition / back-transition lane on the field map | Transition entered at ≥ 50 m on any heading (`SPEC.md` transition table); no lane or keep-out drawn | GAP (G-03) |

### 3.3 Navigation requirements (§2.5)

| ID | CR page | Requirement as stated | Applies? | K09-L equivalent and source | Status |
|---|---|---|---|---|---|
| N-25 | p. 45–46 | Information to the pilot: aircraft status (fuel, power), system status, situation (track, speed, altitude, **vertical velocity**, position), environmental data (wind), hazards | scaled | Pocket screen with the Yaapu script plus voice for mode, battery and link; EdgeTX page with 1RSS, RQly, Bat, Capa, FM, Alt, GSpd; spotter (`team/F5/RC-LINK.md` l.122) | COMPLIES |
| N-26 | p. 46–49 Table 8 | Checklist: non-saturable, line-of-sight independent, real-time, all-weather, map-referenced, accuracy … | scaled | u-blox M10 GNSS (`AVN-002`) fused with two IMUs in the EKF: non-saturable, map-referenced, continuous | COMPLIES |
| N-27 | p. 49 | Accuracy is specified **at 95 % likelihood** | yes | Position-hold pass lines give no probability: "±1 m at 5 m/s" (SITL S3), "within 1 m" (`R-TWIN`, `TUNING-PLAN.md` step 5) | GAP (G-08) |
| N-28 | p. 51 | Autopilot coupling: full 3-axis control including long vertical ascent and descent, and hover | yes | QLOITER / QHOVER / QRTL / QLAND (`K09L.param` §10) | COMPLIES |
| N-29 | p. 52; p. 54 | Pilot display: direct readout of present position and course deviation; 2-D deviation and progress for landing, take-off and missed approach | scaled: distance and bearing to home, fence margin | Yaapu screen named, but its fields are not listed. The EdgeTX fallback page has no distance-to-home (`RC-LINK.md` l.122) | GAP (G-13) |
| N-30 | p. 53 Table 10 | Take-off guidance: vertical-plane guidance is as essential for take-off as for landing | yes | Vertical take-off in climb-rate modes; wingtip into wind (`Q_WVANE_TAKEOFF` 3); pitch-over only at ≥ 50 m (`R-TEST-ORDER`) | COMPLIES |
| N-31 | p. 54 | Automatic, positive obstacle and terrain avoidance; hazards shown to the pilot | scaled: geofence with keep-outs | `FENCE_TYPE` 3 (ceiling 110 m + 250 m circle). The sub-field polygon is not uploaded ("7 once the sub-field polygon is uploaded (H3 provides the corners)", `K09L.param` l.334). `R-FAILSAFES` asks for the polygon | GAP (G-04) |
| N-32 | p. 54 | Navigation coverage from the final-approach intercept down to the surface; minimise shielding | scaled: GNSS sky view on the tilted mast | 45° tilted patch; HDOP ≤ 1.2 within 3 min standing on the fin tips (`T-F3-HDOP`, `CL-F3-GPS-SKY`) | COMPLIES (`UNVERIFIED`) |
| N-33 | p. 55–56 Table 11 #1 | Range: 5 nm take-off/landing, 25 nm terminal | scaled | VLOS ≤ 500 m (`vlos_max_m`), fence 250 m, link 0 dB margin at 6 175 m (`CL-F5-LINK-RANGE-0DB`) | COMPLIES |
| N-34 | Table 11 #2; p. 55–57 | Coverage: elevation 0–20°, azimuth ±90° for landing | no: beam-navaid geometry; GNSS has none | — | N/A |
| N-35 | Table 11 #3; p. 57–58 | Obstacle proximity: operate to within 500 ft in take-off/landing; 0.5 nm terminal and 2 nm cruise separation | scaled | No obstacle survey or stand-off distances (as N-23) | GAP (G-03) |
| N-36 | Table 11 #4; p. 58–59 | Landing position error **25 ft (2σ)**, about the CAT III lateral touchdown dispersion; terminal 500 ft, cruise 2000 ft | scaled: landing error against landing-zone size (CR pad 200 ft, p. 8 → ratio 8) | QLOITER hold ±1 m at 5 m/s (S3), `R-TWIN` within 1 m. Scaled zone ≥ 8 × 1 m = 8 m across (EST, CR ratio applied) | COMPLIES (`UNVERIFIED`); zone size in G-03 |
| N-37 | Table 11 #4; p. 59 | Velocity accuracy 2 kt landing, 5 kt terminal, 10 kt cruise; angular 0.05° | scaled | EKF GPS-IMU velocity; M10 receiver velocity accuracy — (no maker figure in the repo). Angular: no beam, N/A | COMPLIES (velocity; to measure, M3) |
| N-38 | p. 59 | Altitude known to 1 part in 100; near touchdown, vertical speed known to **0.2 ft/s** (10 % of a typical 2 ft/s touchdown rate) to prevent a hard landing | scaled: 10 % of 0.3 m/s = 0.03 m/s | Baro altitude with ground-effect compensation on (`Q_OPTIONS` bit 13 off, l.28). No rangefinder (`Q_PILOT_SPD_DN` note "no rangefinder", `team/F4/SUMMARY.md` l.24). Baro drift at landing and EKF climb-rate noise near the ground: — (no test) | GAP (G-06) |
| N-39 | p. 59 | Typical touchdown descent rate 2 ft/s (0.61 m/s) | scaled | Final 0.3 m/s (`Q_LAND_FINAL_SPD`), design hard landing 1.2 m/s at ≤ 10° (`R-LANDING-IMPACT`); pilot full down stick 1.0 m/s, so the card asks for QLAND for the last 6 m | COMPLIES |
| N-40 | Table 11 #5; p. 59 | One landing per minute, 1 nm spacing; 500 aircraft peak | no: one aircraft | — | N/A |
| N-41 | Table 11 #6; p. 59 | Pads 400–800 ft apart = clearance of **one pad diameter** between pads | scaled: clearance between the landing zone and the pilot box, spectators and other users' pads | Not defined (H3 card missing) | GAP (G-03) |
| N-42 | Table 11 #7; p. 60 | **2 kt** horizontal velocity accuracy for control in hover just before touchdown: "the uncertainty which can be tolerated in hover just prior to touchdown" | scaled | No limit on horizontal speed at contact. `R-LANDING-IMPACT` covers sink 1.2 m/s and tilt ≤ 10°; `R-TIPOVER` covers the static angle only | GAP (G-05) |
| N-43 | Table 11 #8; p. 60 | Reliability: CAT II = dual autopilot **or autopilot plus independent monitor**; CAT III = triple redundancy | scaled: CAT II analogue (VFR, pilot in VLOS) | Pilot as independent monitor, with QSTABILIZE takeover and the RC9 e-stop ≤ 1 s (`R-ARM-KILL`). Two IMUs on the CoreWing F405 (`team/F3/AVIONICS.md` l.27). Single GPS, compass, baro, airspeed. CAT III: no zero-visibility operation | COMPLIES (CAT II analogue) |
| N-44 | Table 11 #9; p. 60 | Position update 1 s landing, 4 s terminal, 10 s cruise, given a velocity-control loop | yes | GNSS fused by the EKF; `GPS1_RATE_MS` not set in `K09L.param` (firmware default —, read back in S1) | COMPLIES (read-back pending) |
| N-45 | p. 60–61 Fig. 25 | Loop hierarchy: attitude-loop bandwidth about 1 Hz (6 rad/s) in roll, limited below 4 Hz; velocity loop **below 1 rad/s**; position need not update faster than 1 s; dead-reckoning between fixes (2 kt for 1 s ≈ 3 ft) | yes | Hover attitude crossover roll / pitch / yaw 1.0 / 2.4 / 1.0 Hz, ceilings 4.5 / 4.5 / 2.4 Hz (`CL-F4-XOVER-*`, `SPEC.md` key numbers). The velocity / position loop (`Q_P_VELXY_*`, `Q_P_POSXY_P`) is not in `K09L.param`, so it runs at firmware defaults with bandwidth — and no test | GAP (G-09) |
| N-46 | Table 11 #10; p. 61–62 | Data link 8 kbit/s: a traffic picture every 4 s | scaled: downlink to the pilot | CRSF telemetry 1:4 = 37.5 Hz on ELRS 150 Hz (`RC-LINK.md` l.32–33) | COMPLIES |
| N-47 | Table 11 #11; p. 62 | Need both ground (position) and air (velocity) data in a hybrid. Losing a ground signal leaves the vehicle in "a compromising control situation" | yes | EKF3 GNSS + IMU. GPS/EKF loss → QLAND without position hold; pilot recovers in QSTABILIZE (`SPEC.md` failsafes; SITL S10). In 5 m/s wind that QLAND drifts downwind, so the pilot must act | COMPLIES (S10 pending) |
| N-48 | Table 11 #12; p. 62–63 | Signal continuity: no multipath; RF interference; signal loss near power lines | scaled: GNSS and the 2.4 GHz link at the field | `T-F3-HDOP`; `T-F5-RANGE` at 25 mW, 100 m, LQ ≥ 0.9; daily range check (`RC-LINK.md` l.133–134) | COMPLIES (`UNVERIFIED`) |
| N-49 | Table 11 #13; p. 63 | Inertial hybrid updated within one tenth of the Schuler period (< 8 min); airspeed and heading are poor at low airspeed near the ground | yes | GNSS updates the EKF continuously; Q modes do not use airspeed; FW gain scaling falls back to synthetic airspeed (`TUNING-PLAN.md` step 6) | COMPLIES |

### 3.4 Hybrid navigation, guidance and sensors (§3.4, §3.6, §4.2.3, §4.3)

| ID | CR page | Requirement as stated | Applies? | K09-L equivalent and source | Status |
|---|---|---|---|---|---|
| N-50 | p. 94 | The hybrid's statistics give subsystem failure detection when expected limits are "grossly exceeded" | yes | `FS_EKF_THRESH` 0.8 → QLAND (`K09L.param` l.305) | COMPLIES |
| N-51 | p. 94–96 | Kalman-filter limits: wrong error models and statistics, divergence. Verify with sensitivity analysis and "exhaustive simulation" | scaled: EKF innovations on this airframe (vibration, a magnetometer near 100 A, a tilting GNSS mast) | No log-review pass line for EKF innovations or variances; only VIBE/Clip (`TUNING-PLAN.md` step 3) | GAP (G-10) |
| N-52 | p. 97–100 | Collision-avoidance systems (EROS, SECANT, AVOIDS, Synchro-DABS) | no: cooperative transponder CAS | Covered by see-and-avoid, N-14 | N/A |
| N-53 | p. 118–120 Fig. 39–40 | Velocity-command flight control system fed by perturbation guidance; bank and yaw rate limited to a standard-rate 3 °/s turn | scaled: velocity command, yes; the 3 °/s passenger limit, no | QLOITER is velocity-command; yaw rate limit `Q_A_RATE_Y_MAX` 90 °/s (`K09L.param` l.115) | COMPLIES |
| N-54 | p. 121–122 Fig. 41 | Waypoint leg changeover when inside the airway half-width w | no: no AUTO missions; no AUTO in `FLTMODE1-6` | — | N/A |
| N-55 | p. 125–126, 133 | Air-data model: airspeed error ~**2 kt** (wind dominates); altimeter scale factor plus random error; vertical-speed error σ ~**100 fpm** | scaled | Airspeed RSS error at cruise 0.45 m/s against a 0.5 limit (`CL-F3-ASPD-ERR`), below 2 kt = 1.03 m/s. Vertical speed: as N-38 | COMPLIES |
| N-56 | p. 126 Eqs. (26)–(31) | Wind = steady + exponentially correlated + random gusts, horizontal and vertical | scaled | SITL wind 0 / 5 / 8 m/s with `SIM_WIND_TURB` 1 (`SITL-PLAN.md` set-up) | COMPLIES (plan) |

### 3.5 Low-altitude factors and conclusions (§5.4, §6)

| ID | CR page | Requirement as stated | Applies? | K09-L equivalent and source | Status |
|---|---|---|---|---|---|
| N-57 | p. 166–167 | Obstacle data lag the charts (a 537 ft stack shown as 345 ft); **temporary obstructions** (a 100 ft crane) appear near landing sites and break the missed-approach clearance; periodic checks needed | scaled: re-walk the field each session | `R-LEGAL` checks the FAA UAS facility map once. No pre-flight site and obstacle walk (H3 card missing) | GAP (G-03) |
| N-58 | p. 168 | Waypoint-definition errors slip past without feedback; entries need a cross-check | scaled: parameter file and fence corners | Parameters: `fsw_check.py` lint and mirror check, plus the S1 read-back of every name (COMPLIES). Fence corners: no read-back step, see G-04 | COMPLIES (parameters) |
| N-59 | p. 168–169 | Fatigue (workload × time) slows response to in-flight anomalies | yes | No limit on session length or flights per pilot | GAP (G-14) |
| N-60 | p. 172 | Curved, decelerating approaches; spiral descent as a standard procedure | scaled | As N-21 | GAP (G-01) |
| N-61 | p. 171–174 | Recommendations: filtering study, spiral guidance study, RNAV/MLS and VLF flight evaluations, TSD, coverage prediction, fuel economy | no: research agenda for NASA | — | N/A |
| N-62 | p. 174 | Spiral guidance must fix "airspeed, bank angle, descent rate and protected airspace" | scaled | Airspeed 16 m/s, bank 23.5° (N-22, EST), sink ≤ 2.5 m/s set; the protected airspace (loiter circle clear of the pilot box and obstacles) is not defined | GAP (G-03) |

Counts: **62 requirements: 30 COMPLIES, 22 GAP, 10 N/A.** The 22 GAP rows collapse into 14 distinct gaps
(G-01 … G-14), because several rows (N-20, N-23, N-24, N-35, N-41, N-57, N-62) share one fix (G-03).

## 4. Gaps and the changes that close them

Each gap gives the change, the CR page that sets it, and who applies it (owner from `team/A2/REQUIREMENTS.md` or
`SPEC.md`).

### G-01 (Major): RTL arrives on any heading and hovers down 50 m. Use the wing-borne spiral and the into-wind transition (N-19, N-21, N-60)

CR p. 35 and 172: "a tailwind cannot be tolerated, principally because of the vortex ring state". CR p. 38–39 and
172: the spiral descent "avoids the vortex ring state, maintains a stable airspeed, and uses less fuel", and keeps a
missed-approach leg. Today `Q_RTL_MODE` 1 back-transitions at 50 m over home on the RTL arrival heading. For a
tailsitter, a downwind back-transition means a groundspeed overshoot past home at low airspeed. It also means about
42 s of hover at 1.2 m/s (EST, 50 / 1.2) on a pack already at `BATT_LOW`.

ArduPilot's `Q_RTL_MODE` value 2, "VTOL approach", does what the report asks: "vehicle will RTL at RTL alt and circle
with a radius of Q_FW_LND_APR_RAD down to Q_RTL_ALT and then transition into the wind and QRTL" (`ArduPlane/quadplane.cpp`
parameter description, ArduPilot master, read 2026-11-13). Values on master: 0 Disabled, 1 Enabled, 2 VTOL approach,
3 QRTL Always. Keep `Q_OPTIONS` bit 16 (DisableApproach) off; 262 400 already leaves it off. **`Q_RTL_ALT` must rise
from 30 to 50 m.** With mode 2 the transition happens at `Q_RTL_ALT`, and `transition_alt_min_m` is 50 m
(`R-TEST-ORDER`). At 50 = `RTL_ALTITUDE` there is no spiral leg; the gain is the into-wind transition and approach. If
H3 later allows a lower back-transition altitude, the spiral leg comes back. Pilot-flown back-transitions get the same
rule on the flight card: **select QHOVER only heading into wind (± 45°, EST)**.

Not verified on the 4.7.x tag or on a tailsitter. SITL S1 confirms the names. A new SITL case confirms the heading at
back-transition in 5 m/s wind from four directions.

### G-02 (Major): No missed-approach / go-around and no alternate landing spot (N-18)

CR p. 33: the procedure is "often executed prior to reaching the MAP for reasons other than lack of visual contact"
(traffic, nav loss, comms loss, emergencies, pad conditions). Hovering in place is not desirable "for fuel economy or
where proximity to the ground or obstacles could be hazardous". CR p. 39 Fig. 19: an alternate final leg to an
alternate pad. Proposed flight-card section (H3) and `TUNING-PLAN.md` step 5 practice item (F4/H2):

- **Go-around triggers in any Q-mode landing:** drift > 2 m from the spot (EST, 2 × the 1 m hold), tilt > 10°
  (`R-LANDING-IMPACT` limit), a spotter call (traffic, person or animal in the zone), a link warning, a gust above the
  card limit.
- **Action:** QLOITER (switch position 3), climb to ≥ 10 m (EST, above the 6 m `Q_LAND_FINAL_ALT` band plus margin),
  re-position upwind, re-try once. A second abort, or `BATT_LOW` → land at the **alternate spot**.
- **Alternate spot:** marked on the field map, upwind side, same clearance rules as G-03.
- **In fixed wing:** RTL or FBWA loiter at ≥ 50 m is the hold; never hold in hover.

### G-03 (Major): No landing zone, approach sector, clearance surfaces or obstacle survey (N-20, N-23, N-24, N-35, N-41, N-57, N-62)

CR p. 42 and 58 Fig. 24: approach clearance surfaces set a minimum approach angle, with a 10° slope satisfying "most
instances". Table 11 #3: obstacles within 500 ft of take-off and landing need specific treatment. CR p. 59: a clearance
of one pad diameter between pads. CR p. 166–167: temporary obstructions must be re-checked. Proposed field-map sheet
(H3; new file, e.g. `subsystems/ops/FIELD-MAP.md`, owner H3):

| Item | Proposed value | Basis |
|---|---|---|
| Landing zone | ≥ 8 m square, flat, mown | EST: CR pad 200 ft / 2σ error 25 ft = 8 (p. 8, 58), × K09-L hold 1 m (S3) |
| Clearance, zone edge to pilot box, spectators, other pads | ≥ 8 m (one zone width) | CR p. 59 "clearance equal to one pad diameter" |
| Approach / departure sector | 90° wide (EST) centred on the day's wind; no obstacle above a 10° surface from the zone edge | CR p. 42, 58 |
| Back-transition / transition lane | over the sector, ≥ 50 m AGL, never toward the pilot box | CR p. 45 corridors; `transition_alt_min_m` |
| Loiter circle (RTL) | 60 m radius about home, clear of the pilot box at ≥ 50 m | CR p. 174 "protected airspace"; `RTL_RADIUS` |
| Obstacle survey | every object > 3 m (EST) within the 250 m fence: position and height; tallest + margin (—, H3) ≤ `RTL_ALTITUDE` 50 | CR p. 36 MOCA logic, p. 166 |
| Pre-flight walk | each session: re-walk the zone, sector and alternate; note new obstructions (vehicles, tents, other pilots' gear) | CR p. 167 |

### G-04 (Major): Fence polygon not uploaded; no read-back of the corners (N-31, N-58)

`K09L.param` l.334–335 already plans `FENCE_TYPE` 3 → 7 "once the sub-field polygon is uploaded". CR p. 54 asks for
automatic, positive obstacle avoidance; CR p. 168 shows that coordinate entries go wrong without feedback. Change:
upload the RFS sub-field polygon, plus an **exclusion polygon around the pilot box and spectator line**. Before the
first flight, **plot the uploaded fence over satellite imagery and check every corner against the field-map sheet**
(two people, initialled). SITL S9 adds a polygon breach and an exclusion-zone breach. Whether the 4.7.x fence accepts
exclusion zones on this board is not checked here (—, S9).

### G-05 (Major): No horizontal-speed limit at touchdown (N-42)

CR p. 60: 2 kt horizontal velocity is "the uncertainty which can be tolerated in hover just prior to touchdown". A
tailsitter on four fin tips is more sensitive to lateral speed at contact than a skid helicopter. Today only sink
(1.2 m/s) and tilt (≤ 10°) are designed (`R-LANDING-IMPACT`), and tip-over is a static angle (`R-TIPOVER`).
Change: C5 derives the largest horizontal groundspeed at contact that the stance takes without tipping over (value —;
from the 30° tip-over margin and the foot friction). A2 adds it to `R-LANDING-IMPACT`. H2 checks it in every logged
landing (M2).

### G-06 (Minor): Altitude and vertical-speed knowledge near touchdown unmeasured (N-38)

CR p. 59: altitude to 1 %, and near touchdown vertical speed to 0.2 ft/s (10 % of the touchdown rate). Scaled to
K09-L: about 0.03 m/s at the 0.3 m/s final. The 6 m switch to the final rate runs on baro height relative to the
arming point. Baro drift over a 10 min flight and propwash on the pod static: —. No rangefinder (mass reserve 0 g free,
`STATUS.md` issue 3, so none is proposed). Change: measure M1 and M3. If the touchdown baro error exceeds 1 m (EST),
raise `Q_LAND_FINAL_ALT` by the measured error so the final 0.3 m/s still starts above the ground.

### G-07 (Minor): Approach deceleration not stated (N-08)

Eq. (1), CR p. 19: descent angle and deceleration must be set together. `Q_TRANS_DECEL` (stopping-distance
deceleration for the fixed-wing → VTOL change; default 2.0 m/s², range 0.2–5, ArduPilot master, read 2026-11-13) drives
where a G-01 approach starts its transition. Change: state it in `K09L.param` at the default 2.0 m/s². That gives a
64 m stop from 16 m/s (EST), inside the 250 m fence. SITL G-01 case: record the actual overshoot past home and lower it
if the tailsitter flare stops short.

### G-08 (Minor): Position-hold pass lines carry no probability (N-27, N-36)

CR p. 49: accuracy "should be specified in terms of a 95 percent likelihood". Change the pass lines in SITL S3,
`TUNING-PLAN.md` step 5 and `R-TWIN` from "±1 m" / "within 1 m" to **"95 % of logged position samples within 1 m of
the hold point over the 2 min run"**.

### G-09 (Major): Velocity loop not checked against the slow attitude loop (N-45)

CR p. 61: the attitude loop runs at about 1 Hz (6 rad/s) and the velocity loop "below 1 rad/s"; the inner loop must be
the faster. K09-L's roll attitude crossover is deliberately low, 1.0 Hz (`CL-F4-XOVER-RLL`), because of the 11.9–14.9 Hz
wing-torsion mode. The QLOITER velocity and position gains are left at firmware defaults chosen for ordinary copters,
and nothing checks the separation. A velocity loop that is too fast against a 1 Hz attitude loop oscillates in QLOITER
and QLAND, right at touchdown. Change: SITL stage B case S3b, plus a tethered step in `TUNING-PLAN.md` step 4/5. Log a
1 m/s velocity-demand step in QLOITER and read the velocity-loop crossover. **Pass: ≤ 1/6 of the attitude crossover,
i.e. ≤ 1.0 rad/s at the 1.0 Hz roll loop** (CR ratio 6 rad/s : < 1 rad/s). If it fails, lower `Q_P_VELXY_P` /
`Q_P_POSXY_P` and record the values in `K09L.param`. Names to confirm on the 4.7.x tag in S1.

### G-10 (Minor): No EKF-innovation check in the log review (N-51)

CR p. 95: the filter's error models must be verified, and divergence is a known failure. Change: add to the
`TUNING-PLAN.md` step 3 "done when", and to every post-flight log review, **EKF innovation test ratios (velocity,
position, height, magnetometer) < 1 throughout, peak logged**. These are ArduPilot's XKF4 fields (names to confirm on
the 4.7.x log). Report the peak against `FS_EKF_THRESH` 0.8. A magnetometer ratio rising with current points at the
`R-COMPASS` 0.3 interference limit.

### G-11 (Minor): Wind limits not on a card, and the RFS wind ratio is unmeasured (N-12)

CR p. 22: gusting wind and turbulence make low-speed control hard. `R-WIND` (5 / 8 m/s) and `R-WIND-MEASURE` exist,
but the measurement is not done and there is no card. Change (H3): go/no-go **5 m/s steady, wingtip-into-wind landing
only**. The broadside landing limit is 4 m/s (`STATUS.md` R-WIND row), and the 5.4 vs 5.0 m/s landing margin is thin.
**Abort above 8 m/s gust → lay flat / land at once**; morning ≤ 5 m/s for first transitions (`TUNING-PLAN.md` step 7).
Rescale after `R-WIND-MEASURE`.

### G-12 (Minor): See-and-avoid procedure not written (N-14)

CR p. 40, 97 and 167: low-altitude VFR operations meet unannounced traffic, and "some form of proximity alerting device
will be necessary". Scaled: the spotter is that device (`R-SITE`). Change (H3 card): the spotter's only job is the sky
and the zone. Use a fixed call ("TRAFFIC – [direction]") that means: Q mode → QLOITER and descend; FW → descend below
the traffic or RTL. Brief RFS's other users before each session. No ADS-B receiver is proposed: there is $0 of
reserve headroom (`STATUS.md` issue 2).

### G-13 (Minor): Pilot display fields not fixed (N-29)

CR p. 52 and 54: a direct readout of position and course deviation for landing, take-off and missed approach. Change
(F5): list the Yaapu screen fields in `RC-LINK.md`. They must include distance and bearing to home, altitude, climb
rate, groundspeed, mode, battery mAh used, and link quality. Add distance-to-home to the EdgeTX fallback page. Check at
`T-F5-BENCH`.

### G-14 (Minor): Pilot fatigue not limited (N-59)

CR p. 169: fatigue "would be more of a factor during inflight anomalies than during normal operations". Change (H2/H3
card): a maximum number of flights per pilot per session and a rest between flights (values —, H2 sets). Keep the
existing "one parameter change per flight" rule (`TUNING-PLAN.md` rules). Rotate the spotter role.

## 5. Proposed changes, for the integrator

Nothing below has been applied. Other engineers are editing these files; apply in a new F4 / H3 revision and re-run
`python -I redesign/team/F4/fsw_check.py` (and add `Q_FW_LND_APR_RAD`, `Q_TRANS_DECEL` to `params.json` so the mirror
check passes).

| # | File | Key / location | Old → new | Why | CR page | Gap |
|---|---|---|---|---|---|---|
| C-01 | `subsystems/flight-software/K09L.param` (+ `params.json` mirror) | `Q_RTL_MODE` | 1 → **2** (VTOL approach: circle down to `Q_RTL_ALT`, transition into wind, QRTL) | no downwind back-transition; wing-borne spiral instead of a 50 m hover descent | p. 35, 38–39, 172 | G-01 |
| C-02 | same | `Q_RTL_ALT` | 30 → **50** m | mode 2 transitions at `Q_RTL_ALT`; keeps `transition_alt_min_m` 50 (`R-TEST-ORDER`) | p. 35, 172 | G-01 |
| C-03 | same | `Q_FW_LND_APR_RAD` (new line) | not set (default —) → **60** m (= `RTL_RADIUS`, bank 23.5° at 16 m/s, EST) | spiral radius inside the Table 29 bank range 9–30° | p. 165, 174 | G-01 |
| C-04 | same | `Q_TRANS_DECEL` (new line, default stated) | not set → **2.0** m/s² (default, stated) | fix the approach deceleration with the descent angle; 64 m stop (EST) | p. 19 Eq. (1) | G-07 |
| C-05 | same | `FENCE_TYPE` | 3 → **7** after the polygon is uploaded and corners read back (already planned in l.334) | positive obstacle and boundary avoidance; entry-error check | p. 54, 168 | G-04 |
| C-06 | same | `Q_P_VELXY_P`, `Q_P_POSXY_P` (new lines after the test) | firmware default → value from SITL S3b / tether step, crossover ≤ 1/6 of attitude (≤ 1.0 rad/s) | inner loops faster than outer | p. 61 | G-09 |
| C-07 | same | `Q_LAND_FINAL_ALT` | 6 → 6 + measured baro error at touchdown, only if M1 > 1 m (EST) | final rate must start above the ground | p. 59 | G-06 |
| C-08 | `subsystems/flight-software/SITL-PLAN.md` | new case S18 "RTL VTOL approach" | — → RTL from 200 m in 5 m/s wind from N/E/S/W; pass: back-transition heading within ± 45° of into-wind (EST), overshoot past home logged, ≤ 10 m height loss | verify C-01–C-04 on a tailsitter | p. 35, 38–39 | G-01, G-07 |
| C-09 | same | new case S3b; S3 pass line | "±1 m" → "95 % of samples within 1 m"; S3b velocity step, crossover ≤ 1.0 rad/s | statistical accuracy; loop hierarchy | p. 49, 61 | G-08, G-09 |
| C-10 | same | S9 | add polygon and exclusion-zone breach | fence as obstacle avoidance | p. 54 | G-04 |
| C-11 | `subsystems/flight-software/TUNING-PLAN.md` | step 3 "done when" | + EKF innovation ratios < 1, peak reported against `FS_EKF_THRESH` 0.8 | verify filter models | p. 95 | G-10 |
| C-12 | same | step 5 | + go-around practice (QLOITER, climb ≥ 10 m, re-try, alternate spot); + horizontal speed at contact logged against the G-05 limit; "within 1 m" → 95 % form | missed approach; touchdown velocity | p. 33, 39, 60 | G-02, G-05, G-08 |
| C-13 | `subsystems/flight-software/SPEC.md` | Transition logic table, back-transition row | + "pilot-flown back-transition only heading into wind"; RTL row → `Q_RTL_MODE` 2 | no downwind approach | p. 35, 172 | G-01 |
| C-14 | `team/A2/REQUIREMENTS.md` | `R-LANDING-IMPACT` | + horizontal groundspeed at contact ≤ — m/s (C5 derives) | touchdown velocity tolerance | p. 60 | G-05 |
| C-15 | `team/A2/REQUIREMENTS.md` | `R-TWIN`, `R-SITE` | "within 1 m" → 95 % form; `R-SITE` + field-map sheet (zone, sector, alternate, obstacle survey, pre-flight walk) | statistical accuracy; clearance surfaces | p. 49, 42, 58–59, 166–167 | G-03, G-08 |
| C-16 | H3 flight card (to be written) | sections | + go-around, alternate spot, wind go/no-go, traffic call, field walk, back-transition into wind, fatigue limit | procedures | p. 22, 33, 35, 39, 167, 169 | G-02, G-03, G-11, G-12, G-14 |
| C-17 | `team/F5/RC-LINK.md` | "Live flight data" row | + list of Yaapu fields incl. distance/bearing to home; EdgeTX page + distance to home | pilot position readout | p. 52, 54 | G-13 |

## 6. What the team must measure

| # | Measure | How (cheap method) | Fails when |
|---|---|---|---|
| M1 | Baro height error at touchdown | log BARO / EKF height at disarm vs 0 at arming, 10 flights, same pack and morning | \|error\| > 1 m (EST): C-07 applies; > 5 m: the final 0.3 m/s may start below ground level (`Q_LAND_FINAL_ALT` 6) |
| M2 | Horizontal groundspeed at contact | GPS velocity at the RC9 cut in every logged landing (`T-F4-TD-CUT` logs) | above the G-05 limit (—, C5) → tip-over risk; also reports 2 kt = 1.03 m/s as the CR reference |
| M3 | Vertical-speed noise in hover near the ground | tethered hover at 1 m: σ of EKF climb rate over 60 s | σ > 0.03 m/s (10 % of `Q_LAND_FINAL_SPD`, scaled from CR p. 59) |
| M4 | Velocity-loop crossover in QLOITER | SITL stage B, then tethered: 1 m/s step | > 1.0 rad/s at the 1.0 Hz roll loop (CR p. 61 ratio) |
| M5 | Back-transition heading and overshoot under `Q_RTL_MODE` 2 | SITL S18, then one RTL at ≥ 50 m in ≤ 5 m/s | heading > 45° off into-wind (EST), or overshoot past the 250 m fence |
| M6 | EKF innovation peaks | every log, XKF4 test ratios | any ratio ≥ 1 for > 1 s, or within 0.2 of `FS_EKF_THRESH` 0.8 |
| M7 | Position-hold dispersion | QLOITER 2 min in 5 m/s | 95th percentile > 1 m (`R-TWIN`) |

## 7. Method, page map and pages not read

**Page map.** PDF image `pNNN` = report page + 14 for pp. 1–63. Page 64 is blank, not filmed, so the offset is +13 for
pp. 65–100 and +12 for pp. 117–169 (a second unfilmed page falls between p. 100 and p. 117). Page 170 is blank, not
filmed, so the offset is +11 from p. 171. Checked on p. 6 = p020, p. 65 = p078, p. 91 = p104, p. 119 = p131,
p. 167 = p179, p. 171 = p182.

**Read in full:** pp. 6, 8–9 (§2.1.2), 16–28 and 30–33 (§2.2, §2.3 incl. §2.3.4), 34–45 (§2.4), 45–63 (§2.5, all
subsections and Table 11), 65 (§3 opening), 91–100 (§3.4–3.7 opening), 117–135 (§4.2.1–4.3.3, incl. §4.2.3 and
§4.3.2), 164–169 (end of §5.3.4 incl. Table 29, all of §5.4), 171–178 (§6).

**Not read:** front matter and §1 (pp. 1–5, 7, 10–15); p. 29 (Fig. 13, NYA approach plates); §3.1–3.3 navaid
descriptions (pp. 66–90); §3.7 remainder and §4.1 (pp. 101–116); §4.3.3 remainder after p. 135; §5.1–5.3.3
(pp. 136–163); appendices and references. None of these sets a number the read sections cite as a requirement, except
Table 1 pad sizes (p. 8 gives 200 ft and 300–400 ft square, used here). Every page attempted was legible. No page
failed to load.

**External checks (2026-11-13):** ArduPilot `ArduPlane/quadplane.cpp` on master (raw GitHub) for `Q_RTL_MODE` values
and description, `Q_TRANS_DECEL`, `Q_OPTIONS` bits, `Q_LAND_FINAL_ALT/SPD`, `Q_PILOT_SPD_DN`. These are master-branch
texts; the 4.7.x tag on the CoreWing F405 is confirmed only by SITL S1.
