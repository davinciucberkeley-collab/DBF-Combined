# C1 Loads — summary

Owner: C1 (loads engineer). Revision **C1-R5**, 2026-11-10, at params A1-R5 (D-62, D-65) and A3-R7.
Full report: [`LOADS.md`](LOADS.md). Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md). Claims: `claims.json`
(112 claims). Re-run: `python -I redesign/team/C1/loads.py` (~10 s), then `python -I redesign/proofs/build_graph.py`.

All loads are **limit** (largest expected in service) unless marked ult (= 1.5 × limit). The calculation is
`CHECKED`. Its inputs (thrust, CLmax, masses, capped VH, C5's simulated side load) are `UNVERIFIED` or `MODELLED`, so
every load stays `UNVERIFIED` until the stand, the level-speed log, the scale, the swing, the foot drop and the wing
proof replace them.

## Basis changes in R5

| Input | R4 | R5 | Source |
|---|---|---|---|
| Landing design factor | 6.0 | **6.6** | `P:requirements.landing_n_design` (D-65) |
| Foot side load (L4/L5) | 22.9 N (μ × corner) | **39.30 N** lim / 58.96 ult | `CL-C5-SIM3D-SIDE-LOAD` → `CL-C1-FOOT-SIDE-DESIGN(-ULT)` |
| CG x (MC-C / MC-P) / z | 0.050 / 0.0549; z free | **0.0466 / 0.0514; z 0.0185** | `P:cg.x_range_m`, `P:cg.z_target_m` (D-62) |
| Centre group, pack, harness | C1 lumps | **A3 group centroids** | `CL-A3-GROUPS` (CR-C1-33 done) |
| Model CG trim / inertia vs A3 | 28.7 mm / 0.91–1.00 | **7.2 mm / 0.90–1.02** (band 0.85–1.15) | `CL-C1-CG-TRIM-DX`, `-INERTIA-RATIO-MIN/-MAX` |

## Governing loads by structure

| Structure (consumer) | Quantity | Limit | Ult | Unit | Case | vs R4 |
|---|---|---|---|---|---|---|
| Spar root (C2) | bending resultant | 13.8 | 20.7 | N·m | L1 | +5 % |
| Wing (C2) | torsion / shear Vz | 5.6 / 21.8 | 8.4 / 32.8 | N·m / N | L4 / F7-VA | +12 % / +1 % |
| Fin root + saddle, each side (C4, C6) | force / moment | 59.4 / 15.0 | 89.2 / 22.5 | N / N·m | L1 / L4 | +8 % / **+57 %** |
| Half-fin at the wing plane, J-FINHALF (C4, C6) | torsion | 12.63 | 18.94 | N·m | L4 | **+71 %** |
| Half-fin section (C4) | bending | 10.9 | 16.3 | N·m | L5 | +43 % |
| Lower motor can, set-down (C4) | reaction, `CL-C1-G3-CAN-F` | 23.46 | 35.19 | N | G3 | new claim |
| Pod → wing, spar saddle + bond (C3) | force | 75.8 | 113.7 | N | L1 | −3 % |
| Pack → aft stop (C3) | resultant (design × 1.15 × 1.25 = 91.6) | 42.5 | 63.7 | N | L1 | new; above crash 73.75 ult |
| Foot (C5, D5) | upper foot / side / cut force | 44.4 / 39.3 / 53.2 | 66.6 / 59.0 / 79.7 | N | L1 / L4 | +10 % / +72 % / +34 % |

## Fin roots, spar saddles and pack stop at n 6.6 (D-65 check)

| Item | Result | Status |
|---|---|---|
| Fin roots | joint design moment 32.3 N·m (was 20.6), collar torsion 12.63 N·m; C1's scaling of C4's R4 margins: collar MS ≈ −0.32, fin face ≈ −0.29, block ≈ 0.0 | `UNVERIFIED` estimate → C4/C6 re-run (CR-C1-35) |
| Same with C5's μ ≤ 0.5 pad face (29.1 N) | torsion 9.38 N·m, design moment 25.4 N·m (block ≈ +0.26, collar ≈ −0.08) | recommended (CR-C1-36) |
| Spar saddles | pod saddle 75.8 N lim (−3 %); fin saddle force 59.4 N lim (+8 %) | `CHECKED` (loads) |
| Pack stop | 42.5 N lim; the landing now sizes the aft stop | `CHECKED` → C3 (CR-C1-37) |

## Transport (D7) and wing proof (H1)

| Item | Value | Status |
|---|---|---|
| Floor drop 0.3 m | n 10.09 vs 13.19 allowable | `CHECKED` (+31 %) |
| Aft wall on the feet | n 7.79 vs **10.76** (9.22 confirmed as a safe lower bound) | `CHECKED` (+28 %) |
| Nose wall, pod nose on the pad (new X6) | allowable **n 4.98** → 0.021 m (3/4 in) / **0.014 m** (1/2 in) vs D7's 0.059 m | `FAIL` vs 0.059 m, label-and-test (CR-C1-38) |
| GT-08 step 1, per side | pads y 0.120 / 0.250 / 0.355 / 0.465 m at **9.01 / 5.14 / 4.44 / 6.01 N**; relief 19.92 N | `PROPOSED` (CR-C1-39) |
| GT-08 step 2 (V-block at y 0.32 m) | pads 3 / 4 at **4.90 / 16.10 N** | `PROPOSED` (CR-C1-39) |

## Open

1. On C1's estimate the fin roots do not close at the 39.3 N side load. C4/C6 must re-run; the pad-face μ decision belongs to D5 and C5.
2. Nose-first box drop: D7 adds cradle x-stops or keeps it label-only.
3. Inputs are live (A3, C5, F4 republished during this run). VD still rests on F4's THR_MAX cap (H2 log).
4. Quasi-static only: no dynamic overshoot or vibration (C4, `R-VIBRATION`). The stall-line n at VD (5.22) is still a `FAIL`, held by F4's envelope (CR-C1-08).
