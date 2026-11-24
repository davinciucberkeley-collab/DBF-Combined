# Review round 7, 2026-11-23 (HEAD 0d0a2ccc): T-039 and T-094

Independent review. Reran: `python -I tools/ledger_audit.py` (0 errors; 94 tasks: 72 VERIFIED COMPLETE, 2 READY FOR REVIEW, 2 IN PROGRESS, 7 BLOCKED, 7 NOT STARTED, 4 DEFERRED), `python -I redesign/qp/A/bom_a.py` (total $1,939.17, margin $60.83, mass-gate line 1.881 kg), `python -I redesign/qp/A/proofs/run_all.py` (exit 1; 12 distinct STRICT claim FAILs, "fails 16" because the 4 A-P rows repeat; PROPOSED 20). Not rerun: the 3-D gates (quoted from `T092_report.md`: 66 steps, 129 parts, 0 blocked).

## Verdicts
| Row | Verdict |
|---|---|
| T-039 weekly status page | PASS WITH FIXES |
| T-094 TP-15..TP-18 | PASS WITH FIXES |

## T-039

Versions: the scratchpad `vtol-status.html` (current published) differs from `docs/status/weekly-2026-11-23.html` (older: "66 / 93", no TP-15..18 tile). So docs/status holds a stale copy.

Numbers checked on the current published version:
| Page item | Source | Result |
|---|---|---|
| Mass 1.881 kg EST, gate 1.47 kg missed | bom_a / run_all CL-A-MASS-PRED 1.881 vs 1.47 | OK |
| Cost $1,939 of $2,000, margin $60.83 | bom_a.py | OK |
| 3-D checks 129 parts, 66 steps, 0 clashes | T092_report.md l.17 | OK (not rerun) |
| Claims failing 12 | run_all, 12 distinct claim ids | OK |
| D-237 GM 1.13, FC 187 m/s2, limit 30 | CHANGE-LOG D-237 | OK |
| D-239 41 options, 95-109 Hz | D-239, T091_report s1 (41 candidates), D-237 (94.6-108.7 Hz) | OK |
| D-240 GM 2.5-4.0 vs 2.0, 5.6 g, exposed 0.597 m | D-239 (2.81 / 4.00 / 2.52), D-240 | OK |
| D-238 21 lines, $887.25, main $1,051.92 | ORDER-1.csv total 887.25; 1,939.17 - 887.25 = 1,051.92 | OK |
| Cleanup 3.55 GB | T043-T044.md l.42 | OK |
| Branch redesign/v1 not pushed | `git status -sb`: ahead 144 | OK |
| **71 / 94 verified complete** | ledger 72 | **STALE** |
| **3 ready for review** | ledger 2 (T-039, T-094) | **STALE** |
| Records "D-233 to D-240", rounds 4 and 5 | D-241 exists; rounds 6a/6b and 7 exist | stale |

Findings
- T-039-F1 (medium): the page says 71 / 94 and "3 ready for review"; the ledger says 72 and 2 (T-048 became VERIFIED). Fix: "72 / 94 ... 2 ready for review" and drop or reword "(updated after ... review round 6)".
- T-039-F2 (low): Records line stops at D-240 and round 5. Fix: "D-233 to D-241, docs/audits/2026-11-23-review-round-4.md to -7.md".
- T-039-F3 (low): the "bench tests added" tile says the foam-coupon tests "can run before the main order" using gear "we already have". That depends on T-094-F2 below; word it as "before the main order, with the foam, epoxy and linkage parts bought early" or "after the main order".
- T-039-F4 (process): `docs/status/weekly-2026-11-23.html` is not the published page. Fix: copy the corrected published version over it (it is the first-publish source; the row says "source docs/status/..."), and keep one file per week (later weeks add files, no overwrite). Yes, docs/status should hold the current version, because the ledger row names it as the source and an older copy there misstates the counts.
- Plain-words check: readable; no jargon left unexplained except "GM", "FC" and "TP-10b" (state: "gain margin", "flight controller", "tap test"). Low.
- Note outside T-039: stored claim CL-A-ASSY-STEPS reads 43 steps (READABLE.md l.4275-4290) while a_assembly and the build guide give 66; the page quotes 66, correctly, but the stored count is stale (margin shows 0 %). Not a T-039 defect.

## T-094

Checked: `T094_report.md`, `TEST-PLAN-O4B.md` l.312-327, `claims_a0_base.py` l.142-147, `claims_a2_struct.py` l.180-232, `BOM-A.csv`, `ORDER-1.csv`.

Passes:
- Each TP names its claim ids (TP-15 LINKAGE-FREEPLAY; TP-16 HORN-RIB-FOAM-HOLD / -STALL, HORN-BEARING-STALL; TP-17 ELEVON-TORSION-FOAM; TP-18 BEARING-STALL, FOAM-STALL plus the stall-bench and shear-out and keeper claims).
- Loads recomputed: 17.05 x 2.156 = 36.8 N; 0.397 / (8.5 mm x 0.916) = 51.0 N; 2.156 x 74.65 N mm = 0.161 N m; 0.161 / 0.009155 = 17.6 N. These match `claims_a2_struct.py` and `linkage_loads_check`. Pass criteria (<= 1 deg, 0.1 mm, set < 0.5 deg, 30 s / 5 s) match the claims' `how` text and `kit.claim` limits.
- G02 (10 kg cell + HX711 + caliper), G03 and T10 are BOM-A lines; dial gauge, 1.2 mm pin gauge, laser pointer are marked "-" and not bought (AM-030 respected). Timing is stated per test. Specimen order and n = 3 (lowest governs) stated.
- `claims_a0_base.py` l.142-147: the three new `kit.test` entries have state="planned". run_all failing set unchanged (same 12 STRICT; status line only PROPOSED 17 -> 20).

Findings
- T-094-F1 (high, wrong number): TP-15 l.317 uses the horn-hole radius "12.9 mm (`HORN_R`)" and a 0.225 mm limit. `HORN_R` is now 9.155 mm (`redesign/qp/A/cad/amodel/electrical.py` l.655; 12.9 was the superseded D-212 rev 1 geometry; TP-17 in the same section correctly uses 9.155 mm). At 9.155 mm, 1.0 deg is 9.155 x tan 1 deg = 0.160 mm. Using 0.225 mm would pass a 1.41 deg linkage and falsely pass a claim that has a 1.28 deg budget. Fix in TEST-PLAN l.317 and in `T094_report.md` l.8: replace "12.9 mm (`HORN_R`)" with "9.155 mm (`HORN_R`)" and "0.225 mm" with "0.160 mm", and say that the same limit scales as r x 0.01745 for a reading at the trailing edge (measure r from the hinge axis with the caliper). Also state that a +-0.05 mm gauge is 31 % of the 0.160 mm limit at the horn hole, so read at the trailing edge (larger r) where the 1 deg limit is a larger travel.
- T-094-F2 (medium, timing / equipment): TP-15(a), TP-16 and TP-17 are scheduled "before the main order" with "no purchase". Their specimens need parts that are in the main order, not in ORDER-1.csv: R01 foam (elevon foam), T4 / R05 epoxy, M02 pushrod and clevis set, M01 servo for TP-15 "servo ... powered", plus T10 lever-rig hardware (local, EST). Only G02, G03 and R03 (PETG) are in Order 1. Fix: either add a sentence "needs R01, R05 / T4, M02, T10 bought early; these are BOM lines (no extra cost) but move $X from the main order to Order 1", or move the timing to "after the main order" for those tests. Do not claim "gear we already have" for the specimens.
- T-094-F3 (low): TP-15(a) says "servo locked at neutral (powered and holding; horn clamped for (a))" but the claim `how` text measures with "the servo powered at neutral"; for the bench coupon there is no servo in the specimen list. State whether (a) includes a servo (M01) or is linkage only; (b) records both, which is right.
- T-094-F4 (low): the equipment line says loads are "each x (1 + u)" but the pass lines state bare loads (36.8 / 51 N). Say whether the applied load is raised by u (my reading: applied load = demand x (1 + u), pass criteria unchanged) so the lever-rig uncertainty cannot let an under-load pass.
- T-094-F5 (low): T-094 report l.14 says "the brief said 12 FAILs; the run reports 16 (the ERROR lines list some twice)". Precise: 12 distinct claim ids plus 4 A-P requirement rows (A-P1, A-D3, A-P10, A-P13). Reword.
- The ledger acceptance text says "4 of 12 run_all FAILs"; five claims are decided (TORSION-FOAM is the fifth). Update the T-094 row wording when the row is reconciled.

## Required before VERIFIED COMPLETE (caller)
T-039: F1, F2, F3, F4 (then republish; ledger "version 31" cannot be checked from here).
T-094: F1 (must), F2 (must), F3-F5 (should). run_all failing set unchanged after the fixes (text-only edits).
Neither row marked VERIFIED COMPLETE by this review.
