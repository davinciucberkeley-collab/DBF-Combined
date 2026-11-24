# Budget lift propulsion: cheapest credible motor + ESC + prop

**Date checked: 2026-10-13.** I read every price, spec and stock flag below on a live page that day, through WebFetch or the in-app browser. Amazon and GetFPV block WebFetch with 403/503, so I read them in the browser. "—" means the value was not on the page. "est." means I derived it and it is not published.

**Scope.** Lift rotors for a quadplane at MTOW 5–7.5 kg. The baseline being replaced is the Hobbywing X6 SE at $134.98 per lift station (figure from the brief).

**Targets (from the brief).**
- 4-lift: max static thrust ≥ 3.0–4.5 kgf per motor; hover 1.25–1.9 kg per motor.
- 8-lift / X8: max static thrust ≥ 1.5–2.5 kgf per motor; hover 0.65–0.95 kg per motor.

**Station cost formula:** station $ = motor + ESC + 1 prop. It is pre-tax and excludes shipping. A set total is N × station $. With the 10.25 % tax: set × 1.1025.

**ESC rule used.** If the motor's published max current is ≤ 25 A, the station uses the LANRC 35A ($7.13 each). If it is > 25 A, or unknown, the station uses the SoloGood 45A ($10.00 each). That keeps at least about 1.2× headroom.

---

## Verdict

| Layout | Cheapest credible set | Station $ | Set $ (pre-tax) | Set $ incl. 10.25 % tax | Max thrust / motor | Hover point (published) |
|---|---|---|---|---|---|---|
| 4-lift, 6S | SunnySky X3515S 400KV + SoloGood 45A + APC 16x5.5MR | 63.72 | 254.88 | 281.01 | 3360 gf (16x6, 22.2 V) | 1500 g @ 9.0 A, 199.8 W, **7.51 g/W** |
| 8-lift, 4S | SunnySky X3108S KV900 + SoloGood 45A + APC 11x4.5MR | 38.82 | 310.56 | 342.39 | 1580 gf (APC 11x4.7, 14.8 V) | 750 g @ 7 A, 104 W, **7.2 g/W** |
| 8-lift, 6S (best credible) | SunnySky V3508 KV380 + LANRC 35A + Eolo CN15x5.5 | 59.12 | 472.96 | 521.44 | 1840 gf (22.2 V) / 2150 gf (25 V) | 800 g @ 3.5 A, 78 W, **10.30 g/W** |
| Baseline (brief) | Hobbywing X6 SE | 134.98 | 539.92 (×4) | 595.26 | — | — |

**Reading the verdict.**
- The cheapest credible set overall is **4-lift with the X3515S: $254.88 for 4 stations**. That is 53 % less than 4 × X6 SE (1 − 254.88/539.92).
- **Limit of the X3515S set.** At 3.36 kgf per motor it meets T/W ≥ 2.0 only up to MTOW 6.7 kg (4 × 3.36 / 2.0, est.). At 7.5 kg its T/W is 1.79.
- **8-lift costs more than 4-lift at these sizes.** The ESC and prop cost per station does not shrink much, and you buy twice as many.
- The **V3508 8-lift** has the best hover efficiency: about 568 W total hover at 6 kg (est. = 8 × ~71 W, interpolated between the 700 g and 800 g rows), against 799 W for 4 × X3515S (4 × 199.8 W). It costs $218 more (472.96 − 254.88).
- **Limit of the X3108S set.** It is 4S, so the rest of the system would also go 4S. Its 1.58 kgf max gives T/W 2.0 only up to MTOW 6.3 kg (8 × 1.58 / 2.0, est.).

---

## Table A — 4-lift (target ≥ 3.0–4.5 kgf max, hover 1.25–1.9 kg), sorted by station cost

| # | Motor (exact part) | KV | Weight g | Cells | Prop (per table) | Max thrust | Mid-table point (g / A / W) | Motor $ | ESC $ | Prop $ | **Station $** | In stock | Ships from | Shipping | Credible? | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 | FFTY 4214 380KV (Amazon B0GFVY568B) | 380 | 212.5 (item weight) | ≤ 33 V max (≈ 7S) | 12–14" (listing) | 4.7 kg (title claim only) | — (no table in listing or images) | 32.99 | 10.00 | 8.73 | 51.72 | In Stock | Amazon, seller FFTY-US | Free over $35 shipped by Amazon | **No**: no thrust table | [amazon.com/dp/B0GFVY568B](https://www.amazon.com/dp/B0GFVY568B) |
| A1 | Tarot 4114 320KV TL100B08-01 | 320 | 148 | 6S | Tarot 1555–1655 | ~2.65 kg (vendor text) | 1.3–1.5 kg @ 50 % (A, W —) | 41.99 | 10.00 | 7.36 | 59.35 | In Stock | US (Ohio) | — | **Fails 4-lift** (< 3.0 kgf) | [readymaderc 85596](https://www.readymaderc.com/products/details/85596-tarot-brushless-motor-high-efficiency-6s-4114-320kv); thrust text: [flyingtech.co.uk](https://www.flyingtech.co.uk/product/tarot-4114-320kv-6s-multirotor-brushless-motor-tl100b08-01/) |
| **A2** | **SunnySky XS X3515S KV400** | 400 | 170 | 6S | 16x6 (also 14x4.7, 15x5.5) | **3360 gf @ 28.6 A, 634.9 W (22.2 V)**; 3600 gf @ 30.1 A (25 V) | 1500 / 9.0 / 199.8 (7.51 g/W) @ 22.2 V | 44.99 | 10.00 | 8.73 (APC 16x5.5MR) | **63.72** | Add to Cart | US (SunnySky USA, Columbus OH) | — | Yes | [sunnyskyusa.com x3515s](https://sunnyskyusa.com/collections/multirotor-motors/products/x3515s) |
| A3 | SunnySky XS X4110S KV400 | 400 | 165 | 6S | 17x5.8 (also 15x5.5, 16x6, 18x6.1) | 3130 gf @ 27.7 A, 615 W (22.2 V); 3600 gf @ 33.3 A (25 V) | 1500 / 8.1 / 180 (8.34 g/W) @ 22.2 V | 46.99 | 10.00 | 9.30 (JeeFly 1755, half of $18.60 pair) | 66.29 | Add to Cart (inventory 60) | US (SunnySky USA) | — | Yes (see table flags) | [sunnyskyusa.com x4110s](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-x4110s-motors) |
| ref | Hobbywing XRotor X6 SE (integrated) | 280 | — | 6S | MFP 22x7 | — | — | — | — | — | 134.98 (brief) | — | — | — | Baseline | brief; [lift-propulsion.md](lift-propulsion.md) |

Also checked; not cheaper, or no data:
- **iFlight XING X4214 400KV.** $96.16, "On Demand", RobotShop US; no thrust table found ([robotshop](https://www.robotshop.com/products/iflight-xing-4214-x-class-motor-400kv)).
- **SunnySky X4112S 400KV.** $52.99 at SunnySky USA, $67.99 on Amazon.
- **SunnySky V4006.** $55.20.
- **T-Motor MN4006 KV380.** $149.9 per 2-pack ([store.tmotor.com](https://store.tmotor.com/categorys/uav-mult-motor-antigravity-type)).
- **T-Motor MN4110.** From $86.99.
- **Emax MT4114 340KV.** EU sellers only (€49.90–59.95), or sold out; 2020 g max claim; no table.
- **Generic 5010 360KV on Amazon** (e.g. GoolRC B0C2YRNX1Z, $27.98). Spec sheet only, no thrust table, so not credible.

## Table B — 8-lift / coaxial X8 (target ≥ 1.5–2.5 kgf max, hover 0.65–0.95 kg), sorted by station cost

| # | Motor (exact part) | KV | Weight g | Cells | Prop (per table) | Max thrust | Mid-table point (g / A / W) | Motor $ | ESC $ | Prop $ | **Station $** | In stock | Ships from | Shipping | Credible? | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | SunnySky V2216 KV800 | 800 | 68 (+13 accessories) | 3–4S | ZX 11x4.7 CF / APC 10x3.8 | ~1250 gf (14.8 V; 100 % row partly cut off in the image) | 650 / 5.4 / 80 (8.1 g/W), APC 10x3.8 @ 65 %, 14.8 V | 21.99 | 7.13 | 3.83 | 32.95 | Available (inventory 60) | US (SunnySky USA) | — | **Fails** (< 1.5 kgf) | [sunnyskyusa.com v2216](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-v2216-motors); [data image](https://cdn.shopify.com/s/files/1/2024/0305/files/WeChatImage_20230918141609.png?v=1695061136) |
| **B1** | **SunnySky XS X3108S KV900** | 900 | 81 | 3–4S | APC 11x4.7 | **1580 gf @ 30 A, 447 W (14.8 V)** | 750 / 7 / 104 (7.2 g/W); 870 / 9 / 133 (6.5 g/W) | 24.99 | 10.00 | 3.83 (APC 11x4.5MR) | **38.82** | Available (inventory 60) | US (SunnySky USA) | — | Yes, but 4S only | [sunnyskyusa.com x3108s](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-x3108s-motors); [data 3](https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg) |
| B2 | FEICHAO 4108 380KV (Amazon B08R79J6CH) | 380 | 113 | 3–6S | 15x5.5 CF | 2080 g @ 17.2 A, 381.8 W (22.2 V) | Only full-throttle rows, one per prop/voltage. Lower-voltage point: 1170 / 9.6 / 142.1 (15x5.5 @ 14.8 V) | 29.89 | 7.13 | 7.36 (APC 15x5.5MR) | 44.38 | In stock ("ships within 4 to 5 days") | Seller "Trust-Worthy" (origin —; delivery Oct 29–Nov 9 suggests CN) | Free (shown) | **Weak**: WOT-only table, generic clone | [amazon.com/dp/B08R79J6CH](https://www.amazon.com/dp/B08R79J6CH); table image [71GdKpgIq0L](https://m.media-amazon.com/images/I/71GdKpgIq0L._SL1100_.jpg) |
| **B3** | **SunnySky V3508 KV380** (Kv row reads 350) | 350/380 | 97 | 4–6S | Eolo CN15x5.5 | **1840 gf @ 13.4 A, 297 W (22.2 V)**; 2150 gf @ 15.8 A (25 V) | 800 / 3.5 / 78 (10.30 g/W); 900 / 4.3 / 95 (9.43 g/W) @ 22.2 V | 42.99 | 7.13 | 9.00 (Eolo CN1555, half of $17.99 pair) | **59.12** | Add to Cart | US (SunnySky USA) | — | Yes | [sunnyskyusa.com v3508](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-v3508-motor) |
| B4 | Tarot 4114 320KV TL100B08-01 | 320 | 148 | 6S | Tarot 1555–1655 | ~2.65 kg (vendor text) | 1.3–1.5 kg @ 50 % (A, W —) | 41.99 | 10.00 | 7.36 | 59.35 | In Stock | US (Ohio) | — | Partial: no table; oversized for 8-lift | as A1 |
| B5 | T-Motor MN2806 KV400 | 400 | 46 | 4–6S | T-Motor P13x4.4 | 1068 g @ 7.10 A, 163.5 W (100 %) | 729 / 3.82 / 88.4 @ 75 % (8.25 g/W) | 46.90 | 7.13 | — | — | — | CN (free intl. express ≥ $200) | — | **Fails** (< 1.5 kgf) | [store.tmotor.com mn2806](https://store.tmotor.com/product/mn2806-motor-antigravity-type.html) |

Also seen on Amazon, without checking their tables:
- DYS X3115 900KV 4-pack, $74.99.
- Flash Hobby D4215 650KV, $30.99: 2290 g on 6S with APC 1238 per [flyingtech](https://www.flyingtech.co.uk/product/dys-d4215-21-650kv-multirotor-brushless-disc-motor/); a 12" prop at about 39 A max gives poor hover g/W.

These are FPV-class motors on 9–12" props, with poor hover efficiency, so I did not pursue them.

---

## ESCs (all BLHeli_S unless noted; none has prop-position stop)

| Part | Rating / cells | Pack | Price | $/ESC | In stock | Seller / ships | Shipping | Source |
|---|---|---|---|---|---|---|---|---|
| LANRC BLHeli_S 35A (RGB LED) | 35 A, 2–6S, DShot150/300/600 | 4 pcs | $28.50 | **7.13** | In Stock | Sparkhobby (delivery Oct 23, likely CN) | $1.50 | [amazon.com/dp/B0D2HQPNG9](https://www.amazon.com/dp/B0D2HQPNG9) |
| SoloGood 45A BLHeli_S | 45 A, 2–6S, DShot | 4 pcs | $39.99 | **10.00** | Only 8 left | SoloGood, Prime / FBA (US) | Free (orders shipped by Amazon) | [amazon.com/dp/B0DJQVGSBC](https://www.amazon.com/dp/B0DJQVGSBC) |
| Readytosky 35A BLHeli_S | 35 A, 2–6S | 4 pcs | $46.49 | 11.62 | In Stock | SkywalkerRC, Prime-eligible | Free | [amazon.com/dp/B0C77JSR14](https://www.amazon.com/dp/B0C77JSR14) |
| Readytosky 45A BLHeli_S (single) | 45 A, 2–6S | — (search result) | $16.99 | 16.99 | — | — | — | Amazon search, B0FDY4Q5YG |
| DYS Aria 35A **BLHeli_32**, current sensor | 35 A, 3–6S | — (search result) | $32.99 | 32.99 | — | — | — | Amazon search, B0GKVPLX3T |

ESC continuous vs burst ratings, weights and heat-sinking are not stated on these listings ("—").

## Props

| Part | Size | Pack | Price | $/prop | Ships | Source |
|---|---|---|---|---|---|---|
| APC 11x4.5MR (LP11045MR) | 11x4.5 | single | $3.83 | 3.83 | US (APC); stock — ; shipping — | [apcprop.com 11x4-5mr](https://www.apcprop.com/product/11x4-5mr/) |
| APC 15x5.5MR / MRP (LP15055MR/MRP) | 15x5.5 | single | $7.36 | 7.36 | US (APC); stock — | [15x5-5mr](https://www.apcprop.com/product/15x5-5mr/), [15x5-5mrp](https://www.apcprop.com/product/15x5-5mrp/) |
| APC 16x5.5MR (LP16055MR) | 16x5.5 | single | $8.73 | 8.73 | US (APC); needs LPAR06E adapter ring (not included) | [16x5-5mr](https://www.apcprop.com/product/16x5-5mr/) |
| SunnySky Eolo CN 15x5.5 carbon-nylon | 15x5.5 | CW+CCW pair | $17.99 | 9.00 | US (Columbus OH); inventory 60 | [eolo-cn15-5-5-prop](https://sunnyskyusa.com/products/eolo-cn15-5-5-prop) |
| SunnySky Eolo CN 11x4.5 carbon-nylon | 11x4.5 | pair | $11.99 | 6.00 | US | [eolo-cn11-4-5-prop](https://sunnyskyusa.com/products/eolo-cn11-4-5-prop) |
| JeeFly 3K carbon 1555 / 1655 / 1755 / 1855 | 15–18 x 5.5 | pair | $16.98 / $17.90 / $18.60 / $19.99 | 8.49 / 8.95 / 9.30 / 10.00 | JeeFly office store, $4.99 delivery, Oct 23–Nov 3 (likely CN) | [amazon.com/dp/B0FJ21V736](https://www.amazon.com/dp/B0FJ21V736) |
| **Folding:** Eolo foldable CN 16x6.0 | 16x6 | pair | $46.99 | 23.50 | US | [sunnyskyusa search](https://sunnyskyusa.com/search?q=eolo+cn) |
| **Folding:** Eolo foldable CN 17x6.2 | 17x6.2 | pair | $49.99 | 25.00 | US | same |
| **Folding:** KingVal 1552 CF folding | 15x5.2 | "CW/CCW" (qty —) | $18.88 | — | KingVal RC store, Amazon-fulfilled; only 9 left | [amazon.com/dp/B096K9Y5JZ](https://www.amazon.com/dp/B096K9Y5JZ) |

Cheap folding props cost about $14–16 more per station than fixed props (e.g. Eolo 16x6 folding at $23.50 against APC 16x5.5MR at $8.73).

---

## Thrust-table excerpts (top 3 per layout)

### 4-lift

**A2 SunnySky X3515S KV400, 16x6, 22.2 V** ([source](https://sunnyskyusa.com/collections/multirotor-motors/products/x3515s))

| Thrust gf | A | W | g/W |
|---|---|---|---|
| 1250 | 6.9 | 153.18 | 8.16 |
| 1500 | 9.0 | 199.8 | 7.51 |
| 2000 | 13.2 | 293.04 | 6.83 |
| 3360 (max) | 28.6 | 634.92 | 5.29 |

**A3 SunnySky X4110S KV400, 17x5.8, 22.2 V** ([source](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-x4110s-motors))

| Thrust gf | A | W | g/W |
|---|---|---|---|
| 1250 | 6.1 | 135 | 9.23 |
| 1500 | 8.1 | 180 | 8.34 |
| 2000 | 13.1 | 291 | 6.88 |
| 3130 (max) | 27.7 | 615 | 5.09 |

**A1 Tarot 4114 320KV** ([source](https://www.flyingtech.co.uk/product/tarot-4114-320kv-6s-multirotor-brushless-motor-tl100b08-01/)): vendor text only. It quotes 1.3–1.5 kg at 50 % throttle on 1555–1655 props and a max of about 2.65 kg; no A or W. Tarot's datasheet is a JPG I did not read. It fails the 3.0 kgf floor.

### 8-lift

**B3 SunnySky V3508 KV380, Eolo CN15x5.5, 22.2 V** ([source](https://sunnyskyusa.com/collections/multirotor-motors/products/sunnysky-v3508-motor))

| Thrust gf | A | W | g/W |
|---|---|---|---|
| 700 | 2.9 | 64 | 10.87 |
| 800 | 3.5 | 78 | 10.30 |
| 900 | 4.3 | 95 | 9.43 |
| 1840 (max) | 13.4 | 297 | 6.19 |

**B1 SunnySky X3108S KV900, APC 11x4.7, 14.8 V** ([data image 3](https://cdn.shopify.com/s/files/1/2024/0305/files/SunnySky_X3108S_KV900_Data_3.jpg))

| Thrust g | A | W | g/W |
|---|---|---|---|
| 690 | 6 | 89 | 7.8 |
| 750 | 7 | 104 | 7.2 |
| 870 | 9 | 133 | 6.5 |
| 1580 (max) | 30 | 447 | 3.5 |

**B2 FEICHAO 4108 380KV** ([table image](https://m.media-amazon.com/images/I/71GdKpgIq0L._SL1100_.jpg)): full-throttle rows only.

| V | Prop | A | Pull g | W |
|---|---|---|---|---|
| 14.8 | 15x5.5 CF | 9.6 | 1170 | 142.1 |
| 22.2 | 12x3.8 APC | 13 | 1660 | 288.6 |
| 22.2 | 13x6.5 CF | 15.4 | 1690 | 341.9 |
| 22.2 | 15x5.5 CF | 17.2 | 2080 | 381.8 |

---

## Caveats and flags

1. **Possible errors in published tables.**
   - X4110S KV340 table, 18x6.1 rows: W ≠ V × A. For example, 1.6 A × 22.2 V = 35.5 W, but the table lists 80 W. Those rows look wrong.
   - X4110S KV400 table, 16x6 @ 25 V: the row "2300 gf / 26 A / 650 W" is out of sequence; the next row is 2600 gf at 19.5 A. It looks like a typo.
   - X3515S: W equals exactly V × A (e.g. 46.62 = 2.1 × 22.2), so power is computed from current, not measured.
   - V3508 table: the header says KV380 but the Kv row reads 350.
   - FEICHAO 4108: full-throttle points only, from a generic seller. The same 4108 sheet appears on many clone listings, so treat it as unverified.
   - FFTY 4214: its 4.7 kg claim has no table behind it.
2. **Prop in the table vs. prop priced.**
   - X3515S was tested on an unbranded "16x6"; I priced the APC 16x5.5MR.
   - X4110S was tested on 17x5.8; I priced the JeeFly 1755 (17x5.5).
   - X3108S was tested on APC 11x4.7; I priced the APC 11x4.5MR.
   - Expect thrust and current to differ by a few percent. Only the V3508 + Eolo CN15x5.5 pairing matches its table exactly.
3. **Mounting.**
   - APC MR props have a 1/4" bore and need LPAR06E adapter rings (not included).
   - The V3508 is a disc-type motor; check its prop hub and bolt pattern against the Eolo prop before buying. Neither page states hub compatibility ("—").
4. **No prop-stop or position lock.** None of these BLHeli_S ESCs can park a 2-blade prop fore-aft in cruise, so expect extra cruise drag from randomly parked blades. Folding props, or the T-Motor V60A from [lift-propulsion.md](lift-propulsion.md), solve this at much higher cost.
5. **BLHeli_S ESC ratings.** These are FPV ESCs and only the "35A/45A" headline rating is listed; continuous ratings are "—". Hover current is ≤ 9 A on every candidate, but full-throttle transients reach 28.6–30 A on X3515S and X3108S, hence the 45A choice there.
6. **4S vs 6S.** The cheapest 8-lift set (X3108S) is 3–4S only. Going 4S changes the battery and pusher selection, and it raises pack current about 1.5× for the same power (6S/4S, est.). It is cheaper per station, but at $310.56 it is still $55.68 more than the 6S 4-lift set ($254.88).
7. **Not included in station $.**
   - Shipping: SunnySky USA, APC and readymaderc shipping costs were not shown ("—").
   - Spares: budget at least one spare prop set and 1–2 spare motors.
   - Pack rounding: ESCs come in 4-packs and Eolo/JeeFly props in pairs, which matches 4 or 8 stations exactly.
8. **Brands not checked.** Turnigy/HobbyKing, Racerstar, BrotherHobby, Mitoot, GEPRC and Readytosky motors were not verified on a live page with a thrust table. Readytosky ESCs were checked. GetFPV's SunnySky X4110S was listed at $42.74 but Out of Stock ([getfpv](https://www.getfpv.com/sunnysky-x4110s-400kv.html)).

## What the team must measure

- **M1 — Static thrust at hover.** Run one station (motor + ESC + the actual prop bought) on a thrust stand or a kitchen scale with a lever arm, at 22.2 V. Measure the current at 1500 g (4-lift) or 750 g (8-lift). If the 4-lift station needs more than 230 W per motor at 1500 g (15 % above the 199.8 W table value), hover endurance falls short of the battery sizing.
- **M2 — Full-throttle current and motor temperature after 30 s.** It fails if current exceeds the ESC rating, or if the case temperature passes 80 °C.
- **M3 — Stopped-prop drag in cruise orientation.** Use a car-top or wind test to decide whether folding props are worth +$14–16 per station.
