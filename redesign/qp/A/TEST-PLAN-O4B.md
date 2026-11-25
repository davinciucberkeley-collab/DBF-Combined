# December test and purchase plan, concept A O4b (T-081, 2026-11-20)

Status: **plan, not VERIFIED COMPLETE. Nothing bought, no account made, nothing committed.** Nobody has run any test below.
Prices were read from vendor pages on 2026-11-20 unless marked. EST = estimate. "—" = unknown or not read. The tests are physical measurements. The one analysis in this file is the cost arithmetic (category: illustrative, hand arithmetic on a scratch copy of `bom_a.py`).
**T-083c update (2026-11-22; D-227, D-228, D-229, AM-016 to AM-019): the propulsion is now the SunnySky X2216 V3 880KV, the fin root block is a machined 6061 fitting, and the bench-test lines, TP-1 to TP-4 and a new TP-11 (A-P6 stall) are re-specified in the section "T-083c re-spec" at the end of this file, which supersedes any MN2212 value in s0 to s4 below (kept as the record).** Mass-dependent values are at 1.913 kg (T-083) unless marked 1.873 kg (T-083b); where the reports give no recomputation they are marked "(at 1.913 kg, T-083)".
Limits not relaxed: RF >= 1.0, KF 1.725, KP 2.156, A-P3 window >= +-5 %, A-P16 (12.1 A one motor was the MN2212 / 0.90-cap line; X2216 line 24.9 A EST and 32 A / 30 s maker, T-083 s2.1, re-spec TP-1), A-P5 12 g, A-P9 30 deg, total spend including the crash reserve <= $2,000 (AM-013), crash reserve kept (AM-012), no purchase before early December 2026 (Order 1 is 1-4 Dec, `SCHEDULE-A.md`).

## 0. Answers in one place

| # | Question | Answer |
|---|---|---|
| 1 | What decides the 29 Jan 2027 go/no-go (AM-037, D-248; was 2026-12-15)? | **[T-083c] Only bench items: derate >= 0.889 (X2216 V3 880KV + APC 9x4.5MR; the 204.6 s cruise need, at 1.913 kg, T-083), current and rpm within the TP-1 lines, the Lua cap (1.0, `Q_M_BAT_CURR_MAX` 72) and the 72 A limiter on the H743-Wing.** (Record, MN2212: derate >= 0.905 / 0.873, one motor <= 12.1 A; `O4-feasibility.md` s6.) Tests TP-1 and TP-2 are those. The A-P10 tap test (TP-10 / TP-10b) is not among them (D-236): it runs on the built airframe after the build and before the first tethered hover and does not gate the 29 Jan 2027 go/no-go. |
| 2 | What gates the build, not the go/no-go? | TP-3 to TP-9. Each closes a row that is below 1.0 or has an unknown allowable. They need parts that only arrive after Order 1. |
| 3 | Is there a rig for kN loads? | **No.** The only load cell in the BOM is a 10 kg cell (about 98 N, G02/B05). The bond and tube coupons need about 1 to 4 kN. A frame or press with a force readout is missing (s3). |
| 4 | Total with every purchase in s4? | **[SUPERSEDED (T-023 fix): the adopted total is $1,981.31 incl. reserve $346.94, margin +$18.69, `BOM-A.csv` / `bom_a.py` (D-230, AM-019); see the Budget-closed section. The figures that follow are the 2026-11-20 record.]** **$2,330.25 (full list) and $2,243.34 (trimmed list), against $2,000, crash reserve held at $327.43.** The O4b parts alone (H743-Wing + RDQ packs) are $1,879.77 (reserve held) to $1,899.50 (reserve rebuilt from the pack price). The test and material purchases do not fit. Over by about $243 to $330 before the "—" lines. |
| 5 | Calendar | Order 1-4 Dec; **no fabrication before Jacobs reopens (AM-037)**: Jacobs access ends 18 Dec, reopening assumed Tue 19 Jan 2027 (spring instruction begins that day, Registrar calendar; Jacobs publishes no spring date); stand build, prints, soldering and TP-1 / TP-2 run 19-28 Jan; **go/no-go Fri 29 Jan 2027** (`SCHEDULE-A.md` AM-037 section, D-248). TP-3 to TP-9 follow the decision. See s5 item 3. |

## 1. Test table (in the order of the 29 Jan 2027 go/no-go, then by build gate)

| ID | What it closes (row or claim, current RF) | Specimen (n) | Rig and instrument | Pass number | On fail | Duration (EST) | Who and where |
|---|---|---|---|---|---|---|---|
| TP-1 | Bench derate and one-motor current. `T-A-BENCH-THRUST`, `T-A-BENCH-MOTOR`, `CL-A-WINDOW-PRED`; derate 0.93 is EST (T-074 check 3). Threshold 0.873 repo arithmetic, about 0.905 with the 3 % download | 1 X2216 V3 880KV + APC 9x4.5MR (+ MRP) on the stand (T-083c; was MN2212); repeat on a second motor if the first is within 2 % of the line | Stand G03 + load cell G02, watt meter G01, K-type probes B03; **rpm sensor and a 14.9 V source: missing** | **Derate >= 0.889 (at 1.913 kg, T-083)**; full lines in the T-083c re-spec | **Failure reopens the configuration (AM-016 failure branch: bigger props or motors, or fallback concept B), not an O6 order (the D-217 O6 branch is withdrawn, AM-008/AM-016).** Derate between the A-P3 line 0.824 and 0.889: cruise need fails, reviewer rules (s5 item 1) | 0.5 day | Team lab |
| TP-2 | Current limiter and sensor on the real FC (**D-256: the Lua spin-cap script is dropped**; it set Q_M_SPIN_MAX 1.0 on every path since the X2216, D-227); `Q_M_BAT_CURR_MAX` 72 A (T-083c; was 45 / 41 A); `Q_M_SPIN_MAX` 1.0 read back | H743-Wing + ESC + motors on the stand (4-motor stand or the tethered aircraft for the 72 A limiter) | Stand as TP-1, FC log | Limiter holds <= 72 A; current sensor reads to >= 80 A; Q_M_SPIN_MAX reads 1.0 | Limiter does not hold or the sensor range is short: configuration reopens (AM-016) | 0.5 day | Team lab |
| TP-3 | Pad drop. D-222 hold point; `CUP EVA` rows 0.01 / 0.14 / 0.15; A-P5 n 12.41 g at zeta 0.10 (RF 0.97); stroke 21.5 of 24 mm; tilt 2.97 deg (RF 1.01) | Per foam: 3 drops x 2 masses (0.41, 0.82 kg); 3 foams | Guided drop rig 73 mm, **ADXL375 + a logger: logger missing** | **[T-083c] Pad zeta <= 0.05 is the gate for the landing rows** (target 0.02); plateau 36 N at 24 mm usable (T-083); the old line < 0.09 / 30 N is superseded **[D-233] If the pad is lengthened (e.g. to the D-222 length, X_GROUND 0.3475 m), re-check A-P9: 30.22 deg there, under the 30.5 deg target (`T084_report.md` s1.3).** | zeta > 0.05: the D-226 landing rows fail (min 0.66 at zeta 0.10), new foam or geometry or cell regrowth (re-spec TP-3) | 1 day + rig 1 day | Team lab, Jacobs makerspace |
| TP-4 | CF-in-Al bond. `bond mean shear` RF 0.77 (D-1) / 0.55 to 0.77 (floor); needs >= 2.6 to 2.9 MPa vs 2.0 EST; C-5 | CF 12x10 tube in 6061 sleeve, L 32 mm (n = 5) and L 24 mm (n = 5) push-out, plus 3 torsion | **Force frame >= 5 kN: missing**, calipers | Min of 5 >= 2.9 MPa (3.5 kN at L 32; 2.6 kN at L 24). **[T-083c: also the 6061 root-fitting bond coupon, re-spec TP-4]** | Add a rung: longer sleeve, second bond line, or credit the cross-pins (T-076d s4.3) | 1 day (cure 24 h) | Metal shop, frame "—" |
| TP-5 | Tube interlaminar shear. Judged tau_s,r 16.8 to 18.9 MPa (D-1), allowable "—"; needs >= 30 to 33 MPa (D-1) or 43 MPa (RB x 1.61) | 12x10 tube with the P1 tapered doubler, 3-point bend, n = 5; plain 12x10 short-beam n = 5 | Frame as TP-4 | See s2.5 | No named fallback; stop rule says add nothing beyond P1/P2 (s5 item 5) | 1 day | Metal shop, frame "—" |
| TP-6 | **WITHDRAWN (D-225, 2026-11-21: the X7 centre node is withdrawn; D-226 uses a machined 6061 centre node, covered by the rib torsion coupon and TP-4 bonds). Kept as record.** X7 node CGE-006. C-2 (CF knockdown >= 400 MPa EST), C-3 (CF tube to Onyx bond), Mz row (PETG net section 0.81 at x2) | Onyx beam with CF rings, 3-point bend n = 5; pin-bearing coupon n = 5; CF-to-Onyx and CF-to-PETG push-out n = 5 + 5 | X7 job, frame as TP-4 | Fibre stress >= 400 MPa; bond mean >= 2.0 MPa | Machined 6061 node on the Tormach (+10 to +15 g, T-080) | 1 day + print | Room 332, Metal shop |
| TP-7 | Printed joints. C-1 (PETG 20 / 9.5 MPa EST), `ASM-A-PETG-JOINT-ILAY`, root block P6 / P8 (0.50 / 0.51 pre-package; **[T-083c, D-229: the PETG root block is replaced by the machined 6061 root fitting FIN-003, so the PETG root-block rows no longer apply; the "Onyx for the root block" fallback below is obsolete]**), tray, clamps; C-4 clamshell node [WITHDRAWN D-225 / D-226] (FIN-005; saddle 0.28) | C-1: 5 + 5 per orientation, PETG (team printer) and Onyx; C-4: 2 nodes [WITHDRAWN, D-225] | Frame as TP-4 | mean - 3 sigma >= 20 / 9.5 MPa; C-4: no failure at 2.156 x limit | Onyx for the root block; resize the clamshell (T-080 s3.3) | 1.5 days | Team lab, room 332 |
| TP-8 | Glass skin. P15 wrinkling RF 1.13 baseline, 0.87 at zeta 0.10, 0.54 at the 1.61 floor; allowable is dry Vf 50 % x 0.70 EST (T-071) | Foam sandwich beams, 1 ply +-45 glass, n = 3 flexure + n = 3 torsion | Frame (low load), caliper, scale | Measured/EST wrinkling stress ratio r >= 1.15 (zeta 0.10) | 2 plies, +27 g (T-071) | 1.5 days (cure 24 h) | Team lab |
| TP-9 | Pad friction drag. T-068 hold point; P9a rib 0.86, 1.23 at mu 0.30 | Actual pad + UHMW face, n = 5 per surface | G02 cell (98 N is enough: breakaway about 9 N), 30 N dead load | Max of 5 <= 0.30 per surface | Face not approved: drag test at design mu 0.40 and RMRC rib twist coupon (T-068 F3b) | 0.5 day | Team lab, RFS |
| TP-10 | Tap test A-P10 / D-185 (a): decided by the T-A-TAP measurement of the built airframe, procedure TP-10b below (the earlier single-frequency limit is superseded: D-185 is a strong-mode-in-band rule, `T085_report.md`) | Built airframe, motors and pack installed | Hammer, FC IMU (TP-10b) | No mode with cx or cy >= 0.5 / (1 + u) in 94-321 Hz (D-185 (a) unchanged) | Reviewer, `T-A-TAP` | after the build | Team lab |
| TP-10b | **T-A-TAP (D-233 A, T-085): D-185 (a) / A-P10(a) measured on the built airframe.** Decides the case the beam FE cannot (wing cell, pack on the tray, hub joint; `T085_report.md`). Measures every mode below 400 Hz and its motor coupling cx, cy (the FE definition) | The assembled airframe: 4 motors with props, ESC, FC, wiring, **pack with tray, straps and pad installed**, fins, no battery change; weighed; hung free-free (method in the TP-10b sheet near the end of this file) | Pendulum hammer (steel, soft-tip option; $0, shop or team stock), 1 kg reference mass on the G02 scale, H743-Wing IMU raw batch log (V03 in the BOM; **rate >= 2 kHz to be confirmed before the test, as TP-3**), laptop FFT / ring-down fit script (team, $0) | **No mode with cx or cy >= 0.5 / (1 + u) inside 94-321 Hz** (u = the measured repeatability, TP-10b sheet; band and 0.5 unchanged, A-P10(a)). Also: every measured mode in 60-400 Hz within +-20 % of the updated FE (A-P10(c) tap tolerance) | Strong mode in band: the D-233 C design trade (bridge soft in z / stiff in torsion, or the tray carried by the wing centre node, `T085_report.md` s6) before the first tethered hover; no Dillon-level limit change. Frequency outside +-20 %: re-tune the rate loop (A-P10(c)) | 0.5 day (setup 1 h, 60 hit sets, fit) | Team lab, Jacobs makerspace (`T-A-TAP`), after the build |

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

### 2.2 TP-2 Lua cap on the H743-Wing (go/no-go) — SUPERSEDED (MN2212-era steps; the script is dropped, D-256, 2026-11-24; see TP-2 re-spec below)
| Step | Action |
|---|---|
| 1 | Flash ArduPlane for the KakuteH7-Wing target. Check `SCR_ENABLE 1`, the script heap, and that `spin_cap.lua` loads ("spin_cap.lua loaded" message). |
| 2 | Set `Q_M_BAT_CURR_MAX 45`, battery monitor on with the real calibration, `BATT_` resistance learning on. |
| 3 | Pack at 16.8 V, 16.0 V, 15.4 V, 14.9 V resting. Log `voltage_resting_estimate` (script message every 10 s) and `Q_M_SPIN_MAX`. |
| 4 | At each voltage run one motor at full throttle for 5 s on the stand. Log current. |
| 5 | Disconnect the battery monitor sense. Check the script goes to 0.90 and holds it. |

Pass: cap matches the script table within 0.01 (16.8 V 0.903, 16.0 V 0.952, 15.4 V 0.992, 14.9 V 1.0); one motor <= 12.1 A at 16.8 V; failsafe 0.90 within 2 s. Fail: no usable resting estimate on the real FC (T-076 "Not verified") means no go. Note the SITL finding that the failsafe 0.90 fails the r 1.33 entry at 1.64 kg (T-076 F-4).
Gap: needs the H743-Wing, the new packs and the FC to be in hand before the bench week of 19 Jan 2027 (Order 1 arrives 7-22 Dec EST; the powered work waits for Jacobs, AM-037).

### 2.3 TP-3 Pad drop (gate before the pad CAD changes; D-222 s4.1)
Specimen: pad column 12 x 15 x 30 mm (T-068 F-6) of each foam, with the UHMW face when TP-9 is run. Candidates: the present EVA/PE and two others ("—": products not chosen; EVA 1/2 in proxy in s4).

| Step | Action |
|---|---|
| 1 | Build a guided drop rig (G03 wood + B04 bearings): mass 0.41 kg, release height 73 mm (v^2/2g, 1.2 m/s). Fix the ADXL375 to the mass. |
| 2 | Calibrate: drop onto a rigid stop, check the accelerometer peak against a hand estimate. State the logger sample rate (ADXL375 bandwidth 1 kHz, Adafruit page; logger rate "—"). |
| 3 | Drop on each foam, 3 times. Repeat with 0.82 kg (two feet loaded). |
| 4 | Record force-time (mass x acceleration), stroke from the integral. Fit plateau Fp, yield stroke, rate term (zeta) and recovery. |
| 5 | Re-run `landing_path_a.py` with the measured law (D-222 step 7). |

**[T-098 rev 2, D-243] Foam pass criterion = a joint (plateau Fp, damping zeta) region, not a plateau band.** Fit Fp (mean crush force between 2 and 18 mm stroke) and zeta of each specimen at the 1.2 m/s drop rate. The model (`landing_a.py`, 1.881 kg, drawn rib 25x23, all 10 AR-014 cases) passes stroke <= 20 mm, n <= 12 g, tilt <= 3 deg, rib RF >= 1.0 only on this grid (AR-016): zeta 0.01: Fp 40 and 42 N pass, 33-37.5 N FAIL; zeta 0.02: 37.5-42 N pass, 33 and 35 N FAIL (33 N: 20.47 mm, 26.8 g); zeta 0.03: 37.5-42 N pass, 33 and 35 N FAIL; zeta 0.05: 33-42 N pass; zeta 0.07: 33-37.5 N pass, 40 and 42 N FAIL (n 12.4, 12.9 g); zeta 0.10: only 33 N passes. The D-226 cell / saddle path was last sized at Fp 36 N (T-083b: min RF 1.09, R4 junction, zeta 0.05) and was NOT rerun above 36 N; hand scaling RF x 36 / Fp (EST, conservative) gives RF >= 1.0 up to 39.2 N, and zeta 0.10 fails the cell (min 0.66). **ACCEPT only if the measured pair lies inside Fp 37.5-39.0 N AND zeta 0.02-0.05, with usable stroke >= 20 mm on the drawn 30 mm pad** (target Fp 37.5-38 N, zeta about 0.03-0.05; margins at the corner Fp 37.5 N / zeta 0.02: 0.44 mm stroke; the region is 1.5 N wide, about +-2 % of Fp, narrower than any plausible foam scatter, so expect to select or condition foam to it). Any pair outside the region is NOT accepted: rerun `landing_a.py` at the measured (Fp, zeta) (and, for Fp above 39 N, the T-083 demand / `landing_path_a.py` strength table) and accept only if every case and row passes. Zeta below 0.01 and Fp between the grid points were not run (stroke falls monotonically with Fp and with zeta in the grid, so the interior of the region is bracketed by its tested corners). Not shown: mu 0.30 and the 13 T-083 cases not in the AR-014 ten. **FALLBACK if TP-3 misses the region above (pad lengthened to 36 mm, CAD change, A-P9 re-check; D-243, AR-016):** ACCEPT only if the measured pair lies inside Fp 34.5-39.0 N AND zeta 0.02-0.05 with usable stroke >= 24 mm (model: zeta 0.05 passes 30-42 N, zeta 0.02 passes 34.5-45 N and fails 33 N on tilt 3.01 deg, zeta 0.10 passes 33 N only; cell cap 39 N, EST). A-P9 with the 36 mm pad: edge toward CG 30.60 deg (target 30.5, 0.10 margin), pad-centre bound 29.81 deg; the T-084 30.22 deg is the 40 mm pad. Strength rows not rerun on the longer pad.

Pass: the joint region above (Fp 37.5-39.0 N, zeta 0.02-0.05, usable stroke >= 20 mm); the older line 'zeta <= 0.02 target, plateau 30 N, peak foot force <= 37 N' is superseded (the peak foot force of the accepted foam is 41-56 N in the model at 37.5 N, `landing_cad_1881_p37p5_rib25.txt`; record the measured peak as information, it is not a pass line). Fail: any pair outside the region (rerun rule above); zeta >= 0.09 means a new foam or geometry from the T-076d step-2 grid.

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
| C-4 | **WITHDRAWN (D-225: the waterjet CF clamshell is withdrawn; the printed saddles returned).** One clamshell fin saddle (0.5 mm CF plates, cradle, 3 pins) in Mz, My, Mx | no failure at 2.156 x limit |

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

### 4.1 Budget run [SUPERSEDED by the adopted BOM-A.csv total $1,981.31, D-230; record only] (illustrative; scratch copy of `bom_a.py`, `BOM-A.csv` and `bom_a.py` not edited; files in `redesign/qp/A/mechanism/out/T081_data/`)

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
| 3 | Calendar | Order 1 is 1-4 Dec, go/no-go Fri 29 Jan 2027, and under AM-037 no fabrication runs before Jacobs reopens (assumed 19 Jan): the X7 and Tormach runs, TP-4 to TP-8, all move to 19 Jan or later, after TP-1 / TP-2 in the bench week (lead times not read). |
| 4 | Glass cloth weight | The skin analysis uses 48 g/m2 (1.4 oz/yd2). The only 38 in cloth I found is 2 oz (about 68 g/m2): about +42 % ply mass. No 1.4 to 1.5 oz at 38 in found. Decide the cloth before TP-8. |
| 5 | Tube interlaminar | No fallback is in the records; P1/P2 stop rule forbids adding material. |
| 6 | Tap test (TP-10) in the go/no-go | Closed (D-236, TP-10b "When / who"): the tap test needs the built airframe, so it is decided after the build and before the first tethered hover and does not gate the 29 Jan 2027 go/no-go. No partial PETG cage and no change to criterion 3 is used. |
| 7 | Pack fit | RDQ 107 x 33 x 46 mm vs a 35 mm slot and 37 mm tray height (T-079 open item). Order only after the CAD fit. |
| 8 | Budget | Section 4.1. The O4b parts leave about $100 to $120; the tests and materials cost more than that. |

## 6. Sources
`CHANGE-LOG.md` D-215 to D-222; `docs/audits/2026-11-20-landing-demand-rootcause.md` s4; `T076d_landing_path.md` s3 to s7; `T076c_hub_al.md`; `T074_check3.md`; `docs/audits/2026-11-19-O4-feasibility.md` s6; `docs/audits/2026-11-20-T080-manufacturing.md` s8, s10; `docs/audits/2026-11-19-T068-decision.md`; `T071_wing_skin.md`; `proofs/claims.a0_base.json`; `docs/reference/jacobs-equipment.md`; `BOM-A.csv`, `bom_a.py`; `T079_cost_closure.md`; `SCHEDULE-A.md`; `AM-009`, `AM-012`, `AM-013` in `docs/spec-amendments.md`. Model values from `prop_a.py` (`full`, run 2026-11-20).

## 7. Limits
All allowables except cited vendor figures are EST. The model gf and A values are the repo's motor model, not a measurement. Push-out loads are hand arithmetic on the nominal diameter. Prices marked snippet or prior are not page reads today. Shipping is the BOM's EST per group, not read from any vendor. Lead times, X7 and Tormach access and charges, the 5 kN rig and the drop-rig logger are "—". The TP-5 and TP-8 pass lines depend on item 1 of s5. The test order after TP-2 is as the brief gave it, not scheduled against real arrival dates.

## Budget-closed purchase list (T-082)

**Adopted total (updated 2026-11-22, T-086 / T-087, D-234 / D-235): $1,939.17 including the crash reserve ($346.94), margin +$60.83 against $2,000 (`python -I redesign/qp/A/bom_a.py`).** Changes since the $1,981.31 / +$18.69 of D-230 / AM-019: T1 hub bar to 2.00 x 2.50 in (T-023 F-2), now Zoro Select 61F2X2.5-12 6061-T6511 $43.29; T11 1 x 4 in bar Zoro Select 61F1X4-12 $33.69; Zoro shipping $5.99 for both (guest cart 2026-11-22), Alcobra line removed; M01 servos 3 -> 2 (no BOM spare; the reserve prices one). Earlier history: it supersedes the $1,957.51 / $1,971.40 of T-082 below (R15, T11, T12, W10, X2216 swap, no spare motor, W01 RDQ 2,800 mAh, V03 H743-Wing). Open: R15 25x23 rib tube from Carbonwebshop (EU, stock not stated, $25 shipping EST): confirm before ordering (T-088); Zoro prices and stock reconfirmed at order time.

Added 2026-11-21 by T-082. Decision record: `docs/audits/2026-11-20-T082-budget.md`, which has every price, URL and lever. Rules: AM-013 to AM-015; the DAF ruling D-223 is folded in. **Plan, not VERIFIED COMPLETE; nothing bought.** Where this section differs from s1 to s4 above, this section supersedes them for purchasing and rigs. Pass lines follow D-223.

**Total (scratch copy of `bom_a.py`, 2026-11-21): $1,957.51 including the crash reserve by its definition ($313.54); $1,971.40 with the reserve held at $327.43. Both are under $2,000 provided the RMRC, Amazon and T-Motor free-shipping terms hold ($36.42; recheck at checkout).**

| ID | Purchase (beyond `BOM-A.csv`, or replacing a line) | Vendor | Qty | Unit $ | Used by |
|---|---|---|---|---|---|
| V03 | Kakute H743-Wing (replaces the F405) | RMRC | 1 | 141.44 | TP-2, TP-3 logger |
| W01 | RDQ 4S 2800 (replaces the Tattu). **Order only after the CAD tray fit** | RDQ | 2 | 54.99 | TP-1, TP-2 |
| T1 | 6061-T6511 bar 2.00 x 2.50 x 12 in (Zoro Select 61F2X2.5-12; was 1.75 x 2.5 Alcobra $49.41, too thin for the 49.3 mm hub) | Zoro | 1 | 43.29 | hub, spare blank, TP-4 / TP-5 sleeves, rig cheek plates |
| T2 | CF sheet 0.5 mm 200 x 300 | Amazon | 1 | 15.98 | FIN-005 (now the D-226 waterjet fin-node bulkheads and plates), FIN-009, WNG-013; N2 and C-4 [WITHDRAWN, D-225] |
| T3 | Glass 1080 1.45 oz 50 in | Wicks | 3 yd | 6.46 | skin (2-ply), TP-8, bond scrim |
| T4 | US Composites 635 + 556 epoxy 16 + 8 oz | US Composites | 1 | 20.20 | skin, all bonds, all coupons |
| T5 | CF strip 3 x 1 mm 1 m | RMRC | 2 | 2.02 | cove strip |
| T6 | APT UHMW tape 1 in x 5 yd 10 mil | Amazon | 1 | 14.99 | pad face, TP-9 |
| T7 / T8 | EVA 1/2 in sheet; closed-cell PE 1/2 in roll | Amazon | 1 + 1 | 23.79 / 24.69 | TP-3 (third candidate: packing PE, $0) |
| T9 | Nano clone (HX711 logger to the laptop) | Amazon | 1 | 13.99 | TP-1, TP-9, rig |
| T10 | Lever-rig hardware (M8 rod, bolts, nuts), EST | Local | 1 | 8.00 | TP-4 to TP-7 fallback rig |
| R14 | 3 mm CF rod (price found) | RMRC | 1 | 2.30 | pins |
| R03 | ELEGOO PETG 1 kg (replaces Prusament) | Amazon | 1 | 12.99 | all PETG parts, C-1 |
| G02 / G05 | re-priced: 2 generic 10 kg cell + HX711 sets, caliper, 0.01 g scale, IR thermometer ($45.15); anemometer ($12.99) | Amazon | 1 / 1 | — | TP-1, TP-9, wind |

Removed: B01 / B02 (R1 bench), B05 (SparkFun group), ADXL375, reamers, PETG cover sheet (cover printed as drawn), the T-081 5 kN frame, and the 2 oz cloth / West kit / 2.5 in bar / Rockwest plate / US Plastic UHMW / Zoro EVA lines. $0 under AM-015: phones, laptop, Jacobs drills (31/64, 9/16, 41/64 in for the bond bores), clamps, drill press, bandsaw.

Test changes:

| Test | Change |
|---|---|
| TP-3 (run first, D-223) | Logger: the H743-Wing IMU (ICM42688 or LSM6DSV, ±16 g) fixed rigidly to the drop mass, ArduPilot raw IMU batch log. **Confirm the rate is >= 1 kHz before the test**; fallback is a ±16 g I2C accelerometer on the Nano (about $5-10 EST). Phone slow-motion gives stroke and rebound. Foams: T7, T8, packing PE. A reading at 16 g saturation is a fail (above A-P5 12 g). |
| TP-1 | **[SUPERSEDED T-083c / AM-019: the motor is the X2216 V3 880KV and there is no spare motor; the flight MN2212 spare is withdrawn]** Flight MN2212 spare + APC. rpm from the blade-pass frequency, phone audio FFT (2 blades: 306 Hz at 9,180 rpm), cross-checked by ESC telemetry if available. Logging: laptop. |
| TP-4 | D-223 interface (doubler s 11-32, tube abs(s) < 11, 45 deg chamfer, build prep), L 32 only, n = 5 push-out + 3 torsion. Sleeves are milled from the T1 offcut and drilled oversize. Rig: ask a Berkeley ME lab for a test-frame loan first. Fallback: plywood lever about 70:1 (20 mm / 1.4 m) on M8 pivots in Al cheek plates, effort read by the 10 kg cell (capacity about 6.9 kN). Calibrate the ratio with known masses and measure the uncertainty u. **Pass: min of 5 >= 4.47 MPa x (1 + u), that is 5.40 kN x (1 + u)**, by break or proof load (3.5 MPa if TP-3 shows zeta <= 0.05, per D-223 s2). Named fallback: credit the 3 mm cross-pins with their own hand and FE rows (analysis, $0). That still needs a CF-wall bearing coupon on the same rig. |
| TP-5 | Same-detail load-ratio test (tube + tapered doubler + chamfered sleeve), n = 5, D-223 s2 line x (1 + u). Plain short-beam set dropped. Pieces come from the R08 / R09 offcuts (about 0.88 of 0.995 m and 0.38 of 0.45 m: little spare). |
| TP-6 [WITHDRAWN, D-225] / TP-7 | Same rig; PETG coupons from the ELEGOO spool; each line x (1 + u). |
| TP-8 | 1080 cloth + 635 epoxy, 1-ply and 2-ply beams; pass r >= 2.26 (2.56 interim). The 2-ply skin (+27 g) needs no extra purchase; re-run A-P3 and the landing rows at the new mass. |
| TP-9 | APT 10 mil face, 10 kg cell. |

Open for Dillon: the reserve by definition is $313.54 versus the old $327.43; X7 material is $0 EST; purchase approval; the ME-lab loan request. Budget risk: margin $42.49 (definition) / $28.60 (reserve held); +30 % growth on the unverified lines gives $2,053.09 (G7, information only).

## T-083c re-spec (2026-11-22; D-227 X2216 swap, D-228 T-083 outcome, D-229 FIN-003 6061 fitting, AM-016 to AM-019)

Plan, not VERIFIED COMPLETE. Nothing bought, nobody has run these tests. Text applied from `mechanism/out/T083_report.md` s10 (proposed text), s2.1 to s2.4, s5.3, and `mechanism/out/T083b_report.md` s3, s4, s9. Category of every model value below: illustrative (repo `prop_a.py` EST thrust model, not a measurement). Stated at 1.913 kg (T-083) unless marked 1.873 kg (T-083b); the reports do not recompute the bench lines at 1.873 kg, so those stay at 1.913 kg and the true line at 1.873 kg is "—" (the 236 s cruise at 1.873 kg, T083b_report s0 row 6, means the derate line there is no higher than 0.889; not computed). Limits not relaxed: A-P3 >= +5 %, A-P2 2.0 / 1.6, A-P5 12 g, A-P6 <= 17.0 m/s, KF 1.725, KP 2.156, RF >= 1.0 at x2.23, total <= $2,000.

**Failure branch (AM-016, replaces "no-go, order O6" in s1):** a failed bench test (TP-1 or TP-2) reopens the configuration (bigger props or motors, or fallback concept B, AM-016); it does not trigger an O6 order. The go/no-go is Fri 29 Jan 2027 (AM-037, D-248; was 2026-12-15); the derate line is the value the as-drawn mass requires (D-228: 0.889; AM-016 had estimated about 0.950 on the earlier mass).

### TP-1 (re-spec): X2216 V3 880KV + APC 9x4.5MR (+ MRP), derate and current (go/no-go)
Model values (prop_a EST; Kv 880, Rm 0.089 ohm, I0 0.5 A; pack R 30 mohm EST):
| State | rpm | thrust per motor (table) | current | Source |
|---|---|---|---|---|
| Sag 14.92 V rest, all four at duty 1.0 | 10,343 | 1,185 gf | 15.15 A per motor, bus 13.10 V | T083_report s2.1 |
| Fresh at the 72 A pack limit (duty 0.993) | 11,358 | 1,434 gf | 18.1 A per motor | T083_report s2.1 |
| Hover, derate 0.93 (at 1.913 kg, T-083) | 7,106 (1P 118 Hz) | about 516 gf | 7.51 A per motor | T083_report s2.1 |

Steps 1 to 4 and 7 as in s2.1 above (the 14.9 V and fresh-pack sweeps; zero the cell; run `bench_analysis.py`). **Step 5:** read thrust at 10,343 rpm, derate = gf(10,343 rpm) / 1,185. **Step 6:** hover hold about 516 gf (at 1.913 kg, T-083), log the motor-base temperature (H-1).
**Pass (at 1.913 kg, T-083):**
- derate >= **0.889** (the 204.6 s cruise need binds first: 1,053 gf at 10,343 rpm; the A-P3 window alone needs 0.824 = 976 gf);
- current at that rpm within +-10 % of 15.15 A;
- rpm at full throttle on a fresh pack <= 11,667 (APC MR limit), rpm from the audio FFT or ESC telemetry;
- one motor <= 24.9 A EST (450 W / 16.8 V x 12.1/13) and <= 32 A for 30 s (maker); the model one-motor-saturated case is 20.08 A.
Cross-check, not a pass line: SunnySky's own 14.8 V table (prop "APC9045", variant not stated) gives 16.3 A and 1,180 gf at 10,972 rpm and is 0.80 to 0.88 of the APC MR rows at equal rpm (T083_report s2.2). **If TP-1 measures about 0.80 to 0.88 the window is +3.5 to +8.3 % and the cruise 157 to 200 s, so the bench can fail A-P3 (window >= +5 %) and the cruise need** (T083_report s2.1 sensitivity, at 1.913 kg: 0.88 -> +8.3 % / 200 s; 0.85 -> +6.6 % / 185 s; 0.80 -> +3.5 % / 157 s). The X2216 must not be held below about 15 A in flight (one-motor line 15.0 A -> window +4.9 %). Failure branch: above.
Gaps (unchanged): no rpm sensor, one motor only so the all-four pack current (73.3 A uncapped / 72.0 A at the limit EST) is not measured in TP-1.

### TP-2 (re-spec): current limiter and sensor on the H743-Wing (go/no-go)
**D-256 (2026-11-24, AM-060):** the Lua spin-cap script `spin_cap.lua` is dropped from the build: since the X2216 (D-227) its table and failsafe are 1.0, so it only re-wrote the `Q_M_SPIN_MAX` 1.0 already in A.param. No script is loaded (`SCR_ENABLE` 0); the cap-versus-voltage checks are removed.
Settings: `Q_M_BAT_CURR_MAX` 72, `Q_M_SPIN_MAX` 1.0 (no script), BATT_CAPACITY 2800, BATT_LOW_MAH 790, BATT_CRT_MAH 420 (T083_report s2.4; the 0.90 failsafe would cut the sag window to +4.6 % without download, `gate_prop_sched.txt`).
**Pass:** `Q_M_SPIN_MAX` reads 1.0; the battery-current limiter holds <= 72 A with four motors at full throttle on a fresh pack (needs a 4-motor stand or the built aircraft tethered); the H743-Wing current sensor reads to >= 80 A (its range is "—", not read; read it before Order 1). Connector: XT90 (90 A = 1.25 x 72 A, BOM W10); XT60 60 A momentary fails (T083_report s2.1).
**Before the first powered test (T-092 / D-240, review round 4):** read the ArduPilot `INS_POS1_X/Y/Z` definition and confirm its reference point (the params assume the CG, `A.param` l.268-273); measure the IMU chip position on the Kakute H743-Wing (now "—", EST +-10 mm) and the built CG (T-A-CG-BREADBOARD), then reset INS_POS1 from the measured values.
Also open for the bench: the A-P10(b) forced-response sweep (6,000 to 10,500 rpm) must be extended to 11,400 rpm (full duty 11,358 rpm), and 1P at hover (118 Hz) is now at the top of the hover band 100 to 119 Hz (T083_report s2.1).

### TP-3 (re-spec): pad zeta acceptance, the gate for the landing rows
The D-226 cell, struts and clamps as drawn pass only with a pad whose damping ratio is **zeta <= 0.05** (T083_report s5.3; T083b_report s4.3). Pad plateau **36 N at 24 mm usable** (T-083; 33.6 N would tilt 3.14 deg), drop at 1.913 kg (T-083) on the guided rig of s2.3; the per-foot specimen masses 0.41 / 0.82 kg and the logger (H743-Wing IMU, rate >= 1 kHz to confirm) are unchanged.
Model results the test must reproduce or beat (rigid-body dynamics; at 1.873 kg / CG 22.26 mm, T083b_report s4.3): stroke 20.44 mm, end tilt 2.82 deg (limit 3.0), n 8.90 / 10.44 / 12.90 g at zeta 0.02 / 0.05 / 0.10 (A-P5 12 g: **fails at 0.10**). Landing rows on the T-083 demand at x2.23: whole D-226 cell, rib, bridge, strut and R4 clamp min **1.09** at zeta 0.05 (R4 junction; T083b_report s4.3); at zeta 0.10 min **0.66** (centre flange bond C3), 9 row groups fail (T083_report s0 row 3a).
**[T-098 rev 2, D-243: for the drawn 30 mm pad the acceptance is the joint (Fp, zeta) region of s2.3 (Fp 37.5-39.0 N, zeta 0.02-0.05, usable stroke >= 20 mm); the 36 N / 24 mm figures below apply to the lengthened pad only.]** **Pass:** zeta <= 0.05 measured (target 0.02), plateau 36 N, usable stroke >= 24 mm, A-P5 n <= 12 g. **Fail:** zeta > 0.05: the landing rows do not pass; the options are a new foam or geometry, or regrowth of the cell (T083_report s5.3; fitting alone at zeta 0.10: wall 1.3 mm, ring 60 mm, 17.92 g each, min 1.01, T083b_report s3 note c, only worth doing with the cell regrowth). This is a test gap, not a design change made by T-083c.

### TP-4 (re-spec, added coupon): 6061 root fitting FIN-003 bonds, plus the existing CF-in-Al push-out
Existing TP-4 (CF-in-Al push-out, s2.4 and the T-082 section) is unchanged. Added (T083b_report s2, s3, s9): epoxy bond coupons covering the machined 6061-T6 root fitting FIN-003 (ring OD 18.2 / bore 16.2 x 38 mm on the 16x14 fin tube; plug OD 22.8 / ID 20.8 x 31 mm inside the 25x23 rib end; 2.0 mm end plate):
| Coupon | Specimen (n = 5 each, proposal) | Allowable used in the rows | Row RF at x2.23, zeta 0.05 | Source |
|---|---|---|---|---|
| Plug-in-rib shear (Q7a) | 6061 plug piece in a 25x23 CF rib end, L 31 mm, push-out | epoxy 2.0 MPa EST (same as the CGE-006 6061 flange bond C3) | 1.78 | T083b_report s3 |
| Ring-on-tube shear (Q1a) | 6061 ring on a 16x14 CF tube, L 38 mm, push-out | 2.0 MPa EST | 2.05 | T083b_report s3 |
| Ring and plug **peel** (Q1c / Q7c, integrity class, outside the RF minimum by T-069 F-3) | peel coupons of the same prep | assumed peel allowable not stated in T083b: "—" | 0.16 / 0.15 | T083b_report s3 |
| CF wall bearing | CF tube wall bearing on the ring (fin tube) and on the plug (rib wall) | allowable "—"; the rows put **12.4 MPa** (fin tube in the ring) and **13.2 MPa** (rib wall on the plug) at x2.23, zeta 0.05 | record only | T083b_report s3 |
Prep as the build: abraded 6061 + acetone (T083b_report s2). **Pass (proposal):** mean shear min of 5 >= 2.0 MPa on both shear coupons; CF wall bearing >= 13.2 MPa (rib) and >= 12.4 MPa (fin tube) on the x2.23 basis, without failure; peel: the measured peel strength raises Q1c / Q7c to >= 1.0 or a 60 mm ring (+3.2 g each, T083b_report s3 note b) is adopted. Fail: lengthen the ring (60 mm) or add a bond line; reviewer rules. Same frame as the s2.4 coupon (force frame loan or the lever rig, T-082).
Rib torsion coupon (T083_report s10): the line rises from 79 to about 92 MPa at zeta 0.02 (99 MPa all zeta, EST) on the T-083 demand. The 14x12 rib case: T-083's root-block socket bond D14 x 31 needed about 47 mm (EST) and was the PETG block, which D-229 replaced; the 14x12 rib with the 6061 fitting is not computed ("—"), and the 14x12 variant would need another cage move (T083b_report s4.1). Test rows TP-12 to TP-14 follow (T-081 re-check G-1 to G-3, added 2026-11-22). Their specimen count n = 5 is a proposal copied from the coupons above; no report gives an n.

#### TP-12 (new): rib torsion coupon (D-226, saddle-loadpath SL-4; closes G-1)
| Item | Value |
|---|---|
| What it closes | Whether the rib may be the lighter 14x12 tube (about -23.8 g against 25x23, saddle-loadpath s2) instead of the drawn 25x23. D-226: "rib 25x23 unless a torsion coupon shows >= 79 MPa"; T083_report s10 re-states the line for the T-083 demand. |
| Specimen | Offcuts of the BOM R09 14x12 tube, n = 5 (proposal), length per the lever rig |
| Rig and instrument | Plywood lever rig of the T-082 section (about 70:1 on M8 pivots in Al cheek plates), effort read by the 10 kg cell (G02) and the HX711 / Nano (T9); torque = effort x lever arm; in-plane shear stress by the thin-wall tube formula tau = T / (2 pi r_m^2 t) (r_m and t from caliper readings) |
| **Pass** | **Measured in-plane shear allowable (min of 5) >= about 92 MPa** (T083_report s10: 79 -> about 92 MPa at pad zeta 0.02 on the T-083 demand, EST; 99 MPa at all zeta). Basis: zeta 0.02 (the TP-3 target). The line at zeta 0.05, the TP-3 gate, is not stated in the reports: "—". The old 79 MPa line is superseded. |
| On fail | Keep the drawn 25x23 rib (R15). |
| If it passes | 14x12 is still not adopted automatically: its root-block socket bond (D14 x 31 mm, RF 0.67, about 47 mm needed, EST, T083_report s3b) was for the PETG block replaced by D-229, and the 14x12 rib with the 6061 fitting is not computed ("—"); a reviewer must re-run it first. |

#### TP-13 (new): rib-to-CF-bulkhead bond (D-226; closes G-2)
| Item | Value |
|---|---|
| What it closes | `docs/audits/2026-11-21-saddle-loadpath.md` s3 row "Rib to bulkhead": RF 0.90 at L 99.5 mm (2.21 MPa), 1.16 at L 113 mm (1.73 MPa), "needs a 4-ply 0/90 wrap, or the plates extended to the rib top (EST)". The row was computed for the 14x12 rib; for the drawn 25x23 rib it is not recomputed ("—"). |
| Specimen | A rib end bonded to a 0.5 mm CF bulkhead (T2) with two 7 mm epoxy fillets (T4, T12 flox): n = 5 as drawn and n = 5 with the 4-ply 0/90 glass wrap (T3) |
| Rig and instrument | Lever rig as TP-12 or the borrowed force frame; effort from the 10 kg cell; load applied as the moment and shear taken out over the bond length L |
| **Pass** | **Fillet shear stress at failure, min of 5, >= 2.21 MPa for L 99.5 mm (the s3 demand at x2.23, RF 1.0) or >= 1.73 MPa for L 113 mm.** The 2.0 MPa epoxy value behind RF 0.90 is an EST allowable (s3), so the test replaces it. No margin beyond the x2.23 already in the demand is stated in the source: "—". |
| On fail / adoption | As drawn (no wrap) is expected to fail (RF 0.90); the wrap is then the adopted fix and the wrapped specimen must pass the same line. If it still fails: extend the plates to the rib top under the FIN-006 fairing (EST, mass "—") or use L 113 mm; reviewer rules. |

#### TP-14 (new): CF wall bearing in the 6061 socket (D-226 "socket bearing '—'"; closes G-3)
| Item | Value |
|---|---|
| What it closes | Saddle-loadpath s3 row "Bridge CF wall bearing in the 6061 socket": demand 48.5 MPa on the CF wall (6M/(D L^2) + V/(D L), P7.2 N6 equivalent); allowable "—". SL-5: add it to the TP-4 coupon. CF plate shear and bearing allowables are also "—" there; no number is given for them in the sources. |
| Specimen | 16x14 CF bridge tube (R02 offcut) in a 6061 socket piece (T1 / T11 offcut), same prep as the TP-4 push-out (abraded, acetone), n = 5 (proposal), tested with the TP-4 coupon sets |
| Rig and instrument | As TP-4: force frame >= 5 kN (missing) (AM-030: not bought) or the lever rig of T-082; cell for effort |
| **Pass** | **Bearing stress on the CF wall at failure (min of 5) >= 48.5 MPa** (the s3 demand, RF 1.0), no wall crushing at that load. The CF wall bearing allowable has no source value ("—"); the test sets it. |
| On fail | Longer socket than drawn or a bonded wall doubler; the reviewer rules and the saddle-loadpath row is re-run. |

### TP-10b (new, T-085): T-A-TAP: modal tap test of the built airframe (D-185 (a), A-P10(a) and (c))
Why a test: the beam FE puts the governing mode at 84-107 Hz (band edge 94 Hz) or places strong modes at 230-330 Hz depending on the wing cell, the pack on its tray and the hub joint, none of which it can settle (`T085_report.md`, `T066_record.md` s5). D-185 (a) is therefore judged on the measured modes; the rule is not changed.
**Method (category: test; the processing is the FE metric applied to measured driving-point data).**
| Step | Action |
|---|---|
| 1 Setup | Fully assembled airframe as flown (4 motors with props and nuts, ESC, FC, wiring, pack on the tray with both straps and the pad, fins, pack at the nominal tray position). Weigh it (G02 scale) and mark the pack position. Hang it free-free from two soft elastic cords (bungee loops, 0.6 m or longer) round the spar at |y| 0.15 m, level, nose up not required: the rigid-body hang modes must be < 2 Hz (check by one tap and the FFT; if not, lengthen the cords). The FE is free-free. |
| 2 Sensor | The H743-Wing IMU (V03) is the accelerometer: take the FC off its stack and tape it (rigid, 3 axes aligned to x aft, y right, z up) to the station being tested; log the raw IMU batch (ArduPilot `INS_LOG_BAT_*` raw batch logging). **Confirm the logged accelerometer rate is >= 2 kHz and the range is not clipped by the hit before the test** (D-223 / TP-3 rule); if not, use a +-16 g I2C accelerometer on the Nano (about $5-10 EST, not in the BOM, so a purchase to approve). Phone accelerometers are not used (rate about 400 Hz or less, below the 321 Hz band edge needs). Mass of the FC and tape stays on the station; the FE lump is corrected by the weighed mass. |
| 3 Impulse | Pendulum hammer released from a fixed angle (fixed height, marked) at the motor cup (X-mount plate) so the hit is at the driving point. Calibrate the impulse I (N s) by hitting the 1 kg reference mass hung free with the FC on it: I = m x (peak velocity change = integral of the logged acceleration); repeat 5 times, I is the mean, u_I the scatter. A soft tip lengthens the pulse to about 2-4 ms (flat to > 100 Hz only: check the pulse width on the reference mass; use the hard tip for the 100-400 Hz band). **Bandwidth check on both: the reference mass AND the motor cup.** The reference-mass hit gives the pulse of that contact only; a hit on the stiff installed cup is shorter. So also hit the installed cup (airframe hung, FC on the cup, hard tip), log the impulse record, and take its spectrum: the usable band is where the spectrum has not rolled off by more than 3 dB (team criterion, EST) from its low-frequency level and stays above the IMU noise floor. It must reach 321 Hz on the cup; if not, change the tip or the release height. A mode above the usable cup band is reported as "not measured" and counts as undecided (step 6), never as a pass. |
| 4 Driving points | Four motor stations (UR, LL, LR, UL), three axes each: hit along x (thrust), y, z at the station while the FC sits on the same cup: 12 sets, 5 hits each (60 hits), 2 s record per hit. Plus one set each at the hub (x, y, z) and on the pack (z) for the shape check. |
| 5 Processing | For each record fit the sum of decaying sinusoids (or read the FFT peaks, then a half-power / log-decrement damping zeta_k): the acceleration amplitude of mode k at the driving point is A_k = omega_k x phi^2 x I, so **phi_ik^2 = A_k / (omega_k I)** (mass-normalised, kg^-1; the same quantity as the FE `v` squared). cx_k = sqrt(sum over the 4 motors of phi_x^2), cy_k = sqrt(sum over the 4 motors of (phi_y^2 + phi_z^2)): the FE definition used in `structures_a.py`. u = sqrt(u_I^2 + (scatter of A_k over the 5 hits)^2 + (0.10 sensor-mass allowance EST)^2), as a fraction. |
| 6 Pass rule | **D-185 (a), unchanged: no mode in 94-321 Hz (hover 1P / 1.2 to cruise 2P x 1.2) with cx or cy >= 0.5.** Applied to the measurement as: pass if every mode in the band has max(cx_k, cy_k) x (1 + u) < 0.5; fail if any mode has max(cx_k, cy_k) / (1 + u) >= 0.5; between the two the mode is "undecided" and counts as a fail until the FE with the stiffness updated to the measured frequencies (change the hub-joint and tray / pad stiffness only, keep the CAD masses) gives cx, cy < 0.5 for it. A mode seen only at one motor station (phi^2 at one motor >= 0.25 kg^-1 alone) is strong by itself. |
| 7 A-P10(c) | Every measured mode in 10-400 Hz within +-20 % of the FE (the corner that brackets it: kd / nom / hi). [T-091 wording update: the window starts at 10 Hz, not 60 Hz, so it covers the modes that set the pitch gain margin on the T-085 model: bridge mode 16-18 Hz, first symmetric wing-flap / cage mode **26.8-29.7 Hz** (the closed-loop pole that limits the pitch GM, `T089_report.md`), 42-47 Hz, and the 94.6-108.7 Hz wing-flap / cage-bounce mode (D-185 governing mode, `T085_report.md`); the iteration-2 cage windows 9-17 Hz and 21-43 Hz are superseded. Also record the damping zeta of the 27-30 Hz and 94.6-108.7 Hz modes: the T-089 forced response and pole position assume zeta 0.3-1 % (EST).] Modes that move more than 20 %: re-run the rate-loop gain-margin check with the measured frequencies (`fu_cage.py` method, D-191). |
| 8 Record | Frequencies, zeta, phi^2 by station and axis, I, u, the hang-mode frequency, the FC rate, photographs of the hang; the impulse spectra (reference mass and cup) with the usable band, one table in `T-A-TAP` evidence. |
| Equipment | In the BOM: FC (V03), motors and props, G02 scale + caliper. $0: pendulum hammer, 1 kg reference mass (weighed on G02), bungee cords, laptop and Python. Not in the BOM, only if the IMU rate fails: a +-16 g I2C accelerometer ($5-10 EST). No force hammer, force frame or purchase is needed (the impulse is calibrated on the reference mass). |
| When / who | After the build and before the first tethered hover (the VIBE check in A-P10(d) is the second line); about 0.5 day, 2 people, team lab or the Jacobs makerspace. The result closes the D-185 (a) row; the test does not gate the 29 Jan 2027 go/no-go (s0 item 6). |

### TP-11 (new): A-P6 stall, CLmax measurement (gates A-P6, not the 29 Jan 2027 go/no-go)
A-P6 (DERIVED): clean stall Vs <= cruise / 1.3. Vs = sqrt(2 m g / (rho S CLmax)), S 0.22 m^2, rho 1.225, CLmax 0.75 EST gives 1.3 Vs = 17.71 m/s at 1.913 kg (T083_report s2.3) and **17.53 m/s at 1.873 kg** (T083b_report s0), both > 17.0. D-228: A-P6 is gated by a measured stall; **pass line CLmax >= 0.81**. (T083_report s2.3 needs 0.81 at 1.913 kg by 2 m g / (rho S (17/1.3)^2); the same formula at 1.873 kg gives about 0.80, arithmetic by T-083c; the line stays at 0.81, not relaxed, per D-228.) A cruise-speed re-derivation alone has zero margin (196 s available against 196 s needed, T083_report s2.3) and is not used.
Specimen and rig (decided T-083c, 2026-11-22, engineering team): **in-flight stall of the built aircraft**. A wind tunnel for the wing panel is not on the Jacobs list (`docs/reference/jacobs-equipment.md`), so that option is dropped. Method: wing-borne flight at >= 40 m AGL, calm air (wind <= 3 m/s), a 1 g power-off deceleration at about 1 m/s per s until the stall break or the elevon stop; Vs from the on-board airspeed sensor (BOM V05, MS4525, calibrated against GPS ground speed in two opposite legs); three runs, the lowest CLmax is used. Recovery: switch to the VTOL hover mode (quad motors) at the break, as in the transition test. Mass at the test is weighed; CLmax = 2 m g / (rho S Vs^2), rho from the day's temperature and pressure. Needs the built wing, so it cannot run before the wing is built (first cut from 26 Jan 2027, SCHEDULE-A B1; was 15 Dec).
**Pass:** CLmax >= 0.81. **Fail:** A-P6 stays failed; the configuration reopens per AM-016 (bigger props or motors, or fallback concept B) or the cruise speed / wing area / mass is re-derived; the team and reviewer rule, Dillon is told (the mass ceiling at CLmax 0.75 is 1.762 kg, T083_report s2.3).

### TP-15 to TP-18 (new, T-094, 2026-11-23): elevon linkage and horn bench tests (decide the run_all FAIL claims on the horn / rib / elevon)
Added by T-094 (category: test plan; no analysis is run here). Demand values are the claims' own (`proofs/claims_a2_struct.py` l.188-194 and the test-form claims below l.205, `mechanism/out/linkage_loads_check.json`, `docs/analysis-records.md` l.244): hold force 17.05 N x 2.156 = 36.8 N along the chord; servo stall force 51 N (0.397 N m / (8.5 mm x 0.916)); elevon hold torque 0.161 N m (2.156 x 74.65 N mm). The analysis FAILs are foam shear 431.8 / 860.9 / 504.3 kPa against 85.8 kPa (EST) and bearing 36.65 MPa against 20 MPa (EST). A foam stress cannot be read on a coupon, so the test decides the claim as the claims' own `how` text says: the demand load is held with no crack, slip or set, which replaces the analysis FAIL (the logged re-point of the claim is a separate edit, not done here). Order: TP-15 (a), TP-16 and TP-17 on foam / printed coupons **after the main order arrives, before the wing build** (needs main-order lines R01 foam, R05 / T4 epoxy, M02 linkage, M01 servo and T10 lever hardware; Order 1 holds only G02, G03, R03; review round 7); TP-15 (b) and TP-18 **after the build** (BUILD D5b). No equipment is bought (AM-030).

| TP | Decides (claim ids) | Specimen, n, order | Rig and instrument | Load and **pass** | On fail | When |
|---|---|---|---|---|---|---|
| TP-15 free play | `CL-A-LINKAGE-FREEPLAY` (1.28 deg budget against <= 1 deg, SERVO.md s4 flutter guide; the only sourced number, review r3 m-7) | (a) bench coupon first: servo arm + M02 rod + printed horn + hinge on the Z-bend, n = 3 assemblies; (b) then the built elevon + linkage, each of the 2 elevons | Servo locked at neutral (powered and holding; horn clamped for (a)). Dial gauge (+-0.05 mm per the claim) on the trailing edge, or on the horn hole radius 9.155 mm (`HORN_R`, cad/amodel/electrical.py l.655) if the TE is not reachable. **A dial gauge is not in BOM-A.csv: borrow from Jacobs or the shop, else a laser pointer on the TE and a ruler at a measured distance ($0); availability "-"**. Push the TE by hand to each end of the play, read the total travel x at radius r (caliper) | Free play = atan(x / r). **Pass: <= 1.0 deg on each of the 3 coupons (a) and each built elevon (b)** (x <= 0.01745 r mm: 0.160 mm (= r x tan 1 deg; at the trailing edge use the measured hinge-to-reading radius r, which is preferred: a +-0.05 mm gauge is 31 % of the limit at the horn hole) at r = 9.155 mm). Servo gear backlash and cheek holes are "-" in the 1.28 deg budget, so on (b) record the servo included and, with the servo unpowered and the horn clamped, the linkage alone | Above 1 deg: the claim stays FAIL; options are tighter arm / horn holes (0.10 mm now), a shimmed Z-bend, or a measured-flutter case; reviewer rules | (a) after the main order arrives, before the wing build; (b) at BUILD D5b |
| TP-16 horn-rib coupon | `CL-A-HORN-RIB-FOAM-HOLD` (36.8 N), `CL-A-HORN-RIB-FOAM-STALL` (51 N), `CL-A-HORN-BEARING-STALL` (51 N on the clevis pin hole). Same coupon as `T-A-HORN-RIB` steps 1 and 2 (`CL-A-HORN-RIB-COUPON`, `CL-A-HORN-STALL-STEP`) | 100 mm span of the real elevon foam with its tape skin, the printed 2 mm PETG horn rib bonded in its slot with the build epoxy, the real clevis pin; **n = 3, lowest governs** (the 1.4375 stall scatter factor is not in a single coupon); run coupons 1 to 3 in order | Clamps 50 mm each side of the rib; load along the chord through the clevis pin by the lever rig (T10 hardware, G03 stand parts) with the effort read by the G02 10 kg cell (98 N full scale, 51 N is inside it); caliper; 1.2 mm pin gauge (a drill shank; "-" if not in the shop) | Step 1 **36.8 N for 30 s, no crack, no slip, set < 0.5 deg**; step 2 then **51 N for 5 s, hole elongation <= 0.1 mm** (pin gauge), no crack, set < 0.5 deg. Record what yields first (foam face, rib, hole). Local result only (clamps 50 mm from the rib; about 160 mm of elevon in flight) | Foam face fails: longer or deeper rib or a bonded skin patch, or limit the horn force (servo torque limit); hole elongates: bush the hole or a thicker horn (PETG allowable is EST). Any change re-runs the claims | After the main order arrives, before the wing build (printed and foam coupons) |
| TP-17 elevon torsion | `CL-A-ELEVON-TORSION-FOAM` (foam only; the tape skin is credited only by this test, `CL-A-ELEVON-TORSION-COUPON`) | Tape-skinned elevon section about 160 mm long, root clamped; **n = 3, lowest governs** | Torque applied through the horn hole path (force x 9.155 mm); lever rig, G02 10 kg cell, a known weight on the lever arm as the check; caliper at the TE for the twist set | **0.161 N m held 30 s (0.161 / 0.009155 = 17.6 N at the hole), no tape debond or crack, twist set < 0.5 deg at the TE** | The spanwise CF tube in the elevon (trade row J of the linkage trade table); re-run | After the main order arrives, before the wing build |
| TP-18 bench stall, built | `CL-A-HORN-BEARING-STALL`, `CL-A-HORN-RIB-FOAM-STALL` on the real part (also loads `CL-A-HORN-STALL-BENCH`, `CL-A-HORN-SHEAROUT-STALL`, `CL-A-KEEPER-BRIDGE-STALL`) | Each built elevon, BUILD D5b | Servo at 7.2 V driven into the +21 deg stop (endpoints temporarily past the stop; smallest arm lever, 51 N) for 5 s; pin gauge, caliper, eye for cracks in horn, rib, slot tape, keeper | **51 N for 5 s, hole elongation <= 0.1 mm, no crack in horn / rib / slot tape / stop / keeper, TE set < 0.5 deg**; then endpoints back to +-20 deg | Strengthen per the TP-16 fail row; no flight | After the build, before the first tethered hover |

Equipment: G02 10 kg cell + HX711 + caliper (BOM), T10 lever-rig hardware, G03 stand parts, hand tools. Not in the BOM, "-" and not bought: dial gauge (borrow; laser-pointer fallback), 1.2 mm pin gauge (drill shank). The lever ratio is calibrated with known masses and gives an uncertainty u (as TP-4); the load factors above are the claims' own, each x (1 + u).

### Sources for this section
`mechanism/out/T083_report.md` s2.1 to s2.4, s5.3, s10; `mechanism/out/T083b_report.md` s0, s2 to s4, s9; `docs/spec-amendments.md` AM-016 to AM-019; `CHANGE-LOG.md` D-227, D-228, D-229.

### TP-19 (new, T-101): first-transition flight-card step: CRUISE switch timing and TECS setting
Added 2026-11-23 (T-101); reworded 2026-11-24 for the 0.25 chord after D-250 was superseded by D-251 (reverted). Category: test plan; no analysis run here. The C3 SITL runs (pitch use 0.554 Z5, 0.571 Z5+Lua, 0.651 T-074, 0.605 T-074+Lua; AR-017) used a pilot-procedure change and one parameter, both of which must be on the first-transition flight card (AR-017 s diagnosis: the peak came from the 3 s entry-throttle hold, the airspeed overshoot to 20.5 m/s and the CRUISE-mode TECS throttle chop and pull-up, pitch -4 to +9 deg, q about 18 deg/s).

| Item | Value |
|---|---|
| Procedure | After the "Transition FW done" message the pilot switches FBWA -> CRUISE **1.0 s** later (the T-097 harness used 3.0 s; `fw_hold=1.0` in `sitl/run_fwd.py`). Throttle is not held at the entry value beyond that. |
| Parameter | `TECS_SPDWEIGHT 0.5` (stock default 1.0; 0 = height only, 1 = balanced, 2 = speed only, ArduPilot TECS tuning guide, read 2026-11-23). It is a line in `redesign/qp/A/A.param`. Bench check before flight: read the parameter back from the loaded board (GCS parameter list or parameter dump) and compare with `A.param`; the card is not signed until the dump shows 0.5. |
| Log | Elevon outputs SERVO5 and SERVO6 (microseconds, convert to degrees about the bench-set trim and endpoints); airspeed (MS4525, BOM V05) and groundspeed; pitch and pitch rate; throttle output and TECS log messages; time stamps of the "Transition FW done" message and the mode change. Keep the BIN log. |
| **Pass** | **Peak mean elevon deflection <= 9 deg (= 0.60 of 15 deg), taken as max of the mean of the two elevons, measured from zero command (the `fwd_sum.py` metric), from the FBWA switch until 20 s into CRUISE.** The C3 SITL runs gave 0.554 / 0.571 / 0.651 / 0.605 of 15 deg (Z5, Z5+Lua, T-074, T-074+Lua; AR-017). The pass line is still peak mean elevon <= 9 deg (0.60 of 15 deg); the worst C3 case 0.651 is ABOVE it (open, pending the reserve derivation, D-251). One sample per case, scatter 0.01-0.03 of 15 deg. |
| Abort rule (EST, team line, not derived from a flight measurement) | If, after the CRUISE switch, the airspeed rises past 20 m/s (the 20.5 m/s overshoot of the T-097 harness) or the pitch goes beyond +-15 deg or the pitch rate exceeds about 18 deg/s (the SITL transient), the pilot switches to QHOVER / QSTABILIZE (VTOL motors) at once, as in the TP-11 recovery, and the card is not repeated until the log is read. The 20 m/s, 15 deg and 18 deg/s figures are EST thresholds taken from the AR-017 diagnosis, not tested. |
| If the pass line fails | The claim CL-A-PITCH-USE flight value stays open; the team and reviewer rule. Untried controls (D-249): TECS_SPDWEIGHT 0, TECS_PTCH_DAMP 0.2-0.3, a CRUISE switch only once the pitch rate is near zero; each is the same lever, so the margin is weak evidence (D-249). |
| When | First transition flight, after the tethered hover; a flight item that does not gate the 29 Jan 2027 go/no-go (EST scoping, the team confirms). |
| Source | D-251 (D-250 superseded, reverted); AR-017; `redesign/qp/A/mechanism/out/T101_results.json`; `docs/audits/2026-11-24-T101-revert.md`. |

### Flight settings (D-255, 2026-11-24, T-101)
For every flight from the first cruise sortie on: **battery pack at the aft end of its tray slot** (10 mm aft of nominal, CG 23.49 mm aft of the LE EST, inside the A-P4 band 19-26 mm; weigh and balance on the built aircraft, T-A-CG-BREADBOARD); A.param `AIRSPEED_CRUISE` 18, `AIRSPEED_MAX` 20, `RLL2SRV_RMAX` 45, `RLL2SRV_TCONST` 0.9 (with the C3 transition controls, D-249). First cruise logs check: elevon pitch use <= 9 deg mean (TP-11 / TP-19 rows above), cruise throttle duty below the THR_MAX 68 ceiling (headroom 0.2-0.7 m/s EST), bank overshoot in roll reversals.
