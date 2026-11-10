# A3 Mass properties: summary

Role A3 (mass-properties). Revision **A3-R6**, 2026-11-09 20:41, answering CR-A1-44 and CR-A1-53. Owns
`redesign/MASS-CG.md`. All numbers come from `python -I redesign/team/A3/mass_rollup.py` on all nine flying
`parts.csv`: D2-R5 pod (D-47 bay), F1's pack node at −0.022, E1's CAD centroids with stripped ESCs, D1's four plugs, D3-R4
fins, D5-R4 landing (spares `flight: false`), D6 mechanisms. Allocations are D-48 (2 355 g + 245 g reserve), checked equal
to `mass_budget.json`. The station rule reads the D-59 keys.

## Result

| Quantity | Value | Limit | Claim | Verifies | Status |
|---|---|---|---|---|---|
| Take-off mass, basic / predicted (growth 114 g) | 2 323 / 2 437 g | ≤ 2 600 g | `CL-A3-MASS-BASIC`, `-PREDICTED` | `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth: 503 / 550 / 680 g pack | +210 / +163 / +33 g | ≥ 100 g overrun | `CL-A3-GATE-MARGIN-503`, `CL-A3-GATE-MARGIN`, `-680` | `R-MASS-GATE` (`R-PACK-MASS`) | `MODELLED` / `MODELLED` / `FAIL` |
| Heaviest pack the overrun still covers | 613 g | — | from `CL-A3-GATE-MARGIN` | — | `MODELLED` |
| Worst subsystem / allocation | fins 436.4 / 418 g (1.044); pod 131.0 / 131 and propulsion 462.0 / 462 on the line | ≤ 1.0 | `CL-A3-ALLOC-WORST` | `R-MASS-ALLOC` | `FAIL` (CR-A3-26) |
| CG x, 550 g at the −0.022 datum | 0.0525 m (16.4 % c), range use 0.01 | 0.050–0.0549 m | `CL-A3-CG-X-RANGE` | `R-CG-RANGE` | `MODELLED` |
| CG x predicted | 0.0539 m (range use 0.58) | 0.050–0.0549 m | `CL-A3-CG-X-PRED` (new), `-PRED-RANGE` (new) | — | `MODELLED` |
| CG x, each pack at its D-59 station, basic and predicted | worst 0.89 (503 g on the stack: aft +0.3 mm predicted) | ≤ 1.0 | `CL-A3-CG-X-STATIONS` (new) | `R-CG-RANGE` | `MODELLED` (thin) |
| Stations 550 / 503 / 680 g | −0.024 (14 mm) / −0.0254 (stack) / −0.010 (none) m | bay −0.0254 … −0.010 | `CALC-A3-CG` `station_cases` | — | `MODELLED` |
| Pack slide beyond the bay travel; forward room at the datum | 0 mm; 3.4 mm | 0; ≥ 0 | `CL-A3-PACK-TRIM`, `CL-A3-PACK-FWD-ROOM` | `R-CG-RANGE` | `MODELLED` |
| Lateral / vertical CG | −1.1 mm / +0.018 m | ≤ 5 mm / −0.02 … +0.03 m | `CL-A3-CG-Y`, `CL-A3-CG-Z-RANGE` | `R-CG-RANGE` | `MODELLED` |
| Hover pitch-trim split upper/lower | 1.216 | ≤ 1.25 | `CL-A3-HOVER-SPLIT` | `R-HOVER-SPLIT` | `MODELLED` (+3 %) |
| Ixx / Iyy / Izz about the CG | 0.173 / 0.045 / 0.167 kg·m² | — | `CL-A3-IXX/IYY/IZZ` | — | `MODELLED` |

## CR-A1-44 / CR-A1-53, item by item

| Item | Done |
|---|---|
| D2's R5 bay, pack at `pod.pack_x_nominal_m` | D2-R5 and F1 published during the run; the four A3 bay overrides (`PWR-001`, `POD-004/-006/-008`, written as `=P:` expressions) were used while they were missing, then dropped. `ASM-A3-NOSE-STACK` 40.6 → 34.6 mm (stop −0.1212) |
| Per-pack stations | D-59 rule in `CALC-A3-CG`, reading `P:pod.pack_aft_travel_m` and `P:pod.pack_spacer_step_m`. Basic and predicted CG are both checked per pack (`CL-A3-CG-X-STATIONS`) |
| D-48 allocations | read from `params.json`, equal to `mass_budget.json` (2 355 + 245 g) |
| E1 CAD centroids (CR-E1-34) | used from `propulsion/interfaces.json`; ESC override reason updated to 7.6 g stripped |
| D1 four plugs 22 g | `WNG-E06` → `WNG-004-L/R`, `WNG-E07` (now qty 2) → `WNG-005-L/R` via `part_ids` (self-inertia boxes); the pack box is mapped onto `PWR-001` the same way |
| D5 `flight: false` spares, `GER-E02` | 7 spares excluded by the flag; `GER-E02` is not in the model, and no adders remain |
| `verifies=['R-HOVER-SPLIT']` | on `CL-A3-HOVER-SPLIT` in `claims.json` |
| `CL-A3-CG-X-RANGE` in 0.050–0.0549, three gate margins | published (0.01; +210 / +163 / +33 g) |
| `CL-A3-CG-X-PRED` (CR-A1-53) | published, 0.0539 m |
| `MASS-CG.md` | block regenerated; the verdict and the station table were rewritten by hand for A3-R6 |

During the run, three deliveries moved the CG from 0.0513 m (20:35: E1 and D6 lighter aft; the 680 g pack 0.4 mm off
the forward limit, which led to D-59) to 0.0525 m (20:41: D3-R4 fins +21 g aft, D2-R5; F2's harness −4.5 g at the end). The station note that A1 wrote
from the 20:35 run is now stale (CR-A3-27).

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/A3/mass_rollup.py` | 21 claims; block, `rollup/` refreshed; no roll-up warnings |
| `python -I redesign/team/A3/mass_rollup.py --check` | roll-up current |
| `python -I redesign/proofs/build_graph.py` | no `CALC-A3-*` drift and no A3 errors (684 drifts elsewhere; overall FAILED for other roles). Downstream drifts on A3 inputs are for B3, A1, F4, C5, C1 and H1 to re-run (CR-A3-28) |

Open CRs: CR-A3-17, CR-A3-25 to -28 in `CHANGE-REQUESTS.md`. Files: `mass_rollup.py`, `mass_model.csv`, `overrides.csv`,
`claims.json`, `rollup/ROLLUP.md`, `rollup/rollup.json`, `rollup/mass_items.json`; owned document `redesign/MASS-CG.md`.
