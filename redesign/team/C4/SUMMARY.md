# C4 — Fin and motor-tube structures (S1 simulation round, 2026-11-10)

> **R6 (2026-11-13, D-90 ... D-93, Dillon Alcouffe):** mount grip 12 -> 18 mm: `CL-C4-D3-MOUNT-K-EST` 2 235 vs
> `-REQ` 1 455 N·m/rad (nominal tube; the R5 1 531 vs 2 229 closed CR-H1-24), the D-80 short outboard cheek now in
> the model, FE nominal 2 200. Station 22 mm collar, 6 mm lower; collar mass corrected 5.7 -> 11.6 g. Separation
> nominal 0.228 (shell); the 70 / 3 GPa corner is a record and `CL-C4-D3-TUBE-E-REQ` 69.7 GPa / `-G-REQ` 4.01 GPa are
> the tube-test pass lines. Strip force 2 233 N design, pins 103 N at 12 mm. 3-D (`sim_fin.py`) re-run on the D-90
> geometry: `CL-C4-SIM-SEP` 0.095 -> 0.155 (fails 0.20; lower quarter 229 Hz vs 237.6 needed), face MS drawn
> -0.29 -> -0.58 (hot spot, not converged), extended cheeks +0.63. The S1 verdict table below is older text.

Motor tubes, half-fins, brace, station collar, strips, mounts and the through-core block of the K09-L quad tailsitter.
S1 re-ran the fin quarters as 3-D solid FE on the settled geometry (D3-R4 fin, D5-R4 shoe, A3-R6a masses), three
meshes each, against the R4 shell/beam model. Reports: `SIMULATION-REPORT.md` (S1), `BOOM-STRUCTURES.md` (R4 sizing).
Claims: `claims.sim.json` (S1), `claims.d3.json` (R4, re-run today), `claims.json` (R1 shared assumptions).

## Verdict

**Vibration passes with less margin (0.29). The R4 tip `FAIL` does not reproduce in 3-D:** the drawn D5 shoe gives
face MS +0.11 (bounded by a non-converging corner), not −0.54. The proof test on an as-drawn article decides whether
D5 needs the 25 mm cheek extension (CR-C4-36). No requirement newly fails. Fins mass is still over (434.8 g vs 418 g).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| First station mode, upper / lower (3-D, Richardson, GCI 1.7 / 1.1 %) | 262.4 / 255.5 | Hz | `CL-C4-SIM-F1-UP`, `-F1-LO` | `MODELLED` |
| Separation from 1P/2P (hover 5 416, cruise 5 946 rpm), need ≥ 0.20 | 0.29 | — | `CL-C4-SIM-SEP` | `MODELLED` |
| Same, R4 shell with today's inputs | 0.35 (A3 masses 0.33) | — | `CL-C4-D3-SEP`, `CL-C4-SIM-SEP-PLATE-A3` | `CHECKED` |
| Face MS at the D5 shoe as drawn (3-D bound / R4 shell) | +0.11 / −0.54 | — | `CL-C4-SIM-MS-FACE-DRAWN`, `CL-C4-D3-MS-FACE` | `MODELLED` |
| Face MS, cheeks to \|z\| 0.171 m (3-D) | +1.70 | — | `CL-C4-SIM-MS-FACE-PROP` | `MODELLED` |
| Face MS away from discontinuities (converged) | +0.42 | — | `CL-C4-SIM-MS-FACE-FAR` | `MODELLED` |
| Edge-strip MS, L4 | +2.04 | — | `CL-C4-SIM-MS-STRIP` | `MODELLED` |
| Foot deflection, L4 limit (3-D / shell) | 3.7 / 9.3 | mm | `CL-C4-SIM-FOOT-DEFL`, `CL-C4-D3-FOOT-DEFL` | `MODELLED` |
| Side-load moment through the bare board (3-D / shell) | 0.47 / 1.06 | — | `CL-C4-SIM-BOARD-SHARE` | `MODELLED` |
| Mount rocking stiffness needed (bench pass now ≥ 1 100) | 1 030 | N·m/rad | `CL-C4-D3-MOUNT-K-REQ` | `UNVERIFIED` |
| SU2 benchmark error (Richardson) / hex8 vs SU2 | −0.68 % / 4.7 × 10⁻¹¹ | — | `CL-C4-SIM-BENCH-ERR`, `-BENCH-CODES` | `CHECKED` |
| Fins mass vs 418 g allocation | 434.8 | g | `CL-C4-D3-FINS-MASS` | `FAIL` (A1) |

## What S1 found

| Finding | Consequence | Status |
|---|---|---|
| Strip pair clamped in the D5 cheeks carries 53 % of the tip twist (the shell model cannot) | CR-C4-30 held; test decides (CR-C4-36) | `MODELLED` |
| Hot-spot at the 8 mm cheek corner does not converge (order < 0.5) | as-drawn MS +0.03 to +0.85; bound +0.11 used | `UNVERIFIED` |
| Strip tails in the collar tongue are load-bearing; unbonded → LE corner MS −0.17 | build inspection (CR-C4-37) | `PROPOSED` |
| Separation 0.37 → 0.29: cruise rpm +52, motor +3.2 g, 3-D −3.5 % | still passes; re-run trigger above 6 390 rpm (CR-C4-39) | `MODELLED` |
| Panel mode 71–73 Hz, 21 % below 1P hover (station KE < 4 %) | tap the board centre too (CR-C4-38) | `MODELLED` |
| SU2 CG/ILU and FGMRES/ILU do not converge on the laminate; no PaStiX in this build | hex8 direct solver, verified against SU2 (CR-C4-40) | `CHECKED` |

## Requests raised (S1)

| Id | To | Short |
|---|---|---|
| CR-C4-36 | D5, H1 | hold CR-C4-30; proof article as drawn decides |
| CR-C4-37 | D3 | strip-tail bond as a build inspection item |
| CR-C4-38 | H1 | gauges and predictions for the proof test; tap the board centre |
| CR-C4-39 | A1, A2 | separation 0.29; re-run triggers |
| CR-C4-40 | A1 | SU2 solver limits on laminated solids |
| CR-C4-41 | H1, D3 | mount stiffness pass level ≥ 1 100 N·m/rad |

## How to verify

`python -I redesign/team/C4/sim_fin.py` (cached < 2 min; cold ~3 h), `python redesign/team/C4/sim/sim_plots.py`,
`python -I redesign/team/C4/fin_structures_d3.py`, `python -I redesign/proofs/build_graph.py` (no C4 drift).
Hardware: `T-C4-FIN-PROOF` (as drawn), `T-C4-MOUNT-STIFF`, `T-C4-TAP-D3`, `T-C4-TUBE-BEND`, `-TORSION`.
