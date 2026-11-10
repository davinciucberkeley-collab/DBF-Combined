# E1 Propulsion — summary

Status: performance `UNVERIFIED` (catalogue data; the thrust stand has not run) · stations `MODELLED` (Fusion
module; `check.py` propulsion `ok`, 0 errors). Revision 5, 2026-11-09. Detail: [`PROPULSION.md`](PROPULSION.md).
Model and claims: `propulsion.py` → `claims.json` (61 claims). Subsystem: [`subsystems/propulsion/SPEC.md`](../../subsystems/propulsion/SPEC.md).
Requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (rev 5: CR-E1-35 to -43).

## Decision

| Item | Choice | Price | Status |
|---|---|---|---|
| Motor | SunnySky X3108S KV900 (5, 1 spare) | $24.99 | `UNVERIFIED` (R, I0 agree across 2 listings) |
| ESC | LANRC BLHeli_S 45 A, Bluejay, carried stripped of power leads (8, 4 spare); fallback Tekko32 F4 45A AM32 | $7.50 / $22.50 | `UNVERIFIED` / `CHECKED` |
| Prop | APC 11×5.5MR/MRP (8) + 11×4.5MR/MRP (4, stand A/B) | $3.83 | `CHECKED` (D-05) |
| Prop adapter | Bolt-on M6×1, 2 RH + 2 LH (Small Parts CNC set), M3×4 under D-58; M3×5 if the bell allows | $23.95 / set | `CHECKED`, out of stock |
| Current limit | `Q_M_BAT_CURR_MAX` 100 A | — | `PROPOSED` |

## Key numbers (2.6 kg gate, 11×5.5MR, cruise 16 m/s)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 7°) / pack current | 6.81 / 27.3 | N / A | `CL-E1-HOVER-T`, `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W fresh pack with the limiter / worst pack state (limits 2.0 / 1.6) | 2.47 / 2.12 | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Sag factor (re-run on `r_ext` 6.5 mΩ, CR-E2-17) | 0.851 | — | `CL-E1-SAG-FACTOR` | `UNVERIFIED` |
| Per-motor current with the limiter / unlimited burst at 16.8 V | 24.75 / 51.6 | A | `CL-E1-ILIM-I`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Pack current with the limiter (to A2 for `R-ESC-CURRENT`) | 100 | A | `CL-E1-IPACK-LIM` | `UNVERIFIED` |
| Cruise propulsion power (16 m/s) | 234 | W | `CL-E1-CRUISE-P-55` | `UNVERIFIED` |
| Motor out in hover: T/W left | 1.07 | — | `CL-E1-MOTOROUT-TW` | `UNVERIFIED` |
| Propulsion mass vs allocation (ESC 7.6 g stripped, D-48) | 462.0 / 462 | g | `CL-E1-MASS-PRP` | `UNVERIFIED` (weigh) |
| Prop keep-out on the 7° axis: radius / axial half | 164.7 / 35 | mm | `CL-E1-KO-HALF` | `MODELLED` (0 hits) |
| Adapter screws: bell thread needed for D-58 / free depth for M3×5 | 2.5 / 4.0 | mm | `CL-E1-ADAPTER-THREAD-D58`, `-M3X5-DEPTH` | `UNVERIFIED` (measure) |
| Adapter strip RF at 2.0 / 2.5 mm, 0.5 N·m (≥ 1.5) | 1.70 / 2.12 | — | `CL-E1-ADAPTER-STRIP`, `-RF-NOM` | `UNVERIFIED` |
| ESC envelope for B4: proud of the pad / frontal | 7.5 / 172.5 | mm / mm² | `CL-E1-ESC-PROUD`, `-FRONTAL` | `UNVERIFIED` |
| Prop plane to collar / 0.14 D | 0.97 | — | `CL-E1-CAD-PROP-GAP` | `FAIL` → D3 `face_ahead_m` 0.0025 (D-51) |
| ESC strap-slot clearance ratio (pad 28 mm) | 0.90 | — | `CL-E1-ESC-SLOT` | `FAIL` → D3 pad 31 mm (D-51) |

## Rev 5 actions

| Item | Done | Status |
|---|---|---|
| CR-A1-48 re-run | `propulsion.py` → `make_propulsion.py`; `PRP-002` 7.6 g; CAD centroids in `interfaces.json` | `CHECKED` |
| CR-A5-21 | `k9.prop_keepout(..., rotate=rot, blade_half=0.010)`; `ASM-E1-BLADE-HALF` 8 → 10 mm | `CHECKED` (`check.py`) |
| CR-A4-43 / D-58 | M3×4 2.5 mm under the deviation, condition as a claim and a `T-E1-MOTOR-RM` step; M3×5 rule in `PROPULSION.md` | `PROPOSED` |
| CR-D3-22, lead reach | base Ø ≥ 28 mm, 16 × 19 mm, hole ≥ 4.0 mm, lead vs 0.121 m added to `T-E1-MOTOR-RM` and `BUILD.md` | `PROPOSED` |
| Acknowledgements | 16 declared (`E-FIN-61…68`, `E-HRN-17…20`, `E-TRN-17…20`); 20 in `acknowledges_pending` (`E-HRN-13…16`, `-24…27`, `-34…37`, `E-FIN-81…88`) | `CHECKED` |
| `ASM-E1-PACK` | kept: B4's `props.py` still reads it (CR-E1-37) | open |

Checks (2026-11-09): `fusion/check.py` propulsion `ok`, 0 errors, 0 keep-out hits; WARN `mass` 462 g at zero margin
(floating-point) and 8 `unpowered` (power edges not declared). `merge_check.py` 0 propulsion errors.
`build_graph.py`: no `CALC-E1` drift, no E1 errors (other roles' drift remains). Three E1 claims fail on D3 keys
that A1 has adopted but `fins/params.json` does not carry yet (CR-E1-38).

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/subsystems/propulsion/make_propulsion.py` →
`python -I redesign/fusion/check.py` → `python -I redesign/proofs/build_graph.py`; hardware `T-E1-MOTOR-RM`
(masses, base Ø and pattern, hole depth, bell thread and free depth, lead length, ESC height, R, I0), `T-E1-STAND`,
`T-C6-PROPNUT`.
