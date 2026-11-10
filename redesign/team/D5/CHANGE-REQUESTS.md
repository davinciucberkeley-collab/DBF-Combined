# D5 change requests

## Round R3 (2026-11-09, revision D5-R3, answers CR-A1-34 / D-30)

| Id | To | What | Why / numbers |
|---|---|---|---|
| CR-D5-11 | D3 (cc C4, B3, A1) | **Half-fin tip for the R3 foot.** `fin_detail.fin.tip_square_m` 0.040 → **0.0454 m** (square tip x 0.2746–0.320); cut the square tip down to a **flat step at \|z\| 0.2005 m** (9.5 mm below the 0.21 tip); end both edge strips at x 0.2746 (their end faces meet the step front). Nothing else on x ≥ 0.2666 m, \|z\| ≥ 0.196 m (collar cheeks). Re-run `make_fins.py`. | With the pad edge kept at z ±0.219 (D-30) and a 38 mm stroke, the sleeve (17.1 mm deep) must overlap the fin in x and cannot sit above a 0.21 m tip. Twin sleeves beside the fin were sized and rejected: ≈ 15.6 g per foot (62 g vs 43 g). The step removes 431 mm² of board per half-fin, replaced in the same plane by the shoe side walls (17 × 51 mm). `CL-D5-FIN-STEP-Z/-X/-DEPTH`. C4: strip termination now bonded into the shoe (back wall + cheeks, CR-C4-09). B3: no loss of projected fin area. |
| CR-D5-12 | C6 | Replace the `E-GER-01…04` bond block: area **1 621 mm²**, design **87.4 N** (upper foot ult 60.4 N × 1.4375), RF **1.85** at your 0.10 MPa. Review the rim lip model (`CALC-D5-SIDE`: R = F(a+e)/(e+s0) = 98.8 N, fixed-ended beam, SF 1.24) and the cap tape joint `CT-GER-CAP-TAPE`. Snap fingers are 6.5 mm (1.7 %, `CL-D5-SNAP-*`), closing CR-C6-12. | `CL-D5-BOND-AREA`, `CL-D5-BOND-SF`, `CL-D5-SIDE-RIM-SF`. |
| CR-D5-13 | A4 (cc A5, A3) | Merge D5-R3: 18 parts. **New** `GER-007-R/L` (corner caps), **`GER-008-LR/LL`** (type-L cartridge) replaces `GER-003-LR/LL` (one part number per geometry); `E-GER-11/12` and `E-GER-19/20` now have `part_a` `GER-008-LR/LL`; **new** `E-GER-21/22` (cap ↔ `WNG-001`, `CT-GER-CAP-TAPE`). A5: `DX-FOOT-*` = pad contact x 0.368, z ±0.218 (CR-A1-38). | `subsystems/landing/interfaces.json`. `E-GER-21/22` dangle until D1 declares `WNG-001` (same as `E-POD-01`, `E-TRN-*`). |
| CR-D5-14 | C1 (cc C4) | Carry the **biased feet** per type in `loads.py`: upper foot peak **40.3 N** limit / **60.4 N** ult, lower 34.3 N limit; mean 37.3 N; side load at the pad 20.4 N limit (C5 mat). Your R3 `CL-C1-FOOT-MAX` 41.2 N covers the upper foot by 2 % (`CL-D5-F-PEAK-UPPER`); D5 sizes the flange and bond to your 60.8 N ult. | `CL-D5-F-PLATEAU-UPPER/-LOWER`, `CL-D5-F-ULT-UPPER`. C4: fin face check at 60.8 N on the upper tips. |
| CR-D5-15 | C5 | Re-run `landing_calc.py`: `CL-D5-F-PLATEAU` (mean) 33.9 N (was 34.1), `CL-D5-CART-LEN` 89 mm, stroke 38 mm, `CL-D5-SET-NORMAL` 0.17 mm. Achieved bias ×1.080 / ×0.920 (U/L 1.175 vs your 1.167) from a 6.35 mm bore in the type-L cartridge: confirm the pitch case or ask for a 6.0 mm bore (×1.071). | `CL-D5-BIAS-UPPER`, `CL-D5-BIAS-ERR` 0.003. Usable 35 mm vs your 31.5 mm pair-first (`CL-D5-STROKE-USABLE`). |
| CR-D5-16 | A1 (cc D7, A2) | (a) `transport.envelope_props_off_m` span 1.15 → **1.152 m** (corner caps 0.8 mm each side, `CL-D5-ENVELOPE-SPAN-GROWTH`); height 0.438 unchanged. (b) README feet row: "shoe on a 9.5 mm step of a 45.4 mm square tip; pad contact ±0.218; 42.1 g". (c) Wording: CR-A1-34 says "≥ 38 mm usable"; `requirements.foot_crush_stroke_min_m` is the flange-to-sleeve **gap** (38 mm); usable after C5's 3 mm guard is 35 mm. A 38 mm usable stroke would need a 51 mm foot. | Box slack in height 52 mm (`CL-D5-BOX-SLACK`). |
| CR-D5-17 | A3 | Landing **42.05 g** `EST` from CAD volumes (`CL-D5-MASS-TOTAL`; 4 feet 40.60 + 2 caps 1.45) against 43 g, margin 0.95 g; per-instance masses and CGs in `subsystems/landing/interfaces.json`; spares are ground items. | `CALC-D5-MASS`. |
| CR-D5-18 | D6, D1 | Outboard elevon (`WNG-012-L/R`): one wrap of 12 mm filament tape round the outboard 25 mm of the elevon TE (scuff guard; C5 roll case touches 2 mm inboard of the tip). The TPU cap sits on the fixed tip y 0.5615–0.575 only, clear of the elevon end gap. D1: declare `WNG-001` so `E-GER-21/22` close. | CR-C5-04 asked for 40 mm; only 15 mm of fixed tip exists outboard of the elevon (`k9.elevon_spans` 0.56). |
| CR-D5-19 | H1 (cc G3) | Plan `T-D5-COUPON` (3 pairs per type, 40 mm, pass U 34.5–38.5 N, L 29.5–33.0 N, U/L 1.15–1.19), `T-D5-PROOF` (88 N along x on a stepped two-layer offcut), `T-D5-SIDE` (32 N sideways at the pad, insert pushed 4 mm). | All strength and crush claims are `UNVERIFIED` until these run. |
| CR-D5-20 | I1 | BOM: 1/4 in K&S brass tube ~$3 (`GER-013`), TPU 95A (~2 g), orange + blue paint markers, orange and blue PETG (shop stock); neoprene sheet stays (`GER-006`). Field kit: 4 + 4 spare inserts, 16 + 16 loose cartridges (CR-C5-06), 2 spare shoes. | `subsystems/landing/parts.csv`. |

## Earlier rounds

| Id | To | State |
|---|---|---|
| CR-D5-01 | A1 | closed (D-30, D-31: envelope 0.438, `CL-A1-TIPOVER` on the contact z) |
| CR-D5-02 | A5 | open, carried in CR-D5-13 (`DX-FOOT-*` at ±0.218) |
| CR-D5-03 | D3 | superseded by CR-D5-11 (square tip 45.4 mm with a step) |
| CR-D5-04 | C6 | answered by CR-C6-12 (0.10 MPa, 6 mm fingers); updated numbers in CR-D5-12 |
| CR-D5-05 | C5 | answered (CR-C5-01, CR-C5-10) |
| CR-D5-06 | A3 | superseded by CR-D5-17 |
| CR-D5-07 | A4 | superseded by CR-D5-13 |
| CR-D5-08 | H1 | superseded by CR-D5-19 |
| CR-D5-09 | F4 | open (`Q_LAND_SPEED` ≤ 0.5 m/s; set 0.17 mm per landing) |
| CR-D5-10 | I1 | superseded by CR-D5-20 |
