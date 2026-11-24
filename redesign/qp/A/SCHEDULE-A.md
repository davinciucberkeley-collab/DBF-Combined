# Concept A schedule, 2026-11-15 to 30 April 2027 (I2)

Status `PROPOSED`. Nothing ordered. **AM-037 (2026-11-23): no fabrication before Jacobs reopens (19 Jan 2027, assumed); the current plan is the AM-037 section below, go/no-go Fri 29 Jan 2027, slack +2 d; the Timeline / Slack / Critical-path sections after it are the superseded record.** Dates are computed or `EST`. Flight-programme dates: `python -I redesign/qp/A/schedule_a.py`. Structure and facts follow `team/I2/SCHEDULE.md` (K09-L, I2-R2) and `team/H2/FLIGHT-TEST-PLAN.md`; cost side in `review/QP-3/COST-SCHEDULE.md`.

## Basis

| Input | Value | Source |
|---|---|---|
| Order 1 | Tue 1 Dec - Fri 4 Dec 2026 | user |
| Fall instruction and Jacobs access end | 18 Dec; spring instruction starts 19 Jan; recess 22-26 Mar | `team/I2/SCHEDULE.md` (third-party calendar, not confirmed); Jacobs closed 19 Dec - 18 Jan assumed |
| Soldering | Electronics Lab only (Jacobs), so open only until 18 Dec and from 19 Jan | `team/I2/SCHEDULE.md` |
| RFS | request >= 7 business days ahead, 07:00-10:00 flights, mean wind <= 5 m/s, gust <= 8 m/s; A heading rule: edge-on, belly-on only <= 3 m/s | H2 plan s1; `A-P8/P8a` |
| Flyable fraction of booked mornings | **0.72** (low end of 72-81 %, `config-study/tiebreak/DECISION.md` l.175, a K09-L basis); 0.60 as a sensitivity. RFS itself unmeasured (0 of 3, `team/H3/WIND-RFS.md`); February not measured | |
| Flight mornings | F01 2, F02 5, F03 4, F04 3, F05 5, F06 3 = 22 (K09-L numbers, H2 s6; two sorties per morning, two packs) | H2 plan |
| Build hours | K09-L stages 2-10 = 82 h (`team/G4/BUILD-STEPS.md` s2) scaled **x0.65** to A (a smaller wing, no pod; `EST`, range 0.5-0.8): **53 h** (41-66), of which 8.5 h before first cut (power stack, flash, feet); checks 10 h; range check 2 h; 6 serial 24 h cures (K09-L 8) | `EST` |
| Team hours | exam weeks 7-18 Dec 8 h/wk; winter break 16 h/wk (two people, no Jacobs); spring 20-22 h/wk | `EST` |
| Lead times | RMRC / SparkFun 5-7 d (K09-L ORDER-PLAN 5 d, +2 for December); SunnySky X2216 V3 from RMRC: RMRC backorder to Nov 2026, lead time after restock —, D-227 / D-228 (the earlier T-Motor express 5-10 d no longer applies); Prusa 7 d; Rock West >= 4 weeks (page) | `EST` unless noted |

## AM-037 re-plan (2026-11-23, T-103, CHANGE-LOG D-248): no fabrication before Jacobs reopens; this section replaces the Timeline, Slack and Critical-path sections below (kept as the pre-AM-037 record)

User constraint AM-037 (verbatim, `docs/spec-amendments.md`): "Realistically, we will not be doing any fabrication work until after winter break, we will likely start making orders though during early december". Reading used here: purchasing, SITL, compliance, measuring and software work may run in December and over the break; every step that builds, prints, solders, cuts or needs the thrust stand or a soldered power stack waits for Jacobs. Dates are computed by `python -I redesign/qp/A/schedule_a.py` or `EST`. Full working: `docs/audits/2026-11-23-T103-replan.md`.

### Dates and sources

| Input | Value | Source |
|---|---|---|
| Spring instruction begins | **Tue 19 Jan 2027**; Mon 18 Jan and Mon 15 Feb holidays; spring recess Mon 22 - Thu 25 Mar (Fri 26 Mar holiday) | UC Berkeley Registrar, `registrar.berkeley.edu/wp-content/uploads/UCB_AcademicCalendar_2026-27_a11y.pdf`, read 2026-11-23 (this replaces the earlier third-party calendar) |
| Jacobs last fall access day | Fri 18 Dec 2026 | `jacobsinstitute.berkeley.edu/making-at-jacobs/`, read 2026-11-23 |
| Jacobs spring reopening date | **not published** on that page; assumed = 19 Jan 2027 (`ASSUMED`; confirm with Jacobs staff before 15 Jan) | same page: no spring date listed |
| Hands-on tool trainings | "only available in the first half of each semester" (fall: 31 Aug - 23 Oct); spring window opens with the term, dates not published; a ShopBot / printer / electronics training missing on 19 Jan costs days (not modelled, "-") | same page |
| Team hours | spring 21 h/wk (middle of 20-22, `EST`); winter break 16 h/wk but none of it may be fabrication | SCHEDULE-A Basis |
| Hours before first hover | bench stand + prints + solder + campaign 12 h (`EST`, no source) + pre-cut power stack 8.5 h + first cut 30 h + B2 14.5 h + checks 12 h = **77 h** (`EST`; 53 h build scaling x0.65 is the old basis) | `schedule_a.py` HOURS |

### Timeline (baseline, AM-037)

| ID | Task | Dates | Critical | Fabrication? |
|---|---|---|---|---|
| M1 | Compliance (TRUST, UC drone program, FAA, AMA) | by 30 Nov | no | no |
| O1 | Order 1 (`ORDER-1.csv`, $887.25 EST, the TP-1 / TP-2 kit, X2216 motors first: RMRC backorder) | 1-4 Dec (approval) | **yes** (motor lead time "-") | no |
| O1b | Order 1b: config-independent main lines + R15 rib tube (see split below) | 1-11 Dec (with or just after O1) | no | no |
| O2 | Parts arrive; incoming weigh-in against the mass table (scale G02) | 7-22 Dec EST | no | no |
| S1 | >= 10 h SITL on A with the Pocket TX (A-D9) | 9 Dec - 15 Jan | no | no |
| WN1 | RFS anemometer mornings x 3 (R-WIND-MEASURE; G05 $12.99 is in Order 1b) | 21 Dec - 15 Jan | no | no |
| FC0 | Optional, fabrication-free: H743-Wing firmware, `A.param` load, Lua script load check, ELRS bind, on USB power, 2 people, about 6 h `EST`. The cap-versus-voltage reading (TP-2) needs the soldered power input, so it stays in the bench week | 28 Dec - 15 Jan | no (saves unknown hours, not credited) | no |
| - | Winter break, Jacobs closed (18 Dec - 18 Jan): **no printing, soldering, cutting, stand building** | 19 Dec - 18 Jan | | none |
| B0 | Bench stand build, PETG prints, power stack solder, flash at Jacobs | Tue 19 - Fri 22 Jan | **yes** | yes |
| TP | TP-1 (derate, current) and TP-2 (Lua cap, 72 A limiter) | Mon 25 - Thu 28 Jan | **yes** | yes (stand) |
| D1 | **Bench decision = go / no-go: Fri 29 Jan 2027** (one date; replaces 15 Dec and 18 Dec) | 29 Jan | **yes** | no |
| O3 | Order 2: the config-dependent lines still unbought ($113.28 EST in Option B+) | Fri 29 Jan, arrives about 5 Feb EST | no (needed by about 11 Feb) | no |
| B1 | First cut: wing cores, spar, fin parts (ShopBot assumed D-203; hours-limited, in parallel with TP days) | 26 Jan - 5 Feb | **yes** | yes |
| B2 | Skin, harness, servos, linkage, motors | 5-10 Feb | **yes** | yes |
| B3 | Checks: weigh-in, CG, motor test, range check, TP-10b tap test | 10-15 Feb | **yes** | yes |
| F01 | First tethered hover | **Tue 16 Feb** (15 Feb holiday) - 21 Feb | **yes** | |
| F02 | Free hover, landing practice | 21 Feb - 5 Mar | **yes** | |
| F03 | Fixed-wing tune | 5-15 Mar | **yes** | |
| F04 | First transition, back-transition | 15-22 Mar | **yes** | |
| CR1 | Crash-repair loop (one) | 22 Mar - 2 Apr | **yes** | yes |
| F04b | F04 repeated | 2-9 Apr | **yes** | |
| F05 | Round trips, landing practice | 9-21 Apr | **yes** | |
| F06 | Full mission flights | 21-28 Apr | **yes** | |
| END | Deadline | 30 Apr | | **slack +2 d (baseline)** |

### Order split (December versus after the bench decision)

Lines from `BOM-A.csv` and `ORDER-1.csv`, prices include 10.25 % tax, shipping per `bom_a.py` (RMRC / Amazon / Local $0 in the model, real RMRC rate "-"; splitting adds $0 in the model). "At risk" = worst case with nothing returned (return policies not read, "-"). Case (i) = TP-1 / TP-2 fails and the prop / motor choice is reopened (AM-016): only the size-sensitive lines are lost. Case (ii) = the reopen ends in fallback concept B: the airframe and mechanism lines bought are lost too (the electronics, charger, test gear and printed-part PETG are reused).

| Option | Bought 1-11 Dec | Bought after 29 Jan | At risk (i) / (ii) | F01 start, slack |
|---|---|---|---|---|
| A: Order 1 only | $887.25 | $704.98 (incl. $5 FAA) | $283.34 / $283.34 | 24 Feb, **-5 d** (the main order's 7 d lead starts at the decision) |
| B: Order 1 + config-independent main lines | $1,398.72 | $193.50 | $283.34 / $593.20 | 16 Feb, **+2 d** |
| **B+ (adopted): B + R15 rib tube (no stock shown, T-088)** | **$1,478.94** | **$113.29** | **$338.56 + $25.00 R15 shipping / $648.42 + $25.00** | **16 Feb, +2 d** |
| C: everything in December | $1,592.23 | $0 | $440.86 + $30.99 shipping / $750.72 + $30.99 | 16 Feb, +2 d |

Why B+: A lowers the case-(ii) exposure by $365 against B+ but costs 8 days of F01 start and turns the baseline slack negative; December buys of the config-independent lines (foam, spar and fin tubes, servos, glass, epoxy, pad foams, pitot, tools) are the only way to start cutting on 19 Jan. The size-sensitive lines ($102.29 left for the end of January: 6061 hub bars T1 / T11 with the TP-4 coupons, 8x6 strut tube R10, 3 mm pin rod R14, strut offcut R06) are $113 and arrive by 5 Feb, about 5 days before they are needed. R15 is bought early only because its stock and lead time are the largest supply uncertainty (T-088); motors are already in Order 1. Total never exceeds the BOM $1,939.17 (A + B + C are timings of the same lines; the reserve $346.94 is not a purchase).

### Slack and sensitivities (`schedule_a.py`, F01 start 16 Feb, END 30 Apr)

| Case | F06 ends | Slack |
|---|---|---|
| Baseline: 4 mornings, p 0.72, one crash | 28 Apr | **+2 d** (was +11 d on 8 Feb) |
| p 0.60 | 13 May | **-13 d** |
| 3 mornings a week | 16 May | **-16 d** |
| No crash | 8 Apr | +22 d |
| Hours x1.25 (96 h) | 2 May | -2 d |
| Option A (main order waits for the bench) | 5 May | -5 d |

Negative cases, $0 options (each EST, none applied without the team): (1) **5 booked mornings a week** from 16 Feb: +12 d at p 0.72, +3 d at p 0.60 (the same lever the 2026-11-15 update proposed); (2) **more build hours in the reopening weeks**: 28 team-h/wk (all four people) moves F01 to 7 Feb, +12 d; (3) **run B1 wing cuts and the TP-1 / TP-2 stand work as parallel pairs** with four people (already inside the 28 h/wk case); (4) **fabrication-free prep over the break** (FC0, incoming weigh-in, WN1, SITL) removes hours from the 77 h, unmeasured, not credited; (5) **scope**: F06 (3 mornings) is the last gate and the one to drop first, giving back about 7 d at 4 a week; (6) shorten the crash loop (11 d) by pre-cutting a spare elevon and fin panel in the build, which needs foam already bought (Option B+).
Latest-safe F01 start (4 mornings, p 0.72, one crash): **18 Feb**; planned 16 Feb, so a 2-day slip anywhere before F01 ends the margin. Jacobs reopening later than 19 Jan, a missing hands-on training, or an X2216 arrival after 22 Dec moves F01 day for day.

**Risk: B1 (first cut of the wing cores, from 26 Jan) starts before D1 (go / no-go, 29 Jan).** A failed bench test at D1 reopens the configuration (AM-016: bigger props or motors, or concept B), and wing cores cut on 26-28 Jan for the 0.90 m wing could be wasted. Cost of that waste: core foam and 3 days of ShopBot hours, not priced here ("-"). Options, none applied without the team: (1) hold the first cut to 29 Jan, after D1 (the F01 date moves by the 3 days, slack effect not computed with `schedule_a.py` here; the baseline slack is +2 d, so it would be about -1 d, EST); (2) start B1 with the size-independent parts (spar, fin parts) and cut the wing cores only after D1; (3) accept the risk and cut on 26 Jan (bench TP-1 / TP-2 run 19-28 Jan, so the result is often known by the cut; EST). Choosing is a team decision.

### What this changes elsewhere

Go / no-go and bench decision: **29 Jan 2027** (was 15 Dec; the 28 Dec latest-safe main-order date and the 18 Dec D1 no longer apply). T-099 F-6 is answered by AM-037. The bench steps TP-1 / TP-2, TP-15 .. TP-18 (stand parts) all run after 19 Jan. `TEST-PLAN-O4B.md` was aligned to 29 Jan in fix pass C (review round 13; it printed 15 Dec before).

## Record (superseded by the AM-037 section above): Timeline, Slack and Critical path as of 2026-11-15 to 2026-11-22

## Timeline (record, pre-AM-037)

| ID | Task | Dates | Critical | Notes |
|---|---|---|---|---|
| O1 | Order 1 (`ORDER-1.csv`, rebuilt T-090 2026-11-22 from `BOM-A.csv`; **$887.25** incl. 10.25 % tax and $10.71 RDQ shipping EST, 21 lines, plan only, nothing bought): the TP-1 / TP-2 bench kit (4 SunnySky X2216 V3 880KV, APC 9x4.5MR, SpeedyBee ESC, 2 RDQ 2,800 mAh packs, H743-Wing, TX/RX, WM150, load cell and stand lines, XT90 / wire), plus stock-risk lines (motors BACKORDER to Nov 2026, GPS). No tubes, servos, foam or anemometer. Order 1 + main order ($1,051.92) = BOM total $1,939.17. History: the earlier MN2212 plan ($967.90 / $1,123.02) is withdrawn. | 1-4 Dec | no (14 d slack) | `mechanism/out/T090_report.md` |
| O2 | Order 1 arrives | 7-15 Dec | no | X2216 motors the latest (RMRC backorder, D-228) |
| M1 | Compliance (TRUST, UC drone program, FAA, AMA) | 16-30 Nov | no | before any RFS request |
| S1 | >= 10 h SITL on A with the Pocket TX (A-D9) | 9 Dec - 15 Jan | no (slack 30 d) | break is the pilot-training window |
| B0 | Bench stand build (Jacobs, print fixture), thrust and yaw-hang campaign, `bench_analysis.py` | 10-17 Dec | **yes** | needs the 0.35 N m yaw result |
| EL1 | Power stack solder, flash, motor map at Jacobs EL | 14-18 Dec | no, but Jacobs shuts 18 Dec | slip costs about 1 week after 19 Jan, inside slack |
| PR1 | Print cage, mounts, pads (PETG, Jacobs) | 14-18 Dec | no | if missed, print 19-26 Jan |
| D1 | Bench decision, main order placed (4 X2216 motors, local foam and epoxy, Amazon lines) | Fri 18 Dec | **yes** | latest-safe 28 Dec; ship before 21 Dec |
| WN1 | RFS anemometer mornings x 3 (R-WIND-MEASURE) | 21 Dec - 15 Jan | no | RFS request 7 business days ahead |
| O3 | Main order arrives | by Tue 5 Jan (18 d incl. holidays) | **yes** | |
| B1 | First cut: wing core halves and fin fairings on the Jacobs ShopBot (D-203, assumed; backup: hot wire at workspace W), spar, fin laminates at W | 6-18 Jan, about 30 h | **yes** | needs W named by 30 Nov |
| B2 | Skin, harness (soldering at Jacobs EL), servos, linkage, motors | 19-29 Jan, about 14.5 h | **yes** | cures in series |
| B3 | Checks: weigh-in, CG, motor test, range check | 30 Jan - 5 Feb, 12 h | **yes** | A-P mass 1.50 kg gate |
| F01 | First tethered hover | 8-13 Feb | **yes** | R4 trigger revised to 18 Feb (BOARD QP-3): 5 d spare |
| F02 | Free hover, landing practice | 13-25 Feb | **yes** | |
| F03 | Fixed-wing tune | 25 Feb - 7 Mar | **yes** | |
| F04 | First transition, back-transition | 7-14 Mar | **yes** | |
| CR1 | Crash-repair loop (one) | 14-25 Mar, 11 d | **yes** | K09-L loop 10.5 d |
| F04b | F04 repeated | 25-31 Mar | **yes** | recess 22-26 Mar books +1 morning |
| F05 | Round trips, landing practice | 31 Mar - 12 Apr | **yes** | |
| F06 | Full mission flights | 12-19 Apr | **yes** | |
| END | Deadline | 30 Apr | | **slack 11 d** (baseline) |

The first cut to first hover is 33 d (K09-L 33 d on 82 h; A is smaller but the cures and the Jacobs closure are the same).

## Slack and latest-safe dates (record, pre-AM-037)

Baseline = 4 booked mornings per week, p 0.72, one crash loop (`schedule_a.py`):

| Item | Plan | Latest-safe | Slack |
|---|---|---|---|
| F01 start | 8 Feb | **18 Feb** | 10 d |
| First cut | 6 Jan | 16 Jan | 10 d |
| Main order | 18 Dec | **28 Dec** (do not ship after 21 Dec) | 10 d |
| Bench decision | 18 Dec | 28 Dec | 10 d |
| Order 1 (if the main order waits for the bench) | 1-4 Dec | 15 Dec | 11-14 d |
| F06 end | 19 Apr | 30 Apr | 11 d |

Slack is one chain: a day lost anywhere before F01 is a day off the 11 d. Latest-safe F01 start by flight-rate scenario (crash = one loop; `schedule_a.py` table):

| Booked mornings/wk | p | no crash | one crash |
|---|---|---|---|
| 3 | 0.72 | 19 Feb (slack +13 d from 8 Feb) | **fails**: F06 10 May, -10 d; latest 29 Jan |
| 3 | 0.60 | 4 Feb (-2 d) | fails, -25 d |
| 4 | 0.72 | 10 Mar (+29 d) | 18 Feb (+11 d) |
| 4 | 0.60 | 24 Feb (+17 d) | fails, -5 d |
| 5 | 0.72 / 0.60 | 19 / 10 Mar | 1 Mar / 19 Feb (+22 / +12 d) |
| 2 | 0.72 | fails, -26 d | fails, -52 d |

## Critical path (record, pre-AM-037)

Order 1 (1-4 Dec) -> arrival -> bench B0 -> bench decision and main order (18 Dec) -> arrival (5 Jan) -> first cut (6 Jan) -> B1, B2, B3 -> F01 (8 Feb) -> F02 -> F03 -> F04 -> CR1 -> F04b -> F05 -> F06 -> 30 Apr. The path from F01 on is rate-limited by the number of flyable RFS mornings, not by work content: 25 flown mornings (22 plus 3 repeated) at 4 x 0.72 = 2.9 a week is 8.7 weeks.

Near-critical: SunnySky X2216 motors (RMRC backorder, no restock lead time known, D-228); Jacobs closure on 18 Dec (EL1 and PR1); ShopBot access for foam (assumed, D-203) and workspace W.

## Needed from the team

1. Commit to **4 booked RFS mornings a week from 8 Feb** (request in blocks, 7 business days ahead) with at least three of the four people on each; at 3 a week one crash ends the programme after the deadline.
2. Name workspace W by 30 Nov (glue, cures, and the backup hot wire). Ask Jacobs by 30 Nov that XPS may go on the ShopBot (D-203).
3. Fin skin decided: no CFRP sheet; 16x14 tube + 3 mm XPS fairing + tape (STRUCTURES iter. 2). Risk R04 retired.
4. Measure RFS wind on 3 mornings before 15 Jan (anemometer G05 is not in Order 1: borrow one, or buy it with the main order; D-J6-3 cut candidate).

## Open

All durations after 5 Jan are `EST` and replaced by measured hours after the first foam core. The crash loop is one loop after F04, as K09-L; a second one needs another 11 d plus 3 mornings and is not covered at 4 a week. Flight mornings are modelled by week, not by weekday.

## Update 2026-11-15 (CLAIMS-FIX D-192): hover wind limit 4 m/s mean, gust 6.4 m/s

The RFS criterion in the table above (5 / 8 m/s) is replaced by 4 / 6.4 m/s for all hover (A-P8; SITL peak motor output at the 1.47 kg gate, review/QP-4/CLAIMS-FIX.md s3). Effect, two bounds, both `EST`: (a) WIND.md s3 block method (RCMC1 2022-2025): usable mornings Jan-Apr 0.80 -> 0.64, the February blocks F01 / F02 are short, **+1.4 d average year, +8.4 d worst year**, against the 11 d slack of the baseline here (9.6 d / 2.6 d left); (b) scaling p by 0.64 / 0.80 gives p about 0.58, the 0.60 row above: 4 booked mornings a week with one crash ends **-5 d** past 30 Apr, 5 booked mornings a week +12 d. Mitigation to take at the Feb booking: 5 booked mornings a week for F01-F02, or allow 5 m/s for hover-only gates F01-F02 on packs that land above 3.90 V per cell at rest (about 55 %: SITL fresh-pack peak 0.79 at 5 m/s, CLAIMS-FIX s3), which removes the WIND.md shortfall (only F01 / F02 are short at 4 m/s). Not applied; board call.

## Update 2026-11-22 (T-084..T-087, D-233..D-236; review round 3 fix M-D)

State carried from the reports (EST; `schedule_a.py` NOT re-run for this update, so no slack figure above is recomputed: "—"): tallied mass 1.8796 kg, CG 23.13 mm, SM 7.17 %, window +11.88 %, T/W 2.632 / 2.111, cruise 234 s, A-P6 FAIL carried (TP-11, stall test after the build), tip-over A-P9 31.00 deg with FIN_H 0.1937 m (`T084_report.md`); BOM $1,939.17, margin +$60.83 (D-234, D-235, `T086_report.md`, `T087_report.md`); D-185 (a) carried FAIL on the model, decided by TP-10b (D-236, `T085_report.md`).

Schedule effects: (1) the TP-10b T-A-TAP tap test (TEST-PLAN-O4B, 0.5 day, 2 people, team lab or Jacobs) sits between B3 (checks) and F01 (first tethered hover); it does not gate the go/no-go (29 Jan 2027; was 2026-12-15 when D-236 was written). It adds up to 0.5 d to the B3-F01 gap against the 10 d F01 slack above (EST). (2) If TP-10b finds a strong in-band mode, the D-233 option C trade (best lever: 10x8 arms, 4 of 6 cases, about -11 g, tube price "—") needs a tube purchase, lead time "—" and a rebuild of 4 arms: not scheduled here, "—". (3) R15 (rib tube, Carbonwebshop, EU) was kept (T-087); its stock and lead time are "—" and remain the largest supply uncertainty. (4) The Order 1 and O1 lines above are the MN2212 plan; the current purchase plan is the budget-closed list in TEST-PLAN-O4B and `BOM-A.csv`.
