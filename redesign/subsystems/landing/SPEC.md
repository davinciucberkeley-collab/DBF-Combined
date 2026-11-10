# Landing feet (GER)

Status: `MODELLED` (D5, revision D5-R3, 2026-11-09, params A1-R3). Answers CR-A1-34 / D-30. Calc and claims:
`team/D5/feet_calc.py`; CAD: `fusion/landing.py`; parts and edges: `team/D5/make_interfaces.py`.

## Purpose

Four crushable feet on the half-fin TE tips and two wingtip corner caps. Each foot stands the aircraft, takes a
1.5 m/s hard landing at n ≤ 6 with C5's pair-first tilt, keeps the wing TE ≥ 10 mm off the ground at full stroke,
and is repaired at the field by swapping one colour-coded insert without tools.

| Part | What | Life |
|---|---|---|
| `GER-001` shoe | PETG sleeve 19.8 × 17.1 mm on a 9.5 mm step in the half-fin square tip; back wall on the step front and strip ends; legs on both faces; collar cheeks over both edge-strip ends; rim at the sleeve end | permanent |
| `GER-002` piston | PETG tine 17.8 × 15.1 mm, two 6.5 mm snap fingers, stop flange, inspection windows; **orange** UR/UL, **blue** LR/LL | insert |
| `GER-003` / `GER-008` cartridge | XPS F-250 16 × 13.3 mm, 2 × 44.5 mm; type U solid (upper), type L with a 6.35 mm bore (lower) | insert, consumable |
| `GER-004` pad | 1/16 in neoprene, adhesive back, on the flange; outboard edge at z ±0.219 m | insert |
| `GER-007` corner cap | TPU U-cap on the fixed wingtip TE corner, y 0.5615–0.575 m + tip wall, taped | replace when worn |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Foot beyond TE / stroke (flange to rim) / usable (−3 mm guard) | 48 / 38 / 35 | mm | `CL-D5-STROKE-AVAIL`, `-STROKE-USABLE` | `UNVERIFIED` |
| C5 pair-first stroke vs usable | 31.5 vs 35 | mm | `CL-C5-DROP-PAIR-PITCH` | `UNVERIFIED` |
| Plateau upper / lower / mean; bias | 36.6 / 31.2 / 33.9; ×1.080 (target 1.077) | N; — | `CL-D5-F-PLATEAU-UPPER/-LOWER`, `-BIAS-UPPER` | `UNVERIFIED` (coupon) |
| Peak upper foot, limit / ultimate (C1 R3 bound 41.2 / 60.8) | 40.3 / 60.4 | N | `CL-D5-F-PEAK-UPPER`, `-F-ULT-UPPER` | `UNVERIFIED` (+2 %) |
| Level landing: stroke / n / η | 25.4 mm / 5.85 / 0.83 | — | `CL-D5-STROKE-USED`, `-N-LAND`, `-ETA` | `UNVERIFIED` |
| Wing TE above ground at full stroke | 10 | mm | `CL-D5-TE-CLEAR-CRUSHED` (≥ 10) | `UNVERIFIED` |
| Tip-over pivot z / angle at target / worst flying CG | 0.218 / 34.7 / 30.6 | m / ° / ° | `CL-D5-CONTACT-Z`, `-TIPOVER-NARROW`, `-CORNER` | `UNVERIFIED` |
| Fin step: \|z\| / from x / depth | 0.2005 / 0.2746 / 9.5 | m / m / mm | `CL-D5-FIN-STEP-Z/-X/-DEPTH` (CR-D5-11) | `PROPOSED` |
| Shoe bond area / RF at C6's 0.10 MPa, 87.4 N design | 1 621 / 1.85 | mm² / — | `CL-D5-BOND-AREA`, `-BOND-SF` | `UNVERIFIED` |
| Flange SF / rim SF (side load 30.5 N ult) / tine SF | 2.52 / 1.24 / 3.52 | — | `CL-D5-FLANGE-SF`, `-SIDE-RIM-SF`, `-SIDE-TINE-SF` | `UNVERIFIED` |
| Snap finger strain / length (C6 ≥ 6.0 mm, ≤ 2 %) | 1.7 % / 6.5 mm | — / mm | `CL-D5-SNAP-STRAIN`, `-SNAP-LEN` | `CHECKED` |
| Set per 0.5 m/s landing / landings per cartridge | 0.17 / 20 | mm / — | `CL-D5-SET-NORMAL`, `-LANDINGS-PER-CART` | `UNVERIFIED` |
| Insert swap | 3 | min | `CL-D5-REPLACE-TIME` (≤ 10) | `PROPOSED` |

## Interfaces

| Edge | Between | How | Registered |
|---|---|---|---|
| `E-GER-01…04` | shoe ↔ `FIN-001-UR/UL/LR/LL` | 30 min epoxy + silica: floor on the step, legs, back wall, cheeks; 1 621 mm² | contact; fins acknowledges |
| `E-GER-05…08` | piston ↔ shoe | `CT-GER-CRUSH-SLIDE`: 0.2 mm/side, 2 snap fingers, flange stops on the rim | slider X, −38…0 mm |
| `E-GER-09…12` | cartridge (`GER-003`/`GER-008`) ↔ piston | `CT-CA` foam-safe CA | contact |
| `E-GER-13…16` | pad ↔ flange | `CT-GER-PSA` | contact |
| `E-GER-17…20` | cartridge ↔ shoe back wall | `CT-GER-END-BEAR`, 0.5 mm preload | contact |
| `E-GER-21/22` | cap ↔ `WNG-001` | `CT-GER-CAP-TAPE`, 2 wraps 12 mm filament tape | contact (waits for D1) |
| `KO-GROUND` | only `GER-004-*` reach x 0.368 | keep-out | `k9.hover_ground` |

No fasteners: the field joint is the snap fit. Load path: pad → flange → cartridge → back wall → step, legs → fin.
Nothing at the CG-jig patch (\|y\| 0.45, lower surface); the caps start at \|y\| 0.5615.

## Mass budget

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Shoe / piston / cartridge U, L / pad / cap | 5.77 / 3.05 / 0.62, 0.53 / 0.75 / 0.73 | g `EST` | `CALC-D5-MASS` (CAD volumes) | `UNVERIFIED` |
| Foot upper / lower | 10.19 / 10.11 | g `EST` | `CL-D5-MASS-FOOT` | `UNVERIFIED` |
| Landing (4 feet + 2 caps) / allocation / margin | 42.05 / 43 / 0.95 | g | `CL-D5-MASS-TOTAL` | `UNVERIFIED` |

## Open issues

- The step in the half-fin tip (9.5 × 45.4 mm) and the 45.4 mm square tip are D3's cut (CR-D5-11); until then the CAD shoe overlaps the fin board.
- Upper-foot peak 40.3 N sits 2 % inside C1's R3 bound 41.2 N; C1 to confirm the per-type split (CR-D5-14).
- Rim SF 1.24 rests on a beam model of a printed lip (`T-D5-SIDE`); plateau rests on the datasheet (`T-D5-COUPON`).
- Type-L bias by a bored cartridge: bias error 0.3 %, U/L ratio 1.175 vs 1.167; C5 confirms (CR-D5-15).
- Mass margin 0.95 g: no third perimeter outside the rim.

## How to verify

| Check | How | Who |
|---|---|---|
| Numbers | `python -I redesign/team/D5/feet_calc.py` (asserts CAD volumes = calc) | anyone |
| CAD | `python -I redesign/fusion/check.py`; Fusion: BuildAll, slide E-GER-05 to −38 mm | A5 |
| Crush, bias | `T-D5-COUPON` both types; `T-C5-FOOT-RIG`, `T-C5-AIRCRAFT-DROP` | H1, C5 |
| Strength | `T-D5-PROOF` (88 N along x), `T-D5-SIDE` (32 N sideways) | H1, C6 |
| Stance, field | tilt board ≥ 30°; `T-D5-PAD-MU` ≥ 0.7; `T-D5-REPLACE` ≤ 10 min; weigh 4 feet + 2 caps ≤ 43 g | C5, H1, H2, A3 |
