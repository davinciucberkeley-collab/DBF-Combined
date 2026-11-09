# F1 power distribution: summary

Status `PROPOSED`. Numbers `MODELLED` in `team/F1/power.py` (31 claims in `claims.json`, revision F1-R2); none bench-tested. Details:
`team/F1/POWER.md`, schematic `team/F1/power-schematic.svg`, derating data `team/F1/data/`.

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Main disconnect (CR-A2-08, CR-A4-09, CR-J1-04) | **Amass AS150U**, anti-spark; packs re-terminated | 70 A cont ≥ 37.8 A; 140 A momentary ≥ 120 A | `CL-F1-AS150U-CONT`, `CL-F1-AS150U-BURST` (supersedes `CL-J1-XT60-BURST`) | `UNVERIFIED` (reseller ratings) |
| XT60 | rejected | 35 / 30 A < 37.8 A; no cited rating ≥ 120 A | — | — |
| Pack's own leads | ≥ 10 AWG, cut to 0.10 m at re-termination; 12 AWG pack not accepted | rise 16.4 °C vs 20 °C limit; 12 AWG 28.4 °C | `CL-F1-PACKLEAD-RISE`, `-PEAK` | `UNVERIFIED` (gauge not on listing) |
| Pack-plug-to-bus path | 8 AWG, 0.15 m, twisted | rise 9.2 °C steady, 12.0 °C peak | `CL-F1-MAIN-RISE`, `-PEAK` | `MODELLED` |
| ESC leads (CR-A3-06) | **16 AWG**, 0.5 m, two grooves in the wing | rise 9.2 °C; 18 AWG 16.4 °C fails | `CL-F1-ESC-RISE`, `CL-F1-ESC18-RISE` | `MODELLED` |
| UBEC | **fitted**, 6 V 8 A class, 5 A fuse on its feed | required 5.2 A > FC servo BEC 4.5 A | `CL-F1-SERVO-BEC-REQ`, `CL-F1-UBEC-RATING` | `UNVERIFIED` (stall current) |
| Propulsion fuse | none (a blown fuse = crash) | limiter worst case 105 A < 140 A | `CL-F1-ILIM-WORST` | `MODELLED` |
| Sensing | FC power board, ≥ 38 A cont / ≥ 120 A peak | candidate 90 / 215 A | `CL-F1-SENSOR-CONT`, `-PEAK` | `UNVERIFIED` (F3) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Continuous design current (max of hover 29.9, cruise 29.8, climb 30.2) | 30.3 | A | `CL-F1-I-CONT` | `MODELLED` |
| Disconnect required, continuous / ≤ 60 s | 37.8 / 53.7 | A | `CL-F1-DISC-REQ-CONT`, `-SHORT` | `MODELLED` |
| Pack terminals → ESC pads, equivalent hot | 6.5 | mΩ | `CL-F1-R-EXT` | `MODELLED` |
| Drop at 30 A / at the 100 A limiter | 1.41 / 4.37 | % | `CL-F1-DROP-CONT`, `-PEAK` | `MODELLED` |
| Anti-spark pre-charge t95 / inrush | 180 / 1.1 | ms / A | `CL-F1-PRECHARGE-T95`, `CL-F1-INRUSH` | `MODELLED` |
| Power mass excluding the pack | 69 vs 45 allocated | g | `CL-F1-POWER-MASS` | **`FAIL`** (CR-F1-02 asks +25 g) |
| ESC leads, 4 pairs (harness) | 64.6 | g | `CL-F1-ESC-MASS` | `MODELLED` |

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/F1/power.py` | 31 claims; all margins ≥ +8 % except `CL-F1-POWER-MASS` (−53 % against 45 g) |
| `python -I redesign/proofs/build_graph.py` | no F1 errors; the build fails on drift in other roles' scripts (A1, B1, E2), none in F1 |
| Model hand check | 10 °C steady ampacity in free air: 18 AWG ~7.5 A, 16 AWG ~10 A, 10 AWG ~25 A; agrees with published single-wire charts from memory, `UNVERIFIED` until `T-F1-WIRE-HEAT` |

## Open issues

| Issue | Owner | Status |
|---|---|---|
| AS150U and SpeedyBee ratings are from resellers and search results; open the maker sheets before ordering | F1 | `UNVERIFIED` |
| 10 °C rule needs a duration basis (CR-F1-01); the 8 % margins depend on the routing in CR-F1-07 | A2, F2 | `PROPOSED` |
| Servo stall current 1.3 A assumed; decides whether the UBEC stays | D6, F1 | `UNVERIFIED` |
| Pack lead gauge unknown; must be ≥ 10 AWG (CR-F1-14) | I1, E2 | `UNVERIFIED` |
| Connector park in the pod is 30 mm (XT60); AS150U needs 60 mm (CR-F1-13) | D2 | `PROPOSED` |
| Bought items itemised (≈ $86 `EST`) in POWER.md; prices not quoted | I1 | `PROPOSED` |
| `subsystems/power/` (SPEC, parts.csv, interfaces.json, Fusion module) not yet written; `PWR-003…005` warn as missing from interfaces | F1 | next |

Change requests: `team/F1/CHANGE-REQUESTS.md` (CR-F1-01 … 15).
