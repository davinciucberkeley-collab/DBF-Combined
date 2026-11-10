# D3 change requests

Raised by D3 (fins and motor-tube designer). Numbers come from `subsystems/fins/` (CAD, `make_fins.py`) and
`team/D3/claims.json`. R4 requests (2026-11-09, answering CR-A1-47 and CR-A4-40) first, then R3 and R2 with A1's
disposition.

## R4 (open)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-D3-26 | A1 (E1, A5, B4) | **Prop keep-out after D-52.** Decide one: (a) `face_ahead_m` 0.0025 → 0.020 (prop plane −0.0077 → −0.0247; mount cheeks +17 mm, C4 re-checks rocking stiffness); (b) E1/A5 give `KO-PROP` E1's real axial envelope (−6 mm aft / +10 mm fwd, `ASM-E1-BLADE-HALF`) and test the blade surface, not a symmetric 35 mm cylinder; (c) 5° cant (B4's option; still hits block, plug and wing skin). Also set `propulsion.stations.x_plate_face_m` 0.0309 → **0.02935** (DP-MOTOR-FACE at face_ahead 2.5 mm) | With the corrected sense the wing-side blade tip swings aft over the tube. `check.py` now reports 16 keep-out ERRORs: `FIN-002/004/006/009` and `WNG-001/003` | `CL-D3-PROP-TIP-GAP` 26.9 mm, mid-plane to tube face (B4 `CL-B4-GAP-TUBE` 27.3). Less the aft blade 6 mm it is 20.9 mm (< 25). Probe runs, all restored: face_ahead 0.0165 clears the fins parts, 0.020 clears everything; 3° leaves only the block. D3 keeps D-51's 0.0025 until A1 decides |
| CR-D3-27 | A1 (A3, C4) | **Mass 436.4 g vs 418 g (−18.4 g).** Take +18 g from the reserve now; D3 returns what the levers give. Levers: block fill 0.55 → 0.45 (−14 g, C4 re-checks `CL-C4-D3-BLOCK-MS` +0.55); fillet mix 0.55 → 0.45 g/cm³ if the T-D3-WEIGH cup allows (−5.9 g); mount cheeks 12 → 8 mm (−4 g, C4: 926 N·m/rad needed) | D-48 booked +3 g for the 15 mm fillets. Modelled as bodies they are 32.2 g; the old 3 g/root estimate held about a quarter of the real volume. The collar 16 → 12 mm saved 2.0 g, not 3 (the 12 mm ear already set the ring top). The ESC pad 31 mm costs +0.8 g | `CL-D3-MASS` 436.4, `CL-D3-FILLET-MASS` 32.2 (UR/UL 8.1, LR/LL 8.0 g); collars 40.2 (was 42.2) |
| CR-D3-25 | C6 (C4) | Re-run `joints.py` on R4. **Collar 12 mm**: your 12.0 mm gives RF 1.00, so T-C6-COLLAR decides; the 16 mm fallback costs +2 g. **Root fillets** as drawn in `E-FIN-53…56`: 15 mm over the last 0.15 m of *bonded* root (lower: x 0.146–0.2376), 13 mm aft of the hinge, a 6 mm bead ahead, none over the D6 slot. Accept this zoning in place of "15 mm full root chord" or say why the forward root needs 15 mm. A full-chord 15 mm fillet would add +17 g | A full-length 15 mm leg aft of the hinge leaves 0.2 mm to the elevon end, so it cannot be built. Forward of x 0.17 the D3 root model gives no credit | `CL-D3-ROOT-FILLET-RF` 2.28 typical (lower governs; upper 2.29), `-ALLOW` 1.14 at your 0.125 MPa; skin bond 5 318 / 5 078 mm² |
| CR-D3-28 | E1 | Acknowledge `E-FIN-81…88` (`CT-THERMAL-CONTACT`, E3 blocks filled from `CL-E3-MOUNT-ASA` 66.3 / 83 °C and `CL-E3-ESC-PEAK` 61.6 / 85 °C). The mount plate geometry changed with the sense (D-52), so print R4 mounts only | 8 one-sided WARN in `check.py` / `merge_check.py` | `subsystems/fins/interfaces.json` |
| CR-D3-29 | C4 | Re-run `fin_structures_d3.py` on R4: collar ring z 0.1475–0.1595 (ear unchanged, brace end \|z\| 0.1535); stepped tip (strip 224 mm, ends x 0.2746, 12 pins to x 0.2641); ESC pad 46 × 31 mm, 2.04 g; root fillets as part bodies (8.0–8.1 g per half-fin at CG from `FIN-001-*` `cg_xyz_m`); thrust side load in the D-52 sense; then the block-fill lever (CR-D3-27) | Mass and geometry moved under your FE | `subsystems/fins/interfaces.json` |
| CR-D3-30 | D5 | Tip step adopted as CR-D5-11 asked (closes it; CR-D3-19 withdrawn): `tip_square_m` 0.0454, step \|z\| 0.2005 from x 0.2746, strips end at 0.2746, last pin x 0.2641 (edge 0.2651 < 0.2666). `check.py` shows no shoe–fin overlap | D-54 | `CL-D3-TIP-STEP-MISMATCH` 0 |
| CR-D3-31 | D6, D1, F1 | Information. D6: no fillet over x 0.2376–0.2616 on either face of the lower roots (closes CR-D6-04). D1: fillets up to 15 mm on the skin each side of y ±0.320; aft of the hinge 13 mm, so 2.2 mm clear of each elevon end. F1: `E-PWR-11…14` acknowledged; the pad is now x 0.078–0.124, \|z\| 0.1025–0.1335, and your caps at x ≥ 0.127 stay clear | CR-D6-04, CR-F1-22 | — |

**Answers to I1.** CR-I1-17: yes. One 20 × 18 × 1 000 mm length gives both `FIN-006` plugs (2 × 53 mm) and C2's six
36 mm spar plugs (216 mm): 322 mm plus 8 saw kerfs, leaving about 0.65 m for crash spares. C2 must confirm its plugs
are the same stock sanded to 19.9 mm. `parts.csv` now prices `FIN-006` at $1.06 (53 mm share of $20). CR-I1-20: the
flying ASA is about 46 g (4 mounts 38.5 g of print, 4 pads 7.0 g). With a spare A/B mount set and pads (~46 g), the
E3/H1 stand mount (~10 g) and supports/brims (~30 %), the need is about 130 g. A 1 kg spool is the practical buy: a
0.5 kg spool costs nearly the same, and the rest of the spool covers reprints after crashes. One spool is enough.

## R3 (A1-R4 disposition: CR-D3-16 accepted at 418 g (D-48); CR-D3-19 superseded by D-54; the rest forwarded)

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
