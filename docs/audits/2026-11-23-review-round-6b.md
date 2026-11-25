# Independent review round 6B (2026-11-23, HEAD 3bf00f72)

Category: records review (not an engineering analysis). Reviewer did not write the work. Read-only except this file. No ledger edit; nothing marked VERIFIED COMPLETE. Spec and amendments untouched.

## Verdicts

| Row | Verdict |
|---|---|
| T-004 | PASS WITH FIXES |
| T-039 | PASS WITH FIXES |
| T-040 | PASS |
| T-048 | PASS WITH FIXES |
| T-055 | PASS |
| T-050 | FAIL (acceptance not met; row must not go VERIFIED COMPLETE as written) |
| T-051 | PASS WITH FIXES |

## Reruns (this session)
- `python -I tools/ledger_audit.py`: exit 0, 113 requirements, 94 tasks, {VC 62, RFR 12, BLOCKED 7, NOT STARTED 8, IN PROGRESS 1, DEFERRED 4}; 0 errors.
- `python -I tools/plan_rid_check.py`: 113 R-ids, 0 missing.
- `python -I docs/audits/2026-11-23-rollup_check.py`: 6 mismatches (R-GEN-01, R-GEN-08, R-PHY-05, R-RULE-02, -03, -09), identical to the 6 listed in `docs/audits/2026-11-23-milestone-fixes.md` "Roll-up recompute" (documented as deliberate).
- `python -I docs/audits/2026-11-23-T051-metrics.py`: rc 0, see T-051.

## T-004 (CLAUDE.md) PASS WITH FIXES
Evidence checked: `CLAUDE.md` (7,899 B, matches `wc -c`), `docs/audits/2026-11-23-recovery-test.md`, session-state, CHANGE-LOG D-235..D-241.
- Accurate: spec pointer, ledger/state files, AM-001 communication block, subagent models (`.claude/agents/*.md`: eng-reviewer opus, implementer sonnet, ledger-auditor/runner haiku), O4b line (BOM $1,939.17 D-235, 1.88 kg EST, X2216 D-227, go/no-go 2026-12-15) agree with session-state l.26-27 and D-235.
- F-1 (acceptance evidence gap, medium). Acceptance is "a headless session reports the rules and the spec path". `recovery-test.md` is a no-context haiku subagent (not `claude -p`), run before the last CLAUDE.md edit (commit 9fd6af83), and it quotes only the spec path and next action, not the communication rules. `docs/audits/2026-11-19-compact-test.md` l.18 shows only AM-001 behaviour. `docs/audits/2026-11-19-setup-check.md` l.12 says T-004 "CANNOT CHECK" (needs a logged-in headless `claude -p`). Fix: run one `claude -p "report the spec path and the communication rules you were given"` (or a fresh subagent asked that question) against the current CLAUDE.md, save the transcript line to `docs/audits/`, cite it in the T-004 Evidence cell.
- F-2 (stale/duplicate content, low). `CLAUDE.md:36-39` still says "lifeboat: the ZOHD Altus VTOL kit" and the whole K09-L paragraph, contradicting AM-008 two paragraphs above (flagged "withdrawn" at l.26 only). R-PRES-04 says keep concise. Fix: delete or strike the lifeboat clause at l.38-39 (replace by "lifeboat withdrawn, AM-008"); optionally move the K09-L history to `docs/` and leave one line.
- F-3 (low). CLAUDE.md does not name AM-028 (no "continue?" prompts) or AM-030; recovery works without them via session-state, so optional.

## T-039 (weekly report) PASS WITH FIXES
Numbers checked against HEAD~ (4f4a2b81 ledger) and sources: 66 VC / 93 tasks = true at 4f4a2b81 (66/5/6/1/3 match); $1,939.17, margin $60.83, 1.881 kg, 129 parts + 66 steps (`mechanism/out/T092_report.md` l.17), 12 FAILs (T092_report l.18), exposed 0.597 m (T084_report l.187), Order 1 $887.25 (SCHEDULE-A l.23), main order $1,051.92 (T090_report l.17), D-237/D-239/D-240 text match CHANGE-LOG. All match at the time.
- F-1 (medium). "12 not started" is wrong at 4f4a2b81: the ledger then had 11 NOT STARTED + 1 READY FOR REVIEW (T-039 itself). Fix: "11 not started, 1 ready for review" or say 12 incl. this report.
- F-2 (medium). The page is now stale: the milestone fixes moved 4 rows (T-016, T-017, T-026, T-074 per milestone-fixes s3.2) from VERIFIED COMPLETE to READY FOR REVIEW, T-061 FAILED to DEFERRED, and added T-094. The 66 included rows lacking independent evidence. Ledger today: 62 / 94, 1 IN PROGRESS, 0 FAILED, 4 DEFERRED. Fix: either regenerate the page (62 / 94; 12 ready for review; 7 blocked; 8 not started; 1 in progress; 4 deferred; 0 failed) or add a "superseded by 2026-11-23 milestone audit" line; and update the T-039 Evidence cell (artifact "version 31" is not checkable in the repo).
- Note: "12 FAILs" vs `proofs/out/graph.json` meta `fails: 16` (duplicates of the same claims via the STRICT A-P rows; the 12 distinct claims list in T092_report l.18). State "12 distinct claims" on the page.

## T-040 (repository-audit s1-s2) PASS
Reran against a93f14da (the stated baseline commit): `git ls-tree -r -l a93f14da` = 13,798 files, 1,489.25 MB (page: 1 489 MB, 13 798 files); `redesign` 1,355 MB with qp 471.6, showcase 314.9, team 212.2 (page 472/315/212); 52 `.BIN` files, 447.2 MB (page: 52, 447). `git count-objects`: packs 4, in-pack 22,407, size-pack 1.51 GiB match; loose is now 6,677 / 745 MiB vs the page's 2,451 / 524 MiB (loose objects grew since; the page is a dated baseline). HEAD is now 15,290 files / 1,065 MB after cleanup.
- F-1 (low). s1 does not say its loose-object and `du -sh .` (14 GB, 9 worktrees) rows are as of 2026-11-18 and no longer reproducible (worktrees removed, 3.55 GB). Fix: add "as of a93f14da, 2026-11-18" to the table header; s3-s12 carry the post-cleanup numbers.

## T-048 / T-055 (milestone audit and fixes) T-048 PASS WITH FIXES, T-055 PASS
- Full-spec read is stated at `2026-11-23-milestone-audit.md:8` (1,173 lines, matches the spec line count); `verification-report.md` l.32 and l.69 carry the dated entry. T-055 acceptance met.
- Spot check of 12 roll-up flips against the recomputed ledger (rollup_check expected == requirements.md): R-PRES-01, R-PRES-11, R-CAD-06, R-PHY-04, R-PHY-06, R-PHY-11, R-OPT-03, R-REPO-02, R-VID-14, R-ORC-02, R-ORC-05, R-TRK-01 all VERIFIED COMPLETE, all carrying tasks VERIFIED COMPLETE; R-VID-01 -> IN PROGRESS (T-026 READY FOR REVIEW), R-TRK-05 and R-GEN-04 IN PROGRESS (T-048, T-055 READY FOR REVIEW). All match.
- T-061: EXPLICITLY DEFERRED, superseded by T-063, residual CL-A-LINKAGE-FREEPLAY 1.28 deg carried to T-094 (matches READABLE.md / graph.json: FAILS 1.28 deg vs 1). T-094: NOT STARTED, acceptance numeric (<= 1 deg, four CL-A ids named). T-077, T-083, T-088: duplicates removed, statuses (RFR, BLOCKED, BLOCKED) match session-state; Deps of T-083 reads "T-077 (READY FOR REVIEW)".
- F-1 (medium). R-PHY-05 stays IN PROGRESS (roll-up says VERIFIED COMPLETE because T-061 is DEFERRED), but no open task carries R-PHY-05: T-094's Parent is `R-PHY-03, R-CAD-02`. The row is IN PROGRESS with nothing that can close it. Fix: add R-PHY-05 to T-094 column 1 (`docs/task-ledger.md:104`) so the open status has an owner (then the rollup check shows 5 mismatches, all documented).
- F-2 (low). R-GEN-08 / T-083 BLOCKED vs IN PROGRESS and the three R-RULE rows are deliberate; instead of leaving them as unexplained script mismatches, add R-RULE-02/-03/-09 to the STANDING set at `docs/audits/2026-11-23-rollup_check.py:11` and R-GEN-01 to it so the script exits 0 (leaving 2 genuine judgement rows).
- F-3 (low). `2026-11-23-milestone-fixes.md` Gates line shows READY FOR REVIEW 11 / IN PROGRESS 2; ledger now 12 / 1 (T-051 moved). Fix: note "at time of writing" or refresh.
- The fix list was applied as written for every row spot-checked (ledger Evidence cells for T-004, T-040, T-048, T-050, T-051, T-055, T-077, T-083, T-088 carry the fix text; no row marked VERIFIED COMPLETE by the fix pass).

## T-050 (benchmark rule) FAIL as VERIFIABLE
Checked: `docs/audits/2026-11-23-T050-dentries.md` (33 ids D-208..D-240: 13 GAP, 20 N/A, 0 COMPLY), `-benchmarks.md`, CHANGE-LOG D-241 (l.949).
- Sources fetched (curl, 2026-11-23, HTTP 200): (1) ArduPilot "Mounting the Autopilot": contains "IMU position offset parameters", supports D-239; (2) arXiv 2509.09024: "260 g, making it 10% lighter than the commercial DJI F450 frame", as cited; (3) Wikibooks RC Airplane control surfaces: "solid so that a control horn can be attached"; also Model Aviation node/145 opens and describes foam-core stressed-skin torsion strength (the +-45 deg sentence was not located in the fetched text; the cited claim "45 deg raises torsional stiffness" is unconfirmed by this check). All cited with URL and read date. No fabrication found; the weak sources are flagged by the author.
- F-1 (high). The acceptance "all D-entries after 2026-11-18 comply" is not met and cannot be VERIFIED: D-229, D-225 (printed saddle) and D-215 (UHMW pad friction) have "no benchmark found"; D-212 rev 3, D-220, D-221 rest on weak sources (a generic wiki, a vendor blog, a preprint with a different process); D-210/D-225 trade tables are retrospective and rows (d)-(f) of D-210 are "not computed".
- F-2 (high). The benchmark lines are proposals ("the CHANGE-LOG owner appends the one-line texts", `-benchmarks.md` header). CHANGE-LOG D-241 summarises them, but the per-entry `Benchmark (6.4):` lines were not appended to D-210..D-239 (`grep -c "Benchmark (6.4)" redesign/params/CHANGE-LOG.md` = 2, D-212 rows only). The rule is "decisions carry" the citation; the entries do not.
- F-3 (medium). Acceptance text is a standing forward rule ("check new D-entries at each milestone"); a one-time check cannot close it.
- What the row should be: not VERIFIED COMPLETE. Set to IN PROGRESS (not READY FOR REVIEW) with the residual list: (a) append the 10 proposed benchmark lines into their CHANGE-LOG rows; (b) for D-229, D-225, D-215 record "benchmark searched, none found" with the search terms plus the named test that substitutes (TP-4 / TP-9), and have the conductor either amend the acceptance via a logged decision to "each M/S decision cites a benchmark or a documented negative search" (an acceptance change needs its own D-entry and independent review, so do not do it silently) or find a benchmark; (c) re-run the D-entry check at the next milestone (D-241 itself and later). R-OPT-02 / R-OPT-04 stay IN PROGRESS meanwhile (they are, per the roll-up).

## T-051 (metrics) PASS WITH FIXES
Reran `python -I docs/audits/2026-11-23-T051-metrics.py`: rc 0. Token and minute tables agree with the md (19,937 k total tokens, mean 221.5, median 191.5, 4,154.6 min, 18.4 k/min; by model/agent tables identical). Differences from the written report:
- F-1 (medium). The script now finds 111 rows (md says 110), "none" model group 2 rows (md 1), retries recorded on 76 rows with a rerun rate of 3.9 % (md 75, 4.0 %), because `docs/model-usage.md` gained a row (milestone-fixes lists a T-039 row at model-usage l.117) after the md was written. Fix: rerun the script and refresh the headline (`T051-metrics.md:12`, `:65-67`, by-model "none" row) or state "as of the 110th row". Token statistics unaffected (the new row has no numbers).
- F-2 (low). The script prints a `�` (cp1252) for the em dash unless run with `-X utf8`; the md uses the same command with `-X utf8` (l.7) but the acceptance command in the ledger omits it. Fix: add `-X utf8` or `sys.stdout.reconfigure(encoding="utf-8")` in the script.
- Explorer first-load and memory (s2-s4) are not re-measured by this review; s2 is explicitly copied from the T-043/T-044 file and s4 measured by a scratchpad helper not in the repo (reproducibility gap, low).

## Fixes applied (2026-11-23, conductor decisions; rounds 6a and 6b)

Category: records edits (no engineering analysis). Nothing committed. Gates after the edits: `python -I tools/ledger_audit.py` exit 0 (113 requirements, 94 tasks, VERIFIED COMPLETE 71, READY FOR REVIEW 3, BLOCKED 7, NOT STARTED 7, IN PROGRESS 2, EXPLICITLY DEFERRED 4); `python -I tools/plan_rid_check.py` exit 0 (113 R-ids, 0 missing); `python -I docs/audits/2026-11-23-rollup_check.py` exit 0 (0 mismatches; R-GEN-08 printed as an explained judgement row).

| Finding | Fix | File:line |
|---|---|---|
| 6b T-004 F-2 | Lifeboat clause replaced by "lifeboat withdrawn (AM-008)"; K09-L paragraph shortened to one line pointing to `redesign/CONFIGURATION.md`; line 26 "named below" removed | `CLAUDE.md:27`, `:40`, `:42` (7,402 B) |
| 6b T-004 F-3 | One "Standing rules: AM-028, AM-030" line added | `CLAUDE.md:24` |
| 6b T-004 F-1 | Left for the conductor (fresh-session test); T-004 stays READY FOR REVIEW, Evidence notes the F-2/F-3 edits | `docs/task-ledger.md:14` |
| 6b T-039 F-1/F-2 | Left for the conductor (status page republish); T-039 stays READY FOR REVIEW | `docs/task-ledger.md:49` |
| 6b T-040 F-1 | s1 table header states "as of a93f14da, 2026-11-18" and that two rows are no longer reproducible | `docs/repository-audit.md:7` |
| 6b T-048 F-1 | R-PHY-05 added to T-094 Parent | `docs/task-ledger.md:104` |
| 6b T-048 F-2 | STANDING set adds R-RULE-02/-03/-09 and R-GEN-01; JUDGEMENT dict explains R-GEN-08; script exits 0 | `docs/audits/2026-11-23-rollup_check.py:10-13` and the main block |
| 6b T-048 F-3 | Gates line dated "at time of writing" | `docs/audits/2026-11-23-milestone-fixes.md:178` |
| 6b T-050 F-2 | 13 one-line "Benchmark (6.4, added 2026-11-23, D-241):" texts appended to the Decision cell of D-210, D-212 rev 3, D-213, D-215, D-216, D-220, D-221, D-224, D-225, D-226, D-229, D-233, D-239 (D-225 and D-229 read "none found ..."); no other text changed, columns intact | `redesign/params/CHANGE-LOG.md:909, 913, 921, 923, 924, 928, 929, 932, 933, 934, 937, 941, 947` |
| 6b T-050 F-1/F-3 | Status IN PROGRESS; Evidence appended (standing rule, 10 of 13 cited with 3 weak, none found for D-229, D-225 printed saddle, D-215 pad friction); acceptance rewording not done (needs its own D-entry and independent review) | `docs/task-ledger.md:60` |
| 6b T-051 F-1 | Script rerun; md refreshed to 111 rows, 21 without numbers, "none" model 2 rows, conductor (Opus) rows, 2026-11-23 date row 9 / 8 / 1, 76 retries rows, 3.9 % | `docs/audits/2026-11-23-T051-metrics.md:12, 24, 36, 50, 61, 69, 82` (approx.; found by grep) |
| 6b T-051 F-2 | `sys.stdout.reconfigure(encoding="utf-8")` added; command line in the md no longer needs `-X utf8` | `docs/audits/2026-11-23-T051-metrics.py:6`, `...metrics.md:9` |
| 6a F-6 | Full-repo grep and residual classes appended to T-017 Evidence | `docs/task-ledger.md:27` |
| 6a F-8 | R-VID-01 verification cell notes the O read | `docs/requirements.md:102` |
| 6a F-10/F-11 | Conditions and RDQ 2800 mAh note appended to T-074 Evidence | `docs/task-ledger.md:84` |
| 6a F-13/F-14/F-15 | T-077 Evidence states 3-D, wire and drawing gates PASS; build_a fails only the allowed mass gate (AM-011 / R-GEN-08); run_all 12 STRICT FAILs plus UNVERIFIED A-P13 flutter; window figures cited to T-084 | `docs/task-ledger.md:87` |
| Status flips | T-016, T-017, T-026, T-074, T-077, T-040, T-048, T-051, T-055 -> VERIFIED COMPLETE with evidence "2026-11-23 review round 6a/6b ... fixes applied" | `docs/task-ledger.md:26, 27, 36, 50, 58, 61, 65, 84, 87` |
| Roll-up | R-GEN-04, R-TRK-05, R-CAD-01, R-CAD-05, R-PHY-01, R-PHY-02, R-VID-01, R-REPO-01, R-REPO-05 -> VERIFIED COMPLETE (found by rollup_check.py) | `docs/requirements.md:40, 53, 68, 72, 78, 79, 102, 131, 135` |
| 6a F-1..F-5, F-3 | Already done by the conductor before this pass (capability-audit.md, T022-decisions.md, STOP_CHECK.md); left as is | n/a |

Not applied: 6b T-004 F-1 and T-039 F-1/F-2 (conductor). Placement choice: the benchmark text sits in the Decision cell (the cell holding the entry's text), not in the last cell (Re-check / Basis), so the columns are unchanged.
