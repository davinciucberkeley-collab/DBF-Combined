# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements (full spec at milestones/after compaction/final).
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (IN PROGRESS / BLOCKED / FAILED rows first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## Checkpoint — 2026-11-18 (session 7cb35b0a, conductor Opus)
**Goal:** Phase 1 of the master program (preservation, tracking, hooks, recovery test, initial audit), then Phases 2–8.
**Relevant requirements:** R-PRES-*, R-TRK-*, R-ORC-01, R-REPO-01, R-COM-*.
**Done:** spec + AM-001 saved verbatim; requirements (≈90 rows), ledger (48 tasks), plan, decisions, hooks, audit tool written.
**Pending:** seal; CLAUDE.md integration; hook unit run; compaction + new-session tests (T-007/T-008); agent definitions;
baseline repo audit (T-040); commit; then T-016 capability audit, T-026 video audit.
**Failed attempts:** `du -sh .` on the working tree exceeded 120 s (2.3 GB .git; worktrees inside `.claude/worktrees`) → use `git count-objects -vH` + per-dir sizes excluding `.claude`.
**Engineering decisions this session:** PD-001…PD-004 (`engineering-decisions.md`).
**Blocked on people:** James's agent definitions (T-015), shared aircraft schema (T-034), DaVinci access + spend (T-037), deletion approval (T-041).
**Next action:** finish T-004/T-006/T-007.

## Reconciliation
- 2026-11-18: registry built from the full spec + AM-001; independent haiku check pending (T-011).
