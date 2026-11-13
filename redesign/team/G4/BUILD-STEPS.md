# G4 build-step sheets: K09-L

Revision G4-R1, 2026-11-13. Status `PROPOSED`. Owner G4 (assembly sequence engineer). Requirements: `R-BUILD-HOURS`, `R-JOINT-STACK` (support), `R-FIELD-SETUP` (support).
These sheets **sit on top of `../../BUILD-GUIDE.md`**: stage numbers 1-12 are the same, the numbered steps stay in the guide and in each `subsystems/<x>/BUILD.md` (one source, no copies that can drift),
and each sheet here adds what the guide does not carry: who, where, which tools and BOM lines, hold points, records and the I2 task ids. If a step changes in the guide, nothing here needs editing unless a hold point or a record changes.
Companions: [`../G1/PROCESS-PLAN.md`](../G1/PROCESS-PLAN.md) (processes, gates), [`../G2/COMPOSITES-FOAM-PLAN.md`](../G2/COMPOSITES-FOAM-PLAN.md) (foam, epoxy, tape sheets), [`../G3/PRINT-LIST.md`](../G3/PRINT-LIST.md) (print list),
[`../I2/SCHEDULE.md`](../I2/SCHEDULE.md) (dates, load). Animations: each stage has a clip in `showcase/animation/build/` (`stage-NN.mp4`, linked from the guide).

## 1. Conventions

| Item | Rule |
|---|---|
| Roles | P1 wing and fin structure, P2 electrical and software, P3 printing, pod, mechanisms, landing, P4 test, compliance, pilot. Names are assigned by the team (`../I2/SCHEDULE.md`); **no stage is signed by the person who built it alone: a second person initials every hold point** |
| Traveler | One row per part or sub-assembly in [`templates/traveler.csv`](templates/traveler.csv); weigh every part, log the measured value against the BUILD.md check, copy masses to A3 (`T-A3-WEIGH-PARTS`) |
| Hold point (H) | the check in the guide's "Inspect before moving on" box; the next stage does not start until it is initialled |
| Open fix | "pending" items from `BUILD-GUIDE.md`: the step is not started until the fix is in CAD and the part re-exported |
| Where | J = Jacobs Hall (Maker Pass, drop-in, in-lab; closed 19 Dec - 18 Jan), W = team workspace (hot wire, epoxy, CF; to be named, `../G1/PROCESS-PLAN.md` `CR-G1-01`), F = field (RFS) |
| Re-run before any print or cut | `python -I redesign/fusion/check.py`, `python -I redesign/collision/collide.py`, `python -B redesign/manufacturing/make_shop_files.py` (`BUILD-GUIDE.md`, RESUME) |

## 2. Hours check against `R-BUILD-HOURS` (<= 90 team-hours to first hover)

| Stage | Hours `EST` (guide's times, 8 h per day) | I2 tasks |
|---|---|---|
| 2 Wing core and spar | 16 | `B01`-`B05` |
| 3 Elevon panels | 3.5 | `B06` |
| 4 Fins on the motor tubes | 16 | `B07`-`B10` |
| 5 Pod and power stack | 8.5 + 3 | `B11`, `B12` |
| 6 Harness, then skin | 12 + 7 | `B13`, `B14` |
| 7 Servos, linkage, hinges | 8 | `B15` |
| 8 Motor mounts, motors, props | 4 | `B16` |
| 9 Avionics | 8 | `B17` |
| 10 Feet and corner caps | 9 | `B18` |
| 11 Checks | 16 | `B19` |
| **Sum, stages 2-11** | **111** | |

111 h is 21 h over the 90 h line even before stage 1 (prints, jigs) and stage 12; the schedule's sum is 113.5 h (`../I2/SCHEDULE.md`, with `B02` split differently). **This is a `FAIL` on the guide's own times.** Levers (none applied):
two-person parallel work does not change the team-hours; moving printing, harness cutting and jig work to stage 1 (done: they are before first cut); a measured reduction after the practice cores; or A2 rewording `R-BUILD-HOURS` to the hours after first cut and before the first hover for the airframe only (`CR-I2-02`).

## 3. Stage sheets

### Stage 1. Buy, measure, print and cut parts (Nov - 18 Dec, then home)

| Item | Detail |
|---|---|
| Owner, where | P1, P3 (jigs, templates, coupons), P2 (electronics), P4 (compliance); J and W |
| Tools | calipers, steel rule 1 m, scales 0.1 g and 1 g, depth gauge, inclinometer, preset torque screwdriver, pin vise, Z-bend pliers, hot-wire bow, laser, Prusa, drill press |
| BOM lines | B01, B02, A01, M01, P01, W03, W04, W05, W08, D01-D03, C03, G11, H05 (`team/I1/BOM.csv`) |
| Holds | **stop items before stage 1 in `BUILD-GUIDE.md`**: CG fix (modelled only), fin tip on one datum, mount slit and dog (dog shear size open, C6), SW-01 strap eyes pending; shop files exist |
| Steps | `BUILD-GUIDE.md` stage 1 steps 1-6; `../G3/PRINT-LIST.md` print order; `../G2/COMPOSITES-FOAM-PLAN.md` practice cores |
| Hold point | every measured value logged; one mount, one collar, one frame test-fitted; **design freeze signed 18 Dec** (`../I2/SCHEDULE.md` `FZ1`) |
| Records | motor, tube, board, pack measurements in `team/H1/templates/motor_incoming.csv`, `weigh.csv`; packs in `team/E2/pack_log.csv` |
| Tests that belong here | GT-01 to GT-05, GT-15, GT-16 (H1); twin build and flight (`../H2/FLIGHT-TEST-PLAN.md` gate 1) |

### Stage 2. Wing core and spar

| Item | Detail |
|---|---|
| Owner, where | P1 (lead), P3 (second pair of hands for the jig); W |
| Needs | W01 XPS, W03/W04 tube, plugs (print list `WNG-004/005`), C05 epoxy, blocks `FIN-004` x 2, JIG-01 + ply base |
| Holds | SW-01 (block strap eyes) must be fixed in CAD first; practice cores accepted (two in a row) |
| Steps | `BUILD-GUIDE.md` stage 2 steps 1-5; `subsystems/wing/BUILD.md` steps 1-8; `../G2` sheets P-01 to P-03 |
| Hold point (H2) | core straight within 1 mm, no twist; blocks at y +/-320 +/- 1 mm; bores parallel and vertical within +/-0.5 deg in the jig; beads continuous |
| Records | cut log (V, I, feed), core mass, template gauge readings at 3 stations, jig readings |
| I2 | `B01`-`B05`; hours 16; cures 2 x 24 h |

### Stage 3. Elevon panels

| Item | Detail |
|---|---|
| Owner, where | P1; W |
| Needs | torque tubes `MEC-009` (H02), hinge tape |
| Steps | `BUILD-GUIDE.md` stage 3 steps 1-3; `wing/BUILD.md` step 9; `mechanisms/BUILD.md` steps 1-4; `../G2` P-04 |
| Hold point | panels 228 and 218 mm long, chord 70.4 mm; >= 1 mm foam over each tube; corner radii by gauge |
| I2 | `B06`; hours 3.5; cure 24 h |

### Stage 4. Fins on the motor tubes

| Item | Detail |
|---|---|
| Owner, where | P1, P3; spray lamination at J (booth), the rest W |
| Needs | W02 foam board, W04 tubes, D03 plugs, D01 braces, D02 strips, C03 pins, collars `FIN-008` (**on hold**), anchors, ESC pads `FIN-007` |
| Holds | collar height not frozen (H7 / BR-08); pin row depends on the tip decision; lower roots rod notch under a fillet pending C4 check (SC-04); weigh a cup per fillet batch |
| Steps | `BUILD-GUIDE.md` stage 4 steps 1-6; `fins/BUILD.md` steps 1-17; `../G2` P-05, P-06 |
| Hold point | tubes vertical and parallel; each half-fin weighed before and after (+6.3 g expected); no filler in lead holes or elevon gaps |
| Records | laminate thickness per board, tube length, cup mass per batch, half-fin before/after |
| I2 | `B07`-`B10`; hours 16; 4-5 cures |

### Stage 5. Pod and power stack

| Item | Detail |
|---|---|
| Owner, where | P3 (pod, W), P2 (power stack, J Electronics Lab for soldering) |
| Needs | pod board and prints `POD-*` (W02, W05), F01 AS150U, F02-F04 wire, F07 caps, F08 FR4, C02 inserts, C06 nylon screws, D06 straps; F05/F06 only if gate X12 |
| Holds | pod BUILD step 11 handle bridge to a non-existent slot fill (SW-10): bond to the spar saddles only; WB-02 order of the ESC lead soldering; pack station may move forward up to 6 mm (BR-00) |
| Steps | `BUILD-GUIDE.md` stage 5 steps 1-5; `pod/BUILD.md`; `power/BUILD.md` and `power/BOARD-CHECK.md` (30 min on arrival of the FC) |
| Hold point | polarity; > 1 Mohm between rails; loop resistance logged; stack weighed (88 g) |
| I2 | `B11`, `B12`; hours 8.5 + 3; 3 cures |

### Stage 6. Harness, then skin

| Item | Detail |
|---|---|
| Owner, where | P2 (harness, J for soldering), P1 + P3 (skin, W, two people) |
| Needs | F03 16 AWG, H01 harness parts, F09 heat-shrink, W06 tape, 100 mm tape, pull-test gauge |
| Holds | `T-F2-CONT` with the pack out before skinning; nothing runs on top of the tape (D-86); trim the tape square along the fin fillet (D-88); **no soldering 19 Dec - 18 Jan** (`../I2/SCHEDULE.md`) |
| Steps | `BUILD-GUIDE.md` stage 6 steps 1-6 (bus-bar landing order, ESC termination); `harness/BUILD.md`; `wing/BUILD.md` step 11; `../G2` P-07 |
| Hold point | continuity and isolation logged (every net < 0.1 ohm, > 1 Mohm between nets); no tape wrinkles at the LE; LE-strip edges >= 32 mm |
| I2 | `B13`, `B14`; hours 12 + 7 |

### Stage 7. Servos, linkage and hinges

| Item | Detail |
|---|---|
| Owner, where | P3 + P1 (both sides in parallel), W |
| Needs | M01 servos, H02 mechanisms hardware, horns and frames `MEC-004...008`, servo tester |
| Holds | SC-01 JR housing off while the lead passes the straw; arm drilled to 1.85 mm (SC-07); slip-fit the outboard horn (SC-03) |
| Steps | `BUILD-GUIDE.md` stage 7 steps 1-5; `mechanisms/BUILD.md` steps 5-12 |
| Hold point | free play <= 1 deg at the TE; both panels of a side within 1 deg at 0 and +/-25 deg; warm peel test passed (3.5 N at the TE, 10 min) |
| I2 | `B15`; hours 8; 2 x 24 h |

### Stage 8. Motor mounts, motors and props

| Item | Detail |
|---|---|
| Owner, where | P1 (mounts), P2 (electrical, direction); W, spin test at the thrust stand |
| Needs | B01 motors, B03 props, B05 rings, B07 screws, C01 pinch bolts and nylocs, C04 Loctite 243, mounts `FIN-003` (ASA) |
| Holds | incoming check on every motor (weight, pattern, hole depths, E-clip, phase resistance); drill from a printed guide with no motor on it; spin test for direction at 5 %, props off; slip number: use the one D3 and C6 agree (70-80, 74 or 85-100 N differ between documents) |
| Steps | `BUILD-GUIDE.md` stage 8 steps 1-6; `propulsion/BUILD.md`; `fins/BUILD.md` steps 18-19 |
| Hold point | each motor turns in its stated direction; witness marks on every screw and nut; slip holds 60 N |
| I2 | `B16`; hours 4; 4 x `T-E1-STAND` runs after (H1) |

### Stage 9. Avionics

| Item | Detail |
|---|---|
| Owner, where | P2; J (soldering the RP3 pads, GPS splice) |
| Needs | A01 FC, A02 GPS, A03 RX, A04 airspeed (**gated X08**: synthetic airspeed until bought), A05 microSD, A06 antennas, A07 isolation set |
| Holds | check the RP3 pad order against the board (CAD order is an estimate); pitot lines on different couplers (WB-13); compass chip ID at the I2C scan (WB-12) |
| Steps | `BUILD-GUIDE.md` stage 9 steps 1-5; `avionics/BUILD.md` |
| Hold point | pre-arm checks pass; airspeed rises on a blow at the tip and drops on a suck (if A04 is fitted) |
| I2 | `B17`; hours 8 |

### Stage 10. Feet and corner caps

| Item | Detail |
|---|---|
| Owner, where | P3; W, drill press at J for cartridge pre-crush |
| Needs | shoes `GER-001`, pistons `GER-002`, cartridges (W01 offcuts: F-400 per `GER-003`: **BOM has F-250 offcuts**, `CR-G4-01`), D05 neoprene, D07 brass cutter, TPU caps `GER-007` |
| Holds | weigh the first shoe and report it to A3 before printing the other three (D-76 foot 59.1 g `EST`, allocation 60 g) |
| Steps | `BUILD-GUIDE.md` stage 10 steps 1-4; `landing/BUILD.md` |
| Hold point | four feet and two caps weighed and reported to A3; pads level |
| I2 | `B18`; hours 9; cure 24 h |

### Stage 11. Checks: weight, CG, controls, thrust stand

| Item | Detail |
|---|---|
| Owner, where | P4 lead with all four; W / J (bench power supply) |
| Needs | G04 watt meter, G06/G12 stand, CG jig, scales, inclinometer |
| Holds | **if the aircraft balances aft of 51.4 mm do not fly it** (BR-00); report measured CG to A3 and B3 |
| Steps | `BUILD-GUIDE.md` stage 11 steps 1-5; `team/H1/GROUND-TEST-PLAN.md` GT-06, 07, 12, 13, 14, 18 |
| Hold point | CG inside the marks with every pack; all four stations in band; no witness mark moved; range check passed (`../F5/RANGE-TEST.md`) |
| I2 | `B19`, `RG1`; hours 16 + 3 |

### Stage 12. First hover (hands over to H2)

| Item | Detail |
|---|---|
| Owner, where | P4 pilot; F (RFS) |
| Needs | the flight card and flight request (`../H3/`), the battery procedure, charged packs |
| Holds | gates 1-2 passed (twin, stand), SITL >= 10 h logged, RFS request accepted, range check passed, flight card signed (`../H2/FLIGHT-TEST-PLAN.md`) |
| Steps | `BUILD-GUIDE.md` stage 12; `../H2/FLIGHT-TEST-PLAN.md` gate 3 |
| I2 | `F01` |

## 4. Work packages by week and person (matches `../I2/SCHEDULE.md`)

| Week of | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| 19 Jan | cut cores, slot and pockets (B01, B02) | power stack in the lab (B12) | fin laminates, pod box (B08, B11) | compliance, flight request (FR1) |
| 26 Jan | spar and blocks in the jig, bond, elevons (B04-B06) | harness solder in the lab | pod walls, tray (cure) | wind log, SITL |
| 2 Feb | tubes, half-fin roots, collars, strips (B07-B10) | harness route and T-F2-CONT (B13) | fins, pod into the recess | stand and bench set-up |
| 9 Feb | skin (B14), mounts (B16) | avionics (B17), calibration | servos, feet (B15, B18) | checks (B19) |
| 16 Feb | checks, range test | range test, SITL | checks | first tethered hover (F01) |

## 5. Change requests from G4

| # | To | What | Why |
|---|---|---|---|
| CR-G4-01 | D5, I1 | Cartridge stock: `GER-003/008` are cut from 2 in **F-400**, the BOM carries F-250 offcuts from `W01` | landing parts.csv (D-76) vs `W01` |
| CR-G4-02 | A2 | `R-BUILD-HOURS` reading (section 2) | 111 h vs 90 h |
| CR-G4-03 | A5 | Draw the aids G1 lists as "named, not drawn" | `../G1/PROCESS-PLAN.md` section 4 |
