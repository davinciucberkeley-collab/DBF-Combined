# December test and purchase plan, concept A O4b (T-081, 2026-11-20)

Status: **plan, not VERIFIED COMPLETE. Nothing bought, no account made, nothing committed.** Nobody has run any test below.
Prices were read from vendor pages on 2026-11-20 unless marked. EST = estimate. "—" = unknown or not read. The tests are physical measurements. The one analysis in this file is the cost arithmetic (category: illustrative, hand arithmetic on a scratch copy of `bom_a.py`).
Limits not relaxed: RF >= 1.0, KF 1.725, KP 2.156, A-P3 window >= +-5 %, A-P16 12.1 A one motor, A-P5 12 g, A-P9 30 deg, total spend including the crash reserve <= $2,000 (AM-013), crash reserve kept (AM-012), no purchase before early December 2026 (Order 1 is 1-4 Dec, `SCHEDULE-A.md`).

## 0. Answers in one place

| # | Question | Answer |
|---|---|---|
| 1 | What decides 2026-12-15? | Only bench items: derate >= 0.905 (0.873 on the repo arithmetic), one motor <= 12.1 A at the cap, the Lua cap running on the H743-Wing, and the A-P10 tap test (`O4-feasibility.md` s6). Tests TP-1 and TP-2 are those. **The tap test (TP-10) needs a built cage and cannot be done by 15 Dec** (s5, item 6). |
| 2 | What gates the build, not the go/no-go? | TP-3 to TP-9. Each closes a row that is below 1.0 or has an unknown allowable. They need parts that only arrive after Order 1. |
| 3 | Is there a rig for kN loads? | **No.** The only load cell in the BOM is a 10 kg cell (about 98 N, G02/B05). The bond and tube coupons need about 1 to 4 kN. A frame or press with a force readout is missing (s3). |
| 4 | Total with every purchase in s4? | **$2,330.25 (full list) and $2,243.34 (trimmed list), against $2,000, crash reserve held at $327.43.** The O4b parts alone (H743-Wing + RDQ packs) are $1,879.77 (reserve held) to $1,899.50 (reserve rebuilt from the pack price). The test and material purchases do not fit. Over by about $243 to $330 before the "—" lines. |
| 5 | Calendar | Order 1-4 Dec, go/no-go 15 Dec, Jacobs access ends 18 Dec and is assumed closed 19 Dec to 18 Jan (`SCHEDULE-A.md`, third-party calendar). TP-3 to TP-9 do not all fit before 18 Dec. See s5 item 3. |

## 1. Test table (in the order of the 2026-12-15 go/no-go, then by build gate)

| ID | What it closes (row or claim, current RF) | Specimen (n) | Rig and instrument | Pass number | On fail | Duration (EST) | Who and where |
|---|---|---|---|---|---|---|---|
| TP-1 | Bench derate and one-motor current. `T-A-BENCH-THRUST`, `T-A-BENCH-MOTOR`, `CL-A-WINDOW-PRED`; derate 0.93 is EST (T-074 check 3). Threshold 0.873 repo arithmetic, about 0.905 with the 3 % download | 1 MN2212 + APC 9x4.5MR (+ MRP) on the stand; repeat on a second motor if the first is within 2 % of the line | Stand G03 + load cell G02, watt meter G01, K-type probes B03; **rpm sensor and a 14.9 V source: missing** | Thrust at the model rpm >= 0.905 x APC table (s2.1) | Derate < 0.873: no-go, order O6 on 15 Dec (D-217). 0.873 to 0.905: plant arithmetic fails, reviewer rules (s5 item 1) | 0.5 day | Team lab |
| TP-2 | Lua cap on the real FC. Check 1 (H743-Wing) ran only in SITL; `Q_M_BAT_CURR_MAX` 45 A | H743-Wing + ESC + 1 motor on the stand | Stand as TP-1, FC log, `sitl/lua/spin_cap.lua` | Cap table matches +-0.01; failsafe sets 0.90; one motor <= 12.1 A at the cap | No Lua on the board or no usable resting voltage: no-go (D-217). Cap script fails but hardware runs it: fix script, one re-test | 0.5 day | Team lab |
| TP-3 | Pad drop. D-222 hold point; `CUP EVA` rows 0.01 / 0.14 / 0.15; A-P5 n 12.41 g at zeta 0.10 (RF 0.97); stroke 21.5 of 24 mm; tilt 2.97 deg (RF 1.01) | Per foam: 3 drops x 2 masses (0.41, 0.82 kg); 3 foams | Guided drop rig 73 mm, **ADXL375 + a logger: logger missing** | Equivalent zeta <= 0.02 target; **hard line < 0.09**; plateau 30 N; usable stroke >= 24 mm | zeta >= 0.09: change foam or geometry (s2.3) | 1 day + rig 1 day | Team lab, Jacobs makerspace |
| TP-4 | CF-in-Al bond. `bond mean shear` RF 0.77 (D-1) / 0.55 to 0.77 (floor); needs >= 2.6 to 2.9 MPa vs 2.0 EST; C-5 | CF 12x10 tube in 6061 sleeve, L 32 mm (n = 5) and L 24 mm (n = 5) push-out, plus 3 torsion | **Force frame >= 5 kN: missing**, calipers | Min of 5 >= 2.9 MPa (3.5 kN at L 32; 2.6 kN at L 24) | Add a rung: longer sleeve, second bond line, or credit the cross-pins (T-076d s4.3) | 1 day (cure 24 h) | Metal shop, frame "—" |
| TP-5 | Tube interlaminar shear. Judged tau_s,r 16.8 to 18.9 MPa (D-1), allowable "—"; needs >= 30 to 33 MPa (D-1) or 43 MPa (RB x 1.61) | 12x10 tube with the P1 tapered doubler, 3-point bend, n = 5; plain 12x10 short-beam n = 5 | Frame as TP-4 | See s2.5 | No named fallback; stop rule says add nothing beyond P1/P2 (s5 item 5) | 1 day | Metal shop, frame "—" |
| TP-6 | X7 node CGE-006. C-2 (CF knockdown >= 400 MPa EST), C-3 (CF tube to Onyx bond), Mz row (PETG net section 0.81 at x2) | Onyx beam with CF rings, 3-point bend n = 5; pin-bearing coupon n = 5; CF-to-Onyx and CF-to-PETG push-out n = 5 + 5 | X7 job, frame as TP-4 | Fibre stress >= 400 MPa; bond mean >= 2.0 MPa | Machined 6061 node on the Tormach (+10 to +15 g, T-080) | 1 day + print | Room 332, Metal shop |
| TP-7 | Printed joints. C-1 (PETG 20 / 9.5 MPa EST), `ASM-A-PETG-JOINT-ILAY`, root block P6 / P8 (0.50 / 0.51 pre-package), tray, clamps; C-4 clamshell node (FIN-005; saddle 0.28) | C-1: 5 + 5 per orientation, PETG (team printer) and Onyx; C-4: 2 nodes | Frame as TP-4 | mean - 3 sigma >= 20 / 9.5 MPa; C-4: no failure at 2.156 x limit | Onyx for the root block; resize the clamshell (T-080 s3.3) | 1.5 days | Team lab, room 332 |
| TP-8 | Glass skin. P15 wrinkling RF 1.13 baseline, 0.87 at zeta 0.10, 0.54 at the 1.61 floor; allowable is dry Vf 50 % x 0.70 EST (T-071) | Foam sandwich beams, 1 ply +-45 glass, n = 3 flexure + n = 3 torsion | Frame (low load), caliper, scale | Measured/EST wrinkling stress ratio r >= 1.15 (zeta 0.10) | 2 plies, +27 g (T-071) | 1.5 days (cure 24 h) | Team lab |
| TP-9 | Pad friction drag. T-068 hold point; P9a rib 0.86, 1.23 at mu 0.30 | Actual pad + UHMW face, n = 5 per surface | G02 cell (98 N is enough: breakaway about 9 N), 30 N dead load | Max of 5 <= 0.30 per surface | Face not approved: drag test at design mu 0.40 and RMRC rib twist coupon (T-068 F3b) | 0.5 day | Team lab, RFS |
| TP-10 | Tap test A-P10, hi-corner mode vs the re-based limit 88.0 Hz (84 Hz as modelled, margin 4.5 %) | Built cage and fin | Hammer, FC accelerometer | Mode <= limit | Reviewer, `T-A-TAP` | after the build | Team lab |

Existing coupons carried unchanged: RMRC rib twist (`ASM-A-RIB-TWIST`), horn stall bench, C-6 pad cup (folded into TP-3). H-1 motor-base temperature is run inside TP-1.

## 2. Test sheets

### 2.1 TP-1 Bench thrust, derate, current (go/no-go)
Derate is defined as in `prop_a.py` (`DER`): measured thrust divided by the APC PER3 table thrust at the same rpm. Model values (illustrative, `prop_a.full`, EST I0 0.5 A, pack R 30 mohm): sag state 14.92 V rest, all four at duty 1.0: **9,180 rpm, 930 gf per motor, 10.75 A bus**. Cap state 16.8 V, duty 0.903: 9,373 rpm, 971 gf, 11.21 A.

| Step | Action |
|---|---|
| 1 | Zero the cell, weigh a 500 g reference mass, log zero before and after (`bench_analysis.py` rule, drift <= 0.005). |
| 2 | Fit the APC 9x4.5MR to one MN2212 on the stand, motor on an ESC channel, FC at idle. Fit the K-type probe to the motor base (H-1). |
| 3 | Set the pack to about 14.9 V resting (partial discharge on the M6AC charger). Step throttle 0 to 100 % in 10 % steps, 10 s each. Log gf, bus A, V, rpm. |
| 4 | Repeat on a fresh pack (16.8 V). |
| 5 | Read thrust at 9,180 rpm. Compute derate = gf(9,180 rpm) / 930. Judge it against both lines (0.873 and 0.905). The bench has no slipstream, so the 3 % download is in the 0.905 line, not in the measurement. |
| 6 | Hold throttle for the H-1 run: 5 min at hover thrust (about 396 gf at 1.47 kg, `bench_analysis.py` `T_HOVER`; the 1.64 kg value is "—"), log the base temperature. |
| 7 | Run `python -I redesign/qp/A/bench/bench_analysis.py LOG.csv` and save the output next to the log. |

Pass: **derate >= 0.905** (842 gf at 9,180 rpm; 0.873 is 812 gf). Current at the same rpm within +-10 % of 10.75 A. Base temperature below the PETG heat-deflection temperature less 10 deg C (HDT not read: "—"). The old claim line (780 / 624 gf per motor at the 0.90 cap) is for 1.47 kg and is stale for 1.64 kg.
Gaps: no rpm sensor (the ESC's bidirectional DShot telemetry is UNVERIFIED, BOM P04), no 14.9 V source other than a part-discharged pack, **one motor only, so the all-four pack current (43.9 A at sag, T-074) is not measured**.

### 2.2 TP-2 Lua cap on the H743-Wing (go/no-go)
| Step | Action |
|---|---|
| 1 | Flash ArduPlane for the KakuteH7-Wing target. Check `SCR_ENABLE 1`, the script heap, and that `spin_cap.lua` loads ("spin_cap.lua loaded" message). |
| 2 | Set `Q_M_BAT_CURR_MAX 45`, battery monitor on with the real calibration, `BATT_` resistance learning on. |
| 3 | Pack at 16.8 V, 16.0 V, 15.4 V, 14.9 V resting. Log `voltage_resting_estimate` (script message every 10 s) and `Q_M_SPIN_MAX`. |
| 4 | At each voltage run one motor at full throttle for 5 s on the stand. Log current. |
| 5 | Disconnect the battery monitor sense. Check the script goes to 0.90 and holds it. |

Pass: cap matches the script table within 0.01 (16.8 V 0.903, 16.0 V 0.952, 15.4 V 0.992, 14.9 V 1.0); one motor <= 12.1 A at 16.8 V; failsafe 0.90 within 2 s. Fail: no usable resting estimate on the real FC (T-076 "Not verified") means no go. Note the SITL finding that the failsafe 0.90 fails the r 1.33 entry at 1.64 kg (T-076 F-4).
Gap: needs the H743-Wing, the new packs and the FC to be in hand before 15 Dec.

### 2.3 TP-3 Pad drop (gate before the pad CAD changes; D-222 s4.1)
Specimen: pad column 12 x 15 x 30 mm (T-068 F-6) of each foam, with the UHMW face when TP-9 is run. Candidates: the present EVA/PE and two others ("—": products not chosen; EVA 1/2 in proxy in s4).

| Step | Action |
|---|---|
| 1 | Build a guided drop rig (G03 wood + B04 bearings): mass 0.41 kg, release height 73 mm (v^2/2g, 1.2 m/s). Fix the ADXL375 to the mass. |
| 2 | Calibrate: drop onto a rigid stop, check the accelerometer peak against a hand estimate. State the logger sample rate (ADXL375 bandwidth 1 kHz, Adafruit page; logger rate "—"). |
| 3 | Drop on each foam, 3 times. Repeat with 0.82 kg (two feet loaded). |
| 4 | Record force-time (mass x acceleration), stroke from the integral. Fit plateau Fp, yield stroke, rate term (zeta) and recovery. |
| 5 | Re-run `landing_path_a.py` with the measured law (D-222 step 7). |

Pass: **zeta <= 0.02 (target), hard line < 0.09** (above it n > 12 g at Fp 30; at 0.10 A-P5 fails); plateau 30 N; usable stroke >= 24 mm; peak foot force <= 37 N model value at 1.2 m/s. Fail: zeta >= 0.05 keeps the present pad but the foot rows fall 25 to 40 % (T-076d s5); zeta >= 0.09 means a new foam or geometry from the T-076d step-2 grid (7 of 10 points pass at 0.05).

### 2.4 TP-4 CF-in-Al bond push-out (C-5)
Needed allowable >= 2.6 to 2.9 MPa (T-076d s4.3). I set the pass line at 2.9 MPa, the top of that range. Bond area is pi x 12 x L; load = 2.9 MPa x area (hand calculation).

| Step | Action |
|---|---|
| 1 | Cut 6061 sleeves (15/12 mm, L 32 and L 24), mill-reamed to the bond fit; bore size is "—" until the tube OD is measured. |
| 2 | Prep as the build: abrade, solvent, glass-scrim wrap (galvanic barrier), primer "—". Bond 12x10 CF tube pieces. Cure 24 h. |
| 3 | Push the tube out at a fixed rate; log peak load. Torsion on 3 more. |
| 4 | Report mean shear = peak / (pi x 12 x L). |

Pass: min of 5 >= 2.9 MPa (about 3.5 kN at L 32, 2.6 kN at L 24). Fail: more rungs (longer sleeve, second bond line, credit the 3 mm cross-pins, not credited in T-076d).

### 2.5 TP-5 Tube interlaminar coupon
Specimens from offcuts of the R08 12x10 tubes ($0). Plain short-beam (span-to-OD 2 to 3) n = 5; P1 geometry (14x12 doubler, tapered tip, staggered past the sleeve end) in 3-point bend n = 5. Layup of the RMRC tube is "—".
Pass: the finite-element interlaminar value at the measured failure load, taken with the same judging method as T-076d (0.5 mm exclusion), is >= 43 MPa (RB x 1.61, zeta 0.10) or >= 30 to 33 MPa (D-1 direct) if the reviewer takes the D-1 reading. Fail: no named fallback; T-076d stopped at P1/P2. Reviewer.
Needs the force frame from TP-4.

### 2.6 TP-6 X7 node, TP-7 printed joints
| Test | Specimen | Pass |
|---|---|---|
| C-2 | Onyx beam with concentric CF rings, 3-point bend, n = 5; pin-bearing coupon with CF ring round a 3 mm hole, n = 5 | Fibre tension stress >= 400 MPa EST (Markforged sheet 800 MPa x 0.5) |
| C-3 | CF tube bonded in an Onyx socket (and PETG as control), push-out n = 5 + 5 | Mean shear >= 2.0 MPa |
| C-1 | PETG (team printer) and Onyx tensile bars, in-layer and interlayer, n = 5 each | min of 5 (or mean - 3 sigma) >= 20 / 9.5 MPa x the knockdown used |
| C-4 | One clamshell fin saddle (0.5 mm CF plates, cradle, 3 pins) in Mz, My, Mx | no failure at 2.156 x limit |

Print z-up for the node and the root block (D-215 rule). Weigh the C-2 beam to get the real CF density (T-080 F-7). Fail: node to machined 6061 on the Tormach.

### 2.7 TP-8 Skin coupon
1 ply 48 g/m2 glass at +-45, wet lay-up on FOAMULAR 150 sandwich, 24 mm class. Compression-face wrinkling in 4-point flexure and a torsion strip, n = 3 each. Ratio r = measured wrinkling stress / EST (Hoff-Mautner 0.5 (E_f E_c G_c)^(1/3), T-071). The EST stress value is in the T-071 script, not restated here ("—").
RF scales with r: baseline 1.13 r, zeta 0.10 0.87 r, floor 0.54 r. **Pass r >= 1.15; r >= 1.85 is needed for the floor.** Fail: 2 plies (+27 g).

### 2.8 TP-9 Pad friction drag
Pad with UHMW face loaded to 30 N dead weight on each candidate surface, pulled with the G02 cell at a slow constant rate, breakaway n = 5. Grass is tested with the pad set into the grass. Surface list: "—" (T-068 proposes the text; not read here). Pass: max <= 0.30 per surface. Only passing surfaces go on the approved list.

## 3. Equipment: what exists and what is missing

| Need | Have | Missing |
|---|---|---|
| Static force to 98 N | G02 TAL220 10 kg + HX711 (SparkFun $12.95 read 2026-11-20) | — |
| Force to 1 to 4 kN | Metal shop 20 t press (Jacobs list; readout "—") | **Calibrated frame or load cell to about 5 kN. Not priced, not in the BOM.** Ask the Jacobs staff or a mechanical-engineering lab first |
| Impact force | — | ADXL375 ($31.95) + a logger and rate "—" |
| Motor rpm | — | Tach or confirmed ESC telemetry |
| Machines | Knee mills, Tormach (training in the Maker Pass), waterjet, X7, Prusas, vacuum former (`jacobs-equipment.md`) | X7 and Tormach booking, material charges, Prusa PETG policy: all "—" |

## 4. Purchase list (beyond the current BOM-A.csv)

Source column: read = vendor page read 2026-11-20; snippet = search result only, page not read (BOM status "U"); prior = read 2026-11-19 by the conductor, page returned HTTP 429 today. Tax 10.25 % and one shipping group per vendor at $10.71 EST (the BOM's own Amazon/Prusa figure; real rates not read) are applied by the scratch run.

| ID | Item | Qty | Unit USD | Source and URL | Status |
|---|---|---|---|---|---|
| V03 | Kakute H743-Wing FC (replaces V03 F405) | 1 | 141.44 | read: https://www.readymaderc.com/products/details/87185-holybro-kakute-h743-wing-flight-controller (In Stock) | read |
| W01 | RDQ 4S 2800 mAh 100C pack (replaces Tattu 2300) | 2 (+1 in reserve) | 54.99 | prior: https://www.racedayquads.com/products/rdq-series-11-1v-4s-2800mah-100c-lipo-battery-xt60 (429 today; 107 x 33 x 46 mm, 270 g, tray fit open) | prior |
| T1 | 6061 bar, 2.5 in square, about 305 mm (hub block about 60 x 110 x 42 mm needs a 63.5 mm face) | 1 | 74.25 | read (range low end, length not shown, $25 cut fee not added: Jacobs bandsaw): https://alcobrametals.com/?p=52854 | snippet-grade |
| T2 | CF plate 0.5 mm, 300 x 300 (saddle plates + node plates) | 1 | 40.99 | snippet (Rockwest page I read shows no price): https://www.rockwestcomposites.com/121709762.html | snippet |
| T3 | Glass cloth 2 oz 38 in, 5 yd | 1 | 17.00 | snippet (429 today): https://clcboats.com/products/fiberglass-cloth-2oz-39 | snippet |
| T4 | Laminating epoxy, 105/205 kit 1.2 qt | 1 | 92.02 | snippet: https://fiberglasssupply.com/epoxy/west-system/west-system-105-epoxy-resin/west-system-kits-105-epoxy-with-205-fast-hardener/ | snippet |
| T5 | CF strip 3 x 1 mm, 1 m (cove strip, 3 mm2) | 2 | 2.02 | read: https://www.readymaderc.com/collections/airplanes/build-and-repair-parts/carbon-fiber-strips-tubes-spars/carbon-fiber-strips | read |
| T6 | UHMW tape 1 in x 18 yd (10 mil, acrylic adhesive) | 1 | 26.38 | read: https://www.usplastic.com/catalog/item.aspx?itemid=26497 (In Stock) | read |
| T7 | EVA foam 1/2 in, 12 x 12 (proxy for pad foam samples) | 3 | 17.99 | snippet: https://www.zoro.com/zoro-select-foam-sheet-water-resistant-closed-cell-12-in-w-12-in-l-12-in-thick-black-zusa-eva-4/i/G7273578/ | snippet |
| T8 | ADXL375 +-200 g accelerometer breakout | 1 | 31.95 | read: https://www.adafruit.com/product/5374 (In stock, bandwidth up to 1 kHz) | read |
| — | PETG sheet 0.5 mm (vacuum-formed cover); only 0.060 in 12 x 12 at a US shop seen (snippet) | 1 | — | — | — |
| — | 12 mm and 16 mm reamers (sizes set by TP-4); a Zoro 12 mm NC reamer at $46.15 is a different tool (snippet) | 2 | — | — | — |
| — | Pad foam candidates other than the present one; X7 material charge; scanning spray; force frame or cell to 5 kN; drop-rig logger; tach; test fixtures beyond G03 / B04 | — | — | — | — |

Already in the BOM and used by the tests: G01 watt meter, G02 load cell + HX711 + scale + caliper, G03 stand parts, B01/B02 bench motor and props, B03 bar cell and K-type probes, B04 fixture, B05 TAL220, W02 charger, R03 PETG, R08 tubes (offcuts for coupons), R14 3 mm CF rod (price "not found").

### 4.1 Budget run (illustrative; scratch copy of `bom_a.py`, `BOM-A.csv` and `bom_a.py` not edited; files in `redesign/qp/A/mechanism/out/T081_data/`)

| Scenario | Goods | Shipping | Spend | Crash reserve | Total | vs $2,000 |
|---|---|---|---|---|---|---|
| Current `BOM-A.csv` (reference) | 1,262.50 | 55.13 + FAA 5 | 1,452.04 | 327.43 | 1,779.47 | +220.53 |
| C: H743-Wing + RDQ only (reserve rebuilt from the $54.99 pack) | 1,343.76 | 65.84 + FAA | 1,552.34 | 347.17 | 1,899.50 | +100.50 |
| C with the reserve held at $327.43 (AM-012) | | | 1,552.34 | 327.43 | 1,879.77 | +120.23 |
| A: C + T1 to T8 as listed | 1,684.36 | 140.81 + FAA | 2,002.82 | 327.43 held / 347.17 rebuilt | **2,330.25 / 2,349.98** | **-330.25 / -349.98** |
| B: A trimmed (CF plate 200 x 300 at $19.99 on the existing Amazon group, cloth and epoxy from one vendor at $14.58, one EVA sheet) | 1,624.96 | 119.39 + FAA | 1,915.91 | 327.43 held / 347.17 rebuilt | **2,243.34 / 2,263.07** | **-243.34 / -263.07** |

The T1 to T8 lines add about $375 with tax, plus about $75 for seven new shipping groups. The "—" lines are not in these totals, so the real overrun is larger.
**Flag: the list pushes the total over $2,000 in both scenarios.** No cut to the crash reserve is made here (AM-012). Levers (not applied, Dillon's call): consolidate vendors (each group is about $10.71 EST); ask Jacobs for X7 charge $0, aluminium offcut, CF plate scrap, foam and epoxy; drop G05 anemometer ($27.56 with tax, may be borrowed); drop B01/B02 bench motor and props ($31.95 with tax) if the MN2212 stand is enough; the 5 kN frame by loan not purchase. These add to about $100, which still leaves the total above $2,000.

## 5. Open judgment items for a reviewer

| # | Item | Why it is open |
|---|---|---|
| 1 | **DAF floor.** T-076d judges at max(DAF, 1.5) = 1.61, the envelope ratio at pad zeta 0.02, hi corner, 1 % damping. The case-max ratio is **3.08** (kd corner). The D-1 direct rows are judged without a scale. | Which one is the rule sets the TP-4, TP-5 and TP-8 pass lines (43 vs 30 to 33 MPa; r 1.15 vs 1.85). Rule: does the floor lift when TP-3 gives the pad law? (D-222 LR-9) |
| 2 | Derate line | 0.873 (repo arithmetic) vs about 0.905 (plant, with the 3 % download). Between them, A-P3 passes on one and fails on the other. |
| 3 | Calendar | Order 1 is 1-4 Dec, go/no-go 15 Dec, Jacobs access ends 18 Dec and the X7 and Tormach runs, TP-4 to TP-8, do not fit unless materials arrive by about 7 Dec (lead times not read). Otherwise they slide to 19 Jan or later. |
| 4 | Glass cloth weight | The skin analysis uses 48 g/m2 (1.4 oz/yd2). The only 38 in cloth I found is 2 oz (about 68 g/m2): about +42 % ply mass. No 1.4 to 1.5 oz at 38 in found. Decide the cloth before TP-8. |
| 5 | Tube interlaminar | No fallback is in the records; P1/P2 stop rule forbids adding material. |
| 6 | Tap test (TP-10) in the go/no-go | It needs the built cage and cannot run before 15 Dec. Either build a partial cage (cups, hub, fin) from PETG, or move criterion 3 after the build. |
| 7 | Pack fit | RDQ 107 x 33 x 46 mm vs a 35 mm slot and 37 mm tray height (T-079 open item). Order only after the CAD fit. |
| 8 | Budget | Section 4.1. The O4b parts leave about $100 to $120; the tests and materials cost more than that. |

## 6. Sources
`CHANGE-LOG.md` D-215 to D-222; `docs/audits/2026-11-20-landing-demand-rootcause.md` s4; `T076d_landing_path.md` s3 to s7; `T076c_hub_al.md`; `T074_check3.md`; `docs/audits/2026-11-19-O4-feasibility.md` s6; `docs/audits/2026-11-20-T080-manufacturing.md` s8, s10; `docs/audits/2026-11-19-T068-decision.md`; `T071_wing_skin.md`; `proofs/claims.a0_base.json`; `docs/reference/jacobs-equipment.md`; `BOM-A.csv`, `bom_a.py`; `T079_cost_closure.md`; `SCHEDULE-A.md`; `AM-009`, `AM-012`, `AM-013` in `docs/spec-amendments.md`. Model values from `prop_a.py` (`full`, run 2026-11-20).

## 7. Limits
All allowables except cited vendor figures are EST. The model gf and A values are the repo's motor model, not a measurement. Push-out loads are hand arithmetic on the nominal diameter. Prices marked snippet or prior are not page reads today. Shipping is the BOM's EST per group, not read from any vendor. Lead times, X7 and Tormach access and charges, the 5 kN rig and the drop-rig logger are "—". The TP-5 and TP-8 pass lines depend on item 1 of s5. The test order after TP-2 is as the brief gave it, not scheduled against real arrival dates.
