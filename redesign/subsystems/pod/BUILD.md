# Pod — build notes for G4

Status: `PROPOSED` (D2, 2026-11-09). Dimensions from `subsystems/pod/params.json` and `fusion/pod.py`; print the
parts from the Fusion bodies (BuildAll → export STL per component). Total about 6 h hands-on + 2 × 24 h cures.

## Before you start

| Item | Detail |
|---|---|
| Materials | 3/16 in foam board (one 20 × 30 in sheet), XPS offcut from the core sheet, PETG filament ~60 g, 30 min laminating epoxy + microballoons, 2 × 20 × 300 mm rubber-backed battery straps, 0.5 mm silicone sheet, 2 × 7.6 × 300 mm nylon ties (50 lb), hook-and-loop 30 mm, 4 × M3 × 5.7 brass heat-set inserts, 1 × M3x16 SHCS + nyloc + washer, label |
| Tools | steel rule, snap knife, sanding block 120 grit, soldering iron with insert tip, 2.5 mm hex key, 5.5 mm spanner, 0.1 g scale, calipers, masking tape |
| Needs first | D1's core with the pod recess cut, tape skin left off over x 0 … 0.095 m, y ±0.07 m, spar slot left open at the two foot stations and the two ties laid under the spar before the spar bond (`CR-D2-04`) |
| Stop | no CA on XPS or foam board (melts it); epoxy fumes: ventilate, gloves |

## Steps

| # | Action | Tools · cure | Check after |
|---|---|---|---|
| 1 | Print: tray (bay floor + guides + aft stop), FC plate, avionics plate at 100 % (plates are ≤ 1.5 mm); handle, spacers, pitot socket at 3 perimeters + 25 % infill; mast and nose lip solid. PETG, 0.2 mm layers | printer | weigh each part against `parts.csv` (`T-D2-WEIGH`); ±15 % else re-slice |
| 2 | Heat-set the 4 M3 inserts in the FC plate bosses, flush | iron 230 °C | insert square to the plate, M3 screw runs in by hand |
| 3 | Cut the board: floor 165.2 × 130.4, 2 side walls (profile from the CAD drawing: flat bottom to x 0.065 m, then the wing upper surface), nose wall 130.4 × 70 with a 12 × 12 hole centred y −46, z 45 mm, aft wall 130.4 × 62.3 with two 16 × 12 exits, aft deck 24.2 × 130.4 with two 7.8 mm square leg slots, hatch 160 × 140 | rule, knife | dry-fit the box on the core; walls sit in the recess with no rock |
| 4 | Hot-wire the XPS LE filler (x 0 … 0.023 m, under the floor, full width) with the core template | hot wire | filler top flat at the pod base, bottom matches the LE |
| 5 | Cut a 1 mm deep, 22 mm wide strap groove across the floor under each pair of strap slots | knife | strap slides through under the tray |
| 6 | Bond the tray, FC plate and avionics plate to the floor (sand PETG 120 grit). Weight on top | epoxy · 24 h | guides parallel, bay 52 mm between guides at both ends |
| 7 | Bond nose wall, side walls, aft wall and nose lip to the floor; pitot socket through the nose-wall hole, flush with the inside of the nose lip line, axis along x | epoxy · 4 h tack | socket bore points at x −0.185 m: sight a 6 mm rod along it |
| 8 | Scuff the spar top at the two foot stations (120 grit, IPA). Bond the handle feet onto the spar, legs vertical; pass each tie through its foot slot and cinch | epoxy + microballoons · 24 h | grip level, centred on y = 0, legs at x 0.080 m |
| 9 | Bond the pod box into the recess (floor, filler, wall bottoms) with thickened epoxy; slide the aft deck over the handle legs and bond it to the walls and legs | epoxy · 24 h before any load | no gap under the floor; deck flush with the wall tops |
| 10 | Tape the wing skin over the pod foot by 15 mm all round; fit the 'LIFT HERE — do not lift by the motors' label on the grip | tape | label readable from both sides |
| 11 | Hatch: bond the tongue to the front underside, hook tab at the aft edge, loop patch on the aft deck | epoxy · 1 h | hatch closes flush, opens with one finger, no magnets |
| 12 | Mast into the grip socket, M3x16 SHCS + washer + nyloc across, snug (≈ 0.3 N·m) | hex key, spanner | mast does not rock; GPS plate level |
| 13 | Thread the straps through the slots; fit the two silicone pads on the tray at the strap stations | — | strap passes freely under the tray |
| 14 | Proof tests: `T-D2-FIT` (both packs, both trim ends, hatch closes, XT60 and balance lead reachable); `T-D2-HANDLE-PULL` (12 kg on the grip, wing supported at the spar ends, 10 s) | spring scale, weights | no tie slip, no foot lift, no pack movement |

## Field use (pre-flight card)

| # | Action |
|---|---|
| 1 | Hatch open (pull the tab up, slide the hatch aft) |
| 2 | Spacers: the card for this pack (weighed) says how many go in front of the pack; the rest go behind it. Pack lead end aft |
| 3 | Pack in against the front spacers or the nose wall, straps cinched, leads over the stop wall into the left channel |
| 4 | Plug the XT60 last, after the RC link is up; balance lead parked in the left channel |
| 5 | Hatch on (tongue under the nose lip, press the tab); pitot boom pushed fully home, keyed flat up |
| 6 | Lift only by the grip |

Removing the pack: lift the spacers out, slide the pack 6 mm aft so its nose clears the lip, lift it out.
