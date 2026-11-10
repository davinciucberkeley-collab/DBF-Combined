# Redesign v1 — K09-L quad tailsitter

Status: `PROPOSED` design frame, revision **A1-R4** (A1, 2026-11-09, after the integration round: every subsystem's
parts list and interface declaration is in, the CG is fixed by moving the pack bay, allocations follow the delivered
parts). Configuration
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
pod on the upper surface behind a crush block, its nose 130 mm ahead of the wing, at a station marked per weighed
pack. The whole aircraft travels in one piece in one box; field set-up is four props (one spanner), the pitot boom
and a pack: five minutes, one person. ArduPilot Plane, tailsitter mode, CoreWing F405 Wing V2 with its power board
split onto the power frame. It is the cheapest and fastest-built concept in the study and the riskiest to fly: any
motor failure is a crash, and the flight card is limited to 5 m/s wind, mornings only.

## Key numbers

All at the 2.6 kg gate. Re-check: `python -I redesign/team/A1/frame_claims.py` then
`python -I redesign/proofs/build_graph.py`.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, area, AR | 1.15 × 0.32, 0.368, 3.59 | m, m², — | `CL-A1-WING-AREA` | `CHECKED` |
| Allocations / sized / hard gate | 2 355 / 2 600 / 2 600 | g | `CL-A1-MASS-SIZED` | `CHECKED` (+0 %: the pack weigh-in decides) |
| A3 roll-up, basic / predicted by maturity (550 g pack) | 2 330 / 2 449; 680 g pack 2 579 | g | `CL-A3-MASS-BASIC`, `-PREDICTED`, `CL-A3-GATE-MARGIN-680` | `MODELLED` (A3-R5; 680 g case `FAIL` on the overrun) |
| Hover T/W, fresh pack with the 100 A limiter / worst pack state | 2.49 / 2.12 | — | `CL-A1-HOVER-TW-GATE`, `-SAG` | `UNVERIFIED` (thrust stand) |
| Stall, trimmed CLmax 0.80 (target CG / forward limit) | 11.90 / 11.93 | m/s | `CL-B3-VS-TRIM`, `CL-A1-STALL-GATE` | `UNVERIFIED` |
| Transition ≥ 1.3 Vs at the forward CG vs cruise | 15.51 ≤ 16 | m/s | `CL-B3-VT-TRIM` | `UNVERIFIED` (+3 %) |
| Cruise power / current, L/D (E1 on B1 rev 3; B1 227.8 / 300.6 pessimistic) | 240 / 16.2, 6.2 | W, A, — | `CL-E1-CRUISE-P-55`, `CL-B1-CRUISE-P`, `-P-PESS` | `UNVERIFIED` |
| Cruise after 2 min hover, mission base / pessimistic | 12.7 / 6.8 (B1 level cruise 16.3 / 12.0) | min | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Level speed with the fixed-wing `THR_MAX` 70 % cap vs VH; VD | 21.3 ≤ 21.8; 27.2 | m/s | `CL-F4-VLEVEL-VH`, `CL-C1-VD` | `UNVERIFIED` (first full-throttle level log, D-50) |
| Hover power / pack current | 400 / 27 | W / A | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| Hover lean at 5 / 8 m/s; landing wind limit | 16 / 36; 5.8 | ° ; m/s | `CL-B1-LEAN-*`, `CL-B1-WIND-HOVER-MAX` | `UNVERIFIED` |
| CG range (target), chord fraction | 0.050–0.0549 (0.0522), 15.6–17.2 % | m | `CL-B3-CG-FWD`, `-AFT`, `CL-A1-CG-RANGE-*` | `UNVERIFIED` (B3 R3) |
| Take-off CG x, A3-R5 before / after the bay move (550 g pack, basic → predicted) | 0.0577 `FAIL` → 0.0525 → 0.0540 | m | `CL-A3-CG-X-RANGE`, `CL-A1-PACK-STATION` | `UNVERIFIED` (D-47; D2 re-lays, A3 re-runs) |
| Cruise Cn_β, aft CG, 1.3 Vs (0.21 m fins) | 0.0373 | /rad | `CL-B3-CNB` | `UNVERIFIED` (B3 R3) |
| Hover yaw authority / 5 m/s disturbance at 7° (no fin credit / with B4's fin factor) | 1.30 / 2.23–3.15 | — | `CL-B3-HOVER-YAW-RATIO`, `CL-B4-YAW` | `UNVERIFIED` (cant sense corrected, D-52; T-B4-YAW) |
| Tip-over toward the pod, worst flying CG / corner bound | 32.4 / 30.6 | ° | `CL-C5-TIPOVER-WORST`, `CL-A1-TIPOVER` | `UNVERIFIED` (+2 %; C5 re-checks with the CG 5 mm higher) |
| Fin station first mode vs 80–330 Hz, two layers | separation 0.41 (worst 0.33) | — | `CL-C4-D3-SEP` | `UNVERIFIED` (tap test) |
| Wing torsion modes (antisym / sym) | 11.7–14.9 / 21–27 | Hz | `CL-C2-F-TORSION-*` | `UNVERIFIED` (notch + tap test, D-45) |
| Minimum prop clearance (disc edge to wing plane; canted tip to tube face) | 35; 27 | mm | `CL-A1-PROP-CLEAR`, `CL-B4-*` | `UNVERIFIED` |
| Elevon area fraction | 17.2 | % | `CL-A1-ELEVON-FRAC` | `CHECKED` |
| Box, external / fit slack along the chord / box mass | 1.25 × 0.55 × 0.54 / 2 mm / 3.57 kg | m, mm, kg | `CL-A1-BOX-FIT`, `CL-D7-BOX-H-REQ` | `PROPOSED` (two cars first; D7 re-fits the nose pad) |
| Spend pessimistic / reserve / one crash | $1 687 / $313 / $309 | USD | `CL-I1-RESERVE-PESS`, `CL-A1-RESERVE` | `UNVERIFIED` (+1 %; three gated lines) |
| Field ambient ceiling (mission) | 43 | °C | `CL-E3-CEIL-MISSION` | `UNVERIFIED` |
| Build to first hover | ≤ 90 (plan 70–85) | h | `params.json#requirements` | `PROPOSED` |

## General arrangement

![K09-L general arrangement, three views to scale](team/A1/ga-3view.svg)

`FIG A1-01 — General arrangement at revision A1-R4, 1 m = 500 px, drawn from params.json by team/A1/draw_ga.py.`

**Frame** (every CAD module, `interfaces.json`, the viewer and every analysis): metres, right-handed.
Origin at the wing root leading edge on the chord line. **x aft** (0 at the LE, 0.32 at the TE), **y to the right
wing tip**, **z up** in cruise attitude. In hover the nose points up and +x points at the ground. Symmetry plane
XZ. Fusion receives cm through `fusionkit`.

| Station | x | y | z | Unit | What is there |
|---|---|---|---|---|---|
| Wing LE / TE | 0 / 0.320 | ±0.575 | 0 | m | one-piece XPS core, S5010, chord 0.32, t/c 9.82 % (31 mm); no tape under the pod and fin roots (bond to bare foam) |
| Spar centreline | 0.080 | −0.50 … +0.50 | +0.0066 | m | CF 22 × 20 × 1 000 mm in a slot cut from the lower surface, on the camber line; four internal PETG plugs (Ø 19.8 × 36 at \|y\| 0.32 under the blocks, × 20 at \|y\| 0.242 under the brace anchors; D1 CR-D1-03) |
| CG target (range) | 0.0522 (0.050–0.0549) | 0 | +0.018 (−0.02 … +0.03) | m | 16.3 % chord; forward limit = elevon trim ≤ 12.5° at CLmax, aft = SM 5 % (B3 R3, D-47) |
| Pod | −0.130 … 0.095 | ±0.07 | 0.015 … 0.085 | m | shell 0.225 × 0.14 × 0.07; bay 21 mm forward of R3 (forward stop −0.1212, aft stop 0.056) with the pack nominal centroid at x −0.022 (680 g at −0.014 on an 8 mm spacer, 503 g at −0.0245; D-47); XPS crush block ≥ 24.3 mm and a 1.5 mm spreader ahead of the pack, 8.8 mm nose block; FC right channel on gel cubes with a strap, airspeed / RX left channel; power frame `PWR-006` with the AS150U cradle, PDB plate and the CoreWing power board at x −0.038 … 0.072; hatch, GPS mast, carry handle tied to the spar; spar saddle `POD-007` at x 0.080 |
| Motor tubes | 0.045 | ±0.32 | −0.172 … +0.172 | m | CF 22 × 20, 0.344 m, vertical through the core in the through-core block; ends inside the printed mounts |
| Through-core block | 0.045 / 0.080 | ±0.32 | 0 | m | printed PETG block 69 × 36 mm in a full-depth core pocket: vertical bore for the tube, spanwise bore for the spar, 35 mm apart |
| Half-fins (4) | 0.045 … 0.320 | ±0.32 | 0 … ±0.21 | m | two 4.8 mm foam-board layers, chord 0.275, LE on the tube, TE = wing TE; 10 × 1 mm CF edge strips (pinned); station collar on the tube at z ±0.1535 with a 10 × 3 mm CF brace to a spar anchor at y ±0.242 |
| Motors (axis at the plate) | 0.045 (plate face 0.0309, tube front face 0.034) | ±0.32 | ±0.19 | m | stations `UR` `UL` `LR` `LL`; ASA mounts (slip collar 2.5 N·m, the tip-over fuse), plate 29 × 30 × 4.5 mm canted 7° with the prop end leaning toward the wing and outboard (`cant_sense_UR` −1, D-52); shaft along −x; ESC on an ASA pad (31 mm high) on the outboard face at x 0.078–0.124, \|z\| 0.104–0.132, 680 µF cap 3 mm aft of it |
| Prop planes | −0.0077 | ±0.32 | ±0.19 | m | ⌀ 0.279 m; vertical pair gap 0.10 m, lateral 0.36 m; ≥ 39.1 mm from the plane to the collar front (stack 37.3 mm, D-51); disc edge 35 mm above the wing plane; canted tip 27 mm ahead of the tube face; LH adapters on the CW motors, adapter screws 2.0 mm engagement by deviation (D-58) |
| Feet | 0.320 … 0.368 | ±0.32 | ±0.218 (pad contact) | m | printed shoe on a 9.5 mm step of a 45.4 mm square fin tip (strips end at x 0.2746), piston + pre-crushed XPS constant-force cartridge (upper 39.6 N, lower 35.4 N; 17.3 × 13.3 mm section), 48 mm foot, 38 mm flange-to-sleeve gap (35 mm usable), neoprene pad, snap-fit swap ≤ 10 min; 42.5 g; TE corner caps at y ±0.575 (span 1.152 m) |
| Elevons (per side) | 0.2496 … 0.320 | 0.07–0.30 and 0.34–0.56 | 0 | m | 22 % chord, two panels on one Savox SH-0255MG+ (≥ 3.93 kgf·cm through the four-bar); 5 × 4 mm CF torque tube in each panel, 3/32 in inter-panel rod through the notch in the lower half-fin root x 0.2376–0.2616; full travel to VA 20.5 m/s, the VD half of the schedule held by envelope (`THR_MAX` 70 %, D-50) |
| Pitot tip | −0.210 | −0.046 | 0.045 | m | plug-in 6 mm keyed boom in the left channel, 80 mm ahead of the pod nose (part unchanged, D-47); barbed tube couplers at the root |
| Box (external) | 1.25 × 0.55 × 0.54 | | | m | props off, pitot boom off, packs in the LiPo bag: envelope 1.152 × 0.498 × 0.438 (chord slack 2 mm); cradles at y ±0.20 on 120 mm crush columns bearing on the tape skin, lid pillars over the spar; floor drop 0.3 m, "keep upright" (D-53) |

## Subsystems: who owns every part

Folders under `subsystems/<key>/` (standard files: `SPEC.md`, `parts.csv`, `interfaces.json`, `params.json`,
`fusion/<key>.py`, `BUILD.md`). Part ids `<PREFIX>-NNN`. Each physical part has exactly one owner.
`parts.csv#mass_g` is **per unit** (line mass = qty × mass_g); a multi-instance part has one `interfaces.json`
node per instance, id `<part_id>-<UR|UL|LR|LL|L|R|C>` (station codes: `UR` = upper right; side family `L R C`),
each with its own `cg_xyz_m` (CR-A3-09; one suffix family per part number, D-26). The same part twice at one
station takes a face letter `I`/`O` (e.g. `FIN-011-URO`, CR-A4-31). Parts not carried in flight (spares, tools,
the box, the transmitter) are nodes with `"flight": false`; parts held only by tape, ties or a label are
`"carried": true` and need no load-bearing joint.

| Key | Prefix | Designer (CAD) | Analysis · structures | Owns these parts |
|---|---|---|---|---|
| `wing` | `WNG` | D1 | B2 · C2 | XPS core (one piece, with the block and anchor pockets, the pod recess, the wire grooves and the lower servo pockets), tape skin and doublers, CF spar, the four spar plugs, the four elevon panels (foam, with torque-tube grooves and horn slots), spar slot cap, wingtip edge tape, TE corner caps' host edge, FAA label |
| `fins` | `FIN` | D3 | B3 (vertical surfaces) · C4 | 4 two-layer half-fins with edge strips and pins, 2 CF motor tubes, 2 spar plugs' partner blocks (through-core blocks), 4 ASA canted motor mounts, 4 station collars, 4 CF braces, 4 spar anchors, 4 ASA ESC pads, fin-root bonds |
| `pod` | `POD` | D2 | C3 | pod shell with the extended nose, printed tray with stops and guides, hatch, pack straps, crush block and spreader, GPS mast, pitot socket, carry handle and spar ties, vents |
| `landing` | `GER` | D5 | C5 | 4 crush feet (shoe, piston, cartridge, pad), wingtip TE corner caps |
| `propulsion` | `PRP` | E1 | E1 · B4 · E3 | 4 motors, 4 ESCs, 4 props, adapters, prop nuts, motor screws, spares |
| `power` | `PWR` | F1 | F1 · E2 · E3 | flight packs (AS150U), main disconnect, the CoreWing power board `PWR-003` (split from the FC stack, D-48), bus board, PDB plate and power frame `PWR-006`, UBEC + 5 A fuse `PWR-007`, four ESC caps `PWR-008-<st>` |
| `avionics` | `AVN` | F3 | F3 · F5 | CoreWing F405 Wing V2 flight controller (12 g, without its power board), M100-5883 GPS/compass, RP3 receiver with two 150 mm T-antennas, MS4525DO airspeed + pitot boom, gel cubes, microSD, antenna tubes |
| `harness` | `HRN` | F2 | F1 | every wire and connector between parts (incl. the ESC power and motor leads and any phase extension), routes, grooves, supports, strain relief, service loops |
| `mechanisms` | `MEC` | D6 | B2/B3 (hinge moments) · C6 | 2 servos, horns, pushrods, servo frames and covers, inter-panel links, hinge tape (the hinge edge is declared by `wing`) |
| `transport` | `TRN` | D7 | C1 (transport loads) | box, spar cradles, lid pillars, cam straps, handles, pouch with the prop spanner, field checklist — all `flight: false` |
| `flight-software` | `FSW` | F4 | — | `K09L.param`, output map, failsafes, SITL plan (no parts) |
| `ground` | `GND` | F5 | F5 | transmitter `GND-001` and ground station, `flight: false` (CR-A4-31) |

Mass allocations (flying mass, g) are in `params/mass_budget.json`, written from `params.json#mass.allocation_g`
and read by `merge_check.py`, `check.py` and the viewer. A3 tracks every part against them in `MASS-CG.md`;
changes go through `params/CHANGE-LOG.md`.

| Subsystem | wing | fins | pod | landing | propulsion | power | avionics | harness | mechanisms | A1 reserve | **sum** | **gate** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Allocation (g) | 405 | 418 | 131 | 43 | 462 | 648 | 45 | 123 | 80 | 245 | **2 600** | **2 600** |

Every allocation now carries its designer's delivered `parts.csv` (D-48), with three reductions A1 directed inside
them (3/32 in inter-panel rod, ESCs stripped of their factory power leads, a 12 mm collar paying for the 15 mm root
fillets). The 245 g reserve covers A3's growth by maturity (119 g at A3-R5) and the 100 g first-build overrun with
26 g free; it is released only through a change request. The pack (550 g carried, listings 503–680 g; I1's fetched
listing says 680 g) decides the gate: above 601 g the overrun is no longer covered (D-58, E2 names the SKU).

## Joints: both sides of every interface

The owner declares the edge in its `interfaces.json` with the joint stack (fastened) or wire block (electrical);
the other side `acknowledges` it. Rules (CHANGE-LOG D-20): an owner holds one side of every edge it declares;
for an electrical edge `part_a` is the supply side; the harness owns every wire, the `power` subsystem owns the
boxes (pack, disconnect, PDB, UBEC). C6 sizes every fastened and bonded joint (`team/C6/joint_stacks.json`, M3
only); A4 merges and checks. Thread engagement: 1.0 d metal, 1.5 d insert, 2.0 d plastic, nyloc + 2 pitches (D-41).

| Joint | Side A (subsystem: part) | Side B | Owner | Type | Sized by |
|---|---|---|---|---|---|
| Spar in core | wing: spar | wing: core | wing | epoxy + microballoons in a 22.4 mm slot, foam cap re-bonded | C2 |
| Spar plugs | wing: PETG plug (four: 36 mm under the blocks, 20 mm under the anchors) | wing: spar bore | wing | pushed in from the spar ends before bonding | C2 (ring MS −0.96 without, bearing +2.7 with) |
| Through-core block | fins: block | wing: spar, core | fins | printed PETG block, bonded; tube and spar bores 35 mm apart | C4 (961 N couple, MS +0.55), C6 (bond RF 5.7–6.3) |
| Tube in block | fins: tube | fins: block | fins | bonded | C4, C6 |
| Half-fin root to wing | fins: half-fin | wing: core (bare foam) | fins | bonded before skinning, tape lapped 15 mm up the board | C4, C6 (RF 1.12, thin) |
| Station collar and brace | fins: collar, brace | fins: tube; wing: spar anchor at y ±0.242 | fins | bonded collar 16 mm tall with a 40 mm two-face tail; brace ends ≥ 10 mm in printed slots; anchor pull-off | C4 (166 N design), C6 (CR-C6-01…03) |
| Edge strips | fins: CF strip | fins: board | fins | bonded + Ø 2 mm CF pins every 15 mm | C6 (RF 0.20 bare → 1.41 pinned) |
| Motor to mount | propulsion: motor | fins: ASA mount (7° cant, sense −1) | fins | 4 × M3×8 into the 4.5 mm canted plate, 3.5 mm engagement, 0.20 N·m, Loctite 243, drilled pattern | C6, E1 |
| Mount to tube | fins: motor mount | fins: tube | fins | slip collar, pinch bolts, 2.5 N·m slip: the mount fails before the tube (D-23) | C4 (≥ 1 000 N·m/rad pass level), C6 (3.2 N·m prop-nut case RF 3.3) |
| Prop to motor | propulsion: prop + adapter | propulsion: motor | propulsion | adapter screws M3×4, 2.0 mm engagement by deviation (D-58), 0.5 N·m + 243; M6 nut, LH on the CW motors, 1.5 N·m with the pouch spanner | E1, C6 |
| ESC to fin | propulsion: ESC | fins: ASA ESC pad (31 mm high) | fins | one 10 mm hook-and-loop strap through the slots beside the ESC, FET side out, in the slipstream; cap foam-taped 3 mm aft | E3 (61.6 °C), F1 |
| Foot to fin tip | landing: shoe | fins: half-fin tip step (45.4 mm square, step at \|z\| 0.2005, bare laminate) | landing | bonded shoe 1 350 mm² (RF 1.54); piston snap-fit, swap ≤ 10 min | C5, C6 |
| Pod to wing | pod: shell | wing: core (bare, sanded foam) | pod | bonded 10 014 mm² + 2 nylon ties under the spar | C3 (R 0.65 design, 0.76 crash) |
| Pack in pod | power: pack | pod: tray, stops, straps, crush block | pod | 3 mm printed stops (forward stop derived from the nose, D-47), 1.5 mm guides, 50 mm strap overlap, 6 mm corner fillets under the straps | C3, C5 (85 N crash; ≤ 100 g) |
| Power frame | power: `PWR-006` (AS150U cradle, PDB plate, power board) | pod: tray inserts | power | 4 × M3×18 nylon pan head into M3 × 5.7 brass inserts, 5.5 mm engagement, 0.2 N·m | F1, C6 |
| Avionics mounts | avionics: FC, GPS, RX, airspeed | pod: tray, mast | avionics | FC on four 5 mm gel cubes with a 10 mm strap; airspeed on foam tape; mast pad 45°, PA66 cross-bolt | F3, C6 |
| Pitot boom | avionics: pitot boom | pod: nose socket with flange | avionics | plug-in, keyed, barbed couplers, removed for transport | B4 (placement), F3, C6 |
| Elevon hinge | wing: core TE | wing: elevon panel | wing (D6 designs) | tape hinge, bevelled lower edge | D6 |
| Servo in wing | mechanisms: servo frame | wing: lower-skin servo pocket | mechanisms | bonded frame ≥ 720 mm² (VD 27.2, D-50); servo ears captured in slots, cover on M2 × 6 screws (exception to M3-only, D-58) | D6, C6 |
| Horn and pushrod | mechanisms: horn, pushrod | wing: elevon panel | mechanisms | through-panel horn bonded 1 385 mm² onto the 5 × 4 mm torque tube, 2-56 clevis + keeper | D6, C6 |
| Inter-panel link | mechanisms: 3/32 in rod | mechanisms: horns on both panels | mechanisms | crosses the lower half-fin root through the 24 × 12 mm notch; root fillets stopped there | D6, D3 |
| Motor leads | harness: wire (supply: ESC) | propulsion: motor | harness | soldered staggered splices (no bullets); extension ≤ 100 mm if the factory lead is short (reach 0.121 m) | F1 (gauge), E1, F2 |
| ESC power leads | harness: wire (supply: bus bars) | propulsion: ESC | harness | 16 AWG soldered to the ESC pads (factory leads removed), routed 0.51–0.65 m in two taped surface grooves ahead of the spar, 8 mm hole through each half-fin 22 mm off the skin; 680 µF cap at the ESC (`E-HRN-34…37`) | F1, F2 |
| Pack ↔ disconnect ↔ power board ↔ bus | harness: wire (supply: pack) | power: AS150U in the frame cradle, `PWR-003`, bus board | harness | AS150U anti-spark pair; 10 AWG main path (`E-HRN-11/12`) | F1 |
| Bus ↔ fuse ↔ UBEC ↔ FC, servos | harness: wire (supply: bus) | power: `PWR-007` fuse, UBEC; avionics: FC; mechanisms: servos | harness | 5 A fuse → UBEC 6 V (`E-HRN-21`, `-33`); servo stall 1.4 A each; Vx not paralleled | F1, F3, D6 |
| Signals | harness: wire (supply: FC) | mechanisms: servos; avionics: GPS, RX, airspeed | harness | outputs 1–4 DShot300 bidirectional (LR M1, UL M2, LL M3, UR M4), 5–6 PWM; SERIAL5 GPS + I²C, SERIAL6 RX (CRSF) | F4, F3 |
| Cradles and pillars | transport: cradle, pillar | wing: spar line at y ±0.20 (saddle on the tape skin, `also_contacts`) | transport | contact, `flight: false`; patches on the wing kept clear | C1, D7 |

Open joint questions (`team/C6/CHANGE-REQUESTS.md`): the collar torsion (C1 section total 6.60 N·m vs C4's FE 4.61;
C6 sizes to the larger plus the brace shear) and the strip anchorage (paper bare MS −0.77, pinned +) are the thinnest
bonds; every allowable is a guess until the C6 coupons run with the first prints. Two deviations from the thread rule
are granted (D-58): the prop-adapter screws (2.0 mm) and the mechanisms' bought 2-56 / M2 hardware.

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
H1). Weigh the pack and the tube on arrival (`team/A1/HANDOFF.md`). Before the first hover: check the cant sense on
every mount with an inclinometer and a hanging yaw test (D-52), and the pack station mark for the weighed pack
(D-47). Reverse to K01-lean on the conditions listed there.

## Integration state (A1-R4)

| Check | Result | Owner of the next step |
|---|---|---|
| `interfaces/merge_check.py` (159 parts, 214 edges) | FAIL: 1 error (CG 0.0577, fixed by D-47 once D2 re-lays and A3 re-runs), 36 warnings (21 harness wires parked, 5 allocations) | D2, A3, F2 |
| `fusion/check.py` (10 modules build) | FAIL: 5 errors (the CG; `E-GER-21/22` registered but undeclared; `GER-007-L/R` floating) | D5 |
| `team/A3/mass_rollup.py --check` | PASS; 2 330 / 2 449 g; CG 0.0577 m before the bay move | A3 |
| `team/A4/interface_plan.py --compare` | 251 planned, 238 declared (24 parked), 13 missing, 10 deviations | F2, D3, F5 |
| `proofs/build_graph.py` | FAILED on drift only: the owners re-run on the R4 keys (A3, A5, B1, B3, B4, C1, C3 (`KeyError`), C5 (`IndexError`), E1, E2, E3, F1, F4, H1, J1); A1's 19 claims re-compute | each owner |
