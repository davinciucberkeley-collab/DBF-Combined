# Landing feet (GER)

Status: `MODELLED` (D5, revision D5-R8, 2026-11-13). R8 (CR-H1-22, side-load margin): sleeve inside fillets R 1.0 → 2.0,
rim y sides 3.4 → 4.6 mm, rim floor side 3.4 → 0.4 mm, tine chamfers 1.0 → 1.4 mm, tine rails 2.0 → 2.5 mm; sleeve
section, roof rim, lip and fin step unchanged; shoe RF 1.06 → 1.27 at the 59.25 N ultimate side load (D5 FEA, three
meshes), landing 59.08 → 58.94 g. R7 (D-75, D-76, D-78; BR-00, BR-01 / SW-02): the cartridges
move to FOAMULAR 400 so the section, sleeve and tine shrink (landing 69.9 → 59.1 g), and the half-fin tip is cut where
this stack puts the step (x 0.2614), which D3 now copies exactly. R6 (D-65, CR-C5-18): sleeve end sized by FEA for
C5's 59.0 N ultimate side load, 25 mm engagement. Calc and claims: `team/D5/feet_calc.py`; FEA:
`team/D5/sim/fea_shoe_d5.py`; CAD: `fusion/landing.py`; parts and edges: `team/D5/make_interfaces.py`.

## Purpose

Four crushable feet on the half-fin TE tips and two wingtip corner caps. Each foot stands the aircraft, takes C5's
design touchdown (1.2 m/s sink at ≤ 10° of combined tilt in any direction, D-65) inside its 35 mm usable stroke at
n ≤ 6.6, survives C5's 39.5 N limit / 59.25 N ultimate pad side load, keeps the wing TE ≥ 10 mm off the ground at
full stroke, and is repaired at the field by swapping one colour-coded insert without tools.

| Part | What | Life |
|---|---|---|
| `GER-001` shoe | PETG sleeve 19.1 × 14.4 mm, 1.2 mm walls, R 2.0 inside fillets, rim at the open end 4.6 mm on the y sides / 3.4 mm roof / 0.4 mm floor, 3 mm snap windows; floor on a 9.0 mm step in the half-fin square tip; back wall on the step front and strip ends; 7 mm legs on both faces; 8 mm collar cheeks over both edge-strip ends | permanent |
| `GER-002` piston | PETG tine 16.3 × 11.6 mm (0.8 mm walls, 1.4 mm corner chamfers, 2.5 mm rails beside the inspection windows), two 6.5 mm snap fingers, 1.8 mm stop flange, 25 mm engaged; **orange** UR/UL, **blue** LR/LL | insert |
| `GER-003` / `GER-008` cartridge | **FOAMULAR 400** XPS 14.5 × 9.8 mm, 3 × 34.0 mm (cut 35.0, each pre-crushed 1 mm); type U solid (upper), type L with a 3.97 mm (5/32 in) bore (lower) | insert, consumable |
| `GER-004` pad | 1/16 in neoprene, adhesive back, 19.1 × 17.8 mm on the flange; outboard edge at z ±0.219 m | insert |
| `GER-007` corner cap | TPU U-cap on the fixed wingtip TE corner, y 0.5615–0.575 m + tip wall, taped | replace when worn |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Foot beyond TE / stroke (flange to rim) / usable (−3 mm guard) | 48 / 38 / 35 | mm | `CL-D5-STROKE-AVAIL`, `-STROKE-USABLE` | `UNVERIFIED` |
| C5 3-D sim worst stroke, 1.2 m/s, 10° any direction, gate mass | 35.0 vs 35 | mm | `CL-C5-SIM3D-STROKE` | `UNVERIFIED` |
| Plateau upper / lower / mean (C5-R3: 39.4 / 35.6 / 37.5) | 39.2 / 35.8 / 37.49 | N | `CL-D5-F-PLATEAU-UPPER/-LOWER`, `-F-MEAN-ERR` 0.04 % | `UNVERIFIED` (coupon) |
| Bias upper (C5 target 1.05) | 1.046 | — | `CL-D5-BIAS-UPPER`, `-BIAS-ERR` 0.0045 ≤ 0.01 | `UNVERIFIED` |
| Peak upper foot, limit / ultimate | 39.2 / 58.8 | N | `CL-D5-F-PEAK-UPPER`, `-F-ULT-UPPER` | `UNVERIFIED` |
| Level landing at 1.2 m/s: stroke / n / η | 15.9 mm / 5.88 / 0.84 | — | `CL-D5-STROKE-USED`, `-N-LAND`, `-ETA` | `UNVERIFIED` |
| Permanent set per 0.5 m/s landing / sink with no set | 1.15 mm / 0.34 m/s | — | `CL-D5-SET-NORMAL`, `-V-NO-SET` | `UNVERIFIED` |
| Wing TE above ground at full stroke | 10 | mm | `CL-D5-TE-CLEAR-CRUSHED` (≥ 10) | `UNVERIFIED` |
| Tip-over at target / worst flying CG | 32.0 / 31.0 | ° | `CL-D5-TIPOVER-NARROW`, `-CORNER` | `UNVERIFIED` |
| **Fin step: front x / \|z\| / depth** (D3 copies these, D-75) | **0.2614 / 0.2010 / 9.0** | m / m / mm | `CL-D5-FIN-STEP-X/-Z/-DEPTH`; D3 `CL-D3-TIP-STEP-MISMATCH` 0 | `PROPOSED` |
| Shoe length on the fin (step front to TE) / cheeks from | 58.6 / x 0.2536 | mm / m | `CL-D5-LEG-LEN`; fins `tip_clear_x_m` | `PROPOSED` |
| Shoe bond area / RF at C6's 0.10 MPa, 114.9 N design (C1 80.0 N × 1.4375) | 1 657 / 1.44 | mm² / — | `CL-D5-BOND-AREA`, `-BOND-SF` | `UNVERIFIED` |
| Sleeve end RF at 59.25 N ult side load (D5 FEA, finest mesh h 0.2: +y 31.6 MPa at the inboard window corner, rim 30.4; +z 24.2 MPa at h 0.3; vs 40 MPa). R7 was 1.06 (+y 37.6 MPa at the rim) | 1.27 | — | `CL-D5-SIDE-RIM-SF` (`ASM-D5-FEA-SHOE-K` 0.533 MPa/N) | `UNVERIFIED` |
| Mesh study, +y governing, h 0.4 / 0.3 / 0.2 mm: rim 28.7 / 30.1 / 30.4 MPa (converging), window corner 28.3 / 28.9 / 31.6 MPa (sharp re-entrant corner, grows with refinement) | — | MPa | `sim/out/fea_d5_h{400,300,200}_py.json` | `MODELLED` |
| Tine SF (R8: windowed section at F (a − 3 mm), full section at F a) / flange SF (C1 80.0 N bound) | 1.23 / 1.07 | — | `CL-D5-SIDE-TINE-SF`, `-FLANGE-SF` | `UNVERIFIED` |
| Tine chamfer clear of the R 2.0 sleeve fillet (0.2 mm slide clearance) | 0.16 | mm | `CL-D5-FILLET-CLEAR` (≥ 0.10) | `PROPOSED` |
| Snap finger strain / length (C6: ≥ 6.0 mm, ≤ 2 %) | 1.7 % / 6.5 mm | — / mm | `CL-D5-SNAP-STRAIN`, `-SNAP-LEN` | `CHECKED` |
| Insert swap | 3 | min | `CL-D5-REPLACE-TIME` (≤ 10) | `PROPOSED` |

## Interfaces

| Edge | Between | How | Registered |
|---|---|---|---|
| `E-GER-01…04` | shoe ↔ `FIN-001-UR/UL/LR/LL` | 30 min epoxy + silica: floor on the step, 7 mm legs, back wall, cheeks; 1 657 mm² | contact; fins acknowledges |
| `E-GER-05…08` | piston ↔ shoe | `CT-GER-CRUSH-SLIDE`: 0.2 mm/side, 2 snap fingers, flange stops on the rim | slider X, −38…0 mm |
| `E-GER-09…12` | cartridge (`GER-003`/`GER-008`) ↔ piston | `CT-CA` foam-safe CA | contact |
| `E-GER-13…16` | pad ↔ flange | `CT-GER-PSA` | contact |
| `E-GER-17…20` | cartridge ↔ shoe back wall | `CT-GER-END-BEAR`, 0.5 mm preload | contact |
| `E-GER-21/22` | cap ↔ `WNG-001` | `CT-GER-CAP-TAPE`, 2 wraps 12 mm filament tape | contact |
| `KO-GROUND` | only `GER-004-*` reach x 0.368 | keep-out | `k9.hover_ground` |

No fasteners: the field joint is the snap fit. Load path: pad → flange → cartridge → back wall → step, legs → fin.
Fin fit (D-75): the shoe floor sits 0.2 mm (glue line) above the 0.2010 step from x 0.2614 to the TE; the cheeks
(x 0.2536–0.2616) and legs straddle the board and strips outside their faces. Shoe and fin solids do not overlap
(minimum clearance 0.20 mm, checked body by body against the fins CAD on 2026-11-11). Ground items (`GER-005`,
`-006`, `-009…013`) are `"flight": false` and modelled as one unit per kit line at y 0.85 m.

## Mass budget

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Shoe (with 0.35 g epoxy) / piston / cartridge U, L / pad / cap | 9.98 / 3.19 / 0.51, 0.47 / 0.71 / 0.73 | g `EST` | `CALC-D5-MASS` (CAD volumes) | `UNVERIFIED` |
| Foot upper / lower · insert upper | 14.39 / 14.35 · 4.41 | g `EST` | `CL-D5-MASS-FOOT`, `-MASS-INSERT` | `UNVERIFIED` |
| Landing (4 feet + 2 caps) / allocation / margin | 58.94 / 60 / 1.06 | g | `CL-D5-MASS-TOTAL` (D-78: 48 → 60, from power) | `UNVERIFIED` |
| R8 change against R7: shoe +0.05 each (R 2.0 fillets and 4.6 mm y-side rim, less the floor-side rim cut to 0.4 mm); piston −0.09 each (1.4 mm chamfers, less the 2.5 mm rails) | −0.14 | g | `CALC-D5-MASS` R7 59.08 → R8 58.94 | `UNVERIFIED` |
| R6 for comparison (F-250, 25.5 × 15.6 mm sleeve) | 69.9 | g | — | superseded |

Where the mass is: four shoes 39.7 g (sleeve walls ~60 %, rim ~15 %), four pistons 13.1 g, cartridges 2.0 g, pads
2.8 g, caps 1.5 g. The 59.25 N side load sets the sleeve wall and rim (FEA sweep: 0.8 and 1.0 mm walls fail +y at
60 / 52 MPa), and the 38 mm stroke plus 25 mm engagement set the length (C5's 3-D sim already uses all 35 mm), so
48 g is not reachable inside this concept. The next lever is the side-load fuse (SW-03 / BR-09): a foot that lets go
at a set load would let the sleeve return toward 0.8 mm walls (est. −8 g), but C1/C4/C6 must size the fin to the
capped load first.

## Open issues

- **F-400 is not yet bought or tested.** `T-D5-COUPON` on F-400 (U 38.2–40.2 N, L 34.6–36.3 N, U/L 1.09–1.14) gates
  the shoe print. If F-400 cannot be had, the fallback is R6's F-250 section with the R6 shoe (+11 g, CG +1.1 mm aft).
  I1 to add one 2 in F-400 board (or an offcut from an insulation supplier) to the order (CR-D5-32).
- Each normal 0.5 m/s landing crushes 1.15 mm; at ≤ 0.3 m/s nothing (`Q_LAND_SPEED` 30 cm/s, CR-D5-21).
- Shoe RF 1.27 and tine SF 1.23 rest on a linear FEA and a beam: `T-D5-SIDE` (60 N, +y and +z) decides. The h 0.2
  peak is at the sharp inboard snap-window corner and still rises with refinement (singular); the printed corner is
  rounded by the 0.4 mm extrusion, so the rim value (30.4 MPa, converging, RF 1.32) is the better estimate. Print and
  inspect the window corners (step 1).
- C5's own shoe FEA (`CALC-C5-FEA-SHOE-D5R6`) and C4's fin-station model (CR-C6-38) were run on the R6 shoe and
  the x 0.2746 tip: both re-run on R7 (CR-D5-33).

## How to verify

| Check | How | Who |
|---|---|---|
| Numbers | `python -I redesign/team/D5/feet_calc.py` (asserts CAD volumes = calc, FEA records = drawn shoe) | anyone |
| Shoe FEA | `python -I redesign/team/D5/sim/fea_shoe_d5.py --one 0.4 +y` and `+z` (≈ 2 min each) | D5 |
| CAD | `python -I redesign/fusion/check.py`; Fusion: BuildAll, slide E-GER-05 to −38 mm | A5 |
| Crush, bias | `T-D5-COUPON` on F-400; `T-C5-AIRCRAFT-DROP` | H1, C5 |
| Strength | `T-D5-PROOF` (96 N along x), `T-D5-SIDE` (60 N sideways, +y and +z) | H1, C6 |
| Stance, field | tilt board ≥ 30°; `T-D5-PAD-MU` ≥ 0.7; `T-D5-REPLACE` ≤ 10 min; weigh 4 feet + 2 caps ≤ 60 g | C5, H1, H2, A3 |
