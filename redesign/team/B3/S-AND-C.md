# K09-L stability and control (B3), R1 geometry

Status: `PROPOSED` (B3, 2026-11-09, params revision A1-R2). AVL 3.52 whole-aircraft model plus hand models for what
AVL leaves out. Re-check: `python -I redesign/team/B3/sc_analysis.py`, `python -I redesign/team/B3/run_avl_study.py`,
`python -I redesign/team/B3/draw_cg.py`, then `python -I redesign/proofs/build_graph.py` (2026-11-09: no B3 errors;
the build still fails on A1, B1, D3 and E2 drift, which those roles re-run).

**Verdict (answers CR-A1-10 / D-17 / D-21).** At R1 geometry the CG range is **0.0499–0.0553 m** (15.6–17.3 % c),
target **0.0526 m**. **A3's pack-centred CG, 0.0515 m, is inside it** (1.6 mm behind the forward limit, 3.7 mm ahead
of the aft limit), so **the pod stays at −0.105 m**. Moving it to −0.125 would put the pack-centred CG at 0.0444 m,
5.5 mm ahead of the forward limit. The pack goes **4 mm aft of the pod centre**, not 29 mm forward. The trimmed stall is
**11.90 m/s** at the target and **11.93 m/s** at the forward limit. That makes 1.3 Vs **15.51 m/s**, so set
`ARSPD_FBW_MIN` to 15.6 m/s. The 16 m/s cruise passes with 3 % margin. Two checks fail:
**(1) hover yaw**, which reaches 1.15× the 5 m/s disturbance and 1.15 rad/s² with 3° cant and the 30 % differential
cap. **7° cant** gives 2.23× and 2.24 rad/s² (CR-B3-12).
**(2) Cn_β at the aft limit and 1.3 Vs is 0.0286 /rad**, 5 % short of 0.03. Half-fins to z = ±0.21 m give 0.037
(CR-B3-14). Cruise yaw is now passively stable, so the old FAIL (−0.105 /rad) is closed.

## Model

| Item | What | Source | Status |
|---|---|---|---|
| Geometry | wing 1.15 × 0.32 m, S5010 camber line (`avl/s5010.dat` = B2's UIUC file), 4 elevon panels (hinge 0.78 c) as `elevator` (d1) and `aileron` (d2); half-fins as flat plates x 0.045…0.32, z ±0.19 at y ±0.32 | `params.json#wing`, `#fins`; `avl/k09l.avl` | `CHECKED` |
| Lattice | derivatives on the fine lattice (16 chordwise, 8 mm spanwise); trim sweeps with strip loads on the medium lattice | `avl_model.py` | `CHECKED` |
| Convergence | Xnp coarse / medium / fine 0.07365 / 0.07371 / 0.07377 m (Δ 0.018 % c); Cm_δ medium→fine 4.0 %; Cn_β Δ 2e-5 | `CL-B3-AVL-CONV` | `CHECKED` |
| Section terms (B2) | viscous Δcm −0.0103 added to AVL Cm; elevon effectiveness η 0.606 (AVL control gain, so AVL degrees are physical); clmax vs elevon (1.24 at 0°, 1.03 at −10°) | `CL-B2-DCM-VISC`, `CL-B2-ELEVON-ETA`, `ASM-B3-CLMAX-FLAP` | `UNVERIFIED` |
| Trimmed CLmax | critical-section method (B2's): AVL trims Cm + Δcm = 0 at CL 0.4–1.2, and the first strip at its local clmax sets CLmax. The AVL reference is shifted by Xnp_aero − Xnp so the props-off model has the whole aircraft's margin | `sc_analysis.py#critical_section` | `MODELLED` |
| Added by hand | Ribner prop normal force (4 × 11×5.5MR, dCN/dα 0.11 /rad per disc, upwash 1.15); tube and motor cross-flow drag in sideslip; Munk pod (pitch k 0.5, yaw k 1.0) | `flight_models.py` | `UNVERIFIED` |
| Mass | 2.6 kg gate; A3 inertias scaled by 2.6 / 2.145 | `CL-A3-IXX/IYY/IZZ`, `avl/k09l.mass` | `PROPOSED` |
| Cross-check | B2's critical-section CLmax 0.798 vs B3 0.799 at the target. AVL `MODE` (aero only) vs the B3 4×4 model: short period −3.94 ± 8.32i vs −4.21 ± 8.40i; Dutch roll −1.00 ± 3.69i vs −1.12 ± 3.35i; spiral +0.094 vs +0.172 /s (props add) | `results/study.json` | `CHECKED` |

Retired: `xfoil_elevon.py`, `xfoil/` and `avl/mh45.dat` (MH 45, R0). Nothing reads them now. B2's claims replace them.

## Neutral point and CG range

![CG stations](fig-b3-cg-stations.svg)

`FIG B3-01 — Chordwise stations at R1, drawn from results/sc_results.json and params.json by draw_cg.py.`

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP, wing + fins (AVL) | 0.0738 (23.0 % c) | m | `CL-B3-XNP-AERO` | `CHECKED` |
| NP shift: props / pod | −1.9 / −0.6 | mm | `CALC-B3-NP` | `UNVERIFIED` |
| **NP, whole aircraft** | **0.0713 (22.3 % c)** | m | `CL-B3-XNP` | `UNVERIFIED` |
| Lift slope / α0 | 3.46 /rad / −0.52° | — | `CL-B3-CLA`, `CL-B3-ALPHA0` | `CHECKED` |
| **Aft limit** (SM 5 %, `requirements.static_margin_min`) | **0.0553** (17.3 % c) | m | `CL-B3-CG-AFT` | `UNVERIFIED` |
| **Forward limit** (elevon at trimmed CLmax ≤ 50 % of travel = 12.5°, `requirements.elevon_trim_travel_max`) | **0.0499** (15.6 % c, SM 6.7 %) | m | `CL-B3-CG-FWD` | `UNVERIFIED` |
| Forward limit from Vs ≤ 12 m/s (not binding) | 0.0433 (SM 8.7 %) | m | `CALC-B3-CG-LIMITS` | `MODELLED` |
| **Target** / SM there | **0.0526** / 5.8 % | m / — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| Range width | 5.3 (≥ 4) | mm | `CL-B3-CG-WIDTH` | `UNVERIFIED` |

| CG scan (critical section, 2.6 kg) | SM 3 % | 4 % | **5 %** | 6 % | **6.7 %** | 8 % | 10 % | 12 % |
|---|---|---|---|---|---|---|---|---|
| x_cg m | 0.0617 | 0.0585 | **0.0553** | 0.0521 | **0.0499** | 0.0457 | 0.0393 | 0.0329 |
| Trimmed CLmax | 0.864 | 0.835 | 0.809 | 0.798 | 0.795 | 0.789 | 0.780 | 0.771 |
| Elevon at CLmax, deg | −6.5 | −8.1 | −9.7 | −11.3 | **−12.5** | −14.8 | −18.2 | −21.6 |
| Vs m/s | 11.44 | 11.64 | 11.83 | 11.90 | 11.93 | 11.98 | 12.04 | 12.11 |

The stall always starts at y ≈ 0.07 m, where the inboard elevon begins (B2 found the same).

### Where the A3 layout sits (D-17)

| Case | CG x m | vs range 0.0499–0.0553 | Source |
|---|---|---|---|
| A3 roll-up, pack 29 mm forward of the pod centre (today) | 0.0440 | **5.9 mm ahead of the forward limit** (`FAIL`) | `CL-B3-CG-NOW-FWD` |
| **Pack centred in the pod, pod nose −0.105** | **0.0515** | **inside** (+1.6 / +3.7 mm) | `CL-B3-CG-CENTRED-FWD/AFT` |
| Pack centred, pod nose −0.125 (D-17 fallback) | 0.0444 | 5.5 mm ahead of the forward limit: do not move | `results/study.json#layout_d17` |
| Pack for the target: centroid x = −0.001 m, 4 mm aft of the pod centre | 0.0526 | 26 mm of the ±30 mm slide left | `CL-B3-PACK-SLIDE-LEFT` |
| 680 g pack (heaviest listing), centred | ≈ 0.048 | slide it ~14 mm aft | A3 sensitivity |

Sensitivity: prop dCN/dα ±50 % moves the NP and the aft limit ∓0.9 mm. Δcm ±0.01 moves the trimmed stall by
−0.15 / +0.05 m/s and the stall trim by ±2.2°. η ±20 % changes the stall trim by ±2.3° (`results/study.json#sensitivity`).
That is the main uncertainty in the forward limit. `T-B3-TWIN-NP` and the twin's slow flight settle it.

## Trimmed stall and trim across speeds (2.6 kg, AVL trim, elevon in physical degrees)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Trimmed CLmax at target | 0.799 (elevon −11.0°, α 15.9°) | — | `CL-B3-CLMAX-TRIM`, `CL-B3-DELTA-STALL` | `UNVERIFIED` |
| **Vs at target / forward limit / aft limit** | **11.90 / 11.93 / 11.83** (≤ 12) | m/s | `CL-B3-VS-TRIM`, `CL-B3-VS-TRIM-FWD` | `UNVERIFIED` |
| **1.3 Vs, forward limit** → `ARSPD_FBW_MIN` | **15.51** (≤ 16 cruise) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |

| V m/s | 11.9 | 13 | 14 | 15 | 16 | 18 | 20 | 25 |
|---|---|---|---|---|---|---|---|---|
| CL | 0.799 | 0.669 | 0.577 | 0.503 | 0.442 | 0.349 | 0.283 | 0.181 |
| α deg (target) | 15.9 | 13.1 | 11.2 | 9.7 | **8.4** | 6.6 | 5.2 | 3.2 |
| Elevon deg, fwd / target / aft | −12.6 / −11.1 / −9.5 | −10.4 / −9.2 / −7.9 | −8.9 / −7.9 / −6.8 | −7.8 / −6.9 / −6.0 | −6.9 / **−6.1** / −5.3 | −5.5 / −4.9 / −4.3 | −4.6 / −4.1 / −3.6 | −3.1 / −2.8 / −2.5 |

Induced trim drag at 16 m/s: CDi 0.01682 trimmed vs 0.01677 clean (+0.3 %). AVL span efficiency 1.03 (inviscid,
fins as end plates).

## Control surfaces (elevons) and cruise authority

| Check | Value | Limit | Source | Status |
|---|---|---|---|---|
| Elevon area (22 % c, both panels per side) | 17.2 % of S | 15–25 % | `CL-B3-ELEVON-FRAC-MIN/MAX` | `CHECKED` |
| Trim at 1.3 Vs, worst CG (forward) | −7.3° = 29 % of travel | ≤ 50 % | `CL-B3-TRIM-USE-VT` | `UNVERIFIED` |
| Steady roll rate at 1.3 Vs, 17.7° left | 269°/s | ≥ 90°/s | `CL-B3-ROLL-RATE-VT` | `UNVERIFIED` |
| Roll at the trimmed stall, 14.0° left: pb/2V, t to 60° | 0.137, 0.67 s (τ 0.35 s) | ≥ 0.07, ≤ 1.3 s | `CL-B3-ROLL-PB2V`, `-T60` | `UNVERIFIED` |
| **Cruise motor-out roll (E1 0.22 N·m) at 1.3 Vs** | elevons give 3.38 N·m; hold needs 1.2° | ratio 15 ≥ 2 | `CL-B3-MOTOROUT-ROLL-RATIO` | `UNVERIFIED` |

| Elevon chord (target CG) | 0.18 c | **0.22 c** | 0.26 c |
|---|---|---|---|
| Area / S | 14.1 % (below the floor) | **17.2 %** | 20.3 % |
| Vs trimmed, m/s | 11.89 | **11.90** | 11.90 |
| Roll rate at 1.3 Vs after stall trim, °/s | 181 | **202** | 223 |

Keep 22 % chord, both panels and ±25° (unchanged). Chord hardly changes the stall. B2's clmax-vs-flap table is
reused for every hinge, which is approximate. The panels freeze on the twin.

## Dynamic modes at 16 m/s (CG target, props included)

| Mode | Eigenvalue /s | Meaning | Claim | Status |
|---|---|---|---|---|
| Short period | −4.21 ± 8.40i (ωn 9.4 rad/s, ζ 0.45) | well damped | `CL-B3-SP-ZETA` ≥ 0.30 | `UNVERIFIED` |
| Phugoid | −0.033 ± 0.78i | lightly damped: TECS holds it | — | `PROPOSED` |
| Roll subsidence | −3.79 | — | — | `PROPOSED` |
| **Dutch roll** | −1.12 ± 3.35i (ζ 0.32) | damped | `CL-B3-DR-ZETA` ≥ 0.08 | `UNVERIFIED` |
| Spiral | +0.172 (doubles in 4.0 s) | Cl_β +0.004 (slightly unstable dihedral effect); the FBWA roll loop holds it | `CL-B3-LAT-T2` ≥ 4 s | `UNVERIFIED` (+1 %) |

| Cn_β build-up, aft limit at 1.3 Vs (α 7.3°) | /rad | Source |
|---|---|---|
| Wing + half-fins (AVL) | +0.0372 | `CALC-B3-LATDIR` |
| 4 props (Ribner) | −0.0038 | `ASM-B3-PROP-CNA` |
| Pod (Munk, k 1.0) | −0.0040 | `ASM-B3-POD-K-YAW` |
| Tubes + motors | −0.0008 | `ASM-B3-CD-CYL` |
| **Total** | **+0.0286** (need ≥ 0.03, `R-DIRECTIONAL`) | `CL-B3-CNB` `FAIL` (−5 %) |
| Same at 16 m/s, CG target | +0.0314 | `CL-B3-CNB-CRUISE` |

| Fix (aft CG, 1.3 Vs) | Cn_β /rad | Cost |
|---|---|---|
| R1 baseline | 0.0286 | — |
| Half-fin TE +15 mm aft of the wing TE | 0.0306 | feet move 15 mm aft |
| Half-fin TE +30 mm | 0.0325 | feet move 30 mm aft |
| **Half-fins 0.21 m high (fin tips at the tube ends)** | **0.0373** | ~+6 g of foam board; same envelope (tube ends are ±0.21 already); matches D5's foot splay to z ±0.21 |

The shortfall (0.0014) is inside the model uncertainty (prop term ±0.002, pod factor). It is still a requirement
miss, so B3 asks for the fin change (CR-B3-14). Yaw by motors in fixed-wing mode is now optional damping, not a
stabiliser.

## Hover (tailsitter axes) and transition

The differential is capped at 30 % of hover thrust per motor (`R-HOVER-AUTHORITY`, `ASM-B3-HOVER-DIFF`), which is
2.03 N per motor at the gate.

| Axis (hover) | Actuator | Moment N·m (rad/s²) | 5 m/s disturbance N·m | Ratio (≥ 1.5) | Status |
|---|---|---|---|---|---|
| Pitch (cruise y) | upper vs lower pair, arm 0.19 m | 1.54 (29.8) | 0.62 (wing face, CP 0.45 c) | 2.49 | `UNVERIFIED` |
| Roll (cruise z) | left vs right pair, arm 0.32 m | 2.59 (13.9) | 0.50 (fins broadside) | 5.20 | `UNVERIFIED` |
| **Yaw (thrust axis), 3° cant** | reaction torque × 0.48 swirl recovery (B4) + cant | **0.22 (1.15)** | 0.19 (10 % gust asymmetry) | **1.15** | `FAIL` (accel and ratio) |
| Yaw, no cant | reaction torque × 0.48 | 0.065 (0.34) | 0.19 | 0.33 | — |
| Yaw, 3° cant, full differential (no 30 % cap) | dT 4.08 N | 0.45 (2.32) | 0.19 | 2.31 | info |
| **Yaw, 7° cant (CR-B3-12)** | | **0.43 (2.24)** | 0.19 | **2.23** | `MODELLED` |

The cant needed for both yaw limits is **6.1°** (`CL-B3-HOVER-CANT-REQ`). 7° costs 0.75 % of thrust: 5° gives 1.69×
but only 1.70 rad/s², and 8° gives 2.49×. Pitch trim (A3 split 1.19) uses 9.7 % of the full pitch differential
(`CL-B3-HOVER-TRIM-USE` ≤ 12.5 %). Inside the 30 % cap it takes 30 % of the pitch budget, which leaves pitch at 1.76×.
The elevons sit 46 mm outside the contracted hover wash (`CL-B3-ELEVON-WASH-GAP`; B4 gets 33 mm), so they give no
hover authority.
E1's ±30 % yaw moment of 0.149 N·m is for isolated props with Q = 0.129 N·m. B3's figure on the same basis with B4's
0.113 N·m is 0.135 N·m. Neither includes swirl recovery or cant.

| V m/s | 0 | 4 | 6 | 8 | 10 | 11 | 12 | 16 |
|---|---|---|---|---|---|---|---|---|
| Body angle α deg (level, quasi-steady) | 90 | 80 | 69 | 55 | 43 | 38 | 12 | 7 |
| T/W | 1.06 | 0.99 | 0.94 | 0.83 | 0.69 | 0.63 | 0.11 | 0.09 |
| Aero pitch moment N·m (− nose-down) | 0 | −0.41 | −0.76 | −0.99 | −1.03 | −1.00 | −0.46 | −0.49 |
| Share of motor pitch differential used | 0 | 0.10 | 0.16 | **0.19** | 0.17 | 0.13 | 0 (elevons) | 0 |

The motors use at most 19 % of the pitch differential, against an allowance of 60 % (`CL-B3-TRANS-PITCH-USE`). In
the back-transition the motors must hold up to 1.03 N·m nose-up at 8–11 m/s.

## Responses to requests addressed to B3

| Request | Answer |
|---|---|
| CR-A1-10, D-17 | Range 0.0499–0.0553, target 0.0526. The pack-centred 0.0515 is inside, so keep the pod at −0.105 and move the pack 4 mm aft of the pod centre (CR-B3-11) |
| D-21 | 1.3 Vs = 15.51 m/s at the forward limit. `ARSPD_FBW_MIN` 15.6, and 16 m/s cruise holds (CR-B3-15) |
| CR-B4-03 | Used: no elevon hover authority, swirl factor 0.48, Q 0.113 N·m, cant from `params` (3°). The 3° cant fails at 30 % differential, so 7° is requested (CR-B3-12) |
| CR-E1-04 | 0.22 N·m motor-out roll is 1.2° of elevon at 1.3 Vs; authority 3.38 N·m (ratio 15). Within authority |
| CR-A3-04 / D-18 | Split 1.19 uses 9.7 % of the pitch differential (limit 12.5 % at 1.25) |

## Open issues

1. The forward limit rests on B2's η and Δcm (`UNVERIFIED`): ±20 % on η moves the stall trim ±2.3°, about 3 mm of CG.
   The twin slow-flight and glide tests settle it before the order.
2. The hover yaw disturbance (10 % spanwise asymmetry, `ASM-B3-GUST-ASYM`) is an estimate. `T-B3-HOVER-WIND` on the twin tests it.
3. Spiral time-to-double is 4.0 s (limit 4 s). It is benign under FBWA but marginal in MANUAL.
4. The transition model is quasi-steady with no prop-wash on the wing. F4's SITL with `results/sc_results.json` is the next check.
