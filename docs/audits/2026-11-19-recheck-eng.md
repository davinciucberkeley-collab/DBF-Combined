# Independent recheck: T-021, T-056, r3 minors m-3..m-9, T-062 (2026-11-19)

## T-021 (R-PHY-06/07): VERIFIED (no finding above LOW)
- AR-001..AR-005 under "After D-212 rev 3" each carry a labelled block with Category, Solver, Model version, Inputs, Assumptions, BC/loads, Settings, Outputs, Acceptance, Result, Limits. AR-003 has two blocks (analytic sweep, mesh gate), each with one category. AR-004 (hand calculation) and AR-005 (hand calculation) have one category each. Each record has exactly one category.
- Spot-checks against the output JSON and run log (rerun of linkage_loads_check.py; others read from stored out/*.json):
  1. Stall force 50.99 N (JSON F_stall_N 50.9937) = 51.0. OK.
  2. Free-play budget 1.2801 deg (arm 0.6258 + horn 0.6258 + Z-bend 0.0284), all three joint states 1.2800-1.2802. OK.
  3. D2 hold margin 2.929 (7.2 V), P_euler 111.17 N, peak step 42.74 N, hold rod force 17.05 N (linkage_dynamics.json). OK.
  4. Sweep: min positive clearance 0.0664 mm (mid), worst design contacts arm/rod 0.0284 mm (lo), keeper bridge/rod 0.0029 mm (hi). OK.
  5. Mesh gate report_d212r3_pose21.json: deepest depth 0.034 mm. OK. Runlog walls (4.2, 7.0, 13, 6.2, 145 s) match the text.
  6. Rib foam factored 431.8 / 860.9 kPa; torsion 504.3 kPa; bearing stall 36.65 MPa; keeper 19.48 MPa. All match JSON.
- LOW: AR-001 text gives gearing 0.905-0.930 over three states; JSON gives 0.9049-0.9300 (hi) to 0.9287 (mid max), so 0.905-0.930 is fine. AR-005 quotes 0.909-0.928 for the +-20 deg range (JSON 0.9089-0.9285), also correct. No fix needed.
- LOW: the "ten fields" are in fact eleven labelled lines (Result and Limits separate). Cosmetic.

## T-056 (R-PHY-08): VERIFIED (LOW notes)
- Reran `python -I redesign/qp/A/mechanism/linkage_loads_check.py`: exit OK, JSON identical to docs (loaded rate 231.25 / 263.03 deg/s; speed margins R1 2.89/3.29, R2 1.52/1.73, R3 0.84/0.95; torque margins hold 2.46/2.93, loaded 2.17/2.59).
- Hand check: omega_nl = 60 deg / 0.13 s = 461.5 deg/s = 8.055 rad/s; tau_loaded = 0.9282 x (0.146+0.0093+0.0098) = 0.1534 N m; 8.055 x (1 - 0.1534/0.397) = 4.946 rad/s; x 0.9282 = 4.59 rad/s = 263 deg/s. Matches. Required rates: R1 20 deg / 0.25 s = 80; R2 2 pi x 2.2 x 11 = 152.05; R3 2 pi x 2.2 x 20 = 276.5. All reproduce.
- Sources: no-load speed 0.13 s / 60 deg at 6 V and stall 0.333 N m at 6.0 V are in redesign/review/QP-4/SERVO.md lines 31-32; 7.2 V stall 0.397 N m is labelled EST (interpolated); required rates labelled EST (D5 0.25 s step is an EST in elevon_dynamics.py; 11 deg amplitude and 2.2 Hz crossover cited to A-P11 / CLAIMS-FIX.md); gearing from solved AR-001 linkage; 7.2 V speed "-" so the 6 V speed is used (conservative-by-label but note speed at 7.2 V is likely higher, so it is not optimistic). All inputs sourced or EST.
- Motor-mount FEA citation is real: CHANGE-LOG.md D-209 and D-210 rows exist; redesign/review/QP-5/FEA-ARM.md section 8 (line 123) and 8.1 (line 162) contain tube axial 29.9/203 and 79.8/350, shear 9.6/30, cup p99 0.75/9.3 and 3.1/20 (D-209), and D-210 cup peak 4.4/9.3, 18.0/20 (S3 13.6), p99 0.98 and 4.2, 167,457 elements. Numbers match. Properly labelled "cited, not rerun" (T-058 holds reproduction).
- LOW: R3 (full-throw sinusoid) is not met (0.84-0.95) and is explicitly stated as not a required case; the acceptance rests on EST requirement R2. Fine as labelled. CL-A-SERVO-SPEED is only proposed, no claim in the graph; the evidence lives in the record only.

## Review-r3 minors m-3..m-9: VERIFIED as closed as stated (MEDIUM caveats noted)
- m-3: a_build_steps.py line 571-574 has the 91 N receipt test; linkage_loads_check.json receipt_test_load_N 90.83, e_hi 1.9, required yield 1392 MPa. CLOSED.
- m-4: keeper_bridge_MEC008 in JSON (19.48 vs 20 MPa EST, hold 9.77); retorque/inspection text in a_build_steps.py D2a and D5b steps. CLOSED as a check line; honestly states 0.97 utilisation, creep "-", claim not added.
- m-5: compose_drawings.py PART_NOTES has MEC-004 / MEC-008 ORIENTATION text; viewed drawings/out/MEC-004.png: process line reads "ORIENTATION: PRINT FLAT on the 2.0 mm face (BUILD D3). Hole: STL = finished 1.1 mm; print 0.9 mm, ream 1.1 mm." PDFs timestamped 2026-11-19 01:56. CLOSED (MEC-008 PDF regenerated same minute; its note is in PART_NOTES, image not viewed).
- m-6: row K trade exists per record and CHANGE-LOG entry (not rechecked in engineering-decisions.md text beyond the log reference). CLOSED as a trade row.
- m-7: free_play/basis in JSON states flutter basis; BUILD D5b text has the +-19 deg rule. CLOSED as a decision; claim stays FAIL (as stated).
- m-8: stall_8p4V_informational 59.2 N in JSON; 7.2 V basis in notes. CLOSED.
- m-9: gen_params_a.py line 37 and 286-287 read report_d212r3_pose21.json for neutral and +-21 deg; +-20 deg still reads pre-D-212 report_pose20.json, labelled. Report depth 0.034 verified. CLOSED for neutral/+-21 only, as the record says (MEDIUM, open item 11: +-20 deg not rerun).
- MEDIUM (recorded, not a closure defect): open item 10, D3 Euler margin 9 % at 51 N stall, not rerun. AR-002 correctly says OPEN.

## T-062 (R-INT-05): VERIFIED with one LOW inaccuracy in the audit note
- Changed numbers on app.html vs sources: exposed wire 1.02 strand-m = wire_inventory.json totals_strand_m.EXPOSED 1.0246 (app.html shows 1.02); "0.86 without vendor pack leads" = 1.0246 - 0.1075 - 0.054 = 0.863 (arithmetic OK, component values from the audit, not re-read); BOM "42 lines" = BOM-A.csv 43 lines incl. header; build 42.8 h and 66 steps match BUILD-GUIDE-A.md (header says 66 steps); "115 of 115 parts" matches params-A.json cad3d.parts = 115; "59 of 59 swept steps" matches CL-A-ASSY-STEPS = 59 per proofs.
- a-sheet.svg contains "qp/A/cad CAD build, 115 parts." and make_sheet_a.py line 208 reads P['cad3d']['parts']['value'] (= 115, SRC-A-COLL "report.json parts checked").
- No new dashboard: `git show --stat c62c1ea1` lists edits to site/app.html, index.html, sync_status_a.py, a-sheet.svg and four new MEC-004/MEC-008 webp/jpg assets only; no new html/js dashboard file.
- LOW: audit says "distinct part_id in parts-a.csv = 115"; the file has 117 distinct ids (it also lists consumable kits HRN-001 / HRD-001, as the make_sheet_a.py comment says). The 115 is correct (params-A.json); the audit's stated derivation is wrong. Fix: edit the audit row to cite params-A.json cad3d.parts.
- LOW: audit row 22 says the SVG was hand-patched, while the commit message says "re-rendered from current CAD"; reconcile wording.
- LOW: "50 sheets" gallery vs 42 PDFs in drawings/out (gallery includes other sheets); not rechecked.

## Overall
No HIGH findings. All four items verified on re-computation; MEDIUM items are open items already declared in the record (D3 at 51 N, +-20 deg collision rerun, bench tests). Nothing marked VERIFIED COMPLETE by this review.
