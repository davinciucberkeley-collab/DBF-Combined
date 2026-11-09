# F3 avionics hardware: summary

Status `PROPOSED`, F3-R1, 2026-11-09. Details are in `team/F3/AVIONICS.md` and the claims come from
`team/F3/avionics.py` (26 claims, 7 planned tests). Nothing has been bench-tested.

## Decisions

| Item | Decision | Key number | Claim | Status |
|---|---|---|---|---|
| Flight controller | **CoreWing F405 Wing APP V2** (BOM `A01`, $67.26); SpeedyBee F405 WING is the fallback | Plane 4.7.2 stable, QuadPlane on; bdshot on outputs 1–4; dual IMU | `CL-F3-FC-STABLE`, `CL-F3-BDSHOT-OUTS` | `PROPOSED` (firmware server checked 2026-11-09) |
| Airspeed | **MS4525DO** at 0x28 (RMRC, $59.99), replacing the MS5525 | MS5525 0x76 = baro 0x76 on the only I²C bus | `CL-F3-I2C-CLASH` 3/3 unique | `PROPOSED` |
| GPS / compass | HGLRC M100-5883 on the pod mast, **tilted 45° to the nose** | 0.154 m from the nearest power item; interference 0.075 at hover | `CL-F3-GPS-CLEAR`, `CL-F3-COMPASS-RATIO` | `UNVERIFIED` |
| FC mounting | gel pads, f_n ≈ 35 Hz; no header pins | transmissibility 0.20 at hover 1P (90 Hz) | `CL-F3-VIBE-T1P` | `UNVERIFIED` |
| Orientation | FC flat, arrow to the cruise nose, `AHRS_ORIENTATION` 0 | ArduPilot tailsitter rule | `SRC-F3-AP-TAILSITTER` | `CHECKED` (source) |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Compass interference, hover / 100 A limit (limit 0.3) | 0.075 / 0.247 | — | `CL-F3-COMPASS-RATIO`, `-LIM` | `UNVERIFIED` |
| Airspeed error at 16 m/s, RSS (limit 1.0; B1 asks 0.5) | 0.44 | m/s | `CL-F3-ASPD-ERR` | `UNVERIFIED` |
| 5 V load ×2 vs FC BEC | 0.87 vs 2.4 | A | `CL-F3-5V-REQ` | `UNVERIFIED` |
| FC dissipation (E3 assumed 2.0) | 1.73 | W | `CL-F3-FC-DISS` | `UNVERIFIED` |
| Current sensing vs need | 90 / 215 vs 37.8 / 120 | A | `CL-F3-SENSE-*` | `PROPOSED` |
| Servo BEC vs need | 4.5 vs 5.2: **FAIL**, UBEC stays | A | `CL-F3-SERVO-BEC` | `UNVERIFIED` |
| Avionics mass vs allocation | 78.5 vs 75: **FAIL** −3.5 g | g | `CL-F3-MASS` | `UNVERIFIED` (`EST`) |
| Cost change | $0 (the airspeed swap costs the same); microSD ≈ $6 if not in team stock | USD | `team/I1/BOM.csv` | `PROPOSED` |

## Checks run

| Check | Result |
|---|---|
| `python -I redesign/team/F3/avionics.py` | 26 claims; all margins ≥ +7 % except `CL-F3-MASS` (−5 %) and `CL-F3-SERVO-BEC` (−13 %, by design: it records why the UBEC stays) |
| `python -I redesign/proofs/build_graph.py` | no F3 errors. Warnings only: `AVN-*` parts not yet in any `interfaces.json`. The build still fails on drift in the A1, B1 and E2 scripts, which belongs to those roles |

## Open issues

| Issue | Owner |
|---|---|
| CoreWing hole pattern and stack layout are not published; measure on arrival before D2 prints | F3, D2 |
| No Lua on any F405: F4's Lua fallbacks are gone. An H743 board would add about $35 and take the reserve below $309 | F4, A1 |
| Loop areas, Earth field and the RMRC chip address are estimates or unlisted; the bench tests decide | F3, H1 |
| `subsystems/avionics/` (SPEC, parts.csv, interfaces.json, Fusion module) is not written yet; the part and edge tables are in AVIONICS.md §5 | F3 |

Change requests: `team/F3/CHANGE-REQUESTS.md` (CR-F3-01 … 11, to A1, F4, D2, F1, F2, I1, E3, A4, A2, H1/H2, B4).
