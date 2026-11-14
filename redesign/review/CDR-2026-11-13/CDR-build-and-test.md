# CDR, build and test: K09-L quad tailsitter

Reviewer J6-build-and-test, 2026-11-13, branch `redesign/v1` at `39d52a2`. Status of this review: `PROPOSED`
(read-only: documents, CSVs and committed outputs were read; no generator, collision, CAD or graph script was run).
Scope: buildability, manufacturing, assembly, test plans, safety, BOM and budget, schedule, transport, collision report.

## 1. Verdict

**Go with conditions for the 20 Nov early order. Conditional go for the 15 Dec order: it is not releasable today.**
No finding says the aircraft cannot be built. Three things stop the December order as planned:

1. **The twin gate cannot be flown legally on the plan's dates unless five filings land by 24 Nov** (CDR-BT-01).
   Nothing is filed and no pilot is named.
2. **The reserve is worse than the known fail once the parts the mission needs are counted** (CDR-BT-02, -03):
   $280.41 at order, but $64.55 after the transport box and the airspeed sensor, before about $60–250 of
   unlisted consumables, tools and fees (`EST`, depends on what the team already owns).
3. **The reversal rule in `CONFIGURATION.md` fires by default** if the twin has not completed a transition by
   15 Dec, and the plan gives it six calendar days with an unnamed pilot and 0 h of SITL (CDR-BT-04).

Conditions to release the December order are in section 6.

| Figure | Value | Limit | Status | Source |
|---|---|---|---|---|
| Pessimistic reserve at order | 280.41 | ≥ 309 USD | `FAIL` by 28.59 | `team/I1/bom_summary.json` `reserve_pess`; `proofs/out/CHAIN.md` `CL-I1-RESERVE-PESS` |
| Same, with X07 box and X08 airspeed sensor bought | 64.55 | ≥ 309 USD | `FAIL` | 280.41 − 149.72 − 66.14 (`bom_summary.json` `gated`) |
| All-in pessimistic reserve (every gated line) | 17.14 | ≥ 0 USD | inside $2 000, no crash cover | `bom_summary.json` `reserve_pess_allin` |
| Committed goods with a price read on a vendor page | 429.87 of 1 369.05 (31 %) | — | 11 `CHK`, 15 `CARRY`, 32 `EST` lines | `team/I1/BOM.csv` `price_status`, summed 2026-11-13 |
| Build hours, stages 2–11 | 111 (G4) / 113.5 (I2) | ≤ 90 h | `FAIL` | `team/G4/BUILD-STEPS.md` §2; `team/I2/SCHEDULE.md` verdict |
| First cut to first hover | 34 d (19 Jan → 22 Feb) | ≤ 21 d | `FAIL`, not listed as one | `team/I2/SCHEDULE.md` Gantt `B01`, `F01`; `R-BUILD-HOURS` text |
| First tethered hover | 22–24 Feb (week 5 into 6) | week 4 (9–15 Feb) | `FAIL` | `team/I2/SCHEDULE.md`; `BUILD-GUIDE.md` week table |
| Slack on 30 Apr with one crash loop | 2 d | ≥ 0 | thin | `team/I2/SCHEDULE.md` critical path |
| Assembly check | 0 swept-path violations, 6 unsupported | 0 / 0 | pass with 6 notes | `showcase/animation/build/ASSEMBLY-CHECK.md` |
| Collision check | pass, 3 poses, 18 contacts ≤ 0.043 mm | 0.05 mm | pass | `collision/out/REPORT.md` |

## 2. Findings

Severity: **blocker** = the December order or the first flight cannot proceed; **major** = costs a week, a crash,
or more than $25; **minor** = fix in passing. Owner = role id (names are not assigned: `HANDOFF.md` §5 name column
is empty). Costs include 10.25 % tax (`params.json#requirements.tax_rate`) unless marked pre-tax.

| ID | Sev. | Finding | Evidence | Owner | Recommended fix, with numbers | Cost / time |
|---|---|---|---|---|---|---|
| CDR-BT-01 | **blocker** | The twin flights (8–13 Dec) need a UC flight request filed ≥ 7 business days ahead, so by **24 Nov**. That request needs a PI sponsor, UC Drone Program registration, course-project status, $1 M liability cover, FAA registration and TRUST. None is filed; the pilot is not named. Eleven days remain, with Thanksgiving inside them | `team/H3/COMPLIANCE.md` §3 rows 1, 6, 7, 10 and §5 (all "-"); `team/I2/SCHEDULE.md` `TW2` 24 Nov, `M01`; `STATUS.md` "no filing done"; `HANDOFF.md` H6 (pilot "Dec") | H3, team lead | Section 5 table: every item with an owner and a date. Name the pilot and a back-up at the next meeting, not in December | $5 FAA + $0–184 liability (CDR-BT-08); about 6 person-hours `EST` |
| CDR-BT-02 | **blocker** | The reserve gate is met on paper only by holding parts the mission needs behind gates. The transport box X07 ($149.72) is needed before the first drive to the field; the airspeed sensor X08 ($66.14) is in the design ("fitted for gain scheduling"), and the fallback `AIRSPEED_MIN` logic rests on it. With both bought the pessimistic reserve is **$64.55**, the baseline $149.76 | `team/I1/ORDER-PLAN.md` lines 40, 106, 107, 112; `CONFIGURATION.md` "What it is"; `bom_summary.json` | I1, A1 | Report two reserve lines in every document: "at order" and "flight-ready" (X07 + X08 in). Close with CDR-BT-03 levers; then A1 decides the crash line (lever L6) in writing before 15 Dec | 0; one I1 revision (2 h `EST`) |
| CDR-BT-03 | **major** | Budget levers exist that the order plan has not applied. See section 3: L1–L5 recover **$72–91** `EST` at order (reserve $352–371, pass). They do not cover CDR-BT-05 | section 3 | I1 | Apply L1–L3 now, L4–L5 on order day; re-issue the BOM as R5 | saves $72–91 `EST` |
| CDR-BT-04 | **major** | The reversal rule fires by default. `CONFIGURATION.md` reverses to K01 if the twin "cannot complete a transition before the December order". Gate 1 has 11 cards (1a–1k) including 20 landings, stalls and a two-lap transition, in six calendar days, on a first-week tune, with 0 of 10 SITL hours flown. Card 1d needs a measured 5 m/s wind or a fan; mornings are ≤ 5 m/s in about 92 % of hours, and neither an anemometer nor a fan is in the BOM | `CONFIGURATION.md` "Reverse to K01"; `team/H2/FLIGHT-TEST-PLAN.md` gate 1; `team/I2/SCHEDULE.md` `TW3`; `STATUS.md` issue 10; `team/H3/WIND-RFS.md` equipment | A1, H2 | A1 writes by 1 Dec what happens if 1c–1e pass and 1i is not flown by 13 Dec. Proposed: order on 15 Dec only the lines common to K09-L and K01-lean (servos `M01` $92.59, hardware, filament), hold the Aloft carbon cart ($106, 5-day lead) to 5 Jan; it still lands before first cut on 19 Jan. 1d: fly it in the afternoon sea breeze with the anemometer, not with a fan | 0; carbon cart moves 3 weeks, no schedule cost |
| CDR-BT-05 | **major** | Lines the build and the test plans call for are not in `BOM.csv`. Missing: TPU 95A spool (`GER-007`), 3M 77 spray (`FIN-106`, "shop stock", nothing owned), anemometer ($20–30, tie-break estimate), sand bucket, tether line and anchor, 100 mm tape, filament tape, blades, abrasives, cups, gloves, IPA, the "bring or buy" tools (torque screwdriver 0.1–1 N·m, calipers, 0.1 g scale, inclinometer, Z-bend pliers, prop balancer, servo tester, ball bits). `C05` prices laminating epoxy, silica and microballoons at $14 but links a West System 105/206 kit; that kit alone is $82.35–87.97 | `BUILD-GUIDE.md` "Bring or buy", "Consumables"; `review/MANUFACTURING.md` MF-11; `team/G3/PRINT-LIST.md` CR-G3-02; `team/H3/BATTERY-PROCEDURE.md` CR-H3-04; `team/H3/COMPLIANCE.md` CR-H3-02; fiberglasssupply.com West System 105-A/206-A kit, search 2026-11-13 | I1, G1 | One owner walks the list with the team: mark each item owned, borrowed (name the lender) or bought. Budget **$60–250** `EST` until that list exists: about $60 if calipers, scales, torque driver and inclinometer are owned or borrowed, about $250 if everything is bought (reviewer estimate: no page read for most items, so each is "—" in the BOM until priced). Replace `C05` with a 9 oz hobby 30-min epoxy plus small filler bags and price it from a page | +$60–250 `EST`; 2 h |
| CDR-BT-06 | **major** | Flight packs are ordered from Germany, against the team's own requirement. `R-BATT-HANDLING` says "bought from US stock and shipped by ground". The Ampow page prices in EUR (€113.30) and ships from Frankfurt or Bremen. US duty-free entry under $800 ended 29 Aug 2025, so duty and a carrier brokerage fee (UPS minimum $14; $17.50 quoted for DHL) are likely and are not in the pessimistic $131.43 | `team/A2/REQUIREMENTS.md` line 116; `team/I1/BOM.csv` `P01`; ampow.com EU listing and dhl.com de minimis page, search 2026-11-13; `team/I1/ORDER-PLAN.md` early table | I1, E2 | Find a US-stock 4S 6500 120C EC5 pack (same SKU, ≤ 556 g, ≥ 10 AWG) before 20 Nov; none was found by search today. If only the EU store has it: A2 waives the US-stock clause in writing and I1 adds duty + brokerage, **$20–45** `EST`, to the pessimistic line | +$0–45 `EST`; removes a 14-day lead if US stock exists |
| CDR-BT-07 | **major** | Prices: 31 % of committed goods by value were read on a vendor page. Sample re-checked today (section 4): 3 of 8 confirm, 2 links are dead, 2 could not be read, 1 looks low. RadioMaster Pocket Crush is $64.99 in the BOM; US dealers list $77.99–95.99. LANRC 45 A 4-pack: still no US listing found | section 4; `BOM.csv` `R01`, `B02`, `A01`, `M01` | I1 | Before 20 Nov open every `EARLY` line in a browser (automated fetches are blocked: HTTP 429/403), log it in `listing_log.csv`. Carry `R01` at $84.49 (mid dealer price) until the vendor page is read: +$19.50 pre-tax, +$21.50. Decide the ESC now: Tekko32 fallback is +$60 pre-tax and back-ordered to December (`BOM.csv` `B02` note), which would miss the twin | +$21.50 to +$87.65 `EST` if both land |
| CDR-BT-08 | **major** | AMA cover is not in the BOM: $89 per adult member per year (2026) plus a $3 card fee; one pilot $92, pilot + back-up $184. The reserve cannot take it | `team/H3/COMPLIANCE.md` §4; amablog.modelaircraft.org "changes for the 2026 membership year", search 2026-11-13 | H3, team lead | Email UC Risk Services this week: does UC cover a course project at RFS for the $1 M line? If no, the owner pays AMA outside the budget, as with the Maker Pass, or it becomes a BOM line | $0 or $92–184 |
| CDR-BT-09 | **major** | `R-BUILD-HOURS` fails on both clauses, and only one is tracked. 111 h vs 90 h is known. The second clause, "≤ 3 weeks from first cut", is 34 days against 21; eight serial 24 h cures set it and no lever removes them | `team/A2/REQUIREMENTS.md` line 99; `team/G4/BUILD-STEPS.md` §2; `team/I2/SCHEDULE.md`; `review/MANUFACTURING.md` MF-12 | I2, A2, G4 | Section 3, S1–S3. Hours: count build stages 2–10 (95 h; stage 11 is 16 h of test cards) and move 13 h `EST` of bench work before first cut → **82 h**. Calendar: A2 re-words the clause to "≤ 5 weeks from first cut"; the configuration study itself carried 115 h pessimistic | 0 |
| CDR-BT-10 | **major** | Hover lands in week 5–6, and the whole programme has 2 days of slack with one crash loop. The study put P(transition round trip by end of April) at 0.55–0.65; a second crash has no room | `team/I2/SCHEDULE.md` verdict, critical path; `CONFIGURATION.md` "The price" | I2, team lead | S2: start cores, slot and spar-and-block bonding 9 days early (10 Jan) in the team workspace, which is not Jacobs. Hover moves to 13–15 Feb (week 4) and slack on 30 Apr rises from 2 to 11 days, one more 10.5-day repair loop. Needs two people in town from 10 Jan, blocks `FIN-004` printed by 9 Jan, and the workspace named | 0 |
| CDR-BT-11 | **major** | Load peaks are twice the study's capacity in the last two weeks of term. Team load is 67.8 h (week of 30 Nov) and 73.4 h (week of 7 Dec); the tie-break's build rate was 35 team-hours per week. Per-student capacity is "—" in the schedule | `team/I2/SCHEDULE.md` load table and note; `config-study/tiebreak/DECISION.md` gate 2 | I2, team lead | Each student states hours per week for 30 Nov–18 Dec before 20 Nov. Move to January what the December order does not need: coupons other than `T-C4-TUBE-BEND` (decides the carbon cart), practice core 3, jig prints. `EST` −25 h across the two weeks | 0 |
| CDR-BT-12 | **major** | Trainings and places. The fall hands-on training window closed 23 Oct; laser, drill press and woodshop work in `W01`, `W02`, `W03` (29 Nov–16 Dec) depends on trainings nobody holds on record. The workspace for hot wire, epoxy and LiPo charging is not named. No enclosed printer is booked for the ASA motor mounts. Where full-throttle props-on tests run is "—" | `team/I2/SCHEDULE.md` facts and CR-I2-03, -04; `team/G3/PRINT-LIST.md` CR-G3-01; `team/H3/BATTERY-PROCEDURE.md` CR-H3-05; `team/H1/GROUND-TEST-PLAN.md` "Rules for every props-on card" (no location) | G1, H1, team lead | Send the Jacobs questions (drafted, not sent) by 17 Nov and add: "which trainings can we take before 18 Dec" and "may we run a thrust stand with an 11 in prop in the building". Name one workspace by 30 Nov for hot wire, epoxy, charging and props-on runs | 0; 1 h |
| CDR-BT-13 | **major** | `R-CRASH-REPAIR` is not met by the committed BOM. It asks for spares of 1 motor, 4 ESCs, 8 props, 1 CF tube, 4 feet. Bought: 1 motor, 0 ESCs (`B02` "0 spare", X01 gated), 4 props of the flight pitch, and the one spare tube `W03` is the bend-test specimen. Stage 1 of the guide also says "three servos"; the BOM buys two (X02 gated) | `team/A2/REQUIREMENTS.md` line 101; `BOM.csv` `B02`, `B03`, `W03`, `M01`; `BUILD-GUIDE.md` stage 1 step 1; `review/MANUFACTURING.md` MF-10 | I1, G1 | Either buy X01 ($33.08) and a third tube ($26.46) and take $59.54 from the reserve, or A2 re-words the requirement to what is bought and the crash line carries the rest. Cut the ring-crush specimen from the `W04` offcut (312 mm) so `W03` survives as a spare spar | $0–59.54 |
| CDR-BT-14 | **major** | The build documents lag the CAD and the decisions. (a) `BUILD-GUIDE.md` stage 4 still fits strips (4.4) before collars (4.5); the assembly check proves the collar cannot slide on after the strips, and lists four more order changes not written back. (b) Stage 4.5 says the collar height is "not frozen"; D-90 set 22 mm. (c) Stage 11 says mass and CG "currently FAIL", CG 52.6 mm; D-95…D-98 closed it. (d) `team/G3/PRINT-LIST.md` (106 pieces) and `team/G1/PROCESS-TABLE.md` (133 lines) predate `FIN-013` and `MEC-013`; the exporter list has them (2 files, 12 pieces, 134 part lines). (e) `HRN-107-I2C` and `HRN-107-RX` are named in no build step. (f) `team/H1/SUMMARY.md` still expects GT-17 and `T-D5-SIDE` to fail (closed by D-91, D-101). (g) The flight card says the CG rule is open (closed by D-98) and cites a field map that does not exist; the fatigue limits are "—". (h) Twin stall pass line is 12.0 m/s in H2, 12.3 m/s in `HANDOFF.md` D3 | `showcase/animation/build/ASSEMBLY-CHECK.md` "Order changes against BUILD-GUIDE.md", "Parts no BUILD-GUIDE step names"; `BUILD-GUIDE.md` lines 141–165, 349–365; `manufacturing/out/PRINT-LIST.csv` rows 8, 50; `STATUS.md` issues 1, 3, 7, 8, 9; `team/H3/FLIGHT-CARD.md` §1 note, §2 step 0, §4b; `team/H2/FLIGHT-TEST-PLAN.md` 1g | G4, G3, G1, H1, H3, H2 | One pass per owner before the 18 Dec freeze: write the five order changes into the guide; re-run the G1 and G3 generators once the tree is quiet; H3 writes `FIELD-MAP.md` after the first site walk and sets the fatigue limit (proposed: 4 flights per pilot per session, 10 min rest, `EST`) | 0; 6 h `EST` |
| CDR-BT-15 | **major** | What the assembly check does not cover is where a first build fails: hands and tools. No check shows a 2.5 mm hex key reaching the pinch bolts, an iron reaching the FC output pads with the pod in the recess (step 9.4), or a 10 mm spanner on the lower prop nuts. 88 of 214 first-choice directions were blocked, so the fit is tight in many places | `ASSEMBLY-CHECK.md` "What this check does not prove", "First-choice direction blocked" | G4, D2, D3 | Use the fin-station test article (stage 1 step 6) and one printed pod as a tool-access rehearsal before the freeze: log reach for each fastener in `interfaces.json` joint stacks. No new software | 0; 3 h on parts already planned |
| CDR-BT-16 | minor | The six unsupported placements. Four `HRN-113` XT30U pairs hang on their leads, held by a cable tie: at hover vibration that is a fatigue point at the solder cup. `AVN-002` GPS sits 0.6 mm above its pad (tape not modelled): fine. `HRN-107-I2C` touches nothing and has no step | `ASSEMBLY-CHECK.md` "Unsupported placements" | F2 | Give each XT30U pair a printed saddle or a foam-tape pad on the tray (4 × about 0.3 g `EST`; the free mass reserve is 3 g, `README.md`); add a heat-shrink step for the two `HRN-107` joints to guide stage 9 | about 1.2 g `EST`; $0 |
| CDR-BT-17 | minor | Collision report limits. Three poses only; the pushrods and servo arms stay at neutral in the elevon sweep; the sweep is ±25° while the mechanisms build check is at ±30°. Zero clearance passes, so a hand-cut foam part 0.5 mm oversize is an interference the report cannot see. Geometry is the stub backend, not Fusion | `collision/out/REPORT.md` "Not checked"; `subsystems/mechanisms/BUILD.md` step at line 40; `review/MANUFACTURING.md` tolerance table | A5, D6 | Add the four-bar path at ±30° to the collision job; list every part pair closer than 0.5 mm so the builder knows where to sand. Run BuildAll in Fusion once (`HANDOFF.md` H3) | 0; 2 h |
| CDR-BT-18 | major | Transport box does not close on the aircraft as drawn, has no car, and does not fit its sheet. Nose pad gap 2.95 mm vs 10; antenna-to-pad −7.05 mm vs +2; the box needs +10 mm inside length. The cross-shaped base blank is 1 614 mm wide on a 1 219 mm sheet. No car is measured. `CLAUDE.md` still says 0.45 m height; the spec is 0.54 m | `proofs/out/CHAIN.md` `CL-D7-NOSE-GAP`, `-ANTENNA-PAD-GAP`, `-SIDE-CLEAR`; `PROOFS.md` transport row; `review/MANUFACTURING.md` MF-16; `subsystems/transport/CAR-FIT.md` results (empty) | D7, team lead | Box 1.26 × 0.55 × 0.54 m; walls as separate panels with taped corners from the two sheets already priced (floor 1 252 × 542 + lid from sheet 1, four walls from sheet 2: D7 confirms the nest); measure two cars against 1.28 m before the box is cut; correct `CLAUDE.md` | 0 if the nest works, else +$16.54 for a third sheet (`T01` $15.00 pre-tax) |
| CDR-BT-19 | minor | The tethered hover has no rig. Gate 3 and tuning steps 3–4 fly "tethered" but no document gives the line, length, anchor or attachment, and no line is bought. A badly placed tether on a tailsitter can tip it into its own props | `team/H2/FLIGHT-TEST-PLAN.md` gate 3; `subsystems/flight-software/TUNING-PLAN.md` steps 3–4; `BOM.csv` (no line) | H2 | One card: two slack lines from the carry handle `POD-007` to ground stakes 3 m apart, slack length limiting height to 1.5 m, people ≥ 8 m away (flight card zone). 10 m of 3 mm cord and two stakes, about $10 `EST` | +$10 `EST` |
| CDR-BT-20 | minor | Reserve figure differs across documents: $280.41 (`bom_summary.json`, proof graph), $283.72 (`STATUS.md` phases, `team/I1/SUMMARY.md`, `COMPLIANCE.md`), $278.77 (`STATUS.md` issue 2), $284 (`README.md`). Build hours: 111, 113.5 and 114 | files named | I1, I2 | Quote the generated value only (`bom_summary.json`); sweep the four documents | 0 |
| CDR-BT-21 | minor | BOM part ids do not match `parts.csv` one to one. Bought parts are covered, but through lumps and stale ids: `C01`/`C02`/`C04`/`C05` carry `HRN-003`, `H01` carries `HRN-103`, `F04`/`F05` carry `PWR-005` (none exists in a `parts.csv`); `A05` microSD is `AVN-006`, the part is `AVN-007`; nine ground lines `GND-002…012` have no `parts.csv` row (ground lists one part). `FIN-013` and `MEC-013` need no line: 4 × 1.36 g + 4 × 0.63 g = 8 g of PETG on a spool with 445 g margin | check run 2026-11-13: ids in `subsystems/*/parts.csv` (134 lines) vs ids in `team/I1/BOM.csv`; `team/G3/PRINT-LIST.md` §2 | I1, F5 | Add a `covers` column to `BOM.csv` listing every part id a line pays for; add the ground gear to `subsystems/ground/parts.csv`. Then the 1:1 check is a script, not a reading | 0; 2 h |
| CDR-BT-22 | minor | Two dead links in the BOM: `M01` (AMain page 404; the stocked SKU is SH-0255MGP) and `A01` (ReadyMadeRC "Product not found"; the page moved). The Savox servo is single-source with mixed stock: back-order at one dealer, sold out at two, 2 units at another, all $41.99 | fetched 2026-11-13; liquidrc.com, hobbyrecreationproducts.com, store.hobbyetc.com via search 2026-11-13 | I1, D6 | Move `M01` to the 20 Nov order (same price, removes the single-source lead-time risk from December and lets D6 caliper the case before the frame `MEC-008` is printed). Confirm with D6 that MG+ and MGP share the case | 0; cash moves 3 weeks earlier |
| CDR-BT-23 | minor | Compliance facts still open: RFS is a FRIA per the RFS site (confirmed today) but not yet checked on the FAA map; airspace class "—"; whether the team needs "Working at RFS" training "—" | rfs.berkeley.edu/sky, search 2026-11-13; `team/H3/COMPLIANCE.md` §2 rows 5, 7, §3 row 11 | H3 | Screenshot the FAA FRIA map and the UAS facility map for RFS; file both with the first flight request | 0; 30 min |
| CDR-BT-24 | minor | Proof graph: `R-PROCESS`, `R-SCHEDULE`, `R-BUILD-HOURS`, `R-TWIN`, `R-LEGAL`, `R-SITE`, `R-PILOT`, `R-TEST-ORDER`, `R-CAR-FIT`, `R-WIND-MEASURE` have 0 claims, so the two known schedule fails do not show as `FAILS` in the graph; `CL-H1-MSTIFF-U` 10.4 % vs 10 % is a new rig fail | `proofs/out/CHAIN.md` summary table; `PROOFS.md` vibration row | I2, G4, H1 | I2 emits `CL-I2-BUILD-HOURS`, `-FIRST-HOVER-WEEK`, `-CUT-TO-HOVER-D`; H1 raises the GT-17 load inside its 13 % room | 0; 2 h |

Counts: **2 blocker · 12 major · 10 minor.**

## 3. Closing the two known fails

### Budget reserve (short $28.59 at order)

| Lever | What | Reserve gain USD | Basis | Certainty |
|---|---|---|---|---|
| L1 | Foam board: 10 sheets at $1.25 (store) replace the $35.92 Amazon 10-pack `W02` | +25.82 | `subsystems/fins/parts.csv` `FIN-001` vendor note ($1.25); (35.92 − 12.50) × 1.1025 | `EST`: read the shelf price; one brand only (MF-21) |
| L2 | microSD `A05` from team stock | +6.62 | `subsystems/avionics/parts.csv` `AVN-007` "team stock (else ~$6)" | firm if a card exists |
| L3 | Fewer carts: RaceDayQuads lists the GPS, the Pocket Crush and the CoreWing stack ($69.49); put `A01`, `A02`, `R01`, `R02`, `G02` in one cart and the M3 screws (`B07`, `C01`, $7 of goods) in the Amazon cart: 14 vendors → 9 | +40 to +54 | pessimistic shipping $150 over about 14 vendors = $10.71 each (`ORDER-PLAN.md` lines 16, 151); 4–5 carts removed | `EST`: re-quote in the carts; dealer prices differ (CDR-BT-07) |
| L4 | USD pack price confirmed below the EUR × 1.16 guess | up to +18.69 | `ORDER-PLAN.md` line 38 | open; may be negative (CDR-BT-06) |
| L5 | Jacobs yes on ShopBot foam, team accepts CNC cores | +62.54 | `ORDER-PLAN.md` line 38 | open; not relied on |
| **L1–L3** | | **+72 to +86 → reserve $352–367 at order** | 280.41 + 72.44 … 86.44 | passes the $309 line by $43–58 |
| L6 | Re-base the crash line on K09-L's own repair bill instead of the study's class-S formula | line falls to about $228 `EST` | pack $65.72 + ESC 4-pack $30.00 + motor $24.99 + servo $41.99 + tube $24.00 + core and tape $20 = $206.70 pre-tax (`BOM.csv` `P01`/2, `B02`, `B01`, `M01`, `W03`; `CONFIGURATION.md` "$20") | a decision for A1 and A2, not an I1 edit; the tie-break allowed K01 the same test against its own $224 bill (`DECISION.md` line 169) |

Reading: L1–L3 close the **order-day** gate. They do not close the flight-ready picture: $64.55 + $72–86 = $137–151
before CDR-BT-05 (−$60–250 `EST`) and CDR-BT-07 (−$21.50 or more), and before CDR-BT-08 if AMA is charged to
the budget (−$92–184). On pessimistic prices the flight-ready reserve is therefore about **−$135 to +$90** `EST`
(137 − 250 − 21.50 … 151 − 60 − 0): no crash cover in any case, and in the bad case the $2 000 cap itself is at
risk. On baseline prices the same sum is about +$85 higher (365.62 − 280.41). The team should decide L6 with that
number in front of it, settle the owned-or-borrowed list first, and keep X04 (packs 3–4), X05 and X06 gated.

### Schedule (111 h vs 90 h; hover week 5 vs 4)

| Lever | What | Effect | Basis |
|---|---|---|---|
| S1 | Count build, not test: stage 11 (16 h) is GT-06/07/12/13/18 | 111 → 95 h | `team/G4/BUILD-STEPS.md` §2 |
| S2 | Move bench work before first cut: power stack 3 h (already in `EL1` before 18 Dec), avionics flash and bench calibration 4 of 8 h `EST`, foot cartridges 6 of 9 h `EST` (knife and XPS, home work in the closure) | 95 → **82 h** `EST` | `team/G4/BUILD-STEPS.md` stages 5, 9, 10; `team/I2/SCHEDULE.md` `EL1`, `HR1` |
| S3 | Start `B01`–`B05` on 10 Jan in the team workspace (hot wire and epoxy are not Jacobs work) | hover 22–24 Feb → **13–15 Feb** (week 4); slack 2 → 11 d | `team/I2/SCHEDULE.md` Gantt; `team/G4/BUILD-STEPS.md` "Where" (W) |
| S4 | A2 re-words the calendar clause | "≤ 3 weeks from first cut" → "≤ 5 weeks" | 34 d today; 8 serial 24 h cures (MF-12) |

S1 and S2 need G4 to re-time on the practice cores and the fin test article (measured hours replace `EST`). S3 costs
nothing and buys the second crash loop; it needs the workspace named by 30 Nov and the blocks printed by 9 Jan.
If S3 is not possible (nobody in town), accept week 5 formally: A1 closes `CR-I2-01` and A2 edits `R-SCHEDULE`.

## 4. Price and lead-time sample (checked 2026-11-13)

| BOM line | BOM USD | Found | Result | Source |
|---|---|---|---|---|
| `W03`/`W04` Aloft CF tube 22 × 20 × 1 000 | 24.00 | $24.00, in stock, ready to ship | confirms | alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish (search; page 429) |
| `B03` APC 11×5.5MR | 3.83 | $3.83, 0.60 oz; stock not stated | confirms | apcprop.com/product/11x5-5mr/ (fetched) |
| `M01` Savox SH-0255MG+ | 41.99 | $41.99 at four US dealers; stock mixed; BOM link 404 | price confirms; link and stock do not | amainhobbies.com (404), store.hobbyetc.com, liquidrc.com (search) |
| `P01` Ovonic 4S 6500 120C EC5 2-pack | 114.48 / 131.43 pess. | €113.30, ships from Germany; no USD listing found | pessimistic line holds before duty | ampow.com/el-gb listing (search; page 429) |
| `R01` RadioMaster Pocket Crush ELRS | 64.99 | US dealers $77.99–95.99; vendor page not readable | looks low by $13–31 | racedayquads.com, getfpv.com, pyrodrone.com (search) |
| `A01` CoreWing F405 Wing APP V2 | 67.26 | BOM link "Product not found"; RaceDayQuads stack $69.49; GetFPV out of stock | link dead; price near | readymaderc.com (fetched); racedayquads.com (search) |
| `B01` SunnySky X3108S KV900 | 24.99 | vendor page 429; no price found by search (KV720 at another dealer $26.90) | not confirmed | sunnyskyusa.com (429); buddyrc.com (search) |
| `B02` LANRC 45 A 4-pack | 30.00 | no US listing found | not confirmed, as I1 reports | search 2026-11-13 |
| `W01` FOAMULAR NGX F-250 2 in | 59.97 | Home Depot price not shown; third-party $57.08–59.37 | near | superarbor.io (search); homedepot.com (no price returned) |
| AMA adult membership (not in BOM) | — | $89 + $3 card fee from 1 Jan 2026 | confirms H3's $89 | amablog.modelaircraft.org (search) |

Lead times: Aloft and APC as planned (5 d, `BOM.csv`). Packs 14 d from Germany plus customs, "—" days. Savox: plan 7 d,
at risk (stock). Tekko32 fallback back-ordered to December (`BOM.csv` `B02` note).

## 5. Human-only items

No agent can do these. Names are "—" until the team fills `HANDOFF.md` §5.

| # | Item | Owner (role) | Name | Deadline | Why that date | Evidence to file |
|---|---|---|---|---|---|---|
| 1 | Name the pilot and a back-up; start the SITL log | team lead, H2 | — | **17 Nov** | 10 h of SITL and the twin on 8 Dec | `team/H2/PILOT-LOG.md` |
| 2 | Faculty PI sponsor; course-project status confirmed by the capstone instructor | team lead | — | **18 Nov** | UC Drone Program entry needs both | instructor email |
| 3 | UC Drone Program: register pilots and aircraft | team lead, pilot | — | **20 Nov** | before the flight request | confirmation |
| 4 | TRUST certificate, pilot and back-up (free) | pilot | — | **20 Nov** | flight card line 8 | PDF each |
| 5 | FAA registration ($5) and number for label `WNG-020`; put the number on the twin too | pilot (registrant) | — | **20 Nov** | 14 CFR 48.15; twin flies 8 Dec | DroneZone receipt, photo |
| 6 | Liability: ask UC Risk Services; if no, AMA $89 + $3 per pilot | H3, team lead | — | **20 Nov** (answer), 24 Nov (membership) | UC policy $1 M line | email or card |
| 7 | UC flight request for the twin block 8–13 Dec, and the RFS 72 h window | H3 | — | **24 Nov** | 7 business days, Thanksgiving inside | request id |
| 8 | Jacobs questions sent (five drafted, plus trainings before 18 Dec and props-on policy) | G1 / H1 | — | **17 Nov** | fall access ends 18 Dec | reply PDF |
| 9 | Approve and pay the 20 Nov carts, pack cart first; open every listing by hand | owner, I1 | — | **20 Nov** | 14-day pack lead | `listing_log.csv` |
| 10 | Workspace named: hot wire, epoxy, LiPo charging, props-on runs | team lead | — | **30 Nov** | practice cores from 29 Nov; packs arrive about 5 Dec | one line in `team/G1/PROCESS-PLAN.md` |
| 11 | FRIA map screenshot, airspace class, RFS training question | H3 | — | **3 Dec** | before the first twin flight | screenshot |
| 12 | Anemometer in hand; three RFS mornings measured | H3, B1 | — | **7 Dec** | card 1d and `R-WIND-MEASURE` | `wind_log.csv` |
| 13 | A1's written rule for a partly passed twin gate (CDR-BT-04) | team lead | — | **1 Dec** | order on 15 Dec | CHANGE-LOG entry |
| 14 | Enclosed printer booked for 93 g of ASA | G3 | — | **11 Dec** | mounts print in the closure | booking |
| 15 | Two cars named and measured | team lead | — | **15 Dec** | before the box is cut | `CAR-FIT.md` rows |
| 16 | Keep / reverse decision and December order | team lead | — | **15 Dec** | `HANDOFF.md` H1 | CHANGE-LOG entry |
| 17 | BuildAll run once in Fusion 360 | A5 (licence holder) | — | **11 Dec** | before the 18 Dec freeze | FAIL/ERROR lines to A5 |
| 18 | Spring 2027 Maker Pass for all four (outside the budget) | owner | — | **19 Jan** | build week 1 | pass |
| 19 | Flight request for the first hover block | H3 | — | **3 Feb** (S3: 26 Jan) | 7 business days | request id |

## 6. Conditions on the December order

1. Items 1–7 of section 5 done by 24 Nov, or the twin dates move and the order moves with them.
2. BOM R5 issued with CDR-BT-05, -06, -07 lines priced from pages and levers L1–L3 applied; both reserve lines shown.
3. A1's written answers to CDR-BT-04 (partly passed twin) and L6 (crash line).
4. `T-C4-TUBE-BEND` result in hand (10 Dec) before the Aloft cart; `T-C6-LAP-PETG` and `T-C6-STRIP-ANCHOR` planned on
   the first prints, before flight collars (`STATUS.md` issue 1). The December order buys no part that the open
   fin-station decision changes except the strip stock, and the 62 mm solid-tail contingency uses the same stock.
5. Hours per student per week stated for 30 Nov–18 Dec (CDR-BT-11).

## 7. Open proof-graph failures in this scope

| Node | Value | Limit | State | Clears with |
|---|---|---|---|---|
| `CL-I1-RESERVE-PESS` → `R-RESERVE`, `R-BUDGET` | 280.4 USD | ≥ 309 | `FAILS` −9 % | CDR-BT-03 levers, then L6 |
| `CL-D7-NOSE-GAP`, `CL-D7-SIDE-CLEAR` → `R-TRANSPORT` | 2.95 mm | ≥ 10 | `FAILS` −70 % | CDR-BT-18 (+10 mm box) |
| `CL-D7-ANTENNA-PAD-GAP` | −7.05 mm | ≥ 2 | `FAILS` | same |
| `CL-H1-MSTIFF-U` | 10.4 % | ≤ 10 % | `FAILS` (new, D-97) | H1 raises the GT-17 load |
| `CL-H1-LEVER-NEED9` | rig tracks the anchor force | — | `FAILS` (fin station) | `T-C6-STRIP-ANCHOR` on the 15:1 hole |
| `R-BUILD-HOURS`, `R-SCHEDULE`, `R-PROCESS`, `R-TWIN`, `R-LEGAL`, `R-SITE`, `R-PILOT`, `R-TEST-ORDER`, `R-CAR-FIT`, `R-WIND-MEASURE` | 0 claims | — | `UNVERIFIED (no claim)`; two are real fails | CDR-BT-24 |

Source: `proofs/out/CHAIN.md` summary table and lines 1821, 20900, 39318, 39357; `PROOFS.md` triage table.

## 8. What was checked, and what was not

Read: the documents named in each evidence cell. Computed here, read-only: BOM price-status sums; part ids in
`subsystems/*/parts.csv` against ids in `BOM.csv`; the reserve arithmetic above. Web: 10 lines by search or fetch on
2026-11-13; four vendor pages refused automated reads (HTTP 429 or 403), so those rows rest on search snippets.
Not run: `build_bom.py`, `collide.py`, `assembly_check.py`, `build_graph.py`, any `make_*.py` (they rewrite shared
files). Not checked: UC Berkeley's fall 2026 exam dates (—); Jacobs policy on LiPo charging and props-on tests (—);
US duty rate on the packs (—); mass effect of `FIN-013` / `MEC-013` in the A3 roll-up (outside this scope).
