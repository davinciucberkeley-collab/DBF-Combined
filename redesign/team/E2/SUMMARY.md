# E2 battery / energy: summary

Status `PROPOSED`, revision **E2-R4**, 2026-11-10 (params A1-R4a, D-47 … D-59). Full report: `team/E2/ENERGY.md`.
Calculations: `team/E2/energy_claims.py` → `claims.json` (41 claims, 4 planned tests). No E2 claim fails. Nothing is
`VERIFIED`: no pack has been bought or weighed.

**Decision (D-58 answered).** Buy **2 × Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5** (2-pack, listed
551 ± 5 g, 135 × 46 × 49 mm), re-terminated to AS150U, one fully charged pack per sortie, **2 sorties per test day**
(D-12). Re-leading the held 680 g 130C XT60 pack is **not accepted**. I1 releases the pack cart after confirming
10 AWG leads at order (CR-E2-24).

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pack SKU | Ovonic 120C 4S 6500 hard case, EC5 → AS150U, JST-XH | — | `SRC-E2-OVONIC-120C-EC5` | `CHECKED` (listing) |
| Listed mass, worst / D-58 line | 0.556 / ≤ 0.601 (margin 0.045) | kg | `CL-E2-SKU-MASS-MARGIN` | `UNVERIFIED` |
| Mass carried / acceptance limit | 0.55 / ≤ 0.601 (was 0.68) | kg | `CL-E2-PACK-MASS` | `UNVERIFIED` (not weighed) |
| Body in the 160 × 52 × 53 mm bay, tightest | 1 (height, at +3 mm tolerance) | mm | `CL-E2-SKU-BAY-CLEAR` | `UNVERIFIED` |
| Discharge leads | 10 (inferred from EC5; confirm at order and on arrival) | AWG | `CL-E2-SKU-LEAD-AWG` | `UNVERIFIED` |
| Pack R warm / cold (cells + 6.5 mΩ harness) | 22.5 / 30.5 | mΩ | `P:electrical.r_ext_mohm`, `ASM-E2-R-CELL` | `UNVERIFIED` |
| Cruise after 2 min hover to 20 %, base / pess. (B1 227.8 / 300.6 W) | **12.6 / 6.8** (req. ≥ 5) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Same at the params' 240 W (E1, D-49) | 12.0 / 6.4 | min | `CL-E2-CRUISE-MIN-BASE-240`, `-PESS-240` | `UNVERIFIED` |
| Cruise before `BATT_LOW`, pess. (B1 / 240 W) | 6.4 / 6.1 (req. ≥ 5) | min | `CL-E2-CRUISE-TO-LOW-PESS`, `-240` | `UNVERIFIED` |
| Phase currents, pess.: climb / hover / fwd / back / descent / cruise | 35.5 / 30.1 / 43.5 / 40.0 / 30.1 / 22.4 | A | `CL-E2-I-*-PESS`, `CL-E2-HOVER-I-GATE`, `CL-E2-CRUISE-I-PESS` | `UNVERIFIED` |
| Peak current (limiter) / C-rate | 100 / 15.4 (limit 25) | A / C | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Worst-state T/W (one team claim) | 2.12 (≥ 1.6) | — | `CL-E1-TW-WORST` | `UNVERIFIED` |
| Thrust factor worst / fresh: E1 vs E2 bracket | 0.851 in 0.816–0.873 (+0.022) | — | `CL-E1-SAG-FACTOR` = `voltage_sag`, `CL-E2-SAG-BRACKET` | `UNVERIFIED` |
| Bus voltage at 100 A, 20 %, 10 °C | 11.87 (0.76 V/cell sag) | V | `CL-E2-V-BUS-WORST` | `UNVERIFIED` |
| Pack temperature at landing, 30 °C morning | 43 (limit 50) | °C | `CL-E2-PACK-T-END` | `UNVERIFIED` |
| `BATT_LOW_MAH` / `BATT_CRT_MAH` | 2600 / 1300 (unchanged at 240 W) | mAh | `CL-E2-BATT-LOW-MAH`, `-CRT-MAH` | `UNVERIFIED` |
| Sorties per day / window used / charge for 2 packs | 2 / 58.4 of 180 min / 2.0 h | — | `CL-E2-SORTIES-PACKS`, `-WINDOW-USED`, `CALC-E2-TESTDAY` | `UNVERIFIED` |

## SKU options (CR-I1-13)

| Option | Mass, g | Leads | Result |
|---|---|---|---|
| **Ovonic 120C 4S 6500 hard case, EC5, 2-pack** | 551 ± 5 | 10 AWG inferred | **named**; EUR 98.69 per pair on the EU page, inside I1's $119.88 pessimistic line |
| Tattu 4S 6750 25C, XT90 | 605 ± 10 | 10 AWG stated | fallback, only if A1 accepts A3-R6's 613 g line |
| Ovonic 130C 4S 6500, XT60 (held `P01`) | 680 | 12 AWG | rejected; re-leading not accepted (+33 g vs the 100 g overrun) |

## Action items this revision

| Item | Result |
|---|---|
| D-58 / CR-I1-13: name a SKU ≤ 601 g, ≥ 10 AWG | Done (above, CR-E2-24); acceptance 0.601 kg, lead-gauge step added to `T-E2-WEIGH` |
| Weigh the first pack on arrival | `T-E2-WEIGH` planned; `pack_log.csv` ready; pass ≤ 601 g, 10 AWG |
| D-49: sag 0.851; re-point `CL-E2-TW-SAG-WORST` at `CL-E1-TW-WORST` | E2 reads E1's re-run 0.851 / 2.12; the E2 id was retired in R3; A1's how-line is the last pointer (CR-E2-23a) |
| Re-run at 240 W if E1 and B1 reconcile | Not reconciled (B1 227.8 W); sensitivity claims published, all pass |
| Drifts | No E2 calculation drifts. The E3 drifts that cite E2 clear when E3 re-runs (CR-E2-27) |

## Open issues

- The lead gauge of the named SKU is inferred, not printed. If it arrives 12 AWG, the pair goes back (CR-E2-24a).
- Bay height clearance is 1 mm at the listing's +3 mm tolerance; 4 mm at nominal. Measure on arrival.
- B1's pessimistic cruise is 28 % below E2's own K09-based model (CR-E2-21); the first tune-flight current decides.
- Pack IR and capacity are assumptions until `T-E2-IR` and `T-E2-CAPACITY` run.

## Change requests

New: CR-E2-23 (A1: how-line, cruise minutes, 240 W swap), -24 (I1: pack SKU and order checks), -25 (A1: `battery`
params), -26 (F1, D2: EC5 re-termination, envelope), -27 (E3: r_ext re-point). Earlier ones: `CHANGE-REQUESTS.md`.

## How to verify

`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
