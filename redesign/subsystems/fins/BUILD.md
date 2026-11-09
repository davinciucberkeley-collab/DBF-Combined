# Fins and motor tubes: build notes for G4

Design R2 (`SPEC.md`). All dimensions come from `fusion/fins.py` and `params.json`. Positions are in the aircraft
frame: x aft from the wing LE, y to the right tip, z up from the chord plane. Left parts mirror right parts.
This subsystem slots into the wing build (D1): the blocks and anchors go in **before the wing is skinned**, and the
half-fin roots are bonded **to bare foam**.

| Cure | 30 min epoxy: handle after 1 h, load after 24 h at ≥ 20 °C · laminating epoxy: 24 h |
|---|---|
| Tools | fine-tooth saw, 120-grit paper, try square, calipers, 2.5 mm hex key (short arm), 5.5 mm wrench, luggage scale (≥ 15 kg), paint pen, masking tape, 1 g scale |
| Prints (PETG) | 2 blocks (3–4 perimeters, 40 % gyroid), 4 mounts (2 × print A, 2 × print B), 4 station collars, 4 anchors, 4 ESC pads; all 100 % unless noted in `parts.csv` |
| Bought / cut | 2 tubes 22 × 20 × 344 mm, 2 plugs 20 × 18 × 53 mm, 4 braces 10 × 3 mm, 8 edge strips 10 × 1 mm, 4 one-layer boards (DXF of the outline from Fusion) |

## Steps

1. **Measure the stock** before anything is cut: tube OD and ID, board thickness, and the motor base pattern and
   screw-hole depth (E1). **Check:** OD 22.0 ± 0.1 mm. Board 4.8 ± 0.2 mm. Pattern 16 × 19 mm. If a value is off,
   tell D3, because the print bores and slots are drawn from it.
2. **Cut the tubes.** Cut two 344 mm lengths from the 1 000 mm stock. Wrap tape over the cut line and saw through
   the tape. Square the ends on 120-grit paper. Mark the middle (z = 0). **Check:** 344 ± 0.5 mm, ends square.
3. **Fit the plugs.** Sand each 53 mm piece of 20 × 18 tube until it slides into the motor tube. Coat it with
   laminating epoxy and push it in with a dowel until its centre is 7 mm above the tube middle (it spans z −19.6 to
   +33.4 mm). Wipe out the excess. Cure 24 h.
4. **Test-fit the prints.** The 22.3 mm bores must slide on the tube, and the block spar bore must slide on the spar.
   The block boss slots must take the board, and the collar slots must take the board with a strip on each face.
   **Check:** every fit is a slide with no play over 0.3 mm. Ream or reprint before going on.
5. **Blocks on the spar (with D1).** Thread both blocks onto the spar with the keyhole slots aft (+x) and the tube
   bore vertical. Set them with the spar jig at y = ±0.320 m and bond with 30 min epoxy. D1 then bonds the spar and
   both blocks into the core (full-depth pockets at x 0.028–0.097 m, 36 mm wide). **Check:** each block within ±1 mm
   of y = 0.320, and the tube bore square to the chord plane within 1°.
6. **Sand flush.** Sand only the front edge of each tube socket flush with the core contour (up to 2.8 mm proud).
   Leave the bosses alone.
7. **Anchors.** D1 cuts the four 20 × 16 mm pockets down to the spar at y = ±0.242 m, top and bottom. Bond each
   anchor foot onto the spar with thickened epoxy, with the brace slot aimed at the tube (use the paper template from
   Fusion). Cure 1 h.
8. **Tubes in.** Scuff the tube over the bore zone. Slide the tube down through the upper boss, the block and the
   lower boss until it stands 141.6 mm above the upper boss top and 155.4 mm below the lower boss bottom. Make it
   vertical with the square in both views, then epoxy it in the bore. **Check:** the tube ends are at ±0.172 m and
   the tube is vertical within 0.5°. Cure 24 h before loading it.
9. **Station collars (dry).** Put a 12.5 mm spacer on each tube end and slide a collar up to it: slot aft, brace ear
   inboard. Do not glue it yet.
10. **Half-fins.** Dry-fit each board: root LE in the boss slot, top LE in the collar slot, root on bare foam. Then
    epoxy both slots, bond the collar to the tube, run a microballoon fillet along the board LE to the tube on both
    sides, and run 12 mm-leg fillets along the root on both sides. **Check:** the board is vertical, the LE gap is
    ≤ 1 mm, and the lower half-fin's link slot sits on the hinge line (x 0.238–0.262 m). Cure 1 h.
11. **Edge strips.** Scuff the strips. Bond one on each face along the top edge, with the end 20 mm inside the
    collar slot and the other end flush with the TE tip. Hold them with tape while they cure. **Check:** the board
    has no twist (lay a straight edge on it).
12. **Braces.** Measure each brace between the bottom of the ear slot and the bottom of the anchor slot (about
    145 mm upper, 157 mm lower). Cut the 10 × 3 strip to that length, scuff the ends and epoxy it into both slots.
    **Check:** the tube is still vertical (square) after the brace is in, because the brace must not pull the tube.
13. **ESC pads.** Bond each pad to the outboard board face at x 78–124 mm and |z| 104–132 mm. Knife two 12 × 3 mm
    slots through the board, matching the pad slots, for the strap.
14. **Skin (D1).** Tape-skin the wing. Lap the tape 15 mm up both board faces at the root, and cut it around the
    bosses and anchors.
15. **Motor mounts.** (a) Check the plate holes against the real motor and drill them out if the pattern differs.
    (b) Screw the motor to the mount with 4 × M3x8, Loctite 243, 0.5 N·m. **Check:** every screw bites at least 3 mm
    (count the turns). (c) Fit print A on UR and LL and print B on UL and LR, unless F4's spin map says otherwise
    (CR-D3-07). (d) Slide each mount onto the tube end until the lip cap seats. Line the plate up square to the fin
    with the try square, then snug the pinch bolt (M3x16, 2 washers, nyloc).
16. **Set the slip (T-D3-SLIP).** Prop off. Hook the luggage scale on the motor can and pull along y, square to the
    fin. Tighten the pinch bolt in 1/8 turns until the collar just turns at **85–100 N (8.7–10.2 kgf)**. Turn it back
    to square and draw a paint-pen witness line across the collar and the tube. **Check:** it holds 60 N without
    moving.
17. **Final checks.** Weigh each part or sub-assembly and record it in `interfaces.json` (T-D3-WEIGH). The gap from
    the motor face to the collar front must be at least 1 mm (prop plane ≥ 39 mm ahead of all structure). Hand the
    aircraft to C4/H1 for the tap test (T-C4-TAP). The witness lines go on the preflight card.

## Repair

| Damage | Fix | Time |
|---|---|---|
| Mount slipped (witness line off) | loosen, square, re-run step 16 | 5 min |
| Mount or plate cracked | swap in a spare print; motor screws stay with the motor | 10 min + step 16 |
| Brace cracked or debonded | cut it out, re-run step 12 | 1 h cure |
| Board broken | cut along the root fillet and the LE, sand the slots clean, bond a new board (steps 10–11) | 2 h cure |

Animation candidate for J3: the mount sliding onto the tube end and the slip test (step 15d–16), 6 s.
