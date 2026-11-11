# Fins and motor tubes (FIN): SPEC

Owner D3 · structures C4 · aero B3/B4 · joints C6 · design R5 (CR-A1-63; D-61, D-63, D-68, D-70; CR-E3-13, CR-F2-16,
C6-R5 CR-C6-36) on R4 (D-26, D-27, D-42, D-48, D-51, D-52, D-54) · `MODELLED` · 2026-11-10. Re-check:
`python -I redesign/subsystems/fins/make_fins.py` → `python -I redesign/team/D3/fins_calcs.py` →
`python -I redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py`.

## Purpose

Carry the four motors ±0.19 m above and below the wing on two vertical CF tubes through the wing core, give the
cruise fins (0.21 m half-fins), stand the aircraft on four stepped fin tips, and hold the ESCs in the slipstream.

## Fin-tube junction (P25) and load path

The tube is the fin LE. Each half-fin is a flat 9.6 mm laminate (two 4.8 mm boards) butting the tube. The block's
bore boss holds the root LE in a slot. At the top, the 15 mm station collar has a 40 mm tail: a tongue of board
thickness fills a notch in the laminate's LE-top corner (tongue 11.3 mm, 3.7 mm under the ring), and each CF edge
strip sits in a slot between the tongue and an outer wall, so both strip faces bond to PETG. Nothing wraps the board
around the tube.

| Path | Route |
|---|---|
| Motor loads | motor → 7° canted ASA plate (D-52 sense), face 7.5 mm ahead of the collar (D-61) → 17 mm cheeks → slit collar (friction, D-23 fuse) → tube → station collar → brace (axial) → anchor → spar |
| Tube root | tube → block bore 47 mm (CF plug inside) → spar bore (C2 plug inside the spar) → spar; block vertical edges R 3 mm in an R 3 mm pocket with ≥ 3 mm beads (D-68) |
| Fin top edge | CF edge strips (Ø 2.5 mm CF pins every 15 mm, D-70) → collar tail (two faces, 39.5 mm; bond inspected, BUILD step 13) → tube |
| Fin root, feet | laminate → cove fillets (15 mm on the last 0.15 m of bonded root, 13 mm aft of the hinge, 4 mm bead ahead, none over the D6 slot) and tape laps → core; D5 shoe on the stepped tip. Fillet credited fail-safe only in the wing (D-68) |
| Heat (E3) | motor → own wash (mount not credited, `E-FIN-81…84`); ESC FET face → wash at h 64.6 W/m² K, pad side adiabatic (`E-FIN-85…88`) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fin plane / tube x / tube | ±0.320 / 0.045 / CF 22 × 20 × 344 | m, m, mm | `params.json#fins` | `PROPOSED` |
| Motor plate face x (DP-MOTOR-FACE) / prop plane x, A1 copies both (D-61) | **0.02435 / −0.01267** | m | `CL-D3-X-FACE`, `CL-D3-X-PROP` | `CHECKED` |
| Collar front to prop plane ÷ 0.14 D / blade tip mid-plane to tube | 1.14 / 31.9 (E1 swept volume 26.1 ≥ 25) | —, mm | `CL-D3-PROP-GAP`, `-TIP-GAP`, `CL-E1-TIP-GAP-AT-75` | `MODELLED` |
| Cant sense UR (prop end toward the wing, outboard) | −1 | — | `fin_detail.mount.cant_sense_UR` (D-52) | `UNVERIFIED` |
| Motor screws: canted plate 4.5 mm, engagement every hole | 3.5 (≥ 3.0) at 0.20 N·m | mm | `CL-D3-SCREW-ENGAGE` | `UNVERIFIED` |
| Mount slip: side force at the can / fuse ratio / hold ratio | 74 / 2.29 / 1.76 | N, —, — | `CL-D3-SLIP-F`, `-FUSE`, `-HOLD` | `UNVERIFIED` |
| Collar 15 mm ÷ C4 required / ÷ C6 required (live C1 12.67 N·m) / tongue fit | 1.45 / **0.77** / 3.7 mm | — | `CL-D3-COLLAR-H`, `-H-C6`, `CL-D3-TONGUE-FIT` | `FAIL` → CR-D3-36 |
| Tail embedment ÷ C6 required | 1.27 | — | `CL-D3-TAIL-EMBED` | `UNVERIFIED` |
| Root fillet RF typical / at C6 allowable, D-65 side load 59.0 N ult | 1.62 / **0.81** (needs L_eff 0.182 m) | — | `CL-D3-ROOT-FILLET-RF`, `-ALLOW`, `-ROOT-LEFF-REQ` | `FAIL` → CR-D3-35 |
| Half-fin tip: step front x / step \|z\| / D5 mismatch | 0.2746 / 0.2005 / 0 | m | `CL-D3-TIP-SQUARE`, `-STEP-MISMATCH` | `CHECKED` |
| ESC pad 46 × 31 mm: outer edge ÷ wash radius | 0.89 | — | `CL-D3-ESC-WASH` | `UNVERIFIED` |
| Thermal: motor base / ESC design vs limit | 66.3 / 83, **56.1** / 85 | °C | `CL-E3-MOUNT-ASA`, `CL-E3-ESC-PEAK` (E3) | `UNVERIFIED` |
| Subsystem mass / allocation (fillet mix 0.45 g/cm³ lever taken) | 435.9 / 437 (root fillets 25.0) | g | `CL-D3-MASS`, `-FILLET-MASS` | `MODELLED` |

## Parts (42 nodes; mass = CAD volume × density, `make_fins.py`)

| Id | Part | Qty | Each g | Line g |
|---|---|---|---|---|
| `FIN-001-<st>` | Half-fin laminate, notch, stepped tip, Ø 8 lead hole, root fillets (lower: link slot) | 4 | 25.9 | 103.5 |
| `FIN-002-R/L` | Motor tube CF 22 × 20 × 344 | 2 | 35.1 | 70.2 |
| `FIN-003-<st>` | Motor mount ASA, 7° canted plate 7.5 mm ahead, 17 mm cheeks (A = UR/LL, B = UL/LR) | 4 | 11.9 | 47.8 |
| `FIN-004-R/L` | Through-core block PETG, R 3 mm vertical edges, bosses, 2 strap eyes, 2 tie lugs | 2 | 40.9 | 81.7 |
| `FIN-006-R/L` | Tube plug CF 20 × 18 × 53 | 2 | 5.5 | 10.9 |
| `FIN-007-<st>` | ESC pad ASA 46 × 31 | 4 | 2.0 | 8.2 |
| `FIN-008-<st>` | Station collar PETG, 15 mm ring, 40 mm tail, ear, phase tie lug (x 0.060, open along x) | 4 | 10.5 | 42.0 |
| `FIN-009-<st>` | Brace CF 10 × 2 (145 / 157 mm) | 4 | 5.2 | 20.6 |
| `FIN-010-<st>` | Brace anchor PETG | 4 | 3.2 | 12.7 |
| `FIN-011-<st><O/I>` | Edge strip CF 10 × 1 × 224 | 8 | 4.1 | 32.6 |
| `FIN-012-<st>` | Pin set, 12 × CF Ø 2.5 × 11.6 | 4 | 1.5 | 5.8 |
| | **Total** (allocation 437 g, D-63) | 42 | | **435.9** (+1.1) |

Hardware and consumables are `FIN-101`…`FIN-107` in `parts.csv`.

## Interfaces

| With | Edges | State |
|---|---|---|
| wing (D1) `WNG-001/002` | `E-FIN-49…60` (pocket R 3 mm + beads in `E-FIN-51/52` notes, D-68) | declared |
| propulsion (E1) | `E-FIN-61…64` screws, `65…68` straps, `81…88` thermal (ESC 56.1 °C, h 64.6) | declared; E1 acknowledges all |
| power (F1), landing (D5), harness (F2) | `E-PWR-11…14`; `E-GER-01…04`; `E-HRN-03/05…09` (phase lug moved, CR-F2-16) | acknowledged |
| internal | `E-FIN-01…48`, `69…80` | declared |

## Open issues

1. Collar: C6's live run reads C1's 12.67 N·m section torsion (R4 7.40) and needs 19.4 mm. 15 mm drawn; CR-D3-36.
2. Root fillet at the C6 allowable 0.81 on the D-65 side load. Fix offered (L_eff 0.185 m, +5 g); CR-D3-35.
3. Levers not taken: block fill (C4 re-check), mount cheeks (length set by the reach to the collar). Fillet mix 0.45
   is gated by the T-D3-WEIGH cup (≤ 9.0 g per 20 cm³).

## How to verify

T-D3-WEIGH (fillet cup first), T-D3-SLIP (70–80 N), T-D3-ROOT, T-D3-EYE, the strip-tail tap/pull check (BUILD step
13), the D-52 inclinometer and hanging yaw test, D5 shoe dry-fit, C4 T-C4-TAP-D3 / T-C4-MOUNT-STIFF (≥ 1 100 N·m/rad),
C6 coupons (collar, strip anchor, pins, XPS pull), `check.py`.
