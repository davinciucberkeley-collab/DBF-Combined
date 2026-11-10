# Redesign v1 — K09-L quad tailsitter

Status: `PROPOSED` design frame, revision **A1-R3** (A1, 2026-11-09, after the detail-analysis round). Configuration
decided in [`CONFIGURATION.md`](CONFIGURATION.md); numbers live in [`params/params.json`](params/params.json) and
every change to them in [`params/CHANGE-LOG.md`](params/CHANGE-LOG.md); roles in [`TEAM.md`](TEAM.md); rules in
[`BRIEF.md`](BRIEF.md). Reversible until the mid-December order on the conditions in `CONFIGURATION.md`.

## The aircraft

A 1.15 × 0.32 m flat flying wing (hot-wired XPS core, packing-tape skin, one 22 × 20 mm carbon spar at 25 % chord,
Selig S5010 reflexed section) with two vertical foam-board fins at ±0.32 m span. At each fin a vertical 22 mm carbon
tube passes **through the wing core at x = 0.045 m**, 35 mm ahead of the spar, in a printed through-core block; a
printed mount at each tube end carries a SunnySky X3108S motor with an APC 11 × 5.5MR prop: four fixed motors in
an X, two above and two below the wing, each canted 7° for hover yaw. Each fin is two half-fins (two foam-board
layers, 0.21 m high, from the tube back to the wing trailing edge) braced by a carbon strip to an anchor on the spar.
It stands on four crushable feet at the fin trailing-edge tips, takes off as a quadcopter, pitches 90° nose-down
onto the same four motors for cruise at 16 m/s, and pitches back up to land. Two elevon pairs give roll and pitch in
cruise; an airspeed sensor on the pod nose schedules the gains in fixed-wing flight. One 4S 6500 mAh pack sits in a
pod on the upper surface behind a crush block, its nose 115 mm ahead of the wing. The whole aircraft travels in one
piece in one box; field set-up is four props (one spanner), the pitot boom and a pack: five minutes, one person.
ArduPilot Plane, tailsitter mode, CoreWing F405 Wing V2. It is the cheapest and fastest-built concept in the study
and the riskiest to fly: any motor failure is a crash, and the flight card is limited to 5 m/s wind, mornings only.

## Key numbers

All at the 2.6 kg gate. Re-check: `python -I redesign/team/A1/frame_claims.py` then
`python -I redesign/proofs/build_graph.py`.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, area, AR | 1.15 × 0.32, 0.368, 3.59 | m, m², — | `CL-A1-WING-AREA` | `CHECKED` |
| Allocations / sized / hard gate | 2 324 / 2 594 / 2 600 | g | `CL-A1-MASS-SIZED` | `CHECKED` (+0 %: thin) |
| A3 roll-up, basic / predicted by maturity | 2 145 / 2 492 (at R2 allocations; A3 re-runs) | g | `CL-A3-MASS-PREDICTED` | `UNVERIFIED` (estimates) |
| Hover T/W, fresh pack with the 100 A limiter / worst pack state | 2.49 / 1.89 | — | `CL-A1-HOVER-TW-GATE`, `-SAG` | `UNVERIFIED` (thrust stand) |
| Stall, trimmed CLmax 0.80 (target CG / forward limit) | 11.90 / 11.93 | m/s | `CL-B3-VS-TRIM`, `CL-A1-STALL-GATE` | `UNVERIFIED` |
| Transition ≥ 1.3 Vs at the forward CG vs cruise | 15.51 ≤ 16 | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` (+3 %) |
| Cruise power / current, L/D | 218 (285 pessimistic) / 14.7, 6.9 | W, A, — | `CL-B1-CRUISE-P`, `-I`, `-LD` | `UNVERIFIED` |
| Cruise after 2 min hover, mission base / pessimistic | 13.7 / 7.3 (B1 level cruise 17.0 / 12.7) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` (E2 re-runs) |
| Hover power / pack current | 400 / 27 | W / A | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| Hover lean at 5 / 8 m/s; landing wind limit | 16 / 36; 5.8 | ° ; m/s | `CL-B1-LEAN-*`, `CL-B1-WIND-HOVER-MAX` | `UNVERIFIED` |
| CG range (target), chord fraction | 0.050–0.055 (0.0526), 15.6–17.2 % | m | `CL-B3-CG-FWD`, `-AFT`, `CL-A1-CG-RANGE-*` | `UNVERIFIED` (B3 re-runs at 7°, 0.21 m) |
| Cruise Cn_β, aft CG, 1.3 Vs (0.19 m fins → 0.21 m) | 0.0286 → 0.0373 | /rad | `CL-B3-CNB` | `FAIL` −5 % today → B3 re-run |
| Hover yaw authority / 5 m/s disturbance (3° → 7° cant) | 1.15 → 2.23 | — | `CL-B3-HOVER-YAW-RATIO` | `FAIL` today → B3 re-run |
| Tip-over toward the pod, worst flying CG / corner bound | 32.4 / 30.6 | ° | `CL-C5-TIPOVER-WORST`, `CL-A1-TIPOVER` | `UNVERIFIED` (+2 %) |
| Fin station first mode vs 80–330 Hz, two layers | separation 0.41 (worst 0.33) | — | `CL-C4-D3-SEP` | `UNVERIFIED` (tap test) |
| Wing torsion modes (antisym / sym) | 11.7–14.9 / 21–27 | Hz | `CL-C2-F-TORSION-*` | `UNVERIFIED` (notch + tap test, D-45) |
| Minimum prop clearance (disc edge to wing plane) | 35 | mm | `CL-A1-PROP-CLEAR` | `UNVERIFIED` |
| Elevon area fraction | 17.2 | % | `CL-A1-ELEVON-FRAC` | `CHECKED` |
| Box, external / fit slack / box mass | 1.25 × 0.55 × 0.54 / 17 mm / 3.63 kg | m, mm, kg | `CL-A1-BOX-FIT`, `CL-D7-BOX-H-REQ` | `PROPOSED` (two cars first) |
| Spend pessimistic / reserve / one crash | $1 680 / $320 / $309 | USD | `CL-I1-RESERVE-PESS`, `CL-A1-RESERVE` | `UNVERIFIED` (+3 %) |
| Field ambient ceiling (mission) | 43 | °C | `CL-E3-CEIL-MISSION` | `UNVERIFIED` |
| Build to first hover | ≤ 90 (plan 70–85) | h | `params.json#requirements` | `PROPOSED` |

## General arrangement

![K09-L general arrangement, three views to scale](team/A1/ga-3view.svg)

`FIG A1-01 — General arrangement at revision A1-R3, 1 m = 500 px, drawn from params.json by team/A1/draw_ga.py.`

**Frame** (every CAD module, `interfaces.json`, the viewer and every analysis): metres, right-handed.
Origin at the wing root leading edge on the chord line. **x aft** (0 at the LE, 0.32 at the TE), **y to the right
wing tip**, **z up** in cruise attitude. In hover the nose points up and +x points at the ground. Symmetry plane
XZ. Fusion receives cm through `fusionkit`.

| Station | x | y | z | Unit | What is there |
|---|---|---|---|---|---|
| Wing LE / TE | 0 / 0.320 | ±0.575 | 0 | m | one-piece XPS core, S5010, chord 0.32, t/c 9.82 % (31 mm); no tape under the pod and fin roots (bond to bare foam) |
| Spar centreline | 0.080 | −0.50 … +0.50 | +0.0066 | m | CF 22 × 20 × 1 000 mm in a slot cut from the lower surface, on the camber line; six internal PETG plugs (Ø 19.8 × 36 at \|y\| 0.32, × 20 at \|y\| 0.242) |
| CG target (range) | 0.0526 (0.050–0.055) | 0 | +0.017 (−0.02 … +0.03) | m | 16.4 % chord; forward limit = elevon trim ≤ 12.5° at CLmax, aft = SM 5 % (D-24) |
| Pod | −0.115 … 0.095 | ±0.07 | 0.015 … 0.085 | m | shell 0.21 × 0.14 × 0.07; bay with the pack nominal centroid at x −0.001 (aft face 0.069, 0.073 with a 680 g pack); XPS crush block ≥ 24 mm ahead of the pack; FC right channel on gel pads, airspeed / RX / AS150U park (60 mm) left channel; hatch, GPS mast, carry handle tied to the spar |
| Motor tubes | 0.045 | ±0.32 | −0.172 … +0.172 | m | CF 22 × 20, 0.344 m, vertical through the core in the through-core block; ends inside the printed mounts |
| Through-core block | 0.045 / 0.080 | ±0.32 | 0 | m | printed PETG block 69 × 36 mm in a full-depth core pocket: vertical bore for the tube, spanwise bore for the spar, 35 mm apart |
| Half-fins (4) | 0.045 … 0.320 | ±0.32 | 0 … ±0.21 | m | two 4.8 mm foam-board layers, chord 0.275, LE on the tube, TE = wing TE; 10 × 1 mm CF edge strips (pinned); station collar on the tube at z ±0.1535 with a 10 × 3 mm CF brace to a spar anchor at y ±0.242 |
| Motors (axis at the plate) | 0.045 (plate face 0.0309) | ±0.32 | ±0.19 | m | stations `UR` `UL` `LR` `LL`; ASA mounts (slip collar 2.5 N·m, the tip-over fuse); shaft along −x, 7° tangential cant; ESC on an ASA pad on the outboard face at x 0.078–0.124, \|z\| 0.104–0.132 |
| Prop planes | −0.0082 | ±0.32 | ±0.19 | m | ⌀ 0.279 m; vertical pair gap 0.10 m, lateral 0.36 m; ≥ 39 mm from the plane to the collar front; disc edge 35 mm above the wing plane; LH adapters on the CW motors |
| Feet | 0.320 … 0.368 | ±0.32 | ±0.218 (pad contact) | m | printed shoe + piston + XPS constant-force cartridge (upper feet ×1.077, lower ×0.923), 48 mm, stroke ≥ 38 mm, neoprene pad, snap-fit swap ≤ 10 min; TE corner caps at y ±0.575 |
| Elevons (per side) | 0.2496 … 0.320 | 0.07–0.30 and 0.34–0.56 | 0 | m | 22 % chord, two panels on one servo ≥ 3.93 kgf·cm; full travel to VA 20.5 m/s, ≤ 1/3 at VD 27.2 (F4 schedule); link slot in the lower half-fin root x 0.2376–0.2616 |
| Pitot tip | −0.195 | −0.046 | 0.045 | m | plug-in 6 mm keyed boom in the left channel, 80 mm ahead of the pod nose; barbed tube couplers at the root |
| Box (external) | 1.25 × 0.55 × 0.54 | | | m | props off, pitot boom off, packs in the LiPo bag: envelope 1.15 × 0.483 × 0.438; cradles at y ±0.20 with ≥ 70 mm crush stroke, lid pillars over the spar |

## Subsystems: who owns every part

Folders under `subsystems/<key>/` (standard files: `SPEC.md`, `parts.csv`, `interfaces.json`, `params.json`,
`fusion/<key>.py`, `BUILD.md`). Part ids `<PREFIX>-NNN`. Each physical part has exactly one owner.
`parts.csv#mass_g` is **per unit** (line mass = qty × mass_g); a multi-instance part has one `interfaces.json`
node per instance, id `<part_id>-<UR|UL|LR|LL|L|R>` (station codes: `UR` = upper right), each with its own
`cg_xyz_m` (CR-A3-09; one suffix family per part number, D-26).

| Key | Prefix | Designer (CAD) | Analysis · structures | Owns these parts |
|---|---|---|---|---|
| `wing` | `WNG` | D1 | B2 · C2 | XPS core (one piece, with the block and anchor pockets and the pod recess), tape skin and doublers, CF spar, the six spar plugs, the four elevon panels (foam), spar slot cap, servo pockets, wingtip edge tape, TE corner caps' host edge, FAA label |
| `fins` | `FIN` | D3 | B3 (vertical surfaces) · C4 | 4 two-layer half-fins with edge strips and pins, 2 CF motor tubes, 2 spar plugs' partner blocks (through-core blocks), 4 ASA canted motor mounts, 4 station collars, 4 CF braces, 4 spar anchors, 4 ASA ESC pads, fin-root bonds |
| `pod` | `POD` | D2 | C3 | pod shell with the extended nose, printed tray with stops and guides, hatch, pack straps, crush block and spreader, GPS mast, pitot socket, carry handle and spar ties, vents |
| `landing` | `GER` | D5 | C5 | 4 crush feet (shoe, piston, cartridge, pad), wingtip TE corner caps |
| `propulsion` | `PRP` | E1 | E1 · B4 · E3 | 4 motors, 4 ESCs, 4 props, adapters, prop nuts, motor screws, spares |
| `power` | `PWR` | F1 | F1 · E2 · E3 | flight packs (AS150U), main disconnect, PDB, UBEC + 5 A fuse, ESC caps; the FC's power board belongs to `avionics` |
| `avionics` | `AVN` | F3 | F3 · F5 | CoreWing F405 Wing V2 (with power board), M100-5883 GPS/compass, RP3 receiver, MS4525DO airspeed + pitot boom, gel pads, microSD, antenna tubes |
| `harness` | `HRN` | F2 | F1 | every wire and connector between parts (incl. the ESC power and motor leads and any phase extension), routes, grooves, supports, strain relief, service loops |
| `mechanisms` | `MEC` | D6 | B2/B3 (hinge moments) · C6 | 2 servos, horns, pushrods, servo frames and covers, inter-panel links, hinge tape (the hinge edge is declared by `wing`) |
| `transport` | `TRN` | D7 | C1 (transport loads) | box, spar cradles, lid pillars, cam straps, handles, pouch with the prop spanner, field checklist — all `flight: false` |
| `flight-software` | `FSW` | F4 | — | `K09L.param`, output map, failsafes, SITL plan (no parts) |

Mass allocations (flying mass, g) are in `params/mass_budget.json`, written from `params.json#mass.allocation_g`
and read by `merge_check.py`, `check.py` and the viewer. A3 tracks every part against them in `MASS-CG.md`;
changes go through `params/CHANGE-LOG.md`.

| Subsystem | wing | fins | pod | landing | propulsion | power | avionics | harness | mechanisms | A1 reserve | **sum** | **gate** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Allocation (g) | 405 | 408 | 122 | 43 | 476 | 620 | 80 | 105 | 65 | 276 | **2 600** | **2 600** |

Six allocations now carry the designers' own numbers (D-38). The 276 g reserve must cover A3's growth by maturity
and the 100 g first-build overrun; it is released only through a change request. The pack (550 g carried,
listings 503–680 g) decides the gate: a 680 g pack takes 130 g of the reserve on its own.

## Joints: both sides of every interface

The owner declares the edge in its `interfaces.json` with the joint stack (fastened) or wire block (electrical);
the other side `acknowledges` it. Rules (CHANGE-LOG D-20): an owner holds one side of every edge it declares;
for an electrical edge `part_a` is the supply side; the harness owns every wire, the `power` subsystem owns the
boxes (pack, disconnect, PDB, UBEC). C6 sizes every fastened and bonded joint (`team/C6/joint_stacks.json`, M3
only); A4 merges and checks. Thread engagement: 1.0 d metal, 1.5 d insert, 2.0 d plastic, nyloc + 2 pitches (D-41).

| Joint | Side A (subsystem: part) | Side B | Owner | Type | Sized by |
|---|---|---|---|---|---|
| Spar in core | wing: spar | wing: core | wing | epoxy + microballoons in a 22.4 mm slot, foam cap re-bonded | C2 |
| Spar plugs | wing: PETG plug | wing: spar bore | wing | pushed in from the spar ends before bonding | C2 (ring MS −0.96 without, bearing +2.7 with) |
| Through-core block | fins: block | wing: spar, core | fins | printed PETG block, bonded; tube and spar bores 35 mm apart | C4 (961 N couple, MS +0.55), C6 (bond RF 5.7–6.3) |
| Tube in block | fins: tube | fins: block | fins | bonded | C4, C6 |
| Half-fin root to wing | fins: half-fin | wing: core (bare foam) | fins | bonded before skinning, tape lapped 15 mm up the board | C4, C6 (RF 1.12, thin) |
| Station collar and brace | fins: collar, brace | fins: tube; wing: spar anchor at y ±0.242 | fins | bonded collar 16 mm tall with a 40 mm two-face tail; brace ends ≥ 10 mm in printed slots; anchor pull-off | C4 (166 N design), C6 (CR-C6-01…03) |
| Edge strips | fins: CF strip | fins: board | fins | bonded + Ø 2 mm CF pins every 15 mm | C6 (RF 0.20 bare → 1.41 pinned) |
| Motor to mount | propulsion: motor | fins: ASA mount (7° cant) | fins | 4 × M3×8, 0.20 N·m, Loctite 243, drilled pattern | C6, E1 |
| Mount to tube | fins: motor mount | fins: tube | fins | slip collar, pinch bolts, 2.5 N·m slip: the mount fails before the tube (D-23) | C4 (≥ 900 N·m/rad), C6 (3.2 N·m prop-nut case RF 3.3) |
| Prop to motor | propulsion: prop + adapter | propulsion: motor | propulsion | M6 nut, LH on the CW motors, 1.5 N·m with the pouch spanner | E1 |
| ESC to fin | propulsion: ESC | fins: ASA ESC pad | fins | one 10 mm hook-and-loop strap, FET side out, in the slipstream | E3 (61.6 °C) |
| Foot to fin tip | landing: shoe | fins: half-fin tip (square 40 mm, both layers) | landing | bonded shoe; piston snap-fit, swap ≤ 10 min | C5, C6 (RF 1.35) |
| Pod to wing | pod: shell | wing: core (bare, sanded foam) | pod | bonded 10 014 mm² + 2 nylon ties under the spar | C3 (R 0.65 design, 0.76 crash) |
| Pack in pod | power: pack | pod: tray, stops, straps, crush block | pod | 3 mm printed stops, 1.5 mm guides, 50 mm strap overlap | C3, C5 (85 N crash; ≤ 100 g) |
| Avionics mounts | avionics: FC, GPS, RX, airspeed | pod: tray, mast | avionics | FC on gel pads; airspeed on foam tape; mast pad 45° | F3, C6 |
| Pitot boom | avionics: pitot boom | pod: nose socket with flange | avionics | plug-in, keyed, barbed couplers, removed for transport | B4 (placement), F3, C6 |
| Elevon hinge | wing: core TE | wing: elevon panel | wing (D6 designs) | tape hinge, bevelled lower edge | D6 |
| Servo in wing | mechanisms: servo frame | wing: servo pocket | mechanisms | bonded frame ≥ 720 mm², screws into bosses | D6, C6 |
| Horn and pushrod | mechanisms: horn, pushrod | wing: elevon panel | mechanisms | through-panel horn with backplate, clevis + keeper | D6, C6 |
| Inter-panel link | mechanisms: link | wing: inboard and outboard panels | mechanisms | crosses the lower half-fin root through the slot | D6, D3 |
| Motor leads | harness: wire (supply: ESC) | propulsion: motor | harness | 3 × 3.5 mm bullet; extension ≤ 100 mm if the factory lead is short | F1 (gauge), E1 |
| ESC power leads | harness: wire (supply: PDB) | propulsion: ESC | harness | 16 AWG, 0.5 m, two taped surface grooves 5 mm apart, 680 µF cap at the ESC | F1 |
| Pack ↔ disconnect ↔ PDB | harness: wire (supply: pack) | power: AS150U, PDB | harness | AS150U anti-spark pair; 8 AWG ≤ 0.15 m twisted | F1 |
| UBEC ↔ FC, servos | harness: wire (supply: UBEC) | avionics: FC; mechanisms: servos | harness | 5 A fuse → UBEC 6 V; Vx not paralleled | F1, F3 |
| Signals | harness: wire (supply: FC) | mechanisms: servos; avionics: GPS, RX, airspeed | harness | outputs 1–4 DShot300 bidirectional (LR M1, UL M2, LL M3, UR M4), 5–6 PWM; SERIAL5 GPS + I²C, SERIAL6 RX (CRSF) | F4, F3 |
| Cradles and pillars | transport: cradle, pillar | wing: spar line at y ±0.20 | transport | contact, `flight: false`; patches on the wing kept clear | C1, D7 |

Open joint questions (`team/C6/CHANGE-REQUESTS.md`): the collar torsion (C1 5.29 vs C4 9.3 N·m) and the strip
anchorage are the thinnest bonds; every allowable is a guess until the C6 coupons run with the first prints.

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
1 m in 5 m/s, then a transition); tune it as a plain flying wing before any transition; the stable ArduPilot Plane
tailsitter build for the CoreWing F405 Wing V2 is confirmed (F3, 2026-11-09); measure RFS wind against RCMC1; order
electronics, two packs, the US-stock carbon tube and the props early (~20 Nov); bend-test the tube by 10 Dec (C4,
H1). Weigh the pack and the tube on arrival (`team/A1/HANDOFF.md`). Reverse to K01-lean on the conditions listed
there.
