# Avionics build notes (for G4)

Status `PROPOSED` (F3-R2). Prerequisites: pod shell, tray and mast built and cured (pod `BUILD.md`); harness pigtails
per `subsystems/harness/WIRE-LIST.csv`. Positions are in `SPEC.md`; numbers in `params.json`.
Tools: soldering iron (fine tip), heat-shrink, flush cutters, calipers, 0.01 g scale, IPA + wipes, 5 min epoxy,
scalpel, 100 mm ruler, 50 g calibration mass, laptop with Mission Planner. No screws in this subsystem.

| # | Step | Detail | Check after |
|---|---|---|---|
| 1 | Arrival inspection (`T-F3-ARRIVAL`) | Weigh every part; caliper FC board, airspeed board with ports, RX, GPS, probe OD. Confirm the FC top board separates from the power board and runs on the supplied cable. Write measured values into `params.json`, re-run `team/F3/avn_data.py` | masses within 20 % of `parts.csv`; airspeed board ≤ 20.5 mm long (tie-post gap); if the stack does not separate, stop and tell F3/F1 (fallback in `team/F3/claims.avn_data.json`, `T-F3-ARRIVAL`) |
| 2 | Bench firmware (`T-F3-FW-LOAD`) | DFU-flash Plane stable `CoreWingF405WingV2`; microSD (FAT32) in; load F4's `K09L.param`; solder 100 mm signal pigtails (outputs 1–6, servo rail) with in-line JR male ends; heat-shrink every joint. No header pins | `Q_TAILSIT_ENABLE` visible; log file on SD; all pigtails pull-tested by hand |
| 3 | Gel cubes and sag test | Cut 4 cubes 5 × 5 × 5 mm from the 5 mm gel sheet. IPA on the FC plate and the board underside corners. Press one cube under each corner, 4 mm in from the edges, ≥ 18 °C, 30 s. Place the board between the end stops, arrow toward the pod nose (−x). Put 50 g on the board centre | sag 0.6–1.2 mm (calipers on the board edge): < 0.6 → use 4 mm cubes; > 1.2 → 6 mm cubes. Board 2 mm clear of both end stops, touching nothing but the cubes |
| 4 | FC retention strap | 10 mm hook-and-loop strap through the slots in both end stops, over the board, closed with 1–2 mm slack (a 1.5 mm hex key slides under it) | board lifts ≤ 2 mm before the strap catches; strap does not press the board |
| 5 | Airspeed sensor | Foam tape under the board; seat it between the two tie posts, ports up; one tie through the post slots over the board. Cut two silicone lines 40 mm, push on the sensor ports; label T (total, port P1) and S (static) | board does not move; lines not kinked |
| 6 | Receiver | Bind and flash FCC firmware first (F5). Foam tape; lay it crosswise on the avionics plate, 0.5 mm behind the aft tie post. Antenna A up the hatch tube, antenna B forward into the nose tube (F5's antenna lengths, CR-F3-15) | RX LED solid with the transmitter on; antenna elements beyond the tube ends |
| 7 | Pitot boom (bench, once) | Print the sleeve in PETG, 100 % infill, bore = measured probe OD + 0.1 mm, key flat up. Bond the probe with 5 min epoxy, root barbs flush with the sleeve end, static holes clear of glue; cure 1 h. Push a barbed coupler on each barb | shoulder square to the sleeve; total/static marked on the sleeve |
| 8 | Pitot boom (every set-up, field joint) | Flat up, push the sleeve into the nose socket until the shoulder sits on the collar; inside the hatch push the T and S lines onto the couplers. One wrap of PTFE tape on the sleeve if the pull-out is < 2 N | pull-out 2–5 N; blow on the tip: airspeed rises |
| 9 | GPS | Foam tape full face on the 45° mast pad, module arrow pointing down the pad toward the nose; one tie round module and pad; cable to the mast with one tie, 30 mm service loop at the mast base (F2). No steel screw, washer or nut within 50 mm | arrow toward the nose; nothing magnetic near (test with a small magnet on a string) |
| 10 | Connect | GPS (SERIAL5 + I2C), RX (SERIAL6), power-board link, airspeed I²C branch (F2 Y-splice), JR leads to ESC/servo extensions; tie within 20 mm of each plug | `T-F3-I2C-SCAN`: SPL06, QMC5883, MS4525 found; `T-F3-5V` ≤ 1.2 A |
| 11 | Calibrate | Accelerometer level in the cruise attitude (FC flat); compass with `COMPASS_AUTO_ROT 2` (expect `COMPASS_ORIENT` 36); airspeed zero with the tip covered; measure `INS_POS*` and `GPS1_POS*` from the CG mark | orientation in the HUD matches the aircraft in cruise and in hover |
| 12 | Tethered and flight tests | `T-F3-VIBE` (VIBE < 30 m/s², clip 0), `T-F3-COMPASSMOT` (≤ 30 %), `T-F3-HDOP` (standing, ≤ 1.2 in 3 min), then `T-F3-ARSPD-CAL` in the fixed-wing tune | results logged in `team/F3/claims.json` tests |

Transport: pull the pitot boom (couplers part), fit the PE tip plug, stow it in the prop tray slot (`E-TRN-21`).
After a crash: replace the gel cubes, re-check step 3 sag, re-seat the GPS tape.
Animation candidate (BRIEF rules): step 8, boom sliding into the socket and the couplers mating (one 4 s loop).
