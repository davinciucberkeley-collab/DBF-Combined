# T-064r landing side load, load-path part checks and tip-over on the CAD ground plane (2026-11-19)

Task T-064 revision (R-PHY-09), concept A. Responds to `docs/audits/2026-11-19-D213-review.md` (D-213 REJECTED, findings F1-F10). Nothing committed; no CAD source, docs/*.md, CHANGE-LOG or ledger edited. SITL not run.
Analysis categories: **rigid-body dynamics** (landing_a.py, explicit 6-DOF, four elasto-plastic feet, Coulomb friction); **hand-calculation part checks** (statics, beam / tube / bond / rectangular-section theory, EST allowables); **illustrative** (option screening, section 7). No FEA, CFD, flight dynamics or interference run.

## 0. Acceptance test (restated from the brief)
(1) landing_a.py on the CAD foot (X_GROUND 0.3375, pad-centre z) and CAD CG; rerun AR-008, AR-012, lean / drift scan; report static narrow-axis tip-over vs A-P9 (>= 30 deg). (2) A script that checks every part on the CAD load path with CAD dimensions at the governing loads, KP 2.156 printed / bonded, RF >= 1.0, naming the true minimum. (3) FIN-005 / FIN-003 volume from CAD vs listed mass. (4) F7 / F8 / F9 fixes, claim drafts. (5) Ladder options with trade table for every RF < 1 and for A-P9; no pick.
**Outcome: the CAD-geometry rerun produces FAILS that D-213 did not see.** A-P9 static tip-over is 29.2 deg (FAIL, 0.8 deg short); with the project's EST allowables most load-path check groups are below RF 1.0, including the rib tube itself at RF 0.86 under a friction yaw-slip case that appears only with the CAD CG; FIN-005 / FIN-003 CAD solid volumes are 18x / 7x their listed masses. Not VERIFIED COMPLETE; decisions are for the opus reviewer.

## 1. Commands, exit codes, wall times (cwd `redesign/qp/A/structures`, Python 3.14, 20-core Windows 11)
| # | Command | Exit | Wall | Output |
|---|---|---|---|---|
| 1 | `python -I landing_a.py 30` (CAD geometry, default) | 0 | 32 s | `T064r_data/landing_30_cad.txt` |
| 2 | `GEOM_LEGACY=1 python -I landing_a.py 30` (old geometry) | 0 | 27 s | `landing_30_legacy.txt`; identical to `T064_data/landing_30_after.txt` except the added static() keys (diff checked) |
| 3 | `python -I landing_side_a.py` (CAD) | 0 | 160 s | `landing_side_cad.txt` |
| 4 | `python -I landing_sitl_env_a.py` (CAD) | 0 | 61 s | `sitl_env_cad.txt` |
| 5 | `python -I landing_lean_scan_a.py` (new; 728 runs, dt 2e-4, T 1.2 s) | 0 | 147 s | `lean_scan_cad.txt` |
| 6 | `python -I landing_path_a.py` (new, 23 cases + volumes) | 0 | 48 s | `path_full.txt` (`path_quick.txt` = early 10-case run) |
| 7 | `python -I landing_path_options_a.py` (new, option screening) | 0 | 267 s | `path_options.txt` |
| 8 | `python -I landing_tip_options_a.py` (new) | 0 | 119 s | `tip_options.txt` |
| 9 | `python -I landing_sitl_records_a.py` (new, F8 glob) | 0 | <1 s | `sitl_records.txt` |
| 10 | `python -I` copy of `sitl/cad_mass.py` writing to `T064r_data/cad_mass_regen_20261119.json` (regeneration check; `sitl/cad_mass.json` untouched) | 0 | 6 s | CG x 21.366 mm, z 6.364 mm vs stored 21.369 / 6.369: identical to 0.01 mm |
| 11 | `python -I redesign/qp/A/proofs/run_all.py` (baseline, before any claim edit) | **1** | 1 s | `run_all_baseline.txt`: `gen_params_a.py` FileNotFoundError `cad/out/assembly.json`. `git status` shows `D cad/out/assembly.json` and modified `cad/amodel/electrical.py`, `wing.py`, `a_build_steps.py`: another session is editing the CAD tree. Not caused by this task. |

Scripts changed / new (all in `redesign/qp/A/structures/`): `landing_a.py` (CAD geometry + CG, `--legacy` / `GEOM_LEGACY=1`, `trace=True`, new static() keys), `landing_side_a.py` (CAD geometry, baseline rows relabelled, arms from geometry), `landing_sitl_env_a.py` (absolute path removed), new `landing_lean_scan_a.py`, `landing_path_a.py`, `landing_path_options_a.py`, `landing_tip_options_a.py`, `landing_sitl_records_a.py`. `structures_a.py` imports landing_a: its s5 would print CAD-geometry numbers when regenerated; `structures_run.md` was **not** regenerated.
Caveat on the CAD tree: another session left uncommitted edits in `cad/amodel/electrical.py` and `wing.py` during this task. `git diff` shows no change to X_GROUND, YFIN, FIN_H, RIB_*, or the pad / shoe / saddle / block geometry (grep checked), so the numbers below use the same landing geometry as HEAD `f2707f19`.

## 2. F2: CAD ground plane and CG (item 1)
Source of every input: x_ground 0.3375 m = `electrical.py` X_GROUND l.498; y 0.38 = `common.py` YFIN; pad box z FIN_H-0.009 .. FIN_H+0.003 = 0.171 .. 0.183, centre **0.177** = `electrical.py` build_landing 'foot pad'; CG = `redesign/qp/A/sitl/cad_mass.json` (written 2026-11-18 by `sitl/cad_mass.py`; the 2026-11-19 regeneration agrees to 0.01 mm): x **21.369 mm**, y **-2.034 mm**, z **+6.369 mm**, basic mass 1.27324 kg (CAD declared masses, no growth). Loads keep M_GATE 1.50 kg (AR-008 convention, covers growth; tip-over is mass-independent). Inertia stays the landing_a ITEMS roll-up about its own CG (Ixx 0.0577, Iyy 0.0260, Izz 0.0625; cad_mass.json gives 0.0657 / 0.0265 / 0.0718 at 1.273 kg, so ITEMS is lighter in roll and yaw: not changed). `landing_a.py --legacy` reproduces the old x 0.30 / z 0.18 / ITEMS-CG values exactly.

### 2.1 Static tip-over against A-P9 (>= 30 deg, `REQUIREMENTS-A.md` l.42, which quotes 33.2 deg EST)
h = x_ground - CG x = 0.3375 - 0.02137 = 0.3161 m. Narrow axis (about a pad pair at z = +-0.177), angle = atan(lever / h):
| Pivot | toward the CG side (z_cg +6.4 mm) | away from it | legacy value |
|---|---|---|---|
| pad centre z 0.177 | **28.36 deg** | 30.12 deg | 33.0 deg |
| pad outer edge z 0.183 | **29.19 deg** | 30.92 deg | 33.0 deg |
| CG z ignored, pad centre | 29.24 deg | | |

Wide axis (about a fin, y 0.38): 50.2 deg (legacy 53.9). **A-P9 static narrow-axis tip-over FAILS on the CAD geometry: 29.2 deg about the pad outer edge, 28.4 deg about the pad centre, toward the side the CG is offset to** (review F2: 29.4 / 29.3). The pad edge is the more physical pivot for a foam pad that rolls; the centre is what the sim uses (conservative). Needed: z_edge - z_cg >= 0.1825 m, i.e. pad edge at 0.1889 m (5.9 mm outward) or CG z at 0.

### 2.2 AR-008 cases on the CAD geometry (30 N plateau, 1.50 kg; `landing_30_cad.txt`)
```
{'cg_x': np.float64(0.021368686971819924), 'cg_y': np.float64(-0.0020344773962489397), 'cg_z': np.float64(0.006369460588734254), 'h': np.float64(0.3161313130281801), 'geom': 'CAD', 'I': array([0.05772651, 0.02599915, 0.06252816]), 'tip_narrow': 29.244199184630762, 'tip_wide': 50.24209980998184, 'tip_narrow_ctr_toward_cg': 28.35776743408385, 'tip_narrow_ctr_away': 30.115536711688375, 'tip_narrow_edge_toward_cg': 29.19319384217381, 'tip_narrow_edge_away': 30.922516233483233, 'tip_wide_toward_cg': 50.39244074746207, 'tip_wide_away': 50.09080448398054, 'v_tip_parked': 6.761106408376056, 'restore_ratio_5ms': 1.8285023946153507}

### plateau 30.0 N per foot, usable stroke 20 mm
hard level                   stroke max   8.4 mm  n 10.79  Fmax  39.7 N  side  12.4 N  tilt_end   0.0  drift    10 mm  set 6.9  rib RF 2.95
hard 10 narrow               stroke max  14.8 mm  n 5.43  Fmax  40.0 N  side  13.3 N  tilt_end   2.0  drift   105 mm  set 13.3  rib RF 2.21
hard 10 narrow neg           stroke max  14.5 mm  n 5.43  Fmax  40.0 N  side  13.4 N  tilt_end   1.9  drift   104 mm  set 13.0  rib RF 2.26
hard 10 wide                 stroke max   8.2 mm  n 5.88  Fmax  44.8 N  side  17.9 N  tilt_end   0.2  drift    47 mm  set 6.7  rib RF 1.55
hard 7/7 combo               stroke max  10.3 mm  n 5.15  Fmax  42.5 N  side  17.0 N  tilt_end   0.7  drift    25 mm  set 8.8  rib RF 1.24
hard 10 narrow + drift .5    stroke max  17.5 mm  n 5.45  Fmax  40.1 N  side  16.0 N  tilt_end   2.5  drift    37 mm  set 16.0  rib RF 2.85
hard 10 wide + drift .5 y    stroke max  10.9 mm  n 6.16  Fmax  46.4 N  side  18.6 N  tilt_end   0.4  drift   124 mm  set 9.4  rib RF 1.49
normal level .5              stroke max   2.3 mm  n 8.93  Fmax  32.9 N  side  11.8 N  tilt_end   0.0  drift     6 mm  set 0.8  rib RF 1.36
normal 10 narrow .5          stroke max   3.5 mm  n 4.56  Fmax  33.9 N  side  13.5 N  tilt_end   0.3  drift   103 mm  set 2.0  rib RF 2.14
normal 10 wide .5 + drift    stroke max   5.9 mm  n 5.34  Fmax  39.9 N  side  16.0 N  tilt_end   0.3  drift   113 mm  set 4.4  rib RF 1.78
```
vs legacy (AR-008 / D-213): worst stroke 17.5 mm (was 15.4), n 10.79 (same), side 18.6 N (18.7), end tilt 2.5 deg (2.2), rib RF min **1.24** (1.26, 7/7 combo). All AR-008 limits except A-P9 hold: stroke <= 20 mm (2.5 mm margin), n <= 12 g, tilt <= 3 deg.

### 2.3 AR-012 side-load and mu sweep, CAD geometry (`landing_side_cad.txt`)
```
## 1. Part capacity at the worst simulated foot load (30 N plateau, mu 0.40), RF = capacity / demand, factors as structures_a.py
worst foot: normal 46.4 N, side 18.6 N (resultant 50.0 N); both maxima taken as simultaneous (conservative)
- [BASELINE GEOMETRY, NOT THE A LOAD PATH, superseded by landing_path_a.py] shoe bond on fin corner, 1,500 mm2, allowable 0.1 MPa (C6 paper/foam value EST): 71.9 kPa -> RF 1.39
- [BASELINE GEOMETRY, NOT THE A LOAD PATH] foam bearing at the fin slot (65 x 23 mm, both feet 18.6 N), allowable 120 kPa EST: 52.9 kPa -> RF 2.27
- [BASELINE GEOMETRY, NOT THE A LOAD PATH] fin skin 0.1 mm CFRP bending at the root, M = 18.6 x 0.18 = 3.34 N m (structures_a.py s6 geometry), allowable 450 MPa EST: 31.8 MPa -> RF 14.1
- rib torsion alone, ONE foot loaded sideways, lever 0.177 m, 30 MPa EST: capacity 24.4 N per foot (structures_a.py s6 row: 15 N gives RF 1.60); at 41.3 MPa (Tap Plastics pultruded shear sheet, checked 2026-11-18, test method not stated): 33.5 N
- rib root bending alone, both feet sideways, arm 0.2670 m, 350 MPa EST: capacity 47.1 N per foot
- rib root, combined bending + torsion + axial, all four feet resolved in the body frame each time step (landing_a.py): see the RF column below; minimum is the governing number

## 2. Pad friction sweep (30 N plateau): side load per foot N / rib RF
hard 7/7 combo               mu 0.30:  13.3 N RF  1.53  mu 0.40:  17.0 N RF  1.24  mu 0.50:  20.9 N RF  1.04  mu 0.60:  24.5 N RF  0.89  mu 0.70:  28.0 N RF  0.78
hard 10 wide + drift .5 y    mu 0.30:  14.2 N RF  1.94  mu 0.40:  18.6 N RF  1.49  mu 0.50:  22.7 N RF  1.07  mu 0.60:  26.5 N RF  1.02  mu 0.70:  30.6 N RF  1.17
hard 10 wide                 mu 0.30:  13.9 N RF  1.80  mu 0.40:  17.9 N RF  1.55  mu 0.50:  21.5 N RF  0.96  mu 0.60:  24.3 N RF  0.94  mu 0.70:  28.3 N RF  1.15
normal 10 wide .5 + drift    mu 0.30:  11.9 N RF  2.31  mu 0.40:  16.0 N RF  1.78  mu 0.50:  19.9 N RF  1.08  mu 0.60:  24.0 N RF  0.97  mu 0.70:  27.9 N RF  1.07
mu at RF = 1 (linear interp.) hard 7/7 combo: 0.53
RF stays >= 1 over mu 0.30-0.70: hard 10 wide + drift .5 y (RF at 0.70 = 1.17)
mu at RF = 1 (linear interp.) hard 10 wide: 0.49
mu at RF = 1 (linear interp.) normal 10 wide .5 + drift: 0.57

## 3. Plateau sweep at mu 0.40 (foot geometry lever: pad area x 0.17 MPa): worst stroke / n / side / rib RF over the four cases + hard narrow + drift
Fp   24 N: stroke  20.3 mm  n 25.16  side  77.7 N  rib RF min  0.45  tilt_end max 3.0
Fp   27 N: stroke  19.4 mm  n  9.85  side  17.2 N  rib RF min  1.36  tilt_end max 2.8
Fp   30 N: stroke  17.5 mm  n 10.79  side  18.6 N  rib RF min  1.24  tilt_end max 2.5

## 4. Touchdown envelopes: controlled (SITL touchdown records, 29 runs) and stated structural limits
SITL max: sink .35, lat .52 (x), lean 0      stroke   3.0 mm  n 6.91  Fmax  33.2 N  side  13.3 N  tilt_end   0.2  drift   32 mm  rib RF 3.07
SITL max: sink .35, lat .52 (y), lean 0      stroke   2.6 mm  n 7.18  Fmax  32.7 N  side  13.1 N  tilt_end   0.1  drift   56 mm  rib RF 3.42
SITL lean 29 narrow, sink .35, lat .52 (x)   stroke  21.9 mm  n 140.17  Fmax 999.9 N  side 400.0 N  tilt_end 177.9  drift  643 mm  rib RF 0.11
SITL lean 29 wide, sink .35, lat .52 (y)     stroke   9.0 mm  n 6.24  Fmax  43.0 N  side  17.2 N  tilt_end   0.5  drift  227 mm  rib RF 1.55
SITL lean 19 wide, sink .35, lat .52 (y)     stroke   7.7 mm  n 5.49  Fmax  42.3 N  side  16.9 N  tilt_end   0.4  drift  165 mm  rib RF 1.30
```
Reading: worst side 18.6 N (hard 10 wide + drift); rib torsion alone 24.4 N per foot; mu at rib RF = 1: **0.53** (hard 7/7), **0.49** (hard 10 wide), 0.57 (normal 10 wide + drift). The 24 N plateau now exceeds the stroke (20.3 mm, rigid stop, n 25): D-213 row C (plateau 24 N) no longer works on the CAD geometry; 27 N: stroke 19.4 mm, RF 1.36. The three "BASELINE GEOMETRY" rows in s1 are kept only as labelled legacy rows (F1) and are superseded by section 3.

### 2.4 SITL touchdown records re-run on the CAD geometry (`sitl_env_cad.txt`; record list `sitl_records.txt`)
```
29 records with lateral_speed_ms: 22 under key 'landing', 7 at the top level
max lateral speed m/s: 0.52 (R5_b45 landing), n = 29
max peak sink last 1 s m/s: 0.34 (Z5_b0 landing), n = 29
max lean at touch deg: 29.1 (Z5_b0 landing), n = 29
tipped_over true: []
```
```
Z5_b0 (belly-on 5 m/s, 1.41 kg)    lean 29.1 narrow sign +1 sink 0.34 lat 0.16: stroke  22.1 mm n 154.09 side 439.1 N tilt_end  178.1 drift   757 mm rib RF 0.10
Z5_b0 (belly-on 5 m/s, 1.41 kg)    lean 29.1 narrow sign -1 sink 0.34 lat 0.16: stroke  22.2 mm n 158.46 side 451.8 N tilt_end  179.0 drift   830 mm rib RF 0.09
Z5_b0 (belly-on 5 m/s, 1.41 kg)    lean 29.1 wide   sign +1 sink 0.34 lat 0.16: stroke  10.8 mm n   8.00 side  17.6 N tilt_end    0.6 drift   186 mm rib RF 1.00
Z5_b0 (belly-on 5 m/s, 1.41 kg)    lean 29.1 wide   sign -1 sink 0.34 lat 0.16: stroke  10.9 mm n   7.62 side  17.7 N tilt_end    0.6 drift   181 mm rib RF 1.03
Z5_b45                             lean 17.2 narrow sign +1 sink 0.32 lat 0.21: stroke   5.3 mm n   5.33 side  14.3 N tilt_end    0.5 drift   129 mm rib RF 2.14
Z5_b45                             lean 17.2 narrow sign -1 sink 0.32 lat 0.21: stroke   6.4 mm n   5.12 side  14.5 N tilt_end    0.7 drift   112 mm rib RF 2.25
Z5_b45                             lean 17.2 wide   sign +1 sink 0.32 lat 0.21: stroke   6.2 mm n   5.14 side  16.3 N tilt_end    0.3 drift    97 mm rib RF 0.99
Z5_b45                             lean 17.2 wide   sign -1 sink 0.32 lat 0.21: stroke   6.3 mm n   5.14 side  16.3 N tilt_end    0.3 drift    96 mm rib RF 1.00
Ta_h5 (1.381 kg)                   lean 18.8 narrow sign +1 sink 0.3 lat 0.11: stroke   5.0 mm n   6.00 side  13.6 N tilt_end    0.5 drift   135 mm rib RF 2.21
Ta_h5 (1.381 kg)                   lean 18.8 narrow sign -1 sink 0.3 lat 0.11: stroke   5.2 mm n   6.54 side  13.1 N tilt_end    0.5 drift   123 mm rib RF 2.35
Ta_h5 (1.381 kg)                   lean 18.8 wide   sign +1 sink 0.3 lat 0.11: stroke   6.3 mm n   5.02 side  16.2 N tilt_end    0.3 drift    88 mm rib RF 1.26
Ta_h5 (1.381 kg)                   lean 18.8 wide   sign -1 sink 0.3 lat 0.11: stroke   6.4 mm n   5.03 side  16.3 N tilt_end    0.3 drift    86 mm rib RF 1.24
Tb_h5                              lean 16.5 narrow sign +1 sink 0.31 lat 0.09: stroke   4.2 mm n   6.32 side  13.6 N tilt_end    0.3 drift    99 mm rib RF 2.42
Tb_h5                              lean 16.5 narrow sign -1 sink 0.31 lat 0.09: stroke   3.8 mm n   4.60 side  13.8 N tilt_end    0.3 drift    86 mm rib RF 1.67
Tb_h5                              lean 16.5 wide   sign +1 sink 0.31 lat 0.09: stroke   5.9 mm n   5.05 side  16.3 N tilt_end    0.3 drift    71 mm rib RF 0.89
Tb_h5                              lean 16.5 wide   sign -1 sink 0.31 lat 0.09: stroke   5.9 mm n   5.06 side  16.3 N tilt_end    0.3 drift    69 mm rib RF 0.88
Lb_5e                              lean 12.1 narrow sign +1 sink 0.32 lat 0.45: stroke   6.9 mm n   6.56 side  14.6 N tilt_end    0.7 drift   100 mm rib RF 1.99
Lb_5e                              lean 12.1 narrow sign -1 sink 0.32 lat 0.45: stroke   6.7 mm n   5.35 side  14.4 N tilt_end    0.7 drift    95 mm rib RF 2.09
Lb_5e                              lean 12.1 wide   sign +1 sink 0.32 lat 0.45: stroke   8.0 mm n   7.74 side  15.8 N tilt_end    0.5 drift    84 mm rib RF 2.92
Lb_5e                              lean 12.1 wide   sign -1 sink 0.32 lat 0.45: stroke   8.1 mm n   7.65 side  15.8 N tilt_end    0.5 drift    84 mm rib RF 2.91
Z5_gb45                            lean 11.0 narrow sign +1 sink 0.32 lat 0.5: stroke   6.5 mm n   5.74 side  14.2 N tilt_end    0.7 drift    94 mm rib RF 1.96
Z5_gb45                            lean 11.0 narrow sign -1 sink 0.32 lat 0.5: stroke   7.3 mm n   5.90 side  13.9 N tilt_end    0.8 drift    85 mm rib RF 2.31
Z5_gb45                            lean 11.0 wide   sign +1 sink 0.32 lat 0.5: stroke   5.3 mm n   5.25 side  15.7 N tilt_end    0.2 drift   107 mm rib RF 2.35
Z5_gb45                            lean 11.0 wide   sign -1 sink 0.32 lat 0.5: stroke   5.4 mm n   5.26 side  15.7 N tilt_end    0.3 drift   108 mm rib RF 2.31
```
The six records (lean, lateral, sink as D-213), both axes, both signs, lateral speed in the lean direction. **New with the CAD CG:** the wide-axis cases give rib RF **0.86** (Tb_h5), **1.00** (Z5_b45), 1.25 (Ta_h5) at only 16-17 N side load and 0.3 m/s sink (legacy 3.3). Decomposition (scratch run, not saved: a copy of landing_a.py logging the governing step, plus `cg z = 0` / `cg y = 0` toggles): foot normal 33-37 N, side +12.8 N and -15.4 N on the two feet of one fin, i.e. **opposite friction on the upper and lower foot** = the aircraft yaws about the vertical axis on its pads and each foot is at its friction limit. The couple Mx = 2 mu Fn z = 2 x 0.4 x 35 x 0.177 = **5.0 N m** goes fin tube -> root block -> rib as torsion (tau 34.8 MPa with KF vs 30 MPa EST). The yaw is started by the CG z offset (friction along the span acts 6.4 mm off the CG: yaw torque about 0.2 N m on I_xx 0.058 kg m2; with CG z = 0 the RF is 2.85; CG y alone does nothing). Hand upper bound of the mechanism: Mx = 2 mu Fn z = 6.6 N m at Fn 46.7 N (hard sink), mu 0.4 -> rib tau 45.9 MPa (RF 0.65 on torsion alone); not simulated. Z5_b0 narrow (belly-on 5 m/s, card-prohibited) still tips (end tilt 178 deg).

### 2.5 Lean / drift scan, CAD geometry (F2, F4; `landing_lean_scan_a.py`, `lean_scan_cad.txt`)
```
# geometry CAD, dt 0.0002, T 1.2 s, sink 0.34, Fp 30 N, mu 0.40; tipped = end tilt > 45 deg; entries = largest lean (deg, grid step 2) that stays upright from 0 upward
sign mode    foot  lat 0.00  lat 0.16  lat 0.30  lat 0.40  lat 0.52  lat 0.60  lat 0.70
+1   with     ctr   >=24        22        18        14        10         8         8
+1   with     edge  >=24        22        18        14        10        10         8
+1   against  ctr   >=24      >=24      >=24      >=24      >=24      >=24      >=24
+1   against  edge  >=24      >=24      >=24      >=24      >=24      >=24      >=24
-1   with     ctr   >=24      >=24        18        16        12        10        10
-1   with     edge  >=24      >=24        20        16        12        10        10
-1   against  ctr   >=24      >=24      >=24      >=24      >=24      >=24      >=24
-1   against  edge  >=24      >=24      >=24      >=24      >=24      >=24      >=24

```
Entries: largest narrow-axis lean (deg, grid 2) that stays upright; ">=24" = no tip-over to the scan limit. `with` = lateral travel in the direction of the lean; `against` = opposite; sign = lean toward +z / -z; ctr / edge = foot contact at pad centre z 0.177 / outer edge 0.183. With the lean in the direction of travel the aircraft tips at **12 deg and 0.52 m/s, 10 deg at 0.60-0.70 m/s** (the CG z offset makes the +z direction worse at 0.16 m/s: 22 vs >=24). Against the travel nothing tips to 24 deg. Same as the review's R6 within the 2-deg grid. Card-allowed SITL touchdowns reach 11.0 deg at 0.50 m/s (Z5_gb45) and 12.1 deg at 0.45 m/s (Lb_5e): 0-4 deg from tipping in this pessimistic (no thrust or control) model. SITL itself did not tip; the two models are not reconciled (F4, section 7.4).

## 3. F1: load-path part checks on CAD dimensions (item 2)
Script `landing_path_a.py`; 23 landing cases (the 10 AR-008 cases, 10 SITL-record cases at both axes, one extra 16 deg wide + 0.5 m/s drift case); foot force histories from landing_a (dt 2e-4 s; RF is dt-converged to 0.1 % per review R4); statics per fin with both feet; 30 N plateau, mu 0.40, 1.50 kg. Dimensions read from CAD: fin tube 16x14 (common.py FIN_OD / FIN_ID), rib 14x12 x 0.0705-0.286 (wing.py RIB_*), saddle ring OD 21 x 60 on the spar 12x10 and socket 19x19 x 0.0665-0.0905, root block ring OD 23 x 60 and socket 19x19 x 0.255-0.286 (wing.py build_fins), shoe ring OD 21 x 12, plate 5.5 x 21 x 15, pad 12 x 15 x 30 (electrical.py build_landing). KF 1.725 (CF), KP 2.156 (printed / bonded). Criterion **RF >= 1.0** (F6): KF / KP already carry 1.5 x 1.15 (x 1.25); I found no cited project 0.15 rule that applies to an RF (`structures_a.py rating()` uses MS >= 0.15 on its other tables; that would be RF >= 1.15: the table shows demand stress so the reader can apply it).
Check geometry notes (EST where stated): junction sections between ring and socket are the chord of the ring wall at the plane where the box face meets it (root block 16.5 x 19 mm at x 0.286; saddle 16.5 x 19 mm at x 0.0665; shoe plate-to-ring 13.6 x 12 mm); print orientation is not stated in the CAD or BUILD-GUIDE, so the interlayer allowable PETG_ILAY 9.5 MPa is used for bending and shear (worst case); bond bearing is 6M/(D L^2) + V/(D L); peel on the tension side uses BOND 2.0 MPa as an EST lower bound (no peel allowable in the repo); the spar check counts foot loads only (wing loads and the foam core's torsion share are not credited: conservative); the PSA peel check uses a rigid pad and no compressive relief (conservative; foam compliance lowers it).
Allowable sources: all **EST**, carried from `structures_a.py` l.14-21 (K09-L C2 / C4 / C6 values, "UNVERIFIED until coupons"): CF 350 / 30 MPa, PETG_ILAY 9.5, PETG_BEAR 20, BOND 2.0 (neat epoxy on CF / PETG, K09-L E-FIN-13), SPAR_HOOP 40. PSA 0.10 MPa = the project foam-bond value (C6, used for the shoe bond in D-213); **no PSA or double-sided-tape product or data sheet exists in the repo** (BOM has no tape line; build step C9 "double-sided tape (CAD: pad PSA)").

## Minimum RF per check over all cases (criterion RF >= 1.0)
| Check | Allowable | min RF | governing case | demand stress = allowable / RF |
|---|---|---|---|---|
| P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no foam compliance) | EST PSA 0.10 MPa | 0.02 | hard 7/7 combo | 4.9 MPa |
| P10 saddle socket: rib epoxy bond / bearing (D14 x 20) - peel, tension side [EST lower bound] | EST BOND 2.0 MPa | 0.07 | hard 16 wide + drift .5 y | 27.8 MPa |
| P7 root-block socket: rib epoxy bond / bearing (D14 x 31) - peel, tension side [EST lower bound] | EST BOND 2.0 MPa | 0.26 | hard 7/7 combo | 7.6 MPa |
| P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm) | EST PETG_ILAY 9.5 MPa | 0.28 | hard 16 wide + drift .5 y | 34.4 MPa |
| P14a spar 12x10 bending + torsion under the saddle (foot loads only) | EST 350 / 30 MPa | 0.32 | hard 7/7 combo | 94.9 MPa |
| P11 saddle socket wall, PETG box 19x19 / bore 14, bending + torsion | EST PETG_ILAY 9.5 MPa | 0.34 | hard 16 wide + drift .5 y | 27.8 MPa |
| P1 pad PSA to shoe plate (180 mm2) - shear | EST PSA 0.10 MPa | 0.35 | hard 16 wide + drift .5 y | 0.3 MPa |
| P3 shoe ring epoxy bond on fin tube (D16 x 12) - peel, tension side [EST lower bound] | EST BOND 2.0 MPa | 0.37 | hard 10 narrow + drift .5 | 5.4 MPa |
| P13 saddle ring epoxy bond on spar (D12 x 60) - peel, tension side [EST lower bound] | EST BOND 2.0 MPa | 0.48 | hard 16 wide + drift .5 y | 4.2 MPa |
| P6 root-block ring-to-socket junction, PETG (16.5 x 19 mm) | EST PETG_ILAY 9.5 MPa | 0.50 | SITL Tb_h5 wide (y drift) | 18.9 MPa |
| P8 root-block socket wall, PETG box 19x19 / bore 14, bending + torsion | EST PETG_ILAY 9.5 MPa | 0.51 | hard 7/7 combo | 18.8 MPa |
| P10 saddle socket: rib epoxy bond / bearing (D14 x 20) - bearing, compression side | EST PETG_BEAR 20 MPa | 0.72 | hard 16 wide + drift .5 y | 27.8 MPa |
| P9b rib tube 14x12 at x 0.0705 (AR-012 section) | EST 350 / 30 MPa | 0.86 | SITL Tb_h5 wide (y drift) | 34.8 MPa |
| P9a rib tube 14x12 at saddle mouth x 0.0905 | EST 350 / 30 MPa | 0.86 | SITL Tb_h5 wide (y drift) | 34.8 MPa |
| P5 root-block ring epoxy bond on fin tube (D16 x 60) - peel, tension side [EST lower bound] | EST BOND 2.0 MPa | 1.09 | hard 7/7 combo | 1.8 MPa |
| P10 saddle socket: rib epoxy bond / bearing (D14 x 20) - shear (axial + torsion) | EST BOND 2.0 MPa | 1.14 | SITL Tb_h5 wide (y drift) | 1.8 MPa |
| P13 saddle ring epoxy bond on spar (D12 x 60) - shear (axial + torsion) | EST BOND 2.0 MPa | 1.31 | hard 7/7 combo | 1.5 MPa |
| P14b spar wall diametral crush under the saddle ring (hoop EST 40 MPa) | EST 40 MPa | 1.45 | hard 10 wide + drift .5 y | 27.6 MPa |
| P2 shoe plate-to-ring junction, PETG (13.6 x 12 mm) | EST PETG_ILAY 9.5 MPa | 1.46 | hard 7/7 combo | 6.5 MPa |
| P7 root-block socket: rib epoxy bond / bearing (D14 x 31) - shear (axial + torsion) | EST BOND 2.0 MPa | 1.76 | SITL Tb_h5 wide (y drift) | 1.1 MPa |
| P7 root-block socket: rib epoxy bond / bearing (D14 x 31) - bearing, compression side | EST PETG_BEAR 20 MPa | 2.62 | hard 7/7 combo | 7.6 MPa |
| P3 shoe ring epoxy bond on fin tube (D16 x 12) - bearing, compression side | EST PETG_BEAR 20 MPa | 3.73 | hard 10 narrow + drift .5 | 5.4 MPa |
| P4 fin tube 16x14 at root-block edge | EST 350 / 30 MPa | 3.91 | hard 10 wide + drift .5 y | 7.7 MPa |
| P3 shoe ring epoxy bond on fin tube (D16 x 12) - shear (axial + torsion) | EST BOND 2.0 MPa | 4.25 | hard 16 wide + drift .5 y | 0.5 MPa |
| P13 saddle ring epoxy bond on spar (D12 x 60) - bearing, compression side | EST PETG_BEAR 20 MPa | 4.78 | hard 16 wide + drift .5 y | 4.2 MPa |
| P5 root-block ring epoxy bond on fin tube (D16 x 60) - shear (axial + torsion) | EST BOND 2.0 MPa | 10.70 | hard 16 wide + drift .5 y | 0.2 MPa |
| P5 root-block ring epoxy bond on fin tube (D16 x 60) - bearing, compression side | EST PETG_BEAR 20 MPa | 10.87 | hard 7/7 combo | 1.8 MPa |

**True minimum, stated both ways.** (a) Every row as defined: **P1 pad PSA peel RF 0.02** (demand 4.9 MPa against an EST 0.10 MPa), then **P10 saddle socket peel 0.07**. (b) Excluding the peel rows and the PSA rows (allowables with no repo source): **P12 saddle socket-to-ring junction (printed PETG) RF 0.28**, then P14a spar 0.32, P11 saddle socket wall 0.34, P6 / P8 root-block junction and socket wall 0.50 / 0.51, P10 socket bearing 0.72, then **P9 rib tube 0.86** (the part D-213 called governing, at 1.26). D-213's "rib root governs" is therefore wrong on two counts: the rib is not the weakest part, and under the CAD CG its own RF is 0.86 in the yaw-slip case. The review's hand estimates (saddle bearing about 0.84, saddle wall about 0.4, PSA about 0.45) are reproduced in order of magnitude (this script: 0.72, 0.34, 0.35 shear). Parts that pass: fin tube P4 3.91, shoe plate junction P2 1.46, spar crush P14b 1.45, root-block bond shear / bearing, shoe ring shear / bearing.
Notes. P12 / P11 / P6 / P8 are limited by the PETG section at the ring-to-socket junction (section modulus 860-990 mm3) against 5-10 N m moments from the 0.267 m foot arm; the printed parts at both ends of the rib are the weak links, as the review expected. P14a (spar torsion at the saddle, 5 N m from friction along z at the 0.277 m arm) is a conservative row because the foam core and the opposite fin share the wing torque. Everything depends on EST allowables; the demand-stress column gives the allowable each row would need for RF = 1 (e.g. 34 MPa at the saddle junction exceeds even the 20 MPa in-layer PETG, so print orientation alone cannot close P12).

## 4. F10: FIN-005 / FIN-003 mass from the CAD (item 3)
```
## F10 volumes (voxel 0.25 mm of the stub-built CAD shapes, minus cuts; solid PETG at RHO_PETG 1.27 g/cm3)
FIN-005-R: voxel volume 14.48 cm3 -> solid 18.39 g; listed 1.0 g; sum of shape volumes before cuts 22.66 cm3 -> 28.78 g; listed / solid 0.05
FIN-003-R: voxel volume 18.54 cm3 -> solid 23.54 g; listed 3.2 g; sum of shape volumes before cuts 24.06 cm3 -> 30.55 g; listed / solid 0.14
GER-001-UR: voxel volume 4.16 cm3 -> solid 5.28 g; listed 1.4 g; sum of shape volumes before cuts 4.52 cm3 -> 5.73 g; listed / solid 0.26
GER-002-UR: voxel volume 5.40 cm3 -> solid 6.86 g; listed 0.7 g; sum of shape volumes before cuts 5.40 cm3 -> 6.86 g; listed / solid 0.10
```
Method: the stub-built CAD shapes (`build_a.build` with StubBackend, the route `cad_mass.py` uses) are voxelised at 0.25 mm (union of the part's shapes minus all its cuts: rib bore, spar bore, clip slot) and multiplied by RHO_PETG 1.27 g/cm3 (`wing.py` l.182, the density `electrical.py` uses for printed parts). Listed masses (`wing.py` l.531, 533; `electrical.py` l.687) are hard-coded 3.2 / 1.0 / 1.4 g. **Solid PETG: FIN-005 18.4 g (listed 1.0), FIN-003 23.5 g (listed 3.2), GER-001 5.3 g (listed 1.4).** Per aircraft (2 + 2 + 4 parts) the solid-minus-listed difference is +34.8 g (FIN-005), +40.7 g (FIN-003), +15.5 g (GER-001), **+91 g** if printed solid; infill and shell fraction are not stated ("-"), so the true mass lies between the listed values and the solid mass. Against the 1.470 kg predicted mass (ASM-A-CUTS) this is an open question of up to +91 g. It is a CAD-table issue (outside this task's edit scope: reported, not changed). GER-002 (pad) is foam: its PETG-density line is not meaningful.

## 5. F7, F8, F9 (item 4)
- **F7:** 41.3 MPa (Tap Plastics sheet) appears only as a sensitivity (`landing_side_cad.txt` s1: torsion capacity 33.5 N vs 24.4 N), never as a capacity; the coupon claim is written for the RMRC 14x12 tube actually bought (BOM R09).
- **F8:** `landing_sitl_env_a.py` no longer inserts an absolute path (script directory, as landing_side_a.py). The lean scan is saved (`landing_lean_scan_a.py`; both lean signs, travel with / against, lateral 0 and 0.16-0.70 m/s, lean 0-24 deg step 2, centre and edge foot). The SITL record set is named in `landing_sitl_records_a.py`: glob `redesign/qp/A/sitl/runs/*/sum.json`; 22 files hold the fields under key `landing`, 7 at the top level (La_3b, La_5e, Lb_3b, Lb_5e, R5_l0, R5_l4, d_land); maxima 0.52 m/s lateral (R5_b45), 0.34 m/s peak sink, 29.1 deg lean (Z5_b0); tipped_over true in none. Total 29 confirmed (the review's "22 landing + 7 land cases" had the second key spelling wrong; it is the top level).
- **F9:** seven draft assumption nodes in `T064r_data/claims_T064r_draft.json`: rib twist coupon (`ASM-A-RIB-TWIST`), pad static-mu drag test and the landing-surface definition (`ASM-A-PAD-MU`), drift analysis envelope 0.70 m/s (`ASM-A-DRIFT-ENVELOPE`), printed joints coupon covering FIN-003 and FIN-005 (`ASM-A-PETG-JOINT-ILAY`), pad attachment drop rig (`ASM-A-PAD-ATTACH`), interim lean limit (`ASM-A-LEAN-LIMIT`), CAD tip-over (`ASM-A-GROUND-GEOM`). **Not merged into `proofs/`:** the claims files are generated by claims_a0_base.py / claims_a2_struct.py and `run_all.py` fails today in `gen_params_a.py` (item 11, `cad/out/assembly.json` deleted in the working tree by another session), so the condition in the brief cannot be met; fail count **not measurable** (baseline exits 1 before the claims step). To merge: add as `kit.assumption(...)` in claims_a0_base.py (the form of ASM-A-HUB-WALL), run run_all.py, report the fail count against a clean baseline.

## 6. What changes in the D-213 conclusions (for the conductor)
1. "Rib root governs, PASS RF 1.26": withdrawn. On CAD geometry rib RF is 1.24 for the AR-008 set and **0.86** for SITL-record wide-axis cases (friction yaw-slip couple 5.0 N m); the printed saddle / block junctions (RF 0.28-0.51) and the pad attachment are weaker, and all allowables are EST.
2. Static tip-over 33.0 deg (A-P9 33.2 EST) is 29.2 deg on the CAD (FAIL by 0.8 deg).
3. Mu: rib RF = 1 at mu 0.49-0.53; with the printed parts no tested mu closes the path (7.2 R1: mu 0.30 lifts the rib to 1.23 while P6-P13 stay at 0.3-0.56).
4. Drift: the SITL maximum is 0.52 m/s, above "0.5"; with lean in the direction of travel the pessimistic model tips at 10-12 deg at 0.52-0.70 m/s.
5. FIN-005 / FIN-003 mass entries are 18x / 7x below the CAD solid volume.

## 7. Ladder options (illustrative screening; NO pick; the decision goes to an opus reviewer)
Ladder (`docs/engineering-decisions.md`): 1 subtract, 2 modify geometry, 3 rearrange, 4 change approach, 5 add material / parts. Mass numbers are EST (solid PETG 1.27 g/cm3; CF 16x14 tube 75.3 g/m from FIN-001 27.1 g / 0.36 m; infill unknown "-"). "Margin" is the screening result of `landing_path_options_a.py` / `landing_tip_options_a.py` (same 23 cases, same allowables).

### 7.1 A-P9 static tip-over 29.2 deg (needs >= 30 deg) and dynamic lean
`tip_options.txt` (columns: static about the pad edge toward the CG side / about the pad centre / largest upright lean at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s):
```
variant | static edge toward CG side (deg) | static pad centre | max upright lean at lateral 0.16 / 0.40 / 0.52 / 0.70 m/s (deg, grid 2)
CAD as drawn                                            | 29.19 | 28.36 | 22 / 14 / 10 / 8
track +6 mm (pad edge z 0.189)                          | 30.02 | 29.19 | 22 / 14 / 10 / 8
track +10 mm                                            | 30.56 | 29.74 | 24 / 16 / 12 / 8
track +13 mm (31 deg)                                   | 30.96 | 30.15 | 24 / 16 / 12 / 10
CG z centred (0)                                        | 30.07 | 29.24 | 22 / 14 / 12 / 8
CG z centred and track +3 mm                            | 30.47 | 29.66 | 24 / 16 / 12 / 8
CG 10 mm aft                                            | 29.98 | 29.13 | 22 / 14 / 10 / 8
ground plane 6 mm forward (pad 24 mm long, stroke -6 mm) | 29.66 | 28.82 | 22 / 14 / 10 / 8
track +6 mm and CG 5 mm aft                             | 30.41 | 29.58 | 24 / 16 / 12 / 8
```
| Option (rung) | Δmass g | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| T1 Rearrange: move mass so z_cg = 0 | 0 | edge 30.07 deg (0.07), centre 29.24; dynamic at 0.52 m/s 10 -> 12 deg | edge only, no margin | CG z has no measured value | none | place mass in -z | none | needs 8 g m moment (1.27 kg x 6.4 mm), e.g. a 100 g item 81 mm; no candidate identified "-" | `tip_options.txt`; cad_mass.json cg_z |
| T2 Modify geometry: foot track +6 mm (fin tube 0.372 m, pad edge z 0.189) | +2.1 (tube +1.8, fairing +0.3, EST) | edge 30.02 deg (0.02), centre 29.19; dynamic unchanged | zero margin | none | CAD: FIN-001, FIN-004, shoe, drawings | none | fin area +3 % | box height 0.39 m vs fin span 0.372 m (ASM-A-TRUNK) | `tip_options.txt` |
| T3 Modify geometry: foot track +13 mm (pad edge z 0.196) | +4.6 EST | edge 30.96 deg (0.96), centre 30.15; dynamic 24 / 16 / 12 / 10 | yes on A-P9; dynamic +2 deg | none | as T2 | none | fin area +7 % | box height 0.386 of 0.39 m: 4 mm clearance | `tip_options.txt` |
| T4 Rearrange: CG 10 mm aft | 0 | 29.98 deg | no | static margin (40.7 - 21.4) / 245 = 7.9 % -> 3.8 % (NP 40.7 mm EST, MASS-GATE) | none | move pack | none | static-margin requirement not re-read "-" | `tip_options.txt`; ASM-A-NP |
| T5 Modify geometry: pad 30 -> 24 mm | -0.14 | 29.66 deg | no; the 20 mm stroke needs the 30 mm foam | n limit | cut | none | none | A-P5 12 g | `tip_options.txt` |
| T6 T1 + 3 mm pad / plate z (rungs 2 + 3) | +1 EST | 30.47 deg; dynamic 24 / 16 / 12 / 8 | yes | as T1 | small CAD change | none | none | as T1 | `tip_options.txt` |
| T7 Change approach: re-base A-P9 on the CAD (29 deg) | 0 | 0.2 deg over 29 | formally | none | none | none | none | requirement change (derived requirement, ours per memory) that moves a number the review said must not move silently: log it | review F2 |
| T8 Operational: card lean <= 10 deg when translating, go around | 0 | upright at 10 deg to 0.52 m/s | dynamic only | pilot / FC | card | none | none | not observable by eye (F5); does not fix the static number | `lean_scan_cad.txt` |

### 7.2 Rib torsion (rib RF 0.86 in yaw-slip cases) and the printed joints (RF 0.28-0.51)
Screening, minimum RF over the 23 cases by part (`path_options.txt`; P9 rib, P6 / P8 block, P10-P13 saddle and spar ring, P1 / P3 pad and shoe):
```

### V0 baseline CAD (mu 0.40, CG z 6.4 mm) 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.28 (P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm))
by part: P1 0.02  P2 1.46  P3 0.37  P4 3.91  P5 1.09  P6 0.50  P7 0.26  P8 0.51  P9a 0.86  P9b 0.86  P10 0.07  P11 0.34  P12 0.28  P13 0.48  P14a 0.32  P14b 1.45

### V2a saddle socket 20 -> 40 mm long (x 0.0665-0.1105); EST +5.3 g per saddle solid 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.28 (P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm))
by part: P1 0.02  P2 1.46  P3 0.37  P4 3.91  P5 1.09  P6 0.50  P7 0.26  P8 0.51  P9a 0.86  P9b 0.86  P10 0.31  P11 0.37  P12 0.28  P13 0.48  P14a 0.32  P14b 1.45

### V2b saddle socket 40 mm long and 24 mm square; EST +9.5 g per saddle solid 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.32 (P14a spar 12x10 bending + torsion under the saddle (foot loa)
by part: P1 0.02  P2 1.46  P3 0.37  P4 3.91  P5 1.09  P6 0.50  P7 0.26  P8 0.51  P9a 0.86  P9b 0.86  P10 0.31  P11 0.38  P12 0.35  P13 0.48  P14a 0.32  P14b 1.45

### V3 root-block socket 71 mm long (x 0.215-0.286) and 24 mm square; EST +10 g per block solid 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.28 (P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm))
by part: P1 0.02  P2 1.46  P3 0.37  P4 3.91  P5 1.09  P6 0.76  P7 1.28  P8 1.09  P9a 0.86  P9b 0.86  P10 0.07  P11 0.75  P12 0.28  P13 0.48  P14a 0.32  P14b 1.45

### V2b+V3 together 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.32 (P14a spar 12x10 bending + torsion under the saddle (foot loa)
by part: P1 0.02  P2 1.46  P3 0.37  P4 3.91  P5 1.09  P6 0.76  P7 1.28  P8 1.09  P9a 0.86  P9b 0.86  P10 0.31  P11 0.84  P12 0.35  P13 0.48  P14a 0.32  P14b 1.45

### V1 pad face mu 0.30 (UHMW-PE-class face, mu is the assumption; EST +0.2 g on four pads, K09-L D-105) 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.32 (P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm))
by part: P1 0.02  P2 1.71  P3 0.45  P4 4.24  P5 1.05  P6 0.50  P7 0.27  P8 0.51  P9a 1.23  P9b 1.23  P10 0.08  P11 0.40  P12 0.32  P13 0.56  P14a 0.34  P14b 1.42

### V1 pad face mu 0.25 (UHMW-PE-class face, mu is the assumption; EST +0.2 g on four pads, K09-L D-105) 
min all rows 0.03 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.34 (P14a spar 12x10 bending + torsion under the saddle (foot loa)
by part: P1 0.03  P2 1.87  P3 0.50  P4 4.38  P5 1.07  P6 0.51  P7 0.27  P8 0.52  P9a 1.52  P9b 1.52  P10 0.09  P11 0.44  P12 0.36  P13 0.61  P14a 0.34  P14b 1.40

### V5 CG z centred (rearrange mass, CG z 0), mu 0.40 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.29 (P12 saddle socket-to-ring junction, PETG (16.5 x 19 mm))
by part: P1 0.02  P2 1.45  P3 0.37  P4 3.93  P5 1.08  P6 0.50  P7 0.26  P8 0.50  P9a 1.26  P9b 1.25  P10 0.07  P11 0.34  P12 0.29  P13 0.48  P14a 0.31  P14b 1.41

### V6 mu 0.30 and CG z centred 
min all rows 0.02 (P1 pad PSA to shoe plate (180 mm2) - peel (30 mm lever, no f); min excluding peel and PSA rows 0.33 (P14a spar 12x10 bending + torsion under the saddle (foot loa)
by part: P1 0.02  P2 1.70  P3 0.45  P4 4.27  P5 1.09  P6 0.52  P7 0.27  P8 0.52  P9a 1.55  P9b 1.55  P10 0.08  P11 0.40  P12 0.34  P13 0.56  P14a 0.33  P14b 1.40
```
| Option (rung) | Δmass g | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| R1 Subtract load: UHMW-PE-class pad face, mu 0.30 (rung 5, F3a) | +0.2 EST (four pads) | rib 0.86 -> 1.23; P6-P13 0.3-0.56 unchanged | rib only | mu is the assumption; tape wear "-" | tape on pad | easy | none | A has no tape line; K09-L price $4.91 (findtape.com, 2026-11-14) not an A order | `path_options.txt` V1; K09-L D-105 |
| R2 Subtract the yaw trigger: CG z centred (rung 3) | 0 | rib 0.86 -> 1.26 | rib only; yaw can start from other asymmetry (hand bound 6.6 N m stays) | not robust | none | move mass | none | as T1 | `path_options.txt` V5 |
| R3 R1 + R2 | +0.2 | rib 1.55 | rib only | fair | tape | easy | none | as above | `path_options.txt` V6 |
| R4 Add material: rib 14x10 CF (I x1.6) | about +24 both ribs EST (A 75 vs 41 mm2, 14.1 g each) | torsion x1.6 (0.86 -> about 1.4, not run) | rib only | tube availability and layup "-" (BOM R09 is RMRC 14x12) | new BOM line | none | none | rung 5 | I = pi/64 (14^4 - 10^4) = 1,395 vs 868 mm4 |
| R5 Change approach: swivel or low-friction foot so yaw slip does not twist the fin | +1.5 per foot EST (+6) | removes the friction couple "-" | unproven | new moving part, wear "-" | printed, more parts | +4 parts | none | CAD fidelity rule needs a drawn real part | engineering judgement, not computed |
| J1 Modify geometry: saddle socket 20 -> 40 mm | +5.3 per saddle solid (+10.6) | P10 0.07 -> 0.31, P11 0.34 -> 0.37, P12 0.28 unchanged | no | none | CAD, FIN-005 | none | none | socket mouth moves to x 0.1105, wing cove clearance not checked "-" | `path_options.txt` V2a |
| J2 J1 plus 24 mm square socket | +9.5 per saddle (+19) | P10 0.31, P11 0.38, P12 0.35, P14a 0.32 | no | none | CAD | none | none | wing cut-out | V2b |
| J3 Root block socket 71 mm, 24 mm square | +10 per block (+20) | P7 0.26 -> 1.28, P8 0.51 -> 1.09, P11 0.75, P6 0.50 -> 0.76 | partly (P6 0.76) | none | CAD FIN-003, fairing slot | none | fairing wider | fairing / box clearance "-" | V3 |
| J4 Rearrange: print orientation so junction stress lies in the layer plane (drawing rule) | 0 | allowable 20 vs 9.5 MPa: P12 0.28 -> about 0.59, P6 -> about 1.05, P8 -> about 1.08 (hand scaling x2.1, not run) | partly | needs the coupon | print setup | none | none | P12 still needs 34 MPa | ASM-A-PETG-ALLOW (20 MPa in-layer, EST) |
| J5 Change approach: replace printed saddle / block by CF or aluminium fittings | "-" (not designed) | removes the PETG limit; metal allowables not in the repo | unproven | proven in RC practice (not cited here) | machining, Jacobs tools | clamp | none | CAD fidelity needs vendor drawings; cost "-" | none |
| J6 Change approach: continuous CF load member (rib continued through the spar to a second socket, or a CF plate bonded across the wing) | "-" | removes the junction as the limit | unproven | none | new part | more steps | none | spar / core cut-outs | none |
| J7 Add: pocketed shoe plate (2 mm walls) so the PSA carries retention only; pad 15 x 12 -> 15 x 20 | +0.5 per foot (+2) | shear area x1.7; pocket removes PSA shear; peel lever unchanged | partly | print feature | CAD shoe plate | pad slides into the pocket (C9 already slides from aft) | none | track and stroke unchanged | `path_full.txt` P1 |
| J8 Change approach: epoxy-bond the pad (foam-safe CA / epoxy) | 0 | bond allowable on EVA/PE "-" | unproven | foam substrate fails first "-" | bonding | cure | none | needs a coupon | none |

No single option in the screening reaches RF >= 1.0 for every row: the three problem groups (rib torsion, printed junctions P6 / P12 / P11, spar torsion P14a) need a combination (for example R1 + J3 + J4 + a larger saddle junction), and every allowable behind these rows is EST until the section 9 coupons are done.

### 7.3 F3 options: pad face vs drag-test hold point; landing surface
- **F3a, adopt the UHMW-PE face now.** +0.2 g EST; needs an A BOM line with a price read for A (the $4.91 is K09-L, findtape.com 2026-11-14; no new price read here) and CAD (a 0.1-0.2 mm face on GER-002, step C9). Screening V1: mu 0.30 lifts the rib 0.86 -> 1.23; the printed joints stay below 1.
- **F3b, drag test as a hold point before the first free landing.** On each defined surface: pad loaded to the 30 N plateau, breakaway (static) force over normal force, n >= 5; pass if mu_static <= 0.40 (and <= the value the final structure is rated for); a fail routes to F3a. Cost $0; claim `ASM-A-PAD-MU`.
- **Landing-surface definition (proposal for MISSION / REQUIREMENTS):** no surface is defined in MISSION.md, REQUIREMENTS-A.md or A.param ("-"). Proposal: name the surfaces (for example dry mown grass, dry asphalt or concrete: team to confirm), state mu_static per surface after the drag test, forbid landing on an untested surface; grass needs its own test with the pad in the grass (snagging acts as extra friction).
- **F3c joint acceptance:** side load scales with mu x peak normal (plateau + damping); accept by rerunning `landing_path_a.py` with the measured plateau (crush coupon) and measured mu_static, not by two independent limits.

### 7.4 F5 card items and F4 reconciliation (proposals, not card text)
- Do not publish 0.5 m/s as a card limit: it cannot be observed at 0.3 m height and SITL already reached 0.52 m/s (29 records). Use 0.70 m/s (EST, +35 % on the SITL maximum) as the analysis envelope (`ASM-A-DRIFT-ENVELOPE`).
- Observable items: land into the wind; belly-on landing only to 3 m/s (kept); go around if the aircraft is visibly translating or leaning in the direction of travel below about 1 m; interim lean <= 10 deg when translating (12 deg tips at 0.52 m/s in the scan).
- ArduPilot: the only A.param facts used are the vertical rates at l.116-119 (Q_WP_SPD_DN 1.2, Q_LAND_FINAL_SPD 0.3, Q_LAND_FINAL_ALT 6); no horizontal-speed limit is there. Parameter names for lean or horizontal speed bounds in the final descent are **not verified** here; a cited check against the ArduPilot docs is open ("-").
- F4: not done (SITL not to be run here): add the land-detector and spool-down behaviour to landing_a.py, or remove the artificial angular damping in the `a_plant.py` contact (`al - 8.0*w` when 3 or more feet touch) and rerun Z5_b0, Z5_gb45, Lb_5e on the CAD geometry.

## 8. Proposed AR-012 revision (ten fields plus limits, for `docs/analysis-records.md`; the conductor places it)
### AR-012 Landing foot side load, load-path part checks and tip-over on the CAD ground plane (T-064r, R-PHY-09; 2026-11-19, supersedes the first issue of the same day)
- **Category:** rigid-body dynamics (explicit 6-DOF, four elasto-plastic foot springs, Coulomb friction) plus hand-calculation part checks (tube, bond, rectangular-section statics); illustrative option screening (`landing_path_options_a.py`, `landing_tip_options_a.py`). No FEA.
- **Solver / engine:** `redesign/qp/A/structures/landing_a.py` (CAD geometry default, `--legacy` for the earlier hand geometry), `landing_side_a.py`, `landing_sitl_env_a.py`, `landing_lean_scan_a.py`, `landing_path_a.py`, `landing_sitl_records_a.py`; Python 3.14, numpy; dt 1e-4 s (AR-008 sets) / 2e-4 s (path, scan; RF converged to 0.1 % per review R4), T 1.2-1.5 s.
- **Model version:** git HEAD f2707f19 plus the uncommitted tree of 2026-11-19 (another session was editing `cad/amodel/electrical.py` and `wing.py` outside the landing geometry); `sitl/cad_mass.json` of 2026-11-18 (regenerated 2026-11-19: CG identical to 0.01 mm); ITEMS mass list with motor assemblies 4 x 88.26 g.
- **Inputs:** ground plane x 0.3375 m, fin y 0.38, pad centre z 0.177 (edge 0.183), pad 12 x 15 x 30 mm (electrical.py); CG (21.369, -2.034, 6.369) mm (cad_mass.json); mass 1.50 kg (gate); rib 14x12 x 0.0705-0.286, fin tube 16x14, saddle / block / shoe dimensions from wing.py and electrical.py; plateau 30 N (EST), mu 0.40 (K09-L pad_mu_max; A pad unmeasured), sink 1.2 / 0.5 m/s (AR-008); 29 SITL touchdown records (lateral <= 0.52 m/s, peak sink <= 0.34 m/s, lean <= 29.1 deg); allowables EST from structures_a.py (CF 350 / 30 MPa, PETG_ILAY 9.5, PETG_BEAR 20, BOND 2.0, PSA 0.10 with no source; KF 1.725, KP 2.156).
- **Assumptions:** fin and rib rigid in the dynamics; both feet of one fin summed; normal and side peaks simultaneous for the bond checks; no thrust or control after 0.6 s (pessimistic bound); print orientation unknown so the interlayer allowable is used; peel allowable = BOND 2.0 MPa (EST lower bound); PSA peel with a rigid pad; spar check counts foot loads only; inertia from the ITEMS roll-up.
- **Boundary conditions / loads:** the 10 AR-008 cases; 10 SITL-record cases (five records, both axes) plus one 16 deg wide + 0.5 m/s case; lean x lateral-speed scan (lean 0-24 deg, lateral 0-0.70 m/s, both signs, with / against travel, centre / edge foot); mu 0.30-0.70 and plateau 24 / 27 / 30 N sweeps.
- **Numerical settings:** as above; Coulomb friction regularised at 0.02 m/s; rigid stop 5e5 N/m at 20 mm; tipped = end tilt > 45 deg.
- **Outputs:** `redesign/qp/A/mechanism/out/T064r_landing.md`, `T064r_data/` (landing_30_cad, landing_30_legacy, landing_side_cad, sitl_env_cad, sitl_records, lean_scan_cad, path_full, path_options, tip_options, claims_T064r_draft.json, logs).
- **Acceptance criteria:** (i) A-P9 static narrow-axis tip-over >= 30 deg; (ii) every part on the CAD load path RF >= 1.0 at KF 1.725 (CF) / KP 2.156 (printed, bonded) at the governing loads and pad mu <= the measured static value; (iii) stroke <= 20 mm, n <= 12 g, end tilt <= 3 deg (AR-008); (iv) no tip-over inside the card-allowed touchdown envelope (lean <= 10 deg with translation, lateral speed <= 0.70 m/s EST). One criterion: RF >= 1.0 (KF / KP already hold the factors); no separate 0.15 margin.
- **Result:** (i) **FAIL: 29.19 deg (pad edge) / 28.36 deg (pad centre) toward the CG side**, 0.8 deg short (the earlier 33.0 deg used a ground plane 37.5 mm too high). (ii) **FAIL with EST allowables:** minimum 0.02 (pad PSA peel, no allowable source) and 0.28 (printed saddle socket-to-ring junction); rib tube 0.86 (friction yaw-slip couple 5.0 N m, SITL-record wide-axis cases) and 1.24 (AR-008 set); fin tube 3.9. (iii) PASS: stroke 17.5 mm, n 10.79 g, tilt 2.5 deg. (iv) Pessimistic sim tips at 12 deg / 0.52 m/s and 10 deg / 0.60-0.70 m/s with the lean in the travel direction; card-allowed SITL touchdowns reach 11.0-12.1 deg at 0.45-0.50 m/s. The 14 N cap stays withdrawn (it was K09-L's design demand scaled by mass).
- **Limits / validity:** every allowable is EST (no coupons); pad mu, foam plateau, PSA product and print orientation unmeasured; the yaw-slip result needs the 6.4 mm CG z offset and depends on the friction regularisation; sim and SITL not reconciled (SITL has angular damping); rigid fin and rib (no 7 deg rib twist); FIN-005 / FIN-003 / GER-001 listed masses are 18x / 7x / 4x below the CAD solid volume; the options are screening, not designs.

## 9. Proposed D-213 replacement items and follow-ups (for the conductor)
- D-213 (rev) should record: cap withdrawn (stands); "rib governs, PASS" withdrawn; A-P9 FAIL on the CAD (29.2 deg); load-path minimum RF as in section 3; ladder decision pending with section 7; coupons: RMRC rib twist, pad static mu per surface, printed joint, pad attachment drop rig, crush plateau; landing-surface definition open.
- Proposed new tasks: (a) FIN-005 / FIN-003 / GER-001 mass entries vs CAD volume (CAD edit, not mine); (b) `structures_run.md` s5 regeneration on the CAD geometry (landing_a.py default changed); (c) A-P9 value in REQUIREMENTS-A.md (33.2 EST vs CAD 29.2); (d) reconcile `a_plant.py` and landing_a.py (F4); (e) restore `cad/out/assembly.json` or document why it is deleted (blocks `run_all.py`).
- Open ("-"): static-margin limit (for T4), landing-surface list, PSA product, print orientation, infill of FIN-003 / FIN-005 / GER-001, ArduPilot parameter names for lean / horizontal speed.
