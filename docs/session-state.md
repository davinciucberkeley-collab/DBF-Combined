# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements (full spec at milestones/after compaction/final).
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (IN PROGRESS / BLOCKED / FAILED rows first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## Checkpoint — 2026-11-22 PAUSE (session 7cb35b0a, conductor Opus); sections follow spec 10.4
Paused at Dillon's request (AM-023, "Reach a good place to pause for later resumption"). Working tree clean; nothing
running; nothing pushed (branch redesign/v1, last commit after 59c707e2).

**Goal:** master program (spec + AM-001..AM-023). Concept A O4b, Claude-designed and student-built (AM-008). Current
configuration: D-226 saddle load path (CF bulkheads, 6061 centre node, 3-ply skin, 25x23 rib), SunnySky X2216 V3
short-shaft 880KV on APC 9x4.5MR (D-227/D-228), no spare motor (AM-019), FIN-003 machined 6061 root fitting (D-229),
fin tubes 387.4 mm / FIN_H 0.1937 (D-233), no BOM spare servo (D-234), hub bars T1/T11 from Zoro (D-235). Budget =
total incl. crash reserve by its definition <= $2,000 (AM-013, AM-018); weight may exceed the mass gate (AM-011).

**Requirements:** 109 R-ids; ledger 88 tasks; `python -I tools/ledger_audit.py` 0 errors.

**State (EST):** 1.8796 kg tallied, CG 23.13 mm, SM 7.17 %, window +11.88 %, T/W 2.632/2.111, cruise 234 s, A-P9
tip-over 31.00 deg; BOM $1,939.17, margin +$60.83 (reserve $346.94). 3-D gates PASS at T-084 (no geometry change since).

**Open engineering items:** D-185 rotor-band vibration rule (T-085, see below); A-P6 1.3 Vs 17.56 > 17.0 m/s (TP-11
stall test); landing pad zeta <= 0.05 (TP-3) and pad retention PSA 0.13; TP-4 bond coupon; bench derate >= 0.889;
X2216 short-shaft backorder; R15 rib tube supply (T-088, Carbonwebshop EU); if TP-3 lengthens the pad, re-check A-P9
(30.22 deg); mass gate 1.5 kg missed (carried).

**Paused task T-085 (D-185 FE upgrade):** implementer stopped before its report. Partial, unreviewed work is in
`redesign/qp/A/mechanism/out/T085_data/` (read `README-PAUSED.md` first; fe_a.py / TEST-PLAN edits saved as
`t085_partial.patch` and as `*_post_t085.*` whole files, NOT applied). Preliminary: D-185 FAILs at all corners with
tray + hub-joint compliance (about 99-107 Hz cage bounce, 249-272 Hz); C1/C2 sketches do not clear it. Check the
"pad" strain-energy element source first. This may become a critical engineering issue for Dillon if it holds.

**Next action:** (1) resume T-085 from README-PAUSED.md (sonnet implementer; restore the post files, verify the pad
element, write T085_report.md + D-236); (2) then fix T-081 G-6..G-8 (TP-10 limit, A-P9 re-check line, budget lines
$1,939.17 / Zoro) and T-066 M-1 (re-point vibration claims in proofs/gen_params_a.py to the T-085 modes), re-review
T-066, T-081, T-014 (add the T-085 usage row); (3) T-023 F-9 (WNG-009 printed-mass note) and F-10 (regenerate
drawings after commit); (4) T-032 video pipeline hashes + follow-once; (5) T-088 before the December order; then
cleanup T-042..T-045, T-008, final verification T-047. Review findings: `docs/audits/2026-11-22-review-round-2.md`.
Ask Dillon only for: December purchase approval (not before early Dec; check RMRC and Carbonwebshop stock first),
trunk height and lid opening (2018 Altima SL), Jacobs material and test-frame confirmations, anything over $2,000.
Note: a Zoro guest cart in the browser pane holds the two hub bars (nothing bought).

**Failures (history):** see git log and CHANGE-LOG; O4b with MN2212 infeasible (AM-017 study); MN3110, legs/skid,
0.8 m/s touchdown and concept B rejected (`docs/audits/2026-11-21-config-study.md`); PETG FIN-003 failed (D-229).

**Decisions:** aircraft in `redesign/params/CHANGE-LOG.md`; program in `docs/engineering-decisions.md` (PD-002..PD-007).

**Inspection (R-PRES-13):** CLAUDE.md kept whole; no AGENTS.md.

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
