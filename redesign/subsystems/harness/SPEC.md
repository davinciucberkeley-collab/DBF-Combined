# Harness (HRN)

Owner F2 · gauges F1 · status `PROPOSED` (routes `MODELLED` in `fusion/harness.py`, numbers `CHECKED` by
`team/F2/harness.py`) · revision F2-R4 (D-74), 2026-11-11. Re-check: `python -I redesign/team/F2/harness.py` → `python -I
redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py` → `python -I redesign/proofs/build_graph.py`.

**Purpose.** Every wire and connector between the pack, power stack, FC, sensors, ESCs, caps, motors and servos,
routed through the real structure with supports, bend radii, chafe protection and strain relief. The pack plug
(AS150U) is the only field disconnect. Cut list: [`WIRE-LIST.csv`](WIRE-LIST.csv) (33 rows, 25 electrical edges).
Figure: [`team/F2/fig-hrn-01-route.svg`](../../team/F2/fig-hrn-01-route.svg).

**R2 changes.** All 21 parked edges are in `interfaces.json` (`edges-pending.json` is empty) and the CAD draws 28
wires. CR-F1-18: fuse `PWR-007` in the UBEC feed (`E-HRN-21` bars → fuse, new `E-HRN-33` fuse → UBEC), ESC caps
`E-HRN-34…37`, 10 AWG main jumpers on F1's PWR-R1 stack. Wire ends on F3's port points (CR-F3-16). Servo lead to D6's
lower pocket through D1's lead hole (CR-D1-06). Fin lead hole 22 mm off the skin (CR-D3-23). Bundle bodies sized by
their wire mass, so the declared CG is the CAD centroid (CR-A5-27).

**R4 changes (D-74, 2026-11-11).** UBEC `PWR-005` and fuse `PWR-007` deleted: `W-FUSE-IN`, `W-UBEC-IN`,
`W-UBEC-OUT` and their edges `E-HRN-21`, `-33`, `-22` are gone. The servos take Vx from the FC header, fed by the
power board's servo BEC (6 V jumper) through the board link. One Amass **XT30U** per ESC pair (`HRN-113`, BOM `H06`;
edges `E-HRN-13…16` via `CT-XT30U`), drawn as parts `HRN-113-UR/UL/LR/LL` at the manufacturer's 20.1 × 10.2 mm
(× 5.2 mm listing): the right pair stacked just inside the right exit, the left pair stacked in the tunnel under the
AS150U cradle (the cradle legs moved 10 mm forward for the turn to the left exit). Servo + / − are 22 AWG (signal
28 AWG) and the link carries Vx on 4 conductors, so the stalled servo holds 5.75 V. D-79 moves 6 g of allocation
from power to harness (129 g). `W-PMOD` re-typed: a 10-way 28 AWG ribbon on
the boards' own board-to-board headers (case S, `CT-PIN-HEADER-LINK`), re-routed over the front edge of the 56 mm deck
(`KO-PWR-BOARD`). Route clearance still 0 penetrations (`team/F2/ROUTE-CLEARANCE.md`).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| ESC power leads 16 AWG, routed UR / UL / LR / LL | 0.595 / 0.475 / 0.620 / 0.497 | m | `CL-F2-ESC-LEN-*` | `CHECKED` (calc) |
| 10 AWG jumpers cups → board / board → bars (F1 sized 0.030 / 0.050); path ≤ 0.15 | 0.030 / 0.050; 0.080 | m | `CL-F2-MAIN-1-LEN`, `-2-LEN`, `CL-F2-MAIN-LEN` | `UNVERIFIED` (`ASM-F2-PWR-STACK`) |
| ESC cap legs, cap → pads (≤ 0.020) | 0.011 | m | `CL-F2-CAP-LEAD` | `CHECKED` |
| Phase reach ESC pad → motor lead exit / extension needed (≤ 0.10) | 0.116 / 0.056 | m | `CL-F2-PHASE-REACH`, `-EXT` | `UNVERIFIED` (motor lead unpublished) |
| I²C bus total (≤ 0.5) / RX lead (≤ 0.15) | 0.461 / 0.116 | m | `CL-F2-I2C-LEN`, `CL-F2-RX-LEN` | `UNVERIFIED` (`ASM-F2-FC-PORTS`, ±10 mm) |
| Longest DShot lead (≤ 0.7 `ASM`) | 0.674 | m | `CL-F2-DSHOT-LEN` | `UNVERIFIED` (+4 %, `T-F2-DSHOT`) |
| Longest servo circuit FC → servo case / terminal voltage, both stalled at 1.4 A (≥ 5.7): harness + / − 22 AWG (lead drop 0.149 V) and board link 4 Vx + 3 GND (0.102 V, case S) | 0.571 / 5.75 | m / V | `CL-F2-SERVO-LEN`, `-SERVO-V`, `-SERVO-LEAD-DROP`, `-SERVO-LINK-DROP` | `UNVERIFIED` (+0.9 %, `T-F1-SERVO-STALL`) |
| Board link `W-PMOD` (case S), PDB → FC, cut | 0.198 | m | `CL-F2-PMOD-LEN` | `UNVERIFIED` (pin map, `BOARD-CHECK.md` step 4) |
| ESC-lead grooves to the GPS module (≥ 0.12) | 0.180 | m | `CL-F2-GROOVE-MAST` | `CHECKED` |
| Worst bend: allowed / required radius (k × OD) | 1.02 | — | `CL-F2-BEND` | `CHECKED` |
| Longest free span in the slipstream (≤ 0.05) | 0.047 | m | `CL-F2-FREE-SPAN` | `CHECKED` (phase run) |
| Fullest pass: under-pack channel, board-link ribbon 10 + RX 4 + airspeed 4 (≤ 0.40) | 0.38 | — | `CL-F2-FILL` | `CHECKED` |
| Harness mass, basic (allocation 129, D-79) incl. the four XT30U parts (8.0 g) | 127.7 (115.5 if no phase extension) | g | `CL-F2-MASS` | `CHECKED` +1 % |
| Harness CG x (wire mass) | 0.063 | m | `CL-F2-CG-X` | `CHECKED` |
| Declared CG (body centroid) vs wire-mass CG, worst bundle (≤ 0.010) | 6.3 (pod), 0.5 (wing-fin) | mm | `CL-F2-CG-BODY` | `CHECKED` |

## Routing (aircraft frame, m)

| Run | Route | Support / protection |
|---|---|---|
| Power stack (F1 PWR-R1) | pack lead over the aft stop to the AS150U mating face x 0.031; 10 AWG cups (x 0.002) → board input pads (aft edge x −0.010, z 0.048); board output pads → down the deck window → bus-bar aft end (x −0.0105, z 0.024) | jumpers formed before soldering, two bends ≥ 2 × OD (F1 `CL-PWR-BEND`) |
| Pod power | ESC pigtails leave the bars aft through the tunnel under the cradle in four stacked layers (LR, UR, LL, UL, 3 mm pitch); left pairs out between cradle leg 0 and the bracket flange; right pairs run in the inboard half of the tunnel (y −0.043), cross aft of the strut ribs (x 0.085) over the foot bridge, inboard of the right leg, in the right lane (the former UBEC zone, now free) to the right exit; the left pairs run in the outboard half (y −0.052) and turn to the left exit aft of the cradle legs (moved to x 0.046–0.050). **XT30U** bodies (`HRN-113-*`, stacked 5.8 mm pitch, flat): UR / LR at (0.067, 0.050, z 0.035 / 0.029) on the last run to the right exit, between the handle leg and the right signal leads; UL / LL at (0.026, −0.052, z 0.034 / 0.028) in the tunnel under the cradle; the pigtail length bars → plug is in `WIRE-LIST.csv` (disconnect column). Signals, servo, sensor runs each in their own lane (JR row order: servo L, UL, LL, servo R, LR, UR; three lanes in the under-pack channel). No run touches another or the structure (`team/F2/ROUTE-CLEARANCE.md`) | tied ≤ 0.08 m; plug body tied in its lane; PET sleeve on the crossing |
| Pod signals | FC aft edge (0.014, 0.046, 0.030): 6 output pigtails ≤ 100 mm → JR row x 0.030; servo rail = the FC header's Vx row (power-board servo BEC, D-74) | tray tie bar |
| Exits | D2 side-wall exits x 0.056–0.072, z 0.027–0.039 (power + DShot); D2 aft exits for the servo leads only | PET sleeve 40 mm, edge taped |
| Wing, upper | three grooves ahead of the spar slot: DShot x 0.054, + 0.059, − 0.064 (5 mm pitch, 3 mm foam to the slot), y 0.086 → 0.296 | power 3.0 × 3.1 mm, signal 2.5 × 2.4 mm; wire 0.5 mm below the surface; tape tabs, then the skin |
| Wing, lower | LR/LL pair + DShot through P1 (7 mm straw, 45° slant, y 0.092 → 0.122), same grooves on the lower surface | straw liner, lips sanded R ≥ 12 mm |
| Fin root | lead leaves the groove 12 mm before its end, rises out of the skin over the bead lip and the block boss (boss top + 1.5 mm) → tie above the boss-tail lug (x 0.071, inboard) → Ø 8 mm hole through the half-fin at x 0.086, **22 mm off the skin** (z +0.0447 / −0.0307, D3) → outboard face, 1.9 mm off it | printed ASA grommet 10/7 mm; the tie point resets the free span |
| Fin face | tape strips every ≤ 50 mm; the pair rises **below** the ESC and lands on its aft-end power pads from underneath (x 0.122); the 680 µF cap sits in line aft of the ESC (x 0.127–0.147) and its legs fold forward onto the same pads (11 mm) | never under the ESC strap or over its FET face (E3) |
| Phase | ESC phase end (x 0.078) → tie beside the collar-tail lug (x 0.0655, 1.5 mm off the tail wall and lug) → over the pinch bolt and nut → tie at the pinch ear (x 0.052, 2.5 mm over the ear) → motor lead exit; free spans 29 / 29 mm; 3 staggered soldered splices, outer sleeve | ≥ 5 mm off the bell; phase order labelled (F4 rotation); no contact with the collar, mount, bolt or nut (`ROUTE-CLEARANCE.md`) |
| Servo | aft exit → groove x 0.108 (aft of the slot) → D1 upper branch groove along \|y\| 0.285 → JR in-line in an 18 × 10 × 5 mm recess (x 0.150–0.168, CR-F2-14) → servo's own lead (cut to 40 mm, re-terminated) → D1 lead hole x 0.173–0.177 (4 mm straw) → D6 lower pocket → case front | 4.0 × 1.6 mm groove; recess under a re-openable tape flap |
| GPS / sensors | GPS cable up the right side wall (z 0.06) → right handle-leg window and bore → grip → mast → connector (0.081, 0, 0.183); RX, airspeed I²C branch and power-board link cross under the pack in D2's floor channel at **x −0.0245**; left-side runs pass inboard of the RX. Board link (case S): from the PDB contacts (top face, forward-inboard corner, x −0.058) forward over the deck front edge (x −0.066), down at x −0.0685 inboard of the airspeed board, into the corridor under the deck (y −0.028) | GPS cable alone, crosses power at 90° |

Removable joints (one-piece airframe: no structural field joint carries a wire):

| Removable joint | When | Wire across it | Disconnect |
|---|---|---|---|
| Pack | every flight | Vbat (pack's own 10 AWG lead) | AS150U at the cradle |
| Props ×4, pitot boom `AVN-005` | every trip | none (pitot is pneumatic, F3 couplers) | — |
| FC `AVN-001` | bench | 6 outputs, rail, GH cables | JR in-line row on the tray tie bar; GH |
| Elevon servo `MEC-001` | bench | 26 AWG 3-core | JR in the wing recess (lift the tape flap) |
| ESC power pair (wing ↔ pod), × 4 | bench (ESC, lead or half-fin swap) | 16 AWG + / − | **XT30U** just inside each pod side exit (D-74, WB-03) |
| GPS, RX, airspeed | bench | 28 AWG | JST-GH (RX: solder pads at the RP3) |
| Power board ↔ FC | bench | case S: 28 AWG ribbon `W-PMOD`; case U: none (stacked) | the board's own board-to-board header (no JST-GH 6 exists on this product) |
| Power stack (4 screws) | bench | ESC pairs | the four XT30U; no desoldering |
| ESC, motor, cap | bench | 16 AWG power, phases, cap legs | none on purpose: soldered (below) |

Soldered on purpose: ESC power pads, cap legs and motor phases (any motor/ESC fault is fatal; no bullet contacts on
the motor phases, −15.6 g vs 12 × 3.5 mm bullets). The one exception is the pod–wing plug below.

### Pod–wing power disconnect (WB-03, D-74)

| Item | Choice | Numbers | Source / status |
|---|---|---|---|
| Connector | **Amass XT30U**, one male/female pair per ESC pair (4 fitted), keyed, 2 pins | — | `PROPOSED` |
| Where | right pair: stacked just inside the right exit (x 0.062–0.072); left pair: stacked in the tunnel under the AS150U cradle (x 0.016–0.036), reached with the power frame lifted; female (socket) on the bus-board pigtail (live side), male on the ESC lead | mated 20.1 × 10.2 mm (Amass manual drawing), 5.2 mm thick (listing, `UNVERIFIED`); drawn as parts, in route clearance | `T-F2-FIT` |
| Rating vs need per ESC | 20 A (Amass, 16 AWG, ΔT < 85 K; resellers say 15 A cont / 30 A peak) vs 7.6 A cruise share, 8.4 A hover, 24.8 A limited peak, 51.6 A for 2 s | contact heating at 51.6 A for 2 s: ≈ 3 J into ≈ 1 g of brass, < 10 K | Amass XT30U manual; `CL-F1-I-CONT`, F1 limiter figures; `UNVERIFIED` |
| Added loop resistance | 2 contacts × ≤ 1.2 mΩ (Amass) = ≤ 2.4 mΩ | at 24.8 A: ≤ 60 mV, +0.4 % of 14.8 V on top of the LR lead's 4.89 % → ≈ 5.3 %, over F1's 5 % guideline (WB-11: a guideline, not a hardware limit) | `T-F1-DROP` measures it with the plugs in |
| Mass | ≈ 2.0 g per mated pair with heat-shrink (resellers: 1.7 g bare) | **+8.0 g** for 4 | `EST`, weigh at `T-F2-WEIGH` |
| Why not XT60 | ≈ 5 g per pair, +20 g; its 30 A class is not needed per ESC | — | — |
| Why not bullets | 2 contacts per pair, unkeyed, polarity can be swapped | — | — |

**Harness mass change (state it: above the ±2 g target), as modelled.** +8.0 g (four XT30U, now parts `HRN-113-*`)
− 3.8 g (`W-FUSE-IN`, `W-UBEC-IN`, `W-UBEC-OUT`) + 1.0 g (`W-PMOD` 10-way ribbon 0.198 m) + 3.2 g (servo + / − 26 →
22 AWG, signal 28 AWG, for `CL-F2-SERVO-V`) − 0.5 g of fittings = **+7.9 g**: harness 119.8 → **127.7 g**. D-79 moves
6 g of allocation from power (636 → 630 g; power 622.4 g after D-74) to harness (123 → 129 g); total allocation and
the reserve unchanged. The ESC lead wire itself does not change: pigtail and lead together are the same routed
16 AWG length.

## Parts summary

| Id | Part | Qty | Each g |
|---|---|---|---|
| `HRN-001` | Pod bundle (lumped, carried, mass proxy: not drawn) | 1 | 39.1 |
| `HRN-002-R/L` | Wing-fin bundle (lumped, carried, mass proxy: not drawn) | 2 | 40.6 / 40.0 |
| `HRN-113-UR/UL/LR/LL` | Amass XT30U mated pair, drawn 20.1 × 10.2 × 5.2 mm, carried (tied, `E-HRN-38…41`) | 4 | 2.0 |
| `HRN-101`, `-102`, `-104…112` | wire 16 / 22 / 28 AWG (22 AWG red + black for the servo + / −; the 26 AWG servo cable `HRN-103` is gone), JR and JST-GH kits, heat-shrink, ties, PET sleeve, grommets, straws | — | 0 (in bundles); $63 `EST`, prices `UNVERIFIED` |
| `HRN-113` | Amass XT30U pairs, 10-pack (4 fitted as `HRN-113-*`), BOM `H06` | 1 | $9.99 |
| `HRN-114` | pin-header strip + 10-way 28 AWG ribbon for `W-PMOD` (case S); I1 to add to the BOM | 1 | 0 (in `HRN-001`); $3 `EST` |

## Interfaces

| With | Edges | State |
|---|---|---|
| pod (D2) | `E-HRN-01` tie bar on the tray | declared, acknowledged |
| wing (D1) | `E-HRN-02/04` groove channels | declared; wing to acknowledge (CR-F2-04) |
| fins (D3) | `E-HRN-03/05` boss-tail ties, `E-HRN-06…09` collar ties | declared, acknowledged (CR-D3-23); collar lug position CR-F2-16 |
| power (F1) | `E-HRN-10…16` (`-13…16` via `CT-XT30U`), `-23` (`CT-PIN-HEADER-LINK`); caps `-34…37`; `-21`, `-22`, `-33` deleted (D-74) | declared, acknowledged |
| propulsion (E1) | `E-HRN-13…20`, `-24…27`, `-34…37` | declared, acknowledged |
| avionics (F3) | `E-HRN-23…32` | declared, acknowledged; avionics still lists the deleted `E-HRN-22` (merge_check WARN, F3 to drop it) |
| mechanisms (D6) | `E-HRN-28/29` | declared, acknowledged |

## Mass budget

| Item | g | Maturity |
|---|---|---|
| ESC power leads 16 AWG (R pair 39.2, L pair 31.1) | 70.3 | CALC |
| Phase extensions (0 if the factory leads reach) | 12.2 | EST |
| DShot 5.1 · servo (22 / 28 AWG) 9.3 · JST-GH cables + board-link ribbon 5.6 | 20.0 | CALC |
| XT30U × 4 (`HRN-113-*`) | 8.0 | EST |
| Fittings (JR, GH, pin headers, splices, grommets, ties, tape, sleeves, straws) | 17.3 | EST |
| **Total / allocation** | **127.7 / 129** (D-79) | `CHECKED` +1 % |

Not booked here: 10 AWG jumpers (PWR-002), cap legs (PWR-008), pack lead (PWR-001), servo's own lead (MEC-001).

## Open issues

1. Motor and ESC factory lead lengths unpublished: measure at `T-E1-MOTOR-RM`, then cut the extension (12 g back to
   A1 if they reach, D-48).
2. CoreWing pin-out: the manual (power `SPEC.md`, WB-01) now places S1–S11 + SBUS on a 3 × 12 field at one FC short
   edge (order S11 … S1, SBUS) and the GH ports on the FC edges; F3 updates the port points from it. Still open: the
   board-to-board link pitch and pin order (`BOARD-CHECK.md` step 4). `W-PMOD` is not a GH-6 lead: case S makes it a
   28 AWG ribbon on the board's own header; case U deletes it.
5. Done (R4): the UBEC rows are out of `team/F2/harness.py` and `WIRE-LIST.csv`, the XT30U are in. If
   `BOARD-CHECK.md` step 7 fails, the fallback UBEC needs its own zone (D2) and new feed rows.
6. Closed (D-74 follow-up): `CL-F2-SERVO-V` 5.75 V with 22 AWG servo + / − and 4 Vx + 3 GND in the link. No link
   option alone reaches 5.7 V inside D2's 10 × 3 mm under-pack channel (fill ≤ 0.40 admits at most a 22 AWG pair:
   5.66 V). Case U (no link cable) would give ≈ 5.85 V.
7. Closed by D-79 (harness 129 g, power 630 g).
8. The XT30U are drawn (`HRN-113-*`): 0 penetrations, nearest wires 0.3–0.6 mm (right signal leads). The left pair
   sits under the cradle: unplug it with the power frame lifted (4 screws). Thickness 5.2 mm is a listing figure:
   measure at `T-F2-WEIGH` and re-run the clearance if it is thicker.
3. JR recess in the wing core (CR-F2-14 to D1) and the shortened servo lead (CR-F2-15 to D6) need acceptance.
4. Downstream re-runs on the new routed ESC lengths: F1 `power.py` (CR-F2-13).

## How to verify

`T-F2-FIT` (dry fit before skinning), `T-F2-WEIGH`, `T-F2-CONT` (continuity, polarity, isolation, 10 N pull),
`T-F2-DSHOT` (bdshot error rate), `T-F3-I2C-SCAN`, `T-F1-WIRE-HEAT` on a routed groove sample, `T-F1-SERVO-STALL`,
`T-PWR-FIT` (jumpers), `T-F1-DROP` with the XT30U in the loop.
