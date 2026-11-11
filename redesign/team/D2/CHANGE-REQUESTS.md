# D2 change requests

Revision D2-R6 (2026-11-10), params A1-R5 (D-62, D-64, D-69). The numbers come from `team/D2/pod_claims.py`,
`team/D2/pod_data.py`, `team/D2/pod_station_options.py` and `subsystems/pod/params.json`. Every request has
status `PROPOSED`.

## Open (R7, 2026-11-11: D-74, D-77)

| Id | To | What | Why / numbers |
|---|---|---|---|
| CR-D2-31 | F1, F2 (cc A3, F3) | (a) **F1**: move `PWR-001`'s node to the D-77 datum −0.036 (read `pod.pack_x_nominal_m`, CR-A3-32): `check.py` and `merge_check.py` still put the pack at −0.022 and report CG 0.052 m; A3's override already uses the datum. (b) **F1, case U only**: `KO-PWR-SIDE` cannot be 6 mm on the outboard edge; the 37.7 mm channel leaves 1.8 mm to the side wall (`CL-D2-KO-PWR-SIDE-OUT`). Use vertical-entry GH plugs there, or turn the stack so its plugged long edge faces inboard (inboard 6 mm is clear: the forward strap moved to x −0.079). (c) **F1/F2**: route the two ESC pairs per side to the XT30U zones (`xt30u_zone_m`: right x 0.044–0.074, left 0.062–0.074 on the foot plate, z 0.0258–0.0378); the AS150U cradle must end by 0.060. (d) **F1/F2**: stop reading `ubec_zone_x_m` (status `RETIRED`); D2 deletes it after. | D-74 / D-77. Pod: 0 bodies in `KO-PWR-BOARD/-PADS/-FWD/-SIDE-IN` (`CL-D2-KO-PWR-HITS`), 0 in the XT30U zones, one XT30U body passes a side exit with 5.8 mm to spare (size `UNVERIFIED`). |

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-D2-24** (new) | A1 (cc A3, C5, H3) | (a) Read the D-62 aft stop as **0.0475**, not 0.050. Correct the D-62 / CR-A1-62 text and the `pod.pack_aft_travel_m` note ("= 0.050"). (b) The crush-stack limit −0.0379 uses the 24.3 mm block. With C5's 550 g class block (`CL-C5-BLOCK-L` 25.8 mm) the most forward centroid is **−0.0364**. Quote that one, or have C5 confirm 24.3 mm for 546–590 g packs. (c) Retire `ASM-A3-PACK-RANGE` [503, 680] in favour of `ASM-A1-PACK-CASES-G` [546, 590]. D2's stations and the pod crash mass already use it | (a) With the 0.135 Ovonic pack, x_nom + L/2 + travel = −0.032 + 0.0675 + 0.012 = 0.0475. The 0.050 figure is the same sum with the retired 0.140 pack. A stop at 0.050 would put the no-spacer station at −0.0175 and the datum on a 14.5 mm stack, off the 2 mm grid. `pod.py` now refuses a stop that disagrees with the shared keys. (b) The D-62 frame estimate at −0.036 still fits with 0.6 mm of block margin | `ASM-D2-AFT-STOP-X` 0.0475; `CL-D2-PACK-X-STACK` −0.0379 (gap 17.9 mm = 16 mm spacers + **1.9 mm play**); `CL-D2-PACK-X-STACK-C5` −0.0364 (16 mm + 0.4 mm); `CL-D2-BLOCK-B-LIGHT` 26.2 ≥ 25.6 mm |
| **CR-D2-25** (new; answers CR-C3-14 … -18) | C3 (cc A1, H1) | Re-run `pod_structures.py` / `pod_fea.py` on the R6 drawing. (a) **Strut**: pad 40 × 14 × **1.5** mm on the stop back face at x 0.0505. Three 3 × 14 mm ribs at y 0 and ±0.0185, z 0.026–0.040, **25 mm** long (x 0.052 → 0.077, not 14 mm: the D-62 stop is 12.5 mm further forward). Each rib ends in a 3 mm heel standing on the bridge top (z 0.0258), because the bridge lies below the ribs. (b) **Forward-stop T**: separate print, 3 × 54 mm upright through the floor's front-edge notch, flange 12 × 54 × **1.2** mm under the floor (9 mm of it bonded to the floor). The tray front piece now starts behind the upright. (c) **Brackets**: 2 mm web plus a **1.2 mm** flange per side, **1 232 mm²** epoxied to the wall (x 0.066–0.0902 above the side exit, z 0.041–0.0797; x 0.074–0.0902 down to the foot), total 2 464 ≥ 1 996 mm². (d) `CL-D2-AFT-STOP-BOND` is kept only as a read-out (no `verifies`). Drop `CL-C3-AFT-STOP-BOND`'s limit on it, and D2 deletes the claim | The thicknesses are D2's mass levers inside 146 g. The rib length follows the D-62 bay | Euler at 25 mm ≈ (14/25)² × 8 565 ≈ 2 700 N vs 85 N; pad bearing 0.15 MPa; `CL-D2-BRACKET-AREA` 1.23e-3 m²; `CL-D2-FWD-FLANGE-AREA` 4.86e-4 m² |
| **CR-D2-26** (new; supersedes CR-D2-10, -23) | C5 (cc A3, H3) | Re-run `CALC-C5-CRASH` and `landing_calc.py` on the D-62 bay and the D-64 cases. `pack_x_per_pack_m` keys are now **"546", "550", "590"** (−0.036 / −0.034 / −0.028); line 964 of `landing_calc.py` still loops over "503" / "550" / "680". Forward stop −0.1312, now a T clamped on the floor and backed by the nose wall. Block lengths 26.2 / 28.2 / 34.2 mm. H3: the spacer set is 2 white / 4 yellow / 6 green / 8 blue. The stacks are 2 + 6 + 8, 6 + 8 and 8 until A3 publishes the live stations | D-62, D-64 | `CL-D2-BLOCK-B-*`, `CL-D2-SPACER-*`; station table from `pod_station_options.py` |
| **CR-D2-27** (new; supersedes CR-D2-13) | F1, F2 (cc F3) | F1: (a) the UBEC envelope (41 mm) runs from x 0.044 to 0.085, past its 28 mm zone (0.044–0.072), under the handle foot (x ≥ 0.067, z 0.0228–0.0258) and the new bracket web. Fit it inside the zone (on edge, or a shorter UBEC), or ask D2 to move the JR bar. (b) The pack leads (`lead_b`) cross the aft stop at x 0.0475–0.0505 below its top (0.0503). Route them over the stop and the strut ribs (top 0.040). (c) The PDB plate now runs x −0.038 → **0.046** under your frame and cradle, with 1.2 × 3 mm ribs along the boss rows. Bosses are Ø 7.2, pattern centre unchanged, frame legs (0.056) clear. F2: your bundle legs lie in the floor at the channel and on the extended PDB plate (+0.8 mm). Lift them onto the plate and the tray | Bbox clash check of the R6 bodies against PWR-001/-005 and HRN-001 | UBEC overlap 12.5 × 4.9 × 2.0 mm with the web; the foot overlap predates R6; lead box 3.0 × 19.5 × 7.7 mm in the stop |
| **CR-D2-28** (new) | D7 (cc A1) | `check.py`: the pitot socket collar `POD-006` (front face x −0.148) overlaps your nose pad `TRN-001` by 5 mm. Fit the ½ in pad of D-62 | D-62 nose −0.140 | antenna tube B ends at −0.144 (≥ −0.150, `CL-D2-ANT-B-TIP-X`) |
| **CR-D2-29** (new; supersedes CR-D2-20) | A4 | Plan changes at R6: new pod edges **`E-POD-14`** (`POD-007` strut pad ↔ `POD-002` aft stop, `CT-EPOXY`, 560 mm²) and **`E-POD-15`** (`POD-007` wall brackets ↔ `POD-001` side walls, `CT-EPOXY`, 2 464 mm²). Brackets and strut are bodies of `POD-007`; the stop T is a body of `POD-002` | D-69 | — |
| **CR-D2-30** (new; supersedes CR-D2-21) | A3 (cc A1, H3) | Re-run the roll-up on D2-R6: pod 145.8 g, CG (−0.0074, −0.0031, 0.0483), per-part CGs from the bodies in `subsystems/pod/parts.csv` / `interfaces.json`. The CAD pack (F1's `PWR-001`) is at the −0.032 datum with a 12 mm stack. Per-pack stations are yours (CR-A3-27) | D-62 | `CL-D2-MASS` 145.8 g vs 146 |
| **CR-D2-18** (re-stated R6) | F2 (cc F1, F3) | The wire channel stays at x −0.0245 (−0.0295 … −0.0195, 10 × 3.5 mm). Straps move to x **−0.062 / 0.006**, and `pack_aft_face_m[0]` is now **0.0355** (`harness.py` reads it and `strap_x_m`). D-62: pack lead and pod crossing +10 mm (CR-A1-62) | D-62 bay | `CL-D2-FLOOR-CH-H` 3.5 mm; crossing gap 6.7 mm, side exits unchanged |
| **CR-D2-19** (re-stated R6) | A5 (cc A3) | `POD-001` (15.1 mm) and `POD-003` (9.7 mm) are bonded foam board + XPS + PETG parts. Their declared CGs are mass-weighted from the bodies, which is the physical CG. Weight the body centroids by the material tag at the start of each pod body name (`fb`, `xps`, `petg`, `petgb`, `eva`), or record these two as by-design differences. `cad_claims.py` reads `pack_aft_face_m` (now 0.0355 / 0.0475) | A uniform-density centroid is not the CG of a part made of 30 and 1 270 kg/m³ materials | `pod_data.py` prints the comparison per part |
| **CR-D2-04** (re-stated R6) | D1 | Recess x 0.0226 … 0.065, floor z 0.015, y ±0.070; no tape over x 0 … 0.095, y ±0.070; spar slot filled flush over the spar at \|y\| < 0.029 (foot bridge), open at y ±0.029 … 0.053 (saddles); ties under the spar at y ±0.036. **Add (D-69, CR-C3-17): a 5 mm microballoon-epoxy fillet in the recess-step corner (x 0.065, z 0.015–0.0198, full width) before the pod goes in.** You now model it as `WNG-007` (`E-WNG-17`): acknowledged, and the floor's aft lower edge is bevelled 45° through its 4.8 mm onto it (`floor_bevel_m`). D-62 does not change the recess | Handle feet on the spar; recess-step peel | bridge 766 mm²; saddles 680 mm²; ties 2 × 222 N |
| **CR-D2-14** (R3, unchanged) | F3, F5 | Antenna B tube is 20.5 mm below the boom axis, so the boom sleeve must be non-carbon. Antenna B to the pack is now 40.5 mm (≥ 30.7) | F5's 31 mm rule | `CL-D2-ANT-B-CLR` 40.5 mm |

## Closed or superseded

| Id | Outcome |
|---|---|
| CR-D2-22 | closed by D-64 (the named Ovonic EC5 SKU, 135 × 46 × 49 mm, fits; the 157 mm alternative is not bought) |
| CR-D2-23, CR-D2-10 | superseded by CR-D2-26 (C5) and CR-D2-25 (C3) |
| CR-D2-11 | superseded by CR-D2-25 |
| CR-D2-13 | superseded by CR-D2-27 |
| CR-D2-20, CR-D2-21 | superseded by CR-D2-29 and CR-D2-30 |
| CR-D2-16 | adopted as D-47 |
| CR-D2-09 | adopted as D-48, then D-63 (146 g) |
| CR-D2-17 | folded into CR-D2-20 |
| CR-D2-01, CR-D2-03 | adopted (D-25) |
| CR-D2-02 | superseded by D-24 |
| CR-D2-05, -06, -07 | answered (C3, F3, F1) |
| CR-D2-08, CR-D2-15 | replaced by CR-D2-17 |
| CR-D2-12 | withdrawn (C6's PA66 stack adopted) |

## Requests to D2 answered at R6

| Id | From | Answer |
|---|---|---|
| CR-A1-62 / D-62 (blocker) | A1 | Done. Nose −0.140, length 0.235 (from params). Forward stop face −0.1312; crush block ≥ C5's length and 1.5 mm spreader unchanged. Datum read from `pod.pack_x_nominal_m` −0.032 and aft stop from the shared keys: **0.0475** (CR-D2-24). The pack is drawn at the datum (F1's `PWR-001` reads `pack_aft_face_m[0]` 0.0355). On the crush stack it sits at −0.0379 with 17.9 mm to the stop: 16 mm of spacers + 1.9 mm play (`CL-D2-PACK-X-STACK`, `-STACK-PLAY`). Spacer set 2 / 4 / 6 / 8 gives every 2 mm step from −0.020 to −0.036. Published at R6, 145.8 g against 146 g, `POD-*` CGs from the bodies |
| CR-A3-25 | A3 | Superseded by D-62: the aft stop is 0.0475 and `pack_x_per_pack_m` holds A1's D-64 frame estimates. The crush-stack case and its play are above |
| CR-C3-14 … -18 / D-69 | C3 | Strut, forward-stop T with flange, and wall brackets drawn (CR-D2-25 lists the R6 dimensions). `CL-D2-AFT-STOP-BOND` is retired as a check. The recess fillet goes to D1 (CR-D2-04) |
| CR-C6-27 | C6 | Bosses Ø 7.2 mm. Unplug path: the PDB plate runs aft to 0.046 (84 × 36.7 mm) with a 1.2 × 3 mm rib along each boss row, so it acts as a rigid pad. σ b L² / 6 at 0.05 MPa gives 2.16 N·m vs 1.94 (RF 1.11, `CL-D2-PDB-PAD-M`). The field rule (thumb on the cradle) stands |
| CR-E3-15 | E3 | `E-POD-12` `t_design_c` 44.8 °C (ambient 44, D-67); SPEC thermal row 44.8 / FC 54.9 °C (68.9 hover-only) |
| CR-F3-12 | F3 | Already in since R4 and kept: tie posts 21 mm apart (from `tie_post_x_m`), avionics plate to −0.040, FC strap slots 11 × 2 mm, key flat 5.8 mm, `E-AVN-07` / `-10` acknowledged; notes say 4 gel cubes, 13 mm |
| CR-F1-26 | F1 | Left channel x −0.063 … −0.053, z 0.031 … 0.070 holds no pod body (`CL-D2-LEFT-CH-CLEAR` 0). Antenna A tube starts at z 0.076 |
| CR-D7-23 | D7 | Antenna B tube end x −0.144 (≥ −0.150, `CL-D2-ANT-B-TIP-X`) |
| CR-E2-26 | E2 | 135 × 46 × 49 mm pack drawn; bay 0.179 × 0.052 × 0.057 m |
| CR-C5-14 | C5 | (a) R6 published in `CL-D2-*`. (b) Stations from `pack_x_per_pack_m`, blocks against `CL-C5-BLOCK-L` scaled by mass. (c) Blocks are cut to fill the gap (no play) |
