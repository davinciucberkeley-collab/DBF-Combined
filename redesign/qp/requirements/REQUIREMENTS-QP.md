# Small quadplane: requirement set (QP-1, A2)

Status `PROPOSED`, 2026-11-14, QP-1 round. Owner A2. Nothing built or flown; every quadplane number is `EST` unless a source says otherwise. `—` is unknown.
Paths are relative to `redesign/`. Airframe basis: candidate B of `config-study/RESTUDY-2026-11-14.md`. The K09-L tree was only read.

**QP-B working point (all `EST`, restudy section 2):** MTOW 1.88 kg, wing 0.30 m^2 / 1.40 m, stall 9.6 m/s, 1.3 Vs 12.5 m/s, hover T/W 2.13 on 4 lift motors (SunnySky X2212 KV980, thrust `EST` 1.0 kgf each), hover 277 W, cruise 65 W, one 4S 3000 mAh pack (44.4 Wh), 2 flight packs, total $1,625, margin +$375 (+$175 with candidate parts +30 %). Motor thrust is not measured: test QP1-2 (`TEST-PLAN-QP1.md`) replaces it.

**Classes** (as in `review/CLOSURE-ROUND-2026-11-14/A2.md` section 1): `USER` = a user constraint (budget, schedule, portability, 3-D physics, plus the legal ceiling); `PHYS` = physical, safety or legal limit; `DERIVED` = a team or agent choice with its basis stated. **Disposition:** carry (same text and value), adapt (same intent, new value or wording), drop, new.

## 1. User requirements (the only fixed ones)

| ID | Requirement | Class | K09-L | Disp | Basis |
|---|---|---|---|---|---|
| QP-U1 | Total physical spend <= $2,000 incl. tax, shipping, packs, charger, radio, test gear, crash reserve. Jacobs Makers Pass outside the budget | USER | R-BUDGET | carry | root `CLAUDE.md`; `qp/README.md`. Restudy B: $1,625 `EST` |
| QP-U2 | Built and flight-tested by 2027-04-30 | USER | R-SCHEDULE | carry | `CLAUDE.md`. Interior milestones are DERIVED (QP-D8) |
| QP-U3 | Portable: team of 4, < 25 kg, one piece in a car box | USER | R-TRANSPORT, R-CAR-FIT, R-ENVELOPE | adapt | `CLAUDE.md`. K09-L's 1.25 m box came from a 1.15 m span; **QP-B span 1.40 m does not fit it. Open: D-QP-1, not decided here** |
| QP-U4 | 3-D gates (CLAUDE.md wording "3-D physics simulation"; computed: interference check, static; swept insertion check, straight-line paths): no floating parts, no phasing, assembly motions swept | USER | R-NO-FLOATING | carry | `CLAUDE.md`; tools in `CARRY-OVER.md` |
| QP-U5 | Mass < 25 kg (55 lb) | USER/LEGAL | R-LEGAL, `mass_max_legal_kg` | carry | `CLAUDE.md`. QP-B 1.88 kg `EST` |

## 2. K09-L requirements: carry / adapt / drop

Every ID of the closure table in `review/CLOSURE-ROUND-2026-11-14/A2.md` section 1 appears below once (or in section 2.5).

### 2.1 Mission, mass, energy

| QP ID | K09-L | Disp | Class | Quadplane requirement | Basis |
|---|---|---|---|---|---|
| QP-D1 | R-CONFIG | adapt | USER-derived | Small quadplane, 4 lift + 1 pusher (D-181); fallback ZOHD Altus | `qp/README.md` |
| QP-D2 | R-MISSION | adapt | DERIVED phases, PHYS-linked 20 % reserve | Hover-mode time 3.0 min total, cruise 3.6 min, reserve 20 % (section 3) | A2.md 2.1 redone at 15 m/s |
| QP-P1 | R-MASS-GATE | adapt | PHYS | Gate = largest mass with hover T/W >= 2.0 on the **measured** motor row at the 14.8 V table: m_max = 4 T_motor / (2.0 g). `EST` 2.0 kg at 1.0 kgf; sized 1.88 kg. Value `—` until QP1-2 | K09-L rule (T/W binds the gate), A2.md 2.2 |
| QP-D3 | R-MASS-ALLOC, growth, overrun | adapt | DERIVED | Allocations booked by A3 roll-up; growth and first-build overrun as a percent of sized mass (K09-L overrun 84 g of 2.6 kg = 3.2 %, `build_overrun_kg`); 4 % `EST` until a roll-up exists | `params.json` |
| QP-P2 | R-HOVER-TW | carry | PHYS | Hover T/W >= 2.0 fresh at gate mass (4 motors, no cant); >= 1.6 on the worst pack state (20 % rest voltage 3.73 V/cell); hover throttle <= 1/1.6 = 0.625 | `hover_tw_min`, `hover_tw_min_sag`; A2.md 2.3. Restudy 2.13 `EST` |
| QP-P3 | R-HOVER-AUTHORITY, R-GUST-LEAN | adapt | PHYS | Authority >= 1.5 x disturbance at 5 m/s on every hover axis; no lift motor above 85 % or below 10 % output in a 5 m/s hover (H2 gate 1d line); 8 m/s gust: lean <= `Q_A_ANGLE_MAX` - 5 deg with 1.3 thrust headroom | `hover_ctrl_factor`, `gust_*`; H2 plan 1d |
| QP-P4 | R-HOVER-SPLIT | adapt | PHYS | Front/rear pair thrust ratio for CG offset d from the lift-motor centroid, arm a: (a+d)/(a-d) <= 1.25, so d <= 0.111 a. a is `—` (geometry) | `hover_split_max` 1.25; formula derived here |
| QP-P5 | R-CG-RANGE, R-STATIC-MARGIN | adapt | PHYS | Cruise CG ahead of the neutral point by >= 5 % chord (floor kept), lateral CG within 5 mm, CG within d of the lift centroid (QP-P4). Marks `—` until aero gives the neutral point | `static_margin_min`, `cg_lateral_max_m` |
| QP-D4 | R-PACK-MASS | adapt | DERIVED | Pack accepted at <= listed mass + 5 g (CNHL 4S 3000 listing 356 g, `U`) and fits the bay | K09-L D-64 rule |
| QP-P6 | R-PACK-RETENTION | carry | PHYS | Pack retained at the design crash decel (K09-L 12 g, C1 12.75 g); re-derive if landing sink changes | `crash_decel_g` |
| QP-D5 | R-RESERVE, R-CRASH-REPAIR | adapt | DERIVED | Crash reserve = (one flight pack + one servo + one airframe set not already spared) x 1.1025 + 2 shipments, pessimistic prices; restudy $150 `EST`. Spares already in the spend are not billed twice | restudy section 1; A2.md 2.4 |

### 2.2 Flight envelope, transition, assist

| QP ID | K09-L | Disp | Class | Quadplane requirement | Basis |
|---|---|---|---|---|---|
| QP-P7 | R-STALL | adapt | DERIVED | Trimmed clean stall Vs <= AIRSPEED_MIN / 1.3. At QP-B: Vs 9.6 `EST`, AIRSPEED_MIN 13 (integer, `EST`), limit 10.0 m/s. Measured stall before AIRSPEED_MIN is frozen | A2.md R-STALL (D-96 method) |
| QP-P8 | R-TRANSITION | adapt | PHYS | Forward transition completes at >= 1.3 Vs (12.5 m/s `EST`). The pusher alone accelerates through 1.3 Vs while lift motors hold attitude: **pusher static thrust >= 0.25 W** (0.47 kgf at 1.88 kg) `EST`, about 0.15 g net after drag; transition 10-15 s | restudy `trans_s` 15; rule DERIVED here, checked by QP1-2 |
| QP-P9 | **Q_ASSIST** (new) | new | PHYS | Assist engages above stall and below normal cruise: Vs + 2 m/s <= `Q_ASSIST_SPEED` <= AIRSPEED_MIN. The 2 m/s covers a 1-2 m/s^2 deceleration over `Q_ASSIST_DELAY` plus spool (`EST`). QP-B window 11.6-13 m/s, cruise 15. `Q_ASSIST_ANGLE`, `Q_ASSIST_ALT` set; assist cannot exceed the lift T/W of QP-P2. No speed-based assist on synthetic airspeed (Q_OPTIONS bit 12; bits 7, 8, 18, 19 also read, https://ardupilot.org/plane/docs/quadplane-parameters.html, fetched 2026-11-14), so the airspeed sensor is required. Names exist in `team/F4/ap_plane_param_names_4.7.1.txt`; values `—` until SITL and flight. **Conflict, not picked:** the older C0 file (`../firmware/vtol_c0.param`) sets assist 3 m/s below AIRSPEED_MIN (stall 12, min 16), which at QP-B gives 10.0 m/s, only 0.4 above stall; the Vs + 2 rule gives 11.6 | tests QP1-4 |
| QP-P10 | R-AIRSPEED | carry | PHYS | Airspeed error <= 0.5 m/s at cruise; pitot (<= 2 % error) outside lift and pusher wash | `airspeed_err_max_ms`; restudy floor has Matek ASPD-4525 |
| QP-P11 | R-CRUISE-AUTHORITY, R-SERVO-TORQUE | adapt | PHYS | Conventional surfaces: roll rate >= 90 deg/s at cruise; servo stall torque >= 1.5 x hinge moment (EMAX ES3352HV 1.7-2.4 kgf-cm `U`, adequate below about 2.5 kg `EST`) | `roll_rate_min_degs`, `servo_torque_factor` |
| QP-P12 | R-DIRECTIONAL, R-SPIRAL | carry | PHYS | Cn_beta >= 0.03 /rad, no spiral divergence; tail volume sets it, pusher and booms count | `cnbeta_min` |
| QP-P13 | R-LOADS, R-STRUCT-MARGIN, R-JOINT-STACK | adapt | PHYS | Limit load factor +3.4 / -1.5 as a floor, ultimate 1.5 x limit, VD = 1.25 VH and the 8 m/s gust line re-run at QP-B speeds; MS >= 0 at 1.5 x limit on spar, booms, joiners, gear | `load_factor_limit_*`, `vd_ms`, `safety_factor_ult` |
| QP-P14 | R-WIND | carry | DERIVED value, PHYS checks | Flight-card wind <= 5 m/s steady; survive-and-land 8 m/s gust; gate together with QP-P3 | H3 flight card limits 1-2 |

### 2.3 Quadplane-specific

| QP ID | K09-L | Disp | Class | Requirement | Basis |
|---|---|---|---|---|---|
| QP-P15 | **lift-motor-out** (new); R-FAILSAFES, R-ARM-KILL | new | PHYS | (a) **Hover / QLOITER, one lift motor out: not survivable** with 4 fixed rotors in an X (no authority on that corner); 6 or 8 rotors are outside $2,000 `EST`. Declared, not hidden. Controls: motor test before every flight; no motor above 85 % output (QP-P3); winding and ESC current within rating (QP-P19); thermal pass (QP1-2). (b) **Forward flight, lift motors parked:** failure is found at back-transition spin-up; abort to a fixed-wing glide and belly landing; airframe sacrificial, QP-D5 covers it. (c) **Pusher out in cruise:** glide on the wing, Q_ASSIST holds, then QRTL or QLAND; needs the 20 % reserve. (d) Never start a forward transition after a failed motor test. (e) Each case run in SITL and recorded (QP1-4); real behaviour `—` | A2.md 2.3 |
| QP-P16 | **boom stiffness and vibration** (new); R-VIBRATION | new | PHYS | Boom + motor + prop bending and torsion modes each >= 20 % from 1P and 2P across hover-to-max rpm (`vibration_sep_frac` 0.2; hover 1P about 130 Hz, 2P about 260 Hz is `EST` from KV980 x 14.8 V x about 0.7). FC VIBE < 30 m/s^2 per axis, clip 0 (`fc_vibe_max_ms2`); notch from ESC rpm telemetry. Static: boom tip rotates the thrust axis <= 3 deg at 1.25 x max motor thrust (`EST`, structures to set); MS >= 0 at limit hover thrust plus landing load. Test: tap test, hover-log FFT | K09-L GT-16 / GT-18 methods |
| QP-P17 | **landing-gear tip-over** (new form); R-TIPOVER, R-LANDING-IMPACT | adapt | PHYS | Static tip-over angle, worst axis, worst flying CG >= 30 deg = 5 m/s hover lean 16 deg + 10 deg attitude error (K09-L derivation carried). Hard landing 1.2 m/s sink at <= 10 deg without gear or boom failure. Lift props >= 25 mm off the ground at 10 deg; pusher prop clear at flare attitude. Stance `—` | `tipover_min_deg` D-172; `landing_sink_ms` D-65 |
| QP-P18 | **pusher clearance** (new); R-PROP-CLEAR | new | PHYS | Pusher tip >= 25 mm (`prop_clearance_min_m`) from tail, boom, fin, rudder and any lift prop at every control deflection, and from the ground at the gear's strike angle; pitot out of the pusher wash; **parked lift props** stop aligned with the boom, drag measured in cruise power (parked-prop drag `—`; folding or braking `—`); CAD swept-volume keep-out passes | `check.py` keepout; D-QP-3 |
| QP-D6 | **VTOL-to-cruise energy split** (new) | new | DERIVED | Mission energy checked by phase: hover 13.9 Wh (65 %), transitions 3.8 Wh (18 %), cruise 3.9 Wh (18 %) `EST` (restudy powers 277 / 65 / 450 W). Pack need = E / (0.80 x 0.90) = 29.7 Wh; fitted 44.4 Wh. Flight pass: mAh per phase within +/-15 % of the model (`hover_current_tol`). Cruise costs 1.1 Wh/min against 4.6 hover, so the mission can lengthen in cruise before it touches the pack | restudy `physics()` |
| QP-P19 | R-ESC-CURRENT, R-THERMAL, R-DISCONNECT, R-AVIONICS-POWER | carry | PHYS | Winding and ESC currents <= rating; connector >= 1.25 x peak continuous; BEC >= 2 x servo stall; thermal limits from the maker (`—` until the X2212 datasheet and ESC rating are read); `Q_M_BAT_CURR_MAX` from the measured row | `disconnect_factor`, `ubec_factor` |
| QP-P20 | R-FC-STABLE, R-FSW-PARAMS, R-COMPASS | adapt | PHYS | Param file passes the firmware name check; compass interference <= 30 % at hover current; HDOP <= 1.2 at 3 min | `compass_interference_max`, `hdop_max` |
| QP-P21 | R-ARM-KILL, R-RC-LINK | carry | PHYS | Arm switch and hard kill stop all motors <= 1 s; ELRS LQ >= 0.9; RSSI at 100 m / 25 mW >= -93.8 dBm; RC loss in a Q mode -> QLAND | `estop_time_max_s`, F5 `RANGE-TEST.md` |
| QP-P24 | R-HARNESS-INSTALL | adapt | PHYS (support, chafe); mass check DERIVED | Wire support <= 0.15 m, bend radius and chafe rules, strain relief at motors and boom roots; harness mass allocation from the routed mass | `wire_support_max_m`; harness SPEC |

### 2.4 Process, site, build, transport

| QP ID | K09-L | Disp | Class | Requirement | Basis |
|---|---|---|---|---|---|
| QP-D7 | R-TEST-ORDER, R-TWIN | adapt | DERIVED | Gates in order, none skipped. **No twin**: the VTOL half is a plain quad and the fixed-wing half a plain plane, so each half is tested on the real aircraft (section 4). First forward transitions at >= 50 m (`transition_alt_min_m`), lowered only on logged evidence | A2.md R-TEST-ORDER |
| QP-D8 | R-BUILD-HOURS, R-SCHEDULE milestones | adapt | DERIVED | Hours and cure-chain limits `—` until I2 plans the quadplane; latest first tethered hover = 2027-04-30 minus the flight programme length minus one crash loop | A2.md 2.5 method |
| QP-D9 | R-PILOT | carry | DERIVED | >= 10 h SITL on the quadplane model with the team's param file, including motor-out and failed transition; stick time on a small quad before first hover | `sitl_hours_min`; H2 gate 0 |
| QP-P22 | R-SITE, R-LEGAL | carry | PHYS/LEGAL | RFS yellow fields, FRIA, VLOS <= 500 m, <= 400 ft, spotter, request >= 7 business days ahead; fence 250 m / 110 m (racetrack far point about 190 m) | H3 flight card |
| QP-P23 | R-BATT-HANDLING | carry | PHYS | LiPo bag, charge 10-45 C, no re-flying a part-used pack the same day | `team/H3/BATTERY-PROCEDURE.md` |
| QP-D10 | R-TRANSPORT (drop test, mass), R-FIELD-SETUP, R-CAR-FIT | adapt | DERIVED / USER | 0.3 m floor drop, <= 6 kg loaded, field setup <= 5 min one person. Box size open (QP-U3); each field joint counts against the 5 min | `box_drop_m`, `field_setup_max_min` |
| QP-D11 | R-PROCESS, R-PROOF-BUILD | carry | PHYS / DERIVED | Print bed 0.2 m; thread engagement minimums; claims graph with zero failing claims | `print_max_m`, `thread_engagement_*` |
| QP-D12 | R-WIND-MEASURE | adapt | DERIVED | Wind measured at the field before each sortie, ratio to RCMC1 < 1.4 | `wind_ratio_max`; `WIND-RFS.md` |

### 2.5 Dropped (tailsitter only)

| K09-L item | Why |
|---|---|
| R-ELEVON-AREA, `elevon_trim_travel_max`, elevon schedule | No elevons; QP-P11 covers surfaces |
| R-FIN-TUBE-JOINT, `foot_*`, `pad_mu_max`, `landing_n_design` (foot crush) | No fins or fin-tip feet; gear is QP-P17 |
| `Q_TAILSIT_*`, 7-10 deg motor cant, pitch-over entry (1.4 W, 0.80 control reserve), `hover_lean_max_deg` as a tailsitter criterion | No pitch-over; transition is QP-P8; lean 20 deg kept only as a hover criterion in QP-D7 |
| `foot_replace_max_min`, `core_recut_max_days` | No cartridge foot, no cored fin |

## 3. Mission re-derived from the flight-test programme (A2.md section 2.1)

Same method at QP-B speed (`EST`): cruise 15 m/s (1.56 Vs, above 1.3 Vs = 12.5 and above `Q_ASSIST_SPEED`).

| Cruise segment | Basis | Time |
|---|---|---|
| Settle to trimmed 15 m/s after the transition | K09-L 15 s, `EST` | 15 s |
| 2 laps | gate 1i precedent | 2 x 56.7 = 113.3 s |
| 1 go-around lap | flight card 4b | 56.7 s |
| Run-in into the wind | <= 1/2 lap | 28.3 s |
| **Total** | | **213.3 s = 3.56 min, requirement 3.6 min** |

R = 15^2 / (9.807 tan 30 deg) = **39.7 m**; leg 300 m; lap = 600 + 2 pi x 39.7 = 849.7 m = 56.7 s; far point 150 + 39.7 = **189.7 m**, inside the 250 m fence. (K09-L at 17 m/s: 3.41 min.)

Hover-mode time stays **3.0 min**: climb 0-50 m at 2 m/s 25 s, hold 35 s, descent 1.0 m/s 50 s, landing hover 30 s, one go-around 40 s = 180 s. The K09-L segments are carried because the 50 m transition rule is carried; the hold may shrink on logged evidence since there is no pitch-over check. Energy: restudy 180 s hover + 210 s cruise + 2 x 15 s transitions at 450 W = 21.4 Wh; with 213 s cruise 21.45 Wh.

## 4. Flight-test programme (basis of the mission and of the gate order)

1. Bench, props off: arm, kill, failsafes, motor map; RC range check.
2. Thrust stand: lift motor, pusher; restrained four-motor run.
3. Tethered hover, free hover, QLOITER, 5 m/s wind.
4. Fixed wing at >= 80 m: trim, AUTOTUNE, stalls (QP-P7), full-throttle level leg (QP-P8).
5. Transition at >= 50 m, assist check (QP-P9), 2 laps, back-transition; 20 landings, <= 2 touchdowns per sortie.
6. Full mission: QP-D2.

## 5. Open items for A1 and the team (not decided here)

| ID | Item |
|---|---|
| D-QP-1 | Span 1.40 m against the 1.25 m box: longer box (car cargo length `—`; `subsystems/transport/CAR-FIT.md` records no car measured), two-piece wing with a field joint, or a shorter span (stall rises). |
| D-QP-2 | A motor-out-capable layout (more rotors) is not affordable `EST`; confirm the declared non-survivable case in QP-P15. |
| D-QP-3 | Pusher or tractor; folding lift props (parked-prop drag unknown). |
| D-QP-4 | Load factors and 5 m/s wind are K09-L numbers; re-derive with the new wing. |
