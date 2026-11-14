# B3 stability and control: K09-L summary (V1 verification round)

**CDR fix round, 2026-11-13 (CDR-14, CDR-16; details `S-AND-C.md` §9).** `MIXING_GAIN` 0.65 moves the forward CG limit
0.0465 → **0.0393 m**; range **[0.0394, 0.0513] m, 12.0 mm** (was 4.8). First fixed-wing flights at x ≤ 0.0465 m (static
margin ≥ 6.5 %). New cases: hover yaw with a wingtip into a 5 m/s wind 3.24 at 10° heading error, **1.32 at 20° (`FAILS` 1.5)**,
saturating at 25° (12° in the 8 m/s gust); 10° cant contingency +28 % yaw arm. `CL-B3-TRANS-PITCH-USE` re-based on the 30 % cap
with no elevon credit: **0.91 (`FAILS` 0.60)**. Gust pitch: 0.94 at the cap, 32 % differential needed, 1.25 at 40 %
(`R-GUST-LEAN` now has claims). Thrust line: 0.083 N·m in cruise (0.77° of elevon), 3.4° at `THR_MAX`. The tables
below are V1 / R4 and their CG range is superseded.

Status: `MODELLED` (B3, 2026-11-10). V1 re-runs the chain on the settled CAD (fins `fins.py` R4, wing elevon gaps)
and the A3-R6a roll-up. Report: **`SIMULATION-REPORT.md`**; R4 design basis: `S-AND-C.md`. Requests:
`CHANGE-REQUESTS.md` (CR-B3-24 … -29 new). Claims: `claims.verify.json` (32, `CL-B3-V-*`) beside R4's `claims.json`.

**V1 answer: two requirements now fail, both from the CG height.** A3's CG is **18.5 mm above the chord plane**; R4
assumed 0 (`cg.z_target_m`). That moves the effective NP **3.4 mm forward at 1.3 Vs** (AVL; hand formula within
0.4 %). The SM-limited aft CG becomes **0.0514 m**: A3's 0.0522 m is 0.77 mm aft (**SM 4.76 %, FAIL**), the
predicted 0.0536 m is 2.15 mm aft. The raised CG also gives Cl_β +0.023 and **spiral t2 3.51 s (< 4 s, FAIL)**. The
range keeps its width (4.85 mm) and slides forward to **0.0466–0.0514 m, target 0.0490** (CR-B3-25). The CAD fins
beat the R4 rectangle: Cn_β 0.048–0.062 vs 0.035.

## V1 key numbers (as designed, gate 2.6 kg)

| Parameter | R4 | V1 as designed | Limit | Claim | Status |
|---|---|---|---|---|---|
| Xnp whole aircraft at 1.3 Vs: CG on chord plane / at A3 z | 0.0709 m | 0.0709 / **0.0674** m | — | `CL-B3-V-XNP-ENV` | `UNVERIFIED` |
| **CG range** (fwd – aft) | 0.0509 – 0.0549 m | **0.0466 – 0.0514 m** (width 4.85 mm) | ≥ 4 mm | `CL-B3-V-CG-FWD`, `-CG-AFT-ENV`, `-CG-WIDTH-ENV` | `UNVERIFIED` |
| A3-R6a CG 0.0522 / predicted 0.0536 vs aft limit | +2.4 mm | **−0.77 / −2.15 mm** | ≥ 0 | `CL-B3-V-CG-A3-AFT-ENV`, `-A3PRED-AFT-ENV` | **FAIL** |
| SM at A3 CG: 1.3 Vs / cruise / Vs | 5.6 % | **4.76 / 4.83 / 3.80 %** | ≥ 5 % | `CL-B3-V-SM-A3-ENV` | **FAIL** |
| CG move to the 0.0490 target, basic / predicted | — | 3.2 / 4.6 mm forward (to the limit 0.8 / 2.2) | — | `CL-B3-V-CG-SHIFT-REQ(-PRED)` | `PROPOSED` |
| Cn_β, 1.3 Vs, aft: laminate / tube as fin LE | 0.0354 | 0.0615 / 0.0479 | ≥ 0.03 | `CL-B3-V-CNB`, `-CNB-TUBE` | `UNVERIFIED` |
| Trimmed Vs at A3 CG / 1.3 Vs at forward limit | 11.90 / 15.51 m/s | 11.77 / 15.52 m/s | ≤ 12 / ≤ 16 | `CL-B3-V-VS-A3`, `-VT` | `UNVERIFIED` |
| Short period ζ / Dutch roll ζ | 0.45 / 0.33 | 0.48 / 0.28 | ≥ 0.30 / 0.08 | `CL-B3-V-SP-ZETA`, `-DR-ZETA` | `UNVERIFIED` |
| **Spiral t2** | 4.08 s | **3.51 s** | ≥ 4 s | `CL-B3-V-LAT-T2` | **FAIL** |
| Hover pitch / roll / yaw ratios (5 m/s) | 2.50 / 4.72 / 2.87 | unchanged (A3-R6a inertia already in R4; motor CAD within 1 mm) | ≥ 1.5 | R4 `CL-B3-HOVER-*` | `UNVERIFIED` |

| Verification check | Result | Status |
|---|---|---|
| AVL lattice, 4 levels (692 → 4 676 vortices) | Xnp fine → xfine 0.006 mm; Cn_β GCI 0.13 %; Cm_δ / Cl_δ GCI 3.9 / 5.8 % | `CHECKED` |
| Own flat-plate VLM vs AVL; CG-height hand formula vs AVL | CL_α −2.5 %, Xnp −0.11 % c; NP shift −0.4 % | `CHECKED` |
| Elevon η: XFOIL 160/240/320 panels vs SU2 SA RANS (L1, L2 converged; L3 not) | XFOIL 0.57–0.61 (GCI 15 %), SA 0.87; B2's 0.606 is the conservative end | `MODELLED` |

## R4 key numbers (CG on the chord plane; CG range, SM and spiral superseded by V1)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP: wing + fins (AVL) / whole aircraft | 0.07385 / 0.07090 | m | `CL-B3-XNP-AERO` / `CL-B3-XNP` | `CHECKED` / `UNVERIFIED` |
| **CG range** (fwd – aft) | **0.05085 – 0.05490** (15.9–17.2 % c) | m | `CL-B3-CG-FWD`, `CL-B3-CG-AFT` | `UNVERIFIED` |
| CG width (≥ 4 mm) | 4.05 (full play band: 3.3, fails) | mm | `CL-B3-CG-WIDTH` | `UNVERIFIED` (thin) |
| CG target, static margin there | 0.05287, 5.63 % | m, — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| A3-R5 CG, 550 g at the −0.022 datum | 0.0525: +1.6 fwd / +2.4 aft | m / mm | `CL-B3-CG-NOW-FWD/-AFT` | `UNVERIFIED` |
| Packs at D-59 stations on 0.0529 (503 / 550 / 680 g at −0.024 / −0.020 / −0.010) | worst +1.0 fwd (680 g) / +1.3 aft (503 g) | mm | `CL-B3-CG-PACKS-FWD/-AFT` | `UNVERIFIED` |
| Trimmed CLmax / Vs at target, 2.6 kg | 0.798 / 11.90 (≤ 12) | —, m/s | `CL-B3-CLMAX-TRIM`, `CL-B3-VS-TRIM` | `UNVERIFIED` |
| **1.3 Vs at the forward limit** (`ARSPD_FBW_MIN` 15.6 stands) | **15.51** (≤ 16) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |
| Elevon trim / α at 16 m/s, target | −6.2 (TE up) / 8.4 | deg | `CL-B3-ELEVON-TRIM-CRUISE`, `-ALPHA-CRUISE` | `UNVERIFIED` |
| Elevons 22 % c, 17.2 % S, ±25°: trim at 1.3 Vs / roll rate (D6 terms in) | 30.5 % / 244°/s | — | `CL-B3-TRIM-USE-VT`, `-ROLL-RATE-VT` | `UNVERIFIED` |
| Cn_β, aft limit, 1.3 Vs / cruise | 0.0354 / 0.0378 (≥ 0.03) | /rad | `CL-B3-CNB`, `-CNB-CRUISE` | `UNVERIFIED` |
| Short period ζ / Dutch roll ζ / spiral t2 | 0.45 / 0.33 / 4.08 s | — | `CL-B3-SP-ZETA`, `-DR-ZETA`, `-LAT-T2` | `UNVERIFIED` |
| Hover 5 m/s ratio: pitch / roll | 2.50 / 4.72 (≥ 1.5) | — | `CL-B3-HOVER-PITCH/ROLL-RATIO` | `UNVERIFIED` |
| **Hover yaw at 7°, factor 1.40 (sizing) / 1.79** | **2.87× / 2.88 rad/s²** / 3.15× / 3.15 rad/s² | — | `CL-B3-HOVER-YAW-*-LOW` / `-YAW-*` | `UNVERIFIED` |
| Cant needed (factor 1.40 / 1.79) | 3.8 / 2.7 (installed 7) | deg | `CL-B3-HOVER-CANT-REQ` | `UNVERIFIED` |
| Hover trim share, split 1.216 | 10.8 % (≤ 12.5 %) | — | `CL-B3-HOVER-TRIM-USE` | `UNVERIFIED` |
| Hover pitch loop GM at F4 2.6 Hz (21.7 Hz mode) / max crossover | 11.6 dB / 4.5 Hz | dB / Hz | `CL-B3-FLEX-GM-PITCH`, `-XOVER-MAX-PITCH` | `MODELLED` |
| Hover yaw loop GM at F4 1.0 Hz / max crossover / band 11.7–14.9 Hz at the ceiling | 22.0 dB / 2.4 Hz / ≥ 12.8 dB | — | `CL-B3-FLEX-GM-YAW`, `-XOVER-MAX-YAW` | `MODELLED` |
| Transition: worst motor pitch share | 0.20 (≤ 0.60) at 8 m/s | — | `CL-B3-TRANS-PITCH-USE` | `UNVERIFIED` |

## What others must do

| # | Request | To |
|---|---|---|
| **CR-B3-25** | `cg.x_range_m` [0.0466, 0.0514], target 0.0490; bring the CG 3.2 mm forward (≈ 41 g at the pod nose, or the bay ~10 mm forward) or lower it | A1 (A3, D2, F1, C5, H1, J1) |
| **CR-B3-26** | Spiral 3.51 s: lower the CG to z ≤ 0, or amend the limit (≥ 3.3 s, roll-stabilised modes only) | A2 (A1, F4, H2) |
| CR-B3-24, -27 | Publish `CL-A3-CG-Z`; set `cg.z_target_m` to A3's value and narrow `cg.z_range_m` | A3, A1 |
| CR-B3-28, -29 | η note (no change); balance marks 0.0466 / 0.0514 m | B2, H1 |
| CR-B3-22 (superseded by -25) | `cg.x_range_m` [0.0509, 0.0549], `cg.x_target_m` 0.0529; re-run `CALC-A1-CG-RANGE`, `CALC-C5-STANCE`; D-59 stations 503 / 550 / 680 g at −0.024 / −0.020 / −0.010 | A1 (A3, C5, H1, J1) |
| CR-B3-23 | Centre each elevon servo in its play band, report the band (≤ 0.84°) | D6 (H1, F4) |
| CR-B3-19 | Hover crossovers ≤ 4.5 Hz pitch / 2.4 Hz yaw until the tap test, then notches | F4 (C2, H2) |
| CR-B3-20 | T-B4-YAW; 5° acceptable only if the factor is ≥ 0.92 | B4 (H1) |
| CR-B3-21, -13, -16, -09 | C2 mode claims; B2 η (−20 % closes the range); A2 text; H1/H2 tests (marks 0.0509 / 0.0549) | C2, B2, A2, H1, H2 |

## Files

| File | What |
|---|---|
| `verify_asdesigned.py` → `claims.verify.json`, `results/verify.json` | V1: CAD fin outline (re-read from `fins.py`), 4-level lattice study, own VLM, NP vs CL, CG limits, Cn_β, stall, modes |
| `sens_zcg.py` → `results/sens_zcg.json` · `cfd_elevon.py` → `cfd/cfd_results.json` | V1: CG-height sweep; SU2 RANS + XFOIL elevon η (3 meshes / 3 panel counts) |
| `plot_verify.py` → `fig/B3-V1…V6.svg` | V1 report figures |
| `sc_analysis.py` → `claims.json` (66 claims), `results/sc_results.json` | AVL, NP, CG limits with D6 terms, pack stations, stall, trim, authority, modes, hover and cant, torsion-mode loops, transition |
| `hover_loop.py` | hover rate-loop models with the torsion modes |
| `avl_model.py` · `avl/k09l.avl` · `avl/k09l.mass` · `avl/s5010.dat` | AVL generator, runner, cache; R4 model files (A3-R5 inertia at 2.6 kg) |
| `flight_models.py` | props/tubes/pod terms, hover authority, slipstream gap, quasi-steady transition |
| `run_avl_study.py` → `results/study.json` | sensitivities, elevon chord sweep, fin options, cant sweep, AVL MODE check, trim drag |
| `draw_cg.py` → `fig-b3-cg-stations.svg` | FIG B3-01 chordwise NP / CG range / A3 CG |

## Open issues

1. R-STATIC-MARGIN, R-CG-RANGE and the spiral fail until A1 / A2 act on CR-B3-25 / -26. Each 10 mm of CG height
   costs 1.85 mm of aft limit and 0.27 s of spiral t2.
2. R4 `CL-B3-CG-*` claims (z = 0) are superseded by `CL-B3-V-*`; `sc_analysis.py` takes A3's z once A1 sets
   `cg.z_target_m` (CR-B3-27).
3. SU2 L3 (δ 0) does not converge on its mesh: the CFD η is a two-level cross-check only. 41 % of the fin's AVL Cn_β
   comes from the 77°-swept top strip; the half-effectiveness bracket (0.041) still passes.
4. The hover pitch margin rests on a 40 ms motor lag and the 21.7 Hz mode (both `UNVERIFIED`).
