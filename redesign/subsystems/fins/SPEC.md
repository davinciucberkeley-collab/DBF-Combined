# Fins and motor tubes (FIN): SPEC

Owner D3 · structures C4 · aero B3/B4 · joints C6 · design R4 (CR-A1-47; D-26, D-27, D-42, D-48, D-51, D-52, D-54;
CR-F2-05) · `MODELLED` · 2026-11-09. Re-check: `python -I redesign/subsystems/fins/make_fins.py` →
`python -I redesign/team/D3/fins_calcs.py` → `python -I redesign/fusion/check.py` →
`python -I redesign/interfaces/merge_check.py`.

## Purpose

Carry the four motors ±0.19 m above and below the wing on two vertical CF tubes through the wing core, give the
cruise fins (0.21 m half-fins), stand the aircraft on four stepped fin tips, and hold the ESCs in the slipstream.

## Fin-tube junction (P25) and load path

The tube is the fin LE. Each half-fin is a flat 9.6 mm laminate (two 4.8 mm boards) butting the tube. The block's
bore boss holds the root LE in a slot. At the top, the 12 mm station collar has a 40 mm tail: a tongue of board
thickness fills a notch in the laminate's LE-top corner (tongue 11.3 mm, 0.7 mm under the ring), and each CF edge
strip sits in a slot between the tongue and an outer wall, so both strip faces bond to PETG. Nothing wraps the board
around the tube.

| Path | Route |
|---|---|
| Motor loads | motor → 7° canted ASA plate (D-52 sense) → slit collar (friction, D-23 fuse) → tube → station collar → brace (axial) → anchor → spar |
| Tube root | tube → block bore 47 mm (CF plug inside) → spar bore (C2 plug inside the spar) → spar |
| Fin top edge | CF edge strips (Ø 2 mm CF pins every 15 mm) → collar tail (two faces, 39.5 mm) → tube |
| Fin root, feet | laminate → cove fillets (15 mm on the last 0.15 m of bonded root, 13 mm aft of the hinge, 6 mm bead ahead, none over the D6 slot) and tape laps → core; D5 shoe on the stepped tip |
| Heat (E3) | motor → own wash (mount not credited, `E-FIN-81…84`); ESC FET face → wash, pad side adiabatic (`E-FIN-85…88`) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fin plane / tube x / tube | ±0.320 / 0.045 / CF 22 × 20 × 344 | m, m, mm | `params.json#fins` | `PROPOSED` |
| Half-fin tip: step front x / step \|z\| / D5 mismatch | 0.2746 / 0.2005 / 0 | m, m, m | `CL-D3-TIP-SQUARE`, `CL-D3-TIP-STEP-MISMATCH` | `CHECKED` |
| Cant sense UR (prop end toward the wing, outboard) | −1 | — | `fin_detail.mount.cant_sense_UR` (D-52) | `UNVERIFIED` |
| Motor face x / prop plane x / gap ÷ 0.14 D | 0.02935 / −0.00767 / 1.01 | m, m, — | `CL-D3-X-FACE`, `CL-D3-X-PROP`, `CL-D3-PROP-GAP` | `CHECKED` |
| Blade tip (mid-plane) to tube face, canted disc | 26.9 (≥ 25) | mm | `CL-D3-PROP-TIP-GAP` | `MODELLED` |
| Motor screws: canted plate 4.5 mm, engagement every hole | 3.5 (≥ 3.0) at 0.20 N·m | mm | `CL-D3-SCREW-ENGAGE` | `UNVERIFIED` |
| Collar 12 mm ÷ C4 required / ÷ C6 required / tongue fit | 1.50 / 1.00 / 0.74 mm | — | `CL-D3-COLLAR-H`, `-H-C6`, `CL-D3-TONGUE-FIT` | `UNVERIFIED` |
| Tail embedment ÷ C6 required | 1.74 | — | `CL-D3-TAIL-EMBED` | `UNVERIFIED` |
| Root fillet RF typical / at C6 allowable (lower root governs) | 2.28 / 1.14 | — | `CL-D3-ROOT-FILLET-RF`, `-ALLOW` | `UNVERIFIED` |
| Mount slip: side force / fuse ratio | 87 N / 1.26 | N, — | `CL-D3-SLIP-F`, `CL-D3-SLIP-FUSE` | `UNVERIFIED` |
| ESC pad 46 × 31 mm: outer edge ÷ wash radius | 0.89 | — | `CL-D3-ESC-WASH` | `UNVERIFIED` |
| Thermal: motor base / ESC design vs limit | 66.3 / 83, 61.6 / 85 | °C | `CL-E3-MOUNT-ASA`, `CL-E3-ESC-PEAK` (E3) | `UNVERIFIED` |
| Subsystem mass / allocation | 436.4 / 418 (root fillets 32.2) | g | `CL-D3-MASS`, `CL-D3-FILLET-MASS` | `FAIL` |

## Parts (42 nodes; mass = CAD volume × density, `make_fins.py`)

| Id | Part | Qty | Each g | Line g |
|---|---|---|---|---|
| `FIN-001-<st>` | Half-fin laminate, notch, stepped tip, Ø 8 lead hole, root fillets (lower: link slot) | 4 | 27.7 | 110.7 |
| `FIN-002-R/L` | Motor tube CF 22 × 20 × 344 | 2 | 35.1 | 70.2 |
| `FIN-003-<st>` | Motor mount ASA, 7° canted plate (A = UR/LL, B = UL/LR, R4 sense) | 4 | 11.0 | 44.0 |
| `FIN-004-R/L` | Through-core block PETG, bosses, 2 strap eyes, 2 tie lugs | 2 | 41.0 | 82.1 |
| `FIN-006-R/L` | Tube plug CF 20 × 18 × 53 | 2 | 5.5 | 10.9 |
| `FIN-007-<st>` | ESC pad ASA 46 × 31 | 4 | 2.0 | 8.2 |
| `FIN-008-<st>` | Station collar PETG, 12 mm ring, 40 mm tail, ear, tie lug | 4 | 10.1 | 40.2 |
| `FIN-009-<st>` | Brace CF 10 × 2 (145 / 157 mm) | 4 | 5.2 | 20.6 |
| `FIN-010-<st>` | Brace anchor PETG | 4 | 3.2 | 12.7 |
| `FIN-011-<st><O/I>` | Edge strip CF 10 × 1 × 224 | 8 | 4.1 | 32.6 |
| `FIN-012-<st>` | Pin set, 12 × CF Ø 2 × 11.6 | 4 | 1.1 | 4.3 |
| | **Total** (allocation 418 g) | 42 | | **436.4** (−18.4) |

Hardware and consumables are `FIN-101`…`FIN-107` in `parts.csv`. Parts plus hardware cost about $66.

## Interfaces

| With | Edges | State |
|---|---|---|
| wing (D1) `WNG-001/002` | `E-FIN-49…60` (root bonds now 5 318 / 5 078 mm² of fillet on the skin) | declared |
| propulsion (E1) | `E-FIN-61…64` screws (C6 load line merged), `65…68` straps, **`81…88` thermal (new)** | declared; E1 to acknowledge `81…88` |
| power (F1) | `E-PWR-11…14` caps foam-taped on the half-fin faces | **acknowledged** |
| landing (D5), harness (F2) | `E-GER-01…04`; `E-HRN-03/05…09` | acknowledged |
| internal | `E-FIN-01…48`, `69…80` | declared |

## Open issues

1. Mass 436.4 g against 418 g: the 15 mm root fillets weigh 32 g as drawn, not the +3 g D-48 booked (CR-D3-27).
2. `check.py` KO-PROP: with the D-52 sense the symmetric 10 + 25 mm tilted keep-out reaches the tube, block, plug,
   braces and wing skin; it clears at face_ahead ≥ ~0.019 m. A1 decides (CR-D3-26).
3. `propulsion.stations.x_plate_face_m` 0.0309 is the R3 face; R4 is 0.02935 (CR-D3-26).

## How to verify

T-D3-WEIGH (incl. a fillet cup), T-D3-SLIP, T-D3-ROOT, T-D3-EYE, the D-52 inclinometer and hanging yaw test, D5 shoe
dry-fit on the step, C4 T-C4-TAP-D3 / T-C4-MOUNT-STIFF, C6 coupons (collar, strip anchor, pins, XPS pull), `check.py`.
