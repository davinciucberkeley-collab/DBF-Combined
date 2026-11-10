# Mechanisms build (MEC)

D6-R2 · for G4's work packages. Right side shown; the left side is the mirror (print mirrored parts, bend the left
pushrod the other way). Do it after the wing core is cut and skinned (D1 BUILD) and the fins are bonded (D3), before
the first power-up. Times are for one side.

## Parts, tools, consumables

| Item | Per side | Note |
|---|---|---|
| `MEC-001` servo SH-0255MG+ | 1 | weigh, record (`T-D6-WEIGH`) |
| `MEC-004` horn, `MEC-006` link horn, `MEC-008` frame, `MEC-007` cover | 1 each | PETG; horns 100 % infill, flat on the y face; frame (windowed top plate) and cover 3 / 2 perimeters |
| `MEC-005` rod 1/8 in pultruded carbon | 67 mm | cut with an abrasive disc (not side cutters: they split it), wrap tape at the cut, scuff the bonded ends 120 grit, wear a mask |
| `MEC-009` CF tube 5 × 4 mm | 160 + 210 mm | inboard / outboard panel |
| `MEC-003` 2-56 rod + steel clevis + silicone keeper | 1 | Z-bend pliers |
| M2 × 6 self-tapping pan head | 2 | cover |
| Tools | — | pin vise + 1.6 mm drill, Z-bend pliers, 2.5 mm slot saw or hobby knife, 5.4 mm ball router bit or round file, protractor, feeler gauges 1.0 mm, Phillips #0 and #1, servo tester or the FC |
| Consumables | — | 30 min epoxy, microballoons, IPA, 120 grit paper, Loctite 222, packing tape 48 mm |

## Steps

1. **Check the prints.** Horn bore 3.3 mm and pin hole: drill the pin hole to the clevis pin (1.6 mm) with the pin
   vise. Push the rod into both bosses: snug, no rock. **Check:** rod slides in by hand, clevis pin turns freely in
   the horn with no visible play.
2. **Rout the torque-tube grooves** (panels off the wing or hinged up): 5.4 mm round groove along each panel,
   centre 7.5 mm aft of the panel front edge (upper corner), mid-thickness: inboard panel from |y| 0.135 to 0.295
   (the 65 mm at the root end has no tube), outboard panel from 0.345 to 0.555. Cut the
   2.5 mm horn slots through the panel at y 0.285 (inboard) and 0.355 (outboard), x 6–40 mm aft of the hinge line.
   **Check:** tube sits flush, ≥ 1.2 mm foam above and below.
3. **Bond the tubes** with epoxy + microballoons; wipe flush; tape over. Cure 24 h. **Check:** panel twisted by hand
   end to end feels stiff; no epoxy on the hinge line.
4. **Tape the panel LE bevel face** with one strip of packing tape (closes the skin into a torsion box). Then apply
   the 25 mm hinge strips (`MEC-010`) on the upper skin, centred on the hinge line, panel at neutral and pressed
   flat. **Check:** panel swings ±30° with no tape wrinkle at the hinge line; end gaps to the fin ≥ 15 mm.
5. **Fit the horns.** Cut the tape back 1 mm outside the flange (lower) and backplate (upper) outlines. Sand the
   PETG 120 grit, IPA wipe. Dry-fit both horns and the rod through D3's fin notch (rod passes under the fin root
   fillet gap). Bond `MEC-004` and `MEC-006` with the rod already in both bosses, panels clamped at neutral on a flat
   board, rod parallel to the hinge line. If the delivered rod is 3.0 mm, fill the 3.3 mm bore with thickened
   epoxy and centre it. Cure 24 h. **Check:** both panels move together; at ±30° the rod clears the
   notch sides, the notch bottom and the fixed-core skin by ≥ 1 mm (feeler gauge).
6. **Prepare the servo.** Centre it (1500 µs from the servo tester or FC). Fit the single arm pointing straight
   down (toward the lower skin), drill its hole to 1.6 mm at 15.6 mm from the shaft, screw on with Loctite 222.
   **Check:** arm at 90° to the case face ±2°.
7. **Bond the frame** (`MEC-008`) in D1's lower pocket with epoxy + microballoons on the top plate and walls; frame
   open side toward the arm plane. Cure 24 h. **Check:** frame lip flush with the lower skin ±0.3 mm.
8. **Install the servo.** Feed the lead through D1's lead hole at the pocket front first. Slide the ears into the
   end-wall slots, case base on the skin plane. Fit the cover (`MEC-007`) with the arm through its slot; 2 × M2 × 6,
   snug only. Tape the cover edges (10 mm overlap). **Check:** servo does not rock when the arm is pushed.
9. **Pushrod.** Z-bend one end of the 2-56 rod, hook it into the arm, thread the clevis on the other end, set the
   length so the panel is at neutral with the arm straight down, clip the clevis on the horn pin hole, slide the
   silicone keeper over the clevis. Length about 55 mm pin to pin. **Check:** no binding over the full servo travel.
10. **Set the throws** with F4's parameters (`T-D6-THROW`): protractor on the panel TE, adjust `SERVO5/6_MIN/MAX/TRIM`
    for exactly −25° (TE up) and +25° (TE down) on both panels; read the arm angles (expect +44.7 / −42.9°, both
    ≤ 45°). Drive by hand to the 30° stops: bevel contact TE down, arm on the cover slot end TE up. **Check:** both
    panels within 1° of each other at every point; servo never buzzes against a stop at the software limits.
11. **Free play** (`T-D6-SLOP`): servo powered at neutral, push the TE up and down with about 0.5 N, dial gauge at
    the TE. **Check:** ≤ 1.0° (≤ 1.2 mm at the 70 mm elevon chord) on each panel.
12. **Load test** (`T-B2-HINGE`, `T-D6-TWIST`): wing on its back, servo at ±25°, hang the VA hinge-moment share at
    each panel's far-end TE (inboard 0.128 N·m → 3.6 N at 35 mm; outboard 0.122 N·m → 3.5 N). **Check:** servo holds,
    far-end lag ≤ 3.7° (predicted 2.8° outboard, 3.0° inboard; mean lag ≤ 2.5° = 10 % of travel), nothing slips;
    record in `T-D6-TWIST`.

## Pre-flight (every flight)

Clevis keeper on · cover screws snug, tape edges down · hinge tape ends not lifting · free play by hand ≤ 1° · both
panels move together and in the right sense in FBWA (stick right: right elevons up).
