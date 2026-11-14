# Judge: flight risk and controllability

Status: PROPOSED (flight-risk judge, 2026-11-09). One lens only: **how likely is a first-time team to fly it
successfully and safely** — hover, transition, cruise, landing, wind; autopilot maturity; failure modes; testability
in stages. Budget, buildability, schedule, transport and mission fit are other judges' lenses and are not scored here,
though they are named where they touch flight risk (a cheap crash is a flight-risk advantage; a mission miss is not).

Inputs: `requirements/REQUIREMENTS.md` §5 (flight-risk anchors: 0 = no documented hobby builds on the chosen autopilot,
or any single motor-out fatal in hover *and* cruise; 10 = ≥ 5 documented builds, hover T/W ≥ 2.0, gust tilt ≤ 15°,
motor-out survivable in cruise), D11 (T/W ≥ 1.6, 2.0 recommended; 5 m/s steady, 8 m/s gust), D15 (pilot readiness);
`screening/SCREENING.md`; every `cards/*/CARD.md` and `REVIEW.md`. **Skeptic-corrected numbers are used throughout.**
`ESTIMATE` = this judge's engineering guess; `UNVERIFIED` = claim resting on forum data.

Context that applies to every concept: one airframe, one budget, a first-time pilot, and a bay-shore test site (RFS)
with a routine afternoon sea breeze. The two things that most change the odds of *flying successfully* are therefore
(a) how many flight hours the team logs before the hard parts, and (b) what one crash costs in time and money.

---

## 1. Ranking

| Rank | ID | Concept | Score 0–10 | One-line reason |
|---|---|---|---|---|
| 1 | **U01** | Wing-assisted quad, ArduCopter | **8.0** | No transition to fail, the most mature autopilot path, staged by nature (fly the bare quad, then tape on the wing). Loses points for quad motor-out and a wing whose lift changes sign through 6–13 m/s. |
| 2 | **B08** | HEEWING T1-S tilt-tri PNP | **7.5** | Flown by hundreds, official ArduPilot board, flies in build week 1–2, and a crash costs foam. Loses points for 0.7 kg in a bay-shore breeze, 9 g tilt servos, and a reported factory transition abort and an unresolved QLOITER failure. |
| 3 | **K01** | Twin-boom quadplane 4+1 | **7.0** | The best-documented VTOL transition, a tailed airframe, motor-out survivable in cruise. Loses points for T/W 1.70 with sag, zero static margin as drawn (fixable), no hover motor-out, and first hover only in week 6–8. |
| 4 | **K19** | Flying-wing quadplane 4+1 | **6.0** | Same transition logic as K01 but tailless: ±13 mm CG window, elevon-only pitch once lift fades, weak hover yaw, T/W 1.6 at end of pack. Centre-section-as-quad test is a real plus. |
| 5 | **B09** | Printed Flightory Stallion tilt-tri | **5.0** | Good T/W (2.15 worst motor) and a V-tail, but no published PIDs, motor and prop off the designer's list, LW-PLA that resonates, softens at 50 °C and shatters in a crash. Rear motor and tilt servos are single points of failure. |
| 6 | **K06** | Scratch tilt-tricopter | **4.0** | T/W 1.62 fresh / 1.53 at end of pack, three classes of single-point failure in hover (any motor, ESC, tilt servo), tailless with ~3 % static margin, and a tilt transition the team tunes from scratch. Good in wind (8° at 8 m/s). |
| 7 | **K09** | Quad tailsitter, motor-only | **3.5** | T/W 2.6 is the best in the set, but 36° lean in an 8 m/s gust, a fin landing that tips at 39°, roll in cruise from motor torque alone (one builder: "unfeasible in most cases"), and motor-out fatal in both modes — the §5 zero anchor. Elevons (+$30) lift it to about 5. |

Scores are this judge's judgement, not an average of the table in §2; they tilt toward crash consequence and
time-on-airframe because those decide whether a first-time team's single airframe is still flying in April.

---

## 2. Phase-by-phase matrix (0–10 per cell, corrected numbers)

| Phase | U01 | B08 | K01 | K19 | B09 | K06 | K09 |
|---|---|---|---|---|---|---|---|
| **Hover** (T/W, authority, SPOF) | 8 — T/W 2.2, pure quad, ArduCopter | 6 — T/W ≈ 2.0, 1.5 with growth; vectored yaw on 9 g servos | 6 — T/W 1.83 / **1.70 sag**; boom twist in foam saddles costs yaw | 5 — T/W 1.9 / **1.6 low-V**; weak torque yaw, 0.05 m² winglets | 7 — worst-motor T/W 2.15; rear carries 37 %; servo backlash → yaw wobble | 4 — T/W **1.62 / 1.53 end of pack**; rear motor margin 1.4–1.6 | 7 — T/W 2.6; stance 0.64 × 0.38 m on fin tips |
| **Transition** | 9 — none (no failure mode; see §4 on mission) | 6 — factory setup aborted at ~3 s (`Q_TRANS_FAIL`), tilt endpoints per aircraft; many T1 owners have flown it | 7 — speed-scheduled, `Q_ASSIST`; Vs 10.8, trans 14.1 m/s; **SM 0–3 % as drawn must be fixed first** | 5 — Vs 12.8, trans 16.6, cruise ≥ 17 m/s; CG ±13 mm; elevons only once lift fades | 5 — tilt, no PIDs, V-tail helps; Vs 10.7 (CLmax 1.2 optimistic `ESTIMATE`) | 4 — tilt, nose rears up as rear spools down; Vs 12.9, trans 16.8; 3–4 weeks of tuning on the card itself | 4 — 90° pitch-over and back; `Q_TAILSIT_*` scheduling by a first-time team; back-transition deceleration |
| **Cruise** | 7 — a quad at 16° nose-down; Su et al. "insignificant effect on controllability" (abstract, `UNVERIFIED` body) | 7 — small foam plane, 33–41 W; stopped rear prop | 8 — tailed, L/D 6.6–7.2, pusher-out → return to hover, lift-motor-out → glide | 7 — clean wing; pusher 27 mm from rear lift props (strike after a boom twist) | 6 — tailed; front-motor-out asymmetric; V-tail glide plausible | 6 — tailless; front-motor-out asymmetric on a tailless wing | 3 — roll from motor torque only; H-Wing saturation → uncontrolled roll; PX4 builder failed |
| **Landing** | 9 — quad land, 215 mm gear | 8 — hover land, 0.7 kg | 8 — QLAND on 0.18 m legs; pusher tip 5 cm off ground | 8 — QLAND on printed feet; props near ground | 7 — tilt back then QLAND on skids; LW-PLA skids brittle | 7 — tilt back then QLAND; TPU feet | 3 — vertical onto four fin tips in a crosswind, tip-over at 39° |
| **Wind** (5 m/s steady, 8 m/s gust) | 5 — wing ΔL −21 to +21 % W in a 5→8 gust; tailwind stalls wing at −25°; no weathervane in Copter | 3 — gust lift 0.2 W at 8 m/s; 12.6 m/s transition is 1.6 × gust; morning-only aircraft | 6 — 3.45 kg, tailed, `Q_WVANE`; gust tilt not quantified `ESTIMATE` ~20° | 5 — weak yaw saturates in gusts; `Q_WVANE` helps; card's own risk 2 | 7 — 12° at 8 m/s (card, `ESTIMATE`) | 7 — 8° bank at 8 m/s (card, `ESTIMATE`) | 2 — 16° at 5 m/s, **36° at 8 m/s**; flight card must say 5 m/s |
| **Autopilot maturity** | 10 — ArduCopter QUAD/X | 8 — official `HEEWING-F405v2` board; community 4.7.1 params; V1 no logging, V2 internal flash only, no on-board compass | 9 — `Q_FRAME_CLASS 1`, ≥ 5 builds; FC beta target → swap to SpeedyBee | 8 — X8/DeltaQuad lineage, ≥ 4 build threads; same FC caveat | 6 — tilt-rotor supported; output map supplied; **no PIDs**, deviated motor/prop voids them | 6 — `Q_TILT_TYPE 2` documented; Convergence/AR-Pro/Dolphin lineage; scratch geometry | 5 — `Q_TAILSIT_ENABLE 2` supported; H-Wing, Cygnet (forum, `UNVERIFIED` logs) |
| **Failure modes** (what one fault or one crash costs) | 5 — any motor/ESC fatal; crash = arms + foam half, ~1 day | 6 — any motor/ESC/servo fatal; **crash = foam + CA, spare airframe $434** | 5 — any lift motor/ESC fatal in hover; 93 A on a 70 A connector; no spar as drawn; crash = re-cut half in a day | 5 — as K01; joiner socket crushes at 4 g as drawn; boom hard-points tear out of foam (new centre section ≈ 15 h) | 3 — rear motor + 2 tilt servos fatal; **LW-PLA resonance, 50 °C HDT, brittle**; crash = 25 h reprint per wing half | 3 — rear motor, any ESC, either tilt servo fatal; crash = re-cut half 4 h + nacelle reprint | 2 — any motor fatal in hover *and* cruise; crash = re-cut core 1 day |
| **Staged testability** | 10 — bare quad first (is also the D15 trainer), then foam-board wing, same day | 9 — bench → thrust stand → QHOVER in week 1–2; months of flight time before April | 7 — thrust stand → tethered hover → car-top pusher/stopped-prop → QLOITER → FBWA with `Q_ASSIST` | 8 — **centre section hovers as a quad before the panels exist**; glide test only valid at ≤ 1.5 kg | 6 — one printed wing half + nacelle on the stand in week 1; tilt sweep | 6 — tilt-nacelle bench rig (200 cycles); tethered hover | 8 — $40 foam-board twin in 2 days: hover in a fan, then transition |

---

## 3. Per-concept reasoning

### U01 — 8.0
- **Why high.** It removes the transition, which is where every other concept's crash lives. ArduCopter QUAD/X is
  the most-flown autopilot path there is; the skeptic rates control risk 2/5, the lowest in the set. The test plan is
  the staging: fly the bare quad (which is also the D15 trainer), autotune, log passes, tape on a foam-board wing at
  20/25/30°, re-autotune. Nothing has to work the first time.
- **What costs it points.** A quad is dead on any motor or ESC failure (same as K01/K19/K09 in hover). The wing is a
  real disturbance: corrected lift goes from −19 % W at 6 m/s to +25 % W at 13 m/s (REVIEW §4), so the altitude loop
  absorbs a sign change while the aircraft accelerates; gusts swing lift ±21 % W; a tailwind in hover stalls the wing
  downward and Copter has no weathervane, so the pilot holds the nose into wind. Su et al. (AIAA 2023) found a 30°
  wing on a quad had an insignificant effect on controllability — that is one documented build, abstract only.
- **Outside this lens, but the team must know:** the skeptic says U01 *fails the stated mission* (no transition).
  High flight-risk score does not make it the answer; it makes it the safest thing to fly.
- **Would move the score:** fly the first winged passes in AltHold with `ANGLE_MAX` conservative (+0); a second
  pack-and-arm spare set so a crash is a same-day repair (+0.5).

### B08 — 7.5
- **Why high.** A PNP that hundreds of hobbyists have flown, on an official ArduPilot board, with a community
  parameter file. First hover in build week 1–2 means the pilot and the parameter set get two to three months of
  flying before April, which no scratch concept offers. A crash costs foam and CA; the corrected reserve (~$570)
  buys a whole second airframe. Through a flight-risk lens, cheap crashes are the strongest mitigation there is.
- **What costs it points.** It is a 0.7 kg aircraft at RFS: gust lift at 8 m/s is 0.2 W, and the 12.6 m/s transition
  is only 1.6 × the gust speed — this is a morning-only aircraft. Corrected T/W is ~2.0 and 1.5 with the growth
  allowance (the allowance is arguably moot on a PNP, but any added sensor or compass counts). The forum reports
  (`UNVERIFIED`): the factory setup aborted transitions at ~3 s until `Q_TRANS_FAIL` was zeroed; tilt endpoints must be
  bench-set per aircraft or the nacelles bind; one owner's QLOITER "worked on first flights, later all failed" with no
  resolution. The V1 board has no logging (fails D7), V2 logs to internal flash only, and there is no on-board
  compass. Tilt servos are 9 g and a single point of failure; spares are in the BOM.
- **Would move the score:** confirm V2 board on arrival and fit the external compass (+0); set a 5 m/s flight-card
  limit and log every flight (+0); the 21700 Li-ion pack the forum owner used cuts T/W to 1.8 — do not take it (−0.5).

### K01 — 7.0
- **Why high.** The 4+1 quadplane with a tail is the most-documented hobby VTOL transition. Speed-scheduled with an
  airspeed sensor and `Q_ASSIST`, stall 10.8 m/s (CLmax 1.1 is reasonable for a tailed wing), transition at 14 m/s.
  In cruise a lift-motor failure is a glide on the pusher and a pusher failure is a return to hover — the only
  concept besides K19 that meets the §5 "motor-out survivable in cruise" anchor. 3.45 kg with a tail and
  `Q_WVANE` is the most wind-tolerant hover in the set after B09/K06.
- **What costs it points.** Corrected hover T/W is 1.83 on the table and **1.70 with sag**, below the 2.0
  recommendation, and any lift motor or ESC out in hover is a crash (K21 hexa fixes both for +$102; the skeptic says it
  now earns its weight). The CG is set at the lift centroid, giving a **static margin of 0–3 %** (REVIEW C4) — in FBWA
  cruise that is pitch-sensitive or divergent. It is a drawing error, not a layout fault, and the fix (front motors
  forward, or a larger tail, then an XFLR5 check) must happen before the order freeze; the score assumes it does.
  As drawn there is no spar (foam at ~0.41 MPa at 3 g) and boom twist in foam saddles turns into lost yaw authority.
  The corrected transition peak needs 93 A on a 70 A-continuous connector. First hover is in build week 6–8, so the
  pilot has fewer flying days than B08/U01 before the first transition, and one March crash is a day of foam work but
  a week of calendar.
- **Would move the score:** K21 hexa (+1.0: hover motor-out survivable, T/W 2.7); static-margin fix verified in
  XFLR5 and spar added (required to keep 7.0, else −1.5); 4S 5000 pack (T/W 1.77 sag, +0.25).

### K19 — 6.0
- **Why mid.** Same QuadPlane logic, firmware and transition scheduling as K01, and the flying-wing quadplane is well
  flown (DeltaQuad, many X8 threads). The build-order test is excellent: the centre section with booms *is* a
  quadcopter and can be hovered on a tether before the outer panels exist.
- **What costs it points.** Tailless. Static margin ~8 % MAC is a **±13 mm CG window**; pusher thrust line, parked-prop
  drag and the pack position all move trim, and the elevons are the only pitch control once lift motors fade — a wrong
  CG shows up exactly at transition. Trimmed CLmax ~0.65 gives Vs 12.8 m/s, transition ≥ 16.6 m/s and cruise ≥ 17 m/s:
  everything happens faster than on K01. Four 11 in props on a 3.3 kg wing with 0.05 m² of winglet give weak torque yaw
  that 8 m/s gusts can saturate. Corrected T/W is 1.9 fresh and **1.6 at low voltage** — right at the gate at the end
  of a pack, which is when the back-transition and landing happen. The joiner socket crushes at 4 g as drawn
  (REVIEW #8, fix required); hard landings can tear the boom saddles out of the foam. The card's hand-glide at 3.1 kg is
  not throwable; at ≤ 1.5 kg it is.
- **Would move the score:** 3° motor tilt for yaw + `Q_WVANE_GAIN` tuned in the centre-section stage (+0.5); fly the
  first transitions ≥ 30 m with `Q_ASSIST_SPEED` 12 (assumed); hexa not offered on this card.

### B09 — 5.0
- **Why mid.** Worst-motor T/W 2.15 with sag (1.96 pessimistic) is comfortably above the gate; a V-tail gives
  conventional pitch authority through transition; 12° gust tilt. The layout is a scaled Convergence that others fly,
  and Flightory supplies an output map.
- **What costs it points.** The structure is the flight-safety risk: a builder reported wing resonance and "PLA not
  rigid enough"; LW-PLA's HDT is 50 °C (a car in spring sun), and it shatters rather than dents, so the first hard
  landing is a 25 h reprint, not a tape job. No published PIDs, so hover QAUTOTUNE and fixed-wing AUTOTUNE are done
  from scratch; the card's 1700 KV motor and 7 in props are off the designer's list, so even the base parameters need
  retuning. The single rear motor is both the most loaded (37 %) and a single point of failure, with its arm an
  `ESTIMATE` until the STEP files are measured; 16 g tilt servos are single points of failure whose backlash shows up as
  hover yaw wobble. An ArduPilot thread asking Stallion VTOL owners for flight data got no replies, so there is no
  documented log of this exact design transitioning on ArduPilot (`UNVERIFIED`).
- **Would move the score:** week-1 wing-half load test to 2.5 g with no permanent set, and a tap test for
  resonance (required to keep 5.0); fly the 7x3.5x3 prop that has a published thrust table (+0.25); 60 A ESCs
  instead of running 45 A ESCs at 100 % (+0.25).

### K06 — 4.0
- **Why low.** Corrected hover T/W is **1.62 fresh and ~1.53 at end of pack** — at or below the gate, and the rear
  motor's own margin is 1.4–1.6, so it saturates first in pitch. Three independent single points of failure in hover:
  any of three motors, any ESC, either tilt servo. The wing is tailless with ~3 % static margin before the
  destabilising tractor nacelles are counted (REVIEW C7). The tilt transition is the card's own risk 2: pitch trim
  changes as the rear motor spools down, the nose rears up, vectored-yaw gains need tuning, and the card budgets
  3–4 of the 12 weeks for it. Scratch-built tilt geometry adds the forum's usual reversed-servo and ESC-wiring
  surprises. Trimmed CLmax 0.75 gives Vs 12.9 and transition ≥ 16.8 m/s.
- **What saves it from lower.** The layout is the best-documented small VTOL after the plain quadplane
  (`Q_TILT_TYPE 2`; Convergence, T1, Stallion, AR-Pro, Dolphin). Side area is small, so an 8 m/s gust needs only ~8° of
  bank. The tilt bench rig (200 cycles at hover thrust) is a good staged test. Crash repair is fast (foam half 4 h).
- **Would move the score:** K07 fourth motor (+$78) takes sag T/W to ~2.0 at corrected mass (+1.0, still every
  motor/servo fatal); set the CG for static margin first, then place the rear motor (required); lighter tilt servos
  (−60 g, +0.25).

### K09 — 3.5
- **Why low.** Two things happen on every flight at a bay-shore site. First, hover in wind: 16° of lean at 5 m/s and
  **36° at 8 m/s** on a broadside wing (method accepted by the skeptic), and a fin landing in a gust tips over past
  39°. Second, cruise roll comes only from differential motor torque: the H-Wing thread reports motor saturation
  causing uncontrolled rolling at high throttle, and a PX4 builder of the same layout called motor-only roll
  "unfeasible in most cases" (both forum, `UNVERIFIED`). The skeptic rates control risk 4/5. Any motor failure is fatal
  in hover *and* cruise, which is REQUIREMENTS §5's explicit zero anchor. Tailsitter transition and back-transition
  tuning (`Q_TAILSIT_*` angles, gain scheduling against airspeed) is the least-documented path in the set for a
  first-time team.
- **What saves it from lower.** T/W 2.6 is the best hover margin in the study and lets the autopilot command up to
  ~66° of lean if `Q_A_ANGLE_MAX` is raised — the limit is the landing tip-over, not thrust. The $40 foam-board twin in
  two days is the cheapest, earliest de-risk of any concept: hover it in a fan at 5 m/s before cutting XPS. One piece,
  no joints, so nothing works loose in the field.
- **Would move the score:** two foam elevons (+$30, +0.05 kg) and `Q_TAILSIT_ENABLE 1` give real roll and pitch in
  cruise and let motor-only mode be an experiment, not the baseline (+1.5 → about 5.0); K11 biplane planform cuts gust
  lean to 30° (+0.5); a 5 m/s wind limit written on the flight card (required).

---

## 4. Findings that cut across the set

1. **Every concept is dead on a hover motor-out** except K01 with the K21 hexa option. Since the §5 anchors treat
   motor-out as a major discriminator, the hexa is the only cheap way to buy real redundancy; nothing else in the set
   can. Tilt-tris (K06, B08, B09) add tilt servos as a second class of single-point failure.
2. **Corrected hover T/W splits the set:** K09 2.6, U01 2.2, B09 2.15 (worst motor), B08 ~2.0, K01 1.70 (sag),
   K19 1.6 (low voltage), K06 1.53–1.62. Only three concepts meet the 2.0 recommendation; two sit on the 1.6 gate at
   end of pack, which is exactly when the back-transition and landing happen.
3. **Tailless pitch trim appears three times** (K19, K06, and K09 by nature) and K01 has a zero-margin CG as drawn.
   Only B09 (V-tail) and K01-after-fix carry conventional pitch stability through transition. For a first-time
   team, a tail is worth more than its drag.
4. **Wind decides the test calendar.** K09 (36°) and B08 (0.2 W gust lift at 0.7 kg) are morning-only aircraft; K06
   and B09 (8–12°) are the most wind-tolerant; K01/K19/U01 sit between. Any concept needs a wind limit on the flight
   card; for K09 and B08 that limit is the design.
5. **Time on the airframe is the biggest single risk reducer** and it is inversely related to build hours: B08 and
   U01 fly in weeks 1–3, K09 in ~3, K19/B09 in 3–4, K01/K06 in 5–8. A concept that first hovers in March has one
   chance at its transition campaign.
6. **Crash cost in hours**: foam (K01, K19, K06, K09, U01 wing) ≈ 4 h–1 day; EPO PNP (B08) ≈ an evening or a $434
   spare; LW-PLA (B09) ≈ 25 h per wing half. B09 is the only concept where a crash can also be a structural *cause*
   (resonance, heat softening) rather than only a consequence.
7. **Firmware board**: K01, K19, K06, U01 all name the CoreWing F405 Wing V2 (1 MB flash, beta or vendor-hex history,
   naming confusion with the SpeedyBee). Before any order, confirm a *stable* build with the needed VTOL mode on
   firmware.ardupilot.org, or move to a Matek/SpeedyBee board. This is a one-hour check that removes a controls risk
   shared by four concepts.
8. **Every controls-maturity cell rests on forum evidence** (`UNVERIFIED`); the three `research/*/FINDINGS.md` files
   were absent at screening. A documented transition *log* (not a video) for the tilt-tris (K06, B08, B09) and the
   tailsitter (K09) is still missing. The quadplanes (K01, K19) and the quad (U01) are the only layouts whose flight
   record does not depend on a thread.

---

## 5. Confidence

| ID | Confidence in score | Why |
|---|---|---|
| U01 | High | ArduCopter is well known; one AIAA flight test of the same arrangement. The open question (wing payoff) is not a flight-risk question. |
| B08 | Medium-high | Many owners; specific forum failure reports; the aircraft's own numbers (props, span, T/W) were wrong on the card and corrected by the skeptic. |
| K01 | High | Best-documented layout; the T/W and static-margin corrections are calculations, not guesses. |
| K19 | Medium | Tailless trim and yaw behaviour are `ESTIMATE`; the X8 lineage is close but not this wing. |
| B09 | Medium-low | No owner flight data found; LW-PLA behaviour is from one builder's report. |
| K06 | Medium | Layout well documented; this specific scratch geometry and its CG are not. |
| K09 | Medium | Lean-angle method accepted; roll-authority evidence is two forum threads pointing opposite ways. |
