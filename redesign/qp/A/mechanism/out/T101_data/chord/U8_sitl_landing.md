# T-101 U8: SITL consistency rerun (C5) and landing rerun at the final CAD (elevon chord 0.30, linkage resized), 2026-11-23

Result: Part A PASS (all four T101C5 runs all_pass true). Part B PASS (all four D-243 window corners pass every AR-016 criterion; static tip-over 31.03 deg edge-toward-CG). Nothing edited except new files in `chord/` (no CAD, params, proofs, cad_mass.json, T098 originals touched).

## Mass arithmetic
Formula (U4 s4, CALC-A-MASS-PRED): m = basic x 1.1174 + 0.032 x 1.47. CAD basic 1.64198 kg (`sitl/cad_mass.json`): 1.64198 x 1.1174 = 1.834762; + 0.04704 = 1.881788, **1.882 kg EST** (U4 used 1.64288 -> 1.883; cad_mass.json now 1.64198). Used 1.882 in SITL and LAND_MASS_KG.

## Part A, SITL
Script `chord/run_sitl_t101_chord_c5.sh` (= U4 script with mass=1.882, 4 lines plus header comment; log `chord/sitl_batch_C5.log`). Command: `bash redesign/qp/A/mechanism/out/T101_data/chord/run_sitl_t101_chord_c5.sh C5 "fw_hold=1.0 P:TECS_SPDWEIGHT=0.5"`. Wall (log): Z5 276 s, Z5 Lua 277 s, T-074 124 s, T-074 Lua 124 s; all exit 0, ALLDONE, no rerun. Then `python -I redesign/qp/A/sitl/fwd_sum.py <tag>` for each T101C5_* tag (output `U8_fwd_sum.out`), then `python -I .../T101_data/t101_collect.py C1 C2 C3 C4 C5` (rewrote C1-C4 entries from their existing run dirs; C1-C4 values unchanged vs U4 output). Toolchain as U4 s8. Copies in `T101_data/sitl_T101C5_*`; results `mechanism/out/T101_results.json`.

Pitch use unrounded = peak mean elevon / 15 (`U8_unrounded.txt`, same method as U4_unrounded.txt):
| Run | peak mean elevon deg C4 -> C5 | pitch use C4 -> C5 | limit | all_pass C5 |
|---|---|---|---|---|
| Z5 | 7.210 -> 7.150 | 0.4807 -> 0.4767 | 0.60 | true |
| Z5 Lua | 7.265 -> 7.640 | 0.4843 -> 0.5093 | 0.60 | true |
| T-074 | 7.540 -> 8.050 | 0.5027 -> 0.5367 | 0.60 | true |
| T-074 Lua | 8.140 -> 8.100 | 0.5427 -> 0.5400 | 0.60 | true |

Other T-097 limits, C4 / C5 (all pass): 
| Run | peak alt m (<110) | climb m (<60) | t to 1.3 Vs s (<=15) | cap run s (<=1) | motor>=0.85 s (<=1) | elevon sat s (<=1) | touch in flight | u_max | pack peak A | hinge N m | V_end | QLAND sink peak m/s (<=1.2) | tip-over |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z5 | 90.5 / 89.9 | 39.5 / 38.4 | 9.9 / 9.8 | 0 / 0 | 0 / 0 | 0 / 0 | no / no | 0.771 / 0.771 | 32.2 / 32.2 | 0.0228 / 0.0227 | 17.1 / 17.1 | 0.29 / 0.29 | no / no |
| Z5 Lua | 89.6 / 91.8 | 38.5 / 40.3 | 8.5 / 8.7 | 0 / 0 | 0 / 0 | 0 / 0 | no / no | 0.791 / 0.794 | 32.2 / 32.2 | 0.0248 / 0.0266 | 17.0 / 17.0 | 0.31 / 0.30 | no / no |
| T-074 | 85.1 / 86.2 | 34.0 / 34.8 | 9.4 / 9.4 | 0 / 0 | 0 / 0 | 0 / 0 | no / no | 0.751 / 0.751 | 30.2 / 30.1 | 0.0234 / 0.0247 | 17.7 / 17.7 | n/a | n/a |
| T-074 Lua | 85.0 / 85.5 | 33.9 / 34.1 | 8.8 / 8.8 | 0 / 0 | 0 / 0 | 0 / 0 | no / no | 0.751 / 0.751 | 30.2 / 30.1 | 0.0263 / 0.0258 | 17.6 / 17.7 | n/a | n/a |
Hinge peak against servo 0.167 N m. Note: C5 differs from C4 only by mass 1.883 -> 1.882 (and the sample scatter of 0.01-0.03 in pitch use, AR-017); changes of up to 0.026 (Z5 Lua, T-074) are within the single-sample scatter band, not a mass effect. Largest C5 pitch use 0.5400, margin 0.060 to the limit. One sample per case.

## Part B, landing
CAD part table: `LAND_PART_TABLE=<chord>/cad_part_table_t101.json python -I landing_mass_cad.py --build --mass 1.882` run in `redesign/qp/A/structures/` (the T-097 method, AR-014 audit s: `--build`; 13 s). Table basic 1641.98 g, CG (21.49, -3.33, 6.59) mm, I diag 88.52 / 34.86 / 98.63 g m2 = CAD (ratio 1.0); at 1.882 kg growth by class (E x1.3142, C x1.1571) gives I 103.0 / 39.41 / 115.53 g m2 (the sim uses the CAD CG 21.486 mm, not the table's grown CG 27.79 mm, as T-097).
Env: LAND_MASS_KG=1.882 LAND_MASS_MODEL=cad LAND_PART_TABLE=chord/cad_part_table_t101.json LAND_RIB_OD=0.025 LAND_RIB_ID=0.023, LAND_TRACE unset.
Run 1 (record): `python -I redesign/qp/A/structures/landing_a.py 37.5 > chord/landing_cad_t101_p37p5_rib25.txt` (exit 0, 36 s; the record landing_a default zeta 0.05, stroke 20 mm). 
Run 2 (window): `chord/sweep_t101.py` = copy of sweep_t098.py with default mass 1.882, default table t101 and the structures path depth (4 up) changed; command `T98_FP="37.5,39" T98_Z="0.02,0.05" python -I sweep_t101.py zeta 25 window_t101.json 12` (group zeta, 4 corners x 10 cases = 40 runs, exit 0, 40 s; the first launch failed on the structures path in my copy, a launch bug, fixed and rerun; no sim case crashed). Output `chord/window_t101.json`, log `window_t101.log`.

Worst of the 10 cases per corner (rib 25x23):
| Fp N / zeta | stroke mm (<=20) | n g (<=12) | end tilt deg (<=3) | min rib RF (>=1.0) | verdict |
|---|---|---|---|---|---|
| 37.5 / 0.05 (record run, T-098: 17.2 / 10.76 / 2.3 / 3.36) | 17.22 (hard 10 narrow + drift) | 10.75 (hard level) | 2.28 | 3.37 (hard 7/7) | PASS |
| 37.5 / 0.02 | 19.59 (hard 10 narrow + drift) | 9.20 | 2.54 (hard 10 narrow + drift) | 3.39 (hard 10 wide) | PASS |
| 39.0 / 0.02 | 18.84 | 9.54 | 2.44 | 3.33 | PASS |
| 39.0 / 0.05 | 16.59 | 11.12 | 2.17 | 3.25 | PASS |
T-098 for comparison at 37.5 / 0.02: 19.56 mm, 9.20 g (AR-016); new 19.59 mm, 9.20 g. The 37.5 N / 0.02 corner has the smallest stroke margin (0.41 mm of 20). Record run, all ten cases: worst side 22.5 N, Fmax up to 56.2 N, all strokes <= 17.2 mm, n <= 10.75 g, tilt <= 2.3 deg (`landing_cad_t101_p37p5_rib25.txt`).
Static tip-over at the new CG (x 21.486, z 6.590 mm, h 0.3160 m; from the record header): narrow edge toward CG **31.03 deg** (T-098: 31.08), PASS against 30.5 (A-P9 target, edge basis as AR-016); pad-centre toward CG 30.23 deg (below 30.5; the AR-016 verdict uses the edge basis, report only); wide 50.50 deg. 36 mm pad not run (not requested).

Limits: unmeasured foam, mu 0.40, rigid body, ten AR-014 cases only, mass 1.882 rounded (unrounded 1.88179), rib RF root check only; one-sample SITL scatter as above.
