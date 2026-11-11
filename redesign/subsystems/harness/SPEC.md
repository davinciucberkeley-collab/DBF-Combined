# Harness (HRN)

Owner F2 · gauges F1 · status `PROPOSED` (routes `MODELLED` in `fusion/harness.py`, numbers `CHECKED` by
`team/F2/harness.py`) · revision F2-R3, 2026-11-10. Re-check: `python -I redesign/team/F2/harness.py` → `python -I
redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py` → `python -I redesign/proofs/build_graph.py`.

**Purpose.** Every wire and connector between the pack, power stack, FC, sensors, ESCs, caps, motors and servos,
routed through the real structure with supports, bend radii, chafe protection and strain relief. The pack plug
(AS150U) is the only field disconnect. Cut list: [`WIRE-LIST.csv`](WIRE-LIST.csv) (36 rows, 28 electrical edges).
Figure: [`team/F2/fig-hrn-01-route.svg`](../../team/F2/fig-hrn-01-route.svg).

**R2 changes.** All 21 parked edges are in `interfaces.json` (`edges-pending.json` is empty) and the CAD draws 28
wires. CR-F1-18: fuse `PWR-007` in the UBEC feed (`E-HRN-21` bars → fuse, new `E-HRN-33` fuse → UBEC), ESC caps
`E-HRN-34…37`, 10 AWG main jumpers on F1's PWR-R1 stack. Wire ends on F3's port points (CR-F3-16). Servo lead to D6's
lower pocket through D1's lead hole (CR-D1-06). Fin lead hole 22 mm off the skin (CR-D3-23). Bundle bodies sized by
their wire mass, so the declared CG is the CAD centroid (CR-A5-27).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| ESC power leads 16 AWG, routed UR / UL / LR / LL | 0.595 / 0.475 / 0.620 / 0.497 | m | `CL-F2-ESC-LEN-*` | `CHECKED` (calc) |
| 10 AWG jumpers cups → board / board → bars (F1 sized 0.030 / 0.050); path ≤ 0.15 | 0.030 / 0.050; 0.080 | m | `CL-F2-MAIN-1-LEN`, `-2-LEN`, `CL-F2-MAIN-LEN` | `UNVERIFIED` (`ASM-F2-PWR-STACK`) |
| ESC cap legs, cap → pads (≤ 0.020) | 0.011 | m | `CL-F2-CAP-LEAD` | `CHECKED` |
| Phase reach ESC pad → motor lead exit / extension needed (≤ 0.10) | 0.116 / 0.056 | m | `CL-F2-PHASE-REACH`, `-EXT` | `UNVERIFIED` (motor lead unpublished) |
| I²C bus total (≤ 0.5) / RX lead (≤ 0.15) | 0.461 / 0.116 | m | `CL-F2-I2C-LEN`, `CL-F2-RX-LEN` | `UNVERIFIED` (`ASM-F2-FC-PORTS`, ±10 mm) |
| Longest DShot lead (≤ 0.7 `ASM`) | 0.674 | m | `CL-F2-DSHOT-LEN` | `UNVERIFIED` (+4 %, `T-F2-DSHOT`) |
| Longest servo circuit FC → servo case / terminal voltage, both stalled at 1.4 A (≥ 5.7) | 0.558 / 5.74 | m / V | `CL-F2-SERVO-LEN`, `-SERVO-V` | `UNVERIFIED` (+1 %) |
| ESC-lead grooves to the GPS module (≥ 0.12) | 0.180 | m | `CL-F2-GROOVE-MAST` | `CHECKED` |
| Worst bend: allowed / required radius (k × OD) | 1.02 | — | `CL-F2-BEND` | `CHECKED` |
| Longest free span in the slipstream (≤ 0.05) | 0.047 | m | `CL-F2-FREE-SPAN` | `CHECKED` (phase run) |
| Fullest pass (straw / grommet, ≤ 0.40) | 0.31 | — | `CL-F2-FILL` | `CHECKED` |
| Harness mass, basic (allocation 123, D-48) | 117.3 (106.4 if no phase extension) | g | `CL-F2-MASS` | `CHECKED` (+5 %) |
| Harness CG x (wire mass) | 0.064 | m | `CL-F2-CG-X` | `CHECKED` |
| Declared CG (body centroid) vs wire-mass CG, worst bundle (≤ 0.010) | 6.4 (pod), 0.5 (wing-fin) | mm | `CL-F2-CG-BODY` | `CHECKED` |

## Routing (aircraft frame, m)

| Run | Route | Support / protection |
|---|---|---|
| Power stack (F1 PWR-R1) | pack lead over the aft stop to the AS150U mating face x 0.031; 10 AWG cups (x 0.002) → board input pads (aft edge x −0.010, z 0.048); board output pads → down the deck window → bus-bar aft end (x −0.0105, z 0.024) | jumpers formed before soldering, two bends ≥ 2 × OD (F1 `CL-PWR-BEND`) |
| Pod power | ESC pairs leave the bars aft through the tunnel under the cradle in four stacked layers (LR, UR, LL, UL, 3 mm pitch); left pairs out between cradle leg 0 and the bracket flange; right pairs cross aft of the strut ribs (x 0.085) over the foot bridge, inboard of the right leg, over the UBEC to the right exit; the fused UBEC feed runs over all four under the cradle floor and crosses above them at x 0.088 to the UBEC input pads. Signals, servo, sensor runs each in their own lane (JR row order: servo L, UL, LL, servo R, LR, UR; three lanes in the under-pack channel). No run touches another or the structure (`team/F2/ROUTE-CLEARANCE.md`) | tied ≤ 0.08 m; PET sleeve on the crossing; fuse holder in the frame clip |
| Pod signals | FC aft edge (0.014, 0.046, 0.030): 6 output pigtails ≤ 100 mm → JR row x 0.030; UBEC output → FC rail | tray tie bar |
| Exits | D2 side-wall exits x 0.056–0.072, z 0.027–0.039 (power + DShot); D2 aft exits for the servo leads only | PET sleeve 40 mm, edge taped |
| Wing, upper | three grooves ahead of the spar slot: DShot x 0.054, + 0.059, − 0.064 (5 mm pitch, 3 mm foam to the slot), y 0.086 → 0.296 | power 3.0 × 3.1 mm, signal 2.5 × 2.4 mm; wire 0.5 mm below the surface; tape tabs, then the skin |
| Wing, lower | LR/LL pair + DShot through P1 (7 mm straw, 45° slant, y 0.092 → 0.122), same grooves on the lower surface | straw liner, lips sanded R ≥ 12 mm |
| Fin root | lead leaves the groove 12 mm before its end, rises out of the skin over the bead lip and the block boss (boss top + 1.5 mm) → tie above the boss-tail lug (x 0.071, inboard) → Ø 8 mm hole through the half-fin at x 0.086, **22 mm off the skin** (z +0.0447 / −0.0307, D3) → outboard face, 1.9 mm off it | printed ASA grommet 10/7 mm; the tie point resets the free span |
| Fin face | tape strips every ≤ 50 mm; the pair rises **below** the ESC and lands on its aft-end power pads from underneath (x 0.122); the 680 µF cap sits in line aft of the ESC (x 0.127–0.147) and its legs fold forward onto the same pads (11 mm) | never under the ESC strap or over its FET face (E3) |
| Phase | ESC phase end (x 0.078) → tie beside the collar-tail lug (x 0.0655, 1.5 mm off the tail wall and lug) → over the pinch bolt and nut → tie at the pinch ear (x 0.052, 2.5 mm over the ear) → motor lead exit; free spans 29 / 29 mm; 3 staggered soldered splices, outer sleeve | ≥ 5 mm off the bell; phase order labelled (F4 rotation); no contact with the collar, mount, bolt or nut (`ROUTE-CLEARANCE.md`) |
| Servo | aft exit → groove x 0.108 (aft of the slot) → D1 upper branch groove along \|y\| 0.285 → JR in-line in an 18 × 10 × 5 mm recess (x 0.150–0.168, CR-F2-14) → servo's own lead (cut to 40 mm, re-terminated) → D1 lead hole x 0.173–0.177 (4 mm straw) → D6 lower pocket → case front | 4.0 × 1.6 mm groove; recess under a re-openable tape flap |
| GPS / sensors | GPS cable up the right side wall (z 0.06) → right handle-leg window and bore → grip → mast → connector (0.081, 0, 0.183); RX, airspeed I²C branch and power-board link cross under the pack in D2's floor channel at **x −0.0245**; left-side runs pass inboard of the RX | GPS cable alone, crosses power at 90°, ≥ 25 mm above the UBEC |

Removable joints (one-piece airframe: no structural field joint carries a wire):

| Removable joint | When | Wire across it | Disconnect |
|---|---|---|---|
| Pack | every flight | Vbat (pack's own 10 AWG lead) | AS150U at the cradle |
| Props ×4, pitot boom `AVN-005` | every trip | none (pitot is pneumatic, F3 couplers) | — |
| FC `AVN-001` | bench | 6 outputs, rail, GH cables | JR in-line row on the tray tie bar; GH |
| Elevon servo `MEC-001` | bench | 26 AWG 3-core | JR in the wing recess (lift the tape flap) |
| UBEC `PWR-005` / fuse `PWR-007` | bench | 20 AWG | solder splices; the fuse itself pulls out of its holder |
| GPS, RX, airspeed, power board | bench | 28 AWG | JST-GH (RX: solder pads at the RP3) |
| Power stack (4 screws) | bench | ESC pairs, fuse feed at the bars | none: re-solder at the bars |
| ESC, motor, cap | bench | 16 AWG power, phases, cap legs | none on purpose: soldered (below) |

Soldered on purpose: ESC power pads, cap legs and motor phases (any motor/ESC fault is fatal; no bullet contacts in
the propulsion path, −15.6 g vs 12 × 3.5 mm bullets).

## Parts summary

| Id | Part | Qty | Each g |
|---|---|---|---|
| `HRN-001` | Pod bundle (lumped, carried, mass proxy: not drawn) | 1 | 41.4 |
| `HRN-002-R/L` | Wing-fin bundle (lumped, carried, mass proxy: not drawn) | 2 | 39.5 / 38.9 |
| `HRN-101…112` | wire 16/20/26/28 AWG, JR and JST-GH kits, heat-shrink, ties, PET sleeve, grommets, straws | — | 0 (in bundles); $68 `EST`, prices `UNVERIFIED` |

## Interfaces

| With | Edges | State |
|---|---|---|
| pod (D2) | `E-HRN-01` tie bar on the tray | declared, acknowledged |
| wing (D1) | `E-HRN-02/04` groove channels | declared; wing to acknowledge (CR-F2-04) |
| fins (D3) | `E-HRN-03/05` boss-tail ties, `E-HRN-06…09` collar ties | declared, acknowledged (CR-D3-23); collar lug position CR-F2-16 |
| power (F1) | `E-HRN-10…16`, `-21…23`, `-33`; caps `-34…37` | declared, acknowledged |
| propulsion (E1) | `E-HRN-13…20`, `-24…27`, `-34…37` | declared, acknowledged |
| avionics (F3) | `E-HRN-22…32` | declared; avionics to acknowledge (CR-F2-17) |
| mechanisms (D6) | `E-HRN-28/29` | declared, acknowledged |

## Mass budget

| Item | g | Maturity |
|---|---|---|
| ESC power leads 16 AWG (R pair 39.3, L pair 31.4) | 70.6 | CALC |
| Phase extensions (0 if the factory leads reach) | 10.9 | EST |
| DShot 5.3 · servo + fuse/UBEC feed + rail 9.0 · JST-GH cables 4.3 | 18.5 | CALC |
| Fittings (JR, GH, splices, grommets, ties, tape, sleeves, straws) | 17.2 | EST |
| **Total / allocation** | **117.3 / 123** | `CHECKED` +5 % |

Not booked here: 10 AWG jumpers (PWR-002), cap legs (PWR-008), pack lead (PWR-001), servo's own lead (MEC-001).

## Open issues

1. Motor and ESC factory lead lengths unpublished: measure at `T-E1-MOTOR-RM`, then cut the extension (12 g back to
   A1 if they reach, D-48).
2. CoreWing pin-out still unpublished: F3's port points are ±10 mm; I²C (+8 %) and DShot (+4 %) margins depend on it.
3. JR recess in the wing core (CR-F2-14 to D1) and the shortened servo lead (CR-F2-15 to D6) need acceptance.
4. Downstream re-runs on the new routed ESC lengths: F1 `power.py` (CR-F2-13).

## How to verify

`T-F2-FIT` (dry fit before skinning), `T-F2-WEIGH`, `T-F2-CONT` (continuity, polarity, isolation, 10 N pull),
`T-F2-DSHOT` (bdshot error rate), `T-F3-I2C-SCAN`, `T-F1-WIRE-HEAT` on a routed groove sample, `T-F1-SERVO-STALL`,
`T-PWR-FIT` (jumpers).
