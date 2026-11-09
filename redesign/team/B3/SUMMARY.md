# B3 stability and control: K09-L summary (R1)

Status: `PROPOSED` (B3, 2026-11-09, params A1-R2). Full report: `S-AND-C.md`. Requests: `CHANGE-REQUESTS.md`
(CR-B3-11…16 open). Re-check: `python -I redesign/team/B3/sc_analysis.py`, `run_avl_study.py`, `draw_cg.py`, then
`python -I redesign/proofs/build_graph.py` (2026-11-09: B3 has no drift and no id errors; the build fails on other
roles' drift, including A1's `CALC-A1-POD-RULE`, which reads the new B3 CG claims).

**D-17 answer: 0.051 m is inside the new range, so the pod stays at −0.105 m.** Put the pack 4 mm aft of the pod
centre, not 29 mm forward. Moving the pod to −0.125 would put the CG 5.5 mm ahead of the forward limit.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP: wing + fins (AVL) / whole aircraft (props, pod) | 0.0738 / 0.0713 | m | `CL-B3-XNP-AERO` / `CL-B3-XNP` | `CHECKED` / `UNVERIFIED` |
| **CG range** (fwd – aft) | **0.0499 – 0.0553** (15.6–17.3 % c) | m | `CL-B3-CG-FWD`, `CL-B3-CG-AFT` | `UNVERIFIED` |
| CG target, static margin there | 0.0526, 5.8 % | m, — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| CG, pack centred (A3) vs range | 0.0515: +1.6 mm fwd / +3.7 mm aft margin | m | `CL-B3-CG-CENTRED-FWD/AFT` | `UNVERIFIED` |
| CG, pack 29 mm forward (A3 today) | 0.0440: 5.9 mm ahead of the forward limit | m | `CL-B3-CG-NOW-FWD` | `FAIL` → CR-B3-11 |
| Trimmed CLmax / Vs at target, 2.6 kg | 0.799 / 11.90 (≤ 12) | —, m/s | `CL-B3-CLMAX-TRIM`, `CL-B3-VS-TRIM` | `UNVERIFIED` |
| **1.3 Vs at the forward limit** (`ARSPD_FBW_MIN` 15.6) | **15.51** (≤ 16 cruise) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |
| Elevon trim / α at 16 m/s | −6.1 (TE up) / 8.4 | deg | `CL-B3-ELEVON-TRIM-CRUISE`, `-ALPHA-CRUISE` | `UNVERIFIED` |
| Elevons: chord, area, travel | 22 % c, 17.2 % S, ±25 | —, —, deg | `CL-B3-ELEVON-FRAC-MIN/MAX` | `CHECKED` |
| Trim at 1.3 Vs / roll rate with the rest | 29 % of travel / 269 | —, deg/s | `CL-B3-TRIM-USE-VT`, `-ROLL-RATE-VT` | `UNVERIFIED` |
| Cruise motor-out roll (E1 0.22 N·m): authority ratio | 15 (1.2° of elevon) | — | `CL-B3-MOTOROUT-ROLL-RATIO` | `UNVERIFIED` |
| **Cn_β, aft CG, 1.3 Vs** / cruise, target | **0.0286** / 0.0314 (≥ 0.03) | /rad | `CL-B3-CNB` / `CL-B3-CNB-CRUISE` | `FAIL` (−5 %) / `UNVERIFIED` |
| Short period ζ / Dutch roll ζ / spiral t2 | 0.45 / 0.32 / 4.0 s | — | `CL-B3-SP-ZETA`, `-DR-ZETA`, `-LAT-T2` | `UNVERIFIED` |
| Hover control / 5 m/s wind, 30 % diff: pitch, roll | 2.49, 5.20 (≥ 1.5) | — | `CL-B3-HOVER-PITCH/ROLL-RATIO` | `UNVERIFIED` |
| **Hover yaw, 3° cant: ratio / accel** | **1.15 / 1.15 rad/s²** (≥ 1.5 / 2) | — | `CL-B3-HOVER-YAW-RATIO/ACCEL` | `FAIL` → 7° cant |
| Cant needed for hover yaw | 6.1 (7° gives 2.23× / 2.24 rad/s²) | deg | `CL-B3-HOVER-CANT-REQ` | `FAIL` vs 3° |
| Hover pitch-trim share (split 1.19) | 9.7 % (≤ 12.5 %) | — | `CL-B3-HOVER-TRIM-USE` | `UNVERIFIED` |
| Transition: worst motor pitch share | 0.19 (≤ 0.60) at 8 m/s | — | `CL-B3-TRANS-PITCH-USE` | `UNVERIFIED` |
| AVL grid change of NP | 0.018 % c | — | `CL-B3-AVL-CONV` | `CHECKED` |

## What others must do

| # | Request | To |
|---|---|---|
| CR-B3-11 | `cg.x_range_m` [0.050, 0.055], target 0.0526; pod stays at −0.105; pack centroid at x −0.001 | A1, A3, D2 |
| CR-B3-12 | Motor cant 3° → 7° (or A2 lifts the 30 % cap for yaw) | A1, B4, D3, E1 |
| CR-B3-13 | Publish clmax-vs-elevon as a param; B2 AVL cross-check at R1 | B2 |
| CR-B3-14 | Half-fins 0.21 m high (Cn_β 0.037) with D5's foot splay | A1, D3, D5 |
| CR-B3-15 | `ARSPD_FBW_MIN` 15.6 m/s; FW yaw by motors optional; trims and back-transition moments | F4 |
| CR-B3-16 | `R-CG-RANGE` text; scope of the 30 % cap | A2 |

## Files

| File | What |
|---|---|
| `avl_model.py` · `avl/k09l.avl` · `avl/k09l.mass` · `avl/s5010.dat` | AVL generator, runner (incl. multi-CL trim sweeps with strip loads), cache; R1 model files for AVL 3.52 |
| `flight_models.py` | props/tubes/pod terms, hover authority (30 % cap), slipstream gap, quasi-steady transition |
| `sc_analysis.py` → `claims.json`, `results/sc_results.json` | 50 claims, critical-section CG scan, 4 planned tests |
| `run_avl_study.py` → `results/study.json` | D-17 layout cases, sensitivities, elevon chord sweep, Cn_β fixes, cant sweep, AVL MODE check, trim drag |
| `draw_cg.py` → `fig-b3-cg-stations.svg` | FIG B3-01 chordwise NP / CG range / A3 CG cases |
| `xfoil_elevon.py`, `xfoil/`, `avl/mh45.dat` | retired (MH 45, R0). Nothing reads them; B2's claims replace them |

## Open issues

1. The forward limit and the stall rest on B2's `UNVERIFIED` η and Δcm: ±20 % η moves the stall trim ±2.3° (~3 mm of
   CG). The twin's slow flight and glides (`T-B3-TWIN-NP`) close it.
2. The hover yaw disturbance model (10 % spanwise gust asymmetry) is an estimate. `T-B3-HOVER-WIND` tests it.
3. The transition model is quasi-steady. A SITL run with B3's aero table is next (F4).
