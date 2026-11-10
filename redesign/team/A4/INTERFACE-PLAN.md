# Interface plan — K09-L quad tailsitter

Status: `PROPOSED`, plan revision **A4-R3** on design frame A1-R3 (A4, 2026-11-09). Every part id and every joint
the aircraft needs, who declares it, who acknowledges it, who designs and sizes it, and the data it must carry.
Owners copy their rows into `subsystems/<key>/interfaces.json` (schema `redesign/interfaces/SCHEMA.md`); A4 merges
with `redesign/interfaces/merge_check.py` and compares against this plan with `interface_plan.py --compare`.
Source of the tables below: `redesign/team/A4/interface_plan.py` plus the frozen declarations in
`baseline-R3.json` (machine copy of the whole plan: `interface_plan.json`).

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

Generated by `python -I redesign/team/A4/interface_plan.py` from the plan in that script and `baseline-R3.json`. Do not edit by hand.

| Parts (flight) | Interfaces | Cross-subsystem | Declared (pending) | Mech · elec · kin · thermal | Connected (load path) | Powered (power wires) | Field disconnects (field joints) | Stowed | Id-rule breaches | Plan errors | Schema blocks owed | Masses owed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 139 (125) | 222 | 97 | 137 (12) | 176 · 24 · 12 · 10 | 100 % | 100 % | 1 (7) | 5 | 0 | 0 | 44 | 125 |

## N² matrix

Interfaces between each pair of subsystems (diagonal: internal joints). Read a row: who this subsystem must agree with. Wires count under the two subsystems they join; harness (`HRN`) declares all 23 of them (D-20); the radio link `E-AVN-09` is an avionics edge.

| | WNG | FIN | POD | GER | PRP | PWR | AVN | HRN | MEC | TRN | GND |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **WNG** | 11 | 12 | 2 | 2 | · | · | · | 2 | 10 | 4 | · |
| **FIN** | 12 | 60 | · | 4 | 16 | · | · | 2 | · | · | · |
| **POD** | 2 | · | 8 | · | · | 6 | 7 | 1 | · | · | · |
| **GER** | 2 | 4 | · | 16 | · | · | · | · | · | · | · |
| **PRP** | · | 16 | · | · | 12 | 4 | 4 | · | · | 4 | · |
| **PWR** | · | · | 6 | · | 4 | 4 | 2 | · | · | · | · |
| **AVN** | · | · | 7 | · | 4 | 2 | 5 | · | 2 | 1 | 1 |
| **HRN** | 2 | 2 | 1 | · | · | · | · | · | · | · | · |
| **MEC** | 10 | · | · | · | · | · | 2 | · | 8 | · | · |
| **TRN** | 4 | · | · | · | 4 | · | 1 | · | · | 12 | · |
| **GND** | · | · | · | · | · | · | 1 | · | · | · | · |

## Part ids reserved

One node per physical instance, id `<PREFIX>-NNN-<UR|UL|LR|LL|L|R|C>[I|O]`; all instances of a part are one `parts.csv` line with `mass_g` per unit (CR-A3-09). Stations `UR UL LR LL` = upper/lower, right/left (`params.json#propulsion.stations.ids`); a half-fin takes the station it carries; `C` = centre; `I`/`O` = inboard/outboard face of the same part at one station (A4-R3). `NNN` 001–899; `9xx` is reserved for `fusion/skeleton/` (CR-A5-04). *Declared* = taken from the owner's `interfaces.json` into `baseline-R3.json`.

| Subsystem | Designer | Prefix | Parts | Declared | Ids |
|---|---|---|---|---|---|
| `wing` | D1 | `WNG` | 12 | 0 | `WNG-001` `WNG-002` `WNG-003` `WNG-004-L` `WNG-005-L` `WNG-004-R` `WNG-005-R` `WNG-011-L` `WNG-012-L` `WNG-011-R` `WNG-012-R` `WNG-020` |
| `fins` | D3 | `FIN` | 42 | 42 | `FIN-001-UR` `FIN-001-UL` `FIN-001-LR` `FIN-001-LL` `FIN-002-R` `FIN-002-L` `FIN-003-UR` `FIN-003-UL` `FIN-003-LR` `FIN-003-LL` `FIN-004-R` `FIN-004-L` `FIN-006-R` `FIN-006-L` `FIN-007-UR` `FIN-007-UL` `FIN-007-LR` `FIN-007-LL` `FIN-008-UR` `FIN-008-UL` `FIN-008-LR` `FIN-008-LL` `FIN-009-UR` `FIN-009-UL` `FIN-009-LR` `FIN-009-LL` `FIN-010-UR` `FIN-010-UL` `FIN-010-LR` `FIN-010-LL` `FIN-011-URO` `FIN-011-URI` `FIN-011-ULO` `FIN-011-ULI` `FIN-011-LRO` `FIN-011-LRI` `FIN-011-LLO` `FIN-011-LLI` `FIN-012-UR` `FIN-012-UL` `FIN-012-LR` `FIN-012-LL` |
| `pod` | D2 | `POD` | 8 | 8 | `POD-001` `POD-002` `POD-003` `POD-004` `POD-005` `POD-006` `POD-007` `POD-008` |
| `landing` | D5 | `GER` | 18 | 18 | `GER-001-UR` `GER-001-UL` `GER-001-LR` `GER-001-LL` `GER-002-UR` `GER-002-UL` `GER-002-LR` `GER-002-LL` `GER-003-UR` `GER-003-UL` `GER-004-UR` `GER-004-UL` `GER-004-LR` `GER-004-LL` `GER-007-R` `GER-007-L` `GER-008-LR` `GER-008-LL` |
| `propulsion` | E1 | `PRP` | 16 | 16 | `PRP-001-UR` `PRP-002-UR` `PRP-003-UR` `PRP-004-UR` `PRP-001-UL` `PRP-002-UL` `PRP-003-UL` `PRP-004-UL` `PRP-001-LR` `PRP-002-LR` `PRP-003-LR` `PRP-004-LR` `PRP-001-LL` `PRP-002-LL` `PRP-003-LL` `PRP-004-LL` |
| `power` | F1 | `PWR` | 5 | 0 | `PWR-001` `PWR-002` `PWR-003` `PWR-004` `PWR-005` |
| `avionics` | F3 | `AVN` | 7 | 0 | `AVN-001` `AVN-002` `AVN-003` `AVN-004` `AVN-005` `AVN-006` `AVN-007` |
| `harness` | F2 | `HRN` | 3 | 0 | `HRN-001` `HRN-002-L` `HRN-002-R` |
| `mechanisms` | D6 | `MEC` | 14 | 0 | `MEC-001-L` `MEC-002-L` `MEC-003-L` `MEC-004-L` `MEC-005-L` `MEC-007-L` `MEC-008-L` `MEC-001-R` `MEC-002-R` `MEC-003-R` `MEC-004-R` `MEC-005-R` `MEC-007-R` `MEC-008-R` |
| `transport` | D7 | `TRN` | 13 | 13 | `TRN-001` `TRN-005` `TRN-002-L` `TRN-002-R` `TRN-003` `TRN-004-L` `TRN-004-R` `TRN-006-L` `TRN-006-R` `TRN-007-C` `TRN-007-L` `TRN-007-R` `TRN-008` |
| `ground` | F5 | `GND` | 1 | 0 | `GND-001` |
| `flight-software` | F4 | `FSW` | 0 | — | no parts: data interfaces below |

Retired ids (never reuse): `FIN-001-L` split into half-fins FIN-001-UL / -LL (D-04); `FIN-001-R` split into FIN-001-UR / -LR (D-04); `FIN-005-L` clip set per half-fin (R2), retired in R3; `FIN-005-R` clip set per half-fin (R2), retired in R3; `FIN-005-UR` clip sets retired in R3: station collars FIN-008 + edge strips FIN-011 (D3); `FIN-005-UL` clip sets retired in R3; `FIN-005-LR` clip sets retired in R3; `FIN-005-LL` clip sets retired in R3; `TRN-004` hold-down strap replaced by lid pillars TRN-004-L/R (CR-D7-03); `TRN-006-A` rename to TRN-006-L (side family, CR-A4-24); `TRN-006-B` rename to TRN-006-R (CR-A4-24).

## Interface register

Declared by the owner in `subsystems/<owner>/interfaces.json`; each subsystem in *Ack* lists the id under `acknowledges`. *By* = designs · sizes. *Decl.* = in the R3 baseline (`yes`), parked in the owner's `edges_pending` (`pending`), or still to declare (`—`). *C6* = blocks C6 has written in `team/C6/joint_stacks.json` for the owner to copy. *Must carry* is in addition to the per-method block above (for declared edges: the owner's notes, shortened). `OI-nn` = open issue below.

### wing (D1, 11)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-WNG-01` | `WNG-002` Spar CF 22x20x1000 | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | — | D1 · C2 | — | — | slot fit (22.2 mm `EST`), bond length 1 000 mm, spar centre z +0.0066 m (D-43), spar bending load into core; blocks threaded on the spar before it is bonded (E-FIN-49/50) |
| `E-WNG-02` | `WNG-003` Tape skin | `WNG-001` Wing core, one piece (XPS) | mechanical · taped · `CT-TAPE-SKIN` | — | D1 · G2 | — | — | strip layout, overlap 10 %, wrap at LE/TE; laps 15 mm up the half-fin roots |
| `E-WNG-03` | `WNG-020` FAA registration label | `WNG-003` Tape skin | mechanical · taped · `CT-LABEL` | — | D1 · H3 | — | — | position visible without tools (FAA) |
| `E-WNG-04` | `WNG-011-L` Elevon inboard L | `WNG-001` Wing core, one piece (XPS) | kinematic · hinged · `CT-TAPE-HINGE` | — | D6 designs · B2 hinge moment | — | — | motion Y [-25, 25]°; hinge line x 0.2496 m, panel y 0.07–0.30 m, end gap to the half-fin, throw ±25° to stops (OI-03) |
| `E-WNG-05` | `WNG-012-L` Elevon outboard L | `WNG-001` Wing core, one piece (XPS) | kinematic · hinged · `CT-TAPE-HINGE` | — | D6 designs · B2 hinge moment | — | — | motion Y [-25, 25]°; hinge line x 0.2496 m, panel y 0.34–0.56 m, end gap to the half-fin, throw ±25° to stops (OI-03) |
| `E-WNG-06` | `WNG-011-R` Elevon inboard R | `WNG-001` Wing core, one piece (XPS) | kinematic · hinged · `CT-TAPE-HINGE` | — | D6 designs · B2 hinge moment | — | — | motion Y [-25, 25]°; hinge line x 0.2496 m, panel y 0.07–0.30 m, end gap to the half-fin, throw ±25° to stops (OI-03) |
| `E-WNG-07` | `WNG-012-R` Elevon outboard R | `WNG-001` Wing core, one piece (XPS) | kinematic · hinged · `CT-TAPE-HINGE` | — | D6 designs · B2 hinge moment | — | — | motion Y [-25, 25]°; hinge line x 0.2496 m, panel y 0.34–0.56 m, end gap to the half-fin, throw ±25° to stops (OI-03) |
| `E-WNG-08` | `WNG-004-L` Spar plug under the through-core block L (PETG) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | C2 · D1 | — | — | plug 19.8 × 36 mm inside the spar under the block at /y/ 0.320 (bearing for E-FIN-49/50) (OI-13) |
| `E-WNG-09` | `WNG-004-R` Spar plug under the through-core block R (PETG) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | C2 · D1 | — | — | plug 19.8 × 36 mm inside the spar under the block at /y/ 0.320 (bearing for E-FIN-49/50) (OI-13) |
| `E-WNG-10` | `WNG-005-L` Spar plug at the brace anchors L (PETG) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | C2 · D1 | — | — | plug 19.8 × 20 mm inside the spar at the anchor station /y/ 0.242 (E-FIN-57…60) (OI-13) |
| `E-WNG-11` | `WNG-005-R` Spar plug at the brace anchors R (PETG) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | — | C2 · D1 | — | — | plug 19.8 × 20 mm inside the spar at the anchor station /y/ 0.242 (E-FIN-57…60) (OI-13) |

### fins (D3, 88)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-FIN-01` | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes) | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | tube through the block socket bore (22.3 mm, 47 mm long with the bosses), 30 min epoxy, tube scuffed 120 grit |
| `E-FIN-02` | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes) | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | tube through the block socket bore (22.3 mm, 47 mm long with the bosses), 30 min epoxy, tube scuffed 120 grit |
| `E-FIN-03` | `FIN-006-R` Tube plug R, CF 20x18 x 53 mm inside the tube at the block | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | plug pushed in from the tube end to z -0.020..0.033 with a rod, laminating epoxy, before the collars and mounts |
| `E-FIN-04` | `FIN-006-L` Tube plug L, CF 20x18 x 53 mm inside the tube at the block | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | plug pushed in from the tube end to z -0.020..0.033 with a rod, laminating epoxy, before the collars and mounts |
| `E-FIN-05` | `FIN-003-UR` Motor mount UR, ASA, 7 deg canted plate, slip clamp (print A) | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-06` | `FIN-003-UL` Motor mount UL, ASA, 7 deg canted plate, slip clamp (print B) | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-07` | `FIN-003-LR` Motor mount LR, ASA, 7 deg canted plate, slip clamp (print B) | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-08` | `FIN-003-LL` Motor mount LL, ASA, 7 deg canted plate, slip clamp (print A) | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · clamped · `CT-TUBE-CLAMP` | — | D3 | yes | clamp joint_stack | ASA slit collar, 12 mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the block or tube is overloaded); paint-pen witness line across collar and tube (OI-01) |
| `E-FIN-09` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes) | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block upper bore boss, 30 min epoxy |
| `E-FIN-10` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes) | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block upper bore boss, 30 min epoxy |
| `E-FIN-11` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes) | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block lower bore boss, 30 min epoxy |
| `E-FIN-12` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes) | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | laminate root LE in the 10.0 mm slot of the block lower bore boss, 30 min epoxy |
| `E-FIN-13` | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-14` | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-15` | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-16` | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | station collar ring 16 mm bonded on the tube directly under the mount, tail aft, ear inboard |
| `E-FIN-17` | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-18` | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-19` | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-20` | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch bottom and aft edges; the strips cover both faces |
| `E-FIN-21` | `FIN-011-URO` Edge strip upper right outboard face, CF 10 x 1 | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UR after cure |
| `E-FIN-22` | `FIN-011-URI` Edge strip upper right inboard face, CF 10 x 1 | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UR after cure |
| `E-FIN-23` | `FIN-011-ULO` Edge strip upper left outboard face, CF 10 x 1 | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UL after cure |
| `E-FIN-24` | `FIN-011-ULI` Edge strip upper left inboard face, CF 10 x 1 | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-UL after cure |
| `E-FIN-25` | `FIN-011-LRO` Edge strip lower right outboard face, CF 10 x 1 | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LR after cure |
| `E-FIN-26` | `FIN-011-LRI` Edge strip lower right inboard face, CF 10 x 1 | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LR after cure |
| `E-FIN-27` | `FIN-011-LLO` Edge strip lower left outboard face, CF 10 x 1 | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LL after cure |
| `E-FIN-28` | `FIN-011-LLI` Edge strip lower left inboard face, CF 10 x 1 | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip bonded along the sloped top edge (229 mm), 30 min epoxy, paper scuffed 220 grit; pinned with FIN-012-LL after cure |
| `E-FIN-29` | `FIN-011-URO` Edge strip upper right outboard face, CF 10 x 1 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-30` | `FIN-011-URI` Edge strip upper right inboard face, CF 10 x 1 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-31` | `FIN-011-ULO` Edge strip upper left outboard face, CF 10 x 1 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-32` | `FIN-011-ULI` Edge strip upper left inboard face, CF 10 x 1 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-33` | `FIN-011-LRO` Edge strip lower right outboard face, CF 10 x 1 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-34` | `FIN-011-LRI` Edge strip lower right inboard face, CF 10 x 1 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-35` | `FIN-011-LLO` Edge strip lower left outboard face, CF 10 x 1 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-36` | `FIN-011-LLI` Edge strip lower left inboard face, CF 10 x 1 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | strip forward end 40 mm in the collar-tail slot between the tongue and the outer wall, both strip faces bonded to PETG (CR-C6-01) |
| `E-FIN-37` | `FIN-009-UR` Brace UR, CF strip 10 x 2 | `FIN-008-UR` Station collar UR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-38` | `FIN-009-UL` Brace UL, CF strip 10 x 2 | `FIN-008-UL` Station collar UL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-39` | `FIN-009-LR` Brace LR, CF strip 10 x 2 | `FIN-008-LR` Station collar LR, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-40` | `FIN-009-LL` Brace LL, CF strip 10 x 2 | `FIN-008-LL` Station collar LL, 16 mm, 40 mm two-face tail + brace ear | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the ear slot (2.2 x 10.4 mm), 30 min epoxy |
| `E-FIN-41` | `FIN-009-UR` Brace UR, CF strip 10 x 2 | `FIN-010-UR` Brace anchor UR on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-42` | `FIN-009-UL` Brace UL, CF strip 10 x 2 | `FIN-010-UL` Brace anchor UL on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-43` | `FIN-009-LR` Brace LR, CF strip 10 x 2 | `FIN-010-LR` Brace anchor LR on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-44` | `FIN-009-LL` Brace LL, CF strip 10 x 2 | `FIN-010-LL` Brace anchor LL on the spar at |y| 0.242 | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | bond | brace end 10 mm in the anchor slot, 30 min epoxy |
| `E-FIN-45` | `FIN-007-UR` ESC pad UR, ASA, on the outboard face of half-fin UR | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-46` | `FIN-007-UL` ESC pad UL, ASA, on the outboard face of half-fin UL | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-47` | `FIN-007-LR` ESC pad LR, ASA, on the outboard face of half-fin LR | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-48` | `FIN-007-LL` ESC pad LL, ASA, on the outboard face of half-fin LL | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | ASA pad on the outboard laminate face, 30 min epoxy |
| `E-FIN-49` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | spar through the block spar bore (22.3 mm, 36 mm long, C2 plug inside the spar); blocks threaded on the spar and set by jig at y = +/-0.320 before the spar is bonded into the core (CL-C4-D3-BLOCK-MS) (OI-02) |
| `E-FIN-50` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes) | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | spar through the block spar bore (22.3 mm, 36 mm long, C2 plug inside the spar); blocks threaded on the spar and set by jig at y = +/-0.320 before the spar is bonded into the core (CL-C4-D3-BLOCK-MS) (OI-02) |
| `E-FIN-51` | `FIN-004-R` Through-core block R (tube socket + spar saddle + 2 strap eyes) | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | block bonded into the core cut-out x 0.028-0.097, y 0.320 +/- 0.018, full depth (D1 cuts it); tape skin over (OI-02) |
| `E-FIN-52` | `FIN-004-L` Through-core block L (tube socket + spar saddle + 2 strap eyes) | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | block bonded into the core cut-out x 0.028-0.097, y 0.320 +/- 0.018, full depth (D1 cuts it); tape skin over (OI-02) |
| `E-FIN-53` | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-54` | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-55` | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-56` | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | laminate root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both faces (L-angle); root contour from the S5010 section |
| `E-FIN-57` | `FIN-010-UR` Brace anchor UR on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | anchor foot bonded on the spar top face through a 20 x 16 mm pocket in skin and core at y +0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-58` | `FIN-010-UL` Brace anchor UL on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | anchor foot bonded on the spar top face through a 20 x 16 mm pocket in skin and core at y -0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-59` | `FIN-010-LR` Brace anchor LR on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | anchor foot bonded on the spar bottom face through a 20 x 16 mm pocket in skin and core at y +0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-60` | `FIN-010-LL` Brace anchor LL on the spar at |y| 0.242 | `WNG-002` Spar CF 22x20x1000 | mechanical · bonded · `CT-EPOXY` | wing | D3 | pending | bond | anchor foot bonded on the spar bottom face through a 20 x 16 mm pocket in skin and core at y -0.242 (D1 cuts it, C2 plug inside the spar); thickened epoxy fills the saddle (OI-13) |
| `E-FIN-61` | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | `FIN-003-UR` Motor mount UR, ASA, 7 deg canted plate, slip clamp (print A) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-62` | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-UL` Motor mount UL, ASA, 7 deg canted plate, slip clamp (print B) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-63` | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | `FIN-003-LR` Motor mount LR, ASA, 7 deg canted plate, slip clamp (print B) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-64` | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | `FIN-003-LL` Motor mount LL, ASA, 7 deg canted plate, slip clamp (print A) | mechanical · fastened · `CT-M3-SHCS-MOTOR` | propulsion | D3 | yes | joint_stack | motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x 0.0308 on the axis |
| `E-FIN-65` | `PRP-002-UR` ESC UR LANRC 45 A | `FIN-007-UR` ESC pad UR, ASA, on the outboard face of half-fin UR | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-66` | `PRP-002-UL` ESC UL LANRC 45 A | `FIN-007-UL` ESC pad UL, ASA, on the outboard face of half-fin UL | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-67` | `PRP-002-LR` ESC LR LANRC 45 A | `FIN-007-LR` ESC pad LR, ASA, on the outboard face of half-fin LR | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-68` | `PRP-002-LL` ESC LL LANRC 45 A | `FIN-007-LL` ESC pad LL, ASA, on the outboard face of half-fin LL | mechanical · strapped · `CT-STRAP-VELCRO` | propulsion | D3 | yes | — | ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02) |
| `E-FIN-69` | `FIN-012-UR` Edge-strip pin set UR, 12 x CF rod 2 mm | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-70` | `FIN-012-UL` Edge-strip pin set UL, 12 x CF rod 2 mm | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-71` | `FIN-012-LR` Edge-strip pin set LR, 12 x CF rod 2 mm | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
| `E-FIN-72` | `FIN-012-LL` Edge-strip pin set LL, 12 x CF rod 2 mm | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | — | D3 | yes | — | 12 pins 2 mm drilled through strip-laminate-strip every 15 mm along the strip after the strips cure, bonded flush (CR-C6-02) |
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
| `E-POD-01` | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D2 | yes | bond | shell floor, XPS LE filler, side walls and aft wall bonded to bare, sanded foam: D1 cuts the recess (x_rec0 ... x_rec1, z = pod base, full pod width) and leaves the tape skin off under the pod (CR-C2- |
| `E-POD-02` | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | bond | tray (with the forward stop), FC, avionics and PDB plates epoxied full-area to the foam-board floor (paper face scuffed); floor-to-side-wall fillets over x -0.100 ... 0 (CR-C3-01) |
| `E-POD-03` | `POD-003` Hatch (foam board, printed tongue, 12 x 40 hook-and-loop tab, antenna tube A) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · strapped · `CT-HATCH-HL` | — | D2 | yes | — | opened every flight, tool-free, no magnets; the hatch carries no pack load |
| `E-POD-04` | `POD-004` Pack straps (2, 20 mm hook-and-loop, rubber-backed) + 2 EVA pads 2.5 mm | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · slid · `CT-STRAP-SLOT` | — | D2 | yes | — | each strap passes down a slot, under the tray in a 1 mm groove cut in the foam floor, up the other slot |
| `E-POD-05` | `PWR-001` Flight pack 4S (re-terminated AS150U) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · strapped · `CT-STRAP-VELCRO` | power | D2 | yes | — | field joint; field joint. z/y: 2 straps + guides + EVA pads; fore-aft: crush block + spreader ahead (on the forward stop, x -0.1002), U-spacers + aft stop (x 0.077, on the handle bridge) behind. Nominal centroid x |
| `E-POD-06` | `POD-005` GPS mast with 45 deg pad (printed PETG, plugs into the handle grip) | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | mechanical · fastened · `CT-M3-BRASS-NUT` | — | D2 | yes | joint_stack | mast plugs 8 mm into the grip socket; cross-bolted with brass hardware (F3: no steel within 50 mm of the compass, the bolt is about 0.06 m from the GPS); 6.5 mm counterbore 4.5 deep on +y keeps the gr |
| `E-POD-07` | `POD-006` Pitot boom socket with 32 mm flange (printed PETG, pod nose, left channel) | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | — | socket through a 12 mm square hole in the nose wall; 32 x 32 mm flange bonded to the wall inside face (CR-C6-09); the nose block is cut round the flange; boom bending (1 kg on the tip in handling, 0.8 (OI-12) |
| `E-POD-08` | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | `POD-001` Pod shell (foam-board box, XPS LE filler and nose block, printed nose lip and antenna tube) | mechanical · bonded · `CT-EPOXY` | — | D2 | yes | — | handle legs pass through 7.8 mm slots in the aft deck at y +/-0.048, bonded: locates the deck |
| `E-POD-09` | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | `WNG-002` Spar CF 22x20x1000 | mechanical · strapped · `CT-SPAR-TIE` | wing | D2 | yes | — | carry point on the spar (D-23): feet saddle the spar top in the open slot (y 0.029 ... 0.053), bonded (scuffed CF, 30 min epoxy), one 7.6 mm nylon tie per foot at y +/-0.036 laid under the spar before |
| `E-POD-10` | `POD-008` Trim kit: XPS crush block (cut per pack), 1.5 mm PETG spreader, PETG U-spacers 2 / 4 / 8 / 8 mm | `POD-007` Carry handle on the spar with the aft stop bridge (printed PETG) + 'LIFT HERE - do not lift by the motors' label | mechanical · slid · `CT-SLIDE-STOP` | — | D2 | yes | — | U-spacers stand between the pack aft face and the aft stop, held by the pack; the pack leads pass over them |
| `E-POD-11` | `POD-008` Trim kit: XPS crush block (cut per pack), 1.5 mm PETG spreader, PETG U-spacers 2 / 4 / 8 / 8 mm | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · slid · `CT-SLIDE-STOP` | — | D2 | yes | — | crush block (with the spreader on the pack fore face) against the 3 mm forward stop, between the guides; cut per pack (length = pack fore face - 1.5 mm - (-0.1002)); in a nose-in crash the stop breaks |
| `E-POD-12` | `PWR-001` Flight pack 4S (re-terminated AS150U) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | thermal · conductive · `CT-THERMAL-CONTACT` | power | E3 · D2 | — | — | insulating; pack 47.1 °C at landing (`CL-E3-PACK-END`) vs 50 °C life; take-off ≤ 34 °C; two pod vents |

### landing (D5, 22)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-GER-01` | `GER-001-UR` Foot shoe UR | `FIN-001-UR` Half-fin upper right, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 10 mm down both faces, back wall on the step front and the st (OI-05) |
| `E-GER-02` | `GER-001-UL` Foot shoe UL | `FIN-001-UL` Half-fin upper left, two-layer foam board, square 40 mm tip | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 10 mm down both faces, back wall on the step front and the st (OI-05) |
| `E-GER-03` | `GER-001-LR` Foot shoe LR | `FIN-001-LR` Half-fin lower right, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 10 mm down both faces, back wall on the step front and the st (OI-05) |
| `E-GER-04` | `GER-001-LL` Foot shoe LL | `FIN-001-LL` Half-fin lower left, two-layer foam board, square 40 mm tip, link slot | mechanical · bonded · `CT-EPOXY` | fins | D5 | yes | bond | shoe bonded on the half-fin TE step (D3 cuts the tip to /z/ 0.2005 from x 0.2746 to the TE, CR-D5-11): sleeve floor on the step edge, legs 10 mm down both faces, back wall on the step front and the st (OI-05) |
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
| `E-GER-21` | `GER-007-R` Wingtip TE corner cap R | `WNG-001` Wing core, one piece (XPS) | mechanical · taped · `CT-GER-CAP-TAPE` | wing | D5 | yes | — | TPU corner cap on the fixed wingtip TE corner (outboard of the elevon end at /y/ 0.560), over the tape skin; sacrificial contact in a roll-first landing (CR-C5-04, CL-C5-WINGTIP-CLEAR-ROLL); keeps cle |
| `E-GER-22` | `GER-007-L` Wingtip TE corner cap L | `WNG-001` Wing core, one piece (XPS) | mechanical · taped · `CT-GER-CAP-TAPE` | wing | D5 | yes | — | TPU corner cap on the fixed wingtip TE corner (outboard of the elevon end at /y/ 0.560), over the tape skin; sacrificial contact in a roll-first landing (CR-C5-04, CL-C5-WINGTIP-CLEAR-ROLL); keeps cle |

### propulsion (E1, 8)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-PRP-01` | `PRP-004-UR` Prop adapter UR M6x1 LH + nut + washer | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot on the 4 mm shaft, four screws into the bell top on a 12 mm circle (vendor fit list names the X3108S KV900) |
| `E-PRP-02` | `PRP-004-UL` Prop adapter UL M6x1 RH + nut + washer | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot on the 4 mm shaft, four screws into the bell top on a 12 mm circle (vendor fit list names the X3108S KV900) |
| `E-PRP-03` | `PRP-004-LR` Prop adapter LR M6x1 RH + nut + washer | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot on the 4 mm shaft, four screws into the bell top on a 12 mm circle (vendor fit list names the X3108S KV900) |
| `E-PRP-04` | `PRP-004-LL` Prop adapter LL M6x1 LH + nut + washer | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | mechanical · fastened · `CT-PROP-ADAPTER` | — | E1 | yes | joint_stack | adapter pilot on the 4 mm shaft, four screws into the bell top on a 12 mm circle (vendor fit list names the X3108S KV900) |
| `E-PRP-05` | `PRP-003-UR` Prop UR APC 11x5.5MRP (LP11055MRP) | `PRP-004-UR` Prop adapter UR M6x1 LH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MRP (LP11055MRP) on a LH post; LPAR06E ring centres the 1/4 in bore on the M6 post; prop off for transport |
| `E-PRP-06` | `PRP-003-UL` Prop UL APC 11x5.5MR (LP11055MR) | `PRP-004-UL` Prop adapter UL M6x1 RH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MR (LP11055MR) on a RH post; LPAR06E ring centres the 1/4 in bore on the M6 post; prop off for transport |
| `E-PRP-07` | `PRP-003-LR` Prop LR APC 11x5.5MR (LP11055MR) | `PRP-004-LR` Prop adapter LR M6x1 RH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MR (LP11055MR) on a RH post; LPAR06E ring centres the 1/4 in bore on the M6 post; prop off for transport |
| `E-PRP-08` | `PRP-003-LL` Prop LL APC 11x5.5MRP (LP11055MRP) | `PRP-004-LL` Prop adapter LL M6x1 LH + nut + washer | mechanical · fastened · `CT-PROP-NUT` | — | E1 | yes | joint_stack | field joint; 11x5.5MRP (LP11055MRP) on a LH post; LPAR06E ring centres the 1/4 in bore on the M6 post; prop off for transport |

### power (F1, 4)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-PWR-01` | `PWR-002` Main disconnect AS150U, aircraft half + 8 AWG pigtail | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · slid · `CT-CONN-PARK` | pod | F1 · F2 · D2 | — | — | AS150U parked in a 60 mm slot x 0.030…0.090 in the left channel (CR-F1-13); the slot, not a tie, takes the ≈ 30–50 N `EST` unplug force at every field set-up; plug reachable with the pack in |
| `E-PWR-02` | `PWR-003` Power module: CoreWing V2 power board (V/I sense) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F1 · F3 | — | — | CoreWing power board beside the FC |
| `E-PWR-03` | `PWR-004` Power distribution (PDB) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · fastened · `CT-M3-SHCS-INSERT` | pod | F1 · C6 | — | joint_stack | only if the PDB is a PCB (C6 stack); nylon spacers |
| `E-PWR-04` | `PWR-005` UBEC 6 V 8 A class for servos (fitted, D-32) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F1 | — | — | away from the GPS mast |

### avionics (F3, 10)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-AVN-01` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-GEL-PAD` | pod | F3 · C6 | — | retention | 2 gel pads 5 mm, no screws, f_n ≈ 35 Hz; secondary tie with slack (C6 retention); arrow toward -x; beside the pack, never its stop (CR-C5-07) |
| `E-AVN-02` | `AVN-002` GPS + compass HGLRC M100-5883 | `POD-005` GPS mast with 45 deg pad (printed PETG, plugs into the handle grip) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 | — | — | 45° pad toward the nose; no steel within 50 mm (brass E-POD-06); 0.154 m from the nearest power item |
| `E-AVN-03` | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 · F5 | — | — | antennas out through the hatch, one along z, one along y, ≥ 30 mm from spar and tubes, ≥ 60 mm from the GPS |
| `E-AVN-04` | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-TAPE-FOAM` | pod | F3 | — | — | left channel front, behind the socket; tubes ≤ 60 mm |
| `E-AVN-05` | `AVN-005` Pitot boom (plug-in) | `POD-006` Pitot boom socket with 32 mm flange (printed PETG, pod nose, left channel) | mechanical · slid · `CT-PLUG-IN` | pod | F3 · B4 · D2 | — | — | field joint; plug-in at every field set-up, tip [-0.195, -0.046, 0.045] m (`P:avionics.pitot_tip_xyz_m`, D-25) aligned to x, keyed so total/static cannot swap (OI-12) |
| `E-AVN-06` | `AVN-005` Pitot boom (plug-in) | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | mechanical · press_fit · `CT-PITOT-TUBING` | — | F3 | — | — | barbed couplers at the boom root part when the boom is pulled; lines labelled, no kinks (OI-12) |
| `E-AVN-07` | `AVN-006` Isolation and retention set: gel pads, foam tape, ties | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · taped · `CT-GEL-PAD` | pod | F3 | — | — | consumables set lumped on the tray (mass holder) |
| `E-AVN-08` | `AVN-007` microSD 16-32 GB (logging) | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | mechanical · press_fit · `CT-CARD-SLOT` | — | F3 | — | — | 16–32 GB SDHC, FAT32; logging (R-FC-STABLE) |
| `E-AVN-09` | `GND-001` RC transmitter (ELRS 2.4 GHz, 25 mW) | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | electrical · radio · `CT-ELRS-RF` | ground | F5 | — | — | signal {protocol ELRS 2.4 GHz → CRSF 420 kbaud, tx_power_mw 25, telemetry through ELRS, no separate radio}; range test `T-F5-RANGE` |
| `E-AVN-10` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | thermal · conductive · `CT-THERMAL-CONTACT` | pod | E3 · F3 | — | — | gel pads + vents; FC 57.0 °C design (`CL-E3-FC-PEAK`), 70.7 °C hover-only, vs 85 °C |

### harness (F2, 28)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-HRN-01` | `HRN-001` Pod harness bundle (lumped mass) | `POD-002` Tray: bay floor + 3 mm forward stop + 1.5 mm guides, FC plate, avionics plate, PDB plate (printed PETG) | mechanical · strapped · `CT-TIE` | pod | F2 | — | — | tie points on the tray |
| `E-HRN-02` | `HRN-002-L` Wing-fin harness bundle L (lumped mass) | `WNG-001` Wing core, one piece (XPS) | mechanical · taped · `CT-WIRE-CHANNEL` | wing | F2 · D1 | — | — | ESC leads in two taped surface grooves 5 mm apart, not buried, ≥ 0.12 m from the mast top (F1); route clear of the spar slot and the anchor pockets (OI-04) |
| `E-HRN-03` | `HRN-002-L` Wing-fin harness bundle L (lumped mass) | `FIN-002-L` Motor tube L, CF 22x20 x 344 mm | mechanical · strapped · `CT-TIE` | fins | F2 · D3 | — | — | ties along the tube, clear of the prop discs |
| `E-HRN-04` | `HRN-002-R` Wing-fin harness bundle R (lumped mass) | `WNG-001` Wing core, one piece (XPS) | mechanical · taped · `CT-WIRE-CHANNEL` | wing | F2 · D1 | — | — | ESC leads in two taped surface grooves 5 mm apart, not buried, ≥ 0.12 m from the mast top (F1); route clear of the spar slot and the anchor pockets (OI-04) |
| `E-HRN-05` | `HRN-002-R` Wing-fin harness bundle R (lumped mass) | `FIN-002-R` Motor tube R, CF 22x20 x 344 mm | mechanical · strapped · `CT-TIE` | fins | F2 · D3 | — | — | ties along the tube, clear of the prop discs |
| `E-HRN-10` | `PWR-001` Flight pack 4S (re-terminated AS150U) | `PWR-002` Main disconnect AS150U, aircraft half + 8 AWG pigtail | electrical · connector · `CT-AS150U` | power | F1 · F2 | — | — | THE field disconnect; AS150U 70 A cont / 140 A momentary ≥ 37.8 A required (1.25 ×, `CL-F1-AS150U-CONT`, D-32); current_a {cont: `P:performance.hover_current_a` 27 A hover, peak: `P:electrical.peak_current_a` 120 A < 5 s} |
| `E-HRN-11` | `PWR-002` Main disconnect AS150U, aircraft half + 8 AWG pigtail | `PWR-003` Power module: CoreWing V2 power board (V/I sense) | electrical · soldered · `CT-SOLDER-DC` | power | F1 · F2 | — | — | 8 AWG ≤ 0.15 m twisted (`CL-F1-MAIN-RISE`); current_a {cont: `P:performance.hover_current_a` 27 A hover, peak: `P:electrical.peak_current_a` 120 A < 5 s} |
| `E-HRN-12` | `PWR-003` Power module: CoreWing V2 power board (V/I sense) | `PWR-004` Power distribution (PDB) | electrical · soldered · `CT-SOLDER-DC` | power | F1 · F2 | — | — | 8 AWG, same run; current_a {cont: `P:performance.hover_current_a` 27 A hover, peak: `P:electrical.peak_current_a` 120 A < 5 s} |
| `E-HRN-13` | `PWR-004` Power distribution (PDB) | `PRP-002-UR` ESC UR LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | ESC lead 16 AWG 0.5 m (`CL-F1-ESC-RISE`); current_a {cont: hover share, peak: `P:propulsion.current_max_per_motor_a` 24.8 A}; route pod → wing groove → fin (OI-04) |
| `E-HRN-14` | `PWR-004` Power distribution (PDB) | `PRP-002-UL` ESC UL LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | ESC lead 16 AWG 0.5 m (`CL-F1-ESC-RISE`); current_a {cont: hover share, peak: `P:propulsion.current_max_per_motor_a` 24.8 A}; route pod → wing groove → fin (OI-04) |
| `E-HRN-15` | `PWR-004` Power distribution (PDB) | `PRP-002-LR` ESC LR LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | ESC lead 16 AWG 0.5 m (`CL-F1-ESC-RISE`); current_a {cont: hover share, peak: `P:propulsion.current_max_per_motor_a` 24.8 A}; route pod → wing groove → fin (OI-04) |
| `E-HRN-16` | `PWR-004` Power distribution (PDB) | `PRP-002-LL` ESC LL LANRC 45 A | electrical · soldered · `CT-SOLDER-DC` | power, propulsion | F1 · F2 | — | — | ESC lead 16 AWG 0.5 m (`CL-F1-ESC-RISE`); current_a {cont: hover share, peak: `P:propulsion.current_max_per_motor_a` 24.8 A}; route pod → wing groove → fin (OI-04) |
| `E-HRN-17` | `PRP-002-UR` ESC UR LANRC 45 A | `PRP-001-UR` Motor UR SunnySky X3108S KV900 (CW from the nose) | electrical · connector · `CT-BULLET-3` | propulsion | F2 · E1 | — | — | phase extension ≤ 100 mm if the factory leads are short; phase order sets rotation (F4 map) (OI-06) |
| `E-HRN-18` | `PRP-002-UL` ESC UL LANRC 45 A | `PRP-001-UL` Motor UL SunnySky X3108S KV900 (CCW from the nose) | electrical · connector · `CT-BULLET-3` | propulsion | F2 · E1 | — | — | phase extension ≤ 100 mm if the factory leads are short; phase order sets rotation (F4 map) (OI-06) |
| `E-HRN-19` | `PRP-002-LR` ESC LR LANRC 45 A | `PRP-001-LR` Motor LR SunnySky X3108S KV900 (CCW from the nose) | electrical · connector · `CT-BULLET-3` | propulsion | F2 · E1 | — | — | phase extension ≤ 100 mm if the factory leads are short; phase order sets rotation (F4 map) (OI-06) |
| `E-HRN-20` | `PRP-002-LL` ESC LL LANRC 45 A | `PRP-001-LL` Motor LL SunnySky X3108S KV900 (CW from the nose) | electrical · connector · `CT-BULLET-3` | propulsion | F2 · E1 | — | — | phase extension ≤ 100 mm if the factory leads are short; phase order sets rotation (F4 map) (OI-06) |
| `E-HRN-21` | `PWR-004` Power distribution (PDB) | `PWR-005` UBEC 6 V 8 A class for servos (fitted, D-32) | electrical · soldered · `CT-SOLDER-DC` | power | F1 | — | — | UBEC feed through an inline 5 A fuse + holder (bus → fuse → UBEC, CR-F1-06); fuse rating in the wire block |
| `E-HRN-22` | `PWR-005` UBEC 6 V 8 A class for servos (fitted, D-32) | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | electrical · connector · `CT-SERVO-JR` | avionics, power | F1 · F3 | — | — | servo rail 6 V; 5.2 A required > FC BEC 4.5 A (`CL-F1-SERVO-BEC-REQ`); stall current `UNVERIFIED` |
| `E-HRN-23` | `PWR-003` Power module: CoreWing V2 power board (V/I sense) | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | electrical · connector · `CT-JST-GH-6` | avionics, power | F1 · F3 · F4 | — | — | signal {BATT_* scaling of the CoreWing board: 64 A/V (`CL-F3-SENSE-*`)} |
| `E-HRN-24` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-UR` ESC UR LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 · F3 · F4 | — | — | signal only; signal {fc_port per F4 motor map for UR, protocol DShot}; ground reference; no power (ESC has no BEC) |
| `E-HRN-25` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-UL` ESC UL LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 · F3 · F4 | — | — | signal only; signal {fc_port per F4 motor map for UL, protocol DShot}; ground reference; no power (ESC has no BEC) |
| `E-HRN-26` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-LR` ESC LR LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 · F3 · F4 | — | — | signal only; signal {fc_port per F4 motor map for LR, protocol DShot}; ground reference; no power (ESC has no BEC) |
| `E-HRN-27` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `PRP-002-LL` ESC LL LANRC 45 A | electrical · connector · `CT-SERVO-JR` | avionics, propulsion | F2 · F3 · F4 | — | — | signal only; signal {fc_port per F4 motor map for LL, protocol DShot}; ground reference; no power (ESC has no BEC) |
| `E-HRN-28` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `MEC-001-L` Elevon servo L | electrical · connector · `CT-SERVO-JR` | avionics, mechanisms | F2 · F4 | — | — | signal {fc_port elevon L}; servo power from the rail; extension through the wing groove (OI-04) |
| `E-HRN-29` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `MEC-001-R` Elevon servo R | electrical · connector · `CT-SERVO-JR` | avionics, mechanisms | F2 · F4 | — | — | signal {fc_port elevon R}; servo power from the rail; extension through the wing groove (OI-04) |
| `E-HRN-30` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-002` GPS + compass HGLRC M100-5883 | electrical · connector · `CT-JST-GH-6` | avionics | F3 · F4 | — | — | signal {fc_port SERIAL5 (UART5) + I2C1, protocol UBX, compass i2c_addr 0x0D/0x2C} |
| `E-HRN-31` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-003` RC receiver RadioMaster RP3 V2 (ELRS 2.4 GHz) | electrical · connector · `CT-JST-GH-4` | avionics | F3 · F5 · F4 | — | — | signal {fc_port SERIAL6, protocol CRSF 420 kbaud}; ≤ 150 mm twisted, away from ESC power leads (CR-F5-04) |
| `E-HRN-32` | `AVN-001` Flight controller CoreWing F405 Wing APP V2 | `AVN-004` Airspeed sensor MS4525DO (I2C 0x28) | electrical · connector · `CT-JST-GH-4` | avionics | F3 · F4 | — | — | signal {fc_port I2C1, protocol I2C, i2c_addr 0x28}; ≤ 0.5 m |

### mechanisms (D6, 18)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-MEC-01` | `MEC-008-L` Servo frame L | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D6 · D1 | — | — | servo pocket; frame ≥ 720 mm² into XPS (CR-C6-13) |
| `E-MEC-02` | `MEC-008-R` Servo frame R | `WNG-001` Wing core, one piece (XPS) | mechanical · bonded · `CT-EPOXY` | wing | D6 · D1 | — | — | servo pocket; frame ≥ 720 mm² into XPS (CR-C6-13) |
| `E-MEC-03` | `MEC-001-L` Elevon servo L | `MEC-008-L` Servo frame L | mechanical · fastened · `CT-M2-SCREW-PLASTIC` | — | D6 · C6 | — | joint_stack | servo ear screws into bosses (C6 stack) |
| `E-MEC-04` | `MEC-001-R` Elevon servo R | `MEC-008-R` Servo frame R | mechanical · fastened · `CT-M2-SCREW-PLASTIC` | — | D6 · C6 | — | joint_stack | servo ear screws into bosses (C6 stack) |
| `E-MEC-05` | `MEC-002-L` Servo arm L | `MEC-001-L` Elevon servo L | mechanical · fastened · `CT-SERVO-SPLINE` | — | D6 | — | — | arm centred at servo neutral |
| `E-MEC-06` | `MEC-002-R` Servo arm R | `MEC-001-R` Elevon servo R | mechanical · fastened · `CT-SERVO-SPLINE` | — | D6 | — | — | arm centred at servo neutral |
| `E-MEC-07` | `MEC-003-L` Pushrod L | `MEC-002-L` Servo arm L | kinematic · hinged · `CT-CLEVIS` | — | D6 | — | — | motion Y [-25, 25]°; arm hole radius, pushrod clear of skin |
| `E-MEC-08` | `MEC-003-R` Pushrod R | `MEC-002-R` Servo arm R | kinematic · hinged · `CT-CLEVIS` | — | D6 | — | — | motion Y [-25, 25]°; arm hole radius, pushrod clear of skin |
| `E-MEC-09` | `MEC-003-L` Pushrod L | `MEC-004-L` Control horn L (inboard panel) | kinematic · hinged · `CT-CLEVIS` | — | D6 | — | — | motion Y [-25, 25]°; horn hole radius (linkage ratio) |
| `E-MEC-10` | `MEC-003-R` Pushrod R | `MEC-004-R` Control horn R (inboard panel) | kinematic · hinged · `CT-CLEVIS` | — | D6 | — | — | motion Y [-25, 25]°; horn hole radius (linkage ratio) |
| `E-MEC-11` | `MEC-004-L` Control horn L (inboard panel) | `WNG-011-L` Elevon inboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 · B2 | — | — | through-panel horn, ≥ 720 mm² bond, hinge moment |
| `E-MEC-12` | `MEC-004-R` Control horn R (inboard panel) | `WNG-011-R` Elevon inboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 · B2 | — | — | through-panel horn, ≥ 720 mm² bond, hinge moment |
| `E-MEC-13` | `MEC-005-L` Inter-panel link L | `WNG-011-L` Elevon inboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | — | — | link bonded in inboard panel (OI-03) |
| `E-MEC-14` | `MEC-005-L` Inter-panel link L | `WNG-012-L` Elevon outboard L | mechanical · bonded · `CT-EPOXY` | wing | D6 | — | — | link bonded in outboard panel (OI-03) |
| `E-MEC-15` | `MEC-005-R` Inter-panel link R | `WNG-011-R` Elevon inboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | — | — | link bonded in inboard panel (OI-03) |
| `E-MEC-16` | `MEC-005-R` Inter-panel link R | `WNG-012-R` Elevon outboard R | mechanical · bonded · `CT-EPOXY` | wing | D6 | — | — | link bonded in outboard panel (OI-03) |
| `E-MEC-17` | `MEC-007-L` Servo cover L | `WNG-003` Tape skin | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | — | — | removable for servo service |
| `E-MEC-18` | `MEC-007-R` Servo cover R | `WNG-003` Tape skin | mechanical · taped · `CT-TAPE-SKIN` | wing | D6 | — | — | removable for servo service |

### transport (D7, 21)

| Edge | Side A | Side B | Kind · method · type | Ack | By | Decl. | C6 | Must carry |
|---|---|---|---|---|---|---|---|---|
| `E-TRN-01` | `TRN-002-L` Spar cradle L (saddle + crush column) | `TRN-001` Box base (floor, walls, end pads) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | column base on the floor + 2 zip ties through the floor |
| `E-TRN-02` | `TRN-002-R` Spar cradle R (saddle + crush column) | `TRN-001` Box base (floor, walls, end pads) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | as E-TRN-01 |
| `E-TRN-03` | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | `TRN-001` Box base (floor, walls, end pads) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | tray on the floor between the cradles |
| `E-TRN-04` | `TRN-004-L` Lid hold-down pillar L | `TRN-005` Lid with plug lip (no lining, D-31) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | pillar on the lid shell |
| `E-TRN-05` | `TRN-004-R` Lid hold-down pillar R | `TRN-005` Lid with plug lip (no lining, D-31) | mechanical · taped · `CT-TRN-LSE-TAPE` | — | D7 | yes | — | pillar on the lid shell |
| `E-TRN-06` | `TRN-002-L` Spar cradle L (saddle + crush column) | `WNG-001` Wing core, one piece (XPS) | mechanical · slid · `CT-CRADLE-CONTACT` | wing | D7 | yes | — | saddle under the lower surface at y -0.20 (0.17-0.23), x -0.015..0.235 (spar line), 15 000 mm2 >= C2 1 080 mm2; 4 mm inboard of the brace anchors (0.234); elevons, fins, tubes, braces never pressed (P |
| `E-TRN-07` | `TRN-002-R` Spar cradle R (saddle + crush column) | `WNG-001` Wing core, one piece (XPS) | mechanical · slid · `CT-CRADLE-CONTACT` | wing | D7 | yes | — | as E-TRN-06 at y +0.20 |
| `E-TRN-08` | `TRN-004-L` Lid hold-down pillar L | `WNG-001` Wing core, one piece (XPS) | mechanical · slid · `CT-TRN-PRELOAD-PAD` | wing | D7 | yes | — | upper surface over the spar at y -0.20, x 0.03..0.13; replaces the strap of the A4 plan (E-TRN-07 there) |
| `E-TRN-09` | `TRN-004-R` Lid hold-down pillar R | `WNG-001` Wing core, one piece (XPS) | mechanical · slid · `CT-TRN-PRELOAD-PAD` | wing | D7 | yes | — | as E-TRN-08 at y +0.20 |
| `E-TRN-10` | `TRN-005` Lid with plug lip (no lining, D-31) | `TRN-001` Box base (floor, walls, end pads) | mechanical · slid · `CT-TRN-PLUG-LID` | — | D7 | yes | — | — |
| `E-TRN-11` | `TRN-006-L` Cam-buckle strap A | `TRN-001` Box base (floor, walls, end pads) | mechanical · strapped · `CT-TRN-CAM-STRAP` | — | D7 | yes | — | y -0.40 |
| `E-TRN-12` | `TRN-006-R` Cam-buckle strap B | `TRN-001` Box base (floor, walls, end pads) | mechanical · strapped · `CT-TRN-CAM-STRAP` | — | D7 | yes | — | y +0.40 |
| `E-TRN-13` | `TRN-007-C` Side carry handle | `TRN-001` Box base (floor, walls, end pads) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | side handle at the box CG |
| `E-TRN-14` | `TRN-007-L` End handle L | `TRN-001` Box base (floor, walls, end pads) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | end handle |
| `E-TRN-15` | `TRN-007-R` End handle R | `TRN-001` Box base (floor, walls, end pads) | mechanical · fastened · `CT-TRN-M3-BOLT` | — | D7 | yes | — | end handle |
| `E-TRN-16` | `TRN-008` Field pouch (10 mm prop spanner, spare M6 prop nuts, 2.5 mm key, tape, checklist card) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | — | D7 | yes | — | pouch pocket at the tray aft end |
| `E-TRN-17` | `PRP-003-UR` Prop UR APC 11x5.5MRP (LP11055MRP) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 · E1 | — | — | stowed; prop in its tray slot 285 × 30 × 40 mm (prop Ø 279 mm) |
| `E-TRN-18` | `PRP-003-UL` Prop UL APC 11x5.5MR (LP11055MR) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 · E1 | — | — | stowed; prop in its tray slot 285 × 30 × 40 mm (prop Ø 279 mm) |
| `E-TRN-19` | `PRP-003-LR` Prop LR APC 11x5.5MR (LP11055MR) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 · E1 | — | — | stowed; prop in its tray slot 285 × 30 × 40 mm (prop Ø 279 mm) |
| `E-TRN-20` | `PRP-003-LL` Prop LL APC 11x5.5MRP (LP11055MRP) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | propulsion | D7 · E1 | — | — | stowed; prop in its tray slot 285 × 30 × 40 mm (prop Ø 279 mm) |
| `E-TRN-21` | `AVN-005` Pitot boom (plug-in) | `TRN-003` Prop tray with pitot-boom slot and pouch pocket | mechanical · slid · `CT-TRN-POCKET` | avionics | D7 · F3 | — | — | stowed; pitot boom in its 220 × 25 × 25 mm slot, PE tip plug |

## Acknowledgements owed

| Subsystem | Must list under `acknowledges` |
|---|---|
| `wing` | `E-FIN-49` `E-FIN-50` `E-FIN-51` `E-FIN-52` `E-FIN-53` `E-FIN-54` `E-FIN-55` `E-FIN-56` `E-FIN-57` `E-FIN-58` `E-FIN-59` `E-FIN-60` `E-GER-21` `E-GER-22` `E-POD-01` `E-POD-09` `E-TRN-06` `E-TRN-07` `E-TRN-08` `E-TRN-09` `E-MEC-01` `E-MEC-02` `E-MEC-11` `E-MEC-12` `E-MEC-13` `E-MEC-14` `E-MEC-15` `E-MEC-16` `E-MEC-17` `E-MEC-18` `E-HRN-02` `E-HRN-04` |
| `fins` | `E-GER-01` `E-GER-02` `E-GER-03` `E-GER-04` `E-HRN-03` `E-HRN-05` |
| `pod` | `E-PWR-01` `E-PWR-02` `E-PWR-03` `E-PWR-04` `E-AVN-01` `E-AVN-02` `E-AVN-03` `E-AVN-04` `E-AVN-05` `E-AVN-07` `E-AVN-10` `E-HRN-01` |
| `landing` | — |
| `propulsion` | `E-FIN-61` `E-FIN-62` `E-FIN-63` `E-FIN-64` `E-FIN-65` `E-FIN-66` `E-FIN-67` `E-FIN-68` `E-FIN-81` `E-FIN-82` `E-FIN-83` `E-FIN-84` `E-FIN-85` `E-FIN-86` `E-FIN-87` `E-FIN-88` `E-TRN-17` `E-TRN-18` `E-TRN-19` `E-TRN-20` `E-HRN-13` `E-HRN-14` `E-HRN-15` `E-HRN-16` `E-HRN-17` `E-HRN-18` `E-HRN-19` `E-HRN-20` `E-HRN-24` `E-HRN-25` `E-HRN-26` `E-HRN-27` |
| `power` | `E-POD-05` `E-POD-12` `E-HRN-10` `E-HRN-11` `E-HRN-12` `E-HRN-13` `E-HRN-14` `E-HRN-15` `E-HRN-16` `E-HRN-21` `E-HRN-22` `E-HRN-23` |
| `avionics` | `E-TRN-21` `E-HRN-22` `E-HRN-23` `E-HRN-24` `E-HRN-25` `E-HRN-26` `E-HRN-27` `E-HRN-28` `E-HRN-29` `E-HRN-30` `E-HRN-31` `E-HRN-32` |
| `harness` | — |
| `mechanisms` | `E-HRN-28` `E-HRN-29` |
| `transport` | — |
| `ground` | `E-AVN-09` |

## Connection types used

*Where*: `library` = `redesign/interfaces/connection_types.json` (A4-R3 additions marked +), else the subsystem that declares it locally.

| Id | Kind | Method | Where | Spec |
|---|---|---|---|---|
| `CT-AS150U` | electrical | connector | library + | Amass AS150U anti-spark pair (battery main; 70 A continuous, 140 A momentary per maker; packs re-terminated, D-32) |
| `CT-BULLET-3` | electrical | connector | library + | 3 x gold bullet connectors, motor phases (size per E1) |
| `CT-CA` | mechanical | bonded | library | cyanoacrylate bond (foam-safe CA where foam) |
| `CT-CARD-SLOT` | mechanical | press_fit | avionics | memory card pushed into the board's spring-latched slot |
| `CT-CLEVIS` | kinematic | hinged | library + | steel pushrod end (Z-bend or clevis) in a horn or arm hole |
| `CT-CONN-PARK` | mechanical | slid | power | connector half parked in a printed slot that takes the plug/unplug force; cable tie over it as secondary retention |
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
| `CT-M3-BRASS-NUT` | mechanical | fastened | pod | M3 brass SHCS through clearance hole, brass nut + Loctite 222 (non-magnetic, near a compass) |
| `CT-M3-SHCS-INSERT` | mechanical | fastened | library | M3 SHCS into M3 brass heat-set insert |
| `CT-M3-SHCS-MOTOR` | mechanical | fastened | library | M3 SHCS into motor base tapped hole (manufacturer pattern) |
| `CT-PITOT-TUBING` | mechanical | press_fit | library + | silicone tubing pushed on the pitot and sensor barbs, total and static lines (pneumatic); not a load path |
| `CT-PLUG-IN` | mechanical | slid | library + | boom pushed into a printed socket, keyed, retained by a detent or O-ring; tool-free field joint |
| `CT-PROP-ADAPTER` | mechanical | fastened | library + | bolt-on prop adapter, 4 x M3x4 SHCS into the motor bell, pilot on the shaft |
| `CT-PROP-NUT` | mechanical | fastened | library + | M6x1 nut and washer clamp the prop hub on the adapter post (field joint) |
| `CT-SERVO-JR` | electrical | connector | library | JR/Futaba 3-pin servo connector |
| `CT-SERVO-SPLINE` | mechanical | fastened | library + | servo arm on the output spline, M2 retaining screw |
| `CT-SLIDE-STOP` | mechanical | slid | pod | loose printed spacer trapped between two stops |
| `CT-SOLDER-DC` | electrical | soldered | library + | soldered DC power joint, heat-shrink |
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
| Plan is consistent | `python -I redesign/team/A4/interface_plan.py` | `PASS`, connected 100 %, powered 100 %, 1 field disconnect, 0 id-rule breaches |
| Plan checks catch faults | `python -I redesign/team/A4/test_interface_plan.py` | 13 seeded faults caught, baseline clean |
| merge_check D-46 rules | `python -I redesign/team/A4/test_merge_check_d46.py` | 10 seeded cases + clean baseline |
| Real graph vs plan | `python -I redesign/team/A4/interface_plan.py --compare` → `team/A4/PLAN-STATUS.md` | 0 missing, 0 owed, deviations explained |
| Real graph | `python -I redesign/interfaces/merge_check.py --strict` | 0 errors, 0 warnings |
| CAD | `python -I redesign/fusion/check.py` | every edge registered, nothing floats |
| Proof chain | `python -I redesign/proofs/build_graph.py` | no drift on `CALC-A4-PLAN-GRAPH` |
