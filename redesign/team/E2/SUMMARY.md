# E2 battery / energy: summary

Status `PROPOSED`, 2026-11-09. Full report: `team/E2/ENERGY.md`. Calculations: `team/E2/energy_claims.py` →
`claims.json` (22 claims, 4 planned tests). `build_graph.py`: OK, 0 drift, no E2 claim fails. All claims are
`UNVERIFIED` until a pack is weighed, capacity-tested and IR-tested.

**Decision.** Ovonic 4S 6500 mAh hard-case LiPo, one fully charged pack per sortie. It is the only candidate that
passes the 2.6 kg gate, 5 min of pessimistic cruise and the 120 A peak together.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pack | LiPo 4S 6.5 Ah, 96.2 Wh, XT60 + JST-XH | — | `params.json#battery` | `PROPOSED` |
| Pack mass (listings 522–551; one 680) | 0.55 | kg | `CL-E2-PACK-MASS` | `UNVERIFIED` |
| Pack envelope | 0.139 × 0.047 × 0.049 (params says 0.035 high) | m | `SRC-E2-OVONIC-LISTINGS` | `UNVERIFIED` |
| Cruise after 2 min hover to 20 %, base / pessimistic | 15.1 / 6.4 (req. ≥ 5) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Hover-only sortie, pessimistic | 9.4 | min | `CL-E2-HOVER-ONLY-MIN-PESS` | `UNVERIFIED` |
| Hover / transition / peak current | 29.9 / 42.9 / 117 | A | `CALC-E2-BUDGET-PESS`, `CALC-E2-SAG` | `UNVERIFIED` |
| Peak C-rate | 18.5 (limit 25) | C | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Thrust factor from sag, 20 % charge, 10 °C | 0.72 (params 0.93) | — | `CL-E2-SAG-F-WORST` | `UNVERIFIED` |
| Hover T/W at the gate, worst pack state | 1.76 (req. ≥ 1.6) | — | `CL-E2-TW-SAG-WORST` | `UNVERIFIED` |
| Pack temperature at landing, 30 °C morning | 44 (limit 50) | °C | `CL-E2-PACK-T-END` | `UNVERIFIED` |
| `BATT_LOW_MAH` / `BATT_CRT_MAH` | 2600 / 1300 | mAh | `CL-E2-BATT-LOW-MAH`, `-CRT-MAH` | `UNVERIFIED` |
| Charge time per pack / 4 packs | 59 / 3.9 | min / h | `CL-E2-CHARGE-MIN`, `-H-4` | `UNVERIFIED` |
| Sorties per test day, 2 packs / window limit | 2 / 4 | — | `CL-E2-SORTIES-PACKS`, `-WINDOW` | `UNVERIFIED` |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| The pessimistic cruise is 6.4 min, not 12 | R-MISSION still passes (+27 %), with no room left for further pessimism | A1, B1 |
| The sag factor is 0.72 at the end of a cold flight, not 0.93 | T/W 1.76 still passes 1.6. Keep packs warm | A1, E1, F4 |
| The real pack is 49 mm tall | The pod's ~50 mm inside height does not fit the pack | D2, A1 |
| The Admiral 4000 fallback gives 2.3 min of pessimistic cruise | Drop it as the fallback | A1, I1 |
| Two packs give two sorties per morning | Packs 3–4 cost $87.37, which takes the reserve to $234 (< $309) | A1, I1, I2 |

## Open issues

- Pack mass, dimensions, IR and capacity all come from listings or assumptions. Weigh and test the first pack
  (`T-E2-*`).
- The cruise model (CD0, η) belongs to B1. The hover margin needs logs from the twin.
- Room for the charging station and the disposal site: H3.

## Change requests

The 10 requests are in `team/E2/CHANGE-REQUESTS.md`: A1 (params), D2 (pack bay), F4 (failsafe parameters), F1
(design currents), A1/I1 (packs 3–4), H3 (handling), E3 (heat), B1 (cruise model), H1/H2 (tests), I2 (test days).

## How to verify

`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
