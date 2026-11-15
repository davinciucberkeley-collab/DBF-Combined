# DESIGN-TO-COST: K09-L under $2,000, all new (I1)

Date 2026-11-14. Owner I1. Reproduce: `python -I team/I1/design_to_cost.py` (reads `team/I1/BOM.csv`, writes nothing). No design file, `params.json`, gate or git touched.
Labels: `EST` estimate; `UNVERIFIED` price from a search snippet or aggregator, vendor page not read; `—` not found. Prices checked 2026-11-14.

## 0. Verdict

**No credible path closes at $2,000 under the user's rules.** The full parts-only path (section 5, ordered by risk) ends at **$2,577** (gap **$577**). Adding the only architecture change that moves the needle (3S packs, `EST` -$282) reaches about **$2,295** (gap about $295) and reopens nearly every engineering role with a likely T/W failure. The smallest gap I can defend is about **$300-$580 depending on the 3S decision**.

Why the number is larger than the "about $2,450" in the brief: that figure is the spend with the X14 tools excluded (the model gives $2,453.10 for that case). The user rules also count tools (+$378.92) and a crash reserve that includes a fin tube when no spare tube is carried (+$347.39).

The two models differ, so numbers must not be mixed: `bom_summary.json` / I1.md uses 16 shipments, owned-item columns and a $130 crash line ($2,259 spend). This script uses every distinct vendor shipment ($10.71 x 23) and the crash rule below. Use one model; this file uses the script's.

## 1. Honest baseline (script model)

Applied: airspeed sensor A04 kept; 2 Gens Ace packs; RW 35046-S cut to 36 in ($118.97, no spare tube, C4.md); silica C07 and microballoons C08 replaced by one System Three 3145S16 quart at Zoro $15.69 (`UNVERIFIED`, C2.md); X07 box, X13 microSD in; X10 / X12 fallbacks out; all X14 tools new (Jacobs lists no K-line tool: BUILD-GUIDE.md, labs page 2026-11-13).
Crash rule: one bad crash = pack $131.99 + servo $41.99 + one fin tube $118.97 (only because no spare tube is carried), x 1.1025, plus one $10.71 shipment per vendor = **$347.39**. Spares carried (5th motor, 4 spare ESCs, props) are not billed again.

| Group | $ incl. tax |
|---|---|
| propulsion | 371.87 |
| power | 414.95 |
| avionics | 335.09 |
| mechanisms | 77.15 |
| airframe | 695.71 |
| ground + test | 293.87 |
| tools (X14) | 378.92 |
| transport | 77.38 |
| shipping 23 x 10.71 + FAA 5 | 251.33 |
| **Spend** | **2,896.28** |
| crash reserve | 347.39 |
| **Total** | **3,243.67** (tools out: 2,800.49) |

Carrying the 48 in tube ($151.96, third segment is the spare) is cheaper than reserving it: crash line 205.52, total 3,138.17 (lever L0).

## 2. Cost caps per subsystem (targets; sum $1,900 + contingency $100 = $2,000)

Caps are the design-to-cost allocation. Column "path" is the section 5 full path; the overrun is what each role must still find or reject.

| Subsystem | Cap $ | Path $ | Over |
|---|---|---|---|
| Propulsion (motors, ESCs, props, adapters) | 300 | 348 | +48 |
| Power (packs, connectors, wire, caps) | 330 | 386 | +56 |
| Avionics (FC, GPS, RX, airspeed, TX, cells) | 250 | 294 | +44 |
| Mechanisms (servos, linkage) | 70 | 77 | +7 |
| Airframe (tubes, foam, composites, hardware) | 420 | 667 | **+247** |
| Ground + test | 150 | 243 | +93 |
| Tools | 90 | 156 | +66 |
| Transport | 25 | 23 | -2 |
| Shipping + FAA | 125 | 176 | +51 |
| Crash reserve | 140 | 206 | +66 |
| **Caps total** | **1,900** | 2,577 | +677 |
| Contingency (minimum 40) | 100 | | |

Airframe is the problem: tube $152 + plug $29 + foam / composites / epoxy / hardware. It cannot reach $420 without the fin tube changing.

## 3. Cheaper component families

None qualifies on published data. Table rows are candidates and the re-check each would trigger.

### Motors (bar: >= 0.305 N m continuous at rated current, 11 in on 4S, <= 110 g, $15-25)
| Candidate | Price | Data | Bar | Triggers | Pass? |
|---|---|---|---|---|---|
| Racerstar BR2814 1000KV 3-4S, 106 g | $24.75 low end of a $24.75-102.05 range `UNVERIFIED` (https://rcbuying.com/products/racerstar-br2814-1000kv-brushless-motor-for-3-4s-rc-airplane-models, 2026-11-14) | no thrust table, no Rm, no torque `—` | torque `—` | E1 (T/W, current: 1000 KV on 11x8 draws more at the same rpm), C4 (rpm / mass), E2, A3 | `EST` unlikely: no data and +11 % KV |
| Emax Pro 2814 730KV | $31.99 `UNVERIFIED` (ReadyMadeRC snippet) | none `—` | `EST` Kt 9.55/730 = 0.0131 N m/A, so 0.305 N m at about 23 A, if the winding holds it | E1, C4, A3 (mass `—`), B1 climb (lower rpm) | `EST` 40 %; saves $8 per motor, about $44 for 5 |
| LIG AS2814 KV900 | `—` | max thrust 2209 g, rec. 12x6 (https://www.ligpower.com/product/as2814-kv900-motor.html, 2026-11-14) | torque `—` | E1, C4 | unknown |
| Hobbywing Skywalker 2814 1000KV | `—` | maker page only (https://www.hobbywing.com/en/products/skywalker2814) | `—` | E1 | unknown |
| T-Motor AS2814 / AT2814 900KV | `—` | RCbenchmark tests at 9x5 / 10x6 only (tytorobotics) | no 11 in row | E1 | no data |

Result: no $15-25 2814 with a maker or reputable thrust table at 11 in. The SunnySky X2814 V3 stays ($39.99, no second US price). Motor spend cannot fall under about $175 (4 x 39.99 + tax).

### Servos (bar: >= 3.49 kgf-cm at 6 V, pocket 12 mm)
| Candidate | Torque | Speed | Mass | Price | Result |
|---|---|---|---|---|---|
| Savox SH-0255MG+ (current M01) | 3.9 kgf-cm at 6 V (BOM.csv) | — | 12 mm micro `—` g | $34.99 baseline / $41.99 pess. | passes, only part found |
| Emax ES3352HV | 1.7 / 2.4 kgf-cm (6 / 8.4 V presumed) | 0.18 / 0.13 s | 12.4 g | about $12-16 `UNVERIFIED` (https://www.getfpv.com/emax-hv-high-voltage-servo-es3352hv.html) | fails 3.49 |
| Savox SH-0257MG | 2.2 kg-cm at 6 V | — | — | $39.99 | fails |
| Savox SV-1250MG | 4.6 kg at 6 V | — | — | about $64.99 | too wide: 35 x 15 x 29.2 mm vs 12 mm pocket |

Servos stay. Triggers if B2's hinge moment is cut instead: B2, B3, D1 (smaller elevon, area 15.5 % S already).

### Packs (bar: 4S >= 5.7 Ah, <= 440 g, 10 AWG, >= 80 A, fits 160 x 52 x 53 mm)
| Candidate | Price | Mass | Result |
|---|---|---|---|
| Gens Ace Redline Shorty 6000 HV (current) | $127.99-131.99 | 410 +/- 10 g (E2) | only pack that passes (E2 D-173) |
| Turnigy Rapid 6000 4S 100C | $36.39 special `UNVERIFIED` (HobbyKing snippet 2026-11-14) | `—` (6000 mAh class, `EST` > 600 g) | `EST` fails 440 g, XT90 |
| Zeee 6000 4S 100C EC5 | about $60 each, 2-pack $169.99 less 30 % `UNVERIFIED` (zeeebattery.com snippet) | `—`, `EST` > 600 g | `EST` fails mass; E2 / A3 / C5 CG re-run |
| Tattu 6000 4S 35C XT60 | `—` | `—`, `EST` > 600 g | `EST` fails mass and 80 A |
| CNHL LiHV 4S 6000 | $69.99 | 479 g | rejected by E2 (12 AWG leads, stock, CG -3.5 mm) |

Packs are a floor: 2 x $131.99 x 1.1025 = $291.04.

### ESCs (45 A, bidirectional DShot)
LANRC 45 A 4-pack $30 (B02, `UNVERIFIED`, no US page found). Fallback Holybro Tekko32 F4 45 A $22.50 each (backorder). Bidirectional DShot needs BLHeli_S + Bluejay or AM32: F4 / F1 re-check. A second 4-pack for spares ($33.08) is cheaper than 4 singles; singles cost more (script lever tested and removed).

### Flight controller
SpeedyBee F405 Wing APP $51.99 (https://eurilca.org/products/speedybee-f405-wing-app-flight-controller-275/208628715/, snippet 2026-11-14) vs CoreWing $69.49: saves $17.50 (pess.). Bidirectional DShot, 8 A BEC, ArduPlane quad-plane target all `UNVERIFIED`. Triggers F3 (airspeed I2C, 6 UARTs), F4 (params, Bluejay), B3 (Plane hold), F1 (BEC). `EST` 50 %.

### Radio, charger, tools
- Radio: plain Pocket ELRS $64.99 in the B01 cart vs Crush $84.49: -$21 (ReadyMadeRC, carried from COST-TRADE X1, not re-read). No re-check.
- Charger HTRC C150 $56.99 stays; no cheaper charger found that lists LiHV 4.35 V and >= 6 A (E2 checks the manual on arrival).
- Tools: lean kit keeps scales, caliper, hex set, sandpaper, IPA, gloves, cups, knife blades; drops K01 torque driver (C6 accepts lever-arm), K04 (phone inclinometer), K05, K06, K08 (TPU 1.5 g from Jacobs stock; D3 to confirm). Tools $378.92 -> $156.49 (cap 90 needs more drops).

## 4. Architecture-level options (each on top of path L0-L8, total $2,585.72)

| Option | $ saved (EST) | Physics risk | Roles reopened |
|---|---|---|---|
| 3S 6000 packs about $50 x 2 | 282 | high: hover power fixed, V 12.6 vs 16.8 sets rpm and max thrust (T/W 2.0 at 2.70 kg already thin: fresh 2.096, worst 1.771) | E1, E2, B1, B2, B3, A3, C1, C4, C5, F1, F4 |
| Smaller prop (10 in) | 0 on BOM (props $4) | lowers disc area, hover power up | E1, E2, B1, B4, C4, D3 |
| One flight pack | 146 | breaks the 2-pack schedule rule | H1, H2, I2; not allowed |
| CNHL 2 x $69.99 | 205 | mass +27-65 g, CG fails -3.5 mm, E2 failed | E2, A3, D2, C5 |
| Cheap fin tube (INFINITubeV 36 in $76.99) | 83 | E / G unpublished; needs 96 / 12.5 GPa for equal EI (COST-TRADE 2.7) | C4, C2, D3, C6 |
| Fin geometry change (C4's 3 questions, COST-TRADE 2.7): shorter span or bigger brace so a lower-E tube passes; coupon test first | 83 plus tube $119 -> about $77 | span 10 % shorter is about +37 % stiffness `EST` | C4, D3, B3 (fin area / yaw), A3, D7 (box) |
| Smaller wing | 15-25 `EST` (foam) | stall 12.13 m/s, 1.3 Vs 15.76 vs THR_MAX / AIRSPEED_MAX 18: no margin | B1, B2, B3, C1, C2, D1, A3 |
| Defer airspeed sensor | 69 | user: required | not allowed |
| Fewer spares with bigger reserve | about 0 | reserve grows by the same amount plus a shipment | A2 only |

No option is large and low-risk. Wing size saves foam only; motors, packs and the tube are the cost.

## 5. Recommended path (least engineering risk), script output

Cumulative total incl. crash reserve; L0-L8 low-risk parts and spares.

| Step | Risk | Change | Cum. total $ |
|---|---|---|---|
| base | | honest baseline, 36 in tube | 3,243.67 |
| L0 | 1 | keep 48 in tube; spare tube leaves reserve | 3,138.17 |
| L1 | 1 | lean tools | 2,872.90 |
| L2 | 1 | hot wire from a flight pack (no G11) | 2,833.51 |
| L3 | 1 | plain Pocket | 2,812.01 |
| L4 | 1 | merge carts (XT60H, M6 nut, filament, airspeed) | 2,779.88 |
| L5 | 1 | 8 props / adapters, 9 caps, one bag, one 16 AWG reel | 2,715.91 |
| L6 | 2 | drop W03 spare test tube, W11 PTFE | 2,662.71 |
| L7 | 2 | US 19 mm plug tube $28.56 | 2,639.70 |
| L8 | 2 | no mat T05, foam T06, tote T07 | 2,585.72 |
| L9 | 3 | SpeedyBee F405 Wing APP | **2,577.13** |

Remaining gap **$577**, or about **$295** if 3S also passes. Neither closes. The smallest honest reduction of the gap needs the user to relax one rule. Options for the user, with $ from the script: (a) accept one flight pack until the first gate passes and buy the second after (-$146); (b) count only tools Jacobs actually lists (already assumed); (c) defer airspeed (-$69).

## 6. Ordered re-checks (if the user takes the path)

1. D7 / A3 / C4: 48 in tube kept with spare; plug from US tube (fit to Rock West 19.05 mm bore).
2. D1 / C2 / D3: PTFE release replaced by packing tape; hot wire from pack; no mat.
3. F1: caps 9 at 48 kHz derate (maker frequency multiplier >= 0.86).
4. F3 / F4 / B3 / F1: SpeedyBee F405 Wing APP (bdshot, BEC, airspeed I2C, Plane hold).
5. E1: Emax Pro 2814 730KV if a thrust / Rm table is published (current, T/W, mass); then C4 (vibration from rpm and mass), E2 mission, B3 control, A3 mass / CG.
6. Only if the user wants 3S: E1, E2, B1, B2, B3, A3, C1, C4, C5, F1, F4.

## 7. Open items

Motor $15-25 and servo cheaper families: none found with published data. Not read (snippet only): HobbyKing, Zeee, rcbuying, eurilca, GetFPV, Zoro. `—` marks unknown masses.
