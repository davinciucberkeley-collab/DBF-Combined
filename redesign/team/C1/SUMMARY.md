# C1 Loads — summary

Owner: C1 (loads engineer). Revision **C1-R4**, re-run 2026-11-10 at params A1-R4 / A1-R4a and the A3-R5 roll-up.
Full report: [`LOADS.md`](LOADS.md). Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md). Claims: `claims.json`
(103 claims). Re-run: `python -I redesign/team/C1/loads.py` (~3 s), then `python -I redesign/proofs/build_graph.py`.

All loads are **limit** (largest expected in service) unless marked ult (= 1.5 × limit). The calculation is
`CHECKED`; its inputs (thrust, CLmax, masses, capped VH) are `UNVERIFIED`, so every load stays `UNVERIFIED` until the
thrust stand, level-speed log, scale, swing and wing proof replace them.

## Flight envelope (D-50)

| Item | Value | Unit | Claim | Status |
|---|---|---|---|---|
| VH (F4 level speed at THR_MAX 70 %) | 21.28 | m/s | `CL-C1-VH` ← `CL-F4-VLEVEL` | `UNVERIFIED` (H2 log) |
| Derived VD = 1.25 VH, rounded up | 26.7 vs 27.2 req | m/s | `CL-C1-VD` | `CHECKED` (+1.9 %) |
| Envelope VD / q at VD | 27.2 / 453 | m/s / Pa | `CL-C1-VD-ENV`, `CL-C1-Q-VD` | `CHECKED` |
| n⁺ / n⁻ (gust peak +3.32 / −1.36) | +3.4 / −1.5 | — | `CL-C1-N-LIMIT-POS/-NEG`, `-GUST-N-*` | `CHECKED` |
| Stall-line n at VD | 5.22 vs 3.4 | — | `CL-C1-N-STALL-VD` | `FAIL`, held by F4 envelope (D-50, CR-C1-08) |
| Inertia vs A3-R5 (ratio, band 0.85–1.15) | 0.90–0.99 | — | `CL-C1-INERTIA-RATIO-MIN/-MAX` | `CHECKED` |

## Governing loads by structure

| Structure (consumer) | Quantity | Limit | Ult | Unit | Case |
|---|---|---|---|---|---|
| Spar root (C2) | bending resultant | 13.1 | 19.6 | N·m | L1 level landing |
| Spar (C2) | flap Mx | 8.0 | 12.0 | N·m | G2 tube-end carry |
| Wing (C2) | torsion / shear Vz | 5.0 / 21.5 | 7.5 / 32.3 | N·m / N | L4 / F7-VA |
| Fin joint, each side (C4, C6) | moment | 9.6 | 14.4 | N·m | L4 corner + side |
| Half-fin at wing plane, J-FINHALF (C4, C6) | torsion | 7.40 | 11.10 | N·m | L4 |
| Mount → tube (C4, C6) | force / moment | 20.8 / 0.65 | 31.2 / 0.97 | N / N·m | G3 / H5 |
| Motor plane, 7° cant incl. (C6) | side force / mount-face moment | 8.43 / 0.49 | — / 0.74 | N / N·m | F7-VA / H5 |
| Pod → wing (C3) | force | 78.3 | 117.5 | N | L1 |
| Foot, upper (C5, D5) | applied | 40.4 | 60.6 | N | L1 (D5 plateau 39.6 inside, ratio 0.980) |

## Wing limit proof (GT-08 = `T-C1-WING-PROOF`; one proof for C1 and C2, CR-C1-27)

| Load point per side | y (m) | Limit (N) | Claim |
|---|---|---|---|
| P1 / P2 / P3 / P4 | 0.120 / 0.250 / 0.355 / 0.465 | 8.95 / 7.66 / 4.44 / 6.04 | `CL-C1-PROOF-Y1..4`, `-P1..4-LIM` |
| Relief pull at the tube | 0.320 | 19.40 | `CL-C1-PROOF-R-LIM` |
| Step 2 (V-block at y 0.32), pads 3 / 4 | 0.355 / 0.465 | 4.85 / 15.85 | `CL-C1-PROOF-OUT-*` |

## Transport (D7 axes confirmed: x = chord = long walls, y = span = end walls)

| Case | n demand vs allowable | Status |
|---|---|---|
| Floor drop 0.3 m on 66 mm cradle | 10.09 vs 12.45 | `CHECKED` (+23 %) |
| Aft wall on the feet, 0.25 m | 7.79 vs 9.22 | `CHECKED` (+18 %) |

## Action items D-50 — status

| Item | Result | Status |
|---|---|---|
| Capped VH from F4 | VD 26.7 ≤ 27.2; 32.1 and 27.25 rejected | `CHECKED` |
| A3-R5 mass / inertia | read live (basic 2.3225 kg); centre-group spread matches Iyy | `CHECKED` |
| B2 c 0.32 (CLmin 0.44, CLα 3.48 /rad) | 1 g root moment 3.0942 vs B2 3.0942 N·m | `CHECKED` |
| D5 per-type feet (39.6 / 59.4 N, η 0.903) | read live; C1 bound 40.4 / 60.6 N | `CHECKED` (2 % margin, CR-C1-34) |
| 7° side force in J-MOTOR / J-FINHALF | 2.70 N in-plane vs T sin 7° 2.57 N | `CHECKED` |
| Pad 4 and half-fin torsion as claims | published | `CHECKED` |
| One wing limit proof with C2 | GT-08 runs C1's tree + step 2 | `PROPOSED` (CR-C1-27) |
| D7 box axis names | confirmed | `CHECKED` (CR-C1-31) |
| Drift (`build_graph.py`, 2026-11-10) | **0 C1 drift**, no unknown C1 ids; 583 drifts remain, all in other roles (C2, C4, C5, C6, D7, H1 re-run on R4 loads) | `CHECKED` |

## Open

1. VD rests on F4's THR_MAX cap until the H2 full-throttle level log shows ≤ 21.76 m/s (CR-C1-32).
2. Centre-group spread is at its physical cap; A3 group inertias would replace it (CR-C1-33).
3. Downstream roles re-run on R4 loads (CR-C1-28, -29); C2 should read `CL-C1-VD-ENV`.
4. Quasi-static only: no dynamic overshoot, prop imbalance or vibration (C4, `R-VIBRATION`).
