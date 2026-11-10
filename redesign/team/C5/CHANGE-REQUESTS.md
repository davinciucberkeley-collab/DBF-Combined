# C5 change requests

Revision C5-R5 (2026-11-10). Inputs: params A1-R4a (D-47, D-59), A3-R6 roll-up, B3's CG range on A3-R6, D2's R5a pod
params (D-59 stations, aft stop 0.060) and D5-R4. Numbers from `python -I redesign/team/C5/landing_calc.py` (claims
`team/C5/claims.json`, report `LANDING.md`).

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-C5-15** (new) | D5, D7, C4 | Re-run your scripts on C5-R5: `feet_calc.py` (D5), `transport_calc.py` (D7), `fin_structures_d3.py` (C4). | C5's re-run on A3-R6 moved inputs you read: `CALC-D5-CRUSH.mark_margin_m` drifts (pitch pair stroke 31.43 → 31.55 mm), `CALC-D7-BOX-STACK.nose_gap_m` drifts (`CL-C5-NOSE-EXT` 9.3 → 0 mm since D-47), and `CALC-C4-D3-STATIC` / `CALC-D5-SIDE` drift on rounding of the 22.9 N side load. | `CL-C5-DROP-PAIR-PITCH` 0.03155 m; `CL-C5-NOSE-EXT` 0; `CL-C5-FOOT-SIDE-LOAD` 22.9 N |
| **CR-C5-14** (updated to D-59) | D2 (cc A3, H3, C3) | (a) Publish the R5a bay in `CL-D2-*`. (b) Point `CALC-D2-NOSE-EXT` / `CALC-D2-STATION` at the D-59 stations (`pack_x_per_pack_m`) and C5's per-pack block lengths `CL-C5-BLOCK-L-503`, `CL-C5-BLOCK-L`, `CL-C5-BLOCK-L-680`, not at `CL-C5-PACK-X-B3*`, which are now a cross-check only. (c) Cut block B to fill the stop-to-spreader gap so the pack has no forward play: **25.7 / 31.7 / 39.7 mm** (`CL-C5-BLOCK-FILL-503/-550/-680`). (d) H3: print the most forward allowed station per pack on the flight card (rule S9). | D-59 moved the stations aft. Each pack has more block room now, and the 503 g pack gains only 0.5 mm. If the 503 g pack is trimmed onto the B3 target (−0.0280), it is 1.5 mm short. | margins at the D-59 marks +2.4 / +7.0 / +8.9 mm; block B needed 24.3 / 25.7 / 31.8 mm; most forward station −0.0264 / −0.0250 / −0.0189 m (`CL-C5-PACK-X-FWD-MAX-*`) |
| CR-C5-06 (updated) | H3 (cc H2, D7, I1) | Flight-card stance rules S1–S9 (LANDING.md §4). New: S7 check the groove **after every landing** (2.3 normal landings per cartridge at D5-R4); S9 pack at its D-59 mark only (503 g −0.024, 550 g −0.018, 680 g −0.010), never forward of `CL-C5-PACK-X-FWD-MAX-*`. Landing mat; 16 spare cartridges of each type, pre-crushed. | D5-R4 set 1.28 mm per landing; crush block margin 2.4 mm (503 g). | `CL-C5-LANDINGS-PER-CARTRIDGE` 2.35; `CL-C5-V-PARK-GUST` 5.3 m/s mat / 4.5 grass |
| CR-C5-04 | D5 (cc D1) | Keep the wingtip TE corner caps (`GER-007`). | At A3-R6's I_zz the corner clears by only +2.3 mm in the worst roll landing (was −2.1 mm). That is inside the model's accuracy. | `CL-C5-WINGTIP-CLEAR-ROLL` +2.3 mm |
| CR-C5-05 | F4 (cc H2, B3) | Wingtip-into-wind landing heading; spin-min within 0.5 s of landing detection. | Forwarded by A1. | `CL-C5-V-LAND-BROADSIDE` 4.44 m/s `FAIL`; spanwise 8.3 m/s; `CL-C5-LAM-MAX` 0.71 |
| CR-C5-07 | C3, D2 | Bond the aft stop wall to the side guides; no screw heads within 5 mm of the pack faces. | Forwarded by A1. | 85 N |
| CR-C5-08 | H2 | Log touchdown ground speed and time to spin-min for 20 twin landings. | Forwarded by A1. | — |

## Closed or withdrawn (R4, confirmed at R5)

| Id | Status | Note |
|---|---|---|
| CR-C5-10 | **Closed by D5-R4** (CR-D5-22) | Delivered cartridges U 39.6 / L 35.4 N, bias 1.056, pre-crushed. Pitch pair-first 31.4 of 35 mm, n 5.88 (`CL-C5-DYN-PAIR-CUR`, `-N-CUR`). C5's optimum bias at A3-R5 inertia is 1.055. |
| CR-C5-12 | **Superseded by D-47** | The bay moves with the nose, and the crush block stays whole. All three packs pass at their D-59 marks (+2.4 / +7.0 / +8.9 mm). |
| CR-C5-13 | **Withdrawn by C5; C3/D2's call** (C3 declined it, see C3 SUMMARY) | At R5 block A is 1 mm. A full-section stop gains only 0.5 mm, and D2's 3 × 25 × 54 mm stop passes for every pack (`CL-C5-PACK-ROOM-C3-STOP` +1.4 mm). Keep the 4 g. |
| CR-C5-11, -02, -09, -01, -03 | Closed earlier | D-30 / D-38, D-25, C1 μ 0.7, A2 wording (CR-A2-20, -21). |

## Answered here

- CR-A1-46 / CR-A1-43 (C5 part), re-checked at R5: `CALC-C5-STANCE` runs (the pack is found as the single
  power/energy row `PWR-001`); re-run on D5-R4 (plateau 37.49 N, bias 1.056, η 0.903, set 1.28 mm) and A3-R6 mass and
  inertia; no C5 drift in the build. Tip-over with the CG higher: D-47 rise 5.0 mm, 4.1 mm net at the D-59 550 g
  station (−0.34°); worst station 32.1° (+7 %); a further 5 mm gives 31.7° (+6 %, `CL-C5-TIPOVER-STATION-PLUS5`);
  corner bound 30.7° (+2 %) at B3's forward limit, which no flying case passes.
- CR-A1-54 (C5 part): `CALC-C5-CRASH` per pack at the D-59 stations on D2's R5a bay: +2.4 / +7.0 / +8.9 mm; the 503 g
  pack with A3's 1.4 mm play (−0.0254) still +1.0 mm.
- CR-A2-21a: `verifies` stays dropped on `CL-C5-DYN-LEVEL-CUR` and `-PAIR-CUR` (cross-checks of D5-R4's foot).
- CR-A4-47: every claim names `GER-008-LR/LL` for the lower cartridges (`CL-C5-DROP-STROKE` included); none names
  `GER-003-LR/LL`.
- CR-D2-10: `CL-C5-BLOCK-L` per pack mass published (`-503`, `-680`), plus `CL-C5-BLOCK-FILL-*` and
  `CL-C5-PACK-X-FWD-MAX-*`.
