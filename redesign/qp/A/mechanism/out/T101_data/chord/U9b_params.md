# T-101 U9b: proof inputs updated for the T-101 chord / linkage change (2026-11-24)

Files edited: `redesign/qp/A/proofs/gen_params_a.py`, `claims_a0_base.py`, `claims_a1_flight.py`, `claims_a2_struct.py`, `explain_a.py`. Regenerated: `params-A.json`, `proofs/claims.*.json`, `proofs/out/*` (by the run). No limit changed.

## Run caveat (blocker, partly worked around)
`cad/out/assembly.json` is DELETED in the working tree (git status ` D`; `a_assembly.py` was last run 00:03 and left no file; another unit is touching `cad/out`). `gen_params_a.py` (and therefore `run_all.py`) throws FileNotFoundError at line 41 on every call, with or without my edits (twice reproduced). I did not touch CAD output. Workaround (scratchpad wrappers, no repo edit): `gen_wrap.py` ran `gen_params_a.py` reading the HEAD copy of `assembly.json` (43 steps + 16 bench = 59; the current `ASSEMBLY.md` says 66 steps, so the assembly step counts in `params-A.json` are STALE: assy_steps, assy_steps_ok, assy_parts_placed), then `run_all_nogen.py` ran the same steps as `run_all.py` minus the gen_params step. Output `chord/U9b_run_all.txt`; exit 1 (STRICT fails, as before: the run exits 1 whenever any claim FAILS). Rerun `python -I redesign/qp/A/proofs/run_all.py` once `assembly.json` is regenerated (`a_assembly.py`) to refresh the step counts; no claim value in the list below depends on them.

## Values changed (old -> new, source)
| Param | Old | New | Source / note |
|---|---|---|---|
| sim.pitch_use_15_worst | 0.79 (AR-015) | 0.54 (0.5400) | SRC-A-AR018: worst of four C5 runs (Z5 0.4767, Z5 Lua 0.5093, T-074 0.5367, T-074 Lua 0.5400); C4 0.4807 / 0.4843 / 0.5027 / 0.5427; 1.882 kg EST, CG 21.486 mm, chord 0.30, fw_hold 1.0 s, TECS_SPDWEIGHT 0.5; single sample (U8_sitl_landing.md). Limit req.pitch_use_max 0.60 unchanged |
| servo.hinge_vd_nm | 0.151 | 0.2174 (0.151 x 1.44) | SRC-A-AR018, chord^2 scaling, EST. Note: `linkage_loads_check.json` inputs use 0.21024 (0.146 x 1.44); the 0.2174 follows the brief |
| servo.arm_mm | 8.5 | 7.00 | SRC-A-AR018, CAD ARM_R in `cad/amodel/electrical.py` (T-101 U6a) |
| servo.horn_mm | 9.155 | 7.54 | SRC-A-AR018, CAD HORN_R = ROD_Z - HINGE_Z = 7.539 mm (electrical.py) |
| flutter_hot_ms (kd/nom/hi) | 37.5, 40.0, 44.0 | 36.0, 38.0, 42.0 | new source SRC-A-T101FL, flutter_t101.md case B (lead 14.0 g, elevon 7.6 g) |
| flutter_nom_ms | 41.0, 44.0, 49.0 | 40.0, 43.5, 48.0 | case C |
| flutter_cold_ms | 44.0, 47.5, 53.5 | 44.0, 47.5, 53.5 | case D (unchanged) |
| flutter_half_kd_ms | 31.5 | 29.0 (K 0.50) | case E kd; margin to the 28.8 m/s line is only 0.2 m/s (nom 30.5, hi 33.5) |
| wing_flutter_ms | 46.2, 49.5, 56.3 | 46.0, 49.3, 56.2 | flutter_wing_t101.md, fins on |
| wing_flutter_nofin_ms | 33.7, 39.9, 46.5 | 35.5, 42.3, 49.4 | flutter_wing_t101.md, fins off |
| struct.landing_stroke_mm | 17.2 (AR-016) | 17.22 | SRC-A-AR018, U8 record run at 1.882 kg EST (n 10.75 g, tilt 2.28 deg); window corners 16.59-19.59 mm all pass |
| linkage.* (generated from JSON, not typed) | | f_hold 29.84 N, f_stall 61.99 N (was about 51 N), blade, bearing, rib, torsion, rod leg 936 MPa (was 1392 / 1172) | `linkage_loads_check.json`, `linkage_kinematics.json` (free play 1.567 deg) |
| Predicted mass | 1.881 kg | 1.882 kg (1.88179) | computed by CALC-A-MASS-PRED from `sitl/cad_mass.json` (basic 1.64198 kg); text updated in claims_a1_flight.py (CL-A-MASS-PRED `how`) and explain_a.py (STALL-PRED card) |
| Elevon stop / peak values | unchanged | unchanged | no new number in the evidence |

Text updates: clevis / pin wording removed (rod end Z-bend through the 1.6 mm reamed hole in the 2.4 mm horn boss) in gen_params_a.py (bearing_hold, free_play notes) and claims_a2_struct.py (CL-A-HORN-BEARING-*, CL-A-LINKAGE-FREEPLAY, stall-step and bench-stall text, 1.2 -> 1.6 mm pin gauge). Test loads written in text now match the JSON: hold rod force 29.84 N x 2.156 = 64.3 N (was 36.8 N); stall force 62 N (was 51 N, 61.99 N in the JSON; text also in claims_a0_base.py TP-16 / TP-18); torsion coupon 0.1065 N m x 2.156 = 0.230 N m (was 0.161); rod receipt test 109 N = 1.5 x 62 N x 2.05 / 1.75 (was 91 N, 1.9 / 1.6); ASM-A-ROD-GRADE needs 936 MPa from a 1.5 mm rod. New sources added to `claims_a0_base.py`: SRC-A-AR018 (docs/analysis-records.md, AR-018 being written by another unit) and SRC-A-T101FL. CL-A-PITCH-USE explain card rewritten (passes in simulation, 0.54 against 0.60, "T-101 decision", single-sample caveat, via AR-018). Historical text left (AR-015 notes, CALC-A-STALL-PRED equation text "1.881 kg, T-084", CL-A-STALL-PRED note on D-212 rev 2).

## Claim status
Failing claims before: 14 (HEAD claims JSON evaluated with HEAD params; matches CLAUDE.md 2026-11-23). After: 15.

Changed PASS <-> FAIL:
- CL-A-PITCH-USE: FAIL -> PASS (0.79 -> 0.54 against <= 0.60).
- CL-A-SERVO-FACTOR: PASS -> FAIL NEW (1.556 -> 1.119 against >= 1.5). Cause: hinge_vd_nm x 1.44 with the same servo stall torque. Reported, not fixed.
- CL-A-SERVO-COLD: PASS -> FAIL NEW (1.585 -> 1.157 against >= 1.5). Same cause; horn / arm ratio 7.54 / 7.00 = 1.077 unchanged. Reported, not fixed.

Still FAIL, value changed: CL-A-ELEVON-TORSION-FOAM 504.3 -> 378.7 kPa (<= 85.8); CL-A-HORN-BEARING-STALL 36.65 -> 24.77 MPa (<= 20); CL-A-HORN-RIB-FOAM-HOLD 431.8 -> 493.2; CL-A-HORN-RIB-FOAM-STALL 860.9 -> 682.9; CL-A-LINKAGE-FREEPLAY 1.28 -> 1.567 deg (<= 1); CL-A-MASS-PRED / MASS-GATE-ROOM 1.8807 -> 1.8818 kg (<= 1.47); CL-A-CUTS-REQUIRED 409.1 -> 410.1 g; CL-A-STALL-PRED 17.744 -> 17.749 m/s (<= 17). Unchanged FAIL: CL-A-VIB-FC, VIB-GM, VIB-GM-SHIFT, VIB-IN-BAND.

Still PASS with value change (close margins): CL-A-SERVO-SPEED 1.521 -> 1.015 (>= 1.0), CL-A-SERVO-RATIO 2.63 -> 1.83, CL-A-HORN-BEARING-HOLD 18.39 -> 17.89 (<= 20), CL-A-KEEPER-BRIDGE-STALL 19.48 -> 18.85 (<= 20), CL-A-HORN-SHEAROUT-STALL 10.92 (<= 11.55), CL-A-ROD-LEG-STALL 936 (allow 1626), CL-A-LANDING-STROKE 17.22, CG 21.49 mm, SM 7.84 %, CL-A-COST-TOTAL 1935.31 (BOM-A.csv edited by another unit, not by me). Elevon / wing flutter claims (list inputs, lowest governs) show no FAIL in the run.

Note: the 15-FAIL set is the 14 of CLAUDE.md minus PITCH-USE plus SERVO-FACTOR and SERVO-COLD. CLAUDE.md's "12 of D-237 pending" wording is not re-derived here.

Run summary: `chord/U9b_run_all.txt`, exit 1 (FAILED strict gate on the failing claims above; no exception in the claims scripts or build_graph; render step reached only through the wrapper list as run_all ordering, see file).
