# Loads — K09-L quad tailsitter

Owner: C1 (loads engineer). Revision **C1-R5** (D-65 action items), 2026-11-10, at params revision **A1-R5**
(landing_n_design **6.6**, CG range 0.0466–0.0514 m with the CG **18.5 mm** above the chord plane, pod nose −0.140 m,
pack datum −0.032 m, allocations 2 386 g, VD 27.2 m/s, n⁺ 3.4, T_lim 21.1 N, 7° cant) and **A3-R7** (`CL-A3-GROUPS`,
`CL-A3-IYY` 0.0461 kg·m², basic 2.342 kg). Requests CR-C1-35…39 in `CHANGE-REQUESTS.md`. Status: the calculation is
`CHECKED` (equilibrium, convergence, two hand checks); its inputs are `PROPOSED`/`UNVERIFIED` (thrust, CLmax, masses,
capped VH, C5's simulated side load), so every load is `UNVERIFIED` until the stand, the level-speed log, the scale,
the swing, the foot drop and the proof test replace them.
Re-run in ~10 s: `python -I redesign/team/C1/loads.py`, then `python -I redesign/proofs/build_graph.py`.

Every number is a **limit** load (largest expected in service) unless labelled ultimate; ultimate = 1.5 × limit.
Frame: x aft, y right, z up in cruise (`params.json#frame`); in hover +x points at the ground.

## What changed in R5

| Item | R4 | R5 | Why |
|---|---|---|---|
| Landing design factor | n_L 6.0 | **6.6** (`P:requirements.landing_n_design`, read live) | D-65 / CR-C5-19 |
| Foot side load in L4/L5 | μ 0.7 × corner load (22.9 N) | **max(μ × corner, C5 sim) = 39.30 N** limit, 58.96 ult (`CL-C1-FOOT-SIDE-DESIGN(-ULT)` ← `CL-C5-SIM3D-SIDE-LOAD`) | D-65 / CR-C5-16 |
| CG | x on the limits 0.050 / 0.0549, z free (~0.02) | x on **0.0466 / 0.0514** (MC-C / MC-P), **z trimmed to 0.0185** (`P:cg.z_target_m`, `CL-C1-CG-TRIM-DZ`) | D-62 |
| Centre group, pack, harness | lumps at pod-geometry points; pack at `CL-A3-PACK-X-REQ` | at **A3's group centroids** (`CL-A3-GROUPS`); centre group split at ± its A3 radius of gyration (65.7 mm) + Iyy shortfall; harness as A3's two side runs at y ±0.256 | CR-C1-33 answered by A3-R7 |
| CG trim of the lumped model | 28.7 mm | **7.2 mm** (`CL-C1-CG-TRIM-DX`) | A3 groups |
| New claims | — | `CL-C1-G3-CAN-F(-ULT)`, `-PACK-STOP-LIM/-ULT`, `-POD-F-LIM`, `-FOOT-SIDE-DESIGN(-ULT)`, `-TRANSPORT-N-ALLOW-NOSE`, `-CG-TRIM-DZ` | CR-C4-29, D-65, CR-D7-24 |
| Transport | X1–X5 | **+ X6 nose wall with the pod nose on the nose pad** (reacted at the pod, not the cradles) | CR-D7-24 |
| Sensitivity | VD only | + `data/sensitivity_side.json` (39.3 / 29.1 N / friction-only) | CR-C1-36 |

## Action items (D-65) — resolution

| Item | Result | Status |
|---|---|---|
| Re-run at landing_n_design 6.6 | read live; L1 upper foot **44.41 N** (40.38), corner 36.68 N; L1-driven loads +7–10 % (spar root Mb ult 20.65 N·m, fin-joint force ult 89.15 N) | `CHECKED` |
| 39.3 / 59.0 N foot side load | applied with the corner load in L4 (y) and L5 (z); fin-joint moment ult **22.46 N·m** (14.34), half-fin torsion at the wing plane **12.63 N·m** limit (7.37), half-fin bending ult **16.33 N·m** (11.41) | `CHECKED` (input `MODELLED` by C5) |
| D-62 CG (0.0490, z 0.0185) | MC-C at 0.0466, MC-P at 0.0514 (bracket the 0.0490 target), both at z 0.0185 | `CHECKED` |
| A3-R7 inertia and group centroids | Iyy 0.90–0.99, Ixx 0.99–1.00, Izz 0.99–1.02 of A3 (`CL-C1-INERTIA-RATIO-MIN/-MAX`); trim 7.2 mm; residual offset = C1's fin lumps 27 mm forward and feet 26 mm aft of A3's (`data/checks.json`) | `CHECKED` |
| Publish `CL-C1-G3-CAN-F` | **23.46 N** limit / 35.19 N ult per lower can (G3, 2 g) | `CHECKED` |
| GT-08 pad table and step 2 to H1 | CR-C1-39 (table below) | `PROPOSED` (H1) |
| D7 aft-wall n 9.22 | allowable now **10.76** (J-FIN force); 9.22 stays a safe lower bound; demand 7.79 | `CHECKED` (+28 %) |
| D7 0.059 m nose drop | **not confirmed**: pod-nose-reacted allowable n **4.98** → 0.021 m (3/4 in pad) / 0.014 m (1/2 in) (CR-C1-38) | `FAIL` vs 0.059 m (label-and-test case, D-53) |
| Fin roots, spar saddles, pack stop at n 6.6 | fin roots: large rise, C4/C6 margins estimated negative (CR-C1-35); pod saddle 75.8 N limit (−3 %); pack stop 42.5 N limit, design 91.6 N > crash 73.75 N (CR-C1-37) | `CHECKED` (loads); capacity checks are C4/C6/C3's |

## Basis

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design mass | 2.600 (gate) | kg | `P:requirements.mtow_gate_kg` | `PROPOSED` |
| Mass configurations | MC-C: gap to the gate in the pod, CG on the forward limit; MC-P: every item × gate/sum, CG on the aft limit | — | `data/mass_model.csv` | `PROPOSED` |
| CG range / height | 0.0466 / 0.0514; z 0.0185 | m | `P:cg.x_range_m`, `P:cg.z_target_m` | `UNVERIFIED` |
| Inertia | centre group at ± A3 radius of gyration + Iyy shortfall (spread 0.1175 m, pod half-length cap); Iyy 0.90–0.99 of `CL-A3-IYY` | kg·m² | `CALC-C1-MASS-XCHECK`, `CL-A3-GROUPS` | `CHECKED` vs A3 (`UNVERIFIED`, T-A3-SWING) |
| Lumped model | wing 5 mm strips, fins 4 × 8, tubes 8, 4 stations, centre group at A3's centroid (split for Iyy), pack and harness at A3's centroids | — | `loads.py#build_items` | `CHECKED` |
| Method | quasi-static rigid body (d'Alembert); cut load = sum over the outboard part | — | `loads.py#solve` | `CHECKED` |
| Spanwise lift and cm | B2 AVL + XFOIL strip shape at c 0.32, trimmed chordwise to the CG | — | `ASM-C1-B2-SPANLOAD` | `UNVERIFIED` |
| Factor of safety / fitting / printed-bonded | 1.5 / 1.15 / 1.25 | — | `P:requirements.safety_factor_ult`, `ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR` | `PROPOSED` |
| Crash loads | ultimate as stated, no further factor | — | FAR 23.561 practice | `PROPOSED` |

## Load cases

`F` flight · `H` hover · `T` transition · `L` landing · `G` ground handling · `X` transport · `C` crash · `A`
assembly. F, H, T, L1–L5 and G form the **sizing envelope**; L6/L7 (damage), X, C and A are reported separately.
Every envelope case runs on both mass configurations.

| Case | What | Key numbers | Sizes |
|---|---|---|---|
| F1 / F2 | symmetric pull-up at VD / VA | n +3.4, V 27.2 / 22.0 m/s | proof test |
| F3 | push-over at VD | n −1.5 | negative bending |
| F4 / F5 | gust peaks (Pratt, U 8 m/s at VC → 4 m/s at VD) | +3.32 at 21.7 m/s / −1.36 at 19.2 m/s | inside n± |
| F6 | roll: full elevon at VA, ⅓ at VD (D-50: held by F4's envelope), n 1 | ±25° / ±8.3° | elevon roots |
| F7 | rolling pull-up, ⅔ n⁺, same schedule | n 2.27 | **wing shear Vz**, outboard proof step |
| F8 | cruise 1 g, 16 m/s | reference | — |
| H1 / H2 | hover trimmed / four motors at T_lim (7° cant) | 21.1 N each, n 3.31 | in-plane spar |
| H3 / H4 | one pair at T_lim, other off, + gyro 3 rad/s | 0.37 N·m per rotor | mounts |
| H5 | right pair at T_lim, left off | in-plane yaw | **mount / motor moment** |
| H6 / H7 | diagonal pair at T_lim (yaw), cant side forces add | Q 0.42 N·m per motor | wing torsion (2nd) |
| H8 / H9 | 8 m/s gust broadside on the wing / fins | — | out-of-plane fin loads |
| T1 / T2 / T3 | transition 45° at the A1 gate / flare 30° at 16 m/s, one pair + gyro | — | biaxial spar, mounts |
| L1 | level on four feet, n_L **6.6**, rotor lift ⅔ W, D5 per-type cartridges | upper 44.4 N, lower 39.7 N per foot | **spar, fin-joint force, pod saddle, pack stop** |
| L2 / L3 | one pair first, 10° pitch / roll error | 28.0 / 33.4 N per foot | pod moment (L2) |
| L4 / L5 | one foot first + design side load across / along the fin | 36.7 N + **39.3 N** side | **fin-joint moment, half-fin torsion and bending, wing torsion, foot** |
| L6 / L7 | wingtip TE strike / tip-over (damage) | 63 N / 4.7 J | — (feet clear 10.7°) |
| G1 / G2 | lifted by the pod / carried by one upper tube end, 2 g | G2 hand load 51 N | **spar flap Mx** (G2) |
| G3 | set down flat on the lower motor cans and feet, 2 g | **23.46 N** per motor can (`CL-C1-G3-CAN-F`) | **mount / motor force** |
| X1–X4 | 0.3 m box drop: nose wall (x), end walls (y), floor (z), lid-down; props and pack out | n_T 10.09 at 66 mm | compared with the envelope |
| X5 | aft-wall drop on the four feet at D5's plateaus (D-53) | n 7.79 | compared with the envelope |
| X6 | nose-wall drop with the pod nose on D7's nose pad (reacted at the pod) | n_T 10.09 → J-POD 154 N | compared with the envelope |
| C1 | 5 m/s arrested in 0.10 m (ultimate) | n_c 12.75, pack 73.75 N | pack strap, avionics |
| A1 / A2 | prop-nut torque / pack strap preload | 1.5 N·m / 40 N | mount clamp, tray |

## Flight envelope

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Stall Vs (gate, trimmed CLmax 0.80) | 11.90 | m/s | `CL-C1-VS` | `UNVERIFIED` (T-B2-STALL) |
| Manoeuvre speed VA | 21.94 | m/s | `CL-C1-VA` | `UNVERIFIED` |
| VH = max(pitch speed 18.0 at 7 749 rpm, F4 level speed at THR_MAX 70 %) | 21.27 | m/s | `CL-C1-VH` ← `CL-F4-VLEVEL` | `UNVERIFIED` (H2 log) |
| Derived VD = 1.25 VH rounded up | 26.6 vs requirement 27.2 | m/s | `CL-C1-VD` | `CHECKED` (+2 %) |
| Envelope VD, q | 27.2, 453 | m/s, Pa | `CL-C1-VD-ENV`, `CL-C1-Q-VD` | `CHECKED` |
| Design n± (gust peak) | +3.4 / −1.5 (+3.32 / −1.36) | — | `CL-C1-N-LIMIT-POS/NEG`, `CL-C1-GUST-N-POS/NEG` | `CHECKED` |
| Uncapped VD (information) | 32.1 | m/s | `CL-C1-VD-UNCAPPED` | rejected (D-50) |
| Stall-line n at VD | 5.22 vs 3.4 | — | `CL-C1-N-STALL-VD` | `FAIL` → F4 envelope (CR-C1-08) |

![V-n diagram](data/vn-diagram.svg)

`FIG C1-01 — V-n diagram at 2.6 kg: manoeuvre envelope (blue), stall lines (dashed), gust lines, gust peak (orange).`

**What the THR_MAX cap buys** (`data/sensitivity_vd.json`, envelope at 27.2 vs the rejected 32.1 m/s): spar, fin
joint, fin half, mounts, pod and feet unchanged (landing, handling and hover govern); wing shear Vz −2 %; proof load
−5 %. The cap is worth q 453 vs 631 Pa (−28 %: elevon hinge, horns, servo) and the stall-line n 5.2 vs 7.3. If the
H2 log shows a level speed above 21.76 m/s, `CL-F4-VLEVEL-VH` fails and C1 re-runs.

## Rotor loads per motor

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Peak static thrust at the 9 350 rpm cap | 21.08 vs requirement 21.1 | N | `CL-C1-T-CAP` | `CHECKED` (+0.1 %) |
| Limit thrust T_lim (every case) | 21.1 | N | `CL-C1-T-LIMIT` | `UNVERIFIED` (T-C1-THRUST-FRESH) |
| Cant side force at T_lim (7°, tangential, net zero in symmetric hover) | 2.57 | N | `CL-C1-CANT-FSIDE` | `PROPOSED` (sense per D-52) |
| Motor-plane force at the mount face, rotor-on cases | 8.43 (F7-VA) | N | `CL-C1-MOTOR-FSIDE-LIM` | `UNVERIFIED` |
| Bending at the mount face, rotor-on cases | 0.49 / 0.74 | N·m limit / ult | `CL-C1-MOTOR-MB-LIM/-ULT` (H5) | `UNVERIFIED` |
| Reaction torque / gyroscopic moment | 0.42 / 0.37 | N·m | `CL-C1-MOTOR-TORQUE`, `CL-C1-GYRO-MOMENT` | `UNVERIFIED` |
| Prop-nut torque at set-up | 1.5 | N·m | `ASM-C1-PROP-NUT-TORQUE` | `UNVERIFIED` |

## Results by structure (envelope, both sides folded)

| Structure (consumer) | Quantity | Limit | Ultimate | Unit | Governing case | Claim |
|---|---|---|---|---|---|---|
| Spar root (C2) | bending resultant √(Mx²+Mz²) | 13.8 | 20.7 | N·m | L1 (in-plane) | `CL-C1-SPAR-MB-ULT` |
| Spar (C2) | flap bending Mx, max along span | 8.0 | 12.0 | N·m | G2 | `CL-C1-SPAR-MX-ULT` |
| Wing (C2) | torsion about the spar | 5.6 | 8.4 | N·m | L4 | `CL-C1-WING-TORSION-ULT` |
| Wing (C2) | shear Vz / in-plane Vx | 21.8 / 53.3 | 32.8 / 79.9 | N | F7-VA / L1 | `CL-C1-WING-SHEAR-ULT` |
| Fin group → wing (fin root + saddle), each side (C4, C6) | force / moment | 59.4 / 15.0 | 89.2 / 22.5 | N / N·m | L1 / L4 | `CL-C1-FINJOINT-F/M-ULT` |
| Same, joint design (× 1.15 × 1.25) | moment | — | 32.3 | N·m | — | `CL-C1-FINJOINT-M-DESIGN` |
| Fin + tube section (C4) | bending / torsion (section total) | 10.9 / 12.7 | 16.3 / 19.0 | N·m | L5 / L4 | `CL-C1-FINHALF-MB-ULT`, `-T-LIM/-ULT` |
| Fin + tube at the wing plane, J-FINHALF (C4, C6 collar) | torsion | 12.63 | 18.94 | N·m | L4 | `CL-C1-FINHALF-T-WINGPLANE-LIM/-ULT` |
| Mount → tube (C4, C6) | force / moment | 21.1 / 0.66 | 31.6 / 0.99 | N / N·m | G3 / H5 | `CL-C1-MOUNT-F/M-ULT` |
| Lower motor can on the bench (C4) | reaction per can | 23.46 | 35.19 | N | G3 | `CL-C1-G3-CAN-F(-ULT)` |
| Motor → mount screws (C6) | force | 21.4 | 32.2 | N | G3 | `CL-C1-MOTOR-F-ULT` |
| Pod → wing, spar saddle POD-007 + bond (C3) | force / moment | 75.8 / 2.7 | 113.7 / 4.0 | N / N·m | L1 / L2 | `CL-C1-POD-F-LIM`, `-POD-F-ULT` |
| Pack → tray, aft stop (C3) | resultant, landing | 42.5 | 63.7 (design 91.6) | N | L1 (MC-P) | `CL-C1-PACK-STOP-LIM/-ULT` |
| Pack → tray, crash any axis (C3) | force (ultimate) | — | 73.75 | N | C1 | `CL-C1-PACK-CRASH-LOAD` |
| Foot → fin tip (C5, D5) | cut force / applied upper foot | 53.2 / 44.4 | 79.7 / 66.6 | N | L4 / L1 | `CL-C1-FOOT-F-ULT`, `-FOOT-LEVEL-UPPER(-ULT)` |
| Foot side force at the pad | design (C5 sim; friction alone gives 25.7) | 39.30 | 58.96 | N | L4 / L5 | `CL-C1-FOOT-SIDE-DESIGN(-ULT)` |
| Elevon panel (D6) | normal load per metre at VD, CN 1.0 | 31.9 | 47.9 | N/m | q 453 Pa | `data/envelope.json` |

**Fin roots at n 6.6 with the 39.3 N side load** (`data/sensitivity_side.json`):

| Quantity | R4 | R5, friction only | R5, C5 μ 0.5 (29.1 N) | R5, C5 μ 0.7 (39.3 N) |
|---|---|---|---|---|
| Fin-joint moment, ult (N·m) | 14.34 | 16.11 | 17.65 | **22.46** |
| Half-fin torsion at the wing plane, limit (N·m) | 7.37 | 8.30 | 9.38 | **12.63** |
| Half-fin bending, ult (N·m) | 11.41 | 12.39 | 13.06 | **16.33** |
| Foot cut force, ult (N) | 59.6 | 66.3 | 69.3 | **79.7** |

n 6.6 alone adds about 10 %; the side load adds the rest. Scaling C4's R4 margins linearly (an estimate; C4's re-run
replaces it): collar bond MS 0.16 → about −0.32, fin face with the shoe cheeks 0.01 → about −0.29, through-core block
0.55 → about 0.0. The fin roots do not close at 39.3 N without a change: CR-C1-35 (C4/C6 re-run) and CR-C1-36 (μ ≤ 0.5
pad face, C1's recommendation).

![Wing spanwise envelope](data/wing-envelope.svg)

`FIG C1-02 — Ultimate spanwise moments on the spar axis, right half (left mirrored), envelope of all sizing cases.`

## Transport (D7)

Axis names (CR-D7-14a, confirmed): aircraft **x = chord = the box's long walls** (X1 nose wall, cradle-reacted;
X5 aft wall, feet-reacted; X6 nose wall with the pod nose on the nose pad); **y = span = the end walls** (wingtips, X2);
z = floor (X3) and lid (X4).

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Floor drop 0.3 m on D7's 66 mm cradle stroke, η 0.5 | n_T 10.09 vs allowable 13.19 | — | `CL-C1-TRANSPORT-N`, `-N-ALLOW` | `CHECKED` (+31 %) |
| Aft-wall drop, feet at D5's plateaus | n 7.79 vs allowable **10.76** (R4's 9.22 a safe lower bound) | — | `CL-C1-TRANSPORT-N-AFT`, `-N-ALLOW-AFT` | `CHECKED` (+28 %; J-FIN force governs) |
| Nose wall, pod nose on the nose pad (X6) | allowable **n 4.98** (J-POD governs) → h 0.021 m on 3/4 in, **0.014 m** on 1/2 in vs D7's 0.059 m | — | `CL-C1-TRANSPORT-N-ALLOW-NOSE` | `FAIL` vs 0.059 m (label-and-test, CR-C1-38) |
| Nose wall cradle-reacted (X1) / end walls (y) / lid allowable | 13.04 / 13.11 / 13.19 | — | `CL-C1-TRANSPORT-N-ALLOW-X/-Y/-LID` | label-and-test only (D-53) |
| Stroke a 0.3 m drop would need: floor / nose (cradle) / end | 49 / 50 / 50 | mm | `CL-C1-CRADLE-STROKE-REQ`, `CL-C1-BOX-STROKE-REQ-X/-Y` | information |
| Pillar / cradle force per side (limit) | 102 / 102 | N | `CL-C1-PILLAR-F-LIM`, `CL-C1-CRADLE-F-LIM` | `CHECKED` |

## Wing limit proof (GT-08 = `T-C1-WING-PROOF`, agreed with C2 per CR-H1-13)

**Step 1, symmetric tree.** Aircraft inverted on a stand under the pod (support |y| ≤ 0.07 m), half-fins hanging
free; four 40 × 40 mm pads per side on the lower surface over the spar (x 0.08 m), plus an upward relief pull R on
each motor tube at the wing plane. It reproduces F1 at VD (MC-C) at the pod edge and on both sides of the fin; in
between the test moment is 0.78–1.06 of the case.

| Load point (per side) | y m | Limit N | Mass kg | Claim |
|---|---|---|---|---|
| P1 | 0.120 | 9.01 | 0.919 | `CL-C1-PROOF-Y1`, `-P1-LIM` |
| P2 | 0.250 | 5.14 | 0.524 | `CL-C1-PROOF-Y2`, `-P2-LIM` |
| P3 | 0.355 | 4.44 | 0.453 | `CL-C1-PROOF-Y3`, `-P3-LIM` |
| P4 | 0.465 | 6.01 | 0.613 | `CL-C1-PROOF-Y4`, `-P4-LIM` |
| Sum of pads, centroid | 0.274 | 24.60 | — | `CL-C1-PROOF-P-SIDE-LIM`, `-PIVOT-Y` |
| Relief R, upward at the tube | 0.320 | 19.92 | 2.031 | `CL-C1-PROOF-R-LIM` |
| Flap moment at the pod edge | 0.070 | 1.78 N·m | — | `CL-C1-PROOF-MX-ROOT-LIM` |

Pad 2 fell from 7.90 to 5.14 N in R5: the harness now rides at y 0.256 m, as A3 places it, and relieves the inboard
panel. Between y 0.07 and 0.44 m the test moment is 0.87–1.07 of the case; `CL-C1-PROOF-COVER-MIN` 0.60 sits at
y 0.45 m, where the case moment is only 0.18 N·m.

**Step 2, outboard, each side in turn** (rolling case F7-VA, which a symmetric tree cannot reach): padded V-block
under the spar at y 0.32 m (C2's set-up), pads 3 and 4 only at **4.90 N and 16.10 N** limit (0.499 / 1.642 kg);
reproduces V 21.8 N and Mx 2.61 N·m just outboard of the fin, ≥ 0.987 of the flight envelope out to pad 3
(`CL-C1-PROOF-OUT-*`). C2's 51 N tube-end hang is the **G2 handling case** and belongs to `T-C1-STATION-PROOF`.

All steps at **LIMIT** on the flight article (no permanent set, C2's 0.5 mm criterion). Ultimate only on a
sacrificial wing. Torsion: twist test at `CL-C1-WING-TORSION-ULT` / 1.5.

## Findings

| # | Finding | Number | Status | Action |
|---|---|---|---|---|
| 1 | C5's simulated side load at μ 0.7 raises the fin-root loads far more than n 6.6 does | torsion 7.37 → 12.63 N·m (+71 %), joint moment ult 14.3 → 22.5 N·m | `CHECKED` | C4/C6 re-run (CR-C1-35); μ ≤ 0.5 pad face (CR-C1-36) |
| 2 | Estimated C4 margins at 39.3 N go negative (collar, fin face), block about 0 | MS ≈ −0.32 / −0.29 / 0.0 | `UNVERIFIED` (C1 scaling estimate) | C4 `fin_structures_d3.py` |
| 3 | The landing now sizes the pack aft stop, not the crash | design 91.6 N vs crash 73.75 N ult | `CHECKED` | C3 (CR-C1-37) |
| 4 | A nose-first box drop onto the nose pad loads the pod joint; the allowance is far below D7's | n 4.98; 0.014 m at 1/2 in vs 0.059 m | `FAIL` (label-and-test) | D7 x-stops at the cradles, or label only (CR-C1-38) |
| 5 | Aft-wall drop on the feet | n 7.79 vs 10.76 | `CHECKED` (+28 %) | D7 limits `CL-D7-AFT-N` by `-ALLOW-AFT` |
| 6 | C1's upper-foot bound at the gate is above D5's plateau | 44.41 vs 39.58 N (ratio 0.891) | `CHECKED` (conservative) | D5 sizes to C1 (CR-C1-36) |
| 7 | With A3's groups the lumped model sits 7 mm off the CG limits before trim (was 29 mm); the rest is C1's fin and foot lumps | 7.2 mm | `CHECKED` | none needed (band met) |
| 8 | Stall-line n at VD 5.2 > 3.4 | 5.22 vs 3.4 | `FAIL` | F4 envelope (CR-C1-08) |
| 9 | Parked on the mat it slides at μ 0.68 needed vs 0.7; a μ 0.5 pad face (finding 1) would let the parked aircraft slide in 8 m/s | 3 % | `CHECKED` (thin) | lay flat in wind (C5 S1–S8) if the μ 0.5 face is chosen |

## Data files (`team/C1/data/`)

All loads are limit, SI units, aircraft frame. Cut loads are the resultant on the outboard part about the cut point.

| File | Content | Consumer |
|---|---|---|
| `wing_spanwise.csv` / `wing_envelope.csv` | every case × mass config on the spar axis every 5 mm / signed envelope + ultimate Mbend | C2, D1 |
| `fin_heightwise.csv` / `fin_envelope.csv` | fin + tube section cut at height z (tube axis), each side and half / envelope | C4, D3 |
| `joints.csv` | 6-component load at every named joint per case (J-MOTOR includes the cant side force) | C3–C6 |
| `envelope.json` | per joint class: limit, ultimate, joint design, printed/bonded design, case; landing, crash, assembly, elevon, rotor, transport, fin-collar torsion | C3–C6, D5–D7 |
| `whiffletree.json` / `.csv` | four pads, relief, outboard step 2, masses, limit/ultimate, coverage per station | H1, C2 |
| `sensitivity_vd.json` | envelope at 27.2 vs the rejected uncapped 32.1 m/s | A1, F4 |
| `sensitivity_side.json` | envelope at the 39.3 N side load vs 29.1 N (μ 0.5) and friction only | C4, C5, D5, A1 |
| `feet.csv`, `cases.json`, `mass_model.csv`, `checks.json` | foot loads; case states (X5, X6 included); masses, trim in x and z, spread, inertia; self-checks incl. C1 vs A3 group centroids | C5, D5, A3, review |

## Checks

| Check | Result | Status |
|---|---|---|
| Free-body equilibrium, every case and config | residual < 1e-11 N or N·m | `CHECKED` |
| Strip convergence, F1 root Mx at dy 10 / 5 / 2.5 mm | 2.8250 / 2.8260 / 2.8259 N·m (0.03 %) | `CHECKED` |
| Hand check, F8 root Mx (B2's own centroid) | 0.817 hand vs 0.831 model N·m (1.8 %) | `CHECKED` |
| B2's 1 g root lift moment (`CL-B2-ROOT-BM-1G`) | 3.0942 model vs 3.0942 N·m (0.002 %) | `CHECKED` |
| Cant in J-MOTOR, H2 | in-plane 2.67 N vs T sin 7° 2.57 N | `CHECKED` |
| Inertia vs A3-R7 (`CALC-C1-MASS-XCHECK`) | 0.90–1.02, band 0.85–1.15 | `CHECKED` |
| Proof chain `build_graph.py` | 0 C1 drift, no unknown ids; one C1 FAIL (`CL-C1-N-STALL-VD`, finding 5) | `CHECKED` |
| Physical tests (planned) | `T-C1-WING-PROOF` (GT-08), `T-C1-FOOT-DROP`, `T-C1-THRUST-FRESH`, `T-C1-STATION-PROOF` | `PROPOSED` |

## Open issues

1. Fin roots: C4/C6 must re-run on the R5 loads; the pad-face μ decision (CR-C1-36) moves them by about 25 %.
2. The side load is C5's rigid-airframe 6-DOF value (fin flexibility would soften it); C1 pairs it with the corner
   normal load quasi-statically, which is conservative. `T-D5-SIDE` and `T-C1-FOOT-DROP` replace it.
3. VD rests on F4's THR_MAX cap: until the H2 log, `CL-C1-VH` is `UNVERIFIED`.
4. The centre-group spread is still at the pod half-length (MC-P Iyy 0.90 of A3): C1's fin board lumps sit 27 mm
   forward of A3's fin centroid. Moving C1's fin lumps to A3's per-station centroids is the next model step.
5. Inputs are live: A3, C5 and D5 republished during this run; a later republish moves these numbers by a few %.
6. Quasi-static only: no dynamic overshoot, no ω² terms, no prop imbalance (C4, `R-VIBRATION`).
7. Tip-over (L7): first contact is the upper props and motor cans (D-23 fuse); 4.7 J is an upper bound.
