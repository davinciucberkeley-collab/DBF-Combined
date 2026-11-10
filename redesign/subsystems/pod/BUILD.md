# Pod — build notes for G4

Status: `PROPOSED` (D2, revision D2-R4 on params A1-R3, 2026-11-09). Dimensions from `subsystems/pod/params.json`
and `fusion/pod.py`; print the parts from the Fusion bodies (BuildAll → export STL per component). About 7.5 h
hands-on + 2 × 24 h cures. All x from the wing LE, z from the chord line, y + to the right, mm unless stated.

## Before you start

| Item | Detail |
|---|---|
| Materials | 3/16 in foam board (one 20 × 30 in sheet); XPS F-250 offcut from the core sheet (nose block, 2 crush blocks); PETG ~80 g; 30 min laminating epoxy + glass microballoons; 2 × 20 × 300 mm rubber-backed battery straps; 10 × 200 mm hook-and-loop strap (FC); 2.5 mm EVA sheet with anti-slip face; 2 × 7.6 × 300 mm nylon ties (50 lb); hook-and-loop 40 mm; 4 × M3 × 5.7 brass heat-set inserts; 1 × M3x16 **PA66** cheese-head screw + PA66 nut; 2.5 mm ties (airspeed, JR bar); light-coloured tape; label |
| Tools | steel rule, snap knife, hot wire with the core templates, sanding block 120 / 220 grit, soldering iron with insert tip, flat screwdriver, 0.1 g scale, calipers, feeler gauge, masking tape, 3 mm drill shank (gauge) |
| Needs first | D1's core with the pod recess cut (x 22.6 … 65, z 15, y ±70); tape skin left off over x 0 … 95, y ±70; spar slot **filled flush over the spar at \|y\| < 29** and **left open at y ±29 … 53** (feet); one tie laid under the spar at **y ±36** before the spar bond (CR-D2-04) |
| Stop | no CA on XPS or foam board (melts it); no steel screws, nuts or washers within 50 mm of the GPS; epoxy fumes: ventilate, gloves |

## Steps

| # | Action | Tools · cure | Check after |
|---|---|---|---|
| 1 | Print, PETG, 0.2 mm layers. Tray front piece (floor + 3 mm forward stop, 100 %) and rear piece (floor with strap slots and windows + both guides with the 3 mm channel notch); FC, avionics, PDB and UBEC plates 0.8 mm, 100 % (FC plate with the two end stops and their 11 × 2 mm strap slots; avionics plate with 2 tie posts 21 mm apart inside); JR tie bar; handle lying flat (feet, bridge, aft stop, gussets, legs with the right-leg windows, grip with its groove, mast socket: 3 perimeters + 25 %; aft stop and bridge 100 %); spreader 100 %; spacers 2 / 4 / 8 / 8; pitot socket with flange and the keyed (D) bore; mast with the 45° pad (arrow toward the pad's low edge = nose); hatch tongue, latch tab, nose lip, 2 antenna tubes | printer | weigh each against `parts.csv` (`T-D2-WEIGH`); ±15 % else re-slice; a 6.0 mm rod with a 5.6 mm flat enters the socket one way only |
| 2 | Heat-set 4 M3 inserts in the PDB bosses, flush; counterbore the mast socket boss Ø6.5 × 4.5 on +y | iron 230 °C, drill | M3 runs in by hand; boss grip 10.0 mm |
| 3 | Cut board: floor 175.2 × 130.4; 2 side walls 210 long (flat bottom x −115 … 65, then the wing upper surface to x 95; top z 80.2) with a **16 × 12 exit at x 56 … 72, z 27 … 39**; nose wall 130.4 × 70 with a 12 × 12 hole at y −46, z 45, a 30 × 15 vent at the top centre (z 65.2 … 80.2) and a 6.4 hole at y −46, z 24.5; aft wall 130.4 × 62.2 with two 11 × 16 exits at y ±53 … 64, z 27 … 43 (servo leads) and a 30 × 15 vent top centre; aft deck 24.2 × 130.4 with two 7.8 square slots at x 80, y ±48; hatch 170.2 × 140 with a 6.4 hole at x −54, y −46. Tape the exit edges | rule, knife | dry-fit the box on the core; no rock |
| 4 | Hot-wire: LE filler (x 0 … 22.6, under the floor, full width); nose block 7.0 × 130.4 × 60.4 with the 33 × 33 flange cut-out, vent notch and antenna hole; crush block per pack (step 15) | hot wire | block faces square; 0.1 g weigh |
| 5 | Cut a 1 mm deep, 22 mm wide strap groove across the floor under each strap-slot pair (x −36, +33.5) | knife | strap slides under the tray |
| 6 | Bond to the floor, **full area** (sand PETG 120 grit, scuff the paper 220): tray front piece (forward stop aft face at x −100.2), rear piece starting at x −60.5 so a **10 mm channel** stays open at x −70.5 … −60.5; FC, avionics, PDB and UBEC plates; JR bar at x 28.5 … 32.5 right. Weight on top | epoxy · 24 h | 52 mm between guides at both ends; 3 mm drill shank passes under each guide notch |
| 7 | Bond nose wall, side walls, aft wall and nose lip to the floor. **6 mm microballoon fillet** floor-to-side-wall inside, over x −66 … −6 and x 3.5 … 63.5 (±30 mm of each strap, CR-C6-17) and over x −100 … 0. Pitot socket through the nose hole, flange epoxied to the wall inside face, flat up (clamp); nose antenna tube through its hole | epoxy · 4 h tack | socket bore points at (−195, −46, 45): sight a 6 mm rod |
| 8 | Bond the nose block behind the nose wall: to the nose wall, both side walls and the floor | thickened epoxy · 4 h | flush with the forward stop fore face (x −103.2), vent notch clear |
| 9 | Scuff the spar top at both foot stations and the slot fill over \|y\| < 29 (120 grit, IPA). Bond the handle: saddles on the spar, bridge on the slot fill; cinch the tie at y ±36 round each saddle | thickened epoxy · 24 h | aft stop face at x 77.0 ± 0.5, vertical; legs at x 80, y ±48; right-leg window faces +y |
| 10 | Bond the box into the recess (floor, filler, wall bottoms) with thickened epoxy; slide the aft deck over the legs and bond it to the walls and legs | epoxy · 24 h before any load | no gap under the floor; deck flush; 6.7 mm between each leg and the aft wall |
| 11 | Tape the wing skin over the pod foot by 15 mm all round; light-coloured tape over the pod top; label on the grip | tape | label readable both sides |
| 12 | Hatch: tongue under the front, 12 × 40 hook tab at the aft edge, loop on the deck; antenna tube A bonded in its hole | epoxy · 1 h | closes flush, opens with one finger |
| 13 | Mast into the grip socket; M3x16 PA66 screw from +y, PA66 nut, finger tight + ¼ turn, no washer, no threadlocker | screwdriver | nut fully on, ≥ 2 pitches showing; pad faces forward-up |
| 14 | Straps through the slots, hook-and-loop overlap ≥ 50 mm, mark the overlap line; EVA pads on the tray centred on the slots | — | strap slides under the tray |
| 15 | Per pack (weighed): spacer = 77 − aft face (nominal 8, 680 g 4); crush block length = (aft face − 140 − 1.5) + 100.2 (nominal 27.7, 680 g 31.7), section 51.4 × 58.9 (sliding fit between the guides, 0.5 under the hatch) with a 30 × 8 top groove; spreader 1.5 mm on the pack fore face; label block and spacer with the pack id | hot wire, rule | block ≥ 24.9 mm (C5) |
| 16 | Hand over to F1, F3, F2: F1's power frame on the inserts and the UBEC on its plate; FC on 4 gel cubes, 10 mm strap through both end-stop slots, round the board, 1–2 mm slack; GPS cable up the right side wall, in at the leg window, out under the grip, up the mast bore | — | strap does not press the board; cable not alongside power |
| 17 | Proof tests: `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL` (12 kg on the grip, 10 s), `T-C3-STOP-PUSH` | spring scale, weights | no slip, no lift, no pack play; feeler ≥ 0.5 mm under the pack over the slot; stop breaks before the tray peels |

## Field use (pre-flight card)

| # | Action |
|---|---|
| 1 | Hatch open (pull the tab up, slide the hatch aft) |
| 2 | This pack's spacer against the aft stop (label on the pack) |
| 3 | Pack in, leads aft, lowered with the aft face at the hatch edge, then slid back under the deck onto the spacer; spreader and crush block in front, against the forward stop |
| 4 | Straps cinched, overlap past the mark; leads over the stop, left inboard of the leg, AS150U into F1's cradle; plug last, after the RC link is up |
| 5 | Hatch on (tongue under the nose lip, press the tab); pitot boom home, flat up |
| 6 | Lift only by the grip |

## Parts

| Id | Part | Make | Mass g |
|---|---|---|---|
| `POD-001` | Shell: board floor, walls (side exits), nose, aft wall, deck; XPS filler and nose block; nose lip; antenna tube B; fillets | knife, hot wire, FDM | 24.8 |
| `POD-002` | Tray front + rear, forward stop, guides; FC, avionics, PDB, UBEC plates; JR bar; 4 inserts | FDM ×7 | 31.2 |
| `POD-003` | Hatch, tongue, latch tab, antenna tube A | knife, FDM | 8.5 |
| `POD-004` | 2 straps + 2 EVA pads | buy | 9.1 |
| `POD-005` | GPS mast with 45° pad, PA66 screw + nut | FDM | 5.5 |
| `POD-006` | Pitot socket with flange, keyed bore | FDM | 5.8 |
| `POD-007` | Handle: saddles, bridge + aft stop + gussets, legs, grip, mast socket; 2 ties; label | FDM | 34.1 |
| `POD-008` | Trim kit (nominal): crush block, spreader, 8 mm spacer | hot wire, FDM | 9.1 |
| | **Total** (allocation 122, CR-D2-09 asks 128) | | **128.0** `EST` |

## How to verify

| Check | Command or test |
|---|---|
| CAD, masses, interfaces | `python -I redesign/team/D2/pod_data.py --check`; `python -I redesign/fusion/check.py`; `python -I redesign/interfaces/merge_check.py` |
| Pod against stand-in wing and pack | `python -I redesign/team/D2/pod_selfcheck.py` |
| Claims | `python -I redesign/team/D2/pod_claims.py` then `python -I redesign/proofs/build_graph.py` |
| Built | `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-C3-STOP-PUSH`; `T-A3-CG-BALANCE` with the nominal pack |
