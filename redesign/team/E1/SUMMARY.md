# E1 Propulsion — summary

Status: performance `UNVERIFIED` (catalogue data; the thrust stand has not run) · stations `MODELLED` (Fusion
module; `check.py` propulsion `ok`, **0 keep-out ERRORs**) · prop clearance `MODELLED` (26.1 mm vs 25 mm) · cruise
power **`FAIL`** (246 W vs 240 W; CR-E1-51 to A1). Revision 8, 2026-11-10. Detail: [`PROPULSION.md`](PROPULSION.md).
Model and claims: `propulsion.py` → `claims.json` (66 claims); clearance probe `prop_clearance.py` →
`prop_clearance.json`. Subsystem: [`subsystems/propulsion/SPEC.md`](../../subsystems/propulsion/SPEC.md). Requests:
[`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (rev 8: CR-E1-51 to -54).

## Decision

| Item | Choice | Price | Status |
|---|---|---|---|
| Motor | SunnySky X3108S KV900 (5, 1 spare) | $24.99 | `UNVERIFIED` (R, I0 agree across 2 listings) |
| ESC | LANRC BLHeli_S 45 A, Bluejay, carried stripped of power leads (8, 4 spare); fallback Tekko32 F4 45A AM32 | $7.50 / $22.50 | `UNVERIFIED` / `CHECKED` |
| Prop | APC 11×5.5MR/MRP (8) + 11×4.5MR/MRP (4, stand A/B) | $3.83 | `CHECKED` (D-05) |
| Prop adapter | Bolt-on M6×1, 2 RH + 2 LH (Small Parts CNC set), M3×4 under D-58; M3×5 if the bell allows | $23.95 / set | `CHECKED`, out of stock |
| Current limit | `Q_M_BAT_CURR_MAX` 100 A | — | `PROPOSED` |
| Mount stand-off | `face_ahead_m` 0.0075 m (D-61, carried); least 0.0065 | — | `MODELLED` |

## Key numbers (2.6 kg gate, 11×5.5MR, cruise 16 m/s)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 7°) / pack current | 6.81 / 27.3 | N / A | `CL-E1-HOVER-T`, `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W fresh pack with the limiter / worst pack state (limits 2.0 / 1.6) | 2.47 / 2.12 | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Sag factor on `r_ext` 6.7 mΩ (D-67) / closed-form check | 0.8508 / 0.873 | — | `CL-E1-SAG-FACTOR`, `-SAG-XCHECK` | `UNVERIFIED` |
| Per-motor current with the limiter / unlimited burst at 16.8 V | 24.75 / 51.6 | A | `CL-E1-ILIM-I`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Pack current with the limiter | 100 | A | `CL-E1-IPACK-LIM` | `UNVERIFIED` |
| Cruise drag / L/D eff on `CL-B1V-CD0` 0.0579, `CL-B1V-K` 0.0957 | 4.51 / **5.66** | N / — | `CL-E1-CRUISE-DRAG`, `-LD-EFF` | `UNVERIFIED` (A1 copies `ld_cruise`) |
| **Cruise propulsion power (kP 1 → 1.24) / limit** | **200–246 / 240** | W | `CL-E1-CRUISE-P-55`, `-P-55-LO` | **`FAIL`** (+2.5 %) |
| Cruise power at 15 m/s (option in CR-E1-51) | 214 | W | sweep in `PROPULSION.md` | `UNVERIFIED` |
| Transition corridor margin / motor out hover T/W | 2.12 / 1.07 | — | `CL-E1-CORRIDOR-55`, `-MOTOROUT-TW` | `UNVERIFIED` |
| ESC / motor peak, mission at 30 °C (E3, limits 85 / 80) | 56.1 / 64.8 | °C | `CL-E3-ESC-PEAK`, `-MOTOR-PEAK` | `UNVERIFIED` |
| Propulsion mass vs allocation (D-48) | 462.0 / 462 | g | `CL-E1-MASS-PRP` | `UNVERIFIED` (weigh) |
| Prop hub x (datum −0.0127; D3 `CL-D3-X-PROP` −0.012672) | −0.01267 | m | `CL-E1-CAD-HUB-X` | `MODELLED` |
| Blade swept volume to CF motor tube (probe 26.2) | **26.1** (limit 25) | mm | `CL-E1-TIP-GAP-TUBE` | `MODELLED` |
| Least `face_ahead` for 25 mm | 6.5 | mm | `CL-E1-FACE-AHEAD-FOR-CLR` | `MODELLED` |
| Prop plane to collar ÷ 0.14 D / ESC strap-slot ratio | 1.14 / 1.05 | — | `CL-E1-CAD-PROP-GAP`, `CL-E1-ESC-SLOT` | `MODELLED` |
| Keep-out reach fwd / aft of hub mid-plane / half-length | 35 / 31 / 33 | mm | `CL-E1-KO-FWD`, `-KO-AFT`, `-KO-HALF` | `CHECKED` (`check.py`) |

## CAD centroids for A3 (rev 8, `subsystems/propulsion/interfaces.json`)

| Part (UR; mirror y for L, z for lower) | Mass | x / y / z | Δx vs rev 7 | Status |
|---|---|---|---|---|
| `PRP-001` motor | 84.2 g | 0.0106 / 0.3210 / 0.1885 m | −5.0 mm | `MODELLED` |
| `PRP-003` prop | 17.0 g | −0.0127 / 0.3223 / 0.1861 m | −5.0 mm | `MODELLED` |
| `PRP-004` adapter | 6.7 g | −0.0096 / 0.3221 / 0.1864 m | −5.0 mm | `MODELLED` |
| `PRP-002` ESC | 7.6 g | 0.101 / 0.329 / 0.118 m | 0 | `MODELLED` |
| Effect on the aircraft CG at 2.6 kg | — | −0.83 mm in x (D-62 counted −0.9) | — | `CHECKED` |

## Rev 8 action items

| Item | Done | Status |
|---|---|---|
| Re-run on D3's 7.5 mm mount | `propulsion.py`, `make_propulsion.py`, `prop_clearance.py`; hub −0.01267 matches D3's −0.012672 | `CHECKED` |
| `check.py` keep-out errors | **0** (rev 7: 4) | `CHECKED` |
| `CALC-E1-WORST` on `r_ext` 6.7 | sag 0.8508, T/W worst 2.12: `voltage_sag` 0.851 stands | `UNVERIFIED` |
| `CL-E1-CRUISE-P-55` / `-LD-EFF` on `CL-B1V-CD0` / `-K` | 246.0 W `FAIL`, L/D 5.66; CR-E1-51 (252 W or 15 m/s; `ld_cruise` 5.66) | `FAIL` → A1 |
| SPEC thermal row | 56.1 / 64.8 °C; stale FAIL rows and the pending list corrected | done |
| `E-FIN-81…88` | acknowledged (36 acknowledged, 0 pending) | `CHECKED` |
| Model fix | `CALC-E1-TIP-GAP` bisection starts at 0, so the least `face_ahead` reads 6.5 mm, not the carried 7.5 | `CHECKED` |

Checks (rev 8, 2026-11-10): `fusion/check.py` propulsion `ok`, 0 keep-out ERRORs; overall FAIL on 20 errors in
the pod and avionics modules (pod `pack_aft_face_m` vs `pack_x_nominal_m`, other roles); WARN `mass` 462 g at zero
margin (floating point). `merge_check.py`: PASS, 0 errors. `build_graph.py` on the E1 folder alone: 0 `CALC-E1` drift (only the expected cross-folder references unresolved); the full-tree run did not finish in 35 min on the shared machine.
`plots.py` not re-run (local matplotlib lacks `packaging`); FIG PRP-01 still draws the rev 3 drag line.

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/subsystems/propulsion/make_propulsion.py` →
`python -I redesign/team/E1/prop_clearance.py` (about 75 s) → `python -I redesign/fusion/check.py` →
`python -I redesign/proofs/build_graph.py`; hardware `T-E1-MOTOR-RM` (masses, base Ø and pattern, hole depth, bell
thread and free depth, lead length, ESC height, R, I0, 25 mm gauge at the tube), `T-E1-STAND`,
`T-B1-CRUISE-POWER` (settles CR-E1-51), `T-C6-PROPNUT`.
