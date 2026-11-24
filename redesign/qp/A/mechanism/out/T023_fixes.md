# T-023 / T-081 review fixes (2026-11-22, HEAD f4781329)

Category: documentation and data-label fixes (no geometry, no analysis). Basis: D-226..D-231, `BOM-A.csv` / `bom_a.py` ($1,981.31, margin +$18.69, re-run today), T083 / T083b reports. Nothing committed. Not edited: `structures/`, `proofs/`, ledger, spec-amendments, MASTER spec, CHANGE-LOG, `BOM-A.csv`, `CLAUDE.md`.

Gates not re-run: no geometry, mass or wire route changed (only text, labels, a code comment), so the full CAD build was not needed. `cad/out/REPORT.md` still reads PASS (583 bodies, 129 parts, wire ends 0), as generated before these edits. Caveat: the `a_assembly_plan.py` step B0b caption wording changed ("printed" -> "machined"); `cad/out/_plan.json` / `assembly.json` still carry the old caption until the next assembly run (label only).

## Review 1: T-023 CAD consistency

| ID | Status | How fixed / why not |
|---|---|---|
| F-1 | FIXED | Generator `cad/parts_links_a.py` MAP corrected (CGE-005 -> R10; CGE-006 / FIN-003 -> T11; FIN-002 -> R15; FIN-005 -> T2, T3, T12; FIN-009, WNG-013 -> T2, T3; WNG-014 -> T3, T4; "not in BOM-A" text removed) and regenerated with `python -I redesign/qp/A/cad/parts_links_a.py` (131 parts, 106 vendor links). The 12 PRP rows, PWR-001 and AVN-002 now read from current `BOM-A.csv` (SunnySky X2216 RMRC, RDQ 2800, Kakute H743-Wing); grep for T-Motor / tmotor in `parts-a.csv`: 0 hits. |
| F-2 | FIXED, ONE OPEN PURCHASE ITEM | Plan caption B0b ("printed hub" -> "machined hub"), `parts-a.csv` CGE-001 (now machined 6061-T6, BOM T1, not R03), build-step need line (`a_build_steps.py`) and the regenerated `BUILD-GUIDE-A.md` (parts table, caption) corrected. **Engineering choice:** the drawn hub bbox is 59.5 x 107.8 x 49.3 mm (`DRAWINGS-A.md`); no orientation fits the T1 bar section 44.45 x 63.5 mm (49.3 > 44.45), and T11 is 25.4 mm thick. The hub needs a 2.00 x 2.50 in (50.8 x 63.5 mm) bar; the build guide now says so with a blank of at least 63.5 x 50.8 x 110 mm (replaces the 63.5 x 63.5 x 50.8 blank). `BOM-A.csv` T1 was NOT changed (it sets the $1,981.31): the Alcobra 2 x 2.5 in page (read 2026-11-22) shows only $65.56 as the minimum over all lengths, no 12 in price, so the BOM impact is up to about +$16 (EST) against a margin of +$18.69. The BOM line change and price lookup remain for the owner of `BOM-A.csv` (money decision). FIN-003 / CGE-006 blanks come from T11 and are unaffected. |
| F-3 | PARTLY FIXED, BLOCKED | `python -I redesign/qp/A/proofs/gen_params_a.py` re-run: `params-A.json` `cost.bom_rows` now equals `BOM-A.csv` (P01 4 x $22.99 RMRC, W01 RDQ x2, V03 $129.01, R15, T1..T12, W10; B01/B02/B05 gone). Still stale and not fixable here because the generator is in `proofs/` (another agent): `ship_usd` is hard-coded in `gen_params_a.py` l.268 (TMotor / SparkFun groups; `bom_a.py` SHIP has RDQ, Alcobra, Wicks, USComposites, Carbonwebshop) and the `pack_g` note l.104 says "Tattu 2300 4S". `claims_a3_program.py` `bom_cost` does `sh[g]` for every group in the rows, so with the new rows it will raise KeyError for "RDQ" until `ship_usd` is read from `bom_a.SHIP`. `run_all.py` was NOT run (would hit this); G7 claim not re-confirmed. Needed edit for the proofs owner: `ship_usd` from `bom_a.SHIP`, note text "RDQ 2800 mAh 4S, 270 g", and `claims_a3_program.py` reserve term `sh["TMotor"]` (bom_a.py `reserve()` is the reference). |
| F-4 | FIXED | `MASS-GATE.md` s15 last line now says BOM-A.csv was replaced in D-230 and carries $1,981.31. |
| F-5 | FIXED | `T083b_report.md` s7: E-HRN-13 stated as 0.253 strand-m (2 x 126.6 mm, `wire_inventory.json`), transcription error noted. Extension added to the build steps (`a_build_steps.py` E4a need line and E4b fit line, guide regenerated): 46.6 mm per strand beyond the 80 mm RDQ lead, EST 50 mm of 14 AWG from W05 (no extra purchase), 2 solder splices with 3 mm heat-shrink; not drawn (the CAD draws the full 126.6 mm run). The name clash is resolved by calling it "pack lead extension (W05 stock)"; W10 stays the XT90 pigtails. The exposed-wire total 0.597 is unchanged (D-229). |
| F-6 | FIXED | WNG-011 -> T3 + T4, WNG-012 -> T5 + T4 in the MAP. |
| F-7 | FIXED | GER-002 -> T7 / T8 (EVA or PE foam per TP-3). |
| F-8 | FIXED | Build-guide open item rewritten (X2216 X-mount, M3 screws, R05); AVN-002 "price -" now "$129.01". |
| F-9 | NOT FIXED | Adding WNG-009 to `cad/amodel/printed_mass.json` would change the T-067 mass basis (an engineering choice, not a label). Left as the review's "partly explained" item; AVN-010 multi-body CHECK flag is a drawing-tool change, not touched. |
| F-10 | PARTLY | Comment in `amodel/electrical.py` l.602 now says the clamshell cradle is withdrawn (comment only). NOT done: `DRAWINGS-A.md` header commit stamp (needs the drawing regeneration, not run) and the `CLAUDE.md` "predicted 1.64 kg" line (project instructions, not edited). |

## Review 2: T-081 re-check (TEST-PLAN-O4B.md)

| Gap | Status | Fix |
|---|---|---|
| G-1 rib torsion coupon | FIXED | New row TP-12 (14x12 offcut, n = 5 proposal, T-082 lever rig, 10 kg cell, thin-wall tau formula). Pass: >= about 92 MPa at zeta 0.02 (T083_report s10, EST; 99 MPa all zeta). Zeta 0.05 line: "—" (no report value). Fail: keep 25x23. The 14x12 + 6061 fitting case is stated as not computed. |
| G-2 rib-bulkhead bond | FIXED | New row TP-13. Pass: min of 5 >= 2.21 MPa (L 99.5) or >= 1.73 MPa (L 113) (saddle-loadpath s3 l.98); wrap as the adopted fix on fail. Margin beyond x2.23: "—". 25x23 recomputation: "—". |
| G-3 socket bearing | FIXED | New row TP-14. Pass: CF wall bearing >= 48.5 MPa (saddle-loadpath s3 l.104); allowable "—" (the test sets it); CF plate shear / bearing allowables "—". |
| G-4 budget total | FIXED | "Adopted total $1,981.31, reserve $346.94, margin +$18.69" paragraph added at the top of the Budget-closed section with the lines that moved it; s0 row 4 and s4.1 marked SUPERSEDED. |
| G-5 withdrawn / MN2212 items | FIXED | Tags added: TP-7 row (C-4 WITHDRAWN D-225 / D-226), T2 purchase line (N2, C-4 withdrawn; FIN-005 now the waterjet bulkheads), TP-1 "flight MN2212 spare" (superseded by X2216, AM-019), TP-6 / TP-7 "same rig" (TP-6 withdrawn). |

Numbers for TP-12..14 come only from T083_report s4 / s10 and saddle-loadpath s3; n = 5 and the rig are proposals (labelled). TP-12..14 ids are new in this file and are not yet in `docs/requirements.md` / ledger (not edited here).

## Verification run
- `python -I redesign/qp/A/cad/parts_links_a.py`: 131 parts, 106 with vendor link, 0 with no link; no T-Motor text.
- `python -I redesign/qp/A/make_build_guide_a.py`: 2,317 lines, 66 steps.
- `python -I redesign/qp/A/bom_a.py`: unchanged $1,981.31 / margin +$18.69 (BOM untouched).
- `python -I tools/ledger_audit.py`: 109 requirements, 83 tasks, 0 errors.
