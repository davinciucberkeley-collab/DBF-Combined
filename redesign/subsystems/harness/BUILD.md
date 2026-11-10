# Harness — build steps

Lengths, gauges and ends: `WIRE-LIST.csv` (cut length includes the service loop). Route: `SPEC.md` § Routing and
`team/F2/fig-hrn-01-route.svg`. Do the wing grooves (steps 3–4) after D1 has bonded the spar and D3 the
through-core blocks and half-fins, and **before** the wing is skinned.

Tools: wire stripper, 60 W iron + 2.4 mm chisel tip, rosin-core solder, heat gun, flush cutter, cordless drill
(twisting), 3 mm ball-nose rotary bit with a depth stop, 8 mm brad-point drill, straightedge, tape measure,
multimeter, 0.1 g scale, label maker or marker sleeves.

| # | Step | Check after it |
|---|---|---|
| 1 | Weigh 1 m of each reel (16, 20, 26, 28 AWG) and log it (`T-F2-WEIGH`); re-run `harness.py` if > 10 % off `ASM-F2-WIRE-GPM`. | log filled |
| 2 | Cut every wire to `length_cut_m`; label both ends with its `wire_id`. Twist pairs with the drill: 16 AWG lay 25 mm, 28 AWG lay 15 mm; leave the groove section (`G` points) untwisted. | count 29 wires; lengths ± 5 mm |
| 3 | Mark the grooves on both wing surfaces from the spar-slot fore face: − at 4.5 mm, + at 9.5 mm, DShot at 14.5 mm ahead, from y ±0.086 to ±0.296 m; servo groove 17 mm aft of the slot. Rout to depth (power 3.1, signal 2.4, servo 1.6 mm) with the depth stop. | 3 mm foam wall to the slot everywhere |
| 4 | Drill P1 (Ø 8 mm, 45° outboard, upper mouth y ±0.092, x 0.0615) and the fin holes (Ø 8 mm at x 0.086, 10 mm off the skin, both half-fins each side); sand the P1 lips to R ≥ 12 mm; glue the straw and the printed grommets (CA). | 7 mm rod passes freely |
| 5 | Bench: solder the 16 AWG pairs and the 28 AWG DShot pairs to each ESC (remove factory power leads), add the 680 µF cap (leads ≤ 20 mm), adhesive heat-shrink. Cut the phase extension to (reach − measured factory leads) and solder it to the phase pads. | `T-F2-CONT` on each ESC |
| 6 | Strap the ESCs on their pads (E3: one strap, FET side out). Thread each ESC's leads through the fin hole inboard, lay them in the grooves (lower ones via P1), tape-tab every 100 mm. | no wire proud of the surface |
| 7 | Phase: splice to the motor leads, staggered 10 mm, heat-shrink each, 30 mm outer sleeve; tie to the collar tail; label the phase order (F4 rotation map). | lead ≥ 5 mm off the bell by hand-spin |
| 8 | Pod: route to the bus PDB along the left channel; right-side pairs across behind the aft stop (pairs stacked 8 mm); PET sleeve at the crossing and exits; solder to the bus pads. | polarity by colour; 10 N pull |
| 9 | Signals: FC pigtails (≤ 100 mm) to the JR row on the tie bar; DShot and servo extensions plugged and tied; RX, airspeed and power-board cables in the under-pack channel; GPS cable up the right wall, through the right leg bore (fit the GH housing after threading), grip, mast. | `T-F2-FIT` photo of every run |
| 10 | Skin the wing (G2). Full `T-F2-CONT` with the pack disconnected: every net < 0.1 Ω end to end, > 1 MΩ between nets. Then `T-F2-DSHOT` and `T-F3-I2C-SCAN`. | no fault; weigh the aircraft (A3) |
