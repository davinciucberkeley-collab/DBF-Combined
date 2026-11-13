# RC link, telemetry and ground station — K09-L

Status `PROPOSED`, revision F5-R2, 2026-11-10 (R2: `GND-001` declared in `subsystems/ground/`; 150 mm RX antennas, CR-F3-15). Owner F5. Numbers: `team/F5/rc_link.py` → `team/F5/claims.json`
(re-run: `python -I redesign/team/F5/rc_link.py`, then `python -I redesign/proofs/build_graph.py`). Verdict: one
2.4 GHz ExpressLRS link carries control and telemetry, the laptop GCS is wired (USB) only, and no extra radio is
bought; the only addition is a ~$6 pair of longer RX antennas. The modelled link margin is 21.6 dB at the 515 m VLOS limit, so the radio does not limit the operating
radius.

## Equipment (all new; all in the BOM except the antenna pair, CR-F5-11)

| Item | Choice | Key numbers | BOM line | Cost incl. tax | Status |
|---|---|---|---|---|---|
| Transmitter | RadioMaster Pocket, ELRS 2.4 GHz **FCC** version, internal module, EdgeTX | 25–250 mW; 2 × 18650; ≈ 330 g with cells | `R01` (`GND-001`, declared in `subsystems/ground/`) | $71.65 | `UNVERIFIED` (BOM names "Pocket Crush": I1 confirms same module) |
| TX cells | 2 × 18650 | charged in the radio by USB-C | `R02` | $27.00 | `PROPOSED` |
| Receiver | RadioMaster RP3 V2, **FCC** version, antenna diversity, TCXO | stock 2 × 65 mm T-antennas (UFL), replaced below; telemetry ≤ 100 mW; 5 V; CRSF; 4.6 g | `A03` (`AVN-003`) | $22.04 | `UNVERIFIED` (maker page 429; 3 retailers agree) |
| RX antennas | 2 × 150 mm U.FL 2.4 GHz T-antenna | stock 65 mm leads do not reach the hatch-top and nose tubes (CR-F3-15); +0.5 g inside avionics 45 g | new line (CR-F5-11) | ~$6 | `UNVERIFIED` (price estimate) |
| Telemetry radio | none: telemetry rides on ELRS (CRSF) | 37.5 Hz downlink | — | $0 | `PROPOSED` |
| Ground station | Mission Planner (Windows, free) on a team laptop, USB-C cable to the FC | setup, parameters, logs | — | $0 | `PROPOSED` |
| **Added spend** | | | | **~$6** (`CL-F5-ADDED-COST`) | `PROPOSED` |

Why no SiK 915 MHz pair (~$35–60): the pessimistic reserve is $312.99 against a $309 crash (D-57), so any
purchase over $3.99 fails `R-RESERVE`; even the ~$6 antennas need A1 to pull I1's first lever (borrow the soldering kit, +$94.82, CR-F5-12). Live GCS telemetry is a convenience; the DataFlash log (FC) and the EdgeTX SD
log (ground) carry everything flight test needs. Upgrade paths if A1 later frees money: (1) ELRS **MAVLink mode**
(ELRS ≥ 3.5, TX backpack ≥ 1.5, $0, but RC then enters by MAVLink and the Pocket backpack's Wi-Fi is
`UNVERIFIED`): try on the twin only, never first on K09-L; (2) a SiK pair on a free UART, `FS_GCS_ENABL 0`.

## Link settings

| Setting | Value | Unit | Why | Source |
|---|---|---|---|---|
| ELRS firmware, TX and RX | same major version 3.x, FCC domain | — | TX/RX must match; never LBT or an "unlocked" build | `T-F5-BENCH` |
| Packet rate | 150 | Hz | sensitivity −112 dBm (4 dB over 250 Hz), 6.7 ms frame | `ASM-F5-RATE`, `SRC-F5-ELRS-SIGNAL` |
| Telemetry ratio | 1:4 (37.5 Hz) | — | CRSF passthrough wants ≥ 25 Hz | `ASM-F5-RATE` |
| Switch mode | Wide | — | ch 5 every packet; ch 6–12 round robin | `CL-F5-SWITCH-LATENCY` |
| TX power | 100 fixed (dynamic off) | mW | logs comparable flight to flight; 250 mW kept in hand | `ASM-F5-POWER` |
| Binding phrase | team-chosen, **not in the repo** | — | brief: no secrets in files | — |
| Model match | on; K09-L and the twin have different model ids | — | the wrong EdgeTX model cannot fly the wrong aircraft | `T-F5-BENCH` |
| RX serial protocol | CRSF | — | RC + telemetry on one UART | `SRC-F5-AP-ELRS` |

## Channel map (EdgeTX model "K09L", AETR)

ELRS sends ch 5 (AUX1) as a 2-position bit in every packet: it is the arm channel and **cannot carry six flight
modes**. `K09L.param` puts the modes on ch 5 and arm on ch 8, so `CR-F5-01` asks F4 to swap them.

| Ch | Function | Switch (Pocket) | ArduPilot | Status |
|---|---|---|---|---|
| 1–4 | roll, pitch, throttle, yaw | sticks, mode 2 | `RCMAP_*` default | `PROPOSED` |
| 5 | arm / disarm | SA, 2-pos | `RC5_OPTION 153` (CR-F5-01) | `PROPOSED` |
| 6 | flight mode, 6 positions | SC up = Q modes, SC down = FW; SB selects 1 of 3 | `FLTMODE_CH 6` (CR-F5-01) | `PROPOSED` |
| 9 | emergency motor stop | SD, 2-pos | `RC9_OPTION 31` (F4) | `PROPOSED` |
| 7, 8, 10–12 | spare | — | `RCn_OPTION 0` | `PROPOSED` |

Mode outputs on ch 6 (ArduPilot band centres; confirm in Mission Planner radio calibration):

| Position | SC · SB | Mode | Pulse | EdgeTX output |
|---|---|---|---|---|
| 1 | up · up | QSTABILIZE | 1165 µs | −65 % |
| 2 | up · mid | QHOVER | 1295 µs | −40 % |
| 3 | up · down | QLOITER | 1425 µs | −15 % |
| 4 | down · up | FBWA (starts transition) | 1555 µs | +11 % |
| 5 | down · mid | CRUISE | 1685 µs | +36 % |
| 6 | down · down | RTL | 1815 µs | +62 % |

Pocket switch names are taken from the manual and are `UNVERIFIED` until the radio arrives.

## ArduPilot link parameters (F4 writes them into `K09L.param`)

| Parameter | Value | Why | Source |
|---|---|---|---|
| `SERIALn_PROTOCOL` (n = F3's DMA UART) | 23 (RCIN) | CRSF needs a full UART with DMA on F4 boards | `SRC-F5-AP-ELRS` |
| `RSSI_TYPE` | 3 | RSSI and LQ from the CRSF stream into the log | `SRC-F5-AP-ELRS` |
| `RC_OPTIONS` | 8448 (bit 8 passthrough telemetry + bit 13 420 kbaud ELRS) | Yaapu screen; ELRS baud | `SRC-F5-AP-ELRS` |
| `FS_GCS_ENABL` | 0 | no GCS link in flight; a USB unplug must not trigger anything | `R-FAILSAFES` |
| `THR_FAILSAFE`, `FS_SHORT_TIMEOUT`, `FS_LONG_TIMEOUT` | 1, 1.5 s, 5 s (F4 values kept) | CRSF stops frames on link loss → RC failsafe | `K09L.param` §10 |
| No other `SERIALn_PROTOCOL` = 10 | — | conflicts with CRSF passthrough | ArduPilot CRSF thread |

## Failsafe behaviour (link side; F4 owns the actions)

| Event | Receiver | ArduPilot (F4) | Time | Claim |
|---|---|---|---|---|
| Link lost | stops CRSF channel frames (no "hold" or "custom" outputs in CRSF) | Q modes: QLAND in place; FW: circle, RTL at 5 s, then QRTL (`Q_RTL_MODE 1`) | ≤ 2.5 s TX off → failsafe | `CL-F5-FS-TIME` `UNVERIFIED` |
| Link back | frames resume | pilot re-selects the mode switch to take control | — | `T-F5-FS-BENCH` |
| E-stop ch 9 | sent within one round-robin cycle | all motors off | ≤ 0.059 s link part vs 1 s | `CL-F5-SWITCH-LATENCY` |
| RX brown-out | RX reboots, ~1 s without frames | as link lost | — | CR-F5-02: RX on the FC 5 V rail, not the servo rail |
| TX on after RX powered | RX may not sync | refuse to fly | — | power-up order: **TX on before the pack plug** |
| Weak link | — | — | warn −102 dBm, critical −107 dBm on 1RSS; LQ warn < 90 % | `CL-F5-RSSI-WARN`, `-CRIT` |

## Link budget (100 mW, 150 Hz, 0 dBi each end, 16 dB implementation loss)

| Quantity | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design distance (500 m VLOS, 400 ft AGL) | 514.6 | m | `CL-F5-LINK-DIST` | `CHECKED` (geometry) |
| Path loss at 2 440 MHz | 94.4 | dB | `CALC-F5-LINK` | `CHECKED` |
| Received power | −90.4 | dBm | `CALC-F5-LINK` | `UNVERIFIED` (loss assumed) |
| Fade margin vs −112 dBm / required | 21.6 / 10 | dB | `CL-F5-LINK-MARGIN` | `UNVERIFIED` |
| Range at 0 dB margin | 6 175 | m | `CL-F5-LINK-RANGE-0DB` | `UNVERIFIED` |
| RX antenna clearance to carbon, pack, ESC leads (λ/4) | 31 | mm | `CL-F5-ANT-CLEAR` | `CHECKED` (calc) |
| EIRP at 250 mW, 2.15 dBi vs 36 dBm limit | 26.1 | dBm | `CL-F5-EIRP-MAX` | `UNVERIFIED` (FCC ID read on arrival) |

The 16 dB implementation loss (airframe 8, polarisation 3, body and multipath 5) is the weak link in this table;
the two-attitude ground check below measures it.

## Receiver installation (pod)

| Item | Rule | Owner |
|---|---|---|
| RX position | on the pod tray aft of the FC, ≥ 50 mm from the ESC/PDB power leads | F3, D2 |
| Antenna A | vertical (+z) through the hatch top, in a printed tube | D2 |
| Antenna B | along −x out of the pod nose, below the pitot boom | D2 |
| Antenna leads | two 150 mm U.FL T-antennas so each element starts beyond its tube end (CR-F3-15, CR-F5-11) | F3, I1 |
| Clearance | each 30 mm active element ≥ 31 mm from the CF spar, pack, power leads and GPS mast | `CL-F5-ANT-CLEAR` |
| Why two axes | the aircraft turns 90° at transition: one element stays useful in each attitude | `ASM-F5-LOSS` |
| Harness | `E-HRN-31` JST-GH 4-pin (5 V, GND, TX→RX, RX→TX), ≤ 150 mm, twisted, away from ESC leads | F2 |

## Ground station

| Task | Tool | When | Output |
|---|---|---|---|
| Install stable ArduPilot Plane, load `K09L.param` | Mission Planner over USB | bench | parameter diff saved under `subsystems/flight-software/` |
| Accel, compass, radio, ESC, airspeed calibration | Mission Planner | bench and field (compass) | calibration screenshots in the test log |
| Geofence polygon (H3 corners) | Mission Planner plan screen | before flight day 1 | `.fen` file in the repo |
| Live flight data | Pocket screen: Yaapu B&W script (`RC_OPTIONS` bit 8) showing distance and bearing to home, altitude, climb rate, groundspeed, flight mode, battery mAh used and link quality (LQ); fallback EdgeTX telemetry page (1RSS, RQly, Bat, Capa, FM, Alt, GSpd) plus distance to home (Dist; C-17, G-13, NASA CR-132423 p. 52, 54, `review/NASA-CR-132423-COMPLIANCE.md`) | every flight; fields checked at `T-F5-BENCH` | voice: mode, battery, link warnings |
| Ground log | EdgeTX SD logging at 10 Hz, switch-on with arm | every flight | `.csv` per flight |
| Aircraft log | DataFlash on the FC, downloaded over USB | after every flight | `.bin` per flight; RSSI msg (RSSI, RXLQ) |
| Log review | Mission Planner graphs or plot.ardupilot.org (UAVLogViewer) | after every flight | link plot for `T-F5-FLIGHT-LINK` |

## Range and failsafe test plan

| Id | Test | Set-up | Pass | Claim |
|---|---|---|---|---|
| `T-F5-BENCH` | arrival bench | FCC domain, matching ELRS 3.x, bind, model match, channel directions, ch 9 latency from log | all channels right; latency ≤ 1 s | `CL-F5-SWITCH-LATENCY` |
| `T-F5-FS-BENCH` | RC failsafe, props off, tied down | armed in QSTABILIZE, FBWA, CRUISE in turn; TX off | QLAND in Q modes; circle → RTL in FW; ≤ 2.5 s | `CL-F5-FS-TIME` → `R-FAILSAFES` |
| `T-F5-RANGE` (updates H1 `GT-14`) | ground range check | **25 mW** (Pocket minimum), 150 Hz; aircraft 1 m up on a stand, motors spinning props-off at 20 %; 100 m; 4 headings × 2 attitudes (hover and cruise) | LQ ≥ 0.9 and best of 1RSS/2RSS ≥ **−93.8 dBm** in every position (predicted −82.2) | `CL-F5-RC-RSSI-REQ`, `-PRED` → `R-RC-LINK` |
| Daily | short range check | first flight of each day, 25 mW, 100 m, one heading per attitude | LQ ≥ 0.9, no failsafe | `R-RC-LINK` |
| `T-F5-FLIGHT-LINK` | in-flight log review | every flight; fixed-wing tune flights reach the 250 m fence | LQ ≥ 0.9, RSSI ≥ −102 dBm at the farthest point | `CL-F5-LINK-MARGIN` |
| Later (H2 decides) | in-flight RC loss | QHOVER at 15 m over the pad after QLAND is proven; TX off 3 s | QLAND starts, pilot recovers on TX on | `R-FAILSAFES` |

The −93.8 dBm line: at 25 mW and 100 m, a 10 dB margin at 515 m and 100 mW needs
RSSI ≥ −112 + 10 + 20 log10(515/100) − 6 dB. A pass proves the margin with the real airframe losses.

## Legal frequencies and power (United States)

| Item | Rule | Our value | Status |
|---|---|---|---|
| RC band | 2 400–2 483.5 MHz ISM, 47 CFR 15.247, licence-free | ELRS FHSS 2.4 GHz | `UNVERIFIED` (FCC IDs on labels) |
| Conducted power | ≤ 1 W (30 dBm) | 100 mW fly, 250 mW max | `CHECKED` |
| EIRP | ≤ 36 dBm (6 dBi allowance) | 26.1 dBm max | `CL-F5-EIRP-MAX` |
| Firmware | stay inside the certified power; FCC domain; no amateur-radio or unlocked builds | ELRS 3.x FCC | `PROPOSED` |
| Other emitters | none: no video TX, no telemetry radio; GPS is receive-only | — | `PROPOSED` |
| Remote ID, registration, airspace | H3 (`R-LEGAL`); RFS is a FRIA, no module fitted | — | H3 |

## Ground subsystem declaration (`GND`)

| Item | Value | Status |
|---|---|---|
| Files | `subsystems/ground/interfaces.json`, `parts.csv`, `SPEC.md` (generated by `rc_link.py`) | `MODELLED` |
| Part | `GND-001` transmitter, `flight: false`, no `electrical` role, CG `null` | `PROPOSED` |
| Edge | `E-AVN-09` (`GND-001` → `AVN-003`, `CT-ELRS-RF`), owner avionics; `ground` acknowledges it | waits for F3 to move it out of `edges_pending` (CR-F5-13) |
| merge_check today | PASS, 0 errors; 1 transient WARN `one-sided E-AVN-09` (acknowledged, still pending in avionics) | `CHECKED` |
| merge_check with the edge promoted (simulated copy) | PASS, 0 errors; no `E-AVN-09`/`GND` warning | `CHECKED` |

## Open issues

| Issue | Effect | Closes with |
|---|---|---|
| Implementation loss 16 dB assumed | link margin and range-check prediction `UNVERIFIED` | `T-F5-RANGE` |
| ELRS link-loss time 1.0 s assumed | failsafe time 2.5 s `UNVERIFIED` | `T-F5-FS-BENCH` |
| BOM "Pocket Crush" vs Pocket ELRS manual | power range and switch names | I1 (CR-F5-06) |
| Flight-mode channel on ch 5 in `K09L.param` | modes unusable over ELRS | F4 (CR-F5-01) |
| Yaapu on the Pocket's 128 × 64 screen | fallback is the EdgeTX telemetry page | `T-F5-BENCH` |
