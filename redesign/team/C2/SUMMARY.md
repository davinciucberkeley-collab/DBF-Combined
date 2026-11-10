# C2 Wing structures — summary

Owner: C2. Revision **C2-R2**, 2026-11-10, at params A1-R4, C1-R4 loads, D1-R1 geometry. Full reports:
[`WING-STRUCTURES.md`](WING-STRUCTURES.md) (sizing, beam model, modes, aeroelastics) and
[`SIMULATION-REPORT.md`](SIMULATION-REPORT.md) (3-D FEA of the as-designed wing). Requests:
[`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md). Build data for D1: `sizing.json`. Claims: `claims.json` (30, beam and hand
calcs) and `fea/claims.json` (13, 3-D FEA).

**Verdict.** The one-piece XPS wing on a 22 × 20 mm CF spar with one tape layer carries every C1 case. The 3-D FEA
agrees with the beam model on deflection (within 5 %) and shows it is conservative on twist (16 %). New from the FEA:
the foam at the inboard corners of the through-core block pockets is over its allowable at ultimate (CR-C2-11), and
the fin-root tab fails if the fin root fillet carries load (CR-C2-12). `R-VIBRATION` stays FAIL (tap test + notch).

## Key numbers (ultimate = 1.5 × limit; low-corner stiffness E 70 / G 3 GPa)

| Item | Value | Limit / allowable | MS | Claim | Status |
|---|---|---|---|---|---|
| Spar | CF 22 × 20 × 1 000, x 0.080, z +0.0066 m, 4 PETG plugs | — | — | `sizing.json#spar` | `MODELLED` (D1) |
| Spar bending, hand calc, spar alone (L1 root) | 59.3 MPa | 350 MPa | +4.9 | `CL-C2-SPAR-SIGMA-ULT` | `UNVERIFIED` |
| Spar stress, 3-D FEA, max (G2, block face) | 38.3 MPa | 350 MPa | +8.1 | `CL-C2-FEA-SPAR-SIGMA-ULT` | `UNVERIFIED` |
| Spar wall ring without plug (block / anchor) | 911 / 76 MPa | 40 MPa hoop | −0.96 / −0.48 | `CL-C2-RING-NO-PLUG`, `-ANCHOR` | `FAIL` → plugs fitted |
| Tip deflection / semi-span (G2), beam / FEA | 0.0044 / 0.0043 | 0.05 | +10 | `CL-C2-TIP-DEFL-FRAC`, `CL-C2-FEA-TIP-DEFL-FRAC` | `UNVERIFIED` |
| Twist at limit, flight (F7) / envelope (L4) | 1.84° / 2.88° | — | — | `CL-C2-TWIST-FLIGHT` | `UNVERIFIED` |
| Bulk foam, 3-D FEA, 99.5th pct (tension / shear) | 49 / 36 kPa | 150 / 100 kPa | +2.06 / +1.81 | `CL-C2-FEA-FOAM-S1`, `-TAU` | `UNVERIFIED` |
| **Foam at block-pocket inboard corners** (tension / compression) | 203 / 199 kPa | 150 / 120 kPa | **−0.26 / −0.40** | `CL-C2-FEA-FOAM-CORNER-S1`, `-S3` | `FAIL` → CR-C2-11 |
| Foam shear if the fin root fillet carries station load | 222 kPa | 100 kPa | −0.55 | `CL-C2-FEA-FOAM-FILLET-SENS` | `FAIL` (sensitivity) → CR-C2-12 |
| PETG block / plugs, 3-D FEA von Mises | 2.7 MPa | 20 MPa | +6.3 | `CL-C2-FEA-PETG` | `UNVERIFIED` |
| Reversal / divergence / flutter-free speed | 53 / 91 / ≥ 80 m/s | ≥ 32.0 m/s (1.2 VD) | +0.66 / +1.8 / +1.5 | `CL-C2-V-*` | `UNVERIFIED` |
| First wing modes (torsion, anti / sym, low corner) | 11.9 / 24.1 Hz | in hover control path | — | `CL-C2-F-TORSION-*` | `UNVERIFIED` |
| Wing-mode separation from rotor orders | 0.072 | ≥ 0.20 | — | `CL-C2-WING-MODE-SEP` | `FAIL` → CR-C2-04 |
| Wing structure mass | 389 g | 405 g | — | `CL-C2-WING-MASS` | `MODELLED` |

## Simulation round (3-D FEA)

| Check | Result | Status |
|---|---|---|
| Model | gmsh mesh of the D1-R1 wing with every cut-out, block, anchor and plug; C1-R4 loads; tube as orthotropic (O) and as SU2's two isotropic bounds (B, T) | `CHECKED` |
| Solvers | SU2 ELASTICITY (CG + LU_SGS; ILU diverges, CR-C2-14) and an in-house PCG on the same mesh: agree to 2 × 10⁻⁸ | `CHECKED` |
| Element check | spar tube cantilever vs beam theory: −2.3 % deflection, +0.3 % twist | `CHECKED` |
| Mesh convergence | 3 levels, 107 k → 1.27 M dofs; GCI ≤ 4.9 % on every governing output | `CHECKED` |
| Against the hand calcs and beam model | flap 0.955, in-plane 0.989, twist 0.84; spar stress between the composite-beam and spar-alone hand values | `CHECKED` |

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Block-pocket corner foam: radius / fillet the pocket, re-run FEA, proof-test (CR-C2-11) | D1, D3, C2 |
| 2 | Fin root fillet must stay fail-safe; C4 to send its load share (CR-C2-12); radius the elevon cut-out corners (CR-C2-13) | C4, C6, D1 |
| 3 | Wing modes in the rotor band: tap test + harmonic notch (CR-C2-04); B3 re-run for the updated torsion modes (CR-C2-03) | A2, F4, B3, H1 |
| 4 | Every material value `UNVERIFIED`: T-C4-TUBE-BEND (+ GJ, CR-C2-15), T-C2-XPS-COUPON, T-C2-WING-PROOF, T-C2-TWIST, T-C2-TAP-TEST | H1, C4 |

## How to verify

`python -I redesign/team/C2/wing_struct.py` → `c2_claims.py`; FEA: the commands in SIMULATION-REPORT §9 →
`fea/fea_report.py` → `fea/fea_claims.py` → `python -I redesign/proofs/build_graph.py` (no C2 drift; the C2 FAIL
claims are the expected-fail ring checks, the two block-corner claims, the fillet sensitivity and the mode separation).
