# C6 change requests

Revision C6-R3, 2026-11-09 (params A1-R4). Numbers from `team/C6/claims.json`
(`python -I redesign/team/C6/joints.py`); report `JOINTS.md`; copy-ready blocks in `joint_stacks.json`.

## New in C6-R3

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-25 | D3 (cc C4, I1) | Edge-strip through-pins `E-FIN-21…28` / `69…80`: pitch **15 → 12 mm** (20 per strip pair, 80 pins ≈ 0.93 m of Ø 2 mm rod; ≈ +0.3 g per half-fin `EST`); first pin half a pitch aft of the tail. Also refresh the stale `edge_strip.pin_d_m` note (says RF 1.41) | C4's FE pin force is 64 N per pin at 15 mm (`CL-C4-D3-STRIP-PIN-F`); with the pin reacted at the board mid-plane it bends past the 400 MPa CF allowable. A uniform-bearing model gives ≈ 1.7, but the coupons do not cover pin bending, so C6 sizes to the bound | `CL-C6-STRIP-PIN-RF` 0.92 → `CL-C6-STRIP-PIN-RF-PROP` 1.15 |
| CR-C6-26 | F1 (cc A4, D7) | `E-PWR-03`: torque **0.20 → 0.08 N·m max** on the PA66 M3x18 (1.6 N on a luggage scale 50 mm out on the hex key; with a PH1 pan head: fingertips only, stop when the washer stops turning). Prefer a PA66 **socket-head** M3x18 (same 2.5 mm key, measurable torque). Add to the field card (D7): **thumb on the cradle while pulling the AS150U pack half** | 0.20 N·m gives ≈ 93 MPa von Mises in the nylon shank (preload 333 N + torsion) against 50 MPa; nylon also creeps, so re-snug every 10 flights | `CL-C6-PWR-INSTALL-RF` 0.54 → 1.35; tension RF 1.46, friction 1.24, spacer 7.2, insert 1.74; engagement 5.5 mm (RF 1.22) |
| CR-C6-27 | D2 (cc F1, C3) | PDB-plate bosses in `POD-002`: `boss_d_m` **0.007 → 0.0072** (1.6 mm wall round the 4.0 mm insert bore). Show how the AS150U unplug moment (50 N at 18 mm: 1.94 N·m design) leaves the four bosses: tie them into the tray stops or guides with a rib, or thicken the plate under the frame to 1.6 mm, so ≥ ≈ 62 × 62 mm of floor bond acts flat-wise at 0.05 MPa. `T-C6-INSERT` now pulls inserts from a boss on a bonded 0.8 mm plate and records the plate-peel load | Boss-wall rule; a 0.8 mm plate bonded to paper-faced board peels under a local moment long before the insert pulls | 1.5 mm wall now; required pad ≈ 62 mm square (rigid-pad estimate); in normal use the thumb rule keeps the load off the frame |
| CR-C6-28 | H1 | `T-C6-STRIP-ANCHOR`: pass line **≥ 908 N** on **one** strip of a bonded pair (`CL-C6-STRIP-ANCHOR-F`, published), on the 12 mm collar + 40 mm tail as D3 draws it; record whether the bond or the tail net section fails. New `T-C6-NYLON-TORQUE` (5 PA66 M3x18 to failure; 48 h creep at 0.08 N·m). `T-C6-INSERT` on a boss printed on a 0.8 mm plate bonded to board | Answers CR-H1-12; the lever frame (1 177 N) covers 908 N | 10 C6 tests in `claims.json` |
| CR-C6-29 | C4 | Publish the **coincident** strip force on the other face of the pair at the collar end (the case that gives `CL-C4-D3-STRIP-END-F` 908 N), or confirm the pair is never in tension together | Both strips end in the same two-face tail; C6 checks its net section with one strip's force (`CL-C6-STRIP-TAIL-NET-RF` 1.57 on D3's 95 mm²). If the pair adds, the tail reaches 19 MPa vs 15 MPa | RF 1.57 (one strip) / 0.79 (both at 908 N, bound) |
| CR-C6-30 | I1 | Kit at R3: M3x8 A2 ×20, M3x16 A2 ×6, M3x16 PA66 + PA66 nut ×3 + 3, **M3x18 PA66 (socket head) ×11**, M3 nyloc ×8, M3 washer ×12, M3 × 5.7 insert ×12, **M3 nylon washer 0.5 mm ×6 + 10 mm nylon spacer OD 6 / ID 3.2 ×6**, CF rod Ø 2 × 1 000 mm ×2. **Drop M3x10** (the PCB stack is gone) and the 0.8 mm washers / 2 mm spacers | `JOINTS.md` kit table; supersedes CR-C6-22 | ≈ $26 `EST` |

## Answers to requests addressed to C6 (R3)

| Request | Answer |
|---|---|
| CR-C4-23 (re-run on C4's R3 claims) | Done. Collar = max(`CL-C1-FINHALF-T-LIM` 7.40, `CL-C4-D3-COLLAR-T` 4.61 N·m) + `CL-C4-D3-BRACE-F` 164 N as shear: needs 11.98 mm; 12 mm RF 1.00, 16 mm RF 1.34. Strip tail on `CL-C4-D3-STRIP-END-F` 908 N: RF 1.74. Pins on `CL-C4-D3-STRIP-PIN-F` 64 N: RF 0.92 → CR-C6-25. `ASM-C6-C4-COLLAR-T` (9.3 N·m) and `ASM-C6-FINHALF-MZ-ULT` retired. Closes CR-C6-02a and CR-C6-03 |
| CR-D3-17 (re-run on R3 geometry) | Done on R4 (collar 12 mm). Collar bond 829 mm² (RF 1.00); tail 790 mm² two faces (39.5 mm, RF 1.74, needs 22.7 mm); tail net section 9.6 MPa on your 95 mm² (RF 1.57, CR-C6-29); canted 4.5 mm plate confirmed (3.5 mm engagement, `E-FIN-61…64`); pins → CR-C6-25. Blocks re-issued |
| CR-F1-20 / CR-A4-44 (power frame; withdraw stacks) | `E-PWR-03` issued: 4 × M3x18 PA66 + 0.5 mm nylon washer, 2 mm deck, 10 mm spacer, M3 × 5.7 brass insert, 5.5 mm engaged (≤ 5.7, tip 1.0 mm clear of the 6.5 mm bore floor), **0.08 N·m** (not 0.20, CR-C6-26). Your 50 N unplug: 18 N tension per screw → 39 N design, RF 1.46; shear checked on friction and spacer bending. `E-MEC-03/04` and `E-PWR-05` withdrawn (`joint_stacks.json#withdrawn`) |
| CR-D5-24 (bond block) | Adopted: `E-GER-01…04` 1 350 mm², 87.4 N design, RF 1.54 at 0.10 MPa (`CL-C6-FOOT-SHOE-RF` now reads `CL-D5-BOND-SF` directly; the R2 double knock-down is removed). Rim lip SF 1.18 on your fixed-ended model: accepted as thin; `T-D5` drop covers it |
| CR-C6-18 (mast cross-bolt) | D2 adopted: M3x16 PA66 + PA66 nut, grip 10.0 mm, 6.0 mm past the grip; block updated |
| D-50 / CR-C6-23 (bond area at VD 27.2) | `CALC-C6-LINKAGE` reads `requirements.vd_ms` 27.2: **719 mm²**. D6's horn 1 385 mm² passes |
| D-58 (deviations) | Listed in `JOINTS.md` (prop-adapter 2.0 mm; 2-56 / M2 in mechanisms); `E-PRP-01…04` block carries the 2.0 mm minimum with its condition |
| CR-H1-12 (strip-anchor force claim) | `CL-C6-STRIP-ANCHOR-F` 908 N published; test text fixed (CR-C6-28) |
| CR-D7-10 (handle stack) | Confirmed: M3x16 + fender washer + nyloc on the 3 mm ply strip. Minimum engagement is nyloc + 2 pitches = 5.0 mm (not 3.0): grip ≤ 11.0 mm |
| CR-E1-33 | Listed as deviation D-58 (a) |
| CR-D6-11 | (a) stack withdrawn, `E-MEC-35/36` M2 × 6 at 5.2 mm ≥ 4.0 accepted; (b) D-58 (b); (c) horn 1 385 ≥ 719 mm² |
| CR-C3-11 | Re-run: `CALC-C6-POD-ALLOW` reads C3's current values (pod bond RF 1.15 / 1.29, tray 2.59, hatch 1.18) |

## Status of earlier requests

| Id | To | Request (short) | Status |
|---|---|---|---|
| CR-C6-01 | D3 | 40 mm two-face collar tail | **Adopted**; RF 1.74 |
| CR-C6-02 | C4, D3 | strip shear flow in the FE; pins | FE done (C4); pins adopted, pitch now CR-C6-25 |
| CR-C6-03 | C4, C1, D3 | agree the collar torsion | **Closed** by CR-C4-23 (max of both) |
| CR-C6-04 | E3 | collar temperature vs epoxy Tg | Forwarded (A1) |
| CR-C6-05, -06, -07 | A1, A2, D2, F3 | one prop spanner; per-type engagement; airspeed on tape | Accepted (D-40, D-41, D-33) |
| CR-C6-08 | D7 | box handles M3 | **Confirmed** (CR-D7-10) |
| CR-C6-09 | D2 | pitot flange ≥ 30 × 30 mm | Forwarded |
| CR-C6-10 | E1, D3 | motor screws 0.20 N·m, drilled pattern | **Adopted** (D3, E1 `PRP-005`) |
| CR-C6-12 | D5 | snap finger ≥ 6.0 mm | **Adopted** (6.5 mm) |
| CR-C6-13, -23 | D6 | servo frame / horn bond area | **Closed** at 719 mm² (D-50) |
| CR-C6-14 | H1 | coupons with the first prints | Forwarded; now ten tests (CR-C6-28) |
| CR-C6-15 | A4 | merge `joint_stacks.json` | Forwarded; R3 adds `withdrawn` |
| CR-C6-16 | C3 | pod allowables | **Adopted** (C3 reads C6's nodes) |
| CR-C6-17 | D2, C3 | 6 mm floor-corner fillet | **Adopted** (C3 `CL-C3-FLOOR-GLUE-FILLET`) |
| CR-C6-18 | D2 | PA66 mast bolt | **Adopted** |
| CR-C6-19 | F3, D2 | slack strap over the FC | Adopted (F3: 10 mm strap) |
| CR-C6-20 | C4, A4 | FE NaN stops the build | Forwarded (A1 row CR-C4-23…28) |
| CR-C6-21 | C1 | (a) cant side force in J-MOTOR; (b) VD | (b) closed by D-50; (a) open, C6 carries it locally |
| CR-C6-22 | I1 | kit R2 | Superseded by CR-C6-30 |
| CR-C6-24 | D3 | root fillet leg 15 mm | **Adopted in D-48**; D3 still draws 12 mm (`ASM-D3-FILLET-LEG`): RF 0.87 → 1.24 once drawn |
