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

## T-104 layout cleanup (2026-11-23)

- **Root entries:** before 31 (plan s1.1); after 23 counting hidden entries (`ls -A | grep -v '^\.git$' | wc -l`) and 17 visible (`ls | wc -l`).
- **Tracked files:** before 15508 (`git ls-tree -r --name-only 73656c93 | wc -l`); now 15519 (`git ls-files | wc -l`, measured before the U7 commit; U7 adds none).
- **Commits:** U1 no commit (empty `NVIDIA Corporation/` folder removal, untracked); U3 `51622f1e` (launcher renamed to `START-EXPLORER.bat`, link checker); U4 `9825669a` (archive README and path map); U5 `085fc2bf` (C0 and v0.3.1 material moved to `archive/c0`); U6 `cd92df91` (redirect stubs for the old root pages, root index to `redesign/site`); U7: see `git log` (README directory map, concept A entry in `redesign/README.md`, old entry page kept as `redesign/README-K09L.md` by `git mv`).
- **What moved:** every old path to new path is in `docs/archive-path-map.md`.
- **Deliberately not done:** U8 (moving the K09-L folders inside `redesign/`; decision D7 stops after U7); D4 (`redesign/review` stays); D6 (worktree).
- **Note:** `python -I redesign/qp/A/proofs/run_all.py` rewrites `redesign/qp/A/cad/model/*/interfaces.json` as a side effect (observed in U5, not investigated).
- **Link check:** 2 broken links remain (`redesign/qp/A/sitl/SITL-FLIGHT.md` from `redesign/site/index.html` and `app.html`), both already in the baseline. Proof-graph refs of the form `redesign/README.md#joints-both-sides-of-every-interface` (`redesign/proofs/out/`, `redesign/team/A2/`) already had no such anchor in the old README (checked: none in `redesign/README-K09L.md`); generated files were not edited.

## Final audit 2026-11-24 (T-049, R-REPO-10, R-REPO-08)

Measured 2026-11-24 on branch `redesign/v1`, HEAD `71cab7a2`. Sizes from `du -sh` (1024-based) unless stated; `ls-tree` and `du -b` sums are bytes. "—" = no before value in this file.

The working tree was not clean at measurement time. `git status --short` showed `?? redesign/qp/A/cad/out/glb/` (already present at session start). The regression commands in 13.2 then modified 10 `redesign/qp/A/cad/model/*/interfaces.json` files and `docs/session-log.md` (side effects, see 13.3).

### 13.1 Before / after table

| Metric | Before (this file) | After 2026-11-24 | Command (from the repo root) |
|---|---|---|---|
| Root entries, all incl. `.git` | 31 (T-104 section, plan s1.1) | 25 | `ls -A \| wc -l` |
| Root entries, visible | 17 (T-104 after) | 17 | `ls \| wc -l` |
| Root entries, excl. `.git` | 23 (T-104 after, `ls -A \| grep -v '^\.git$' \| wc -l`) | 24 = 7 hidden + 17 visible. The 7 hidden: 6 tracked (`.claude .gitattributes .github .gitignore .impeccable .nojekyll`) and the git-ignored `.env`. Whether T-104 counted `.env` is not verified. | `ls -A \| grep -v '^\.git$' \| wc -l` |
| Git-tracked files | 13,798 (T-040, a93f14da); 15,281 (T-045, 76894339); 15,508 (T-104, 73656c93) | 15,803 | `git ls-files \| wc -l` |
| Tracked tree size (sum of blob sizes at HEAD) | 1,489 MB, 13,798 files (T-040); 1,064.8 MB, 15,281 files (T-045, unit not stated) | 1,125,121,219 B = 1,125.1 MB (1,073.0 MiB), 15,803 files | `git ls-tree -r -l HEAD \| awk '{s+=$4; n++} END{print s, n}'` |
| Git object store | 22,407 packed in 4 packs, 1.51 GiB, 2,451 loose, 524 MiB (T-040); 6,609 loose, 744.61 MiB (T-045) | 5 packs, 2.17 GiB, 29,599 in pack; 689 loose, 46.82 MiB | `git count-objects -vH` |
| Working tree size excl. `.git` | ≈ 11.7 GB (T-040: `du -sh .` less `.git`, incl. 9 worktrees) | 4.5 GB | `du -sh --exclude=./.git .` (about 2 min) |
| `.git` on disk | 2.3 GB (T-040); 2.7 GB (T-045) | 2.7 GB | `du -sh .git` |
| Largest 10 tracked files | — (T-040 gave folder and type totals only) | largest 31,771,409 B; list below | `git ls-files -z \| xargs -0 du -b \| sort -n \| tail` |
| `.claude/worktrees` | 9 checkouts, size not measured (T-040); 1 checkout `ui-redesign-survey`, 768 MB (T-045, `du -sm`) | 250 MB (`du -sm`): one leftover folder `agent-a738e3f4799ad7786`. `git worktree list` shows only the main checkout, so the folder is not a registered worktree. | `du -sh .claude/worktrees`; `du -sm .claude/worktrees`; `git worktree list` |
| `__pycache__` directories (excl. `.git`) | — | 23 | `find . -path ./.git -prune -o -type d -name __pycache__ -print \| wc -l` |
| Untracked files, excl. `.env` | — | 2 files: `redesign/qp/A/cad/out/glb/_job_glb.json` and `redesign/qp/A/cad/out/glb/glb_report.json` (git lists 2 paths) | `git ls-files --others --exclude-standard \| wc -l` |
| Untracked size, excl. `.env` | — | 14,507,145 B (14.5 MB) | `git ls-files --others --exclude-standard -z \| tr '\0' '\n' \| grep -Ev '(^\|/)\.env$' \| tr '\n' '\0' \| xargs -0 du -cb \| tail -1` |

Largest 10 tracked files (bytes, `git ls-files -z | xargs -0 du -b | sort -n | tail`; no before list exists, so each before value is "—"):

| Bytes | Path |
|---|---|
| 16,440,265 | `archive/c0/concepts/variants/a3/fusion/a3.f3d` |
| 19,785,812 | `redesign/showcase/concept-a/animation/a-build.mp4` |
| 19,785,812 | `redesign/site/assets/animation/build/a-build.mp4` (same size as the line above: a copy, kept per s5) |
| 22,760,084 | `redesign/showcase/stl/k09l-assembly.stl` |
| 27,929,485 | `archive/c0/concepts/variants/a2/fusion/a2.step` |
| 28,083,195 | `redesign/showcase/animation/build/k09l-build.mp4` |
| 28,409,920 | `redesign/showcase/concept-a/film/film-main-1080p60.mp4` |
| 28,890,336 | `archive/c0/inventory/fusion/VTOL_Fusion.step` |
| 30,859,527 | `archive/c0/concepts/variants/a1/fusion/a1.step` |
| 31,771,409 | `archive/c0/concepts/variants/a3/fusion/a3.step` |

### 13.2 Regression commands (exit codes and key lines)

| Check | Command | Exit | Key line | Before (T-045, s9) | Result |
|---|---|---|---|---|---|
| Ledger | `python -I tools/ledger_audit.py` | 0 | `113 requirements, 105 tasks, {... 'VERIFIED COMPLETE': 89, 'BLOCKED': 5, 'EXPLICITLY DEFERRED': 5, 'IN PROGRESS': 2, 'NOT STARTED': 4}; 0 errors` | 109 requirements, 93 tasks, 0 errors | PASS (counts grew with new tasks) |
| Proof claims | `python -I redesign/qp/A/proofs/run_all.py` | 1 | 20 `ERROR: STRICT ...` lines: 18 contain `FAILS`, 2 are `UNVERIFIED` (A-P6 `CL-A-STALL`, A-P13 `CL-A-FLUTTER-ELEVON-NOM`). The literal text `STRICT FAIL` does not occur; the count is `grep -c 'ERROR: STRICT'` = 20 and `grep 'ERROR: STRICT' \| grep -c FAILS` = 18. | 12 distinct FAIL claims plus 1 UNVERIFIED, printed as 16 STRICT lines | rc 1 is expected while claims fail. **Count rose**: 18 FAIL lines against 12, and 2 UNVERIFIED against 1 (see 13.3). |
| BOM | `python -I redesign/qp/A/bom_a.py` | 0 | `G7 (...): FAIL (total 1,939.17, +30 % margin -29.68)` | total 1,939.17 | PASS, total unchanged |
| Session-start hook | `echo '{"source":"startup"}' \| python -I .claude/hooks/recovery.py session-start` | 0 | `DBF master program recovery ...` | — | PASS (side effect: one line appended to `docs/session-log.md`) |
| Site JS syntax | `node --check redesign/site/<f>.js` for `fea-view.js`, `model.js`, `replay.js`, `site.js`, `viewer.js` | 0 for each of the 5 | no output | rc 0 on 3 build scripts (different files) | PASS (no before value for these files) |
| Link checker (T-104 U3) | `python -I docs/audits/2026-11-23-T104-linkcheck.py` | 0 | `2 broken`: `redesign/site/index.html -> redesign/qp/A/sitl/SITL-FLIGHT.md` and `redesign/site/app.html -> redesign/qp/A/sitl/SITL-FLIGHT.md` | 2 broken (T-104 baseline, `docs/audits/2026-11-23-T104-linkcheck-baseline.txt`) | PASS, same 2 broken links, none new. The checker is in `docs/audits/`, not `tools/`; `find tools -iname '*link*'` finds nothing. |

### 13.3 Regressions and side effects

1. **Proof claim count rose.** `run_all.py` prints 18 FAIL lines and 2 UNVERIFIED, against 12 FAIL and 1 UNVERIFIED in s9. The FAIL lines include `CL-A-MASS-PRED` (1.881 kg, margin -28 %), `CL-A-HORN-BEARING-STALL`, `CL-A-LINKAGE-FREEPLAY` and `CL-A-VIB-GM-SHIFT`. This run does not show which are new since T-045, and the brief's stop rule forbids fixing. These are design-claim findings, not cleanup regressions.
2. **Side effects of the regression commands (not reverted; the brief allows no edits):**
   - `run_all.py` rewrote 10 `redesign/qp/A/cad/model/*/interfaces.json` files (assembly, avionics, cage, fins, harness, landing, mechanisms, power, propulsion, wing). `git diff --stat` shows 10 files, 130 insertions, 645 deletions. The T-104 section records the same side effect. The run also printed `wrote ...\redesign\qp\A\params-A.json`; git status does not show that file as modified.
   - `.claude/hooks/recovery.py session-start` appended `- 2026-11-24T03:02:36-07:00 SessionStart source=startup session=?` to `docs/session-log.md`.
   - Git printed `LF will be replaced by CRLF` warnings for the rewritten `interfaces.json` files and other CAD model files. These are line-ending warnings from the working copy.
3. **Worktree leftover.** `.claude/worktrees` is 250 MB (768 MB at T-045). `git worktree list` shows only the main checkout, so the folder is unregistered. Removing it needs Dillon's approval; not done.
4. **Growth since T-045.** Tracked files rose from 15,281 to 15,803. The object store is now 2.17 GiB in packs (was 1.51 GiB) with loose objects down to 689 (was 6,609); `.git` on disk is unchanged at 2.7 GB. No history rewrite was done. The T-045 size unit was not stated, so the tracked-tree size change is not computed here.
5. **Rows with no before value** (`__pycache__`, untracked count and size, largest-10 list, node check per file) are shown as "—".

**Conductor note on s13.3 (2026-11-24).** The STRICT count did not regress. run_all prints 20 STRICT lines: 14 failing claims (the same set as before), 4 requirement-level roll-up lines (A-P1, A-D3, A-P10, A-P11), and 2 UNVERIFIED (A-P6 CL-A-STALL, A-P13 CL-A-FLUTTER-ELEVON-NOM). The earlier "16 lines" was counted while 12 claims were failing, before CL-A-STALL-PRED and CL-A-PITCH-USE were added (fix pass A, D-245). Correction (T-059 V-1): the interfaces.json rewrite was a real content change (645 lines deleted, cg_xyz_m null), most likely from two run_all processes running at once (T-049 and T-059): build_a writes interfaces.json in two passes, and pass 1 has no CGs. The T-059 reviewer restored the files with git checkout; my empty diff was read after that restore. Rule: run run_all and the gates one at a time, never in parallel.

## 14. Redundancy audit and speed measurements (2026-11-24)

Spec 9.4 and 9.5 follow-up to s5 and s8 (T-104 follow-up, rows 23-24 of `docs/audits/2026-11-24-T059-deliverables.md`). Measured on HEAD `71cab7a2`. Evidence: `git ls-files`, `git ls-tree -r -l`, `git grep` on imports and path strings (excluding `*/out/*`, `*.md`, `*.json`). Report only: nothing was deleted, moved or merged. "A uses it" means a script under `redesign/qp/A`, `redesign/showcase/concept-a` or `redesign/site` imports it or names its path. Items marked "(to confirm)" were judged from file headers and grep hits, not by reading every line.

### 14.1 Redundancy audit (report only)

**A. CAD pipelines**
| Paths | What overlaps | A uses it? | Recommendation | Risk |
|---|---|---|---|---|
| `redesign/fusion/` (25 .py, 0.3 MB: `build_all.py`, `check.py`, `backends/stub_backend.py`, `fusion_backend.py`) vs `redesign/qp/A/cad/model/*/fusion/*.py` | Not a duplicate: the K09-L generic builder is the engine, A's modules are its input. `fusion_backend.py` (real Fusion 360) is not called from A; only `StubBackend` is. | Yes: `qp/A/cad/build_a.py` lines 11-21 and `collide_a.py` lines 19-23 import `build_all` and `StubBackend`; `build_a.py` line 38 runs `fusion/check.py`. Also `wire_inventory.py`, `proxy_collide.py`, `collide_glb_a.py`, drawings and two landing scripts match. | keep. `fusion_backend.py` and `BuildAll/` are archive candidates once a grep confirms no A caller. | Medium: a move breaks `build_a.py`, `collide_a.py`, `wire_inventory.py`, `proxy_collide.py`. |
| `archive/c0/fusion/` (22 files: `build_vtol_fusion.py`, `build_hardware_fusion.py`, `render_animations_fusion.py` ...), `archive/c0/cad/`, `archive/c0/concepts/variants/*/fusion` (STEP up to 31.8 MB) | v0.3.1 Fusion scripts: the same job as `redesign/fusion` plus `qp/A/cad`, for the old hybrid. | No. Nothing outside `archive/c0` names it (grep). | keep (already archived; spec 9.2: do not assume old designs are useless). The 5 largest STEP/F3D files (about 135 MB) are delete-after-OK candidates only. | Low for function; `.git` does not shrink (s10). |
| `redesign/qp/A/cad/` (19 .py) | Internal overlap: `collide_a.py` (stub bodies), `collide_glb_a.py` (exported GLB), `proxy_collide.py`, and `showcase/animation/assembly_check.py` (about 1,900 lines) all drive the `collision/collide.py` machinery on the same model. They are gates on different inputs, not copies. `a_assembly_plan.py` and `showcase/animation/assembly_plan.py` overlap by name (to confirm). | Yes, all. | merge candidate, low priority: one gate driver with several inputs. A merge would not save run time (the gates cost 227 to 2,283 s each, s8). | Medium: they are the proof gates (CLAUDE.md hard constraint). |
| `redesign/collision/` (3 .py, 0.1 MB) | K09-L collide, imported unmodified by `collide_a.py`, `assembly_check.py`, `a_collide_blender.py`. | Yes. | keep | Medium. |
| `redesign/viewer/` (19 files, 1.4 MB, `build_data.py`, demo aircraft in `data/aircraft`) vs `redesign/site/viewer.js` plus `site/data/viewer-data.js` | Two three.js assembly viewers. The README says `redesign/viewer` shows a generic demo aircraft; the Explorer has its own. | `qp/A/cad/viewer_data_a.py` mentions the folder; it writes the Explorer data (to confirm whether it also feeds this viewer). | archive candidate, delete-after-OK. | Low. `redesign/index.html` may link it (check before moving). |
| `redesign/blender/out/aircraft/glb/*.glb` (8.96 MB assembly, 5.4 MB harness, others) vs A's `site/assets/concept-a.glb` (11.8 MB) and `concept-a.opt.glb` (2.5 MB) | K09-L GLB outputs next to A's. | No. Only an example path in the `fea_coverage_render.py` docstring and in `redesign/viewer/build_data.py`. | keep the `redesign/blender` scripts (A imports `blender_backend.py`); the K09-L `out/aircraft/glb` files are delete-after-OK (about 17 MB, regenerable). | Low. |
| Blender builders: `redesign/blender/{render_figures,render_kit,explode,annotate,export_glb}.py` vs `showcase/tools/render_showcase.py`, `showcase/animation/render_animation.py`, `render_build.py`, `showcase/concept-a/render_build_a.py` | Several Blender entry points that each build scene, lights and world. `render_animation.py` copies lighting and world code from `render_kit` and says so in comments (lines 216, 221, 682). | `blender_backend.py` is imported by `collide_glb_a_blender.py`, `render_animation.py`, `render_build.py`. `render_figures.py`, `render_kit.py`, `explode.py`, `annotate.py`: no A caller found. | merge (later): move shared scene setup into `blender_backend.py`; archive `render_figures.py` and `render_kit.py` after OK. | Medium: a render regression costs hours to detect (s8). |

**B. Simulation wrappers**
| Paths | What overlaps | A uses it? | Recommendation | Risk |
|---|---|---|---|---|
| `redesign/team/{B2,B3,B4,C2,C4,C5,E1}/**` (9,922 tracked files, 212.2 MB incl. all of `team`, 182 .py) | K09-L team simulation code. `team/C5/sim/landing_sim3d.py` is the parent of `qp/A/structures/landing_a.py`; `team/C4` is the method source of `fe_a.py`. A copied and rescaled them; the docstrings say "adapted, standalone". | No imports; docstring mentions only (`fe_a.py`, `fe_a_iter1.py`, `landing_a.py`). | keep as record (or archive the folder as a unit). Merging is not possible without re-validating A. | Low: large, no live caller, but old K09-L numbers cite it. |
| `redesign/qp/A/structures/` (40 .py, 12 `landing_*`) | `landing_a.py` is the engine (17 referrers in `qp/A`). `landing_centre_a`, `landing_lean_scan_a`, `landing_path_a`, `landing_path_options_a`, `landing_side_a`, `landing_sitl_records_a`, `landing_tip_options_a` are one-purpose studies with one or a few referrers; `landing_nodes_b.py`, `landing_tip_b.py`, `landing_sitl_env_a.py` have 0 referrers. `fe_a.py` sits beside `fe_a_iter1.py` (iteration 1 kept). | Yes (proof claims). | keep the engine; the 3 orphans and `fe_a_iter1.py` are archive candidates (delete-after-OK; they are record scripts for cited results). | Low to medium: D-243 and AR-014 cite their output. |
| `qp/A/sims3d/` (4 .py) vs `qp/A/sitl/` (18 .py) vs `qp/A/mechanism/*.py` (6) | `sims3d/run_landing_traces.py` imports `landing_a` and restates the touchdown case list that its own comment says is "same list and order as sweep_t098.py / landing_a.py". `export_flight.py` re-reads SITL output already summarised by `sitl/gather.py` and `fwd_sum.py`. | Yes (T-105). | merge candidate: `run_landing_traces.py` could import the case list from `landing_a.py`. | Low. |
| `qp/A/sitl/` | `run_case.py` (hover) and `run_fwd.py` (forward flight) are two drivers for ArduPlane SITL with the same plant; `jobq.py` queues `run_fwd`; `wsum.py`, `fwd_sum.py`, `gather.py` each summarise runs; `fu_*` are four follow-up reports. | Yes. | merge (low value): one runner with a mode flag, one summary script. Not worth doing unless SITL is rerun. | Low. |
| `qp/A/mechanism/out/T0*_data/` | 218 tracked `.py` among 1,578 files, 90.3 MB, mostly frozen before/after code copies (`a_build_steps_*backup.py`, `structures_a_before.py`); `a_build_steps.py` exists in 6 places. | No (data folders, not imported). | archive or delete-after-OK: keep results, drop the code copies (git history has them). Largest: `T076_data` 20.8 MB, `T071b_data` 16.4 MB, `T073_data` 15.4 MB. | Low, but decisions and AR entries cite these folders; check citations first. The three tracked SITL `.BIN` (s10 item 2) are in here. |
| `tools/opencae-studio/` (130 tracked files, 89 .py, 5.7 MB) | A separate FE/CFD app (CalculiX, SU2), overlapping `team/C2/fea`, `team/C4/sim` and `qp/A/structures/fe_a.py`. | No: `git grep opencae` outside its folder finds `.gitignore`, PROVENANCE.md, docs and `redesign/inputs/` only. | keep as a team tool; mark unused by A. | Low. |
| `tools/design_loop/` (3 .py) | Wraps `gen_params_a`, the claims scripts and `build_graph --strict`: a second route to what `run_all.py` runs. | It calls A; A does not call it (docs only). | keep (T-035 deliverable). | Low. |
| `redesign/proofs/build_graph.py`, `proofkit.py` vs `qp/A/proofs/run_all.py` | Not duplicates: `run_all.py` shells out to `build_graph.py --strict`. `redesign/proofs/examples/` is a generic demo aircraft used by `test_proofs.py`. | Yes. | keep; `examples/` is an archive candidate. | Low. |

**C. Rendering systems**
| Paths | What overlaps | A uses it? | Recommendation | Risk |
|---|---|---|---|---|
| `showcase/animation/render_build.py` plus `render_animation.py` (K09-L film) vs `showcase/concept-a/render_build_a.py` (A film) | Two build-film renderers; `assembly_check.py` and `assembly_plan.py` in `showcase/animation/` are shared. | A's film: `render_build_a.py`. The older two are still named by `concept-a/audit_film.py`, `qp/A/cad/a_build_steps.py` and `parts_links_a.py` (grep hits on path strings; to confirm which are imports). | merge (later): one renderer parameterised by model root. Keep both now. | Medium: renders take hours (1.94 s per frame per worker, 6,470 frames, s8). |
| `showcase/drawing/make_sheet.py` (K09-L sheet) vs `showcase/concept-a/make_sheet_a.py` and `qp/A/drawings/*` (`make_drawings_a.py`, `compose_drawings.py`, `render_drawings_blender.py`) | Two drawing generators for A (a general-arrangement sheet in `make_sheet_a.py`, the drawing set in `qp/A/drawings`); `render_drawing.py` is shared (to confirm how much of the output overlaps). | `make_sheet.py`: K09-L only. | merge: name one canonical A drawing path, archive `make_sheet.py`. | Low to medium. |
| `showcase/_work/*.json` (16) vs `showcase/concept-a/_work/*.json` (15); `blender/specs/showcase.json` vs `showcase-a.json` | K09-L and A scene specs side by side; `render_animation.py` still reads `specs/showcase.json`. | A set: yes. K09-L set: record. | keep; label the K09-L set as record. | Low. |
| `redesign/showcase/renders/hero-iso.png`, `showcase/_work/hero-iso.png`, `site/assets/renders/hero-iso.png` | Byte-identical (2.34 MB each, equal blob id). | n/a | merge: keep one tracked copy, regenerate the others (delete-after-OK). | Low. |

**D. Site generators** (`redesign/site/`, 14 .py including `ui-review/gen/*`)
| Paths | What overlaps | A uses it? | Recommendation | Risk |
|---|---|---|---|---|
| `make_index.py`, `make_build_guide.py`, `make_proof_embed.py`, `make_drawing_gallery.py`, `make_morph_sketches.py`, `make_sims_view.py`, `make_replays_view.py`, `sync_bom_a.py`, `sync_status_a.py` | Each patches a different part of `app.html`; `make_index.py` then copies it to `index.html`. `make_build_guide.py` renders the guide that `qp/A/make_build_guide_a.py` writes (a chain, not a copy). | Yes. | keep | Low. |
| `sync_bom_tab.py` vs `sync_bom_a.py` | Both rebuild the BOM tab. `sync_bom_tab.py` reads K09-L `team/I1/BOM.csv`; `sync_bom_a.py` reads `qp/A/BOM-A.csv`. `git grep` finds no caller of `sync_bom_tab.py` outside its own docstring and `docs/audits`. | No. | archive candidate, delete-after-OK. | Low. |
| `ui-review/` (3 concept pages, 4 .py, `mwrap.html`) | The UI survey concepts; one direction was merged (AM-043). | No. | archive once the UI decision is final. | Low. |
| `redesign/proofs/viewer/` vs `redesign/site/proofs/` | Two copies of the proof-graph viewer (`app.js`, `model.js`, `3d-force-graph.min.js`, `force-graph.min.js`). `make_proof_embed.py` builds the Explorer page from `site/proofs`. | `site/proofs`: yes. `redesign/proofs/viewer`: written to by `build_graph.py` output paths and checked by `check_viewer.js` (s5). | merge: one viewer folder; `check_viewer.js` and the generator must follow. | Medium: the viewer loads `graph.js` from `file://` (s5). |
| Root pages `Concept-Models.html`, `VTOL-Review.html`, `build-manual.html`, `flight-software.html`, `templates.html`, `index.html` vs `archive/c0/*.html`; `redesign/index.html` | After T-104 U5/U6 the root pages are redirect stubs and the full copies are in `archive/c0`. `redesign/index.html` is a second entry page. | n/a | keep (stubs are the redirect). | Low. |

**E. Duplicated assets**
Measured with `git ls-tree -r -l HEAD`, grouping identical blob ids: 1,904 files sit in groups of identical content (193.2 MB counting every copy). **1,318 are extra copies totalling 98.8 MB**: 86.6 MB (114 files) in `redesign/site`, 6.2 MB (479) in `redesign/qp`, 3.3 MB (685) in `redesign/team`, 2.3 MB (1) in `redesign/showcase`, 0.2 MB in `archive/c0`.
| Paths | What overlaps | A uses it? | Recommendation | Risk |
|---|---|---|---|---|
| `redesign/site/assets/animation/**` (24 files, 70.0 MB) vs `redesign/showcase/concept-a/animation/**` | Byte-identical film copies (`a-build.mp4` 19.8 MB, 10 stage clips, `a-how-it-flies.mp4` 4.8 MB, posters). `publish_assets.py` makes the site copy and is the only writer. | Yes: the Explorer serves `site/assets`. | keep until a CI publish step exists (s5, s10 item 6); then delete the site copies after OK and publish from CI. | Medium: GitHub Pages breaks without them. |
| `site/assets/renders`, `drawings`, `sims3d`, `plots` (rest of the 105.8 MB, 269 files in `site/assets`) | Web-size derivatives of showcase and drawing outputs, made by `publish_assets.py` and `make_drawing_gallery.py`. | Yes. | keep | Low. |
| `qp/A/**/out` and `*_data` duplicates (479 extra files, 6.2 MB); `team/**` (685 extra files, 3.3 MB) | Repeated small outputs, per-round backups. | n/a | `mechanism/out` code copies: see B. The rest is not worth review time. | Low. |
| `site/assets/concept-a.glb` (11.8 MB) beside `concept-a.opt.glb` (2.5 MB) | `viewer_data_a.py` (line 9) keeps the plain GLB "for the record and for other tools"; `collide_glb_a.py` uses it as its default input (line 49). | Yes (gate input). | keep | Medium: the GLB gate reads it. |

**Not found redundant:** `tools/ledger_audit.py` and `tools/plan_rid_check.py` (different checks); `qp/A/bom_a.py` and `proofs/run_all.py` (different outputs). The other spec 9.4 items (repeated calculations, duplicate validation logic, conflicting configurations, overlapping agent instructions, repeated documentation) were not audited here (—).

### 14.2 Speed before and after

Setup: a throwaway `git worktree add --detach` of `c0caebf4` (perf-before; 2026-11-23 11:14, before the T-104 layout moves U1 to U7) and of HEAD `71cab7a2` (perf-after), both in the session scratchpad, not the main checkout. One script ran each command 3 times back to back (`subprocess.run`, wall time by `time.perf_counter`, Python 3.14.2, Windows 11). Other sessions may have been running, so noise is real. Both worktrees were removed with `git worktree remove --force`; `git worktree list` now shows only the main checkout.

| | perf-before `c0caebf4` | perf-after `71cab7a2` | Main checkout (HEAD, not timed) |
|---|---|---|---|
| Tracked files | 15,319 | 15,803 | 15,803 |
| Tracked size (`git ls-tree -r -l`) | 1,070.4 MB | 1,125.1 MB | 1,125.1 MB tracked; 4.5 GB working tree excl. `.git` (s13.1) |
| Root layout | old (`analysis cad concepts fusion inventory review sim` at root) | T-104 layout (K09-L material in `archive/c0`) | same as after |

Working-tree disk size of the two worktrees was not measured (`du` took over 3 minutes and was dropped).

| Command | Before: runs (s), median | After: runs (s), median | Median change |
|---|---|---|---|
| `python -I tools/ledger_audit.py` (rc 0 both) | 0.077, 0.055, 0.055; **0.055** | 0.233, 0.058, 0.054; **0.058** | +0.003 s (+5 %), inside noise |
| `python -I redesign/qp/A/bom_a.py` (rc 0) | 0.043, 0.029, 0.029; **0.029** | 0.103, 0.029, 0.030; **0.030** | +0.001 s |
| `python -I redesign/qp/A/proofs/run_all.py` (rc 1 both: failing claims, expected) | 2.078, 1.253, 1.228; **1.253** | 3.140, 1.254, 1.302; **1.302** | +0.049 s (+4 %); the first run of each is a cold start |
| `redesign/site/make_index.py` (rc 0) | 0.056, 0.045, 0.043; **0.045** | 0.241, 0.050, 0.049; **0.050** | +0.005 s |
| `redesign/site/make_build_guide.py` (rc 0) | 0.071, 0.063, 0.061; **0.063** | 0.103, 0.059, 0.059; **0.059** | -0.004 s |
| `redesign/site/make_drawing_gallery.py` (rc 0) | 0.104, 0.280, 0.269; **0.269** | 0.139, 0.314, 0.227; **0.227** | -0.042 s; spread larger than the change |
| `redesign/site/make_proof_embed.py` (rc 0) | 0.332, 0.079, 0.093; **0.093** | 0.643, 0.093, 0.121; **0.121** | +0.028 s; spread larger than the change |
| `git status --short`, cold (first run in the fresh worktree) | **0.667** | **1.018** | HEAD 0.35 s slower cold |
| `git status --short`, warm (runs 2 and 3) | 0.055, 0.054 (median of all 3: 0.055) | 0.052, 0.054 (median of all 3: 0.054) | none |

`make_replays_view.py` and `make_sims_view.py` exist only at HEAD, so they have no before value and were not timed. The generators wrote their outputs inside the throwaway worktrees only.

**Interpretation.**
1. No speed improvement is measured. Warm results are equal within noise. Where HEAD is slower (ledger_audit +5 %, run_all +4 %, make_proof_embed +30 %, cold `git status` +50 %), the first-run outliers (0.1 to 3 s) are as large as the differences, so the honest reading is "equal or slightly slower", not a proven regression. The ledger, BOM and generator runs are dominated by Python start-up (about 0.03 s), so they cannot show a cleanup effect.
2. This is expected. Between the two commits the cleanup moved root files into `archive/c0`; none of these commands reads them. HEAD also has 16 more commits that added 484 tracked files and 54.7 MB and more ledger rows and claims (113 requirements and 105 tasks against 109 and 93 in s9). The comparison is "layout cleanup plus 16 commits of growth", not cleanup alone.
3. `c0caebf4` is itself after batch 2 (the file deletions of 2026-11-19), so it cannot show batch 2. No true pre-cleanup speed baseline exists (s8).
4. The commands that dominate real time were not re-timed: `collide_a` 1,007 s, `assembly_check` 2,283 s, drawings 227 s, SITL and the Blender films (s8, recorded values). They read A's model, not the moved root material, so no change is expected. The main checkout (4.5 GB working tree, 23 `__pycache__` folders, untracked GLB outputs) was not timed so as not to disturb running work; `git status` there is likely slower than in a fresh worktree.
5. File count did not fall (15,803 tracked now against 15,319), so no checkout or `git status` gain is claimed. The recovered space is disk space (s7). Cutting the redundancy listed above (98.8 MB of identical-blob copies, 90.3 MB of `mechanism/out` backups) would shrink the checkout, not gate run time.
