# T-101 U2: elevon flutter and fin-node bond at chord fraction 0.30 (hard row: moving control surface)

Category: flight dynamics (aeroelastic 3-DOF section, wing bending-torsion) and hand calculation (EST). Chord decision D-number pending (conductor).

## Outcome

- Task A: PASS after ladder rung (b) add: lead 10.0 -> 14.0 g per elevon at the unchanged 20 mm reach. With the CAD inputs unchanged (lead 10.0 g) case E (damper 0.3 C0) FAILED at corners kd and nom.
- Task B: **FAIL / STOP** under the brief's stop rule: rows N4a (rib strap laps) and R1 (rib at the node exit) go below RF 1.0 in the stated scaling range (N4a at pad zeta 0.05; R1 all-zeta bound). Nothing redesigned; the fin node is not touched.

## 1. Task A inputs, old vs new

| Input | Old (T077p8) | New | Source |
|---|---|---|---|
| cf (elevon chord fraction) | 0.25 | 0.30 | common.py ELEV_FRAC (U1) |
| hinge x | 183.75 mm | 171.50 mm | U1_cad.md s2 |
| elevon mass me (WNG-006) | 6.7 g | 7.6 g | wing.py:930 / U1_cad.md s2 |
| lead / reach | 10.0 g / 20 mm | 10.0 g / 20 mm first; final **14.0 g / 20 mm** (ladder b) | wing.py BAL_REACH, BAL_T |
| tabs | 0.5 g | 0.5 g | WNG-007 |
| damper C0 | 1.0297e-3 N m s/rad | same; confirmed: every DMP_* constant and the DMP_C formula unchanged in `git diff HEAD` of wing.py; STOP_CHECK.md prints c = 1.03e-03 | wing.py:564-574 |
| cases / grid / corners / limit | A-E, K 0.01-20 N m/rad 600 pts, kd/nom/hi, no instability <= 28.8 m/s | same | script logic unchanged |

Hard-coded check: `flutter_a.py` takes the hinge from `EL_CF` / `C_H`, which `fixes2_run.setup(me, cf)` sets from cf (C_H = ((1-cf)*CH - 0.5*CH)/B), so the section model follows cf. `fixes2_run.wing_modes` hard-codes the lump x at 0.18375 - arm; the copy (`t101_flutter.py`) has its own `wing_modes` / `run_case` taking x = (1-cf)*CH - arm (original untouched). `flutter_a.wing_flutter` itself does not depend on the hinge position other than through the lump x and C_H.

Hinge-inertia cross-check (`flutter_t101.md`, lead 14.0 g): section model 1.949e-05 vs CAD cad_mass.json 1.961e-05 kg m2 (elevon 1.369e-05 + balance 5.919e-06). At lead 10.0 g: 1.789e-05 vs CAD 1.793e-05 (`flutter_t101_new10.md`). Elevon CG aft of the hinge, unbalanced 25.73 mm (CAD); balanced -4.07 mm at 14.0 g (-0.55 mm at 10.0 g).

## 2. Section model results (damper cases; lowest unstable speed on the K grid, m/s, EST; PASS = no instability <= 28.8 m/s at any K)

Baseline reproduction: `flutter_t101_old.md` (old inputs through the copy) gives the T077p8 numbers exactly (E: 29.5 / 31.5 / 34.5 at kd / nom / hi).

| case | corner | old (cf 0.25, 6.7 g, lead 10.0) | new, lead 10.0 g (`flutter_t101_new10.md`) | **new, lead 14.0 g (`flutter_t101.md`)** |
|---|---|---|---|---|
| A no damper (reported, not gated) | kd / nom / hi | FAIL / FAIL / FAIL | FAIL / FAIL / FAIL | FAIL / FAIL / FAIL |
| B hot 0.6 C0 | kd / nom / hi | 35.5 / 38.0 / 41.5 PASS | 33.0 / 35.5 / 38.5 PASS | 36.0 / 38.0 / 42.0 PASS |
| C nominal | kd / nom / hi | 39.5 / 42.0 / 47.0 PASS | 38.0 / 40.5 / 45.0 PASS | 40.0 / 43.5 / 48.0 PASS |
| D cold 2 C0 | kd / nom / hi | 43.0 / 46.5 / 52.0 PASS | 42.0 / 45.5 / 51.0 PASS | 44.0 / 47.5 / 53.5 PASS |
| E half-hot 0.3 C0 | kd / nom / hi | 29.5 / 31.5 / 34.5 PASS | **26.5 FAIL / 28.0 FAIL / 30.5 PASS** | 29.0 / 30.5 / 33.5 PASS |

Wing model (`flutter_wing_t101.md`): lump per semispan = lead 14.0 + tabs 0.5 + caps 3.69 + 3.72 (CAD WNG-008-RU / RL part masses, interfaces.json) + 2.5 (half of 5.0 g dampers; CAD WNG-009 2.0 + WNG-010 0.47 = 2.47 g) = 24.41 g at x 0.1515 m, y 0.285. Flutter speed m/s (limit 28.8), all PASS:

| model | corner kd / nom / hi | old baseline (cf 0.25, lump 20.47 g at x 0.1638; `_old`) | new lead 10.0 (`_new10`) | **new lead 14.0** |
|---|---|---|---|---|
| fins on | kd / nom / hi | 46.2 / 49.6 / 56.3 | 46.1 / 49.3 / 56.2 | 46.0 / 49.3 / 56.2 |
| fins off | kd / nom / hi | 34.1 / 40.7 / 47.5 | 36.1 / 43.2 / 50.4 | 35.5 / 42.3 / 49.4 |

Sensitivity: with the caps from the post-ladder STOP_CHECK.md (3.10 + 3.15 g, printed volume; `flutter_wing_t101_newstop.md`) the fins-off kd speed is 35.7 and all rows PASS. The old baseline used HEAD STOP_CHECK caps 3.72 + 3.75 as the brief directed; the new run uses the CAD part masses (3.69 + 3.72), which differ from STOP_CHECK's printed-volume figures.

## 3. Ladder

- (a) modify, BAL_REACH 22.5 / 25 / 27.5 / 30 mm at lead 10.0 g (`t101_ladder_sweep.py`): case E kd FAIL (73 / 60 / 52 / 48 failing K points, onset 26.5), nom FAIL (25 / 20 / 18 / 20), hi PASS. **Rung (a) failed**: reach lowers the failing band but does not clear kd or nom inside the 30 mm cap.
- (b) add, lead mass in 0.5 g steps at reach 20 mm (`t101_ladder_sweep2.py`): kd needs 14.0 g (13.5 g leaves 12 failing K points); nom passes from 11.0 g. At reach 30 mm, 14.0 g still fails kd (18 points); at 25 mm, 14.0 g fails kd (6 points). **Chosen: 14.0 g at reach 20 mm (+4.0 g per elevon, +8.0 g aircraft).** Reach stays at 20 mm because moving it did not help kd at any step.
- Strip: 10 mm x 1.17 mm x 106 mm (BAL_T = 0.0013 x 14.0 / 15.6), 14.0 g at 11.34 g/cm3.

## 4. wing.py change

`redesign/qp/A/cad/amodel/wing.py` only: BAL_T 0.0013 x 10.0/15.6 -> 0.0013 x 14.0/15.6 (comment added, D-number pending); WNG-007 part text "14.0 g lead strip ... T-101 U2 ... was 10.0 g" and mass 10.5 -> 14.5 g. BAL_REACH unchanged (0.020).

- `python -I redesign/qp/A/cad/build_a.py` (19 s): exit 1, `check: FAIL (10 modules, 1 errors, 0 warnings)`; the only error is `graph:mass TOTAL aircraft 1640 g > limit 1500 g` (pre-existing mass-gate error). `U2_build_a.txt`.
- `python -I redesign/qp/A/cad/stop_check.py`: exit 0; cap clearance upper 0.51 / lower 0.52 mm (>= 0.5), boss-to-lead 1.40 / 1.34 mm: PASS. Lead poke at the stop 1.86 / 1.75 mm (was 1.69 / 1.59 at 10.0 g). `U2_stop_check.txt`.
- `python -I redesign/qp/A/sitl/cad_mass.py`: exit 0. `U2_cad_mass.txt`. cad_mass.json: mass_basic 1.64048 kg (1.63248 after U1; +8.00 g), CG x 21.413 mm (20.777 after U1; +0.636 mm), y -3.328 mm, z 6.603 mm; elevon hinge inertia total 1.9605e-05 kg m2, balance one 5.919e-06, cg_aft_of_hinge_balanced -4.07 mm, balance_mass_each_g 14.5.
- The strip y range 232-338 mm is unchanged (servo pocket edge |y| 222.5 mm not approached); only the thickness grew 0.83 -> 1.17 mm.
- Not run (per brief): collide_a.py, a_assembly.py, GLB export. The thicker strip needs the collision gate.
- **Stale text left (outside the allowed edit list):** `redesign/qp/A/cad/a_build_steps.py` lines 393, 395, 405, 406, 408 ("10.0 g lead strip", "10 x 0.83 x 106 mm = 10.0 g", "within 0.3 g") and the generated BUILD-GUIDE-A.md; U1_cad.md s7 mass/CG totals; T-077 p8 records carry 10.0 g.

## 5. Task B: fin-node bond and plate rows, hand scaling (EST)

Geometry change (live wing.py via `t101_nodegeom.py`): bond L = FNB_X1 - RIB_X0 105.5 -> 93.25 mm (ratio 1.131; squared 1.280); plate x 58..168 -> 58..163.75 mm (110 -> 105.75 mm; A 1962 -> 1899 mm2, J 2.870e6 -> 2.604e6 mm4, rmax 58.36 -> 56.37 mm; the old values reproduce the T-083 records 1962 / 2.87e6); cell area to the bulkhead end A_FIN 3259 mm2 (record, to x 176) -> 3126 mm2 (live inner loop clipped at 163.75; ratio 0.959); the pad is at x 347.5 mm (demand_t083.json xf), so the load arm from the node exit grows 171.5 -> 183.75 mm (x 1.0714) for moments taken about x = FNB_X1 (t083_path.py:177).

Scaling laws (formulas from t083_path.py):
- N3: w_z = 0.5 (6 My / L^2 + Fz / L) + Mx / (D L): bending term 1/L^2 (and My x 1.0714 from the arm), shear and torque terms 1/L. Factor range **1.131 (all 1/L, My unchanged) to 1.371 (1.280 x 1.0714)**; RF_new = RF_old / factor.
- N4a, N4b, N6: w_y = 6 Mz / L^2 + Fy / L: same range 1.131-1.371.
- N1, N2, K1: q or T / 2 A_FIN: RF proportional to A_FIN, x 0.959.
- N5: stress = Mz rmax / 2J + F / 2A: factor rmax/J 1.065 x arm to the plate centroid 234.5 -> 236.6 (1.009) = 1.075; RF / 1.075.
- R1 (rib tube at the node exit): bending arm x 1.0714; Fx and Mx unchanged; so RF_new >= RF_old / 1.0714.
- No dependence on FNB_X1 / FNP_X: R2 (x 255), root-block P5-P8, centre-node and bridge rows.
- CL-A-MS-BOND (claims_a2_struct.py:81, rib saddle on the spar) and ms_rib_torsion (claims_a2_struct.py:92): static values 0.34 and 0.60 (gen_params_a.py:216, 226), not computed from FNB_X1 / FNP_X; no scaling, unchanged (reported only).

RF columns: T-083 `strength_table_t083.md` (x2.23, 25x23 rib) at pad zeta 0.02 / 0.05 / all-zeta (= zeta 0.10). The T-083 baseline already fails at zeta 0.10 for N3, N4a and K1 (pre-existing; TP-3 accepts only pad zeta <= 0.05).

| Row | old RF z0.02 / z0.05 / all | factor | new RF z0.02 / z0.05 / all | verdict |
|---|---|---|---|---|
| N3 rib-to-bulkhead flox fillet (L 105.5 -> 93.25) | 1.58 / 1.41 / 0.83 | 1.131-1.371 | 1.15-1.40 / 1.03-1.25 / 0.61-0.73 | z <= 0.05 PASS (z0.05 lower bound 1.03); all-zeta FAIL (pre-existing 0.83, lower now) |
| **N4a rib strap laps (Mz, Fy)** | 1.24 / 1.11 / 0.94 | 1.131-1.371 | **0.90-1.10 / 0.81-0.98 / 0.69-0.83** | **FAIL at z0.05 (whole range < 1.0); z0.02 FAIL at the lower end; all-zeta FAIL (pre-existing)** |
| N4b rib strap tension | 4.96 / 4.42 / 3.75 | 1.131-1.371 | 3.62-4.39 / 3.22-3.91 / 2.74-3.32 | PASS |
| N6 skin + plate shear at the strap lap line | 7.19 / 6.40 / 5.44 | 1.131-1.371 | 5.24-6.36 / 4.67-5.66 / 3.97-4.81 | PASS |
| N1 bulkhead-to-skin lap | 3.71 / 3.28 / 2.14 | 1/0.959 | 3.56 / 3.15 / 2.05 | PASS |
| N2 bulkhead in-plane shear | 8.12 / 7.17 / 4.68 | 1/0.959 | 7.79 / 6.88 / 4.49 | PASS |
| N5 in-plane plates on skin (plate 110 -> 105.75) | 2.84 / 2.53 / 2.11 | 1.075 | 2.64 / 2.35 / 1.96 | PASS |
| K1 skin shear at the fin node | 1.32 / 1.16 / 0.76 | 1/0.959 | 1.27 / 1.11 / 0.73 | z <= 0.05 PASS; all-zeta FAIL (pre-existing) |
| **R1 rib tube at the node exit (x 176 -> 163.75)** | 1.14 / 1.16 / 1.06 | <= 1.0714 | >= 1.06 / >= 1.08 / **>= 0.99** | z <= 0.05 PASS; all-zeta bound < 1.0: **possible FAIL, needs the demand re-run** |

Records stale until re-run (U1 s8): strength_adopted.txt R1 and demand records "at x 176" (Mx 5.14, My 10.01, Mz 10.00 N m); D-226 saddle-loadpath audit line 98 (L 99.5 / 113 mm); TEST-PLAN-O4B TP-13 bond coupon (2.21 MPa at L 99.5 mm): the new L 93.25 mm is shorter than the tested lengths.

Consequence (stop rule): N4a < 1.0 at pad zeta 0.05 (the TP-3 acceptance zeta) and R1 may be < 1.0 over all zeta. Not redesigned. The conductor decides (exact re-run of t083_path.py on the new geometry, longer strap lap, etc.; out of this unit's scope).

## 6. Files and commands

New files in `redesign/qp/A/mechanism/out/T101_data/chord/`: `t101_flutter.py` (modes new / new10 / old; `python t101_flutter.py new`, plain python for multiprocessing spawn; 20-28 s each), `t101_flutter_wing.py` (`python -I t101_flutter_wing.py new|newstop|new10|old`), `t101_ladder_sweep.py`, `t101_ladder_sweep2.py` (plain python), `t101_nodegeom.py` (`python -I`), `flutter_t101.md`, `flutter_t101_new10.md`, `flutter_t101_old.md`, `flutter_wing_t101.md`, `flutter_wing_t101_new10.md`, `flutter_wing_t101_newstop.md`, `flutter_wing_t101_old.md`, `U2_build_a.txt`, `U2_stop_check.txt`, `U2_cad_mass.txt`, `t101_new.log`, `t101_old.log`, this file. Edited: `redesign/qp/A/cad/amodel/wing.py` (BAL_T, WNG-007 text and mass). Regenerated by the scripts: cad/out/STOP_CHECK.md, sitl/cad_mass.json, cad/out/_job.json, cad/model/*/interfaces.json.

Note: `python -I tools/ledger_audit.py` returned exit 2 when run after these changes; not investigated (ledger not mine, no rows touched).
