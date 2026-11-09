# A2 systems engineer — requirements and verification matrix for K09-L

Status: `PROPOSED` requirement set, revision A2-R1 (2026-11-09, after CR-A1-17). One inventory (`requirements.json`) drives
the proof-chain nodes, the requirement document and the matrix: `python -I redesign/team/A2/build_requirements.py` (< 3 s).
Every number in the set is a `{P:key}` read from `params/params.json` at build time; nothing is typed twice.

## What was produced

| File | What | Status |
|---|---|---|
| `team/A2/REQUIREMENTS.md` | 58 requirements in 8 groups, each with P-line, value, unit, `params.json` source, owner, method (A/I/T/D); P1–P25 map; live table of every `params.json#requirements.*` key with the rows that use it; retired-id table | `PROPOSED` |
| `team/A2/VERIFICATION-MATRIX.md` | requirement → owner → support → method → evidence (on disk?) → claims → margin → status; by-owner table; retired ids still cited | live from `proofs/out/graph.json` |
| `team/A2/claims.json` | 40 `R-…` requirement nodes (A1's 18 reused, none duplicated) + 2 thin aliases (`ASM-A2-SERVO-TORQUE-FACTOR`, `ASM-A2-PACK-CAPACITY-FRAC`) that copy the parameter value and `cites` it, kept only while B2 and E2 still cite them | builds, 0 errors on A2 nodes |
| `team/A2/requirements.json` | the inventory; `retired_limits` maps each old `ASM-A2-…` id to its `requirements.*` key | — |
| `team/A2/build_requirements.py` | validator + generator; exit 1 on a duplicate id, unmapped P-line, missing `params.json` key, a row naming a retired id, or a graph error on an A2 node | runs, `A2 check: OK` |
| `team/A2/CHANGE-REQUESTS.md` | round-1 status (3 done, 4 closed, 4 open) + 8 new (A1, E1, F4/H1, A3, B2, E2, D7/C1, B3/A5) | open |

## CR-A1-17 resolution

| Item | Done | Evidence |
|---|---|---|
| Retire `ASM-A2-*`, point `R-*` at `params.json#requirements.*` (D-14) | 37 of 39 gone; 2 aliases pending CR-A2-16 (B2), CR-A2-17 (E2); every row's source is a `params.json` key; the validator rejects any `ASM-A2-…` in a row | `REQUIREMENTS.md` "Retired ids"; `build_requirements.py` |
| Rewrite `R-ESC-CURRENT` around the 100 A limiter (CR-E1-07) | (a) `Q_M_BAT_CURR_MAX` ≤ 100 A set and bench-verified; (b) ≤ 25 A per motor with the limiter; (c) unlimited burst ≤ 55 A at 16.8 V; (d) hover 27 A ± 15 %; method I+A+T, support F4/F1/H1 | `R-ESC-CURRENT` row; CR-A2-13, -14 re-point E1's 7 claims and add F4/H1's |
| Add `requirements.hover_split_max` to the matrix | new `R-HOVER-SPLIT` (A3, ≤ 1.25, D-18), P4/P8; the claim is `CL-A3-HOVER-SPLIT` once A3 adds `verifies` (CR-A2-15) | matrix row, `UNVERIFIED (no claim)` |
| Map `CL-A1-BOX-FIT` at box 0.50 m to `R-TRANSPORT` | `R-TRANSPORT` value reads `requirements.box_external_m` (1.25 × 0.55 × 0.50 m, D-16); `CL-A1-BOX-FIT` +25 mm listed; A1's shared text still says 0.45 m (CR-A2-12a) | matrix row |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Requirements (shared / new) | 58 (18 / 40) | — | `requirements.json` | `CHECKED` (validator) |
| P1–P25 lines mapped | 25 / 25 | — | `REQUIREMENTS.md` P-map | `CHECKED` |
| `params.json#requirements.*` keys / used by a row | 73 / 73 | — | `REQUIREMENTS.md` limits table | `CHECKED` |
| Retired `ASM-A2-…` ids / aliases still emitted | 39 / 2 | — | `claims.json` | `CHECKED` |
| Requirements with ≥ 1 claim | 27 | — | `VERIFICATION-MATRIX.md` | — |
| Status today | 0 `VERIFIED` · 3 `CHECKED` · 1 `PROPOSED` · 54 `UNVERIFIED` | — | `proofs/out/graph.json` | — |
| Requirements failing | 11 | — | matrix header | `FAIL` |
| Evidence files | 27 rows with 0 of their files on disk | — | matrix "On disk" | — |
| Proof graph | `FAILED`: 66 drift errors in other roles' scripts (J1, E1, …) at the last run; 0 on A2 nodes | — | `build_graph.py` | `UNVERIFIED` |

## Failing requirements (owner → reason)

| Requirement | Worst margin | Owner | Reason |
|---|---|---|---|
| `R-ESC-CURRENT` | −18 % | E1 | claims still test the old 36 / 45 A text; CR-A2-13 re-points them (ILIM 24.75 A and burst 51.6 A pass the new text) |
| `R-LOADS` | −21 % | C1 | `CL-C1-VD` 27.2 vs 22.4 m/s, `CL-C1-N-LIMIT-POS` 3.36 vs 3.0 at cruise 16 m/s: C1 re-derives (CR-A1-15) |
| `R-TRANSPORT` | −47 % | D7 | `CL-D7-A1-BOX-DROP-ALLOW` 0.158 vs 0.3 m drop: cradle foam (CR-A2-18); the fit itself is +25 mm |
| `R-VIBRATION` | −91 % | C4 | `CL-J1-TUBE-MODE-SEP` 0.017 vs 0.20: tube mode on 1P (CR-B4-07) |
| `R-DISCONNECT` | −50 % | F1 | XT60 60 A burst vs the 120 A unlimited case (CR-A2-08; the limiter case is 100 A) |
| `R-STATIC-MARGIN` | −18 % | B3 | A5's layout-CG claim against the old 0.045 m limit (CR-A2-19) |
| `R-WIND` | −46 % | B1/B3 | hover yaw ratio 1.08 without cant; the canted claim is `UNVERIFIED` (D-09) |
| `R-MISSION` | −7 % | B1/E2 | pessimistic cruise 4.6 min at the low pack (E2) |
| `R-STALL` / `R-TRANSITION` | −6 % / −3 % | B2/B3 | B3's trim claims at R0 geometry (D-21: re-run at R1) |
| `R-LANDING-IMPACT` | −1 % | C5 | `CL-C1-N-LAND-STROKE-MIN` 6.07 vs 6.0 at the 40 mm stroke |

## Open issues

1. 31 of 58 requirements have no claim; the by-owner table names each role's open ids (F3, H2, H3, G1, I2 have none at all).
2. Two aliases stay in the graph until B2 and E2 re-point one input each (CR-A2-16, -17); the build lists them every run.
3. `R-ESC-CURRENT` parts (b) and (c) cite typed ratings (25 A motor, 55 A ESC burst) until A1 adds the two propulsion keys (CR-A2-12b).
4. The proof graph fails on drift in other roles' scripts; the matrix statuses come from that graph and move when they re-run.
5. SITL cannot run on the design machine: `R-PILOT` and the SITL half of `R-FAILSAFES` stay `UNVERIFIED` until the team runs them.
