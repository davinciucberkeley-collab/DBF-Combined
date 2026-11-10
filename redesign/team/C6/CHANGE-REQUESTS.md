# C6 change requests

Revision C6-R2, 2026-11-09 (params A1-R3). Numbers from `team/C6/claims.json`
(`python -I redesign/team/C6/joints.py`); report `JOINTS.md`; copy-ready blocks in `joint_stacks.json`.

## New in C6-R2

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-16 | C3 (cc D2, D5) | Point the pod allowables at the C6 values: XPS tension 125 kPa (keep your 100 kPa if you prefer, it is conservative), XPS shear 100 kPa, **board flat-wise 50 kPa** (not 100), **epoxy on paper face 100 kPa** (not 200, which is the undiscounted `ASM-D5-BOND-TAU`), PETG across layers 15 MPa, hook-and-loop 5 / 2.5 N/cm². Re-run `CL-C3-TRAY-FLAT` and `CL-C3-FLOOR-GLUE` limits on these | CR-C3-05: C6 owns the joint allowables | `CALC-C6-POD-ALLOW`; tray RF 2.54, floor glue RF 0.90 |
| CR-C6-17 | D2 (cc C3) | Inside `POD-001`, run a **6 mm-leg microballoon-epoxy fillet** along both floor-to-side-wall corners over ± 30 mm of each pack strap | The floor edge glued to the wall face carries the strap pull through the paper: 111 kPa vs 100 kPa | `CL-C6-POD-FLOOR-RF` 0.90 → `-RF-PROP` 2.03; ≈ +1.5 g `EST`; `T-C6-BOARD-CORNER` |
| CR-C6-18 | D2 (cc F3, I1) | GPS mast cross-bolt `E-POD-06`: **M3x16 PA66 screw + PA66 nut**, finger tight + ¼ turn, grip ≤ 11.0 mm; drop the A2 nyloc and washer here | F3: no steel within 50 mm of the compass; the mast is the fuse, so a nylon pin is enough | `joint_stacks.json#E-POD-06` |
| CR-C6-19 | F3, D2 | FC on gel pads `E-AVN-01`: add one 3 mm tie or 10 mm hook-and-loop strap over the board, 1–2 mm slack (does not bridge the isolation); D2 leaves two tie slots in `POD-002` beside the right channel | Gel-pad tack is not a crash retention | 10 N any axis (`ASM-C6-AVN-CRASH`) |
| CR-C6-20 | C4 (cc A4) | `CALC-C4-D3-STATIC` / the FE re-run gives a singular matrix and NaN on the current fin inputs (D3 R3: collar 16 mm, 40 mm tail); `build_graph.py` then stops in `proofkit.fmt` on the NaN before any later check. A4: make `fmt` print `nan` instead of raising | No chain check runs past it | `proofs/proofkit.py` line 108 |
| CR-C6-21 | C1 (cc A1, C4) | (a) Add the 7° tangential cant to the J-MOTOR and J-FINHALF cases: side force 12.2 % of thrust (2.57 N at the 21.1 N limit), 0.10 N·m at the motor base; C6 carries it locally (`CALC-C6-MOTOR-SCREW`, `CALC-C6-MOUNT-SIDE`). (b) `CL-C1-VD-ENV` now reads 32.1 m/s against `requirements.vd_ms` 27.2 (D-29): confirm which is meant | (a) D-27 asks C4/C6 to check it; it belongs in the envelope. (b) the servo frame and horn bond area moves 720 → 1 002 mm² | `CL-C6-MOTOR-SEP-RF` 4.12; `CL-C6-LINK-BOND-AREA-MIN` |
| CR-C6-22 | I1 | Kit at R2: M3x8 ×20, M3x10 ×6, M3x16 A2 ×6, **M3x16 PA66 ×3 + PA66 nut ×3**, M3 nyloc ×8, M3 washer ×15 → 12, M3 × 5.7 insert ×12, nylon washer 0.8 mm ×6 + 2 mm nylon spacer ×6, **CF rod Ø 2 × 1 000 mm ×2** (72 pins); FC grommets dropped (gel pads, F3) | `JOINTS.md` kit table | ≈ $26 `EST` |
| CR-C6-23 | D6 (cc B2) | Servo frames `MEC-008` and horns `MEC-004`: bonded area into XPS ≥ **1 002 mm²** each at C1's current VD (replaces 720 in CR-C6-13; falls back to 720 if C1 confirms 27.2 m/s) | Pushrod design force 125 N | `CL-C6-LINK-BOND-AREA-MIN` |
| CR-C6-24 | D3 (cc C5, C4) | Half-fin root fillets `E-FIN-53…56`: leg 12 → **15 mm** (microballoon epoxy, both faces, full root chord), or carry the C6 XPS allowable 0.125 MPa in `CALC-D3-ROOT` and size the leg there | At μ 0.7 and 0.21 m half-fins the root moment is 5.59 N·m; D3's RF 1.74 uses the undiscounted 0.25 MPa XPS strength | `CL-C6-FIN-ROOT-RF` 0.87 → 1.24 with 15 mm (leg needed 13.1 mm); ≈ +3 g `EST` for four roots |

## Status of the R1 requests

| Id | To | Request (short) | Status |
|---|---|---|---|
| CR-C6-01 | D3 | 40 mm two-face collar tail | **Adopted** (`fin_detail.station_collar.tail_m` 0.04); RF 1.76 |
| CR-C6-02 | C4, D3 | strip shear flow in the FE; Ø 2 mm CF pins every 15 mm | Pins **adopted** (`fin_detail.edge_strip.pin_*`), RF 1.15 at C4's latest strip force (908 N); (a) C4 FE check still open |
| CR-C6-03 | C4, C1, D3 | agree the collar torsion; collar 16 mm | Collar **adopted** (16 mm, RF 1.09 on 9.3 N·m + brace shear); torsion agreement open (C1 4.93, C4 R3 3.46, C4 R2 9.3 N·m limit) |
| CR-C6-04 | E3 | collar temperature vs epoxy Tg; post-cure | Forwarded by A1 (G2, G3, E3) |
| CR-C6-05 | A1, A2 | one 10 mm prop spanner | **Accepted** (D-40) |
| CR-C6-06 | A1, A2 | per-type thread engagement | **Accepted** (D-41) |
| CR-C6-07 | D2, F3 | airspeed board on foam tape, no M2 | **Accepted** (D-33, CR-F3-03) |
| CR-C6-08 | D7 | box handles M3 | Forwarded (D-31) |
| CR-C6-09 | D2 | pitot flange ≥ 30 × 30 mm; mast grip | Forwarded; mast bolt now CR-C6-18 |
| CR-C6-10 | E1, D3 | motor screws 0.20 N·m, drilled pattern | Drilled pattern **adopted** by D3 (canted 4.5 mm plate, holes square to it); E1 torque value still to change in `PRP-005` |
| CR-C6-11 | I1 | fastener kit | Superseded by CR-C6-22 |
| CR-C6-12 | D5 | snap finger ≥ 6.0 mm | Forwarded (D-30) |
| CR-C6-13 | D6 | servo frame / horn bond area | Forwarded; area updated by CR-C6-23 |
| CR-C6-14 | H1 | coupons with the first prints | Forwarded; now **nine** tests (`JOINTS.md` test table): add `T-C6-BOARD-CORNER`, `T-C6-CANT-SEAT`, flat-wise pulls in `-BOARD-LAP`, shear pushes in `-XPS-PULL` |
| CR-C6-15 | A4 | merge `joint_stacks.json` | Forwarded; R2 adds `E-AVN-01` gel-pad retention block and `E-PWR-03` PDB stack |

## Answers to requests addressed to C6

| Request | Answer |
|---|---|
| CR-C3-05 (own the pod allowables) | Done: `JOINTS.md` pod-allowables table, `CALC-C6-POD-ALLOW`; four confirmed, two halved → CR-C6-16, -17 |
| CR-C4-22 (collar, brace ends, anchor joint stacks) | `joint_stacks.json` E-FIN-13…16, 37…44, 57…60: collar RF 1.09 at 9.3 N·m + 209 N, brace ends 2.30, anchor 1.32 (same contact area as C4) |
| D-27 (C4/C6 check the 12 % side component) | Mount slip RF 16.6 (torsion) / 48 (axial); motor-screw separation RF 4.12; engagement 3.5 mm on D3's canted plate |
| CR-C1-11 (mount clamp vs prop-nut torque) | Closed at R1: RF 3.26 bearing, 5.94 hoop |
| CR-A4-10 / CR-A4-20 (joint stacks, M2/M3 only) | `joint_stacks.json` (69 edges); M3 only bought |
| CR-D5-04 (board allowable, snap hook) | Board 0.10 MPa shear design; finger ≥ 6.0 mm |
