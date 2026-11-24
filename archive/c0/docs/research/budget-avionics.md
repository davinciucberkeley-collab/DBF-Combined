# Budget avionics set — ArduPilot QuadPlane (cut from the ~$700 Pixhawk set)

Lift + cruise VTOL: 4 or 8 lift motors stopped in cruise, 1 pusher, 4 servos
(2 ailerons, elevator, rudder). ArduPilot Plane with QuadPlane enabled.

- All prices and stock were checked on live pages on **2026-10-13**. Shopify stores were read
  through their public product JSON (`<product-url>.js`), which returns price and an
  `available` flag per variant. Other pages were read as rendered.
- "—" means the page did not show the value. Prices are USD, before tax and shipping.
- Search-engine snippets were **not** used as a price source. Where a snippet price differed
  from the live page, the live page wins. Examples: RDQ H743-WLITE showed $99.99 "in stock" in a
  snippet but is **$119.99, sold out** live. The RadioMaster Pocket "$59.99" is the **CC2500**
  variant; the ELRS variant is **$71.50**.
- Output counts needed: 4-lift = 4 lift + 1 pusher + 4 servos = **9**. 8-lift = 8 + 1 + 4 = **13**.
- Tax factor ×1.1025 (Berkeley) is reused from `docs/research/avionics-autopilot.md` §6.

---

## 0. Verdict

| Set | Total (pre-tax) | ×1.1025 | vs. Pixhawk set ($602.95, `avionics-autopilot.md` §6) |
|---|---|---|---|
| **4-lift, recommended** (CoreWing F405 Wing V2) | **$289.68** | **$319.37** | −$313.27 |
| 4-lift, floor (Wing Mini, T8L, MG996R) | $171.17 | $188.71 | −$431.78 |
| **8-lift, recommended** (Kakute H743-Wing, 14 outputs) | **$327.42** | **$360.98** + import duty — | −$275.53 |
| 8-lift, 12-output fallback (F405 Wing V2, ailerons on one Y-lead) | $289.68 | $319.37 | −$313.27 |

Arithmetic and line items are in §7. Shipping is not included: most pages did not show a cost
(see the per-row notes). Airspeed sensor is **not** in the totals. It is optional (§3) and adds $59.99.

Main caveats:
1. **F405 (1 MB flash) builds include QuadPlane** (`HAL_QUADPLANE_ENABLED` in the official
   features.txt). They **drop OctaQuad frames, Lua scripting, DLVR airspeed and OpenDroneID**. Octa (8 separate
   booms) is kept; coaxial OctaQuad is not.
2. **The CoreWing F405 Wing V2 / Wing Mini V2 have a firmware target only in Plane beta
   (4.7.2-beta) and latest**, not in stable 4.7.1. The older SpeedyBee F405 Wing is in stable,
   but every US vendor checked shows it sold out.
3. Only boards with **≥ 13 outputs** do 8-lift without Y-leads. The only one in stock was the
   Holybro Kakute H743-Wing. Holybro states its products ship from China, DAP, so the buyer pays duty.
4. The FC's built-in current sensor sits on a **2–6S (F405) / 3–8S (Kakute)** input. A 12S lift
   pack cannot go through it. 12S lift needs a separate FC supply and external current sensing.
5. Remote ID: the two cheapest modules checked are on the FAA DoC list: **NewBeeDrone BeeID ($36.99)
   and Ruko R111S ($39.99)**. ArduRemoteID-type boards (Holybro, CubePilot, Matek) are **not** on
   the list as broadcast modules.

---

## 1. Flight controllers

### 1.1 ArduPilot firmware support (official firmware server, Plane **stable = 4.7.1**)

Source: `https://firmware.ardupilot.org/Plane/stable/<TARGET>/features.txt` and
`firmware-version.txt`, checked 2026-10-13. "!" in features.txt = excluded from the build.

| Target (board) | QuadPlane | Octa | OctaQuad | Lua scripting | DLVR airspeed | MS4525 / MS5525 | OpenDroneID |
|---|---|---|---|---|---|---|---|
| SpeedyBeeF405WING (Wing APP / Wing Mini) | **yes** (`HAL_QUADPLANE_ENABLED`) | yes | **no** | **no** | **no** | yes / yes | no |
| CoreWingF405WingV2 / CoreWingF405WMiniV2 (**beta 4.7.2 only**) | yes | yes | no | no | no | — | — |
| MatekF405-TE (F405-WTE / WMN / WMO) | yes | yes | no | no | no | yes / yes | no |
| MatekF405-Wing | yes | yes | no | no | no | yes / yes | no |
| MicoAir405v2 | yes | yes | no | no | no | — | no |
| MatekH743 (H743-WING V1–V3, WLITE, SLIM, MINI) | yes | yes | yes | yes | yes | yes / yes | no |
| KakuteH7-Wing (Kakute H743-Wing) | yes | yes | yes | yes | yes | — | no |
| MicoAir743 / MicoAir743v2 | yes | yes | yes | yes | yes | — | no |
| FoxeerH743v1 | yes | yes | yes | **no** | yes | — | no |

Rule from the ArduPilot docs:

> "The ArduPilot firmware in some configurations exceeds 1 MB in size … For the affected
> autopilots, a reduced firmware is generated."
> — https://ardupilot.org/plane/docs/common-limited-firmware.html (checked 2026-10-13)

That page does not name per-board exclusions. It points to features.txt on the firmware
server. The F405 board pages say: "Due to flash memory limitations, this board does not include all
ArduPilot features." (SpeedyBee F405 Wing, Matek F405-Wing and CoreWing F405 Wing V2 pages, below.)

Board-page QuadPlane statements:
- SpeedyBee F405 Wing: "Sufficient outputs for QuadPlane applications."
  https://ardupilot.org/plane/docs/common-speedybeef405wing.html
- CoreWing F405 Wing V2 / Mini V2: suited to "fixed-wing and QuadPlane/VTOL aircraft."
  https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html
- Matek F405-TE family, H743 family, Kakute H743-Wing, MicoAir pages: no QuadPlane sentence.
  Support comes from features.txt above.

### 1.2 Hardware (ArduPilot board pages, checked 2026-10-13)

| Board | PWM outputs | ≥9 | ≥13 | Built-in current sensor | Servo BEC | Other BECs | Source |
|---|---|---|---|---|---|---|---|
| SpeedyBee F405 Wing APP | 12 (PWM12 = LED) | y | n | "120A" and "90A Cont., 215A peak" (page gives both) | 4.9/6/7.2 V, 4.5 A | 5 V 2.4 A; VTX 9/12/5 V 1.8 A | [AP page](https://ardupilot.org/plane/docs/common-speedybeef405wing.html) |
| CoreWing F405 Wing V2 | 12 (1–10 DShot, 11–12 PWM) | y | n | 90 A cont / 215 A peak | 5/6/7.2 V, 8 A / 14 A | 5.2 V 4 A; VTX 5/9/12 V 2 A | [AP page](https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html) |
| CoreWing F405 Wing Mini V2 | 12 | y | n | 90 A / 215 A | 5/6 V, 4 A / 5 A | 5 V 2 A | same |
| Matek F405-WTE | 12 | y | n | 220 A | 5/6/7.2 V, 8 A / 10 A | 5 V 2 A; 9/12 V 2 A | [AP page](https://ardupilot.org/plane/docs/common-matekf405-te.html) |
| Matek F405-WMN | 12 | y | n | 132 A | 5/6 V, 5 A | 5 V 1.5 A | same |
| Matek F405-WMO | "10x" in the spec list, "9x" in the header (S1–S9 + LED). Page is inconsistent | marginal | n | "132A"; a later notice on the page says "changed to 13.2A" | 5/6 V, 4.5 A (7 A peak) | 5 V 2 A | [Matek page](https://www.mateksys.com/?portfolio=f405-wmo) |
| Matek H743-WLITE | 13 (12 + LED) | y | y (13 incl. LED) | 220 A range, 90 A cont | 5/6/7.2 V, 8 A / 10 A | 5 V 2 A; 9/12 V 2 A | [Matek page](https://www.mateksys.com/?portfolio=h743-wlite) (marked **EOL**) |
| Matek H743-WING V3 | 13 | y | y | 132 A | 5/6/7.2 V, 8 A | 5 V 2 A; 9/12 V 2 A | [AP page](https://ardupilot.org/plane/docs/common-matekh743-wing.html) |
| **Holybro Kakute H743-Wing** | **14** | y | **y** | up to 120 A | 6/7.2 V, 6 A / 8 A | 5 V 2 A; 9/12 V 2 A; 3.3 V 1 A | [AP page](https://ardupilot.org/plane/docs/common-kakuteh7wing.html) |
| MicoAir H743 V2 (30×30) | 11 | y | n | **none** (external input) | **none** | 5 V 3 A; 9 V (AP page) / 12 V (vendor) 3 A | [AP page](https://ardupilot.org/plane/docs/common-MicoAir743v2.html) |
| MicoAir743 (v1) | 10 | y | n | none | none | 5 V 3 A; 9 V 3 A | [AP page](https://ardupilot.org/plane/docs/common-MicoAir743.html) |
| Foxeer H743 v1 | 9 | y (no spare) | n | — (current pin only) | none | 5 V 2 A; 10 V 2 A | [AP page](https://ardupilot.org/plane/docs/common-foxeerh743v1.html) |
| Holybro Kakute F4-Wing | 7 | **n** | n | "?? Amps" on page | 6/7.2 V, ? A | — | [AP page](https://ardupilot.org/plane/docs/common-KakuteF4-Wing.html) |
| SpeedyBee F405 Mini (stack) | 5 | **n** | n | none | none | — | [AP page](https://ardupilot.org/plane/docs/common-speedybeef405-mini.html) |

### 1.3 Price and stock (live, 2026-10-13)

| Board | Vendor | Price | In stock | Ships from | Shipping note | URL |
|---|---|---|---|---|---|---|
| **CoreWing F405 Wing APP V2 (soldered pins)**, model F405WING-V2-PIN | ReadyMadeRC | **$67.26** | **y** | US (banner "FAST SHIPPING FROM OHIO"; country of origin CN) | — | https://readymaderc.com/products/details/85786-speedybee-f405-wing-app-fixed-wing-flight-controller |
| CoreWing F405 Wing Mini (unsoldered pins) | ReadyMadeRC (same page, related item) | $50.91 | y | US (Ohio) | — | same |
| SpeedyBee F405 Wing APP | RaceDayQuads | $47.99 | **n** | — | — | https://www.racedayquads.com/products/speedybee-f405-wing-app-fixed-wing-flight-controller |
| SpeedyBee F405 Wing APP | ProgressiveRC | $44.99 | n | — | — | https://www.progressiverc.com/products/speedybee-f405-wing-app-flight-controller |
| SpeedyBee F405 Wing APP | NewBeeDrone | $51.99 | n | — | — | https://newbeedrone.com/products/speedybee-f405-wing-app-fixed-wing-flight-controller |
| SpeedyBee F405 Wing APP | WREKD | $47.99 | n | — | — | https://wrekd.com/products/speedybee-f405-wing-app-2-6s-fixed-wing-flight-controller |
| SpeedyBee F405 Wing APP Mini | RaceDayQuads | $43.49 | n | — | — | https://www.racedayquads.com/products/speedybee-f405-wing-mini-2-6s-fixed-wing-flight-controller |
| SpeedyBee F405 Wing Mini | ProgressiveRC | $39.99 | n | — | — | https://www.progressiverc.com/products/speedybee-f405-wing-mini-flight-controller |
| SpeedyBee (official store) | speedybee.com | — (no wing FC in its flight-controller catalog) | — | — | — | https://www.speedybee.com/flight-controller/ |
| SpeedyBee F405 Wing APP | GetFPV | — (HTTP 403) | — | — | — | https://www.getfpv.com/speedybee-f405-wing-app-flight-controller.html |
| Matek F405-WMO | Pyrodrone | $69.99 | y | — | "FREE US SHIPPING OVER $199" | https://pyrodrone.com/products/matek-f405-wmo-wing-flight-controller |
| Matek F405-WTE | RaceDayQuads | $71.99 | n | — | — | https://www.racedayquads.com/products/matek-f405-wte-wing-flight-controller |
| Matek F405-WMN | ProgressiveRC / WREKD | $65.99 / $79.49 | n / n | — | — | https://www.progressiverc.com/products/matek-f405-wmn-flight-controller |
| MicoAir H743 V2 (30×30, preloaded ArduPilot) | Pyrodrone | $72.99 | y | — | free over $199 | https://pyrodrone.com/products/micoair-h743-v2-2-6s-flight-controller-with-bluetooth-and-pre-loaded-with-ardupilot-30-30mm |
| **Holybro Kakute H743-Wing (no header)** | Holybro | **$105.00** | **y** | **China** ("All our products ship from China (unless noted otherwise)", DAP) | shipping calculated at checkout: — | https://holybro.com/products/kakute-h743-wing |
| Kakute H743-Wing (pin header soldered) | Holybro | $72.99 | n | China | — | same |
| Kakute H743-Wing | RaceDayQuads / WREKD / ProgressiveRC | $72.99 / $72.99 / $79.99 | n / n / n | — | — | https://www.racedayquads.com/products/holybro-kakute-3-8s-fixed-wing-flight-controller |
| Matek H743-WLITE | RaceDayQuads / WREKD | $119.99 / $119.99 | n / n | — | — | https://racedayquads.com/products/matek-h743-wlite-wing-flight-controller |
| Matek H743-WING V3 | WREKD / ProgressiveRC | $130.99 / $124.99 | n / n | — | — | https://wrekd.com/products/matek-h743-wing-v3-flight-controller |
| Kakute F405-Wing Mini | Holybro | $75.00 | y | China | — | https://holybro.com/products/kakute-f405-wing-mini |

**FC picks**
- **4-lift:** CoreWing F405 Wing V2, $67.26, in stock (US). It has 12 outputs (3 spare), a 90 A sensor and
  an 8 A servo BEC. Its firmware target is beta-only (see §0, caveat 2). Cheaper: Wing Mini V2 at $50.91, with a 4 A servo BEC.
  Stable-firmware alternative in stock: Matek F405-WMO at $69.99. It has 9–10 outputs, so no spare
  outputs, and the page's current-sensor figure is unclear.
- **8-lift:** Kakute H743-Wing, $105.00, in stock (China, duty —). It has 14 outputs, full H7 feature set
  and OctaQuad support. No ≥13-output wing board was in stock at a US vendor: every Matek H743 and
  Kakute H743-Wing listing checked at RDQ, WREKD and ProgressiveRC was sold out. Fallback: a 12-output F405 board with both ailerons on one output (Y-lead). This
  works for Octa (separate booms) but gives up independent ailerons and OctaQuad.

**Current-sensor headroom (estimate).** Hover electrical power from
`docs/research/lift-propulsion.md` "Hover-power comparison at the 12 kg reference" is
1.17–2.06 kW. Current is I = P / V_pack:
- 6S nominal 22.2 V (3.7 V/cell): 1170 / 22.2 = **53 A** to 2030 / 22.2 = **91 A** (est.). This
  sits at or above the 90 A continuous rating of the CoreWing / SpeedyBee sensor, so the top-power
  candidates would need external sensing.
- 12S nominal 44.4 V: 1170 / 44.4 = 26 A to 2060 / 44.4 = 46 A (est.). This is above the board input
  limit (SpeedyBee listing title "2-6S"; Kakute listing title "3-8S"). The FC must be powered
  from a BEC, and the lift pack needs an external current sensor (e.g. Matek 150A Current
  Sensor, $18.99 at ProgressiveRC, in stock:
  https://www.progressiverc.com/products/matek-150a-current-sensor — rating per title only).

---

## 2. GPS + compass (ArduPilot u-blox / UBX)

| Module | GNSS | Compass | Price | Vendor | In stock | Ships from | URL |
|---|---|---|---|---|---|---|---|
| **HGLRC M100-5883** (10th gen) | u-blox M10, 10 Hz, UBX | "Compass" (chip not named; "5883" in name) | **$20.49** | RaceDayQuads | **y** | — (local pickup Sarasota, FL listed) | https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen |
| HGLRC M100-5883 | same | same | $20.99 | WREKD | y | — | https://wrekd.com/products/hglrc-m100-5883-micro-gps-w-compass-10th-gen-oh |
| RDQ BN-880 (Beitian-type) | M8-class (72 ch; default 1 Hz) | HMC5883L | $23.99 | RaceDayQuads | y | — | https://www.racedayquads.com/products/rdq-bn-880-flight-control-gps-module-dual-module-compass-with-cable |
| Holybro Micro M10 | u-blox M10 | IST8310 or IST8308 | $27.99 | Holybro | y (IST8310 with case) | China | https://holybro.com/products/micro-m10-gps |
| Holybro M10 (standard 10-pin) | u-blox M10 | IST8310 / IST8308 | $43.99 | Holybro | y | China | https://holybro.com/products/m10-gps |
| Matek M10Q-5883 | M10 | QMC5883 (per name) | $47.99 | RaceDayQuads | n | — | https://www.racedayquads.com/products/matek-m10q-5883-gnss-compass |
| Matek M10Q-5883 | M10 | — | $51.99 | Pyrodrone | n | — | https://pyrodrone.com/products/matek-m10q-5883-gps-module-gps-compass |
| Foxeer M10Q-250 5883 | M10 | 5883 | $25.99 | Pyrodrone | n | — | https://pyrodrone.com/products/foxeer-m10q-250-5883-gps-and-compass-module |
| NewBeeDrone BeeID v1.1 (GPS + Remote ID) | u-blox M10Q, UART, "works with … Ardupilot" | **none listed** | $36.99 | RaceDayQuads | y | — | https://www.racedayquads.com/products/newbeedrone-beeid-v1-1-m10q-gps-module-remote-id |

**Pick:** HGLRC M100-5883, $20.49. The 25 × 25 mm patch Holybro Micro M10 ($27.99) is the step
up. It has a named IST8310 compass, but it ships from China. BN-880 is cheaper than the Holybro but M8-class.

---

## 3. Airspeed sensor (optional)

| Sensor | Bus | Supported in F405 build? | Price | Vendor | In stock | URL |
|---|---|---|---|---|---|---|
| **Holybro MS5525DSO + PT40 pitot** | I²C | yes (`AP_AIRSPEED_MS5525_ENABLED`) | **$59.99** | Holybro (China) | y | https://holybro.com/products/digital-air-speed-sensor-standard |
| Holybro MS5525DSO sensor only | I²C | yes | $53.59 | Holybro | y | same |
| Holybro MS4525DO + PT60 | I²C | yes | $71.99 | Holybro | y (PT40 kit $57.99: n) | same |
| Matek ASPD-4525 | I²C | yes (MS4525) | $59.99 | RaceDayQuads / WREKD | n / n | https://www.racedayquads.com/products/matek-analog-airspeed-sensor-aspd-4525 |
| Matek ASPD-DLVR | I²C | **no on F405** (`!AP_AIRSPEED_DLVR_ENABLED`); yes on H743 | $131.99 | RaceDayQuads | n | https://www.racedayquads.com/products/matek-digital-airspeed-sensor-aspd-dlvr |
| "Matek Digital Airspeed Sensor" (model not stated on page) | I²C | — | $89.99 | ProgressiveRC | y | https://www.progressiverc.com/products/matek-digital-airspeed-sensor |
| Generic MS4525DO | — | — | — (Amazon/AliExpress not readable; no live price) | — | — | — |

**Flying a QuadPlane without an airspeed sensor is supported.** ArduPilot then uses a
synthetic airspeed estimate:

> "Plane supports the use of an airspeed sensor … It is not recommended for most new users,
> however, as it does require additional tuning and adds one more layer of control to set up."
> — https://ardupilot.org/plane/docs/airspeed.html (checked 2026-10-13)

> Q_ASSIST_SPEED: "If unsure then set to 3 m/s below the minimum airspeed you will fly at. If you
> don't have an airspeed sensor then use 5 m/s below the minimum airspeed you fly at." The default of 0
> "will generate a pre-arm failure".
> — https://ardupilot.org/plane/docs/parameters.html#q-assist-speed (checked 2026-10-13)

Transition risk without a sensor:

> "if the transition is made downwind, the transition time is short, and no airspeed sensor is
> used in non-tailsitters, a stall could occur" … the logged CTUN.As uses "the synthetic airspeed
> if not" fitted.
> — https://ardupilot.org/plane/docs/quadplane-transitions.html (checked 2026-10-13)

Related: Q_OPTIONS bit 12 "disable speed based Qassist when using synthetic airspeed"
(https://ardupilot.org/plane/docs/quadplane-parameters.html). The Q_OPTIONS bit 19
groundspeed-complete trick on the transitions page is **"for tiltrotors only"**. It does not apply
to this airframe.

**Recommendation:** leave the airspeed sensor out of the first build (saves $59.99). Fly
transitions into wind and set Q_ASSIST_SPEED 5 m/s below the minimum flight speed, per the docs.
Add the MS5525DSO kit if transitions prove marginal. Do not buy a DLVR sensor for an F405 board.

---

## 4. Remote ID

### 4.1 FAA Declaration of Compliance (DoC) list — broadcast modules

Source: FAA UAS DoC public API, `https://uasdoc.faa.gov/api/v1/publicDOCRev?pageIndex=0&itemsPerPage=5000`
(the data behind https://uasdoc.faa.gov/listDocs), pulled 2026-10-13. There were 507 records; 478 were
"rid | accepted". Selected **Broadcast Module** rows, all status "accepted":

| Tracking # | Make | Model |
|---|---|---|
| RID000001995 | NewBeeDrone | BeeID |
| RID000000506, 827, 828, 1008 | Ruko | R111 |
| RID000001939 | Ruko | R111S |
| RID000000290 / 1281 / 2329 | Holy Stone | HSRID01 / HSRID02 / HSRID03 |
| RID000001125 | Potensic | RID-916 |
| RID000001753 / 1950 | Bwine | B112 / B112S |
| RID000001887 / 1948 | Veeniix | V113 / V113S |
| RID000001915 / 1949 | Gleesfun | G115 / G115S |
| RID000001611 / 2437 | Holyton | HT60 / HT65 |
| RID000000679 | Phoenix UAS | mRID |
| RID000001464 | Lumenier | RID |
| RID000001575 | FrSky | FrID |
| RID000000461 | Spektrum | SPMA9500 SkyID |
| RID000000058 | BlueMark | db120 (also db100, db121, db121pcb, db122fpv, db150–db154) |
| RID000000045 / 1121 | Dronetag | Beacon / Beacon gen.2 (also Mini, DRI, BS) |
| RID000002604 / 2603 | Aerobits | idME / idME+ (also RID000000309 "idME Pro") |
| RID000000645 / 1023 / 1141 | Zing Drone Solutions | Z-RID / Z-RID Lite / Z-RID Lite V2 |
| RID000000405 | DIY-D LLC | DIY-D ESP32-C3-MINI-1 |

**Not found** on the list (any category): Holybro, CubePilot, Matek, or any "ArduRemoteID"
make. An ArduRemoteID-based board wired to the FC is therefore **not** a DoC-accepted broadcast module.
The F405 builds also exclude OpenDroneID (`!AP_OPENDRONEID_ENABLED`). Use a standalone module.

### 4.2 Prices (live, 2026-10-13)

| Module | DoC # | Vendor claim (quoted) | Price | Vendor | In stock | Ships from / shipping | URL |
|---|---|---|---|---|---|---|---|
| **NewBeeDrone BeeID v1.1** (M10Q GPS + RID, 5.2 g, 5 V from FC) | RID000001995 ("BeeID") | "Remote ID compliant for FAA requirements"; the NewBeeDrone page also links "FAA UAS Declaration of Compliance here" | **$36.99** | RaceDayQuads | **y** | — | https://www.racedayquads.com/products/newbeedrone-beeid-v1-1-m10q-gps-module-remote-id |
| NewBeeDrone BeeID v1.1 | same | "fully compliant Remote ID broadcast functionality" | $39.99 | NewBeeDrone | y | — | https://newbeedrone.com/products/newbeedrone-beeid-v1-1-m10q-gps-module-with-remoteid-drone-tracker |
| **Ruko R111S** (self-powered, 13.5 g, USB-C) | RID000001939 | "Ensures FAA Compliance for Drones over 250g" (no DoC number on page) | **$39.99** | Ruko | JSON: available = true (rendered text also shows "Variant sold out", likely theme text) | "Free shipping on all orders within the mainland US"; 3–7 days US | https://www.ruko.net/products/ruko-r111-remote-id-module |
| Potensic RID-916 | RID000001125 | title "FAA-compliant Remote ID Broadcast Module" | $49.99 (was $79.99) | Potensic | **n** | — | https://store.potensic.com/products/rid-916 |
| Phoenix UAS mRID (needs separate M10 GPS) | RID000000679 | "a remote ID module approved by the FAA"; "Testing pending for Ardupilot" | $59.99 | Pyrodrone | y | free over $199 | https://pyrodrone.com/products/phoenix-uas-mrid-remote-id-module-no-gps |
| Lumenier RID | RID000001464 | — | $89.99 | Pyrodrone | n | — | https://pyrodrone.com/products/lumenier-remote-id-module-ndaa |
| Spektrum Sky Remote ID SPMA9500 | RID000000461 | — (snippet only; page not read) | — | Horizon Hobby | — | — | https://horizonhobby.com/product/sky-remote-id-module/SPMA9500.html |
| BlueMark db120 | RID000000058 | — | — (Dronefly/DSLRPros listings sold out, EOL) | — | — | — | https://www.dronefly.com/dronebeacon-db120-remoteid-broadcast-module-with-battery.html |
| Dronetag Beacon | RID000000045 / 1121 | — | $149 known (repo §3.6); live: — | — | — | — | — |
| Holy Stone HSRID0x, Bwine, Veeniix, Gleesfun, Holyton | on list | — | — (sold mainly on Amazon; Amazon pages not readable) | — | — | — | — |
| Aerobits idME | RID000002604 | — | — (no live USD page read) | — | — | — | — |

**Pick:** BeeID v1.1 at $36.99. Wire it to a 5 V pad and use only its RID broadcast. The HGLRC module
stays the nav GPS because BeeID lists no compass. Alternative: Ruko R111S at $39.99, self-powered,
which can move between aircraft. Before flight, look up the purchased unit's serial number on the
FAA DoC site (`uasdoc.faa.gov`, serial-number search). The DoC row names model "BeeID", while the
listing is "BeeID v1.1".

### 4.3 Flying without a module: FRIA / AMA fields

> "A FRIA is a defined geographic area where drones can be flown if they don't have Remote ID
> equipment. Both the drone and the pilot must be located within the FRIA's boundaries throughout
> the operation. In addition, the pilot of the drone must be able to see it at all times."
> "Only FAA-recognized Community Based Organizations (CBOs) and educational institutions such as
> … colleges, and universities are eligible to request the establishment of a FRIA."
> "The FAA publishes the locations of approved FRIAs on the FAA's UAS Data Delivery System."
> — https://www.faa.gov/uas/getting_started/remote_id/fria (checked 2026-10-13)

An AMA field is **not automatically** a FRIA. AMA distinguishes FAA-approved FRIAs, which "apply to
anyone within the designated boundary," from RIDEs (club exemptions). A RIDE "only provides
Remote ID relief for the club and its guests," may carry operational conditions, and lasts up to
four years. Posted 2025-02-14, updated 2026-01-05.
https://amablog.modelaircraft.org/amagov/?p=7634 (checked 2026-10-13). Check the specific
field's FRIA/RIDE badge in AMA Club Finder. UC Berkeley could also apply for its own FRIA as an
educational institution (FAA page above).

A module is cheap ($36.99), so the recommended set includes one. That leaves test sites unrestricted.

---

## 5. RC link (ELRS, CRSF to ArduPilot)

| Item | Type | Channels | RF | Price | Vendor | In stock | URL |
|---|---|---|---|---|---|---|---|
| RadioMaster T8L (M2) | screenless TX, 2× 18650 not incl. | "Up to 10 channels"; firmware "Special T8L Edition, non-configurable" | ELRS SX1281, 10–100 mW | **$34.99** | RadioMaster | y | https://www.radiomasterrc.com/products/t8l-radio-controller |
| BetaFPV LiteRadio 4 Neo | screenless TX, built-in 1S 1000 mAh | 10 | ELRS 2.4, 25/50/100 mW | $32.99 | BetaFPV | y (Mode 2 gray) | https://betafpv.com/products/literadio-4-radio-transmitter |
| **RadioMaster Pocket Crush (M2), ELRS** | EdgeTX, LCD, ext. module bay | "Maximum 16" | ELRS 2.4; "built-in ExpressLRS Backpack" | **$64.99** | RadioMaster | y | https://www.radiomasterrc.com/products/pocket-crush-radio-controller |
| RadioMaster Pocket (M2), ELRS | EdgeTX | 16 | ELRS 2.4 | $71.50 (CC2500 variant $59.99) | RadioMaster | y | https://www.radiomasterrc.com/products/pocket-radio-controller-m2 |
| RadioMaster Pocket Crush | — | — | — | $84.49 | RaceDayQuads | y | https://www.racedayquads.com/products/radiomaster-pocket-crush-rc-transmitter-elrs-2-4ghz-choose-your-color |
| BetaFPV ELRS Lite RX (flat antenna V1.2) | RX | — | 2.4 | $8.99 | BetaFPV | y | https://betafpv.com/products/elrs-lite-receiver |
| BetaFPV ELRS Nano RX | RX | — | 2.4 / 915 | $9.99 (was $16.99) | BetaFPV | y | https://betafpv.com/products/elrs-nano-receiver |
| RadioMaster XR1 Nano (dual-band) | RX | — | 2.4 + 900 | $11.99 | RadioMaster | y | https://www.radiomasterrc.com/products/xr1-nano-multi-frequency-expresslrs-receiver |
| **RadioMaster RP3 V2** | RX, dual antenna | — | 2.4 | **$19.99** (was $22.99) | RadioMaster | y | https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver |

Ships-from and shipping cost for RadioMaster and BetaFPV direct stores: — (not shown on the
product or policy pages read).

**ELRS MAVLink telemetry** (replaces a SiK radio):
- Requires TX and RX firmware 3.5.0. WiFi to the GCS needs TX Backpack 1.5.0. "STM32 based hardware
  cannot support running MAVLink mode": both TX and RX must be ESP-based. USB-to-GCS does not
  work with internal TX modules, so an internal module (Pocket, T8L, LiteRadio) must use the WiFi
  backpack.
- ArduPilot: `SERIALx_PROTOCOL=2`, `SERIALx_BAUD=460`, `RSSI_TYPE=5`, stream rates set to 1.
- MAVLink forces Hybrid or 16ch/2 switch mode, with telemetry ratio fixed 1:2. At 2.4 GHz 333 Hz Full,
  the downlink is about 1470 B/s.
- Source: https://www.expresslrs.org/software/mavlink/ (checked 2026-10-13).
- Pocket Crush states a built-in backpack, which meets the requirement. T8L / LiteRadio 4 backpack: not stated (—).
  RX MCU (ESP vs STM32) is not stated on the BetaFPV / RadioMaster RX pages read (—). Confirm before
  relying on MAVLink.

**Pick:** Pocket Crush ELRS ($64.99) + RP3 V2 ($19.99) = **$84.98**. It runs EdgeTX, so mode and
Q-mode switches are freely mappable, and the built-in backpack enables MAVLink over WiFi. Floor: T8L ($34.99) +
ELRS Lite ($8.99) = $43.98. Its firmware is "non-configurable", which limits switch mapping
for ArduPilot flight modes, and its backpack is unconfirmed.

---

## 6. Servos (2 ailerons, elevator, rudder)

Requirement from the task: ~8–15 kg·cm at 5–6 V, metal gear. The hinge moment has not been measured
(see `pusher-battery-servo.md` M4). The F405/H743 wing boards have a selectable 6 V (or 7.2 V) servo rail
(§1.2), so 6 V figures apply.

| Servo | Torque (stall) | Weight | Gears | Voltage | Price | Vendor | In stock | URL |
|---|---|---|---|---|---|---|---|---|
| **EMAX ES3005HV** (digital) | **8 kg·cm @6.0 V**; 10 @7.4 V; 11 @8.4 V | 43.2 g | metal | **6.0–8.4 V (no 5 V rating)** | **$19.99** | Emax USA (US store) | y | https://shop.emax-usa.com/products/es3005hv-high-voltage-servo |
| EMAX ES3005HV | same (specs from this page) | 43.2 g | metal | 6.0–8.4 V | $19.99 | ReadyMadeRC (US) | y | https://readymaderc.com/products/details/85971-emax-es3005-analog-waterproof-servo |
| MG996R (Waveshare) — **quality flag**: generic analog clone, no manufacturer QA data | 9 kg·cm @4.8 V; 11 @6 V | 55 g | metal | 4.8–6 V | $4.70 ea (1–9) | Waveshare | stock — | https://www.waveshare.com/mg996r-servo.htm |
| MG996R (Hobby Porter) — same flag | — | — | metal | — | $14.99 | 997RC Raceway (US) | y | https://997rcraceway.com/products/mg996r-hobby-porter-servo-analog-digital-metal-gear-servo-90-180-360 |
| Powerhobby LP200 (low profile, coreless) | 8 @6.0 V; 9 @7.4 V; 10 @8.4 V | — | metal | — | $29.95 | WREKD | y | https://wrekd.com/products/powerhobby-lp200-low-profile-high-speed-metal-gear-waterproof-hv-servo |
| Powerhobby 329TG | 19.0 @6.0 V; 24.0 @8.4 V | 63 g | titanium | 4.8–8.4 V | $27.95 | WREKD | y | https://wrekd.com/products/powerhobby-329tg-aluminum-high-torque-speed-titanium-gear-24kg-digital-servo |
| Hitec HS-5485HB | — | — | Karbonite (not metal) | — | $24.95 | WREKD | y | https://wrekd.com/products/hitec-hs-5485hb-standard-karbonite-digital-sport-servo |
| EMAX ES3054 (17 g) | 3.0 @4.8 V; 3.5 @6.0 V — **too weak** | 20.1 g | metal | — | $11.99 | RaceDayQuads | n | https://www.racedayquads.com/products/emax-es3054-17g-metal-gear-digital-servo |
| EMAX ES08MD II | 1.6 @4.8 V; 2.0 @6.0 V — **too weak** | 12 g | metal | — | $13.49 | RaceDayQuads | y | https://www.racedayquads.com/products/emax-es08md-ii-12g-digital-metal-gear-servo |
| Corona DS-339MG / DS-939MG | — | — | — | — | — (no live listing found; HobbyKing 403) | — | — | — |
| Miuzei MG996R / AGFRC / Savox budget | — | — | — | — | — (Amazon not readable; no live page) | — | — | — |
| Hitec D645MW (repo pick) | 8.3–12.9 kg·cm (range) | 57 g | metal | 4.8–8.4 V | $45.99 | ReadyMadeRC | y | `pusher-battery-servo.md` §4 |

**Pick:** 4 × EMAX ES3005HV = **$79.96**. It is metal, digital and 8 kg·cm at 6 V, and sold by a US store.
Set the FC servo rail to 6 V or 7.2 V. The ES3005HV has no 5 V rating. This replaces 5 × D645MW ($229.95)
in `pusher-battery-servo.md` §4, if the hinge-moment check (M4 there) shows 8 kg·cm is enough.
Floor: 4 × MG996R at $4.70 = $18.80. Shipping cost and origin are unknown, and it is a quality risk on
primary flight controls.

---

## 7. Totals

### 7.1 4-lift, recommended

| Item | Part | Price | Vendor |
|---|---|---|---|
| FC + PDB + current sensor | CoreWing F405 Wing APP V2 (soldered) | $67.26 | ReadyMadeRC |
| GPS + compass | HGLRC M100-5883 | $20.49 | RaceDayQuads |
| Remote ID | NewBeeDrone BeeID v1.1 | $36.99 | RaceDayQuads |
| TX | RadioMaster Pocket Crush ELRS | $64.99 | RadioMaster |
| RX | RadioMaster RP3 V2 | $19.99 | RadioMaster |
| Servos | 4 × EMAX ES3005HV | $79.96 | Emax USA |
| Airspeed | none (synthetic; §3) | $0.00 | — |
| **Total** | | **$289.68** | 67.26+20.49+36.99+64.99+19.99+79.96 |
| ×1.1025 | | **$319.37** | 289.68×1.1025 |

### 7.2 4-lift, floor (lowest live prices; more risk)

| Item | Part | Price |
|---|---|---|
| FC | CoreWing F405 Wing Mini (unsoldered; 4 A servo BEC) | $50.91 |
| GPS + compass | HGLRC M100-5883 | $20.49 |
| Remote ID | BeeID v1.1 | $36.99 |
| TX + RX | RadioMaster T8L + BetaFPV ELRS Lite | $34.99 + $8.99 |
| Servos | 4 × MG996R (Waveshare) | $18.80 |
| **Total** | | **$171.17** (50.91+20.49+36.99+34.99+8.99+18.80) |
| ×1.1025 | | $188.71 |

### 7.3 8-lift, recommended

| Item | Part | Price |
|---|---|---|
| FC (14 outputs, 120 A sensor, 3–8S) | Holybro Kakute H743-Wing (no header) | $105.00 (ships China; duty —) |
| GPS, RID, TX, RX, servos | as §7.1 | $20.49 + $36.99 + $64.99 + $19.99 + $79.96 |
| **Total** | | **$327.42** (105.00+222.42) |
| ×1.1025 | | **$360.98** + duty — |

8-lift fallback: §7.1 set ($289.68) with both ailerons on one output. Octa frame only, no OctaQuad.

Optional add-ons: airspeed MS5525DSO + PT40 $59.99 (Holybro); external 150 A current sensor
$18.99 (ProgressiveRC) for 12S lift or > 90 A hover.

---

## 8. What the team must measure

- **M1 — Hover current at MTOW** (watt meter on the lift pack, tethered hover). Compare it with the FC sensor's
  continuous rating: **90 A** for CoreWing / SpeedyBee, **120 A** for Kakute. Above the rating, add an external
  sensor. Above 6S on an F405 board, the FC must run from a BEC.
- **M2 — Control-surface hinge moment at cruise speed** (spring scale on the horn, or estimate from
  surface area). If the moment is > 50 % of 8 kg·cm (the ES3005HV at 6 V), the servo is undersized
  (same threshold as `pusher-battery-servo.md` M4).
- **M3 — Servo-rail current with 4 servos stalled** (bench, clamp meter). It must stay under the BEC rating:
  8 A for Wing V2, 4 A for Wing Mini V2, 6 A for Kakute H743-Wing.
- **M4 — Transition into wind without airspeed sensor** (log CTUN.As vs GPS groundspeed). If
  the synthetic airspeed reads > 3 m/s off the GPS-derived estimate in calm air, or transitions
  time out, add the MS5525DSO kit.
- **M5 — ELRS MAVLink link** (bench). Confirm both RX and TX run ELRS ≥ 3.5.0 in MAVLink mode
  and that Mission Planner connects over the Pocket Crush backpack WiFi. If not, budget a SiK radio
  ($58.99, `avionics-autopilot.md` §3.5).
- **M6 — Remote ID broadcast check** (phone app such as Drone Scanner). Confirm the BeeID serial
  appears on the FAA DoC serial search before the first outdoor flight.
- **M7 — Firmware**: confirm a CoreWingF405WingV2 build in Plane *stable* before flight-test
  season. If it is still beta-only, buy a board with a stable target: Matek F405-WMO (stable
  MatekF405-TE) or Kakute H743-Wing.
