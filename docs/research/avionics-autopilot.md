# Avionics, autopilot software, test gear, compliance costs

Parts research for the lift + cruise VTOL (4 or 8 lift rotors stopped in cruise,
pusher, fixed wing, 8–15 kg MTOW, $2,000 total budget).

- All items checked on live pages on **2026-10-13** unless a row says otherwise.
- "—" means the page did not show the value. Prices are USD before tax and shipping.
- "Ships from" is given only where the page says so. Otherwise it is "—", and the
  vendor's home country is noted for context only.
- Search-engine snippets were **not** used as sources for prices. Where only a
  third-party snippet existed, the row says so and is labeled *unverified*.

---

## 1. Autopilot software

### 1.1 Latest stable releases

| Stack | Latest stable | Release date | Next in pipeline | Source (checked 2026-10-13) |
|---|---|---|---|---|
| ArduPilot Plane | **Plane-4.7.1** (marked "Latest") | 04-Sep-2026 per the release notes; the GitHub entry shows 03-Sep | Plane-4.7.0 came out 21-Jul-2026. The docs parameter list is already "V4.8.0 dev" | https://github.com/ArduPilot/ardupilot/releases |
| PX4 Autopilot | **v1.17.0** ("Stable Release", marked "Latest") | 13-May-2026 (asset timestamps are 2026) | v1.18.0-rc1, 10-Sep-2026 (pre-release) | https://github.com/PX4/PX4-Autopilot/releases |

The ArduPilot "Complete Parameter List" page shows **Plane latest V4.8.0 dev**
(https://ardupilot.org/plane/docs/parameters.html). The descriptions below come
from that page. The page does not show default values for most of these
parameters, so a default is listed only where some doc page states it.

### 1.2 ArduPilot QuadPlane (lift + cruise = "QuadPlane" with separate lift motors)

**Frame class/type** (https://ardupilot.org/plane/docs/parameters.html, https://ardupilot.org/plane/docs/quadplane-frame-setup.html)

| Param | Values relevant to us | Notes |
|---|---|---|
| `Q_FRAME_CLASS` | 1 Quad, 2 Hexa, **3 Octa**, **4 OctaQuad**, 5 Y6, 7 Tri, 10 Single/Dual, 12 DodecaHexa, 14 Deca, 15 Scripting Matrix, 17 Dynamic Scripting Matrix | 8 lift rotors on 8 separate booms = Octa (3). 8 rotors as 4 coaxial pairs = OctaQuad (4) |
| `Q_FRAME_TYPE` | 0 Plus, **1 X**, 2 V, **3 H**, 4 V-Tail, 5 A-Tail, 10 Y6B, 11 Y6F, 12 BetaFlightX … 19 Y4 | Lift + cruise booms are usually X or H |
| Motor outputs | Motor1–8 = `SERVOn_FUNCTION` 33–40 | Quad lift motors default to outputs 5–8. The frame-setup page gives an OctaQuad example on outputs 5–12. The functions are set automatically on boot |

**Transition and assist** (descriptions quoted or paraphrased from https://ardupilot.org/plane/docs/parameters.html; transition behavior from https://ardupilot.org/plane/docs/quadplane-transitions.html)

| Param | Meaning | Default | Range / guidance from docs |
|---|---|---|---|
| `AIRSPEED_MIN` (was `ARSPD_FBW_MIN`) | Minimum airspeed demanded in auto-throttle modes. **The forward transition completes when airspeed reaches AIRSPEED_MIN** (transitions page) | — | 5–100 m/s. The docs say to set it "20% higher than level flight stall speed". The rename from `ARSPD_FBW_MIN` in 4.5.x is reported only on forums (e.g. https://discuss.ardupilot.org/t/missing-parameters-arspd-fbw-min-and-arspd-fbw-max-on-speedybee-f405-wing-with-quadplane-configuration-body/129425). The current param list has only `AIRSPEED_MIN` |
| `AIRSPEED_CRUISE` | Target cruise airspeed (indicated) in auto-throttle modes | — | m/s |
| `AIRSPEED_STALL` | Used by stall prevention and as the TECS minimum on landing final. 0 = assume AIRSPEED_MIN | — | 5–75 m/s |
| `Q_TRANSITION_MS` | Time after AIRSPEED_MIN is reached over which the VTOL motor contribution tapers to zero. The lift motors then switch off | **5000 ms** (transitions page) | 500–30000 ms. Marked "advanced" |
| `Q_TRANS_FAIL` | Maximum forward-transition time. If exceeded, the aircraft changes to the `Q_TRANS_FAIL_ACT` mode (or completes the transition if Q_OPTIONS bit 19 is set) | **0 = no limit** (transitions page) | 0–20 s |
| `Q_TRANS_FAIL_ACT` | Mode on transition timeout: -1 warn only, 0 QLand, 1 QRTL | — | |
| `Q_TRANS_DECEL` | Deceleration used to compute stopping distance for the back-transition | — | 0.2–5 m/s² |
| `Q_BACKTRANS_MS` | Back-transition pitch-limit ramp (SLT and tiltrotor) | — | 0–10000 ms |
| `Q_ASSIST_SPEED` | Airspeed below which the VTOL motors give stability and lift assist in fixed-wing modes. **0 = assist disabled, but this causes a pre-arm failure.** -1 = assist off except during transitions | **0** (stated in the param description) | 0–100 m/s. The docs say: "If unsure then set to 3 m/s below the minimum airspeed you will fly at. If you don't have an airspeed sensor then use 5 m/s below" |
| `Q_ASSIST_ANGLE` | Attitude error beyond which the VTOL motors assist. Needs a positive Q_ASSIST_SPEED. Assist starts when attitude is ≥5° outside the normal limits for Q_ASSIST_DELAY | — | 0–90°. 0 disables |
| `Q_ASSIST_ALT` | Assist triggers below this AGL altitude while the VTOL motors are off | — | 0–120 m. 0 disables |
| `Q_ASSIST_DELAY` | Delay between the threshold being met and assist starting | — | 0–2 s |
| `Q_ASSIST_OPTIONS` | bit0: disable forced fixed-wing controller recovery. bit1: disable QuadPlane spin recovery | — | |
| `Q_THRST_LOSS_OPT` | **Motor-out**: VTOL thrust-loss detection ("Potential VTOL Thrust Loss" warning). Detection lets the mixer ignore the failed motor and make better use of the remaining motors | — | bit0 disables detection. bit1 limits it to VTOL modes |

**Lift motor stop in cruise:** in MANUAL and ACRO the VTOL motors stop immediately.
In other fixed-wing modes they stay on until AIRSPEED_MIN, then ramp down over
Q_TRANSITION_MS and switch off. On a back-transition the forward motor stops
immediately (https://ardupilot.org/plane/docs/quadplane-transitions.html).
Holding the stopped props in line with the airflow is not covered on the pages
checked: —.

### 1.3 PX4 Standard VTOL

Parameter values come from https://docs.px4.io/main/en/advanced_config/parameter_reference.html.
This is the **main (dev)** branch reference; the page also offers a v1.17 (stable)
selector. Tuning guidance comes from https://docs.px4.io/v1.17/en/config_vtol/vtol_quad_configuration.html.

| Param | Meaning | Default | Range |
|---|---|---|---|
| `VT_TYPE` | VTOL type: 0 Tailsitter, 1 Tiltrotor, **2 Standard** | 0 | 0–2 |
| `VT_ARSP_TRANS` | Transition airspeed: airspeed at which the aircraft switches to FW mode. The docs say to keep it "comfortably above stall" (FW_AIRSPD_MIN). This is not checked automatically | **10.0 m/s** | 0–30 |
| `VT_ARSP_BLEND` | Airspeed at which MC and FW control start to blend. 0 = keep full MC control until transition | **8.0 m/s** | 0–30 |
| `VT_F_TRANS_DUR` | Front-transition duration (time used for a transition) | **5.0 s** | 0.1–20 |
| `VT_F_TRANS_THR` | Pusher throttle target during the front transition. Must be high enough to reach VT_ARSP_TRANS | **1.0** | 0–1 |
| `VT_TRANS_MIN_TM` | Minimum front-transition time | **2.0 s** | 0–20 |
| `VT_TRANS_TIMEOUT` | Front-transition timeout. On expiry the transition is cancelled and a **quad-chute** is triggered | **15.0 s** | 0.1–30 |
| `VT_F_TR_OL_TM` | Open-loop transition time with no airspeed sensor. With a sensor, the transition times out if VT_ARSP_BLEND is not reached in this time | **6.0 s** | 1–30 |
| `VT_B_TRANS_DUR` | Maximum back-transition duration. The back-transition also ends when groundspeed < MPC_XY_CRUISE | **10.0 s** | 0.1–20 |
| `VT_B_TRANS_RAMP` | MC motor ramp-up time in the back-transition | **3.0 s** | 0–20 |
| `VT_B_DEC_MSS` | Back-transition deceleration (tracked by a controller on standard VTOL) | **2.0 m/s²** | 0.5–10 |
| `VT_ELEV_MC_LOCK` | Lock the control surfaces in hover | **Enabled (1)** | |
| Quad-chute: `VT_FW_MIN_ALT` | Below this altitude in FW, switch to MC and run COM_QC_ACT | 0 (off) | 0–200 m |
| Quad-chute: `VT_QC_ALT_LOSS` | Uncommanded-descent threshold in FW | 0 (off) | 0–200 m |
| Quad-chute: `VT_FW_QC_P` / `VT_FW_QC_R` | Pitch / roll thresholds for quad-chute | 0 (off) | 0–180° |
| Quad-chute: `VT_FW_QC_HMAX` | Maximum height at which a quad-chute can trigger | 0 | m |

The PX4 docs also say to be ≥20 m AGL before transitioning, that the transition
should complete within 50–100 m, and to transition into wind (v1.17 page above).
PX4 output functions list **Motor 1–12** (https://docs.px4.io/main/en/config/actuators).
The docs checked did not state a geometry limit for 8 lift motors on a Standard
VTOL: —.

**Verdict:** both stacks support a quad- or octo-lift QuadPlane with stopped lift
motors. ArduPilot's docs explicitly list Octa / OctaQuad frame classes for
QuadPlane and a lift-motor thrust-loss handler (Q_THRST_LOSS_OPT). For an 8-lift
build, ArduPilot Plane 4.7.1 is the better-documented path.

---

## 2. Flight controllers

Output need: 8 lift + 1 pusher + 4–5 servos = **13–14 outputs** (octo), or
4 + 1 + 5 = **10** (quad).

| FC | Part / SKU | PWM outputs | ArduPilot | PX4 | Price | In stock | Ships from | Source (2026-10-13) | Meets ≥14? |
|---|---|---|---|---|---|---|---|---|---|
| **Holybro Pixhawk 6C** (plastic) | Pixhawk 6C | **16** (8 IO + 8 FMU). Only the FMU outputs do DShot; BDShot needs the "Pixhawk6C-bdshot" build | yes | yes | **$199.00** bare; $219.99 w/ PM06; $242.99 w/ PM07 | y | — (Holybro, China/HK) | https://holybro.com/products/pixhawk-6c ; https://docs.holybro.com/autopilot/pixhawk-6c/technical-specification ; https://ardupilot.org/plane/docs/common-holybro-pixhawk6C.html | **Yes** |
| Holybro Pixhawk 6C (aluminum) | Pixhawk 6C | 16 | yes | yes | $209.00 bare; $229.99 w/ PM06 | y | — | same | Yes |
| Holybro Pixhawk 6C Mini (Model A rev / Model B) | 6C Mini | **14** (8 IO + 6 FMU). No PWM 7/8 on FMU | yes | yes | $179.00 bare; $199.99 w/ PM06 | y (Model A legacy sold out) | — | https://holybro.com/products/pixhawk-6c-mini ; https://docs.holybro.com/autopilot/pixhawk-6c-mini/technical-specification | Exactly 14, no spare |
| CubePilot Cube Orange+ Standard Set (ADS-B carrier) | MPN HX4-06222 | **14** (8 IO + 6 FMU), per PX4 docs | yes | yes | **$451.00** | y (45) | — | https://irlock.com/products/cube-orange-plus-standard-set ; outputs: https://docs.px4.io/v1.16/en/flight_controller/cubepilot_cube_orange | Exactly 14 |
| Matek H7A3-WING | MATEKH7A3-Wing | **11** (all DShot-capable) | yes (4.6+) | **no** (ArduPilot only, per vendor) | $100.49 at ReadyMadeRC | **n (discontinued at that store)** | US (ReadyMadeRC) | https://www.mateksys.com/?portfolio=h7a3-wing ; https://www.readymaderc.com/products/details/86418-matek-h7a3-wing-flight-controller | No (quad only) |
| Matek H743-WING V3 | MATEKH743 | 13 incl. LED pad | yes | — | — (GetFPV returned 403). A UK retailer lists it as "Discontinued (2026)" | n | — | https://www.flyingtech.co.uk/product/matek-h743-wing-v3-ardupilot-flight-controller/ (search snippet, *unverified*) | No |
| CUAV (V5+/X7/7-Nano) | — | — | — | — | — | — | — | not checked | — |

**Pick:** Holybro Pixhawk 6C plastic bundled with the PM06 ($219.99), or the bare
board ($199) plus a separate high-current power module (§3.3). It has 16 outputs
(2 spare for octo), runs both stacks, and the aluminum case is not needed.

---

## 3. Sensors, power, links, Remote ID

### 3.1 GPS / compass

| Item | SKU | Compass | Price | In stock | Source (2026-10-13) |
|---|---|---|---|---|---|
| **Holybro M10 GPS, standard 10-pin (GPS1)** | 12093 | IST8308 | **$43.99** | y | https://holybro.com/products/m10-gps |
| Holybro M10 GPS, standard 10-pin | 12040 | IST8310 | $43.99 | y | same |
| Holybro M10 secondary (6-pin GPS2) | 12094 | IST8308 | $43.99 | y | same |

The page notes that IST8308 is supported on the Pixhawk 6C from PX4 1.16.0+, and
that "M10 V2" is now available. The guessed URL for the V2 page returned 404, so
its price is —. To use IST8310 with no firmware caveat, pick SKU 12040.

### 3.2 Airspeed sensor (digital, I2C)

| Item | SKU | Price | In stock | Source (2026-10-13) |
|---|---|---|---|---|
| **Holybro MS5525DSO + PT40 pitot** | 19010 | **$59.99** | y | https://holybro.com/products/digital-air-speed-sensor |
| Holybro MS5525DSO + PT60 pitot | 19011 | $77.99 | y | same |
| Holybro MS4525DO + PT60 pitot | 19008 | $71.99 | y | same |
| Holybro MS4525DO + PT40 | 19003 | $57.99 | **n** | same |
| Holybro DLVR (L10D/L20D) | — | — | — | listed in the comparison chart only |

### 3.3 Power module (6S–12S, high current)

| Item | Input | Current (PCB) | Price | In stock | Source (2026-10-13) |
|---|---|---|---|---|---|
| **Holybro DroneCAN PM08, 14S 200 A** | 7–60.9 V (2–14S) | **200 A continuous**, 400 A 1 s burst; senses up to 376 A | **$83.00** tinned wires / $85.00 XT90 | y | https://holybro.com/products/dronecan-pm08-power-module-14s-200a |
| Holybro PM06 V2 (14S) | 2–14S | 70 A continuous / 120 A burst. The pre-soldered XT60 + 12 AWG lead is only 30 A continuous | $20.99 | y (10S version sold out) | https://holybro.com/products/micro-power-module-pm06-v2 |
| Holybro PM02 V3 (12S) | 2–12S | 60 A continuous / 100 A burst (XT60 lead 30 A) | $18.99 | y | https://holybro.com/products/pm02-v3-12s-power-module |
| Holybro PM07 (14S) | 14S | — | $43.99 | — | https://holybro.com/collections/power-modules-pdbs (product page not opened) |
| Matek PM12S-3 | 12S | BEC board with a current-sensor *pass-through pad* only, not a sensor | $63.99 at Pyrodrone (search snippet, *unverified*) | — | https://pyrodrone.com/collections/all-inventory/products/matek-pm12s-3-power-module-12s-input-bec |
| Mauch | — | — | — | — | not checked |

The hover current at 8–15 kg comes from the propulsion research
(docs/research/lift-propulsion.md), not this file. If the whole-pack current
exceeds about 70 A, only the PM08 in this table has margin.

### 3.4 RC link

| Item | Price | In stock | Source (2026-10-13) |
|---|---|---|---|
| **RadioMaster Boxer (M2)** | from **$109.99** | listed available | https://radiomasterrc.com/collections/radio-controller |
| RadioMaster Pocket (M2) | from $59.99 | available | same |
| RadioMaster TX16S MK3 (ELRS / M2) | $199.99 | available | same |
| RadioMaster TX16S Mark II (Mode 2) | from $199.99 | available | same |
| RadioMaster Zorro (M2) | from $99.99 | available | same |
| **RadioMaster RP3 V2 Nano ELRS RX** (diversity) | **$19.99** sale ($22.99 regular) | no label | https://radiomasterrc.com/collections/receivers |
| RadioMaster RP4TD true-diversity ELRS RX | $24.99 | no label | same |
| RadioMaster ER8 2.4 GHz PWM RX | $34.99 | no label | same |

"M2" is not defined on the page. It is taken to mean Mode 2 (not verified).
RadioMaster ships from: —.

### 3.5 Telemetry

| Item | Price | In stock | Source (2026-10-13) |
|---|---|---|---|
| **Holybro SiK Telemetry Radio V3, 100 mW 915 MHz** (pair) | **$58.99** | y | https://holybro.com/products/sik-telemetry-radio-v3 |
| Holybro SiK V3, 500 mW 915 MHz | $62.99 | **n (discontinued)** | same |
| ELRS MAVLink mode (no extra hardware) | $0 | — | https://www.expresslrs.org/software/mavlink/ |

ELRS MAVLink notes: it needs TX/RX firmware ≥3.5.0 and TX Backpack ≥1.5.0, and
works only on **ESP-based** TX/RX (not STM32). It supports ArduPilot and PX4.
ArduPilot settings: SERIALx_PROTOCOL=2, 460 kbaud. The downlink is about
4,755 B/s at 2.4 GHz F1000, and the uplink is shared with RC. Whether the RP3 V2
is ESP-based is not stated on the receivers page: —.

### 3.6 Remote ID broadcast module

| Item | Price | FAA DoC status | In stock | Ships from | Source (2026-10-13) |
|---|---|---|---|---|---|
| **Dronetag Beacon** | **$149** (€139) | The vendor page lists "FAA (USA)" under Remote ID Compliant (ASTM F3411-22a). A secondary source dates the DoC to 15-Nov-2022 (https://www.droneblog.com/dronetag-mini-commercial-rid-unit-review/). **FAA record not verified** | — | — (Dronetag, Czech Republic). Sold through shop.dronetag.com | https://dronetag.com/products/beacon/ |
| Dronetag Mini | $329 at Advexure (search snippet only; the Advexure page returned 404, *unverified*) | DoC 28-Sep-2022 per a secondary source | — | — | droneblog link above |
| BlueMark db120 | — (no live page found; the 2022 launch price was 129 EUR ex-VAT) | Launch press release claims approval | — | — | https://bluemark.io/2022/11/remote-id-db120-add-on/ (not opened) |
| Holybro Remote ID | $19.99 / $29.59 w/ case | **Not an accepted DoC for DIY use.** The page says US integrators must do their own DoC submission, and the unit ships with no serial number | y | — | https://holybro.com/products/remote-id |
| CubePilot Cube ID | — | — | — | — | not checked |

The FAA DoC lookup at https://uasdoc.faa.gov/listDocs is a JavaScript app that
could not be read with the tools available, so DoC status could not be confirmed
from the FAA record. **The team must look up the module's serial number there
before buying.**

**Pick:** Dronetag Beacon, $149 (vendor page), with the FAA DoC check pending.

---

## 4. Test gear

### 4.1 Thrust stand (need 5–10 kgf)

| Item | Thrust / torque | Price | In stock | Ships from | Source (2026-10-13) |
|---|---|---|---|---|---|
| Tyto Robotics Series 1585 Thrust Stand Bundle | **5 kgf**, 2 Nm, 50 V, 55 A continuous | **$1,075.00** | **n** (the product page says "Out of Stock"; the store JSON says available) | — (made in Gatineau, QC, Canada) | https://www.tytorobotics.com/products/series-1580-test-stand-bundle ; https://www.tytorobotics.com/pages/series-1580-1585 |
| Tyto Series 1780 | 75 kgf | — | **discontinued** | — | https://www.tytorobotics.com/pages/series-1780 |
| Tyto Flight Stand 15 | 15 kgf, 8 Nm, 180 V, 150 A | quote only (—) | — | — | https://www.tytorobotics.com/pages/flight-stand-15 |
| **DIY: SparkFun TAL220 10 kg straight-bar load cell** | 10 kg | **$12.95** (SEN-13329) | y | US (SparkFun) | https://www.sparkfun.com/load-cell-10kg-straight-bar-tal220.html |
| **DIY: SparkFun HX711 load-cell amplifier** | — | **$4.95** (SEN-13879) | y | US | https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html |

The 1585 covers only 5 kgf, and it is 54% of the $2,000 budget (1075 / 2000).
**Pick DIY:** one 10 kg TAL220 for thrust and a second one on a lever arm for
torque. Parts: 2 × $12.95 + 2 × $4.95 = **$35.80** plus an Arduino you already
have and a frame (estimate, frame cost —). Use the WM150 below for V/A/W, and
calibrate with known weights.

### 4.2 Watt meter, LiPo safety, IR thermometer

| Item | Spec | Price | In stock | Source (2026-10-13) |
|---|---|---|---|---|
| **ToolkitRC WM150** watt meter / servo tester | 1–50 V (covers 12S), 150 A max | **$51.99** | y | https://pyrodrone.com/products/toolkitrc-wm150-advanced-watt-power-meter |
| **Bat-Safe LiPo charging safe box** (steel, vented) | 2 × 6S 5000 mAh (222 Wh) | **$89.99** | y ("only 2 left") | https://997rcraceway.com/products/bafbatsafe-bat-safe-lipo-battery-charging-safe-box |
| BetaFPV LiPo safety handbag (small, 165×90×120 mm) | — | $6.99 at RaceDayQuads (search snippet, *unverified*) | — | https://racedayquads.com/products/betafpv-lipo-safety-hand-bag |
| **Etekcity IR thermometer** (Amazon B00DMI632G, -58 to 1130 °F) | — | **$24.99** | y | https://www.amazon.com/dp/B00DMI632G |

A Bat-Safe rated for 2 × 6S 5000 mAh may be too small for 12S or large-capacity
packs. Size it once the battery choice is fixed (docs/research/pusher-battery-servo.md).

---

## 5. Compliance costs

| Item | Cost | Notes | Source (2026-10-13) |
|---|---|---|---|
| FAA registration (Part 107) | **$5 per drone**, valid 3 years | Register at FAA DroneZone. The aircraft must be < 55 lb | https://www.faa.gov/uas/getting_started/register_drone (WebFetch got 403; read with a browser user-agent via curl) |
| FAA registration (recreational exception) | **$5**, covers all drones, 3 years | | same |
| TRUST (recreational test) | **Free** | "All FAA-approved TRUST test administrators offer the test free." | https://www.faa.gov/uas/recreational_flyers/knowledge_test_updates (403 to WebFetch; read via curl) |
| Part 107 knowledge test (UAG) at PSI | **$175** | The PSI FAQ says "The price for an Airman Knowledge Test (AKT) is $175." The same page's side panel shows "PSI Exam Fee $96*, price may vary by location". Which exam that $96 applies to is not stated, so budget $175. Part 107 recurrent training is free online | https://faa.psiexams.com/FAA/login ; https://www.faa.gov/uas/commercial_operators/become_a_drone_pilot |
| AMA Full membership (adult) | **$89/yr** ($79 age 65+); $168 for 2 yr | **$2,500,000** personal liability, $25,000 medical AD&D, $1,000 fire/theft/vandalism. Required to fly models > 2 lb | https://www.modelaircraft.org/membership-options ; https://www.modelaircraft.org/join |
| AMA Youth (under 19) | **$20/yr**; $37 for 2 yr | $2,500,000 liability | same |
| AMA Park Pilot | $52/yr | $500,000 liability. **No aircraft > 2 lb** and no speeds > 60 mph, so it does not fit this aircraft | same |
| AMA Three-month trial | $23.95 for 3 months | $2,500,000 liability | same |
| AMA student/college tier | — (no student tier on either page) | | same |
| CA sales tax, **Berkeley** | **10.25%** | Statewide base 7.25% plus district taxes. Rates effective 1-Oct-2026 | CDTFA rate table https://www.cdtfa.ca.gov/taxes-and-fees/SalesTaxRates10-1-26.xlsx (linked from https://www.cdtfa.ca.gov/taxes-and-fees/sales-use-tax-rates.htm) |
| CA sales tax, Alameda County (unincorporated) | 10.25% | Alameda city is 10.75% | same |

---

## 6. Recommended avionics set (estimate, before tax and shipping)

| Item | Price | Source row |
|---|---|---|
| Pixhawk 6C (plastic) + PM06 bundle | $219.99 | §2 |
| PM08-CAN 200 A (only if pack current > ~70 A) | $83.00 | §3.3 |
| M10 GPS (12040, IST8310) | $43.99 | §3.1 |
| MS5525DSO + PT40 airspeed | $59.99 | §3.2 |
| RadioMaster Boxer + RP3 V2 receiver | $109.99 + $19.99 | §3.4 |
| SiK V3 915 MHz 100 mW (optional if using ELRS MAVLink) | $58.99 | §3.5 |
| Dronetag Beacon RID | $149.00 | §3.6 |
| **Subtotal, without PM08 / SiK** | **$602.95** | 219.99+43.99+59.99+109.99+19.99+149.00 |
| **Subtotal, with PM08 and SiK** | **$744.94** | 602.95 + 83.00 + 58.99 |
| With Berkeley tax (×1.1025) | $664.75 / $821.30 | 602.95×1.1025 ; 744.94×1.1025 |

| Test gear + fees | Price |
|---|---|
| DIY thrust stand electronics (2 load cells + 2 HX711) | $35.80 |
| WM150 watt meter | $51.99 |
| Bat-Safe box | $89.99 |
| IR thermometer | $24.99 |
| FAA registration | $5.00 |
| AMA Full × 1 (pilot of record) | $89.00 |
| Part 107 test × 1 (only if flying under Part 107) | $175.00 |

## What the team must measure / confirm

- **M1:** Look up the RID module's serial number in the FAA DoC system
  (uasdoc.faa.gov) before purchase. If it is not listed, flying outside a FRIA
  violates Part 89.
- **M2:** Peak whole-pack current in hover, from the propulsion analysis or a
  bench test with the WM150. If it is above 70 A continuous, the PM06 fails and
  the PM08 is needed.
- **M3:** Final output count (lift motors + pusher + servos). If it is above 14,
  only the Pixhawk 6C (16) works. If it is above 16, an extra I/O board is needed.
- **M4:** Calibrate the DIY thrust stand with known weights from 0 to 10 kg. If
  the error is above about 2% of full scale, the motor/prop data is not good
  enough to size the lift rotors (threshold is an estimate).
- **M5:** Confirm whether the team flies recreationally (TRUST + AMA,
  community-based org) or under Part 107. A university capstone may count as
  non-recreational. That decides whether the $175 Part 107 test is needed.
