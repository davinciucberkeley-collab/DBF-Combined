# A3 Mass properties: summary

Role A3 (mass-properties). Revision A3-R3, 2026-11-09, after CR-A1-11 (D-17, D-18, CR-A2-04). Owns
`redesign/MASS-CG.md`. All numbers come from `python -I redesign/team/A3/mass_rollup.py`. No `parts.csv` exists yet, so
every line is the A3 bottom-up model (`mass_model.csv`, 43 lines).

## Result

| Quantity | Value | Limit | Claim | Verifies | Status |
|---|---|---|---|---|---|
| Take-off mass, basic | 2 145 g | ≤ 2 600 g | `CL-A3-MASS-BASIC` | `R-MASS-GATE` | `UNVERIFIED` (estimates) |
| Take-off mass, predicted (basic + growth by maturity) | 2 492 g | ≤ 2 600 g | `CL-A3-MASS-PREDICTED` | `R-MASS-GATE` | `UNVERIFIED` |
| Gate margin after growth | 108 g | ≥ 100 g overrun | `CL-A3-GATE-MARGIN` | `R-MASS-GATE` | `CHECKED` (+8 %) |
| Worst subsystem / allocation | 1.000 (power 595/595 g; fins 369/370 g) | ≤ 1.0 | `CL-A3-ALLOC-WORST` | `R-MASS-ALLOC` | `CHECKED` (zero margin) |
| CG x, pack 29 mm ahead of pod centre | 0.044 m (13.8 % c) | 0.040–0.049 m | `CL-A3-CG-X-RANGE` (0.10 of half-range) | `R-CG-RANGE` | `UNVERIFIED` (range at R0) |
| CG z | +0.017 m | −0.02 … +0.03 m | `CL-A3-CG-Z-RANGE` (0.47) | `R-CG-RANGE` | `UNVERIFIED` |
| Pack centroid for the CG target | x = −0.034 m | — | `CL-A3-PACK-X-REQ` | — | `PROPOSED` |
| Pack fore face to pod nose (outside skin) | 1 mm | ≥ 0 | `CL-A3-PACK-FWD-ROOM` (new) | — | passes on paper, no room for the wall: CR-A3-11 |
| Hover pitch-trim split upper/lower | 1.194 | ≤ 1.25 (`P:requirements.hover_split_max`, D-18) | `CL-A3-HOVER-SPLIT` | — | `UNVERIFIED` (+4 %) |
| Ixx / Iyy / Izz about the CG | 0.160 / 0.043 / 0.154 kg·m² | — | `CL-A3-IXX/IYY/IZZ` | — | `MODELLED` |

## What changed in this revision (CR-A1-11)

| Item | Before | Now |
|---|---|---|
| Hover split limit | `ASM-A3-SPLIT-MAX` 1.10 (A3 placeholder, `FAIL` −9 %) | assumption removed; claim limit is `P:requirements.hover_split_max` 1.25 (pass +4 %) |
| CG range claims | verified `R-STATIC-MARGIN` (B3's) | verify `R-CG-RANGE` (CR-A2-04) |
| `CL-A3-ALLOC-WORST` | verified nothing | verifies `R-MASS-ALLOC` (CR-A2-04) |
| Pack station (`PWR-E01`, and its strap `POD-E02`) | pod centre, x = −0.005 m; CG 0.051 m (`FAIL` −52 %) | 29 mm forward, x = −0.034 m (D-17); CG 0.044 m (pass +90 %) |
| Fins rows `FIN-E04/05/06` | old 0.18 m bridge saddle 15 g, bridged-joint clips 40 g, glue 10 g (each); fins 371 g, `FAIL` by 1 g | D-04 through-core block 20 g, bond along tube + clips 30 g, consumables 14 g (each); fins 369 g |
| New claim | — | `CL-A3-PACK-FWD-ROOM`: the D-17 station leaves 1 mm to the outside of the pod nose |

The fins change brings stale rows up to the D-04 hardware. It was not made to hit the number. Each mass is justified
in the `basis` column of `mass_model.csv`. Fins now sit 1 g under their allocation, which is no real margin.

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/A3/mass_rollup.py` | 14 claims written; `MASS-CG.md` block and `rollup/` refreshed |
| `python -I redesign/team/A3/mass_rollup.py --check` | roll-up current |
| `python -I redesign/proofs/build_graph.py` | no A3 errors. Downstream DRIFT in B3 (`CALC-B3-CG-CHECK`, `-ROLL`, `-HOVER`, `-HOVER-TRIM`) from the new A3 values: CR-A3-13. Other drifts (A5, B1) are not caused by A3 |

## Open items

| CR | To | Issue |
|---|---|---|
| CR-A3-11 | D2, A1 | Pack at the D-17 station does not leave room for the pod nose wall. Forward slide 0, aft 29 mm. Use 26 mm forward (CG 0.0448 m) or move the pod nose to −0.110 m |
| CR-A3-12 | A1 | Fins and power at zero allocation margin. The reserve (400 g) is 47 g short of growth + overrun (447 g) |
| CR-A3-13 | B3 | Re-run `sc_analysis.py` on the new CG, split and inertia |
| CR-A3-08 | E2 | Weigh the pack first (503–680 g). It decides the gate margin, and a 680 g pack puts the CG on the 0.040 m forward limit |

Files: `mass_rollup.py`, `mass_model.csv`, `claims.json`, `rollup/ROLLUP.md`, `rollup/rollup.json`,
`rollup/mass_items.json`, `CHANGE-REQUESTS.md`; owned document `redesign/MASS-CG.md`.
