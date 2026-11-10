# Order plan: early order (~20 Nov 2026) and mid-December order (15 Dec 2026)

Revision I1-R2, 2026-11-09. Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv). Money: `python -I redesign/team/I1/build_bom.py`, then
`python -I redesign/team/I1/make_order_plan.py` regenerates the vendor tables below. Prices are 2026 list prices before 10.25 % tax.
`CHK` = compared with the vendor page on 2026-11-09, `CARRY` = carried from `cards/K09/cost.csv`, `EST` = estimate, no vendor page.

## Totals by order

| Order | Goods | Tax 10.25 % | Shipping `EST` | Total |
|---|---|---|---|---|
| Early, ~20 Nov | $910.89 | $93.37 | $75 | **$1,079.26** |
| December, 15 Dec | $313.69 | $32.15 | $45 | **$390.84** |
| Store pick-up (XPS, jig, ammo can) | $94.96 | $9.73 | 0 | **$104.69** |
| FAA registration (DroneZone, not taxed) | | | | **$5.00** |
| Whole BOM, baseline (excl. gated lines) | $1,319.54 | $135.25 | $120 | **$1,579.79** (`CL-I1-SPEND-BASE`) |
| Whole BOM, pessimistic (excl. gated lines) | $1,365.09 | $139.92 | $150 | **$1,687.01** (`CL-I1-SPEND-PESS`; + $5 FAA + $27 adders) |

## Reserve gate (hard: $2 000, reserve >= $309 on pessimistic numbers)

| Case | Spend | Reserve | Limit | Status |
|---|---|---|---|---|
| Committed order, baseline | $1,579.79 | $420.21 | >= $150 planned | `CHECKED` against inputs; prices `UNVERIFIED` |
| Committed order, pessimistic (Ovonic at list, tubes overseas, shipping +$30, tax measure +$7, jig/box +$20) | $1,687.01 | **$312.99** (margin $3.99) | >= $309 | `UNVERIFIED` |
| **Everything bought**, baseline (gated X07 box/field kit and X08 airspeed sensor included) | $1,764.78 | $235.22 | >= $150 | holds |
| **Everything bought**, pessimistic | $1,872.00 | **$128.00** | >= $309 | **FAILS by $181.00** (`CL-I1-RESERVE-PESS-ALLIN`) |

**Why two lines.** Itemising the designers' requests (F1, C6, D3, D5, D7, E3, F3, H1) adds about $190 incl. tax over the R1 BOM, because the old
$124.01 wiring/hardware lump did not cover them. The committed order holds the $309 reserve only by holding two blocks behind a gate:
X07 (D7 box and field kit, store pick-up, $118.85, needed before the first drive to the field in March, no lead time) and X08 (airspeed sensor,
$66.14, DECISION 5.1 lever, last in the lever order). Cheaper levers than X08, each needing a fact I cannot verify from here, are in `SUMMARY.md`.

## Early order, ~20 Nov (electronics, packs, test hardware, power parts)

Purpose: the $40 foam-board twin, the thrust stand, charging and first power bench on real hardware (`CONFIGURATION.md` de-risking). Place it as
five or six carts. Re-read every listing first (`T-I1-LISTINGS`).

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `B02`, `A05`, `W02`, `W06`, `W07`, `H01`, `F01` x5, `F02`, `F03`, `F04`, `F05`, `F06`, `F07`, `F08`, `F09`, `G01`, `G04`, `G05`, `G06`, `G08`, `G09`, `G10`, `G12` | $376.82 | $38.62 | $415.44 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| SunnySky USA | `B01` x5 | $124.95 | $12.81 | $137.76 | 5 | page 429 on 2026-11-09, price by search snippet; measure bolt pattern, hole depth and leads on arrival |
| RadioMaster | `A03`, `R01` | $84.98 | $8.71 | $93.69 | 5 | select the **FCC** variant for both RP3 V2 and Pocket Crush (CR-F5-06); not LBT |
| OVONIC US | `P01` | $82.97 | $8.50 | $91.47 | 7 **LONG** | **HOLD:** listing is 12 AWG leads, 680 g (CR-I1-13); sale price may end, list $119.88 is the pessimistic case |
| ReadyMadeRC | `A01` | $67.26 | $6.89 | $74.15 | 5 | FC page URL changed (product 87195); price carried from 2026-10-13; F3 gate (stable tailsitter build) before ordering |
| APC | `B03` x8, `B04` x4, `B05` x12 | $51.96 | $5.33 | $57.29 | 5 | props `CHK` $3.83; rings `EST` |
| Pine64 | `G07` | $25.99 | $2.66 | $28.65 | 7 |  |
| GetFPV | `R02` | $24.49 | $2.51 | $27.00 | 5 | 18650 cells: RadioMaster says batteries ship only with a radio order |
| Aloft Hobbies | `W03` | $24.00 | $2.46 | $26.46 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| RaceDayQuads | `A02` | $20.49 | $2.10 | $22.59 | 5 |  |
| Pyrodrone | `G02` x2 | $19.98 | $2.05 | $22.03 | 5 |  |
| Bolt Depot | `B07` x20, `C01` | $7.00 | $0.72 | $7.72 | 5 | minimum order may exceed the line price |

**Early total $1,079.26** (goods $910.89 + tax $93.37 + shipping $75 `EST`). Before the first charge (late Nov, store): `G03` ammo can,
Harbor Freight 63750, $19.99 + $2.05 tax. **Do not place the pack cart (`P01`) until CR-I1-13 is answered** (12 AWG leads, 680 g on the 2026-11-09 listing).

At order, in the cart:

| Check | Value | Why |
|---|---|---|
| Pack connector | XT60 (listing: "XT60 to TRA plug") | CR-I1-06; the AS150U pair `F01` is crimped on afterwards |
| Pack lead gauge | **>= 10 AWG** (listing says 12 AWG: fails) | CR-F1-14: 12 AWG rises 28.4 K at 30.3 A against 20 K |
| Pack mass | <= 658 g, expect 550 g (listing says 680 g: fails) | `HANDOFF` L2, `CL-A3-GATE-MARGIN-680` |
| RP3 V2 and Pocket Crush | FCC variant | CR-F5-06 |
| FC | CoreWing F405 Wing APP V2 (not the Mini: no bdshot) | CR-F3-06 |
| ESC | LANRC 4-pack: title, 45 A, 4 pieces, price | CR-I1-04 |

## Mid-December order, 15 Dec (airframe, mechanisms, fin and fastener kits)

Place the Aloft carbon cart first (tubes, strips, 20x18 tube), then the rest.

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `H02`, `H03`, `C02`, `C03`, `C04`, `C05`, `D04`, `D05`, `D06`, `G11` | $131.73 | $13.50 | $145.23 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| Aloft Hobbies | `W04` x2, `D01`, `D02` x3, `D03` | $96.00 | $9.84 | $105.84 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| West3D | `W05`, `W08` | $45.98 | $4.71 | $50.69 | 5 | ASA is not in the Jacobs free stock |
| EMAX USA | `M01` x2 | $39.98 | $4.10 | $44.08 | 7 | placeholder until D6 picks the servo (>= 3.04 kgf cm) |

**December total $390.84** (goods $313.69 + tax $32.15 + shipping $45 `EST`). Store pick-up in January (`LOCAL`):

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Home Depot El Cerrito | `W01`, `H05` | $74.97 | $7.68 | $82.65 | 0 | store pick-up; check the XPS sheet is flat |
| Harbor Freight | `G03` | $19.99 | $2.05 | $22.04 | 0 | store pick-up |

## Gated lines held in the BOM (not in any total above)

| Gate | Item | Cost incl. tax | Condition |
|---|---|---|---|
| X01 | 2nd LANRC ESC 4-pack (4 spare ESCs) | $33.08 | realised reserve after all December receipts >= $309 + this line incl. tax |
| X02 | Spare elevon servo (3rd ES3005HV) | $22.04 | as X01 |
| X03 | Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included) | $18.39 | as X01; only if the stand shows the MR/MRP pair short |
| X04 | Flight packs 3-4, one more Ovonic 2-pack | $91.47 | D-12: reserve after the December order >= $309 + $91.47 (at sale price); and only a SKU that passes CR-I1-13 |
| X05 | Small Parts CNC 4114 prop adapter set (2 RH + 2 LH), CR-E1-20 / D-39 | $26.40 | as X01; only if the motor-box adapters fail the stand (T-E1-STAND) and the page is back in stock |
| X06 | Remote ID module NewBeeDrone BeeID | $44.09 | only if flown outside the RFS FRIA |
| X07 | D7 box and field kit (lines T01-T06: Coroplast, tape, straps, handles, pouch, spanner, mat, PE foam) | $118.85 | as X01, before the first drive to the field (store pick-up, no lead time); until then a borrowed carton |
| X08 | RMRC MS4525DO airspeed sensor + pitot (line A04) | $66.14 | as X01; DECISION 5.1 lever, last in the order (CR-I1-03) |
| X09 | K-type thermocouple logger / 2-channel meter (E3 GT-04) | $16.54 | only if Jacobs Hall cannot lend one |

With the baseline reserve of $420.21, X07 + X08 ($184.99) leave $235.22: both fit on baseline, not on pessimistic numbers.
The gate test is the realised reserve (2 000 minus actual spend after the December receipts), not the pessimistic forecast.

## Borrow list (not bought, not in the BOM): H1's rig, Jacobs Hall (D-39)

Needs a yes from Jacobs Hall staff in writing before 20 Nov (`T-I1-BORROW`). Bought for the rig: G06 ($17.97, 20 kgf cell kit, already in the baseline) and G12 ($17.00, new, <= $20).

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
| Ovonic packs `P01` | 12 AWG leads and 680 g on the listing; sale ends | CR-I1-13: E2 and F1 name a SKU; order first once named |
| LANRC ESC `B02` | listing unconfirmed | open the page before 20 Nov; Tekko32 fallback +$60 |
| Small Parts adapters | out of stock; now gated X05 | E1's fallback: adapter in each motor box + Loctite 243 |
| FC `A01` | firmware support unconfirmed; page moved | F3 gate before ordering |
| Shipping | $120 baseline assumes few carts; this plan has about 14 vendors | free-shipping thresholds on Amazon, Aloft, RadioMaster; re-quote in cart |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |
