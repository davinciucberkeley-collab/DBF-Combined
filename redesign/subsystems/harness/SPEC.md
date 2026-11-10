# Harness (HRN)

Owner F2 · gauges F1 · status `PROPOSED` (routes `MODELLED` in `fusion/harness.py`, numbers `CHECKED` by
`team/F2/harness.py`) · 2026-11-09. Re-check: `python -I redesign/team/F2/harness.py` → `python -I
redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py` → `python -I redesign/proofs/build_graph.py`.

**Purpose.** Every wire and connector between the pack, power boxes, FC, sensors, ESCs, motors and servos, routed
through the real structure with supports, bend radii, chafe protection and strain relief. The pack plug (AS150U)
is the only field disconnect. Cut list: [`WIRE-LIST.csv`](WIRE-LIST.csv) (29 wires). Figure:
[`team/F2/fig-hrn-01-route.svg`](../../team/F2/fig-hrn-01-route.svg).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| ESC power leads 16 AWG, routed UR / UL / LR / LL (F1 assumed 0.50) | 0.626 / 0.512 / 0.650 / 0.534 | m | `CL-F2-ESC-LEN-*` | `CHECKED` (calc) |
| 8 AWG plug-to-bus path per conductor (≤ 0.15) | 0.038 | m | `CL-F2-MAIN-LEN` | `UNVERIFIED` (`ASM-F2-PWR-STACK`) |
| Phase reach ESC pad → motor lead exit / extension needed (≤ 0.10) | 0.121 / 0.061 | m | `CL-F2-PHASE-REACH`, `-EXT` | `UNVERIFIED` (motor lead unpublished) |
| I²C bus total (≤ 0.5) / RX lead (≤ 0.15) | 0.455 / 0.134 | m | `CL-F2-I2C-LEN`, `CL-F2-RX-LEN` | `UNVERIFIED` (`ASM-F2-FC-PORTS`) |
| Longest DShot lead (≤ 0.7 `ASM`) | 0.686 | m | `CL-F2-DSHOT-LEN` | `UNVERIFIED` (+2 %, `T-F2-DSHOT`) |
| Servo terminal voltage, both stalled, 26 AWG (≥ 5.7) | 5.75 | V | `CL-F2-SERVO-V` | `UNVERIFIED` (+1 %) |
| ESC-lead grooves to GPS mast top (≥ 0.12) | 0.173 | m | `CL-F2-GROOVE-MAST` | `CHECKED` |
| Worst bend: allowed / required radius (k × OD) | 1.07 | — | `CL-F2-BEND` | `CHECKED` |
| Longest free span in the slipstream (≤ 0.05) | 0.050 | m | `CL-F2-FREE-SPAN` | `CHECKED` |
| Fullest pass (straw / grommet, ≤ 0.40) | 0.31 | — | `CL-F2-FILL` | `CHECKED` |
| Harness mass, basic (allocation 105) | 122.6 (111 if no phase extension) | g | `CL-F2-MASS` | **`FAIL`** (CR-F2-01) |
| Harness CG x (A3 model ≈ 0.035) | 0.067 | m | `CL-F2-CG-X` | `CHECKED` (+1.6 mm aircraft CG) |

## Routing (aircraft frame, m)

| Run | Route | Support / protection |
|---|---|---|
| Pod | bus PDB (left channel) → aft along the inboard side; right-side leads cross behind the aft stop at x 0.087 (pairs stacked 8 mm apart) | tied to the tray tie bar ≤ 0.08 m; PET sleeve on the crossing |
| Exits | new side-wall exits 16 × 12 mm at x 0.056–0.072, z 0.027–0.039 (power + DShot); D2's aft exits for the servo leads only | PET sleeve 40 mm, edge taped |
| Wing, upper | three grooves ahead of the spar slot: DShot x 0.054, + 0.059, − 0.064 (5 mm pitch, 3 mm foam to the slot), y 0.086 → 0.296 | power 3.0 × 3.1 mm, signal 2.5 × 2.4 mm; wire 0.5 mm below the surface; tape tabs, then the skin |
| Wing, lower | LR/LL pair + DShot through P1 (7 mm straw, 45° slant, y 0.092 → 0.122), same three grooves on the lower surface | straw liner, lips sanded R ≥ 12 mm |
| Fin root | groove end → tie at the boss tail (inboard) → Ø 8 mm hole through the half-fin at x 0.086, 10 mm off the skin → outboard face | printed ASA grommet 10/7 mm |
| Fin face | tape strips every ≤ 50 mm to the ESC power end (x 0.124); 680 µF cap beside it, leads ≤ 20 mm | never under the ESC strap or over its FET face (E3) |
| Phase | ESC phase end (x 0.078) → collar tie → motor lead exit; 3 staggered soldered splices, outer sleeve | ≥ 5 mm off the bell; phase order labelled (F4 rotation) |
| Servo | aft exit → groove x 0.108 (aft of the slot) → y 0.285 → branch to the pocket at x 0.19 | 4.0 × 1.6 mm groove; JR at the servo |
| GPS / sensors | GPS cable up the right side wall (z 0.06) → right handle-leg bore → grip → mast; RX, airspeed I²C branch and power-board link under the pack in a 10 × 3 mm floor channel at x −0.065 | GPS cable alone, crosses power at 90°, ≥ 25 mm above the UBEC |

Removable joints (one-piece airframe: no structural field joint carries a wire):

| Removable joint | When | Wire across it | Disconnect |
|---|---|---|---|
| Pack | every flight | Vbat 10 / 8 AWG | AS150U in the 60 mm park |
| Props ×4, pitot boom `AVN-005` | every trip | none (pitot is pneumatic, F3 couplers) | — |
| FC `AVN-001` | bench | 6 outputs, rail, GH cables | JR in-line row on the tray tie bar; GH |
| Elevon servo `MEC-001` | bench | 26 AWG 3-core | JR at the servo pocket |
| GPS, RX, airspeed, power board | bench | 28 AWG | JST-GH both ends |
| Landing feet `GER` | bench | none | — |
| ESC, motor | bench | 16 AWG power, phases | none on purpose: soldered (below) |

Disconnects: AS150U (field) · JR in-line at the tray for the 6 FC outputs (FC swap) · JR at each servo · JST-GH at
GPS, RX, airspeed, power board. Soldered on purpose: ESC power pads and motor phases (any motor/ESC fault is fatal;
no bullet contacts in the propulsion path, −15.6 g vs 12 × 3.5 mm bullets). Motor or ESC swap is a bench solder job.

## Parts summary

| Id | Part | Qty | Each g |
|---|---|---|---|
| `HRN-001` | Pod bundle (lumped, carried) | 1 | 41.2 |
| `HRN-002-R/L` | Wing-fin bundle (lumped, carried) | 2 | 40.7 / 40.6 |
| `HRN-101…111` | wire 16/20/26/28 AWG, JR and JST-GH kits, heat-shrink, ties, PET sleeve, grommets, straws | — | 0 (in bundles); ≈ $68 `EST` |

## Interfaces

| With | Edges | State |
|---|---|---|
| pod (D2) | `E-HRN-01` tie bar on the tray | declared, D2 acknowledges |
| fins (D3) | `E-HRN-03/05` boss-tail ties, `E-HRN-06…09` collar ties (new ids, CR-F2-06) | declared, fins to acknowledge |
| propulsion (E1) | `E-HRN-17…20` phases (`CT-SOLDER-PHASE`); `-13…16`, `-24…27` | 17–20 declared; others pending |
| wing, power, avionics, mechanisms | `E-HRN-02/04`, `-10…16`, `-21…32` with `wire`, `current_a`, `signal.fc_port` blocks | in `edges-pending.json` until `WNG/PWR/AVN/MEC` parts exist; promoted automatically |

## Mass budget

| Item | g | Maturity |
|---|---|---|
| ESC power leads 16 AWG (R pair 41.2, L pair 33.8) | 75.0 | CALC |
| Phase extensions (0 if the factory leads reach) | 11.7 | EST |
| DShot 5.4 · servo + UBEC 9.4 · JST-GH cables 4.2 | 19.0 | CALC |
| Fittings (JR, GH, splices, grommets, ties, tape, sleeves) | 16.9 | EST |
| **Total / allocation** | **122.6 / 105** | `FAIL` |

## Open issues

1. Mass +17.6 g over: the right ESC pairs cross the pod (+0.11 m each) and F1's 0.5 m was short; CR-F2-01 to A1.
2. Motor and ESC factory lead lengths unpublished: measure at `T-E1-MOTOR-RM`, then cut the extension.
3. CoreWing port positions and the power-board/bus stack are assumptions (`ASM-F2-FC-PORTS`, `-PWR-STACK`).
4. `check.py` reports the carried bundles as floating (no `carried` exemption in its floating check, CR-F2-09).

## How to verify

`T-F2-FIT` (dry fit before skinning), `T-F2-WEIGH`, `T-F2-CONT` (continuity, polarity, isolation, 10 N pull),
`T-F2-DSHOT` (bdshot error rate), `T-F3-I2C-SCAN`, `T-F1-WIRE-HEAT` on a routed groove sample, `T-F1-SERVO-STALL`.
