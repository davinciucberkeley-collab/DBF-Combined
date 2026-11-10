# Redesign v1 — K09-L quad tailsitter

Status: `PROPOSED` design frame, revision **A1-R5** (A1, 2026-11-10, after the simulation round: every analysis role
re-ran on the settled CAD with CFD, VLM, FEA and a 6-DOF touchdown model; four requirements failed as designed and are
fixed by D-61 … D-73: the CG range now carries the CG height, the pack bay moves 10 mm forward, the prop plane 5 mm
forward, the feet are sized to a 1.2 m/s diagonal landing, the pod stops and the wing's block pockets are reinforced).
Configuration
decided in [`CONFIGURATION.md`](CONFIGURATION.md); numbers live in [`params/params.json`](params/params.json) and
every change to them in [`params/CHANGE-LOG.md`](params/CHANGE-LOG.md); roles in [`TEAM.md`](TEAM.md); rules in
[`BRIEF.md`](BRIEF.md). Reversible until the mid-December order on the conditions in `CONFIGURATION.md`.

## The aircraft

A 1.15 × 0.32 m flat flying wing (hot-wired XPS core, packing-tape skin, one 22 × 20 mm carbon spar at 25 % chord,
Selig S5010 reflexed section) with two vertical foam-board fins at ±0.32 m span. At each fin a vertical 22 mm carbon
tube passes **through the wing core at x = 0.045 m**, 35 mm ahead of the spar, in a printed through-core block (its
vertical edges rounded R 3 mm); a printed mount at each tube end carries a SunnySky X3108S motor with an APC
11 × 5.5MR prop, its plane 7.5 mm further ahead of the tube face than the R4 stack so the canted blade clears the tube
by 26 mm: four fixed motors in an X, two above and two below the wing, each canted 7° for hover yaw. Each fin is two half-fins (two foam-board
layers, 0.21 m high, from the tube back to the wing trailing edge) braced by a carbon strip to an anchor on the spar.
It stands on four crushable feet at the fin trailing-edge tips, takes off as a quadcopter, pitches 90° nose-down
onto the same four motors for cruise at 16 m/s, and pitches back up to land. Two elevon pairs give roll and pitch in
cruise; an airspeed sensor on the pod nose schedules the gains in fixed-wing flight. One 4S 6500 mAh pack (Ovonic 120C
hard case, 551 g) sits in a pod on the upper surface behind a crush block, its nose 140 mm ahead of the wing, at a
station marked per weighed pack; the pod group puts the take-off CG 18.5 mm above the chord plane, which is now in
every stability number. The whole aircraft travels in one piece in one box; field set-up is four props (one spanner), the pitot boom
and a pack: five minutes, one person. ArduPilot Plane, tailsitter mode, CoreWing F405 Wing V2 with its power board
split onto the power frame. It is the cheapest and fastest-built concept in the study and the riskiest to fly: any
motor failure is a crash, and the flight card is limited to 5 m/s wind, mornings only.

## Key numbers

All at the 2.6 kg gate. Re-check: `python -I redesign/team/A1/frame_claims.py` then
`python -I redesign/proofs/build_graph.py`.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, area, AR | 1.15 × 0.32, 0.368, 3.59 | m, m², — | `CL-A1-WING-AREA` | `CHECKED` |
| Allocations / sized / hard gate | 2 386 / 2 600 / 2 600 | g | `CL-A1-MASS-SIZED` | `CHECKED` (+0 %; reserve 214 g = growth 114 + overrun 100, 0 g free) |
| A3 roll-up, basic / predicted by maturity (550 g pack) | 2 322 / 2 436 (A3-R6a; ≈ 2 458 after the R5 additions) | g | `CL-A3-MASS-BASIC`, `-PREDICTED` | `MODELLED` (A3 re-runs on D2-R6, D3-R5, D5-R5) |
| Pack acceptance line (heaviest pack the 100 g overrun still covers) vs the SKU maximum | 592.6 ≥ 556 | g | `CL-A1-PACK-ACCEPT` | `UNVERIFIED` (+7 %; T-E2-WEIGH) |
| Hover T/W, fresh pack with the 100 A limiter / worst pack state | 2.49 / 2.12 | — | `CL-A1-HOVER-TW-GATE`, `-SAG` | `UNVERIFIED` (thrust stand) |
| Stall at the gate, trimmed CLmax 0.80 (frame / B2 forward CG / B1 as designed) | 11.90 / 11.99 / 11.99 | m/s | `CL-A1-STALL-GATE`, `CL-B2R3-VS-GATE-FWD`, `CL-B1V-VS-GATE` | `UNVERIFIED` (+0.1 %: `T-B2-STALL` is the gate, D-71) |
| Transition ≥ 1.3 Vs at the forward CG vs cruise | 15.52 ≤ 16 | m/s | `CL-B3-V-VT` | `UNVERIFIED` (+3 %; vs `ARSPD_FBW_MIN` 15.6 +0.1 %) |
| Cruise power / current, L/D (E1; B1 as designed 238.9 at the gate, 312.4 pessimistic, CD0 0.0579) | 240 / 16.2, 6.2 | W, A, — | `CL-E1-CRUISE-P-55`, `CL-B1V-CRUISE-P`, `-P-PESS` | `UNVERIFIED` (E1 re-runs on `CL-B1V-CD0`) |
| Cruise after 2 min hover, mission base / pessimistic (240 W case) | 12.0 / 6.4 (B1 level cruise 16.2 / 11.9) | min | `CL-E2-CRUISE-MIN-BASE-240`, `-PESS-240` | `UNVERIFIED` (E2 re-runs on 312 W) |
| Level speed with the fixed-wing `THR_MAX` 70 % cap vs VH; VD | 21.0 ≤ 21.8; 27.2 | m/s | `CL-B1V-VH-FW`, `CL-C1-VD` | `UNVERIFIED` (first full-throttle level log, D-50) |
| Hover power / pack current | 400 / 27 | W / A | `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| Hover lean at 5 / 8 m/s; landing wind limit | 16 / 36; 5.8 | ° ; m/s | `CL-B1-LEAN-*`, `CL-B1-WIND-HOVER-MAX` | `UNVERIFIED` |
| CG range (target), chord fraction; CG height | 0.0466–0.0514 (0.0490), 14.6–16.1 %; z +0.0185 | m | `CL-B3-V-CG-FWD`, `-CG-AFT-ENV`, `CL-A1-CG-RANGE-*` | `UNVERIFIED` (B3 V1, D-62: 4.8 mm wide) |
| Take-off CG x: A3-R6a in the D-47 bay / D-62 frame estimate (550 g at −0.034, basic → predicted) / worst pack | 0.0522 (0.8 mm aft of the new limit) / 0.0485 → 0.0498 / 546 g 0.0495 predicted (aft +1.5 mm), 590 g 0.0486 basic (fwd +1.5 mm) | m | `CL-A3-CG-X-RANGE`, `CL-A1-PACK-CG-FWD` / `-AFT` | `MODELLED` (D-61, D-62; D2 re-lays, A3 re-runs) |
| Cruise Cn_β, aft CG, 1.3 Vs (CAD fins: laminate / tube as LE) | 0.0615 / 0.0479 | /rad | `CL-B3-V-CNB`, `-CNB-TUBE` | `UNVERIFIED` (B3 V1) |
| Spiral t2 (limit 4 s; A2 decides D-66) / Dutch roll ζ / short period ζ | 3.51 `FAIL` / 0.28 / 0.48 | s, —, — | `CL-B3-V-LAT-T2`, `-DR-ZETA`, `-SP-ZETA` | `UNVERIFIED` |
| Hover yaw authority / 5 m/s disturbance at 7° (no fin credit / with B4's fin factor) | 1.30 / 2.23–3.15 | — | `CL-B3-HOVER-YAW-RATIO`, `CL-B4-YAW` | `UNVERIFIED` (cant sense corrected, D-52; T-B4-YAW) |
| Tip-over toward the pod, worst flying CG / corner bound (fwd limit 0.0466, z 0.025) | 32.0 / 31.0 | ° | `CL-C5-TIPOVER-WORST`, `CL-A1-TIPOVER` | `UNVERIFIED` (+3 %; C5 re-runs at D-62) |
| Hard landing: 1.2 m/s at ≤ 10° any direction, usable stroke 35 mm; n at 2.32 kg; foot side load limit / ult | 34.5; 6.59; 39.3 / 59.0 | mm; —; N | `CL-C5-SIM3D-V-SINK-10`, `-N`, `-SIDE-LOAD` | `MODELLED` (D-65; D5 shoe fix, C1/C4 at n 6.6) |
| Fin station first mode vs 80–330 Hz, 3-D solid FE (shell) | separation 0.29 (0.35) | — | `CL-C4-SIM-SEP`, `CL-C4-D3-SEP` | `UNVERIFIED` (tap test; re-run above 6 390 rpm) |
| Wing torsion modes (antisym / sym), beam (3-D FEA ≈ +9 %) | 11.9–14.4 / 24.1–29.0 | Hz | `CL-C2-F-TORSION-*` | `UNVERIFIED` (notch + tap test, D-45) |
| Wing foam at the block-pocket corners, ultimate (tension / compression) | 203 vs 150 / 199 vs 120 → R 3 mm + fillet bead | kPa | `CL-C2-FEA-FOAM-CORNER-S1`, `-S3` | `FAIL` as drawn → D-68 (C2 re-runs) |
| Prop clearance: blade swept volume to the motor tube at face_ahead 2.5 / 7.5 mm; to the wing upper skin | 21.1 `FAIL` / 26.1; 35.8 | mm | `CL-E1-TIP-GAP-TUBE`, `-AT-75`, `CL-B4-TIP-WING-FIX5` | `UNVERIFIED` (D-61; 25 mm gauge, T-B4-INSTALLED) |
| Elevon area fraction | 17.2 | % | `CL-A1-ELEVON-FRAC` | `CHECKED` |
| Box, external / fit slack along the chord on D7's real stack / box mass | 1.25 × 0.55 × 0.54 / 17 mm / 3.57 kg | m, mm, kg | `CL-A1-BOX-FIT`, `CL-D7-NOSE-GAP` | `PROPOSED` (two cars first; D7 nose pad 1/2 in, D-62) |
| Spend pessimistic / reserve / one crash | $1 687 / $313 / $309 | USD | `CL-I1-RESERVE-PESS`, `CL-A1-RESERVE` | `UNVERIFIED` (+1 %; $307 after the $6 antennas until I1's lever 1, D-72) |
| Field ambient ceiling (mission); ESC pad peak | 44; 56.1 | °C | `CL-E3-CEIL-MISSION`, `CL-E3-ESC-PEAK` | `UNVERIFIED` (SU2 pad h, T-E3-ESC-PAD-CFD) |
| Build to first hover | ≤ 90 (plan 70–85) | h | `params.json#requirements` | `PROPOSED` |

## General arrangement

![K09-L general arrangement, three views to scale](team/A1/ga-3view.svg)

`FIG A1-01 — General arrangement at revision A1-R5, 1 m = 500 px, drawn from params.json by team/A1/draw_ga.py.`

**Frame** (every CAD module, `interfaces.json`, the viewer and every analysis): metres, right-handed.
Origin at the wing root leading edge on the chord line. **x aft** (0 at the LE, 0.32 at the TE), **y to the right
wing tip**, **z up** in cruise attitude. In hover the nose points up and +x points at the ground. Symmetry plane
XZ. Fusion receives cm through `fusionkit`.

| Station | x | y | z | Unit | What is there |
|---|---|---|---|---|---|
| Wing LE / TE | 0 / 0.320 | ±0.575 | 0 | m | one-piece XPS core, S5010, chord 0.32, t/c 9.82 % (31 mm); no tape under the pod and fin roots (bond to bare foam) |
| Spar centreline | 0.080 | −0.50 … +0.50 | +0.0066 | m | CF 22 × 20 × 1 000 mm in a slot cut from the lower surface, on the camber line; four internal PETG plugs (Ø 19.8 × 36 at \|y\| 0.32 under the blocks, × 20 at \|y\| 0.242 under the brace anchors; D1 CR-D1-03) |
| CG target (range) | 0.0490 (0.0466–0.0514) | 0 | +0.0185 (+0.010 … +0.025) | m | 15.3 % chord; forward limit = elevon trim at the stall, aft = SM 5 % at 1.3 Vs, both with the CG height (B3 V1, D-62); A3-R6a 0.0522 in the D-47 bay, frame estimate 0.0485 → 0.0498 after D-61 / D-62 |
| Pod | −0.140 … 0.095 | ±0.07 | 0.015 … 0.085 | m | shell 0.235 × 0.14 × 0.07; bay 31 mm forward of R3 (forward stop −0.1312, aft stop 0.050) with the pack nominal centroid at x −0.032 (D-62; aft travel 12 mm to the no-spacer station −0.020; 2 mm spacer steps; the 135 mm Ovonic EC5 pack on the crush stack at −0.0379; stations per weighed pack from A3's live roll-up); XPS crush block ≥ 24.3 mm and a 1.5 mm spreader ahead of the pack, 1 mm epoxy bed at the nose wall; aft stop strutted to the handle bridge, forward stop flanged under the floor, handle feet bracketed to the side walls (C3 FEA, D-69); FC right channel on gel cubes with a strap, airspeed / RX left channel; power frame `PWR-006` with the AS150U cradle, PDB plate and the CoreWing power board at x −0.038 … 0.072; hatch, GPS mast, carry handle tied to the spar; spar saddle `POD-007` at x 0.080 |
| Motor tubes | 0.045 | ±0.32 | −0.172 … +0.172 | m | CF 22 × 20, 0.344 m, vertical through the core in the through-core block; ends inside the printed mounts |
| Through-core block | 0.045 / 0.080 | ±0.32 | 0 | m | printed PETG block 69 × 36 mm, vertical edges R 3 mm (D-68), in a full-depth core pocket with ≥ 3 mm microballoon fillet beads along the pocket edges: vertical bore for the tube, spanwise bore for the spar, 35 mm apart |
| Half-fins (4) | 0.045 … 0.320 | ±0.32 | 0 … ±0.21 | m | two 4.8 mm foam-board layers, chord 0.275, LE on the tube, TE = wing TE; 10 × 1 mm CF edge strips pinned with Ø 2.5 mm CF at 15 mm (D-70); 13 mm station collar on the tube (ear at z ±0.1535) with a 10 × 2 mm CF brace to a spar anchor at y ±0.242; 15 mm root fillets (30.6 g for four) credited fail-safe only |
| Motors (axis at the plate) | 0.045 (plate face 0.0244, tube front face 0.034) | ±0.32 | ±0.19 | m | stations `UR` `UL` `LR` `LL`; ASA mounts (slip collar 2.5 N·m, the tip-over fuse; cheeks +5 mm, rocking stiffness ≥ 1 100 N·m/rad), plate 29 × 30 × 4.5 mm canted 7° with the prop end leaning toward the wing and outboard (`cant_sense_UR` −1, D-52), 7.5 mm ahead of the tube face (D-61); shaft along −x; ESC on an ASA pad (31 mm high) on the outboard face at x 0.078–0.124, \|z\| 0.104–0.132, 680 µF cap 3 mm aft of it |
| Prop planes | −0.0127 | ±0.32 | ±0.19 | m | ⌀ 0.279 m; vertical pair gap 0.10 m, lateral 0.36 m; blade swept volume (+10 / −6 mm) 26.1 mm from the CF tube (D-61; was 21.1 at −0.0077), 35.8 mm from the wing upper skin; ≥ 39.1 mm from the plane to the collar front; LH adapters on the CW motors, adapter screws 2.0 mm engagement by deviation (D-58) |
| Feet | 0.320 … 0.368 | ±0.32 | ±0.218 (pad contact) | m | printed shoe on a 9.5 mm step of a 45.4 mm square fin tip (strips end at x 0.2746; sleeve end wall 2.0 mm, rim 3.0, 25 mm engagement for the 59 N ultimate side load, D-65), piston + pre-crushed XPS constant-force cartridge (upper 39.6 N, lower 35.4 N; 17.3 × 13.3 mm section), 48 mm foot, 38 mm flange-to-sleeve gap (35 mm usable: 1.2 m/s at ≤ 10° any direction), neoprene pad, snap-fit swap ≤ 10 min; 48 g allocated; TE corner caps at y ±0.575 (span 1.152 m) |
| Elevons (per side) | 0.2496 … 0.320 | 0.07–0.30 and 0.34–0.56 | 0 | m | 22 % chord, two panels on one Savox SH-0255MG+ (≥ 3.93 kgf·cm through the four-bar); 5 × 4 mm CF torque tube in each panel, 3/32 in inter-panel rod through the notch in the lower half-fin root x 0.2376–0.2616; full travel to VA 20.5 m/s, the VD half of the schedule held by envelope (`THR_MAX` 70 %, D-50) |
| Pitot tip | −0.220 | −0.046 | 0.045 | m | plug-in 6 mm keyed boom in the left channel, 80 mm ahead of the pod nose (part unchanged, D-47 / D-62); barbed tube couplers at the root |
| Box (external) | 1.25 × 0.55 × 0.54 | | | m | props off, pitot boom off, packs in the LiPo bag: envelope 1.152 × 0.508 × 0.438 (chord slack 17 mm on D7's 4 mm shell + 1/2 in nose pad); cradles at y ±0.20 on 120 mm crush columns bearing on the tape skin, lid pillars over the spar; floor drop 0.3 m, "keep upright" (D-53) |

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
| Allocation (g) | 405 | 437 | 146 | 48 | 462 | 648 | 45 | 123 | 72 | 214 | **2 600** | **2 600** |

Every allocation carries its designer's delivered `parts.csv` plus the simulation-round fixes (D-63): fins take the
root fillets as drawn (30.6 g), Ø 2.5 mm pins and the 13 mm collar; the pod takes C3's strut, flange and brackets
and the 10 mm nose; landing takes the shoe sleeve fix; mechanisms return 8 g (1/8 in CF rod). The 214 g reserve
equals A3's growth by maturity (114 g at A3-R6a) plus the 100 g first-build overrun with 0 g free; it is released
only through a change request, and the next release needs a lever (D3's fillet filler, block fill and cheek levers up
to −23 g; the 12 g harness return). The pack is the Ovonic 120C EC5 at 551 ± 5 g (D-64); the overrun stays covered
up to `CL-A1-PACK-ACCEPT` (592.6 g), which is the T-E2-WEIGH pass line.

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
| Through-core block | fins: block | wing: spar, core | fins | printed PETG block, vertical edges R 3 mm, bonded in a pocket with ≥ 3 mm fillet beads on both surfaces (D-68) | C4 (961 N couple, MS +0.55), C6 (bond RF 5.7–6.3), C2 (pocket-corner foam MS −0.26 / −0.40 as drawn, FEA re-run on the radius) |
| Tube in block | fins: tube | fins: block | fins | bonded | C4, C6 |
| Half-fin root to wing | fins: half-fin | wing: core (bare foam) | fins | bonded before skinning, tape lapped 15 mm up the board | C4, C6 (RF 1.12, thin) |
| Station collar and brace | fins: collar, brace | fins: tube; wing: spar anchor at y ±0.242 | fins | bonded collar 13 mm tall (D-70) with a 40 mm two-face tail whose strip-tail bond is a build inspection item; brace ends ≥ 10 mm in printed slots; anchor pull-off | C4 (163 N design, collar 6.26 N·m), C6 (RF 1.09 at 13 mm on C1's 7.4 N·m; tail 1.27 at 1 248 N) |
| Edge strips | fins: CF strip | fins: board | fins | bonded + Ø 2.5 mm CF pins every 15 mm (D-70) | C6 (RF 0.20 bare → 1.59 pinned at 72.7 N per pin) |
| Motor to mount | propulsion: motor | fins: ASA mount (7° cant, sense −1) | fins | 4 × M3×8 into the 4.5 mm canted plate, 3.5 mm engagement, 0.20 N·m, Loctite 243, drilled pattern | C6, E1 |
| Mount to tube | fins: motor mount | fins: tube | fins | slip collar, pinch bolts, 2.5 N·m slip: the mount fails before the tube (D-23); cheeks +5 mm for the 7.5 mm `face_ahead` (D-61) | C4 (≥ 1 100 N·m/rad pass level, D-70), C6 (3.2 N·m prop-nut case RF 3.3) |
| Prop to motor | propulsion: prop + adapter | propulsion: motor | propulsion | adapter screws M3×4, 2.0 mm engagement by deviation (D-58), 0.5 N·m + 243; M6 nut, LH on the CW motors, 1.5 N·m with the pouch spanner | E1, C6 |
| ESC to fin | propulsion: ESC | fins: ASA ESC pad (31 mm high) | fins | one 10 mm hook-and-loop strap through the slots beside the ESC, FET side out, in the slipstream; cap foam-taped 3 mm aft | E3 (61.6 °C), F1 |
| Foot to fin tip | landing: shoe | fins: half-fin tip step (45.4 mm square, step at \|z\| 0.2005, bare laminate) | landing | bonded shoe 1 350 mm² (RF 1.57); drawn 8 mm cheeks clamp both strip ends (carry 53 % of the tip twist, 3-D FE); sleeve end to RF ≥ 1 at 59 N ultimate side load (D-65); piston snap-fit, swap ≤ 10 min | C5 (sim side load 39.3 N limit), C4 (T-C4-FIN-PROOF decides the cheek extension), C6 |
| Pod to wing | pod: shell | wing: core (bare, sanded foam) | pod | bonded 10 014 mm² + 2 nylon ties under the spar + one bracket per side from the handle feet to the side walls (≥ 1 000 mm² each, D-69); 5 mm fillet in the recess-step corner | C3 (FEA R 0.56 design tied, 0.95 crash +z) |
| Pack in pod | power: pack | pod: tray, stops, straps, crush block | pod | 3 mm printed stops: forward stop through a floor slot to a 12 mm flange, aft stop strutted by three ribs to the handle bridge (D-69); 1.5 mm guides, 50 mm strap overlap, 6 mm corner fillets under the straps | C3 (as drawn the stops peel the board at 400 kPa vs 50), C5 (85 N crash; ≤ 100 g) |
| Power frame | power: `PWR-006` (AS150U cradle, PDB plate, power board) | pod: tray inserts | power | 4 × M3×18 nylon pan head into M3 × 5.7 brass inserts, 5.5 mm engagement, 0.2 N·m | F1, C6 |
| Avionics mounts | avionics: FC, GPS, RX, airspeed | pod: tray, mast | avionics | FC on four 5 mm gel cubes with a 10 mm strap; airspeed on foam tape; mast pad 45°, PA66 cross-bolt | F3, C6 |
| Pitot boom | avionics: pitot boom | pod: nose socket with flange | avionics | plug-in, keyed, barbed couplers, removed for transport | B4 (placement), F3, C6 |
| Elevon hinge | wing: core TE | wing: elevon panel | wing (D6 designs) | tape hinge, bevelled lower edge | D6 |
| Servo in wing | mechanisms: servo frame | wing: lower-skin servo pocket | mechanisms | bonded frame 1 855 mm² (≥ 720, VD 27.2, D-50); servo ears captured in slots, cover on M2 × 6 screws (exception to M3-only, D-58); servo neutral centred in the ≤ 0.84° play band (CR-B3-23) | D6, C6 |
| Horn and pushrod | mechanisms: horn, pushrod | wing: elevon panel | mechanisms | through-panel horn bonded 1 109 mm² onto the 5 × 4 mm torque tube, 2-56 clevis + keeper | D6, C6 |
| Inter-panel link | mechanisms: 1/8 in pultruded CF rod (D-63) | mechanisms: horns on both panels | mechanisms | crosses the lower half-fin root through the 24 × 12 mm notch; root fillets stopped there | D6, D3 |
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

## Simulation round: what failed as designed and what fixed it (A1-R5)

| Finding (role, tool) | Claim | Fix | Decision |
|---|---|---|---|
| Static margin 4.76 % at A3's CG, 4.33 % predicted: the CG sits 18.5 mm above the chord plane, which moves the effective NP 3.4 mm forward (B3, AVL 4 lattices + hand formula) | `CL-B3-V-CG-A3-AFT-ENV` −0.77 mm | range [0.0466, 0.0514] with the CG height; pack bay 10 mm forward; prop plane 5 mm forward; `cg.z_target_m` 0.0185 | D-62, D-61 |
| Blade swept volume 21.1 mm from the motor tube (E1 CAD probe, B4 exact geometry, A5 hull test) | `CL-E1-TIP-GAP-TUBE` −16 % | `face_ahead_m` 7.5 mm → 26.1 mm | D-61 |
| Diagonal touchdown at 1.5 m/s bottoms the stroke from 5° of tilt; shoe sleeve RF 0.22 at the simulated 59 N side load; n 6.59 at 2.32 kg (C5, 6-DOF with friction, SU2 FEA 3 meshes) | `CL-C5-SIM3D-BOTTOM-TILT`, `CL-C5-FEA-SHOE-SF`, `CL-C5-SIM3D-N` | 1.2 m/s at ≤ 10° any direction; shoe sleeve wall 2.0 / rim 3.0 / 25 mm engagement; n 6.6; side load 39.3 / 59.0 N | D-65 |
| Spiral t2 3.51 s from Cl_β +0.023 at the raised CG (B3) | `CL-B3-V-LAT-T2` | A2 decides: t2 ≥ 3.3 s with roll-stabilised modes only (A1's position) | D-66 |
| Wing foam at the block-pocket corners 203 / 199 kPa ultimate; fin-root tab fails if the root fillet carries load (C2, SU2 + in-house FEA, 3 levels) | `CL-C2-FEA-FOAM-CORNER-S1/-S3`, `-FILLET-SENS` | block edges R 3 mm, pocket fillet beads, cut-out radii, fillet fail-safe only, seam-free LE | D-68 |
| Pod aft stop peels the board at 408 kPa vs 50, forward-stop bed 391 kPa, spar-clamped shell R 1.40 (C3, SU2 FEA 4 levels) | `CL-C3-FEA-AFT-*`, `-FWD-BED-PEEL`, `-TIED-*` | strut, floor flange, wall brackets, recess-corner fillet (+13.9 g) | D-69, D-63 |
| Fins 434.8 g vs 418: the 15 mm root fillets weigh 30.6 g drawn (D3, C4); 2 mm pins bend at C4's 72.7 N; 12 mm collar at RF 1.00 (C6) | `CL-D3-MASS`, `CL-C6-STRIP-PIN-RF` | fins 437 g, pins 2.5 mm, collar 13 mm; tip cheeks decided by test (3-D FE gives MS +0.11, not −0.54) | D-63, D-70 |
| Fin drag 1.23 × the hand value (B1, SU2 2-D RANS, GCI 5.8 %): CD0 0.0579; cruise 235 W at 2.436 kg, 16.2 min | `CL-B1V-CD0`, `CL-B1V-CRUISE-P` | 240 W stands (agrees at the gate); E2 12.0 / 6.4 min; E1 re-runs L/D | D-67 |
| ESC pad h 64.6 W/m² K (E3, SU2 RANS): ESC 56.1 °C, ceiling 44 °C | `CL-E3-ESC-PEAK`, `CL-E3-CEIL-MISSION` | keys and notes updated | D-67 |
| Stall and transition pass by 0.1 % at the forward CG (B2, XFOIL + AVL; SU2 clmax not converged); B1 and B2 differ 9 % on CLmax | `CL-B2R3-VS-GATE-FWD` | T-B2-STALL is a gate on the twin and the first build; B1 / B2 / B3 reconcile; the lower CLmax is carried | D-71 |

## Before the mid-December order

Mandatory de-risking from `CONFIGURATION.md`: fly the $40 foam-board twin on the real motors, FC and pack (hold
1 m in 5 m/s, then a transition); tune it as a plain flying wing before any transition; the stable ArduPilot Plane
tailsitter build for the CoreWing F405 Wing V2 is confirmed (F3, 2026-11-09); measure RFS wind against RCMC1; order
electronics, two Ovonic 120C EC5 packs (D-64: ≤ 592.6 g each, 10 AWG leads), the US-stock carbon tube and the props
early (~20 Nov); bend-test the tube by 10 Dec (C4, H1); Jacobs Hall's written yes for the borrowed soldering kit
before 20 Nov (D-72). Weigh the pack and the tube on arrival (`team/A1/HANDOFF.md`). Fly the slow-flight stall on the
twin at the gate mass and the forward CG before `ARSPD_FBW_MIN` is frozen (D-71). Before the first hover: check the
cant sense on every mount with an inclinometer and a hanging yaw test (D-52), the blade-to-tube gap with the 25 mm
gauge (D-61), and the pack station mark for the weighed pack (D-62). Reverse to K01-lean on the conditions listed there.

## Integration state (A1-R5)

| Check | Result | Owner of the next step |
|---|---|---|
| `interfaces/merge_check.py` (162 parts, 252 edges, 2 320 g) | FAIL: 1 error (CG 0.052 m outside the D-62 range 0.047–0.051, expected until D2 re-lays the bay and A3 re-runs), 1 warning (propulsion 462 g float tie, CR-A1-59); the fins 435 / 418 g warning is cleared by D-63 | D2, D3, D5, A3 |
| `fusion/check.py` | 4 keep-out errors (motor tube 21.0 mm) until D3's 7.5 mm mount; then expect 0 | D3, E1, A5 |
| `team/A3/mass_rollup.py` | A3-R6a: 2 322 / 2 436 g, CG 0.0522 m, z +0.0185 m in the D-47 bay; re-run owed on the R5 deliveries | A3 |
| `team/A1/frame_claims.py` | 24 claims, no negative margin (CG range +0.0 / +0.04 mm on B3's V1 limits; packs +1.5 / +1.5 mm; box 17 mm; pack acceptance 592.6 g; tip-over 30.98°) on three stop-gap assumptions (`ASM-A1-A3-PACK-X`, `-STACK-DX`, `-R5-ADDED-G`) that A3's re-run retires | A1 |
| `proofs/build_graph.py` | not completed in this session (the build was still re-running other roles' scripts after 25 min); A1's 24 claims re-compute clean in frame_claims.py; drift is expected in every script that reads the R5 keys (B3, B4, B1, E1, E2, E3, C1, C3, C4, C5, D2, D3, D5, D7, F4, H1) until the owners re-run | each owner, after D2, D3 and A3 |
