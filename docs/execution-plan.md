# Execution plan — master program

Spec: `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`). Requirements: `requirements.md`. Tasks: `task-ledger.md`.
Checkpoint: `session-state.md`. Phases follow spec Part 11; dependencies are the ledger's Deps column.

## Phases
| Phase | Tasks | Gate to leave the phase |
|---|---|---|
| 1 Preservation + audit | T-001…T-014, T-016, T-040, T-046 | spec sealed; hooks tested (T-007, T-008); haiku registry audit (T-011) clean |
| 2 Initial repo optimization | T-041…T-045 (dry-run, then approved batches) | Dillon approves deletions; regression green |
| 3 Orchestration | T-013, T-014, T-015, T-048 | one routed agent run per tier logged |
| 4 Mechanical engineering | T-016…T-025 | kinematic + dynamic + swept-collision records; O review |
| 5 Video | T-026…T-033 | preview reviewed → full render → playback + visual sign-off |
| 6 Team integration | T-034…T-039 | blocked items resolved or recorded |
| 7 Final optimization | T-042…T-045 rerun | final audit; benchmarks before/after |
| 8 Final verification | T-047 | O reviewer per-requirement table |

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

## Standing constraints carried in
- CLAUDE.md hard constraints (budget, schedule, trunk, 3-D gates, CAD fidelity, enclosed wiring).
- Memory "no sims until final" (Dillon, 11-14…11-16) vs spec Part 5 (11-18) → see `engineering-decisions.md` PD-002.
- No purchases before early Dec 2026; DaVinci API spend needs Dillon's approval.
