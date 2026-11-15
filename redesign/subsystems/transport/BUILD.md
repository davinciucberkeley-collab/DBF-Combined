# Transport box — build steps

Status `PROPOSED` (D7, closure round 2026-11-14: board box from 4 Home Depot XLBX blanks, 1.25 × 0.565 × 0.54 m, PE from one Walmart 2-count, hand holes, cord lashings; was Coroplast with bolted handles). About 6 h for two people, and 1.5 h for the mat. Build after the first wing core exists
(the saddles are cut to it) and after `CAR-FIT.md` has two measured cars.

| Tools | Materials |
|---|---|
| straightedge, box cutter, scoring tool (blunt butter knife), hot-wire bow, band saw, tape measure, luggage scale, laser cutter (mat only) | 4 Home Depot XLBX moving boxes 24 × 20 × 21 in (`T01`), 1 roll packaging tape 1.88 in (`T02`), 1 Walmart PE foam sheet 2-count 16 × 12 × 2 in (`T06`), XPS offcuts (wing stock), 2 × 2.6 m paracord from the G18 roll, 3 mm birch ply (two 800 × 400 mm mat panels), 1.5 mm rubber sheet 0.8 × 0.8 m, cloth tape, 1 m of 25 mm webbing |

1. **Check the cars first.** `CAR-FIT.md` passes for two cars at 1.25 × 0.565 × 0.54 m. If a car rejects 0.54, stop
   and tell A1. The fallback is a 0.50 m box with 56 mm columns and a "MAX DROP 0.15 m" label. CHECK: two rows signed.
2. **Cut the panels** (`SPEC.md` "Panel nest"). Slit each XLBX at its glue flap and lay it flat. Blanks 1 and 2: a
   long wall 1 250 × 536 and an end wall 557 × 536 from the body row. Blanks 3 and 4: floor and lid, each two
   610 × 565 pieces from the 24 in columns plus a 30 × 565 strip; every score and splice runs across the 565 mm span.
   Lid lips 30 mm, edge saddles, column collars and hand-hole patches from the offcuts. Read the ECT stamp on each
   blank (32 lb/in expected). CHECK: floor diagonals within 3 mm.
3. **Assemble the base.** Splice the floor pieces with tape both faces over a 50 mm offcut strip. Stand the long walls
   on the floor edges, the end walls between them, flutes vertical; tape every seam inside and out. CHECK: outside
   1 250 × 565 mm ± 3 mm, walls square.
4. **Make the lid** (spliced as the floor) and tape the four 30 mm lip strips 4 mm inside its edge (plug lid). No
   lining. CHECK: the lid drops in and sits on the wall tops, no gap > 3 mm.
5. **Make the two crush columns.** Cut 3 PE layers 60 × 50 mm per column from sheet A; band-saw one layer to 18.6 mm
   so the stack is **120** mm; wrap the stack with packing tape (the tape only holds the layers in line). CHECK:
   height 120 ± 2 mm (the window in `SPEC.md`).
6. **Hot-wire the two saddles** from 3 stacked 2 in XPS offcuts with the wing's lower-surface template
   (`subsystems/wing/s5010.dat`, chord 320 mm; trace the template from a **taped** wing rib or add the tape thickness, so
   the saddle fits the skin, not the bare core: no preload, `trn.cradle.saddle_preload_m` 0), x −15 … 235 mm, **width 60 mm (y 0.17–0.23)**, 6 mm LE lip. Tape a
   6 mm PE cap (sliced from sheet B) on the contour. Knife a **9 mm wide, 3 mm deep relief channel** across the cap at x 57–66 mm, under
   the ESC-lead groove (`trn.cradle.relief_x_m`). CHECK: the wing sits in the saddle with no rock; the chalked contact
   patch is ≥ 40 × 40 mm (C2); no chalk on the lead tape; the elevon hinge line is ≥ 10 mm behind the saddle.
7. **Join each saddle to its column** with a packing-tape wrap, column centred under the spar line (x 80 mm).
8. **Place the cradles** on the floor at y ±200 mm from the box centre, with x set so that the foot pads are **12 mm
   from the aft wall** (`trn.box.aft_gap_m`; the feet take an aft-wall drop) and the pod nose is about 12 mm from the
   nose pad (step 11; ≥ 10 mm, design 12.3 mm). Tape a 30 mm tall board collar round each column base to the floor
   (it stays below the 48 mm bottomed column top). CHECK with the aircraft in: lower feet
   and tube ends ≥ 82 mm above the floor (design 84 mm); upper tube ends ≥ 10 mm under the lid; a 2 mm feeler passes
   between each saddle and the brace anchor (y 0.234); nothing else touches.
9. **Cut the tray** (XPS, 460 × 300 × 60 mm): 8 slots 285 × 30 × 40 mm for props on edge (APC 11x5.5E), a 220 × 25 × 25 mm
   pitot-boom slot with a 30 mm PE plug at the tip end, a 140 × 100 × 45 mm pouch pocket. Tape it to the floor
   between the cradles. CHECK: tray top ≥ 150 mm below the wing.
10. **Cut the hold-down pillars** (PE, 100 × 60 mm, 5 layers from sheet A, tape-wrapped, length = lid underside to wing
    upper surface + 5 mm, about 234 mm; 10 mm soft face). Tape them straight to the lid shell over the spar at y ±200 mm (y 0.17–0.23). CHECK:
    the lid closes with light hand pressure; the aircraft does not move when the closed box is tilted 45°.
11. **Cut the hand holes and fit the pads.** Die-cut 100 × 30 mm hand holes, top 35 mm under the lid-lip bottom: one
    on the **aft** wall at y 0, one on each end wall at the chord centre. Tape a 2-layer 180 × 80 mm offcut patch
    (flutes vertical) inside each and cut the hole through it. Tape the end pads (PE 200 × 150 × 30 mm, sliced from
    sheet B) on the end walls and the **nose pad** (PE **1/2 in**, two 160 × 100 mm pieces butted to 160 × 200 mm, centred on the pod nose at 50 mm above the chord plane, with a
    14 mm wide vertical relief slot at y −46 mm for the pitot collar and antenna B, from z +55 mm down 95 mm) on the front wall.
    Fold 4 edge saddles (3-layer offcut, 60 mm) for each cord at the box edges, y ±400 mm. CHECK: `T-D7-HANDLE-PULL`, no crease or tear at a hole; nose to pad ≥ 10 mm; antenna B tip and pitot collar to pad ≥ 2 mm.
12. **Label** the lid and both end walls with the six lines of `trn.box.labels` (`TRN-109`): THIS SIDE UP · KEEP FLAT:
    NEVER STAND ON END · LIFT BY THE HAND HOLES · AIRCRAFT INSIDE: NO LOAD ON LID · PACKS TRAVEL IN THE BATTERY CAN, NEVER IN
    THE BOX · PROPS AND PITOT IN THE TRAY. Add "MAX DROP 0.15 m" on the 0.50 m fallback box only. The end-first and
    lid-down drops are protected only by these labels (`SPEC.md`, drop policy).
13. **Weigh** the box empty and loaded (`T-D7-WEIGH-BOX`) and record the result as a test in `team/D7/transport_calc.py`.
14. **Drop test** with a ballasted dummy on real feet first (`T-D7-CUSHION`, `T-D7-BOX-DROP`), then with the aircraft
    (floor drops only). Chalk all motor caps, feet, the pod nose and the wingtips: no mark on the floor, lid or walls
    except the pads.
15. **Make the landing mat** (`TRN-104`, C5 S1). Laser-cut two 800 × 400 mm panels from 3 mm birch ply, contact-glue
    1.5 mm rubber sheet on one face, hinge the long edges with cloth tape on both faces, edge-tape all round, and rivet
    or tape a webbing carry loop on one panel. CHECK: it folds to 800 × 400 mm and lies flat when open; weigh it
    (`CL-D7-MAT-MASS` 2.7 kg `EST`).
16. **Pack the tote** (`TRN-107`): TX, the landing-spares box (`TRN-108`: D5's spare inserts, cartridges and shoes),
    the flight card and the anemometer. CHECK: weigh the tote, the battery can loaded and the mat (`T-D7-WEIGH-BOX`).
