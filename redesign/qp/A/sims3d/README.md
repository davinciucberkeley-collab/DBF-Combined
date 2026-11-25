# sims3d: data export for the 3-D viewer (T-105 unit 1)

Data only; no viewer code. Written 2026-11-23. Nothing here is committed. `redesign/site`, the ledger, spec files and CHANGE-LOG are untouched; the only existing file edited is `redesign/qp/A/structures/landing_a.py` (opt-in flag, section 2).

## Commands (from the repo root; Python 3 with numpy and scipy)
| Output | Command | Time |
|---|---|---|
| `out/flight_<run>.json` x 16 | `python -I redesign/qp/A/sims3d/export_flight.py [run ...]` | seconds |
| `out/landing_<case>.json` x 10 | `python -I redesign/qp/A/sims3d/run_landing_traces.py [--cad-mass <json>] [--nproc N]` | about 6 min on 10 cores |
| same, via the flag directly | from `redesign/qp/A/structures/`: `LAND_TRACE=<dir> LAND_MASS_KG=1.881 LAND_MASS_MODEL=cad LAND_PART_TABLE=../mechanism/out/T098_data/cad_part_table_t097.json LAND_RIB_OD=0.025 LAND_RIB_ID=0.023 python -I landing_a.py 37.5` (uses the working-tree CG, see the CG note) | about 5 min |
| `out/linkage.json` | `python -I redesign/qp/A/sims3d/export_linkage.py [step_deg]` | 20 s |
| pass check | `python -I redesign/qp/A/sims3d/verify_exports.py [--md]` (exit 0 = all match) | seconds |

## 1. Flight files (`flight_<run>.json`)
Runs (16): `T097_{T074,T074_lua,Z5,Z5_lua}` and `T101C{1,2,3}_{T074,T074_lua,Z5,Z5_lua}` (the T-074-type runs used by T-097 are `T097_T074*`, as listed in `mechanism/out/T097_results.json`; the T101 runs are those of `T101_results.json`). Source: `sitl/runs/<run>/case.fwd.csv`, `case.events.json`, `result.json`.
Top level: `meta`, `events`, then one array per field, all the same length; 10 Hz (first plant sample at or after each 0.1 s tick, plus the last sample), values rounded to 3 decimals.
- Fields: `t, pn, pe, alt, pitch, roll, hdg_nose, dl, dr, th1, th2, th3, th4, V, alpha, touch, pitch_use_15`.
- `meta`: `run, mass_kg, setup` (driver args, plant cfg, transition entry), `lua`, `rate_hz, n_samples, n_source_samples, duration_s`, `pass_fail`, `pitch_use_scalar` (15/20/25 deg bases and max elevon, from `sitl/fwd_sum.py` `trans()`), `summary`, `conventions`, `fields`.
- `meta.pass_fail`: `result.json` carries no pass/fail lines. The lines come from `mechanism/out/T101_results.json` `runs[run].checks` (all 16 runs: value, limit, pass) with `all_pass`; `ar015_rows` are the AR-015 rows of `T097_results.json` (T097 runs only, empty for T101 runs).
- `events`: `source_case_events_json` (is `[]` in all 16 runs: the plant writes events only when a `cmd_file` is used), `marks` (t_armed, t_qstab, t_fbwa, t_fwdone, t_cruise_mode, t_cruise_end, t_back, t_qland, ...), `modes` ([t, mode]), `events` ([t, text], autopilot messages). Mark times come from the driver clock and sit about 0.1-0.4 s off the plant clock `t` (e.g. `t_fbwa` 100.924 against the FBWA mode line at 101.22): do not draw sub-second alignments from them.

### Conventions (checked against `sitl/a_plant.py` `euler_rpy`, `step`, `fwd_loads` and `sitl/a_aero.py` `airframe`)
- World NED: `pn` north (+N), `pe` east (+E) in m from the start point; `alt` = up from the ground plane, m (start 0.314 m = fin feet on the ground).
- Body FRD in cruise attitude (x nose, y right wing, z belly). Hover = nose up (x_b up); copter forward = +z_b (belly); copter down = -x_b (tail).
- `pitch` = asin(-x_b . down) = nose elevation above the horizon: **+90 deg = nose straight up (the hover / tailsitter stance)**, 0 = level cruise; the forward transition runs 90 to about 0, the back transition 0 to 90. The CAD is built in cruise attitude (x nose), so draw it with `pitch` about the body y axis, nose-up positive.
- `roll` = atan2(y_b.z, z_b.z), deg about the nose axis, 0 = upright cruise, + = right wing down. Undefined at pitch near 90 (the CSV jumps between 0 and 180): ignore it while pitch > about 80.
- `hdg_nose` = atan2(x_b east, x_b north), deg from north, clockwise; also undefined at pitch near 90. In hover the plant's copter-forward heading (`hdg_belly`, not exported) is the meaningful yaw.
- `dl` / `dr`: left (-y) / right (+y) elevon, deg, **trailing edge down positive** (a_aero: `Mx += EL_Y*FzR - EL_Y*FzL`; SERVO5 = left, SERVO6 = right); plant stops +-20 deg.
- `th1..th4`: motor thrust, N, per motor. `V`: airspeed, m/s (x-z body plane, wind-relative); `alpha`: deg, + = relative wind from below the nose; `touch`: 0-4 fin-foot contacts (0 = airborne).
- `pitch_use_15`: |0.5 (dl+dr)| / 15 per sample (the AR-015 pitch-use share); `meta.pitch_use_scalar.pitch_use_15` is the max over t_fbwa..t_cruise_end (matches the AR-015 values 0.69 / 0.77-0.79 against the 0.60 line).
- `t` starts at 0.05 s (plant clock). T074-type files cover about 112 s, Z5 files about 257 s.
- Static copies of the SITL outputs as of this export; if T-101 re-runs a `T101C*` run, re-export it.

## 2. Landing time histories (`landing_<case>.json`, 200 Hz, 301 samples)
Opt-in flag in `structures/landing_a.py`: environment variable `LAND_TRACE=<directory>`. With it set, `__main__` writes one `landing_<case>[_<Fp>N].json` per case into that directory. `simulate(..., hist=list)` is the underlying hook (`hist=None` by default; the recorder only reads state); `write_trace()` formats and downsamples (full-rate peaks are kept in `peaks`).
Fields: `t` (s), `p` (CG position, world axes, m, Z up, ground z = 0), `quat_wxyz` (body to world), `tilt_deg` (body +x against world down, 0 = upright stance), `crush_mm` (4 pads, penetration depth), `set_mm` (4 pads, permanent set), `force_N` (4 pads, normal force), `load_factor_g` (sum of pad normal forces / m g, the `n_peak` definition, rotor lift excluded), `rotor_lift_frac` (lam ramp: 0.667 to 0.3 s, then to 0 at 0.6 s). `meta.limits` = stroke 20 mm, tilt 3 deg, load factor 12 g. `meta.pads`: order (sy, sz) = (+1,+1), (+1,-1), (-1,+1), (-1,-1); y = sy x 0.38 m (fin), z_body = sz x z_foot. `peaks` = the printed row of `landing_a.py` plus full-rate maxima.
Frame: body x aft (down in the stance), y right, z cruise-up (world +X in the stance); `R0` = body to world in the upright stance (landing_a.py header).
- Case = D-243 chosen point: Fp 37.5 N, zeta 0.05, usable stroke 20 mm, rib 25x23 (`LAND_RIB_OD=0.025 LAND_RIB_ID=0.023`), 1.881 kg, CAD mass model with the T097 part table, mu 0.40: the inputs of `mechanism/out/T098_data/sweep_t098.py` and `landing_cad_1881_p37p5_rib25.txt`.
- **CG note.** `landing_a.py` reads the CG from the working-tree `sitl/cad_mass.json`, which changed after T-098 (T-101 chord work, uncommitted: CG x 22.049 to 20.688 mm). With it the ten cases do NOT reproduce T-098 (for example hard 10 narrow + drift .5: n 5.43 g, not 7.05; rib RF 7.49, not 7.62 for hard level). `run_landing_traces.py` therefore defaults to `sims3d/T098_cad_mass.json` (= `git show HEAD:redesign/qp/A/sitl/cad_mass.json`, the CG T-098 used). With it all 40 compared peaks (4 metrics x 10 cases) equal the `T098_results.json` `chosen_37.5N_rib25x23` rows: **0 mismatches**. Pass `--cad-mass ../sitl/cad_mass.json` for current-CAD histories. The files in `out/` are the T-098 basis (`meta.cad_mass_source`, `meta.cg_m`). Regenerate against the current CAD once T-101 settles if the viewer should show the new CG.
- Default behaviour check: `python -I landing_a.py` (no env) before and after the edit: stdout byte-identical (`cmp`; sha256 prefix 8c54efa81cf81a07 for both). The T-098-env run (`landing_a.py 37.5`) with `LAND_TRACE` set also prints a table byte-identical to the unedited code. Without the flag `landing_a.py` writes no files.

## 3. Linkage (`linkage.json`)
`R` (+y) and `L` (-y) pose lists, delta from -ELEV_STOP to +ELEV_STOP deg in 0.5 deg steps (85 per side). Per pose: `delta_deg`, `servo_theta_deg`, `arm_tip_mm`, `horn_hole_mm` (CAD frame: x aft, y span, z up, mm), `rod_len_mm`, `gear_ddelta_dtheta`, `horn_transmission_deg`, `arm_transmission_deg`, `jac_sigma_min`, `hinge_moment_Nm`, `servo_torque_req_Nm`, `rod_force_N`, `residual_m`, `min_clearance_mm` (+ `_pair`), `min_clearance_excl_design_contact_mm` (+ `_excl_pair`). `meta.geometry` holds the hinge axis, arm pivot, ARM_R, HORN_R, rod length; `meta.conventions` the signs (theta counter-clockwise about +z, 0 at neutral; delta + = trailing edge down, same as `dl` / `dr`).
- Clearance = the analytic separating-axis engine of `elevon_sweep_collision.py` over its pair list and exclusions (solid hulls, so a lower bound). All-pairs minimum 0.000 mm (arm on servo case, a declared design contact); excluding design contacts 0.062 mm (this run). Hinge moment = `HINGE_NM` (0.146 N m, EST) x |delta| / ELEV_LIM, the linear model of `elevon_dynamics.py`; the plant's own hinge-moment model is not exported.
- **Must be re-run after T-101 lands.** The exporter reads the working-tree CAD constants, and the working tree already carries part of the T-101 chord edit (ELEV_FRAC 0.30, ARM_R 6.86 mm, HORN_R 7.39 mm, hinge x 171.50 mm; see `git diff redesign/qp/A/cad/amodel/`, marked "D-number pending"). So `linkage.json` is the new-chord geometry as of now and differs from the committed `mechanism/out/linkage_kinematics.csv` and `linkage_sweep_collision.csv` (old chord; for example theta at delta +20 is 21.68 here, 21.67 there; delta 0 identical). If T-101 changes the constants again, re-run `export_linkage.py` (20 s).

## 4. Sizes (KB)
| file | KB |
|---|---|
| flight_T097_T074.json | 107.7 |
| flight_T097_T074_lua.json | 108.4 |
| flight_T097_Z5.json | 251.2 |
| flight_T097_Z5_lua.json | 252.1 |
| flight_T101C1_T074.json | 104.9 |
| flight_T101C1_T074_lua.json | 105.4 |
| flight_T101C1_Z5.json | 251.4 |
| flight_T101C1_Z5_lua.json | 253.3 |
| flight_T101C2_T074.json | 104.8 |
| flight_T101C2_T074_lua.json | 105.5 |
| flight_T101C2_Z5.json | 251.6 |
| flight_T101C2_Z5_lua.json | 253.3 |
| flight_T101C3_T074.json | 104.7 |
| flight_T101C3_T074_lua.json | 105.5 |
| flight_T101C3_Z5.json | 251.1 |
| flight_T101C3_Z5_lua.json | 253.6 |
| landing_hard_10_narrow.json | 50.1 |
| landing_hard_10_narrow_neg.json | 49.5 |
| landing_hard_10_narrow_plus_drift_p5.json | 49.2 |
| landing_hard_10_wide.json | 49.3 |
| landing_hard_10_wide_plus_drift_p5_y.json | 49.6 |
| landing_hard_7-7_combo.json | 49.0 |
| landing_hard_level.json | 49.7 |
| landing_normal_10_narrow_p5.json | 48.7 |
| landing_normal_10_wide_p5_plus_drift.json | 48.6 |
| landing_normal_level_p5.json | 49.1 |
| linkage.json | 90.0 |
| total | 3447.3 |

## 5. Pass check
`python -I redesign/qp/A/sims3d/verify_exports.py` exits 0: every JSON loads; 137 comparisons, 0 mismatches. Flight values (5 per file, 16 files) are compared with an independent re-read of the source `case.fwd.csv` at the same `t`; landing values (4 T-098 metrics plus Fmax per file) with `T098_results.json` and `landing_cad_1881_p37p5_rib25.txt`; linkage values (5 servo angles, gear, rod length) with an independent `scipy.optimize.brentq` re-solve of `linkage_core.g`, a central difference, and `L_ROD`.

| file | value | exported | source | result |
|---|---|---|---|---|
| flight_T097_T074.json | alt @t=22.722 | 0.314 | 0.314 | ok |
| flight_T097_T074.json | pitch @t=56.832 | 89.5 | 89.5 | ok |
| flight_T097_T074.json | dl @t=37.820 | -0.0 | -0.0 | ok |
| flight_T097_T074.json | V @t=85.247 | 0.04 | 0.04 | ok |
| flight_T097_T074.json | th1 @t=113.460 | 0.581 | 0.581 | ok |
| flight_T097_T074_lua.json | alt @t=22.722 | 0.314 | 0.314 | ok |
| flight_T097_T074_lua.json | pitch @t=56.832 | 89.5 | 89.5 | ok |
| flight_T097_T074_lua.json | dl @t=37.820 | -0.0 | -0.0 | ok |
| flight_T097_T074_lua.json | V @t=85.247 | 0.03 | 0.03 | ok |
| flight_T097_T074_lua.json | th1 @t=113.460 | 0.61 | 0.61 | ok |
| flight_T097_Z5.json | alt @t=52.307 | 28.527 | 28.527 | ok |
| flight_T097_Z5.json | pitch @t=130.743 | 20.86 | 20.86 | ok |
| flight_T097_Z5.json | dl @t=87.128 | -0.0 | -0.0 | ok |
| flight_T097_Z5.json | V @t=196.115 | 1.21 | 1.21 | ok |
| flight_T097_Z5.json | th1 @t=261.385 | 0.0 | 0.0 | ok |
| flight_T097_Z5_lua.json | alt @t=52.206 | 28.617 | 28.617 | ok |
| flight_T097_Z5_lua.json | pitch @t=130.540 | 20.13 | 20.13 | ok |
| flight_T097_Z5_lua.json | dl @t=87.027 | -0.0 | -0.0 | ok |
| flight_T097_Z5_lua.json | V @t=195.708 | 1.21 | 1.21 | ok |
| flight_T097_Z5_lua.json | th1 @t=260.927 | 0.0 | 0.0 | ok |
| flight_T101C1_T074.json | alt @t=22.316 | 0.314 | 0.314 | ok |
| flight_T101C1_T074.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C1_T074.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C1_T074.json | V @t=83.621 | 0.01 | 0.01 | ok |
| flight_T101C1_T074.json | th1 @t=111.427 | 0.723 | 0.723 | ok |
| flight_T101C1_T074_lua.json | alt @t=22.214 | 0.314 | 0.314 | ok |
| flight_T101C1_T074_lua.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C1_T074_lua.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C1_T074_lua.json | V @t=83.519 | 0.0 | 0.0 | ok |
| flight_T101C1_T074_lua.json | th1 @t=111.325 | 0.641 | 0.641 | ok |
| flight_T101C1_Z5.json | alt @t=52.511 | 28.93 | 28.93 | ok |
| flight_T101C1_Z5.json | pitch @t=131.302 | 65.8 | 65.8 | ok |
| flight_T101C1_Z5.json | dl @t=87.535 | -0.0 | -0.0 | ok |
| flight_T101C1_Z5.json | V @t=196.928 | 1.2 | 1.2 | ok |
| flight_T101C1_Z5.json | th1 @t=262.503 | 0.0 | 0.0 | ok |
| flight_T101C1_Z5_lua.json | alt @t=52.714 | 29.207 | 29.207 | ok |
| flight_T101C1_Z5_lua.json | pitch @t=131.811 | 78.64 | 78.64 | ok |
| flight_T101C1_Z5_lua.json | dl @t=87.840 | -0.0 | -0.0 | ok |
| flight_T101C1_Z5_lua.json | V @t=197.742 | 1.21 | 1.21 | ok |
| flight_T101C1_Z5_lua.json | th1 @t=263.520 | 0.0 | 0.0 | ok |
| flight_T101C2_T074.json | alt @t=22.214 | 0.314 | 0.314 | ok |
| flight_T101C2_T074.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C2_T074.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C2_T074.json | V @t=83.519 | 0.01 | 0.01 | ok |
| flight_T101C2_T074.json | th1 @t=111.325 | 0.738 | 0.738 | ok |
| flight_T101C2_T074_lua.json | alt @t=22.214 | 0.314 | 0.314 | ok |
| flight_T101C2_T074_lua.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C2_T074_lua.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C2_T074_lua.json | V @t=83.519 | 0.01 | 0.01 | ok |
| flight_T101C2_T074_lua.json | th1 @t=111.325 | 0.762 | 0.762 | ok |
| flight_T101C2_Z5.json | alt @t=52.612 | 29.037 | 29.037 | ok |
| flight_T101C2_Z5.json | pitch @t=131.506 | 78.24 | 78.24 | ok |
| flight_T101C2_Z5.json | dl @t=87.738 | -0.0 | -0.0 | ok |
| flight_T101C2_Z5.json | V @t=197.335 | 1.2 | 1.2 | ok |
| flight_T101C2_Z5.json | th1 @t=263.012 | 0.0 | 0.0 | ok |
| flight_T101C2_Z5_lua.json | alt @t=52.612 | 29.206 | 29.206 | ok |
| flight_T101C2_Z5_lua.json | pitch @t=131.709 | 79.54 | 79.54 | ok |
| flight_T101C2_Z5_lua.json | dl @t=87.840 | -0.0 | -0.0 | ok |
| flight_T101C2_Z5_lua.json | V @t=197.538 | 1.19 | 1.19 | ok |
| flight_T101C2_Z5_lua.json | th1 @t=263.317 | 0.0 | 0.0 | ok |
| flight_T101C3_T074.json | alt @t=22.214 | 0.314 | 0.314 | ok |
| flight_T101C3_T074.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C3_T074.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C3_T074.json | V @t=83.519 | 0.0 | 0.0 | ok |
| flight_T101C3_T074.json | th1 @t=111.325 | 0.694 | 0.694 | ok |
| flight_T101C3_T074_lua.json | alt @t=22.316 | 0.314 | 0.314 | ok |
| flight_T101C3_T074_lua.json | pitch @t=55.713 | 89.5 | 89.5 | ok |
| flight_T101C3_T074_lua.json | dl @t=37.108 | -0.0 | -0.0 | ok |
| flight_T101C3_T074_lua.json | V @t=83.621 | 0.01 | 0.01 | ok |
| flight_T101C3_T074_lua.json | th1 @t=111.427 | 0.649 | 0.649 | ok |
| flight_T101C3_Z5.json | alt @t=52.511 | 29.124 | 29.124 | ok |
| flight_T101C3_Z5.json | pitch @t=131.404 | 70.85 | 70.85 | ok |
| flight_T101C3_Z5.json | dl @t=87.637 | -0.0 | -0.0 | ok |
| flight_T101C3_Z5.json | V @t=197.132 | 1.2 | 1.2 | ok |
| flight_T101C3_Z5.json | th1 @t=262.707 | 0.0 | 0.0 | ok |
| flight_T101C3_Z5_lua.json | alt @t=52.714 | 29.44 | 29.44 | ok |
| flight_T101C3_Z5_lua.json | pitch @t=131.811 | 78.91 | 78.91 | ok |
| flight_T101C3_Z5_lua.json | dl @t=87.840 | -0.0 | -0.0 | ok |
| flight_T101C3_Z5_lua.json | V @t=197.742 | 1.21 | 1.21 | ok |
| flight_T101C3_Z5_lua.json | th1 @t=263.520 | 0.0 | 0.0 | ok |
| landing_hard_10_narrow.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 14.559515980852977 | 14.6 | ok |
| landing_hard_10_narrow.json | peaks.n_g vs T098 'peak load factor (g)' | 5.417189630203121 | 5.42 | ok |
| landing_hard_10_narrow.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 1.7544026247336706 | 1.8 | ok |
| landing_hard_10_narrow.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 12.55105049415571 | 12.55 | ok |
| landing_hard_10_narrow.json | peaks.Fmax_N vs T098 txt | 49.98582652461211 | 50.0 | ok |
| landing_hard_10_narrow_neg.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 14.240133455754478 | 14.2 | ok |
| landing_hard_10_narrow_neg.json | peaks.n_g vs T098 'peak load factor (g)' | 5.426392740152902 | 5.43 | ok |
| landing_hard_10_narrow_neg.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 1.6511979538085324 | 1.7 | ok |
| landing_hard_10_narrow_neg.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 10.574968915196365 | 10.57 | ok |
| landing_hard_10_narrow_neg.json | peaks.Fmax_N vs T098 txt | 49.9674243118126 | 50.0 | ok |
| landing_hard_10_narrow_plus_drift_p5.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 17.214793402413108 | 17.2 | ok |
| landing_hard_10_narrow_plus_drift_p5.json | peaks.n_g vs T098 'peak load factor (g)' | 7.047025357158212 | 7.05 | ok |
| landing_hard_10_narrow_plus_drift_p5.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 2.2679732032408872 | 2.3 | ok |
| landing_hard_10_narrow_plus_drift_p5.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 5.382586522534794 | 5.38 | ok |
| landing_hard_10_narrow_plus_drift_p5.json | peaks.Fmax_N vs T098 txt | 50.1312105032199 | 50.1 | ok |
| landing_hard_10_wide.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 8.982056517009784 | 9.0 | ok |
| landing_hard_10_wide.json | peaks.n_g vs T098 'peak load factor (g)' | 5.624179850657479 | 5.62 | ok |
| landing_hard_10_wide.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.11811995890361227 | 0.1 | ok |
| landing_hard_10_wide.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 3.4791980698845384 | 3.48 | ok |
| landing_hard_10_wide.json | peaks.Fmax_N vs T098 txt | 53.04303433136842 | 53.0 | ok |
| landing_hard_10_wide_plus_drift_p5_y.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 11.665333643754716 | 11.7 | ok |
| landing_hard_10_wide_plus_drift_p5_y.json | peaks.n_g vs T098 'peak load factor (g)' | 5.93813294232194 | 5.94 | ok |
| landing_hard_10_wide_plus_drift_p5_y.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.38575839449960536 | 0.4 | ok |
| landing_hard_10_wide_plus_drift_p5_y.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 4.844899096521057 | 4.84 | ok |
| landing_hard_10_wide_plus_drift_p5_y.json | peaks.Fmax_N vs T098 txt | 55.649558486319734 | 55.6 | ok |
| landing_hard_7-7_combo.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 12.41185885349111 | 12.4 | ok |
| landing_hard_7-7_combo.json | peaks.n_g vs T098 'peak load factor (g)' | 6.905004215889674 | 6.91 | ok |
| landing_hard_7-7_combo.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 1.19639722027281 | 1.2 | ok |
| landing_hard_7-7_combo.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 3.3649325556160394 | 3.36 | ok |
| landing_hard_7-7_combo.json | peaks.Fmax_N vs T098 txt | 55.90214824213298 | 55.9 | ok |
| landing_hard_level.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 8.436723947966184 | 8.4 | ok |
| landing_hard_level.json | peaks.n_g vs T098 'peak load factor (g)' | 10.759050250320186 | 10.76 | ok |
| landing_hard_level.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.04317867930609722 | 0.0 | ok |
| landing_hard_level.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 7.622769774442971 | 7.62 | ok |
| landing_hard_level.json | peaks.Fmax_N vs T098 txt | 49.678811905965944 | 49.7 | ok |
| landing_normal_10_narrow_p5.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 3.417364555805158 | 3.4 | ok |
| landing_normal_10_narrow_p5.json | peaks.n_g vs T098 'peak load factor (g)' | 7.872583301496376 | 7.87 | ok |
| landing_normal_10_narrow_p5.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.1493469870496824 | 0.1 | ok |
| landing_normal_10_narrow_p5.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 6.812862588265994 | 6.81 | ok |
| landing_normal_10_narrow_p5.json | peaks.Fmax_N vs T098 txt | 41.96201528621769 | 42.0 | ok |
| landing_normal_10_wide_p5_plus_drift.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 6.8488039074750535 | 6.8 | ok |
| landing_normal_10_wide_p5_plus_drift.json | peaks.n_g vs T098 'peak load factor (g)' | 5.285796621211291 | 5.29 | ok |
| landing_normal_10_wide_p5_plus_drift.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.37621892646091104 | 0.4 | ok |
| landing_normal_10_wide_p5_plus_drift.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 4.38623059408028 | 4.39 | ok |
| landing_normal_10_wide_p5_plus_drift.json | peaks.Fmax_N vs T098 txt | 49.4329516816193 | 49.4 | ok |
| landing_normal_level_p5.json | peaks.stroke_mm vs T098 'foam stroke (mm)' | 2.2806537812100625 | 2.3 | ok |
| landing_normal_level_p5.json | peaks.n_g vs T098 'peak load factor (g)' | 8.902410265049541 | 8.9 | ok |
| landing_normal_level_p5.json | peaks.tilt_end_deg vs T098 'end tilt (deg)' | 0.018515544669979143 | 0.0 | ok |
| landing_normal_level_p5.json | peaks.rib_rf vs T098 'rib-root RF (min over run)' | 5.600408780070303 | 5.6 | ok |
| landing_normal_level_p5.json | peaks.Fmax_N vs T098 txt | 41.218721222605325 | 41.2 | ok |
| linkage.json | R servo_theta_deg @delta=-21 vs brentq re-solve | -22.6318 | -22.63181692527336 | ok |
| linkage.json | R servo_theta_deg @delta=-10 vs brentq re-solve | -10.7771 | -10.777065897216689 | ok |
| linkage.json | R servo_theta_deg @delta=+0 vs brentq re-solve | 0.0 | 2.7520247313660318e-14 | ok |
| linkage.json | R servo_theta_deg @delta=+10 vs brentq re-solve | 10.7845 | 10.784543316414199 | ok |
| linkage.json | R servo_theta_deg @delta=+20 vs brentq re-solve | 21.6812 | 21.681188468177304 | ok |
| linkage.json | R gear @delta=+10 vs central difference (+-0.5 deg) | 0.92473 | 0.9247272054743847 | ok |
| linkage.json | R rod_len_mm @delta=+20 vs linkage_core.L_ROD | 31.0 | 30.99999999999997 | ok |
files loaded: 27; comparisons: 137; mismatches: 0

