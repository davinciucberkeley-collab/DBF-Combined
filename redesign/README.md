# Redesign v1 — K09-L quad tailsitter

Status: `PROPOSED` design frame (A1, 2026-11-09). Configuration decided in [`CONFIGURATION.md`](CONFIGURATION.md);
numbers live in [`params/params.json`](params/params.json); roles in [`TEAM.md`](TEAM.md); rules in
[`BRIEF.md`](BRIEF.md). Reversible until the mid-December order on the conditions in `CONFIGURATION.md`.

## The aircraft

A 1.15 × 0.30 m flat flying wing (hot-wired XPS core, packing-tape skin, one 22 × 20 mm carbon spar, MH 45-type
reflexed section) with two vertical foam-board fins at ±0.32 m span. Each fin carries a vertical 22 mm carbon tube
along its leading edge with a SunnySky X3108S motor and an APC 11 × 4.5MR prop at each end: four fixed motors in
an X, two above and two below the wing. It stands on its four fin trailing-edge tips, takes off as a quadcopter,
pitches 90° nose-down onto the same four motors for cruise, and pitches back up to land. Two elevon pairs give
roll and pitch in cruise; an airspeed sensor schedules the gains. One 4S 6500 mAh pack sits in a pod on the upper
surface. The whole aircraft travels in one piece in one box; field set-up is four props and a pack, five minutes,
one person, no tools. ArduPilot Plane, tailsitter mode. It is the cheapest and fastest-built concept in the study
and the riskiest to fly: any motor failure is a crash, and the flight card is limited to 5 m/s wind, mornings only.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, area | 1.15 × 0.30, 0.345 | m, m² | `params.json#wing` | `CHECKED` |
| Sized mass / hard gate | 2.482 / 2.600 | kg | `team/A1/claims.json#CL-A1-MASS-SIZED` | `CHECKED` |
| Hover T/W at the gate (table / with sag) | 2.43 / 2.26 | — | `CL-A1-HOVER-TW-GATE` | `UNVERIFIED` (thrust table, prop 11×4.5MR) |
| Stall at the gate (CLmax 0.9 `EST`) | 11.6 | m/s | `CL-A1-STALL-GATE` | `UNVERIFIED` |
| Transition ≥ 1.3 Vs at the gate | 15.05 | m/s | `CL-A1-TRANSITION-GATE` | `FAIL` by 0.3 % against 15 m/s cruise: B1/B2 resolve (CR-A1-05) |
| Cruise speed, L/D, power | 15, 5.9, 194 | m/s, —, W | `params.json#performance` | `PROPOSED` |
| Cruise after 2 min hover | 19 (12 pessimistic) | min | `params.json#performance` | `PROPOSED` |
| Hover power / current | 355 / 24 | W / A | `params.json#performance` | `PROPOSED` |
| Hover lean at 5 / 8 m/s | 16 / 36 | ° | `params.json#performance` | `PROPOSED` |
| Tip-over angle, narrow axis | 37 | ° | `CL-A1-TIPOVER` | `CHECKED` |
| Minimum prop clearance (to tube face) | 39 | mm | `CL-A1-PROP-CLEAR` | `UNVERIFIED` |
| Elevon area fraction | 17 | % | `CL-A1-ELEVON-FRAC` | `CHECKED` (B3 sizes) |
| Box, external / loaded | 1.25 × 0.55 × 0.45 / ≤ 6 | m / kg | `params.json#requirements` | `PROPOSED` (measure two cars) |
| Spend pessimistic / reserve / one crash | $1 679 / $321 / $309 | USD | `CL-A1-RESERVE` | `CHECKED` |
| Build to first hover | ≤ 90 (plan 70–85) | h | `params.json#requirements` | `PROPOSED` |

Re-check everything: `python -I redesign/team/A1/frame_claims.py` then `python -I redesign/proofs/build_graph.py`.

## General arrangement

![K09-L general arrangement, three views to scale](team/A1/ga-3view.svg)

`FIG A1-01 — General arrangement, 1 m = 500 px, drawn from params.json by team/A1/draw_ga.py.`

**Frame** (every CAD module, `interfaces.json`, the viewer and every analysis): metres, right-handed.
Origin at the wing root leading edge on the chord line. **x aft** (0 at the LE, 0.30 at the TE), **y to the right
wing tip**, **z up** in cruise attitude. In hover the nose points up and +x points at the ground. Symmetry plane
XZ. Fusion receives cm through `fusionkit`.

| Station | x | y | z | Unit | What is there |
|---|---|---|---|---|---|
| Wing LE / TE | 0 / 0.300 | ±0.575 | 0 | m | one-piece XPS core, chord 0.30, t/c 9.85 % (30 mm) |
| Spar centreline | 0.080 | −0.50 … +0.50 | 0 | m | CF 22 × 20 × 1 000 mm in a slot, 26.7 % chord |
| CG target (range) | 0.060 (0.045–0.075) | 0 | 0 (−0.02 … +0.03) | m | 20 % chord; B3 fixes the range from AVL |
| Pod | −0.02 … 0.18 | ±0.05 | 0.015 … 0.075 | m | pack, FC, RX, hatch; pack slides ±0.03 for trim |
| Fins | −0.10 … 0.30 | ±0.32 | ±0.19 | m | foam board, chord 0.40, height 0.38 |
| Motor tubes | −0.10 | ±0.32 | −0.21 … +0.21 | m | CF 22 × 20, 0.42 m, along the fin LE |
| Motors (mount face) | −0.10 | ±0.32 | ±0.19 | m | stations `UR` `UL` `LR` `LL`; shaft along −x |
| Prop planes | −0.15 | ±0.32 | ±0.19 | m | ⌀ 0.279 m; vertical pair gap 0.10 m, lateral 0.36 m |
| Feet | 0.30 … 0.31 | ±0.32 | ±0.19 | m | crushable printed feet on the fin TE tips; footprint 0.64 × 0.38 |
| Elevons (per side) | 0.234 … 0.300 | 0.07–0.30 and 0.34–0.56 | 0 | m | 22 % chord, two panels on one servo |
| Pitot | B4/F3 place it out of the prop wash | | | | `PROPOSED` wing LE at y ≈ 0.15 or pod nose |

## Subsystems: who owns every part

Folders under `subsystems/<key>/` (standard files: `SPEC.md`, `parts.csv`, `interfaces.json`, `params.json`,
`fusion/<key>.py`, `BUILD.md`). Part ids `<PREFIX>-NNN`. Each physical part has exactly one owner.

| Key | Prefix | Designer (CAD) | Analysis · structures | Owns these parts |
|---|---|---|---|---|
| `wing` | `WNG` | D1 | B2 · C2 | XPS core (one piece), tape skin, CF spar, the four elevon panels (foam), spar slot, servo pockets, pod recess, wingtip edge tape, FAA label |
| `fins` | `FIN` | D3 | B3 (vertical surfaces) · C4 | 2 foam-board fins, 2 CF motor tubes, 4 printed motor mounts, 2 tube-to-spar saddles, fin-to-tube clips, fin-to-wing joint parts, ESC mounting pads |
| `pod` | `POD` | D2 | C3 | pod shell, printed tray, hatch, pack strap, GPS mast, pitot boom mount, pod-to-wing attachment |
| `landing` | `GER` | D5 | C5 | 4 crushable feet, contact-point protection |
| `propulsion` | `PRP` | E1 | E1 · B4 · E3 | 4 motors, 4 ESCs, 4 props, adapters, prop nuts, motor spares |
| `power` | `PWR` | F1 | F1 · E2 · E3 | flight packs, main disconnect, power distribution / ESC power leads, UBEC, current-voltage sensor |
| `avionics` | `AVN` | F3 | F3 · F5 | flight controller, GPS/compass, receiver, airspeed sensor + pitot, telemetry, vibration mounts |
| `harness` | `HRN` | F2 | F1 | every wire and connector between parts, routes, supports, strain relief, service loops |
| `mechanisms` | `MEC` | D6 | B2/B3 (hinge moments) · C6 | elevon tape hinges, 2 servos, horns, pushrods, servo covers, inter-panel links |
| `transport` | `TRN` | D7 | C1 (transport loads) | box, spar cradles, prop tray, field checklist — all `flight: false` |
| `flight-software` | `FSW` | F4 | — | ArduPilot parameter file, output map, failsafes, SITL plan (no parts) |

Mass allocations (flying mass, g) are in `params/mass_budget.json`, written from `params.json#mass.allocation_g`
and read by `merge_check.py`, `check.py` and the viewer. A3 refines them in `MASS-CG.md` through a change request.

| Subsystem | wing | fins | pod | landing | propulsion | power | avionics | harness | mechanisms | growth (A1) | **sized** | **gate** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Allocation (g) | 378 | 410 | 90 | 24 | 430 | 600 | 90 | 60 | 50 | 350 | **2 482** | **2 600** |

## Joints: both sides of every interface

The owner declares the edge in its `interfaces.json` with the joint stack (fastened) or wire block (electrical);
the other side `acknowledges` it. C6 sizes every fastened joint; A4 merges and checks.

| Joint | Side A (subsystem: part) | Side B | Owner | Type | Sized by |
|---|---|---|---|---|---|
| Spar in core | wing: spar | wing: core | wing | epoxy bond in slot | C2 |
| Tube-to-spar saddle | fins: saddle | wing: spar (and core) | fins | printed saddle, bonded + strapped | C4, C2 (spar bearing), C6 |
| Fin root to wing | fins: fin | wing: core / skin | fins | bonded + taped | C4 |
| Fin to motor tube | fins: fin | fins: tube | fins | printed clips, epoxy | C4 |
| Motor to mount | propulsion: motor | fins: motor mount | fins | M3 fasteners | C6 |
| Mount to tube | fins: motor mount | fins: tube | fins | clamp or bonded plug | C4, C6 |
| Prop to motor | propulsion: prop + adapter | propulsion: motor | propulsion | prop nut | E1 |
| ESC to fin | propulsion: ESC | fins: ESC pad | fins | strapped / taped | E3 (cooling) |
| Foot to fin tip | landing: foot | fins: fin | landing | printed cap, bonded | C5 |
| Pod to wing | pod: shell | wing: core / skin | pod | bonded + strapped | C3 |
| Pack in pod | power: pack | pod: tray + strap | pod | strap, Velcro | C3, C1 (crash) |
| Avionics mounts | avionics: FC, GPS, RX, airspeed | pod: tray | avionics | M3 / foam tape mounts | F3 |
| Pitot | avionics: pitot | wing: LE or pod: nose | avionics | bonded boom | B4 (placement) |
| Elevon hinge | wing: elevon panel | wing: core TE | mechanisms | tape hinge | D6 |
| Servo in wing | mechanisms: servo | wing: servo pocket | mechanisms | screws / bonded frame | D6, C6 |
| Horn and pushrod | mechanisms: horn, pushrod | wing: elevon panel | mechanisms | bonded horn, clevis | D6 |
| ESC ↔ motor leads | harness: wire | propulsion: ESC, motor | harness | 3 × bullet | F1 (gauge) |
| Pack ↔ disconnect ↔ distribution | harness: wire | power: pack, disconnect, PDB | harness | XT60 / AS150U | F1 |
| Distribution ↔ ESCs, UBEC ↔ FC | harness: wire | power, avionics | harness | soldered / JST | F1, F3 |
| Servo and sensor signals | harness: wire | mechanisms: servos; avionics: FC, GPS, RX, airspeed | harness | servo lead, JST-GH, I2C | F3 |
| Cradles | transport: cradle | wing: spar line | transport | contact, `flight: false` | C1 |

Unresolved joints the designers must solve first (P25): the fin-tube junction (the card's two-layer sandwich is
not flat over a 22 mm tube) and the 0.18 m offset between the motor tube (x = −0.10) and the spar (x = 0.08).

## Directory map

| Path | What |
|---|---|
| `CONFIGURATION.md` · `BRIEF.md` · `TEAM.md` | the decision, the rules, the roles |
| `params/params.json` · `params/mass_budget.json` · `params/claims.json` | top-level numbers · mass allocations · shared requirement and source ids |
| `config-study/` | how K09 was chosen: requirements, morph chart, cards, reviews, tie-break |
| `inputs/` | advisor lessons, mentor guidance, simulation tools, prior decisions |
| `team/<role>/` | each role's SUMMARY.md, reports, scripts, claims, CHANGE-REQUESTS.md |
| `subsystems/<key>/` | CAD and build data per subsystem (table above) |
| `interfaces/` · `fusion/` | knowledge-graph schema and checker · Fusion framework, `build_all.py`, `check.py` |
| `proofs/` | proof chains: `build_graph.py`, `out/CHAIN.md`, 3-D viewer |
| `viewer/` · `blender/` · `manual-kit/` | aircraft viewer · renders and animations · build manual |
| `design-system/` | the one look every visual output follows |
| `reviews/` | tooling review, CDR reports |
| `MASS-CG.md` (A3) · `HANDOFF.md` (A1, final) | mass and CG roll-up · what the team does next |

## Before the mid-December order

Mandatory de-risking from `CONFIGURATION.md`: fly the $40 foam-board twin on the real motors, FC and pack (hold
1 m in 5 m/s, then a transition); tune it as a plain flying wing before any transition; confirm a stable ArduPilot
Plane tailsitter build for the chosen board; measure RFS wind against RCMC1; order electronics and carbon tubes
early (~20 Nov). Reverse to K01-lean on the conditions listed there.
