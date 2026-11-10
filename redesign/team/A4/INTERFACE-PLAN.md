# Interface plan — K09-L quad tailsitter

Status: `PROPOSED`, plan revision **A4-R4** on design frame A1-R3 (A4, 2026-11-09, integration check). Every part id and every joint
the aircraft needs, who declares it, who acknowledges it, who designs and sizes it, and the data it must carry.
Owners copy their rows into `subsystems/<key>/interfaces.json` (schema `redesign/interfaces/SCHEMA.md`); A4 merges
with `redesign/interfaces/merge_check.py` and compares against this plan with `interface_plan.py --compare`.
Source of the tables below: `redesign/team/A4/interface_plan.py` plus the frozen declarations in
`baseline-R4.json` (R3 freeze kept in `baseline-R3.json`) (machine copy of the whole plan: `interface_plan.json`).

## What changed in A4-R4 (integration check, 2026-11-09)

All ten subsystems with parts have now declared; `ground` (F5) has not. Results: `INTEGRATION-CHECK.md`.

| Change | Why | Ids |
|---|---|---|
| Baseline R4: wing, power, avionics, harness, mechanisms added to the frozen declarations (10 subsystems, 160 parts, 238 declared edges incl. 24 parked) | the declarations replace the R2/R3 plan rows; the plan keeps only what no owner has declared yet | `baseline-R4.json`, `BASELINED` |
| Parked edges read from F2's `edges-pending.json` as well as `edges_pending` | 21 harness wires were counted missing although declared | `pending_edges()` |
| Field disconnect read from `wire.disconnect` of a declared edge | the pack plug `E-HRN-10` is F2's now | `CL-A4-FIELD-DISCONNECTS` |
| D6-R1 accepted: rod bonded in the horns, not the panels; torque tubes `MEC-009-<side><I/O>`, hinge tape `MEC-010`, outboard horns `MEC-006`; servo held by ear slots (slid) | declared with reasons in the edge notes | `E-MEC-19…36`; `E-MEC-13…16` retired |
| F1 PWR-R1 accepted: power frame `PWR-006` bolted to the pod, AS150U half bonded in its cradle, bus board taped; fuse `PWR-007` and ESC caps `PWR-008-<st>` are parts | declared with reasons | `E-PWR-01…07`, `E-PWR-11…14` |
| F2 R1 accepted: `E-HRN-03/05` are the block ties (R/L), `E-HRN-06…09` collar ties, motor phases soldered (`CT-SOLDER-PHASE`) | declared with reasons | `E-HRN-03…09`, `E-HRN-17…20` |
| A4 additions from CR-F1-18 (F2 declares them): `E-HRN-21` ends at the fuse; `E-HRN-33` fuse → UBEC; `E-HRN-34…37` ESC → cap leads | without them the fuse and the four caps have no wire (`unconnected` in merge_check) | `OVERRIDE`, `E-HRN-33…37` |
| Loose kit items (`"flight": false` spares and tools, `GER-005…013`) need no joint | they are not aircraft parts | `check_plan()` |
| `integration_check.py`: one command runs merge_check (real and after-re-run), `fusion/check.py`, A3 roll-up and `--compare` | repeatable gate check | `INTEGRATION-CHECK.md` |

## What changed in A4-R3 (CR-A1-38)

| Change | Why | Ids |
|---|---|---|
| Shared tooling in `redesign/interfaces/` done (D-46, CR-A4-15a): 22 types added to the library; `merge_check.py` exempts harness wires from `owner`, skips `"structural": false` types in the floating check (parts flagged `"carried"` exempt), follows power wires `part_a` → `part_b`, accepts method `radio`; SCHEMA gains `stowed`, `carried`, `structural`, `edges_pending`, `radio`, the `C` and `I/O` suffixes | `merge_check.py --strict` could not pass at a gate (23 `owner` warnings); load and power paths were only checked on the plan | `connection_types.json`, `merge_check.py`, `SCHEMA.md`; `test_merge_check_d46.py` 11/11 |
| Declared subsystems frozen as **baseline R3**: fins (D3, 42 parts, `E-FIN-01…80` incl. 12 pending), landing (D5, 18 parts, `E-GER-01…22`), pod (D2, 8 parts, `E-POD-01…11`), propulsion (E1, 16 parts, `E-PRP-01…08`), transport (D7, 13 parts, `E-TRN-01…16`) | the declarations replace the R2 plan rows; later changes show in `--compare` until A4 re-baselines | `baseline-R3.json`, `--rebaseline` |
| R2 plan numbers for `E-FIN-*` and `E-TRN-08…12` superseded by D3's and D7's numbering | never declared, so no published graph breaks; the declarer's numbering is the CAD's | table below |
| Thermal edges (E3, CR-E3-11) | conduction paths E3's temperatures rely on | `E-FIN-81…84` motor → mount, `E-FIN-85…88` ESC → pad, `E-POD-12` pack → tray, `E-AVN-10` FC → plate |
| Stowed transport edges (CR-A5-10, CR-D7-09) | props and pitot boom ride in the tray; the part stays at its flight station in CAD | `E-TRN-17…20` props, `E-TRN-21` boom, `"stowed": true` |
| Power (F1, D-32, CR-F1-06) | AS150U main disconnect; UBEC fitted; 5 A fuse in its feed; 8 AWG main run, 16 AWG ESC leads | `E-HRN-10` → `CT-AS150U` (OI-09 closed); `E-HRN-21` fuse; `PWR-003` = CoreWing power board |
| Avionics (F3, CR-F3-08) and RC link (F5, CR-F5-10) | gel-pad FC, tape-mounted airspeed, real I2C/UART map; telemetry through ELRS | `AVN-006`, `AVN-007`; `E-AVN-01` → `CT-GEL-PAD`, `E-AVN-04` → `CT-TAPE-FOAM`; signals on `E-HRN-30…32` (OI-08 closed); subsystem `ground`, `GND-001`, radio link `E-AVN-09` (OI-10 answered) |
| Wing additions for the R3 fins | spar plugs under the blocks and at the brace anchors (C2) | `WNG-004-L/R`, `WNG-005-L/R`, `E-WNG-08…11`; OI-13 |
| Main disconnect mount | the R2 plan held `PWR-002` only by a cable tie; the new load-path rule flags it | `E-PWR-01` → `CT-CONN-PARK` |
| C6 joint stacks merged into `--compare` (CR-C6-15) | each owner copies C6's block; `--compare` lists what is not copied and where a declaration differs from C6 | column *C6* in the register |
| Part-id rule widened: side family `L R C`, face letter `I`/`O` | `FIN-011-URO/URI` (two identical strips per station), `TRN-007-C` (centre handle) | `id_rule()`, `SCHEMA.md` |

R2 → R3 renumbering of the fins (the R2 numbers were plan-only):

| Joint | R2 plan | R3 (D3) |
|---|---|---|
| half-fin root ↔ core | `E-FIN-01/02/33/34` | `E-FIN-53…56` (pending until `WNG-001` exists) |
| block ↔ tube · spar · core | `E-FIN-07…12` | `E-FIN-01/02` · `E-FIN-49/50` · `E-FIN-51/52` |
| clip sets `FIN-005-*` | `E-FIN-03…06`, `35…38` | retired: station collars `FIN-008` (`E-FIN-13…20`) and edge strips `FIN-011` (`E-FIN-21…36`) |
| motor mount ↔ tube (slip clamp, D-23) | `E-FIN-13…16` | `E-FIN-05…08` |
| motor ↔ mount (screws) | `E-FIN-17…20` | `E-FIN-61…64` |
| ESC pad ↔ half-fin · ESC ↔ pad | `E-FIN-21…24` · `25…28` | `E-FIN-45…48` · `E-FIN-65…68` (strap, not tape) |
| motor ↔ mount (thermal) | `E-FIN-29…32` | `E-FIN-81…84` (A4-R3 addition) |
| new in R3 | — | tube plugs `E-FIN-03/04`, braces and anchors `E-FIN-37…44`, `57…60`, pin sets `E-FIN-69…80` |

## Rules

| Rule | Value | Source |
|---|---|---|
| Frame | metres; origin wing root LE on the chord line; x aft, y right, z up in cruise; hover: +x points at the ground | `params.json#frame`, `fusion/DATUMS.md` |
| Part ids | `<PREFIX>-NNN`; a multi-instance part has one node per instance `<PREFIX>-NNN-<UR\|UL\|LR\|LL\|L\|R\|C>[I\|O]`, one suffix family (station or side) per part number; `I`/`O` only for the same part twice at one station; two different parts on one side get two numbers; `NNN` 001–899, `9xx` reserved for `fusion/skeleton/` | README, CR-A3-09, CR-A5-04, `id_rule()` |
| Mass | `parts.csv mass_g` is per unit (line = qty × `mass_g`); each instance node carries that unit mass and its own `cg_xyz_m`; qty = number of nodes | README, CR-A3-09 |
| Edge ids | `E-<owner prefix>-NN`; once declared an id is fixed; a joint that survives a layout change keeps its id, new joints take the next free number, retired ids are never reused | this plan |
| Baseline | a declared subsystem is planned by its declaration (`baseline-R3.json`); A4 reviews each deviation `--compare` reports and either asks the owner (CR) or re-baselines | this plan |
| Pending edges | an edge to a part nobody has declared yet goes in the owner's `edges_pending` with `waits_for`; it counts as declared-pending, not missing | `SCHEMA.md` (D3 practice) |
| Who declares | the owner in the register; the owner holds one side of its edge, except `harness`, which declares every wire; `power` owns the boxes; the elevon hinge is a `wing` edge (D6 designs) | CHANGE-LOG D-20, README joint table |
| Who acknowledges | every other subsystem that holds a side lists the edge id under `acknowledges` | `SCHEMA.md` |
| Electrical direction | `part_a` is the supply side, `part_b` the load; signal-only leads carry `"signal_only": true`; a radio link (`method: radio`) carries no power | D-20, D-46, `SCHEMA.md` |
| Load path | ties, wire channels, labels and pitot tubing (`"structural": false`) locate a part but never hold it; only a part flagged `"carried": true` (harness bundles, the label) may hang on them alone | D-46, `merge_check.py`, `load_path()` |
| Wires | an electrical edge runs end part to end part and *is* the installation (`wire` block + `ctx.wire` route); harness mass sits in three lumped bundle parts (`HRN-001`, `HRN-002-L/R`) | `ADVISOR-XV24-LESSONS.md` lesson 3 |
| Field disconnects | exactly one electrical: the pack plug `E-HRN-10` (AS150U). Field joints (made at every set-up, `field_joint`): 4 prop nuts `E-PRP-05…08` (one 10 mm spanner, D-40), pitot boom `E-AVN-05`, pack strap `E-POD-05` | `params.json#electrical.field_disconnects`, `#transport.field_steps` |
| Transport | box parts are `"flight": false`; cradle and pillar edges are touch-checked in the aircraft frame; props and boom in the tray are `"stowed": true` | D-31, CR-A5-10 |
| Thermal | every heat source E3 sizes has a `thermal` edge to the part that carries it, insulating paths included | CR-E3-11 |
| Moving joints | no wire crosses a moving joint: both servos sit in the fixed core, so no `slack_mm` is needed | this plan |
| Deviations | an owner may change a joint type or split a part; state why in the edge `notes`; `--compare` lists it and A4 updates the plan | — |
| Status | parts and edges start `PROPOSED`; `MODELLED` in Fusion, `CHECKED` by `check.py`/calc, `VERIFIED` on the bench | `BRIEF.md` |

## Data each interface must carry

Schema blocks are checked by `merge_check.py` (ERROR when missing). A4 blocks are optional fields in the same edge
object, checked by `interface_plan.py --compare` (reported as owed until filled). Numbers carry units; unknown is `—`.
C6 writes the fastened, clamped and bonded blocks in `team/C6/joint_stacks.json`; the owner copies them.

| Method | Block | Fields | Checked by |
|---|---|---|---|
| fastened | `joint_stack` | fastener, count, grade, hole, insert, engagement_mm, min_engagement_mm, washer_nut, torque, tool, access, install_order, removal_order (+ `max_engagement_mm` where a screw can reach windings or a servo case); minimum per D-41: 1.0 d metal, 1.5 d insert, 2.0 d plastic | merge_check (schema) · `--compare` vs C6 · C6 sizes |
| clamped | `joint_stack` + `clamp` | stack for the closing screws; clamp {bore_mm, part_od_mm, slip_load_n, sized_by} | `--compare` · C4/C6 |
| bonded | `bond` | adhesive, area_mm2, prep, cure, load_n, load_case, sized_by | `--compare` · C2/C3/C4/C6 |
| taped · strapped · slid · press_fit | `retention` | item, count, load_n, inspection | `--compare` |
| hinged | `motion` + `clearance_mm` | axis, range_deg; clearance at both stops; hinge_moment_nmm | merge_check (motion) · `--compare` · B2/D6 |
| connector · soldered | `wire` + `current_a` or `signal` | gauge_awg, connector, route_id, support_points, bend_radius_mm, strain_relief, disconnect; power: current_a {cont, peak}; signal: {fc_port, protocol, i2c_addr} | merge_check (wire) · `--compare` · F1/F2/F3 |
| radio | `signal` | protocol, band, tx_power_mw (no wire block) | `--compare` · F5 |
| conductive (thermal) | `thermal` | heat_w, t_max_c, t_ambient_c, path, sized_by (+ t_design_c, claim id) | `--compare` · E3 |
| any field joint | `field_joint: true` | marks a joint made at every field set-up (H2 times them) | `interface_plan.py`, `--compare` |
| transport | `stowed: true` | a flight part stored in the box | `fusion/check.py`, `--compare` |

<!-- BEGIN GENERATED REGISTER (interface_plan.py) -->

Generated by `python -I redesign/team/A4/interface_plan.py` from the plan in that script and `baseline-R4.json` (revision A4-R4). Do not edit by hand.

| Parts (flight) | Interfaces | Cross-subsystem | Declared (pending) | Mech · elec · kin · thermal | Connected (load path) | Powered (power wires) | Field disconnects (field joints) | Stowed | Id-rule breaches | Plan errors | Schema blocks owed | Masses owed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 160 (139) | 251 | 113 | 238 (24) | 200 · 29 · 12 · 10 | 100 % | 100 % | 1 (7) | 5 | 0 | 0 | 57 | 139 |

## N² matrix

Interfaces between each pair of subsystems (diagonal: internal joints). Read a row: who this subsystem must agree with. Wires count under the two subsystems they join; harness (`HRN`) declares all 28 of them (D-20); the radio link `E-AVN-09` is an avionics edge.

| | WNG | FIN | POD | GER | PRP | PWR | AVN | HRN | MEC | TRN | GND |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **WNG** | 11 | 12 | 2 | 2 | · | · | · | 2 | 14 | 4 | · |
| **FIN** | 12 | 60 | · | 4 | 16 | 4 | · | 6 | · | · | · |
| **POD** | 2 | · | 8 | · | · | 5 | 7 | 1 | · | · | · |
| **GER** | 2 | 4 | · | 16 | · | · | · | · | · | · | · |
| **PRP** | · | 16 | · | · | 12 | 8 | 4 | · | · | 4 | · |
| **PWR** | · | 4 | 5 | · | 8 | 8 | 2 | · | · | · | · |
| **AVN** | · | · | 7 | · | 4 | 2 | 5 | · | 2 | 1 | 1 |
| **HRN** | 2 | 6 | 1 | · | · | · | · | · | · | · | · |
| **MEC** | 14 | · | · | · | · | · | 2 | · | 18 | · | · |
| **TRN** | 4 | · | · | · | 4 | · | 1 | · | · | 12 | · |
| **GND** | · | · | · | · | · | · | 1 | · | · | · | · |

## Part ids reserved

One node per physical instance, id `<PREFIX>-NNN-<UR|UL|LR|LL|L|R|C>[I|O]`; all instances of a part are one `parts.csv` line with `mass_g` per unit (CR-A3-09). Stations `UR UL LR LL` = upper/lower, right/left (`params.json#propulsion.stations.ids`); a half-fin takes the station it carries; `C` = centre; `I`/`O` = inboard/outboard face of the same part at one station (A4-R3). `NNN` 001–899; `9xx` is reserved for `fusion/skeleton/` (CR-A5-04). *Declared* = taken from the owner's `interfaces.json` into `baseline-R4.json`.

| Subsystem | Designer | Prefix | Parts | Declared | Ids |
|---|---|---|---|---|---|
| `wing` | D1 | `WNG` | 12 | 12 | `WNG-001` `WNG-002` `WNG-003` `WNG-004-R` `WNG-004-L` `WNG-005-R` `WNG-005-L` `WNG-011-R` `WNG-011-L` `WNG-012-R` `WNG-012-L` `WNG-020` |
| `fins` | D3 | `FIN` | 42 | 42 | `FIN-001-UR` `FIN-001-UL` `FIN-001-LR` `FIN-001-LL` `FIN-002-R` `FIN-002-L` `FIN-003-UR` `FIN-003-UL` `FIN-003-LR` `FIN-003-LL` `FIN-004-R` `FIN-004-L` `FIN-006-R` `FIN-006-L` `FIN-007-UR` `FIN-007-UL` `FIN-007-LR` `FIN-007-LL` `FIN-008-UR` `FIN-008-UL` `FIN-008-LR` `FIN-008-LL` `FIN-009-UR` `FIN-009-UL` `FIN-009-LR` `FIN-009-LL` `FIN-010-UR` `FIN-010-UL` `FIN-010-LR` `FIN-010-LL` `FIN-011-URO` `FIN-011-URI` `FIN-011-ULO` `FIN-011-ULI` `FIN-011-LRO` `FIN-011-LRI` `FIN-011-LLO` `FIN-011-LLI` `FIN-012-UR` `FIN-012-UL` `FIN-012-LR` `FIN-012-LL` |
| `pod` | D2 | `POD` | 8 | 8 | `POD-001` `POD-002` `POD-003` `POD-004` `POD-005` `POD-006` `POD-007` `POD-008` |
| `landing` | D5 | `GER` | 25 | 25 | `GER-001-UR` `GER-001-UL` `GER-001-LR` `GER-001-LL` `GER-002-UR` `GER-002-UL` `GER-002-LR` `GER-002-LL` `GER-003-UR` `GER-003-UL` `GER-004-UR` `GER-004-UL` `GER-004-LR` `GER-004-LL` `GER-007-R` `GER-007-L` `GER-008-LR` `GER-008-LL` `GER-005` `GER-009` `GER-010` `GER-011` `GER-012` `GER-006` `GER-013` |
| `propulsion` | E1 | `PRP` | 16 | 16 | `PRP-001-UR` `PRP-002-UR` `PRP-003-UR` `PRP-004-UR` `PRP-001-UL` `PRP-002-UL` `PRP-003-UL` `PRP-004-UL` `PRP-001-LR` `PRP-002-LR` `PRP-003-LR` `PRP-004-LR` `PRP-001-LL` `PRP-002-LL` `PRP-003-LL` `PRP-004-LL` |
| `power` | F1 | `PWR` | 11 | 11 | `PWR-001` `PWR-002` `PWR-003` `PWR-004` `PWR-005` `PWR-006` `PWR-007` `PWR-008-UR` `PWR-008-UL` `PWR-008-LR` `PWR-008-LL` |
| `avionics` | F3 | `AVN` | 7 | 7 | `AVN-001` `AVN-002` `AVN-003` `AVN-004` `AVN-005` `AVN-006` `AVN-007` |
| `harness` | F2 | `HRN` | 3 | 3 | `HRN-001` `HRN-002-R` `HRN-002-L` |
| `mechanisms` | D6 | `MEC` | 22 | 22 | `MEC-001-R` `MEC-001-L` `MEC-002-R` `MEC-002-L` `MEC-003-R` `MEC-003-L` `MEC-004-R` `MEC-004-L` `MEC-005-R` `MEC-005-L` `MEC-006-R` `MEC-006-L` `MEC-007-R` `MEC-007-L` `MEC-008-R` `MEC-008-L` `MEC-009-RI` `MEC-009-LI` `MEC-009-RO` `MEC-009-LO` `MEC-010-R` `MEC-010-L` |
| `transport` | D7 | `TRN` | 13 | 13 | `TRN-001` `TRN-005` `TRN-002-L` `TRN-002-R` `TRN-003` `TRN-004-L` `TRN-004-R` `TRN-006-L` `TRN-006-R` `TRN-007-C` `TRN-007-L` `TRN-007-R` `TRN-008` |
| `ground` | F5 | `GND` | 1 | 0 | `GND-001` |
| `flight-software` | F4 | `FSW` | 0 | — | no parts: data interfaces below |

Retired ids (never reuse): `FIN-001-L` split into half-fins FIN-001-UL / -LL (D-04); `FIN-001-R` split into FIN-001-UR / -LR (D-04); `FIN-005-L` clip set per half-fin (R2), retired in R3; `FIN-005-R` clip set per half-fin (R2), retired in R3; `FIN-005-UR` clip sets retired in R3: station collars FIN-008 + edge strips FIN-011 (D3); `FIN-005-UL` clip sets retired in R3; `FIN-005-LR` clip sets retired in R3; `FIN-005-LL` clip sets retired in R3; `TRN-004` hold-down strap replaced by lid pillars TRN-004-L/R (CR-D7-03); `TRN-006-A` rename to TRN-006-L (side family, CR-A4-24); `TRN-006-B` rename to TRN-006-R (CR-A4-24); `E-MEC-13` link bonded in the horns E-MEC-19…22 (D6-R1); `E-MEC-14` as E-MEC-13; `E-MEC-15` as E-MEC-13; `E-MEC-16` as E-MEC-13.

## Interface register

Declared by the owner in `subsystems/<owner>/interfaces.json`; each subsystem in *Ack* lists the id under `acknowledges`. *By* = designs · sizes. *Decl.* = in the baseline (`yes`), parked in the owner's `edges_pending` or `edges-pending.json` (`pending`), or still to declare (`—`). *C6* = blocks C6 has written in `team/C6/joint_stacks.json` for the owner to copy. *Must carry* is in addition to the per-method block above (for declared edges: the owner's notes, shortened). `OI-nn` = open issue below.

### wing (D1, 11)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-WNG-01` | `WNG-002` Spar CF 22x20x1000 | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | — | D1 | yes | — | spar in the 22.4 mm bore on the camber line (x 0.080, z +0.0066): slot cut from the lower surface to z_s + 11.2 mm with a round top, spar bonded, slot strip trimmed and re-bonded as the cap; four PETG |
| `E-WNG-02` | `WNG-003` Tape skin (packing tape, both surfaces, doublers, tip edge layer) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-TAPE-SKIN` | — | D1 | yes | — | spanwise strips LE to TE, 10 % overlap, 15 mm round the LE; tape laps 15 mm up both faces of each half-fin root (L-angle, E-FIN-53...56); no tape under the pod; 60 mm doublers over the block and servo |
| `E-WNG-03` | `WNG-020` FAA registration label | `WNG-003` Tape skin (packing tape, both surfaces, doublers, tip edge layer) | mechanical · taped · `CT-LABEL` | — | D1 | yes | — | FAA registration number on the right wing upper skin, x 0.115-0.215, y 0.375-0.405; readable without tools (14 CFR 48.205); laminated label, one clear tape strip over the edges |
| `E-WNG-04` | `WNG-011-L` Elevon inboard L | `WNG-001` Wing core, one piece (XPS), with all cuts | kinematic · hinged · `CT-TAPE-HINGE` | — | D1 | yes | — | tape hinge on the upper skin at x 0.2496 (DP-HINGE), panel /y/ 0.071-0.299 with 1 mm end gaps; panel front face bevelled 30 deg on the lower side (5.5 mm at the lower skin); hinge tape and stops by D6 |
| `E-WNG-05` | `WNG-012-L` Elevon outboard L | `WNG-001` Wing core, one piece (XPS), with all cuts | kinematic · hinged · `CT-TAPE-HINGE` | — | D1 | yes | — | tape hinge on the upper skin at x 0.2496 (DP-HINGE), panel /y/ 0.341-0.559 with 1 mm end gaps; panel front face bevelled 30 deg on the lower side (5.5 mm at the lower skin); hinge tape and stops by D6 |
| `E-WNG-06` | `WNG-011-R` Elevon inboard R | `WNG-001` Wing core, one piece (XPS), with all cuts | kinematic · hinged · `CT-TAPE-HINGE` | — | D1 | yes | — | tape hinge on the upper skin at x 0.2496 (DP-HINGE), panel /y/ 0.071-0.299 with 1 mm end gaps; panel front face bevelled 30 deg on the lower side (5.5 mm at the lower skin); hinge tape and stops by D6 |
| `E-WNG-07` | `WNG-012-R` Elevon outboard R | `WNG-001` Wing core, one piece (XPS), with all cuts | kinematic · hinged · `CT-TAPE-HINGE` | — | D1 | yes | — | tape hinge on the upper skin at x 0.2496 (DP-HINGE), panel /y/ 0.341-0.559 with 1 mm end gaps; panel front face bevelled 30 deg on the lower side (5.5 mm at the lower skin); hinge tape and stops by D6 |
| `E-WNG-08` | `WNG-004-L` Spar plug under the through-core block (PETG) L | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | D1 | yes | — | PETG plug D 19.8 x 36 mm bonded inside the spar under the through-core block at /y/ 0.320; pushed from the spar end with a marked dowel (anchor plug first, then the block plug) before the spar is bond |
| `E-WNG-09` | `WNG-004-R` Spar plug under the through-core block (PETG) R | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | D1 | yes | — | PETG plug D 19.8 x 36 mm bonded inside the spar under the through-core block at /y/ 0.320; pushed from the spar end with a marked dowel (anchor plug first, then the block plug) before the spar is bond |
| `E-WNG-10` | `WNG-005-L` Spar plug at the brace anchors (PETG) L | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | D1 | yes | — | PETG plug D 19.8 x 20 mm bonded inside the spar under the brace anchors at /y/ 0.242; pushed from the spar end with a marked dowel (anchor plug first, then the block plug) before the spar is bonded |
| `E-WNG-11` | `WNG-005-R` Spar plug at the brace anchors (PETG) R | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | D1 | yes | — | PETG plug D 19.8 x 20 mm bonded inside the spar under the brace anchors at /y/ 0.242; pushed from the spar end with a marked dowel (anchor plug first, then the block plug) before the spar is bonded |

### fins (D3, 88)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-FIN-01` | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | tube through the block socket bore (22.3 mm, 47 mm long with the bosses), 30 min epoxy, tube scuffed 120 grit |
| `E-FIN-02` | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | tube through the block socket bore (22.3 mm, 47 mm long with the bosses), 30 min epoxy, tube scuffed 120 grit |
| `E-FIN-03` | `FIN-006-R` Tube plug R, CF 20x18 x 53 mm inside the tube at the block | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | plug pushed in from the tube end to z -0.020..0.033 with a rod, laminating epoxy, before the collars and mounts |
| `E-FIN-04` | `FIN-006-L` Tube plug L, CF 20x18 x 53 mm inside the tube at the block | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | plug pushed in from the tube end to z -0.020..0.033 with a rod, laminating epoxy, before the collars and mounts |
| `E-FIN-05` | `FIN-003-UR` Motor mount UR, ASA, 7 deg canted plate, slip clamp (print A) | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-06` | `FIN-003-UL` Motor mount UL, ASA, 7 deg canted plate, slip clamp (print B) | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-07` | `FIN-003-LR` Motor mount LR, ASA, 7 deg canted plate, slip clamp (print B) | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-08` | `FIN-003-LL` Motor mount LL, ASA, 7 deg canted plate, slip clamp (print A) | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-09` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block upper bore boss, 30 min epoxy |
| `E-FIN-10` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block upper bore boss, 30 min epoxy |
| `E-FIN-11` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block lower bore boss, 30 min epoxy |
| `E-FIN-12` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block lower bore boss, 30 min epoxy |
| `E-FIN-13` | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-14` | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-15` | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-16` | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-17` | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-18` | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-19` | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-20` | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-21` | `FIN-011-URO` Edge strip upper right outboard face, CF 10 x 1 | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UR after cure |
| `E-FIN-22` | `FIN-011-URI` Edge strip upper right inboard face, CF 10 x 1 | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UR after cure |
| `E-FIN-23` | `FIN-011-ULO` Edge strip upper left outboard face, CF 10 x 1 | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UL after cure |
| `E-FIN-24` | `FIN-011-ULI` Edge strip upper left inboard face, CF 10 x 1 | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UL after cure |
| `E-FIN-25` | `FIN-011-LRO` Edge strip lower right outboard face, CF 10 x 1 | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LR after cure |
| `E-FIN-26` | `FIN-011-LRI` Edge strip lower right inboard face, CF 10 x 1 | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LR after cure |
| `E-FIN-27` | `FIN-011-LLO` Edge strip lower left outboard face, CF 10 x 1 | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LL after cure |
| `E-FIN-28` | `FIN-011-LLI` Edge strip lower left inboard face, CF 10 x 1 | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LL after cure |
| `E-FIN-29` | `FIN-011-URO` Edge strip upper right outboard face, CF 10 x 1 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-30` | `FIN-011-URI` Edge strip upper right inboard face, CF 10 x 1 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-31` | `FIN-011-ULO` Edge strip upper left outboard face, CF 10 x 1 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-32` | `FIN-011-ULI` Edge strip upper left inboard face, CF 10 x 1 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-33` | `FIN-011-LRO` Edge strip lower right outboard face, CF 10 x 1 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-34` | `FIN-011-LRI` Edge strip lower right inboard face, CF 10 x 1 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-35` | `FIN-011-LLO` Edge strip lower left outboard face, CF 10 x 1 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-36` | `FIN-011-LLI` Edge strip lower left inboard face, CF 10 x 1 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-37` | `FIN-009-UR` Brace UR, CF strip 10 x 2 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-38` | `FIN-009-UL` Brace UL, CF strip 10 x 2 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-39` | `FIN-009-LR` Brace LR, CF strip 10 x 2 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-40` | `FIN-009-LL` Brace LL, CF strip 10 x 2 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-41` | `FIN-009-UR` Brace UR, CF strip 10 x 2 | `FIN-010-UR` Brace anchor UR on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-42` | `FIN-009-UL` Brace UL, CF strip 10 x 2 | `FIN-010-UL` Brace anchor UL on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-43` | `FIN-009-LR` Brace LR, CF strip 10 x 2 | `FIN-010-LR` Brace anchor LR on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-44` | `FIN-009-LL` Brace LL, CF strip 10 x 2 | `FIN-010-LL` Brace anchor LL on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-45` | `FIN-007-UR` ESC pad UR, ASA, on the outboard face of half-fin UR | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-46` | `FIN-007-UL` ESC pad UL, ASA, on the outboard face of half-fin UL | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-47` | `FIN-007-LR` ESC pad LR, ASA, on the outboard face of half-fin LR | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-48` | `FIN-007-LL` ESC pad LL, ASA, on the outboard face of half-fin LL | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-49` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | spar through the block spar bore (22.3 mm, 36 mm long, C2 plug inside the spar); blocks threaded on the spar and set by jig at y = +/-0.320 before the spar is bonded into the core (CL-C4-D3-BLOCK-MS) (OI-02) |
| `E-FIN-50` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | spar through the block spar bore (22.3 mm, 36 mm long, C2 plug inside the spar); blocks threaded on the spar and set by jig at y = +/-0.320 before the spar is bonded into the core (CL-C4-D3-BLOCK-MS) (OI-02) |
| `E-FIN-51` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | block bonded into the core cut-out x 0.028-0.097, y 0.320 +/- 0.018, full depth (D1 cuts it); tape skin over (OI-02) |
| `E-FIN-52` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | block bonded into the core cut-out x 0.028-0.097, y 0.320 +/- 0.018, full depth (D1 cuts it); tape skin over (OI-02) |
| `E-FIN-53` | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-54` | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-55` | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-56` | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-57` | `FIN-010-UR` Brace anchor UR on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | anchor foot bonded on the spar top face through a 20 x 16 mm pocket in skin and core at y +0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-58` | `FIN-010-UL` Brace anchor UL on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | anchor foot bonded on the spar top face through a 20 x 16 mm pocket in skin and core at y -0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-59` | `FIN-010-LR` Brace anchor LR on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | anchor foot bonded on the spar bottom face through a 20 x 16 mm pocket in skin and core at y +0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-60` | `FIN-010-LL` Brace anchor LL on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | yes | bond | anchor foot bonded on the spar bottom face through a 20 x 16 mm pocket in skin and core at y -0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-61` | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | `FIN-003-UR` Motor mount UR, ASA, 7 deg canted plate, slip clamp (print A) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-62` | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-UL` Motor mount UL, ASA, 7 deg canted plate, slip clamp (print B) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-63` | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-LR` Motor mount LR, ASA, 7 deg canted plate, slip clamp (print B) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-64` | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | `FIN-003-LL` Motor mount LL, ASA, 7 deg canted plate, slip clamp (print A) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-65` | `PRP-002-UR` ESC UR LANRC 45 A | `FIN-007-UR` ESC pad UR, ASA, on the outboard face of half-fin UR | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-66` | `PRP-002-UL` ESC UL LANRC 45 A | `FIN-007-UL` ESC pad UL, ASA, on the outboard face of half-fin UL | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-67` | `PRP-002-LR` ESC LR LANRC 45 A | `FIN-007-LR` ESC pad LR, ASA, on the outboard face of half-fin LR | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-68` | `PRP-002-LL` ESC LL LANRC 45 A | `FIN-007-LL` ESC pad LL, ASA, on the outboard face of half-fin LL | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-69` | `FIN-012-UR` Edge-strip pin set UR, 12 x CF rod 2 mm | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-70` | `FIN-012-UL` Edge-strip pin set UL, 12 x CF rod 2 mm | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-71` | `FIN-012-LR` Edge-strip pin set LR, 12 x CF rod 2 mm | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-72` | `FIN-012-LL` Edge-strip pin set LL, 12 x CF rod 2 mm | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-73` | `FIN-012-UR` Edge-strip pin set UR, 12 x CF rod 2 mm | `FIN-011-URO` Edge strip upper right outboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the outboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-74` | `FIN-012-UR` Edge-strip pin set UR, 12 x CF rod 2 mm | `FIN-011-URI` Edge strip upper right inboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the inboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-75` | `FIN-012-UL` Edge-strip pin set UL, 12 x CF rod 2 mm | `FIN-011-ULO` Edge strip upper left outboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the outboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-76` | `FIN-012-UL` Edge-strip pin set UL, 12 x CF rod 2 mm | `FIN-011-ULI` Edge strip upper left inboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the inboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-77` | `FIN-012-LR` Edge-strip pin set LR, 12 x CF rod 2 mm | `FIN-011-LRO` Edge strip lower right outboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the outboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-78` | `FIN-012-LR` Edge-strip pin set LR, 12 x CF rod 2 mm | `FIN-011-LRI` Edge strip lower right inboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the inboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-79` | `FIN-012-LL` Edge-strip pin set LL, 12 x CF rod 2 mm | `FIN-011-LLO` Edge strip lower left outboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the outboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-80` | `FIN-012-LL` Edge-strip pin set LL, 12 x CF rod 2 mm | `FIN-011-LLI` Edge strip lower left inboard face, CF 10 x 1 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | pins through the inboard strip: carry the strip shear flow into the laminate (CR-C6-02) |
| `E-FIN-81` | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | `FIN-003-UR` Motor mount UR, ASA, 7 deg canted plate, slip clamp (print A) | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | four 4 × 4 mm pads; base 66.3 °C design (hover-only, 30 °C, `CL-E3-MOUNT-ASA`) vs 83 °C ASA limit; PETG fails (`CL-E3-MOUNT-PETG`, D-42) |
| `E-FIN-82` | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-UL` Motor mount UL, ASA, 7 deg canted plate, slip clamp (print B) | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | four 4 × 4 mm pads; base 66.3 °C design (hover-only, 30 °C, `CL-E3-MOUNT-ASA`) vs 83 °C ASA limit; PETG fails (`CL-E3-MOUNT-PETG`, D-42) |
| `E-FIN-83` | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-LR` Motor mount LR, ASA, 7 deg canted plate, slip clamp (print B) | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | four 4 × 4 mm pads; base 66.3 °C design (hover-only, 30 °C, `CL-E3-MOUNT-ASA`) vs 83 °C ASA limit; PETG fails (`CL-E3-MOUNT-PETG`, D-42) |
| `E-FIN-84` | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | `FIN-003-LL` Motor mount LL, ASA, 7 deg canted plate, slip clamp (print A) | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | four 4 × 4 mm pads; base 66.3 °C design (hover-only, 30 °C, `CL-E3-MOUNT-ASA`) vs 83 °C ASA limit; PETG fails (`CL-E3-MOUNT-PETG`, D-42) |
| `E-FIN-85` | `PRP-002-UR` ESC UR LANRC 45 A | `FIN-007-UR` ESC pad UR, ASA, on the outboard face of half-fin UR | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | hook-and-loop, treated as insulating; ESC 61.6 °C design (`CL-E3-ESC-PEAK`) vs 85 °C; ASA pad (D-42) |
| `E-FIN-86` | `PRP-002-UL` ESC UL LANRC 45 A | `FIN-007-UL` ESC pad UL, ASA, on the outboard face of half-fin UL | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | hook-and-loop, treated as insulating; ESC 61.6 °C design (`CL-E3-ESC-PEAK`) vs 85 °C; ASA pad (D-42) |
| `E-FIN-87` | `PRP-002-LR` ESC LR LANRC 45 A | `FIN-007-LR` ESC pad LR, ASA, on the outboard face of half-fin LR | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | hook-and-loop, treated as insulating; ESC 61.6 °C design (`CL-E3-ESC-PEAK`) vs 85 °C; ASA pad (D-42) |
| `E-FIN-88` | `PRP-002-LL` ESC LL LANRC 45 A | `FIN-007-LL` ESC pad LL, ASA, on the outboard face of half-fin LL | thermal · conductive · `CT-THERMAL-CONTACT` | propulsion | E3 · D3 | — | — | hook-and-loop, treated as insulating; ESC 61.6 °C design (`CL-E3-ESC-PEAK`) vs 85 °C; ASA pad (D-42) |

### pod (D2, 12)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-POD-01` | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D2 | yes | bond | shell floor, XPS LE filler, side walls and aft wall bonded to bare, sanded foam: D1 cuts the recess (x_rec0 ... x_rec1, z = pod base, full pod width) and leaves the tape skin off under the pod (CR-C2- |
| `E-POD-02` | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | bond | tray front piece (with the forward stop) and rear piece, FC, avionics, PDB and UBEC plates and the JR bar epoxied full-area to the foam-board floor (paper face scuffed); 6 mm microballoon fillets floo |
| `E-POD-03` | `POD-003` Hatch (foam board, printed tongue, 12 x 40 hook-and-loop tab, antenna tube A) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · strapped · `CT-HATCH-HL` | — | D2 | yes | — | opened every flight, tool-free, no magnets; the hatch carries no pack load |
| `E-POD-04` | `POD-004` Pack straps (2, 20 mm hook-and-loop, rubber-backed) + 2 EVA pads 2.5 mm | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · slid · `CT-STRAP-SLOT` | — | D2 | yes | — | each strap passes down a slot, under the tray in a 1 mm groove cut in the foam floor, up the other slot |
| `E-POD-05` | `PWR-001` Flight pack 4S 6500 mAh (re-terminated AS150U, own 10 AWG leads 0.10 m) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · strapped · `CT-STRAP-VELCRO` | power | D2 | yes | — | field joint; field joint. z/y: 2 straps + guides + EVA pads; fore-aft: crush block + spreader ahead (on the forward stop, x -0.1002), U-spacers + aft stop (x 0.077, on the handle bridge) behind. Nominal centroid x |
| `E-POD-06` | `POD-005` GPS mast with 45 deg pad (printed PETG, plugs into the handle grip) | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | mechanical · fastened · `CT-M3-PA66-NUT` | — | D2 | yes | joint_stack | mast plugs 8 mm into the grip socket; cross-screwed with PA66 hardware (C6 CR-C6-18; F3: no steel within 50 mm of the compass); 6.5 mm counterbore 4.5 deep on +y keeps the grip at 10.0 mm (C6 <= 11.0) |
| `E-POD-07` | `POD-006` Pitot boom socket with 32 mm flange (printed PETG, pod nose, left channel) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | — | socket through a 12 mm square hole in the nose wall; 32 x 32 mm flange bonded to the wall inside face (CR-C6-09); the nose block is cut round the flange; boom bending (1 kg on the tip in handling, 0.8 (OI-12) |
| `E-POD-08` | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | — | handle legs pass through 7.8 mm slots in the aft deck at y +/-0.048, bonded: locates the deck |
| `E-POD-09` | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | `WNG-002` Spar CF 22x20x1000 | mechanical · strapped · `CT-SPAR-TIE` | wing | D2 | yes | — | carry point on the spar (D-23): feet saddle the spar top in the open slot (y 0.029 ... 0.053), bonded (scuffed CF, 30 min epoxy), one 7.6 mm nylon tie per foot at y +/-0.036 laid under the spar before |
| `E-POD-10` | `POD-008` Trim kit: XPS crush block (cut per pack), 1.5 mm PETG spreader, PETG U-spacers 2 / 4 / 8 / 8 mm | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | mechanical · slid · `CT-SLIDE-STOP` | — | D2 | yes | — | U-spacers stand between the pack aft face and the aft stop, held by the pack; the pack leads pass over them |
| `E-POD-11` | `POD-008` Trim kit: XPS crush block (cut per pack), 1.5 mm PETG spreader, PETG U-spacers 2 / 4 / 8 / 8 mm | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · slid · `CT-SLIDE-STOP` | — | D2 | yes | — | crush block (with the spreader on the pack fore face) against the 3 mm forward stop, between the guides; cut per pack (length = pack fore face - 1.5 mm - (-0.1002)); in a nose-in crash the stop breaks |
| `E-POD-12` | `PWR-001` Flight pack 4S 6500 mAh (re-terminated AS150U, own 10 AWG leads 0.10 m) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | thermal · conductive · `CT-THERMAL-CONTACT` | power | D2 | yes | — | insulating contact (E3 CR-E3-11): pack on 2.5 mm EVA pads on the 1 mm PETG tray over 4.8 mm foam board; the pack heat leaves by the pod air through the two vents (CR-E3-03), not by this contact |

### landing (D5, 22)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-GER-01` | `GER-001-UR` Foot shoe UR | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 7 mm down both faces, back wall on the step front and the str (OI-05) |
| `E-GER-02` | `GER-001-UL` Foot shoe UL | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 7 mm down both faces, back wall on the step front and the str (OI-05) |
| `E-GER-03` | `GER-001-LR` Foot shoe LR | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 7 mm down both faces, back wall on the step front and the str (OI-05) |
| `E-GER-04` | `GER-001-LL` Foot shoe LL | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 7 mm down both faces, back wall on the step front and the str (OI-05) |
| `E-GER-05` | `GER-002-UR` Foot piston UR | `GER-001-UR` Foot shoe UR | kinematic · slid · `CT-GER-CRUSH-SLIDE` | — | D5 | yes | — | field joint, no tools: press both snap fingers through the side windows (thumb and finger), pull the insert out, push a pre-glued spare of the SAME COLOUR in until both click; <= 3 min (CL-D5-REPLACE- |
| `E-GER-06` | `GER-002-UL` Foot piston UL | `GER-001-UL` Foot shoe UL | kinematic · slid · `CT-GER-CRUSH-SLIDE` | — | D5 | yes | — | field joint, no tools: press both snap fingers through the side windows (thumb and finger), pull the insert out, push a pre-glued spare of the SAME COLOUR in until both click; <= 3 min (CL-D5-REPLACE- |
| `E-GER-07` | `GER-002-LR` Foot piston LR | `GER-001-LR` Foot shoe LR | kinematic · slid · `CT-GER-CRUSH-SLIDE` | — | D5 | yes | — | field joint, no tools: press both snap fingers through the side windows (thumb and finger), pull the insert out, push a pre-glued spare of the SAME COLOUR in until both click; <= 3 min (CL-D5-REPLACE- |
| `E-GER-08` | `GER-002-LL` Foot piston LL | `GER-001-LL` Foot shoe LL | kinematic · slid · `CT-GER-CRUSH-SLIDE` | — | D5 | yes | — | field joint, no tools: press both snap fingers through the side windows (thumb and finger), pull the insert out, push a pre-glued spare of the SAME COLOUR in until both click; <= 3 min (CL-D5-REPLACE- |
| `E-GER-09` | `GER-003-UR` Crush cartridge type U (solid) UR | `GER-002-UR` Foot piston UR | mechanical · bonded · `CT-CA` | — | D5 | yes | — | foam-safe CA, two drops on the piston floor; segments tacked to each other |
| `E-GER-10` | `GER-003-UL` Crush cartridge type U (solid) UL | `GER-002-UL` Foot piston UL | mechanical · bonded · `CT-CA` | — | D5 | yes | — | foam-safe CA, two drops on the piston floor; segments tacked to each other |
| `E-GER-11` | `GER-008-LR` Crush cartridge type L (bored) LR | `GER-002-LR` Foot piston LR | mechanical · bonded · `CT-CA` | — | D5 | yes | — | foam-safe CA, two drops on the piston floor; segments tacked to each other |
| `E-GER-12` | `GER-008-LL` Crush cartridge type L (bored) LL | `GER-002-LL` Foot piston LL | mechanical · bonded · `CT-CA` | — | D5 | yes | — | foam-safe CA, two drops on the piston floor; segments tacked to each other |
| `E-GER-13` | `GER-004-UR` Foot pad UR | `GER-002-UR` Foot piston UR | mechanical · bonded · `CT-GER-PSA` | — | D5 | yes | — | pad cut to the flange outline; wipe the flange with IPA first, press 30 s |
| `E-GER-14` | `GER-004-UL` Foot pad UL | `GER-002-UL` Foot piston UL | mechanical · bonded · `CT-GER-PSA` | — | D5 | yes | — | pad cut to the flange outline; wipe the flange with IPA first, press 30 s |
| `E-GER-15` | `GER-004-LR` Foot pad LR | `GER-002-LR` Foot piston LR | mechanical · bonded · `CT-GER-PSA` | — | D5 | yes | — | pad cut to the flange outline; wipe the flange with IPA first, press 30 s |
| `E-GER-16` | `GER-004-LL` Foot pad LL | `GER-002-LL` Foot piston LL | mechanical · bonded · `CT-GER-PSA` | — | D5 | yes | — | pad cut to the flange outline; wipe the flange with IPA first, press 30 s |
| `E-GER-17` | `GER-003-UR` Crush cartridge type U (solid) UR | `GER-001-UR` Foot shoe UR | mechanical · slid · `CT-GER-END-BEAR` | — | D5 | yes | — | landing load path: pad -> flange -> cartridge -> shoe back wall -> step and legs -> half-fin |
| `E-GER-18` | `GER-003-UL` Crush cartridge type U (solid) UL | `GER-001-UL` Foot shoe UL | mechanical · slid · `CT-GER-END-BEAR` | — | D5 | yes | — | landing load path: pad -> flange -> cartridge -> shoe back wall -> step and legs -> half-fin |
| `E-GER-19` | `GER-008-LR` Crush cartridge type L (bored) LR | `GER-001-LR` Foot shoe LR | mechanical · slid · `CT-GER-END-BEAR` | — | D5 | yes | — | landing load path: pad -> flange -> cartridge -> shoe back wall -> step and legs -> half-fin |
| `E-GER-20` | `GER-008-LL` Crush cartridge type L (bored) LL | `GER-001-LL` Foot shoe LL | mechanical · slid · `CT-GER-END-BEAR` | — | D5 | yes | — | landing load path: pad -> flange -> cartridge -> shoe back wall -> step and legs -> half-fin |
| `E-GER-21` | `GER-007-R` Wingtip TE corner cap R | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-GER-CAP-TAPE` | wing | D5 | pending | — | TPU corner cap on the fixed wingtip TE corner (outboard of the elevon end at /y/ 0.560), over the tape skin; sacrificial contact in a roll-first landing (CR-C5-04, CL-C5-WINGTIP-CLEAR-ROLL); keeps cle |
| `E-GER-22` | `GER-007-L` Wingtip TE corner cap L | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-GER-CAP-TAPE` | wing | D5 | pending | — | TPU corner cap on the fixed wingtip TE corner (outboard of the elevon end at /y/ 0.560), over the tape skin; sacrificial contact in a roll-first landing (CR-C5-04, CL-C5-WINGTIP-CLEAR-ROLL); keeps cle |

### propulsion (E1, 8)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-PRP-01` | `PRP-004-UR` Prop adapter UR M6x1 LH + nut + washer | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot bore (4 mm x 8.5 mm) on the shaft stub, base flat on the bell top, four M3x4 on the 12 mm circle (vendor fit list names the X3108S KV900); bench joint, never a field joint |
| `E-PRP-02` | `PRP-004-UL` Prop adapter UL M6x1 RH + nut + washer | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot bore (4 mm x 8.5 mm) on the shaft stub, base flat on the bell top, four M3x4 on the 12 mm circle (vendor fit list names the X3108S KV900); bench joint, never a field joint |
| `E-PRP-03` | `PRP-004-LR` Prop adapter LR M6x1 RH + nut + washer | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot bore (4 mm x 8.5 mm) on the shaft stub, base flat on the bell top, four M3x4 on the 12 mm circle (vendor fit list names the X3108S KV900); bench joint, never a field joint |
| `E-PRP-04` | `PRP-004-LL` Prop adapter LL M6x1 LH + nut + washer | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot bore (4 mm x 8.5 mm) on the shaft stub, base flat on the bell top, four M3x4 on the 12 mm circle (vendor fit list names the X3108S KV900); bench joint, never a field joint |
| `E-PRP-05` | `PRP-003-UR` Prop UR APC 11x5.5MRP (LP11055MRP) | `PRP-004-UR` Prop adapter UR M6x1 LH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MRP (LP11055MRP) on a LH post; LPAR06E ring centres the 1/4 in bore on the M6 post; hub rear face on the adapter shoulder; prop off for transport (pouch spanner, D-40) |
| `E-PRP-06` | `PRP-003-UL` Prop UL APC 11x5.5MR (LP11055MR) | `PRP-004-UL` Prop adapter UL M6x1 RH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MR (LP11055MR) on a RH post; LPAR06E ring centres the 1/4 in bore on the M6 post; hub rear face on the adapter shoulder; prop off for transport (pouch spanner, D-40) |
| `E-PRP-07` | `PRP-003-LR` Prop LR APC 11x5.5MR (LP11055MR) | `PRP-004-LR` Prop adapter LR M6x1 RH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MR (LP11055MR) on a RH post; LPAR06E ring centres the 1/4 in bore on the M6 post; hub rear face on the adapter shoulder; prop off for transport (pouch spanner, D-40) |
| `E-PRP-08` | `PRP-003-LL` Prop LL APC 11x5.5MRP (LP11055MRP) | `PRP-004-LL` Prop adapter LL M6x1 LH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MRP (LP11055MRP) on a LH post; LPAR06E ring centres the 1/4 in bore on the M6 post; hub rear face on the adapter shoulder; prop off for transport (pouch spanner, D-40) |

### power (F1, 10)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-PWR-01` | `PWR-002` Main disconnect AS150U aircraft half + two 10 AWG main jumpers | `PWR-006` Power frame: deck on 4 spacers, wire window, AS150U cradle, legs, fuse clip (printed PETG) | mechanical · bonded · `CT-CONN-PARK` | — | F1 | yes | — | AS150U aircraft half in the frame cradle (x 0.002 ... 0.031, left channel); the cradle, not the 10 AWG cups, takes the plug and unplug force at every field set-up; plug reachable through the hatch wit |
| `E-PWR-02` | `PWR-003` Power module: CoreWing F405 Wing V2 power board (V/I sense), separated from the FC stack | `PWR-006` Power frame: deck on 4 spacers, wire window, AS150U cradle, legs, fuse clip (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | — | F1 | yes | — | power board on 3M foam tape on the deck, aft edge at the wire window; one tie round board and deck through two deck slots. Replaces the R2 tape-to-tray (CR-F1-16); the frame screws sit under the board |
| `E-PWR-03` | `PWR-006` Power frame: deck on 4 spacers, wire window, AS150U cradle, legs, fuse clip (printed PETG) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · fastened · `CT-M3-SHCS-INSERT` | pod | F1 | yes | joint_stack | frame deck on four 10 mm nylon spacers over D2's four PDB-plate bosses (25 mm pattern, inserts at z 0.0266); nylon keeps the stack insulating next to the bus bars and non-magnetic. Supersedes the C6 M |
| `E-PWR-04` | `PWR-005` UBEC 6.0 V, 8 A class, servo rail | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F1 | yes | — | UBEC on foam tape + 1 tie in the right channel UBEC zone, label up, >= 0.10 m from the GPS; on a 1 mm tray plate (CR-F1-17) |
| `E-PWR-05` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F1 | yes | — | bus board on foam tape on the PDB plate between D2's boss rows, under the deck; the ESC leads are tied to the tray tie bar within 80 mm (F2), so lead pulls do not reach the tape |
| `E-PWR-07` | `PWR-007` UBEC feed fuse 5 A mini blade in an inline holder | `PWR-006` Power frame: deck on 4 spacers, wire window, AS150U cradle, legs, fuse clip (printed PETG) | mechanical · press_fit · `CT-SNAP-CLIP` | — | F1 | yes | — | fuse holder snapped into the clip under the cradle floor, outboard half of the lead tunnel; fuse change on the bench (frame screws out) |
| `E-PWR-11` | `PWR-008-UR` ESC capacitor 680 uF 25 V low-ESR, UR | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · taped · `CT-TAPE-FOAM` | fins | F1 | yes | — | cap laid along x on the half-fin outboard face 3 mm aft of the ESC pad, clear of the ESC strap and FET face (E3); leads to the ESC power pads <= 20 mm (harness edge, CR-F1-18) |
| `E-PWR-12` | `PWR-008-UL` ESC capacitor 680 uF 25 V low-ESR, UL | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip, 8 mm lead hole | mechanical · taped · `CT-TAPE-FOAM` | fins | F1 | yes | — | cap laid along x on the half-fin outboard face 3 mm aft of the ESC pad, clear of the ESC strap and FET face (E3); leads to the ESC power pads <= 20 mm (harness edge, CR-F1-18) |
| `E-PWR-13` | `PWR-008-LR` ESC capacitor 680 uF 25 V low-ESR, LR | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · taped · `CT-TAPE-FOAM` | fins | F1 | yes | — | cap laid along x on the half-fin outboard face 3 mm aft of the ESC pad, clear of the ESC strap and FET face (E3); leads to the ESC power pads <= 20 mm (harness edge, CR-F1-18) |
| `E-PWR-14` | `PWR-008-LL` ESC capacitor 680 uF 25 V low-ESR, LL | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, 8 mm lead hole, link slot | mechanical · taped · `CT-TAPE-FOAM` | fins | F1 | yes | — | cap laid along x on the half-fin outboard face 3 mm aft of the ESC pad, clear of the ESC strap and FET face (E3); leads to the ESC power pads <= 20 mm (harness edge, CR-F1-18) |

### avionics (F3, 10)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-AVN-01` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-GEL-PAD` | pod | F3 | yes | retention | FC top board on 4 gel cubes (5 mm) on the scuffed FC plate, between D2's end stops (2 mm clear); no screws, no header pins; arrow -x; beside the pack, never its stop (CR-C5-07). Secondary: 10 mm hook- |
| `E-AVN-02` | `AVN-002` GPS + compass HGLRC M100-5883 | `POD-005` GPS mast with 45 deg pad (printed PETG, plugs into the handle grip) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 | yes | — | GPS on 1 mm foam tape on the 45 deg mast pad (pad normal (-x,+z)/sqrt2), module arrow down-forward along the pad (toward the nose); cable tied once to the mast; no steel within 50 mm (non-metallic mas |
| `E-AVN-03` | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 | yes | — | RX on 1 mm foam tape on the avionics plate, crosswise behind the aft tie post, under antenna tube A; antenna A up the hatch tube (z), antenna B to the nose tube (F5: needs a 100-150 mm U.FL antenna, C |
| `E-AVN-04` | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 | yes | — | airspeed board on 1 mm foam tape between the two tie posts (locating fit in x), 1 tie through the post slots over the board; ports up; lines to the couplers 40 mm each (<= 60 mm) |
| `E-AVN-05` | `AVN-005` Pitot boom (plug-in): pitot-static probe in a printed keyed sleeve | `POD-006` Pitot boom socket with 32 mm flange (printed PETG, pod nose, left channel) | mechanical · slid · `CT-PLUG-IN` | pod | F3 | yes | — | field joint; keyed sleeve (5.6 mm flat on +z) into the 6.2 mm socket bore, shoulder on the collar front face (x -0.123); drag in cruise and gravity in hover act along +x and push it home; friction set to 2-5 N pul (OI-12) |
| `E-AVN-06` | `AVN-005` Pitot boom (plug-in): pitot-static probe in a printed keyed sleeve | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | mechanical · press_fit · `CT-PITOT-TUBING` | — | F3 | yes | — | two silicone lines 2.5 mm ID: probe total (centre barb) to sensor port P1, static to P2 (ARSPD_TUBE_ORDR 2, so a swap is harmless); barbed couplers at the probe root part when the boom is pulled; line |
| `E-AVN-07` | `AVN-006` Isolation and retention set: 4 gel cubes, foam tape, ties, FC strap | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · taped · `CT-GEL-PAD` | pod | F3 | yes | — | gel cubes stuck to the IPA-wiped FC plate; mass holder for tape, ties and the FC strap |
| `E-AVN-08` | `AVN-007` microSD 16-32 GB (logging) | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | mechanical · press_fit · `CT-CARD-SLOT` | — | F3 | yes | — | 16-32 GB SDHC, FAT32, in the FC fore-edge slot; a strip of tape over the card against vibration |
| `E-AVN-09` | `GND-001` RC transmitter (ELRS 2.4 GHz, 25 mW) | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | electrical · radio · `CT-ELRS-RF` | ground | F3 | pending | — | ELRS 2.4 GHz radio link, CRSF 420 kbaud to the FC; telemetry through ELRS (ratio 1:4), no separate radio; range test T-F5-RANGE |
| `E-AVN-10` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | thermal · conductive · `CT-THERMAL-CONTACT` | pod | F3 | yes | — | FC board on gel cubes (insulating): heat leaves by convection in the vented pod; the BEC losses sit on the power board (PWR-003) on the PDB plate after the stack split (CR-F3-14 to E3) |

### harness (F2, 37)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-HRN-01` | `HRN-001` Pod harness bundle (lumped: pod runs of every lead, GPS cable, JR row, GH plugs) | `POD-002` Tray: bay floor (2 pieces) + 3 mm forward stop + 1.5 mm guides, FC, avionics, PDB and UBEC plates, JR tie bar (printed PETG) | mechanical · strapped · `CT-TIE` | pod | F2 | yes | — | pod runs tied to the tray tie bar and taped to the floor and side walls; JR row on the tie bar (CR-F2 to D2) |
| `E-HRN-02` | `HRN-002-L` Wing-fin harness bundle L (grooves, fin-face leads, phase joints) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-WIRE-CHANNEL` | wing | F2 | pending | — | three grooves per surface ahead of the spar slot (signal, +, - at 5 mm pitch), P1 slanted straw, servo groove aft of the spar; tape over, skin over |
| `E-HRN-03` | `HRN-002-R` Wing-fin harness bundle R (grooves, fin-face leads, phase joints) | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | tie at the boss tail (inboard face), lead then crosses the half-fin in the grommeted hole (D3 CR-D3-12: tie points at the block boss and the collar) |
| `E-HRN-04` | `HRN-002-R` Wing-fin harness bundle R (grooves, fin-face leads, phase joints) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-WIRE-CHANNEL` | wing | F2 | pending | — | as E-HRN-02, right side |
| `E-HRN-05` | `HRN-002-L` Wing-fin harness bundle L (grooves, fin-face leads, phase joints) | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes + 2 tie lugs) | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | as E-HRN-03, left side |
| `E-HRN-06` | `HRN-002-R` Wing-fin harness bundle R (grooves, fin-face leads, phase joints) | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | phase leads tied to the station collar tail (outboard) |
| `E-HRN-07` | `HRN-002-R` Wing-fin harness bundle R (grooves, fin-face leads, phase joints) | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | as E-HRN-06, lower |
| `E-HRN-08` | `HRN-002-L` Wing-fin harness bundle L (grooves, fin-face leads, phase joints) | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | as E-HRN-06, left |
| `E-HRN-09` | `HRN-002-L` Wing-fin harness bundle L (grooves, fin-face leads, phase joints) | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear + tie lug | mechanical · strapped · `CT-TIE` | fins | F2 | yes | — | as E-HRN-06, left lower |
| `E-HRN-10` | `PWR-001` Flight pack 4S 6500 mAh (re-terminated AS150U, own 10 AWG leads 0.10 m) | `PWR-002` Main disconnect AS150U aircraft half + two 10 AWG main jumpers | electrical · connector · `CT-AS150U` | power | F2 | pending | — | field joint; Pack + / - (pack's own 10 AWG lead). Wire list rows W-PACK; routed cut length 0.056 m |
| `E-HRN-11` | `PWR-002` Main disconnect AS150U aircraft half + two 10 AWG main jumpers | `PWR-003` Power module: CoreWing F405 Wing V2 power board (V/I sense), separated from the FC stack | electrical · soldered · `CT-SOLDER-DC` | power | F2 | pending | — | Vbat main + / -. Wire list rows W-MAIN-1; routed cut length 0.016 m |
| `E-HRN-12` | `PWR-003` Power module: CoreWing F405 Wing V2 power board (V/I sense), separated from the FC stack | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | electrical · soldered · `CT-SOLDER-DC` | power | F2 | pending | — | Vbat main + / -. Wire list rows W-MAIN-2; routed cut length 0.022 m |
| `E-HRN-13` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `PRP-002-UR` ESC UR LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F2 | pending | — | ESC UR power + / -. Wire list rows W-PWR-UR; routed cut length 0.626 m |
| `E-HRN-14` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `PRP-002-UL` ESC UL LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F2 | pending | — | ESC UL power + / -. Wire list rows W-PWR-UL; routed cut length 0.512 m |
| `E-HRN-15` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `PRP-002-LR` ESC LR LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F2 | pending | — | ESC LR power + / -. Wire list rows W-PWR-LR; routed cut length 0.650 m |
| `E-HRN-16` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `PRP-002-LL` ESC LL LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F2 | pending | — | ESC LL power + / -. Wire list rows W-PWR-LL; routed cut length 0.534 m |
| `E-HRN-17` | `PRP-002-UR` ESC UR LANRC 45 A | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | electrical · soldered · `CT-SOLDER-PHASE` | propulsion | F2 | yes | — | Motor UR phases A/B/C. Wire list rows W-PH-UR; routed cut length 0.121 m |
| `E-HRN-18` | `PRP-002-UL` ESC UL LANRC 45 A | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | electrical · soldered · `CT-SOLDER-PHASE` | propulsion | F2 | yes | — | Motor UL phases A/B/C. Wire list rows W-PH-UL; routed cut length 0.121 m |
| `E-HRN-19` | `PRP-002-LR` ESC LR LANRC 45 A | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | electrical · soldered · `CT-SOLDER-PHASE` | propulsion | F2 | yes | — | Motor LR phases A/B/C. Wire list rows W-PH-LR; routed cut length 0.121 m |
| `E-HRN-20` | `PRP-002-LL` ESC LL LANRC 45 A | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | electrical · soldered · `CT-SOLDER-PHASE` | propulsion | F2 | yes | — | Motor LL phases A/B/C. Wire list rows W-PH-LL; routed cut length 0.121 m |
| `E-HRN-21` | `PWR-004` Bus board: FR4 strip with two tinned 8 AWG bus bars (+ / -) | `PWR-007` UBEC feed fuse 5 A mini blade in an inline holder | electrical · soldered · `CT-SOLDER-DC` | power | F2 | pending | — | UBEC feed, bus bars -> fuse holder pigtail 20 AWG (CR-F1-18); E-HRN-33 continues to the UBEC |
| `E-HRN-22` | `PWR-005` UBEC 6.0 V, 8 A class, servo rail | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | electrical · connector · `CT-SERVO-JR` | avionics, power | F2 | pending | — | Servo rail 6 V + / -. Wire list rows W-UBEC-OUT; routed cut length 0.058 m |
| `E-HRN-23` | `PWR-003` Power module: CoreWing F405 Wing V2 power board (V/I sense), separated from the FC stack | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | electrical · connector · `CT-JST-GH-6` | avionics, power | F2 | pending | — | Power-board link: Vbat sense, current sense, 5 V, GND (6-pin). Wire list rows W-PMOD; routed cut length 0.146 m |
| `E-HRN-24` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-UR` ESC UR LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 | pending | — | signal only; DShot300 bidirectional + GND, motor UR (twisted, no power). Wire list rows W-SIG-UR-P, W-SIG-UR; routed cut length 0.530 m |
| `E-HRN-25` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-UL` ESC UL LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 | pending | — | signal only; DShot300 bidirectional + GND, motor UL (twisted, no power). Wire list rows W-SIG-UL-P, W-SIG-UL; routed cut length 0.664 m |
| `E-HRN-26` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-LR` ESC LR LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 | pending | — | signal only; DShot300 bidirectional + GND, motor LR (twisted, no power). Wire list rows W-SIG-LR-P, W-SIG-LR; routed cut length 0.555 m |
| `E-HRN-27` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-LL` ESC LL LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 | pending | — | signal only; DShot300 bidirectional + GND, motor LL (twisted, no power). Wire list rows W-SIG-LL-P, W-SIG-LL; routed cut length 0.686 m |
| `E-HRN-28` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `MEC-001-L` Elevon servo Savox SH-0255MG+ left | electrical · connector · `CT-SERVO-JR` | avionics, mechanisms | F2 | pending | — | Elevon L PWM 50 Hz + 6 V + GND. Wire list rows W-SRV-L-P, W-SRV-L; routed cut length 0.560 m |
| `E-HRN-29` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `MEC-001-R` Elevon servo Savox SH-0255MG+ right | electrical · connector · `CT-SERVO-JR` | avionics, mechanisms | F2 | pending | — | Elevon R PWM 50 Hz + 6 V + GND. Wire list rows W-SRV-R-P, W-SRV-R; routed cut length 0.519 m |
| `E-HRN-30` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-002` GPS + compass HGLRC M100-5883 | electrical · connector · `CT-JST-GH-6` | avionics | F2 | pending | — | GPS UART (SERIAL5 TX/RX) + I2C SDA/SCL + 5 V + GND. Wire list rows W-GPS; routed cut length 0.272 m |
| `E-HRN-31` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | electrical · connector · `CT-JST-GH-4` | avionics | F2 | pending | — | CRSF: 5 V, GND, FC TX -> RX RX, FC RX <- RX TX. Wire list rows W-RX; routed cut length 0.134 m |
| `E-HRN-32` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | electrical · connector · `CT-JST-GH-4` | avionics | F2 | pending | — | I2C branch SDA/SCL + 5 V + GND to MS4525DO (0x28). Wire list rows W-ASPD; routed cut length 0.183 m |
| `E-HRN-33` | `PWR-007` UBEC feed fuse 5 A mini blade in an inline holder | `PWR-005` UBEC 6.0 V, 8 A class, servo rail | electrical · soldered · `CT-SOLDER-DC` | power | F1 · F2 | — | — | fuse holder pigtail -> UBEC input, 20 AWG; fuse 5 A in the wire block (CR-F1-06, CR-F1-18) |
| `E-HRN-34` | `PRP-002-UR` ESC UR LANRC 45 A | `PWR-008-UR` ESC capacitor 680 uF 25 V low-ESR, UR | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | 680 µF 25 V cap leads ≤ 20 mm at the ESC power pads, cap x 0.127…0.147 on the fin face (CR-F1-18, CR-F1-22) |
| `E-HRN-35` | `PRP-002-UL` ESC UL LANRC 45 A | `PWR-008-UL` ESC capacitor 680 uF 25 V low-ESR, UL | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | 680 µF 25 V cap leads ≤ 20 mm at the ESC power pads, cap x 0.127…0.147 on the fin face (CR-F1-18, CR-F1-22) |
| `E-HRN-36` | `PRP-002-LR` ESC LR LANRC 45 A | `PWR-008-LR` ESC capacitor 680 uF 25 V low-ESR, LR | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | 680 µF 25 V cap leads ≤ 20 mm at the ESC power pads, cap x 0.127…0.147 on the fin face (CR-F1-18, CR-F1-22) |
| `E-HRN-37` | `PRP-002-LL` ESC LL LANRC 45 A | `PWR-008-LL` ESC capacitor 680 uF 25 V low-ESR, LL | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | 680 µF 25 V cap leads ≤ 20 mm at the ESC power pads, cap x 0.127…0.147 on the fin face (CR-F1-18, CR-F1-22) |

### mechanisms (D6, 32)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-MEC-01` | `MEC-008-L` Servo frame (ear slots, cover bosses) left | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | servo frame bonded in the lower-skin pocket (top plate + walls, epoxy + microballoons), tape cut back 3 mm |
| `E-MEC-02` | `MEC-008-R` Servo frame (ear slots, cover bosses) right | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | servo frame bonded in the lower-skin pocket (top plate + walls, epoxy + microballoons), tape cut back 3 mm |
| `E-MEC-03` | `MEC-001-L` Elevon servo Savox SH-0255MG+ left | `MEC-008-L` Servo frame (ear slots, cover bosses) left | mechanical · slid · `CT-SERVO-EAR-SLOT` | — | D6 | yes | joint_stack | servo ears captured in the frame end-wall slots; the cover holds the servo up into the frame |
| `E-MEC-04` | `MEC-001-R` Elevon servo Savox SH-0255MG+ right | `MEC-008-R` Servo frame (ear slots, cover bosses) right | mechanical · slid · `CT-SERVO-EAR-SLOT` | — | D6 | yes | joint_stack | servo ears captured in the frame end-wall slots; the cover holds the servo up into the frame |
| `E-MEC-05` | `MEC-002-L` Servo arm, single, hole at 15.6 mm left | `MEC-001-L` Elevon servo Savox SH-0255MG+ left | mechanical · fastened · `CT-SERVO-SPLINE` | — | D6 | yes | — | arm on the spline at servo neutral, supplied M2 screw + Loctite 222 |
| `E-MEC-06` | `MEC-002-R` Servo arm, single, hole at 15.6 mm right | `MEC-001-R` Elevon servo Savox SH-0255MG+ right | mechanical · fastened · `CT-SERVO-SPLINE` | — | D6 | yes | — | arm on the spline at servo neutral, supplied M2 screw + Loctite 222 |
| `E-MEC-07` | `MEC-003-L` Pushrod 2-56 steel, Z-bend + steel clevis + keeper left | `MEC-002-L` Servo arm, single, hole at 15.6 mm left | kinematic · hinged · `CT-CLEVIS` | — | D6 | yes | — | Z-bend in the arm hole drilled 1.6 mm |
| `E-MEC-08` | `MEC-003-R` Pushrod 2-56 steel, Z-bend + steel clevis + keeper right | `MEC-002-R` Servo arm, single, hole at 15.6 mm right | kinematic · hinged · `CT-CLEVIS` | — | D6 | yes | — | Z-bend in the arm hole drilled 1.6 mm |
| `E-MEC-09` | `MEC-003-L` Pushrod 2-56 steel, Z-bend + steel clevis + keeper left | `MEC-004-L` Control horn, inboard panel (clevis + rod boss) left | kinematic · hinged · `CT-CLEVIS` | — | D6 | yes | — | steel 2-56 clevis on the horn pin hole, silicone keeper |
| `E-MEC-10` | `MEC-003-R` Pushrod 2-56 steel, Z-bend + steel clevis + keeper right | `MEC-004-R` Control horn, inboard panel (clevis + rod boss) right | kinematic · hinged · `CT-CLEVIS` | — | D6 | yes | — | steel 2-56 clevis on the horn pin hole, silicone keeper |
| `E-MEC-11` | `MEC-004-L` Control horn, inboard panel (clevis + rod boss) left | `WNG-011-L` Elevon inboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | through-panel horn: blade in a 2.5 mm slot, lower flange and upper backplate on bare foam, bore on the tube |
| `E-MEC-12` | `MEC-004-R` Control horn, inboard panel (clevis + rod boss) right | `WNG-011-R` Elevon inboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | through-panel horn: blade in a 2.5 mm slot, lower flange and upper backplate on bare foam, bore on the tube |
| `E-MEC-17` | `MEC-007-L` Servo cover with arm slot left | `WNG-003` Tape skin (packing tape, both surfaces, doublers, tip edge layer) | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | yes | — | cover edges taped to the skin (service: peel, remove 2 screws) |
| `E-MEC-18` | `MEC-007-R` Servo cover with arm slot right | `WNG-003` Tape skin (packing tape, both surfaces, doublers, tip edge layer) | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | yes | — | cover edges taped to the skin (service: peel, remove 2 screws) |
| `E-MEC-19` | `MEC-005-L` Inter-panel rod, 1/8 in music wire left | `MEC-004-L` Control horn, inboard panel (clevis + rod boss) left | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | rod bonded over 10 mm in the inboard horn boss |
| `E-MEC-20` | `MEC-005-R` Inter-panel rod, 1/8 in music wire right | `MEC-004-R` Control horn, inboard panel (clevis + rod boss) right | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | rod bonded over 10 mm in the inboard horn boss |
| `E-MEC-21` | `MEC-005-L` Inter-panel rod, 1/8 in music wire left | `MEC-006-L` Link horn, outboard panel (rod boss) left | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | rod bonded over 10 mm in the link horn boss |
| `E-MEC-22` | `MEC-005-R` Inter-panel rod, 1/8 in music wire right | `MEC-006-R` Link horn, outboard panel (rod boss) right | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | rod bonded over 10 mm in the link horn boss |
| `E-MEC-23` | `MEC-006-L` Link horn, outboard panel (rod boss) left | `WNG-012-L` Elevon outboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | through-panel link horn in the outboard panel |
| `E-MEC-24` | `MEC-006-R` Link horn, outboard panel (rod boss) right | `WNG-012-R` Elevon outboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | through-panel link horn in the outboard panel |
| `E-MEC-25` | `MEC-009-LI` Elevon torque tube CF 5 x 4 mm left, inboard panel | `WNG-011-L` Elevon inboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | torque tube in a routed groove, epoxy + microballoon fill, taped over |
| `E-MEC-26` | `MEC-009-RI` Elevon torque tube CF 5 x 4 mm right, inboard panel | `WNG-011-R` Elevon inboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | torque tube in a routed groove, epoxy + microballoon fill, taped over |
| `E-MEC-27` | `MEC-009-LO` Elevon torque tube CF 5 x 4 mm left, outboard panel | `WNG-012-L` Elevon outboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | torque tube in a routed groove, epoxy + microballoon fill, taped over |
| `E-MEC-28` | `MEC-009-RO` Elevon torque tube CF 5 x 4 mm right, outboard panel | `WNG-012-R` Elevon outboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | yes | — | torque tube in a routed groove, epoxy + microballoon fill, taped over |
| `E-MEC-29` | `MEC-004-L` Control horn, inboard panel (clevis + rod boss) left | `MEC-009-LI` Elevon torque tube CF 5 x 4 mm left, inboard panel | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | horn blade bore bonded on the torque tube |
| `E-MEC-30` | `MEC-004-R` Control horn, inboard panel (clevis + rod boss) right | `MEC-009-RI` Elevon torque tube CF 5 x 4 mm right, inboard panel | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | horn blade bore bonded on the torque tube |
| `E-MEC-31` | `MEC-006-L` Link horn, outboard panel (rod boss) left | `MEC-009-LO` Elevon torque tube CF 5 x 4 mm left, outboard panel | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | link horn blade bore bonded on the torque tube |
| `E-MEC-32` | `MEC-006-R` Link horn, outboard panel (rod boss) right | `MEC-009-RO` Elevon torque tube CF 5 x 4 mm right, outboard panel | mechanical · bonded · `CT-EPOXY` | — | D6 | yes | — | link horn blade bore bonded on the torque tube |
| `E-MEC-33` | `MEC-010-L` Elevon hinge tape, two strips left | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | yes | — | hinge tape on the core side of the hinge (the panel side is the wing hinge edge E-WNG-04..07) |
| `E-MEC-34` | `MEC-010-R` Elevon hinge tape, two strips right | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | yes | — | hinge tape on the core side of the hinge (the panel side is the wing hinge edge E-WNG-04..07) |
| `E-MEC-35` | `MEC-007-L` Servo cover with arm slot left | `MEC-008-L` Servo frame (ear slots, cover bosses) left | mechanical · fastened · `CT-M2-SCREW-PLASTIC` | — | D6 | yes | — | cover screwed to the frame bosses, 2 x M2 x 6 |
| `E-MEC-36` | `MEC-007-R` Servo cover with arm slot right | `MEC-008-R` Servo frame (ear slots, cover bosses) right | mechanical · fastened · `CT-M2-SCREW-PLASTIC` | — | D6 | yes | — | cover screwed to the frame bosses, 2 x M2 x 6 |

### transport (D7, 21)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-TRN-01` | `TRN-002-L` Spar cradle L (saddle + crush column) | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | column base on the floor + 2 zip ties through the floor |
| `E-TRN-02` | `TRN-002-R` Spar cradle R (saddle + crush column) | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | as E-TRN-01 |
| `E-TRN-03` | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | tray on the floor between the cradles |
| `E-TRN-04` | `TRN-004-L` Lid hold-down pillar L | `TRN-005` Lid with plug lip (no lining, D-31) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | pillar on the lid shell |
| `E-TRN-05` | `TRN-004-R` Lid hold-down pillar R | `TRN-005` Lid with plug lip (no lining, D-31) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | pillar on the lid shell |
| `E-TRN-06` | `TRN-002-L` Spar cradle L (saddle + crush column) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · slid · `CT-CRADLE-CONTACT` | wing | D7 | yes | — | bears on the tape skin WNG-003 over the core (check.py bbox WARN on WNG-003 expected, CR-D7-19). Saddle under the lower surface at y -0.20 (0.17-0.23), x -0.015..0.235 (spar line), 15 000 mm2 >= C2 1 |
| `E-TRN-07` | `TRN-002-R` Spar cradle R (saddle + crush column) | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · slid · `CT-CRADLE-CONTACT` | wing | D7 | yes | — | as E-TRN-06 at y +0.20 |
| `E-TRN-08` | `TRN-004-L` Lid hold-down pillar L | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · slid · `CT-TRN-PRELOAD-PAD` | wing | D7 | yes | — | on the tape skin over the core; upper surface over the spar at y -0.20, x 0.03..0.13; replaces the strap of the A4 plan (E-TRN-07 there) |
| `E-TRN-09` | `TRN-004-R` Lid hold-down pillar R | `WNG-001` Wing core, one piece (XPS), with all cuts | mechanical · slid · `CT-TRN-PRELOAD-PAD` | wing | D7 | yes | — | as E-TRN-08 at y +0.20 |
| `E-TRN-10` | `TRN-005` Lid with plug lip (no lining, D-31) | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · slid · `CT-TRN-PLUG-LID` | — | D7 | yes | — | — |
| `E-TRN-11` | `TRN-006-L` Cam-buckle strap L | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · strapped · `CT-TRN-CAM-STRAP` | — | D7 | yes | — | y -0.40 |
| `E-TRN-12` | `TRN-006-R` Cam-buckle strap R | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · strapped · `CT-TRN-CAM-STRAP` | — | D7 | yes | — | y +0.40 |
| `E-TRN-13` | `TRN-007-C` Side carry handle | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | side handle at the box CG |
| `E-TRN-14` | `TRN-007-L` End handle L | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | end handle |
| `E-TRN-15` | `TRN-007-R` End handle R | `TRN-001` Box base (floor, walls, end pads, nose pad) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | end handle |
| `E-TRN-16` | `TRN-008` Field pouch (10 mm prop spanner, spare M6 prop nuts, 2.5 mm key, tape, checklist card) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | — | D7 | yes | — | pouch pocket at the tray aft end |
| `E-TRN-17` | `PRP-003-UR` Prop UR APC 11x5.5MRP (LP11055MRP) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 | yes | — | stowed; prop UR on edge in a 285 x 30 x 40 mm tray slot, label to the motor colour |
| `E-TRN-18` | `PRP-003-UL` Prop UL APC 11x5.5MR (LP11055MR) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 | yes | — | stowed; as E-TRN-17 |
| `E-TRN-19` | `PRP-003-LR` Prop LR APC 11x5.5MR (LP11055MR) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 | yes | — | stowed; as E-TRN-17 |
| `E-TRN-20` | `PRP-003-LL` Prop LL APC 11x5.5MRP (LP11055MRP) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 | yes | — | stowed; as E-TRN-17 |
| `E-TRN-21` | `AVN-005` Pitot boom (plug-in): pitot-static probe in a printed keyed sleeve | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | avionics | D7 | yes | — | stowed; pitot boom in its 220 x 25 x 25 mm tray slot, tip cover on, tip end against the PE plug (CR-D7-09) |

## Acknowledgements owed

| Subsystem | Must list under `acknowledges` |
|---|---|
| `wing` | `E-FIN-49` `E-FIN-50` `E-FIN-51` `E-FIN-52` `E-FIN-53` `E-FIN-54` `E-FIN-55` `E-FIN-56` `E-FIN-57` `E-FIN-58` `E-FIN-59` `E-FIN-60` `E-POD-01` `E-POD-09` `E-GER-21` `E-GER-22` `E-HRN-02` `E-HRN-04` `E-MEC-01` `E-MEC-02` `E-MEC-11` `E-MEC-12` `E-MEC-17` `E-MEC-18` `E-MEC-23` `E-MEC-24` `E-MEC-25` `E-MEC-26` `E-MEC-27` `E-MEC-28` `E-MEC-33` `E-MEC-34` `E-TRN-06` `E-TRN-07` `E-TRN-08` `E-TRN-09` |
| `fins` | `E-GER-01` `E-GER-02` `E-GER-03` `E-GER-04` `E-PWR-11` `E-PWR-12` `E-PWR-13` `E-PWR-14` `E-HRN-03` `E-HRN-05` `E-HRN-06` `E-HRN-07` `E-HRN-08` `E-HRN-09` |
| `pod` | `E-PWR-03` `E-PWR-04` `E-PWR-05` `E-AVN-01` `E-AVN-02` `E-AVN-03` `E-AVN-04` `E-AVN-05` `E-AVN-07` `E-AVN-10` `E-HRN-01` |
| `landing` | — |
| `propulsion` | `E-FIN-61` `E-FIN-62` `E-FIN-63` `E-FIN-64` `E-FIN-65` `E-FIN-66` `E-FIN-67` `E-FIN-68` `E-HRN-17` `E-HRN-18` `E-HRN-19` `E-HRN-20` `E-HRN-13` `E-HRN-14` `E-HRN-15` `E-HRN-16` `E-HRN-24` `E-HRN-25` `E-HRN-26` `E-HRN-27` `E-TRN-17` `E-TRN-18` `E-TRN-19` `E-TRN-20` `E-HRN-34` `E-HRN-35` `E-HRN-36` `E-HRN-37` `E-FIN-81` `E-FIN-82` `E-FIN-83` `E-FIN-84` `E-FIN-85` `E-FIN-86` `E-FIN-87` `E-FIN-88` |
| `power` | `E-POD-05` `E-POD-12` `E-HRN-10` `E-HRN-11` `E-HRN-12` `E-HRN-13` `E-HRN-14` `E-HRN-15` `E-HRN-16` `E-HRN-21` `E-HRN-22` `E-HRN-23` `E-HRN-33` `E-HRN-34` `E-HRN-35` `E-HRN-36` `E-HRN-37` |
| `avionics` | `E-HRN-22` `E-HRN-23` `E-HRN-24` `E-HRN-25` `E-HRN-26` `E-HRN-27` `E-HRN-28` `E-HRN-29` `E-HRN-30` `E-HRN-31` `E-HRN-32` `E-TRN-21` |
| `harness` | — |
| `mechanisms` | `E-HRN-28` `E-HRN-29` |
| `transport` | — |
| `ground` | `E-AVN-09` |

## Connection types used

*Where*: `library` = `redesign/interfaces/connection_types.json` (A4-R3 additions marked +), else the subsystem that declares it locally.

| Id | Kind | Method | Where | Spec |
|---|---|---|---|---|
| `CT-AS150U` | electrical | connector | library + | Amass AS150U anti-spark pair (battery main; 70 A continuous, 140 A momentary per maker; packs re-terminated, D-32) |
| `CT-CA` | mechanical | bonded | library | cyanoacrylate bond (foam-safe CA where foam) |
| `CT-CARD-SLOT` | mechanical | press_fit | avionics | card pushed into a board-mounted push-push slot (microSD); the slot holds the card |
| `CT-CLEVIS` | kinematic | hinged | library + | steel pushrod end (Z-bend or clevis) in a horn or arm hole |
| `CT-CONN-PARK` | mechanical | bonded | power | connector half seated in a printed cradle: sanded housing bonded with 30 min epoxy, front wall takes the plug-in push, one cable tie over it as secondary retention |
| `CT-CRADLE-CONTACT` | mechanical | slid | library + | aircraft rests in a foam-lined cradle, no fastening (transport only) |
| `CT-ELRS-RF` | electrical | radio | library + | ExpressLRS 2.4 GHz radio link, CRSF to the FC (control and telemetry); no wire |
| `CT-EPOXY` | mechanical | bonded | library | epoxy bond (30 min laminating epoxy), surfaces scuffed |
| `CT-GEL-PAD` | mechanical | taped | library + | adhesive vibration-isolation gel pads (Zeal class, 5 mm) on a scuffed face, no screws; secondary tie or strap with slack |
| `CT-GER-CAP-TAPE` | mechanical | taped | landing | TPU cap pushed over the TE corner, two wraps of 12 mm filament tape over its legs onto the tape skin |
| `CT-GER-CRUSH-SLIDE` | kinematic | slid | landing | printed tine in printed sleeve, 0.2 mm/side; two 6.5 mm snap fingers with 0.6 mm hooks in 41.5 mm windows retain it through the 38 mm crush stroke; flange stops on the sleeve-end rim |
| `CT-GER-END-BEAR` | mechanical | slid | landing | crush cartridge slides in the sleeve and bears on the back wall in compression (0.5 mm preload, not bonded) |
| `CT-GER-PSA` | mechanical | bonded | landing | rubber sheet pressure-sensitive adhesive backing on a degreased printed face |
| `CT-HATCH-HL` | mechanical | strapped | library + | hatch: printed tongue under a fixed lip at one end, hook-and-loop tab at the other (tool-free, no magnets) |
| `CT-JST-GH-4` | electrical | connector | library + | JST-GH 4-pin (UART or I2C) |
| `CT-JST-GH-6` | electrical | connector | library | JST-GH 6-pin (telemetry / GPS) |
| `CT-LABEL` | mechanical | taped | library + | adhesive label on the skin (FAA number); not a load path |
| `CT-M2-SCREW-PLASTIC` | mechanical | fastened | library | M2 self-tapping or machine screw into printed/plastic boss (servo ears) |
| `CT-M3-PA66-NUT` | mechanical | fastened | pod | M3 PA66 (nylon) screw through a clearance hole, PA66 nut, finger tight + 1/4 turn (non-magnetic, near a compass; the screw is a fuse) |
| `CT-M3-SHCS-INSERT` | mechanical | fastened | library | M3 SHCS into M3 brass heat-set insert |
| `CT-M3-SHCS-MOTOR` | mechanical | fastened | library | M3 SHCS into motor base tapped hole (manufacturer pattern) |
| `CT-PITOT-TUBING` | mechanical | press_fit | library + | silicone tubing pushed on the pitot and sensor barbs, total and static lines (pneumatic); not a load path |
| `CT-PLUG-IN` | mechanical | slid | library + | boom pushed into a printed socket, keyed, retained by a detent or O-ring; tool-free field joint |
| `CT-PROP-ADAPTER` | mechanical | fastened | library + | bolt-on prop adapter, 4 x M3x4 SHCS into the motor bell, pilot on the shaft |
| `CT-PROP-NUT` | mechanical | fastened | library + | M6x1 nut and washer clamp the prop hub on the adapter post (field joint) |
| `CT-SERVO-EAR-SLOT` | mechanical | slid | mechanisms | servo mounting ears slid into slots in a printed frame, held by a screwed cover (no screws along the span: no tool access in a wing pocket) |
| `CT-SERVO-JR` | electrical | connector | library | JR/Futaba 3-pin servo connector |
| `CT-SERVO-SPLINE` | mechanical | fastened | library + | servo arm on the output spline, M2 retaining screw |
| `CT-SLIDE-STOP` | mechanical | slid | pod | loose printed spacer trapped between two stops |
| `CT-SNAP-CLIP` | mechanical | press_fit | power | bought part snapped into a printed clip (fuse holder), removable by hand |
| `CT-SOLDER-DC` | electrical | soldered | library + | soldered DC power joint, heat-shrink |
| `CT-SOLDER-PHASE` | electrical | soldered | library | soldered motor phase wires, heat-shrink |
| `CT-SPAR-TIE` | mechanical | strapped | pod | printed saddle bonded on a round spar + nylon cable tie round saddle and spar (7.6 mm, 50 lb class) |
| `CT-STRAP-SLOT` | mechanical | slid | library + | strap threaded through slots in a printed tray |
| `CT-STRAP-VELCRO` | mechanical | strapped | library | hook-and-loop strap + anti-slip pad |
| `CT-TAPE-FOAM` | mechanical | taped | library + | double-sided foam tape (3M VHB-class) + one cable tie as secondary retention |
| `CT-TAPE-HINGE` | kinematic | hinged | library | tape hinge (top surface), control surface |
| `CT-TAPE-SKIN` | mechanical | taped | library + | packing-tape skin or cover, spanwise strips, 10 % overlap |
| `CT-THERMAL-CONTACT` | thermal | conductive | library + | dry contact of a heat source on the part that carries it (conduction path; treated as insulating where the thermal block says so) |
| `CT-TIE` | mechanical | strapped | library + | cable tie to a tie point or round a tube; not a load path |
| `CT-TRN-CAM-STRAP` | mechanical | strapped | transport | 25 mm PP webbing with cam buckle around the box, through wall loops |
| `CT-TRN-LSE-TAPE` | mechanical | taped | transport | double-sided tape for low-surface-energy plastics (3M 300LSE class) on PP/PE, plus zip ties where stated |
| `CT-TRN-M3-BOLT` | mechanical | fastened | transport | M3 SHCS through handle strap and Coroplast wall, M3 x 12 mm fender washer outside, 3 mm plywood backing strip and nyloc inside |
| `CT-TRN-PLUG-LID` | mechanical | slid | transport | plug lid: folded lip inside the base walls, held closed by cam-buckle straps |
| `CT-TRN-POCKET` | mechanical | slid | transport | item sits in a cut foam pocket, no fastening |
| `CT-TRN-PRELOAD-PAD` | mechanical | slid | transport | foam pillar pressed onto the part by the closed lid (5 mm preload), no fastening |
| `CT-TUBE-CLAMP` | mechanical | clamped | library | printed split clamp around round tube, closed by fasteners listed in the joint stack |
| `CT-WIRE-CHANNEL` | mechanical | taped | library + | wires laid in a hot-wired or routed channel in the core, closed with tape; not a load path |

<!-- END GENERATED REGISTER -->

## Data interfaces without a physical edge

`flight-software` has no parts. Its inputs live in the edges above, so the parameter file reads one source.

| Interface | Data | Lives in | Supplied by | Read by |
|---|---|---|---|---|
| Motor map | station `UR UL LR LL` → FC output → ArduPilot motor number (X frame), prop CW/CCW, LH adapters on the CW motors | `signal.fc_port` on `E-HRN-24…27`; notes on `E-PRP-05…08` (E1 declares rotation and thread per station) | E1 (rotation), F2 (ports) | F4 |
| Elevon outputs | FC output, direction, trim, throw ±25° | `signal.fc_port` on `E-HRN-28/29`; `motion` on `E-WNG-04…07` | D6 | F4 |
| Board orientation | FC arrow vs frame (nose up in hover) | notes on `E-AVN-01` | F3 | F4 (`AHRS_ORIENTATION`) |
| Compass orientation | arrow on the mast, 45° toward the nose | notes on `E-AVN-02` | F3 | F4 (`COMPASS_ORIENT`) |
| Battery monitor | volts and amps per volt of the CoreWing power board (64 A/V) | `signal` on `E-HRN-23` | F1 · F3 | F4 (`BATT_*`) |
| Airspeed | MS4525DO, I2C1, 0x28, total/static line order | `signal` on `E-HRN-32`; notes on `E-AVN-06` | F3 | F4 (`ARSPD_TYPE 1`) |
| RC and telemetry | SERIAL6, CRSF 420 kbaud; ELRS 2.4 GHz at 25 mW, telemetry over the same link | `signal` on `E-HRN-31`, `E-AVN-09` | F5 | F4 (`SERIALn_*`, `RSSI_*`) |
| Mass properties | mass, CG, inertia | part `mass_g`, `cg_xyz_m` | every owner, A3 rolls up | B3, F4, viewer |

## Clearances and keep-outs

Not joints, so not edges: each is a number a designer must hold and a check that proves it.

| Keep-out | Between | Minimum | Now | Source | Status | Owner |
|---|---|---|---|---|---|---|
| Prop disc | any prop tip ↔ structure or prop | 25 mm | per B4/D3 at R3 (7° mounts) | `P:requirements.prop_clearance_min_m`, `CL-A1-PROP-CLEAR` | `UNVERIFIED` | B4 · D3 |
| Prop wash | pitot tip `P:avionics.pitot_tip_xyz_m` (−0.195, −0.046, 0.045), GPS mast ↔ prop discs | outside the disc + wash | B4 re-runs at y −0.046 | `CL-B4-PITOT` | `PROPOSED` | B4 · F3 |
| Link slot | inter-panel link ↔ lower half-fin root, slot x 0.2376–0.2616, 12 mm below the skin, ±25° | slot clears the full sweep | declared by D3 (`FIN-001-LR/LL` "link slot") | OI-03, CR-D3-05 | `PROPOSED` | D6 · D3 |
| Elevon end gaps | panel ends ↔ half-fin faces | > 0 at ±25° | — | `params.json#wing.elevon` | `PROPOSED` | D6 · D3 |
| Wing TE to ground | wing TE ↔ ground plane at the foot pads | > 0 after a full crush on grass | 32 mm crush stroke (D5); wing caps `GER-007-L/R` | `P:cg.foot_height_m`, OI-05 | `UNVERIFIED` | D5 · C5 · A1 |
| Compass | GPS compass ↔ power leads, PDB, UBEC; no steel within 50 mm | ratio per F3 | 0.154 m to the nearest power item; brass/nylon mast screw | `team/F3/AVIONICS.md` | `PROPOSED` | F3 · D2 |
| Antennas | RX antennas ↔ CF spar and tubes; ↔ GPS | ≥ 30 mm; ≥ 60 mm | per F3 placement | `T-F5-RANGE` | `PROPOSED` | F5 · F3 |
| ESC leads | ESC power leads ↔ mast top | ≥ 0.12 m | F1 routing | `team/F1/POWER.md` | `PROPOSED` | F2 · F1 |
| Pushrod | pushrod ↔ skin and servo cover through full throw | — | — | `E-MEC-07…10` | `PROPOSED` | D6 |
| Box | box walls, cradles, pillars ↔ half-fins, tubes, motors | no contact (`check.py` overlap check; stowed parts exempt) | box 1.25 × 0.55 × 0.54 m (D-31) | `CL-A1-BOX-FIT`, `CAR-FIT.md` | `PROPOSED` (two cars before the freeze) | D7 |

## Open interface issues

| Id | Issue | Edges | Owner(s) | Close by |
|---|---|---|---|---|
| OI-01 | Motor-mount slip collar is the D-23 fuse: slip 2.5 N·m set by `T-D3-SLIP`, ASA so the preload does not relax at 66 °C (D-42); `clamp` block declared by D3 from C6 | `E-FIN-05…08` | D3 · C4 · C6 | `T-D3-SLIP` |
| OI-02 | Through-core block: blocks threaded on the spar and jig-set at y = ±0.320 before the spar is bonded; core cut-out x 0.028–0.097 (D1 cuts it); pending until `WNG-001/002` are declared | `E-FIN-49…52` | D3 · D1 · C2 | D1 declares the wing |
| OI-03 | Inter-panel link crosses the lower half-fin root at the hinge line; D3 has cut the slot, D6 must confirm the link path and ±25° sweep (CR-D3-05) | `E-WNG-04…07`, `E-MEC-13…16`, `FIN-001-LR/LL` | D6 · D3 | D6 R3 |
| OI-04 | Wire route pod → fins: ESC leads 16 AWG in two taped surface grooves 5 mm apart, ≥ 0.12 m from the mast top (F1); must clear the spar slot and the anchor pockets at y ±0.242 | `E-HRN-02…05`, `E-HRN-13…16`, `E-HRN-28/29` | F2 · D1 · D3 | F2's first harness release |
| OI-05 | Landing: crush cartridge 32 mm stroke; wing caps `GER-007-L/R` taped to the core protect the TE; on grass the TE margin after a full crush is still `UNVERIFIED` | `E-GER-01…22` | D5 · C5 | `T-D5-COUPON`, C5 landing case |
| OI-06 | ESC on a half-fin pad in the prop wash; motor lead length decides a ≤ 100 mm phase extension; mount and pad in ASA (D-42) | `E-FIN-45…48`, `E-FIN-65…68`, `E-FIN-81…88`, `E-HRN-17…20` | E1 · E3 · D3 | GT-04 (H1) |
| OI-10 | Answered by F3/F5: telemetry through ELRS (no separate radio); antenna and compass placement rules in `team/F3/AVIONICS.md`; closes when `T-F5-RANGE` and a compass calibration pass | `E-AVN-02/03/09`, `E-HRN-31` | F3 · F5 | `T-F5-RANGE` |
| OI-12 | Plug-in pitot boom: barbed couplers at the boom root part when it is pulled; the socket carries the boom's bending load in a nose-first tip-over | `E-AVN-05`, `E-AVN-06`, `E-POD-07`, `E-TRN-21` | F3 · D2 | pod design |
| OI-13 | Wing features the R3 fins need: spar plugs under the blocks and at the anchors (count: C2 says 6, A3 books 2 + 4, this plan 2 + 2), anchor pockets 20 × 16 mm through skin and core at y ±0.242 top and bottom | `E-FIN-49/50`, `E-FIN-57…60`, `E-WNG-08…11` | D1 · C2 · A3 | D1 declares the wing |
| OI-14 | Prop adapter screws: E1 declares 2.5 mm engagement against a 2.0 mm minimum; D-41 (1.0 d into metal) and C6 give 3.0 mm | `E-PRP-01…04` | E1 · C6 | E1 measures the bell thread depth (`T-E1-MOTOR-RM`) |
| OI-15 | Fuse `PWR-007` and ESC caps `PWR-008-*` have no wire: F2 has not applied CR-F1-18 (split `E-HRN-21`, cap leads, 10 AWG main jumpers) | `E-HRN-11/12/21`, `E-HRN-33…37` | F2 · F1 | F2 re-runs `harness.py` |
| OI-16 | Take-off CG x 0.0577 m vs aft limit 0.055 m (0.0550 B3 R2): 2.7 mm aft with every subsystem declared; forward pack room 3 mm | merged graph `cg` ERROR | A1 · A3 · B3 · D2 | A1 decision (pod group −16 mm or stations −27 mm or ballast) |

Closed in A4-R3: OI-08 (I2C: MS4525DO at 0x28, no clash with the board barometer, F3), OI-09 (AS150U, D-32).
Closed earlier: OI-07 (D-15), OI-11 (D-20).

## Tooling changes in `redesign/interfaces/`

| # | Change | Status |
|---|---|---|
| 1 | `SCHEMA.md`: frame from `params.json#frame`; K09-L folders and prefixes; `9xx` reserved for the skeleton; `mass_budget.json` exists | done A4-R2 (CR-A5-04, CR-IF-01, CR-IF-02) |
| 2 | `connection_types.json`: the 19 plan types + `CT-AS150U`, `CT-GEL-PAD`, `CT-ELRS-RF`; owner text verbatim where an owner declared first (pod, propulsion, transport); `CT-THERMAL-CONTACT` widened to every heat source; keeper A4 | done A4-R3 (D-46) |
| 3 | `merge_check.py`: no `owner` warning on a `harness` electrical edge (D-20) | done A4-R3 (D-46) |
| 4 | `SCHEMA.md`: D-20 ownership and supply-side rule; per-unit mass and instance-id rule; A4 blocks; K09-L example | done A4-R2 (CR-A1-18, CR-A3-09) |
| 5 | `merge_check.py` floating check: `"structural": false` types do not hold a part; a part flagged `"carried": true` held only by them is exempt | done A4-R3 (D-46) |
| 6 | `merge_check.py` power check: `unpowered` follows power wires `part_a` → `part_b`, skipping `signal_only` and radio | done A4-R3 (D-46) |
| 7 | `merge_check.py`: method `radio` (no wire block); `SCHEMA.md`: `stowed` (CR-A5-10), `carried`, `edges_pending`, `C` and `I/O` suffixes, `ground` subsystem, R3 example | done A4-R3 |

Regression after the change (2026-11-09): `merge_check.py --examples` PASS 0/0; `fusion/tests/test_framework.py`
27 tests OK; `test_merge_check_d46.py` 11/11. A5 re-runs `fusion/tests` and `check.py --strict` (D-46).

## How to verify

| Check | Command (repo root) | Pass |
|---|---|---|
| Integration (all checks) | `python -I redesign/team/A4/integration_check.py` → `team/A4/INTEGRATION-CHECK.md` | merge, after-re-run, `check.py`, roll-up, compare all PASS |
| Plan is consistent | `python -I redesign/team/A4/interface_plan.py` | `PASS`, connected 100 %, powered 100 %, 1 field disconnect, 0 id-rule breaches |
| Plan checks catch faults | `python -I redesign/team/A4/test_interface_plan.py` | 16 seeded faults caught, baseline clean |
| merge_check D-46 rules | `python -I redesign/team/A4/test_merge_check_d46.py` | 10 seeded cases + clean baseline |
| Real graph vs plan | `python -I redesign/team/A4/interface_plan.py --compare` → `team/A4/PLAN-STATUS.md` | 0 missing, 0 owed, deviations explained |
| Real graph | `python -I redesign/interfaces/merge_check.py --strict` | 0 errors, 0 warnings |
| CAD | `python -I redesign/fusion/check.py` | every edge registered, nothing floats |
| Proof chain | `python -I redesign/proofs/build_graph.py` | no drift on `CALC-A4-PLAN-GRAPH` |
