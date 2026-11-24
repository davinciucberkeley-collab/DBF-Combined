# T-101 U4: plant edit and SITL rerun, elevon chord 0.30 + C3 controls (C4), 2026-11-23

Result: all four T101C4 runs have all_pass true (`redesign/qp/A/mechanism/out/T101_results.json`). Highest pitch use 0.5427 (T-074 + Lua), limit 0.60.

## 1. Plant edits (`redesign/qp/A/sitl/a_aero.py`)
| Item | Old | New | Source |
|---|---|---|---|
| EL_CF | 0.25 | 0.30 | conductor decision; scout `docs/audits/2026-11-23-T101-scout-trim.md` s3.3; CAD `chord/U1_cad.md` |
| EL_TAU | 0.5 | 0.5 x tau(0.30)/tau(0.25) = 0.5424863 | thin airfoil tau(E) = 1 - (theta - sin theta)/pi, theta = arccos(2E-1); ratio about 1.085 (CALC) |
| EL_S | 0.0380 m2 | 0.04557 m2 (formula unchanged, uses EL_CF) | |
| CLD | 0.3226 /rad | 0.4200 /rad | CLA x EL_TAU x EL_S/S_W |
| EL_X | -(0.875 C_W - CG_X) = -192.8 mm at new CG | -((1 - EL_CF/2) C_W - CG_X) = -186.7 mm | centroid at 1 - cf/2 of chord |
| `set_cg` | same 0.875 | same expression with EL_CF | |
| HINGE_CH | -0.60 (EST) | unchanged | hinge moment scales with ce^2 via `se * ce` (a_aero.py line about 121) |

Other uses in `redesign/qp/A/sitl/*.py` (grep 0.875, 0.25 * C_W, EL_CF, EL_TAU, EL_X): a_aero.py lines 31-37, 46-47, 107, 121 (all consistent now); fwd_checks.py line 39 only prints A.EL_CF, EL_S, CLD, EL_TAU (follows automatically). No other file uses them. cad_mass.json was NOT regenerated. EL_IH reads cad_mass.json (already new).

Caveat: cad_mass.json was already the new CAD (CG 21.567 mm, EL_IH 1.96e-5) before the "old" fwd_checks run, so U4_fwd_checks_old.txt is old chord with new CG and new inertia (the old-CG case is only in the trim table). fwd_checks was run with `python -I -c "sys.path.insert(0,'.'); runpy.run_path('fwd_checks.py')"` because `-I` drops the script directory from sys.path (plain `python -I fwd_checks.py` raised ModuleNotFoundError a_aero).

## 2. fwd_checks old vs new (`U4_fwd_checks_old.txt`, `U4_fwd_checks_new.txt`)
| Line | Old chord | New chord |
|---|---|---|
| elevon area / CL_delta / tau | 0.0380 m2 / 0.323 / 0.50 | 0.0456 m2 / 0.420 / 0.54 |
| 1.500 kg, 17 m/s: trim, hinge per elevon | 5.0 deg, 0.0107 N m | 3.9 deg, 0.0122 N m |
| 1.500 kg, 15 / 18 m/s hinge | 0.0117 / 0.0102 N m | 0.0133 / 0.0116 N m |
| roll rate, +-15 deg at 17 m/s (req 90 deg/s) | 132 deg/s | 172 deg/s |
| peak hinge moment 18 m/s, 20 deg stop vs servo 0.167 N m | 0.0483 N m, ratio 3.5 | 0.0696 N m, ratio 2.4 |

## 3. Steady cruise trim, 17 m/s (`U4_trim.txt`, script `u4_trim.py`)
Own solve: lift = weight and zero pitch moment from `a_aero.airframe` (no thrust term), so it reads about 0.75 deg above the scout figure 6.54 deg at old CG (the scout s2 method was not reproduced exactly); the differences between rows are the useful part.

| Case (m = 1.881 kg) | CG mm | alpha deg | Trim deg TE up | SM % | CLD /rad | EL_X mm |
|---|---|---|---|---|---|---|
| old chord, old CG | 22.049 | 7.37 | 7.29 | 7.61 | 0.3226 | -192.3 |
| old chord, new CG | 21.567 | 7.39 | 7.53 | 7.81 | 0.3226 | -192.8 |
| new chord, new CG | 21.567 | 7.42 | 6.00 | 7.81 | 0.4200 | -186.7 |

At 1.883 kg: 7.31 / 7.54 / 6.01 deg. CG effect +0.24 deg (worse); chord effect -1.53 deg. Ratio 6.00/7.53 = 0.80, the scout predicted 1/1.26 = 0.79. SITL mean elevon in the last 5 s of cruise (case.fwd.csv): C3 6.34-7.04 deg, C4 5.24-5.76 deg TE up.

## 4. Mass arithmetic
m = basic x growth_factor + overrun_frac x gate (CALC-A-MASS-PRED, `proofs/claims_a1_flight.py` lines 75-80; params-A.json mass.growth_factor 1.1174, overrun_frac 0.032, req.mass_gate_kg 1.47). Check old: 1.64098 x 1.1174 + 0.032 x 1.47 = 1.83364 + 0.04704 = 1.88068, 1.881 (matches). New: 1.64288 x 1.1174 + 0.04704 = 1.83576 + 0.04704 = 1.88280, so **1.883 kg EST** (CAD basic 1.64288 kg, cad_mass.json).

## 5. SITL
Script `chord/run_sitl_t101_chord.sh` = `run_sitl_t101.sh` with mass=1.881 changed to 1.883 (4 lines), log path changed to chord/sitl_batch_$CAND.log (the header comment line was also reworded). Command: `bash redesign/qp/A/mechanism/out/T101_data/chord/run_sitl_t101_chord.sh C4 "fw_hold=1.0 P:TECS_SPDWEIGHT=0.5"`; the C3 argument set was confirmed as fw_hold=1.0 plus TECS_SPDWEIGHT 0.5 (AR-017 line 420; `sitl_T101C3_Z5/A_sitl.parm` TECS_SPDWEIGHT 0.5). Wall times (`chord/sitl_batch_C4.log`): Z5 301 s, Z5 Lua 300 s, T-074 139 s, T-074 Lua 139 s; all exit 0, no rerun needed.

Collection: the runs wrote no sum.json (the shell script does not call fwd_sum), so `python -I redesign/qp/A/sitl/fwd_sum.py <4 tags>` was run first (output `U4_fwd_sum.out`), then `python -I redesign/qp/A/mechanism/out/T101_data/t101_collect.py C1 C2 C3 C4` (this also rewrote the C1-C3 entries from their existing run dirs; copies in `T101_data/sitl_T101C4_*`).

## 6. Per-run table against C3 and the limits
Pitch use unrounded = peak mean elevon deg / 15 (`U4_unrounded.txt`).

| Run | pitch use C3 -> C4 | peak mean elevon deg C3 -> C4 | elevon_max deg C3 -> C4 | hinge_peak N m C3 -> C4 | V_end C3 -> C4 | cruise elevon, last 5 s, deg TE up C3 -> C4 | all_pass C4 |
|---|---|---|---|---|---|---|---|
| Z5 | 0.5543 -> 0.4807 | 8.315 -> 7.210 | 8.3 -> 7.2 | 0.019 -> 0.0228 | 17.0 -> 17.1 | 6.98 -> 5.70 | true |
| Z5 Lua | 0.5713 -> 0.4843 | 8.570 -> 7.265 | 8.6 -> 7.3 | 0.0209 -> 0.0248 | 17.0 -> 17.0 | 7.04 -> 5.76 | true |
| T-074 | 0.6507 -> 0.5027 | 9.760 -> 7.540 | 9.8 -> 7.5 | 0.0209 -> 0.0234 | 17.7 -> 17.7 | 6.51 -> 5.43 | true |
| T-074 Lua | 0.6050 -> 0.5427 | 9.075 -> 8.140 | 9.1 -> 8.1 | 0.0203 -> 0.0263 | 17.6 -> 17.6 | 6.34 -> 5.24 | true |

Other T-097 limits, C4 (all pass): peak altitude 85.0-90.5 m (< 110); climb 33.9-39.5 m (< 60); 1.3 Vs reached at 8.5-9.9 s (<= 15); cap run 0.0 s (<= 1); time at motor >= 0.85 0 s (<= 1); elevon saturation 0 s (<= 1); no touch in flight; u_max 0.751-0.791; pack peak 30.2-32.2 A; QLAND sink peak 0.29 (Z5) and 0.31 (Z5 Lua) m/s (<= 1.2); no tip-over. Hinge peak 0.0263 N m against servo 0.167 N m (fwd_checks, ES3352HV at 6 V).

## 7. Limits and validity
One sample per case; repeat scatter 0.01-0.03 (AR-017). T-074 Lua improves least (0.605 -> 0.543, margin 0.057 to the limit). Elevon effectiveness (EL_TAU ratio), HINGE_CH and elevon lag are EST; no wind or gust; SITL hinge peaks rise 12-30 % with chord (EST HINGE_CH). Flutter margin is not part of this run (see `U2_flutter.md`).

## 8. Toolchain (as AR-015/AR-017)
`sitl/run_fwd.py` + `sitl/fwd_sum.py`; ArduPlane SITL (ArduPilot bf693f31, 4.7.3-beta1, per AR-017), pymavlink 2.4.50, JSON backend, speedup 8, `A_MOTOR=x2216`, venv at `C:/Users/dillo/tools/ardupilot-sitl/venv`; ArduPlane.elf SHA-256 not re-hashed in this run (unknown). Tree: working tree with the uncommitted a_aero.py edit above; A.param, a_plant.py, lua/spin_cap.lua untouched.
