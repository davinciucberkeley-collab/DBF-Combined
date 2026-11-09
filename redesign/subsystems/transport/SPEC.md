# Transport (TRN)

Status `PROPOSED` (D7, 2026-11-09). Designer D7, loads C1. Every part is a ground item (`flight: false`). Numbers
from `team/D7/transport_calc.py` (claims `CL-D7-*`, `team/D7/claims.json`) and `params.json` (`subsystems/transport/params.json` for `trn.*`).

## Purpose

Carry the one-piece aircraft (props off, pitot boom out, packs out) in a 1.25 × 0.55 × 0.54 m Coroplast box in a car,
by one or two people; survive a 0.3 m drop off a car sill; go from the closed box to the arm check in under 5 min.
There is no structural field joint; the only field connections are 4 props, the pitot boom and the pack plug.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Box external L × W × H | 1.25 × 0.55 × 0.54 | m | `trn.box.external_m` (A1 has 0.50 high: CR-D7-01) | `PROPOSED` |
| Height needed for the drop stroke | 0.535 | m | `CL-D7-BOX-H-REQ` | `UNVERIFIED` (foam data) |
| Wall stack: shell / floor / lid | 4 / 4 / 10 | mm | `trn.box.*` (4 mm Coroplast; lid + 6 mm PE lining) | `PROPOSED` |
| Aircraft envelope in the box | 1.15 × 0.47 × 0.425 | m | `params.json#transport.envelope_props_off_m` | `PROPOSED` |
| Free travel, lower tube ends to floor | 91 | mm | `CL-D7-TRAVEL` | `CHECKED` |
| Clearance left when the columns bottom (≥ 10 mm) | 14.8 | mm | `CL-D7-TUBE-CLEAR-DROP` | `UNVERIFIED` |
| Upper tube ends to lid lining | 10 | mm | `trn.box.top_gap_min_m` | `PROPOSED` |
| Pod nose / foot tips to side walls (≥ 10 mm) | 36 | mm | `CL-D7-SIDE-CLEAR` | `CHECKED` |
| Wingtip to end pad | 16 | mm | `CL-D7-TIP-PAD-GAP` | `CHECKED` |
| Cradle stations, saddle chord range | y ±0.20, x −0.015 … 0.235 | m | `trn.cradle.*`, `ASM-C1-CRADLE-Y` | `PROPOSED` |
| Crush column (PE 1.7 pcf), per cradle | 60 × 50 × 127 | mm | `trn.cradle.*` | `PROPOSED` |
| Usable stroke vs C1 need | 69.9 vs 68.6 | mm | `CL-D7-CRADLE-STROKE` vs `CL-C1-CRADLE-STROKE-REQ` | `UNVERIFIED` |
| 0.3 m drop load factor vs airframe allowable | 9.59 vs 9.74 | — | `CL-D7-DROP-N` vs `CL-C1-TRANSPORT-N-ALLOW` | `UNVERIFIED` (`T-D7-BOX-DROP`) |
| Static column stress (band 2–7 kPa) | 3.35 | kPa | `CL-D7-CRADLE-STRESS` | `UNVERIFIED` |
| Drop the 0.50 m box would allow | 0.18 (needs 0.30) | m | `CL-D7-A1-BOX-DROP-ALLOW` | `FAIL` → CR-D7-01 |
| Empty box (cradles, tray, pillars, straps, handles) | 3.63 | kg | `CL-D7-BOX-MASS` | `UNVERIFIED` (`EST`) |
| Loaded (aircraft at gate less one pack, 4 spare props, pouch) vs 6 kg | 5.90 | kg | `CL-D7-LOADED-MASS` | `UNVERIFIED` (+2 %) |
| Loaded if both packs went in (not allowed) | 7.00 | kg | `CL-D7-LOADED-WITH-PACKS` | — |
| Set-up, closed box to arm check | 4.4 (limit 5) | min | `CL-D7-SETUP-MIN` | `UNVERIFIED` (`T-D7-SETUP`) |

**Why 0.54 m and not 0.50 m.** In a floor drop the aircraft sinks into the cradle foam by the crush stroke, so the
lower tube ends (z −0.2125 m) need the same free travel above the floor (stroke at bottoming 76 mm + 10 mm). The foam
fits inside the 0.21 m below the wing, as D-22 says, but the travel under the tube ends does not: the 0.50 m box leaves
51 mm, enough for a 0.18 m drop only.

## Parts

| Id | Part | Mass g | Make/buy |
|---|---|---|---|
| `TRN-001` | Box base: floor, walls, end pads, corners | 2 317 | make (Coroplast) |
| `TRN-005` | Plug lid + 6 mm PE lining | 744 | make |
| `TRN-002-L/R` | Spar cradle: XPS saddle (S5010 lower surface, LE lip) on a PE crush column | 68 each | make |
| `TRN-004-L/R` | Lid hold-down pillar, PE, 5 mm preload over the spar | 37 each | make |
| `TRN-003` | Prop tray: 8 prop slots, pitot-boom pocket, pouch pocket | 149 | make (XPS) |
| `TRN-006-A/B` | Cam-buckle strap (closes the lid) | 45 each | buy |
| `TRN-007-C/L/R` | Side handle at the CG (one person), two end handles (two people) | 40 each | buy |
| `TRN-008` | Field pouch (spare nuts, tape, checklist card; wrench only if CR-D7-05 keeps a nut) | 150 | buy |

BOM-only lines `TRN-101…104` (LSE tape, M5 hardware, checklist card, ground mat) in `parts.csv`. Cost ≈ $117 `EST` (6 × M5 counted at $0.50 each).

## Interfaces

| Edge | To | How |
|---|---|---|
| `E-TRN-06/07` | `wing: WNG-001` lower surface at y ±0.20 | rests in the saddle, no fastening (`CT-CRADLE-CONTACT`); elevons, fins, tubes, feet never touched |
| `E-TRN-08/09` | `wing: WNG-001` upper surface over the spar at y ±0.20 | lid pillar, 5 mm preload (`CT-TRN-PRELOAD-PAD`); load goes straight into the cradle below |
| `E-TRN-01…05, 10…16` | internal | LSE tape + zip ties, plug lid, cam straps, M5 handle bolts (joint stack in `interfaces.json`) |
| packing only | props, pitot boom (`avionics`), packs (`power`) | props and boom in the tray, packs in the LiPo bag outside the box (`ASM-D7-PACK-OUT`) |

## Mass budget

Ground item: not counted in the 2 600 g flying mass. Against `params.json#mass.transport_box_kg` 3.0 kg `EST`: 3.63 kg
(+0.63, CR-D7-01). Against the 6 kg loaded limit: 5.90 kg. Levers: weigh the Coroplast (0.76 kg/m² is a packaged
weight), 3 mm Coroplast lid (≈ −0.2 kg `EST`), aircraft at A3's predicted mass (−0.1 kg).

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Box height 0.54 m and two measured cars (`CAR-FIT.md`) before anything freezes | D7, A1 |
| 2 | PE density from a coupon drop (`T-D7-CUSHION`): curve data for 1.7 vs 2.2 pcf at 3.4 kPa not checked | D7 |
| 3 | Side, end and corner drops are test-only; C1 per-axis allowables wanted (CR-D7-02) | C1 |
| 4 | Prop nut needs a wrench at 1.5 N·m: conflicts with "no tools" (CR-D7-05) | E1, A2 |
| 5 | Pitot boom: tube quick-disconnect and pocket size (CR-D7-06) | F3, D2 |
| 6 | Wing patches under and over the cradles kept free of servo covers and horns (CR-D7-04) | D1, D6 |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-D7-CUSHION` | two PE columns under a 2.05 kg dummy, 0.3 m drop, phone accelerometer; 1.7 and 2.2 pcf | stroke, column stress |
| `T-D7-BOX-DROP` | loaded box (dummy first), 0.3 m flat and bottom-edge drop, accelerometer on the spar, chalk on the lower motor caps | `CL-D7-DROP-N`, tube clearance |
| `T-D7-WEIGH-BOX` | luggage scale, empty and loaded | box and loaded mass |
| `T-D7-SETUP` | `CHECKLIST.md`, one person, timed by a second, three field days | `CL-D7-SETUP-MIN` |
| `R-CAR-FIT` | `CAR-FIT.md` filled for two cars | car fit |
| CAD | `python -I redesign/fusion/check.py`: transport 0 errors, 0 warnings once `WNG-001` is declared | interfaces, touch |
