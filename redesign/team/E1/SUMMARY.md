# E1 Propulsion — summary

Status: `UNVERIFIED` (modelled from catalogue data; the thrust stand has not run). Revision 2, 2026-11-09.
Detail: [`PROPULSION.md`](PROPULSION.md). Model and claims: `propulsion.py` → `claims.json` (38 claims) and
`subsystems/propulsion/parts.csv`. Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (CR-E1-14 to -21 are new).

## Decision

| Item | Choice | Price | Status |
|---|---|---|---|
| Motor | SunnySky X3108S KV900 (5, 1 spare) | $24.99 | `UNVERIFIED` (R, I0 agree across 2 listings) |
| ESC | LANRC BLHeli_S 45 A, Bluejay (8, 4 spare); fallback Tekko32 F4 45A AM32 | $7.50 / $22.50 | `UNVERIFIED` / `CHECKED` |
| Prop | APC 11×5.5MR/MRP (8) + 11×4.5MR/MRP (4, stand A/B) | $3.83 | `CHECKED` (D-05) |
| Prop adapter | Bolt-on M6×1, 2 RH + 2 LH (Small Parts CNC set) | $23.95 / set | `CHECKED`, out of stock |
| Current limit | `Q_M_BAT_CURR_MAX` 100 A | — | `PROPOSED` |

## Key numbers (2.6 kg gate, 11×5.5MR, cruise 16 m/s)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 3°) | 6.77 | N | `CL-E1-HOVER-T` | `UNVERIFIED` |
| Hover pack current / power | 27.1 / 335–401 | A / W | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W fresh pack with the limiter | 2.50 | — | `CL-E1-ILIM-TW-FRESH` | `UNVERIFIED` |
| **T/W worst pack state (one E1 + E2 claim)** | **2.18** (limit 1.6) | — | `CL-E1-TW-WORST` | `UNVERIFIED` |
| Sag factor, worst ÷ fresh (replaces params 0.72) | 0.854 | — | `CL-E1-SAG-FACTOR` | `UNVERIFIED` |
| Per-motor current with the limiter | 24.8 | A | `CL-E1-ILIM-I` | `UNVERIFIED` |
| Cruise pack power | 201–247 | W | `CL-E1-CRUISE-P-55` | `UNVERIFIED` |
| Transition thrust margin (worst point) | 2.19 | — | `CL-E1-CORRIDOR-55` | `UNVERIFIED` |
| Motor out: hover T/W / cruise roll torque | 1.09 (fatal: yaw) / 0.23 | — / N·m | `CL-E1-MOTOROUT-*` | `UNVERIFIED` |
| Mount face to prop mid-plane | 37.3 | mm | `CL-E1-STACK-PROP-PLANE` | `UNVERIFIED` |
| Propulsion mass incl. leads, adapters, screws | 475.6 (allocation 440) | g | `CL-E1-MASS-PRP` | `FAIL` |

## Action items closed this revision

| Item | Result | Status |
|---|---|---|
| Re-run `propulsion.py` (drift) | Re-run on the current params (16 m/s, c 0.32, L/D 5.6, cant 3°); `build_graph.py` shows no `CALC-E1` drift. The remaining errors are A5, B2, B3 and E2 drift (E2 is downstream of my new cruise power) | `CHECKED` |
| Sag 0.72 vs 0.86 | One claim, `CL-E1-TW-WORST` 2.18, from my station model with E2's pack assumptions. E2's (V/V)² on an already current-limited thrust counted the sag twice (CR-E1-15) | `MODELLED` |
| CR-A3-05 | `subsystems/propulsion/parts.csv`: 5 lines, 118.9 g per station; motor 81 g with factory leads, ESC 11 g `EST` with leads | `MODELLED` |
| CR-A4-06, CR-A5-06 | Bolt pattern not published: slotted mount until measured. M3×8, 5 mm plate, 3.0 mm engagement. Bolt-on M6 adapter (LH on CW motors). Hub 8.9 mm; stack 37.3 mm to the mid-plane, 48.1 mm to the post tip (CR-E1-16, -17) | `UNVERIFIED` |

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/proofs/build_graph.py` (no `CALC-E1` drift); then
`T-E1-MOTOR-RM` (incoming: masses, bolt pattern, hole depth, lead length, R, I0) and `T-E1-STAND` (fresh pack and a cold
pack at 3.73 V/cell).
