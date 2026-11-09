# E1 Propulsion — summary

Status: `UNVERIFIED` (modelled from catalogue data; the thrust stand has not run). 2026-11-09.
Detail: [`PROPULSION.md`](PROPULSION.md). Model and claims: `propulsion.py` → `claims.json` (33 claims).
Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md).

## Decision

| Item | Choice | Price | Status |
|---|---|---|---|
| Motor | SunnySky X3108S KV900 (5, 1 spare) | $24.99 | `UNVERIFIED` (R and I0 from one listing) |
| ESC | LANRC BLHeli_S 45 A, Bluejay reflash (8, 4 spare); fallback Holybro Tekko32 F4 45A AM32 | $7.50 / $22.50 | `UNVERIFIED` / `CHECKED` |
| Prop | **APC 11×5.5MR/MRP** (proposed; was 11×4.5MR), plus 4 × 11×4.5MR for the stand A/B | $3.83 | `PROPOSED` (CR-E1-01, B4 to concur) |
| Current limit | `Q_M_BAT_CURR_MAX` 100 A (4 × 25 A motor rating) | — | `PROPOSED` (CR-E1-08) |

## Key numbers (2.6 kg gate, 11×5.5MR)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06) | 6.76 (689 gf) | N | `CL-E1-HOVER-T` | `UNVERIFIED` (download factor) |
| Hover pack current / power | 27.0 / 335–400 | A / W | `CL-E1-HOVER-I-55`, `CALC-E1-SENS` | `UNVERIFIED` |
| T/W: limiter, fresh pack / low pack sagged | 2.50 / 2.15 | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-ILIM-TW-LOW` | `UNVERIFIED` |
| Per-motor current with the limiter | 24.8 | A | `CL-E1-ILIM-I` | `UNVERIFIED` |
| Unlimited full throttle per motor, 14.8 / 16.8 V | 42.4 / 51.6 | A | `CL-E1-IMAX-148-55`, `CL-E1-IMAX-168-55` | `FAIL` vs `R-ESC-CURRENT` (CR-E1-07) |
| Cruise 15 m/s: thrust per prop, J, η_prop | 1.08, 0.57, 0.39 | N, —, — | `CALC-E1-CRUISE` | `UNVERIFIED` |
| Cruise power (11×4.5MR) | 176–216 (219–269) | W | `CL-E1-CRUISE-P-55`, `CL-E1-CRUISE-P-45` | `FAIL` vs params 194 W; mission passes at about 17.7 min |
| Transition thrust margin (worst point) | 2.19 | — | `CL-E1-CORRIDOR-55` | `UNVERIFIED` |
| Hover winding rise | 23 | K | `CALC-E1-HOVER` | `UNVERIFIED` (E3) |
| Motor out in hover / in cruise | fatal (yaw 0.26 > 0.15 N·m) / glide possible (0.22 N·m roll to elevons) | N·m | `CALC-E1-MOTOR-OUT` | `UNVERIFIED` |
| Propulsion mass | 422 (allocation 430) | g | `PROPULSION.md` | `UNVERIFIED` |

## Findings

- The maker's "14.8 V" table was taken on a sagging supply. Its top row (1 580 gf, 447 W) corresponds to about 11.2 V at the motor, and the W column is just 14.8 × A. The PER3 fit (kT 1.04, kP 1.24) reproduces the rows within 6 %.
- The 11×4.5MR runs close to windmilling in cruise (J 0.49 against J₀ 0.55). The 11×5.5MR cuts cruise power by about 20 % at the same price.
- Full throttle without a limiter exceeds the motor's 25 A / 30 s rating and `R-ESC-CURRENT`. With the 100 A limiter, T/W stays at 2.15 or more.

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/proofs/build_graph.py` ("every stored number re-computes"); then `T-E1-MOTOR-RM` and `T-E1-STAND`.
