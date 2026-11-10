# Loads — K09-L quad tailsitter

Owner: C1 (loads engineer). Revision **C1-R4** (D-50 action items), 2026-11-09, at params revision **A1-R4** (CG range
0.050–0.0549 m, pod nose −0.130 m, allocations 2 355 g, VD 27.2 m/s, n⁺ 3.4, T_lim 21.1 N, 7° cant). Status: the
calculation is `CHECKED` (equilibrium, convergence, two hand checks, 0 C1 drift in the proof chain); its inputs are
`PROPOSED`/`UNVERIFIED` (thrust, CLmax, masses, the capped VH), so every load is `UNVERIFIED` until the stand, the
level-speed log, the scale, the swing and the proof test replace them.
Re-run in ~10 s: `python -I redesign/team/C1/loads.py`, then `python -I redesign/proofs/build_graph.py`.

Every number is a **limit** load (largest expected in service) unless labelled ultimate; ultimate = 1.5 × limit.
Frame: x aft, y right, z up in cruise (`params.json#frame`); in hover +x points at the ground.

## What changed in R4

| Item | R3 | R4 | Why |
|---|---|---|---|
| VH basis | B1's uncapped top speed `CL-B1-VMAX` 25.7 m/s → VD 32.1 | F4's level speed at THR_MAX 70 % **`CL-F4-VLEVEL` 21.28 m/s** (pitch-speed cross-check at `CL-F4-FW-RPM-CAP` 7 749 rpm: 18.0 m/s) → `CL-C1-VD` **26.7 m/s** (1.25 VH rounded **up**) | D-50; the 32.1 alternative and a 27.25 rounding are rejected |
| Envelope VD, n± | 32.1 m/s, +3.58 / −1.58 | **27.2 m/s, +3.4 / −1.5** (requirement governs; gust peak +3.32 / −1.36) | follows VD |
| Negative CL | 0.40 | **0.44** (`ASM-C1-CLMIN`, CR-B2-13) | B2 at c 0.32 |
| B2 strip load, CLα | c 0.30 table | c 0.32 table (centroid 0.422 b/2), CLα **3.48 /rad** read live | CR-B2-13 |
| Mass properties | lumped model, Iyy 0.72–0.82 of A3 | centre group **spread ±0.1125 m in x** (pod half-length cap) → Iyy 0.90–0.99 of A3-R5, Ixx 0.94–0.95, Izz 0.94–0.97 (`CL-C1-INERTIA-RATIO-MIN/-MAX`) | A3-R5 action item; low inertia was unconservative |
| Feet | `ASM-C1-FOOT-BIAS` 1.077 | **D5's per-type plateaus read live** (39.58 / 35.40 N → bias 1.056); η **0.903** (`CL-D5-ETA`) | CR-D5-23; assumption retired |
| Cant in J-MOTOR / J-FINHALF | carried, not published | published: `CL-C1-CANT-FSIDE` 2.57 N, `-MOTOR-FSIDE-LIM` 8.43 N, `-MOTOR-MB-LIM` 0.49 N·m | CR-C6-21a |
| Half-fin torsion | `CL-C1-FINHALF-T-LIM` only | + **`CL-C1-FINHALF-T-WINGPLANE-LIM/-ULT`** (J-FINHALF joint cut) | action item, CR-C1-21 |
| Whiffletree | pads 1–3 as claims; pad 4 in the JSON only | **pad 4, relief R, centroid and an outboard step 2** as claims; JSON lists all four pads | CR-H1-09, CR-H1-13 |
| Transport | x "end", y "side"; no aft-wall case | x = **nose wall** (box long wall), y = **end walls** (wingtips); **X5 aft wall on the feet** | CR-D7-14, D-53 |

## Action items (D-50) — resolution

| Item | Result | Status |
|---|---|---|
| Re-run on the capped VH | `CL-C1-VH` 21.28 m/s ← `CL-F4-VLEVEL`; `CL-C1-VD` 26.7 ≤ 27.2 (**pass**, +1.9 %); `CL-C1-VD-ENV` 27.2; q 453 Pa | `CHECKED` (`UNVERIFIED` until the H2 level log) |
| A3-R5 mass and inertia | pack station `CL-A3-PACK-X-REQ` read live; Iyy matched by the centre-group spread; CG trim now 28–29 mm (lumped model nose-heavy against A3's roll-up, CR-C1-33) | `CHECKED` |
| B2 c 0.32 inputs | CLmin 0.44, CLα 3.48, strip table; B2's 1 g root lift moment reproduced **3.0942 vs 3.0942 N·m** | `CHECKED` |
| D5 per-type feet | L1 upper 40.38 N / lower 36.12 N limit; D5's 39.58 N peak inside (`CL-C1-FOOT-D5-RATIO` 0.980) | `CHECKED` (thin, 2 %) |
| 7° side force in J-MOTOR / J-FINHALF | already in every rotor-on case (thrust vector applied at the prop plane); H2 check: J-MOTOR in-plane 2.70 N vs T sin 7° 2.57 N (+ rotor-group inertia) | `CHECKED` |
| Pad 4 and half-fin torsion as claims | `CL-C1-PROOF-Y4` 0.465 m, `-P4-LIM` 6.04 N; `CL-C1-FINHALF-T-WINGPLANE-LIM` 7.40 N·m | `CHECKED` |
| One wing limit proof with C2 | GT-08 = `T-C1-WING-PROOF`: step 1 four-pad tree, step 2 outboard V-block at y 0.32 (C2's set-up, C1's loads); C2's 51 N tube-end hang moves to `T-C1-STATION-PROOF` | `PROPOSED` (CR-C1-27 to C2) |
| Box axis names for D7 | D7's reading confirmed: x = chord = long walls (nose X1, aft X5), y = span = end walls (X2) | `CHECKED` |
| 91 drifts | 0 C1 drift after the re-run (`CALC-C1-ENVELOPE` 75, `-LANDING` 15, `-CRASH` 1 cleared) | `CHECKED` |

## Basis

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design mass | 2.600 (gate) | kg | `P:requirements.mtow_gate_kg` | `PROPOSED` |
| Mass configurations | MC-C: gap to the gate in the pod, CG on the forward limit; MC-P: every item × gate/sum, CG on the aft limit | — | `data/mass_model.csv` | `PROPOSED` |
| CG range | 0.050 / 0.0549 | m | `P:cg.x_range_m` | `UNVERIFIED` |
| Inertia | Iyy matched to `CL-A3-IYY` (MC-C as rolled up; MC-P × m_gate/m_A3) by a ±0.1125 m centre-group spread | kg·m² | `CALC-C1-MASS-XCHECK` | `CHECKED` vs A3 (`UNVERIFIED`, T-A3-SWING) |
| Lumped model | wing 5 mm strips, fins 4 × 8, tubes 8, 4 stations, pod group (split for Iyy), pack | — | `loads.py#build_items` | `CHECKED` |
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
| L1 | level on four feet, 1.5 m/s, n_L 6, rotor lift ⅔ W, D5 per-type cartridges | upper 40.4 N, lower 36.1 N per foot | **spar, fin half, pod, feet** |
| L2 / L3 | one pair first, 10° pitch / roll error | 25.5 / 29.3 N per foot | fin halves |
| L4 / L5 | one foot first + μ 0.7 across / along the fin | 32.7 N + 22.9 N side | **fin joint moment, fin torsion, wing torsion** |
| L6 / L7 | wingtip TE strike / tip-over (damage) | 93 N / 4.6 J | — (feet clear 10.7°) |
| G1 / G2 | lifted by the pod / carried by one upper tube end, 2 g | G2 hand load 51 N | **spar flap Mx** (G2) |
| G3 | set down flat on the lower motor cans and feet, 2 g | 23.2 N per motor can | **mount / motor force** |
| X1–X4 | 0.3 m box drop: nose wall (x), end walls (y), floor (z), lid-down; props and pack out | n_T 10.09 at 66 mm | compared with the envelope |
| X5 | aft-wall drop on the four feet at D5's plateaus (D-53) | n 7.79 | compared with the envelope |
| C1 | 5 m/s arrested in 0.10 m (ultimate) | n_c 12.75 | pack strap, avionics |
| A1 / A2 | prop-nut torque / pack strap preload | 1.5 N·m / 40 N | mount clamp, tray |

## Flight envelope

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Stall Vs (gate, trimmed CLmax 0.80) | 11.91 | m/s | `CL-C1-VS` | `UNVERIFIED` (T-B2-STALL) |
| Manoeuvre speed VA | 21.96 | m/s | `CL-C1-VA` | `UNVERIFIED` |
| VH = max(pitch speed 18.0 at 7 749 rpm, F4 level speed at THR_MAX 70 %) | 21.28 | m/s | `CL-C1-VH` ← `CL-F4-VLEVEL` | `UNVERIFIED` (H2 log) |
| Derived VD = 1.25 VH rounded up | 26.7 vs requirement 27.2 | m/s | `CL-C1-VD` | `CHECKED` (+1.9 %) |
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
| Spar root (C2) | bending resultant √(Mx²+Mz²) | 13.1 | 19.6 | N·m | L1 (in-plane) | `CL-C1-SPAR-MB-ULT` |
| Spar (C2) | flap bending Mx, max along span | 8.0 | 12.0 | N·m | G2 | `CL-C1-SPAR-MX-ULT` |
| Wing (C2) | torsion about the spar | 5.0 | 7.5 | N·m | L4 | `CL-C1-WING-TORSION-ULT` |
| Wing (C2) | shear Vz / in-plane Vx | 21.5 / 49.5 | 32.3 / 74.3 | N | F7-VA / L1 | `CL-C1-WING-SHEAR-ULT` |
| Fin group → wing, each side (C4, C6) | force / moment | 55.2 / 9.6 | 82.8 / 14.4 | N / N·m | L1 / L4 | `CL-C1-FINJOINT-F/M-ULT` |
| Same, joint design (× 1.15 × 1.25) | moment | — | 20.7 | N·m | — | `CL-C1-FINJOINT-M-DESIGN` |
| Fin + tube section (C4) | bending / torsion (section total) | 7.6 / 7.42 | 11.4 / 11.1 | N·m | L1 / L4 | `CL-C1-FINHALF-MB-ULT`, `-T-LIM/-ULT` |
| Fin + tube at the wing plane, J-FINHALF (C4, C6 collar) | torsion | 7.40 | 11.1 | N·m | L4 | `CL-C1-FINHALF-T-WINGPLANE-LIM/-ULT` |
| Mount → tube (C4, C6) | force / moment | 20.8 / 0.65 | 31.2 / 0.97 | N / N·m | G3 / H5 | `CL-C1-MOUNT-F/M-ULT` |
| Motor → mount screws (C6) | force | 21.2 | 31.8 | N | G3 | `CL-C1-MOTOR-F-ULT` |
| Pod → wing (C3) | force / moment | 78.3 / 3.0 | 117.5 / 4.4 | N / N·m | L1 / L2 | `CL-C1-POD-F-ULT` |
| Pack → tray, crash any axis (C3) | force (ultimate) | — | 85.0 | N | C1 | `CL-C1-PACK-CRASH-LOAD` |
| Foot → fin tip (C5, D5) | cut force / applied upper foot | 39.8 / 40.4 | 59.6 / 60.6 | N | L1 | `CL-C1-FOOT-F-ULT`, `-FOOT-LEVEL-UPPER(-ULT)` |
| Foot side force (μ 0.7) | corner | 22.9 | 34.3 | N | L4 | `data/envelope.json` |
| Elevon panel (D6) | normal load per metre at VD, CN 1.0 | 31.9 | 47.9 | N/m | q 453 Pa | `data/envelope.json` |

The R4 inertia match raised the L4-driven loads: fin-joint moment +14 %, half-fin torsion +12 %, corner foot +11 %,
wing torsion +10 % (L4 now governs it, was H6). A lumped model with too little inertia under-states them.

![Wing spanwise envelope](data/wing-envelope.svg)

`FIG C1-02 — Ultimate spanwise moments on the spar axis, right half (left mirrored), envelope of all sizing cases.`

## Transport (D7)

Axis names (CR-D7-14a, confirmed): aircraft **x = chord = the box's long walls** (X1 nose wall, cradle-reacted;
X5 aft wall, feet-reacted); **y = span = the end walls** (wingtips, X2); z = floor (X3) and lid (X4).

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Floor drop 0.3 m on D7's 66 mm cradle stroke, η 0.5 | n_T 10.09 vs allowable 12.45 | — | `CL-C1-TRANSPORT-N`, `-N-ALLOW` | `CHECKED` (+23 %) |
| Aft-wall drop, feet at D5's plateaus | n 7.79 vs allowable 9.22 | — | `CL-C1-TRANSPORT-N-AFT`, `-N-ALLOW-AFT` | `CHECKED` (+18 %; J-FINHALF bending governs) |
| Nose wall (x) / end walls (y) / lid allowable | 12.28 / 12.28 / 12.45 | — | `CL-C1-TRANSPORT-N-ALLOW-X/-Y/-LID` | label-and-test only (D-53) |
| Stroke a 0.3 m drop would need: floor / nose / end | 52 / 53 / 53 | mm | `CL-C1-CRADLE-STROKE-REQ`, `CL-C1-BOX-STROKE-REQ-X/-Y` | information |
| Pillar / cradle force per side (limit) | 102 / 102 | N | `CL-C1-PILLAR-F-LIM`, `CL-C1-CRADLE-F-LIM` | `CHECKED` |

## Wing limit proof (GT-08 = `T-C1-WING-PROOF`, agreed with C2 per CR-H1-13)

**Step 1, symmetric tree.** Aircraft inverted on a stand under the pod (support |y| ≤ 0.07 m), half-fins hanging
free; four 40 × 40 mm pads per side on the lower surface over the spar (x 0.08 m), plus an upward relief pull R on
each motor tube at the wing plane. It reproduces F1 at VD (MC-C) at the pod edge and on both sides of the fin; in
between the test moment is 0.78–1.06 of the case.

| Load point (per side) | y m | Limit N | Mass kg | Claim |
|---|---|---|---|---|
| P1 | 0.120 | 8.95 | 0.912 | `CL-C1-PROOF-Y1`, `-P1-LIM` |
| P2 | 0.250 | 7.66 | 0.781 | `CL-C1-PROOF-Y2`, `-P2-LIM` |
| P3 | 0.355 | 4.44 | 0.452 | `CL-C1-PROOF-Y3`, `-P3-LIM` |
| P4 | 0.465 | 6.04 | 0.616 | `CL-C1-PROOF-Y4`, `-P4-LIM` |
| Sum of pads, centroid | 0.272 | 27.08 | — | `CL-C1-PROOF-P-SIDE-LIM`, `-PIVOT-Y` |
| Relief R, upward at the tube | 0.320 | 19.40 | 1.979 | `CL-C1-PROOF-R-LIM` |
| Flap moment at the pod edge | 0.070 | 2.24 N·m | — | `CL-C1-PROOF-MX-ROOT-LIM` |

**Step 2, outboard, each side in turn** (rolling case F7-VA, which a symmetric tree cannot reach): padded V-block
under the spar at y 0.32 m (C2's set-up), pads 3 and 4 only at **4.85 N and 15.85 N** limit (0.495 / 1.616 kg);
reproduces V 21.5 N and Mx 2.57 N·m just outboard of the fin, ≥ 0.99 of the flight envelope out to pad 3
(`CL-C1-PROOF-OUT-*`). C2's 2 × 25 N per side carried an old VD 32.1 / ultimate-level moment (≈ 5 N·m at 0.32 m,
2 × this) and is withdrawn. C2's 51 N tube-end hang is the **G2 handling case** (hand load 2 W) and belongs to
`T-C1-STATION-PROOF` (J-FIN cut in G2: 42.2 N, 8.09 N·m limit).

All steps at **LIMIT** on the flight article (no permanent set, C2's 0.5 mm criterion). Ultimate only on a
sacrificial wing. Torsion: twist test at `CL-C1-WING-TORSION-ULT` / 1.5.

## Findings

| # | Finding | Number | Status | Action |
|---|---|---|---|---|
| 1 | With F4's THR_MAX 70 % the derived VD is 26.7 m/s, inside 27.2; the structure runs at 27.2 | 26.7 vs 27.2 m/s | `CHECKED` | H2 full-throttle level log confirms (`CL-F4-VLEVEL-VH`) |
| 2 | The lumped model had 72–82 % of A3's pitch inertia; matching it raises the L4 loads 10–14 % | Iyy ratio 0.90–0.99 now | `CHECKED` | C4/C5/C6 re-run (CR-C1-29); A3 group inertia (CR-C1-33) |
| 3 | D5's per-type upper foot sits 2 % inside C1's L1 bound | 39.58 vs 40.38 N | `CHECKED` (thin) | D5 sizes to C1's 60.6 N ult (CR-C1-34) |
| 4 | Aft-wall drop on the feet: n 7.79 vs 9.22 allowable | +18 % | `CHECKED` | D7 (CR-C1-31) |
| 5 | Stall-line n at VD 5.2 > 3.4 | 5.22 vs 3.4 | `FAIL` | F4 envelope (no raw-stick FW, PTCH_LIM_MIN −10, AIRSPEED_MAX 18) (CR-C1-08) |
| 6 | Model CG sits 28–29 mm ahead of the limits before the trim (larger than R3's 16–18 mm) | 28.8 mm | `PROPOSED` | A3 group centroids (CR-C1-33) |
| 7 | Set-down on the lower motor cans is the mount's largest force | 20.8 N limit | `PROPOSED` | CR-C1-24 open |
| 8 | Parked on the mat it slides at μ 0.68 needed vs 0.7 | 3 % | `CHECKED` (thin) | rule S1 |

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
| `feet.csv`, `cases.json`, `mass_model.csv`, `checks.json` | foot loads; case states (X5 included); masses, trim, spread, inertia; self-checks | C5, D5, A3, review |

## Checks

| Check | Result | Status |
|---|---|---|
| Free-body equilibrium, every case and config | residual < 1e-11 N or N·m | `CHECKED` |
| Strip convergence, F1 root Mx at dy 10 / 5 / 2.5 mm | 3.4439 / 3.4448 / 3.4448 N·m (0.03 %) | `CHECKED` |
| Hand check, F8 root Mx (B2's own centroid) | 0.999 hand vs 1.013 model N·m (1.5 %) | `CHECKED` |
| B2's 1 g root lift moment (`CL-B2-ROOT-BM-1G`) | 3.0942 model vs 3.0942 N·m (0.002 %) | `CHECKED` |
| Cant in J-MOTOR, H2 | in-plane 2.70 N vs T sin 7° 2.57 N | `CHECKED` |
| Inertia vs A3-R5 (`CALC-C1-MASS-XCHECK`) | 0.90–0.99, band 0.85–1.15 | `CHECKED` |
| Proof chain `build_graph.py` | 0 C1 drift, no unknown ids; one C1 FAIL (`CL-C1-N-STALL-VD`, finding 5) | `CHECKED` |
| Physical tests (planned) | `T-C1-WING-PROOF` (GT-08), `T-C1-FOOT-DROP`, `T-C1-THRUST-FRESH`, `T-C1-STATION-PROOF` | `PROPOSED` |

## Open issues

1. VD rests on F4's THR_MAX cap: until the H2 log, `CL-C1-VH` is `UNVERIFIED`.
2. The centre-group spread is at its physical cap (pod half-length) in both configs; MC-P still sits at 0.90 of A3's
   Iyy. A3's group inertia would replace the spread (CR-C1-33).
3. Downstream drift from R4 (not C1's): C2 (spar root, τ, brace, `CALC-C2-AE-REQ` reads `CL-C1-VD`, should read
   `-VD-ENV`), C4 (static, block, cant), C5 (drop-dyn), C6, D3, D5, D7, H1 re-run on the new values.
4. Tip-over (L7): first contact is the upper props and motor cans (D-23 fuse); 4.6 J is an upper bound.
5. Quasi-static only: no dynamic overshoot, no ω² terms, no prop imbalance (C4, `R-VIBRATION`).
6. Spin and cant senses per D-52; magnitudes are sense-independent.
