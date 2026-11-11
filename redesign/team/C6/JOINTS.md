# Joints and fasteners — K09-L

Owner C6. Revision **C6-R5b**, 2026-11-10, at params A1-R5 (D-63 … D-72). Inputs read live: C1 claims and
`team/C1/data/envelope.json` (D-65 re-run of 14:29: half-fin section torsion **12.67 N·m** limit, J-FIN Mz 17.18 N·m
ult); C4's frozen R4 fin set `team/C4/claims.d3.json` (11:51: strip 1 243 N, pin 72.4 N, collar 6.24 N·m, solved at
C1's earlier 7.37 N·m); fins D3-R5b (`subsystems/fins/params.json`: pins Ø 2.5 at 15 mm, collar 15 mm, block edges
R 3 mm, root fillet fail-safe only); D5 R5 shoe bond (1 350 mm², 85.7 N, RF 1.57); F1 power frame. Re-run in a few
seconds: `python -I redesign/team/C6/joints.py`, `python -I redesign/team/C6/make_stacks.py`, then
`python -I redesign/proofs/build_graph.py`. Joint stacks `PROPOSED`; claims `UNVERIFIED` until the C6 coupons run.
Blocks for the edge owners: [`joint_stacks.json`](joint_stacks.json) (84 edges + 1 withdrawn). Every fastener of
every stack is a modelled part since R5c: [`FASTENERS-CAD.md`](FASTENERS-CAD.md) (`fastener_parts.py`).

Check method: reserve factor RF = allowable / applied at the **design load** = C1 ultimate (1.5 × limit) × fitting
factor 1.15, × 1.25 more for anything printed or bonded (`ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR`).
RF ≥ 1.0 passes; the proof chain shows the margin RF − 1.

## What changed since C6-R4

The R5 action items were run as asked (C4's frozen set, 13 mm collar, 2.5 mm pins, D5's bond, the R 3 mm pocket,
fillet RF kept on the joint side). Two things moved underneath them. First, the four C1 envelope values `joints.py`
held as hand copies had drifted (J-FIN Mz 9.04 → 17.18 N·m ult), so they are now read live from `envelope.json`.
Second, C1 re-ran for D-65 (n 6.6, 39.3 / 59.0 N foot side load) twice during this session, and the half-fin torsion
went 7.39 → 8.13 → **12.67 N·m** limit. At 8.13 N·m the 13 mm collar read RF 0.9995, so C6 asked for 15 mm (CR-C6-36)
and D3 drew it within the hour. At 12.67 N·m, 15 mm is not enough either.

| Item | C6-R4 | C6-R5b (now) | Consequence |
|---|---|---|---|
| Collar torsion, max(C1, C4) | max(7.39, 6.26) N·m + 163 N brace | **max(12.67, 6.24) N·m** + 163 N brace (C1 governs) | needs **19.45 mm**; drawn 15 mm RF **0.77**; 16 mm 0.82 → **22 mm, RF 1.13** (CR-C6-37). The D-70 12 mm option is void (0.63 even at 4.1 MPa) |
| Pins | Ø 2 drawn 0.82; Ø 2.5 proposed 1.59 | **Ø 2.5 at 15 mm drawn: 1.60** on C4's 72.4 N | D-70 closed for C4's R4 load; on D-65 loads, estimate **0.93** (CR-C6-38) |
| Strip tail anchor / net section | 1.27 / 1.14 at 1 248 N | 1.27 / 1.15 at 1 243 N (C4 frozen) | estimate on D-65 loads **0.74 / 0.67** at ≈ 2 130 N: hold collar and tail prints for C4 (CR-C6-38) |
| Tube in block / block on spar | 5.03 / 5.66 | **2.65 / 4.64** (envelope read live) | still pass |
| Root fillet | 1.14 (15 mm, zoned) | **0.81** on D-65's 59 N side load; fail-safe only (D-68) | kept as a C6 claim; D3's CR-D3-35 (zone to 0.185 m) supported |
| Block pocket (D-68) | — | new `CALC-C6-BLOCK-POCKET`: wall area × 0.976; square-corner void 1.24 mm; pocket corner R 3.0–4.2 mm; beads 1.1 g | `E-FIN-51/52` rewritten; CR-C6-40 to D1 |
| Foot shoe `E-GER-01…04` | 1.57 | **1.57**, 85.7 N on 1 350 mm² (D5 R5) | — |
| Power frame `E-PWR-03` | 0.08 N·m | unchanged, **open with F1** (CR-C6-26) | — |
| Avionics crash load | 10.0 N (hand copy) | 5.62 N (envelope) | insert RF set by the unplug case; still 1.74 |

The `-EST` claims (`CALC-C6-FIN-SCALE`) scale C4's frozen strip and pin forces by k = C1 torsion now / the torsion C4
solved at (12.62 / 7.37 = **1.71**). The D-65 side load drives both the torsion and the strip couple, so linear scaling
is the right first estimate. They are bounding estimates for planning and retire when C4 re-runs.

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| How many fastener sizes? | **One bought thread, M3**: steel 8 and 16 mm, PA66 16 and 18 mm, one nyloc, one washer, one heat-set insert, plus Ø 2.5 CF rod for pins. M2 and 2-56 only as supplied mechanism hardware; M3x4 + M6 nut with the prop adapter (D-58) | kit table | `PROPOSED` |
| Fastened joints pass? | Yes. Motor screws 0.20 N·m: head 1.32, separation 3.69, 3.5 mm engagement. Power frame at 0.08 N·m: engagement 1.22, install 1.35, tension 1.46, friction 1.24, insert 1.74 | `CL-C6-MOTOR-*`, `-CANT-ENGAGE`, `-PWR-*` | `UNVERIFIED` |
| Station collar? | **Fails as drawn.** 15 mm RF 0.77 on C1's 12.67 N·m; needs 19.45 mm; **22 mm gives 1.13** for ≈ +4.4 g `EST` (four) | `CL-C6-COLLAR-RF`, `-L-REQ`, `-RF-PROP` | `FAIL` → CR-C6-37 |
| Fin strips and pins? | On C4's frozen R4 loads: tail 1.27, net section 1.15, pins 1.60, bearing 3.45, strip net 2.41. **On C1's D-65 loads (estimate ×1.71): tail 0.74, net 0.67, pins 0.93** | `CL-C6-STRIP-*`, `-*-EST` | `FAIL` (estimate) → CR-C6-38 |
| Block bonds and pocket? | Tube in block 2.65, block on spar 4.64; pocket corners R 3.0–4.2 mm, no square corners | `CL-C6-TUBE-BLOCK-RF`, `-BLOCK-SPAR-RF`, `-POCKET-*` | `UNVERIFIED` |
| Foam bonds? | Foot shoe 1.57. Root fillet 0.81 (fail-safe path, D-68). Servo frame and horn ≥ 719 mm² | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF`, `-LINK-BOND-AREA-MIN` | root `FAIL` → D3 CR-D3-35 |
| Pod joints? | Pod bond 1.15 / 1.33 crash, tray 2.59, hatch 1.18, floor glue line 2.03 with the fillet C3 flies | `CL-C6-POD-*` | `UNVERIFIED` |

## Rules: which fastening goes where

| Situation | Use | Engagement minimum (D-41) | Torque / locking | Never |
|---|---|---|---|---|
| Steel screw into metal (motor base, prop adapter into the bell) | SHCS A2-70, tapped hole | ≥ 1.0 d (3.0 mm), except `E-PRP-01…04` (D-58: 2.0 mm); ≤ hole depth − 0.5 mm | per table; Loctite 243 on the **tip threads only** | threadlocker on or under a printed or nylon part |
| Through a printed part, both sides reachable | SHCS + ISO 7089 washer + ISO 10511 nyloc | nut fully on + 2 pitches (5.0 mm past the grip for M3) | ≤ 0.4 N·m; nyloc reused ≤ 3 times | split washers; plain nuts |
| Into a printed part, one side or repeated service | M3 × 5.7 brass heat-set insert, bore Ø 4.0 × ≥ engagement + 0.5 mm, boss wall ≥ 1.6 mm (boss Ø ≥ 7.2 mm), 230–245 °C | ≥ 1.5 d (4.5 mm), ≤ 5.7 mm (insert length) | steel ≤ 0.4 N·m; **PA66 ≤ 0.08 N·m**; no threadlocker; paint-pen witness | screws straight into printed plastic |
| Screw on a canted face | holes drilled square to the face, head seat parallel to it | as above | as above | holes normal to one face with the motor canted on pads |
| Within 50 mm of the compass, or beside bare bus bars | PA66 screw (+ PA66 nut) | nut fully on + 2 pitches; insert 1.5 d | ≤ 0.08 N·m (1.6 N on the luggage scale) | steel |
| Self-tapping into plastic | only the supplied M2 (servo cover, D-58); 1.6 mm pilot in a printed boss | ≥ 2.0 d (4.0 mm) | snug, head seated | |
| Anything into XPS or foam board | **no screw**: bond a printed hardpoint ≥ 719 mm² (`CL-C6-LINK-BOND-AREA-MIN`) and fasten into it | — | — | screws, pins or inserts in foam |
| Field joints | tool-free (straps, plug-ins, snap hooks), except the prop nut | — | — | any tool other than the one 10 mm spanner (D-40) |

Torque without a torque screwdriver: hook a luggage scale on the long arm of the hex key 50 mm from the screw axis;
0.08 N·m = 1.6 N, 0.20 N·m = 4.0 N (0.41 kg), 0.4 N·m = 8.0 N.

## Deviations from the thread rules (D-58, granted by A1)

| # | Interface | Deviation | Rule it breaks | Justification | Condition |
|---|---|---|---|---|---|
| a | `E-PRP-01…04` prop adapter → bell | vendor M3x4, **2.0 mm** minimum engagement (2.5 mm nominal) | 1.0 d into metal (3.0 mm) | strip RF 1.70 at 2.0 mm against the 0.83 kN tightening preload; service 14 N shear, 4 N axial per screw (`CL-E1-ADAPTER-STRIP`) | `T-E1-MOTOR-RM` measures ≥ 2.5 mm of bell thread; 0.5 N·m + 243 on the tips |
| b | `E-MEC-07…10`, `E-MEC-35/36` mechanisms | supplied **2-56** clevis thread; **M2 × 6** self-tapping cover screws (5.2 mm engaged in a 1.6 mm pilot, 6 mm deep) | M3 only | bought servo and clevis hardware; no M3 part at this size | silicone keeper on every clevis; covers snug only |

## Fastener kit (bought; I1)

| Item | Standard | Qty (incl. spares) | Used at | Tool |
|---|---|---|---|---|
| M3x8 SHCS A2-70 | ISO 4762 | 20 | motor to mount (`PRP-005`, 16) | 2.5 mm hex |
| M3x16 SHCS A2-70 | ISO 4762 | 6 | mount pinch bolts (4, `FIN-101`) | 2.5 mm hex |
| M3x16 PA66 screw + PA66 hex nut | — | 3 + 3 | GPS mast cross-bolt (1) | 2.5 mm hex / fingers |
| M3x18 PA66 screw, socket head preferred | — | 11 | power frame (4), `T-C6-NYLON-TORQUE` (5), spares | 2.5 mm hex (PH1 if pan head) |
| M3 nyloc A2 | ISO 10511 | 8 | pinch bolts | 5.5 mm spanner |
| M3 washer A2 | ISO 7089 | 12 | pinch bolts (8) | — |
| M3 × 5.7 brass heat-set insert | Ruthex RX-M3x5.7 class | 12 | power frame (4), `T-C6-INSERT` (3), spares | iron + insert tip |
| M3 nylon washer 0.5 mm + 10 mm nylon spacer (OD 6 / ID 3.2) | — | 6 + 6 | power frame | — |
| Pultruded CF rod **Ø 2.5 mm** × 1 m | — | 1 + 1 spare | strip through-pins at 15 mm (D-70): 15 per half-fin × 4 = 60 × 11.6 mm ≈ 0.70 m (76 pins ≈ 0.88 m at 12 mm, if CR-C6-38 needs it: still one rod) | 2.5 mm drill |
| Supplied, not bought | M3x4 × 4 + M6 nut + washer per adapter (`PRP-004`); servo cover M2 × 6 and 2-56 clevises (D6); gel cubes (F3) | — | prop adapter, mechanisms, FC | 2.5 mm hex, 10 mm spanner, Phillips #1 |
| Ground (D7 buys) | handle stacks `E-TRN-13…15`: M3x16 + fender washer + nyloc on a ply strip | — | transport box | 2.5 mm hex, 5.5 mm spanner |

Tool set for the whole aircraft: 2.5 mm hex key, 5.5 and 10 mm spanners, Phillips #1, luggage scale.

## Fastened and retained joint stacks

Ids are the declared edges in `subsystems/*/interfaces.json`. Order = install / removal within the owner's build.

| Interface | Parts | Fastener × n | Hole / insert | Engagement (min), mm | Washer / nut | Torque · locking | Design load · check | Status |
|---|---|---|---|---|---|---|---|---|
| `E-FIN-61…64` | `PRP-001-<st>` → `FIN-003-<st>` | M3x8 SHCS × 4 | Ø 3.4 drilled square to the canted 4.5 mm plate on the measured pattern | 3.5 (3.0); ≤ probed depth − 0.5 | none, head flat | **0.20 N·m** + 243 on tip | 90 N per screw incl. 7° side moment 0.14 N·m ult; head RF 1.32, no-gap RF 3.69, strip RF 29 | `PROPOSED` |
| `E-FIN-05…08` | `FIN-003-<st>` → `FIN-002-<R/L>` | M3x16 SHCS × 1 | Ø 3.4 through both ears (grip 10.5) | 5.5 past grip (5.0) | 2 washers + nyloc | set by `T-D3-SLIP` (85–100 N at the can), ≈ 0.14 N·m, ≤ 0.4 | prop nut 3.23 N·m: bearing RF 3.26, hoop 5.94; 7° side: slip RF 16.8 / 48 | `PROPOSED` |
| `E-PWR-03` | `PWR-006` frame → `POD-002` | **M3x18 PA66 × 4** | deck and spacer Ø 3.4; brass insert, bore 4.0 × 6.5 | **5.5 (4.5)**, ≤ 5.7; tip 1.0 clear | 0.5 nylon washer + 2.0 deck + 10 nylon spacer | **0.08 N·m** (1.6 N at 50 mm), no 243, witness | 50 N unplug at 18 mm: 39 N tension per screw, RF 1.46; shear 108 N, friction RF 1.24 (0.62 after creep, then spacer bending RF 7.2); insert RF 1.74; install RF 1.35 | `PROPOSED` (CR-C6-26) |
| `E-POD-06` | `POD-005` → `POD-007` | M3x16 PA66 × 1 | Ø 3.4 across the boss | 6.0 past grip (4.0); grip 10.0 (≤ 11.0) | PA66 nut | finger + ¼ turn (≤ 0.08 N·m) | mast is the fuse; non-magnetic | `PROPOSED` (D2 adopted CR-C6-18) |
| `E-AVN-01` | `AVN-001` → `POD-002` | 4 gel cubes 5 mm, no screws (F3) | — | — | + 10 mm strap over the board, 1–2 mm slack | — | 10 N crash on the strap if the cubes let go | `PROPOSED` |
| `E-AVN-04` | airspeed board → `POD-002` | foam tape + 1 tie (D-33) | — | — | — | — | 6 g part | `PROPOSED` |
| `E-MEC-35/36`, `E-MEC-03/04` | `MEC-007-<L/R>` → `MEC-008-<L/R>`; servo `MEC-001-<L/R>` held in the frame ear slots by the cover | M2 × 6 self-tapping pan head × 2 (`MEC-011-<L/R>`, the same two screws on both edges; D-58 b) | 1.6 pilot, 6 deep in the 4 × 5 × 6 mm end-wall bosses | 5.2 (4.0) | — | snug, from below (−z) | 2.0 N crash on 2 screws; thread shear 245 N each | `PROPOSED` (D6; 03/04 reinstated, FASTENERS-CAD) |
| `E-PRP-01…04` | `PRP-004-<st>` → `PRP-001-<st>` | M3x4 × 4 (supplied) | bell tapped | 2.5 (**2.0, D-58 a**) | — | 0.5 N·m + 243 | RF 1.70 (`CL-E1-ADAPTER-STRIP`) | `PROPOSED` |
| `E-PRP-05…08` field | `PRP-003-<st>` → `PRP-004-<st>` | M6 nut ISO 4032 (LH on CW motors) | prop on LPAR06E ring | nut fully on (5.2) | 1.0 mm washer | 1.5 N·m, bell held | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` |
| `E-TRN-13…15` ground | handle → box | M3x16 × 2 + 12 mm fender washer + nyloc on a 3 mm ply strip | Ø 3.4 | grip ≤ 11.0 → ≥ 5.0 (nyloc + 2 pitches) | — | snug, wall not crushed | 57–59 N per bolt, 27 kPa on Coroplast | **confirmed** (CR-D7-10) |
| withdrawn | `E-PWR-05` (bus board taped, F1) | — | — | — | — | — | no C6 stack | — |

## Bonded joints

Adhesive: one 30 min laminating epoxy for everything. **Structural** (printed and CF parts): + ~5 % colloidal
silica, bond gap 0.1–0.3 mm. **Foam** fillets: + glass microballoons. Prep: PETG/ASA and CF 120 grit + IPA; paper
face 220 grit without tearing; foam dust-off only. Cure 24 h ≥ 18 °C; parts within 50 mm of a motor get 4 h at
50 °C post-cure (CR-C6-04).

| Interface | Parts | Area, mm² | Design load | Allowable | RF | Claim | Status |
|---|---|---|---|---|---|---|---|
| `E-FIN-01/02` | tube in block bore (43 mm) | 2 972 | 24.7 N·m torsion (J-FIN Mz 17.18 ult) | 2.0 MPa | 2.65 | `CL-C6-TUBE-BLOCK-RF` | `UNVERIFIED` |
| `E-FIN-49/50` | block on spar (36 mm) | 2 488 | 11.8 N·m torsion | 2.0 MPa | 4.64 | `CL-C6-BLOCK-SPAR-RF` | `UNVERIFIED` |
| `E-FIN-51/52` | block in its core pocket, edges R 3 mm, ≥ 3 mm beads both surfaces (D-68) | 6 500 (× 0.976 with the radius) | secondary: the bores carry the block | 0.125 MPa | not credited | `CL-C6-POCKET-WALL-AREA-RATIO`, `-SQUARE-GAP` 1.24 mm, `-R-MAX` 4.2 mm, `-BEAD-MASS` 1.1 g | `PROPOSED` (CR-C6-40) |
| `E-FIN-13…16` | station collar on tube, **15 mm** drawn | 1 037 | 27.3 N·m (C1 12.67 limit) + 204 N brace shear → 2.59 MPa | 2.0 MPa | **0.77**; 16 mm 0.82; **22 mm 1.13** | `CL-C6-COLLAR-RF`, `-RF-15MM`, `-RF-PROP`, `-L-REQ` 19.45 mm | `FAIL` → CR-C6-37 |
| `E-FIN-29…36` | strip end in the two-face tail, 39.5 mm | 790 per strip | **1 243 N** per strip (C4 R4); ≈ 2 130 N on D-65 (est.) | 2.0 MPa; tail net 15 MPa on 95 mm² | 1.27 / net 1.15; est. **0.74 / 0.67** (needs 53 mm and ≈ 140 mm²) | `CL-C6-STRIP-ANCHOR-*`, `-TAIL-NET-RF(-EST)`, `-EMBED-REQ` | `UNVERIFIED`; est. `FAIL` → CR-C6-38 |
| `E-FIN-21…28` | strip on board paper (locating bond; the pins carry the shear) | 2 239 | C4 FE 4.83 N/mm design | paper 0.10 MPa | paper alone 0.21 | `CL-C6-STRIP-FACE-RF` | info |
| `E-FIN-69…72` | CF through-pins strip-board-board-strip, Ø 2.5 × 11.6 mm, bonded in | 15 per half-fin | 72.4 N per pin at 15 mm (C4 R4) | 50 MPa shear; 400 MPa bending (reaction at board mid-plane, bound) | **1.60** drawn; max pitch 24.0 mm; fallback Ø 2 at 9 mm 1.36; est. on D-65 **0.93** (max pitch 14.0 mm) | `CL-C6-STRIP-PIN-RF`, `-PITCH-MAX`, `-RF-ALT`, `-RF-EST` | `UNVERIFIED`; est. `FAIL` → CR-C6-38 |
| `E-FIN-73…80` | pin bearing in each 10 × 1 mm strip | — | 72.4 N per pin; 1 243 N at the hole | 100 MPa CF bearing; 400 MPa | bearing 3.45; net section 2.41 | `CL-C6-STRIP-PIN-BRG-RF`, `-NET-PIN-RF` | `UNVERIFIED` |
| `E-FIN-37…44` | brace ends in ear and anchor slots (10 mm) | 240 | 204 N | 2.0 MPa | 2.35 | `CL-C6-BRACE-END-RF` | `UNVERIFIED` |
| `E-FIN-57…60` | anchor saddle on spar, 90° contact | 276 | 204 N pull-off | 1.0 MPa | 1.35 | `CL-C6-ANCHOR-PULL-RF` | `UNVERIFIED` |
| `E-FIN-53…56` | half-fin root fillets on XPS, zoned (15 mm over 0.15 m, 13 mm aft of hinge, 4 mm sealing bead ahead); **fail-safe path only (D-68)** | 5 318 upper / 5 078 lower | D3: 50 % of the D-65 side load, 59.0 N ult | 0.125 MPa | **0.81** (= 0.5 × `CL-D3-ROOT-FILLET-RF` 1.62) | `CL-C6-FIN-ROOT-RF` | `FAIL` → D3 CR-D3-35 |
| `E-FIN-45…48` | ESC pad on board | 1 288 | 1.4 N (crash) | 0.10 MPa | > 90 | — | `PROPOSED` |
| `E-GER-01…04` | foot shoe on fin tip step | **1 350** | **85.7 N** | 0.10 MPa | **1.57** | `CL-C6-FOOT-SHOE-RF` (= `CL-D5-BOND-SF`) | `UNVERIFIED` |
| `E-POD-01` | pod shell on core | 10 014 | C3 envelope / 12.75 g crash | 0.125 / 0.10 MPa | 1.15 / 1.33 | `CL-C6-POD-WING-RF`, `-POD-CRASH-RF` | `UNVERIFIED` |
| `E-POD-02` | tray on floor, flat-wise under a strap | 13 505 | 19.3 kPa | 0.05 MPa | 2.59 | `CL-C6-POD-TRAY-RF` | `UNVERIFIED` |
| inside `POD-001` | floor-to-side-wall line under the front strap | 4.8 mm edge | 111 kPa | 0.10 MPa | **2.03 with the 6 mm fillet** (0.90 bare, record only) | `CL-C6-POD-FLOOR-RF-PROP` | `UNVERIFIED` (C3 flies the fillet) |
| `E-POD-03` | hatch latch tab, hook-and-loop | tab per C3 | 2.11 N/cm² at VD 27.2 | 2.5 N/cm² | 1.18 | `CL-C6-POD-HATCH-RF` | `UNVERIFIED` |
| `E-POD-07` | pitot socket with a ≥ 30 × 30 mm flange | ≥ 900 | 0.8 N·m handling | 0.10 MPa | — | CR-C6-09 | `PROPOSED` |
| `E-MEC-01/02`, `11/12` | servo frame in core; horn in elevon | ≥ **719** each (D6 horn 1 385) | 89.9 N pushrod design at VD 27.2 (D-50; was 1 002 mm² at 32.1) | 0.125 MPa | — | `CL-C6-LINK-BOND-AREA-MIN` | `PROPOSED` (D6) |

## Pod allowables owned by C6 (CR-C3-05; C3 reads them, CR-C3-11)

| Allowable | C6 design value | Basis | C3 use |
|---|---|---|---|
| Epoxy into XPS, tension / shear | 125 / 100 kPa | 0.5 × 0.25 / 0.20 MPa typical | C3 keeps 100 kPa tension (conservative) |
| Foam board flat-wise / epoxy on paper face, shear | 50 / 100 kPa | 0.5 × 0.10 / 0.20 MPa | adopted (CR-C6-16) |
| Printed PETG across layers | 15 MPa | 0.5 × Z yield 30 MPa, below 50 °C | adopted |
| Hook-and-loop shear / tension | 5 / 2.5 N/cm² | 0.5 × catalogue, sew-on tape | adopted |

## Retention and field joints (no thread, no structural bond)

| Interface | Joint | Rule | Inspection |
|---|---|---|---|
| `E-GER-05…08` | foot piston snap hooks | free finger ≥ 6.0 mm for 2 % strain (`CL-C6-SNAP-L-MIN`); D5 draws 6.5 mm | hooks seated: pre-flight |
| `E-FIN-65…68` | ESC strap through pad and board | strap never over the heat sink | strap tight: pre-flight |
| `E-AVN-01` | FC on gel cubes | slack strap over the board for the crash | board does not lift with one finger |
| `E-PWR-03` field use | AS150U unplug | **thumb on the cradle while pulling the pack half** (the load stays in the hand) | frame does not rock |
| `E-POD-03`, `-05`, `-10` | hatch, pack straps, spacers | D2/C3 sized; 50 mm strap overlap | pre-flight card |
| `E-AVN-05` | pitot plug-in | keyed | seated: pre-flight |
| `E-MEC-07…10` | clevises (2-56, D-58 b) | silicone keeper sleeve on every clevis | keeper on: pre-flight |

## Inspection

| When | What | Pass |
|---|---|---|
| Every flight | 4 mount witness lines; prop nuts; feet hooks; hinge tape ends; clevis keepers; fin roots | lines unbroken, nuts tight, nothing lifting |
| After a hard landing or tip-over | + coin-tap block region, collars, strip tails and pin rows (no pin end proud, no strip split at a hole); look along each fin root for a crack line in the fillet (fail-safe path, D-68: a crack is a repair if collar and strips are sound); flex each fin tip 5 mm and listen; rock each motor by hand | no dull spot, no creak, no play |
| Every 10 flights | motor-screw and frame witness marks (PA66 creeps: re-snug the frame to 0.08 N·m); mast bolt; anchor bonds; pod spar ties; FC strap | marks unbroken, frame does not rock |
| Fin build (D-70, D-68) | strip tails: strips down to the tube surface, epoxy fills both slots over the full tail, tongue with 3 perimeters under each strip; tap/pull check before the fin closes. Block pocket: dry-fit, 0.5 mm feeler at every corner | no void, no strip movement at 20 N by hand, feeler does not enter |
| Every bond batch | witness cup cured beside the part; batch and time on the build log | cup hard, not tacky |

## Tests — with the first prints (H1)

| Test | Coupon | Pass line | Replaces | Claims |
|---|---|---|---|---|
| `T-C6-LAP-PETG` | 5 PETG–CF and 5 ASA–CF single laps, 25 × 12.5 mm | mean × 0.5 ≥ 2.0 MPa (22 mm collar at RF 1.13). Collar height needed = 19.45 mm × (2.0 MPa / allowable) × (C1 torsion / 12.67 N·m) | `ASM-C4-BOND-SHEAR` | tube, spar, collar, brace, strip tail |
| `T-C6-BOARD-LAP` | 5 PETG tabs on board in shear + 5 flat-wise | mean × 0.5 ≥ 0.10 / 0.05 MPa | `ASM-D5-BOND-TAU`, `ASM-C6-BOARD-FLAT-TYP` | foot shoe, strip face, tray |
| `T-C6-XPS-PULL` | 5 pucks pulled + 5 pushed on F-250 | mean × 0.5 ≥ 0.125 / 0.10 MPa | `ASM-D3-XPS-TENSILE`, `ASM-C6-XPS-SHEAR-TYP` | fin root, pod bond, servo frames |
| `T-C6-BOARD-CORNER` | 2 board U-sections (bare, filleted) under a strap pull | ≥ 43 N per strap | — | pod floor glue line |
| `T-C6-INSERT` | 3 inserts in 7 mm bosses on a 0.8 mm plate **bonded to board** | ≥ 300 N each, or record the plate-peel load | `ASM-C6-INSERT-PULL` | power-frame inserts |
| `T-C6-NYLON-TORQUE` (new) | 5 PA66 M3x18 into inserts through the 12.5 mm stack | mean failure torque ≥ 0.16 N·m (3.2 N at 50 mm); 48 h at 0.08 N·m keeps ≥ 0.04 N·m breakaway | `ASM-C6-PA66-SIGMA` | power frame |
| `T-C6-HEAD-CREEP` | ASA plate on an Al block, 4 × M3x8 at 0.20 N·m, 2 h at 70 °C | breakaway ≥ 0.15 N·m | `ASM-C6-HEAD-BEARING` | motor head |
| `T-C6-CANT-SEAT` | first printed mount A with the motor | ≥ 6 turns to seat, 0.05 mm feeler does not enter | — | engagement on the canted plate |
| `T-C6-STRIP-ANCHOR` | collar as drawn + 40 mm tail with a strip pair; pull **one** strip on H1's lever frame | **≥ `CL-C6-STRIP-ANCHOR-F`, 1 243 N today** (written from the claim on every run); frame sized to 1.25 × `-ANCHOR-F-EST` ≈ 2 660 N until C4 re-runs | — | strip tail, tail net section |
| `T-C6-PROPNUT` | finished mount, 10 × 1.5 N·m | witness line unmoved | — | mount rock, hoop |

Each coupon set takes under an hour from shop stock. All ten run before the fin build starts.

## Findings

| # | Finding | Number | Action |
|---|---|---|---|
| 1 | C1's D-65 re-run raised the half-fin torsion 7.39 → 12.67 N·m limit (×1.71) during this session; the foot side load went 22.8 → 39.3 N limit. The collar is sized directly on C1 (CR-C4-23 max rule) | 15 mm RF 0.77; needs 19.45 mm | CR-C6-37: 22 mm (RF 1.13) |
| 2 | C4's frozen R4 set was solved at the old side load (`CL-C4-D3-SIDE-LOAD` 22.8 N, section torsion 7.37 N·m), so its strip, pin and collar numbers are stale by ≈ ×1.71 | est. anchor 0.74, tail net 0.67, pins 0.93 | CR-C6-38: C4 re-runs on D-65; D3 holds collar, tail and pin prints |
| 3 | `joints.py` held four C1 envelope numbers as hand copies; J-FIN Mz had moved 9.04 → 17.18 N·m ult | tube-in-block RF 5.03 → 2.65 | fixed: read live from `envelope.json` |
| 4 | D-70's 12 mm collar condition (4.1 MPa coupon mean) no longer releases 12 mm | RF 0.63 at a 2.05 MPa allowable | withdrawn; `CL-C6-COLLAR-RF-12MM-COND` kept as the record |
| 5 | D-68 block pocket: a square-cut pocket round an R 3 block leaves a 1.24 mm void on each corner diagonal, where C2's foam peak sits | void 1.24 mm vs 0.5 mm bond line | CR-C6-40: corners R 3.0–4.2 mm or packed; feeler dry-fit |
| 6 | Root fillet fails at the C6 allowable on the D-65 side load. It is fail-safe only (D-68), but it is bonded and will see load | 0.81 | D3's CR-D3-35 (0.185 m zone, +5 g) supported; C4's fillet-intact share would refine the 0.5 share |
| 7 | F1's 0.20 N·m on a PA66 M3 yields the shank (install RF 0.54); 0.08 N·m gives 1.35 | — | CR-C6-26 (open with F1) |
| 8 | D2's PDB-plate bosses Ø 7.0 mm leave a 1.5 mm wall | rule ≥ 1.6 mm | CR-C6-27 (open with D2) |

## Open issues

1. The fin station joints are not closed: collar (CR-C6-37), strip tail, tail net section and pins on D-65 loads
   (CR-C6-38). The `-EST` claims are linear scalings of C4's R4 set, not C4 results.
2. C1 moved three times today. `joints.py` reads C1 and C4 live; re-run it after any change to `team/C1/claims.json`,
   `team/C1/data/envelope.json` or `team/C4/claims.d3.json`. Figures here: C1 14:29, C4 11:51.
3. Every allowable is `UNVERIFIED` until the coupons run; the collar height scales directly with the lap-shear result.
4. Mass: 22 mm collars ≈ +4.4 g `EST` over the drawn 15 mm; any tail or pin change from CR-C6-38 adds more. Fins sit
   at their 437 g allocation (D-63) with 0 g free reserve: A1 decides (CR-C6-37 cc A1).
5. The tail net section uses D3's 95 mm² estimate and one strip's force; the coincident pair force is still
   unpublished (CR-C6-29 / -34b).
6. Motor pattern, hole and bell-thread depths are measured on arrival (E1); F1 measures the power-frame stack.
