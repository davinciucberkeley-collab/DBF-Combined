# Tie-break decision: K09 quad tailsitter (lean, with elevons and airspeed)

Status: DECIDED (deciding judge, 2026-11-09), for the team lead's sign-off before the mid-December order.
Inputs: `../README.md`, `../cards/{K01,K09,K19}/{CARD,REVIEW}.md`, `../judging/*.md`, `wind/WIND.md`,
`k01-lean/CARD.md` + `cost.csv`, `tailsitter-evidence/EVIDENCE.md`. Every dollar figure below is reproduced in §9 so
it can be checked line by line. Tags as in the study: `ESTIMATE`, `UNVERIFIED`.

**Decision in four lines.** Build **K09-L**: the README's K09 quad tailsitter with two elevons, plus an airspeed
sensor, minus the Remote ID module, with two flight packs instead of four. It is the only candidate whose reserve
covers the study's $309 crash on pessimistic numbers ($321 left of $2,000). Lean K01 is the better flying bet by
about 0.1 in probability, and it lost at the budget gate, not in the air: $201 of reserve against a $309 crash.
K19 fails the same gate by $76 and would not have won the flying contest either.

---

## 1. The rule applied

The team lead's constraints, in the order they bind:

| Step | Test | Numbers used |
|---|---|---|
| **Gate 1: budget** | Spend at order time ≤ $2,000 **and** reserve ≥ one realistic crash, on **pessimistic** numbers | Crash = the study's class-S formula, **$309 incl. tax** (`cards/K09/cost.csv` line 35, `cost_model.py`). Spend = skeptic-corrected total, same levers for every candidate (§2), plus the same adverse adders. |
| **Gate 2: schedule and transport** | Student-buildable at Jacobs Hall in ≤ ~12 weeks **including one crash repair**; one box in a normal car | Build judge's rate 35 team-hours/week; RFS request lead ≥ 7 business days, so every repair-refly loop costs ≥ 1.5 weeks of calendar; pessimistic hours = each card's skeptic value, ×1.3 where no independent skeptic existed. |
| **Step 3: pick** | Among gate passers, the highest probability of a **logged full transition round trip (vertical take-off, transition, cruise, back-transition, vertical landing) by end of April** at the test site's real wind | `EVIDENCE.md` §3 model (hover week × weekly transition hazard × crash and wind discounts), re-run for lean K01's hours; wind from `WIND.md` (RCMC1 and KOAK, 2022–2025). Tie-breakers only if P ties: build effort, then capstone design content. **Budget margin beyond gate 1 earns nothing.** |

Excluded before judging, per the team lead's rule: **B08** (bought PNP: the team designs and builds nothing),
**U01** (no transition).

## 2. The same pessimistic basis for all three

So that no candidate is punished for being costed more honestly than another, every BOM was put on one footing:

1. **Start** from the skeptic-corrected total (K09 $1,632; K19 $1,810) or the card's own corrected baseline where the
   corrections were built in (K01-lean $1,719).
2. **Same levers for all:** no Remote ID module (RFS is a FRIA; K01-lean already had it out), **two** flight packs
   (K01-lean already had two; K09 had four, K19 three), airspeed sensor fitted (K01-lean and K19 already had one; added
   to K09 because `EVIDENCE.md` §3 conditions K09's probability on it and ArduPilot's tailsitter guide recommends it).
   K09 also takes its own BOM's note: 1 kg of PETG, non-structural prints in Jacobs' free PLA.
3. **Same adverse adders, all at once:** pack bought at list price, not the sale price seen on 2026-11-09; shipping +$30;
   Berkeley sales-tax measure +$7; jig and box growth +$20. These are the K01-lean card's own S8–S11 applied to everyone.
   The stacked case assumes four independent bad outcomes together; the baseline column assumes none.

## 3. Gate table (pessimistic column decides)

| | **K09-L** (tailsitter + elevons + airspeed, 2 packs) | **K01-lean** (twin-boom quadplane 4+1, re-sized) | **K19** (flying-wing quadplane 4+1, 2 packs, no RID) |
|---|---|---|---|
| Spend, baseline / **pessimistic** | $1,577 / **$1,679** | $1,719 / **$1,797** (card: ≈ $1,799) | $1,700 / **$1,767** |
| Reserve, baseline / **pessimistic** | $423 / **$321** | $281 / **$201** | $300 / **$233** |
| Reserve ≥ $309 crash (study formula)? | **PASS** (+$12 pessimistic, +$114 baseline) | **FAIL** (−$108 pessimistic; −$28 even at baseline; −$23 against its own $224 crash bill at pessimistic) | **FAIL** (−$76 pessimistic; −$9 even at baseline) |
| What it would take to pass | Nothing further. First lever if an adder lands: defer the airspeed sensor to a reserve purchase (+$66 → $388) | Jacobs tool loan in writing (+$105, `UNVERIFIED`) **and** SpeedyBee in stock at $48 with a stable build (+$19) **and** an independent skeptic finding < $18 of new cost → $327 | Two more `UNVERIFIED` recoveries plus Maker Pass coverage; no identified path to $309 |
| **Gate 1** | **PASS** | **FAIL** | **FAIL** |
| Team-hours to first hover, skeptic / pessimistic | 70–85 h / **≈ 115 h** (×1.3, plus elevons and airspeed) → hover week 3–4 | 100–130 h / **130–150 h** (self-reviewed only) → week 4–5 | 120–140 h / **≈ 160 h** → week 5 |
| Flight-test hours to a clean transition | 30–40 h | 25–35 h | ≈ 30 h `ESTIMATE` |
| One crash: money / time | $20 XPS core + prints + feet; **2–4 days** + RFS loop | Boom, saddle or tail; **1–2 weeks** + RFS loop | Boom hard-point tear-out = **15 h centre-section rebuild**; tubes overseas |
| Fits 12 weeks with one crash? | **Yes**: 8 weeks left after hover | Yes: 7 weeks left | Yes, thin: 6–7 weeks left |
| Packed, field assembly | One piece, box ≈ 1.25 × 0.55 × 0.45 m, 6 kg, 0 joints, 1 plug, 5 min, 1 person; back seat or hatchback, compact-sedan trunk marginal | 4 pieces, box 1.25 × 0.52 × 0.37 m, 5 kg, 3 joints + 5 plugs, 7 min | 5 pieces, box 1.2 × 0.5 × 0.4 m, 6 kg, 5 joints, 8–10 min |
| **Gate 2** | **PASS** | PASS | PASS (marginal) |

Only K09-L reaches step 3. The rest of this document still scores the other two on step 3, because the team lead
should see what the gate cost him and what would change it.

## 4. Step 3, scored for all three so the trade is visible

| | K09-L | K01-lean | K19 |
|---|---|---|---|
| In-class documented precedent on stock ArduPilot (`EVIDENCE.md`) | **None found** with elevons at 1–1.5 m / 2–3 kg; one logged auto-mission transition of unknown size; three "dive after handoff" reports; instructor-with-students case: no clean round trip in a month | Most mature ArduPilot VTOL path; expert transitioned 8 days after first hover; first-timer failures are setup errors caught on the ground | X8 / DeltaQuad lineage; tailless: CG window ±13 mm, elevon-only pitch once lift fades |
| Hover in the real wind | Lean 16° at 5 m/s, 36° at 8 m/s; fin-tip landing tips at 39°; **flight card 5 m/s mean / 8 m/s gust, mornings** | 6° / 16° broadside at 5 / 8 m/s; tailed, weathervanes; 8 / 12 m/s limit | Weak torque yaw; 5 m/s card advised by its own card |
| Usable mornings per week, Mar–Apr (`WIND.md`, 07–10 h, criterion B) | **5.0 (KOAK) to 5.7 (RCMC1)**; worst year 4.6–5.0; afternoons mostly out (27 % at KOAK) | **6.4 to 6.8**; afternoons mostly in | as K09 (5 m/s card) |
| Chance a morning booked 7 days ahead is flyable | ≈ 72–81 % | ≈ 91–96 % | ≈ 72–81 % |
| Hover T/W at low voltage | **≈ 2.4** | 2.02 (pess.) | **1.6** (at the gate when landing) |
| Motor-out in cruise | fatal | glide | glide |
| **P(logged full round trip by week 8)** | 0.40 (0.25–0.55); **≈ 0.50** with the three conditions in §5.3 | **0.55–0.60** `ESTIMATE` (evidence model re-run at 130–150 h) | ≈ 0.40 `ESTIMATE` |
| **P by week 12 (end of April)** | **0.50–0.60**; ≈ 0.60–0.65 with the conditions | **0.65–0.70** | 0.50–0.60 `ESTIMATE` |
| Tie-breaker 1: build effort | **best** (115 h, 4 stations, 2 servos, 0 joints) | 130–150 h, 5 stations, 3 servos, 3 joints | 160 h, 5 stations, 2 servos, 5 joints |
| Tie-breaker 2: capstone design content (mission judge C / D) | 8 / 7 | **9 / 9** | 7 / 8 |

Read plainly: **if lean K01 had passed gate 1 it would have won step 3** by roughly 0.1 in probability, with
overlapping bands (every P here is `ESTIMATE`). The head start that made K09 competitive against the heavy K01 in
`EVIDENCE.md` (hover three weeks earlier) is mostly gone against the lean K01, which hovers only a week later.
What remains in K09's favour is cheaper and faster crashes, hover margin, and 30–40 fewer build hours. What remains
against it is the thing no file in this study could verify: a logged elevon quad-tailsitter round trip in this class.

The gate is the team lead's rule, and it is the right rule for a one-airframe program: an aircraft whose reserve
covers a crash only if two unverified favours come through is not a $2,000 aircraft.

## 5. The choice: K09-L, defined

### 5.1 Configuration (changes from `README.md` §4.1 in bold)

Rectangular 1.15 × 0.30 m flying wing, hot-wired XPS, tape skin, one 22 × 20 mm CF spar; two foam-board fins at
±0.32 m carrying vertical CF tubes with a SunnySky X3108S + APC 11×4.5MR at each end (four motors in an X); stands on
the fin tips. ArduPilot Plane, `Q_TAILSIT_ENABLE 1`, `Q_TAILSIT_MOTMX` all four motors. Corrected mass 2.48 kg sized,
gate 2.6 kg; hover T/W ≈ 2.55; cruise ≈ 19 min (12 pessimistic) after 2 min hover on one 6500 pack.

- **Elevons sized from the twin, not from the card.** The card's 0.22 × 0.05 m pair is ≈ 6 % of wing area; tailsitter
  builders use far larger surfaces (`EVIDENCE.md` §1.3). Plan 20–25 % chord between the fins and outboard to the tips
  (`ESTIMATE` 15–25 % of area, +≈ 0.03 kg over the card), and freeze the size on what the foam-board twin needs.
- **Airspeed sensor in the order** (Holybro MS5525, $60) for `Q_TAILSIT_GSCMSK` gain scheduling. README D7 said
  "optional"; this decision says "fitted", because the probability claim in §4 rests on it.
- **No Remote ID module** (RFS is a FRIA, README §1). If a non-FRIA site is ever used, the $44 module comes from reserve.
- **Two Ovonic 4S 6500 packs**, not four (parity with K01-lean; 2 × 13 min hover-only; 70 min per charge). A third pack
  is the first reserve purchase after the first logged transition, if the reserve is still whole. US-stock fallback if
  Ovonic is out: Admiral 4S 4000 2-pack, $107, corrected cruise 11.4 / 7.1 min, still above the 5 min threshold.
- **1 kg PETG**; tray, feet and jigs in Jacobs' house PLA.
- Flight controller stays the CoreWing F405 Wing V2 at $67 (already the pessimistic price) **only if** a stable Plane
  build with tailsitter support exists for it (§8 item 3); otherwise SpeedyBee F405 Wing or Matek at the same money.

### 5.2 Operating limits the team lead is accepting with this choice

| Limit | Why |
|---|---|
| **Flight card: mean ≤ 5 m/s, gust ≤ 8 m/s, flights 07:00–10:00**; go/no-go from the RCMC1 real-time page plus a handheld anemometer on site | 36° lean at 8 m/s, tip-over at 39° (`cards/K09/REVIEW.md` §5); `WIND.md` shows this still gives 5–6 mornings a week in March–April |
| Land into wind, descent throttle kept up (`Q_TAILSIT_THR_VT`), slow `Q_LAND_SPEED`; first transitions ≥ 50 m AGL with recovery to QSTABILIZE rehearsed on the twin | Back-transition descent tumble and post-handoff dive are the two most-reported tailsitter failures (`EVIDENCE.md` §1.3) |
| Any single motor or ESC failure is a crash in both modes | Same as every quad in hover; unlike the quadplanes in cruise. Accepted for a demonstrator whose airframe costs $20 to re-cut |
| Mass gate 2.6 kg, tracked per subsystem every build week | Advisor's XV-24 lesson; every skeptic in this study found mass |

### 5.3 The three conditions that raise K09's probability (all cheap, all mandatory)

From `EVIDENCE.md` §3: K09 moves from ≈ 0.40 to ≈ 0.50 at week 8 when all three hold, and drops to ≈ 0.25 if the
first is skipped.

1. **Fixed-wing tune before any transition.** Tune hover, then tune FBWA trim, CG and gains as a separate campaign
   (Wurzburg's two-independent-tunes advice), so the first handoff is into a known airframe. Do the FW autotune on the
   foam-board twin by hand launch. The full 2.5 kg aircraft stalls at 11.2 m/s and cannot be hand-launched at throwing
   speed (`cards/K19/REVIEW.md` #9 makes the same point at 3.1 kg); options, decided from the twin's results: a $15
   surgical-tubing bungee (`ESTIMATE`, from reserve), or a vertical take-off to ≥ 50 m followed by a transition flown
   with the CG and trims carried over from the twin and the pilot ready on the QSTABILIZE switch.
2. **Airspeed sensor fitted** (§5.1).
3. **≥ 10 h SITL on the copter-tailsitter model** by the designated pilot before first hover (README D15 stands), plus
   a cheap quad or simulator for stick time.

### 5.4 Test sequence (the order matters more than the dates)

Twin: bench → tethered hover → hover in a 5 m/s fan or breeze (hold 1 m, log lean vs 16°) → hand-launch FBWA autotune
→ transition round trip at altitude → back-transition descent practice. Full aircraft: thrust stand (confirm 11×4.5MR
vs the 11×4.7 table) → tethered QHOVER (current 24 A ± 15 %) → QHOVER / QLOITER untethered → FW campaign (§5.3 item 1)
→ first transition ≥ 50 m → back-transition at altitude → landing practice in calm air → full demonstration.

## 6. Why the others lost

**K01-lean (twin-boom quadplane, re-sized).** Lost at gate 1 and nowhere else. Its own skeptic pass puts the
pessimistic reserve at ≈ $201 against the study's $309 crash and against its own $224 crash bill; even the baseline
$281 is $28 short of $309. The levers that could rescue it are a Jacobs tool loan (+$105, `UNVERIFIED`) and the
SpeedyBee being in stock at $48 (+$19, search snippet only); with both verified it reaches $327, and with only the loan
it reaches $308, one dollar short. Two further cautions: the lean card is self-reviewed, and every independently
reviewed card in this study got heavier, hungrier and dearer under review (README §6 item 5); and its top two risks
(single-saddle boom joint under 13 N·m; pusher thrust on a 10×6E with no maker table) are untested design items, not
tuning items. On step 3 it is the better aircraft: a tail, static margin set by construction (15 % / 8.5 % pessimistic),
the best-documented transition, a glide on lift-motor failure, 6.4–6.8 flyable mornings a week. None of that buys a
crash it cannot pay for.

**K19 (flying-wing quadplane).** Fails gate 1 by $76 pessimistic and by $9 even at its lean baseline, with no
identified recovery, and Maker Pass exposure on top. It is also the weakest flyer of the three: T/W 1.6 at low
voltage, which is exactly when the back-transition and landing happen; a ±13 mm CG window with elevon-only pitch at the
one moment the demo exists to show; the longest build (≈ 160 h pessimistic); a crash that is a 15 h centre-section
rebuild on overseas tubes. It would have lost step 3 to K01-lean and tied or lost to K09-L. It is a cheaper K01, not a
safer one (README §4.2), and it is not cheap enough.

**B08 and U01** were not judged: the team lead's rule excludes a bought airframe and a non-transitioning aircraft.
Their arithmetic (8.68 and 7.71 in README §3.2) is not disputed; the mission is.

## 7. What would reverse this decision

All of these must happen **before the mid-December order**. After the order the question is closed.

| If… | Then |
|---|---|
| **K01-lean's reserve reaches ≥ $309 on pessimistic numbers, verified**: Jacobs tool loan in writing **and** SpeedyBee F405 Wing in stock with a stable Plane build **and** an independent skeptic pass of `k01-lean/` adds less than ≈ $18 of cost | K01-lean passes gate 1 and **wins step 3**; the decision flips to K01-lean. This is three stacked `UNVERIFIED` items; do not plan on it, but do run the two emails (§8 item 9) because they are free |
| The foam-board twin **cannot hold position within 1 m at 5 m/s**, or cannot complete a transition round trip within the pre-order window | K09's wind limit or transition story is wrong. Fallback is K01-lean, and the team lead must then either verify the levers above or accept a reserve that covers K01-lean's own $224 crash bill rather than the study's $309. There is no third scratch concept inside the gate |
| Handheld anemometer at RFS shows morning wind ≥ 1.4× RCMC1 (RFS behaving like KSFO: ≈ 4 usable mornings a week) | K01-lean, same budget caveat as above. `WIND.md` says this is unlikely (RFS lies between RCMC1 and KOAK) but nobody has measured RFS |
| Jacobs **Maker Passes are charged to this budget** ($125–250, `UNVERIFIED`) | **No candidate passes gate 1** (K09-L pessimistic reserve falls to $71–196). The team lead must get them covered or relax the crash-reserve number; K09-L remains the least-bad choice because it has the largest reserve and the cheapest crash |
| The team lead redefines the crash reserve as each concept's **own** crash bill | K09-L passes with more room (own bill ≈ $230–245, `ESTIMATE`: the formula's $100 airframe line is ≈ $35 of foam and prints here). **K01-lean still fails** ($201 vs $224). The order does not change |
| The team lead accepts a bought PNP as student-built | B08, per README §4.2; this document is then moot |
| The CoreWing/SpeedyBee/Matek check (§8 item 3) finds **no stable Plane build with tailsitter support on any affordable F405/H743 board** | Hold the order; a beta-only autopilot on an undocumented configuration is a different risk class. This is a one-hour check and has never failed for quadplanes |

## 8. Immediate pre-order de-risking steps

Numbered by urgency. Everything here is inside the $1,679 pessimistic spend; nothing is extra money.

| # | Step | Who / cost / when | Pass criterion |
|---|---|---|---|
| 1 | **Partial early order (≈ $650 incl. tax) of the electronics set**: 4 motors, ESC 4-pack, FC, GPS, receiver, transmitter + 18650 cells, charger, LiPo bag, one 6500 2-pack, 4 props, 2 micro servos, foam board. All of it goes into the aircraft; nothing is wasted. Order the **CF tubes** in the same week (overseas, ≈ 2 weeks) | Team lead approves splitting the order; by ≈ 20 Nov | Parts in hand by early December. If the team lead will not split the order, the twin flies in build weeks 1–2 of January and no XPS is cut until it passes; the go/no-go moves 4 weeks right |
| 2 | **Build and fly the foam-board twin from Wurzburg's Box Kite guide** on the real motors, FC and pack (≈ $40 of board, 2 days). Run the §5.4 twin sequence, log every flight | 2 students, early December, 2–3 flying mornings | Hover held within 1 m in a 5 m/s fan or breeze, lean ≤ ≈ 20°; one logged transition round trip; elevon size that gives clean FBWA authority. Fail = §7 row 2 |
| 3 | **Confirm a stable (not beta) ArduPilot Plane build with tailsitter support** on firmware.ardupilot.org for the CoreWing F405 Wing V2; if absent, pick SpeedyBee F405 Wing or Matek F405-WING at the same money. Confirm DShot on 4 motor outputs, 2 servo outputs, I2C for the MS5525 | 1 student, 1 hour, before step 1 | Board name on the stable-build list; output map written down |
| 4 | **Measure RFS wind**: handheld anemometer ($20–30, from the hardware line) on 2–3 mornings at 2 m and ≈ 5 m, logged against RCMC1 real time | 1 student, November | RFS/RCMC1 ratio known; flight card limit confirmed or rescaled |
| 5 | **Design the fin-tube joint and the box cradles** (one print iteration; the card's "two foam-board layers over a 22 mm tube" is not flat), and **size the elevons** from step 2 | 2 students, December, in parallel with the twin | Printed clips fit a real tube; box drawing with cradles under the spar; elevon size and servo torque on paper |
| 6 | **SITL**: ≥ 10 h on the copter-tailsitter model by the pilot, plus stick time on a cheap quad or simulator | Pilot, December–January | Logged hours; QSTABILIZE recovery from a failed transition practised |
| 7 | **Measure two team members' cars** against a 1.25 × 0.55 × 0.45 m box | 10 minutes | At least two cars take it on the back seat or in a hatchback |
| 8 | **Weigh the first pack and the first XPS core**; re-run `cards/K09/sizing.py` with the real masses | On arrival | Mass tracking starts at zero, not at first flight |
| 9 | **Three emails**: Maker Pass coverage for spring 2027; whether course flights are recreational/educational (no $175 Part 107 exam); whether Jacobs lasers foam board (knife-cut fallback costs nothing). **Plus two more** that settle §7 row 1 for free: Jacobs tool loan (iron, multimeter, PD supply) and SpeedyBee stock | Team lead, this week | Written answers before the order |
| 10 | **Freeze the K09-L BOM** (§5.1) and reconfirm Ovonic price and stock on order day; take the Admiral 4000 fallback if Ovonic is out | Team lead, mid-December | Pessimistic reserve ≥ $309 on the day; if an adder lands, defer the airspeed sensor to a reserve purchase before touching anything else |

## 9. Numbers behind the tables (checkable)

Tax 10.25 %. K09 corrected total from `cards/K09/REVIEW.md` §6: $1,528.51 + $89.49 + $9.17 + $5 = **$1,632.17**.

| K09-L line | $ |
|---|---|
| Start, skeptic-corrected | 1,632.17 |
| − Remote ID 39.99 × 1.1025 | −44.09 |
| + Elevons (2 micro servos, hinge, horns) 30 × 1.1025 | +33.08 |
| + MS5525 airspeed 59.99 × 1.1025 | +66.14 |
| − One 6500 2-pack at sale price 79.25 × 1.1025 | −87.37 |
| − 1 kg PETG 20.99 × 1.1025 | −23.14 |
| **Baseline spend / reserve** | **1,576.78 / 423.22** |
| + Remaining 2-pack at list (119.88 − 79.25) × 1.1025 | +44.79 |
| + Shipping, tax measure, jig and box | +30 + 7 + 20 |
| **Pessimistic spend / reserve** | **1,678.58 / 321.42** |
| Pessimistic without the airspeed sensor | 1,612.44 / 387.56 |
| Pessimistic if four packs were kept at list price | 1,810.75 / 189.25 (fails: this is why the pack count changed) |

K01-lean: `k01-lean/cost.csv` total $1,718.62 → reserve $281.38; own skeptic S8–S11 (+30 +19.27 +7 +22) → $1,796.89 →
reserve **$203** (the card rounds to ≈ $201). With a $105 Jacobs loan: $308. With the SpeedyBee also in stock: $327.

K19: `cards/K19/REVIEW.md` corrected $1,810 (RID in, 3 packs at $59.91) → − RID $44.09 − one pack $66.05 =
$1,699.86 → reserve $300; adders +7 +20 + two packs from a US stocker (+$18 each, +$39.69 with tax) → $1,766.55 →
reserve **$233**.

Probability model (`EVIDENCE.md` §3): P = 0.85 (stable hover) × (1 − (1 − h)^weeks left) × discount. K09: h =
0.15–0.25 per week, 4.5 weeks left by week 8 and 8.5 by week 12, discount 0.80 (crash + wind) → 0.35–0.49 at week 8,
0.51–0.62 at week 12. K01-lean: h = 0.35–0.40, 3.5 and 7.5 weeks left (hover week 4–5 at 130–150 h), discount 0.85 →
0.56–0.60 at week 8, 0.69–0.71 at week 12. All `ESTIMATE`; the evidence base is a forum sample that under-reports
successes and gives sizes for few of them.

Wind (`WIND.md` §2b, March–April 2022–2025, 07–10 h, all hours inside the limit): 5 / 8 m/s limit gives 5.7 mornings
a week at RCMC1 and 5.0 at KOAK (worst years 5.0 and 4.6); 8 / 12 m/s limit gives 6.7 and 6.4. The README §4.3 flip
condition "> 5 m/s on most mornings" is **not met**. Rain is not counted; RFS itself is unmeasured (step 4).

## 10. What this decision does not claim

- It does not re-rank B08 or U01, and it does not re-run any sizing script. It applies the team lead's rule to the
  numbers already in the study and in `tiebreak/`.
- The K01-lean numbers are the lean card author's own skeptic pass; no independent reviewer has seen them. The study's
  history says an independent pass would move them the wrong way for K01-lean.
- Every probability is an `ESTIMATE` built on a forum sample. The one fact that should worry the team is that no logged
  elevon quad-tailsitter round trip in this class was found; the twin in step 2 is how the team makes its own evidence
  before any XPS is cut, and §7 says what happens if the twin says no.
