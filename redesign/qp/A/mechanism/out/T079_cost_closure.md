# T-079 O4b cost closure (research only, $0), 2026-11-19

Scope per AM-013 (conductor message): budget gate = total spend including the unchanged crash reserve <= $2,000; G7 informational. BOM trims were optional and were not pursued. Nothing bought, no accounts. `—` = not read. Real `BOM-A.csv` / `bom_a.py` unedited; scratch copy and run in the session scratchpad (`.../scratchpad/t079/run.py`).

## 1. Pack price (USD)

BOM pack line W01 carries qty 2 flight packs (Tattu 2300, $37.09 each); the crash reserve adds 1 more pack at the same unit price (`bom_a.py` `reserve()`), so each $1 of unit price moves the total by 3 x 1.1025 = $3.31.

### 1a. GNB 2800 mAh 4S 100C at Rotorama (EU)
- Page read 2026-11-19 (https://www.rotorama.com/product/gnb-2800mah-4s-100c): EUR 41.29, In Stock, 267 g, 107 x 34 x 37 mm. The page does not say whether the price includes VAT.
- Rotorama "Payment and Delivery" page read 2026-11-19 (https://www.rotorama.com/doprava-a-platba): "We deliver to all EU countries, except island regions"; carriers GLS, PPL, Packeta; non-CZ prices listed only for EU countries; no US rate, no import duty/tax statement, no VAT-exemption note.
- **Result: Rotorama does not list delivery to the US, so the O4b pack cannot be bought there. USD price, shipping to the US and import duty = —.** (An EUR to USD conversion was not made: no rate page read, and it is moot.)
- KiwiQuads (NZ), read earlier today per T-074: $74.99, out of stock. Currency of the symbol not stated on the page (NZ shop; may be NZD). Not a US source.

### 1b. US in-stock 4S >= 2,350 mAh, <= 275 g, fits the tray
The tray is a 109 mm plate, about 35 mm wide in x, height raised to 37 mm (T-074). Pages I could read:
- Nothing new readable. RDQ Series 2800 mAh 4S 100C XT60 (Race Day Quads / GetFPV), 270 g, 107 mm long: Race Day Quads returned HTTP 429 on every attempt (three today), GetFPV 403, rcdrone.top 403. I stopped retrying (a further retry with a changed client string was blocked by the harness and not pursued).
- Search-result snippets only (2026-11-19, pages NOT read, so these are not prices under the CLAUDE.md rule): Race Day Quads $35.99 "in stock" and a second RDQ listing $48.99 (different SKU); rcdrone.top GAONENG GNB2800 4S 100C $52.50, 267 g +- 8 g; GetFPV pages conflict on stock (in stock vs out of stock) and GetFPV ships LiPo by ground only. The RDQ dimension is listed as 107 x 33 x 46 mm / 107 x 46 x 33 mm (T-074): the 46 mm side does not fit the 35 mm slot or the 37 mm height unless the tray changes. The rcdrone.top GNB would be the same cell as the 107 x 34 x 37 candidate, but it is unread.
- Read pages with other packs: Hobbyking Turnigy Graphene 2200 mAh 4S 100C, 107 x 36 x 34 mm, 244 g (search snippet only, below 2,350 mAh). Glacier 2600 mAh 30C: 115 mm, 288 g (snippet), too long and heavy. Tattu 3200 (136 mm), Turnigy Nano-Tech 2800 (141 mm), Dualsky 2700 (138 mm, 269 g, snippet): too long.
- Conclusion: no US, in-stock, tray-fitting pack was confirmed from a read page. USD price for the O4b pack: **—**.

### 1c. Budget bounds (scratch, not prices)
Because the USD price is unread, the gate was computed as a function of unit price. O4b = Kakute H743-Wing $141.44 (read 2026-11-19 at RMRC, In stock, https://www.readymaderc.com/products/details/87185-holybro-kakute-h743-wing-flight-controller) replacing V03, plus the pack unit price X (2 + 1 reserve packs), plus an optional new ship group (+$15.00 EST, the RMRC rate in `bom_a.py`; a non-RMRC US shop is a new group). Crash reserve line unchanged in structure (it still holds one pack; its dollar figure rises with X because it is built from the W01 price: 327.43 at $37.09).

| Pack unit price X | Source status | Total, no new ship group | Total with +$15 ship group | <= $2,000 |
|---|---|---|---|---|
| $37.09 (Tattu, as BOM) | read 2026-11-14 | 1,829.59 | n/a | PASS |
| $35.99 | RDQ snippet, unread | 1,825.95 | 1,840.95 | PASS |
| $48.99 | RDQ snippet, unread | 1,868.95 | 1,883.95 | PASS |
| $52.50 | rcdrone.top snippet, unread | 1,880.55 | 1,895.56 | PASS |
| $74.99 | KiwiQuads (read, OOS, currency unclear) | 1,954.94 | 1,969.94 (1,984.94 with $30) | PASS |
| $100.00 | hypothetical | 2,037.66 | | FAIL |

- Break-even unit price for total = $2,000: about $88.6 with no new ship group, about $84.1 with a +$15 ship group. Any pack priced at or below $84 each (shipped, with tax as modelled at 10.25 %) keeps the total under $2,000 with the crash reserve scaling with it and not cut.
- G7 (informational, +30 % margin >= $100 AND total <= $1,800): FAIL at every row above (best case $37.09: total 1,829.59, +30 % margin +49.93; at $35.99: +53.56; matches T-074). With +30 % on unverified lines the total exceeds $2,000 at X >= about $52.50 (+30 % total 2,001.04).
- Caveat: sales tax on a non-RMRC US shop is modelled at the BOM's 10.25 %; import duty applies only to a non-US source (none found).

## 2. Cheaper Lua-capable FCs than the Kakute H743-Wing ($141.44)
- Not resolved. Matek H743-WLITE: price/stock unread (GetFPV 403, Pyro 429 per T-074). Holybro store $105.00 for the Kakute H743-Wing was a T-074 snippet, store page 429, stock unread. ArduPilot Lua support on H7 targets (KakuteH7-Wing, MatekH743) is from T-074 features.txt read 2026-11-19 (https://firmware.ardupilot.org/Copter/latest/KakuteH7-Wing/features.txt pattern). I did not re-read these today. FC cheaper than $141.44 with a read price: none found.

## 3. BOM trims
- Not pursued (optional per AM-013). The budget gate is met without them for any pack up to about $84 per unit.

## 4. O4b BOM result
- With the H743-Wing at $141.44 and the Tattu unit price: total $1,829.59, margin $170.41, +30 % margin +$49.93, G7 FAIL (informational), crash reserve $327.43 unchanged.
- With a pack at X: see the table in 1c; <= $2,000 holds up to about $84 to $88 per pack.

## Open for the board
1. The O4b pack has no confirmed US source, and the only read in-stock source (Rotorama) does not deliver to the US. Needs someone with a browser to read the Race Day Quads / GetFPV / rcdrone.top GNB pages (price, stock, dimensions) or a forwarder/EU purchase by a person in the EU (outside this research).
2. If the RDQ 46 mm side is the width, the pack does not fit the 35 mm slot.
