# Joints and fasteners — K09-L

Owner C6. Revision C6-R1, 2026-11-09, at params A1-R2, C1-R2 loads, fins D3-R2, pod D2, landing D5. Re-run in 1 s:
`python -I redesign/team/C6/joints.py`, `python -I redesign/team/C6/make_stacks.py`, then
`python -I redesign/proofs/build_graph.py` (0 C6 errors; other roles' drift still fails the build).
Status: every joint stack below is `PROPOSED`; the calculations re-run, but every claim is `UNVERIFIED` because the
bond and plastic allowables are guesses until the C6 coupons run. Machine-readable blocks for the edge owners:
[`joint_stacks.json`](joint_stacks.json) (67 edges, `interfaces/SCHEMA.md` field names).

Check method: reserve factor RF = allowable / applied at the **design load** = C1 ultimate (1.5 × limit) × fitting
factor 1.15, × 1.25 more for anything printed or bonded (`ASM-C1-FITTING-FACTOR`, `ASM-C1-PRINTED-FACTOR`).
RF ≥ 1.0 passes; the proof chain shows the margin RF − 1.

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| How many fastener sizes? | **One bought thread, M3**, in three lengths (8, 10, 16 mm), plus one nyloc, one washer and one heat-set insert. M2 only as the servos' own screws; M3x4 and the M6 prop nut come in the prop-adapter set | kit table below | `PROPOSED` |
| Fastened joints pass? | Yes, after one change: the motor screws at **0.20 N·m**, not 0.5 N·m. At 0.5 N·m the screw head crushes the printed plate (57 MPa, RF 0.53) | `CL-C6-MOTOR-HEAD-RF` 1.32 | `UNVERIFIED` |
| Mount clamp vs the prop-nut torque (CR-C1-11)? | Holds: 3.23 N·m design gives 6.1 MPa bearing on the collar, RF 3.26; tube hoop RF 5.94 | `CL-C6-MOUNT-ROCK-RF` | `UNVERIFIED` |
| Fin bonds pass? | **Two fail as drawn.** (1) Edge-strip ends in the collar: 1 348 N on 200 mm², RF 0.30. (2) Strip-to-board shear flow on the paper face: 0.51 MPa, RF 0.20. Fixes: 40 mm two-face collar tail (RF 1.19) and 2 mm CF through-pins every 15 mm (RF 1.41) | `CL-C6-STRIP-ANCHOR-RF`, `CL-C6-STRIP-FACE-RF` | `FAIL` → CR-C6-01, -02 |
| Station collar bond? | RF 1.60 on C1's half-fin torsion; RF 0.91 on C4's 9.3 N·m. Collar 12 → 16 mm covers both | `CL-C6-COLLAR-RF`, `CL-C6-COLLAR-L-REQ` 13.2 mm | `FAIL` (C4 basis) → CR-C6-03 |
| Bonds into foam and board? | Pass at C6's halved allowables (XPS 0.125 MPa, paper face 0.10 MPa): foot shoe RF 1.35, fin root 1.12, pod 2.09 | `CL-C6-FOOT-SHOE-RF`, `-FIN-ROOT-RF`, `-POD-WING-RF` | `UNVERIFIED` (coupons) |

## Rules: which fastening goes where

| Situation | Use | Engagement minimum | Torque / locking | Never |
|---|---|---|---|---|
| Steel screw into metal (motor base, prop adapter into the bell) | SHCS A2-70, tapped hole | ≥ 1.0 d (3.0 mm); ≤ hole depth − 0.5 mm | per table; Loctite 243 on the **tip threads only** | threadlocker on or under a printed part: uncured anaerobic liquid stress-cracks ASA/ABS |
| Through a printed part, both sides reachable | SHCS + ISO 7089 washer + ISO 10511 nyloc | nut fully on + 2 pitches (5.0 mm past the grip for M3) | ≤ 0.4 N·m; nyloc reused ≤ 3 times | split washers; plain nuts |
| Into a printed part, one side or repeated service | M3 × 5.7 brass heat-set insert, hole Ø 4.0 × ≥ 6.5 mm blind, boss wall ≥ 1.6 mm, 230–245 °C | ≥ 1.5 d (4.5 mm) | ≤ 0.4 N·m, no threadlocker, paint-pen witness | screws straight into printed plastic |
| Self-tapping into plastic | only the screws supplied with a servo; 1.6 mm pilot in a printed or ply boss | ≥ 2.0 d | snug, head seated | |
| Anything into XPS or foam board | **no screw**: bond a printed hardpoint ≥ 720 mm² (`CL-C6-LINK-BOND-AREA-MIN`, 90 N design) and fasten into it | — | — | screws, pins or inserts in foam |
| Field joints | tool-free (straps, plug-ins, snap hooks), except the prop nut | — | — | anything needing a key at the field other than one 10 mm spanner (CR-C6-05) |

This replaces the single `requirements.thread_engagement_min` 1.0 d (CR-C6-06). Torque without a torque
screwdriver: hook a luggage scale on the long arm of the hex key 50 mm from the screw axis; 0.20 N·m = 4.0 N
(0.41 kg), 0.4 N·m = 8.0 N.

## Fastener kit (bought; I1)

| Item | Standard | Qty (incl. spares) | Used at | Tool |
|---|---|---|---|---|
| M3x8 SHCS A2-70 | ISO 4762 | 20 | motor to mount (`PRP-005`, 16) | 2.5 mm hex |
| M3x10 SHCS A2-70 | ISO 4762 | 10 | FC on inserts (4), PDB if a PCB (4) | 2.5 mm hex |
| M3x16 SHCS A2-70 | ISO 4762 | 8 | mount pinch bolts (4, `FIN-101`), GPS mast (1) | 2.5 mm hex |
| M3 nyloc A2 | ISO 10511 | 10 | pinch bolts, GPS mast | 5.5 mm spanner |
| M3 washer A2 | ISO 7089 | 15 | pinch bolts (8), GPS mast (1) | — |
| M3 × 5.7 brass heat-set insert | Ruthex RX-M3x5.7 class | 12 | `POD-002` FC plate (4), PDB (4) | iron + insert tip |
| M3 nylon washer 0.8 mm + soft-mount grommets | — | 8 | FC | — |
| Pultruded CF rod Ø 2 mm × 1 m | — | 1 | strip through-pins (CR-C6-02) | 2.0 mm drill |
| Supplied, not bought | M3x4 × 4 + M6 nut + washer per adapter (`PRP-004`); servo M2 screws | — | prop adapter, servos | 2.5 mm hex, 10 mm spanner, Phillips #1 |

Hex key 2.5 mm, spanners 5.5 and 10 mm, Phillips #1, luggage scale: the whole aircraft tool set.

## Fastened joint stacks

Ids are the declared edges in `subsystems/*/interfaces.json`; `E-MEC`, `E-AVN-01/04`, `E-PWR-03`, `E-PRP` are
A4 plan ids (not yet declared). Order = install / removal within the owner's build.

| Interface | Parts | Fastener × n | Hole / insert | Engagement (min), mm | Washer / nut | Torque · locking | Tool · access | Order | Check | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `E-FIN-61…64` | `PRP-001-<st>` → `FIN-003-<st>` | M3x8 SHCS × 4 | 3.4 mm through plate + pads (4.1–4.9 mm); **drilled to the measured pattern, no radial slots** | 3.07 (3.0); max = probed depth − 0.5 | none | **0.20 N·m** + 243 on tip | 2.5 hex, from behind the plate above the tube end | 3 / 1 | head RF 1.32, no-gap RF 4.80, strip RF 33 | `PROPOSED` |
| `E-FIN-05…08` | `FIN-003-<st>` → `FIN-002-<R/L>` | M3x16 SHCS × 1 | 3.4 mm through both ears (grip 10.5) | 5.5 past grip (5.0) | 2 washers + nyloc | set by `T-D3-SLIP` (85–100 N at the can), ≈ 0.14 N·m, ≤ 0.4 | 2.5 hex + 5.5 spanner, outboard | 4 / 2 | `CL-C6-PINCH-*`, rock RF 3.26 | `PROPOSED` |
| `E-POD-06` | `POD-005` → `POD-007` | M3x16 SHCS × 1 | 3.4 mm across the boss | 16 − grip − 0.5 (5.0): **grip ≤ 10.5 mm** | 1 washer + nyloc | snug ≤ 0.3 N·m | 2.5 hex + 5.5 spanner, +y | 7 / 1 | D2 measures grip | `PROPOSED` |
| `E-AVN-01` | `AVN-001` → `POD-002` | M3x10 SHCS × 4 | heat-set insert, hole 4.0 × 6.5 | 5.6 (4.5) | nylon washer, grommets | 0.4 N·m, witness | 2.5 hex, from above | 2 / 3 | `CL-C6-FC-ENGAGE-RF` 1.24, pull RF 22 | `PROPOSED` (stack 4.4 mm `UNVERIFIED`) |
| `E-PWR-03` | `PWR-004` → `POD-002` | M3x10 SHCS × 4 (if PCB) | heat-set insert | 4.6 (4.5) | 3 mm nylon spacer + nylon washer | 0.4 N·m | 2.5 hex, from above | 1 / 4 | — | `PROPOSED` |
| `E-AVN-04` | `AVN-004` → `POD-002` | **none: foam tape + 1 tie** (drops M2) | — | — | — | — | — | — | 6 g part | `PROPOSED` (CR-C6-07) |
| `E-MEC-03/04` | `MEC-001-<L/R>` → `MEC-008-<L/R>` | servo M2 self-tapping × 2 | 1.6 mm pilot, printed ear boss ≥ 5 mm | 4.0 (4.0) | servo grommets | snug | Phillips #1, cover off | 2 / 1 | — | `PROPOSED` |
| `E-PRP-01…04` | `PRP-004-<st>` → `PRP-001-<st>` | M3x4 × 4 (supplied) | bell tapped | E1 measures (3.0) | — | 0.5 N·m + 243 (maker wins) | 2.5 hex, front | 1 / 9 | `UNVERIFIED` | `PROPOSED` |
| `E-PRP-05…08` field | `PRP-003-<st>` → `PRP-004-<st>` | M6 nut ISO 4032 (LH on CW motors) | prop on LPAR06E ring | nut fully on, 5.2 (E1: 0.1 mm past) | 1.0 mm washer | 1.5 N·m, bell held by hand | 10 mm spanner, front | 2 / 1 | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` |
| `E-TRN-13…15` ground | handle → box | M5x16 now; propose M3x16 + 3 × 12 fender washers + nyloc | — | 5.0 | — | snug | 2.5 hex | — | 59 N per bolt | `PROPOSED` (CR-C6-08) |

## Bonded joints

Adhesive: one 30 min laminating epoxy for everything. **Structural** (printed and CF parts): + ~5 % colloidal
silica, bond gap 0.1–0.3 mm (D3's 0.15 mm in every 22.3 mm bore is right). **Foam** fillets: + glass
microballoons. Prep: PETG/ASA and CF 120 grit + IPA; paper face 220 grit without tearing; foam dust-off only.
Cure 24 h ≥ 18 °C before load; parts within 50 mm of a motor get 4 h at 50 °C post-cure (CR-C6-04). Allowables:
epoxy on abraded PETG/CF 2.0 MPa shear (`ASM-C4-BOND-SHEAR`), 1.0 MPa peel (`ASM-C6-PEEL`); into XPS 0.125 MPa;
onto paper-faced board 0.10 MPa (0.5 × the typical value, `ASM-C6-FOAM-KD`).

| Interface | Parts | Area, mm² | Design load | Allowable | RF | Claim | Status |
|---|---|---|---|---|---|---|---|
| `E-FIN-01/02` | tube in block bore (43 mm) | 2 972 | 10.4 N·m torsion | 2.0 MPa | 6.26 | `CL-C6-TUBE-BLOCK-RF` | `UNVERIFIED` |
| `E-FIN-49/50` | block on spar (36 mm) | 2 488 | 9.7 N·m torsion | 2.0 MPa | 5.67 | `CL-C6-BLOCK-SPAR-RF` | `UNVERIFIED` |
| `E-FIN-51/52` | block in core pocket | ≈ 6 500 | secondary (spar carries the block) | 0.125 MPa | — | C4 | `PROPOSED` |
| `E-FIN-03/04` | CF plug in tube | 3 330 | bearing doubler | — | — | C4 | `PROPOSED` |
| `E-FIN-13…16` | station collar on tube (12 mm) | 829 | 11.4 N·m (C1) / 20.1 N·m (C4) | 2.0 MPa | 1.60 / **0.91** | `CL-C6-COLLAR-RF`, `-COLLAR-L-REQ` 13.2 mm | `FAIL` (C4) |
| `E-FIN-29…36` | strip end in collar tail, as drawn: 20 mm, outer face only | 200 | 1 348 N | 2.0 MPa | **0.30** | `CL-C6-STRIP-ANCHOR-RF` | `FAIL` |
| same, CR-C6-01 | 40 mm tail, PETG tongue between the strips | 800 | 1 348 N | 2.0 MPa | 1.19 | `CL-C6-STRIP-ANCHOR-RF-PROP` | `PROPOSED` |
| `E-FIN-21…28` | strip on board paper face | 2 640 | 5.1 N/mm → 0.51 MPa | 0.10 MPa | **0.20** | `CL-C6-STRIP-FACE-RF` | `FAIL` |
| same, CR-C6-02 | + Ø 2 mm CF pins every 15 mm (18 per pair) | — | 77 N per pin | shear 50 / bend 400 MPa | 1.41 | `CL-C6-STRIP-PIN-RF` | `PROPOSED` |
| `E-FIN-37…44` | brace ends in ear and anchor slots (10 mm) | 260 | 178 N | 2.0 MPa | 2.93 | `CL-C6-BRACE-END-RF` | `UNVERIFIED` |
| `E-FIN-57…60` | anchor on spar (≤ 20 × 16 mm) | ≤ 320 | 178 N pull-off | 1.0 MPa | 1.80 | `CL-C6-ANCHOR-PULL-RF` | `UNVERIFIED` |
| `E-FIN-53…56` | half-fin root fillets on XPS | ≈ 6 300 | D3 L4 case | 0.125 MPa | 1.12 | `CL-C6-FIN-ROOT-RF` | `UNVERIFIED` |
| `E-FIN-09…12`, `17…20` | board in boss / collar slots | 288 / 480 | part of root / strip paths | 0.10 MPa | — | covered above | `PROPOSED` |
| `E-FIN-45…48` | ESC pad on board | 1 288 | 1.4 N (crash) | 0.10 MPa | > 90 | — | `PROPOSED` |
| `E-GER-01…04` | foot shoe on fin tip | 1 100 | 81 N | 0.10 MPa | 1.35 | `CL-C6-FOOT-SHOE-RF` | `UNVERIFIED` |
| `E-POD-01` | pod shell on core | 10 014 | 175 N + 5.0 N·m | 0.125 MPa | 2.09 | `CL-C6-POD-WING-RF` | `UNVERIFIED` |
| `E-POD-02` | tray on floor | 13 505 | 85 N crash | 0.10 MPa | > 15 | — | `PROPOSED` |
| `E-POD-09` | handle feet on spar + 2 ties | 680 | 111 N | 2.0 MPa | 12 | — | `PROPOSED` |
| `E-POD-07` | pitot socket in a 14 mm hole | 230 | 0.8 N·m handling | — | — | needs a flange (CR-C6-09) | `PROPOSED` |
| `E-MEC-01/02`, `E-MEC-11/12` | servo frame in core; horn in elevon | ≥ 720 each | 90 N pushrod at VD | 0.125 MPa | — | `CL-C6-LINK-BOND-AREA-MIN` | `PROPOSED` (D6) |
| `E-MEC-13…16` | inter-panel link rod in panels | ≥ 30 mm groove each end + glass tape | — | — | — | D6 | `PROPOSED` |
| `E-WNG-01` | spar in slot | ≈ 69 000 | C2 | 0.125 MPa | — | C2 | `PROPOSED` |

## Retention and field joints (no thread, no structural bond)

| Interface | Joint | Rule | Inspection |
|---|---|---|---|
| `E-GER-05…08` | foot piston snap hooks | free finger ≥ **6.0 mm** for 2 % strain at 0.6 mm hook, 0.8 mm wall (`CL-C6-SNAP-L-MIN`); load path is compression on the back wall, hooks carry only < 1 N | hooks seated: pre-flight |
| `E-FIN-65…68` | ESC strap through pad and board | strap never over the heat sink | strap tight: pre-flight |
| `E-POD-03`, `-05`, `-10` | hatch, pack straps, spacers | D2/C3 sized | pre-flight card |
| `E-AVN-05` | pitot plug-in | keyed (OI-12) | seated: pre-flight |
| `E-WNG-04…07` | hinge tape | top-surface tape, full span | no peel at ends: pre-flight |
| `E-MEC-07…10` | clevises | positive retention: silicone keeper sleeve on every clevis | keeper on: pre-flight |

## Inspection

| When | What | Pass |
|---|---|---|
| Every flight | 4 mount witness lines; prop nuts; feet hooks; hinge tape ends; clevis keepers; fin roots | lines unbroken, nuts tight, nothing lifting |
| After a hard landing or tip-over | + coin-tap block region, collars, strip tails; flex each fin tip 5 mm and listen; rock each motor by hand | no dull spot, no creak, no play |
| Every 10 flights | motor-screw witness marks; FC and mast screws; anchor bonds; pod spar ties | marks unbroken, ties tight |
| Every bond batch | witness cup cured beside the part; batch and time on the build log | cup hard, not tacky |

## Findings

| # | Finding | Number | Action |
|---|---|---|---|
| 1 | 0.5 N·m on the motor screws puts 57 MPa under an M3 head on a printed plate (66 °C); radial slots would cut the bearing area by 4× | RF 0.53 → 1.32 at 0.20 N·m | CR-C6-10 to E1, D3 |
| 2 | Edge strips cannot be anchored by 20 mm of one-face bond in the collar | 1 348 N, RF 0.30 | CR-C6-01 to D3 |
| 3 | Strips bonded only to paper faces: the paper-to-core interface carries the flange shear flow | 0.51 vs 0.10 MPa | CR-C6-02 to C4, D3 |
| 4 | Collar torsion differs between C1 (5.3 N·m limit) and C4 (9.3 N·m limit) | RF 1.60 vs 0.91 | CR-C6-03 to C4, C1, D3 |
| 5 | 30 min hobby epoxy Tg is about 50–60 °C; the motor base runs at 66 °C (E3) | — | CR-C6-04 to E3 |
| 6 | "No tools" field set-up conflicts with an M6 prop nut | 10 mm spanner | CR-C6-05 to A1, A2 |
| 7 | D3/D2 joint stacks give nyloc "engagement 4.0, min 3.0": the rule is bolt end ≥ 2 pitches past a 4.0 mm nyloc | 5.0 mm past the grip | `joint_stacks.json` |
| 8 | Prop-nut torque reaches the mount only if the fin is held; still checked | RF 3.26 | CR-C1-11 closed |

## Tests (planned, `claims.json`)

`T-C6-LAP-PETG` (epoxy on PETG and CF), `T-C6-BOARD-LAP` (epoxy on paper face), `T-C6-XPS-PULL` (puck on XPS),
`T-C6-INSERT` (pull-out ≥ 300 N), `T-C6-HEAD-CREEP` (motor screws, 2 h at 70 °C), `T-C6-STRIP-ANCHOR`
(≥ 1 350 N), `T-C6-PROPNUT` (10 × 1.5 N·m). Each coupon set costs < 1 h and shop stock. Allowable = 0.5 × mean.

## Open issues

1. Every allowable is `UNVERIFIED` until the coupons run; the thin RFs are the root fillet (1.12), the strip tail
   (1.19) and the motor head (1.32).
2. C4 re-runs the fin with D3's 10 × 3 brace (CR-D3-10); the brace force 142 N here is C4's 10 × 2 model.
3. Motor bolt pattern, hole depth and bell thread depth are measured on arrival (E1).
4. FC board and grommet stack (4.4 mm) are `UNVERIFIED` until F3 picks the board.
5. Wing, mechanisms, avionics, power and propulsion `interfaces.json` are not declared yet; their stacks here use
   A4's plan ids.
