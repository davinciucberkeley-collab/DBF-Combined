# Pod: build notes for G4

Status: `PROPOSED` (D2, revision D2-R6 on params A1-R5, 2026-11-10). This revision re-lays the bay for D-62: nose at
−140, bay 10 mm forward, aft stop at 47.5. It also adds the D-69 fixes: forward-stop T, aft-stop strut, wall brackets.
Dimensions come from `subsystems/pod/params.json` and `fusion/pod.py`. Print the parts from the Fusion bodies
(BuildAll, then export one STL per component). Budget about 8.5 h hands-on plus 3 × 24 h cures. All x are from the
wing LE, z from the chord line, y + to the right; mm unless stated.

## Before you start

| Item | Detail |
|---|---|
| Materials | 3/16 in foam board, one 20 × 30 in sheet<br>XPS F-250 offcut from the core sheet: LE filler, one crush block per pack<br>PETG about 95 g, in 4 colours for the spacers (white, yellow, green, blue)<br>30 min laminating epoxy and glass microballoons<br>2 × 20 × 300 mm rubber-backed battery straps<br>10 × 200 mm hook-and-loop strap for the FC<br>2.5 mm EVA sheet with an anti-slip face<br>2 × 7.6 × 300 mm nylon ties (50 lb)<br>40 mm of hook-and-loop<br>4 × M3 × 5.7 brass heat-set inserts<br>1 × M3x16 **PA66** cheese-head screw and a PA66 nut<br>2.5 mm ties (airspeed, JR bar)<br>light-coloured tape; label |
| Tools | steel rule, snap knife, hot wire with the core templates, sanding block 120 / 220 grit, soldering iron with insert tip, flat screwdriver, 0.1 g scale, calipers, feeler gauge, masking tape, 3 mm drill shank (gauge) |
| Needs first | D1's core with the pod recess cut (x 22.6 … 65, z 15, y ±70)<br>a **5 mm microballoon fillet in the recess-step corner** (x 65, z 15 … 20, full width), laid by D1 before the pod goes in (D-69)<br>tape skin left off over x 0 … 95, y ±70<br>spar slot **filled flush over the spar at \|y\| < 29** and **left open at y ±29 … 53** (feet)<br>one tie laid under the spar at **y ±36** before the spar bond (CR-D2-04) |
| Stop | No CA on XPS or foam board (it melts them). No steel screws, nuts or washers within 50 mm of the GPS. Epoxy fumes: ventilate and wear gloves |

## Steps

| # | Action | Tools · cure | Check after |
|---|---|---|---|
| 1 | Print in PETG, 0.2 mm layers. **Forward-stop T** (100 %): upright 3 × 54 × 32 mm with a 12 × 54 × 1.2 mm flange at its foot, flange running aft.<br>**Tray front piece**: floor with the forward strap slots, starting at the stop's aft face.<br>**Rear piece**: floor with the aft strap slots and windows, plus the 3 mm aft stop with 2 root ribs 2 mm long (100 %).<br>Both guides, 6 mm tall, with the 3 mm channel notch, ending at the aft stop.<br>FC, avionics, UBEC plates 0.8 mm (100 %). The FC plate has two end stops with 11 × 2 mm strap slots; the avionics plate has 2 tie posts 21 mm apart (inside faces).<br>**PDB plate** 84 × 36.7 × 0.8 mm with 4 bosses Ø 7.2 (25 mm square) and a 1.2 × 3 mm rib along each boss row, broken at the bosses.<br>JR tie bar.<br>**Handle**, standing on the foot plates: feet, foot bridge (x 77 … 90), legs with the right-leg windows, grip with its groove, mast socket (3 perimeters + 25 %; bridge 100 %). Printed with it: the **strut** (pad 40 × 14 × 1.5 on a 3 × 14 mm rib at y 0 and ±18.5, 25 mm long, each rib's heel on the bridge; support under the ribs) and two **wall brackets** (2 mm web off each foot's outboard edge, then a 1.2 mm flange standing on the wall line, stepped over the side exit).<br>Spreader (100 %); spacers 2 white / 4 yellow / 6 green / 8 blue; pitot socket with flange and the keyed (D) bore; mast with the 45° pad (arrow toward the pad's low edge = nose); hatch tongue, latch tab, nose lip, 2 antenna tubes | printer | Weigh each part against `parts.csv` (`T-D2-WEIGH`); outside ±15 %, re-slice. A 6.0 mm rod with a 5.6 mm flat enters the socket one way only. The bracket flanges are flat and square to the web |
| 2 | Heat-set the 4 M3 inserts in the PDB bosses, flush. Counterbore the mast socket boss Ø 6.5 × 4.5 on +y | iron 230 °C, drill | M3 runs in by hand; boss grip 10.0 mm |
| 3 | Cut board:<br>**floor** 200.2 × 130.4 with a **4 × 54 notch** centred in the front edge (the stop slot) and its **aft lower edge bevelled 45° through the full thickness** (it bonds on D1's recess-step fillet, `E-WNG-17`)<br>2 **side walls** 235 long: flat bottom x −140 … 65, then the wing upper surface to x 95, top z 80.2, with a **16 × 12 exit at x 56 … 72, z 27 … 39**<br>**nose wall** 130.4 × 70 with a 12 × 12 hole at y −46, z 45, a 30 × 15 vent at the top centre (z 65.2 … 80.2), and a 6.4 hole at y −46, z 24.5<br>**aft wall** 130.4 × 62.2 with two 11 × 16 exits at y ±53 … 64, z 27 … 43 (servo leads) and a 30 × 15 vent top centre<br>**aft deck** 24.2 × 130.4 with two 7.8 square slots at x 80, y ±48<br>**hatch** 195.2 × 140 with a 6.4 hole at x −54, y −46<br>Tape the exit edges | rule, knife | Dry-fit the box on the core: no rock |
| 4 | Hot-wire the LE filler (x 0 … 22.6, under the floor, full width) and one crush block per pack (step 16) | hot wire | Block faces square; weigh to 0.1 g |
| 5 | Cut a 1 mm deep, 22 mm wide strap groove across the floor under each strap-slot pair (x −62, +6) | knife | Strap slides under the tray |
| 6 | **Stop T into the floor:** push the T up from below so its upright fills the floor notch and its flange lies under the floor. Epoxy the upright to the notch edge and the flange to the floor underside (9 × 54 mm). Clamp flat | epoxy · 4 h tack | Upright square to the floor; flange fully wetted; aft face 4.0 mm behind the floor's front edge |
| 7 | Bond to the floor, **full area** (sand the PETG 120 grit, scuff the paper 220 grit):<br>tray front piece butted against the stop's aft face (x −131.2)<br>rear piece starting at x −19.5, leaving a **10 mm channel** open at x −29.5 … −19.5 (aft stop face at x 47.5 ± 0.5, back face 50.5)<br>FC, avionics, PDB (x −38 … 46, left) and UBEC plates<br>JR bar at x 28.5 … 32.5, right<br>Put weight on top | epoxy · 24 h | 52 mm between the guides at both ends; the 3 mm drill shank passes under each guide notch |
| 8 | Bond the nose wall, side walls, aft wall and nose lip to the floor. Lay a **6 mm microballoon fillet** floor-to-side-wall inside over x −92 … −32 and x −24 … 36 (±30 mm of each strap, CR-C6-17) and over x −131 … −10. Fit the pitot socket through the nose hole and epoxy its flange to the wall inside face, flat up (clamp). Fit the nose antenna tube through its hole | epoxy · 4 h tack | The socket bore points at (−220, −46, 45): sight it with a 6 mm rod |
| 9 | Fill the 1 mm gap between the nose wall and the stop T's fore face with microballoon epoxy, so the wall backs the stop. Bond antenna tube B in its wall hole, 10 mm inside, with its end 4 mm proud of the nose (x −144, ≥ −150 for D7's box) | thickened epoxy · 4 h | No void behind the stop (look from above); vent clear |
| 10 | Check D1's recess-step fillet is in and cured. Bond the box into the recess (floor, filler, wall bottoms) with thickened epoxy | epoxy · 24 h before any load | No gap under the floor |
| 11 | Scuff the spar top at both foot stations and the slot fill over \|y\| < 29 (120 grit, IPA). Scuff the side-wall inside faces at x 66 … 90 (220 grit) and the bracket flanges, strut pad and saddles (120 grit).<br>**Handle in, in one epoxy session**: saddles on the spar, bridge on the slot fill, each **bracket flange onto its side wall** (epoxy over the whole flange, 1 232 mm² each), and the **strut pad on the aft stop's back face** bedded in thickened epoxy so it bears with no gap. Cinch the tie at y ±36 round each saddle | thickened epoxy · 24 h | Feet on the spar, bridge on the fill; legs at x 80, y ±48; right-leg window faces +y; squeeze-out all round each flange; the pad touches the stop over its whole face; ribs 3.5 mm clear of the skin |
| 12 | Slide the aft deck over the legs and bond it to the walls and legs | epoxy · 4 h | Deck flush; 6.7 mm between each leg and the aft wall |
| 13 | Tape the wing skin over the pod foot by 15 mm all round, and tape over the stop-T flange under the nose. Light-coloured tape over the pod top; label on the grip | tape | Label readable from both sides |
| 14 | Hatch: tongue under the front, 12 × 40 hook tab at the aft edge, loop on the deck. Bond antenna tube A in its hole | epoxy · 1 h | Closes flush, opens with one finger |
| 15 | Mast into the grip socket. M3x16 PA66 screw from +y, PA66 nut, finger tight + ¼ turn, no washer, no threadlocker. Straps through the slots, hook-and-loop overlap ≥ 50 mm, overlap line marked. EVA pads on the tray, centred on the slots | screwdriver | Nut fully on with ≥ 2 pitches showing; pad faces forward-up; strap slides under the tray |
| 16 | Per pack (weighed): H3 takes the station from A3's roll-up on the balance-test day. A1's estimates:<br>546 g: 16 mm spacers (white + green + blue), block 26.2<br>550 g: 14 mm (green + blue), block 28.2<br>590 g: 8 mm (blue), block 34.2<br>Block length = (aft face − 135 − 1.5) + 131.2, never under C5's minimum (25.8 mm for the 550 g class). Section 51.4 × 58.9 (sliding fit between the guides, 0.5 under the hatch) with a 30 × 8 top groove. Spreader 1.5 mm on the pack fore face. Write the pack mass, station and spacer colours on the pack label and on the block | hot wire, rule | No fore-aft play with block, spreader and spacers in |
| 17 | Hand over to F1, F3 and F2:<br>F1's power frame on the inserts (thumb on the cradle when unplugging) and the UBEC on its plate<br>FC on 4 gel cubes, 10 mm strap through both end-stop slots and round the board, 1–2 mm slack<br>Keep x −63 … −53 in the left channel clear above z 31 (F1's PDB)<br>GPS cable up the right side wall, in at the leg window, out under the grip, up the mast bore | — | Strap does not press the board; cable not alongside power |
| 18 | Proof tests: `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL` (12 kg on the grip, 10 s), `T-C3-STOP-PUSH`, `T-C3-POD-PROOF` (+200 N on the brackets along +x and −z), `T-C6-INSERT` | spring scale, weights | No slip, no lift, no pack play; no peel at either stop; no bracket flange lifts |

## Field use (pre-flight card)

| # | Action |
|---|---|
| 1 | Open the hatch: pull the tab up, slide the hatch aft |
| 2 | Put this pack's spacer stack against the aft stop (colours on the pack label) |
| 3 | Pack in, leads aft, lowered through the hatch onto the spacer stack. Spreader and this pack's crush block in front, against the forward stop |
| 4 | Cinch the straps, overlap past the mark. Leads over the stop and the strut, left inboard of the leg, AS150U into F1's cradle. Plug in last, after the RC link is up |
| 5 | Hatch on (tongue under the nose lip, press the tab). Pitot boom home, flat up |
| 6 | Lift only by the grip |

## Parts

| Id | Part | Make | Mass g |
|---|---|---|---|
| `POD-001` | Shell: board floor (stop notch, aft bevel), walls (side exits), nose, aft wall, deck; XPS filler; nose lip; antenna tube B; fillets | knife, hot wire, FDM | 24.7 |
| `POD-002` | Tray front + rear, forward-stop T, aft stop, root ribs, guides; FC, avionics, ribbed PDB, UBEC plates; JR bar; 4 inserts | FDM ×8 | 43.3 |
| `POD-003` | Hatch, tongue, latch tab, antenna tube A | knife, FDM | 9.2 |
| `POD-004` | 2 straps + 2 EVA pads | buy | 9.1 |
| `POD-005` | GPS mast with 45° pad, PA66 screw + nut | FDM | 5.5 |
| `POD-006` | Pitot socket with flange, keyed bore | FDM | 5.8 |
| `POD-007` | Handle: saddles, foot bridge, strut, wall brackets, legs, grip, mast socket; 2 ties; label | FDM | 38.6 |
| `POD-008` | Spacer set (CAD: blue 8 + yellow 4 at the datum; the rest is field kit) | FDM | 1.8 |
| `POD-009` | Crush block (cut at the datum) | hot wire | 2.5 |
| `POD-010` | Spreader | FDM | 5.3 |
| | **Total** (allocation 146, D-63) | | **145.8** `EST` |

## How to verify

| Check | Command or test |
|---|---|
| CAD, masses, interfaces | `python -I redesign/team/D2/pod_data.py --check`; `python -I redesign/fusion/check.py`; `python -I redesign/interfaces/merge_check.py` |
| Pod against stand-in wing and pack | `python -I redesign/team/D2/pod_selfcheck.py` |
| Claims | `python -I redesign/team/D2/pod_claims.py`, then `python -I redesign/proofs/build_graph.py` |
| Built | `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-C3-STOP-PUSH`, `T-C3-POD-PROOF`, `T-C6-INSERT`; `T-A3-CG-BALANCE` with each pack |
