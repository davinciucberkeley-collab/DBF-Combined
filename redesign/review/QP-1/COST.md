# QP-1 cost confirmation (2026-11-14)

Reproduce: `python -I redesign/qp/cost/bom_qp1.py` (reads `redesign/qp/cost/BOM-QP1.csv`). Labels: V = vendor page read 2026-11-14, U = not read, EST = estimate.
Basis: tax 10.25 %, FAA $5, crash reserve = (flight pack + servo + airframe set) x 1.1025 + 2 shipments (RESTUDY rule).

## Result

| Config | Spend | Crash reserve | **Total** | **Margin** | Margin if EST/U lines +30 % |
|---|---|---|---|---|---|
| B quadplane 4+1 | 1,342.11 | 179.92 | **1,522.03** | **+477.97** | +380.75 |
| A scaled tailsitter | 1,130.29 | 138.13 | **1,268.42** | **+731.58** | +637.67 |
| D2 ZOHD Altus VTOL | 1,317.15 | 235.04 | **1,552.19** | **+447.81** | +345.95 |
| T scratch tilt-tri | not priced | | | | `sizing_T/` had not landed; the board uses T's own estimate |

RESTUDY gave B 1,625 / +375, A 1,461 / +539, D2 1,549 / +451. `sizing_A/` had not landed either, so A is priced with the RESTUDY parts.
Floor goods 606.87 (RESTUDY 602.31). Lines: 25 V, 1 U, 10 EST. EST/U goods are about $284-308 per config, about 25 % of goods.

## Caveats on the V lines

- **One consolidated vendor.** Nearly every V line is Ready Made RC (readymaderc.com, Ohio), so there is one parts shipment plus Amazon plus local pickup (Home Depot, Harbor Freight). RMRC checkout rates are not readable: its shipping page lists carriers and a 5 %-of-order free-shipping rule but no dollar rates. Shipping is EST $15 per RMRC order, $10.71 Amazon, $0 pickup. Total shipping is $25.71.
- **Other vendors could not be read.** RaceDayQuads, BuddyRC, Pyrodrone, ChinaHobbyLine and Defiance returned 429; GetFPV returned 403. Their prices are search snippets only and are not used. I did not work around the blocks.
- **Not buyable today.** F04 GPS (Foxeer M10Q-250, $20.68) is on backorder (page says November 2026); Holybro Micro M10 is also backorder. The CoreWing/SpeedyBee F405 Wing V2 ($67.26) and Matek ASPD-4525 ($49.87) are Unavailable at RMRC, so the FC and airspeed lines use the in-stock substitutes below.
- **Pack mismatch.** No 4S 3000 mAh pack is in stock at a readable vendor. B and D2 use Tattu 3700 mAh 4S 45C ($59.99, 361 g, in stock; sizing assumed 356 g). A uses Tattu 2300 mAh 4S 75C ($37.09, 270 g vs 245 g assumed; the 45C version is discontinued).
- **ESC mass.** The only in-stock 30 A ESC read is HobbyWing Skywalker 30A V2 at 33 g with a 5 V BEC. It replaces the assumed 10 g ESCs, adding about 115 g to B and A. It is not confirmed for fast multirotor PWM. Sizing agents must rerun mass.
- **D2.** The RMRC product page reads $299.99 "In Stock", but its collection-page snippet said backorder. The kit is unassembled and has no FC, RX or battery. The earlier RESTUDY "V" for D2 used a wrong slug; the right page is `86192-zohd-altus-fpv-vtol-pnp`. The alternative route (Altus PNP $159.99 at RMRC plus a VTOL kit at about $120-130 in snippets) is not read and not priced.

## Jacobs Hall (labs-and-equipment page, read 2026-11-14)

Free under the Maker Pass: soldering irons with solder provided, multimeters, oscilloscopes, power supplies, hand tools, drill/jigsaw/sander, Prusa printers (no cost, no training, PLA), laser cutters. I removed the Pinecil, PD supply and multimeter from the floor (about $46 + $25). Not listed: calipers, scale, IR thermometer, load cell, watt meter, hot-wire cutter. Filament price is not given, so PETG stays EST. The page also says the Electronics Lab is the only iron and Jacobs closes 19 Dec to 18 Jan (BUILD-GUIDE).

## Lines that moved more than 20 % (per unit, vs RESTUDY)

| Line | Was | Now | Change | Cause |
|---|---|---|---|---|
| F03 flight controller | 51.99 | 95.98 | +85 % | Kakute F405 Wing Mini: the cheap board is unavailable at the only readable vendor. Switching back to the CoreWing at $67-69 would cut about $29 + tax once its page is readable |
| F11a watt meter | 12.99 | 35.31 | +172 % | WM150 read on RMRC; the old value was a card figure |
| F12 soldering | 60.99 | 15.00 | -75 % | Jacobs provides iron, solder and supply |
| F09 LiPo bag | 9.99 | 7.61 | -24 % | TBS bag |
| X2212 motor (B, A) | 30.00 | 15.99 | -47 % | RMRC multirotor CW/CCW pages; the old figure was an EST |
| ESC (B, A) | 7.50 each | 14.99 each | +100 % | Skywalker singles replace a 4-pack EST |
| Pack (B, D2) | 42.00 | 59.99 | +43 % | Tattu 3700 replaces an EST 3000 mAh |
| 9x4.5 prop pair (A) | 7.00 | 2.99 | -57 % | SunnySky 9045 pair |
| Carbon tube (A) | 40.00 | 27.46 | -31 % | RMRC 16x14 mm, 1 m |

## Still EST or not read

F06, F11b, F13 (floor); foam (Home Depot), PETG, hardware, D2 spares and modification budget; F10 ammo can (U, Harbor Freight). The shipping rates. Maker thrust for X2212 on 4S is still unmeasured.

## Reading

All three clear the $100 margin on the read prices, and B, A and D2 hold above +$345 with EST lines +30 %. B and D2 are about $30 apart in total. B's margin rests on the in-stock substitutes above and on EST foam/hardware. Two procurement actions help: place one RMRC order once the GPS is off backorder, and buy the FC from whichever vendor shows the CoreWing in stock.
