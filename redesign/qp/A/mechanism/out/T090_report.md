# T-090 Order 1 rebuild (2026-11-22)

Category: cost accounting (no engineering analysis). Plan only: nothing bought, no cart, no account.

## Method
`T090_data/build_order1.py` (`python -I build_order1.py`, output `T090_data/run_output.txt`) selects BOM-A.csv ids by the scope below, copies id, qty, unit price, vendor (ship group), status, date checked and URL unchanged, and computes the subtotal with the `bom_a.py` rules: tax 10.25 % on goods, shipping per distinct ship group (RMRC, Amazon, Local = $0, RDQ = $10.71 EST in `bom_a.py`). FAA $5 and the crash reserve stay with the main order.

Scope (SCHEDULE-A.md O1, TEST-PLAN-O4B s0/s1 and the T-083c re-spec): everything TP-1 (bench thrust / derate / current, one X2216 + APC 9x4.5MR, K-type probe, load cell, watt meter, laptop logger) and TP-2 (Lua cap, 72 A limiter, current sensor on the H743-Wing, 4 motors, XT90) need, plus concept-neutral power and avionics, plus stock-risk lines. No tubes, servos, foam or anemometer: no TP due before 2026-12-15 uses them.

## Result
| Item | $ |
|---|---|
| Goods (21 lines) | 795.05 |
| Tax 10.25 % | 81.49 |
| Shipping EST (RDQ only, per bom_a.py) | 10.71 |
| **Order 1 total** | **887.25** |
| Remaining main order (goods 587.36 x 1.1025 + ship 52.41 + FAA 5.00 + crash reserve 346.94) | 1,051.92 |
| Order 1 + main | 1,939.17 |
| BOM total (`python -I bom_a.py`) | 1,939.17 (margin +60.83) |

Reconcile PASS (script check, exact to the cent). Caveats: (1) the model charges $0 RMRC shipping, so splitting RMRC lines across two orders adds nothing here; the real RMRC rate is not readable ("—"). (2) Unverified (EST) goods in Order 1: W06, G02, G03, B03 = $93.15. (3) P01 motors are on BACKORDER (RMRC, availability Nov 2026, page read 2026-11-22); lead time after ordering "—". The 1-4 Dec order date therefore carries stock risk on the whole bench.

History: the earlier file (T-Motor MN2212 plan, $967.90 with 2 motors, $1,123.02 with 5) is withdrawn; no MN2212 line remains.

## Line-by-line rationale
| Order id | BOM id | Item (short) | Qty | Unit $ | Why |
|---|---|---|---|---|---|
| O1-01 | P01 | SunnySky X2216 V3 880KV SHORT shaft (4 with no BOM spare per | 4 | 22.99 | TP-1 (1 motor on the stand), TP-2 (4-motor limiter run); stock risk: RMRC BACKORDER (availability Nov 2026, read 2026-11-22), no spare (AM-019) |
| O1-02 | P02 | APC 9x4.5MR 4-pack (2 x 9x4.5MR standard rotation + 2 x 9x4. | 1 | 9.40 | TP-1 (MR + MRP on the stand), TP-2 (4 props); in stock, no spare (D-183) |
| O1-03 | P04 | SpeedyBee BLS 35A Mini V2 4-in-1 ESC 20x20 (DShot300/600; 7. | 1 | 45.66 | TP-2 needs 4 ESC channels on the stand; single-source 4-in-1; bidirectional-DShot rpm check (UNVERIFIED) is a TP-1 option |
| O1-04 | W01 | RDQ 2800 mAh 4S 100C XT60 270 g (2 flight packs; O4b) | 2 | 54.99 | TP-1 fresh-pack and 14.9 V sweeps, TP-2 voltage cap; 2 packs; order only after the CAD tray fit (TEST-PLAN-O4B T-082 note) |
| O1-05 | W02 | ToolkitRC M6AC charger | 1 | 63.71 | charges / part-discharges the packs to 14.9 V resting for TP-1 and TP-2 |
| O1-06 | W03 | TBS LiPo bag | 2 | 7.61 | LiPo safety for the 2 packs before first charge |
| O1-07 | W04 | Metal ammo can (pack storage) | 1 | 13.99 | LiPo storage before the first charge |
| O1-08 | W05 | Wire 14 AWG silicone (2 m red + 2 m black), XT60 5-pair, hea | 1 | 19.94 | 14 AWG leads, XT60, heat-shrink: stand power wiring for TP-1 and TP-2 |
| O1-09 | W06 | Threadlocker | 1 | 6.00 | motor-stand / ESC hardware (unverified EST, local) |
| O1-10 | W07 | Wire 20 AWG silicone (4 m red + 4 m black): phase-lead exten | 2 | 3.96 | phase-lead extensions: X2216 stock leads are only 100 mm, the 4-motor stand needs the extensions |
| O1-11 | W10 | XT90 male + female pigtails, 12 AWG 10 cm, 3 pairs (aircraft | 1 | 12.99 | TP-2 pass line names XT90 (90 A = 1.25 x 72 A); the 72 A limiter run needs it |
| O1-12 | V01 | Radiomaster Pocket ELRS TX | 1 | 76.99 | TX to command throttle and trigger the failsafe on the FC in TP-2 (concept-neutral) |
| O1-13 | V02 | Radiomaster RP3 V2 ELRS RX | 1 | 23.08 | RX paired with V01 for TP-2 (concept-neutral) |
| O1-14 | V03 | Holybro Kakute H743-Wing FC (Lua-capable; replaces V03 F405  | 1 | 129.01 | TP-2 runs on the real H743-Wing (Lua cap, 72 A limiter, current sensor range read before the order) |
| O1-15 | V04 | TBS M10Q GPS + QMC5883 compass (13.5 g; replaces Foxeer M10Q | 1 | 19.76 | stock risk (Foxeer backordered); not needed by TP-1/TP-2; ships in the same RMRC group |
| O1-16 | G01 | ToolkitRC WM150 watt meter | 1 | 35.31 | TP-1 bus current and voltage logging |
| O1-17 | G02 | Load cell + HX711, IR thermometer, 0.1 g scale, caliper, kni | 1 | 45.15 | TP-1 thrust cell + HX711, scale, IR thermometer, caliper (Amazon lines, EST) |
| O1-18 | G03 | Thrust-stand + hanging yaw-rig parts (wood and hardware) | 1 | 25.00 | TP-1 / TP-2 thrust stand (wood and hardware, EST) |
| O1-19 | B03 | 1 kgf bar cell + HX711 (+K-type probes) for the yaw-torque a | 1 | 17.00 | TP-1 K-type probes for the H-1 motor-base temperature (EST; the 1 kgf cell part is the yaw rig, not needed before 15 Dec) |
| O1-20 | T9 | Nano V3 clone ATmega328P USB-C (HX711 logger) | 1 | 13.99 | TP-1 HX711 logger to the laptop |
| O1-21 | R03 | PETG 1.75 mm 1 kg (ELEGOO, black; printed cage, mounts, foot | 1 | 12.99 | PETG for the stand motor mount prints (TP-1 base temperature is on a PETG base); Jacobs prints before 18 Dec |

## Deferred to the main order, and why
V05 airspeed sensor (no TP before 15 Dec; moving it into Order 1 adds $66.14 incl. tax, no shipping change), W08 strap and W09 pad (tray, after CAD tray fit), M01 / M02 servos and linkage, R01 foam, R02 / R08 / R09 / R10 / R14 / R15 tubes and rod, R05 fasteners (motor ships with X-mount screws), R06 / R07 / R11 / R12 / R13, G04 foam planform, G05 anemometer, B04 bench fixture (yaw rig, not TP-1/TP-2), T1 / T11 Zoro bars, T2 to T8, T10 lever rig (TP-4+), T12. All have no use in TP-1 or TP-2.

## Open items
- H743-Wing current-sensor range is "—" (TEST-PLAN-O4B TP-2: read before ordering).
- W01 order only after the CAD tray fit.
- No rpm sensor in the list (audio FFT / ESC telemetry per TP-1; none priced).
