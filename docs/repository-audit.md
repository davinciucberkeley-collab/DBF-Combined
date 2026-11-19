# Repository audit

Initial audit 2026-11-18 (T-040), commit a93f14da, branch `redesign/v1`. Dry run only: **nothing removed yet**;
deletions wait for Dillon's approval (spec 9.3 step 9, T-041). Final audit: T-045 at the end of the program.

## 1. Baseline size (commands shown)
| Metric | Value | Command |
|---|---|---|
| `.git` on disk | 2.3 GB | `du -sh .git` |
| Packed history | 1.51 GiB in 4 packs, 22 407 objects; 524 MiB loose (2 451 objects) | `git count-objects -vH` |
| Tracked tree at HEAD | 1 489 MB in 13 798 files | `git ls-tree -r -l HEAD` summed |
| Identical content tracked twice or more | 94.7 MB | same listing, grouped by blob hash |
| Working tree on disk incl. `.git` and the 9 agent worktrees under `.claude/worktrees` | 14 GB (≈ 11.7 GB outside `.git`, mostly worktree checkouts) | `du -sh .` (≈ 3 min) |

Tracked size by top folder: `redesign` 1 355 MB (`qp` 472, `showcase` 315, `team` 212, `site` 175, `config-study` 64,
`review` 48, `blender` 33, `proofs` 28), `analysis` 55, root `VTOL-Review.html` 29, `docs` 8.4, others < 7 each.
By type: `.BIN` 447 MB, `.mp4` 254, `.png` 215, `.json` 201, `.txt` 105, `.html` 47, `.stl` 46, `.glb` 30.

## 2. Largest items / candidates (classification is a proposal)
| Item | Size | Proposed class | Reason / check needed |
|---|---|---|---|
| `redesign/qp/A/sitl/runs/**/logs/*.BIN` (52 files) | 447 MB | Uncertain → regenerable | ArduPilot SITL dataflash logs; regenerable by rerunning SITL, but they may be evidence for concept A claims. Proposal: keep the summary CSV/MD per run, move BINs to git-ignored local storage or a release asset. Needs Dillon. |
| `redesign/site/assets/animation/**` = copies of `redesign/showcase/concept-a/animation/**` | ≈ 75 MB duplicated | Obsolete duplicate (one side) | Explorer publishes from `site/`; `publish_assets.py` copies. Proposal: keep one copy, have the publish step copy at publish time. Check publish script + artifact file list first. |
| `redesign/showcase/animation/**` K09-L films (`k09l-build.mp4` 28 MB, GIF 9.7 MB) + `site/assets/animation/build/k09l-build.mp4` 13.7 MB | ≈ 55 MB | Protected (record) / duplicate copy obsolete | K09-L is the previous design; keep one copy as record. |
| `redesign/showcase/pages/overview-full.png` | 24.7 MB | Regenerable | headless-Chrome page snapshot. |
| `analysis/cfd3d/out/viz/cfd3d_viz.json` | 23 MB | Uncertain | 11-02 resize CFD output for the old hybrid concept. |
| `redesign/showcase/stl/k09l-assembly.stl`, `wing.stl` | 33 MB | Regenerable (K09-L) | `export_stl.py`. |
| `redesign/config-study/tiebreak/wind/data/*.txt` (8 × ≈ 7.6 MB) | 61 MB | Protected (source data) | Downloaded wind records used in the config study; keep or replace by a fetch script + checksum. |
| `VTOL-Review.html`, `Inventory-Overview.html`, `build-manual.html`, `test-plan.html` at root | 44 MB | Uncertain | Old-concept standalone pages (GitHub Pages?); DECISIONS.md says root areas are pre-redesign. |
| `redesign/proofs/out/graph.js` + `graph.json` (same data) | 19.8 MB | Duplicate format | Check which the viewer loads. |
| `.claude/worktrees/*` (9 worktrees; 2 named merged branches `build-film-audit`, others agent branches) | not measured | Regenerable once merged | `git worktree remove` after confirming each branch is merged. Untracked, so no repo-size effect. |
| History: 1.5 GiB pack | — | Do not touch | Rewriting history needs team authorization (spec 9.3). |

## 3. Files removed or archived
Batches 1 and 2 below. Dry-run facts: `docs/audits/2026-11-18-cleanup-dryrun.md` (T-041a). Measured reclaimable on disk:
untracked SITL `.BIN` 2 401 MB (all 232 runs keep `case.csv` + `result.json`); 7 merged agent worktrees 4.3–7.9 GB
(2 fully clean: `agent-a3ad648c…` 1.48 GB, `agent-ab6e7d18…` 0.69 GB); tracked SITL `.BIN` 447 MB (repo size only
shrinks with a history rewrite, which needs team authorization); 23 K09-L leftovers in `site/assets` 55.5 MB.
An attempt to `git worktree remove` the two clean merged worktrees (branches kept) was blocked by the session's
permission classifier on 2026-11-18, so every removal now waits for Dillon's approval (dry-run §9 questions).

| Date | Batch | Approval | Action | Recovered | Regression |
|---|---|---|---|---|---|
| 2026-11-18 | 1 | Dillon in chat: "approved, remove the two clean merged worktrees" | `git worktree remove` `agent-a3ad648c…` (build-film-audit) and `agent-ab6e7d18…`; branches kept (recoverable) | ≈ 2.17 GB disk (untracked; repo size unchanged) | `git worktree list` 8 entries; both branches still listed |
| 2026-11-19 | 2 | AM-002: "if something is unused let it go" | `git worktree remove` 3 clean merged worktrees (`structures-d9x`, `worktree-agent-a77bd…`, `worktree-agent-a7a16…`; branches kept; their ignored files were K09-L-era FEA/solver `history.csv`); `git rm --cached` 52 tracked SITL `.BIN` (447.2 MB) and deleted all 232 `.BIN` on disk (2,848.4 MB; every run keeps `case.csv` + `result.json`; no script or claim reads a BIN); `git rm` 23 K09-L site copies (55.5 MB; Explorer captions repointed to the kept `showcase/animation` record), `showcase/pages/overview-full.png` (24.7 MB, unreferenced), `Inventory-Overview.html` (5.9 MB, v0.3.1, unlinked), `analysis/cfd3d/out/viz/cfd3d_viz.json` (23.1 MB, old-hybrid CFD panel) and rebuilt `VTOL-Review.html` without the panel (29.1 → 6.0 MB) | ≈ 2.85 GB disk + ≈ 2.3 GB worktrees; tracked tree −≈ 579 MB (history unchanged) | `gather.py` rc 0; `proofs/run_all.py` fails 6 (unchanged); `app.html` / `index.html` 0 missing local links; `git ls-files` 0 `.BIN`; `review/build.mjs` rebuild (build-manual / test-plan SVG drift was pre-existing nondeterminism, committed as rebuilt) |
| 2026-11-19 | 2 (held) | — | 3 merged worktrees (`worktree-agent-a952e…`, `claude/morph-chart-bc71a6`, `claude/proof-chain-readable-c5026d`) whose only change is a line-ending rewrite of `tools/opencae-studio/launch_opencae.bat` (diff empty with `--ignore-cr-at-eol`): `git worktree remove --force` was blocked by the session permission classifier; waits for Dillon | — | — |
| 2026-11-19 | kept | AM-002 (used by the current design) | Site animation copies (Explorer serves them), `showcase/animation` K09-L record films, `graph.js`/`graph.json`, CI-checked root pages, unmerged `ui-redesign-survey` worktree; Q7 (CI publish step) is a future change, not a removal | — | — |

Batch 2 reclassification note (2026-11-19). `analysis/cfd3d/out/viz/cfd3d_viz.json` was listed as "Protected" in the dry run, pending Dillon's call on the old-hybrid CFD panel. AM-002 ("if something is unused let it go ... if they do not contribute to our current design") answered it: the panel is the old hybrid concept, not concept A, so the file was removed in batch 2. It is recoverable from git history (the last commit before 8d15f419).

Dangling references the review found after batch 2, open for T-042 / T-044: `DECISIONS.md`, `PRODUCT.md`, `PROVENANCE.md`, `inventory/build_overview.mjs`, `review/build.mjs`, `analysis/cfd3d/postprocess.py`, `redesign/inputs/decisions/*` (they still name removed files such as the CFD panel data, `Inventory-Overview.html` or the K09-L site copies). Not edited yet.

## 4–12. Consolidation, dependencies, space recovered, benchmarks, regression tests, remaining inefficiencies, preserved references, risks
Pending T-041…T-045. Benchmarks to take before any change (T-043): `collide_a.py` wall time, concept A
Blender build/render time per frame, Explorer first-load bytes and time, `ledger_audit.py` time.

## Protected (never removed by cleanup)
`docs/MASTER_PROJECT_SPEC.md`, `docs/spec-amendments.md`, `docs/spec-integrity.sha256`, `docs/requirements.md`,
`docs/task-ledger.md`, `docs/execution-plan.md`, `docs/session-state.md`, `docs/session-log.md`,
`docs/engineering-decisions.md`, `docs/verification-report.md`, `docs/model-usage.md`, `.claude/settings.json`,
`.claude/hooks/`, `.claude/agents/`, `tools/ledger_audit.py`, `redesign/params/CHANGE-LOG.md`, concept A CAD
(`redesign/qp/A/cad/`), verified analysis outputs, current films.
