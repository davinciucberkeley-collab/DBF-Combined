# Configuration study — decision document

Status: PROPOSED (study lead, 2026-11-09), for the team lead's decision. Ten-minute read. Every number is traceable to
a file in this folder; "corrected" means the skeptic's value from `cards/<ID>/REVIEW.md`, not the card's.
Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against a primary source, `ASSUMPTION` = the team can
overturn it.

**The answer in three lines.** Take **K09, the quad tailsitter (flat flying wing on four fixed motors), with two
elevons added**, into detailed design. Runner-up: **K01, the small twin-boom quadplane 4+1**. The decision flips to K01
if the $40 foam-board twin cannot hold position in a 5 m/s breeze, or if the team will not accept a 5 m/s wind limit
on the flight card at Richmond Field Station (§4.3).

Files behind this document: `requirements/REQUIREMENTS.md` → `concepts/MORPH.md` + `concepts/AUDIT-LOG.md` →
`screening/SCREENING.md` → `cards/{K01,K19,K06,K09,B08,B09,U01}/{CARD,REVIEW}.md` → `judging/*.md`.
`research/existing-vtol/` and `research/flight-control/` were empty when every file above was written; all
controls-maturity claims therefore rest on ArduPilot docs and forum threads cited in the cards (`UNVERIFIED`).

---

## 1. The question and the real constraints

**Question.** Which aircraft configuration should a first-time UC Berkeley MEng team design, build and fly between
January and the end of April 2027, with $2,000 total?

**Constraints the team lead actually set (2026-11-09).** Everything else in this study is a proposal.

| # | Constraint | Status |
|---|---|---|
| 1 | **$2,000 total, hard**, including tax, shipping, batteries, charger, radio, tools the team does not own, spares | Team lead: hard |
| 2 | **VTOL** ("a sort of VTOL drone") | Team lead: hard |
| 3 | **Easy to transport**: a normal car, carried and assembled by one or two people | Team lead: hard, unquantified |
| 4 | **Student-built** at Jacobs Hall (FDM, laser, hot-wire foam, hand tools) | Team lead: hard |
| 5 | **Schedule**: parts ordered mid-December 2026; build January/February; everything done by end of April 2027 (~12 weeks worst case, including one crash repair) | Team lead: hard |

**Mission (flagged `ASSUMPTION`).** The team lead said *VTOL demonstrator: vertical take-off, transition to forward
flight, short cruise, transition back, vertical landing, no payload*. The numbers used to size every card come from
`REQUIREMENTS.md` §3 "M-A", written by a previous agent: hover 2 min, cruise 5 min threshold / 10 min objective, 20 %
energy reserve, 0.25 kg growth allowance. Every shortlisted concept clears the 5 min threshold after correction, so
the mission numbers do not change the ranking; the word *transition* does (it removes U01, §3).

**Derived numbers the team should know are proposals, not constraints** (`REQUIREMENTS.md` §1, previous agent):
planning cap $1,850 so ≥ $150 stays as crash reserve; one or two boxes ≤ 1.2 × 0.5 × 0.4 m, no piece > 1.5 m, ≤ 15 kg
per box; hover thrust-to-weight ≥ 1.6 (2.0 recommended); hover controllable in 5 m/s steady / 8 m/s gusts. The legal
items are real: < 25 kg, FAA registration ($5), § 44809 recreational/educational path with TRUST, Richmond Field
Station is a FRIA (no Remote ID module needed there), campus flight request ≥ 7 business days ahead, logging autopilot.

---

## 2. How the space was explored

| Step | File | What happened |
|---|---|---|
| Morphological chart | `concepts/MORPH.md` | 11 dimensions × 67 options (lift method, cruise thrust, transition, wing form, control, rotor count, landing, breakdown, material, energy, buy/build). **33 concepts** written as code strings through the chart: 18 conventional (K), 7 buy-and-modify (B), 8 unconventional (U). |
| Completeness audits | `concepts/AUDIT-LOG.md` | **3 rounds** against ArduPilot docs, forums, vendor pages and three VTOL taxonomy reviews. Round 1 added 6 concepts (K19–K22, B08, B09), round 2 added 2 (K23, K24), round 3 added 2 (K25, U09); 33 candidates examined and rejected as variants. Declared **saturated** for lift method, rotor arrangement and transition method. **43 concepts** total. |
| Screening | `screening/SCREENING.md` | Deduplicated 43 → 24 families (19 concepts became options on a parent: folding props, foam board, hexa, wheels, biplane planform, etc.). Four quick numbers per family (cost, pack, build, controls). Result: **7 kept, 19 merged, 17 dropped**. |
| Cards + skeptic reviews | `cards/*/` | One sizing script, one priced BOM and a 3-view per shortlisted concept; a skeptic re-ran every script (all 7 reproduce byte-for-byte) and corrected inputs. **Every correction went the same way: heavier, more power, less reserve.** |
| Three judges | `judging/*.md` | Mission-and-learning, flight-risk, build-and-transport, each scoring the 7 on corrected numbers. |

**What was eliminated and why** (17 dropped; the 19 merged live on as options on a kept parent):

| Reason | Concepts |
|---|---|
| Over the raw $2,000 at today's prices | K02 C0-class quadplane (2.4 m, 6S: $2,003), K15 octo 8+1 ($2,350), B05 MFE Fighter kit (> $2,000, UK lead time) |
| No maintained ArduPilot/PX4 mode (campus logging rule D7) or none documented flying | K13 tandem wing, K14 box wing, K17 fan-in-wing, K23 folding-wing Transwing (hinge geometry unsolved by two students), K20 single-motor tailsitter (no hover yaw, no logged transition), K22 tri 3+1 (unflown) |
| Too many loaded mechanisms or a documented transition failure | K08 all-four tiltrotor (4 servos, builder gave up), K12 tilt-wing (wing pivot under full lift), K24 reverse tricopter (two failed transitions), K25 Y6 tilt (6 stations, documented stall/flat spin), K16 bicopter (builder gave up) |
| Covered by a cheaper or safer member of the same family | K10 twin tailsitter (any motor-out fatal in both modes; K09 covers the cell), U02 ring-wing tailsitter (poor L/D, largest side area) |
| Not a transition aircraft | K18 pure quad (kept as the trainer / hover test bed, not the aircraft) |

**The seven that reached cards:** K01 twin-boom quadplane 4+1 · K19 flying-wing quadplane 4+1 · K06 scratch
tilt-tricopter · K09 quad tailsitter · B08 bought HEEWING T1-S tilt-tri PNP · B09 printed Flightory Stallion (bought
files) · U01 wing-assisted quad on a bought frame.

---

## 3. Trade matrix

### 3.1 Gates first (pass/fail, `REQUIREMENTS.md` §5 step 1), on corrected numbers

| Gate | K01 | K19 | K06 | K09 | B08 | B09 | U01 |
|---|---|---|---|---|---|---|---|
| G1 ≤ $1,850 (reserve ≥ $150) | **Fail as costed** ($1,897, reserve $103); recoverable to ≈ $197 by dropping the RID module (RFS is a FRIA) and buying 2 packs | Pass ($1,810 / $190) | Pass ($1,705 / $295) | Pass ($1,632 / $368) | Pass ($1,430 / $570) | Pass ($1,695 / $305) | Pass ($1,626 / $374) |
| G2 VTOL | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| G3 Transport (car) | Pass, 1.2 m box 7 kg, back seat | Pass, 1.2 m box 6 kg | Pass, 0.88 m box | Pass, one piece, ≈ 1.25 m box 6 kg, back seat | Pass, maker case 0.75 m | Pass, 1.09 m box | Pass, 0.80 m box |
| G4 Buildable at Jacobs | Pass | Pass | Pass (team-designed tilt nacelle) | Pass | Pass (nothing to build) | **Conditional**: bring-your-own LW-PLA policy not found | Pass |
| G5 Legal (< 25 kg, supported autopilot mode) | Pass | Pass | Pass | Pass | Pass (V2 board only; V1 has no logging) | Pass | Pass |
| G6 Mission: hover 2 min + cruise 5 min, T/W ≥ 1.6, **transition** | Pass (T/W 1.70 sag) | Pass (T/W 1.6 at low voltage, no margin) | **Marginal** (T/W 1.53 at end of pack; K07 fourth motor needed) | Pass (T/W 2.6) | Pass (T/W 2.0; 1.5 with growth allowance) | Pass | **Fail: no transition** (skeptic and mission judge agree) |

Two concepts carry a flag into the ranking. **U01 is listed but not ranked**: it is a quadcopter carrying a wing (rotors
carry ≥ 75 % of weight at every speed, corrected), and the team lead's one sentence on the mission says *transition*.
Its real value is as the pilot trainer and hover test bed; about 70 % of its BOM transfers to any winner. **B08 is ranked
but set aside** (§4.2): it passes every gate and wins the arithmetic, but the team designs and builds nothing.

### 3.2 Weighted score (`REQUIREMENTS.md` §5 step 2 weights; judges' scores and corrected numbers)

How each criterion is filled, so the arithmetic can be checked:

| Criterion (weight) | Where the 0–10 comes from |
|---|---|
| Budget margin (25) | Anchor from §5: 0 at $150 reserve, 10 at ≥ $500, linear: score = (corrected reserve − 150) / 35, clamped 0–10 |
| Buildability (20) | Build-and-transport judge, sub-scores A process + B hours + C parts/joints + E repair/reserve, out of 8, × 10/8 |
| Flight risk (20) | Flight-risk judge's score as given |
| Schedule (15) | Corrected team-hours ÷ 35 h/week (build judge's rate) + tuning weeks from the card/review; 10 at ≤ 6 weeks, 0 at ≥ 12 weeks, linear; −2 if no tuning guide exists (B09 only: no published PIDs) |
| Transportability (10) | Build-and-transport judge, sub-score D (packability) out of 2, × 5 |
| Mission fit (10) | Mission-and-learning judge's score as given (transition, margin, growth, capstone content) |

| Concept | Budget (25) | Build (20) | Flight (20) | Schedule (15) | Transport (10) | Mission (10) | **Σ / 100** |
|---|---|---|---|---|---|---|---|
| **B08** buy T1-S PNP | 10.0 (reserve $570) | 9.4 | 7.5 | 10.0 (flies week 1–2) | 10.0 | 3.0 | 250 + 188 + 150 + 150 + 100 + 30 = **8.68** |
| U01 wing-assisted quad *(fails G6)* | 6.4 ($374) | 8.8 | 8.0 | 10.0 (3 wk) | 10.0 | 2.5 | 160 + 176 + 160 + 150 + 100 + 25 = **7.71** |
| **K09** quad tailsitter, motor-only as carded | 6.2 ($368) | 8.8 | 3.5 | 8.8 (2.2 wk build + 4.5 wk test loops) | 7.5 | 7.0 | 155 + 176 + 70 + 132 + 75 + 70 = **6.78** |
| **K09 + elevons** (recommended form) | 5.3 ($335) | 8.8 | 5.0 (flight judge: "about 5") | 8.8 | 7.5 | 7.5 (mission judge: "≈ 7.5") | 132.5 + 176 + 100 + 132 + 75 + 75 = **6.91** |
| K19 flying-wing quadplane | 1.1 ($190) | 5.6 | 6.0 | 8.8 (3.7 + 3 wk) | 5.0 | 6.0 | 27.5 + 112 + 120 + 132 + 50 + 60 = **5.01** |
| K06 scratch tilt-tri | 4.1 ($295) | 4.4 | 4.0 | 5.6 (5.1 + 3.5 wk tilt tuning) | 7.5 | 6.5 | 102.5 + 88 + 80 + 84 + 75 + 65 = **4.95** |
| B09 printed Stallion | 4.4 ($305) | 5.0 | 5.0 | 5.3 (3.6 + 1 queue + 3 wk, −2 no PIDs) | 5.0 | 4.5 | 110 + 100 + 100 + 79.5 + 50 + 45 = **4.84** |
| K01 twin-boom quadplane | 0.0 ($103) | 3.8 | 7.0 | 7.2 (4.7 + 3 wk) | 5.0 | 8.0 | 0 + 76 + 140 + 108 + 50 + 80 = **4.54** |
| K01 with budget recovery (drop RID, 2 packs → ≈ $197) | 1.3 | 3.8 | 7.0 | 7.2 | 5.0 | 8.0 | 32.5 + 76 + 140 + 108 + 50 + 80 = **4.87** |

**Sensitivity (§5 step 3):** each weight × 0.7 and × 1.3 in turn, 12 cases (checked by script, sums × 100). B08 stays
first in all 12: it leads K09 by 1.9 in the base case and by ≥ 1.6 in every case. Among the transition-capable concepts
the team would build, **K09 stays first in all 12 cases**: its narrowest lead is over K19 with flight-risk weight × 1.3
(699 vs 538). K01 reaches 4.87 with the budget recovery, or 4.74 with the K21 hexa (flight 8.0, but the hexa spends the
recovered reserve again); it never passes K19 or K06 while its reserve stays under one crash. The order is robust; the
two things that are not weights (whether a bought PNP counts as student-built, and whether a non-transitioning quad
counts as VTOL) move the result more than any weight.

### 3.3 The corrected numbers the matrix rests on (one line each)

| | MTOW | Hover T/W (corrected) | Cruise after 2 min hover | Spend / reserve | Team-hours to first hover | Packed |
|---|---|---|---|---|---|---|
| K09 | 2.43 kg (card 2.38) | **2.6** | ≈ 19 min (pess. 12; card 27) | $1,632 / **$368** (card $1,529 / $471) | **70–85 h** + 30–40 h flight sessions | one piece, ≈ 1.25 × 0.55 × 0.45 m, 6 kg |
| K01 | 3.45 kg (card 3.22) | 1.83 / **1.70 sag** | 15–20 min (card 22) | $1,897 / **$103** (card $1,742 / $258) | 150–180 h | 1.2 × 0.5 × 0.4 m, 7 kg, 5 joints + 6 plugs |
| K19 | 3.30 kg (card 3.10) | 1.9 / **1.6 low V** | ≈ 10 min (pess. 5.7; card 17) | $1,810 / $190 | 120–140 h | 1.2 × 0.5 × 0.4 m, 6 kg |
| K06 | 2.63 kg (card 2.39) | 1.62 / **1.53 end of pack** | ≈ 9.4 min (card 17) | $1,705 / $295 | ≈ 180 h + 3–4 wk tilt tuning | 0.88 × 0.50 × 0.39 m |
| B08 | 0.72 kg | 2.0 (1.5 with growth) | ≈ 17 min (pess. 9; card 24) | $1,430 / $570 | 80–100 h, hovers week 1–2 | maker case 0.75 × 0.42 × 0.18 m |
| B09 | 2.30 kg (2.52 pess.) | 2.15 worst motor | 12 min (pess. 8; card 19) | $1,695 / $305 ($55 if Maker Passes are paid) | ≈ 125 h + ≈ 100 printer-h | 1.09 × 0.44 × 0.31–0.41 m |
| U01 | 2.70 kg | 2.2 | ≈ 20 min with wing (bare quad 15) | $1,626 / $374 | 70–85 h | 0.80 × 0.44 × 0.38 m |

---

## 4. Recommendation

### 4.1 Take K09 into detailed design: quad tailsitter, flat flying wing, four fixed motors, two elevons

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 250" width="800" height="250" font-family="sans-serif" font-size="11">
  <!-- scale 200 px = 1 m; props dashed; all three views same scale. Copied from cards/K09/CARD.md; elevons added by the study lead. -->
  <text x="10" y="16" font-weight="bold">K09 3-view, to scale (200 px = 1 m). Cruise attitude. Props dashed (11 in). Elevons (blue) added per the skeptic review.</text>
  <!-- FRONT VIEW (from nose) centre 160,130 -->
  <text x="110" y="40">FRONT (from nose)</text>
  <rect x="45" y="127" width="230" height="6" fill="#bbb" stroke="#000"/>
  <rect x="150" y="115" width="20" height="12" fill="#ddd" stroke="#000"/>
  <line x1="96" y1="92" x2="96" y2="168" stroke="#000" stroke-width="3"/>
  <line x1="224" y1="92" x2="224" y2="168" stroke="#000" stroke-width="3"/>
  <g fill="#555"><circle cx="96" cy="92" r="4"/><circle cx="224" cy="92" r="4"/><circle cx="96" cy="168" r="4"/><circle cx="224" cy="168" r="4"/></g>
  <g fill="none" stroke="#666" stroke-dasharray="3,3"><circle cx="96" cy="92" r="28"/><circle cx="224" cy="92" r="28"/><circle cx="96" cy="168" r="28"/><circle cx="224" cy="168" r="28"/></g>
  <line x1="45" y1="215" x2="275" y2="215" stroke="#000"/><text x="135" y="230">span 1.15 m</text>
  <line x1="96" y1="200" x2="224" y2="200" stroke="#000"/><text x="128" y="196">motors ±0.32 m</text>
  <line x1="285" y1="92" x2="285" y2="168" stroke="#000"/><text x="289" y="134">0.38 m</text>
  <!-- TOP VIEW centre 470; LE y=100, TE y=160 -->
  <text x="430" y="40">TOP (nose up)</text>
  <rect x="355" y="100" width="230" height="60" fill="#bbb" stroke="#000"/>
  <rect x="358" y="150" width="44" height="10" fill="#9bc" stroke="#000"/>
  <rect x="538" y="150" width="44" height="10" fill="#9bc" stroke="#000"/>
  <rect x="460" y="108" width="20" height="40" fill="#ddd" stroke="#000"/>
  <line x1="406" y1="80" x2="406" y2="160" stroke="#000" stroke-width="3"/>
  <line x1="534" y1="80" x2="534" y2="160" stroke="#000" stroke-width="3"/>
  <rect x="402" y="72" width="8" height="8" fill="#555"/><rect x="530" y="72" width="8" height="8" fill="#555"/>
  <line x1="378" y1="70" x2="434" y2="70" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="506" y1="70" x2="562" y2="70" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="595" y1="100" x2="595" y2="160" stroke="#000"/><text x="599" y="134">0.30 m</text>
  <text x="440" y="180">pod 0.20 × 0.10 m; elevons 0.22 × 0.05 m (added)</text>
  <!-- SIDE VIEW: nose left; tube x=650, LE x=670, TE x=730, wing y=130 -->
  <text x="660" y="40">SIDE (nose left)</text>
  <rect x="650" y="92" width="80" height="76" fill="#eee" stroke="#000"/>
  <path d="M670,130 Q685,123 705,126 Q722,129 730,129 Q715,133 690,133 Q675,133 670,130 Z" fill="#bbb" stroke="#000"/>
  <line x1="650" y1="92" x2="650" y2="168" stroke="#000" stroke-width="4"/>
  <rect x="642" y="88" width="8" height="8" fill="#555"/><rect x="642" y="164" width="8" height="8" fill="#555"/>
  <line x1="640" y1="64" x2="640" y2="120" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <line x1="640" y1="140" x2="640" y2="196" stroke="#666" stroke-dasharray="3,3" stroke-width="2"/>
  <g fill="#000"><circle cx="730" cy="92" r="3"/><circle cx="730" cy="168" r="3"/></g>
  <text x="736" y="95">foot</text><text x="736" y="171">foot</text>
  <line x1="650" y1="215" x2="730" y2="215" stroke="#000"/><text x="652" y="230">fin 0.40 m</text>
  <text x="655" y="245">hover: stands on 4 feet, nose up</text>
</svg>

**What it is.** A 1.15 × 0.30 m rectangular flying wing (hot-wired XPS, tape skin, one 22 mm carbon spar) with two
foam-board fins at ±0.32 m, each carrying a vertical carbon tube with a motor at each end: four motors in an X, two
above and two below the wing. It stands on the fin tips, takes off as a quadcopter, pitches 90° onto the same four
motors for cruise, and pitches back to land. ArduPilot Plane tailsitter mode, four class-S stations (SunnySky X3108S +
APC 11×4.5, 4S 6500 packs). Baseline mass 2.43 kg + 0.05 kg for elevons; hover T/W ≈ 2.55. The whole aircraft travels in
one piece: four props and a pack at the field, five minutes, one person, no tools.

**Why this one, against the team's own constraints:**
- **Budget.** $1,632 corrected (≈ $1,665 with elevons), leaving ≈ $335–368. That covers one bad crash ($309 incl. tax)
  with change; a crashed wing is re-cut from the same XPS sheet (six cores per sheet, ≈ $20). It is the only scratch
  concept whose reserve survives a crash. K01's does not ($103 vs $266).
- **Transport.** One piece, no structural joint, one electrical disconnect. The box is the largest in the study
  (≈ 1.25 × 0.55 × 0.45 m external, 6 kg, back seat or hatchback) but it is one box, one person, five minutes.
- **Student-built, in 12 weeks.** Fewest parts in the set (4 stations, 2 servos with elevons, 0 loaded mechanisms, 0
  field joints). 70–85 team-hours to first hover (≈ 3 weeks), the fastest scratch build, leaving 8–9 weeks for the
  transition campaign and a crash. All parts US stock except the carbon tubes (≈ 2 weeks, order first).
- **Mission.** T/W 2.6 is the best hover margin in the study; ≈ 19 min cruise (12 pessimistic) against a 5 min
  threshold; the 90° pitch-over is the most visible demonstration of "VTOL to forward flight" in the set.
- **Learning.** A novel configuration the team designs entirely; the old 29-layout trade study also ranked tailsitters
  first. The $40 foam-board twin gives a clean proposal → modelled → checked → verified chain and answers the one
  question that could kill it before any XPS is cut.

**The two changes from the card, adopted from the skeptic review (`cards/K09/REVIEW.md` §8):**
1. **Elevons as baseline** (+$30, +0.05 kg, 2 micro servos): fly `Q_TAILSIT_ENABLE 1` with `Q_TAILSIT_MOTMX` set for
   all four motors, so roll and pitch in cruise come from surfaces, not from motor torque alone. Motor-only mode
   (the card's baseline, `Q_TAILSIT_ENABLE 2`) becomes an experiment, not the plan. This is what moves the flight-risk
   judge from 3.5 to about 5.
2. **A 5 m/s wind limit on the flight card** and morning flights. Hover lean is 16° at 5 m/s and 36° at 8 m/s, and a
   fin landing tips over past 39°. This is a procedural limit the team must accept; it is the price of the concept.

**What it is bad at, plainly.** It is the riskiest of the seven to fly (flight-risk judge: 3.5/10 as carded, ≈ 5 with
elevons, 7th of 7). Any motor or ESC failure is fatal in both modes; the vertical landing on fin tips is the recurring
damage mode at a bay-shore site; tailsitter transition tuning (`Q_TAILSIT_*` angles, gain scheduling with airspeed) is
the least-documented path in the set for a first-time team, with two forum threads pointing opposite ways on
motor-only roll. The mitigation is that the aircraft is nearly a consumable and flies in week 3.

### 4.2 Runner-up: K01, small twin-boom quadplane 4+1

K01 is the mirror image: it is the concept two of the three judges prefer (mission-and-learning 8.0, first;
flight-risk 7.0, best of the scratch builds: tailed, best-documented ArduPilot transition, a lift-motor failure in cruise
is a glide), and the one the budget and build lenses rank last (reserve $103 after corrections, 150–180 team-hours,
the heaviest box, 5 joints and 6 plugs at every assembly). It becomes the choice only with four changes the skeptic
requires: add a full-span spar (+0.08 kg, +$20), move the lift centroid or enlarge the tail to get ≥ 8 % static margin
(as drawn it is 0–3 %), switch to the SpeedyBee F405 Wing and 4S 5000 packs, and recover reserve (drop the $44 RID
module because RFS is a FRIA; buy 2 packs, not 3; buy a spare boom). Even then the reserve is ≈ $200 against a $266
crash. K19 (flying-wing quadplane) scores higher than K01 on the matrix but is tailless, sits at T/W 1.6 at the end of
a pack, and has a $190 reserve below one crash; it is not a safer runner-up, only a cheaper K01.

**B08, the bought HEEWING T1-S, wins the arithmetic (8.68) and is set aside.** It passes every gate, costs $1,430, flies in
week 1–2, and a whole second airframe is affordable. The study lead sets it aside because "student-built" is one of the
team lead's four constraints and B08 designs nothing structural (mission-and-learning judge: 3.0, capstone content 2/10).
This is a team decision, not a physics one (§5.1 item 2). If the team lead accepts a PNP, B08 is the answer and this
document's recommendation is wrong.

### 4.3 What would flip the decision

| If… | Then |
|---|---|
| The $40 foam-board twin (2 days, before any order) cannot hold position within 1 m in a 5 m/s fan or breeze, or the team will not accept a 5 m/s flight-card limit | **K01** with the four fixes above |
| RFS morning wind records for March–April show > 5 m/s on most days (check before December; the mission judge asked for this) | **K01** |
| The team wants a hover motor-out to be survivable | **K01 + K21 hexa** (+$102, T/W 2.7): the only redundant layout under $2,000, and it needs ≈ $250 of reserve recovered first |
| A bought PNP counts as "student-built" for the capstone | **B08** outright; or B08 as a January mule plus a scratch K09 main aircraft (B06 plan), which leaves < $200 of reserve |
| "Transition" is redefined so partial wing-borne flight counts | U01 rises to ≈ 5 on mission fit; the study lead does not recommend this reading |
| Jacobs Maker Passes ($125 per student per semester, `UNVERIFIED`) are charged to this budget | K09 reserve falls to ≈ $85–210, still passes; K01, K19 and B09 fall below zero or one crash |
| The team prefers a visibly conventional aircraft and a tail over the budget margin | K01; the numbers say it costs ≈ $270 of reserve and 80–100 team-hours |

**Before the mid-December order (all cheap, all from the cards and judges):** build and fly the foam-board twin; design
the fin-tube joint and the box cradles (the card's "two layers of foam board sandwiching a 22 mm tube" is not flat);
confirm a *stable* ArduPilot Plane build with tailsitter support for the chosen board on firmware.ardupilot.org (five of
seven cards name a backordered or beta-target FC); open the Ovonic page for US stock and the pack's real mass (503–680 g
conflicting); buy one spare carbon tube; measure two team members' cars against a 1.25 × 0.55 × 0.45 m box; get Maker
Pass coverage and RFS wind records in writing.

---

## 5. What the team must decide, and what changes in D1–D15

### 5.1 Decisions for the team lead

1. **Mission numbers.** Confirm the demonstrator as hover ≥ 2 min total, cruise ≥ 5 min, 20 % reserve, no payload, inside
   one RFS sub-field. Drop the 10 min "objective": every concept clears it or nearly, and it was a previous agent's
   number. Say whether growth to a mapping (camera) or delivery mission matters at all; it does not for K09's choice.
2. **Does a bought PNP satisfy "student-built"?** No → K09 (this document). Yes → B08, and most of this study is moot.
3. **Accept the K09 operating limits:** 5 m/s wind on the flight card, morning flights, elevons as baseline, any single
   motor failure fatal. If not → K01.
4. **Requirement changes under K09:** drop "no moving surfaces" (elevons in); the transport box grows to
   ≈ 1.25 × 0.55 × 0.45 m (C3a's 1.2 m was a proposal; measure the cars); the mass gate becomes 2.6 kg (sized 2.48 kg
   + 5 %); stall ≤ 12 m/s applies (the emergency mode is a hover landing, but transition is at ≥ 1.3 Vs = 14.6 m/s).
5. **Who flies.** D15 stands: ≥ 10 h SITL and a cheap quad or sim before first hover; the foam-board twin is the trainer.
6. **Three one-email questions** that move money: Maker Pass coverage; whether the course treats flights as recreational/
   educational (no $175 Part 107 exam); whether Jacobs lasers foam board (knife-cut fallback costs nothing).

### 5.2 Previous decisions D1–D15 (`inputs/DECISIONS-ADOPTED.md`) under K09

| # | Was | Under K09 |
|---|---|---|
| D1 Baseline: 2.4 m, NACA 2415, 7.438 kg, 4 lift + 1 pusher | **Void.** New baseline: 1.15 m span, MH 45-type reflexed section, 2.48 kg sized, 4 fixed motors, no pusher (`cards/K09`). |
| D2 Cruise 18 m/s, stall 11.75 m/s | **Void.** Cruise ≈ 15 m/s, stall ≈ 11.2 m/s corrected, transition ≥ 14.6 m/s. |
| D3 Hard as-built limit 7.75 kg, mass tracked per subsystem | **Principle carries over; number void.** Gate = sized mass + 5 % ≈ **2.6 kg**. Per-subsystem tracking stays (advisor lesson 7). |
| D4 No payload; CG 28 % MAC; ≤ 100 g trim | **Carries over in kind.** No payload; CG set by the reflexed wing's static margin (to be fixed in detailed design), not by the lift centroid; trim ballast only inside the 2.6 kg gate. |
| D5 AS150U disconnect, XT90-S removed, 8 AWG pack wire | **Principle carries over (D9 ≥ 1.25 × peak); sizes void.** Hover 24 A, all-motors-full ≈ 120 A momentary; re-size the wire for a 24 A hover with ≤ 10 °C rise `ESTIMATE`; the skeptic notes XT60 (60 A) would also pass and avoids re-terminating four packs. Decide in detailed design. |
| D6 LANRC BLHeli_S 45 A lift ESCs | **Carries over** (same ESC family in the K09 BOM, 4 + 4 spare); confirm the 30 A full-throttle per motor against the 45 A rating and reflash to Bluejay if bidirectional DShot is wanted. |
| D7 Airspeed MS4525DO + pitot | **Changes to optional** (card: $59.99). With elevons and `Q_TAILSIT_ENABLE 1`, an airspeed sensor is recommended for gain scheduling; decide at the first transition tests. |
| D8 GPS RMRC SAM-M10Q-5883 | **Carries over** (K09 BOM lists the HGLRC M100-5883 at $20.49; either works). |
| D9 Spare motor not bought now | **Void.** The K09 BOM already holds 1 spare motor, 4 spare ESCs and 8 spare props. |
| D10 `C0_BOM.csv` is the single BOM; reserve ≥ $100 | **Changes.** `cards/K09/cost.csv` plus the skeptic's added lines (18650 cells, connector re-termination, real box, hot-wire jig, FAA $5, elevon servos) becomes the single BOM; planned reserve ≥ $150, currently ≈ $335. |
| D11 No mission above 25 °C; morning flights; hover ≤ 30 s before transition; vents | **Numbers void, habits carry over.** Morning flights stay, now for wind (5 m/s limit). The 25 °C ceiling was C0's; re-derive the thermal ceiling for 4 × X3108S at 24 A in the open (D13). The 30 s hover cap is gone (T/W 2.6, 13 min hover-only). |
| D12 Prop spec: 18.2 N hover / 29.2 N peak per rotor; 6 lift + 2 pusher props | **Void.** 4 × APC 11×4.5MR, ≈ 6 N hover per motor, 15.5 N max on the maker table; 12 props bought; no pusher. |
| D13 All CAD in Autodesk Fusion, generated from `params.json` | **Stands** (team lead override). |
| D14 Tilt-wing archived | **Stands**; K12 was dropped again at screening. |
| D15 GitHub Pages canonical, old repos archived | **Stands.** |
| Cross-cutting: 7.75 kg gate, 6061 joiner reserve factor 1.41, stale docs | 7.75 kg and the joiner are void (no joiner; one 22 × 20 mm CF spar, bearing and bending check to be done); "write fresh docs, do not patch old ones" stands. |

---

## 6. Disagreements, stated plainly

1. **The three judges rank K09 three different ways.** Build-and-transport: 8.5 (3rd, best scratch build). Mission-and-
   learning: 7.0 (2nd). Flight-risk: 3.5 (7th, last). The same aircraft is the cheapest and simplest to build and the
   riskiest to fly. This document resolves it with the team lead's own weights (budget 25, build 20, schedule 15 outweigh
   flight 20) and the elevon change, not by pretending the risk is small.
2. **The judges invert on K01 too.** Mission-and-learning puts it first (8.0); build-and-transport puts it last (4.0)
   because a $103 reserve cannot absorb a crash. The flight-risk judge's 7.0 holds only if the spar and static-margin
   fixes are made ("else −1.5").
3. **U01: safest to fly, fails the mission.** Flight-risk judge 8.0 (first); skeptic and mission judge: no transition,
   fails as specified. The study lead sides with the skeptic. The card itself listed this as its own risk 1.
4. **B08: the numbers say buy it; the capstone says no.** Build 9.5, flight 7.5, mission-and-learning 3.0. Nobody disputes
   the numbers; the dispute is what the project is for. Decision 5.1 item 2.
5. **Every card was optimistic, and the skeptics all pushed the same way.** K01 reserve $258 → $103; K09 cruise 27 → 19 min;
   U01 wing saving 52 % → ≈ 20 % (one AIAA flight test, Su et al. 2023); B08 hover power +40 % (wrong prop size, wrong
   airframe variant); K06 T/W 1.79 → 1.53 at end of pack. No card's conclusion was reversed, but no card's margin
   survived intact. Treat the advisor's XV-24 mass history (3 → 6 → 10.8 kg) as the warning it is.
6. **K09 motor-only vs elevons.** The card chose motor-only (zero servos); the skeptic rates motor-only roll in cruise
   4/5 risk and recommends elevons; the flight-risk judge agrees; the mission judge says elevons should be baseline.
   This document adopts elevons. The K09 card's author would say this gives up the "zero servos, fastest repair" point;
   the study lead judges two micro servos a small price.
7. **K06 is scored two ways.** The mission judge scores it assuming the K07 fourth motor is bought (+$78); the flight-risk
   judge scores it as drawn (T/W 1.53). Both agree K06 as drawn is not a safe demonstrator.
8. **Screening vs cards on B08's price.** Screening: $950–1,100; card with the full ground floor: $1,389; skeptic: $1,430.
   The screening number omitted the shared floor every concept pays.
9. **Wind at RFS is the unknown nobody measured.** The flight-risk judge calls K09 and B08 "morning-only aircraft"; the
   K09 skeptic accepts the lean-angle method but notes T/W 2.6 allows ≈ 66° of lean if the limit is raised, so the real
   limit is the fin-tip landing. The mission judge says K09 drops to ≈ 6 if wind is routinely > 5 m/s. One afternoon with
   the RFS weather records settles who is right.
10. **The research folders were empty.** `research/existing-vtol/` and `research/flight-control/` never landed, so every
    "documented build" claim is a forum citation read by the concept, audit or card agent. A logged transition (not a
    video) for a motor-only or elevon quad tailsitter on ArduPilot is still `UNVERIFIED`; the foam-board twin is the
    team's own evidence.

See `REQUIREMENTS-PROPOSED.md` in this folder for the requirement set the 18-agent detailed design should use.
