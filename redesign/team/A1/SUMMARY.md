# A1 chief engineer — change-request round, revision A1-R2

Status: `PROPOSED` frame at revision **A1-R2**, 2026-11-09. Every number re-derivable:
`python -I redesign/team/A1/frame_claims.py` then `python -I redesign/proofs/build_graph.py`.
Build result today (re-run 2026-11-09, after the D-17 / CR-A1-21 items): **FAILED on drift in B1, B3 and E2 only**
(B3 has ten calcs that do not run, mid-edit); A1's 20 claims re-compute with no drift. One A1 claim fails on
purpose: `CL-A1-POD-HELD-ROOM` −2.2 mm is the D-17 trigger reading `FAIL` on B3's stored range.

## This round: action items CR-A1-21 and D-17

| Item | Resolution | Where | Status |
|---|---|---|---|
| CR-A1-21 team-lead actions | L1 Fusion BuildAll on the R1 skeleton (named teammate, after A5's CR-A1-12), L2 weigh the first pack (`T-E2-WEIGH`), L3 weigh the first CF tube (`T-A3-WEIGH-PARTS`), each with done-criteria and same-day thresholds (pack > 658 g fails the gate after growth) | `HANDOFF.md` §1 | `PROPOSED`; open until the lead names people |
| D-17 pod station | Rule re-stated as two claims that read B3's claims directly: part 1 aft limit < `CL-A1-POD-TRIGGER` 0.0519 m (was "0.051"); part 2 `CL-A1-POD-HELD-ROOM` < 0. Either fires → pod −0.105 → −0.125 m | `HANDOFF.md` §2, `frame_claims.py` `CALC-A1-POD-RULE` | `MODELLED`; **pod held**: B3 has not published at R1 |
| Fallback −0.125 m | CG 0.0448 m pack centred (+9 % to the aft limit, +5.0 mm to the forward), 27 mm pack slide each way, box chordwise slack 30 → 10 mm, pitot −0.205 m | same | `UNVERIFIED` (R0 range) |
| Preview | build re-run of B3's NP at R1 inputs: 0.0674 m → aft ≈ 0.0514 m; part 1 would fire by ~0.5 mm. Not acted on | `HANDOFF.md` §2 | `UNVERIFIED` |
| CR-A3-11 | interim pack 26 mm forward (option a, CG 0.0448 m); option b (−0.110) declined | `CHANGE-REQUESTS.md` CR-A1-22 | `PROPOSED` |

## What was produced

| File | What | Status |
|---|---|---|
| `redesign/params/CHANGE-LOG.md` | decisions D-01 … D-15 (R1, reconstructed) and D-16 … D-23 (R2); every change request from 13 roles dispositioned (accept / reject / forward + reason) | `PROPOSED` |
| `redesign/params/params.json` | revision A1-R2: box 0.50 m high, `requirements.hover_split_max` 1.25, CG hold note (D-17), tip-over and transition notes | `PROPOSED` |
| `redesign/params/mass_budget.json` | regenerated: 2 200 g allocated, 400 g reserve, CG 0.040–0.049 | `PROPOSED` |
| `redesign/README.md` | rewritten to R2: aircraft, key numbers, stations (tubes through the wing, half-fins, block, feet, pitot, box), ownership incl. the per-unit mass rule, joint table with D-20 ownership rules | `PROPOSED` |
| `redesign/MASS-CG.md` | hand-written sections aligned with A3's live roll-up: verdict, adopted allocations (D-07), rules (D-17, D-18), levers | `PROPOSED` |
| `team/A1/claims.json` · `ga-3view.svg` | 20 claims (6 new for D-17) re-run; GA re-drawn from R2 params | 1 intended `FAIL` (`CL-A1-POD-HELD-ROOM`) |
| `team/A1/HANDOFF.md` | team-lead actions L1–L3 and the D-17 rule, fallback checks and the procedure when B3 publishes | `PROPOSED` |
| `team/A1/CHANGE-REQUESTS.md` | 9 old requests closed; 12 new requests (A2, A3, A4, A5, B1, B2, B3, C1, D5/C5, D7, J1, team lead) | open |

## Decisions this round (CHANGE-LOG D-16 … D-23)

| Id | Decision | Numbers |
|---|---|---|
| D-16 | Transport box 0.45 → 0.50 m high | envelope 0.425 m (tube ends); `CL-A1-BOX-FIT` −25 → +25 mm |
| D-17 | Hold the pod at −0.105 m until B3 re-derives the CG range at R1 geometry | A3 basic CG 0.051 vs 0.040–0.049 (R0 range); pack 29 mm forward gives 0.044 |
| D-18 | Hover pitch-trim split limit 1.25 (`requirements.hover_split_max`) | A3 split 1.19; B3 allows 12.5 % of the pitch differential |
| D-19 | Static margin stays 0.05 (CR-J1-02 rejected) | B2's trimmed CLmax 0.80 already includes the up-trim |
| D-20 | Joint ownership: hinge → `wing`; ESC leads → `harness`; electrical `part_a` = supply | README joint table |
| D-21 | CR-B3-07 superseded: cruise stays 16 m/s; `ARSPD_FBW_MIN` from B3's R1 re-run | 1.3 Vs 15.42 m/s at c 0.32 / S5010 |
| D-22 | Box drop 0.3 m and 1.5 m/s sink kept; D7 puts ≥ 70 mm crush foam under the cradles | C1 CR-C1-05 |
| D-23 | Printed mounts and props are the tip-over fuse; carry point + label; C4 still sizes to G2 | 3.5 J, 10.7 N·m |

## Key numbers from the chain (2.6 kg gate)

| Claim | Value | Limit | Margin | Status |
|---|---|---|---|---|
| `CL-A1-MASS-SIZED` | 2.55 kg | ≤ 2.6 kg | +2 % | `CHECKED` |
| `CL-A1-HOVER-TW-GATE` / `-SAG` | 2.49 / 1.79 | ≥ 2.0 / 1.6 | +25 % / +12 % | `UNVERIFIED` (stand) |
| `CL-A1-STALL-GATE` | 11.91 m/s | ≤ 12 m/s | +1 % | `UNVERIFIED` (B2 trimmed CLmax now 0.798) |
| `CL-A1-TRANSITION-GATE` | 15.48 m/s | ≤ 16 m/s | +3 % | `CHECKED` |
| `CL-A1-POD-TRIGGER` | 0.0519 m | B3 aft limit | — | `MODELLED` (rule input) |
| `CL-A1-POD-HELD-ROOM` | −2.2 mm | ≥ 0 | — | `FAIL` on R0 range (→ pod moves when B3 publishes) |
| `CL-A1-POD-ALT-AFT` / `-FWD` | 0.0448 m / +5.0 mm | ≤ 0.0491 m / ≥ 0 | +9 % / — | `UNVERIFIED` |
| `CL-A1-POD-ALT-PACK-ROOM` / `-BOX` | 27 mm / 10 mm | ≥ 0 | — | `MODELLED` |
| `CL-A1-TIPOVER` | 30.6° | ≥ 30° | +2 % | `CHECKED` (thin: D5 splays) |
| `CL-A1-PROP-CLEAR` | 35 mm | ≥ 25 mm | +38 % | `UNVERIFIED` |
| `CL-A1-ELEVON-FRAC` | 0.172 | ≥ 0.15 | +15 % | `CHECKED` |
| `CL-A1-BOX-FIT` | +25 mm | ≥ 0 | — | `CHECKED` |
| `CL-A1-RESERVE` | $321 | ≥ $309 | +4 % | `CHECKED` |

## Scripts that had to be re-run at R2 (as listed at A1-R2; at the latest build only B1, B3 and E2 still drift)

| Script | Drifted calcs | Owner | Also |
|---|---|---|---|
| `team/B4/props.py` | 124 | B4 | download with the tube at 0.045 (disc edge 35 mm above the LE) |
| `team/B3/sc_analysis.py` | 103 | B3 | NP, CG range, trimmed stall, Cn_β at c 0.32, S5010, tube 0.045, 3° cant (D-17, D-21) |
| `team/C1/loads.py` | 91 | C1 | inputs → `requirements.*` keys (D-14); `CL-C1-N-LAND-NOW` at the 45 mm foot |
| `team/B1/performance.py` | 59 | B1 | 16 m/s, 11×5.5MR, CLmax 0.80, S5010 CD, hover 400 W |
| `team/E1/propulsion.py` | 44 | E1 | one worst-state T/W claim with E2 |
| `team/E2/energy_claims.py` | 27 | E2 | B1's cruise power |
| `team/A5/cad_claims.py` | 18 | A5 | spar cover at z 0.0066; layout CG; skeleton to R1 |
| `team/B2/wing_claims.py` | 12 | B2 | `CL-B2-STALL-GATE` at c 0.32; AVL e with 0.275 fins |
| `team/J1/research_claims.py` | 12 | J1 | re-point at `R-VIBRATION`, `R-DIRECTIONAL` |

## Open issues

1. The CG range is `UNVERIFIED` at R1 geometry; no station freezes until B3's re-run (D-17, CR-A1-23). Rule now in claims: the pod moves to −0.125 m if B3's aft limit < 0.0519 m or `CL-A1-POD-HELD-ROOM` < 0; the preview says it will. `ASM-A1-POD-GROUP` (763 g) is typed from A3 until CR-A1-22.
2. Tip-over margin is +2 % at the 45 mm feet; D5/C5 splay the feet to z ≥ ±0.21 m for ≥ 33°.
3. The through-core block and the half-fin-to-tube junction are undesigned (D3, C4, P25); the bare tube's first mode sits 6 % from the hover 2P.
4. Main disconnect undecided (F1): XT60 only with a cited burst rating covering the ≤ 5 s momentary case at the 100 A limiter.
5. Mass gate margin after growth is 105 g and rests on a 550 g pack (listings 503–680 g).
6. `fusion_backend.py` has never run in Fusion (CR-A5-08): the team lead assigns a teammate (`HANDOFF.md` L1).
7. `proofs/out/*` was regenerated by `build_graph.py` (J2's folder; expected).
