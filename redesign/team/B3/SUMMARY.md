# B3 stability and control: K09-L summary (R4)

Status: `PROPOSED` (B3, 2026-11-10, A1-R4a params, A3-R5 roll-up, B4 R3, D6 R3, C2 modes, F4 R4, read live from the
claim graph). Full report: `S-AND-C.md`. Requests: `CHANGE-REQUESTS.md` (CR-B3-22, -23 new).
Re-check: `python -I redesign/team/B3/sc_analysis.py`, `run_avl_study.py`, `draw_cg.py`, then
`python -I redesign/proofs/build_graph.py`. On 2026-11-10 there is no `CALC-B3-*` drift and no B3 id error. Two
downstream calcs drift on the new B3 claims and must re-run: A1's `CALC-A1-CG-RANGE` and C5's `CALC-C5-STANCE`.

**R4 answer.** The claim ids are unchanged. **The forward limit moves 1.3 mm aft to 0.0509 m**, because D6's elevon
effectiveness and half of its 0.84° free play now come out of the trim budget. The range is **0.0509–0.0549 m**
(4.05 mm wide, minimum 4) and the target is **0.0529**. A1's carried 0.050 is now ahead of the forward limit, so A1
narrows the range (CR-B3-22). The D-47 bay works: the 550 g pack at −0.022 gives CG 0.0525 m, +1.6 / +2.4 mm. The task
text's 0.0577 m is the pre-D-47 bay, not A3-R5's published CG. The cant is sized on B4's 1.40 factor: 3.8° is needed
and 7° is kept. The 12–15 Hz torsion band leaves ≥ 12.8 dB in the hover yaw loop.

## Key numbers

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
| CR-B3-22 | `cg.x_range_m` [0.0509, 0.0549], `cg.x_target_m` 0.0529; re-run `CALC-A1-CG-RANGE`, `CALC-C5-STANCE`; D-59 stations 503 / 550 / 680 g at −0.024 / −0.020 / −0.010 | A1 (A3, C5, H1, J1) |
| CR-B3-23 | Centre each elevon servo in its play band, report the band (≤ 0.84°) | D6 (H1, F4) |
| CR-B3-19 | Hover crossovers ≤ 4.5 Hz pitch / 2.4 Hz yaw until the tap test, then notches | F4 (C2, H2) |
| CR-B3-20 | T-B4-YAW; 5° acceptable only if the factor is ≥ 0.92 | B4 (H1) |
| CR-B3-21, -13, -16, -09 | C2 mode claims; B2 η (−20 % closes the range); A2 text; H1/H2 tests (marks 0.0509 / 0.0549) | C2, B2, A2, H1, H2 |

## Files

| File | What |
|---|---|
| `sc_analysis.py` → `claims.json` (66 claims), `results/sc_results.json` | AVL, NP, CG limits with D6 terms, pack stations, stall, trim, authority, modes, hover and cant, torsion-mode loops, transition |
| `hover_loop.py` | hover rate-loop models with the torsion modes |
| `avl_model.py` · `avl/k09l.avl` · `avl/k09l.mass` · `avl/s5010.dat` | AVL generator, runner, cache; R4 model files (A3-R5 inertia at 2.6 kg) |
| `flight_models.py` | props/tubes/pod terms, hover authority, slipstream gap, quasi-steady transition |
| `run_avl_study.py` → `results/study.json` | sensitivities, elevon chord sweep, fin options, cant sweep, AVL MODE check, trim drag |
| `draw_cg.py` → `fig-b3-cg-stations.svg` | FIG B3-01 chordwise NP / CG range / A3 CG |

## Open issues

1. The CG width is 4.05 mm against a 4 mm minimum. It depends on centring the servo in the play band (CR-B3-23).
2. B2's η −20 % closes the range. The twin glides (T-B3-TWIN-NP) measure η.
3. A3's predicted CG with a 503 g pack sits at the aft limit. The D-59 nose ballast (≤ 10 g, 0.8 mm) covers it.
4. The hover pitch margin rests on a 40 ms motor lag and the 21.7 Hz mode (both `UNVERIFIED`). Spiral t2 4.08 s is 2 %
   over its limit.
