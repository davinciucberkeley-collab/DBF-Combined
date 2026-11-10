# K09-L stability and control (B3), R3 geometry

Status: `PROPOSED` (B3, 2026-11-09, params revision A1-R3; A3 roll-up and B4 swirl as published at 15:04). AVL 3.52
whole-aircraft model plus hand models for what AVL leaves out. Re-check: `python -I redesign/team/B3/sc_analysis.py`,
`python -I redesign/team/B3/run_avl_study.py`, `python -I redesign/team/B3/draw_cg.py`, then
`python -I redesign/proofs/build_graph.py` (2026-11-09: no B3 drift or id errors; the build fails on other roles'
drift, including A1's `CALC-A1-CG-RANGE`, which reads the new B3 CG claims).

**Verdict (answers CR-A1-26, CR-J1-11, CR-C2-03).** At R3 the CG range is **0.0495–0.0550 m** (15.5–17.2 % c),
target **0.0522 m**: 0.3 mm forward of R1, because the wider pod and the props at −0.0082 move the NP forward and the
taller fins do not touch the longitudinal NP. **The two R1 failures are closed:** Cn_β at the aft limit and 1.3 Vs is
**0.0357 /rad** with the 0.21 m half-fins (≥ 0.03), and hover yaw at 7° cant is **3.15× the 5 m/s disturbance and
3.22 rad/s²** (≥ 1.5× and 2 rad/s²; 2.23× and 2.28 rad/s² even with B4's old 0.48 swirl factor). 1.3 Vs is
**15.53 m/s**, so `ARSPD_FBW_MIN` 15.6 stands. Two new findings:
**(1) the pack at x −0.001 puts the CG 0.15 mm ahead of the aft limit** (A3 R3 roll-up, 0.0548 m). Move the pack's
nominal station to **x −0.012** (CR-B3-18).
**(2) The symmetric wing torsion mode (21.7 Hz) limits the hover pitch rate loop to a 4.5 Hz crossover** for a 6 dB gain
margin: F4's 4.0 Hz gives 7.4 dB, but the 5 Hz ceiling F4 was given leaves 5.1 dB (CR-B3-19). Yaw has 16 dB.

## 1 Model

| Item | What | Source | Status |
|---|---|---|---|
| Geometry | wing 1.15 × 0.32 m, S5010 camber line (`avl/s5010.dat`), 4 elevon panels (hinge 0.78 c) as `elevator` (d1) and `aileron` (d2); half-fins as flat plates x 0.045…0.32, z ±0.21 at y ±0.32 | `params.json#wing`, `#fins`; `avl/k09l.avl` | `CHECKED` |
| Lattice | derivatives on the fine lattice (16 chordwise, 8 mm spanwise); trim sweeps with strip loads on the medium lattice | `avl_model.py` | `CHECKED` |
| Convergence | Xnp coarse / medium / fine 0.0737 / 0.0738 / 0.0738 m (Δ 0.018 % c); Cn_β Δ < 1e-5 | `CL-B3-AVL-CONV` | `CHECKED` |
| Section terms (B2) | viscous Δcm −0.0103; elevon effectiveness η 0.606 (AVL control gain, so AVL degrees are physical); clmax vs elevon (1.24 at 0°, 1.03 at −10°) | `CL-B2-DCM-VISC`, `CL-B2-ELEVON-ETA`, `ASM-B3-CLMAX-FLAP` | `UNVERIFIED` |
| Trimmed CLmax | critical-section method (B2's): AVL trims Cm + Δcm = 0 at CL 0.4–1.2; the first strip at its local clmax sets CLmax. The AVL reference is shifted by Xnp_aero − Xnp so the props-off model has the whole aircraft's margin | `sc_analysis.py#critical_section` | `MODELLED` |
| Added by hand | Ribner prop normal force (4 × 11×5.5MR, dCN/dα 0.11 /rad per disc, upwash 1.15) at the prop plane −0.0082; tube and motor cross-flow drag in sideslip; Munk pod 0.21 × 0.14 × 0.07 (pitch k 0.5, yaw k 1.0) | `flight_models.py` | `UNVERIFIED` |
| Mass | 2.6 kg gate; A3 R3 inertias (Ixx 0.171, Iyy 0.0425, Izz 0.164 kg·m² at 2.339 kg) scaled by 2.6 / 2.339 | `CL-A3-IXX/IYY/IZZ`, `avl/k09l.mass` | `PROPOSED` |
| Hover loops | rate PID (F4 gain ratios) × Padé delay 4 ms × motor lag 40 ms × structure × gyro low-pass 40 Hz; torsion modes from C2 | `hover_loop.py` | `MODELLED` |
| Cross-check | AVL `MODE` (aero only) vs the B3 4×4 model: short period −4.10 ± 8.78i vs −4.40 ± 8.82i; Dutch roll −1.17 ± 4.13i vs −1.29 ± 3.76i; spiral +0.092 vs +0.170 /s (props add); B3's own root finder vs numpy on the loop polynomials: identical to 3 decimals | `results/study.json` | `CHECKED` |

## 2 Neutral point and CG range

![CG stations](fig-b3-cg-stations.svg)

`FIG B3-01 — Chordwise stations at R3, drawn from results/sc_results.json and params.json by draw_cg.py.`

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP, wing + fins (AVL) | 0.0738 (23.1 % c) | m | `CL-B3-XNP-AERO` | `CHECKED` |
| NP shift: props (Ribner) / pod (Munk) | −1.95 / −0.95 | mm | `CL-B3-PROP-DXNP`, `CALC-B3-NP` | `UNVERIFIED` |
| **NP, whole aircraft** | **0.07095 (22.2 % c)** | m | `CL-B3-XNP` | `UNVERIFIED` |
| Lift slope / α0 | 3.46 /rad / −0.52° | — | `CL-B3-CLA`, `CL-B3-ALPHA0` | `CHECKED` |
| **Aft limit** (SM 5 %, `requirements.static_margin_min`) | **0.05495** (17.2 % c) | m | `CL-B3-CG-AFT` | `UNVERIFIED` |
| **Forward limit** (elevon at the trimmed CLmax ≤ 12.5°, `requirements.elevon_trim_travel_max`) | **0.04953** (15.5 % c, SM 6.7 %) | m | `CL-B3-CG-FWD` | `UNVERIFIED` |
| Forward limit from Vs ≤ 12 m/s (not binding) | 0.0443 (SM 8.3 %) | m | `CALC-B3-CG-LIMITS` | `MODELLED` |
| **Target** / SM there | **0.05224** / 5.85 % | m / — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| Range width | 5.4 (≥ 4) | mm | `CL-B3-CG-WIDTH` | `UNVERIFIED` |
| For `params.json` (rounded inward) | [0.050, 0.0549], target 0.0522 | m | CR-B3-17 | `PROPOSED` |

| CG scan (critical section, 2.6 kg) | SM 3 % | 4 % | **5 %** | 6 % | **6.7 %** | 8 % | 10 % | 12 % |
|---|---|---|---|---|---|---|---|---|
| x_cg m | 0.0614 | 0.0582 | **0.0550** | 0.0518 | **0.0495** | 0.0454 | 0.0390 | 0.0326 |
| Trimmed CLmax | 0.863 | 0.833 | 0.807 | 0.796 | 0.793 | 0.787 | 0.778 | 0.769 |
| Elevon at CLmax, deg | −6.4 | −8.1 | −9.6 | −11.3 | **−12.5** | −14.8 | −18.2 | −21.5 |
| Vs m/s | 11.45 | 11.65 | 11.84 | 11.92 | 11.94 | 11.99 | 12.06 | 12.13 |

The stall always starts at y ≈ 0.07 m, where the inboard elevon begins (B2 found the same).

### 2.1 Ribner prop normal force at the aft limit (CR-J1-11)

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Prop plane ahead of the aft limit | 63.2 (J1 49 mm at R1) | mm | `CL-B3-PROP-ARM-AFT` | `CHECKED` |
| dCm/dα of the four props about the aft limit | +0.0166 (destabilising) | /rad | `CALC-B3-PROP-AFT` | `UNVERIFIED` |
| Cn_β of the four props about the aft limit | −0.0040 | /rad | `CL-B3-PROP-CNB-AFT` | `UNVERIFIED` |
| Prop normal force at 1.3 Vs | 0.070 | N/deg | `CALC-B3-PROP-AFT` | `UNVERIFIED` |
| Thrust coefficient at 1.3 Vs, Tc = T/(ρV²D²) | 0.040 (lightly loaded, Perkins f(Tc) ≈ 1.1 holds) | — | `CALC-B3-PROP-AFT` | `MODELLED` |
| SM at the aft limit if the props were left out | 5.6 % (they cost 0.6 % c = 1.9 mm of aft limit) | — | `CALC-B3-PROP-AFT` | `MODELLED` |

The prop term is in the NP, the aft limit and Cn_β (it was at R1 as well). dCN/dα ±50 % moves the aft limit ∓0.9 mm
(`results/study.json#sensitivity`).

### 2.2 Where the A3 R3 layout sits

| Case (550 g pack unless noted) | CG x m | vs range 0.0495–0.0550 | Source |
|---|---|---|---|
| **Pack at x −0.001 (D-24 nominal), A3 R3 roll-up 2.339 kg** | **0.0548** | **0.15 mm ahead of the aft limit** | `CL-B3-CG-CENTRED-AFT/-FWD`, `CL-B3-CG-NOW-*` |
| 503 g pack at −0.001 | 0.0559 | 1.0 mm behind the aft limit | A3 `cg_x_pack_light_heavy_m` |
| 680 g pack at −0.001 | 0.0519 | inside | A3 |
| Pack at its forward stop (−0.015) / aft stop (+0.007) | 0.0515 / 0.0567 | inside / 1.7 mm aft of the limit | `CALC-B3-CG-CHECK` |
| **Pack at x −0.012 (CR-B3-18)** | **0.0522 = target** | 3.1 mm of forward travel left | `CL-B3-PACK-SLIDE-LEFT` |

The pack moves the CG 0.235 mm per mm. The station has to follow the weighed pack: a 680 g pack left at −0.012 puts the
CG at 0.0489 m, 0.7 mm ahead of the forward limit. Stations that put the CG on the target: 680 g at x 0.000, 550 g at
−0.012; a 503 g pack needs −0.018, past the forward stop, so it goes on the stop (−0.015) and the CG is 0.0529 m,
inside the range. All three fit the bay's travel (−0.015 … +0.007).

## 3 Trimmed stall and trim across speeds (2.6 kg, AVL trim, elevon in physical degrees)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Trimmed CLmax at target | 0.797 (elevon −11.0°, α 15.8°) | — | `CL-B3-CLMAX-TRIM`, `CL-B3-DELTA-STALL` | `UNVERIFIED` |
| **Vs at target / forward limit / aft limit** | **11.91 / 11.94 / 11.84** (≤ 12) | m/s | `CL-B3-VS-TRIM`, `CL-B3-VS-TRIM-FWD` | `UNVERIFIED` |
| **1.3 Vs, forward limit** → `ARSPD_FBW_MIN` | **15.53** (≤ 16 cruise) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |

| V m/s | 11.9 | 13 | 14 | 15 | 16 | 18 | 20 | 25 |
|---|---|---|---|---|---|---|---|---|
| CL | 0.798 | 0.669 | 0.577 | 0.503 | 0.442 | 0.349 | 0.283 | 0.181 |
| α deg (target) | 15.8 | 13.1 | 11.2 | 9.6 | **8.4** | 6.5 | 5.2 | 3.2 |
| Elevon deg, fwd / target / aft | −12.6 / −11.0 / −9.5 | −10.4 / −9.2 / −7.9 | −9.0 / −7.9 / −6.8 | −7.8 / −6.9 / −6.0 | −6.9 / **−6.1** / −5.3 | −5.5 / −4.9 / −4.3 | −4.6 / −4.1 / −3.6 | −3.1 / −2.8 / −2.5 |

Induced trim drag at 16 m/s: CDi 0.01669 trimmed vs 0.01665 clean (+0.3 %).

## 4 Control surfaces (elevons) and cruise authority

| Check | Value | Limit | Source | Status |
|---|---|---|---|---|
| Elevon area (22 % c, both panels per side) | 17.2 % of S | 15–25 % | `CL-B3-ELEVON-FRAC-MIN/MAX` | `CHECKED` |
| Trim at 1.3 Vs, worst CG (forward) | −7.3° = 29 % of travel | ≤ 50 % | `CL-B3-TRIM-USE-VT` | `UNVERIFIED` |
| Steady roll rate at 1.3 Vs, 17.7° left | 267°/s | ≥ 90°/s | `CL-B3-ROLL-RATE-VT` | `UNVERIFIED` |
| Roll at the trimmed stall, 14.0° left: pb/2V, t to 60° | 0.137, 0.66 s (τ 0.34 s) | ≥ 0.07, ≤ 1.3 s | `CL-B3-ROLL-PB2V`, `-T60` | `UNVERIFIED` |
| Cruise motor-out roll (E1 0.23 N·m) at 1.3 Vs | elevons give 3.38 N·m; hold needs 1.1° | ratio 16 ≥ 2 | `CL-B3-MOTOROUT-ROLL-RATIO` | `UNVERIFIED` |

| Elevon chord (target CG) | 0.18 c | **0.22 c** | 0.26 c |
|---|---|---|---|
| Area / S | 14.1 % (below the floor) | **17.2 %** | 20.3 % |
| Vs trimmed, m/s | 11.91 | **11.91** | 11.92 |
| Roll rate at 1.3 Vs after stall trim, °/s | 180 | **201** | 222 |

Keep 22 % chord, both panels and ±25°. The panels freeze on the twin.

## 5 Dynamic modes at 16 m/s (CG target, props included) and directional stability

| Mode | Eigenvalue /s | Meaning | Claim | Status |
|---|---|---|---|---|
| Short period | −4.40 ± 8.82i (ωn 9.9 rad/s, ζ 0.45) | well damped | `CL-B3-SP-ZETA` ≥ 0.30 | `UNVERIFIED` |
| Phugoid | −0.034 ± 0.78i | lightly damped: TECS holds it | — | `PROPOSED` |
| Roll subsidence | −3.90 | — | — | `PROPOSED` |
| **Dutch roll** | −1.29 ± 3.76i (ζ 0.32) | damped | `CL-B3-DR-ZETA` ≥ 0.08 | `UNVERIFIED` |
| Spiral | +0.170 (doubles in 4.07 s) | Cl_β +0.004; the FBWA roll loop holds it | `CL-B3-LAT-T2` ≥ 4 s | `UNVERIFIED` (+2 %) |

| Cn_β build-up, aft limit at 1.3 Vs (α 7.3°) | /rad | Source |
|---|---|---|
| Wing + half-fins 0.21 m (AVL) | +0.0463 (0.19 m fins: +0.0375) | `CALC-B3-LATDIR`, `results/study.json` |
| 4 props (Ribner, about the aft limit) | −0.0040 | `CL-B3-PROP-CNB-AFT` |
| Pod 0.21 × 0.14 × 0.07 (Munk, k 1.0) | −0.0058 | `ASM-B3-POD-K-YAW` |
| Tubes + motors | −0.0007 | `ASM-B3-CD-CYL` |
| **Total** | **+0.0357** (≥ 0.03, `R-DIRECTIONAL`, +19 %) | `CL-B3-CNB` |
| Same at 16 m/s, CG target | +0.0390 | `CL-B3-CNB-CRUISE` |

With the R1 0.19 m half-fins and the R3 pod the total would be 0.0269. The wider pod (D-25) costs 0.0018.

## 6 Hover (tailsitter axes), torsion modes and transition

### 6.1 Control power

The differential is capped at 30 % of hover thrust per motor (`R-HOVER-AUTHORITY`), which is 2.03 N per motor at the
gate. B4's R3 swirl model (`CL-B4-YAW` 1.79) has the fin side force turning the airframe with the reaction torque;
B3 also carries B4's R0–R2 factor 0.48 as the low bracket until T-B4-YAW.

| Axis (hover) | Actuator | Moment N·m (rad/s²) | 5 m/s disturbance N·m | Ratio (≥ 1.5) | Status |
|---|---|---|---|---|---|
| Pitch (cruise y) | upper vs lower pair, arm 0.19 m | 1.54 (32.6) | 0.62 (wing face, CP 0.45 c) | 2.48 | `UNVERIFIED` |
| Roll (cruise z) | left vs right pair, arm 0.32 m | 2.59 (14.2) | 0.55 (fins 0.21 m broadside) | 4.69 | `UNVERIFIED` |
| **Yaw (thrust axis), 7° cant, B4 R3 factor 1.79** | reaction torque × 1.79 + cant | **0.61 (3.22)** | 0.19 (10 % gust asymmetry) | **3.15** | `UNVERIFIED` |
| Yaw, 7° cant, low bracket 0.48 | | 0.43 (2.28) | 0.19 | 2.23 | `UNVERIFIED` (`CL-B3-HOVER-YAW-*-LOW`) |
| Yaw, no cant, factor 1.79 | | 0.24 (1.28) | 0.19 | 1.26 | info |

The cant gives 60 % of the yaw moment. With B4's R3 factor 2.6° of cant would do (`CL-B3-HOVER-CANT-REQ`); with the
low bracket 6.1° (R1). 7° is kept: it covers both. Pitch trim (A3 split 1.19) uses 9.5 % of the full pitch
differential (`CL-B3-HOVER-TRIM-USE` ≤ 12.5 %). The elevons sit 46 mm outside the contracted hover wash
(`CL-B3-ELEVON-WASH-GAP`), so they give no hover authority.

### 6.2 Rate loops with the wing torsion modes (CR-C2-03, D-45)

C2's first wing modes are torsion with the fin stations rocking about the spar. Hover pitch (upper vs lower pairs)
drives the **symmetric** mode, 21.7–27 Hz: the motors twist the stations against the rest of the airframe and the pod
gyro sees the body side of the spring (two-inertia, non-collocated). Hover yaw (diagonal pairs) drives the
**antisymmetric** mode, 11.7–14.9 Hz: the node is at the centreline, so the gyro sees nothing directly, but the twist
tilts each station's thrust and adds a yaw moment 4 T y θ. With F4's motor map (UR and LL CW seen from the nose, cant
aiding the reaction torque) that moment adds to the control moment (σ = +1); σ = −1 is checked as well.

Loop: F4's PID ratios (pitch P = I = 0.08, D 0.002, D filter 32 Hz; yaw P 0.40, I 0.04) scaled to F4's crossovers
(pitch 4.0 Hz, yaw 1.8 Hz), 4 ms delay, 40 ms motor lag, 40 Hz gyro filter, modal damping 2 %. Margins are the minimum
over every −180° and 0 dB crossing, and the closed-loop roots are checked.

| Loop (worst corner) | Gain margin dB (≥ 6) | Phase margin deg (≥ 45) | Rigid GM / PM | Max crossover for 6 dB / 45° | Claim | Status |
|---|---|---|---|---|---|---|
| **Pitch, 21.7 Hz mode, 4.0 Hz** | **7.4** (27 Hz: 10.4) | 58.6 | 14.4 / 59.2 | **4.5 Hz** | `CL-B3-FLEX-GM-PITCH`, `-PM-PITCH`, `CL-B3-XOVER-MAX-PITCH` | `MODELLED` |
| Pitch at the 5 Hz ceiling | 5.1 (`FAIL` vs 6) | 53.1 | — | — | `CALC-B3-HOVER-FLEX` | `MODELLED` |
| **Yaw, 11.7 Hz mode, 1.8 Hz** | **16.3** (σ −1: 15.9) | 55.2 | 18.7 / 58.9 | **2.4 Hz** (rigid PM binds: no D) | `CL-B3-FLEX-GM-YAW`, `-PM-YAW`, `CL-B3-XOVER-MAX-YAW` | `MODELLED` |
| Static twist effect on hover yaw power | +16 % (not credited) | | | | `CL-B3-HOVER-YAW-FLEX-STATIC` | `MODELLED` |

| Pitch loop sensitivity at 4.0 Hz (21.7 Hz mode) | GM dB | PM deg |
|---|---|---|
| Baseline | 7.4 | 58.6 |
| Modal damping 1 % / 3 % | 7.2 / 7.5 | 58.6 |
| Motor lag 25 ms / 60 ms | **4.2** / 9.0 | 71.5 / 47.4 |
| Gyro filter 20 Hz / 80 Hz | 8.0 / **2.7** | 50.0 / 62.8 |
| D filter 20 Hz | 8.5 | 56.9 |
| Crossover 3 Hz / 5 Hz | 10.2 / 5.1 | 64.0 / 53.1 |

The pitch margin is set by the gain rise below the mode, 1/(1 − (f/f_mode)²), which does not depend on the station
inertia. F4 should hold the pitch crossover at or below 4.5 Hz, keep the gyro filter at 40 Hz or lower, measure the
motor lag on the stand, and add a static notch at the tapped symmetric frequency before raising pitch gains
(CR-B3-19).

### 6.3 Transition (quasi-steady, level)

| V m/s | 0 | 4 | 6 | 8 | 10 | 11 | 12 | 16 |
|---|---|---|---|---|---|---|---|---|
| Body angle α deg | 90 | 80 | 69 | 55 | 43 | 38 | 12 | 7 |
| T/W | 1.06 | 0.99 | 0.94 | 0.83 | 0.69 | 0.63 | 0.11 | 0.09 |
| Aero pitch moment N·m, forward limit (− nose-down) | 0 | −0.43 | −0.79 | −1.04 | −1.09 | −1.06 | −0.53 | −0.56 |
| Share of motor pitch differential used | 0 | 0.09 | 0.15 | **0.20** | 0.18 | 0.15 | 0 (elevons) | 0 |

The motors use at most 20 % of the pitch differential (`CL-B3-TRANS-PITCH-USE` ≤ 60 %). In the back-transition they
hold up to 1.09 N·m nose-up at 8–11 m/s.

## 7 Responses to requests addressed to B3

| Request | Answer |
|---|---|
| CR-A1-26 | Re-run at R3 done; claim ids unchanged (`CL-B3-CG-FWD/-AFT/-TARGET`, `CL-B3-CNB`, `CL-B3-HOVER-YAW-*`, `CL-B3-VT-TRIM`). New params values in CR-B3-17; pack station in CR-B3-18 |
| CR-J1-11 | Prop normal force at the 63 mm arm is in the NP, the aft limit and Cn_β; reported at the aft limit with elevons neutral (section 2.1, `CL-B3-PROP-*`) |
| CR-C2-03 | Torsion modes in the hover pitch and yaw loops (section 6.2): pitch 7.4 dB at 4 Hz, yaw 16 dB; pitch crossover ≤ 4.5 Hz (CR-B3-19) |
| CR-B4 (R3 swirl) | Used `CL-B4-YAW` 1.79 and `CL-B4-HOVER-Q` 0.114 N·m; 0.48 kept as a bracket (CR-B3-20) |

## 8 Open issues

1. **The aft CG margin with the pack at −0.001 is 0.15 mm.** Until A1/A3/D2 move the pack mark to −0.012 (CR-B3-18),
   the as-built aircraft may balance behind the aft limit. T-B3-CG-BALANCE decides on the real aircraft.
2. The forward limit rests on B2's η and Δcm (`UNVERIFIED`): ±20 % on η moves the stall trim ±2.3°, about 3 mm of CG.
3. The hover pitch loop margin depends on the motor lag (40 ms, `UNVERIFIED`) and the 21.7 Hz mode (C2 model): both are
   measured before the first hover (stand test, T-C2-TAP-TEST).
4. The hover yaw factor spans 0.48–1.79 between B4's two models; both pass at 7°.
5. Spiral time to double 4.07 s (limit 4 s): benign under FBWA, marginal in MANUAL.
6. The transition model is quasi-steady with no prop wash on the wing. F4's SITL with `results/sc_results.json` is the
   next check.
