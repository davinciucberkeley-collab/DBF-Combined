# Change requests from E2 (battery / energy engineer)

Revision E2-R5, 2026-11-10. Numbers are from `team/E2/energy_claims.py` → `team/E2/claims.json`. All are
`UNVERIFIED` until `T-E2-WEIGH`, `T-E2-CAPACITY` and `T-E2-IR` have run.

## Open (new in R5)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-E2-28 | I1 (cc A1, F1) | **Pack cart `P01` released (D-64).** Order one 2-pack Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5 (SKU and URL as CR-E2-24). Before paying, tick and keep the evidence for: (1) **10 AWG** discharge leads stated by the listing, a lead photo, or a written seller answer (12 AWG or no answer → do not pay, tell E2 and F1); (2) cart shows **EC5 / 4S / 6500 mAh / hard case / 2 packs**; (3) total inside the $119.88 pessimistic pack line. Copy the release record (ENERGY.md §1a) into `ORDER-PLAN.md` and lift the `P01` HOLD. No substitute without A1 and E2: the Tattu 4S 6750 (605 ± 10 g) is over the acceptance line. | `CL-E2-PACK-ACCEPT-KG` 0.5926 kg (= `CL-A1-PACK-ACCEPT`); SKU worst 0.556 kg, margin +36.6 g (`CL-E2-SKU-MASS-MARGIN`); `CL-E2-SKU-LEAD-AWG` 10 inferred, not printed (E2's re-read on 2026-11-10 got HTTP 429) |
| CR-E2-29 | A1 | `params.json#performance`: `cruise_after_hover_pess_min` 6.4 → **6.3** (`CL-E2-CRUISE-MIN-PESS-240` 6.29 on 312.4 W and 6.7 mΩ; B1-basis `CL-E2-CRUISE-MIN-PESS` 6.33); `cruise_after_hover_min` stays **12.0** (11.98); note: cruise to `BATT_LOW` 5.9 min (`CL-E2-CRUISE-TO-LOW-PESS-240`, was 6.1). `cruise_current_a` note: E2 pessimistic cruise current **24.0 A** (`CL-E2-CRUISE-I-PESS`, was 22.4). `battery.mass_kg` note: E2's acceptance is `CL-E2-PACK-ACCEPT-KG`, read from `CL-A1-PACK-ACCEPT`. | D-67 asked E2 to re-run on 312.4 W (expected about 6.2): result 6.3; the D-13 conservative pair is the 240 W one |
| CR-E2-30 | F1 | `CALC-F1-PROFILE` re-reads the claims (no copy needed): pessimistic cruise **24.0 A** (was 22.4), back-transition 40.1, others within 0.1 A; highest phase 43.5 A unchanged. Cruise duration 380 s (was 407). Ground phase is now `CL-E2-I-GROUND-PESS` 0.41 A / `CL-E2-T-GROUND-PESS` 180 s: `ASM-F1-GROUND` can go. CR-F1-27 done on E2's side. | 312.4 W and r_ext 6.7 |

## Closed in R5

| # | Disposition |
|---|---|
| CR-E2-24, -25, -26 | accepted (D-64); CR-E2-24 superseded by CR-E2-28 (release record) |
| CR-E2-23 | (b), (c) accepted (D-67); A1 carries the 240 W values; (a) remains A1's how-line item |
| CR-E2-17, CR-E2-27 | closed: `ASM-E2-R-EXT` retired, no role reads it |
| CR-E2-19 | closed with CR-F1-27 |

## Requests to E2 answered in R5

| From | Request | Answer |
|---|---|---|
| D-64 | Release the pack cart with I1; `PACK_ACCEPT_KG` = `CL-A1-PACK-ACCEPT`; `T-E2-WEIGH` pass line | CR-E2-28; `CL-E2-PACK-ACCEPT-KG` 0.5926 kg read live; `T-E2-WEIGH` passes at ≤ it |
| D-67, CR-B1-20 | Re-run `CALC-E2-BUDGET-PESS` on 312.4 W and r_ext 6.7 | 6.3 min (+27 %), `BATT_LOW` after 6.0 / 5.9 min; CR-E2-29 |
| CR-F1-27 | Retire the profile-assumption text reference; optionally emit the ground phase | Done (CR-E2-30) |

## Open from R4 (dispositions under Closed in R5)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-E2-24 | I1 (cc F1, A3, A1) | **Answer to CR-I1-13 / D-58: release the pack cart on a new `P01`.** Buy **2 × Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5 plug (2-pack)**, listed 551 ± 5 g, 135 × 46 × 49 mm, JST-XH balance (https://www.ampow.com/products/2-pack-ovonic-4s-6500mah-120c-lipo-hardcase-ec5-1-8-rc-car, or the same SKU from Ovonic US). Two checks before paying: (a) the listing or the seller confirms **10 AWG** discharge leads (the page does not print the gauge; EC5 contacts take 8–10 AWG); 12 AWG → stop, tell E2 and F1; (b) EC5, 4S, 6500 mAh, hard case, 2 packs in the cart. Price seen: EUR 98.69 for the pair on the EU page; re-price `P01` in USD. Do **not** buy the held 130C XT60 SKU (680 g, 12 AWG). Fallback only if the EC5 SKU is unavailable and A1 accepts the 613 g line: Tattu 4S 6750 25C XT90 (605 ± 10 g, 10 AWG stated, about USD 74–83 each). | `CL-E2-SKU-MASS-MARGIN` +45 g under 601 g on the worst listed mass; `CL-E2-SKU-BAY-CLEAR` 1 mm (height, +3 mm tolerance); `CL-E2-SKU-LEAD-AWG` 10 (inferred). The pessimistic pack line ($119.88) covers the EUR price. E2 does not accept re-leading the 680 g pack: A3-R6 gives +33 g margin against the 100 g overrun, and replacing the lead means cutting at the cell tabs |
| CR-E2-25 | A1 | `params.json#battery`: `pack` → "Ovonic 4S 6500 mAh 120C hard case EC5, re-terminated to AS150U", source `SRC-E2-OVONIC-120C-EC5`; `size_m` → **[0.135, 0.046, 0.049]** (source same, `UNVERIFIED` until measured); `mass_kg` stays **0.55** (listing 551 ± 5 g; note "D-58 line 601 g, CL-E2-SKU-MASS-MARGIN"). The pack-acceptance limit is now 0.601 kg in E2 (`PACK_ACCEPT_KG`). | D-58 closed from E2's side; `CL-E2-PACK-MASS` limit 0.68 → 0.601 |
| CR-E2-23 | A1 | (a) `CL-A1-HOVER-TW-SAG` how-line in `frame_claims.py`: replace "fresh value x CL-E2-SAG-F-WORST" with "fresh value x CL-E1-SAG-FACTOR (CL-E1-TW-WORST)"; this is the last pointer to a retired E2 sag id (D-49 item "re-point at `CL-E1-TW-WORST`"). (b) `performance.cruise_after_hover_min` 12.7 → **12.6** (`CL-E2-CRUISE-MIN-BASE` 12.64 on the 2.600 kg sized mass); `_pess_min` stays 6.8. (c) If B1 adopts E1's 240 W, carry `CL-E2-CRUISE-MIN-BASE-240` **12.0**, `-PESS-240` **6.4** instead; `BATT_LOW_MAH` stays 2600 (`CL-E2-CRUISE-TO-LOW-PESS-240` 6.1 min ≥ 5). | D-49 asked E2 to re-run at 240 W if E1 and B1 reconcile; they have not (B1 stores 227.8 W), so E2 publishes both |
| CR-E2-26 | F1, D2 | The named pack ships **EC5**, not XT60: F1's re-termination step (EC5 → AS150U, ENERGY.md §6) and the H03 line follow. D2: listed body 135 × 46 × 49 mm (was 139 × 47 × 49); at +3 mm tolerance the height leaves 1 mm in the 53 mm bay; the lead exits one 46 × 49 end. | `CL-E2-SKU-BAY-CLEAR` 0.001 m |
| CR-E2-27 | E3 | Still reading `ASM-E2-R-EXT` (now a 6.5 mΩ mirror): re-point `thermal.py` to `P:electrical.r_ext_mohm` (mOhm) and re-run; your stored `CALC-E3-MISSION` drifts on it and on `CL-E2-HOVER-ONLY-MIN-PESS` 9.355 → 9.28. | repeat of CR-E2-17 for E3 |

## Open from R3

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-E2-17 | E1, E3, H1 | Read the line resistance from **`P:electrical.r_ext_mohm`** (unit mOhm, divide by 1000), not `ASM-E2-R-EXT`, and re-run. E1's working script already does this (rev 3, 14:55) but `team/E1/claims.json` (09:36) still stores the old input map, so the build re-runs `CALC-E1-WORST` with the mirror's 0.0065 divided by 1000 and reports nonsense drift (pack R 24.0 mΩ). E1: re-run `propulsion.py`. E2 ran your current `worst()` on the current params: **`CL-E1-TW-WORST` 2.12** (stored 2.18), **`CL-E1-SAG-FACTOR` 0.851** (stored 0.854), fresh limited thrust 1 634 gf, worst 1 390 gf, bus 14.55 / 11.87 V. E3 and H1: re-point and re-run. | F1's `CL-F1-R-EXT` 6.5 mOhm (D-32) replaces E2's 3 mOhm. `ASM-E2-R-EXT` now mirrors 6.5 mOhm, so stored outputs that read it drift until they re-run. The id retires once E3 and H1 read the parameter. D-35: E2 adopts your `CL-E1-TW-WORST` as the one worst-state T/W claim. `CL-E2-SAG-BRACKET` (+0.019) checks it against the physical bounds 0.816 and 0.873. |
| CR-E2-18 | A1 | `params.json`: (a) `propulsion.voltage_sag` 0.76 → **0.851**, source `CL-E1-SAG-FACTOR` (0.854 until E1 re-runs on 6.5 mOhm). E2's `CL-E2-SAG-F-WORST` and `CL-E2-TW-SAG-WORST` no longer exist. (b) `performance.cruise_after_hover_min` 13.7 → **12.7** and `cruise_after_hover_pess_min` 7.3 → **6.8** (`CL-E2-CRUISE-MIN-BASE` 12.67, `-PESS` 6.78). (c) `performance.cruise_power_w` 218 differs from B1's stored `CL-B1-CRUISE-P` **227.8 W** (`-P-PESS` 300.6 W, B1's pod re-run); carry B1's stored values. (d) `cruise_current_a` note: E2's pessimistic cruise current is now **22.4 A** (`CL-E2-CRUISE-I-PESS`), not 29.8. (e) In `frame_claims.py`, `CL-A1-HOVER-TW-SAG` should cite `CL-E1-TW-WORST` / `CL-E1-SAG-FACTOR`, not `CL-E2-SAG-F-WORST`. | CR-A1-31. 12.7 / 6.8 come from B1's 227.8 / 300.6 W and r_ext 6.5 (−0.1 min). The params' 13.7 / 7.3 were the build's re-run on B1's earlier 216.9 / 283.4 W. |
| CR-E2-19 | F1 | Point `ASM-F1-PROFILE` at the new claims instead of the copied table. Currents: `CL-E2-I-CLIMB-PESS` 35.5 A, `CL-E2-HOVER-I-GATE` 30.1 A, `CL-E2-I-TRANS-FWD-PESS` 43.5 A, `CL-E2-I-TRANS-BACK-PESS` 40.0 A, `CL-E2-I-DESCENT-PESS` 30.1 A, `CL-E2-CRUISE-I-PESS` 22.4 A. Durations: `CL-E2-T-*-PESS` (25, 120, 20, 20, 50, 407 s). Highest phase current: `CL-E2-I-MAX-PHASE-PESS` 43.5 A. The momentary peak stays 100 A (limiter). | CR-F1-04 done. r_ext 6.5 moved each phase by +0.3 to +0.6 A, and B1 rev 2 moved cruise from 29.8 to 22.4 A. Supersedes CR-E2-14. Charge lead and re-termination: ENERGY.md §5–6. |
| CR-E2-20 | F4 | `BATT_LOW_MAH` **2600** (back from the provisional 2700; `CL-E2-BATT-LOW-MAH`, landing allowance 1 265 mAh). `BATT_CRT_MAH` 1300 unchanged. The worst full-throttle bus voltage is **11.87 V** (`CL-E2-V-BUS-WORST`): keep `BATT_FS_VOLTSRC` 1; `Q_M_BAT_VOLT_MIN` 13.2 saturates only in that state. | Supersedes CR-E2-13. `CL-E2-CRUISE-TO-LOW-PESS` 6.4 min ≥ 5 (+28 %). |
| CR-E2-21 | B1 | Your pessimistic cruise (300.6 W level) is 28 % below E2's independent K09-based model (386 W level). E2 carries yours. Please state in `ASM-B1-*` which drag terms the pessimistic case covers (CD0 0.0452 × 1.3 vs the K09 0.0593), so the gap is explained in one place. | If E2's model were right, pessimistic cruise would be ~5.2 min and `BATT_LOW` would trigger at ~4.7 min. The first tune flight's logged current settles it (`T-E2-MISSION-LOG`). |
| CR-E2-22 | I2 | Test-day plan: 2 sorties now use **58.5 of 180 min** (sortie 19.3 min + 20 min turnaround). | Supersedes the CR-E2-16 numbers; `CL-E2-WINDOW-USED`. |

## Earlier requests and their disposition

| # | To | Disposition (CHANGE-LOG) | E2 follow-up |
|---|---|---|---|
| CR-E2-01 | A1 | accepted (D-06, D-12, D-13, D-15); (b) `SRC-OVONIC-4S6500` stays unchecked until weighed | (d) superseded by CR-E2-12, then CR-E2-18 |
| CR-E2-02 | D2 | accepted (D-15): bay ≥ 0.160 × 0.052 × 0.053 m | none |
| CR-E2-03 | F4 | forwarded | `BATT_LOW_MAH` now CR-E2-20 |
| CR-E2-04 | F1 | forwarded | now CR-E2-19 |
| CR-E2-05 | A1, I1 | deferred (D-12): packs 3–4 only if the post-order reserve ≥ $396 | 2 sorties per day planned |
| CR-E2-06 | H3 | forwarded | none |
| CR-E2-07 | E3 | forwarded | heat input now 21.8 W cold / 14.5 W hot, 43 °C at landing (CR-E3-10: re-run on the R3 tables) |
| CR-E2-08 | B1 | forwarded | E2 reads B1's claims |
| CR-E2-09 | H1, H2 | forwarded | add filling `team/E2/pack_log.csv` to `T-E2-WEIGH` |
| CR-E2-10 | I2 | forwarded (D-12) | restated as CR-E2-16, then CR-E2-22 |
| CR-E2-11 | B1 | done by B1 rev 2 (11×5.5MR at 16 m/s, D-36) | E2 re-ran (R3) |
| CR-E2-12 | A1 | applied in part (D-35, D-36) | superseded by CR-E2-18 |
| CR-E2-13 | F4 | forwarded | superseded by CR-E2-20 (2600) |
| CR-E2-14 | F1 | forwarded | superseded by CR-E2-19 |
| CR-E2-15 | A3 | open | unchanged: replace the 550 g pack line with the heaviest weighed pack |
| CR-E2-16 | I2 | forwarded | numbers in CR-E2-22 |

## Requests to E2 answered in R4

| From | Request | Answer |
|---|---|---|
| CR-I1-13, D-58, CR-A1-56, CR-A3-24 | Name a 4S 6500 SKU ≤ 601 g with ≥ 10 AWG leads, or accept re-leading and 680 g | Named: Ovonic 120C 4S 6500 hard case EC5, 551 ± 5 g (CR-E2-24). Re-leading and 680 g not accepted |
| D-58 | Weigh the first pack on arrival (`battery.mass_kg`) | `T-E2-WEIGH` planned; pass ≤ 601 g plus a lead-gauge step (ENERGY.md §8) |
| D-49, CR-E1-25 | `voltage_sag` 0.851; re-point `CL-E2-TW-SAG-WORST` at `CL-E1-TW-WORST` | E2 reads `CL-E1-SAG-FACTOR` 0.851 (bracket +0.022); `CL-E2-TW-SAG-WORST` was retired in R3; A1's how-line is the last pointer (CR-E2-23a) |
| D-49, CR-A1-50 | Re-run the budget if E1 and B1 reconcile at 240 W | Not reconciled; sensitivity published (`CALC-E2-BUDGET-240`: 12.0 / 6.4 / 6.1 min, all ≥ 5) |

## Requests to E2 answered in R3

| From | Request | Answer |
|---|---|---|
| CR-A1-31 | Re-run on B1 rev 2 and r_ext 6.5; one T/W claim with E1 | Done: 12.7 / 6.8 min, `BATT_LOW_MAH` 2600; adopted `CL-E1-TW-WORST` (ENERGY.md §3) |
| CR-A2-17 | `cap_frac` → `P:requirements.pack_capacity_min_frac` | Done; E2 no longer cites `ASM-A2-PACK-CAPACITY-FRAC` |
| CR-E1-15 | Drop E2's T/W output or cite E1 | Done: `CL-E2-SAG-F-WORST` and `CL-E2-TW-SAG-WORST` retired; bus-voltage outputs kept for `BATT_*` |
| CR-E3-10 | Re-run on B1's new cruise power | Done |
| CR-F1-03 / -04 | Re-run on r_ext 6.5; phase currents as claims; charge lead; re-termination | Done (ENERGY.md §2, §5, §6) |
| CR-F1-14, CR-I1-06 | Confirm the pack connector and a ≥ 10 AWG lead at order | Order-time check in ENERGY.md §1; I1 places the order |
| CR-D7-07 | Packs in the LiPo bag, never in the box | Adopted (ENERGY.md §6) |
