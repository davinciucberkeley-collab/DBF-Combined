# T-101 U6a: elevon linkage resize (finishing pass)

Conductor decision: resize existing parts, remove allowed, no limit relaxed. Nothing committed. Allowables unchanged from U5.
Evidence: U6a_loads.txt, U6a_kin_{lo,mid,hi}.txt, U6a_dyn_{lo,mid,hi}.txt, U6a_sweep_{lo,mid,hi}.txt, U6a_build_a.txt, U6a_stop_check.txt, U6a_cad_mass.txt, U6a_bom.txt, U6a_build_guide.txt; ../../linkage_loads_check.json.

## 1. Rows that failed in U5: old (U5) -> new
Allowables as in linkage_loads_check.py: A228 bending allowable 1626 MPa at 1.499 mm (script formula from the recalled Sut, "recalled", not a datasheet value) with a 1.5 x required-yield check; PETG bearing 20 MPa EST; shear-out 11.55 MPa EST; keeper bridge 20 MPa EST. Load factors hold 2.156, stall 1.4375.

| row | U5 (1.2 mm wire) | U6a (1.499 mm) | allowable | result |
|---|---|---|---|---|
| Z-bend leg, required yield x1.5, hold / stall (MPa) | 831 / 1727 | 451 / 936 (sigma_K 301 / 624, K 1.625, e 1.75-2.05 mm) | 1626 | PASS both (U5 stall FAIL) |
| horn hole bearing hold (factored) | 32.8 FAIL | 17.89 (d 1.499, t 2.4 mm) | 20 | PASS |
| horn hole bearing stall (factored) | 45.5 FAIL | 24.77 | 20 | still FAIL |
| horn shear-out stall (factored) | 13.8 FAIL | 10.92 (e = 2.5 - 0.8 = 1.7 mm) | 11.55 | PASS (hold 7.88) |
| keeper bridge utilisation hold / stall | 1.22 / 1.69 FAIL | 0.68 / 0.94 (bridge 1.1 mm) | 1.0 | PASS both |
| servo speed R2 at 6.0 V | (U5 PASS) | 1.0151 | 1.0 | PASS, but only 1.5 % over the line; 7.2 V EST 1.306 |
| servo torque margin hold, 6.0 V / 7.2 V | - | 1.70 / 2.03 (tau_hold 0.1955 N m) | 1.0 | PASS |

Geometry old -> new: ROD_D 1.2 -> 1.499 mm (RMRC .059 in A228); ARM_R 6.86 -> 7.00 mm; ARM_HOLE_D 1.3 -> 1.6 mm; HORN_HOLE_D 1.1 -> 1.599 mm (printed 1.4, reamed 1.6); horn boss 2.0 -> 2.4 mm (head radius 2.5 mm); HORN_R 7.39 -> 7.54 mm; rod end is a Z-bend leg through the horn hole (bend centre-line radius 1.5 d, HORN_Y_OFF 3.55 mm, leg protrudes 1.0 mm EST); ROD_LEG_L 2.65 mm; KEEP_T 0.8 -> 1.1 mm. Rod force: hold 29.8 N, stall 62.0 N (U5 63.2 N).

Ladder rung per change: rod = modify (diameter); clevis and clevis pin (MEC-005) = remove; horn boss = modify; keeper = modify (bridge thickness).

## 2. Kinematics, dynamics, sweeps (joint states ELEVON_ZJ lo / mid / hi)
- K1-K7: all true in lo, mid, hi. Min horn angle 68.4 / 68.1 / 67.8 deg (40 deg rule met).
- D1-D6: 6.0 V constant case reaches target in 0.109 s, overshoot -0.09 deg, peak rod tension 43.6 N, no compression, hold margin 1.71 / 1.70 / 1.70, residuals ~1e-17 (lo / mid / hi). R2 as above.
- Analytic sweep (elevon_sweep_collision.py): pass_no_penetration_gt_tol true, pairs_failing empty in all three; horn rib to core min 2.55 mm at +21 deg; elevon nose to core min 1.14 mm.
- stop_check.py: PASS (cap clearance >= 0.5 mm, boss to lead >= 0.5 mm).

## 3. Rows that failed before and still fail
- hole bearing stall: 24.77 vs 20 MPa (U5 45.5), improved, still FAIL.
- rib in foam hold / stall: FAIL / FAIL (unchanged).
- elevon torsion, foam only, hold / stall: FAIL / FAIL (unchanged).
- free play: 1.28 deg (pre-T-101 CAD) -> 1.59 (U5) -> 1.567 deg (arm hole 0.101 mm = 0.768 deg, horn hole 0.100 mm = 0.760 deg, Z-bend freedom 0.040 deg) vs 1.0 deg guide: FAIL. Servo backlash "-", measured at E1.
No limit was relaxed; these need a bench test or a decision.

## 4. Mass and BOM
- cad_mass: mass_basic_kg 1.64198 (U1c 1.64288, -0.90 g); cg_x 21.486 mm (U1c 21.567 mm). Elevon hinge inertia total 1.9605e-05 kg m2, unchanged, so I_E_CAD in elevon_dynamics.py needs no change (task 3 not triggered).
- Per part (new CAD functions): rod 0.55 g each, horn 1.16 g each, keeper 0.080 g each; clevis and pin removed (pin was 0.03 g CAD). Old per-part values come from the old build-step text (rod 0.97 g with clevis, horn 0.95 g), not a rerun; the total delta is from cad_mass.
- build_a: only the pre-existing graph:mass error (1642 g > 1500 g).
- BOM M02: RMRC 10 pc linkage set $8.99 -> RMRC .059 in piano wire, 6 pcs x 12 in, $5.49 (https://www.readymaderc.com/products/details/-059-piano-wire-6-pcs-with-z-bends, opened 2026-11-23, docs/audits/2026-11-23-T101-linkage-scout.md 1c; Z-bends and A228 not stated on the listing, confirm on delivery, else the team forms the bends). BOM total $1,939.17 -> $1,935.31 (<= $2,000, margin $64.69).

## 5. References to MEC-005 / clevis
Fixed this pass in a_build_steps.py (stale before): arm step (hole 1.3 -> 1.6 mm, radius 6.86 -> 7.00 mm); keeper bridge text 0.8 -> 1.1 mm; D3 horn (reamer 1.6 mm, height 7.54 mm, clevis fit check replaced by leg check); D4 pushrods (1.499 mm wire, rod-end Z-bend through horn hole, leg 2.65 mm, no clevis); D5 and D5b retitled "Rod-end leg check", callouts MEC-005-R/L -> MEC-003-R/L; stall-test pin gauge 1.8 mm vs 1.6 mm hole. BUILD-GUIDE-A.md regenerated (66 steps, 50.2 h).
Already updated: a_assembly_plan.py D4/D5/D5b (marker steps); electrical.py (no MEC-005 part; the 'CT-CLEVIS' contact-type key is kept as an internal label); BOM-A.csv M02; elevon_linkage.py, elevon_sweep_collision.py, linkage_loads_check.py notes.
History or unrelated: wing.py "node outer clevis ears" (cage part, unrelated).
Stale live, outside what I was allowed to edit (for later units):
- Proofs: proofs/claims_a2_struct.py 193-194 (CL-A-HORN-BEARING-HOLD/STALL titles "Clevis pin bearing"), 225-227 (CL-A-LINKAGE-FREEPLAY "clevis cheek" text); proofs/gen_params_a.py 260 ("1.0 mm clevis pin bearing") and 271.
- Pose tooling (will break or mislabel when --linkage-poses is next run, MEC-005 no longer exists): cad/linkage_poses_a.py (PIN 'MEC-005-', pin_with, clevis mesh names), cad/a_linkage_blender.py (TARGET_PARTS), cad/collide_a.py line 37 (--pin-with), mechanism/linkage_poses_report.py 65-67 and 136-137, mechanism/linkage_core.py docstring, mechanism/elevon_linkage.py ALLOW_C / clevis_misalign fields (harmless).
- Generated files that still carry MEC-005 until regenerated by their tools: cad/model/mechanisms/interfaces.json, cad/out/_plan.json, report_*pose*.json, glb/_job_glb.json. cad/out/parts-a.csv rows MEC-003/005 still show the old "clevis" text and the MEC-005 rows: parts_links_a.py (already updated, no clevis text) is not run by build_a, so the CSV is stale until its generator is run.

## 6. Files written or changed this pass
redesign/qp/A/cad/a_build_steps.py; redesign/qp/A/BUILD-GUIDE-A.md (regenerated); redesign/qp/A/cad/out/* (build_a, stop_check); chord/U6a_build_a.txt, U6a_stop_check.txt, U6a_cad_mass.txt, U6a_bom.txt, U6a_build_guide.txt, U6a_resize.md. Earlier in U6a (previous builder): electrical.py, a_assembly_plan.py, BOM-A.csv, mechanism scripts.
