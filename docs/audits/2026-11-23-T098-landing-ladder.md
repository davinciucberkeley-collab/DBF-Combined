# T-098: T-097 landing and pitch-use findings, 2026-11-23 (rev 2 after independent review round 10)

Status: analysis evidence, NOT VERIFIED COMPLETE (not self-marked). Nothing committed. `docs/task-ledger.md`, requirements, spec files, `redesign/site`, CAD and `tools/design_loop` not edited. Records: D-243 and D-244 (`redesign/params/CHANGE-LOG.md`), trade tables (`docs/engineering-decisions.md`), AR-016 (`docs/analysis-records.md`), TP-3 criterion (`redesign/qp/A/TEST-PLAN-O4B.md` s2.3), results `redesign/qp/A/mechanism/out/T098_results.json` (145 rows, T097 schema plus a `decision` sentence).
Rev 2 changes (review `docs/audits/2026-11-23-review-round-10.md`): 98-1 the plateau band is replaced by a joint (plateau, zeta) region from a finer zeta grid; 98-2 the upper edge is capped by the D-226 cell path; 98-3 the contradicting 37 N peak-force line is removed from TP-3; 98-4 the 20 deg pitch-use basis is withdrawn; 98-5 / 98-6 stated as limits / worst-case values.

## 0. Acceptance test restated from the brief
1. No limit or load factor relaxed (stroke <= 20 mm, n <= 12 g, tilt <= 3 deg, rib-root RF >= 1.0).
2. Landing ladder with numbers in order: (1) subtract, (2) modify (plateau sweep, band width), (3) rearrange, (4) material only if 1-2 fail; prefer no CAD change.
3. Pitch-use line (AR-010 open item 5) checked against the hardware; verdict and margin.
4. D-243 / D-244, trade tables with a Benchmark (6.4) line, `landing_a` rerun at the chosen spec for every AR-014 case, AR-016, TP-3 pass criterion, this audit.
5. Rev 2: TP-3 must not accept any (Fp, zeta) point the model fails.

Result: **landing passes with no CAD change, but only inside a joint foam region (Fp 37.5-39.0 N AND zeta 0.02-0.05 AND usable stroke >= 20 mm); the elevon pitch-use line stays FAIL on its 15 deg basis (open item).**

## 1. Findings
1. **Stale rib in T-097.** `landing_a.py` defaults to a 14x12 rib tube (`LAND_RIB_OD/ID`); the drawn rib is 25x23 since D-226. T-097 did not set the override, so its rib RF values (0.42, 0.76-0.95) are on the stale tube. The 14x12 run reproduces T-097 exactly at 30 N (20.3 mm, 17.45 g, RF 0.42). Both bases are reported.
2. The T-083 pad (36 N / 24 mm usable, 36 mm free foam) is a CAD pad change gated by TP-3; not needed.

## 2. Landing ladder (rigid-body dynamics; `landing_a.py` unchanged; 1.881 kg, CAD CG, T097 part table, mu 0.40)
Worst over the 10 AR-014 cases, stroke 20 mm, zeta 0.05, CAD rib 25x23 (`plateau_rib25.json`):
| Plateau N | stroke mm | n g | tilt deg | rib RF | verdict |
|---|---|---|---|---|---|
| 30.0 | 20.3 | 17.45 | 2.80 | 1.46 | FAIL (stroke, n) |
| 31.5 | 20.1 | 9.26 | 2.75 | 2.44 | FAIL (stroke) |
| 33.0 | 19.4 | 9.64 | 2.66 | 3.19 | pass |
| 34.5 | 18.6 | 10.01 | 2.53 | 3.62 | pass |
| 36.0 | 18.1 | 10.39 | 2.40 | 3.49 | pass |
| 37.5 | 17.2 | 10.76 | 2.27 | 3.36 | pass |
| 39.0 | 16.7 | 11.13 | 2.15 | 3.25 | pass |
| 40.5 | 16.0 | 11.50 | 2.05 | 3.15 | pass |
| 42.0 | 15.5 | 11.87 | 1.95 | 2.99 | pass |
| 43.5 | 15.0 | 12.24 | 1.88 | 2.84 | FAIL (n) |
| 45.0 | 14.5 | 12.60 | 1.85 | 2.65 | FAIL (n) |

**Rung 1 (subtract: card limit), tried, not adopted.** 30 N, rib 25x23 (`card_rib25.json`): stroke 17.9 / 18.8 / 19.5 / 20.1 / 20.2 / 20.3 mm at forward drift 0 / 0.1 / 0.2 / 0.3 / 0.4 / 0.5 m/s (10 deg lean, sink 1.2); stroke 14.4 / 16.2 / 16.1 / 18.0 / 19.9 / 20.3 mm at lean 0 / 2 / 4 / 6 / 8 / 10 deg (drift 0.5); sink up to 1.1 m/s passes (18.4 mm). The case passes only for drift <= 0.2 m/s or lean <= 8 deg, but the 29 SITL touchdown records reach 0.50 m/s lateral at 11-12 deg lean (AR-012), so a card limit would exclude cases the aircraft sees, and the 1.2 m/s sink is the A-P5 design case, not a controlled rate.

**Rung 2 (modify: foam spec), adopted, as a region.** The plateau alone is not enough: the pass set moves with pad damping (`zeta_rib25.json`, `zeta2_rib25.json`; worst of 10 cases; P = pass, F = fail):
| zeta \ Fp N | 33 | 35 | 37.5 | 40 | 42 |
|---|---|---|---|---|---|
| 0.01 | F 20.60 mm | F 20.45 mm | F 20.20 mm | P 19.21 mm | P 18.29 mm |
| 0.02 | F 20.47 mm, 26.8 g | F 20.28 mm | P 19.56 mm, 9.20 g | P 18.34 mm | P 17.48 mm |
| 0.03 | F 20.31 mm | F 20.26 mm | P 18.69 mm | P 17.55 mm | P 16.75 mm |
| 0.05 | P 19.4 mm | P (34.5 N: 18.6 mm) | P 17.2 mm | P (40.5 N: 16.0 mm) | P 15.5 mm |
| 0.07 | P 17.88 mm | P 16.95 mm | P 15.93 mm, 11.77 g | F 12.41 g | F 12.92 g |
| 0.10 | P 16.1 mm, 11.98 g | not run | F 13.23 g | not run | F 14.46 g |

**Rung 2b, upper edge vs the D-226 cell / saddle path (review 98-2).** T-083b sized the whole cell (rib, bridge, strut, R4 clamp, root fitting) at Fp 36 N: min RF 1.09 (R4 junction, zeta 0.05, x2.23); at zeta 0.10 min 0.66. The strength pipeline (`landing_path_a.py` / T-083 demand, 23 cases, DAF) was NOT rerun: it is a long job and the machine is loaded by the film render. Hand scaling (EST): RF x 36 / Fp, conservative because peak foot force grows only about 1.3 N per N of plateau (Fmax 46 N at 30 N to 55.9 N at 37.5 N, hard 7/7 combo): RF >= 1.0 up to 39.2 N. Upper edge set to **39.0 N** (RF 1.006 by scaling). Any measured pair above 39 N needs the T-083 strength rows rerun.

**Accepted region (TP-3, D-243): Fp 37.5-39.0 N per foot (0.208-0.217 MPa on the 12x15 mm face, 180 mm2) AND zeta 0.02-0.05 AND usable stroke >= 20 mm on the drawn 30 mm pad.** The lower plateau edge 37.5 N comes from zeta 0.02 (35 N fails, 37.5 passes; 0.44 mm stroke margin at the corner 37.5 N / 0.02); zeta 0.01 would need >= 40 N (above the cell cap), so zeta < 0.02 is outside; zeta above 0.05 is outside because the cell fails at 0.10 and the 0.07 column was not run on the cell. Interior points are bracketed by tested corners (stroke falls monotonically with Fp and with zeta in the grid). **The region is 1.5 N wide (about +-2 % of Fp): narrower than any plausible foam scatter, so the foam must be selected or conditioned to it by test; a pair outside it is not accepted without rerunning `landing_a.py` (and the strength rows above 39 N).** The coupon scatter of A's foam is "—". Stroke / pad-thickness options from the same stock: the pad is 30 mm long with 20 mm usable (AR-008 convention); 24 mm usable needs a 36 mm pad (T-083, CAD change): see the fallback below.

Record run, `landing_a.py 37.5` (zeta 0.05), all 10 cases, rib 25x23 (`landing_cad_1881_p37p5_rib25.txt`):
| Case | stroke mm | n g | side N | tilt deg | rib RF |
|---|---|---|---|---|---|
| hard level | 8.4 | 10.76 | 15.4 | 0.0 | 7.62 |
| hard 10 narrow | 14.6 | 5.42 | 16.9 | 1.8 | 12.55 |
| hard 10 narrow neg | 14.2 | 5.43 | 17.2 | 1.7 | 10.57 |
| hard 10 wide | 9.0 | 5.62 | 21.2 | 0.1 | 3.48 |
| hard 7/7 combo | 12.4 | 6.91 | 22.4 | 1.2 | 3.36 |
| hard 10 narrow + drift .5 | 17.2 | 7.05 | 20.1 | 2.3 | 5.38 |
| hard 10 wide + drift .5 y | 11.7 | 5.94 | 22.3 | 0.4 | 4.84 |
| normal level .5 | 2.3 | 8.90 | 14.6 | 0.0 | 5.60 |
| normal 10 narrow .5 | 3.4 | 7.87 | 15.8 | 0.1 | 6.81 |
| normal 10 wide .5 + drift | 6.8 | 5.29 | 19.8 | 0.4 | 4.39 |
Peak foot force Fmax in this run 41.2-55.9 N (so the old TP-3 line "peak foot force <= 37 N" could not be met by any passing foam and is removed, review 98-3). Static tip-over unchanged: 31.08 deg.

Other validity limits: 14x12 (stale, not the drawn part): worst RF 0.91 / 1.03 / 0.96 / 0.85 at 33 / 34.5 / 37.5 / 42 N, no robust band (if the D-226 rib-twist coupon restores 14x12 the region must be re-run). Six AR-012 SITL-record touchdown cases at 30 / 36 / 40.5 N: worst stroke 9.8 / 8.4 / 7.6 mm, n <= 7.86 g excluding Z5_b0; Z5_b0 (29 deg lean, belly-on 5 m/s, card-prohibited) tips over at every plateau (AR-012 item). Coverage: 10 AR-014 cases at mu 0.40; T-083 used 23 cases and mu 0.30 (98-5, not shown here). `landing_a.py` checks only the AR-012 rib-root combination.

**TP-3 fallback (rev 3): 24 mm usable stroke, 36 mm pad (CAD change, not made).** (usable stroke 24 mm on the 36 mm pad of T-083, rib 25x23, 10 AR-014 cases, mu 0.40; `stroke24_rib25.json`, `zeta24_rib25.json`, `zeta24b_rib25.json`): zeta 0.05: Fp 30-42 N pass (30 N: 21.2 mm, tilt 2.93; 43.5 and 45 N fail n, 12.24 / 12.60 g); zeta 0.02: 34.5-45 N pass (34.5 N: 21.26 mm, tilt 2.81; 36 N: 20.37 mm, 2.66; 37.5 N: 19.56 mm; 39 N: 18.8 mm; 45 N: 16.3 mm) and 33 N FAILS (tilt 3.01 deg, stroke 22.7 mm); zeta 0.10: 33 N passes (11.98 g), 39 and 45 N fail n (13.64, 15.26 g). With the cell cap of 39 N (hand scaling of T-083b, unchanged) the fallback region is **Fp 34.5-39.0 N AND zeta 0.02-0.05 AND usable stroke >= 24 mm**: 4.5 N wide (about +-6 % of Fp), three times the 1.5 N main region; binding limit is tilt (2.81 deg at 34.5 N / zeta 0.02) not stroke (21.3 of 24 mm). Cost: a CAD change (pad 30 -> 36 mm, cup / shoe lengthened, not made here) and an A-P9 re-check. A-P9 recomputed from the CAD constants at the current CG (x 22.05 mm, z 6.56 mm; `landing_a.cad_geom`): 30 mm pad (x_foot 0.3375) edge toward CG 31.08 deg; **36 mm pad (x_foot 0.3435, pad start fixed) edge toward CG 30.60 deg (0.10 deg over the 30.5 target, thin), pad-centre bound 29.81 deg (under 30)**; 40 mm analysis pad (x_foot 0.3475) 30.30 deg, which sits inside the T-084 record range 30.22-30.52, so the T-084 30.22 figure is confirmed but belongs to the 40 mm pad, not to the 36 mm pad (a 36 mm pad gains about 0.3 deg over it). Strength rows (shoe, fin tube, root fitting, cell) were not rerun on the longer pad geometry (T-083b sized the cell at 36 N / 24 mm / x_foot 0.3475).

Rungs 3 (foot position), 4 and 5 (material) not needed while the foam can be conditioned into the region; if TP-3 shows it cannot, rung 3 / 5 (e.g. 24 mm pad, A-P9 re-check) are the next steps.

## 3. Elevon pitch-use line (flight dynamics; a reading of AR-015; no new SITL run) - rev 2: basis change WITHDRAWN
- Standing line: elevon pitch use <= 0.60 of 15 deg (`redesign/review/QP-3/SITL-FLIGHT.md` l.25: K09-L 25 deg travel less 10 deg kept; <= 9 deg mean pitch deflection). AR-015: 0.69 (Z5_gb0), 0.77-0.79 (T-074 cases): **FAIL, open item (AR-010 item 5 stays open).**
- The first version of this audit and D-244 re-based the line to the 20 deg commanded endpoint (0.52-0.59, "pass"). The review (98-4) found that this raises the pitch allowance from 9 deg to 12 deg without deriving A's roll / yaw / gust reserve (a relaxation), and that the "fraction-preserving" arithmetic was wrong (0.60 x 12 = 7.2 deg). Withdrawn.
- Information only: 20 deg basis 0.52 (Z5) / 0.58-0.59 (T-074); 25 deg basis 0.41-0.47. Hardware: plant EL_MAX 20 deg (`a_aero.py`), commanded endpoints +-20 deg (AR-006), stops +-21 deg (AR-001 rev 3), SERVO5/6 MIN / MAX in `A.param` still K09-L pulses (1003-1976 / 1024-1997 us), to be bench-set; servo throw "—". Peak individual surface: T-074 12.0 deg, Z5 10.6 deg (98-6).
- What closes it (open, owner / controls): derive A's roll and gust authority demand as deflection and a reserve rule from it, or reduce the pitch demand through the ladder (e.g. the transition entry schedule) and re-run SITL. Not done here.
- Benchmark (6.4): none found for an elevon pitch-use line (project-internal criterion).

## 4. Benchmark (6.4)
Landing foam: Dynamic Crushing Behavior of EVA Copolymer Foam Based on Energy Method, MDPI Polymers 2023, https://pmc.ncbi.nlm.nih.gov/articles/PMC10385341, checked 2026-11-23 (elastic / plateau / densification stages; plateau stress rises with loading rate). No published drone or tailsitter foam-pad comparable found.

## 5. Commands, exit codes, wall times
Windows 11, 20 logical CPUs, Python 3.14.2, numpy; the machine was loaded by a concurrent film render (T-097 ran the same table in 78-85 s). Common env: `LAND_MASS_KG=1.881 LAND_MASS_MODEL=cad LAND_PART_TABLE=redesign/qp/A/mechanism/out/T097_data/cad_part_table_t097.json`; rib 25 adds `LAND_RIB_OD=0.025 LAND_RIB_ID=0.023`. cwd `redesign/qp/A/mechanism/out/T098_data/`.
| # | Command | Exit | Wall |
|---|---|---|---|
| 1 | first launch with LAND_PART_TABLE unset (workers raced to rebuild the table, JSONDecodeError; my launch bug) | 1 | n/a |
| 2 | `python -I sweep_t098.py plateau 14 plateau_rib14.json 8` (110 runs) | 0 | 373 s |
| 3 | `python -I sweep_t098.py plateau 25 plateau_rib25.json 8` (110 runs) | 0 | 376 s |
| 4 | `T98_FP=33,37.5,42 python -I sweep_t098.py zeta 25 zeta_rib25.json 6` (zeta 0.02, 0.10; 60 runs) | 0 | 341 s |
| 5 | `python -I sweep_t098.py card 25 card_rib25.json 6` (97 runs) | 0 | 452 s |
| 6 | `python -I landing_a.py 37.5` (structures/, rib 25 env) | 0 | 306 s |
| 7 | rev 2: `T98_FP=33,35,37.5,40,42 T98_Z=0.01,0.02,0.03,0.07 python -I sweep_t098.py zeta 25 zeta2_rib25.json 10` (200 runs) | 0 | 319 s |
| 8a | rev 3: `python -I sweep_t098.py stroke 25 stroke24_rib25.json 10` (24 mm, Fp 30-45 N, zeta 0.05; 110 runs) | 0 | 127 s |
| 8b | rev 3: `T98_FP=33,39,45 T98_Z=0.02,0.10 T98_S=24 python -I sweep_t098.py zeta 25 zeta24_rib25.json 8` (60 runs) | 0 | 107 s |
| 8c | rev 3: `T98_FP=34.5,36,37.5 T98_Z=0.02 T98_S=24 python -I sweep_t098.py zeta 25 zeta24b_rib25.json 10` (30 runs) | 0 | 31 s |
| 8d | rev 3: A-P9 recompute with `landing_a.cad_geom` (x_foot 0.3375 / 0.3435 / 0.3475) | 0 | seconds |
| 9 | `python -I t098_collect.py` -> `T098_results.json` (145 rows) | 0 | seconds |

## 6. Limits and open items
Foam plateau, stroke, zeta and pad mu are unmeasured (TP-3, after Order 1); the region is a model result at EST allowables, 1.5 N wide; its upper edge is a hand scaling of the T-083b strength rows, not a rerun (open: rerun `landing_path_a.py` / the T-083 demand at the measured pair, 23 cases, mu 0.30 and 0.40); the region assumes the 25x23 rib is built; one rigid-body family; pitch-use FAIL on its standing basis is open and needs a derivation or a pitch-demand fix.
