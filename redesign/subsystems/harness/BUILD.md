# Harness — build steps

Lengths, gauges and ends: `WIRE-LIST.csv` (cut length includes the service loop). Route: `SPEC.md` § Routing and
`team/F2/fig-hrn-01-route.svg`. Do the wing grooves (steps 3–4) after D1 has bonded the spar and D3 the
through-core blocks and half-fins, and **before** the wing is skinned. The power stack (F1 `subsystems/power/BUILD.md`)
is built and screwed in before step 8.

Tools: wire stripper, 60 W iron + 2.4 mm chisel tip, rosin-core solder, heat gun, flush cutter, cordless drill
(twisting), 3 mm ball-nose rotary bit with a depth stop, 8 mm brad-point drill, open-barrel crimper (JR), straightedge,
tape measure, multimeter, 0.1 g scale, label maker or marker sleeves.

| # | Step | Check after it |
|---|---|---|
| 1 | Weigh 1 m of each reel (16, 20, 26, 28 AWG) and log it (`T-F2-WEIGH`); re-run `harness.py` if > 10 % off `ASM-F2-WIRE-GPM`. | log filled |
| 2 | Cut every harness wire to `length_cut_m`; label both ends with its `wire_id`. Twist pairs with the drill: 16 AWG lay 25 mm, 28 AWG lay 15 mm, 20 AWG lay 20 mm; leave the groove section (`G` points) untwisted. | 28 harness wires (rows booked "harness"); lengths ± 5 mm |
| 3 | Mark the grooves on both wing surfaces from the spar-slot fore face: − at 4.5 mm, + at 9.5 mm, DShot at 14.5 mm ahead, from y ±0.086 to ±0.296 m; servo groove 17 mm aft of the slot, then D1's branch along \|y\| 0.285 to x 0.173. Rout to depth (power 3.1, signal 2.4, servo 1.6 mm). Cut the JR recess 18 × 10 × 5 mm at x 0.150–0.168 on the branch (CR-F2-14). | 3 mm foam wall to the slot everywhere |
| 4 | Drill P1 (Ø 8 mm, 45° outboard, upper mouth y ±0.092, x 0.0615) and the fin holes (Ø 8 mm at x 0.086, **22 mm off the skin**, every half-fin, D3 CR-D3-23); sand the P1 lips to R ≥ 12 mm; glue the 7 mm straw and the printed grommets (CA). Glue a 4 mm straw into each D1 servo lead hole (x 0.173–0.177). | 7 mm rod passes freely |
| 5 | Bench, each ESC: strip its factory power leads; solder the 16 AWG pair and the 28 AWG DShot pair to the pads from **below** (leads leave toward the wing); fold the 680 µF cap legs (sleeved) forward onto the same power pads, cap body in line aft of the ESC, legs ≤ 20 mm (11 mm cut); adhesive heat-shrink. Cut the phase extension to (reach − measured factory leads) and solder it to the phase pads. | `T-F2-CONT` on each ESC; cap polarity |
| 6 | Strap the ESCs on their pads (E3: one strap, FET side out), foam-tape the caps aft of them (F1 `E-PWR-11…14`). Thread each ESC's leads through the fin hole inboard, tie at the boss-tail lug, lay them in the grooves (lower ones via P1), tape-tab every 100 mm. | no wire proud of the surface |
| 7 | Phase: splice to the motor leads, staggered 10 mm, heat-shrink each, 30 mm outer sleeve; tie to the collar-tail lug; label the phase order (F4 rotation map). | lead ≥ 5 mm off the bell by hand-spin |
| 8 | Pod power: pairs in through the side exits, left channel forward under the cradle (tunnel) to the bus bars; right-side pairs across behind the aft stop (stacked 8 mm); PET sleeve at the crossing and exits; solder to the bars (+ y −0.050, − y −0.043). Fuse feed: 20 AWG from the bars to the fuse-holder pigtail, splice, holder into the frame clip; fused feed + − across the crossing to the UBEC input; UBEC output to the FC rail (JR). | polarity by colour; 10 N pull; fuse removed |
| 9 | Signals: FC pigtails (≤ 100 mm) to the JR row on the tie bar; DShot and servo extensions plugged and tied; RX, airspeed and power-board cables through the floor channel at x −0.0245, inboard of the RX; GPS cable up the right wall, through the right leg window and bore (fit the GH housing after threading), grip, mast. | `T-F2-FIT` photo of every run |
| 10 | Servos: shorten each servo's own lead to 40 mm, crimp a JR male (HRN-105), pass it up the lead-hole straw, plug into the harness JR in the recess, tape the bodies in, close the recess with a re-openable tape flap. | servo sweeps on the bench; plug reachable |
| 11 | Skin the wing (G2). Full `T-F2-CONT` with the pack disconnected: every net < 0.1 Ω end to end, > 1 MΩ between nets. Fit the 5 A fuse. Then `T-F2-DSHOT` and `T-F3-I2C-SCAN`. | no fault; weigh the aircraft (A3) |
