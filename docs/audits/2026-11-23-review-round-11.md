# Review round 11: re-review of T-098 rev 3, the T-095 fixes, the Explorer #sims T-098 section and the T-097 correction notes (2026-11-23)

Reviewer: independent eng-reviewer (opus). I did not write any of the work reviewed. I edited only this file; ledger, spec,
requirements and CHANGE-LOG are untouched. Round 10 findings are in `docs/audits/2026-11-23-review-round-10.md`.

## Verdicts
| Item | Verdict | Key check |
|---|---|---|
| (a) T-098 rev 3 | **VERIFIED** (the main region holds), with 4 minor corrections that do not block | grid recomputed from the raw JSON matches; spot rerun 35 N / zeta 0.02 reproduces exactly (FAIL, 20.28 mm); the untested corner 39 N / zeta 0.02 run now and PASSES (18.81 mm, 9.54 g); A-P9 30.60 deg reproduced; the fallback was run at the 30 mm-pad foot position (minor, 98r-1) |
| (b) T-095 fixes | **VERIFIED** | Fins card says "25 x 23 mm rib tubes" in both app.html and index.html; the intro now says 131 parts; no "14 x 12 mm rib" text left in the Subsystems view |
| (c) Explorer #sims T-098 section | **SEND BACK** (text only) | regenerating in a scratch copy gives a byte-identical page and the T-098 tables match the JSON, but the AR-015 block still says the basis is open and "on ±20° it passes with 0.08 to spare" and shows the 20/25 deg rows as PASS, which contradicts the D-244 withdrawal |
| (d) T-097 correction notes | **VERIFIED** | the note is present in AR-014 (l.373), in the T-097 audit (l.6, plus the s1 geometry row reworded) and in T097_results.json (top-level `correction` key, and all 30 rib-RF rows carry the 14x12 note) |
| ledger_audit | 0 errors | `python -I tools/ledger_audit.py`: 113 requirements, 99 tasks, 0 errors |

## (a) T-098 rev 3
### Checks run
1. **Grid recomputed** (worst of the 10 cases, limits stroke <= s_max, n <= 12 g, tilt <= 3 deg, RF >= 1.0) from
   `plateau_rib25.json`, `zeta_rib25.json`, `zeta2_rib25.json` (20 mm) and `stroke24_rib25.json`, `zeta24_rib25.json`,
   `zeta24b_rib25.json` (24 mm). Every PASS/FAIL cell and number in the audit s2 grid, AR-016, the D-243 trade table, TP-3 s2.3
   and the #sims grid matches. Pass set at 20 mm: zeta 0.01: 40, 42 N; 0.02: 37.5-42 N; 0.03: 37.5-42 N; 0.05: 33-42 N;
   0.07: 33-37.5 N; 0.10: 33 N.
2. **Spot rerun** (`T98_FP=35,39 T98_Z=0.02 python -I sweep_t098.py zeta 25 <scratch>/r11_zeta.json 10`, the T-097 env, 20 runs,
   24.7 s, exit 0). 35 N / 0.02: all 10 case rows identical to `zeta2_rib25.json` (max |diff| 0.0): stroke 20.28 mm FAIL.
   39 N / 0.02 (a corner of the accepted region that had **not** been run): stroke 18.81 mm, n 9.54 g, tilt 2.46 deg, RF 3.31: PASS.
3. **Region corners** (20 mm, Fp 37.5-39.0 x zeta 0.02-0.05): 37.5/0.02 P (19.56 mm, 0.44 mm margin), 39/0.02 P (this review),
   37.5/0.05 P, 39/0.05 P (11.13 g, 0.87 g margin); interior 37.5/0.03 P. Over the tested points, stroke and tilt fall
   monotonically as Fp and zeta rise and n rises with both, so the worst-stroke corner is (37.5, 0.02) and the worst-n corner
   is (39, 0.05). Both pass, so TP-3 accepts no pair the model fails (10 AR-014 cases, mu 0.40).
4. **39 N cap.** T083b_report l.92: the D-226 path rows have min 1.09 over zeta 0.02-0.05 (C3 at 0.02-0.05, R4 junction at
   0.05). 1.09 x 36/39 = 1.006, which the docs label EST. Scaling by Fp is conservative here: in the record run the peak foot
   force grows less than in proportion (Fmax/Fp 1.53 at 30 N, 1.49 at 37.5 N), and the damping force grows with sqrt(Fp).
   Small basis caveat, info only: T-083b ran at 1.873 kg, 24 mm stroke, x_foot 0.3475. At 1.881 kg the mass scaling gives
   1.006 x 1.873/1.881 = 1.002, still >= 1.0 but thin and below the project's 1.15 margin habit. TP-3 already requires the
   strength rows to be rerun at the measured pair for Fp > 39 N. I recommend the same rerun at the measured pair whatever its
   value before first flight. This is non-blocking.
5. **A-P9** recomputed by hand from `landing_a.cad_geom()` (CG x 22.05, z 6.56 mm; z_edge 0.1967, z_foot 0.1907), edge / centre:
   x_foot 0.3375: 31.08 / 30.27 deg; 0.3435: **30.60** / 29.81 deg; 0.3475: 30.30 / 29.50 deg. Matches.
6. **D-244** (CHANGE-LOG l.952), the D-244 trade table, AR-016 "Result (pitch use)", audit s3 and T098_results.json all show
   the 15 deg standing line FAIL (0.69 / 0.77-0.79) as an open item. The 20 and 25 deg rows are "information only" with
   `pass: null`. The fraction-preserving arithmetic is corrected (7.2 deg). The worst surface is 12.0 deg (T-074).
7. **Superseded text.** Searched AR-016, the trade tables, CHANGE-LOG, TEST-PLAN and the T-098 audit for "33-42", "0.183-0.233",
   "governing basis" and "commanded-endpoint basis". Only two hits remain, both legitimate: AR-016 "33-42 N pass" is stated as
   the zeta 0.05 result inside the grid, and trade-table row 2a is marked "REJECTED by review 98-1". TP-3 s2.3 drops the
   37 N peak-force line, and the TP-3 re-spec block (l.252) points to the joint region.
8. `landing_a.py` is unmodified (`git diff --stat` empty).

### Findings (minor, do not block)
| # | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| 98r-1 | Minor (the fallback is not adopted) | The 24 mm fallback sweeps (`sweep_t098.py` group `stroke`, and `zeta` with `T98_S=24`) change only `s_max`. The feet stay at the 30 mm-pad position x_foot 0.3375, although the 36 mm pad puts them at 0.3435 (the A-P9 calc in the same section uses 0.3435). Rerun here with `x_foot=0.3435` (scratch `fb36.py`, 40 runs, 37 s): 34.5 N / 0.02 gives tilt **2.97 deg** (reported 2.81), stroke 21.43 mm, n 8.51 g, RF 2.59: still PASS, but with 0.03 deg margin, not 0.19. 39 N / 0.05 gives tilt 2.27, stroke 16.69 mm: PASS. | `sweep_t098.py` l.44-46; scratch rerun | Rerun the fallback grid at x_foot 0.3435 before the fallback is ever used. Correct "binding tilt 2.81 deg" in the audit s2, AR-016, the trade table row 2c, TP-3 s2.3 and the #sims fallback table, or label those numbers as the 30 mm-pad foot position. |
| 98r-2 | Minor | "model passes every tested corner" (T098_results `accepted_foam_region`, TP-3 "bracketed by its tested corners"): the 39 N / zeta 0.02 corner had not been tested. It passes (this review), so the claim is now true, but only because of this review's run. | `zeta2_rib25.json` has 40 N, not 39 N | Add the 39 N / 0.02 run to T098_data and the results (or cite this review). |
| 98r-3 | Minor | Trade-table "Passing grid" line: "35 N: 0.05" and "39-40 N: 0.01-0.05" list points that were not run (35 N at 0.05; 39 N at 0.01-0.03). | engineering-decisions.md, after the D-243 table | List only the points that were run, or mark the inferred ones. |
| 98r-4 | Minor | The audit title says "rev 2" but the file contains rev 3 sections (fallback). | T-098 audit l.1 | Retitle "rev 3". |

## (b) T-095 fixes
- app.html and index.html #subsystems Fins card: "25 x 23 mm rib tubes to CF-sheet fin nodes". `grep "14 x 12 mm rib"` finds
  nothing in either file. The one remaining "14x12 rib" string is BOM row R15 ("replaces the 14x12 rib use of R09"), a
  correct record.
- Intro: "131 parts in the current CAD data (redesign/site/data/viewer-data.json)" matches 131 parts.
- Info only, outside T-095 scope: the Status "Mass gate missed" row and one more still say "129 placed parts". The CAD part
  name in `wing.py` l.942 is still 'Fin rib tube 14x12', so viewer-data FIN-002 names stay stale until a CAD regeneration.
  Neither blocks T-095.

## (c) Explorer #sims T-098 section
Checks: copied `make_sims_view.py`, app.html, both results JSON and the plots to a scratch copy and ran the generator: exit 0,
"33437 bytes, plots 2, T-098 in". The output is byte-identical to the working-tree app.html, and the #sims section in
index.html matches app.html. The T-098 block was checked against T098_results.json (145 rows) and my grid recomputation:
the region (PASS at 37.5 N / 0.02, 0.03, 0.05 and 39 N / 0.05), the pass* cells above the 39 N cap, the sweep at 0.05, the
37.5 N record table, the fallback table and the A-P9 table all match. The pitch-use rows in T098_results.json are correctly
labelled (15 deg governing FAIL; 20/25 deg information only).

| # | Severity | Finding | Evidence | Required fix |
|---|---|---|---|---|
| SV-11-1 | **Major** (published text contradicts the decision record) | The AR-015 block, hard-coded at `make_sims_view.py` l.184, still says "Which elevon basis governs is still open ... On ±15° the line fails; on ±20° it passes with 0.08 to spare". Its table, built from T097_results.json, shows "share of ±20°: 0.52 ... PASS" and "±25° ... PASS" against "0.60 or less". D-244 rev withdraws the 20 deg basis: 15 deg is the standing line, and 20/25 deg are information only. The page's own summary paragraph says pitch use is FAIL / open, so the page now contradicts itself. | rendered #sims text; `make_sims_view.py` l.184 | Reword the AR-015 intro (15 deg standing line, FAIL, open item; 20/25 deg information only). Render the 20/25 deg rows with an "info" tag, not PASS badges (e.g. take the badges from T098_results.json, where `pass` is null). Regenerate app.html and index.html. |
| SV-11-2 | Minor | The fallback table is titled "36 mm pad" but its numbers use the 30 mm-pad foot position (98r-1). | as 98r-1 | Follow 98r-1. |
| SV-11-3 | Minor | "A foam that is too soft or too lightly damped bottoms out ... (stroke past 20 mm, then a jolt of 15-34 g)". Several failing points bottom out by only 0.1-0.5 mm with n < 12 g (31.5 N / 0.05: 9.26 g; 35 N / 0.03: 11.37 g; 37.5 N / 0.01: 9.67 g). | grid recomputation | Say "up to 34 g" or "stroke past 20 mm, in some cases a jolt of 15-34 g". |

## (d) T-097 correction notes
- AR-014 (`docs/analysis-records.md` l.373): the correction paragraph names the 14x12 default and the 25x23 drawn tube, says
  stroke / n / tilt / tip-over are unaffected, and points to AR-016.
- T-097 audit: the same note at l.6. The s1 "Landing geometry" row now says "rib tube NOT read from the CAD: landing_a.py
  default 14x12 mm", which fixes the false "read live" claim.
- `T097_results.json`: top-level `correction` key added. All 30 rib-RF rows carry "computed on the default 14x12 rib tube, not
  the drawn 25x23 (review round 10); see T098_results.json". No rows were deleted.
Verdict: VERIFIED. With these notes T-097 meets the round-10 condition for VERIFIED as a record.

## Commands run (this review)
| Command | Exit | Result |
|---|---|---|
| inline python: worst-of-10 grid from the six T098 sweep JSON files | 0 | matches audit / AR-016 / TP-3 / #sims |
| `T98_FP=35,39 T98_Z=0.02 python -I sweep_t098.py zeta 25 <scratch>/r11_zeta.json 10` (T-097 env) | 0 | 24.7 s; 35 N identical to zeta2_rib25.json (FAIL 20.28 mm); 39 N PASS 18.81 mm / 9.54 g |
| `python -I <scratch>/fb36.py` (24 mm, x_foot 0.3375 vs 0.3435, 34.5 N/0.02 and 39 N/0.05) | 0 | 37 s; 34.5/0.02 tilt 2.81 -> 2.97 deg; 39/0.05 2.15 -> 2.27 deg; all PASS |
| inline python: A-P9 from `landing_a.cad_geom()` at x_foot 0.3375 / 0.3435 / 0.3475 | 0 | 31.08 / 30.60 / 30.30 deg edge |
| `make_sims_view.py` in a scratch copy | 0 | byte-identical app.html |
| `python -I tools/ledger_audit.py` | 0 | 113 requirements, 99 tasks, 0 errors |
Scratch outputs (not kept in the repo): `C:\Users\dillo\AppData\Local\Temp\claude\1dc032cbc6faa005\7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f\scratchpad\r11_zeta.json`, `...\scratchpad\fb36.py`.
