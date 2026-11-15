# Wing: build notes for G4

Design D1-R2 (`SPEC.md`; D-68 / D-69 structure fixes). Positions in the aircraft frame: x aft from the LE, y to the right tip (0 at the centre
line), z up from the chord line. Left = mirror of right. Every cut is drawn in `fusion/wing.py`; print templates
1:1 from its sketches. The wing is the base part: the fins (D3), pod (D2), harness (F2) and mechanisms (D6) steps
slot in where marked **→**.

| Item | Detail |
|---|---|
| Cure | laminating epoxy 30 min: handle 1 h, load or tape after 24 h at ≥ 18 °C |
| Foam glue | epoxy + glass microballoons 1:1 by volume. **No CA, no solvent glue on XPS** |
| Tools | hot-wire bow ≥ 1.25 m (G1 jig), two S5010 c 320 mm templates (2 mm ply or hardboard, TE 0.6 mm), 22.4 mm slot cutter (heated U-wire on a guide rail, or a router with a 22 mm ball bit and fence), sharp knife + new blades, steel rule 1 m, square, calipers, depth gauge, 120-grit block, dowel 18 mm × 0.6 m marked at 180 / 258 mm, 1 g scale, protractor, radius gauge R 3 mm, 45° sanding block (3 mm), printed corner templates (block pocket R 3.15, cut-out R 3) |
| Stock | 1 XPS F-250 blank 1 200 × 330 × 50 mm, 1 CF tube 22 × 20 × 1 000, 4 PETG plugs (print: 2 × Ø 19.8 × 36 at 50 % gyroid, 2 × Ø 19.8 × 20 at 30 %), 2 rolls packing tape 48 mm, 1 roll clear packing tape **100 mm** (4 in) for the LE strip, glass microballoons for the beads and fillet, label |

## Steps

1. **Measure and weigh.** Tube OD/ID, blank mass and size. **Check:** OD 22.0 ± 0.1 mm; XPS ≤ 30 kg/m³ (else tell
   A3: +6.2 g per +1 kg/m³). If OD is off, change `slot.bond_gap_m` so the bore stays OD + 0.4 mm.
2. **Hot-wire the core.** Templates at both ends, LE on the same line, cut the full 1.150 m section in one pass;
   trim the ends square at y ±0.575. **Sand the LE** with a long 120-grit block until no wire step or ridge can be felt
   (B2: a turbulent LE costs 7 % stall speed). Mark the centre line (y 0) and the stations of the cut table on the lower and
   upper faces with a fine pen. **Check:** chord 320 ± 1 mm at both ends and mid-span; TE ≥ 0.6 mm; weigh.
3. **Spar slot from below.** Fence on the LE, cut a 22.4 mm slot centred on x 80 mm, from the lower skin up to
   z +17.8 mm (round top), over |y| ≤ 500 mm. Keep the slot strip. **Check:** the tube slides in with 0.1–0.3 mm per
   side, its top 4.8 mm under the upper skin (≥ 2 mm); no crack to the upper skin.
4. **Pockets and windows.** Knife and hot tool, all per the SPEC cut table:
   block pockets full depth (x 28–97 mm, |y| 302–338 mm) with **R 3.15 mm corners** cut from the printed template
   (D3's block has R 3 mm vertical edges, D-68); then **chamfer the inboard and outboard pocket lips 3 × 3 mm at 45°**
   on both surfaces over the full pocket length (45° block guided on the pocket wall) for the lip beads; anchor pockets top and bottom down to the tube
   (x 69–91, |y| 234–251 mm); pod saddle windows on top (x 69–91, |y| 29–53 mm) to 1 mm below the tube's top
   quarter (z 15.4 mm), with a 2 mm channel round the tube at |y| 32–40 mm for the ties; pod recess (x 23–65 mm,
   |y| ≤ 70, floor flat at z 15 mm, ≤ 6.9 mm deep); servo pockets **from below** (x 172.2–207.5, |y| 252.7–287.9,
   flat ceiling z 7.5 mm, 13–14.5 mm deep; D6's frame must drop in). **Check:** blocks and servo frames drop in by
   hand with no corner contact (radius gauge); chamfer 3 mm deep on the wall and 3 mm wide on the skin; foam over
   the pocket ceiling ≥ 4 mm; recess ends 4 mm ahead of the slot.
5. **Grooves.** Hot-tool or a guided knife, both surfaces, |y| 86–296 mm: signal at x 54.3 (2.5 × 2.4 mm), power at
   x 59.3 and 64.3 (3.0 × 3.1 mm); upper servo groove x 108.2 (4.0 × 1.6) from |y| 65 to 285 mm, then aft along
   y 285 mm to x 173 mm; on that branch cut F2's **JR recess 18 × 10 × 5 mm** (x 150–168, |y| 280–290 mm, floor 5 mm
   under the skin; 4.2 mm foam left to the servo pocket); drill a 5 mm lead hole straight down at x 175, y 285 mm into the pocket. Drill the P1 pass (Ø 8 mm, 45°, x 61.5 mm, upper mouth |y| 92, lower |y| 122) with a 45°
   guide block, line with a 7 mm straw. **Check:** 3.0 mm foam between the aft groove and the slot.
6. **Plugs into the spar.** Scuff tube ends and bore 120 grit, IPA. Butter each plug with thickened epoxy; with the
   marked dowel push the **anchor plug first, centre 258 mm** from the tube end (= |y| 242 mm), then the **block plug,
   centre 180 mm** (= |y| 320 mm). Both ends. Cure 24 h. **Check:** dowel marks; tap test shows the hard spots.
7. **→ Fins (D3, BUILD steps for the blocks):** thread both through-core blocks on the tube and set them at
   |y| 320 mm in the jig. **→ Pod (D2):** lay one nylon tie under the tube at y ±36 mm in each tie channel.
8. **Bond the spar.** Scuffed tube, slot vacuumed. Wet the slot, blocks and pockets with microballoon epoxy, press
   the tube and blocks home on the axis, re-bond the trimmed slot strip as the cap (flush). In the same pour fill the
   **lip-bead chamfers** (upper and lower, inboard and outboard of each block) with microballoon epoxy so the bead
   wets the block side face; strike off flush, sand flush after cure (`WNG-006`, `E-WNG-12…15`). Weight the core flat on
   the bench, LE against a straight edge. Cure 24 h. **Check:** core straight within 1 mm over the span; no
   twist (both TEs on the bench); blocks at y ±320 ± 1 mm; beads continuous, no voids, flush within 0.3 mm.
9. **Cut the elevons free.** Vertical cut at x 249.6 mm through the core over |y| 70–300 and 340–560 mm; end cuts at
   those stations. At the four corners where the hinge cut meets the fin-root tab (|y| 300 and 340) leave foam to an
   **R 3 mm** radius (template; no knife over-run into the tab: D-68, CR-C2-13) and relieve the matching panel corner
   (R 3 mm, 1 mm off the tab radius). Trim each panel 1 mm at both ends; sand the panel's front face to a 30° bevel on the lower side
   (5.5 mm at the lower skin). Route D6's torque-tube groove from below (D6-R2 lengths): inboard panels |y| 133.5–296 mm,
   outboard |y| 344–556 mm, x 254.4–259.8 mm (5.4 mm wide),
   up to z 3.2 mm (1.1 mm foam left under the upper face: go slowly). Knife the 2.5 mm horn-blade slots through each
   panel at |y| 284–286 mm (inboard) and 354–356 mm (outboard), x 254.4–289.6 mm. **Check:** panels 228 and 218 mm
   long, chord 70.4 mm; tube lies in the groove below the face; blade slides in the slot; corner radii by gauge.
   **TE-corner chamfers (D-164, B4 CR-B4-32; params `wing.elevon.te_chamfer_m` [0.02, 0.07]).** Beside each fin-root tab cut
   each panel's trailing corner on a straight line from the hinge-line end (|y| 300 inboard, 340 outboard) to the TE at
   **|y| 280 (inboard panel, 20 mm set-back)** and **|y| 410 (outboard panel, 70 mm)**, both sides; the full-chord panel
   is then |y| 71–280 and 410–559 mm. Mark the line from the template (`fusion/wing.py` `cham_xmax`), saw or hot-wire it,
   sand the cut face square, tape both faces over the cut. The core, the hinge line, the servo pocket (x 172–208,
   |y| 253–288, ahead of the hinge) and the inboard blade slot (y 285, the line is 52.8 mm aft of the hinge there) are not
   touched. **Outboard link-horn slot (y 355): the line is only 15.1 mm aft of the hinge, so D6's 40 mm blade and the
   outboard tube's first 5 mm (|y| 344–349) stand outside the panel: open item for D6 (`team/D1/CHANGE-REQUESTS.md`).**
   **Check:** panel area 15.3 % of S (≥ 15 %, `CL-D1-ELEVON-FRAC`); line meets the TE at |y| 280 / 410 ± 1 mm.
10. **→ Fins:** half-fin roots, anchors and fillets on bare foam (D3). **→ Harness:** ESC and servo leads into the
    grooves with tape tabs (F2), JR joint in its recess. No recess-step fillet (D-103 deleted it: C3-R4 FEA shows it
    does not lower the crash peak). **→ Pod:** shell bonded in the recess, the floor's aft end square on the step,
    and on the spar saddles (D2).
    **Fin-root bond break (C2 closure round, D-179):** the fin roots are released from x 0.22 to the TE on D3's PTFE strips
    (D3 BUILD step 11, params `fin_detail.fin.root_fillet.release_x_m`); keep the skin there clean and dry: no tape
    laps, no epoxy, no skin-prep sanding aft of x 0.22 under the four roots.
11. **Skin.** Lower surface first: spanwise strips from the TE forward, 10 % overlap, the forward strip ending at
    x 41.8 mm (it runs 4.8 mm under the LE strip); then upper the same (forward strip ends at x 40.8 mm). **Then the LE strip:**
    one continuous 100 mm strip per half-span (|y| 70–575 mm), laid last, upper edge on the pen line at x 45.5 mm, wrapped
    round the LE, lower edge at x 46.6 mm. **No seam, overlap edge or doubler edge within 32 mm of the LE** on either
    face (CR-B2-17); the block-pocket doublers are the only exception. No tape on the pod footprint (x 0–95 mm, |y| ≤ 70) or under the half-fin roots; lap 15 mm up both
    fin faces. **Base skin over the blocks (structural, D-153):** every spanwise strip runs unbroken through
    |y| 270–370 mm on both faces for x ≤ 240 mm: no strip end, butt joint, splice or overlap edge started or stopped in
    that zone (C2 rule 2). Doublers: **block doubler, structural (C2-R5, D-153):** two extra layers (3 in all) of
    60 mm chordwise band over each block pocket, |y| 290–350 mm (centred on 320), upper x 120 → round the LE → lower
    x 120, on top of the LE strip, continuous over the lip beads; slit **only** round the tube boss and the half-fin
    root, ≤ 2 mm clearance; one over each servo pocket on the lower face (x 120 → hinge), opening cut
    out. One
    extra strip folded round each tip edge. **Tab edges:** slit a 48 mm strip in half; fold one 24 mm strip over each
    fin-root tab side face (|y| 300 and 340) from the hinge round the R 3 mm corner to the TE, 12 mm onto each face
    (CR-C2-13). Tape both faces of each elevon panel; cut the tape back at each horn station for D6's flange (lower,
    x 257.6–287.6 × 14 mm) and backplate (upper, x 263.6–287.6 × 12 mm). **Check:** no wrinkles at the LE,
    grooves and pockets visible under the tape; rule from the LE at five stations each side: both LE-strip
    edges ≥ 32 mm (`CL-D1-LE-SEAM-X`).
    **Turbulator (D-168, B2; params `wing.turbulator`), laid after the hold point below is signed:** zigzag tape, 6 mm wide,
    0.7 mm high, on the **lower** surface only, centred on **x 64.0 mm** (x/c 0.20; strip x 61–67), rule it from the LE at
    five stations and pen the line before the tape goes on. Full span in pieces: one piece |y| 0 → 290 each side, then
    290 → 305.6 (on the 3-layer doubler band), a **gap 305.6–334.4 at each half-fin root** (fin face 2.4 + 10 mm cove + 2 mm
    clear: nothing is taped under the roots or coves), 334.4 → 350, then 350 → 572. The line is 1.8 mm ahead of the spar-slot cap
    (x 68.8 from the LE) and crosses the aft ESC power groove (x 64.3, |y| 86–296) under the skin: no cut into either. **Do not**
    slit, lift or replace any doubler layer for the turbulator: the D-153 band (|y| 290–350, lower x 0 → 120) stays unbroken and the
    tape rides on top (3 layers + 0.7 mm). **Check:** pieces straight to ±0.5 mm, burnished, no lifted edge; weigh the tape used
    (`WNG-009`, 5.9 g `EST`).
    **HOLD POINT (structural, D-153; sign off before step 12).** The block-pocket corner strength claims pass only
    with this tape (102 / 75 / 52 kPa at 50 % tape credit against 150 / 120 / 100 kPa; `review/DESIGN-ROUND-2026-11-14/C2.md`).
    A second person checks, both blocks, both faces: (a) band edges at |y| 290 ± 2 and 350 ± 2 mm, so it covers the
    pocket faces (|y| 301.85 / 338.15) and the bead toes 3 mm beyond; (b) band ends at x 120 ± 2 mm upper and lower;
    (c) 2 doubler layers over the base skin, counted at the band edge; (d) slits only at the tube boss and half-fin
    root, gap ≤ 2 mm (feeler); (e) no base-skin strip end or splice in |y| 270–370 for x ≤ 240. Any miss: strip and
    re-lay that band. Do not fly a wing that has not passed this hold point.
12. **→ Mechanisms (D6):** torque tubes in the panel grooves, servo frames in the pockets (lead up through the hole),
    horns, link through the lower fin slot, hinge tape, covers.
    **Check (T-D1-THROW):** each panel ±25° by hand, a 0.5 mm feeler passes at the lower edge at +25°.
    **→ Landing (D5):** after the tip tape layer, D5 fits the TPU corner caps `GER-007-L/R` on the fixed TE tip
    corners (|y| 560–575 mm, outboard of the elevon end) with two wraps of 12 mm filament tape (`E-GER-21/22`);
    keep the cap off the outboard elevon (1 mm gap at y 559) and off the CG-jig patch at |y| 450.
13. **Label.** FAA number on the right upper skin, x 115–215, y 375–405 mm; clear tape round the edge.
14. **Weigh and balance (T-D1-WEIGH).** Weigh each part as it is made (core after step 9, tube + plugs after step 6,
    tape roll before / after step 11, panels, label): sum 391.7 g `EST` (allocation 405 g); weigh a cured 20 cm³ cup of the bead mix (≤ 13 g). Record in the `team/A3`
    M-items; a bare-wing knife-edge balance before step 10 (CG x ≈ 114 mm) is optional.

Repair: a tip strike outboard of the spar end (|y| > 500 mm) is a re-cut: saw at y ±500 mm, bond a new 75 mm tip block
(same templates), re-tape (C2 damage fuse).

Repair of the block doubler band (structural, D-153): **replace in kind before flight.** A cut, lifted, torn or
punctured band (or base skin under it) is peeled back to clean tape and re-laid as the original: 2 layers, |y| 290–350,
upper x 120 → LE → lower x 120, slits only at the boss and root (≤ 2 mm), no new base-skin splice in |y| 270–370 for
x ≤ 240; then repeat the step-11 hold-point check. No patch, no other tape, no CA. This goes on the H3 flight card.

Status of the tape credit: the coupon test `T-C2-XPS-COUPON` (owner H1: taped and untaped XPS block coupons in
torsion, pass = no foam crack at 1.5 × the scaled limit, plus 3 notched XPS beams for K_Ic) decides it. If the taped
coupon fails, the fallback is the root-continuous glass D-cell: 1 ply Style 1080 cloth on the bias at ±45, upper
x 120 → LE → lower x 120 mm, |y| 0 → 363 mm continuous across the centre, 2 mm cut-out round each tube boss, laid
with laminating epoxy after the spar bond (step 8) and before the skin (step 11); +16.5 g `EST`, ≈ $43.55 `EST`,
4 h `EST` (C2.md §2, option 6lt: 72 / 70 / 56 kPa). It is not drawn; D1 draws it only if A1 chooses it.
