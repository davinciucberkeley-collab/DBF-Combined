# Concept A schedule, 2026-11-15 to 30 April 2027 (I2)

Status `PROPOSED`. Nothing ordered. Dates are computed or `EST`. Flight-programme dates: `python -I redesign/qp/A/schedule_a.py`. Structure and facts follow `team/I2/SCHEDULE.md` (K09-L, I2-R2) and `team/H2/FLIGHT-TEST-PLAN.md`; cost side in `review/QP-3/COST-SCHEDULE.md`.

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
| Lead times | RMRC / SparkFun 5-7 d (K09-L ORDER-PLAN 5 d, +2 for December); T-Motor express 5-10 d (page gives none); Prusa 7 d; Rock West >= 4 weeks (page) | `EST` unless noted |

## Timeline (baseline)

| ID | Task | Dates | Critical | Notes |
|---|---|---|---|---|
| O1 | Order 1 (`ORDER-1.csv`, $967.90 with 2 motors; $1,123.02 if all 5): bench parts, concept-neutral avionics / power, stock-risk lines (props, GPS, PETG, ESC, FC). No CFRP (R04 removed), no tubes, servos, foam or anemometer. T-Motor asked for stock and lead time; no answer by 4 Dec = buy all 5 motors | 1-4 Dec | no (14 d slack) | BOARD QP-3 s7.1; FOLDIN.md s4 |
| O2 | Order 1 arrives | 7-15 Dec | no | T-Motor the latest |
| M1 | Compliance (TRUST, UC drone program, FAA, AMA) | 16-30 Nov | no | before any RFS request |
| S1 | >= 10 h SITL on A with the Pocket TX (A-D9) | 9 Dec - 15 Jan | no (slack 30 d) | break is the pilot-training window |
| B0 | Bench stand build (Jacobs, print fixture), thrust and yaw-hang campaign, `bench_analysis.py` | 10-17 Dec | **yes** | needs the 0.35 N m yaw result |
| EL1 | Power stack solder, flash, motor map at Jacobs EL | 14-18 Dec | no, but Jacobs shuts 18 Dec | slip costs about 1 week after 19 Jan, inside slack |
| PR1 | Print cage, mounts, pads (PETG, Jacobs) | 14-18 Dec | no | if missed, print 19-26 Jan |
| D1 | Bench decision, main order placed (3 motors, local foam and epoxy, Amazon lines) | Fri 18 Dec | **yes** | latest-safe 28 Dec; ship before 21 Dec |
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

## Slack and latest-safe dates

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

## Critical path

Order 1 (1-4 Dec) -> arrival -> bench B0 -> bench decision and main order (18 Dec) -> arrival (5 Jan) -> first cut (6 Jan) -> B1, B2, B3 -> F01 (8 Feb) -> F02 -> F03 -> F04 -> CR1 -> F04b -> F05 -> F06 -> 30 Apr. The path from F01 on is rate-limited by the number of flyable RFS mornings, not by work content: 25 flown mornings (22 plus 3 repeated) at 4 x 0.72 = 2.9 a week is 8.7 weeks.

Near-critical: T-Motor motors (no lead time on the page); Jacobs closure on 18 Dec (EL1 and PR1); ShopBot access for foam (assumed, D-203) and workspace W.

## Needed from the team

1. Commit to **4 booked RFS mornings a week from 8 Feb** (request in blocks, 7 business days ahead) with at least three of the four people on each; at 3 a week one crash ends the programme after the deadline.
2. Name workspace W by 30 Nov (glue, cures, and the backup hot wire). Ask Jacobs by 30 Nov that XPS may go on the ShopBot (D-203).
3. Fin skin decided: no CFRP sheet; 16x14 tube + 3 mm XPS fairing + tape (STRUCTURES iter. 2). Risk R04 retired.
4. Measure RFS wind on 3 mornings before 15 Jan (anemometer G05 is not in Order 1: borrow one, or buy it with the main order; D-J6-3 cut candidate).

## Open

All durations after 5 Jan are `EST` and replaced by measured hours after the first foam core. The crash loop is one loop after F04, as K09-L; a second one needs another 11 d plus 3 mornings and is not covered at 4 a week. Flight mornings are modelled by week, not by weekday.

## Update 2026-11-15 (CLAIMS-FIX D-192): hover wind limit 4 m/s mean, gust 6.4 m/s

The RFS criterion in the table above (5 / 8 m/s) is replaced by 4 / 6.4 m/s for all hover (A-P8; SITL peak motor output at the 1.47 kg gate, review/QP-4/CLAIMS-FIX.md s3). Effect, two bounds, both `EST`: (a) WIND.md s3 block method (RCMC1 2022-2025): usable mornings Jan-Apr 0.80 -> 0.64, the February blocks F01 / F02 are short, **+1.4 d average year, +8.4 d worst year**, against the 11 d slack of the baseline here (9.6 d / 2.6 d left); (b) scaling p by 0.64 / 0.80 gives p about 0.58, the 0.60 row above: 4 booked mornings a week with one crash ends **-5 d** past 30 Apr, 5 booked mornings a week +12 d. Mitigation to take at the Feb booking: 5 booked mornings a week for F01-F02, or allow 5 m/s for hover-only gates F01-F02 on packs that land above 3.90 V per cell at rest (about 55 %: SITL fresh-pack peak 0.79 at 5 m/s, CLAIMS-FIX s3), which removes the WIND.md shortfall (only F01 / F02 are short at 4 m/s). Not applied; board call.
