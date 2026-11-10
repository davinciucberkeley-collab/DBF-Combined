# Pod structures — K09-L

Owner C3 (pod structures; the fuselage role re-scoped by A1). Revision **C3-R2**, 2026-11-09, against params A1-R4
(D-47: nose −0.130 m, pod 0.225 × 0.14 × 0.07 m), C1 loads (`team/C1/data/joints.csv`), D2's pod at D2-R5, the D-47 re-lay
(`subsystems/pod/params.json`) and C6's pod allowables (CR-C6-16). Re-run in < 1 s:
`python -I redesign/team/C3/pod_structures.py`, then `python -I redesign/proofs/build_graph.py`. The build reports no
C3 errors. C6's `CALC-C6-POD-ALLOW` drifts until C6 re-runs (CR-C3-11). Every number below is in `claims.json`
(`CL-C3-…`) or `out/results.json`.

Status: the calculations are `CHECKED` (closed-form, hand-reproducible). Every allowable is an `UNVERIFIED`
estimate until the tests in section 6 have run, so every margin is `UNVERIFIED`.

R2 changes: re-pointed at D2's R4 keys (`stop_wall_h_m` retired → `fwd_stop_m[1]`, `aft_stop_m[1]`,
`pod.size_m[1]`); allowables read from C6's nodes; floor glue checked with C6's corner fillet; new
`CALC-C3-NOSE-PATH` for the D-47 nose; the full-section forward stop (CR-C5-13) decided; the hatch re-sized for the
longer nose.

## 1. Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| Does the pod-to-wing bond hold? | **Yes.** x 0 … 0.065 m × 0.140 m on bare XPS. Worst design case L2 pair-first landing, narrow (MC-C): interaction 0.886 | `CL-C3-BOND-R-DESIGN` | +11 % `UNVERIFIED` |
| Does it hold the pod group in a 12.75 g crash? | **Yes.** 0.954 kg × 12.75 g = 119 N, worst direction +z (peel): interaction 0.72 | `CL-C3-BOND-R-CRASH` | +28 % `UNVERIFIED` |
| Aft stop 3.0 mm, 27 mm tall, on the tray rear piece at x 0.056 (pack +x) | Passes: 14.0 vs 15 MPa across the layers (gussets ignored), needs 2.90 mm; 86 N design vs 417 N piece bond (D2) | `CL-C3-AFT-STOP-D2`, `-BOND`, `-T-REQ` | +7 % / +80 % `UNVERIFIED` |
| Forward stop 3.0 × 25 × 54 mm (pack −x) | Passes: 12.9 MPa; root holds 99 N vs 85 N crash | `CL-C3-FWD-STOP-REC`, `-FUSE` | +14 % / +16 % |
| Does the D-47 nose (stack 8.8 mm) keep the crush path? | **Yes.** Block A falls to 1.0 mm and ≤ 4 % of the nose-in energy; block B carries the path. 1 mm of XPS is not buildable; D2-R5 made it a 1 mm epoxy bond line (CR-C3-08, closed) | `CL-C3-NOSE-BLOCK-A`, `-NOSE-STACK`, `CL-C3-BLOCK-A-SHARE` | +59 % `UNVERIFIED` |
| Full-section forward stop (CR-C5-13)? | **No.** Worth 0.56 mm of block B at D-47 (3.9 mm at R4), costs 6.3 g and would take the pod to 137.2 vs 130.9 g | `CL-C3-STOP-SECTION-PENALTY`, `CL-C3-POD-MASS-FULL-STOP` | +44 % |
| Guides 1.5 mm (pack ±y) | Pass: 6.5 MPa | `CL-C3-GUIDE-D2` | +57 % |
| Straps (pack +z) | Pass: leg 31 N vs 100 N; overlap ≥ 50 mm (31 mm needed) | `CL-C3-STRAP-LEG`, `-OVERLAP-REQ` | +69 % / +38 % |
| Tray-to-floor flat-wise (C6 50 kPa) | Passes: 19.3 kPa | `CL-C3-TRAY-FLAT` | +61 % |
| Floor-to-wall glue under the front strap (C6 100 kPa) | 110.7 kPa on the board edge alone; **49.2 kPa with the 6 mm corner fillet** (D2 has it) | `CL-C3-FLOOR-GLUE`, `-FILLET` | +51 % |
| Overhang ahead of the LE (pack at −0.024, most forward with block B) | Passes: 7.7 MPa crash vs 10 MPa; 4.4 MPa design. With block B left out (−0.051) the crash case fails (11.9 MPa): block B is a no-fly item | `CL-C3-OVERHANG-CRASH`, `-DESIGN` | +23 % / +56 % |
| Carry handle on the spar (G1) | Passes: 110 N design vs 2 ties 444 N; grip 9.9 MPa along the raster | `CL-C3-HANDLE-TIES`, `CL-C3-GRIP` | +75 % / +60 % |
| Hatch at VD suction (185 mm hatch after D-47) | Passes: 12 × 40 mm tab 2.11 vs 2.5 N/cm² at C1's q 453 Pa | `CL-C3-HATCH-TAB` | +16 % |
| Mass | D2-R5 130.9 g already holds the C3 sizes (Δ 0 g) vs 131 g | `CL-C3-POD-MASS-REC` | 0 % |

## 2. Load path

Frame x aft, y right, z up in cruise; in hover +x points at the ground. One path per pack direction. Nothing relies
on the hatch.

| Pack load | Link 1 | Link 2 | Link 3 | To the wing |
|---|---|---|---|---|
| +x (hover landing, fin-tip fall) | aft stop 3.0 mm + 2 gussets on the tray rear piece (x 0.056) | rear piece bond (417 N, `CL-D2-AFT-STOP-BOND`) | foam-board floor | pod-to-wing bond |
| −x, airframe decelerates (≤ 85 N) | forward stop 3.0 mm (root fillet, solid tray front) | tray front piece bond (182 N, `CL-D2-FWD-STOP-BOND`) + epoxy bond line to the nose wall | floor, side walls | pod-to-wing bond |
| −x, nose-in impact (D-47) | spreader 1.5 mm (full section) | block B crushes (≤ 509 N) | forward stop + 1 mm bond line | nose wall, backed by the ground |
| ±y | guide 1.5 mm PETG | tray floor | tray-to-floor epoxy | bond |
| +z (push-over, crash up) | 2 straps, 4 legs | strap under the tray | tray-to-floor (flat-wise); front strap: floor-to-wall glue + 6 mm fillet | bond (peel) |
| −z (pull-up, crash down) | tray bearing | foam-board floor | overhang: 2 side walls to x 0 | bond (bearing) |
| Lift by the handle | grip | 2 legs | 2 feet + 2 nylon ties | spar |

Nose-in: block B's crush force (509 N, worst pack) is five times the forward stop's root capacity. The stop and nose
wall react it only because the ground is behind the nose wall in the impact block B is designed for. In every other
crash direction the pack load is ≤ 85 N (12.75 g) and the stop holds it. With block A at 1 mm the stop no longer has to
fuse and ride forward. It is bonded to the nose wall instead (D2-R5, CR-C3-08).

## 3. Loads and factors

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod-group joint loads, envelope rows (F, H, T, L, G; MC-C, MC-P) | 6 components at C1's point | N, N·m | `ASM-C3-POD-LOADS` ← J-POD | `UNVERIFIED` |
| Pack-to-tray loads | Fx +41.4 / −0.9, Fy +5.9 / −10.9, Fz +10.4 / −21.2 (limit) | N | `ASM-C3-PACK-LOADS` ← J-PACK | `UNVERIFIED` |
| Design factor | 1.5 × 1.15 × 1.25 = 2.16 | — | `P:requirements.safety_factor_ult`, `ASM-C1-*-FACTOR` | `PROPOSED` |
| Crash, ultimate | n 12.75; pack 85 N any axis; pod group 0.954 kg → 119 N | —, N | `CL-C1-CRASH-N`, `CL-C1-PACK-CRASH-LOAD`, `CL-C3-POD-GROUP-MASS` | `UNVERIFIED` |
| Nose-in crash (C5) | 5 m/s, pack ≤ 100 g, XPS plateau 172 kPa | m/s, —, Pa | `ASM-C1-CRASH-V`, `ASM-C5-PACK-G-MAX`, `ASM-D5-XPS-PLATEAU` | `UNVERIFIED` |
| q at VD | 454 | Pa | `CL-C1-Q-VD` | `UNVERIFIED` |

## 4. Materials and allowables (C6 values, CR-C6-16)

| Material | Use | Allowable | Value | Source | Status |
|---|---|---|---|---|---|
| XPS F-250 + epoxy | pod-to-wing bond | tension / shear | 100 / 100 kPa | `ASM-D2-XPS-ALLOW` (C6 125, kept), `CL-C3-ALLOW-XPS-SHEAR` | `UNVERIFIED` |
| Board + epoxy | floor-to-wall, bond paper face | shear on the paper face | 100 kPa | `CL-C3-ALLOW-PAPER-SHEAR` | `UNVERIFIED` |
| Board | tray-to-floor | flat-wise | **50 kPa** (was 100) | `CL-C3-ALLOW-BOARD-FLAT` | `UNVERIFIED` |
| Paper-faced board 4.8 mm | walls, floor, nose | face stress | 10 MPa, face 0.10 mm | `ASM-C4-FACE-*` | `UNVERIFIED` |
| Printed PETG across layers | stops, guides | tension | 15 MPa | `ASM-C4-PETG-TENSILE` | `UNVERIFIED` |
| Printed PETG along raster | handle grip | bending | 25 MPa | `ASM-C3-PETG-INPLANE` | `UNVERIFIED` |
| Hook-and-loop | straps, hatch tab | shear / flat-wise | 5 / 2.5 N/cm² | `ASM-C3-HL` | `UNVERIFIED` |
| Nylon tie 7.6 mm | handle to spar | rating | 222 N each | `ASM-D2-TIE-CAP` | `UNVERIFIED` |

Epoxy for every structural joint; hot glue only for trim.

## 5. Sizing for D2 (R2)

| Item | D2-R5 | C3 R2 | Margin | Why |
|---|---|---|---|---|
| Aft stop (`POD-002` rear piece) | 3.0 mm, top 27 mm, 2 gussets, x 0.056 | accepted (CR-C3-10 closed); push test on the built rear piece | +7 % | 86 N design |
| Forward stop (`POD-002`) | 3.0 × 25 × 54 mm, 1 mm bond line to the nose wall | accepted (CR-C3-08 closed) | +14 % | D-47 leaves 1 mm |
| Full-section forward stop | — | **not adopted** (CR-C5-13) | — | 0.56 mm for 6.3 g |
| Guides | 1.5 × 8 mm | unchanged | +57 % | — |
| Straps | 2 × 20 mm, 50 mm overlap | unchanged | +38 % | — |
| Floor-to-wall corners | 6 mm fillets ± 30 mm of each strap | unchanged (required) | +51 % | RF 0.90 without |
| Hatch tab (`POD-003`) | 12 × 40 mm | unchanged (CR-C3-09 withdrawn) | +16 % | 185 mm hatch |
| Side walls | 4.8 mm board | no cut-out between x −0.06 and +0.02; F2's side exits (x 0.056–0.072) are aft of it | +14 % | compression flange of the overhang |

## 6. Tests that turn the margins `VERIFIED`

| Test | What | Verifies |
|---|---|---|
| `T-C3-BOND-COUPON` | epoxy on F-250 and on board: flat-wise pulls, lap shears; mean − 2 s | bond, tray, glue-line claims |
| `T-C3-STOP-PUSH` | tray offcut, 3.0 mm stops, 1.5 mm guides: 90 N at 13 mm height, 85 N along a guide, then to failure | stops, guides, fuse |
| `T-C3-POD-PROOF` | built pod on the wing, 680 g dummy pack: down 64 N, up 85 N, aft 85 N, sideways 85 N, 10 s | bond crash, overhang, glue lines |

Plus `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-D2-WEIGH`, C6's `T-C6-BOARD-CORNER`, C5's block coupon.

## 7. Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Block B (`POD-008`) is now structural for the overhang: left out, the pack can sit at −0.051 and the overhang crash check fails (−19 %). Pre-flight card no-fly item (CR-C3-13) | H3, D2 |
| 2 | Aft stop margin +7 % rests on 15 MPa across layers; `T-C3-STOP-PUSH` decides | C3, H1 |
| 3 | Bond design margin +11 % (C1's new L2 pair-first case governs) rests on the 100 kPa XPS tension estimate; `T-C3-BOND-COUPON` | C6, H1 |
| 4 | C6 drift (CR-C3-11); C5's `CALC-C5-CRASH` fails in the build on its own inputs (CR-C3-12) | C6, C5 |

## 8. Calculation index

| Calc | Claims |
|---|---|
| `CALC-C3-ALLOW` | `CL-C3-ALLOW-XPS-SHEAR`, `-PAPER-SHEAR`, `-BOARD-FLAT` |
| `CALC-C3-BOND` | `CL-C3-BOND-R-DESIGN`, `-SIGMA-DESIGN`, `-R-CRASH`, `CL-C3-POD-GROUP-MASS` |
| `CALC-C3-STOPS` | `CL-C3-AFT-STOP-D2`, `-BOND`, `-T-REQ`, `-REC`, `CL-C3-FWD-STOP-REC`, `-FUSE`, `CL-C3-NOSE-WALL-M` (reference) |
| `CALC-C3-GUIDES`, `-STRAPS` | `CL-C3-GUIDE-*`, `CL-C3-STRAP-*`, `CL-C3-TRAY-FLAT`, `CL-C3-FLOOR-GLUE` (reference), `-FILLET` |
| `CALC-C3-OVERHANG`, `-HANDLE`, `-HATCH` | `CL-C3-OVERHANG-*`, `CL-C3-HANDLE-*`, `CL-C3-GRIP`, `CL-C3-HATCH-TAB` |
| `CALC-C3-MASS`, `-NOSE-PATH` | `CL-C3-POD-MASS-REC`, `-FULL-STOP`, `CL-C3-NOSE-BLOCK-A`, `-NOSE-STACK`, `CL-C3-BLOCK-A-SHARE`, `CL-C3-STOP-SECTION-PENALTY`, `CL-C3-BLOCK-B-FORCE` |
