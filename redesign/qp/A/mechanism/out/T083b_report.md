# T-083b (T-083 continuation): fin root block FIN-003 redrawn as a machined 6061 root fitting. 2026-11-21. Not VERIFIED COMPLETE. Nothing committed.

No edit to docs/, CHANGE-LOG, task ledger, TEST-PLAN, MASS-GATE or BOM-A.csv (proposed text in s9). Labels: EST = estimate; "—" = unknown; V = vendor page read today (URL, 2026-11-21).
Categories: rigid-body dynamics (the T-083 landing demand, not re-run; one sensitivity re-run at the new mass / CG, s4.3), hand calculation (every strength row, `t083b_rootblock.py`; torsion of the junction planes by a finite-difference Prandtl stress function, checked against closed forms), geometry arithmetic (voxel mass, CG, box, wire lengths), illustrative (prop_a EST thrust model for window / T-W / cruise / A-P6), interference (collide, linkage poses, assembly). No FEA, CFD or SITL.
Data and scripts: `T083b_data/` (index s10). No large array written to the repo: the sensitivity demand npz (87 MB) is in the session scratchpad only.

## Acceptance test (restated from the brief)
1. Find why FIN-003 fails (P6 0.25-0.44, P8 0.31-0.60) and redesign it with the least mass, material / process from `docs/reference/jacobs-equipment.md` with sourced allowables, load into the D-226 bulkhead / torsion cell; **every row of the part RF >= 1.0 at x2.23 on the T-083 demand at pad zeta <= 0.05**; report zeta 0.10.
2. Draw it in `cad/amodel/`; printed_mass.json, build steps, drawing; recompute mass / CG / SM / window / T-W / A-P6; any material priced (URL, date) in a BOM copy with the total incl. crash reserve <= $2,000.
3. Gates once at the end into `T083b_data/gates/`; drawings and build guide regenerated.
4. This report. Never relaxed: KF 1.725, KP 2.156, RF >= 1.0 at max(DAF, 1.5) = 2.23, window >= +5 %, A-P4 / SM, 500 mm box. No ballast.

## 0. Outcome
| # | Item | Result | Verdict |
|---|---|---|---|
| 1 | Root cause | The PETG block is printed and judged on the 9.5 MPa interlayer allowable (EST) with KP 2.156: at the rigid-body (RB) demand the junction P6 already runs at 8.8 MPa (My) + 6.2 (Mz) + 7.6 (torsion + shear), RB RF 0.86; P8 RB 1.18. x2.23 then needs 2.6x (P6) and 1.9x (P8) more strength. The section cannot grow that much: the ring chord is fixed by the 16 mm tube and the 23 mm ring (16.5 mm), the socket by the 25 mm rib inside a 29 mm box, and a PETG box big enough (about 40 x 40, EST) is heavier than the whole new part. **Material-limited, not a missing load path**: the path fin tube -> block -> rib -> D-226 fin node is right, and the rib (R1 / R2) already passes. | found |
| 2 | Redesign | **FIN-003 = one machined 6061-T6 root fitting** (Tormach / knee mill, two setups, 1.0 mm walls like the CGE-001 hub): ring OD 18.2 / bore 16.2 x 38 mm on the fin tube, **plug OD 22.8 / ID 20.8 x 31 mm bonded INSIDE the 25x23 rib end** (same 31 mm engagement), 2.0 mm end plate (24.6 mm diameter) the rib end bears on, notched by the fin tube. Load path: fin tube -> ring bond -> plate -> plug -> rib -> D-226 fin node bulkheads -> cell (unchanged downstream). | drawn |
| 3 | Strength, T-083 demand | **all RF-class rows pass at x2.23: min 1.21 (zeta <= 0.05; 1.40 at zeta 0.02, 1.21 at 0.05)**; zeta 0.10: min 0.89 (ring at the collar root, conservative), fin tube at the shorter ring edge 0.97 (1.01 with the old 60 mm ring) | **PASS** (zeta <= 0.05); zeta 0.10 gap listed |
| 3a | Sensitivity: demand re-run at the new 1.873 kg / CG 22.26 mm | root fitting min 1.21 (zeta <= 0.05); whole D-226 cell, rib, bridge, strut and R4 clamp min **1.09** (R4 junction, zeta 0.05); zeta 0.10 min 0.66 (C3, as T-083) | PASS (zeta <= 0.05) |
| 4 | Mass | fitting **12.04 g** each (drawn volume x 2.70) vs PETG drawn 22.86 g + 6.1 g undrawn enlargement tally: **-33.8 g** pair on the tally | |
| 5 | CG / SM | the lighter fittings move the tallied CG 5.2 mm forward (to 19.19 mm, below the 19.3 band edge; drawn forward trim end 18.54 < 19.0, CL-A-CG-TRIM-FWD). Ladder rung 3 (rearrange): **T083_DX -3 -> +3 mm** (cage, pack, tray windows 6 mm aft of T-083, 3 mm aft of T-077 p8). Tallied **CG 22.26 mm, SM 7.52 %**, trim ends 21.27 / 23.92; drawn 21.08 mm, 8.01 % | PASS A-P4 (19.3..26.0, trim 28.5), CL-A-CG-TRIM-FWD 20.08 >= 19.0 |
| 6 | Window / T-W / cruise | tallied **1,634.5 g, 1.873 kg**: window **+12.05 %**, T/W 2.641 / 2.118, cruise 236 s | PASS (A-P3, A-P2, cruise >= 204.6 s) |
| 6a | A-P6 | 1.3 Vs **17.53 m/s > 17.0** (T-083 17.71) | FAIL, carried (limit gap of T-083 s2.3; geometry cannot close it) |
| 7 | Box | x **490.9 mm** (T-083 496.9) of 500 | PASS |
| 8 | BOM | material from the existing T11 6061 offcut: **$0**; total **$1,981.31, margin +$18.69** (unchanged) | PASS |
| 9 | Exposed wire | 0.597 strand-m (T-083 0.609): pack leads 3 mm shorter each; the fitting adds none (no wire at the fin root) | listed (s7) |
| 10 | Gates | collide pose 21 PASS, 18 linkage poses PASS, assembly PASS (66 steps, 129 / 129), wire inventory, cad_mass, mission gate, prop sched, drawings 49 / 49, build guide OK; build_a fails only on the 1,500 g mass gate; proofs 8 failing claims (as T-083), CG claims pass | PASS except the mass gate (not relaxed) |

**Blocker:** none for this task. Carried, not mine to close: A-P6 (17.53 > 17.0, needs Dillon's CLmax / cruise decision from T-083), the zeta-0.10 regrowth (TP-3), the build_a 1,500 g mass gate (not relaxed), and the T-083 money item (motor SKU backorder).

## 1. Root cause (hand calculation, `t083b_rootblock.py --petg`, `rb_petg_z00*.txt`)
Reproduces T-083 exactly: P6 0.44 / 0.39 / 0.25 and P8 0.60 / 0.53 / 0.31 at zeta 0.02 / 0.05 / 0.10 (x2.23). Decomposition at zeta 0.05 (RB, with KP, MPa): P6 sigma from My 8.80, Mz 6.18, Fx 0.49; tau (torsion + shear) 7.63; P8 sigma 8.06, tau 4.44; junction My 9.45 N m RB. Against 9.5 MPa interlayer the block is near its limit before the dynamic factor. Three components contribute about equally, so no single dimension (e.g. a taller socket for My) fixes it; the 16.5 mm chord is set by the ring round the 16 mm tube.
Options weighed (least mass that passes with a sourced allowable):
| Option | Allowable | Result | Verdict |
|---|---|---|---|
| PETG grown in section | 9.5 MPa interlayer EST | needs about 2.6x section modulus on P6: a solid block about 40 x 40 mm round the 25 mm rib, more than 30 g each (EST) | rejected (mass; outside the rib / fairing envelope) |
| X7 Onyx + continuous CF | Onyx interlayer "—"; the bores lie in the layer plane so fibre cannot ring them; T-080 coupons C-1..C-3 open | not shown | rejected (no sourced allowable) |
| CF plate gussets on the PETG block | CF plate allowable "—" (repo uses glass +-45 70 MPa as a lower bound); PETG junction stays in the path | not shown | rejected |
| **Machined 6061-T6** | yield 240 MPa minimum (T-080 s1), bearing yield 386 MPa (ASM data sheet, t083_path.py) | 12 times PETG's specific strength; minimum gauge (1.0 mm, CGE-001 practice) sets the mass | **chosen** |

## 2. The part (drawn; `cad/amodel/wing.py` `build_fins`, constants `FB_*`, `fin_block_volume_m3`)
| Feature | Value | Note |
|---|---|---|
| Ring | OD 18.2, bore 16.2 (0.1 mm bond gap per side, EST), height 38 mm (z +-19) | was PETG OD 23 x 60 |
| Plug | OD 22.8 / ID 20.8 x 31 mm (x 255..286), inside the 25x23 rib | the rib's own wall now carries bending to x 286; was a 29 x 29 outer socket |
| End plate | 2.0 mm (x 286..288), diameter 24.6 (0.2 mm under the rib OD), notched by the fin bore | the rib end bears on it |
| Cuts | fin bore through; rib-wall annulus r 11.4..12.55 ahead of x 286 (the ring front clears the rib wall); plug bore | modelled as real cuts (shop file has the bores) |
| Mass | **12.04 g** each, CG x 282 mm (voxel 0.2 mm x 2.70 g/cm3) | PETG 22.86 g (voxel, T-067 basis) |
| Envelope | x 255.0..303.1, y 370.7..395.3, z +-19 mm: inside the old block / ring envelope except the plate's outboard edge (x 286..288, y 389.8..395.3), free space | |
| Stock | two blanks 50 x 40 x 25.4 mm (x, z, y) from the T11 1.00 x 4.00 x 12 in 6061-T6511 offcut left after the two CGE-006 blanks (305 - 2 x 125 - 2 kerfs, about 51 mm, EST) | $0; second-attempt blank from T1 ("spare blank", allocation EST) |
| Process | Setup 1 (ring axis vertical): ring OD contour, 16.2 bore through. Setup 2 (plug axis vertical): plate and plug OD contours, plug bore. Tormach 440 or the knee mills (Jacobs list) | cutters / feeds "—" |
Bond prep: abraded 6061 + acetone; the repo's epoxy 2.0 MPa (EST) is used, the same value as the CGE-006 6061 flange bond (C3); a 6061 bond coupon belongs with TP-4.

## 3. Strength table (hand calculation on the T-083 demand: 1.913 kg, CG 24.41, Fp 36 N / 24 mm, 23 cases x zeta x mu 0.40 / 0.30; `rb_drawn_z002/z005/z010.txt`, `rb_drawn_zle005.txt`, `rb_drawn_all.txt`)
Rows: concurrent per-time-step combination, minimum over all cases, both fins. 6061 rows: von Mises x KF 1.725 <= 240 MPa; bonds KP 2.156 vs 2.0 MPa; bearing KP vs 386 MPa. Junction planes Q4 / Q5: section by a 0.1 mm grid, torsion by the Prandtl stress function (validated in `prandtl_check.txt`: circle J +1.5 %, tau +14 %; rectangle 5 x 20 tau -5 % against Roark; a x1.10 knock-up is applied to every tau).
| Row | RB (z 0.05) | x2.23 z 0.02 | **x2.23 z 0.05** | x2.23 z 0.10 |
|---|---|---|---|---|
| Q3 ring 18.2/16.2 alone at the collar root z +-12.3 (one foot, fin tube share ignored: conservative) | 2.70 | 1.55 | **1.21** | 0.89 |
| Q2 fin tube 16x14 at the new ring edge z +-19 (landing_path_a P4 formula) | 2.74 | 1.40 | **1.23** | 0.97 (1.01 at the old +-30 edge) |
| Q7a plug bond inside the rib, D23 x 31, shear | 3.97 | 1.75 | **1.78** | 1.63 |
| Q1a ring bond on the fin tube, D16 x 38, shear | 4.58 | 2.31 | **2.05** | 1.75 |
| Q6b plug at the mouth x 255 | 4.90 | 2.51 | **2.20** | 1.28 |
| Q6a plug at its root x 286 | 5.08 | 2.62 | **2.28** | 1.33 |
| Q5 plate aft face x 288 (plate + ring strips; all the fin wrench crosses it) | 5.29 | 2.35 | **2.37** | 2.15 |
| Q4 plate mid-plane x 287 | 7.34 | 3.26 | **3.29** | 2.99 |
| Q8 rib end bearing on the plate | 10.02 | 5.18 | **4.49** | 2.63 |
| Q7b plug bearing (6061) | 65.4 | 33.5 | **29.3** | 17.4 |
| Q1b ring bearing (6061) | 69.6 | 35.9 | **31.2** | 18.5 |
| **minimum (RF class)** | | **1.40** | **1.21** | **0.89** |
| Integrity class (outside the RF minimum, T-069 F-3): Q1c ring bond peel / Q7c plug bond peel | 0.36 / 0.34 | 0.19 / 0.17 | 0.16 / 0.15 | 0.10 / 0.09 |
| Record: CF fin-tube wall bearing in the ring / CF rib-wall bearing on the plug, at x2.23 [MPa], allowable "—" (TP-4) | | 10.7 / 11.5 | 12.4 / 13.2 | 20.9 / 22.2 |
PETG drawn block for comparison: P6 0.44 / 0.39 / 0.25, P8 0.60 / 0.53 / 0.31.
Notes: (a) the rib-wall bearing (13.2 MPa) is the same stress the PETG socket put on the rib (same D25/23, L 31). (b) The 38 mm ring is the least-mass choice; it raises the fin-tube wall bearing to 12.4 MPa (5.1 MPa with a 60 mm ring) and lowers the peel integrity row 0.40 -> 0.16. A 60 mm ring costs +3.2 g each (15.25 g, `mass_regrow_z010.txt`); I chose the lighter one because both are outside the RF minimum by the repo rule and both depend on the same TP-4 coupon. (c) Zeta 0.10 regrowth of the fitting alone: wall 1.3 mm and ring 60 mm, **17.92 g** each, min 1.01 (`rb_z010_regrow.txt`), only worth doing with the T-083 s5.3 cell regrowth (C3 0.66).

## 4. Mass, CG, window, T-W, A-P6, box (geometry arithmetic + prop_a EST; `t083b_metrics.py` -> `metrics_t083b.txt`, `gates/gate_*`)
### 4.1 Mass
| State | basic g | pred kg | CG mm | SM % | trim ends mm | window % (dl) | T/W fresh / sag | cruise s | 1.3 Vs |
|---|---|---|---|---|---|---|---|---|---|
| T-083 tallied (for reference) | 1,669.8 | 1.9129 | 24.41 | 6.65 | 23.44 / 26.03 | +11.02 | 2.586 / 2.074 | 223 | 17.71 |
| T-083b, cage at -3 mm (intermediate, rejected) | 1,636.0 | 1.8751 | **19.19** | 8.78 | **18.20** / 20.84 | +12.00 | 2.638 / 2.116 | 236 | 17.54 |
| **T-083b as drawn** (cad_mass.json) | **1,627.5** | 1.8656 | **21.08** | 8.01 | 20.08 / 22.74 | +12.25 | 2.652 / 2.127 | 239 | 17.49 |
| **T-083b tallied** (+7.0 g shoe cups at 298.1, the only undrawn item) | **1,634.5** | **1.8734** | **22.26** | **7.52** | 21.27 / 23.92 | **+12.05** | **2.641 / 2.118** | **236** | **17.53** |
| T-083b tallied, rib 14x12 (if the coupon passes) | 1,610.7 | 1.8468 | 19.88 | 8.50 | 18.88 / 21.56 | +12.75 | 2.679 / 2.148 | 245 | 17.41 |
Limits: A-P4 19.3..26.0 mm (proof cg_lo 19.0), trim aft 28.5, SM >= 5 %; A-P3 >= +5 %; A-P2 2.0 / 1.6; cruise >= 204.6 s; A-P6 <= 17.0. Predicted = basic x 1.1174 + 0.032 x 1.47.
Mass build-up T-083 tally -> T-083b tally (-35.3 g): root blocks -33.8 (2 x (22.86 + 6.1 EST tally - 12.04)), harness and tray -1.5 (shorter routes after the cage moved aft; tray plate end follows the pack).
Note: the 14x12 rib variant would again sit below 19.3 (19.88 / trim 18.87): if the coupon passes, the cage goes a further 2 mm aft (EST), not checked.

### 4.2 CG decision (ladder rung 3, rearrange; no limit change, no ballast)
The fittings take 21.6 g (drawn) / 33.8 g (tally) off x 283 mm: CG -3.4 / -5.2 mm. At T083_DX -3 mm the tally is 19.19 mm (band 19.3) and the drawn forward trim end 18.54 < 19.0 (proof CL-A-CG-TRIM-FWD FAILED in a check run). T-083 had moved the cage, pack and tray windows 3 mm forward only for aft A-P4 margin; that reason is gone. Tried 0 mm (tally 20.73, drawn trim-fwd 18.54 still < 19.0: fails the claim), then **+3 mm** (cage 9 mm forward of the wing instead of 12): tally 22.26 mm, near the band centre 22.65. Changes: `common.py` T083_DX = +0.003 (CAGE_DX, HUB, PACK_X, tray windows follow) and TRAY_X1 = -0.0028 + T083_DX (gate run 1, s6), `a_assembly_plan.py` B0j1 / B0j2 strut push axis (-0.42766, -/+0.90394) from STRUT_S / STRUT_E. The bridge and struts are 3 mm shorter than at p8 (their rows improve per mm, T-083 s3.2).

### 4.3 Landing demand at the new state (sensitivity; rigid-body dynamics; `sens/`)
The rows above use the T-083 demand as the brief asks. Because the CG moved 2.2 mm forward and the mass fell 40 g, I re-ran `t083_demand.py` unchanged at 1.873 kg / CG 22.26 mm (copy `sens/t083b_demand_sens.py`, npz in the scratchpad only): stroke 20.44 mm, **end tilt 2.82 deg** (<= 3.0), n 8.90 / 10.44 / 12.90 g at zeta 0.02 / 0.05 / 0.10. On it: root fitting min 1.39 / 1.21 / 0.90; D-226 path (`path_sens_*.txt`, t083_path rows; its FIN-003 row is the old PETG formula and is superseded by s3) min 1.09 C3 / 1.11 N4a / 1.12-1.13 rib R1 / 1.16 K1 / 1.18 B1 at zeta 0.02-0.05; strut + R4 clamp (`sc_sens_*.txt`) min 1.35 (z 0.02), **1.09** (z 0.05, R4 junction; T-083 1.13), 0.84 (z 0.10). Zeta 0.10: C3 0.66, K1 0.77, P15 0.81, R4 0.84, N3 0.84, B1 0.92 (the T-083 s5.3 gap, unchanged in kind).

### 4.4 Box
x 490.9 mm (PRP-004-LL -153.4 .. GER-002-UR 337.5), y 900.0, z 465.2 (`gates/gate_bbox.txt`; T-083 496.9). PASS against 500 mm.

## 5. BOM
No purchase: the two blanks come from the T11 offcut (`T083b_data/BOM-T083b.csv`: T11 note only; `bom_t083b.py` -> `bom_t083b_out.txt`, identical totals to T-083 after AM-019): goods 1,416.35, tax 145.18, shipping 67.84, FAA 5.00, spend 1,634.37, crash reserve 346.94, **total $1,981.31, margin +$18.69**. A dedicated bar would not fit the margin: Alcobra 1.00 x 2.50 in 6061-T6511 is listed at "$29.70 – $237.60" over 12-94 in, no per-length price shown (https://alcobrametals.com/product/1-x-2-1-2-6061t6511/, read 2026-11-21), i.e. about $32.74 with tax for 12 in (EST): over the $18.69 margin. Risk: if the T11 offcut is short after kerfs, the second blank comes from T1 (EST allocation), else this is a money item.

## 6. Gates (`T083b_data/gates/`, driver `run_gates_t083b.sh`, one run at the end)
Run history: run 1 (`gates/run1/`) found one static collision, PWR-002 strap loops x CGE-008 rear lip tab 1.00 mm: the tray plate aft end TRAY_X1 had stayed at -2.8 mm while the pack moved 3 mm aft; fixed `common.py` TRAY_X1 = -0.0028 + T083_DX (strap inner face 1.0 mm clear). Run 2 re-ran all gates; a leftover a_assembly.py from the stopped run 1 overlapped run 2's two collide jobs (shared `cad/out/_job.json`), so run 3 re-ran both collides alone and the proofs after assembly.json existed. Final rows:
| Gate | Run | Exit | Time | Result |
|---|---|---|---|---|
| build_a | 2 | 1 | 18 s | 10 modules, **1 error: graph:mass 1,627 g > 1,500 g MASS-GATE limit (not relaxed, as T-083)**; otherwise clean |
| `A_ELEV_POSE=21 collide_a.py` | 3 | 0 | 991 s | **PASS**, 583 bodies, 129 parts, static / -21 / +21: 0 pairs > 0.05 mm; wire ends 0, folds 0 (run 2 also PASS) |
| `collide_a.py --linkage-poses` | 3 | 0 | 1,135 s | **PASS**, 18 poses (run 2 also PASS) |
| `a_assembly.py` | 2 | 0 | 2,245 s | **PASS**, 66 steps, 129 / 129 parts, 0 blocked (C5 root fittings from aft into the rib ends, B0j1 / B0j2 new strut axes) |
| wire_inventory | 2 | 0 | 11 s | exposed 0.597 strand-m, total 11.825 |
| cad_mass | 2 | 0 | 8 s | 1,627.5 g, CG 21.08 mm |
| `mission_gate_a.py --o4b` | 2 | 0 | 1 s | CG 21.1 mm, SM 8.0 % |
| `prop_a.py --sched --mass 1.873` | 2 | 0 | 8 s | cap 1.0 at every voltage; derate 0.93: T/W 2.752 / 2.184 (no download), window +13.6 % |
| `proofs/run_all.py` | 3 | 1 | 2 s | **8 failing claims, as T-083** (5 known: horn-rib foam hold / stall, elevon torsion foam, horn bearing stall, linkage free-play; 3 mass: MASS-PRED 1.866 kg, MASS-GATE-ROOM, CUTS-REQUIRED 395.6 g) + FLUTTER-ELEVON-NOM UNVERIFIED; CG claims pass: CL-A-CG 21.08, CG-TRIM-FWD 20.08 >= 19.0 (+6 %), TRIM-AFT 22.74 |
| bbox (`t083_bbox.py`) | 2 | 0 | 8 s | x 490.9 / y 900.0 / z 465.2 mm |
| drawings | 2 | 0 | 225 s | 49 / 49 composed; FIN-003 drawn 48.1 x 24.6 x 38.0 mm (2,024 tris; 23 non-manifold edges reported by the drawing mesher where the bore notch meets the plate face: a tessellation note, not a gate); "printed parts not in one piece: AVN-010" (as before) |
| build guide | 2 | 0 | 5 s | 2,317 lines, 66 steps, 50.2 h EST (T-083 46.8 h: +3.4 h for machining two fittings, EST) |
| parts_links | 2 | 0 | 4 s | written |
| `tools/ledger_audit.py` | - | 0 | - | 0 errors (`ledger_audit.txt`) |

## 7. Exposed wires (`gates/gate_wire_inventory.txt`)
Total 0.597 strand-m (T-083 0.609). Changed: pack leads E-HRN-13 0.253 strand-m in `wire_inventory.json` (2 strands x 126.6 mm; the earlier text said 0.133 -> 0.127, a transcription error, corrected T-023 F-5; the listed items sum to 0.5975 only with 0.253; the pack sits 6 mm further aft, nearer the wing; reason unchanged: the pack must come out of the tray). Unchanged: X2216 phase strands 12 x about 8.4-8.9 mm between the can and the cup lead hole (E-HRN-02..05, 0.008-0.009 each edge), balance lead 64 mm, battery tail 42 mm, servo lead ends 2 x 12 mm, GPS 3 mm. The root fitting carries no wire.

## 8. Ladder (docs/engineering-decisions.md failure-resolution ladder) and decisions taken here
- FIN-003 rows: rung "redesign the element" (material and form), no limit change: PETG block -> 6061 root fitting with an internal plug.
- Ring 38 mm (least mass) over 60 mm (+3.2 g each): s3 note (b).
- CG: rung 3 (rearrange): T083_DX -3 -> +3 mm.
- Stock: existing T11 offcut, no purchase.

## 9. Proposed text (not applied)
**CHANGE-LOG (T-083b; ladder: redesign of the element + rung 3 rearrange; no limit change, no ballast):** "Fin root block FIN-003 redrawn as a machined 6061-T6 root fitting (Tormach, T11 offcut): ring OD 18.2 / bore 16.2 x 38 mm on the fin tube, plug OD 22.8 / ID 20.8 x 31 mm bonded inside the 25x23 rib end, 2.0 mm end plate notched by the fin tube; 12.04 g each (PETG block 22.86 g + 6.1 g undrawn enlargement). Root cause of P6 0.25-0.44 / P8 0.31-0.60: PETG interlayer 9.5 MPa at KP, the section is fixed by the tube and rib sizes; no PETG section fits. All fitting rows pass at x2.23 on the T-083 demand at pad zeta <= 0.05 (min 1.21, ring at the collar root); zeta 0.10 min 0.89. Lighter fittings moved the CG 5.2 mm forward (19.19 mm < 19.3): cage, pack and tray windows 3 mm aft of p8 (T083_DX +3). Tray plate aft end follows the pack (TRAY_X1 + T083_DX). Tallied 1,634.5 g, 1.873 kg, CG 22.26 mm, SM 7.52 %, window +12.05 %, T/W 2.64 / 2.12, cruise 236 s; A-P6 17.53 > 17.0 (carried); box 490.9 mm; BOM unchanged $1,981.31. Sensitivity demand at the new state: whole D-226 path min 1.09 at zeta <= 0.05."
**MASS-GATE basis:** FIN-003 12.04 x 2 (6061, drawn volume x 2.70); drop the +12.2 g enlarged-root-block tally line.
**TEST-PLAN TP-4 (add):** 6061-to-CF epoxy bond coupon (abraded 6061, the root fitting plug / ring prep) and CF tube wall bearing at >= 13.2 MPa (rib) / 12.4 MPa (fin tube) x 2.23 basis.
**BUILD:** step C5 rewritten (machine, then bond the plug into the rib end).

## 10. Data index (`T083b_data/`)
Strength: `t083b_rootblock.py` (-> `rb_<tag>.json` / `.txt`: `rb_drawn_*` adopted, `rb_petg_*` root cause, `rb_z010_regrow.txt`), `prandtl_check.txt`. Mass: `t083b_mass.py` (sizing tool, no bond gap), `mass_adopted.txt`, `mass_regrow_z010.txt`; drawn mass `wing.fin_block_volume_m3`. Metrics: `t083b_metrics.py` -> `metrics_t083b.txt`. Sensitivity: `sens/` (demand copy, path and strut-clamp copies and their outputs, demand json). printed_mass: `t083b_write_printed_mass.py`. BOM: `BOM-T083b.csv`, `bom_t083b.py`, `bom_t083b_out.txt`. Backups: `wing_t083_backup.py`, `common_t083_backup.py`, `a_assembly_plan_t083_backup.py`, `a_build_steps_t083_backup.py`, `parts_links_a_t083_backup.py`, `printed_mass_t083_backup.json`. Gates: `run_gates_t083b.sh`, `run_gates_t083b_r3.sh`, `gates/` (`run1/`, `run2/`, `run2_ASSEMBLY.md`), `ledger_audit.txt`.
Files changed in the repo: `cad/amodel/wing.py` (FB_* constants, fin_block_volume_m3, FIN-003 P line, build_fins), `cad/amodel/common.py` (T083_DX, TRAY_X1), `cad/amodel/printed_mass.json` (FIN-003 removed), `cad/a_assembly_plan.py` (B0j1 / B0j2 axes), `cad/a_build_steps.py` (C5), `cad/parts_links_a.py` (FIN-003); regenerated by the gates: drawings, build guide, cad_mass.json, params, proofs outputs, wire inventory.

## 11. Limits
- Hand bounds with EST allowables except 6061 yield (minimum, secondary source) and bearing (ASM data sheet). No FEA of the fitting: the knee at the plate / ring junction has no stress-concentration factor (Q4 / Q5 carry 2.4-3.3 at zeta 0.05; a Kt above about 2.4 would need the FEA the hub got).
- Q3 and Q5 put the whole wrench through the fitting (fin tube share ignored): conservative.
- 1.0 mm walls follow the CGE-001 hub practice; manufacturability of a 38 mm tall 1.0 mm ring and a 31 mm deep 20.8 mm bore is EST.
- The tally CG uses the EST shoe-cup line (7.0 g at 298.1). The 14x12 rib variant would need another cage move (s4.1).
