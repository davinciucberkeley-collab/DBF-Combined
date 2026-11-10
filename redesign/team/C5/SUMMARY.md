# C5 Landing / impact: summary

Fin-tip feet of the K09-L tailsitter (hardware by D5). Revision **C5-R4**, 2026-11-09. Inputs: params A1-R4 (D-47),
A3's R5 roll-up with the D-47 bay, B3's R3 CG range, D2's R5 pod params and D5-R4's foot. To re-check, run
`python -I redesign/team/C5/landing_calc.py`, then `python -I redesign/proofs/build_graph.py`. The build shows no C5
drift, crash or warning. It still fails on other roles' drift.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Tip-over, pod side: B3 target / worst flying / D-47 stations worst / corner bound (limit 30) | 32.3 / 31.8 / 31.9 / 30.6 | ° | `CL-C5-TIPOVER-R1`, `-WORST`, `-D47`, `-B3-CORNER` | `UNVERIFIED` (+8 / +6 / +6 / +2 %) |
| D-47 effect, 550 g: CG rise in the stance / tip-over change | +5.1 / −0.42 | mm / ° | `CL-C5-D47-CG-RISE`, `-TIP-CHANGE` | `MODELLED` |
| Landing wind limit, broadside / span into wind | 4.41 / 8.2 | m/s | `CL-C5-V-LAND-*` | `FAIL` (rule S2) / `UNVERIFIED` |
| Hard landing, pair first, D5-R4 as delivered: stroke / usable | 31.4 / 35.0 | mm | `CL-C5-DYN-PAIR-CUR`, `CL-C5-DROP-PAIR-PITCH` | `UNVERIFIED` (+10 %) |
| Peak n, level free drop / tilted | 5.88 / 5.88 | — | `CL-C5-DYN-N-LEVEL`, `-N-CUR` | `UNVERIFIED` (+2 %) |
| Cartridge bias: C5 optimum / D5-R4 | 1.055 / 1.056 | — | `CL-C5-CART-BIAS-UPPER` | `CHECKED` |
| Normal landings per cartridge | 2.3 (≥ 5) | — | `CL-C5-LANDINGS-PER-CARTRIDGE` | `FAIL` (D5, CR-D5-21) |
| Test drop heights: level / tilted | 0.115 / 0.098 | m | `CL-C5-DROP-HEIGHT`, `CL-C5-TEST-TILT-H` | `PROPOSED` |
| Foot side load on the mat (μ 0.7) | 22.8 = C1 | N | `CL-C5-FOOT-SIDE-LOAD` | `UNVERIFIED` |
| Parked standing, pack out: largest gust on the mat / grass | 5.3 / 4.5 | m/s | `CL-C5-V-PARK-GUST*` | `UNVERIFIED` |
| Crush block B margin at the D-47 marks, 503 / 550 / 680 g (5 m/s, ≤ 100 g) | +1.9 / +3.0 / +4.9 | mm | `CL-C5-PACK-ROOM-MARGIN-503/-550/-680` | `UNVERIFIED` |
| Block B length needed, 503 / 550 / 680 g | 24.3 / 25.7 / 31.8 | mm | `CL-C5-BLOCK-L-503`, `CL-C5-BLOCK-L`, `-680` | `MODELLED` |
| Further nose extension / box x slack | 0 / 2 | mm | `CL-C5-NOSE-EXT`, `CL-C5-BOX-X-SLACK-NOSE` | `UNVERIFIED` |

## Decisions and findings

1. **The `IndexError` is fixed.** A3 renamed the pack row `PWR-E01` → `PWR-001`. The script now finds the single
   power/energy row and fails with a clear message if it is missing.
2. **Tip-over holds after D-47.** The CG rises 5.1 mm in the stance and costs 0.4°. The worst flying case is 31.8°
   (+6 %). The +2 % corner bound sits at B3's forward limit, which D-47 does not move.
3. **D5-R4's cartridges pass.** Pitch pair-first strokes 31.4 of 35 mm at n 5.88. CR-C5-10 is closed. The
   "foot today" claims are cross-checks only and no longer carry `verifies` (CR-A2-21a).
4. **The crush block passes for every pack at its D-47 mark.** CR-C5-12 is closed. Do not trim a pack forward of its
   mark: a 503 g pack slid onto the B3 target has 0 mm left (flight-card rule S9, CR-C5-14).
5. **CR-C5-13 is withdrawn.** At R5 a full-section forward stop gains only 0.5 mm. C3 and D2 close it.
6. Lower cartridges are named `GER-008-LR/LL` in the claims (CR-A4-47).

## Files

| File | What | Status |
|---|---|---|
| `landing_calc.py` | six calculations (stance, wind, lay-flat, hand drop, planar dynamics, crash block), 83 claims, 4 tests | `CHECKED` (runs; no C5 drift in the build) |
| `claims.json` | proof-chain nodes (generated) | `CHECKED` |
| `LANDING.md` | report: tip-over, wind, dynamics and D5 sizing, drop tests, stance rules S1–S9, crash path | `PROPOSED` |
| `CHANGE-REQUESTS.md` | CR-C5-14 new (D2 R5 claims, H3 station rule); 10, 12, 13 closed or withdrawn | open |

## Open issues

- D5's permanent set (1.28 mm per landing) gives 2.3 landings per cartridge. D5 owns the fix (CR-D5-21).
- D2's `CL-D2-*` claims still describe the R4 bay, and `CALC-D2-NOSE-EXT` reads C5's trim stations (CR-C5-14).
  `CALC-C5-CRASH` reads D2's R5 pod params directly.
- The wingtip TE corner clears by only 2.4 mm in the worst roll landing. Keep the corner caps.
- Touchdown drift (0.3 m/s), gust factor (1.4), pack shock limit (100 g) and the coupon plateau stay
  `UNVERIFIED`.
