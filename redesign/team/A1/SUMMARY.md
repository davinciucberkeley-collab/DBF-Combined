# A1 chief engineer — detail-analysis integration, revision A1-R3

Status: `PROPOSED` frame at revision **A1-R3**, 2026-11-09. Every number re-derivable:
`python -I redesign/team/A1/frame_claims.py` then `python -I redesign/proofs/build_graph.py`.
Build result after this round: **FAILED on drift only, in the 22 scripts that read the changed keys** (773 drifting
outputs: B4 133, B3 107, C4 175, C1 74, E1 64, E3 48, C5 31, B1 26, E2 22, D5 19, A5 12, A3 12, D7 11, J1 8, C3 7,
H1 6, D2 6, D3 4, B2 4, F3 3, F1 1: expected, each owner re-runs on R3). A1's 18 claims re-compute with no drift and no
failure; no unknown-id or unit error.

## This round

| Item | Resolution | Where | Status |
|---|---|---|---|
| Every change request from 27 roles since A1-R2 | dispositioned: 55 to A1 (accept / reject / supersede with a reason), ~150 forwarded by target role with A1's position | `params/CHANGE-LOG.md` "revision A1-R3" tables | `PROPOSED` |
| Decisions | D-24 … D-46 (23 rows) | `params/CHANGE-LOG.md` | `PROPOSED` |
| `params.json` | 71 leaves changed; revision A1-R3 | `params/params.json` | `PROPOSED` |
| `mass_budget.json` | 2 324 g allocated, 276 g reserve, CG 0.050–0.055 | written by `frame_claims.py` | `CHECKED` |
| `README.md` | aircraft, key numbers, stations, ownership, joint table at R3 | `redesign/README.md` | `PROPOSED` |
| `MASS-CG.md` | verdict, allocations (D-38), rules, levers rewritten; A3's generated block flagged stale | `redesign/MASS-CG.md` | A3 re-runs (CR-A1-25) |
| `params/claims.json` | `R-TRANSPORT` text reads the box key and the spanner rule (CR-A2-12a) | — | done |
| `frame_claims.py` | `CALC-A1-POD-RULE` and `ASM-A1-POD-*` retired; `CALC-A1-CG-RANGE` added; tip-over on D5's pad contact with z_cg; sag note | `team/A1/claims.json` (18 claims) | `CHECKED` |
| GA figure | re-drawn at R3 (0.21 m fins, 48 mm feet, pod −0.115) | `team/A1/ga-3view.svg` | `MODELLED` |
| Hand-off | D-17 section closed with the outcome; cars for `CAR-FIT.md` added | `team/A1/HANDOFF.md` | `PROPOSED` |
| Requests | CR-A1-25 … 42 (A3, B3, D2, D3, B4, B1, E2, E1, C1, D5, D7, F4, A2, A4/A5, I1, F2, H1, team lead) | `team/A1/CHANGE-REQUESTS.md` | open |

## Decisions that change the aircraft (full list D-24 … D-46 in the log)

| Id | Decision | Numbers | Conflict resolved |
|---|---|---|---|
| D-24 | CG range 0.050–0.055 m at R1 geometry; pod stays; pack 4 mm aft of the pod centre; D-17 closed | NP 0.0713 m; pack-centred CG 0.0515 inside | B3 over A3 / A5 / A1's −0.125 fallback |
| D-25 | Pod nose shell −0.115 with an XPS crush block; pod 0.21 × 0.14 × 0.07; pitot [−0.195, −0.046, 0.045]; pod 122 g | ≥ 24.3 mm crush holds any pack to ≤ 100 g | C5 over C3's −0.108 |
| D-26 | Fins: two layers, 0.21 m half-fins, tube 0.344 m, 408 g, ids `UR/UL/LR/LL` | one-layer mode 14 % from 2P; Cn_β 0.0286 → 0.0373 | C4 over D3 (layers); A4/A5 over D3 (ids) |
| D-27 | Motor cant 7° | yaw 1.15 → 2.23 × disturbance for 0.75 % thrust | B3's cant over lifting A2's cap |
| D-28 | Prop plane −0.0082 m, plate face 0.0309 | ≥ 39 mm to the collar front | D3's CAD over E1's −0.0033 until measured |
| D-29 | n⁺ 3.4, VD 27.2 m/s, thrust limit 21.1 N; elevon deflection schedule | gust 3.36; VH 21.8 at the rpm cap | C1 + H1 over the 17.8 N; schedule over a 5.9 kgf·cm servo |
| D-30 | Feet 48 mm, ≥ 38 mm constant-force stroke, biased cartridges; landing 43 g; tip-over 30° at the worst flying CG on the pad contact | 32.4° worst, 30.6° corner | C5's planar model over C1's 41 / 26 mm; 33° target retired |
| D-31 | Box 0.54 m high (`PROPOSED`, two cars first; fallback 0.50 + 0.15 m label); 3.63 kg; packs out | drop travel 70 mm under the tube ends | D7 over D-16 / D-22 |
| D-32 | AS150U, packs re-terminated; `r_ext` 6.5 mΩ; UBEC fitted; power 620 g | 37.8 A cont., 120 A momentary | F1 over XT60 (CR-A2-08, CR-A4-09, CR-J1-04 closed) |
| D-33 | CoreWing F405 Wing V2; MS4525DO at 0x28; telemetry over ELRS; avionics 80 g | stable build checked; I²C clash removed | — |
| D-34 | Propulsion 476 g; `motor_max_a` 25, `esc_burst_a` 55 | 118.9 g per station with leads | — |
| D-35 | Sag factor 0.72 → 0.76 (E2, limiter-consistent); E1's 0.854 noted | T/W worst 1.89 ≥ 1.6 | conservative of E1 / E2 until one claim |
| D-36 | Performance from B1 rev 2: 218 W (285 pess.), L/D 6.9, 13.7 / 7.3 min (E2 re-run), transition 15.6 | B1 17.0 / 12.7 min level cruise | B1 over E1's 247 W (stale L/D) |
| D-37 | Airspeed error 0.5 m/s | margin to 1.3 Vs 0.49–0.58 m/s; F3 RSS 0.44 | tighten over 16.5 m/s cruise |
| D-38 | Allocations 2 324 g, reserve 276 g, growth allowance 170 g, sized 2.59 kg | `CL-A1-MASS-SIZED` +0 % | the gate rests on A3's re-run and the pack |
| D-39 | Ground-test gear counts; cost keys from I1; lever order (adapter set gated, SpeedyBee, airspeed last) | reserve $319.65 → ≈ $326 | — |
| D-40 … D-46 | one prop spanner; per-type thread engagement; thermal keys and ASA prints; spar unchanged; `R-STALL` over the R3 range; wing modes by tap test + notch; A4 does the `interfaces/` tooling | — | — |

## Key numbers from the chain (2.6 kg gate)

| Claim | Value | Limit | Margin | Status |
|---|---|---|---|---|
| `CL-A1-MASS-SIZED` | 2.594 kg | ≤ 2.6 kg | +0 % | `CHECKED` (thin) |
| `CL-A1-RESERVE-COVERS` / `CL-A1-ALLOC-GATE` | +6 g / 0 g | ≥ 0 | — | `CHECKED` |
| `CL-A1-HOVER-TW-GATE` / `-SAG` | 2.49 / 1.89 | ≥ 2.0 / 1.6 | +25 % / +18 % | `UNVERIFIED` (stand) |
| `CL-A1-STALL-GATE` | 11.91 m/s | ≤ 12 m/s | +1 % | `UNVERIFIED` |
| `CL-A1-TRANSITION-GATE` | 15.48 m/s | ≤ 16 m/s | +3 % | `CHECKED` |
| `CL-A1-CG-RANGE-FWD` / `-AFT` | +0.1 / +0.3 mm | ≥ 0 | — | `CHECKED` against B3's claims |
| `CL-A1-CG-CENTRED` | +1.5 mm | ≥ 0 | — | `UNVERIFIED` (A3 re-runs) |
| `CL-A1-TIPOVER` (corner) / `-TARGET` | 30.6° / 34.7° | ≥ 30° | +2 % | `UNVERIFIED` (C5 worst flying CG 32.4°) |
| `CL-A1-PROP-CLEAR` | 35 mm | ≥ 25 mm | +38 % | `UNVERIFIED` |
| `CL-A1-ELEVON-FRAC` | 0.172 | ≥ 0.15 | +15 % | `CHECKED` |
| `CL-A1-BOX-FIT` | +17 mm | ≥ 0 | — | `CHECKED` (fit only; drop is D7's) |
| `CL-A1-RESERVE` | $320 | ≥ $309 | +3 % | `UNVERIFIED` (I1 re-prices) |

## Open issues

1. **Mass gate is thin.** Allocations rose 124 g to the designers' numbers; the reserve is 276 g for growth plus the 100 g overrun. With a 680 g pack the overrun is not covered. A3's R3 roll-up (CR-A1-25) and the pack weigh-in (~1 Dec) decide; levers in `MASS-CG.md`.
2. **Two B3 failures are fixed on paper only** (Cn_β −5 %, hover yaw 1.15 ×): D-26 / D-27 wait for B3's and B4's re-runs (CR-A1-26, -29).
3. **Box height 0.54 m** can be vetoed by a car; the fallback drops the drop case to 0.15 m (D-31).
4. **E1 and E2 still disagree on the sag factor** (0.854 vs 0.758); 0.76 carried (D-35); the cold-pack stand run decides.
5. **Pack bay layout**: D2's drawn travel is 5 mm short of B3's station; D2 re-lays (CR-A1-27).
6. **Budget margin** rests on gating the adapter set and borrowing test gear (D-39); I1 re-prices on 20 Nov.
7. `proofs/out/*` was regenerated by `build_graph.py` (J2's folder; expected).
