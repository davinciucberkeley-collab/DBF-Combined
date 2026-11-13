# Landing feet — build notes for G4

Status: `PROPOSED` (D5-R8, 2026-11-13: R 2.0 sleeve fillets, 4.6 mm y-side rim, 0.4 mm floor rim, 1.4 mm tine
chamfers, 2.5 mm rails for the 59.25 N side load with margin, CR-H1-22; D5-R7, 2026-11-11: F-400 cartridges and a narrower shoe, fin step at x 0.2614, D-75 / D-76; R6: shoe sleeve end sized by FEA for C5's 59.0 N ultimate side load, CR-C5-18 /
CR-A1-65; R5: caps on `WNG-001`, field kit modelled; R4: pre-crushed cartridges). Four feet, one per half-fin TE tip
(`UR UL LR LL`), two wingtip corner caps, plus the field kit (4 + 4 spare inserts, 16 + 16 loose cartridge sets, 2
spare shoes; the CAD shows one unit of each kit line in a row at y 0.85 m, a layout only: the kit travels in
`TRN-108`). Dimensions from `subsystems/landing/params.json` via `fusion/landing.py`; numbers in `SPEC.md`.

## What changed in R8 (read this if you printed R7 parts)

| Item | R7 | R8 |
|---|---|---|
| Sleeve inside fillets | R 1.0 | **R 2.0** (four corners, full length) |
| Rim at the sleeve end | 3.4 mm all round | **4.6 mm** y sides, 3.4 mm roof (unchanged, level with the pad edge), **0.4 mm** floor side |
| Tine corner chamfers / window rails | 1.0 / 2.0 mm | **1.4 / 2.5 mm** (a 1.0 mm chamfer binds on the R 2.0 fillet) |
| Sleeve section, walls, fin step | 19.1 × 14.4 mm, 1.2 mm, x 0.2614 / \|z\| 0.2010 | unchanged |

R7 shoes and pistons do not mix with R8 parts (chamfer vs fillet). Reprint both.

## What changed in R7 (read this if you printed R6 parts)

| Item | R6 | R7 (D-75, D-76) |
|---|---|---|
| Cartridge foam / section | F-250 offcut, 20.9 × 11.0 mm | **FOAMULAR 400** (40 psi), **14.5 × 9.8 mm**, same 3 × 34.0 mm and same crush force |
| Type-L bore | 7/32 in (5.56 mm) | **5/32 in (3.97 mm)** K&S tube |
| Shoe sleeve / rim | 25.5 × 15.6 mm, rim 2.8 mm | **19.1 × 14.4 mm**, 1.2 mm walls kept, **rim 3.4 mm** |
| Tine / flange | 23.1 × 13.2 mm, flange 1.6 mm, rails 1.5 mm | **16.3 × 11.6 mm**, flange **1.8 mm**, rails **2.0 mm** |
| Fin step (D3) | \|z\| 0.2004 from x 0.2616, 9.6 mm deep | \|z\| **0.2010** from x **0.2614**, **9.0 mm** deep; D3's tip now matches it exactly (D-75) |
| Mass, 4 feet + 2 caps | 69.9 g | **59.1 g** |

R6 shoes, pistons and cartridges do not fit R7 parts. Scrap them; do not mix. Do not print R7 shoes until
`T-D5-COUPON` has passed on F-400 (fallback: R6 parts with F-250, +11 g).

## What changed in R6 (history)

| Item | R5 | R6 |
|---|---|---|
| Shoe sleeve | 21.1 × 17.1 mm, 0.8 mm walls, sharp inside corners | **25.5 × 15.6 mm, 1.2 mm walls (3 perimeters), R 1.0 inside fillets**, R 1.0 fillet outboard of each leg |
| Rim | 1.2 mm | **2.8 mm**, its top level with the pad edge |
| Snap windows | 41 mm long slots | **3 mm windows**; the hook ramp cams under the front edge once the cartridge has set > 1 mm |
| Tine | 19.1 × 15.1 mm, 12 mm engaged | 23.1 × 13.2 mm, 1 mm corner chamfers, **25 mm engaged** |
| Cartridge | 17.3 × 13.3 mm, 2 × 44.5 mm | **20.9 × 11.0 mm, 3 × 34.0 mm** (cut 35.0), same crush force |
| Fin step (D3) | \|z\| 0.2005 from x 0.2746 (45.4 mm) | \|z\| 0.2004 from **x 0.2616 (58.4 mm)**, depth 9.6 mm (CR-D5-31) |
| Print orientation | back wall on the bed | **rim end on the bed**: layers stacked along the sleeve axis (CR-C5-18) |

R5 shoes, pistons and cartridges do not fit R6 parts. Scrap them; do not mix.

## Before you start

| Item | Detail |
|---|---|
| Needs | half-fins laminated and bonded, with the **R7 tip**: square tip x 0.2614–0.320 m cut down to a flat step at \|z\| 0.2010 m, edge strips ending at x 0.2614, last pin at x 0.249 (D3, D-75) |
| Tools | PETG and TPU printer, calipers, knife + steel rule, 5/32 in K&S brass tube sharpened inside (`GER-013`), drill press with a depth stop, 220-grit paper, IPA, 0.1 g scale, **1.5 mm hex key** (insert release) |
| Consumables | 30 min epoxy + colloidal silica (~1.5 g), foam-safe CA, neoprene 1/16 in adhesive-back sheet (`GER-006`), FOAMULAR 400 (F-400) board, 2 in thick (D-76), orange and blue paint markers, 12 mm filament tape |
| Time | prints 4 × 55 min shoes, 4 × 25 min pistons (+ spares), 2 × 10 min caps; bench 60 min; cure 24 h before load |

## Steps

1. **Print the shoes** (`GER-001`, 4 + 2): export `GER-001-UR`; one part fits all four tips (symmetric about the fin
   plane; turn it over for the lower feet). **Stand it on the rim end** so the layers stack along the sleeve axis
   (CR-C5-18: the side load bends the walls within the layers). 0.2 mm layers, 1.2 mm walls = 3 perimeters, 100 %
   solid; keep the modelled R 2.0 inside fillets and R 1.0 leg fillets (the FEA peak sits in those corners). Supports only
   under the two leg ends at the TE. Check: leg gap 10.0 mm, legs 7 mm deep, cheek gap 12.0 mm, wall 1.2 ± 0.1 mm and rim 4.6 mm
   (y sides) / 3.4 mm (roof) / 0.4 mm (floor) at the rim end, snap-window corners clean (no stringing or notch), sleeve 19.1 × 14.4 mm outside; a piston slides in by hand.
2. **Print the pistons** (`GER-002`): 2 + 4 spare in **orange** PETG (upper), 2 + 4 spare in **blue** (lower). Flange
   on the bed. Check: the 1.4 mm corner chamfers are there (a sharp tine corner binds on the sleeve fillet); both 6.5 mm
   fingers free (clear the 0.8 mm slots with a blade); the hook ramps face forward (away from the flange); the piston
   slides the full 38 mm. Knife the replace groove all round the tine 3 mm aft of the rim position (35 mm from the flange).
3. **Weigh**: shoe ≤ 9.8 g bare, piston ≤ 3.4 g. Heavier: check the extrusion multiplier before printing more.
4. **Cut the cartridges**: from 2 in F-400 cut 14.5 × 9.8 mm sticks with the stick axis **through the board
   thickness**, **35.0 mm** long, **3 per foot**. Type U (`GER-003`): solid, orange stripe. Type L (`GER-008`): twist
   the sharpened 5/32 in brass tube through each segment along its axis, push the plug out, blue stripe. Check: square
   ends; bore centred ± 0.5 mm.
4a. **Pre-crush every segment 1 mm** (CR-C5-10): stand it on end on the drill-press table under a flat 20 × 15 mm
   block, set the depth stop, press once to 34.0 mm, release. Check: 34.0 ± 0.3 mm after 1 min (102.0 mm per foot
   incl. 0.5 mm preload). Make the field-kit cartridges (16 + 16 sets of three) the same way.
5. **Glue the cartridges into the pistons** (`E-GER-09…12`): orange piston + type U, blue piston + type L only. Two
   drops of foam-safe CA on the piston floor, first segment home, one drop between segments. 2 min.
6. **Pads** (`GER-004`): cut 19.1 × 17.8 mm, round the corners 1 mm; IPA on the flange; press 30 s.
7. **Dry-fit each shoe on its fin tip**: sleeve floor on the step, back wall against the step front and the two strip
   ends, cheeks over the strip ends, legs on both faces, sleeve end pointing aft past the TE. Scuff the board paper
   under the 7 mm legs (220 grit, not through).
8. **Bond the shoes** (`E-GER-01…04`): epoxy + silica on the legs, floor, back-wall face and cheeks; slide on; align the
   sleeve axis with the wing TE line using a straight edge; wipe the bore clean. Tape; 24 h before landing loads.
9. **Fit the inserts** (`E-GER-05…08`): orange up (UR, UL), blue down (LR, LL). Push in until both hooks click into
   their windows. Check: flange-to-rim gap 38 ± 1 mm on all four; the four pads lie in one plane (no rocking).
10. **Corner caps** (`GER-007`, TPU): push over each wingtip TE corner outboard of the elevon end (do not touch the
    elevon); two wraps of filament tape over the legs. Nothing on the lower surface at \|y\| 0.45 m (CG-jig patch).
11. **Record**: weigh 4 feet + 2 caps (59.1 g expected, ≤ 60 g allocation; tell A3); photograph each foot.

## Field replacement (≤ 10 min, 1.5 mm hex key)

| # | Action | Check |
|---|---|---|
| 1 | Replace groove inside the rim → replace; visible → fly | groove at the rim = 3 mm used (C5 pair-first stroke + 3 mm guard left) |
| 2 | Hooks in their windows: push each hook in with the hex key, pull the insert aft. Hooks not visible (set > 1 mm): pull the insert aft until both hooks snap into the windows, then release them | insert comes out with its cartridge |
| 3 | Push in a spare **of the same colour** (orange up, blue down) until both click | 38 mm gap; pads level |
| 4 | Shoe cracked (rim, window, roof) or bond lifting → ground the aircraft; razor-saw the shoe off, sand, step 8, 24 h | no crack |

Normal landings at `Q_LAND_SPEED` 50 cm/s crush ≈ 1.3 mm each; at ≤ 30 cm/s nothing (`CL-D5-V-NO-SET`, CR-D5-21).
Check the groove after every landing (C5 S7).

## Animation

One 4 s clip for the build manual (J3): the orange insert sliding into the shoe and clicking, then the crush stroke
(`E-GER-05` slider 0 → −38 mm) with the hook camming under the window edge and the flange stopping on the rim; the fin
ghosted, the insert highlighted.
