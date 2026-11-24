# E2 battery / energy: summary

> **Design round 2026-11-14, wave 2 (D-145, D-148, D-154).** `failsafe_rows()` counts from the pack's real
> capacity (`BATT_CAPACITY` = measured; 5.98 Ah on the 92 % pessimistic pack), not 6 500 mAh. **R-MISSION as flown
> fails:** cruise at 17 m/s before `BATT_LOW` (QRTL), pessimistic, **3.57 min** against 5.0
> (`CL-E2-CRUISE-TO-LOW-PESS-V17`; was 4.68 on the nameplate counter, which spent the reserve). The requirement's
> budget to the 20 % line passes at 5.11 min (`CL-E2-CRUISE-MIN-PESS-V17`). `BATT_LOW_MAH` 2 700 at 17 m/s. Pack
> pass line = `CL-A3-PACK-ACCEPT`, read live: **≤ 564 g** on 2026-11-14 (558 g of D-132 retired), re-read on the
> weigh day. Options for R-MISSION are the students' (A1.md §2 item 1). Report: `review/DESIGN-ROUND-2026-11-14/E2-W2.md`.
>
> **CDR fix round, 2026-11-13 (CDR-05; D-115, D-118).** Re-run on `electrical.r_ext_mohm` 7.9 mΩ (was 6.7): pack R
> 24.0 / 32.0 mΩ warm / cold, worst bus 11.85 → 11.73 V. Cruise before `BATT_LOW`, pessimistic, at the carried
> 253 W: 5.41 → **5.45 min** (`CL-E2-CRUISE-TO-LOW-PESS-240`, limit 5, +9 %; 5.38 on `r_ext` alone, then B1's base power
> rose with Oswald e 0.85, which lowers the factor applied to the pessimistic power); to the 20 % line 5.97 → 6.02 min. New
> claims for the 17 m/s fallback (D-96 c, the planning case of CDR decision B6), at E1's 286.2 W + 6 W: base
> 9.84 min, pessimistic **5.16 min** to the 20 % line (`CL-E2-CRUISE-MIN-PESS-V17`, +3 %) and **4.68 min before
> `BATT_LOW`** (`CL-E2-CRUISE-TO-LOW-PESS-V17`, limit 5: **fails, −6 %**, verifies `R-MISSION`). The pessimistic
> 17 m/s power scales B1's pessimistic 16 m/s power by the base ratio (`EST`). 49 claims; one fails. The rows
> below are E2-R5 (6.7 mΩ) unless marked; current values: `claims.json`.
>
> **Pack pass line.** `T-E2-WEIGH` passes a pack at or under `CL-E2-PACK-ACCEPT-KG`, which is read live from
> `CL-A3-PACK-ACCEPT` (D-154): **≤ 564 g** on 2026-11-14 (558 g by D-132, S4: 558.5 g after the 31 g structures contingency; 560 g by D-95, 592.6 g
> by D-64). SKU maximum 556 g, margin +8.4 g. The claim follows A1 on every re-run: while the landing parts list
> stood at 69.9 g during the fix round it read 546.5 g and `CL-E2-PACK-ACCEPT-KG`, `CL-E2-SKU-MASS-MARGIN` and
> `CL-E2-PACK-MASS` failed (`review/CDR-2026-11-13/fixes/S4.md`, CDR-12). Read the claim on the day of the weigh.

Status `PROPOSED`, revision **E2-R5**, 2026-11-10 (params A1-R5, D-61 … D-73). Full report: `team/E2/ENERGY.md`.
Calculations: `team/E2/energy_claims.py` → `claims.json` (44 claims, 4 planned tests). No E2 claim fails. Nothing is
`VERIFIED`: no pack has been bought or weighed.

**Decision (D-64).** The pack cart `P01` is **released to I1**: 2 × Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5
(one 2-pack, listed 551 ± 5 g, 135 × 46 × 49 mm), re-terminated to AS150U, one pack per sortie, **2 sorties per test
day** (D-12). I1 pays only after two order-time checks: (1) 10 AWG discharge leads confirmed; (2) EC5 / 4S / 6500 mAh /
hard case / 2 packs in the cart (release record: ENERGY.md §1a, CR-E2-28).

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pack SKU | Ovonic 120C 4S 6500 hard case, EC5 → AS150U, JST-XH | — | `SRC-E2-OVONIC-120C-EC5` | `CHECKED` (listing) |
| Acceptance line `PACK_ACCEPT_KG` = `CL-A3-PACK-ACCEPT` | 0.5644 on 2026-11-14, D-154 (was 0.5585 D-132, 0.5608 D-95, 0.5926 D-64); `T-E2-WEIGH` pass ≤ 564 g, re-read on the day | kg | `CL-E2-PACK-ACCEPT-KG` | `MODELLED` (read live) |
| Listed worst mass / margin to the line | 0.556 / +0.0025 (D-132) | kg | `CL-E2-SKU-MASS-MARGIN` | `UNVERIFIED` |
| Mass carried | 0.55 (until weighed) | kg | `CL-E2-PACK-MASS` | `UNVERIFIED` |
| Body in the 160 × 52 × 53 mm bay, tightest | 1 (height, +3 mm tolerance) | mm | `CL-E2-SKU-BAY-CLEAR` | `UNVERIFIED` |
| Discharge leads | 10 (inferred from EC5; order check 1) | AWG | `CL-E2-SKU-LEAD-AWG` | `UNVERIFIED` |
| Pack R warm / cold (cells + 6.7 mΩ harness) | 22.7 / 30.7 | mΩ | `P:electrical.r_ext_mohm`, `ASM-E2-R-CELL` | `UNVERIFIED` |
| Cruise after 2 min hover, base / pess. (B1 as designed 238.9 / 312.4 W) | **12.0 / 6.3** (req. ≥ 5) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Same at the carried 240 W (A1 carries these) | **12.0 / 6.3** | min | `CL-E2-CRUISE-MIN-BASE-240`, `-PESS-240` | `UNVERIFIED` |
| Cruise before `BATT_LOW`, pess. (B1 / 240 W) | 6.0 / 5.9 (req. ≥ 5) | min | `CL-E2-CRUISE-TO-LOW-PESS`, `-240` | `UNVERIFIED` |
| Phase currents, pess.: ground / climb / hover / fwd / back / descent / cruise | 0.4 / 35.5 / 30.1 / 43.5 / 40.1 / 30.1 / 24.0 | A | `CL-E2-I-*-PESS`, `CL-E2-HOVER-I-GATE`, `CL-E2-CRUISE-I-PESS` | `UNVERIFIED` |
| Peak current (limiter) / C-rate | 100 / 15.4 (limit 25) | A / C | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Thrust factor worst / fresh: E1 in E2's bracket | 0.851 in 0.816–0.873 (+0.022) | — | `CL-E1-SAG-FACTOR`, `CL-E2-SAG-BRACKET` | `UNVERIFIED` |
| Bus voltage at 100 A, 20 %, 10 °C | 11.85 (0.77 V/cell sag) | V | `CL-E2-V-BUS-WORST` | `UNVERIFIED` |
| Pack temperature at landing, 30 °C morning (adiabatic) | 43.8 (limit 50) | °C | `CL-E2-PACK-T-END` | `UNVERIFIED` |
| `BATT_LOW_MAH` / `BATT_CRT_MAH` | 2600 / 1300 (8 mAh before the line steps to 2700) | mAh | `CL-E2-BATT-LOW-MAH`, `-CRT-MAH` | `UNVERIFIED` |
| Sorties per day / window used / charge for 2 packs | 2 / 57.2 of 180 min / 2.0 h | — | `CL-E2-SORTIES-PACKS`, `-WINDOW-USED`, `CALC-E2-TESTDAY` | `UNVERIFIED` |

## Action items this revision

| Item | Result |
|---|---|
| Release the pack cart with I1 (D-64), two order-time checks | Released on the record in ENERGY.md §1a (CR-E2-28). Check 1 (10 AWG) is still open: the product page does not print the gauge and E2's re-read was rate-limited (HTTP 429) |
| `PACK_ACCEPT_KG` = `CL-A3-PACK-ACCEPT` | Read live from A3's claim (D-154; 0.5644 kg on 2026-11-14, 0.5585 kg by D-132, 0.5926 kg when written); new claim `CL-E2-PACK-ACCEPT-KG`; `CL-E2-PACK-MASS` and `T-E2-WEIGH` pass at ≤ it |
| Re-run `CALC-E2-BUDGET-PESS` on 312.4 W and r_ext 6.7 | Done: pessimistic 6.8 → **6.3 min**, `BATT_LOW` after 6.0 min; at 240 W 6.3 / 5.9 min. A1's 6.4 → 6.3 (CR-E2-29) |
| Retire F1's old profile-assumption text reference (CR-F1-27) | Done: phase-current claims point at `CALC-F1-PROFILE` / `CL-F1-PROFILE`; ground phase is now a claim too |
| Leftover from an interrupted edit | The script's `ASM-E2-R-EXT` mirror check was removed (the mirror was already retired; the script would not run) |

## Open issues

- Lead gauge of the named SKU is inferred, not printed. If the seller says 12 AWG, the cart is not paid (CR-E2-28).
- Bay height clearance is 1 mm at the listing's +3 mm tolerance; measure on arrival.
- Pessimistic cruise: E2's own K09-based model gives 405 W against B1's 337 W (+20 %); on it `BATT_LOW` would trigger
  at 4.9 min, under 5. The first tune flight's logged cruise current decides (`T-E2-MISSION-LOG`).
- The pessimistic mass scaling uses A3's stored 2.436 kg; A3's R5 re-run (about 2.458 kg) moves it by < 0.05 min.
- E1 still stores `CL-E1-TW-WORST` / `-SAG-FACTOR` on 6.5 mΩ; it re-runs on 6.7 (D-67).

## Change requests

New: CR-E2-28 (I1: pack cart release record), CR-E2-29 (A1: `cruise_after_hover_pess_min` 6.3, notes), CR-E2-30
(F1: updated phase currents, ground claim). Earlier ones: `CHANGE-REQUESTS.md`.

## How to verify

`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
