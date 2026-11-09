# Loads — K09-L quad tailsitter

Owner: C1 (loads engineer). Status: `CHECKED` against the calculation (equilibrium, convergence, hand check);
inputs are `PROPOSED`/`UNVERIFIED` (thrust table, CLmax, masses), so every load is `UNVERIFIED` until B2, E1/H1
and A3 replace them. Re-run in 1 s: `python -I redesign/team/C1/loads.py`, then
`python -I redesign/proofs/build_graph.py` (OK, 0 drift).

Every number below is a **limit** load (largest expected in service) unless marked ultimate. Ultimate = 1.5 ×
limit. Frame: x aft, y right, z up in cruise (`params.json#frame`); in hover +x points at the ground.

## Basis

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design mass | 2.600 (gate) | kg | `P:requirements.mtow_gate_kg` | `PROPOSED` |
| Mass configurations | MC-C: gap to the gate (447 g) in the pod; MC-P: every item × 1.21 | — | `data/mass_model.csv` | `PROPOSED` |
| Lumped model | 540 masses: wing in 5 mm strips, fins 4 × 8, tubes 8, 4 stations, pod group | — | `loads.py#build_items` | `CHECKED` |
| Method | quasi-static rigid body (d'Alembert); cut load = sum over the outboard part | — | `loads.py#solve` | `CHECKED` |
| Spanwise lift | Schrenk (mean of planform and elliptic), trimmed chordwise to the CG | — | `SRC-C1-SCHRENK` | `PROPOSED` (B2's AVL supersedes) |
| Factor of safety | 1.5 | — | `ASM-A2-SAFETY-FACTOR` | `PROPOSED` |
| Fitting factor (every joint) | 1.15 | — | `ASM-C1-FITTING-FACTOR` (FAR 23.625) | `PROPOSED` |
| Printed PETG / bond into foam | 1.25 on top | — | `ASM-C1-PRINTED-FACTOR` | `UNVERIFIED` (C6 coupons) |
| Crash loads | ultimate as stated, no further factor | — | FAR 23.561 practice | `PROPOSED` |
| Fatigue | not a design case (< 50 flight hours) | — | — | `PROPOSED` |

## Load cases

`F` flight · `H` hover · `T` transition · `L` landing · `G` ground handling · `X` transport · `C` crash · `A`
assembly. Cases F, H, T, L1–L5 and G form the **sizing envelope**; L6/L7 (damage), X, C and A are reported
separately. Every envelope case runs on both mass configurations.

| Case | What | Key numbers | Sizes |
|---|---|---|---|
| F1 / F2 | symmetric pull-up at VD / VA | n = +3.0, V 22.4 / 20.1 m/s | spar flap bending, wing shear |
| F3 | push-over at VD | n = −1.5 | negative bending |
| F4 / F5 | vertical gust peak (Pratt, stall-limited) | n +2.92 at 19.8 m/s; −1.06 at 17.9 m/s; U 8 / 4 m/s | covered by F1/F3 |
| F6 / F7 | full roll elevon ±25° at VD, n = 1 / rolling pull-up n = 2.0 | dCl = 1.10 per elevon strip | wing torsion, elevon roots |
| F8 | cruise 1 g at 15 m/s | reference, deflection check | — |
| H1 / H2 | hover trimmed / all four motors at T_lim | T_lim = 17.8 N each, n_hover = 2.80 | in-plane spar, mounts |
| H3 / H4 | upper / lower pair at T_lim, other pair off, + gyro at 3 rad/s | M_gyro = 0.43 N·m per rotor | fin pitch moment, mounts |
| H5 | right pair at T_lim, left off | in-plane yaw | spar in-plane |
| H6 / H7 | diagonal pair at T_lim (yaw) | Q = 0.45 N·m per motor | wing torsion (opposite fin moments), mounts |
| H8 / H9 | hover in an 8 m/s gust broadside on the wing / on the fins | N = 16.2 / 14.3 N, lean 40° / 34° | out-of-plane fin loads |
| T1 | transition at 45°, CLmax at 1.3 Vs (15.05 m/s), four motors at T_lim | L = 43.1 N | biaxial spar bending |
| T2 / T3 | back-transition flare at 30°, CLmax at 15 m/s, one pair at T_lim + gyro | — | mount moments |
| L1 | level landing on four feet, 1.5 m/s sink, n_L = 6, rotor lift 2/3 W | 38.2 N per foot | spar in-plane, pod, fin joint force |
| L2 / L3 | one foot pair first, 10° pitch / roll error | 30.3 / 29.0 N per foot | fin halves |
| L4 / L5 | one foot first + friction 0.5 across / along the fin | 36.3 N + 18.1 N side | fin out-of-plane bending, torsion |
| L6 | wingtip TE strikes first (damage case) | 91 N at the TE tip | — (removed by CR-C1-01) |
| L7 | tip-over onto the upper motor-tube ends (damage case) | 3.5 J, 1.9 m/s at the tube end | — (see findings) |
| G1 | lifted by the pod, 2 g | handling factor 2.0 | pod bond |
| G2 | carried by one upper motor tube, 2 g | 51 N at the tube end | fin joint moment, fin half (CR-C1-04) |
| G3 | set down flat on lower tube ends and feet, 2 g | 16.8 N per tube end | lower tube ends |
| X1–X3 | 0.3 m box drop along x, y, z; spar cradles at y ±0.20 m react it, props and pack out | n_T = 31 with 20 mm foam | compared with the envelope (CR-C1-05) |
| C1 | crash 5 m/s arrested in 0.10 m, any axis (ultimate) | n_c = 12.75 | pack strap, avionics mounts |
| A1 / A2 | prop-nut torque at set-up / pack strap preload | 1.5 N·m about the shaft / 40 N | mount torsion, tray |

## Flight envelope

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Stall Vs (gate, CLmax 0.9) | 11.58 | m/s | `CALC-C1-VN` | `UNVERIFIED` (CLmax) |
| Manoeuvre speed VA | 20.06 | m/s | `CL-C1-VA` | `UNVERIFIED` |
| Prop pitch speed at T_lim | 17.9 | m/s | `CALC-C1-ROTOR` | `UNVERIFIED` |
| Design dive speed VD = 1.25 × 17.9 | 22.39 | m/s | `CL-C1-VD` | `UNVERIFIED` |
| Limit n positive / negative | +3.0 / −1.5 | — | `CL-C1-N-LIMIT-POS/NEG` | `CHECKED` (gust stays below) |
| Gust peak positive / negative | +2.92 / −1.06 | — | `CL-C1-GUST-N-POS/NEG` | `UNVERIFIED` (a = 3.59 /rad, μ = 11.4, kg = 0.60) |
| Stall-line n at VD | 3.74 | — | `CL-C1-N-STALL-VD` | `FAIL` against 3.0 → F4 limits (CR-C1-08) |

![V-n diagram](data/vn-diagram.svg)

`FIG C1-01 — V-n diagram at 2.6 kg: manoeuvre envelope (blue), stall lines (dashed), gust lines, gust peak (orange).`
Below about 19 m/s the 8 m/s gust is stall-limited, so the manoeuvre case governs.

## Rotor loads per motor

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Limit thrust T_lim = 1.15 × 1.58 kgf (fresh pack) | 17.8 | N | `CL-C1-T-LIMIT` | `UNVERIFIED` (H1 at 16.8 V) |
| Rotor speed at T_lim | 9 400 | rpm | `CALC-C1-ROTOR` | `UNVERIFIED` |
| Reaction torque | 0.45 | N·m | `CL-C1-MOTOR-TORQUE` | `UNVERIFIED` |
| Gyroscopic moment at 3 rad/s | 0.43 | N·m | `CL-C1-GYRO-MOMENT` | `UNVERIFIED` |
| Prop-nut torque at set-up | 1.5 | N·m | `ASM-C1-PROP-NUT-TORQUE` | `UNVERIFIED` — governs mount torsion about the shaft |

## Results by structure (envelope, both sides folded)

| Structure (consumer) | Quantity | Limit | Ultimate | Unit | Governing case | Claim |
|---|---|---|---|---|---|---|
| Spar root (C2) | bending resultant √(Mx²+Mz²) | 13.8 | 20.7 | N·m | L1 (in-plane) | `CL-C1-SPAR-MB-ULT` |
| Spar (C2) | flap bending Mx, max along span | 8.7 | 13.1 | N·m | G2 at y = 0.32 m | `CL-C1-SPAR-MX-ULT` |
| Spar root (C2) | flight-only flap bending Mx | 4.2 | 6.4 | N·m | F1 | `data/joints.csv` |
| Wing (C2) | torsion about the spar | 5.6 | 8.5 | N·m | F7 | `CL-C1-WING-TORSION-ULT` |
| Wing (C2) | shear Vz / in-plane shear Vx | 24.2 / 50.2 | 36.4 / 75.3 | N | F7 / L1 | `CL-C1-WING-SHEAR-ULT` |
| Fin group → wing, each side (C4, C6) | force / moment | 55.6 / 10.7 | 83.4 / 16.1 | N / N·m | L1 / G2 | `CL-C1-FINJOINT-F/M-ULT` |
| Same, if lifting by a tube is ruled out | moment | 7.6 | 11.3 | N·m | L4 | `CL-C1-FINJOINT-M-FLIGHT-LIM` |
| Same, joint design (× 1.15 × 1.25) | force / moment | — | 119.8 / 23.1 | N / N·m | — | `CL-C1-FINJOINT-M-DESIGN` |
| Fin + tube at the wing plane (C4) | bending / torsion | 8.9 / 7.5 | 13.3 / 11.2 | N·m | G2 / L4 | `CL-C1-FINHALF-MB-ULT` |
| Mount → tube (C4, C6) | force / moment | 16.4 / 0.64 | 24.6 / 0.96 | N / N·m | H6 / T3 | `CL-C1-MOUNT-F/M-ULT` |
| Motor → mount screws (C6) | force / moment | 16.6 / 0.64 | 24.9 / 0.95 | N / N·m | H6 / T3 | `CL-C1-MOTOR-F-ULT` |
| Pod → wing (C3) | force / moment | 82.5 / 2.0 | 123.7 / 3.0 | N / N·m | L1 | `CL-C1-POD-F-ULT` |
| Pack → tray, flight and landing (C3) | force | 42.9 | 64.3 | N | L1 | `data/envelope.json` |
| Pack → tray, crash any axis (C3) | force (ultimate) | — | 85.0 | N | C1, 680 g pack × 12.75 g | `CL-C1-PACK-CRASH-LOAD` |
| Foot → fin tip (C5) | force | 40.3 | 60.4 | N | L5 | `CL-C1-FOOT-F-ULT` |
| Elevon panel, hinge tape and horn (D6) | normal load per metre of span at VD | 20.3 | 30.4 | N/m | CN 1.0 at q 307 Pa | `data/envelope.json` |

![Wing spanwise envelope](data/wing-envelope.svg)

`FIG C1-02 — Ultimate spanwise moments on the spar axis, right half (left mirrored), envelope of all sizing cases.`
The spar is sized by landing and handling, not by flight: the four motor stations at y = ±0.32 m relieve
the flight bending (F1 root Mx is only 4.2 N·m), while landing on the fin tips decelerates the 1.3 kg pod group
in the wing plane (L1 root Mz 13.8 N·m).

## Findings

| # | Finding | Number | Status | Action |
|---|---|---|---|---|
| 1 | The wing TE tip touches the ground at a 2.2° roll error (feet protrude 10 mm, tip is 0.255 m outboard of the feet); with the 10° attitude error the wingtip, not a foot, lands first | 2.2° vs 10° | `FAIL` | feet protrude ≥ 45 mm beyond the TE (CR-C1-01); tip-over stays 33.7° ≥ 30° |
| 2 | A 10 mm foot gives n_L = 23 at 1.5 m/s sink (148 N per foot); n_L ≤ 6 needs a 40 mm stroke (η 0.5) or 25 mm with a constant-force crush core (η 0.8) | 23.3 vs 6 | `FAIL` | CR-C1-01 |
| 3 | Parked on its feet, motors off, the aircraft tips at 10.3 m/s wind but slides at 8 m/s (μ needed 0.64 > 0.5); at the 5 m/s card limit μ = 0.25 is enough | 0.64 vs 0.5 | `FAIL` (8 m/s) | CR-C1-02 |
| 4 | Tip-over onto the upper tube ends releases 3.5 J at 1.9 m/s; a 10 mm contact gives ~690 N, beyond any sensible station design | 3.5 J | damage case | accept props/mounts as replaceable; keep tip-over ≥ 30° (CR-C1-03) |
| 5 | Lifting by one motor tube (G2) sets the fin-joint moment: 10.7 N·m vs 7.6 N·m without it | +42 % | `PROPOSED` | carry handle + label, or C4 sizes to G2 (CR-C1-04) |
| 6 | A 0.3 m box drop on 20 mm foam gives 31 g; the airframe tolerates 9.7 g (pod bond in the y-drop governs, then the fin joint at 11.9 g) | 31 vs 9.7 | `FAIL` | ≥ 69 mm stroke, or a cradle under the pod, or a 0.087 m drop limit (CR-C1-05) |
| 7 | Above VA (20.1 m/s) a full pull can reach 3.74 g before stall | 3.74 vs 3.0 | `FAIL` | F4 airspeed and pitch limits (CR-C1-08) |
| 8 | Prop-nut tightening (1.5 N·m) is 3 × the motor reaction torque: the mount-to-tube joint must not rotate under it | 1.5 vs 0.45 N·m | `PROPOSED` | C6 sizes the mount clamp to 1.5 × 1.5 N·m |

## Data files (`team/C1/data/`)

All loads are limit, SI units, aircraft frame. Cut loads are the resultant on the outboard part about the cut
point, i.e. the load the cut passes inboard.

| File | Content | Columns | Consumer |
|---|---|---|---|
| `wing_spanwise.csv` | every case × mass config, cut on the spar axis (x 0.08, z 0) every 5 mm, left half at −y | `case, mass_config, family, y_m, Fx…Mz, Mbend_Nm` | C2, D1 |
| `wing_envelope.csv` | signed max/min of each component per station + governing case (left half mirrored), ultimate Mbend | `y_m, <comp>_max/min_limit/_case …` | C2 |
| `fin_heightwise.csv` | fin + tube section cut at height z (reference point on the tube axis x −0.10), each side and half | `case, …, side, half, z_cut_m, Fx…Mz, Mbend_Nm` | C4, D3 |
| `fin_envelope.csv` | fin + tube envelope per height (bending, torsion, shears, axial), limit and ultimate | — | C4 |
| `joints.csv` | 6-component load at every named joint (fin root, fin halves, motor/mount ×4, feet ×4, pod, pack, spar root), per case | `…, joint, Fx…Mz, F_res_N, M_res_Nm, Mbend_Nm` | C3, C4, C5, C6 |
| `envelope.json` | per joint class: limit, ultimate, joint design, printed/bonded design, governing case; landing, crash, assembly, elevon, rotor, transport numbers | — | C3–C6, D5–D7 |
| `feet.csv` | foot-to-fin load per foot per case | — | C5, D5 |
| `cases.json` | per case: CG, rigid-body accelerations, gravity vector, case inputs | — | review |
| `mass_model.csv` | the lumped masses grouped, both configurations | — | A3 cross-check |
| `checks.json` | equilibrium residual, strip convergence, hand check | — | J6 |

## Checks

| Check | Result | Status |
|---|---|---|
| Free-body equilibrium, every case and config | residual 1.5e-12 N or N·m | `CHECKED` |
| Strip convergence, F1 root Mx at dy 10 / 5 / 2.5 mm | 4.2393 / 4.2391 / 4.2387 N·m (0.01 %) | `CHECKED` |
| Hand check, F8 root Mx = W/2 · ȳ_Schrenk − Σ m g y | 1.4128 hand vs 1.4130 model N·m (0.01 %) | `CHECKED` |
| Proof chain `build_graph.py` | OK, every stored number re-computes | `CHECKED` |
| Physical tests (planned) | `T-C1-WING-PROOF`, `T-C1-FOOT-DROP`, `T-C1-THRUST-FRESH`, `T-C1-STATION-PROOF` | `PROPOSED` |

## Open issues

1. Inputs to replace: CLmax 0.9, CLmin 0.4, a0, elevon effectiveness, Cm0 (B2, CR-C1-09); thrust at 16.8 V (E1/H1, CR-C1-07); real masses (A3).
2. The fin–tube–saddle load path is undesigned (P25): loads are given at the fin-group resultant and at the fin + tube section; C4 splits them between board, tube and saddle.
3. Quasi-static only: no dynamic overshoot, no ω² terms (0.2 g at 3 rad/s), no prop imbalance (C4 owns vibration, `R-VIBRATION`).
4. Rotor spin senses UR/LL vs UL/LR assumed; F4's motor map may swap the sign of torque and gyro terms (magnitudes unchanged).
