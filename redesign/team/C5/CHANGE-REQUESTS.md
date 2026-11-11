# C5 change requests

Revision **C5-R6** (2026-11-10, after D-62 / D-64 / D-65). New rows CR-C5-20 … -23; CR-C5-16 updated; CR-C5-17, -18
and -19 closed by D-65. Inputs: params A1-R5, A3-R6a roll-up, A1's D-62 frame estimate for the D-64 pack stations,
D2-R5a pod params, D5-R5a foot. Numbers from `landing_calc.py` (`claims.json`, `LANDING.md`) and
`landing_sim_claims.py` (`claims.sim.json`, `SIMULATION-REPORT.md` §0).

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-C5-20** (new, R6) | D5 (cc A1, C4) | Publish the D-65 shoe in your inputs (`CALC-D5-SIDE` / `subsystems/landing/params.json`: sleeve end wall 2.0 mm, rim 3.0 mm, inside fillets R 1.0 mm, engagement 25 mm, side-load basis **59.25 N ult**), re-run `feet_calc.py` and `make_interfaces.py`, report the real mass against the +5 g `EST` of D-63. C5 then re-runs `sim/run_fea.sh` on your file instead of its overrides. | C5's FEA of exactly that stack on 3 meshes passes: RF @RF@ at 59.25 N ult (@RFG@ with the grid error), so no further change to the part. Until D5 publishes, the claim rests on C5's overrides of your inputs. | `CL-C5-FEA-SHOE-SF` @RF@, `-SF-GCI` @RFG@, `CL-C5-FEA-SIDE-CAPACITY-D65` @CAP@ N limit; lever R/F @LEV@ |
| **CR-C5-21** (new, R6) | A1, D2, A3 (cc H3, C3) | The D-62 bay note's "crush block ≥ 24.3 mm" is the retired 503 g pack's length. For the D-64 packs block B must be **≥ 25.5 / 25.8 / 27.6 mm** (546 / 551 / 590 g; `CL-C5-BLOCK-L-546`, `CL-C5-BLOCK-L`, `CL-C5-BLOCK-L-590`), so the most forward pack centroid is **−0.0367 / −0.0364 / −0.0346 m**, not −0.0379 (`CL-C5-PACK-X-FWD-MAX-*`). A1: `ASM-A3-NOSE-STACK` / `pack_x_fwd_limit` per pack (nose stack 35.8 mm for 546 g). D2: replace `pack_x_per_pack_m` (503 / 550 / 680 g, D-59) with the D-64 stations from A3's re-run and cut block B to fill the gap (26.2 / 28.2 / 34.2 mm, `CL-C5-BLOCK-FILL-*`). A3: `ASM-A3-PACK-RANGE` to 546 / 590 g. | The bay section caps the block force at 509 N, so the block length grows with pack mass. At the D-62 marks all three packs pass (+0.7 / +2.4 / +6.6 mm), but a pack placed on the 24.3 mm stack would be 1.2–3.3 mm short. The 546 g pack has only 0.7 mm, so no forward play. C5-R6 also stops crediting the 1 mm epoxy bond line (block A since D-47) as crush (−1 mm on every margin). | `CL-C5-PACK-ROOM-MARGIN-546/-551/-590` +0.66 / +2.42 / +6.60 mm; `CL-C5-PACK-STACK-MARGIN` −3.3 mm; pack n 95 / 94 / 88 |
| **CR-C5-22** (new, R6) | D5, C1 (cc A2, A1) | n at the lightest flying mass sits on the limit: **6.60 vs 6.6** (A3-R6a basic with the 546 g pack, 2.318 kg). Either (a) **D5** accepts cartridges at **−3 / +0 %** of the nominal plateau (sort by coupon; C5 recommends this), or (b) **C1** checks the airframe at n 6.75 (`landing_n_design` 6.6 → 6.75) to cover the +2 % coupon tolerance. Do not lower the plateau: the gate stroke has no margin left. | n = 4 × 37.5 N / (m g) does not depend on the sink speed; +2 % plateau gives 6.73. The R5 additions (≈ +21 g) give 0.06 back once A3 re-runs, which is not enough to rely on. | `CL-C5-SIM3D-N-LIGHT` 6.60; `CL-C5-SIM3D-N` 6.59 |
| **CR-C5-23** (new, R6) | F4 (cc A2, H3, H2) | Set `Q_PILOT_SPD_DN` to **1.0 m/s** (D-65 allows ≤ 1.2) so that a pilot down-stick landing with GPS drift stays inside the stroke; flight card S3. Keep `R-LANDING-IMPACT` at 1.2 m/s, 10°, no drift. | With 0.3 m/s touchdown drift, 1.2 m/s at 10° bottoms a foot (38.1 mm at the gate, 36.9 at A3 predicted); 1.1 m/s holds (33.4 mm). 1.0 m/s keeps one 0.1 m/s step in hand (28.0 mm). Without drift the gate case is 34.9 of 35 mm. | `CL-C5-SIM3D-V-SINK-DRIFT` 1.1 m/s; `CL-C5-SIM3D-STROKE` 34.9 mm |
| **CR-C5-16** (updated R6) | D5, C4/D3, C1 | Design foot side load **39.5 N limit / 59.25 N ultimate** (`CL-C5-SIM3D-SIDE-LOAD`, `-SIDE-ULT`; was 39.3 / 59.0) in `CALC-D5-SIDE`, `CALC-C4-D3-STATIC` and C1's fin-tip landing case. Option for D5: a pad face with **μ ≤ 0.5** on the landing mat (e.g. UHMW / PTFE tape over the neoprene, confirmed by T-D5-PAD-MU) cuts it to **29.1 N limit / 43.7 N ult** (`CL-C5-SIM3D-SIDE-MU05`); shoe RF then @RFMU@. | The 1.2 m/s envelope gives 39.3 N (unchanged: the scrub load saturates at μ × plateau plus the tilt component); the 0.3 m/s drift landings give 39.44 N, so C5 rounds the basis up by 0.2 N. You re-run on the R5 keys anyway. | 39.44 N with drift; 39.3 N without; μ 0.5 → 29.1 N |
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
| CR-C5-17 | **Closed by D-65** (option a) | `landing_sink_ms` 1.2 m/s at ≤ 10° any direction. Re-run at 1.2 m/s: 34.9 of 35 mm at the gate, nothing bottoms inside 10° (`CL-C5-SIM3D-STROKE`, `-BOTTOM-TILT`). Drift follow-up in CR-C5-23. |
| CR-C5-18 | **Closed by D-65** (D5 implements, CR-C5-20) | Wall 2.0 / rim 3.0 / R 1.0 / 25 mm: RF @RF@ at 59.25 N ult on 3 meshes. |
| CR-C5-19 | **Closed by D-65** | `landing_n_design` 6.6; at the lightest flying mass n is 6.60 (follow-up CR-C5-22). |
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
