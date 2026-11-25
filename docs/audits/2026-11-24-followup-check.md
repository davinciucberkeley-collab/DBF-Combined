# Follow-up check R-MON-01 / R-GEN-01 (2026-11-24)

Reviewer: fresh reviewer instance (opus). HEAD 7cbaa3f9 = origin/redesign/v1 (`git rev-parse`, after `git fetch`).
I wrote this file instead of `docs/verification-report.md`. The reviewer role writes only under `reviews/`, and
`docs/reference/agent-standard/LOCAL.md` maps that folder to `docs/audits/`. The conductor can paste it.

## Validators

```
python -I tools/ledger_audit.py
113 requirements, 105 tasks, {'VERIFIED COMPLETE': 92, 'BLOCKED': 5, 'EXPLICITLY DEFERRED': 5, 'IN PROGRESS': 2, 'NOT STARTED': 1}; 0 errors
git log --oneline -1 origin/redesign/v1  ->  7cbaa3f9 T-047 / T-049 / T-059 final verification (design phase); ...
```

I did not run the physics, CAD or BOM validators. Neither item depends on them.

Requirement-status count, from `grep` on the last column of `docs/requirements.md`: 100 VERIFIED COMPLETE, 7 IN PROGRESS,
5 BLOCKED and 1 EXPLICITLY DEFERRED (113 in total).

## R-MON-01: FAIL

The criterion is the requirements.md row R-MON-01: "Persist active tasks, agents, state, deps, progress, errors, blocks
outside conversation". Its acceptance is "Updated at each milestone", and it is checked by reading.

| Check | Result | Reason |
|---|---|---|
| Task counts against ledger_audit | PASS | 105 tasks and 92 VERIFIED COMPLETE agree with the audit output. |
| Requirement count | FAIL | session-state.md says "99 VERIFIED COMPLETE after T-047". requirements.md now has 100. |
| Push record against `git log origin/redesign/v1` | FAIL | The checkpoint line says "Pushed ... four times, latest 71cab7a2". Origin is at 7cbaa3f9. The approval-gate table has no row for the 71cab7a2..7cbaa3f9 push, so that push has no recorded approval (R-GEN-02, T-054). |
| Checkpoint header | FAIL | The header still reads "Checkpoint — 2026-11-23 ... AM-001..AM-030 in force". The amendments now run to AM-050, as T-047 read them. |
| Stale contradictory line | FAIL | "Resumed 2026-11-22 (AM-027) ... Nothing pushed." is still present, and it contradicts the push rows below it. |
| Next action is current | PASS (with a note) | Steps (1)-(3) are marked done. Steps (4) DaVinci branch deletion (AM-050) and (5) T-093 on 1-4 Dec are the real next actions. Note: the open-item numbers in the file differ from CLAUDE.md. The file has CL-A-PITCH-USE 0.651 and A-P6 17.56 m/s. CLAUDE.md has 0.69-0.79 and 17.74 m/s. One of the two is stale. |
| Open items and blocks named | PASS | BLOCKED T-034, T-035, T-036, T-083 and T-088 are named, along with T-094 NOT STARTED and T-037 IN PROGRESS. These match the ledger rows that are not closed. |
| Agents recorded (model-usage, audit files) | FAIL | `docs/model-usage.md` has no row for the 7cbaa3f9 work: T-047 final verification, T-059, T-049, and the Impeccable finish review with its fix pass (`grep` for T-047, T-049, T-059 and Impeccable finds nothing). The T-047 audit file itself names its agent ("fresh reviewer instance (opus)"). Several 11-23 and 11-24 rows give the model as "— (not recorded)". This is logged as a backfill, but the agent model is still not persisted. |

The fix: update the checkpoint header, the counts, the push line and the approval-gate row for 7cbaa3f9, or record
that it was pushed without approval. Remove the "Nothing pushed" line. Add model-usage rows for T-047, T-049, T-059 and
the Impeccable review. Reconcile the PITCH-USE and A-P6 numbers with CLAUDE.md.

## R-GEN-01: FAIL

The criterion is the requirements.md row R-GEN-01. Its acceptance is "Phase plans name the skill used; one Impeccable
audit of changed pages", checked against "session-state + audit file".

| Part | Result | Reason |
|---|---|---|
| One Impeccable audit of changed pages | PASS | `docs/audits/2026-11-24-impeccable-replays-review.md` reviews the changed #sims replays. "Fixes applied" lists 8 fixes with headless-Chrome check output (`fail: []`). Fix 3 is "applied in part". The fixes were checked in the same file and not by a separate instance. |
| Phase plans name the skill used | FAIL | The `docs/execution-plan.md` Phases table (line 7) has the columns Phase / Tasks / Gate, with no skill column. No phase names a skill. "Skills used" (lines 92-97) is a single section added on 2026-11-24. It says the Agent Standard "replaces" Superpowers' development and dispatching patterns, and it leaves the question to the reviewer. It names no Superpowers skill per phase for planning, implementation or testing, apart from using-superpowers loading at start and verification-before-completion "in practice". |
| AM-040 / "other tools when better" | Does not rescue the row | Spec line 27 allows "other proven tools or skills when they provide a meaningful advantage". AM-040 makes the Agent Standard mandatory. Together they can justify replacing Superpowers. They do not remove the acceptance text, and the plan states no advantage. It says only that AM-040 requires the standard. |

The fix, which is one of two: (a) add a skill column to the Phases table, naming per phase the skill or the Agent
Standard role and the advantage that justifies it under spec line 27; or (b) log an amendment or decision that re-words
R-GEN-01's acceptance to the Agent Standard, and cite AM-040.

## Process

There is no `plans/agent-log.jsonl` in this repo. `docs/model-usage.md` takes its place (LOCAL.md mapping). Process
miss: as noted under R-MON-01, the agents behind commit 7cbaa3f9 are not logged there.

## Non-blocking suggestions

- Simpler: session-state.md repeats counts that ledger_audit prints. Point to the audit command instead of copying the
  numbers, so they cannot go stale.
- Remove: the "Resumed 2026-11-22 ... Nothing pushed" paragraph and the long approval-gate notes paragraph. Move the
  notes to `docs/audits/2026-11-19-recheck-docs.md`, which they already cite.
