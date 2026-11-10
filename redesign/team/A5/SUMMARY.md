# A5 CAD lead: Fusion framework for K09-L

Status: `CHECKED` framework and R3 skeleton, `UNVERIFIED-IN-FUSION` backend (A5, 2026-11-09, params revision A1-R3).
Re-check: `python -I redesign/fusion/tests/test_framework.py` · `python -I redesign/fusion/check.py --skeleton --strict`
· `python -I redesign/team/A5/cad_claims.py` then `python -I redesign/proofs/build_graph.py`.

## This round (A1-R3 action items: CR-D3-14/21, CR-D5-02, D-46)

| Item | Done | Status |
|---|---|---|
| Re-test after A4's `merge_check.py` change (D-46) | `fusion/tests` and `check.py --strict` re-run on the new module | `CHECKED` |
| Skeleton fins to R3 | tube 0.344 m (ends z ±0.172), 0.21 m half-fins, mounts as a tube-end grip + plate to z ±0.2075 with the motor on `DP-MOTOR-FACE`, new station collars, CF braces (`k9.strut`) and spar anchors; fins 408 g split from D3's R3 unit masses. The 7° cant is not modelled (D3 cants the plate) | `MODELLED` |
| Rest of the skeleton to R3 | allocations 2 324 g (D-38), 48 mm feet splayed to the pad contact, pod 0.21 × 0.14 at −0.115, pack at the D-24 station (x −0.001, from D2's `pack_aft_face_m`), box 1.25 × 0.55 × 0.54, library types `CT-PROP-NUT`, `CT-CRADLE-CONTACT`, `CT-THERMAL-CONTACT` | `MODELLED` |
| DATUMS.md (52 datums, was 43) | `DP-TUBE` 0.045, `DP-TE` 0.320, `DP-GROUND` 0.368, new `DP-MOTOR-FACE` 0.0309, `DX-FOOT-*` at the pad contact (0.368, ±0.320, ±0.218), new `DX-COLLAR-*` (0.045, ±0.3023, ±0.1535), new `DX-ANCHOR-*` (0.080, ±0.242, +0.0266 / −0.0127), `DX-BOX` x 0.1265; hover lift 0.368 m; section 4 at R3 | `CHECKED` (matches D3's `fins.geometry()` to 1e-6 m, test) |
| `cad_claims.py` re-run | closed form rebuilt for R3; cross-check against the CAD roll-up: 0.0 mm. `CL-A5-LAYOUT-CG-X` now verifies `R-CG-RANGE` against 0.050–0.055, with `-FWD` and `-RANGE-USE` claims | `CHECKED` (0 A5 drift) |
| Also fixed | the elevon pod gap read 0 mm after the pod widened to 0.14 m; it is now the true corner distance (the pod ends 155 mm ahead of the hinge). Fusion material map: "CF tube" and "CF strip" did not match Carbon Fiber, and ASA had no entry | `CHECKED` |

## Check results

| Run | Result |
|---|---|
| `check.py --skeleton --strict` | PASS: 10 modules, 54 parts (50 flight), 52 datums, 5 keep-outs, 0 errors, 0 warnings; 2 324 g, CG (0.052, 0, 0.018) m |
| `check.py --examples --strict` | PASS: 3 modules, 0 errors, 0 warnings |
| `tests/test_framework.py` | 27 tests OK (2 new: R3 datums against D3 and D5, strut volume and centroid) |
| `check.py` (real `subsystems/`: D3 fins, D2 pod, D5 landing, D7 transport) | FAIL, as expected: 9 dangling edges to `WNG-001/002` and `PWR-001` and the partial-aircraft CG, until D1 and F1 ship. No framework errors; the modules build with the R3 datums |
| `build_graph.py` | no A5 errors or drift; the build reports drift in A1, B2, C2, C3 and C4 claims (theirs) |

## Claims others build on

| Claim | Value | Unit | Limit | Status |
|---|---|---|---|---|
| `CL-A5-HINGE-X` / `CL-A5-HINGE-Z` | 0.2496 / 0.0056 | m | — | `CHECKED` |
| `CL-A5-SPAR-COVER` (spar z 0.0066) | 0.0043 | m | ≥ 0.002 | `CHECKED` |
| `CL-A5-ELEVON-GAP-MIN` | 0.015 | m | ≥ 0.010 | `CHECKED` |
| `CL-A5-LAYOUT-CG-X` / `-FWD` (allocations, pack at −0.001) | 0.0521 (16.3 % c) | m | 0.050–0.055 | `UNVERIFIED` (+4 % / +5 %) |
| `CL-A5-LAYOUT-CG-X-RANGE-USE` | 0.15 | — | ≤ 1 | `UNVERIFIED` |
| `CL-A5-PACK-X-FOR-CG` · `CL-A5-PACK-SHIFT` | +0.001 · +0.002 | m | — | `UNVERIFIED` |
| `CL-A5-LAYOUT-CG-Z` | 0.0177 | m | ≤ 0.030 | `UNVERIFIED` |
| `CL-A5-HOVER-SPLIT` (upper / lower) | 1.20 | — | ≤ 1.25 | `UNVERIFIED` (+4 %) |

**The layout CG is inside the range only on allocated masses.** A3's bottom-up 0.0556 m is 0.6 mm aft of the aft limit
(`CL-A3-CG-X-RANGE` FAIL) because the real fins, harness and feet are heavier and sit further aft. A3's number governs
`R-CG-RANGE`; this one shows the layout itself is not the cause (CR-A5-17).

## Open issues

1. `R-CG-RANGE` rests on A3's bottom-up CG and D-24's pack station (CR-A3-15). The skeleton follows D2's `pack_aft_face_m` once it changes.
2. The R3 datums D3 and D5 own are read from their `params.json` files until A1 promotes them (CR-A5-16, CR-A5-19).
3. `fusion_backend.py` has never run in Fusion (CR-A5-08). The R3 skeleton is ready for BuildAll.
4. Checks use one bounding box per body, which is coarse for diagonal parts such as the braces. Real clearances need a Fusion interference check.

Change requests: `team/A5/CHANGE-REQUESTS.md` (round 2 status; CR-A5-16 … 19 to A1, A3, D3, D5).
