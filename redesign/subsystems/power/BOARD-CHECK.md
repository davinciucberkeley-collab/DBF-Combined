# CoreWing F405 Wing V2: arrival bench check (WB-01 / BR-05)

Status: `PROPOSED` (2026-11-11). Owner F1 with F3. Run it **the day the board arrives**, before the pod CAD is
frozen (`D2`) and before anything is soldered. About 30 minutes. It closes `T-PWR-ARRIVAL` and `T-F3-ARRIVAL` for the
power board and decides two things: split or whole stack (keep-out envelope in `SPEC.md`), and UBEC or no UBEC
(D-74).

What the documents already settle is in `SPEC.md` § "CoreWing V2 power board: what the documents settle". This
check measures only what they do not settle, plus the ratings the design now relies on.

**Tools:** calipers, 0.1 g scale, multimeter (with a milliohm range or 4-wire set-up), phone camera, bench supply
14–17 V ≥ 3 A with a current limit (or a flight pack behind a smoke stopper), IR thermometer, USB-C cable and a
laptop with Mission Planner. **Dummy servo load** (the servos arrive with the December order): two 2.2 Ω ≥ 25 W
resistors (2.2 Ω ≈ 2.7 A at 6 V, about two stalled servos' worth each, so two of them load the rail to the 5.6 A design case) and a 2-pin JR lead to each, or a borrowed electronic load.

**Rules:** nothing powered until step 6. Do not connect an ESC BEC red wire to any Vx pin (manual, PDB page). Set
the servo-BEC jumper to 6 V **before** any servo or dummy load is plugged in: the Savox SH-0255MG+ is a 4.8–6.0 V
servo and the board can be set to 7.2 V.

## Steps

| # | Min | Do | Pass | If it fails |
|---|---|---|---|---|
| 1 | 2 | **Box contents.** Lay out and photograph: FC board, **PDB board ("PDB Board PLUS")**, top plate / wireless-USB board, 470 µF 35 V cap, M2 × 12 studs × 5, M2 × 4 screws × 10, M3 × 4 silicone rings × 5, 1 × 12 straight pins × 3, cables (GPS, VTX, CAM, DJI, USB extension). | PDB and cap present (the ReadyMadeRC "included" list names no PDB; the manual does) | PDB missing: stop, contact ReadyMadeRC the same day, tell I1. The pod CAD stays open |
| 2 | 3 | **Weigh** each board bare on the 0.1 g scale. | PDB ≤ 13 g, FC ≤ 10 g, wireless board ≤ 5 g (listing 11.4 / 8.9 / 4.2 g). Any value ≤ the 28 g `PWR-003` allowance passes for the pod | Log in `power/params.json` `board_mass_g` and `avionics/params.json` `fc_mass_g`; A3 re-runs the roll-up |
| 3 | 5 | **Outline (each board).** Calipers: length incl. battery pads, width, PCB thickness, tallest part on the top face, tallest part on the bottom face (incl. the board-to-board socket or pins), M2 hole centres and diameter, hole centre to each edge. Assemble FC + PDB with the supplied studs and measure the stack height. Photograph both faces of both boards on 5 mm grid paper. | PDB ≤ 53.0 × 33.0 mm, PDB height ≤ 9.0 mm (split case), stack ≤ 17.5 mm without the wireless board (whole-stack case), holes Ø 2.0–2.3 mm at 30.5 × 26.5 ± 0.3 mm, ~10.5 mm from each short end, 2.75 mm from each long edge | Outside the **keep-out envelope** (`SPEC.md`): give the measured box to D2 before the pod CAD freeze. Within it: nothing changes |
| 4 | 6 | **Board-to-board link.** Count the contacts (expected 20: two 2 × 5 blocks on the FC underside at diagonal corners in the manual's drawing), measure the pitch (2.54 / 2.0 / 1.27 mm) and the mated height. Unpowered, with the boards apart, map each PDB contact with the meter against the manual's PDB pin figure: GND (0 Ω to the battery − pads), SERVO-BEC (contacts shorted together), FC-BEC (shorted together), VTX&CAM-BEC, BATT_VOLT (≈ 100 kΩ class to battery +), BATT_CURR, GPIO1. Then FC side: Vx row of the S1–S11 header to the FC's SERVO-BEC contacts (0 Ω), the SBUS column's middle pin to 4V5. | Roles match the manual figure; Vx on the FC header reaches the SERVO-BEC contacts | A pin role differs: write the map into `harness/SPEC.md` (open issue 2) before F2 makes the split cable. If the pitch is 1.27 mm, the split cable is a bought IDC ribbon, not hand-soldered |
| 5 | 4 | **Battery pads and shunt.** Count the pads along the PDB short edge (manual drawing: 3 − and 3 +; one + is the battery input, two + feed ESCs). Pad width and length. 4-wire milliohm from the battery + pad to each ESC + pad, and between the two ESC + pads. | The battery + pad is identified: it reads a shunt (≈ 0.1–1 mΩ) to the ESC + pads, which read ≈ 0 to each other. Each pad ≥ 4 mm wide (10 AWG, OD 4.8 mm, lands on one pad or bridges two) | W-MAIN-1 (from the AS150U) goes to the pad **upstream** of the shunt; W-MAIN-2 (to the bus bars) to the ESC + pads, bridged. If no shunt reads between them, the sensor is on the − side: map the − pads the same way and land the wires to match |
| 6 | 3 | **Power-up, no load.** Stack assembled, bench supply 16.0 V, limit 0.3 A, to the battery pads. Measure at the pads: FC 5 V pads, 4V5, VTX 9 V, Vx on the S-header. Then power off, bridge the **servo-BEC jumper to 6 V**, power on, measure Vx again. | Idle input ≤ 0.25 A; 5.1–5.3 V; 9 V ± 0.2; Vx 5.0 ± 0.1 V at the default, then **5.9–6.1 V** on the 6 V jumper | Any rail out of range or idle > 0.25 A: stop, photograph, return the board under the 30-day warranty. Order the fallback (`F05` UBEC, gate X12) the same day |
| 7 | 5 | **Servo-BEC load (stall budget).** Plug the two 2.2 Ω dummy loads into S5 and S6 (signal pin unused). Supply 16 V, limit 3 A. Read Vx at the S5 header pins and the FC 5 V rail; 60 s; IR on the servo-BEC area. Each resistor takes ≈ 16 W: lay them on a metal plate, not on the bench mat. | Two loads (≈ 5.4 A total, about the 2 × 2 × 1.4 = 5.6 A design case): **Vx ≥ 5.8 V** at the header, FC 5 V ≥ 5.0 V, no reset, no BEC cut-out, board ≤ 70 °C after 60 s | Vx < 5.8 V or a cut-out: **keep the UBEC** (D-74 fallback): buy `F05` (gate X12, a 4S-input part), F1 names it and D2 gives it its own zone (CR-D2-27) |
| 8 | 2 | **Sense check.** USB to Mission Planner (CoreWingF405WingV2 firmware loaded at `T-F3-FW-LOAD`, or that step first). With the dummy loads on, read `BATT_VOLTAGE` and `BATT_CURRENT`. | Voltage within 0.1 V of the meter at the pads (`BATT_VOLT_MULT` 11.05). Current reads the supply's current within 0.3 A, zero offset ≤ 0.3 A with no load | Re-set `BATT_VOLT_MULT` / `BATT_AMP_OFFSET` now; full calibration stays `T-F1-SENSOR-CAL` |

Total about 30 minutes. Step 7 is repeated with the real servos stalled when they arrive (`T-F1-SERVO-STALL`): same
pass line, Vx ≥ 5.8 V with both servos held against their stops.

## Decisions it makes (write them down the same day)

| Question | Rule | Who writes it |
|---|---|---|
| Split or whole stack | **Split** (PDB on the deck, FC on gel in its own bay, `SPEC.md` option S) if step 4 shows a pitch the team can cable (2.54 or 2.0 mm) and step 3 passes. **Whole stack** (option U) on the deck if the link cannot be cabled or the split cable would exceed 0.18 m. Both fit the keep-out envelope | F1 + F3 in `power/SPEC.md` and `avionics/SPEC.md`; tell D2 |
| UBEC | Step 7 passes → no UBEC, no fuse (D-74 stands). Fails → fallback above | F1; I1 releases or keeps gate X12 |
| Pad map | Steps 4–5 → the pin and pad map goes into `harness/SPEC.md` and `WIRE-LIST.csv` (`W-PMOD`, `W-MAIN-1/2`) | F2 |
| Pod CAD freeze | All of steps 1–5 within the envelope → D2 may freeze | D2 |

Log the numbers in `power/params.json`, `avionics/params.json` and the photos in `team/F1/data/`.
