# T-101 U1: elevon chord fraction 0.25 -> 0.30 in the concept A CAD (both passes)

Ladder rung: **modify** (values changed in place; no part added, no mass added by design). Chord decision D-number pending (conductor). Source for the decision: `docs/audits/2026-11-23-T101-scout-trim.md` s3.3.

## 1. Files changed (U1, both passes)

- `redesign/qp/A/cad/amodel/common.py`: ELEV_FRAC.
- `redesign/qp/A/cad/amodel/wing.py`: FNB_X1, FNP_X, BAL_DZ, WNG-001 / WNG-006 masses, rib-bond note (L1010), comments on the cap cut and RIBF_X1.
- `redesign/qp/A/cad/amodel/electrical.py`: ARM_R, HORN_R text, HORN_RIB_X1 text, antenna comment, servo-arm / horn part names.
- `redesign/qp/A/cad/a_build_steps.py`: A1 text (cove foot / hinge / elevon chord), and (pass 2) the four blister lengths "x 70.5 to 176.25 mm" -> "x 70.5 to 164.0 mm" (lines 368, 376, 385, 388).
- `redesign/qp/A/drawings/core_hand.py` (pass 2): comment on line 42 only (hinge 183.75 -> 171.50).
- Regenerated (not hand edited): `redesign/qp/A/BUILD-GUIDE-A.md`, `redesign/qp/A/cad/model/*/interfaces.json`, `redesign/qp/A/cad/out/STOP_CHECK.md`, `redesign/qp/A/sitl/cad_mass.json`, `cad/out/_job.json`.
- Not mine: `redesign/qp/A/structures/landing_a.py` shows modified (T-105 LAND_TRACE `hist` argument); left alone.

## 2. Values old -> new (from the diff)

| Value | Old | New | Source |
|---|---|---|---|
| ELEV_FRAC | 0.25 | 0.30 | common.py:33 |
| XH (hinge) = C(1-ELEV_FRAC), C 245 mm | 183.75 mm | 171.50 mm | common.py:34 |
| elevon chord | 61.25 mm | 73.50 mm | C x 0.30 |
| HORN_R (rod height - hinge height) | 9.155 mm | 7.39 mm | electrical.py:655 |
| ARM_R = HORN_R / 1.077 | 8.5 mm | 6.86 mm | electrical.py:645 |
| BAL_DZ | -3.3 mm | -4.3 mm | wing.py:362 (stop_check scan) |
| FNB_X1 = XH - 7.75 mm | 176 mm | 163.75 mm | wing.py:101 |
| FNP_X end (FNP_X = (58 mm, FNB_X1)) | 168 mm | 163.75 mm | wing.py:103 |
| RIBF_X1 = XH - 7.5 mm | 176.25 mm | 164.0 mm | wing.py:829 (formula unchanged) |
| cap shell cut xcut = XH - 4.0 mm | 179.75 mm | 167.5 mm | wing.py:492 (formula unchanged) |
| WNG-001 core | 100.1 g | 97.4 g | wing.py:919 (CALC, -119.7 mm2 section x length) |
| WNG-006-R/L elevon | 6.7 g | 7.6 g | wing.py:930 (CALC +0.92 g) |
| flox bond length L = FNB_X1 - RIB_X0 (70.5) | 105.5 mm | 93.25 mm | CALC from the two lines above |

## 3. Pass-check results (final run, after pass 2)

- `python -I redesign/qp/A/cad/build_a.py`: exit 1, `check: FAIL (10 modules, 1 errors, 0 warnings)`; the one error is `graph:mass TOTAL aircraft 1632 g > limit 1500 g` (pre-existing mass-gate error). 0 other errors. Stdout `U1_build_a.txt`.
- `python -I redesign/qp/A/cad/stop_check.py`: exit 0; STOP_CHECK.md "Cap clearance >= 0.5 mm ... **PASS**" (upper 0.51 mm, lower 0.52 mm; cap x range upper 131-166, lower 135-167 mm). `U1_stop_check.txt`.
- `python -I redesign/qp/A/sitl/cad_mass.py`: exit 0. `U1_cad_mass.txt`.
- `python -I redesign/qp/A/make_build_guide_a.py`: exit 0. `U1_build_guide.txt`.
- collide_a.py, a_assembly.py and the GLB export were NOT run (per the brief).

## 4. Task 1: receiver antennas (electrical.py `rx_antenna_paths`, RX_ANT_ANG 45 deg, RX_B x1 = 109 mm, 65 mm long)

Computed from the live model (`rx_antenna_paths()`, last path point = tip), XH = 171.50 mm:

| Antenna | tip x | tip y | clearance ahead of XH (need >= 12.7) | in elevon y 40..350? | Result |
|---|---|---|---|---|---|
| 1 (outboard, -y) | 155.03 mm | -92.88 mm | 16.47 mm | yes (|y| 92.9) | OK |
| 2 (inboard, +y) | 155.03 mm | +0.88 mm | 16.47 mm | no (|y| < 40) | OK |

No change to lay angle or routing. Antennas stay on the skin, 65 mm long.

## 5. Task 2: XH-derived clearances (values from the live model)

| Name | Value | Clearance | OK? |
|---|---|---|---|
| Damper notch front x (XH - DMP_R_OUT 6.35 - 0.4 mm), wing.py:1109 | 164.75 mm | core ends at XH 171.5 mm (notch is inside the core, 0.4 mm radial margin to the housing by construction) | OK |
| Damper housing front x (XH - 6.35 mm); housing y 350.7..369.0 mm | 165.15 mm | to fin bulkhead end 163.75: 1.40 mm; notch to bulkhead end: 1.00 mm (the comment's "1 mm ahead of the notch") | OK |
| Fin bulkhead FNB_X1 | 163.75 mm | 1.00 mm ahead of the notch; 7.75 mm ahead of the hinge | OK |
| Fin-node plates end FNP_X[1] (plate y 360..400 overlaps housing y 351..369) | 163.75 mm | 1.40 mm ahead of the housing front 165.15 | OK |
| RIBF_X1 (rib fairing end) | 164.0 mm | 0.75 mm ahead of the notch (164.75); fairing |y| 369.3..396.7 (RIB_Y 383, R 13.9) vs housing end y 369.0 | OK |
| Rib groove in FIN-004 (cut from x XH to XFIN_T 294, radius 14.0 mm vs fairing R 13.9 / rib 12.5) | starts 171.5 mm | fin fairing front is at x 171.8 mm, so the groove still spans the whole fairing (starts 0.3 mm ahead of it) | OK |
| Cap shell cut xcut (XH - 4.0 mm) | 167.5 mm | 4.0 mm ahead of the hinge (as the D-194 comment); cap-to-lead / tab clearance 0.51 / 0.52 mm >= 0.5 (STOP_CHECK.md) | OK |
| Horn rib depth at HORN_RIB_X1 (XH + 55 mm = 226.5 mm) | skin-to-skin 2.260 mm; rib depth after 2 x HORN_RIB_IN (0.2 mm) = 1.860 mm | 1.860 mm > 2 x HORN_RIB_IN = 0.4 mm (and the skin depth 2.260 mm is also > 0.4 mm) | OK |

No NOT OK item; nothing modified in task 2.

## 6. Task 3: stale numbers (grep of cad/*.py, cad/amodel/*.py, drawings/core_hand.py)

Fixed (live text that described the current design): a_build_steps.py 368, 376, 385, 388 ("x 70.5 to 176.25 mm" -> "164.0 mm"; line 373 already said 164.0); core_hand.py:42 comment. Remaining hits for 183.75 / 179.25 / 61.25 / 9.155 / 8.5 mm / 6.7 g / 176 are all "was ..." history text (common.py:33, electrical.py:645/655/660, wing.py:101/490/491/919/930/1010) or unrelated ("x_A - 8.5 mm" pin insertion, wing.py:647; gen_interfaces.py:60 has no stale number). `make_build_guide_a.py` has no stale values. BUILD-GUIDE-A.md regenerated.

## 7. Task 4: mass and CG change per part

Source: `git show HEAD:redesign/qp/A/cad/model/<sub>/interfaces.json` (old) vs the current files, all 10 subsystem folders; centroid x = `cg_xyz_m[0]` (rounded to 0.1 mm in that file). Contribution = (m_new x_new - m_old x_old) / M_new; the dM term = -(M_new - M_old) x X_old / M_new (X_old from the same source).

**Observed totals now (cad_mass.json, precise centroids): mass 1640.98 -> 1632.48 g (-8.50 g); CG x 22.049 -> 20.777 mm (shift -1.272 mm).** These differ from the figures in the brief (1633.38 g, 20.688 mm, -1.36 mm): the brief's figures came from the earlier run; the files on disk now, after this pass's final rerun, give 1632.48 g and 20.777 mm. I did not find which earlier edit accounts for the 0.90 g; the part table below is built from the current files and reproduces the current cad_mass.json.

Interface-file totals: old 1640.98 g / x 21.9995 mm; new 1632.48 g / x 20.7269 mm; shift -1.2726 mm. Sum of the part contributions -1.3871 mm + dM term +0.1145 mm = **-1.2726 mm**. Against the cad_mass.json shift (-1.2724 mm) the residual is 0.0002 mm (within the 0.05 mm limit). Against the -1.36 mm in the brief the difference is 0.09 mm, explained by the 0.9 g / run difference above, not by the table.

| Part | mass old g | mass new g | x old mm | x new mm | CG contribution mm |
|---|---|---|---|---|---|
| WNG-001 wing core | 100.1 | 97.4 | 86.9 | 83.3 | -0.3585 |
| WNG-011 torsion skin ply 1 | 26.7 | 25.1 | 91.9 | 86.1 | -0.1792 |
| WNG-014-R plies 2-3 | 23.2 | 21.8 | 91.9 | 86.1 | -0.1563 |
| WNG-014-L plies 2-3 | 23.2 | 21.8 | 91.9 | 86.1 | -0.1563 |
| WNG-007-R balance lead | 10.5 | 10.5 | 166.1 | 153.9 | -0.0785 |
| WNG-007-L balance lead | 10.5 | 10.5 | 166.1 | 153.9 | -0.0785 |
| WNG-006-R elevon | 6.7 | 7.6 | 204.2 | 195.4 | +0.0716 |
| WNG-006-L elevon | 6.7 | 7.6 | 204.2 | 195.4 | +0.0716 |
| FIN-009-R in-plane plates | 9.2 | 8.5 | 113.0 | 110.9 | -0.0594 |
| FIN-009-L in-plane plates | 9.2 | 8.5 | 113.0 | 110.9 | -0.0594 |
| FIN-005-R fin bulkheads | 10.0 | 9.3 | 85.4 | 81.8 | -0.0571 |
| FIN-005-L fin bulkheads | 10.0 | 9.3 | 85.4 | 81.8 | -0.0571 |
| FIN-004-R fin fairing | 9.04 | 9.04 | 239.5 | 233.3 | -0.0343 |
| FIN-004-L fin fairing | 9.04 | 9.04 | 239.5 | 233.3 | -0.0343 |
| WNG-012 cove CF strip | 3.7 | 3.7 | 181.2 | 168.4 | -0.0290 |
| WNG-008-LU cap | 3.69 | 3.69 | 158.1 | 147.7 | -0.0235 |
| WNG-008-RU cap | 3.69 | 3.69 | 158.1 | 147.7 | -0.0235 |
| WNG-008-LL cap | 3.72 | 3.72 | 160.2 | 151.4 | -0.0201 |
| WNG-008-RL cap | 3.72 | 3.72 | 160.2 | 151.4 | -0.0201 |
| WNG-013-R centre bulkhead | 4.0 | 3.8 | 86.8 | 83.2 | -0.0190 |
| WNG-013-L centre bulkhead | 4.0 | 3.8 | 86.8 | 83.2 | -0.0190 |
| WNG-009-R damper stator | 2.0 | 2.0 | 183.7 | 171.5 | -0.0149 |
| WNG-009-L damper stator | 2.0 | 2.0 | 183.7 | 171.5 | -0.0149 |
| HRD-001 lumped hardware | 27.77 | 27.67 | 100.0 | 100.0 | -0.0061 |
| MEC-004-R control horn | 0.95 | 0.95 | 198.6 | 189.0 | -0.0056 |
| MEC-004-L control horn | 0.95 | 0.95 | 198.6 | 189.0 | -0.0056 |
| MEC-003-R pushrod | 0.97 | 0.97 | 168.8 | 161.5 | -0.0043 |
| MEC-003-L pushrod | 0.97 | 0.97 | 168.8 | 161.5 | -0.0043 |
| HWC-001 FC screws | 1.18 | 1.28 | 45.9 | 47.0 | +0.0037 |
| WNG-010-R damper rotor | 0.47 | 0.47 | 183.7 | 171.5 | -0.0035 |
| WNG-010-L damper rotor | 0.47 | 0.47 | 183.7 | 171.5 | -0.0035 |
| FIN-006-R rib fairing upper | 0.6 | 0.6 | 123.4 | 117.2 | -0.0023 |
| FIN-006-L rib fairing upper | 0.6 | 0.6 | 123.4 | 117.2 | -0.0023 |
| FIN-010-R rib fairing lower | 0.4 | 0.4 | 123.4 | 117.2 | -0.0015 |
| FIN-010-L rib fairing lower | 0.4 | 0.4 | 123.4 | 117.2 | -0.0015 |
| MEC-005-R clevis pin | 0.03 | 0.03 | 183.7 | 171.5 | -0.0002 |
| MEC-005-L clevis pin | 0.03 | 0.03 | 183.7 | 171.5 | -0.0002 |
| dM term (-8.50 g) | | | | | +0.1145 |
| **Total** | 1640.98 | 1632.48 | 21.9995 | 20.7269 | **-1.2726** |

Mass by group: core -2.7 g, skin ply 1 -1.6 g, plies 2-3 -2 x 1.4 = -2.8 g, fin plates -1.4 g, fin bulkheads -1.4 g, centre bulkheads -0.4 g, elevons +1.8 g, lumped hardware -0.10 g, FC screws +0.10 g; net -8.5 g. Lever arms: the x shift of the whole elevon / hinge group is -12.25 mm (hinge move); the core, skin and fin-node centroids move 2 to 6 mm forward as the core shrinks (aft trimmed, WNG-001 centroid -3.6 mm).

## 8. Task 5: structural side-effect list (no analysis; a later unit re-checks)

Live code that reads FNB_X1 / FNP_X (values change automatically):
- `redesign/qp/A/cad/amodel/wing.py`: 101 (FNB_X1), 103 (FNP_X), 259-260 (plate_loop), 341, 345-347 (bulkhead, flox, plate, strap masses), 954-957 (FIN-005 / FIN-009 part rows), 1229 (FIN-009 solid), 1239-1241 (FIN-005 solid), 1010 (rib-to-bulkhead flox bond edge text "x 70.5..163.75").
- `redesign/qp/A/mechanism/out/T077p8_data/t077p8_path.py`: 49 (XE = FNB_X1, node exit / bond end), 58 (PL_X = FNP_X), 88 (A_FIN cell area "to x 176"). Same pattern in the T-083 copy `redesign/qp/A/mechanism/out/T083_data/t083_path.py`: 51, 60, 90.
- `redesign/qp/A/cad/a_build_steps.py`: 78 (waterjet bulkheads step, fit text), 99 (spar passes the fin bulkheads), 354 (rib pushed between bulkheads), 361 (flox fillet x 70.5-163.75, already updated).

Records that carry the old "x 176" / bond length / cell area (not regenerated; stale until re-run):
- `redesign/qp/A/mechanism/out/T077p8_data/strength_adopted.txt`: 2 (cell area "to x 176" 3259 mm2), 23 (row R1 node exit x 176, RF 1.32), 68-70 (demand records Mx/My/Mz at x 176). Also `strength_adopted.json` 202, 640, 647, 654; `strength_table_p8.md` 22, 70-72.
- `redesign/qp/A/mechanism/out/T083_data/`: `strength_table_t083.md` 25, 82-84; `strength_all.json` 212, 640, 647, 654 (also `strength_all_rib1412.json`, `strength_z002.json`, `strength_z002_rib1412.json`, `strength_z005.json`, `strength_z010.json`, same line pairs).
- `redesign/qp/A/mechanism/out/T077_cad.md`: 690, 703 (bulkheads LE to x 176), 726 (R1 x 176, RF 1.32 PASS).
- `docs/audits/2026-11-21-saddle-loadpath.md:98` (D-226 s3 row "Rib to bulkhead": L 99.5 / 113 mm; RF 0.90 / 1.16; `My 10.00, Fz 38.3 at x 0.17`). The bond length is now 93.25 mm (was 105.5 mm in the CAD).
- `redesign/qp/A/TEST-PLAN-O4B.md`: 192 (T2 sheet note), 250-251 (cell, struts, clamps pass only at zeta <= 0.05), 275-281 (TP-13 rib-to-bulkhead bond: pass 2.21 MPa at L 99.5 mm or 1.73 MPa at L 113 mm), 265-268 (TP-12 rib torsion coupon).
- `redesign/qp/A/mechanism/out/T083_report.md:23` (row 3a "D-226 rows + strut / R4 clamp, 25x23 rib ... all pass at pad zeta <= 0.05") and 187-190 (TP-3 addition).
- Proof claims: `redesign/qp/A/proofs/claims_a2_struct.py:81` (CL-A-MS-BOND, uses FIN-005-R/L; param `struct.ms_bond_thin`, static value 0.34 at `proofs/gen_params_a.py:216`, not computed from FNB_X1); `gen_params_a.py:226` (`ms_rib_torsion` 0.60, static). Generated copies: `proofs/out/graph.json` 11527-11534, `graph.js` 11528-11535 (FIN-005 titles carry the part text).
- `docs/engineering-decisions.md`, `docs/analysis-records.md:373`, `docs/session-state.md:19`, `docs/model-usage.md:83-85`: mention D-226 / T-077 p8 (no x 176 numeric found by grep, but D-226 rows live there).
- Not searched: `redesign/site/`, films, archive, `.claude/worktrees/` (excluded by the brief or copies).

## 9. Added mass / parts

None. Mass changes are the geometry-driven values in s2 / s7 only.

## 10. Open item for the conductor

- The brief's CAD mass 1633.38 g / CG 20.688 mm does not match the files on disk (1632.48 g / 20.777 mm); see s7.
