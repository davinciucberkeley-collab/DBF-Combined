# Change requests from E2 (battery / energy engineer)

Revision E2-R3, 2026-11-09. Numbers are from `team/E2/energy_claims.py` → `team/E2/claims.json`. All are
`UNVERIFIED` until `T-E2-WEIGH`, `T-E2-CAPACITY` and `T-E2-IR` have run.

## Open (new in R3)

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
