# C6 change requests

Revision C6-R5b, 2026-11-10 (params A1-R5; C1 claims and `data/envelope.json` of 14:35 read live; C4's frozen R4 set
`team/C4/claims.d3.json` of 11:51; D3-R5b fins params). Numbers from `team/C6/claims.json`
(`python -I redesign/team/C6/joints.py`); report `JOINTS.md`; copy-ready blocks in `joint_stacks.json` (82 edges).

## New in C6-R5

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-36 | D3 (cc C4, A3) | Station collar 13 → 15 mm. **Adopted by D3-R5b; superseded by CR-C6-37** | C1's first D-65 run raised the section torsion to 8.13 N·m: 13 mm read RF 0.9995 | 15 mm RF 1.15 at 8.13 N·m |
| CR-C6-37 | D3 (cc C4, A1, A3) | `fin_detail.station_collar.height_m` **15 → 22 mm** (ring grows down to \|z\| 0.1375; top, ear and brace end unchanged). Do not print collars until this is settled. If `T-C6-LAP-PETG` runs first, the height needed is 19.45 mm × (2.0 MPa / measured allowable) × (C1 torsion / 12.67 N·m), plus 10 % | C1's second D-65 run (14:29, confirmed 14:35) gives the half-fin section torsion **12.67 N·m** limit, ×1.71 on R4. The collar is sized on max(C1, C4) (CR-C4-23); C1 governs. A1: ≈ +4.4 g `EST` on a fins line with 0 g free | needs **19.45 mm** (`CL-C6-COLLAR-L-REQ`); 15 mm RF **0.77**, 16 mm 0.82, **22 mm 1.13** (`CL-C6-COLLAR-RF-PROP`); 12 mm option of D-70 void (0.63) |
| CR-C6-38 | C4 (cc D3, H1, A1) | Re-run `fin_structures_d3.py` / `sim_fin.py` on the D-65 loads (side load 39.3 N limit / 59.0 N ult, C1 claims of 14:35) and publish one new frozen `CL-C4-D3-*` set: strip end force, pin force, collar torsion, and the **coincident** pair force (CR-C6-29 / -34b) and the fillet-intact share (CR-C2-12). D3: **hold the collar, tail and pin drilling** until it lands | The frozen R4 set was solved at `CL-C4-D3-SIDE-LOAD` 22.8 N and 7.37 N·m section torsion; C1 is now 12.62 N·m at the wing plane. Scaled by k = 1.71, the strip joints fail | estimates (`CALC-C6-FIN-SCALE`): strip force ≈ **2 130 N**; anchor RF **0.74** (needs 53 mm of tail); tail net **0.67** (needs ≈ 140 mm²); Ø 2.5 pins at 15 mm **0.93** (max pitch 14.0 mm, so 12 mm would give ≈ 1.17) |
| CR-C6-39 | H1 | `T-C6-STRIP-ANCHOR` frame: build it to **≥ 2 660 N** (1.25 × `CL-C6-STRIP-ANCHOR-F-EST`), e.g. 15:1 with 20 kg (2 940 N); the pass line still comes from `CL-C6-STRIP-ANCHOR-F` once C4 re-runs | The 9:1 frame of CR-C6-33 (1 766 N) covers the R4 force but not the D-65 estimate | `CL-C6-STRIP-ANCHOR-F` 1 243 N (C4 R4); `-F-EST` 2 131 N |
| CR-C6-40 | D1 (cc D3, C2) | Block pockets (D-68): cut the four vertical pocket corners **R 3.0–4.2 mm** to the R 3 block, or pack the corners with the microballoon mix before the block goes in; dry-fit with a 0.5 mm feeler at every corner; beads ≥ 3 mm leg along the inboard and outboard pocket edges, both surfaces; doubler continuous over the beads | A square-cut pocket round an R 3 block leaves a 1.24 mm void on each corner diagonal, where C2's foam peak sits; a pocket radius under R 3 makes the block ride on its corners | `CL-C6-POCKET-SQUARE-GAP` 1.24 mm vs 0.5 mm bond line; `-R-MAX` 4.2 mm; beads 277 mm per block, **1.1 g** for two at 0.45 g/cm³ (`-BEAD-MASS`); wall area × 0.976 (no C6 RF credits it) |
| CR-C6-41 | C1 (cc A1) | Publish the governing case of `CL-C1-FINHALF-T-LIM` (case id and foot side load used) beside the claim, and announce re-runs that move it by more than 5 % | It moved 7.39 → 8.13 → 12.67 N·m in one afternoon; C6, C4 and D3 size the collar, strips, pins and tail on it | — |

## Answers to the R5 action items

| Item | Answer |
|---|---|
| Re-run on C4's frozen R4 set | Done: strip 1 243 N, pin 72.4 N, collar 6.24 N·m. **The set predates D-65** (side load 22.8 N); C1's torsion now governs and is 1.71 × what C4 solved at → CR-C6-38 |
| 13 mm collar (D-70) | 13 mm reads **0.67** on C1's 12.67 N·m (0.9995 on the 8.13 of the first D-65 run). 15 mm (drawn, CR-C6-36) 0.77 → **22 mm, CR-C6-37** |
| 2.5 mm pins (D-70) | Drawn; **RF 1.60** on C4's R4 pin force (bearing 3.45, strip net 2.41); `CL-C6-STRIP-PIN-RF` now reads the drawn pin. Estimate on D-65 loads 0.93 → CR-C6-38 |
| D5's R5 bond | `E-GER-01…04`: 1 350 mm², **85.7 N, RF 1.57** (`CL-C6-FOOT-SHOE-RF` = `CL-D5-BOND-SF`) — unchanged and passing |
| R 3 mm block pocket | New `CALC-C6-BLOCK-POCKET`; `E-FIN-51/52` rewritten; CR-C6-40 to D1 |
| Fillet RF on the joint side (D-68) | `CL-C6-FIN-ROOT-RF` kept, re-titled fail-safe path, verifies `R-STRUCT-MARGIN` only (no longer `R-FIN-TUBE-JOINT`). Reads **0.81** on D-65's 59 N side load; D3's CR-D3-35 (0.185 m zone) supported |
| `E-PWR-03` at 0.08 N·m | Unchanged and open with F1 (CR-C6-26) |

## Issued in C6-R4

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
| CR-C6-26 | F1 | PA66 frame screws 0.08 N·m | Open (R5 action item: stays open with F1) |
| CR-C6-27 | D2 | PDB-plate bosses Ø 7.2 mm; unplug-moment path | Open |
| CR-C6-28 | H1 | strip-anchor pass line from the claim; nylon-torque and insert tests | Pass line done; frame size → CR-C6-33 |
| CR-C6-29 | C4 | coincident strip force on the pair | Open; re-sent in CR-C6-38 |
| CR-C6-30 | I1 | kit R3 | Superseded for the CF rod by CR-C6-35; rest stands |
| CR-C6-31 | D3 | pins Ø 2.5 at 15 mm | **Adopted** (D-70, D3-R5); RF 1.60 on C4 R4; D-65 → CR-C6-38 |
| CR-C6-32 | D3 | collar 13 mm | **Adopted** (D-70), then superseded by CR-C6-36 / -37 |
| CR-C6-33 | H1 | anchor frame ≥ 1 560 N | Adopted (D-70); raised by CR-C6-39 |
| CR-C6-34 | C4 | freeze one R4 set; coincident force | (a) done (11:51 set); (b) open, in CR-C6-38 |
| CR-C6-35 | I1 | Ø 2.5 rod × 2 | Forwarded; one rod covers 60 pins (0.70 m) |
