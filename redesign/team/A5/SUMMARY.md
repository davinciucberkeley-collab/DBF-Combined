# A5 CAD lead: Fusion framework for K09-L

Status: `CHECKED` framework and R1 skeleton, `UNVERIFIED-IN-FUSION` backend (A5, 2026-11-09, params revision A1-R2).
Re-check: `python -I redesign/fusion/tests/test_framework.py` · `python -I redesign/fusion/check.py --skeleton --strict`
· `python -I redesign/team/A5/cad_claims.py` then `python -I redesign/proofs/build_graph.py`.

## This round (CR-A1-12, CR-A4-11)

| Item | Done | Status |
|---|---|---|
| Re-run `cad_claims.py` (18 drifting calcs) | Section now the real S5010 (`ASM-A5-SECTION`; placeholder `ASM-A5-CAMBER` and `ASM-A5-FOAMBOARD-T` retired); layout CG rebuilt for R1; the script cross-checks the closed form against the CAD roll-up and stops on > 1 mm | `CHECKED` (0 A5 drift) |
| Skeleton to R1 | tubes through the core at x 0.045, 4 half-fins (`k9.half_fin`, root on the skin), 2 through-core blocks (`k9.core_block`), clip sets, 45 mm feet, pod at −0.105, 11×5.5MR, harness bundle bodies, new `transport` module (box 1.25 × 0.55 × 0.50 m); instance ids `<id>-<UR…/L/R>` | `MODELLED` |
| `s5010.dat` → `subsystems/wing/` | byte-identical copy of B2's file; `k9.section()` and the claims read it | `CHECKED` |
| CR-A4-11 | (a) `stowed` edges skip touch, new `transport` overlap check, ground parts out of `ctx.rollup`; (b) `k9.bundle`; (c) thermal = `ctx.contact`, touch-checked | `CHECKED` (tests) |
| Also fixed | revolve centroid now r-weighted (`fk.revolve_volume_centroid`); envelope includes pod nose and pitot; floating check anchors on undeclared parts; datum `DX-SADDLE` → `DX-BLOCK`, new `DX-BOX` (43 datums) | `CHECKED` |

## Check results

| Run | Result |
|---|---|
| `check.py --skeleton --strict` | PASS: 10 modules, 44 parts (40 flight), 43 datums, 5 keep-outs, 0 errors, 0 warnings; 2 200 g, CG (0.053, 0, 0.018) m |
| `check.py --examples --strict` | PASS: 3 modules, 0 errors, 0 warnings |
| `check.py` (real `subsystems/`: D5 landing, D7 transport so far) | FAIL, expected: 8 dangling edges to `WNG-001` / `FIN-001-*` and the partial-aircraft CG (merge_check) until D1/D3 ship; no framework errors |
| `tests/test_framework.py` | 25 tests OK (3 new: transport stowed/pressed, thermal + bundle, revolve centroid) |
| `build_graph.py` | no A5 errors; the build fails on B1, B3, E2, A1 drift (theirs) |

## Claims others build on

| Claim | Value | Unit | Limit | Status |
|---|---|---|---|---|
| `CL-A5-HINGE-X` / `CL-A5-HINGE-Z` | 0.2496 / 0.0056 | m | — | `CHECKED` |
| `CL-A5-SPAR-COVER` (spar z 0.0066; upper 5.0 mm) | 0.0043 | m | ≥ 0.002 | `CHECKED` (was a stale `FAIL`) |
| `CL-A5-SPAR-Z-CAMBER` · `CL-A5-SPAR-COVER-CAMBER` | 0.0070 · 0.0046 | m | ≥ 0.002 | `CHECKED` (0.0066 in params is fine) |
| `CL-A5-ELEVON-GAP-MIN` | 0.015 | m | ≥ 0.010 | `CHECKED` |
| `CL-A5-LAYOUT-CG-X` (pack centred) | 0.053 (16.6 % c) | m | ≤ 0.049 | `FAIL` −8 % → CR-A5-11 |
| `CL-A5-PACK-X-FOR-CG` · `CL-A5-PACK-SHIFT` | −0.041 · −0.036 | m | slide ±0.030 | `UNVERIFIED` (beyond the slide) |
| `CL-A5-LAYOUT-CG-Z` | 0.018 | m | ≤ 0.030 | `UNVERIFIED` |
| `CL-A5-HOVER-SPLIT` (upper / lower) | 1.20 | — | ≤ 1.25 | `UNVERIFIED` (+4 %) |

A1 forecast 0.058 m for the old calc at the new params; the R1 split (clip sets at the tube, power lump at the pod
nose, elevon mass by volume) gives 0.053. A3's bottom-up 0.051 differs mainly by the harness route (CR-A5-12).

## Open issues

1. Layout CG is 4 mm aft of the R0-derived range and the pack cannot reach the target inside ±30 mm with an aft wire channel: B3's R1 range decides (D-17).
2. `fusion_backend.py` has never run in Fusion (CR-A5-08 / CR-A1-21; the R1 skeleton is ready for it).
3. Checks use bounding boxes per body: coarse for diagonal parts; real clearances need a Fusion interference check.
4. Not modelled in the skeleton: 3° motor cant, tube holes and block cut-outs in the core, feet splay (CR-A1-20).

Change requests: `team/A5/CHANGE-REQUESTS.md` (round 1 status; CR-A5-10 … 15 to A4, A1, F2/D1, E1, D7; answer to CR-A4-11).
