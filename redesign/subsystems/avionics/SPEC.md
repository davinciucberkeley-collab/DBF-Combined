# Avionics

Status: `MODELLED` (F3, revision F3-R2 on params A1-R3, 2026-11-09). CAD `fusion/avionics.py`; masses, CGs,
`interfaces.json` and `parts.csv` from `team/F3/avn_data.py`; analysis `team/F3/avionics.py` (claims in
`team/F3/claims.json`, `claims.avn_data.json`). Every station is read from D2's pod (`pod.py#layout()`).

## Purpose

Fly ArduPilot Plane stable as a quad tailsitter: flight controller, GPS + compass, ELRS receiver (control and
telemetry), airspeed sensor with a pitot that stays out of the prop wash, logging. All on the pod tray and mast;
the FC is vibration-isolated; nothing needs a tool in the field except plugging in the pitot boom.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Firmware | Plane 4.7.x stable, `CoreWingF405WingV2`, `Q_TAILSIT_ENABLE 1` | — | `CL-F3-FC-STABLE` | `CHECKED` (server, 2026-11-09) |
| Avionics mass (CAD) vs allocation | 36.5 vs 80 | g | `CL-F3-AVN-CAD-MASS`, `params.json#mass` | `UNVERIFIED` (EST) |
| Avionics CG (x, y, z) | (−0.020, 0.001, 0.062) | m | `CL-F3-AVN-CG-X/-Y` | `MODELLED` |
| FC mount: f_n vertical / lateral | 35.6 / 20.6 | Hz | `CL-F3-VIBE-FN`, `-FN-LAT` | `UNVERIFIED` (gel E) |
| Transmissibility at hover 1P (90 Hz) | 0.21 (limit 0.30) | — | `CL-F3-VIBE-T1P` | `UNVERIFIED` (`T-F3-VIBE`) |
| Gel-cube sag under 50 g (bench gate) | 0.82 (accept 0.6–1.2) | mm | `CL-F3-PAD-SAG` | `UNVERIFIED` |
| Pitot tip; prop-induced error worst / cruise | (−0.195, −0.046, 0.045); 1.72 / 0.27 | m; % | `params avionics.pitot_tip_xyz_m`, `CL-B4-PITOT`, `-CRUISE` | `PROPOSED` |
| Airspeed error at cruise, RSS (limit 0.5) | 0.45 | m/s | `CL-F3-ASPD-ERR` | `UNVERIFIED` |
| Pitot line path (cut 40 mm, limit 60) | 18 | mm | `CL-F3-PITOT-LINE` | `MODELLED` |
| GPS tilt toward the nose · to nearest power item | 45 · 0.154 | ° · m | `CL-F3-GPS-TILT-CAD`, `CL-F3-GPS-CLEAR` | `MODELLED` |
| Compass interference hover / 100 A (limit 0.3) | 0.075 / 0.247 | — | `CL-F3-COMPASS-RATIO`, `-LIM` | `UNVERIFIED` |
| I²C bus: baro 0x76, compass 0x0D/0x2C, airspeed 0x28 | 3 of 3 unique | — | `CL-F3-I2C-CLASH` | `PROPOSED` |
| 5 V load ×2 vs FC BEC | 0.87 vs 2.4 | A | `CL-F3-5V-REQ` | `UNVERIFIED` |

## Parts

| Id | Part | Mass g | Where (cruise frame) | Mount |
|---|---|---|---|---|
| `AVN-001` | CoreWing F405 Wing APP V2, FC top board + wireless board | 12.0 | right channel, (−0.010, 0.046), arrow −x | 4 gel cubes 5 mm + slack strap |
| `AVN-002` | HGLRC M100-5883 GPS + compass | 7.73 | mast pad (0.075, 0, 0.178), 45° to the nose | foam tape + 1 tie |
| `AVN-003` | RadioMaster RP3 V2 ELRS RX (CRSF, telemetry 1:4) | 4.6 | left channel, crosswise behind the aft tie post | foam tape |
| `AVN-004` | RMRC MS4525DO board + 2 silicone lines 40 mm | 4.5 | left channel between the tie posts, ports up | foam tape + 1 tie |
| `AVN-005` | Pitot boom: Ø4 probe in a printed Ø6 keyed sleeve, shoulder, 2 couplers | 4.8 | pod nose socket, left channel | plug-in (field joint) |
| `AVN-006` | 4 gel cubes, foam tape, 3 ties, 10 mm FC strap | 2.4 | under the FC | — |
| `AVN-007` | microSD 16–32 GB | 0.4 | FC fore-edge slot | slot + tape |

The CoreWing power board (`PWR-003`, ~28 g EST) is split from the FC and hard-mounted on the PDB plate: the 8 AWG
main leads would otherwise short the FC's isolation. Its mass and station belong to power (CR-F3-13).

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-AVN-01` / `-07` / `-10` | `POD-002` FC plate | gel cubes between D2's end stops; strap through stop slots; heat by convection | F3, C6, E3 |
| `E-AVN-02` | `POD-005` mast pad | foam tape on the 45° pad, no steel within 50 mm | F3 |
| `E-AVN-03` / `-04` | `POD-002` avionics plate | foam tape; airspeed located by the tie posts + 1 tie | F3 |
| `E-AVN-05` | `POD-006` socket | keyed plug-in, shoulder on the collar; drag and hover gravity seat it | F3, D2, C6 |
| `E-AVN-06` | `AVN-004` | two silicone lines; couplers part when the boom is pulled | F3 |
| `E-AVN-08` | `AVN-001` | card slot | F3 |
| `E-AVN-09` (pending `GND-001`) | transmitter | ELRS 2.4 GHz, CRSF 420 kbaud | F5 |
| `E-HRN-22…32` | FC, GPS, RX, airspeed | harness (F2) owns every wire; connector points in `ASM-F3-PORTS` | F2 |

## Open issues

| Issue | Owner |
|---|---|
| CoreWing stack split (FC top board cabled to the power board) not confirmed; FC mass 12 g EST | F3 on arrival (`T-F3-ARRIVAL`) |
| D2: tie-post gap +1 mm, avionics plate +4 mm aft, strap slots in the FC end stops, key flat in the socket bore, ack `E-AVN-07/-10` | D2 (CR-F3-12) |
| Stock RP3 antennas (65 mm) do not reach the hatch tube top or the nose tube | F5 (CR-F3-15) |
| Gel modulus is a class value; the 50 g sag test sets the cube size | F3 |
| Pod group floats in `check.py` until the wing module exists; `AVN-005` vs box wall until D7 declares `E-TRN-21` | D1, D7 |

## How to verify

`python -I redesign/team/F3/avn_data.py`, `python -I redesign/team/F3/avionics.py`, `python -I redesign/fusion/check.py`
(avionics row `ok`, 0 errors from avionics), `python -I redesign/interfaces/merge_check.py`. Bench: `T-F3-ARRIVAL`
(weigh, measure), `T-F3-FW-LOAD`, `T-F3-I2C-SCAN`, `T-F3-5V`, 50 g sag; tethered: `T-F3-VIBE`, `T-F3-COMPASSMOT`,
`T-F3-HDOP`; flight: `T-F3-ARSPD-CAL`.
