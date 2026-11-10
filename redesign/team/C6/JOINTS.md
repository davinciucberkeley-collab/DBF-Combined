# Joints and fasteners — K09-L

Owner C6. Revision **C6-R2**, 2026-11-09, at params A1-R3, C1 envelope re-run at R3, C4 R3 fin model
(`CL-C4-D3-*`), fins D3-R3 (`subsystems/fins/params.json` 14:50), pod C3/D2, landing D5. Re-run in 1 s:
`python -I redesign/team/C6/joints.py`, `python -I redesign/team/C6/make_stacks.py`, then
`python -I redesign/proofs/build_graph.py`. Status: every joint stack is `PROPOSED`; every claim is `UNVERIFIED`
until the C6 coupons run with the first prints. Machine-readable blocks for the edge owners:
[`joint_stacks.json`](joint_stacks.json) (69 edges, `interfaces/SCHEMA.md` field names).

Check method: reserve factor RF = allowable / applied at the **design load** = C1 ultimate (1.5 × limit) × fitting
factor 1.15, × 1.25 more for anything printed or bonded (`ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR`).
RF ≥ 1.0 passes; the proof chain shows the margin RF − 1.

## What changed since C6-R1

| Item | R1 | R2 | Why |
|---|---|---|---|
| Station collar | 12 mm; RF 0.91 on C4's 9.3 N·m | **16 mm (D3 adopted)**; sized to 9.3 N·m **plus** the 209 N brace shear: 1.84 MPa, RF 1.09, needs 14.7 mm | A1 forward of CR-C6-03: size to the larger torsion until C1 and C4 agree |
| Strip tail | 20 mm, one face, RF 0.30 | **40 mm two-face tongue (D3 adopted)**, RF 1.76 (needs 22.7 mm) | strip force 908 N from C4's latest edge margin (`CL-C4-D3-MS-EDGE` 5.33; 1 348 N at R1) |
| Strip on paper | RF 0.20 bare | still RF 0.29 bare → **Ø 2 mm CF pins every 15 mm (D3 adopted)**, RF 1.15 through both layers (11.6 mm pin, bending governs) | two layers double the pin lever |
| Motor screws at 7° cant | not checked | plate canted as a whole, 4.5 mm under every head (D3 adopted): **3.5 mm engagement at every hole**; side force adds 0.15 N·m ult, separation RF 4.80 → 4.12 | D-27. R2's flat plate + canted pads would give 2.5 mm (< 3.0) and need a 7° screw lean the 3.4 mm hole cannot give (5.1° max) |
| Mount under the side force | — | tube torsion 0.070 N·m limit vs 2.5 N·m slip: RF 16.6; along the tube 2.2 N: RF 48 | D-27, CR-C4 forward row |
| Brace | 142 N (C4 R2, 10 × 2) | 167 N × 1.25 = 209 N (`CL-C4-D3-BRACE-F`, 10 × 3); anchor on the 90° saddle contact 276 mm² (C4 method): RF 1.32 | R3 brace; contact area corrected |
| Pod allowables | C3 assumed | **owned by C6** (CR-C3-05): two of C3's six are 2 × too high; floor glue line fails at C6's value → fillet | below |
| FC | M3 × 4 into inserts | **gel pads (F3, D-33)** + slack tie for the crash; inserts now only under the bus PDB | CR-F3-03 |
| GPS mast cross-bolt | A2-70 M3x16 | **PA66 M3x16 + PA66 nut** (non-magnetic) | CR-F3-03 |
| C1 loads | R2 | R3 envelope: fin Mz 6.77, My 6.74, half-fin Mz 7.39 N·m ult; avionics crash 10 N | `team/C1/data/envelope.json` |

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| How many fastener sizes? | **One thread, M3**, in three steel lengths (8, 10, 16 mm) and one nylon M3x16, plus one nyloc, one washer and one heat-set insert. M2 only as the servos' own screws; M3x4 and the M6 prop nut come with the prop adapter | kit table | `PROPOSED` |
| Fastened joints pass? | Yes. Motor screws at 0.20 N·m on the canted ASA plate: head RF 1.32, engagement 3.5 mm at every hole, separation RF 4.12 with the 7° side moment | `CL-C6-MOTOR-HEAD-RF`, `-CANT-ENGAGE`, `-MOTOR-SEP-RF` | `UNVERIFIED` |
| Station collar at C4's 9.3 N·m? | Passes at 16 mm: RF 1.09 (torsion + brace shear, C4's own method); C1's torsion gives RF 2.29 | `CL-C6-COLLAR-RF-C4`, `-COLLAR-L-REQ` 14.7 mm | `UNVERIFIED` (thin) |
| Fin bonds pass? | Yes with the R3 geometry: strip tail RF 1.76, pins RF 1.15, brace ends 2.30, anchor 1.32, block bonds 5.6–6.7 | `CL-C6-STRIP-*`, `-BRACE-*`, `-TUBE-BLOCK-RF` | `UNVERIFIED` |
| Pod joints at C6's allowables? | Pod bond RF 1.54 / 1.31 crash, tray 2.54, hatch tab 1.03 (thin). **Floor-to-wall glue line under the front strap fails: RF 0.90**; a 6 mm microballoon fillet gives 2.03 | `CL-C6-POD-*` | `FAIL` → CR-C6-17 |
| Foam bonds? | Foot shoe RF 1.35. **Fin root fillet fails at C6's XPS allowable: RF 0.87** (D3 now at μ 0.7, 0.21 m); a 15 mm fillet leg gives 1.24. Servo frame and horn need ≥ 1 002 mm² each at C1's current VD | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF`, `-LINK-BOND-AREA-MIN` | `FAIL` → CR-C6-24 |

## Rules: which fastening goes where

| Situation | Use | Engagement minimum (D-41) | Torque / locking | Never |
|---|---|---|---|---|
| Steel screw into metal (motor base, prop adapter into the bell) | SHCS A2-70, tapped hole | ≥ 1.0 d (3.0 mm); ≤ hole depth − 0.5 mm | per table; Loctite 243 on the **tip threads only** | threadlocker on or under a printed part: uncured anaerobic liquid stress-cracks ASA/ABS |
| Through a printed part, both sides reachable | SHCS + ISO 7089 washer + ISO 10511 nyloc | nut fully on + 2 pitches (5.0 mm past the grip for M3) | ≤ 0.4 N·m; nyloc reused ≤ 3 times | split washers; plain nuts |
| Into a printed part, one side or repeated service | M3 × 5.7 brass heat-set insert, hole Ø 4.0 × ≥ 6.5 mm blind, boss wall ≥ 1.6 mm, 230–245 °C | ≥ 1.5 d (4.5 mm) | ≤ 0.4 N·m, no threadlocker, paint-pen witness | screws straight into printed plastic |
| Screw on a canted face | holes drilled square to the face, head seat parallel to it (uniform grip) | as above | as above | holes normal to one face with the motor canted on pads |
| Within 50 mm of the compass | PA66 or brass hardware | nut fully on + 2 pitches | finger tight + ¼ turn | steel |
| Self-tapping into plastic | only the screws supplied with a servo; 1.6 mm pilot in a printed or ply boss | ≥ 2.0 d | snug, head seated | |
| Anything into XPS or foam board | **no screw**: bond a printed hardpoint ≥ 1 002 mm² (`CL-C6-LINK-BOND-AREA-MIN`) and fasten into it | — | — | screws, pins or inserts in foam |
| Field joints | tool-free (straps, plug-ins, snap hooks), except the prop nut | — | — | any tool other than the one 10 mm spanner (D-40) |

Torque without a torque screwdriver: hook a luggage scale on the long arm of the hex key 50 mm from the screw axis;
0.20 N·m = 4.0 N (0.41 kg), 0.4 N·m = 8.0 N.

## Fastener kit (bought; I1)

| Item | Standard | Qty (incl. spares) | Used at | Tool |
|---|---|---|---|---|
| M3x8 SHCS A2-70 | ISO 4762 | 20 | motor to mount (`PRP-005`, 16) | 2.5 mm hex |
| M3x10 SHCS A2-70 | ISO 4762 | 6 | bus PDB on inserts (4) | 2.5 mm hex |
| M3x16 SHCS A2-70 | ISO 4762 | 6 | mount pinch bolts (4, `FIN-101`) | 2.5 mm hex |
| M3x16 PA66 screw + PA66 hex nut | — | 3 + 3 | GPS mast cross-bolt (1) | 2.5 mm hex / fingers |
| M3 nyloc A2 | ISO 10511 | 8 | pinch bolts | 5.5 mm spanner |
| M3 washer A2 | ISO 7089 | 12 | pinch bolts (8) | — |
| M3 × 5.7 brass heat-set insert | Ruthex RX-M3x5.7 class | 12 | PDB (4), coupons `T-C6-INSERT` (3), spares | iron + insert tip |
| M3 nylon washer 0.8 mm + 2 mm nylon spacer | — | 6 + 6 | PDB | — |
| Pultruded CF rod Ø 2 mm × 1 m | — | 2 | strip through-pins: 18 per strip pair × 4 half-fins = 72 × ≈ 13 mm | 2.0 mm drill |
| Supplied, not bought | M3x4 × 4 + M6 nut + washer per adapter (`PRP-004`); servo M2 screws; gel pads (F3 `AVN-006`) | — | prop adapter, servos, FC | 2.5 mm hex, 10 mm spanner, Phillips #1 |

Tool set for the whole aircraft: 2.5 mm hex key, 5.5 and 10 mm spanners, Phillips #1, luggage scale.

## Fastened and retained joint stacks

Ids are the declared edges in `subsystems/*/interfaces.json`; `E-MEC`, `E-AVN-01`, `E-PWR-03`, `E-PRP` are A4 plan
ids. Order = install / removal within the owner's build.

| Interface | Parts | Fastener × n | Hole / insert | Engagement (min), mm | Washer / nut | Torque · locking | Design load · check | Status |
|---|---|---|---|---|---|---|---|---|
| `E-FIN-61…64` | `PRP-001-<st>` → `FIN-003-<st>` | M3x8 SHCS × 4 | Ø 3.4 drilled **square to the canted 4.5 mm plate** on the measured pattern; no slots | 3.5 (3.0); ≤ probed depth − 0.5 | none, head flat on the canted face | **0.20 N·m** + 243 on tip | 81 N per screw incl. 7° side moment; head RF 1.32, no-gap RF 4.12, strip RF 33 | `PROPOSED` |
| `E-FIN-05…08` | `FIN-003-<st>` → `FIN-002-<R/L>` | M3x16 SHCS × 1 | Ø 3.4 through both ears (grip 10.5) | 5.5 past grip (5.0) | 2 washers + nyloc | set by `T-D3-SLIP` (85–100 N at the can), ≈ 0.14 N·m, ≤ 0.4 | prop nut 3.23 N·m: bearing RF 3.26, hoop 5.94; 7° side: slip RF 16.6 / 48 | `PROPOSED` |
| `E-POD-06` | `POD-005` → `POD-007` | **M3x16 PA66** × 1 | Ø 3.4 across the boss | 16 − grip (4.0): grip ≤ 11.0 | PA66 nut | finger + ¼ turn | mast is the fuse; non-magnetic | `PROPOSED` (CR-C6-18) |
| `E-PWR-03` | bus PDB → `POD-002` | M3x10 SHCS × 4 | heat-set insert, hole 4.0 × 6.5 | 5.6 (4.5) | 2 mm nylon spacer + 0.8 mm nylon washer | 0.4 N·m, witness | 10 N crash: pull RF 20.9; engage RF 1.24 | `PROPOSED` (stack `UNVERIFIED`) |
| `E-AVN-01` | `AVN-001` → `POD-002` | **2 gel pads**, no screws (F3) | — | — | + one tie or 10 mm strap over the board, 1–2 mm slack | — | 10 N crash on the tie if the pads let go | `PROPOSED` (CR-C6-19) |
| `E-AVN-04` | airspeed board → `POD-002` | foam tape + 1 tie (D-33) | — | — | — | — | 6 g part | `PROPOSED` |
| `E-MEC-03/04` | `MEC-001-<L/R>` → `MEC-008-<L/R>` | servo M2 self-tapping × 2 | 1.6 mm pilot, printed ear boss ≥ 5 mm | 4.0 (4.0) | servo grommets | snug | — | `PROPOSED` |
| `E-PRP-01…04` | `PRP-004-<st>` → `PRP-001-<st>` | M3x4 × 4 (supplied) | bell tapped | E1 measures (3.0) | — | 0.5 N·m + 243 (maker wins) | — | `PROPOSED` |
| `E-PRP-05…08` field | `PRP-003-<st>` → `PRP-004-<st>` | M6 nut ISO 4032 (LH on CW motors) | prop on LPAR06E ring | nut fully on (5.2) | 1.0 mm washer | 1.5 N·m, bell held | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` |
| `E-TRN-13…15` ground | handle → box | M3x16 + 3 × 12 fender washers + nyloc (CR-C6-08, D7) | — | 5.0 | — | snug | 59 N per bolt | `PROPOSED` |

## Bonded joints

Adhesive: one 30 min laminating epoxy for everything. **Structural** (printed and CF parts): + ~5 % colloidal
silica, bond gap 0.1–0.3 mm. **Foam** fillets: + glass microballoons. Prep: PETG/ASA and CF 120 grit + IPA; paper
face 220 grit without tearing; foam dust-off only. Cure 24 h ≥ 18 °C; parts within 50 mm of a motor get 4 h at
50 °C post-cure (CR-C6-04, forwarded by A1 to E3/G2).

| Interface | Parts | Area, mm² | Design load | Allowable | RF | Claim | Status |
|---|---|---|---|---|---|---|---|
| `E-FIN-01/02` | tube in block bore (43 mm) | 2 972 | 9.7 N·m torsion | 2.0 MPa | 6.72 | `CL-C6-TUBE-BLOCK-RF` | `UNVERIFIED` |
| `E-FIN-49/50` | block on spar (36 mm) | 2 488 | 9.7 N·m torsion | 2.0 MPa | 5.65 | `CL-C6-BLOCK-SPAR-RF` | `UNVERIFIED` |
| `E-FIN-13…16` | station collar on tube, **16 mm** | 1 106 | 20.1 N·m (C4 9.3 limit) + 209 N brace shear → 1.84 MPa | 2.0 MPa | **1.09** (C1 torsion: 2.29; at 12 mm: 0.82) | `CL-C6-COLLAR-RF-C4`, `-L-REQ` 14.7 mm | `UNVERIFIED` |
| `E-FIN-29…36` | strip end in the **40 mm two-face tail** | 800 per strip | 908 N | 2.0 MPa | 1.76 (needs 22.7 mm) | `CL-C6-STRIP-ANCHOR-RF`, `-EMBED-REQ` | `UNVERIFIED` |
| `E-FIN-21…28` | strip on board paper + **Ø 2 mm CF pins every 15 mm** through both layers (11.6 mm) | 2 640 | 3.44 N/mm; 52 N per pin | paper 0.10 MPa; pin 50 MPa shear / 400 MPa bend | paper alone 0.29; pins **1.15** | `CL-C6-STRIP-FACE-RF`, `-PIN-RF` | `UNVERIFIED` |
| `E-FIN-37…44` | brace ends in ear and anchor slots (10 mm) | 260 | 209 N | 2.0 MPa | 2.30 | `CL-C6-BRACE-END-RF` | `UNVERIFIED` |
| `E-FIN-57…60` | anchor saddle on spar, 90° contact | 276 | 209 N pull-off | 1.0 MPa | 1.32 | `CL-C6-ANCHOR-PULL-RF` (= C4 +0.33) | `UNVERIFIED` |
| `E-FIN-53…56` | half-fin root fillets on XPS, 12 mm leg as drawn | ≈ 6 300 | D3 L4 case at μ 0.7: 5.59 N·m | 0.125 MPa | **0.87** → 1.24 with a 15 mm leg | `CL-C6-FIN-ROOT-RF` | `FAIL` → CR-C6-24 |
| `E-FIN-45…48` | ESC pad on board | 1 288 | 1.4 N (crash) | 0.10 MPa | > 90 | — | `PROPOSED` |
| `E-GER-01…04` | foot shoe on fin tip | 1 100 | 81 N | 0.10 MPa | 1.35 | `CL-C6-FOOT-SHOE-RF` | `UNVERIFIED` |
| `E-POD-01` | pod shell on core | 10 014 | C3 envelope / 12.75 g crash | 0.125 / 0.10 MPa | 1.54 / 1.31 | `CL-C6-POD-WING-RF`, `-POD-CRASH-RF` | `UNVERIFIED` |
| `E-POD-02` | tray on floor, flat-wise under a strap | 13 505 | 19.7 kPa | 0.05 MPa | 2.54 | `CL-C6-POD-TRAY-RF` | `UNVERIFIED` |
| inside `POD-001` | floor-to-side-wall glue line under the front strap | edge 4.8 mm wide | 111 kPa | 0.10 MPa | **0.90** → 2.03 with a 6 mm fillet | `CL-C6-POD-FLOOR-RF`, `-RF-PROP` | `FAIL` → CR-C6-17 |
| `E-POD-03` | hatch latch tab, hook-and-loop | 12 × 40 tab | 2.44 N/cm² at VD | 2.5 N/cm² | **1.03** | `CL-C6-POD-HATCH-RF` | `UNVERIFIED` (thin) |
| `E-POD-07` | pitot socket with a ≥ 30 × 30 mm flange | ≥ 900 | 0.8 N·m handling | 0.10 MPa | — | CR-C6-09 (forwarded) | `PROPOSED` |
| `E-MEC-01/02`, `11/12` | servo frame in core; horn in elevon | ≥ **1 002** each | 125 N pushrod at C1's VD 32.1 m/s | 0.125 MPa | — | `CL-C6-LINK-BOND-AREA-MIN` | `PROPOSED` (D6) |

## Pod allowables owned by C6 (CR-C3-05)

C6 design allowable = 0.5 × typical value (`ASM-C6-FOAM-KD`) until the coupons replace it.

| Allowable | C3 used | C6 design value | Basis | Verdict |
|---|---|---|---|---|
| Epoxy into XPS, tension | 100 kPa (`ASM-D2-XPS-ALLOW`) | 125 kPa | 0.5 × 0.25 MPa (`ASM-D3-XPS-TENSILE`) | **confirmed**, C3's is conservative (ratio 0.80, `CL-C6-POD-ALLOW-RATIO`) |
| Epoxy into XPS, shear | 100 kPa (`ASM-C3-XPS-SHEAR`) | 100 kPa | 0.5 × 0.20 MPa (`ASM-C6-XPS-SHEAR-TYP`) | **confirmed** |
| Foam board flat-wise (paper lifts) | 100 kPa (`ASM-C3-FB-FLAT`) | **50 kPa** | 0.5 × 0.10 MPa (`ASM-C6-BOARD-FLAT-TYP`) | **halved**; tray still RF 2.54 |
| Epoxy on paper face, shear | 200 kPa (`ASM-D5-BOND-TAU`) | **100 kPa** | 0.5 × 0.20 MPa | **halved**; floor glue line fails (RF 0.90) → fillet |
| Printed PETG across layers | 15 MPa (`ASM-C4-PETG-TENSILE`) | 15 MPa | 0.5 × Z yield 30 MPa; pod parts stay below 50 °C | **confirmed** |
| Hook-and-loop shear / tension | 5 / 2.5 N/cm² (`ASM-C3-HL`) | 5 / 2.5 N/cm² | 0.5 × catalogue class; sew-on tape | **confirmed**; hatch tab RF 1.03 is thin: any adhesive-backed tape on paper is limited by the paper (5 N/cm²), so this holds |

## Retention and field joints (no thread, no structural bond)

| Interface | Joint | Rule | Inspection |
|---|---|---|---|
| `E-GER-05…08` | foot piston snap hooks | free finger ≥ **6.0 mm** for 2 % strain (`CL-C6-SNAP-L-MIN`) | hooks seated: pre-flight |
| `E-FIN-65…68` | ESC strap through pad and board | strap never over the heat sink | strap tight: pre-flight |
| `E-AVN-01` | FC on gel pads | slack tie over the board for the crash | board does not lift with one finger |
| `E-POD-03`, `-05`, `-10` | hatch, pack straps, spacers | D2/C3 sized; 50 mm strap overlap | pre-flight card |
| `E-AVN-05` | pitot plug-in | keyed | seated: pre-flight |
| `E-MEC-07…10` | clevises | silicone keeper sleeve on every clevis | keeper on: pre-flight |

## Inspection

| When | What | Pass |
|---|---|---|
| Every flight | 4 mount witness lines; prop nuts; feet hooks; hinge tape ends; clevis keepers; fin roots | lines unbroken, nuts tight, nothing lifting |
| After a hard landing or tip-over | + coin-tap block region, collars, strip tails and pin rows; flex each fin tip 5 mm and listen; rock each motor by hand | no dull spot, no creak, no play |
| Every 10 flights | motor-screw witness marks; PDB and mast screws; anchor bonds; pod spar ties; FC pads | marks unbroken, ties tight |
| Every bond batch | witness cup cured beside the part; batch and time on the build log | cup hard, not tacky |

## Tests — with the first prints (H1, CR-C6-14)

| Test | Coupon | Pass line | Replaces | Claims |
|---|---|---|---|---|
| `T-C6-LAP-PETG` | 5 PETG–CF and 5 ASA–CF single laps, 25 × 12.5 mm | mean × 0.5 ≥ 2.0 MPa | `ASM-C4-BOND-SHEAR` | tube, spar, collar, brace, strip tail |
| `T-C6-BOARD-LAP` | 5 PETG tabs on board in shear + 5 flat-wise | mean × 0.5 ≥ 0.10 / 0.05 MPa | `ASM-D5-BOND-TAU`, `ASM-C6-BOARD-FLAT-TYP` | foot shoe, strip face, tray |
| `T-C6-XPS-PULL` | 5 pucks pulled + 5 pushed on F-250 | mean × 0.5 ≥ 0.125 / 0.10 MPa | `ASM-D3-XPS-TENSILE`, `ASM-C6-XPS-SHEAR-TYP` | fin root, pod bond, servo frames |
| `T-C6-BOARD-CORNER` | 2 board U-sections (bare, filleted) under a strap pull | ≥ 43 N per strap | — | pod floor glue line |
| `T-C6-INSERT` | 3 inserts in a printed boss | ≥ 300 N each | `ASM-C6-INSERT-PULL` | PDB inserts |
| `T-C6-HEAD-CREEP` | ASA plate on an Al block, 4 × M3x8 at 0.20 N·m, 2 h at 70 °C | breakaway ≥ 0.15 N·m | `ASM-C6-HEAD-BEARING` | motor head |
| `T-C6-CANT-SEAT` | first printed mount A with the motor | ≥ 6 turns to seat, 0.05 mm feeler does not enter | — | engagement at 7° |
| `T-C6-STRIP-ANCHOR` | 40 mm two-face tail with a strip pair | ≥ 908 N | — | strip tail |
| `T-C6-PROPNUT` | finished mount, 10 × 1.5 N·m | witness line unmoved | — | mount rock, hoop |

Each coupon set takes under an hour from shop stock. All nine run before the fin build starts.

## Findings

| # | Finding | Number | Action |
|---|---|---|---|
| 1 | Collar sized to the largest torsion on record: C1 4.93, C4 R3 3.46, C4 R2 9.3 N·m limit; at 16 mm the 9.3 case passes with the brace shear | RF 1.09 (12 mm: 0.82) | CR-C6-03 open with C1/C4 |
| 2 | Two board layers cut the strip force but double the pin lever; bending governs the pins | RF 1.15 | done (D3) |
| 3 | At 7° a flat plate on canted pads leaves 2.5 mm engagement and needs a 7° screw lean (hole allows 5.1°) | D3 canted the plate: 3.5 mm | done (D3) |
| 4 | Cant side force is 12 % of thrust: small at the mount (slip RF 16.6) and at the screws (+0.15 N·m ult) | separation RF 4.12 | C1 to add to J-MOTOR (CR-C6-21) |
| 5 | C3 used 2 × C6's value for the board flat-wise and paper-shear allowables; one pod glue line fails at C6's value | RF 0.90 | CR-C6-16, -17 |
| 6 | GPS mast bolt is steel near the compass | — | PA66, CR-C6-18 |
| 7 | Gel pads are not a crash retention | 10 N | slack tie, CR-C6-19 |
| 8 | Servo frame / horn bond area tracks C1's VD, which reads 32.1 m/s against params 27.2 | 720 → 1 002 mm² | CR-C6-21 |
| 9 | Root fillet at μ 0.7 and 0.21 m half-fins: D3's RF 1.74 uses the undiscounted XPS 0.25 MPa | RF 0.87; 15 mm leg 1.24 | CR-C6-24 |

## Open issues

1. Every allowable is `UNVERIFIED` until the coupons run; the thin RFs are the hatch tab (1.03), the collar (1.09)
   and the strip pins (1.15); the fin root fails until D3 takes the 15 mm leg.
5. C1, C4 and D3 re-ran during this revision; values here are those of the last `joints.py` run (15:0x).
2. The collar torsion is still not agreed between C1 and C4 (CR-C6-03).
3. `build_graph.py` stops on a NaN from C4's FE at the current fin inputs before it reaches the C6 checks
   (CR-C6-20). `joints.py` resolves every input from the current claims files, so the C6 values are current.
4. Motor bolt pattern, hole depth and bell thread depth are measured on arrival (E1); PDB stack measured by F1.
