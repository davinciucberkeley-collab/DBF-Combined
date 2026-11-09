# C3 — Pod structures (summary)

Revision C3-R1, 2026-11-09. The pod's load path from the pack to the wing, sized with C1's loads against D2's
modelled pod. Report: `FUSELAGE-STRUCTURES.md`. Script: `pod_structures.py` (< 1 s) → `claims.json` (22 claims,
3 planned tests), `out/results.json`. Proof build: no C3 errors.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod-to-wing bond, interaction, design (L1, MC-C) | 0.65 (+35 %) | — | `CL-C3-BOND-R-DESIGN` | `UNVERIFIED` |
| Pod-to-wing bond, interaction, 12.75 g crash (+z peel) | 0.76 (+24 %) | — | `CL-C3-BOND-R-CRASH` | `UNVERIFIED` |
| Pod group in the crash (680 g pack) | 0.900 / 113 | kg / N | `CL-C3-POD-GROUP-MASS` | `UNVERIFIED` |
| Aft stop 1.5 mm (D2) / 3.0 mm (C3), design stress vs 15 MPa | 55.1 / 13.8 | MPa | `CL-C3-AFT-STOP-D2`, `-REC` | `FAIL` / `UNVERIFIED` (+8 %) |
| Nose wall as forward stop: needed vs available | 45 vs 4.7 | N·mm/mm | `CL-C3-NOSE-WALL-M` | `FAIL` |
| New 3.0 mm printed forward stop | 13.1 | MPa | `CL-C3-FWD-STOP-REC` | `UNVERIFIED` (+13 %) |
| Guides 1.0 / 1.5 mm, lateral crash | 14.6 / 6.5 | MPa | `CL-C3-GUIDE-D2`, `-REC` | `UNVERIFIED` (+3 % / +57 %) |
| Strap leg tension (+z crash + preload) / overlap needed | 31 / 31 | N / mm | `CL-C3-STRAP-LEG`, `-OVERLAP-REQ` | `UNVERIFIED` (+69 % / +38 %) |
| Overhang root face stress, crash / design | 8.5 / 4.8 | MPa | `CL-C3-OVERHANG-CRASH`, `-DESIGN` | `UNVERIFIED` (+15 % / +52 %) |
| Handle design load vs 2 ties | 110 vs 444 | N | `CL-C3-HANDLE-TIES` | `UNVERIFIED` (+75 %) |
| Pod mass with C3 changes vs allocation | 109.9 vs 105 | g | `CL-C3-POD-MASS-REC` | `FAIL` (−5 %) |

Factors: design = limit × 1.5 × 1.15 × 1.25; crash = C1 ultimate (12.75 g), no further factor. Calculations
`CHECKED`; allowables are estimates, so every margin is `UNVERIFIED` until the tests below run.

## Sizing handed to D2 (`CR-C3-01`)

| Change | Mass |
|---|---|
| Aft stop 1.5 → 3.0 mm | +2.6 g |
| New 3.0 mm forward stop on the tray (nose 3 mm forward, `CR-C3-02`) | +5.2 g |
| Guides 1.0 → 1.5 mm | +1.7 g |
| Epoxy joints, 50 mm strap overlap, 12 × 40 mm hatch tab, handle printed flat | ~0 g |

## Change requests

`CR-C3-01` D2 sizing · `CR-C3-02` A1 nose −0.108 m · `CR-C3-03` A1 pod allocation 115 g · `CR-C3-04` D2 claim
clean-up (ties are not a crash path) · `CR-C3-05` C6 allowables · `CR-C3-06` A1/C5 crush block, stop wall =
spreader · `CR-C3-07` H1 tests.

## How to verify

| Check | Command or test |
|---|---|
| Re-run claims | `python -I redesign/team/C3/pod_structures.py` then `python -I redesign/proofs/build_graph.py` |
| Allowables | `T-C3-BOND-COUPON`, `T-C3-STOP-PUSH` |
| Built pod | `T-C3-POD-PROOF` (680 g dummy pack, 64–85 N pulls), `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL` |
