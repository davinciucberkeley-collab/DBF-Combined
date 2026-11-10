# Loads — K09-L quad tailsitter

Owner: C1 (loads engineer). Revision **C1-R3** (CR-A1-33), 2026-11-09, at params revision **A1-R3** (CG range
0.050–0.055 m, half-fins 0.21 m, tube 0.344 m, 7° cant, feet 48 mm, n⁺ 3.4, VD 27.2 m/s, T_lim 21.1 N). Status: the
calculation is `CHECKED` (equilibrium, convergence, hand check, 0 C1 drift in the proof chain); its inputs are
`PROPOSED`/`UNVERIFIED` (thrust, CLmax, masses, VH), so every load is `UNVERIFIED` until the stand, the twin, the
scale and the proof test replace them.
Re-run in ~2 s: `python -I redesign/team/C1/loads.py`, then `python -I redesign/proofs/build_graph.py`.

Every number is a **limit** load (largest expected in service) unless labelled ultimate; ultimate = 1.5 × limit.
Frame: x aft, y right, z up in cruise (`params.json#frame`); in hover +x points at the ground.

## What changed in R3

| Item | R2 | R3 | Why |
|---|---|---|---|
| Geometry and keys | R1 keys, 45 mm feet, 3° cant, 0.19 m half-fins | A1-R3 keys read live: n⁺ 3.4, VD 27.2, T 21.1 N, feet 48 mm, **7° cant modelled** (thrust side force 2.57 N per motor), half-fins 0.21, tube 0.344 | CR-A1-33 |
| CG | lumped model at x 0.036 / 0.044 m (ahead of the range) | centre group trimmed so MC-C sits on the **forward** limit 0.050 m and MC-P on the **aft** limit 0.055 m (shift +18 / +16 mm) | D-24; brackets the range |
| VH | pitch-speed proxy 21.8 m/s | **B1's `CL-B1-VMAX` 25.7 m/s** (11×5.5MR at the cap, CR-C1-14 answered) → derived VD **32.1 m/s** | finding 1 |
| Roll cases | full elevon at VD | full travel at VA, **⅓ travel at VD** (`ASM-C1-ELEVON-VD-FRAC`, the D-29 schedule) | FAR 23.455; CR-C1-15 |
| L4/L5 friction | 0.5 (grass) | **0.7** (neoprene pad on the mat, `ASM-D5-PAD-MU`) | CR-C5-09, rule S1 |
| Landing | η 0.5 foam, equal feet | D5 cartridge η (`CL-D5-ETA`); L1 with **biased cartridges** (upper ×1.077, lower ×0.923) | D-30, CR-C5-10 |
| G3 bench | lower motors + tube ends | lower motor cans + lower feet (tube ends now end at z ±0.172 inside the mounts) | D-26 |
| Transport | `ASM-C1-CRADLE-STROKE` 70 mm, one allowable | **`CL-D7-CRADLE-STROKE`** (66 mm today), allowables per axis x / y / z / lid, lid-pillar preload and lid-down case X4 | CR-D7-02 |
| Proof test | none | three-level **whiffletree** with limit / ultimate labels (`data/whiffletree.json`) | CR-H1-03 |
| Ids | `ASM-J1-MOUNT-MASS` read | **no `ASM-J1-*` id in C1** (`ASM-C1-MOUNT-MASS`); `ASM-J1-APC-KT`, `-MH45-CM0` gone | CR-J1-10 |

## Action items (CR-A1-33) — resolution

| Item | Result | Status |
|---|---|---|
| Re-run on R3 keys | done; envelope runs at max(requirement, derived), so VD 32.1 / n⁺ 3.58 (finding 1) | `CHECKED` |
| μ 0.7 on the mat for L4/L5 | side load 20.4 N per foot (0.7 × 29.1 N); fin-joint moment 8.34 N·m limit (L4 now governs it) | `CHECKED` |
| Fin-collar torsion with C4 (5.29 vs 9.3 N·m) | **agreed basis**: C1's 6.60 N·m (μ 0.7) is the **section total** about the tube axis; C4's FE collar torque is an **internal** path value (strip end + brace-ear couple) and may exceed it. C6 sizes the collar to the larger, i.e. C4's FE number re-run at μ 0.7 (expect ≈ 9.3 × 6.60/5.29 ≈ 11.6 N·m limit) | `PROPOSED` (C4 re-runs, CR-C1-21) |
| Cradle stroke 0.0699 | read from D7's claim (now 0.066 m): n_T 10.09 vs allowable 12.45 (+23 %) | `CHECKED` |
| x / y box allowables | n 12.13 (end) / 11.53 (side); a 0.3 m drop on those faces needs 54 / 57 mm of crush stroke, D7 has 16 / 36 mm of gap | `CHECKED` → test-only or foam (CR-C1-22) |
| Lid-pillar case | preload 5 N `EST` per pillar is a self-equilibrated pinch (no wing bending); lid-down drop puts 102 N per pillar (limit) over the spar; pad 64 kPa on 40 × 40 mm | `CHECKED` |
| Whiffletree, limit / ultimate labels for H1 | below; `CL-C1-WING-SHEAR-ULT` **is ultimate** (33.4 N; limit 22.2 N) | `CHECKED` |
| Retire `ASM-J1-*` | none left in `claims.json` or `loads.py` | `CHECKED` |

## Basis

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design mass | 2.600 (gate) | kg | `P:requirements.mtow_gate_kg` | `PROPOSED` |
| Mass configurations | MC-C: gap to the gate in the pod, CG on the forward limit; MC-P: every item × gate/sum, CG on the aft limit | — | `data/mass_model.csv` | `PROPOSED` |
| CG range | 0.050 / 0.055 (z +0.021 / +0.018) | m | `P:cg.x_range_m` | `UNVERIFIED` |
| Lumped model | 540 masses: wing 5 mm strips, fins 4 × 8, tubes 8, 4 stations, pod group, pack | — | `loads.py#build_items` | `CHECKED` |
| Method | quasi-static rigid body (d'Alembert); cut load = sum over the outboard part | — | `loads.py#solve` | `CHECKED` |
| Spanwise lift and cm | B2 AVL + XFOIL strip shape, trimmed chordwise to the CG | — | `ASM-C1-B2-SPANLOAD` | `UNVERIFIED` (B2 ran c 0.30) |
| Factor of safety / fitting / printed-bonded | 1.5 / 1.15 / 1.25 | — | `P:requirements.safety_factor_ult`, `ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR` | `PROPOSED` |
| Crash loads | ultimate as stated, no further factor | — | FAR 23.561 practice | `PROPOSED` |

## Load cases

`F` flight · `H` hover · `T` transition · `L` landing · `G` ground handling · `X` transport · `C` crash · `A`
assembly. F, H, T, L1–L5 and G form the **sizing envelope**; L6/L7 (damage), X, C and A are reported separately.
Every envelope case runs on both mass configurations.

| Case | What | Key numbers | Sizes |
|---|---|---|---|
| F1 / F2 | symmetric pull-up at VD / VA | n +3.58, V 32.1 / 22.0 m/s, L 91.4 N | spar flap bending, proof test |
| F3 | push-over at VD | n −1.58 | negative bending |
| F4 / F5 | gust peaks (Pratt, U 8 m/s at VC → 4 m/s at VD) | +3.58 / −1.58 at 24.1 m/s | n± |
| F6 | roll: full elevon at VA, ⅓ at VD, n 1 | ±25° / ±8.3° | wing torsion, elevon roots |
| F7 | rolling pull-up, ⅔ n⁺, same schedule | n 2.39 | **wing shear Vz** (F7-VA) |
| F8 | cruise 1 g, 16 m/s | reference | — |
| H1 / H2 | hover trimmed / four motors at T_lim (7° cant) | 21.1 N each, n 3.31 | in-plane spar |
| H3 / H4 | one pair at T_lim, other off, + gyro 3 rad/s | 0.37 N·m per rotor | mounts |
| H5 | right pair at T_lim, left off | in-plane yaw | **mount / motor moment** |
| H6 / H7 | diagonal pair at T_lim (yaw), cant side forces add | Q 0.42 N·m per motor | **wing torsion** (H6) |
| H8 / H9 | 8 m/s gust broadside on the wing / fins | N 17.3 / 10.9 N | out-of-plane fin loads |
| T1 / T2 / T3 | transition 45° at 15.5 m/s / flare 30° at 16 m/s, one pair + gyro | L 43.1 / 46.0 N | biaxial spar, mounts |
| L1 | level on four feet, 1.5 m/s, n_L 6, rotor lift ⅔ W, biased cartridges | upper 41.2 N, lower 35.3 N per foot | **spar, fin half, pod, feet** |
| L2 / L3 | one pair first, 10° pitch / roll error | 22.2 / 28.0 N per foot | fin halves |
| L4 / L5 | one foot first + μ 0.7 across / along the fin | 29.1 N + 20.4 N side | **fin joint moment, fin torsion** |
| L6 / L7 | wingtip TE strike / tip-over (damage) | 87 N / 4.6 J | — (feet clear 10.7°; props are the fuse) |
| G1 / G2 | lifted by the pod / carried by one upper tube end, 2 g | — | pod bond; no longer governs the fin joint |
| G3 | set down flat on the lower motor cans and feet, 2 g | 23.2 N per motor can, 2.3 N per foot | **mount / motor force** |
| X1–X4 | 0.3 m box drop: end, side, floor, lid-down; props and pack out | n_T 10.09 at 66 mm | compared with the envelope |
| C1 | 5 m/s arrested in 0.10 m (ultimate) | n_c 12.75 | pack strap, avionics |
| A1 / A2 | prop-nut torque / pack strap preload | 1.5 N·m / 40 N | mount clamp, tray |

## Flight envelope

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Stall Vs (gate, trimmed CLmax) | 11.91 | m/s | `CL-C1-VS` | `UNVERIFIED` (T-B2-STALL) |
| Manoeuvre speed VA | 21.96 | m/s | `CL-C1-VA` | `UNVERIFIED` |
| Highest level speed VH = max(pitch speed 21.8, B1 top speed) | 25.68 | m/s | `CL-C1-VH` ← `CL-B1-VMAX` | `UNVERIFIED` |
| Design dive speed VD = 1.25 × VH (to 0.1 m/s) | 32.1 vs requirement 27.2 | m/s | `CL-C1-VD` | `FAIL` −18 % → CR-C1-20 |
| Envelope VD, q | 32.1, 631 | m/s, Pa | `CL-C1-VD-ENV`, `CL-C1-Q-VD` | `CHECKED` |
| Gust peak ± (= design n±) | +3.58 / −1.58 vs 3.4 / −1.5 | — | `CL-C1-GUST-N-POS/NEG`, `CL-C1-N-LIMIT-POS/NEG` | `FAIL` −5 % (follows VD) |
| Stall-line n at VD | 7.27 | — | `CL-C1-N-STALL-VD` | `FAIL` → F4 limits (CR-C1-08) |

![V-n diagram](data/vn-diagram.svg)

`FIG C1-01 — V-n diagram at 2.6 kg: manoeuvre envelope (blue), stall lines (dashed), gust lines, gust peak (orange).`

**VD sensitivity** (`data/sensitivity_vd.json`, envelope re-run at 27.2 m/s): spar, fin joint, fin half, mounts,
pod and feet are **unchanged** (landing, handling and hover govern); wing shear Vz 33.4 → 32.3 N ult (−3 %); the
proof load 29.0 → 27.4 N per side. What VD really moves is q at VD (631 vs 453 Pa, +39 %: elevon hinge, horn, servo)
and the stall-line n (7.3 vs 5.2) that F4 must fence off.

## Rotor loads per motor

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Peak static thrust at the 9 350 rpm cap | 21.08 vs requirement 21.1 | N | `CL-C1-T-CAP` | `CHECKED` (+0.1 %) |
| Limit thrust T_lim (every case) | 21.1 | N | `CL-C1-T-LIMIT` | `UNVERIFIED` (T-C1-THRUST-FRESH) |
| Cant side force at T_lim (7°, tangential, net zero in symmetric hover) | 2.57 | N | `P:propulsion.stations.cant_deg` | `PROPOSED` |
| Reaction torque / gyroscopic moment | 0.42 / 0.37 | N·m | `CL-C1-MOTOR-TORQUE`, `CL-C1-GYRO-MOMENT` | `UNVERIFIED` |
| Prop-nut torque at set-up | 1.5 | N·m | `ASM-C1-PROP-NUT-TORQUE` | `UNVERIFIED` |

## Results by structure (envelope, both sides folded)

| Structure (consumer) | Quantity | Limit | Ultimate | Unit | Governing case | Claim |
|---|---|---|---|---|---|---|
| Spar root (C2) | bending resultant √(Mx²+Mz²) | 13.4 | 20.1 | N·m | L1 (in-plane) | `CL-C1-SPAR-MB-ULT` |
| Spar (C2) | flap bending Mx, max along span | 8.0 | 12.0 | N·m | G2 | `CL-C1-SPAR-MX-ULT` |
| Wing (C2) | torsion about the spar | 4.6 | 6.9 | N·m | H6 | `CL-C1-WING-TORSION-ULT` |
| Wing (C2) | shear Vz / in-plane Vx | 22.2 / 49.9 | 33.4 / 74.9 | N | F7-VA / L1 | `CL-C1-WING-SHEAR-ULT` |
| Fin group → wing, each side (C4, C6) | force / moment | 55.6 / 8.3 | 83.4 / 12.5 | N / N·m | L1 / L4 | `CL-C1-FINJOINT-F/M-ULT` |
| Same, joint design (× 1.15 × 1.25) | force / moment | — | 119.8 / 18.0 | N / N·m | — | `CL-C1-FINJOINT-M-DESIGN` |
| Fin + tube at the wing plane (C4) | bending / torsion (section total) | 7.7 / 6.6 | 11.6 / 9.9 | N·m | L1 / L4 | `CL-C1-FINHALF-MB-ULT`, `CL-C1-FINHALF-T-LIM/-ULT` |
| Mount → tube (C4, C6) | force / moment | 20.9 / 0.65 | 31.3 / 0.97 | N / N·m | G3 / H5 | `CL-C1-MOUNT-F/M-ULT` |
| Motor → mount screws (C6) | force | 21.2 | 31.8 | N | G3 | `CL-C1-MOTOR-F-ULT` |
| Pod → wing (C3) | force / moment | 80.1 / 2.4 | 120.2 / 3.6 | N / N·m | L1 | `CL-C1-POD-F-ULT` |
| Pack → tray, crash any axis (C3) | force (ultimate) | — | 85.0 | N | C1 | `CL-C1-PACK-CRASH-LOAD` |
| Foot → fin tip (C5) | force / side force | 40.6 / 20.4 | 60.8 / 30.5 | N | L1 (upper foot) / L4 | `CL-C1-FOOT-F-ULT`, `CL-C1-FOOT-LEVEL-UPPER` |
| Elevon panel (D6) | normal load per metre at VD, CN 1.0 | 44.4 | 66.6 | N/m | q 631 Pa | `data/envelope.json` |

![Wing spanwise envelope](data/wing-envelope.svg)

`FIG C1-02 — Ultimate spanwise moments on the spar axis, right half (left mirrored), envelope of all sizing cases.`

## Transport (D7)

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Floor drop 0.3 m on D7's cradle stroke 66 mm, η 0.5 | n_T 10.09 vs allowable 12.45 | — | `CL-C1-TRANSPORT-N`, `-N-ALLOW` | `CHECKED` (+23 %) |
| End (x) / side (y) impact allowable | 12.13 / 11.53 | — | `CL-C1-TRANSPORT-N-ALLOW-X/-Y` | `CHECKED` |
| Stroke a 0.3 m drop needs: floor / end / side | 52 / 54 / 57 | mm | `CL-C1-CRADLE-STROKE-REQ`, `CL-C1-BOX-STROKE-REQ-X/-Y` | end and side `FAIL` today (16 / 36 mm gap) → test-only |
| Lid-down allowable; pillar force per side | 12.45; 102 (limit) | —; N | `CL-C1-TRANSPORT-N-ALLOW-LID`, `CL-C1-PILLAR-F-LIM` | `CHECKED` |
| Cradle force per side: static (1 g + 5 N preload) / floor drop | 14.6 / 102 | N | `CL-C1-CRADLE-F-LIM` | `CHECKED` |
| Pad pressure, 40 × 40 mm: static / floor drop | 9.1 / 64 | kPa | `CL-C1-CRADLE-PAD-P-LIM` | C2 checks the skin and core |

The fin joint (`J-FIN` force) governs the floor and lid cases; the pod bond moment governs end and side impacts.

## Wing proof whiffletree (H1, `T-C1-WING-PROOF`)

Aircraft **inverted** on a stand under the pod (support at |y| ≤ 0.07 m), half-fins hanging free. Per side: four
40 × 40 mm sandbag pads on the lower surface over the spar (x 0.08 m) on two bars, plus an **upward relief pull R**
on the motor tube at the wing plane (sling, pulley, counterweight). R replaces the fin group's in-flight inertia
relief, which its own weight reverses when inverted. The tree reproduces F2 (n 3.58, MC-C) exactly at the pod edge
and on both sides of the fin; between them the test moment is 0.84–1.09 of the case.

| Load point (per side) | y m | Limit N | Ultimate N | Claim |
|---|---|---|---|---|
| P1 | 0.120 | 9.93 | 14.89 | `CL-C1-PROOF-Y1`, `-P1-LIM` |
| P2 | 0.260 | 7.98 | 11.97 | `CL-C1-PROOF-Y2`, `-P2-LIM` |
| P3 | 0.355 | 4.69 | 7.03 | `CL-C1-PROOF-Y3`, `-P3-LIM` |
| P4 | 0.465 | 6.40 | 9.60 | `data/whiffletree.json` |
| Sum of pads | pivot 0.273 | 28.99 | 43.48 | `CL-C1-PROOF-P-SIDE-LIM/-ULT` |
| Relief R, upward at the tube | 0.320 | 19.99 | 29.98 | `data/whiffletree.json` |
| Flap moment reproduced at the pod edge | 0.070 | 2.46 N·m | 3.70 N·m | `CL-C1-PROOF-MX-ROOT-LIM` |

Proof at **LIMIT** on the flight article (no permanent set). Ultimate only on a sacrificial wing. The tree covers the
symmetric pull-up; inboard of the fin it reaches ≥ 0.83 of the whole flight envelope, outboard of the fin the
rolling case F7-VA is 2.2 × higher (one-sided outboard proof: scale P3, P4 on one side by 2.2). Torsion and the
fin-station couples from rotor cases are proven by the twist test and `T-C1-STATION-PROOF`.

## Findings

| # | Finding | Number | Status | Action |
|---|---|---|---|---|
| 1 | B1's top level speed with the 11×5.5MR at the cap is 25.7 m/s, so VD = 1.25 VH = 32.1 m/s, above the 27.2 requirement; n± follow (3.58 / −1.58) | 32.1 vs 27.2 m/s | `FAIL` | F4 caps fixed-wing THR_MAX so VH ≤ 21.8 m/s (logs), keep 27.2; or A1 raises VD to 32.1 and n⁺ to 3.6 (CR-C1-20). Structure is insensitive; elevon and servo are not |
| 2 | Fin-collar torsion: C1 section total 6.60 N·m at μ 0.7; C4's FE collar value is internal and larger | 6.60 vs ~11.6 N·m | `PROPOSED` | C6 sizes to C4's FE re-run at μ 0.7 (CR-C1-21) |
| 3 | End and side box impacts from 0.3 m need 54 / 57 mm of stroke; the box has 16 / 36 mm of gap | 54 / 57 vs 16 / 36 mm | `FAIL` | D7: test-only + label, or foam on end and side walls (CR-C1-22) |
| 4 | Carrying by one tube end (G2) no longer sets the fin-joint moment; L4 at μ 0.7 does | 8.34 N·m (L4) | `CHECKED` | CR-C1-04 closed: a label is good practice, not a sizing need |
| 5 | Setting it down flat puts 23 N (limit, 2 g) on each lower motor can, the mount's largest force | 20.9 N mount limit | `PROPOSED` | C4/C6 size mounts to G3; flight card: lay it on its feet or on a pad, not on the motors |
| 6 | Parked on the mat it slides at μ 0.68 needed vs 0.7: margin 3 % | 0.68 vs 0.70 | `CHECKED` (thin) | keep rule S1 (lay flat above 5 m/s) |
| 7 | With 48 mm feet the wingtip TE clears a 10.7° roll error | 10.66° vs 10° | `CHECKED` (+7 %) | — |
| 8 | Stall-line n at VD 7.3 (5.2 at 27.2) | 7.27 vs 3.58 | `FAIL` | F4 airspeed and pitch limits (CR-C1-08) |

## Data files (`team/C1/data/`)

All loads are limit, SI units, aircraft frame. Cut loads are the resultant on the outboard part about the cut point.

| File | Content | Consumer |
|---|---|---|
| `wing_spanwise.csv` / `wing_envelope.csv` | every case × mass config on the spar axis every 5 mm / signed envelope + ultimate Mbend | C2, D1 |
| `fin_heightwise.csv` / `fin_envelope.csv` | fin + tube section cut at height z (tube axis), each side and half / envelope | C4, D3 |
| `joints.csv` | 6-component load at every named joint per case | C3–C6 |
| `envelope.json` | per joint class: limit, ultimate, joint design, printed/bonded design, case; landing, crash, assembly, elevon, rotor, **transport and lid**, **fin-collar torsion** | C3–C6, D5–D7 |
| `whiffletree.json` / `.csv` | proof load points, limit and ultimate, coverage per station | H1 |
| `sensitivity_vd.json` | envelope at derived VD vs requirement VD | A1, F4 |
| `feet.csv`, `cases.json`, `mass_model.csv`, `checks.json` | foot loads; case states; masses with the CG trim; self-checks | C5, D5, A3, review |

## Checks

| Check | Result | Status |
|---|---|---|
| Free-body equilibrium, every case and config | residual < 1e-12 N or N·m | `CHECKED` |
| Strip convergence, F1 root Mx at dy 10 / 5 / 2.5 mm | 3.7645 / 3.7654 / 3.7654 N·m (0.02 %) | `CHECKED` |
| Hand check, F8 root Mx (B2's own centroid) | 1.036 hand vs 1.051 model N·m (1.4 %) | `CHECKED` |
| Cant: symmetric hover net side force and roll moment | 0 (diagonal pairs cancel) | `CHECKED` |
| Proof chain `build_graph.py` | 0 C1 drift, no unknown ids; downstream C2, C4, D3, D7, H1 re-run on the new values | `CHECKED` |
| Physical tests (planned) | `T-C1-WING-PROOF`, `T-C1-FOOT-DROP`, `T-C1-THRUST-FRESH`, `T-C1-STATION-PROOF` | `PROPOSED` |

## Open issues

1. VD: finding 1 waits on A1/F4. Until then the envelope carries 32.1 m/s (conservative).
2. B2's strip loads are at c 0.30 (CR-C1-18 open). Pod lift and slipstream excluded.
3. The CG trim moves the centre group 16–18 mm: the lumped model is nose-heavy against A3's roll-up. A3's R3
   re-run should make the trim small; C1 then reads A3's pack station alone.
4. Tip-over (L7): with the 0.344 m tube the tube ends no longer stand proud of the feet; first contact is the upper
   props and motor cans (D-23 fuse). 4.6 J is an upper bound (90° rotation).
5. Quasi-static only: no dynamic overshoot, no ω² terms, no prop imbalance (C4, `R-VIBRATION`).
6. Spin senses: UR/LL vs UL/LR assumed; F4's map may swap torque, gyro and cant signs (magnitudes unchanged).
