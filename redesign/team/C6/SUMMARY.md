# C6 Joints and fasteners — summary

Revision C6-R1, 2026-11-09 (params A1-R2, C1-R2 loads). Joint stacks `PROPOSED`; claims `UNVERIFIED` (allowables
await coupons). Re-run: `python -I redesign/team/C6/joints.py` → `make_stacks.py` → `python -I redesign/proofs/build_graph.py`
(0 C6 errors).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Bought thread sizes / screw lengths | 1 (M3) / 3 (8, 10, 16) | — | `JOINTS.md` kit | `PROPOSED` |
| Motor screw torque (was 0.5) | 0.20 | N·m | `P:joints.torque.motor_screw_nm` | `PROPOSED` |
| Motor screw head bearing RF at 0.20 / 0.5 N·m | 1.32 / 0.53 | — | `CL-C6-MOTOR-HEAD-RF` | `UNVERIFIED` |
| Mount collar under the 3.2 N·m prop-nut case | RF 3.26 | — | `CL-C6-MOUNT-ROCK-RF` | `UNVERIFIED` |
| Pinch bolt past the grip / needed | 5.5 / 5.0 | mm | `CL-C6-PINCH-ENGAGE-RF` | `UNVERIFIED` |
| FC screw in heat-set insert / needed | 5.6 / 4.5 | mm | `CL-C6-FC-ENGAGE-RF` | `UNVERIFIED` |
| Tube-in-block / block-on-spar bond | RF 6.26 / 5.67 | — | `CL-C6-TUBE-BLOCK-RF`, `-BLOCK-SPAR-RF` | `UNVERIFIED` |
| Station collar bond, C1 / C4 torsion | RF 1.60 / 0.91 | — | `CL-C6-COLLAR-RF`, `-COLLAR-L-REQ` | `FAIL` (C4) |
| Edge-strip anchorage, as drawn / 40 mm tail | RF 0.30 / 1.19 | — | `CL-C6-STRIP-ANCHOR-RF`, `-PROP` | `FAIL` / `PROPOSED` |
| Strip shear on paper face, bare / pinned | RF 0.20 / 1.41 | — | `CL-C6-STRIP-FACE-RF`, `-PIN-RF` | `FAIL` / `PROPOSED` |
| Brace end / anchor pull-off | RF 2.93 / 1.80 | — | `CL-C6-BRACE-END-RF`, `-ANCHOR-PULL-RF` | `UNVERIFIED` |
| Foot shoe / fin root / pod bond | RF 1.35 / 1.12 / 2.09 | — | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF`, `-POD-WING-RF` | `UNVERIFIED` |
| Min bond area, servo frame or horn into XPS | 720 | mm² | `CL-C6-LINK-BOND-AREA-MIN` | `UNVERIFIED` |
| Foot snap-hook finger length | ≥ 6.0 | mm | `CL-C6-SNAP-L-MIN` | `PROPOSED` |
| Design allowables: PETG/CF bond, XPS, paper face | 2.0, 0.125, 0.10 | MPa | `ASM-C4-BOND-SHEAR`, `ASM-C6-FOAM-KD` | `UNVERIFIED` |

## Produced

| File | What |
|---|---|
| `JOINTS.md` | rules, fastener kit, fastened joint stacks and bonded joints keyed by interface id, inspection, findings |
| `joints.py` → `claims.json` | 9 calculations, 25 claims, 7 planned tests |
| `make_stacks.py` → `joint_stacks.json` | 67 edge blocks (`joint_stack`, `clamp`, `bond`) in SCHEMA names for the owners |
| `params.json` | C6 local values (`P:joints.*`): ISO hardware sizes, torques, proposals |
| `CHANGE-REQUESTS.md` | CR-C6-01 … 15 and answers to CR-C1-11, CR-A4-10/20, CR-C4-10, CR-D5-04 |

## What others must act on

| Who | Action | CR |
|---|---|---|
| D3 | 40 mm two-face collar tail; CF through-pins on the strips; collar 16 mm; motor screws 0.20 N·m, drilled pattern | 01, 02, 03, 10 |
| C4 / C1 | agree the collar torsion; confirm strip shear flow | 02, 03 |
| E1 | motor screw torque and no slots; prop-nut engagement | 10 |
| A1 / A2 | one 10 mm prop spanner at the field; per-type engagement rule | 05, 06 |
| E3 | collar temperature vs epoxy Tg | 04 |
| D2, D5, D6, D7, I1, H1, A4 | pitot flange and mast grip; snap finger; hardpoint area; M3 handles; kit; coupons; merge | 07–09, 11–15 |

## Open issues

1. Allowables are guesses until `T-C6-*` coupons run (≈ 1 h, shop stock). Thin: fin root 1.12, strip tail 1.19.
2. Brace force is C4's 10 × 2 model; C4 re-runs with the 10 × 3 brace.
3. Motor pattern, hole depths and the FC grommet stack are measured on arrival.

## How to verify

Run the seven C6 coupons (`claims.json`), then `T-C4-FIN-PROOF` and `T-C4-BLOCK-PROOF` with witness marks on every
collar; re-run `joints.py` with the coupon allowables.
