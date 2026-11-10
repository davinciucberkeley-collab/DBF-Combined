# E1 Propulsion — summary

Status: performance `UNVERIFIED` (catalogue data; the thrust stand has not run) · stations `MODELLED` (Fusion
module; `check.py` propulsion 0 errors). Revision 4, 2026-11-09. Detail: [`PROPULSION.md`](PROPULSION.md). Model and
claims: `propulsion.py` → `claims.json`. Subsystem: [`subsystems/propulsion/SPEC.md`](../../subsystems/propulsion/SPEC.md).
Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (rev 4: CR-E1-22 rev, CR-E1-29 to -34).

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
| Hover thrust per motor (download 1.06, cant 7°) | 6.81 | N | `CL-E1-HOVER-T` | `UNVERIFIED` |
| Hover pack current | 27.3 | A | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W fresh pack with the limiter / worst pack state | 2.47 / 2.12 (limits 2.0 / 1.6) | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Per-motor current with the limiter / unlimited burst at 16.8 V | 24.75 / 51.6 | A | `CL-E1-ILIM-I`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Cruise propulsion power (16 m/s) | 234 | W | `CL-E1-CRUISE-P-55` | `UNVERIFIED` |
| Mount face → prop mid-plane (stack) | 37.3 | mm | `CL-E1-STACK-PROP-PLANE` | `UNVERIFIED` |
| Modelled hub x on the canted axis / vs datum `DP-PROP` | −0.0062 m / +2.0 mm | — | `CL-E1-CAD-HUB-X`, `-VS-DATUM` | `MODELLED` |
| Prop plane to collar / 0.14 D | 0.97 | — | `CL-E1-CAD-PROP-GAP` | `FAIL` → CR-E1-22 |
| Canted-disc tip excursion / keep-out half | 25.0 / 33 | mm | `CL-E1-KO-TILT` | `CHECKED` |
| ESC strap-slot clearance ratio (pad 28 mm) | 0.90 | — | `CL-E1-ESC-SLOT` | `FAIL` → CR-E1-30 |
| Adapter M3×4 thread strip RF (2.0 mm, 0.5 N·m) | 1.70 (≥ 1.5) | — | `CL-E1-ADAPTER-STRIP` | `UNVERIFIED` |
| Propulsion mass vs allocation (D-34) | 475.6 / 476 | g | `CL-E1-MASS-PRP` | `UNVERIFIED` (weigh) |

## Rev 4 deliverables (`subsystems/propulsion/`)

| File | What | Status |
|---|---|---|
| `fusion/propulsion.py` | 16 components: motor (base boss, bell, shaft, E-clip, lead exit), adapter + washer + nut, prop (hub + twisted blades), ESC; each stack rotated 7° onto D3's canted plate; rigid joints `E-PRP-01…08`; `KO-PROP-<st>` | `MODELLED`, `UNVERIFIED-IN-FUSION` |
| `make_propulsion.py` | writes `interfaces.json` (CAD-centroid CGs, joint stacks, 16 acknowledgements) from the module and `parts.csv` | `CHECKED` |
| `params.json` · `parts.csv` | bought-part envelopes and spares · per-unit masses (written by `propulsion.py`) | `UNVERIFIED` |
| `SPEC.md` · `BUILD.md` | one page · nine numbered steps for G4 | `PROPOSED` |

Checks (2026-11-09): `fusion/check.py` propulsion `ok`, 0 errors, 8 WARN `unpowered` (ESC power edges wait for the
`PWR` nodes); every touch, joint-origin, wire-end and keep-out check on PRP parts passes. `merge_check.py` 0
propulsion errors. `build_graph.py` no `CALC-E1` drift (other roles' drift remains).

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/subsystems/propulsion/make_propulsion.py` →
`python -I redesign/fusion/check.py` → `python -I redesign/proofs/build_graph.py`; hardware `T-E1-MOTOR-RM`
(masses, bolt pattern, hole and bell-thread depth, lead and post length, R, I0), `T-E1-STAND`, `T-C6-PROPNUT`.
