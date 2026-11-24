# Session state — persistent checkpoint

Update at every milestone and before any handoff. Never treat a compaction summary as authoritative; this file,
the ledger and the spec are.

## Recovery procedure (spec 1.5)
1. Project-root `CLAUDE.md` (auto-loaded). 2. Spec at `docs/MASTER_PROJECT_SPEC.md` (+ `spec-amendments.md`).
3. Read the spec sections for the active tasks' parent requirements; read the full spec (and all amendments) in a new
   session, after compaction, at milestones and before final verification. Rows without a section number (e.g. R-GEN-02)
   trace to the amendment named in their requirements.md row: read that amendment.
4. `docs/requirements.md`. 5. `docs/task-ledger.md` (rows are in ID order: `grep -E "IN PROGRESS|BLOCKED|FAILED"` first). 6. `docs/execution-plan.md`.
7. This file. 8. Active task + unfinished deps. 9. Compare plan vs requirements (`python -I tools/ledger_audit.py`).
10. Note any lost/changed instruction under "Reconciliation" below. 11. Resume "Next action".

## PAUSE CHECKPOINT — 2026-11-24 evening (Dillon: "Reach a good place to pause for later resumption"; AM-001..AM-068 in force; supersedes "Next action on resume" below)

**Pushed:** origin/redesign/v1 at 9de29365 (CI green). Requirements 103 / 113 VERIFIED, tasks 93 / 105 (ledger_audit 0 errors). Since the checkpoint below: D-253..D-261, T-037 VERIFIED (DAVINCI.md), T-101 adopted A1 (pack aft, cruise 18, RLL2SRV_RMAX 45 / TCONST 0.9; pitch use 0.59; flight decides), D-256 Lua dropped, D-258 A-P8 pass, D-259 FC kept + A.param battery / airspeed fixes, D-260 Cn_beta pass / spiral re-derived, D-261 glass-skin render fix + stills + Explorer text; replays include the A1 runs; side branches deleted (only main and redesign/v1 remain).

**In flight at pause (background, may or may not have finished):** AM-068 video re-render: `python -I redesign/showcase/animation/render_animation.py --concept a` then `python -I redesign/showcase/concept-a/render_build_a.py` (logs in the session scratchpad, not durable). Output lands in `redesign/showcase/concept-a/animation/`; nothing published yet.

**Next actions on resume, in order:**
1. Videos: check `redesign/showcase/concept-a/animation/` timestamps (a-how-it-flies.mp4 / build stage-NN.mp4 newer than 2026-11-24 15:00). If missing or old, re-run the two commands above (the build film supports `--skip-render` if frames exist). Frame check: X2216 motors, FC annex 75 mm left (D-240), light glass skin (no wood). Then `python -I redesign/showcase/concept-a/publish_assets.py`, add `?v=20261124` to the assets/animation/*.mp4 / *.webp URLs in redesign/site/app.html, `make_index.py`, commit, push.
2. GLB colour: `redesign/site/assets/concept-a.opt.glb` (3-D viewer fallback colour and the replays) still carries the wood colour for WNG-011 / WNG-014; re-export (redesign/blender/export_glb.py), re-run the exported-model gate `redesign/qp/A/cad/collide_glb_a.py` (must stay 0 / 0 / 0), bump GLB_URL ?v= in replay.js / viewer, commit, push.
3. AM-067 / AM-068: open a PR redesign/v1 -> main (fast-forward; main at 2026-11-18) and merge it; then ccd_pr get_status / bind_pr.
4. Refresh the status page artifact (Da5o3i6p5o6Jvf3iaheFBG) and Dillon's weekly card (4RrDZ8DYUqq5UzAzMx61oG, doc 2026-12-02__dylan; the week resets Wed 2 Dec).
5. 1-4 Dec: T-093 order-week re-check, then Dillon approves Order 1 ($887.25). Waiting on Dillon (not urgent): car-trunk measurement (T-078), Carbonwebshop email for the R15 tube (T-088), dbf-hangar "not yet" (T-034), OpenCAE hold (T-036).

## Checkpoint — 2026-11-24 (resumed AM-027, running under AM-028 / AM-036; AM-001..AM-050 in force; session 7cb35b0a, conductor Opus); sections follow spec 10.4
Pushed to origin redesign/v1 five times, latest 7cbaa3f9 on 2026-11-24 (CI and Pages green); see the approval gate below.

**Goal:** master program (spec + AM-001..AM-050). Concept A O4b, Claude-designed and student-built (AM-008). Current
configuration: D-226 saddle load path (CF bulkheads, 6061 centre node, 3-ply skin, 25x23 rib), SunnySky X2216 V3
short-shaft 880KV on APC 9x4.5MR (D-227/D-228), no spare motor (AM-019), FIN-003 machined 6061 root fitting (D-229),
fin tubes 387.4 mm / FIN_H 0.1937 (D-233), no BOM spare servo (D-234), hub bars T1/T11 from Zoro (D-235). Budget =
total incl. crash reserve by its definition <= $2,000 (AM-013, AM-018); weight may exceed the mass gate (AM-011).

**Requirements:** 113 R-ids (102 VERIFIED COMPLETE after T-047, the conductor follow-up, the R-MON-01 re-check and AM-051 closing R-GEN-01); ledger 105 tasks (92 VERIFIED COMPLETE); `python -I tools/ledger_audit.py` 0 errors. (Updated 2026-11-24.)

**State (EST):** CAD 1,641.0 g, predicted 1.881 kg (CL-A-MASS-PRED), CG 22.05 mm CAD (tallied about 23.22), SM 7.61 % CAD, lateral CG -3.32 mm (FC 75 mm left, D-240), window +11.88 %, T/W 2.632/2.111, cruise 234 s, A-P9
tip-over 31.00 deg; BOM $1,939.17, margin +$60.83 (reserve $346.94). 3-D gates PASS at T-092 (2026-11-23; no geometry change since).

**Open item (T-103, 2026-11-23):** T-099 F-6 (go/no-go date) is answered by AM-037: go/no-go and bench decision Fri 29 Jan 2027, no fabrication before Jacobs reopens (19 Jan assumed), D-248, SCHEDULE-A, slack +2 d.

**Open engineering items:** D-185 rotor-band vibration rule (D-236, TP-10b decides); A-P6 1.3 Vs 17.74 > 17.0 m/s (at 1.881 kg; 17.56 was the 1.873 kg figure) (TP-11
stall test); landing pad zeta <= 0.05 (TP-3) and pad retention PSA 0.13; TP-4 bond coupon; bench derate >= 0.889;
X2216 short-shaft backorder; R15 rib tube supply (T-088, Carbonwebshop EU); if TP-3 lengthens the pad, re-check A-P9
(30.22 deg); mass gate 1.5 kg missed (carried).

**D-185 (T-085 / D-236):** upgraded FE FAILs D-185 (a) in 23 of 24 bound groups (wing flap / cage bounce 94.6-108.7 Hz);
no robust lever; decided by TP-10b (T-A-TAP tap test of the built airframe, $0) before the first tethered hover; if
confirmed, reopen the C-route (arms 10x8 + bridge soft in z first). Proof chain carries CL-A-VIB-IN-BAND FAIL; gain
margin claims UNVERIFIED (T-089).

**Resumed 2026-11-22 (AM-027) after the AM-026 pause; running.** (Push history: see the approval gate.) `docs/session-log.md` shows as modified between commits: hook logging, committed with the next checkpoint.

**Known dependency gaps (2026-11-23 milestone audit s3.3; none blocks the next action):** T-077 is READY FOR REVIEW (part-8 blocker superseded by AM-017, AM-018, D-226..D-240) and T-083 waits on it (Deps "T-077 (READY FOR REVIEW)"); T-083 itself is BLOCKED on TP-3 (zeta <= 0.05), TP-11 (A-P6) and the X2216 backorder (T-093); T-088 is BLOCKED until order week (T-093); T-094 (free-play bench entry in TEST-PLAN-O4B, closes the T-061 residual FAIL) is NOT STARTED. T-045 and T-008 are VERIFIED COMPLETE.
**Next action on resume:** (2026-11-24, after review round 13) (1) Fix pass C (done 6cc99eeb; re-review closed) (review round 13 findings R13-1..R13-4, T-103, T-104 / T-105 LOW, R13-3, R13-P1; change list in `docs/audits/2026-11-24-review-round-13.md` "Fix pass C"); (2) push done 71cab7a2 (AM-041; Dillon to confirm the 2026-11-24 push covered the non-layout commits too); (3) final verification T-047 / T-059 / T-049 done 2026-11-24 (99 / 113 requirements verified; docs/verification-report.md); (4) the DaVinci branch deletion (`concept-a-snapshot-73656c93`, storage at its 1.0 GB limit) is Dillon's decision (AM-050); T-037 stays IN PROGRESS (spend proof needs a usage read after asOf moves); (5) T-093 on 1-4 Dec 2026: re-check ORDER-1 prices and stock (R15 vendor with Dillon's cart address, X2216 backorder) and present Order 1 ($887.25) for approval; T-088 closes with it. Then bench tests TP-1..TP-4 and TP-15..TP-18 from 19 Jan 2027 as parts arrive (go / no-go 29 Jan 2027). Open engineering item: CL-A-PITCH-USE 0.651 FAIL, next rung cut cruise trim (D-251, D-252). Team-blocked: T-034, T-035, T-036.

**Failures (history):** see git log and CHANGE-LOG; O4b with MN2212 infeasible (AM-017 study); MN3110, legs/skid,
0.8 m/s touchdown and concept B rejected (`docs/audits/2026-11-21-config-study.md`); PETG FIN-003 failed (D-229).

**Decisions:** aircraft in `redesign/params/CHANGE-LOG.md`; program in `docs/engineering-decisions.md` (PD-002..PD-007).

**Inspection (R-PRES-13):** CLAUDE.md kept whole; no AGENTS.md.

## Approval gate (T-054, R-GEN-02)
Irreversible or costly actions: date, approval wording, sub-actions. No history rewritten, no purchase made, no DaVinci AI spend seen (usage unchanged; not proof, asOf 2026-11-09). Pushes are listed below.
| Date | Action | Approval (exact wording) | Sub-actions |
|---|---|---|---|
| 2026-11-18 | Cleanup batch 1 | Dillon in chat: "approved, remove the two clean merged worktrees" | `git worktree remove` of `agent-a3ad648c…` and `agent-ab6e7d18…`; branches kept (recoverable); ≈ 2.17 GB disk |
| 2026-11-19 | Cleanup batch 2 (commit 8d15f419) | AM-002: "if something is unused let it go" (full text in `docs/spec-amendments.md`) | (1) `git worktree remove` of 3 clean merged worktrees (`structures-d9x`, `worktree-agent-a77bd…`, `worktree-agent-a7a16…`; branches kept; ignored files deleted with them); (2) `git rm --cached` of 52 tracked SITL `.BIN` (447.2 MB); (3) deleted all 232 `.BIN` on disk (2,848.4 MB; every run keeps `case.csv` + `result.json`); (4) `git rm` of 23 K09-L site copies (55.5 MB), `showcase/pages/overview-full.png`, `Inventory-Overview.html`, `analysis/cfd3d/out/viz/cfd3d_viz.json`; (5) rebuilt `VTOL-Review.html` without the old-hybrid CFD panel. Detail: `docs/repository-audit.md` batch 2 |
| 2026-11-19 | FFmpeg install (standalone executable) | Dillon: "Okay go ahead with that", after the ffmpeg explanation | `winget install Gyan.FFmpeg` (user scope), FFmpeg 9.0.2; used for the full decode of the four films (251702a2) |
| 2026-11-19 | Reproducibility reruns (landing_a.py, D-209 FEA, one SITL transition case Z5_gb0), an exception to the "no new sims until final" rule | Dillon: "Yes, rerun them", answering "Rerun the landing, FEA and one SITL case to confirm reproducibility?" | T-057, T-058; outputs to new names, committed results not overwritten |
| 2026-11-19 | Manual `/compact` (00:51 and 03:23) | typed by Dillon (his own action) | T-007 tests 1 and 2 |
| 2026-11-23 | Cleanup batch 3 | AM-029: "Yes, remove them" | 3 line-ending-only worktrees removed with --force, branches kept, about 3.55 GB (`docs/repository-audit.md` s3 batch 3) |
| 2026-11-23 | git push redesign/v1 (c6d027b6) | AM-032 "Yeah, push it"; AM-033 ("make sure to have the results available in the explored and GitHub") | CI + Pages green |
| 2026-11-24 | git push redesign/v1 (c6d027b6..71cab7a2: T-099..T-105, T-015, T-037, layout cleanup) | AM-041 ("cleaning up the file layout in the local folder and the github"), read by the conductor as covering this push; confirmation from Dillon requested for the non-layout commits | CI + Pages green, live #sims checked |
| 2026-11-24 | DaVinci writes to the org project API Test (scratch and snapshot branches, 367 objects, GLB, 129 + 76 STEP geometries; 836 MB of org storage) | AM-046 "Yes, use API Test and start the research", AM-047, AM-048 "Do all three", AM-049 | token in git-ignored .env; no agent prompts; branch deletion pending with Dillon (AM-050) |
| 2026-11-24 | git push redesign/v1 (71cab7a2..7cbaa3f9: T-047 / T-049 / T-059 final verification, Impeccable replay fixes, film card) | AM-041 and AM-036 ("keep working until you achieve this"), read by the conductor as covering it; confirmation from Dillon requested | CI and Pages checked after push |
| Pending | DaVinci access and spend; branch deletion | AM-003: no spend; AM-050: branch deletion is Dillon's | T-037 IN PROGRESS |
| Pending | Purchases | none before early Dec 2026 (ordering timeline) | none made |
| 2026-11-19..21 | Board choice O1-O6 for concept A mass/wing (D-216, T-072) | AM-005, AM-006, AM-009 | O4 then O4b |
| 2026-11-21 | Motor swap to SunnySky X2216 880KV (T-083) | AM-018: "I approve the swap and follow the definition of the reserve" | no purchase before early December; reserve by definition (`T082_data/bom_t082.py`) |
| 2026-11-21 | Drop the spare fifth motor | AM-019: "Go ahead with that" | 4 X2216 V3 short-shaft motors in Order 1, no BOM spare; reserve covers one replacement |
| 2026-11-23 | Test equipment | AM-030: "Keep what we have now, ..." | no press rig / testing machine bought; TP-4 / TP-12..14 use a borrowed force frame, else the T-082 lever rig |

**Approval-gate notes (re-check 2026-11-19, `docs/audits/2026-11-19-recheck-docs.md`):** the reflog entries `reset: moving to HEAD` (2026-11-09, -15, -17, -18 at 164c815a) are no-op resets written by `git stash` / `git reset` without a target, at 338e214a (11-09), 55815dba (11-15), 0a574ec1 (11-17) and 164c815a (11-18): HEAD did not move and no commit was lost (each entry's hash equals the entry before it; checked 2026-11-19). Other tracked edits in batch 2 (8d15f419), besides the deletions: rebuilt `build-manual.html`, `test-plan.html`, `VTOL-Review.html`; `redesign/site/app.html`, `redesign/site/index.html` (captions repointed); `docs/task-ledger.md`, `docs/repository-audit.md`; `docs/spec-amendments.md` (append only, AM-002/AM-003) and `docs/spec-integrity.sha256` (seal line for spec-amendments.md rewritten af2e3817… -> cebeca6b…; the spec's own line unchanged). 2026-11-19 01:58 local: `git checkout --` on 39 regenerated PDFs in `redesign/qp/A/drawings/out` (all except MEC-004.pdf, MEC-008.pdf, DRAWINGS-A.*): the discarded changes were the conductor's own `make_drawings_a.py --compose` output of minutes earlier, whose content should equal HEAD (the only composer change was the MEC-004/MEC-008 notes; the diff was not inspected before the checkout, so this is inferred, not shown); no one else's work; regenerable by the same command. Uncommitted tracked edits seen during the check were the in-flight agent edits of this program, committed in c62c1ea1 and 94a3a48a; none is irreversible. Held worktrees (pending Dillon): `.claude/worktrees/agent-a952e3335f2d57495`, `.claude/worktrees/morph-chart-bc71a6`, `.claude/worktrees/proof-chain-readable-c5026d` (only change: line endings of `tools/opencae-studio/launch_opencae.bat`). Kept, not held: `.claude/worktrees/agent-a738e3f4799ad7786` (branch `ui-redesign-survey`, unmerged; listed "kept" in `docs/repository-audit.md`).

## Reconciliation
- 2026-11-18: registry built from the full spec + AM-001; independent haiku check pending (T-011).
- 2026-11-22..23: AM-023 and AM-026 pauses (pause = stop agents, save partial work, checkpoint, commit); AM-024, AM-025, AM-027 resume / continue; AM-028 standing rule: do not ask "continue?" between steps, move to the next queue item, prompt Dillon only for a team decision or a problem. None lost; all in spec-amendments.md.
- 2026-11-23: T-008 recovery test (`docs/audits/2026-11-23-recovery-test.md`) found 8 procedure gaps; fixed in this file (steps 3 and 5, counts, header, pause state, this section, dependency gaps).
- 2026-11-23: AM-029 (batch 3 approved and executed, T-042) and AM-030 (keep current equipment; continue every doable task per AM-028) recorded; none lost.
- 2026-11-23: AM-004 (Opus consults replace Dillon while away 8+ h) lapsed; not a standing rule, no R-id needed.
- 2026-11-23: spec-amendments.md header names `tools/spec_guard.py`; the file does not exist, the seal check is `tools/ledger_audit.py` (0 errors). The header is inside the append-only region and was not edited (milestone audit F-12).
- 2026-11-23: milestone audit `docs/audits/2026-11-23-milestone-audit.md` (T-048 / T-055, full spec read) fixes applied: requirements roll-up, new rows R-GEN-05..R-GEN-08, T-094, status corrections, execution-plan T-064..T-094, change list `docs/audits/2026-11-23-milestone-fixes.md`.
