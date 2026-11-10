# A2 systems engineer — requirements and verification matrix for K09-L

Status: `PROPOSED` requirement set, revision A2-R2 (2026-11-09, after CR-A1-37). One inventory (`requirements.json`) drives
the proof-chain nodes, the requirement document and the matrix: `python -I redesign/team/A2/build_requirements.py`
(`--no-graph` < 1 s; the full run rebuilds the proof graph, 2–3 min). Every number in the set is a `{P:key}` read from
`params/params.json` at build time (108 distinct keys); nothing is typed twice.

## What was produced

| File | What | Status |
|---|---|---|
| `team/A2/REQUIREMENTS.md` | 58 requirements in 8 groups (18 shared A1 ids, 40 A2 ids), each with P-line, value, unit, `params.json` source, owner, method (A/I/T/D); R3 wording for 3 shared nodes A1 still has to paste; P1–P25 map; live limits table (77 keys, all used); retired-id table; 15 differences from `REQUIREMENTS-PROPOSED.md` as data | `PROPOSED` |
| `team/A2/VERIFICATION-MATRIX.md` | requirement → owner → support → method → evidence (on disk?) → claims → margin → status; by-owner table; retired ids still cited | live from `proofs/out/graph.json` |
| `team/A2/claims.json` | 40 `R-…` requirement nodes + 1 alias (`ASM-A2-SERVO-TORQUE-FACTOR`, kept only while B2 cites it) | builds, 0 errors on A2 nodes |
| `team/A2/requirements.json` | the inventory: rows, `r3_text` for shared nodes, `differences`, `retired_limits` | — |
| `team/A2/build_requirements.py` | validator + generator; exit 1 on a duplicate id, unmapped P-line, missing key, a retired id in a row, an `r3_text` A1 has already adopted, or a graph error on an A2 node; evidence globs for H1's dated logs | runs, `A2 check: OK` |
| `team/A2/CHANGE-REQUESTS.md` | rounds 1–2 status (8 done/closed, 9 open) + 9 new (A1, C5/C1, C2, J1, E3, H1, A3, F3, B2) + answers to the 12 CRs forwarded to A2 | open |

## CR-A1-37 resolution

| Item | Done | Where |
|---|---|---|
| `R-CG-RANGE` → `cg.x_range_m` | reads the key with B3's two limit definitions (elevon trim / SM 5 %, D-24); 30 % cap stays on yaw (CR-B3-16) | row; `R-HOVER-AUTHORITY` |
| `R-TIPOVER` ≥ 30° toward the pod side at the worst flying CG, wingtip into wind | R3 wording written; shared node, so A1 pastes it (CR-A2-20a); `how`, support (D5, H1, H3) and evidence updated | "Shared nodes awaiting A1's edit" |
| `R-LANDING-IMPACT` per CR-C5-03 | 1.5 m/s sink with 2/3 W lift, tilt ≤ 10°, n ≤ 6, ≥ 3 mm of the 38 mm stroke left, planar model + `T-C5-AIRCRAFT-DROP` | row; CR-A2-21 clears the superseded claims |
| `R-VIBRATION` tap-test + notch branch (D-45) | three parts: fin stations at the operating points (band rule advisory, CR-C4-06), wing modes by tap test + rpm notch, VIBE | row; CR-A2-22 (C2), CR-A2-23 (J1) |
| `R-DISCONNECT` 10 °C steady / 30 °C < 60 s / 20 °C pack leads | R3 wording (continuous = max of hover, cruise, climb); the two F1 limits need `electrical.*` keys | CR-A2-20a/b |
| `R-FIELD-SETUP` one spanner (D-40) | re-worded on `transport.field_steps`; `CL-D7-SETUP-MIN` is its claim | row |
| `R-AIRSPEED` RSS ≤ 0.5 m/s | RSS after `ARSPD_AUTOCAL` + reciprocal legs; `CL-F3-ASPD-ERR` 0.44 passes (+11 %) | row |
| `R-RC-LINK` 25 mW + RSSI line | `rc_rssi_check_min_dbm` −93.8 dBm read; LQ ≥ 0.9 and RSSI ≥ −102 dBm in flight to the fence radius; 500 m by analysis | row |
| `R-JOINT-STACK` per-type engagement (D-41) | the four D-41 keys read (were unused); six C6/D3 claims, +2 % | row |
| `R-BUDGET` / `R-RESERVE` → I1 claims | `CL-I1-SPEND-PESS`, `-RESERVE-PESS`, `-RESERVE-BASE` named in `how`, I1 files as evidence | rows |
| `R-THERMAL` → E3 claims | seven claims, three tests, four `env.*` keys as the value | row; CR-A2-24 |
| `R-ESC-CURRENT` reads the D-34 keys | `propulsion.motor_max_a`, `esc_burst_a`, `env.full_throttle_max_s` replace typed 25 / 55 A | row |
| Close CR-A1-17 | closed by A1 in CR-A2-12 (D-34) | CHANGE-REQUESTS |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Requirements (shared / A2) | 58 (18 / 40) | — | `requirements.json` | `CHECKED` (validator) |
| P1–P25 lines mapped | 25 / 25 | — | `REQUIREMENTS.md` P-map | `CHECKED` |
| `params.json#requirements.*` keys / used by a row | 77 / 77 | — | limits table | `CHECKED` |
| Shared nodes with an R3 wording pending A1 | 3 (`R-MASS-GATE`, `R-TIPOVER`, `R-DISCONNECT`) | — | `REQUIREMENTS.md` | `PROPOSED` |
| Retired `ASM-A2-…` ids / alias still emitted | 39 / 1 (B2) | — | `claims.json` | `CHECKED` |
| Requirements with ≥ 1 claim | 42 of 58 | — | `VERIFICATION-MATRIX.md` | — |
| Status at the last A2 build | 0 `VERIFIED` · 1 `CHECKED` · 1 `PROPOSED` · 56 `UNVERIFIED` | — | `proofs/out/graph.json` | — |
| Requirements failing | 17 | — | matrix header | `FAIL` |
| Evidence files listed / on disk | 179 / 122 | — | matrix "On disk" | — |
| Proof graph | 2 471 nodes, 7 773 edges; `FAILED` on 713 drift errors in other roles' scripts, 0 on A2 nodes | — | `build_graph.py` | `UNVERIFIED` |

## Failing requirements (owner → reason; the graph is rebuilt by other roles between A2 runs, so the set moves)

| Requirement | Worst claim | Owner | Reason / fix |
|---|---|---|---|
| `R-VIBRATION` | `CL-J1-TUBE-MODE-SEP` −91 %, `CL-C2-WING-MODE-SEP` −62 % | C4 | both superseded by D-45 (C4's `CL-C4-D3-SEP` 0.41 passes); CR-A2-22, -23 |
| `R-DISCONNECT` | `CL-J1-XT60-BURST` −50 % | F1 | XT60 rejected by D-32; every AS150U and wire claim passes; CR-A2-23 |
| `R-HOVER-AUTHORITY`, `R-WIND` | `CL-B3-HOVER-YAW-ACCEL` −42 % | B3 | stored at 3° cant; B3 re-runs at 7° (D-27) |
| `R-CG-RANGE`, `R-MASS-ALLOC`, `R-MASS-GATE` | `CL-A3-CG-X-RANGE`, `CL-A3-ALLOC-WORST` | A3 | stale R2 roll-up re-run on R3 parameters; CR-A2-26 (CR-A1-25) |
| `R-ESC-CURRENT` | `CL-E1-IMAX-148-55` −18 % | E1 | tests the old typed 36 / 45 A; CR-A2-13 (D-34 keys exist) |
| `R-THERMAL` | `CL-E3-MOUNT-PETG` −14 % | E3 | the rejected PETG mount (D-42); CR-A2-24 |
| `R-LANDING-IMPACT` | `CL-C5-DYN-PAIR-CUR` −17 %, `CL-C1-N-LAND-STROKE-MIN` −6 % | C5 | superseded "foot today" claims and C1's eta 0.5 bound; CR-A2-21 |
| `R-PACK-RETENTION` | `CL-C3-NOSE-WALL-M` | C3 | D2's nose wall vs the crush-block layout (D-25); C3/D2 re-run |
| `R-STRUCT-MARGIN`, `R-FIN-TUBE-JOINT` | `CL-C6-STRIP-FACE-RF` −80 % | C2/C4 | C6's strip anchorage bonds; coupons (CR-C6-14) |
| `R-STATIC-MARGIN` | `CL-A5-LAYOUT-CG-X` −8 % | B3 | A5's old 0.049 m aft limit; CR-A2-19 |
| `R-MISSION` | `CL-E1-CRUISE-P-55` −7 % | B1 | E1 reads the old L/D; CR-B1-11 |
| `R-DIRECTIONAL` | `CL-B3-CNB` −5 % | B3 | 0.19 m fins stored; 0.0373 at 0.21 m (D-26) once B3 re-runs |
| `R-TRANSPORT` | `CL-D7-TUBE-CLEAR-DROP` −82 %, `CL-D7-A1-BOX-DROP-ALLOW` −3 % | D7 | D7's own foam-travel margin; CR-A2-18 |
| `R-STALL`, `R-LOADS` | `CL-B2-STALL-GATE-FWD` −0.5 %, `CL-C1-VD` −0.05 % | B2, C1 | old 0.040 m forward limit (D-44, CR-A2-28); VD rounding (CR-A2-20c) |

## Open issues

1. 16 of 58 requirements still have no claim (by-owner table): `R-HOVER-SPLIT` (A3, CR-A2-26), `R-GUST-LEAN` (B1), `R-SERVO-TORQUE` (D6), `R-ENVELOPE` (A5), `R-HARNESS-INSTALL` (F2), `R-NO-FLOATING` (A4), the H2/H3 demonstrations, `R-PROCESS`, `R-SCHEDULE`, `R-BUILD-HOURS`, `R-PROOF-BUILD`.
2. Three shared-node texts wait on A1 (CR-A2-20a); the proof graph carries A1's text until then, `REQUIREMENTS.md` shows both.
3. Two `R-DISCONNECT` limits (30 °C short-time, 20 °C pack leads) and E3's four temperature limits are still typed in claims, not `params.json` keys (CR-A2-20b, -24b).
4. Every structural, thermal and link claim stays `UNVERIFIED` until H1's campaign runs; the matrix names each dated log file it will look for (CR-A2-25).
5. The graph fails on other roles' drift (713 errors at this run) and is rebuilt by other sessions between A2 runs, so the matrix statuses move; nothing on A2 nodes fails.
