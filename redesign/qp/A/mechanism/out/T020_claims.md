# T-020 / follow-up item 11: claims added, FIXES2 step 7 applied, +-20 deg mesh gate rerun (2026-11-19)

Git base 94a3a48a, nothing committed. docs/*.md not edited; proposed record text is in section 4.

## 1. Part A: proof graph
Edits (all under `redesign/qp/A/proofs/`):
- `gen_params_a.py`: new params `linkage.keeper_bridge_stall_mpa` (19.48 MPa, from `linkage_loads_check.json` `keeper_bridge_MEC008.stall.factored_MPa`, EST), `linkage.servo_speed_margin_r2` (1.521, from `servo_speed_torque_T056.cases["6.0V_pair_0.333"].speed_margin_R2`, EST) and `linkage.servo_speed_margin_min` (1.0, the AR-005 acceptance criterion). Source `SRC-A-LINKLOADS`, same as the other linkage claims.
- `claims_a2_struct.py`: `stored(...)` claims, same pattern as CL-A-HORN-SHEAROUT-STALL.
  - CL-A-KEEPER-BRIDGE-STALL: 19.48 <= 20 MPa (`linkage.petg_allow_mpa`), margin +3 %, verifies A-P13, assumes ASM-A-PETG-ALLOW, parts MEC-008-R/L + MEC-004-R/L. Text says it is thin (EST allowable), creep and preload loss are "-", retorque/inspect at D2a, D5b, preflight.
  - CL-A-SERVO-SPEED: 1.521 >= 1.0, margin +52 %, verifies A-P11, parts MEC-001/002/004 R/L. Basis 6.0 V pair; 7.2 V speed unpublished (7.2 V case 1.73 not used); required rates EST; R3 0.84 is not a required case.
- FIXES2 E1 step 7 (`redesign/review/QP-4/FIXES2.md`, section 8 table) replaced: now probes the BUILT free play (step 2 value, strips off), pass basis measured free play <= 1 deg (SERVO.md s4 flutter guide, CL-A-LINKAGE-FREEPLAY); above 1 deg, endpoints go to +-19 deg and are recorded. (Old text: "free play deliberately 1 deg".)

Run: `python -I redesign/qp/A/proofs/run_all.py` rc 1 (strict FAILED, expected), ~1.4-3 s. 555 nodes, 1174 edges (was 548 / 1151; +7 nodes: 2 claims, 2 read calcs, 3 params... as the graph counts them). Status UNVERIFIED 217, PROPOSED 17, CHECKED 321, VERIFIED 0; **fails 6, unchanged** (A-P13 via CL-A-FLUTTER-ELEVON-NOM UNVERIFIED, the five known FAIL claims: HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY). The two new claims CHECKED, not failing. Stdout: `redesign/qp/A/mechanism/out/T020_run_all_stdout.txt`. `python -I tools/ledger_audit.py`: 0 errors (109 req, 63 tasks).
Category: hand calculation (stored results read, not recomputed). Note A-P13 now also rests on a claim with +3 % margin on an EST allowable; not a pass.

## 2. Part B: mesh gate at +-20 deg, D-212 rev 3
Command: `A_ELEV_POSE=20 python -I redesign/qp/A/cad/collide_a.py` (from `redesign/qp/A/cad`), Blender 4.5.14 BVH, tol 0.05 mm. rc 0, wall 152 s (script 145 s). Log `cad/out/collide_d212r3_pose20.log`.
Script always writes `out/report.json` + `REPORT.md` (and `_job.json`, `blender.log`); I copied them to `report_d212r3_pose20.json` / `REPORT_d212r3_pose20.md` and restored `report.json`, `REPORT.md` (pose21 content, as before), `_job.json` (git checkout). The pose21 files were not touched.

Result (category: interference, mesh): 115 parts, 486 bodies, 3 poses.
- static: 10 hits, all under 0.05 mm (deepest HWC-001 / HWC-003 0.034 mm; AVN-006 / AVN-009-S and -T 0.017 mm); 0 over tolerance.
- elevons at -20 deg: 0 hits. elevons at +20 deg: 0 hits.
- part pairs over 0.05 mm: 0; wire ends not on a termination: 0; wire folds: 0.
- Identical to the +-21 deg report in counts and depths (the pose20 run adds no new contact; 0.034 mm max is the static nut contact).
Collision claims: `gen_params_a.py` now reads `report_d212r3_pose20.json` for the +-20 deg poses (was the pre-D-212 `report_pose20.json`), because +-20 deg is the commanded endpoint (BUILD D5b) and the rev 3 geometry (rib, keepers, slot cut) must be what the claim reads; +-21 deg stays (physical stop). CL-A-COLL-COUNT 0, CL-A-COLL-DEPTH 0.034 mm (unchanged). Text updated in `claims_a0_base.py` (SRC-A-COLL), `claims_a3_program.py` (how/equation of the two claims).

### What is held out of the moving mesh poses
From `_job.json` (via `collide.poses()`): moved = MEC-004 L/R (horn + rib), MEC-005 L/R (clevis pin), WNG-006 L/R (elevon), WNG-007 L/R (lead), WNG-010 L/R (damper rotor). Held out (`skip_with`, "linked", path not modelled): **MEC-003 L/R (pushrod with Z-bend and clevis)** and **WNG-009 L/R (damper stator side)**. The servo arm **MEC-002 and the keeper MEC-008 are not in either list**: they stay at their neutral position in the +-20/21 poses (not moved, not held out), so the mesh gate never rotates the arm or the keeper. Arm and keeper therefore are checked statically at neutral only in the mesh gate.
Analytic sweep (AR-003, `elevon_sweep_collision.py`, delta -21..+21 deg every 0.5 deg, so it includes +-20) does move arm, rod, clevis, horn blade/rib, keeper spacer/bridge, elevon, against servo case, wing skin, caps and the core section. It does NOT cover the damper (WNG-009), wires, or any other CAD part; and it is analytic shapes from CAD constants, not the meshes. Gap: arm, rod and keeper moving against the actual meshes (e.g. wires, damper, case details) is covered by neither gate.
Flag: `collide_a.py` has no option to include rod and arm in the moving poses (options: --blender, --tol-mm, --no-sweep, --job-only); the pose list comes from `collide.poses()` (K09-L helper, not edited) which holds out joint-linked parts. So no second run was possible without new code (rod/arm follow the 3-D linkage_core solution, not a rotation about the hinge); not attempted. Proposed follow-up: a `--linkage-poses` mode feeding `linkage_core` rigid motions for MEC-002/003/008 per pose into the job's `over`/`motion` dicts.

## 3. Open items remaining
Item 11 now: only `assembly_check.py` and `collide.py --glb` still not run (no GLB export). CL-A-KEEPER-BRIDGE-STALL and CL-A-SERVO-SPEED added; FIXES2 step 7 applied; +-20 deg rerun done.

## 4. Proposed analysis-records text (for the T-020 owner to paste; not applied)
Replace item 11 with: "11. **Still open:** `assembly_check.py` and `collide.py --glb` (no GLB export). Closed 2026-11-19 (T-020 follow-up): claims CL-A-KEEPER-BRIDGE-STALL (19.48 <= 20 MPa EST, +3 %) and CL-A-SERVO-SPEED (1.52 >= 1.0) added (graph 555 nodes / 1174 edges, fails still 6); FIXES2 E1 step 7 now probes the built free play; `collide_a.py` +-20 deg rerun for rev 3 (`report_d212r3_pose20.json`). Evidence `redesign/qp/A/mechanism/out/T020_claims.md`." In item m-9 replace "+-20 deg is still the pre-D-212 ... not rerun" with "+-20 deg read from `report_d212r3_pose20.json` (2026-11-19)".

Ten-field block (T-020, mesh gate at +-20 deg):
- Category: interference during motion (mesh, Blender BVH).
- Solver / tool + version: `redesign/qp/A/cad/collide_a.py` -> `a_collide_blender.py`, Blender 4.5.14; Python 3.14.2.
- Model version (git commit): git `94a3a48a` plus the uncommitted working tree of 2026-11-19 (D-212 rev 3 CAD).
- Inputs: CAD model of 115 parts / 486 bodies (`redesign/qp/A/cad/model`), 41 wire strands; elevon limits from `A_ELEV_POSE=20`.
- Assumptions: elevon, horn, rib, clevis pin, lead, damper rotor turn rigidly about the hinge; pushrod (MEC-003) and damper stator (WNG-009) held out as linked parts; servo arm (MEC-002) and keeper (MEC-008) stay at neutral.
- Boundary conditions / loads: static, both elevons at -20 deg, both at +20 deg; no loads.
- Numerical settings: tolerance 0.05 mm, report threshold 0.01 mm; no sweep between poses.
- Outputs: `redesign/qp/A/cad/out/report_d212r3_pose20.json`, `REPORT_d212r3_pose20.md`, log `collide_d212r3_pose20.log`.
- Acceptance criteria (set before the run): 0 part pairs deeper than 0.05 mm, 0 open wire ends, 0 wire folds.
- Result: PASS: 0 / 0 / 0; 115 parts, 486 bodies; static hits 10 all <= 0.034 mm; wall 152 s. Limits: three poses only (not a sweep); rod, arm, keeper and damper path covered only by the analytic sweep (AR-003), which does not cover the damper or wires.
