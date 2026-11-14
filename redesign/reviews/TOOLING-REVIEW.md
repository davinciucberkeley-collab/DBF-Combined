# Tooling review (independent, fresh eyes) — 2026-11-09

Scope: `redesign/fusion/`, `interfaces/`, `blender/`, `manual-kit/`, `viewer/`, `proofs/`. Judged against BRIEF.md
(digestible, easy to check, easy to build) and ADVISOR-XV24-LESSONS.md (status words, joint stacks, wiring as
installation, viewer modes, no verification bureaucracy). Clear bugs were fixed in place; judgement calls are listed,
not changed. Nothing committed.

## 1. Every documented check, run on this machine

| Tool | Command (repo root) | Result | Time |
|---|---|---|---|
| fusion | `python -I redesign/fusion/check.py --examples --strict` | PASS, 3 modules, 0 err, 0 warn | 0.3 s |
| fusion | `python -I redesign/fusion/check.py` (real subsystems, none yet) | FAIL "no modules found" (correct: not a vacuous pass) | 0.3 s |
| fusion | `python -I redesign/fusion/tests/test_framework.py` | 13 tests OK | 0.4 s |
| fusion | `python -I redesign/fusion/build_all.py --examples` | ok, 1470 g, CG 0.202 m | 0.3 s |
| interfaces | `python -I redesign/interfaces/merge_check.py` | PASS, now with 1 WARN `no-sources` (was a silent vacuous PASS, fixed) | 0.3 s |
| blender | `blender -b --factory-startup -P redesign/blender/selftest.py -- --examples` | all ok (12 parts, bbox ≤ 0.01 mm, volume ≤ 0.3 %, manifold, GLB round trip) | ~1 s |
| blender | `... export_glb.py -- --examples` | 12 parts, 4 wires; output byte-identical to the committed GLBs | ~1 s |
| blender | `... render_figures.py -- --examples --only step_1 --samples 16 --percent 50` | rendered (into the scratchpad); checked by eye: x-ray fuselage, orange focus parts and wire, floor shadow | 5.7 s |
| manual-kit | `python -I redesign/manual-kit/test_manual_kit.py` | 8 tests OK | 0.7 s |
| manual-kit | `build_manual.py --examples --check` / `--examples --no-render` / real | OK 0 err 0 warn / OK, 6 cards, 12 images / "nothing to build" exit 0 | 0.3–0.6 s |
| proofs | `python -I redesign/proofs/test_proofs.py` | 5 tests OK | 0.5 s |
| proofs | `build_graph.py --examples` / real | OK, 69 nodes, 2 fails as designed / OK, 0 nodes | 0.3 s |
| viewer | `build_data.py --examples` / real | 12 parts, 7 claims, **0 warnings** (was 9, fixed) / empty state with 2 WARN | 0.3 s |
| viewer | `node redesign/viewer/check_viewer.js` | OK 161 checks | 0.3 s |
| proofs viewer | `node redesign/proofs/viewer/check_viewer.js` | OK | 0.2 s |

Every stdlib check is well under a second; the Blender ones are seconds. Blender 4.2.3 was found where
`blender/README.md` says (`~/tools/blender/blender-4.2.3-windows-x64/`) and by `manual-kit/figures.find_blender()`.

## 2. Bugs fixed (files edited)

| # | File | Problem | Fix |
|---|---|---|---|
| F1 | `fusion/backends/fusion_backend.py` | `sk.isVisible = False` on sketches. Autodesk docs: `isVisible` is the computed state, `isLightBulbOn` is the settable one; the old working scripts (`fusion/build_vtol_fusion.py:271`) use `isLightBulbOn`. Likely a silent no-op or an exception in real Fusion | `isLightBulbOn = False` in `body()` and `_point_geometry()` |
| F2 | `fusion/backends/fusion_backend.py` | A Fusion joint aligns **both joint frames** (origin and axes), not only the origins. The joint-point sketches are Z-normal planes of each component, so a part placed with `ctx.part(rotate=)` has a frame that differs from its partner's and Fusion will turn it to match. Silent geometry change; the old scripts never hit it because they placed parts by translation only | `joint()` records a WARN (`joins rotated component ... check its placement`) that `end()` adds to `ctx.issues`, so it appears in the Fusion summary; documented in the module docstring and README. Real fix (JointInput.angle or a world-aligned joint plane) is UNVERIFIED-IN-FUSION, so not attempted blind. The unused `log_lines` was replaced by this `warnings` list |
| F3 | `interfaces/merge_check.py` | With no `<subsystem>/interfaces.json` the graph check printed `PASS (0 errors, 0 warnings)` and wrote an empty merged graph: a vacuous pass a student could mistake for a clean integration | WARN `no-sources` ("nothing was checked"); `--strict` fails. `check.py` already failed on no modules |
| F4 | `proofs/examples/*`, `proofs/viewer/check_viewer.js`, `viewer/build_data.py` | The proof-chain demo named parts `EX-FUS-001`, `EX-PWR-001..004`, `EX-HRN-00x`; the generic test aircraft is `FUS-001`, `BMS-003`... The viewer stripped `EX-` and still printed 9 "not a part of this aircraft" warnings in its own demo (viewer CHANGE-REQUEST #1) | Demo claims now name the generic aircraft's parts (`FUS-001`, `FUS-002`, `FUS-003`, `WNG-001..004`, `BMS-003/004`); `proofs/examples/interfaces.json` lists them; claims.json, graph and viewer data regenerated; alias set to `None`; CR #1 marked done. One inventory, one set of ids |
| F5 | `proofs/build_graph.py`, `viewer/build_data.py` | Every run rewrote `generated: <time>` into 8 committed files, so running the checks dirtied `git status` and the orchestrator would commit timestamp noise each phase | The stamp is kept when nothing but the stamp differs ("when the data last changed"). Verified: re-running both generators twice leaves `git diff` empty |
| F6 | `blender/selftest.py` | With an empty module root it crashed with `StopIteration` from `next(iter(ctx.components))` instead of saying what was wrong | Prints `FAIL no parts were built (...)` and exits 1 (verified on an empty folder) |
| F7 | `manual-kit/md_out.py`, `html_out.py`, `steps_lib.py` | "Flying mass" summary and the `type: mass` check target summed `flight: false` ground tools/fixtures, against ADVISOR lesson 4 | Both exclude `flight: false` parts |

All tests re-run after the edits: fusion 13/13, manual-kit 8/8, proofs 5/5, viewer 161 checks, proofs viewer OK,
check.py --examples --strict PASS.

## 3. Fusion backend: what is likely to work, what is not (cannot be run here)

Compared with the old scripts in `fusion/` and the Autodesk API reference
([Occurrence.isGroundToParent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrence_isGroundToParent.htm),
[Sketch.isLightBulbOn](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketch_isLightBulbOn.htm),
[JointGeometry.createByPoint](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_JointGeometry_createByPoint.htm),
[ConstructionPointInput.setByPoint](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ConstructionPointInput_setByPoint.htm)).

| Item | Verdict | Why |
|---|---|---|
| Offset construction planes with the normal-sign fix, closed polylines, profile pick, extrude/revolve/loft, `Matrix3D.setWithArray`, copied appearances | **proven pattern** | copied line for line from `build_vtol_fusion.py`, which built the previous aircraft |
| Joint points as **sketch points** (`createByPoint` + `createForAssemblyContext`) | sound | docs: `createByPoint` takes ConstructionPoint, SketchPoint or BRepVertex. Better than the old script's `ConstructionPointInput.setByPoint(Point3D)`, which the docs say is "only valid in direct edit modeling mode" (the new backend sets `ParametricDesignType`) |
| `isGroundToParent` un-grounding before a revolute/slider joint | sound | property exists since May 2024, wrapped in `try` for older Fusion |
| Rotation limits widened by 0.1° | proven | from `build_joints_fusion.py:409` |
| Joint frame alignment with rotated components | **risk, now warned** (F2) | see above |
| Wires as 3-D sketch lines (points off the sketch plane) | UNVERIFIED | docs for `addByTwoPoints` only say "SketchPoint or Point3D". If it fails, `Context.finish()` catches it per wire as an ERROR issue; the parts and joints still build |
| Revolve axis: a construction line from `(0,0)` to `(0.01,0)` on the axis | UNVERIFIED | for a profile that touches the axis (the example motor) this line overlaps the profile's closing edge. Construction lines do not split profiles, so it should work; if Fusion rejects it, use the on-axis profile line itself as the axis |
| Material library names (`Fusion Material Library` / `Fusion 360 Material Library`, `Aluminum 6061`, `PLA`...) | UNVERIFIED | both library names tried; a miss keeps the default material and the declared mass stays authoritative (documented) |
| `fc.description`, `fc.attributes.add`, `physicalProperties.mass`, `bRepBodies.item(0).material.name` | sound | standard API, all inside `try` where they are only informative |
| `BuildAll/` launcher (adds `redesign/fusion` to `sys.path`, drops cached modules, message box ≤ 3000 chars) | sound | no path to edit; finds the repo from its own location |

Performance: everything is parametric (timeline). ~12 features for the example; a 200-part aircraft with lofts will
take minutes, not seconds, in Fusion. `DirectDesignType` would be faster but loses the timeline. Judgement call.

## 4. Mismatches between stub and real backends

| Check | Stub (`check.py`) | Fusion / Blender |
|---|---|---|
| Geometry validity | only counts and empty loops; cannot see self-intersecting profiles or failed lofts | Blender `selftest.py` now proves the mesh matches fusionkit (bbox, volume, manifold) — a real second opinion on the geometry, not on Fusion's kernel |
| Touch | bounding boxes within 2 mm. **Revolve bbox uses `rmax` for every profile point**, so a motor's thin shaft "touches" anything its full-radius box reaches. Lenient, never strict; documented as coarse | none |
| Joints | registered, origins on both parts | Fusion joints also fix orientation (F2) |
| Mass | declared `mass_g` | Fusion prints geometry × library density for comparison; Blender carries `mass_g` as an extra |
| Wires | ≥ 2 points, ends on parts | Blender rounds corners to the declared bend radius (good: wiring as installation); Fusion draws a polyline |

The `_Any` fake-`adsk` test proves the backend's Python runs end to end (names, arithmetic, control flow); it proves
nothing about API behaviour. The README says so. Good.

## 5. Vacuous or weak checks found

| Where | Finding | State |
|---|---|---|
| `merge_check.py` on an empty subsystems folder | PASS with nothing checked | fixed (F3) |
| `viewer/build_data.py` | exit 0 whenever the output can be written, even with no interfaces and no model | documented and reasonable: the viewer shows the empty state and lists the warnings |
| `check.py` register check | edges whose parts are not both modelled are skipped (WARN only if registered) | correct while subsystems are PROPOSED; listed in the README table |
| `manual-kit` | `visual` checks only warn; `time_min` missing only warns | right level: the manual still builds, the open items list shows it |
| `proofs` statuses | an author can only downgrade a status, never type `CHECKED`/`VERIFIED` | exactly the advisor's status ladder; `VERIFIED` needs a run test |

## 6. Hard-coded paths, fragility

| Where | What | Verdict |
|---|---|---|
| `manual-kit/figures.find_blender()` | `~/tools/blender/blender-4.*`, `C:/Program Files/Blender Foundation/...`, `/Applications/...`, `/usr/bin/blender` | fine: home-relative globs after `--blender`, `DBF_BLENDER` and PATH, with a clear message when none is found |
| `blender/annotate.browser()` | Edge/Chrome under Program Files | fine: optional rasterising, `shutil.which` first, SVG still produced |
| `blender/README.md` | names the team laptop's Blender folder | fine as a hint |
| every script | repo located from `__file__` | no user directories anywhere |
| generated files | written with LF; this clone has autocrlf, so after a `git checkout` of a generated file `git status` shows M with an empty diff | not a tooling bug; integrator may add `.gitattributes` (`*.json *.js *.md text eol=lf`) |

## 7. Over-engineering vs the advisor's warning

Nothing here is a sealed receipt or a kernel proof. Items I weighed:

- `viewer-data.json` stores the GLB's SHA-256 and `check_viewer.js` verifies it: 1 line, catches a stale base64 copy. Keep.
- `manual-kit/figures.lock.json` hashes spec + inputs so only changed figures re-render (15 s each). Keep; it is the
  reason `build_manual.py --examples` takes 0.5 s. Note: the hash includes `design-system/blender-style.json`, which
  `render_kit.py` never reads (it hard-codes its own look). Harmless extra re-renders; see §8.
- `html_out.py` (689 lines: hover cards, localStorage progress, print CSS, glossary) is big but every feature is for
  the builder at the bench, not for certification. Keep.
- `proofs/build_graph.py` recomputes every calculation by importing the analysis script: that is the one check that
  makes "every number traces to a calculation" true, and it runs in 0.3 s. Keep.
- `blender/render_kit._visible_point()` casts a 28 × 28 ray grid per callout to place a dot on a visible surface.
  It is what makes the hidden-fastener "(behind other parts)" marker honest. Keep.

## 8. Judgement calls not changed (owners decide)

| # | For | Observation |
|---|---|---|
| J1 | Design system + Blender | `render_kit.py` uses `Standard` view transform, 48 samples and its own light rig; `design-system/blender-style.json` says AgX, 128 samples, named lights. The README argues Standard keeps token colours true. Pick one and make `render_kit` read `blender-style.json` (or drop it from the manual-kit fingerprint) |
| J2 | Fusion keeper | F2: decide the real fix for joints on rotated parts once a teammate has run `BuildAll` once. Until then do not use `rotate=` on parts that carry joints, or expect to check them |
| J3 | Fusion keeper | `ParametricDesignType` vs direct modelling for build speed (§3) |
| J4 | Fusion keeper | `Shape.points()` for revolves inflates the bbox to `rmax` (§4). A per-point radius would make the touch check tighter; cost ~5 lines |
| J5 | Proofs | the demo's `n_lift = 4` (params) now sits next to two modelled motors (`BMS-003/004`); the numbers are illustrative and say so. Fine for a demo; the real aircraft will have one set of parts |
| J6 | Viewer / interfaces | `structural` inference (viewer CR #2) and "which side of a hinge moves" (CR #3) are real schema gaps; both are already filed |
| J7 | Manual kit | fasteners and tools are summed by exact text (README "known limits"); CR #3 to the keeper covers it |
| J8 | Blender | `Stage.camera()` with nothing visible (a step whose parts are all hidden) raises `ValueError: min() of empty` without a message naming the step; worth a one-line check when the first real steps arrive |
| J9 | All | the generated outputs (`interfaces/REPORT.md`, `proofs/out`, `viewer/data`, `blender/out`) are committed. Fine for GitHub Pages; with F5 they no longer churn on every run |

## 9. Against the advisor's lessons

| Lesson | Where it lives | Status |
|---|---|---|
| Status words PROPOSED/MODELLED/CHECKED/VERIFIED | `interfaces/SCHEMA.md`, `check.py` (missing MODELLED parts are errors, PROPOSED ones listed), `proofs` (computed, never typed), viewer colour-by-status | consistent; `proofs` adds `UNVERIFIED` with reasons, as BRIEF asks |
| Joint-stack table per fastened edge | `SCHEMA.md` 13 fields, `merge_check` fails on a missing field or engagement < minimum, manual kit sums fasteners and tools from it, viewer shows it per part | done, one source |
| Wiring as installation | `wire` block (gauge, connector, supports, bend radius, strain relief, disconnect) required on electrical edges; `ctx.wire()` must exist; Blender draws the bend radius; manual wiring table | done |
| One inventory drives everything | `interfaces.json` + modules → check.py → Blender GLB → viewer → manual → proofs link by part id | done; F4 closed the one id mismatch |
| Viewer modes (whole / inside & wiring / structure / exploded, click a part) | `viewer/model.js` rules, tested in Node | done |
| Proportionate verification | every check < 1 s stdlib; Blender seconds | done |
| Missing parts shown, never dropped | `check.py` `missing`, manual "parts index" lists un-fitted parts, viewer lists parts with no geometry | done |

## 10. Files changed by this review

`fusion/backends/fusion_backend.py`, `fusion/README.md`, `interfaces/merge_check.py` (+ regenerated
`interfaces/REPORT.md`), `blender/selftest.py`, `manual-kit/{md_out,html_out,steps_lib}.py`,
`proofs/build_graph.py`, `proofs/examples/{interfaces.json,power/analysis.py,wing/analysis.py}` (+ regenerated
`claims.json`, `examples/out/*`), `proofs/viewer/check_viewer.js`, `viewer/build_data.py`, `viewer/README.md`,
`viewer/CHANGE-REQUESTS.md` (+ regenerated `viewer/data/examples/*`).
