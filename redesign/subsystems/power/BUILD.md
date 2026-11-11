# Power: build notes for G4

Status: `PROPOSED` (F1, PWR-R1, 2026-11-09; build order rewritten 2026-11-11 for WB-02 / WB-03, D-74).
**One build order, shared with `harness/BUILD.md`:** every joint on the 8 AWG bars is made **on the bench, in free
air, before the bus board goes into the pod** (order B1–B7 below, the same table in both files). The ESC leads are
never soldered at the bars: each ESC pair ends in an XT30U plug just inside the pod side exit, and the bus board
carries four pigtails with the mating halves (WB-03). Inside the pod there are plugs, screws and two 10 AWG joints on
the power board's pads, nothing else. Bench work about 3 h plus 24 h cure. Before step 1:
[`BOARD-CHECK.md`](BOARD-CHECK.md) has passed (step 7 decides UBEC or no UBEC: D-74 builds without).

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

**STOP — LiPo.** Re-terminate packs in the LiPo bag area, one lead at a time, never both bare at once, fire bucket
and sand within reach (H3 procedure). Never solder on a pack above storage charge (3.8 V/cell).

| Tools (this subsystem) | Parts |
|---|---|
| 80–100 W iron with a chisel tip, 63/37 rosin solder, flux, helping hands; wire stripper 10–20 AWG; flush cutter; metal shear or hacksaw + file (FR4); 3.2 mm drill; PH1 screwdriver; multimeter with a milliohm range or 4-wire setup; heat gun; 120-grit paper, IPA; 30 min epoxy; luggage scale | `PWR-001` ×2 packs, `PWR-002` (AS150U ×5 pairs), `PWR-003`, `PWR-004` (FR4 + 8 AWG offcut), `PWR-006` printed, `PWR-008` ×4 (+1 spare), `PWR-101…106`, `HRN-113` (XT30U ×4 pairs + spares) |

## Steps

1. **Measure on arrival.** `BOARD-CHECK.md` (power board, 30 min) and `T-PWR-ARRIVAL`: calipers on an AS150U half
   (expect ≈ 29 × 22 × 14 mm), weigh every part, unplug force of a mated AS150U pair with a luggage scale.
   CHECK: numbers into `subsystems/power/params.json`; anything outside the keep-out (`SPEC.md`) → tell F1 and D2
   before printing the frame.
2. **Print `PWR-006`.** PETG, 0.2 mm, 100 % (plates are 2 mm), deck flat on the bed, 4 perimeters; the deck's board
   seat is `KO-PWR-BOARD` (56 × 34 mm, x −0.066 … −0.010; `CL-PWR-KO-SEAT`), no fuse clip; the two cradle legs
   10 mm forward of the cradle's aft end (x 0.046–0.050). Drill the four deck
   holes 3.4 mm and the two tie slots. CHECK: deck flat within 0.3 mm; the board sits pads-aft at the window with
   4 mm free ahead of it; AS150U half slides into the cradle by hand.
3. **Bus board `PWR-004`, bench, free air: B1–B5 above.** Strip 2 × 25 mm of 8 AWG, twist tight, tin solid for the
   bars; the pigtail lengths come from `WIRE-LIST.csv` (UR 0.193, LR 0.193, UL 0.046, LL 0.043 m incl. 10 mm loop).
   CHECK: > 1 MΩ between bars; polarity at every XT30U; each bar joint shiny, no bridging over the slot.
4. **AS150U aircraft half.** Solder the two 10 AWG `W-MAIN-1` jumpers (0.030 m + slack, red/black) into the cups;
   15 mm adhesive heat-shrink over each cup. Sand the housing sides and bottom 120 grit, wipe IPA, epoxy into the
   cradle with the cups at the front wall slots; one tie over it through the floor slots. **Cure 24 h** before any
   plug-in. CHECK: `T-PWR-PARK-PULL` 150 N for 10 s, no movement.
5. **Bus board into the pod (B6).** Foam tape on the PDB plate, centred between the two boss rows, bars up. Lay the
   four pigtails aft through the tunnel under the cradle in their layers (harness `SPEC.md` § Routing), tie them; the
   left pair's XT30U females sit in the tunnel's outboard half (x 0.016–0.036), the right pair's just inside the
   right exit. Mate the two left plugs (B7) now, before the frame goes on. CHECK: no pigtail under a boss or spacer.
6. **Frame on the bosses (`E-PWR-03`).** Thread the `W-MAIN-2` pair up through the deck window, four 10 mm nylon
   spacers on the bosses, frame on top, 4 × M3×18 nylon with a nylon washer, ≈ 9 turns each, snug (0.2 N·m),
   paint-pen witness. CHECK: deck clear of every bar joint (≥ 5 mm), no lead pinched under a spacer.
7. **Power board `PWR-003`.** Hold the board just above the deck at the hatch (the jumpers are its leash). Solder
   `W-MAIN-1` to the battery pads **upstream of the shunt** (`BOARD-CHECK.md` step 5) and `W-MAIN-2` to the output
   (ESC) pads, + bridged over two pads if one is too narrow; the supplied 470 µF 35 V cap on the battery pads,
   legs ≤ 10 mm. Form the output pair down through the window (bend radius ≥ 10 mm). Case S: foam-tape the board on
   the deck, one tie round board and deck. Case U: four gel cubes and the strap, then the FC and top board on the
   studs (F3). CHECK: no insulation whitening at the bends; loop resistance cup → bar ≤ 0.68 mΩ (`T-F1-DROP`).
8. **Servo rail.** Confirm the servo-BEC jumper is on **6 V** (set at `BOARD-CHECK.md` step 6) before any servo is
   plugged into the FC header. No UBEC, no fuse (D-74). CHECK: Vx 6.0 ± 0.1 V at the S5 header pins.
9. **ESC caps `PWR-008`.** At each ESC, cap leads ≤ 20 mm to the power pads (stripe = −), can laid along x on the
   outboard fin face 3 mm aft of the ESC pad, foam tape + one tape strip (harness step 5 solders them on the bench).
   CHECK: not under the ESC strap.
10. **Packs.** Re-terminate both packs to AS150U pack halves (leads cut to 0.10 m, ≥ 10 AWG), and build the
    AS150U-to-XT60 charge lead. CHECK: polarity on every plug; first plug-in slowly, hold at the first detent ≥ 0.5 s
    (pre-charge, `T-F1-PRECHARGE`).
11. **Close-out.** Mate the four ESC XT30U plugs (B7, harness step 8). `T-F1-DROP` with the plugs in the loop
    (LR branch ≈ 5.3 % at the 100 A limiter, a guideline per WB-11), `T-F1-SENSOR-CAL`, `T-F1-WIRE-HEAT`; weigh the
    stack (`CL-PWR-MASS-NONPACK` 72.4 g after D-74).

Service: the stack comes out as one unit with no desoldering: unplug the two right XT30U at the right exit, power-board tie, 4 screws, lift the frame, unplug the two left XT30U in the tunnel, peel the bus board off its tape. An ESC or lead fault is an XT30U unplug (WB-03). Field: only the pack plug (`E-HRN-10`).
4 screws, peel the bus board off its tape. An ESC or lead fault is an XT30U unplug at the exit (WB-03). Field: only
the pack plug (`E-HRN-10`).
