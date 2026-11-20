# T-076c: hub escalation implementation (D-220), steps 1-4, concept A O4b (2026-11-20)

Status: **review evidence, not VERIFIED COMPLETE. Step 4 STOPPED at H-A1** on the stop rule (rows < 1.0 at max(DAF, 1.5)). The aluminium hub itself passes; the **CF arm-tube shear and the arm-tube/sleeve bond rows fail** for the landing demand, and they fail with a PETG hub too (control), so they are not caused by the hub material. H-A2 was not run (it is conditional on H-A1 passing). Not committed. No CAD, docs, CHANGE-LOG, ledger, MASS-GATE or BOM file was touched. `landing_centre_a.py` / `landing_a.py` defaults unchanged.
Escalation audit: `docs/audits/2026-11-20-hub-escalation.md` (s3.4 steps 1-4). Data and scripts: `redesign/qp/A/mechanism/out/T076c_data/`. Large arrays (traces, D-1 wrenches, the H-A1 mesh) are in the git-ignored `T076_data/fea/*.npz`.
Limits not relaxed: RF >= 1.0, KF 1.725 / KP 2.156, PETG 20 / 9.5 MPa EST, CF 350 / 40 / 30 MPa EST, epoxy 2.0 MPa EST, the 21 landing cases (hard 1.2 m/s), mass 1.64 kg. EST = estimate; "—" = unknown. Note: the cases list holds **21** cases (10 + 10 SITL-envelope + 1), the "23" in older records is a label.

## 0. Acceptance test (restated from the brief, then run)
1. Step 1: new script; all six wrench components at the bore mouth and at bore mid-length per case at 1.64 kg; bending rows with |(My,Mz)| and V = |(Fy,Fz)|; block net-section row; reproduce audit V3 / V4 within 2 %. **Run: all 17 compared numbers within 2 % (or within half a unit of the audit's last printed digit)**, `step1_demand_stdout.txt` section 5.
2. Step 2: D-1 modal transient, stop if DAF_bridge >= 1.93. **Run: not triggered on the audit's definition; see s2 for the three definitions and why.**
3. Step 3: corrected judging code (volume-weighted zone percentiles, corner exclusion, PETG orientation split, von Mises for metal, old p99 kept). **Written (`t076c_judge.py`) and run on H-A1.** The PETG orientation-split branch is implemented but was not exercised on a solved model (no PETG hub was judged, only the Al path), so it is untested beyond syntax: **unverified**.
4. Step 4: alloy properties cited from a read page; H-A1 (and H-A2 if H-A1 passes); stop on any row < 1.0 at max(DAF, 1.5). **Run: H-A1 done, rows < 1.0 found (tube shear, bond), STOP.**

## 1. Step 1 demand fix (rigid-body dynamics + hand calculation; `t076c_step1_demand.py`, 30 s)
Mass 1.64 kg (`LAND_MASS_KG` set inside the new script), D2 pad, 30 N plateau, dt 0.2 ms, hub-side group = ITEMS 2, 3, 4, 6, moments about the original bore mouth P0 (hub-frame x 24.0 mm, z -2.0 mm). Full per-case tables in `step1_demand_stdout.txt` (peak |Fx..Mz| per case at P0 and at the H-A1 bore mid-length).
Global peaks at P0: Fx 92.8, Fy 43.7, Fz 28.9 N; Mx 6.22, My 6.71, **Mz 17.51 N m** (governing sample "hard 10 wide + drift .5 y" step 342: F (-53.7, -28.9, 2.1) N, M (-0.07, 0.12, 17.51) N m, identical to the audit V1). 11 of 21 cases have |Mz| > 6.05 N m (the T-071b design moment).
Bearing rows (audit V3 formula, M_b = |(My,Mz)| about the bore mid-length, V = |(Fy,Fz)|, min over cases and time):

| variant | L mm | RF RB | RF x1.5 | RF x2 | My-only control (the T-071b method) |
|---|---|---|---|---|---|
| as drawn | 9 | 0.115 | 0.077 | 0.06 | 0.30 |
| V1 | 21 | 0.62 | 0.41 | 0.31 | 1.53 |
| C6 | 22.5 | 0.71 | 0.47 | 0.35 | 1.76 |
| V2 | 28.5 | 1.13 | 0.75 | 0.57 | 2.75 |
| H-A1 (Al, PETG bore model) | 30 | 1.25 | 0.83 | 0.62 | 3.01 |

Bore length for RF 1.0: 26.4 mm (RB), 32.3 mm (x1.5) against the audit's 26.6 / 32.6. Block net section (20 x 20 mm solid PETG, 9.275 MPa): capacity 12.37 N m, RF 0.71 / 0.47 / 0.35 at RB / x1.5 / x2; width for RF 1: 23.8 / 29.1 / 33.7 mm; 27 mm wide block RF 1.29 / 0.86. Bridge 16x14 bending at the mouth: RF 1.93 / 1.29 / 0.96 (audit 1.93 / 1.29 / 0.97). The one comparison that differs by more than 2 % is the "as drawn" RF (0.115 against the printed 0.11: +4.5 % on a two-decimal number, within its rounding). The My-only control column reproduces the old C6 RF 1.76 (T-076 s1.3), so the old method and the corrected one differ by the Mz term alone.
Pad stroke (landing_a, same runs, `step1_pad_stroke.json`): **no case bottoms**. Maximum stroke 18.8 mm ("hard 10 narrow + drift .5") against the 20 mm usable stroke (reserve 1.2 mm); 15.8 / 15.4 mm for the two 10-degree narrow cases; wide cases 6-12 mm. Per-foot |Fx| peaks of 41-47.5 N above the 30 N plateau are the viscous term (zeta 0.05 damper) in the sim, not bottoming. This answers audit F-9 for the sim model (the sim pad itself is EST, "—" measured).

## 2. Step 2 D-1 modal transient (dynamics; `t076c_step2_d1.py`, 2 min)
Beam frame `fe_a.py` + the `t073_modal.py` patches (imported unmodified) + the T-076 T067 mass mapping (copied, RESID 1, 1.640 kg, EST). Free-free, all 6N modes, exact first-order-hold integration of the modal equations (no numerical damping), zeta 1 % and 2 % in flexible modes. Input: the 21 foot-force histories applied at the four fin-tip nodes with the foot offset moment. **One-way coupling** (forces from the rigid-body sim, not re-solved with the flexible frame); gravity and rotor lift neglected like the rigid-body wrench. 12 frame runs: bridge as-built 16x14 (CAD D-206) and "rec" 12x10 (the committed t073 / T-076 modal CFG, which predates D-206: **finding**, the A-P10 modal record uses a 12x10 bridge), corners kd / nom / hi, zeta 1 / 2 %.
Consistency checks: the FE quasi-static (inertia-relief) hub Mz follows the sim rigid-body Mz with correlation >= 0.996 and a constant ratio 0.55. Cause: the sim ITEMS model has the 213 g wing as a point mass at y = 0, so its yaw inertia is 68.4 g m2 against 108.5 g m2 for the FE mass model (CG x 26.3 against 22.9 mm). So the sim rigid-body demand is conservative for hub Mz relative to a distributed-wing mass model, and the foot forces are one-way inputs from the lighter-inertia model (EST, not re-solved).

DAF results (max over the 12 runs; hub-root = bridge + struts wrench about P0; "env" = envelope over cases, "case" = max over cases with the reference >= 50 % of its envelope):

| quantity | vs sim rigid-body (the audit definition, demand basis) env / case | vs FE quasi-static env / case |
|---|---|---|
| hub-root Mz | 0.90 / 1.21 | 1.75 / 2.36 |
| bridge |(My,Mz)| at the mouth | 0.91 / 1.08 | 2.82 / 4.92 |
| arm-root bending (hub end of the 4 arms) | — (no sim reference) | 2.30 / 3.73 |
| component envelopes vs sim RB (nom, zeta 1 %): Fx, Fy, Fz, Mx, My, Mz | 1.53, 2.70, 3.99, 0.89, 1.70, 0.88 | |

Dynamic peaks of the as-built frame: hub Mz 13.3-15.7 N m (against sim RB 17.51), bridge |(My,Mz)| 11.4-16.0 N m, **bridge RF with the dynamic peak = 2.12 minimum** (hi corner, zeta 1 %; capacity 350 MPa EST / KF; 2.12-4.39 over the runs). The hub-side forces are amplified up to 4x (Fz 115 N against 28.9 N RB: arm flapping), but the stress-driving moments are not (the force terms are small in the bearing formula).
**Stop rule (DAF_bridge >= 1.93):** not triggered on the audit's definition (dynamic bridge peak against the rigid-body demand: 0.91 enveloped, 1.08 case-max) and on its stated purpose (RF_bridge(dyn) >= 2.12, not < 1). **Flagged ambiguity:** against the FE quasi-static reference the bridge ratio is 2.82 (env) / 4.92 (case), which would be >= 1.93; those cases have small absolute moments (the 4.9 case has a 3 N m reference), and that reference is itself 0.55 of the sim demand (inertia mismatch above), so I did not read it as the stop. If the conductor reads the rule on that basis, the bridge options are: (a) 18x16 tube ("—": stock and price not looked up); (b) rung 1b: pad stroke reserve is only 1.2 mm (18.8 of 20 mm in the worst case), so a longer stroke is the lever, "—" for its mass and box fit; (c) 16x14 stays with RF >= 2.12 on the dynamic peak.
Judging scale used downstream: max(DAF, 1.5) = **1.5** with DAF = 1.21 (hub Mz case-max vs sim RB); plus the D-1 dynamic wrench histories applied directly (1,024 candidate steps, partition A) because a scalar DAF does not describe the force components. Also tabulated for sensitivity: 2.36 (the largest hub DAF against the FE quasi-static reference, which double counts the inertia mismatch).

## 3. Step 3 judging code (`t076c_judge.py`)
Volume weights = Gauss weight x detJ computed from the mesh (check: sum 20,550 mm3 against the mesh volume 20,548 mm3); corner exclusion 0.5 mm (EST per the audit) from tied re-entrant edges (nodes on a hub/other-material interface and a free hub face: 478 nodes on H-A1, **0.29 % of the hub volume excluded**, per zone 0-1.4 %, listed in the JSON); von Mises vs yield / KF for metal; PETG layer-normal / in-layer split for a declared print normal (not exercised: see s0); old unweighted first-principal p99 kept as the `old p99` column. Zones as `t076b_run.regions`. Mesh convergence (< 5 % on one refinement, audit s2.4) **not done** (one mesh, MS 1.1): stated, "—".

## 4. Step 4 H-A1 (FEA; `t076c_ha.py`, 104 min incl. judging; mesh 427,333 tet10, 1.97 M dof, equilibrium error 1.9e-10)
Alloy (read page): Wikipedia, "6061 aluminium alloy", https://en.wikipedia.org/wiki/6061_aluminium_alloy, read 2026-11-20 by WebFetch: density 2.70 g/cm3, Young's modulus 69 GPa (text; infobox 68), Poisson's ratio 0.33, yield "at least 240 MPa (35 ksi)" (typical 270), ultimate at least 290 MPa, fatigue limit 97 MPa at 5e8 reversed cycles (**not used**: landing is a limit-load case, no cycle count claimed). Used: E 69,000 MPa, nu 0.33, rho 2.70, **yield 240 MPa (the minimum)**, allowable von Mises = 240 / 1.725 = 139.1 MPa. **Source is secondary** (a design value needs the supplier certificate or MMPDS, "—" not read; MakeItFrom and MatWeb pages refused automated reads). Shear strength not given; not used.
Geometry (C6 envelope; `make`-style GEO overrides): X_BR0 15.0, X_HUB1 45 (bonded bore L 30), COL_E 21, BR_GAP 0.5 (tube end released), SLV_W 1.5, BR_CH 0.8, FIL 2.0, MS 1.1. **Solid hub volume 20,548 mm3 = 55.5 g aluminium** (audit estimate 53 g solid; lightened 24-30 g EST not run). Wall: mesh 8 min, solve 6 min, judging 70+ min (first pass aborted for speed, `ha1_aborted_first_pass_stdout.txt`; unchanged numbers reproduced).

Hub von Mises rows, RF = 139.1 MPa / value at **scale 1.0** (RF at 1.5 = RF / 1.5):

| load set | whole-hub w p99.9 | max excl (0.5 mm) | RF p99.9 / RF max excl | RF max excl at 1.5 | worst zone (max excl) |
|---|---|---|---|---|---|
| A partition, 301 landing combos | 34.4 | 81.7 | 4.04 / 1.70 | **1.13** | collar x > 24 (3.47 / 1.70) |
| B partition | 33.6 | 81.7 | 4.15 / 1.70 | **1.13** | collar |
| D-1 dynamic wrenches (1,024 steps, A) | 35.0 | 79.1 | 3.97 / 1.76 | (scale 1 is the demand) 1.76 | sleeves outside the block 2.08, block forward 2.17 |
| F1 / F2 flight (KF) | 9.6 / 11.0 | 21.2 / 24.0 | 14.5 / 6.6, 12.7 / 5.8 | | |
| S1 / S2 / S3 strike (factor 1.0) | 20.5 / 26.6 / 7.8 | 44.1 / 61.0 / 18.6 | 11.7 / 5.4, 9.0 / 3.9, 30.7 / 12.9 | | |

Old columns kept (landing A partition, whole hub): unweighted principal p99 18.7 MPa (collar 21.6) against the volume-weighted vm p99 21.0 / p99.9 34.4. The aft block / bore wall: max excl 33.4 (RF 4.16), floor band 33.2 (4.19): the PETG hot spots (floor band, block net section) are gone in aluminium. At the sensitivity scale 2.36 the collar max excl is RF 0.72: the collar max sits at the collar's sharp re-entrant corners (112 MPa raw max, 81.7 after exclusion), "—" until a filleted CAD shape exists; flagged, not a stop (the scale double counts, s2).
Hand rows (`t076c_hand_al.py`): block net section RF 10.6 (RB) / 7.1 (x1.5) solid, 8.0 / 5.4 with the 16 mm bore removed; CF bridge transverse bearing in the Al bore L 30: RF 2.93 / 1.95 / 2.39 (RB / x1.5 / D-1 dynamic; 40 MPa transverse EST); bore bond in torsion Mx RF 1.80 / 1.20 / 1.85; bridge tube bending RF 1.80 / 1.20 / 1.50 (non-coincident maxima, conservative, against 1.93 coincident in s1).

**Rows below 1.0 (the stop), CF tube and bond from `fea_hub_c6.evaluate` (the A-partition landing combos; this evaluation was never run for the landing demand before):**

| row | Al, A, RB x1.0 | Al, A, x1.5 | Al, B, x1.0 | Al, D-1 dynamic | PETG control A / B, x1.0 |
|---|---|---|---|---|---|
| tube A axial (350) | 1.45 | 0.96 | 1.78 | 1.16 | 1.47 / 1.69 |
| tube B axial | 1.37 | 0.91 | 1.60 | 1.20 | 1.39 / 1.51 |
| tube A hoop (40) | 1.50 | 1.00 | 1.83 | 1.24 | 1.27 / 1.42 |
| tube B hoop | 1.58 | 1.06 | 1.87 | 1.34 | 0.63 / 0.67 |
| **tube A shear (30)** | **0.77** | 0.52 | 0.95 | 0.63 | 0.77 / 0.84 |
| **tube B shear** | **0.74** | 0.50 | 0.86 | 0.65 | 0.50 / 0.52 |
| **arm bond, mean shear x KP (2.0)** | **0.89** | 0.60 | 0.92 | 0.84 | 0.49 / 0.50 |

All governing tube values sit at s = 24.9-25.2 mm along the tube, i.e. at the sleeve exit (L_SLV 24), the stiff-sleeve edge of the tube, where a bonded-sleeve model has a stress singularity; the repo judges tube rows by the maximum (no percentile), so I report the maximum and did not apply the new exclusion to tubes (not asked for). Strike S2 tube A shear RF 1.22 reproduces the audit's "1.22 tightest". The aluminium hub **improves** the bond (0.49 to 0.89) and the PETG control is not better on shear or hoop, so the failing rows come from the **landing demand reaching the arm tubes** (A: whole wrench through the stub ends; B: arm group only, 0.86-0.95), not from the hub material. Landing flows through the arm tubes at the hub exit: 22.5 MPa shear against 30 / 1.725 = 17.4 MPa allowable (EST).
Decision for the conductor: the hub material change (rung 4a) is not enough by itself; the arm-tube exit and bond need their own fix (candidate levers, none tried: a longer or tapered sleeve exit, a flared doubler, the pad-stroke lever 1b to cut the demand, a CF doubler under the sleeve edge, re-judging with a tied-edge exclusion for the tube rows if the conductor accepts that for CF). Each is "—" (not run) in mass and rows.

## 5. Findings (new, for the conductor to place in records)
| ID | Severity | Finding |
|---|---|---|
| T76c-1 | CRITICAL | Landing arm-tube shear (RF 0.74-0.95 at RB) and arm bond (0.49-0.92) fail on the H-A1 geometry and on a PETG control: the tube rows were never evaluated for the landing demand. Hub material is not the cause. |
| T76c-2 | MAJOR | Al hub itself passes at max(DAF, 1.5): vm max excl RF 1.13 (landing x1.5), 1.76 (D-1 dynamic), 55.5 g solid (+34 g against C6 21.44 g; upper bound, not lightened). The collar re-entrant corners govern (RF 1.70 at RB). |
| T76c-3 | MAJOR | D-1: hub-root Mz DAF 0.90 / 1.21 vs the sim demand, but hub-side forces amplify to 4x and the FE-consistent static demand is 0.55 of the sim's (sim wing is a point mass: yaw inertia 68 against 108 g m2). One-way coupling. |
| T76c-4 | MINOR | The T-073 / T-076 modal CFG carries a 12x10 bridge; CAD D-206 is 16x14 (modes 9.6-11.1 Hz lowest). A-P10 should be re-run with the 16x14 bridge. |
| T76c-5 | MINOR | Pad never bottoms in the sim (18.8 of 20 mm worst), the 41-47 N foot peaks are the damper term. |
| T76c-6 | MINOR | Step 3 PETG orientation-split path untested; mesh convergence not done; alloy source is secondary. |

## 6. Suggested records (conductor writes them; I wrote none)
CHANGE-LOG ladder entry: rung 4a (Al hub) tried with H-A1: hub rows pass, CF tube exit and bond rows fail at the landing demand independent of hub material, so rung 4a alone does not close O4b; next rung applies to the arm-tube exit / demand (1b or 2 on the sleeve). AR record: D-1 (s2) and H-A1 (s4). Demand basis: all six wrench components (s1).

## 7. Reproduce
`cd redesign/qp/A/mechanism/out/T076c_data`: `python -I t076c_step1_demand.py` (30 s), `python -I t076c_step2_d1.py` (2 min), `python -I t076c_hand_al.py`, `./run_ha1.sh` (about 100 min), `./run_tubes.sh` (about 50 min). Logs: `step1_demand_stdout.txt`, `step2_d1_stdout.txt`, `ha1_stdout.txt`, `tubes_stdout.txt`; results `step1_demand.json`, `step2_d1.json`, `ha_result_t076cha1.json`, `tubes_diag.json`, `hand_al_stdout.txt`. Check run: `python -I tools/ledger_audit.py` gives 0 errors (unchanged by this task).

## 8. Limits
Every allowable except the Al yield is EST. Al yield is a minimum from a secondary page. D-1 is one-way coupled with EST mass placements; DAF depends on the reference chosen (s2). H-A1 is one mesh, solid (unlightened), no fillets on the collar corners, no mesh convergence; tube rows use a max with a bonded-sleeve singularity. H-A2, the lightened mass, the CG trim (+34 g solid at the hub moves the CG forward about 2 mm at 1.64 kg: 34 x 90 / 1,640, EST, **above the 0.5 mm forward-trim margin**, to re-check), the purchase and mill access were not addressed.
