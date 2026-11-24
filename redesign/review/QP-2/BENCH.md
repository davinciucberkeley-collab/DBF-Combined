# QP-2 bench kit, procedure and pass lines for concept A (H1 + E1 + I1), 2026-11-14

Files: `redesign/qp/A/bench/` : `ORDER-LIST.csv`, `order_total.py` (totals), `DATASHEET-TEMPLATE.csv`, `bench_analysis.py` (logs to pass / fail table; `--selftest` runs on synthetic data and checks the script only). Nothing ordered, built or run; no git. Labels: `V` vendor page read today, `U` snippet or unread, `EST` estimate, `—` unknown. Prices checked 2026-11-14.

## 1. Order list (user places the order)

| # | Item | Qty x unit | Flag | Stock today | URL |
|---|---|---|---|---|---|
| O1 | T-Motor MN2212 V2.0 KV780 (flight stock) | 2 x 46.90 | V | Add to Cart shown, no stock figure | https://store.tmotor.com/goods-388-MN2212-V20.html |
| O2 | T-Motor T9545 prop pair (flight stock) | 2 x 10.42 | U | **sold out** in listing; unread (pyrodrone, 3dxr gave 429) | https://rcdrone.top/products/t-motor-t9545-a-b-2pcs-pair-prop-self-tightening-ing-propeller |
| O3 | Holybro Tekko32 F4 45 A single ESC, AM32, DShot150-1200, telemetry, 2-6S, 5.8 g (flight stock) | 2 x 22.50 | V | in stock | https://www.readymaderc.com/products/details/87186-holybro-tekko32-f4-45a-esc-am32 |
| O4 | Tattu 2300 mAh 4S 75C (flight pack 1 of 2) | 1 x 37.09 | V | in stock | https://www.readymaderc.com/products/details/tattu-2300-75c-4s1p-xt60 |
| O5 | SunnySky X2212 KV980 CW (R1 candidate, $15.99 is under the $25 line) | 1 x 15.99 | V | in stock | https://www.readymaderc.com/products/details/sunnysky-x2212-kv980-multirotor-cw |
| O6 | Holybro 1045 prop set (10x4.5, 2CW + 2CCW) | 1 x 12.99 | V | in stock | https://www.readymaderc.com/products/details/87244-holybro-1045-propeller-set-2cw-2ccw-x500-s500-spare-parts |
| O7 | SunnySky 9045 prop pair (stand-in while T9545 is sold out) | 2 x 2.99 | V | in stock | https://www.readymaderc.com/products/details/sunny-sky-9045-prop-x2212 |
| O8 | Higher-pitch 9 in prop for C7 (9x6 class) | 1 x 5.00 | EST | — | none read |
| O9 | SparkFun TAL220 10 kg bar load cell (replaces G06's 20 kgf cell, same price, 2x finer for a 0.9 kg thrust) | 1 x 12.95 | V | in stock | https://www.sparkfun.com/load-cell-10kg-straight-bar-tal220.html |
| O10 | SparkFun HX711 amplifier | 1 x 4.95 | V | in stock | https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html |
| O11 | H1 `G12` 1 kgf bar cell + HX711 + K-type probes (torque arm 0.100 m; needed for the yaw check) | 1 x 17.00 | EST | page not opened | https://www.amazon.com/dp/B0F52QCK3T |
| O12 | H1 `G04` 150 A watt meter | 1 x 12.99 | U | Amazon 503 today | https://www.amazon.com/dp/B0F13JWDFV |
| O13 | Arduino Nano or clone (HX711 read + servo-PWM throttle; drop if the Kakute is on the bench) | 1 x 8.00 | EST | — | — |
| O14 | Fixture: 2 x 608 bearings, plywood, M3/M6 hardware; motor mount printed free at Jacobs | 1 x 15.00 | EST | — | — |

Reuse: O9-O14 are the K09-L GT-01 stand (`team/H1/GROUND-TEST-PLAN.md`), same layout, thrust axle in 608 bearings, torque arm 0.100 m, 60 s zero step, rules for props-on cards. `G04` and `G12` are H1's own lines (`team/I1/BOM.csv`); if the team already owns them, subtract. The ESC fills the board's "DShot ESC not sourced" gap (QP-1 s1 item 3). Bidirectional-DShot rpm on the Tekko32 is not stated on its page, so rpm comes from audio FFT plus telemetry if the FC reads it (H1 GT-01 already specifies both).

Totals (`python -I order_total.py`; tax 10.25 % and shipping lines from COST.md, EST):

| Group | Goods | With tax | With shipping (EST) |
|---|---|---|---|
| Flight stock (O1-O4: motors, props, ESCs, pack; reused in the aircraft) | 196.73 | 216.89 | 227.60 (T-Motor 10.71) |
| Bench-only (O5-O14) | 110.85 | 122.21 | **155.92** (RMRC 15 + SparkFun 8 + Amazon 10.71) |
| Bench-only net of lines COST.md's floor already holds (watt meter, load cell/HX711 F11a/F11b, Nano) | | | 113.05 |
| R1 minimum only (O5 + O6) | 28.98 | 31.95 | 46.95 |

**This is more than the board's ~$32-60.** That figure matches the R1 pair plus a little; the stand, torque cell, ESCs and shipping were not in it. Bench-only is about $156 gross, $113 net of floor lines, and $228 more is flight hardware that is not wasted. Against A's margin (+$501, +$387 at +30 %) the bench-only cost is 22-29 % of margin and is the cheapest reduction of R1 / R3 uncertainty. A leaner cut: O5, O6, O9, O10, O11, O13, O14 only ($95 goods, drop the spare props, watt meter and 9 in comparators).

Open ordering items: T9545 has no in-stock US source read (O2); if none, run on 9045 first (derate comparator) and ask `onlinesales@tmotor.com` for the 9545B. The maker's A/B naming is unresolved. Self-tightening prop adapter fit on the MN2212 is `—`.

## 2. Procedure (adapts TEST-PLAN-QP1 QP1-2 and K09-L GT-01/GT-02; rules for props-on cards unchanged: nobody in the prop plane +/-30 deg, hard kill within reach, pack in a bag, full steps <= 2 s then >= 60 s idle, thrust corrected to rho 1.225)

0. **Rig (GT-01).** Calibrate thrust cell with 0.5/1.0 kg hangs and torque cell with 50-500 g at the 0.100 m mark; 60 s zero, 80 SPS; repeat at session end. Pass: linearity <= 0.5 % FS, drift <= 0.5 %. Log `zero_start` and `zero_end` rows. Record ambient T, pressure, RH every run.
1. **Incoming check** of each motor (`team/H1/templates/motor_incoming.csv`): mass (65 g listed), Rm, I0 and Kv at 10 V no prop. Run on the ESC with direction check props off (QP1-6).
2. **Thrust, current, power vs throttle, 4S.** MN2212 + T9545 (then 9045, then the C7 higher pitch prop): 0 to 100 % in steps 50, 65, 75, 85, 90, 100 (the maker rows) plus 10 % steps below, 3 s each, mean of last 2 s. Fresh pack 16.8 V rest (`condition=fresh`); V logged at the ESC; thrust, torque, rpm, V, I, can and ESC temperature per row. Rest >= 60 s after any step above 85 %.
3. **Prop derate.** measured / maker row (918 g at 100 %, 293 / 476 / 605 / 742 at the others) and 9045 vs 9545.
4. **Sag.** Repeat the 100 % step with the pack discharged to 20 % (3.73 V/cell rest) under the watt meter, `condition=sag`, 2 s. Until then the script estimates sag from fresh by T ~ V^2 x 0.97 and marks it EST.
5. **Saturation current.** 100 % for 2 s fresh: peak A against 13 A. Then a 180 s hold at 90 % (the `Q_M_SPIN_MAX` cap; sizing 10.8 A), `condition=hold`, `hold_s=180`, can temperature logged each 10 s, stop at 80 C or 13 A. The 13 A / 180 s maker rating is the limit; no burst rating exists (SIZING-A).
6. **rpm column.** rpm from ESC telemetry (if the FC reads it) and phone audio FFT blade-pass (2 blades, f = 2 n) at 50, 75, 100 %. Compute static CT = T / (rho n^2 D^4), D 9.5 in. The maker's 7350 rpm implies CT 0.148 (SIZING-A); a real 9x4.5 is 0.10-0.11.
7. **Yaw torque.** Torque cell reads Q on the 0.100 m arm at the throttle giving 326 gf (the hover thrust); sizing assumed Q 65 N mm (EST). The script rebuilds the yaw ratio as (0.201 + 1.2 Q) / 0.178; the 0.201 N m cant term and arm stay EST. **The stand cannot see the cant geometry**: the hanging yaw test (4 motors, ESCs, foam planform at 14-16 deg, BOARD M3 / C1) decides it and uses the 4 flight motors, so it follows the main motor order.
8. **R1.** Same steps 2, 4 and 5 for X2212 + 1045 on 4S, one CW motor: 100 % for <= 10 s (maker 25 A / 30 s), peak A, thrust; then the sag run. Abort at 25 A or 80 C.

Decision on fail: A fails a thrust line, resize once (R3: props or pack); second failure, B (BOARD R3). Nothing is waived.

## 3. Pass lines

| Line | Pass | Basis |
|---|---|---|
| Fresh thrust 100 %, MN2212 per motor | **>= 773 gf** (T/W 2.0 at the 1.50 kg gate: 2.0 x 1500 / (4 cos 14)) and **>= 854 gf** (R3, 0.93 x 918 g) | BOARD C5, R3 |
| Sag thrust 100 % at ~13.2 V | **>= 618 gf** (T/W 1.6 at 1.50 kg) | BOARD C5; at gate the sizing predicts 1.77 |
| Prop derate | measured / 918 g >= 0.93 | BOARD R3 |
| Hover point 326 gf | power <= 41.5 W (36.1 W +15 %, EST) | SIZING-A s3 |
| One-motor current, 100 % fresh | <= 13.0 A (sizing predicts 13.3, over); at 90 % <= 13.0 A (sizing 10.8); 180 s hold at 90 % <= 13 A, can <= 80 C | maker 13 A / 180 s; SIZING-A |
| rpm column | measured within 5 % of 7350 means the column is right; otherwise it is wrong and the CT band 0.08-0.125 (EST) tells whether thrust or rpm is the bad number; telemetry vs audio within 3 % | SIZING-A s3 |
| Yaw Q at 326 gf | **>= 55 N mm** (ratio >= 1.5 with cant term 0.201 N m); sizing EST 65 | SIZING-A s4, BOARD C1 |
| R1 motor (X2212 + 1045, 4S) | **>= 1100 gf** fresh, peak <= 25 A, price <= $25 ($15.99); sag >= 872 gf (EST). Pass is half of R1: B's re-priced margin at +30 % >= $150 is the other half and not a bench quantity | BOARD R1; score 79 for B |
| Rig | zero drift <= 0.5 %, can <= 80 C | H1 GT-01, QP-P19 |

Limits are derived, not new claims; `EST` ones are marked. `python -I bench_analysis.py LOG.csv` prints each as PASS / FAIL / NOT RUN and exits 1 on any FAIL. Selftest ran (19 pass, designed fails on rpm column and hover, so the FAIL path is exercised).

## 4. Caveats

- Maker rows are copied from the T-Motor page read today; the 85 % row (6000 rpm vs 5960 at 75 %) is also suspect, a second sign the rpm column is bad.
- 918 gf is 9 % of a 10 kg cell on an HX711: GT-01 noise step decides; if 2 sigma > 2 g, average 5 s per point and report U95 (TEST-PLAN-QP1).
- G12, G04 and the Nano are unread Amazon lines (503 today); verify links at order time.
