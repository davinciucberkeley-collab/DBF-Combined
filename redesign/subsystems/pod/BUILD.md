# Pod — build notes for G4

Status: `PROPOSED` (D2, revision D2-R5 on params A1-R4, 2026-11-09; D-47 re-lay: nose −130, bay 21 mm forward). Dimensions from `subsystems/pod/params.json`
and `fusion/pod.py`; print the parts from the Fusion bodies (BuildAll → export STL per component). About 7.5 h
hands-on + 2 × 24 h cures. All x from the wing LE, z from the chord line, y + to the right, mm unless stated.

## Before you start

| Item | Detail |
|---|---|
| Materials | 3/16 in foam board (one 20 × 30 in sheet); XPS F-250 offcut from the core sheet (LE filler, one crush block per pack); PETG ~85 g in 4 colours for the spacers (white, yellow, green, blue); 30 min laminating epoxy + glass microballoons; 2 × 20 × 300 mm rubber-backed battery straps; 10 × 200 mm hook-and-loop strap (FC); 2.5 mm EVA sheet with anti-slip face; 2 × 7.6 × 300 mm nylon ties (50 lb); hook-and-loop 40 mm; 4 × M3 × 5.7 brass heat-set inserts; 1 × M3x16 **PA66** cheese-head screw + PA66 nut; 2.5 mm ties (airspeed, JR bar); light-coloured tape; label |
| Tools | steel rule, snap knife, hot wire with the core templates, sanding block 120 / 220 grit, soldering iron with insert tip, flat screwdriver, 0.1 g scale, calipers, feeler gauge, masking tape, 3 mm drill shank (gauge) |
| Needs first | D1's core with the pod recess cut (x 22.6 … 65, z 15, y ±70); tape skin left off over x 0 … 95, y ±70; spar slot **filled flush over the spar at \|y\| < 29** and **left open at y ±29 … 53** (feet); one tie laid under the spar at **y ±36** before the spar bond (CR-D2-04) |
| Stop | no CA on XPS or foam board (melts it); no steel screws, nuts or washers within 50 mm of the GPS; epoxy fumes: ventilate, gloves |

## Steps

| # | Action | Tools · cure | Check after |
|---|---|---|---|
| 1 | Print, PETG, 0.2 mm layers. Tray front piece (floor with the forward strap slots + 3 mm forward stop, 100 %) and rear piece (floor with the aft strap slots and windows + 3 mm aft stop with 2 gussets, 100 %) + both guides with the 3 mm channel notch, ending at the aft stop; FC, avionics, PDB and UBEC plates 0.8 mm, 100 % (FC plate with the two end stops and their 11 × 2 mm strap slots; avionics plate with 2 tie posts 21 mm apart inside); JR tie bar; handle lying flat (feet, foot bridge x 77 … 90, legs with the right-leg windows, grip with its groove, mast socket: 3 perimeters + 25 %; bridge 100 %); spreader 100 %; spacers 2 white / 4 yellow / 6 green / 8 blue / 8 blue; pitot socket with flange and the keyed (D) bore; mast with the 45° pad (arrow toward the pad's low edge = nose); hatch tongue, latch tab, nose lip, 2 antenna tubes | printer | weigh each against `parts.csv` (`T-D2-WEIGH`); ±15 % else re-slice; a 6.0 mm rod with a 5.6 mm flat enters the socket one way only |
| 2 | Heat-set 4 M3 inserts in the PDB bosses, flush; counterbore the mast socket boss Ø6.5 × 4.5 on +y | iron 230 °C, drill | M3 runs in by hand; boss grip 10.0 mm |
| 3 | Cut board: floor 190.2 × 130.4; 2 side walls 225 long (flat bottom x −130 … 65, then the wing upper surface to x 95; top z 80.2) with a **16 × 12 exit at x 56 … 72, z 27 … 39**; nose wall 130.4 × 70 with a 12 × 12 hole at y −46, z 45, a 30 × 15 vent at the top centre (z 65.2 … 80.2) and a 6.4 hole at y −46, z 24.5; aft wall 130.4 × 62.2 with two 11 × 16 exits at y ±53 … 64, z 27 … 43 (servo leads) and a 30 × 15 vent top centre; aft deck 24.2 × 130.4 with two 7.8 square slots at x 80, y ±48; hatch 185.2 × 140 with a 6.4 hole at x −54, y −46. Tape the exit edges | rule, knife | dry-fit the box on the core; no rock |
| 4 | Hot-wire: LE filler (x 0 … 22.6, under the floor, full width); crush block per pack (step 15). No nose block since D-47 | hot wire | block faces square; 0.1 g weigh |
| 5 | Cut a 1 mm deep, 22 mm wide strap groove across the floor under each strap-slot pair (x −54, +16) | knife | strap slides under the tray |
| 6 | Bond to the floor, **full area** (sand PETG 120 grit, scuff the paper 220): tray front piece **1 mm off the nose-wall line** (fore face x −124.2, forward stop aft face x −121.2), rear piece starting at x −19.5 so a **10 mm channel** stays open at x −29.5 … −19.5 (aft stop face at x 56.0 ± 0.5); FC, avionics, PDB and UBEC plates; JR bar at x 28.5 … 32.5 right. Weight on top | epoxy · 24 h | 52 mm between guides at both ends; 3 mm drill shank passes under each guide notch |
| 7 | Bond nose wall, side walls, aft wall and nose lip to the floor. **6 mm microballoon fillet** floor-to-side-wall inside, over x −84 … −24 and x −14 … 46 (±30 mm of each strap, CR-C6-17) and over x −121 … 0. Pitot socket through the nose hole, flange epoxied to the wall inside face, flat up (clamp); nose antenna tube through its hole | epoxy · 4 h tack | socket bore points at (−210, −46, 45): sight a 6 mm rod |
| 8 | Fill the 1 mm gap between the nose wall and the fore faces of the forward stop and the tray front with microballoon epoxy (D-47: replaces block A; the stop is now backed by the wall); antenna B tube bonded in its wall hole, 10 mm inside | thickened epoxy · 4 h | no void behind the stop (look from above); vent clear |
| 9 | Scuff the spar top at both foot stations and the slot fill over \|y\| < 29 (120 grit, IPA). Bond the handle: saddles on the spar, bridge on the slot fill; cinch the tie at y ±36 round each saddle | thickened epoxy · 24 h | feet on the spar, bridge on the fill; legs at x 80, y ±48; right-leg window faces +y |
| 10 | Bond the box into the recess (floor, filler, wall bottoms) with thickened epoxy; slide the aft deck over the legs and bond it to the walls and legs | epoxy · 24 h before any load | no gap under the floor; deck flush; 6.7 mm between each leg and the aft wall |
| 11 | Tape the wing skin over the pod foot by 15 mm all round; light-coloured tape over the pod top; label on the grip | tape | label readable both sides |
| 12 | Hatch: tongue under the front, 12 × 40 hook tab at the aft edge, loop on the deck; antenna tube A bonded in its hole | epoxy · 1 h | closes flush, opens with one finger |
| 13 | Mast into the grip socket; M3x16 PA66 screw from +y, PA66 nut, finger tight + ¼ turn, no washer, no threadlocker | screwdriver | nut fully on, ≥ 2 pitches showing; pad faces forward-up |
| 14 | Straps through the slots, hook-and-loop overlap ≥ 50 mm, mark the overlap line; EVA pads on the tray centred on the slots | — | strap slides under the tray |
| 15 | Per pack (weighed; `python -I redesign/team/D2/pod_station_options.py <g> <x>` for other masses): 680 g no spacer, block 35.7; 550 g 8 blue, block 27.7; 503 g 8 blue + 2 white, block 25.7. Block length = (aft face − 140 − 1.5) + 121.2, section 51.4 × 58.9 (sliding fit between the guides, 0.5 under the hatch) with a 30 × 8 top groove; spreader 1.5 mm on the pack fore face; write the pack mass, station and spacer colours on the pack label and the block | hot wire, rule | block ≥ C5's length for that mass (25.7 mm at 550 g) |
| 16 | Hand over to F1, F3, F2: F1's power frame on the inserts and the UBEC on its plate; FC on 4 gel cubes, 10 mm strap through both end-stop slots, round the board, 1–2 mm slack; GPS cable up the right side wall, in at the leg window, out under the grip, up the mast bore | — | strap does not press the board; cable not alongside power |
| 17 | Proof tests: `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL` (12 kg on the grip, 10 s), `T-C3-STOP-PUSH` | spring scale, weights | no slip, no lift, no pack play; pack aft face ahead of the recess end; neither stop peels at 100 N |

## Field use (pre-flight card)

| # | Action |
|---|---|
| 1 | Hatch open (pull the tab up, slide the hatch aft) |
| 2 | This pack's spacer stack against the aft stop (colours on the pack label: 680 g none, 550 g blue, 503 g blue + white) |
| 3 | Pack in, leads aft, lowered through the hatch onto the spacer stack; spreader and this pack's crush block in front, against the forward stop |
| 4 | Straps cinched, overlap past the mark; leads over the stop, left inboard of the leg, AS150U into F1's cradle; plug last, after the RC link is up |
| 5 | Hatch on (tongue under the nose lip, press the tab); pitot boom home, flat up |
| 6 | Lift only by the grip |

## Parts

| Id | Part | Make | Mass g |
|---|---|---|---|
| `POD-001` | Shell: board floor, walls (side exits), nose, aft wall, deck; XPS filler; nose lip; antenna tube B; fillets | knife, hot wire, FDM | 24.3 |
| `POD-002` | Tray front + rear, forward and aft stops, gussets, guides; FC, avionics, PDB, UBEC plates; JR bar; 4 inserts | FDM ×7 | 40.0 |
| `POD-003` | Hatch, tongue, latch tab, antenna tube A | knife, FDM | 8.9 |
| `POD-004` | 2 straps + 2 EVA pads | buy | 9.1 |
| `POD-005` | GPS mast with 45° pad, PA66 screw + nut | FDM | 5.5 |
| `POD-006` | Pitot socket with flange, keyed bore | FDM | 5.8 |
| `POD-007` | Handle: saddles, foot bridge, legs, grip, mast socket; 2 ties; label | FDM | 28.3 |
| `POD-008` | Spacer set (flight: the 8 mm blue one; the rest field kit) | FDM | 1.5 |
| `POD-009` | Crush block (550 g cut) | hot wire | 2.3 |
| `POD-010` | Spreader | FDM | 5.3 |
| | **Total** (allocation 131, D-48) | | **131.0** `EST` |

## How to verify

| Check | Command or test |
|---|---|
| CAD, masses, interfaces | `python -I redesign/team/D2/pod_data.py --check`; `python -I redesign/fusion/check.py`; `python -I redesign/interfaces/merge_check.py` |
| Pod against stand-in wing and pack | `python -I redesign/team/D2/pod_selfcheck.py` |
| Claims | `python -I redesign/team/D2/pod_claims.py` then `python -I redesign/proofs/build_graph.py` |
| Built | `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-C3-STOP-PUSH`; `T-A3-CG-BALANCE` with the nominal pack |
