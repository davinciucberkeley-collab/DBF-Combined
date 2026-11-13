# C6 Joints and fasteners — summary

> **R6 (2026-11-13, D-90, D-94, Dillon Alcouffe):** C4 re-solved on the D-65 loads, so the `-EST` set is moot.
> Collar 22 mm: `CL-C6-COLLAR-RF` 1.13 (CR-C6-37 adopted); pins at 12 mm: `CL-C6-STRIP-PIN-RF` 1.12; strip tail
> anchor 0.71 / tail net 0.64 stay open on `T-C6-LAP-PETG` and `T-C6-STRIP-ANCHOR` (contingency 62 mm solid tail,
> +29 g). Dog (D-81): `CALC-C6-DOG`, fuse 3.71 N·m, downstream RF 9.0, hold RF 2.34, `T-C6-DOG-SHEAR`. Root fillet
> RF claims are records (D-92).

Revision C6-R5b, 2026-11-10 (params A1-R5; C1 claims and `data/envelope.json` of 14:35 read live; C4's frozen R4 set
`team/C4/claims.d3.json` of 11:51; fins D3-R5b; D5 R5). Joint stacks `PROPOSED`; claims `UNVERIFIED` until the
coupons run. Re-run with `python -I redesign/team/C6/joints.py`, then `make_stacks.py`, then
`python -I redesign/proofs/build_graph.py`. The R5 items are done: D-70 pins pass and D-68 pocket rules are issued.
The fin station is not closed. C1's D-65 re-run took the half-fin torsion from 7.39 to **12.67 N·m** during this
session, so the collar fails as drawn, and C4's frozen set is stale by ×1.71.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Bought thread / screw lengths | M3 only / steel 8, 16; PA66 16, 18 (+ Ø 2.5 CF rod pins) | mm | `JOINTS.md` kit | `PROPOSED` |
| Collar torsion, max(C1, C4) + brace shear | max(**12.67**, 6.24) + 163 | N·m, N | `CALC-C6-TUBE-BONDS` | `UNVERIFIED` |
| Collar height needed / drawn 15 mm RF / 22 mm RF | **19.45** / **0.77** / 1.13 | mm / — / — | `CL-C6-COLLAR-L-REQ`, `-RF`, `-RF-PROP` | `FAIL` → CR-C6-37 |
| Pins Ø 2.5 at 15 mm (drawn, D-70), C4 R4 load 72.4 N | 1.60 (bearing 3.45, strip net 2.41) | — | `CL-C6-STRIP-PIN-RF` | `UNVERIFIED` |
| Strip tail anchor / tail net, C4 R4 1 243 N | 1.27 / 1.15 | — | `CL-C6-STRIP-ANCHOR-RF`, `-TAIL-NET-RF` | `UNVERIFIED` |
| Load scale k = C1 now / C4's solved torsion | 1.71 | — | `CL-C6-FIN-LOAD-SCALE` | `UNVERIFIED` |
| D-65 estimate: strip force / anchor / tail net / pins | 2 131 N / **0.74** / **0.67** / **0.93** | N / — | `CL-C6-*-EST` | `FAIL` (est.) → CR-C6-38 |
| Tube in block / block on spar | 2.65 / 4.64 | — | `CL-C6-TUBE-BLOCK-RF`, `-BLOCK-SPAR-RF` | `UNVERIFIED` |
| Block pocket (D-68): square-corner void / max pocket R / beads | 1.24 / 4.2 / 1.1 g | mm / mm / g | `CL-C6-POCKET-*` | `PROPOSED` → CR-C6-40 |
| Root fillet, fail-safe only (D-68), D-65 side load | 0.81 | — | `CL-C6-FIN-ROOT-RF` | `FAIL` → D3 CR-D3-35 |
| Foot shoe bond (D5 R5), area / design / RF | 1 350 / 85.7 / 1.57 | mm² / N / — | `CL-C6-FOOT-SHOE-RF` | `UNVERIFIED` |
| Power frame `E-PWR-03`, 4 × M3x18 PA66, engagement / torque | 5.5 / 0.08 (install 1.35, tension 1.46, insert 1.74) | mm / N·m | `CL-C6-PWR-*` | `UNVERIFIED`, open with F1 |
| Motor screws 0.20 N·m: head / separation | 1.32 / 3.69 | — | `CL-C6-MOTOR-HEAD-RF`, `-SEP-RF` | `UNVERIFIED` |
| Pod bond design / crash; floor line with fillet; hatch | 1.15 / 1.33; 2.03; 1.18 | — | `CL-C6-POD-*` | `UNVERIFIED` |
| Min bond area, servo frame or horn into XPS | 719 | mm² | `CL-C6-LINK-BOND-AREA-MIN` | `UNVERIFIED` |

## Produced

| File | What |
|---|---|
| `JOINTS.md` | what changed since R4, verdict, rules, kit, joint-stack and bond tables by interface id, inspection, tests, findings |
| `joints.py` → `claims.json` | 14 calculations, 63 claims, 10 planned tests; C1 envelope now read live; new `CALC-C6-BLOCK-POCKET`, `CALC-C6-FIN-SCALE` |
| `make_stacks.py` → `joint_stacks.json` | 82 edge blocks + 3 withdrawn; `E-FIN-13…16`, `29…36`, `51/52`, `53…56`, `69…80` rewritten |
| `params.json` | `P:joints.*`: collar 22 mm proposal, D-70 12 mm condition, Ø 2 fallback pin, bond-line and bead rules |
| `CHANGE-REQUESTS.md` | CR-C6-36 … 41 and answers to every R5 action item |

## What others must act on

| Who | Action | CR |
|---|---|---|
| D3 (cc A1) | collar 15 → **22 mm** (≈ +4.4 g `EST`); hold collar, tail and pin prints for C4 | 37, 38 |
| C4 | re-run the fin FE on the D-65 loads; publish one new frozen set + coincident pair force + fillet-intact share | 38 |
| H1 | strip-anchor frame ≥ 2 660 N | 39 |
| D1 | pocket corners R 3.0–4.2 mm or packed; feeler dry-fit; beads both surfaces | 40 |
| C1 | publish the governing case with the torsion claim; announce moves > 5 % | 41 |
| F1, D2 | 0.08 N·m on the PA66 frame screws; boss Ø 7.2 and the unplug-moment path | 26, 27 (open) |

## Open issues

1. The collar, strip tail, tail net section and pins are not closed on the D-65 loads. The `-EST` claims are
   linear scalings of C4's R4 set; they retire when C4 re-runs.
2. C1 moved three times today. Re-run `joints.py` whenever `team/C1/claims.json`, `team/C1/data/envelope.json` or
   `team/C4/claims.d3.json` changes.
3. Mass: the 22 mm collar and any CR-C6-38 changes land on a fins line with 0 g free reserve. A1 has to decide.
4. Every allowable is a guess until `T-C6-*` runs (ten tests, about 1 h each, from shop stock).

## How to verify

Run `T-C6-LAP-PETG` before any collar prints (the height scales with it), then the other nine C6 coupons, then
`T-C4-FIN-PROOF` with witness marks on every collar. After C4 re-runs, re-run `joints.py` and drop the `-EST` claims.
