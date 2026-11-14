# K09-L stability and control (B3), R4 re-run

> **V1 verification (2026-11-10) supersedes §2 (CG range) and the spiral line of §5.** With A3-R6a's CG 18.5 mm above
> the chord plane (this report assumes 0) the range is 0.0466–0.0514 m, A3's CG fails SM 5 % by 0.77 mm and spiral t2
> is 3.51 s. See `SIMULATION-REPORT.md` and CR-B3-25 / -26.

Status: `PROPOSED` (B3, 2026-11-10, params A1-R4a, A3-R5 roll-up, B4 R3 swirl, D6 R3 elevon, C2 torsion modes, F4 R4
crossovers, all read live from the claim graph). AVL 3.52 whole-aircraft model plus hand models for what AVL leaves
out. Re-check: `python -I redesign/team/B3/sc_analysis.py`, `python -I redesign/team/B3/run_avl_study.py`,
`python -I redesign/team/B3/draw_cg.py`, then `python -I redesign/proofs/build_graph.py`. On 2026-11-10 there is no
`CALC-B3-*` drift and no B3 id error. The build still fails on other roles' drift. Two of those calcs read B3 claims:
A1's `CALC-A1-CG-RANGE` (it carries the R3 range) and C5's `CALC-C5-STANCE` (it reads the new target and limits).
CR-B3-22 asks both roles to re-run.

**Verdict (answers the R4 forward of CR-A3-23, CR-A2-19, CR-B4-13, CR-C2-03, CR-D6-08, CR-B3-19/20/21).**
Re-run on A3-R5 (2.323 kg basic, Ixx/Iyy/Izz 0.1733 / 0.0448 / 0.1674 kg·m², split 1.216). The aft limit is unchanged
at **0.0549 m**. **The forward limit moves 1.3 mm aft, to 0.0509 m.** D6's elevon effectiveness (0.973 at the 12 m/s
stall) and half of D6's 0.84° free play now count against the 12.5° trim budget, so 12.08° is left at the trimmed
CLmax. The range is **0.0509–0.0549 m** (15.9–17.2 % c), **4.05 mm wide** against a 4 mm minimum. The target is
**0.0529 m** (SM 5.6 %). A1's carried 0.050 forward value is now 0.85 mm ahead of the forward limit, so A1 narrows
the range (CR-B3-22). The D-47 bay works: with the 550 g pack at its −0.022 datum the CG is 0.0525 m, 1.6 mm behind the
forward limit and 2.4 mm ahead of the aft limit. Every 503 / 550 / 680 g pack at its spacer station keeps 1.0 mm or
more to both limits. Everything else passes:

- Cn_β 0.0354 /rad at the aft limit and 1.3 Vs (limit 0.03).
- 1.3 Vs = 15.51 m/s, so `ARSPD_FBW_MIN` 15.6 stands.
- Hover yaw at 7° cant: 2.87× the 5 m/s disturbance and 2.88 rad/s² on B4's low factor 1.40. The cant needed on that
  factor is 3.8°.
- The 11.7–14.9 Hz antisymmetric torsion band leaves the yaw loop at least 12.8 dB / 45.9° even at its 2.4 Hz
  crossover ceiling.
- The symmetric mode still caps the hover pitch crossover at 4.5 Hz. F4's 2.6 Hz has 11.6 dB.

The task text gave a CG of 0.0577 m. That is the pre-D-47 bay (pack at −0.001, the "pre-D-47" case in C5's stance
table). It is not A3-R5's published `CL-A3-CG-X` (16.4 % c = 0.0525 m). The task's inertia values (0.1746 / 0.0423 /
0.1654) and split 1.214 also differ by 1–6 % from A3's published claims, which are what the graph links. B3 uses the
claims.

## 1 Model

| Item | What | Source | Status |
|---|---|---|---|
| Geometry | wing 1.152 × 0.32 m, S5010 camber line (`avl/s5010.dat`), 4 elevon panels (hinge 0.78 c) as `elevator` (d1) and `aileron` (d2); half-fins as flat plates at y ±0.32, z ±0.21 | `params.json#wing`, `#fins`; `avl/k09l.avl` | `CHECKED` |
| Lattice | derivatives on the fine lattice; trim sweeps with strip loads on the medium lattice | `avl_model.py` | `CHECKED` |
| Convergence | Xnp coarse / medium / fine 0.07371 / 0.07379 / 0.07385 m (Δ 0.018 % c); Cn_β Δ 2e-5 | `CL-B3-AVL-CONV` | `CHECKED` |
| Section terms (B2) | viscous Δcm, elevon η 0.606 (AVL gain, so AVL degrees are physical), clmax vs elevon | `CL-B2-DCM-VISC`, `CL-B2-ELEVON-ETA`, `ASM-B3-CLMAX-FLAP` | `UNVERIFIED` |
| **Elevon mechanics (D6, new at R4)** | effectiveness e = 1 − loss·(V/VA)², loss = max(out 0.079, in 0.071) at VA 20.5 m/s, so e = 0.921 at VA, 0.973 at the 12 m/s stall and 0.955 at 1.3 Vs. AVL sees gain × deflection, so the commanded deflection is δ_AVL / e. Free play 0.84°: trim is charged half the band (`ASM-B3-SLOP-TRIM-FRAC` 0.5, servo neutral set at the band centre by T-D6-THROW), roll is charged the full band | `CL-D6-EFF-LOSS-OUT/-IN`, `CL-D6-SLOP`, `ASM-F4-VA-SCHED` | `UNVERIFIED` |
| Trimmed CLmax | critical-section method (B2's): AVL trims Cm + Δcm = 0 at CL 0.4–1.2; the first strip at its local clmax sets CLmax; the AVL reference is shifted by Xnp_aero − Xnp | `sc_analysis.py#critical_section` | `MODELLED` |
| Added by hand | Ribner prop normal force at the prop plane −0.0077 (D-51); tube and motor cross-flow drag; Munk pod (D-47 pod, nose −0.130, length 0.225) | `flight_models.py` | `UNVERIFIED` |
| Mass | 2.6 kg gate; A3-R5 inertias (Ixx 0.1733, Iyy 0.0448, Izz 0.1674 kg·m² at 2.323 kg) scaled by 2.6 / 2.323 (`avl/k09l.mass`: 0.1940 / 0.0495 / 0.1881) | `CL-A3-IXX/IYY/IZZ`, `CL-A3-MASS-BASIC` | `PROPOSED` |
| Hover loops | rate PID (F4 gain ratios) × Padé delay 4 ms × motor lag 40 ms × structure × gyro low-pass 40 Hz; torsion modes from C2 | `hover_loop.py` | `MODELLED` |
| Cross-check | AVL `MODE` (aero only) vs the B3 4×4 model with props: short period −4.01 ± 8.45i vs −4.27 ± 8.39i; Dutch roll −1.15 ± 4.04i vs −1.28 ± 3.65i; spiral +0.093 vs +0.170 /s (the props add the difference) | `results/study.json` | `CHECKED` |

## 2 Neutral point and CG range

![CG stations](fig-b3-cg-stations.svg)

`FIG B3-01 — Chordwise stations at R4, drawn from results/sc_results.json and params.json by draw_cg.py.`

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP, wing + fins (AVL) | 0.07385 (23.1 % c) | m | `CL-B3-XNP-AERO` | `CHECKED` |
| NP shift: props (Ribner) / pod (Munk) | −1.94 / −1.01 | mm | `CL-B3-PROP-DXNP`, `CALC-B3-NP` | `UNVERIFIED` |
| **NP, whole aircraft** | **0.07090 (22.2 % c)** | m | `CL-B3-XNP` | `UNVERIFIED` |
| Lift slope / α0 | 3.46 /rad / −0.52° | — | `CL-B3-CLA`, `CL-B3-ALPHA0` | `CHECKED` |
| **Aft limit** (SM 5 %) | **0.05490** (17.2 % c) | m | `CL-B3-CG-AFT` | `UNVERIFIED` |
| **Forward limit** (commanded elevon at the trimmed CLmax + ½ free play ≤ 12.5°) | **0.05085** (15.9 % c, SM 6.3 %) | m | `CL-B3-CG-FWD` | `UNVERIFIED` |
| Forward limit with no D6 terms (R3 basis) / full play band charged | 0.04947 / 0.05160 | m | `CALC-B3-CG-LIMITS` | `MODELLED` |
| Forward limit from Vs ≤ 12 m/s (does not bind) | 0.0442 (SM 8.3 %) | m | `CALC-B3-CG-LIMITS` | `MODELLED` |
| **Target** / SM there | **0.05287** / 5.63 % | m / — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| Range width | **4.05 (≥ 4, +1 %)** | mm | `CL-B3-CG-WIDTH` | `UNVERIFIED` (thin) |
| For `params.json` (rounded inward) | [0.0509, 0.0549], target 0.0529 | m | CR-B3-22 | `PROPOSED` |

| CG scan (critical section, 2.6 kg) | SM 3 % | 4 % | **5 %** | 6 % | **6.3 %** | 7 % | 8 % | 10 % |
|---|---|---|---|---|---|---|---|---|
| x_cg m | 0.0613 | 0.0581 | **0.0549** | 0.0517 | **0.0509** | 0.0485 | 0.0453 | 0.0389 |
| Trimmed CLmax | 0.863 | 0.833 | 0.807 | 0.796 | 0.795 | 0.792 | 0.787 | 0.778 |
| Commanded elevon at CLmax, deg | −6.6 | −8.3 | −9.9 | −11.6 | **−12.1** | −13.4 | −15.2 | −18.7 |
| Vs m/s | 11.45 | 11.65 | 11.84 | 11.92 | 11.93 | 11.95 | 11.99 | 12.06 |

The stall always starts at y ≈ 0.07 m, where the inboard elevon begins. The forward limit moves about 1 mm per 0.56° of
trim budget. The width is the item to watch. If T-D6-THROW cannot centre the servo in the play band, the full band is
charged: the forward limit goes to 0.0516 and the width to 3.3 mm, which fails. Halving the play recovers 0.4 mm.

| Forward-limit sensitivity | x_fwd m | Width mm |
|---|---|---|
| R4 baseline (e 0.973, ½ × 0.84° play) | 0.05085 | 4.05 |
| No D6 effectiveness, no play (R3 basis) | 0.04947 | 5.43 |
| Full play band charged to trim | 0.05160 | 3.30 (`FAIL`) |
| B2 η −20 % / +20 % (stall trim at the target −13.3° / −9.0° vs −11.0°) | η −20 %: about 0.0554, behind the aft limit, so the range closes (`FAIL`); η +20 %: about 0.0465 | — / about 8.4 |
| Prop dCN/dα ±50 % (aft limit) | aft limit 0.0558 / 0.0540 | — |

### 2.1 Ribner prop normal force at the aft limit

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Prop plane (−0.0077) ahead of the aft limit | 62.6 | mm | `CL-B3-PROP-ARM-AFT` | `CHECKED` |
| dCm/dα of the four props about the aft limit | +0.0165 (destabilising) | /rad | `CALC-B3-PROP-AFT` | `UNVERIFIED` |
| Cn_β of the four props about the aft limit | −0.0040 | /rad | `CL-B3-PROP-CNB-AFT` | `UNVERIFIED` |
| Thrust coefficient at 1.3 Vs | 0.045 (lightly loaded) | — | `CALC-B3-PROP-AFT` | `MODELLED` |
| SM at the aft limit if the props were left out | 5.6 % (they cost 1.9 mm of aft limit) | — | `CALC-B3-PROP-AFT` | `MODELLED` |

### 2.2 Where the A3-R5 layout sits (D-47 bay, D-59 spacer stations)

The pack moves the CG 0.236 mm per mm. Values are basic CG at 2.323 kg (550 g pack).

| Case | Pack x m | CG x m | Forward / aft margin mm | Source |
|---|---|---|---|---|
| **550 g at the D-47 datum (A3-R5 `CL-A3-CG-X`)** | **−0.022** | **0.0525** | **+1.6 / +2.4** | `CL-B3-CG-NOW-FWD/-AFT`, `CL-B3-CG-CENTRED-*` |
| 550 g on the B3 target | −0.0203 | 0.0529 | +2.0 / +2.0 | `CALC-B3-CG-CHECK` |
| 503 g, D-59 rule on the 0.0529 target | −0.024 | 0.0536 | +2.7 / **+1.3** | `CL-B3-CG-PACKS-AFT` |
| 550 g, D-59 rule on the 0.0529 target | −0.020 | 0.0530 | +2.1 / +1.9 | `CALC-B3-CG-CHECK` |
| 680 g, D-59 rule (no spacer) | −0.010 | 0.0519 | **+1.0** / +3.0 | `CL-B3-CG-PACKS-FWD` |
| Pack on the crush stack / at the aft stop | −0.0254 / −0.010 | 0.0517 / 0.0553 | stack +0.8; aft stop −0.4 (550 g) | `CALC-B3-CG-CHECK` |
| A3's predicted CG (growth allowance, `CL-A3-CG-X-PRED`) | −0.022 | 0.0539 | +3.0 / +1.0 | A3 claim (hand check) |
| Heaviest / lightest pack that fits the bay | — | — | 721 g / 457 g | `CL-B3-PACK-MASS-MAX/-MIN` |

D-59 picked the 550 g station at −0.018 for A1's 0.0522 on an earlier roll-up. On A3-R5 the same rule gives −0.020
for the 0.0529 target, and −0.018 would put the CG at 0.0534, which is still inside (1.5 mm aft margin). A3's predicted
CG with the 503 g pack is the thin case. A3 already flags it as 0.5 mm aft of the R3 aft mark. The D-59 nose ballast
(≤ 10 g) covers it: 10 g at the nose moves the CG 0.8 mm forward.

## 3 Trimmed stall and trim across speeds (2.6 kg, commanded elevon)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Trimmed CLmax at the target | 0.798 (elevon −11.0°, α 15.8°) | — | `CL-B3-CLMAX-TRIM`, `CL-B3-DELTA-STALL` | `UNVERIFIED` |
| **Vs at target / forward limit / aft limit** | **11.90 / 11.93 / 11.84** (≤ 12) | m/s | `CL-B3-VS-TRIM`, `-VS-TRIM-FWD` | `UNVERIFIED` |
| **1.3 Vs, forward limit** → `ARSPD_FBW_MIN` | **15.51** (≤ 16) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |

| V m/s | 11.9 | 13 | 14 | 15 | 16 | 18 | 20 | 25 |
|---|---|---|---|---|---|---|---|---|
| CL | 0.799 | 0.669 | 0.577 | 0.503 | 0.442 | 0.349 | 0.283 | 0.181 |
| α deg (target) | 15.8 | 13.0 | 11.1 | 9.6 | **8.4** | 6.5 | 5.2 | 3.2 |
| Elevon deg, fwd / target / aft | −12.1 / −11.0 / −9.8 | −10.1 / −9.2 / −8.2 | −8.7 / −7.9 / −7.1 | −7.7 / −7.0 / −6.2 | −6.8 / **−6.2** / −5.6 | −5.5 / −5.0 / −4.5 | −4.7 / −4.3 / −3.8 | −3.3 / −3.1 / −2.8 |

## 4 Control surfaces (elevons) and cruise authority, D6 terms included

| Check | Value | Limit | Source | Status |
|---|---|---|---|---|
| Elevon area (22 % c, both panels per side) | 17.2 % of S | 15–25 % | `CL-B3-ELEVON-FRAC-MIN/MAX` | `CHECKED` |
| Trim at 1.3 Vs, forward limit (e 0.955, ½ play) | 30.5 % of travel | ≤ 50 % | `CL-B3-TRIM-USE-VT` | `UNVERIFIED` |
| Steady roll rate at 1.3 Vs, 16.9° left after trim and full play | 244°/s | ≥ 90°/s | `CL-B3-ROLL-RATE-VT` | `UNVERIFIED` |
| Roll at the trimmed stall, 13.2° left: pb/2V, time to 60° | 0.126, 0.71 s (τ 0.35 s) | ≥ 0.07, ≤ 1.3 s | `CL-B3-ROLL-PB2V`, `-T60` | `UNVERIFIED` |
| Cruise motor-out roll at 1.3 Vs | elevons 3.09 N·m; hold needs 1.2° | ratio 14.6 ≥ 2 | `CL-B3-MOTOROUT-ROLL-RATIO` | `UNVERIFIED` |

| Elevon chord (target CG) | 0.18 c | **0.22 c** | 0.26 c |
|---|---|---|---|
| Area / S | 14.1 % (below the floor) | **17.2 %** | 20.3 % |
| Vs trimmed, m/s | 11.90 | **11.90** | 11.91 |
| Roll rate at 1.3 Vs after stall trim, °/s | 185 | **206** | 227 |

Keep 22 % chord, both panels and ±25°. A wider chord buys little forward CG range: Cm_δ grows 4 % per 0.04 c and the
stall trim drops about 0.3° (about 0.5 mm of forward limit). That is not worth the hinge moment and the D6 rework.

## 5 Dynamic modes at 16 m/s (CG target, props included) and directional stability

| Mode | Eigenvalue /s | Meaning | Claim | Status |
|---|---|---|---|---|
| Short period | −4.27 ± 8.39i (ωn 9.4 rad/s, ζ 0.45) | well damped | `CL-B3-SP-ZETA` ≥ 0.30 | `UNVERIFIED` |
| Phugoid | −0.033 ± 0.77i | lightly damped: TECS holds it | — | `PROPOSED` |
| Roll subsidence | −3.83 | — | — | `PROPOSED` |
| **Dutch roll** | −1.28 ± 3.65i (ζ 0.33) | damped | `CL-B3-DR-ZETA` ≥ 0.08 | `UNVERIFIED` |
| Spiral | +0.170 (doubles in 4.08 s) | Cl_β +0.0044; the FBWA roll loop holds it | `CL-B3-LAT-T2` ≥ 4 s | `UNVERIFIED` (+2 %) |

Against R3, the A3-R5 inertias lower the short-period frequency by 5 % (9.9 → 9.4 rad/s, ζ unchanged) and the
Dutch-roll frequency by 3 % (ζ 0.32 → 0.33). The spiral root is unchanged.

| Cn_β build-up, aft limit at 1.3 Vs (α 7.3°) | /rad | Source |
|---|---|---|
| Wing + half-fins 0.21 m (AVL) | +0.0463 | `CALC-B3-LATDIR` |
| 4 props (Ribner, about the aft limit) | −0.0040 | `CL-B3-PROP-CNB-AFT` |
| Pod (D-47, nose −0.130, length 0.225; Munk k 1.0) | −0.0063 | `ASM-B3-POD-K-YAW` |
| Tubes + motors | −0.0007 | `ASM-B3-CD-CYL` |
| **Total** | **+0.0354** (≥ 0.03, `R-DIRECTIONAL`, +18 %) | `CL-B3-CNB` |
| Same at 16 m/s, CG target | +0.0378 | `CL-B3-CNB-CRUISE` |

The 15 mm longer D-47 nose costs 0.0005 of Cn_β against R3.

## 6 Hover (tailsitter axes), torsion modes and transition

### 6.1 Control power and cant sizing (CR-B4-13)

The differential is capped at 30 % of hover thrust per motor (`R-HOVER-AUTHORITY`), which is 2.03 N per motor at the
gate. B4's R3 swirl factor `CL-B4-YAW` 1.79 is the nominal. **The cant is now sized on B4's half-fin factor
`CL-B4-YAW-LOW` 1.40**, which replaces the retired 0.48.

| Axis (hover) | Actuator | Moment N·m (rad/s²) | 5 m/s disturbance N·m | Ratio (≥ 1.5) | Status |
|---|---|---|---|---|---|
| Pitch (cruise y) | upper vs lower pair | 1.54 (30.7) | 0.62 | 2.50 | `UNVERIFIED` |
| Roll (cruise z) | left vs right pair, arm 0.32 m | 2.59 (13.8) | 0.55 | 4.72 | `UNVERIFIED` |
| **Yaw, 7° cant, factor 1.79** | reaction torque × 1.79 + cant | **0.61 (3.15)** | 0.19 | **3.15** | `UNVERIFIED` |
| **Yaw, 7° cant, factor 1.40 (sizing)** | | 0.56 (**2.88**) | 0.19 | **2.87** | `UNVERIFIED` (`CL-B3-HOVER-YAW-*-LOW`) |
| Yaw, no cant, factor 1.79 | | 0.24 (1.26) | 0.19 | 1.26 (`FAIL`) | info |

| Cant (sizing factor 1.40) | 0° | 3° | **3.8°** | 5° | **7°** | 8° |
|---|---|---|---|---|---|---|
| Yaw ratio | 0.98 | 1.79 | 2.0 | 2.33 | **2.87** | 3.14 |
| Yaw accel rad/s² (≥ 2.0) | 0.98 | 1.80 (`FAIL`) | **2.0 (floor)** | 2.34 | **2.88** | 3.15 |
| Thrust lost to cant | 0 | 0.14 % | 0.22 % | 0.38 % | 0.75 % | 0.97 % |

**Cant sizing:** the yaw accel floor (2 rad/s² at 30 % differential) binds before the 1.5× disturbance ratio. On the
1.40 factor it needs **3.8°** (`CL-B3-HOVER-CANT-REQ`); on 1.79 it needs 2.7°. 7° carries 44 % margin on accel and
covers a misbuilt fin. 5° (B4's CR-B4-14 option) passes with 17 %. B3 concurs with D-52: keep 7° until T-B4-YAW.
5° is acceptable if T-B4-YAW measures a factor of 0.92 or more, which is the floor at 5°. 7° holds the floor down to
a factor of 0.15.

Pitch trim at A3's split 1.216 uses 10.8 % of the pitch differential (`CL-B3-HOVER-TRIM-USE` ≤ 12.5 %, +14 %). The
elevons sit 46 mm outside the contracted hover wash (`CL-B3-ELEVON-WASH-GAP`), so they give no hover authority.

### 6.2 Rate loops with the wing torsion modes (CR-C2-03, D-45)

Hover pitch (upper vs lower pairs) drives the **symmetric** torsion mode, 21.7–27 Hz. The gyro sees the body side of
the spring (two-inertia, non-collocated). Hover yaw (diagonal pairs) drives the **antisymmetric** mode, the **12–15 Hz**
band of D-45 (C2: 11.7–14.9 Hz). Its node is on the centreline, so the gyro sees nothing directly. The twist does tilt
each station's thrust, which adds a yaw moment. Both signs of that coupling are checked (σ = ±1). The loop uses:

- F4's R4 PID ratios scaled to F4's R4 starting crossovers (pitch 2.6 Hz, yaw 1.0 Hz; R3 used 4.0 / 1.8)
- 4 ms delay, 40 ms motor lag, 40 Hz gyro filter, 2 % modal damping

Margins are the minimum over every −180° and 0 dB crossing.

| Loop (worst corner) | Gain margin dB (≥ 6) | Phase margin deg (≥ 45) | Rigid GM / PM | Max crossover for 6 dB / 45° | Claim | Status |
|---|---|---|---|---|---|---|
| **Pitch, 21.7 Hz mode, 2.6 Hz** | **11.6** (27 Hz: 14.7) | 66.1 | 18.7 / 66.3 | **4.5 Hz** | `CL-B3-FLEX-GM-PITCH`, `-PM-PITCH`, `CL-B3-XOVER-MAX-PITCH` | `MODELLED` |
| Pitch at 5 Hz | 5.1 (`FAIL` vs 6) | 53.1 | — | — | `CALC-B3-HOVER-FLEX` | `MODELLED` |
| **Yaw, 11.7 Hz mode, 1.0 Hz** | **22.0** (σ −1: 21.5) | 69.1 | 24.3 / 71.5 | **2.4 Hz** (rigid PM binds: no D) | `CL-B3-FLEX-GM-YAW`, `-PM-YAW`, `CL-B3-XOVER-MAX-YAW` | `MODELLED` |
| **Yaw at its 2.4 Hz ceiling, mode anywhere in 11.7–14.9 Hz, σ ±1** | **≥ 12.8** (worst at 11.7 Hz) | ≥ 45.9 | — | — | `CALC-B3-HOVER-FLEX` (`yaw_band_*`) | `MODELLED` |
| Yaw at 5 Hz | 4.2 | 15.4 (`FAIL`) | — | — | `CALC-B3-HOVER-FLEX` | `MODELLED` |
| Static twist effect on hover yaw power | +16 % (not credited) | | | | `CL-B3-HOVER-YAW-FLEX-STATIC` | `MODELLED` |

The 12–15 Hz mode is not the limit on yaw. Above 2.4 Hz the rigid yaw loop runs out of phase margin first (P+I with no
D), and 12.8 dB of gain margin is left across the band at that ceiling. At R3 (4.0 Hz pitch crossover), a 25 ms motor
lag cost 3.2 dB and an 80 Hz gyro filter 4.7 dB. At F4's R4 2.6 Hz the pitch margin is 11.6 dB, so the same losses
would still leave more than 6 dB. That sensitivity was not re-run at 2.6 Hz. F4 holds pitch ≤ 4.5 Hz and yaw ≤ 2.4 Hz
and adds a static notch at the tapped frequencies before raising gains (CR-B3-19).

### 6.3 Transition (quasi-steady, level, forward limit)

| V m/s | 0 | 4 | 6 | 8 | 10 | 11 | 12 | 16 |
|---|---|---|---|---|---|---|---|---|
| Body angle α deg | 90 | 80 | 69 | 55 | 43 | 38 | 12 | 7 |
| T/W | 1.06 | 0.99 | 0.94 | 0.83 | 0.69 | 0.63 | 0.11 | 0.09 |
| Aero pitch moment N·m (− nose-down) | 0 | −0.42 | −0.78 | −1.02 | −1.06 | −1.03 | −0.50 | −0.53 |
| Share of motor pitch differential used | 0 | 0.08 | 0.15 | **0.20** | 0.19 | 0.16 | 0 (elevons) | 0 |

The motors use at most 20 % of the pitch differential (`CL-B3-TRANS-PITCH-USE` ≤ 60 %). The elevon post-stall credit
in the transition now carries D6's effectiveness and play.

## 7 Responses to requests addressed to B3

| Request | Answer |
|---|---|
| CR-A3-23 / A1 forward (R4 roll-up) | Re-run on A3-R5. `CL-B3-CG-FWD/-AFT/-TARGET` keep their ids: 0.05085 / 0.05490 / 0.05287 m. New params values in CR-B3-22 |
| CR-B3-17 (accepted D-47) | Superseded by CR-B3-22: the D6 terms move the forward limit 1.3 mm aft |
| CR-B3-18 | Closed. Superseded by D-47 (pack at −0.022 with the bay moved). The datum CG 0.0525 is inside the range with 1.6 / 2.4 mm margins |
| CR-B4-13 | Cant sized on `CL-B4-YAW-LOW` 1.40: needs 3.8°, 7° kept (section 6.1); `CL-B4-YAW` 1.79 is the nominal |
| CR-D6-08 | Effectiveness and play are in the CG limits, stall trim, roll, cruise authority and transition (section 1). Effect: forward limit +1.3 mm, roll rate at 1.3 Vs 267 → 244°/s |
| CR-C2-03 / D-45 | The 12–15 Hz antisymmetric band is swept in the yaw loop (section 6.2): ≥ 12.8 dB at the 2.4 Hz ceiling |
| CR-A2-19 | Claim ids unchanged; `R-HOVER-AUTHORITY`, `R-DIRECTIONAL`, `R-CG-RANGE` links unchanged |

## 8 Open issues

1. **The CG range is 4.05 mm wide, against 4 mm.** The width depends on T-D6-THROW centring the servo in the 0.84° play
   band. With the full band charged it is 3.3 mm. T-B3-CG-BALANCE and T-D6-THROW decide.
2. The forward limit rests on B2's η and Δcm (`UNVERIFIED`). η −20 % puts the stall trim at the target at −13.3°,
   past the 12.08° budget, and the range closes. η +20 % widens it to about 8.4 mm (deflection scaled as 1/η on the CG scan). The twin's trim-vs-CL glides
   (T-B3-TWIN-NP) measure η before the aircraft flies.
3. A3's predicted CG with a 503 g pack is at the aft limit. The D-59 nose ballast (≤ 10 g, 0.8 mm) covers it.
4. The hover pitch margin rests on a 40 ms motor lag and C2's 21.7 Hz mode (both `UNVERIFIED`). It is measured before
   the first hover (stand test, T-C2-TAP-TEST).
5. Hover yaw factor 1.40–1.79 between B4's models. Both pass at 7°. T-B4-YAW settles it.
6. Spiral time to double 4.08 s (limit 4 s): benign under FBWA, marginal in MANUAL.
7. The transition model is quasi-steady with no prop wash on the wing. F4's SITL with `results/sc_results.json` is the
   next check.

## 9 CDR fix round, 2026-11-13 (stream S3: CDR-14, CDR-16)

Run: `verify_asdesigned.py` (CG limits, 22 min of fresh AVL), then `sc_analysis.py`. Everything is `UNVERIFIED` (nothing
flown). "Before" is the tree at `3268e69`. Where a number above in this file disagrees, this section is the newer one.

### 9.1 CG plan (CDR-14, board decision B9)

The forward limit was the 12.5° of pure-pitch elevon that `MIXING_GAIN` 0.5 leaves, not a physical limit. `CALC-B3-V-CG`
now reads the travel from `P:fsw.mixing_gain` (0.65 → 16.25°); `requirements.elevon_trim_travel_max` 0.5 keeps its
other job, the trim share at 1.3 Vs.

| Quantity | Before | After | Limit | Claim |
|---|---|---|---|---|
| Forward CG limit (trim at the stall, CG height in) | 0.04647 m | **0.03932 m** (12.3 % c; static margin there 9.2 %; binding: trim) | — | `CL-B3-V-CG-FWD` |
| Aft CG limit (static margin 5 % at 1.3 Vs) | 0.05128 m | 0.05133 m | — | `CL-B3-V-CG-AFT-ENV` |
| Range width | 4.81 mm | **12.0 mm** | ≥ 4 mm | `CL-B3-V-CG-WIDTH-ENV` |
| Effective neutral point, 1.3 Vs | 0.06728 m | 0.06733 m | — | `CL-B3-V-XNP-ENV` |
| `cg.x_range_m` (rounded inward) | [0.0466, 0.0514] | **[0.0394, 0.0513]** | — | D-120 |
| Aft end of the params range against the claim | −0.12 mm (`FAILS`, hidden by the graph) | +0.03 mm with 0.0513 | ≥ 0 | `CL-B3-V-RANGE-AFT-IN` |
| Trimmed stall at the forward limit, free transition | 11.93 m/s | 12.01 m/s (B2: 12.08) | ≤ 12.3 | `CL-B3-V-VS-FWD`, `CL-B2R3-VS-GATE-FWD` |
| 1.3 Vs at the forward limit | 15.52 m/s | 15.61 m/s (B2: **15.70, `FAILS` the 15.6 key**; flown value is 17) | ≤ 16 (cruise key) / 15.6 | `CL-B3-V-VT`, `CL-B2R3-VTR-GATE-FWD` |
| Trim share at 1.3 Vs, worst CG | 0.33 | 0.42 | ≤ 0.5 | `CL-B3-TRIM-USE-VT` |
| Roll helix angle at the stall, CG target | 0.126 | 0.126 | ≥ 0.07 | `CL-B3-ROLL-PB2V` |
| Roll helix angle at the stall on the forward limit (pitch uses 16.25°, 8.75° left) | — | about 0.078 (`EST`: 0.126 × 8.75 / 14.1, not an AVL run) | ≥ 0.07 | — |

**First fixed-wing flights (D-121).** Static margin ≥ 6.5 % at the worst wingborne speed means
x ≤ 0.06733 − 0.065 × 0.32 = **0.0465 m**; the first-flight band is 0.0453 m (the new mid-range, 6.9 %) to 0.0465 m.
Against S4's roll-up cases (`MASS-CG.md`, read 2026-11-13):

| Case (S4) | CG x | Static margin | To the forward limit 0.0393 | Reading |
|---|---|---|---|---|
| 551 g pack, basic, 30 g nose ballast | 0.04667 m | 6.46 % | +7.3 mm | 0.14 mm short of 6.5 %: 32 g, or accept 6.46 % |
| 546 g pack, basic, 30 g ballast, 11 × 7E props | 0.04626 m | 6.58 % | **+6.9 mm** (was −0.34 mm outside the old 0.0466 limit) | inside; ballast and the heavier props can be fitted together |
| Predicted growth all realised (0.0499–0.0501 m unballasted), 30 g | 0.0475–0.0477 m | 6.1–6.2 % | +8 mm | 6.5 % then needs 43–45 g at 0.8 mm per 10 g (D-59) |

So ≤ 30 g reaches 6.5 % only while the as-weighed unballasted CG is ≤ 0.0489 m. The marks are not scribed until the
twin's neutral point is measured (`T-B3-TWIN-NP`): a ±2 % c neutral-point error is ±6.4 mm, half the new range.

### 9.2 Hover yaw with a wingtip into the wind (CDR-AE-04)

`Q_WVANE_LAND` / `TAKEOFF` 3 puts a wingtip into wind. The wing is then a plate of aspect ratio c / b = 0.28 at an
incidence equal to the heading error; its centre of pressure is ahead of mid-span, so the moment grows with the error
(`CALC-B3-HOVER-WTIP`, `ASM-B3-WTIP-CN`, `-ARM`: estimates, the twin test replaces them). Control: 0.550 N·m at 30 %
differential (B4 half-fin factor, 7° cant), 2.79 rad/s². The elevons give nothing (outside the wash).

| Case | Wing moment | Ratio, no fin credit | With the fins' restoring moment | Limit | Claim |
|---|---|---|---|---|---|
| Belly into wind, 5 m/s (the old case, 9 % asymmetry) | 0.19 N·m | 2.83 | — | ≥ 1.5 | `CL-B3-HOVER-YAW-RATIO-LOW` |
| Wingtip into 5 m/s, 10° error | 0.170 N·m | **3.24** | 3.99 | ≥ 1.5 | `CL-B3-HOVER-YAW-WTIP-10` |
| Wingtip into 5 m/s, 20° error | 0.417 N·m | **1.32 (`FAILS`)** | 1.55 | ≥ 1.5 | `CL-B3-HOVER-YAW-WTIP-20`, `-FINS` |
| Wingtip into the 8 m/s gust, 10° | 0.435 N·m | 1.26 | 1.56 | ≥ 1.0 | `CL-B3-HOVER-YAW-WTIP-GUST-10` |
| Wingtip into the 8 m/s gust, 20° | 1.068 N·m | 0.51 | 0.60 | — | information |
| Heading error where the ratio is 1.5 / 1.0, 5 m/s | — | 18.1° / 24.6° | — | — | `CL-B3-HOVER-YAW-WTIP-BETA`, `-BETA-SAT` |
| Heading error where control saturates, 8 m/s | — | 12.0° | — | — | `CL-B3-HOVER-YAW-WTIP-BETA-GUST` |

Reading: the stance holds for small errors and lets go beyond about 25° in 5 m/s (12° in the gust); the aircraft then
swings broadside, where pitch (the strongest axis) carries the wind. The reviewer's 1.5 at 20° is 1.32 here because the
cross-flow arm is taken at b / 8. **Contingency, cant 7° → 10° (PROPOSED, not applied; decided before any mount is
printed if `T-B3-HOVER-YAW-WTIP` fails):** yaw arm 0.0678 → 0.0871 m (**+28.4 %**), yaw acceleration 2.79 → 3.58 rad/s²,
ratio at 20° 1.32 → 1.69, lift −0.78 % against 7° (1.52 % against no cant). It needs D3's mount re-drawn and E1's
blade-to-tube gap (26.1 mm) re-checked. `Q_A_ACC_Y_MAX` is set to 135 deg/s/s = 2.36 rad/s², 85 % of 2.79 (`CL-F4-YAW-ACC-SET`).

### 9.3 Gust pitch claim for `R-GUST-LEAN` (CDR-AE-10)

| Quantity | Value | Limit | Claim |
|---|---|---|---|
| Pitch control / 8 m/s gust moment at the 30 % cap | 0.94 (2.40 × (5 / 8)²) | — (below 1: the cap does not hold the gust) | `CL-B3-HOVER-PITCH-RATIO-GUST-CAP30` |
| Differential needed | 32 % | ≤ 40 % (`ASM-B3-GUST-DIFF-MAX`, PROPOSED, A2 to accept) | `CL-B3-HOVER-PITCH-DIFF-GUST` |
| Ratio at the 40 % gust differential | 1.25 | ≥ 1.0 | `CL-B3-HOVER-PITCH-RATIO-GUST` → `R-GUST-LEAN` |

### 9.4 Transition pitch claim re-based (CDR-AE-07)

`CL-B3-TRANS-PITCH-USE` now divides the motor moment (no elevon credit) by the pitch moment at the 30 % cap, 1.54 N·m.

| Basis | Before | After | Limit |
|---|---|---|---|
| Full differential (lower pair to zero), elevon credit: `CL-B3-TRANS-PITCH-USE-FULLDIFF` | 0.247 | 0.275 (forward limit moved) | information |
| 30 % cap, no elevon credit, hub H-force bound: `CL-B3-TRANS-PITCH-USE` | — | **0.91 (`FAILS`)**, 1.40 N·m needed | ≤ 0.60 |
| 30 % cap, Ribner normal force only: `-NOHUB-CAP30` | — | **0.83 (`FAILS`)** | ≤ 0.60 |

The reviewer's 0.64 was at the old CG range; the forward limit 0.0393 m lengthens the wing's nose-down arm. The level
quasi-steady moment does not depend on the pitch-over rate, so lowering `Q_TAILSIT_RAT_FW` does not change it. What
can: first flights at CG ≥ 0.0453 m (not the forward limit), the differential allowed in the pitch-over (40 % brings
0.91 to 0.68), and measurement: SITL stage B S4 and the twin's logged upper / lower RCOU split. Open (item 8 below).

### 9.5 Thrust line below the CG (CDR-AE-11)

Four equal thrusts act in the chord plane; the CG is 18.5 mm above it (`CALC-B3-THRUST-LINE`).

| Point (16 m/s) | Thrust | Nose-up moment | ΔCm | Elevon equivalent | Claim |
|---|---|---|---|---|---|
| Cruise | 4.50 N | 0.083 N·m | 0.0045 | 0.77° (power-on trim −5.95° instead of −6.72°) | `CL-B3-THRUST-LINE-M-CRUISE`, `-DELEV-CRUISE` |
| `THR_MAX` 70 % | 20 N (`REVIEWER EST`, upper end) | 0.37 N·m | 0.0200 | 3.41° (≤ 5°) | `CL-B3-THRUST-LINE-DELEV-THRMAX` |
| Step 30 → 70 % | — | — | — | 1.95° | SITL S19 |

The power-off trim and stall already in §3 are the conservative side (thrust reduces the up-elevon needed).

### 9.6 Open after this round

8. `CL-B3-TRANS-PITCH-USE` 0.91 and `CL-B3-HOVER-YAW-WTIP-20` 1.32 fail on paper; both close by test (SITL stage B, twin TW3), not by argument.
9. No time-domain back-transition case was added to `CALC-B3-TRANSITION` (CDR-AE-03, part of CDR-07): not done.
10. `T-B3-TWIN-NP` before the CG marks are scribed.
