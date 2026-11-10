# C5 change requests

Revision C5-R4 (2026-11-09). Inputs: params A1-R4 (D-47), A3's R5 roll-up with the D-47 bay (20:36 run), B3's R3 CG
range, D2's R5 pod params and D5-R4. Numbers from `python -I redesign/team/C5/landing_calc.py` (claims
`team/C5/claims.json`, report `LANDING.md`).

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-C5-14** (new) | D2 (cc A3, H3, C3) | (a) Publish the R5 bay in `CL-D2-*`: forward stop aft face −0.1212, nose inner −0.1252, block A 1 mm, travel. (b) Re-point `CALC-D2-NOSE-EXT` / `CALC-D2-STATION` at the D-47 stations (`pack_x_per_pack_m`) and C5's per-pack block lengths `CL-C5-BLOCK-L-503`, `CL-C5-BLOCK-L`, `CL-C5-BLOCK-L-680`, not at `CL-C5-PACK-X-B3*`. The B3-target trim stations are a cross-check only. (c) Cut block B to fill the stop-to-spreader gap: 25.2 / 27.7 / 35.7 mm. (d) H3: print the most forward allowed station per pack on the flight card (rule S9). | D-47 fixed the stations. `CALC-D2-NOSE-EXT` still reads C5's trimmed stations and now drifts (ext 10.6 → 21.6 mm, a false alarm). A 503 g pack trimmed onto the B3 target (−0.0264) leaves 0.0 mm of block. | margins at the D-47 marks +1.9 / +3.0 / +4.9 mm (`CL-C5-PACK-ROOM-MARGIN-503/-550/-680`); block B needed 24.3 / 25.7 / 31.8 mm; most forward station −0.0264 / −0.0250 / −0.0189 m |
| CR-C5-06 (updated) | H3 (cc H2, D7, I1) | Flight-card stance rules S1–S9 (LANDING.md §4). New: S7 check the groove **after every landing** (2.3 normal landings per cartridge at D5-R4); S9 pack at its mark only, never forward of it. Landing mat; 16 spare cartridges of each type, pre-crushed. | D5-R4 set 1.28 mm per landing; crush block margin 1.9 mm. | `CL-C5-LANDINGS-PER-CARTRIDGE` 2.35; `CL-C5-V-PARK-GUST` 5.3 m/s mat / 4.5 grass |
| CR-C5-04 | D5 (cc D1) | Keep the wingtip TE corner caps (`GER-007`). | At A3-R5's I_zz the corner clears by only +2.4 mm in the worst roll landing (was −2.1 mm). That is inside the model's accuracy. | `CL-C5-WINGTIP-CLEAR-ROLL` +2.4 mm |
| CR-C5-05 | F4 (cc H2, B3) | Wingtip-into-wind landing heading; spin-min within 0.5 s of landing detection. | Forwarded by A1. | `CL-C5-V-LAND-BROADSIDE` 4.41 m/s `FAIL`; spanwise 8.2 m/s; `CL-C5-LAM-MAX` 0.71 |
| CR-C5-07 | C3, D2 | Bond the aft stop wall to the side guides; no screw heads within 5 mm of the pack faces. | Forwarded by A1. | 85 N |
| CR-C5-08 | H2 | Log touchdown ground speed and time to spin-min for 20 twin landings. | Forwarded by A1. | — |

## Closed or withdrawn in R4

| Id | Status | Note |
|---|---|---|
| CR-C5-10 | **Closed by D5-R4** (CR-D5-22) | Delivered cartridges U 39.6 / L 35.4 N, bias 1.056, pre-crushed. Pitch pair-first 31.4 of 35 mm, n 5.88 (`CL-C5-DYN-PAIR-CUR`, `-N-CUR`). C5's optimum bias at A3-R5 inertia is 1.055. |
| CR-C5-12 | **Superseded by D-47** | The bay moves with the nose, and the crush block stays whole. All three packs pass at their D-47 marks. |
| CR-C5-13 | **Withdrawn by C5** (C3/D2 close it) | At R5 block A is 1 mm. A full-section stop gains only 0.5 mm, and D2's 3 × 25 × 54 mm stop passes for every pack (`CL-C5-PACK-ROOM-C3-STOP` +1.4 mm). Keep the 4 g. |
| CR-C5-11, -02, -09, -01, -03 | Closed earlier | D-30 / D-38, D-25, C1 μ 0.7, A2 wording (CR-A2-20, -21). |

## Answered here

- CR-A1-46 / CR-A1-43 (C5 part): `IndexError` fixed (the pack row is now `PWR-001`, found as the single power/energy
  row); re-run on D5-R4 and A3-R5; `CALC-C5-CRASH` per pack on the R5 bay; tip-over with the D-47 CG rise
  (+5.1 mm, −0.42°, worst 31.8°, corner bound 30.6° unchanged).
- CR-A2-21a: `verifies` dropped on `CL-C5-DYN-LEVEL-CUR` and `-PAIR-CUR`. Both are now cross-checks of D5-R4's
  delivered foot.
- CR-A4-47: claims name `GER-008-LR/LL` (lower cartridges); the `FEET` list no longer names `GER-003-LR/LL`.
- CR-D2-10: `CL-C5-BLOCK-L` per pack mass published (`-503`, `-680`).
