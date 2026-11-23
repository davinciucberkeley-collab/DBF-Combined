# Execution plan — master program

Spec: `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`). Requirements: `requirements.md`. Tasks: `task-ledger.md`.
Checkpoint: `session-state.md`. Phases follow spec Part 11; dependencies are the ledger's Deps column.

## Phases
| Phase | Tasks | Gate to leave the phase |
|---|---|---|
| 1 Preservation + audit | T-001…T-014, T-016, T-040, T-046, T-052, T-054, T-060 | spec sealed; hooks tested (T-007, T-008); haiku registry audit (T-011) clean |
| 2 Initial repo optimization | T-041…T-045 (dry-run, then approved batches) | Dillon approves deletions; regression green |
| 3 Orchestration | T-013, T-014, T-015, T-048, T-051, T-055 | one routed agent run per tier logged |
| 4 Mechanical engineering | T-016…T-025, T-050, T-056…T-058, T-061, T-063, T-064…T-066, T-067…T-071, T-073, T-076, T-077, T-083…T-085, T-089, T-091, T-092, T-094 | kinematic + dynamic + swept-collision records; O review |
| 4b O4b design + budget | T-072, T-074, T-075, T-078…T-082, T-086…T-088, T-090, T-093 | go/no-go 2026-12-15 (AM-016); Order 1 approved by Dillon in order week (T-093) |
| 5 Video | T-026…T-033 | preview reviewed → full render → playback + visual sign-off |
| 6 Team integration | T-034…T-039, T-053, T-062 | blocked items resolved or recorded |
| 7 Final optimization | T-042…T-045 rerun, T-049 | final audit; benchmarks before/after |
| 8 Final verification | T-047, T-059 | O reviewer per-requirement table |

Phases 4 and 5 share one dependency (T-018 drives the film's mechanism motion); 2, 4 and 5 can otherwise run in
parallel in separate worktrees. Phase 6 waits on team inputs (schema, DaVinci access).

## Model routing (R-ORC-01)
| Work | Agent (`.claude/agents/`) | Model |
|---|---|---|
| File inspection, inventories, ledger accounting, test runs, docs | `ledger-auditor`, `runner` | haiku |
| CAD features, mechanism/sim scripts, render pipeline, CLI, moderate analysis | `implementer` | sonnet |
| Architecture, hard trade-offs, root cause after 2 failed attempts, independent engineering/film/final review | `eng-reviewer` | opus |
Escalate one tier after two failed attempts with different approaches; log the escalation in `model-usage.md`.

## Task protocol (R-TRK-04)
Before: ledger row exists with parent R-id, deps met, deliverable, acceptance test, owner → status IN PROGRESS.
Brief to a subagent contains: task ID, parent R-ids, files in scope, acceptance test, evidence path to write,
and the return format below. After: conductor opens the evidence, reruns the acceptance test (or has a
different agent run it), records evidence, then READY FOR REVIEW → VERIFIED COMPLETE only after an independent check.
Partial completion: unfinished parts stay as a new or reopened row.

Subagent return format (AM-001): `Task: T-nnn | Outcome: … | Verification: <what was run, result> | Evidence: <path> | Blocker: <none|…>`.
Details go to the evidence file, not the reply.

## Delegation rules (R-ORC-03)
Plan first; split into independent units; cheapest capable model; parallel only on disjoint files; code-writing
agents in worktrees; evidence-backed reports; escalate on repeated failure; diagnose before retry; independent review of
engineering changes; merge only on met acceptance; ledger status survives handoffs.

## Stall and failure rules (R-MON-02, R-MON-03)
Long jobs (collision gate ~17 min, renders) run in the background with a stated expected duration; > 2× expected = stalled →
inspect logs, not restart. Same error twice = structural → change approach or escalate. Every FAILED row gets a
diagnosis line in `session-state.md` "Failed attempts".

## Failure recovery (spec 10.3, R-MON-03; nine steps)
When a process fails, in this order (spec 10.3 "Recover intelligently"):
1. Identify the specific failure: the command, file or claim that failed and the exact message, not "it did not work".
2. Decide whether it is transient (network, lock, timeout, a one-off tool refusal) or structural (same error twice, a wrong model of the problem).
3. Inspect the relevant logs and artifacts (job output, `session-log.md`, evidence files, `git diff`) before acting.
4. Do not repeat an identical unsuccessful attempt; a retry must differ in something named.
5. Revise the approach: apply the ladder in `engineering-decisions.md` (subtract, modify, rearrange, change approach, add) and, for design changes, a trade table.
6. Escalate to a more capable model only if justified (two failed attempts with different approaches, or a high-impact judgement), and log the escalation in `model-usage.md`.
7. Preserve the task's original requirements: the revised approach is checked against the same R-ids and acceptance test; the test is never loosened to make it pass.
8. Verify the recovery: rerun the acceptance test (or have a different agent run it) and keep the output as evidence.
9. Record the resolution: a diagnosis line in `session-state.md` "Failed attempts", the ledger row status and evidence, and `redesign/params/CHANGE-LOG.md` for design decisions.
Failed tasks are never silently abandoned (spec 10.3): a task that cannot be recovered stays as a FAILED or BLOCKED row with its diagnosis, or is reopened as a new row.

## R-id to phase assignment (T-046, R-PLAN-01)
Each requirement is assigned to the phase of the task(s) that carry it in `task-ledger.md` (Parent column). A requirement carried by tasks in two phases appears in both; the first listed is its primary phase. Generated from the ledger on 2026-11-19; the check below must print 0 missing.

| Phase | Tasks carrying R-ids | R-ids |
|---|---|---|
| 1 Preservation + audit | T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-008, T-009, T-010, T-011, T-012, T-040, T-046, T-052, T-054, T-060 | R-PRES-01, R-PRES-02, R-RULE-01, R-PRES-03, R-PRES-04, R-REPO-06, R-COM-01, R-COM-02, R-COM-04, R-COM-05, R-COM-06, R-PRES-05, R-MON-01, R-MON-04, R-PRES-10, R-PRES-06, R-PRES-07, R-PRES-08, R-PRES-09, R-PRES-11, R-PRES-12, R-TRK-01, R-TRK-02, R-TRK-03, R-TRK-05, R-TRK-04, R-TRK-06, R-ORC-03, R-MON-02, R-MON-03, R-REPO-01, R-REPO-10, R-PLAN-01, R-PRES-13, R-GEN-02, R-PHY-11 |
| 2 Initial repo optimization | T-041, T-042, T-043, T-044, T-045 | R-REPO-02, R-REPO-03, R-REPO-04, R-REPO-07, R-REPO-05, R-RULE-08, R-REPO-08, R-REPO-09, R-GEN-05 |
| 3 Orchestration | T-013, T-014, T-015, T-048, T-051, T-055 | R-ORC-01, R-ORC-02, R-COM-03, R-ORC-05, R-RULE-04, R-ORC-04, R-TRK-05, R-REPO-05, R-GEN-04 |
| 4 Mechanical engineering | T-016, T-017, T-018, T-019, T-020, T-021, T-022, T-023, T-024, T-025, T-050, T-056, T-057, T-058, T-061, T-063, T-064, T-065, T-066, T-067, T-068, T-069, T-070, T-071, T-073, T-076, T-077, T-083, T-084, T-085, T-089, T-091, T-092, T-094 | R-CAD-01, R-PHY-01, R-PHY-02, R-CAD-02, R-PHY-03, R-PHY-04, R-PHY-05, R-PHY-07, R-PHY-06, R-CAD-03, R-CAD-04, R-CAD-05, R-CAD-06, R-OPT-01, R-RULE-06, R-OPT-02, R-OPT-03, R-OPT-04, R-OPT-05, R-PHY-08, R-PHY-09, R-PHY-10 |
| 4b O4b design + budget | T-072, T-074, T-075, T-078, T-079, T-080, T-081, T-082, T-086, T-087, T-088, T-090, T-093 | R-GEN-02, R-GEN-06, R-GEN-07, R-GEN-08, R-OPT-01, R-OPT-02, R-OPT-05, R-PLAN-01, R-PHY-08, R-PHY-09, R-CAD-04 |
| 5 Video | T-026, T-027, T-028, T-029, T-030, T-031, T-032, T-033 | R-VID-01, R-VID-02, R-VID-04, R-VID-05, R-VID-09, R-RULE-05, R-VID-08, R-VID-10, R-VID-03, R-VID-07, R-VID-11, R-VID-12, R-VID-13, R-VID-06, R-VID-14, R-VID-15, R-RULE-10 |
| 6 Team integration | T-034, T-035, T-036, T-037, T-038, T-039, T-053, T-062 | R-INT-01, R-INT-02, R-INT-03, R-INT-04, R-INT-05, R-RULE-07, R-INT-06, R-GEN-01, R-GEN-03 |
| 7 Final optimization | T-049 | R-REPO-10, R-REPO-08 |
| 8 Final verification | T-047, T-059 | R-VER-01, R-VER-02, R-VER-03, R-VER-04, R-VER-05, R-VER-06, R-RULE-02, R-RULE-03, R-RULE-09, R-DEL-01, R-GEN-05, R-GEN-06 |

Placement notes: T-016 (listed under phase 1 in the table above for its inventory use) is carried in phase 4 for its R-ids; T-013 and T-014 build the agent routing and the usage log and are carried in phase 3; T-042…T-045 are carried in phase 2 and rerun in phase 7 (R-ids not repeated); T-050 (forward rule for mechanism decisions), T-056…T-058, T-061 and T-063 (D-212 linkage fix) and the physics analyses sit in phase 4; T-052, T-054 and T-060 (PD-005) are phase 1 housekeeping; T-062 (refresh Explorer numbers, R-INT-05) is phase 6 with T-038; T-051 and T-055 are phase 3 monitoring.

Check (spec 11, R-PLAN-01): every R-id in `requirements.md` appears in the table above:
`python -I tools/plan_rid_check.py` (reads both files; prints the missing ids and exits 1 if any).

## Standing constraints carried in
- CLAUDE.md hard constraints (budget, schedule, trunk, 3-D gates, CAD fidelity, enclosed wiring).
- Memory "no sims until final" (Dillon, 11-14…11-16) vs spec Part 5 (11-18) → see `engineering-decisions.md` PD-002.
- No purchases before early Dec 2026; DaVinci API spend needs Dillon's approval.
