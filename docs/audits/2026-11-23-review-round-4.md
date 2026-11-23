# Independent review, round 4 (2026-11-23, HEAD 5660ee07)

Reviewer: independent agent (wrote none of the rows). Scope: the five READY FOR REVIEW rows T-032, T-089, T-090, T-091, T-092. Edited: this file only. No web page re-fetched (no web tool); no collide / assembly gate rerun (saved outputs in `T092_data/gates/` read). Style: `docs/reference/REVIEW-STYLE.md` (verdict first, evidence, what is still to measure). Paths in the findings are relative to the repo root; `OUT` = `redesign/qp/A/mechanism/out`, `A` = `redesign/qp/A`.

Git state at review: only `docs/session-log.md` is modified; all five rows' work is committed (`1a709569` T-089, `8217ebfa` T-090, `defe9338` T-091, `5660ee07` T-092, `6dc84019` T-032). `python -I tools/ledger_audit.py`: 109 requirements, 92 tasks, 0 errors.

## Verdict table

| Row | Verdict | One-line reason |
|---|---|---|
| T-032 | **PASS WITH FIXES** | Hashes, pins and counts recomputed and equal; follow-once record is honest that a re-render is not bit-identical. Two record defects (stale "nothing committed", unexplained rewrite of two tracked files left open). "reproducible" holds for process, counts and content only |
| T-089 | **PASS** (2 notes) | run_all rerun gives the same 12 STRICT FAILs; GM and forced-response numbers reproduce from the saved JSON; limits unchanged; honest FAIL |
| T-090 | **PASS WITH FIXES** | ORDER-1 arithmetic and every line vs BOM-A.csv recomputed and equal ($795.05 / $81.49 / $10.71 / $887.25). Ledger claim "prices re-read the order week" is not supported; one MN2212 string remains in ORDER-1.csv; one CHANGE-LOG wording differs from the stock file |
| T-091 | **PASS WITH FIXES** | 72-case table and FC-node scan reproduce from `fin1.json` / `nodes_all.json`; recommendation correctly not credited as a pass. Report numbering (D-238 vs logged D-239) and one garbled sentence; benefit rests on one beam-FE mode shape |
| T-092 | **PASS WITH FIXES** | Gate outputs, mass / CG, wire inventory and INS_POS arithmetic check out; side choice is reasoned. But the acceptance item "R15 shipping read from the Easy Composites cart" was not done, so the row cannot be VERIFIED COMPLETE as worded; a few stale texts and one unquantified claim |

No finding below blocks the evidence from being accepted for the work done. Blocking items concern what the ledger may claim.

## Checks done across all rows

| Check | Result |
|---|---|
| `python -I proofs/run_all.py` (from `A`, 2 s) | exit 1, 12 "FAILS" claims: CL-A-MASS-PRED, -MASS-GATE-ROOM, -CUTS-REQUIRED, -VIB-IN-BAND, -VIB-FC, -VIB-GM, -VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD / -STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY; equals the T-089 after-list and `gates/gate_proofs.txt`; working tree unchanged after the rerun |
| `python -I bom_a.py` | total 1,939.17, margin 60.83 (equals D-235 / T-090 / T-092). The +30 % case (-29.68, G7 FAIL) is pre-existing and printed, not new |
| `python -I OUT/T090_data/build_order1.py` | 21 lines, goods 795.05, tax 81.49, ship 10.71, Order 1 887.25; remaining main 1,051.92; sum 1,939.17; "reconcile PASS"; repo unchanged afterwards |
| Limits | `req.gm_min` 2.0, `vib_fc_ms2` limit 30, D-185 band 94-321 Hz and 0.5 rule, lateral CG 5 mm (A-P4), budget 2,000: none changed (diff of `gen_params_a.py`, `claims_a2_struct.py`, `claims_a0_base.py`, `A.param` from `1a709569~1` to HEAD shows only the value / text re-pointing listed below) |
| Claim status by hand | None. Diff shows claim values replaced by computed lists (`SRC-A-T089`, est=True) and `how` text; `run_all` computes the FAIL. CL-A-VIB-GM / -SHIFT still evaluate the FC-at-centre model |
| Exposed wiring | `gates/gate_wire_inventory.txt`: EXPOSED 0.597 strand-m = T-084; no new exposed length; min bend 4.0 mm |
| Personal data | No ZIP code, e-mail or home-path in `ORDER-1.csv`, `T088_stock_2026-11-22.md`, `T089..T092_report.md`, `docs/video/PIPELINE*.md`. (The "9472x" hits in `T091_data/*.json` are digits inside floating-point numbers.) `PIPELINE-FOLLOW-2026-11-22.md` names `C:\Users\dillo\AppData\Local\Temp\wt32` style paths (local user name, no other personal data): note only |
| Unknowns as "—", estimates as EST | Held in all reports read; exceptions listed per row |

---

## T-032 Pipeline doc + improvements summary: PASS WITH FIXES

Acceptance: "reproducible". Evidence: `docs/video/PIPELINE.md` (210 lines), `docs/video/PIPELINE-FOLLOW-2026-11-22.md` (48 lines).

Rechecked:
- Film pin `0da084ab278ecee52321fb0192c6349a5ded0337` exists. `git rev-parse 0da084ab:redesign/showcase/concept-a/film/shots-main.json` = `1001c3eba308...`, blob SHA-256 `f0387489 1634...` and CRLF working-copy SHA-256 `aaa8331b...` equal PIPELINE.md s2. `film-main-1080p60.mp4` SHA-256 starts `7e229b80b4e4...` as stated.
- `git diff 0da084ab HEAD` on `shots-main.json` and `film/clips` is empty (the doc's statement that shot lists, clips and videos are identical at the pin and at 4ebfe0a5 holds).
- The follow record states what was not run (full main film about 92 min estimated, highlight, build film, previews) and labels the 92 min and 6 h as estimates. Step 3 (S3 only, 1,080 frames) is not bit-identical to the committed clips; the record says so (finding 5) and states the cause was not isolated. Honest.
- `a_film` holds no `map_*.json` now. Directory mtime is 2026-11-22 14:55, before step 1 (cam-check, about 23:00 that day); deleting a file at 23:xx would have moved the mtime, so step 1 very probably did not delete `map_T030N.json` (the record says "cannot claim either way"; this evidence narrows it).

Findings:
1. **fix** `docs/video/PIPELINE-FOLLOW-2026-11-22.md` (header line 3 "nothing is committed", s5 "Nothing committed"): the file and PIPELINE.md are committed in `6dc84019`. Replace with "committed in 6dc84019 after this record was written".
2. **fix** same file, s4 item 6 (two tracked clip lists in the main checkout rewritten during the worktree run, cause not found). `render_build_a.py` lines 59 and 72 set `FILM_DIR` from `__file__`, so a worktree run should write the worktree copy; the main-checkout rewrite therefore came from something else (another agent or a script with the main path). Open defect left open. Fix: record, in the doc or `PIPELINE-AUDIT.md`, that the cause is unexplained and add the check "git status redesign/showcase" to the pipeline's end-of-run steps (the doc already warns of it; keep it as a numbered step, not a warning).
3. **note** PIPELINE.md s3 item 1 recipe `cp $F/cam-clearance.json $F/cam-clearance-highlight.json` overwrites a tracked file with a run result; equal to the committed one per the record, but state "expect an empty `git diff`" so a different result is noticed.
4. **note** Ledger acceptance "reproducible" is met for commands, counts, durations, decode and decoded hash of a re-encode, not for pixel identity of a re-render. Status READY FOR REVIEW is the right state; whoever marks it VERIFIED COMPLETE should record that interpretation in `docs/verification-report.md`.

## T-089 Control-band gain margin, X2216 / current cage: PASS

Acceptance: gain-margin claims re-sourced and judged against unchanged limits. Evidence: `OUT/T089_report.md`, `OUT/T089_data/`.

Recomputed:
- Forced response: from `T089_data/t089_fvib.json` (24 groups x 6 corner / zeta rows) the worst sweep and hover-window values are 82.7 / 157.2 / 87.6 / 167.9 / 97.9 / **187.2** and 19.3 / 21.4 / 21.8 / 26.2 / 32.4 / **32.9** m/s2, equal to the report table and to `gen_params_a.py` `vib_fc_ms2`.
- `t089_sens_stdout.txt` VALIDATION: default `iter2` plant reproduces all 27 stored `gm_*` values exactly (read from the file; script not rerun, runtime not cheap).
- `t089_params.json` lists equal the lists in `gen_params_a.py` (`gm_nominal` 1.13 min, `gm_shifted_up` 1.05 min).
- `sitl/fu_cage.py` `configure("t089")` derives TFULL and KQ from `prop_a.py`; default unchanged. Constants labelled EST (16.0 V bus, 40 ms lag, 4 ms delay, gyro LPF 60).
- GM >= 2.0 and 30 m/s2 unchanged; three claims FAIL by computation (run_all rerun).

Findings:
1. **note** `OUT/T089_report.md` s2 "Ladder ... rung 3: FC off the spar centre is not credited (the node choice does not remove the pole)" and the same sentence in D-237 are wrong for spar stations; T-091 corrects it and D-239 says so. Add one erratum line at s2 of the T-089 report ("corrected by T-091 / D-239: true for the cage hub node, not for spar stations") so a reader of T-089 alone is not misled.
2. **note** `OUT/T089_report.md` header and s5 ("Nothing committed", "all uncommitted") are stale after `1a709569`. Cosmetic.
3. **note** The report's lowest-damping statement is correct but worth keeping in the ledger text: forced-response peak is at the sweep edge (6,000 rpm), outside the lowest operating rpm 6,789; operating-window value 32.9 fails 30 only at zeta 0.5 % / hi corner. The ledger row says "19.3-32.9 operating vs 30 FAIL", which is accurate.

## T-090 Order 1 rebuild: PASS WITH FIXES

Acceptance: every line in BOM-A.csv, total and BOM total <= $2,000, MN2212 references removed, ready for approval; prices re-read the order week. Evidence: `A/ORDER-1.csv`, `OUT/T090_report.md`, `OUT/T088_stock_2026-11-22.md`, `OUT/T090_data/`.

Recomputed independently of the script: for all 21 ORDER-1 lines, qty, unit price and status equal the BOM-A.csv row of the same id (P01 4 x 22.99 ... R03 12.99; the script copies them, so I checked them against the file rather than the script output). Goods 795.05, tax 10.25 % 81.49, RDQ shipping 10.71 (EST per `bom_a.py`), total 887.25; main order 1,051.92; sum 1,939.17 = `bom_a.py` total. Unverified EST lines W06, G02, G03, B03 = 93.15 (6.00 + 45.15 + 25.00 + 17.00) correct. Stock statements are dated 2026-11-22 and carry URLs (`T088_stock_2026-11-22.md`); items not readable (Zoro 403) say "not re-read" and give the last read date; R15 shipping "—".

Findings:
1. **fix** `docs/task-ledger.md:100` evidence "prices re-read the order week". Not supported: `ORDER-1.csv` `date_checked` values are 2026-11-14 to 2026-11-21 (W06, G02, G03, B03 "—"); only P01 (and R15 / Zoro in T-088) was read on 2026-11-22; the order date is 1-4 Dec. Fix: reword to "prices as dated per line (2026-11-14..21; P01 re-read 2026-11-22); re-read at the order week" and keep that re-read as an open item (or a new task) before Dillon approves.
2. **fix** `A/ORDER-1.csv` last row (`TOTAL ... ORDER 1 TOTAL`, "written for T-Motor MN2212"). Acceptance says MN2212 references removed. History belongs in `T090_report.md` (it is already there). Fix: delete the history sentence from the CSV row note.
3. **fix** `redesign/params/CHANGE-LOG.md` D-238 says "R15 Carbonwebshop shows no stock"; `T088_stock_2026-11-22.md` says stock "not stated; page shows Add to cart". Reword to "stock not stated, outside-Europe orders by manual quote".
4. **note** Deliverable is a 21-line subset (TP-1 / TP-2 needs plus stock-risk lines); the remaining BOM lines are listed under "Deferred" with reasons. Acceptance "every line in BOM-A.csv" is met by Order 1 + main order = BOM, and the reconcile is by construction (the script derives the main order as BOM minus Order 1), as D-238 itself says. Zoro hub bars for TP-4 are deferred to the main order; the ledger text names them, so state in the ledger that this is deliberate.
5. **note** Budget margin of $60.83 assumes RMRC and Amazon shipping $0 (`bom_a.py`; real RMRC rate "—"). Already stated in the report caveat (1). Keep it as an open item at approval.
6. **note** Order 1 contains P01 with no spare and the RMRC BACKORDER (availability "November 2026", lead time "—"); stated in the report. Also the H743-Wing current-sensor range is "—" (open before ordering, TEST-PLAN-O4B TP-2).

## T-091 Pre-order structural trade: PASS WITH FIXES

Acceptance: candidate judged on GM, VIB-FC, D-185, strength rows, mass, BOM; recommendation with evidence, nothing applied without checks. Evidence: `OUT/T091_report.md`, `OUT/T091_data/`.

Recomputed: `python -I t091_sumnodes.py nodes_all.json` (seconds, 72 cases) gives FC at centre pitch 1.13 / 1.61 / 1.05 (= T-089), at s+0.075 **2.81 / 4.00 / 2.52** (modes x1.0 / 0.8 / 1.2), roll min 2.52 (centre 2.44), yaw min 2.13 (centre 2.13); s+0.150 4.74 / 5.97 / 4.59; s+0.285 12.9 / 7.1 / 15.0 (yaw 2.09, still >= 2.0). Forced response at +75 mm: window 32.2 / 32.7, sweep 94.9 / 180.5: no better than the centre, as the report says. `fin1_summary.txt` reproduces the other table rows (sleeve 1.69 / 2.13 / 1.69, struts 12x10 1.45, arms 10x8 1.66 / 2.48 / 1.49, D-185 FAIL 65 / 69 / 66 / 57 of 72). Limits unchanged; the recommendation does not claim VIB-FC or D-185 fixed. Benefit is not credited in any claim (run_all still FAILS the GM claims).

Findings:
1. **fix** `OUT/T091_report.md` s5 and header call the proposed entry "D-238"; the CHANGE-LOG numbered it D-239 (D-238 is T-090). Fix: change the heading text to D-239 so the report matches the log.
2. **fix** `OUT/T091_report.md` s2 "Reading (a)": "6 of its 72 D-185 cases still pass fewer, 57 FAIL" is garbled. Replace with "arms 10x8: 57 of 72 D-185 cases FAIL (15 pass; baseline 65 FAIL, 7 pass)".
3. **note** The whole pitch-GM benefit rests on one beam-FE mode shape at the 27-30 Hz mode and an IMU placed on the spar line; the real board is 13+ mm forward of the spar axis (x 32-62 mm) and its mount flexibility is not modelled. The sensitivity is steep (1.13 at centre, 2.81 at 75 mm, 12.9 at 285 mm) and only four stations were scanned (0 / 75 / 150 / 285 mm), so the shape between 0 and 75 mm is unchecked. The report states all of this (s1 model limits, s4 check list); the ledger should keep the benefit as "model result, unconfirmed". Optional: scan 25 / 50 mm to show the trend is monotonic.
4. **note** Prices in s3 (R09 spare $15.36, "Only 9 left", RMRC page 2026-11-23; R10 $8.50) have no saved page copy; labelled with a date but unrecomputable. Costs of the not-recommended options are therefore EST-grade; no purchase depends on them.
5. **note** The stale-wording edits (step 0) are present at HEAD: `structures/structures_run.md` l.228, `REQUIREMENTS-A.md` A-P10, `TEST-PLAN-O4B.md` TP-10b step 7 (window 10-400 Hz, l.301). Copies in `T091_data/docs_pre` / `docs_post`. The A-P10 "status FAIL" text is a requirement-table label, not a claim status, and matches the run_all result.

## T-092 FC 75 mm off centre in the CAD: PASS WITH FIXES

Acceptance: CAD mount, cable run inside channels, INS_POS, exposed-wire inventory, claims text, R15 shipping from the Easy Composites US guest cart and the R15 vendor decision, gates once at the end. Evidence: `OUT/T092_report.md`, `OUT/T092_data/gates/`.

Checked against saved outputs and files:
- Gates (`gates_summary.txt`): build_a exit 1 with only `graph:mass TOTAL 1641 g > limit 1500 g`; collide pose 21 `PASS (585 bodies in 129 parts, 3 poses)`, 0 wire ends, 0 folds; 18 linkage poses PASS; a_assembly exit 0, 66 steps; run_all 12 FAILs. The first pose-21 run with 3 wire folds is kept in `gates_run1_wirefold/` and the gates were rerun from the start (honest, no exemption).
- Mass and CG: `cad_mass_stdout.txt` mass 1.64098 kg, CG x 22.049 mm, y **-3.323 mm**, z 6.560 mm; `gate_proofs.txt` CL-A-CG-LATERAL 3.323 mm margin +34 %, CL-A-SM 7.613 %; equal to the report. Lateral limit 5 mm unchanged.
- Exposed wire: 0.597 strand-m unchanged (`gate_wire_inventory.txt`).
- **INS_POS1 signs**: stated conventions (CAD x aft from the leading edge, y right, z up; body x forward, y right, z down) are those in `cad/amodel/common.py` l.12 and `A.param` l.269. Board centre (47.0, -75.0, 17.68) minus CG (22.05, -3.32, 6.56) = (+24.95, -71.68, +11.12) mm in CAD; body = (-24.95, -71.68, -11.12) mm. `A.param` l.271-273: -0.0250 / -0.0717 / -0.0111 m. Signs and magnitudes follow the stated conventions. The FC is aft of the CG (X negative), left of it (Y negative) and above it (Z negative, z down).
- Claims text: `claims_a0_base.py` l.149 stale "12-16 Hz / 21-43 Hz" replaced; VIB-GM / -SHIFT `how` says the benefit is credited only after T-A-TAP / tether; no value changed.

Side choice (-y, lateral CG -3.32 of 5 mm): reasoned in report s1 (single enclosed annex instead of a tunnel past the GPS at y +27.5..52.5; RX UART, I2C and left servo leads go to -y; the T-091 model is symmetric in y so GM is the same either side) and the cost is stated with margin left (1.68 mm) and a reversal route. I consider the choice acceptable, with finding 2 below.

Findings:
1. **blocking (for VERIFIED COMPLETE only)** Ledger acceptance for T-092 includes "R15 shipping read from the Easy Composites US cart (guest) and the R15 vendor decision". The report s4 says the cart was not run ("fetch tool cannot add to a cart") and shipping is "—"; the decision was "no switch, shipping unread". The ledger evidence column says "R15 not switched (shipping —)", so it is honest, but the row's own acceptance is unmet. Fix: either do the guest cart read (browser session) and record the shipping with date, or move the R15 item into a new open task (T-093) and remove it from T-092's acceptance text by an append (not an edit of history), then re-review.
2. **fix** Report s1 "+y would have kept it near -0.4 mm" has no computation on disk. `cad/amodel/electrical.py` l.599 predicts a CG-y shift of about -1.3 mm (28 g x 75 mm / total), the measured shift is -1.66 mm (-1.66 to -3.32), and the +y figure follows neither. Fix: either run `cad_mass` once with `FC_YC = +0.075` (cheap, no gates) and record the number, or label the -0.4 mm "EST (mirror of the measured shift, not computed)". Also state the margin consequence: 1.68 mm of lateral CG is left for as-built asymmetry (pack y-trim, wire routing, the 0.6 g splice).
3. **fix** Right servo lead needs about +74 mm (report s1, "0.6 g splice EST"), servo stock lead length "—". Confirm in the build guide that the splice is in the enclosed groove / under the cover and counted; if it sits outside, the exposed length (0.597 m) rises. Fix: add the splice location to the wire inventory notes (`HRN-001` / E3b) and rerun `wire_inventory` (11 s) only.
4. **fix** `A.param` l.102 comment says the FC is moved "to cut the 27-30 Hz wing-flap pickup" as a fact. Per D-239 the benefit is a model result until T-A-TAP / tether. Fix: append "(model result, T-091; unconfirmed until T-A-TAP / tether)".
5. **fix** `A/cad/amodel/electrical.py:817` part description `AVN-007` still reads "FC on the wing centre, not on the cage hub"; the FC is now 75 mm off centre. Fix: "FC on the wing 75 mm left of centre (D-239 / D-240), not on the cage hub". Regenerate parts list only if the text feeds a generated file.
6. **fix** `A.param` l.270 and `A.param` l.268 correctly say the INS_POS reference point (CG assumed) and the IMU chip offset are unverified. Add both to the ledger open items and to the T-A-CG-BREADBOARD / TP step list so they are checked before the first powered test, not "before flight". (Reference point not re-read this session; I could not read the ArduPilot parameter text either, so I do not confirm or deny the CG assumption.)
7. **note** Report s2 gives "predicted 1.8796 -> about 1.888 kg EST (hand tally)" while `run_all` (CL-A-MASS-PRED) prints 1.881 kg from `params-A.json` (`1.64098 x 1.1174 + 0.048 = 1.8815`). Two bases for one quantity; state which is quoted (the claim's, 1.881) and drop or label the hand tally.
8. **note** R15 data (Easy Composites US, $59.05 / m, 113.1 g/m, "more than 50") read 2026-11-23 has no URL or saved capture in `T092_report.md` s4 (the URL is in `T088_stock_2026-11-22.md`, which carries the same price but not the 113.1 g/m). Add the URL and the read date next to 113.1 g/m. Easy Composites US, Carbonwebshop line and BOM unchanged: `bom_a.py` 1,939.17.
9. **note** Report header "Nothing committed" stale after `5660ee07`. Report s6 item 2 says REQUIREMENTS / MISSION text still says "FC on the wing spar centre"; a grep of `A/*.md` for FC / IMU near "spar centre / wing centre" found only `BUILD-GUIDE-A.md` (updated) and `electrical.py:817` (finding 5), so that item is partly out of date.
10. **note** All CAD gate outputs are saved; the saved times (collide pose 21 1,007 s, linkage 1,153 s, assembly 2,283 s) agree with the run being real. No part clash, no open wire end.

## Required before any of these rows is marked VERIFIED COMPLETE

- T-092: finding 1 (R15 shipping read or split), findings 2-6.
- T-090: findings 1-3.
- T-091: findings 1-2.
- T-032: findings 1-2 (and the interpretation note in finding 4).
- T-089: none required; findings are notes.

Not verified by me: the web prices and stock (no web tool); the beam FE and fu_cage numerical runs themselves (about 22 min and longer; outputs recomputed from saved JSON only); the three T-092 gate runs (read, not rerun, as instructed); whether ArduPilot's INS_POS origin is the CG.

## Re-check of the fixes (conductor, 2026-11-23)

Each fix was applied as written and checked by reading the changed line; text-only, so collide / assembly were not rerun (no geometry changed). Cheap reruns in `redesign/qp/A/mechanism/out/T092_data/r4/`: build_a fails only `graph:mass 1641 g > 1500 g`; wire_inventory EXPOSED 0.597 strand-m; cad_mass, parts_links, build_guide exit 0; run_all the same 12 STRICT FAILs; `build_order1.py` rerun, ORDER-1.csv differs only in the TOTAL note.

| Finding | Fix applied |
|---|---|
| T-032 1 | PIPELINE-FOLLOW header and s5: "committed in 6dc84019 after this record was written" |
| T-032 2, 3 | PIPELINE-FOLLOW s4 item 6: cause stays unexplained (FILM_DIR from `__file__`); PIPELINE.md s7 step 4: end-of-run `git status --short redesign/showcase` and the expected empty highlight diff |
| T-032 4 | interpretation recorded in the ledger evidence and docs/verification-report.md |
| T-089 1, 2 | erratum line at s2 of T089_report.md (hub node, not spar stations; committed 1a709569) |
| T-090 1 | the order-week re-read is a new task, T-093; T-090 evidence says prices are as dated per line |
| T-090 2 | ORDER-1.csv TOTAL note and the `build_order1.py` generator: MN2212 history removed (it is in T090_report.md) |
| T-090 3 | CHANGE-LOG D-238: "stock not stated (page shows Add to cart), outside-Europe orders by manual quote only" |
| T-091 1, 2 | T091_report.md s5 heading and row now read D-239; the garbled sentence reads "57 of 72 FAIL, 15 pass; baseline 65 FAIL, 7 pass" |
| T-092 1 | R15 cart shipping moved to T-093 (the cart needs a delivery address only Dillon can enter); T-092 report s6 item 5 says so |
| T-092 2 | "+y about -0.4 mm" labelled EST (not computed); the 1.68 mm margin is stated as the as-built asymmetry allowance |
| T-092 3 | splice placed under the bay cover next to the FC: `a_build_steps.py` E3b and the HRN-001 text in `electrical.py`; BUILD-GUIDE regenerated; exposed length unchanged (0.597) |
| T-092 4 | A.param l.102: "model result, T-091; unconfirmed until T-A-TAP / tether" |
| T-092 5 | electrical.py AVN-007: "FC on the wing, 75 mm left of centre (D-239 / D-240)" |
| T-092 6 | TEST-PLAN-O4B TP-2: INS_POS reference point and IMU chip offset checked before the first powered test |
| T-092 7, 8, 9 | report quotes CL-A-MASS-PRED 1.881 kg; Easy Composites URL and read date added; header says committed 5660ee07 |
