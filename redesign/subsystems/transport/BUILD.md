# Transport box — build steps

Status `PROPOSED` (D7). About 6 h for two people plus glue cure. Build after the first wing core exists (the saddles
are cut to it) and after `CAR-FIT.md` has two measured cars.

| Tools | Materials |
|---|---|
| straightedge, box cutter, scoring tool (blunt butter knife), hot-wire bow, hot-melt gun, 5.5 mm drill, 3 mm hex + 8 mm spanner, tape measure, luggage scale | 2 sheets 4 mm Coroplast 48 × 96 in, PE plank 2 in + 1 in (1.7 pcf), 6 mm PE roll, XPS offcuts (wing stock), LSE double-sided tape, zip ties, 6 × M5 × 16 + nylocs + fender washers, 3 strap handles, 2 cam straps, 8 corner protectors |

1. **Check the cars first.** `CAR-FIT.md` passes for two cars at 1.25 × 0.55 × 0.54 m. If not, stop and tell A1.
   CHECK: two rows signed.
2. **Cut the base blank** (one sheet, flutes running along the 1.25 m length): floor 1 242 × 542 mm with 536 mm walls
   on all four sides as one cross-shaped blank. Score the fold lines on the inside face; add 40 mm glue flaps on the
   end walls. CHECK: diagonals of the floor within 3 mm.
3. **Fold and close the base.** Fold walls up, hot-melt the flaps to the inside of the long walls, then a strip of
   LSE tape over every inside corner. Fit 8 corner protectors. CHECK: outside 1 250 × 550 mm ± 3 mm, walls square.
4. **Cut and fold the lid** (second sheet): 1 250 × 550 mm top with a 30 mm lip that folds down 4 mm inside the walls.
   Tape the 6 mm PE lining to its underside. CHECK: lid drops in and sits on the wall tops, no gap > 3 mm.
5. **Make the two crush columns.** Laminate PE 2 in + 2 in + 1 in with LSE tape, cut 60 × 50 × 127 mm. CHECK: height
   127 ± 2 mm; weigh (≈ 10 g each).
6. **Hot-wire the two saddles** from 3 stacked 2 in XPS offcuts with the wing's lower-surface template
   (`subsystems/wing/s5010.dat`, chord 320 mm), x −15 … 235 mm, width 60 mm, 6 mm LE lip. Tape a 6 mm PE cap on
   the contour. CHECK: the wing sits in the saddle with no rock, the elevon hinge line is ≥ 10 mm behind the saddle.
7. **Bond each saddle on its column** (LSE tape), column centred under the spar line (x 80 mm).
8. **Place the cradles** on the floor at y ±200 mm from the box centre, x so the pod nose and the foot tips are
   36 mm from the walls. Tape + 2 zip ties through the floor each. CHECK with the aircraft in: lower tube ends
   ≥ 86 mm above the floor (design 91 mm), upper tube ends ≥ 10 mm under the lid lining, nothing else touches.
9. **Cut the prop tray** (XPS, 460 × 300 × 60 mm): 8 slots 285 × 30 × 40 mm for props on edge, a 220 × 25 × 25 mm
   pitot-boom pocket, a 140 × 100 × 45 mm pouch pocket. Tape it to the floor between the cradles. CHECK: tray top
   ≥ 150 mm below the wing.
10. **Cut the hold-down pillars** (PE, 100 × 60 mm, length = lid lining to wing upper surface + 5 mm, about 205 mm;
    10 mm soft face). Tape them to the lid lining over the spar at y ±200 mm. CHECK: lid closes with light hand
    pressure; aircraft does not move when the closed box is tilted 45°.
11. **Fit handles**: side handle on the front wall at y 0, 80 mm under the top; end handles on both ends. M5 with
    fender washers both sides, nyloc inside, snug only. Glue end pads (PE 200 × 150 × 30 mm) on the end walls.
12. **Label** the lid: "THIS SIDE UP", "LIFT BY HANDLES", "AIRCRAFT INSIDE: NO LOAD ON LID", "PACKS TRAVEL IN THE LIPO BAG".
13. **Weigh** empty and loaded (`T-D7-WEIGH-BOX`); record in `team/D7/claims.json` via a test record.
14. **Drop test** with a ballasted dummy first (`T-D7-CUSHION`, `T-D7-BOX-DROP`), then with the aircraft.
