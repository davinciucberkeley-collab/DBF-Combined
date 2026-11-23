# T-038 Explorer refresh, 2026-11-23

Category: illustrative / site generation (no engineering analysis). Acceptance test (brief): after regenerating only stale outputs, the
Explorer served from redesign/site shows mass 1.881 kg, BOM $1,939.17, 12 STRICT proof FAILs, 129 parts, FC 75 mm left of centre, and no
unlabelled MN2212 / K09-L as current. **Result: PARTLY MET** (3-D model data could not be regenerated; hand-authored text still stale, listed below).

## Staleness found (before)
app.html / index.html 2026-11-19; site/data/viewer-data.json and assets/concept-a*.glb 2026-11-18 (115 parts, 65 claims, budget gate 1,500 g,
Kakute F405 name); site graph.js 2026-11-18; against BOM-A.csv 11-22, ORDER-1.csv 11-23, BUILD-GUIDE-A.md 11-23, graph.js 11-23 10:51,
drawings/out PNG 11-23 (58 sheets; site showed 50).

## Generators run (from repo root, `python -I redesign/site/<x>.py`)
| Generator | Exit | Time | Result |
|---|---|---|---|
| make_proof_embed.py | 0 | <1 s | graph.js copied (site copy now byte-identical to qp/A/proofs/out/graph.js), readable.js updated; app.html markup unchanged |
| sync_bom_a.py (1st run) | 1 | <1 s | StopIteration: ORDER-1.csv (rebuilt D-238) has no row "ORDER 1 TOTAL, 2..." |
| make_build_guide.py | 0 | <1 s | 16 sections, 165,009 bytes HTML |
| make_drawing_gallery.py | 0 | 17 s | 58 sheets (was 50); 96 webp/thumb files re-encoded |
| sync_status_a.py | 0 | <1 s | ran, but its lists are hand-authored (see residual); output unchanged in substance |
| make_index.py | 0 | 1 s | index.html rebuilt |
| sync_bom_a.py (fixed, 2nd run) | 0 | <1 s | 53 lines, total $1,939.17, margin $60.83, +30 % margin -$29.68, Order 1 $887.25 |
| make_index.py (again) | 0 | 1 s | 512,826 bytes |

Generator fix (only code change): redesign/site/sync_bom_a.py now matches the row "ORDER 1 TOTAL" (the CSV has one total after D-238), drops the
"5 motors" Order-1 variant sentence (no longer in ORDER-1.csv) and labels the tile "4 X2216 motors (ORDER-1.csv, D-238)". No numbers typed in;
layout and styles untouched. Not run: sync_bom_tab.py (reads team/I1/BOM.csv, the K09-L record, not concept A).
**NOT run: viewer_data_a.py.** It needs a fresh assembly.glb from the Blender pipeline (a_assembly_blender.py); Blender is not installed on this machine
(no blender on PATH, none under Program Files) and the newest GLB in redesign/blender/out/aircraft/glb is 2026-11-18, before D-226..D-240. Node/npx is present.

## Files changed (git status, nothing committed or pushed)
M redesign/site/app.html, M redesign/site/index.html, M redesign/site/proofs/data/graph.js, M redesign/site/proofs/data/readable.js,
M redesign/site/sync_bom_a.py, 96 x M redesign/site/assets/drawings/*.webp and thumb/*.jpg (re-encoded, 58 sheets), plus this file.

## Number checks (served with `python -m http.server 8766 --bind 127.0.0.1` from redesign/site, fetched with curl, all HTTP 200)
Port 8765 was already held by about ten stray `http.server 8765` processes from earlier sessions (one serving an unrelated "Advanced Controls" page,
index.html returned 404), so the check used 8766. I stopped only the 8765/8766 servers I started.
| Item | Expected | Found | Result |
|---|---|---|---|
| BOM total (index.html) | $1,939.17 | $1,939.17 (2 hits), margin $60.83, Order 1 $887.25 | PASS |
| STRICT proof FAILs (proofs/data/graph.js) | 12 | 12 distinct claims FAIL (15 error lines, A-P and CL- ids duplicate) plus 1 UNVERIFIED (A-P13 flutter); mass 1.881 kg vs 1.47 kg | PASS |
| Predicted mass 1.881 kg on the page | 1.881 | 0 hits in index.html text; only in the proof graph. Status tab still says "predicted 1,455.6 g" | FAIL (hand-authored status text) |
| Part count 129 | 129 | viewer-data.json has 115 parts, 65 claims, generated 2026-11-18; build guide / ASSEMBLY.md state 129 | FAIL (3-D data stale) |
| CAD 1,641 g | 1,641 | 0 hits | FAIL (3-D data / status text) |
| FC position 75 mm left of centre | 75 mm | build guide text carries it (10 hits "75 mm"); viewer-data.json still names AVN-002 "Kakute F405 Wing Mini" and predates D-240 | PARTIAL |
| TP-15..TP-18, D-240 on page | present | 0 hits for TP-15 and D-24x in index.html | FAIL (status/decision tabs hand-authored) |
| MN2212 as current | none | 7 hits, all unlabelled (below) | FAIL |

## Residual stale text (not edited: hand-authored, outside the generators' inputs, or needs the Blender step)
MN2212 (unlabelled, current-tense), by page section of app.html:
- aircraft (4): spec line "APC 9x4.5MR on T-Motor MN2212"; the a-detail-propulsion render caption and alt text "Propulsion station: MN2212 on a canted cup" (the render image itself is the old CAD: needs a Blender re-render).
- decision (1): table row "Propulsion 4 x T-Motor MN2212 KV780, APC 9x4.5MR/MRP ... Tattu 4S 2300" (D-183, D-184, D-189 era).
- subsystems (1): "Four T-Motor MN2212 V2.0 KV780 motors on 4S" card.
- status (1): "T-Motor stock and lead time for the MN2212 ... buy all 5 motors in Order 1".
K09-L: 71 mentions across the page; most carry "previous design / record" wording, not individually audited; the Status tab key lines (mass "4 g of room, predicted 1,455.6 g against 1.46 kg", "1,499" cost, bench kit, ZOHD Altus lifeboat, withdrawn by AM-008) and the decision tab (1.46 kg target, $1,499 in 2 places) are current-tense and stale against D-217..D-241.
Also stale: sync_status_a.py PHASES/ISSUES/decision lists (hand-edited source, last meaningful content 2026-11-18); site/data/viewer-data.* and
assets/concept-a*.glb (3-D viewer: 115 parts, FC at old position); a-detail renders and film assets.

## Needed to finish
1. Run the Blender assembly export (a_assembly_blender.py) on a machine with Blender, then merge_check.py and viewer_data_a.py (needs npx), then make_index.py.
2. Update the lists in sync_status_a.py and the aircraft / decision / subsystems hand-written sections for X2216, 1.881 kg, $1,939.17, D-233..D-241 (the user's team decision on wording).
3. Re-render the a-detail-propulsion and other renders after step 1.


---
## Update after coordinator message (same day, second pass)

Result of the second pass: **MET for the checked numbers** (see table); K09-L mentions not individually audited.

### 3-D data regenerated (Blender 4.5.14, not the 4.2.3 folder)
| Step | Command | Exit | Time | Result |
|---|---|---|---|---|
| GLB export | `blender.exe -b --factory-startup -P redesign/blender/export_glb.py -- --root redesign/qp/A/cad/model --out <scratchpad>/glb` | 0 | 154 s | 131 parts, 14 wires |
| Interfaces merge | `python -I redesign/interfaces/merge_check.py --root redesign/qp/A/cad/model --out <scratchpad>/mi` | 1 | <1 s | wrote interfaces.json; reports 1 ERROR (CG x 0.022 m outside the old 0.043..0.050 m band) and 1 WARN (avionics 74 g > 36 g allocation): stale allocation table, not a model change; flagged, not fixed |
| Viewer data | `python -I redesign/qp/A/cad/viewer_data_a.py --glb <scratchpad>/glb --interfaces <scratchpad>/mi/interfaces.json --out redesign/site/data` | 0 | 32 s | 131 parts (129 placed + harness and hardware lumps HRN-001, HRD-001), 196 edges, 82 claims; concept-a.glb 11.74 MB -> opt 2.48 MB via npx gltf-transform 4.5.1 |
Scratch inputs are in the session scratchpad, outside the repo.

### Text updated (generator source sync_status_a.py and hand-written app.html, every value with its source on the row)
Status tab: new phase "O4b re-sit and X2216 redesign" (D-217..D-241); mass issue now "Mass gate missed, predicted 1,881 g EST (params-A.json, 1,641.0 x 1.1174 + 48)"; new FAIL issue "12 claims FAIL in the strict proof build" (graph.js); exposed wire 0.597 m (D-240); TP-15..TP-18 test row; decision rows for X2216 stock (D-228) and Order 1 $887.25 (D-238, servo qty 2 D-234); summary and claims line "12 FAIL". Decision tab: five current-design rows (mass 1.881 kg, X2216 propulsion, FC 75 mm left, BOM $1,939.17, 12 FAIL / TP-15..18), old rows labelled. Aircraft tab: intro mass, cost, MN2212 captions and GA callout labelled. Subsystems tab: propulsion card now X2216 (MN2212 labelled), pack card, 1260 g basis and legend labelled "earlier design (record)". Layout and styles untouched.

### Re-check (curl, served `python -m http.server 8766 --bind 127.0.0.1`, all 200)
| Item | Found | Result |
|---|---|---|
| BOM $1,939.17 | 4 hits in index.html | PASS |
| Predicted 1.881 kg | 4 hits | PASS |
| CAD 1,641.0 g | 3 hits; params-A.json basic 1.64098 kg | PASS |
| 12 STRICT FAILs | 12 distinct FAIL claims in graph.js (15 error lines), text on Status / Decision tabs | PASS |
| Part count | viewer-data.json 131 entries = 129 placed + 2 lumps; "129" in build guide text | PASS (129 placed) |
| FC position | AVN-002 Kakute H743-Wing cg_xyz_m [0.0472, -0.075, 0.0178] in viewer-data.json; "75 mm left of centre" in text | PASS |
| TP-15..TP-18, D-240 | 4 and 3 hits | PASS |
| MN2212 / 1,455 / 1,499 unlabelled as current | scan found none without "earlier design (record)" within 260 characters | PASS |

### Residual
- The 7 MN2212 hits, the "1,455.6 g" and both "1,499" hits are now labelled; the render a-detail-propulsion.webp and the GA drawing still show the old MN2212 model (images, not re-rendered; caption says so).
- Per-subsystem mass numbers on the Subsystems tab (1260 g basis) are the 2026-11-15 CAD, labelled, not recomputed (no generator exists for that tab).
- K09-L: 71 mentions; 31 in the generated build guide ("K09-L practice" cure times etc., sourced from BUILD-GUIDE-A.md), 5 on the Decision tab, others labelled. Not rewritten.
- merge_check ERROR / WARN above (stale CG band and avionics allocation in the merge input).
- Build-film clips and renders were not regenerated (not in this task).
- I stopped two `http.server 8765 --bind 127.0.0.1` processes (PIDs 37044, 32396) that I believed were my own first check; they may have been earlier sessions' copies of the same command. The other 8765 servers were left running. My 8766 server is stopped at the end.

## Conductor note (2026-11-23)
merge_check's 1 ERROR / 1 WARN come from its default budget `redesign/params/mass_budget.json`, the K09-L record (limit 2,700 g, CG x 0.043-0.0501 m, avionics 36 g). Concept A is judged by its own gates: `cad_mass.py` / `mission_gate_a.py --o4b` (CG 22.05 mm in the A-P4 band, CL-A-CG / -SM / -CG-LATERAL PASS in run_all). Not a model defect; no concept-A budget file is passed to merge_check (open note, not a blocker).
