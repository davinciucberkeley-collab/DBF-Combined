# Milestone audit T-048 with full-spec reconciliation T-055 (2026-11-23)

Auditor: ledger-auditor (accounting audit; no technical re-derivation). Repo HEAD 4f4a2b81, branch redesign/v1.
Working tree at start: CLAUDE.md, docs/spec-amendments.md (AM-030 appended) and docs/spec-integrity.sha256 modified, uncommitted.
Read-only audit: no ledger, requirements, spec or amendment file was edited. Nothing here is a VERIFIED COMPLETE mark.

## 0. Full-spec statement (T-055, R-GEN-04)
I read ALL of `docs/MASTER_PROJECT_SPEC.md` (1,173 lines: Directive, Parts 1-13, the 20 non-negotiable rules,
Immediate Execution Instructions; read in two passes, lines 1-600 and 601-1174) and ALL of `docs/spec-amendments.md`
(378 lines, AM-001..AM-030), then `docs/requirements.md` (185 lines, 109 R-ids), `docs/task-ledger.md` (103 lines,
93 T-ids), `docs/session-state.md` (70 lines) and the phase table of `docs/execution-plan.md`.

## 1. Commands run
| Command | Result |
|---|---|
| `python -I tools/ledger_audit.py` | 109 requirements, 93 tasks, {VERIFIED COMPLETE 66, IN PROGRESS 5, BLOCKED 6, NOT STARTED 11, READY FOR REVIEW 1, FAILED 1, EXPLICITLY DEFERRED 3}; 0 errors |
| `python -I tools/plan_rid_check.py` | 109 R-ids, 0 missing from execution-plan.md |
| script (scratchpad) rolling task statuses up to requirement rows | 109 rows parsed; every R-id has at least one task; 47 rows stale (section 3.1) |
| script checking backticked evidence paths of all 66 VERIFIED rows | all exist except `T092_data/r4/` (a bare relative path; directory is under `redesign/qp/A/mechanism/out/`, fine, cosmetic) |
| `python -I tools/spec_guard.py --check` (named in spec-amendments.md header) | file does not exist (see F-12) |

Counts agree with session-state ("109 R-ids; ledger 93 tasks (66 VERIFIED COMPLETE)").

## 2. Finding (1): coverage of the spec and the amendments by R-ids and tasks

### 2.1 Spec: covered
Every Part 1-13 sub-section has at least one R-id (PRES, GEN, TRK, ORC, CAD, PHY, OPT, VID, INT, REPO, MON, PLAN,
VER, DEL); non-negotiable rules 1-20 map to R-RULE-01..10 (rules 1,2,12 / 3,4,14,20 / 5 / 6,7 / 8 / 9 / 10,11 / 13 /
15-18 / 19; all 20 present). Every R-id has a task (no orphan). Every task has a parent that exists.

### 2.2 Spec: missing, merged or mis-scoped
| # | Item | Problem | Fix |
|---|---|---|---|
| S-1 | Directive "Do not start from scratch. Preserve existing working capabilities" and 4.1 "Preserve functioning systems" | No R-id states it (R-CAD-01 only lists a baseline; R-RULE-07 covers deleting files, not preserving capabilities) | requirements.md, new row R-GEN-05, Src "Directive; 4.1", Requirement "Do not start from scratch; preserve existing working capabilities and functioning systems", Pri P0, Owner C, Acceptance "No working capability removed; T-044 and final regression show the same gates run", Verification "regression list T-044 / T-049", Status IN PROGRESS. Parent task: add R-GEN-05 to T-044's Parent column and to T-047. Add R-GEN-05 to execution-plan.md phase 2 row (plan_rid_check requires it). |
| S-2 | 8.2 "Do not duplicate another team member's work unnecessarily" | Not in R-INT-02 or any row | requirements.md R-INT-02 Interpretation: append "; reuse `tools/vtol.py` / team CLI, do not duplicate it (spec 8.2)". |
| S-3 | R-VER-01..06 all carried by one task (T-047) | Spec 2.1 "do not combine unrelated requirements into broad tasks that cannot be independently verified"; six independent verifications (requirements, engineering, AI workflow, video, repository, resolve) in one row | task-ledger.md: keep T-047 as the umbrella (Status NOT STARTED, correct) and append rows T-094..T-099, one per R-VER-nn (Parent R-VER-0n, Deps T-047's deps, Owner O, Status NOT STARTED). Alternative: leave and note that T-047 produces six sections each with its own evidence; flagged because spec 2.1 names exactly this pattern. |
| S-4 | R-DEL-01 lumps all of Part 13 (five groups, about 38 bullets) in one row | Interpretation maps groups to families but acceptance is one checklist | Acceptable if T-059 produces a per-bullet table; add to T-059 Acceptance: "one row per Part 13 bullet (38 lines), each with an artifact path". |
| S-5 | R-REPO-08 (spec 9.8, ten checks) | Row rolls up VERIFIED only through T-044, whose own evidence says "spec 9.8 re-execution of collide / assembly / render / browser load after cleanup deferred to T-049 and the final gate run". Also 9.8 "prompt preservation still works" and "context recovery still works" are not named in T-044's evidence | task-ledger.md T-044 Status: keep VERIFIED only if R-REPO-08's Status stays IN PROGRESS; set requirements.md R-REPO-08 Status to `IN PROGRESS` (not VERIFIED), Verification append "9.8 items collide/assembly/render/browser/recovery/prompt preservation re-run in T-049". Add R-REPO-08 to T-049's Parent column so the deferral has an owner (currently T-049 has Parent R-REPO-10 only; the deferral is carried by words, not by a link). |
| S-6 | T-051 (agent and software performance metrics, spec 9.5) NOT STARTED, carried only under R-REPO-05 | The deferral is real, tracked; but it can be done now (model-usage backfilled 2026-11-22) | see section 4. |

### 2.3 Amendments: every instruction against requirements.md
requirements.md has rows only for AM-001 (R-COM-01..06). AM-002..AM-030 are mapped only by the "Requirement IDs"
line inside spec-amendments.md; the cited R-ids exist, but the instruction content itself is in no requirement row,
so a requirement-by-requirement final audit (T-047, spec 12.1) cannot test it from requirements.md. Standing
instructions with no R-id text:

| # | Amendment | Standing instruction not captured | Fix (requirements.md, new rows) |
|---|---|---|---|
| A-1 | AM-008 | Aircraft is designed by Claude and built by students; no commercial kit airframe (cited R-OPT-01/02, R-GEN-02, R-CAD-01: none says it) | R-GEN-06, Src AM-008, P0, Owner C, Acceptance "no kit airframe in the BOM or design record", Verification "BOM-A.csv + CHANGE-LOG review", Status IN PROGRESS. Parent task: T-075 (VERIFIED; add R-GEN-06 to its Parent) and T-047. |
| A-2 | AM-011, AM-013, AM-012, AM-014, AM-018, AM-019, AM-020, AM-015 | Budget test = total incl. crash reserve (by definition) <= $2,000; weight may exceed the mass gate in initial design (AM-011); no supplied materials (AM-014); team phones/laptop/Jacobs tools free (AM-015); no purchase before early Dec | R-GEN-07 (budget), Src "CLAUDE.md hard constraints; AM-010..AM-021", P0, Acceptance "`bom_a.py` total incl. reserve <= $2,000 at every milestone", Verification "run bom_a.py (T-092: $1,939.17)"; R-GEN-08 (weight tolerance AM-011: mass gate miss does not stop design; physics checks apply at predicted mass), P1. Parents: T-082, T-086, T-087, T-093 for R-GEN-07; T-083 for R-GEN-08. |
| A-3 | AM-016 | Stronger-wing path adopted; limits not relaxed; 2026-12-15 bench test decides; failed bench reopens configuration | covered functionally by T-083 / TEST-PLAN-O4B (R-OPT-05, R-CAD-03 cited). Add one sentence to R-OPT-05 Interpretation: "AM-016: limits not relaxed; bench test of 2026-12-15 decides". |
| A-4 | AM-028 (and AM-024..AM-027) | "Do not ask to continue between steps" | R-COM-02 Interpretation says it, but cites only the memory file. Fix: R-COM-02 Interpretation append "AM-028 (verbatim in spec-amendments.md)". |
| A-5 | AM-004 | Opus consults replace Dillon while away (8+ h; expired) | Not a standing rule; no R-id needed. Note in session-state Reconciliation that AM-004 lapsed. |
| A-6 | AM-029 | Approval to remove 3 line-ending-only worktrees | Cited R-REPO-04; the approval is the one spec 9.3 step 9 needs, so R-REPO-03 is the right parent too. task-ledger.md T-042 already cites AM-029 (good); T-041 Parent R-REPO-03: append to the T-041 Evidence cell "batch 3 approval AM-029 (2026-11-23)". |
| A-7 | AM-030 | "Keep what we have now" (no test equipment bought: no press rig/testing machine; borrow a frame, else TEST-PLAN lever rig) plus a work rule "continue every task that can be done now" | see section 5 (not reflected anywhere). |

## 3. Finding (2) and (3): requirements roll-up, VERIFIED evidence, stale statuses

### 3.1 requirements.md Status column is stale (spec 2.3, R-TRK-03, "Status is the requirement's roll-up")
The file states "Status is the requirement's roll-up: VERIFIED COMPLETE only when every task under it is". 47 rows
show IN PROGRESS / NOT STARTED although every task under them is VERIFIED COMPLETE. Fix, column "Status" (last
column) to `VERIFIED COMPLETE` for each of:
R-PRES-01, -02, -03, -05, -06, -07, -08, -09, -10, -11, -12, -13; R-TRK-01, -02, -03, -04, -06; R-ORC-01, -02, -03,
-05; R-CAD-01, -06; R-PHY-01, -02, -04, -06, -07, -10, -11; R-OPT-03; R-VID-14; R-REPO-02, -03, -04, -07, -09
(R-REPO-08: see S-5, keep IN PROGRESS); R-MON-01, -02, -03, -04; R-PLAN-01; R-RULE-01, -04, -05, -06, -08, -10;
R-COM-03.
Caveats the conductor must apply before flipping (do not flip blindly):
- R-RULE-01 / -04 / -06 / -08 and R-MON-02 / -03 are standing rules that bind every task; they are "ongoing"
  until T-047. Keep IN PROGRESS (their only task being VERIFIED does not close a rule that continues). Remaining flips: 41 rows.
- R-PLAN-01: tasks T-046 and T-075 are VERIFIED; but the plan table omits T-064..T-093 (F-9). Flip only after F-9.
- R-PHY-03 and R-PHY-05 show NOT STARTED while T-018 / T-020 / T-063 are VERIFIED and T-061 is FAILED (see 3.3): set to IN PROGRESS until T-061 is resolved, then VERIFIED.
- Rows NOT STARTED with real work done, set to `IN PROGRESS`: R-CAD-02, R-CAD-03, R-CAD-04, R-CAD-05, R-PHY-08, R-PHY-09, R-OPT-02, R-OPT-04, R-OPT-05, R-GEN-04 (once this audit is accepted, to VERIFIED via T-055).

### 3.2 VERIFIED COMPLETE rows whose evidence lacks a check by someone other than the implementer
Rule: ledger header "only with evidence that someone other than the implementer checked". 66 rows read. 58 name a review file, reviewer agent, Dillon or a fresh-agent test. Weak or missing:

| Row | Evidence as written | Gap | Fix (row T-nnn, column Evidence; Status stays until done) |
|---|---|---|---|
| T-016 | "conductor re-read electrical.py:530-560, values match s5" | Conductor is the delegating agent, not an independent reviewer; acceptance asked "O spot-checks 3"; `2026-11-19-setup-check.md` only confirms paths exist | Run an O/sonnet spot-check of 3 capability-audit rows (rerun command each), file `docs/audits/<date>-T016-spotcheck.md`; append that path to Evidence. Until then set Status to READY FOR REVIEW. |
| T-017 | "conductor re-grep" + `2026-11-18-physics-labels.md` (implementer's own list) | no independent re-grep | Add an independent `grep -rniE "physics (check|simulation|gate)"` re-run by the next audit; append the path. Status READY FOR REVIEW until then. |
| T-026 | "conductor checked render_build_a.py:66-70 ... Blender exe exists"; film-final-review does review the film but not PIPELINE-AUDIT.md coverage | acceptance "all 7.1 items covered" never checked by a non-implementer | R-VID-01 row says "O read"; append an O read note (can be done in the T-048 pass). Status READY FOR REVIEW until then. |
| T-031 | "encoded from ebb89693; full decode 0 errors" | the decode is the implementer's; independence comes from T-033 (O, VERIFIED) and `2026-11-18-film-final-review.md` | acceptable: append "independently checked by T-033 (verification-report Video)" to Evidence. No status change. |
| T-063 | conditions "checked by conductor rerun of run_all.py" | the opus review `2026-11-18-D212r3-review.md` said "accept with conditions"; closure of the conditions was verified only by the conductor | `2026-11-19-mech-review.md` (T-018/T-019/T-020 reruns of the same joint) is a partial independent check; append that path. Acceptable with the append. |
| T-074 | implementer reports + "decided by Dillon" | Dillon decided the outcome (AM-007), not the three check results; `2026-11-22-ready-rows-review.md` does not review T-074 | Next review round: recompute the three check results (T074_checks12.md, T074_check3.md); append the review path. Status READY FOR REVIEW until then. |
| T-075 | "Altus withdrawn (AM-008); Dillon chose O4b (AM-009)" | the "re-plan record" deliverable and "every R-id still carried" acceptance were checked by nobody | This audit supplies the R-id check (`plan_rid_check.py`: 109/109, 0 missing). Append "R-id carry check: `docs/audits/2026-11-23-milestone-audit.md` s1" to Evidence. Acceptable after that append (the task has no engineering content beyond the board choice). |
| T-011 | haiku audit + conductor fixes | fixes to the 21 gaps were applied by the conductor; the setup-check of 2026-11-19 re-read the registry | acceptable (T-009's 11-19 independent check covers it); append `2026-11-19-setup-check.md` to T-011 Evidence. |
| T-008 | fresh haiku agent, conductor fixed the 8 gaps | fix verification by conductor | acceptable; the fresh agent is the independent check. |

### 3.3 BLOCKED / FAILED / IN PROGRESS rows: is the stated blocker still true?
Latest evidence read: `redesign/qp/A/mechanism/out/T092_report.md` (D-240, 2026-11-23), `T084_report.md` (D-233),
`T083b_report.md`, `redesign/qp/A/proofs/out/READABLE.md` (CL-A-LINKAGE-FREEPLAY), run_all in T092_report s2.

| Row | Status now | Stated blocker | True now? | Fix |
|---|---|---|---|---|
| T-077 | BLOCKED | "part 8 (D-226 drawn): tallied 1,598.4 g, window +1.07 %, CG 30.17 mm / SM 4.30 % FAIL, BOM $2,150.75 (-$150.75); O4b infeasible as drawn, configuration reopened per AM-016" | **No, stale.** AM-017 study, AM-018 motor swap, D-227..D-233 closed that branch. Current (T092_report): CAD 1,641.0 g, predicted 1.881 kg, CG 22.05 mm, SM 7.61 %, window +11.88 %, T/W 2.632 / 2.111, BOM $1,939.17 (+$60.83); collide pose 21 + 18 linkage poses PASS, a_assembly 129 / 129 PASS; build_a fails only the 1.5 kg mass gate (allowed to be missed, AM-011); run_all 12 STRICT FAILs, all carried and explained (D-237, bench / tap tests) | Status -> `READY FOR REVIEW`. Evidence column: append "2026-11-23: blocker of part 8 superseded: AM-017 study, AM-018 (X2216), D-226..D-240; current gates PASS (T092_report s2, T084_report s7: collide, a_assembly 129/129, wire 0.597 strand-m, drawings 49/49); open items moved: hub RF to T-083b (min 1.21 at x2.23), pad zeta to TP-3, stall to TP-11, vibration to TP-10b / T-089; needs an independent review before VERIFIED". Also: the Evidence cell repeats the part 1-7 text six times verbatim (about 30 kB); replace the copies with one pass plus a pointer to `T077_cad.md` (append-only applies to rows, not to duplicated sentences; keep a one-line note "duplicates removed 2026-11-23"). |
| T-083 | IN PROGRESS | waits on BLOCKED T-077 (Deps column, session-state "Known dependency gaps"); open: A-P6 stall, root block RF 0.25-0.44, zeta <= 0.05, BOM <= $2,000 | **Partly stale.** Root block RF 0.25-0.44 closed by T-083b/D-229 (min 1.21 at zeta <= 0.05, T084 reproduces); BOM $1,939.17; window / T-W / CG pass. Still true: A-P6 1.3 Vs 17.56 > 17.0 m/s (TP-11), zeta <= 0.05 not yet shown (TP-3 drop test), motor backorder (T-088 / T-093) | Status `BLOCKED` (genuine blocker: December bench TP-3 / TP-11 and motor stock, no more $0 work). Evidence: append "2026-11-23: root block RF closed (T083b: min 1.21, T084: identical); BOM $1,939.17 (T087); remaining blockers TP-3 (zeta <= 0.05), TP-11 (A-P6), X2216 backorder (T-093)"; the Evidence cell also contains the first sentences twice, dedupe. Deps column: change "T-077" to "T-077 (READY FOR REVIEW)". |
| T-061 | FAILED | "v1 REJECTED by opus review (F-1 critical: modelled joint != built joint, 1.4 deg free play); revision in progress" | **Stale.** The revision was done and accepted as T-063 (D-212 rev 3, VERIFIED, `2026-11-18-D212r3-review.md` accept with conditions; AR-001..AR-003 reruns; T-020 mesh linkage-poses 0 pairs over 0.05 mm, AR-007). No "revision in progress" exists. Residual FAIL: CL-A-LINKAGE-FREEPLAY = 1.28 deg vs <= 1 deg (UNVERIFIED inputs, 28 % over), still one of the 12 run_all STRICT FAILs; its closure path (E1 dial-gauge measurement, `analysis-records.md:244`) is NOT in `redesign/qp/A/TEST-PLAN-O4B.md` (only the generic line 34 "horn stall bench" carried) | Status -> `EXPLICITLY DEFERRED`, Evidence append: "2026-11-23: superseded by T-063 (VERIFIED, D-212 rev 3). Residual FAIL CL-A-LINKAGE-FREEPLAY 1.28 deg vs 1 deg (READABLE.md l.4899) carried to a free-play bench measurement (E1 step 7); registered as T-094". Do not leave FAILED (spec 10.3 "do not silently abandon": FAILED with a nonexistent revision is the abandonment). New row: T-094, Parent R-PHY-03 and R-CAD-02, Description "Free-play closure: add a TP-n dial-gauge free-play measurement (and the horn stall bench named at TEST-PLAN l.34) to TEST-PLAN-O4B.md with a numeric pass criterion <= 1 deg (SERVO.md s4) and the order of the specimens; CL-A-LINKAGE-FREEPLAY, CL-A-HORN-*, CL-A-ELEVON-TORSION-FOAM, CL-A-HORN-BEARING-STALL named", Deps T-063, Owner S, Status NOT STARTED. This closes the unowned FAIL set (4 of the 12 run_all FAILs have no TP number). |
| T-076 | BLOCKED | "C6 hub FEA RF 0.94 ... A-P10 79 vs 88 Hz; DAF floor ruling open; CF-in-Al bond; blocked on December coupons" | **Partly stale.** C6 / CF-in-Al sleeve were replaced by D-221 (machined hub) and D-226 (6061 centre node); the DAF floor is applied as max(DAF, 1.5) in T-083 / T-084; A-P10 rebased by T-085 (D-236, TP-10b). Still true: coupons are December (TP-3 pad zeta, TP-4 bond) | Status stays BLOCKED. Evidence append: "2026-11-23 current blockers only: TP-3 (pad zeta <= 0.05), TP-4 (6061 fitting bond / CF-in-Al push-out), TP-10b (cage mode); C6 hub, DAF floor and A-P10 rows superseded by D-221 / D-226 / D-236". |
| T-078 | BLOCKED | purchases not approved, none before early Dec 2026; trunk L/W/H not measured | True (AM-027: team measures the Altima trunk before 1 Dec; Order 1 approval is T-093). | Evidence append: "2026-11-23: Order 1 rebuilt (T-090, $887.25, 21 lines); approval presented in T-093 (1-4 Dec); trunk tape measurement still open". |
| T-015 | BLOCKED | no James definitions in the repo; AM-003 team not done | True; last searched 2026-11-18, AM-003 2026-11-19. | Evidence append the date of the next search; `ls .claude/agents ~/.claude/agents` and note "re-checked 2026-11-23: <result>" at the next milestone (T-048 owner). |
| T-034 | BLOCKED | shared schema not provided | True (AM-003; no later amendment). | none. |
| T-037 | BLOCKED | DaVinci credentials + approval; AM-003 no spend | True. | none. |
| T-004 | IN PROGRESS | evidence "—" | Work is done: T-007 / T-008 headless sessions load CLAUDE.md and name the spec and rules (`2026-11-19-compact-test*.md`, `2026-11-23-recovery-test.md`). Remaining: CLAUDE.md is modified uncommitted (3 lines, mass line updated) and its size before/after (R-REPO-06 acceptance) was never measured | Status -> `READY FOR REVIEW`. Evidence: "headless sessions in T-007 / T-008 report spec path and rules (`docs/audits/2026-11-23-recovery-test.md`); CLAUDE.md size before/after: `git show a93f14da:CLAUDE.md | wc -c` vs `wc -c CLAUDE.md` (to be recorded)"; commit the CLAUDE.md edit. |
| T-038 | IN PROGRESS | evidence "—"; acceptance "no new interface" | A continuing guard; T-039 and T-062 added results only to existing pages. Honest status. | Evidence: append `docs/audits/2026-11-19-recheck-eng.md` (T-062: "no new dashboard"); keep IN PROGRESS until T-047 diff review. |
| T-040 | IN PROGRESS | evidence "—" | **Stale.** The deliverable (`docs/repository-audit.md` s1 baseline with commands, s2 candidates) exists, round 5 reran `git ls-files` counts and checked s1 figures; T-043 and T-045 (VERIFIED) already depend on it. Spec 9.1 item "measure performance metrics" is the only open part (T-051) | Status -> `READY FOR REVIEW`; Evidence: "docs/repository-audit.md s1-s2 (commands shown, initial audit 2026-11-18, a93f14da); round 5 reran the counts (`docs/audits/2026-11-23-review-round-5.md`); performance metrics are T-051". |
| T-088 | IN PROGRESS | stock not shown at Carbonwebshop, Easy Composites US alternative $59.05 | True but the next step cannot start until 1-4 Dec (needs Dillon's cart address): session-state says "T-088 closes with T-093" | Status -> `BLOCKED`, Evidence append "waits for order week (T-093): Carbonwebshop quote or Easy Composites US cart with Dillon's address". |
| T-039 | READY FOR REVIEW | no reviewer yet | Correct; the weekly report file exists (`docs/status/weekly-2026-11-23.html`). | Nobody has reviewed it: include in the next review round; no model-usage row exists for it (docs/model-usage.md, add one). |

### 3.4 Other stale text found
| # | Where | Stale | Fix |
|---|---|---|---|
| F-9 | execution-plan.md "Phases" and "R-id to phase assignment" tables | tasks T-064 .. T-093 (30 tasks) appear in no phase (checked by script: all 30 missing); plan_rid_check passes because it tests R-ids only | Phase 4 row: append "T-064..T-066, T-067..T-071, T-073, T-076, T-077, T-083..T-085, T-089, T-091, T-092"; Phase 6 or a new "4b O4b design + budget" note: T-072, T-074, T-075, T-078..T-082, T-086..T-088, T-090, T-093. Add the same ids to the R-id table "Tasks carrying R-ids" cells (R-GEN-02, R-OPT-*, R-PHY-08/09, R-CAD-03..05 already listed). |
| F-10 | verification-report.md "Milestone audits (T-011, T-048)", lines 31-32 and 69 | "T-048 milestone audits: not run yet" although review rounds 2-5 and 11-19 checks were run | Replace with: "T-048: 2026-11-23 `docs/audits/2026-11-23-milestone-audit.md` (this audit); earlier phase-end reviews: 2026-11-19 setup / recheck files, 2026-11-22 rounds 2-3, 2026-11-23 rounds 4-5". |
| F-11 | session-state.md "Known dependency gaps" | says T-045 IN PROGRESS and phase 1 gate open until T-008 VERIFIED; T-045 and T-008 are VERIFIED COMPLETE (11-23); T-083 waits on T-077 (see above) | Replace the paragraph with the gaps in section 3.3 (T-077, T-083, T-088 order-week, T-094). |
| F-12 | spec-amendments.md header | cites `tools/spec_guard.py --check`; the file is not in `tools/` (only `ledger_audit.py`, `plan_rid_check.py`, `vtol.py`, `opencae-studio`); the seal check is in ledger_audit.py (0 errors) | The header is inside the append-only region, so do not edit; add one line to session-state Reconciliation: "spec-amendments.md header names tools/spec_guard.py; the seal check is tools/ledger_audit.py". |
| F-13 | T-077, T-083 Evidence cells | the same paragraphs repeated up to six times (T-077 about 30 kB) | dedupe as above; makes the row reviewable. |
| F-14 | session-state "Approval gate" | "Pending: Force-remove 3 worktrees ... not yet asked or answered" (answered by AM-029, 2026-11-23, executed: `docs/repository-audit.md` s3 batch 3); "Pending: Board choice O1-O6 (D-216, T-072) not yet answered" (answered AM-005..AM-009; T-072 VERIFIED) | Replace both rows with answered rows: `2026-11-23 | Cleanup batch 3 | AM-029 "Yes, remove them" | 3 worktrees removed, branches kept, about 3.55 GB (repository-audit s3)`; `2026-11-19..21 | Board choice | AM-005, AM-006, AM-009 | O4 then O4b`. Add rows for AM-018 (motor swap), AM-019 (drop spare motor), AM-030 (keep equipment). |

## 4. Work the ledger can still do now (AM-030 "if there is anything more you can do")
Open rows 27 (not VERIFIED). Time- or person-gated: T-015, T-034, T-035, T-036, T-037 (team), T-076, T-078, T-083,
T-088, T-093 (December / Dillon), T-047, T-049, T-059 (program end). Doable now with no purchase and no new sims:
- T-048 and T-055: this audit; move both to READY FOR REVIEW after the conductor applies the fixes (I do not mark them).
- T-050 (forward trade-table rule, deps T-024 VERIFIED): check D-215..D-240 for trade tables and benchmark citations.
- T-051 (agent/software metrics): token counts per delegation are in `docs/model-usage.md`; Explorer startup and memory need one measured run.
- T-053 (Impeccable audit of changed Explorer pages; dep T-029 VERIFIED).
- T-094 (new, free-play / horn test registration in TEST-PLAN-O4B).
- T-016, T-017, T-026, T-074 independent spot-checks (3.2).
- Commit the three modified files (CLAUDE.md, spec-amendments.md AM-030, spec-integrity.sha256); the AM-030 seal line already matches (ledger_audit 0 errors).

## 5. Finding (4): AM-029 and AM-030 reflected?
| Item | R-id | Task | session-state | Other |
|---|---|---|---|---|
| AM-029 (remove 3 worktrees) | cited R-REPO-04 in spec-amendments.md; requirements.md has no AM-029 text | **Yes**: T-042 Evidence cites AM-029 (batch 3, 3.55 GB); `docs/repository-audit.md` s3 and line 47; round 5 verified | **No**: header and Goal say AM-001..AM-028; Approval gate still lists the removal as "Pending"; Reconciliation has no AM-029 entry | spec-amendments.md l.363 present and sealed |
| AM-030 (keep equipment, continue tasks) | cited R-GEN-02, R-COM-01; requirements.md has no AM-030 text | **No**: no task or evidence cell mentions AM-030 | **No**: not mentioned anywhere (grep AM-030: only spec-amendments.md; the file is uncommitted) | TEST-PLAN-O4B.md still lists "force frame >= 5 kN (missing)" for TP-4 / TP-14 without the AM-030 decision text; the lever-rig fallback exists (TP-4 l.268) |

Exact fixes:
1. session-state.md, header "Checkpoint": change "AM-001..AM-028" to "AM-001..AM-030" in the Goal line ("master program (spec + AM-001..AM-028)") and the heading text.
2. session-state.md "Approval gate", add rows: `2026-11-23 | Cleanup batch 3 | AM-029: "Yes, remove them" | 3 line-ending-only worktrees removed with --force, branches kept (repository-audit s3)`; `2026-11-23 | Test equipment | AM-030: "Keep what we have now, ..." | no press rig / testing machine bought; TP-4 / TP-12..14 use a borrowed force frame, else the T-082 lever rig`.
3. session-state.md "Reconciliation", add: `2026-11-23: AM-029 (batch 3 approved and executed, T-042) and AM-030 (keep current equipment; continue every doable task per AM-028) recorded; none lost.`
4. requirements.md, R-GEN-02 Interpretation, append: "AM-029 (worktree removal approval), AM-030 (no test-equipment purchase; borrow a frame, else lever rig)". R-REPO-03 Interpretation append "AM-029 batch 3".
5. task-ledger.md T-082 Evidence (or T-081) append "AM-030 2026-11-23: no press rig or testing machine; TP-4 frame loan else lever rig (TEST-PLAN-O4B l.268, l.278)". TEST-PLAN-O4B.md line 287 ("force frame >= 5 kN (missing)"): add "(AM-030: not bought)".
6. Add task row T-095: Parent R-GEN-02 / R-COM-01, Description "Apply AM-030: execute the doable queue (T-048/T-050/T-051/T-053/T-094) and record equipment decision", Owner C, Status IN PROGRESS. (Optional; T-050/T-051 already cover the work.)
7. Commit: CLAUDE.md, docs/spec-amendments.md, docs/spec-integrity.sha256 are modified and uncommitted; AM-030 exists only in the working tree.

## 6. Summary of defects
| Severity | Count | Ids |
|---|---|---|
| High (status wrong, could mislead the final audit) | 4 | T-077 stale blocker, T-061 FAILED with nonexistent revision (and unowned FREEPLAY / horn FAILs), requirements.md roll-up stale (47 rows), AM-030 absent from ledger / session-state / requirements |
| Medium | 6 | T-016, T-017, T-026, T-074 not independently checked; execution-plan omits T-064..T-093; R-REPO-08 closed despite its own deferral |
| Low | 8 | T-083 / T-040 / T-004 / T-088 status wording, F-10 .. F-14, S-1 .. S-4 |

No VERIFIED COMPLETE row was found with a missing evidence file. No requirement is orphaned. No task has an unknown parent.
