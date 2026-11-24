# T-099 final design audit, concept A O4b (AM-035), 2026-11-23

Reviewer: independent eng-reviewer (opus). Repo `redesign/v1`, HEAD `c6d027b6`. Scope: the design as final "with what we have now"
(AM-035), against the hard constraints in `CLAUDE.md`, the master spec (read in full, 1,173 lines) and `docs/spec-amendments.md`
(AM-001 to AM-035, read in full). Nothing in the repo was edited. My only writes are this file and
`docs/audits/2026-11-23-T099-final-audit-logs/`. The ledger row is not marked; this audit does not mark anything VERIFIED COMPLETE.

**Verdict: NOT FINAL-CLEAN.** The core design is one coherent configuration. Mass 1.881 kg EST (CAD 1,641.0 g), BOM $1,939.17,
SunnySky X2216 880KV, FC 75 mm left of centre and the landing foam region agree across the CAD, the parameters, the BOM, the
analysis records and the Explorer `#sims` / `#subsystems` views. Six HIGH findings stop it from being called final:
- the pitch-use basis is ruled two opposite ways in the record (F-1);
- the exported-model (`--glb`) gate has never passed for concept A, and my probe run of it fails (F-2);
- the hub FEA shown in the Explorer and the film is for the superseded PETG hub (F-3);
- README.md describes the earlier design (F-4);
- the film's closing card shows stale results (F-5);
- the 2026-12-15 go/no-go date does not fit the schedule (F-6).

T-096 film: **SEND BACK** (section 4).

## 0. What I re-ran (commands from the repo root)

| Command | Exit | Result | Matches the record? |
|---|---|---|---|
| `python -I tools/ledger_audit.py` | 0 | 113 requirements, 99 tasks; 80 VERIFIED COMPLETE, 7 BLOCKED, 5 DEFERRED, 5 NOT STARTED, 1 IN PROGRESS, 1 READY FOR REVIEW; 0 errors | yes |
| `python -I redesign/qp/A/proofs/run_all.py` | 1 | 565 nodes; 12 distinct STRICT FAIL claims plus `CL-A-FLUTTER-ELEVON-NOM` UNVERIFIED; VERIFIED 0, UNVERIFIED 226 (log: `T099-final-audit-logs/run_all_rerun.txt`) | yes (same 12 as D-237 / T-092) |
| `python -I redesign/qp/A/bom_a.py` | 0 | spend $1,592.23 + reserve $346.94 = **$1,939.17**, margin $60.83; +30 % on unverified lines $2,029.68 (information only, AM-013) | yes |
| `python -I redesign/qp/A/schedule_a.py` | 0 | baseline (4 mornings, p 0.72, one crash) F06 ends 19 Apr, **slack +11 d**; p 0.60 + crash -5 d; 3 mornings -2 to -25 d | yes |
| Gate logs `docs/audits/2026-11-23-T099-logs/` (not re-run) | 0 / 0 | collide_a pose 21: 585 bodies, 129 parts, 3 poses, 0 pairs > 0.05 mm, 0 open wire ends, 0 folds; a_assembly: 66 steps, 129/129 placed, 0 blocked, 0 unsupported | read and checked against `a_assembly_blender.py` |
| **New probe:** `blender -b --factory-startup --python-exit-code 1 -P redesign/collision/collide_glb_blender.py -- <T-099 _job.json> redesign/site/assets/concept-a.glb <out>` | 0 | 129 part bodies, 44 wire strands; **40 pairs > 0.05 mm (deepest 1.327 mm), 0 unseated ends, 27 bad wire entries** (`T099-final-audit-logs/glb_gate_concept-a_report.json`, `.log`) | no record exists (F-2) |
| `ffprobe` and frame grabs of `film-main-1080p60.mp4` (frames 1074, 1180); 9 saved T-096 frames opened | 0 | 1920x1080, 60/1, 7,194 frames | yes |

`git status` after all runs shows only the untracked T-099 audit files: `run_all` and `bom_a` rewrote no tracked file.

## 1. Hard constraints

| Constraint | Verdict | Evidence | Open |
|---|---|---|---|
| $2,000 total incl. crash reserve (AM-013, AM-018) | **PASS (EST)** | `bom_a.py` $1,939.17, margin +$60.83; reserve by definition $346.94 (AM-018); BOM tab `app.html:1260-1266` equals it. 15 of 53 lines unverified ($222.14): at +30 % they come to $2,029.68, which is information only since AM-013. G7 FAIL, also information only. | R15 rib tube landed price "—" (T-088, T-093); X2216 RMRC backorder; prices must be re-read 1-4 Dec (T-093). BOM tab header still reads "prices read 2026-11-14/15" (`app.html:1258`), and "+$-29.68" is a formatting slip (`:1266`). |
| Built and flight-tested by 2027-04-30 | **PASS on baseline, thin (EST)** | `schedule_a.py` +11 d slack (4 booked mornings, p 0.72); negative with p 0.60 + crash (-5 d) or with 3 mornings (-2 to -25 d) | F-6: the go/no-go date does not fit SCHEDULE-A. SCHEDULE-A still names T-Motor as the late vendor (`SCHEDULE-A.md:24`) and "3 motors" in the main order (`:30`). |
| Portable, one car trunk, < 25 kg | **CONDITIONAL** | One piece, 0.90 x 0.50 x 0.394 m with props on (`params-A.json` box/packed_m, T-084). `CL-A-BOX-FIT` ratio 1.00 against the 1.2 x 0.5 x 0.4 m box: width 0.50 sits exactly on the limit. 1.881 kg is far under 25 kg. | The trunk has not been measured (ASM-A-TRUNK; AM-027 asks the team to measure the Altima trunk). Zero width margin. |
| 3-D gates: every build step and the assembled aircraft, no interpenetration, no open wire ends, no exemptions | **PASS for the CAD gates; FAIL / UNRESOLVED for the exported-model gate** | collide_a and a_assembly as in section 0, plus 18 linkage poses 0 pairs (`cad/out/REPORT_linkage_poses.md`, T-092; CAD unchanged since). | F-2, F-13 |
| Flight cases in the 3-D sims pass against their limits | **CONDITIONAL / FAIL** | Landing: AR-014 FAIL at 30 N and 45 N. AR-016 passes all 10 cases only for foam Fp 37.5-39.0 N and zeta 0.02-0.05 (D-243); the 39 N cap is a hand scaling (EST). I checked the 37.5 N table against `T098_data/landing_cad_1881_p37p5_rib25.txt`: worst stroke 17.2 mm, n 10.76 g, tilt 2.3 deg, matching `#sims`. SITL AR-015: every categorical line passes. Pitch use 0.69 / 0.79 of 15 deg FAILs, which I re-read from `T097_data/sitl_T097_{Z5,T074}/sum.json`. Cruise 17.0-17.2 m/s is under 1.3 Vs = 17.75 m/s (A-P6 FAIL). | F-1 (which pitch basis stands), F-7 (A-P6 not judged at the predicted mass in the proof chain), F-8 (landing claim stale). TP-3 foam decides the landing. |
| CAD fidelity (real shapes, unknowns marked) | **PASS with notes** | Vendor or EST labels and "—" for unknowns throughout `amodel/*.py`. Examples: FC header envelope "NOT drawn" (`electrical.py:605`), RX antenna T element "—" (`:1090`), ESC component envelope "shape unknown" (`propulsion.py:325`). The two mass proxies HRN-001 and HRD-001 carry no mesh in the GLB (node `mesh` None), so there are no stand-in boxes. The hub is drawn as machined 6061 (`wing.py:961`). | F-2: if the 40 GLB overlaps are uncut booleans in the export (the D-88 failure mode), the Explorer 3-D model shows parts through uncut skin, which is a fidelity gap in what users see. The `hub_body.py:1` docstring still says "printed hub". |
| Exposed wiring listed with length and reason, kept minimal | **PARTIAL** | CAD total 0.597 strand-m (`T092_data/r4/wire_inventory.txt`: pack leads E-HRN-13 2 x 0.127, balance lead E-HRN-14 0.064, battery tail E-HRN-12 2 x 0.042, phase-lead ends 4 x 3 x 0.008-0.009, servo leads 2 x 3 x 0.012, ESC signal 6 x 0.003). | F-9: the per-wire table with reasons is still the D-198 / D-199 table (0.87-1.02 strand-m, `review/QP-5/HARNESS-ENCLOSED.md` s5 and D-199.2). No table matches 0.597 m. |

### 1.1 Rulings asked for in the brief

**Travel-0 steps (A1, B0b, E3d, E5): not a violation of "no exemptions".**
- A1 (wing core) and B0b (hub in the bench run) are the first placements of their runs. Nothing is placed before them, so there is no path to sweep against.
- E3d (silicone pitot lines) and E5 (webbing straps) are flexible. A rigid straight-line sweep does not describe how they go in.
- The fitted position of all four is checked: `_job.json` holds all 129 parts, including AVN-009-T/S, PWR-002, WNG-001 and CGE-001, and collide_a's static pose finds 0 penetrations among them.

The step captions are inaccurate, though. E3d and E5 say "this step checks the fitted position only". In fact `a_assembly_blender.py:38` skips every step whose `dir` is None, so a_assembly checks nothing for these steps; only collide_a does. Fix the captions (F-13) and cite collide_a in the gate record. The hand threading of E5 and the push-on of E3d stay build-guide checks.

**Are collide_a / a_assembly the right concept A equivalents? Partly.**
- `collide_a.py` is the concept A form of `collide.py` without `--glb`. It drives the same unmodified `collide_blender.py` checker (`collide_a.py:2`) and checks static, both elevon limits, wire ends and folds, plus the 18 linkage poses.
- `a_assembly.py` is the concept A form of `assembly_check.py`: swept insertion, support and wire order on the same meshes and the same 0.05 mm rule.
- Nothing covers the `--glb` half of the named gate (`collide.py:171-252`, D-88): the check on the **exported** model as the Explorer shows it, with cuts baked in and no cutter honoured, plus the wire-entry rule.
- The gates audit says "No concept A GLB exists in the repo". That is wrong. `redesign/site/assets/concept-a.glb` (11.74 MB, exported in T-038 by `export_glb.py --root redesign/qp/A/cad/model`) is tracked. The only commit after it, `f48f9756`, touched `model/mass_budget.json` only.
- My probe run of the `--glb` checker on that GLB fails (F-2).
- `CLAUDE.md` should name the concept A tools. Editing it is for the conductor.

## 2. Proof claims and checks currently FAIL or UNVERIFIED

Source: the `run_all.py` re-run (section 0) and AR-014..016. "$0 action" means a design or modelling action at no cost that could still close or improve the claim before a test.

| # | Claim | Value | Limit | Decided by | $0 design action left? |
|---|---|---|---|---|---|
| 1 | CL-A-MASS-PRED (A-D3) | 1.881 kg | <= 1.47 kg | T-A-WEIGH weigh-in (G6) | No; the miss is accepted by AM-011 and the physics checks govern. The how-text still says "1,423.9 g predicted" (stale, F-11). |
| 2 | CL-A-MASS-GATE-ROOM (A-P1) | 1.881 kg | <= 1.47 kg | weigh-in | No (AM-011) |
| 3 | CL-A-CUTS-REQUIRED | 409.1 g | <= 41.6 g | weigh-in of foam, prints and epoxy (M11) | No |
| 4 | CL-A-VIB-IN-BAND (A-P10a, D-185) | 3 strong modes | 0 in 94-321 Hz | TP-10b T-A-TAP on the built airframe | No. The D-239 trade found no candidate (57-69 of 72 cases fail). The D-233 C trade is held for after the tap test. |
| 5 | CL-A-VIB-FC | 187.2 m/s2 (sweep); 19.3-32.9 in the operating window | <= 30 | first tethered hover, IMU VIBE (T-A-TETHER-VIBE), and TP-10b | No (D-239); arms 10x8 is held as a fallback |
| 6 | CL-A-VIB-GM | 1.13 | >= 2.0 | TP-10b and the tether hover | **Yes, modelling only.** The claim still evaluates the FC-at-centre model. The as-drawn FC at y -75 mm gives 2.52-4.00 in the model (D-239). Credit stays held until the tap test, but the claim should show the as-drawn value as UNVERIFIED rather than the superseded geometry. |
| 7 | CL-A-VIB-GM-SHIFT | 1.05 | >= 2.0 | as 6 | as 6 |
| 8 | CL-A-HORN-RIB-FOAM-HOLD | 431.8 kPa | <= 85.8 kPa | TP-16 horn-rib coupon | No; the test claim supersedes the analysis |
| 9 | CL-A-HORN-RIB-FOAM-STALL | 860.9 kPa | <= 85.8 kPa | TP-16, TP-18 | Partly: the named fallback limits horn force through the servo torque limit |
| 10 | CL-A-ELEVON-TORSION-FOAM | 504.3 kPa | <= 85.8 kPa | TP-17 | No (CF spar in the elevon is the fallback) |
| 11 | CL-A-HORN-BEARING-STALL | 36.65 MPa | <= 20 MPa | TP-16, TP-18 | Partly: bush the hole or limit the stall force (servo endpoint or torque) on paper |
| 12 | CL-A-LINKAGE-FREEPLAY | 1.28 deg | <= 1.0 deg | TP-15 dial-gauge free play | Yes: tighten the arm and horn hole tolerance (0.10 mm now) or shim the Z-bend on the drawing |
| 13 | CL-A-FLUTTER-ELEVON-NOM (A-P13) | 41 m/s, UNVERIFIED | >= 28.8 m/s | E1 hinge-damper coupon (G8) | No |
| 14 | 4 test claims with value "—": HORN-RIB-COUPON, HORN-STALL-STEP, ELEVON-TORSION-COUPON, HORN-STALL-BENCH | — | per TP | TP-16, TP-18 | No |
| 15 | Elevon pitch use, A-P11 (D-244; **not in run_all**) | 0.69 (Z5) / 0.79 (T-074) of 15 deg; peak 10.6 / 12.0 deg | 0.60 of 15 deg (D-244), or <= 0.60 x 20 = 12 deg peak (BOARD QP-4 s3) | **A ruling first (F-1)**, then F04 first transition | **Yes: a $0 decision.** On the board basis it passes (12.0 deg sits exactly on the line). |
| 16 | A-P6, 1.3 Vs at the predicted mass (**not in run_all**; CL-A-STALL is judged at 1.47 kg) | 17.75 m/s (AR-015), 17.56 m/s (REQUIREMENTS-A:38) | <= 17.0 m/s cruise | TP-11 measured stall, pass at CLmax >= 0.81 | No. F-7: the claim should be judged at 1.881 kg per AM-011. |
| 17 | Landing (A-P5 / AR-014; CL-A-LANDING-STROKE shows a stale 15.2 mm PASS) | AR-014 FAIL at 30 / 45 N; AR-016 PASS only at Fp 37.5-39.0 N and zeta 0.02-0.05 | stroke <= 20 mm, n <= 12 g, tilt <= 3 deg, RF >= 1 | TP-3 pad-drop foam coupon | No further $0 rung at 20 mm. The fallback (36 mm pad, Fp 34.5-39 N) is a CAD change not yet made; A-P9 there is 30.60 deg, 0.10 deg over its target. |

The proof graph has 226 UNVERIFIED nodes and 0 VERIFIED, because nothing is built. Every row above needs hardware or a ruling.

## 3. Cross-artifact consistency (spot check)

Agreeing everywhere I looked:
- mass 1.881 kg EST / CAD 1,641.0 g: CLAUDE.md:29, `app.html:424, 1184, 1197, 1224, 2515`, params-A.json, film S6;
- BOM $1,939.17: CLAUDE.md:31, `app.html:425, 452, 1260`, bom_a.py;
- motor X2216 880KV: `app.html:1190`, film S2;
- FC at y -75 mm: `app.html:1192`, CHANGE-LOG D-240;
- foam region 37.5-39.0 N / zeta 0.02-0.05: `app.html:2515, 2534`, AR-016, TEST-PLAN-O4B.md:77-79, CHANGE-LOG D-243.

Mismatches (each is also a finding below):

| # | File:line | Says | Should agree with |
|---|---|---|---|
| C-1 | `README.md:13-15` | "Current design (2026-11-16) ... 4 x T-Motor MN2212 KV780 ... about 1.456 kg ... BOM $1,779" | X2216, 1.881 kg EST, $1,939.17 (CLAUDE.md:29-31) |
| C-2 | `README.md:98-125` | "Status and next steps, as of 2026-11-10": the K09-L status, foam-board twin, main order 2026-12-15 | concept A status (`app.html` #status) |
| C-3 | `redesign/qp/A/proofs/claims_a1_flight.py:332-339`, `params-A.json:139-143` (pitch_use_max note "of the 20 deg stop"), `site/proofs/data/graph.js` and `site/data/viewer-data.json` (CL-A-PITCH-USE 0.575 CHECKED) | pitch use PASS on the 20 deg basis with the D-195 value 11.5 deg | `app.html:2529-2534` and CHANGE-LOG:952 (D-244): FAIL on 15 deg. `review/QP-4/BOARD.md:91` rules the reverse. F-1. |
| C-4 | `site/data/viewer-data.json`, `graph.js` CL-A-LANDING-STROKE 15.2 mm CHECKED | stale STRUCTURES iteration-2 value | AR-014 / AR-016 (17.2 mm at the accepted foam, FAIL outside it) |
| C-5 | `app.html:2404-2452` (#structures: "Printed hub ... PETG 2.156 ... PASS", 2026-11-17) and `app.html:411` (cage render caption "printed hub") | PETG hub | machined 6061 hub (D-220; `wing.py:961`; `app.html:1189` says "Machined 6061 hub") |
| C-6 | `app.html:411` (propulsion still caption) | "render predates D-227 ... MN2212 on a canted cup" | the asset was re-rendered with the X2216 in T-096 (`assets/renders/a-detail-propulsion.webp`, commit c6d027b6) |
| C-7 | `app.html:1212` | "Concept A (D-182) · 2026-11-15" | 2026-11-23 |
| C-8 | `app.html:1218` phase 07 and `:1224` issue 1 | exposed wire "9.09 to 1.02 strand-m (2026-11-18)", "pitot tube run not designed (0.45 m)" | 0.597 strand-m (D-240); pitot lines AVN-009-T/S are drawn (E3d, 39 mm each) |
| C-9 | `app.html:1224` issue 2 | hub arm-socket wall, PETG hoop check (D-196) | the hub is machined 6061 (D-220); the issue is either obsolete or needs restating |
| C-10 | `app.html:1224` issue 4 (`sync_status_a.py:40`) | flutter "lowest onset 38.5 m/s hot", "free play ≤ 0.5°" | CL-A-FLUTTER-ELEVON-HOT 37.5 m/s; TP-15 / CL-A-LINKAGE-FREEPLAY limit 1.0 deg |
| C-11 | `app.html:1224` issue 7 | "Ask T-Motor ...; G7 keeps only about $5 of room" | motor is SunnySky (D-227); G7 is information only (AM-013) and FAILs |
| C-12 | `app.html:1224` / `:1214` | no line for pitch use, A-P6 or the landing foam region | `#sims` (`app.html:2515`) |
| C-13 | `app.html:1230` | "CG ... D-228 CG 24.41 mm EST"; "at least 40.8 g of the estimated cuts real" | CG 22.05 mm (CL-A-CG, D-240); CUTS claim: 27.2 g of 41.6 g |
| C-14 | `app.html:1233` (`sync_status_a.py:74`) | "Declare the design final ... brings back the Simulations tab (held until then, 2026-11-15)" | the #sims view exists and is published (T-097/T-098) |
| C-15 | `CLAUDE.md:31` | "12 proof claims FAIL pending bench / tap tests" | true for run_all, but the AR-015 pitch-use FAIL (D-244), A-P6 and the landing foam dependence are not named |
| C-16 | `docs/requirements.md` R-INT-02 NOT STARTED, R-INT-03 NOT STARTED | — | T-035 VERIFIED COMPLETE; T-036 EXPLICITLY DEFERRED (roll-up lag; ledger_audit does not catch it) |
| C-17 | Film S6 card (main t118), S5 (t96), S4 / H4 | 1.50 kg Z5 landing, PETG hub d209, "D-212 rev 3, commit 49a9afe3-dirty" | AR-015 / AR-016, the 6061 hub, D-244 at a clean commit |
| C-18 | `REQUIREMENTS-A.md:38` vs AR-015 | 1.3 Vs 17.56 m/s at 1.8796 kg vs 17.75 m/s at 1.881 kg | one basis (F-7) |
| C-19 | `CL-A-ASSY-STEPS` how-text "28 of 28 steps", value 59; `params-A.json` cad3d notes "35 of 35", "96 of 96" | — | a_assembly 66 steps (59 with parts plus 7 marker steps), 129 of 129 placed |

## 4. T-096 film review: **SEND BACK**

What I checked myself:
- `ffprobe`: 1920x1080, 60/1, 7,194 frames. I did not re-decode in full: the `decode.log` record shows exit 0, and 2 frames grabbed at frames 1074 and 1180 decoded cleanly.
- Frames opened: main_t3, t19.5, t38.5, t56, t75, t96, t118, highlight_t12 and still_detail-avionics, plus the two new grabs.
- The geometry is the current CAD:
  - the X2216 is visible and captioned (t19.5);
  - the FC annex on the -y side (t19.5);
  - 2800 mAh pack (avionics still);
  - 129 parts.
- The SIMULATED and ILLUSTRATIVE tags are present (t38.5, t56, t75, t96).
- The camera re-check claims are confirmed from the scratch JSON (`t096cam/work-main/cam_clearance.json`):
  - inside-geometry frames: 0;
  - S2/2.2 blocked frames: 15 (FIN-004-R 11, FIN-001-R 4);
  - worst block ratio 0.498, at frame 1074.

Defects (fix all before VERIFIED):
1. **S6 closing card (t118) shows superseded results as the "latest validated design" (spec 7.3 S6, 7.4, 12.4 "technical labels are accurate").**
   - "Landing (SITL, Z5_gb0) sink 0.02 m/s ... tipped over: no (1.50 kg, run of 2026-11-15)". The current landing passes only inside the D-243 foam region (AR-016), and AR-015 has a 1.881 kg run.
   - "Hub FEA (run d209) ... PETG ...". The hub is 6061 (F-3).
   - "Revision D-212 rev 3, commit 49a9afe3-dirty". It should read D-244 at a clean hash.
   - "(-410.7 g left)" for a missed gate. It should read "over the gate by 410.7 g".
2. **S5 (t96) "SIMULATED: FEA hub S2 prop strike ... PETG hub single-point peak 18.3 vs 20 MPa"** is the PETG hub of D-209. Either label it "earlier design (record)" on screen, or show the current hub analysis (T-076c H-A1, 6061) with its open tube-shear and bond rows.
3. **S4 shot 4.2 (t75) and highlight H4.1 (highlight_t12)** play the 1.50 kg Z5_gb0 run from geometry before D-207. The label says so, which keeps R-VID-09 honest. But T-097 left a 1.881 kg Z5 run with a plant csv (`T097_data/sitl_T097_Z5/`). Repoint S4 and H4 to it. The highlight is a presentation piece, so stale-mass motion is the wrong default.
4. **S2/2.2, frames about 1062-1076.** The "Propulsion" caption is on screen while the right fin tube and its root fitting fill the view and no motor is visible (frame 1074, block ratio 0.498; grab `docs/audits/2026-11-23-T099-final-audit-logs/main_frame1074_S2-2.2_blocked.png`). Adjust the camera path or the caption timing.
5. Adopt the new camera-check results into the tracked `film/cam-clearance*.json`, or record why not. The repo copy still describes the 2026-11-19 film. This is the owner's decision; it is listed so it is not lost.
6. Outside the film but the same work: the Explorer caption `app.html:411` still says the propulsion render predates D-227 (C-6).

## 5. Requirements not VERIFIED COMPLETE (`docs/requirements.md`, 113 rows: 62 VERIFIED, 38 IN PROGRESS, 10 NOT STARTED, 3 BLOCKED)

- **IN PROGRESS (38):**
  - preservation and general: R-PRES-04, R-GEN-01, R-GEN-02, R-GEN-05, R-GEN-06, R-GEN-07, R-GEN-08;
  - CAD and physics: R-CAD-02, R-CAD-03, R-CAD-04, R-PHY-03, R-PHY-05, R-PHY-08, R-PHY-09;
  - optimisation: R-OPT-01, R-OPT-02, R-OPT-04, R-OPT-05;
  - integration: R-INT-05, R-INT-06;
  - repository and monitoring: R-REPO-06, R-REPO-08, R-REPO-10, R-MON-02, R-MON-03;
  - rules: R-RULE-01, R-RULE-02, R-RULE-03, R-RULE-04, R-RULE-06, R-RULE-07, R-RULE-08, R-RULE-09;
  - communication: R-COM-01, R-COM-02, R-COM-04, R-COM-05, R-COM-06.
- **NOT STARTED (10):** R-GEN-03, R-INT-02 (roll-up lag, C-16), R-INT-03 (should read EXPLICITLY DEFERRED per T-036 / AM-033), R-VER-01, R-VER-02, R-VER-03, R-VER-04, R-VER-05, R-VER-06, R-DEL-01.
- **BLOCKED (3):** R-ORC-04 (James's agent definitions), R-INT-01 (team schema, AM-003), R-INT-04 (DaVinci, AM-003).

## 6. Findings (severity, evidence, required fix)

| ID | Sev | Evidence | Required fix |
|---|---|---|---|
| F-1 | HIGH | The pitch-use basis is ruled both ways. `review/QP-4/BOARD.md:91`: "G5 uses the hardware stop ... <= 0.60 x 20 deg = 12 deg ... The old 15 deg basis is withdrawn." D-244 (CHANGE-LOG:952), AR-016 and `#sims` say the reverse. Neither T-098 nor review rounds 10 and 11 cites BOARD QP-4 s3 (grep: no hits). The proof chain and params follow the board, with the stale value 0.575 (C-3). On the board basis the current peaks of 10.6 / 12.0 deg pass; on 15 deg they FAIL. The Explorer shows both PASS (Proof view) and FAIL (#sims). | A single explicit ruling (board / Dillon, or AM-004 opus, since this is an engineering line) in a new CHANGE-LOG entry that names which earlier ruling it supersedes. Then make the claim, params, `#sims`, Status and CLAUDE.md agree, using the current SITL value. Do not pick a side silently (CLAUDE.md "Where things are"). |
| F-2 | HIGH | No exported-model gate has been run for concept A. My probe of `collide_glb_blender.py` on the tracked `concept-a.glb` gives 40 pairs > 0.05 mm, the deepest WNG-008-LL/RL x WNG-011 at 1.33 mm. Others: WNG-008 x WNG-014 1.29 mm; E-HRN-02..05 x WNG-011 0.61-0.84 mm; CGE-001 x E-HRN-02..05 0.63-0.69 mm; WNG-007/009/010 x WNG-011/014 0.50-0.62 mm; MEC-002 0.31-0.36 mm; AVN-009 x WNG-001 0.19-0.24 mm. Also 27 bad wire entries at PRP-003, AVN-002 and MEC-001, and 0 unseated ends. Collide_a honours cutters at these places (WNG-011 has 113 cutters in `_job.json`), so the likely cause is booleans not baked into the export (D-88). Caveats: the checker lacks a_collide_blender's orientation fix, and the wire-entry rule is a K09-L rule. | Make a concept A GLB gate (collide_glb with the a_collide_blender orientation fix) and run it officially. Classify each pair as an export artefact or a real clash, then fix the exporter or the CAD. Decide whether the wire-entry rule applies to concept A pad solders. Re-export `concept-a.glb` / `.opt.glb` and re-run until 0. Name the concept A gate tools in CLAUDE.md (conductor). |
| F-3 | HIGH | `app.html:2404-2452` (#structures, the README "Hub stress map" link) and film S5 / S6 present the 2026-11-17 PETG hub FEA (d209) as PASS. The hub has been machined 6061-T6 since D-220 (`wing.py:961`), which found that the PETG hub had been sized on the wrong load (Mz 17.51 N m). The 6061 result (T-076c H-A1: the hub passes; tube shear and bond rows fail, routed to D-226 / TP-4 / TP-5) is not shown. | Label the d209 map "earlier design (record)" and add the 6061 hub status and its open rows, or re-run the hub FEA on 6061 and publish it. Fix `app.html:411` "printed hub". |
| F-4 | HIGH | `README.md:13-15` and `:98-125` (C-1, C-2): the front door states the MN2212, 1.456 kg and $1,779, with a K09-L status section | Rewrite the current-design paragraph and the status section from CLAUDE.md, bom_a and run_all |
| F-5 | HIGH | T-096 film S6, S5, S4 / H4 (section 4) | The section 4 fixes, then an independent frame re-review |
| F-6 | HIGH | The go/no-go is 2026-12-15 (CLAUDE.md:31; AM-005, AM-006, AM-009, AM-016). SCHEDULE-A runs the bench campaign B0 10-17 Dec, the bench decision D1 on 18 Dec (latest safe 28 Dec) and Order 1 arrival 7-15 Dec, "T-Motor the latest" (`SCHEDULE-A.md:24-30, 56-58`). The X2216 is on RMRC backorder (T-088; AM-019). TP-1 and TP-2 cannot finish by 15 Dec unless Order 1 lands by about 10 Dec. | Re-plan the dates around the X2216 stock re-read at Order 1 (T-093). Either keep 15 Dec with a stated latest arrival date, or record a new go/no-go date as a team decision. Remove the T-Motor and "3 motors" text. |
| F-7 | MED | `CL-A-STALL` is judged at the 1.47 kg gate (15.69 m/s PASS). At 1.881 kg, 1.3 Vs is 17.75 m/s (AR-015) or 17.56 m/s (REQUIREMENTS-A:38), above the 17.0 m/s cruise. AM-011 says physics checks apply at the predicted mass. | Add or replace the claim at the predicted mass (FAIL, gated by TP-11), and unify the 17.56 / 17.75 basis |
| F-8 | MED | `CL-A-LANDING-STROKE` 15.2 mm CHECKED (C-4) | Re-source to AR-016 and gate it on TP-3 (the PASS holds only inside the foam region) |
| F-9 | MED | The exposed-wire table with reasons is from D-198 / D-199 (0.87-1.02 strand-m). The CAD now has 0.597 strand-m with different per-edge lengths (E-HRN-13 0.127 vs the table's 0.107 per lead). The Explorer quotes 1.02 m and an undesigned pitot (C-8). | Regenerate the per-wire table (wire, strands, exposed length, reason) from `wire_inventory.json` and point CLAUDE.md, the Explorer and HARNESS-ENCLOSED to it |
| F-10 | MED | Explorer #status stale lines C-7 to C-14 (`sync_status_a.py` hard-coded rows) | Update `sync_status_a.py` and regenerate |
| F-11 | LOW | Stale proof how-texts: MASS-PRED "1,423.9 g"; ASSY-STEPS "28 of 28"; params cad3d notes "35 of 35" / "96 of 96" (C-19) | Refresh the text |
| F-12 | MED | The CI "Regenerate and verify" workflow runs only `analysis/verify.py`, `review/build.mjs` and `firmware/tools/check_params.py`, none of the concept A generators (bom_a, run_all, sync_bom_a, sync_status_a, make_sims_view, viewer_data_a). A green CI is no evidence of concept A consistency. | Add a concept A regenerate-and-diff job, or stop citing CI as concept A evidence |
| F-13 | LOW | Gates audit (`2026-11-23-T099-gates.md`): §1 says "No concept A GLB exists" (false); §5 says REPORT.md was regenerated at 967 s, but the file reads 998 s and git shows no change. The E3d and E5 captions overstate what a_assembly checks (`a_assembly_blender.py:38`). | Correct the gates record and the two captions in `a_assembly_plan.py`; cite collide_a static coverage for the travel-0 steps |
| F-14 | LOW | Requirement roll-up lag (C-16) | Set R-INT-02 per T-035 (still open on T-034) and R-INT-03 to EXPLICITLY DEFERRED (AM-033) |
| F-15 | LOW | BOM tab header date and "+$-29.68" (`app.html:1258, 1266`) | Cosmetic fix in `sync_bom_a.py` |

## 7. Final verdict and what must happen before the 2026-12-15 go/no-go

Is this a coherent "final design with what we have now"? **On the engineering core, yes.**
- One configuration is drawn, priced and simulated at one mass.
- Every failing check is either named against a bench test with a numeric pass line, or accepted by a recorded decision (AM-011 mass, AM-016 stronger wing).
- No limit was relaxed in T-097 or T-098.

**As a published final, no.** F-1 leaves a pass/fail line undecided. F-2 leaves the named exported-model gate unpassed. F-3 to F-5 publish superseded results. F-6 makes the go/no-go date itself inconsistent.

**Before the go/no-go, $0 and paper:**
1. Close F-1 with a single ruling.
2. Run and close the concept A GLB gate (F-2).
3. Correct the published copy (F-3, F-4, F-9, F-10) and the film (F-5), then have the film re-reviewed.
4. Re-date or confirm the go/no-go against X2216 stock (F-6).
5. Put A-P6 at the predicted mass into the proof chain (F-7) and re-source the landing claim (F-8).

**Order and tests:**
6. Order 1: T-093 re-read 1-4 Dec (every line, X2216 stock, R15 landed price or vendor), BOM <= $2,000, Dillon's approval.
7. Go/no-go tests: TP-1 bench derate >= 0.889 at 1.913 kg (re-state at 1.881 kg) and one-motor current, and TP-2 Lua cap 1.0 +- 0.01 with the limiter holding <= 72 A. A failure reopens the configuration (AM-016).
8. Early, so the order buys the right pad (both are December items): TP-3 foam coupon against the D-243 region before any pad CAD change; the E1 damper coupon (flutter).

TP-10b (vibration and gain margin), TP-11 (stall), TP-15 to TP-18 (elevon linkage) and the weigh-in decide the remaining FAILs after the build. They do not gate 15 Dec, per D-236 and the TEST-PLAN.

### What the team must measure (for the go/no-go)
- M1 TP-1: thrust derate of one X2216 + APC 9x4.5MR on the stand. Fails A-P3 / the cruise need below 0.889 (T-083 line).
- M2 TP-2: Lua cap on the H743-Wing at each pack voltage. Fails below 1.0 +- 0.01, or if the limiter exceeds 72 A.
- M3 TP-3: foam plateau Fp (mean 2-18 mm) and damping zeta at 1.2 m/s. The landing fails outside Fp 37.5-39.0 N with zeta 0.02-0.05 (D-243).
- M4 Trunk: opening and floor of the team car. A-U3 fails if the 0.90 x 0.50 x 0.394 m box does not fit with props on.
