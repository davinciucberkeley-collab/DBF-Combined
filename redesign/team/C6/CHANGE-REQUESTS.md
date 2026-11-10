# C6 change requests

Revision C6-R4, 2026-11-10 (params A1-R4a; C4 fin claims `team/C4/claims.d3.json` as of 04:28). Numbers from
`team/C6/claims.json` (`python -I redesign/team/C6/joints.py`); report `JOINTS.md`; copy-ready blocks in
`joint_stacks.json` (82 edges).

## New in C6-R4

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-31 | D3 (cc C4, I1, A3) | Edge-strip through-pins `E-FIN-69…80`: **Ø 2 → Ø 2.5 mm pultruded CF rod, keep the drawn 15 mm pitch** (12 per half-fin, 2.5 mm drill, epoxy injected before the pin). Set `edge_strip.pin_d_m` 0.0025 and refresh its note (it still says RF 1.41). If 2.5 mm rod cannot be bought: Ø 2 at **9 mm** (`CL-C6-STRIP-PIN-RF-ALT`). **Supersedes CR-C6-25** (12 mm pitch) | C4's FE pin force has read 64, 92 and 72.7 N in three runs. A 2 mm pin bends past 400 MPa at every one of them, and 12 mm pitch gives only 1.02 at 73 N and 0.80 at 92 N. A 2.5 mm pin has 1.95 × the bending capacity, so the drawn pitch passes the whole spread | `CL-C6-STRIP-PIN-RF` 0.82 → `-RF-PROP` **1.59** (1.25 at 92 N); bearing on the strip 3.44, strip net section at the hole 2.40; Ø 2 max pitch 12.2 mm. Mass ≈ +1.5 g `EST` (48 pins) |
| CR-C6-32 | D3 (cc C4, A3) | Station collar `fin_detail.station_collar.height_m` **12 → 13 mm**. Keep 12 mm only if `T-C6-LAP-PETG` comes in at mean ≥ 4.1 MPa (allowable ≥ 2.05) before the collars are printed | C1's section torsion reads 7.39 … 7.42 N·m between runs, so 12 mm sits on RF 0.9998 … 1.003 (needs 11.96 … 12.00 mm). Zero margin on an unverified bond allowable is not a design | `CL-C6-COLLAR-RF` 1.00 → `-RF-13MM` **1.09**; 16 mm 1.34. ≈ +0.6 g `EST` (4 collars) |
| CR-C6-33 | H1 | `T-C6-STRIP-ANCHOR` lever frame: capacity **≥ 1 560 N** (1.25 × `CL-C6-STRIP-ANCHOR-F` 1 248 N), e.g. 9:1 (coupon 0.10 m, jugs 0.90 m) = 1 766 N with 20 kg. Read the pass line from the claim, not from a number in the plan | The anchor force rose 908 → 1 248 N with C4's FE re-run. The 6:1 frame (1 177 N) cannot reach even the pass line | `CL-C6-STRIP-ANCHOR-F` 1 248 N (`UNVERIFIED`, tracks `CL-C4-D3-STRIP-END-F`) |
| CR-C6-34 | C4 | (a) Freeze one R4 set of `CL-C4-D3-*` and update `CHANGE-REQUESTS.md` CR-C4-23 / `BOOM-STRUCTURES.md` to match. The text says 908 N / 64 N / 4.61 N·m; the claims now say 1 248 N / 72.7 N / 6.26 N·m (1 198 / 92 / 6.03 at 20:44). (b) Re-sends CR-C6-29: publish the **coincident** force on the other strip of the pair at the collar end in the case that gives `STRIP-END-F`, or confirm the pair never loads together | C6 sizes the tail, the pins and H1's frame on these numbers, and two unannounced changes moved them by up to 44 %. With both strips loaded together the tail net section would carry the sum | tail net RF 1.14 (one strip) / 0.57 (both at 1 248 N, bound) |
| CR-C6-35 | I1 | Kit R4: CF rod **Ø 2.5 × 1 000 mm × 2** (one + spare) replaces Ø 2 × 2. Everything else as CR-C6-30 | CR-C6-31 | ≈ $26 `EST` unchanged |

## Answers to requests addressed to C6 (R4 action items)

| Request | Answer |
|---|---|
| CR-C4-23 (re-run on C4's claims) | Re-run on the claims C4 publishes now, which are not the numbers in the CR text. Collar = max(`CL-C1-FINHALF-T-LIM` **7.39**, `CL-C4-D3-COLLAR-T` **6.26** N·m) + `CL-C4-D3-BRACE-F` 163 N as shear: needs 11.96 mm, 12 mm RF 1.003 (0.9998 on C1's 7.42 an hour earlier) → CR-C6-32. Strip tail on `CL-C4-D3-STRIP-END-F` **1 248 N** per face: 39.5 mm two-face embedment RF 1.27 (needs 31.2 mm); tail net 1.14. Pins on `CL-C4-D3-STRIP-PIN-F` **72.7 N**: Ø 2 RF 0.82 → CR-C6-31. Discrepancy → CR-C6-34 |
| CR-D3-17 / CR-D3-25 (R3/R4 geometry) | Re-run on D3-R4: collar 829 mm² at 12 mm; tail 790 mm² two faces; canted 4.5 mm plate, 3.5 mm engagement (`E-FIN-61…64`); strip area 2 239 mm², root areas 5 318 / 5 078 mm². **Root fillet zoning accepted**: 15 mm over the effective root, 13 mm aft of the hinge, 6 mm bead ahead. `joints.py` now reads the drawn leg (`fin_detail.fin.root_fillet.leg_m`) because `ASM-D3-FILLET-LEG` was retired: root RF **1.14**. CR-C6-24 closed. Pin blocks `E-FIN-69…80` issued (they carried the R1 "77 N, RF 1.41" text) |
| CR-F1-20 / CR-A4-44 (power frame; withdraw stacks) | `E-PWR-03` stands: 4 × M3x18 PA66 + 0.5 mm nylon washer, 2 mm deck, 10 mm spacer, M3 × 5.7 brass insert, **5.5 mm** engaged (RF 1.22, ≤ 5.7, tip 1.0 mm clear of the 6.5 mm bore floor), **0.08 N·m** (CR-C6-26). Unplug 39 N tension per screw, RF 1.46; friction 1.24; spacer 7.2; insert 1.74. `E-MEC-03/04` and `E-PWR-05` withdrawn (`joint_stacks.json#withdrawn`) |
| CR-D5-24 (bond block) | `E-GER-01…04` 1 350 mm²; D5's SF moved to **1.57**, design 85.7 N at 0.10 MPa (`CL-C6-FOOT-SHOE-RF` = `CL-D5-BOND-SF`) |
| CR-C6-18 (mast cross-bolt) | `E-POD-06`: M3x16 PA66 + PA66 nut, grip 10.0 mm, 6.0 mm past the grip (≥ 4.0), finger + ¼ turn (≤ 0.08 N·m) |
| D-50 / CR-C6-23 (bond area at VD 27.2) | `CL-C6-LINK-BOND-AREA-MIN` **719 mm²** (89.9 N pushrod design); D6 horn 1 385 mm² passes |
| D-58 (deviations) | Listed in `JOINTS.md`: (a) prop-adapter M3x4 at 2.0 mm, RF 1.70, conditional on `T-E1-MOTOR-RM`; (b) supplied 2-56 clevises and M2 × 6 self-tapping covers in mechanisms |
| CR-H1-12 (strip-anchor force claim) | `CL-C6-STRIP-ANCHOR-F` published, **1 248 N** now; the `T-C6-STRIP-ANCHOR` pass line is written from it on every run. The frame is too small → CR-C6-33 |

## Issued in C6-R3 (status below)

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-25 | D3 (cc C4, I1) | Edge-strip through-pins `E-FIN-21…28` / `69…80`: pitch **15 → 12 mm** (20 per strip pair, 80 pins ≈ 0.93 m of Ø 2 mm rod; ≈ +0.3 g per half-fin `EST`); first pin half a pitch aft of the tail. Also refresh the stale `edge_strip.pin_d_m` note (says RF 1.41) | C4's FE pin force is 64 N per pin at 15 mm (`CL-C4-D3-STRIP-PIN-F`); with the pin reacted at the board mid-plane it bends past the 400 MPa CF allowable. A uniform-bearing model gives ≈ 1.7, but the coupons do not cover pin bending, so C6 sizes to the bound | `CL-C6-STRIP-PIN-RF` 0.92 → `CL-C6-STRIP-PIN-RF-PROP` 1.15 |
| CR-C6-26 | F1 (cc A4, D7) | `E-PWR-03`: torque **0.20 → 0.08 N·m max** on the PA66 M3x18 (1.6 N on a luggage scale 50 mm out on the hex key; with a PH1 pan head: fingertips only, stop when the washer stops turning). Prefer a PA66 **socket-head** M3x18 (same 2.5 mm key, measurable torque). Add to the field card (D7): **thumb on the cradle while pulling the AS150U pack half** | 0.20 N·m gives ≈ 93 MPa von Mises in the nylon shank (preload 333 N + torsion) against 50 MPa; nylon also creeps, so re-snug every 10 flights | `CL-C6-PWR-INSTALL-RF` 0.54 → 1.35; tension RF 1.46, friction 1.24, spacer 7.2, insert 1.74; engagement 5.5 mm (RF 1.22) |
| CR-C6-27 | D2 (cc F1, C3) | PDB-plate bosses in `POD-002`: `boss_d_m` **0.007 → 0.0072** (1.6 mm wall round the 4.0 mm insert bore). Show how the AS150U unplug moment (50 N at 18 mm: 1.94 N·m design) leaves the four bosses: tie them into the tray stops or guides with a rib, or thicken the plate under the frame to 1.6 mm, so ≥ ≈ 62 × 62 mm of floor bond acts flat-wise at 0.05 MPa. `T-C6-INSERT` now pulls inserts from a boss on a bonded 0.8 mm plate and records the plate-peel load | Boss-wall rule; a 0.8 mm plate bonded to paper-faced board peels under a local moment long before the insert pulls | 1.5 mm wall now; required pad ≈ 62 mm square (rigid-pad estimate); in normal use the thumb rule keeps the load off the frame |
| CR-C6-28 | H1 | `T-C6-STRIP-ANCHOR`: pass line **≥ 908 N** on **one** strip of a bonded pair (`CL-C6-STRIP-ANCHOR-F`, published), on the 12 mm collar + 40 mm tail as D3 draws it; record whether the bond or the tail net section fails. New `T-C6-NYLON-TORQUE` (5 PA66 M3x18 to failure; 48 h creep at 0.08 N·m). `T-C6-INSERT` on a boss printed on a 0.8 mm plate bonded to board | Answers CR-H1-12; the lever frame (1 177 N) covers 908 N | 10 C6 tests in `claims.json` |
| CR-C6-29 | C4 | Publish the **coincident** strip force on the other face of the pair at the collar end (the case that gives `CL-C4-D3-STRIP-END-F` 908 N), or confirm the pair is never in tension together | Both strips end in the same two-face tail; C6 checks its net section with one strip's force (`CL-C6-STRIP-TAIL-NET-RF` 1.57 on D3's 95 mm²). If the pair adds, the tail reaches 19 MPa vs 15 MPa | RF 1.57 (one strip) / 0.79 (both at 908 N, bound) |
| CR-C6-30 | I1 | Kit at R3: M3x8 A2 ×20, M3x16 A2 ×6, M3x16 PA66 + PA66 nut ×3 + 3, **M3x18 PA66 (socket head) ×11**, M3 nyloc ×8, M3 washer ×12, M3 × 5.7 insert ×12, **M3 nylon washer 0.5 mm ×6 + 10 mm nylon spacer OD 6 / ID 3.2 ×6**, CF rod Ø 2 × 1 000 mm ×2. **Drop M3x10** (the PCB stack is gone) and the 0.8 mm washers / 2 mm spacers | `JOINTS.md` kit table; supersedes CR-C6-22 | ≈ $26 `EST` |

## Status of earlier requests

| Id | To | Request (short) | Status |
|---|---|---|---|
| CR-C6-01 | D3 | 40 mm two-face collar tail | **Adopted**; RF 1.27 at 1 248 N |
| CR-C6-02 | C4, D3 | strip shear flow in the FE; pins | FE done (C4); pins adopted, size now CR-C6-31 |
| CR-C6-03 | C4, C1, D3 | agree the collar torsion | **Closed** by CR-C4-23 (max of both) |
| CR-C6-04 | E3 | collar temperature vs epoxy Tg | Forwarded (A1) |
| CR-C6-05, -06, -07 | A1, A2, D2, F3 | one prop spanner; per-type engagement; airspeed on tape | Accepted (D-40, D-41, D-33) |
| CR-C6-08 | D7 | box handles M3 | **Confirmed** (CR-D7-10) |
| CR-C6-09 | D2 | pitot flange ≥ 30 × 30 mm | Forwarded |
| CR-C6-10 | E1, D3 | motor screws 0.20 N·m, drilled pattern | **Adopted** (D3, E1 `PRP-005`) |
| CR-C6-12 | D5 | snap finger ≥ 6.0 mm | **Adopted** (6.5 mm) |
| CR-C6-13, -23 | D6 | servo frame / horn bond area | **Closed** at 719 mm² (D-50) |
| CR-C6-14 | H1 | coupons with the first prints | Forwarded; ten tests (CR-C6-28), frame CR-C6-33 |
| CR-C6-15 | A4 | merge `joint_stacks.json` | Forwarded; R3 adds `withdrawn` |
| CR-C6-16 | C3 | pod allowables | **Adopted** (C3 reads C6's nodes) |
| CR-C6-17 | D2, C3 | 6 mm floor-corner fillet | **Adopted** (C3 `CL-C3-FLOOR-GLUE-FILLET`) |
| CR-C6-18 | D2 | PA66 mast bolt | **Adopted** |
| CR-C6-19 | F3, D2 | slack strap over the FC | Adopted (F3: 10 mm strap) |
| CR-C6-20 | C4, A4 | FE NaN stops the build | Forwarded (A1 row CR-C4-23…28) |
| CR-C6-21 | C1 | (a) cant side force in J-MOTOR; (b) VD | (b) closed by D-50; (a) open, C6 carries it locally |
| CR-C6-22 | I1 | kit R2 | Superseded by CR-C6-30 |
| CR-C6-24 | D3 | root fillet leg 15 mm | **Closed**: D3-R4 draws 15 mm, zoned (CR-D3-25 accepted); RF 1.14 |
| CR-C6-25 | D3 | pins at 12 mm pitch | **Superseded** by CR-C6-31 (Ø 2.5 at 15 mm) |
| CR-C6-26 | F1 | PA66 frame screws 0.08 N·m | Open |
| CR-C6-27 | D2 | PDB-plate bosses Ø 7.2 mm; unplug-moment path | Open |
| CR-C6-28 | H1 | strip-anchor pass line from the claim; nylon-torque and insert tests | Pass line done; frame size → CR-C6-33 |
| CR-C6-29 | C4 | coincident strip force on the pair | Open; re-sent as CR-C6-34 (b) |
| CR-C6-30 | I1 | kit R3 | Superseded for the CF rod by CR-C6-35; rest stands |
