# Cleanup dry run, 2026-11-18 (T-041a, parents R-REPO-02, R-REPO-03)

Read-only. Nothing was deleted, moved, untracked or committed. The only file written is this one.
Sizes are decimal MB (1 MB = 1,000,000 bytes) as measured by `du -sb` / `stat`. "Working tree" means bytes on disk.
Labels: **Protected** (needed by a page, test, CI check or record), **Regenerable** (rebuilt by a script in the repo),
**Obsolete-duplicate** (same content elsewhere, or unreferenced), **Uncertain** (could not confirm; needs Dillon).

## 0. Summary

| Class | Items | Working-tree MB reclaimable if the proposed action runs |
|---|---|---|
| Protected | site `a-*` copies (70.0); showcase concept-a films (70.1); K09 showcase films (43.3); proofs `graph.js` (10.2) and `graph.json` (10.2); `cfd3d_viz.json` (23.1); `VTOL-Review.html`, `build-manual.html`, `test-plan.html` (38.0); unmerged worktree `ui-redesign-survey` (783.2) | 0 |
| Regenerable | tracked SITL BIN, 52 files (447.2, reclaimable only if local copies are deleted); untracked SITL BIN, 180 files (2,401.2); `__pycache__` (5.9) | 2,407.1 |
| Obsolete-duplicate | site K09-L leftovers, 23 files (55.5); 5 clean, merged worktrees (4,310.0) | 4,365.5 |
| Uncertain | `overview-full.png` (24.7); `Inventory-Overview.html` (5.9); 3 merged worktrees with the same uncommitted `.bat` edit (3,634.8) | 0 counted (3,665.4 if Dillon approves) |

Corrections to `docs/repository-audit.md` section 2:
- The 447 MB figure is only the 52 BIN files that git tracks. The working tree holds 232 BIN files, 2,848.4 MB, because 180 more are git-ignored and untracked.
- `redesign/site/assets/animation` and `redesign/showcase/concept-a/animation` are not a clean "75 MB duplicate". 24 site files are byte-identical copies made by `publish_assets.py` (70.0 MB). The other 23 site files are K09-L leftovers that no script makes and no page references (55.5 MB).
- The two K09-L `k09l-build.mp4` files are different encodes (13.7 MB vs 28.1 MB), not one file.
- `overview-full.png` has no generator in the repo. The page that is referenced is `overview-full.jpg`.
- The root HTML pages are not "uncertain": `VTOL-Review.html`, `build-manual.html` and `test-plan.html` are regenerated and diffed by CI.
- The tracked BIN files are git-tracked even though `.gitignore:126` ignores `redesign/qp/A/sitl/runs/`. They were force-added.

## 1. SITL run logs: `redesign/qp/A/sitl/runs/**/logs/*.BIN`

**Facts**
- 232 BIN files in 232 run folders, 2,848,403,456 bytes (2,848.4 MB), at `runs/<case>/logs/00000001.BIN`.
- Git tracks 52 of them (447,229,952 bytes, 447.2 MB). `git check-ignore` reports the other 180 as ignored (`.gitignore:126`). The tracked set is the `w_*` and `w4_*` cases (for example `w_ac60t`, `w4_h70t`). 563 files under `runs/` are tracked in all.
- Readers: no script reads a `.BIN`. `grep -rn "\.BIN\|dataflash\|\.bin"` in `redesign/qp/A/sitl` matched only `sock.bind` and two keep/delete filters for `eeprom.bin` and `mav.parm`. `run_case.py:17` and `run_fwd.py:22` delete old `.log`/`.csv` files from a run folder before a re-run; they do not read BIN files.
- Claims and docs: no claim, CSV, JSON or markdown cites a SITL BIN path. `redesign/review/QP-4/CLAIMS-FIX.md` and `FOLDIN.md` cite `sitl/results.jsonl` and the git-ignored `sitl/runs/`. `docs/video/PIPELINE-AUDIT.md` says nothing reads `case.csv`. `log_summary.py` and `docs/test/cards/*` concern real flight logs, not SITL.
- Summaries: all 232 run folders with a BIN also have `case.csv` and `result.json` (232 of 232). 119 also have `sum.json`.

**Classification**
- Tracked 52 BIN files: **Regenerable**. Their content is not cited, and the summaries cover them.
- Untracked 180 BIN files: **Regenerable**. Ignored and not in git.

**Proposed action (reversible)**
1. Tracked 52: `git rm --cached` on the 52 paths, then add `*.BIN` under the `runs/` rule. The local copies stay on disk. The blobs stay in history, so the 1.5 GiB pack does not shrink. History rewriting needs team sign-off (spec 9.3) and is not proposed here.
2. Untracked 180: keep, or move to external storage. Deleting them frees 2,401.2 MB. Hold until Dillon confirms no SITL BIN is needed as evidence.

**Regression check**
- `git ls-files | grep -c '\.BIN$'` returns 0 after step 1.
- `python -I redesign/qp/A/sitl/gather.py` still prints the case table from `result.json`.
- `python -I redesign/qp/A/proofs/run_all.py` runs (strict) and the claims still pass.
- Count BIN files after step 2 with `find redesign/qp/A/sitl/runs -name '*.BIN' | wc -l`.

## 2. Animation copies: `redesign/site/assets/animation/**` vs `redesign/showcase/concept-a/animation/**`

**Facts**
- `publish_assets.py` (lines 52 to 72) copies `showcase/concept-a/animation/*` to `site/assets/animation/` and `.../build/`, renaming `stage-NN` to `build/a-stage-NN`. It also runs `mp4_faststart.faststart(p)` on the source file in place, before the copy. No workflow runs it (grep of `.github` finds only `regenerate-check.yml`, which does not).
- `site/assets/animation`: 47 files, 125,548,740 bytes. `showcase/concept-a/animation`: 25 files, 70,059,314 bytes (24 films and posters plus `a-build.json`).
- 24 site files are byte-identical to showcase files (`cmp` confirmed `a-stage-01.mp4`; `git hash-object` matches for `a-how-it-flies.mp4`, `a-poster.webp`, `a-build.mp4`, `a-build-poster.webp`, and the stage clips). Total 70,010,272 bytes.
- Pages that use the `a-*` copies: `redesign/site/app.html` (lines 355 to 2043, `assets/animation/...?v=20261118c`) and `redesign/site/index.html`. Explorer links point to `davinciucberkeley-collab.github.io/DBF-Combined/redesign/site/assets/...` (`app.html:369`), so GitHub Pages serves the repo files directly. Other references (`redesign/qp/A/BUILD-GUIDE-A.md`, `docs/video/PIPELINE-AUDIT.md`, `README.md`, `redesign/SHOWCASE.md`) point to `showcase/...` or to the same `assets/animation/build/a-stage-NN.mp4` paths.
- The `.git` pack stores identical blobs once, so the 70 MB of identical copies costs working-tree disk only.

**Classification**
- `site/assets/animation/a-*` (24 files, 70.0 MB): **Protected**. Pages serves them and no build step recreates them.
- `showcase/concept-a/animation/*` (25 files, 70.1 MB): **Protected**. It is the source that `publish_assets.py` reads.

**Proposed action**
- None now. The "remove duplicate" idea is safe only after a CI step runs `publish_assets.py` on each push and the Pages source reads from that output. Until then the site copies must stay. Record that as a follow-up, not a cleanup.
- Side effect to note: `publish_assets.py` changes the showcase `.mp4` files in place (faststart). Re-running it is not a no-op on git.

**Regression check (for the future change)**
- Run `publish_assets.py`, then `git diff --stat -- redesign/site/assets/animation` must be empty.
- Check every `src=` and `data-src=` path in `redesign/site/app.html` and `index.html` resolves to an existing file.

## 3. K09-L film copies

**Facts**
- `showcase/animation/build/k09l-build.mp4`: 28,083,195 bytes, hash `6f939ef6`. Referenced by `README.md:58`, `redesign/BUILD-GUIDE.md:15`, `redesign/SHOWCASE.md`, and written by `render_build.py:1033`.
- `site/assets/animation/build/k09l-build.mp4`: 13,700,808 bytes, hash `7c576906`. Different file (different encode). No script in the repo makes it. No page references its path. `make_build_guide.py:57` maps any `k09l-build.mp4` link to an in-page anchor, so the site copy is not used.
- Other K09 site leftovers: `site/assets/animation/k09l-how-it-flies.mp4`, `poster.png`, and `build/stage-02..11.mp4/.png` (22 files, 41,837,660 bytes). `cmp` and the MP4 `moov`/`mdat` offsets show that `k09l-how-it-flies.mp4` and `build/stage-02.mp4` are the same encodes as the showcase files with the `moov` atom moved to the front (faststart). Same size, different bytes. The other 20 were not compared byte-for-byte. Their showcase counterparts are referenced by `BUILD-GUIDE.md:104-152` through `showcase/animation/build/stage-NN.*`.
- Showcase K09 keepers: `k09l-how-it-flies.gif` (9,718,351 bytes) and `k09l-how-it-flies.mp4` (4,852,942 bytes) are referenced by `redesign/SHOWCASE.md:66-68`.

**Classification**
- `showcase/animation/**` K09 films (about 43.3 MB for `k09l-build.mp4`, the GIF, the MP4 and `poster.png`): **Protected** (record; referenced).
- `site/.../k09l-build.mp4` (13.7 MB): **Obsolete-duplicate** (unreferenced, different encode of the showcase film).
- `site/.../k09l-how-it-flies.mp4`, `poster.png`, `build/stage-02..11.*` (41.8 MB): **Obsolete-duplicate** (unreferenced; same content as showcase files, moov relocated).

**Proposed action**
- `git rm` the 23 site K09 files (55.5 MB), keeping a local copy under the scratchpad or an external drive. Git history keeps the blobs. Because the moov-relocated copies are not identical blobs, the git pack also carries them, so removing them shrinks the working tree only.
- Do not touch the showcase K09 films.

**Regression check**
- `grep -rIn "site/assets/animation/build/k09l\|site/assets/animation/k09l\|assets/animation/build/stage-0[2-9]\.\(mp4\|png\)\|assets/animation/poster.png" redesign` returns nothing that is a live link (the `a-stage-NN` matches are not K09).
- Confirm the K09 `src=` paths in `site/app.html` and `index.html` are absent or unchanged, then run the link check from section 2.

## 4. `redesign/showcase/pages/overview-full.png`

**Facts**
- 24,697,557 bytes, tracked by git (1 file). Created 2026-11-14 01:16, with the batch of `overview-*.png` files.
- The only reference is in the audit itself. `redesign/SHOWCASE.md:173` links `showcase/pages/overview-full.jpg` (5.8 MB, 2026-11-11). Nothing links the `.png`.
- Generator: none found. The headless-browser screenshot code in `redesign/showcase/tools/render_showcase.py` (line 154) and `redesign/blender/annotate.py` (line 217) produces render images, not this page. The audit's "headless-Chrome" note is unverified.

**Classification**: **Uncertain** (unreferenced and no generator; the `.jpg` is the referenced one).

**Proposed action**: after Dillon confirms, move the `.png` out of the repo (`git rm`, keep a local copy). Keep `overview-full.jpg`.

**Regression check**: `grep -n "overview-full" redesign/SHOWCASE.md` resolves to an existing `.jpg`.

## 5. `redesign/proofs/out/graph.js` and `graph.json`

**Facts**
- Both tracked. `graph.js` 10,172,196 bytes, `graph.json` 10,172,100 bytes. Written together by `build_graph.py` (lines 501 to 509).
- `redesign/proofs/viewer/index.html` loads `model.js` and `app.js`. `app.js:17` sets `SOURCES.redesign = '../out/graph.js'`, which the page loads as a script (`window.PROOF_GRAPH`) so that it works from `file://`.
- `graph.json` is read by `redesign/proofs/viewer/check_viewer.js:21` (asserts the JSON equals the JS data), `redesign/proofs/test_proofs.py:47,126`, `build_graph.py:501` (diff against the previous build), and `app.js` accepts `?graph=<url of a graph.json>`.
- `redesign/qp/A/proofs/out/` has its own `graph.js` and `graph.json` (not in the audit list); `qp/A/cad/viewer_data_a.py` and `render_readable_a.py` read that `graph.json`.

**Classification**: `graph.js` **Protected** (the viewer loads it on file://). `graph.json` **Protected** (tests and the consistency check read it). Neither is a true duplicate to drop.

**Proposed action**: none. Dropping `graph.json` would need changes to `check_viewer.js`, `test_proofs.py`, and the `?graph=` option first.

**Regression check**: `node redesign/proofs/viewer/check_viewer.js` and `python -I redesign/proofs/test_proofs.py`.

## 6. `analysis/cfd3d/out/viz/cfd3d_viz.json` and the root HTML pages

**Facts**
- `cfd3d_viz.json`: 23,091,021 bytes, tracked. Written by `analysis/cfd3d/postprocess.py:485` (`pack`). Read by `review/build.mjs:83` (embeds it in `VTOL-Review.html`; the build logs "missing" and skips the panel if absent), `review/src/cfdviz.js`, and listed in `tools/vtol.py:95`.
- `VTOL-Review.html` (29,082,181 bytes, tracked). `index.html` at the root is a meta-refresh to it. `.nojekyll` is at the root, so GitHub Pages serves the root (the Pages source setting is not in the repo and is not confirmed). Built by `review/build.mjs`.
- `.github/workflows/regenerate-check.yml:43-50` runs the build and fails if `VTOL-Review.html`, `build-manual.html`, `test-plan.html`, `flight-software.html` or `templates.html` differs from the committed copy.
- `build-manual.html` (5,871,950 bytes) and `test-plan.html` (3,041,423 bytes): tracked, CI-diffed. `PRODUCT.md:40` names them as generated companion pages.
- `Inventory-Overview.html` (5,888,992 bytes): tracked. Built by `inventory/build_overview.mjs:392`. Cited in `DECISIONS.md:157` and `:195`. Not in the CI list. Not linked from `index.html`. It describes the v0.3.1 inventory.

**Classification**
- `cfd3d_viz.json` (23.1 MB): **Protected**. It is an input to the published review and regenerating it needs a full SU2 run. Whether the CFD panel should stay for the old hybrid concept is a Dillon decision; if it goes, the build must be changed first.
- `VTOL-Review.html`, `build-manual.html`, `test-plan.html` (38.0 MB together): **Protected**. Not "uncertain": CI checks them.
- `Inventory-Overview.html` (5.9 MB): **Uncertain**.

**Proposed action**: none now. For `Inventory-Overview.html`, ask Dillon whether v0.3.1 stays public; if not, `git rm` it and remove the build script's output target.

**Regression check**: `node review/build.mjs && git -c core.autocrlf=input diff --stat --exit-code -- VTOL-Review.html build-manual.html test-plan.html flight-software.html templates.html` (same as CI) must be empty. For `Inventory-Overview.html`, `node inventory/build_overview.mjs` then a diff.

## 7. `.claude/worktrees/*`

Every worktree is under `.claude/*` (ignored by `.gitignore:11`). `git branch --merged redesign/v1` was used for the merge check. Sizes are `du -sb` of the whole checkout, which is mostly tracked content recoverable from its branch.

| Worktree | Branch | Uncommitted | Merged into redesign/v1 | Ignored entries | Bytes | Class |
|---|---|---|---|---|---|---|
| agent-a3ad648c29da7b3df | build-film-audit | 0 | yes | 0 | 1,483,578,325 | Obsolete-duplicate |
| agent-a45a26cc3e280ea87 | structures-d9x | 0 | yes | 182 | 723,515,103 | Obsolete-duplicate (inspect ignored entries first) |
| agent-a738e3f4799ad7786 | ui-redesign-survey | 0 | **no** | 1 | 783,234,015 | Protected (unmerged) |
| agent-a77bd26a1685e113a | worktree-agent-a77bd26a1685e113a | 0 | yes | 33 | 709,965,776 | Obsolete-duplicate (inspect ignored entries first) |
| agent-a7a1675acd0e1edfe | worktree-agent-a7a1675acd0e1edfe | 0 | yes | 3 | 703,823,671 | Obsolete-duplicate (inspect ignored entries first) |
| agent-a952e3335f2d57495 | worktree-agent-a952e3335f2d57495 | 1 | yes | 1 | 718,722,924 | Uncertain |
| agent-ab6e7d188b427f2b2 | worktree-agent-ab6e7d188b427f2b2 | 0 | yes | 0 | 689,093,460 | Obsolete-duplicate |
| morph-chart-bc71a6 | claude/morph-chart-bc71a6 | 1 | yes | 1 | 1,456,041,778 | Uncertain |
| proof-chain-readable-c5026d | claude/proof-chain-readable-c5026d | 1 | yes | 3 | 1,460,047,332 | Uncertain |

- The uncommitted item in the three "Uncertain" worktrees is the same file in each: `tools/opencae-studio/launch_opencae.bat` (blob `7b5b6b9a81`, identical in all three, 107 lines changed and 107 added, so probably a line-ending rewrite). Check it before removing anything.
- Totals: Obsolete-duplicate 4,310.0 MB (5 worktrees), Uncertain 3,634.8 MB (3 worktrees), Protected 783.2 MB (1 worktree). Sum 8,728.0 MB, matching `du -sbc .claude/worktrees/*/`.

**Proposed action** (per worktree, after its checks pass): `git -C <wt> status --ignored` and inspect the listed ignored entries, then `git worktree remove <wt>`. The branch keeps the commits, so the content is recoverable with `git worktree add <path> <branch>`. Do not remove `ui-redesign-survey`. Do not remove the three "Uncertain" worktrees until the `.bat` change is resolved.

**Regression check**: `git worktree list`, `git branch --merged redesign/v1` before and after, `git -C <branch-worktree> rev-parse HEAD` equal to the branch tip for each kept worktree.

## 8. Other checks

- `git ls-files | grep -E '__pycache__|\.pyc$'`: 0 tracked. Good.
- `git status --porcelain` on the main worktree: empty at start. No untracked, not-ignored generated folder exists.
- Ignored generated items in the main worktree: 90 `__pycache__` directories, 5.9 MB (**Regenerable**), plus `redesign/collision/out/*.log`, `_job.json`, and several PNG renders under `manual-kit/out` (not measured). The `.git` directory is 2.44 GB.

## 9. Open questions for Dillon (none blocks the dry run)

1. Keep the 180 untracked SITL BIN logs locally, or move them out? (Section 1.)
2. Approve `git rm --cached` on the 52 tracked BIN files? (Section 1.)
3. Should the K09-L site copies (23 files) go? (Section 3.)
4. Should `overview-full.png` go? (Section 4.)
5. Is the v0.3.1 `Inventory-Overview.html` still public? Keep the CFD panel in `VTOL-Review.html` for the old hybrid concept? (Section 6.)
6. What is the `launch_opencae.bat` change in three worktrees? (Section 7.)
7. Should the site animation copies become a CI build step (`publish_assets.py` output) so the duplicate can go later? (Section 2.)

## 10. Not done

Nothing was deleted, moved, untracked, committed, or pushed. No history was rewritten. The `.git` pack (1.5 GiB in the audit, 2.44 GB for the whole `.git` directory) was not touched.
