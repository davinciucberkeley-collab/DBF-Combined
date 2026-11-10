# D2 change requests

Revision D2-R5 (2026-11-09), params A1-R4. Numbers from `team/D2/pod_claims.py`, `team/D2/pod_data.py`,
`team/D2/pod_station_options.py` and `subsystems/pod/params.json`. Status of every request: `PROPOSED`.

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-D2-22** (new) | E2 (cc A1, F1) | Strike the 157 Ã— 48 Ã— 43 mm alternative SKU from the pack list, or tell D2 before the order | The D-47 bay is 177.2 mm stop to stop. A 157 mm pack plus the 1.5 mm spreader leaves an 18.7 mm crush block, shorter than C5's 25.7 mm, and at the 680 g station its aft face would be at 0.0645, past the 0.056 aft stop | bay `CL-D2-BAY-L` 0.1772 m; `CL-C5-BLOCK-L` 25.7 mm |
| **CR-D2-10** (re-stated R5) | C5 (cc A1, C3) | Re-run `CALC-C5-CRASH` on the D-47 bay. Block A is deleted. The forward stop (aft face âˆ’0.1212) is now backed by the nose wall through a 1 mm microballoon epoxy line, so it no longer breaks off and rides into block A. Block B per pack: 680 / 550 / 503 g = 35.7 / 27.7 / 25.7 mm. Publish `CL-C5-BLOCK-L` per pack mass so D2 can drop its linear scaling. Your `landing_calc.py` parts lists: the crush block is now `POD-009` (the spreader is `POD-010`, the spacers stay `POD-008`) | D-47 took away the 7 mm of block A stroke, and the crush plateau now goes into the nose wall | `CL-D2-BLOCK-B-NOM` 27.7 mm (â‰¥ 25.7); `-BLOCK-B-LIGHT` 25.7 (â‰¥ 23.5 scaled); `-BLOCK-B-HEAVY` 35.7 (â‰¥ 31.8 scaled); section 2 849 mmÂ²; `CL-D2-PACK-FWD-ROOM` 2.0 mm |
| **CR-D2-11** (re-stated R5) | C3 | Re-run `pod_structures.py` on D2-R5. (a) The aft stop has moved from the handle bridge to the tray rear piece. It is 3.0 Ã— 55 mm, its top 29.5 mm above the tray, with 2 gussets 6 Ã— 3 mm, and the rear-piece bond is 4 172 mmÂ². Check the peel at the stop root: 85 N at 27.5 mm is 2.3 N m. (b) The nose wall now takes the block's crush load through the stop (1 350 mmÂ² epoxy face). Check the wall and its edge bonds. (c) `ASM-D2-FWD-STOP` is now [1 mm bond line, 3 mm stop]. (d) The handle (`E-POD-09`) carries handling loads only | D-47 put the aft stop 9 mm ahead of the recess end, over the tray, where the bridge cannot reach without crossing the guides | `CL-D2-FWD-STOP-BOND` 182 N, `CL-D2-AFT-STOP-BOND` 417 N (â‰¥ 85 N at C6's 100 kPa) |
| **CR-D2-18** (new) | F2 (cc F1, F3) | The wire channel moves from x âˆ’0.0655 to **âˆ’0.0245** (âˆ’0.0295 â€¦ âˆ’0.0195, still 10 Ã— 3.5 mm). It now lands on the PDB plate (left) and the FC (right). Straps move to x âˆ’0.054 / 0.016. `pack_aft_face_m[0]` is now 0.048 (`harness.py` reads it and `strap_x_m`) | After D-47 the forward strap slot (âˆ’0.0725 â€¦ âˆ’0.0355) sits on the old channel | `CL-D2-FLOOR-CH-H` 3.5 mm; crossing gap and side exits unchanged |
| **CR-D2-19** (new; answers CR-A5-27) | A5 (cc A3) | (a) The trim kit is split into three single-material parts, so each declared CG is the body centroid (0.0 mm): `POD-008` spacers, `POD-009` crush block, `POD-010` spreader. (b) `POD-001` (14.7 mm) and `POD-003` (10.0 mm) are bonded foam board + XPS + PETG parts. Their declared CGs are mass-weighted from the bodies, which is the physical CG. Please weight the body centroids by the material tag that starts each pod body name (`fb`, `xps`, `petg`, `petgb`, `eva`; densities in `subsystems/pod/params.json` and `fins.areal_mass_kgm2`), or record these two as by-design differences. (c) `cad_claims.py` reads `pack_aft_face_m` (now 0.048 / 0.056) | A uniform-density centroid is not the CG of a part made of 30 and 1 270 kg/mÂ³ materials. Block A used to offset `POD-001`; it has been deleted | `pod_data.py` prints the comparison per part |
| **CR-D2-20** (new; supersedes CR-D2-17) | A4 | Plan changes at R5: new parts `POD-009` and `POD-010`; `POD-008` renamed "trim spacer set"; `E-POD-10` part_b `POD-007` â†’ `POD-002` (the aft stop is on the tray); `E-POD-11` part_a `POD-008` â†’ `POD-009`; new `E-POD-13` `POD-010`â€“`POD-009` `CT-SLIDE-STOP`. The R4 items in CR-D2-17 (`CT-M3-PA66-NUT`, `E-POD-05` field joint, `E-POD-12` thermal, acknowledgements) still stand | D-47 re-lay and CR-A5-27 | merge_check: pod 10 parts, 0 errors |
| **CR-D2-21** (new) | A3 (cc A1, H3) | Re-run the roll-up on D2-R5: pod 131.0 g, CG (âˆ’0.0071, âˆ’0.0025, 0.0503). The 503 g station is âˆ’0.024 rather than âˆ’0.0245, because the 2 mm spacer steps give 10 mm (+0.12 mm aircraft CG); a 12 mm stack gives âˆ’0.026 with block B 23.7 mm. Forward room at 550 g is 2.0 mm with C5's 25.7 mm block (D-47 quoted 3.4 mm with 24.3 mm). A1's "680 g on an 8 mm spacer" means 8 mm aft of nominal: the 680 g pack flies with **no** spacer, on the aft stop. H3: spacer colours are 2 white, 4 yellow, 6 green, 8 blue | Keep the CG chain on what the hardware can do | `CL-D2-PACK-X-NOM` âˆ’0.022, `-LIGHT` âˆ’0.024, `-HEAVY` âˆ’0.014; `CL-D2-MASS` 131.0 g |
| **CR-D2-04** (R3, unchanged) | D1 | Recess x 0.0226 â€¦ 0.065, floor z 0.015, y Â±0.070; no tape over x 0 â€¦ 0.095, y Â±0.070; spar slot filled flush over the spar at \|y\| < 0.029 (foot bridge), open at y Â±0.029 â€¦ 0.053 (saddles); ties under the spar at y Â±0.036. D-47 does not change the recess | handle feet on the spar | bridge 766 mmÂ²; saddles 680 mmÂ²; ties 2 Ã— 222 N |
| **CR-D2-13** (rev. R4) | F1 (cc F2) | Confirm against your PWR-R1 frame: PDB plate x âˆ’0.038 â€¦ âˆ’0.004, inserts on a 25 mm square (placeholder), insert face z 0.0266; UBEC plate x 0.044 â€¦ 0.072; park zone x 0 â€¦ 0.060 is yours (`PWR-006`). The wire channel now lands on the PDB plate (CR-D2-18) | your module reads `pdb_plate_x_m`, `plate_t_m`, `ubec_zone_x_m` live | `CL-D2-GPS-CLR` 0.152 m â‰¥ 0.10 |
| **CR-D2-14** (R3, unchanged) | F3, F5 | Antenna B tube is 20.5 mm below the boom axis, so the boom sleeve must be non-carbon. Antenna B to the pack is now 38 mm (â‰¥ 30.7) | F5's 31 mm rule | `CL-D2-ANT-B-CLR` 38 mm |

## Closed or superseded

| Id | Outcome |
|---|---|
| CR-D2-16 | adopted as D-47 (âˆ’0.130 / 0.225, the 503 g variant); D2 re-laid the bay at R5 |
| CR-D2-09 | adopted as D-48 (pod 131 g); R5 is 131.0 g `EST`, 0 g margin |
| CR-D2-17 | folded into CR-D2-20 |
| CR-D2-01, CR-D2-03 | adopted (D-25) |
| CR-D2-02 | superseded by D-24 |
| CR-D2-05, -06, -07 | answered (C3, F3, F1) |
| CR-D2-08, CR-D2-15 | replaced by CR-D2-17 |
| CR-D2-12 | withdrawn (C6's PA66 stack adopted) |

## Requests to D2 answered at R5

| Id | From | Answer |
|---|---|---|
| CR-A1-43 / D-47 | A1 | Done. Nose âˆ’0.130, length 0.225 (from params). Nose skin to stop face is 8.8 mm (`CL-D2-NOSE-TO-STOP`): block A was deleted and the 1 mm left is an epoxy line. Forward stop at âˆ’0.1212 and aft stop at 0.056 (now on the tray). Block B is â‰¥ C5's 25.7 mm; spreader 1.5 mm. The pack nominal centroid is read from `pod.pack_x_nominal_m` (âˆ’0.022), and `pod.py` refuses a local aft face that disagrees. Spacer set 2 / 4 / 6 / 8 / 8, colour-coded per pack: 680 g none (âˆ’0.014), 550 g blue (âˆ’0.022), 503 g blue + white (âˆ’0.024). The pitot socket moved with the nose; the boom is unchanged at 107 mm (tip âˆ’0.210). The spar saddle `POD-007` stays at x 0.080. `subsystems/pod/` is published at R5. Mass is 131.0 g against 131 g |
| CR-A3-22 | A3 | Done as above. Forward room is 2.0 mm with C5's current block (3.4 mm with 24.3 mm), and the 0â€“22 mm spacer travel is kept (set total 28 mm). See CR-D2-21 |
| CR-A5-27 | A5 | `POD-008` is now 0.0 mm after the split. `POD-003` is recomputed from the bodies at 10.0 mm, with the residual explained in CR-D2-19. All `cg_xyz_m` are regenerated from the bodies by `pod_data.py` |
