# QP-1 design review board (J6), 2026-11-14

Board: aero / flight control, structures, electrical / propulsion, build-and-test / schedule critics; J6 chair decides.
Inputs: `SIZING.md` (B), `SIZING-A.md` (A), `SIZING-T.md` (T), `COST.md` (+ `qp/cost/BOM-QP1.csv`, `bom_qp1.py` re-run today), `REQUIREMENTS.md`, `qp/requirements/{REQUIREMENTS-QP,TEST-PLAN-QP1,CARRY-OVER}.md`, `config-study/RESTUDY-2026-11-14.md`, `config-study/tiebreak/DECISION.md` (D-181), `CLOSURE-ROUND-2026-11-14/{DESIGN-TO-COST,A1-STATUS}.md`.
Board arithmetic: `python -I` on a scratch script (not in the repo); every input is a number from the files above and the formula is shown where used. Labels: `V` vendor page read, `U` snippet, `EST` estimate, `—` unknown. Nothing bought, built or flown. No other file edited; no git.

## Verdict

**Chair: build A, the scaled quad tailsitter (0.90 m wing, 4 × T-Motor MN2212 KV780, 4S, ~1.4 kg `EST`). Fallback: B, the 4+1 quadplane, re-priced. D2 is a date-triggered lifeboat only.** This reverses D-181's provisional pick.

Reason in one line: B as its own sizing agent specified it has **+$117 margin, +$8 with EST/U lines +30 %, and 4 % mass headroom to its T/W gate**, the same thin-margin pattern that killed K09-L; A has +$501 / +$387 and 18 % mass headroom, and its weak points (hover yaw, wind lean, fin vibration, static margin) are geometry choices that $0 SITL and < $60 bench tests can settle before the 15 Dec order. One reversal trigger is explicit: if a ≤ $25 lift motor passes the 4S bench test, B's cost recovers and B is re-scored (B then leads, 79 vs 71).

| KPI | A tailsitter | B quadplane | T tilt-tri | D2 Altus kit |
|---|---|---|---|---|
| Total / margin, sized parts | **$1,499 / +$501** | $1,883 / **+$117** (risk) | $1,605 / +$395 | $1,552 / +$448 |
| Margin, EST/U lines +30 % | +$387 | **+$8** (fail $100 rule) | +$184 | +$346 |
| Mass headroom to T/W gate | 18 % (1.66 kg) | **4 %** (2.28 kg) | 6 % on pack energy | — |
| Weighted score (/100) | **71** | 67 | 45 | 59 |

## 1. What the board found wrong in the inputs

Three inconsistencies change the comparison; none was visible in any single report.

1. **COST.md priced different motors than the sizing reports chose.** COST prices SunnySky X2212 KV980 ($15.99 `V`) for both A and B; SIZING.md picks T-Motor MN3110 ($61.90 `V`) for B's lift and MN2212 ($46.90 `V`) for the pusher; SIZING-A picks MN2212 for A, because the X2212 has no published 4S table (RESTUDY §2). Re-pricing COST's totals with the sized parts (formula: Δgoods × 1.1025 tax + one T-Motor shipment $10.71 `EST`):
   - B: Δgoods = 5 × 61.90 + 2 × 46.90 − 6 × 15.99 + 8 × 4.49 (APC 12x4.5MR `U`) − 2 × 12.99 = **+$317.30** → total **$1,882.56, margin +$117.44**; EST/U lines (293.94 + 35.92) +30 % × 1.1025 → **+$8.34**.
   - A: Δgoods = 5 × (46.90 − 15.99) + 6 × (10.42 − 2.99) (T9545 pairs `U`) = **+$199.13** → total **$1,498.67, margin +$501.33**; +30 % → **+$386.74**.
   - SIZING.md itself already flagged B at $1,806 / +$194, and +$34 if the reseller price applies (its risk 6). D-181's $1,625 assumed X2212 lift thrust that no one has measured.
2. **ESC mass.** The only in-stock ESC read (HobbyWing Skywalker 30A V2) is 33 g vs 10 g assumed (COST.md). Board re-roll, mass × (1 + 10 % contingency): A 1,115 + 4 × 23 + 38 (Tattu 2300 pack vs CNHL 2000) → **1,370 g, T/W fresh 2.52, sag 1.93**; B 2,060 + 5 × 23 + 5 → **2,180 g, T/W fresh 2.09, sag 1.72**. Headroom to the T/W 2.0 fresh / 1.6 sag gates = min(m·TWf/2.0, m·TWs/1.6): A 1.655 kg, B 2.276 kg, T 2.509 kg. B is 96 g (4 %) from failing; K09-L's gate moved 2.60 → 2.70 kg (+4 %) in one closure round (A1-STATUS.md).
3. **The Skywalker 30A V2 is a fixed-wing PWM ESC.** COST.md says fast multirotor PWM is not confirmed; the board adds that the rpm-tracking notch carried from K09L.param (`INS_HNTCH_*` mode 3, CARRY-OVER §1 section 8) needs bidirectional DShot telemetry. Every concept that hovers on fixed motors needs a DShot ESC that is not yet sourced in stock (`—`).

Also: the mission is defined three ways (B 17 m/s and 204.5 s cruise against a 3.5 min line; REQUIREMENTS-QP 15 m/s and 3.6 min; A and T 3.5 min at 15-16 m/s). B's SIZING.md shows 3.41 min against 3.5 min: a definition gap, not an energy gap, but it must be one number before gates. And `qp/README.md` lists "one-piece car-box transport" as a user constraint while the board's brief says only "a box that fits a standard car" and calls the 1.25 m box derived: the user must say which (decision card D-J6-2).

Lesson carried from K09-L (DESIGN-TO-COST §0-§1, A1-STATUS top block): the estimate grew from $1,580 to $3,110 because tools, crash reserve, the fin tube and pack changes were added late, and the mass gate crept, forcing prop, motor and pack changes in cascade. The board therefore measures each candidate by **how much growth it absorbs**: margin ÷ (candidate goods × 1.1025). A 77 %, D2 73 %, T 61 %, **B 12 %**. K09-L-scale growth (×2 on candidate goods) breaks every candidate; ×1.3 breaks only B.

## 2. Critics' findings

### Aero / flight control

- **A** `risk`. Hover yaw ratio 1.57 at 14° cant against limit 1.5 rests on `EST` plate Cd 2.05 and arm; K09-L's 10° cant gives 1.25 (fail) here. Lean 29° at 5 m/s, 47° at 7 m/s needs `Q_ANGLE_MAX` ~45. Transition window 1.33-1.73 W (±13 %) comes from a point-mass model without pitch moment or elevon limit; K09-L's full B3 model gave ±2.5 %, so **±13 % is optimistic until a time-domain run exists**. Parked tip-over at 6.8 m/s is below the 8 m/s survive-and-land gust (QP-P14): crew must catch or lay down the aircraft after touchdown. 1.3 Vs = 14.3 m/s against 15 m/s cruise (5 % gap) and the 9545 prop's pitch speed 13.4 m/s is below cruise (η_p 0.26 `EST`). SM 6.6 % only with the pack ahead of the LE.
- **B** `met` on control architecture, `open` on numbers. Speed-scheduled QuadPlane transition and gear landing are the lowest-risk items in the study. Not computed: hover in 5 m/s wind (lean, yaw by rotor torque against a tail that weathervanes), boom-flex coupling. L/D 5.8 hangs on parked-prop CdA 0.0048 `EST`. `Q_ASSIST_SPEED` conflict (10.0 vs 11.6 m/s) unresolved.
- **T** `risk`. Vectored yaw 3.7× (`EST`) is the best yaw margin. Transition tuning evidence for a scratch tri is forum titles and snippets; one listed crash cause is a swapped `Q_TILT_MASK`.
- **D2** `open`. No maker ArduPilot file; hover T/W 1.82 `EST` (RESTUDY) is **below the 2.0 fresh gate applied to A, B and T**, and the 361 g Tattu 3700 may exceed the 1.1-1.3 kg listed flying weight (`—`).

### Structures

- **A** `risk`. Fin f1 separation from 1P/2P is 43 / 22 / 7 % at root fixity 1.0 / 0.85 / 0.75 (need 20 %); K09-L's C4 found the root, not the fin, set stiffness. Fin mass 36 g for two fins with pads looks low: 0.2 mm CFRP both sides of a 0.36 × 0.12 m fin at 1,550 kg/m³ (`EST`) is ~27 g of skin per fin before foam. Board estimate: +30-40 g. Inside the 18 % headroom. 12 g, 147 N hard-landing load on the fin tips is not analysed.
- **B** `open`. Two 1 m CF booms (16 × 14 mm `V`) carry four lift motors; boom modes ≥ 20 % from 1P/2P (QP-P16) are not computed. The 1.20 m wing needs a plug-in joint (spar joiner, servo plugs). Rear discs overlap the TE by 13 mm.
- **T** `risk`. Two tilt nacelles with bearings and a 63 g servo each; K06 REVIEW found first-pass masses 0.25 kg low; three print iterations expected (K06 card).
- **D2** `met` for the kit structure as sold; modifications `—`.

### Electrical / propulsion

- **A** `risk`. MN2212 table rpm column is inconsistent (implies CT 0.148, too high for a 9x4.5); thrust and power cross-check at FM·η 0.48. Full-duty current 13.3 A vs 13 A rating fresh; `Q_M_SPIN_MAX` 0.90 fixes it. Hover 2.4 A/motor (~2.8 A at 1.37 kg, `EST`, I ∝ m^1.5). Pack 1.3× energy margin (`EST`, re-rolled mass and 34 Wh Tattu 2300).
- **B** `risk` on cost, `met` on physics with MN3110 (13 A of 21 A, published table, APC derate 0.95 `EST`). With X2212 the thrust and current on 4S are `—`. Energy 1.28× on 3000 mAh; ~1.5× on the in-stock 3700 (`EST`).
- **T** `risk`. AT2317 + APC 11x5.5 table is published, but **no counter-rotating 11x5.5 exists at APC**, so the table may not apply to one front motor. Pack energy +6 % at 1.845 kg, zero at 1.95 kg. 40C pack.
- **D2** `open`. Stock motors and ESCs, no table.
- **All**: in-stock DShot ESC `—`; GPS on backorder (F04); FC is the $95.98 Kakute F405 Wing Mini (log to 16 MB flash, no SD) because the CoreWing is unavailable.

### Build-and-test / schedule

24 weeks to 30 April; Jacobs closes 19 Dec-18 Jan (COST.md), so the effective shop window is ~20 weeks.
- **A**: fewest parts (one wing, two fins, one motor cage, no booms, tail, gear or pusher). ArduPilot tailsitter support exists and the team owns a reviewed `K09L.param`, transition switch, B3 transition models, landing and fin analyses, and the H1 stand plan. Tuning risk is the pitch-over and hover in wind. Build hours `—`, lowest by part count.
- **B**: QuadPlane is the most-flown ArduPilot VTOL and `../firmware/vtol_c0.param`, `check_params.py`, `mission_test.py`, `c0_physics.py` carry (CARRY-OVER). Most build work: two wing panels with joiner, pod, two booms, tail, gear, 5 motors.
- **T**: K06 card 120 person-hours `EST`, 3-4 weeks of hover and transition tuning; tethered hover by end of February or the schedule fails (SIZING-T §8).
- **D2**: kit assembly; lowest build effort, but parameter set from scratch and stock availability unclear (product page "In Stock", collection page "backorder").

## 3. Scored comparison

Scores 1-5 (5 best). Weights: cost margin 20, technical risk 25, schedule 20, transport 5, mission margin 10, reuse 10, educational content 10 (sum 100). Cost and schedule are hard user constraints; technical risk feeds both, so it carries the largest single weight. Weighted score = Σ w·s / 5.

| Criterion (w) | A | B | T | D2 | Basis |
|---|---|---|---|---|---|
| Cost margin (20) | 5 | 1 | 3 | 4 | §1: +$501 / +$117 / +$395 / +$448; at +30 %: +387 / **+8** / +184 / +346 |
| Technical risk (25) | 2 | 4 | 1 | 3 | A: yaw, lean, tip-over, fin, transition all marginal on `EST`; B: lowest-risk control, booms open; T: motor-out fail on 3 motors, tilt-servo SPOF; D2: T/W 1.82 `EST` |
| Schedule (20) | 3 | 4 | 2 | 3 | ArduPilot maturity QuadPlane > tailsitter (own file) > tilt-tri; part count A < B; D2 has no param file |
| Transport (5) | 5 | 3 | 2 | 4 | A one piece, props on, 0.90 × 0.50 × 0.39 m; B plug-in wing; T 3+ pieces; D2 0.98 m span, joints `—` |
| Mission margin (10) | 3 | 4 | 2 | 3 | Energy A ~1.3×, B ~1.3-1.5×, T 1.06×, D2 1.46× `EST`; A cruise 5 % above 1.3 Vs |
| Reuse (10) | 5 | 3 | 2 | 2 | A: tailsitter params, B3, landing, fin, stand; B: C0 QuadPlane tooling; T: K06 card |
| Educational (10) | 4 | 5 | 5 | 1 | B: classic wing/tail/boom sizing; A: tailsitter dynamics; T: mechanism; D2: kit |
| **Weighted** | **71** | 67 | 45 | 59 | |

Sensitivity: technical risk 35 / cost 10 → B 73, A 65 (B leads). Cost 30 / technical 15 → A 77, B 61. **B with a ≤ $25 lift motor that passes the bench (cost score 4) → 79**, the highest of any case. So the decision turns on one measurable fact: the price of a lift motor that lifts B. The board picks on the evidence held today and makes that fact a named reversal trigger.

## 4. Decisive uncertainties and the cheapest test for each (before the 15 Dec main order)

| Cand | Decisive uncertainty | Cheapest test | Cost | Fails if |
|---|---|---|---|---|
| A | Hover in 5 m/s crosswind and 7 m/s gust; yaw ratio | ArduPilot tailsitter SITL (stage A logic, then A mass/inertia) with crosswind; frame name `UNVERIFIED` until checked in `vehicleinfo.py` | $0 | lean > `Q_ANGLE_MAX` 45 at 7 m/s, or yaw saturates at 5 m/s |
| A | MN2212 + 9545 thrust (rpm column inconsistent) | QP1-2 stand, one motor, 4S | $46.90 + prop (motor is flight stock) | < 854 g at 100 % fresh (0.93 × 918 g → T/W fresh 2.34 at 1.37 kg) |
| A | Cant 14° yaw authority | hanging yaw test (K09-L `T-B3-HOVER-YAW-WTIP` method) on a foam-board planform with the 4 bench motors | ~$10 foam `EST` | ratio < 1.5 at 14-16° cant |
| A | Fin root stiffness | tap test of a sample fin and root mount (phone accelerometer) | ~$15 `EST` | f1 within 20 % of 1P/2P (71/142, 76/153 Hz) |
| B | Lift motor ≤ $25 with a 4S table | X2212 KV980 CW + CCW on the stand, 1045 prop, 4S | $31.98 `V` | < 1.10 kgf fresh (T/W 2.0 at 2.18 kg ÷ 4) within its rated current (rating `—`) |
| B | Hover in wind, assist window | QuadPlane SITL S1-S7 (TEST-PLAN-QP1) | $0 | — |
| B | Boom modes | QP1-5 tap test of a 16 × 14 mm tube | $27.46 `V` | mode within 20 % of 1P/2P |
| T | Motor-out | none: architectural (any of 3 motors) | — | already fails |
| T | Counter-rotating prop | read APC 11 × 4.7 SF/SFP table | $0 | no matched pair |
| D2 | Hover T/W and ArduPilot setup | read ZOHD manual / forum logs; otherwise buying the kit is the test | $0 / $299.99 | T/W < 2.0 at flying weight with the 3700 pack |

## 5. Chair's decision

**Concept: A, scaled quad tailsitter.** Working point (`EST`, re-rolled): 0.90 × 0.245 m wing, two 0.36 m fins, 4 × MN2212 KV780 at 14° cant, 9545-class props, 4S 2300 mAh × 2, ~1.37 kg, total ~$1,499, margin ~$501.
**Fallback: B, small quadplane 4+1**, entered only through trigger R1 or R2 below, and only with a re-priced lift motor that keeps its margin at +30 % above $100.
**Lifeboat: D2 ZOHD Altus**, only through date trigger R4; it fails the educational criterion and its T/W is unverified.

Why not anchor on D-181: D-181 chose B at $1,625 / +$375 with X2212 thrust `EST`; B's own sizing round then moved it to MN3110 motors and 2.06-2.18 kg, which removes the cost case that justified it. D-181's concern about the tailsitter in wind is real and is carried as conditions C1-C3, not dismissed.

### Conditions

| # | Condition | Owner role | Closes |
|---|---|---|---|
| C1 | Motor mounts at 14° cant minimum; hanging yaw ratio ≥ 1.5 measured before any free hover | aero / structures | `risk` hover yaw |
| C2 | Flight card hover wind ≤ 5 m/s steady, land wing-edge into the wind; crew catches or lays the aircraft down at touchdown (parked tip 6.8 m/s < 8 m/s gust); `Q_ANGLE_MAX` from SITL | flight test | `risk` lean, tip-over |
| C3 | B3-style time-domain pitch-over with elevon limit, run before the first transition; the ±13 % window is not used until then | aero | `risk` transition |
| C4 | Pack in the motor cage ahead of the LE; CG breadboard shows SM ≥ 5 % before the wing is cut | structures | `risk` SM 6.6 % |
| C5 | **Mass gate 1.50 kg, frozen** (T/W sag at gate 2.16 × 1.226 / 1.50 = 1.77); any change needs the board | A1 | K09-L gate creep |
| C6 | One BOM (sized parts, DShot ESC, Kakute or CoreWing) and one mission definition (speed, cruise time) shared by all reports; re-run `bom_qp1.py` | cost / A2 | §1 items 1-3 |
| C7 | Cruise prop chosen on the bench (9545 vs a higher pitch) with hover T/W still ≥ 2.0 fresh at the gate | propulsion | `risk` pitch speed 13.4 m/s |
| C8 | Fin tap test passes 20 % separation at the as-built root | structures | `risk` fin modes |

### Reversal triggers

| # | Trigger | Action |
|---|---|---|
| R1 | A lift motor ≤ $25 measures ≥ 1.10 kgf fresh on 4S within its rated current **and** B's re-priced margin at +30 % is ≥ $150 | board re-sits A vs B within one week; B is expected to lead (score 79) |
| R2 | A fails in SITL at 5 m/s crosswind, or yaw ratio < 1.5 at 16° cant, or the time-domain pitch-over finds no window ≥ ±5 % | switch to B (with a motor that meets R1's price line) |
| R3 | A weighs > 1.50 kg at the CG breadboard, or MN2212 < 854 g at 100 % | resize (props, pack) once; second failure → B |
| R4 | No tethered hover of the chosen concept by 2027-02-15 | order D2 for the April flight test |
| R5 | A's re-priced total > $1,750 (margin < $250) | board re-sits |

### First three actions

1. **SITL, now, $0:** install per `subsystems/flight-software/SITL-PLAN.md`; run the tailsitter quad with `K09L.param` adapted to A's mass and inertia (`EST`), 5 m/s steady and 7 m/s gust crosswind hover, and the stock QuadPlane S1-S7 for B. Due 2026-11-30.
2. **Order the bench kit with the floor** (common to A and B, nothing wasted): 2 × MN2212 + 9545 and one higher-pitch prop, 2 × X2212 KV980 CW/CCW + 1045 ($31.98 `V`), one 4S pack, stand parts, watt meter, two DShot ESCs (source `—`). Run QP1-2 for both motors and the hanging yaw test by 2026-12-10.
3. **One BOM, one mission, one gate** (C5, C6) before 2026-12-10, so the 15 Dec order is placed on the decided concept with vendor-page prices only.

## What the team must measure

- **M1** MN2212 + 9545, 4S, thrust at 100 % fresh on the stand. Fails R-T/W below 854 g per motor at 1.37 kg.
- **M2** X2212 KV980 + 1045, 4S, thrust and current. ≥ 1.10 kgf within rating triggers R1.
- **M3** Hanging yaw ratio at 14° cant (foam planform, 4 bench motors). Fails below 1.5.
- **M4** Fin and root tap test (phone accelerometer). Fails within 20 % of 71 / 142 Hz.
- **M5** CG breadboard on a kitchen scale and knife edge with the pack in the cage. Fails below SM 5 % or above 1.50 kg.
- **M6** SITL crosswind hover. Fails if lean exceeds 45° at 7 m/s or yaw saturates at 5 m/s.

## Open decision cards

**D-J6-1 Does the board's pick replace D-181?** D-181 (A1) chose B; this board picks A on re-priced numbers. Recommended: A1 records D-182 = A with fallback B, triggers R1-R5. Alternative: keep B and buy down its cost first with M2. Evidence §1, §3.

**D-J6-2 Is one-piece transport a user constraint?** `qp/README.md` says yes; the board brief says the box is derived and no car is measured. A passes either way; B needs a plug-in wing. Recommended: ask the user, and measure one team car. Evidence §2 transport.
