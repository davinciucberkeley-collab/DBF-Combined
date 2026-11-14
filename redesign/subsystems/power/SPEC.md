# Power

Status: `MODELLED` (F1, revision PWR-R1 on params A1-R3, 2026-11-09; D-74 applied 2026-11-11: UBEC and fuse out
of every model, deck 56 mm). CAD `fusion/power.py`; graph and BOM from `make_power.py`; claims `power_claims.py` (15). Analysis behind the choices: `team/F1/POWER.md` (F1-R2).

## Purpose

Carry the 4S 6500 pack and get its current to four ESCs and a servo rail, measured and protected, with the pack plug
as the only field disconnect. Main disconnect is the **Amass AS150U** (XT60 fails 37.8 A continuous and 120 A
momentary, `CL-F1-AS150U-*`). Everything except the ESC caps is one screwed stack in the pod's left channel that
comes out as a unit (4 screws, four XT30U plugs at the side exits; D-74 removes the UBEC and its fuse).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Design current continuous / limited peak / momentary | 30.3 / 105 / 120 | A | `CL-F1-I-CONT`, `CL-F1-ILIM-WORST`, `params.json#electrical.peak_current_a` | `UNVERIFIED` |
| AS150U rating vs need, continuous / momentary | 70 vs 37.8 / 140 vs 120 | A | `CL-F1-AS150U-CONT`, `-BURST` | `UNVERIFIED` (maker sheet) |
| Main jumpers 10 AWG (cups → board 0.030, board → bars 0.050 per conductor) | 0.61 (budget 0.68) | mΩ | `CL-PWR-JUMPER-R` | `CHECKED` |
| Jumper rise above its terminals at 30.3 A | 0.5 (limit 10) | °C | `CL-PWR-JUMPER-RISE` | `CHECKED` |
| Output-jumper drop / two bends at 2 × OD | 1.29 | — | `CL-PWR-BEND` | `UNVERIFIED` (`ASM-PWR-BEND`) |
| Frame screw engagement in the M3 × 5.7 insert (min 4.5) | 5.5 | mm | `CL-PWR-ENGAGE` | `CHECKED` |
| Park bond reserve on a 50 N unplug (need 3) | 28 | — | `CL-PWR-PARK-RF` | `UNVERIFIED` (pull test) |
| GPS to nearest power item (≥ 0.10) | 0.138 | m | `CL-PWR-GPS-CLR` | `CHECKED` |
| Deck clear of the bus-bar joints (≥ 5) · deck inside the channel | 11.1 · 1.9 | mm | `CL-PWR-DECK-CLR`, `-CHANNEL-FIT` | `CHECKED` |
| Board inside `KO-PWR-BOARD` (≥ 0) · deck seat vs keep-out (≤ 0.5) · top z split / whole stack vs 0.0626 | 0 · 0 · 0.0486 / 0.0626 | mm, m | `CL-PWR-KO-FIT`, `-KO-SEAT`, `-KO-TOP-S`, `-KO-TOP-U` | `CHECKED` (geometry); board size `UNVERIFIED` |
| Servo rail: power-board servo BEC on the 6 V jumper, rating vs need (2 × 2 × 1.4 A stall) | 8 cont / 14 peak vs 5.6 | A | `CL-F1-SERVO-BEC-RATING` vs `CL-F1-SERVO-BEC-REQ`; CoreWing manual V2.1 p. 7; D-74 | `UNVERIFIED` (`BOARD-CHECK.md` step 7) |
| UBEC and its 5 A fuse | deleted from every model (D-74); fallback only if `BOARD-CHECK.md` step 7 fails (BOM gate X12) | — | `CL-F1-SERVO-BEC-RATING` | `PROPOSED` |
| Drop pack → LR ESC at the 100 A limiter, XT30U in the branch (5 % guideline, WB-11) | 5.28 (XT30U 0.40) | % | `CL-F1-DROP-PEAK`, `CL-F1-XT30U-DROP` | `UNVERIFIED` (`T-F1-DROP`) |
| Flying mass vs allocation | 622.4 vs 630 (D-79) | g | `CL-PWR-MASS` | `CHECKED` +1 % |

## Parts

| Id | Part | Where (x, m) | g | Status |
|---|---|---|---|---|
| `PWR-001` | Pack 4S 6500, own 10 AWG leads 0.10 m, AS150U pack half | bay −0.071 … 0.069; plug half in the park | 550 | `UNVERIFIED` mass |
| `PWR-002` | AS150U aircraft half + two 10 AWG main jumpers | cradle 0.002 … 0.031, left | 18.6 | `MODELLED` |
| `PWR-003` | CoreWing V2 power board ("PDB Board PLUS": V/I sense 64 A/V, three BECs; servo BEC on the 6 V jumper feeds the servos via the FC Vx rail), off the FC stack (case S) or under it (case U) | deck, pads aft at the window: −0.062 … −0.010 (52 mm) inside `KO-PWR-BOARD` | 28 `EST` (listing 11.4) | `UNVERIFIED` size |
| `PWR-004` | Bus board: FR4 strip, two tinned 8 AWG bars; four 16 AWG pigtails to XT30U females (bench, D-74) | PDB plate −0.041 … −0.005, under the deck | 7.3 | `MODELLED` |
| ~~`PWR-005`~~ | UBEC: **deleted** (D-74); id retired; fallback only via gate X12 | — | 0 (was 13) | — |
| `PWR-006` | Power frame (PETG): deck with a 56 × 34 mm board seat (= `KO-PWR-BOARD`), wire window, AS150U cradle, legs | −0.066 … 0.060, z 0.020 … 0.049 | 9.7 | `MODELLED` |
| ~~`PWR-007`~~ | 5 A fuse and holder: **deleted** with the UBEC (D-74); id retired | — | 0 (was 3.5) | — |
| `PWR-008-UR/UL/LR/LL` | 680 µF 25 V low-ESR cap at each ESC | half-fin face, x 0.127 … 0.147 | 4 × 2.2 | `MODELLED` |

Stack, bottom up (z, m): floor 0.0198 · bus board 0.0206 (bars to 0.0255) · bosses 0.0266 · 10 mm nylon spacers ·
deck 0.0366–0.0386 · power board to 0.0486. The AS150U sits on the deck plane, so its cups line up with the board
input pads; the output pair drops 24.8 mm through the 10 mm window to the bars. The four ESC pigtails leave the
bars through the tunnel under the cradle; the left pair's XT30U sit in the tunnel's outboard half (x 0.016–0.036),
the right pair's just inside the right exit. The two cradle legs are 10 mm forward of the cradle's aft end
(x 0.046–0.050, `leg_setback_m`) so the left pairs turn to their exit behind them.

## CoreWing V2 power board: what the documents settle (WB-01, BR-05)

Sources: CoreWing *F405 WING V2 User Manual V2.1* (Coolwing Technology; English machine translation on manuals.plus,
13 pp.: overview table p. 2, pin-out p. 3, PDB pins and jumpers p. 4, power logic p. 5, parameter table p. 7,
dimension drawing and box list p. 13) = **[M]**; ArduPilot *CoreWing F405 Wing V2 / Wing Mini V2* hardware page and
`hwdef/CoreWingF405WingV2/README.md` = **[AP]**; ReadyMadeRC product 87195 (the BOM's `A01` SKU) = **[RMRC]**.
Where a reseller disagrees with [M] and [AP], [M] wins.

| Question | Answer | Source | Settled? |
|---|---|---|---|
| Does the power board separate? | **Yes, by design.** Three PCBs: FC, "PDB Board PLUS", top plate / wireless-USB board. Assembly: PDB to FC "ensuring alignment of the pin headers and sockets", then the top board, M2 × 12 studs and M2 × 4 screws | [M] p. 2, p. 13 box list; [RMRC] weights per board | Yes |
| How do the boards connect? | **Board-to-board pin header + socket, not a cable.** About 20 contacts (the FC underside shows two 2 × 5 blocks at diagonal corners). PDB pin roles: VTX&CAM-BEC, FC-BEC (several), SERVO-BEC (4), GND (several), BATT_VOLT, BATT_CURR, GPIO1 (VTX power switch). **There is no JST-GH 6 power port**: `W-PMOD` as drawn (GH-6, Vbat/I/5 V/GND, no Vx) does not exist on this product. The "unsoldered pins" SKU leaves only the 3 × 12 PWM header and the 1 × 12 strips unsoldered, not the board-to-board link | [M] p. 3 (FC underside), p. 4 (PDB pin figure; "PDB boards cannot be interchanged" with SpeedyBee) | Roles yes; **pitch, count and exact pin order: measure** (`BOARD-CHECK.md` step 4) |
| Which board carries the outputs? | **The FC.** S1–S11 + SBUS on a 3 × 12 pad field along one short edge of the FC (rows signal / Vx / G; the SBUS column carries 4V5); PWM 12 = the LED pad. Vx reaches the FC header from the PDB's servo BEC through the board-to-board link | [M] p. 3, p. 7 ("12x: 11 to the header pins + 1 to the LED signal"); [AP] | Yes |
| Outline and holes | **PDB and FC both 52 × 32 mm** (PDB length includes its battery pads); stack 52 × 32 × 17 mm, 40 g with the wireless board. M2 holes (Ø 2 mm, Ø 4 mm pad) on a **30.5 × 26.5 mm** rectangle, 2.75 mm from the long edges, ≈ 10.5 mm from each short end. Not 30.5 × 30.5 | [M] p. 13 drawing; [AP] | Footprint yes; **PDB height (split case) not published: measure** (step 3) |
| Masses | PDB 11.4 g, FC 8.9 g, wireless board 4.2 g | [RMRC] | Listing only: weigh (step 2) |
| BECs | FC BEC **5.2 V, 4 A cont / 5 A peak**. Servo BEC **5 / 6 / 7.2 V by jumper, default 5 V, 8 A cont / 14 A peak**. VTX&CAM BEC 5 / 9 / 12 V by jumper, default 9 V, 2 A / 3 A. 4V5 pads via a diode, ≤ 2 A. Input 10–28 V (3–6S) | [M] p. 4–5, p. 7; [AP] | Yes. [RMRC] "4.9 V @ 4 A" and Banggood "4 A sustained" contradict [M] and [AP] |
| Where the team's 4.5 A came from | The SpeedyBee F405 Wing APP column of [M]'s comparison table: "sustained 4.5 A, peak 5.5 A". It is not the CoreWing figure | [M] p. 2 | Yes |
| Current and voltage sense | **90 A cont / 215 A peak**, 64 A/V in ArduPilot (158 in iNav); Vbat divider 10 k : 100 k, `BATT_VOLT_MULT` 11.05, `BATT_VOLT_PIN` 10, `BATT_CURR_PIN` 11. Banggood's "125 A peak" is wrong | [M] p. 7; [AP] | Yes; calibrate at `T-F1-SENSOR-CAL` |
| Battery / output pads | Six pads on one 32 mm short edge of the PDB: 3 − and 3 +; the drawing wires the battery to one + pad and two ESCs to the other two | [M] p. 4 drawing | **Which + pad is upstream of the shunt, and pad size: measure** (step 5) |
| Input capacitor | 470 µF 35 V supplied, "should be installed" at the battery pads | [AP]; [M] p. 13 box list | Yes |

### Servo-rail current budget (D-74)

| Load on the servo BEC (6 V) | Each | Count | Total | Source |
|---|---|---|---|---|
| Savox SH-0255MG+ stall at 6.0 V | 1.4 A | 2 | 2.8 A | retailer listings of the Savox sheet (1.2 A at 4.8 V, 1.4 A at 6.0 V); `CL-F1-SERVO-BEC-REQ` |
| Idle | 5 mA | 2 | 0.01 A | same |
| Other loads on Vx | none: the ESCs run on DShot without BEC leads, the RX / GPS / airspeed are on the FC 5 V rail | — | 0 | `WIRE-LIST.csv` |
| **Worst case, both stalled** | | | **2.8 A** | |
| Design case with F1's × 2 factor | | | **5.6 A** | `CL-F1-SERVO-BEC-REQ` |
| Servo BEC rating | | | **8 A cont / 14 A peak** → margin 43 % on the design case, 186 % on the real stall | [M], [AP] |
| FC 5 V rail: 2 × 0.87 A vs 4 A cont | | | margin 130 % | `CL-F3-5V-REQ`, [M] |

**Decision:** drop the UBEC `PWR-005` and its fuse `PWR-007`; the power board's servo BEC on the **6 V jumper**
feeds the servos (never 7.2 V: the SH-0255MG+ is a 4.8–6.0 V servo). The UBEC existed only because of the 4.5 A
SpeedyBee figure. A UBEC adds a part whose pod zone already overruns (CR-D2-27), a fused 20 AWG feed, the
"never in parallel" wiring rule and 16.5 g. The BOM's UBEC (`F05`) is also listed for 2–3S input on its link check,
so it would not run on this 4S pack. The design keeps it only as a fallback (gate X12) if `BOARD-CHECK.md` step 7
reads Vx < 5.8 V with two 2.2 Ω loads (≈ 5.4 A). The servo voltage at the far servo stays as F2 computed it,
through the board link and the harness servo leads: `CL-F2-SERVO-V` 5.75 V ≥ 5.7 with both servos stalled
(link 4 Vx + 3 GND, 0.10 V; servo + / − 22 AWG, 0.15 V).

### Power-board keep-out envelope (holds in both cases)

The pod CAD reserves one box on the power deck that fits the board whether it is used split or as the whole stack.
Aircraft frame, metres; deck top z 0.0386 (stack above).

| Zone | x | y | z | Contents |
|---|---|---|---|---|
| `KO-PWR-BOARD` (footprint) | **−0.066 … −0.010** (56 mm: 52 board + 2 + 2) | board centreline ± 0.017 (34 mm, same channel margin as today) | 0.0386 … **0.0626** (24 mm) | **S, split** (baseline): PDB alone on foam tape, ≤ 9 mm + 1.1 mm tape, top ≤ 0.0487; the 13.9 mm above it stay free. **U, whole stack**: PDB + FC (+ wireless board) 17 mm on four 5 mm gel cubes, + 2 mm strap and sway |
| `KO-PWR-PADS` | −0.010 … 0.000 (the existing 10 mm deck window) | as above | 0.0200 … 0.0626 | battery and output pads face aft; W-MAIN-1 / -2 (10 AWG) drop through the window to the bars |
| `KO-PWR-FWD` (U only) | −0.076 … −0.066 | as above | 0.0500 … 0.0626 | S-header JR pigtails and the GH plug bodies at the FC's forward short edge |
| `KO-PWR-SIDE` (U only) | −0.066 … −0.010 | 6 mm outboard of each long edge | 0.0500 … 0.0626 | GH plug bodies on the FC's long edges (RX, telemetry, I²C) |

Mounting: four M2 holes on 30.5 (x) × 26.5 (y) mm. Case S keeps the foam tape + tie on the deck (`E-PWR-02`); the
deck needs no M2 holes. Case U puts the stack on four gel cubes on the deck corners with a hook-and-loop strap
through two deck slots (F3's FC mount, `E-AVN-01`), not on screws. `KO-PWR-FWD` and `KO-PWR-SIDE` are reserved
only if `BOARD-CHECK.md` selects U; D2 checks now that nothing structural must go there (channel walls below z 0.050
next to the deck, or notched).

**Split link (case S).** `W-PMOD` becomes a 0.198 m (`CL-F2-PMOD-LEN`) 28 AWG ribbon with a male header of the measured pitch at each
end, plugged into the FC's and the PDB's own board-to-board contacts. Wire 10 (`ASM-F1-PMOD-CONDUCTORS`, the most the 10 mm under-pack channel takes at fill 0.40): FC-BEC × 1, SERVO-BEC × 4
(all four, 0.7 A each at the 2.8 A stall, 1.8 °C, `CL-F1-PMOD-SERVO-RISE`), GND × 3 (5.1 °C), BATT_VOLT, BATT_CURR. VTX&CAM-BEC and GPIO1 stay open (no VTX). Mass 2.2 g (+1.0 g on the
1.2 g GH-6 lead). Case U has no link cable.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-PWR-03` | `POD-002` bosses | 4 × M3×18 nylon + 0.5 mm washer, deck, 10 mm nylon spacer, brass insert; 5.5 mm engaged; 0.2 N·m | F1 (CR-F1-20 to C6) |
| `E-PWR-01` | `PWR-006` cradle | AS150U housing sanded and epoxied (1 400 mm²) + 1 tie; front wall takes the push | F1 |
| `E-PWR-02` / `-05` | deck / PDB plate | foam tape + 1 tie (board); tape (bus board). `E-PWR-04` (UBEC) and `-07` (fuse clip) deleted (D-74); D2 still acknowledges `E-PWR-04` (WARN) | F1 |
| `E-PWR-11…14` | `FIN-001-*` | cap foam-taped on the outboard face, clear of the ESC strap | F1, D3 acks |
| `E-POD-05`, `E-POD-12` (ack) | pod tray | straps, stops, crush block; thermal contact | D2, C3, E3 |
| `E-HRN-10…16`, `-23`, `-34…37` | harness | pack plug (field), jumpers, ESC leads (`CT-XT30U` plug per pair at the pod side exits, D-74), board-to-board link (`W-PMOD`, 10-way ribbon, case S only, `CT-PIN-HEADER-LINK`); `E-HRN-21`, `-22`, `-33` (fuse feed, UBEC rail) deleted (D-74) | F2 (CR-F1-18) |

## Mass budget

| Allocation | Pack | Non-pack | Total | Margin |
|---|---|---|---|---|
| 630 g (`params.json#mass.allocation_g.power`, D-79) | 550 `UNVERIFIED` | 72.4 (`CL-PWR-MASS-NONPACK`) | 622.4 | +7.6 g |

D-74 as modelled: UBEC −13.0 g, fuse −3.5 g, deck 42 → 56 mm and no fuse clip +0.7 g (frame 9.0 → 9.7 g):
non-pack 88.2 → **72.4 g**, power **−15.8 g** (638.2 → 622.4 g). The harness gains 4.8 g (XT30U, board-link
ribbon, 22 AWG servo leads; harness `SPEC.md`): D-79 moves 6 g of allocation from power to harness. The 11.4 g listing for the board, if the scale confirms it, gives back another 16.6 g.

## Open issues

| Issue | Owner |
|---|---|
| CoreWing power board: separation, outputs, BECs and footprint settled from the manual (above). Still to measure on arrival (`BOARD-CHECK.md`): PDB height, link pitch and pin order, which + pad is upstream of the shunt; then choose S or U | F1, F3 |
| Deck re-drawn to `KO-PWR-BOARD` (56 × 34 mm, x −0.066 … −0.010) by F1 (D-74, `CL-PWR-KO-*`); D2 reserves the keep-out in the pod CAD (nothing structural inside it up to z 0.0626) | D2 |
| Done (D-74): `PWR-005` / `PWR-007` out of `make_power.py`, `fusion/power.py`, `power_claims.py` and `team/F1/power.py`; F2 removed `W-FUSE-IN`, `W-UBEC-IN`, `W-UBEC-OUT` and added the four XT30U. Still pointing at the old parts (owners to re-run): D2 `pod_data.py` acknowledges `E-PWR-04`; F3 acknowledges `E-HRN-22` and carries `CL-F3-SERVO-BEC` 4.5 A; E3 `thermal.py` heats the pod with the UBEC. D6 `CL-D6-SERVO-SUPPLY` now limits on `CL-F1-SERVO-BEC-RATING` | D2, F3, E3 |
| AS150U and XT30U from reseller figures; open the Amass sheets; measure the unplug force | F1, I1 |
| Pack mass 503–680 g decides the gate | E2, A3 |
| Harness edges still in `edges-pending.json`; endpoints to move to the new stack | F2 (CR-F1-18) |

## How to verify

`python -I redesign/subsystems/power/make_power.py` → `python -I redesign/subsystems/power/power_claims.py` →
`python -I redesign/fusion/check.py` (power: 0 errors) → `python -I redesign/interfaces/merge_check.py`.
Bench: [`BOARD-CHECK.md`](BOARD-CHECK.md) (30 min, the day the board arrives, before the pod CAD freeze), `T-PWR-ARRIVAL`, `T-PWR-FIT`, `T-PWR-PARK-PULL`, `T-F1-DROP`, `T-F1-WIRE-HEAT`, `T-F1-PRECHARGE`.
