# D2 change requests

Revision D2-R4 (2026-11-09), params A1-R3. Numbers from `team/D2/pod_claims.py`, `team/D2/pod_data.py`,
`team/D2/pod_station_options.py` and `subsystems/pod/params.json`. Status of every request: `PROPOSED`.

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-D2-16** (new) | A1 (cc B3, A3, C5, C3, B4, F3) | Decide the pack station and, with it, **`pod.x_le_m` −0.115 → −0.127** and **`pod.size_m` L 0.210 → 0.222** (nose +12 mm; tray, hatch, handle, aft stop unchanged). The bay follows by itself: the forward stop is now derived from the nose (`CL-D2-FWD-STOP-X`). If A1 takes C5's 503 g station (−0.0207), make it −0.130 / 0.225 (+15 mm) and D2 adds a 6 mm spacer (set 2/4/6/8/8). Pitot tip stays at −0.195 (boom 12 mm shorter, 95 mm) | B3 (CR-B3-18 −0.012), A3 (CR-A3-15 −0.0104) and C5 (`CL-C5-PACK-X-B3` −0.0144) all put the 550 g pack forward of −0.001; today the most forward station that keeps C5's block B is **−0.0038** (`CL-D2-PACK-X-FWD-MIN`). CR-A3-15's alternative (forward stop 6 mm forward) deletes block A and still leaves block B 2 mm short | `CL-D2-NOSE-EXT-NOM` 10.6 mm, `-LIGHT` 14.7 mm. At +12 mm: B3's 503 / 550 / 680 g stations −0.015 / −0.012 / 0.000 fit with block B 25.7 / 28.7 / 40.7 mm (≥ 22.7 / 24.9 / 30.7, block scaled with pack mass `UNVERIFIED`) and spacers 22 / 19 / 7 mm. Pod 131.2 g (+3.2 g), frontal area unchanged |
| **CR-D2-09** (rev. R4) | A1 (cc A3, C3) | `mass.allocation_g.pod` 122 → **128 g** (131 g with CR-D2-16) from the reserve | R4 adds what others asked: C6 corner fillets 1.5 g, UBEC plate (F1) 1.0 g, JR tie bar (F2) 0.5 g, solid tray front under the forward stop 0.8 g. Taken off at R4: plates 1.0 → 0.8 mm (−1.3 g), PA66 mast hardware (−1.1 g), grip groove (−0.5 g), park slot left to F1's frame (CR-F1-16) | `CL-D2-MASS` 128.1 g vs 122 (−5 %); CG (0.000, −0.002, 0.051) m; all `EST` until `T-D2-WEIGH` |
| **CR-D2-04** (R3, unchanged) | D1 | Recess x 0.0226 … 0.065, floor z 0.015, y ±0.070; no tape over x 0 … 0.095, y ±0.070; spar slot filled flush over the spar at \|y\| < 0.029 (stop bridge), open at y ±0.029 … 0.053 (saddles); ties under the spar at y ±0.036 | handle feet and stop bridge on the spar | bridge 766 mm²; saddles 680 mm²; ties 2 × 222 N |
| **CR-D2-10** (R3, re-stated) | C5 (cc A1, C3) | Re-run `CALC-C5-CRASH` on the R3/R4 bay: nose wall inside face −0.1102 (4.8 mm board), block A 7.0 mm, block B section 2 849 mm², travel 37.2 mm; give `CL-C5-BLOCK-L` per pack mass (503 / 550 / 680 g) so CR-D2-16 can use your numbers instead of D2's linear scaling. CR-C5-13 (full-section forward stop) still waits for C3's break-off load | the build graph shows `CALC-C5-CRASH` drifting on `CL-D2-BAY-H` and `CL-D2-PACK-TRAVEL` | `CL-D2-BLOCK-B-NOM` 27.7 mm; `CL-D2-FWD-STOP-BOND` 180 N |
| **CR-D2-11** (R3, re-stated) | C3 | Re-run `pod_structures.py` on D2-R4. It fails today on keys D2 retired at R3: `stop_wall_h_m` → `aft_stop_m[1]` (aft) / `fwd_stop_m[1]` (forward); `width_m` → `params.json#pod.size_m[1]`. Aft stop 3.0 mm on `POD-007` (bridge between the saddles, 2 gussets); tray split at x −0.0705 … −0.0605 (front piece 1 798 mm² carries the forward stop, `CL-D2-FWD-STOP-BOND` 180 N at C6's 100 kPa); plates 0.8 mm; fillets per CR-C6-17 | `CALC-C3-*` all error in the build graph | pack +x 40 N limit, 85 N ultimate |
| **CR-D2-13** (rev. R4) | F1 (cc F2) | Confirm against your PWR-R1 frame: PDB plate now x −0.038 … −0.004 (CR-F3-12 b), inserts still a 25 mm square (placeholder until the bus board is cut), insert face z 0.0266; UBEC plate x 0.044 … 0.072, 0.8 mm; park zone x 0 … 0.060 is yours (`PWR-006`), F2 asks it against the inboard guide (CR-F2-03 b) | your module reads `pdb_plate_x_m`, `plate_t_m`, `ubec_zone_x_m` live | `CL-D2-GPS-CLR` 0.152 m ≥ 0.10 |
| **CR-D2-14** (R3, unchanged) | F3, F5 | Antenna B tube 20.5 mm below the boom axis: the boom sleeve must be non-carbon | F5's 31 mm rule | `CL-D2-ANT-B-CLR` 44 mm |
| **CR-D2-17** (new) | A4 | Graph changes at R4: `E-POD-06` via new `CT-M3-PA66-NUT` (replaces `CT-M3-BRASS-NUT`, C6's stack); `E-POD-05` `field_joint: true`; `E-POD-12` declared with a thermal block (E3 values); pod acknowledges `E-PWR-03/-04/-05`, `E-AVN-01 … -05, -07, -10`, `E-HRN-01` and no longer `E-PWR-01/-02` (they land on F1's `PWR-006`, CR-F1-16) | CR-A4-23 (a)–(d) | — |

## Closed or superseded

| Id | Outcome |
|---|---|
| CR-D2-01, CR-D2-03 | adopted (D-25) |
| CR-D2-02 | superseded by D-24 |
| CR-D2-05, -06, -07 | answered (C3, F3, F1) |
| CR-D2-08, CR-D2-15 | replaced by CR-D2-17 |
| CR-D2-12 | withdrawn: D2 adopts C6's PA66 stack (CR-C6-18) |

## Requests to D2 answered at R4

| Id | From | Answer |
|---|---|---|
| CR-F2-03 | F2 | (a) side-wall exits 16 × 12 at x 0.056 … 0.072, z 0.027 … 0.039, both sides; aft exits for servo leads. (b) park is F1's cradle: passed to F1 (CR-D2-13). (c) 6.7 mm leg-to-aft-wall, 54 mm high (`CL-D2-CROSS-GAP`, `-CROSS-H`). (d) 10 mm channel at x −0.0655 (not −0.065: keeps the strap-slot border), 3.5 mm under the pack, guides notched 3 mm (`CL-D2-FLOOR-CH-H`). (e) GPS cable in the right leg, window z 0.055 … 0.065 on the outboard face, groove under the grip, hole up into the mast bore; left leg empty. (f) JR tie bar x 0.0285 … 0.0325, 3 slots. (g) UBEC zone x 0.044 … 0.072 |
| CR-F3-12 | F3 | (a) tie posts at +7.5 / +32.5 mm (inner faces 21 mm), in params. (b) avionics plate to −0.040, PDB plate from −0.038. (c) 11 × 2 mm strap slot at each FC end-stop root. (d) socket bore keyed, flat 5.8 mm across on +z. (e) acknowledged. (f) FC 13 mm on 4 gel cubes noted |
| CR-C6-17 | C6 | 6 mm microballoon fillets ±30 mm of each strap, 1.5 g |
| CR-C6-18 | C6 | adopted: M3x16 PA66 + PA66 nut, grip 10.0 mm (≤ 11.0), 6.0 mm past the grip |
| CR-C6-19 | C6 | met by F3's strap through the end-stop slots (CR-F3-12 c) |
| CR-A4-23 | A4 | (a)–(d) done (CR-D2-17) |
| CR-F1-17 | F1 | UBEC plate added |
| CR-B3-18, CR-A3-15, CR-C5-12 | B3, A3, C5 | A1's decision; D2's ready option is CR-D2-16 |
