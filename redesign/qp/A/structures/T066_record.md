# T-066 record: structures_a.py re-baselined to the current concept A geometry (R-PHY-09). 2026-11-22. Not VERIFIED COMPLETE. Nothing committed.

Category labels: s1 geometry arithmetic; s2 / s3 hand calculation; s4 FEA-lite (3-D Euler-Bernoulli beam frame, eigen + modal forced response; NOT shell / solid FEA); s5 rigid-body dynamics + hand calculation; s6 carried rows (not recomputed). EST = estimate, "—" = unknown.
No edit to docs/, CHANGE-LOG, TEST-PLAN-O4B.md, MASS-GATE.md or any top-level `redesign/qp/A/*.md`. Edited: `structures/structures_a.py`, `structures/structures_run.md` (regenerated), `structures/fe_a.py` and `structures/landing_a.py` (keyword / environment overrides only, defaults unchanged). New: `structures/T066_record.md`, `structures/T066_data/` (CAD part table, proof build output).

## Acceptance test (restated from the brief)
1. structures_a.py inputs updated to the committed CAD at ac983050 (D-226 / D-227 / D-228 / D-229), every number citing its source file.
2. Weak-mode rows carry coupling and a forced-response verdict.
3. `python -I structures_a.py` rerun, `structures_run.md` regenerated, diff against `iter3_run.md` recorded here.
4. Limits of the D-202 arm crossing and the hub stiffness listed; claims citing changed structures_run.md values re-pointed; `run_all.py` run once, failing-claim count vs T-083b's 8.
Never relaxed: any limit. Rows that fail are reported as FAIL with the RF / margin; no part redesigned.

## 1. Run
`python -I structures_a.py` (cwd = structures/): exit 0, 2 min 57 s, 291 lines written to `structures_run.md` (the last run; two earlier runs of the same file during development gave identical numbers). Landing sweep 126 runs (21 cases x 3 zeta x 2 mu).

## 2. Inputs and where each comes from
| Input | Value | Source |
|---|---|---|
| Spar | 12x10 at x 60 | `cad/amodel/common.py` SPAR_OD / SPAR_ID (via a_model) |
| Arms | 12x10, two continuous tubes (D-202) | `common.py` D-202 note (TUBE_DX, TUBE_OF); part CGE-002-A/B |
| Bridge | 16x14, x -63.0 .. 51.5 mm | `wing.py` BR_OD / BR_ID / BR_X0 / BR_X1 |
| Struts | **8x6** (not the ledger row's 6x4.5), end y 0.285 | `wing.py` STRUT_OD / STRUT_ID (T-077 p7, D-225), STRUT_E |
| Rib | **25x23** (not 14x12) | `wing.py` RIB_OD / RIB_ID (T-077 p8, D-226 s3) |
| Fin tube, fin y / height, fin x | 16x14, 0.38, 0.18, 0.294 | `common.py` FIN_OD, YFIN, FIN_H, XFIN_T |
| Hub x, motor station | -78.0 mm, y 0.228 / z 0.156 | `common.py` HUB, YM, ZM |
| Masses (FE lumps, structure table) | 131 declared part masses, basic 1,627.5 g | `a_model.PARTS` = `sitl/cad_mass.json` mass_basic_kg 1.6275 (match checked in the run) |
| Predicted mass | 1.873 kg | `mechanism/out/T083b_report.md` s0 row 6 (tallied) |
| CG for the landing | 21.08 mm | `sitl/cad_mass.json` cg_x_m |
| DAF, KF, KP | 2.23 wing / 1.97 tubes, 1.725, 2.156 | D-223, `T083_report.md` s5.3, `T083b_report.md` |
| Pad, stroke, zeta, mu, case list | 36 N, 24 mm, 0.02 / 0.05 / 0.10, 0.40 / 0.30, `landing_path_a.cases(False)` | `T083_report.md` s5.2, `T083_data/t083_demand.py` |
| Cap thrust | 13.08 N per motor | `T083_data/t083_cup_checks.md` (prop_a EST, 72 A, derate 0.93) |
| Rotor rpm | hover 6,777 / 7,036 / 8,015, full 10,343 / 11,358, max 11,415 | `prop_a.py` (hover, full; X2216 V3 880KV, T-083) at 1.873 kg |
| Cruise rpm 7,300-7,600 | **EST, carried** from QP-3 (MN2212, 1.5 kg), not re-derived | `iter3_run.md` |
| Foam allowables | 103 / 129 / 86 kPa | `foam_103.md` |
| Landing mass model | rebuilt from the current CAD (`T066_data/cad_part_table_T066.json`) | `landing_mass_cad.build_table` |

Noted discrepancies in the records: (a) the ledger row geometry is stale (rib 25x23, struts 8x6); (b) T-083 text says 23 landing cases, `landing_path_a.cases(False)` returns 21 (same function; my envelope reproduces T-083b s4.3: stroke 20.4 mm, tilt 2.80 deg, n 8.9 / 10.4 / 12.9 g at zeta 0.02 / 0.05 / 0.10); (c) FIN-002's part name still says 14x12 while its 26.0 g and `RIB_OD` are 25x23.

## 3. Results and rows that FAIL
| Row | Result | RF / margin | Verdict |
|---|---|---|---|
| Mass (s1) | CAD basic 1,627.5 g, predicted 1.873 kg vs MASS-GATE 1.50 kg | +373 g over | FAIL against the gate (as T-083b; gate not relaxed) |
| C1 / C2 spar (s2, s3) | spar 12x10 root 117 MPa vs 350 (MS +1.99); shear MS +8.6; tip 1.7 % of semispan | | PASS |
| Foam shear from bridge moment (s3, iteration-1 row) | 180 kPa vs 86 | MS -0.52 | **not a load path since D-226** (centre node slip-fit, bulkheads): shown, not counted; judged by T-083b C-rows. Reviewer should confirm this reading |
| Strong-coupled mode in the excluded band (s4) | spar mode kd 203 / nom 218 / hi 247 Hz, coupling cy **0.52** (iter3: 0.45, weak) inside the 94-321 Hz band | separation 10 / 4 / 2 % | **FAIL by the D-185 rule** (>= 0.5 in band). Single-mode forced response 0.11-0.16 m/s2 (0.4-0.5 % of 30); rule not relaxed; threshold ruling is for the design owner |
| Forced-response sweep 6,000-11,415 rpm (s4) | worst sum of axes 26.1 m/s2 (kd 0.5 %, at 11,400 rpm), per-axis 11.3 | MS +0.15 (bound) / +1.66 | PASS (bound); closes T-083's open "extend the sweep to 11,400 rpm" for the beam FE |
| Arm / bridge mount rows (s4) | arm 63 MPa MS +4.53, strike MS +0.82, bridge strike +6.21, crash +5.24, buckling +158 | | PASS |
| Static tip-over, drawn pads (s5) | 29.2 deg vs A-P9 30 | -0.8 deg | **FAIL** (pre-existing, T-083 29.48) |
| Landing, pad zeta 0.02 and 0.05 (s5) | stroke <= 20.4 of 24 mm, tilt <= 2.8 deg, n <= 10.4 g, rib-root RF x2.23 >= 1.11 | | PASS |
| Landing, pad zeta 0.10 (s5) | n **12.9 g > 12** (A-P5); stroke 14.9, tilt 2.0, rib-root RF x2.23 1.08 | | **FAIL** (A-P5), TP-3 test gap |
| Carried landing rows (s6) | all class-RF rows pass at zeta <= 0.05 (min 1.09); at zeta 0.10 nine groups fail (min 0.66) | | as T-083 / T-083b, not recomputed |

## 4. Diff against iter3_run.md (D-185 iteration 3: MN2212, 1.50 kg, structure frozen 473 g) and the pre-T066 structures_run.md
| Quantity | iter3_run.md / old structures_run.md | T-066 (current CAD) | Why |
|---|---|---|---|
| Mass basis | 1.50 kg gate, structure 473 g (494 g with D-187 lead) | CAD basic 1.6275 kg, predicted 1.873 kg | D-226 cell, X2216, hub, fittings |
| Rotor bands | hover 6,018 / 6,272 / 7,151 rpm; cruise 7,300-7,600 | hover 6,777 / 7,036 / 8,015; cruise carried; full 11,358 | X2216 on 1.873 kg |
| Excluded band (strong modes) | 84-304 Hz | 94-321 Hz | same rule, new rpm |
| Highest strong mode below band (kd / nom / hi) | 63 / 67 / 77 Hz (margins 32 / 24 / 9 %) | 69 / 72 / 84 Hz (37 / 32 / 12 %) | stiffer rib / bridge, heavier cage |
| Lowest strong mode above band | 432 / 462 / 524 Hz (42 / 52 / 73 %) | 442 / 478 / 538 Hz (38 / 49 / 68 %) | |
| Strong modes in band | none | spar mode 203 / 218 / 247 Hz, cy 0.52 | coupling 0.45 -> 0.52 |
| Sweep worst FC accel, sum of axes (kd 1 %) | 25.8 at 10,500 rpm (MS +0.16) | 25.9 at 11,400 (MS +0.16); worst 26.1 (kd 0.5 %), MS +0.15 | sweep extended to 11,415 rpm |
| per-axis / sqrt2 (VIBE-like) | 11.9 | 11.3 | |
| Worst up to the sag full-duty rpm | 22.7 up to 10,142 | 19.3 up to 10,343 | |
| Worst up to 9,349 rpm | 18.7 | 15.3 | |
| Cruise 7,300-7,600 | 9.5 | 7.4 | |
| Gust U 4 m/s at VD n / stall line | 3.01 / 3.96 | 2.72 / 3.17 | 1.873 kg lowers the stall line below the 3.4 floor |
| Spar 12x10 root bending, unrelieved | 4.78 N m, 94 MPa, MS +2.73 | 5.97 N m, 117 MPa, MS +1.99 | mass x 1.249 |
| Spar shear / tip deflection | 2.5 MPa / - | 3.1 MPa / 7.5 mm (1.7 %) | |
| Cage pitch moment | 2.44 N m (cap 8.8 N) | 3.77 N m (cap 13.08 N) | X2216 |
| Arm root bending | 14x12: 30 MPa (old file) | 12x10: 63 MPa | arm 12x10, thrust 13.08 N |
| Bridge strike | 8x6: 235 MPa MS +0.49 | 16x14: 49 MPa MS +6.21 | D-206 |
| Landing tip-over | 33.0 deg (legacy geometry) | 29.2 deg FAIL | CAD pads |
| Landing stroke / n | 15.4 of 20 mm / 10.8 g (30 N, 1.50 kg) | 17.9 of 24 mm / 10.4 g at zeta 0.05, 12.9 g at 0.10 (36 N, 1.873 kg) | |
| Control-band GM (iter3) | min 2.16 | **not re-run** | needs `sitl/fu_cage.py` with X2216 inertias; CL-A-VIB-GM-SHIFT still cites 2.16 |

## 5. Limits: D-202 arm crossing and hub stiffness (what this file does and does not capture)
D-202 arm crossing in the beam FE:
1. Four 12x10 beams meet at ONE rigid hub node at x -78.0 mm; the CAD has two continuous tubes offset +-6.5 mm in x (TUBE_DX) crossing with a 3 mm pin (CGE-010-C). The x offset, the crossing-pin shear transfer and tube-to-tube torsion through the hub block are not modelled; motor nodes sit at the common x, not at +-6.5 mm.
2. Arms are 12x10 beams with the doublers (14x12, 36 mm, +15 mm stagger), sleeves, pins and cups lumped as mass (hub_extra_g, motor_g); their stiffness is not added.
3. The prop strike is a damage case at factor 1.0 (D-202 decision, hub FEA `fea_hub.py`); this file only uses a 30 N EST strike on a bare tube and does not reproduce the hub FEA.
Hub stiffness:
4. The hub is rigid in the FE (machined 6061 CGE-001, 1.0 mm walls, 43.3 g, bonded sleeves 32 mm): hub, sleeve-bond, pin-clearance and bridge-bore compliance are absent. Arm-group modes (28-65 Hz) and the cage pitch / roll modes are therefore upper bounds in frequency; the kd / hi corners (E 61 / 90 GPa) bracket tube modulus only, not joint stiffness (joint stiffness "—"; the tap test T-A-TAP measures it).
5. The arm tip stiffness here (7.4 N/mm, 3EI/L^3, root fixed) is the rigid-hub value; T-083 reports 2.0 mm tip deflection at the cap and there is no repo limit on it ("—").
6. The D-226 torsion cell (3-ply skin, bulkheads, 6061 centre node, foam) is not in the FE: spar and rib tubes are joined by rigid nodes at the spar and the rib is rigidly tied to the spar at y +-0.38; the skin / bulkhead stiffness is none credited, so wing and fin / rib modes are not verified against the cell.
7. Lump rotary inertia is a placeholder (1e-5 x m); propeller gyroscopics are absent; the FC is hard-mounted (foam tape rigid, mount frequency not measured); damping 0.5 / 1 %, unbalance 1 g mm per rotor, 2P ripple 5 % of the static thrust are EST; cruise rpm band is the carried QP-3 EST.
8. Hub FEA of the 6061 hub (H-A1 / H-A2, D-224 condition) is in T-076c / T-077 records, not repeated.

## 6. Claims
- No file in `redesign/qp/A/proofs/` cites `structures_run.md` (grep of claims *.py / *.json and gen_params_a.py): nothing to re-point. `gen_params_a.py` line 211 cites `structures_a.py KF = 1.5 x 1.15` = 1.725: unchanged.
- Claims that read `iter3_run.md` (not structures_run.md, so NOT re-pointed; flagged for the owner because the new run changes their inputs): CALC-A-GUST-N-READ (n at VD 3.01 -> 2.72), CALC-A-VIB-LOW (63 / 67 / 77 -> 69 / 72 / 84 Hz), CALC-A-VIB-HIGH (432 / 462 / 524 -> 442 / 478 / 538 Hz), CALC-A-VIB-FC (25.8 / 27.1 -> 26.1 over a sweep to 11,415 rpm), CALC-A-VIB-GM and CL-A-VIB-GM-SHIFT (2.16, not re-run).
- `python -I redesign/qp/A/proofs/run_all.py` run once: **aborted with exit 1 at `claims_a3_program.py`** (`KeyError: 'Carbonwebshop'` in `bom_cost`, then 'USComposites'): HEAD (174529b8) has BOM-A.csv ship groups (Alcobra, RDQ, USComposites, Wicks, Carbonwebshop) that `gen_params_a.py` `ship_usd` does not list. Not caused by this task; I did not edit it (the ship rates there also differ from `bom_a.py` SHIP, so a fix is a BOM / proof-owner decision). The run rewrote `params-A.json` (one price) which I reverted with `git checkout`.
- To get the count anyway: `build_graph.py --strict` on the existing claim JSONs into `T066_data/proofs_out/` (`T066_data/build_graph_stdout.txt`): **8 failing claims, same 8 as T-083b** (CL-A-MASS-PRED 1.866 kg, CL-A-MASS-GATE-ROOM, CL-A-CUTS-REQUIRED 395.6 g, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY) + CL-A-FLUTTER-ELEVON-NOM UNVERIFIED, plus 1 extra build error (CALC-A-COST KeyError above). Delta vs T-083b: 0 failing claims, +1 build error from the BOM / params mismatch.

## 7. Proposed CHANGE-LOG text (not applied; ladder: no failure resolved, record re-baseline)
"T-066: structures_a.py re-baselined to the CAD at ac983050 (spar 12x10, arms 12x10 continuous, bridge 16x14, struts 8x6, rib 25x23, fin tube 16x14; 1.873 kg; X2216 cap 13.08 N; pad 36 N / 24 mm; DAF 2.23 / 1.97; masses from the CAD part table). Results (EST allowables): spar MS +1.99; strong modes clear of the 94-321 Hz band except a spar mode (cy 0.52) at 203-247 Hz that fails the D-185 0.5 rule (forced response 0.1 m/s2, sweep worst 26.1 m/s2 sum of axes, MS +0.15); landing PASS at pad zeta <= 0.05, n 12.9 g > 12 at 0.10; drawn-pad tip-over 29.2 deg < 30 (A-P9, pre-existing). No limit relaxed. D-202 crossing and hub stiffness limits: T066_record s5."

## 8. Open items for the lead
1. D-185 strong-coupling threshold (0.5) vs the spar mode at cy 0.52: rule ruling or accept as a recorded FAIL.
2. Confirm that the iteration-1 foam-shear-from-bridge-moment row is retired as "not a load path" (D-226).
3. `gen_params_a.py` ship_usd vs BOM-A.csv groups (blocks `run_all.py`).
4. Cruise rpm for the X2216 at 1.873 kg (carried EST) and the control-band GM clause need `sitl/` re-runs.

> 2026-11-22 note: this record is the snapshot at ac983050 (FIN_H 0.18, tip-over 29.2 deg FAIL, 1.873 kg). The committed `structures_a.py` / `structures_run.md` are the T-084 rerun (FIN_H 0.1937, tip-over 31.1 deg PASS, 1.8796 kg): see `redesign/qp/A/mechanism/out/T084_report.md` s4.
