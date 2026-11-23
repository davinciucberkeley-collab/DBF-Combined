# Review round 8, T-038 Explorer refresh (commit 3b0dcf24), 2026-11-23

Reviewer: independent (eng-reviewer role). Category: review of site generation, no engineering analysis. Style: docs/reference/REVIEW-STYLE.md.

## Verdict: PASS WITH FIXES

All five checks pass on substance; three small findings (none changes a number on the pages).

## Check 1: no new interface, layout and styles unchanged. PASS
- `git diff --stat 3b0dcf24~1 3b0dcf24 -- '*.css'` returns nothing; no stylesheet changed. No `<style>`, `<script>`, `<link>`, `<nav>`, `<section>` or `<button>` markup line added or removed in app.html (diff grep, one id-only line match).
- Set of `id` / `data-tab` / `data-page` / `data-view` attributes, before vs after: the only differences are generated content ids: build-guide step anchors (build-b0b-machine-the-hub, build-c1b-lower-rib-fairings, build-c5-fin-root-fittings, build-e2-fc-esc-gps-rx-bosses-r2, build-e5-pack-straps; two removed) and drawing anchors (drw-AVN-010, FIN-009/010, WNG-011..014, FIN-005-L/R added; drw-AVN-001, drw-FIN-005 removed). The three top-level view buttons (guide, overview, reqs) are identical. No new page, tab or dashboard. app.html and index.html differ by identical id sets.
- Changed files (`git show --stat`): app.html, index.html, data/viewer-data.{js,json}, assets/*.glb, drawings webp/jpg, proofs/data/graph.js + readable.js, sync_bom_a.py, sync_status_a.py, the audit note. Nothing outside redesign/site and docs/audits.

## Check 2: changed numbers vs sources, recomputed. PASS
| Number on pages | Source recomputed | Result |
|---|---|---|
| BOM $1,939.17, margin $60.83, +30 % margin -$29.68 | `python -I redesign/qp/A/bom_a.py` | match |
| Order 1 $887.25 EST | ORDER-1.csv line 26 "ORDER 1 TOTAL" 887.25 | match |
| Predicted 1,881 g = 1,641.0 x 1.1174 + 48 | params-A.json l.290-306; arithmetic 1881.63 | match |
| CAD basic 1,641.0 g | params-A.json 1.64098; cad_mass.json mass_basic_kg 1.64098; sum of 131 viewer parts 1640.98 g | match |
| 12 strict FAILs | graph.json meta: 16 error strings = 15 FAIL + 1 UNVERIFIED (A-P13 flutter); distinct CL- claims failing = 12 (MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, VIB-IN-BAND, VIB-FC, VIB-GM, VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD, -STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY) | match (text says "15 error lines": correct for FAIL lines) |
| TP-15..TP-18 | TEST-PLAN-O4B.md l.312 (T-094) | match |
| D-227, D-228, D-233, D-234, D-238, D-239, D-240, D-241 | each has one row in params/CHANGE-LOG.md | exist |
| Exposed wire 0.597 m (D-240); CG 24.41 mm (D-228) | CHANGE-LOG D-240 text "0.597 strand-m"; D-228 text "24.41 mm" | match |
| FC 75 mm left | CHANGE-LOG D-239/D-240; viewer-data AVN-002 | match |

## Check 3: served pages (python -I -m http.server 8767 --bind 127.0.0.1, started, stopped; port confirmed closed afterwards). PASS
- index.html, app.html, data/viewer-data.json all HTTP 200.
- viewer-data.json: generated 2026-11-23 18:00 UTC; 131 parts entries (all in_model), 196 edges, 82 claims, 0 warnings. 131 = 129 placed parts + 2 lumps (HRN-001, HRD-001); the 9 HRN/HRD-prefixed ids reflect harness items, consistent with the audit's statement.
- AVN-002 "Kakute H743-Wing" cg_xyz_m [0.0472, -0.075, 0.0178]: y = -0.075 m. Motors PRP-001-* are SunnySky X2216 V3 880KV, 67.5 g.

## Check 4: legacy strings in the served pages. PASS
Text-only scan of index.html (app.html identical): MN2212 5 hits, 1,455 1 hit, 1,499 2 hits, K09-L 68 hits. I read every MN2212, 1,455 and 1,499 hit in context: each carries "earlier design (record)" (or "at selection, earlier design (record)"), with the current X2216 / 1,881 g / $1,939.17 alongside. K09-L: 68 hits, scanned only for nearby historical wording (record / previous / earlier / withdrawn), none found without it; not individually rewritten (matches the audit's own residual note). ZOHD Altus at app.html:433 is in the QP-1 candidate table (selection record), fine.

## Findings
| # | Sev | Where | Evidence | Required fix |
|---|---|---|---|---|
| F1 | Minor | redesign/site/data/viewer-data.json `budget` (`_note` "gate 1.50 kg", limit_g 1500, CG band 4.0..28.5 mm) | Written by redesign/qp/A/cad/viewer_data_a.py; pages and run_all use 1.47 kg gate (weigh-in) and the 1,881 g prediction. 3-D viewer budget gate is the 2026-11-18 figure. | Update the budget block source in viewer_data_a.py (or label it "earlier design (record)") and regenerate; check the viewer's budget bar. |
| F2 | Minor | same viewer-data.json: 2 occurrences of the string MN2212 ("T-Motor MN2212 base ...", "... adapter") outside parts[] | grep count 2; not in any part record (parts carry X2216). Likely connections / source lists. | Confirm they are sources/edges for the superseded part and label or drop. |
| F3 | Minor | docs/audits/2026-11-23-T038-explorer-refresh.md l.1-60 | First-pass tables report FAIL / PARTLY MET; second pass supersedes them but the first-pass "Result" lines are not struck. A reader may misread. | Add a one-line header "superseded by second pass" (append only). |

Not findings: K09-L mentions (record, labelled by context); merge_check ERROR/WARN (K09-L default budget; conductor note covers); renders (a-detail-propulsion, GA drawing) still show MN2212 CAD, caption says so.

## Check 5: secrets and personal data. PASS
Diff of app.html, the two sync scripts, the audit note, viewer-data.json and graph.js for api key / token / password / secret / emails / phone / C:\Users / user name: no hits. Commit author uses the Dalcouffe1 no-reply address as required.

## Verification commands
git show --stat 3b0dcf24; git diff --stat 3b0dcf24~1 3b0dcf24 -- '*.css' (empty); id-set diff of app.html/index.html; python -I redesign/qp/A/bom_a.py; python -I json reads of params-A.json, graph.json, cad_mass.json; http.server 8767 plus curl; regex scans of served index.html.
