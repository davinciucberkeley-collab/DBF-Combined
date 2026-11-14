# E1 Propulsion — summary

Status: performance `UNVERIFIED` (catalogue data; the thrust stand has not run) · stations `MODELLED` (Fusion
module; `check.py` propulsion `ok`, **0 keep-out ERRORs**) · prop clearance `MODELLED` (26.1 mm vs 25 mm) · cruise
power **`FAIL`** (246 W vs 240 W; CR-E1-51 to A1). Revision 8, 2026-11-10. Detail: [`PROPULSION.md`](PROPULSION.md).
Model and claims: `propulsion.py` → `claims.json` (84 claims since rev 9); clearance probe `prop_clearance.py` →
`prop_clearance.json`. Subsystem: [`subsystems/propulsion/SPEC.md`](../../subsystems/propulsion/SPEC.md). Requests:
[`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (rev 8: CR-E1-51 to -54).

## Rev 9, 2026-11-13: CDR fix round (CDR-05, CDR-29; D-115, D-116, D-118, D-119)

Source of every value: `team/E1/claims.json`, written by `python -I redesign/team/E1/propulsion.py` on 2026-11-13.
Nothing is tested; all of it is `UNVERIFIED` until `T-E1-STAND`.

| Item | Before (rev 8) | Now | Limit | Claim | Result |
|---|---|---|---|---|---|
| Path resistance read by the model | 6.7 mΩ | **7.9 mΩ** | — | `P:electrical.r_ext_mohm` (D-115; `CL-F1-R-EXT` 7.92) | — |
| T/W, worst pack state | 2.120 | **2.106** | ≥ 1.6 | `CL-E1-TW-WORST` | passes, +32 % |
| T/W, fresh pack, 100 A limiter (no cant, older fresh case) | 2.466 | **2.453** | ≥ 2.0 | `CL-E1-ILIM-TW-FRESH` | passes, +23 % |
| Full thrust per motor, worst state | 1 389 gf | **1 379 gf** | — | `CL-E1-TMAX-WORST` | — |
| Sag factor worst / fresh | 0.8508 | **0.8497** | — | `CL-E1-SAG-FACTOR` (cross-check 0.8718) | — |
| **Motor current at the 100 A limiter, fresh pack** | 24.75 A (battery side) | **30.0 A in the winding** (24.75 A battery side, now `CL-E1-ILIM-I-BAT`) | ≤ 25 A (maker, 25 A / 30 s) | `CL-E1-ILIM-I` | **FAILS, −20 %** |
| Same, worst pack state, 80 °C winding | — | 25.8 A | ≤ 25 A | `CL-E1-ILIM-I-WORST` | fails, −3 % |
| Same, fresh, second bound | — | 25.7 A | ≤ 25 A | `CL-E1-ILIM-I-B2` | fails, −3 % |
| Pack-current limit that holds 25 A in the winding | — | 71.1 A, T/W 2.04 fresh | ≥ 2.0 | `CL-E1-ILIM-FOR-25A`, `CL-E1-ILIM-25A-TW` | passes, +2 % |
| T/W worst state, **second bound** (maker's rows above 12 A read as true 14.8 V points) | — | **1.72** (1 126 gf) | ≥ 1.6 | `CL-E1-TW-WORST-B2` | passes, +8 % |
| T/W fresh, second bound | — | 2.10 | ≥ 2.0 | `CL-E1-TW-FRESH-B2` | passes, +5 % |
| Thrust per motor at a held 11.9 V bus (the stand point of CDR condition B-7): first bound / second bound / rpm ∝ bus voltage | — | 1 392 / 1 090 / **972 gf** | ≥ 1 048 gf (`CL-E1-T-NEED-SAG`; the board's line is 1 060) | `CL-E1-T-STAND-B2`, `CL-E1-T-STAND-B2-PROP` | second bound passes, +4 %; **the rpm ∝ V reading FAILS, −7 %** |
| Path resistance the thrust requirement allows | — | 17.1 mΩ (first bound alone 42.5) | ≥ 7.9 mΩ | `CL-E1-REXT-ALLOW` | passes, +116 % |
| 100 A drop the thrust requirement allows (F1's new limit) | — | 11.5 % | — | `CL-E1-DROP-ALLOW` | limit of `CL-F1-DROP-PEAK` (5.68 %) |
| Worst-state thrust lost to the 7.9 mΩ path | — | 4.2 % (second bound 6.5 %) | — | `CL-E1-PATH-THRUST-COST` | — |
| Cruise power at the 17 m/s fallback (D-96 c, decision B6), propulsion only | 283 W (CR-E1-51 sweep, no claim) | 283.5 W | — | `CL-E1-CRUISE-P-55-V17` | feeds `CL-E2-CRUISE-TO-LOW-PESS-V17` |

What changed in the model:

- **Motor current is judged in the winding** (CDR-AE-02, decision B7). At the limiter the ESC runs at a duty of
  about 0.83, so the winding carries more than the battery lead: 30.0 A against the maker's 25 A / 30 s. The claim
  fails as posed. The limiter value is decided on the stand: keep 100 A only if a 30 s run holds the bell ≤ 80 °C,
  otherwise about 71 A, which leaves T/W 2.04 fresh. F4 owns `Q_M_BAT_CURR_MAX`; nothing was changed there.
- **The maker's rows above 12 A are recorded, not discarded** (CDR-AE-01). `CALC-E1-CAL` lists all seven
  (`hi_rows`): at the measured rpm the model's thrust agrees within 0.8 % (`CL-E1-CAL-TERR-HI`), and the battery
  power is 7–26 % under the maker's column. First bound, as before: the maker's supply sagged to about 11.2 V at
  the 30 A row. Second bound, new: the row is a true 14.8 V point, which needs a series resistance of 0.218 Ω
  (`CL-E1-R-EFF-MAKER`) against the model's 0.096 Ω. `CALC-E1-BOUND2` runs the worst and fresh cases on it. A third,
  cruder reading (full-throttle rpm proportional to bus voltage, the rule the reviewer used for T/W 1.44,
  `REVIEWER EST`) is carried as a sensitivity and is the one that fails. Only `T-E1-STAND` with a logged bus
  voltage picks between them: 7 500 rpm at a held 14.8 V with the 11×4.7 means the second bound, above 9 000 rpm
  the first.
- **The script no longer writes shared files by default** (CDR-29). `python -I redesign/team/E1/propulsion.py`
  writes `team/E1/claims.json` only and prints the propulsion parts lines beside the file's values.
  `--write-parts` rewrites `subsystems/propulsion/parts.csv` and then runs C6's `fastener_parts.py`.

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
| T/W fresh pack with the limiter / worst pack state (limits 2.0 / 1.6) | 2.45 / 2.11 (rev 9, `r_ext` 7.9 mΩ) | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Sag factor on `r_ext` 7.9 mΩ (D-115) / closed-form check | 0.8497 / 0.872 | — | `CL-E1-SAG-FACTOR`, `-SAG-XCHECK` | `UNVERIFIED` |
| Winding current at the limiter (limit 25: **fails**) / battery side per ESC / unlimited burst at 16.8 V | 30.0 / 24.75 / 51.6 | A | `CL-E1-ILIM-I`, `CL-E1-ILIM-I-BAT`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
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
| `CALC-E1-WORST` on `r_ext` 7.9 (rev 9; was 6.7) | sag 0.8497, T/W worst 2.106: `voltage_sag` 0.851 stands to two places (0.85) | `UNVERIFIED` |
| `CL-E1-CRUISE-P-55` / `-LD-EFF` on `CL-B1V-CD0` / `-K` | 246.0 W `FAIL`, L/D 5.66; CR-E1-51 (252 W or 15 m/s; `ld_cruise` 5.66) | `FAIL` → A1 |
| SPEC thermal row | 56.1 / 64.8 °C; stale FAIL rows and the pending list corrected | done |
| `E-FIN-81…88` | acknowledged (36 acknowledged, 0 pending) | `CHECKED` |
| Model fix | `CALC-E1-TIP-GAP` bisection starts at 0, so the least `face_ahead` reads 6.5 mm, not the carried 7.5 | `CHECKED` |

Checks (rev 8, 2026-11-10): `fusion/check.py` propulsion `ok`, 0 keep-out ERRORs; overall FAIL on 20 errors in
the pod and avionics modules (pod `pack_aft_face_m` vs `pack_x_nominal_m`, other roles); WARN `mass` 462 g at zero
margin (floating point). `merge_check.py`: PASS, 0 errors. `build_graph.py` on the E1 folder alone: 0 `CALC-E1` drift (only the expected cross-folder references unresolved); the full-tree run did not finish in 35 min on the shared machine.
`plots.py` not re-run (local matplotlib lacks `packaging`); FIG PRP-01 still draws the rev 3 drag line.

## Verify

`python -I redesign/team/E1/propulsion.py` (writes `team/E1/claims.json` only; `--write-parts` to rewrite the
shared `parts.csv`, rev 9) → `python -I redesign/subsystems/propulsion/make_propulsion.py` →
`python -I redesign/team/E1/prop_clearance.py` (about 75 s) → `python -I redesign/fusion/check.py` →
`python -I redesign/proofs/build_graph.py`; hardware `T-E1-MOTOR-RM` (masses, base Ø and pattern, hole depth, bell
thread and free depth, lead length, ESC height, R, I0, 25 mm gauge at the tube), `T-E1-STAND`,
`T-B1-CRUISE-POWER` (settles CR-E1-51), `T-C6-PROPNUT`.
