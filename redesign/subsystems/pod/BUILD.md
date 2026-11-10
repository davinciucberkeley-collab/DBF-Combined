# Pod — build notes for G4

Status: `PROPOSED` (D2, revision D2-R3 on params A1-R3, 2026-11-09). Dimensions from `subsystems/pod/params.json`
and `fusion/pod.py`; print the parts from the Fusion bodies (BuildAll → export STL per component). About 7 h
hands-on + 2 × 24 h cures. All x from the wing LE, z from the chord line, y + to the right, mm unless stated.

## Before you start

| Item | Detail |
|---|---|
| Materials | 3/16 in foam board (one 20 × 30 in sheet); XPS F-250 offcut from the core sheet (nose block, 2 crush blocks); PETG ~80 g; 30 min laminating epoxy + microballoons; 2 × 20 × 300 mm rubber-backed battery straps; 2.5 mm EVA sheet with anti-slip face; 2 × 7.6 × 300 mm nylon ties (50 lb); hook-and-loop 40 mm; 4 × M3 × 5.7 brass heat-set inserts (PDB); 1 × M3x16 **brass** SHCS + brass nut + nylon washer, Loctite 222; light-coloured tape; 2 × 4 mm nylon ties (airspeed); label |
| Tools | steel rule, snap knife, hot wire with the core templates, sanding block 120 grit, soldering iron with insert tip, 2.5 mm hex key, 5.5 mm spanner, 0.1 g scale, calipers, feeler gauge, masking tape |
| Needs first | D1's core with the pod recess cut (x 22.6 … 65, z 15, y ±70); tape skin left off over x 0 … 95, y ±70; spar slot **filled flush over the spar at \|y\| < 29** and **left open at y ±29 … 53** (feet); one tie laid under the spar at **y ±36** before the spar bond (CR-D2-04 rev. R3) |
| Stop | no CA on XPS or foam board (melts it); no steel screws, nuts or washers within 50 mm of the GPS; epoxy fumes: ventilate, gloves |

## Steps

| # | Action | Tools · cure | Check after |
|---|---|---|---|
| 1 | Print, PETG, 0.2 mm layers: tray (bay floor + forward stop + guides) in one piece, FC plate, avionics plate, PDB plate (all ≤ 1 mm, 100 %); handle lying flat (feet, bridge, aft stop, gussets, legs, grip, mast socket: 3 perimeters + 25 %; aft stop and bridge 100 %); spreader 100 %; spacers 2 / 4 / 8 / 8; pitot socket with flange; mast with the 45° pad (arrow toward the pad's low edge = nose); hatch tongue, latch tab, nose lip, 2 antenna tubes | printer | weigh each against `parts.csv` (`T-D2-WEIGH`); ±15 % else re-slice |
| 2 | Heat-set 4 M3 inserts in the PDB bosses, flush; counterbore the mast socket boss Ø6.5 × 4.5 on +y | iron 230 °C, drill | M3 runs in by hand; boss grip 9.5 mm |
| 3 | Cut board: floor 175.2 × 130.4; 2 side walls 210 long (flat bottom x −115 … 65, then the wing upper surface to x 95; top z 80.2); nose wall 130.4 × 70 with a 12 × 12 hole at y −46, z 45, a 30 × 15 vent at the top centre (z 65.2 … 80.2) and a 6.4 hole at y −46, z 24.5; aft wall 130.4 × 62.2 with two 11 × 16 exits at y ±53 … 64, z 27 … 43 and a 30 × 15 vent top centre; aft deck 24.2 × 130.4 with two 7.8 square slots at x 80, y ±48; hatch 170.2 × 140 with a 6.4 hole at x −54, y −46 | rule, knife | dry-fit the box on the core; no rock |
| 4 | Hot-wire: LE filler (x 0 … 22.6, under the floor, full width); nose block 7.0 × 130.4 × 60.4 with the 33 × 33 flange cut-out, vent notch and antenna hole; crush block per pack (below) | hot wire | block faces square; 0.1 g weigh |
| 5 | Cut a 1 mm deep, 22 mm wide strap groove across the floor under each strap-slot pair (x −36, +33.5) | knife | strap slides under the tray |
| 6 | Bond tray, FC, avionics and PDB plates to the floor, **full area** (sand PETG 120 grit, scuff the paper). Weight on top | epoxy · 24 h | 52 mm between guides at both ends; forward stop aft face at x −100.2 |
| 7 | Bond nose wall, side walls, aft wall and nose lip to the floor; fillet floor-to-side-wall over x −100 … 0. Pitot socket through the nose hole, flange epoxied to the wall inside face (clamp); nose antenna tube through its hole | epoxy · 4 h tack | socket bore points at (−195, −46, 45): sight a 6 mm rod |
| 8 | Bond the nose block behind the nose wall: to the nose wall, both side walls and the floor | thickened epoxy · 4 h | flush to the forward stop fore face (x −103.2), vent notch clear |
| 9 | Scuff the spar top at both foot stations and the slot fill over \|y\| < 29 (120 grit, IPA). Bond the handle: saddles on the spar, bridge on the slot fill; cinch the tie at y ±36 round each saddle | thickened epoxy · 24 h | aft stop face at x 77.0 ± 0.5, vertical; legs at x 80, y ±48 |
| 10 | Bond the box into the recess (floor, filler, wall bottoms) with thickened epoxy; slide the aft deck over the legs and bond it to the walls and legs | epoxy · 24 h before any load | no gap under the floor; deck flush |
| 11 | Tape the wing skin over the pod foot by 15 mm all round; light-coloured tape over the pod top; label on the grip | tape | label readable both sides |
| 12 | Hatch: tongue under the front, 12 × 40 hook tab at the aft edge, loop on the deck; antenna tube A bonded in its hole | epoxy · 1 h | closes flush, opens with one finger |
| 13 | Mast into the grip socket; M3x16 brass SHCS from +y, nylon washer, brass nut + Loctite 222, snug ≤ 0.3 N·m | hex key, spanner | ≥ 2 threads past the nut; pad faces forward-up |
| 14 | Straps through the slots, hook-and-loop overlap ≥ 50 mm, mark the overlap line; EVA pads on the tray centred on the slots | — | strap slides under the tray |
| 15 | Per pack (weighed): spacer = 77 − aft face (nominal 8, 680 g 4); crush block length = (aft face − 140 − 1.5) + 100.2 (nominal 27.7, 680 g 31.7), section 51.4 × 58.9 (sliding fit between the guides, 0.5 under the hatch) with a 30 × 8 top groove; spreader 1.5 mm on the pack fore face; label block and spacer with the pack id | hot wire, rule | block ≥ 24.9 mm (C5) |
| 16 | Proof tests: `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL` (12 kg on the grip, 10 s) | spring scale, weights | no slip, no lift, no pack play; feeler ≥ 0.5 mm under the pack over the slot |

## Field use (pre-flight card)

| # | Action |
|---|---|
| 1 | Hatch open (pull the tab up, slide the hatch aft) |
| 2 | This pack's spacer against the aft stop (label on the pack) |
| 3 | Pack in, leads aft, lowered with the aft face at the hatch edge, then slid back under the deck onto the spacer; spreader and crush block in front, against the forward stop |
| 4 | Straps cinched, overlap past the mark; leads over the stop, left inboard of the leg, AS150U into the park; plug last, after the RC link is up |
| 5 | Hatch on (tongue under the nose lip, press the tab); pitot boom home, keyed flat up |
| 6 | Lift only by the grip |

## Parts

| Id | Part | Make | Mass g |
|---|---|---|---|
| `POD-001` | Shell: board floor, walls, nose, aft wall, deck; XPS filler and nose block; nose lip; antenna tube B | knife, hot wire, FDM | 23.4 |
| `POD-002` | Tray (floor + forward stop + guides); FC, avionics, PDB plates; 4 inserts | FDM ×4 | 30.0 |
| `POD-003` | Hatch, tongue, latch tab, antenna tube A | knife, FDM | 8.5 |
| `POD-004` | 2 straps + 2 EVA pads | buy | 9.1 |
| `POD-005` | GPS mast with 45° pad, brass bolt | FDM | 6.6 |
| `POD-006` | Pitot socket with flange | FDM | 5.8 |
| `POD-007` | Handle: saddles, bridge + aft stop + gussets, legs, grip, mast socket; 2 ties; label | FDM | 34.8 |
| `POD-008` | Trim kit (nominal): crush block, spreader, 8 mm spacer | hot wire, FDM | 9.1 |
| | **Total** (allocation 122, CR-D2-09 asks 128) | | **127.3** `EST` |

## How to verify

| Check | Command or test |
|---|---|
| CAD, masses, interfaces | `python -I redesign/team/D2/pod_data.py --check`; `python -I redesign/fusion/check.py`; `python -I redesign/interfaces/merge_check.py` |
| Pod against stand-in wing and pack | `python -I redesign/team/D2/pod_selfcheck.py` |
| Claims | `python -I redesign/team/D2/pod_claims.py` then `python -I redesign/proofs/build_graph.py` |
| Built | `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`; `T-A3-CG-BALANCE` with the nominal pack |
