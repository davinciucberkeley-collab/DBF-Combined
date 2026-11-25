# T-074 checks 1 and 2 (O4b feasibility: scheduled spin cap, pack >= 2,350 mAh), 2026-11-19

Research only, $0, nothing bought, no accounts. All web pages read 2026-11-19 (WebFetch / curl). `—` = not read. Scratch G7 run was done on a copy of `bom_a.py` + `BOM-A.csv` in a temp folder; `BOM-A.csv` is unedited.

## Verdicts

| Check | Verdict |
|---|---|
| 1. Lua scheduled cap runs on the A flight controller | **FAIL** for the Kakute F405 Wing Mini (no Lua on F4 or in the 1 MB build). No parameter-only route holds one motor at or below 12.1 A. The cheapest fitting H7 FC (RMRC Kakute H743-Wing, $141.44) breaks G7 (total $1,829.59 > $1,800; +30 % margin +$49.93 < $100). |
| 2. In-stock 4S pack >= 2,350 mAh, <= 275 g | **PASS, conditional.** One candidate fits the tray and the mass limit: GNB 2800 mAh (267 g, 107 x 34 x 37 mm, XT60, 100C). It is in stock only at a EU retailer (read today); US stock is not confirmed. One more candidate fits on mass but is out of stock. A third fails on length. |

## Check 1: Lua on the Kakute F405 Wing Mini

### 1a. Findings

1. ArduPilot scripting page (https://ardupilot.org/plane/docs/common-lua-scripts.html, read 2026-11-19): requires "at least 2 MB of flash" and 80 kB RAM; "Scripting is not available on F4-based autopilots". The Wing Mini is an STM32F405 with 1 MB flash (Holybro docs, https://docs.holybro.com/autopilot/kakute-f405-wing-mini/overview, read 2026-11-19; also RMRC page, `87184-holybro-kakute-f405-wing-mini-flight-controller`, $95.98, In Stock, 25 x 30 x 20 mm, 20 x 20 mm M2 pattern, 17 g, read 2026-11-19).
2. ArduPilot hwdef for the Kakute F4-Wing target (the F4 Wing family; the Wing Mini's own target name is not stated on the Holybro page, so the match to this target is an assumption): `FLASH_SIZE_KB 1024`, `MCU STM32F4xx STM32F405xx`, `include ../include/minimize_fpv_osd.inc` ("minimal drivers to reduce flash usage") (https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_HAL_ChibiOS/hwdef/KakuteF4-Wing, hwdef.dat read 2026-11-19).
3. Firmware server feature list for the same target, Copter latest (https://firmware.ardupilot.org/Copter/latest/KakuteF4-Wing/features.txt, read 2026-11-19): `!AP_SCRIPTING_LUA_ENABLED`, `!AP_SCRIPTING_BINDING_MOTORS_ENABLED`, `!AP_SCRIPTING_BINDING_VEHICLE_ENABLED`, `!AP_SCRIPTING_SERIALDEVICE_ENABLED` (the `!` means not built in). The KakuteH7-Wing and MatekH743 targets list the same lines without `!`.
4. ArduPilot limited-firmware page (https://ardupilot.org/copter/docs/common-limited-firmware.html, read 2026-11-19): 1 MB boards get a reduced build; a custom build is the only route to a removed feature. Another board's forum thread (search result, 2026-11-19, not opened) reports an F405 custom Lua build that ran out of RAM (192 kB). So a custom build is not a credible route.

Conclusion: the Wing Mini cannot run the O4b Lua script with stock firmware, and a custom build is not credible.

### 1b. Parameter-only alternative (no Lua)

Source: ArduPilot `libraries/AP_Motors/AP_MotorsMulticopter.cpp` and `AP_Motors_Thrust_Linearization.cpp`, master, read 2026-11-19 (https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Motors/AP_MotorsMulticopter.cpp). In Plane QuadPlane these are the `Q_M_` parameters.

| Parameter | What it does | Holds one motor at or below 12.1 A? |
|---|---|---|
| `Q_M_SPIN_MAX` | Fixed fraction of output range. This is the present 0.90. | Only at one voltage. This is the cap O4b replaces. |
| `Q_M_BAT_VOLT_MAX` / `Q_M_BAT_VOLT_MIN` | Voltage compensation: output is scaled by `1 / (V / V_max)` so a thrust command gives the same thrust at any voltage. In `AP_Motors_Thrust_Linearization.cpp`, `lift_max` and the battery scale rescale the command. The actuator is still clamped to `spin_max` (`constrain_float(_actuator, spin_min, spin_max)`, line 528 of the motors file). | No. It lowers duty for a given thrust at high voltage but does not lower the maximum duty. A full-thrust command still reaches `SPIN_MAX`. |
| `Q_M_BAT_CURR_MAX` + `Q_M_BAT_CURR_TC` | Limits total battery current. An integrator reduces the throttle headroom above hover (`get_throttle_hover() + (1 - hover) * throttle_limit`) when measured pack current exceeds the limit. Needs pack resistance and a current monitor. | No. It limits the sum over four motors, not one motor, and acts through a time constant (a slow integrator, not a peak limit). Hover is about 5.9 A per motor at 1.639 kg (`prop_a.hover`, fresh pack, derate 0.93, run today), about 23.6 A total. A limit that lets one saturated motor reach 12.1 A with three at hover is about 12.1 + 3 x 5.9 = 29.8 A total. With four motors saturated that is about 7.4 A each, only 1.26 x the hover current (about T/W 1.3), far below A-P2 (T/W 2.0 or more). |

Conclusion: no parameter-only solution. Check 1 does not pass without an FC change.

### 1c. In-stock Lua-capable H7 wing-style FCs against the A bay

A bay (from `redesign/qp/A/cad/amodel/electrical.py` and `common.py`): FC stack 30 x 25 x 20 mm (FC_B), 20 x 20 mm M2 pattern, FC at x 45..75 mm hard-mounted on the spar centre; cover half-width 26.5 mm (53 mm inside), roof 45.0 mm over x 40..80 mm and 32.5 mm aft of x 83.3 mm; plate x 40.8..127.0 mm, half-width 55 mm. The Kakute stack includes a power board with BEC (the CAD pads "ESC", S5, S6, GPS, I2C, RX are on it).

| Option | Price / stock as read 2026-11-19 | Dimensions, mass | Lua | Fit to A bay |
|---|---|---|---|---|
| **Holybro Kakute H743-Wing** (ArduPilot target KakuteH7-Wing) | RMRC $141.44, In stock (https://www.readymaderc.com/products/details/87185-holybro-kakute-h743-wing-flight-controller). Holybro store lists $105.00, stock not read (429 error). | 45 x 30 x 13.5 mm, 28 g with USB board, 25 x 25 mm M2 pattern; 2 MB flash, 1 MB RAM (https://docs.holybro.com/autopilot/kakute-h743-wing/overview). Servo BEC 6 V (8 V by jumper), 6 A / 8 A peak; 90 A current sensor. | Yes (`AP_SCRIPTING_LUA_ENABLED` in features.txt, 2026-11-19) | Envelope fits: 13.5 mm tall under a 32.5 to 45 mm roof, 30 mm wide inside 53 mm. It needs new M2 holes (25 x 25, not 20 x 20), the 45 mm length runs x 45 to 90 mm across the roof step at x 83 mm and the ESC pads, and the harness changes. Mass +11 g (28 vs 17 g). BEC: 6 V / 8 V against the Wing Mini 5.3 V / 7.2 V, so the servo rail must be checked against the ES3054HV rating (not read). |
| Matek H743-Wing V3 | RMRC page (matek-h743-wing-flight-controller) $121.95, **Discontinued** | 54 x 36 x 13 mm, 30 g, 30.5 x 30.5 mm pattern | Yes (MatekH743 target) | 54 mm long and a 30.5 mm pattern: does not fit the 20 x 20 / 25 mm bay without a larger plate. Not buyable at RMRC. |
| Matek H743-WLITE | Prices "$29.99 / $96.99 / US$90" in search snippets (Pyro Drone, Team BlackSheep), one page marked discontinued; GetFPV and Pyro pages not readable (403, 429). Stock — | 44 x 29 x 14.5 mm, 22 g, 25 x 25 mm (search snippet, FPVFaster, not opened) | Yes | Fits better than the Holybro (smaller, lighter), but it has a 2 to 6 S input and no 7.2 V servo BEC read. Price and stock — (not read). Not used for G7. |

The cheapest option with a price and stock read on a page, and one that fits, is the Kakute H743-Wing at RMRC. RMRC is already a ship group (no new shipping).

### 1d. G7 scratch run (copy of `bom_a.py` and `BOM-A.csv`, V03 changed from $95.98 to $141.44, nothing else)

| Item | Baseline (BOM-A.csv) | With H743-Wing |
|---|---|---|
| Goods | 1,262.50 | 1,307.96 |
| Spend | 1,452.04 | 1,502.16 |
| Total | 1,779.47 | **1,829.59** |
| Margin | 220.53 | 170.41 |
| +30 % margin | +100.05 | **+49.93** |
| G7 (+30 % margin >= $100 and total <= $1,800) | PASS by $0.05 | **FAIL** |

The Kakute swap adds $50.12 of spend ($45.46 x 1.1025, V03 is a verified line so the +30 % bump does not scale it). To pass G7 again: total must drop by $29.59 and the +30 % margin must rise by $50.07, so about $50.1 must come out of the BOM (the crash reserve of $327.43 is the only large line). The O4b pack (check 2) is not included in this run: its price in USD is — (the GNB price read was in EUR).

Check 1: **FAIL** (Wing Mini: no Lua, no parameter solution; the cheapest fitting H7 FC fails G7 by $29.59 on total and $50.07 on margin, before any pack change).

## Check 2: 4S pack >= 2,350 mAh and <= 275 g

### 2a. Requirement and the A tray

- Needed C: A-P16 peak is one motor at 12.1 A with three at hover. Worst sum is 4 x 12.1 = 48.4 A (all four at 12.1 A, which is above the repo's 10.75 A all-four sag case). At 2.8 Ah that is 17.3C; at 2.35 Ah it is 20.6C. Any 30C or higher pack meets it; 75C and 100C packs carry large margin.
- Tray (from `wing.py` 843 to 850 and `electrical.py` 534): plate 109 mm along the pack length (y +-54.5 mm); lead notch; integral 2 mm lips at the trim ends; the current Tattu 2300 is 105 x 35 x 29 mm (RMRC, read 2026-11-15) and spans x -27.5 to +7.5 mm (35 mm) with +-10 mm trim. So a pack must be at most about 107 mm long (plate 109 mm), about 35 mm wide in x (up to about 55 mm only by giving up the trim travel and moving the lips), and about 29 mm high (a height limit under the strap and bay cover is not stated in the CAD: —). Strap 20 mm wide; pad 100 x 30 mm.
- Mass: 275 g from O4b (`docs/audits/2026-11-19-O4-feasibility.md`).

### 2b. Candidates

| # | Pack | Price / stock as read | Mass | Dimensions L x W x H | C | Connector | Fit |
|---|---|---|---|---|---|---|---|
| 1 | **GNB 2800 mAh 4S 100C** | Rotorama (EU) EUR 41.29, **in stock**, read 2026-11-19 (https://www.rotorama.com/product/gnb-2800mah-4s-100c). KiwiQuads (NZ) page read 2026-11-19: $74.99, **out of stock** (https://www.kiwiquads.co.nz/product/gnb-battery-14-8v-100c-2800mah-4s/). | 267 g (+- 8 g on KiwiQuads); 267 g on Rotorama | 107 x 34 x 37 mm (both pages) | 100C continuous (Rotorama text also says 120C once) | XT60 (+ JST-XH balance) | Length 107 mm fits the 109 mm plate (2 mm clearance, with the lead notch EST); width 34 mm fits; height 37 mm is 8 mm above the Tattu (29 mm), so the strap routing and any bay roof are to be checked (—). At +8 g tolerance it is 275 g: at the limit. |
| 2 | **RDQ Series 2800 mAh 4S 100C** (Race Day Quads) | GetFPV listing: out of stock (search result 2026-11-19; page itself not readable, 403). Race Day Quads page 429 on both tries, so stock and price —. | 270 g (+- 1 %) (search snippets: Race Day Quads, GetFPV) | 107 x 33 x 46 mm (Race Day Quads); GetFPV states 107 x 46 x 33 | 100C | XT60 (80 mm lead) | If the 46 mm side is the width (x), it is 11 mm wider than the 35 mm slot and needs the lips moved (trim travel lost); if it is the height it is 17 mm taller than the Tattu. Marginal either way; stock not confirmed. |
| 3 | Turnigy Nano-Tech 4S 2800 mAh 70C (HobbyKing) | Page returned 403; figures are from a search snippet only (2026-11-19): price and stock — | 275 g | 141 x 43 x 22 mm | 70C | XT60 | **Fails**: 141 mm is 32 mm longer than the 109 mm plate. |

Also seen and rejected: CNHL 2700 mAh 40C (about 320 g, over the limit); Tattu 3200 mAh 45C (136 x 44 x 29 mm, 136 mm long: too long; mass not read); CNHL Black 2000 mAh (about 232 to 234 g, below 2,350 mAh); Tattu 2300 mAh 75C at RMRC (270 g, 2,300 mAh: below the 2,350 mAh need, but it is the current pack).

Check 2: **PASS, conditional.** Candidate 1 meets capacity (2,800 mAh), mass (267 g), C (100C against 17.3C needed) and connector (XT60) and has a read dimension match for the tray footprint; it is in stock only at a EU retailer (ship from EU: a lithium-battery shipping restriction and the cost are — and not read; GetFPV states that it cannot ship LiPo by air). Height (37 mm) and the 275 g tolerance are open. A US in-stock source was not found today.

## Not done

- The Holybro store, GetFPV, Pyro Drone and HobbyKing pages were not readable (403, 429) so those prices and stocks are —.
- The O4b pack price in USD, shipping and tax were not put into G7.
- The H743-Wing servo BEC against the ES3054HV rating, and the CAD pad positions, are not checked.
