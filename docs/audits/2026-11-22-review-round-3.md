# Independent review, round 3 (2026-11-22, HEAD 13e6f4d3, working tree clean)

Reviewer: independent agent (wrote none of the rows). Acceptance read from `docs/task-ledger.md`; protocol from `docs/execution-plan.md`. Edited: this file only. Round 2 findings (`2026-11-22-review-round-2.md`) were the fix list. No web page re-fetched (no web tool); no 3-D gate run (saved outputs / generated files read). T-032 out of scope.

## Verdict table

| Row | Verdict | One-line reason |
|---|---|---|
| T-085 | **VERIFIED for the acceptance column, provided the D-236 forced-response sentence is amended (M-A)** | Defaults reproduce T-084 (rerun); pad inputs sourced and bounded (arithmetic reproduced); FAIL judged with band and 0.5 rule unchanged; TP-10b can decide D-185 (a). One unsupported claim in D-236 and one hidden risk (M-A) |
| T-066 | **VERIFIED** | M-1 closed: params match `structures_run.md`, chain rerun reproduces the 9 STRICT fails incl. new CL-A-VIB-IN-BAND; GM claims UNVERIFIED with T-089 open. Two Minor labelling points |
| T-081 | **keep READY (one gap)** | G-6, G-7, G-8 fixed and checked; G-9 (TP-12..14 ids not registered) still open; one internal contradiction (m-C) |
| T-014 | **keep READY (one gap)** | Rows now exist for T-085, T-086, T-087, M-1, round-2 review; but rows 105-110 sit outside the table (M-B) |
| T-023 | **keep IN PROGRESS, close after M-D and m-E** | M-2, F-9, F-10 fixed; N-3 (no T-084 / T-087 row in MASS-GATE / MISSION / REQUIREMENTS-A / SCHEDULE-A) still open; A-P10 text stale |

## Independent reruns

| # | Check | Command / arithmetic | Result |
|---|---|---|---|
| V1 | Ledger audit | `python -I tools/ledger_audit.py` | 109 requirements, 89 tasks, 0 errors (51 VERIFIED, 5 READY, 6 IN PROGRESS, 1 FAILED, 6 BLOCKED, 17 NOT STARTED, 3 DEFERRED) |
| V2 | T-085 defaults reproduce T-084 | `cd redesign/qp/A/mechanism/out/T085_data; python -I t085_detail.py` (reran, about 1 min) | spar-only kd / nom / hi 201.0 / 215.3 / 244.2 Hz (cx 0.02, cy 0.52); cell nominal 84.6 / 88.0 / 96.2 Hz, hi in band at cx 0.81 / cy 0.93. Equal to T-084 s2.4 and to the report s5 |
| V3 | Pad modulus (Gent) | E = 0.0981 (56 + 7.62336 S) / (0.137505 (254 - 2.54 S)) | S 30 / 50 / 70 A -> 1.142 / 2.456 / 5.520 MPa. Matches the report s2 |
| V4 | Pad shape factor and multiplier | S = 3,000 / (2 (100 + 30) x 1.0) = 11.54; Ec_inc = E (1 + 2 S^2) = 267 E; bulk limit K 1 GPa: Ec = Ec_inc K / (Ec_inc + K) | 50 A: 655 -> 396 MPa = 161 x E; 70 A: 1,474 -> 596 MPa = 108 x E. Matches. K "—" (unsourced) but swept to 0.25 GPa (x74), no change in the governing mode |
| V5 | Pad geometry vs CAD | `electrical.py` l.733, 925; `BOM-A.csv` W09 | PWR-003 100 x 30 x 1.0 mm silicone, hardness "—", EST; as the report says |
| V6 | Governing-mode table | `detail_t085.txt` (printed by V2) rows: nominal cell, 6061, 50 A | 100.1 / 102.9 / 108.7 Hz, cx 0.74-0.75, cy 1.33-1.35, energy spar 34 %, arm 24-29 %, hub joint 23-29 %, bridge 6-7 %, no pad. Matches report s3.1. Soft pad: 206-211 Hz pad bounce (pad energy 76-77 %) |
| V7 | Proof chain | `python -I proofs/run_all.py` from `redesign/qp/A` (rc 1, expected) | Summary `UNVERIFIED 222, PROPOSED 17, CHECKED 323, VERIFIED 0; fails 13`; STRICT fails: MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY (8) + VIB-IN-BAND (value 3, limit 0) = 9; CL-A-FLUTTER-ELEVON-NOM UNVERIFIED. `git status` clean afterwards, so the committed claims JSON equals a fresh run. Equals `T066M1_fixes.md` s2 |
| V8 | Params vs sources | `gen_params_a.py` l.179, 189-198 vs `structures_run.md` l.26, 52, 56, 116-118 | gust_n_vd 2.71; vib_below 66 / 69 / 81; vib_above 438 / 474 / 532; band 94-321 Hz; hover 1P 113 Hz, 6,789 rpm; 2P 268 Hz (8,028 rpm): all equal. gm_* values unchanged, marked `est`, "STALE, MN2212" |
| V9 | BOM | `python -I redesign/qp/A/bom_a.py` | Total $1,939.17, margin $60.83 (as TEST-PLAN l.179 and D-235) |
| V10 | Alcobra / T-Motor text | grep `parts-a.csv`, `BUILD-GUIDE-A.md` | No "Alcobra" / "T-Motor" / "1.75 x 2.5 ... must change" hits (M-2 of round 2 fixed). Only BOM-A.csv T1 note mentions Alcobra as history |
| V11 | CAD numbers | `cad_mass.json` mass_basic 1.63298 kg, fin_h 0.1937; `BUILD-GUIDE-A.md` l.67, 1372, 1475 (387.4 mm); `DRAWINGS-A.md` stamp "commit 604443a7" | consistent; geometry unchanged since T-084; T-085 changed no CAD file |
| V12 | CLAUDE.md mass line | CLAUDE.md l.28 | now "predicted 1.64 kg at D-219, now 1.88 kg EST after D-226..D-233 ... mass gate missed"; F-10 residual closed |

## T-085 (D-185 FE upgrade): VERIFIED for the acceptance column, with M-A

Acceptance: "D-185 (a) judged with the upgraded model, band and >= 0.5 rule unchanged; T-A-TAP procedure and pass rule in TEST-PLAN-O4B".

Is the upgraded FE credible, and is every EST sourced or bounded? Yes, with stated limits.
- Pad: the paused run's E 4 / 2 / 0.5 MPa was unsourced and applied as E A / t; the report replaces it with Gent E per Shore A (V3), the thin-pad shape factor and a bulk-limited compression modulus (V4); the bounds are swept (30 / 50 / 70 A, K 1 and 0.25 GPa, tray 24 / 112 mm, hub 6061 / PETG, cell nominal / lower). Hardness, K, pouch and strap stiffness, bond slack and the core-slot support are "—" and are listed as limits, not invented. The audit finding "pad 62-65 % was an artifact" is consistent with V4 (100-200x too soft in z) and with V6 (no pad energy in the governing mode once the compression stiffness is bounded).
- Hub joint: D-209 mesh, not the drawn D-220 sleeve; said plainly. PETG block as a proxy for slack is labelled a proxy.
- The FAIL is insensitive to every bounded EST (pad nominal and stiff give identical modes, V6), so the conclusion does not rest on an unsourced number. 23 of 24 groups fail; the one pass is by 0.1 Hz at one extreme and is correctly called a coincidence.
- Defaults reproduce T-084: V2, exact to the digit. `structures_a.py` was reported exit 0 (not re-run by me, 3 min; the T-085 stdout / exit files exist).
- Band 94-321 Hz and 0.5 are used unchanged (lower edge 94 vs the 83.6 Hz of the iter3 band is stricter, not looser).

Can TP-10b decide D-185 (a) as defined? Yes, read in `TEST-PLAN-O4B.md` l.31-32, 288-304.
- Pass rule: no mode in 94-321 Hz with max(cx, cy) x (1 + u) >= 0.5; fail if max / (1 + u) >= 0.5; the undecided case counts as a fail until the FE is updated to the measured frequencies. Band, 0.5 and the "one strong motor" rule match `structures_a.py` (`cx = sqrt(sum v_x^2)` over the four motor nodes, `cy` the same over y, z, mass-normalised).
- The measured quantity is the same as the FE one: driving-point phi^2 = A / (omega I), cx / cy as the sqrt of the sums over the four motors. I checked units: the FE `v` is mass-normalised, so the threshold is in kg^-1/2 in both. The impulse is calibrated on a 1 kg reference mass (no force hammer), the sensor is the FC IMU (rate >= 2 kHz "to be confirmed"; a $5-10 I2C fallback is named and flagged as a purchase). Hit sets: 4 motors x 3 axes x 5 hits plus hub and pack. Honest and reproducible at $0.
- Caveats (Minor, m-A): (1) the impulse calibrated on a free 1 kg mass gives the pulse width of that contact, not of the hit on a stiff cup, so the usable bandwidth to 321 Hz needs the stated check on the reference mass AND on the cup; the sheet says only the first. (2) The tray is not included in the FE comparison (A-P10(c) within +-20 %) unless the weighed mass is entered; stated. (3) Route A in the report s7 says "if the measured mode is below 94 Hz / (1 + u) decoupled the airframe passes" which mixes frequency and coupling; the test plan's rule (coupling) is the correct one, align the report wording. (4) A-P10(a) in `REQUIREMENTS-A.md` l.43 still lists the MN2212 rotor bands (hover 1P 100-119 Hz ... cruise 2P 243-253 Hz), not the 94-321 Hz band the tests and claims use; the band was recomputed in T-084. The requirement text should be refreshed so "unchanged" has one referent.
- Timing: TP-10b runs after the build and before the first tethered hover; it does not gate 2026-12-15 (D-236, TP-10b "When / who"). Consistent with D-236; but see m-C for two older lines that still say the tap test decides 12-15.

Is the D-236 decision reasoned, and does it hide a risk? Reasoned: no lever clears all corners (s6; I checked the lever table is internally consistent with the mass numbers: 4 arms 61.1 -> 50.0 g = -11.1 g), screened with the ladder rule, nothing applied, rule not relaxed. Hidden risk:

- **M-A (Major, within D-236 text; analysis, not an arithmetic error).** D-236 closes with "forced response at the motors stays small (T-066 sweep, 26.6 m/s2 summed, MS +0.13)". That sweep (`structures_run.md` s4, `vib_fc_ms2` in `gen_params_a.py` l.194-195) is the **spar-only** model, in which the strong mode is at 201-244 Hz with cy 0.52 and responds 0.12-0.18 m/s2 on resonance. The governing mode of the credible upgraded model is at **94.6-108.7 Hz with cy 1.12-1.35 (about 2.6x the coupling)**. Hover 1P is 113 Hz at the lowest swept hover rpm (6,789 rpm) and 1P reaches 100 Hz at 6,000 rpm, the bottom of the swept range; the hi-corner mode at 108.7 Hz is about 4 % from hover 1P. So the quoted 26.6 m/s2 does not cover the mode the FE says is there, and a forced-response run on the upgraded model was not done (grep of the report for "forced" / "sweep": none). The claim "stays small" is therefore unsupported for the model D-236 itself adopts, and the risk is a hover resonance on the first tethered flight, which is exactly when the tap test result will first matter. Required fix: either run the existing forced-response routine (zeta 0.5 % and 1 %, U 1 g mm, 6,000-11,415 rpm) on the T-085 cell-credited model with the cage mode (cy 1.35) and record the FC acceleration, or delete the sentence and mark the forced response of the upgraded model "—, not run" in D-236 and add it to T-A-TAP / T-089 scope.
- m-B (Minor, schedule): D-236 says "if the measurement confirms a strong in-band mode, re-open the C-route trade ... before flight". If that happens, the arms (10x8 in the best lever) are already bought and bonded; the 10x8 tube price is "—" and the lever clears only 4 of 6 cases. The decision is acceptable for a student design with weight-over accepted, but the ledger should carry an explicit contingency (cost, 1-2 week lead time, rebuild of 4 arms) so the end-of-April date is not silently at risk. No row exists; T-089 covers only the gain margin.
- The BOM / mass margin of the lever is not hidden: -11 g, "tube price —" is stated.

## T-066 (structures re-baseline, M-1): VERIFIED

Acceptance: current-geometry run, every number traced, limits of D-202 arm crossing and hub stiffness listed (met in round 2). The round-2 gap M-1 (claims not re-pointed) is closed:
- V8: five vibration params and `vib_inband_corners` re-pointed with source ids SRC-A-STRUCT-RUN / SRC-A-T085 and the old value in each note; values equal `structures_run.md`.
- V7: the chain builds and now carries the D-185 (a) FAIL as CL-A-VIB-IN-BAND (3 corners vs limit 0); CL-A-VIB-LOW / HIGH how-texts say they do not show D-185 (a) met. The 8 earlier fails are unchanged (no limit relaxed). No false CHECKED on the D-185 rule remains.
- CL-A-VIB-GM / GM-SHIFT are UNVERIFIED (stale MN2212 / iteration-2 cage, values kept and labelled), and **T-089 exists** (NOT STARTED, depends on T-085, own acceptance). The ledger row therefore does not hide the gap.
- m-1 of round 2 (record vs HEAD run) is addressed by the pointer line per the fix note (not re-read in full).
- m-D (Minor): CL-A-VIB-LOW / HIGH still read CHECKED with the spar-only values (66-81 Hz below, 438-532 Hz above). The T-085 model finds a strong 324.7-348 Hz mode (cy 0.59-0.64) just above the 321 Hz edge, and 297-317 Hz modes for the PETG-hub bound, so "lowest above the band 438 Hz, margin 36 %" overstates the separation on the model D-236 adopts. Add a note to the claim (or an est value 324.7 Hz / margin +1 %) so the chain does not show a comfortable margin. The in-band claim fails regardless, so no verdict changes.
- m-E (Minor): `cruise_2p_hz_hi` is named "cruise" but holds the hover-lean 2P (the note says so); rename at the next edit.

## T-081 (test and purchase plan): keep READY (one gap)

Round 2 gaps, rechecked at HEAD:
- **G-6 fixed.** TP-10 now points to TP-10b; the 88.0 / 84 Hz limit is gone (grep: 0 hits of "88.0 Hz" in the tap row). TP-10b has the method, equipment, pass rule on the 94-321 Hz band (see T-085 above). It can decide D-185 (a).
- **G-7 fixed.** TP-3 carries "[D-233] If the pad is lengthened (X_GROUND 0.3475 m), re-check A-P9: 30.22 deg there, under the 30.5 deg target" (l.24), matching round 2's figure.
- **G-8 fixed.** l.179 "Adopted total ... $1,939.17 ... margin +$60.83" equals V9; l.189 T1 is "Zoro Select 61F2X2.5-12 ... $43.29", T11 Zoro $33.69; the R15 / Carbonwebshop open item points to T-088.
- **G-9 still open (Minor).** `grep TP-12|TP-13|TP-14 docs/requirements.md docs/task-ledger.md` returns nothing: the three coupon tests have no requirement or ledger link. Fix: add the ids to the T-081 row or to R-PHY-09 text.
- m-C (Minor, internal contradiction): `TEST-PLAN-O4B.md` l.12 s0 item 1 still lists "the A-P10 tap test" among what decides 2026-12-15 (then says it cannot be done by 15 Dec); l.167 item 6 offers a partial PETG cage or moving criterion 3. TP-10b and D-236 say the test does not gate 12-15. Make one statement (suggest: delete the tap test from item 1 and close item 6 with "decided after the build, D-236").
- Purchase total read and under $2,000 (V9); every open coupon-gated row has a test (TP-12..14 numeric lines present). Acceptance is met; keep READY only for G-9 and m-C, both one-line fixes.

## T-014 (model-usage log): keep READY (one gap)

Round-2 gaps m-6 / m-7 are closed in content: rows exist for T-086, T-087, round-2 review, T-085 (paused and resumed), T-066 M-1 + F-10, and the earlier rows for T-066, T-084, T-023 / T-081 fixes. "Usage not recorded" is stated where true.
- **M-B (Major for this row's acceptance "one row per delegation", cosmetic for the data).** Rows 105-110 were appended after the prose notes ("Scope (2026-11-18)...", l.103) with no table header or separator, so they are not part of the table (table ends l.94; l.95-103 are paragraphs). In a Markdown viewer they render as plain text, and this is the structure the 2026-11-19 re-check fixed ("one table"). Fix: move rows 105-110 into the table above the prose (or add a second header) and keep appending there.
- m-F (Minor): no row yet for this round-3 review (expected: the conductor logs after it returns), and none for the conductor-run round-2 fix batch (M-2 regeneration, T-088 row, CLAUDE.md edit, F-9 note). If those were done by the conductor, one line in the log saying so satisfies "per delegation".
- The structural suggestion (ledger_audit warning when a READY / VERIFIED S / O row has no model-usage row) is still not implemented; not required.

## T-023 (CAD consistency final re-diff): keep IN PROGRESS

Earlier findings:
| ID | Status | Evidence |
|---|---|---|
| F-1, F-2, F-3, F-5..F-8 | Fixed (rechecked) | V10, V11; `parts-a.csv` / `BUILD-GUIDE-A.md` have no Alcobra / T-Motor / "must change" text; BOM T1 / T11 Zoro |
| M-2 (stale T1 / T11 vendor text) | **Fixed** | V10 |
| F-9 (WNG-009) | **Fixed** | `MASS-GATE.md` l.212-216: WNG-009-L/R 2.0 g, enter the CAD table as `DMP_STATOR_G` (`wing.py` l.571), not in `printed_mass.json` (T-067 voxel basis), fluid and preload mass "—" (no unsourced estimate), AVN-010 "14: CHECK" is a drawing-tool note. Accepted |
| F-10 stamps | **Fixed** | `DRAWINGS-A.md` l.3 "commit 604443a7" (a commit after T-084 f7b385f6, so it contains FIN_H 0.1937); CLAUDE.md l.28 updated (V12). Note the stamp is the commit that was HEAD when regenerated; later commits changed no CAD file (`git diff 604443a7 HEAD --stat`: docs, proofs, params only) |

New or remaining:
- **M-D (Major per the acceptance "no unexplained inconsistency"; carried N-3 from round 2).** `MASS-GATE.md` s15 table still stops at "T-083b tallied 1,634.5 g / 1.8734 kg" and its last paragraph cites $1,981.31 / +$18.69 (BOM now $1,939.17, V9); `grep -c "T-084|1.8796|0.1937"` gives 0 in `MASS-GATE.md`, `MISSION.md`, `REQUIREMENTS-A.md`, `SCHEDULE-A.md`. The current numbers (basic 1,633.0 g, tallied 1.8796 kg, CG 23.13 mm, FIN_H 0.1937, A-P9 31.00 deg) live in `T084_report.md`, D-233 and `cad_mass.json` only. Add one T-084 row and the current BOM to s15, and one current-state line to the other three files.
- m-G (Minor) `REQUIREMENTS-A.md` A-P10(a) lists the MN2212 rotor bands while claims and tests use 94-321 Hz (see T-085 m-A (4)); refresh it. A-P10 should also record that (a) is carried FAIL on the model and decided by TP-10b.
- m-H (Minor) `params-A.json` `cost` has no `total_usd` key at the top level of `cost` (the total is in `bom_rows` / the claim CL-A-COST-TOTAL = 1,939); not an inconsistency (V7, V9), but a reader grepping `cost.total_usd` gets None.
- Consistent (checked, no issue): mass 1.63298 kg basic (cad_mass.json), FIN_H 0.1937 in CAD / build guide / drawings / structures, BOM total across `bom_a.py`, TEST-PLAN and D-235, claims values vs `structures_run.md`, T-085 touched only `fe_a.py`, `TEST-PLAN-O4B.md`, report and data (no CAD, mass, BOM or parts-list change; `git diff 604443a7 HEAD`).
- Verdict: close after M-D and m-G. The T-085 re-diff the earlier review asked for is done here: T-085 introduced no CAD / BOM / parts inconsistency.

## Findings summary (severity-ranked)

| ID | Sev | Row | Finding | Required fix |
|---|---|---|---|---|
| M-A | Major | T-085 / D-236 | "Forced response stays small (26.6 m/s2)" rests on the spar-only model; the governing mode of the adopted model (94.6-108.7 Hz, cy 1.35, 4 % from hover 1P at hi) was never run through the forced-response sweep | Run the sweep on the T-085 model, or strike the sentence and record "not run" (add to T-A-TAP / T-089 scope) |
| M-B | Major (for acceptance) | T-014 | Rows 105-110 sit outside the table (no header) | Move them into the table |
| M-D | Major | T-023 | MASS-GATE s15, MISSION, REQUIREMENTS-A, SCHEDULE-A have no T-084 / T-087 state; MASS-GATE cites the old BOM total | Add the rows and current numbers |
| G-9 | Minor | T-081 | TP-12..14 ids not in requirements / ledger | Register them |
| m-C | Minor | T-081 | s0 item 1 and s5 item 6 still say the tap test decides 12-15 | One consistent statement |
| m-A | Minor | T-085 | Pulse-bandwidth check on the cup, report wording on route A, A-P10 text stale | Edit as listed |
| m-B | Minor | T-085 / D-236 | No contingency row (cost, lead time) if TP-10b fails after the arms are built | Add to ledger (new row or T-089 note) |
| m-D | Minor | T-066 | VIB-HIGH shows 438 Hz / +36 % while the T-085 model has strong modes at 324.7-348 Hz | Annotate the claim |
| m-E, m-F, m-G, m-H | Minor | T-066 / T-014 / T-023 | Name `cruise_2p_hz_hi`; log rows for review round 3 and conductor-run fixes; A-P10(a) bands; `cost.total_usd` absent | Fix at next edit |

No Critical finding. No limit was relaxed by T-085, T-066 M-1 or the test plan (band 94-321 Hz, 0.5, A-P9 30 deg, $2,000 hard).

## Not checked
- `structures_a.py` (3 min) and the hub FEA (`t085_hubflex.py`) were not re-run; `t085_detail.py` and `run_all.py` were. The lever table (s6) was spot-checked for mass arithmetic only, not re-run.
- Web sources (Dow durometer grades, Wikipedia Gent formula, Orfeo / Kelly / Van Engelen, Zoro) not re-fetched; the Gent formula was reproduced numerically from the stated expression.
- 3-D gates not run; none needed (no CAD file changed since T-084).
- `BUILD-GUIDE-A.md` grep-checked for stale vendor and FIN_H text, not read in full.
