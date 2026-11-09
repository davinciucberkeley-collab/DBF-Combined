# Pusher propulsion, flight batteries, charger, servos — parts research

**Date checked: 2026-10-13** (every price, spec and stock flag below was read from the linked page on this date unless marked otherwise).
Scope: the physical lift + cruise VTOL (8–15 kg MTOW, 18–22 m/s cruise, $2,000 total budget).
Conventions: "—" = not on the page. "Est." = estimate computed here, not a vendor figure. Stock: y / n / pre-order / —. Prices exclude shipping and tax.

---

## 0. Sizing basis (computed here)

| Quantity | Formula | Value |
|---|---|---|
| Cruise thrust | T = m·g / (L/D), L/D = 10 (task brief) | 8 kg: 7.85 N (800 gf); 15 kg: 14.7 N (1,500 gf) |
| Static thrust target | task brief | 2.5–4 kgf |
| Pitch speed | V_p = pitch[m] × RPM / 60 | 14×7 @ 8,762 rpm (AT3520 KV550, 100 %): 0.1778 × 8,762 / 60 = **26.0 m/s** |
| Cruise electrical power (est.) | P = T·V / (η_prop·η_motor), η_prop 0.6, η_motor 0.85 (assumed) | 12 N × 20 m/s / 0.51 ≈ **470 W** (est.) |
| Hover battery current (est.) | 4 × 367 W (hover input/motor at 3 kg, `docs/research/lift-propulsion.md` line 115) / 21.6 V | ≈ **68 A** continuous, 6S |

The 26 m/s pitch speed of a 14×7 at full static RPM is only ~1.2× the 22 m/s top cruise. A higher-pitch pusher (14×8.5EP, V_p = 0.2159 × 8,762 / 60 = 31.5 m/s at the same RPM; real loaded RPM will be lower, —) is the safer choice for 18–22 m/s. No vendor thrust table exists for the 14×8.5 on this motor.

---

## 1. Pusher motor, prop, ESC

### 1a. Motors

| Part | KV | Cells | Weight (g) | Max thrust (vendor test) | Low-throttle point (vendor test) | Max current / power | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|---|---|
| **T-Motor AT3520 Long Shaft KV550** (pick) | 550 | 4–6S | 218 (incl. cable) | 4,116 g (APC 14×7, 21.83 V, 100 %) | 50 %: 1,408 g, 8.50 A, 190.7 W, 22.43 V (APC 14×7) | 50 A peak (180 s), 1,100 W (180 s) | $79.99 | — | — (T-Motor store; origin not stated) | https://store.tmotor.com/goods.php?id=794 |
| T-Motor AT3520 Long Shaft KV720 | 720 | 4–5S | 219 | 4,316 g (APC 14×7, 100 %) | 40 %: 1,076 g, 7.55 A, 18.46 V (APC 14×7) | 70 A peak | $79.99 | — | — | https://store.tmotor.com/goods.php?id=794 |
| T-Motor AT4130 Long Shaft KV230 (12S option) | 230 | 12S | 408 | 7,630 g (APC 17×10, 43.62 V, 100 %) | 50 %: 1,744 g, 5.18 A, 229.9 W, 44.36 V (APC 16×8) | 2,500 W (180 s) | $119.99 | — | — | https://store.tmotor.com/product/at4130-long-shaft-fixed-wing-motor.html |
| T-Motor AT4130 Long Shaft KV300 | 300 | 6–12S | 405 | 7,787 g (APC 15×8, 43.14 V, 100 %) | 40 %: 1,431 g, 4.37 A, 193.7 W, 44.32 V (APC 15×8) | 3,200 W (180 s) | $119.99 | — | — | same as above |
| SunnySky X4120 V3 480KV | 480 | 6S (page: "optimized for 6S") | 292 (with wire) | — (no thrust table on page) | — | 97 A / 2,425 W (30 s) | $105.99 | y | US (RMRC) | https://www.readymaderc.com/products/details/86775-sunnysky-x-series-v3-x4120-480kv-brushless-motor |

AT4130 is ~2× the needed thrust and ~190 g heavier than the AT3520; carry it only if the aircraft goes 12S for the lift system.

### 1b. Thrust-table excerpt — top pick (T-Motor AT3520 KV550, APC 14×7, 6S)

Source: https://store.tmotor.com/goods.php?id=794 (checked 2026-10-13). Vendor note: bench data "for reference only"; motor surface 59 °C after 3 min at 100 %.

| Throttle | Voltage (V) | Current (A) | Power (W) | RPM | Thrust (g) | g/W |
|---|---|---|---|---|---|---|
| 40 % | 22.49 | 5.15 | 115.79 | 4,423 | 973 | 8.40 |
| 45 % | 22.46 | 6.71 | 150.66 | 4,888 | 1,169 | 7.76 |
| 50 % | 22.43 | 8.50 | 190.74 | 5,313 | 1,408 | 7.38 |
| 55 % | 22.37 | 11.18 | 250.13 | 5,785 | 1,689 | 6.75 |
| 60 % | 22.34 | 13.70 | 305.98 | 6,192 | 1,954 | 6.39 |
| 70 % | 22.23 | 20.26 | 450.36 | 7,056 | 2,529 | 5.62 |
| 80 % | 22.08 | 29.20 | 644.83 | 7,818 | 3,216 | 4.99 |
| 100 % | 21.83 | 44.28 | 966.63 | 8,762 | 4,116 | 4.26 |

Static 4.1 kgf meets the 2.5–4 kgf target. The 800–1,500 gf cruise thrust is in the 40–55 % static band, but static thrust overstates in-flight thrust at 20 m/s (see pitch-speed note in §0).

### 1c. Pusher props (APC electric pusher "EP", reverse rotation)

| Part no. | Size | Weight | Price | Stock | URL |
|---|---|---|---|---|---|
| LP14085EP (pick) | 14×8.5 EP | 1.31 oz (37 g) | $6.79 | — | https://www.apcprop.com/product/14x8-5ep/ |
| LP14070EP | 14×7 EP | 1.20 oz (34 g) | $6.79 | — | https://www.apcprop.com/product/14x7ep/ |
| LP13080EP | 13×8 EP | 1.09 oz (31 g) | $5.73 | — | https://www.apcprop.com/product/13x8ep/ |

(oz → g: × 28.35.) Vendor thrust tables use tractor APC props; pusher EP versions are the mirror geometry.

### 1d. ESCs

| Part | Cells | Continuous / burst | BEC | Weight | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|
| **Hobbywing Skywalker V2 60A** (pick, 6S) | 3–7S | 60 A / 80 A | 5 V / 7 A | 68 g (page also shows "82", unitless) | $41.99 | y (page also says pre-order, ships 0–1 days) | US (Florida) | https://wrekd.com/products/hobbywing-skywalker-v2-3-7-wing-60a-esc |
| T-Motor AT75A | 2–6S | — / 95 A peak | 5 V / 5 A | 82 g | $35.99 | — | — | https://www.ligpower.com/product/at-75a-6s-fixed-wing-esc.html |
| T-Motor AT115A (12S option) | 6–14S | 115 A / 120 A (<10 s) | switch-mode, 5.2/6/7.4 V selectable | 182 g | $137.99 | n (sold out) | US (RDQ) | https://racedayquads.com/products/t-motor-at115a-6-14s-vtol-fixed-wing-single-esc |

AT3520 KV550 draws 44.3 A at 100 % on a 14×7 (table above), so a 60 A continuous ESC leaves ~35 % margin. The 14×8.5 will draw more; current is not published (—). Measure it on a bench before flight.

---

## 2. Flight batteries

Wh = V_nom × Ah (V_nom is the voltage printed on the vendor page). Wh/kg = Wh / weight (kg, from page). Continuous A = C × Ah for LiPo; Li-ion = vendor "max continuous discharge".

| Part no. / name | Chem. | Config | mAh | V_nom | Wh (computed) | Weight g (page) | Wh/kg (computed) | Cont. rating | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **WREKD / Nexus 6S3P Molicel P50B** (pick, Li-ion) | Li-ion 21700 | 6S3P | 15,000 | 21.6 | 21.6 × 15 = **324** | 1,350 (spec; product data 1,551) | 324/1.350 = **240** (209 at 1,551 g) | 180 A; charge 15 A max | $378.00 | pre-order, 1–3 wk | US (Ohio; made in Nevada) | https://wrekd.com/products/6s3p-21-6v-molicel-p50b-15000mah-li-ion-battery-pack |
| WREKD 6S2P Molicel P50B | Li-ion 21700 | 6S2P | 10,000 | 21.6 | 21.6 × 10 = 216 | 900 (spec; data 1,034) | 240 (209) | 120 A; charge 10 A | $252.00 | pre-order, 1–3 wk | US (Ohio) | https://wrekd.com/products/6s2p-21-6v-molicel-p50b-10000mah-li-ion-battery-pack |
| WREKD 6S4P Molicel P50B | Li-ion 21700 | 6S4P | 20,000 | 21.6 | 21.6 × 20 = 432 | 1,800 (spec; data 2,068) | 240 (209) | 240 A; charge 20 A | $504.00 | pre-order, 1–3 wk | US (Ohio) | https://wrekd.com/products/6s4p-21-6v-molicel-p50b-20000mah-li-ion-battery-pack |
| WREKD 6S3P Molicel P42A | Li-ion 21700 | 6S3P | 12,600 | 21.6 | 272.16 (page) | 1,350 (spec; data 1,483) | 202 (184) | 135 A; charge 12.6 A | $306.00 | pre-order, 1–3 wk | US (Ohio) | https://wrekd.com/products/6s3p-21-6v-molicel-p42a-12600mah-li-ion-battery-pack |
| WREKD 6S4P Molicel P42A | Li-ion 21700 | 6S4P | 16,800 | 21.6 | 362.88 (page) | 1,800 (spec; data 1,982) | 202 (183) | 180 A; charge 16.8 A | $408.00 | pre-order, 1–3 wk | US (Ohio) | https://wrekd.com/products/6s4p-21-6v-molicel-p42a-16800mah-li-ion-battery-pack |
| Flywoo Explorer P45B 6S2P | Li-ion 21700 | 6S2P | 9,000 | 22.2 (page) | 22.2 × 9 = 199.8 | 860.7 | 232 | 45 A | £63.19 | n (sold out / backorder) | UK retailer | https://www.unmannedtechshop.co.uk/fr/products/flywoo-explorer-molicell-p45b-21700-6s2p-9000mah-lionpack-battery |
| Tattu TA-30C-12000-6S1P-EC5 | LiPo | 6S1P | 12,000 | 22.2 | 22.2 × 12 = 266.4 | 1,532 | 174 | 30C = 360 A | $268.99 | y | US (RMRC) | https://readymaderc.com/products/details/tattu-6s-30c-12000mah-ec5 |
| **Tattu TA-30C-16000-6S1P-XT90** (pick, LiPo) | LiPo | 6S1P | 16,000 | 22.2 | 22.2 × 16 = **355.2** | 1,988 | **179** | 30C = 480 A (60C burst) | $335.99 | y (<20) | US (FedEx/UPS) | https://www.genstattu.com/ta-30c-16000-6s1p-xt90.html |
| Tattu Plus TA-P2-15C-16000-6S1P-XT90S (smart) | LiPo | 6S1P | 16,000 | 22.2 | 355.2 | 1,932 | 184 | 15C = 240 A (30C burst) | $360.99 | y (20–100) | US | https://genstattu.com/tattu-plus-16000mah-6s-15c-22-2v-lipo-battery-pack-with-xt90s/ |
| Tattu Plus TA-P2-25C-22000-6S1P-XT90 (smart) | LiPo | 6S1P | 22,000 | 22.2 | 22.2 × 22 = 488.4 | 2,650 | 184 | 25C = 550 A (50C burst) | $486.99 | y (20–100) | US (Livermore, CA service) | https://genstattu.com/tattu-plus-25c-22000mah-6s1p-xt90-smart-lipo-battery.html |
| Amprius SA112 6S1P (Dan-Tech TN6S1P-SA112) | Li-ion (Si anode) | 6S1P | 6,500 | 20.8 | 135 (page) | ~500 | 270 | 13 A (2C) | — (samples / quote only) | — | — (Berlin company) | https://www.danenergy.com/catalog/lithium-ion-battery-packs/premium-high-density-amprius-sa112-li-ion-battery-6500mah-20-8v-13a-max-tn6s1p-sa112 |

**12S:** no single 12S pack was priced. Use 2 identical 6S packs in series (for example 2 × WREKD 6S3P P50B = 648 Wh, 2,700 g, $756), which is about 40 % of the budget for one flight set.

Notes:
- **Current check:** an estimated 68 A hover draw (§0) is within the 120–240 A rating of every WREKD pack and all LiPos. The Flywoo 45 A and Amprius 13 A packs **fail** for lift and are listed for energy-density reference only.
- **Li-ion vs LiPo:** at the same 15–16 Ah, the 6S3P P50B pack is about 640 g lighter than the Tattu 16 Ah 30C (1,350 g vs 1,988 g), stores 31 Wh less (324 vs 355.2 Wh) and costs $42 more. Li-ion voltage sags more under the hover burst, and that sag is not measured (—).
- The WREKD weights disagree between the spec list and the product data, by about 10–15 %. Weigh the pack on delivery.
- Tattu Plus "smart" packs charge through a MOLEX-436450-9P port, not a standard JST-XH balance lead. Check that the charger works with it before buying (—).

---

## 3. Charger and power supply

Requirement: a 6S pack at ≥ 10 A needs 25.2 V × 10 A = **252 W**. A 16 Ah pack at 1C (16 A) needs 403 W.

| Part | Channels | Max current | Power | Input | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|
| **HOTA D6 Pro** (pick) | 2 | 15 A/ch | DC 325 W/ch (650 W total); AC 200 W (shared) | AC 100–240 V / DC 6.5–30 V | $149.99 | y | US (RDQ) | https://racedayquads.com/products/hota-d6-pro-325w-15a-1-6s-dual-channel-ac-dc-smart-charger-w-wireless-charging-xt60 |
| **Pyrodrone Power Supply v2** (pick PSU) | — | 16.7 A | 400 W, 24 V | AC | $63.99 | y | US | https://pyrodrone.com/collections/power-supply/products/pyrodrone-power-supply-v2-400w-16-7a-24v-updated-plug-and-play-most-chargers |
| ToolkitRC M7AC | 1 | 15 A | 300 W (AC power not on listing) | AC/DC | $96.99 | y | US (Pyrodrone) | https://pyrodrone.com/collections/chargers-1/brand_toolkitrc |
| ToolkitRC M8S | 1 | 18 A | 400 W, DC only (7–30 V) | DC (PSU needed) | $49.98 | n (sold out) | — (HK company) | https://www.worldronemarket.com/product/toolkitrc-m8s-400w-18a-charger/ |
| ToolkitRC M7 | 1 | 10 A | 200 W, DC | DC | $39.99 | y | US (Pyrodrone) | https://pyrodrone.com/collections/chargers-1/brand_toolkitrc |
| ISDT SP2425 PSU | — | 25 A | 600 W, 24 V | AC | $176.99 (Pyrodrone, y); $179.99 (RDQ, n) | y | US | https://pyrodrone.com/collections/power-supply |
| ToolkitRC ADP-450 PSU | — | 19 A | 450 W, 24 V | AC | $127.99 | y | US | https://pyrodrone.com/collections/power-supply |

- The D6 Pro running on AC alone (200 W shared) delivers only 200 / 25.2 = **7.9 A**, which fails the ≥ 10 A requirement. With the 400 W, 24 V PSU it charges one 6S pack at about 15 A (378 W), or two packs at about 7.9 A each (400 W / 2 / 25.2 V).
- The ToolkitRC M7 (200 W) also tops out at 7.9 A on 6S, which fails the ≥ 10 A requirement.
- Pick total: $149.99 + $63.99 = **$213.98**.

---

## 4. Control-surface servos

Torque is stall torque at the stated voltage. Both the Skywalker and AT75A BECs output **5 V**, so an HV servo there runs below its rated torque. Either use a separate 7.4–8.4 V BEC (part not priced, —) or size from the 4.8–6 V figures.

| Part | Torque | Speed (s/60°) | Weight | Gears | Voltage | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|---|
| **Hitec D645MW** (pick, budget) | 8.3–12.9 kg·cm (range; per-voltage not on RMRC page) | 0.28–0.17 | 57 g | metal | 4.8–8.4 V | $45.99 | y | US (RMRC) | https://readymaderc.com/products/details/86023-hitec-d645mw-32-bit-high-torque-metal-gear-servo |
| AGFRC B53CHN V2 | 12.5 @4.8 V; 15.5 @6.0 V; 18.5 @7.4 V; 20.5 @8.4 V kg·cm | 0.100 / 0.082 / 0.070 / 0.060 | 69 g | steel | 4.8–8.4 V | €42.90 | y (8) | Estonia (EU) | https://rc-modelshop.com/product/agf-rc-servo-b53chn-v2-20-5kg-0-06s-8-4v/ |
| KST X20-1806 (low-profile) | 14 @6.0 V; 16 @7.4 V; 18 @8.4 V kgf·cm | 0.08 / 0.07 / 0.06 | 50 g ±10 % | hardened steel | 6.0–8.4 V | $99.99 | n (backordered) | China | https://aifitlab.com/products/kst-x20-1806-servo-motor |
| Savox SV-1270TGP | 40.0 @7.4 V; 45.0 @8.4 V kg·cm | 0.11 / 0.10 | 64 g | titanium | — (specs at 7.4/8.4 V only) | $109.99 | y ("Add to cart") | US | https://extremeflightrc.com/products/savox-sv1270tgp-servo |

The required hinge moment has not been computed (—), so the 10–25 kg·cm band in the brief is unverified. The D645MW (≤ 12.9 kg·cm) sits at the bottom of that band. If the hinge-moment calculation calls for more than about 10 kg·cm on the ailerons, the B53CHN V2 at 6 V (15.5 kg·cm) is the next step up, but it ships from the EU. Five D645MW (2 ailerons, 2 elevator or ruddervator, 1 rudder) = 5 × $45.99 = **$229.95**.

---

## 5. Pack transport/storage
Skipped. The FAA PackSafe lithium-battery page returned HTTP 403 on 2026-10-13. Two vendor pages carry relevant notes: NextFPV says its Tattu 22 Ah LiPo "cannot be shipped by air" (https://www.nextfpv.com/products/tattu-22000mah-22-2v-25c-6s1p-lipo-battery-with-as150-xt150-plug), and the Tattu US store ships ground by FedEx/UPS. Every pack above 160 Wh in this list should be treated as ground-ship only. That limit is a commonly cited airline threshold that was **not verified** on a live page today.

---

## Recommended baseline (6S)

| Item | Pick | Unit price | Qty | Subtotal |
|---|---|---|---|---|
| Pusher motor | T-Motor AT3520 KV550 | $79.99 | 1 | $79.99 |
| Pusher ESC | Hobbywing Skywalker V2 60A | $41.99 | 1 | $41.99 |
| Pusher prop | APC 14×8.5EP (LP14085EP) | $6.79 | 3 | $20.37 |
| Flight battery | WREKD 6S3P P50B 15 Ah (Li-ion) **or** Tattu 16 Ah 30C (LiPo) | $378.00 / $335.99 | 1 | $378.00 / $335.99 |
| Charger + PSU | HOTA D6 Pro + Pyrodrone 400 W PSU | $213.98 | 1 | $213.98 |
| Servos | Hitec D645MW | $45.99 | 5 | $229.95 |
| **Total (excl. shipping/tax, one battery)** | | | | **$964.28** (Li-ion) / **$922.27** (LiPo) |

This total covers only pusher, battery, charger and servos, and it is already ~46–48 % of the $2,000 budget before lift motors, airframe, avionics and spares.

## Caveats
1. All thrust data are T-Motor static bench tests on tractor APC props. In-flight thrust at 20 m/s is lower, and the 14×8.5EP has no published table.
2. Cruise power (470 W) and hover current (68 A) are estimates built on assumed efficiencies and on `lift-propulsion.md`. They are not measured.
3. The WREKD packs are custom-built pre-orders (1–3 weeks). Their spec weights and product-data weights disagree by 10–15 %.
4. T-Motor store pages show neither stock nor shipping origin. LigPower and the T-Motor store are probably China-shipped; this is unconfirmed (—). The new US tariff and de minimis rules may add cost on top (OzRobotics note, not quantified).
5. Servo torque requirement is unverified until hinge moments are calculated. BEC voltage (5 V) limits HV servo torque.
6. Prices are single snapshots on 2026-10-13. Re-check them before ordering.

## What the team must measure
- **M1** Pusher static thrust and current with the 14×8.5EP on 6S, using a thrust stand or a luggage scale on a pivot plus a clamp meter. This fails the cruise requirement if static thrust at 60 % throttle is < 1.5 kgf, and the 60 A ESC is out of margin if full-throttle current is > 55 A.
- **M2** Received pack weight on a kitchen scale. It fails the battery mass budget if it is > 10 % over the spec weight.
- **M3** Pack voltage under a 68 A load (watt meter in the hover test). If 6S Li-ion sags below 3.2 V/cell, endurance and hover margin fall below estimate.
- **M4** Aileron hinge moment at 22 m/s (estimate from surface area and chord, or a spring-scale test on the built surface). The servo is undersized if the moment is > 50 % of servo stall torque at the BEC voltage.
