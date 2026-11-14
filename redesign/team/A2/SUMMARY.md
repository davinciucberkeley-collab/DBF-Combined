# A2 systems engineer — requirements and verification matrix for K09-L

Status: `PROPOSED` requirement set, revision A2-R3 (2026-11-10, after A1-R5's action items: D-65, D-66, D-70, D-71).
One inventory (`requirements.json`) drives the proof-chain nodes, the requirement document and the matrix:
`python -I redesign/team/A2/build_requirements.py` (`--no-graph` < 1 s; the full run rebuilds the proof graph).
Every number in the set is a `{P:key}` read from `params/params.json` at build time; the two typed numbers left
(`R-SPIRAL` 3.3 s, `R-VIBRATION`'s 6 390 rpm / +15 % triggers) are named below with the key requested for each.

## What was produced

| File | What | Status |
|---|---|---|
| `team/A2/REQUIREMENTS.md` | 59 requirements in 8 groups (18 shared A1 ids, 41 A2 ids), each with P-line, value, unit, `params.json` source, owner, method (A/I/T/D); R3 wording for 3 shared nodes A1 still has to paste; P1–P25 map; live limits table; retired-id table; 17 differences from `REQUIREMENTS-PROPOSED.md` as data | `PROPOSED` |
| `team/A2/VERIFICATION-MATRIX.md` | requirement → owner → support → method → evidence (on disk?) → claims → margin → status; by-owner table | live from `proofs/out/graph.json` |
| `team/A2/claims.json` | 41 `R-…` requirement nodes (`R-SPIRAL` new) + 1 alias (`ASM-A2-SERVO-TORQUE-FACTOR`, kept only while B2 cites it) | builds, 0 errors on A2 nodes |
| `team/A2/requirements.json` | the inventory: rows, `r3_text` for shared nodes, `differences`, `retired_limits` | — |
| `team/A2/build_requirements.py` | validator + generator (unchanged this round); exit 1 on a duplicate id, unmapped P-line, missing key, a retired id in a row, an `r3_text` A1 has already adopted, or a graph error on an A2 node | `A2 check: OK` |
| `team/A2/CHANGE-REQUESTS.md` | rounds 1–3 status (17 done/closed, 8 open) + 9 new (A1, B3, F4, C5, H1, B4, E3, C4, A3) + answers to the 10 CRs forwarded to A2 | open |

## A1-R5 action items — resolution

| Item | Done | Where |
|---|---|---|
| `R-LANDING-IMPACT` = 1.2 m/s sink at ≤ 10° combined tilt in any direction (D-65) | re-worded on the 6-DOF model: sink = `Q_PILOT_SPD_DN`, one foot takes the energy first, n ≤ `landing_n_design` (6.6) at the as-designed mass, ≥ 3 mm stroke left on the worst foot, the simulated side load (`CL-C5-SIM3D-SIDE-LOAD` / `-SIDE-ULT`) as the design side load for shoe, fin tip and root; the six `CL-C5-SIM3D-*` / `-FEA-SHOE-SF` claims named; C1's 1.5 m/s L1 / L4 kept as the structural bounds in `R-LOADS`; F4 and C4 added to support; GT-10 heights 0.115 m level, 0.073 m tilted | row; CR-A2-32 (C5), -33 (H1), -31b (F4) |
| `R-SPIRAL` (D-66) | **A2 decides: option (b) as A1 positioned it.** New node: t2 ≥ 3.3 s over `cg.x_range_m` × `cg.z_range_m`, wing-borne flight only in roll-stabilised modes, no MANUAL / ACRO / STABILIZE above 5 m AGL; owner B3, support F4 / H2 / H3, method A+I+D | row; CR-A2-29a (key), -30 (B3), -31a (F4) |
| `R-CG-RANGE` → `cg.x_range_m` with the B3 V1 ids | text names `CL-B3-V-CG-FWD` (trim at the stall) and `CL-B3-V-CG-AFT-ENV` (SM 5 % at 1.3 Vs with the CG `cg.z_target_m` above the chord plane), the 546 / 550 / 590 g pack cases (D-64) and the D-62 bay keys; `CL-A5-ASSY-CG-X`, `-FWD`, `-RANGE-USE` and `CL-B3-V-CG-A3-FWD` / `-AFT-ENV` in `how`; A5 in support; `claims.verify.json` and A5's claims as evidence | row; CR-A2-37 (A3 re-run) |
| `R-VIBRATION` re-run triggers | text (a) records `CL-C4-SIM-SEP` 0.29 as the value of record and the D-70 triggers: cruise rpm (`CL-B4-CRUISE-RPM`) > 6 390 rpm or station mass > +15 % over 84.2 + 7.6 + 4 g; `claims.sim.json` as evidence | row; CR-A2-36 (C4 trigger claims) |
| `CL-B4-TIP-WING`, `CL-E1-TIP-GAP-TUBE`, `CL-B4-GAP-TUBE-ENV` under `R-PROP-CLEAR` | all three in `how` with their stored values (34.2 / 26.1 / 21.1 mm) and the FIX5 pair; R3 wording on the blade swept volume on the canted axis (shared node, A1 pastes); E1 in support | row; CR-A2-29b, -34 (B4 re-run) |
| E3's `-ASD-*` ids and `T-E3-ESC-PAD-CFD` under `R-THERMAL` | `CL-E3-ASD-MOTOR-PEAK`, `-ESC-PEAK`, `-PACK-END`, `-FC-PEAK`, `CL-E3-CEIL-ASD` and the CFD validation test in `how`; `E3/sim/claims.json` and H1's `T-E3-ESC-PAD-CFD_*.csv` as evidence | row; CR-A2-35, -33c |
| `CL-B2R3-SERVO-TORQUE-REQ` verifies `R-SERVO-TORQUE` | text now reads "at the servo output through D6's linkage ratio, against the rated stall torque at the 6 V rail" (3.49 vs 3.9 kgf·cm, +11 %; D-71); `B2/sim/claims.sim.json`, D6's claims as evidence | row |
| Shared-node texts | `R-DISCONNECT` and the old `R-TIPOVER` wording adopted by A1 (rows closed); `R-TIPOVER` re-opened for D-64's pack cases and `CL-C5-SIM3D-DRIFT-TIPS`; `R-MASS-GATE` (D-63) and `R-PROP-CLEAR` pending | CR-A2-29b |
| Re-run `build_requirements.py` | validator `A2 check: OK` (59 rows, 0 inventory errors); `REQUIREMENTS.md` and the matrix regenerated with `--no-graph` on the 20:10 UTC graph; the full graph rebuild was still running after 60 min (every role's script re-runs; the machine was busy with other sessions) and is left to finish, which only refreshes the statuses | numbers below |

## The `R-SPIRAL` decision (D-66, CR-B3-26)

| Option | t2 | Cost | Verdict |
|---|---|---|---|
| (a) lower the CG to z ≤ 0 | 4.01 s at z 0 (`sens_zcg.py`) | not buildable: the pod sits on the upper surface, the pack overhangs the LE (D-62) | rejected |
| (b) keep z, t2 ≥ 3.3 s, roll-stabilised modes only | 3.51 s at the 0.0185 m target, 3.34 s at the top of `cg.z_range_m` (0.025 m) | none in hardware: F4's `K09L.param` already ships `FLTMODE1-6` = QSTABILIZE / QHOVER / QLOITER / FBWA / CRUISE / RTL (D-50), so only a card rule and two claims are added | **adopted** |

Why 3.3 s and not 4 s: MIL-F-8785C's 4 s is the Level 3 floor for a pilot holding the bank by hand; with every
fixed-wing mode roll-stabilised the autopilot's roll loop (crossover ≤ 5 Hz, `CL-F4-XOVER-RLL`) closes the spiral
long before a 3.3 s doubling matters. 3.3 s is B3's value at the top of the z range, so the limit holds anywhere the
CG may sit. Dutch roll (0.28) and short period (0.48) stay above B3's floors (`R-DIRECTIONAL`).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Requirements (shared / A2) | 59 (18 / 41) | — | `requirements.json` | `CHECKED` (validator) |
| P1–P25 lines mapped | 25 / 25 | — | `REQUIREMENTS.md` P-map | `CHECKED` |
| `params.json#requirements.*` keys / used by a row | 77 / 77 | — | limits table | `CHECKED` |
| Shared nodes with an R3 wording pending A1 | 3 (`R-MASS-GATE`, `R-TIPOVER`, `R-PROP-CLEAR`) | — | `REQUIREMENTS.md` | `PROPOSED` |
| Typed numbers awaiting a key | 2 (`R-SPIRAL` 3.3 s → `requirements.spiral_t2_min_s`; `R-VIBRATION` triggers → C4 claims) | — | CR-A2-29a, -36 | `PROPOSED` |
| Retired `ASM-A2-…` ids / alias still emitted | 39 / 1 (B2) | — | `claims.json` | `CHECKED` |
| Requirements with ≥ 1 claim | 44 of 59 | — | `VERIFICATION-MATRIX.md` | — |
| Status at the A2-R3 build | 0 `VERIFIED` · 1 `CHECKED` · 1 `PROPOSED` · 57 `UNVERIFIED` | — | `proofs/out/graph.json` | — |
| Requirements failing | 11 | — | matrix header | `FAIL` |
| Proof graph | 3 945 nodes, 12 819 edges from the 2026-11-10 20:10 UTC build (`OK`); A2's own full rebuild (`build_requirements.py` without `--no-graph`) was still running after 60 min while other roles' scripts re-ran on the same machine, so the statuses here come from that graph (`--no-graph`) | — | `build_graph.py` | `UNVERIFIED` |

## Failing requirements (owner → reason; other roles rebuild the graph between A2 runs, so the set moves)

| Requirement | Owner | Worst failing claim (margin) | Reason / fix |
|---|---|---|---|
| `R-MASS-GATE` | A3 | CL-A3-GATE-MARGIN-680 -66.0% | A3's 680 g pack case, retired by D-64; A3 re-runs (CR-A2-37) |
| `R-MASS-ALLOC` | A3 | CL-A3-ALLOC-WORST -4.4%; CL-D3-MASS -4.0% | fins 434.8 vs the old 418 g allocation (D-63 is 437); A3 re-runs (CR-A2-37) |
| `R-STATIC-MARGIN` | B3 | CL-B3-V-SM-A3-ENV -4.8% | B3's V1 claims at A3-R6a's CG (SM 4.76 %); A3 then B3 re-run (CR-A2-30c, -37) |
| `R-WIND` | B1 | CL-C5-SIM3D-V-BROADSIDE -20.0% | C5's broadside landing limit 4 m/s vs 5; wingtip-into-wind rule (CR-A2-32d) |
| `R-PROP-CLEAR` | D3 | CL-B4-GAP-TUBE-ENV -15.4%; CL-E1-TIP-GAP-TUBE -15.6% | B4's stored R4 mount value; B4 re-runs on D-61 (CR-A2-34); E1 already at 26.1 mm |
| `R-PACK-MASS` | E2 | CL-A3-GATE-MARGIN-680 -66.0% | same 680 g case (CR-A2-37) |
| `R-STRUCT-MARGIN` | C2 | CL-C2-FEA-FOAM-CORNER-S1 -35.5%; CL-C2-FEA-FOAM-CORNER-S3 -65.8% | C2's pocket-corner foam and C3's bond R as drawn, fixed by D-68 / D-69; C2, C3 re-run |
| `R-VIBRATION` | C4 | CL-C2-WING-MODE-SEP -64.2%; CL-J1-TUBE-MODE-SEP -91.4% | J1's superseded tube-mode claim (CR-A2-23) and C2's wing-mode separation (CR-A2-22) still verify |
| `R-PACK-RETENTION` | C3 | CL-C3-FEA-BOND-R-CRASH -1003.7%; CL-C3-FEA-TIED-R-CRASH -350.0% | C3's FEA of the pod stops as drawn, fixed by D-69; C3 / D2 re-run |
| `R-LANDING-IMPACT` | C5 | CL-C5-SIM3D-STROKE -10.2%; CL-C5-SIM3D-N -9.8% | C5's stored 1.5 m/s run and the pre-fix shoe; re-run at 1.2 m/s on the D-65 sleeve (CR-A2-32) |
| `R-DISCONNECT` | F1 | CL-J1-XT60-CONT-PESS -6.3%; CL-J1-XT60-BURST -50.0% | J1's XT60 claims (CR-A2-23); every AS150U and wire claim passes |

## Open issues

1. `R-SPIRAL` has no claim until B3 re-points `CL-B3-V-LAT-T2` (CR-A2-30) and F4 emits the mode lint (CR-A2-31); A1 adopts `requirements.spiral_t2_min_s` (CR-A2-29a).
2. `R-LANDING-IMPACT` fails on C5's stored 1.5 m/s run (`CL-C5-SIM3D-STROKE` 38.6 mm, `-BOTTOM-TILT` 5°) and the pre-fix shoe (`CL-C5-FEA-SHOE-SF` 0.22) until C5 re-runs at 1.2 m/s on D5's D-65 sleeve (CR-A2-32).
3. `R-CG-RANGE`, `R-STATIC-MARGIN`, `R-MASS-ALLOC`, `R-MASS-GATE` fail on A3-R6a's roll-up in the D-47 bay and the D-48 allocations until A3 re-runs on D-62 / D-63 / D-64 (CR-A2-37, CR-A1-64).
4. Three shared-node texts wait on A1 (CR-A2-29b); the proof graph carries A1's text until then, `REQUIREMENTS.md` shows both.
5. 15 of 59 requirements still have no claim (by-owner table): the H2 / H3 demonstrations, `R-GUST-LEAN`, `R-ENVELOPE`, `R-HARNESS-INSTALL`, `R-NO-FLOATING`, `R-PROCESS`, `R-SCHEDULE`, `R-BUILD-HOURS`, `R-PROOF-BUILD`, `R-SPIRAL`.
6. Every structural, thermal and link claim stays `UNVERIFIED` until H1's campaign runs; the matrix names each dated log file it will look for.
