# B3 stability and control — K09-L summary

Status: `PROPOSED` (B3, 2026-11-09). Full report: `S-AND-C.md`. Requests: `CHANGE-REQUESTS.md` (10).
Re-check: `python -I redesign/team/B3/sc_analysis.py` (AVL cached in `avl/cache/`), then
`python -I redesign/proofs/build_graph.py` (2026-11-09: OK, every stored number re-computes).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP, wing + fins (AVL) / whole aircraft (props, pod) | 0.0696 / 0.0641 | m | `CL-B3-XNP-AERO` / `CL-B3-XNP` | `CHECKED` / `UNVERIFIED` |
| **CG range** (fwd – aft) | **0.040 – 0.049** (13.2–16.4 % c) | m | `CL-B3-CG-FWD`, `CL-B3-CG-AFT` | `UNVERIFIED` |
| CG target, static margin there | 0.044, 6.6 % | m, — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| Current CG vs forward limit (A3) | −13.7 (move +18 mm) | mm | `CL-B3-CG-NOW-FWD` | `FAIL` |
| Trimmed stall / 1.3 Vs at 2.6 kg | 12.73 / 16.55 | m/s | `CL-B3-VS-TRIM`, `CL-B3-VT-TRIM` | `FAIL` (12.0 / 15) |
| Elevon trim at 15 m/s, α | −6.8 (TE up), 10.2 | deg | `CL-B3-ELEVON-TRIM-CRUISE`, `CL-B3-ALPHA-CRUISE` | `UNVERIFIED` |
| Elevons: chord, area, travel | 22 % c, 17.2 % S, ±25 | —, —, deg | `CL-B3-ELEVON-FRAC-MAX` | `CHECKED` |
| Roll pb/2V at the stall, time to 60° | 0.151, 0.59 | —, s | `CL-B3-ROLL-PB2V`, `CL-B3-ROLL-T60` | `UNVERIFIED` |
| Short period ζ at 15 m/s | 0.44 (ωn 7.8 rad/s) | — | `CL-B3-SP-ZETA` | `UNVERIFIED` |
| **Cn_β, cruise** | **−0.105** (need ≥ +0.02) | /rad | `CL-B3-CNB` | `FAIL` |
| Directional divergence, time to double | 0.16 | s | `CL-B3-LAT-T2` | `FAIL` |
| Cruise yaw by motors / need at β 10° | 1.38 | — | `CL-B3-YAW-ACTIVE-RATIO` | `FAIL` (≥ 2) |
| Hover control / 5 m/s wind: pitch, roll | 8.3, 25.8 | — | `CL-B3-HOVER-PITCH/ROLL-RATIO` | `UNVERIFIED` |
| Hover yaw / wind: no cant, 3° cant | 1.08, 3.75 | — | `CL-B3-HOVER-YAW-RATIO(-CANT)` | `FAIL`, `UNVERIFIED` |
| Hover pitch-trim share (split 1.16) | 8 % (≤ 12.5 %) | — | `CL-B3-HOVER-TRIM-USE` | `UNVERIFIED` |
| Transition: worst motor pitch share | 0.18 (≤ 0.60) at 8 m/s | — | `CL-B3-TRANS-PITCH-USE` | `UNVERIFIED` |
| AVL grid change of NP (coarse/medium/fine) | 0.014 % c | — | `CL-B3-AVL-CONV` | `CHECKED` |

## Decisions and what others must do

| # | Decision / request | To |
|---|---|---|
| 1 | CG range 0.040–0.049 m, target 0.044; SM ≥ 5 % kept; elevons unchanged (22 % c, both panels, ±25°) | A1 (CR-B3-01) |
| 2 | Cruise yaw: motor tubes through the wing at x +0.03…+0.045 m, pod forward 73–87 mm (O4/O4b); fallback O7 | A1, D3, C4, D1, D2 (CR-B3-02) |
| 3 | CG +18 mm now: pod group 52 mm aft (not 96 mm), or follow CR-B3-02 | A3, D2 (CR-B3-03) |
| 4 | FW yaw by differential thrust (≥ 15 rad/s), `ARSPD_FBW_MIN` ≥ 16.6 m/s | F4 (CR-B3-04) |
| 5 | 3° tangential motor cant for hover yaw | D3, E1 (CR-B3-05) |
| 6 | MH 45 cm and elevon effectiveness; the trimmed stall needs cruise ≥ 16.6 m/s or +0.06 CLmax | B2, B1 (CR-B3-06/07) |

## Files

| File | What |
|---|---|
| `avl_model.py` · `avl/k09l.avl` · `avl/k09l.mass` · `avl/mh45.dat` | AVL geometry generator, runner, parser, cache; baseline model files (open directly in AVL 3.52) |
| `flight_models.py` | props/tubes/pod terms, trimmed CLmax, hover authority, slipstream gap, quasi-steady transition |
| `sc_analysis.py` → `claims.json`, `results/sc_results.json` | 34 claims with their calcs, assumptions, sources and 4 planned tests |
| `run_avl_study.py` → `results/study.json` | yaw-fix options, elevon chord sweep, cm sensitivity, AVL MODE cross-check, trim drag |
| `xfoil_elevon.py` → `xfoil/` | MH 45 viscous cm and elevon effectiveness (Re 3e5) |
| `draw_cg.py` → `fig-b3-cg-stations.svg` | chordwise NP / CG-limit figure |

## Open issues

1. Everything rests on `UNVERIFIED` section data (MH 45 cm, elevon effectiveness, CLmax 0.9) and the ±50 % prop normal-force slope. The twin glide tests close them.
2. ArduPilot fixed-wing yaw by motors on a copter tailsitter is not yet confirmed (F4, J1).
3. The transition model is quasi-steady; a SITL with B3's aero table is the next check (F4).
