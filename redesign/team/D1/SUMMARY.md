# D1 Wing designer: summary

Revision D1-R1 on params A1-R3, updated 2026-11-10. The deliverables are in `subsystems/wing/`: `SPEC.md`, `BUILD.md`,
`parts.csv`, `interfaces.json`, `params.json` and `fusion/wing.py`. `team/D1/wing_data.py` generates the parts list,
`wing_selfcheck.py` checks the geometry and `wing_claims.py` writes `claims.json`.

## Design

| Item | Value | Unit | Status |
|---|---|---|---|
| Core, one piece XPS, S5010 section | 1.150 × 0.320 | m | `MODELLED` |
| Spar CF 22 × 20, in a bore at x 0.080, z +0.0066 | 1.000 | m | `MODELLED` |
| Elevons, 4 panels, upper tape hinge at x 0.2496 | ±25 | deg | `MODELLED` |
| Elevon area fraction as built (`CL-D1-ELEVON-FRAC`) | 0.171 (≥ 0.15) | – | `CHECKED` |
| Wing mass, CAD estimate (`CL-D1-WING-MASS`) | 387.3 of 405 allocated | g | `UNVERIFIED` until `T-D1-WEIGH` |
| Wing CG x (`CL-D1-WING-CG-X`) | 0.114 | m | `MODELLED` |
| Min foam over the spar bore (`CL-D1-SPAR-COVER`) | 4.1 | mm | `CHECKED` |
| Upper-prop keep-out to the real wing surface (`CL-D1-PROP-SURF-GAP`) | ≥ 5.8 | mm | `CHECKED` (CAD) |

## This revision (action items)

| Item | Done | Status |
|---|---|---|
| Acknowledge `E-HRN-02/04` (harness grooves on `WNG-001`) | F2 declared them, so `wing_data.py` moved them from `acknowledges_pending` to `acknowledges`. The groove geometry is the same on both sides because the wing reads the harness `harness.groove.*` params | `CHECKED` |
| Acknowledge `E-GER-21/22` (TPU tip corner caps) | Acknowledged. The cap goes on the fixed core at \|y\| 0.560–0.575, over the folded tip tape layer. `BUILD.md` step 12 adds the D5 hand-off | `CHECKED` |
| CR-D1-05 (D5) and CR-D1-06 (F2) | closed | – |

## Checks (2026-11-10)

| Check | Result for the wing |
|---|---|
| `wing_data.py --check` | up to date: 36 acknowledged, 0 pending |
| `wing_selfcheck.py` | PASS |
| `merge_check.py --strict` | no wing warnings left. Overall FAIL on 17 one-sided warnings, all `E-HRN-23…32` and `E-TRN-21` waiting on avionics (F3) |
| `fusion/check.py` | wing `ok`, **0 errors, 0 warnings**. A5's convex-hull keep-out test now marks the `WNG-001/003` box hits on `KO-PROP-UR/UL` as artefacts, which matches `CL-D1-PROP-SURF-GAP` (≥ 5.8 mm) |
| `proofs/build_graph.py` | no D1 errors. The graph FAILs on drift in A3, A5 and B1 calcs, which those roles need to re-run |

## Open

| Issue | Owner |
|---|---|
| Saddle and pillar contacts on the tape skin `WNG-003` (CR-D1-02) | D7 |
| Weigh the core, tape and finished wing (`T-D1-WEIGH`) | G4 / D1 |
