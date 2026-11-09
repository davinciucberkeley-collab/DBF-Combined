# Landing feet — build notes for G4

Status: `PROPOSED` (D5-R1). Four feet, one per half-fin TE tip (`UR UL LR LL`), plus 8 spare inserts and 2 spare
shoes. Dimensions from `subsystems/landing/params.json` via `fusion/landing.py`; numbers in `SPEC.md`.

## Before you start

| Item | Detail |
|---|---|
| Needs | half-fins bonded to the wing (fins work package), tip corners square and both layers bonded over the last 40 mm |
| Tools | PETG printer, calipers, sharp knife + steel rule, 120-grit paper, IPA wipe, scale (0.1 g) |
| Consumables | 30 min epoxy (~1.2 g total), foam-safe CA, neoprene 1/16 in adhesive-back sheet, F-250 offcut ≥ 2 in thick |
| Time | prints 4 × 25 min + 4 × 20 min (+ spares); bench work 40 min; cure 30 min (24 h full) |

## Steps

1. **Print the shoes** (`GER-001`, 4 + 2 spares): export body `GER-001-UR` from Fusion. All four shoes (and all four
   pistons) are the same part: it is symmetric about the fin plane, so the lower feet are the upper part turned over. Back wall on the bed, 0.2 mm layers,
   2 perimeters, no infill needed, no supports. Check: piston slides in by hand; legs 10.0 mm apart (fin 9.6 + glue).
2. **Print the pistons** (`GER-002`, 4 + 8 spares): flange on the bed, 2 perimeters. Hooks get a 45° lead-in. Mark
   the replace groove 6 mm aft of where the sleeve end sits (on the skirt, both sides) with a knife if the print
   does not show it. Check: slides the full 32 mm in a shoe without binding; hooks click into the windows.
3. **Weigh** one shoe and one piston: ≤ 4.5 g each. Heavier → reduce to 2 perimeters / check extrusion multiplier.
4. **Cut the cartridges** (`GER-003`, 4 + 8 spares): from a 2 in F-250 offcut cut 11.0 × 18.0 mm sticks with the
   stick axis **through the board thickness**; cut each to 38.75 mm (two per foot = 77.5 mm, 0.5 mm preload).
   Check: square ends (a tilted end lowers the first-crush peak unevenly).
5. **Glue cartridges into pistons**: two drops of foam-safe CA on the piston floor, push the first segment home,
   one drop between segments. Let set 2 min.
6. **Pads** (`GER-004`): cut 14.8 × 29 mm from the neoprene sheet, round corners 1 mm; wipe the flange with IPA;
   press on for 30 s. The long edge of the pad overhangs nothing: it matches the flange.
7. **Dry-fit the shoe on each fin tip**: slide the shoe outboard (±z) over the tip until the sleeve floor sits on
   the tip edge and the leg ends sit at the fin TE. The sleeve's open end points aft (+x, past the TE). Scuff the
   fin paper under the legs lightly (120 grit, do not cut through).
8. **Bond the shoes** (`E-GER-01…04`): thin coat of 30 min epoxy on the inside of the legs and the sleeve floor;
   slide on, align the sleeve axis with the fin TE line (along x) using a straight edge on the wing TE; wipe excess
   out of the sleeve bore (it must stay clean for the piston). Tape in place; cure 30 min before step 9, 24 h before
   flight.
9. **Fit the inserts** (`E-GER-05…08`): push each piston + cartridge + pad into its shoe until both hooks click
   (cartridge bears on the back wall). Check: gap flange-to-sleeve end = 32 mm ± 1 mm on all four; the four pads
   lie in one plane (stand the aircraft on a flat table: no rocking).
10. **Record**: weigh the four feet as built (target ≤ 40 g total; tell A3), photograph each foot.

## Field replacement (after a hard landing, ≤ 10 min, no tools)

| # | Action | Check |
|---|---|---|
| 1 | Look at the replace groove: inside the sleeve → replace; visible → fly | groove at the sleeve end = 6 mm used |
| 2 | Press both hooks inward through the windows (fingernail or the short arm of a 2 mm hex key), pull the insert aft | insert comes out with its cartridge |
| 3 | Push a pre-glued spare (`GER-005`) in until both hooks click | 32 mm gap; pad plane level |
| 4 | Inspect the shoe and fin tip: cracked shoe or loose bond → ground the aircraft, replace the shoe (cut off with a razor saw, sand, step 8, 30 min cure) | no crack at the leg roots |

## Animation

One 4 s clip for the build manual (J3): the insert sliding into the shoe and clicking, then the crush stroke
(E-GER-05 slider 0 → −32 mm) with the flange stopping on the sleeve end; the fin ghosted, the insert highlighted.
