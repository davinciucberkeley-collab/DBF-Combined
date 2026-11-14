# C4 change requests

Raised 2026-11-09 by C4 (fin / motor-tube structures). R3 and R2 numbers from `team/C4/claims.d3.json` and
`out/results_d3.json`; report `BOOM-STRUCTURES.md`. R1 numbers (CR-C4-01…13) came from `claims.json`.

## S1 simulation round (2026-11-10: 3-D solid FE, `SIMULATION-REPORT.md`, `claims.sim.json`)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C4-36 | **D5**, H1 (cc D3, A1, A3) | **Hold CR-C4-30.** Build the `T-C4-FIN-PROOF` test article with the D5 shoe **as drawn** (legs 7 mm, 8 mm collar cheeks over both strip ends, cheeks bonded to both strips). Pass at 1.5 × L4 both senses: D5 keeps the drawn shoe and saves the ≈ 16 g `EST` CR-C4-30 would add. Fail: fit the extended cheeks (to \|z\| 0.171 m) on the flight shoes | 3-D FE does not reproduce the R4 tip `FAIL`: the strip pair, clamped in the cheeks, carries 53 % of the side-load moment that the shell put through the bare board | `CL-C4-SIM-MS-FACE-DRAWN` +0.11 (bound; +0.03 with the global-mesh check) vs R4 `CL-C4-D3-MS-FACE` −0.54; extended cheeks `CL-C4-SIM-MS-FACE-PROP` +1.70; `CL-C4-SIM-BOARD-SHARE` 0.47 vs shell 1.06 |
| CR-C4-37 | **D3** (cc C6, I1) | Make the **strip-tail bond in the station-collar tail a build inspection item** in `BUILD.md`: strips run to the tube surface, epoxy fills both slots over the full 40 mm, tongue printed with its 3 perimeters under each strip (no voids). Add a tap/pull check per tail before the fin is closed | With the tongue unbonded (foam-like) the face at the LE tail corner reaches 8.07 MPa limit (MS −0.17 ult); at ≥ 0.2 GPa it is 4.7 MPa (MS +0.43). The tail also halves the foot deflection | `sim/out/sens_tail.json`; `ASM-C4-SIM-TAIL-E` 1 GPa |
| CR-C4-38 | H1 (I1) | On the `T-C4-FIN-PROOF` article add two strain gauges: paper face 5 mm below the leg edge at x ≈ 0.30 m, and one strip 10 mm forward of the collar cheek; dial gauge at the pad. Predictions at 1.0 × L4 (limit): face ≈ 3.4–4.3 MPa (≈ 0.9–1.1 × 10⁻³ strain at 4 GPa), strip ≈ 88 MPa (≈ 0.8 × 10⁻³ at 110 GPa), pad 3.7 mm (shell said 9.3 mm). Tap the board centre in `T-C4-TAP-D3` (panel mode 71–73 Hz predicted) | Measured strain split decides between the shell and 3-D load paths | `CL-C4-SIM-FOOT-DEFL`, `CL-C4-SIM-MS-STRIP`, `CL-C4-SIM-F1-UP`, `-F1-LO` |
| CR-C4-39 | A1, A2 | `R-VIBRATION` margin fell: separation **0.29** (3-D, lower station 255.5 Hz vs 2P cruise 198.2 Hz at the new 5 946 rpm, A3 motor 84.2 g). Still ≥ 0.20. Any further cruise-rpm rise above ≈ 6 390 rpm or station mass growth > ≈ 15 % needs a C4 re-run | Inputs moved: `CL-B4-CRUISE-RPM` 5 894 → 5 946, motor 81 → 84.2 g | `CL-C4-SIM-SEP` 0.289; shell with the same inputs 0.335 |
| CR-C4-40 | A1 (proofs) | SU2 v8 in this install has **no direct solver** (`PASTIX_*` → "not compiled with -DHAVE_PASTIX") and its CG/ILU and FGMRES/ILU do not converge on laminated foam-board solids (log₁₀ residual +0.15 after 6 000 iterations; FGMRES orthogonalization failure). C4 uses its hex8 code (SU2's element to 4.7 × 10⁻¹¹ on the benchmark) with SciPy SuperLU. Other structures roles: expect the same; a PaStiX build of SU2 would let the quarter run in SU2 | Tooling note for `inputs/SIM-TOOLS.md` | `CALC-C4-SIM-CODES`, `CL-C4-SIM-BENCH-CODES` |
| CR-C4-41 | **H1**, D3 (cc I1) | Raise the `T-C4-MOUNT-STIFF` pass level from 1 000 to **≥ 1 100 N·m/rad** (both rocking axes) and re-run `ground_tests.py` | R4 re-run on today's cruise rpm (5 946): rocking stiffness needed for 0.20 separation rose to **1 030 N·m/rad**, above the old pass level. Estimate is 3 000 | `CL-C4-D3-MOUNT-K-REQ` 1 030 (was 971) |

Status of R4 requests after S1: CR-C4-30 held by CR-C4-36 (decided by test). CR-C4-33 amended by CR-C4-36/38 (test
article as drawn, gauges). CR-C4-34: fins re-run at **434.8 g** vs 418 g (−16.8 g). Others unchanged.

## R4 (2026-11-10: D3-R4 fin with the D5 tip step, 12 mm collar, C1 corner 32.6 N × μ 0.7, B4 swirl, G3)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C4-30 | **D5** (cc D3, C6, H1) | **Extend both shoe cheeks toward the wing to a lower edge at \|z\| ≤ 0.171 m** (25 mm deeper than drawn; x 0.2666–0.320 m unchanged), bonded to both board faces over the full strip band. Then set `ASM-C4-SHOE-Z0` to the drawn value (C4 re-runs). C6: check the cheek-to-paper bond and peel at the new cheek edge | The strips stop at the step front, so the 45 mm square tip is bare board. The 22.8 N side load at the pad bends it below the cheek edge: face MS **−0.54** (21.8 MPa ult vs 10 MPa) | `CL-C4-D3-MS-FACE` −0.54 → `-MS-FACE-SHOE-INTACT` +0.18, `-MS-FACE-SHOE-FS` +0.01 (limit); `CL-C4-D3-SHOE-EXT` 0.025 m; sweep in `out/results_d3.json` `shoe_sweep`. Mass ≈ +4 g per foot at 1.2 mm PETG walls (+16 g for four) `EST` |
| CR-C4-29 | C1 | Publish the G3 set-down force on a lower can as a claim (`CL-C1-G3-CAN-F`); C4 reads it today as `ASM-C4-G3-CAN-F` 23.2 N | One source for the number | G3 never governs: cap MS +38.6, brace 0.61 N, rocking 1.45 N·m design |
| CR-C4-31 | B1, D3 | CR-B1-18: **no new brace section.** Keep the flat CF 10 × 2 and wrap it in clear packing tape as a fairing (1.4 g for four). Sanding both edges round cuts the weak-axis I by 8 % (MS +0.79 → +0.65) and changes the station stiffness, so C4 does not accept it. B1 credits drag only for what the tape wrap gives | Stiffness of the 10 × 2 unchanged | `CL-C4-D3-BRACE-ROUND-I` 0.918, `-BRACE-ROUND-MS` +0.65, `-BRACE-TAPE-MASS` 1.43 g |
| CR-C4-32 | C6 | Re-run `joints.py` on the R4 claims: collar torque **6.24 N·m** limit (`CL-C4-D3-COLLAR-T`, published for you; was 4.61), brace 163 N design, strip end **1 243 N**/face design (was 908), pin **72.4 N** design (was 64), strip q 2 240 N/m. C4's collar bond at 12 mm: MS +0.16 (needs 10.3 mm) | Loads rose with the 32.6 N corner and μ 0.7 | `CL-C4-D3-COLLAR-T`, `-BRACE-F`, `-STRIP-END-F`, `-STRIP-PIN-F`, `-STRIP-Q`, `-COLLAR-H-REQ` |
| CR-C4-33 | H1 (I1) | `T-C4-FIN-PROOF` is now on a **test article** (CR-H1-17 accepted): lower quarter, D5 shoe with the extended cheeks, LE fillet unbonded. Loads 1.5 × limit: L4 **49 N along + 34 N across** both senses, G2 77 N both senses, G3 35 N, 30 s each; then L4 to failure. Flight fins: 1.0 × L4 hand check only | Fail-safe face margin +0.01 rests on a corner that does not converge with mesh; the test decides | procedure in `claims.d3.json` |
| CR-C4-34 | A1, A3 | Fins **436.4 g** vs 418 g allocated (−18.4 g). No structural item can be removed (each of brace, strips, second layer drops separation to ≤ 0.09); the collar is already 12 mm. CR-C4-30 adds ≈ 16 g `EST` to landing (D5) | Allocation decision | `CL-C4-D3-FINS-MASS` |
| CR-C4-35 | D3 | Point the SPEC at R4: `CL-C4-D3-MS-FACE` now `FAIL` as drawn (cleared by CR-C4-30); `CL-C4-D3-SEP` 0.37; `-MOUNT-K-REQ` 971 N·m/rad (bench pass level stays ≥ 1 000); `-COLLAR-H-REQ` 10.3 mm (12 mm passes, MS +0.16) | One answer per question | `claims.d3.json` |

Incoming items closed in R4: CR-C1-21 (μ 0.7 on `CL-C1-FOOT-CORNER`, collar torque published as `CL-C4-D3-COLLAR-T`,
wing-plane torsion agrees with C1 within 0.08 %), CR-C1-24 (G3 case added), CR-B4-19 (swirl 1.43 N misbuilt scaled to
T_lim, Campbell at 5 416 / 5 894 rpm), CR-C6-20 (no NaN; 0 C4 calculation errors in `build_graph.py`), CR-A4-47 (ids
renamed in both scripts), CR-B1-18 (answered by CR-C4-31), CR-H1-17 (CR-C4-33). R3 items: CR-C4-23 superseded by
CR-C4-32; CR-C4-27 by CR-C4-33; CR-C4-28 by CR-C4-34; CR-C4-25 done by D3 (12 mm collar, pins, 40 mm tail).

## R3 (params A1-R3, D3 R3 fin, 7° cant, μ 0.7)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C4-23 | C6 | Re-run `joints.py` on C4's R3 claims. (a) Collar: replace `ASM-C6-C4-COLLAR-T` 9.3 N·m (not a C4 output) with **max(C1 `J-FINHALF` Mz, `CL-C4-D3-COLLAR-T`) + `CL-C4-D3-BRACE-F`** as shear. (b) Strip tail: size to `CL-C4-D3-STRIP-END-F` **908 N** design per face, not 1 348 N. (c) Pins: `CL-C4-D3-STRIP-PIN-F` **64 N** design per pin. (d) Brace force is now 164 N (10 × 2). This closes CR-C6-02a and CR-C6-03 on C4's side | One torsion number for the collar; FE loads replace the hand estimates | Collar 4.61 N·m limit (cracked LE, worst), 4.52 intact; C1 5.29. Bond needs 8.0 / 9.0 mm: **12 mm passes both** (MS +0.49 / +0.33), 16 mm +0.99 / +0.78. Paper bare MS −0.77 (0.43 vs 0.10 MPa design): pins stay |
| CR-C4-24 | C1 | Publish the half-fin torsion about the tube as a claim (C6 reads it today through `ASM-C6-FINHALF-MZ-ULT`) and re-issue it with the μ 0.7 side load (CR-C5-09). C4's FE gives less (4.61 vs 5.29 N·m) because the root fillet on the skin takes part. C4 proposes that C6 sizes to the larger of the two | Agree the collar torsion (CR-C6-03) | `CL-C4-D3-COLLAR-T` 4.61, `CL-C4-D3-TUBE-T-ROOT` 4.63 N·m limit, side load 20.4 N |
| CR-C4-25 | D3 | Keep the Ø 2 mm strip pins at ≤ 15 mm and the 40 mm two-face tail: both are **required**. The 10 × 2 brace is confirmed (CR-C4-16 closed). The station collar needs only 9 mm of bond for torsion: if the strip-tail tongue fits in 12 mm, go back to 12 mm (≈ 3 g `EST` toward CR-D3-16). Set the `T-C4-MOUNT-STIFF` pass level to **≥ 1 000 N·m/rad** | Strip couple shear crosses the board; mass is over by 8.8 g | `CL-C4-D3-MS-STRIP-PAPER` −0.77, `-STRIP-PIN-F` 64 N, `-COLLAR-H-REQ` 8.0 mm, `-MOUNT-K-REQ` 905 N·m/rad, `-BRACE-10X2-MS` +0.82, `-BRACE-10X2-SEP` 0.39 |
| CR-C4-26 | D3, C2 | Stop reading the R1 concept model: D3 `CALC-D3-BRACE` reads `CL-C4-STRUT-LEN` → use `CALC-C4-D3-STATIC` `brace_len_m` (0.155 m) or its own CAD; C2 `wing_struct.py` reads `CL-C4-SPAR-COUPLE` → `CL-C4-D3-SPAR-COUPLE` (same 961 N). C4 then retires `fin_structures.py` | R1 no longer matches the geometry (fin top above the tube end); its claims drift with every upstream change | — |
| CR-C4-27 | H1 (I1) | `T-C4-FIN-PROOF` at R3 loads: 1.5 × L4 with the 20.4 N side load (μ 0.7) both senses, 1.5 × G2 both senses; pins fitted; one quarter built with the LE fillet left unbonded (the fail-safe case); witness lines on the collar and on the strip ends; dial gauge at the foot (6.8 mm limit) | Face MS is +0.10 with the fillet cracked; the strips carry 92 % of the side load | `CL-C4-D3-MS-FACE`, `-FOOT-DEFL` |
| CR-C4-28 | A1, A3 | Fins are 416.8 g against 408 g (D3 CR-D3-16). Structures need every R3 item (2 layers, strips + pins, 40 mm tail, brace); the only C4 lever is the collar 16 → 12 mm (≈ 3 g `EST`). A 10 × 3 brace is **not** needed | Allocation decision | `CL-C4-D3-FINS-MASS` 416.8 g, `-BRACE-SAVE` 9.3 g already taken |

Status of R2 requests after R3: CR-C4-14 accepted (D-26). CR-C4-15 closed (allocation 408 g, D-38). CR-C4-16 closed
(D3 drew 10 × 2). CR-C4-17 kept, with the pass level raised to 1 000 N·m/rad (CR-C4-25). CR-C4-18 forwarded to D1/C2
by A1. CR-C4-19 open (D3's SPEC to point at the R3 claims listed in `BOOM-STRUCTURES.md`). CR-C4-20 accepted (D-26). CR-C4-21 open. CR-C4-22
delivered by C6 and superseded by CR-C4-23.

## R2 (after D3's as-designed fin, CR-D3-10)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C4-14 | A1, D3 (A3, D5) | **Reject CR-D3-02 (one board layer). Keep `fins.layers` = 2** with the brace and the edge strips. D3 sets `fin_detail.layers` back to 2 and laminates the two boards with spray adhesive | On D3's geometry the one-layer fin's first station mode is 228 Hz, 14 % from 2P cruise. Shortening the tube (CR-D3-01) put the motor 30 mm above the fin top; the board carries the motor twist | `CL-C4-D3-SEP-1L` 0.14 `FAIL` → `CL-C4-D3-SEP` 0.41 (worst E/G 0.33, whirl 0.40). Brace or strips removed: 0.01 / 0.02 |
| CR-C4-15 | A1, A3 | Carry the fins at **402 g** (D3 CAD 364.5 g + second layer 37.5 g) against the 370 g allocation: raise the allocation or release 32 g from the reserve. Optional −10 g `EST` with CR-C4-16 | `R-MASS-ALLOC`; A3 CR-A3-12 already shows fins at zero margin | `CL-C4-D3-FINS-MASS` 402 g (−9 %), `CL-C4-D3-LAYER-ADD` 37.5 g |
| CR-C4-16 | D3 | Accept the brace geometry as drawn (ear 17.8 mm inboard at z 0.1535, anchor y ±0.242, L 145 / 157 mm). **10 × 2 strip is enough** if mass is needed (P_cr 293 N vs 166 N design, separation 0.39); 10 × 3 is fine as drawn (+4.9) | The brace stores 2–6 % of the modal strain energy: its stiffness hardly matters, its presence does | `CL-C4-D3-MS-BRACE`, `results_d3.json` "2 layers, brace 10 x 2" |
| CR-C4-17 | D3 | Mount: rocking stiffness ≥ **900 N·m/rad** about x and y (tube end to motor base). Keep the 12 mm grip, 2 mm collar wall and the lip cap; do not thin them to save mass. Anchor saddle stays ≥ 20 × 16 mm; collar 12 mm tall; brace ends ≥ 10 mm bonded | At 500 N·m/rad the separation drops to 0.07; the anchor bond is the tightest joint | `CL-C4-D3-MOUNT-K-REQ` 894 (estimate 3 000); `CL-C4-D3-MS-ANCHOR` +0.33, `-COLLAR` +0.87, `-BRACE-END` +1.50 |
| CR-C4-18 | C2 (D1) | Spar loads at each fin: block couple **961 N** design across the 36 mm bore at y ±0.32 (plug, CR-C4-02); brace anchor **166 N** design along the brace at y ±0.242, upper and lower, pull or push (G2). Check the spar and the 20 × 16 mm skin/core pocket under the anchor, and the wing modes with four 125 g stations | New load point on the spar; the brace anchor is modelled rigid apart from 3e7 N/m | `CL-C4-D3-SPAR-COUPLE`, `CL-C4-D3-BRACE-F`, `ASM-C4-ANCHOR-K` |
| CR-C4-19 | D3 | Point the SPEC at the R2 claims: `CL-C4-D3-SEP`, `-SEP-WORST`, `-F1-LO`, `-MS-FACE`, `-BLOCK-MS`, `-MOUNT-K-REQ` (R1's `CL-C4-SEP-1LB`, `-F1-1LB`, `-MS-FACE-1L` are superseded). Keep reading `CL-C4-STRUT-LEN` in `CALC-D3-BRACE` if useful; it no longer verifies anything | One answer per question | `claims.d3.json` |
| CR-C4-20 | B3 (D3, D5) | Structures accept `fins.half_height_m` 0.21 (CR-B3-14) with two layers | Separation 0.38 (lower) | `results_d3.json` "half height 0.21 m" |
| CR-C4-21 | H1 (I1) | Add `T-C4-MOUNT-STIFF` (mount on a tube stub, 0.5 kg at the prop nut, two dial gauges) and run `T-C4-TAP-D3` on the finished wing (each bell in y and z). Tube tests as CR-C4-03 by 10 Dec (CR-I1-08) | Mount and root stiffness are estimates; every frequency claim is `UNVERIFIED` until tapped | `claims.d3.json` tests |
| CR-C4-22 | C6 | Joint stacks for: station collar on the tube (3.5 N·m limit torque + 166 N design brace shear, bond 1.07 MPa design), brace ends in printed slots (0.80 MPa), anchor on the spar in pull-off (0.75 MPa; C4 uses a 0.5 peel factor). Supersedes the numbers in CR-C4-10 | `ASM-C4-BOND-SHEAR` 2 MPa and `ASM-C4-PEEL-KD` 0.5 are guesses | `CALC-C4-D3-STATIC` |

## R1 (status after R2)

| Id | To | What (short) | Status |
|---|---|---|---|
| CR-C4-01 | A1, D3 | Braced fin with edge strips, one layer | Brace and strips: done by D3. **One layer withdrawn by CR-C4-14** |
| CR-C4-02 | C2, D1 | Spar plug at each block, 961 N couple; brace anchor check | Open; numbers updated in CR-C4-18 |
| CR-C4-03 | I1, H1 | Buy the US-stock 22 × 20 tube, run bend and torsion tests | Open (CR-I1-08: result by 10 Dec) |
| CR-C4-04 | D3 | Block 69 × 36 mm, bosses, plug, collar ear | Done by D3 (block MS +0.55 on D3 geometry) |
| CR-C4-05 | A3 | Fins +66.8 g | Superseded by CR-C4-15 (402 g total) |
| CR-C4-06 | A2, B4 | `R-VIBRATION` (operating points) as criterion of record | Open; band rule still −0.15 |
| CR-C4-07 | F4 | rpm-tracking harmonic notch as backup | Open |
| CR-C4-08 | B1, B4 | Brace drag 0.07–0.24 N | Open (D3 CR-D3-15 adds collars) |
| CR-C4-09 | C5, D5 | Foot cap wraps the edge-strip ends | Open (board now 9.6 mm + strips) |
| CR-C4-10 | C6 | Joint stacks | Superseded by CR-C4-22 |
| CR-C4-11 | H1 | Coupon, tap, proof tests | Open; adds CR-C4-21 |
| CR-C4-12 | J1 | Supersede `CL-J1-TUBE-MODE-SEP` | Now by `CL-C4-D3-SEP` |
| CR-C4-13 | C1 | Confirm L4 side load | Open |
