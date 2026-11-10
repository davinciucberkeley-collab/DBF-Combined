# C4 change requests

Raised 2026-11-09 by C4 (fin / motor-tube structures). R3 and R2 numbers from `team/C4/claims.d3.json` and
`out/results_d3.json`; report `BOOM-STRUCTURES.md`. R1 numbers (CR-C4-01…13) came from `claims.json`.

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
