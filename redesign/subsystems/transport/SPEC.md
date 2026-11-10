# Transport (TRN)

Status `PROPOSED` (D7, 2026-11-09, round 2 for CR-A1-35 / D-31). Designer D7, loads C1. Every part is a ground item
(`flight: false`). Numbers from `team/D7/transport_calc.py` (claims `CL-D7-*`, `team/D7/claims.json`) and
`params.json` (`subsystems/transport/params.json` for `trn.*`).

## Purpose

Carry the one-piece aircraft (props off in the tray, pitot boom off in its slot, packs out in the LiPo bag) in a
1.25 × 0.55 × 0.54 m Coroplast box in a car, by one person (side handle) or two (end handles); survive a 0.3 m drop off
a car sill; go from the closed box to the arm check in under 5 min with one tool, the 10 mm prop spanner (D-40). No
structural field joint: the field connections are 4 prop nuts, the pitot boom and the pack plug.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Box external L × W × H | 1.25 × 0.55 × 0.54 | m | `requirements.box_external_m` (D-31) = `trn.box.external_m` | `PROPOSED` (two cars first, `CAR-FIT.md`) |
| Height needed for the drop stroke | 0.538 | m | `CL-D7-BOX-H-REQ` | `UNVERIFIED` (foam data) |
| Wall stack: shell / floor / lid | 4 / 4 / 4 | mm | `trn.box.*` (4 mm Coroplast; lid lining dropped in round 2) | `PROPOSED` |
| Aircraft envelope in the box | 1.15 × 0.483 × 0.438 | m | `transport.envelope_props_off_m` | `PROPOSED` |
| Free travel, lower feet / tube ends to floor | 84 | mm | `CL-D7-TRAVEL` | `UNVERIFIED` (envelope `PROPOSED`) |
| Clearance left when the columns bottom (≥ 10 mm) | 12 | mm | `CL-D7-TUBE-CLEAR-DROP` | `UNVERIFIED` |
| Upper tube ends / feet to the bare lid | 10 | mm | `trn.box.top_gap_min_m`, `ASM-D7-REBOUND` | `UNVERIFIED` |
| Pod nose / foot tips to side walls (≥ 10 mm) | 29.5 | mm | `CL-D7-SIDE-CLEAR` | `UNVERIFIED` |
| Wingtip to end pad | 16 | mm | `CL-D7-TIP-PAD-GAP` | `UNVERIFIED` |
| Cradle saddle: y, x range | ±(0.17 … 0.23), −0.015 … 0.235 | m | `trn.cradle.*` | `PROPOSED` |
| Saddle contact vs C2 need (≥ 40 × 40 mm) | 15 000 vs 1 080 | mm² | `CL-D7-CRADLE-PAD-AREA` vs `CL-C2-CRADLE-AREA` | `CHECKED` |
| Saddle / pillar edge to brace anchor (y 0.234) | 4 (≥ 2) | mm | `CL-D7-BRACE-GAP` | `CHECKED` |
| Crush column (PE 1.7 pcf), per cradle | 60 × 50 × 120 | mm | `trn.cradle.crush_t_m` (127 → 120) | `PROPOSED` |
| Usable stroke vs C1 need | 66.0 vs 60.0 | mm | `CL-D7-CRADLE-STROKE` vs `CL-C1-CRADLE-STROKE-REQ` | `UNVERIFIED` |
| 0.3 m drop load factor vs airframe allowable | 10.1 vs 11.0 | — | `CL-D7-DROP-N` vs `CL-C1-TRANSPORT-N-ALLOW` | `UNVERIFIED` (`T-D7-BOX-DROP`) |
| Drop height the 0.54 m box allows (needs 0.30) | 0.34 | m | `CL-D7-A1-BOX-DROP-ALLOW` | `UNVERIFIED` (+13 %) |
| Static column stress (band 2–7 kPa) | 3.35 | kPa | `CL-D7-CRADLE-STRESS` | `UNVERIFIED` |
| Handle: load per M3 bolt at 2 g / wall bearing | 57 / 27 | N / kPa | `CL-D7-HANDLE-BOLT-F`, `CL-D7-HANDLE-BEARING` | `UNVERIFIED` (`T-D7-HANDLE-PULL`) |
| Empty box (cradles, tray, pillars, straps, handles) | 3.55 | kg | `CL-D7-BOX-MASS` | `UNVERIFIED` (`EST`) |
| Loaded (aircraft at gate less pack, 4 spare props, pouch) vs 6 kg | 5.82 | kg | `CL-D7-LOADED-MASS` | `UNVERIFIED` (+3 %) |
| Loaded if both packs went in (not allowed) | 6.92 | kg | `CL-D7-LOADED-WITH-PACKS` | — |
| Set-up, closed box to arm check | 4.4 (limit 5) | min | `CL-D7-SETUP-MIN` | `UNVERIFIED` (`T-D7-SETUP`) |

**Drop stack in the 0.54 m box.** The envelope grew to 0.438 m (D-31, feet at z ±0.219). That left 78 mm of travel,
and the 127 mm column bottomed 2 mm off the floor. Round 2 removes the 6 mm lid lining, because the pillars stop the
rebound (`ASM-D7-REBOUND`), and cuts the column to 120 mm. The column has to fall in a 109–123 mm window: thick enough
for n ≤ 11.0, thin enough to bottom 10 mm clear of the floor. 120 mm also passes at C1's previous allowable, 10.34.
**Fallback 0.50 m box:** 44 mm of travel and a 56 mm column allow a 0.15–0.16 m drop, depending on which C1 allowable applies. The box then carries the "MAX DROP 0.15 m" label.

## Parts

| Id | Part | Mass g | Make/buy |
|---|---|---|---|
| `TRN-001` | Box base: floor, walls, end pads, corners | 2 317 | make (Coroplast) |
| `TRN-005` | Plug lid (no lining) | 635 | make |
| `TRN-002-L/R` | Spar cradle: XPS saddle (S5010 lower surface, LE lip) on a 120 mm PE crush column | 70 each | make |
| `TRN-004-L/R` | Lid hold-down pillar, PE 100 × 60 mm, 5 mm preload over the spar | 38 each | make |
| `TRN-003` | Tray: 8 prop slots, pitot-boom slot with tip plug, pouch pocket | 149 | make (XPS) |
| `TRN-006-A/B` | Cam-buckle strap (closes the lid) | 45 each | buy |
| `TRN-007-C/L/R` | Side handle at the CG (one person), two end handles (two people); M3 + backing strip | 40 each | buy |
| `TRN-008` | Field pouch: 10 mm prop spanner, spare M6 nuts, 2.5 mm key, tape, checklist card | 150 | buy |

BOM-only lines `TRN-101…106` in `parts.csv` (LSE tape, M3 handle hardware, backing strips, checklist card, ground
mat, spanner). Cost about $119 `EST`.

## Interfaces

| Edge | To | How |
|---|---|---|
| `E-TRN-06/07` | `wing: WNG-001` lower surface at y ±0.20 | rests in the saddle, no fastening (`CT-CRADLE-CONTACT`); elevons, fins, tubes, braces, feet never touched |
| `E-TRN-08/09` | `wing: WNG-001` upper surface over the spar at y ±0.20 | lid pillar, 5 mm preload (`CT-TRN-PRELOAD-PAD`); load goes straight into the cradle below |
| `E-TRN-01…05, 10…16` | internal | LSE tape + zip ties, plug lid, cam straps, M3 handle bolts (`CT-TRN-M3-BOLT`, joint stack in `interfaces.json`) |
| planned, `stowed` | props `PRP-003-*` (E1), pitot boom `AVN-005` (F3) → `TRN-003` | declared once those parts exist (CR-D7-09). Packs ride in the LiPo bag outside the box (`ASM-D7-PACK-OUT`) |

## Mass budget

Ground item, not in the 2 600 g flying mass. Against `mass.transport_box_kg` 3.63 kg: 3.55 kg (−0.08, CR-D7-08).
Against the 6 kg loaded limit: 5.82 kg. Levers: weigh the Coroplast (0.76 kg/m² is a packaged weight), 3 mm Coroplast
lid (about −0.15 kg `EST`).

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Two measured cars in `CAR-FIT.md` before the 0.54 m box freezes. The team lead names the cars (CR-A1-42) | team lead, D7, A1 |
| 2 | PE density from a coupon drop (`T-D7-CUSHION`); the 109–123 mm column window is narrow | D7 |
| 3 | Rebound into the pillars without a lid lining (`ASM-D7-REBOUND`) is an estimate; `T-D7-BOX-DROP` checks it | D7 |
| 4 | Side, end and corner drops are test-only; C1 per-axis allowables (CR-D7-02) | C1 |
| 5 | `WNG-001` not declared yet: `E-TRN-06…09` dangle in `check.py` (the only transport errors) | D1 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-D7-CUSHION` | two 120 mm PE columns under a 2.05 kg dummy, 0.3 m drop, phone accelerometer; 1.7 and 2.2 pcf | stroke, column stress |
| `T-D7-BOX-DROP` | loaded box (dummy first), 0.3 m flat and bottom-edge drop, accelerometer on the spar, chalk on all motor caps and feet | `CL-D7-DROP-N`, clearances, rebound |
| `T-D7-HANDLE-PULL` | loaded box hung from each handle for 1 min, 3 jerks | handle bolts, wall bearing |
| `T-D7-WEIGH-BOX` | luggage scale, empty and loaded | box and loaded mass |
| `T-D7-SETUP` | `CHECKLIST.md`, one person, timed by a second, three field days | `CL-D7-SETUP-MIN` |
| `R-CAR-FIT` | `CAR-FIT.md` filled for two cars | car fit |
| CAD | `python -I redesign/fusion/check.py`: transport module ok; 4 errors, all `WNG-001` dangling | interfaces, touch |
