# A3 Mass properties: summary

Role A3 (mass-properties). Revision A3-R4, 2026-11-09, answering CR-A1-25 (R3 roll-up). Owns `redesign/MASS-CG.md`.
All numbers come from `python -I redesign/team/A3/mass_rollup.py`. Fins (D3), pod (D2-R3), landing (D5) and propulsion
(E1, with its new `interfaces.json`) come from the designers' `parts.csv`; wing (C2 397.4 g), power (F1 69.0 g),
avionics (F3 78.5 g) and the ESC leads (F1 64.6 g) are the designers' claimed numbers in `mass_model.csv`; the rest of
the harness and the mechanisms are A3 estimates.

## Result (pack at the D-24 station x −0.001 m)

| Quantity | Value | Limit | Claim | Verifies | Status |
|---|---|---|---|---|---|
| Take-off mass, basic | 2 339 g | ≤ 2 600 g | `CL-A3-MASS-BASIC` | `R-MASS-GATE` | `MODELLED` |
| Take-off mass, predicted (growth 154 g) | 2 493 g | ≤ 2 600 g | `CL-A3-MASS-PREDICTED` | `R-MASS-GATE` | `MODELLED` |
| Gate margin, 550 g pack | +107 g | ≥ 100 g overrun | `CL-A3-GATE-MARGIN` | `R-MASS-GATE` | `MODELLED` (+7 %) |
| Gate margin, 680 g pack | −23 g | ≥ 100 g | `CL-A3-GATE-MARGIN-680` (new) | `R-MASS-GATE`, `R-PACK-MASS` | `FAIL` |
| Gate margin, 503 g pack | +154 g | ≥ 100 g | `CL-A3-GATE-MARGIN-503` (new) | `R-MASS-GATE` | `MODELLED` |
| Worst subsystem / allocation (D-38) | 1.072 harness 112.6 / 105 g; fins 417.0 / 408; pod 127.3 / 122 g | ≤ 1.0 | `CL-A3-ALLOC-WORST` | `R-MASS-ALLOC` | `FAIL` |
| CG x | 0.0548 m (17.1 % c); predicted 0.0570 m | 0.050–0.055 m | `CL-A3-CG-X-RANGE` (0.92) | `R-CG-RANGE` | `MODELLED` (0.2 mm inside) |
| Forward slide a 503 g pack needs beyond the crush stack | 0.9 mm (needs 4.3, has 3.4) | 0 | `CL-A3-PACK-TRIM` (new) | `R-CG-RANGE` | `FAIL` |
| Pack centroid for the 0.0526 m target / crush-stack limit | −0.0104 / −0.0044 m | — | `CL-A3-PACK-X-REQ` | — | `PROPOSED` |
| Lateral CG | −0.8 mm | ≤ 5 mm | `CL-A3-CG-Y` (new) | `R-CG-RANGE` | `MODELLED` |
| CG z | +0.016 m | −0.02 … +0.03 m | `CL-A3-CG-Z-RANGE` | `R-CG-RANGE` | `MODELLED` |
| Hover pitch-trim split upper/lower | 1.190 | ≤ 1.25 | `CL-A3-HOVER-SPLIT` | `R-HOVER-SPLIT` (new link) | `MODELLED` (+5 %) |
| Ixx / Iyy / Izz about the CG | 0.171 / 0.043 / 0.164 kg·m² | — | `CL-A3-IXX/IYY/IZZ` | — | `MODELLED` |

## Recommendation

| Decision | Number | Owner | CR |
|---|---|---|---|
| Forward stop 6 mm forward (−0.1002 → −0.1062 m), pack flown against the crush stack at x −0.0104 m | CG 0.0526 (550 g), 0.0539 (503 g), 0.0493 → 0.0504 m with a 4 mm spacer (680 g); predicted 0.0547 m | A1, D2, C5 | CR-A3-15 |
| Weigh the first pack; above 557 g the overrun is not covered | gate margin −1 g per g of pack | E2 | CR-A3-16 |
| Recover 22 g of overruns (harness 8, fins 9, pod 5 g) or release them from the reserve | releasing all three leaves the reserve 1 g short | A1, F2, D3, D2 | CR-A3-14 |

## What changed in this revision (CR-A1-25)

| Item | A3-R3 | A3-R4 |
|---|---|---|
| Pack `PWR-E01`, straps | x −0.034 m | x −0.001 m (D-24); D2-R3 straps at −0.0012 |
| Pack growth | 24 % (to 680 g) inside "predicted" | 0 %; 503 / 550 / 680 g reported as separate gate cases |
| Allocations | R2 (2 200 g, reserve 400 g) | `mass_budget.json` D-38 (2 324 g, reserve 276 g), checked equal to `params.json` each run |
| Wing, power, avionics, ESC leads | A3 estimates | C2, F1, F3 numbers (+ 5 g edge tape and label) |
| Fin clip rows, horns (CR-A4-17) | 2 × 30 g per fin; 4 horns | `FIN-005` 4 × 15 g per half-fin (fallback only: D3 carries bonds in its parts); 2 horns `MEC-004` |
| Servos | 12 g | 18.5 g (B2 CR-B2-10: 17–20 g class) |
| Pack travel | ±30 mm assumed | D2-R3: spacers 0–22 mm (8 mm flown), forward travel clamped by the crush stack (`ASM-A3-NOSE-STACK` 40.6 mm) |
| Roll-up rules | spare kits and 0 g fasteners counted or placed at the subsystem centroid; propulsion collapsed onto the centreline (Ixx 0.097 kg·m²) | ground spares excluded, 0 g lines skipped, positions from the A3 model when no node exists, adders and overrides listed in the block |

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/A3/mass_rollup.py` | 18 claims; `MASS-CG.md` block and `rollup/` refreshed; no roll-up warnings |
| `python -I redesign/team/A3/mass_rollup.py --check` | roll-up current |
| `python -I redesign/proofs/build_graph.py` | no A3 calc drifts. Downstream DRIFT on A3 inputs: `CALC-B3-ROLL/-MODES/-HOVER/-HOVER-TRIM`, `CALC-H1-WEIGH`, `CALC-C1-ENVELOPE/-LANDING`, `CALC-C5-DROP/-DROP-DYN/-WIND` (CR-A3-19). The other failures are not A3's |

D3, D2 and E1 changed their files during this run; the numbers above are from the last run on those files. Open CRs:
CR-A3-14 to -19 in `CHANGE-REQUESTS.md`.

Files: `mass_rollup.py`, `mass_model.csv`, `overrides.csv`, `claims.json`, `rollup/ROLLUP.md`, `rollup/rollup.json`,
`rollup/mass_items.json`, `CHANGE-REQUESTS.md`; owned document `redesign/MASS-CG.md`.
