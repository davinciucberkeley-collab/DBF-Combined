# F3 avionics hardware: summary

Status `PROPOSED`, F3-R3, 2026-11-10. Details are in `team/F3/AVIONICS.md`. The analysis claims come from
`team/F3/avionics.py` (28 claims, 7 tests). The CAD claims and `subsystems/avionics/{interfaces.json, parts.csv}` come
from `team/F3/avn_data.py` (9 claims, `T-F3-ARRIVAL`). Nothing has been bench-tested.

## F3-R3 changes

| Item | Change | Status |
|---|---|---|
| Harness edges `E-HRN-22`…`32` | Each one checked against the port, timer and I²C map, then acknowledged (AVIONICS.md §5.1) | `CHECKED` (paper) |
| Transport edge `E-TRN-21` | Acknowledged. New claims: stowed boom 0.115 m long and 10 mm wide, against a 220 × 25 mm slot | `MODELLED` |
| Radio edge `E-AVN-09` | Moved from `edges_pending` to `edges` because F5 now declares `GND-001` | `PROPOSED` |
| `T-F3-ARRIVAL` | Now also confirms which CoreWing board carries output pads 1–6 and Vx, and that Vx is not on the GH-6 link (CR-F1-29) | `PROPOSED` |

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Flight controller | **CoreWing F405 Wing APP V2**, top board on gel cubes. Its power board is F1's `PWR-003`. SpeedyBee F405 WING is the fallback | Plane 4.7.2 stable with QuadPlane; bdshot on outputs 1–4; dual IMU | `CL-F3-FC-STABLE`, `CL-F3-BDSHOT-OUTS` | `PROPOSED` |
| Airspeed | **MS4525DO** at 0x28 (RMRC) | baro 0x76, compass 0x0D/0x2C, airspeed 0x28: 3 of 3 unique | `CL-F3-I2C-CLASH` | `PROPOSED` |
| GPS / compass | HGLRC M100-5883 on the pod mast, **tilted 45° toward the nose** | 0.154 m from the nearest power item | `CL-F3-GPS-CLEAR` | `UNVERIFIED` |
| Port map | Out 1–4 motors LR/UL/LL/UR (DShot300 bidir), out 5/6 elevons L/R; SERIAL5 GPS, SERIAL6 CRSF | matches F2's `E-HRN-24`…`31` and F4's `motor_map` | `CL-F3-BDSHOT-OUTS` | `CHECKED` (paper) |
| Orientation | FC flat, arrow toward the cruise nose, `AHRS_ORIENTATION` 0 | ArduPilot tailsitter rule | `SRC-F3-AP-TAILSITTER` | `CHECKED` (source) |

## Key numbers

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Avionics mass, CAD roll-up, vs 45 g allocation | 36.48 (+19 %) | g | `CL-F3-MASS`, `CL-F3-AVN-CAD-MASS` | `UNVERIFIED` (`EST`) |
| I²C bus total, FC → GPS + Y-branch to airspeed (limit 0.5) | 0.461 | m | `CL-F2-I2C-LEN` (F2) | `MODELLED` |
| Pitot boom stowed, length / width (slot 220 / 25) | 115 / 10 | mm | `CL-F3-BOOM-STOW-L`, `-W` | `MODELLED` |
| Compass interference at hover / at the 100 A limit (limit 0.3) | 0.075 / 0.247 | — | `CL-F3-COMPASS-RATIO`, `-LIM` | `UNVERIFIED` |
| Mount transmissibility at hover 1P (limit 0.3) | 0.21 | — | `CL-F3-VIBE-T1P` | `UNVERIFIED` |
| Airspeed error at 16 m/s, RSS (limit 1.0; B1 asks 0.5) | 0.45 | m/s | `CL-F3-ASPD-ERR` | `UNVERIFIED` |
| 5 V load ×2 vs FC BEC | 0.87 vs 2.4 | A | `CL-F3-5V-REQ` | `UNVERIFIED` |
| Servo BEC vs F1's need | 4.5 vs 5.6: **FAIL**. This records why the UBEC stays | A | `CL-F3-SERVO-BEC` | `UNVERIFIED` |

## Checks run (2026-11-10)

| Check | Result |
|---|---|
| `python -I redesign/team/F3/avn_data.py`, then `--check` | interfaces.json and parts.csv regenerated with no differences; 36.48 g, CG (−0.022, 0.001, 0.062) m |
| `python -I redesign/team/F3/avionics.py` | 28 claims; all margins ≥ +7 % except `CL-F3-SERVO-BEC`, which is −20 % by design |
| `python redesign/interfaces/merge_check.py --strict` | **0 avionics warnings** (there were 12 one-sided ones, plus 1 from `E-AVN-09`). The build still fails on 2 mass warnings, fins (435 > 418 g) and propulsion, which F3 does not own |
| `python -I redesign/proofs/build_graph.py` | No F3 errors. It still fails on DRIFT in the A3, A5, B1–B3, C1–C6, D5, E3, H1 and J1 scripts, which belong to those roles |

## Open issues

| Issue | Owner |
|---|---|
| Not published: CoreWing hole pattern, whether the output pads and Vx are on the top board or the power board, and the pin-outs. Check at `T-F3-ARRIVAL`; if they are on the power board, F2 re-ends `E-HRN-22` and `-24`…`-29` on `PWR-003` | F3, F2, F1 |
| No Lua on any F405, so F4's Lua fallbacks are not available | F4 |
| Loop areas, Earth field and the RMRC chip address are estimates; bench tests decide | F3, H1 |

Change requests: `team/F3/CHANGE-REQUESTS.md` (CR-F3-01 … 23).
