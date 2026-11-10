# Joints and fasteners — K09-L

Owner C6. Revision **C6-R3**, 2026-11-09, at params A1-R4 (D-48 … D-59), C1 envelope R4 (VD 27.2 m/s), C4 R3 fin
model (`CL-C4-D3-*`, read directly), fins D3-R4 (`subsystems/fins/params.json`: collar 12 mm), landing D5 (1 350 mm²
shoe), power F1 (`PWR-006` frame), pod C3/D2. Re-run in 1 s: `python -I redesign/team/C6/joints.py`,
`python -I redesign/team/C6/make_stacks.py`, then `python -I redesign/proofs/build_graph.py`. Every joint stack is
`PROPOSED`; every claim is `UNVERIFIED` until the C6 coupons run with the first prints. Machine-readable blocks for the
edge owners: [`joint_stacks.json`](joint_stacks.json) (70 edges + 3 withdrawn, `interfaces/SCHEMA.md` field names).

Check method: reserve factor RF = allowable / applied at the **design load** = C1 ultimate (1.5 × limit) × fitting
factor 1.15, × 1.25 more for anything printed or bonded (`ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR`).
RF ≥ 1.0 passes; the proof chain shows the margin RF − 1.

## What changed since C6-R2

| Item | R2 | R3 | Why |
|---|---|---|---|
| Collar torsion | C4 R2 9.3 N·m (`ASM-C6-C4-COLLAR-T`, not a C4 output) | **max(C1 `CL-C1-FINHALF-T-LIM` 7.40, C4 `CL-C4-D3-COLLAR-T` 4.61) N·m** + C4 brace 164 N as shear; C1 governs | CR-C4-23 |
| Collar height | 16 mm, RF 1.09 | **12 mm as D3 drew it (D-48): RF 1.00, needs 11.98 mm**; 16 mm fallback RF 1.34 | D3-R4; thin, gated by `T-C6-LAP-PETG` |
| Strip tail force | derived from C4's edge margin | **`CL-C4-D3-STRIP-END-F` 908 N per strip**, published as `CL-C6-STRIP-ANCHOR-F` for H1 | CR-C4-23 (b), CR-H1-12 |
| Strip tail | 2 × 10 × 40 mm | 2 × 10 × 39.5 mm = 790 mm² (LE gap 0.5 mm): RF 1.74; tail net section 9.6 MPa on D3's 95 mm², RF 1.57 | CR-D3-17 |
| Strip pins | 52 N, RF 1.15 | **C4 FE 64 N per pin at 15 mm: RF 0.92 FAIL** → 12 mm pitch RF 1.15 | CR-C4-23 (c) → CR-C6-25 |
| Power frame `E-PWR-03` | M3x10 A2 into inserts (bought PCB) | **4 × M3x18 PA66 into the brass inserts, 5.5 mm engaged, 0.08 N·m** (F1's 0.20 N·m yields the nylon: RF 0.54) | CR-F1-20, CR-A4-44 → CR-C6-26 |
| Foot shoe `E-GER-01…04` | 1 100 mm², RF 1.35 | **1 350 mm², 87.4 N design, RF 1.54** (= `CL-D5-BOND-SF`) | CR-D5-24 |
| Root fillet | 15 mm proposed | 15 mm **adopted (D-48)**, RF 1.24; D3 still draws 12 mm (RF 0.87) | CR-C6-24 open with D3 |
| Servo frame / horn bond area | 1 002 mm² at VD 32.1 m/s | **719 mm² at VD 27.2 m/s** (`requirements.vd_ms`, D-50); D6 horn 1 385 mm² | CR-C6-23 |
| Stacks withdrawn | — | `E-MEC-03/04` (servo in ear slots), `E-PWR-05` (bus board taped) | CR-A4-44, CR-D6-11 |
| Deviations | — | two granted by A1 (D-58), listed below | D-58 |
| Bought screw lengths | steel 8, 10, 16; PA66 16 | **steel 8, 16; PA66 16, 18** (M3x10 dropped with the PCB stack) | kit table |

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| How many fastener sizes? | **One bought thread, M3**: steel 8 and 16 mm, PA66 16 and 18 mm, one nyloc, one washer, one heat-set insert. M2 and 2-56 only as supplied mechanism hardware, M3x4 + M6 nut with the prop adapter (D-58) | kit table | `PROPOSED` |
| Fastened joints pass? | Yes. Motor screws 0.20 N·m on the canted plate: head RF 1.32, 3.5 mm engagement, separation RF 3.73 with the 7° side moment. Power frame at 0.08 N·m: engagement RF 1.22, install 1.35, tension 1.46, friction 1.24 | `CL-C6-MOTOR-*`, `CL-C6-CANT-ENGAGE`, `CL-C6-PWR-*` | `UNVERIFIED` |
| Station collar? | Passes at 12 mm with no margin: RF 1.00 on C1's 7.40 N·m + 205 N brace shear (C4's torsion alone gives RF 1.50). Back to 16 mm if the lap-shear coupons come in below 2.0 MPa design | `CL-C6-COLLAR-RF`, `-L-REQ`, `-RF-16MM` | `UNVERIFIED` (thin) |
| Fin bonds? | Tail 1.74, tail net section 1.57, brace ends 2.34, anchor 1.35, block bonds 5.0–5.7 pass. **Pins at 15 mm fail (0.92)** under C4's FE pin force with the conservative bending model; 12 mm pitch gives 1.15 | `CL-C6-STRIP-*`, `-BRACE-*`, `-TUBE-BLOCK-RF` | `FAIL` → CR-C6-25 |
| Foam bonds? | Foot shoe 1.54. Fin root 0.87 as drawn, 1.24 with the adopted 15 mm leg. Servo frame and horn ≥ 719 mm² each | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF(-PROP)`, `-LINK-BOND-AREA-MIN` | `FAIL` until D3 draws 15 mm |
| Pod joints? | Pod bond 1.15 / 1.29 crash, tray 2.59, hatch tab 1.18 (C3 at VD 27.2). Floor-to-wall glue line 0.90 bare, 2.03 with the 6 mm fillet that C3 now flies | `CL-C6-POD-*` | `UNVERIFIED` |

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
| Pultruded CF rod Ø 2 mm × 1 m | — | 2 | strip through-pins at 12 mm: 20 per pair × 4 half-fins = 80 × 11.6 mm ≈ 0.93 m | 2.0 mm drill |
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
| `E-FIN-13…16` | station collar on tube, **12 mm** | 829 | 16.0 N·m (C1 7.40 limit) + 205 N brace shear → 2.00 MPa | 2.0 MPa | **1.00** (16 mm: 1.34) | `CL-C6-COLLAR-RF`, `-L-REQ` 11.98 mm | `UNVERIFIED` (thin) |
| `E-FIN-29…36` | strip end in the two-face tail, 39.5 mm | 790 per strip | **908 N** per strip | 2.0 MPa; tail net 15 MPa on 95 mm² | 1.74; net 1.57 | `CL-C6-STRIP-ANCHOR-F`, `-ANCHOR-RF`, `-EMBED-REQ` 22.7 mm, `-TAIL-NET-RF` | `UNVERIFIED` |
| `E-FIN-21…28` | strip on board paper + Ø 2 mm CF pins through both layers (11.6 mm) | 2 290 | C4 FE 4.29 N/mm design; 64 N per pin at 15 mm | paper 0.10 MPa; pin 50 MPa shear / 400 MPa bending | paper alone 0.23; pins **0.92 → 1.15 at 12 mm** | `CL-C6-STRIP-FACE-RF`, `-PIN-RF`, `-PIN-RF-PROP` | `FAIL` → CR-C6-25 |
| `E-FIN-37…44` | brace ends in ear and anchor slots (10 mm) | 240 | 205 N | 2.0 MPa | 2.34 | `CL-C6-BRACE-END-RF` | `UNVERIFIED` |
| `E-FIN-57…60` | anchor saddle on spar, 90° contact | 276 | 205 N pull-off | 1.0 MPa | 1.35 | `CL-C6-ANCHOR-PULL-RF` | `UNVERIFIED` |
| `E-FIN-53…56` | half-fin root fillets on XPS | ≈ 6 300 | D3 L4 case μ 0.7: 5.59 N·m | 0.125 MPa | 12 mm **0.87**; **15 mm (D-48) 1.24**; needs 13.1 mm | `CL-C6-FIN-ROOT-RF`, `-RF-PROP` | `FAIL` until D3 draws 15 mm |
| `E-FIN-45…48` | ESC pad on board | 1 288 | 1.4 N (crash) | 0.10 MPa | > 90 | — | `PROPOSED` |
| `E-GER-01…04` | foot shoe on fin tip step | **1 350** | **87.4 N** | 0.10 MPa | **1.54** | `CL-C6-FOOT-SHOE-RF` (= `CL-D5-BOND-SF`) | `UNVERIFIED` |
| `E-POD-01` | pod shell on core | 10 014 | C3 envelope / 12.75 g crash | 0.125 / 0.10 MPa | 1.15 / 1.29 | `CL-C6-POD-WING-RF`, `-POD-CRASH-RF` | `UNVERIFIED` |
| `E-POD-02` | tray on floor, flat-wise under a strap | 13 505 | 19.3 kPa | 0.05 MPa | 2.59 | `CL-C6-POD-TRAY-RF` | `UNVERIFIED` |
| inside `POD-001` | floor-to-side-wall line under the front strap | 4.8 mm edge | 111 kPa | 0.10 MPa | 0.90 bare → **2.03 with the 6 mm fillet** | `CL-C6-POD-FLOOR-RF(-PROP)` | `UNVERIFIED` (C3 flies the fillet) |
| `E-POD-03` | hatch latch tab, hook-and-loop | tab per C3 | 2.11 N/cm² at VD 27.2 | 2.5 N/cm² | 1.18 | `CL-C6-POD-HATCH-RF` | `UNVERIFIED` |
| `E-POD-07` | pitot socket with a ≥ 30 × 30 mm flange | ≥ 900 | 0.8 N·m handling | 0.10 MPa | — | CR-C6-09 | `PROPOSED` |
| `E-MEC-01/02`, `11/12` | servo frame in core; horn in elevon | ≥ **719** each (D6 horn 1 385) | pushrod force at VD 27.2 | 0.125 MPa | — | `CL-C6-LINK-BOND-AREA-MIN` | `PROPOSED` (D6) |

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
| After a hard landing or tip-over | + coin-tap block region, collars, strip tails and pin rows; flex each fin tip 5 mm and listen; rock each motor by hand | no dull spot, no creak, no play |
| Every 10 flights | motor-screw and frame witness marks (PA66 creeps: re-snug the frame to 0.08 N·m); mast bolt; anchor bonds; pod spar ties; FC strap | marks unbroken, frame does not rock |
| Every bond batch | witness cup cured beside the part; batch and time on the build log | cup hard, not tacky |

## Tests — with the first prints (H1)

| Test | Coupon | Pass line | Replaces | Claims |
|---|---|---|---|---|
| `T-C6-LAP-PETG` | 5 PETG–CF and 5 ASA–CF single laps, 25 × 12.5 mm | mean × 0.5 ≥ 2.0 MPa; **below it the collar goes back to 16 mm** | `ASM-C4-BOND-SHEAR` | tube, spar, collar, brace, strip tail |
| `T-C6-BOARD-LAP` | 5 PETG tabs on board in shear + 5 flat-wise | mean × 0.5 ≥ 0.10 / 0.05 MPa | `ASM-D5-BOND-TAU`, `ASM-C6-BOARD-FLAT-TYP` | foot shoe, strip face, tray |
| `T-C6-XPS-PULL` | 5 pucks pulled + 5 pushed on F-250 | mean × 0.5 ≥ 0.125 / 0.10 MPa | `ASM-D3-XPS-TENSILE`, `ASM-C6-XPS-SHEAR-TYP` | fin root, pod bond, servo frames |
| `T-C6-BOARD-CORNER` | 2 board U-sections (bare, filleted) under a strap pull | ≥ 43 N per strap | — | pod floor glue line |
| `T-C6-INSERT` | 3 inserts in 7 mm bosses on a 0.8 mm plate **bonded to board** | ≥ 300 N each, or record the plate-peel load | `ASM-C6-INSERT-PULL` | power-frame inserts |
| `T-C6-NYLON-TORQUE` (new) | 5 PA66 M3x18 into inserts through the 12.5 mm stack | mean failure torque ≥ 0.16 N·m (3.2 N at 50 mm); 48 h at 0.08 N·m keeps ≥ 0.04 N·m breakaway | `ASM-C6-PA66-SIGMA` | power frame |
| `T-C6-HEAD-CREEP` | ASA plate on an Al block, 4 × M3x8 at 0.20 N·m, 2 h at 70 °C | breakaway ≥ 0.15 N·m | `ASM-C6-HEAD-BEARING` | motor head |
| `T-C6-CANT-SEAT` | first printed mount A with the motor | ≥ 6 turns to seat, 0.05 mm feeler does not enter | — | engagement on the canted plate |
| `T-C6-STRIP-ANCHOR` | 12 mm collar + 40 mm tail with a strip pair; pull **one** strip on H1's lever frame | **≥ 908 N** (`CL-C6-STRIP-ANCHOR-F`; the old 700 N text is void) | — | strip tail, tail net section |
| `T-C6-PROPNUT` | finished mount, 10 × 1.5 N·m | witness line unmoved | — | mount rock, hoop |

Each coupon set takes under an hour from shop stock. All ten run before the fin build starts.

## Findings

| # | Finding | Number | Action |
|---|---|---|---|
| 1 | Collar torsion settled on max(C1, C4) + brace shear; C1's section total governs and grew 6.60 → 7.40 N·m in C1's R4 re-run. The 12 mm collar passes with no margin | RF 1.00 (16 mm 1.34) | accept 12 mm; 16 mm fallback gated by `T-C6-LAP-PETG` |
| 2 | C4's FE pin force (64 N) is 24 % above the C6 hand estimate (52 N); with the pin reacted at the board mid-plane the 2 mm pin bends past 400 MPa | RF 0.92 → 1.15 at 12 mm (uniform foam bearing would give ≈ 1.7) | CR-C6-25 |
| 3 | F1's 0.20 N·m on a PA66 M3 puts ≈ 93 MPa von Mises in the shank (preload + torsion) | install RF 0.54 → 1.35 at 0.08 N·m | CR-C6-26 |
| 4 | The 50 N unplug moment (1.94 N·m design) reaches the floor through four bosses on a 0.8 mm plate bonded flat-wise at 0.05 MPa; a rigid pad would need ≈ 62 × 62 mm | not checkable without D2's plate stiffness | thumb-on-cradle rule; CR-C6-27; `T-C6-INSERT` on a bonded plate |
| 5 | D2's PDB-plate bosses are Ø 7.0 mm: 1.5 mm wall around the 4.0 mm bore | rule ≥ 1.6 mm | CR-C6-27 (Ø 7.2 mm) |
| 6 | D3 still draws the 12 mm root fillet adopted at 15 mm in D-48 | RF 0.87 → 1.24 | CR-C6-24 (open) |
| 7 | VD back to 27.2 m/s (D-50): servo-frame and horn bond area falls back | 1 002 → 719 mm² | CR-C6-23 closed |

## Open issues

1. Every allowable is `UNVERIFIED` until the coupons run; the thin RFs are the collar (1.00), the pins at 12 mm (1.15),
   the pod bond (1.15) and the hatch tab (1.18). Two claims fail as drawn (pins at 15 mm, root fillet 12 mm); the
   fixes are forwarded.
2. The tail net-section check uses D3's 95 mm² estimate and one strip's force; if C4's FE puts both strips of a pair in
   tension in the same case, the tail carries the sum (CR-C6-29).
3. Inputs moved during this revision (D3 collar 12 mm, C1 R4, C3); the values here are from the last `joints.py`
   run, which reads every input live.
4. Motor bolt pattern, hole depth and bell thread depth are measured on arrival (E1); the power-frame stack is
   measured by F1.
