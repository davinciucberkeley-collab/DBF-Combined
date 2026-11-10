# A1 chief engineer: simulation round, revision A1-R5

Status: `PROPOSED` frame at revision **A1-R5** (D-61 … D-73, 2026-11-10) over A1-R4 / R4a / R4b (D-47 … D-60).
Every change request written by the end of the simulation round is dispositioned in `params/CHANGE-LOG.md`
("Revision A1-R5"); `params.json` is at A1-R5; `README.md` and `MASS-CG.md` carry the new frame. Re-derive:
`python -I redesign/team/A1/frame_claims.py` (24 claims, writes `params/mass_budget.json`), then
`python -I redesign/proofs/build_graph.py`.

## What the simulation round found and what A1 decided

| Finding (role) | As designed | Decision | Keys | Status |
|---|---|---|---|---|
| Static margin 4.76 % (A3 CG) / 4.33 % (predicted): the CG sits 18.5 mm above the chord plane, moving the effective NP 3.4 mm forward at 1.3 Vs (B3 V1, AVL 4 lattices) | `CL-B3-V-CG-A3-AFT-ENV` −0.77 mm `FAIL` | **D-62:** range [0.0466, 0.0514] m, target 0.0490, `cg.z_target_m` 0.0185, `z_range_m` [0.010, 0.025]; pod nose −0.140, pack bay 10 mm forward (datum −0.032, aft stop 0.050); pitot −0.220; envelope x 0.508 | `cg.*`, `pod.*`, `avionics.pitot_tip_xyz_m`, `transport.envelope_props_off_m` | `MODELLED` (D2 re-lays, A3 / B3 re-run) |
| Blade swept volume 21.1 mm from the CF motor tube (E1, B4, A5 agree) | `CL-E1-TIP-GAP-TUBE` −16 % `FAIL` | **D-61:** `face_ahead_m` 0.0075 → tube 26.1 mm; prop plane −0.0127, plate face 0.0244; no tool exemption | `propulsion.stations.x_prop_plane_m`, `x_plate_face_m` | `MODELLED` (D3 publishes the exact values) |
| Diagonal touchdown at 1.5 m/s bottoms the stroke from 5° of tilt; shoe RF 0.22 at the simulated 59 N side load; n 6.59 at 2.32 kg (C5 6-DOF + SU2 FEA) | `CL-C5-SIM3D-BOTTOM-TILT`, `-N`, `CL-C5-FEA-SHOE-SF` `FAIL` | **D-65:** 1.2 m/s at ≤ 10° any direction; n 6.6; side load 39.3 / 59.0 N; D5 shoe sleeve fix (+5 g) | `requirements.landing_sink_ms`, `landing_n_design` | `MODELLED` (A2 words it, D5 / C1 / C4 re-run) |
| Spiral t2 3.51 s at the raised CG (B3) | `CL-B3-V-LAT-T2` `FAIL` | **D-66** (A1 position for A2): t2 ≥ 3.3 s, roll-stabilised modes only; no CG change | — | `PROPOSED` (A2 decides) |
| Wing foam at the block-pocket corners 203 / 199 kPa ultimate (C2 FEA); fin-root tab if the fillet carries load | `CL-C2-FEA-FOAM-CORNER-*` `FAIL` | **D-68:** block edges R 3 mm, pocket fillet beads, cut-out radii, seam-free LE, fillet fail-safe only | — (D1, D3 local) | `PROPOSED` (C2 re-runs) |
| Pod stops peel the board at 400 kPa vs 50; spar-clamped shell R 1.40 (C3 FEA) | `CL-C3-FEA-AFT-*`, `-TIED-*` `FAIL` | **D-69:** aft-stop strut, forward-stop floor flange, handle-foot brackets, recess fillet (+13.9 g) | — (D2 local) | `PROPOSED` (D2 draws) |
| Fins 434.8 g (root fillets 30.6 g drawn); 2 mm pins bend; 12 mm collar RF 1.00 (D3, C4, C6) | `CL-D3-MASS`, `CL-C6-STRIP-PIN-RF` | **D-63 / D-70:** fins 437 g, pins Ø 2.5, collar 13 mm; allocations 2 386 g, reserve 214 g (0 g free); pod 146, landing 48, mechanisms 72 | `mass.allocation_g.*`, `growth_reserve_g`, `requirements.growth_allowance_kg` | `CHECKED` (`CL-A1-ALLOC-GATE` 0 g) |
| Pack SKU named by E2: Ovonic 120C EC5 551 ± 5 g, 135 × 46 × 49 mm | `CL-E2-SKU-MASS-MARGIN` +45 g | **D-64:** SKU adopted, cart released with two checks; acceptance line `CL-A1-PACK-ACCEPT` 592.6 g; 503 / 680 g cases retired | `battery.pack`, `size_m` | `UNVERIFIED` (T-E2-WEIGH) |
| Fin drag 1.23 × hand (B1 SU2): CD0 0.0579, 235 W at 2.436 kg; ESC pad h from CFD (E3): 56.1 °C, ceiling 44; F1 R_ext 6.69 mΩ | `CL-B1V-*`, `CL-E3-*`, `CL-F1-R-EXT` | **D-67:** 240 W stands, cruise after hover 12.0 / 6.4 min, `r_ext` 6.7, ceiling 44; `THR_MAX` 70 % stands | `performance.*`, `electrical.r_ext_mohm`, `env.ambient_ceiling_c` | `UNVERIFIED` |
| Stall / transition +0.1 % at the forward CG; B1 vs B2 CLmax 0.862 / 0.787 | `CL-B2R3-VS-GATE-FWD` | **D-71:** judged at the gate, closed by `T-B2-STALL` on the twin and the first build; B1 / B2 / B3 reconcile; lower CLmax carried | — | `UNVERIFIED` (test gate) |
| $6 T-antennas (F5) against a $3.99 reserve margin | `CL-A1-RESERVE` | **D-72:** released against I1's lever 1 (borrow the soldering kit); reserve reads $307 until Jacobs Hall's written yes | `cost.*` (I1 re-publishes) | `UNVERIFIED` |
| SU2 FEA pitfalls (C2, C4) | — | **D-73:** tooling notes for `inputs/SIM-TOOLS.md`; A4's 0.05 g budget tolerance | — | — |

## Key numbers (2.6 kg gate; A1 claims, `team/A1/claims.json`)

| Claim | Value | Limit | Margin | Status |
|---|---|---|---|---|
| `CL-A1-CG-RANGE-FWD` / `-AFT` (params vs B3 V1 limits) | +0.004 / +0.04 mm | ≥ 0 | — | `UNVERIFIED` (B3) |
| `CL-A1-CG-WIDTH` / `CL-A1-CG-TARGET-IN` | 4.8 / 2.4 mm | ≥ 4 / ≥ 2 mm | +20 % | `UNVERIFIED` |
| `CL-A1-PACK-CG-FWD` / `-AFT` (546 / 550 / 590 g packs in the D-62 bay) | +1.5 / +1.5 mm | ≥ 0 | — | `UNVERIFIED` (frame estimate on A3-R6a + `ASM-A1-A3-PACK-X`, `-STACK-DX`) |
| `CL-A1-PACK-STATION` / `CL-A1-NOSE-BALLAST` | 1.9 mm / 0 g | ≥ 0 / ≤ 10 g | — | `UNVERIFIED` |
| `CL-A1-PACK-ACCEPT` | 592.6 g | ≥ 556 g (SKU max) | +7 % | `UNVERIFIED` (T-E2-WEIGH) |
| `CL-A1-MASS-SIZED` / `-RESERVE-COVERS` / `-ALLOC-GATE` | 2.600 kg / 0 g / 0 g | ≤ 2.6 / ≥ 0 / ≥ 0 | +0 % | `CHECKED` |
| `CL-A1-HOVER-TW-GATE` / `-SAG` | 2.49 / 2.12 | ≥ 2.0 / 1.6 | +25 / +33 % | `UNVERIFIED` (stand) |
| `CL-A1-STALL-GATE` / `-TRANSITION-GATE` | 11.90 / 15.47 m/s | ≤ 12 / 16 | +1 / +3 % | `UNVERIFIED` |
| `CL-A1-TIPOVER` (fwd limit 0.0466, z 0.025) | 30.98° | ≥ 30° | +3 % | `UNVERIFIED` (C5) |
| `CL-A1-PROP-CLEAR` (frame bound; record: `CL-E1-TIP-GAP-AT-75` 26.1 mm) | 34.6 mm | ≥ 25 mm | +38 % | `UNVERIFIED` |
| `CL-A1-BOX-FIT` (D7's real stack) | 17 mm | ≥ 0 | — | `CHECKED` |
| `CL-A1-RESERVE` | $313 (I1-R3; $307 after D-72) | ≥ $309 | +1 % | `UNVERIFIED` (I1) |

Frame estimate of the take-off CG after D-61 / D-62 (`CALC-A1-PACK-CASES`): 546 g at −0.036 (16 mm spacer)
0.0481 → 0.0495 m; 550 g at −0.034 (14 mm) 0.0485 → 0.0498; 590 g at −0.028 (8 mm) 0.0486 → 0.0499; most forward
centroid −0.0379 (135 mm pack on the crush stack), no-spacer station −0.020. The flight card takes the stations
from A3's re-run, never from this table.

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/A1/frame_claims.py` | 24 claims, no negative margin; `mass_budget.json` 2 386 + 214 = 2 600 g, `cg_x_m` [0.0466, 0.0514], `cg_z_m` [0.010, 0.025] |
| `python -I redesign/interfaces/merge_check.py` | FAIL: 1 error (CG 0.052 m outside the D-62 range 0.047–0.051, expected until D2 re-lays the bay and A3 re-runs), 1 warning (propulsion 462 g float tie, CR-A1-59); the fins 435 / 418 g warning is cleared by D-63 |
| `python -I redesign/proofs/build_graph.py` | not completed in this session (the build was still re-running other roles' scripts after 25 min); A1's 24 claims re-compute clean in frame_claims.py; drift is expected in every script that reads the R5 keys (B3, B4, B1, E1, E2, E3, C1, C3, C4, C5, D2, D3, D5, D7, F4, H1) until the owners re-run |

## Open issues

1. **Three stop-gap assumptions** carry the D-61 / D-62 effect until A3 re-runs on D2-R6, D3-R5, D5-R5 and E1's
   centroids: `ASM-A1-A3-PACK-X` (−0.022), `ASM-A1-STACK-DX` (−0.9 mm), `ASM-A1-R5-ADDED-G` (21.4 g). A3 tells A1
   to retire them (CR-A1-64). Until then `CL-A3-CG-X-RANGE` reads the old bay and fails the D-62 range.
2. **R-STALL at the new forward limit** (0.0466) is B3's 11.94 m/s with the CG height; B2's z 0 model would give
   ≈ 12.05. B2 re-runs with z; the twin's slow-flight stall is the gate (D-71).
3. **Spiral** is A2's call (D-66). **`R-LANDING-IMPACT`** text is A2's (D-65).
4. **Reserve 0 g free** and the budget $2 under the crash cost until I1's lever 1 is confirmed: no further mass or
   money release without a lever. D3's levers (up to −23 g) and the harness return (−12 g) are the next releases.
5. **Owed re-runs on the R5 keys:** D2 (bay), D3 / E1 (mount, centroids), A3, B3, B4, B1, E2, E3, C1, C3, C4, C5, D5,
   D7, F4, H1, A5 (`check.py` 0 keep-out errors), A2 (texts); listed per role in the CHANGE-LOG forward table.

Files: `params/params.json` (A1-R5), `params/CHANGE-LOG.md` (A1-R4b, A1-R5 rows, D-60 … D-73, dispositions),
`params/mass_budget.json`, `README.md`, `MASS-CG.md` (hand-written sections), `team/A1/frame_claims.py`,
`team/A1/claims.json`, `team/A1/CHANGE-REQUESTS.md` (CR-A1-62 … 67).
