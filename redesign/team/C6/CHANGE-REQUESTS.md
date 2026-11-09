# C6 change requests

Raised 2026-11-09 by C6 (joints and fasteners). Numbers from `team/C6/claims.json` (`python -I redesign/team/C6/joints.py`);
report `JOINTS.md`; copy-ready blocks in `joint_stacks.json`.

| Id | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-C6-01 | D3 (cc C4) | Station collar `FIN-008`: lengthen the strip tail 20 → **40 mm** (`fin_detail.station_collar.tail_m` 0.040) and make it a solid PETG tongue between the two edge strips (board notched 40 mm at the LE top corner), so both strip faces bond to PETG | The strip force cannot pass through 200 mm² of one-face bond | design 1 348 N; RF 0.30 now (`CL-C6-STRIP-ANCHOR-RF`), 1.19 with the tail (`-PROP`); need ≥ 33.7 mm (`CL-C6-STRIP-EMBED-REQ`); ≈ +1 g per collar |
| CR-C6-02 | C4, D3 | (a) C4: check the strip-to-paper shear flow in the FE (strips modelled as perfectly bonded). (b) D3: after the strips cure, drill Ø 2.0 mm through strip–board–strip every 15 mm along the top edge (18 per half-fin) and bond Ø 2 mm pultruded CF pins flush. Alternative: a 10 × 5 mm basswood cap replacing the top 10 mm of board (+≈ 5 g per half-fin) | Flange shear flow goes through the paper-to-foam interface | q 5.1 N/mm, 0.51 MPa vs 0.10 MPa, RF 0.20 (`CL-C6-STRIP-FACE-RF`); pins 77 N each, RF 1.41 (`CL-C6-STRIP-PIN-RF`); +≈ 3 g total |
| CR-C6-03 | C4, C1 (cc D3) | Agree the tube torsion the station collar carries: C1 `J-FINHALF` Mz 5.29 N·m limit vs C4's 9.3 N·m. D3: collar height 12 → **16 mm** covers both | Collar bond RF 1.60 (C1) vs 0.91 (C4) | `CL-C6-COLLAR-RF`, `CL-C6-COLLAR-L-REQ` 13.2 mm needed on C4's number |
| CR-C6-04 | E3 (cc G2, D3) | Estimate the station-collar and mount-collar temperature (0.5 mm below the motor base at 66 °C). C6 adds a 4 h / 50 °C post-cure for every bond within 50 mm of a motor; if the collar runs > 45 °C, buy a laminating epoxy with Tg ≥ 70 °C after post-cure | 30 min hobby epoxies have Tg ≈ 50–60 °C | `CL-E3-*` motor base 65.8 °C |
| CR-C6-05 | A1, A2 (cc E1, D7) | Field set-up "no tools" (P9) conflicts with the M6 prop nut (`params.json#transport.field_steps`). Allow one 10 mm prop spanner in the field kit (recommended), or E1 finds a tool-free prop retention | The prop nut is the only field joint needing a tool | 1.5 N·m nut torque (`ASM-C1-PROP-NUT-TORQUE`) |
| CR-C6-06 | A1, A2 | Replace `requirements.thread_engagement_min` (1.0 d) with the per-type minimums: **1.0 d into metal, 1.5 d into a heat-set insert (= `interfaces/SCHEMA.md`), 2.0 d self-tapping into plastic, nyloc fully on + 2 pitches**; `R-JOINT-STACK` text to match | A2 (1.0 d in an insert) and SCHEMA (1.5 d) disagree | `team/C6/params.json#joints.insert_engage_min_d` |
| CR-C6-07 | D2, F3 | Mount the MS5525 airspeed board on foam tape + one tie and drop the 2 M2 bosses from `POD-002` | Removes the only bought M2 size; 6 g part | — |
| CR-C6-08 | D7 | Box handles `E-TRN-13…15`: M3x16 SHCS + M3 × 12 mm fender washers + nyloc instead of M5 (ground item, optional) | One thread, one key for the whole kit | 59 N per bolt (6 kg × 2 g / 2) |
| CR-C6-09 | D2 (cc C3) | Pitot socket `POD-006`: add a ≥ 30 × 30 mm flange bonded to the inside face of the nose wall; check the GPS-mast bolt grip ≤ 10.5 mm (M3x16 + 1 washer + nyloc, ≥ 5.0 mm past the grip) and correct `E-POD-06` engagement to the nyloc rule | A 14 mm hole edge in foam board cannot bear the boom moment; the nyloc rule is 2 pitches past a 4 mm nut | 0.8 N·m handling; `joint_stacks.json#E-POD-06` |
| CR-C6-10 | E1, D3 | Motor screws `PRP-005` / `E-FIN-61…64`: **0.20 N·m** (not 0.5), Loctite 243 on the tip only, no washer; drill the plate to the measured pattern (no radial slots: a 3.4 mm slot under a 5.5 mm head leaves ¼ of the bearing area). Pinch bolts `E-FIN-05…08`: engagement 5.5 mm past the grip, minimum 5.0 (not 4.0 / 3.0) | Head bearing on the printed plate at 66 °C | 57 MPa, RF 0.53 at 0.5 N·m; 22.7 MPa, RF 1.32 at 0.20 N·m (`CL-C6-MOTOR-HEAD-RF`); preload 333 N still 4.8 × the screw tension |
| CR-C6-11 | I1 | Fastener kit: M3x8 ×20, M3x10 ×10, M3x16 ×8 (SHCS A2-70, ISO 4762); M3 nyloc ×10; M3 washer ×15; M3 × 5.7 brass heat-set insert ×12; M3 nylon washers + FC grommets ×8; CF rod Ø 2 × 1 000 mm ×1; 30 min laminating epoxy, colloidal silica, glass microballoons; Loctite 243; paint pen | `JOINTS.md` kit table | ≈ $25 `EST` |
| CR-C6-12 | D5 | Snap hooks on `GER-002`: free finger length ≥ **6.0 mm** (two 0.8 mm slots in the skirt) for 0.6 mm hook at 0.8 mm wall | Strain ≤ 2 % for repeated swaps | `CL-C6-SNAP-L-MIN`; CR-D5-04 answered: board allowable 0.10 MPa (0.5 × your 0.20), shoe RF 1.35 |
| CR-C6-13 | D6 | Servo frames `MEC-008` and horns `MEC-004`: bonded area into XPS ≥ **720 mm²** each; horn as a through-panel horn with a backplate; servo screws into printed or ply bosses, never foam; silicone keeper on every clevis | 90 N pushrod design force at VD 27.2 m/s | `CL-C6-LINK-BOND-AREA-MIN` |
| CR-C6-14 | H1 | Run the C6 coupons with the first PETG prints (before the fin build): `T-C6-LAP-PETG`, `-BOARD-LAP`, `-XPS-PULL`, `-INSERT`, `-HEAD-CREEP`, `-STRIP-ANCHOR`, `-PROPNUT` | Every C6 claim is `UNVERIFIED` until then | procedures in `claims.json` |
| CR-C6-15 | A4 | Merge `joint_stacks.json` blocks as the owners adopt them; add `CT-M3-SHCS-INSERT` stacks to `E-AVN-01` / `E-PWR-03` and change `E-AVN-04` to `CT-TAPE-FOAM` if CR-C6-07 is accepted | P24 joint stacks | 67 edges |

## Answers to requests addressed to C6

| Request | Answer |
|---|---|
| CR-C1-11 (mount clamp vs prop-nut torque 3.2 N·m) | Closed: collar bearing 6.1 MPa, RF 3.26; tube hoop RF 5.94 (`CL-C6-MOUNT-ROCK-RF`, `-HOOP-RF`) |
| CR-A4-10 / CR-A4-20 (joint stacks, M2/M3 only) | `joint_stacks.json`; M3 only bought |
| CR-C4-10 (collar, strips, brace ends, block bonds; coupons) | Block bonds RF 5.7–6.3; brace RF 1.8–2.9; collar and strips fail as drawn → CR-C6-01…03; coupons CR-C6-14 |
| CR-D5-04 (board allowable, snap hook) | CR-C6-12 |
