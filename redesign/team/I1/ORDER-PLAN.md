# Order plan: early order (~20 Nov 2026) and mid-December order (15 Dec 2026)

Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv) (line ids `B01`…`G11`). Money: `python -I redesign/team/I1/build_bom.py`.
Prices are 2026 list prices before 10.25 % tax. `CHK` = compared with the vendor page on 2026-11-09, `CARRY` = carried from `cards/K09/cost.csv`, `EST` = estimate.

## Totals by order

| Order | Goods | Tax 10.25 % | Shipping `EST` | Total | Source |
|---|---|---|---|---|---|
| Early, ~20 Nov | $836.17 | $85.71 | $75 | **$996.88** | `BOM.csv` lines with order `EARLY` |
| December, 15 Dec | $318.65 | $32.66 | $45 | **$396.31** | `DEC` lines + FAA $5 not taxed counted in the full BOM, not here |
| Store pick-up (Jan, ammo can in Nov) | $154.96 | $15.88 | 0 | **$170.84** | `LOCAL` lines |
| Whole BOM, baseline | $1 309.78 | $134.25 | $120 + $5 FAA | **$1 569.03** | `CL-I1-SPEND-BASE` |
| Whole BOM, pessimistic | $1 359.05 | $139.30 | $150 + $5 FAA + $27 adders | **$1 680.35** | `CL-I1-SPEND-PESS` |

The three order rows add to $1 564.03 + $5 FAA = $1 569.03 (Dec row shipping $45 and early $75 = the $120 baseline).

## Reserve gate (hard: $2 000, reserve >= $309 on pessimistic numbers)

| Case | Spend | Reserve | Limit | Status |
|---|---|---|---|---|
| Baseline | $1 569.03 | $430.97 | >= $150 planned | `CHECKED` against inputs, prices `UNVERIFIED` |
| Pessimistic (Ovonic at list, tubes overseas, shipping +$30, tax measure +$7, jig/box +$20) | $1 680.35 | **$319.65** (+3.4 %) | >= $309 | `UNVERIFIED` (+$10.65 margin) |

The $309 margin exists only because the second LANRC ESC pack ($33.08 incl. tax) is deferred (gated line X01). With it in, the pessimistic reserve is $286.57.

## Early order, ~20 Nov (electronics, packs, test hardware)

Purpose: the $40 foam-board twin, the thrust stand and charging on real hardware (`CONFIGURATION.md` de-risking). Place it as three or four carts. Re-read every listing first (`T-I1-LISTINGS`).

| Vendor | Lines (qty total) | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| SunnySky USA | `B01` motor X3108S KV900 (5) | $124.95 | $12.81 | $137.76 | 3–7 | page 429 today; search shows $24.99 and 60 in stock; measure bolt pattern and leads on arrival |
| OVONIC US | `P01` 2 × 4S 6500 130C (1 two-pack) | $79.25 | $8.12 | $87.37 | 5–10 | sale price may end: **buy first**; list $119.88 in the pessimistic case; confirm XT60 (title says "XT60 to TRA plug"); weigh both packs |
| APC | `B03` 11×5.5MR/MRP (8), `B04` 11×4.5MR/MRP (4), `B05` LPAR06E rings (12) | $51.96 | $5.33 | $57.29 | 3–7 | props $3.83 `CHK`; rings $0.50 `EST`; 2 MR + 2 MRP of each size |
| Amazon | `B02` LANRC 4-pack ESC (1), `W02` foam board, `W06` tape, `W07` glue, `G01` HTRC C150, `G04` watt meter, `G05` IR thermometer, `G06` load-cell kit, `G08` PD supply, `G09` multimeter, `G10` solder | $255.82 | $26.22 | $282.04 | 2–5 | **LANRC ASIN B0D2HS4Y4J not confirmed** (503 today, no US 4-pack page in search): open it, check title, 45 A, 4 pieces, price; fallback Tekko32 +$60 |
| ReadyMadeRC | `A01` CoreWing F405 Wing APP V2 (1) | $67.26 | $6.89 | $74.15 | 3–7 | order only after F3 confirms a stable ArduPilot tailsitter build; else SpeedyBee F405 Wing $47.99 (stock unverified) |
| RaceDayQuads | `A02` HGLRC M100-5883 GPS (1) | $20.49 | $2.10 | $22.59 | 3–7 | |
| RadioMaster | `A03` RP3 V2 (1), `R01` Pocket Crush (1) | $84.98 | $8.71 | $93.69 | 3–7 | |
| GetFPV | `R02` 18650 two-pack (1) | $24.49 | $2.51 | $27.00 | 3–7 | the Pocket needs them |
| Aloft Hobbies | `W03` carbon tube 22×20×1000 (1) | $24.00 | $2.46 | $26.46 | 3–7 | for C4's bend test, then the spare; weigh on arrival |
| Pyrodrone | `G02` LiPo bag (2) | $19.98 | $2.05 | $22.03 | 3–7 | |
| Pine64 | `G07` Pinecil V2 (1) | $25.99 | $2.66 | $28.65 | 5–10 | |
| Bolt Depot | `B07` M3×8 SHCS A2 (20) | $2.00 | $0.20 | $2.21 | 3–7 | minimum order may exceed $2; hardware kit may already hold them |
| Wiring / hardware kit (F1/F2 itemise) | `H01` early share (1) | $55.00 | $5.64 | $60.64 | 3–7 | lump `EST`; F1/F2 owe the itemised list (`CR-I1-01`) |
| **Early total** | | **$836.17** | **$85.71** | **$921.88** + $75 shipping `EST` | | **$996.88** |

Also, before the first charge (late Nov, store): `G03` ammo can, Harbor Freight 63750, $19.99 + $2.05 tax.

Not in the early order: Small Parts adapters (out of stock, see below), servos, airspeed sensor, XPS, PETG, second ESC pack, spare servo, optional E-series props.

## Mid-December order, 15 Dec (airframe, mechanisms, remaining electronics)

Place the carbon-tube cart first.

| Vendor | Lines (qty total) | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Aloft Hobbies, **or** Amazon overseas as the fallback | `W04` carbon tube 22×20×1000 (2: spar + both motor tubes from one) | $48.00 | $4.92 | $52.92 | Aloft 3–7; overseas ~14 | **LONG LEAD.** Buy Aloft if C4's bend test of `W03` passes; overseas $28.32 each (+$8.64 pre-tax) otherwise, and then order on 15 Dec at the latest (arrival ~29 Dec, build start 19 Jan) |
| Small Parts CNC | `B06` adapter set 2 RH + 2 LH (1) | $23.95 | $2.45 | $26.40 | unknown | **out of stock 2026-11-09:** re-check on 20 Nov and 15 Dec; fallback adapters in the motor boxes + Loctite 243 (-$26.40) |
| EMAX USA | `M01` ES3005HV servo (2) | $39.98 | $4.10 | $44.08 | 5–10 | placeholder until D6 picks the servo (needs >= 3.04 kgf·cm) |
| Holybro | `A04` MS5525 airspeed + pitot (1) | $59.99 | $6.15 | $66.14 | 5–10 | not needed before the fixed-wing tune; first lever if a pessimistic adder lands (+$66.14) |
| West3D | `W05` PETG 1 kg (1) | $20.99 | $2.15 | $23.14 | 3–7 | |
| Amazon | `G11` hot-wire supply + Ni80 wire (1) | $41.73 | $4.28 | $46.01 | 2–5 | |
| Hardware kit (F1/F2 itemise) | `H02` balance (1) | $69.01 | $7.07 | $76.08 | 3–7 | lump `EST` |
| AS150U re-termination | `H03` (1) | $15.00 | $1.54 | $16.54 | 3–7 | $0 if F1 keeps XT60 |
| **December total** | | **$318.65** | **$32.66** | **$351.31** + $45 shipping `EST` | | **$396.31** |

FAA registration $5 (DroneZone, not taxed) before the first flight. Store pick-up in Jan (`LOCAL`): `W01` XPS sheet $59.97, `H04` transport box $60.00 `EST`, `H05` hot-wire jig $15.00 `EST`.

## Long-lead and risk flags

| Item | Why | Mitigation |
|---|---|---|
| Carbon tubes `W03`, `W04` | overseas lead ~14 days is the critical path for the build start (19 Jan) | US-stock Aloft in the early order; December cart first; Aloft or overseas by the bend-test result |
| LANRC ESC `B02` | listing unconfirmed (Amazon 503, no US 4-pack page found) | open the page before 20 Nov; fallback Tekko32 F4 45A AM32 $22.50 each, backorder to Dec 2026, +$60 for four |
| Ovonic packs `P01` | sale $79.25 vs list $119.88; connector wording "XT60 to TRA plug"; mass 503–680 g unknown | order first; ask the vendor or read the photos for the connector; weigh on arrival (`T-E2-WEIGH`) |
| Small Parts adapters `B06` | out of stock | fallback in the motor box (E1 `CR-E1-20`) |
| FC `A01` | firmware support unconfirmed | F3 gate before ordering |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |

## Gated purchases (not in any total; bought only when the test passes)

| Id | Item | Cost incl. tax | Gate |
|---|---|---|---|
| X01 | 2nd LANRC ESC 4-pack (4 spare ESCs) | $33.08 | realised reserve after all December receipts >= $309 + cost |
| X02 | Spare elevon servo | $22.04 | same |
| X03 | Optional APC 11×5.5E ×2 + 11×5.5EP ×2 (`CR-B4-11`) | $18.39 | same, and the stand shows the MR/MRP pair short |
| X04 | Flight packs 3–4 (one more two-pack) | $87.37 at sale | D-12: reserve after the December order >= $309 + $87.37 |
| X05 | Remote ID module | $44.09 | only if flown outside the RFS FRIA |

With the baseline reserve of $430.97, X01 + X02 + X03 ($73.51) can all be bought and still leave $357, above $309. X04 needs $396.37 and fits on its own at baseline ($430.97), not on pessimistic numbers; X01–X04 together do not fit.
