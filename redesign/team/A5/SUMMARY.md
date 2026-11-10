# A5 CAD lead: Fusion framework for K09-L

Status: `CHECKED` framework, skeleton and datum sheet, `UNVERIFIED-IN-FUSION` backend (A5, 2026-11-10, params A1-R4 / D-60).
Re-check: `python -I redesign/fusion/tests/test_framework.py` · `python -I redesign/fusion/check.py --skeleton --strict`
· `python -I redesign/team/A5/integration_check.py` · `python -I redesign/team/A5/cad_claims.py` then `python -I redesign/proofs/build_graph.py`.

## This round (action items: keep-out false positives, stale DATUMS.md, layout CG drift)

| Item | Done | Status |
|---|---|---|
| Keep-out test (blocker) | `check.py` still runs the per-body box first as a pre-filter. It then tests the **convex hull of the body's vertices** against the canted cylinder (`Shape.hull_points`: prism and loft vertices; a revolve is swept as a circumscribed 24-gon, at most 0.9 % of r larger). The distance comes from a pairwise Frank-Wolfe solver (`fusionkit._hull_cyl_dist2`), checked against brute-force edge sampling. For a `k9.prop_keepout` zone, a hit means the hull is closer than `clearance` to the swept blade volume, and the message gives that distance in mm. Boxes the hull clears are printed as a note, not an issue | `CHECKED` (2 new tests, 33 OK) |
| Asymmetric blade envelope (CR-E1-45) | `k9.prop_keepout(..., fwd=, aft=)` shifts the cylinder by (aft − fwd)/2 along the shaft. E1 now passes 0.010 / 0.006 | `CHECKED` |
| DATUMS.md | Regenerated: `DP-POD-LE` −0.130, `DP-CG` 0.0522, `DP-MOTOR-FACE` 0.0294, `DP-PROP` and `DX-HUB-*` at x −0.0077, `DX-POD` x −0.0175, `DX-BOX` x 0.119. 52 datums, no longer stale | `CHECKED` |
| Skeleton and `CALC-A5-LAYOUT-CG` | Skeleton regenerated at the D-48 allocations (2 355 g) with D2's D-47 pack bay. The closed form and the CAD skeleton agree to 0.0 mm. Claims rewritten, 0 A5 drift | `CHECKED` |
| Layout CG role | The allocation layout CG is now **0.0466 m, 4.3 mm ahead of the 0.0509 forward limit**. The delivered aircraft sits at 0.0521 m. The difference is where the allocation lumps are placed, not where the parts are. The layout claims are now information only. `R-CG-RANGE` is verified on the assembled CAD, including the new `CL-A5-ASSY-CG-X-FWD` (CR-A5-31) | `CHECKED` |

## Keep-out result on the delivered subsystems

| Body | Zone | Box test (old) | Hull distance to swept blades | Verdict |
|---|---|---|---|---|
| `FIN-009-*` CF brace | KO-PROP, all four | hit | ≥ 34.9 mm (9.9 mm outside the zone) | box artefact, cleared |
| `WNG-001` core; `WNG-003` skin and doubler | KO-PROP-UR/UL | hit | ≥ 33.5 mm | box artefact, cleared |
| `FIN-004` boss and eye; `FIN-006` plug | KO-PROP-UR/UL | hit | ≥ 27 mm (fwd/aft envelope) | cleared |
| **`FIN-002-R/L` motor tube** | **all four** | hit | **21.0 mm, limit 25 mm** | **real: A1 decides CR-D3-26 (CR-A5-30)** |

## Check results

| Run | Result |
|---|---|
| `check.py --skeleton --strict` | PASS: 10 modules, 54 parts, 52 datums, 5 keep-outs, 0 errors, 0 warnings; 2 355 g, CG (0.047, 0, 0.017) m |
| `check.py --examples --strict` | PASS: 3 modules, 0 errors, 0 warnings |
| `tests/test_framework.py` | 33 tests OK |
| `check.py` (delivered `subsystems/`) | FAIL: 4 errors (the motor-tube clearance above; there were 16 keep-out errors), 3 warnings; 2 320 g, CG x 0.0521 m |
| `build_graph.py` | No A5 errors or drift. The build fails on drift in A3, B1, B2 and B3 claims (D-60 range, pod size, sag); those roles must re-run |

## Claims others build on

| Claim | Value | Unit | Limit | Status |
|---|---|---|---|---|
| `CL-A5-HINGE-X` / `-Z` | 0.2496 / 0.0056 | m | — | `CHECKED` |
| `CL-A5-SPAR-COVER` | 0.0043 | m | ≥ 0.002 | `CHECKED` |
| `CL-A5-ELEVON-GAP-MIN` | 0.015 | m | ≥ 0.010 | `CHECKED` |
| `CL-A5-ASSY-CG-X` / `-FWD` (delivered CAD, pack at −0.022) | 0.0521 | m | 0.0509–0.0548 | `UNVERIFIED` (+5 % / +2 %) |
| `CL-A5-ASSY-CG-X-RANGE-USE` | 0.37 | — | ≤ 1 | `UNVERIFIED` |
| `CL-A5-ASSY-MASS` | 2.320 | kg | ≤ 2.600 | `UNVERIFIED` |
| `CL-A5-ASSY-CHECK-ERRORS` | 4 | — | ≤ 0 | `UNVERIFIED` (FAIL, see CR-A5-30) |
| `CL-A5-LAYOUT-CG-X` (information) | 0.0466 | m | — | `UNVERIFIED` |
| `CL-A5-LAYOUT-CG-Z` · `CL-A5-HOVER-SPLIT` | 0.0169 · 1.195 | m · — | ≤ 0.030 · ≤ 1.25 | `UNVERIFIED` |

## Open issues

1. The motor tube's 21.0 mm prop clearance is the only `check.py` error. It is real geometry, not a test artefact (CR-A5-30 to A1).
2. The skeleton's mass lumps use R3 placements. Designers should read the CG from `integration_check.py`, not from the skeleton.
3. The hull test is exact only for convex bodies. A concave body (for example an L-bracket) can over-report and should be split into convex bodies. In Fusion, a smooth loft through three or more sections can bulge slightly past its hull.
4. `fusion_backend.py` has never run in Fusion (CR-A5-08).

Change requests: `team/A5/CHANGE-REQUESTS.md` (round 4: CR-E1-45 done, CR-A5-30 to A1, CR-A5-31 to A2).
