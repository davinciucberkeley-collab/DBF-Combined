# Fins and motor tubes (FIN): SPEC

Owner D3 · structures C4 · aero B3/B4 · joints C6 · design R3 (CR-A1-28; D-26, D-27, D-28, D-42; CR-F2-05) · `MODELLED` ·
2026-11-09. Re-check: `python -I redesign/subsystems/fins/make_fins.py` → `python -I redesign/team/D3/fins_calcs.py`
→ `python -I redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py`.

## Purpose

Carry the four motors ±0.19 m above and below the wing on two vertical CF tubes through the wing core, give the
cruise fins (0.21 m half-fins), stand the aircraft on four square fin tips, and hold the ESCs in the slipstream.

## Fin-tube junction (P25) and load path

The tube is the fin LE. Each half-fin is a flat 9.6 mm laminate (two 4.8 mm boards) butting the tube. The block's
bore boss holds the root LE in a slot. At the top, the 16 mm station collar has a 40 mm tail: a tongue of board
thickness fills a notch in the laminate's LE-top corner, and each CF edge strip sits in a slot between the tongue and an
outer wall, so both strip faces bond to PETG. Nothing wraps the board around the tube.

| Path | Route |
|---|---|
| Motor loads | motor → 7° canted ASA plate → slit collar (friction, D-23 fuse) → tube → station collar → brace (axial) → anchor → spar |
| Tube root | tube → block bore 47 mm (CF plug inside) → spar bore (C2 plug inside the spar) → spar |
| Fin top edge | CF edge strips (Ø 2 mm CF pins every 15 mm) → collar tail (two faces, 39.5 mm) → tube |
| Fin root, feet | laminate → microballoon fillets and skin-tape laps → core; foot shoe on the square tip |
| ESC leads (F2) | tie lug on the boss tail (inboard) → Ø 8 mm grommeted hole 22 mm off the skin at x 0.086 → outboard face; phase leads tied to a lug on the collar tail (outboard) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fin plane / tube x / tube | ±0.320 / 0.045 / CF 22 × 20 × 344 | m, m, mm | `params.json#fins` | `PROPOSED` |
| Half-fin: layers / height / chord / square tip | 2 × 4.8 mm / 0.21 / 0.2635 / x 0.280–0.320 | —, m, m, m | `fins.layers`, `fin_detail.fin.tip_square_m` | `PROPOSED` |
| First station mode, separation (worst E/G) | 0.41 (0.33); brace 10 × 2: 0.39 | — | `CL-C4-D3-SEP`, `CL-C4-D3-SEP-WORST` | `UNVERIFIED` |
| Lower half-fin first mode / face margin | 281 Hz / +0.99 | — | `CL-C4-D3-F1-LO`, `CL-C4-D3-MS-FACE` | `UNVERIFIED` |
| Block MS / mount rocking stiffness required | +0.55 / ≥ 894 N·m/rad | — | `CL-C4-D3-BLOCK-MS`, `CL-C4-D3-MOUNT-K-REQ` | `UNVERIFIED` |
| Motor face x / prop plane x / prop gap ÷ 0.14 D | 0.0309 / −0.0082 / 1.02 | m, m, — | `CL-D3-X-FACE`, `CL-D3-X-PROP`, `CL-D3-PROP-GAP` | `CHECKED` |
| Motor screws: canted plate 4.5 mm, engagement at every hole | 3.5 (≥ 3.0) at 0.20 N·m | mm | `CL-D3-SCREW-ENGAGE` | `UNVERIFIED` |
| Collar height ÷ C6 required / tail embedment ÷ required | 1.09 / 1.74 | — | `CL-D3-COLLAR-H`, `CL-D3-TAIL-EMBED` | `UNVERIFIED` |
| Edge-strip pins: Ø / pitch / per half-fin | 2 / 15 / 12 | mm, mm, — | `fin_detail.edge_strip.pin_*`, `CL-C6-STRIP-PIN-RF` | `PROPOSED` |
| Brace 10 × 2: length upper / lower, P_cr ÷ design | 145 / 157 mm, 2.07 | — | `CL-D3-BRACE-L`, `CL-D3-BRACE-PCR` | `UNVERIFIED` |
| Mount slip torque / side force at the can / fuse ratio | 2.5 / 94 / 1.01 | N·m, N, — | `CL-D3-SLIP-F`, `CL-D3-SLIP-FUSE` | `UNVERIFIED` |
| Strap eye (each fin root) RF at 29.4 N | 9.8 | — | `CL-D3-STRAP-EYE-RF` | `UNVERIFIED` |
| Lead hole Ø 8 at x 0.086, 22 mm off the skin: least clearance to fillet/tape lap, boss, ESC pad | 2 (≥ 1) | mm | `CL-D3-WIRE-HOLE-CLEAR` | `CHECKED` |
| Square tip ÷ shoe / tip edge width | 1.08 / 9.6 | —, mm | `CL-D3-TIP-SQUARE`, `CL-D3-TIP-W` | `PROPOSED` |
| ESC pad outer edge ÷ slipstream radius / root fillet RF | 0.87 / 1.74 | — | `CL-D3-ESC-WASH`, `CL-D3-ROOT-FILLET-RF` | `UNVERIFIED` |
| Subsystem mass / allocation | 417.3 / 408 `EST` | g | `CL-D3-MASS` (CR-D3-16) | `FAIL` |

## Parts (42 nodes; mass = CAD volume × density, `make_fins.py`)

| Id | Part | Qty | Each g | Line g |
|---|---|---|---|---|
| `FIN-001-UR/UL/LR/LL` | Half-fin, two-layer laminate, notch + square tip, Ø 8 lead hole (lower: link slot) | 4 | 22.3 | 89.3 |
| `FIN-002-R/L` | Motor tube CF 22 × 20 × 344 | 2 | 35.1 | 70.2 |
| `FIN-003-<st>` | Motor mount ASA: slit collar, lip cap, 7° canted plate (A = UR/LL, B = UL/LR) | 4 | 11.0 | 44.0 |
| `FIN-004-R/L` | Through-core block PETG, bore bosses, 2 strap eyes, 2 tie lugs | 2 | 41.0 | 82.1 |
| `FIN-006-R/L` | Tube plug CF 20 × 18 × 53 | 2 | 5.5 | 10.9 |
| `FIN-007-<st>` | ESC pad ASA | 4 | 1.9 | 7.4 |
| `FIN-008-<st>` | Station collar PETG, 16 mm ring, 40 mm two-face tail, brace ear, tie lug | 4 | 10.7 | 42.6 |
| `FIN-009-<st>` | Brace, pultruded CF 10 × 2 | 4 | 5.2 | 20.6 |
| `FIN-010-<st>` | Brace anchor PETG on the spar | 4 | 3.2 | 12.7 |
| `FIN-011-<st><O/I>` | Edge strip, pultruded CF 10 × 1 × 229 | 8 | 4.2 | 33.2 |
| `FIN-012-<st>` | Pin set, 12 × CF rod Ø 2 × 11.6 | 4 | 1.1 | 4.3 |
| | **Total** (allocation 408 g) | 42 | | **417.3** (−9.3) |

Hardware and consumables are `FIN-101`…`FIN-107` in `parts.csv`. Parts plus hardware cost about $66.

## Interfaces

| With | Edges | How | State |
|---|---|---|---|
| wing (D1): spar `WNG-002`, core `WNG-001` | `E-FIN-49`…`60` | blocks threaded on the spar and bonded in core pockets; roots on bare foam with tape laps; anchors on the spar | declared; D1 to acknowledge (CR-D3-24) |
| propulsion (E1) | `E-FIN-61`…`68` | 4 × M3×8 drilled to the measured pattern, 0.20 N·m + Loctite 243; one 10 mm strap per ESC | acknowledged by E1; contact until E1 has a CAD module |
| landing (D5) | `E-GER-01`…`04` (acknowledged) | shoe on the square tip | declared |
| harness (F2) | `E-HRN-03/05` boss-tail ties, `E-HRN-06`…`09` collar ties (acknowledged) | 2.5 mm cable tie through a 3 × 1.5 mm lug slot; leads cross the fin in F2's grommet | declared; hole height moved to 22 mm (CR-D3-23) |
| internal | `E-FIN-01`…`48`, `69`…`80` | bonds (C6 blocks), slip clamps (M3×16 + nyloc) | declared |

## Open issues

1. Mass 417.3 g against 408 g: the R3 joint additions (collar and tail +19 g, pins +4 g, eyes +2 g, tie lugs +0.5 g)
   were not in C4's 402 g basis. CR-D3-16 to A1 (+10 g), with levers.
2. C4/C6 re-run on R3 geometry: 16 mm collar (1 106 mm² bond), tongue fill 0.45, canted-plate mount 11.0 g (CR-D3-17/18).
3. Motor pattern, base diameter and screw-hole depth are not published: drill the plate from the motor (E1, T-E1-MOTOR-RM).
4. D1 declared `WNG-001`/`002` (D1-R1): the 12 wing edges are now live; D1 has not acknowledged them yet (CR-D3-24).
5. F2 asked for the lead hole 10 mm off the skin; D3 put it at 22 mm to keep it out of the root joint (CR-D3-23).

## How to verify

T-D3-WEIGH, T-D3-SLIP, T-D3-ROOT, T-D3-EYE, lead-hole position on the dry fit, C4's T-C4-TAP-D3 and T-C4-MOUNT-STIFF, C6 coupons (collar, strip anchor,
pins), a Fusion interference check of the prop discs and the mount sliding past the collar tail, and `check.py` with
the wing and propulsion modules present.
