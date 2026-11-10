# D3 change requests

Raised by D3 (fins and motor-tube designer). Numbers come from `subsystems/fins/` (CAD, `make_fins.py`) and
`team/D3/claims.json`. R3 requests (2026-11-09, answering CR-A1-28) first; R2 requests below with A1's disposition.

## R3 (open)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-D3-16 | A1 (A3, C4) | Raise `mass.allocation_g.fins` **408 → 418 g** (+10 g from the A1 reserve), or pick one lever below | The 408 g basis (C4's 402 + 6) predates the R3 joints: 16 mm collar with the 40 mm two-face tail (CR-C6-01/03), CF pins (CR-C6-02) and strap eyes (CR-H1-08). D3 already took 10 × 2 braces (−9 g, CR-C4-16), ASA (−1 g), a 29 × 30 mm plate and 1.2 mm tail walls | CAD 417.3 g (`CL-D3-MASS`, incl. +0.5 g tie lugs for CR-F2-05); collars 22.9 → 42.2 g, pins 4.3 g, eyes 1.8 g. Levers: block fill 0.55 → 0.45 (−14 g, C4 re-checks `CL-C4-D3-BLOCK-MS`); cheek length 12 → 8 mm (−4 g, C4 re-checks the 894 N·m/rad rocking stiffness); tongue fill 0.45 → 0.30 (−3 g, C6) |
| CR-D3-17 | C6 | Re-run `joints.py` on R3 geometry and re-issue the `E-FIN-*` blocks: collar bond 1 106 mm² (16 mm ring, was 829); strip tail 790 mm² two faces (39.5 mm embedment); tail tension through walls 1.2 mm + cap 1.2 mm + tongue (3 perimeters + 20 % gyroid, `station_collar.tongue_fill` 0.45, ≈ 95 mm² effective, ≈ 14 MPa at 1 348 N); motor stack now a uniform 4.5 mm canted ASA plate (`E-FIN-61…64`, 3.5 mm engagement, head bears flat); pins `E-FIN-69…80` | `fin_detail` changed under your calcs (two layers, collar 16 mm, tail 40 mm, brace 10 × 2): `CL-C6-COLLAR-L-REQ` re-runs to 14.7 mm, `CL-C6-STRIP-EMBED-REQ` to 22.7 mm | `CL-D3-COLLAR-H` 1.09, `CL-D3-TAIL-EMBED` 1.74 |
| CR-D3-18 | C4 | Re-run `fin_structures_d3.py` on R3: two layers, brace 10 × 2 (your CR-C4-16), mount 11.0 g ASA with CG from `FIN-003-*` `cg_xyz_m`, collar 10.6 g at z 0.1435–0.1595 (ear unchanged at 0.1535), square tip (top edge flat x 0.280–0.320 at ±0.21, strips end at 0.280), notch at the LE-top corner (40 × 11 mm filled by the PETG tongue) | Edge-strip length 229 mm (was to the TE tip); mass and CG of the mount and collar changed | `subsystems/fins/interfaces.json` |
| CR-D3-19 | D5 | Tip geometry for the shoe: top edge flat at \|z\| 0.210 from x 0.280 to 0.320, laminate 9.6 mm, **no edge strip or pin in the last 40 mm** (strips and pins end at x 0.280 / 0.264), so the shoe sees bare laminate only; acknowledge `E-GER-01…04` stays as is | CR-D5-03, CR-A1-34 | `CL-D3-TIP-SQUARE` 1.08, `CL-D3-TIP-W` 9.6 mm |
| CR-D3-20 | H1 | Strap eyes: one per fin root on the block bosses, outboard of the tube at (x 0.042–0.048, \|y\| 0.334–0.345, z +0.020…+0.030 and −0.008…−0.018 m), Ø 4 mm hole along x at \|y\| 0.340, rated 29.4 N × 1.5 × 1.25 with RF 9.8 (shear-out); pull along any direction in the y-z plane | CR-H1-08 | `CL-D3-STRAP-EYE-RF`, T-D3-EYE |
| CR-D3-21 | A5 (A4) | Skeleton and datums at R3: `DX-COLLAR-<st>` ring z ±0.1435…±0.1595 (16 mm, ear mid ±0.1535 unchanged), tail to x 0.096; mount plate canted 7° (corner 2.5 mm ahead of the face at the axis); instance ids `FIN-001-<st>`, `FIN-011-<st><O/I>`, new `FIN-012-<st>` (pin sets) and edges `E-FIN-69…80` | A4 register matches by id | `subsystems/fins/interfaces.json` |
| CR-D3-22 | E1 | Motor interface at R3: canted ASA plate 29 × 30 × 4.5 mm (uniform along the screw axis), M3×8 engages 3.5 mm at every hole, 0.20 N·m + Loctite 243 tip only; 10 mm square shaft opening; please confirm base ≥ 28 mm, pattern 16 × 19 mm and screw-hole depth ≥ 4.0 mm on the first motor (T-E1-MOTOR-RM) | CR-C6-10, D-27 | `CL-D3-SCREW-ENGAGE` 3.5 mm |
| CR-D3-23 | F2 (C4) | Answer to CR-F2-05: (a) lead hole Ø 8 mm through every half-fin at x 0.086 but **22 mm off the skin** (centre z +0.0447 upper, −0.0307 lower), not 10 mm; (b) tie lugs built: 3 × 1.5 mm slot, open along z, on the inboard face of each boss-tail wall (x 0.071, y ±0.313, upper z 0.024–0.029, lower −0.016…−0.011) and on the outboard collar-tail wall (x 0.084, y ±0.3274, top 1 mm under the tail edge); (c) `E-HRN-03/05/06…09` acknowledged. Please move the hole in the wire list and BUILD step 4 (lead +12 mm per half-fin); C4: one 8 mm hole 22 mm off the root in a 9.6 mm laminate, please confirm the face margin | At 10 mm the hole edge (6 mm) sits inside the 12 mm root fillet and the 15 mm skin-tape lap: it would cut the root joint that carries the foot side load (`CL-D3-ROOT-FILLET-RF` 1.74) | `CL-D3-WIRE-HOLE-CLEAR` 2 mm (≥ 1); flange edge 17 mm off the skin; fins mass +0.5 g (lugs) |
| CR-D3-24 | D1 | Acknowledge `E-FIN-49`…`60` in `subsystems/wing/interfaces.json` (blocks on the spar `WNG-002` and in the core pockets `WNG-001`, half-fin roots on bare foam, anchors on the spar) | Now declared as live edges since D1-R1 declared `WNG-001/002`; `merge_check.py` warns one-sided on all 12 | pockets x 0.0279–0.0972, y ±0.302–0.338; anchors 20 × 16 mm at (0.080, ±0.242) (CR-D3-03) |

## R2 (disposition from `params/CHANGE-LOG.md`)

| Id | To | What (short) | A1 disposition |
|---|---|---|---|
| CR-D3-01 | A1 | Tube 0.344 m | accepted (D-26) |
| CR-D3-02 | A1 | One board layer | rejected (D-26); D3 uses two layers |
| CR-D3-03 | D1 (C2) | Block pockets, anchors, root-before-skin sequence, declare `WNG-001/002` | forwarded; `WNG-*` still not declared |
| CR-D3-04 | A1, E1 | Prop plane −0.0082, face 0.0309 | accepted (D-28) |
| CR-D3-05 | D6 | Link slot x 0.2376–0.2616 | forwarded |
| CR-D3-06 | E1 | Screw stack | superseded by CR-D3-22 |
| CR-D3-07 | F4 (B4) | Cant sense: print A on UR/LL, B on UL/LR | forwarded; sense unchanged at 7° |
| CR-D3-08 | D5 (A4) | Ids `RU/LU/RD/LD` | rejected (D-26); D3 renamed to `FIN-001-UR/UL/LR/LL` |
| CR-D3-09 | I1 | Buy list | forwarded; add 1 m CF rod Ø 2 mm, brace strip now 10 × 2 |
| CR-D3-10 | C4 | Re-run on the D3 geometry | done by C4 (`CL-C4-D3-*`); R3 re-run is CR-D3-18 |
| CR-D3-11 | D7 | Anchors at y ±0.234–0.250 | forwarded (D-31) |
| CR-D3-12 | F2 | ESC position and tie points | forwarded |
| CR-D3-13 | A4 | Interfaces update, `CT-THERMAL-CONTACT` | forwarded (D-46); R3 adds CR-D3-21 |
| CR-D3-14 | A5 | Skeleton and datums | forwarded; R3 numbers in CR-D3-21 |
| CR-D3-15 | B4, B1 | Collars, braces, pads in the drag and download models | forwarded |
