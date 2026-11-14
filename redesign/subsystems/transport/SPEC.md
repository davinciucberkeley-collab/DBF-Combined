# Transport (TRN)

Status `PROPOSED`, D7 round 5 (CDR fix round S4, D-134, 2026-11-13: box 0.56 m wide, separate panels, nest below), round 4 2026-11-10 (A4 CR-A4-46 and PLAN-STATUS, D-47 nose at −0.130; round 3: C1 CR-C1-22, A4 CR-A4-24, C5 CR-C5-06, I1 CR-I1-18). Designer D7, loads
C1. Every part is a ground item (`flight: false`). Numbers: `team/D7/transport_calc.py` (claims `CL-D7-*`) and
`subsystems/transport/params.json` (`trn.*`). Field joints: `FIELD-JOINTS.md`. Set-up card: `CHECKLIST.md`.

## Purpose

Get the one-piece aircraft to the field and flying in under 5 min. It rides in one 1.25 × 0.56 × 0.54 m Coroplast
box with props off in the tray, the pitot boom off in its slot and the packs out. The box survives a 0.3 m floor drop
off a car sill. One person carries it by the side handle, or two people use the end handles. The field has no
structural joint. The only joints made there are 4 prop nuts (the 10 mm spanner is the only tool, D-40), the pitot
boom and the pack strap and plug.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Box external L × W × H | 1.25 × **0.56** × 0.54 | m | `requirements.box_external_m` (D-31; W +10 mm D-134) | `PROPOSED` (two cars first, `CAR-FIT.md`) |
| Height needed for the floor-drop stroke | 0.538 | m | `CL-D7-BOX-H-REQ` | `UNVERIFIED` (foam data) |
| Floor drop: column stroke vs C1 need / load factor vs allowable | 66 vs 52 / 10.1 vs 12.4 | mm / — | `CL-D7-CRADLE-STROKE`, `CL-D7-DROP-N` | `UNVERIFIED` (`T-D7-BOX-DROP`) |
| Floor drop height the 0.54 m box allows (needs 0.30) | 0.39 | m | `CL-D7-A1-BOX-DROP-ALLOW` | `UNVERIFIED` |
| Lower tube ends to floor when the columns bottom (≥ 10) | 12 | mm | `CL-D7-TUBE-CLEAR-DROP` | `UNVERIFIED` |
| Aft gap (feet to wall) / pod nose (x −0.130) to 3/4 in nose pad / antenna B tip to pad | 12 / **12.95** (≥ 10) / **2.95** (≥ 2) | mm | `CL-D7-SIDE-CLEAR`, `CL-D7-NOSE-GAP`, `CL-D7-ANTENNA-PAD-GAP` (D-134; were 2.95 / −7.05 mm, `FAILS`) | `CHECKED` (geometry) |
| Wingtip to end pad / upper tube ends to lid | 15 / 10 | mm | `CL-D7-TIP-PAD-GAP`, `trn.box.top_gap_min_m` | `UNVERIFIED` |
| Off-axis drop allowed: aft wall (feet crush) / end / nose / lid-down | 0.25 / 0.087 / 0.059 / 0.057 | m | `CL-D7-AFT-`, `-END-`, `-NOSE-`, `-LID-DROP-ALLOW` | `UNVERIFIED` (label + test) |
| Aft-wall drop load factor (feet plateau) vs C1 x allowable | 7.5 vs 12.1 | — | `CL-D7-AFT-N` | `UNVERIFIED` |
| Pillar bearing, lid-down 102 N vs skinned XPS | 17 vs 80 | kPa | `CL-D7-PILLAR-P` | `UNVERIFIED` |
| Saddle contact vs C2 need / gap to the brace anchor | 15 000 vs 1 080 mm² / 4 mm | — | `CL-D7-CRADLE-PAD-AREA`, `CL-D7-BRACE-GAP` | `CHECKED` |
| Crush column (PE 1.7 pcf), per cradle; static stress (band 2–7) | 60 × 50 × 120 mm; 3.35 | mm; kPa | `trn.cradle.*`, `CL-D7-CRADLE-STRESS` | `UNVERIFIED` |
| Handle: load per M3 bolt at 2 g / wall bearing | 57 / 27 | N / kPa | `CL-D7-HANDLE-BOLT-F`, `-BEARING` | `UNVERIFIED` |
| Handle M3 × 16: grip / thread past the nyloc vs D-41 minimum (nyloc 4.0 + 2 × 0.5) / thickest strap tab | 10.5 / 5.5 vs 5.0 / 3.0 | mm | `CL-D7-HANDLE-ENGAGE`, `-ENGAGE-MIN`, `-STRAP-T-MAX` | `CHECKED` (strap tab `EST` 2.5) |
| Saddle and pillar to the tape skin `WNG-003`: modelled gap / saddle preload / pillar preload | 0 / 0 / 5 | mm | `trn.cradle.saddle_preload_m`, `trn.holddown.preload_m` | `MODELLED` |
| Empty box / loaded box (aircraft less pack, spares, pouch) vs 6 kg | 3.60 / 5.86 | kg | `CL-D7-BOX-MASS`, `CL-D7-LOADED-MASS` | `UNVERIFIED` (`EST`, +3 %) |
| Battery can (2 packs) / landing mat / tote | 3.30 / 2.70 / 0.57 | kg | `CL-D7-CAN-MASS`, `-MAT-MASS`, `CALC-D7-CARRY` | `UNVERIFIED` (`EST`) |
| Carrier A (box + tote) / carrier B (can + mat) | 6.4 / 6.0 | kg | `CL-D7-CARRY-A`, `-B` | `UNVERIFIED` |
| Set-up, closed box to arm check (limit 5) | 4.75 | min | `CL-D7-SETUP-MIN` | `UNVERIFIED` (+5 %, `T-D7-SETUP`) |

**Drop policy (C1 CR-C1-22).** The floor drop is designed for 0.3 m. In an aft-wall drop the four feet crush along
their own axis, the same load path as a hard landing, at n 7.5, and they allow 0.25 m. The cartridges are replaced
afterwards from the spares. The end, nose and lid-down faces cannot get 54–57 mm of stroke unless the box grows by
about 0.2 m, and then no car takes it. These faces are label-and-test cases: "THIS SIDE UP", "KEEP FLAT: NEVER STAND
ON END". The aircraft sits 12 mm off the aft wall, and the slack goes to a 3/4 in PE nose pad (round 4: the pod nose
moved to −0.130 under D-47, and the 1 in pad left only 6.6 mm).
**Fallback 0.50 m box** (if a car rejects 0.54): 56 mm columns, a 0.15 m floor-drop label.

## Panel nest (D-134, CDR-24)

The box is cut as **separate flat panels** (no cross-shaped blank: the old one-piece base blank was 1 614 mm wide
against a 1 219 mm sheet, `review/MANUFACTURING.md` MF-16). Sheet: Coroplast 4 mm, 48 × 96 in = 1 219 × 2 438 mm,
the standard size Home Depot sells (CP4896S single sheet, WC4896-10 ten-pack; the other sizes listed are 36 × 72 in
and 24 × 36 in; homedepot.com product pages, search 2026-11-13). Panels from the 1.25 × 0.56 × 0.54 m external
box, 4 mm shell; walls stand on the floor (536 = 540 − 4), end walls sit between the long walls (552 = 560 − 2 × 4).
Every 1 250 mm side runs along the 2 438 mm sheet length, because 1 250 > 1 219.

| Sheet | Panel | Size mm | Qty | Placement | Left over |
|---|---|---|---|---|---|
| 1 | Floor | 1 250 × 560 | 1 | across: 560 + 560 = 1 120 ≤ 1 219, along 1 250 | strip 99 × 1 250: two lid long lips 1 242 × 30 |
| 1 | Lid top | 1 250 × 560 | 1 | beside the floor | — |
| 1 | End walls | 552 × 536 | 2 | block 1 188 × 1 219 left after 1 250 of length: 552 + 552 = 1 104 ≤ 1 188, 536 ≤ 1 219 | 1 188 × 683: lid short lips 544 × 30 × 2, end pads, corner angles, handle-strip templates |
| 2 | Front and aft walls | 1 250 × 536 | 2 | across: 536 + 536 = 1 072 ≤ 1 219, along 1 250 | 1 188 × 1 219 spare (a whole second lid or repair panels) |

Two sheets are enough, so no third sheet is bought (`T01`, $37.98 a sheet, LINKS-CHECK snippet 2026-11-11). Flutes:
run them vertically in the walls and across the floor (stiffer across the cradle span). Corners: LSE tape + hot-melt +
the 8 corner protectors (`TRN-001` notes; `T02`). **x-stops:** the aircraft is loaded against the 15 mm LE lip of each
cradle saddle (`trn.cradle.saddle_x_m` starts at −0.015), which fixes its x position; the nose-pad stack above is
computed from that position. **Cars:** the longest side is unchanged at 1.25 m, so the `CAR-FIT.md` check against
1.28 m is unchanged; it stays a HUMAN item (two cars measured by 15 Dec, before any panel is cut).

## Parts

| Id | Part | Mass g | Make/buy |
|---|---|---|---|
| `TRN-001` | Box base: floor, walls, end pads, 3/4 in nose pad, corners | 2 334 | make (Coroplast) |
| `TRN-005` | Plug lid (no lining) | 635 | make |
| `TRN-002-L/R` | Spar cradle: XPS saddle (S5010 lower surface, LE lip, 9 mm harness relief) on a 120 mm PE column | 70 each | make |
| `TRN-004-L/R` | Lid hold-down pillar, PE 100 × 60 mm, 5 mm preload over the spar | 38 each | make |
| `TRN-003` | Tray: 8 prop slots, pitot-boom slot with tip plug, pouch pocket | 149 | make (XPS) |
| `TRN-006-L/R` | Cam-buckle strap (closes the lid; was `-A/B`) | 45 each | buy |
| `TRN-007-C/L/R` | Side handle at the CG (one person), two end handles (two people); M3 + backing strip | 40 each | buy |
| `TRN-008` | Field pouch: 10 mm prop spanner, spare M6 nuts, 2.5 mm key, tape, checklist card | 150 | buy |

BOM-only lines in `parts.csv`: `TRN-101…106` (tape, M3 hardware, backing strips, card, spanner), `TRN-104` landing
mat (0.8 × 0.8 m, rubber on ply, folding; C5 S1), `TRN-107` tote, `TRN-108` landing-spares box, `TRN-109` labels.
The battery can and LiPo bags are `GND-003/004` (E2). Cost about $150 `EST`.

## Interfaces

| Edge | To | How |
|---|---|---|
| `E-TRN-06/07` | `wing: WNG-001` lower surface at y ±0.20, `also_contacts` `WNG-003` | rests in the saddle (`CT-CRADLE-CONTACT`), contour cut to the outer skin face, preload 0 (`retention.preload_m`); elevons, fins, tubes, braces, feet never touched |
| `E-TRN-08/09` | `wing: WNG-001` upper surface over the spar at y ±0.20, `also_contacts` `WNG-003` | lid pillar, 5 mm preload (`CT-TRN-PRELOAD-PAD`, `retention.preload_m` 0.005) |
| `E-TRN-17…20` | `propulsion: PRP-003-UR/UL/LR/LL` | `stowed` in a tray slot (`CT-TRN-POCKET`) |
| `E-TRN-21` | `avionics: AVN-005` pitot boom | `stowed` in its slot, tip plug; F3 to acknowledge |
| `E-TRN-01…05, 10…16` | internal | LSE tape + zip ties, plug lid, cam straps, M3 handle bolts (`E-TRN-13…15`: C6 `ground_joint` + `joint_stack` copied, engagement 5.5 ≥ 5.0 mm); every non-bolted edge has a `retention` block |

## Mass budget

Ground item: not in the 2 600 g flying mass. Against `mass.transport_box_kg` 3.55 kg: 3.57 kg (+0.02 kg for the
nose pad, CR-D7-12). Against the 6 kg loaded limit: 5.84 kg (+3 %). Levers: weigh the Coroplast (0.76 kg/m² is a
packaged weight), a 3 mm Coroplast lid (about −0.15 kg `EST`).

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Two measured cars in `CAR-FIT.md` before the 0.54 m box freezes (CR-A1-42) | team lead, D7, A1 |
| 2 | PE density from a coupon drop (`T-D7-CUSHION`); the column window is 109–123 mm | D7 |
| 3 | End, nose and lid-down drops are label-and-test only (0.06–0.09 m); A2 to confirm `R-TRANSPORT` means the floor drop | A2, C1 |
| 4 | Closed round 4: saddle–skin overlap (CR-A4-46). Saddle cut to the outer skin face, preload 0, `also_contacts` `WNG-003` on `E-TRN-06…09`; `check.py` shows no transport warning | — |
| 5 | Antenna B (pod nose) must not protrude more than 10 mm ahead of the nose at x −0.130 (CR-D7-13); 2.95 mm left to the pad | D2, F3 |
| 7 | Caliper the bought handle tab: > 3.0 mm needs M3 × 20 (`CL-D7-HANDLE-STRAP-T-MAX`) | D7 |
| 6 | Props-on transport (CR-D7-15) would save 140 s and the tool; the geometry fits (17 mm, 5 mm saddle notch). A1's call | A1, E1 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-D7-CUSHION` | two 120 mm PE columns under a 2.05 kg dummy, 0.3 m drop, phone accelerometer; 1.7 and 2.2 pcf | stroke, column stress |
| `T-D7-BOX-DROP` | dummy with real feet, then the aircraft: 0.3 m floor and bottom-edge drops; dummy only at the off-axis heights; chalk on caps, feet, nose, tips | `CL-D7-DROP-N`, clearances, off-axis claims, pillar bearing |
| `T-D7-HANDLE-PULL` | loaded box hung from each handle for 1 min, 3 jerks | handle bolts, wall bearing |
| `T-D7-WEIGH-BOX` | luggage scale: box empty and loaded, can, mat, tote | masses, carry split |
| `T-D7-SETUP` | `CHECKLIST.md`, one person, timed by a second, three field days | `CL-D7-SETUP-MIN` |
| `R-CAR-FIT` | `CAR-FIT.md` filled for two cars | car fit |
| CAD | `python -I redesign/fusion/check.py`: transport module ok, 0 transport errors, 0 transport warnings (round 4; `E-TRN-21` acknowledged) | interfaces, touch, box overlap |
