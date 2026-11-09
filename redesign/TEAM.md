# Design team (agent roles)

Organised like a real aircraft engineering team: **each agent has exactly one role** and does only that, as well as
it can. Disciplines that touch a subsystem work on it together (e.g. the wing has an aero engineer, a structural
engineer and a CAD designer), coordinated by the leads and the integrator. Roles marked *(config)* exist only if the
chosen configuration has that part; the integrator adds or removes them when the configuration is fixed.

## A. Leadership and systems
| # | Role | Single responsibility |
|---|---|---|
| A1 | Chief engineer / integrator | Configuration-level decisions, resolves conflicts and change requests, owns `params.json` |
| A2 | Systems engineer | Requirements, verification matrix, traceability of every requirement to a check |
| A3 | Mass-properties engineer | Mass, CG and inertia budget; tracks every part against the chosen design's take-off mass limit |
| A4 | Configuration / interface manager | Interface knowledge graph, joint-stack tables, nothing floating |
| A5 | CAD lead | Fusion framework, model integrity, `check.py`, assembly build order |

## B. Aerodynamics
| # | Role | Single responsibility |
|---|---|---|
| B1 | Aero performance engineer | Whole-aircraft sizing and performance (hover, transition, cruise, endurance) |
| B2 | Wing aero engineer | Airfoil, planform, twist, stall behaviour, control-surface sizing on the wing |
| B3 | Stability and control engineer | Tail sizing, static margin, CG limits, control authority in hover and cruise |
| B4 | Rotor / propeller aero engineer | Prop selection, rotor–wing interaction, prop-wash on surfaces and sensors |

## C. Structures
| # | Role | Single responsibility |
|---|---|---|
| C1 | Loads engineer | Load cases (flight, gust, hover, landing, transport, handling) for every structure |
| C2 | Wing structures engineer | Spar, skins, ribs/core, wing joint and wing attachment strength and stiffness |
| C3 | Fuselage structures engineer | Fuselage load path, cut-outs, mounts |
| C4 | Rotor-mount / boom structures engineer *(config)* | Booms/arms, motor mounts, vibration and stiffness |
| C5 | Landing / impact engineer | Gear or skids, hard-landing and crash energy, tip-over |
| C6 | Joints and fasteners engineer | Every bolted/bonded joint: sizing, thread engagement, inserts, torque |

## D. Mechanical design (Fusion CAD)
| # | Role | Single responsibility |
|---|---|---|
| D1 | Wing designer | Wing CAD from B2/C2 inputs |
| D2 | Fuselage designer | Fuselage CAD, hatches, trays, battery bay |
| D3 | Rotor-mount / boom designer *(config)* | Booms, arms, motor mounts CAD |
| D4 | Tail designer *(config)* | Tail surfaces and attachment CAD |
| D5 | Landing gear designer | Gear/skids CAD |
| D6 | Mechanisms designer | Hinges, servo mounts, linkages, any tilt mechanism *(config)* |
| D7 | Transport and packaging designer | How it comes apart, packs in a car, and goes back together fast |

## E. Propulsion and energy
| # | Role | Single responsibility |
|---|---|---|
| E1 | Propulsion engineer | Motor/ESC/prop selection and margins (thrust-to-weight, current, efficiency) |
| E2 | Battery / energy engineer | Pack selection, endurance budget, charging, storage and transport safety |
| E3 | Thermal engineer | Motor, ESC and battery temperatures; cooling paths |

## F. Electrical and avionics
| # | Role | Single responsibility |
|---|---|---|
| F1 | Power distribution engineer | Disconnect, distribution, wire sizing, protection, BECs |
| F2 | Harness engineer | Wire list, routing, connectors, strain relief, disconnects at removable joints |
| F3 | Avionics hardware engineer | Flight controller, sensors, GPS, airspeed, placement and EMI |
| F4 | Flight-control software engineer | ArduPilot/PX4 configuration, transition logic, failsafes, SITL |
| F5 | RC link, telemetry and ground station engineer | Transmitter, receiver, telemetry radio, ground station setup |

## G. Manufacturing
| # | Role | Single responsibility |
|---|---|---|
| G1 | Manufacturing engineer | Process plan per part, fixtures and jigs, Jacobs Hall capability |
| G2 | Composites and foam specialist | Carbon, fibreglass, foam and balsa processes |
| G3 | 3D-printing specialist | Printed-part design rules, materials, orientation, print times |
| G4 | Assembly sequence engineer | Build order and work packages; writes the build steps |

## H. Test and safety
| # | Role | Single responsibility |
|---|---|---|
| H1 | Ground test engineer | Bench, thrust-stand, structural and systems tests |
| H2 | Flight test engineer | Staged flight-test plan and cards |
| H3 | Safety officer | Risk assessment, FAA rules, battery and prop safety, go/no-go criteria |

## I. Program
| # | Role | Single responsibility |
|---|---|---|
| I1 | Procurement / BOM engineer | Single BOM, vendors, lead times, mid-December order |
| I2 | Schedule planner | January–April build and test schedule, critical path |

## J. Support
| # | Role | Single responsibility |
|---|---|---|
| J1 | Outside research analyst | Comparable builds, failure modes, references for every discipline |
| J2 | Verification / proof-chain engineer | Claims graph and 3D proof viewer |
| J3 | Technical illustrator | Blender renders and animations |
| J4 | Visual designer | Design system and final visual polish |
| J5 | Technical writer / documentation | Stale-doc cleanup, READMEs, consistent docs |
| J6 | Design review board | Independent critics: one per discipline group (aero, structures, electrical, manufacturing), led by a chair |

## How they work together
1. **A1–A5** set the frame for the chosen configuration (parameters, budgets, interfaces, CAD framework).
2. **Analysis before CAD per subsystem:** aero and loads (B, C1) feed structures (C2–C6), which feed the designers
   (D). Propulsion (E1–E2) feeds power (F1).
3. **Electrical (F)** and **mechanical (D)** run in parallel and meet at interfaces (A4).
4. **Manufacturing (G)**, **test (H)**, **program (I)** and **support (J)** follow the geometry.
5. **J6** reviews each discipline group; **A1** resolves; repeat until the review board signs off.
