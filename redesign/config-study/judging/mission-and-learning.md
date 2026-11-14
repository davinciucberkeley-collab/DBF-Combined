# Judge: mission fit and value to the capstone

Status: PROPOSED (judge, lens "mission and learning", 2026-11-09). One lens only. Budget, buildability, flight risk,
schedule and transport are other judges' business; they appear here only where they change what the aircraft can
*demonstrate* or *grow into*. Numbers are the **skeptic-corrected** values from each `cards/*/REVIEW.md` unless marked
"card". `ESTIMATE` = my judgement, `UNVERIFIED` = taken from a card/review claim not checked by me.

## What this lens scores

The team lead fixed the mission on 2026-11-09: **VTOL demonstrator** (vertical take-off, transition to forward flight,
short cruise, transition back, vertical landing; no payload). `REQUIREMENTS.md` §3 M-A quantifies it (hover 2 min,
cruise 5 min threshold / 10 min objective, 20 % reserve, 0.25 kg growth allowance) and names the two growth missions
M-B (mapping: 20–30 min cruise + camera) and M-C (delivery: 0.5 kg, 4 min hover, precision landing). The advisor's
XV-24 lessons say what the capstone is meant to show: a complete aircraft from one inventory, joint stacks, wiring as
an installation, mass discipline, proportionate verification. The mentor adds buildability before simulation and
converging on fewer artifacts.

So four sub-questions, weighted inside this lens (`ESTIMATE` weights, mine):

| # | Sub-question | Weight | 0 looks like | 10 looks like |
|---|---|---|---|---|
| A | **Default mission, as corrected.** Does it do a real transition both ways, meet the 10 min objective, and have hover/thrust margin to fly the demo on an ordinary RFS morning? | 40 | No transition, or threshold only with no margin | Objective met with margin, transition documented for the layout, hover T/W ≥ 2.0 corrected |
| B | **Room to grow** into M-B or M-C on the same airframe (thrust, energy, volume, wind tolerance). | 20 | Cannot take the 0.25 kg growth allowance | M-B or M-C reachable with a pack/camera/latch and a parameter change |
| C | **Engineering content the team can show.** How much of the aircraft the team designs, how many distinct disciplines it exercises (aero, structure, mechanism, propulsion, controls), and whether the results are measurable. | 25 | Bought airframe, nothing to design, test campaign only | Team designs the whole airframe; several non-trivial analyses with bench/flight evidence |
| D | **Fit with the AI-assisted design process** the advisor cares about: a parts inventory that drives BOM, renders, build manual and viewer; joint-stack tables; wiring across removable joints; a mass budget to discipline; checks a student can rerun. | 15 | Nothing for the pipeline to drive (PNP) | Scratch build with many interfaces, reusing the repo's existing scripts and mass/CG tooling |

A concept with no transition scores near zero on A regardless of its other merits, because the team lead's one
sentence about the mission is the only mission statement we have.

## Scores

| Rank | ID | Concept | A (40) | B (20) | C (25) | D (15) | **Score 0–10** | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | **K01** | Twin-boom quadplane 4+1 | 8 | 7 | 9 | 9 | **8.0** | Medium-high: most cells rest on reproducible sizing plus the previous repo's work |
| 2 | **K09** | Quad tailsitter, motor-only | 6 | 7 | 8 | 7 | **7.0** | Medium: hover-in-wind and roll authority are `ESTIMATE` until the foam-board twin flies |
| 3 | **K06** | Scratch tilt-tricopter | 6 | 4 | 9 | 8 | **6.5** | Medium: T/W sits at the gate; K07 variant assumed for growth |
| 4 | **K19** | Flying-wing quadplane | 6 | 4 | 7 | 8 | **6.0** | Medium: tailless trim at transition is the open question |
| 5 | **B09** | Printed Flightory Stallion | 6 | 5 | 3 | 2 | **4.5** | Medium-low: no owner data for the VTOL variant; licence `UNVERIFIED` |
| 6 | **B08** | Bought HEEWING T1-S PNP | 5 | 1 | 2 | 1 | **3.0** | Medium: product exists; wind limit and transition-abort reports are forum claims |
| 7 | **U01** | Wing-assisted quad | 1 | 5 | 4 | 2 | **2.5** | High on the verdict (no transition), low on the wing's payoff (coin flip per Su et al.) |

Score = Σ(sub-score × weight) / 100, rounded to the nearest 0.5. Worked:
K01 = (8·40 + 7·20 + 9·25 + 9·15)/100 = 8.00 → 8.0;
K09 = (6·40 + 7·20 + 8·25 + 7·15)/100 = 6.85 → 7.0;
K06 = (6·40 + 4·20 + 9·25 + 8·15)/100 = 6.65 → 6.5;
K19 = (6·40 + 4·20 + 7·25 + 8·15)/100 = 6.15 → 6.0;
B09 = (6·40 + 5·20 + 3·25 + 2·15)/100 = 4.45 → 4.5;
B08 = (5·40 + 1·20 + 2·25 + 1·15)/100 = 2.85 → 3.0;
U01 = (1·40 + 5·20 + 4·25 + 2·15)/100 = 2.70 → 2.5.
No score is overridden by hand; every disagreement with the arithmetic would have to be argued in the sub-scores.

## Reasons, one block per concept (corrected numbers)

### K01 — twin-boom quadplane 4+1 — 8.0
- **A = 8.** True speed-scheduled transition on the best-documented ArduPilot VTOL path (≥ 5 builds). Corrected
  cruise 15–20 min after 2 min hover (objective met three times over), hover-only ≈ 7 min. Corrected hover T/W 1.70
  with sag: passes the gate, no gust margin, so the demo needs the 4S 5000 pack (T/W 1.77) or K21 hexa. Cruise-propulsion
  failure leaves a glide (the only shortlisted layout where cruise motor-out is survivable). The reviewer's two findings
  that bear on the mission (no spar; static margin 0–3 % MAC, so FBWA cruise may be pitch-divergent) are fixable before
  the order freeze and cost about +0.1 kg and $20.
- **B = 7.** The reviewer's own words: "the 6500 pack is oversized" and "even the worst case meets the mission". That
  surplus energy *is* M-B growth: a 0.15–0.25 kg camera fits the growth allowance and 16–20 min cruise is near M-B's 20
  min threshold on a 0.40 m² wing, the largest and highest-AR in the set. M-C needs the K21 hexa (+$102, T/W 2.74 card)
  because a 0.5 kg box drops the quad's T/W to ≈ 1.5 `ESTIMATE`; the reserve after corrections ($103) does not cover it
  today. U07 split-chemistry pack is a documented path to longer cruise.
- **C = 9.** The team designs everything: wing, tail volumes, boom-to-spar joints, pod, pusher sizing (thrust stand),
  stability (XFLR5/AVL check demanded by the review), parked-prop drag measurement, connector rating (93 A need vs
  AS150U 70 A). The skeptic's spar-stress and neutral-point calculations are exactly the kind of engineering a
  capstone report should show being found and fixed.
- **D = 9.** Five mechanical field joints and six plugs give the joint-stack table and wiring-as-installation real
  content. The previous repo's Fusion scripts, `MASS-CG.md`, thermal and electrical studies were built for a lift +
  cruise layout and transfer directly, which is the mentor's "v2 rather than new artifacts". The most parts of any
  shortlisted concept, so the inventory → BOM → build manual → viewer chain has the most to drive.
- **What would lower it:** if the team wants a visibly unconventional aircraft, this is the least novel layout.

### K09 — quad tailsitter, flat flying wing, motor-only — 7.0
- **A = 6.** A pitch-over transition is the most visible demonstration of "VTOL to forward flight" in the set, and the
  energy and thrust margins are the best: corrected cruise ≈ 19 min (pessimistic 12), hover-only 13 min, T/W 2.6. Two
  things cut the score. Hover lean of 36° at an 8 m/s gust and a fin-landing tip-over at 39° mean the *vertical landing*
  leg of the mission is only safe below 5 m/s at a bay-shore site: the demo is weather-limited in a way K01 is not.
  Motor-only roll in cruise is rated 4/5 by the reviewer with a PX4 builder calling it "unfeasible in most cases"
  (forum, `UNVERIFIED`); the +$30 elevon fix drops that to 3/5 and should be baseline.
- **B = 7.** Thrust headroom is the best for M-C's 4 min hover (13 min available), but REQUIREMENTS §3 itself notes
  tailsitters are poor at precision hover in wind, and a 2 × 2 m pad landing on fins is exactly that. M-B is reachable
  in energy (19 min) but at L/D 6 the mapping story is weak. Good on the numbers, poor on the operations.
- **C = 8.** A novel configuration with zero servos, a controls problem (gain scheduling with airspeed, motor-only
  roll) and a cheap foam-board twin that answers the wind question before the XPS wing is cut. The old trade study
  ranked it first. Fewer disciplines than K01 (no tail, no mechanism, one structural joint), so 8 not 9.
- **D = 7.** One piece, no field joints, one electrical disconnect: little for the joint-stack and wiring method to
  show. In its favour: the simplest aircraft is the one most likely to be *complete* early, which is the advisor's
  main lesson, and the foam-board → XPS sequence is a clean "proposal → modelled → checked → verified" chain.

### K06 — scratch tilt-tricopter — 6.5
- **A = 6.** The tilt transition keeps every motor working in cruise, so the demo has nothing parked and nothing
  gliding: it reads as a tiltrotor should. Against it: corrected cruise 9.4 min (just under the objective), hover-only
  6.3 min, and hover T/W 1.62 with sag falling to ≈ 1.53 at end of pack, under the gate. Rear motor carries the most
  load with only 1.4–1.6 headroom `ESTIMATE`. The card and review both say K07 (+$78, fourth rear motor, T/W ≈ 2.0)
  is the coherent variant; I score A assuming K07 is taken. Transition tuning is 3–4 of the 12 weeks, so the
  back-transition leg is the schedule risk to the mission itself.
- **B = 4.** At the gate there is no payload margin; the 0.28 kg "headroom" on the card is consumed by the
  corrections. M-B needs more pack, which lowers T/W further. Only K07 restores any growth, and even then M-C's 0.5 kg
  is out of reach `ESTIMATE`.
- **C = 9.** The richest mechanism content: nacelle pivot on bearings, servo link, 200-cycle bench rig, vectored-yaw
  trim (the reviewer's 1.5° differential-tilt calculation), tailless CG window, plus the usual foam wing and pod. More
  disciplines than K01, but the mission margin is thinner.
- **D = 8.** Wiring across a *moving* joint (slack, strain relief, chafe: advisor item 3) and a loaded mechanism with
  a real joint-stack table. Fewer parts than K01 but each interface is more interesting.

### K19 — flying-wing quadplane — 6.0
- **A = 6.** Same transition mode as K01, documented on X8s and the DeltaQuad. Corrected cruise ≈ 9.6 min (objective
  missed by a hair; pessimistic 5.7 min is at the threshold), hover-only 7 min, T/W 1.9 fresh / 1.6 at low voltage.
  The mission-specific problem is that the elevons are the only pitch control once the lift motors fade and the CG
  window is ≈ ±13 mm: a wrong CG shows up at transition, the one event the demo exists to show. The reviewer also
  pushes cruise to ≥ 17 m/s (trimmed CLmax 0.65), so the demo flies faster and closer to the pack's limit.
- **B = 4.** Energy is fully used at the objective; a second pack (+0.56 kg) puts T/W under the gate. The joiner
  socket crushes at 4 g before any payload is added. No realistic path to M-B or M-C without a bigger wing.
- **C = 7.** Flying-wing aerodynamics (reflex, static margin, trimmed CLmax), joiner-sleeve bearing design, hot-wire
  cores. Two fewer servos and no tail than K01 means a little less to design.
- **D = 8.** Scratch build with five field joints and two servo leads across joints; the same repo tooling as K01
  applies.

### B09 — printed Flightory Stallion VTOL — 4.5
- **A = 6.** On the numbers it flies the mission well: worst-motor T/W 2.15, 12° gust tilt, cruise 12 min corrected
  (pessimistic 8.1), hover-only 4.8 min (thin; early test cards will spend more than 2 min hovering). No published PIDs
  and a single rear motor as the most-loaded single point of failure. One point off a 7 because the whole airframe
  process is conditional: LW-PLA stiffness and heat (HDT 50–54 °C), Jacobs accepting bring-your-own filament, and the
  personal-use licence are all week-1 checks, and if any fails the card's own fallback is K06.
- **B = 5.** Flightory's AUW band runs to 3.0 kg, so ≈ 0.5 kg of thrust-side headroom exists, but hover endurance and
  the fixed printed battery bay limit M-B and M-C alike.
- **C = 3.** "Design hours are near zero, and that is the point of this concept" (card). What remains is real but
  thin: the 1300 → 1700 KV substitution analysis, a wing load test, LW-PLA material characterisation, tuning from
  scratch. The airframe was designed by someone else and the licence is personal-use only.
- **D = 2.** The pipeline would be driving someone else's STL files, which the licence may not even allow the team to
  modify or republish. Nothing of the inventory → viewer story is the team's.

### B08 — bought HEEWING T1-S PNP — 3.0
- **A = 5.** A product that transitions, on an official ArduPilot board. But: corrected hover T/W 2.0 falls to 1.5
  with the growth allowance (fails the gate), a 0.72 kg aircraft sees gust lift of 20 % of its weight at 8 m/s, the
  12.6 m/s transition is only 1.6× the design gust, and the community thread reports factory transitions aborting at
  3 s and later QLOITER failures with no resolution (forum, `UNVERIFIED`). The demo is possible on calm mornings and is
  the only concept that could fly in January.
- **B = 1.** At the listed maximum weight already; no payload, no second pack, no growth.
- **C = 2.** The card's own risk 2: "the team gets an aircraft but designs almost nothing." ArduPilot setup, failsafes
  and a measured modification are good test-campaign content, not design content.
- **D = 1.** Nothing for the inventory, joint-stack or wiring method to work on. The B06 two-aircraft plan would fix
  this, but after corrections the $570 reserve is roughly one class-S scratch airframe with no crash money left.

### U01 — wing-assisted quad on a bought frame — 2.5
- **A = 1.** No transition. The reviewer's corrected run has the rotors carrying ≥ 75 % of weight at all speeds;
  the wing's lift even changes sign (−19 % W at 6 m/s). It is a quadcopter with a wing on it, and REQUIREMENTS §3
  says a multirotor does not demonstrate transition. The card admits this as its own risk 1; the reviewer says
  "fails the stated mission unless transition is redefined." I agree. The one point is for a safe vertical take-off
  and landing.
- **B = 5.** Oddly a good M-C candidate on the numbers: a T/W 2.2 quad with 12 min of hover will carry a 0.5 kg box
  and precision-land well, and 20 min of corrected cruise with the wing meets M-B's threshold. But M-B and M-C are both
  written as transition missions ("transition, cruise to a pad"), so growth from a non-transitioning aircraft is
  growth in the wrong direction; 5 rather than the 7 the raw numbers would give.
- **C = 4.** One real experiment (does an add-on wing pay? Su et al. 2023 measured ≈ 19 %) with a clean A/B flight
  test. One designed part. Its genuine value is as the D15 trainer and the hover test bed for class-S stations, and
  about 70 % of its BOM transfers to any winner.
- **D = 2.** A bought frame and a foam wing give the design pipeline almost nothing.

## What the ranking is sensitive to (for the ranking agent)

| If the team decides… | Then |
|---|---|
| "Transition" can mean tilt-body partial wing-borne flight | U01 rises to ≈ 5 (A becomes 5); nothing else moves. I do not recommend this reading; it changes the mission to fit the aircraft. |
| The capstone is graded on the flight-test campaign and AI-assisted *analysis*, not on airframe design | C and D weights halve (40/20/12.5/7.5, renormalised): B09 ≈ 5, B08 ≈ 3, K01 ≈ 8, K09 ≈ 7. The order does not change; the gap between scratch and bought concepts narrows. |
| Wind at RFS is routinely > 5 m/s during the test window | K09 drops to ≈ 6 (A → 4) and B08 to ≈ 2.5; K01 and K06 are unaffected. The team should look at RFS morning wind records before December. |
| K07 is *not* taken on K06 | K06 drops to ≈ 5.5 (A → 4, B → 2): a tilt-tri at T/W 1.53 end-of-pack is not a safe demonstrator. |
| Elevons are added to K09 (+$30) | K09 A rises to 7 → score ≈ 7.5; it would then tie or pass K06 on every lens I can see, not just this one. |
| M-B (mapping) becomes the mission | K01 extends its lead (largest wing, most spare energy); K09 and K06 fall on L/D and payload margin. |
| M-C (delivery) becomes the mission | K01 + K21 hexa or a bare quad lead; every tailsitter and tilt-tri falls on precision hover in wind. |

In every case except the first two, K01 stays first on this lens. Its weakness is not mission or learning; it is the
$103 corrected reserve, which is another judge's lens, and the two must be read together.

## Confidence and what is still `ESTIMATE`

- All endurance numbers are reviewer re-runs of card scripts with changed inputs, nothing flown. Cruise figures are
  the least certain (parked-prop drag, prop efficiency at low loading); hover T/W figures the most certain (maker tables).
- Sub-score C and D are judgement, not measurement. I scored them by counting designed parts, field interfaces and
  distinct analyses in each card, and by reading the advisor's list of what the XV-24 run was supposed to produce.
- The weights inside this lens (40/20/25/15) are mine. Swapping C and D weights, or raising B to 30, does not change
  the order of the top four or the bottom three; it only moves K09 and K06 relative to each other by about 0.3.

Files read: `STUDY-BRIEF.md`, `inputs/ADVISOR-XV24-LESSONS.md`, `inputs/MENTOR-GUIDANCE-2026-11-04.md`,
`requirements/REQUIREMENTS.md`, `screening/SCREENING.md`, and `cards/{K01,K19,K06,K09,B08,B09,U01}/{CARD,REVIEW}.md`.
