# QP-3 I1 + I2 close-out, concept A (cost re-check and schedule), 2026-11-15

Reproduce: `python -I redesign/qp/A/bom_a.py` and `python -I redesign/qp/A/schedule_a.py`. Files edited: `qp/A/BOM-A.csv`, `qp/A/bench/ORDER-LIST.csv` (new column `recheck_2026-11-15`), new `qp/A/schedule_a.py`, `qp/A/SCHEDULE-A.md`. Nothing bought; no git. Labels: `V` vendor page read today, `EST` estimate. Prices read with WebFetch 2026-11-15; pages that returned 403 / 429 / 503 are named as not read.

## 1. I1: BOM re-check

The `V` lines at RMRC, T-Motor (P01) and the SparkFun pages were re-read: price unchanged on every one, and every RMRC line shows In Stock except the one below. Not re-read today: W04 Harbor Freight, R03 Prusa product page (unchanged from 2026-11-14).

| Line | Result 2026-11-15 | Action |
|---|---|---|
| V04 GPS | Foxeer M10Q-250 at RMRC **$20.68 BACKORDER** ("Notify me when this is in stock"). GetFPV $25.99, RaceDayQuads $23.99, Pyrodrone out of stock (search snippets; GetFPV 403, RDQ 429: not read). Holybro Micro M10 backorder to Nov 2026 (snippet) | **Swapped to TBS M10Q, RMRC $19.76 In Stock, QMC5883 compass, 13.5 g** (https://www.readymaderc.com/products/details/86501-tbs-m10q-gps-receiver-with-glonass). Connector is not on the page: **confirm it mates the Kakute Wing Mini GPS port before ordering**. +1.5 g `EST` |
| W05 | now priced: 14 AWG red and black 1 m $1.99 each (read), XT60 5 pair $5.49 (RMRC wire-cables category page), heat-shrink kit $6.49 (read) = $23.92 | `V`; threadlocker split to W06 $6 `EST` |
| M02 | RMRC 10 pc pushrod and horn set **$8.99** In Stock (was $12 `EST`) | `V` |
| R05 / R07 | RMRC Mercury **15 min epoxy 8 oz $19.99 is Backorder**; thin CA $8.49 and gap-filling CA $5.49 In Stock (category page) | CA is now R07 `V` $13.98; **epoxy must be bought locally** (Home Depot 403, not read) |
| R04 CFRP 0.2 mm | **No US vendor found.** Rock West: 0.5 mm twill 300x300 about $32.99 (snippet); its configurator page says lead time is at least 4 weeks beyond stock and shows no price; DragonPlate minimum is 1/16 in; R&G (Germany) 0.2 mm out of stock | stays `EST` $40. **Highest cost-and-schedule risk**: 0.5 mm skins weigh 2.5x as much. Ask Rock West for a quote this week, or change the fin laminate (A1/C3 decision, not made here) |
| R01 foam | Home Depot 403. Snippets only: 1 in Foamular 150 4x8 about $26-32 elsewhere | stays `EST` $70 |
| R06, G03, G04 | not looked up (local / generic) | `EST` |
| G02 | SparkFun TAL220 10 kg $12.95 and HX711 $4.95 In stock (read); Amazon 503 | stays `EST` $50.95 |
| G05 (new) | H3 `R-WIND-MEASURE` needs an anemometer; no BOM line existed | added `EST` $25 (tie-break budget $20-30), may be borrowed |
| P01 | still $46.90, no stock figure, no lead time | stock UNKNOWN (section 2) |

### Totals (`bom_a.py`)

| | 2026-11-14 (D-184) | now |
|---|---|---|
| Goods | 1,168.52 | 1,193.49 |
| Spend (tax 122.33, shipping 47.13 `EST`, FAA 5) | 1,340.42 | 1,367.95 |
| Crash reserve | 311.42 | 311.42 |
| **Total** | 1,651.85 | **1,679.37** (R5 <= 1,750 PASS) |
| **Margin, verified prices, `EST` lines at nominal** | +348.15 | **+320.63** |
| Unverified lines | 9 | 9 (W06, R01, R04, R05, R06, G02, G03, G04, G05: 21 % of goods) |
| **Margin, remaining unverified lines +30 %** | +217.53 | **+196.94** (>= 100 PASS) |

Net: 3 lines became verified (W05, M02, V04 re-priced), 3 lines were added (G05 +$25, W06 +$6, R07 +$13.98). No subsystem is over its cap.

### Bench order list (`bench/ORDER-LIST.csv`, new column)

Read today: O2, O3, O4, O5, O6 (RMRC) and O9, O10 (SparkFun) In Stock at the listed prices; O1 has no stock figure. O11 and O12 (Amazon) returned 503 again; O13 and O14 not read. Findings:
- `order_total.py` "net $100.94" counts the RMRC and Amazon shipments twice (they are already in the BOM). Corrected extra over the BOM: uncovered bench goods 60.98 x 1.1025 + SparkFun shipping 8.00 = **$75.23**.
- O3 (2 x Holybro Tekko32, $49.55 with tax) is not in the BOM. With it, margin at +30 % = 196.94 - 75.23 - 10.6 (bump on O11/O14) - 49.55 = **$61.5, below the $100 line**. Without it: **$111.1, PASS**. **Drop O3** and bench the flight ESC (P04, one channel at a time).
- Drop O12 (the WM150, G01, covers it). O13 Arduino Nano is $13.70 at SparkFun (snippet; availability conflicting), not $8.

## 2. Stock risks for an order on 1-4 December 2026

| Risk | Evidence | Mitigation |
|---|---|---|
| T-Motor MN2212 (P01) | store page: no stock figure, no lead time; ships by international express (page: free at >= $200). The one part with no in-stock evidence | **order first**: 2 motors for the bench on 1 Dec (other 3 with the main order, one extra $10.71 shipment), or all 5 = $234.50 for free express (page text, not relied on) if the team accepts the cash earlier |
| CFRP 0.2 mm (R04) | no US source; >= 4 week lead for non-stock sizes | **order first or re-decide**: quote request this week, order by 4 Dec |
| GPS (V04) | Foxeer backordered, others out of stock | order the TBS M10Q on 1 Dec |
| APC 9x4.5MR 4-pack (P02) | predecessor T9545 sold out everywhere (D-183); one pack, no spare | order 1 Dec; a second pack ($10.36 with tax) is the cheapest insurance |
| SpeedyBee 35A 4-in-1 (P04), Kakute (V03), packs (W01) | In Stock today; single source each; no spare ESC board | order 1 Dec |
| Epoxy (R05) | RMRC 15 min kit backordered | local purchase |
| Prusament PETG (R03) | Prusa shipping not read | order 1 Dec; the cage must print at Jacobs before 18 Dec (SCHEDULE-A.md) |
| Holiday carriers | not measured | allow +3 days on anything shipped after 10 Dec |

Order first: P01 motors, R04 CFRP, R03 PETG, V04 GPS, P02 props, then the one RMRC order (all RMRC lines, $711 with tax + $15 `EST` shipping). Order 1 total about **$905** (45 % of the budget): RMRC $726, T-Motor 2 motors $114, Prusa $37, SparkFun $28.

## 3. I2: schedule (full text: `qp/A/SCHEDULE-A.md`)

| Milestone | Plan | Latest-safe (4 booked mornings/wk, p 0.72, one crash) |
|---|---|---|
| Order 1 placed | 1-4 Dec | 15 Dec (bench-gated main order) |
| Bench decision | 18 Dec (Jacobs closes) | 28 Dec |
| Main order placed | 18 Dec | **28 Dec**; ship before 21 Dec |
| First cut | 6 Jan | 16 Jan |
| First tethered hover | 8-13 Feb | **18 Feb** |
| Full mission (F06) | 19 Apr | 30 Apr; slack **11 d** |

**Critical path:** order, parts, first cut (6 Jan), build (33 d), first hover (8 Feb), then the weather-limited flight programme (20 flown mornings plus 3 repeated after the crash loop). The flight programme binds. With **3 booked mornings a week the plan fails by 10 d** (F06 10 May) when one crash happens, and with 2 it fails by 52 d. It needs **>= 4 booked RFS mornings per week from 8 Feb** (three to four team members present each morning), or the 20-touchdown landing campaign must be merged, which is an A1/A2 requirement change not made here. p = 0.60 (a wet February, unmeasured) turns 4 booked + crash into -5 d.

## 4. Open

RFS wind unmeasured (0 of 3 mornings, `team/H3/WIND-RFS.md`). The build-hours scale (0.65 of K09-L) is a guess until the cores are cut. Academic calendar is from a third-party page via `team/I2/SCHEDULE.md`: confirm with the Registrar. Jacobs closed 18 Dec to 19 Jan is assumed from the same file, not re-checked.
