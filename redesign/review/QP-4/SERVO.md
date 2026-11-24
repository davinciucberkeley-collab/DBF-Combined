# QP-4 elevon servo check (D6 + I1), concept A, 2026-11-15

Result: the ES3352HV (BOM M01) FAILS the 1.5x torque factor at the FC servo rail. Replaced by the EMAX ES3054HV. `EST` estimate, `CALC` computed, `SPEC` maker page. No git.

## 1. Required torque
Hinge moment re-derived from STRUCTURES-R / iter3_run.md inputs (elevon y 0.04-0.34, chord 61.2 mm, area 184 cm2, +-20 deg, VD 24 m/s, q = 0.5 x 1.225 x 24^2 = 353 Pa):
- q S c = 353 x 0.0184 x 0.0612 = 0.397 N m. The 0.375 N m/rad stiffness from FLUTTER.md implies Ch_delta = 0.94 /rad. That is high (thin-airfoil flap theory for a 0.25 c flap gives about 0.6-0.7, less at this finite span), so it is conservative.
- 0.375 x 0.349 rad = 0.131; alpha term 0.15 x 0.244 x 0.397 = 0.015; total **0.146 N m** (`CALC`, reproduces STRUCTURES-R). Kept: no reason to lower it.
- Required stall torque = 1.5 x 0.146 = **0.219 N m = 2.23 kgf cm** (A-P11 / REQUIREMENTS factor 1.5). This assumes servo arm = horn arm (12 mm); a servo arm longer than the horn raises the rod force and lowers the margin, so keep the arm <= the horn.

## 2. Rail voltage
Holybro Kakute F405 Wing Mini: servo BEC "5.3 V default / 7.2 V selectable / 3 A continuous (4.8 A peak)" (SPEC, https://www.readymaderc.com/products/details/87184-holybro-kakute-f405-wing-mini-flight-controller, 2026-11-15). Consequences:
- At the default 5.3 V the ES3352HV is **outside its 6.0-8.4 V rating**.
- The 7.2 V jumper must be set for any HV servo (action: add to the build checklist and A.param/FOLDIN notes). Servo supply is the FC rail, not the main pack.

## 3. Current servo (ES3352HV) at the rail
SPEC (https://www.readymaderc.com/products/details/85976-emax-es3352-hv-high-voltage-12-4g-metal-gear-dual-bearing-servo, 2026-11-15): 1.7 kgf cm at 6.0 V, 2.4 at 8.4 V; 12 g; 4 metal + 1 plastic gear; 2BB; 23.3 x 9.45 x 26.
| Rail | Stall | N m | Margin on 0.146 | vs 1.5 |
|---|---|---|---|---|
| 5.3 V (default) | out of spec | - | - | FAIL |
| 6.0 V | 1.7 kgf cm | 0.167 | 1.14 | FAIL |
| 7.2 V (linear interp, `EST`) | 2.05 | 0.201 | 1.38 | **FAIL** (needs 0.219) |
| 8.4 V (not available from this FC) | 2.4 | 0.235 | 1.61 | pass |
The "0.17-0.24" quoted in STRUCTURES-R is the 6 V to 8.4 V range, and the FC cannot supply 8.4 V.

## 4. Replacement
Candidates read on the RMRC servo collection (2026-11-15), all in stock with metal gears: ES3054HV $13.99 (only one that passes), ES08MA II HV $9.99 (12 g, torque not stated, no pass shown), ES3059MD $6.99 (2.1 kgf cm at 6 V, 4.8-6 V only, fails). EMAX ES09MD HV (13.5 g, 2.3 kgf cm at 6 V, 3.1 at 8.4 V, 2.7 at 7.2 V = 0.265 N m) passes but is BACKORDERED (search result, RMRC, 2026-11-15; page not opened).

**Pick: EMAX ES3054HV** (https://www.readymaderc.com/products/details/85975-emax-es3054-hv-high-voltage-17g-metal-gear-digital-servo, read 2026-11-15)
- $13.99 each (cheaper than the $15.99 ES3352HV), In Stock.
- 3.4 kgf cm at 6.0 V, 4.7 at 8.4 V; 7.2 V interp 4.05 kgf cm = **0.397 N m** (`EST`): 1.8x the 0.219 required, 2.7x the hinge moment. Passes even at 6.0 V (0.333 N m).
- Metal gears, 2BB, 0.13 s/60 deg at 6 V, running current 350-400 mA no load (2 flight servos about 0.8 A against the 3 A BEC; stall current not listed: "-", measure at the bench for A-P18).
- Mass 20.5 +-0.5 g (page title says 17 g, spec table 20.5; the table is used).
- Size 28.4 x 13.0 x about 26.7 mm (servodatabase.com/servo/emax/es3054hv and getfpv.com, 2026-11-15; the RMRC page gives no drawing, the sources disagree on height).
- K >= 1 N m/rad and free play <= 1 deg: not in any spec or review found ("-"). Metal gears and dual bearings are the best available evidence. Verify with FLUTTER step 5 (spring-scale test on the built wing) before first flight; the 6 mm of extra arm length do not matter, the pushrod and horn do.
- Fit (`EST`, CAD not re-run): a_model.py pocket is x 125.5-165.5, case x 126.85-150.15 (9.45 mm thick, 26 mm span). The new case is 28.4 chordwise (+5 mm, ends at about 155 mm, inside the pocket and clear of the arm 140.5-159.5 only if the spline stays at x about 140: check) and 13 mm thick (+3.6 mm: top z 8.2 -> 11.8 mm). Wing section at x 0.14 with 9.5 % t/c on a 245-300 mm chord is about 18-23 mm, so it fits with the upper-skin pocket opening. **Action: update SV_X0/X1, SV_Z1 and the 'Servo ES3352HV' mass 12 -> 20.5 g in a_model.py, re-run the collision gate (owner: CAD).**

## 5. BOM and G7
M01 changed in `qp/A/BOM-A.csv`: ES3054HV, qty 3 (2 + 1 spare), $13.99. `python -I bom_a.py`:
| | before (ES3352HV) | after |
|---|---|---|
| Goods | 1,243.53 | 1,237.53 |
| Total (spend + crash reserve) | 1,760.76 | **1,751.94** |
| Margin to $2,000 | 239.24 | 248.06 |
| +30 % on unverified: total / margin | 1,873.64 / +126.36 | 1,864.82 / **+135.18** |
G7 (total <= $1,800 and +30 % margin >= $100): **PASS** (before and after). bom_a.py unchanged.

## 6. Mass and CG
- +8.5 g per servo; 2 flight servos **+17.0 g** (the spare is not flown). Predicted mass 1,396 -> 1,413 g (MASS-GATE s3): headroom to the gate (MASS-GATE s3) 104 -> 87 g; to the 1.44 kg target 44 -> 27 g. The structure freeze (473 g) is untouched; the servo line is outside it, but it eats 17 of the 44 g held for first-build adders (glue, wire, CG lead), together with the pending +21 g elevon/lead waiver (STRUCTURES-R), which would leave 6 g. Flag for the board.
- CG: servos at x about 139 mm aft of the wing leading edge, y +-0.20 (symmetric, no lateral shift). dCG = 17 x (139 - 16.2) / 1,413 = **+1.5 mm aft** (`EST`; CAD CG 16.2 mm -> 17.7 mm). That moves toward the 20-26 mm target (A-P4) and costs 0.6 % of chord in SM (10.0 % -> 9.4 % on NP 40.7 mm); the pack slot (+-10 mm) trims the rest. Recompute with the CAD mass table (`sitl/cad_mass.py`) after the part swap.

## Open items
1. Set the Kakute servo rail jumper to 7.2 V (default 5.3 V is below the servo's 6.0 V minimum).
2. CAD part swap and collision re-run.
3. Measure K and free play (FLUTTER step 5); stall current for BEC sizing.
4. Board: mass (+17 g servos, +21 g elevon waiver) against the 44 g headroom.
