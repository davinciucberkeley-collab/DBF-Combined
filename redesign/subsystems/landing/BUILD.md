# Landing feet — build notes for G4

Status: `PROPOSED` (D5-R3). Four feet, one per half-fin TE tip (`UR UL LR LL`), two wingtip corner caps, plus the
field kit (4 + 4 spare inserts, 16 + 16 loose cartridges, 2 spare shoes). Dimensions from
`subsystems/landing/params.json` via `fusion/landing.py`; numbers in `SPEC.md`.

## Before you start

| Item | Detail |
|---|---|
| Needs | half-fins laminated and bonded, with the **R3 tip**: square tip x 0.2746–0.320 m cut down to a flat step at \|z\| 0.2005 m, edge strips ending at x 0.2746 (D3, CR-D5-11) |
| Tools | PETG and TPU printer, calipers, knife + steel rule, 1/4 in K&S brass tube sharpened inside (`GER-013`), 220-grit paper, IPA, 0.1 g scale |
| Consumables | 30 min epoxy + colloidal silica (~1.5 g), foam-safe CA, neoprene 1/16 in adhesive-back sheet (`GER-006`), F-250 offcut ≥ 2 in thick, orange and blue paint markers, 12 mm filament tape |
| Time | prints 4 × 30 min shoes, 4 × 20 min pistons (+ spares), 2 × 10 min caps; bench 50 min; cure 24 h before load |

## Steps

1. **Print the shoes** (`GER-001`, 4 + 2): export `GER-001-UR`; one part fits all four tips (symmetric about the fin
   plane; turn it over for the lower feet). Back wall on the bed, 0.2 mm layers, 2 perimeters, 4 at the rim, no
   supports. Check: leg gap 10.0 mm, cheek gap 12.0 mm; a piston slides in by hand.
2. **Print the pistons** (`GER-002`): 2 + 4 spare in **orange** PETG (upper), 2 + 4 spare in **blue** (lower). Flange
   on the bed. Check: both 6.5 mm fingers free (clear the 0.8 mm slots with a blade), hooks click in a shoe, the
   piston slides the full 38 mm. Knife the replace groove all round the tine 6 mm aft of the rim position.
3. **Weigh**: shoe ≤ 5.9 g, piston ≤ 3.2 g. Heavier: check the extrusion multiplier before printing more.
4. **Cut the cartridges**: from 2 in F-250 cut 16.0 × 13.3 mm sticks with the stick axis **through the board
   thickness**, 44.5 mm long, 2 per foot (89.0 mm incl. 0.5 mm preload). Type U (`GER-003`): solid, orange stripe.
   Type L (`GER-008`): twist the sharpened 1/4 in brass tube through each segment along its axis, push the plug out,
   blue stripe. Check: square ends; bore centred ± 0.5 mm.
5. **Glue the cartridges into the pistons** (`E-GER-09…12`): orange piston + type U, blue piston + type L only. Two
   drops of foam-safe CA on the piston floor, first segment home, one drop between segments. 2 min.
6. **Pads** (`GER-004`): cut 19.8 × 18.1 mm, round the corners 1 mm; IPA on the flange; press 30 s.
7. **Dry-fit each shoe on its fin tip**: sleeve floor on the step, back wall against the step front and the two strip
   ends, cheeks over the strip ends, legs on both faces, sleeve end pointing aft past the TE. Scuff the board paper
   under the legs (220 grit, not through).
8. **Bond the shoes** (`E-GER-01…04`): epoxy + silica on the legs, floor, back-wall face and cheeks; slide on; align the
   sleeve axis with the wing TE line using a straight edge; wipe the bore clean. Tape; 24 h before landing loads.
9. **Fit the inserts** (`E-GER-05…08`): orange up (UR, UL), blue down (LR, LL). Push in until both fingers click.
   Check: flange-to-rim gap 38 ± 1 mm on all four; the four pads lie in one plane (no rocking on a flat table).
10. **Corner caps** (`GER-007`, TPU): push over each wingtip TE corner outboard of the elevon end (do not touch the
    elevon); two wraps of filament tape over the legs. Nothing on the lower surface at \|y\| 0.45 m (CG-jig patch).
11. **Record**: weigh 4 feet + 2 caps (target ≤ 43 g; tell A3); photograph each foot.

## Field replacement (≤ 10 min, no tools)

| # | Action | Check |
|---|---|---|
| 1 | Replace groove inside the rim → replace; visible → fly | groove at the rim = 6 mm used |
| 2 | Squeeze both fingers through the side windows (thumb and finger), pull the insert aft | insert comes out with its cartridge |
| 3 | Push in a spare **of the same colour** (orange up, blue down) until both click | 38 mm gap; pads level |
| 4 | Shoe cracked or bond lifting → ground the aircraft; razor-saw the shoe off, sand, step 8, 24 h | no crack at the rim or legs |

## Animation

One 4 s clip for the build manual (J3): the orange insert sliding into the shoe and clicking, then the crush stroke
(`E-GER-05` slider 0 → −38 mm) with the flange stopping on the rim; the fin ghosted, the insert highlighted.
