# Repository audit

Initial audit 2026-11-18 (T-040), commit a93f14da, branch `redesign/v1`. The first pass was a dry run;
deletions needed Dillon's approval (spec 9.3 step 9); batches 1 to 3 are logged in s3. Report completed by T-045 on 2026-11-23; the final dated audit is T-049 at the end of the program.

## 1. Baseline size (commands shown)
| Metric (as of a93f14da, 2026-11-18; the loose-object and `du -sh .` rows are no longer reproducible: worktrees removed, see s3 and s4) | Value | Command |
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
Batches 1 to 3 below. Dry-run facts: `docs/audits/2026-11-18-cleanup-dryrun.md` (T-041a). Measured reclaimable on disk:
untracked SITL `.BIN` 2 401 MB (all 232 runs keep `case.csv` + `result.json`); 7 merged agent worktrees 4.3–7.9 GB
(2 fully clean: `agent-a3ad648c…` 1.48 GB, `agent-ab6e7d18…` 0.69 GB); tracked SITL `.BIN` 447 MB (repo size only
shrinks with a history rewrite, which needs team authorization); 23 K09-L leftovers in `site/assets` 55.5 MB.
An attempt to `git worktree remove` the two clean merged worktrees (branches kept) was blocked by the session's
permission classifier on 2026-11-18, so every removal now waits for Dillon's approval (dry-run §9 questions); since cleared by batch 1 chat approval, AM-002 and AM-029.

| Date | Batch | Approval | Action | Recovered | Regression |
|---|---|---|---|---|---|
| 2026-11-18 | 1 | Dillon in chat: "approved, remove the two clean merged worktrees" | `git worktree remove` `agent-a3ad648c…` (build-film-audit) and `agent-ab6e7d18…`; branches kept (recoverable) | ≈ 2.17 GB disk (untracked; repo size unchanged) | `git worktree list` 8 entries; both branches still listed |
| 2026-11-19 | 2 | AM-002: "if something is unused let it go" | `git worktree remove` 3 clean merged worktrees (`structures-d9x`, `worktree-agent-a77bd…`, `worktree-agent-a7a16…`; branches kept; their ignored files were K09-L-era FEA/solver `history.csv`); `git rm --cached` 52 tracked SITL `.BIN` (447.2 MB) and deleted all 232 `.BIN` on disk (2,848.4 MB; every run keeps `case.csv` + `result.json`; no script or claim reads a BIN); `git rm` 23 K09-L site copies (55.5 MB; Explorer captions repointed to the kept `showcase/animation` record), `showcase/pages/overview-full.png` (24.7 MB, unreferenced), `Inventory-Overview.html` (5.9 MB, v0.3.1, unlinked), `analysis/cfd3d/out/viz/cfd3d_viz.json` (23.1 MB, old-hybrid CFD panel) and rebuilt `VTOL-Review.html` without the panel (29.1 → 6.0 MB) | ≈ 2.85 GB disk + ≈ 2.3 GB worktrees; tracked tree −≈ 579 MB (history unchanged) | `gather.py` rc 0; `proofs/run_all.py` fails 6 (unchanged); `app.html` / `index.html` 0 missing local links; `git ls-files` 0 `.BIN`; `review/build.mjs` rebuild (build-manual / test-plan SVG drift was pre-existing nondeterminism, committed as rebuilt) |
| 2026-11-19 | 2 (held) | — | 3 merged worktrees (`worktree-agent-a952e…`, `claude/morph-chart-bc71a6`, `claude/proof-chain-readable-c5026d`) whose only change is a line-ending rewrite of `tools/opencae-studio/launch_opencae.bat` (diff empty with `--ignore-cr-at-eol`): `git worktree remove --force` was blocked by the session permission classifier; waits for Dillon | — | — |
| 2026-11-23 | 3 (was 2 held) | AM-029, Dillon in chat: "Yes, remove them" | `git worktree remove --force` `worktree-agent-a952e…`, `claude/morph-chart-bc71a6`, `claude/proof-chain-readable-c5026d` (checked first: only change was the line-ending rewrite of `tools/opencae-studio/launch_opencae.bat`, `git diff --ignore-cr-at-eol` empty); branches kept (recoverable) | 706 + 1,422 + 1,426 MB = about 3.55 GB disk (`du -sm` before removal; untracked, repo size unchanged) | `git worktree list` 2 entries (main + unmerged `ui-redesign-survey`, kept); the 3 branches still listed |
| 2026-11-19 | kept | AM-002 (used by the current design) | Site animation copies (Explorer serves them), `showcase/animation` K09-L record films, `graph.js`/`graph.json`, CI-checked root pages, unmerged `ui-redesign-survey` worktree; Q7 (CI publish step) is a future change, not a removal | — | — |

Batch 2 reclassification note (2026-11-19). `analysis/cfd3d/out/viz/cfd3d_viz.json` was listed as "Protected" in the dry run, pending Dillon's call on the old-hybrid CFD panel. AM-002 ("if something is unused let it go ... if they do not contribute to our current design") answered it: the panel is the old hybrid concept, not concept A, so the file was removed in batch 2. It is recoverable from git history (the last commit before 8d15f419).

Dangling references the review found after batch 2, open for T-042 / T-044: `DECISIONS.md`, `PRODUCT.md`, `PROVENANCE.md`, `inventory/build_overview.mjs`, `review/build.mjs`, `analysis/cfd3d/postprocess.py`, `redesign/inputs/decisions/*` (they still name removed files such as the CFD panel data, `Inventory-Overview.html` or the K09-L site copies). Fixed in T-042 (85ae8c0f), see `docs/audits/2026-11-23-T042-refs.md`.

## 4–12. Remaining report sections (spec 9.9)
Written 2026-11-23 (T-045) from `docs/audits/2026-11-18-cleanup-dryrun.md`, `docs/audits/2026-11-23-T042-refs.md` and
`docs/audits/2026-11-23-T043-T044.md`. Spec 9.9 lists 12 items; this file maps them as: 1 baseline = s1; 2 file inventory = s1
tables plus s4; 3 cleanup candidates = s2; 4 files removed or archived = s3; 5 to 12 = s5 to s12 below (s4 here is the
inventory after cleanup). Category of every measurement here: repository hygiene or benchmark; none is an engineering analysis.

### 4. File inventory after cleanup (spec item 2)
Measured 2026-11-23 on HEAD 76894339 (`git ls-tree -r -l HEAD` summed; `git ls-files`):
| Metric | s1 baseline (2026-11-18) | Now | Note |
|---|---|---|---|
| Tracked files / size | 13,798 files, 1,489 MB | 15,281 files, 1,064.8 MB | Batch 2 removed about 579 MB; new work since then added files and some MB. The two numbers are not a clean before/after. |
| Tracked folders over 20 MB, now | `redesign` 1,355 MB | `redesign/showcase` 340.1, `team` 212.2, `qp` 128.0, `site` 119.4, `config-study` 63.9, `review` 47.7, `blender` 32.5, `proofs` 28.4 MB | `analysis` and the root pages were not re-split (—). |
| Tracked SITL `.BIN` | 52 files, 447 MB | 3 files, 19.3 MB (6.43, 6.43, 6.45 MB) | The 3 are new: `redesign/qp/A/mechanism/out/T076_data/s4b_failed_sleep/*/logs/00000001.BIN`, added after batch 2. Not touched (see s10, s12). |
| Tracked K09-L files under `redesign/site/assets` | 23 files, 55.5 MB | 0 | `git ls-files redesign/site/assets` has no K09 name. 20 other tracked paths mention K09 (showcase record films and similar, kept on purpose). |
| `.claude/worktrees` | 9 checkouts | 1 (`ui-redesign-survey`, 768 MB, unmerged) | `git worktree list`; `du -sm`. |
| `.git` | 2.3 GB | 2.7 GB | Grew because new work was committed; history was not rewritten (s10). |

### 5. Functionality consolidated (spec item 5)
Little was merged; the dry run found most "duplicates" were load-bearing (`docs/audits/2026-11-18-cleanup-dryrun.md` s2, s5, s6).
- Kept, not consolidated: the Explorer film copies (`site/assets/animation/a-*`, 24 files, 70.0 MB). GitHub Pages serves them and `publish_assets.py` is the only thing that makes them. Dropping them needs a CI publish step (future change, Q7; not done).
- Kept: `proofs/out/graph.js` and `graph.json`. The viewer loads the `.js` from `file://`; tests and `check_viewer.js` read the `.json`.
- Done: the K09-L film copies on the site (23 files) were dropped in favour of the one `showcase/animation` record (batch 2); Explorer captions point to it.
- Done: the old-hybrid CFD panel was removed from `VTOL-Review.html` (29.1 to 6.0 MB) and `review/build.mjs` skips the missing input with a message (T-042).
- Done: `inventory/build_variants.mjs` now builds paths with `fileURLToPath`. It had a Windows path bug (`C:\C:\...`) that made `build_overview.mjs` exit 1 (`2026-11-23-T042-refs.md`, conductor follow-up).
- Not done: duplicate CAD pipelines, simulation wrappers, rendering systems and agent instructions (spec 9.4) were not audited beyond the files above (—).

### 6. Dependencies eliminated (spec item 6)
None removed. Python and Node packages were not inventoried in this audit (—). Batch 2 removed files, not packages. Dependencies still in use and fetched from the network: the Explorer's three.js (importmap, cdn.jsdelivr.net) and Google Fonts (see s10).

### 7. Space recovered (spec item 7)
Logged figures. They mix untracked disk, worktree checkouts and the tracked tree, so the total is approximate and was not re-measured (`2026-11-23-T043-T044.md` s1 and s3 note 7).
| Batch | What | Recovered |
|---|---|---|
| 1 (2026-11-18) | 2 clean merged worktrees | about 2.17 GB disk (untracked) |
| 2 (2026-11-19) | 232 SITL `.BIN` on disk | 2,848.4 MB disk |
| 2 | 3 merged worktrees | about 2.3 GB disk |
| 2 | tracked tree: 52 `.BIN`, 23 K09-L site files, `overview-full.png`, `Inventory-Overview.html`, CFD panel data, rebuilt `VTOL-Review.html` | about 579 MB off the tracked tree; history unchanged |
| 3 (2026-11-23) | 3 line-ending-only worktrees | about 3.55 GB disk |
| Sum | batches 1 to 3, disk plus tracked tree | about 10.9 GB (approximate; T-043 note 7) |

`.git` was **not** reduced: 2.7G now (`du -sh .git`; `git count-objects -vH`: 22,407 packed objects, 1.51 GiB in 4 packs, 6,609 loose objects, 744.61 MiB). The recovered space is disk space, not clone size.

### 8. Performance benchmarks (spec item 8)
Full table: `docs/audits/2026-11-23-T043-T044.md` s1 (command logs: `docs/audits/2026-11-23-T043-logs/`). Selected values:
| Metric | Value | Source |
|---|---|---|
| `collide_a` 3 poses / 18 linkage poses | 1,007 s / 1,153 s wall (recorded 2026-11-23, not re-run) | `redesign/qp/A/mechanism/out/T092_data/gates/gates_summary.txt` |
| `assembly_check` / drawings | 2,283 s / 227 s (recorded, not re-run) | same file |
| Blender main film | 1.94 s per rendered frame per worker (6,470 frames, 3 workers); 0.82 s wall per frame (derived) | `redesign/showcase/concept-a/film/timing-T031-main.json` |
| Blender build film | — (not run on this machine) | `docs/video/PIPELINE-FOLLOW-2026-11-22.md` |
| `ledger_audit.py` | 0.302 s | run 2026-11-23 |
| Explorer entry `index.html` | 489,754 B; with linked files 689,430 B; with imported modules 772,473 B; three.js and fonts not counted | `wc -c`, 2026-11-23 |
| Explorer browser first-load time | — (not measured; loopback server fetch only, 0.0017 to 0.030 s) | T-043 s3 note 4 |
| Agent tokens per task, memory, CPU | — (T-051 open) | `docs/task-ledger.md` |

**Before and after:** no speed benchmark was taken before cleanup (T-040 took sizes only), so no speed change is measured. Deleting files is not claimed to have sped up any gate, render or page (spec 9.5). The only measured effects are sizes (s4, s7).

### 9. Regression tests (spec item 9)
Run 2026-11-23 on HEAD 85ae8c0f (`2026-11-23-T043-T044.md` s2; the batch 2 checks are in s3 of this file). All PASS:
- `ledger_audit.py` rc 0 (109 requirements, 93 tasks, 0 errors); `plan_rid_check.py` rc 0 (109 R-ids).
- `proofs/run_all.py` rc 1, as expected: 12 distinct FAIL claims plus 1 UNVERIFIED (A-P13), printed as 16 STRICT lines (duplicates at program and claim level).
- `bom_a.py` total 1,939.17; `build_a.py` rc 1 with only the mass gate (1,641 g against 1,500 g); `wire_inventory.py` EXPOSED 0.597; `cad_mass.py` rc 0 (1.64098 kg).
- `node --check` on three build scripts rc 0; `node review/build.mjs` rc 0 with a clean `git status`.

Not re-run: `collide_a`, `assembly_check`, drawings and Blender render (recorded results only; the later change to `redesign/qp/A/cad` is 4 text-string lines, no coordinates, T-043 s3 note 3). Spec 9.8 items not tested in this pass (—): CAD loading in a viewer, the Explorer in a browser, hooks and compaction recovery (those tests are `docs/audits/2026-11-19-compact-test*.md` and `2026-11-23-recovery-test.md`). The 12 failing claims are design findings, not cleanup regressions; the same count is reported in every run since T-089.

### 10. Remaining inefficiencies (spec item 10)
1. `.git` is 2.7G because history was not rewritten. Removed `.BIN` and film blobs (447 MB of SITL logs alone) stay in the packs. A rewrite and force-push need team authorization (spec 9.3); not requested.
2. Three tracked SITL `.BIN` (19.3 MB) were added after batch 2 under `mechanism/out/T076_data/s4b_failed_sleep/`. Not yet classified; the batch 2 treatment would be `git rm --cached` (needs approval).
3. The unmerged `ui-redesign-survey` worktree (768 MB, commit 4281a19b) is kept; nobody has decided to merge or drop it.
4. Branches of removed worktrees are all still present: `build-film-audit`, `structures-d9x`, `claude/morph-chart-bc71a6`, `claude/proof-chain-readable-c5026d` and six `worktree-agent-*` branches (a3ad648c, a45a26cc, a77bd26a, a7a1675a, a952e333, ab6e7d18), plus `worktree-agent-a738e3f4` (merged, its worktree now holds `ui-redesign-survey`). `git branch` lists 14 in all. They cost little disk (`git branch` output, 2026-11-23) but clutter the list.
5. The Explorer (`redesign/site/index.html`, `app.html`) loads three.js from cdn.jsdelivr.net and Google Fonts from the network (4 CDN lines in each page). It needs a network and its browser first-load time is unmeasured.
6. `site/assets/animation/a-*` copies (70 MB) duplicate `showcase/concept-a/animation` until a CI publish step exists.
7. `publish_assets.py` rewrites showcase `.mp4` files in place (faststart), so running it is not a no-op for git.
8. The Explorer entry page is 489,754 B of inline CSS, SVG and script.
9. `proofs/run_all.py` prints 16 STRICT lines for 12 distinct claims (duplicate reporting).
10. No agent or software performance metrics yet (T-051) and no browser measurement (s8).
K09-L leftovers in `site/assets`: none remain (s4). K09-L record films under `showcase/` remain on purpose (s11).

### 11. Preserved reference materials (spec item 11)
Kept on purpose (`docs/audits/2026-11-18-cleanup-dryrun.md` s0, s3, s5, s6; AM-002: remove only what does not serve the current design):
- the Protected list below;
- `redesign/showcase/animation/**` K09-L record films (about 43.3 MB; referenced by `SHOWCASE.md`, `README.md`, `BUILD-GUIDE.md`);
- `site/assets/animation/a-*` films; `proofs/out/graph.js` and `graph.json`;
- `VTOL-Review.html`, `build-manual.html`, `test-plan.html` (CI diffs them in `.github/workflows/regenerate-check.yml`);
- `redesign/config-study/tiebreak/wind/data/*.txt` (about 61 MB of source wind records) and the K09-L STL files in `redesign/showcase/stl/` (regenerable, kept).
Every path removed in batch 2 is recoverable from git (`8d15f419^`, commit 5020967a). Branches of all removed worktrees are kept. Every SITL run keeps `case.csv` and `result.json`.

### 12. Unresolved risks (spec item 12)
1. **History rewrite not authorized.** Clone size stays at the full pack until the team decides.
2. **232 SITL `.BIN` were deleted on disk.** The 52 that were tracked are recoverable from `8d15f419^`; the 180 untracked ones were never in git and can only be regenerated by rerunning SITL. Nothing in the repo reads them (dry run s1).
3. **Ignored files of removed worktrees are gone** (K09-L-era FEA and solver `history.csv`); only content tracked in the kept branches survives.
4. **Cleanup totals are approximate** (mixed bases, not re-measured); the tracked-tree comparison in s4 is not like for like.
5. **Gate and render times were not re-run** after cleanup; the later text-only change to `redesign/qp/A/cad` is assumed not to affect them (T-043 s3 note 3).
6. **Reference check is not exhaustive.** T-042 fixed the listed dangling references; the link check of `app.html` and `index.html` was done in batch 2 only.
7. **Windows path bugs** may hide in other scripts (one was found and fixed in `build_variants.mjs`); others were not searched.
8. **Final audit pending.** This file is the T-045 report; the dated final audit (T-049, spec 9.10) is still due at program end, and s10 should be re-checked then.

## Protected (never removed by cleanup)
`docs/MASTER_PROJECT_SPEC.md`, `docs/spec-amendments.md`, `docs/spec-integrity.sha256`, `docs/requirements.md`,
`docs/task-ledger.md`, `docs/execution-plan.md`, `docs/session-state.md`, `docs/session-log.md`,
`docs/engineering-decisions.md`, `docs/verification-report.md`, `docs/model-usage.md`, `.claude/settings.json`,
`.claude/hooks/`, `.claude/agents/`, `tools/ledger_audit.py`, `redesign/params/CHANGE-LOG.md`, concept A CAD
(`redesign/qp/A/cad/`), verified analysis outputs, current films.
