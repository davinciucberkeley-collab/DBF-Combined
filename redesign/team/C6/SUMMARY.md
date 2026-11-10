# C6 Joints and fasteners — summary

Revision C6-R4, 2026-11-10 (params A1-R4a; C1 R4; C4 fin claims `team/C4/claims.d3.json` as published at 04:28;
D3-R4). Joint stacks `PROPOSED`; claims `UNVERIFIED` (allowables wait for coupons). Re-run with
`python -I redesign/team/C6/joints.py`, then `make_stacks.py`, then `python -I redesign/proofs/build_graph.py`. R4
clears the 22 drifts: C4 re-ran its FE after R3, `ASM-D3-FILLET-LEG` was retired, and C3 and D5 moved.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Bought thread / screw lengths | M3 only / steel 8, 16; PA66 16, 18 | mm | `JOINTS.md` kit | `PROPOSED` |
| Collar torsion, max(C1, C4) + brace shear | max(7.39, 6.26) + 163 N | N·m | `CALC-C6-TUBE-BONDS` | `UNVERIFIED` |
| Collar bond RF at 12 mm (drawn) / 13 mm / 16 mm | **1.00** (0.9998 … 1.003) / 1.09 / 1.34 | — | `CL-C6-COLLAR-RF`, `-RF-13MM`, `-RF-16MM` | `UNVERIFIED`, zero margin → CR-C6-32 |
| Strip-anchor design force per strip (for H1) | **1 248** | N | `CL-C6-STRIP-ANCHOR-F` | `UNVERIFIED` |
| Strip tail anchor / tail net section | 1.27 / 1.14 | — | `CL-C6-STRIP-ANCHOR-RF`, `-TAIL-NET-RF` | `UNVERIFIED` |
| Pins: Ø 2 at 15 mm (drawn) / Ø 2.5 at 15 mm / Ø 2 at 9 mm | **0.82** / 1.59 / 1.36 | — | `CL-C6-STRIP-PIN-RF`, `-RF-PROP`, `-RF-ALT` | `FAIL` → CR-C6-31 |
| Pin force at 15 mm (C4 FE) | 72.7 | N | `CL-C4-D3-STRIP-PIN-F` | `UNVERIFIED` |
| Power frame `E-PWR-03`: 4 × M3x18 PA66, engagement / torque | 5.5 / 0.08 | mm / N·m | `CL-C6-PWR-ENGAGE-RF` 1.22, `-INSTALL-RF` 1.35 | `UNVERIFIED` |
| Power frame tension / friction / insert pull-out | 1.46 / 1.24 / 1.74 | — | `CL-C6-PWR-*`, `CL-C6-INSERT-PULL-RF` | `UNVERIFIED` |
| Foot shoe bond (D5 block), area / design / RF | 1 350 / 85.7 / 1.57 | mm² / N / — | `CL-C6-FOOT-SHOE-RF` | `UNVERIFIED` |
| Fin root fillet (15 mm zoned, as drawn) | 1.14 | — | `CL-C6-FIN-ROOT-RF` | `UNVERIFIED` |
| Mast cross-bolt `E-POD-06`, M3x16 PA66 past grip | 6.0 | mm | `joint_stacks.json` | `PROPOSED` |
| Min bond area, servo frame or horn into XPS (VD 27.2) | 719 | mm² | `CL-C6-LINK-BOND-AREA-MIN` | `UNVERIFIED` |
| Motor screws 0.20 N·m: head / separation | 1.32 / 3.73 | — | `CL-C6-MOTOR-HEAD-RF`, `-SEP-RF` | `UNVERIFIED` |
| Pod bond design / crash; hatch tab | 1.13 / 1.38; 1.18 | — | `CL-C6-POD-*` | `UNVERIFIED` |

## Produced

| File | What |
|---|---|
| `JOINTS.md` | rules, D-58 deviations, kit, fastened stacks and bonded joints keyed by interface id, inspection, tests, findings |
| `joints.py` → `claims.json` | 12 calculations, 49 claims, 10 planned tests |
| `make_stacks.py` → `joint_stacks.json` | 82 edge blocks (now with pins `E-FIN-69…80`) + 3 withdrawn (`E-MEC-03/04`, `E-PWR-05`) |
| `params.json` | C6 values (`P:joints.*`): new pin Ø 2.5, alternate pitch 9 mm, collar 13 mm |
| `CHANGE-REQUESTS.md` | CR-C6-31 … 35 and answers to every R4 action item |

## What others must act on

| Who | Action | CR |
|---|---|---|
| D3 | pins Ø 2.5 mm at the drawn 15 mm (≈ +1.5 g); collar 12 → 13 mm (≈ +0.6 g) | 31, 32 |
| C4 | freeze one R4 set of `CL-C4-D3-*` and fix the CR-C4-23 text; publish the coincident strip-pair force | 34 (29) |
| H1 | strip-anchor lever frame ≥ 1 560 N (9:1); pass line read from the claim | 33 |
| I1 | CF rod Ø 2.5 × 1 m × 2 replaces Ø 2 | 35 |
| F1, D2 | 0.08 N·m on the PA66 frame screws; boss Ø 7.2 and the unplug-moment path | 26, 27 (open) |

## Open issues

1. The Ø 2 pins fail as drawn (0.82), and the 12 mm collar sits on RF 1.00, flipping either side with each C1 run.
   Both fixes are with D3 and cost ≈ 2 g `EST` on a fins line that is already 18.4 g over.
2. C4's loads moved twice after R3 (strip 908 → 1 198 → 1 248 N; pin 64 → 92 → 73 N). Re-run `joints.py` whenever
   `claims.d3.json` changes. The tail net section is 0.57 if both strips of a pair load together (CR-C6-34).
3. Every allowable is a guess until `T-C6-*` runs (ten tests, about 1 h each, from shop stock).

## How to verify

Run the ten C6 coupons (`claims.json`), then `T-C4-FIN-PROOF` with Ø 2.5 pins and witness marks on every collar,
then re-run `joints.py` with the coupon allowables.
