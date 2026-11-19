# Manual compaction test 2 (T-007, R-PRES-11, spec 1.6) — 2026-11-19

Method: Dillon typed `/compact` in desktop session `7cb35b0a` (second controlled manual test; the first, `2026-11-19-compact-test.md`, was 6 PASS / 1 PARTIAL because `docs/execution-plan.md` was not reopened). This record is written by the conductor during recovery, from the commands it ran; it is not independent. Category: process verification.

## Timeline (local, UTC-8)
| Time | Event | Source |
|---|---|---|
| 03:22:58 | PreCompact trigger=manual, missing=none | `docs/session-log.md` |
| 03:24:25 | SessionStart source=compact; PostCompact trigger=manual | `docs/session-log.md` |
| after 03:24 | Recovery steps 1-11 of `docs/session-state.md`, in order, before any engineering work | commands below |

## Recovery steps run
1. `CLAUDE.md` re-attached as project instructions (auto). 2. `docs/MASTER_PROJECT_SPEC.md` read in full (1,173 lines, Part 1 to Immediate Execution Instructions). 3-4. Requirements registry: 109 `| R-` rows. 5. Ledger open rows listed (IN PROGRESS, BLOCKED, FAILED, READY). 6. `docs/execution-plan.md` read in full. 7. `docs/session-state.md` read. 9. `ledger_audit.py`, `plan_rid_check.py`, seal hashes. 11. Resumed with the T-065 hand-back.

## The seven checks (spec 1.6)
| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Spec exists | PASS | `sha256sum docs/MASTER_PROJECT_SPEC.md` = `2a9eb239…9b2d`, equal to `docs/spec-integrity.sha256`; `spec-amendments.md` `6d3ae65d…a079` equal to its seal line; spec read in full after compaction |
| 2 | Instructions reload | PASS | `CLAUDE.md` attached after the boundary; SessionStart(compact) brief injected ("a compaction summary is NOT authoritative") |
| 3 | Active task identified | PASS | hook brief lists the IN PROGRESS rows (T-004, T-007, T-038, T-040, T-045); compaction summary section 7 names the three running agents (D-213 review, T-065, T-022); the T-065 hand-back arrived and was matched to its ledger row |
| 4 | Statuses kept | PASS | hook brief: VERIFIED 34, READY 4, IN PROGRESS 5, NOT STARTED 18, BLOCKED 3, FAILED 1 (65 tasks); `ledger_audit.py` after recovery: identical, 0 errors; same as the counts recorded before compaction |
| 5 | Execution plan recoverable | PASS | `docs/execution-plan.md` opened and read in full (phases, routing, task protocol, R-id map); `python -I tools/plan_rid_check.py`: "109 R-ids, 0 missing from execution-plan.md" |
| 6 | IDs intact | PASS | 109 R-ids, 65 T-ids; audit 0 errors |
| 7 | Work resumes | PASS | next actions taken from disk state: this record, then T-065 (AR-013), then the pending D-213 and T-022 results |

## Finding (reconciliation, step 10)
`docs/session-state.md` checkpoint was stale at compaction: it still said "63 T", "running: implementer m-3..m-9" and did not name T-064/T-065, AM-004 or the three running agents. The compaction summary carried them, so nothing was lost this time, but the checkpoint is the authority and must be current. Fixed in the same commit as this record (checkpoint rewritten).

## Verdict
7 of 7 PASS, with the stale-checkpoint finding fixed. Not independent: T-007 stays READY FOR REVIEW until a different agent checks this record against `docs/session-log.md`, the seal file and the audit output.
