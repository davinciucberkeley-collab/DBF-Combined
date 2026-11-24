# DaVinci import of concept A (T-037, AM-047), 2026-11-23

Script: `python -I tools/davinci_import_a.py` (stdlib; token from git-ignored `.env`, never printed). Source: committed data only, `git show 73656c93:<path>`; the working tree (unfinished T-101 elevon change) was not read. No agent prompt sent. `main` not written.

## Where to look
DaVinci web app, project **API Test** (b53fed82-b072-43c2-9994-de76de845d93), branch switcher, branch **`concept-a-snapshot-73656c93`**. Under Model: package "Concept A (snapshot 73656c93, 2026-11-23)" with five child packages. Committed with message "Concept A snapshot import, Claude via API" (201, created).

## Counts (read back from the branch tree after the commit)
| Package | Objects in DaVinci | Source rows |
|---|---|---|
| Hard constraints | 6 requirements, each with 1 constraint child | 6 CLAUDE.md hard constraints |
| Parts | 6 parts (36 attributes) | 6 items from cad_mass.json (see note) |
| Bill of materials | 53 items (4 attributes each) + attribute "BOM total" | 53 BOM-A.csv lines |
| Requirements (REQUIREMENTS-A) | 45 requirements | 45 `A-` rows |
| Bench and flight tests | 11 tests | 11 rows of the TP table (TP-1 to TP-10b) |

Tree total 367 objects. All counts match.

## Values
- BOM total: **$1,939.17** (verified: committed `bom_a.py` totals() on the committed CSV; goods $1,382.41, tax $141.70, shipping+FAA $63.12, crash reserve $346.94, margin +$60.83). The plain sum of qty x unit cost is only $1,382.41, so the attribute documentation says how $1,939.17 is built.
- Units accepted without refusal: USD, g, mm, kg*m^2.

## Notes and refusals
- No refusals. Equation constraints were accepted: HC-1 `[BOM total id] <= 2000` and HC-3 `[Aircraft mass id] <= 25000` (g), so cross-object references work over REST. Whether DaVinci evaluates them to TRUE was not read back (the spot checks covered the objects, not satisfaction). HC-2, HC-4, HC-5, HC-6 (date, gates, CAD fidelity, wiring) are inspection constraints with the check text in documentation only; HC-3 trunk fit is documentation only.
- `cad_mass.json` has no per-part list. The "Parts" package holds its scalar items: aircraft (mass 1640.98 g, CG x/y/z mm), inertia (kg*m^2), elevon, motor station, fin, pack slot. Only the aircraft and elevon balance mass carry a mass; the others have positions only, as in the file. Per-part masses are in the CAD viewer data, not in this import.
- First run failed at the tests step on short table rows (script fix: pad rows). It also picked up later TP-n tables that reuse the same ids and overwrote TP-1 etc. Fixed to read only the first contiguous TP table, rerun overwrote them (rerun idempotence confirmed: same uuid5 ids give 201 and no duplicates), and 6 stale test objects were deleted before the final commit.
- Relationships (test verifies requirement) were not created: no REST route found (mapping s2).

## Pass check
- Counts equal source rows: yes (table above).
- Spot reads with Core/ReadObject in a session (closed): BOM total (1939.17 USD), Aircraft Mass (1640.98 g), P01 unit cost, A-U1 requirement, TP-1 test: all HTTP 200, isError false.
- Usage before and after: $49.060351, 1,093 events, asOf 2026-11-09T07:22:13Z, both reads identical (unchanged). Usage is recorded on an interval; re-read after a day.

## Part 2 (T-037, AM-048): 3D model file and CAD parts
Script: `python -I tools/davinci_import_a_3d.py` (stdlib; extends `davinci_import_a.py`; source `git show 73656c93:`; same branch only; no agent prompt; grant never printed). Record: `docs/integration/davinci-import-2026-11-23-3d.json`. Committed on the branch with "Concept A 3D model and CAD parts, Claude via API" (201). Read back from the tree after the commit.

### Created
| Item | Result |
|---|---|
| Package "3D model" (Model) | 1 package holding 1 reference object, the uploaded GLB |
| GLB upload | data-plane route (session, grant, `POST .../api/v1/file/upload/...`), HTTP 200, session closed. fileType .glb, fileSize 2,495,644 bytes (matches the committed file), sha256 stored by DaVinci. **Name caveat:** DaVinci named the object "concept-a.opt" (the requested objectName "concept-a.opt.glb (gated GLB, snapshot 73656c93)" was not applied; the file name concept-a.opt.glb is on the asset). Rename it in the web app if wanted (right-click, rename). |
| Package "CAD parts" | 10 subsystem sub-packages: wing 25, cage 23, propulsion 21, fins 16, mechanisms 14, avionics 12, landing 8, harness 8, power 3, assembly 1 |
| CAD parts | **131 parts** (viewer-data parts = 131; tree count = 131). Each has attributes Mass (g), CG x/y/z (mm, aircraft frame x aft, y right, z up) and Subsystem; documentation holds subsystem, part id, GLB node name, status, make or buy, material and the full viewer-data description. Name = "<part id> <short name>"; shortName = part id |
| GLB node names | the node name equals the part id for 129 parts; HRN-001 and HRD-001 are nodes "HRN-001 (mass proxy)" and "HRD-001 (mass proxy)". The GLB also holds JOINT and E- interface marker nodes with no part (not imported as parts). |

Tree total after commit: 1,166 objects. Usage before and after identical: $49.060351, 1,093 events (asOf 2026-11-09T07:22:13Z).

### Page "Concept A 3D model": NOT created over REST
Pages (HTML, Script, CSS, Bindings, Settings libraries) are not object types. The live probe on the branch (POST type `dashboard` with html, script, css, bindings, libraries, description, source, body, content, layout) returned 400: "not a field of type dashboard"; `dashboard` accepts only common fields. The API reference has no pages route. Nothing was faked and no dashboard object was created.

Click-steps for Dillon (from https://docs.davinci-app.com/pages/editor/pages.md), on branch `concept-a-snapshot-73656c93`:
1. Open the project, pick the branch, open the Pages widget (globe icon, left rail). Click **Add Page** (+). Click the name "New Page" at the top and rename it "Concept A 3D model".
2. Settings tab, Libraries: turn on **three.js**.
3. Bindings tab, Form view: drag the reference "concept-a.opt" (Model, package "3D model") onto the bindings list; it becomes an **Asset** binding. Set its key to `glb` (the script below uses that key).
4. HTML tab: `<h2>Concept A 3D model</h2><div id="model"></div><p id="cap">Exported model that passed the 0-clash GLB gate (D-247) at snapshot 73656c93. The elevon chord change T-101 is not included.</p><p id="pick">Click a part to see its node name.</p>`
5. Script tab:
```js
const box = document.getElementById('model');
const viewer = DavinciViewer.create(box, { height: '520px', spin: false });
viewer.onPick((hit) => { document.getElementById('pick').textContent = 'Picked: ' + (hit && (hit.name || hit.id)); });
async function render() {
  try { await viewer.load(await davinci.asset('glb'), { view: 'iso' }); }
  catch (e) { box.textContent = e.message; }
}
davinci.ready(render);
davinci.onUpdate(render);
```
6. Check the preview: drag to orbit, scroll to zoom, right-drag to pan; a click shows the picked node name (matches "GLB node name" in the CAD parts documentation). Commit (Source Control) on this branch.
Note: the viewer pick may return the mesh or node name rather than an object id for a GLB; the caption line shows whatever it returns.

### How to view
- File: Model tree, package "3D model", reference "concept-a.opt" (open it to see the .glb, 2.5 MB).
- CAD parts: Model tree, package "CAD parts", subsystem sub-package, part; select a part to see Mass and CG attributes and documentation.
- Page: after the click-steps above, Pages widget.
- Idempotent: rerunning re-posts the same uuid5 ids; a rerun uploads another copy of the file only if the upload step runs (the first run's upload was skipped, see record, because the owner id was first taken from the wrong field; the second run uploaded once).

**Page skipped (Dillon, 2026-11-23):** the team's DaVinci editor has no Libraries section in Page settings, so the DavinciViewer page (docs v5.4.1) could not be set up. The deployment may be older than the docs, or the setting is hidden. The GLB and the 131 CAD parts stay on the branch.

## Part 3: STEP test (T-037, AM-049), 2026-11-23
Result: **a STEP upload creates a real `geometry` object over REST.** Same branch only (`concept-a-snapshot-73656c93`), no agent prompt, token and grant never printed, nothing written to git by this test.

Steps and evidence:
1. **Hub mesh.** `git show 73656c93:redesign/site/assets/concept-a.glb` (11.8 MB, the un-optimised GLB the task named), Blender 4.5.14 background, node `CGE-001` (a single mesh node; no suffix), transforms applied, glTF Y-up converted to Z-up (x, -z, y), metres to mm. Raw 24,268 triangles with split vertices; after welding at 1e-7 m: 11,799 vertices, 23,662 triangles, 0 non-manifold edges (closed). Above the 20k limit, so Blender collapse decimate to **19,000 triangles (ratio 0.803 of the welded mesh)**, 9,468 vertices, still closed; bounding box unchanged. Mesh volume 16,013.4 mm3 (x 2.7 g/cm3 = 43.2 g; viewer-data mass 43.3 g, Al 6061-T6).
2. **STEP.** `tools/mesh_to_step.py` (pure Python): AP214 (`AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }`), PRODUCT "CGE-001 hub (6061-T6), concept A snapshot 73656c93", mm units, FACETED_BREP over a CLOSED_SHELL of ADVANCED_FACEs on PLANEs with POLY_LOOP bounds; falls back to SHELL_BASED_SURFACE_MODEL over an OPEN_SHELL if the mesh is not closed. First version (plain FACE, no surface) loaded in gmsh with no volume (empty bounding box), so planes were added. Final file 8,184,100 bytes, 161,489 entities. gmsh 4.15.2 load: 9,468 points, 28,500 curves, 19,000 surfaces, 1 volume. Bbox (mm) x -92.5000 to -33.0000, y -53.8789 to 53.8789, z -24.6723 to 24.6723; GLB node bbox (same frame) identical to 3e-5 mm, well inside the 0.1 mm limit.
3. **Upload.** `tools/davinci_step_test.py`: package "STEP test" (Model) then data-plane POST (same route as the GLB), HTTP 200, session closed. DaVinci created an object of **type `geometry`**, not a reference: id ec2f3d60-dfe4-4b1f-9217-e33e09d0b48f, name "CGE-001" (the requested name is not applied, as with the GLB; rename in the web app), `kind: "code"`, `data: const base = importShape(external("<own id>"));`, `metadata.importedShape` format "step", shapeCount 1, sha256 bd0bf2ed..., 57,017 face anchors, scaleWarning null.
4. **Resolved values read back** (GET /projects/{id}/objects/{id}?branch=..., SI units, metres): volume 1.60134e-5 m3 (16,013.4 mm3, matches the mesh), surface area 0.020439 m2, centroid / centre of mass (-72.362, 0.0008, -1.087) mm, bbox x -92.5 to -33.0 mm, y -53.879 to 53.879 mm, z -24.672 to 24.672 mm (dimensions 59.5 x 107.76 x 49.34 mm). DaVinci reports no mass (no material assigned); volume x 2.7 g/cm3 gives 43.2 g. Centroid x -72.4 mm against viewer-data CG -71 mm (viewer CG is a modelled value, not the mesh centroid). Step 4 (schema probe) was not needed.
5. **Commit.** "STEP test: CGE-001 hub", HTTP 201, hash 26dc82bda82c74d53db7c72be82f97694bcee343 (2 additions: package and geometry). Usage before and after identical: $49.060351, 1,093 events, asOf 2026-11-09T07:22:13Z.
6. Not needed: DaVinci did create the geometry, so no manual drag-in is required. The file is not stored in the repo (8.2 MB); regenerate with `python -I tools/mesh_to_step.py <mesh.json> <out.step> "<name>"` from the Blender export.

Where to look: Model tree, package "STEP test", geometry "CGE-001". Consequence for the mapping: per-part CAD (`geometry`) can be created over REST by uploading a STEP, so mapping row "CAD geometry" (file upload route not found) is now resolved: data-plane upload to the id of the new object. Upload of all 131 parts was not attempted (one part tested); the mesh-based STEP is a 19k-facet approximation, not the true parametric solid.
