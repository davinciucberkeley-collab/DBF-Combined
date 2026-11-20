# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements (full spec at milestones/after compaction/final).
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (IN PROGRESS / BLOCKED / FAILED rows first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## Checkpoint — 2026-11-20 PAUSE (session 7cb35b0a, conductor Opus); sections follow spec 10.4
**Goal:** master program (spec + AM-001..AM-014). Concept A continues as **O4b** (AM-009, D-219): 9x4.5 props, Lua spin cap on a Kakute H743-Wing, RDQ 4S 2800 mAh packs, glass torsion skin, machined 6061 hub, mass recovery; predicted 1.64 kg (weight may exceed the gate in initial design, AM-011); budget = total incl. crash reserve <= $2,000 (AM-013), crash reserve kept (AM-012), nothing supplied by Jacobs/team (AM-014); aircraft must be Claude-designed and student-built (AM-008).

**Requirements:** 109 R-ids; ledger 82 tasks; `python -I tools/ledger_audit.py` 0 errors; `tools/plan_rid_check.py` 0 missing.

**Done (committed):** see git log 2026-11-19..20 and CHANGE-LOG D-213..D-222. Key results: T-067 printed-part mass audit; D-216/D-217 board path (O4 no-go, Altus withdrawn AM-008, O4b AM-009); T-074 O4b checks (sims PASS at 1.64 kg); T-076/T-076b/c/d hub and landing path (Al hub passes; landing demand root cause D-222, CAD mass model cuts arm Mz 41 %); T-080 manufacturing processes (D-221, `docs/reference/jacobs-equipment.md`); T-081 December test plan `redesign/qp/A/TEST-PLAN-O4B.md` (10 tests) whose purchase list is $2,243-2,330 vs $2,000.

**Pending:** T-082 budget closure (opus; partial record `docs/audits/2026-11-20-T082-budget.md`): bring build + tests under $2,000 with the reserve intact. Then: reviewer ruling on the DAF floor (1.61 envelope vs 3.08 case-max) and the 8 T-081 reviewer items; CAD T-077 (decided parts) and drawings; purchases T-078 (Dillon approval, not before early Dec); December tests (2026-12-15 go/no-go on bench derate >= 0.905); trunk height and lid opening measurement (2018 Altima SL); re-checks of READY rows (T-014, T-022, T-067, T-068, T-070, T-071, T-073, T-079, T-080, T-081); T-023 CAD review; cleanup T-042..T-045; final verification T-047.

**Failures:** D-212 v1 rejected (jogged Z-bend, modelled joint differs from built joint); D-212 rev 2 rejected (printed horn bonded to foam: invalid peel model, stall strength) so rev 3 escalated to opus with an approach change (through-bolted hardpoint horn). Earlier: `du -sh .` > 120 s (worked in background: 14 GB); subagent Write of `docs/analysis-records.md` refused (subagent policy), so the conductor writes report files from agent outputs; project agents in `.claude/agents` loaded later in the 11-18 session; `git worktree remove --force` of three line-ending-only worktrees blocked by the permission classifier (waits for Dillon); CLI not logged in for the headless test (T-008).

**Decisions:** aircraft decisions in `redesign/params/CHANGE-LOG.md` (D-212 rev 3 is the latest, trade rows A..J); program decisions in `docs/engineering-decisions.md`: PD-002 (sims vs "no sims until final"), PD-005 (flap item maps to elevons), PD-006 (video verification via Blender FFmpeg libraries, SUPERSEDED 2026-11-19 when Dillon approved the FFmpeg install), PD-007 (film Scene 4 plays back an executed SITL run, Z5_gb0). AM-002 (2026-11-19): unused items that do not contribute to the current design may be removed; cleanup batch 2 done under it. AM-003 (2026-11-19): team inputs (schema, James's agents, DaVinci) not ready, no DaVinci spend; blocked rows stay blocked.

**Running now:** nothing after T-082 returns (stopped at the pause).

**Next action:** on resume: follow the recovery procedure above; read `docs/audits/2026-11-20-T082-budget.md` and finish T-082 (budget under $2,000); then the DAF ruling, then CAD T-077. Ask Dillon only for: purchase approval (December list), trunk height/opening measurement, and anything over $2,000.

**Inspection (R-PRES-13):** CLAUDE.md kept whole, new sections prepended; no AGENTS.md; no prior `.claude/settings.json`; Claude Code 2.1.288 (PreCompact, PostCompact, SessionStart matchers used).

## Approval gate (T-054, R-GEN-02)
Irreversible or costly actions: date, approval wording, sub-actions. Nothing has been pushed, no history rewritten, no purchase made, no DaVinci spend.
| Date | Action | Approval (exact wording) | Sub-actions |
|---|---|---|---|
| 2026-11-18 | Cleanup batch 1 | Dillon in chat: "approved, remove the two clean merged worktrees" | `git worktree remove` of `agent-a3ad648c…` and `agent-ab6e7d18…`; branches kept (recoverable); ≈ 2.17 GB disk |
| 2026-11-19 | Cleanup batch 2 (commit 8d15f419) | AM-002: "if something is unused let it go" (full text in `docs/spec-amendments.md`) | (1) `git worktree remove` of 3 clean merged worktrees (`structures-d9x`, `worktree-agent-a77bd…`, `worktree-agent-a7a16…`; branches kept; ignored files deleted with them); (2) `git rm --cached` of 52 tracked SITL `.BIN` (447.2 MB); (3) deleted all 232 `.BIN` on disk (2,848.4 MB; every run keeps `case.csv` + `result.json`); (4) `git rm` of 23 K09-L site copies (55.5 MB), `showcase/pages/overview-full.png`, `Inventory-Overview.html`, `analysis/cfd3d/out/viz/cfd3d_viz.json`; (5) rebuilt `VTOL-Review.html` without the old-hybrid CFD panel. Detail: `docs/repository-audit.md` batch 2 |
| 2026-11-19 | FFmpeg install (standalone executable) | Dillon: "Okay go ahead with that", after the ffmpeg explanation | `winget install Gyan.FFmpeg` (user scope), FFmpeg 9.0.2; used for the full decode of the four films (251702a2) |
| 2026-11-19 | Reproducibility reruns (landing_a.py, D-209 FEA, one SITL transition case Z5_gb0), an exception to the "no new sims until final" rule | Dillon: "Yes, rerun them", answering "Rerun the landing, FEA and one SITL case to confirm reproducibility?" | T-057, T-058; outputs to new names, committed results not overwritten |
| 2026-11-19 | Manual `/compact` (00:51 and 03:23) | typed by Dillon (his own action) | T-007 tests 1 and 2 |
| Pending | Force-remove 3 worktrees (line-ending-only change in `launch_opencae.bat`) | not yet asked or answered | blocked by the permission classifier; waits for Dillon |
| Pending | DaVinci access and spend | AM-003: no spend | T-037 BLOCKED |
| Pending | Purchases | none before early Dec 2026 (ordering timeline) | none made |
| Pending | Board choice O1-O6 for concept A mass/wing (D-216, T-072) | not yet answered | Phase 2 CAD waits |

**Approval-gate notes (re-check 2026-11-19, `docs/audits/2026-11-19-recheck-docs.md`):** the reflog entries `reset: moving to HEAD` (2026-11-09, -15, -17, -18 at 164c815a) are no-op resets written by `git stash` / `git reset` without a target, at 338e214a (11-09), 55815dba (11-15), 0a574ec1 (11-17) and 164c815a (11-18): HEAD did not move and no commit was lost (each entry's hash equals the entry before it; checked 2026-11-19). Other tracked edits in batch 2 (8d15f419), besides the deletions: rebuilt `build-manual.html`, `test-plan.html`, `VTOL-Review.html`; `redesign/site/app.html`, `redesign/site/index.html` (captions repointed); `docs/task-ledger.md`, `docs/repository-audit.md`; `docs/spec-amendments.md` (append only, AM-002/AM-003) and `docs/spec-integrity.sha256` (seal line for spec-amendments.md rewritten af2e3817… -> cebeca6b…; the spec's own line unchanged). 2026-11-19 01:58 local: `git checkout --` on 39 regenerated PDFs in `redesign/qp/A/drawings/out` (all except MEC-004.pdf, MEC-008.pdf, DRAWINGS-A.*): the discarded changes were the conductor's own `make_drawings_a.py --compose` output of minutes earlier, whose content should equal HEAD (the only composer change was the MEC-004/MEC-008 notes; the diff was not inspected before the checkout, so this is inferred, not shown); no one else's work; regenerable by the same command. Uncommitted tracked edits seen during the check were the in-flight agent edits of this program, committed in c62c1ea1 and 94a3a48a; none is irreversible. Held worktrees (pending Dillon): `.claude/worktrees/agent-a952e3335f2d57495`, `.claude/worktrees/morph-chart-bc71a6`, `.claude/worktrees/proof-chain-readable-c5026d` (only change: line endings of `tools/opencae-studio/launch_opencae.bat`). Kept, not held: `.claude/worktrees/agent-a738e3f4799ad7786` (branch `ui-redesign-survey`, unmerged; listed "kept" in `docs/repository-audit.md`).

## Reconciliation
- 2026-11-18: registry built from the full spec + AM-001; independent haiku check pending (T-011).
