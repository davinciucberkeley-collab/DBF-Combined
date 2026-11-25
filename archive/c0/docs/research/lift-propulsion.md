# Lift propulsion: motor + prop + ESC candidates

**Date checked: 2026-10-13** (all prices, specs and stock below were read on live pages that day; WebFetch/WebSearch).
Scope: lift rotors for a lift + cruise VTOL, MTOW 8–15 kg, $2,000 total budget.

Sizing targets (from the task brief, formula shown):
- 4-lift: max static thrust per motor = MTOW × 1.6 / 4 = **4.0–6.0 kgf** (MTOW 10–15 kg). Hover per motor = MTOW / 4 = 2.5–3.75 kg.
- 8-lift: max static thrust per motor = MTOW × 1.6 / 8 = **2.0–3.0 kgf**. Hover per motor = MTOW / 8 = 1.25–1.9 kg.
- "Hover-ish" efficiency below is read at ~3 kg/motor (4-lift) and ~1.5 kg/motor (8-lift), i.e. a 12 kg MTOW reference.

Legend: "—" = not on the page checked. "est." = derived by me, not published. Ships from: "CN" = T-Motor/LigPower store (states free DHL/UPS international express over $200); "US" = US-based store (ship origin for the actual parcel not always stated).

---

## Table A — 4-lift (target 4–6 kgf max per motor)

| # | Part (exact) | Cells | KV | Weight (g) | Prop | Max thrust (kgf) | Thrust @ ~50% thr. (g / A / W) | g/W @ ~3 kg | ESC (A) | Unit price USD (motor/system) | ESC + prop price | In stock | Ships from | Prop lock / align | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | **Hobbywing XRotor X6 SE 280KV** (integrated motor + ESC, 6208) | 6S (23 V rated) | 280 | 373 ±5 incl. prop + cable | MFP 22×7.0 folding (sold as MFP2270) | 6.06 (100%, 23 V) | 2449 / 11.1 / 256.3 @51% | 8.5 (3132 g @60%) | Integrated 60A-BLDC, 30 A cont / 60 A 3 s | $114.99 (CW or CCW) | ESC incl.; MFP 2270 prop $19.99 (props sold separately) | — (Add to cart shown; prop shown sold out on some pages) | US (Hobbywing North America) | Folding blades; no stop-position (IPC) feature stated | [hobbywing.com/en/products/cmx6se](https://www.hobbywing.com/en/products/cmx6se); [hobbywingdirect.com/products/eps-ips-x6se](https://www.hobbywingdirect.com/products/eps-ips-x6se) |
| A2 | **T-Motor MN505-S KV320** (Navigator, IP45) + P22×6.6 CF | 6S | 320 | 225 incl. cable | P22×6.6 (also P20×6; rec. 20–22") fixed CF | 6.68 (P22) / 5.37 (P20) | P22: 2090 / 9.2 / 221 @50% | 8.15 (2968 g @60%, P22) | Rec. FLAME 60A 12S or ALPHA 60A 6S; peak 55 A/180 s | $109.90 | ALPHA 60A 6S $69.99; P20×6 pair $108.90 (LigPower); P22×6.6 — | — | CN | Fixed 2-blade: can be parked fore-aft only with a position-stopping ESC; ALPHA has no documented lock | [store.tmotor.com/goods.php?id=698](https://store.tmotor.com/goods.php?id=698); [ALPHA 60A](https://store.tmotor.com/product/alpha-60a-6s-esc.html); [P20×6](https://www.ligpower.com/product/20x6-polish-carbon-fiber-propeller.html) |
| A3 | **T-Motor VL5009 KV275** + V60A ESC + DZ17×6.2 (VL series VTOL system) | 12S (also 14S) | 275 | Motor 280 incl. cable; ESC 85; blade 28 ±3 each | DZ17×6.2 | 8.62 (12S, 45.6 V) | 2437 / 7.31 / 331 @50% | ~6.6 est. (interp. 50–60%) | V60A: 30 A cont / 60 A 10 s, 6–14S, PWM or DroneCAN | $129.00 (motor; package contents unclear) | V60A $129.90 (LigPower); DZ17 — | — | CN | **Yes — electronic 360° custom-angle prop locking via V60A** (~10 W to hold) | [uav-en.tmotor.com VL5009](https://uav-en.tmotor.com/2024/VL-Series-Propulsion-System_1108/1250.html); [store.tmotor.com VL5009](https://store.tmotor.com/product/vl5009-brushless-motor-for-uavs.html); [V60A](https://www.ligpower.com/product/v60a-bldc-foc-drone-esc.html) |
| A4 | **T-Motor V505 KV260** (V-type VTOL motor) + P17×5.8 | 12S (42–52 V) | 260 | 215 (255 incl. cable) | P16×5.4 or P17×5.8 fixed CF | 8.74 (P17) / 7.50 (P16) | P17: 3203 / 11.68 / 558 @50% | 5.86 (2979 g @48%, P17) | Rec. FLAME 60A 12S | $119.99 | FLAME 60A 12S V2.0 $99.99; P16×5.4 pair $62.90; P17×5.8 pair $71.9 (LigPower) | — | CN | No lock on motor page; would need an ESC with stop-position | [ligpower.com V505](https://www.ligpower.com/product/v505-vtol-motor.html); [FLAME 60A 12S V2](https://store.tmotor.com/product/flame-60a-12s-V2-esc.html) |
| A5 | **Hobbywing XRotor X6 Plus** (integrated, 6215-class) + MFP 24×8.0 | 12–14S (46 V test) | 150 | 790 total | MFP 24×8.0 folding | 11.85 (100%, 46 V) | 4001 / 9.7 / 449 @51% | 10.2 (2997 g @45%) | Integrated, 80 A max input | — (US: X6 Plus G2 sold out at hobbywingdirect; India ₹11,119–11,373 at Robu, not USD) | ESC incl.; MFP 2480 — (sold out at hobbywingdirect) | n (US) | — | Folding; stop-position not stated for this model | [hobbywing.com X6 Plus](http://www.hobbywing.com/en/products/xrotor-x6-plus269); [hobbywingdirect X-series](https://www.hobbywingdirect.com/collections/x-series) |

Out of range / reference only: **T-Motor V605 KV210** (12S, V22×7.4) max 12.76 kgf, $149.99 — oversized ([store.tmotor.com/goods.php?id=922](https://store.tmotor.com/goods.php?id=922)).

## Table B — 8-lift / coaxial X8 (target 2–3 kgf max per motor)

| # | Part (exact) | Cells | KV | Weight (g) | Prop | Max thrust (kgf) | Thrust @ ~50% thr. (g / A / W) | g/W @ ~1.5 kg | ESC (A) | Unit price USD | ESC + prop price | In stock | Ships from | Prop lock / align | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | **T-Motor MN5008 KV340** (Antigravity) + P17×5.8 CF | 6S | 340 | 135 incl. cable (as listed) | P17×5.8 (rec. P17–18") fixed CF | 3.56 (P17) / 4.22 (P18) | 1224 / 5.33 / 125 @50% | ~9.0 est. (between 1224 g @9.82 and 1697 g @8.55) | Rec. AIR 40A; 26.4 A at 100% P17 | $89.99 | P17×5.8 pair $71.9 (LigPower); ESC e.g. Hobbywing XRotor 40A $17.99 (my pairing, not T-Motor's) | — | CN | Fixed 2-blade; no lock | [ligpower.com MN5008 KV340](https://www.ligpower.com/product/mn5008-kv340-motor-antigravity-type.html); [XRotor 40A](https://www.hobbywingdirect.com/products/xrotor-40a-esc) |
| B2 | **SunnySky V5210 KV300** (SS-V5210-300) + EOLO C18 | 4–6S | 300 | 200 | EOLO CN17×6.2 / C18 / C20 / CN22×6.2 | 3.00 (C18, 22.2 V) / 2.81 (CN17, 22.2 V) | (no throttle column) 1500 / 7.2 / 160 @22.2 V, C18 | 9.38 (1500 g, C18, 22.2 V) | 40–60 A; 44 A / 30 s max | $86.99 | ESC/prop — | — (Add to cart shown) | US (BuddyRC, Columbus OH) | Fixed; no lock | [buddyrc.com sunnysky-v5210-motor](https://www.buddyrc.com/products/sunnysky-v5210-motor) |
| B3 | **T-Motor MN4014 KV330** (Navigator) + P17×5.8 CF | 4–8S (test 22.2 V) | 330 | 150 (171 incl. cable) | P15×5 / P16×5.4 / P17×5.8 fixed CF | 2.60 (P17) / 2.39 (P16) / 1.92 (P15) | P17: 1050 / 4.7 / 104 @50% | 8.90 (1580 g @65%, P17) | Rec. Air 40A | $96.90 | P17×5.8 pair $71.9 | — (GetFPV: out of stock per search snippet) | CN | Fixed; no lock | [store.tmotor.com MN4014 KV330](https://store.tmotor.com/product/mn4014-kv330-motor-navigator-type.html) |
| B4 | **Hobbywing XRotor X6 SE 380KV** (integrated) + MFP 18×6.0 | 6S | 380 | 348 ±5 incl. prop + cable | MFP 18×6.0 folding (MFP1860) | 5.60 (100%, 23 V) | 1962 / 10.1 / 232.8 @51% | 8.9 (1659 g @45%) | Integrated 60A-BLDC, 30 A cont / 60 A 3 s | $129.99 | ESC incl.; MFP1860 $19.99, **sold out** | — (prop n) | US (Hobbywing North America) | Folding; no IPC stated | [hobbywing.com cmx6se](https://www.hobbywing.com/en/products/cmx6se); [hobbywingdirect X6 SE](https://www.hobbywingdirect.com/products/eps-ips-x6se); [MFP1860](https://www.hobbywingdirect.com/products/eps-prop-1860) |
| B5 | **T-Motor MN501-S KV240** (Navigator, IP45) + P15×5 on 12S | 6–12S | 240 | 170 incl. cable | P15×5 (12S) or P22×6.6 (6S); rec. 14–15" or 20–22" | 4.66 (P15, 48.5 V) / 4.19 (P22, 24.3 V) | P15 12S: 1605 / 5.30 / 258 @50% | 6.23 (1605 g, P15, 12S) | Rec. AIR 40A; V60A lists MN501S KV240 as compatible | $99.90 | P15×5 — | — | CN | Fixed; V60A prop-lock pairing for this motor not confirmed | [ligpower.com MN501-S KV240](https://www.ligpower.com/product/mn501-s-kv240-motor-navigator-type.html) |

Note B4 and B5 exceed the 3 kgf ceiling; they are listed because the X6 SE 380KV is Hobbywing-rated at 2 kg/axis recommended (matches 8-lift hover) and the MN501-S is the only 12S option found in this class.

---

## Thrust-table excerpts (published numbers)

### 4-lift #1 — Hobbywing XRotor X6 SE 280KV, MFP 22×7.0, 23 V (6S), 25 °C, sea level
Source: https://www.hobbywing.com/en/products/cmx6se (checked 2026-10-13)

| Throttle | Thrust (g) | Current (A) | Power in (W) | g/W |
|---|---|---|---|---|
| 45% | 2013 | 8.4 | 193.5 | 10.4 |
| 60% | 3132 | 15.9 | 366.6 | 8.5 |
| 75% | 4306 | 25.9 | 597.9 | 7.2 |
| 100% | 6058 | 45.6 | 1051.6 | 5.8 |

### 4-lift #2 — T-Motor MN505-S KV320, P22×6.6, ~24 V (6S), 9.5 °C ambient
Source: https://store.tmotor.com/goods.php?id=698 (checked 2026-10-13)

| Throttle | Thrust (g) | Current (A) | Power (W) | g/W |
|---|---|---|---|---|
| 50% | 2090 | 9.2 | 221 | 9.46 |
| 60% | 2968 | 15.2 | 364 | 8.15 |
| 75% | 4349 | 26.7 | 640 | 6.80 |
| 100% | 6680 | 52.4 | 1249 | 5.35 |

(Same page, P20×6: 2921 g / 16.3 A / 393 W / 7.44 g/W @70%; 5372 g / 38.5 A / 921 W @100%.)

### 8-lift #1 — T-Motor MN5008 KV340, P17×5.8 CF, 6S
Source: https://www.ligpower.com/product/mn5008-kv340-motor-antigravity-type.html (checked 2026-10-13)

| Throttle | Voltage (V) | Thrust (g) | Current (A) | Power (W) | g/W |
|---|---|---|---|---|---|
| 50% | 23.38 | 1224 | 5.33 | 125 | 9.82 |
| 60% | 23.27 | 1697 | 8.53 | 199 | 8.55 |
| 65% | 23.21 | 1936 | 10.38 | 241 | 8.03 |
| 100% | 22.72 | 3556 | 26.39 | 600 | 5.93 |

### 8-lift #2 — SunnySky V5210 KV300, EOLO C18, 22.2 V (6S nominal)
Source: https://www.buddyrc.com/products/sunnysky-v5210-motor (checked 2026-10-13). Table is by thrust step, no throttle column.

| Thrust (g) | Current (A) | Power (W) | g/W |
|---|---|---|---|
| 1000 | 4.1 | 91 | 10.99 |
| 1500 | 7.2 | 160 | 9.38 |
| 2000 | 10.9 | 242 | 8.27 |
| 3000 (max) | 19.8 | 440 | 6.83 |

---

## Hover-power comparison at the 12 kg reference (est., from the tables above)

| Layout | Candidate | Thrust/motor | g/W | Electrical hover power, all motors (est.) |
|---|---|---|---|---|
| 4-lift | X6 Plus (12S, 24") | 2997 g | 10.2 | 4 × 293 W ≈ 1.17 kW |
| 4-lift | X6 SE 280KV (6S, 22") | 3132 g | 8.5 | 4 × 367 W ≈ 1.47 kW |
| 4-lift | MN505-S KV320 + P22 (6S) | 2968 g | 8.15 | 4 × 364 W ≈ 1.46 kW |
| 4-lift | VL5009 (12S, 17") | ~3000 g | ~6.6 est. | ≈ 1.8 kW est. |
| 4-lift | V505 + P17 (12S) | 2979 g | 5.86 | 4 × 509 W ≈ 2.03 kW |
| 8-lift | MN5008 KV340 + P17 | ~1500 g | ~9.0 est. | ≈ 8 × 167 W ≈ 1.33 kW est. |
| 8-lift | V5210 + C18 | 1500 g | 9.38 | 8 × 160 W ≈ 1.28 kW |
| 8-lift | X6 SE 380KV + 1860 | 1659 g | 8.9 | ≈ 8 × 186 W ≈ 1.49 kW (at 1659 g) |
| 8-lift | MN501-S KV240 + P15 (12S) | 1605 g | 6.23 | 8 × 258 W ≈ 2.06 kW |

## Rough lift-set cost (est., parts only, before shipping/tax/spares)

- 4-lift X6 SE 280KV: 4 × $114.99 + 4 × $19.99 (if one prop per listing; listing does not say) ≈ **$540**.
- 4-lift MN505-S KV320: 4 × $109.90 + 4 × $69.99 (ALPHA 60A) + props (P20×6: 2 pairs × $108.90) ≈ **$1,081**.
- 4-lift VL5009 + V60A (with prop lock): 4 × ($129.00 + $129.90) + DZ17 props (—) ≈ **$1,036 + props**.
- 8-lift MN5008 KV340: 8 × $89.99 + 4 pairs × $71.9 + 8 × $17.99 ≈ **$1,151**.
- 8-lift SunnySky V5210: 8 × $86.99 = $696 + 8 ESCs + 8 props (—) ≈ **$840+**.

---

## Notes / caveats

1. **Prop alignment in cruise.** Only the T-Motor VL series + V60A ESC states an electronic, 360° custom-angle prop lock (~10 W holding power). Hobbywing offers "IPC" (Intelligent Propeller Control) stop-position on IPC ESCs (e.g. XRotor Pro H60A 14S BLDC IPC; https://www.hobbywing.com/en/news/info/100), but the US store's H60A listing shows IPC = No for both variants and is sold out (https://www.hobbywingdirect.com/products/eps-esc-foc-h60, $89.99 6S / $104.99 14S). No IPC is stated for the X6 SE. T-Motor ALPHA ESCs have no documented lock (only lock-up *protection*). Everything else needs a fixed 2-blade prop plus a mechanical or ESC-based parking scheme — see the ArduPilot thread on this (https://discuss.ardupilot.org/t/vtol-quadplane-align-brake-props-in-plane-mode/78897).
2. **Folding vs fixed.** Hobbywing MFP props (X6 SE, X6 Plus) are folding. On a stopped lift rotor in cruise, folding blades are free to swing; whether they trail fore-aft or windmill was not found on any page — must be tested. Fixed CF props (T-Motor P-series) hold whatever angle the hub stops at.
3. **X6 SE continuous rating.** Hobbywing lists rated output (max continuous) 187 W (280KV) and recommended 2.2 kg/axis. Hovering at 3 kg/motor needs ~367 W input, above that rating. Fine for short hover-and-transition, but a long hover would run it hot. Rated takeoff weight per Hobbywing implies ~8.8 kg MTOW for a quad.
4. **X6 SE 380KV table has duplicated rows** (35% and 37% identical) on Hobbywing's page — treat as a publishing error.
5. **X6 Plus** gives the best published hover efficiency (10.2 g/W at 3 kg) but is 790 g/unit, 24" props, 12S, and no current USD source was found (G2 sold out in US). Oversized for a 2–3 m span.
6. **12S options found (V505, VL5009, MN501-S on 12S) run 5.9–6.6 g/W at hover**, 25–40% worse than the best 6S/large-prop options. 12S lowers current but these motors are sized for heavier aircraft.
7. **MN5008 weight**: LigPower lists 135 g incl. cable; verify on receipt (other MN50xx motors list heavier).
8. **MN4014 KV330 max 2.6 kgf** gives T/W = 8 × 2.6 / 15 = 1.39 at 15 kg — below the 1.6 target above ~13 kg MTOW.
9. **SunnySky V5210 thrust table is by thrust step, not throttle**; the CN22 100% row was a 1-minute test at 124 °C — not continuous.
10. **ESC pairing for MN5008 with Hobbywing XRotor 40A ($17.99, 2–6S, 40 A cont, no BEC)** is my pairing, not a manufacturer recommendation.
11. **Stock** is "—" for most: T-Motor/LigPower and BuddyRC pages show Add-to-Cart without an explicit stock status. GetFPV returned HTTP 403 to automated fetch, so GetFPV prices/stock were not verified.
12. **Shipping/tariffs** for CN-shipped T-Motor parts are not included; RobotShop's US listing of the ALPHA 60A ($86.45 vs $69.99) notes tariffs included, suggesting a ~20%+ landed premium (est.).
13. **Not covered:** Brother Hobby, iFlight and SunnySky V5215/V4014 — no live thrust table or US price was found in this pass. Hobbywing V-series VTOL motors (V8014 etc.) are 12–24S and 21 kg+ class, too large.
14. Thrust tables are manufacturer bench data ("for reference only" on T-Motor and Hobbywing pages) at differing ambient temperatures (T-Motor MN505-S at 9.5 °C, Hobbywing at 25 °C); compare with care and verify with a thrust stand.
