# Pod structures — FEA verification round

Owner C3. Revision **C3-R3**, 2026-11-10. Geometry: D2-R5a pod CAD (`subsystems/pod/fusion/pod.py` `layout()`, `subsystems/pod/params.json`), D1 wing section and spar (`params.json` A1-R4a). Masses: A3-R6a roll-up (`team/A3/rollup/mass_items.json`). Loads: C1 (`ASM-C3-POD-LOADS`, `CL-C1-CRASH-N`). Allowables: C6 (`CL-C3-ALLOW-*`). Solver: SU2 8.5.0 `ELASTICITY` on gmsh meshes.

## 1. Verdict

The FEA overturns three hand-calc passes. Each of the three has a fix. The FEA proves two of the fixes. The third (the forward stop) has no proven fix yet.

| Check (as drawn) | Hand (C3-R2/R3) | FEA (finest, 2 mm mean) | Allowable | Status | Fix |
|---|---|---|---|---|---|
| Pod-to-wing bond, design (L2 pair, MC-C) | R 0.868 | **R 1.405** (5 mm mean 1.263) | R ≤ 1 | `FAIL` | CR-C3-16 feet bonded to walls: **R 0.559** `MODELLED` |
| Bond, 12.75 g crash, worst of ±x ±z | R 0.750 (+z) | **R 11.0** (−z, re-entrant step corner, singular) | R ≤ 1 | `FAIL` | CR-C3-16 → +z 0.95, +x 0.23; −z / −x corner R 4.5 left: CR-C3-17 corner fillet, `UNVERIFIED` |
| Aft stop: board peel under the tray | not checked (shear area only, 403 N) | **408 kPa** | 50 kPa | `FAIL` | CR-C3-14 strut to the spar bridge: **1.1 kPa** `MODELLED` |
| Aft stop: 1 mm tray bending | not checked | **48.2 MPa** | 25 MPa | `FAIL` | strut: 0.03 MPa |
| Aft stop: root fillet σ1 | 16.6 MPa (root, pad lever) | **49.9 MPa** | 15 MPa | `FAIL` | strut: 0.04 MPa |
| Forward stop, −x 85 N, as built (1 mm bed to the nose wall) | 12.9 MPa (stop) | stop 4.0 MPa; **board peel 391 kPa** | 50 kPa | `FAIL` | CR-C3-15 (anchor flange through the floor), not yet modelled |
| Overhang wall-top face, crash | 8.10 MPa | 6.95 MPa | 10 MPa | +30 % `CHECKED` | — |

The allowables are C6 estimates, so every margin stays `UNVERIFIED` until `T-C3-BOND-COUPON`, `T-C3-STOP-PUSH` and `T-C3-POD-PROOF` have run. The failures are 1.4 to 8 times the allowable. A better allowable will not close them.

## 2. Models

| Model | What | Plane | Mesh levels (elements) | BCs and loads |
|---|---|---|---|---|
| BENCH | two-material cantilever 100 × 10 mm vs Timoshenko | plane stress | 4: 614 … 36 856 | clamped end, tip shear |
| M1 | pod on the wing, x–z section at y 0 (FIG C3-FEA-01) | 2.5-D plane stress: each region E × (real depth / 0.14 m) | 4: 7 553 … 415 595 (footprint), 9 271 … 513 574 (bonded) | spar bore clamped. Unit Fx, Fz, My on 5 mm floor-top segments (superposed for C1's design row). Crash ±z from the A3 items (pack at −0.024 m, most forward with block B) and ±x at the group CG |
| M1 fixes | feet bonded to walls (`TIED`, `TIED_FOOTPRINT`), + floor end released (`TIED_STEPGAP`) | as M1 | 3: ~9 300 … ~142 000 | as M1. Feet smeared as PETG over 48 of 140 mm depth (E 630 MPa) |
| M2 | pack stops, x–z through the stop | plane strain | 4: h = t/2 … t/16 at the root (537 … 69 874) | board underside held (XPS 10 mm under the aft stop). Pack load uniform from the pad top (2.5 mm) to the stop top, F = 85.5 N (aft, design) / 85 N (fwd, crash) over b = 55 mm |

Materials: XPS 20 MPa (ν 0.25), board faces 4 GPa × 0.10 mm on a 10 MPa core (homogenised 176 MPa in M1), PETG 1.8 GPa (ν 0.38), bed epoxy 3.0 GPa. All are `UNVERIFIED` (`ASM-C3-XPS-E`, `ASM-C3-PETG-E`, `ASM-C3-EPOXY-E`, `ASM-C4-*`).

Post-processing: the bond tractions are the edge tractions on the wing side. Where the pod contact is two 4.8 mm wall edges, they are scaled by 0.14 / (2 × 0.0048). Interaction R = max(σn, 0) / 100 kPa + |τ| / 100 kPa, averaged over d0 = 2 mm (`ASM-C3-FEA-D0`) and also reported over 5 mm. The stop root stress is section-linearised 3.5 mm above the tray; the peak is the maximum principal stress in the fillet. Board peel is the normal traction on the paper-face-to-core plane under the tray (C6's 50 kPa failure plane). Every load case checks equilibrium: the interface resultant equals the applied force to < 2 × 10⁻⁹. The `TIED` cases split the load between the bond and the feet by design.

## 3. Solver check (BENCH)

| Level | Elements | Tip deflection FEA / beam | Stress at x 30 mm FEA / beam |
|---|---|---|---|
| L0 | 614 | 0.946 | 0.962 |
| L3 | 36 856 | **0.997** | **0.999** |

Monotone convergence toward the beam solution confirms the SU2 set-up, the CST post-processor and the units. Section-linearised stop stresses also match the beam at the same section: aft 12.94 vs 12.96 MPa, forward 10.36 vs 10.30 MPa.

## 4. Grid convergence (finest three levels, refinement ratio 2, GCI with Fs 1.25)

| Quantity | L1 → L3 | Order p | GCI | Use |
|---|---|---|---|---|
| Bond peel σ, design (d0) | 46.9 / 47.0 / 47.1 kPa | 0.46 | 0.6 % | converged |
| Bond R, design (d0) | 1.300 / 1.357 / 1.405 | 0.29 | 19 % | finest (largest) value used |
| Bond R, design (5 mm) | 1.258 / 1.258 / 1.263 | — | < 1 % | converged reference |
| Bond R, crash −z (d0) | 9.69 / 10.35 / 11.04 | 0.07 | — | **singular corner: does not converge.** Reported as finest, decision on the trend |
| Overhang face stress, crash | 6.73 / 6.62 / 6.47 MPa | — | ± 2 % | max over levels (6.95 MPa) |
| Aft board peel, solid tray (d0) | 401 / 405 / 407 kPa | 1.46 | 0.3 % | converged |
| Aft tray bending peak | 47.0 / 47.6 / 47.9 MPa | 1.13 | 0.6 % | converged |
| Aft fillet peak σ1 | 49.9 / 49.4 / 49.7 MPa | — | ± 1 % | converged (oscillates) |
| Forward bedded board peel (d0) | 363 / 379 / 386 kPa | 1.29 | 1.5 % | converged |
| Sharp (un-filleted) stop root | 66.5 / 96.1 / 130.6 MPa | < 0 | — | singular, so the 2 mm root fillet is required |

FIG C3-FEA-03 plots each quantity against mesh level. Where a quantity does not converge, the margin uses the largest level, and Richardson extrapolation is applied only when p > 0.5 (`pod_structures.py` `_fea_summary`).

## 5. What the FEA found, against the hand calc

| Item | Hand | FEA | Why they differ |
|---|---|---|---|
| Bond peel, design | 77.9 kPa (linear, peak at the nose end) | 47 kPa | the hand calc's peel is conservative |
| Bond shear, design | 8.9 kPa (uniform Fx / A) | **140 kPa** at the recess aft step | the wing is bare XPS clamped only at the spar (x 0.080), so shear flows to the footprint end nearest the spar (shear lag). The hand calc's uniform-shear assumption is the error |
| Bond, crash −z / −x | not a peel case (bearing) | peel at the top corner of the recess step | the overhang's nose-down moment opens the re-entrant step corner |
| Wall-edge bonds aft of the recess (as drawn, E-POD-01) | left out | R 8.5 design | 2 × 4.8 mm edges over the spar take the load first and **will peel at design load**. Do not rely on them |
| Overhang | 8.10 MPa | 6.95 MPa | the hand beam is conservative by 14 % |
| Aft stop | 16.6 MPa at the root (needs 3.2 mm) | section 12.9 MPa (matches the beam); **tray and board fail** | the stop is a cantilever on a 1 mm tray glued to board. Its 1.4 N·m root moment must come out as flat-wise peel over about 25 mm of tray. 6M / (b L²) is already 239 kPa for a rigid tray |
| Forward stop | 12.9 MPa | 4.0 MPa in the stop; board peel 391 kPa | the bed hands the load to a nose wall that is free at the top in 2-D, so the wall rotates and the tray-board joint still carries the moment |

Fix studies:

| Variant | Design R | +z | −z | +x | −x | Board peel | Note |
|---|---|---|---|---|---|---|---|
| M1 as drawn, footprint | 1.405 | 1.085 | 11.0 | 0.80 | 5.46 | — | FIG C3-FEA-05 |
| M1 feet bonded to the walls (no wall-edge bonds) | **0.559** | **0.95** | 4.50 | **0.23** | 2.16 | — | feet carry 200 N (crash) |
| + floor end released from the step | 1.99 | 2.37 | **0.43** | 1.31 | **0.80** | — | moves the peak to the floor's lower corner: **rejected** |
| M2 aft + 2 mm heel | — | — | — | — | — | 196 kPa | fixes the PETG (15.6 MPa), not the peel: **rejected** |
| M2 aft + strut to the bridge | — | — | — | — | — | **1.1 kPa** | stop 0.04 MPa, tray 0.03 MPa: **adopt** (CR-C3-14) |

## 6. Limits of the models

| Limit | Effect | Direction |
|---|---|---|
| 2.5-D: the wing XPS beside the pod (outboard of y ±0.07) and the packing-tape skin are left out | less load-spreading area to the spar | conservative |
| Linear elastic: XPS crushes and the bond line yields at corners | real corner peaks redistribute | conservative at singular corners; decided by test |
| M2 plane strain: the nose wall is free at the top, and the side walls and hatch are left out | the forward nose wall gets no help from them | conservative for the forward stop |
| Feet smeared over the model depth; the strut prop is rigid | idealised fixes | the brackets and strut are sized by hand (`CALC-C3-STRUT`, `CL-C3-FEA-SADDLE-*`) |
| d0 = 2 mm averaging | sets the corner values | the 5 mm values are shown too. Every failure above still fails at 5 mm |

## 7. Re-run

| Step | Command | Time |
|---|---|---|
| All FEA parts (they can run in parallel) | `python -I redesign/team/C3/pod_fea.py --part bench` (and `m1f m1b m2 m2x m1t m1tf m1tg`) | ≈ 1.2 h total, single-thread SU2 |
| Merge and draw the figures | `python -I redesign/team/C3/pod_fea.py --combine` | 5 s |
| Claims | `python -I redesign/team/C3/pod_structures.py`, then `python -I redesign/proofs/build_graph.py` | < 1 min |

Each run keeps its `case.cfg`, `log.txt` and `summary.json` under `fea/runs/`. Results are in `fea/fea_results.json`. Figures (SVG, design-system diagram style) are in `fea/`:

- `FIG C3-FEA-01`: M1 section, regions and boundary conditions.
- `FIG C3-FEA-02`: bond peel along the footprint, FEA against the hand calc.
- `FIG C3-FEA-03`: convergence of each reported quantity.
- `FIG C3-FEA-04`: stop variants as ratios to their allowables.
- `FIG C3-FEA-05`: bond interaction per variant and load case.

Proof build: no C3 errors. C6's `CALC-C6-POD-ALLOW` drifts on the new hand values (CR-C3-11).

## 8. C3-R4 (2026-11-13): the D-69 drawings checked, CR-H1-23 answered

Load: pack crash load on the forward stop `CALC-C3-STOPS` `F_fwd_n` 73.75 N over the bay + guides (55 mm); pod crash
12.75 g (`CL-C1-CRASH-N`). Allowables from C6 nodes (board flat-wise 50 kPa, paper / core shear 100 kPa, XPS 100 / 100
kPa, PETG 15 MPa, epoxy flat-wise `ASM-C6-PEEL` 1.0 MPa). Values: finest level, or the Richardson value when larger
(`_fea_summary` rule). Parts: `fea/parts/m2f.json`, `m1tfl*.json`, `m1tf.json`; runs under `fea/runs/M2F/`,
`M1-TIED-FP-FILLET*/`.

### 8.1 Forward-stop T (D-69, D2-R6), new model M2F
Plane strain at y 0 through the T: upright 3 mm from the flange foot to 25 mm above the tray, flange 12 × 1.2 mm under
the floor (`pod.py layout()` `fs_flange`), upright epoxied to the floor end (BUILD step 6), tray front piece not
credited at the upright (0.2 mm gap). Two floor bounds: HELD (underside held aft of the flange, the C3 M2 rule) and BOX
(floor strip clamped 60 mm aft, underside free). Four levels, h = t/2 … t/16 at the T.

| Quantity (2 mm mean) | No bed, HELD | No bed, BOX | **With the 1 mm bed (BUILD step 9), HELD** | With bed, BOX | Allowable |
|---|---|---|---|---|---|
| Board flat-wise peel | **76.5 kPa** (tray / upright notch) | 197 kPa (tray window edge, 30 mm aft) | **42.8 kPa** (+14 %, GCI 1.2 %) | 59.6 kPa at the window edge; 2.8 kPa at the T | 50 kPa |
| Core shear under the faces | 142 kPa | 99 kPa | **94.8 kPa** (+5 %, GCI 1.3 %) | 59 kPa | 100 kPa |
| Upright, section-linearised | 13.3 MPa | 13.4 MPa | **3.7 MPa** (+75 %) | 3.2 MPa | 15 MPa |
| Flange at the upright | 3.0 MPa | 3.2 MPa | **7.1 MPa** (+53 %) | 3.3 MPa | 15 MPa |
| Nose-wall core shear / face peel | — | — | 70 kPa / 0.3 kPa | 94 kPa / 0.3 kPa | 100 / 50 kPa |
| Tension across the bed | — | — | 278 kPa | 274 kPa | 1.0 MPa |

Verdict: **the T as drawn passes only with the bed.** The bed carries the root moment into the nose wall; without it
the floor's top face peels at the tray / upright notch (76.5 kPa, +53 % over). BUILD step 9 is a structural hold
point, not a filler. The BOX bound's window-edge peel (59.6 kPa) needs the floor strip to bend alone 30 mm aft of the
T; the nose box (walls, bed, hatch lip) does not let it, so the claims use HELD, as every C3 M2 claim does. A studied
fix (tray epoxied to the upright + 2 mm fillet, no bed) did not help (peel 84 kPa): not adopted. Claims
`CL-C3-FEA-FWD-T-*`; the pre-D-69 forward-stop claims are kept as records without limits.

### 8.2 Recess-step fillet (CR-C3-17, WNG-007 as drawn), M1 with the feet tied, wall edges not credited
The fillet (wing.py `rf_legs` 5 × 4.8 mm, microballoon epoxy 3 GPa) and the floor's 45° bevel on it were added to M1
(three levels). Results (finest, 2 mm mean unless noted):

| Case | Square end, no fillet (`M1_TIED_FOOTPRINT`, re-run 2026-11-13 on today's A3 / C1 inputs; C3-R3 read 0.56 / 4.50 / 2.17) | **Fillet as drawn** | Fillet, soft 1 GPa | Scarf 15 mm |
|---|---|---|---|---|
| Design, wing-side bond R | 0.60 (5 mm 0.53) | 0.58 (5 mm 0.55) | 0.61 | 0.54 |
| Crash −z, at the step **top** (x 0.065, z 0.0197) | 4.42 (5 mm 3.27) | **4.43** (5 mm 3.28 → 3.56 extrapolated) | 4.42 | 4.65 |
| Crash −x | 1.91 | 1.86 | 1.87 | 1.94 |
| Crash +z / +x | 0.94 (0.95 extrapolated) / 0.20 | 1.00 / 0.19 | 0.97 / 0.20 | 1.06 / 0.24 |
| Floor bevel on the fillet, design, mean over the face (core foam allowables) | — (butt in bearing) | **1.20** | 1.19 | 0.76 (5 mm 1.17) |

Findings: (1) the crash peak is at the **top** of the step, where the bond line ends, not at the bottom corner the
fillet fills; the fillet does not lower it (4.42 → 4.43) and its 5 mm mean converges to about 3.6, so it is a real
local peel, not only a singularity. (2) The 45° bevel turns the floor end's bearing on the step into shear on the
bond: the floor-to-fillet joint fails in flight (mean R 1.20 over the whole face); a 15 mm scarf halves it on average
but keeps a 1.17 peak and worsens crash +z. (3) A PETG chord from the aft stop to the foot bridge (studied) lowers
crash −z to 0.95 but raises the design R to 1.27: not adopted.

Decision: **delete WNG-007 and the floor bevel; the floor end stays square on the step (the R3 joint)**: design 0.60
(`CL-C3-FEA-STEP-R-DESIGN`, +40 %); the square end bears on the step in compression, and the floor-side bond sees the
same tractions as the wing side, checked on the same foam allowables. Crash retention by fail-safe
(`CL-C3-FEA-CRASH-FAILSAFE` 0.95): −z and −x peel the aft bond end locally; the released aft end then holds
(`M1_TIED_STEPGAP` −z 0.43, −x 0.87 with Richardson); +z 0.95 and +x 0.23 hold intact. Post-crash: inspect the aft bond
line before the next flight.

### 8.3 Handle-bracket proof load (CR-H1-23)
From `M1_TIED_FOOTPRINT` (re-run 2026-11-13 with the saddle force combined per case): bracket force at the design row
164.3 / 110.8 N (x / z) → **limit** = design / (1.5 × 1.15 × 1.25) = **76.2 N +x, 51.4 N −z, 91.9 N resultant**
(`CL-C3-BRACKET-PROOF-LIMIT*`); crash worst **204.7 N** (`CL-C3-BRACKET-CRASH-F`). The 200 N pull is the crash force
(ultimate, no factor): it does not go on the flight pod. Flight pod: T-C3-POD-PROOF at the limit components. Crash
force: new `T-C3-BRACKET-CRASH` on two test articles (foot + bracket on a wall offcut and a spar stub).

Re-run: `python -I redesign/team/C3/pod_fea.py --part m2f` (≈ 15 min), `--part m1tf`, `--part m1tfl` (≈ 7 min each;
studies `m1tfl1`, `m1tflh`, `m1tfl10`, `m1tfl15`), then `--combine` and `pod_structures.py`.
