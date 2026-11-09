# Pod structures — K09-L

Owner C3 (pod structures; the fuselage role re-scoped by A1). Revision C3-R1, 2026-11-09, against params A1-R2,
C1 loads C1-R2 (`team/C1/data/joints.csv`) and D2's pod at `MODELLED` (`subsystems/pod/`). Answers `CR-D2-05`,
`CR-C5-07` and takes a position on `CR-C5-02`. Re-run in < 1 s:
`python -I redesign/team/C3/pod_structures.py`, then `python -I redesign/proofs/build_graph.py` (no C3 errors;
other roles' drift still fails the build). Every number below is in `claims.json` (`CL-C3-…`) or `out/results.json`.

Status: the calculations are `CHECKED` (closed-form, hand-reproducible). Every allowable is an `UNVERIFIED`
estimate until the three tests in section 6 have run, so every margin is `UNVERIFIED`.

## 1. Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| Does the pod-to-wing bond hold? | **Yes, as drawn.** Bond on bare XPS, x 0 … 0.065 m × 0.140 m (LE filler + recess floor; walls not counted). Worst design case L1 level landing (MC-C): interaction 0.65 | `CL-C3-BOND-R-DESIGN` | +35 % `UNVERIFIED` |
| Does it hold the pod group in a 12.75 g crash? | **Yes.** 0.900 kg × 12.75 g = 113 N, worst direction +z (peel, the group CG is 56 mm ahead of the bond centroid): interaction 0.76 | `CL-C3-BOND-R-CRASH` | +24 % `UNVERIFIED` |
| Aft stop 1.5 mm (pack +x, hover landing and fin-tip fall) | **Fails.** 55 MPa across the print layers vs 15 MPa. Needs 2.9 mm → **3.0 mm** | `CL-C3-AFT-STOP-D2`, `-REC` | `FAIL` → +8 % |
| Foam-board nose wall as the forward stop (−x crash) | **Fails by 9×.** 45 N·mm/mm needed, 4.7 available. Add a **3.0 mm printed forward stop** on the tray | `CL-C3-NOSE-WALL-M`, `CL-C3-FWD-STOP-REC` | `FAIL` → +13 % |
| Guides 1.0 mm (pack ±y) | Passes by 3 %; **1.5 mm** for a usable margin | `CL-C3-GUIDE-D2`, `-REC` | +3 % → +57 % |
| Straps (pack +z) | Pass: leg tension 31 N vs 100 N; hook-and-loop overlap **≥ 50 mm** (31 mm needed) | `CL-C3-STRAP-LEG`, `-OVERLAP-REQ` | +69 % / +38 % |
| Overhang ahead of the LE (pack 72 % ahead of x 0) | Passes: wall-top face stress 8.5 MPa crash vs 10 MPa; 4.8 MPa design | `CL-C3-OVERHANG-CRASH`, `-DESIGN` | +15 % / +52 % |
| Carry handle on the spar (G1, 2.6 kg at 2 g) | Passes: 110 N design vs 2 ties 444 N; grip 7.0 MPa along the raster | `CL-C3-HANDLE-TIES`, `CL-C3-GRIP` | +75 % / +72 % |
| Hatch at VD suction | Passes by 3 % on a 12 × 30 mm tab; **12 × 40 mm** gives +27 % | `CL-C3-HATCH-TAB` | +3 % |
| Mass with the changes | 100.4 + 9.5 = **109.9 g vs 105 g** allocation | `CL-C3-POD-MASS-REC` | `FAIL` −5 % → `CR-C3-03` |

## 2. Load path

Frame x aft, y right, z up in cruise; in hover +x points at the ground. One path per pack direction; every link is
sized below. Nothing relies on the hatch or the foam-board nose wall.

| Pack load | Link 1 | Link 2 | Link 3 | To the wing |
|---|---|---|---|---|
| +x (hover landing, fin-tip fall) | aft stop wall, 3.0 mm PETG | tray floor (shear) | tray-to-floor epoxy | pod-to-wing bond → recess end → spar |
| −x (nose-in, sliding stop) | **forward stop wall, 3.0 mm PETG (new)** | tray floor | tray-to-floor epoxy | bond |
| ±y | guide, 1.5 mm PETG | tray floor | tray-to-floor epoxy | bond |
| +z (push-over, crash up) | 2 straps, 4 legs | strap run under the tray (1 mm groove) | tray-to-floor epoxy (flat-wise); front strap: floor-to-wall glue lines | bond (peel) |
| −z (pull-up, crash down) | tray bearing | foam-board floor | overhang: 2 side walls in bending to x 0 | bond (bearing) |
| Lift by the handle | grip | 2 legs | 2 feet + 2 nylon ties round the spar | spar directly |

The pack's 140 mm runs from x −0.100 to +0.040 m: **72 % of it is ahead of the wing LE**, carried by the pod as a
cantilever (open-top U: two 65 mm foam-board side walls plus the floor bottom face). The handle ties are **not** a
pod-group crash path: the handle legs only pass through holes in the foam-board deck (`CR-C3-04`).

## 3. Loads and factors

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod-group joint loads, 56 envelope rows (F, H, T, L1–L5, G; MC-C, MC-P) | 6 components at C1's point (x −0.005, z 0.015) | N, N·m | `ASM-C3-POD-LOADS` ← `team/C1/data/joints.csv` J-POD | `UNVERIFIED` (C1 inputs) |
| Pack-to-tray loads, same rows | Fx +41.4 / −0.9, Fy +5.9 / −10.9, Fz +10.4 / −21.2 (limit) | N | `ASM-C3-PACK-LOADS` ← J-PACK | `UNVERIFIED` |
| Design factor, flight and ground | 1.5 × 1.15 × 1.25 = 2.16 | — | `P:requirements.safety_factor_ult`, `ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR` | `PROPOSED` |
| Crash, ultimate, no further factor | n 12.75; pack 85 N any axis; pod group 0.900 kg → 113 N | —, N | `CL-C1-CRASH-N`, `CL-C1-PACK-CRASH-LOAD`, `CL-C3-POD-GROUP-MASS` | `UNVERIFIED` |
| Strap preload | 40 | N | `ASM-C1-STRAP-PRELOAD` | `PROPOSED` |
| q at VD | 454 | Pa | `CL-C1-Q-VD` | `UNVERIFIED` |

Governing cases: bond L1 level landing on four feet (MC-C, 402 g growth in the pod); stops and guides the 85 N crash
(flight loads are lower: aft 89 N design is the exception and is used); overhang the 12.75 g crash.

## 4. Materials and allowables

| Material | Use | Allowable | Value | Source | Status |
|---|---|---|---|---|---|
| XPS F-250 + epoxy | pod-to-wing bond | tension / shear (foam fails) | 100 / 100 kPa | `ASM-D2-XPS-ALLOW`, `ASM-C3-XPS-SHEAR` | `UNVERIFIED` |
| Paper-faced board 4.8 mm | floor, walls, nose, hatch, deck | face stress (wrinkling) | 10 MPa, face 0.10 mm | `ASM-C4-FACE-SIGMA`, `ASM-C4-FACE-T` | `UNVERIFIED` |
| Board + epoxy | tray-to-floor, floor-to-wall | flat-wise / shear | 100 / 200 kPa | `ASM-C3-FB-FLAT`, `ASM-D5-BOND-TAU` | `UNVERIFIED` |
| Printed PETG, tray printed flat | stop walls, guides (stress across layers) | tension | 15 MPa | `ASM-C4-PETG-TENSILE` | `UNVERIFIED` |
| Printed PETG along the raster | handle grip (print lying flat) | bending | 25 MPa | `ASM-C3-PETG-INPLANE` | `UNVERIFIED` |
| Nylon hook-and-loop | straps, hatch tab | shear / flat-wise | 5 / 2.5 N/cm² | `ASM-C3-HL` | `UNVERIFIED` |
| Nylon tie 7.6 mm | handle to spar | rating | 222 N each | `ASM-D2-TIE-CAP` | `UNVERIFIED` |

Use epoxy for every structural joint in the pod. Hot glue only for non-structural trim (hatch edges, label).

## 5. Sizing for D2

| Item | D2 now | C3 size | Margin | Why |
|---|---|---|---|---|
| Aft stop wall (`POD-002`) | 1.5 mm | **3.0 mm**, aft face stays at the recess end, 2 mm root fillet; lead notch above 12 mm unchanged | +8 % | +x pack 89 N design at 12.5 mm height across the layers |
| Forward stop (`POD-002`) | foam-board nose wall | **3.0 mm PETG wall printed with the tray, 25 mm tall, 54 mm wide**, aft face = pack forward stop (x −0.1002 m) | +13 % | the nose wall carries 1/10 of the 85 N crash load; this also satisfies `CR-C5-07` in −x |
| Pod nose | x_le −0.105 | **−0.108** (3 mm forward), so the bay stays 0.162 m ≥ 0.160 and the travel 22.2 ≥ 18 mm | — | `CR-C3-02` to A1; void if `CR-C5-02` (≤ −0.130) is adopted |
| Guides (`POD-002`) | 1.0 × 8 mm | **1.5 × 8 mm** | +57 % | ±y crash 85 N along the pack |
| Straps (`POD-004`) | 2 × 20 mm | unchanged; **mark 50 mm hook-and-loop overlap**; loop pull test 2 × 85 N stays | +38 % | +z crash 42.5 N per strap + preload |
| Tray to floor | bonded | **epoxy over the full tray area**, both strap stations wetted | +80 % | strap pulls the tray up |
| Floor to side walls, x −0.100 … 0 | — | **epoxy fillet both sides**, full length | +45 % | front strap lifts the overhang floor |
| Pod-to-wing bond (`E-POD-01`) | 10 014 mm² | unchanged; bare foam (tape off), epoxy, LE filler bonded on its curved face; ≥ 9 100 mm² wetted | +35 % / +24 % | — |
| Side walls | 4.8 mm board, 65 mm tall | unchanged; **no cut-out in a side wall between x −0.06 and +0.02** (the wall tops are the compression flange at the overhang root) | +15 % | — |
| Cut-outs allowed | — | aft-wall harness exits as drawn; pitot hole and an E3 ram-air inlet (15 × 30 mm) in the nose wall; strap grooves in the floor top face | — | none is on a load path |
| Hatch tab (`POD-003`) | 12 × 30 mm | **12 × 40 mm** | +27 % | VD suction 17.5 N design |
| Carry handle (`POD-007`) | as drawn | unchanged; **print lying flat** (grip along the raster) | +72 % | — |

## 6. Tests that turn the margins `VERIFIED`

| Test | What | Verifies |
|---|---|---|
| `T-C3-BOND-COUPON` | epoxy on F-250 and on board: 3 flat-wise pulls each, 3 lap shears; allowable = mean − 2 s, foam or paper failure | bond, tray, glue-line claims |
| `T-C3-STOP-PUSH` | printed tray offcut with a 3.0 mm stop and 1.5 mm guides: 90 N at 12 mm height; 85 N along a guide; then once to failure | stops, guides |
| `T-C3-POD-PROOF` | built pod on the wing, 680 g dummy pack: pulls down 64 N, up 85 N, aft 85 N, sideways 85 N, 10 s each | bond crash, overhang, glue lines |

Plus D2's `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-D2-WEIGH`.

## 7. Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Pod +9.5 g over its 105 g allocation (+7 g more with `CR-C5-02`) | A1 (`CR-C3-03`) |
| 2 | Nose-in crash: the pack is still the crush zone (`CL-C5-PACK-NOSE-ROOM` `FAIL`). C3 supports `CR-C5-02`; the 3 mm forward stop is designed to break at its root (~100 N) and then act as C5's spreader plate | A1, C5 (`CR-C3-06`) |
| 3 | B3's re-derived CG range (target 0.0526 m in the current graph, was 0.0444) may move the pod aft (D-17). Aft is better here (shorter overhang); re-run this script on any pod move | A1 |
| 4 | Every allowable is an estimate; C6 owns joint allowables | C6, H1 (`CR-C3-05`, `-07`) |
| 5 | Pod drag and slipstream loads are not in C1's model (q 454 Pa on a 70 × 140 mm box ≈ 5 N, small against 113 N) | C1 |
