# Order plan: early order (~20 Nov 2026) and mid-December order (15 Dec 2026)

Revision I1-R3, 2026-11-10. Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv). Money: `python -I redesign/team/I1/build_bom.py`, then
`python -I redesign/team/I1/make_order_plan.py` regenerates the vendor tables below. Prices are 2026 list prices before 10.25 % tax.
`CHK` = compared with the vendor page on 2026-11-09, `CARRY` = carried from `cards/K09/cost.csv`, `EST` = estimate, no vendor page.

## Totals by order

| Order | Goods | Tax 10.25 % | Shipping `EST` | Total |
|---|---|---|---|---|
| Early, ~20 Nov | $897.41 | $91.98 | $75 | **$1,064.39** |
| December, 15 Dec | $349.96 | $35.87 | $45 | **$430.83** |
| Store pick-up (XPS, jig, ammo can) | $79.96 | $8.20 | 0 | **$88.16** |
| FAA registration (DroneZone, not taxed) | | | | **$5.00** |
| Whole BOM, baseline (excl. gated lines) | $1,327.33 | $136.05 | $120 | **$1,588.38** (`CL-I1-SPEND-BASE`) |
| Whole BOM, pessimistic (excl. gated lines) | $1,352.92 | $138.67 | $150 | **$1,673.59** (`CL-I1-SPEND-PESS`; + $5 FAA + $27 adders) |

## Reserve gate (hard: $2 000, reserve >= $309 on pessimistic numbers)

| Case | Spend | Reserve | Limit | Status |
|---|---|---|---|---|
| Committed order, baseline | $1,588.38 | $411.62 | >= $150 planned | `CHECKED` against inputs; prices `UNVERIFIED` |
| Committed order, pessimistic (Ovonic at EUR 113.30 x 1.16, tubes overseas, shipping +$30, tax measure +$7, jig/box +$20) | $1,673.59 | **$326.41** (margin $17.41) | >= $309 | `UNVERIFIED` |
| **Everything bought**, baseline (gated X07 box/field kit and X08 airspeed sensor included) | $1,961.59 | $38.41 | >= $150 | **FAILS by $111.59** |
| **Everything bought**, pessimistic | $2,046.80 | **$-46.80** | >= $309 | **FAILS by $355.80** (`CL-I1-RESERVE-PESS-ALLIN`) |

**What changed in R3 (CR-A1-67, D-72).** Pack re-priced for the Ovonic 120C EC5 pair (+$31.51 baseline, +$11.55 pessimistic, pre-tax); Savox SH-0255MG+ replaces the placeholder
servo (+$44.00); the $6 T-antennas, FC isolation set, F2 harness lines, D6 mechanisms hardware, 2.5 mm CF rod, PA66 socket-head set, 7/32 in brass tube and two strain gauges are
itemised; the D7 mat, tote, spares box and labels sit in the gated X07. Net of the designers' lines: pessimistic spend +$130.55 pre-tax ($143.94 incl. tax) before any lever.
**Lever 1 alone is not enough.** Borrowing the soldering kit (G07-G10, $94.80 incl. tax) leaves the pessimistic reserve at $263.87, $45.13 under the $309 crash.
Lever 2 (borrow the hot-wire gear G11 + H05, $62.54) is also applied and gives the reserve above. Both are bought if Jacobs Hall refuses (gates X10, X11): H1's written yes before 20 Nov is a hard dependency.
The committed order holds the $309 reserve only by holding blocks behind gates: X07 (D7 box and field kit, store pick-up, needed before the first drive to the field in March), X08 (airspeed sensor, DECISION 5.1 lever), X10, X11.

## Early order, ~20 Nov (electronics, packs, test hardware, power parts)

Purpose: the $40 foam-board twin, the thrust stand, charging and first power bench on real hardware (`CONFIGURATION.md` de-risking). Place it as
five or six carts. **Place the pack cart (`P01`) first: ~14 days from Germany.** Re-read every listing first (`T-I1-LISTINGS`).

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `B02`, `A05`, `A06`, `W02`, `W06`, `W07`, `F01` x5, `F02`, `F03`, `F04`, `F05`, `F06`, `F07`, `F08`, `F09`, `G01`, `G04`, `G05`, `G06`, `G12` | $316.82 | $32.47 | $349.29 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| SunnySky USA | `B01` x5 | $124.95 | $12.81 | $137.76 | 5 | page 429 on 2026-11-09, price by search snippet; measure bolt pattern, hole depth and leads on arrival |
| Ampow / OVONIC (same SKU) | `P01` | $114.48 | $11.73 | $126.21 | 14 **LONG** | **LONG LEAD (~14 d, ships from Germany); USD price not found**: baseline EUR 98.69 x 1.16, pessimistic EUR 113.30 x 1.16. Ask the seller for 10 AWG leads before paying |
| RadioMaster | `A03`, `R01` | $84.98 | $8.71 | $93.69 | 5 | select the **FCC** variant for both RP3 V2 and Pocket Crush (CR-F5-06); not LBT |
| ReadyMadeRC | `A01` | $67.26 | $6.89 | $74.15 | 5 | FC page URL changed (product 87195); price carried from 2026-10-13; F3 gate (stable tailsitter build) before ordering |
| APC | `B03` x8, `B04` x4, `B05` x12 | $51.96 | $5.33 | $57.29 | 5 | props `CHK` $3.83; rings `EST` |
| Amazon / DigiKey | `H01` | $41.00 | $4.20 | $45.20 | 4 | JST-GH from DigiKey: separate shipping, use pigtails if the cart allows |
| GetFPV | `R02` | $24.49 | $2.51 | $27.00 | 5 | 18650 cells: RadioMaster says batteries ship only with a radio order |
| Aloft Hobbies | `W03` | $24.00 | $2.46 | $26.46 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| RaceDayQuads | `A02` | $20.49 | $2.10 | $22.59 | 5 |  |
| Pyrodrone | `G02` x2 | $19.98 | $2.05 | $22.03 | 5 |  |
| Bolt Depot | `B07` x20, `C01` | $7.00 | $0.72 | $7.72 | 5 | minimum order may exceed the line price |

**Early total $1,064.39** (goods $897.41 + tax $91.98 + shipping $75 `EST`). Before the first charge (late Nov, store): `G03` ammo can,
Harbor Freight 63750, $19.99 + $2.05 tax. The pack cart (`P01`) is released by D-64 after the two checks below; **no USD price is confirmed**, read the cart total before paying (pessimistic case $131.43).

At order, in the cart:

| Check | Value | Why |
|---|---|---|
| Pack SKU | Ovonic 4S 6500 mAh **120C hard case, EC5, 2-pack**, listed 551 +/- 5 g, 135 x 46 x 49 mm | D-64, CR-E2-24; NOT the 130C XT60 SKU (680 g) |
| Pack lead gauge | **>= 10 AWG** confirmed by the seller (the page does not print it); 12 AWG: stop, tell E2 and F1 | CR-F1-14: 12 AWG rises 28.4 K at 30.3 A against 20 K |
| Pack mass on arrival | accept <= 592.6 g each (`CL-A1-PACK-ACCEPT`) | weigh both, log in E2 `pack_log.csv` |
| RP3 V2 and Pocket Crush | FCC variant | CR-F5-06 |
| FC | CoreWing F405 Wing APP V2 (not the Mini: no bdshot) | CR-F3-06 |
| ESC | LANRC 4-pack: title, 45 A, 4 pieces, price | CR-I1-04 |

## Mid-December order, 15 Dec (airframe, mechanisms, fin and fastener kits)

Place the Aloft carbon cart first (tubes, strips, 20x18 tube), then the rest. Servos (Savox) have a 7-day lead `EST`: the same day.

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `A07`, `H03`, `C06`, `C02`, `C03` x2, `C04`, `C05`, `D04`, `D05`, `D06`, `G13` | $97.00 | $9.94 | $106.94 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| Aloft Hobbies | `W04` x2, `D01`, `D02` x3, `D03` | $96.00 | $9.84 | $105.84 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| Savox USA / hobby dealer | `M01` x2 | $83.98 | $8.61 | $92.59 | 7 | single-source 12 mm servo; US dealer with stock; price from D6, not re-read |
| West3D | `W05`, `W08` | $45.98 | $4.71 | $50.69 | 5 | ASA is not in the Jacobs free stock |
| Amazon / hobby shop | `H02`, `D07` | $27.00 | $2.77 | $29.77 | 5 |  |

**December total $430.83** (goods $349.96 + tax $35.87 + shipping $45 `EST`). Store pick-up in January (`LOCAL`):

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Home Depot El Cerrito | `W01` | $59.97 | $6.15 | $66.12 | 0 | store pick-up; check the XPS sheet is flat |
| Harbor Freight | `G03` | $19.99 | $2.05 | $22.04 | 0 | store pick-up |

## Gated lines held in the BOM (not in any total above)

| Gate | Item | Cost incl. tax | Condition |
|---|---|---|---|
| X01 | 2nd LANRC ESC 4-pack (4 spare ESCs) | $33.08 | realised reserve after all December receipts >= $309 + this line incl. tax |
| X02 | Spare elevon servo (3rd Savox SH-0255MG+) | $46.29 | as X01; D6 and CR-A1-52 ask for 3, the reserve pays for 2 |
| X03 | Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included) | $18.39 | as X01; only if the stand shows the MR/MRP pair short |
| X04 | Flight packs 3-4, one more Ovonic 2-pack | $91.47 | D-12: reserve after the December order >= $309 + $91.47 (at sale price); and only a SKU that passes CR-I1-13 |
| X05 | Small Parts CNC 4114 prop adapter set (2 RH + 2 LH), CR-E1-20 / D-39 | $26.40 | as X01; only if the motor-box adapters fail the stand (T-E1-STAND) and the page is back in stock |
| X06 | Remote ID module NewBeeDrone BeeID | $44.09 | only if flown outside the RFS FRIA |
| X07 | D7 box and field kit (lines T01-T06: Coroplast, tape, straps, handles, pouch, spanner, mat, PE foam) | $149.72 | as X01, before the first drive to the field (store pick-up, no lead time); until then a borrowed carton |
| X08 | RMRC MS4525DO airspeed sensor + pitot (line A04) | $66.14 | as X01; DECISION 5.1 lever, last in the order (CR-I1-03) |
| X10 | Soldering kit if Jacobs Hall will not lend it (G07 Pinecil, G08 PD supply, G09 multimeter, G10 solder/flux/wick) | $94.80 | Jacobs Hall refuses in writing (T-I1-BORROW, before 20 Nov); then the line is BOUGHT and the reserve falls by its value |
| X11 | Hot-wire gear if Jacobs Hall will not lend it (G11 30 V 10 A supply + Ni80 wire, H05 bow and template stock) | $62.54 | as X10 (hot-wire foam cutting is a stated Jacobs capability; the written yes covers it) |
| X09 | K-type thermocouple logger / 2-channel meter (E3 GT-04) | $16.54 | only if Jacobs Hall cannot lend one |

With the baseline reserve of $411.62, X07 + X08 ($184.99) leave $226.63: both fit on baseline, not on pessimistic numbers.
The gate test is the realised reserve (2 000 minus actual spend after the December receipts), not the pessimistic forecast.

## Borrow list (not bought, not in the spend): Jacobs Hall (D-39, D-57 levers 1 and 2, D-72)

Needs a yes from Jacobs Hall staff **in writing before 20 Nov** (`T-I1-BORROW`, H1 obtains it). Two blocks fall in this list because the budget needs them:

| Lever | Lines | Cost if refused (incl. tax) | Needed for |
|---|---|---|---|
| 1: soldering kit | `G07` Pinecil, `G08` PD supply, `G09` multimeter, `G10` solder/flux/wick (gate X10) | $94.80 | harness, ESC leads, AS150U re-termination (every build week) |
| 2: hot-wire gear | `G11` 30 V 10 A supply + Ni80 wire, `H05` bow and template stock (gate X11) | $62.54 | wing core cutting (January) |

Bought for the rig: G06 ($17.97, 20 kgf cell kit, already in the baseline), G12 ($17.00) and G13 ($9.00, fin-proof strain gauges, CR-C4-38).

| Item | From H1's list ($ `EST`) | If not lent |
|---|---|---|
| 2 x 5 kg x 1 g scales | 30 | buy; +$33 incl. tax |
| Optical tachometer | 20 | use ESC rpm telemetry (F4 bdshot) |
| K-type thermocouple meter / logger | in the $30 thermal line | gated X09 $16.54 |
| 10 kg spring scale, sandbags, straps, eye bolts | 20 | luggage scale and shop weights |
| 608 bearings, M8 rod, plywood, fasteners (stand frame) | 15 | shop stock; +$17 |
| Bench supply >= 44.6 A for 14.8 V sweeps | not listed | use a flight pack with V logged at the ESC (H1 rule) |
| 100 A watt meter | 20 | `G04` ($12.99) is bought |

## Long-lead and risk flags

| Item | Why | Mitigation |
|---|---|---|
| Carbon tubes `W03`, `W04` | overseas lead ~14 days is the critical path for the build start (19 Jan) | US-stock Aloft in the early order; December Aloft cart first; Aloft or overseas by the bend-test result (CR-I1-08, 10 Dec) |
| Strips and 20x18 tube `D01`-`D03` | same Aloft cart, `EST` prices | order with the tubes; weigh the strips on arrival |
| Ovonic packs `P01` | ships from Germany (~14 days); no USD price found; 10 AWG leads unconfirmed | order first on 20 Nov; ask the seller for the lead gauge; fallback Tattu 4S 6750 XT90 (605 g, A1 must accept) |
| Savox servos `M01` | single-source 12 mm servo, price from D6 | order 15 Dec with a US dealer; the spare (X02, $46.29) first when the reserve allows |
| Jacobs Hall loan | levers 1 and 2 rest on a written yes | H1 before 20 Nov; a refusal costs $157.34 and breaks the reserve gate |
| LANRC ESC `B02` | listing unconfirmed | open the page before 20 Nov; Tekko32 fallback +$60 |
| Small Parts adapters | out of stock; now gated X05 | E1's fallback: adapter in each motor box + Loctite 243 |
| FC `A01` | firmware support unconfirmed; page moved | F3 gate before ordering |
| Shipping | $120 baseline assumes few carts; this plan has about 14 vendors | free-shipping thresholds on Amazon, Aloft, RadioMaster; re-quote in cart |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |
