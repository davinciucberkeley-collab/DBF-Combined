# QP-3 CAD, concept A (scaled quad tailsitter), 2026-11-15

Group: CAD (A5 with the D roles). Files: `qp/A/cad/` (nothing else edited; K09-L tree, `fusion/`, `collision/`, `showcase/` untouched, no git). Labels: `DOC` number from an A document, `V` vendor page read 2026-11-15, `EST` estimate or CAD interpretation, `CALC` computed here, `-` unknown.

## 1. Verdict

A is modelled as 69 parts (67 solids + 2 mass proxies), 85 interface edges and 11 routed wires on the **unmodified K09-L framework** (`fusionkit`, `k09kit`, `merge_check`, `check.py`, `collide_blender.py`), stub backend, same JSON schema (`dbf-interfaces/1`).

| Gate | Result |
|---|---|
| CAD check (`fusion/check.py --root qp/A/cad/model`) | **PASS**, 0 errors, 0 warnings (module build, part data, edge registration, touch, floating, prop and ground keep-outs, graph) |
| Collision gate (`collide_a.py`, the K09-L checker on A's job: static + elevons at both limits, 0.05 mm) | **PASS**, 0 part pairs penetrate, 0 wire ends off a termination, 0 wire folds (123 bodies, 67 parts, 11 wires) |
| Build sequence (`a_assembly.py`) | **PASS**: 24 steps, all 24 swept paths clear, all parts supported, no wire laid early (section 5) |
| Mass vs MASS-GATE | CAD basic 1,205 g vs MASS-GATE basic 1,194 g (+11 g, the structures iteration-2 overrun, section 4) |
| CG vs MASS-GATE | **CAD 16.2 mm aft of the LE vs 24.8 mm predicted: 8.6 mm further forward** (section 4). Inside the 4.0-28.5 mm limits, outside the 20-26 mm design band |

## 2. What is built (all in `qp/A/cad/a_model.py`; `model/<sub>/` has the generated `interfaces.json` and a 6-line module stub per subsystem)

| Module | Parts | Geometry (mm; `DOC` unless marked) |
|---|---|---|
| wing | core, spar, 5 plugs, 2 elevons | chord 245, span 900, 9.5 % section 23 mm (reflex placeholder, `EST`: no A section file); spar CF 12x10 x 900 at x 60; PETG plugs at y 0, +-300, +-380; elevons y 40-340, chord 25 % and +-20 deg (`EST`); core back face slanted as a cove for the elevon nose; servo pockets, grooves and bores cut by seat |
| fins | 2 tubes, 2 ribs, 2 root blocks, 2 fairings, 2 rib saddles | tube 16x14 x 360 at (x 294, y +-380); fairing 3 mm XPS; rib 14x12 from the saddle (x 70) to the tube front (x 286); saddle 60 mm wide on the spar |
| cage | hub, 4 arms, 4 cups, bridge, 2 V struts, saddle, 2 clamps, pack tray | hub at (-75, 0, 0); arms 12x10 x 245, motors at y +-228 / z +-156 (R 276, arm x1.2); bridge 12x10 from the hub to the spar saddle; struts 6x4.5 from the hub to clamps on the spar at y +-285; cup = 5 mm plate + arm sleeve; hub is a 100 x 60 disc envelope (a printed shell, 16 g) |
| propulsion | 4 motors, 4 props, ESC | MN2212 27.5 x 26.5 (`V`), shaft 4; prop = swept disc 228.6 (APC 9 in) 16 mm thick (`EST`); **16 deg cant about the arm axis, same sense on all four** (DOC D-184); ESC 35 x 35 x 5.5 (`V`) with solder-pad bodies |
| power | pack | Tattu 2300 4S 105 x 35 x 29 (`V`), centre 20 mm ahead of the LE (DOC), long axis along y, on a tray lying on the bridge |
| avionics | plate, 4 gel pads, FC, RX, GPS, airspeed, pitot | plate follows the upper skin on the core's own vertices (x 27-127, y +-55, bonded to the core, which the spar carries); **FC at the wing centre on four 5 mm gel pads** (SITL-FLIGHT follow-up 2: not on the cage hub, whose 8-15 Hz flex modes destabilise the roll and yaw loops), centre x 86 (26 mm aft of the spar axis), y 0, the nearest cage part (pack tray) is 71 mm forward; FC 30 x 25 x 20 (`V`, stack envelope); RX, GPS, MS4525 sizes `EST`; pitot at y +0.41 in an LE groove (outside the rotor wash, `EST`) |
| mechanisms | 2 servos, arms, pushrods, horns | ES3352HV 23.3 x 9.45 x 26 (`V`) at y +-200 (moved in from DOC y 300, which is inside the elevon, `EST`); rod 1.2 mm to a horn on the elevon |
| landing | 4 shoes, 4 pads | PETG cap on each tube end, EVA/PE pad 12 x 15 x 30 (DOC); hover ground at x 337.5 (`EST`), keep-out `KO-GROUND` |
| harness, assembly | 2 mass proxies (`HRN-001` 56.5 g, `HRD-001` 37 g), 11 wires, all joints | every wire starts and ends on a named termination body (ESC pad joints, FC header / pad bodies, pack lead exit, motor phase-lead exit, servo lead exit, JST plugs); motor leads run over the LE and along the aft side of each arm and enter the cup through a drilled hole |

Keep-outs (check.py): four canted prop zones (swept blade volume + 5 mm), the hover ground plane. All pass.

## 3. Findings and fixes made while closing the gates

1. **Latent defect in the K09-L collision gate (not fixed there, worked around here).** `manufacturing/blender_mesh._body` orients meshes with `recalc_face_normals` on a mixed-winding raw mesh. For every part rotated about X by more than 90 deg (A's UL and LL arms, cups, motors, props) the result was **inside out**: `inside()` found no point inside the body, so seat cuts failed, 6 false overlaps appeared and a wire end could not be seated. A silent inside-out body also hides real overlaps. `a_collide_blender.py` reverses any body with negative signed volume at run time (the K09-L script is imported unchanged). **A4/A5 should apply the same fix in `blender_mesh._body`; K09-L's own PASS rests on every part happening to come out outward.**
2. Strut ends touched the spar (0.49 mm): ends pulled back 2 mm. Elevon at +20 deg touched the core cove (0.13 mm): cove slope 22 -> 24 deg. Wire bends tighter than the wire (3): lanes raised so every segment is >= 6 mm.
4. **FC placement (coordinator requirement, SITL-FLIGHT follow-up 2).** The FC was already on the wing-centre plate, not on the hub; it now sits on 4 gel pads (`AVN-007`, 1.6 g `EST`, edges `CT-GEL-PAD`), raised 5 mm, and every FC wire (ESC lead, servo leads, RX, GPS, airspeed) was re-routed 7 mm higher to its new headers; check and collision gates re-run after the change. Load path: FC - gel - plate - core - spar, no cage member. The FC is 26 mm aft of the spar axis, not on it (the ESC occupies the plate forward of it); moving it onto the spar axis means swapping ESC and FC and re-routing the pack lead around the FC: not done. Gel stiffness and the FC filter / notch setting are `-` until the first tethered hover.
3. Parts moved or changed against the documents so that the model is buildable: servos inboard (y 200, was 300 inside the elevon); the wing aft strips outboard of y 340 and at the centre are not modelled (the rib, the fin and the elevon gap occupy them); spar clamps, bridge saddle and rib saddles are **C-clips open downward** with access slots in the core so the cage docks from below (section 5).

## 4. Mass and CG from the CAD vs `MASS-GATE.md`

Declared masses (`MASS-GATE` s2 lines and STRUCTURES iteration 2, vendor pages `V` for bought parts), CG = CAD volume centroid per part (lumps: declared).

| Group | CAD g | MASS-GATE g | x of group CG, mm aft of LE |
|---|---|---|---|
| Wing (core, spar, plugs, elevons) | 191.1 | 220 | 91.3 |
| Fins (tubes, ribs, blocks, fairings, rib saddles) + feet | 111.8 + 10.0 | 70 | 249.6 / 304.9 |
| Cage (hub, arms, cups, bridge, struts, saddle, clips, tray) | 120.5 | 135 | -57.9 |
| Motors + props + ESC | 324.2 | 260 + 44 + 20 = 324 | -93.1 |
| Pack | 270.0 | 270 | -20.0 |
| Avionics (itemised 53.5 + harness remainder 56.5) | 110.0 | 110 | 72.4 / 30.0 |
| Servos + linkage | 30.0 | 30 | 146.0 |
| Hardware lump | 37.0 | 35 (+3 g rib saddles carried in the fins line) | 100.0 |
| **Total basic** | **1,204.6** | **1,194** | **16.2** (y +2.0, z +7.5) |

* Mass: +10.6 g over MASS-GATE basic, all in the fins line (+52 g) offset by wing -29, cage -15: the structures bottom-up (473 g vs 460 g, iteration 2). Adding MASS-GATE's growth (139 g) and overrun (48 g) gives 1,392 g predicted against 1,381 g (+11 g); gate 1,500 g, target 1,440 g: **both hold**. The avionics harness remainder (56.5 g) is the budget line less the itemised parts, not a weighed number (`EST`).
* **CG 16.2 mm vs 24.8 mm.** Not a modelling slip in one part: the motors and props sit at x -99 / -121 (motor frame at the arm plane x -75 plus cup, can and prop), the MASS-GATE 24.8 mm assumed the rest of the aircraft at 35.7 mm and the arms not moving it. SM from the CAD CG with NP 40.7 mm (`EST`, SIZING-A): (40.7 - 16.2) / 245 = **10.0 %** (limit 5 %): more stable, well inside the 4.0 mm forward limit, **4 mm ahead of the 20-26 mm design band**. The pack is the knob (20 mm of pack travel moves CG about 4 mm, MASS-GATE s5): to reach 24.8 mm the pack would have to move 38 mm aft (centre at x +18, over the wing), which is not needed; the question for A1/A2 is whether a forward CG costs elevon trim drag (not computed). Lateral CG +2.0 mm (the single pitot at y +410): inside 5 mm. Vertical CG 7.5 mm above the chord plane.
* Prop plane: the CAD puts the prop hub at x -121 (121 mm ahead of the LE); SIZING-A / STRUCTURES assumed 75-85 mm. The 16 deg cant and arm radius are DOC values; the fore-aft position of the motor is a CAD interpretation (cup plate in front of the arm axis, can and prop in front of that). **A3 must confirm 121 mm** (every 10 mm the arm plane, hub, cups, arms, motors and props move aft shifts the CG +3.3 mm: 394 g x 10 mm / 1,205 g).

## 5. Build sequence and assembly check

Sequence (`qp/A/cad/a_assembly_plan.py`, 24 steps, all 68 solid parts placed, every wire laid after both end parts are on): A wing core, spar from the tip, plugs up the bore; B cage unit **built on the bench** (hub, arms, cups, bridge, struts, saddle, strut clamps, tray, motors, props) and **docked from below** (+z) so the open-top C-clips snap on the spar, then the rib saddles; C ribs from aft, elevons, fairings from outboard, root blocks from aft, fin tubes down through the blocks, shoes, pads; D servos, arms, horns, pushrods from above; E pitot from the front, plate, ESC / gel pads / FC / RX / GPS / airspeed, pack into the tray. `a_assembly.py` checks (1) support (each part has a mechanical edge to something already on or to its own step), (2) the swept straight path of each step against everything placed earlier (K09-L collision meshes, cuts count as empty, 0.05 mm), (3) wire order. Sampling is coarse (3-100 mm steps by travel) to keep compute modest; a thin obstacle narrower than the step could be missed.

| Run | Result |
|---|---|
| First full run | 4 of 24 steps blocked: cage docking (clips opened the wrong way: slot faced down, the spar must enter from above; clip bosses overlapped the spar), rib saddles (core slot did not cover the ring), both fairings (rib groove an exact fit, 0.9 mm at 0.5 mm of travel) |
| After fixes (clips open up, bosses clear of the spar, core access slots open below, 0.5 mm fairing clearance), full run `out/ASSEMBLY-full-run.md` | 23 of 24 ok; B1 blocked by 0.71 mm (both V struts against the core) |
| Re-run to B2 after widening the slots | B2 ok, B1 still 0.71 mm (slot start, see below) |
| **Final full run** (`out/ASSEMBLY.md`) | **24 of 24 steps ok** |

**B1 closed (final fix):** the 0.71 mm graze was real, not sampling: the strut access slot in the core started at x 0 on a slanted edge, so the strut cut the LE foam just behind it. The slot now starts 12 mm ahead of the LE and the strut seat has a 0.5 mm per-side groove clearance (EST; a bonded slip fit, no C6 value found for foam). Check, collision and the full 24-step run (`out/ASSEMBLY.md`) all PASS after it.

**Left:** (b) the elevon tape hinge, tape skin, epoxy fillets, fasteners and the pack strap are not sequenced or drawn; (c) the C-clip docking and the open-bottom core slots are a CAD proposal for A2/A3 (foam strips close the slots after docking): confirm it or choose a split-hub cage; (d) a swept check of laid wires (done in place by `collide_a.py`, not along a path).

## 6. Estimates and CAD interpretations to confirm (all `EST`)

1. Airfoil: K09-L reflex placeholder at 9.5 % (no A section file). Elevon chord 25 %, +-20 deg, inboard end y 40; hinge on the upper surface; all four are not in any A document.
2. Prop plane x -121 and cup geometry (section 4). Cant sense: all four motors canted about their arm axis in the same circulation sense; the sign that gives yaw authority with the rotor reaction must be checked against the spin directions (A-P7).
3. Hub 100 x 60 solid envelope for a 16 g printed shell; arm sockets are 18.5 mm deep (DOC 25 mm); bridge 154 mm (DOC 160); rib saddle socket 24 mm, strut clamp ring 16 mm; motor bolt pattern and the lead hole in the cup plate (the T-Motor drawing could not be read); motor lead exit position.
4. Avionics layout, RX / GPS / MS4525 sizes, pitot at y +410 with its tubing to the sensor (the tubing is not drawn), FC stack envelope 20 mm high.
5. Mass lumps: 56.5 g harness remainder and 37 g hardware are budget lines, not parts. Fasteners, epoxy fillets, tape skin and hinge tape are **not drawn** (K09-L fastener kit not ported).
6. Pack strap is not drawn (the tray lips and end walls hold the pack; the edge is `CT-STRAP-VELCRO`).
7. The mesh orientation defect in section 3 item 1 should be fixed at source; until then `collide_a.py` is the only gate that sees A's UL / LL parts correctly.

## 7. Reproduce

```
python -I redesign/qp/A/cad/build_a.py        # regenerate model/*/interfaces.json (CGs from the CAD) and run check.py
python -I redesign/qp/A/cad/collide_a.py      # collision gate, about 2 min (Blender 4.5 in the background, no render)
python -I redesign/qp/A/cad/a_assembly.py     # build-sequence check -> out/ASSEMBLY.md
```

## 8. CG note for A1 / B3 (CAD 16.2 mm aft of the LE vs the 20-26 mm design band)

`CALC` from the CAD masses (basic 1,205 g). **Why it is forward:** the pack is where MASS-GATE put it (centre -20 mm), but the *rest of the aircraft* (935 g) is at **26.7 mm** in the CAD against the 35.7 mm MASS-GATE assumed. The 9 mm difference is the cage and rotor group (394 g: motors 260, props 44, arms 54, hub 16, cups 20) sitting at x -57 to -121, and the 16 deg-canted motor stack with the prop plane 121 mm ahead of the LE (SIZING assumed 75-85 mm).

| Knob | Effect on CG (CALC) | Cost / note |
|---|---|---|
| Pack station | 17 mm aft (centre -3 mm, pack just touching the LE) = +3.8 mm, **20.0 mm, lower edge of the band**; 38 mm aft (centre +18 mm, over the wing) = +8.6 mm, 24.8 mm | pack station is bounded by the tray and the LE; SIZING-A computed SM 4.9 % for the pack at the LE with its 35.7 mm assumption, which the CAD does not support (CAD with pack at the LE: CG 20.7 mm, SM 8.2 %) |
| Cage and rotor plane | 10 mm aft = +3.3 mm | arm 245 mm and radius are DOC; moving the prop plane aft cuts the 121 mm to ~110 mm and needs the cup/arm frame re-cut |
| ESC, FC, avionics (110 g) | 10 mm aft = +0.9 mm | small |
| Wing / fin | fixed | fins at x 250, already aft |

SM with NP 40.7 mm (`EST`): CG 16.2 -> **10.0 %**; 20 -> 8.4 %; 24.8 -> 6.5 %; 26 -> 6.0 %. The CAD CG is inside the hard limits (4.0 forward, 28.5 aft) and is more stable than the target, so the issue is not safety but whether the band is the right band. **Not decided here (A1 / B3):** (1) keep the layout and lower the band to about 14-22 mm because the band was derived from a 35.7 mm "rest of aircraft" that the CAD contradicts (cost: more nose-up trim demand on the elevons at 17 m/s, not computed, and a larger pitch-over moment in transition), or (2) keep the band and move the pack to about -3 mm (and/or the cage plane 10 mm aft) so the CAD CG reaches 20 mm. Weigh the pack option against its effect on the tray / LE clearance and against NP being `EST`; the M5 CG breadboard measures NP and settles it.
