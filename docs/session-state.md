# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements (full spec at milestones/after compaction/final).
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (IN PROGRESS / BLOCKED / FAILED rows first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## Checkpoint — 2026-11-19 03:30 (session 7cb35b0a, conductor Opus, after the second manual /compact); sections follow spec 10.4
**Goal:** master program (spec of 2026-11-18 + AM-001..AM-004): Phases 1, 2, 4, 5 largely done; independent verification of ledger rows in progress. AM-004 (2026-11-19): Dillon away 8+ h, decisions go to an opus agent; hard constraints, money, irreversible actions, push/history still wait for Dillon. Concept A is the target (CLAUDE.md).

**Requirements:** registry `docs/requirements.md` (109 R-ids), tasks `docs/task-ledger.md` (66 T), phase map `docs/execution-plan.md` (`tools/plan_rid_check.py` 0 missing); audit `python -I tools/ledger_audit.py` 0 errors. Key now: R-PRES-11 (T-007, second manual /compact 7/7 PASS, needs independent check), R-PHY-09 (T-064 D-213, T-065 D-214, T-066 re-baseline), R-CAD-* (T-022/T-023), R-REPO-* (T-042..T-045).

**Done (committed):** spec + AM-001..AM-003 sealed; registry and ledger; hooks, audit tool, agents; capability audit (T-016), video audit (T-026), registry audit + fixes (T-011), physics relabel (T-017); elevon mechanism analyses AR-001..003 (D-212 rev 3, T-063, VERIFIED 2026-11-18: rib horn MEC-004 + keeper MEC-008; five analysis FAIL claims carried and superseded by test claims under T-A-HORN-RIB; fallback row J, CF torsion tube); video VERIFIED 2026-11-18 night (main 119.9 s, highlight 24.2 s, two elevon clips, 1080p60 from 0da084ab, opus sign-off PASS `docs/audits/2026-11-18-film-final-review.md`). 2026-11-19: AM-002 cleanup batch 2 committed (8d15f419); FFmpeg 9.0.2 installed and the four films fully decoded, 0 errors (251702a2; PD-006 superseded); manual /compact test run (T-007 READY FOR REVIEW; evidence `docs/audits/2026-11-19-compact-test.md`); GA sheet regenerated from current CAD; T-062 Explorer numbers refreshed from the generators.

**Pending:** re-checks of T-007, T-014, T-054, T-064 (after D-213 review), T-065 (D-214); T-032 follow PIPELINE.md once; T-022 result; T-023 independent CAD review; T-066; T-035/036/039, T-042..T-045, T-048..T-051, T-053, T-055, T-047, T-059, T-008; assembly_check + collide --glb at the next GLB export; regenerate params-A.json and sitl/cad_mass.json; open engineering items (pad friction, tube twist, touchdown lean, SITL repeat, fin-skin fatigue).

**Failures:** D-212 v1 rejected (jogged Z-bend, modelled joint differs from built joint); D-212 rev 2 rejected (printed horn bonded to foam: invalid peel model, stall strength) so rev 3 escalated to opus with an approach change (through-bolted hardpoint horn). Earlier: `du -sh .` > 120 s (worked in background: 14 GB); subagent Write of `docs/analysis-records.md` refused (subagent policy), so the conductor writes report files from agent outputs; project agents in `.claude/agents` loaded later in the 11-18 session; `git worktree remove --force` of three line-ending-only worktrees blocked by the permission classifier (waits for Dillon); CLI not logged in for the headless test (T-008).

**Decisions:** aircraft decisions in `redesign/params/CHANGE-LOG.md` (D-212 rev 3 is the latest, trade rows A..J); program decisions in `docs/engineering-decisions.md`: PD-002 (sims vs "no sims until final"), PD-005 (flap item maps to elevons), PD-006 (video verification via Blender FFmpeg libraries, SUPERSEDED 2026-11-19 when Dillon approved the FFmpeg install), PD-007 (film Scene 4 plays back an executed SITL run, Z5_gb0). AM-002 (2026-11-19): unused items that do not contribute to the current design may be removed; cleanup batch 2 done under it. AM-003 (2026-11-19): team inputs (schema, James's agents, DaVinci) not ready, no DaVinci spend; blocked rows stay blocked.

**Running now:** implementer T-071 (D-216 Phase 1 steps 1-2, wing skin + node rows, $0 analysis).

**Next action:** WAIT FOR DILLON on T-072: board choice O1-O6 (recommended O4, go/no-go 2026-12-15), purchases, trunk measurement (`docs/audits/2026-11-19-T070-decision.md` s6, s8). Meanwhile $0 work only: T-071, re-checks of T-014/T-022/T-067/T-068, T-023, cleanup T-042..T-045. No CAD change for D-215/D-216 before the board choice.

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
