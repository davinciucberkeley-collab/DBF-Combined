# Fins and motor tubes: build notes for G4

Design R5 (`SPEC.md`; CR-A1-63: D-61, D-68, D-70, CR-E3-13, CR-F2-16, CR-C6-36; on R4: D-48, D-51, D-52, D-54). All dimensions come from `fusion/fins.py` and `params.json`. Positions are in the aircraft
frame: x aft from the wing LE, y to the right tip, z up from the chord plane. Left parts mirror right parts; lower
parts mirror upper parts. This subsystem slots into the wing build (D1): the blocks and anchors go in **before the
wing is skinned**, and the half-fin roots are bonded **to bare foam**.

| Cure | 30 min epoxy (+ ~5 % colloidal silica): handle after 1 h, load after 24 h at ≥ 18 °C; parts within 50 mm of a motor + 4 h at 50 °C (C6) · laminating epoxy: 24 h |
|---|---|
| Tools | fine-tooth saw, 120/220-grit paper, try square, calipers, 2.5, 3.4 and 8 mm drills (or an 8 mm brass-tube cutter), pin vice, 2.5 mm hex key (short arm), 5.5 mm spanner, luggage scale (≥ 15 kg), spring scale, paint pen, masking tape, 1 g scale |
| Prints | **ASA** (enclosed printer, D-42): 4 mounts (2 × print A, 2 × print B), 4 ESC pads. **PETG**: 2 blocks (3 perimeters, 15 % gyroid, vertical edges R 3 mm), 4 station collars (15 mm ring, 100 %, tongue 3 perimeters + 20 % gyroid), 4 anchors (80 %). Filament in the flying parts: ~46 g ASA, ~125 g PETG |
| Bought / cut | 2 tubes 22 × 20 × 344 mm, 2 plugs 20 × 18 × 53 mm (the same 1 m length also gives C2's six spar plugs), 4 braces 10 × 2 mm, 8 edge strips 10 × 1 × 224 mm, 48 pins Ø 2.5 × 12 mm (pultruded rod; if 2.5 mm cannot be bought, Ø 2 at 9 mm pitch and tell D3, D-70), 8 boards (DXF of the half-fin outline from Fusion) |
| Fillet mix | light non-sag: phenolic or low-density glass microballoons, ~3 parts to 1 part laminating epoxy by volume, ≤ 3 % colloidal silica (≤ 0.45 g/cm³ cured, `ASM-D3-FILLET-DENSITY`, R5 mass lever); about 14 cm³ per half-fin root. **Before any fillet:** a cured 20 cm³ cup must weigh ≤ 9.0 g (T-D3-WEIGH); if not, use the lightest mix that stays non-sag and tell D3 |

## Steps

1. **Measure the stock** first: tube OD and ID, board thickness, and the motor base pattern, base diameter and
   screw-hole depth (E1). **Check:** OD 22.0 ± 0.1 mm, board 4.8 ± 0.2 mm, pattern 16 × 19 mm, base ≥ 28 mm. If a
   value is off, tell D3, because the print bores and slots are drawn from it.
2. **Laminate the boards.** Spray-glue pairs of boards face to face (3M 77 class, both faces, 1 min open time),
   roll flat and weight under a flat board for 1 h. Then knife-cut the four half-fin outlines through both layers
   from the DXF: LE notch for the collar tongue (40 × 11.3 mm at the top corner, plus the 4.1 mm step under the
   15 mm ring), the **stepped tip** (D5-R7, D-75: the top edge reaches 210 mm at x 0.2614, then a straight cut down to
   a flat step at 201.0 mm to the TE; 58.6 × 9.0 mm removed. The R5 tip, 45.4 × 9.5 mm from x 0.2746, is retired: do not cut it), and the link slot in the two lower halves. Cut the Ø 8 mm ESC-lead hole in every
   half-fin at x 0.086 m, centre 22 mm from the root edge (twist a sharpened 8 mm brass tube through both layers;
   a twist drill tears the paper). **Check:** 9.6 ± 0.3 mm, no delamination at the edges, step edge flat and
   square (D5 shoe dry-fit), hole edge ≥ 17 mm from the root edge (clear of the 15 mm tape lap).
3. **Cut the tubes.** Two 344 mm lengths from the 1 000 mm stock: tape over the cut line, saw through the tape,
   square the ends on 120 grit. Mark the middle (z = 0). **Check:** 344 ± 0.5 mm.
4. **Fit the plugs.** Sand each 53 mm piece of 20 × 18 tube to slide in the motor tube. Coat with laminating epoxy
   and push it in with a dowel to z −19.6 … +33.4 mm. Cure 24 h.
5. **Test-fit the prints.** The 22.3 mm bores slide on the tube; the block spar bore slides on the spar; the boss
   slots take the 9.6 mm laminate; the collar tongue drops into the board notch with a strip on each face in the
   tail slots; the mount collar passes over the collar tail cap. A 2.5 mm cable tie threads each tie lug (two on each block, on
   the inboard boss-tail walls, slot along z; one on each collar, outboard at x 0.060, **slot along x** for the phase
   bundle that rises along z, CR-F2-16). The block's four vertical edges are round (R 3 mm) and seat in D1's R 3 mm
   pocket corners. **Check:** slides with ≤ 0.3 mm play; ties pass.
6. **Drill the motor plates.** Hold the motor on the canted plate face, centred on the shaft opening, and drill
   3.4 mm square to the face through the four pilots (follow the motor's real holes, not the pilots, if they
   differ). No slots (C6). **Check:** each M3×8 bites 3.5 mm (count the turns), no screw bottoms out.
7. **Blocks on the spar (with D1).** Thread both blocks onto the spar, keyhole slots aft (+x), tube bore vertical
   (no strap eyes on the block since D-89c: the four `FIN-013` eyes are bonded on in BUILD-GUIDE stage 6). Set them with the spar jig at y = ±0.320 m, bond with 30 min epoxy. D1 bonds the spar and
   both blocks into the core (pockets x 0.028–0.097 m, 36 mm wide, corners R 3 mm) and lays the ≥ 3 mm microballoon
   bead along the inboard and outboard pocket edges on both surfaces (D-68). **Check:** ±1 mm on y, bore square
   within 1°, no gap at the rounded corners.
8. **Sand flush.** Sand only the front edge of each tube socket flush with the core contour. Leave bosses and eyes.
9. **Anchors.** D1 cuts four 20 × 16 mm pockets to the spar at y = ±0.242 m (top and bottom, C2 plug inside the
   spar). Bond each anchor foot with thickened epoxy, slot aimed at the tube (paper template). Cure 1 h.
10. **Tubes in.** Scuff the bore zone. Slide each tube through upper boss, block and lower boss until its ends are at
    z ±0.172 m (141.6 mm above the upper boss top). Square in both views, epoxy. **Check:** vertical within 0.5°.
    Cure 24 h.
11. **Half-fins.** Dry-fit each laminate: root LE in the boss slot, root on bare foam, LE ≤ 1 mm from the tube.
    Bond the root and an LE fillet to the tube up to the notch, then run **cove fillets on both faces** with the
    fillet mix, using printed radius gauges (CR-C6-24, `E-FIN-53…56`):

    | Zone (x, m) | Upper roots | Lower roots |
    |---|---|---|
    | 0.074 → start of full zone | 4 mm sealing bead | 4 mm sealing bead |
    | full zone → hinge 0.2496 | **15 mm** from x 0.170 | **15 mm** from x 0.146 to 0.2376 |
    | link slot 0.2376–0.2616 | (15 mm to the hinge, then 13 mm) | **no fillet, both faces** (D6 rod, CR-D6-04) |
    | aft of the hinge → 0.318 | **13 mm** (elevon end 2.2 mm clear) | **13 mm** from x 0.2616 |

    Keep filler out of the lead hole, the boss tie lugs and the elevon end gaps (F2 fits the grommets and ties,
    harness BUILD). **Check:** vertical, lower link slot on the hinge line (x 0.2376–0.2616 m), gauge passes, nothing
    within 2 mm of an elevon end. Weigh one half-fin before and after (T-D3-WEIGH, expect +6.3 g). Cure 1 h.
12. **Edge strips.** Scuff. Bond one strip on each face along the sloped top edge, from the LE to the square tip
    step front (x 0.2614, D-75; the strip end faces meet the step); the forward 40 mm stays free over the notch. Tape until cured. **Check:** no twist.
13. **Station collars.** Before buttering, dry-fit: each strip must reach the tube surface inside the tail. Butter
    the tongue, **both tail slots over the full 40 mm** and the ring bore. Drop each collar down the tube end (tail
    aft, ear inboard): the tongue goes between the strips into the notch, the walls outside the strips, until the ring
    top is 12.5 mm below the tube end (spacer). Wipe the squeeze-out at both slot mouths. **Check:** ring top at |z|
    0.1595, ring bottom 0.1445 (15 mm), strips seated. Cure 24 h.

    **Inspection item, strip-tail bond (D-70, CR-C4-37), every tail, before the fin is closed (step 14):**

    | Look for | Pass | Fail → action |
    |---|---|---|
    | Strip forward ends | touch the tube surface (feeler ≤ 0.5 mm) | short strip: pull the collar while wet, re-cut |
    | Epoxy in both slots | continuous bead at both slot mouths over the full 40 mm, no dry strip face visible | voids: inject epoxy with a blunt needle, re-cure |
    | Tongue print | 3 perimeters under each strip face (check the print at the tongue end, no gaps) | reprint the collar |
    | Tap test | uniform sound along the tail with a coin, both faces | dull spot: debond → cut out, re-fit |
    | Pull check | 20 N on each strip end with the spring scale, no movement, no crack at the slot mouth | re-make the joint |

    Record each tail (station, pass/fail, initials) on the build sheet; C4's face margin assumes a bonded tongue.
14. **Pins.** Drill Ø 2.5 mm through strip–laminate–strip at the 11 marked points (every 15 mm, x 0.103 to 0.249,
    5 mm below the edge; none past x 0.2523, the D5-R7 shoe cheeks start at 0.2536, D-75) with a drill guide square to the
    face. Inject epoxy into each hole before the Ø 2.5 mm pin goes in, sand flush (D-70).
15. **Braces.** Measure each brace between the ear-slot bottom and the anchor-slot bottom (≈ 145 mm upper,
    157 mm lower). Cut the 10 × 2 strip, scuff the ends, epoxy into both slots (10 mm each). **Check:** the tube is
    still vertical.
16. **ESC pads.** Bond each ASA pad (46 × 31 mm, CR-E1-30) to the outboard face at x 78–124 mm, |z| 102.5–133.5 mm.
    Knife two 12 × 3 mm strap slots through the laminate, matching the pad. Leave x ≥ 127 mm free for F1's
    capacitor (foam tape, `E-PWR-11…14`).
17. **Skin (D1).** Tape-skin the wing. Lap the tape 15 mm up both laminate faces at the root; cut it around bosses,
    eyes and anchors.
18. **Motor mounts.** Screw each motor to its mount: 4 × M3×8, Loctite 243 on the tip only, no washer, **0.20 N·m**
    (4 N on the luggage scale 50 mm out on the key). Print A on UR and LL, print B on UL and LR. **R5 prints
    only** (D-61: the plate sits 5 mm further forward on longer cheeks; R3/R4 prints must be scrapped). Slide each mount onto the tube end
    until the lip cap seats, square the plate to the fin, snug the pinch bolt (M3×16, 2 washers, nyloc, engagement
    ≥ 5 mm past the nut). **Check (D-52):** look along each shaft from the nose: the prop end leans **toward the
    wing and outboard** at 7 ± 1° (inclinometer on the motor can); H1 repeats it with the hanging yaw test.
19. **Set the slip (T-D3-SLIP).** Prop off. Luggage scale on the motor can, pull along y, square to the fin. Tighten
    in 1/8 turns until the collar just turns at **70–80 N** (2.5 N·m at the 33.9 mm lever of the R5 mount); never
    above 0.4 N·m on the bolt. Square it back, draw a
    witness line across collar and tube. **Check:** holds 60 N.
20. **Final checks.** Weigh each part (T-D3-WEIGH) and record it in `params.json`/`interfaces.json` via D3. Motor
    face to collar front 7.5 ± 0.5 mm (D-61; plate face x 0.02435, tube front face x 0.034: 9.65 mm). Hand over for the tap test (T-C4-TAP-D3) and the mount stiffness test
    (T-C4-MOUNT-STIFF). Witness lines go on the preflight card. Ground-run restraint ties go through the four strap
    eyes (29.4 N each, H1).

## Repair

| Damage | Fix | Time |
|---|---|---|
| Mount slipped (witness line off) | loosen, square, re-run step 19 | 5 min |
| Mount or plate cracked | swap in a spare ASA print (drill it, step 6); motor screws stay with the motor | 10 min + step 19 |
| Brace cracked or debonded | cut it out, re-run step 15 | 1 h cure |
| Strip debonded | cut the pins flush, re-bond the strip, re-drill beside the old holes | 24 h cure |
| Half-fin broken | cut along the root fillet and LE, warm and pull the collar tail off, bond a new laminate (11–14) | 24 h cure |
| Root fillet cracked | grind out the cracked length, re-fillet to the step-11 table | 1 h cure |

Animation candidate for J3: the station collar's tongue dropping between the strips into the notch (step 13), then
the mount sliding onto the tube end and the slip test (steps 18–19), 8 s.
