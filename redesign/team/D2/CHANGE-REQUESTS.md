# D2 change requests

Revision D2-R3 (2026-11-09), params A1-R3. Numbers from `team/D2/pod_claims.py`, `team/D2/pod_data.py` and
`subsystems/pod/params.json`. Status of every request: `PROPOSED`.

## Open

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| **CR-D2-09** (new) | A1 (cc A3, C3) | `mass.allocation_g.pod` 122 → **128 g** from the reserve. Alternative (b): F1 mounts the PDB on ties instead of 4 inserts (−3.5 g, see CR-D2-13) and the allocation goes to 124 g | R3 adds scope the 122 g did not count: spreader 1.5 mm (C5) 5.3 g, PDB plate + inserts (C6/F1) 4.0 g, aft stop moved onto a spar bridge with gussets (+3 g over a tray stop), pitot flange (C6) 2.2 g, 45° GPS pad (F3) 1.0 g, EVA pads 1.1 g, light tape (E3) 1.5 g, antenna tubes (F5) 0.7 g. Already trimmed: side plates 1.5 → 1.0 mm (−3.4 g), saddle tongues 24 → 14 mm (−2.1 g), GPS base plate dropped (−1.0 g) | `CL-D2-MASS` 127.3 g vs 122 (−4 %); CG (0.001, −0.003, 0.052) m; all `EST` until `T-D2-WEIGH` |
| **CR-D2-04** (rev. R3) | D1 | As R2 (recess x 0.0226 … 0.065, floor z 0.015, y ±0.070; no tape over x 0 … 0.095, y ±0.070), plus: **fill the spar slot flush over the spar at \|y\| < 0.029** (the handle's stop bridge bonds on it) and leave it open at y ±0.029 … 0.053 (saddles); the two ties under the spar move **y ±0.048 → ±0.036** | The pack's aft face reaches x 0.073 (680 g) and the aft stop sits at 0.077, over the spar slot; the handle legs moved to y ±0.048 so the pack leads can turn inboard of them | bridge 766 mm² on the fill; saddles 680 mm² on CF; ties 2 × 222 N |
| **CR-D2-10** (new) | C5 (cc A1, C3) | Re-run `CALC-C5-CRASH` on D2-R3 geometry: nose wall inside face **−0.1102** (4.8 mm foam board, not the 2 mm of `ASM-C5-NOSE-WALL`) → block A 7.0 mm (`CL-D2-NOSE-INNER`, `-NOSE-BLOCK-L`); block B section **2 849 mm²** (52 × 59.4 on the tray, less a 30 × 8 vent groove), not bay W × H (`CL-D2-BLOCK-SECTION`); travel 37.2 mm. D2 holds A1's station (−0.001 nominal, block B 27.7 mm ≥ your 24.9); the most forward station that keeps block B is **−0.0038** (`CL-D2-PACK-X-FWD-MIN`). Your R3 stations (−0.0144 / −0.0207) need CR-C5-12 decided by A1 first. CR-C5-13 (full-section forward stop): ready in the CAD (`fwd_stop_m` height), +4.1 g, not adopted until C3 confirms the break-off load | D-25 sized the block at A1's station; the vent groove (E3) and the tray under the block change your A_bay | `CL-D2-BLOCK-B-NOM` 27.7 mm; `CL-D2-AFT-REACH` 0.007 m |
| **CR-D2-11** (new) | C3 | Re-run `pod_structures.py` on D2-R3: aft stop 3.0 mm now on **POD-007**, standing on a 3 mm bridge between the spar saddles (x 0.077 … 0.090, y ±0.029) with two 8 × 3 mm gussets at its ends: the +x pack load goes stop → bridge → saddles → spar (`E-POD-09`, 1 445 mm²), not into the tray. Pack centroid 25.5 mm above the stop base (as R2). Pads 2.5 mm EVA: pack z 0.0483. Forward stop 3 × 25 × 54 as you sized; guides 1.5; tray and plates full-area epoxy; hatch tab 12 × 40. `CL-D2-TIE-CAP` now handling only; `CL-D2-BOND-STRESS` retired (CR-C3-04) | A1's 0.073 aft face lies 4 mm past the spar-slot front face (0.069): the stop cannot stand on the tray | pack +x 40 N limit (hover landing), 85 N ultimate; `ASM-D2-STOP-T` 0.003 |
| **CR-D2-12** (new) | C6 (cc F3) | Accept `E-POD-06` as **M3x16 brass SHCS + brass nut + Loctite 222 + 1 nylon washer** (`CT-M3-BRASS-NUT`, declared in `subsystems/pod/interfaces.json`) instead of A2-70 + nyloc; grip 10.0 mm with a Ø6.5 × 4.5 counterbore, 5.5 mm past the grip | F3 CR-F3-03: no steel on the mast, the bolt is 56 mm from the compass; brass nylon-insert nuts are not a stock M3 part | `CL-D2-MAST-BOLT-PAST` 5.5 ≥ 5.0 mm |
| **CR-D2-13** (new) | F1 (cc F2) | Confirm the power layout: PDB plate x −0.042 … −0.004 left channel, 4 M3 inserts on a **25 mm square (placeholder)** or say "ties" (CR-D2-09 b); fuse holder x −0.004 … 0; AS150U park 0 … 0.060 (CR-F1-13); **UBEC on the right channel floor x 0.042 … 0.088**; pack leads over the aft stop (top z 0.050), left at x 0.080 … 0.088 inboard of the leg (y −0.048), forward to the park, about 85 mm of the 100 mm lead; harness exits now **11 × 16 mm** at y ±0.053 … 0.064, z 0.027 … 0.043 (outboard of the legs) | The left channel is full; the UBEC goes beside the FC's aft end, 0.15 m from the GPS | `CL-D2-GPS-CLR` 0.153 m ≥ 0.10 |
| **CR-D2-14** (new) | F3, F5 | Placements: RX on the left floor x −0.064 … −0.044 behind the airspeed sensor (x −0.086 … −0.066, tape + 1 tie on 2 posts); antenna A tube at (−0.054, −0.046), top z 0.100; antenna B tube out of the nose at y −0.046, z 0.0245, 20.5 mm below the boom axis: **the boom sleeve must be non-carbon** (F3 names its material); GPS pad 45° to the nose, centre (0.076, 0, 0.178) | F5's 31 mm rule against carbon; the boom is the only conductor near antenna B | `CL-D2-ANT-A-CLR` 34.6 mm, `-B-CLR` 44 mm vs `CL-F5-ANT-CLEAR` 30.7 |
| **CR-D2-15** (rev. of CR-D2-08) | A4 | Plan deviations at R3: `POD-008` is the trim kit (crush block, spreader, spacers); the aft stop moved from `POD-002` to `POD-007`; `E-POD-10` is `POD-008` ↔ `POD-007`; new `E-POD-11` `POD-008` ↔ `POD-002` (block on the forward stop, `CT-SLIDE-STOP`); `E-POD-06` via new `CT-M3-BRASS-NUT` | interfaces follow the load paths | — |

## Closed or superseded

| Id | Outcome |
|---|---|
| CR-D2-01, CR-D2-03 | adopted (D-25): width 0.14, pitot y −0.046 |
| CR-D2-02 | superseded by D-24 (nominal −0.001, block ahead, spacers behind) |
| CR-D2-05 | answered by C3 (CR-C3-01 … 06); follow-up CR-D2-11 |
| CR-D2-06 | answered by F3 CR-F3-03 (gel pads, no inserts, no M2) |
| CR-D2-07 | answered by F1 CR-F1-13 (60 mm park); follow-up CR-D2-13 |
| CR-D2-08 | replaced by CR-D2-15 |

## Requests to D2 answered at R3

| Id | From | Answer |
|---|---|---|
| CR-A1-27 | A1 | done: aft face 0.069 / 0.073 (spacer 8 / 4 mm), forward stop −0.1002, nose −0.115 with block A and the 3 mm stop, width 0.14, park 60 mm, pitot y −0.046 with flange, vents, gel pads, foam tape; mass 127.3 vs 122 (CR-D2-09) |
| CR-C3-01 | C3 | adopted, except the aft stop face: 0.077 on the handle bridge, not the recess end (CR-D2-11) |
| CR-C3-04, CR-C3-06, CR-C5-02, CR-C2-07 | C3, C5, C2 | adopted |
| CR-C5-07 | C5 | stop braced by gussets and the bridge; no screw heads within 5 mm of the pack (nearest insert 7 mm into the channel) |
| CR-C5-12, CR-C5-13 | C5 | A1's call / waits for C3 (CR-D2-10) |
| CR-C6-07, CR-C6-09 | C6 | adopted (foam tape + tie; 32 × 32 flange; grip 10.0 mm, see CR-D2-12) |
| CR-E3-03, CR-F1-08, CR-F1-13, CR-F3-03, CR-F5-03 | E3, F1, F3, F5 | adopted (vents, park, gel pads, 45° pad, two antenna exits) |
| CR-I1-01 | I1 | `parts.csv` carries vendor class and `EST` cost; part numbers when F1/F2 itemise the kit |
