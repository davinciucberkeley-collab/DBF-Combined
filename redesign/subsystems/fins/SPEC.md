# Fins and motor tubes (FIN): SPEC

Owner D3 · structures C4 · aero B3/B4 · joints C6 · status `MODELLED` (design R2: braced fin per CR-C4-01/04) ·
2026-11-09. Re-check: `python -I redesign/subsystems/fins/make_fins.py` → `python -I redesign/team/D3/fins_calcs.py`
→ `python -I redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py`.

**Purpose.** Carry the four motors ±0.19 m above and below the wing on two vertical CF tubes through the wing core,
give the cruise fins, stand the aircraft on the fin TE tips, and hold the ESCs in the slipstream.

**Fin-tube junction (P25).** The tube is the fin leading edge. Each half-fin is one flat board whose LE butts the
tube. It is held at the root by the slotted bore boss of the through-core block and at the top by the station
collar (22.3 mm bore plus a board slot aft), with an epoxy fillet between them. Nothing wraps the board around the
tube, so the board stays flat.

**Load path.** Motor → mount (friction slip clamp, the D-23 fuse) → tube → station collar → CF brace → anchor → spar.
Tube → block bore (47 mm, CF plug inside) → spar bore → spar. Fin top edge → CF edge strips → station collar.
Fin root → microballoon fillets and skin-tape laps → core.

## Key numbers

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fin plane / tube axis x / tube | ±0.320 / 0.045 / CF 22 × 20 | m, m, mm | `params.json#fins` | `PROPOSED` |
| Tube length, ends at ±0.172 (params: 0.42) | 0.344 | m | `fin_detail.tube_length_m`, CR-D3-01 | `PROPOSED` |
| Half-fin LE x / TE x / tip height / board | 0.0565 / 0.320 / 0.19 / 1 × 4.8 mm | m | `fin_detail.layers`, CR-D3-02 | `PROPOSED` |
| First station mode, braced 1-layer fin (C4 model) | 296 Hz, separation 0.48 (worst E/G 0.43) | — | `CL-C4-F1-1LB`, `CL-C4-SEP-1LB` | `UNVERIFIED` |
| Brace CF 10 × 3: length upper / lower, anchor y | 145 / 157 mm, ±0.242 m | — | `CL-D3-BRACE-L` | `PROPOSED` |
| Brace vs C4 model: lateral stiffness / buckling / ear depth | 1.05 / 5.9 / 36.5 mm (C4 25) | — | `CL-D3-BRACE-KY`, `-PCR`, `-DZ` | `UNVERIFIED` (CR-D3-10) |
| Block 69 × 36 × 31 mm, bores 35 mm apart, web / tube bore | 12.7 / 47 | mm | `CL-C4-BLOCK-MS` +0.47 | `UNVERIFIED` |
| Motor face x (3° tangential cant) / prop plane x | 0.0309 / −0.0082 | m | `CL-D3-X-FACE`, `CL-D3-X-PROP` | `CHECKED` |
| Prop plane to nearest structure / B4 minimum 0.14 D | 40.0 / 39.1 | mm | `CL-D3-PROP-GAP` 1.02 | `CHECKED` |
| Motor-screw engagement, worst hole, M3x8 | 3.07 (≥ 3.0) | mm | `CL-D3-SCREW-ENGAGE` | `UNVERIFIED` (hole depth) |
| Mount slip torque / side force at the can | 2.5 / 94 | N·m / N | `CL-D3-SLIP-F` | `UNVERIFIED` (T-D3-SLIP) |
| Fuse ratio (joint design ÷ root moment at slip) · hold ratio | 1.14 · 2.05 | — | `CL-D3-SLIP-FUSE`, `-HOLD` | `UNVERIFIED` |
| ESC pad radius from the motor axis / 0.71 R | 58–86 / 99 | mm | `CL-D3-ESC-WASH` 0.87 | `PROPOSED` |
| Root fillet reserve factor (L4 side load, 50 % share) | 2.25 | — | `CL-D3-ROOT-FILLET-RF` | `UNVERIFIED` |
| Link slot in the lower half-fin root (CR-A4-04) | x 0.2376–0.2616, 12 mm deep | m | `fin_detail.link_slot` | `PROPOSED` |

## Parts (38 nodes; mass = CAD volume × density, `make_fins.py`)

| Id | Part | Qty | Each g | Line g |
|---|---|---|---|---|
| FIN-001-RU/RD/LU/LD | Half-fin, one board, incl. 3 g root joint | 4 | 11.7 | 46.7 |
| FIN-002-R/L | Motor tube CF 22 × 20 × 344 | 2 | 35.1 | 70.2 |
| FIN-003-UR/UL/LR/LL | Motor mount PETG: slit collar, lip cap, canted pads (print A = UR/LL, B = UL/LR) | 4 | 11.3 | 45.1 |
| FIN-004-R/L | Through-core block PETG with keyhole bore bosses | 2 | 40.1 | 80.3 |
| FIN-006-R/L | Tube plug CF 20 × 18 × 53 | 2 | 5.5 | 10.9 |
| FIN-007-<st> | ESC pad PETG | 4 | 2.2 | 8.6 |
| FIN-008-<st> | Station collar PETG (board top, strip sockets, brace ear) | 4 | 5.7 | 22.9 |
| FIN-009-<st> | Brace, pultruded CF strip 10 × 3 | 4 | 7.4 | 29.7 |
| FIN-010-<st> | Brace anchor PETG, on the spar | 4 | 3.2 | 12.7 |
| FIN-011-<half><O/I> | Edge strip, pultruded CF 10 × 1 | 8 | 4.7 | 37.4 |
| | **Total** (allocation 370 g) | 38 | | **364.5** (+5.5 spare) |

FIN-005 is retired (the root clips became the block bosses). Hardware and consumables are FIN-101…106 in
`parts.csv`. Parts plus hardware cost about $62.

## Interfaces

| With | Edges | How | State |
|---|---|---|---|
| wing (D1): spar WNG-002, core WNG-001 | E-FIN-49…60 | blocks threaded on the spar and bonded in a full-depth core pocket; roots on bare foam with skin-tape laps; anchors on the spar through 20 × 16 mm pockets | pending: WNG ids not declared |
| propulsion (E1): motors, ESCs | E-FIN-61…68 | 4 × M3x8 into the motor base on canted pads; ESC on a hook-and-loop strap through the pad | pending: PRP ids not declared |
| landing (D5) | E-GER-01…04 (acknowledged) | shoe bonded on the half-fin TE tip | D5 points at `FIN-001-UR…`: CR-D3-08 |
| internal | E-FIN-01…48 | bonds; slip clamps (M3x16 + nyloc stack) | declared |

## Open issues

1. One board layer and the 0.344 m tube are proposals (CR-D3-01/02). With two layers the subsystem is about 400 g.
2. C4's modes assume the brace ear 25 mm below the motor axis and the anchor at y 0.20. Here they are 36.5 mm and
   y 0.242 (clear of D7's cradles), with a stiffer 10 × 3 strip. C4 re-runs (CR-D3-10).
3. Motor bolt pattern, base diameter and screw-hole depth are not published: drill the plate from the motor (E1).
4. The cant sense per station waits for F4's spin map (CR-D3-07). Swapping prints A and B reverses it.
5. `check.py` reports the right fin as floating until D1 declares WNG-001/002. Then re-run `make_fins.py`.

## How to verify

T-D3-WEIGH (every part), T-D3-SLIP (collar turns at 85–100 N), T-D3-ROOT (side pull at the tip), C4's T-C4-TAP
(station modes) and T-C4-BLOCK-PROOF, a Fusion interference check of the prop discs, and `check.py` with the wing
and propulsion modules present.
