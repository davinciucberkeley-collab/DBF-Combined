# Redesign v1 — K09-L quad tailsitter

Status: `PROPOSED` design frame, revision **A1-R2** (A1, 2026-11-09). Configuration decided in
[`CONFIGURATION.md`](CONFIGURATION.md); numbers live in [`params/params.json`](params/params.json) and every change
to them in [`params/CHANGE-LOG.md`](params/CHANGE-LOG.md); roles in [`TEAM.md`](TEAM.md); rules in
[`BRIEF.md`](BRIEF.md). Reversible until the mid-December order on the conditions in `CONFIGURATION.md`.

## The aircraft

A 1.15 × 0.32 m flat flying wing (hot-wired XPS core, packing-tape skin, one 22 × 20 mm carbon spar at 25 % chord,
Selig S5010 reflexed section) with two vertical foam-board fins at ±0.32 m span. At each fin a vertical 22 mm carbon
tube passes **through the wing core at x = 0.045 m**, 35 mm ahead of the spar, with a SunnySky X3108S motor and an
APC 11 × 5.5MR prop at each end: four fixed motors in an X, two above and two below the wing, each canted 3° for hover
yaw. The fin is two half-fins (above and below the wing) from the tube back to the wing trailing edge. It stands on
four crushable feet at the fin trailing-edge tips, takes off as a quadcopter, pitches 90° nose-down onto the same four
motors for cruise at 16 m/s, and pitches back up to land. Two elevon pairs give roll and pitch in cruise; an airspeed
sensor on the pod nose schedules the gains. One 4S 6500 mAh pack sits in a pod on the upper surface, its nose 105 mm
ahead of the wing. The whole aircraft travels in one piece in one box; field set-up is four props, the pitot boom and
a pack, five minutes, one person, no tools. ArduPilot Plane, tailsitter mode. It is the cheapest and fastest-built
concept in the study and the riskiest to fly: any motor failure is a crash, and the flight card is limited to 5 m/s
wind, mornings only.

## Key numbers

All at the 2.6 kg gate. Re-check: `python -I redesign/team/A1/frame_claims.py` then
`python -I redesign/proofs/build_graph.py`.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, area, AR | 1.15 × 0.32, 0.368, 3.59 | m, m², — | `CL-A1-WING-AREA` | `CHECKED` |
| Allocations / sized / hard gate | 2 200 / 2 550 / 2 600 | g | `CL-A1-MASS-SIZED` | `CHECKED` |
| A3 roll-up, basic / predicted by maturity | 2 147 / 2 495 | g | `CL-A3-MASS-PREDICTED` | `UNVERIFIED` (estimates) |
| Hover T/W, fresh pack with the 100 A limiter / worst pack state | 2.49 / 1.79 | — | `CL-A1-HOVER-TW-GATE`, `-SAG` | `UNVERIFIED` (thrust stand) |
| Stall, trimmed CLmax 0.80 | 11.86 | m/s | `CL-A1-STALL-GATE` | `UNVERIFIED` (B3 re-derives trimmed, D-21) |
| Transition ≥ 1.3 Vs vs cruise | 15.42 ≤ 16 | m/s | `CL-A1-TRANSITION-GATE` | `CHECKED` (+4 %) |
| Cruise speed, L/D, power | 16, 5.6, 307 (181–216 with the 11×5.5MR) | m/s, —, W | `params.json#performance` | `PROPOSED` (B1 re-runs) |
| Cruise after 2 min hover, base / pessimistic | 12.3 / 6.4 | min | `CL-B1-CRUISE-TIME`, `CL-E2-CRUISE-MIN-PESS` | `UNVERIFIED` |
| Hover power / pack current | 400 / 27 | W / A | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| Hover lean at 5 / 8 m/s | 15 / 34 | ° | `CL-B1-LEAN-5MS`, `-8MS` | `PROPOSED` |
| Cruise Cn_β with the tubes at x 0.045 | +0.044 (was −0.105) | /rad | `CL-B3-CNB` option O4b | `UNVERIFIED` (B3 re-runs at R1) |
| CG target (range) | 0.044 (0.040–0.049) | m | `CL-B3-CG-TARGET` | `UNVERIFIED` (D-17) |
| Tip-over angle, narrow axis | 30.6 | ° | `CL-A1-TIPOVER` | `CHECKED` (+2 %; D5 splays the feet) |
| Minimum prop clearance (disc edge to wing plane / to tube face) | 35 / 39 | mm | `CL-A1-PROP-CLEAR` | `UNVERIFIED` |
| Elevon area fraction | 17.2 | % | `CL-A1-ELEVON-FRAC` | `CHECKED` |
| Box, external / slack / loaded | 1.25 × 0.55 × 0.50 / 25 mm / ≤ 6 kg | m, mm, kg | `CL-A1-BOX-FIT` | `PROPOSED` (measure two cars) |
| Spend pessimistic / reserve / one crash | $1 679 / $321 / $309 | USD | `CL-A1-RESERVE` | `CHECKED` |
| Build to first hover | ≤ 90 (plan 70–85) | h | `params.json#requirements` | `PROPOSED` |

## General arrangement

![K09-L general arrangement, three views to scale](team/A1/ga-3view.svg)

`FIG A1-01 — General arrangement at revision A1-R2, 1 m = 500 px, drawn from params.json by team/A1/draw_ga.py.`

**Frame** (every CAD module, `interfaces.json`, the viewer and every analysis): metres, right-handed.
Origin at the wing root leading edge on the chord line. **x aft** (0 at the LE, 0.32 at the TE), **y to the right
wing tip**, **z up** in cruise attitude. In hover the nose points up and +x points at the ground. Symmetry plane
XZ. Fusion receives cm through `fusionkit`.

| Station | x | y | z | Unit | What is there |
|---|---|---|---|---|---|
| Wing LE / TE | 0 / 0.320 | ±0.575 | 0 | m | one-piece XPS core, S5010, chord 0.32, t/c 9.82 % (31 mm) |
| Spar centreline | 0.080 | −0.50 … +0.50 | +0.0066 | m | CF 22 × 20 × 1 000 mm in a slot, 25 % chord, on the camber line |
| CG target (range) | 0.044 (0.040–0.049) | 0 | 0 (−0.02 … +0.03) | m | 13.8 % chord; B3 re-derives at R1 geometry before any station freezes (D-17) |
| Pod | −0.105 … 0.095 | ±0.05 | 0.015 … 0.085 | m | pack (bay ≥ 0.160 × 0.052 × 0.053), FC, RX, hatch, GPS mast; pack slides ±0.03 for trim |
| Motor tubes | 0.045 | ±0.32 | −0.21 … +0.21 | m | CF 22 × 20, 0.42 m, vertical through a 22 mm hole in the core |
| Through-core block | 0.045 / 0.080 | ±0.32 | 0 | m | printed PETG block bonded in a core cut-out: vertical bore for the tube, spanwise bore for the spar, 35 mm apart |
| Half-fins (4) | 0.045 … 0.320 | ±0.32 | 0 … ±0.19 | m | foam board 4.8 mm, chord 0.275, fin LE on the tube, TE = wing TE; fin height 0.38 |
| Motors (mount face) | 0.045 (plate 0.034) | ±0.32 | ±0.19 | m | stations `UR` `UL` `LR` `LL`; shaft along −x, 3° tangential cant |
| Prop planes | −0.005 | ±0.32 | ±0.19 | m | ⌀ 0.279 m; vertical pair gap 0.10 m, lateral 0.36 m; disc edge 35 mm above the wing plane; tube face 39 mm behind the plane |
| Feet | 0.320 … 0.365 | ±0.32 | ±0.19 | m | crushable printed feet, 45 mm, stroke ≥ 40 mm; footprint 0.64 × 0.38; D5 may splay outward |
| Elevons (per side) | 0.2496 … 0.320 | 0.07–0.30 and 0.34–0.56 | 0 | m | 22 % chord, two panels on one servo ≥ 3.04 kgf·cm |
| Pitot tip | −0.185 | 0 | 0.045 | m | plug-in boom on the pod nose, 180 mm ahead of the prop planes |
| Box (external) | 1.25 × 0.55 × 0.50 | | | m | props off, pitot boom off: envelope 1.15 × 0.47 × 0.425; 25 mm walls |

## Subsystems: who owns every part

Folders under `subsystems/<key>/` (standard files: `SPEC.md`, `parts.csv`, `interfaces.json`, `params.json`,
`fusion/<key>.py`, `BUILD.md`). Part ids `<PREFIX>-NNN`. Each physical part has exactly one owner.
`parts.csv#mass_g` is **per unit** (line mass = qty × mass_g); a multi-instance part has one `interfaces.json`
node per instance, id `<part_id>-<UR|UL|LR|LL|L|R>`, each with its own `cg_xyz_m` (CR-A3-09).

| Key | Prefix | Designer (CAD) | Analysis · structures | Owns these parts |
|---|---|---|---|---|
| `wing` | `WNG` | D1 | B2 · C2 | XPS core (one piece, with the two tube holes and the block cut-outs), tape skin, CF spar, the four elevon panels (foam), spar slot, servo pockets, pod recess, wingtip edge tape, FAA label |
| `fins` | `FIN` | D3 | B3 (vertical surfaces) · C4 | 4 foam-board half-fins, 2 CF motor tubes, 4 printed canted motor mounts, 2 through-core blocks, fin-to-tube clips, fin-to-wing joint parts, ESC mounting pads |
| `pod` | `POD` | D2 | C3 | pod shell, printed tray, hatch, pack strap, GPS mast, pitot boom mount, carry point, pod-to-wing attachment |
| `landing` | `GER` | D5 | C5 | 4 crushable feet, contact-point protection |
| `propulsion` | `PRP` | E1 | E1 · B4 · E3 | 4 motors, 4 ESCs, 4 props, adapters, prop nuts, motor spares |
| `power` | `PWR` | F1 | F1 · E2 · E3 | flight packs, main disconnect, power module / PDB, UBEC (if fitted), current-voltage sensor |
| `avionics` | `AVN` | F3 | F3 · F5 | flight controller, GPS/compass, receiver, airspeed sensor + pitot boom, telemetry, vibration mounts |
| `harness` | `HRN` | F2 | F1 | every wire and connector between parts (incl. the ESC power and motor leads), routes, supports, strain relief, service loops |
| `mechanisms` | `MEC` | D6 | B2/B3 (hinge moments) · C6 | 2 servos, horns, pushrods, servo covers, inter-panel links, hinge tape (the hinge edge is declared by `wing`) |
| `transport` | `TRN` | D7 | C1 (transport loads) | box, spar cradles with ≥ 70 mm crush foam, prop tray, field checklist — all `flight: false` |
| `flight-software` | `FSW` | F4 | — | ArduPilot parameter file, output map, failsafes, SITL plan (no parts) |

Mass allocations (flying mass, g) are in `params/mass_budget.json`, written from `params.json#mass.allocation_g`
and read by `merge_check.py`, `check.py` and the viewer. A3 tracks every part against them in `MASS-CG.md`;
changes go through `params/CHANGE-LOG.md`.

| Subsystem | wing | fins | pod | landing | propulsion | power | avionics | harness | mechanisms | A1 reserve | **sum** | **gate** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Allocation (g) | 405 | 370 | 105 | 40 | 440 | 595 | 75 | 105 | 65 | 400 | **2 600** | **2 600** |

The 400 g reserve covers A3's growth by maturity (348 g predicted) and the 100 g first-build overrun; it is
released only through a change request. The pack (550 g carried, listings 503–680 g) is the largest unknown.

## Joints: both sides of every interface

The owner declares the edge in its `interfaces.json` with the joint stack (fastened) or wire block (electrical);
the other side `acknowledges` it. Rules (CHANGE-LOG D-20): an owner holds one side of every edge it declares;
for an electrical edge `part_a` is the supply side; the harness owns every wire, the `power` subsystem owns the
boxes (pack, disconnect, power module, PDB, UBEC). C6 sizes every fastened joint; A4 merges and checks.

| Joint | Side A (subsystem: part) | Side B | Owner | Type | Sized by |
|---|---|---|---|---|---|
| Spar in core | wing: spar | wing: core | wing | epoxy bond in slot | C2 |
| Through-core block | fins: block | wing: spar, core | fins | printed PETG block, bonded; tube and spar bores 35 mm apart | C4 (fin-joint moment, C1 case G2 10.7 N·m), C2 (spar bearing), C6 |
| Tube in block | fins: tube | fins: block | fins | bonded plug or clamp | C4, C6 |
| Half-fin root to wing | fins: half-fin | wing: core / skin | fins | bonded + taped | C4 |
| Half-fin to motor tube | fins: half-fin | fins: tube | fins | printed clips, epoxy | C4 (mode ≥ 20 % from 80–330 Hz) |
| Motor to mount | propulsion: motor | fins: motor mount (3° cant) | fins | M3 fasteners | C6 |
| Mount to tube | fins: motor mount | fins: tube | fins | clamp or bonded plug; the mount fails before the tube (D-23) | C4, C6 (prop-nut case 3.2 N·m) |
| Prop to motor | propulsion: prop + adapter | propulsion: motor | propulsion | prop nut | E1 |
| ESC to fin | propulsion: ESC | fins: ESC pad | fins | strapped / taped, in the slipstream | E3 (cooling) |
| Foot to fin tip | landing: foot | fins: half-fin | landing | printed cap, bonded, replaceable in ≤ 10 min | C5 |
| Pod to wing | pod: shell | wing: core / skin | pod | bonded + strapped; nose 105 mm ahead of the LE | C3 |
| Pack in pod | power: pack | pod: tray + strap | pod | strap, Velcro; ±0.03 m slide | C3, C1 (12 g crash) |
| Avionics mounts | avionics: FC, GPS, RX, airspeed | pod: tray | avionics | M3 / foam tape mounts | F3 |
| Pitot boom | avionics: pitot boom | pod: nose mount | avionics | plug-in, removed for transport | B4 (placement), F3 |
| Elevon hinge | wing: core TE | wing: elevon panel | wing (D6 designs) | tape hinge, bevelled lower edge | D6 |
| Servo in wing | mechanisms: servo | wing: servo pocket | mechanisms | screws / bonded frame | D6, C6 |
| Horn and pushrod | mechanisms: horn, pushrod | wing: elevon panel | mechanisms | bonded horn, clevis | D6 |
| Inter-panel link | mechanisms: link | wing: inboard and outboard panels | mechanisms | crosses the lower half-fin root through a slot | D6, D3 |
| Motor leads | harness: wire (supply: ESC) | propulsion: motor | harness | 3 × bullet | F1 (gauge) |
| ESC power leads | harness: wire (supply: PDB) | propulsion: ESC | harness | soldered, 16 or 18 AWG | F1 |
| Pack ↔ disconnect ↔ PDB | harness: wire (supply: pack) | power: disconnect, PDB | harness | XT60 or AS150U (F1 decides) | F1 |
| UBEC / BEC ↔ FC, servos | harness: wire (supply: BEC) | avionics: FC; mechanisms: servos | harness | JST / servo lead | F1, F3 |
| Signals | harness: wire (supply: FC) | mechanisms: servos; avionics: GPS, RX, airspeed | harness | servo lead, JST-GH, I2C | F3 |
| Cradles | transport: cradle | wing: spar line | transport | contact, `flight: false` | C1 |

Joints the designers solve first (P25): the through-core block (D3, C4: it carries the tube, the spar bearing and
the fin root in one print), the half-fin-to-tube clip whose bonded fin must lift the tube's first mode out of the
80–330 Hz band (`CL-J1-TUBE-MODE-SEP` fails on the bare tube), and the inter-panel link slot in the lower half-fin.

## Directory map

| Path | What |
|---|---|
| `CONFIGURATION.md` · `BRIEF.md` · `TEAM.md` | the decision, the rules, the roles |
| `params/params.json` · `params/CHANGE-LOG.md` · `params/mass_budget.json` · `params/claims.json` | top-level numbers · every change and change-request decision · mass allocations · shared requirement and source ids |
| `config-study/` | how K09 was chosen: requirements, morph chart, cards, reviews, tie-break |
| `inputs/` | advisor lessons, mentor guidance, simulation tools, prior decisions |
| `team/<role>/` | each role's SUMMARY.md, reports, scripts, claims, CHANGE-REQUESTS.md |
| `subsystems/<key>/` | CAD and build data per subsystem (table above) |
| `interfaces/` · `fusion/` | knowledge-graph schema and checker · Fusion framework, `build_all.py`, `check.py`, skeleton |
| `proofs/` | proof chains: `build_graph.py`, `out/CHAIN.md`, 3-D viewer |
| `viewer/` · `blender/` · `manual-kit/` | aircraft viewer · renders and animations · build manual |
| `design-system/` | the one look every visual output follows |
| `reviews/` | tooling review, CDR reports |
| `MASS-CG.md` (A3 roll-up, A1 text) · `HANDOFF.md` (A1, final) | mass and CG roll-up · what the team does next |

## Before the mid-December order

Mandatory de-risking from `CONFIGURATION.md`: fly the $40 foam-board twin on the real motors, FC and pack (hold
1 m in 5 m/s, then a transition); tune it as a plain flying wing before any transition; confirm a stable ArduPilot
Plane tailsitter build for the chosen board; measure RFS wind against RCMC1; order electronics, two packs, the
US-stock carbon tube and the props early (~20 Nov). Weigh the pack and the tube on arrival. Reverse to K01-lean on
the conditions listed there.
