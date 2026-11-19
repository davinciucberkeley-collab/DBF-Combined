# T-020 Z-bend leg end fix (rung 2, applied)

Date 2026-11-19. Category: **interference (mesh, Blender BVH, and analytic separating-axis)**; leg-length reasoning is a geometric hand calculation. `docs/*.md` not edited; proposed record text in section 5.

## 1. Acceptance test (from the brief)
After the change: `collide_a.py --linkage-poses --zj mid,lo,hi` has 0 pairs over 0.05 mm at all angles and states; `A_ELEV_POSE=21 collide_a.py` static gate PASS; the three mechanism scripts PASS in mid/lo/hi; `build_a.py` check PASS; `proofs/run_all.py` fails stay the known 6.

## 2. What the built joint is (from CAD, build text, vendor data)
- Vendor data: `redesign/review/QP-4/SERVO.md` and the CAD comment on `SV_*`: ES3054HV case 28.4 x 13.0 x 26.7 mm; ears and **output boss height are "-"** (no drawing). So the arm underside to case top gap is unknown; the CAD puts the arm directly on the case top (`ARM_Z0 = SV_Z1`, declared design contact arm / servo case). No vendor number supports a gap.
- Built joint (BUILD D2a / D3, D-212 rev 3): the 1.2 mm wire is formed with an L-end leg that goes down through the 1.3 mm arm hole, the rod lies on the arm top, and the printed keeper MEC-008 over the bend holds it down. There is **no tail below the arm**: the arm sits on the case, so a hooked Z tail would have to sit between arm and case, where there is no space (and the rod can lift only 0.3 mm). The joint is "free in z over 0.3 mm" by the keeper at the top and the rod resting on the arm at the bottom.
- Before: leg end drawn at `ARM_Z0 + 0.1 mm` at mid, i.e. 0.1 mm above the underside (leg 2.65 mm from the rod axis, which is 2.75 mm above `ARM_Z0` at mid). The leg is rigid with the rod, so at lo (rod 0.15 mm lower) the end is 0.05 mm below the case top; the analytic sweep had held its leg base fixed at `ARM_Z0 + 0.1 mm` and never saw this. This is a real finding, not facet noise: a hand-cut 1.2 mm wire leg of that length cannot be built without touching the case at lo (cut tolerance EST +-0.2 mm).
- Does the modelled leg match the built wire? Before: only if the builder cuts the leg to 2.65 mm from the rod axis, with a 0.1 mm margin that is inside any cutting tolerance, so no. After: leg 2.50 mm, a number in the build step ("cut the leg 2.5 mm from the rod axis to its end"), end 0.25 mm inside the arm underside at mid.

## 3. Ladder choice (docs/engineering-decisions.md)
Rung 1 drop the leg: no (it is the joint). **Rung 2 modify geometry: chosen.** The leg length is a made (cut) dimension of the rod MEC-003, not a vendor part, so it is the right thing to change. It is the built geometry, not a number moved to pass: it is chosen from the real constraints (no space below the arm; leg must stay engaged in the 2 mm arm at hi; stay above the case at lo):
- lo: end 0.10 mm above the case (0.25 - 0.15), clear of EST cut tolerance only if the cut is within +0.1 mm; the leg is shortened, not lengthened, so check at build (D3 fit check below).
- mid: 0.25 mm above the underside. hi: 0.40 mm above it, i.e. 1.60 mm of the 2.0 mm arm still engaged (the K5 tilt allowance of 2.86 deg was computed for the full 2 mm; at 1.6 mm the geometric allowance is arctan(0.1/1.6) = 3.58 deg, larger, so K5 stays conservative; K5 is not re-derived).
- Rejected: an arm spacer or boss to open a gap (boss height "-", adds a printed part and moves ARM_Z0 / horn / rod / keeper heights, open item 5); a Z tail below the arm (no space); rung 4 (redefine lo as ROD_Z - 0.10 mm) would change the joint freedom the keeper defines (K7 and the keeper drawing) to fit the model.
- Residual risk: the 0.10 mm margin at lo is within the EST cut tolerance of a hand-cut leg. Build-step D3 now states the leg length; a received rod with a leg longer than 2.6 mm from the axis is re-cut. "-" (no vendor tolerance).

## 4. Files changed
- `redesign/qp/A/cad/amodel/electrical.py`: new `ROD_LEG_GAP = 0.25 mm`, `ROD_LEG_L = ROD_Z - ARM_Z0 - ROD_LEG_GAP` (2.50 mm); the rod leg cylinder is `(tip, ROD_Z - ROD_LEG_L)`, length `ROD_LEG_L` (was base `ARM_Z0 + 0.0001`); part name updated.
- `redesign/qp/A/mechanism/elevon_sweep_collision.py` line 224: leg base `k.ZJ - e.ROD_LEG_L` (rigid with the rod in every joint state; was fixed `ARM_Z0 + 0.0001`).
- `redesign/qp/A/mechanism/linkage_core.py`: no change (it carries only ROD_Z / ROD_KEEP; the leg base is not in it).
- `redesign/qp/A/cad/a_build_steps.py` D3 fit text; `BUILD-GUIDE-A.md` and `redesign/site/app.html` regenerated (`make_build_guide_a.py`, `site/make_build_guide.py`).
- `redesign/qp/A/cad/linkage_poses_a.py`: declared-joint label text only (no logic).
- No drawing changes: MEC-003 has no drawing in `drawings/` (grep: only `a_build_steps.py` callout). `redesign/params/CHANGE-LOG.md`: T-020 entry extended with the decision.

## 5. Commands, exit codes, wall times (full log with output tails: `T020_zbend_runlog.txt`)
Run sequentially from one script (cwd repo root unless noted).
| Command | rc | wall |
|---|---|---|
| `ELEVON_ZJ={mid,lo,hi} python -I redesign/qp/A/mechanism/elevon_linkage.py` | 0 x3 | 9 / 5 / 4 s |
| `ELEVON_ZJ={mid,lo,hi} python -I redesign/qp/A/mechanism/elevon_dynamics.py` | 0 x3 | 8 / 7 / 7 s |
| `ELEVON_ZJ={mid,lo,hi} python -I redesign/qp/A/mechanism/elevon_sweep_collision.py` | 0 x3 | 15 / 14 / 14 s |
| `python -I redesign/qp/A/mechanism/linkage_loads_check.py` | 0 | 6 s |
| `python -I redesign/qp/A/cad/build_a.py` | 0 (check PASS, 10 modules, 0 errors, 0 warnings; TOTAL 1273 g) | 15 s |
| `python -I collide_a.py --linkage-poses --zj mid,lo,hi --tag linkage_poses` (cwd `redesign/qp/A/cad`) | 0 (PASS, 52 poses, 486 bodies, 115 parts) | 474 s |
| `A_ELEV_POSE=21 python -I redesign/qp/A/cad/collide_a.py` | 0 (PASS, 3 poses, 0 pairs over 0.05 mm, 0 wire ends open, 0 folds) | 143 s |
| `python -I redesign/qp/A/proofs/run_all.py` | 1 (the known 6 FAILS: HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY (five listed in the output tail; `fails 6` as before)) | 3 s |
| `python -I redesign/qp/A/mechanism/linkage_poses_report.py linkage_poses` | 0 | 2 s |
| `make_build_guide_a.py`, `site/make_build_guide.py` | 0 | seconds |

## 6. Results
- **Mesh linkage sweep: PASS** (was FAIL, 34 hits). 0 pairs over 0.05 mm at all 17 angles x mid / lo / hi and the static pose (static deepest 0.034 mm, unchanged). Remaining sub-tolerance hits are the leg in the arm hole only: lo -21 deg 0.024 mm, -20 0.016, -18 0.012, +18 0.012, +20 0.018, +21 0.019; hi -21 0.011, +21 0.012. The rod / servo case hit is gone. 0 wire ends open, 0 folds. Reports: `redesign/qp/A/cad/out/REPORT_linkage_poses.md`, `report_linkage_poses.json`, tables `linkage_poses_tables_linkage_poses.md`.
- **Analytic sweep (AR-003):** worst penetration mid 0.0 (arm / clevis cheek +1 contact), lo 0.0284 mm arm / rod (design contact, unchanged), hi 0.0029 mm keeper bridge / rod (design contact, unchanged). Rod Z-bend pin / servo case separation now **0.250 / 0.100 / 0.400 mm (mid / lo / hi)**, was 0.100 mm in every state because its base was fixed.
- **Kinematics (AR-001):** K1-K7 PASS in all three states (`pass_all` true); unchanged, because the rod axis heights and arm geometry did not change. Free play K7 0.028 deg. Dynamics and loads outputs rewritten, geometry-independent of the leg length.
- Mesh and analytic sweeps now agree on the leg to case clearance at lo (mesh +0.10 expected, analytic 0.100).
- Proof fails: still the known 6.

## 7. Proposed record text (for the records owner; not applied)
**AR-003 addendum (mesh sweep and Z-bend leg length).** After the T-020 mesh linkage sweep found the rigid rod leg 0.051-0.056 mm into the servo case at the lo joint state, the leg end was moved from 0.10 mm to 0.25 mm inside the arm underside at mid (cut length 2.50 mm from the rod axis; `ROD_LEG_L` in `electrical.py`); the analytic sweep's leg is now rigid with the rod instead of fixed at a base. Mesh sweep (`collide_a.py --linkage-poses`, 17 angles x 3 states + static, 474 s): 0 pairs over 0.05 mm; leg in the arm hole at most 0.024 mm (lo, -21 deg). Analytic pin / case separation 0.250 / 0.100 / 0.400 mm (mid / lo / hi). Limits: the 0.10 mm margin at lo is below the hand-cut tolerance of the leg (EST +-0.2 mm); arm underside to case top gap and output boss height are "-" (SERVO.md), so the model puts the arm on the case.

**AR-007 ten-field block (update).**
1. Question: do the arm, keeper, rod, clevis and elevon group interfere anywhere in the full elevon range, with the Z-bend joint at any height in its 0.3 mm freedom?
2. Category: interference during motion (mesh, Blender BVH).
3. Model: CAD meshes, 115 parts, 486 bodies; rigid motions from `mechanism/linkage_core.py` (T-018 solution), pin and rod as one rigid frame, 3 joint states mid / lo / hi.
4. Assumptions: rigid parts; 0.05 mm gate tolerance; elevon angles -21..+21 every 3 deg plus +-20 (step justified from AR-003 slopes at most 0.0035 mm/deg); both elevons at the same angle; leg 2.50 mm from the rod axis; arm on the case (boss "-"); leg cut tolerance "-" / EST +-0.2 mm.
5. Inputs: git 73d95966 plus the working tree; `electrical.py` (`ROD_LEG_L`), `linkage_core.py`.
6. Method: `python -I collide_a.py --linkage-poses --zj mid,lo,hi --tag linkage_poses` in `redesign/qp/A/cad`.
7. Outputs: `cad/out/report_linkage_poses.json`, `REPORT_linkage_poses.md`.
8. Result: PASS, 0 pairs over 0.05 mm, 52 poses (the first run FAILED at zj=lo before the leg change).
9. Limitations: facet error on the 12-gon arm hole (real hole has more clearance); clearances are upper bounds within about 0.01 mm; the clevis pin rides with the rod; rod grade, boss height, cut tolerance not published.
10. Reproduce: command above (474 s); also `mechanism/out/T020_zbend_runlog.txt`.
