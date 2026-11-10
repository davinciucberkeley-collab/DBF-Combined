# Power: build notes for G4

Status: `PROPOSED` (F1, PWR-R1, 2026-11-09). Order: after the pod tray is bonded and its four PDB-plate inserts are
set (D2 BUILD); before the harness ESC leads are routed into the wing (F2). Bench work, about 3 h plus 24 h cure.

**STOP — LiPo.** Re-terminate packs in the LiPo bag area, one lead at a time, never both bare at once, fire bucket
and sand within reach (H3 procedure). Never solder on a pack above storage charge (3.8 V/cell).

| Tools (this subsystem) | Parts |
|---|---|
| 80–100 W iron with a chisel tip, 63/37 rosin solder, flux, helping hands; wire stripper 10–20 AWG; flush cutter; metal shear or hacksaw + file (FR4); 3.2 mm drill; PH1 screwdriver; multimeter with a milliohm range or 4-wire setup; heat gun; 120-grit paper, IPA; 30 min epoxy; luggage scale | `PWR-001` ×2 packs, `PWR-002` (AS150U ×5 pairs), `PWR-003`, `PWR-004` (FR4 + 8 AWG offcut), `PWR-005`, `PWR-006` printed, `PWR-007`, `PWR-008` ×4 (+1 spare), `PWR-101…106` |

## Steps

1. **Measure on arrival (`T-PWR-ARRIVAL`).** Calipers on an AS150U half (expect ≈ 29 × 22 × 14 mm), the CoreWing
   power board once separated from the FC stack (must be ≤ 42 × 32 × 9 mm with pads), the UBEC. Weigh every part.
   Unplug force of a mated AS150U pair with a luggage scale. CHECK: numbers into `subsystems/power/params.json`;
   anything larger → tell F1 before printing the frame.
2. **Print `PWR-006`.** PETG, 0.2 mm, 100 % (plates are 2 mm), deck flat on the bed, 4 perimeters. Drill the four
   deck holes 3.4 mm and the two tie slots. CHECK: deck flat within 0.3 mm; AS150U half slides into the cradle by
   hand; the fuse holder snaps into the clip.
3. **Bus board `PWR-004`.** Shear FR4 to 36 × 16 mm. File a 2 mm isolation slot along the length through the
   copper. Strip 2 × 25 mm of 8 AWG, twist tight, tin solid, solder one bar on each rail (+ outboard, − inboard,
   mark with red/black pen). CHECK: > 1 MΩ between bars; bars do not rock.
4. **AS150U aircraft half.** Solder the two 10 AWG jumpers (0.030 m + slack, red/black) into the cups; 15 mm adhesive
   heat-shrink over each cup. Sand the housing sides and bottom 120 grit, wipe IPA, epoxy into the cradle with the
   cups at the front wall slots; one tie over it through the floor slots. **Cure 24 h** before any plug-in.
   CHECK: `T-PWR-PARK-PULL` 150 N for 10 s, no movement.
5. **Bus board in the pod.** Foam tape on the PDB plate, centred between the two boss rows, bars up. Solder the
   four 16 AWG ESC pairs (F2 cut list) and the fuse holder's input pigtail to the bars, leads leaving aft.
   CHECK: polarity with the meter; each joint shiny, no bridging over the slot.
6. **Frame on the bosses (`E-PWR-03`).** Four 10 mm nylon spacers on the bosses, frame on top, 4 × M3×18 nylon
   with a nylon washer, ≈ 9 turns each, snug (0.2 N·m), paint-pen witness. CHECK: deck clear of every bar joint
   (≥ 5 mm), no lead pinched under a spacer.
7. **Power board `PWR-003`.** Solder the input jumpers (from the AS150U) to its battery pads and two 10 AWG
   jumpers (0.050 m) to its output pads first, form the output pair down through the window (bend radius ≥ 10 mm)
   and solder to the aft end of the bars. Then foam-tape the board on the deck, one tie round board and deck.
   CHECK: no insulation whitening at the bends; loop resistance cup → bar ≤ 0.68 mΩ (`T-F1-DROP`).
8. **Fuse and UBEC.** Snap the fuse holder (5 A fitted) into the clip under the cradle. UBEC on foam tape + 1 tie in
   the right channel zone, output set to 6.0 V before connecting any servo. CHECK: rail 6.0 ± 0.1 V on the bench.
9. **ESC caps `PWR-008`.** At each ESC, cap leads ≤ 20 mm to the power pads (stripe = −), can laid along x on the
   outboard fin face 3 mm aft of the ESC pad, foam tape + one tape strip. CHECK: not under the ESC strap.
10. **Packs.** Re-terminate both packs to AS150U pack halves (leads cut to 0.10 m, ≥ 10 AWG), and build the
    AS150U-to-XT60 charge lead. CHECK: polarity on every plug; first plug-in slowly, hold at the first detent ≥ 0.5 s
    (pre-charge, `T-F1-PRECHARGE`).
11. **Close-out.** `T-F1-DROP`, `T-F1-SENSOR-CAL`, `T-F1-WIRE-HEAT`; weigh the stack (`CL-PWR-MASS-NONPACK` 88 g).

Service: the stack comes out as one unit (power board tie, 4 screws, unsolder ESC leads at the bars). Fuse change
is a bench job. Field: only the pack plug (E-HRN-10).
