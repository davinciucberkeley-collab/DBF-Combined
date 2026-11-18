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
| Working-tree `du` | did not finish in 120 s (9 agent worktrees under `.claude/worktrees`) | — |

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
None yet.

## 4–12. Consolidation, dependencies, space recovered, benchmarks, regression tests, remaining inefficiencies, preserved references, risks
Pending T-041…T-045. Benchmarks to take before any change (T-043): `collide_a.py` wall time, concept A
Blender build/render time per frame, Explorer first-load bytes and time, `ledger_audit.py` time.

## Protected (never removed by cleanup)
`docs/MASTER_PROJECT_SPEC.md`, `docs/spec-amendments.md`, `docs/spec-integrity.sha256`, `docs/requirements.md`,
`docs/task-ledger.md`, `docs/execution-plan.md`, `docs/session-state.md`, `docs/session-log.md`,
`docs/engineering-decisions.md`, `docs/verification-report.md`, `docs/model-usage.md`, `.claude/settings.json`,
`.claude/hooks/`, `.claude/agents/`, `tools/ledger_audit.py`, `redesign/params/CHANGE-LOG.md`, concept A CAD
(`redesign/qp/A/cad/`), verified analysis outputs, current films.
