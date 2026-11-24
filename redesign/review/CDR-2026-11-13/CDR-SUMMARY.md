# CDR 2026-11-13 — Chair summary (J6-chair)

Chair: J6-chair, Critical Design Review board. Branch `redesign/v1` at `3268e69`; this file is the only one written,
nothing committed. Inputs: the four board reports in this folder (`CDR-aero.md`, `CDR-structures.md`,
`CDR-electrical.md`, `CDR-build-and-test.md`), `STATUS.md`, `CONFIGURATION.md`. Paths are relative to `redesign/`.
Spot checks read `proofs/out/graph.json` (generated 2026-11-13 19:05 UTC), `team/I1/bom_summary.json`,
`team/I1/BOM.csv`, `team/I1/ORDER-PLAN.md` and `team/A2/REQUIREMENTS.md`; no generator was run. `CHAIR EST` marks
this file's own arithmetic; `EST` and `REVIEWER EST` are carried from the reports. Nothing is tested, so "passes"
means "passes on paper".

## 1. Verdicts

| Order | Verdict | In one line |
|---|---|---|
| (a) Early cart, ~20 Nov 2026 | **Go with conditions** | Buy it. It is the transferable electronics and test stock that every open question needs (`CONFIGURATION.md` de-risking item 5). Six conditions, all due by 19 Nov. |
| (b) Main order, 15 Dec 2026 | **Go with conditions; not releasable today** | No reviewer asks for a different configuration, motor count, wing or electrical architecture. Twelve conditions, dated 20 Nov – 13 Dec. If the twin has not completed a transition by 13 Dec, only the lines common to K09-L and K01-lean are ordered on 15 Dec (decision B5, needs the team's sign-off). |
| Build hold (after the order) | **No-go** for cutting flight half-fins or printing flight collars, shoes and mounts | Until CDR-01, -02, -03 and -13 close (`CDR-structures.md` verdict). |

All four reviewers returned go-with-conditions for 15 Dec. Finding counts: aero 3 blocker / 6 major / 5 minor;
structures 3 / 7 / 7; electrical 2 / 5 / 9; build and test 2 / 12 / 10 (each report's "Counts" line). After merging:
9 blocker, 16 major, 6 minor rows below.

### (a) Conditions on the early cart (all by Thu 19 Nov, order placed 20 Nov)

| # | Condition | Why | Source |
|---|---|---|---|
| A1 | Every `EARLY` line opened in a browser by a person and logged in `listing_log.csv`; `R01` carried at $84.49 until its page is read | 31 % of committed goods by value ($429.87 of $1 369.05) have a price read on a vendor page; 2 of 8 sampled links are dead | `CDR-build-and-test.md` CDR-BT-07, §4 |
| A2 | Pack source decided: US-stock 4S 6500 120C EC5 found, or A2 waives the "US stock, ground" clause of `R-BATT-HANDLING` in writing and I1 adds duty + brokerage $20–45 `EST` | the only listing found ships from Germany, 14 d | CDR-BT-06; `team/A2/REQUIREMENTS.md:116` |
| A3 | ESC line decided: one LANRC 4-pack if the listing is live on the day; if not, the board accepts the Tekko32 fallback knowing it is back-ordered to December and the twin then flies on borrowed or interim ESCs (—, team to name) | the ESC is unidentified (`B02`, ASIN unconfirmed, 503 on 2026-11-09) | CDR-EL-01; CDR-BT-07; `team/I1/ORDER-PLAN.md` early table |
| A4 | Coupon stock moved from the December order into this cart: `W05` PETG 1 kg ($23.14), `D02` CF strip 10 × 1 × 3 ($19.84), `C05` epoxy (re-priced from a page, CDR-BT-05) | the structures condition "coupons before the order" cannot be met otherwise: all three are `DEC` lines today | `team/I1/BOM.csv` `W05`, `D02`, `C05` (order column, read 2026-11-13); `CDR-structures.md` condition 2 |
| A5 | Test parts added: 2 × APC 11×7E + 2 × 11×7EP (about $20 `EST`), 35 V low-ESR caps (about $8 `EST`), second 16 AWG reel pair (about $14), anemometer ($20–30 `EST`); `M01` servos moved forward (same price, single-source stock); `A04` airspeed sensor (gated X08, $66.14) bought now | prop A/B, cap ripple, re-cut wire, card 1d wind, servo case measured before `MEC-008` prints; the twin's stall and neutral-point tests read airspeed (`CHAIR EST`: judgement, GPS ground speed in wind is not enough) | CDR-AE-08; CDR-EL-05, -16; CDR-BT-04, -22, -02 |
| A6 | Pilot and back-up named (17 Nov) and items 2–5 of the human list started | the cart exists to fly the twin 8–13 Dec; without a pilot and filings it cannot be flown | CDR-BT-01 |

Cost of A4–A5 against the reserve: A4 and `M01` move cash three weeks earlier and change no total. New spend is
about $62–72 `EST` (props 20 + caps 8 + wire 14 + anemometer 20–30) plus $66.14 if `A04` is taken out of its gate.
The early cart today is $1 093.85 with tax and shipping `EST` (`team/I1/ORDER-PLAN.md` totals table).

### (b) Conditions to release the 15 Dec order

| # | Condition | Closes | Latest | Set by |
|---|---|---|---|---|
| B-1 | Proof graph counts a violated limit of 0; fails re-triaged | CDR-03 | 20 Nov | chair |
| B-2 | Hours per student per week stated for 30 Nov – 18 Dec | CDR-22 | 20 Nov | CDR-BT-11 |
| B-3 | Five filings landed (PI sponsor, UC Drone Program, TRUST, FAA $5, liability answer) and the UC flight request for 8–13 Dec filed | CDR-06 | 24 Nov | CDR-BT-01 |
| B-4 | Side-load cap written into `params.json`; C5, C1, C4, C6 re-run on it; D-68 wing-pocket submodel run on C1-R5 loads | CDR-01, -13 | 27 Nov | chair |
| B-5 | `electrical.r_ext_mohm` re-based to 7.9 and E1 / E2 / B1 re-run; CG plan re-issued (static margin ≥ 6.5 % for first flights, `MIXING_GAIN` 0.65); A1's written rule for a partly passed twin gate | CDR-05, -14, -08 | 1 Dec | CDR-EL C4, CDR-AE C4, CDR-BT-04 |
| B-6 | Fin fix drawn (cheek extension + face doubler) and funded in mass; structures contingency line booked; CG re-run for both corners | CDR-01, -12 | 4 Dec | chair |
| B-7 | One station on the stand (GT-02): ≥ 1 330 gf fresh at the limiter and ≥ 1 060 gf at 11.9 V bus, with phase current logged | CDR-04 | 5 Dec | CDR-AE C1 |
| B-8 | One ESC identified, Bluejay flashed, bdshot error ≤ 1 % over a 0.7 m lead; ArduPlane 4.7.x and `K09L.param` loaded on the CoreWing, `features.txt` read; `BOARD-CHECK.md` steps 1–8 run and the power-board mount redrawn on the real hole pattern | CDR-09, -07, -17 | 8 Dec | CDR-EL C1–C3 |
| B-9 | BOM R5 issued: missing lines priced from pages, levers L1–L3 applied, both reserve lines shown ("at order" and "flight-ready"); crash-line decision B3 signed | CDR-10 | 8 Dec | chair |
| B-10 | Coupons read: `T-C4-TUBE-BEND` / `-TORSION`, `T-C6-LAP-PETG`, `T-C6-STRIP-ANCHOR` (printed tail vs tow lashing) | CDR-02 | 10 Dec | `CDR-structures.md` cond. 2; `STATUS.md` "by 10 Dec" |
| B-11 | ≥ 10 h SITL on the tailsitter frame incl. the S5 back-transition sweep; twin TW3 flown (hover yaw hold at 5 m/s, stall with the real LE seam, trim vs speed) | CDR-07, -08, -15, -16 | 13 Dec | CDR-AE C2, C3 |
| B-12 | Keep / reverse decision recorded in `params/CHANGE-LOG.md` | CDR-08 | 15 Dec | `CONFIGURATION.md`; CDR-BT §5 item 16 |

## 2. Key figures the board relies on

| Figure | Value | Limit | Status | Source (spot-checked where marked ✓) |
|---|---|---|---|---|
| Half-fin face, far field, D-65 side load | MS −0.34 | ≥ 0 | fail | ✓ `graph.json` `CL-C4-SIM-MS-FACE-FAR` −0.343 |
| Strip tail anchor | RF 0.71 | ≥ 1 | fail | ✓ `graph.json` `CL-C6-STRIP-ANCHOR-RF` 0.7075 |
| Violated claims the graph does not count (limit 0, `margin` None) | 15 | 0 | fail (tooling) | ✓ chair read of `graph.json`; ids in CDR-03 |
| Worst-pack hover T/W if the maker's full-throttle row is real | 1.44 | ≥ 1.6 | risk | CDR-AE-01 (`REVIEWER EST`) |
| Winding current at the 100 A limiter | 30.7 A | 25 A / 30 s | fail as posed | CDR-AE-02 (`REVIEWER EST`); ✓ `CL-E1-ILIM-I` 24.75 A is battery-side |
| Path resistance, pack → ESC pads | 7.92 mΩ | `params.json` carries 6.7 | stale key | ✓ `graph.json` `CL-F1-R-EXT` 7.925 |
| Station-mode separation, 3-D | 0.145 | ≥ 0.20 | fail | ✓ `graph.json` `CL-C4-SIM-SEP` 0.1454 |
| SITL hours | 0 | ≥ 10 before the order | fail | `STATUS.md` issue 10 |
| Filings done | 0 of 5 | 5 by 24 Nov | fail | CDR-BT-01 |
| Pessimistic reserve at order | $280.41 | ≥ $309 | fail by $28.59 | ✓ `team/I1/bom_summary.json` `reserve_pess` |
| Same, flight-ready (X07 box + X08 airspeed bought) | $64.55 | ≥ $309 | fail | ✓ 280.41 − 149.72 − 66.14 (`bom_summary.json` `gated`) |
| Free mass reserve vs asks from this review | 3 g vs about 124 g `CHAIR EST` | — | unfunded | CDR-12 |
| Slack on 30 Apr with one crash loop | 2 d | ≥ 0 | thin | CDR-BT-10 |

### Numbers that disagree between documents (chair ruling: the generated claim wins)

| Quantity | Says | Also says | Ruling | Checked in |
|---|---|---|---|---|
| Pessimistic reserve | $280.41 (`bom_summary.json`, graph) | $278.77, $283.72 (`STATUS.md`), $284 (`README.md`); "$30.23 short" in `CDR-electrical.md` | **$280.41, short $28.59** | `bom_summary.json`; `graph.json` `CL-I1-RESERVE-PESS` |
| Station-mode separation, 3-D | 0.145 (`CL-C4-SIM-SEP`) | 0.155 (D-93, `STATUS.md`) | **0.145** | `graph.json` |
| Tube pass lines | E ≥ 78.6 GPa, G ≥ 4.31 GPa (claims) | 69.7 / 4.01 (`STATUS.md`, D-93); E ≥ 70 (H1 card) | **78.6 / 4.31**; H1 reads the claim live | `graph.json` `CL-C4-D3-TUBE-E-REQ`, `-G-REQ` |
| Mount stiffness | 2 259 vs 1 642 N·m/rad, × 1.38 (claims at `3268e69`) | 2 235 vs 1 455, × 1.54 (`STATUS.md` issue 9, D-91) | **× 1.38** | `graph.json` `CL-C4-D3-MOUNT-K-EST`, `-REQ` |
| Foot side load, limit | 39.5 N (`CL-C4-D3-SIDE-LOAD`) | 39.3 N (`team/C1/SUMMARY.md:21`) | 39.5 N until C5 re-runs (CDR-01) | `graph.json` |
| Failing claims in the graph | 72 + 7 requirements (`STATUS.md` issue 6, graph of 17:46 UTC) | 44 claims with negative margin + 15 uncounted; `meta.counts.fails` 53 (graph of 19:05 UTC, chair read) | re-triage after CDR-03; quote the generated count only | `graph.json` `meta` |
| When the fin coupons run | before the order (`CDR-structures.md` cond. 2) | "on the first prints, before flight collars" (`CDR-build-and-test.md` cond. 4) | **before the order**, made possible by condition A4 | `BOM.csv` order column |
| Limiter setting | 100 A, 10 s rule on the flight card (`K09L.param`, CDR-EL-10) | 70 A option (CDR-AE-02 b) | decided on the stand (decision B7) | — |
| Fin mass | 432.0 g (committed `CL-D3-MASS`) | 434.9 g on re-run vs 434 g allocation (`CDR-structures.md` script table) | re-run and settle (CDR-23) | `graph.json` `CL-D3-MASS` 432.0 |

## 3. Action list (deduplicated, in priority order)

"Who": **ENGINEERING-NOW** = fixable in the repo now (CAD, docs, analysis, parameters, BOM lines, proof tooling);
**TEST** = needs hardware or a measurement; **HUMAN** = paperwork, names, money decisions, sign-ups. Owner ids are
roles from `TEAM.md`; names are "—" until `HANDOFF.md` §5 is filled. Dates without a reviewer's date are chair-set.

| Id | Merges | Sev. | Action | Owner | Due | Who |
|---|---|---|---|---|---|---|
| CDR-01 | ST-01, ST-04, ST-07, ST-17, part of ST-02; `STATUS.md` issue 1; SW-03 | blocker | **Fin station on the sideways-landing load.** (a) Write the side-load cap of decision B1 into `params.json` (≤ 23 N limit, pad μ ≤ 0.40). (b) C5 re-runs `landing_sim3d.py`, `sink_sweep.py` (0.05 m/s grid), `side_check.py` on D5-R8 and current masses, μ 0.7 and 0.4 (clears `CL-C5-SIM-INPUTS-STALE` = 6). (c) C1, C4, C6 re-run on the cap. (d) D3 + D5 draw the cheek extension to \|z\| 0.171 m (+16 g `EST`) and a face doubler over x 0.20–0.26 m (target ≤ 6 g, mass — until drawn). (e) C4 reports hot spot **and** far field, shoe at PETG modulus with a 0.5 mm fillet. (f) Collar tail slots printed in the layer plane, orientation in `parts.csv`. Pass: far-field face MS ≥ 0, strip anchor and tail net RF ≥ 1 at 2.156 × the capped load | A1, C5, C1, C4, C6, D3, D5 | (a)–(c) 27 Nov; (d)–(f) 4 Dec | ENGINEERING-NOW |
| CDR-02 | ST-02, ST-06 (test), ST-08 (test), ST-10, ST-14; BT cond. 4; SW-04, SW-12 | blocker | **Coupons before the order**, on early-cart stock (condition A4): `T-C4-TUBE-BEND` / `-TORSION` (fail E < 78.6 GPa or G < 4.31 GPa); `T-C6-LAP-PETG` (fail mean < 4.0 MPa); `T-C6-STRIP-ANCHOR`, printed tail vs epoxy-wet tow lashing, taken to failure on a new 20:1 hole (3 924 N at 20 kg); new `T-C6-BOARD-PEEL` (≥ 85 N shoe-equivalent) and `T-C4-LAM-SBS` (3M 77 vs laminating epoxy); pad incline test μ ≤ 0.40 (≤ 21.8°, 5 repeats) | C6, C4, H1, D5 | 10 Dec | TEST |
| CDR-03 | ST-03, BT-24, EL-04 (limit removed), EL-12; `STATUS.md` issue 6 | blocker (tooling) | **Proof graph tells the truth.** In `proofs/build_graph.py`, when the resolved limit is 0, fail on the sign and report the value as the margin. Fifteen violations are uncounted today: `CL-C4-D3-MS-FACE`, `-MS-STRIP-PAPER`, `-MS-FACE-ROOT-FREE`, `-MS-COLLAR-16`, `-MS-FACE-SHOE`, `-MS-FACE-SHOE-INTACT`, `-MS-FACE-SHOE-FS`, `-MS-FACE-DRAWN-FINE`, `CL-C4-SIM-MS-FACE-DRAWN`, `-MS-FACE-FAR`, `CL-C5-SIM-INPUTS-STALE`, `CL-C5-PACK-STACK-MARGIN`, `CL-B4-SF-RPM`, `CL-A1-CG-RANGE-AFT` and `CL-B3-V-RANGE-AFT-IN` (both −0.12 mm: the CG range is violated at the aft end, see CDR-14). Give `CL-F1-DROP-PEAK` and `CL-F1-ESC-LEN-ALLOW` a limit again. F2 writes `harness.rules.i2c_max_m` 1.0 (D-99). I2 emits `CL-I2-BUILD-HOURS`, `-FIRST-HOVER-WEEK`, `-CUT-TO-HOVER-D`. Correct the "14.1 vs 10 MPa" line in `PROOFS.md` (claim reads 23.6 MPa). Re-triage | A5, C4, C5, F1, F2, I2 | 20 Nov | ENGINEERING-NOW |
| CDR-04 | AE-01, AE-02 (test), AE-08 (test), EL-05, EL-08, EL-09, EL-10 | blocker | **One station on the stand (GT-02 / GT-04)**, bus voltage and phase current logged: full throttle at 14.6 V and 11.9 V, 11×5.5MR. Pass ≥ 1 330 gf and ≥ 1 060 gf. 30 s limiter run, bell ≤ 80 °C (else limiter 70–80 A). A/B of 11×5.5MR vs 11×7E vs 11×5.5E on hover W and static thrust. Cap-leg ripple ≤ the part's rating and can rise ≤ 15 K. XT30U 8.4 A 10 min + 25 A 10 s, AS150U 38 A 10 min, rise ≤ 30 K. If the 11.9 V point fails, the gate mass, prop or pack changes before 5 motors are bought | E1, H1, F1, E3 | 5 Dec | TEST |
| CDR-05 | AE-02 (claim), EL-04, AE-01 (data), AE-09 | blocker | **Propulsion and power models re-based.** Re-state `CL-E1-ILIM-I` on winding current (`I_m = I_bat / duty`; 30.7 A vs 25 A `REVIEWER EST`). Record the maker's rows above 12 A in `CALC-E1-CAL` as a second bound. Set `electrical.r_ext_mohm` 6.7 → 7.9 and re-run E1 `CALC-E1-WORST`, E2, B1. Add the claim "17 m/s, pessimistic, to `BATT_LOW`". Do not go to 14 AWG (+26 g `REVIEWER EST`) | E1, F1, A1, E2, B1 | 1 Dec | ENGINEERING-NOW |
| CDR-06 | BT-01, BT-08, BT-23; `STATUS.md` "no filing done" | blocker | **Filings.** PI sponsor and course-project status (18 Nov); UC Drone Program, TRUST × 2, FAA registration $5 (20 Nov); UC Risk Services answer on the $1 M line, else AMA $92 per pilot (20 / 24 Nov); UC flight request for 8–13 Dec and the RFS 72 h window (24 Nov); FRIA and facility-map screenshots (3 Dec) | team lead, pilot, H3 | 24 Nov | HUMAN |
| CDR-07 | AE-03, EL-02, AE-07 (SITL), AE-11 (SITL), EL-11 (SITL); `STATUS.md` issue 10 | blocker | **Flight software run for the first time, no hardware needed.** Install SITL; run SITL-PLAN S1 (88 of 155 names unmatched) and S2 (output map, which side is "front"). Read `features.txt` for the `CoreWingF405WingV2` 4.7.x build: QuadPlane, tailsitter, `INS_HNTCH`, bdshot, MS4525, QMC5883L/P, fence. S5 back-transition sweep 20 / 30 / 50 °/s from 16 and 18 m/s with B3's post-stall table (pass: altitude gain ≤ 15 m, no motor at its floor > 0.5 s). B3 adds a time-domain back-transition case to `CALC-B3-TRANSITION`. Then, on the board: `T-F3-FW-LOAD`, load and read back `K09L.param` (TEST, 8 Dec) | F4, F3, B3 | S1–S2 20 Nov; S5 6 Dec; 10 h 13 Dec | ENGINEERING-NOW (board load: TEST) |
| CDR-08 | BT-04, AE cond. C3; `CONFIGURATION.md` reversal rule; BT §5 items 1, 13, 16 | blocker | **Twin gate.** Name the pilot and back-up and start the SITL log (17 Nov). A1 writes what happens if cards 1c–1e pass and 1i (transition) is not flown by 13 Dec (decision B5). Keep / reverse entry on 15 Dec | team lead, A1, H2 | 17 Nov / 1 Dec / 15 Dec | HUMAN |
| CDR-09 | EL-01, EL-13, BT-07 (`B02`), BT-13 (ESC spares); WB-18 | blocker | **ESC identified and spared.** `T-F2-DSHOT` on the CoreWing over 0.7 m of 28 AWG twisted lead beside a live 16 AWG pair: Bluejay flashes, rpm on four outputs, error ≤ 1 %. Pass → buy the second 4-pack (+$33.07). Fail or dead listing → 5 × Tekko32 F4 45A (+$52.50 pre-tax `REVIEWER EST`) and re-check the 45 × 23 × 7.5 mm strap envelope. Repo part now: make `BOM.csv` `B02` ("0 spare") agree with `propulsion/parts.csv` `PRP-002` ("4 spare") | E1, I1, F2 | 8 Dec | TEST (BOM line: ENGINEERING-NOW) |
| CDR-10 | BT-02, BT-03, BT-05, BT-06, BT-07, BT-13, BT-20, BT-21, BT-22, EL-16; `STATUS.md` issue 2 | major | **BOM R5.** Two reserve lines in every document ("at order", "flight-ready" with X07 + X08). Apply L1 (foam board, +$25.82), L2 (microSD, +$6.62), L3 (14 → 9 carts, +$40–54 `EST`): reserve $352–367 at order. Add the missing lines as "—" until priced from a page (TPU, 3M 77, anemometer, tether, tapes, abrasives, tools); re-price `C05`; `R01` at $84.49; pack duty; second 16 AWG reel; test props and caps. `R-CRASH-REPAIR` spares: buy X01 + a third tube ($59.54) or re-word the requirement. Add a `covers` column; fix the two dead links (`M01`, `A01`). Quote `bom_summary.json` only. Flight-ready reserve today: about −$135 to +$90 `EST` (CDR-BT §3) | I1, G1, A1 | 8 Dec | ENGINEERING-NOW |
| CDR-11 | BT-05 (owned list), BT-07 (hand-read), BT-06 (waiver), BT-08 (who pays AMA) | major | **Money facts only the team has.** Walk the consumables and tools list: each item owned, borrowed (lender named) or bought. Open every early listing by hand. Decide the pack source or sign the waiver. Decide whether AMA is paid outside the $2 000 | team lead, owner, I1 | 19 Nov | HUMAN |
| CDR-12 | ST-09, EL-05 (mass), BT-16, AE-05 (ballast), AE-08 (prop mass) | major | **Mass contingency funded.** Asks against 3 g free (`STATUS.md` issue 3): solid tail 29 + cheeks 16 + brace 9 + doubler 6 + second caps 8.8 + XT30U saddles 1.2 + 11×7E props 24 (4 × 6 g) + first-flight ballast 30 = about **124 g** (`CHAIR EST`, sum of the reports' `EST` values; 118 g without the doubler). With the cap of B1 the tail is expected to retire: A1 books ≥ 31 g for structures (cheeks 16 + doubler 6 + brace 9) and states where ballast and props come from. A3 runs the CG for the tail-heavy and nose-heavy corners | A1, A3 | 4 Dec | ENGINEERING-NOW |
| CDR-13 | ST-05; SW-05; `STATUS.md` `R-STRUCT-MARGIN` row | major | **Wing-pocket submodel run.** `team/C2/fea/wing_fea_d68.py` on C1-R5 L4 with the ESC grooves and the slot seam. Pass ≤ 150 kPa tension, ≤ 120 kPa compression at ultimate (203 / 199 kPa today, on R4 loads). If it fails: lower grooves stop ≥ 20 mm short with a round end, or upper grooves only | C2, D1 | 27 Nov | ENGINEERING-NOW |
| CDR-14 | AE-05; hidden `CL-A1-CG-RANGE-AFT` (CDR-03); `STATUS.md` issue 7 | major | **CG plan re-issued.** `MIXING_GAIN` 0.5 → 0.65 in `K09L.param`; B3 re-derives the forward limit (range 4.8 → about 11.5 mm `REVIEWER EST`). First fixed-wing flights at CG 0.046–0.048 m (static margin 6–6.7 %) with ≤ 30 g nose ballast. Marks 0.0466 / 0.0514 m not scribed until the twin's neutral point is measured (`T-B3-TWIN-NP`, TEST, 13 Dec) | B3, A3, F4, A1 | 1 Dec | ENGINEERING-NOW |
| CDR-15 | AE-06, AE-09, AE-08 (analysis), AE-14 | major | **Stall and endurance baseline.** Carry the tripped stall (12.85 m/s, `AIRSPEED_MIN` 17) as the planning case until `T-B2-STALL`. Pre-compute the second fallback (`AIRSPEED_MIN` 18 holds to 13.85 m/s; `AIRSPEED_MAX` 20 < VA 20.5). D1 moves the LE tape seam to the lower surface aft of x/c 0.30. B4 adds 11×7E / 7EP / 5.5E to `PROPS.md` (cruise about −28 % `REVIEWER EST`), `THR_MAX` re-derived for VH ≤ 21.8 m/s. B1 carries e 0.85. Twin wing built with the flight seam (TEST) | B2, D1, B4, E1, B1, A2 | 4 Dec | ENGINEERING-NOW |
| CDR-16 | AE-04, AE-07, AE-10, AE-11, AE-12 | major | **Hover yaw and transition authority.** B3 adds the wingtip-into-wind case with fins to `CALC-B3-HOVER` (ratio about 1.5 at 20° in 5 m/s, < 1 in the 8 m/s gust, `REVIEWER EST`). Re-base `CL-B3-TRANS-PITCH-USE` on the 30 % cap with zero elevon credit (0.64 vs 0.60 `REVIEWER EST`). Add `CL-B3-HOVER-PITCH-RATIO-GUST` and the thrust-line term (z 18.5 mm). `Q_A_ACCEL_Y_MAX` 13 500 in `K09L.param`. State the cant 7° → 10° contingency (+28 % yaw arm, −1.5 % thrust) before any mount prints. Twin: QHOVER at 5 m/s, ±20° yaw steps, RCOU spread ≤ 30 % (TEST, 13 Dec) | B3, F4, E1, D3 | 4 Dec | ENGINEERING-NOW |
| CDR-17 | EL-03, EL-06, EL-07; WB-04, WB-17 | major | **Power board mount, link and kill plug.** Redraw: frame to pod on M3 × 18 with the head on the deck (5.5 mm in the insert); board above the heads on four M2 stand-offs ≥ 3 mm on 30.5 × 26.5 mm, no fastener under the 10 AWG pads; re-run the assembly check. `BOARD-CHECK.md` rule changed to prefer case U (decision B8); if S stays, servo power off the link, 2 conductors for FC 5 V, latched headers. Kill plug: WB-04 flying pigtail, or `T-PWR-PARK-PULL` + 50 mate cycles (≤ 50 N). Fix `pod/BUILD.md` step 4. Board facts confirmed at `BOARD-CHECK.md` steps 1–8 (TEST, 8 Dec) | F1, D2, F3, H3 | CAD 27 Nov; check 8 Dec | ENGINEERING-NOW |
| CDR-18 | ST-08, ST-17 | major | **One allowables table** in `team/C6`: PETG and ASA, in-plane and across layers, with the factor that applies. Proposed 23.5 MPa in-plane, 9 MPa across layers (0.5 × 47 and 0.5 × 18, Prusament TDS). D5 states the shoe print orientation, radiuses the snap-window corner (R ≥ 0.5 mm), reports RF on the common value (0.79–0.88 today on other roles' values vs 1.27 on its own) | C6, D5, C3, C2 | 27 Nov | ENGINEERING-NOW |
| CDR-19 | ST-06, ST-11 | major | **Station modes and tube pass lines.** H1's GT-16 card reads `CL-C4-D3-TUBE-E-REQ` / `-G-REQ` live. One table of the 3-D gain of each lever (brace, lighter station, grip) against 0.145 → 0.20. Name the ±45° fallback tube in the BOM. Write the 2P cruise notch (about 200 Hz) into `K09L.param` and add a cruise-rpm dwell to `T-C2-HOVER-VIBE`. Correct D-91 / D-93 numbers | C4, H1, I1, F4 | 27 Nov | ENGINEERING-NOW |
| CDR-20 | BT-09, BT-10, BT-24 | major | **Schedule and `R-BUILD-HOURS`.** G4 re-times stages 2–10 (95 h) and moves 13 h `EST` of bench work before first cut (82 h `EST`). I2 re-plans with cores started 10 Jan (hover 13–15 Feb, slack 2 → 11 d). A2 re-words per decision B2 after sign-off | I2, G4, A2 | 4 Dec | ENGINEERING-NOW |
| CDR-21 | BT-12, BT-10 (workspace), BT §5 items 8, 10, 14, 18 | major | **Places and trainings.** Send the Jacobs questions incl. trainings before 18 Dec and props-on policy (17 Nov). Name one workspace for hot wire, epoxy, LiPo charging and props-on runs (30 Nov). Book an enclosed printer for 93 g of ASA (11 Dec). Two people in town from 10 Jan | team lead, G1, H1, G3 | 17 Nov / 30 Nov | HUMAN |
| CDR-22 | BT-11 | major | **Load.** Each student states hours per week for 30 Nov – 18 Dec (peaks 67.8 h and 73.4 h vs 35 team-hours per week in the study); I2 then moves about 25 h `EST` to January | all four, I2 | 20 Nov | HUMAN |
| CDR-23 | BT-14, ST-16, EL-15, BT-20; WB-02 | major | **Documents brought to the claims.** `BUILD-GUIDE.md`: collars before strips and the four other order changes, collar 22 mm, stage 11 mass / CG text, `HRN-107` steps. Regenerate `team/C6/JOINTS.md`; rename `CL-C6-COLLAR-RF-15MM`. Rewrite C4 `SUMMARY.md` and `SIMULATION-REPORT.md` on D-65. Remove limits from the 13 superseded C3 records. Re-run `fins_calcs.py` and settle 434.9 vs 434 g. G1 / G3 lists gain `FIN-013`, `MEC-013`. E3, F1, F3, harness `SPEC.md` republished on D-89c. H1 `SUMMARY.md`, flight card, twin stall line (12.0 vs 12.3 m/s). One reserve figure and one build-hours figure everywhere, incl. `STATUS.md` | G4, C6, C4, C3, D3, G1, G3, E3, F1, F2, F3, H1, H3, H2, I1 | 11 Dec (before the 18 Dec freeze) | ENGINEERING-NOW |
| CDR-24 | BT-18, ST-15 (c) | major | **Transport box.** 1.26 × 0.55 × 0.54 m with cradle x-stops (nose gap 2.95 mm vs 10; antenna −7.05 mm vs +2); walls as separate panels nested on the two priced sheets; correct the 0.45 m height in the root `CLAUDE.md`. Two cars measured against 1.28 m before the box is cut (HUMAN, 15 Dec) | D7, team lead | 4 Dec | ENGINEERING-NOW |
| CDR-25 | BT-15 | major | **Tool-access rehearsal** on the fin-station test article and one printed pod: hex key on the pinch bolts, iron on the FC pads in the recess, 10 mm spanner on the lower prop nuts; log reach per fastener | G4, D2, D3 | 11 Dec | TEST |
| CDR-26 | EL-11, EL-12 (test), EL-14 | minor | **Failsafe, I²C, compass.** Add "RX failsafe: No Pulses" to `RC-LINK.md` and `T-F5-BENCH`; state the QLAND timer in the SPEC (`FS_LONG_TIMEOUT` 2–3 s if SITL S7 shows 5 s). SCL rise time and compass address at `T-F3-I2C-SCAN`; name a fallback GPS / compass module | F4, F5, F2, F3 | 8 Dec | ENGINEERING-NOW (bench part: TEST) |
| CDR-27 | ST-12, ST-13 | minor | **D-89c parts get claims.** `CL-C6-EYE-BOND-RF` for `FIN-013` (0.59 MPa design, RF 1.7–3.4 `EST`); stack rows `E-FIN-89…92`, `E-MEC-37…40`; `T-D3-EYE` on a bonded eye to 58.8 N; horn bond reported at 930 mm² without the backplate; slot-on-tube torsion check at 2.29 N·m | D3, D6, C6, H1 | 4 Dec | ENGINEERING-NOW |
| CDR-28 | ST-14, ST-15 (a, b), BT-24 (`CL-H1-MSTIFF-U`) | minor | **Rigs and load cases.** 20:1 lever hole; retire `CL-H1-LEVER-NEED9`; C1 adds G4 (restrained run, 29.45 N per tie) and P1 (prop strike); H1 raises the GT-17 load (10.4 % vs 10 %) | H1, C1 | 4 Dec | ENGINEERING-NOW |
| CDR-29 | AE-13 | minor | **`team/E1/propulsion.py` stops writing shared files**: C6's `fastener_parts.py` hook becomes print-only, `--write` to patch | E1, C6, A5 | 20 Nov | ENGINEERING-NOW |
| CDR-30 | BT-16, BT-17, BT-19 | minor | **Small build and check gaps.** Saddle or pad for the four `HRN-113` XT30U pairs; four-bar path at ±30° in the collision job and a list of pairs closer than 0.5 mm; tether card (two slack lines from `POD-007`, stakes 3 m apart, 1.5 m height limit) | F2, A5, D6, H2 | 11 Dec | ENGINEERING-NOW |
| CDR-31 | BT §5 item 17; `STATUS.md` "Unverified in Fusion" | minor | **BuildAll run once in Fusion 360** by a licence holder; FAIL / ERROR lines to A5 | A5 (licence holder) | 11 Dec | HUMAN |

## 4. Decisions the board takes now

"Sign-off" = needs the student team before it is written into the requirements or the order plan. The rest are
engineering decisions the board takes and logs (`params/CHANGE-LOG.md`, next D-number, by the owner named).

| # | Decision | Numbers | Why | Sign-off |
|---|---|---|---|---|
| B1 | **Cap the foot side load at ≤ 23 N limit**, by a pad face with measured μ ≤ 0.40 on the landing mat. The sideways piston snap (23–26 N) is the fallback if the incline test fails | 39.5 N at μ 0.7 today; 29.1 N at μ 0.5; 23 N at μ 0.4 (`EST`, 29.1 × 0.4 / 0.5). Drawn far-field face reaches MS 0 at 25.9 N (`EST`), so at 23 N it reads about +0.13 (`CHAIR EST`, 25.9 / 23 − 1). Strip anchor 0.71 → 1.20, tail net 0.64 → 1.08 (`EST`). Strip force 2 233 → about 1 300 N (`CHAIR EST`, × 23 / 39.5) | One decision removes the root of three fails (face, strip tail, 29 g solid tail) at no mass and ≤ $10 `EST`. The fin fix is still drawn (CDR-01 d): the hot spot is not converged and the 10 MPa paper allowable is a dry estimate | no; consequence for the flight card: a parked aircraft needs μ 0.68 to stay put in 8 m/s (`team/C1/LOADS.md:218`), so it is laid flat or tied when parked (H3 writes it) |
| B2 | **Re-word `R-BUILD-HOURS`**: "≤ 90 team-hours of build (stages 2–10) to first hover and ≤ 5 weeks from first cut" | 111 h (G4) / 113.5 h (I2) vs 90 today; stages 2–10 are 95 h, 82 h `EST` after 13 h of bench work moves before first cut; first cut to hover 34 d vs 21, set by eight serial 24 h cures | Stage 11 is 16 h of test cards, not build. No lever removes the cures. The configuration study itself carried about 115 h pessimistic (`CONFIGURATION.md`) | **yes** (requirement change; A2 edits after sign-off) |
| B3 | **Re-base the crash line on K09-L's own repair bill** | $309 (class-S formula, `SRC-TIEBREAK`) → about $228: pack $65.72 + ESC 4-pack $30.00 + motor $24.99 + servo $41.99 + tube $24.00 + core and tape $20 = $206.70 pre-tax, × 1.1025 = $227.89 (`CHAIR EST` on CDR-BT §3 L6). At-order reserve $280.41 then passes by about $52; flight-ready $64.55 still fails | The tie-break let K01 use its own $224 bill (`config-study/tiebreak/DECISION.md` line 169). The board records that this does not make the aircraft crash-covered once the box and airspeed sensor are bought | **yes** (money rule) |
| B4 | **Report two reserve lines everywhere**: "at order" and "flight-ready" (X07 box and X08 airspeed sensor bought) | $280.41 and $64.55 pessimistic; $365.62 and $149.76 baseline | The gate is met on paper only by holding parts the mission needs behind gates | no |
| B5 | **Partly passed twin gate: split the December order.** If hover and position-hold cards pass and the transition card is not flown by 13 Dec, order on 15 Dec only the lines common to K09-L and K01-lean (servos, hardware, filament) and hold the Aloft carbon cart ($106, 5-day lead) to 5 Jan | first cut is 19 Jan, so the carbon still lands in time; gate 1 has 11 cards in six calendar days with 0 of 10 SITL hours | Otherwise the reversal rule in `CONFIGURATION.md` fires by default on weather or paperwork, not on evidence | **yes** (changes the reversal rule the team confirmed on 2026-11-13) |
| B6 | **Tripped stall is the planning baseline** until `T-B2-STALL`: Vs 12.85 m/s, `AIRSPEED_MIN` / `CRUISE` 17 | free-transition 11.99 m/s rests on XFOIL clmax 1.256 alone; tripped ratio 0.871; the wing has a tape seam at x/c about 0.05. At 17 m/s cruise is about 289 W and about 5.2 min pessimistic, under 5 min to `BATT_LOW` | The likelier case should be the one the mission is planned on. The board accepts that `R-MISSION` is then at risk on paper and that the prop A/B (CDR-04, 11×7E about −28 % cruise power `REVIEWER EST`) is the way out, not an argument between drag models | no |
| B7 | **Motor current is judged in the winding; the limiter value is set on the stand** | 100 A pack limit = 30.7 A winding vs the 25 A / 30 s rating (`REVIEWER EST`); motor reaches 80 °C after 13.6 s at the limiter (`CL-E3-BURST-MAX`). 70 A gives 25 A and T/W 2.01 fresh, zero margin (`REVIEWER EST`) | Keep `Q_M_BAT_CURR_MAX` 100 only if the 30 s stand run holds the bell ≤ 80 °C; otherwise 70–80 A and the T/W line is re-read at the gate mass | no |
| B8 | **Prefer case U (whole FC stack, no link ribbon)** unless `T-F3-VIBE` on the stack fails (transmissibility > 0.30 at 90 Hz) | case S puts the FC's only 5 V on one 28 AWG conductor held by hot glue, and lifts the FC ground about 53 mV with both servos stalled: about 3.4 A and 0.59 V of sense error (`REVIEWER EST`) | The limiter and every battery failsafe read those two lines. Case U also saves 1.9 g | no |
| B9 | **Wider CG range and a more forward first-flight CG**: `MIXING_GAIN` 0.65; first flights at static margin ≥ 6.5 % with ≤ 30 g nose ballast | range 4.8 mm (1.5 % c) is smaller than a ±2 % c neutral-point error (±6 mm `REVIEWER EST`); `CL-A1-CG-RANGE-AFT` already reads −0.12 mm in the graph | The neutral point is unvalidated VLM; 5 % is an aft limit for a tailless aircraft, not a first-flight setting | no (ballast mass comes out of CDR-12) |
| B10 | **Pack source** | Ampow ships from Germany, €113.30, 14 d; duty + brokerage $20–45 `EST` not in the pessimistic line | `R-BATT-HANDLING` says US stock, ground. Either find US stock or waive the clause in writing | **yes** (waiver and money) |
| B11 | **Liability cover outside the $2 000 if UC does not cover it** (as with the Maker Pass) | AMA $89 + $3 per pilot; $92–184 | The reserve cannot take it; without it the twin cannot fly at RFS | **yes** (who pays) |

## 5. What is good

- **The architecture holds.** Four reviewers, 71 findings, none asks for a different configuration, motor count, wing
  or power architecture (each report's verdict).
- **The numbers trace.** Every figure is a claim with a source in one graph (1 728 claims, 145 tests, 0 build errors;
  `graph.json` `meta.counts`). The board could find the stale and the wrong numbers *because* they are claims.
- **FEA practice is sound**: three mesh levels with GCI, beam-theory benchmarks (C2 −2.3 %, C4 −0.68 %), two solvers
  agreeing to 10⁻⁸–10⁻¹¹, equilibrium checks (CDR-ST-17).
- **The aero chain survives independent hand checks**: hover shaft power, cruise point, cruise drag, neutral-point
  shift from CG height, vortex-ring limit all agree; hover electrical power is conservative by about 13 %
  (`CDR-aero.md` "Checks that held").
- **Electrical sizing has margin**: AS150U 70 A vs 37.8 A, servo BEC 8 A vs 5.6 A, FC BEC 4 A vs 0.87 A; the
  tailsitter parameter set matches the ArduPilot pages on every item checked (`CDR-electrical.md` verdict and
  parameter table).
- **Assembly is proven by motion**: 0 swept-path violations; collision check passes in 3 poses with 18 contacts
  ≤ 0.043 mm (`showcase/animation/build/ASSEMBLY-CHECK.md`, `collision/out/REPORT.md`).
- **Structure is cheap to fix**: about $125 per airframe `EST`; no open structural item changes the BOM by more than
  a tube SKU, a pad sheet and some cloth or strip (`CDR-structures.md` verdict).
- **The team finds its own faults**: D-90…D-104 on 13 Nov closed the collar, pins, mount stiffness, pack acceptance
  and CG rule before the board sat (`STATUS.md` issues 1, 3, 7, 9).

## 6. What the team must measure before 15 Dec

| # | Measure | How | The design fails when | Row |
|---|---|---|---|---|
| M1 | Full-throttle thrust, rpm, bus voltage, phase current | GT-02, 14.6 V and 11.9 V bus | < 1 330 gf fresh or < 1 060 gf at 11.9 V (`R-HOVER-TW`) | CDR-04 |
| M2 | Bell temperature after 30 s at the limiter | K-type, GT-04 | > 80 °C: limiter 70–80 A | CDR-04 |
| M3 | Epoxy–PETG lap shear | 5 + 5 single laps, lever frame | mean < 4.0 MPa | CDR-02 |
| M4 | Strip-tail pull, printed tail vs tow lashing | 20:1 lever hole, to failure | < 2.156 × the capped strip force | CDR-02 |
| M5 | Tube E and G | GT-16 | E < 78.6 GPa or G < 4.31 GPa | CDR-02 |
| M6 | Pad friction on the landing mat | incline, 5 repeats | μ > 0.40 (slides above 21.8°) | CDR-02 |
| M7 | ESC identity and bdshot error | Bluejay flash, 0.7 m lead | no target, or error > 1 % | CDR-09 |
| M8 | Power board holes, Vx under load | `BOARD-CHECK.md` steps 1–8 | pattern ≠ 30.5 × 26.5 mm; Vx < 5.8 V at about 5.4 A | CDR-17 |
| M9 | Twin: hover yaw hold, stall with the real seam, trim vs speed | TW3, QHOVER and FBWA logs | RCOU spread > 30 %; Vs > 12.31 m/s (then 17), > 13.07 (then 18); NP ahead of 0.0673 m | CDR-14, -15, -16 |
| M10 | Back-transition altitude gain | SITL S5 | > 15 m, or a motor at its floor > 0.5 s | CDR-07 |
| M11 | Wind at RFS vs RCMC1 | handheld anemometer, three mornings | RFS ≥ 1.4 × RCMC1 (`CONFIGURATION.md` reversal) | CDR-08 |

## 7. What the chair checked, and what it did not

Checked by reading (2026-11-13): the values marked ✓ in section 2 and every row of the "disagree" table against
`proofs/out/graph.json` (19:05 UTC) and `team/I1/bom_summary.json`; the fifteen zero-limit violations by a read-only
query of `graph.json`; the order column of `W05`, `D02`, `C05`, `A04` in `team/I1/BOM.csv`; `R-BUILD-HOURS`,
`R-CRASH-REPAIR`, `R-RESERVE`, `R-BATT-HANDLING` wording in `team/A2/REQUIREMENTS.md:99–116`.
Not checked: any `REVIEWER EST` (carried as the reviewers' own); vendor pages (the reviewers' reads of 2026-11-13
are carried); UC and Jacobs policies (—); the US duty rate on the packs (—); whether the twin's flight controller
set-up needs the airspeed sensor (condition A5 is a chair judgement).
The graph was regenerated between the structures review (17:46 UTC) and this summary (19:05 UTC), and commit
`3268e69` landed during the review; counts in this file are from the later graph.
