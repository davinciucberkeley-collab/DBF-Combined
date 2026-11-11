# Harness — build steps

Lengths, gauges and ends: `WIRE-LIST.csv` (cut length includes the service loop). Route: `SPEC.md` § Routing and
`team/F2/fig-hrn-01-route.svg`. Do the wing grooves (steps 3–4) after D1 has bonded the spar and D3 the
through-core blocks and half-fins, and **before** the wing is skinned. **Build order shared with
`subsystems/power/BUILD.md` (WB-02, D-74):** each ESC power pair is cut at its XT30U station just inside the pod side
exit. The pod part (bars → XT30U, pigtail length in `WIRE-LIST.csv`) is a bus-board pigtail that F1 solders to the
bars on the bench (B3). The wing part (XT30U → ESC) is the lead below, soldered only at the ESC. No joint on the
bars is made inside the pod, and no ESC lead is soldered after it is routed.

### Bus-bar joints: one bench order (D-74, identical in `power/BUILD.md` and `harness/BUILD.md`)

Every joint on the 8 AWG bars is made on the bench, in free air, before the bus board goes into the pod. Nothing is
ever soldered to the bars inside the pod.

| # | Who | Bench step | Check |
|---|---|---|---|
| B1 | F1 | Shear the FR4 to 36 × 16 mm, file the 2 mm isolation slot, tin and solder one 8 AWG bar per rail (+ outboard, − inboard, marked red / black) | > 1 MΩ between bars |
| B2 | F2 → F1 | F2 cuts the four 16 AWG **pod pigtails** to the pigtail length in `WIRE-LIST.csv` (`W-PWR-*`, disconnect column: route bars → XT30U + 10 mm), labels them UR / UL / LR / LL and hands them over | lengths ± 5 mm |
| B3 | F1 | Solder the four pigtails to the bars (+ to + bar, − to − bar), leads leaving aft | shiny joints, no bridge over the slot |
| B4 | F1 | Solder the two 10 AWG `W-MAIN-2` jumpers (0.050 m) to the aft end of the bars | 4-wire mΩ jumper to bar |
| B5 | F1 | Solder an **XT30U female** (socket, live side) on each pigtail end, adhesive heat-shrink | polarity at every XT30U; > 1 MΩ between bars again |
| B6 | F1 | Only now: bus board into the pod (power step 5). Inside the pod there are plugs, screws and the two 10 AWG joints on the power-board pads (power step 7), nothing else | — |
| B7 | F2 | After the wing leads are routed: XT30U **male** on each ESC lead, mated with its pigtail at its station (`HRN-113-*`: right pair just inside the right exit, left pair in the tunnel under the cradle, reached before the frame goes down), body tied (harness step 8) | + red to + red; 10 N pull |

Tools: wire stripper, 60 W iron + 2.4 mm chisel tip, rosin-core solder, heat gun, flush cutter, cordless drill
(twisting), 3 mm ball-nose rotary bit with a depth stop, 8 mm brad-point drill, open-barrel crimper (JR), straightedge,
tape measure, multimeter, 0.1 g scale, label maker or marker sleeves.

| # | Step | Check after it |
|---|---|---|
| 1 | Weigh 1 m of each reel (16, 22, 28 AWG) and one mated XT30U pair (and measure its thickness, 5.2 mm assumed), and log them (`T-F2-WEIGH`); re-run `harness.py` if > 10 % off `ASM-F2-WIRE-GPM`. | log filled |
| 2 | Cut every harness wire to `length_cut_m`; split each `W-PWR-*` at its XT30U station (the pigtail length in the disconnect column goes to F1 for B2–B5; the rest is the wing lead here); label both ends with its `wire_id`. Cut the board-link ribbon `W-PMOD` (case S, 10 of the board-to-board contacts per power `SPEC.md` and the `BOARD-CHECK.md` step 4 map). Make each servo lead (`W-SRV-*`, `-P`) from 22 AWG red + black and a 28 AWG signal, laid flat (3.6 mm wide in the 4.0 mm groove). Twist pairs with the drill: 16 AWG lay 25 mm, 28 AWG lay 15 mm; leave the groove section (`G` points) untwisted; the ribbon stays flat. | 25 harness wires (rows booked "harness"); lengths ± 5 mm |
| 3 | Mark the grooves on both wing surfaces from the spar-slot fore face: − at 4.5 mm, + at 9.5 mm, DShot at 14.5 mm ahead, from y ±0.086 to ±0.296 m; servo groove 17 mm aft of the slot, then D1's branch along \|y\| 0.285 to x 0.173. Rout to depth (power 3.1, signal 2.4, servo 1.6 mm). Cut the JR recess 18 × 10 × 5 mm at x 0.150–0.168 on the branch (CR-F2-14). | 3 mm foam wall to the slot everywhere |
| 4 | Drill P1 (Ø 8 mm, 45° outboard, upper mouth y ±0.092, x 0.0615) and the fin holes (Ø 8 mm at x 0.086, **22 mm off the skin**, every half-fin, D3 CR-D3-23); sand the P1 lips to R ≥ 12 mm; glue the 7 mm straw and the printed grommets (CA). Glue a 4 mm straw into each D1 servo lead hole (x 0.173–0.177). | 7 mm rod passes freely |
| 5 | Bench, each ESC: strip its factory power leads; solder the 16 AWG pair and the 28 AWG DShot pair to the pads from **below** (leads leave toward the wing); fold the 680 µF cap legs (sleeved) forward onto the same power pads, cap body in line aft of the ESC, legs ≤ 20 mm (11 mm cut); adhesive heat-shrink. Cut the phase extension to (reach − measured factory leads) and solder it to the phase pads. Leave the pod end of the 16 AWG pair bare: its XT30U male goes on after threading (step 8). | `T-F2-CONT` on each ESC; cap polarity |
| 6 | Strap the ESCs on their pads (E3: one strap, FET side out), foam-tape the caps aft of them (F1 `E-PWR-11…14`). Thread each ESC's leads through the fin hole inboard, tie at the boss-tail lug, lay them in the grooves (lower ones via P1), tape-tab every 100 mm. | no wire proud of the surface |
| 7 | Phase: splice to the motor leads, staggered 10 mm, heat-shrink each, 30 mm outer sleeve; tie beside the collar-tail lug (outboard), lead clear of the tail wall; run over the pinch bolt and nut, second tie at the pinch ear; free runs ≤ 50 mm, no contact with the mount, bolt or nut; label the phase order (F4 rotation map). | lead ≥ 5 mm off the bell by hand-spin |
| 8 | Pod power (B7): the power stack is in (power steps 3–7, bus pigtails already routed: left pairs through the tunnel under the cradle, right pairs across aft of the strut ribs over the foot bridge, inboard of the right leg). Bring each ESC pair in through its side exit, PET sleeve on, solder the **XT30U male** on its end, mate it with that ESC's pigtail at its station (right pair just inside the right exit; the left pair was mated in the tunnel at power step 5, so the left leads are brought to it before the frame goes down) and tie the body in its lane (keyed: + red to + red). No UBEC, no fuse feed (D-74). | polarity by colour at each plug; 10 N pull; plug seated to the shoulder |
| 9 | Signals: FC pigtails (≤ 100 mm) to the JR row on the tie bar; DShot and servo extensions plugged and tied; RX and airspeed cables, and in case S the power-board link ribbon (`W-PMOD`, power `SPEC.md`), through the floor channel at x −0.0245, inboard of the RX; GPS cable up the right wall, through the right leg window and bore (fit the GH housing after threading), grip, mast. | `T-F2-FIT` photo of every run |
| 10 | Servos: shorten each servo's own lead to 40 mm, crimp a JR male (HRN-105), pass it up the lead-hole straw, plug into the harness JR in the recess, tape the bodies in, close the recess with a re-openable tape flap. | servo sweeps on the bench; plug reachable |
| 11 | Skin the wing (G2). Full `T-F2-CONT` with the pack disconnected: every net < 0.1 Ω end to end, > 1 MΩ between nets. Then `T-F2-DSHOT` and `T-F3-I2C-SCAN`. | no fault; weigh the aircraft (A3) |
