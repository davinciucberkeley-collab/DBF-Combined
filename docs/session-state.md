# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements (full spec at milestones/after compaction/final).
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (IN PROGRESS / BLOCKED / FAILED rows first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## Checkpoint — 2026-11-18 evening (session 7cb35b0a, conductor Opus)
**Goal:** master program; Phase 1 done except the manual compaction test (needs the user to type /compact); Phases 2, 4, 5 running.
**Done (committed):** spec + AM-001, registry (109 R) and ledger (61 T), hooks, audit tool, agents; capability audit (T-016), video audit (T-026), registry audit + fixes (T-011); elevon mechanism analyses AR-001..003 (all FAIL, real defects); film shot-list mode + 1080p60 preview (T-027).
**D-212 rev 3 (T-063) VERIFIED and committed 2026-11-18:** rib horn MEC-004 + keeper MEC-008; five analysis FAIL claims (rib-foam hold/stall, elevon torsion foam-only, bearing at stall, free play 1.28 deg) carried in the graph, superseded by test claims under T-A-HORN-RIB (coupon 36.8 N / 30 s, elevon torsion coupon, 51 N stall step + bench stall D5b); fallback trade row J (CF torsion tube). Open: assembly_check + collide --glb at next export.
**Video (2026-11-18 night) VERIFIED:** main film 119.9 s, highlight 24.2 s, two elevon clips, 1080p60, encoded from ebb89693 (0da084ab); full decode 0 errors; opus sign-off PASS (`docs/audits/2026-11-18-film-final-review.md`). Open: T-032 PIPELINE.md "follow doc once"; optional minors m-F..m-I.
**Running:** none.
**Next (old list, video items done):** Scene 3 driven by the post-D-212 kinematics (T-028); records for FEA/SITL/landing reuse (T-057/T-058); film defects (S1.1 camera through arms, S2 framing); cleanup approval request to Dillon.
**Failed attempts:** D-212 v1 rejected (jogged Z-bend, modelled joint ≠ built joint); D-212 rev 2 rejected (printed horn bonded to foam: invalid peel model, stall strength) → rev 3 escalated to opus with an approach change (through-bolted/hardpoint horn). Earlier: `du -sh .` > 120 s (worked in background: 14 GB); subagent Write of docs/analysis-records.md refused (subagent policy) → conductor writes report files from agent outputs; project agents in `.claude/agents` not loadable until a new session → general-purpose + model override.
**Inspection (R-PRES-13):** CLAUDE.md kept whole, new sections prepended; no AGENTS.md; no prior `.claude/settings.json`; Claude Code 2.1.288 (PreCompact, PostCompact, SessionStart matchers used).
**Approvals (R-GEN-02):** 2026-11-18 Dillon approved removing the two clean merged worktrees (done, branches kept). Pending asks: /compact test; deletions (after dry run); ffmpeg install (optional, PD-006); DaVinci access + spend; James's agent definitions; shared schema location.
**Blocked on people:** T-015, T-034, T-037; T-007 needs /compact.

## Reconciliation
- 2026-11-18: registry built from the full spec + AM-001; independent haiku check pending (T-011).
