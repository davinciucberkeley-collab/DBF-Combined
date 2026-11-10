# F1 power distribution: summary

Status `PROPOSED`. Analysis F1-R2 (`team/F1/power.py`, 31 claims) + design PWR-R1 (`subsystems/power/`, 10 claims,
CAD `MODELLED`); nothing bench-tested. Details: `team/F1/POWER.md`, `subsystems/power/SPEC.md`, `BUILD.md`.

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Main disconnect | **Amass AS150U**, packs re-terminated; XT60 rejected | 70 A ≥ 37.8 A; 140 A ≥ 120 A (XT60 35 A, no ≥ 120 A rating) | `CL-F1-AS150U-CONT`, `-BURST` | `UNVERIFIED` (reseller figures) |
| Disconnect mount | aircraft half bonded in a printed cradle on the power frame | park bond RF 28 vs 3 | `CL-PWR-PARK-RF` | `UNVERIFIED` (pull test) |
| Layout | one screwed stack in the left channel: bus board on the PDB plate, frame on D2's 4 inserts, power board on the deck | channel margin 1.9 mm; deck 11 mm over the bar joints | `CL-PWR-CHANNEL-FIT`, `-DECK-CLR` | `CHECKED` |
| Main jumpers | **10 AWG**, ≤ 0.05 m (replaces 8 AWG 0.15 m) | 0.61 mΩ (budget 0.68); 0.5 °C over terminals | `CL-PWR-JUMPER-R`, `-RISE` | `CHECKED` |
| Distribution | shop-made bus board, two tinned 8 AWG bars | 4 ESC pairs + fuse feed | — | `MODELLED` |
| ESC leads | 16 AWG (F2 routes) | rise 9.2 °C | `CL-F1-ESC-RISE` | `MODELLED` |
| Sensing | CoreWing V2 power board (separated, `PWR-003`) | 90 / 215 A ≥ 38 / 120 A | `CL-F1-SENSOR-*` | `UNVERIFIED` (outline, CR-F1-21) |
| Protection | no propulsion fuse; 5 A fuse on the UBEC feed; 680 µF at each ESC | limiter worst 105 A < 140 A | `CL-F1-ILIM-WORST` | `MODELLED` |
| Servo rail | UBEC 6.0 V 8 A class | 5.2 A required > FC BEC 4.5 A | `CL-F1-SERVO-BEC-REQ` | `UNVERIFIED` |

## Mass

| Item | g | Status |
|---|---|---|
| Pack | 550 | `UNVERIFIED` (503–680 listed) |
| AS150U half + jumpers 18.6 · power board 28 · bus 7.3 · UBEC 13 · frame 9 · fuse 3.5 · caps 8.8 | 88.2 | `EST` |
| **Total vs 620 g allocation** | **638.2: `FAIL` −18.2 g** | CR-F1-19 moves the board's 28 g from avionics → 648 g, +9.8 g |

## Checks run (2026-11-09)

| Check | Result |
|---|---|
| `python -I redesign/subsystems/power/make_power.py` | 11 nodes, 10 edges, 638.2 g |
| `python -I redesign/subsystems/power/power_claims.py` | 10 claims; 9 pass (+11 % … +833 %), `CL-PWR-MASS` −3 % |
| `python -I redesign/fusion/check.py` | power module ok: 11 parts, 23 bodies, 1 joint, **0 errors**; WARNs = mass (CR-F1-19), D2/D3 acks (CR-F1-16, -22), unconnected until F2 declares the wires (CR-F1-18). Overall FAIL from mechanisms (in progress) |
| `python -I redesign/interfaces/merge_check.py` | 0 power errors; same power WARNs. Overall result moves with the partial aircraft (last run: 1 ERROR, aircraft CG x 0.058 with no wing modelled) |
| `python -I redesign/proofs/build_graph.py` | no power errors; build fails on other roles' drift |

## Open issues

| Issue | Owner |
|---|---|
| CoreWing power board separable? outline ≤ 42 × 32 × 9 mm | F3 (CR-F1-21) |
| Harness wires to re-point (W-PACK 31 mm off, W-MAIN, W-PMOD), fuse split, cap leads | F2 (CR-F1-18) |
| Pod acks and UBEC plate; C6 nylon stack; D3 cap acks | D2, C6, D3 (CR-F1-16, -17, -20, -22) |
| Amass sheet, UBEC datasheet, unplug force | F1, I1 (`T-PWR-ARRIVAL`) |

Change requests: `team/F1/CHANGE-REQUESTS.md` (CR-F1-01 … 22). Sources checked 2026-11-09: CoreWing F405 Wing V2
(https://ardupilot.org/plane/docs/common-CoreWingF405WingV2.html; getfpv stack listing); no AS150U drawing found.
