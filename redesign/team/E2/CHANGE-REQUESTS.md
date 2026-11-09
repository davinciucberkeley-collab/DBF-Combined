# Change requests from E2 (battery / energy engineer)

Revision E2-R2, 2026-11-09. Numbers are from `team/E2/energy_claims.py` → `team/E2/claims.json`. All are
`UNVERIFIED` until `T-E2-WEIGH`, `T-E2-CAPACITY` and `T-E2-IR` have run.

## Open (new in R2)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-E2-11 | B1 | Re-run `CALC-B1-CRUISE` with the **11×5.5MR at 16 m/s, c 0.32, S 0.368 m²** (the D-13 note already plans it) and keep the claim ids `CL-B1-CRUISE-P` / `CL-B1-CRUISE-P-PESS` (W, gate mass, level flight, avionics included). E2 reads them directly and re-runs. | With your delivered 11×4.5MR values (306.6 / 396.9 W), the pessimistic mission gives 5.1 min of cruise (+3 %) and `BATT_LOW` triggers at 4.6 min (`CL-E2-CRUISE-TO-LOW-PESS` **FAILS**, −7 %). Scaling by E1's 11×5.5MR ratio (216 / 269 W = 0.80) gives 6.5 / 6.1 min (`CL-E2-CRUISE-MIN-PESS-55`), so your re-run likely closes it. Your stored claims also drift (S 0.345 → 0.368: 311 / 405 W). |
| CR-E2-12 | A1 | `params.json#performance`: `cruise_after_hover_pess_min` 6.4 → **5.1** (`CL-E2-CRUISE-MIN-PESS`); add the E2 mission base **9.6 min** in the note next to B1's 12.3 (the E2 figure counts climb, descent, transitions, ground and circuits). `propulsion.voltage_sag` 0.72: my claim is now **0.758** with the 24.8 A limiter (100 A total); keep 0.72 as the conservative carry and say so in the note, or update it (T/W worst 1.89). Interim until CR-E2-11. | `CL-E2-CRUISE-MIN-PESS`, `CL-E2-SAG-F-WORST`, `CL-E2-TW-SAG-WORST`; the params value cites my claim but no longer equals it |
| CR-E2-13 | F4 | `BATT_LOW_MAH` 2600 → **2700** (provisional; back to 2600 if B1's 11×5.5MR re-run confirms). Other battery parameters unchanged from CR-E2-03. | Landing allowance is now 1 380 mAh pessimistic (`CL-E2-BATT-LOW-MAH`) |
| CR-E2-14 | F1 | Design currents update: momentary peak **100 A** (24.8 A per motor limiter, D-05) instead of 117 A; hover 29.9 A, transition 42.9 A (20 s), cruise **29.8 A** pessimistic (was 24.0). XT60 and a ≥ 120 A sensor still fit. | `CALC-E2-SAG`, `CL-E2-CRUISE-I-PESS` |
| CR-E2-15 | A3 | When the first pack is weighed (~20 Nov order), replace the 550 g pack line with the heaviest weighed pack from `team/E2/pack_log.csv` (`CL-E2-PACK-MASS`). Accept ≤ 680 g; above that E2 returns the pack. | CR-A3-08; your predicted roll-up already carries 680 g |
| CR-E2-16 | I2 | Plan every test day at **2 sorties** (52 of 180 min of the window) with a 2.0 h attended charge the afternoon before. | D-12; `CL-E2-SORTIES-PACKS`, `CL-E2-WINDOW-USED` |

## Earlier requests (R1) and their disposition

| # | To | Disposition (CHANGE-LOG) | E2 follow-up |
|---|---|---|---|
| CR-E2-01 | A1 | accepted (D-06, D-12, D-13, D-15); (b) `SRC-OVONIC-4S6500` stays unchecked until weighed | (d) superseded by CR-E2-12 |
| CR-E2-02 | D2 | accepted (D-15): bay ≥ 0.160 × 0.052 × 0.053 m | none |
| CR-E2-03 | F4 | forwarded | `BATT_LOW_MAH` changed by CR-E2-13 |
| CR-E2-04 | F1 | forwarded | currents changed by CR-E2-14 |
| CR-E2-05 | A1, I1 | deferred (D-12): packs 3–4 only if the post-order reserve ≥ $396 | 2 sorties per day planned |
| CR-E2-06 | H3 | forwarded | none |
| CR-E2-07 | E3 | forwarded | heat input now 21.4 W cold / 14.3 W hot, 45 °C at landing |
| CR-E2-08 | B1 | forwarded | E2 now reads B1's claims; CR-E2-11 asks for the 11×5.5MR re-run |
| CR-E2-09 | H1, H2 | forwarded | add filling `team/E2/pack_log.csv` to `T-E2-WEIGH` |
| CR-E2-10 | I2 | forwarded (D-12) | restated as CR-E2-16 |
