# Concept A CAD fidelity audit (QP-5), 2026-11-15

Constraint (user, 2026-11-15): the CAD must look exactly like the physical design. Read-only audit of
`qp/A/cad/a_model.py` (80 parts, 11 wires), `fusion/k09kit.py`, `fusion/fusionkit.py`, `blender/blender_backend.py`,
`qp/A/BOM-A.csv`, `qp/A/cad/model/*/interfaces.json`. Web pages read 2026-11-15. "—" = not published.
Grades: REAL = catalogue or designed shape at its real dimensions (CF tubes, designed printed parts, lead strip);
SIMPLIFIED = right size, wrong detail; STAND-IN = box/disc placeholder; MISSING = physically present, not in the CAD.

## 0. Primitives available (same Shape set in both backends)

| Primitive | Signature | Notes |
|---|---|---|
| prism | `prism(axis, offset, loops, depth)`; first loop outer, rest are holes | PCB outlines with holes, horns, tabs |
| revolve | `revolve(axis, center, profile[(a,r)])` | motor bell, shaft, nuts, screws |
| loft | `loft(axis, sections[(offset, loop)], smooth)` | sections on planes normal to one axis; Blender resamples to equal point count and caps the ends |
| box / cylinder / tube | wrappers | |
| cut_box / cut_cylinder / cut_prism / cut(shape, matrix) | subtractive | |
| wire | `ctx.wire(edge, points, dia)` | polyline, one round diameter, no connector bodies |
| fasteners | `k9.hw_screw / hw_nut / hw_washer / hw_insert` (M2, M3, M6 in `HW_DIMS`) | exist, UNUSED by a_model.py (`hw_part` needs the part declared in interfaces.json) |
| keep-outs | `k9.prop_keepout` (canted cylinder), `keepout_halfspace` | tested by hull, not by blade shape |

Limits: no threads, no fillets, no mesh/STEP import. A twisted blade must be built as a loft along the radial axis whose
section loops are rotated in-plane by the local pitch (the loops are plain 2-D points, so this works).

## 1. Parts table (80 CAD ids)

| Id | Name | Current geometry | Grade | Real geometry |
|---|---|---|---|---|
| WNG-001 | Wing core | loft of `reflex_placeholder(0.095, 0.012)`, cove, pockets | SIMPLIFIED (section invented) | foam core cut from a named airfoil (section 3) |
| WNG-002 | Spar 12x10x900 | tube | REAL | catalogue CF tube (R08) |
| WNG-003-C, 004-R/L, 005-R/L | 5 spar plugs | tube | REAL (as designed) | printed |
| WNG-006-R/L | Elevons | `k9.elevon` on the placeholder section | SIMPLIFIED | foam + tape hinge |
| WNG-007-R/L | Balance horn + lead strip | prisms | REAL (as designed) | 15.6 g lead strip 10 x 1.3 x 106 mm + PETG/CF tabs |
| WNG-008 x4 | Lens caps + stop bosses | prism arch from computed profile | REAL (as designed) | printed, 0.6 mm wall |
| WNG-009/010 x4 | Hinge damper stator/rotor | tubes, discs | REAL (as designed) | printed drum + silicone |
| FIN-001 x2 / FIN-002 x2 | Fin tube 16x14, rib 14x12 | tubes | REAL | R02 / R09 |
| FIN-003 x2 / FIN-005 x2 | Root block, rib saddle | ring + socket, clip slot | REAL (as designed) | printed |
| FIN-004 x2 | Fin fairing | flat box 3 mm | SIMPLIFIED | XPS fairing with real LE/TE rounding and tape |
| CGE-001 | Hub | cylinder R 50 x 60 mm, "envelope of a printed shell" | STAND-IN | printed hub with 4 arm sockets, bridge, 2 strut sockets, tray pads: no designed shape exists |
| CGE-002 x4, CGE-004, CGE-005 x2 | Arms, bridge, V struts | tubes | REAL | R08 / R10 |
| CGE-003 x4 | Motor cup | plate 24 x 33 x 5 + sleeve + lead hole | SIMPLIFIED | real motor plate with MN2212 hole pattern (EST), wire slot |
| CGE-006, 007 x2 | Bridge saddle, strut clamps | ring + box + clip slot | REAL (as designed) | printed |
| CGE-008 | Pack tray | plate, walls, lips, slots | REAL (as designed) | printed; lip bolts missing (below) |
| PRP-001 x4 | Motor MN2212 V2.0 | `motor_envelope` can 27.5 x 26.5, shaft 4 x 12 (length EST), lead stub | SIMPLIFIED | bell profile, vents, stator, base ring with 4 holes, shaft clip, 400 mm leads |
| PRP-002 x4 | Prop APC 9x4.5MR | swept-disc tube R 114.3 x 16 mm | STAND-IN | 2 blades (chord/twist/thickness), hub, adapter ring |
| PRP-003 | ESC SpeedyBee BLS 35A Mini V2 | box 35x35x5.5 + 6 pad boxes | STAND-IN | PCB, 4 holes, FETs, pads, capacitor, leads |
| PWR-001 | Tattu 2300 4S | box 105x35x29 + 5.5 mm lead box | SIMPLIFIED | rounded pouch under shrink, 14 AWG leads, XT60, balance lead |
| AVN-001 | Avionics plate | skin-profile prism, no windows | SIMPLIFIED | printed plate with 4 lightening windows (8 g assumes them) |
| AVN-002 | Kakute F405 Wing Mini | box 30x25x20 + 6 header boxes | STAND-IN | 2-board stack, standoffs, USB board, sockets |
| AVN-003 | RP3 V2 | box 20 x 12 x 4 | STAND-IN, undersized | 22 x 13 x 4 mm, 2 x 65 mm antennas, CRSF wire |
| AVN-004 | TBS M10Q GPS | box 25x25x8 + plug | STAND-IN | PCB + patch + compass, cable |
| AVN-005 | MS4525 board | box 15x15x8 (EST) | STAND-IN | PCB, 2 barbed ports, JST-GH |
| AVN-006 | Pitot | tube 175 mm (EST) | SIMPLIFIED | probe with tip and static holes, silicone line |
| AVN-007 | Foam-tape pads x4 | boxes | REAL | |
| MEC-001 x2 | Servo ES3054HV | box 28.4 x 26.7 x 13 + lead box | SIMPLIFIED | case, 2 ears, offset output boss, 240 mm lead, JR plug |
| MEC-002 x2 | Servo arm | box | STAND-IN | molded arm with hole row, screw |
| MEC-003 x2 | Pushrod | cylinder r 0.6 | SIMPLIFIED | 1.2 mm rod, bends or clevises at both ends |
| MEC-004 x2 | Control horn | box 14x2x10 | STAND-IN | molded horn, base plate, hole row |
| GER-001 x4 / GER-002 x4 | Foot shoe / EVA pad | ring, plate / box | REAL (as designed) | printed / 12x15x30 foam |
| HRN-001, HRD-001 | Harness, hardware lumps | 2 mm proxy cylinders | MISSING | about 40 itemisable physical items (below) |
| 11 wires | HRN edges | round 4 / 2.5 / 1.5 mm polylines | SIMPLIFIED | motor leads are 20 AWG (about 2 mm over insulation, EST); no connector bodies |

**Counts (80 parts): REAL 44, SIMPLIFIED 20, STAND-IN 14, MISSING 2 (lumps).** Grading by judgement, +-3.

### Present in the product, absent from the CAD
| Item | Count | Evidence |
|---|---|---|
| M3x8 SHCS motor screws | 16 | E-PRP-01/03/05/07 stacks |
| Prop nut + washer (stack says M6x1, but the shaft is 4 mm: check) | 4 | E-PRP-02.. |
| APC adapter rings | 4 | BOM P02 |
| Servo-arm M2x6 screws | 2 | E-MEC-02/07 |
| FC M2 screws; ESC 20x20 screws/grommets | 8 | E-AVN notes, ESC pattern |
| Tray lip M3 bolts, 25 mm Velcro strap | 4 + 1 | CGE-008, E-PWR-01 |
| XT60 plugs (pack lead, ESC lead) | 2 | E-HRN-01 |
| Pack balance lead (JST-XH 5-pin) | 1 | Tattu listings |
| Motor phase leads, solder or bullet joints | 4 | T-Motor page |
| JST-GH plugs (RX, GPS, airspeed, ESC-FC), JR servo plugs | 5 + 2 | E-HRN-06..11 |
| Pushrod clevises | 4 | BOM M02 |
| RX antennas 2 x 65 mm with U.FL | 2 | RadioMaster |
| Pitot silicone tubing 2/4 mm | 2 | RMRC page |
| Hinge tape, skin tape, epoxy fillets | — | BOM R01/R05; thin: model hinge strip only if it affects gaps, flag the rest |
| ESC input capacitor | 1 | not confirmed |

## 2. Sources of real dimensions (non-REAL items)

| Item | Source | Gives | Not published, how to measure |
|---|---|---|---|
| APC 9x4.5MR blades | https://www.apcprop.com/propeller-technical-data/ ; per-prop file `9x45MR-PERF.PE0` linked from /propeller-technical-data-files/ ; zip `PE0-FILES_WEB-YYYYMM.zipx` on /technical-information/file-downloads/ (example 202602) | page says files list "blade properties along the span (chord, pitch, thickness ratio)". **I could not read a PE0 file**: files page 403, guessed /files/ URL 404. `PER3_9x45MR.dat` (sim 2022-09-22) is Ct/Cp only | download the zipx in a browser; hub dia/thickness and adapter bore by caliper on the 4-pack; blade airfoil coordinates are not published: thickness ratio on a flat-bottom section, flag EST |
| T-Motor MN2212 V2.0 | https://store.tmotor.com/goods-388-MN2212-V20.html | 27.5 dia, 26.5 height, shaft 4, stator 22 x 13, 400 mm 20 AWG leads, 55 g bare / 65 g. Drawing is a JPEG `MN2212-draw-0603-v1.jpg` (not readable by my tool) | shaft length, mount pattern/hole size, base ring: read the JPEG, else caliper. Page text mentions MN4112 once: confirm the drawing is MN2212 |
| EMAX ES3054HV | https://www.readymaderc.com/products/details/85975-emax-es3054-hv-high-voltage-17g-metal-gear-digital-servo | 20.5 g, 240 mm lead, JR plug, **23T spline** (CAD joint stack says 25T: reconcile). "See drawing", none shown | body 28.4 x 13.0 x 26.7 is from servodatabase.com (per SERVO.md), axis of the ear span unclear; ears, output offset: caliper the servo |
| Kakute F405 Wing Mini | https://holybro.com/products/kakute-f405-wing-mini ; docs.holybro.com/autopilot/kakute-f405-wing-mini (page 429; search snippets only) | 25 x 30 x 20 mm stack, 20 x 20 M2 pattern, 17 g with USB board | board thickness, socket positions: Holybro pinout page / dimension drawing (not located); measure |
| SpeedyBee BLS 35A Mini V2 | https://www.readymaderc.com/products/details/86873-speedybee-bls-35a-mini-v2-20x20-4-in-1-esc ; retailer specs agree | 35 x 35 x 5.5, 20 x 20 pattern, hole 3.5 mm (some 3.6), 7.2 g | pad layout, capacitor, input leads: measure (SpeedyBee page 404) |
| Tattu 2300 4S 75C XT60 | https://www.readymaderc.com/products/details/tattu-2300-75c-4s1p-xt60 ; nextfpv, gravesrc, rcdrone | 105 x 35 x 29 (two EU retailers: 105 x 33 x 28), 14 AWG, discharge lead about 100 mm (one says 35/60 mm: conflict), balance lead about 65 mm, JST-XH 5-pin | lead length, corner radius, XT60 body (Amass drawing not fetched): measure on arrival |
| RadioMaster RP3 V2 | https://www.readymaderc.com/products/details/85670-radiomaster-rp3-expresslrs-2-4ghz-nano-receiver-v2 | 22 x 13 x 4 mm, 4.6 g with antennas, 2 x 65 mm T antennas, CRSF wire | header position: measure. CAD box 20 x 12 is wrong |
| TBS M10Q | https://www.readymaderc.com/products/details/86501-tbs-m10q-gps-receiver-with-glonass | 25 x 25 x 7.7 mm, 13.5 g, QMC5883 | connector (JST-SH 6-pin ASSUMED), cable, patch size: measure |
| RMRC MS4525 | https://www.readymaderc.com/products/details/rmrc-digital-air-speed-sensor-pixhawk-ii-2 | 4-pin JST-GH, 15 cm cable, 2/4 mm tube about 0.5 m | board size, pitot size: not published (ask RMRC); CAD values are EST |
| Linkage set | https://www.readymaderc.com/products/details/rmrc-10pc-pushrod-linkage-set-control-horn | 1.2 mm rods, clevises, 20 mm horns (BOM text) | horn hole spacing/base: measure |
| XT60, JST-GH, JR plugs | maker datasheets not fetched | standard published parts | look up at implementation |

## 3. Wing section

- A documents give only 9.5 % t/c (`COORDS` comment; review/QP-3/CAD.md section 6 item 1). `a_aero.py` says CM0 0.015 "S5010-like" (EST), CLMAX 0.75 (MISSION.md, EST), lift slope from a Helmbold formula, not a section polar. I found no named airfoil in concept A files.
- A real named section must be chosen; a NACA00xx plus cubic camber cannot be "exactly" the aircraft, and the foam template, servo pocket, cove, plate seat, tray slot and spar fit all derive from `zu/zl`.
- Candidate: **S5010**, `subsystems/wing/s5010.dat` (also `team/B2/airfoils/s5010.dat`). Basis: K09-L adopted it (params/CHANGE-LOG.md D-02: reflexed tailless section, t/c 0.0982, trimmed CLmax 0.80) and a_aero's CM0 is already "S5010-like". t/c 9.82 % vs 9.5 % is +0.8 mm at 245 mm chord. MH 45 (pre-D-02 K09-L section) is the other repo precedent; its .dat was not found. No basis in the repo for any other.
- Decision for the parent. Implementation is one line: `COORDS = k9.read_dat(path)`.
- Re-run if it changes: `cad_mass.py` (CG, hinge inertia), `stop_check.py` and the pose collision runs (balance pocket, caps, cove, bosses), servo pocket vs lower skin, pack bay and plate seat, `a_aero.py` (CM0, NP 40.7 mm, CLMAX, trim, then SITL cases), `flutter_a.py`, structures shear at the spar (depth at x 60 mm), then assembly_check and collide once.

## 4. Modelling method, effort, gates at risk (effort is an estimate)

| Item | Method | Effort | Gates at risk |
|---|---|---|---|
| Prop blades | per blade a `loft` along the radius from PE0 stations (12-16): section loop scaled to chord, rotated in-plane by pitch; hub = revolve; adapter = tube; second blade from mirrored loops | 1 d | keep-out cylinders stay as the gate (real blade lies inside); watch hub/blade root against the cup |
| Motor | revolve of the bell profile, stator tube, base-ring prism with 4 `cut_cylinder` holes, shaft + clip, leads as wires | 0.5 d after the JPEG is read | cup plate, prop-to-cup axial gap |
| ESC | PCB prism with 4 holes, FET boxes, pads, capacitor revolve, lead wires | 0.5 d | plate, FC above, wire endpoints use pad z |
| Pack | chamfered-corner prism, XT60 as 3 boxes, balance plug, 14 AWG wires | 0.5 d | **pack bay**: real XT60 plug (about 16 mm, Amass, not fetched) does not fit the 5.5 mm "lead exit"; aft clearance at +10 mm trim |
| FC | 2 PCB prisms (thickness EST 1.6), standoffs, USB board, sockets with real heights | 0.5 d | harness wire start z, plate overlap |
| RX, GPS, airspeed | PCB prism + connectors + antenna wires; fix RX to 22 x 13 | 0.5 d | plate half-width 55 mm: RX edge at 52.5 mm and GPS at 52.5 mm leave 2.5 mm |
| Servo | case prism with ears, output boss at true offset, lead + JR plug | 0.5 d, blocked on drawing or caliper | **servo pocket** (0.5 mm over the case) and arm sweep: highest risk |
| Arm, horn, pushrod, clevis | prism arm and horn with hole rows, rod as cylinders with bends, clevis tubes | 0.5 d | arm/pushrod/skin at the +-21 deg stops |
| Pitot + tubing | revolve probe, silicone line as wire | 0.2 d | none |
| Hub | needs a design first, then a prism/loft shell with 4 arm sockets, bridge, 2 struts, tray pads | 1 d | all `seat` calls with 11 parts |
| Fasteners (about 40) | `hw_screw/nut/washer`, declare hw parts in interfaces.json via gen_interfaces.py | 0.5-1 d | M3 heads (5.5 mm) against cup and prop keep-out; seats now have zero clearance |
| Lumps | itemise wires and plugs; keep a small flagged proxy for ties and shrink | included | mass roll-up: HRN-001 mass is 106 g less the AVN parts today; move mass out of the lump as bodies appear |
| Wire diameters | 20 AWG about 2 mm (EST), 26 AWG about 1.2 mm, 28 AWG about 1 mm | trivial | clearances improve |
| Fin fairing, plate windows, hinge strip | real LE/TE prism, 4 window cuts, optional tape | 0.3 d | none |

Gates most at risk: servo pocket and linkage sweeps at the +-21 deg stops; pack bay with real XT60 and FC standoffs at +10 mm trim; prop-to-cup and prop-to-arm with the real hub/adapter/nut stack (CAD carries an 8 mm hub offset, EST); plate fit of RX and GPS; the 3 mm cup lead hole against a 20 AWG lead with bullets.

## 5. Work order (3 implementers)

All builders sit in one file, so first split (one person, about 30 min) `a_model.py` into `a_model_wing.py`, `a_model_cage.py`, `a_model_prop.py`, `a_model_elec.py`, imported by a_model.py. Then:

| Lane | Parts | Needs | Files |
|---|---|---|---|
| A: aero and structure | S5010 swap and wing/elevon/cap/damper re-derive, hub design, fin fairing, plate windows, cad_mass/stop_check/aero re-runs | parent's section decision | `a_model_wing.py`, `a_model_cage.py` |
| B: propulsion | prop blades, motor, ESC, prop nut/adapter/screw hardware, phase-lead wires | PE0 download, T-Motor JPEG | `a_model_prop.py` |
| C: avionics, power, mechanisms | FC, RX (fix size), GPS, airspeed, pitot, pack + plugs, servos, arms, horns, pushrods, clevises, plugs, wire gauges, interfaces.json regen | servo caliper (parts not ordered before early Dec: use published data and flag) | `a_model_elec.py`, `gen_interfaces.py` |

Final step (one person): reconcile PARTS/EDGES, regenerate interfaces.json, run assembly_check and collide once. Within each lane: biggest visual errors first (props, hub, motors, boards, servos), then connectors, then fasteners. Total about 6-8 person-days (estimate).

## 6. Top risks
1. APC PE0 geometry not read (403/404): the most visible stand-in; needs a browser download.
2. T-Motor drawing is a JPEG, EMAX drawing absent: shaft length, mount patterns and servo ears are unpublished in text. Servo spline 25T (CAD) vs 23T (vendor).
3. Section is invented; choosing S5010 re-opens CG, aero, flutter and pocket gates.
4. Hub has no designed shape: a design task, not only CAD.
5. Real plugs and leads will fill pack-bay and plate corners that have 0.5-2.5 mm margin; RX is already undersized by 2 x 1 mm.
6. Wire diameters (4 mm motor leads) are about twice real 20 AWG, so wire clearances are currently pessimistic.
