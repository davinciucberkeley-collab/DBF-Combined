# QP-4 design review board (J6), concept A pre-order re-sit, 2026-11-15

Board: aero / flight control, structures, electrical / propulsion, build-test-schedule critics; J6 chair decides.
Inputs: `review/QP-3/BOARD.md` (verdict, D-185 / D-186, s7.1, s7.2, G1-G9); `review/QP-4/{FOLDIN,FLUTTER,STRUCTURES-R,SERVO,ASDRAWN,FIXES}.md`; `qp/A/{ORDER-1.csv,A.param}`, `qp/A/structures/{flutter_a.py,fixes_run.py,fixes_run.md}`, `qp/A/cad/a_model.py` (`BAL_*`); A1's open-items list (scratch, 2026-11-15). Board checks run today: (a) a fine hinge-stiffness sweep of the selected D-187 v2 elevon with `flutter_a.py` unchanged, same inputs as `fixes_run.py` case B (script in the J6 scratch folder, not in the repo; K 0.5-3.0 in 0.1 steps, nom and kd corners, g_s 0 / 0.01 / 0.02); (b) `ORDER-1.csv` re-summed in `python`; (c) the Owens Corning FOAMULAR 150 data sheet (https://www2.owenscorning.com/comminsul/documents/foamular150.pdf, search result read 2026-11-15: compressive strength min 15.0 psi, ASTM D1621; no density given).
Labels: `V` vendor / maker page, `CALC` computed from repo numbers, `EST` estimate, `—` unknown. Nothing bought, built or flown. No other file edited; no git.

## Verdict

**Order 1 (bench kit, 1-4 Dec): YES.** Three of the four s7.1 conditions are met; the fourth (T-Motor lead time) is still unasked, but its default is fixed: no answer by 4 Dec means buy all 5 motors ($1,123.02). The board adds one recommended change: put the three ES3054HV servos in Order 1 (+$46.27) so the elevon test can run before the main order.
**Main order: NOT YET.** G7 is met and G5 / G6 are met on the model. G1-G4 wait on the bench. **G8 is open again.** The selected elevon balance has a flutter dip that is deeper and wider than FIXES reports: undamped speeds fall to **4-12 m/s at K 1.3-1.5 N m/rad** (nom), so the design depends on hinge damping and free play that nobody has measured. The lens caps that cover the lead are not in the CAD, so the collision PASS does not yet meet the "no interpenetration" constraint.

| KPI | Value | Status | Source |
|---|---|---|---|
| Predicted mass / target / gate | 1,406.7 g / 1,440 / 1,500 | met, if >= 11.8 g of the 41.6 g `EST` cuts are real (s1) | FIXES s3.2; `CALC` s1 |
| Structure, CAD with balance and cuts / ruled ceiling | 468.7 g / **494 g** | met on CAD, not weighed | FIXES s3.4 group sum `CALC` |
| CG, CAD / band | 22.5 mm (trim 20.4-24.7) / 20-26 | met | FIXES s3 |
| Elevon flutter, worst undamped (nom / kd) | **4 m/s at K 1.5 / 5 m/s at K 1.2** vs 28.8 | **open** (G8) | board sweep (s2.2) |
| Roll rate, SITL as drawn | 92.9 / 94.1 deg/s vs 90 | met (+3-5 %, `EST` aero) | FIXES s2 |
| BOM total / +30 % margin | $1,762.96 / +$120.85 | met (G7) | FIXES s6 |
| Order 1, 2 / 5 motors | $967.90 / $1,123.02 (re-summed, matches) | YES | `ORDER-1.csv` `CALC` |

## 1. Structure mass: 494 g against the 473 g freeze

**Ruling: waiver granted. The structure line becomes a ceiling of 494 g, weighed. The binding line stays the predicted total <= 1,440 g, and the 41.6 g of cuts count only once they are weighed.** The +21 g (now +34.2 g for the pair with caps) is a flutter fix the board asked for (QP-3 s5), not spec creep, so it does not trigger a re-sit.

Breakdown (FIXES s3.4): wing 208 (incl. balance 34.2) + fins 109 + feet 8.4 + hardware 30 + cage 113.3 = **468.7 g** `CALC` with the cuts, about 506 g without them. The CAD is therefore 25 g under the ceiling, but only because of `EST` cuts.

**Which cuts are load-bearing.** The predicted total is 1,406.7 + (41.6 - X) x 1.1174, where X is the grams of cut that turn out real (FIXES s3.2 method). It stays <= 1,440 only if **X >= 11.8 g** `CALC`. With no cuts at all it is 1,453 g, and the +-5 % transition window (needs <= 1.441 kg, MASS-GATE) fails.

| Cut | g | Credible? | Board view |
|---|---|---|---|
| Foam 30 -> 25 kg/m3 (core, elevons, fin fairings) | 16.6 | plausible. ASTM C578 Type X minimum is 20.8 kg/m3 (FIXES, OneClickLCA); the OC data sheet read today gives no density | **weigh** a FOAMULAR 150 sample (known volume, 0.1 g scale) before the foam is bought. This item alone covers the 11.8 g |
| Printed parts (tray, plate, cups, hub, roots, shoes, plugs) | 18.0 | believable that they get lighter; every mass is a guess. Thinner cups not re-checked for the 30 N prop strike | print and weigh at Jacobs with the Order-1 PETG ($0); C1 re-checks the prop strike |
| Hardware lump, paint removed | 7.0 | weakest: the 15 g for 43 epoxy joints is `EST` | weigh a cured epoxy joint sample; until then credit 0 |

**Also not credited:** the iteration-2 foam-bearing checks used 120 kPa. FOAMULAR 150 is rated **15 psi = 103 kPa minimum** (OC data sheet above) at any density, so C1 re-runs those checks at <= 100 kPa, as FIXES s3.1 already asks. Also weigh: the lead strip (15.6 g `CALC`) and one ES3054HV (the vendor page gives 17 g and 20.5 g; the CAD uses 20.5).

## 2. D-187 elevon balance as fixed

### 2.1 Fit: lead poke under caps that are not drawn
**Ruling: not accepted as a 3-D pass.** `collide_a.py` reports 0 at +-20 deg only because the lens caps do not exist in the model. The lead pokes 1.4 mm beyond the outer skin (FIXES s1.2), and FIXES gives the caps 1.8 mm overall height `EST`. With a printed wall of about 0.8 mm `EST`, the inside height is 1.0 mm, **under the 1.4 mm poke**. Required cap height is >= 1.4 + 0.5 clearance + wall = **about 2.7 mm** `EST`.

Second gap: the +-20 deg stop exists only in software (SERVO5/6 MIN/MAX, not yet calibrated). The ES3054HV's mechanical throw is larger, and the arm is <= the horn, so a mis-set endpoint or a servo test at full PWM drives the lead into the cap or the end of the pocket and **jams the elevon**.

Required before the main order ($0, CAD owner):
1. Draw both caps per elevon with their real wall and >= 0.5 mm clearance.
2. Either draw a mechanical elevon stop at +-20 deg outside the lead's path, or size the pocket and caps for the servo's full throw through the drawn linkage.
3. Re-run `build_a.py`, `collide_a.py` (at the stop **and** at +-22 deg, which allows for calibration error) and `a_assembly.py`.
4. Add the cap drag (`EST` 1-2 % of cruise drag, FIXES) to the MISSION power line.

### 2.2 Flutter dip at K about 1
**Ruling: the dip is worse than FIXES reports. "Removed by 2 % damping" is true in the model but rests on an unmeasured number.** Board sweep, D-187 v2 as selected (speeds in m/s, G8 line 28.8):

| Corner | g_s | K 0.5 | 0.9 | 1.0 | 1.1 | 1.2 | 1.3 | 1.4 | 1.5 | 1.6 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nom (f_h 12.2, f_a 45.1 Hz) | 0 | 32 | 24 | 22 | 19 | 16 | **12** | **8** | **4** | 48 | 50 | 52 |
| nom | 0.01 | 35 | 28 | 27 | 26 | 26 | 47 | 48 | 49 | 49 | 51 | 53 |
| nom | 0.02 | 37 | 35 | 46 | 47 | 48 | 49 | 49 | 50 | 50 | 52 | 53 |
| kd (f_h 10.5, f_a 41.2 Hz) | 0 | 28 | 18 | 15 | **10** | **5** | 44 | — | 45 | 46 | 47 | 48 |
| kd | 0.01 | 30 | 24 | 24 | 44 | 44 | 45 | — | 46 | 46 | 47 | 49 |
| kd | 0.02 | 33 | 43 | 44 | 45 | 45 | 46 | — | 47 | 47 | 48 | 49 |

(">100" outputs at kd K 1.4 and nom K 1.9 are mode-tracking artefacts near coalescence and are shown as "—" / ignored.) What the sweep shows:
- FIXES' 8-point grid jumped from K 1 (22 m/s) to K 2 (50 m/s) and missed the bottom of the dip. Undamped, the selected elevon is **unstable at cruise speed for K 1.1-1.5**. The upper edge of the dip is K 1.6 (nom) / 1.3 (kd), so the proposed K >= 2 acceptance has only 1.25x margin over that edge at nom.
- At g_s 0.01 it still fails (24-28 m/s, K 0.9-1.2). At g_s 0.02 every K passes (min 31-35 m/s). **The design needs g_s >= 0.02 (about 1 % critical) or no free play.**
- **Free play makes K irrelevant.** Inside the free-play band the effective stiffness is about 0. As the amplitude grows it rises toward the measured K, so it must pass through the 1.1-1.5 window. With 1 deg of free play the describing function puts that window at about 1.7x the half-gap, roughly +-0.9 deg `CALC`. The expected result, unless the joint has damping, is a bounded elevon buzz near 45 Hz at cruise, not a divergence. That still fatigues the lead bond and the tape hinge and puts vibration at the IMU.

### 2.3 The K >= 2 test
**Ruling: necessary, not sufficient. Replaced by the elevon coupon test E1, run before the main order** (not just "before gluing"). The result can change the linkage, the balance or the elevon, all of which are main-order items. E1 uses a 300 mm wing-section coupon (FLUTTER torsion coupon) carrying a real elevon, lead strip, tabs, ES3054HV at 7.2 V and the drawn linkage:
1. **Static K** with a spring scale (FLUTTER step 5): >= 2 N m/rad.
2. **Free play** <= 0.5 deg total (0.26 mm at a 30 mm arm) with the servo powered.
3. **Damping**: pluck the elevon trailing edge with the servo holding, read the ring-down with a phone accelerometer or slow-motion video. Requires zeta >= 1 % (g_s >= 0.02).
4. **Lead-bond** pull test on the tabs to 3x the n 3.4 inertial load (STRUCTURES-R lead 0.36 N, so >= 1.1 N).

**Fail action:** add a preload (a spring or elastic band on the horn) to remove free play and re-test. If that fails, use the heavier 17.0 g strip; the sweep in FIXES shows it does not remove the dip, so the preload is the real fix. Owner (C1 / C2) re-runs `fixes_run.py` on the repo with this fine K grid and fixes the tracker artefacts.

## 3. Servo ES3054HV at 7.2 V; elevon to y 0.35

**Servo: accepted.** Required torque is 1.5 x 0.151 = 0.226 N m. The ES3054HV gives 0.397 N m at 7.2 V (`EST`, interpolated from the `V` 6.0 / 8.4 V figures), a factor of 1.76. **At 6.0 V it gives 0.333 N m, a factor of 1.47, which fails 1.5**, so the 7.2 V jumper is a requirement, not an option.

Conditions:
- Rail jumper set to 7.2 V and measured under load on the bench.
- Stall current measured (`—` on the page) against the 3 A continuous / 4.8 A peak BEC (A-P18).
- Servo arm no longer than the horn.
- Mass weighed (s1).

The hinge-moment basis (Ch_delta 0.94 /rad) is conservative (SERVO s1). If E1 adds a preload spring, its torque adds to the required 0.226 N m and must be checked.

**Elevon y 0.35: accepted.** Roll rate is 92.9 / 94.1 deg/s against 90 (FIXES s2). The surface is still at its 20.0 deg stop at the peak, so the 3-5 % margin is smaller than the `EST` aero error. Measure the roll rate on the first cruise (M8 extended). The tip is 22 mm from the fin and the collision gate passes. Reversal is unchanged and still marginal on the 2-D bound (28 m/s). The added 0.26 g per elevon is in the flutter run.

**Pitch-use basis (ASDRAWN s3), ruled:** G5 uses the hardware stop. Peak transition elevon <= 0.60 x 20 deg = 12 deg; measured 8.9-9.6 deg, so it passes. The old 15 deg basis is withdrawn.

## 4. Q_WVANE back to 0; heading by pilot yaw

**Ruling: accepted.** The vane failed its own condition: 15.4-23.7 deg against 15 at gain 1 (ASDRAWN s2.5). Effects:
- **C2** reverts from "automated by `Q_WVANE` 3" to **open: met in SITL by the pilot-yaw rule, open in the field**. The heading rule is again a card item and pilot workload.
- **G3** keeps its numbers (>= 0.35 N m go; 0.30-0.35 go with the 4 m/s card; < 0.30 R2). It now carries more weight: with no vane, the heading in hover and during the yaw to edge-on before landing comes only from yaw authority. **M9 is re-stated** as a tethered hover with heading hold, vane off: an excursion > 15 deg in turbulence imposes the 4 m/s card.
- **Flight card, mandatory (new):** back-transition into the wind (D-186); then, **above 3 m/s, yaw edge-on before QLAND**.
  - Belly-into-wind is prohibited above 3 m/s. In that case the SITL lean at touch is 29.1 deg (FIXES s5.2), against a static tip-over of 32.7-33.2 deg (QP-3 s2), a 3.6 deg margin.
  - Edge-on (wind from 90) gives 9.9 deg at touch but touches the 0.90 cap momentarily. It is accepted with the cap time logged (< 1 s).
- `Q_WVANE_GAIN` 1 and `SPD_MAX` 2 stay in A.param, so a later retest (gain 0.3-0.5, longer filter) only needs ENABLE 3. That retest is not on the critical path.
- REQUIREMENTS A-P8a and MISSION s3 still say "3, conditional" (FOLDIN s1). A1 folds in 0.

## 5. G1-G9 after QP-4

| # | Line | Status | Evidence / what closes it |
|---|---|---|---|
| G1 | T/W sag >= 1.6 at 1.50 kg; capped window >= +-5 % at 1.44 kg | **bench (Order 1)** | model +-8.0 % at 1.40 kg, +-4.5 % at 1.50 (FIXES s3.2, s5.1); M1 |
| G2 | one motor at 90 % <= 13 A, can <= 80 C | **bench** | M2 |
| G3 | yaw >= 0.35 N m | **bench**; heavier now (s4) | M3 |
| G4 | hover <= 57.2 W per motor at 402 gf | **bench** | M1 |
| G5 | as-drawn SITL lines + roll >= 90 deg/s | **met (SITL)** | FIXES s2, s5: pitch use 0.44-0.47 of the stop; 0 s at the cap in transition; 1.3 Vs in 7.1-7.5 s; roll 92.9-94.1; fence 34-57 m margin (ASDRAWN s2.6). The vane line is withdrawn (s4); back-transition cross-wind cap is momentary (flagged) |
| G6 | CG 20-26; predicted <= 1.44 kg; structure <= 494 g (ruled s1) | **met on CAD, needs the weigh-in** | 22.5 mm; 1,406.7 g; 468.7 g; needs >= 11.8 g of the cuts weighed |
| G7 | +30 % margin >= $100, total <= $1,800 | **met** | $1,762.96 / +$120.85 (FIXES s6); +$46.27 servo pull-forward moves spend, not the total |
| G8 | flutter / divergence >= 1.2 VD | wing, divergence, reversal (3-D) **met**; **elevon open** | s2.2; closes with E1 (s2.3) |
| G9 | written >= 4 mornings/wk booking plan; main order by 28 Dec | **open** | no plan in QP-4 |

**Added line G10:** a 3-D gate that includes the caps and the stops passes (s2.1). Fail action: no wing cut.

## 6. Chair's decision

### 6.1 Order 1: YES. The s7.1 conditions, checked against FOLDIN

| # | Condition | Status |
|---|---|---|
| 1 | BOM on iteration 2 + bench lines, +30 % margin >= $100 | **met**: $1,762.96 / +$120.85 after the lead line R11 (FIXES s6; FOLDIN $126.36, SERVO $135.18) |
| 2 | GPS connector; bidirectional DShot | **met by ruling**: the Kakute has UART pads, not a GPS plug, so the M10Q is **soldered** ($0, 30 min). Which UART ArduPilot maps to GPS is `—`; find it in the board's hwdef before first power-up, which does not block the order. DShot: the throttle notch is accepted (A.param `INS_HNTCH_MODE` 1, `SERVO_BLH_BDMASK` 0); M4 stays |
| 3 | T-Motor stock / lead time | **not met: still unasked.** A team member must send the enquiry (FOLDIN s4 gives the details). No answer by **4 Dec** means Order 1 buys all 5 MN2212: **$1,123.02**. The order does not wait for the answer |
| 4 | Order 1 limited to bench, neutral and stock-risk lines | **met**: 24 lines; goods $827.91 + tax $84.86 + shipping `EST` $55.13 = **$967.90** (re-summed, matches); +$155.12 for 3 motors. Seven lines (B03, B04, G02 x2, G03, G04, W06; $123.95) are `EST` |

**Recommended addition:** M01 ES3054HV x 3 ($13.99 `V`, RMRC, same shipment) = **+$46.27** `CALC` (3 x 13.99 x 1.1025). This lets E1 run in December. Order 1 becomes $1,014.17 / $1,169.29. It is a line moved earlier from the main order and does not add to the total. Lead for the coupon: local, `EST` (R11 is `EST` $10, price not looked up).

### 6.2 What remains before the main order (latest-safe 28 Dec)

| # | Work | Closes | Owner | Cost | Due |
|---|---|---|---|---|---|
| 1 | Bench M1-M4 | G1-G4 | H1 / E1 | Order 1 | 17 Dec |
| 2 | Caps drawn with real wall and clearance; mechanical stop or full-throw pocket; gates re-run at +-20 and +-22 deg; cap drag into MISSION | G10, s2.1 | CAD (A5) | $0 | 11 Dec |
| 3 | Elevon coupon E1: K >= 2, free play <= 0.5 deg, zeta >= 1 %, lead-bond pull; fine-K flutter re-run in the repo | G8 | C1 / C2 | ~$5 foam + lead `EST` (servos from Order 1) | 18 Dec |
| 4 | Weigh-in: foam density, printed cups / hub / plate / plugs, lead strip, servo, epoxy sample; >= 11.8 g of cuts real | G6 | A3 | $0 | 18 Dec |
| 5 | C1 re-checks: foam bearing at <= 100 kPa (rated 103), 30 N prop strike on the 1.0 mm cups, tray / pack landing load on the LE slot floor | structures | C1 | $0 | 18 Dec |
| 6 | One-truth: MASS-GATE.md (still QP-3 values, FIXES s6), A-P8a / MISSION s3 to `Q_WVANE` 0, flight card (s4), pitch-use basis (s3), 7.2 V build note, GPS UART | C6 | A1 | $0 | 11 Dec |
| 7 | Written booking plan, >= 4 RFS mornings/wk from 8 Feb | G9 | I2 / team | $0 | 18 Dec |
| 8 | T-Motor enquiry sent (a team member) | s6.1 #3 | user | $0 | now |

### Conditions C1-C8, status changes since QP-3
C2 back to **open in the field** (s4). C4 met (CG 22.5 mm, SM about 7.4 % on NP 40.7 `EST`). C5 met on CAD (1,406.7 g), weigh-in pending. C6 **not met** (row 6). C1, C3, C7 and C8 unchanged.

## 7. What the team must measure (new or changed)

- **M3** Hanging yaw (unchanged). Below 0.30 N m fires R2. It now also sets the landing wind limit, because there is no vane.
- **M9** (re-stated) Tethered hover, heading hold, vane off, light turbulence. Excursion > 15 deg imposes the 4 m/s card.
- **M10** Elevon coupon E1 (s2.3): K < 2 N m/rad, free play > 0.5 deg or zeta < 1 % fails G8. A preload fix comes first.
- **M11** Foam density on a known-volume FOAMULAR 150 block, 0.1 g scale. Above about 27 kg/m3 the foam row loses most of its 16.6 g, and G6 then depends on the printed-part cuts (s1).
- **M12** Kakute servo rail voltage under two-servo load at 7.2 V. Below 6.0 V the servo fails the 1.5x factor (s3).
- **M13** Servo endpoint calibration: elevon at +-20.0 deg (protractor) before the lead is installed. Any overtravel past the drawn stop fails G10.

## Open decision cards

**D-J6-5 Pull the servos into Order 1?** Facts: E1 decides G8, which is a main-order line, and E1 needs the flight servo. Recommended: add M01 x 3 (+$46.27, no change to the total). Alternative: run E1 with a borrowed metal-gear servo. Its K and free play would not represent the ES3054HV, so it does not close G8. Evidence s2.3, s6.1.

**D-J6-6 Preload the elevon linkage by default?** Facts: with any free play the elevon passes through the flutter dip on the way to its full stiffness (s2.2); the model's 2 % damping is unmeasured. Recommended: design in a light preload spring on each horn now (about 0 g, $0 `EST`) and keep the 15.6 g strip. Alternative: rely on E1's damping result alone. Evidence s2.2.
