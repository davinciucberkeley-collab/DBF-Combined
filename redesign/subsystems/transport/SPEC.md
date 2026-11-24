# Transport (TRN)

Status `PROPOSED`, D7 closure round 2026-11-14 (board box from 4 XLBX blanks, W 0.565 m for the D-165 foot, hand holes, cord lashings; `review/CLOSURE-ROUND-2026-11-14/D7.md`), round 5 (CDR fix round S4, D-134, 2026-11-13: box 0.56 m wide, separate panels, nest below), round 4 2026-11-10 (A4 CR-A4-46 and PLAN-STATUS, D-47 nose at −0.130; round 3: C1 CR-C1-22, A4 CR-A4-24, C5 CR-C5-06, I1 CR-I1-18). Designer D7, loads
C1. Every part is a ground item (`flight: false`). Numbers: `team/D7/transport_calc.py` (claims `CL-D7-*`) and
`subsystems/transport/params.json` (`trn.*`). Field joints: `FIELD-JOINTS.md`. Set-up card: `CHECKLIST.md`.

## Purpose

Get the one-piece aircraft to the field and flying in under 5 min. It rides in one 1.25 × 0.565 × 0.54 m corrugated
board box (closure 2026-11-14) with props off in the tray, the pitot boom off in its slot and the packs out. The box survives a 0.3 m floor drop
off a car sill. One person carries it by the side hand hole, or two people use the end hand holes. The field has no
structural joint. The only joints made there are 4 prop nuts (the 10 mm spanner is the only tool, D-40), the pitot
boom and the pack strap and plug.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Box external L × W × H | 1.25 × **0.565** × 0.54 | m | `trn.box.external_m` (closure 2026-11-14: W +5 mm for the D-165 foot; A1 to copy into `requirements.box_external_m`) | `PROPOSED` (two cars first, `CAR-FIT.md`) |
| Height needed for the floor-drop stroke | 0.538 | m | `CL-D7-BOX-H-REQ` | `UNVERIFIED` (foam data) |
| Floor drop: column stroke vs C1 need / load factor vs allowable | 66 vs 52 / 10.1 vs 12.4 | mm / — | `CL-D7-CRADLE-STROKE`, `CL-D7-DROP-N` | `UNVERIFIED` (`T-D7-BOX-DROP`) |
| Floor drop height the 0.54 m box allows (needs 0.30) | 0.39 | m | `CL-D7-A1-BOX-DROP-ALLOW` | `UNVERIFIED` |
| Lower tube ends to floor when the columns bottom (≥ 10) | 12 | mm | `CL-D7-TUBE-CLEAR-DROP` | `UNVERIFIED` |
| Aft gap (feet to wall) / pod nose (x −0.147, D-150) to 1/2 in nose pad (face x −0.1593) / antenna B tip at its −0.157 limit to pad / drawn antenna B end (−0.151) / pitot socket collar (−0.155) to pad | 12 / **12.30** (≥ 10) / **2.30** (≥ 2) / 8.30 (≥ 2) / **4.30** (≥ 2) | mm | `CL-D7-SIDE-CLEAR`, `CL-D7-NOSE-GAP`, `CL-D7-ANTENNA-PAD-GAP`, `-DRAWN`, `CL-D7-COLLAR-PAD-GAP` (D7-W3: the 3/4 in pad on the −0.147 nose gave 5.95 / −4.05 / 1.95 / −2.05 mm, `FAILS`) | `CHECKED` (geometry) |
| Wingtip to end pad / upper tube ends to lid | 15 / 10 | mm | `CL-D7-TIP-PAD-GAP`, `trn.box.top_gap_min_m` | `UNVERIFIED` |
| Off-axis drop allowed: aft wall (feet crush) / end / nose / lid-down | 0.25 / 0.087 / 0.059 / 0.057 | m | `CL-D7-AFT-`, `-END-`, `-NOSE-`, `-LID-DROP-ALLOW` | `UNVERIFIED` (label + test) |
| Aft-wall drop load factor (feet plateau) vs C1 x allowable | 7.5 vs 12.1 | — | `CL-D7-AFT-N` | `UNVERIFIED` |
| Pillar bearing, lid-down 102 N vs skinned XPS | 17 vs 80 | kPa | `CL-D7-PILLAR-P` | `UNVERIFIED` |
| Saddle contact vs C2 need / gap to the brace anchor | 15 000 vs 1 080 mm² / 4 mm | — | `CL-D7-CRADLE-PAD-AREA`, `CL-D7-BRACE-GAP` | `CHECKED` |
| Crush column (PE 1.7 pcf), per cradle; static stress (band 2–7) | 60 × 50 × 120 mm; 3.35 | mm; kPa | `trn.cradle.*`, `CL-D7-CRADLE-STRESS` | `UNVERIFIED` |
| Hand hole: load at 2 g (one hole) / edge line load vs ECT 32 / 2 | 114 / 0.45 vs 2.8 | N / kN/m | `CL-D7-HANDHOLE-F`, `-Q`, `-Q-ALLOW` | `UNVERIFIED` (ECT `EST`, `T-D7-HANDLE-PULL`) |
| Box lines T01 + T02 + T03 + T06 incl. tax: baseline / pessimistic vs $40 | 32.63 / 39.02 | USD | `CL-D7-BOX-COST-BASE`, `-PESS` (was $158.69) | `UNVERIFIED` (snippets 2026-11-14) |
| Least box height for the 0.3 m drop / shells + aircraft only | 0.525 / 0.446 | m | `CL-D7-H-MIN`, `CL-D7-H-FLOOR` | `CHECKED` (stack-up) |
| Saddle and pillar to the tape skin `WNG-003`: modelled gap / saddle preload / pillar preload | 0 / 0 / 5 | mm | `trn.cradle.saddle_preload_m`, `trn.holddown.preload_m` | `MODELLED` |
| Empty box / loaded box (aircraft less pack, spares, pouch) vs 6 kg | 3.60 / 5.86 | kg | `CL-D7-BOX-MASS`, `CL-D7-LOADED-MASS` | `UNVERIFIED` (`EST`, +3 %) |
| Battery can (2 packs) / landing mat / tote | 3.30 / 2.70 / 0.57 | kg | `CL-D7-CAN-MASS`, `-MAT-MASS`, `CALC-D7-CARRY` | `UNVERIFIED` (`EST`) |
| Carrier A (box + tote) / carrier B (can + mat) | 6.4 / 6.0 | kg | `CL-D7-CARRY-A`, `-B` | `UNVERIFIED` |
| Set-up, closed box to arm check (limit 5) | 4.75 | min | `CL-D7-SETUP-MIN` | `UNVERIFIED` (+5 %, `T-D7-SETUP`) |

**Drop policy (C1 CR-C1-22).** The floor drop is designed for 0.3 m. In an aft-wall drop the four feet crush along
their own axis, the same load path as a hard landing, at n 7.5, and they allow 0.25 m. The cartridges are replaced
afterwards from the spares. The end, nose and lid-down faces cannot get 54–57 mm of stroke unless the box grows by
about 0.2 m, and then no car takes it. These faces are label-and-test cases: "THIS SIDE UP", "KEEP FLAT: NEVER STAND
ON END". The aircraft sits 12 mm off the aft wall, and the slack goes to a 1/2 in PE nose pad (D-150, D7-W3: the pod nose moved to −0.147 and the
3/4 in pad left 5.95 mm with the pitot collar into the pad; round 4 had gone 1 in → 3/4 in for the −0.130 nose).
Free length inside the box along x: 552 − 515 = 37 mm = 12 aft gap + 12.7 pad + 12.3 nose gap (`CL-D7-BOX-X-FREE`).
**Fallback 0.50 m box** (if a car rejects 0.54): 56 mm columns, a 0.15 m floor-drop label.

## Panel nest (closure 2026-11-14: board box, I1 cost request)

The box is cut as **separate flat panels from 4 new Home Depot XLBX moving boxes** (24 × 20 × 21 in, $3.48 each,
search snippet 2026-11-14; ECT 32 `EST`, read from the Canadian listing of the same box). External box
**1.25 × 0.565 × 0.54 m** (W +5 mm for the D-165 taller foot), shell about 4 mm (single wall, `EST`). Each box is
slit at its glue flap and laid flat: a blank about 2.27 × 1.04 m (`EST` from the box size: 24 + 20 + 24 + 20 in plus
the glue flap, by 10 + 21 + 10 in). It has two 24 in columns 0.61 m wide that run the full 1.04 m height (flap +
body + flap, two fold scores), two 20 in columns, and one body row 0.533 m tall that runs the full length (three
vertical scores).

| Blank | Panel | Size mm | Placement | Left over |
|---|---|---|---|---|
| 1 | Front wall | 1 250 × 536 | body row (the 3 mm over 533 crosses the flap score) | body 1 020 × 533 |
| 1 | End wall L | 557 × 536 | rest of the body row | flaps: edge saddles, column collars, hand-hole patches |
| 2 | Aft wall + end wall R | as blank 1 | as blank 1 | flaps |
| 3 | Floor | 2 × (610 × 565) + 30 × 565 strip | the two 24 in columns, 565 along the height (crosses one fold score) | 2 × 610 × 475, the 20 in columns |
| 4 | Lid top | as the floor | as blank 3 | lid lips (30 mm strips, spliced), spare |

Rules: fold scores and splices run **along x** (across the 0.565 m short span), never along the span, so the floor
and lid still span front-to-back wall without a hinge. Splices: packing tape both faces, 50 mm overlap strip of offcut
underneath. Walls stand on the floor (536 = 540 − 4); end walls sit between the long walls (557 = 565 − 2 × 4). Lay
the panels out around the factory hand holes of the XLBX (position "—" until a box is in hand); a factory hole that
falls inside a panel gets a taped offcut patch. Corners and seams: packing tape inside and out (`T02`, one roll).
Hand holes: die-cut 100 × 30 mm, top 35 mm under the lid-lip bottom, side hole on the **aft** wall at y 0 and one on
each end wall at the chord centre; each gets a 2-layer offcut patch inside (3 layers at the edge,
`CL-D7-HANDHOLE-Q`). Closure: two paracord lashings from the G18 roll (slipped trucker's hitch) over folded offcut
edge saddles at y ±0.40. Moisture: board loses strength when wet; keep the box in the car, and rebuild it from four
new blanks if it gets soaked (about $15.35 incl. tax). **x-stops:** unchanged (saddle LE lips). **Cars:** the
longest side stays 1.25 m; the width is 0.565 m (`CAR-FIT.md`).

**PE foam (one Walmart 2-count, 16 × 12 × 2 in, 406 × 305 × 51 mm, `T06`).** Sheet A: a 4 × 5 grid of 100 × 60 mm
blocks: 10 for the two pillars (5 layers each, cut to length), 6 for the two columns (60 × 50, 3 layers, one layer
band-sawn to 18.6 mm: 120 mm). Sheet B: two end pads 200 × 150 sliced to 30 mm, the nose pad as two 160 × 100 pieces
sliced to 12.7 mm, two saddle caps 250 × 60 × 6 mm from the slicing offcut. Stacks are bound with a packing-tape wrap
(the tape buckles; it carries no axial load). Density "—" on the listing: `T-D7-CUSHION` on this foam sets the column
footprint (a cut size) so the static stress stays in the 2–7 kPa band.

## Parts

| Id | Part | Mass g | Make/buy |
|---|---|---|---|
| `TRN-001` | Box base: floor, walls, end pads, 1/2 in nose pad, edge saddles | 2 356 | make (board, 4 XLBX blanks) |
| `TRN-005` | Plug lid (no lining) | 650 | make (board) |
| `TRN-002-L/R` | Spar cradle: XPS saddle (S5010 lower surface, LE lip, 9 mm harness relief) on a 120 mm PE column | 70 each | make |
| `TRN-004-L/R` | Lid hold-down pillar, PE 100 × 60 mm, 5 mm preload over the spar | 38 each | make |
| `TRN-003` | Tray: 8 prop slots, pitot-boom slot with tip plug, pouch pocket | 149 | make (XPS) |
| `TRN-006-L/R` | Paracord lashing 2.6 m, slipped trucker's hitch (closes the lid; cord from I1 G18) | 20 each | make |
| `TRN-007-C/L/R` | Die-cut hand holes with a 2-layer board patch: side hole on the aft wall at y 0 (one person), one per end wall (two people) | 22 each | make |
| `TRN-008` | Field pouch: 10 mm prop spanner, spare M6 nuts, 2.5 mm key, tape, checklist card | 150 | buy |

BOM-only lines in `parts.csv`: `TRN-101` packing tape, `TRN-110` PE sheets, `TRN-103` card, `TRN-106` spanner, `TRN-104` landing
mat (0.8 × 0.8 m, rubber on ply, folding; C5 S1), `TRN-107` tote, `TRN-108` landing-spares box, `TRN-109` labels.
The battery can and LiPo bags are `GND-003/004` (E2). Box lines T01 + T02 + T03 + T06: $39.02 incl. tax pessimistic (`CL-D7-BOX-COST-PESS`).

## Interfaces

| Edge | To | How |
|---|---|---|
| `E-TRN-06/07` | `wing: WNG-001` lower surface at y ±0.20, `also_contacts` `WNG-003` | rests in the saddle (`CT-CRADLE-CONTACT`), contour cut to the outer skin face, preload 0 (`retention.preload_m`); elevons, fins, tubes, braces, feet never touched |
| `E-TRN-08/09` | `wing: WNG-001` upper surface over the spar at y ±0.20, `also_contacts` `WNG-003` | lid pillar, 5 mm preload (`CT-TRN-PRELOAD-PAD`, `retention.preload_m` 0.005) |
| `E-TRN-17…20` | `propulsion: PRP-003-UR/UL/LR/LL` | `stowed` in a tray slot (`CT-TRN-POCKET`) |
| `E-TRN-21` | `avionics: AVN-005` pitot boom | `stowed` in its slot, tip plug; F3 to acknowledge |
| `E-TRN-01…05, 10…16` | internal | packing-tape tabs and wraps, column collars, plug lid, cord lashings, hand-hole patches (`E-TRN-13…15`, no fasteners since closure 2026-11-14) | D7 |

## Mass budget

Ground item: not in the flying mass. Empty box 3.48 kg, loaded 5.81 kg against 6 kg (+3 %), `CL-D7-BOX-MASS`,
`CL-D7-LOADED-MASS`. The shell is still costed at the Coroplast 0.76 kg/m² as an upper bound; single-wall board
weight is "—" until a blank is weighed (`T-D7-WEIGH-BOX`).

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Two measured cars in `CAR-FIT.md` before the 0.54 m box freezes (CR-A1-42) | team lead, D7, A1 |
| 2 | PE density from a coupon drop (`T-D7-CUSHION`); the column window is 109–123 mm | D7 |
| 3 | End, nose and lid-down drops are label-and-test only (0.06–0.09 m); A2 to confirm `R-TRANSPORT` means the floor drop | A2, C1 |
| 4 | Closed round 4: saddle–skin overlap (CR-A4-46). Saddle cut to the outer skin face, preload 0, `also_contacts` `WNG-003` on `E-TRN-06…09`; `check.py` shows no transport warning | — |
| 5 | Antenna B (pod nose) must not protrude more than 10 mm ahead of the nose at x −0.130 (CR-D7-13); 2.95 mm left to the pad | D2, F3 |
| 7 | Read the ECT stamp on each XLBX blank (32 lb/in expected, `CL-D7-HANDHOLE-Q-ALLOW`); below 32 add a third patch layer | D7 |
| 6 | Props-on transport (CR-D7-15) would save 140 s and the tool; the geometry fits (17 mm, 5 mm saddle notch). A1's call | A1, E1 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-D7-CUSHION` | two 120 mm PE columns under a 2.05 kg dummy, 0.3 m drop, phone accelerometer; 1.7 and 2.2 pcf | stroke, column stress |
| `T-D7-BOX-DROP` | dummy with real feet, then the aircraft: 0.3 m floor and bottom-edge drops; dummy only at the off-axis heights; chalk on caps, feet, nose, tips | `CL-D7-DROP-N`, clearances, off-axis claims, pillar bearing |
| `T-D7-HANDLE-PULL` | loaded box hung from each hand hole for 1 min, 3 jerks | hole edge: no crease, tear or crushed flutes |
| `T-D7-WEIGH-BOX` | luggage scale: box empty and loaded, can, mat, tote | masses, carry split |
| `T-D7-SETUP` | `CHECKLIST.md`, one person, timed by a second, three field days | `CL-D7-SETUP-MIN` |
| `R-CAR-FIT` | `CAR-FIT.md` filled for two cars | car fit |
| CAD | `python -I redesign/fusion/check.py`: transport module ok, 0 transport errors, 0 transport warnings (round 4; `E-TRN-21` acknowledged) | interfaces, touch, box overlap |
