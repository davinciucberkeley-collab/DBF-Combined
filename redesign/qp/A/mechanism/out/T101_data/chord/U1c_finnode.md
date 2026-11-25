# T-101 U1c: fin-node bulkhead / plate lengths restored (chord 0.30 c)

Rung used: **1 (remove) for the bulkheads**, **2 (modify) for the upper plates only**. Rungs 3 and 4 not used.

## 1. Geometry (from the amodel constants; script output in `U1c_clearance.txt`)

- Hinge x XH = 171.50 mm, hinge axis z 2.060 mm. Damper housing: radius 6.35 mm, y 350.7..369.0 mm (end disc last 0.8 mm); stator pin, rotor sleeve (r 5.25) and flange (r 5.6) lie at y < 369.0. Core notch (a void cut in the core): x 164.75..172.5, y 349.2..369.4, z -4.69..3.06 (wing.py ~1109).
- Elevon tip face y 349.5 (ELEV_Y1 350 - GAP_Y 0.5); the elevon rotates about the Y axis, so its swept envelope stays at y <= 349.5 at any angle (+-21 deg).
- Fin bulkheads FIN-005: 0.5 mm sheets at |y| 369.5..370.0 (inner) and 396.0..396.5 (outer), x 0..176, z = cell (zl..zu). The inner bulkhead is **0.5 mm outboard of the housing end disc (369.0) in y**: no y-z overlap with any damper part, at any x. The overlap that U1 saw was only in x (176 > housing front 165.15), but the two never share a y band. So the bulkheads never needed cutting.
- Plates FIN-009: x 58..168, |y - 383| <= 20 mm -> y 363..403. Upper plate z about +0.9..+3.1 mm (under the skin) lies inside the housing z range (-4.29..8.41) and y 363..369 overlaps the housing y 350.7..369.0, and x 165.15..168 is inside the housing front: **a real overlap in the upper plate** (3.6 mm from the axis at x 168, inside r 6.35). The lower plate is at z about -9..-7.6, 9.6 mm below the axis: clear.

Ladder: rung 1 clears the bulkheads (restored FNB_X1 = 0.176, comment only, nothing cut). Rung 1 does not clear the upper plates (real overlap), so rung 2 for them.

## 2. Changes

- `redesign/qp/A/cad/amodel/wing.py`
  - line 101: `FNB_X1 = 0.176` (was `XH - 0.00775` = 163.75 mm).
  - line 103: `FNP_X = (0.058, 0.168)` (was `(0.058, FNB_X1)`).
  - lines 104-105 (new): `FNP_REL = (XH - 0.00635 - 0.0004 - 0.0005, 0.3620, 0.3699)` and `FNP_REL_Z = 0.0050`.
  - line 349 (new): plate mass less the relief (`pl -= ...`).
  - line ~1233 (new): `fp_.cut_box(...)` relief in the upper plate, before the mirror to FIN-009-L (cuts follow the mirror).
  - line 1013: edge text "x 70.5..176 (restored in U1c)".
- `redesign/qp/A/cad/a_build_steps.py`: lines 78 (bulkheads LE to x 176, plates 110 x 40, x 58-168, with the relief text), 361 (flox fillet and straps x 70.5-176), 393 / 395 / 405 / 406 / 408 (lead 14.0 g, strip 10 x 1.17 x 106 mm), and 399 / 403 (stale "15.6 g", "16.1 g": strip 14.0 g, WNG-007 14.5 g, as in wing.py line 936; same stale family, edited with the rest). Blister lines (x 70.5 to 164.0 mm) unchanged: RIBF_X1 = XH - 7.5 mm is the rib fairing, not the bond.
- Regenerated: `redesign/qp/A/BUILD-GUIDE-A.md`, `cad/model/*/interfaces.json`, `cad/out/STOP_CHECK.md`, `sitl/cad_mass.json`, `cad/out/_job.json` (by the pass-check commands).

Relief in the upper plate (each side, mirrored): x 164.25..168 (3.75 mm), y 363..369.9 (6.9 mm) = 25.9 mm2 plan, 0.5 mm sheet at 1.6 g/cm3 -> 0.02 g removed per plate (0.04 g aircraft). x0 = 0.5 mm ahead of the notch front (164.75), 0.9 mm ahead of the housing; y1 = 0.5 mm outboard of the notch end (369.4). The plate keeps full length 58..168 along y >= 369.9 (the bond zone of the rib flank, |y| 370.5+, and the whole plate outboard).

## 3. Clearances (min mm; `U1c_clearance.txt`, box / cylinder extents from the constants)

| Solid | housing / end disc / pin | rotor sleeve | rotor flange | core notch (void) | elevon tip envelope |
|---|---|---|---|---|---|
| bulkhead inner (369.5..370.0, x 0..176) | 0.500 | 2.0 | 19.0 | **0.100** | 20.0 |
| bulkhead outer | 27.0 | 28.5 | 45.5 | 26.6 | 46.5 |
| upper plate, relieved part (y 363..369.9, x 58..164.25) | 0.911 | 2.011 | 12.6 | 0.500 | 15.3 |
| upper plate, y >= 369.9 | 0.900 | 2.4 | 19.4 | 0.500 | 20.7 |
| lower plate | 4.605 | 5.7 | 13.6 | 3.6 | 13.9 |

Minimum against the damper parts and elevon tip: 0.500 mm (bulkhead inner to end disc: pure y gap, same as before the chord change).

**Exception to flag:** the inner bulkhead is 0.1 mm from the notch box in y (notch end 369.4, bulkhead 369.5). The notch is a void in the core, not a solid; nothing is interpenetrated, and this y gap is geometry that existed before U1 (the old bulkhead stopped 1.0 mm short of the old notch in x, so the gap was never tested). It cannot be raised without cutting the bulkhead over the notch z-band (-4.7..3.1 mm, x 164.75+), which would remove the cell web and the bond line, or moving RIB_Y / the notch (design values, not touched). Conductor to accept or decide.

## 4. Mass and CG (cad_mass.json)

| State | mass_basic_kg | cg_x_m |
|---|---|---|
| Before (U1 + U2, shortened) | 1.64048 | 0.021413 |
| After (restored, relief) | 1.64288 | 0.021567 |

Delta +2.40 g, CG +0.154 mm aft.

## 5. Pass check

- Constants print: FNB_X1 = 0.176, FNP_X = (0.058, 0.168), min clearance 0.500 mm (>= 0.5), except the void-notch 0.1 mm above. `U1c_clearance.txt`.
- `python -I redesign/qp/A/cad/build_a.py`: exit 1, `check: FAIL (10 modules, 1 errors, 0 warnings)`; the one error is `graph:mass TOTAL aircraft 1643 g > limit 1500 g` (pre-existing). `U1c_build_a.txt`.
- `python -I redesign/qp/A/cad/stop_check.py`: exit 0, STOP_CHECK.md "Cap clearance ... **PASS**". `U1c_stop_check.txt`.
- `python -I redesign/qp/A/sitl/cad_mass.py`: exit 0. `U1c_cad_mass.txt`.
- `python -I redesign/qp/A/make_build_guide_a.py`: exit 0. `U1c_build_guide.txt`.
- collide_a.py, a_assembly.py, GLB export not run (per the brief): the relief and the restored lengths are not 3-D-gate verified; they need the conductor's collide run.

## 6. Stale records now consistent again

The strength records at x 176 (T077p8_data, T083_data, TEST-PLAN-O4B.md) match the restored 105.5 mm bond; the U1 note of a 93.25 mm bond no longer applies. `redesign/qp/A/mechanism/out/T101_data/chord/U1_cad.md` s2 / s5 / s7 / s8 still carry the 163.75 values (U1 record, superseded by this file).
