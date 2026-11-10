# Power

Status: `MODELLED` (F1, revision PWR-R1 on params A1-R3, 2026-11-09). CAD `fusion/power.py`; graph and BOM from
`make_power.py`; claims `power_claims.py` (10). Analysis behind the choices: `team/F1/POWER.md` (F1-R2).

## Purpose

Carry the 4S 6500 pack and get its current to four ESCs and a servo rail, measured and protected, with the pack plug
as the only field disconnect. Main disconnect is the **Amass AS150U** (XT60 fails 37.8 A continuous and 120 A
momentary, `CL-F1-AS150U-*`). Everything except the UBEC and the ESC caps is one screwed stack in the pod's left
channel that comes out as a unit (4 screws).

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
| UBEC feed fuse · UBEC rail | 5 A · 6.0 V, 8 A class | — | `CL-F1-SERVO-BEC-REQ` 5.2 A | `UNVERIFIED` |
| Flying mass vs allocation | 638.2 vs 620 | g | `CL-PWR-MASS` | **`FAIL`** −3 % (CR-F1-19) |

## Parts

| Id | Part | Where (x, m) | g | Status |
|---|---|---|---|---|
| `PWR-001` | Pack 4S 6500, own 10 AWG leads 0.10 m, AS150U pack half | bay −0.071 … 0.069; plug half in the park | 550 | `UNVERIFIED` mass |
| `PWR-002` | AS150U aircraft half + two 10 AWG main jumpers | cradle 0.002 … 0.031, left | 18.6 | `MODELLED` |
| `PWR-003` | CoreWing V2 power board (V/I sense, 64 A/V), off the FC stack | deck −0.052 … −0.010 | 28 `EST` | `UNVERIFIED` size |
| `PWR-004` | Bus board: FR4 strip, two tinned 8 AWG bars | PDB plate −0.041 … −0.005, under the deck | 7.3 | `MODELLED` |
| `PWR-005` | UBEC 6.0 V 8 A class | right channel 0.044 … 0.085 | 13 | `UNVERIFIED` |
| `PWR-006` | Power frame (PETG): deck, wire window, AS150U cradle, legs, fuse clip | −0.053 … 0.060, z 0.020 … 0.049 | 9 | `MODELLED` |
| `PWR-007` | 5 A mini-blade fuse in an inline holder | clip under the cradle | 3.5 | `MODELLED` |
| `PWR-008-UR/UL/LR/LL` | 680 µF 25 V low-ESR cap at each ESC | half-fin face, x 0.127 … 0.147 | 4 × 2.2 | `MODELLED` |

Stack, bottom up (z, m): floor 0.0198 · bus board 0.0206 (bars to 0.0255) · bosses 0.0266 · 10 mm nylon spacers ·
deck 0.0366–0.0386 · power board to 0.0486. The AS150U sits on the deck plane, so its cups line up with the board
input pads; the output pair drops 24.8 mm through the 10 mm window to the bars. ESC leads and the fuse feed leave
the bars through the tunnel under the cradle.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-PWR-03` | `POD-002` bosses | 4 × M3×18 nylon + 0.5 mm washer, deck, 10 mm nylon spacer, brass insert; 5.5 mm engaged; 0.2 N·m | F1 (CR-F1-20 to C6) |
| `E-PWR-01` | `PWR-006` cradle | AS150U housing sanded and epoxied (1 400 mm²) + 1 tie; front wall takes the push | F1 |
| `E-PWR-02` / `-05` / `-04` | deck / PDB plate / tray | foam tape + 1 tie (board, UBEC); tape (bus board) | F1 |
| `E-PWR-07` | frame clip | fuse holder snapped in | F1 |
| `E-PWR-11…14` | `FIN-001-*` | cap foam-taped on the outboard face, clear of the ESC strap | F1, D3 acks |
| `E-POD-05`, `E-POD-12` (ack) | pod tray | straps, stops, crush block; thermal contact | D2, C3, E3 |
| `E-HRN-10…16`, `-21…23` + cap leads | harness | pack plug (field), jumpers, ESC leads, fuse feed, rail, GH-6 | F2 (CR-F1-18) |

## Mass budget

| Allocation | Pack | Non-pack | Total | Margin |
|---|---|---|---|---|
| 620 g (`params.json#mass.allocation_g.power`) | 550 `UNVERIFIED` | 88.2 (`CL-PWR-MASS-NONPACK`) | 638.2 | −18.2 g: the 28 g power board left `AVN-001` (F3); CR-F1-19 moves 28 g avionics → power (648 g, +9.8 g) |

## Open issues

| Issue | Owner |
|---|---|
| CoreWing power board outline: deck takes ≤ 42 × 32 × 9 mm; confirm it separates from the FC and runs on a cable | F3 (CR-F1-21) |
| AS150U and UBEC from reseller figures; open the Amass sheet; measure the unplug force | F1, I1 |
| Pack mass 503–680 g decides the gate | E2, A3 |
| Harness edges still in `edges-pending.json`; endpoints to move to the new stack | F2 (CR-F1-18) |

## How to verify

`python -I redesign/subsystems/power/make_power.py` → `python -I redesign/subsystems/power/power_claims.py` →
`python -I redesign/fusion/check.py` (power: 0 errors) → `python -I redesign/interfaces/merge_check.py`.
Bench: `T-PWR-ARRIVAL`, `T-PWR-FIT`, `T-PWR-PARK-PULL`, `T-F1-DROP`, `T-F1-WIRE-HEAT`, `T-F1-PRECHARGE`.
