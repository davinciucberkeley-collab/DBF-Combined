# A5 CAD lead: Fusion framework for K09-L

Status: `CHECKED` framework, `UNVERIFIED-IN-FUSION` backend (A5, 2026-11-09). Re-check:
`python -I redesign/fusion/tests/test_framework.py` · `python -I redesign/fusion/check.py --skeleton --strict` ·
`python -I redesign/team/A5/cad_claims.py` then `python -I redesign/proofs/build_graph.py`.

## What was produced

| File (under `redesign/`) | What | Status |
|---|---|---|
| `fusion/modules.txt` | K09-L build order `wing fins pod landing propulsion mechanisms power avionics harness transport` (closes CR-A1-01; a hyphenated `flight-software` module would import and build last) | `CHECKED` |
| `fusion/DATUMS.md` | frame, cruise/hover attitudes, 42 named datums (table generated from `params.json`), derived geometry, rules | `CHECKED` |
| `fusion/STANDARDS.md` | build order, naming = part ids (9xx = skeleton), geometry, materials, mass/CG, joints, status, hand-over checklist | `PROPOSED` |
| `fusion/k09kit.py` | helpers: datum sheet, `.dat` reader + placeholder reflex section, core/elevon lofts, hinge point, spar/tube, fin plate, motor/prop envelopes, prop and ground keep-outs, `pair`/`quad` mirrors, hover pose | `CHECKED` |
| `fusion/fusionkit.py`, `build_all.py`, `check.py`, `backends/*`, `BuildAll/` | `ctx.value(key, unit)`, `ctx.D()`, datums (Fusion: **00 Datums** component), keep-out and envelope checks, `--skeleton`, TPU material | `CHECKED` (stub) |
| `fusion/skeleton/` | reference layout: 9 modules, 36 parts, 2 132 g = allocations; `make_skeleton.py` writes masses and CAD-centroid CGs | `MODELLED` |
| `fusion/tests/test_framework.py` | 13 → 22 tests (skeleton, datums, sections, `.dat` reader, keep-outs, hover pose, units, backend smoke on skeleton) | `CHECKED` |
| `team/A5/cad_claims.py` → `claims.json` | 12 claims, 5 assumptions, 2 planned tests | see below |

## Check results

| Run | Result |
|---|---|
| `check.py --examples --strict` | PASS (3 modules, 0 errors, 0 warnings) |
| `check.py --skeleton --strict` | PASS (9 modules, 36 parts, 42 datums, 5 keep-outs, 0 errors, 0 warnings); TOTAL 2 132 g, CG (0.039, 0, 0.015) m |
| `check.py` (real subsystems) | FAIL: no modules yet under `subsystems/` (expected until the designers start) |
| `tests/test_framework.py` | 22 tests OK |
| `build_graph.py` | OK: every stored number re-computes |

## Claims others build on

| Claim | Value | Unit | Limit | Status |
|---|---|---|---|---|
| `CL-A5-HINGE-X` / `CL-A5-HINGE-Z` | 0.234 / 0.0072 | m | — | `CHECKED` / `UNVERIFIED` (placeholder section) |
| `CL-A5-ELEVON-GAP-MIN` | 0.015 | m | ≥ 0.010 | `CHECKED` |
| `CL-A5-SPAR-COVER` (spar on the chord line) | −0.0011 | m | ≥ 0.002 | `FAIL` → CR-A5-01 |
| `CL-A5-SPAR-Z-CAMBER` / `CL-A5-SPAR-COVER-CAMBER` | 0.0048 / 0.0037 | m | ≥ 0.002 | `UNVERIFIED` |
| `CL-A5-LAYOUT-CG-X` | 0.037 (CAD roll-up 0.039) | m | ≥ 0.045 | `FAIL` → CR-A5-03 |
| `CL-A5-PACK-X-FOR-CG` | 0.170 | m | pod ends at 0.180 | `UNVERIFIED` |
| `CL-A5-LAYOUT-CG-Z` · `CL-A5-HOVER-SPLIT` | 0.015 · 0.54 (upper pair) | m · — | ≤ 0.030 | `UNVERIFIED` |

## Open issues

1. With the spar on the chord line, the tube breaks the lower skin of any section with about 1.6 % camber (CR-A5-01). The MH 45 file is missing (CR-A5-02).
2. Layout CG is 6–8 mm ahead of the CG range; the pack would need to sit 0.09 m further aft (CR-A5-03).
3. `fusion_backend.py` (datums, lofts, joints, materials) has never run in Fusion (CR-A5-08).
4. Keep-out and touch checks use bounding boxes, which are coarse for diagonal parts. Real prop-tip clearance is A1's `CL-A1-PROP-CLEAR` plus a Fusion interference check.
5. Prop axial thickness 8 mm and foam-board 4.8 mm are `EST` (CR-A5-05, CR-A5-06).

Change requests: 9 in `team/A5/CHANGE-REQUESTS.md` (A1, A3, A4, B2, B3, E1, J3, all designers).
