# Design team (agent roles) — configured for K09-L

Organised like a real aircraft engineering team: **each agent has exactly one role** and does only that, as well as
it can. Disciplines that touch a subsystem work on it together (e.g. the wing has an aero engineer, a structural
engineer and a CAD designer), coordinated by the leads and the integrator. Rows marked **K09-L:** were re-scoped
by the chief engineer (A1, 2026-11-09) for the chosen configuration (`CONFIGURATION.md`); one row is inactive.

## A. Leadership and systems
| # | Role | Single responsibility |
|---|---|---|
| A1 | Chief engineer / integrator | Configuration-level decisions, resolves conflicts and change requests, owns `params.json`, `mass_budget.json`, `README.md` |
| A2 | Systems engineer | Requirements, verification matrix, traceability of every requirement to a check. **K09-L:** map P1–P25 onto the `R-…` ids in `params/claims.json` (extend, do not duplicate) |
| A3 | Mass-properties engineer | Mass, CG and inertia budget; tracks every part against the 2.6 kg gate and the allocations in `params/mass_budget.json` |
| A4 | Configuration / interface manager | Interface knowledge graph, joint-stack tables, nothing floating. **K09-L:** eleven subsystems, prefixes `WNG FIN POD GER PRP PWR AVN HRN MEC TRN FSW` |
| A5 | CAD lead | Fusion framework, model integrity, `check.py`, assembly build order (`fusion/modules.txt` from the README subsystem list) |

## B. Aerodynamics
| # | Role | Single responsibility |
|---|---|---|
| B1 | Aero performance engineer | Whole-aircraft sizing and performance (hover, 90° pitch-over transition corridor, cruise, endurance). **K09-L:** first job is the transition-vs-cruise speed margin at the 2.6 kg gate (`CL-A1-TRANSITION-GATE` fails by 0.3 %) |
| B2 | Wing aero engineer | Airfoil (MH 45-type, XFOIL at Re 2–4e5), planform, twist, stall behaviour, elevon hinge moments. **K09-L:** no ailerons; elevons |
| B3 | Stability and control engineer | **K09-L:** no tail. Neutral point and CG range of the plank wing with fins (AVL), elevon sizing (15–25 % area, freeze on the twin), hover authority from motor differential, cruise authority from elevons, transition handling |
| B4 | Rotor / propeller aero engineer | Prop selection (11×4.5MR vs the 11×4.7 table), rotor–fin and rotor–tube interaction (download), lightly loaded cruise efficiency, prop-wash on elevons and the pitot |

## C. Structures
| # | Role | Single responsibility |
|---|---|---|
| C1 | Loads engineer | Load cases (flight, gust, hover, transition, fin-tip landing, tip-over, transport, handling) for every structure |
| C2 | Wing structures engineer | Spar, foam core, tape skin, spar slot bond, local bearing where the fin saddles load the spar |
| C3 | Pod structures engineer | **K09-L:** was fuselage. Pod load path, pack retention in a crash, tray, hatch, pod-to-wing bond |
| C4 | Fin / motor-tube structures engineer | **K09-L:** was booms. Fins, vertical motor tubes, motor mounts, tube-to-spar saddles and the 0.18 m tube-to-spar offset; stiffness and first bending/torsion frequencies against motor RPM |
| C5 | Landing / impact engineer | **K09-L:** fin-tip feet. Hard vertical landing, tip-over in wind and on slopes, crash energy path protecting pack and avionics, foot replaceability |
| C6 | Joints and fasteners engineer | Every bolted/bonded joint: sizing, thread engagement, inserts, torque; bonds into foam and foam board |

## D. Mechanical design (Fusion CAD)
| # | Role | Single responsibility | Subsystem folder |
|---|---|---|---|
| D1 | Wing designer | Wing CAD from B2/C2 inputs: one-piece core, spar, elevon panels, pockets | `subsystems/wing/` |
| D2 | Pod designer | **K09-L:** was fuselage. Centre pod, tray, hatch, pack bay, GPS mast, pitot mount | `subsystems/pod/` |
| D3 | Fin and motor-tube designer | **K09-L:** was booms. Fins, motor tubes, motor mounts, saddles, fin-tube clips, ESC pads | `subsystems/fins/` |
| D4 | Tail designer | **Inactive for K09-L** (no tail; the fins are D3's) | — |
| D5 | Landing designer | **K09-L:** four crushable feet on the fin TE tips, contact protection | `subsystems/landing/` |
| D6 | Mechanisms designer | Elevon hinges, servo mounts, horns, pushrods, inter-panel links. **K09-L:** no tilt mechanism | `subsystems/mechanisms/` |
| D7 | Transport and packaging designer | One-piece box with spar cradles, prop tray, 5-minute field set-up | `subsystems/transport/` |

## E. Propulsion and energy
| # | Role | Single responsibility | Subsystem folder |
|---|---|---|---|
| E1 | Propulsion engineer | Motor/ESC/prop selection and margins (T/W ≥ 2.0 at 2.6 kg, current, cruise efficiency at ~1 N per prop). **K09-L:** also the designer of `propulsion` (envelopes of motors, ESCs, props) | `subsystems/propulsion/` |
| E2 | Battery / energy engineer | Pack selection (4S 6500, weigh it), endurance budget, charging, storage and transport safety | — |
| E3 | Thermal engineer | Motor, ESC and pack temperatures; ESCs in the fin prop-wash; field-ambient ceiling as an output | — |

## F. Electrical and avionics
| # | Role | Single responsibility | Subsystem folder |
|---|---|---|---|
| F1 | Power distribution engineer | Disconnect (AS150U vs XT60 decision), distribution, wire sizing for 24 A hover / 120 A momentary, protection, UBEC. **K09-L:** also the designer of `power` | `subsystems/power/` |
| F2 | Harness engineer | Wire list, routing along the fins and through the wing, connectors, strain relief; the pack plug is the only field disconnect | `subsystems/harness/` |
| F3 | Avionics hardware engineer | Flight controller (stable tailsitter build), GPS, airspeed, placement and EMI. **K09-L:** also the designer of `avionics` | `subsystems/avionics/` |
| F4 | Flight-control software engineer | ArduPilot Plane tailsitter parameter file (`Q_TAILSIT_ENABLE 1`, motor map, gain scheduling), transition logic, failsafes, SITL plan | `subsystems/flight-software/` |
| F5 | RC link, telemetry and ground station engineer | Transmitter, receiver, telemetry radio, ground station setup, range test | — |

## G. Manufacturing
| # | Role | Single responsibility |
|---|---|---|
| G1 | Manufacturing engineer | Process plan per part, hot-wire jig and templates, fixtures, Jacobs Hall capability |
| G2 | Composites and foam specialist | Hot-wire XPS cores, tape skinning, CF tube bonding, foam-board fins |
| G3 | 3D-printing specialist | Printed mounts, saddles, clips, feet, tray: materials, orientation, inserts, print times |
| G4 | Assembly sequence engineer | Build order and work packages; writes the build steps |

## H. Test and safety
| # | Role | Single responsibility |
|---|---|---|
| H1 | Ground test engineer | Thrust stand (one station, 11×4.5MR), bench electrics, structural proof loads, tip-over board, CG check |
| H2 | Flight test engineer | Twin first; then tethered hover → hover → fixed-wing tune → transition at ≥ 50 m → back-transition → landing practice |
| H3 | Safety officer | Risk assessment, FAA / RFS rules, 5 m/s flight card, battery and prop safety, go/no-go |

## I. Program
| # | Role | Single responsibility |
|---|---|---|
| I1 | Procurement / BOM engineer | Single BOM from `cards/K09/cost.csv` + tie-break lines, vendors, lead times (CF tubes first), mid-December order, early electronics order |
| I2 | Schedule planner | January–April build and test schedule with one crash-repair loop, critical path |

## J. Support
| # | Role | Single responsibility |
|---|---|---|
| J1 | Outside research analyst | Comparable tailsitter builds, failure modes (post-handoff dive, descent tumble, yaw), references per discipline |
| J2 | Verification / proof-chain engineer | Claims graph and 3D proof viewer |
| J3 | Technical illustrator | Blender renders and animations |
| J4 | Visual designer | Design system and final visual polish |
| J5 | Technical writer / documentation | Stale-doc cleanup, READMEs, consistent docs |
| J6 | Design review board | Independent critics: one per discipline group (aero, structures, electrical, build-and-test), led by a chair |

## Subsystems and their designers (K09-L)

| Key | Designer | Key | Designer |
|---|---|---|---|
| `wing` | D1 | `power` | F1 |
| `fins` | D3 | `avionics` | F3 |
| `pod` | D2 | `harness` | F2 |
| `landing` | D5 | `mechanisms` | D6 |
| `propulsion` | E1 | `transport` | D7 |
| | | `flight-software` | F4 |

Inactive: **D4**. Everything else is active. Part prefixes and the owner of every part and joint: `README.md`.

## How they work together
1. **A1–A5** set the frame for the chosen configuration (parameters, budgets, interfaces, CAD framework).
2. **Analysis before CAD per subsystem:** aero and loads (B, C1) feed structures (C2–C6), which feed the designers
   (D). Propulsion (E1–E2) feeds power (F1).
3. **Electrical (F)** and **mechanical (D)** run in parallel and meet at interfaces (A4).
4. **Manufacturing (G)**, **test (H)**, **program (I)** and **support (J)** follow the geometry.
5. **J6** reviews each discipline group; **A1** resolves; repeat until the review board signs off.
