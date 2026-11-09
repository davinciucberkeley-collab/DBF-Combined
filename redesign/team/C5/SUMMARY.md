# C5 Landing / impact: summary

Fin-tip feet of the K09-L tailsitter (hardware by D5). Revision **C5-R2**, 2026-11-09, at params A1-R2, the A3-R3
roll-up, B3's R1 CG range (CR-B3-11) and D2's pod. Re-check: `python -I redesign/team/C5/landing_calc.py`, then
`python -I redesign/proofs/build_graph.py`. The build reports no C5 errors; it still fails on other roles' drift
(A1, B1, E2).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Tip-over, pod side: B3 target / worst flying CG / corner bound (limit 30) | 32.8 / 32.4 / 30.8 | ° | `CL-C5-TIPOVER-R1`, `-WORST`, `-B3-CORNER` | `UNVERIFIED` |
| Tip-over, unsplayed foot | 28.3–29.2 | ° | `CL-C5-TIPOVER-A1-R1-ZCG` | `FAIL` (splay required) |
| Landing wind limit, broadside / span into wind | 4.35 / 8.4 | m/s | `CL-C5-V-LAND-*` | `FAIL` / `UNVERIFIED` |
| Hard landing, pair first, D5 foot today: stroke / usable | 32.8 / 29.0 | mm | `CL-C5-DYN-PAIR-CUR` | `FAIL` |
| Hard landing, pair first, proposed foot: stroke / usable | 34.5 / 35.0 | mm | `CL-C5-DROP-PAIR-PITCH` | `UNVERIFIED` |
| Peak n, level free drop / tilted design (proposed) | 5.84 / 5.54 | — | `CL-C5-DYN-N-LEVEL`, `-TILTED` | `UNVERIFIED` |
| Proposed foot: stroke, beyond TE, cartridge bias upper / lower | 38, 48, ×1.077 / ×0.923 | mm, mm, — | `ASM-C5-STROKE-PROP`, `ASM-C5-FOOT-PROP` | `PROPOSED` |
| Test drop heights: level / tilted | 0.115 / 0.082 | m | `CL-C5-DROP-HEIGHT`, `CL-C5-TEST-TILT-H` | `PROPOSED` |
| Foot side load on the mat (μ 0.7) vs C1 L4 (μ 0.5) | 23.0 vs 16.5 | N | `CL-C5-FOOT-SIDE-LOAD` | `FAIL` vs C1 case |
| Parked standing, pack out: largest gust on the mat / grass | 5.1 / 4.3 | m/s | `CL-C5-V-PARK-GUST*` | `UNVERIFIED` |
| Pack crush room: needed / available (550 g, 5 m/s, ≤ 100 g) | 26.4 / 21.5 | mm | `CL-C5-PACK-NOSE-ROOM` | `FAIL` |
| Pod nose extension, any pack 503–680 g / 550 g | 10.0 / 4.8 | mm | `CL-C5-NOSE-EXT`, `-550` | `PROPOSED` |

## Decisions and findings

1. **The CG move helps.** B3's range (0.050–0.055 m) adds about 0.5° of tip-over everywhere. 33° is not needed.
   Keep the pads at z ±0.219 m, also with 0.21 m fins.
2. **The 32 mm foot is too short.** A planar landing model (validated against the hand balance within 1.3 mm)
   shows two effects. The 17 mm z_cg offset rotates a level landing onto the pod-side pair, and in a pair-first
   touchdown the second pair lands harder. The worst tilt is about 4°. Fix: 38 mm stroke, a 48 mm foot and biased
   cartridges (CR-C5-10, -11). Stroke is the only lever that keeps n ≤ 6.
3. **Pack protection is now within reach.** The aft pack station opens 21.5 mm. A 10 mm nose-shell extension plus
   an XPS block as the forward trim spacer holds any listed pack to ≤ 100 g (CR-C5-02 revised, down from 25 mm).
4. **Landing heading and stance rules stand** (wingtip into wind, mat, lay flat, spin down at contact: S1–S8).
5. **The mat raises the fin side load 40 %.** C1/C4 re-check at μ 0.7 (CR-C5-09).

## Files

| File | What | Status |
|---|---|---|
| `landing_calc.py` | six calculations (stance, wind, lay-flat, hand drop, planar dynamics, crash block), 67 claims, 4 tests | `CHECKED` (runs; no C5 drift) |
| `claims.json` | proof-chain nodes (generated) | `CHECKED` |
| `LANDING.md` | report: tip-over, wind, dynamics and D5 sizing, drop tests, stance rules, crash path | `PROPOSED` |
| `CHANGE-REQUESTS.md` | CR-C5-01 … 11 (09, 10, 11 new; 02 revised) | open |

## Open issues

- Proposed pitch-first case leaves 0.5 mm inside the 3 mm guard. It rests on the XPS plateau (coupon), rotor lift
  2/3 W and frictionless pads. The tilted drops validate the model.
- With a 680 g pack the balanced station is 9.5 mm aft of D2's travel (D2, A1).
- Touchdown drift (0.3 m/s), gust factor (1.4) and pack shock limit (100 g) remain `UNVERIFIED` assumptions.
