# Joints and fasteners — K09-L

Owner C6. Revision **C6-R4**, 2026-11-10, at params A1-R4a (D-48 … D-59), C1 envelope R4 (VD 27.2 m/s), C4 fin FE as
published in `team/C4/claims.d3.json` (re-run 2026-11-10 04:28: strip 1 248 N, pin 72.7 N, collar 6.26 N·m, read
directly), fins D3-R4 (`subsystems/fins/params.json`: collar 12 mm, zoned 15 mm root fillet), landing D5 (1 350 mm²
shoe), power F1 (`PWR-006` frame), pod C3/D2. Re-run in 1 s: `python -I redesign/team/C6/joints.py`,
`python -I redesign/team/C6/make_stacks.py`, then `python -I redesign/proofs/build_graph.py`. Every joint stack is
`PROPOSED`; every claim is `UNVERIFIED` until the C6 coupons run with the first prints. Machine-readable blocks for the
edge owners: [`joint_stacks.json`](joint_stacks.json) (82 edges + 3 withdrawn, `interfaces/SCHEMA.md` field names).

Check method: reserve factor RF = allowable / applied at the **design load** = C1 ultimate (1.5 × limit) × fitting
factor 1.15, × 1.25 more for anything printed or bonded (`ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR`).
RF ≥ 1.0 passes; the proof chain shows the margin RF − 1.

## What changed since C6-R3

The R3 claims had drifted on 22 stored values: C4 re-ran its fin FE after R3 was issued, D3 deleted
`ASM-D3-FILLET-LEG` (it now draws the 15 mm fillet), and C3 and D5 moved. `joints.py` now reads the drawn fillet leg
from `fin_detail.fin.root_fillet.leg_m` and every C4 load from `claims.d3.json`, so it re-runs clean.

| Item | R3 (C4 numbers in the CR-C4-23 text) | R4 (C4 claims as published now) | Consequence |
|---|---|---|---|
| Collar torsion | max(C1 7.40, C4 4.61) N·m + 164 N brace | **max(C1 7.39, C4 6.26) N·m** + 163 N brace: C1 still governs (C1 read 7.42 an hour earlier) | 12 mm RF **1.00** (0.9998 … 1.003 between C1 runs), needs 11.96 mm → **13 mm, RF 1.09** (CR-C6-32) |
| Strip end force per face | 908 N | **1 248 N** (`CL-C4-D3-STRIP-END-F`) | tail RF 1.74 → **1.27**; net section 1.57 → **1.14**; H1 lever frame too small (CR-C6-33) |
| Pin force at 15 mm | 64 N | **72.7 N** (92 N in the 20:44 run) | 2 mm pins **RF 0.82**; 12 mm pitch (CR-C6-25) gives only 1.02 → **Ø 2.5 mm at the drawn 15 mm, RF 1.59** (CR-C6-31) |
| Strip anchor claim for H1 | 908 N | **`CL-C6-STRIP-ANCHOR-F` 1 248 N**, pass line in `T-C6-STRIP-ANCHOR` now written from the claim | CR-H1-12 answered; CR-C6-33 |
| Root fillet | 12 mm drawn (RF 0.87), 15 mm proposed (1.24) | **D3 draws 15 mm, zoned (CR-D3-25): RF 1.14** | CR-C6-24 closed; zoning accepted |
| Foot shoe `E-GER-01…04` | 1 350 mm², 87.4 N, RF 1.54 | 1 350 mm², **85.7 N, RF 1.57** (= `CL-D5-BOND-SF`) | — |
| Pod bond (C3) | 1.15 / 1.29 crash | **1.13 / 1.38** | — |
| Pin edges `E-FIN-69…80` | no C6 block (D3 carried the R1 text "77 N, RF 1.41") | C6 blocks issued | D3 copies |
| Power frame, mast bolt, servo areas, deviations, withdrawn stacks | issued in R3 | unchanged; re-checked | — |

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| How many fastener sizes? | **One bought thread, M3**: steel 8 and 16 mm, PA66 16 and 18 mm, one nyloc, one washer, one heat-set insert. M2 and 2-56 only as supplied mechanism hardware, M3x4 + M6 nut with the prop adapter (D-58) | kit table | `PROPOSED` |
| Fastened joints pass? | Yes. Motor screws 0.20 N·m on the canted plate: head RF 1.32, 3.5 mm engagement, separation RF 3.73. Power frame at 0.08 N·m: engagement RF 1.22, install 1.35, tension 1.46, friction 1.24, insert 1.74 | `CL-C6-MOTOR-*`, `CL-C6-CANT-ENGAGE`, `CL-C6-PWR-*` | `UNVERIFIED` |
| Station collar? | **No margin at 12 mm**: RF 1.003 on C1's 7.39 N·m + 204 N brace shear, and 0.9998 on C1's previous 7.42; it flips with each C1 run. 13 mm gives RF 1.09 for ≈ +0.6 g `EST` (all four) | `CL-C6-COLLAR-RF`, `-L-REQ`, `-RF-13MM`, `-RF-16MM` | `UNVERIFIED` (zero margin) → CR-C6-32 |
| Fin bonds? | Strip tail 1.27, tail net section 1.14 (one strip), brace ends 2.35, anchor 1.35, block bonds 5.0–5.7. **Pins as drawn (Ø 2 at 15 mm) 0.82**; Ø 2.5 at 15 mm 1.59 (bearing 3.4, strip net 2.4); fallback Ø 2 at 9 mm 1.36 | `CL-C6-STRIP-*`, `-BRACE-*`, `-TUBE-BLOCK-RF` | `FAIL` → CR-C6-31 |
| Foam bonds? | Foot shoe 1.57. Fin root 1.14 as drawn. Servo frame and horn ≥ 719 mm² each (D6 horn 1 385) | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF`, `-LINK-BOND-AREA-MIN` | `UNVERIFIED` |
| Pod joints? | Pod bond 1.13 / 1.38 crash, tray 2.59, hatch tab 1.18. Floor-to-wall glue line 0.90 bare, 2.03 with the 6 mm fillet C3 flies | `CL-C6-POD-*` | `UNVERIFIED` |

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
| Pultruded CF rod **Ø 2.5 mm** × 1 m | — | 1 + 1 spare | strip through-pins at 15 mm (CR-C6-31): 12 per half-fin × 4 = 48 × 11.6 mm ≈ 0.56 m | 2.5 mm drill |
| Supplied, not bought | M3x4 × 4 + M6 nut + washer per adapter (`PRP-004`); servo cover M2 × 6 and 2-56 clevises (D6); gel cubes (F3) | — | prop adapter, mechanisms, FC | 2.5 mm hex, 10 mm spanner, Phillips #1 |
| Ground (D7 buys) | handle stacks `E-TRN-13…15`: M3x16 + fender washer + nyloc on a ply strip | — | transport box | 2.5 mm hex, 5.5 mm spanner |

Tool set for the whole aircraft: 2.5 mm hex key, 5.5 and 10 mm spanners, Phillips #1, luggage scale.

## Fastened and retained joint stacks

Ids are the declared edges in `subsystems/*/interfaces.json`. Order = install / removal within the owner's build.

| Interface | Parts | Fastener × n | Hole / insert | Engagement (min), mm | Washer / nut | Torque · locking | Design load · check | Status |
|---|---|---|---|---|---|---|---|---|
| `E-FIN-61…64` | `PRP-001-<st>` → `FIN-003-<st>` | M3x8 SHCS × 4 | Ø 3.4 drilled square to the canted 4.5 mm plate on the measured pattern | 3.5 (3.0); ≤ probed depth − 0.5 | none, head flat | **0.20 N·m** + 243 on tip | 89 N per screw incl. 7° side moment 0.14 N·m ult; head RF 1.32, no-gap RF 3.73, strip RF 29 | `PROPOSED` |
| `E-FIN-05…08` | `FIN-003-<st>` → `FIN-002-<R/L>` | M3x16 SHCS × 1 | Ø 3.4 through both ears (grip 10.5) | 5.5 past grip (5.0) | 2 washers + nyloc | set by `T-D3-SLIP` (85–100 N at the can), ≈ 0.14 N·m, ≤ 0.4 | prop nut 3.23 N·m: bearing RF 3.26, hoop 5.94; 7° side: slip RF 16.8 / 48 | `PROPOSED` |
| `E-PWR-03` | `PWR-006` frame → `POD-002` | **M3x18 PA66 × 4** | deck and spacer Ø 3.4; brass insert, bore 4.0 × 6.5 | **5.5 (4.5)**, ≤ 5.7; tip 1.0 clear | 0.5 nylon washer + 2.0 deck + 10 nylon spacer | **0.08 N·m** (1.6 N at 50 mm), no 243, witness | 50 N unplug at 18 mm: 39 N tension per screw, RF 1.46; shear 108 N, friction RF 1.24 (0.62 after creep, then spacer bending RF 7.2); insert RF 1.74; install RF 1.35 | `PROPOSED` (CR-C6-26) |
| `E-POD-06` | `POD-005` → `POD-007` | M3x16 PA66 × 1 | Ø 3.4 across the boss | 6.0 past grip (4.0); grip 10.0 (≤ 11.0) | PA66 nut | finger + ¼ turn (≤ 0.08 N·m) | mast is the fuse; non-magnetic | `PROPOSED` (D2 adopted CR-C6-18) |
| `E-AVN-01` | `AVN-001` → `POD-002` | 4 gel cubes 5 mm, no screws (F3) | — | — | + 10 mm strap over the board, 1–2 mm slack | — | 10 N crash on the strap if the cubes let go | `PROPOSED` |
| `E-AVN-04` | airspeed board → `POD-002` | foam tape + 1 tie (D-33) | — | — | — | — | 6 g part | `PROPOSED` |
| `E-MEC-35/36` | `MEC-007-<L/R>` → `MEC-008-<L/R>` | M2 × 6 self-tapping × 2 (D-58 b) | 1.6 pilot, 6 deep | 5.2 (4.0) | — | snug | cover only | `PROPOSED` (D6) |
| `E-PRP-01…04` | `PRP-004-<st>` → `PRP-001-<st>` | M3x4 × 4 (supplied) | bell tapped | 2.5 (**2.0, D-58 a**) | — | 0.5 N·m + 243 | RF 1.70 (`CL-E1-ADAPTER-STRIP`) | `PROPOSED` |
| `E-PRP-05…08` field | `PRP-003-<st>` → `PRP-004-<st>` | M6 nut ISO 4032 (LH on CW motors) | prop on LPAR06E ring | nut fully on (5.2) | 1.0 mm washer | 1.5 N·m, bell held | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` |
| `E-TRN-13…15` ground | handle → box | M3x16 × 2 + 12 mm fender washer + nyloc on a 3 mm ply strip | Ø 3.4 | grip ≤ 11.0 → ≥ 5.0 (nyloc + 2 pitches) | — | snug, wall not crushed | 57–59 N per bolt, 27 kPa on Coroplast | **confirmed** (CR-D7-10) |
| withdrawn | `E-MEC-03/04` (servo in ear slots, D6), `E-PWR-05` (bus board taped, F1) | — | — | — | — | — | no C6 stack | — |

## Bonded joints

Adhesive: one 30 min laminating epoxy for everything. **Structural** (printed and CF parts): + ~5 % colloidal
silica, bond gap 0.1–0.3 mm. **Foam** fillets: + glass microballoons. Prep: PETG/ASA and CF 120 grit + IPA; paper
face 220 grit without tearing; foam dust-off only. Cure 24 h ≥ 18 °C; parts within 50 mm of a motor get 4 h at
50 °C post-cure (CR-C6-04).

| Interface | Parts | Area, mm² | Design load | Allowable | RF | Claim | Status |
|---|---|---|---|---|---|---|---|
| `E-FIN-01/02` | tube in block bore (43 mm) | 2 972 | 13.0 N·m torsion (J-FIN Mz 9.04 ult) | 2.0 MPa | 5.03 | `CL-C6-TUBE-BLOCK-RF` | `UNVERIFIED` |
| `E-FIN-49/50` | block on spar (36 mm) | 2 488 | 9.7 N·m torsion | 2.0 MPa | 5.66 | `CL-C6-BLOCK-SPAR-RF` | `UNVERIFIED` |
| `E-FIN-13…16` | station collar on tube, **12 mm** drawn | 829 | 15.9 N·m (C1 7.39 limit) + 204 N brace shear → 1.99 MPa | 2.0 MPa | **1.003** (0.9998 at C1 7.42); 13 mm **1.09**; 16 mm 1.34 | `CL-C6-COLLAR-RF`, `-RF-13MM`, `-L-REQ` 11.96 mm | `UNVERIFIED` (zero margin) → CR-C6-32 |
| `E-FIN-29…36` | strip end in the two-face tail, 39.5 mm | 790 per strip | **1 248 N** per strip | 2.0 MPa; tail net 15 MPa on 95 mm² | 1.27 (needs 31.2 mm); net 1.14 | `CL-C6-STRIP-ANCHOR-F`, `-ANCHOR-RF`, `-EMBED-REQ`, `-TAIL-NET-RF` | `UNVERIFIED` |
| `E-FIN-21…28` | strip on board paper (locating bond; the pins carry the shear) | 2 239 | C4 FE 4.85 N/mm design | paper 0.10 MPa | paper alone 0.21 | `CL-C6-STRIP-FACE-RF` | info |
| `E-FIN-69…72` | CF through-pins strip-board-board-strip, 11.6 mm, bonded in | 12 per half-fin | 72.7 N per pin at 15 mm | 50 MPa shear; 400 MPa bending (reaction at board mid-plane, bound) | Ø 2 drawn **0.82**; **Ø 2.5: 1.59**; Ø 2 at 9 mm 1.36; Ø 2 max pitch 12.2 mm | `CL-C6-STRIP-PIN-RF`, `-PIN-RF-PROP`, `-PIN-RF-ALT`, `-PIN-PITCH-MAX` | `FAIL` → CR-C6-31 |
| `E-FIN-73…80` | pin bearing in each 10 × 1 mm strip | — | 72.7 N per pin; 1 248 N strip force at the hole | 100 MPa CF bearing (`ASM-C6-CF-BEARING`); 400 MPa | bearing 3.44; net section 2.40 (Ø 2.5 hole) | `CL-C6-STRIP-PIN-BRG-RF`, `-NET-PIN-RF` | `UNVERIFIED` |
| `E-FIN-37…44` | brace ends in ear and anchor slots (10 mm) | 240 | 204 N | 2.0 MPa | 2.35 | `CL-C6-BRACE-END-RF` | `UNVERIFIED` |
| `E-FIN-57…60` | anchor saddle on spar, 90° contact | 276 | 204 N pull-off | 1.0 MPa | 1.35 | `CL-C6-ANCHOR-PULL-RF` | `UNVERIFIED` |
| `E-FIN-53…56` | half-fin root fillets on XPS, zoned as D3 R4 draws them (15 mm effective root, 13 mm aft of hinge, 6 mm bead) | 5 318 upper / 5 078 lower | D3 L4 case μ 0.7 | 0.125 MPa | **1.14** (= 0.5 × `CL-D3-ROOT-FILLET-RF` 2.28) | `CL-C6-FIN-ROOT-RF` | `UNVERIFIED` |
| `E-FIN-45…48` | ESC pad on board | 1 288 | 1.4 N (crash) | 0.10 MPa | > 90 | — | `PROPOSED` |
| `E-GER-01…04` | foot shoe on fin tip step | **1 350** | **85.7 N** | 0.10 MPa | **1.57** | `CL-C6-FOOT-SHOE-RF` (= `CL-D5-BOND-SF`) | `UNVERIFIED` |
| `E-POD-01` | pod shell on core | 10 014 | C3 envelope / 12.75 g crash | 0.125 / 0.10 MPa | 1.13 / 1.38 | `CL-C6-POD-WING-RF`, `-POD-CRASH-RF` | `UNVERIFIED` |
| `E-POD-02` | tray on floor, flat-wise under a strap | 13 505 | 19.3 kPa | 0.05 MPa | 2.59 | `CL-C6-POD-TRAY-RF` | `UNVERIFIED` |
| inside `POD-001` | floor-to-side-wall line under the front strap | 4.8 mm edge | 111 kPa | 0.10 MPa | 0.90 bare → **2.03 with the 6 mm fillet** | `CL-C6-POD-FLOOR-RF(-PROP)` | `UNVERIFIED` (C3 flies the fillet) |
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
| After a hard landing or tip-over | + coin-tap block region, collars, strip tails and pin rows (no pin end proud, no strip split at a hole); flex each fin tip 5 mm and listen; rock each motor by hand | no dull spot, no creak, no play |
| Every 10 flights | motor-screw and frame witness marks (PA66 creeps: re-snug the frame to 0.08 N·m); mast bolt; anchor bonds; pod spar ties; FC strap | marks unbroken, frame does not rock |
| Every bond batch | witness cup cured beside the part; batch and time on the build log | cup hard, not tacky |

## Tests — with the first prints (H1)

| Test | Coupon | Pass line | Replaces | Claims |
|---|---|---|---|---|
| `T-C6-LAP-PETG` | 5 PETG–CF and 5 ASA–CF single laps, 25 × 12.5 mm | mean × 0.5 ≥ 2.0 MPa (13 mm collar); **below 1.85 MPa the collar goes to 16 mm**; ≥ 2.05 MPa lets 12 mm stand | `ASM-C4-BOND-SHEAR` | tube, spar, collar, brace, strip tail |
| `T-C6-BOARD-LAP` | 5 PETG tabs on board in shear + 5 flat-wise | mean × 0.5 ≥ 0.10 / 0.05 MPa | `ASM-D5-BOND-TAU`, `ASM-C6-BOARD-FLAT-TYP` | foot shoe, strip face, tray |
| `T-C6-XPS-PULL` | 5 pucks pulled + 5 pushed on F-250 | mean × 0.5 ≥ 0.125 / 0.10 MPa | `ASM-D3-XPS-TENSILE`, `ASM-C6-XPS-SHEAR-TYP` | fin root, pod bond, servo frames |
| `T-C6-BOARD-CORNER` | 2 board U-sections (bare, filleted) under a strap pull | ≥ 43 N per strap | — | pod floor glue line |
| `T-C6-INSERT` | 3 inserts in 7 mm bosses on a 0.8 mm plate **bonded to board** | ≥ 300 N each, or record the plate-peel load | `ASM-C6-INSERT-PULL` | power-frame inserts |
| `T-C6-NYLON-TORQUE` (new) | 5 PA66 M3x18 into inserts through the 12.5 mm stack | mean failure torque ≥ 0.16 N·m (3.2 N at 50 mm); 48 h at 0.08 N·m keeps ≥ 0.04 N·m breakaway | `ASM-C6-PA66-SIGMA` | power frame |
| `T-C6-HEAD-CREEP` | ASA plate on an Al block, 4 × M3x8 at 0.20 N·m, 2 h at 70 °C | breakaway ≥ 0.15 N·m | `ASM-C6-HEAD-BEARING` | motor head |
| `T-C6-CANT-SEAT` | first printed mount A with the motor | ≥ 6 turns to seat, 0.05 mm feeler does not enter | — | engagement on the canted plate |
| `T-C6-STRIP-ANCHOR` | collar as drawn + 40 mm tail with a strip pair; pull **one** strip on H1's lever frame | **≥ `CL-C6-STRIP-ANCHOR-F`, 1 248 N today** (the procedure text is written from the claim on every run) | — | strip tail, tail net section |
| `T-C6-PROPNUT` | finished mount, 10 × 1.5 N·m | witness line unmoved | — | mount rock, hoop |

Each coupon set takes under an hour from shop stock. All ten run before the fin build starts.

## Findings

| # | Finding | Number | Action |
|---|---|---|---|
| 1 | C4 re-ran its fin FE after C6-R3 was issued, so the CR-C4-23 text (908 N, 64 N, 4.61 N·m) no longer matches C4's published claims. Two runs 8 h apart gave the strip end 1 198 → 1 248 N and the pin force 92 → 73 N. C6 sizes for the whole spread, not for one value | strip +37 %, pin +14…44 % on R3 | CR-C6-34 (publish one R4 set; update the CR text and `BOOM-STRUCTURES.md`) |
| 2 | Collar: C1's section torsion still governs, and 12 mm sits exactly on RF 1.00. It read 0.9998 at C1 7.42 N·m and 1.003 at 7.39 N·m, an hour apart | RF 1.00 → 1.09 at 13 mm | CR-C6-32 |
| 3 | 2 mm pins bend past 400 MPa at every C4 pin force. A 12 mm pitch (CR-C6-25) gives only 1.02 at 73 N and fails at 92 N | Ø 2.5 at 15 mm: 1.59 (1.25 at 92 N) for ≈ +1.5 g `EST` | CR-C6-31 supersedes CR-C6-25 |
| 4 | The strip-anchor design force is now 1 248 N. H1's 6:1 lever frame (1 177 N) is below it and below H1's 1.25 × proof (1 560 N) | needs ≥ 1 560 N | CR-C6-33 |
| 5 | Tail net section with one strip loaded is now 1.14. With both strips of a pair loaded together it is 0.57 | RF 1.14 / 0.57 (bound) | CR-C6-29 re-sent with the new force (CR-C6-34) |
| 6 | D3 draws the 15 mm fillet with zoning, and at the C6 XPS allowable the root is 1.14 | was 0.87 | CR-C6-24 closed; zoning accepted (CR-D3-25) |
| 7 | F1's 0.20 N·m on a PA66 M3 yields the shank (install RF 0.54); 0.08 N·m gives 1.35 | — | CR-C6-26 (open with F1) |
| 8 | D2's PDB-plate bosses are Ø 7.0 mm, which leaves a 1.5 mm wall around the 4.0 mm bore | rule ≥ 1.6 mm | CR-C6-27 (open with D2) |

## Open issues

1. Every allowable is `UNVERIFIED` until the coupons run. The thin RFs are the collar (1.09 at 13 mm), the tail net
   section (1.14), the fin root (1.14), the pod bond (1.13) and the hatch tab (1.18). The Ø 2 mm pins fail as
   drawn and the 12 mm collar has no margin; the fixes are with D3 (CR-C6-31, -32).
2. C4's fin loads moved twice after R3 without a note. C6 reads them live, so `joints.py` must be re-run whenever
   `team/C4/claims.d3.json` changes. The figures here come from the run of 2026-11-10 at about 04:30.
3. The tail net-section check uses D3's 95 mm² estimate and one strip's force (CR-C6-29, CR-C6-34).
4. Mass: CR-C6-31 (+1.5 g) and CR-C6-32 (+0.6 g) land on a fins line that is 18.4 g over (`MASS-CG.md`, CR-A3-26).
   Both are `EST`; D3 reports the CAD delta.
5. Motor bolt pattern, hole depth and bell thread depth are measured on arrival (E1); F1 measures the power-frame
   stack.
