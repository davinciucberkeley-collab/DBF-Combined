# Order plan: early order (~20 Nov 2026) and mid-December order (15 Dec 2026)

Revision **I1-R5**, 2026-11-13 (CDR fix round, CDR-09 / CDR-10; see "What changed in R5"). Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv). Money: `python -I redesign/team/I1/build_bom.py`, then
`python -I redesign/team/I1/make_order_plan.py` regenerates the vendor tables below. Prices are 2026 list prices before 10.25 % tax.
`CHK` = compared with the vendor page on 2026-11-09, `CARRY` = carried from `cards/K09/cost.csv`, `EST` = estimate, no vendor page.

## Totals by order

| Order | Goods | Tax 10.25 % | Shipping `EST` | Total |
|---|---|---|---|---|
| Early, ~20 Nov | $1,098.55 | $112.60 | $77.14 | **$1,288.29** |
| December, 15 Dec | $218.00 | $22.34 | $17.14 | **$257.49** |
| Store pick-up (XPS, foam board, hot-wire bow stock, ammo can, 3M 77, sand, tether, filament tape) | $183.31 | $18.79 | 0 | **$202.10** |
| FAA registration (DroneZone, not taxed) | | | | **$5.00** |
| Pack import duty + brokerage `EST` (CDR-BT-06; 0 if a US-stock pack is found) | | | | **$20.00 / $45.00** |
| Whole BOM, baseline (excl. gated lines) | $1,499.86 | $153.74 | $94.29 (11 shipments) | **$1,772.89** (`CL-I1-SPEND-BASE`) |
| Whole BOM, pessimistic (excl. gated lines) | $1,548.42 | $158.71 | $117.86 | **$1,901.99** (`CL-I1-SPEND-PESS`; + $5 FAA + $45 duty + $27 adders) |

## Reserve gate (hard: $2 000, reserve >= $309 on pessimistic numbers)

| Case | Spend | Reserve | Limit | Status |
|---|---|---|---|---|
| Committed order, baseline | $1,772.89 | $227.11 | >= $150 planned | `CHECKED` against inputs; prices `UNVERIFIED` |
| **At order**, pessimistic (Ovonic at EUR 113.30 x 1.16 + $45 duty, tubes overseas, $10.71 per shipment, tax measure +$7, jig/box +$20) | $1,901.99 | **$98.01** (SHORT of $309 by $210.99; against the B3 proposal $227.89: short by $129.88) | >= $309 | `UNVERIFIED` **FAILS (CL-I1-RESERVE-PESS)** |
| **Flight-ready** (at order + X07 box and field kit + X08 airspeed sensor, decision B4), baseline | $2,042.47 | $-42.47 | >= 0 | **OVER $2 000** |
| **Flight-ready**, pessimistic | $2,235.84 | **$-235.84** | >= 0 | **OVER $2 000 (CL-I1-RESERVE-PESS-FLIGHT-READY)** |
| **Everything bought**, baseline (every gated BOM line: X07, X08, X10 flux/wick, X12 UBEC fallback, X13 microSD, X14 owned-or-borrowed list bought new, X15 caps) | $2,636.99 | $-636.99 | within $2 000; >= $150 planned | OVER BUDGET; under the $150 planned reserve by $786.99 |
| **Everything bought**, pessimistic | $2,941.05 | **$-941.05** | within $2 000 | **OVER BUDGET**: X14 bought new is the bound if nothing is owned or borrowed; no crash reserve left, so the gates still decide what is bought (`CL-I1-RESERVE-PESS-ALLIN`) |

**What changed in R5 (2026-11-13, CDR fix round: CDR-09, CDR-10; change-log rows D-130, D-131, D-134 in `review/CDR-2026-11-13/fixes/S4.md`).**
- **Spares to `R-CRASH-REPAIR` (CDR-09, CDR-BT-13):** `B08` second ESC 4-pack = 4 spare ESCs, December wave after `T-F2-DSHOT` passes (was gated X01); `B03` spare props 4 -> 8; `W03` stays the spare spar (T-C4-TUBE-BEND is a stiffness test; the ring-crush specimen comes from the `W04` offcut, 312 mm). The 3rd servo stays gated X02.
- **Levers applied (CDR-BT-03):** L1 foam board from the store, 10 sheets at $1.25 (`W02`); L2 microSD behind X13 (team stock); L3 fewer carts: `A01`, `A02`, `R01`, `R02`, `G02` in one RaceDayQuads cart, `B07` / `C01` in the Amazon cart. Shipping is now counted per paid shipment ($8.57 / $10.71, the R4 flat sum over its 14 vendors); this plan has 11 paid shipments at order.
- **Re-priced from pages read 2026-11-13:** `R01` $84.49 (RDQ); `A01` $69.49 (RDQ stack; the RMRC page is dead); `M01` AMain page $34.99 baseline / $41.99 pessimistic, moved to the 20 Nov cart; `C05` BSI 30 min 9 oz $22.99 (the old link was an $82.35 West System kit); `T01` Coroplast $37.98 a sheet.
- **Added:** pack duty + brokerage $20 / $45 `EST`; `B09` 11x7E props; `F03` second 16 AWG reel set; `W09` filament tape; `G16` 3M 77; `G17` sand bucket; `G18` tether. Chair A4: `W05` PETG, `D02` strip, `C05` epoxy (and `W08` ASA) move to the 20 Nov order.
- **Gated (D-131):** X14 = the owned-or-borrowed walk (CDR-11, 19 Nov): tools `K01`-`K07`, TPU `K08`, shop consumables `K09`-`K12`, fillers `C07` / `C08`, anemometer `G14`; X15 = 35 V caps only if the stand ripple run fails. Seven lines have no price on any page (`U01`-`U06`, `U08`, price "-", in no total).
- **Not applied (needs the students' sign-off):** decision B3 would re-base the crash line from $309 to $227.89; both are shown.

**What changed in R3 (CR-A1-67, D-72).** Pack re-priced for the Ovonic 120C EC5 pair (+$31.51 baseline, +$11.55 pessimistic, pre-tax); Savox SH-0255MG+ replaces the placeholder
servo (+$44.00); the $6 T-antennas, FC isolation set, F2 harness lines, D6 mechanisms hardware, 2.5 mm CF rod, PA66 socket-head set, 7/32 in brass tube and two strain gauges are
itemised; the D7 mat, tote, spares box and labels sit in the gated X07. Net of the designers' lines: pessimistic spend +$130.55 pre-tax ($143.94 incl. tax) before any lever.

**What changed in R4 (2026-11-13, owner fact: the Jacobs Hall Maker Pass is paid for the team outside the $2 000).** The pass is not a BOM line. It gives drop-in access to the
Jacobs Hall makerspaces, not loans: the Jacobs pages say nothing about checkout (`https://jacobsinstitute.berkeley.edu/making-at-jacobs/`, checked 2026-11-13). The Electronics Lab
(studio 110) lists soldering irons with solder provided, multimeters, power supplies, heat guns and fume extractors (`https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/`, checked 2026-11-13).
- **Old gate X10 (soldering kit, lever 1):** G07 Pinecil, G08 PD supply and G09 multimeter are **deleted** (-$70.99 pre-tax, -$78.27 incl. tax from every all-in case); the soldering is done in the lab. G10 (flux, wick; solder is provided) stays as a $16.54 gated fallback X10, bought only if the lab has none.
- **Old gate X11 (hot-wire gear, lever 2):** the page lists **no hot-wire foam cutter**, so the claim "hot-wire foam cutting is a stated Jacobs capability" is withdrawn and the BUILD-GUIDE statement (not listed) stands (MF-03). G11 and H05 are **bought** (+$62.54 incl. tax in every case); G11 moves to the 20 Nov order so the bow and two or three practice cores exist before Jacobs closes on 18 Dec.
- **T-I1-BORROW** is now "ask Jacobs staff" (flux and wick, K-type reading, hot-wire or ShopBot on foam, Spring 2027 pass), not a loan. No purchase waits on a written yes any more.
- Net: committed pessimistic spend +$62.54, so the pessimistic reserve falls from $346.26 to $98.01; the all-in pessimistic case improves from -$57.82 to $-941.05.
- **Open:** the committed pessimistic case is $210.99 under the $309 crash reserve. The pass cannot close it (Jacobs lists no hot-wire gear). Levers, none applied: a Jacobs yes on foam on the ShopBot would remove G11 + H05 (+$62.54); a confirmed USD Ovonic price replaces the EUR x 1.16 pessimistic guess on P01 (up to $18.69 incl. tax); the $7 tax adder lapses if Measure V takes effect after the last pick-up (a news report gives 1 Apr 2027, CDTFA has not published it: not relied on).

The committed order holds its reserve only by holding blocks behind gates: X07 (D7 box and field kit, store pick-up, needed before the first drive to the field in March), X08 (airspeed sensor, DECISION 5.1 lever), X10 (flux, wick), X12 (UBEC fallback).

## Early order, ~20 Nov (electronics, packs, test hardware, power parts)

Purpose: the $40 foam-board twin, the thrust stand, charging and first power bench on real hardware (`CONFIGURATION.md` de-risking). Place it as
five or six carts. **Place the pack cart (`P01`) first: ~14 days from Germany. Place the ReadyMadeRC FC cart (`A01`) the same day:** its board check closes the WB-01 blocker before the pod CAD freeze. Re-read every listing first (`T-I1-LISTINGS`).

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `B02`, `B07` x20, `A06`, `W06`, `W07`, `H06`, `F01` x5, `F02`, `F03` x2, `F07`, `F08`, `F09`, `C01`, `G01`, `G04`, `G05`, `G06`, `G11`, `G12` | $319.62 | $32.76 | $352.38 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| RaceDayQuads | `A01`, `A02`, `R01`, `R02`, `G02` x2 | $218.94 | $22.44 | $241.38 | 5 |  |
| SunnySky USA | `B01` x5 | $124.95 | $12.81 | $137.76 | 5 | page 429 on 2026-11-09, price by search snippet; measure bolt pattern, hole depth and leads on arrival |
| Ampow / OVONIC (same SKU) | `P01` | $114.48 | $11.73 | $126.21 | 14 **LONG** | **LONG LEAD (~14 d, ships from Germany); USD price not found**: baseline EUR 98.69 x 1.16, pessimistic EUR 113.30 x 1.16. Ask the seller for 10 AWG leads before paying |
| AMain Hobbies | `M01` x2, `C05` | $92.97 | $9.53 | $102.50 | 7 | Savox servos and BSI epoxy: AMain page showed **back-order** on 2026-11-13; buy from any dealer with stock (Hobby Etc. $41.99 servo) |
| APC | `B03` x12, `B04` x4, `B05` x12, `B09` x2 | $75.62 | $7.75 | $83.37 | 5 | props `CHK` $3.83; rings `EST` |
| West3D | `W05`, `W08` | $45.98 | $4.71 | $50.69 | 5 | ASA is not in the Jacobs free stock |
| Aloft Hobbies | `W03`, `D02` x3 | $42.00 | $4.30 | $46.30 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| Amazon / DigiKey | `H01` | $41.00 | $4.20 | $45.20 | 4 | JST-GH from DigiKey: separate shipping, use pigtails if the cart allows |
| RadioMaster | `A03` | $19.99 | $2.05 | $22.04 | 5 | select the **FCC** variant for both RP3 V2 and Pocket Crush (CR-F5-06); not LBT |
| DigiKey / Amazon | `H07` | $3.00 | $0.31 | $3.31 | 4 |  |

**Early total $1,288.29** (goods $1,098.55 + tax $112.60 + shipping $77.14 `EST`). Before the first charge (late Nov, store): `G03` ammo can,
Harbor Freight 63750, $19.99 + $2.05 tax. The pack cart (`P01`) is released by D-64 after the two checks below; **no USD price is confirmed**, read the cart total before paying (pessimistic case $131.43).

At order, in the cart:

| Check | Value | Why |
|---|---|---|
| Pack SKU | Ovonic 4S 6500 mAh **120C hard case, EC5, 2-pack**, listed 551 +/- 5 g, 135 x 46 x 49 mm | D-64, CR-E2-24; NOT the 130C XT60 SKU (680 g) |
| Pack lead gauge | **>= 10 AWG** confirmed by the seller (the page does not print it); 12 AWG: stop, tell E2 and F1 | CR-F1-14: 12 AWG rises 28.4 K at 30.3 A against 20 K |
| Pack mass on arrival | accept <= 560 g each (`CL-A3-PACK-ACCEPT`, one line since D-95) | weigh both, log in E2 `pack_log.csv` |
| RP3 V2 and Pocket Crush | FCC variant | CR-F5-06 |
| FC | CoreWing F405 Wing APP V2 (not the Mini: no bdshot); on arrival check the PDB board and the 470 uF cap are in the box, then run `subsystems/power/BOARD-CHECK.md` the same day | CR-F3-06, WB-01, D-74 |
| ESC | LANRC 4-pack: title, 45 A, 4 pieces, price | CR-I1-04 |

## Mid-December order, 15 Dec (airframe, mechanisms, fin and fastener kits)

Place the Aloft carbon cart first (tubes, strips, 20x18 tube), then the rest. Servos (Savox) have a 7-day lead `EST`: the same day.

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Amazon | `B08`, `A07`, `H03`, `C06`, `C02`, `C03` x2, `C04`, `D04`, `D05`, `D06`, `G13` | $113.00 | $11.58 | $124.58 | 5 | **LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each |
| Aloft Hobbies | `W04` x2, `D01`, `D03` | $78.00 | $7.99 | $86.00 | 5 | **LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST` |
| Amazon / hobby shop | `H02`, `D07` | $27.00 | $2.77 | $29.77 | 5 |  |

**December total $257.49** (goods $218.00 + tax $22.34 + shipping $17.14 `EST`). Store pick-up (`LOCAL`): `H05` and the XPS sheet `W01` are collected in late November / early December for the practice cores; `G03` before the first charge.

| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |
|---|---|---|---|---|---|---|
| Home Depot El Cerrito | `W01`, `G16`, `H05` | $87.98 | $9.02 | $97.00 | 0 | store pick-up; check the XPS sheet is flat |
| Tractor Supply / Home Depot (store) | `G17`, `G18` | $53.55 | $5.49 | $59.04 | 0 | sand, bucket, paracord, stakes |
| Harbor Freight | `G03` | $19.99 | $2.05 | $22.04 | 0 | store pick-up |
| Dollar Tree (store) | `W02` x10 | $12.50 | $1.28 | $13.78 | 0 | 10 single sheets, one store, one day (one brand, MF-21) |
| Staples (store) | `W09` | $9.29 | $0.95 | $10.24 | 0 | filament tape; Staples showed out of stock (snippet): School Specialty $17.99 fallback |

## Gated lines held in the BOM (not in any committed total above)

| Gate | Item | Cost incl. tax | Condition |
|---|---|---|---|
| X02 | Spare elevon servo (3rd Savox SH-0255MG+) | $46.29 | as X01; D6 and CR-A1-52 ask for 3, the reserve pays for 2 |
| X03 | Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included) | $18.39 | as X01; only if the stand shows the MR/MRP pair short |
| X04 | Flight packs 3-4, one more Ovonic 2-pack | $91.47 | D-12: reserve after the December order >= $309 + $91.47 (at sale price); and only a SKU that passes CR-I1-13 |
| X05 | Small Parts CNC 4114 prop adapter set (2 RH + 2 LH), CR-E1-20 / D-39 | $26.40 | as X01; only if the motor-box adapters fail the stand (T-E1-STAND) and the page is back in stock |
| X06 | Remote ID module NewBeeDrone BeeID | $44.09 | only if flown outside the RFS FRIA |
| X07 | D7 box and field kit (lines T01-T07: Coroplast, LSE tape, straps, handles, pouch, spanner, mat, PE foam, tote) | $194.88 | as X01, before the first drive to the field (store pick-up, no lead time); until then a borrowed carton |
| X08 | RMRC MS4525DO airspeed sensor + pitot (line A04) | $66.14 | as X01; DECISION 5.1 lever, last in the order (CR-I1-03) |
| X10 | Flux + desoldering wick if the Electronics Lab has none (G10) | $16.54 | first Electronics Lab visit: no flux or wick at the stations (the page says only 'solder provided'); then buy G10 |
| X12 | UBEC fallback (lines F04 20 AWG, F05 UBEC, F06 fuse + holder), D-74 | $30.87 | only if subsystems/power/BOARD-CHECK.md step 7 fails (servo-BEC Vx < 5.8 V at ~5.4 A); then a 4S-input 6 V UBEC (5-day lead), before the January build |
| X13 | microSD 16-32 GB (line A05), lever L2 | $6.62 | CDR-11 owned-or-borrowed walk (19 Nov): bought only if no team member has a card |
| X14 | Owned-or-borrowed list (lines K01-K12: torque driver, scales, inclinometer, Z-bend pliers, prop balancer, hex drivers, TPU, blades, sandpaper, cups, IPA; U03-U06, U08 unpriced) | $450.51 | CDR-11 walk (19 Nov): each item owned, borrowed (lender named) or bought; only the bought ones are ordered, early cart or store |
| X15 | 35 V low-ESR caps x5 (line F10), CDR-EL-05 | $12.84 | GT-04 on the stand with the F07 25 V cap: buy only if cap-leg ripple exceeds the F07 rating (1.79 A at 100 kHz) or the can rises > 15 K |
| X09 | K-type thermocouple logger / 2-channel meter (E3 GT-04) | $16.54 | only if no Electronics Lab multimeter reads the K-type probes in the lab (Jacobs does not lend equipment out; the pass is drop-in access) |

Flight-ready (X07 + X08 bought, decision B4): reserve $-42.47 baseline, $-235.84 pessimistic.
The gate test is the realised reserve (2 000 minus actual spend after the December receipts), not the pessimistic forecast.

## Not bought: Jacobs Maker Pass equipment and team-owned items (D-39, D-72, R4)

The Maker Pass (paid outside the budget) is **in-lab use**, with trainings (`https://jacobsinstitute.berkeley.edu/making-at-jacobs/`, checked 2026-11-13). Plan every task that uses these tools for a Jacobs day (fall access ends 18 Dec; spring access dates are not published on the pass page).

| Tool, covered by the pass | Lines it replaces | Used for | Where on the lab list |
|---|---|---|---|
| Soldering station with solder, fume extractor | old `G07` (Pinecil), `G08` (PD supply), `G10` solder | harness, ESC leads, AS150U re-termination | Electronics Lab, studio 110 |
| Multimeters, bench power supplies, oscilloscope, heat gun | old `G09`; ground tests | rails, continuity, heat-shrink | Electronics Lab |
| Laser cutters (3 x 32 x 18 in; 1 x 48 x 25 in), Prusa printers (PLA free), drill presses, band saw, PCB shear, spray booth | none bought | templates, fins, jigs, prints, FR4 bus board, 3M 77 | labs-and-equipment page |

Bought for the hot wire (not on the Jacobs list): `G11` 30 V supply + Ni80 wire and `H05` bow and template stock, $62.54 incl. tax.

Bought for the rig: G06 ($17.97, 20 kgf cell kit, already in the baseline), G12 ($17.00) and G13 ($9.00, fin-proof strain gauges, CR-C4-38).

| Item | From H1's list ($ `EST`) | If no team member owns one |
|---|---|---|
| 2 x 5 kg x 1 g scales | 30 | team-owned or buy; +$33 incl. tax |
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
| Jacobs pass | drop-in only, no loans; spring access dates unpublished; paid outside the budget by the owner | confirm Spring 2027 covers all four from 19 Jan (`T-I1-BORROW`); soldering needs a lab day |
| LANRC ESC `B02` | listing unconfirmed | open the page before 20 Nov; Tekko32 fallback +$60 |
| Small Parts adapters | out of stock; now gated X05 | E1's fallback: adapter in each motor box + Loctite 243 |
| FC `A01` | power-board facts (split, link, outline) are from the manual only; page moved | order in the first cart; `BOARD-CHECK.md` on arrival before the pod CAD freeze (WB-01) |
| Shipping | $120 baseline assumes few carts; this plan has about 14 vendors | free-shipping thresholds on Amazon, Aloft, RadioMaster; re-quote in cart |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |
