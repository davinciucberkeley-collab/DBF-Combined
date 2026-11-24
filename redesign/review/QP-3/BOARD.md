# QP-3 design review board (J6), concept A pre-order review, 2026-11-15

Board: aero / flight control, structures, electrical / propulsion, build-test-schedule critics; J6 chair decides.
Inputs: `review/QP-1/BOARD.md` (C1-C8, R1-R5); `review/QP-2/{SITL,WIND,BENCH,BASELINE,D183,D184}.md`; `review/QP-3/{SITL-FLIGHT (incl. Follow-ups),STRUCTURES (iter. 1-2),COST-SCHEDULE,CAD (incl. s8)}.md`; `qp/A/{A.param,MISSION,MASS-GATE,REQUIREMENTS-A,SCHEDULE-A}.md`, `BOM-A.csv`; A1's open-items list (scratch, 2026-11-15). Board checks run today: `qp/A/sitl/fu_level.py` re-run (cruise rpm), `a_apc_data.py` read (zero-thrust J), `qp/A/cad/a_assembly_blender.py` read (mesh fix import), arithmetic in `python` on numbers from the files above (formulas shown).
Labels: `V` vendor page, `CALC` computed from repo numbers, `EST` estimate, `—` unknown. Nothing bought, built or flown. No other file edited; no git.

## Verdict

**Bench-kit order (Order 1, 1-4 Dec): YES, with four $0 conditions (s7.1). Main order (18 Dec, latest-safe 28 Dec): NOT YET; five items stand between A and it (s7.2), and nine go / no-go lines decide it (s7.3).** A stays the concept. No reversal trigger has fired as written, except **R5, which trips by $3-15 once the bench lines are counted**; the board re-sits it here and replaces it (s1 item 1).

The design is not wrong; it is less finished than its reports read when taken one at a time. The cross-file check found the K09-L pattern starting again: the margin that absorbs growth fell from 77 % to 18 % in three days, and the first CAD moved the CG 8.6 mm out of its band. Both are caught before money is committed, which is the point of this round.

| KPI | Value | Status | Source |
|---|---|---|---|
| Total incl. bench lines / margin at +30 % on unverified lines | ~$1,753 / ~+$123 `CALC` | risk (rule >= $100) | COST-SCHEDULE s1; STRUCTURES iter. 2 BOM; s1 item 1 |
| Growth absorbed = margin / (goods x 1.1025) | **18 %** (QP-1: 77 %) | risk | `CALC` s1 item 1 |
| Predicted mass (CAD basic + growth + overrun) / target / gate | 1,392 g / 1,440 / 1,500 | met | CAD s4 |
| CG, CAD / design band / hard limits | **16.2 mm** / 20-26 / 4.0-28.5 | fail on band | CAD s4, s8 |
| Schedule slack to 30 Apr (4 booked mornings/wk, one crash) | 11 d | risk | SCHEDULE-A |

## 1. What the board found that no single report shows

1. **Cost: R5 trips and growth headroom collapsed.** COST-SCHEDULE: total $1,679.37; bench lines not in the BOM $75.23 + $10.6 bump = **$1,765.20 > R5 $1,750**. STRUCTURES iteration 2's tube change (-$10.94 goods x 1.1025 = -$12.06, not yet in `BOM-A.csv`) gives **$1,753.14**, still $3 over. Margin at +30 %: $111.1 (COST-SCHEDULE) + about $12 = **~$123**. Growth absorbed = (2,000 - 1,753) / ((1,193.49 + 60.98 - 10.94) x 1.1025) = **18 %**; QP-1 chose A because it was 77 %. The money went to real lines the QP-1 board missed (crash reserve, tools, test gear: BASELINE s1), not to spec creep, but **one unplanned $25 line now puts the +30 % margin near the $100 rule**.
2. **Cruise rpm disagrees by 20-40 %.** `fu_level.py` (re-run today, same aero and APC model as the SITL plant): 17 m/s level at **7,300-7,540 rpm** (duty 0.60-0.70). STRUCTURES iteration 2 uses 8,900-10,500 rpm (`EST`, "the APC file has no V > 0 data"; it does: `a_apc_data.py` has Ct vs J). Consequences: (a) the fin "3 % margin at knock-down" is an artefact (s5); (b) cruise runs at **J = 17 / (125 x 0.2286) = 0.595, against zero thrust at J 0.64** (`a_apc_data.py`, 10,000 rpm row): cruise power and THR_MAX rest on the APC model in the region where a small Ct error is a large thrust error.
3. **Elevons are two different parts.** SITL plant: y 0.10-0.40 m each side, stops +-25 deg (SITL-FLIGHT s1). CAD and STRUCTURES: y 0.04-0.34 m, +-20 deg (the fin root occupies 0.34-0.38). Same area, roll arm 0.19 vs 0.25 m: roll moment per degree x0.76 `EST`, so the 95 deg/s at +-8.7 deg (SITL-FLIGHT s8 item 4) becomes about 72 deg/s; 90 deg/s then needs about +-11 deg `EST`, inside +-20 but stacked on trim (s4). The hinge-moment ratio improves: 1.61 at 25 deg becomes about 2.0 at a 20 deg stop (linear in deflection, `EST`).
4. **The SITL flew SM 6.5 %; the drawn aircraft is SM 10.0 %** (CAD s4). Every transition and back-transition pass in SITL-FLIGHT is at the old CG.
5. **The FC mount is not the one analysed.** `fu_cage.py` puts the IMU on the spar-centre node. CAD puts the FC 26 mm aft of the spar on a plate bonded to foam, on four 5 mm gel pads whose stiffness is `—`. A gel mount adds a mode of unknown frequency that could sit in the rate band (< ~40 Hz) or on hover 1P (100-119 Hz).
6. **The fin laminate risk is already retired, but two reports still schedule it.** STRUCTURES iteration 2 replaced the 0.2 mm CFRP skin with a 16x14 tube + 3 mm XPS fairing (US stock). COST-SCHEDULE s2 and SCHEDULE-A still call R04 the top risk and "order first"; `BOM-A.csv` still carries R04 ($40 `EST`) and two 16x14 tubes.
7. **Fence: 245 m is a fail, not a marginal.** SITL-FLIGHT FU s4 compares 245 m against "250 m less `FENCE_MARGIN` 10 m" = **240 m**.
8. **The yaw gate cannot run before the main order as planned.** The 0.35 N m hanging test needs four motors (BENCH s2 step 7); Order 1 buys two (COST-SCHEDULE s2); SCHEDULE-A B0 still needs the result before D1.
9. **The R4 lifeboat is not funded.** D2 is $299.99 x 1.1025 = **$330.74** `CALC`; the +30 % margin is ~$123. D2 can be bought only from the $311 crash reserve.
10. **Stale against the latest numbers** (C6 one-truth rule): `BOM-A.csv` (tubes, R04); `MASS-GATE.md` (structure 460 g, fins 70, CG 24.8); REQUIREMENTS-A A-P8a (`Q_WVANE_ENABLE` 0), A-P10 (old fin bands 71/142 Hz), A-P13 ("not computed"), A-P24 (far point 201 m); MISSION s3 (`Q_WVANE` 0); `structures_a.py` VD 22; `A.param` `INS_HNTCH_FREQ` 70 (9545-era 1P; hover 1P is now 100-119 Hz).

## 2. Critics' findings

### Aero / flight control
- `met` on the SITL model: transition, cruise at 17 m/s, back-transition, landing, takeoff, failsafes (SITL-FLIGHT s2-s5). `risk`: the aero is `EST` and gentler than K09-L's B3 (no measured post-stall moment peak); the window 1.285-1.60 W is "a pass on this model", not proof (SITL-FLIGHT s2).
- `risk`: CG and elevon geometry in the SITL are not the drawn aircraft (s1 items 3-4). A re-run on the as-drawn aircraft is $0 and must precede the wing cut.
- `risk`: cruise at J 0.595 vs zero thrust 0.64 (s1 item 2). THR_MAX 68 leaves 0.06 duty above the modelled cruise duty (FU s1); MISSION's cruise power is 10-15 % above the model. The static bench cannot measure this; C7 as written cannot close.
- `risk`: weathervane mode 3 was proven only in calm SITL (FU s5); it is lean feedback, so turbulence may make it chase gusts.
- `met`: `Q_TAILSIT_RAT_VT` 24 removes the cap in head wind; crosswind still 2.2-2.4 s at the cap (FU s3).

### Structures
- `met`: strength everywhere (STRUCTURES iter. 2: spar MS +2.73, thinnest bond +0.34); landing stroke 15.2 of 20 mm; tip-over 33.2 deg (at CG 20 mm instead of 25.2: atan(180/280) = 32.7 deg `CALC`, still >= 30).
- `met` on separation for strongly coupled modes (<= 78 Hz vs 83.3, hi corner 7 %), forced response unbalanced MS +0.63-0.67 (iter. 2).
- `risk`: the softness that buys rotor separation puts cage modes at 8-15 Hz inside the rate loop; closure rests on gains, filter, IMU location and an assumed 0.3-1 % damping (FU s2). Tap test of the built cage is mandatory.
- `open`: flutter / divergence at VD 24 never computed. A 0.9 m foam-and-tape wing with a single spar at 0.245 c and tape-hinged elevons on 1.2 mm rods is the configuration where it matters.
- `risk` (mass): structure 473 g vs 460 allocated; fins 119 vs 70. Inside the 1.44 kg target (CAD 1,392 g).

### Electrical / propulsion
- `met` on the model: T/W fresh 2.30, sag 1.82 capped at the gate; 0.90 cap keeps one motor at 12.1 A vs 13 A (D184.md).
- `open`: SpeedyBee 4-in-1 bidirectional DShot unverified (BLHeli_S J-H-40); `INS_HNTCH_MODE` 3 depends on it. Single source, no spare board.
- `open`: MN2212 stock and lead time unknown (COST-SCHEDULE s2) — the one part with no in-stock evidence, and the one A cannot substitute.
- `risk`: APC static table predicts +24 % over the maker's 9545 row (D183.md s2); the x0.93 derate is a guess until M1.
- `met`: energy 1.18x at 1,381 g, 1.08x at the gate (MISSION s4); breaks above ~200 W cruise.

### Build-test-schedule
- `risk`: 11 d slack needs >= 4 booked RFS mornings a week from 8 Feb with one crash (SCHEDULE-A). At 3 a week one crash misses 30 April by 10 d.
- `risk`, compound: the turbulence-yaw fallback is a 4 m/s card (WIND s4), which drops the flyable fraction from 0.80 to 0.64 (WIND s3). SCHEDULE-A's 4 booked / p 0.60 / one crash row is **-5 d**. So "yaw marginal" plus "one crash" fails the deadline unless the team books 5 mornings a week (5 / 0.60 / crash: +12 d).
- `risk`: R4 (tethered hover by 15 Feb) leaves 2 d over the planned F01 (8-13 Feb), and fires before SCHEDULE-A's own latest-safe F01 (18 Feb).
- `met`: CAD, collision and 24-step assembly gates pass (CAD s1, s5) — A-U4 is on track.

## 3. A1's proposed decisions

### D-185 (vibration requirement; structure 473 g): **ACCEPT, modified**

| Part | Ruling | Reason |
|---|---|---|
| Strongly coupled modes >= 20 % from every rotor band | accept; define "strongly" as motor coupling >= 0.5 (the iteration-2 threshold) | without a number the rule cannot be checked |
| Weakly coupled modes pass by forced response, unbalanced | accept at U = 1.0 g mm per rotor, FC <= 30 m/s2, all three corners, **swept over 6,000-10,500 rpm including the SITL cruise 7,300-7,600 rpm** | iteration 2 used six rpm points and a cruise band the SITL contradicts (s1 item 2); the 215-261 Hz spar modes (coupling 0.4) sit near cruise 2P 244-253 Hz |
| (added) Modes in the rate-loop band | closed-loop gain margin >= 2 at all corners with the flight parameter set (`fu_cage.py` method); built-cage tap test within +-20 % of FE or re-tune | the 8-15 Hz cage modes are the real coupling risk (FU s2), and D-185 as written does not cover them |
| Verification | IMU VIBE < 30 m/s2 in the first tethered hover; balancing to <= 0.3 g mm becomes the fallback, not the plan | U 1.0 g mm is `EST` |
| Structure 473 g | accept and **freeze** at wing 191 / fins 119 / cage 122 / hardware 40; any growth needs the board | CAD 1,392 g predicted holds the 1.44 kg target by 48 g |

### D-186 (SITL follow-ups)

| Item | Ruling | Reason / condition |
|---|---|---|
| `THR_MAX` 68 + `FWD_BAT_VOLT_MAX/MIN` 16.8 / 13.2 | **accept** | level speed 18.7 m/s fresh, below VH limit; condition: first cruise logs duty at 17 m/s. If > 0.65 fresh: THR_MAX 70 + VD 25 is allowed once the elevon stop is 20 deg (hinge ratio about 1.85 `EST`), else a higher-pitch prop (C7) |
| VD 24 | **accept**, flutter open | C1 gust n 3.02 < 3.4 (FU s1); flutter / divergence estimate required before the wing is cut (s5) |
| `TECS_CLMB_MAX` 2 | accept | worst-state climb 2.2 m/s (FU s1) |
| `INS_GYRO_FILTER` 60, pitch P 0.15 / D 0.002 / FLTD 40, roll P 0.20 / D 0.003 | **accept for the tether** | min GM 2.1-2.8 with IMU at the spar (FU s2); damping guessed; re-check after the cage tap test; `Q_A_RAT_YAW_FLTE` 4 trial if yaw rings (PM 34 deg) |
| FC on the spar centre | **modify** | keep the FC on the wing-centre plate as drawn, but **hard-mount it (thin foam tape), not on gel pads**, unless the gel mount's frequency is measured and lies between 40 Hz and 70 Hz `EST`; forced response already passes without isolation (iter. 2), and the analysis assumed a rigid spar node (s1 item 5) |
| `INS_HNTCH_*` (A1 flagged stale) | **modify** | set the base frequency from hover 1P 100-119 Hz, not 70 Hz; `MODE` 3 only if bidirectional DShot is confirmed on the bench, otherwise throttle-referenced; final values from the first IMU FFT |
| `Q_TAILSIT_RAT_VT` 24 | **accept** | 0 s at the cap in 0 and 5 m/s head wind (FU s3); card: back-transition into the wind only |
| `WP_LOITER_RAD` 40 | accept | outward excursion 70 -> 49 m (FU s4); 36 deg bank, stall 13.6 < 16 m/s |
| 200 m racetrack leg | **modify: leg <= 150 m** | any-direction bound = L/2 + 51 + 94 <= 240 needs L <= 190 m; 150 m gives 220 m (20 m margin), lap 620 m = 36.5 s, cruise time unchanged `CALC` |
| `Q_WVANE_ENABLE` 3, `GAIN` 1, `SPD_MAX` 2 | **accept, conditional** | works in calm SITL (FU s5); before first free hover: SITL with WIND.md's 1 m/s turbulence model, heading excursion <= 15 deg; card: QLOITER -> QSTABILIZE -> FBWA within 2 s so the vane never acts before the pitch-over; update A-P8a and MISSION s3 |

## 4. CG: change the layout, keep the band

**Ruling: move the pack aft (centre from -20 to <= -3 mm, +3.8 mm of CG, `CALC` CAD s8) and give the tray a +-10 mm slot so the M5 weigh-in trims CG without ballast. Keep the 20-26 mm band. Withdraw the 4.0 mm forward limit until the as-drawn SITL run sets one.** Optional second knob: the cage plane 10 mm aft (+3.3 mm, prop plane 121 -> 111 mm, still ahead of SIZING's 75-85 mm), only with a modes re-run, since a shorter bridge stiffens the cage and pushes the hi-corner arm mode (78 Hz) toward 83.3. Target 20-24 mm.

Basis (B3 terms):
- **Static margin.** The band is an SM band (6.0-8.4 %, NP 40.7 mm `EST`), and it is where all transition evidence sits (SITL at 6.5 %). The CAD's 16.2 mm (SM 10.0 %) is safer statically but has no flight evidence.
- **Elevon trim, cruise and transition.** Extra trim for +3.5 % SM: d(delta) = dSM x CL / |Cm_delta|, Cm_delta ~ 0.31 x 0.73 = 0.23 /rad `EST` (SITL CL_delta, elevon load at ~0.80 c). Cruise 17 m/s at 1.50 kg, CL 0.378: **+3.3 deg**; handover 13.7 m/s, CL 0.582: **+5.2 deg** `CALC`. SITL peak elevon was 8.6 deg against a 9 deg pitch-use line (0.60 of 15) at the old CG: the forward CG most likely fails that line, and CAD's +-20 deg stops (not 25) leave less room. Roll (s1 item 3) stacks on the same surfaces.
- **Back-transition.** A larger SM means a larger nose-down moment against the pitch-up; the crosswind case is already 2.2-2.4 s at the cap. A forward CG moves the marginal item the wrong way.
- **Hover trim** is by differential thrust of the upper / lower pairs; the CG offset changes hover trim little `EST`, so hover does not argue either way.
- **Why not lower the band:** it would accept an untested SM because a mass-property estimate (rest of aircraft 35.7 mm) was wrong. The band was not derived from that estimate; only the prediction was.
- If the pack cannot move (LE / tray conflict), the fallback is the as-drawn SITL run at 16.2 mm: if it passes every SITL-FLIGHT line with CAD elevons, the board lowers the band to that run's tested range, not further.

## 5. Remaining marginal items

| Item | Evidence | Ruling | Action, when |
|---|---|---|---|
| Flutter at VD 24 | never computed (FU s1) | **analysis before the main order** (a fix changes the spar or elevon purchase) | 2-DOF bending-torsion estimate with FE bending and a torsion stiffness from a twist test of a 300 mm wing-section coupon; flutter and divergence >= 1.2 VD = 28.8 m/s `EST` rule; elevon free play measured on the bench; flight speed build-up, `AIRSPEED_MAX` 18 kept |
| Back-transition, 5 m/s crosswind | 2.2-2.4 s at 0.90 cap (FU s3) | **acceptable risk** with a card rule | back-transition only on the into-wind leg; SITL at 45 deg and on the as-drawn CG before F04 decides the heading window ($0) |
| 245 vs 250 m fence | 245 > 240 (FENCE_MARGIN) | **design change** (flight card) | leg <= 150 m (s3); SITL check that a fence breach during QLAND does not command RTL (which starts a forward transition in a Q mode, FU s4) before F04 |
| Turbulence yaw 11-15 deg | WIND s1, own turbulence model | **acceptable risk, gated** | bench yaw >= 0.35 N m, tether turbulence <= 15 deg; 4 m/s fallback is pre-planned with 5 booked mornings a week (s2 schedule) |
| Fin mode 3 % at knock-down | 432 Hz vs 420 limit from cruise 2P at 10,500 rpm (iter. 2) | **acceptable risk** | with the SITL cruise rpm (7,300-7,600) the band top is cruise 2P 253 Hz x 1.2 = 304 Hz: margin 432 / 304 = ~42 % `CALC`; measure cruise rpm (audio FFT) on the first cruise to confirm |
| Bench yaw 0.346 vs 0.35 N m | model Q 59.7 N mm (D184.md) | **acceptable risk**; the bench is the test | >= 0.35 go; 0.30-0.35 go with the 4 m/s card pre-planned; < 0.30 no-go (R2) |
| 4 flying mornings a week | SCHEDULE-A | **needs a team commitment before the main order** | written booking plan from 8 Feb, three people per morning; merge the 20-touchdown campaign into F02 / F05 hover sorties (A1/A2 requirement change, recommended) |
| Motor-out fatal | SITL-FLIGHT s5; A-P20 | **acceptable, declared** | pre-flight motor test, 0.90 cap, card "no Q mode after a cruise motor loss"; note the reserve excludes FC and ESC (~$157 with tax `CALC`) |

## 6. K09-L collision-checker bug (inside-out meshes for parts rotated > 90 deg about X)

**No A conclusion rests on it.** `collide_a.py` and the assembly sweep both install the fix: `a_assembly_blender.py` line 10 imports `a_collide_blender` "(installs the orientation fix)", which reverses any body with negative signed volume (CAD s3). The A gates were also run before the fix and failed on it (6 false overlaps), which shows the fix is exercised.

**K09-L:** its collision and assembly PASS is unproven for any part rotated > 90 deg about X (CAD s3 item 1). K09-L is dropped (D-181 / D-182), and no A number comes from K09-L's CAD gate: A reuses K09-L's code, parameter file, B3 models and landing physics, none of which use the mesh code. Actions: fix `blender_mesh._body` at source before anyone reuses it; add one positive-control case to `collide_a.py` (a UL prop pushed 1 mm into the fin, must FAIL) since the signed-volume test is only valid on closed meshes ($0, minutes). Re-run K09-L's gate only if K09-L is ever reopened.

## 7. Chair's decision

### 7.1 Bench-kit order (Order 1, 1-4 Dec): YES, if these four hold (all $0, by 1 Dec)

1. `BOM-A.csv` carries iteration 2 (3 x 12x10, 1 x 14x12, 1 x 6x4.5, one 16x14, R04 removed) and the bench lines; `bom_a.py` re-run shows +30 % margin >= $100.
2. GPS connector mates the Kakute GPS port (COST-SCHEDULE s1); SpeedyBee firmware read for bidirectional DShot (or the throttle-notch fallback accepted).
3. T-Motor asked for stock and lead time. Order 1 takes 2 MN2212 and the yaw gate runs on one diagonal pair (same spin; pitch and roll cancel, yaw adds; superposition `EST`). **If T-Motor gives no lead time by 4 Dec, buy all 5 in Order 1**: the stock risk outranks the $155.12 exposure if A is reversed (3 x 46.90 x 1.1025).
4. Order 1 limited to bench parts, concept-neutral avionics / power and the stock-risk lines (COST-SCHEDULE s2, minus R04).

### 7.2 Pre-main-order work list (priority order)

| # | Work | Owner | Cost | Due |
|---|---|---|---|---|
| 1 | One-truth fold-in: s1 item 10 list, elevon geometry (y 0.04-0.34, +-20 deg), cruise rpm 7,300-7,600, leg 150 m, D-185 / D-186 as ruled here | A1 | $0 | 1 Dec |
| 2 | CAD pack move + tray slot (s4); **SITL re-run on the as-drawn aircraft** (CAD CG, elevons, inertias, prop plane): transition, back-transition at 0 / 45 / 90 deg wind, cruise trim, roll rate, weathervane in turbulence, fence during QLAND | A5 / F4 / B3 | $0 | 11 Dec |
| 3 | Bench M1-M4 (s8) | H1 / E1 | Order 1 | 17 Dec |
| 4 | Flutter / divergence estimate with the torsion coupon (s5) | C1 / C2 | ~$5 foam `EST` | 18 Dec |
| 5 | Schedule: written 4-mornings booking plan, landing-campaign merge decision, R4 revised (below) | I2 / team | $0 | 18 Dec |

### 7.3 Go / no-go for the main order (all must hold; a miss names the action)

| # | Line | Fail action |
|---|---|---|
| G1 | Measured thrust (M1) gives, in `mission_gate_a.py`, T/W sag >= 1.6 capped at 1.50 kg **and** capped transition window >= +-5 % at 1.44 kg | R3: resize once (prop / pack); second failure, B |
| G2 | One motor at 90 % <= 13 A; 180 s hold, can <= 80 C | R3 |
| G3 | Yaw authority >= 0.35 N m at cant 16, arm 0.228 (diagonal pair x 2 or four motors) | 0.30-0.35: go with the 4 m/s card and 5 booked mornings/wk; < 0.30: R2 |
| G4 | Hover <= 57.2 W per motor at 402 gf (`bench_analysis.py` line) | recompute energy; < 1.08x at the gate is a board re-sit |
| G5 | As-drawn SITL (7.2 #2) passes the SITL-FLIGHT lines (pitch use <= 0.60, no cap > 1 s into wind, 1.3 Vs in 15 s) and roll >= 90 deg/s within +-20 deg | fix CG / elevon geometry before the wing is cut |
| G6 | CAD CG 20-26 mm after the pack move; predicted mass <= 1.44 kg; structure <= 473 g | board re-sits |
| G7 | `bom_a.py` incl. bench lines: +30 % margin >= $100 **and** total <= $1,800 | board re-sits (replaces R5) |
| G8 | Flutter / divergence >= 1.2 VD, or VD lowered with THR_MAX to match | change spar / elevon mass balance before the cut |
| G9 | Written booking plan >= 4 RFS mornings/wk from 8 Feb; main order placed by 28 Dec, shipped before 21 Dec | no main order on A without it |

### Conditions C1-C8 (QP-1), status

| # | Status | Note |
|---|---|---|
| C1 | open | now the 0.35 N m hanging yaw line (G3) |
| C2 | met in SITL, open in the field | heading rule now automated by `Q_WVANE_ENABLE` 3 |
| C3 | met on the `EST` model; re-run on the as-drawn aircraft | post-stall moment unmeasured; first transition from 50 m with pre-climb |
| C4 | SM >= 5 % met (10.0 %); band failed | s4 |
| C5 | met | 1,392 g CAD predicted |
| C6 | **not met** | s1 item 10; 7.2 #1 |
| C7 | **re-stated**: a static bench cannot pick a cruise prop | cruise duty and rpm logged on the first cruise (M8); a higher-pitch prop only if 17 m/s needs > 0.65 duty fresh |
| C8 | replaced by D-185 (fin is now a tube, f1 432-525 Hz) | tap test at build |

### Reversal triggers, revised

R1, R2, R3 unchanged (R2's yaw line is now < 0.30 N m). **R4: tethered hover by 18 Feb** (SCHEDULE-A latest-safe; 15 Feb fired before A was late) and D2 is funded from the crash reserve, so R4 has no lifeboat once the reserve is spent. **R5: replaced by G7.**

## 8. What the team must measure

- **M1** Thrust, current, rpm of MN2212 + APC 9x4.5MR on the stand, 4S fresh and sag. Fails G1 if the capped window at 1.44 kg falls below +-5 %.
- **M2** 180 s hold at 90 %: current <= 13 A, can <= 80 C (IR thermometer). Fails A-P16.
- **M3** Hanging yaw on one diagonal pair at cant 16, arm 0.228 m, +-0.10 throttle; double it. Below 0.30 N m fails A-P7 and fires R2.
- **M4** Bidirectional DShot rpm read on the Kakute from the SpeedyBee (one channel). Absent: notch by throttle, A-P17 re-stated.
- **M5** Elevon free play with the servo powered (dial or ruler at the trailing edge) and the wing-section torsion coupon (hang a weight on a 0.3 m arm, read twist). Feeds G8.
- **M6** CG on a knife edge with the pack in the slotted tray. Outside 20-26 mm fails A-P4.
- **M7** Tap test of the built cage (8-15 Hz, phone accelerometer) and wing (90-120, 215-261 Hz). Outside +-20 % of FE: re-run `fu_cage.py`, re-tune.
- **M8** First cruise: duty and rpm (audio FFT) at 17 m/s. Above 0.65 duty fresh fails the THR_MAX 68 basis.
- **M9** Tethered hover in light turbulence with `Q_WVANE` 3: heading excursion > 15 deg fails the 5 m/s card.

## Open decision cards

**D-J6-3 Accept the slimmer cost margin, or cut?** Facts: +30 % margin ~$123 against $100; growth absorbed 18 %. Recommended: accept, freeze the BOM (every new line needs an offsetting cut) and replace R5 with G7. Alternative: cut G05 now and borrow an anemometer (+$27.56 margin, $25 x 1.1025). Evidence s1 item 1.

**D-J6-4 Merge the landing campaign into hover sorties?** Facts: 4 booked mornings/wk give 11 d slack; one crash plus the 4 m/s fallback gives -5 d. Recommended: A1/A2 merge the 20 touchdowns into F02 / F05 sorties and book 4 mornings with 5 as the yaw-fallback plan. Alternative: keep the campaign and commit to 5 mornings from 8 Feb. Evidence s2 schedule, s5.
