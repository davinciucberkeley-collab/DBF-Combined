# QP-1 sizing: candidate T (K06 scaled down), scratch tilt-tricopter

Date 2026-11-14. Sizing group T. Scripts: `redesign/qp/sizing_T/sizing_T.py` (mass, aero, hover, mission) and `redesign/qp/sizing_T/cost_T.py` (cost). Run with `python -I`.
Basis: `redesign/config-study/cards/K06/` (CARD, REVIEW, cost.csv, sizing.py), `redesign/config-study/RESTUDY-2026-11-14.md` (floor $744.02, cost rules), mission from `redesign/review/CLOSURE-ROUND-2026-11-14/A2.md` §2.1 (cruise 3.5 min, hover-mode 3.0 min incl. a 40 s go-around, reserve 20 % of nameplate, usable 0.90 as in RESTUDY).
Tags: `V` vendor page read 2026-11-14; `U` unverified (search snippet or earlier card); `EST` estimate; `—` unknown.

## Verdict

T at 1.75 kg build (1.85 kg with a 0.10 kg growth allowance) passes hover thrust (T/W 2.72 fresh, 2.44 sag), cost (all-in $1,605, margin $395) and the box. The thrust table is a published maker table. It is **marginal** on pack energy (+6 %), on ArduPilot tuning evidence for a scratch tri, and on schedule. It **fails** on motor-out: any one of three motors lost ends the flight. The 45 g overshoot of the 1.8 kg band is the growth allowance; the build-up itself is 1.745 kg.

## 1. Mass, wing, fit

Layout: flying wing, span 1.20 m, root 0.30 m, tip 0.19 m, LE sweep 20°, S = 0.294 m², AR 4.90, MAC 0.249 m, pod + CF boom, two tip fins, elevons. Same architecture as K06 (card) at 0.92 of its span.

| Group | g | Contents (items in `sizing_T.py`) |
|---|---|---|
| Propulsion | 406 | 3 motors 237, 3 props 69, 3 ESC 20, wiring 80 `EST` |
| Tilt | 246 | 2 servos 126 (63 g each, K06 card), 2 nacelles 120 (60 g each; K06 REVIEW C2 gives 65) `EST` |
| Wing | 381 | XPS 164 (calc, 33 kg/m³ `EST`), tape skin 57 (75 g/m², K06 REVIEW C3), spar sockets 57, joiner 29 (calc), elevon servos 34, fins 40 `EST` |
| Body | 293 | pod 125, boom 38 (calc), rear mount 15, skids 30, fasteners 35, tray / extensions / GPS mast 50 `EST` |
| Avionics | 68 | FC 30, GPS 12, RX 4, airspeed 15, Remote ID 7 `EST` |
| Non-battery | 1,394 | |
| + 10 % contingency | 139 | |
| Pack, CNHL 4S 2200 mAh 40C | 211 | listing weight, see §6 |
| **Build mass** | **1,745** | |
| + growth allowance | 100 | `EST`, scaled down from K06's 250 g |
| **MTOW used** | **1,845** | |

Wing, speeds (CLmax 0.85 `EST`, K06 card; CD0 0.040, e 0.8 `EST`, K06 card):

| Mass | Wing loading | Stall | 1.3 Vs | Cruise | L/D | Cruise power |
|---|---|---|---|---|---|---|
| 1,745 g | 5.9 kg/m² | 10.6 m/s | 13.7 m/s | 16 m/s | 7.3 | 92 W, 6.2 A |
| 1,845 g | 6.3 kg/m² | 10.9 m/s | 14.1 m/s | 16 m/s | 7.5 | 94 W, 6.3 A |
| 1,945 g | 6.6 kg/m² | 11.2 m/s | 14.5 m/s | 16 m/s | 7.7 | 96 W, 6.5 A |

Cruise prop check (`EST`): 11 x 5.5 needs about 6,900 rpm for zero thrust at 16 m/s (pitch 0.140 m), and about 8,000 rpm gives J 0.43. KV 880 x 14.8 V x 0.85 gives about 11,000 rpm available. Thrust needed is 1.2 N per front motor.

**Car-box fit (PASS).** Box 1.25 x 0.55 x 0.45 m. The assembled aircraft is 1.20 m across and about 0.65 m long (nacelle front to rear motor), so it does not lie in the box whole (0.65 m > 0.55 m). It travels as: two wing halves (0.60 span x about 0.38 m with nacelle x 0.12 m, props off), pod + boom (about 0.80 m x 0.11 m), packs in the ammo can. All fit with margin of at least 0.4 m on the long axis. Field joints: 2 wing joiner joints, 2 tilt-servo plugs, 1 power plug per half, 3 props `EST`.

## 2. Rotors, motors, props, servos

**Layout.** 2 front tilt rotors, 1 rear fixed. Front motors 0.20 m ahead of CG, 0.24 m off the centreline; rear motor 0.40 m aft of CG, so thrust shares are equal (arm ratio 2:1). Prop gap between the front discs is 0.20 m; rear disc clears the wing trailing edge by about 0.08 m (geometry, `sizing_T.py`). The rear motor stops in cruise (as K06). I considered a rear-tilt layout and rejected it: a rear tilt servo adds mass and failure points, and ArduPilot vectored yaw only uses the left/right tilt servos (docs below).

**Motor.** T-Motor AT2317 KV880, 79 g, $39.99, peak 25 A / 350 W (180 s) (https://store.tmotor.com/product/at2317-long-shaft-fixed-wing-motor.html, `V` 2026-11-14). I tried SunnySky X2216 and X2814 first; no 4S thrust table was found for either. The AT2814 KV900 (108 g, $49.99, table on the same T-Motor site) also gives a table but is 29 g heavier for thrust we do not need.

Published table, AT2317 KV880 + APC 11 x 5.5, 4S bench supply (V 14.2 to 14.7):

| Throttle | A | W | Thrust g | rpm |
|---|---|---|---|---|
| 40 % | 4.82 | 70.6 | 592 | 5,297 |
| 50 % | 6.60 | 96.6 | 743 | 5,950 |
| 60 % | 8.94 | 130.3 | 928 | 6,585 |
| 70 % | 12.43 | 180.2 | 1,161 | 7,317 |
| 80 % | 16.69 | 240.2 | 1,402 | 8,021 |
| 100 % | 23.36 | 332.1 | 1,670 | 8,750 |

**ESC.** LANRC 45 A BLHeli_S 4-pack, $30 `U` (K06 cost.csv, 2026-11-01). Motor draws 23.4 A at 100 %, so the 45 A part has 1.9x headroom.

**Prop.** APC 11 x 5.5E, $4.17, 0.81 oz (23 g) (https://www.apcprop.com/product/11x5-5e/, `V` 2026-11-14). **Open issue:** the page lists no pusher or reverse-rotation version of the 11 x 5.5, and the counter-rotating front pair needs one. Options: an opposite-handed 11-inch prop of similar pitch (APC 11 x 4.7 SF / SFP pair, table not checked), or reversing ESC direction with a mirror prop. Not resolved here.

**Hover loading (sizing_T.py, table interpolation x 1.10 install x 1.10 control margin).** At 1,845 g each motor carries 615 g, about 42 % throttle:

| Mass | Per motor | Hover power | Hover current | T/W fresh (3 x 1,670 g) | T/W sag (x 0.90 `EST`) |
|---|---|---|---|---|---|
| 1,745 g | 582 g | 250 W | 15.5 A | 2.87 | 2.58 |
| 1,845 g | 615 g | 270 W | 16.8 A | 2.72 | 2.44 |
| 1,945 g | 648 g | 291 W | 18.0 A | 2.58 | 2.32 |

Gate: T/W >= 2.0 fresh and >= 1.6 sag: **PASS**. T/W 2.0 fresh would be reached at about 2.5 kg. The rear motor shares: a 20 mm CG shift forward moves the rear motor from 615 g to 553 g and the fronts to 646 g, well inside the table.

**Tilt servo and mechanism.** Powerhobby 329TG, 63 g, 24 kg-cm listed (2.35 N m), $27.95 `U` (K06 cost.csv, 2026-11-09). The nacelle pivots on a 6 mm steel shaft in two flanged bearings with a horn link; the pivot is on the thrust line (K06 card). Loads:

| Load | N m | Basis |
|---|---|---|
| Gyro of the tilting prop at 90 deg/s | 0.036 | prop inertia 3.5e-5 kg m² `EST` x 660 rad/s x 1.57 rad/s |
| Pivot offset 10 mm x 6 N thrust | 0.06 | offset `EST` |
| Allowance incl. aero and inertia | about 0.15 | `EST` |
| Servo stall | 2.35 | listing `U` |

Margin about 15x. The servo is oversized; a 10 to 12 kg-cm metal-gear servo (about 40 to 55 g) would save about 15 to 45 g, but I did not price one. Kept at the K06 part for a known price.

## 3. Yaw control and wind

Vectored yaw: differential tilt of the front rotors (`Q_TILT_TYPE 2`). Yaw moment = 2 T sin(theta) y with T = 6.0 N per front motor at 615 g and y = 0.24 m:

| Differential tilt | Yaw moment, N m |
|---|---|
| +/-10 deg | 0.50 |
| +/-15 deg | 0.75 |
| +/-20 deg | 0.99 |

Demand: the rear prop reaction torque at hover is 0.090 N m (table torque scaled to 615 g), which is a constant trim the tilt must hold. A 5 m/s steady wind on fins and boom gives about 0.11 N m (0.5 rho V² x 0.024 m² fin area x 0.30 m arm, Cn 1.0, `EST`). Total demand about 0.20 N m against 0.75 N m at +/-15 deg: **3.7x authority** (PASS, `EST`). Yaw acceleration at +/-15 deg is about 12 rad/s² on Izz 0.060 kg m² (`EST`). A 5 m/s side wind needs about 3.4 deg of bank (side area 0.07 m² `EST`, K06 card). Caveat: authority is limited by servo rate and the tilt angle past vertical (`Q_TILT_YAW_ANGLE`); the Convergence builder used 10 deg (see §4), which gives 0.50 N m, still 2.5x.

## 4. ArduPilot

Official page (https://ardupilot.org/plane/docs/guide-tilt-rotor.html, read 2026-11-14):
- Frame class 7 is Tricopter; `Q_FRAME_TYPE` is ignored for Tri.
- `Q_TILT_TYPE` 0 continuous, 1 binary, 2 vectored, 3 bicopter. Vectored yaw needs `Q_TILT_TYPE 2` and `Q_TILT_YAW_ANGLE` (degrees past vertical). Front-two tilt is `Q_TILT_MASK 3`.
- Vectored: left and right front servos use `SERVOn_FUNCTION` 75 and 76; no rear yaw servo needed. Non-vectored tri: tilt servos 41 and a yaw servo 39 with `Q_M_YAW_SV_ANGLE`.
- `Q_TILT_RATE_UP/DN` (start about 15 deg/s), `Q_TILT_MAX` (default 45), `Q_TILT_FIX_GAIN/ANGLE` (fixed-wing tilt stabilisation, start 0.1).
- The page does not cover tilt-servo failure or motor-out. I found no ArduPilot doc that covers either for a tricopter.

Community evidence (forum threads, titles and snippets only unless noted; none is a documented scratch-built tilt-tri with logs):
- Vectored yaw added and tested on an E-flite Convergence, `Q_TILT_YAW_ANGLE` 10: https://discuss.ardupilot.org/t/tiltrotor-support-for-plane/8805/278 (read via search snippet 2026-11-14).
- Convergence on Matek F405 Wing, many pages of logs: https://discuss.ardupilot.org/t/e-flite-convergence-using-matek-f405-wing/35810
- Nimbus tricopter VTOL, very long thread: https://discuss.ardupilot.org/t/nimbus-tricopter-vtol/31042 (title only, not read)
- Tilt-tri Y3 issues: https://discuss.ardupilot.org/t/tilt-tricopter-y3-vtol-issues-pixhawk-acting-crazy/67257 (title only)
- Flightory Stallion tilt-tri, 1.34 m span, AUW 2 to 3 kg, retailer data (K06 REVIEW C5, 2026-11-09, not re-checked): https://www.air-rc.com/aircraft/Flightory_Stallion-VTOL_stallion
- SpeedyBee F405 Wing as an ArduPilot target: RESTUDY lists it `U`; not re-checked.

Known failure modes (what each thread says, read 2026-11-14 unless noted):
1. Wrong `Q_TILT_MASK` or left/right servo function swapped led to a transition crash: https://discuss.ardupilot.org/t/crashed-vtol-fw-maiden-qrtl-quirks/106915 (search snippet only). Mitigation: bench check of each servo against the mask, MANUAL <-> QSTABILIZE tilt test on the ground (official page advice).
2. Yaw "yo-yo" of about +/-30 deg in hover on a Convergence, suggested fix yaw feedforward / tuning: https://discuss.ardupilot.org/t/yaw-yo-yo-with-vtol-tilt-rotor-convergence-help-with-log-analysis-please/42856 (snippet).
3. Yaw spin in transition on a 4-motor tilt-quad, ArduPlane 4.6.3, X mixing; fixed by H mixing (Q_FRAME_TYPE 3), cause unconfirmed, reported 2026-07-05: https://discuss.ardupilot.org/t/yaw-spin-during-vtol-transition/144467 (read). Not directly a tri issue, but shows transition yaw behaviour is firmware-version sensitive.
4. Tilt asymmetry and tilt-tri oscillation and high-wind retune crashes: https://discuss.ardupilot.org/t/oscillation-crash-and-high-wind-problems-when-retuning-vtol-trimotor-plane-with-front-tilt/143035 and https://discuss.ardupilot.org/t/vtol-tricopter-tilt-motor-unstable-pitch-increase-at-high-throttle-in-multicopter-mode-looping/142017 (titles only).
5. Tilt tied to throttle in QLOITER with vectored yaw, fixed by `SCHED_LOOP_RATE` 50 to 300: https://discuss.ardupilot.org/t/q-loiter-and-vectored-yaw-problem/35707 (read, 2018, ArduPlane 3.9.3).
6. K06 card: pitch trim shifts as the rear motor spools down, and the nose rears up in the forward transition (`UNVERIFIED`).

Parameters to start from (K06 card, `UNVERIFIED`, cross-checked against the official page above): `Q_ENABLE 1`, `Q_FRAME_CLASS 7`, `Q_TILT_ENABLE 1`, `Q_TILT_TYPE 2`, `Q_TILT_MASK 3`, `Q_TILT_YAW_ANGLE` 10 to 15, servos 75/76 for tilt and 77/78 for elevons, `Q_ASSIST_SPEED` about `AIRSPEED_MIN` minus 3.

## 5. Failure consequences

| Failure | Consequence | Basis |
|---|---|---|
| Rear motor or ESC out, hover | Pitch-up and loss of 1/3 of lift; front motors cannot balance (arm ratio 1:2). Crash. | moment balance; no ArduPilot tri thrust-loss handling found |
| Front motor out, hover | Roll flip; crash | same |
| Any motor out, cruise | Lose one front: asymmetric thrust, glidable on elevons; lose rear: no effect (it is stopped). Back-transition then impossible after a front loss: belly landing in fixed-wing | `EST` |
| One tilt servo stuck vertical, hover | Yaw authority halves (about 0.38 N m, still above 0.20 N m demand); flight continues, no transition possible | calc |
| One tilt servo stuck forward or dead in hover | The nacelle thrust goes horizontal: crash | geometry |
| One servo stuck mid-angle in cruise | Asymmetric thrust and drag; fixed-wing landing possible only if it holds; belly landing on foam at about 14 m/s | `EST` |
| Tilt servo stripped gears or overheats | Same as dead. 200-cycle bench test at 800 g thrust (K06 first prototype test) is the screen | K06 card |

Motor-out is the same single-point failure as K06 card risk 1. I did not check how A or B behave in motor-out.

## 6. Pack, CG, static margin

Mission (sizing_T.py, `EST`): 180 s hover mode at 1.05 x hover power (climb allowance), 210 s cruise at 16 m/s (3.5 min), two transitions of 12 s at 1.30 x hover power. Pack need = mission Wh / (0.8 x 0.9), the RESTUDY convention.

| Mass | Hover | Cruise | Transitions | Mission Wh | Pack need Wh | Pack Wh | Cruise to reserve line, min | Hover-only, min |
|---|---|---|---|---|---|---|---|---|
| 1,745 g | 13.1 | 5.3 | 2.2 | 20.6 | 28.6 | 32.6 | 5.4 | 5.6 |
| 1,845 g | 14.2 | 5.5 | 2.3 | 22.0 | 30.6 | 32.6 | 4.4 | 5.2 |
| 1,945 g | 15.3 | 5.6 | 2.5 | 23.4 | 32.5 | 32.6 | 3.5 | 4.8 |

Pack: CNHL Black Series 4S 2200 mAh 40C XT60, about 211 g, $17.99, 32.6 Wh (chinahobbyline.com search snippet 2026-11-14, `U`: https://chinahobbyline.com/products/cnhl-black-2200mah-4s-shorty-lipo-battery-xt60). Hover draw 16.8 A is 7.6 C; all-out 70 A is 32 C, both inside the 40C rating, but a cheap 40C pack sags more than the 100C CNHL 2000 mAh (232 g, $40.49 GetFPV snippet; I could not read that page, HTTP 403). The sag thrust factor 0.90 covers it with 2.44 left. **Two flight packs** are in the cost. At 1,845 g the margin is +6 % on pack energy: **MARGINAL**. At 1.95 kg it is zero. Fallback: a 4S 3000 mAh pack (356 g listing, per RESTUDY B), which adds about 145 g and raises hover power about 7 %.

CG and static margin (`EST`, wing-alone NP at 25 % MAC less 18 mm for pod and tractor props at 90 deg): NP 0.145 m aft of the root LE, CG 0.120 m for a 10 % MAC margin (0.025 m). Hover balance needs CG at the point where 2 x front arm = rear arm; we set front motors 0.20 m ahead and rear 0.40 m aft of this CG. Heavy items (pack, FC) go in the pod nose to trim; the pack slides on its tray to set the CG within +/-10 mm. A flying-wing NP estimate this crude carries 5 to 10 % MAC error: **MARGINAL**, to be confirmed by a CG balance and a first glide.

## 7. Cost (cost_T.py, RESTUDY basis)

| Item | Qty | Unit $ | Ext $ | Tag |
|---|---|---|---|---|
| T-Motor AT2317 KV880 (3 + 1 spare) | 4 | 39.99 | 159.96 | `V` |
| APC 11 x 5.5E props (3 + 5 spare) | 8 | 4.17 | 33.36 | `V` |
| LANRC 45 A ESC 4-pack | 1 | 30.00 | 30.00 | `U` |
| Powerhobby 329TG (2 + 1 spare) | 3 | 27.95 | 83.85 | `U` |
| Tilt pivots, bench-rig extras | 2 | 12 / 10 | 22.00 | `EST` |
| 2 flight packs at $25 (listing $17.99) | 2 | 25.00 | 50.00 | `U` |
| XPS, CF tubes (2), PETG, tape / glue / foam board | | | 195.57 | `U` (K06 cost.csv) |
| AS150U anti-spark + leads | 1 | 15.00 | 15.00 | `EST` |
| **Chosen goods** | | | **589.74** | |
| Tax 10.25 % | | | 60.45 | |
| Shipping, 5 vendors x $10.71 | | | 53.55 | |
| **Chosen total** | | | **703.74** | |
| Floor (RESTUDY §1, includes radio, FC, GPS, airspeed, 3 elevon servos, charger, test gear, tools, FAA) | | | 744.02 | |
| **Spend** | | | **1,447.76** | |
| Crash reserve (1 pack + 1 servo + 1 airframe set `EST` $70) x 1.1025 + 2 shipments | | | 156.97 | |
| **All-in** | | | **1,604.73** | |
| **Margin to $2,000** | | | **+395.27** | |
| Margin with chosen parts +30 % (floor unchanged) | | | +184.15 | PASS |

Not in the floor and not added: Remote ID ($39.99 in K06 cost.csv, conditional on flying outside the field's FRIA). Adding it leaves a margin of about +$352. Spares carried: 1 motor, 5 props, 1 tilt servo, 3 ESCs (4-pack minus 3). I did not check vendor shipping for T-Motor; $10.71 is the RESTUDY default. One bad crash of a tilt-tri (2 motors, 2 servos, nacelle, pack, wing half) costs about $250 to $340 (K06 cost.csv "one bad crash" $339.66), above the reserve for one but not two crashes.

## 8. Risks and schedule

| Risk | Rating | Why |
|---|---|---|
| Car-box fit | PASS | pieces at most 0.80 m, box 1.25 m |
| Hover T/W 2.0 fresh / 1.6 sag | PASS | 2.72 / 2.44 on a published table |
| Mass | PASS to MARGINAL | build 1.745 kg, 1.845 kg with growth; most items `EST`, K06 REVIEW found its first-pass masses 0.25 kg low |
| Yaw authority in 5 m/s | PASS | 3.7x `EST` |
| Yaw / transition tuning on a scratch tri | MARGINAL | forum threads show yaw oscillation, firmware sensitivity, mixer errors; no scratch tri with logs found |
| Pack energy | MARGINAL | +6 % at 1.845 kg; zero at 1.95 kg |
| Static margin | MARGINAL | crude NP |
| Prop handedness for the counter-rotating pair | MARGINAL | no 11 x 5.5 pusher found at APC |
| Motor-out | FAIL | single-point failure on any of 3 motors |
| Tilt-servo failure | MARGINAL | stuck-up survivable in hover, dead or forward is a crash; no ArduPilot handling documented |
| Cost | PASS | +$395 margin, +$184 at +30 % parts |
| Schedule to 30 April | MARGINAL (Medium-High) | see below |

Schedule (`EST`; K06 card estimates about 120 person-hours build and 3 to 4 weeks of hover and transition tuning; 24 weeks from today to 30 April):
- Mid-December: floor and motors ordered; order the CF tubes early (K06 notes overseas lead time).
- January: nacelle prototype and 200-cycle tilt bench rig on the thrust stand (K06 first test); expect three print iterations (K06 card). Thrust-stand check of the table at 4S.
- February: airframe built, CG balance, tethered QHOVER below 3 m.
- March: free hover tuning, then transition (the long pole).
- April 1 to 15: full mission; leaves about 2 weeks of margin before 30 April.
The schedule works if the first tethered hover happens by the end of February. A crash with a reprinted nacelle costs 1 to 2 days; a stripped tilt-servo or motor-out crash costs a week with spares in hand.

## Gaps and next steps

1. Bench-test the AT2317 + 11 x 5.5 on 4S (verify the table, hover current, 25 A peak) and resolve the counter-rotating prop.
2. Weigh the first nacelle and the pod; re-run `sizing_T.py` with measured masses.
3. Read the Catastrophic-transition and Nimbus threads in full before committing; only titles were seen.
4. Price a smaller tilt servo and a 3000 mAh pack from vendor pages.
