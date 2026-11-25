# Review round 6A, 2026-11-23 (HEAD 3bf00f72): T-016, T-017, T-026, T-074, T-077

Reviewer: independent (not the author of any of the five rows). Read-only except this file. Reopen reasons: `docs/audits/2026-11-23-milestone-audit.md` s3.2 (T-016, T-017, T-026, T-074) and s3.3 / F-9 / F-13 (T-077). No row is marked VERIFIED COMPLETE here; the conductor decides.

| Task | Verdict |
|---|---|
| T-016 | PASS WITH FIXES |
| T-017 | PASS WITH FIXES |
| T-026 | PASS (one status fix) |
| T-074 | PASS WITH FIXES |
| T-077 | PASS WITH FIXES (acceptance wording) |

Labels: rerun = I executed it; recomputed = arithmetic from the cited files; read = file inspection only.

## T-016 capability audit (docs/capability-audit.md): PASS WITH FIXES

Spot-check of 3 rows (`docs/capability-audit.md` dated 2026-11-18):

| # | Audit row | What I did | Result |
|---|---|---|---|
| 1 | s1 Configuration: `AM/common.py:32-53` constants (C, B, ELEV_FRAC EST :33, XH :34, elevon y :35, ELEV_STOP :36, ELEV_POSE :37) | read `redesign/qp/A/cad/amodel/common.py:32-37` | MATCH, every line number and value (0.25 EST, 0.04-0.35, 21 deg). |
| 2 | s2 Kinematics (2-D geometry): `A/cad/stop_check.py`, "0.51 mm minimum at +21 deg, PASS against 0.5 mm" | rerun `python -I stop_check.py` (12 s) | MATCH: min clearance 0.51 mm upper / 0.52 mm lower at +-21 deg, PASS. The script rewrote `out/STOP_CHECK.md`; I restored it with `git checkout` (tree clean). |
| 3 | s2 Hand calc: `A/MASS-GATE.md:9` "Physics now from prop_a.py" | read line 9 | MATCH (same text, line 9). |

Also checked the ledger's own claim "electrical.py:530-560 values match s5": the s5 table cites `electrical.py:540` ARM_R, `:538`, `:944-978`; today `ARM_R` is at `electrical.py:645`, `SV_XS` :644, `HORN_R` :655 (value 8.5 mm / 9.155 mm match s5, so the facts hold, only the line numbers moved).

Findings:
- F-1 (Low) `docs/capability-audit.md` s2.1 row 1 cites `CLAUDE.md:53`; the "3-D physics simulation" text is now `CLAUDE.md:60`. Same for the T-017 evidence ("CLAUDE.md:53", "CLAUDE.md:74"; the added line is now :81). Fix: add "(as of 2026-11-18; line numbers drift)" under the audit date, or update to :60 / :81.
- F-2 (Low) s5 and s1 line citations into `electrical.py` (:538-:978) are stale by about 100 lines (file grew). Fix: same note as F-1; facts are unchanged.
- F-3 (Low) `redesign/qp/A/cad/out/STOP_CHECK.md` (committed) is out of date against the code: committed cap heights/ranges (4.05 / 4.22 mm, 137-180, 4 caps 15.2 g) differ from the script's current output (3.82 / 4.00 mm, 138-180, 14.9 g). The pass/fail result is the same. Fix: regenerate and commit `out/STOP_CHECK.md` in the next CAD commit (I did not, read-only).
- F-4 (Low) Counts in s1/s2.1 (113 parts, 66 steps, 1.02 strand-m) are 11-18 values; current is 129 parts, 66 steps, 0.597 strand-m (`T092_data/gates/gates_summary.txt`, T092_report s2). Fix: one line "figures as of 2026-11-18; see T092_report for current".

Required to close: file this note, append its path to the T-016 Evidence cell, apply F-1/F-4 notes. The audit is otherwise accurate; spot-check 3 of 3 pass.

## T-017 relabelling (docs/audits/2026-11-18-physics-labels.md): PASS WITH FIXES

Rerun (tracked files): `git ls-files 'docs/*.md' 'redesign/*.md' README.md CLAUDE.md | xargs grep -niE "physics[ -]+(check|simulation|gate|pass|sim)"` excluding MASTER_PROJECT_SPEC.md / spec-amendments.md: 78 lines in 24 files. Classified:

- Accounted for / accurate: `CLAUDE.md:60` (user's constraint text), `README.md:22` and `redesign/README.md:12` ("not physics simulations", negation), `qp/A/REQUIREMENTS-A.md:13`, `REQUIREMENTS-QP.md:17` (quote plus what is computed), `CLAUDE.md:29`, `T092_report.md:47`, `docs/requirements.md:44` R-GEN-08 ("physics checks govern" = stability, T/W, window: real calculations), `config-study/cards/K06/REVIEW.md:20` ("the physics checks out", unrelated idiom), `redesign/RESUME.md:18`, generated `proofs/out/*`, `T066_data/*`, `T087_data/*`, `T091_data/*` copies (SRC-A-USER citation of the user's constraint text), `docs/capability-audit.md` and `docs/audits/2026-11-18-physics-labels.md` (list the old wording as the finding), `docs/task-ledger.md:27`, `docs/requirements.md:79`, `docs/audits/2026-11-23-milestone-audit.md:50`.
- K09-L historical records (left by rule in the T-017 evidence): `redesign/review/CLOSURE-ROUND-2026-11-14/RULES.md:11`, `redesign/review/CDR-2026-11-13/RESUME.md:16`, `.../fixes/INTEGRATOR.md:8`, `redesign/params/CHANGE-LOG.md:822` (D-136 "build-film physics check"), `:826` ("build-sequence physics check"), `:538` ("can go into a rigid-body physics simulator", states purpose).
- Not covered by the T-017 evidence, still mislabelled: **`docs/audits/2026-11-19-T022-decisions.md:244`** "The build-sequence physics check (`assembly_check.py` ...)" names the swept insertion gate a physics check.

Findings:
- F-5 (Medium) `docs/audits/2026-11-19-T022-decisions.md:244`: unlabelled "physics check" for an interference/swept check, written after T-017 (11-18). Fix: change to "build-sequence swept insertion check". (Audit files are dated records, so append a correction line rather than rewriting if the team treats them as append-only.)
- F-6 (Low) The T-017 final grep (evidence file, "Final grep") covered README, CLAUDE, redesign/site, qp, showcase, collision, blender, RESUME, README only; it excluded `docs/` and `redesign/params/`. Acceptance "grep finds no mislabel" is therefore proven for those paths only. Fix: append to the T-017 Evidence the full-repo command above and the two residual classes (K09-L records; F-5 after fix). Also `CHANGE-LOG.md:822/826` could carry a one-line "(K09-L, interference check)" note if the CHANGE-LOG rules allow it; otherwise list them as historical.
- F-7 (Info) The site pages `redesign/site/app.html` / `index.html` now contain no "physics (check|simulation|gate|pass)" (grep of html: no hit), consistent with the evidence.

Required to close: fix F-5, append F-6 text and this path to the T-017 Evidence.

## T-026 video pipeline audit (docs/video/PIPELINE-AUDIT.md): PASS

Spec 7.1 inspect list (`docs/MASTER_PROJECT_SPEC.md:476-491`) against the audit sections (read):

| 7.1 item | Where covered |
|---|---|
| Existing video files | s2 (table of 12 concept A files, resolution, fps, frames, size; K09-L files in the note after the table, line 31) |
| Rendering software | s1 tool paths, s3 (Blender 4.5.14, EEVEE-Next, samples, hardware) |
| Camera paths | s5 |
| Lighting | s6 |
| Materials | s6 |
| CAD imports | s4 (live `bb.build` of `qp/A/cad/model`, GLB exporter, FEA GLBs) |
| Animation scripts | s7 |
| Scene construction | s8 |
| Technical overlays | s9 |
| Export settings | s10 |
| Performance bottlenecks | s11 |
| "Identify opportunities for meaningful improvement", "improve rather than rebuild" | s12 (coverage vs the six scenes of 7.3), s13 (9 ranked improvements, all as extensions of existing scripts), s14 cost, s15 not verified |

All 11 listed items and the improvement clause are covered. Spot facts: `render_build_a.py:66` BLENDER_DEFAULT (verified, the audit's line number is correct), the Blender exe exists, 12 concept A mp4 files exist. Unknowns are honestly listed in s15.

Findings:
- F-8 (Low, status) `docs/requirements.md:102` R-VID-01 still reads "IN PROGRESS" with verification "O read". Fix: append "O read done 2026-11-23, `docs/audits/2026-11-23-review-round-6a.md`, all 11 items covered" and let the conductor set the status.
- F-9 (Info) The audit is dated 2026-11-18; later tasks (T-027 resolution / fps flags in `render_build_a.py`, line 69-70 constants now parametrised) have done ranked item 1. Not an error; a staleness note in the audit header would help.

## T-074 O4b $0 checks (T074_checks12.md, T074_check3.md): PASS WITH FIXES

Recomputed from the files:

Check 1 (FAIL, ledger FAIL) in `T074_checks12.md`:
- Scratch G7: V03 $95.98 -> $141.44 adds $45.46; x1.1025 = $50.12 spend (recomputed). Total 1,779.47 + 50.12 = 1,829.59 (matches). +30 % margin 100.05 - 50.12 = 49.93 (matches). Total over the $1,800 limit by $29.59; margin short by $50.07. So "breaks G7 by ~$50" in the ledger is the margin shortfall; the total shortfall is $29.59 (both in the file). Result FAIL confirmed; F405 no Lua stands on three cited pages (read, not refetched; web pages not re-read by me).

Check 2 (ledger "PASS-conditional"): the GNB 2800 mAh 4S is 267 g, 107 x 34 x 37 mm (<= 275 g, >= 2,350 mAh) at EUR 41.29 in stock at Rotorama (EU only); US stock not found; KiwiQuads out of stock. Ledger text "37 vs 29 mm tray" is loose: 29 mm is the old Tattu pack height, not a tray dimension (the file says tray height limit is "—" in the CAD). Verdict in the file is "PASS, conditional" and agrees with the ledger.

Check 3 (PASS) in `T074_check3.md`:
- Window: (1.566 / 1.33 = 1.177 -> +-8.15 %; 1.510 / 1.33 = 1.135 -> +-6.35 %) recomputed, matches "+-6.35..8.1 %".
- SITL entry T/W 1.25-1.60 pass (1.20 marginal: 12.8 m/s < 12.94, alpha 32 deg), matches the ledger "1.25-1.60".
- C6 min RF 1.24 at rigid-body demand (saddle body shear), ledger "C6 1.24" matches.
- A-P9 30.35 / 30.51 / 30.87 deg across the CG range, matches "30.35-30.87".

Findings:
- F-10 (Low) Ledger T-074 Evidence omits the caveats the check files carry: check 3's x1.5 dynamic C6 factor is 0.83 (< 1, not a criterion, still open); T/W fresh drops under A-P2 2.0 below derate 0.88; `Q_M_BAT_CURR_MAX` must be raised to >= 45 A or the window loses 2 points; the T-A-C3-PITCHOVER claim is "planned", so the SITL sweep stands in for C3. Fix: append a one-line "conditions" clause to the Evidence (these were later carried by D-218..D-233; cite where).
- F-11 (Low) "(2) in-stock 4S" acceptance: the file's own evidence is EU-only stock, so "PASS-conditional" is the honest label; the ledger should say "US in-stock not confirmed" (it says EU-only; fine) and note that the pack finally used is the RDQ 2800 mAh (T-077 part 1), not the GNB. Fix: one clause.
- F-12 (Info) Both check files are dated 2026-11-19 and predate the later motor swap (AM-018, X2216 880KV); they remain valid as the AM-006 record, and the ledger row says the decision was O6. No change needed beyond F-10/F-11.

Required to close: append this review path to T-074 Evidence plus F-10/F-11 clauses.

## T-077 O4b Phase 2 CAD: PASS WITH FIXES (acceptance wording; not a numbers problem)

Gate evidence read from `redesign/qp/A/mechanism/out/T092_data/gates/` (HEAD files, T-092 run; I did not rerun collide / assembly):

| Gate | File | Result |
|---|---|---|
| collide pose 21 (+ 2 elevon limits) | `gate_collide_pose21.txt` | 0 pairs > 0.05 mm, 0 wire ends, 0 folds, 585 bodies in 129 parts: PASS |
| collide 18 linkage poses | `gate_collide_linkage.txt` | 0 / 0 / 0, 18 poses: PASS |
| a_assembly | `gate_assembly.txt` | 66 steps, 129 of 129 parts placed, 0 blocked, none missing: PASS |
| wire_inventory, cad_mass, mission_gate --o4b, drawings, build_guide, parts_links | `gates_summary.txt` | exit 0 |
| build_a | `gate_build_a.txt` | exit 1: ONE error, `graph:mass TOTAL aircraft 1641 g > limit 1500 g`, 0 warnings |
| proofs/run_all | `gate_proofs.txt` | exit 1: 12 claim FAILs (MASS-GATE-ROOM, MASS-PRED, CUTS-REQUIRED, VIB-IN-BAND, VIB-FC, VIB-GM, VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY) plus `A-P13 CL-A-FLUTTER-ELEVON-NOM is UNVERIFIED` (a pillar line, not a claim FAIL) |
| exemptions | grep "exempt" all gate files | 0 matches: no exemptions |

Mass roll-up from CAD: `gate_cad_mass.txt` cg_x 22.049 mm, cg_y -3.323 mm, cg_z 6.560 mm; `mass_basic_kg` 1.64098; `T092_report.md` s2 table (1,641.0 g CAD, CG 22.05, SM 7.61 %, predicted 1.881 kg = 1.64098 x 1.1174 + 0.048) consistent with the gate files. Acceptance "mass roll-up from CAD" is met.

Evidence dedupe check (`git show 9fd6af83:docs/task-ledger.md` row, 16,801 bytes, vs HEAD row, 3,522 bytes): split both on ";" and tested every old segment for presence in the new cell: the only segment absent is the old closing status text "O4b infeasible as drawn, configuration reopened per AM-016 | BLOCKED |" (replaced by the 11-23 supersession note and READY FOR REVIEW, as the milestone audit asked). All numeric facts of parts 1-8 survive once. The new "2026-11-23" clause cites the correct superseding sources. No fact lost.

Findings:
- F-13 (Medium) Acceptance says "gates PASS no exemptions", yet `build_a` exits 1 and `run_all` exits 1 (12 STRICT FAILs). The row's Evidence says "current gates PASS (T092_report s2, T084_report s7: collide, a_assembly 129/129, wire 0.597 strand-m, drawings 49/49)", which is true only of the 3-D / wire / drawing gates. The mass-gate miss is permitted by AM-011 (R-GEN-08) and the 12 FAILs are carried and explained in T092_report s2 and D-237; they are not exemptions of the 3-D gates, but the row should say so. Fix: replace "current gates PASS" with "3-D gates (collide pose 21, 18 linkage poses, a_assembly 129/129) PASS, no exemptions; build_a fails only the 1.5 kg mass gate (allowed by AM-011); run_all 12 STRICT FAILs carried (T092_report s2, D-237), listed in `gate_proofs.txt`".
- F-14 (Low) `gate_proofs.txt` also carries `A-P13 CL-A-FLUTTER-ELEVON-NOM is UNVERIFIED` as an error line that is not among the "12 expected FAILs" of T092_report s2. Fix: add one clause naming it as a pre-existing UNVERIFIED state, or list it with the 12.
- F-15 (Low) The "window +11.88 %, T/W 2.632 / 2.111" quoted in the milestone audit s3.3 are T-084 tallied figures (`T084_report.md:24,150`); the T-092 gate output (`gate_mission_gate.txt:44`) reports CAD 1,641.0 g, CG 22.05, SM 7.61 % and does not recompute the window. Fix: cite T-084 for the window, or rerun `mission_gate_a.py --o4b --sched` at 1,648 g in the next pass (not done here: the shipped gate file has no window line at the T-092 mass).
- F-16 (Info) Row length is now 3.5 kB (was 16.8 kB at 9fd6af83, about 30 kB per the milestone audit); reviewable. The Status column reads READY FOR REVIEW; the F-9 phase-table fix is outside this round.

Required to close: apply F-13 wording (and F-14), append this path to the T-077 Evidence.

## Commands run

- `python -I stop_check.py` in `redesign/qp/A/cad` (exit 0, 12 s), then `git checkout -- redesign/qp/A/cad/out/STOP_CHECK.md`; `git status --short` clean afterwards.
- `git ls-files 'docs/*.md' 'redesign/*.md' README.md CLAUDE.md | xargs grep -niE "physics[ -]+(check|simulation|gate|pass|sim)"` (78 hits), plus an html / py grep.
- Python set-difference of old vs new T-077 row segments (`git show 9fd6af83:docs/task-ledger.md`).
- Reads: ledger rows, milestone audit s3.2 / s3.3, capability-audit, physics-labels, PIPELINE-AUDIT, spec s7.1 (lines 476-491), T074 files, T092 gate files and report.

Not done: web pages cited by T074 were not refetched; collide / assembly not rerun (as instructed); K09-L CHANGE-LOG entries not edited.
