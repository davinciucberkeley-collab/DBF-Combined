# T-062 (R-INT-05): stale numbers on the concept A Explorer

Category: documentation consistency (not an analysis). No Blender, FEA or SITL run. Not committed. Not marked VERIFIED COMPLETE.

## Commands (all exit 0 unless noted)
1. `python -I redesign/qp/A/make_build_guide_a.py` -> 0 (BUILD-GUIDE-A.md: 66 steps, 42.8 h; only diff is the "45 steps" sentence)
2. `python -I redesign/site/make_build_guide.py` -> 0
3. `python -I redesign/site/sync_status_a.py` -> 0
4. `python -I redesign/site/sync_bom_a.py` -> 0 (42 lines)
5. `python -I redesign/site/make_drawing_gallery.py` -> 0 (50 sheets; it re-encoded 100 existing thumbs, reverted with `git checkout -- assets/drawings`; new MEC-004/MEC-008 webp+thumb files stay because app.html now links them)
6. `python -I redesign/site/make_index.py` -> 0 (run last)
7. stale-string grep (45 of 45, 104 of 104, 0.87 strand, 104 parts, 98 parts, 45 steps, 42.4 h, 0.60 without) -> 0 hits in app.html and index.html
8. link check (python, href/src/data-src/data-poster/data-lightbox + #anchors): app.html 252 local links, 0 missing, 0 missing anchors; index.html same.

## Numbers changed (old -> new, source)
| Where | Old | New | Source / how |
|---|---|---|---|
| app/index "3-D interference gates" row | assembly 45 of 45 steps | 59 of 59 swept steps (66 build-guide steps) | CL-A-ASSY-STEPS = 59 (proofs/out/CHAIN.md l.1614; assembly.json 43 + assembly_bench.json 16); 66 = len(a_assembly_plan.STEPS) (cad/out/ASSEMBLY.md). Hand edit (static row, no generator) |
| same row | 104 of 104 parts | 115 of 115 | CL-A-ASSY-PARTS = 115 (CHAIN.md l.1621; assembly.json 115 parts placed; REPORT.md "115 parts"). Hand edit |
| same row, C8 constraint, Status tab (3 places) | exposed wire 0.87 strand-m | 1.02 | cad/out/wire_inventory.json totals_strand_m.EXPOSED = 1.0246. Rows in C8 and the "3-D gates" cell hand-edited; Status rows via sync_status_a.py (text edited in the script) |
| Status tab issue 1 | 0.60 without the vendor pack leads | 0.86 | 1.0246 - E-HRN-13 0.1075 - E-HRN-14 0.054 = 0.863 (wire_inventory.json). Computed |
| GA sheet note (inline SVG + assets/drawing/a-sheet.svg + showcase/concept-a/drawing/a-sheet.svg) | 98 parts | 115 parts | distinct part_id in cad/out/parts-a.csv = 115. Blender not run, so the SVG was patched by hand; make_sheet_a.py now counts parts from parts-a.csv so the next run is right |
| Build guide intro (BUILD-GUIDE-A.md and #build) | 45 steps | 66 steps | make_build_guide_a.py had a hard-coded 45; now len(plan.STEPS) = 66; regenerated |
| Build page header | 42.4 h hands-on | 42.8 h | BUILD-GUIDE-A.md (generated total); static header text, hand edit |
| BOM tab intro | 41 lines | 42 lines | sync_bom_a.py from BOM-A.csv; new row R14 (3 mm CF rod) and updated D-202/D-206 notes on rows R-lines came with the regeneration |
| Drawings section | 48 sheets | 50 sheets | make_drawing_gallery.py from drawings/out |

Unchanged and checked current: viewer-data.json (115 parts, generated 2026-11-18), "66 steps in 10 stages", "14 minutes" (a-build.mp4 = 833.7 s by mp4 header), step "x of 66" labels, stage clips.

## Open items for the caller
- 59 vs 66: the assembly sweep covers 59 steps (43 main + 16 bench run); ASSEMBLY.md headline says "66 steps (16 swept in the bench run...)", i.e. plan steps. The site now states both. CHAIN.md text still says "28 of 28 steps / 78 of 78 parts" in its "how to verify" strings and "35 steps, 96 of 96 parts" in SRC-A-ASSY (proofs dir, not touched).
- Exposed wire is 1.02 now versus 0.87 in HARNESS-ENCLOSED.md (D-199 record, left as record). The increase is the E-HRN-11 / -12 / -13 sampling in the current inventory, not investigated here.
- Team tab (K09-L-era role summaries, e.g. "145.8 g of 146, 50 claims pass", "X3108S + LANRC 45 A, 66 claims") is the previous-design record and was left alone.
- ui-review/ mockups (concept-1..3.html, gen/data.py) still hold 0.87; not linked from app.html/index.html, untouched.
- Files edited: site/app.html, site/index.html (regenerated), site/sync_status_a.py, site/assets/drawing/a-sheet.svg, showcase/concept-a/drawing/a-sheet.svg, showcase/concept-a/make_sheet_a.py, qp/A/make_build_guide_a.py, qp/A/BUILD-GUIDE-A.md (regenerated), new assets/drawings MEC-004/MEC-008.
