# Budget energy, charging and test kit — live price sweep

Date checked for every price and spec below: **2026-10-13**. Prices are USD, before sales tax.
Tax: — (the Berkeley sales-tax rate was not looked up in this sweep; add it before committing
the budget).

## Verdict

- **Cheapest pack that covers the worst-case mission: HOOVO 6S 8000 mAh 100C EC5, 2-pack $199.99**
  ($100.00 per pack, 177.6 Wh, 986.3 g, 180 Wh/kg, ships from Amazon). It is a car pack with
  metal plates, so it is heavy for its energy. Its "100C" (800 A) rating is a marketing number.
- **Cheapest credible pack in 140–220 Wh: Ovonic 6S 6500 mAh 100C EC5, 2-pack $138.99**
  ($69.50 per pack, 144.3 Wh, 820 g, 176 Wh/kg). Close second: the **Ovonic Roam 6500 150C XT90-S
  at $71.99 each** (777 g from Ovonic's own page, 186 Wh/kg). Both are below the worst-case energy
  need once you allow a usable-depth margin (see the energy check).
- **Cheapest charger that reaches ≥ 5 A on 6S from wall AC: HTRC C150 150 W, $56.99 (Amazon) /
  $57.99 (Pyrodrone).** 150 W / 25.2 V = 5.95 A.
  **The ToolkitRC M7AC fails the ≥ 5 A requirement:** its AC output is 100 W, so
  100 / 25.2 = 3.97 A.
- **Cheapest safety and test kit: $68.92** on Amazon and Harbor Freight. That covers a LiPo bag, an
  ammo can, a watt meter, an IR thermometer, a 20 kg load cell with HX711, and a Nano clone.
  Swapping in the SparkFun load cell and amplifier makes it $77.84 plus SparkFun shipping (—).

### Energy check (estimate)
Mission from the task brief: hover 0.6–0.9 kW for 3 min, then cruise 300–450 W for 10 min.

| Case | Hover Wh | Cruise Wh | Total Wh | Pack Wh needed at 80 % usable (estimate) |
|---|---:|---:|---:|---:|
| Best | 0.6 kW × 3/60 h = 30 | 300 W × 10/60 h = 50 | 80 | 100 |
| Worst | 0.9 kW × 3/60 h = 45 | 450 W × 10/60 h = 75 | 120 | 150 |

The 80 % usable depth is an assumption, not a measured value. A 144 Wh pack gives
0.8 × 144.3 = 115 Wh, which falls short of the 120 Wh worst case. A 177.6 Wh pack gives 142 Wh,
which covers it.

Hover current at the 6S nominal voltage: 600 W / 22.2 V = 27 A and 900 W / 22.2 V = 41 A. A
≥ 60 A continuous rating therefore leaves about 1.5× margin over worst-case hover.

## 1. 6S flight packs, sorted by $/Wh

Wh = mAh / 1000 × V nominal (the voltage the page states; Li-ion packs use the cell rated voltage
where the page gives one). Wh/kg = Wh / (g / 1000). "Claim A" = C × Ah, taken from the page's own C
rating. **Every LiPo claim from 480 A to 1200 A is not credible:** it is far beyond what an
EC5/XT90 connector and 10–12 AWG leads carry continuously. Treat these packs as "≥ 60 A plausible,
unverified" until the team measures them (M1).

| # | Pack (part no. / ASIN) | Chem | mAh | V | Wh | g (page) | Wh/kg | Cont. A (page) | Conn. | Price / pack | $/Wh | Vendor | Stock | Ships from | Shipping | In 140–220 Wh? |
|---|---|---|---:|---:|---:|---:|---:|---|---|---:|---:|---|---|---|---|---|
| 1 | Ovonic 6500 mAh 100C 6S, 2-pack (B09CTRKLM4) | LiPo | 6500 | 22.2 | 144.3 | 820 ⚠ | 176 | 100C = 650 A claim | EC5 | $69.50 ($138.99 / 2) | 0.482 | Amazon, sold by Ovonic Direct | In stock | Amazon | Free delivery shown | Yes |
| 2 | Ovonic Roam 6500 mAh 150C 6S1P (B0D3HQLGDG) | LiPo | 6500 | 22.2 | 144.3 | 777 (ovonicshop.com) | 186 | 150C = 975 A claim | XT90-S | $71.99 | 0.499 | Amazon, sold by Ovonic Direct | "Only 10 left" | Amazon | Free delivery shown | Yes |
| 3 | DIY 6S2P from 12× Molicel P50B (RDQ 2-pc pack, SKU 23432) | Li-ion cells | 10000 | 22.2 (3.7 V/cell per page) | 222.0 | — (cell weight not on page) | — | 60 A/cell → 120 A (6S2P) | — | $110.94 (6 × $18.49), cells only | 0.500 | RaceDayQuads | In stock | US (ground only) | — | No (222 Wh) |
| 4 | HOOVO 8000 mAh 100C 6S, 2-pack (B093S2164J) | LiPo | 8000 | 22.2 | 177.6 | 986.3 | 180 | 100C = 800 A claim | EC5 | $100.00 ($199.99 / 2) | 0.563 | Amazon, sold by Hoovo | Not stated; delivers Oct 22–28 | Amazon | Free delivery shown | Yes |
| 5 | Zeee 9000 mAh 100C 6S, 2-pack (B099KQ4JJ8) | LiPo | 9000 | 22.2 | 199.8 | 1136 | 176 | 100C = 900 A claim | EC5 | $121.05 ($242.09 / 2) | 0.606 | Amazon, sold by ZEEE POWER Direct | Not stated; delivers Oct 22–28 | Amazon | Free delivery shown | Yes |
| 6 | Zeee 10000 mAh 120C 6S, 2-pack (B0BHQX8XQX) | LiPo | 10000 | 22.2 | 222.0 | 1150 | 193 | 120C = 1200 A claim ⚠ | EC5 | $137.70 ($275.39 / 2) | 0.620 | Amazon, sold by ZEEE POWER Direct | Not stated; delivers Oct 22–28 | Amazon | Free delivery shown | Just over (222) |
| 7 | CNHL Racing 9500 mAh 90C (950906XT90) | LiPo | 9500 | 22.2 | 210.9 | 1100 | 192 | 90C = 855 A claim | XT90 | $139.99 | 0.664 | chinahobbyline.com | **US: out of stock**; Global: in stock | China (Global whse) | US rate not listed in the policy; 15–25 days | Yes |
| 8 | Zeee 9000 mAh 100C, 2-pack (lipo-222v-011-US) | LiPo | 9000 | 22.2 | 199.8 | 1136 | 176 | 100C | EC5 | $134.50 ($268.99 / 2) | 0.673 | zeeebattery.com | US: in stock | US whse | Free over $59; signature, no PO box | Yes |
| 9 | HOOVO 10000 mAh 120C, 2-pack (B09YM8JK57) | LiPo | 10000 | 22.2 | 222.0 | 1049 | 212 | 120C = 1200 A claim ⚠ | EC5 | $150.00 ($299.99 / 2) | 0.676 | Amazon, sold by Hoovo | "Only 2 left" | Amazon | Free delivery shown | Just over (222) |
| 10 | Zeee 10000 mAh 120C, 2-pack (lipo-222v-012-US) | LiPo | 10000 | 22.2 | 222.0 | 1150 | 193 | 120C | EC5 | $153.00 ($305.99 / 2) | 0.689 | zeeebattery.com | US: in stock | US whse | Free over $59 | Just over (222) |
| 11 | iFlight Fullsend E 8000 mAh 60C 6S1P (V1-14089) | LiPo | 8000 | 22.2 | 177.6 | 990 | 179 | 60C = 480 A claim | XT60 | $122.99 | 0.693 | Pyrodrone | In stock | US (ground only) | Free over $199 | Yes |
| 12 | CNHL Long Range 10000 mAh 6S2P BAK 50D (LI1000106S70XT60) | Li-ion 21700 | 10000 | 21.6 | 216.0 | 852 | 254 | **— (not stated)** | XT60 | $149.99 | 0.694 | chinahobbyline.com | **US: out of stock**; Global: in stock | China (Global whse) | US rate not listed | Yes |
| 13 | Lumenier NAV 10000 mAh 6S 21700 (SKU 22801) | Li-ion 21700 | 10000 | 21.6 (3.6 V/cell) | 216.0 | 975 | 222 | **35 A** (80 °C cutoff) — **fails ≥ 60 A** | XT60 | $149.99 | 0.694 | RaceDayQuads | In stock | US (ground only) | — (not listed) | Yes |
| 14 | Lumenier NAV 12000 mAh 6S 21700 (SKU 22805) | Li-ion 21700 | 12000 | 21.6 | 259.2 | 1402 | 185 | **50 A** — fails | XT90 | $189.99 | 0.733 | RaceDayQuads | In stock | US (ground only) | — | No |
| 15 | Gaoneng GNB 8000 mAh 6S2P Samsung 40T (GNB80006S10R) | Li-ion 21700 | 8000 | 22.2 (page) | 177.6 | 904 | 196 | 10C = **80 A** ✓ | XT60 | $135.99 | 0.766 | Pyrodrone | In stock | US (ground only) | Free over $199 | Yes |
| 16 | Lumenier 10000 mAh 6S 25C LiPo (SKU 2452) | LiPo | 10000 | 22.2 | 222.0 | 1245 | 178 | 25C = 250 A claim | XT90 | $251.49 | 1.133 | RaceDayQuads | In stock | US (ground only) | — | Just over |
| 17 | Tattu G-Tech 9000 mAh 6S 25C (G23880CN1Z) | LiPo | 9000 | 22.2 | 199.8 | 1175 | 170 | 25C = 225 A claim | XT60 | $249.49 | 1.249 | RaceDayQuads | In stock | US (ground only) | — | Yes |

⚠ = see "Amazon / spec flags" below.

**Out of range or unavailable (recorded for completeness):**

| Pack | Why excluded | Price | Source |
|---|---|---:|---|
| Ovonic Roam 5200 mAh 150C XT90-S (B0D3HS6FMC), 678 g | 115.4 Wh, below 140 Wh | $56.99 | Amazon |
| Auline 18650 V45 6S2P 6000 mAh 90 A (SKU 23417), 594 g | 133.2 Wh, below 140 Wh | $164.99 | RaceDayQuads |
| CNHL 8000 mAh 6S 30C XT90 (800306Z), 1300 g | Out of stock in every warehouse | $93.99 | chinahobbyline.com |
| CNHL Racing 6200 / 5200 mAh 90C | US out of stock; 137.6 / 115.4 Wh | $85.99 / $76.99 | chinahobbyline.com |
| iFlight Fullsend LR 8000 mAh 6S2P Li-ion, 840 g | Out of stock | $129.99 | Pyrodrone |
| NewBeeDrone Nitro Nectar GOLD 50XG 10000 mAh 6S2P | Page says "Out Of Stock!"; no weight, current or connector given | $189.99 | newbeedrone.com |
| Upgrade Energy Red V4 10000 mAh 6S2P Amprius, 860 g, 100 A | Out of stock at RDQ (JSON) | $259.99 | RaceDayQuads |
| Flywoo Explorer P45B 6S2P 9000 mAh | Sold out (UK store, £63.19); flywoo.net returned 403 | — | unmannedtechshop.co.uk |
| Tattu 10000 mAh 6S 30C UAV Classic EC5 | Out of stock | $216.99 | genstattu.com |
| Gens Ace / Tattu other 6S 5–10 Ah | Search and listing pages are JS-rendered and showed nothing live; Amazon Gens Ace 6800 2-pk $299.98 | — | genstattu.com, Amazon |
| HRB 6S 8000–10000 | No HRB 6S ≥ 6000 mAh came up in the Amazon search; only HRB 6S 5000 50C XT60 at $86.00 (no reviews) | — | Amazon |
| Turnigy / HobbyKing US warehouse | hobbyking.com search results are JS-templated; no price could be read | — | hobbyking.com |
| SMC | smc-racing.net timed out | — | — |

**Shipping and hazmat notes stated on the pages:**
- RaceDayQuads: "All batteries must be shipped by a ground shipping method" (on each battery
  page). The policy page lists no rates or free-shipping threshold.
- Pyrodrone: LiPo ships ground only (UPS Ground or USPS Ground Advantage) and cannot ship outside
  the US. Free US shipping over $199 (banner) / $200 (policy).
- Zeee US warehouse: free over $59. Below that, $3.96–$12.24 by weight. Street address and
  signature are required.
- CNHL: the US warehouse is free over $79, but **every 6S pack in range is out of stock in the
  US**. The policy table does not list a US rate for the Global warehouse. CN2 lists "RC
  helicopters and planes from $39.99".
- Amazon: every listing shown has "FREE delivery". No hazmat surcharge is shown.

**DIY P50B note:** 12 cells at $18.49 per 2 is the cheapest 220 Wh route. The cell price leaves
out nickel strip, a spot welder, a balance lead, wrap and the main lead, all —. It also adds a
build-quality risk the team would own. It is listed for scale, not as the recommendation.

### Amazon / spec flags (unreliable listing data)
1. **Ovonic B09CTRKLM4** gives the weight as "820kg / 1.81lb". 1.81 lb = 821 g, so 820 g is used.
2. **HOOVO B09YM8JK57** claims "up to 300Wh/kg". Its own numbers work out to 222 Wh / 1.049 kg =
   212 Wh/kg.
3. **Every Amazon LiPo C rating** (100C–150C) implies 650–1200 A, which is not credible.
4. **The HOOVO, Zeee 9000 and Zeee 10000 packs are RC-car packs with metal plates on 5 sides**, so
   their weight includes plates an aircraft does not need.
5. **Third-party "Fullsend 6S2P 10000" listings** (B0HLNVZYQ4 $257.82, B0HLL3ZXJF $351.83,
   B0HLP1889Z $340.33) and the unbranded "6S 22.2V 10000mAh 100C XT60" (B0HKWW5VV3, $241.10) have
   no reviews and are priced 2× iFlight's own. Avoid them.
6. **Generic 150 A watt meters:** "150A" is a seller claim with 12 AWG leads. Do not run them near
   that.
7. **The HTRC charger listing B0H4QLJYHY** has a spec table reading "Input Voltage 240 volts /
   Current Rating 10 A", which is a template artifact. Use the bullet text (150 W, 0.1–10 A).
8. **The Lumenier NAV 10000 page** lists "WATT HOURS 36.0WH" on a 10 Ah 6S pack, which is
   inconsistent. The Wh above is recomputed.

## 2. AC chargers — 6S current from wall power

6S charge current = AC output W / 25.2 V (6 × 4.20 V, end of charge), capped by the charger's
current limit.

| Charger | AC output W (page) | Max A (page) | 6S A from AC = W/25.2 | ≥ 5 A? | Price | Vendor | Stock |
|---|---:|---:|---:|---|---:|---|---|
| **HTRC C150** (HTRC brand per Amazon details) | 150 (AC/DC; no separate AC limit stated) | 10 | **5.95** | **Yes** | **$56.99** | Amazon B0H4QLJYHY (Sage Direct Store) | In stock |
| HTRC C150 | 150 | 10 | 5.95 | Yes | $57.99 | Pyrodrone | In stock |
| Generic 150 W 10 A AC/DC (B07YD3JNTZ) | 150 | 10 | 5.95 | Yes (unverified brand) | $56.99 | Amazon | Listed |
| Haisito C150 | 150 | 10 | 5.95 | Yes | $62.99 | Amazon B0H6J7DZL2 (Xinshangrui) | In stock |
| ISDT D2 Mark II (2 ch) | 200 total | 12 × 2 | 7.94 (one pack) | Yes | $96.00 | chinahobbyline.com (Global whse) | In stock |
| Ovonic X1 (2 ch) | 200 | 15 | 7.94 | Yes | $100.69 | Amazon B0GS5FRW5F | Listed |
| HOTA H6 Pro | 200 | 26 (DC) | 7.94 | Yes | $106.99 | RaceDayQuads | In stock |
| HOTA H6 Pro | 200 | — | 7.94 | Yes | $113.99 | Pyrodrone | In stock |
| HOTA D6 Pro (2 ch) | 200 | 15 | 7.94 | Yes | $115.99 | Amazon B0D4MC4GPC | Listed |
| ISDT K2 Air (2 ch) | 200 total | 20 | 7.94 | Yes | $117.50 / $129.99 / $139.99 | Amazon B092J5LTBW / CNHL / NewBeeDrone | In stock |
| HTRC T400 Pro (2 ch) | 200 total | 12 | 7.94 | Yes | $116.99 | Pyrodrone | **Out of stock** |
| **ToolkitRC M7AC** | **100** | 15 (DC) | **3.97** | **No** | $74.99 | NewBeeDrone | Out of stock |
| ToolkitRC M6AC | AC input max 120 W; AC output — (Pyrodrone title: "AC 100W") | 15 (DC) | ≤ 3.97 | No | $71.99 / $76.99 | RaceDayQuads / Pyrodrone | In stock / OOS |
| ISDT 608AC | 50 | 8 (DC) | 1.98 | No | $64.99 / $64.50 | CNHL / Amazon B0B4DBZ9DK | In stock |
| B6-class 80 W AC clone (B0FJY74L21) | 80 | — | 3.17 | No | $37.99 | Amazon | Listed |

Charge time for one HOOVO 8000 at 5.95 A: 8.0 Ah / 5.95 A = 1.34 h (estimate). Real time is
longer because of the CV taper.

Li-ion note: the Gaoneng 40T pack page says "Charge Rate: 1C", which is 8 A, so the C150 is under
its limit.

The ToolkitRC M7AC price of $96.99 quoted in the brief was not seen on any page checked today.
The only live M7AC listing (NewBeeDrone, $74.99) is out of stock and gives 100 W on AC.

## 3. Safety storage and test instruments

| Item | Part / ASIN | Key spec (page) | Fits a 6S pack? | Price | Vendor | Stock |
|---|---|---|---|---:|---|---|
| LiPo bag (cheapest with stated size) | Tenergy B08QCMMGJT | 7 × 9 in | Flat pouch; one 169 × 49 × 63 mm pack (estimate) | $8.99 | Amazon | Listed |
| LiPo bag | Pyrodrone "Lipo-Safe Pouch" | 12 × 8 in, fiberglass lining | Yes | $9.99 | Pyrodrone | In stock |
| LiPo bag | Zeee B07KZQZBN2 | 8.46 × 6.5 × 5.71 in (215 × 165 × 145 mm) | Yes, 169 mm pack | $13.49 | Amazon | Listed (10.8K ratings) |
| LiPo bag | Lumenier LiPo Safe Bag | 6 × 6 × 8 in | Yes, length-wise | $16.99 | RaceDayQuads | In stock |
| LiPo bag | CNHL charge/storage bag | 215 × 165 × 145 mm, 230.5 g | Yes | $19.99 | Pyrodrone | In stock |
| LiPo bag (no size given) | Zeee B0FWBMK87X | — | — | $6.29 | Amazon | Listed |
| Ammo can | Harbor Freight Metal 0.50 Cal, item 63750 | Inside 11-1/8 × 5-1/2 × 6-7/8 in (283 × 140 × 175 mm) | Two 49 mm wide packs side by side = 98 mm < 140 mm ✓ | $19.99 | harborfreight.com | — (page shows no stock) |
| Watt meter (cheapest ≥ 60 A / ≥ 30 V) | B0F13JWDFV, "150A … DC 60V" | 150 A, 60 V (seller claim) | — | $12.99 | Amazon | Listed (9 ratings) |
| Watt meter (most-reviewed) | B06XPVKY13 | 0–150 A, 4.8–60 V, 12 AWG | — | $14.99 | Amazon (Sage Direct Store) | "Only 16 left" |
| Watt meter (branded) | ToolkitRC WM150 | 150 A, **1–50 V**, PWM servo tester | — | $51.99 | Pyrodrone | In stock |
| IR thermometer (cheapest) | B0BN317X6Z | −50 to 500 °C | — | $8.98 | Amazon | Listed (6.5K ratings) |
| IR thermometer | Etekcity Lasergrip 774, B0B71HFH9K | 12:1 D:S | — | $18.99 | Amazon (ships and sold by Amazon) | In stock |

Ammo-can caution: a gasketed can is meant to seal. Teams commonly remove or slit the gasket so a
venting cell cannot pressurize the can. This is general practice and not from the HF page;
confirm it against the university EH&S LiPo guidance (—).

## 4. DIY thrust stand

| Item | Part | Price | Vendor | Stock |
|---|---|---:|---|---|
| Load cell 10 kg straight bar (TAL220) | SparkFun SEN-13329 | $12.95 | sparkfun.com | In stock |
| HX711 amplifier | SparkFun SEN-13879 | $4.95 | sparkfun.com | In stock |
| 20 kg load cell + HX711 kit | Geekstory B079FQNJJH | $8.98 | Amazon | Listed (64 ratings) |
| 20 kg load cell + HX711 kit | NOYITO B07BGS58TL | $6.99 | Amazon | Listed (13 ratings, 3.8★) |
| Arduino Nano clone (CH340G) + cable | AYWHP B0DFGR288F | $8.99 | Amazon | Listed (322 ratings) |
| Nano clone 3-pack | B07G99NNXL | $13.99 | Amazon | Listed (2.2K ratings) |

SparkFun shipping: — (not checked).

## Kit totals (before tax)

| Kit | Items | Total |
|---|---|---:|
| Cheapest safety and test kit | Tenergy bag $8.99 + HF ammo can $19.99 + watt meter B0F13JWDFV $12.99 + IR B0BN317X6Z $8.98 + Geekstory 20 kg / HX711 $8.98 + Nano B0DFGR288F $8.99 | **$68.92** |
| Same kit with SparkFun load cell and amp | swap the $8.98 kit for $12.95 + $4.95 | $77.84 + SparkFun shipping (—) |
| More-reviewed parts | Zeee bag $13.49 + ammo can $19.99 + B06XPVKY13 $14.99 + Etekcity $18.99 + SparkFun $17.90 + Nano $8.99 | $94.35 |
| Energy system, cheapest worst-case-capable | 2× HOOVO 8000 ($199.99) + HTRC C150 ($56.99) + cheapest kit ($68.92) | **$325.90** |
| Energy system, cheapest 140 Wh packs | 2× Ovonic 6500 ($138.99) + HTRC C150 ($56.99) + cheapest kit ($68.92) | $264.90 |

## What the team must measure

- **M1 — Pack sustained current.** Run each pack at 45 A for 3 min on the thrust stand, logging
  with the watt meter and IR thermometer. **Fails** if any cell sags below 3.5 V under load, or the
  pack surface goes above 60 °C (estimate threshold). Either would mean the ≥ 60 A requirement is
  not real.
- **M2 — Usable Wh.** Discharge a full pack through the mission profile (3 min at the measured
  hover W, then 10 min at cruise W) with the watt meter. **Fails** the mission if the logged Wh
  exceeds 80 % of the computed nominal: above 115 Wh for the 144 Wh packs, above 142 Wh for the
  8000 mAh packs.
- **M3 — Charger AC output.** Charge a 6S pack on AC with the watt meter on the output. **Fails**
  the ≥ 5 A requirement if the C150 delivers under 5.0 A at 24–25 V. Its page gives 150 W but no
  separate AC limit.
- **M4 — Pack mass.** Weigh each pack on a kitchen scale. Recompute Wh/kg. Flag any pack more than
  5 % over the page weight, which matters for the Amazon car packs.
- **M5 — Watt-meter accuracy.** Check the meter against a clamp meter or a known resistive load at
  20–40 A. **Reject** it if the error exceeds 3 %.

## Sources (all checked 2026-10-13)

- CNHL catalog (product JSON, prices, stock by warehouse, specs):
  https://chinahobbyline.com/products.json; product pages
  `/products/cnhl-10000mah-21-6v-6s-21700-li-ion-battery-xt60`,
  `/products/cnhl-racing-series-9500mah-22-2v-6s-90c-lipo-battery-with-xt90-plug`,
  `/products/cnhl-8000mah-22-2v-6s-30c-lipo-battery-with-xt90-plug`,
  `/products/isdt-608ac-smart-balance-charger`, `/products/isdt-d2-mark-ii-smart-balance-charger`,
  `/products/isdt-k2-air-6s-lipo-charger`. Shipping: https://chinahobbyline.com/pages/shipping-policy
- Zeee: https://zeeebattery.com/products/zeee-6s-lipo-battery-9000mah-22-2v-100c-ec5,
  https://zeeebattery.com/products/zeee-6s-lipo-battery-10000mah-22-2v-120c-ec5;
  shipping https://zeeebattery.com/pages/shipping-policy
- Ovonic Roam spec (777 g / 1023 g): https://www.ovonicshop.com/products/ovonic-roam-series-6s-lipo-battery-6500mah-6s1p-150c-22-2v-long-range-lipo-battery-with-xt90-s-anti-spark-plug-for-6-10-inch-long-range-cenilifter-multirotor-x-class
- RaceDayQuads: https://www.racedayquads.com/products/ + `lumenier-nav-10000mah-6s-21700-lithium-ion-battery-xt60`,
  `lumenier-nav-12000mah-6s-21700-lithium-ion-battery-xt90`,
  `auline-18650-v45-6s2p-6000mah-22-2v-90a-li-ion-battery-xt60`,
  `tattu-g-tech-9000mah-6s-25c-lipo-battery-xt60`, `lumenier-10000mah-6s-25c-lipo-battery-xt90`,
  `molicel-p50b-21700-5000mah-60a-3-7v-li-ion-battery-2pcs`,
  `hota-h6-pro-700w-26a-1-6s-ac-dc-smart-charger-black`,
  `toolkitrc-m6ac-300w-15a-1-6s-ac-charger-xt60`, `lumenier-fireproof-lipo-bag`,
  `upgrade-energy-red-v4-10000mah-6s2p-amprius-li-ion-battery-xt60`;
  policy https://www.racedayquads.com/pages/shipping-policy-1
- Pyrodrone: https://pyrodrone.com/products/ + `iflight-fullsend-e-6s-8000mah-22-2v-6s1p-lipo-battery-xt60`,
  `gaoneng-gnb-8000mah-22-2v-6s-10c-6s2p-made-with-samsung-21700-40t-long-range-cinelifter-lipo-battery-xt60`,
  `htrc-lipo-charger-1-6s-ac-dc-c150-for-nicd-li-ion-life-nimh-lihv-pb-smart-battery`,
  `htrc-t400-pro-lipo-charger-dual-dc-400w-ac-200w-12a-2-discharger-for-lipo-lihv-life-lilon-nicd-nimh-pb`,
  `hota-h6-pro-ac-dc-charger-black`, `toolkitrc-wm150-advanced-watt-power-meter`, `lipo-safe-pouch`,
  `cnhl-lipo-charge-and-storage-battery-bag`; policy https://pyrodrone.com/pages/shipping-policy
- NewBeeDrone: https://newbeedrone.com/products/toolkitrc-m7ac-100w-ac-300w-dc-15a-2-6s-multi-function-ac-smart-balance-charger,
  https://newbeedrone.com/products/newbeedrone-nitro-nectar-gold-50xg-21700-10000mah-6s2p-high-rate-battery,
  https://newbeedrone.com/products/isdt-k2-air-dual-channel-smart-charger
- Gens Ace / Tattu: https://genstattu.com/tattu-30c-uav-battery.html, https://genstattu.com/battery-for-long-range-drone
- Amazon (https://www.amazon.com/dp/<ASIN>): B09CTRKLM4, B0D3HQLGDG, B0D3HS6FMC, B093S2164J, B099KQ4JJ8,
  B0BHQX8XQX, B09YM8JK57, B0DNLXTN7M, B0H4QLJYHY, B0H6J7DZL2, B06XPVKY13, B0B71HFH9K; search-result
  prices for B08QCMMGJT, B07KZQZBN2, B0FWBMK87X, B0F13JWDFV, B0BN317X6Z, B079FQNJJH, B07BGS58TL,
  B0DFGR288F, B07G99NNXL, B07YD3JNTZ, B0GS5FRW5F, B0D4MC4GPC, B092J5LTBW, B0B4DBZ9DK, B0FJY74L21
- Harbor Freight ammo can: https://www.harborfreight.com/50-caliber-metal-ammo-can-63750.html
- SparkFun: https://www.sparkfun.com/load-cell-10kg-straight-bar-tal220.html,
  https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html
- Flywoo P45B 6S2P (sold out): https://www.unmannedtechshop.co.uk/de/products/flywoo-explorer-molicell-p45b-21700-6s2p-9000mah-lionpack-battery
