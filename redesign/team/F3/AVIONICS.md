# Avionics hardware (F3)

Status `PROPOSED`, revision F3-R3, 2026-11-10 (R3: harness and transport edges acknowledged, §5.1). Numbers come from `team/F3/avionics.py` (28 claims in
`team/F3/claims.json`) and `team/F3/avn_data.py` (CAD claims in `claims.avn_data.json`). Re-check: `python -I redesign/team/F3/avionics.py`, then
`python -I redesign/proofs/build_graph.py`. Nothing has been bench-tested yet.

**Verdict:** fly the **CoreWing F405 Wing APP V2**. It is already in the BOM and it has a stable ArduPilot Plane
4.7.2 build with QuadPlane. Use an **MS4525DO** airspeed sensor at 0x28 instead of the MS5525, which sits at 0x76,
the same address as the board's barometer on the board's only I2C bus. Use the **HGLRC M100-5883** GPS on the pod
mast, **tilted 45° toward the nose**. Mount the flight controller on gel pads. With the power board carried by F1 as `PWR-003`, the avionics
come to 36.5 g against a 45 g allocation. The board's servo BEC is too weak for F1 to drop the UBEC.

## 1. Flight controller

| Criterion | CoreWing F405 Wing APP V2 (**chosen**) | SpeedyBee F405 WING (fallback) | Matek F405-WING | Source |
|---|---|---|---|---|
| Stable Plane build | 4.7.2 OFFICIAL, 2026-10-13, `HAL_QUADPLANE_ENABLED` | stable folder present, 2026-10-13 | not checked | `SRC-F3-FW-COREWING`, `SRC-F3-AP-SPEEDYBEE` |
| Bi-directional DShot on outputs 1–4 | yes, documented (V2 only, **not the Mini**) | BIDIR in the hwdef on 1 and 4, not documented | no BIDIR | `SRC-F3-AP-COREWING`, hwdefs |
| IMUs | ICM42688 + BMI270 (two lanes) | ICM42605 (one) | MPU6000 / ICM42688 | hwdefs |
| Baro, I2C buses | SPL06 at 0x76, one bus | SPL06 at 0x76, one bus | BMP280/DPS310 at 0x76 | hwdefs |
| Current sensing | 90 A cont / 215 A peak, 64 A/V | 90 / 215 A, 50 A/V | 31.7 A/V | board pages |
| Servo BEC (continuous) | 8 A (page, listings) / **4.5 A (maker manual, carried)** | 4.5 A | — | `ASM-F3-BEC` |
| Lua scripting | **no** (1 MB flash) | no | no | features.txt |
| Size, mass | 52 × 32 × 17 mm, 40 g | 52 × 32 × 19 mm, 35 g | — | board pages |
| Price (BOM `A01`) | $67.26, ReadyMadeRC | $47.99, stock not verified | — | `team/I1/BOM.csv` |

Why the CoreWing: it is the only one of the three whose bdshot on outputs 1–4 is documented, it has a second IMU on
an aircraft where any fault is a crash, and its price is already inside the $321 reserve. The SpeedyBee would save
$19 but has one IMU and undocumented bdshot, so it stays the fallback for a stock-out. An H743 board would bring Lua
but adds about $35 and would take the reserve below the $309 crash case. Choose it only if F4 shows that Lua is
mandatory.

| Setting for F4 | Value | Basis |
|---|---|---|
| Firmware | Plane stable 4.7.x, target `CoreWingF405WingV2`, standard build. No `-bdshot` variant is needed | `CL-F3-FC-STABLE` |
| Output groups | 1–2 (TIM4) and 3–4 (TIM3) are motors, DShot300 bidirectional. 5–7 (TIM8) are PWM 50 Hz: elevons on 5 and 6, nothing on 7. 11–12 are PWM only | `CL-F3-BDSHOT-OUTS` |
| `AHRS_ORIENTATION` | 0: FC flat on the tray, arrow toward −x (the cruise nose), calibrated in the fixed-wing attitude | `SRC-F3-AP-TAILSITTER` |
| `INS_GYRO_RATE` | 0 (1 kHz). The 3P notch at the rpm cap is at 0.935 of Nyquist (F4) | F4 `CL-F4-NOTCH-TOP` |
| `INS_POS1/2_XYZ`, `GPS1_POS_XYZ` (FRD, from the CG) | (0.054, 0.046, −0.035), (−0.036, 0, −0.169) m | `CL-F3-INS-POS`, `CL-F3-GPS-POS` (CG 0.044; re-measure as built) |
| Serial | SERIAL5 = GPS (UART5, GPS connector). SERIAL6 = receiver (USART6, CRSF or MAVLink2 per F5). SERIAL1 = on-board wireless module, left as is | `SRC-F3-AP-COREWING` |
| Battery monitor | `BATT_MONITOR` 4, `BATT_VOLT_MULT` 11.05, `BATT_AMP_PERVLT` 64, then `T-F1-SENSOR-CAL` | `SRC-F3-AP-COREWING` |
| Airspeed | `ARSPD_TYPE` 1 (MS4525), `ARSPD_BUS` 0, `ARSPD_TUBE_ORDR` 2 (auto, so swapped tubes are harmless) | `CL-F3-I2C-CLASH` |
| Compass | external only, `COMPASS_AUTO_ROT` 2 during calibration; expect `COMPASS_ORIENT` 36 (Pitch315) with the 45° mast. Use large-vehicle mag cal (GPS yaw) | `ASM-F3-GPS-TILT` |

## 2. Sensors and the I²C map (one bus, I2C1)

| Device | Part | Address | Port | Status |
|---|---|---|---|---|
| Barometer (on board) | SPL06 | 0x76 | I2C1 | `CHECKED` (hwdef) |
| Compass (in the GPS) | QMC5883L / QMC5883P | 0x0D / 0x2C | I2C1 via the GPS connector | `UNVERIFIED` (chip not named by the seller) |
| Airspeed | **MS4525DO** (RMRC digital airspeed + pitot, $59.99) | 0x28 (driver also probes 0x36, 0x46) | I2C1, Y-split in the pod | `UNVERIFIED` (address read at `T-F3-I2C-SCAN`) |
| ~~Airspeed~~ | ~~Holybro MS5525~~ | ~~0x76~~ **clashes with the baro** | — | rejected (`CL-F3-I2C-CLASH-MS5525` = 1) |
| GPS | HGLRC M100-5883 (u-blox M10) | UART | SERIAL5 | `PROPOSED` |
| Receiver | RadioMaster RP3 V2 ELRS | UART | SERIAL6 | `PROPOSED` (F5 owns the link) |

The DLVR is not compiled into this F405 build, so it is not an option. The ASP5033 (0x6D) is compiled in and is
the fallback if the MS4525 fails its bench check. Keep the whole I²C bus under 0.5 m: about 0.25 m to the mast
plus 0.08 m to the airspeed sensor.

## 3. Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Unique I²C addresses (baro, compass, airspeed) | 3 of 3 | — | `CL-F3-I2C-CLASH` | `PROPOSED` |
| Field at the compass from pack and power currents, hover 30.3 A | 3.6 | µT | `CL-F3-COMPASS-B` | `UNVERIFIED` (loop areas) |
| Interference / Earth field, hover / at the 100 A limiter | 0.075 / 0.247 (limit 0.3) | — | `CL-F3-COMPASS-RATIO`, `-LIM` | `UNVERIFIED` (`T-F3-COMPASSMOT`) |
| Uncorrected heading error at hover | 8.7 | ° | `CL-F3-COMPASS-HDG` | `UNVERIFIED` |
| GPS to the nearest power item (ESC lead grooves) | 0.154 (min 0.10) | m | `CL-F3-GPS-CLEAR` | `PROPOSED` |
| GPS patch off-boresight to zenith, worst attitude: tilted / level | 45 / 90 | ° | `CL-F3-GPS-SKY` | `PROPOSED` (`T-F3-HDOP`) |
| Hover 1P / mount natural frequency | 89.9 / 35 | Hz | `CL-B4-HOVER-RPM`, `CL-F3-VIBE-FN` | `UNVERIFIED` |
| Mount transmissibility at 1P / 2P | 0.20 / 0.06 (limit 0.3) | — | `CL-F3-VIBE-T1P` | `UNVERIFIED` (`T-F3-VIBE`) |
| Airspeed error at 16 m/s, RSS / linear sum | 0.45 / 0.78 (limit 1.0) | m/s | `CL-F3-ASPD-ERR`, `-LIN` | `UNVERIFIED` |
| Airspeed resolution at 16 m/s (one count) | 0.054 | m/s | `CL-F3-ASPD-RES` | `PROPOSED` |
| 5 V load ×2 vs FC BEC | 0.87 vs 2.4 | A | `CL-F3-5V-REQ` | `UNVERIFIED` (`T-F3-5V`) |
| FC board dissipation (for E3) | 1.73 (E3 assumed 2.0) | W | `CL-F3-FC-DISS` | `UNVERIFIED` |
| Current sensing vs need | 90 / 215 vs 37.8 / 120 | A | `CL-F3-SENSE-CONT`, `-PEAK` | `PROPOSED` |
| Servo BEC vs F1 need | 4.5 vs 5.6: **FAIL** −20 % (UBEC stays, by design) | A | `CL-F3-SERVO-BEC` | `UNVERIFIED` |
| FC envelope on its mount, h × w × l | 13 × 32 × 52 (top board on 5 mm gel cubes) (≤ 28 × 36 × 56) | mm | `CL-F3-FC-H/-W/-L` | `PROPOSED` |
| Avionics mass vs allocation (CAD roll-up, F3-R2) | 36.48 vs 45 (+19 %) | g | `CL-F3-MASS`, `CL-F3-AVN-CAD-MASS` | `UNVERIFIED` (`EST`) |

Airspeed budget at 16 m/s: prop wash 0.27 m/s (B4 1.66 %), `ARSPD_RATIO` residual 0.32 m/s (2 %), zero drift
0.15 m/s (3 Pa), quantisation 0.03 m/s. The RSS meets B1's proposed 0.5 m/s (CR-B1-13) with 11 % to spare. The
linear sum does not. The ratio residual dominates, so calibrate before the first transition (`T-F3-ARSPD-CAL`).

## 4. Placement, vibration and EMI

| Item | Where (x, y, z m) | Mounting | Rule it meets |
|---|---|---|---|
| FC `AVN-001` | right channel, centre (−0.010, 0.046), tray top | 2 gel pads (Zeal class, 5 mm), no screws. Signal leads soldered as 100 mm pigtails with in-line JR connectors; no header pins | f_n ≈ 35 Hz: isolates 1P and 2P, above the < 10 Hz control band. Sits beside the pack, never its stop (CR-C5-07) |
| Baro (on the FC) | — | open-cell foam over the SPL06; FC out of the pod vent inlet jet | static pressure only |
| GPS + compass `AVN-002` | mast top (0.080, 0, 0.169) | foam tape on a 45° pad, arrow toward the nose; **no steel within 50 mm** (nylon or brass M3 on the mast) | 0.154 m from the nearest power item; ratio 0.075 |
| GPS cable | FC → mast | runs alone, crosses the pack and ESC leads at 90°, never alongside them | no coupling into I²C |
| Airspeed `AVN-004` | left channel front, behind the pitot socket | foam tape + 1 tie (drop the M2 bosses); short tubes | tube length ≤ 60 mm |
| Pitot boom `AVN-005` | tip (−0.185, −0.046, 0.045) | 6 mm OD keyed sleeve holding the bought pitot-static tube; barbed couplers at the root (CR-D7-06); ≤ 220 mm with fittings | B4 1.66 % wash at y 0; B4 re-runs at y −0.046 |
| Receiver `AVN-003` | left floor (D2) | foam tape. Antennas leave through the hatch, one along z and one along y, ends ≥ 30 mm from the spar and tubes and ≥ 60 mm from the GPS | carbon blocks 2.4 GHz |
| Telemetry | — | through ELRS (F5); no separate radio, no mass | — |
| microSD `AVN-007` | in the FC | 16–32 GB SDHC, FAT32 | logging (R-FC-STABLE) |

**EMI.** The pod path is twisted. The compass sees three sources: the pack's internal current loop (1.3 µT at hover),
the pod terminal loop (1.0 µT) and the four untwisted 5 mm-spaced ESC lead pairs in the wing grooves (1.3 µT).
Those pairs are the nearest source, at 0.154 m. If F2 changes the groove spacing or brings the grooves within
0.12 m of the mast, re-run the script. The UBEC is a switching supply: keep it ≥ 0.10 m from the mast (it is on
the left floor at 0.155 m) and keep its leads off the GPS cable.

**Tailsitter.** The aircraft arms, takes off and lands standing nose-up. A level GPS patch would point at the
horizon exactly when a fix and a heading matter most. The 45° tilt puts zenith 45° off boresight in both hover
and cruise.

## 5. Parts (for `subsystems/avionics/`)

| Id | Part | Qty | Mass g | Cost | Note |
|---|---|---|---|---|---|
| `AVN-001` | CoreWing F405 Wing APP V2, FC top board + wireless board (the power board is `PWR-003` on the PDB plate, CR-F3-13) | 1 | 12.0 `EST` | BOM `A01` $67.26 | order with the early electronics (~20 Nov) |
| `AVN-002` | HGLRC M100-5883 | 1 | 7.73 `EST` | `A02` $20.49 | — |
| `AVN-003` | RadioMaster RP3 V2 | 1 | 4.6 `EST` | `A03` $19.99 | F5 |
| `AVN-004` | RMRC digital airspeed (MS4525DO) + pitot lines | 1 | 4.51 `EST` | `A04` $59.99 (was MS5525, same price) | December order |
| `AVN-005` | Pitot boom: keyed sleeve, probe, 2 couplers (115 mm × Ø10 mm stowed) | 1 | 4.84 `EST` | in `A04` + consumables | plug-in field joint |
| `AVN-006` | Gel cubes, foam tape, ties, FC strap | 1 set | 2.4 `EST` | shop consumables | — |
| `AVN-007` | microSD 16–32 GB | 1 | 0.4 | team stock (else ≈ $6) | — |

Masses are the CAD roll-up written by `avn_data.py` to `subsystems/avionics/interfaces.json`: **36.48 g** total
(`CL-F3-AVN-CAD-MASS`, `CL-F3-MASS`), allocation 45 g asked (CR-F3-13 / -21). That file is the source of truth.

### 5.1 Edges other roles declare on avionics parts (acknowledged F3-R3, 2026-11-10)

Each row was checked against this document before it went into `acknowledges`. The radio edge `E-AVN-09` moved from
`edges_pending` to `edges` now that F5 declares `GND-001`.

| Edge | Owner | Avionics end | Checked against | Result |
|---|---|---|---|---|
| `E-HRN-22` | F2 | UBEC 6 V → FC servo rail | CR-F3-04, CR-F1-29: UBEC alone on the rail, Vx not on the link | `CHECKED` (paper); Vx pin location `UNVERIFIED` until `T-F3-ARRIVAL` |
| `E-HRN-23` | F2 | Power board GH-6 → FC: Vbat, current, 5 V, GND | `BATT_MONITOR` 4, 0.87 A on 5 V (`CL-F3-5V-REQ`) | `CHECKED` |
| `E-HRN-24`…`27` | F2 | Outputs 1–4 → ESCs LR, UL, LL, UR, DShot300 bidirectional | `CL-F3-BDSHOT-OUTS` (TIM4 1–2, TIM3 3–4); F4 `motor_map` | `CHECKED` (map `UNVERIFIED` until `T-F4-BENCH-MAP`) |
| `E-HRN-28`, `29` | F2 | Outputs 5, 6 → elevons L, R, PWM 50 Hz | TIM8 group 5–7, nothing on 7 | `CHECKED` |
| `E-HRN-30` | F2 | GPS: SERIAL5 + I2C1, compass 0x0D / 0x2C | §2 I²C map | `CHECKED` |
| `E-HRN-31` | F2 | RX: SERIAL6 CRSF 420 kbaud | §1 serial map | `CHECKED` |
| `E-HRN-32` | F2 | Airspeed: Y-branch of I2C1, 0x28 | §2; bus total 0.461 m ≤ 0.5 m (`CL-F2-I2C-LEN`, +8 %) | `CHECKED` |
| `E-TRN-21` | D7 | Pitot boom stowed in the 220 × 25 × 25 mm tray slot | boom 0.115 m × 10 mm (`CL-F3-BOOM-STOW-L` +48 %, `-W` +60 %) | `MODELLED` |

One condition is still open on arrival. If the CoreWing output pads and Vx sit on the power board rather than on the FC
top board, `E-HRN-22` and `-24`…`-29` end on `PWR-003` and F2 re-routes. `T-F3-ARRIVAL` now checks this (CR-F1-29).

## 6. Open issues

| Issue | Owner | Status |
|---|---|---|
| Servo BEC continuous rating: 8 A (page) vs 4.5 A (manual). The UBEC stays until `T-F1-SERVO-STALL` | F1, F3 | `UNVERIFIED` |
| Avionics mass: closed by D-48 (36.48 g CAD vs 45 g after the stack split) | A1, A3 | closed |
| CoreWing hole pattern and power-board layout (one stack or two boards) not published: measure on arrival before D2 prints | F3, D2 | open |
| No Lua on F405: F4's Lua fallbacks (CR-F4-02, -06) are not available | F4 | `PROPOSED` |
| Compass loop areas and the Earth field are estimates; compassmot decides | F3, H1 | `UNVERIFIED` |
| RMRC sensor chip and address are not listed; `T-F3-I2C-SCAN` on arrival, ASP5033 fallback | F3 | `UNVERIFIED` |
| CG target moved (B3 0.0526 m vs params 0.044); INS/GPS offsets are re-measured as built anyway | A1 | open |

## 7. How to verify

| Test | What passes | Claims |
|---|---|---|
| `T-F3-FW-LOAD` | stable .apj flashed; `Q_TAILSIT_ENABLE` appears after `Q_ENABLE` 1; rpm telemetry on all four ESCs; log on SD | `CL-F3-FC-STABLE`, `-BDSHOT-OUTS` |
| `T-F3-I2C-SCAN` | SPL06, QMC5883 and MS4525 detected; airspeed rises on a blow, baro does not jump | `CL-F3-I2C-CLASH` |
| `T-F3-5V` | 5 V rail ≤ 1.2 A with everything on; board loss ≤ 2.0 W | `CL-F3-5V-REQ`, `CL-F3-FC-DISS` |
| `T-F3-COMPASSMOT` | interference ≤ 30 % at hover throttle | `CL-F3-COMPASS-RATIO` |
| `T-F3-HDOP` | standing on the fin tips at RFS: HDOP ≤ 1.2 within 3 min | `CL-F3-GPS-SKY` |
| `T-F3-VIBE` | tethered hover: VIBE < 30 m/s², clip 0; FFT 1P peak lower than with a hard mount | `CL-F3-VIBE-T1P`, `-FN` |
| `T-F3-ARSPD-CAL` | after `ARSPD_AUTOCAL`, reciprocal legs at 16 m/s within the requirement | `CL-F3-ASPD-ERR` |
