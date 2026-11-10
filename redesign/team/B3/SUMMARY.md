# B3 stability and control: K09-L summary (R3)

Status: `PROPOSED` (B3, 2026-11-09, params A1-R3, A3 roll-up and B4 swirl as of 15:04). Full report: `S-AND-C.md`.
Requests: `CHANGE-REQUESTS.md` (CR-B3-17…21 new). Re-check: `python -I redesign/team/B3/sc_analysis.py` (2 s with
the AVL cache), `run_avl_study.py`, `draw_cg.py`, then `python -I redesign/proofs/build_graph.py` (no B3 drift or id
errors; A1's `CALC-A1-CG-RANGE` and C5's stance calc drift on the new B3 CG claims and must re-run).

**CR-A1-26 answer: both R1 failures are closed at R3, and the claim ids are unchanged.** Cn_β is now 0.0357 /rad and
hover yaw 3.15×. The range moves 0.3 mm forward to 0.0495–0.0550 m. Two new findings. First, the pack at x −0.001
leaves the CG only 0.15 mm ahead of the aft limit, so move its mark to −0.012 (CR-B3-18). Second, the 21.7 Hz
symmetric torsion mode caps the hover pitch crossover at 4.5 Hz (CR-B3-19).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| NP: wing + fins (AVL) / whole aircraft (props −1.95 mm, pod −0.95 mm) | 0.0738 / 0.07095 | m | `CL-B3-XNP-AERO` / `CL-B3-XNP` | `CHECKED` / `UNVERIFIED` |
| **CG range** (fwd – aft) | **0.04953 – 0.05495** (15.5–17.2 % c) | m | `CL-B3-CG-FWD`, `CL-B3-CG-AFT` | `UNVERIFIED` |
| CG target, static margin there | 0.05224, 5.85 % | m, — | `CL-B3-CG-TARGET`, `CL-B3-SM-TARGET` | `UNVERIFIED` |
| A3 R3 CG, pack at x −0.001 | 0.0548: +5.3 mm fwd / **+0.15 mm aft** margin | m | `CL-B3-CG-CENTRED-FWD/AFT` | `UNVERIFIED` (thin) → CR-B3-18 |
| Pack station for the target (550 g) / forward travel left | −0.0119 / 3.1 | m / mm | `CL-B3-PACK-SLIDE-LEFT` | `UNVERIFIED` |
| Ribner props at the aft limit: arm, Cn_β, NP shift | 63.2 mm, −0.0040 /rad, −1.95 mm | — | `CL-B3-PROP-ARM-AFT`, `-CNB-AFT`, `-DXNP` | `UNVERIFIED` |
| Trimmed CLmax / Vs at target, 2.6 kg | 0.797 / 11.91 (≤ 12) | —, m/s | `CL-B3-CLMAX-TRIM`, `CL-B3-VS-TRIM` | `UNVERIFIED` |
| **1.3 Vs at the forward limit** (`ARSPD_FBW_MIN` 15.6 stands) | **15.53** (≤ 16) | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` |
| Elevon trim / α at 16 m/s | −6.1 (TE up) / 8.4 | deg | `CL-B3-ELEVON-TRIM-CRUISE`, `-ALPHA-CRUISE` | `UNVERIFIED` |
| Elevons: chord, area, travel; trim at 1.3 Vs; roll rate | 22 % c, 17.2 % S, ±25°; 29 %; 267°/s | — | `CL-B3-ELEVON-FRAC-*`, `-TRIM-USE-VT`, `-ROLL-RATE-VT` | `CHECKED` / `UNVERIFIED` |
| **Cn_β, aft limit, 1.3 Vs** / cruise, target | **0.0357** / 0.0390 (≥ 0.03) | /rad | `CL-B3-CNB` / `CL-B3-CNB-CRUISE` | `UNVERIFIED` (pass +19 %) |
| Short period ζ / Dutch roll ζ / spiral t2 | 0.45 / 0.32 / 4.07 s | — | `CL-B3-SP-ZETA`, `-DR-ZETA`, `-LAT-T2` | `UNVERIFIED` |
| Hover 5 m/s ratio, 30 % diff: pitch / roll | 2.48 / 4.69 (≥ 1.5) | — | `CL-B3-HOVER-PITCH/ROLL-RATIO` | `UNVERIFIED` |
| **Hover yaw at 7°: ratio / accel** (B4 R3 1.79; low bracket 0.48) | **3.15 / 3.22 rad/s²** (2.23 / 2.28) | — | `CL-B3-HOVER-YAW-RATIO/ACCEL` (`-LOW`) | `UNVERIFIED` (pass) |
| **Hover pitch loop GM with the 21.7 Hz mode** (F4 4.0 Hz) / max crossover | **7.4 dB** / **4.5 Hz** (5 Hz gives 5.1 dB) | dB / Hz | `CL-B3-FLEX-GM-PITCH`, `CL-B3-XOVER-MAX-PITCH` | `MODELLED` |
| Hover yaw loop GM with the 11.7 Hz mode (F4 1.8 Hz) / max crossover | 16.3 dB / 2.4 Hz | dB / Hz | `CL-B3-FLEX-GM-YAW`, `CL-B3-XOVER-MAX-YAW` | `MODELLED` |
| Transition: worst motor pitch share | 0.20 (≤ 0.60) at 8 m/s | — | `CL-B3-TRANS-PITCH-USE` | `UNVERIFIED` |

## What others must do

| # | Request | To |
|---|---|---|
| CR-B3-17 | `cg.x_range_m` [0.050, 0.0549], `cg.x_target_m` 0.0522; re-run `CALC-A1-CG-RANGE` | A1 (A3, C5) |
| CR-B3-18 | Pack mark x −0.012 for 550 g (680 g: 0.000; 503 g: forward stop) | A1, A3, D2 (H1, H3) |
| CR-B3-19 | Hover pitch crossover ≤ 4.5 Hz, gyro filter ≤ 40 Hz, static notch after the tap test, measure motor lag | F4 (C2, H2) |
| CR-B3-20 | T-B4-YAW to settle the yaw factor (0.48 vs 1.79) | B4 (H1) |
| CR-B3-21 | Publish torsion high corners, damping, station inertia as claims | C2 |
| CR-B3-13, -16, -09 | B2 clmax table and AVL cross-check; A2 `R-CG-RANGE` text; H1/H2 tests (marks at 0.050 / 0.0549) | B2, A2, H1, H2 |

## Files

| File | What |
|---|---|
| `sc_analysis.py` → `claims.json`, `results/sc_results.json` | AVL, NP, CG limits, Ribner at the aft limit, stall, trim, authority, modes, hover, torsion-mode loops, transition |
| `hover_loop.py` | hover rate-loop models with the torsion modes (standard library; margins and closed-loop roots) |
| `avl_model.py` · `avl/k09l.avl` · `avl/k09l.mass` · `avl/s5010.dat` | AVL generator, runner, cache; R3 model files for AVL 3.52 |
| `flight_models.py` | props/tubes/pod terms, hover authority, slipstream gap, quasi-steady transition |
| `run_avl_study.py` → `results/study.json` | R3 layout, sensitivities, elevon chord sweep, fin options, cant sweep, AVL MODE check, trim drag |
| `draw_cg.py` → `fig-b3-cg-stations.svg` | FIG B3-01 chordwise NP / CG range / A3 CG |

## Open issues

1. Aft CG margin 0.15 mm with the pack at −0.001 until CR-B3-18 lands; T-B3-CG-BALANCE on the built aircraft decides.
2. Hover pitch margin rests on a 40 ms motor lag and C2's 21.7 Hz mode (both `UNVERIFIED`); 25 ms lag gives 4.2 dB.
3. The forward limit rests on B2's η and Δcm: ±20 % η moves the stall trim ±2.3° (~3 mm of CG).
4. Hover yaw factor 0.48–1.79 between B4's models; both pass at 7°. Spiral t2 4.07 s is 2 % over its limit.
