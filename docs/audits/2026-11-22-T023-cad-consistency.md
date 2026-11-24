# T-023 (R-CAD-06) independent CAD consistency review (2026-11-22, HEAD f4781329)

Reviewer: independent agent (wrote none of the files under review). Scope: the current aircraft after D-226 to D-231
(`redesign/params/CHANGE-LOG.md` l.934-938). Acceptance: "no unexplained inconsistency". Method: cheap `python -I`
cross-file diffs (scratch, nothing written into the repo except this file). The 3-D gates (`collide.py`,
`assembly_check.py`) were not rerun; their status is read from `cad/out/REPORT.md` and D-229 (PASS, 129 / 129).

## Verdict

**FAIL: the CAD is not consistent with the rest of the A files. 4 Major findings (F-1, F-2, F-3, F-5) are unexplained and must be fixed
before T-023 can close.** None is a geometry error in the 3-D gates; they are stale generated outputs (parts list,
`params-A.json`), a stale hub material and stock line, and a wrong exposed-wire figure in a report. Minor items are
listed after the Major ones. Mass, CG, motor, pack and fin-root-fitting numbers agree across files (section "Agreed").

## Checks run

| # | Check | Result |
|---|---|---|
| C1 | `parts-a.csv` ids vs `assembly.json` step parts | 131 rows vs 129 parts placed. The two not placed are `HRD-001` (hardware lot) and `HRN-001` (wire lot): non-geometric aggregates, matches D-229 "129 / 129". Explained |
| C2 | `parts-a.csv` made parts vs `DRAWINGS-A.md` | Every made part with geometry has a drawing (49 sheet rows). Nothing missing |
| C3 | `parts-a.csv` BOM references (`BOM Pxx`) vs `BOM-A.csv` ids | All referenced ids exist. But the vendor, URL and "not in BOM-A" text is stale (F-1) |
| C4 | `printed_mass.json` (34 parts, 121.24 g) vs the print list in `DRAWINGS-A.md` | Masses agree to 0.01 g for the 34 shared parts. `WNG-009-L/R` (PETG + silicone, 2.0 g) are in the print list but not in `printed_mass.json` (F-9) |
| C5 | `sitl/cad_mass.json` vs `MASS-GATE.md` s15 vs `params-A.json` mass | 1.6275 kg, CG 21.08 mm: agree with s15 "T-083b as drawn" and `mass.basic_cad_kg` 1.6275. The tallied 1,634.5 g / CG 22.26 mm differs by +7.0 g shoe cups (EST), stated in s15 and D-229. Explained |
| C6 | `BOM-A.csv` vs `bom_a.py` vs `params-A.json` cost block | `python -I redesign/qp/A/bom_a.py`: total $1,981.31, reserve $346.94, margin +$18.69 (matches D-230, AM-019). `params-A.json` `cost.bom_rows` does not (F-3) |
| C7 | `wire_inventory.json` vs exposed-wire list in T083b_report s7 | Inventory sum of exposed_m x strands = 0.5975 strand-m, equals the 0.597 in D-229. The s7 breakdown of E-HRN-13 is wrong by 2x (F-5) |
| C8 | Stale-name grep (MN2212, Tattu, F405, T-Motor, X7 node, clamshell, PETG root block) over `amodel/*.py`, `a_build_steps.py`, `a_assembly_plan.py`, `parts-a.csv`, `params-A.json`, `BUILD-GUIDE-A.md`, `DRAWINGS-A.md`, `sitl/cad_mass.json` | Live hits listed in F-1, F-2, F-3, F-8, F-10. Comment-only "Was: MN2212" notes in `propulsion.py`, `wing.py`, `electrical.py`, `common.py` are history notes, not stale data |

## Findings

| ID | Severity | Finding | Files and lines | Explained? | Required fix |
|---|---|---|---|---|---|
| F-1 | **Major** | `parts-a.csv` still names the withdrawn purchases. 12 rows (PRP-001-x, PRP-004-x, PRP-006-x; lines 66-86) cite BOM `P01 TMotor` and the T-Motor MN2212-V20 URL (`store.tmotor.com/goods-388-MN2212-V20.html`). `BOM-A.csv` P01 is the SunnySky X2216 V3 880KV short shaft, ship group RMRC. `PWR-001` (line 87) cites the Tattu 2300 URL; `BOM-A.csv` W01 is the RDQ 2800 mAh pack. `AVN-002` (line 91) cites the Kakute F405 Wing Mini URL; V03 is the Kakute H743-Wing ($129.01). Notes "not in BOM-A" on FIN-002 (R15), FIN-003 (T11), FIN-005 (T2), CGE-006 (T11) (lines 28, 29, 31, 64) and "BOM line and price: -" on CGE-005 (R10 8x6 $8.50 is now in the BOM) are false since D-230 | `redesign/qp/A/cad/out/parts-a.csv` l.28, 29, 31, 36, 37, 39, 60, 64, 66-86, 87, 91; `BOM-A.csv` P01, W01, V03, R10, R15, T2, T11 | **No.** D-230 says the BOM was replaced wholesale and the build guide regenerated; it does not mention `parts-a.csv`, which was generated at 2026-11-21 23:19, before the BOM adoption | Run `parts_links_a.py` (parts_links gate) after the BOM change; commit the new `parts-a.csv`. Check the URL, ship group and "not in BOM-A" text per row |
| F-2 | **Major** | Hub CGE-001 is a printed PETG part in four live places and a machined 6061-T6 part in the CAD. `wing.py` l.961 and `DRAWINGS-A.md` (Al 6061-T6, machined, 59.5 x 107.8 x 49.3 mm) say machined (D-220 / D-221 / D-222). `parts-a.csv` l.43 says "Made (printed PETG) from BOM R03 Prusa ... the printed hub stands on the bench". `a_assembly_plan.py` l.26 caption "the printed hub". `BUILD-GUIDE-A.md` l.205 caption, l.215 and l.662 parts table "made, R03 Amazon, 43.3 g" (PETG source for an aluminium part). **Stock does not fit:** the bar bought is BOM T1 6061-T6511 **1.75 x 2.5 in** (cross-section 44.45 x 63.5 mm); the drawing bbox needs 59.5 x 49.3 across the section (49.3 > 44.45), and the build guide l.221 asks for a 63.5 x 63.5 x 50.8 mm blank (a 2 in thickness). The test-plan note (T1 "hub block about 60 x 110 x 42 mm") predates the D-222 hub, which is 49.3 mm deep | `parts-a.csv` l.43; `cad/a_assembly_plan.py` l.26; `BUILD-GUIDE-A.md` l.205, 215, 221, 662; `amodel/wing.py` l.961; `drawings/out/DRAWINGS-A.md` CGE-001 row; `BOM-A.csv` T1 | **No.** D-220..D-222 explain the aluminium hub; nothing explains the PETG source text or the 1.75 in bar. T-082 line L6 chose 1.75 x 2.5 in on the 60 x 110 x 42 hub | (a) Fix the plan caption, parts source (T1, not R03) and guide text. (b) Check the hub bbox against the bar: either change T1 to a bar at least 50.8 mm (2 in) thick (the 2 x 2.5 in price is not read), or re-orient and confirm 49.3 mm fits in 44.45 mm (it cannot as written). The T1 bar also supplies FIN-003 and CGE-006 blanks, so re-check that stock budget |
| F-3 | **Major** | `params-A.json` is stale on cost and the pack note. `cost.bom_rows` has P01 TMotor 5 x $46.90, V03 $95.98 (F405), W01 37.09, R03 Prusa $23.99, B01/B02/B05 rows, and no T1-T12, R15, W10 rows; 12 of the common rows differ from `BOM-A.csv` (P01, V03, W01, R01, R03, R05, R09, R10, R14, G02, G05, W07). `cost.ship_usd` still has TMotor and SparkFun groups. `pack_g` note (l.389) says "Tattu 2300 4S" (the 270 g value is right, the note is wrong). `params-A.json` feeds the claim scripts (G7 budget claim) | `redesign/qp/A/params-A.json` cost block, l.389; `proofs/gen_params_a.py` | **No.** MASS-GATE s13 already flagged stale params-A and said to regenerate; D-230 adopted the BOM without regenerating this file (generated 2026-11-21 23:19:50) | Rerun `proofs/gen_params_a.py` and the claims (`run_all.py`) once, then commit; confirm the G7 claim matches `bom_a.py` ($1,981.31, +30 % total $2,087.53) |
| F-4 | Minor | `MASS-GATE.md` s15 last line says "`BOM-A.csv` itself was not updated (see `T083c_changes.md`)". D-230 replaced `BOM-A.csv` and `bom_a.py` the same day | `MASS-GATE.md` l.209-210; CHANGE-LOG D-230 | Partly: D-230 explains the change; the s15 text is now false | Replace by "BOM-A.csv adopted $1,981.31 (D-230)" |
| F-5 | **Major** | Exposed-wire list disagrees with `wire_inventory.json`. T083b_report s7 says E-HRN-13 (pack power leads) is "0.133 -> 0.127 strand-m (2 x about 64 mm)". The inventory has E-HRN-13 2 strands x 126.6 mm = **0.253 strand-m**. Only 0.253 makes the listed items sum to the stated total 0.597 (all items: 0.001 + 0.085 + 0.253 + 0.064 + 4 phase edges 0.105 + servo 0.071 + HRN-10 0.019 = 0.5975). The CLAUDE.md rule needs each exposed length and reason; the largest item (42 % of the total) is mis-stated by 2x. Also the exposed run (126.6 mm) exceeds the 80 mm RDQ lead, so a 46.6 mm extension per strand is needed (T077_cad.md l.18, 106-109 names it as "W10 pack lead extension", not drawn); `BOM-A.csv` W10 is now the XT90 pigtail set, and no BOM or build-guide step names the extension | `mechanism/out/T083b_report.md` l.120; `cad/out/wire_inventory.json` E-HRN-13; `mechanism/out/T077_cad.md` l.18, 59, 106-109; `BOM-A.csv` W10; `BUILD-GUIDE-A.md` l.2167 | **No** (the s7 number is a transcription error; the W10 name clash is unexplained) | Correct s7 (E-HRN-13 0.253 strand-m, 2 x 126.6 mm, reason: the pack must come out of the tray); add the lead extension (length, 14 AWG from W05, solder splice and heat-shrink) to the build guide step E4a and the exposed-wire list |
| F-6 | Minor | `parts-a.csv` has no vendor or process mapping for `WNG-011` (glass skin) and `WNG-012` (cove CF strip): "— (not mapped)" (l.3, 4). The BOM now has T3 (1080 glass), T4 (epoxy), T5 (CF strip) | `parts-a.csv` l.3-4; `cad/parts_links_a.py` l.79; `BOM-A.csv` T3, T4, T5 | No | Map the two parts to T3 + T4 and T5 in `parts_links_a.py` |
| F-7 | Minor | `GER-002` foot pad is listed in `parts-a.csv` as made from `R03 Prusa` (PETG, "foot pads (BOM R03 line text)"); `DRAWINGS-A.md` has it as EVA / PE foam (D-222 pad; BOM T7 EVA, T8 PE) | `parts-a.csv` l.123 (GER-002-UR..LL); `DRAWINGS-A.md` GER-002 row; `BOM-A.csv` T7, T8 | No | Map GER-002 to T7/T8 |
| F-8 | Minor | Stale motor-box text in the build guide: l.2306 "named in ARMS.md ... check whether the T-Motor box includes them" for M2.5x8 motor screws. The X2216 uses the supplied X-mount with M3 screws (`propulsion.py` PRP-006; BOM R05). `AVN-002` row shows "price -" (l.1955) while V03 is $129.01 | `BUILD-GUIDE-A.md` l.1955, 2306 | No | Regenerate the guide after F-1; remove the T-Motor line |
| F-9 | Minor | `WNG-009-L/R` (2.0 g each) are in the print list but not in `printed_mass.json`; their mass comes from the CAD part table, not the T-067 basis. `DRAWINGS-A.md` AVN-010 shows "14 pieces: CHECK (a body is not attached)": by design (4 FC + 4 ESC + 4 GPS bosses + 2 RX pads), but the flag will read as a defect | `printed_mass.json`; `DRAWINGS-A.md` print list | Partly (design intent in `electrical.py` l.734) | Note in `printed_mass.json` or the mass-gate why WNG-009 is outside it; tell the drawing tool that AVN-010 is a multi-body part |
| F-10 | Minor | Stale stamps: `DRAWINGS-A.md` header "commit b21947ed" but FIN-003 is the D-229 (ac983050) 6061 fitting. CLAUDE.md header still gives "predicted 1.64 kg" (MASS-GATE s15 says superseded: 1.873 kg EST). `electrical.py` l.602 comment (I2C groove) cites the withdrawn CF clamshell cradle (D-221). Dead clamshell code in `wing.py` (flag `P5_CLAMSHELL = False`, l.94) is labelled as withdrawn D-225/D-226 | `drawings/out/DRAWINGS-A.md` l.3; `CLAUDE.md` l.28; `amodel/electrical.py` l.602 | Dead code: yes (D-225/D-226). Others: no | Regenerate the drawings; update the CLAUDE.md line (reviewer cannot edit it here); update the comment |

## Agreed (no inconsistency found)

- Motor: `propulsion.py` models the X2216 V3 short shaft from the SunnySky drawing (can 27.7 x 32, shaft 3.175, X-mount 34/41 mm, adapter flange 17 x 4); 67.5 g in MASS-GATE s15 and `parts-a`; KV 880, Rm 89 mohm in `params-A.json` (D-227, D-228). Not re-read against the vendor image (not fetched); the code comments cite the drawing values per dimension.
- Pack: `params-A.json` `mission.pack_ah` 2.8, RDQ note; `electrical.py` l.548 lead 80 mm (RDQ).
- FIN-003 6061 fitting: ring OD 18.2 / bore 16.2 x 38, plug 22.8 / 20.8 x 31, 12.04 g (D-229, MASS-GATE s15) agrees; drawing 48.1 x 24.6 x 38.0.
- BOM $1,981.31 (D-230, AM-019) reproduced by `python -I redesign/qp/A/bom_a.py`.
- Predicted 1.873 kg (tallied 1,634.5 g; 1,627.5 g drawn; CG 22.26 / 21.08 mm) consistent between s15, D-229 and `cad_mass.json`.

## Not checked

- No 3-D gate was rerun. Vendor drawings and web pages (SunnySky, RDQ, Holybro) were not re-fetched.
- Whether each vendor part's every dimension matches its drawing (props, FC, ESC, servos, connectors): spot-checked the motor only.
- `BUILD-GUIDE-A.md` was grep-checked for stale names, not read in full (2,316 lines).

## What must be fixed for PASS

F-1, F-2, F-3, F-5 (all Major), then F-4, F-6 to F-10. After the regeneration (parts links, params, drawings, build guide), rerun this diff and the
ledger audit. No Critical finding.

Sources: `redesign/qp/A/cad/out/parts-a.csv`, `assembly.json`, `wire_inventory.json`; `sitl/cad_mass.json`; `cad/amodel/*.py`;
`BOM-A.csv`, `bom_a.py`; `MASS-GATE.md` s15; `drawings/out/DRAWINGS-A.md`; `BUILD-GUIDE-A.md`; `params-A.json`;
`mechanism/out/T083b_report.md`; `redesign/params/CHANGE-LOG.md` D-226 to D-231.
