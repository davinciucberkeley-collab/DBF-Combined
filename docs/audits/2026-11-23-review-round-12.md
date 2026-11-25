# Independent review, round 12 (2026-11-23)

Reviewer: independent eng-reviewer (opus). Branch `redesign/v1`, uncommitted working tree on top of `c6d027b6`.
Scope: T-099 re-check after fix pass A and F-2b, T-096 frame review after the F-5 rework, the T-076 / T-083 split into T-100,
and the T-050 close. I wrote only this file. Scratch outputs (frames, GLB gate re-run, web copies) are in the session
scratchpad and are not evidence by themselves. No ledger status was changed; nothing is marked VERIFIED COMPLETE here.

## Verdicts

| Task | Verdict | Key finding |
|---|---|---|
| T-099 | **SEND BACK** | F-2 is closed (GLB gate 0 / 0 / 0, independently re-run; published GLB is byte-identical to the gated export). F-6 (go/no-go date) is not carried as an open user decision anywhere a user reads (R12-1). README still says the GLB gate is open with 40 pairs (R12-2). The GLB gate's wire-entry rule changes a user-owned gate and is not disclosed in CLAUDE.md or the README (R12-3). C-6 caption still wrong (R12-4). |
| T-096 | **VERIFIED** (reviewer PASS, LOW notes) | All F-5 defects fixed; my own frames match T097_Z5 `case.fwd.csv` / `sum.json`, T098_results.json and the CHANGE-LOG; full decode exit 0 on both files. D-247 is not in the films and does not need to be. |
| T-076 | **VERIFIED** (reviewer PASS, notes) | Acceptance met for the non-test items; the test-gated items are in T-100. Notes R12-6 and R12-7. |
| T-083 | **VERIFIED** (reviewer PASS, notes) | Model, params, CAD, BOM ($1,939.17 re-run) and gates met; A-P6 and the landing rows are in T-100. T-100 is missing the R-GEN-08 parent (R12-8). |
| T-050 | **VERIFIED** (reviewer PASS, LOW notes) | Every M/S D-entry after 2026-11-18 now carries a trade table and a benchmark line or an explicit "none found". I checked two sources: Lavalette ECCM18 matches; Engineering ToolBox matches apart from one wording slip (R12-11). |

The ledger owner decides VERIFIED COMPLETE. For T-076 / T-083 / T-096 / T-050 this review is the independent check the
ledger asks for. Close the T-100 findings (R12-5, R12-8) in the same edit as the T-076 / T-083 status change.

## 1. What I re-ran (repo root unless stated)

| Command | Exit | Result | Agrees with the record? |
|---|---|---|---|
| `python -I tools/ledger_audit.py` | 0 | 113 requirements, 100 tasks: 80 VERIFIED COMPLETE, 6 BLOCKED, 5 DEFERRED, 4 NOT STARTED, 4 READY FOR REVIEW, 1 IN PROGRESS; 0 errors | yes |
| `python -I run_all.py` (in `redesign/qp/A/proofs`) | 1 (strict) | 569 nodes; **14 distinct STRICT FAIL claims**: MASS-PRED, MASS-GATE-ROOM, CUTS-REQUIRED, STALL-PRED 17.74 m/s, PITCH-USE 0.79, VIB-IN-BAND, VIB-FC, VIB-GM, VIB-GM-SHIFT, HORN-RIB-FOAM-HOLD, HORN-RIB-FOAM-STALL, ELEVON-TORSION-FOAM, HORN-BEARING-STALL, LINKAGE-FREEPLAY; plus UNVERIFIED strict lines CL-A-STALL (A-P6) and CL-A-FLUTTER-ELEVON-NOM (A-P13); UNVERIFIED 228, PROPOSED 20, CHECKED 321, VERIFIED 0. `git status` of `proofs/` was the same before and after. | yes (fix pass A) |
| `python -I redesign/qp/A/bom_a.py` | 0 | total $1,939.17, margin $60.83; +30 % $2,029.68 (information only); G7 FAIL | yes |
| `python -I redesign/qp/A/cad/collide_glb_a.py --out <scratch>/glbgate` on the published `redesign/site/assets/concept-a.glb` | 0 | PASS: job 129 parts, 14 wires; 0 part pairs > 0.05 mm (0 artefact, 0 real), 0 unseated ends, 0 bad entries; 129 part bodies, 44 strands, 559 s. Tracked `cad/out/*` files untouched (output in the scratchpad) | yes (`glb_gate_f2b.txt`) |
| `sha256sum` scratch `C:/Users/dillo/AppData/Local/Temp/g/glb3/assembly.glb` vs `redesign/site/assets/concept-a.glb` | 0 | both `f2129c45...2dfc8`, 11,812,400 bytes | yes: the published GLB is the gated F-2b export |
| `ffprobe -count_frames` and `ffmpeg -v error -i F -map 0:v:0 -f null -` on both films | 0 / 0 | main 1920x1080 60/1 7,194 frames; highlight 1,452 frames; full decode exit 0, no output | yes |
| `sha256sum` films | 0 | main `d8426164...`, highlight `2bdda554...` | yes (`rework/decode-rework.log`) |
| 12 frame grabs (`ffmpeg -ss`): main t18.2, 19.6, 75, 88, 96, 101, 118.5; highlight t8, 12, 16.5, 18.5, 23 | 0 | read, s3 | |
| `curl` of the two T-050 sources | 0 | s5 | |

Not re-run: collide_a (1,310 s) and a_assembly (about 54 min). Their F-2b logs agree with each other and with the tracked
outputs: `cad/out/REPORT.md` / `report.json` mtime 21:12:15 matches `collide_a_f2b.txt` (21:12, 0 pairs at 3 poses, 0 open
ends, 0 folds, 1,310 s). `ASSEMBLY.md` mtime 22:06 matches `a_assembly_f2b.txt` (66 steps, 129 / 129, 0 blocked). Both
post-date the CAD edits (`wing.py` 20:47, `electrical.py` 20:50) and the export (finished 20:53). The 18 linkage poses were
not re-run after D-247. D-247 only removes material (cutters), so it cannot create a new overlap; that is acceptable.

## 2. T-099 re-check

### 2.1 GLB gate (F-2, F-2b, D-247)
- **CAD diff read** (`git diff redesign/qp/A/cad/amodel/`), three changes:
  - `wing.py:1326`: the CGE-001 lead-exit hole cutter starts at |z| 6.0 mm, was 6.9 mm, against a 7.0 mm bore. The extra cutter volume lies in the bore void, so the machined part does not change.
  - `electrical.py:1217`: pitot slot floor `PT_ZT - 0.0028`, was 0.0023.
  - `electrical.py:1519-1531`: the six shallow I2C grooves are wider in plan (`hw = hg + 0.0005`); their height is unchanged.
  - `electrical.py:1543-1551`: the skin-ply cut copy is mirrored into the backend (the root cause of the 33 artefact pairs). It is guarded so the Stub backend is unaffected.
  - All three cut changes match D-247 (`CHANGE-LOG.md:956`) and the F-2b table.
- **No exemption.** `collide_glb_a_blender.py` imports `collision/collide_glb_blender.py` unmodified and keeps tolerance 0.05 mm. Its additions:
  - classification is reported, but every pair still counts as a failure (exit 1 on any pair);
  - entry-rule skips happen only when a strand end lies in no host solid, and the unseated-end check covers that case (0 unseated).
- **Logs are consistent.** Export 20:50-20:53, gate 20:58 (PASS 0 / 0 / 0, 129 bodies, 44 strands, 316 s), collide_a 21:12, a_assembly 22:06. The published GLB hash equals the gated export (s1).
- **Publish.** `concept-a.glb` 20:59, `.opt.glb` and `assembly.opt.glb.part1.js` 20:59:47. I did not check the opt GLB or the viewer in a browser. The record says no browser load was done either (LOW, R12-10).
- **Independent re-run on the published GLB** (built from the current working-tree CAD job): **PASS, 0 / 0 / 0**, 559 s, exit 0. F-2 is closed with no exemption.

### 2.2 Findings F-1 .. F-15

| ID | State | Evidence I checked |
|---|---|---|
| F-1 | **Closed** | D-245 (`CHANGE-LOG.md:953`) rules the 15 deg basis and names the BOARD QP-4 s3 G5 ruling it supersedes, with a trade table. CL-A-PITCH-USE is 0.79 vs 0.60 FAIL in run_all, `graph.json` and `site/data/viewer-data.json`; no 0.575 is left. `#sims` (`app.html:2530-2535`), Status issue 6 and CLAUDE.md agree. The open $0 path is controls rung 1 plus a SITL rerun; see R12-5. |
| F-2 | **Closed** | s2.1 |
| F-3 | **Closed** | `app.html:2406` labels the d209 map "Earlier design (record)". `#fea-hub-current` (`:2410`) matches `T076c_hub_al.md` s0: the hub passes; tube shear and bond fail, also with PETG; H-A2 not run. The film S5 / S6 agree. |
| F-4 | **Mostly closed** | `README.md:13-20` current-design paragraph and the `:111-125` status are correct, except `:122` (GLB gate "open, 40 pairs") and `:19` "Decisions D-182 to D-245" (now D-247). See R12-2. |
| F-5 | **Closed** | s3 |
| F-6 | **Not carried** | R12-1 |
| F-7 | **Closed** | CL-A-STALL-PRED 17.74 m/s FAIL (run_all). The formula matches D-246. Hand check: 1.3 x sqrt(2 x 1.8807 x 9.807 / (1.20 x 0.22 x 0.75)) = 17.74. |
| F-8 | **Closed** | CL-A-LANDING-STROKE is 17.2 mm. Its how-text says it holds only inside the D-243 region and is gated on TP-3 (`claims_a2_struct.py:116-118`). Status is CHECKED, which is acceptable because the condition is in the text. |
| F-9 | **Closed** | `cad/out/EXPOSED-WIRING.md` has 14 wires, totals 0.597 strand-m and gives a reason for every non-zero row. CLAUDE.md:67-69 points to it. `wire_inventory.json` (09:36) predates D-247, but D-247 moves no wire. |
| F-10 | **Closed** | `sync_status_a.py`: header 2026-11-23, 14 FAIL, pitch-use / stall / landing rows, CG 22.05 mm. |
| F-11 | **Closed** | The only "1,423.9 g" left is a labelled history clause (`claims_a1_flight.py:106`). No "28 of 28", "35 of 35", "96 of 96" or "41 strands" text remains. |
| F-12 | **Closed** | `README.md` "## CI" |
| F-13 | **Closed** | `T099-gates.md:9, :56` corrected. The E3d / E5 captions are corrected in `a_assembly_plan.py` and in `ASSEMBLY.md`. |
| F-14 | **Closed** | `requirements.md:122-123` |
| F-15 | **Closed** | `app.html:1258` (date range). No "+$-" is left. |
| C-6 (audit s4 item 6) | **Open** | R12-4 |
| s4 item 5 (cam-clearance JSONs) | Open, owner's call, recorded | `T096-film-rerender.md` Residual 4 |

## 3. T-096 frame review (F-5 rework): reviewer PASS

What I checked against source:
- **S6 card** (main t118.5) and **H7** (highlight t23) are identical cards.
  - "CHANGE-LOG D-246, 2026-11-23 (untagged working tree)".
  - Mass "1.881 kg EST (CAD 1.641 kg) ... over the gate by 410.7 g": 1,880.7 - 1,470 = 410.7 g.
  - Interference gate "0 of 129, deepest 0.034 mm": `cad/out/REPORT.md` row HWC-001 x HWC-003 0.034 mm.
  - Landing SITL "sink 0.13 m/s, lean 0.0 deg, tipped over: no" equals `T097_data/sitl_T097_Z5/sum.json` landing block.
  - Foam "17.2 of 20 mm, 10.76 g, tilt 2.3 deg (worst of 10)" equals the `T098_results.json` row `plateau_sweep_rib25x23/37.5N` "17.2 / 10.76 / 2.27 / 3.36". These are worst per metric, and the label says so.
  - Hub line and pitch use 0.79 vs 0.60 match D-245 and T-076c.
- **S5** (t96, t101) and **H6** (t18.5) show CAD views of the 6061 hub with the H-A1 status (427,333 elements, load basis 1.64 kg stated, "not VERIFIED"). No PETG map is shown.
- **S4 / H3-H5 readouts against `case.fwd.csv`**:

  | Frame | Log time | Readout | Csv value |
  |---|---|---|---|
  | main t75 | 123.5 s | pitch 7.6 deg, alt 85.1 m, V 17.0 m/s | 7.64 / 85.085 / 16.998 |
  | highlight t12 | 108.6 s | 5.0 deg / 89.4 m / 17.7 m/s / -3.1 / -3.2 deg | row 108.631 s: 5.11 / 89.389 / 17.70 / -3.14 / -3.19 |
  | highlight t8 | 43.4 s | 89.8 deg / 13.8 m | 89.8 / 13.734 |
  | main t88 | 245.1 s | 90.0 deg / 1.5 m | 89.96 / 1.481 |
  | highlight t16.5 | 249.5 s | 0.3 m, "touch-down 249.0 s: sink 0.13" | equals `sum.json` |

  The tag reads "SIMULATED: ArduPilot SITL run T097_Z5, 1.881 kg EST".
- **S2/2.2**: at t18.2 (the fin fly-by) there is no caption; at t19.6 the "Propulsion" caption sits over the X2216 in view.
- **D-247 not in the films.** The changes are under 1 mm and internal: the hub cutter moves only in the bore void, the pitot slot floor drops 0.5 mm inside an open pocket, and the I2C grooves are 0.5 mm wider under the skin. Nothing changes at 1080p. It does not matter; re-render at the next CAD change.

LOW notes (no re-render needed now):
- R12-9: the "latest design" card names the pitch-use FAIL but not the A-P6 stall FAIL (17.74 vs 17.0 m/s) or the 14-claim total. Spec 7.4 asks for "verified pass/fail results". Add one row ("14 strict proof FAILs, list in README") at the next card re-render, together with the commit hash.
- The S5 tag says "SIMULATED: FEA" over a CAD view with no contour. The panel text makes it clear, so this is acceptable.

## 4. T-076 / T-083 / T-100 split

**T-076 acceptance:** "every row RF >= 1.0 or a named coupon; Lua cap demonstrated in SITL".
- The rows in `T076_o4b_analysis.md` s2 pass: pins 1.43, cradle 1.66, R1'' 1.48 / 1.23 / 1.75, R3fix 1.37, R4 1.89.
- The C6 hub, DAF floor and A-P10 rows are superseded by D-221 / D-226 / D-236. TP-3, TP-4 and TP-10b are named coupons.
- The Lua cap: the `sitl_T097_Z5_lua` run has `SCR_ENABLE 1`, `Q_M_BAT_CURR_MAX 72` (at least 45 A) and `t_cap_run_s` 0.1 at 1.881 kg.
- Met, with notes:
  - R12-6 (LOW): the surviving rows were computed at 1.64 kg. The close note should state, row by row, why they hold at 1.881 kg (R-GEN-08). For example, the pin rows are plateau-limited ("demand falls with mass here") and R3fix is strike-governed. It should also state that the pin / root-block row describes a part since replaced by the 6061 root fitting (D-229, T-083b min RF 1.21).
  - R12-7 (LOW): the SITL "demonstration" is thin, with the cap active for 0.1 s in one run. TP-2 on the bench is the real check, and no ledger task owns running TP-2 (see R12-5).

**T-083 acceptance:** I re-ran the non-test items.
- Window +12.84 % (CL-A-WINDOW-PRED).
- T/W 2.713 / 2.152 at the predicted mass.
- CG 22.05 mm, SM 7.61 %.
- BOM $1,939.17 incl. reserve (bom_a re-run).
- 3-D gates PASS after D-247 (s2.1).
- A-P6 and the landing rows conditional on TP-3 are in T-100. The motor backorder is in T-093.
- Met.

**Is the split honest?** Mostly. Nothing test-gated is left hidden in T-076 / T-083, and T-100 is BLOCKED with test-record acceptance. Two gaps:
- **R12-5 (MED).** T-100 lists "elevon pitch use 0.60 of 15 deg (D-245) in tethered hover / first flight" as a test item. The current model value already FAILs (0.79), and D-245 names a $0 path first: controls rung 1 (lower the entry pitch-rate demand) and a SITL rerun. That path needs Dillon's approval for a sim round (memory "no sims until final"). That is a design action waiting on an approval, not a test. Calling it test-gated hides it. Fix: add a task (or a T-100 sub-item, NOT STARTED, waiting on approval) for the controls change and SITL rerun, and keep the flight check as the confirmation.
  - Related: TP-1 (bench derate >= 0.889, the 15 Dec go/no-go test) and TP-2 (Lua cap 1.0 +- 0.01, <= 72 A) have no ledger task for running them (grep of the ledger: only the re-spec rows T-081 / T-083 / T-092). Neither do TP-15 to TP-18 or the weigh-in. Either widen T-100 or add a sibling task, so every test named in TEST-PLAN-O4B has an owner row.
- **R12-8 (LOW).** T-100 parents are R-PHY-08, R-PHY-09 and R-OPT-01. A-P6 at the predicted mass is the R-GEN-08 requirement (AM-011) that T-083 carried, so add R-GEN-08. TP-10b (vibration) has no R-PHY row among the parents; check whether R-PHY-03 / R-PHY-05 applies.

## 5. T-050 close

- **6.4 compliance after 2026-11-18.**
  - The M/S decisions D-208 to D-240 now each carry a trade table and a benchmark line. The ones that are weak (D-212 r3, D-220, D-221; D-215 ETB; D-225 abstract only) are flagged as weak.
  - Of D-241 to D-247, only D-243 is an M/S decision, and it complies (EVA foam source).
  - D-244 / D-245 state "none found" for a project-internal criterion. D-245 carries a trade table.
  - D-247 is a rung-1 cut fix with no load-path change, and it names its rejected alternative. I accept N/A.
  - Verdict: complies.
- **Spot check 1: Lavalette et al., ECCM18 2018** (TU Delft repository PDF, fetched 2026-11-23). The title, authors and Athens 24-28 June 2018 match. The abstract says "increasing the adhesive overlap length has the highest impact on increasing the joint strength". The specimens are 2-5 mm OD pultruded tubes, overlap 5-20 mm, adhesive 0.1-0.4 mm. **Correct as cited.** The joint pieces are 6082-T6, not 6061, which is consistent with the close's "no 6061-T6 allowable".
- **Spot check 2: Engineering ToolBox friction table** (fetched 2026-11-23). Rubber on dry asphalt 0.9 / 0.5-0.8, wet asphalt 0.25-0.75, dry concrete 0.6-0.85, wet concrete 0.45-0.75 are all present. The page metadata gives datePublished 2004-11-04 and dateModified 2025-05-09. **Correct**, except R12-11.
- LOW notes:
  - **R12-11:** the D-215 CHANGE-LOG line says "no grass row", but the page has "Car tire / Grass 0.35". The close file itself mentions it. Change it to "no foam or UHMW row; car tyre on grass 0.35 only".
  - **R12-12:** the D-241 summary row (`CHANGE-LOG.md:949`) still says "No benchmark found" for D-215 / D-225 / D-229. Add a pointer to the T-050 close lines so the log does not contradict itself.

## 6. Findings

| ID | Sev | Task | Evidence | Required fix |
|---|---|---|---|---|
| R12-1 | HIGH | T-099 | F-6 (go/no-go 2026-12-15 vs SCHEDULE-A D1 18 Dec / O2 7-15 Dec "T-Motor the latest", X2216 backorder) is untouched. It is not in `session-state.md`, not in the Explorer Status decision table, and not in the README "Next" line, which repeats "go/no-go 2026-12-15" with no caveat. The ledger mentions it only inside T-099's evidence cell. The Explorer Status shows "Main order go / no-go ... 28 Dec" (`sync_status_a.py:78`), a third date with no link to 15 Dec. `SCHEDULE-A.md:17, 24, 30, 76` still say T-Motor and "3 motors". | Put F-6 where Dillon will see it: an open-decision row in the Explorer Status (`sync_status_a.py` DECISIONS) and in `session-state.md` (or a ledger row owned by D), naming the conflict and the options (keep 15 Dec with a latest Order 1 arrival date, or re-date). Correct the SCHEDULE-A T-Motor / "3 motors" text (no date decision needed for that). Do not re-date without Dillon. |
| R12-2 | MED | T-099 | `README.md:122` says "the exported-model gate for `concept-a.glb` (T-099 F-2, 40 pairs ...) is open". F-2b passes 0 / 0 / 0, and the published GLB is the gated file. `README.md:19` says "D-182 to D-245". Explorer `app.html:459` says only "tracked in T-099 F-2". | State the GLB gate result (0 pairs, 0 unseated, 0 bad entries, `collide_glb_a.py`, D-247) in the README and the Explorer constraint row, and update the D-range. |
| R12-3 | MED | T-099 | The hard constraint (CLAUDE.md:54-57) names `collide.py --glb`, and the user owns the 3-D physics constraint. The concept A gate `collide_glb_a.py` replaces the K09-L square / flat-ring entry test with a pad / termination-proximity rule (D-247). The rule was settled between runs: the first draft measured at the crossing (13 bad), the final version at the end (0 bad). The rule is technically reasonable: it mirrors collide_a's per-body TERMINATION rule, and concept A leads are soldered or crimped. But it is a change to a user-named gate, and it appears only in the CHANGE-LOG. | Name the concept A gate tools and the D-247 entry rule in the CLAUDE.md hard-constraint line (conductor edit) and in the README. Flag it to Dillon in the next milestone message as a gate-definition change he may veto. |
| R12-4 | LOW | T-099 | `app.html:411` caption: "earlier design (record) (render predates D-227 ...): MN2212 on a canted cup". The asset `assets/renders/a-detail-propulsion.webp` (c6d027b6) shows and labels "SunnySky X2216 880KV". | Caption the current render as current (X2216) in its generator, then regenerate. |
| R12-5 | MED | T-100 | Pitch use is classed as flight-test-gated, but a $0 controls change plus a SITL rerun comes first (D-245 ladder) and is waiting on a sim approval. TP-1, TP-2, TP-15..TP-18 and the weigh-in have no execution task. | s4 |
| R12-6 | LOW | T-076 | The rows are at 1.64 kg; the mass basis at 1.881 kg and the superseded pin / root-block row are not stated in the close note | s4 |
| R12-7 | LOW | T-076 | The Lua cap is active for 0.1 s in one SITL run | Keep TP-2 as the deciding test (R12-5 owner row) |
| R12-8 | LOW | T-100 | R-GEN-08 is missing from the parents | Add R-GEN-08; check the vibration requirement row |
| R12-9 | LOW | T-096 | The S6 / H7 card omits the A-P6 stall FAIL and the 14-claim total; there is no commit hash | Next card re-render (overlay only) |
| R12-10 | LOW | T-099 | The published `.opt.glb` / `part1.js` were not loaded in a browser by anyone | One browser load of `site/app.html` 3-D view before the push |
| R12-11 | LOW | T-050 | D-215 Benchmark line "no grass row" is wrong (car tyre on grass 0.35) | Reword |
| R12-12 | LOW | T-050 | The D-241 summary row contradicts the T-050 close lines | Add a pointer |

## 7. What stays open (not for this review to close)
- The pitch-use FAIL (controls), A-P6 (TP-11), the landing foam region (TP-3) and the 12 D-237 FAILs: all in T-100 or in bench tests.
- The F-6 date decision (Dillon).
- The cam-clearance JSON adoption (film owner).
- The X2216 backorder and the Order 1 re-read (T-093, 1-4 Dec).
