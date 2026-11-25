# Independent review, round 2 (2026-11-22, HEAD 05878a68)

Reviewer: independent agent (wrote none of the rows under review). Rows: T-066, T-084, T-086, T-087, T-014, T-032, T-081, plus the T-023 re-review. Acceptance read from `docs/task-ledger.md`; protocol from `docs/execution-plan.md` ("READY FOR REVIEW -> VERIFIED COMPLETE only after an independent check"). No project file was edited except this one. T-085 (concurrent implementer) files were read at HEAD; `git status` was clean when checked, so HEAD equals the working tree for the files cited. Web pages (Zoro, Alcobra, vendors) were NOT re-fetched: no web tool, and T-086 recorded Zoro as 403 to bots. Zoro lines are judged on internal consistency only. 3-D gates not run; saved outputs read.

## Verdict table

| Row | Verdict | One-line reason |
|---|---|---|
| T-066 | **keep READY (gaps)** | Record is complete and honest, but the "re-point citing claims" part is not done: the proof chain still cites iter3 / MN2212 vibration numbers and shows CHECKED while the record says the D-185 rule fails (M-1) |
| T-084 | **VERIFIED for A-P9 + gates, provided the row text is amended to the D-233 split** (item 2 -> T-085) | A-P9 reproduced (31.00 deg); gates and BOM read and consistent; D-185 is genuinely open and already carried by T-085, so closing T-084 loses nothing once the acceptance column stops saying "D-185 pass" |
| T-086 | **VERIFIED** | BOM rerun $1,983.69 at that commit; arithmetic reproduced; superseded by T-087 but acceptance met |
| T-087 | **VERIFIED for Part 2 (hub bars); Part 1 (R15) is a recorded no-change** | Rerun BOM $1,939.17, margin +$60.83; fit arithmetic reproduced. Two follow-ups: stale Alcobra text in generated files (M-2) and the R15 supply risk needs its own open row |
| T-014 | **keep READY (gaps)** | Backfill covers 2026-11-19..22 up to T-084; no row for T-086 / T-087 (and none for the running T-085 implementer) |
| T-032 | **keep READY (gaps)** | PIPELINE.md untouched since 2026-11-19: hashes stale, no commit pin, never followed once |
| T-081 | **keep READY (gaps)** | G-1..G-5 are fixed in text, but TP-10 is stale against the D-185 finding, the T1 / budget lines are stale after T-086 / T-087, and T-085 is rewriting the file |
| T-023 | **still open** (ledger shows NOT STARTED) | The 4 earlier Major findings are fixed; one new Major (M-2, stale vendor text after T-087) and F-9, F-10 remain |

## Independent reruns

| # | Check | Command / arithmetic | Result |
|---|---|---|---|
| V1 | Ledger audit | `python -I tools/ledger_audit.py` | 109 requirements, 87 tasks, 0 errors (7 READY) |
| V2 | BOM (T-086, T-087) | `python -I redesign/qp/A/bom_a.py` | goods 1,382.41; spend 1,592.23; reserve 346.94; **total 1,939.17; margin 60.83**; matches T-087 report and D-235 |
| V3 | Zoro swap arithmetic | (65.56+47.52 - 43.29-33.69) x 1.1025 = 39.80; ship -10.71 + 5.99 = -4.72; 39.80 + 4.72 | 44.52; 16.31 + 44.52 = 60.83 (matches) |
| V4 | T-086 arithmetic | 13.99 x 1.1025 = 15.42 (servo spare); 1,999.12 - 15.43 | 1,983.69 (matches) |
| V5 | Proof chain cost | `python -I proofs/claims_a3_program.py` (rc 0, `git status` still clean, so the committed claims JSON equals a fresh run); `proofs/out/CHAIN.md` | CL-A-COST-TOTAL 1,939 USD, margin +3 %; CL-A-COST-MARGIN30 -29.68 (info only); `params-A.json` bom_rows has T1 / T11 = Zoro 43.29 / 33.69, M01 qty 2, ship_usd read from `bom_a.py` incl. Zoro 5.99 |
| V6 | Failing claims | read `T087_data/run_all_after.txt`, `T084_data/gates/gate_proofs.txt` | same 8 FAILs (MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY); no cost failure |
| V7 | A-P9 tip-over | `python -I mechanism/out/T084_data/t084_tipover.py`; by hand atan((0.1967 - 0.00648) / (0.3375 - 0.02096)) | min **31.00 deg** (drawn CG, forward trim end), 31.00-31.31 over all bases; hand value 31.00 deg. FIN_H 0.1937 in `cad/amodel/common.py`; `sitl/cad_mass.json` fin_h_m 0.1937, basic 1.63298 kg |
| V8 | Gates for T-084 | read `T084_data/gates/gates_summary.txt`, `gate_collide_pose21.txt`, `gate_collide_linkage.txt`, `cad/out/REPORT.md` | collide PASS (583 bodies, 129 parts, 3 poses); linkage PASS (18 poses); assembly exit 0; wire exposed 0.597 strand-m; drawings exit 0; `build_a` exit 1 only on the 1,500 g mass gate (known, not relaxed). `common.py` was touched after the gates only by the comment (diff vs `common_pre_t084.py`: one line, value 0.1937 already in the gated run's CAD) |
| V9 | Wing / CAD unchanged since gates | `diff T087_data/wing_pre_t087.py cad/amodel/wing.py` (empty); `cad_mass.json` equals `T087_data/cad_mass_pre_t087.json` | the T-087 DragonPlate trial was fully restored |
| V10 | Fit to Zoro stock (worst case) | hub 59.5 x 107.8 x 49.3 in 2.00 x 2.50 in bar (50.8 - 0.61 = 50.19; 63.5 - 0.61 = 62.9; length 12 in - 1 in = 279 mm); node 100.0 x 119.6 x 20.1 in 1 x 4 in (101.6 - 0.86 = 100.74; 25.4 thick) | hub fits (0.89 mm thickness spare); node fits with 0.74 mm spare in width (tight, as noted); both lengths fit |
| V11 | T-086 / T-087 dates | Nov 22 2026 is a Sunday; the Zoro page says delivery "Tue 24 Nov" and "on or before 27 Nov" | consistent with a read on 2026-11-22 |
| V12 | T-032 hashes | `sha256sum film/shots-main.json shots-highlight.json` vs `PIPELINE.md` s2 | main `aaa8331b...` (CRLF working copy) / blob `f0387489...` vs doc `3754af1e...`; highlight `017bcd27...` vs doc `869e82e5...`: all differ |
| V13 | T-014 coverage | `docs/model-usage.md` (90 table rows: 11-18 24, 11-19 39, 11-20 12, 11-21 6, 11-22 7); grep T-085 / T-086 / T-087 | no row for T-085, T-086, T-087 |
| V14 | T-081 plan | `git show HEAD:redesign/qp/A/TEST-PLAN-O4B.md` (295 lines) grep | TP-12, TP-13, TP-14 present with numeric lines; TP-6 and C-4 WITHDRAWN; T1 purchase line still "Alcobra 1.75 x 2.5 $49.41" (l.188); adopted total still $1,981.31 (l.178); TP-10 limit "88.0 Hz (84 Hz as modelled)" (l.31) |

## Row findings

### T-066 (structures re-baseline): keep READY (gaps)
Acceptance: current-geometry run, every number traced, limits of D-202 arm crossing and hub stiffness listed. Met in `structures/T066_record.md`: s2 cites a source per input, s5 lists 8 limits (arm crossing 1-3, hub stiffness 4-6, others 7-8), the run is 291 lines, and the diff vs `iter3_run.md` is tabulated (s4). The task text also says "re-point citing claims".

- **M-1 (Major) claims not re-pointed.** The record (s6) finds that no claim cites `structures_run.md` but that the vibration inputs still read `iter3_run.md`, and leaves them to "the owner". Checked: `proofs/gen_params_a.py` l.179, 189-193 still hold `gust_n_vd` 3.01, `vib_below_hz` [63, 67, 77], `vib_above_hz` [432, 462, 524], `hover_1p_rpm_lo` 6,018 (MN2212 era), `vib_fc_ms2` 25.8...; `CHAIN.md` shows CL-A-VIB-LOW-LIMIT 83.58 Hz and CL-A-VIB-HIGH 432 Hz as CHECKED. The re-baselined run has the band at 94-321 Hz and a strong mode (cy 0.52) inside it (D-185 FAIL), so the proof chain says PASS on a claim the record fails. Required fix: re-point those five parameters to the T-066 / T-084 run (or open an explicit row, e.g. fold into T-085, and say so in the ledger), then re-run the chain.
- **m-1 (Minor)** The record is a snapshot at ac983050 (FIN_H 0.18, tip-over 29.2 deg FAIL, 1.873 kg), while the committed `structures_run.md` and `structures_a.py` are the T-084 rerun (FIN_H 0.1937, tip-over 31.1 deg PASS, M_PRED 1.8796). Both are traceable (the record says "FAILs carried to T-084"), but a reader re-running `structures_a.py` will not reproduce the record's tables. Add one line to the record pointing to the T-084 rerun.
- m-2 (Minor) Control-band GM (CL-A-VIB-GM-SHIFT 2.16) is "not re-run" (needs `sitl/fu_cage.py` with X2216 inertias). Honest, but it is an open requirement; keep a row.
- Not a defect: the 8 known failing claims (V6), the run_all abort at the time (`KeyError: 'Carbonwebshop'`) was fixed in the D-232 commit (V5 shows the chain now builds).

### T-084 (A-P9 and D-185): VERIFIED for A-P9; amend the row
Acceptance column: "A-P9 >= 30 deg with margin, D-185 pass, no limit relaxed, no ballast, BOM <= $2,000, 3-D gates PASS".

- A-P9: reproduced (V7). 31.00 deg minimum, +1.00 over 30, +0.50 over the 30.5 target. The fix (fin tubes 13.7 mm longer, mass +5.5 g basic, no ballast, no strength row changed because the pad stays at the demand z 0.1907) is drawn in the CAD, reflected in the build guide (387.4 mm tubes), drawings (FIN-001 387.4) and the proof chain (SRC-A-T084). BOM stays $1,999.12 at that commit (no purchase), now $1,939.17 after T-087. Gates read (V8) PASS apart from the known mass gate. Thin items stated by the report and confirmed: packed height 0.394 m (ratio 0.985), and a pad lengthened to X_GROUND 0.3475 would give 30.22 deg (re-check A-P9 after TP-3; see T-081 gap G-6).
- D-185: not closed, and the report says so plainly. Evidence is internally consistent (`modes_final.txt` l.39-45: spar-only model FAIL at all three corners, D-226 cell nominal FAIL at hi 96.2 Hz cx 0.81 / cy 0.93, lower-bound cell PASS). The finding that the 201-244 Hz mode is a beam-model artifact (the FE gives the wing only the 12x10 spar's in-plane EI, 37 N m2 vs 185-6,800 for the drawn cell) is plausible and the numbers are in `cell_props.txt`; I did not re-run the modal analysis. Nothing was relaxed (band 94-321 Hz and the 0.5 rule unchanged).
- Judgement on the split: D-233 does not relax D-185. It defers the pass/fail to T-085 (upgraded FE) plus the built-airframe tap test, and T-085 exists with dependency T-084 and its own acceptance ("band and >= 0.5 rule unchanged"). The execution-plan rule "unfinished parts stay as a new or reopened row" is satisfied. **T-084 can be VERIFIED only after the conductor edits the T-084 row (description item 2 and the acceptance text "D-185 pass") to say that item 2 moved to T-085 by D-233**; as written, the acceptance column still demands a pass that did not happen, and a VERIFIED row with an unmet acceptance would fail the ledger's own definition.
- m-3 (Minor) The D-185 FAIL is not visible in the proof chain (see M-1); until it is, the chain shows no open D-185 item.
- m-4 (Minor) `MASS-GATE.md` s15 and `MISSION.md` etc. have no T-084 row (basic 1,633.0 g, tallied 1.8796 kg, CG 23.13 mm, window +11.88 %, FIN_H 0.1937): grep for T-084 / 0.1937 / T-087 gives 0 hits in MASS-GATE, MISSION, REQUIREMENTS-A, SCHEDULE-A. The numbers are in `T084_report.md`, D-233 and `structures_a.py`.

### T-086 (cost trim): VERIFIED
Acceptance: total incl. reserve <= $2,000 with a larger margin, every changed price cited, no limit relaxed. Met: M01 qty 2 (servo spare dropped; reserve() still prices one servo, AM-018), $1,999.12 -> $1,983.69, margin +$0.88 -> +$16.31 (V4). The BOM line cites the 2026-11-15 RMRC page and the T-086 reason. The report is candid that +$50 was not reached with levers 1-3 and that Zoro prices were snippets (not used). Its design-risk statement (a servo failure before first flight grounds the aircraft) is on the record. Superseded in value by T-087; the acceptance does not require the final margin. Note: the model-usage log has no T-086 row (see T-014).

### T-087 (rib tube and hub bars): VERIFIED for Part 2; open items
Acceptance: "rib rows RF >= 1 at max(DAF,1.5), D-185 not worse, 3-D gates PASS, BOM <= $2,000 with prices cited".

- BOM rerun $1,939.17, margin +$60.83 (V2, V3). Lines T1 (Zoro 61F2X2.5-12, $43.29) and T11 (Zoro 61F1X4-12, $33.69) carry the URL, the date (2026-11-22), the temper (6061 T6511), the extrusion tolerances and "no certificate". Shipping $5.99 is a guest-cart figure (free over $50 after sign-in), labelled EST, `SHIP["Zoro"] = 5.99`. The fit arithmetic is reproduced (V10): the hub fits with 0.89 mm spare in thickness, the node with 0.74 mm spare in width (tight; machine from the bar faces as supplied). Allowable: Zoro states typical yield 40 ksi; B221 T6511 minimum is about the 240 MPa used (EST, secondary source), so no FEA rerun is needed; no certificate means TP-4 / TP-5 coupons carry the risk.
- R15 (rib tube): no replacement passes (DragonPlate 25.4 x 22.225 strengthens the rib 1.14 -> 1.66 but adds 29 g and moves the lower-bound hi-corner mode to 96.6 Hz, i.e. D-185 worse; rule honoured, nothing applied). Nothing changed, so rib rows and gates are unchanged; no 3-D gates were needed (V9 shows the trial was restored byte for byte). The brief's "firm Alcobra shipping quote" is moot (Alcobra removed).
- **M-2 (Major, also T-023) generated files not refreshed after T-087.** `cad/out/parts-a.csv` l.29, 37, 43, 64 and `BUILD-GUIDE-A.md` l.215, 662, 664, 1426, 1432, 1438 still say "T1 Alcobra" / "T11 Alcobra" and cite `alcobrametals.com`; `parts-a.csv` CGE-001 and `BUILD-GUIDE-A.md` l.221 still say the T1 bar is "1.75 x 2.5 in ... must change to 2.00 x 2.50 in before ordering" and "BOM T1 not yet changed (T-023 F-2)", all false after T-087. The build guide is the student-facing document and the first thing a buyer reads. Required fix: edit the generator text (`cad/parts_links_a.py` MAP, `a_build_steps.py` T1 need line), rerun `parts_links_a.py` and `make_build_guide_a.py` (both fast), commit.
- m-5 (Minor) The T11 note and the FIN-003 blank plan: if the bar arrives 1 in short, the FIN-003 blanks consume the spare CGE-006 blank, leaving no spare node. The BOM says so; the build step text was not updated (report says "build step text was not changed").
- **Recommendation:** close Part 2 as VERIFIED after M-2, and open a new row for the R15 supply risk (Carbonwebshop EU, stock not stated, $25 ship EST, duties unknown; the report calls it "the largest remaining BOM uncertainty"), per the partial-completion rule. Without that row the ledger would hide an open risk.

### T-014 (model-usage log): keep READY (gaps)
Acceptance "one row per delegation". The backfill (`bbabc7fb`) closed the earlier FAIL: 35+ rows for 2026-11-19..22, "running" cells removed (grep finds none), every task from T-066 to T-084 has a row. Remaining gaps:

- m-6 (Minor, becomes Major if those were delegated) No row for T-086, T-087 (ledger owner O; reports say "conductor re-ran", so a delegate did the work), nor for the independent reviews run this round and the T-085 implementer now running. Either add the rows or write one line in the log stating the task was done by the conductor.
- m-7 (Minor) Two rows have usage "—" (T-066, T-023/T-081 fixes); acceptable if the notifications recorded none, say so.
- Structural note: the row can only stay true while the log is kept up to date; consider making `tools/ledger_audit.py` warn when a READY/VERIFIED row owned by S/O has no matching model-usage row (suggested in the previous review, not done).

### T-032 (video pipeline doc): keep READY (gaps)
`git log` for `docs/video/PIPELINE.md`: last change 2026-11-19. None of the previous review's items (F-5) is fixed: (1) s2 hashes and the 116.0 s / 6,960 frames are stale since T-030-N (V12; s12 mentions the 119.9 s / 7,194 frames change but gives no new hashes); (2) the hashes are of CRLF working copies (the git blob hash differs); (3) no commit pin; (4) only a dry check was run, "follow doc once" never done. Required: replace the s2 hashes with git blob hashes plus a commit to check out (or state the CRLF basis), state that the films show the 2026-11-18 configuration (115 parts, MN2212; the aircraft now has 129 parts, X2216), run one scene end to end (e.g. `--scenes S3`, about 12 min) following only the doc and record frame counts.

### T-081 (test and purchase plan): keep READY (gaps)
Fixed since the previous re-check (read at HEAD): G-1 TP-12 (n = 5 proposal, rig, pass >= 92 MPa EST, fail keeps 25x23); G-2 TP-13 (pass 2.21 / 1.73 MPa); G-3 TP-14 (48.5 MPa demand, allowable "—" stated, test sets it); G-4 adopted-total paragraph added and s0 row 4 / s4.1 marked SUPERSEDED; G-5 withdrawn / MN2212 items tagged (TP-1 spare, TP-6, TP-7 C-4, T2 line). The labelling is honest ("—" where the source gives no number; n = 5 and the rig are marked proposals). Remaining gaps:

- **G-6 (Major)** TP-10 (A-P10 tap test, l.31) still reads "hi-corner mode vs the re-based limit 88.0 Hz (84 Hz as modelled)". D-185 is now judged on the 94-321 Hz band with the coupling >= 0.5 rule, and T-084 shows the cage-bounce mode at 96.2 Hz at hi (cell nominal). The test as written cannot decide D-185. T-085's acceptance already says the T-A-TAP procedure and pass rule go into this file, and a T-085 implementer is editing it now, so this gap closes only when that is committed and reviewed.
- G-7 (Minor) A-P9: TP-3 may lengthen the pad; D-233 says A-P9 must then be re-checked (30.22 deg at X_GROUND 0.3475, below the 30.5 target). The plan does not carry that check (grep: A-P9 appears only in the l.6 limits line).
- G-8 (Minor) Budget lines are stale after T-086 / T-087: l.178 "adopted total $1,981.31, margin +$18.69", "Open: the hub needs a 2.00 x 2.50 in bar... margin may fall by about $16", and the T1 purchase line l.188 (Alcobra 1.75 x 2.5, $49.41). Truth now: $1,939.17, margin +$60.83, T1 Zoro 2.00 x 2.50 $43.29, T11 Zoro $33.69. The total is still under $2,000 so the acceptance is not endangered, but the file is the purchase list.
- G-9 (Minor) TP-12..14 ids are not in `docs/requirements.md` or the ledger (fix note says so).
- Close after G-6..G-8 are fixed in the T-085 commit and rechecked.

## T-023 re-review (CAD consistency)

Method: cross-file diffs of `parts-a.csv`, `BOM-A.csv`, `params-A.json`, `BUILD-GUIDE-A.md`, `DRAWINGS-A.md`, `cad_mass.json`, `printed_mass.json`, `wire_inventory.json`, `amodel/common.py` against HEAD and the earlier review (`2026-11-22-T023-cad-consistency.md`) and `T023_fixes.md`. No 3-D gate was rerun.

### Earlier findings: status
| ID | Status | Evidence |
|---|---|---|
| F-1 (Major) parts-a vendors | **Fixed** for P01 / W01 / V03 / R10 / R15 / T2: grep for T-Motor / tmotor: 0 hits in `parts-a.csv` and `BUILD-GUIDE-A.md` | but see N-1 (T-087 re-staled T1 / T11) |
| F-2 (Major) hub stock | **Fixed in substance**: hub is machined 6061, BOM T1 is now 2.00 x 2.50 in (T-087), fit reproduced (V10) | text still stale (N-1) |
| F-3 (Major) params-A.json | **Fixed**: `cost.bom_rows` equals `BOM-A.csv` (53 rows incl. Zoro T1 / T11); `ship_usd` read from `bom_a.py` (D-232); `pack_g` note now says "was Tattu 2300 (stale)" | one leftover: `ship_usd` still lists unused SparkFun / TMotor groups at 0 / 8 (no cost effect) |
| F-4 `MASS-GATE.md` s15 last line | Fixed (T-023 fix) | but now behind T-084 / T-087 (N-3) |
| F-5 (Major) E-HRN-13 | **Fixed**: `T083b_report.md` l.120 says 0.253 strand-m; build guide l.2152 carries the 2 x 50 mm lead extension (not drawn; stated) | total 0.597 strand-m unchanged (V8) |
| F-6, F-7, F-8 | Fixed (WNG-011 / 012, GER-002 mappings; build guide motor text) | |
| **F-9 (Minor)** WNG-009-L/R printed mass | **Still open**: `printed_mass.json` has 34 entries, no WNG-009; `DRAWINGS-A.md` l.95-96 lists WNG-009-L/R 2.0 g PETG + silicone; AVN-010 still shows "14: CHECK (a body is not attached)" (l.64). Required: one sentence in `printed_mass.json` or `MASS-GATE.md` saying why WNG-009 sits outside the T-067 basis, and a note for the drawing tool that AVN-010 is multi-body by design |
| **F-10 (Minor)** stamps | Partly: `DRAWINGS-A.md` header now reads "commit de638ea8" (regenerated 03:38), but de638ea8 is the commit BEFORE the T-084 geometry change (T-084 landed in f7b385f6), so the stamp names a commit that does not contain the drawn FIN_H. Regenerate after committing, or stamp "working tree on de638ea8". **CLAUDE.md l.28 still says "predicted 1.64 kg"** (project instruction file; reviewer cannot edit): the current predicted mass is 1.8796 kg tallied (D-233; 1.8656-1.873 kg earlier), against the 1.64 kg of the O4b go/no-go; the line needs the conductor's decision (replace with the current number plus "mass gate 1.50 kg FAIL carried, weight over accepted in the initial design"). The `electrical.py` l.602 comment is fixed |

### New findings since T-084 / T-087
- **N-1 = M-2 (Major):** `parts-a.csv` and `BUILD-GUIDE-A.md` still name Alcobra for T1 / T11 and carry the "1.75 x 2.5 ... must change" caveat that T-087 resolved. Fix and regenerate as in M-2.
- N-2 (Minor, FIN_H): consistent everywhere checked: `common.py` 0.1937; `cad_mass.json` fin_h_m 0.1937; `DRAWINGS-A.md` FIN-001 387.4 mm and FIN-004 110 x 3 x 387.4; `BUILD-GUIDE-A.md` l.67, 1372, 1475, 1479 (387.4 mm, 29.2 g each); `structures_a.py` H_FIN = m.FIN_H; proofs SRC-A-T084. No stale 0.180 found in the A markdown outside historical reports. `cad/out/REPORT.md` and the collide outputs predate nothing: they are the T-084 gate outputs (V8).
- N-3 (Minor): `MASS-GATE.md` s15 table still stops at "T-083b as drawn 1,627.5 g, 1.8656 kg" and its last line cites $1,981.31 / +$18.69; no T-084 row (1,633.0 g basic, 1.8796 kg tallied, CG 23.13) and no T-087 BOM. `MISSION.md`, `REQUIREMENTS-A.md`, `SCHEDULE-A.md` do not mention T-084 or T-087 either.
- N-4 (Minor): the packed-height margin is thin (0.394 m, ratio 0.985); any further fin or foot growth breaks CL-A-BOX-FIT. Not an inconsistency; note for the owner.
- Agreed (no inconsistency): mass 1.63298 kg basic and CG 21.95 mm between `cad_mass.json`, `T084_report.md`, `structures_a.py`; BOM total 1,939.17 between `bom_a.py`, `params-A.json`, `CHAIN.md`; wire inventory 0.597 strand-m; 129 parts placed; hub / node / FIN-003 blanks fit the stock.

### T-023 verdict
Not ready to close. Required before a final pass: (1) N-1 regeneration (one commit); (2) F-9 note; (3) DRAWINGS stamp regenerated after committing T-084 / T-087 geometry; (4) the conductor's decision on the CLAUDE.md "1.64 kg" line; (5) after T-085 lands, re-diff once more because it edits `fe_a.py`, `structures_a.py` and the test plan. The ledger row still reads NOT STARTED although a review and fixes exist; set it to IN PROGRESS or READY FOR REVIEW as appropriate (conductor).

## Findings summary

| ID | Severity | Row | Finding | Required fix |
|---|---|---|---|---|
| M-1 | Major | T-066 (and T-085) | Proof chain still cites iter3 / MN2212 vibration inputs and shows CHECKED while D-185 is open | Re-point five params, rerun chain, or open an explicit row |
| M-2 / N-1 | Major | T-087, T-023 | parts-a.csv and BUILD-GUIDE-A.md still say T1 / T11 Alcobra and carry the pre-T-087 hub-stock caveat | Edit generator text, regenerate, commit |
| G-6 | Major | T-081 | TP-10 tap-test limit (88 Hz) is stale against the 94-321 Hz band and the 96.2 Hz finding | T-085 commit with the T-A-TAP method, then re-review |
| A-1 | Major (process) | T-084 | Acceptance column still says "D-185 pass" | Amend the row text to the D-233 split, then verify |
| R-1 | Major (process) | T-087 | R15 supply risk (EU, stock unknown, $25 EST) has no ledger row | Open a new row |
| m-1, m-2, m-3, m-4 | Minor | T-066 / T-084 | record vs HEAD run divergence; GM not re-run; D-185 not visible in chain; MASS-GATE and A-docs lack T-084 / T-087 | one-line pointers; add rows |
| m-5 | Minor | T-087 | FIN-003 blanks eat the spare node blank if bar is short | Update the build step text |
| m-6, m-7 | Minor | T-014 | No rows for T-086, T-087 (delegated?); two usage "—" | Add rows or note conductor-run |
| T-032 | Minor (open) | T-032 | Hashes stale, CRLF, no pin, never followed | See T-032 section |
| G-7, G-8, G-9 | Minor | T-081 | A-P9 re-check after pad change; stale budget and T1 lines; TP-12..14 ids not registered | See T-081 section |
| F-9, F-10 | Minor | T-023 | WNG-009 / AVN-010 notes; DRAWINGS stamp names the pre-change commit; CLAUDE.md 1.64 kg | See T-023 section |

No Critical finding.

## Not checked
- Web pages (Zoro, Alcobra, RMRC, DragonPlate) not re-fetched; Zoro prices, stock and the $5.99 guest shipping are as recorded by T-087.
- D-185 modal analyses, `fe_a.py`, `structures_a.py` not re-run (3 minutes for structures_a; the modal tables were read from `modes_final.txt` and cross-checked against the report).
- 3-D gates (collide, assembly) not run; saved outputs read. T-085 working files not reviewed.
- `BUILD-GUIDE-A.md` grep-checked for stale names and FIN_H values, not read in full.
