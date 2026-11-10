# Transport box — build steps

Status `PROPOSED` (D7, round 3, 2026-11-09). About 6 h for two people plus glue cure, and 1.5 h for the mat. Build after the first wing core exists
(the saddles are cut to it) and after `CAR-FIT.md` has two measured cars.

| Tools | Materials |
|---|---|
| straightedge, box cutter, scoring tool (blunt butter knife), hot-wire bow, band saw, hot-melt gun, 3.5 mm drill, 2.5 mm hex key + 5.5 mm spanner, laser cutter, tape measure, luggage scale | 2 sheets 4 mm Coroplast 48 × 96 in, PE plank 2 in + 1 in (1.7 pcf), XPS offcuts (wing stock), 3 mm birch ply (backing strips; two 800 × 400 mm mat panels), 1.5 mm rubber sheet 0.8 × 0.8 m, cloth tape, 1 m of 25 mm webbing, LSE double-sided tape, zip ties, 6 × M3 × 16 SHCS + nylocs + M3 × 12 mm fender washers, 3 strap handles, 2 cam straps, 8 corner protectors |

1. **Check the cars first.** `CAR-FIT.md` passes for two cars at 1.25 × 0.55 × 0.54 m. If a car rejects 0.54, stop
   and tell A1. The fallback is a 0.50 m box with 56 mm columns and a "MAX DROP 0.15 m" label. CHECK: two rows signed.
2. **Cut the base blank** (one sheet, flutes along the 1.25 m length): floor 1 242 × 542 mm with 536 mm walls on all
   four sides as one cross-shaped blank. Score the fold lines on the inside face; add 40 mm glue flaps on the end
   walls. CHECK: floor diagonals within 3 mm.
3. **Fold and close the base.** Fold the walls up, hot-melt the flaps inside the long walls, then a strip of LSE tape
   over every inside corner. Fit 8 corner protectors. CHECK: outside 1 250 × 550 mm ± 3 mm, walls square.
4. **Cut and fold the lid** (second sheet): 1 250 × 550 mm top with a 30 mm lip that folds down 4 mm inside the walls.
   No lining. CHECK: the lid drops in and sits on the wall tops, no gap > 3 mm.
5. **Make the two crush columns.** Laminate PE 2 in + 2 in + 1 in with LSE tape, band-saw to 60 × 50 × **120** mm.
   CHECK: height 120 ± 2 mm (the 109–123 mm window in `SPEC.md`); about 10 g each.
6. **Hot-wire the two saddles** from 3 stacked 2 in XPS offcuts with the wing's lower-surface template
   (`subsystems/wing/s5010.dat`, chord 320 mm), x −15 … 235 mm, **width 60 mm (y 0.17–0.23)**, 6 mm LE lip. Tape a
   6 mm PE cap on the contour. Knife a **9 mm wide, 3 mm deep relief channel** across the cap at x 57–66 mm, under
   the ESC-lead groove (`trn.cradle.relief_x_m`). CHECK: the wing sits in the saddle with no rock; the chalked contact
   patch is ≥ 40 × 40 mm (C2); no chalk on the lead tape; the elevon hinge line is ≥ 10 mm behind the saddle.
7. **Bond each saddle on its column** (LSE tape), column centred under the spar line (x 80 mm).
8. **Place the cradles** on the floor at y ±200 mm from the box centre, with x set so that the foot pads are **12 mm
   from the aft wall** (`trn.box.aft_gap_m`; the feet take an aft-wall drop) and the pod nose is about 22 mm from the
   nose pad (step 11). Tape and 2 zip ties through the floor for each. CHECK with the aircraft in: lower feet
   and tube ends ≥ 82 mm above the floor (design 84 mm); upper tube ends ≥ 10 mm under the lid; a 2 mm feeler passes
   between each saddle and the brace anchor (y 0.234); nothing else touches.
9. **Cut the tray** (XPS, 460 × 300 × 60 mm): 8 slots 285 × 30 × 40 mm for props on edge, a 220 × 25 × 25 mm
   pitot-boom slot with a 30 mm PE plug at the tip end, a 140 × 100 × 45 mm pouch pocket. Tape it to the floor
   between the cradles. CHECK: tray top ≥ 150 mm below the wing.
10. **Cut the hold-down pillars** (PE, 100 × 60 mm, length = lid underside to wing upper surface + 5 mm, about
    215 mm; 10 mm soft face). Tape them straight to the lid shell over the spar at y ±200 mm (y 0.17–0.23). CHECK:
    the lid closes with light hand pressure; the aircraft does not move when the closed box is tilted 45°.
11. **Fit the handles.** Laser-cut 3 backing strips 140 × 30 × 3 mm ply with two 3.4 mm holes 100 mm apart. Side
    handle on the front wall at y 0, 80 mm below the top; end handles on both ends. M3 × 16 SHCS from outside with a
    fender washer, backing strip and nyloc inside, snug only. Glue the end pads (PE 200 × 150 × 30 mm) on the end
    walls and the **nose pad** (PE 1 in, 160 × 200 mm, centred on the pod nose at 50 mm above the chord plane, with a
    12 mm hole for antenna B) on the front wall. CHECK: `T-D7-HANDLE-PULL`, no pull-through; nose to pad ≥ 10 mm.
12. **Label** the lid and both end walls with the six lines of `trn.box.labels` (`TRN-109`): THIS SIDE UP · KEEP FLAT:
    NEVER STAND ON END · LIFT BY HANDLES · AIRCRAFT INSIDE: NO LOAD ON LID · PACKS TRAVEL IN THE BATTERY CAN, NEVER IN
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
