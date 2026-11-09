# C5 Landing / impact: summary

Fin-tip feet of the K09-L tailsitter (hardware by D5). Revision C5-R1, 2026-11-09, at params A1-R2 and the A3-R3
roll-up. Re-check: `python -I redesign/team/C5/landing_calc.py`, then `python -I redesign/proofs/build_graph.py`.
The graph build currently fails on drift in B1, B3 and F4 scripts. No C5 node has an error.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Tip-over, unsplayed 45 mm feet, R1 CG with z_cg +0.017 m (CR-A3-10) | 28.3 (A1's 30.6 ignores z_cg) | ° | `CL-C5-TIPOVER-A1-R1-ZCG` | `FAIL` (superseded foot) |
| Tip-over, D5 splayed pads, R1 CG / worst flying CG / B3 corner | 32.3 / 31.6 / 30.05 (limit 30) | ° | `CL-C5-TIPOVER-R1`, `-WORST`, `-B3-CORNER` | `UNVERIFIED` |
| Tip-over, wide axis | 45.1 | ° | `CL-C5-TIPOVER-WIDE` | `UNVERIFIED` |
| Hover lean at 5 m/s, broadside / span into wind (2.16 kg) | 18.8 / 11.0 | ° | `CL-C5-LEAN-5-*` | `UNVERIFIED` |
| Landing wind limit, broadside / span into wind | 4.3 / 8.3 | m/s | `CL-C5-V-LAND-*` | `FAIL` / `UNVERIFIED` |
| Touchdown drift allowed: calm 10° error / span into wind 5 m/s | 0.86 / 1.12 | m/s | `CL-C5-DRIFT-ALLOW-*` | `UNVERIFIED` |
| Largest thrust left at contact for a 10° tilt | 0.71 | W | `CL-C5-LAM-MAX` | `UNVERIFIED` |
| Drop test: height, CG peak, stroke used / available | 0.115 m, 5.88 g, 28.8 / 32 mm | — | `CL-C5-DROP-*` | `UNVERIFIED` |
| Foot energy at full stroke vs 40 mm at η 0.5 | 4.10 vs 3.06 | J | `CL-C5-FOOT-ENERGY` | `UNVERIFIED` |
| Parked standing, largest gust, pack out: mat / grass | 5.1 / 4.3 | m/s | `CL-C5-V-PARK-GUST*` | `UNVERIFIED` |
| Lying flat: lower-prop clearance spanwise / wind to lift it | +17 mm / 10.8 m/s | — | `CL-C5-LAYFLAT-PROP-CLEAR`, `CL-C5-V-LIFT-FLAT` | `UNVERIFIED` |
| Crush room ahead of the pack: needed / available | 26.3 / 1 | mm | `CL-C5-PACK-NOSE-ROOM` | `FAIL` |
| Normal landings per cartridge | 13 | — | `CL-C5-LANDINGS-PER-CARTRIDGE` | `UNVERIFIED` |

## Decisions and findings

1. **CR-A3-10 resolved.** With the CG z offset, the unsplayed foot fails (28.3°). D5's splayed pads pass at every
   flying CG (≥ 31.6°). Keep 30°, checked at the worst flying CG. Retire the 33° target: it costs the last 11.6 mm of
   box height for 0.7°.
2. **The landing heading is the main lever.** Broadside in a 5 m/s lull, a 10° error leaves 0.12 m/s of drift
   room. With a wingtip into the wind the lean drops to 11° and acts on the 45° axis: limit 8.3 m/s.
3. **Drop test defined:** 1.5 m/s = 0.115 m free drop at 2.6 kg, no rotor lift (harder than design). Pass at
   n ≤ 6.0 and stroke ≤ 29 mm. Single-foot rig first, then level, pitch, roll and corner drops.
4. **Stance rules for H3 (S1–S8):** landing mat; wingtip into wind; GPS-hold touchdown; idle at contact; lay
   flat between flights unless gusts ≤ 5 m/s, pack in and on the mat; lower props spanwise when flat.
5. **Crash path:** cartridges → pads/shoes → props → motor mounts → fins → core. The pack has no crush room
   (CR-C5-02), and the FC must not be the pack's aft stop (CR-C5-07).

## Files

| File | What | Status |
|---|---|---|
| `landing_calc.py` | five calculations, 43 claims, 4 tests; prints the CG and tip-over case table | `CHECKED` (runs; no drift) |
| `claims.json` | proof-chain nodes (generated) | `CHECKED` |
| `LANDING.md` | report: tip-over, wind and drift, drop test, stance rules, crash path | `PROPOSED` |
| `CHANGE-REQUESTS.md` | CR-C5-01 … 08 to A1, D5, A2, D2/C3, F4, H3, H2 | open |

## Open issues

- Drop-test margins are thin (n +2 %, 0.2 mm beyond the 3 mm guard). D5's coupon and the rig settle them.
- Span-into-wind hover heading needs yaw authority and an ArduPilot procedure (F4, B3, twin).
- The touchdown drift (0.3 m/s), gust factor (1.4) and pack shock limit (100 g) are `UNVERIFIED` assumptions.
