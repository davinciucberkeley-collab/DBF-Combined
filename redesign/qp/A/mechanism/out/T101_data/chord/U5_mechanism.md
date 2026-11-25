# T-101 U5: elevon chord 0.25 -> 0.30, mechanism re-run (AR-001..AR-005, AR-007)

Git HEAD dff3191a (working tree dirty, nothing committed). Baseline copies: `pre_mech/` (linkage_*.json, linkage_loads_check_stdout.txt, taken before any run).
Overall: kinematics K1-K7, dynamics D1-D6, AR-003 analytic sweep, AR-007 mesh sweep, stop_check and servo torque/speed (AR-005) PASS.
AR-004 strength rows: three rows that PASSED before now FAIL (below). Reported for the conductor; no criterion or CAD changed.

## Inputs old -> new
| input | old | new | source |
|---|---|---|---|
| HINGE_NM (elevon_dynamics.py l37, linkage_loads_check.py l58) | 0.146 N m | 0.146 x (73.50/61.25)^2 = 0.2102 N m | CALC, EST basis unchanged (T-101 chord decision) |
| preload / damper | 0.0093 / 0.0098 N m | unchanged | same tape strips and damper |
| I_E_CAD (elevon_dynamics.py l56, asserted against file) | 1.3698e-05 kg m2 | 1.96051e-05 kg m2 (1.36857e-5 elevon + 5.91936e-6 balance) | sitl/cad_mass.json elevon.hinge_inertia_total_kgm2 |
| ARM_R / HORN_R | | 6.86 / 7.39 mm (ratio 1.077) | U1c_finnode.md (read from CAD by linkage_core) |
| F_hold / F_stall rod (loads check) | 17.05 / 50.99 N | 30.44 / 63.25 N | linkage_loads_check.json |
Also edited: plot title (elevon_dynamics.py l238), docstring/comment text in linkage_loads_check.py (l9, l295, l323). linkage_core.py had no chord-dependent hard-coded load. The I_E_CAD constant was a hard-coded CAD copy and aborted the first dynamics run (assert), so it was updated to the new cad_mass.json value (not a criterion).
Note: first loads run (`U5_loads_stale_dyn_json_first_run.txt`) read the stale linkage_dynamics.json (dynamics had aborted), giving F_hold 17.05; it was rerun after dynamics; `U5_loads.txt` is the valid run.

## a. AR-001 kinematics (elevon_linkage.py), mid / lo / hi
| criterion | old | new | result |
|---|---|---|---|
| K1-K7 mid, lo, hi | all PASS | all PASS (exit 0) | PASS |
Wall: 6 / 20 / 14 s. Files: U5_kin_{mid,lo,hi}.txt. Free-play budget 1.280 -> 1.590 deg (informational; guide 1.0, see AR-004 row).

## b. AR-002 dynamics (elevon_dynamics.py), mid / lo / hi
| criterion | old (mid) | new mid / lo / hi | result |
|---|---|---|---|
| D1-D6 | PASS | PASS / PASS / PASS | PASS |
| D4 hold margin min, 6.0 V (>=1.5) | 2.457 | 1.704 / 1.708 / 1.701 | PASS |
| D4 hold margin min, 7.2 V EST (>=1.5) | 2.929 | 2.032 / 2.036 / 2.028 | PASS |
| D3 peak compression vs Euler/2 | 42.74 N vs 55.59 | 53.01 N vs 108.20 (mid; lo/hi 53.02) | PASS (Euler 216.4 N, ratio 4.08) |
| step t_reach / overshoot | 0.056-0.076 s / -0.05..-0.06 deg | 0.062-0.109 s / -0.07..-0.09 deg | informational |
Wall: 19 / 13 / 11 s (after the I_E fix; first attempts 4/14/13 s aborted on the assert). Files: U5_dyn_{mid,lo,hi}.txt.

## c. AR-003 analytic swept interference (elevon_sweep_collision.py)
| criterion | old | new mid / lo / hi | result |
|---|---|---|---|
| no penetration > 0.05 mm | PASS | worst 0.000 / 0.030 (arm/rod, design contact) / 0.003 (keeper bridge/rod, design contact) mm | PASS |
Wall 19 / 17 / 25 s. Files: U5_sweep_{mid,lo,hi}.txt.

## d. AR-004 / AR-005 loads and servo torque/speed (linkage_loads_check.py, mid)
AR-005 criteria (limits as in the script):
| criterion | old | new | result |
|---|---|---|---|
| torque margin hold 6.0 V (>=1.5) | 2.457 | 1.704 | PASS |
| torque margin loaded 6.0 V | 2.173 | 1.562 | PASS |
| torque margin hold 7.2 V | 2.929 | 2.032 | PASS |
| torque margin loaded 7.2 V | 2.591 | 1.863 | PASS |
| speed R1 6.0 V / 7.2 V (>=1.0) | 2.891 / 3.288 | 1.930 / 2.483 | PASS |
| speed R2 6.0 V / 7.2 V (>=1.0) | 1.521 / 1.730 | 1.015 / 1.306 | PASS (6.0 V margin 1.5% only) |
| R3 6.0 V / 7.2 V (informational, <1) | 0.836 / 0.951 | 0.558 / 0.719 | not gated |
| pass.servo_speed_margin_ge_1 | True | True | PASS |

AR-004 strength rows (old -> new):
| row | old | new | result |
|---|---|---|---|
| Z-bend leg stress sigma_K hold / stall (MPa) | 310 / 928 | 554 / 1151 | |
| Z-bend vs A228 allowable 1680 MPa (recalled), x1.5 req. yield: hold / stall | 466 PASS / 1392 PASS | 831 PASS / 1727 FAIL | pass.rod_leg_music_wire_recalled True -> **False (was PASS, now FAIL, stall)** |
| blade root factored (MPa) hold / stall | 3.32 / 6.62 | 5.35 / 7.41 | PASS / PASS (allow 20) |
| hole bearing factored hold / stall | 18.4 PASS / 36.7 FAIL | 32.8 / 45.5 | hold **PASS -> FAIL**, stall FAIL -> FAIL |
| shear-out factored hold / stall (MPa) | 5.57 PASS / 11.1 PASS | 9.95 PASS / 13.8 FAIL | hold PASS; stall **PASS -> FAIL** (horn_blade.stall.shearout_ok; not in the script pass dict) |
| rib in foam hold / stall | FAIL / FAIL (432 / 861 kPa) | FAIL / FAIL (498 / 690 kPa) | unchanged FAIL |
| elevon torsion, foam only hold / stall | FAIL / FAIL | FAIL / FAIL (hold 378 kPa factored vs 85.8) | unchanged FAIL |
| keeper bridge hold / stall (MEC-008) | PASS 0.49 / PASS 0.97 util | FAIL 1.22 / FAIL 1.69 util | **PASS -> FAIL both** |
| free-play budget (guide 1.0 deg) | 1.28 FAIL | 1.59 FAIL | unchanged FAIL |
Rows that PASSED before and now FAIL: Z-bend leg A228 stall (rod_leg_music_wire_recalled), horn hole bearing hold, horn shear-out stall, keeper bridge hold and stall. Rerun once (identical output after the stale-input fix). Cause: hinge moment x1.44 and lever ratio, rod hold force 17.05 -> 30.44 N, stall 50.99 -> 63.25 N. Note the 1.44x scaling of the rod force is a linkage_loads_check input, not a CAD change; the conductor decides the loop.
Wall 13 s. Files: U5_loads.txt, ../../linkage_loads_check.json (the committed linkage_loads_check_stdout.txt was not regenerated).

## e. linkage_poses_report.py (reads cad/out/report_linkage_poses_t101.json): exit 0, 1 s. Output U5_poses_report.txt (also cad/out/linkage_poses_tables_linkage_poses_t101.md).

## f. AR-007 mesh linkage sweep
`cd redesign/qp/A/cad; python -I collide_a.py --linkage-poses --zj mid,lo,hi --tag linkage_poses_t101`: PASS, 585 bodies in 129 parts, 52 poses, 0 part pairs over 0.05 mm in all 52 (52 of 52 lines "0 part pairs"), wire ends off termination 0, folds 0. Wall 1881 s (Blender 4.5.14; a second Blender was running concurrently). U5_mesh_sweep.txt.

## g. stop_check.py: exit 0, PASS, 27 s. U5_stop_check.txt.

## Commands
`python -I redesign/qp/A/mechanism/{elevon_linkage,elevon_dynamics,elevon_sweep_collision}.py` with ELEVON_ZJ unset/lo/hi; `linkage_loads_check.py`; `linkage_poses_report.py linkage_poses_t101`; `collide_a.py` (above); `redesign/qp/A/cad/stop_check.py`. Wall times: U5_walltimes.txt. Outputs overwritten in redesign/qp/A/mechanism/out/linkage_*.{json,csv,png}.
