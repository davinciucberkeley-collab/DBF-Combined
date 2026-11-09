# Judge: build, transport, repair and maintain (one lens)

Status: PROPOSED (judge, build-and-transport lens, 2026-11-09). Inputs: `STUDY-BRIEF.md`, `inputs/ADVISOR-XV24-LESSONS.md`,
`inputs/MENTOR-GUIDANCE-2026-11-04.md`, `requirements/REQUIREMENTS.md`, `screening/SCREENING.md`, and every
`cards/*/CARD.md` and `cards/*/REVIEW.md`. **Skeptic-corrected numbers are used wherever the two disagree.**
Tags: `ESTIMATE` = engineering guess, `UNVERIFIED` = not checked against a primary source.

**The one question this file answers:** can a UC Berkeley student team actually build, transport, repair and maintain
this aircraft inside $2,000 and by the end of April 2027? Nothing else is scored here. Hover margin, transition
tuning, mission fit and capstone content belong to other judges; they appear below only where they change build
hours, the repair loop or the reserve.

---

## 1. Rubric (five sub-scores, 2 points each, sum = score out of 10)

| Sub-score | 2 | 1.5 | 1 | 0.5 | 0 |
|---|---|---|---|---|---|
| **A. Process availability** (Jacobs Hall: FDM, laser, hot-wire bow, hand tools, bought parts) | Everything bought, or standard foam/FDM with nothing left to design under load | Small design items still open (a socket sleeve, an adapter plate, a fin joint) | A loaded mechanism the team designs and iterates, or a structural fix the skeptic says must be done before the order | A process whose availability at Jacobs is not confirmed | A process Jacobs cannot do |
| **B. Team-hours to first hover** (skeptic-corrected) | ≤ 90 h | 90-120 h | 120-150 h | 150-180 h | ≥ 180 h, or the skeptic says the 12 weeks fit "only if nothing slips" |
| **C. Part count and field joints** | ≤ 4 motor stations, ≤ 2 servos, ≤ 3 field joints, no tools | ≤ 5 stations or ≤ 4 servos, ≤ 5 joints, no tools | 5 stations and 4 servos, or tools and ≥ 5 plugs at every assembly | More | - |
| **D. Packability** (skeptic-corrected box) | One box, longest side ≤ 0.9 m, ≤ 5 kg, 1 person, ≤ 5 min | One box ≤ 1.1 m, or 1 person but 5-10 min | One box ≤ 1.25 m, back seat or hatchback only, 2 people or ≥ 10 min, or a heat/transit fragility | Two boxes | Fails C3 |
| **E. Crash repair and reserve** | 1 point: corrected reserve ≥ one "bad crash" at the card's own price. 1 point: the likely-broken part is repaired in ≤ 1 day from US-stock parts and a spare is in the BOM. Half credit where a condition is partly met | | | | |

Calendar conversion used throughout: 3-4 students at about 10 h/week each on the build = **30-40 team-hours per week**
`ESTIMATE`. 85 h is 2-3 weeks; 180 h is 5-6 weeks. The worst-case window is 12 weeks (early February to end of
April) and must hold at least one crash-repair cycle. Richmond Field Station needs a flight request **≥ 7 business
days ahead** (REQUIREMENTS D5), so every crash-repair-refly loop costs **≥ 1.5 weeks of calendar even when the
repair itself takes a day**. A concept that needs several tuning sessions spends its calendar in that loop.

---

## 2. Evidence table (skeptic-corrected)

| | Processes the team must run | Team-hours to first hover | Stations / servos / loaded mechanisms | Field assembly | Packed | Crash repair path | Reserve vs one bad crash | Long-lead or unconfirmed parts |
|---|---|---|---|---|---|---|---|---|
| **K01** twin-boom quadplane | Hot-wire XPS, tape skin, foam-board tail, FDM PETG nodes (~40 printer-h), stock 1 m CF tubes | **150-180 h** (card 100-120) | 5 / 4 / 0; **full-span spar and a CG/tail fix still to be designed** (REVIEW C3, C4) | 5 joints + 6 plugs, 2 people, ~10 min, hex keys | 1 box 1.2 × 0.5 × 0.4 m, ~7 kg, longest 1.0 m; back seat or hatchback; **box not costed** | Wing half re-cut ~1 day, mounts overnight. A cracked 25 mm boom means a **2-4 week overseas re-order; no spare in BOM** | **$103 vs $266: no** | 25 mm CF tubes (overseas), FC backordered, BOM names one FC and links another |
| **K19** flying-wing quadplane | Hot-wire XPS with laser-cut ply templates, ply hard points, bandsaw CF, tape, FDM PETG (~40 unattended h) | **120-140 h** (card 95) | 5 / 2 / 0; joiner socket needs a glued sleeve + ply ribs (REVIEW #8, +3 h) | 5 joints, 1 person, 8-10 min, no tools | 1 box 1.2 × 0.5 × 0.4 m, ~6 kg, longest 1.06 m; back seat; box not costed | Outer panel ~6 h; **boom hard-point tear-out = new centre section ~15 h**; all 3 CF tubes consumed, no spare (overseas) | **$190 vs $310: no** (Maker Passes could take it to $0-65) | 22 mm CF tubes (overseas), CoreWing backordered, Ovonic 6500 out of stock (EU shipping) |
| **K06** scratch tilt-tri | Hot-wire XPS, tape, foam-board fins, FDM PETG pod (30 unattended h), **team-designed tilt nacelles (6 mm shaft, 2 bearings, servo link; card plans 3 print iterations)**, boom | **~180 h** + 3-4 weeks tilt tuning; "fits 12 weeks only if nothing slips" (REVIEW C15) | 3 / 4 (2 tilt + 2 elevon) / **2** | 5 joints (XT60 + 6-pin plug per side), 1 person, ~8 min | 1 box 0.88 × 0.50 × 0.39 m, ~4 kg, longest 0.78 m; any trunk | Wing half 4 h, nacelle overnight; shaft/bearing spares not listed; **no mass headroom: T/W 1.62 fresh, 1.53 end of pack, so glue and tape from a repair push it under the gate** | **$295 vs $340: marginal** ($217 if the K07 fourth motor is bought) | CF tubes (overseas), CoreWing backordered (Kakute H743 fallback +$40) |
| **K09** quad tailsitter | Hot-wire 2 in XPS, epoxy spar slot, tape, foam-board fins (laser on foam board `UNVERIFIED` at Jacobs; knife fallback costs nothing), FDM PETG mounts, saddles, feet, tray | **70-85 h** (+30-40 h of transition flight-test sessions) | 4 / **0** / 0; fin-tube joint needs one design-and-reprint iteration (REVIEW §2) | **No structural joints**: 4 props + pack, 1 person, ~5 min | **One piece**, but the real box is ~1.25 × 0.55 × 0.45 m external, ~6 kg; back seat or hatchback, marginal in a compact trunk; exposed fins and motor tubes need cradles | Wing re-cut in a day, ~6 cores per XPS sheet, feet reprinted; fin-tip landings in gusts are the recurring damage mode | **$368 vs $309: yes** | CF tubes ~2 weeks; everything else US stock |
| **B08** buy HEEWING T1-S PNP | None structural: glue, solder, FDM only for an optional modification | **First hover in build week 1-2**; 80-100 h of which 40-60 h is an optional measured modification | 3 / bought / bought | Wing halves slide on, 1 person, ~3 min, no tools | Maker foam case ~0.75 × 0.42 × 0.18 m, ~2.5 kg with 4 packs; fits a back seat fully assembled | Foam + CA; spare motors, servos, wing set and tail; **a whole second airframe (~$434) is affordable**; US stock 3-7 days | **$570: yes**, more than a second airframe | None long-lead. RDQ price/stock `UNVERIFIED` (fetch blocked); V1 vs V2 board check on arrival; T1 spares-kit fit on the T1-S `UNVERIFIED` |
| **B09** print Flightory Stallion | **FDM only** (LW-PLA + PETG), ~100 printer-h on shared Prusas (1 printer per user, >4 h jobs overnight, 12 h cap); cut CF, heat-set inserts. **Jacobs' policy on bring-your-own LW-PLA not found**; fallback is a team printer (~$250-350) | **~125 h**, 3-4 weeks first print to first hover; design hours near zero | 3 / 4 (2 tilt + 2 aileron) / 2 (bought design) | Spar + 2 wings + 2 multi-pin plugs each, 1 hex key, 1 person, ~10 min | 1 box 1.09 × 0.44 × 0.31-0.41 m, ~3 kg; box not costed; **LW-PLA HDT 50-54 °C, a car in the sun can warp it** | Reprint a wing half ~25 printer-h plus queue; LW-PLA is brittle in a crash; spare spool bought | **$305 vs $208: yes** ($55 if two Maker Passes are paid from the budget) | SpeedyBee F405 Wing backordered (losing it loses the supplied output map); personal-use licence needs an email; LW-PLA policy |
| **U01** wing-assisted quad on X500 | Bought carbon frame; printed or aluminium motor adapters (16 × 16 vs X3108 pattern `UNVERIFIED`); hot-wire 1 in XPS halves, tape, printed saddle and masts | **70-85 h**, ~3 weeks | 4 / 0 / 0 | 2 thumb-screws + 4 props + pack, 1 person, ~5 min; no wiring crosses the wing joint | 1 box ~0.80 × 0.44 × 0.38 m, ~4.5 kg, longest 0.75 m | **Bolt-on arms** (spare set +$30), re-cut foam half; ~1 day; all US stock | **$374 vs $275: yes** (1.4 crashes) | None |

Sources: each row is the concept's REVIEW.md "numbers I believe" table, with CARD.md where the reviewer did not
challenge the item. Bad-crash prices are the cards' own ($266 K01, $310 K19, $340 K06, $309 K09, $434 whole airframe
B08, $208 B09, $275 U01).

---

## 3. Scores

| Rank | Concept | A Process | B Hours | C Parts, joints | D Pack | E Repair, reserve | **Score /10** | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | **B08** buy T1-S PNP | 2 | 2 | 2 | 2 | 1.5 | **9.5** | Medium: price and stock not opened; T1-S dimensions came from a distributor, not the maker |
| 2 | **U01** wing-assisted quad | 1.5 | 2 | 2 | 2 | 1.5 | **9.0** | Medium-high: bought frame and motors are vendor-listed; adapter pattern `UNVERIFIED` |
| 3 | **K09** quad tailsitter | 1.5 | 2 | 2 | 1.5 | 1.5 | **8.5** | Medium: all hours `ESTIMATE`; the fin-tube joint is undesigned |
| 4 | **K19** flying-wing quadplane | 1.5 | 1 | 1.5 | 1 | 0.5 | **5.5** | Medium |
| 5 | **B09** printed Stallion | 0.5 | 1 | 1.5 | 1 | 1 | **5.0** | Low: hinges on one unanswered policy question (LW-PLA at Jacobs) |
| 5 | **K06** scratch tilt-tri | 1 | 0 | 1.5 | 1.5 | 1 | **5.0** | Medium |
| 7 | **K01** twin-boom quadplane | 1 | 0.5 | 1 | 1 | 0.5 | **4.0** | Medium-high: the previous team's work makes the numbers the best-checked, and they are still the worst for this lens |

Tie-break at 5.0: B09 ranks above K06 because its bottleneck is one yes/no answer from Jacobs Hall, while K06's is
180 team-hours and a loaded mechanism the team must iterate three times.

---

## 4. Reasons, one concept at a time

### B08, buy the T1-S: 9.5
Nothing structural is made, so there is nothing for a first-time team to get wrong in the shop. First hover is in
build week 1-2, which leaves ten of the twelve weeks for test, crashes and the measured modification. It packs in the
maker's foam case at about 2.5 kg and goes field-ready in three minutes with no tools, the best transport story in the
study. The corrected reserve ($570) buys a complete second airframe with change, so a bad crash is a shopping trip,
not a schedule event, and the EPP/foam-and-CA repair path is the one every hobby shop uses.
Deductions (E 1.5): hover T/W falls to 1.5 with the 0.25 kg growth allowance, so **any repair or modification must be
mass-neutral**; the 9 g tilt servos are the single point of failure; the T1 spares kit in the BOM may not fit the T1-S;
and the $393 price with US stock is a search snippet the card could not open. None of these stop a student team
building, transporting and repairing it. What it does not give the team is design work, which is another judge's lens.

### U01, wing-assisted quad on a bought frame: 9.0
A bought carbon frame with four bolt-on stations is the most crash-tolerant structure in the set: arms are swapped,
not rebuilt, and a spare arm set is $30. The only team-made parts are a hot-wired foam wing, a printed saddle and a
motor adapter plate. 70-85 h to first hover with everything in US stock. One box, 0.80 m, 4.5 kg, one person, five
minutes, and no wiring crosses the wing joint. Reserve $374 covers 1.4 bad crashes.
Deductions: the 16 × 16 to X3108 adapter pattern is `UNVERIFIED` and the saddle needs an iteration (A 1.5); the
spare arm set was added by the skeptic, not the card, and tape-skinned halves dent in transit (E 1.5). The mission
question (it never transitions) is real but outside this lens.

### K09, quad tailsitter, motor-only: 8.5
The simplest scratch build in the study: one hot-wired core, one spar, two foam-board fins, two tubes, four printed
mounts, four feet, **zero servos and zero structural field joints**. 70-85 h to first hover. A crashed wing is re-cut
in a day and one XPS sheet holds about six cores, so the airframe is nearly a consumable. Reserve $368 covers one bad
crash. All parts except the CF tubes (about 2 weeks) are US stock.
Deductions: the one-piece aircraft needs the **largest box in the study** (about 1.25 × 0.55 × 0.45 m external, 6 kg)
with cradles under the spar because the fins and motor tubes are exposed; it rides on a back seat or in a hatchback,
not in a compact trunk (D 1.5). The fin-tube joint is not yet designed and will take a reprint iteration (A 1.5). The
recurring damage mode is a fin-tip landing in a gust (feet, props, possibly a tube), and the 30-40 h of tailsitter
transition sessions go through the RFS 7-day request loop (E 1.5, and a schedule caution).

### K19, flying-wing quadplane: 5.5
Hot-wire foam plus bought parts, 120-140 h, no tail boom and only two servos, one box and no field tools. Buildable,
and simpler than K01. What pulls it down is the repair-and-reserve column: the corrected reserve of **$190 is below one
bad crash ($310)** and could fall to $0-65 if Maker Passes come out of the budget; all three CF tubes are consumed
with no spare and they ship from overseas; and the likely hard-landing damage (boom hard-points tearing out of the
foam) is a **15 h centre-section rebuild**, not a panel swap. Add the joiner-sleeve redesign before order, a
backordered FC and an out-of-stock pack, and this is a build that can finish but cannot afford to crash once.

### B09, printed Flightory Stallion: 5.0 (conditional)
On paper the easiest process list of any built concept: FDM only, on free Jacobs printers, from a design that already
flies, with near-zero design hours and about 125 team-hours. The reserve ($305) covers 1.5 typical crashes.
But the airframe process rests on a policy nobody has confirmed: **the Jacobs labs page says printers run the house
PLA and no bring-your-own-LW-PLA rule was found**. If LW-PLA is refused, the concept loses its only manufacturing
process and the fallback (a team printer, $250-350) eats the reserve. Even if allowed, ~100 printer-hours on shared
machines with a 12 h overnight cap is calendar the team does not control, a crashed wing half is a **25 printer-hour
reprint plus queue** rather than a one-day foam cut, LW-PLA is brittle in a crash, and its 50-54 °C HDT means a car
parked in the sun can warp the airframe on the way to the field. Score 6.5-7 if Jacobs says yes in writing before
December; 3 if it says no.

### K06, scratch tilt-tricopter: 5.0
Packs best of the scratch concepts (0.88 m box, 4 kg, one person, 8 min) and has only three motor stations. Everything
else in this lens works against it. It is the only shortlisted concept where the team **designs a loaded mechanism
from scratch** (tilt nacelle: shaft, two bearings, servo link) and the card itself budgets three print iterations.
Corrected effort is about **180 team-hours plus 3-4 weeks of tilt tuning**, and the skeptic's words are "fits 12 weeks
only if nothing slips". The reserve ($295) is below one bad crash ($340). The subtler maintenance problem is mass:
corrected T/W is 1.62 fresh and 1.53 at the end of the pack, so **there is no mass budget for repairs**; the tape,
glue and reinforcement every crash repair adds push it under the gate. The K07 fourth motor fixes that for $78 and
takes the reserve to $217.

### K01, twin-boom quadplane 4+1: 4.0
The processes are all ordinary (foam, tape, stock tubes, printed nodes) and the previous team's sizing transfers, which
is why this scores higher on confidence than on buildability. It has the **most parts and the most field work** of
the set: five stations, four servos, two booms, a tail, 5 joints and 6 plugs at every assembly by two people with hex
keys, in the largest and heaviest box (1.2 m, 7 kg). Corrected build is **150-180 h**. Two structural facts are still
undecided (no spar; static margin 0-3 %), so design work remains before the December order. The decisive column is the
reserve: **$103 after corrections, below one bad crash ($266)**, with no spare boom and the boom being the part a
tip-over breaks, on a 2-4 week overseas lead. A team that crashes this aircraft once in March has neither the money nor
the time to be flying again by April.

---

## 5. Findings that cut across every card (this lens)

1. **No scratch card costs its transport box.** K01, K19, K09 and B09 all claim "one box" with no line for it
   ($20-60 `ESTIMATE`, per the reviews). Add it, or plan to build one from foam board and ply at Jacobs.
2. **Carbon tubes are the common long-lead part.** K01, K19, K06 and K09 all buy CF tubes from overseas, and K01 and
   K19 buy none spare. Order tubes first, in December, with at least one spare per size; or price a US composites
   vendor (`UNVERIFIED`, about $60-80 per tube).
3. **The flight controller is backordered on five of seven cards** (CoreWing F405 Wing V2 or SpeedyBee F405 Wing). Pick
   an in-stock board before the order freeze; for B09 that also means re-doing Flightory's output map.
4. **Maker Passes ($125 per student per semester, `UNVERIFIED` for spring 2027) are not in any BOM.** If the course
   does not cover them, K19 and B09 lose most of their reserve and every concept loses $125-250. One email settles it.
5. **The RFS request lead time is the real repair clock.** A one-day repair still costs about 1.5 weeks of calendar
   before the aircraft flies again. Concepts whose first weeks are spent in multiple tuning sessions (tilt and
   tailsitter transitions) should budget the calendar, not just the hours.
6. **Small missing lines appear on every card:** 2 × 18650 cells for the RadioMaster Pocket (~$15-25), FAA registration
   ($5), a LiPo checker (~$8), a hot-wire jig where foam is cut (~$15). About $50 per card, already in the corrected
   totals above.
7. **Mass headroom is a maintenance property.** Repairs add mass. K06 (T/W 1.53-1.62) and B08-with-growth (1.5) have
   none; K09 (2.6) and U01 (2.2) have plenty. A concept at the T/W gate cannot be patched after a crash without
   re-checking the gate.

---

## 6. What to open before the December order, by concept (this lens only)

| Concept | Must be settled before parts are ordered |
|---|---|
| B08 | Open the RDQ/GetFPV page: US stock, price, which board revision ships (V2 logs; V1 does not). Confirm a T1-S-specific spares kit. |
| U01 | Confirm the X500 V2 motor-mount pattern against the X3108S bolt circle; buy the spare arm set. |
| K09 | Design the fin-tube joint and the box cradles; buy one spare CF tube; confirm Jacobs will laser foam board (or plan to knife-cut). |
| K19 | Add the joiner sleeve and ply ribs; buy 2 spare 22 mm tubes; find a US LiPo stocker; confirm a stable Plane build for the chosen FC. |
| B09 | Get Jacobs' answer on bring-your-own LW-PLA in writing; email Flightory about the licence; pick an in-stock FC. Do the week-1 one-wing-half print and load test before buying anything else. |
| K06 | Decide K06 vs K07 on mass headroom; build the nacelle bench rig (SCREENING §5) before committing to three print iterations; list shaft and bearing spares. |
| K01 | Add the spar and the CG/tail fix, then re-run cost; buy a spare boom; recover at least $150 of reserve (drop the RID module if RFS is confirmed a FRIA, buy 2 packs) or this concept cannot absorb a crash. |

Everything in sections 2-4 is `ESTIMATE` where the source was a card build-up; the cheapest way to replace the
estimates is the SCREENING §5 one-day tests (a foam panel cut and weighed, one printed nacelle on the thrust stand),
which also give the team its first real number for its own build rate.
