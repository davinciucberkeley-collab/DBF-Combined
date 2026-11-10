# E2 battery / energy: summary

Status `PROPOSED`, revision E2-R3, 2026-11-09. Full report: `team/E2/ENERGY.md`. Calculations:
`team/E2/energy_claims.py` → `claims.json` (35 claims, 4 planned tests). No E2 claim fails, and `build_graph.py`
reports no drift on any E2 calculation (the build still fails on other roles' drift). Nothing is `VERIFIED`: no pack
has arrived yet (order ~20 Nov).

**Decision.** Ovonic 4S 6500 mAh hard-case LiPo, re-terminated to AS150U, one fully charged pack per sortie,
**2 sorties per test day** (D-12). It is still the only candidate that passes the 2.6 kg gate, 5 min of pessimistic
cruise and the 100 A limiter together.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pack | LiPo 4S 6.5 Ah, 96.2 Wh, AS150U + JST-XH | — | `params.json#battery` | `PROPOSED` |
| Pack mass carried / acceptance limit | 0.55 / ≤ 0.68 | kg | `CL-E2-PACK-MASS` | `PROPOSED` (not weighed) |
| Pack R warm / cold (cells + 6.5 mΩ harness) | 22.5 / 30.5 | mΩ | `P:electrical.r_ext_mohm`, `ASM-E2-R-CELL` | `UNVERIFIED` |
| Cruise power used (B1 rev 2 × 1.05 circuit), base / pess. | 239 / 316 | W | `CL-B1-CRUISE-P`, `-P-PESS` | `UNVERIFIED` |
| Cruise after 2 min hover to 20 %, base / pess. | **12.7 / 6.8** (req. ≥ 5) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Cruise before `BATT_LOW`, pessimistic | 6.4 (req. ≥ 5) | min | `CL-E2-CRUISE-TO-LOW-PESS` | `UNVERIFIED` (R2 `FAILS` closed) |
| Phase currents, pess.: climb / hover / fwd trans. / back trans. / descent / cruise | 35.5 / 30.1 / 43.5 / 40.0 / 30.1 / 22.4 | A | `CL-E2-I-*-PESS`, `CL-E2-HOVER-I-GATE`, `CL-E2-CRUISE-I-PESS` | `UNVERIFIED` |
| Peak current (limiter) / C-rate | 100 / 15.4 (limit 25) | A / C | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Worst-state T/W (one team claim: E1 model, E2 pack) | 2.12 on current params (E1 stores 2.18), ≥ 1.6 | — | `CL-E1-TW-WORST` | `UNVERIFIED` |
| Thrust factor worst / fresh: E1 vs E2 physical bracket | 0.851 vs 0.816–0.873 | — | `CL-E1-SAG-FACTOR`, `CL-E2-SAG-BRACKET` | `UNVERIFIED` (inside bracket, +0.019) |
| Bus voltage at 100 A, 20 %, 10 °C | 11.87 (0.76 V/cell sag) | V | `CL-E2-V-BUS-WORST`, `CL-E2-SAG-V-WORST` | `UNVERIFIED` |
| Pack temperature at landing, 30 °C morning | 43 (limit 50) | °C | `CL-E2-PACK-T-END` | `UNVERIFIED` |
| `BATT_LOW_MAH` / `BATT_CRT_MAH` | **2600** / 1300 | mAh | `CL-E2-BATT-LOW-MAH`, `-CRT-MAH` | `UNVERIFIED` |
| Sorties per test day / window used | 2 / 58.5 of 180 | — / min | `CL-E2-SORTIES-PACKS`, `CL-E2-WINDOW-USED` | `UNVERIFIED` |
| Charge per pack / 2 packs | 59 / 2.0 | min / h | `CL-E2-CHARGE-MIN`, `CALC-E2-TESTDAY` | `UNVERIFIED` |

## Action items this revision (CR-A1-31)

| Item | Result |
|---|---|
| Re-run on B1 rev 2 and `electrical.r_ext_mohm` 6.5 | Done. The calcs read `P:electrical.r_ext_mohm` and `P:requirements.pack_capacity_min_frac` (CR-A2-17). Published values are 12.7 / 6.8 min, not the params' 13.7 / 7.3: B1 has since re-run for the pod (227.8 / 300.6 W), and 6.5 mΩ costs another 0.1 min. `BATT_LOW_MAH` 2600 |
| One worst-state T/W claim with E1 (D-35) | E2 adopts E1's model: under the 100 A limiter, thrust follows power, not V². The limiter binds in every pack state (109 A unlimited even cold at 20 %, `CL-E2-LIMITER-BINDS-WORST`). E2's 0.76 / 1.89 claims are retired. A1 sets `voltage_sag` from `CL-E1-SAG-FACTOR` (0.851 once E1 re-runs) |
| Phase currents as claims (CR-F1-04) | Done: 6 currents, 6 durations and the highest phase current. Charge lead and the AS150U re-termination procedure are in ENERGY.md §5–6 |

## Findings others depend on

| Finding | Effect | To |
|---|---|---|
| E1's stored claims predate its own r_ext re-point; E3 and H1 still read `ASM-E2-R-EXT` (now a 6.5 mΩ mirror) | stored outputs drift until each re-runs; E1's T/W becomes 2.12 | E1, E3, H1 (CR-E2-17) |
| The params' cruise minutes, cruise power and `voltage_sag` are stale | 12.7 / 6.8 min, B1 227.8 W, sag 0.851 | A1 (CR-E2-18) |
| E2's independent pessimistic cruise model is 28 % above B1's | if E2's model were right: ~5.2 min of cruise and `BATT_LOW` at ~4.7 min; the first tune-flight current decides | B1 (CR-E2-21) |

## Open issues

- Pack mass, size, IR and capacity are from listings or assumptions until `T-E2-WEIGH`, `-IR` and `-CAPACITY` run.
- Pessimistic cruise power depends on B1's drag build-up (last finding above); the hover margin waits for the twin's logs.
- The lead gauge (≥ 10 AWG) and the shipped connector are confirmed at order (CR-F1-14, CR-I1-06). Charging room and
  disposal site: H3.

## Change requests

New: CR-E2-17 (E1, E3, H1: r_ext), -18 (A1: params), -19 (F1: profile), -20 (F4: `BATT_LOW_MAH` 2600), -21 (B1:
drag gap), -22 (I2: window). The dispositions of earlier requests are in `team/E2/CHANGE-REQUESTS.md`.

## How to verify

`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
