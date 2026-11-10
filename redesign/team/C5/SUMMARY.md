# C5 Landing / impact: summary

Fin-tip feet of the K09-L tailsitter (hardware by D5). Revision **C5-R5**, 2026-11-10. Inputs: params A1-R4a (D-47,
D-59), A3-R6 roll-up (2.323 kg, I_yy 0.0448 / I_zz 0.1674 kg·m²), B3's CG range on A3-R6 (0.0508 / 0.0529 / 0.0549 m),
D2's R5a pod params (D-59 stations, aft stop 0.060) and D5-R4's foot. To re-check, run
`python -I redesign/team/C5/landing_calc.py`, then `python -I redesign/proofs/build_graph.py`. The build shows no C5
drift, crash or warning. It still fails on other roles' drift. C5's own changes made three of those drifts, in D5, D7
and C4 (see Open issues).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Tip-over, pod side: B3 target / worst flying / D-59 stations worst / corner bound (limit 30) | 32.3 / 32.0 / 32.1 / 30.7 | ° | `CL-C5-TIPOVER-R1`, `-WORST`, `-D47`, `-B3-CORNER` | `UNVERIFIED` (+8 / +7 / +7 / +2 %) |
| CG rise in the stance, pre-D-47 bay → D-59 550 g station / tip-over change | +4.1 / −0.34 | mm / ° | `CL-C5-D47-CG-RISE`, `-TIP-CHANGE` | `MODELLED` |
| Worst station with the CG a further 5 mm higher | 31.7 | ° | `CL-C5-TIPOVER-STATION-PLUS5` | `UNVERIFIED` (+6 %) |
| Landing wind limit, broadside / span into wind | 4.44 / 8.3 | m/s | `CL-C5-V-LAND-*` | `FAIL` (rule S2) / `UNVERIFIED` |
| Hard landing, pair first, D5-R4 as delivered: stroke / usable | 31.5 / 35.0 | mm | `CL-C5-DYN-PAIR-CUR`, `CL-C5-DROP-PAIR-PITCH` | `UNVERIFIED` (+10 %) |
| Peak n, level free drop / tilted | 5.88 / 5.88 | — | `CL-C5-DYN-N-LEVEL`, `-N-CUR` | `UNVERIFIED` (+2 %) |
| Cartridge bias: C5 optimum / D5-R4 | 1.055 / 1.056 | — | `CL-C5-CART-BIAS-UPPER` | `CHECKED` |
| Normal landings per cartridge | 2.3 (≥ 5) | — | `CL-C5-LANDINGS-PER-CARTRIDGE` | `FAIL` (D5, CR-D5-21) |
| Test drop heights: level / tilted | 0.115 / 0.098 | m | `CL-C5-DROP-HEIGHT`, `CL-C5-TEST-TILT-H` | `PROPOSED` |
| Foot side load on the mat (μ 0.7) | 22.9 = C1 | N | `CL-C5-FOOT-SIDE-LOAD` | `UNVERIFIED` |
| Parked standing, pack out: largest gust on the mat / grass | 5.3 / 4.5 | m/s | `CL-C5-V-PARK-GUST*` | `UNVERIFIED` |
| Crush block B margin at the D-59 marks, 503 / 550 / 680 g (5 m/s, ≤ 100 g) | +2.4 / +7.0 / +8.9 | mm | `CL-C5-PACK-ROOM-MARGIN-503/-550/-680` | `UNVERIFIED` |
| Block B length needed / cut to fill, 503 / 550 / 680 g | 24.3 / 25.7 / 31.8 ; 25.7 / 31.7 / 39.7 | mm | `CL-C5-BLOCK-L-*`, `CL-C5-BLOCK-FILL-*` | `MODELLED` |
| Most forward pack station (flight-card S9), 503 / 550 / 680 g | −0.0264 / −0.0250 / −0.0189 | m | `CL-C5-PACK-X-FWD-MAX-*` | `PROPOSED` |
| Further nose extension / box x slack | 0 / 2 | mm | `CL-C5-NOSE-EXT`, `CL-C5-BOX-X-SLACK-NOSE` | `UNVERIFIED` |

## Decisions and findings

1. **The `CALC-C5-STANCE` `IndexError` stays fixed.** The script finds the pack as the single power/energy row
   (`PWR-001`) and stops with a clear message if that row is missing. It runs on A3-R6.
2. **Tip-over holds with the CG higher.** The D-47 rise is 5.0 mm at the old −0.022 station. D-59 moves the 550 g
   pack aft and leaves 4.1 mm. A further 5 mm on the worst station case still gives 31.7° (+6 %). The +2 % corner bound
   sits at B3's forward limit, so no flying case can reach it.
3. **D-59 (aft stations, aft stop 0.060) only helps the crush block.** Every pack passes at its mark: the worst is
   503 g at +2.4 mm. A 503 g pack at A3's −0.0254 (with 1.4 mm of play) still passes at +1.0 mm. Trimming it onto the
   B3 target (−0.0280) leaves it 1.5 mm short, so keep rule S9.
4. **D5-R4's cartridges pass on A3-R6 inertia** (31.5 of 35 mm, n 5.88). The "foot today" claims
   `CL-C5-DYN-LEVEL-CUR` / `-PAIR-CUR` are cross-checks with no `verifies` (CR-A2-21a).
5. Every claim names the lower cartridges `GER-008-LR/LL` (`CL-C5-DROP-STROKE` included); no claim names
   `GER-003-LR/LL` (CR-A4-47).
6. CR-C5-12 is superseded by D-47: the bay moved with the nose, and the block stays whole. CR-C5-13 (full-section
   stop, +4 g) belongs to C3 and D2, and C3 has declined it. C5 agrees.

## Files

| File | What | Status |
|---|---|---|
| `landing_calc.py` | six calculations (stance, wind, lay-flat, hand drop, planar dynamics, crash block), 90 claims, 4 tests | `CHECKED` (runs; no C5 drift in the build) |
| `claims.json` | proof-chain nodes (generated) | `CHECKED` |
| `LANDING.md` | report: tip-over, wind, dynamics and D5 sizing, drop tests, stance rules S1–S9, crash path | `PROPOSED` |
| `CHANGE-REQUESTS.md` | CR-C5-14 updated to D-59 (D2, H3); CR-C5-15 new (D5, D7, C4 re-runs) | open |

## Open issues

- D5's permanent set (1.28 mm per landing) gives 2.3 landings per cartridge. D5 owns the fix (CR-D5-21).
- Downstream drift from C5's re-run: `CALC-D5-CRUSH` (pitch stroke 31.43 → 31.55 mm), `CALC-D7-BOX-STACK` (nose
  extension 9.3 → 0 mm), and `CALC-C4-D3-STATIC` / `CALC-D5-SIDE` (side load, rounding only). Those roles re-run
  their own scripts (CR-C5-15).
- D2's `CALC-D2-NOSE-EXT` and `CL-D2-*` should read the D-59 stations and C5's per-pack block lengths (CR-C5-14).
- The wingtip TE corner clears by only 2.3 mm in the worst roll landing, so keep the corner caps.
- Touchdown drift (0.3 m/s), gust factor (1.4), pack shock limit (100 g) and the coupon plateau stay `UNVERIFIED`.
