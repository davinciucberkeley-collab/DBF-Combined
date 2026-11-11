# A3 Mass properties: summary

Role A3 (mass-properties). Revision **A3-R7**, 2026-11-10 15:15, answering CR-A1-64 and CR-C1-33. Owns
`redesign/MASS-CG.md`. All numbers come from `python -I redesign/team/A3/mass_rollup.py` on the nine flying
`parts.csv` as found on disk at 15:15: D2-R6 pod (D-62 bay, C3 fixes, 145.8 g), D3-R5 fins (435.9 g), E1 rev 8
stations (D-61), D1's re-run wing (391.7 g). D2 and D5 had not yet written their summaries. Allocations D-63
(2 386 + 214 g), checked equal to `mass_budget.json`. Pack cases D-64: 546 / 551 / 590 g.

## Result

| Quantity | Value | Limit | Claim | Status |
|---|---|---|---|---|
| Take-off mass, basic / predicted (growth 116 g) | 2 345 / 2 462 g | ≤ 2 600 g | `CL-A3-MASS-BASIC`, `-PREDICTED` | `MODELLED` |
| Gate margin after growth, 546 / 550 / 590 g pack | +142 / +138 / +98 g | ≥ 100 g overrun | `CL-A3-GATE-MARGIN-546`, `CL-A3-GATE-MARGIN`, `-590` | `MODELLED` / `MODELLED` / `FAIL` (−1.8 g) |
| Pack acceptance (heaviest pack the overrun covers) | 588.2 g | ≥ 556 g SKU max | `CL-A3-PACK-ACCEPT` (new) | `MODELLED` |
| Worst subsystem / allocation | propulsion 462.0 / 462 (1.000) | ≤ 1.0 | `CL-A3-ALLOC-WORST` | `MODELLED` |
| CG x, 550 g pack at the −0.032 datum, basic / predicted | 0.0486 / 0.0502 m (range use 0.15 / 0.49) | 0.0466–0.0514 m | `CL-A3-CG-X-RANGE`, `-PRED`, `-PRED-RANGE` | `MODELLED` |
| Stations 546 / 551 / 590 g (D-59 rule, D-62 bay) | −0.032 / −0.030 / −0.026 m; worst range use 0.67 | ≤ 1.0 | `CL-A3-CG-X-STATIONS` | `MODELLED` (thin: 0.8 mm aft) |
| CG height basic / predicted | +0.0185 / +0.0182 m (range use 0.14) | 0.010–0.025 m | `CL-A3-CG-Z` (new), `-CG-Z-PRED` (new), `-CG-Z-RANGE` | `MODELLED` |
| Lateral CG; hover split | −1.2 mm; 1.216 | ≤ 5 mm; ≤ 1.25 | `CL-A3-CG-Y`, `CL-A3-HOVER-SPLIT` | `MODELLED` |
| Ixx / Iyy / Izz about the CG | 0.1744 / 0.0460 / 0.1701 kg·m² | — | `CL-A3-IXX/IYY/IZZ` | `MODELLED` |
| Group centroids and own inertias (8 groups, per station) | table; closure 6e-16 | ≤ 0.001 | `CL-A3-GROUPS` (new), `-GROUPS-CLOSURE` (new) | `MODELLED` |

## CR-A1-64 / CR-C1-33, item by item

| Item | Done |
|---|---|
| Re-run on D2-R6, D3-R5, E1's D-61 centroids | done on the delivered files; D5-R5 had not landed: C5's +5 g shoe fix is the adder `GER-R5-SLEEVE` (`EST`) |
| D-63 allocations 2 386 / 214 g | read from `params.json`, equal to `mass_budget.json` |
| D-64 pack cases; retire 503 / 680 g | `ASM-A3-PACK-RANGE` [546, 590], `ASM-A3-PACK-NOMINAL` 551 g; `-503` / `-680` kept one revision as unlinked aliases (CR-A3-33) |
| D-62 bay and range [0.0466, 0.0514] | D2-R6 positions; the pack at −0.032 by an A3 override until F1 moves `PWR-001` (CR-A3-37); `ASM-A3-NOSE-STACK` re-based on the −0.140 nose |
| `CL-A3-CG-Z` basic and predicted | published (0.01853 / 0.01816 m) |
| Pack acceptance from `CL-A3-GATE-MARGIN` | `CL-A3-PACK-ACCEPT` 588.2 g, 4.4 g under A1's 592.6 (growth on the R5 `EST` parts, CR-A3-32) |
| Group centroids and own inertia for C1 | `CALC-A3-GROUPS` / `CL-A3-GROUPS`, also in `rollup/rollup.json#groups` (CR-A3-34) |
| MASS-CG.md block | regenerated; header, verdict, station table and pack rows rewritten by hand |
| Tell A1 to retire `ASM-A1-A3-PACK-X`, `-STACK-DX`, `-R5-ADDED-G` and cite `CL-A3-CG-Z` | CR-A3-31 |

`mass_rollup.py` changes: overrides now carry `if_x_m` and adders `if_sub_g`, so a stop-gap retires itself (with a
warning) once the owner republishes. The six D2 bay overrides and four pod adders written for this run retired that
way when D2-R6 landed, and were then removed.

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/A3/mass_rollup.py` | 28 claims; block and `rollup/` refreshed; no roll-up warnings |
| `python -I redesign/team/A3/mass_rollup.py --check` | roll-up current |
| A3 self-check: the four `CALC-A3-*` re-run from stored `input_values` | all re-run to stored outputs (no drift) |
| Dangling citations of A3 ids in other roles' `claims*.json` | none |
| `python -I redesign/proofs/build_graph.py` | `UNVERIFIED`: did not finish within 10 min, or in a second background run, while other roles were re-running; run it again at the phase gate |

Open CRs: CR-A3-17, CR-A3-31 to -37 in `CHANGE-REQUESTS.md`. When D5-R5 and F1's node land, re-run: the stop-gaps
retire themselves. Files: `mass_rollup.py`, `mass_model.csv`, `overrides.csv`, `claims.json`, `rollup/ROLLUP.md`,
`rollup/rollup.json`, `rollup/mass_items.json`; owned document `redesign/MASS-CG.md`.
