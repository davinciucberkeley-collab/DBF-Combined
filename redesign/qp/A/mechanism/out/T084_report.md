# T-084: D-232 FAIL closure (A-P9 tip-over; D-185 spar mode). 2026-11-22. Not VERIFIED COMPLETE. Nothing committed.

No edit to docs/, the CHANGE-LOG, the ledger or the spec files (proposed CHANGE-LOG text in s9). Labels: EST = estimate; "—" = unknown.
Analysis categories used: **geometry arithmetic** (tip-over statics, mass / CG, box, tube cut list), **rigid-body dynamics** (the T-083 landing demand, not re-run; structures_a.py s5 landing sweep, re-run), **hand calculation** (shoe, fin-tube and root-fitting strength rows), **FEA-lite** (3-D Euler-Bernoulli beam frame `fe_a.py`, eigen + modal forced response; no shell or solid FEA), **illustrative** (prop_a EST thrust model for window / T-W / cruise / A-P6), **interference** (collide, linkage poses, a_assembly). No CFD, no flight dynamics, no SITL.
Data and scripts: `T084_data/` (index s10).

## Acceptance test (restated from the brief)
1. A-P9: static tip-over >= 30 deg on the DRAWN pads, sized with margin (target edge >= 30.5 deg) at the current CG and at both pack-trim ends; root cause of why D-215 T2' is not in the CAD; fitting / shoe rows RF >= 1.0 at x2.23 for pad zeta <= 0.05; pad demand re-checked if the pad changes.
2. D-185: root cause of the in-band spar mode (shape; coupling 0.45 -> 0.52) and a real design change (stiffness, mass placement, joint, or moving the mode) so no strongly coupled mode (coupling >= 0.5) sits in 94-321 Hz; frequencies and coupling at kd / nom / hi after the change. Band and metric not redefined.
3. CAD, printed_mass.json, build steps, drawings updated; mass / CG / SM / window / T-W / cruise / A-P6 recomputed; structures_a.py re-run; BOM total <= $2,000 (margin was +$0.88); 3-D gates once at the end; proofs failing claims not above 8.
Never: limit relaxed, ballast, metric or band redefined. Stop and report if a FAIL cannot be closed within the limits and the money.

## 0. Outcome
| # | Item | Result | Verdict |
|---|---|---|---|
| 1 | A-P9 root cause | D-215 (T-068) put the pad move in Phase 2 (CAD), gated on Phase 1 passing; T-069 Phase 1 failed (cup rows 0.01-0.13, P15 / P16 wing torsion), so Phase 2 never started; then D-222 explicitly gated any pad CAD change on the TP-3 drop test, and the analyses carried an undrawn "analysis pad" (x 0.3475, z 0.1907). Not superseded by D-229, and not the CG: the CG moved 0.3 mm FORWARD (21.37 -> 21.08 mm), which changes the angle by -0.02 deg | found |
| 2 | A-P9 fix | **T3 of the T-068 trade (fin tubes longer), chosen over T2' (pad outboard on the shoe)**: FIN_H 0.180 -> **0.1937 m**; the shoe and pad are unchanged relative to the tube end, so the pad centre is z 0.1907 m = the T-083 demand pad (zf 0.19073) and the outer edge 0.1967 m. T2' puts the pad 7.7-13.7 mm beyond the tube end on a printed toe: the toe needs about 16.5 x 21 mm section and a 24 mm ring to pass (+about 27 g EST for four shoes) | **drawn** |
| 3 | A-P9 result | edge toward the CG (D-215 pivot) **min 31.00 deg** (drawn CG, forward trim end), 31.00-31.31 over drawn / tallied CG and both trim ends; pad centre 31.07-31.38; pad centre toward the CG (bound) 30.20-30.50 | **PASS**, +0.50 over the 30.5 target |
| 4 | Strength | shoe rows unchanged (same geometry relative to the tube end): S2 1.12, S3 bearing 1.12, S3 shear 1.30, fin tube at the shoe 1.67 (x2.23, zeta 0.05); root fitting rows identical to T-083b (min 1.21 at zeta <= 0.05) because the demand already had the pad at z 0.1907. Pre-existing and unchanged: pad-to-shoe PSA row 0.13 (retention, D-215 (2) cup still undrawn, T-069 cup rows 0.01-0.13) | PASS for every row the change touches; PSA retention open (not new) |
| 5 | D-185 root cause | The 201 / 215 / 244 Hz mode (kd / nom / hi) is the wing's antisymmetric IN-PLANE bending with the cage swaying sideways. In the FE the wing's in-plane stiffness is the 12x10 spar alone (EI 37 N m2); the drawn D-226 wing has 330-6,800 N m2 nominal, 185-1,650 at the lower bound. Coupling 0.45 -> 0.52 came mainly from the strut end moving inboard 0.300 -> 0.285 m (0.42 -> 0.55) and the fin-root lumps 6 -> 32 g (0.48 -> 0.53) | found: a beam-model artifact |
| 6 | D-185 with the cell credited | the in-plane mode leaves the band at all corners (max in-band coupling 0.21-0.27), but the wing-flap / cage-bounce mode moves up to 79-96 Hz: **in band at hi (96.2 Hz, cx 0.81 / cy 0.93) with the nominal cell**; passes at kd / nom and at all corners with the lower-bound cell. With the pack at its drawn x (rigid on the hub) it is 94-107 Hz and other strong modes appear at 270-300 Hz | **NOT CLOSED** |
| 7 | D-185 design change | no lever inside the BOM moves the governing mode robustly out of the band (s2.5): bridge 12x10 gives 91.2 Hz at hi but fails the D-206 bridge torsion sizing; struts 10x8 / bridge 20x18 / spar 14x12 / strut end 0.30 change it by < 2 %; arms 14x12 raise it into the band at nom too | **blocker: options in s2.6** |
| 8 | Mass / CG | basic 1,627.5 -> **1,633.0 g** (+5.5: fin tubes +2 x 2.1, fairings +2 x 0.64 EST); tallied **1.8796 kg** (+6.2 g); CG 23.13 mm tallied (+0.87), SM 7.17 %, trim 22.14 / 24.78 | A-P4 PASS |
| 9 | Window / T-W / cruise / A-P6 | window **+11.88 %**, T/W 2.632 / 2.111, cruise 234 s; 1.3 Vs 17.56 > 17.0 m/s (carried FAIL, +0.03) | PASS except A-P6 (carried, TP-11) |
| 10 | BOM | no purchase: the two 387.4 mm fin tubes and the 114.5 mm bridge come from the one 1 m R02 tube (0.892 m used, EST kerfs); total **$1,999.12, margin +$0.88** unchanged | PASS |
| 11 | Box | x 490.9 mm (pad aft face to spinner, unchanged); fins 393.4 mm (was 366); CL-A-BOX-FIT packed height 0.39 -> 0.394 m, ratio 0.985 | PASS (thin) |
| 12 | Gates | see s7 | see s7 |

**Blocker:** D-185 is not closed. The T-066 FAIL is an artifact of the beam model, but the corrected model fails D-185 (a) at the hi corner on a different mode, and no design change within the budget, mass and limits moves it out robustly. The decision is for the design owner (s2.6). A-P9 is closed.

## 1. A-P9 static tip-over

### 1.1 Root cause: why the CAD never got T2'
1. **D-215 / T-068 s7** split the landing package into Phase 1 (analysis only) and Phase 2 (CAD: "shoe plate with the cup, pad outboard (edge z >= 0.195)"), with the stop rule "If P15 or P16 < 1.0: stop ... do not start Phase 2".
2. **T-069 Phase 1** (`T069_phase1.md` s RF table) failed: P15 wing torsion 0.15, P16 0.11-0.31, and the proposed cup itself (CUP wall bending 0.13, EVA bearing at the rim 0.01) at the rigid-body demand. Phase 2 was therefore never started; the wing torsion path went to D-216 / D-226.
3. **D-222** (landing demand root cause) then chose "pad specified by its dynamic force ... gated by a bench drop test (1.2 m/s, 73 mm drop) before the pad CAD changes" and an analysis pad with "pad edge +3.5 mm for A-P9" (`docs/audits/2026-11-20-landing-demand-rootcause.md` s4.1). From then on every landing demand (T-077 p6, T-083, T-066) used the analysis pad (x 0.3475, z centre 0.1907-0.1918) while the drawn pad stayed at z centre 0.177.
4. Not the cause: D-229 (the root fitting is at the rib end, not the shoe) and the CG (cad_mass.json 21.37 mm at T064r -> 21.08 at T-083b moves the drawn-pad angle 29.17 -> 29.15 deg, edge toward the CG).
So the A-P9 FAIL is a deferred CAD change whose gate (TP-3) concerns the pad's foam, length and plateau, not its z position. T-084 changes only the z position, which no test gates.

### 1.2 Options (trade table; ladder rungs 1 subtract, 2 modify geometry, 3 rearrange, 4 change approach, 5 add material)
| Option (rung) | Δ basic mass | A-P9 edge, worst CG | Strength rows changed | Box / other | Verdict |
|---|---|---|---|---|---|
| T7 re-base A-P9 to 29 deg | 0 | — | — | relaxes a PHYSICAL limit | rejected (D-215) |
| T5 shorter pad (rung 1) | -0.1 | 29.66 (T-068) | stroke lost | A-P5 | rejected (T-068) |
| T1 CG z to 0 (rung 3) | 0 | 30.03 at the drawn fwd trim end (atan(0.183 / 0.3165), FIN_H 0.180) | none | no mass identified to move; 0.03 deg margin | rejected |
| T4 CG 10 mm aft (rung 3) | 0 | 30.0 (T-068) | — | SM 7.2 -> about 3.1 % < A-P4 5 % | rejected |
| T2' pad outboard on the shoe, 13.7 mm (rung 2), sized here (`t084_shoe.py`, x2.23, zeta 0.05) | about +27 g EST for four shoes (toe 16.5 x 21 x 15 mm + ring 18 mm, OD 24: about 12 cm3 each at the T-067 basis S, vs 4.3 g now) | 31.00 | toe root S1 needs 16.5 x 21 mm (12 x 18: 0.58); ring section S2 needs OD 24 (OD 21: 0.97); ring bearing S3 needs L 18 (L 12: 0.77); pocket walls 0.31-0.41 (retention, as T-069) | z extent as T3 | rejected: heavier, new printed rows, a new cantilever on the landing path |
| **T3 fin tubes 13.7 mm longer each end (rung 2)** | **+5.5 g** (tubes +2 x 2.1, fairings +2 x 0.64 EST) | **31.00** | none new: the shoe, pad and fitting see the same geometry relative to the tube end; demand pad z unchanged | fins 366 -> 393.4 mm (box height 0.394 / 0.40); R02 tube 0.892 of 1.0 m; fin area +7.6 % (A-P15 "—", favourable sign); fin modes lower (spar-only lowest strong above the band 438 Hz, +36 %) | **chosen** |
T3 was rejected in T-068 only for "more CAD change than T2'" and fin area; with the T2' toe sized (it did not exist in T-068) T3 is lighter and leaves every strength row as it was.

### 1.3 Result (geometry arithmetic, `t084_tipover.py` -> `tipover_t084.txt`)
| CG basis | pack | CG x mm | **edge, toward CG (A-P9, D-215 pivot)** | centre (landing_a.static) | centre, toward CG (bound) |
|---|---|---|---|---|---|
| drawn | fwd trim end | 20.96 | **31.00** | 31.07 | 30.20 |
| drawn | nominal | 21.95 | 31.08 | 31.15 | 30.28 |
| drawn | aft trim end | 23.61 | 31.22 | 31.28 | 30.41 |
| tallied | fwd trim end | 22.14 | 31.10 | 31.16 | 30.29 |
| tallied | nominal | 23.13 | 31.18 | 31.24 | 30.37 |
| tallied | aft trim end | 24.78 | 31.31 | 31.38 | 30.50 |
X_GROUND 0.3375 m (electrical.py), pad z 0.1847-0.1967 m, CG z 6.48 mm (cad_mass.json). Before: 29.2 deg (centre), 29.15 (edge toward the CG). Margin +1.00 deg over 30, +0.50 over the 30.5 target; even the conservative centre-toward-CG bound is >= 30.2.
Sensitivity (not the drawn pad): if TP-3 lengthens the pad to the D-222 analysis length (X_GROUND 0.3475) the edge angle is 30.22-30.52 deg: still >= 30 but under the 30.5 target, so a pad lengthening must re-check A-P9 (about +2 mm FIN_H, or the box height allows +3 mm). Build tolerance: 1 mm short on the tube end costs about 0.13 deg (build step C6 check).

### 1.4 Strength rows the change touches (hand calculation on the T-083 demand: 1.913 kg, CG 24.41, pad 36 N / 24 mm, 21 cases x zeta x mu; contact x 0.3475 (demand, longer friction lever than the drawn 0.3375: conservative), z 0.1907)
Shoe GER-001 (Onyx; repo EST allowables 20 in-layer / 9.5 interlayer / 20 bearing; epoxy 2.0; `t084_shoe.py --old` -> `shoe_t3_drawn.txt`):
| Row | x2.23 zeta 0.02 | **x2.23 zeta 0.05** | x2.23 zeta 0.10 | class |
|---|---|---|---|---|
| S2 ring + plate section under the cap (interlayer) | 1.26 | **1.12** | 0.90 | RF |
| S3 ring on the fin tube, bearing | 1.21 | **1.12** | 0.89 | RF |
| S3 ring bond shear (axial + torsion) | 1.46 | **1.30** | 1.10 | RF |
| S5 fin tube 16x14 at the shoe ring edge | 1.88 | **1.67** | 1.42 | RF |
| S3 ring bond peel | 0.12 | 0.11 | 0.09 | integrity (outside the RF minimum, T-069 F-3) |
| P1 pad PSA shear on the plate (0.10 MPa EST) | 0.15 | **0.13** | 0.11 | RF, **pre-existing** |
These are the same numbers the pre-T-084 shoe gives (identical geometry relative to the tube end). The P1 row is the pad retention problem D-215 (2) wanted a pinned cup for; T-069 showed the proposed cup also fails (0.01-0.13 at RB) and the 7.0 g cup tally is still undrawn. It is not changed by T-084 and stays open with TP-3 (drag test, pad law).
Root fitting FIN-003 (`t083b_rootblock.py`, unchanged, `rb_t084_zle005.txt`, `rb_t084_all.txt`): **min 1.21 at zeta <= 0.05** (Q3 ring at the collar root; Q2 fin tube at the ring edge 1.23), 0.89 at zeta 0.10: identical to T-083b row by row (diff empty), because the demand pad was already at z 0.19073.
Landing demand: the drawn pad is now at the demand pad's z; its x is 10 mm shorter (drawn 30 mm pad) than the analysis pad, which only shortens friction levers. The T-084 state (1.8796 kg, CG 23.13) lies between the T-083 demand (1.913 kg, 24.41) and the T-083b sensitivity (1.873 kg, 22.26, cell min 1.09): not re-simulated for the cell rows (EST interpolation). structures_a.py s5 re-simulated at 1.8796 kg: stroke 20.5 of 24 mm, tilt 2.80 deg, n 10.4 g at zeta 0.05 (PASS), 12.9 g at 0.10 (A-P5 FAIL, as T-066).

## 2. D-185 spar mode

### 2.1 The mode (FEA-lite, `t084_modes_final.py` s2, spar-only model, nom, 215.3 Hz, cx 0.02 / cy 0.52; strain energy spar 64 %, bridge 18 %, rib 10 %)
Spar nodes move chordwise (ux) antisymmetrically (+2.19 at y 0.15, -1.08 at the tip; node near y 0.33) and the whole wing slides sideways (uy -0.19) while the hub moves the other way (uy +0.31): the wing's 2nd in-plane (chordwise) bending, with the cage swaying sideways on the bridge and the V struts. The motors follow the hub (uy +0.21, uz +-0.155), hence cy 0.52.

### 2.2 Why the coupling grew 0.45 -> 0.52 (cumulative path from the iter3 inputs, nom, `modes_final.txt` s1)
| step | f Hz | cy |
|---|---|---|
| iter3 inputs | 213.5 | 0.453 |
| + rib 25x23 | 251.3 | 0.412 |
| + bridge 16x14 | 262.1 | 0.459 |
| + struts 8x6 | 269.8 | 0.420 |
| **+ strut end y 0.300 -> 0.285** | 257.9 | **0.552** |
| + hub x -0.078 | 257.1 | 0.557 |
| + wing group 212 -> 309 g | 229.9 | 0.480 |
| **+ fin-root lumps 6 -> 32 g** | 222.3 | **0.530** |
| + centre node / avionics | 222.0 | 0.549 |
| + 6061 hub, pack | 221.3 | 0.520 |
| + X2216 station | 220.9 | 0.506 |
| + feet, FIN_H 0.1937 (T-084) | 215.3 | 0.525 |
The strut end moving inboard (it then sits further from the in-plane mode's node near y 0.33, so the wing bending drives the cage harder) and the heavier fin roots (more wing-tip inertia in the same mode) are the two drivers.

### 2.3 Root cause: the wing's in-plane stiffness is missing from the FE
`fe_a.py` models the wing as the 12x10 spar alone (EI 36.9 N m2 in-plane). The drawn wing (D-226) has a foam core, 1-3 plies of +-45 glass and a cove CF strip, bonded over the full chord. With the section model the landing rows already use (`landing_path_a.py` P15 / P16; `t084_cell_props.py` -> `cell_props.txt`):
| zone | in-plane EI N m2 nominal / lower | flap EI | GJ |
|---|---|---|---|
| |y| < 0.075 (1 ply) | 5,651 / 684 | 57 / 50 | 56 / 40 |
| 0.075-0.40 (3 plies) | 6,800 / 1,649 | 90 / 73 | 156 / 109 |
| 0.40-0.45 (foam + spar) | 332 / 185 | 41 / 39 | 6.2 / 4.7 |
| spar alone (T-066 FE) | 36.9 | 36.9 | 3.16 |
Lower bound = foam E, G x0.5, skin x0.7, no strip. Even the foam alone is 5-9x the spar in-plane. **The 201-244 Hz in-band mode is therefore an artifact of the beam model; the drawn wing cannot bend chordwise at that frequency.** (The flap EI and GJ also rise, which matters in 2.4.)

### 2.4 Corrected model, three corners (`modes_final.txt` s3; same band 94-321 Hz, same >= 0.5 rule; corners scale the CF parts only)
| wing model | corner | strong modes in band (f, cx / cy) | highest strong below (margin) | lowest strong above (margin) | D-185 (a) |
|---|---|---|---|---|---|
| spar only (T-066) | kd | 201.0 (0.02 / 0.52) | 66.2 (+42 %) | 437.7 (+36 %) | FAIL |
| spar only (T-066) | nom | 215.3 (0.02 / 0.52) | 69.3 (+36 %) | 474.4 (+48 %) | FAIL |
| spar only (T-066) | hi | 244.2 (0.02 / 0.52) | 80.6 (+17 %) | 531.9 (+66 %) | FAIL |
| cell nominal | kd | none | 84.6 (+11 %) | 654.6 | PASS |
| cell nominal | nom | none | 88.0 (+7 %) | 700.5 | PASS |
| cell nominal | hi | **96.2 (0.81 / 0.93)** | 47.0 | 793.1 | **FAIL** |
| cell lower bound | kd | none | 79.4 (+18 %) | 630.1 | PASS |
| cell lower bound | nom | none | 82.7 (+14 %) | 663.6 | PASS |
| cell lower bound | hi | none | 91.4 (+3 %) | 724.3 | PASS |
In the cell models the in-plane mode is gone from the band (the 120-330 Hz mode with the largest coupling has 0.21-0.27). The governing mode is now the symmetric wing flap with the hub and pack bouncing on the bridge (hub uz +0.78, ry +11.9; spar centre uz -1.14; arms flexing: motors ux +-0.41, uy +-0.45; strain energy arm 42 %, spar 35 %, bridge 11 %). It was 66-81 Hz in the spar-only model (that is the "highest strong below" row); the stiffer wing raises it to the band's lower edge.
Pack placement (`t084_pack_place.py` -> `pack_place.txt`): the FE lumps the pack (296 g with tray, strap, pad) on the hub node; at its drawn position (x -29 mm, rigid on the hub: the tray CGE-008 is cantilevered from the hub flange) the governing mode is 94.0 / 97.9 / 106.6 Hz (nominal cell) and 88.0 / 91.8 / 100.7 (lower bound), and strongly coupled modes at 270-330 Hz (cy 0.6-0.85) appear in every wing model, including spar-only. So the beam FE's D-185 verdict changes with modelling choices it cannot settle (wing cell, pack / tray compliance, hub joint stiffness, all listed in T066_record s5).

### 2.5 Design levers on the governing mode (`modes_final.txt` s4; f of the strong mode nearest 94 Hz)
| lever | kd (nom cell) | nom | hi | hi (lower cell) | note |
|---|---|---|---|---|---|
| as drawn | 84.6 | 88.0 | 96.2 IN | 91.4 | |
| bridge 12x10 | 79.0 | 82.6 | 91.2 | 87.3 | fails the D-206 bridge torsion sizing (`bridge_torsion_d206.md`); margin only 3 % |
| bridge 20x18 | 86.9 | 90.2 | 98.2 IN | 93.2 | not in the BOM |
| struts 10x8 | 85.8 | 89.4 | 97.6 IN | 92.6 | not in the BOM |
| arms 14x12 | 93.7 | 98.1 IN | 107.7 IN | 103.1 IN | worse |
| strut end y 0.300 | 84.5 | 87.9 | 96.1 IN | 91.3 | decouples the T-066 artifact mode (cy 0.39) but costs strut Euler (EST: RF 1.06 x (0.2900 / 0.3036)^3 = 0.92 < 1, length and strut angle) and leaves this mode |
| spar 14x12 | 84.6 | 88.0 | 96.2 IN | 91.4 | no effect (the cell dominates) |
Moving the mode above 321 Hz needs about 11x the stiffness ((321 / 96.2)^2); below 94 Hz robustly needs a softer bridge (fails torsion) or more cage mass (ballast: not allowed). The rotor band edge itself (6,777 rpm hover at derate 1.0) is set by the props and motor (money).

### 2.6 Options for the design owner (D-185 stays FAIL; nothing relaxed)
| Option | What it settles | Cost | Note |
|---|---|---|---|
| A. Decide on measurement: tap / shaker test of the built airframe (T-A-TAP, already in the test plan) with the motors and pack installed; apply D-185 (a) unchanged to the measured modes and their motor coupling | the real frequencies, including hub, tray and bond compliance | $0 (G02 load cell / phone accelerometer; method "—") | rule unchanged; if a strong mode is in band, fall back to B or C |
| B. Upgrade the FE before the build: cell credited (done here, `fe_a` wing_cell), pack on a compliant tray, hub joint springs from the hub FEA, then re-judge | a defensible pre-build prediction | about 1 task (sonnet), no money | still EST until A |
| C. Design route if A / B confirm the mode in band: re-open D-206 (bridge torsion) for a bridge that is soft in z and stiff in torsion, or move the pack mass off the cage (tray carried by the wing centre node) | moves the cage-bounce mode | CAD + strength re-run; mass "—" | needs its own trade study |
| D. D-185 threshold / applicability ruling | — | — | design-owner ruling only; not proposed here |
Recommendation: A + B (no money, no mass), D-185 stays open on the ledger until the measured modes exist.

## 3. Mass, CG, window, T-W, cruise, A-P6 (geometry arithmetic + illustrative prop_a; `t084_metrics.py` -> `metrics_t084.txt`)
| State | basic g | pred kg | CG mm | SM % | trim ends mm | window % | T/W fresh / sag | cruise s | 1.3 Vs m/s |
|---|---|---|---|---|---|---|---|---|---|
| T-083b tallied (before) | 1,634.5 | 1.8734 | 22.26 | 7.52 | 21.27 / 23.92 | +12.05 | 2.641 / 2.118 | 236 | 17.53 |
| **T-084 as drawn** | 1,633.0 | 1.8717 | 21.95 | 7.65 | 20.96 / 23.61 | +12.09 | 2.643 / 2.120 | 237 | 17.52 |
| **T-084 tallied (+7.0 g shoe cups, EST)** | **1,640.0** | **1.8796** | **23.13** | **7.17** | 22.14 / 24.78 | **+11.88** | **2.632 / 2.111** | **234** | **17.56** |
Limits: A-P4 19.3..26.0 mm (trim 28.5), SM >= 5 %; A-P3 window >= +5 %; A-P2 T/W >= 2.0 / 1.6; cruise >= 204.6 s; A-P6 1.3 Vs <= 17.0 (FAIL carried, TP-11 stall test). MASS-GATE 1.50 kg: FAIL carried (+380 g; not relaxed; build_a reports it). Rib-coupon variant: 1.8530 kg, CG 20.76.

## 4. structures_a.py re-run (`structures_run.md`, exit 0; stdout `T084_data/structures_a_stdout.txt`)
Inputs changed: FIN_H 0.1937 (h_fin into the FE), M_PRED 1.8796 kg, CAD part table rebuilt (`T084_data/cad_part_table_T084.json`), new s4b (cell-credited FE).
| Row | T-066 | T-084 | Note |
|---|---|---|---|
| Static tip-over, drawn pads (centre) | 29.2 FAIL | **31.1 PASS** (edge toward CG 31.08 at this CG) | s1 |
| In-band strong mode, spar-only | 203 / 218 / 247 Hz, cy 0.52 | 201 / 215 / 244 Hz, cy 0.52 | FAIL kept, reading text replaced by the T-084 root cause |
| s4b cell-credited | — | in band only at hi, 96.2 Hz | new FAIL row (s2.4) |
| Highest strong below band | 69 / 72 / 84 Hz | 66 / 69 / 81 | longer fins |
| Lowest strong above band | 442 / 478 / 538 | 438 / 474 / 532 | longer fins |
| Sweep worst, sum of axes | 26.1 m/s2 (MS +0.15) | 26.6 (MS +0.13) | PASS |
| Landing zeta 0.05 | stroke 17.9, n 10.4, rib x2.23 1.11 | 17.9, 10.4, 1.14 | PASS |
| Landing zeta 0.10 | n 12.9 FAIL | n 12.9 FAIL | A-P5, TP-3 (carried) |
| Spar root MS | +1.99 | +1.98 | |

## 5. CAD (all changes parametric on FIN_H; no new part, no new wire)
| File | Change |
|---|---|
| `cad/amodel/common.py` | FIN_H 0.18 -> 0.1937 (with the reason) |
| `cad/amodel/wing.py` | FIN-001 mass from the drawn length 2 x FIN_H (29.2 g each, was 27.1 at a hard-coded 0.36 m); FIN-004 fairing 8.4 -> 9.04 g (scaled by height, EST) |
| `cad/a_build_steps.py` | C3 fairing 387 mm / 9.0 g; C6 tubes 387.4 mm / 29.2 g, R02 cut list (0.775 + 0.1145 m), tip-over tolerance note; C7 shoe text corrected to the CAD (Onyx 4.3 g, was "PETG 1.4 g") |
| `make_build_guide_a.py` | fin tube cut length from 2 x FIN_H |
| `BOM-A.csv` R02 | item text: 2 x 0.3874 m + bridge; price unchanged |
| `proofs/gen_params_a.py`, `proofs/claims_a0_base.py` | box packed height 0.39 -> 0.394 m; CL-A-TIPOVER input re-pointed from SIZING-A 33.2 (EST, stale) to 31.00 (SRC-A-T084, new source) |
| `structures/fe_a.py` | keyword `wing_cell` (cell beam properties) and `h_fin`; defaults unchanged (T-066 / iter3 numbers reproduce) |
| `structures/structures_a.py` | h_fin, M_PRED, part table path, s4b, reading texts |
printed_mass.json unchanged (the shoe is unchanged; the fin tubes and fairings are not printed). CAD fidelity: the fin tube is the RMRC 16x14 tube (R02) cut to 387.4 mm, modelled as the real tube; nothing invented. Exposed wire: no wire on the fins; total unchanged 0.597 strand-m (gate wire_inventory).

## 6. BOM (`python -I bom_a.py` -> `T084_data/bom_a_out.txt`)
Total **$1,999.12, margin +$0.88** (unchanged); no new material: the 1 m RMRC 16x14 tube R02 ($27.46, https://www.readymaderc.com/products/details/86475-carbon-fiber-tube-16mm-x-14mm-1m-long, read 2026-11-15 per the BOM line) still covers both fin tubes and the bridge (0.892 m used EST).

## 7. Gates (once at the end; `T084_data/run_gates_t084.sh` -> `T084_data/gates/`)
| Gate | Exit | Result |
|---|---|---|
| build_a | 1 | fails only the 1,500 g mass gate (aircraft 1,633 g; not relaxed, as T-083b) |
| wire_inventory | 0 | exposed 0.597 strand-m (unchanged), total 11.825 |
| cad_mass | 0 | basic 1.63298 kg, CG 21.95 mm |
| mission_gate --o4b | 0 | SM 7.65 % at the CAD CG |
| prop_sched --mass 1.880 | 0 | |
| bbox (t083_bbox.py) | 0 | x 490.9 mm (<= 500), y 900, z 465.2 (props) |
| collide pose 21 (static, +-21 deg) | 0 | **PASS**: 0 pairs > 0.05 mm, 0 open wire ends, 583 bodies / 129 parts |
| collide 18 linkage poses | 0 | **PASS**: 0 pairs > 0.05 mm, 0 open wire ends |
| a_assembly | 0 | **PASS**: 66 steps, 129 / 129 parts, 0 blocked paths |
| proofs run_all.py | 1 | **same 8 failing claims as T-083b** (CL-A-MASS-PRED 1.872 kg, MASS-GATE-ROOM, CUTS-REQUIRED 401.1 g, HORN-RIB-FOAM-HOLD / -STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY) + CL-A-FLUTTER-ELEVON-NOM UNVERIFIED; no new failure; CL-A-TIPOVER now reads 31.00 deg |
| drawings | 0 | 49 / 49 sheets, 36 STL |
| build guide | 0 | 66 steps |
| parts_links | 0 | 131 parts, no missing link |

## 8. Open items (not closed here)
1. **D-185 (a)**: s2.6 (blocker for this task).
2. Pad retention (P1 PSA 0.13; D-215 (2) cup undrawn, 7.0 g tally): TP-3 / drag test; not changed by T-084.
3. Pad lengthening after TP-3 must re-check A-P9 (30.22 deg at X_GROUND 0.3475).
4. A-P6, A-P5 at zeta 0.10, MASS-GATE: carried.
5. A-P15 with the larger fins: "—" (not computed; the change is in the stabilising direction).

## 9. Proposed CHANGE-LOG text (not applied)
"**D-233 T-084: A-P9 closed by longer fin tubes (T3); D-185 spar mode found to be a beam-model artifact, D-185 stays open (2026-11-22).** A-P9 root cause: the D-215 T2' pad move sat in the T-068 Phase 2 CAD, which never started because T-069 Phase 1 failed, and D-222 then gated pad CAD changes on the TP-3 drop test; analyses used an undrawn analysis pad (z 0.1907). Fix (ladder rung 2, geometry; rungs 1 / 3 rejected: shorter pad loses stroke, CG z gives 0.03 deg, CG aft fails A-P4): FIN_H 0.180 -> 0.1937 m (fin tubes 387.4 mm from the same R02 tube, +5.5 g basic), so the drawn pad centre equals the demand pad z; A-P9 edge-toward-CG 31.00-31.31 deg over drawn / tallied CG and both trim ends (was 29.2). T2' rejected: its toe needs about +27 g EST and new printed rows. No strength row changes (shoe S2 / S3 1.12, root fitting 1.21 at zeta <= 0.05; P1 pad PSA 0.13 pre-existing). Mass 1.8796 kg tallied, CG 23.13 mm, SM 7.17 %, window +11.88 %, T/W 2.632 / 2.111, cruise 234 s, A-P6 17.56 (carried); BOM $1,999.12 unchanged; box height 0.394 m. D-185: the 201-244 Hz mode is the wing's in-plane bending in an FE that gives the wing only the spar's in-plane EI (37 vs 185-6,800 N m2 drawn); coupling rose 0.45 -> 0.52 via the strut end moving inboard (0.300 -> 0.285) and the fin-root lumps (6 -> 32 g). With the D-226 cell credited that mode leaves the band, but the cage-bounce mode reaches 96.2 Hz at the hi corner (band edge 94) and the verdict depends on pack / tray and hub modelling; no lever within the BOM moves it robustly (bridge 12x10 fails D-206). Rule not relaxed; D-185 stays FAIL pending the T-A-TAP measurement and an FE with tray and hub compliance (design-owner decision)."

## 10. Files
`T084_data/`: `t084_tipover.py` + `tipover_t084.txt`; `t084_shoe.py` + `shoe_t3_drawn.txt/.json`; `rb_t084_zle005.txt/.json`, `rb_t084_all.txt/.json` (t083b_rootblock.py re-run); `t084_cell_props.py` + `cell_props.txt/.json`; `t084_modes_probe.py`, `t084_modes_sens.py` + `modes_sens.txt` (one-at-a-time, pre-T3), `t084_modes_cell.py` + `modes_cell.txt` (first cell run, whole-cell corner scaling, superseded by modes_final), `t084_modes_final.py` + `modes_final.txt`, `t084_pack_place.py` + `pack_place.txt`; `t084_metrics.py` + `metrics_t084.txt`; `structures_a_stdout.txt`; `bom_a_out.txt`; `cad_part_table_T084.json`; backups `*_pre_t084.*`; `run_gates_t084.sh`, `gates/`.
