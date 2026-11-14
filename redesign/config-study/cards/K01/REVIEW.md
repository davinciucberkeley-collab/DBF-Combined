# K01 skeptic review

Reviewer: skeptic agent, 2026-11-09. Card files read: CARD.md, sizing.py, sizing.json, cost.csv. The card was not edited.
Mission used for this review: the team lead's VTOL demonstrator (take off, transition, short cruise, transition back,
land). That mission needs about 5 min of cruise, not 22, so endurance matters less than hover margin, stability and cost.

## 0. Re-run
`python -I sizing.py` was run on a copy in the scratchpad. The output matches `sizing.json` byte for byte, so the card
is reproducible. The arithmetic is correct. The problems are in the inputs and in what the model leaves out.

## 1. Challenges

| # | Claim on card | Challenge | Evidence | Corrected estimate |
|---|---|---|---|---|
| C1 | MTOW 3.22 kg including 0.25 kg growth | Optimistic. There is no wing spar (see C3), the 1 m wiring runs to four lift ESCs are light at "0.48 kg incl. wiring", and printed PETG motor mounts, saddles and legs usually come out heavy. The growth allowance is 8 %, and the advisor's XV-24 run shows how mass grows (3 kg target, then 6 kg). | Mini Talon quadplane conversions (1.3 m molded EPO, smaller than K01) are reported at 2.55 kg, 2.86 kg and 3.0 kg all-up on 4S 6 Ah or 6S packs ([ArduPilot Discuss thread](https://discuss.ardupilot.org/t/another-mini-talon-quadplane-conversion/64398), forum claims). A 1.6 m hand-built XPS airframe with two 1 m CF booms should not be lighter than those. | **3.45 kg** `ESTIMATE` (spar +0.08, wiring +0.05, printed parts +0.07, rounding +0.03). Range 3.3 to 3.7 kg. |
| C2 | Hover 523 W / 35 A, T/W 1.96 (1.83 with sag) | The SunnySky table is a bare-motor bench test on 11x4.7 at a steady 14.8 V. The card buys 11x4.5MR props. Download is set to 1.03, but the rear discs start 3 cm behind the TE and the front discs overlap the boom and saddle, so blockage is larger. At 3.45 kg T/W drops below the "1.8 after +0.3 kg" figure on the card. | Re-run with dm +0.23 and DOWNLOAD 1.08: 680 W table, 46 A, T/W 1.83 table / **1.70 with sag**, hover at 56 % of max thrust. The table has no point between 870 g and 1580 g, so linear interpolation there runs about 4 % high (power-law fit through 750/870 g gives exponent 1.66). For comparison, a Mini Talon builder measured about 533 W hover at roughly 2.9 kg (same thread, forum claim). | **Hover ≈ 650 W / 44 A** `ESTIMATE`. **T/W 1.83 table, ≈ 1.70 with sag.** This still passes 1.6, but with no margin for a gust or a motor-out. |
| C3 | Wing is "hot-wired XPS cores, tape skin, CF joiner socket"; booms clamp into "printed wing saddles" | **There is no spar.** The 0.40 m joiner ends 0.20 m from the centreline, and the booms sit at 0.30 m. Hover thrust, landing loads and in-flight bending all pass through bare foam between 0.20 and 0.30 m, and from the booms out to the tips. | At 3 g in cruise, the bending moment at the joiner end is about 9.2 N·m (calc: half-lift outboard of 0.20 m at its centroid minus boom inertia relief). Using Z ≈ 0.1·c·t² = 2.25e-5 m³ for a 30 mm thick, 250 mm chord section, the stress is **≈ 0.41 MPa**. That is at or above the flexural strength of building-grade XPS (a few tenths of a MPa, `UNVERIFIED` per grade). Packing tape adds little in compression. Boom twist into the foam is already the card's own risk 3. | Add a full-span CF spar (tube or strip, about 1.6 m), with each boom saddle clamped to the spar rather than to the foam. **+0.08 kg, about +$20.** Extending the joiner past the boom station would also work. |
| C4 | CG target 34 % MAC (the lift centroid) | **Static margin is close to zero.** The CG is set by where the motors are, not by where the aircraft is stable. The tail is small (Vh 0.38) on a short 0.60 m arm. | Wing-plus-tail neutral point: a_w = 4.62/rad (AR 6.4), dε/dα = 0.46, a_t ≈ 3.0/rad on projected area, η = 0.9, which puts the NP at **≈ 37 % MAC**. The pod and booms move it forward by a few % MAC, giving a static margin of **0 to 3 %** `ESTIMATE`. ArduPilot will fly it in Q modes, but in FBWA cruise it will be pitch-sensitive or divergent. | Move the front motors forward (X_FRONT about −0.30 m) so the lift centroid sits near 25 % MAC, and/or increase the tail chord to about 0.18 m (Vh ≈ 0.5). Cost is about +20 g. Run a 10-minute XFLR5/AVL check before the order freeze. |
| C5 | Peak transition 65 A, needing 82 A on the AS150U; the fix is to cap the pusher at 70 % | At the corrected mass, hover is about 44 A + 30 A pusher = 74 A. 1.25× that is **93 A**, more than the AS150U's 70 A continuous rating. A throttle cap is a firmware workaround for a connector choice. | Re-run above. | Use an XT90-S anti-spark connector (90 A class, about the same price, `UNVERIFIED` rating), or fit two AS150U in parallel. The card keeps the cap. |
| C6 | FC: "CoreWing F405 Wing V2 (Plane beta target)" | The cost.csv line names the CoreWing, but its URL is the **SpeedyBee F405 Wing** page at ReadyMadeRC. The BOM is inconsistent. A beta-only firmware target on a first quadplane adds controls risk the team does not need. | cost.csv row "Avionics, CoreWing…" and the link `85786-speedybee-f405-wing…`. The SpeedyBee F405 Wing has a stable ArduPilot target (`UNVERIFIED` for 4.6/4.7 stable; check firmware.ardupilot.org before ordering). | Make the SpeedyBee F405 Wing the baseline at about the same price. Check before ordering that DShot works on all 5 motor outputs (timer groups). |
| C7 | Cruise L/D 7.2, 22 min after 2 min hover | It does not matter much. The demonstrator needs about 5 min. The drag model is optimistic (prop efficiency 0.60, interference 1.15). | Pessimistic re-run (prop efficiency 0.50, interference 1.35): L/D 6.6, 211 W, **14.6 min** with the 6500 pack at 3.45 kg. | **Cruise 15 to 20 min** (6500 pack). Even the worst case meets the mission. This shows the 6500 pack is oversized; see the recommendation below. |
| C8 | Hover-only 8.8 min | This depends on the mass and download corrections. | Re-run at 3.45 kg with download 1.08: 6.8 min with 20 % reserve. | **≈ 7 min** hover-only (6500). |
| C9 | Packed in one 1.2 × 0.5 × 0.4 m box | The fit itself is plausible (stacking sum 0.50 m wide). But a 1.2 m box often does not go through a compact sedan trunk opening (typically about 1.0 m wide, `ESTIMATE`). It fits on a rear seat or in a hatchback. **The box is not in the BOM.** | Geometry in sizing.py `packing()`. | Plan for the back seat or a hatchback. Add the box (about $25, or build one from foam board/ply). Cutting the booms to 0.9 m would let the box shrink to 1.1 m. |
| C10 | 100 to 120 team-hours, 5 to 7 weeks to first hover | Low for a first-time quadplane. The 30 h for ArduPilot setup and tuning is light: Q-mode tuning, the airspeed sensor, transition tuning and failsafes typically take several flying days. The 22 h wing figure also assumes a working hot-wire bow already exists. | Advisor lesson (the schedule was eaten by detail) and the brief's 12-week worst case. | **150 to 180 team-hours** `ESTIMATE`. With 3 to 4 people that is still about 6 to 8 weeks to first hover, so it fits, but with less flight-test slack than the card claims. The build itself (foam, stock tubes, printed nodes) is genuinely simple. |
| C11 | Lead time: "CF tubes ship from overseas" | Only one spare-ish tube is bought (the 22 mm joiner stock). There is **no spare 25 mm boom**, and a boom is the part most likely to crack in a tip-over. An overseas re-order during the semester costs 2 to 4 weeks. | cost.csv. | Buy a third boom tube up front (+$40.99), or buy from a US composites vendor (pricier, `UNVERIFIED` about $60 to 80 per tube). |
| C12 | Single-point failure in hover | Agreed with the card: any lift motor or ESC lost in hover means a crash. BLHeli_S ESCs are FPV parts with no continuous rating listed (budget-lift.md note 5). | docs/research/budget-lift.md. | Keep this as risk 1. With the corrected T/W of 1.70, the hexa option (K21) earns more weight than the card gives it. |

## 2. Missing or questionable cost lines

| Item | Pre-tax $ | Basis | Flag |
|---|---|---|---|
| Full-span CF spar (C3) | 20.00 | Amazon CF tube/strip class | `ESTIMATE` |
| Spare 25×22×1000 boom (C11) | 40.99 | Same line as the card | from cost.csv |
| 2× 18650 cells for the Pocket transmitter (the Pocket takes 18650 cells; whether the Crush kit ships with cells is unclear) | 15.00 | | `UNVERIFIED` |
| APC LPAR06E adapter rings (budget-lift.md says MR props need them and they are "not included"); may already sit in the $124 hardware lump | 10.00 | | `ESTIMATE` |
| Transport box (C9) | 25.00 | | `ESTIMATE` |
| Hot-wire bow/frame and templates (only the supply and wire are costed) | 15.00 | | `ESTIMATE` |
| Smoke stopper or fused lead for first power-up | 10.00 | | `ESTIMATE` |
| **Subtotal** | **135.99** | + 10.25 % tax = **$149.93** | |
| FAA registration (no tax). A Part 107 test (about $175) is only needed if the flights do not count as recreational/educational. | 5.00 | faa.gov | conditional |

- **Tax:** the 10.25 % Berkeley rate is right for a December 2026 order. Most of Alameda County is at 10.75 %, and a 0.5 % Berkeley increase was on the 3 November 2026 ballot ([Local News Matters, 2026-06-17](https://localnewsmatters.org/2026/06/17/berkeley-sales-tax-increase-budget-deficit-ballot-measure/); [CDTFA rates](https://cdtfa.ca.gov/taxes-and-fees/rates.aspx?os=0)). A new rate would normally start on a later quarter boundary, so the effect is about +$7 at most. `UNVERIFIED` whether it passed.
- **Pack price:** the line assumes an Ovonic 2-pack. If only single packs are available, add +$43.47 (as the card notes).
- **Charger:** the HTRC C150 (150 W) charges one 96 Wh pack at about 1C in roughly 70 min, so three packs take about 3.5 h. That is fine overnight, and there is no field charging. This is acceptable, not a missing line.

**Corrected total:** $1,741.68 + $149.93 + $5 = **≈ $1,897**, which leaves **≈ $103 reserve**. That is below the card's own $150 target and below one bad crash (about $266 per cost_model.py).

Ways to recover it:
- Drop the conditional RID module (−$44 incl. tax) if Richmond Field Station is a FRIA (`UNVERIFIED`).
- Buy 2 packs instead of 3 (−$50).
- Borrow the iron, multimeter and supply from Jacobs Hall if allowed (up to −$95, `UNVERIFIED`).

## 3. Points that hold up
- The model is reproducible, uses the stdlib only, and keeps its assumptions in one block.
- The momentum cross-check agrees with the table to within 7 % at 3.22 kg.
- Using stock parts throughout (no cut tubes, Lowe's foam, printed nodes) makes for a short build and a fast crash repair.
- The pusher sizing is credible. At 4S × 900 KV ≈ 11,300 rpm, the 11x5.5 has a pitch speed of about 26 m/s, so 1.2 to 1.4 kgf static thrust (T/W ≈ 0.4) is enough for transition at 14 m/s. Still `UNVERIFIED` until it is on the thrust stand.
- The tail volumes (Vh 0.38, Vv 0.042) are within the normal ranges. Only the CG/NP relation (C4) is the problem.

## 4. Recommendation
Keep K01 as a strong candidate, but with three changes before freezing the BOM:
1. Add a full-span spar and clamp the booms to it.
2. Move the lift centroid to about 25 % MAC, or enlarge the tail, and confirm a static margin of at least 8 % in XFLR5.
3. Switch to the 4S 5000 pack and the SpeedyBee FC.

With the 5000 pack at the corrected mass (3.32 kg): T/W 1.90 table / 1.77 with sag, about 15 min cruise after 2 min hover. That is still three times the mission, for less mass and cost.

## 5. Numbers this reviewer believes (baseline 4S 6500, corrected)

| Item | Card | Corrected |
|---|---|---|
| MTOW | 3.22 kg | **3.45 kg** (3.3 to 3.7) |
| Hover power / current | 523 W / 35 A | **≈ 650 W / 44 A** |
| T/W (sag) | 1.96 (1.83) | **1.83 (1.70)** |
| Hover-only endurance | 8.8 min | **≈ 7 min** |
| Cruise after 2 min hover | 22 min | **15 to 20 min** (planning value 16) |
| Static margin | not stated | **0 to 3 %, which fails**; fix per C4 |
| Connector need | 82 A | **93 A** |
| Cost incl. tax and shipping | $1,741.68 | **≈ $1,897** (reserve ≈ $103) |
| Team-hours | 100 to 120 | **150 to 180** |
| Packed | 1 box 1.2 × 0.5 × 0.4 m | same, back seat or hatchback; box not costed |

Calculations: the scratchpad re-runs of sizing.py with dm = +0.23 kg and DOWNLOAD = 1.08, plus the pessimistic cruise case (η_prop 0.50, interference 1.35). The stress and NP formulas are shown in C3 and C4.
