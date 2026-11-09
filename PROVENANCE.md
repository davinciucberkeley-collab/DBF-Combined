# Provenance

DBF-Combined was assembled on 2026-11-08 as a **snapshot import**: each area below is a copy of the files at one
commit of a source repository, with fresh Git history. The source repositories stay on GitHub with their full history
(DBF-VTOL `.git` was 357 MB and DillonVTOL 243 MB, mostly old 29 MB copies of the generated review page), so use them
for `git log` / `git blame` on anything older than this repo.

Text and data files were copied byte for byte (`git archive` of the commit, no line-ending conversion). The only
edits made during the import are listed under [Edits made during the import](#edits-made-during-the-import).

## Sources

| Source repository | Commit (full SHA) | Commit date, author |
|---|---|---|
| [davinciucberkeley-collab/DillonVTOL](https://github.com/davinciucberkeley-collab/DillonVTOL) `main` | `cd21931662516fe07fee9faf010b61712e2d3372` | 2026-11-03, Dillon Alcouffe |
| [davinciucberkeley-collab/DBF-VTOL](https://github.com/davinciucberkeley-collab/DBF-VTOL) `main` | `9cc31fe911dcad87f8b70c105177b248588870b1` | 2026-11-04, Tristan Hottier |
| [davinciucberkeley-collab/DBF-VTOL](https://github.com/davinciucberkeley-collab/DBF-VTOL/tree/design2) `design2` | `aef000769e8086dc34b3d2aa64ff460c8339b78a` | 2026-10-19, Vaibhav Bagrodia |
| [davinciucberkeley-collab/TiltWing](https://github.com/davinciucberkeley-collab/TiltWing) `main` | `1488f8f61dc3f10f0d650e13e900560f0a7a9cec` | 2026-10-19 |
| [davinciucberkeley-collab/OpenCAEModel](https://github.com/davinciucberkeley-collab/OpenCAEModel) `main` | `792f0abd60a92ed9027f8fe5f14727926774468a` | 2026-11-02 |

DBF-VTOL and DillonVTOL are one history that forked after the shared commit `3d45b69` (2026-10-26). After the fork,
DBF-VTOL changed no shared engineering file (only `README.md`, `CLAUDE.md`, `PRODUCT.md`, two new root pages, four new
`docs/research/` notes and its own `inventory/ fusion/ concepts/ sim/` trees), while DillonVTOL re-sized the design
(2026-11-02). So for every path that exists in both, the DillonVTOL file is the newer one and is the one used here.

## Where each area came from

| Path in DBF-Combined | Source | Notes |
|---|---|---|
| `analysis/`, `cad/`, `docs/` (except the four files below), `firmware/`, `review/`, `tools/vtol.py`, `VTOL.bat` | DillonVTOL `cd21931` | 11-02 resize, CAD rev G, 3-D CFD, validation matrix |
| `VTOL-Review.html`, `build-manual.html`, `test-plan.html`, `flight-software.html`, `templates.html`, `index.html`, `.nojekyll` | DillonVTOL `cd21931` | generated pages (issue 6) and the GitHub Pages entry point |
| `.github/workflows/regenerate-check.yml`, `.impeccable/`, `DESIGN.md` | DillonVTOL `cd21931` | identical in both repos except the CI edit noted below |
| `CLAUDE.md`, `PRODUCT.md` | DBF-VTOL `9cc31fe` | only DBF-VTOL edited them after the fork (team list, sibling pages); repo name updated |
| `README.md` | hand-merged | DillonVTOL's design table and layout + DBF-VTOL's inventory, Fusion, concepts and artifact sections, numbers checked against the files in this repo |
| `inventory/`, `fusion/`, `concepts/`, `sim/` | DBF-VTOL `9cc31fe` | built on design v0.3.1, see [DECISIONS.md](DECISIONS.md) |
| `Inventory-Overview.html`, `Concept-Models.html` | DBF-VTOL `9cc31fe` | generated pages (v0.3.1 inventory; concept models placed on the rev D C0) |
| `docs/research/electrical-architecture.md`, `hardware-schedule.md`, `nautical-wings-props.md`, `tolerance-analysis.md` | DBF-VTOL `9cc31fe` | v0.3.1 numbers |
| `explorations/tiltwing/` | TiltWing `1488f8f` | = DBF-VTOL `design2:tiltwing/` at `aef0007` (57 of 59 files byte-identical; TiltWing adds an origin note to the README and the paper PDF). Archived exploration |
| `tools/opencae-studio/` | OpenCAEModel `792f0ab` | OpenCAE Studio 0.2 source. Licensed **GPL-3.0** (`tools/opencae-studio/LICENSE`); the rest of this repo carries no licence file |
| `DECISIONS.md`, `PROVENANCE.md`, `.gitattributes`, root `.gitignore` additions | new | written for DBF-Combined |

## Left out, and why

| Left out | Why |
|---|---|
| `review/vtol-review.html`, `review/build-manual.html`, `review/test-plan.html`, `review/flight-software.html`, `review/templates.html` (DillonVTOL) | Second copies of the root pages (about 37 MB). `review/build.mjs` writes both; the root copies are the ones GitHub Pages, `index.html` and the README use. The builder still writes the `review/` copies locally (for publishing as a claude.ai artifact); they are now git-ignored and the CI no longer diffs them |
| `inventory/inventory-overview.html` (DBF-VTOL) | Fragment copy of `Inventory-Overview.html` (5.6 MB), written by `inventory/build_overview.mjs` for artifact publishing; now git-ignored |
| `concepts/variants/a2/fusion/build_a2_fusion.py`, `concepts/variants/a3/fusion/build_a3_fusion.py` (DBF-VTOL) | Byte-identical to `fusion/variants/build_a2_fusion.py` and `build_a3_fusion.py`. The `fusion/variants/` set is kept because it also holds `build_a1_fusion.py`; nothing referenced either path |
| `analysis/cfd3d/out_rev1/scheme_check_2d.json` (DillonVTOL) | Byte-identical to `analysis/cfd3d/out_rev1/scheme_check_2d_rev1.json`, which is the name `analysis/cfd3d/verify_cfd.py` cites |
| Orchestration and build logs nothing cites: `analysis/cfd3d/out/{geometry_rev2,mesh_L1,mesh_L2,mesh_L3,mesh_L4,mesh_audit,resume_L4,run_batch,run_batch_rev2,scheme_check_2d}.log`, `analysis/validation/xtool_boom_fea.log`, `cad/build_2026-11-01.log`, `cad/build_2026-11-03b.log` (DillonVTOL) | Solver/build console output, regenerated on every run |
| DBF-VTOL versions of the 438 shared files that differ, its README "Current design" table, `firmware/vtol_c0.param` rev D, etc. | Superseded by the DillonVTOL versions (rev D 10-25 vs the 11-02 resize). Still in DBF-VTOL history at `9cc31fe` |
| `TiltWing/docs/Cakir-Kurtulus-2022-tilt-wing.pdf` | Third-party journal paper; redistribution licence not checked. Cite it instead: Çakır, Kurtuluş, "Design and aerodynamic analysis of a VTOL tilt-wing UAV", *Turk J Elec Eng & Comp Sci* 30 (2022) 767–784, [doi:10.3906/elk-2105-59](https://doi.org/10.3906/elk-2105-59). The copy remains in the TiltWing repo |
| DBF-VTOL branch `design2` as a separate branch, and the TiltWing repo as a separate copy | Same content as `explorations/tiltwing/` |
| `tools/opencae-studio/opencae/tests/data/pe/{fakeccx.exe,libdep-1.dll,libfwd.dll,libmid.dll}` (OpenCAEModel) | Compiled PE test fixtures for `opencae/tests/test_launcher.py`; executables are not imported (and `*.exe`/`*.dll` are git-ignored). That test cannot run in this copy |
| `tools/opencae-studio/opencae/examples/projects/*_data/results/run_*` (OpenCAEModel) | Solver runs (job.inp, results.npz). Re-solve in the app or run `opencae/examples/build_examples.py`; the example `.ocae` files still name the old run folders |

Kept on purpose although generated: `analysis/cfd3d/out/` (the review build reads `viz/cfd3d_viz.json` and
`mesh_audit.json`, and the validation matrix cites the per-case `history.csv`, `su2.log` and `post/*.json` files as
evidence), `analysis/cfd3d/out_rev1/` (cited by `verify_cfd.py`), `cad/build_2026-11-03.log` (cited as CAD build
evidence in `analysis/validation/validation_matrix.json`), the SITL `console.log` files, and all CI-checked outputs.

Intentional byte-identical pairs that remain: `cad/params.built.txt` = `cad/params.txt` (the as-built record that
`analysis/validation/check_struct.py` compares; identical until the next CAD build), `docs/build/img/fig12_cg_weigh.svg` =
`docs/test/figures/cg_weigh.svg` (both written by `docs/figures/annotate.py` for the two documents),
`firmware/sitl/results_c0.json` = `firmware/sitl/results_c0/summary.json` (both written by `mission_test.py`), four
`inventory/v031/cad/mesh/*.STL` equal to `cad/mesh/*.STL` (the frozen v0.3.1 snapshot), the six identical SU2 `case.cfg`
per angle in `analysis/cfd3d/out/scheme2d/`, three tilt-wing STLs that do not move between the 0° and 90° poses, the two
`analysis/cfd3d/out*/.gitignore` files, and empty `__init__.py`/`.nojekyll` files.

## Edits made during the import

| File | Edit |
|---|---|
| `.github/workflows/regenerate-check.yml` | Dropped the five `review/*.html` paths from the "committed outputs match" diff (those copies are no longer committed) |
| `tools/vtol.py` | `status` lists `VTOL-Review.html` instead of `review/vtol-review.html` |
| `inventory/build_variants.mjs` | "Full design note" link points at DBF-Combined instead of DBF-VTOL (takes effect on the next page build) |
| `CLAUDE.md`, `PRODUCT.md` | Repository name, a "Where things are" section and the no-secrets rule |
| `explorations/tiltwing/README.md` | "Archived exploration" banner; the PDF note replaced by the DOI |
| `tools/opencae-studio/README.md` | Snapshot banner listing what was not imported |
| `.gitignore` | DillonVTOL rules plus secrets, the generated fragment copies, logs, caches and OpenCAE runs |
| `.gitattributes` | New: Git LFS rules |

## People

From the commit logs: Dillon Alcouffe (design, CAD, analysis: DillonVTOL and most of the shared history), Tristan
Hottier (inventory, electrical, Fusion model, alternative designs A1–A3), James Guymon (concept models), Vaibhav
Bagrodia (tilt-wing study). The `sim/` import and OpenCAE Studio were committed mostly by Claude sessions on the team
account. Commit attribution rules are in [CLAUDE.md](CLAUDE.md).
