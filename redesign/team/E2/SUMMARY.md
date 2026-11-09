# E2 battery / energy: summary

Status `PROPOSED`, revision E2-R2, 2026-11-09. Full report: `team/E2/ENERGY.md`. Calculations:
`team/E2/energy_claims.py` → `claims.json` (25 claims, 4 planned tests). `build_graph.py`: no error on any E2 node
(0 E2 drift; the build still fails on other roles' drift). One E2 claim fails (below). Nothing is `VERIFIED`: no pack
has arrived yet.

**Decision.** Ovonic 4S 6500 mAh hard-case LiPo, one fully charged pack per sortie, **2 sorties per test day**
(D-12; packs 3–4 deferred). It is still the only candidate that passes the 2.6 kg gate, 5 min of pessimistic cruise
and the 100 A peak together.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pack | LiPo 4S 6.5 Ah, 96.2 Wh, XT60 + JST-XH | — | `params.json#battery` | `PROPOSED` |
| Pack mass carried / acceptance limit | 0.55 / ≤ 0.68 | kg | `CL-E2-PACK-MASS` | `PROPOSED` (not weighed) |
| Cruise power used (B1 × 1.05 circuit), base / pess. | 319 / 417 | W | `CL-B1-CRUISE-P`, `-P-PESS` | `UNVERIFIED` |
| Cruise after 2 min hover to 20 %, base / pess. | 9.6 / 5.1 (req. ≥ 5) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Cruise before `BATT_LOW`, pessimistic | **4.6 (req. ≥ 5)** | min | `CL-E2-CRUISE-TO-LOW-PESS` | **`FAILS`** (−7 %) |
| Same two, 11×5.5MR (E1 ratio on B1), indicative | 6.5 / 6.1 | min | `CL-E2-CRUISE-MIN-PESS-55`, `-TO-LOW-PESS-55` | `UNVERIFIED` |
| Hover / transition / cruise / peak current (pess.) | 29.9 / 42.9 / 29.8 / 100 | A | `CL-E2-HOVER-I-GATE`, `CALC-E2-SAG` | `UNVERIFIED` |
| Peak C-rate | 15.3 (limit 25) | C | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Thrust factor from sag, 20 % charge, 10 °C / T/W | 0.76 (params 0.72) / 1.89 (≥ 1.6) | — | `CL-E2-SAG-F-WORST`, `CL-E2-TW-SAG-WORST` | `UNVERIFIED` |
| Pack temperature at landing, 30 °C morning | 45 (limit 50) | °C | `CL-E2-PACK-T-END` | `UNVERIFIED` |
| `BATT_LOW_MAH` / `BATT_CRT_MAH` | 2700 / 1300 | mAh | `CL-E2-BATT-LOW-MAH`, `-CRT-MAH` | `UNVERIFIED` |
| Sorties per test day / window used | 2 / 52 of 180 | — / min | `CL-E2-SORTIES-PACKS`, `CL-E2-WINDOW-USED` | `UNVERIFIED` |
| Charge per pack / 2 packs | 59 / 2.0 | min / h | `CL-E2-CHARGE-MIN`, `CALC-E2-TESTDAY` | `UNVERIFIED` |

## Action items this revision

| Item | Result |
|---|---|
| Re-run on B1's cruise model (27 calcs drifted) | Done. The budget now reads `CL-B1-CRUISE-P` / `-P-PESS` directly, so a B1 re-run propagates. B1 has delivered only the 11×4.5MR model; its 11×5.5MR re-run is still open (CR-E2-11) |
| Weigh the first pack before `checked` on `SRC-OVONIC-4S6500` (CR-A3-08) | Not possible yet: the order arrives ~20 Nov. Acceptance procedure, limits and `pack_log.csv` are ready; the script picks the weighed mass up on re-run. `checked` stays unset |
| Plan 2 sorties per test day (D-12) | Done: 2 sorties, 52 min of the 180 min window, 2.0 h charge the afternoon before |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| With B1's 11×4.5MR power, `BATT_LOW` triggers before 5 min of pessimistic cruise | Mission shortfall in the worst stack, not a safety issue; the 11×5.5MR is expected to close it | B1, A1, A2 |
| Base mission cruise is 9.6 min, not 12.3 or 15.1 | The 10 min stretch target is not met on the 11×4.5MR | A1, B1 |
| Peak current is 100 A with the limiter | Sag factor 0.76; params' 0.72 is conservative | A1, F1 |
| `BATT_LOW_MAH` 2700 provisional | F4 parameter file | F4 |

## Open issues

- Pack mass, size, IR and capacity are from listings or assumptions until `T-E2-WEIGH`, `-IR` and `-CAPACITY` run.
- Cruise power waits for B1's 11×5.5MR re-run; hover margin waits for the twin's logs.
- Charging room and disposal site: H3.

## Change requests

New: CR-E2-11 (B1 re-run), -12 (A1 params), -13 (F4 `BATT_LOW_MAH`), -14 (F1 currents), -15 (A3 pack line after
the weigh), -16 (I2 test days). Earlier requests and their disposition: `team/E2/CHANGE-REQUESTS.md`.

## How to verify

`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
