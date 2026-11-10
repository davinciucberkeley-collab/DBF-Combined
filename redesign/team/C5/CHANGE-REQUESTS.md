# C5 change requests

Revision C5-R3 (2026-11-09), at params A1-R3, A3's R3 roll-up (14:54 run) and B3's R1 CG range. Numbers from
`python -I redesign/team/C5/landing_calc.py` (claims `team/C5/claims.json`, report `LANDING.md`).

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-C5-10** (revised R3) | D5 (cc C1, C6, H1, A3) | Keep the 48 mm foot and the ≥ 38 mm stroke (D-30). Change the cartridges: **pre-crush every cartridge 2 mm on a press** (removes the 1.10 initial peak); **plateau upper UR/UL 39.4 N (section 11 × 20.8 mm), lower LR/LL 35.6 N (11 × 18.8 mm)**, mean 37.5 N, bias ×1.05 / ×0.95, colour-marked. Coupon acceptance: mean force 5–35 mm within −3 / +2 % of these. Check the flange and shoe bond at **59.1 N ultimate** per upper foot and the piston/sleeve at **30.5 N ultimate** side load (20.4 N limit, μ 0.7). Re-run `feet_calc.py` on the R3 keys (23 `CALC-D5-*` outputs drift on foot 48 mm, half-fin 0.21 m). | A3-R3's pitch inertia has moved between 0.030 and 0.042 kg·m² during this round. With the R2 cartridges (34.1 N, peak 1.10, bias 1.077) the pair-first pitch case bottoms at 0.030 (38.2 vs 35 mm usable, n 27.6) and passes by 0.5 mm at 0.042. The R3 cartridges pass at both: they are robust to the inertia. The zero-moment bias (1.074) is no longer the optimum; 1.05 minimises the worst pitch stroke. | `CL-C5-DROP-PAIR-PITCH` 31.5 of 35 mm (34.6 at I_yy 0.030); `CL-C5-DYN-N-LEVEL` 5.88; `CL-C5-CART-PLATEAU-UPPER/-LOWER`, `-SECTION-*`, `-ULT-UPPER`, `-BIAS-UPPER` |
| **CR-C5-12** (new) | A1, A3, B3 (cc D2, C3, D7) | **Trim A3-R3's aft CG by moving the pod group forward about 10 mm (`pod.x_le_m` −0.115 → ≈ −0.125), not by sliding the pack 14 mm forward in the bay.** If A1 slides the pack instead, the pod nose must go forward the same amount (≥ 9.3 mm) to keep the crush block. B3's re-run for D-26/D-27 may move the NP aft and shrink this. | A3-R3's roll-up puts the CG at 0.056 m with the pack at −0.001 (`CL-A3-PACK-X-REQ` −0.015). A pack trimmed to −0.0144 leaves 25.8 mm ahead of it against 29.4 mm needed, and a 503 g pack 19.5 vs 28.8 mm. A pod-group move keeps the pack where D-25 sized the block. | `CL-C5-PACK-NOSE-ROOM` 29.4 vs 25.8 mm `FAIL`; `CL-C5-PACK-ROOM-MARGIN-WORST` −9.3 mm; `CL-C5-NOSE-EXT` 9.3 mm; box x slack 17 → 7.7 mm (`CL-C5-BOX-X-SLACK-NOSE`); pod-group move: ≈ +9.8 mm (550 g) / ≈ +4 mm (503 g) `EST` |
| **CR-C5-13** (new) | C3, D2 | **Make the forward stop plate cover the full bay section (52 × ≈ 50 mm), not 25 × 54 mm.** It breaks off at ~100 N (C3's design) and must then spread into the 7 mm XPS block ahead of it over the whole section. | A 25 mm-tall plate crushes block A at only ≈ 230 N, so block A absorbs less energy and block B needs 3.8 mm more length. | `CL-C5-PACK-ROOM-C3-STOP` is 3.8 mm worse than the full-section case at every pack; +≈ 4 g PETG |
| CR-C5-11 | A1 | Closed by D-30 / D-38 (48 mm, 43 g). | — | — |
| CR-C5-02 | A1, D2, C3 | Adopted as D-25 (nose −0.115, XPS block, spreader). Superseded in part by CR-C5-12 (A3-R3's CG) and CR-C5-13 (stop section). | — | — |
| CR-C5-09 | C1, C4 | Answered by C1: `ASM-C1-FRICTION` 0.7 (mat). C4 still re-checks the fin face and edge strips at 20.4 N limit. C5 now carries its own grass friction (`ASM-C5-MU-GRASS` 0.5) for the parked slide check. | — | `CL-C5-FOOT-SIDE-LOAD` 20.4 = C1 20.4 N |
| CR-C5-01 | A2 (cc A1) | A1 adopted (D-30). A2: `R-TIPOVER` text "≥ 30° toward the pod side at the worst flying CG; land with a wingtip into the wind (flight card)". | — | worst flying 32.2°, corner bound 30.6° |
| CR-C5-03 | A2 (cc C1, D5) | `R-LANDING-IMPACT`: "absorbs a 1.5 m/s sink with 2/3 W lift at any touchdown tilt ≤ 10°, n ≤ 6, ≥ 3 mm stroke left; planar model validated by T-C5-AIRCRAFT-DROP". | Forwarded by A1. | as CR-C5-10 |
| CR-C5-04 | D5 (cc D1) | Wingtip TE corner caps (y ±0.575, x 0.32): ≤ 1 g TPU cap or 2 wraps of filament tape over 40 mm. | Forwarded by A1. | `CL-C5-WINGTIP-CLEAR-ROLL` −2.1 mm |
| CR-C5-05 | F4 (cc H2, B3) | Wingtip-into-wind landing heading; spin-min within 0.5 s of landing detection. | Forwarded by A1. | `CL-C5-V-LAND-BROADSIDE` 4.47 m/s `FAIL`; spanwise 8.2 m/s; `CL-C5-LAM-MAX` 0.71 |
| CR-C5-06 | H3 (cc H2, D7, I1) | Flight-card stance rules S1–S8 (LANDING.md §4); landing mat; 16 spare cartridges of each type, **pre-crushed**. | Forwarded by A1. | `CL-C5-V-PARK-GUST` 5.3 m/s mat / 4.5 grass |
| CR-C5-07 | C3, D2 | Bond the aft stop wall to the side guides; no screw heads within 5 mm of the pack faces. | Forwarded by A1. | 85 N |
| CR-C5-08 | H2 | Log touchdown ground speed and time to spin-min for 20 twin landings. | Forwarded by A1. | — |

## Answered here

CR-D5-05 (R2). In R3: A1's action item on the R3 keys (feet 48 mm, stroke 38 mm, CG 0.050–0.055, pod −0.115).
