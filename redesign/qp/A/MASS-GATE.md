# Mass gate, concept A (scaled quad tailsitter), 2026-11-14 (updated D-183 / D-184)

Reproduce: `python -I mission_gate_a.py`. Labels: `V` vendor page, `EST` estimate, `—` unknown. Inputs: SIZING-A.md, BOARD.md s1 and C5, K09-L A2/A3 closure-round rules (`ASM-A3-MGA` growth by maturity, overrun 84 g of 2.6 kg = 3.2 %).

## 1. Verdict: keep 1.50 kg frozen; it is the weigh-in limit, not the design target (updated D-183 / D-184)

Physics now from `prop_a.py` (APC 9x4.5MR PER3 static data through the MN2212, x0.93 derate (BOARD R3), hot x0.97 on the sag case, cant 16 deg, `Q_M_SPIN_MAX` 0.90 required; `EST` until bench M1). The old SIZING-A scaling (fresh 2.82, sag 2.16 at 1.226 kg) is superseded.

| At | T/W fresh | T/W sag | Window (low 1.33 W, high 0.80 x T/W sag) uncapped | Window with the 0.90 cap |
|---|---|---|---|---|
| 1.381 kg (predicted + overrun) | 2.95 (2.50 capped) | 2.34 (1.98 capped) | +-16.8 % | **+-8.7 %** |
| 1.44 kg (target) | 2.83 (2.40) | 2.24 (1.90) | +-14.8 % | **+-6.6 %** |
| 1.50 kg (gate) | 2.71 (2.30) | 2.15 (1.82) | +-12.8 % | **+-4.5 %** |

| Limit | Largest mass (uncapped / 0.90 capped) |
|---|---|
| T/W fresh >= 2.0 | 2.035 / 1.727 kg |
| T/W sag >= 1.6 | 2.016 / **1.707 kg** |
| Transition window >= +-5 % (R2 floor) | 1.756 / **1.486 kg** |
| Hard landing (12.2 g on 6 mm crush, independent of mass) | no mass limit found; fin-tip foot load at 1.50 kg: 1.08 J, 147 N total `EST` |

The motor cannot exceed the 0.90 cap, so the capped column is the one to design to. At the gate T/W passes (fresh 2.30, sag 1.82) but **the capped window is +-4.5 %, just under the R2 floor**: +-5 % holds to 1.486 kg. Cant 16 deg costs 0.9 % of vertical thrust against 14 deg (cos 16 / cos 14 = 0.991). K09-L flew its design on +-2.5 % and was a crisis; C3's time-domain run replaces both edges.

So the gate stays 1.50 kg (C5: a change needs the board) and the design target stays:

- **Design target (predicted mass incl. growth + overrun): <= 1.44 kg.** Current roll-up **1,381 g** (s2-s4): **59 g under the target, 119 g under the gate**; capped window +-8.7 % at 1,381 g.
- **Gate 1.50 kg: as-built weigh-in.** Between 1.44 and 1.486 kg the capped window is still >= +-5 %; above 1.486 kg (to 1.50) the aircraft flies only if the C3 time-domain run shows >= +-5 % at the as-weighed mass.

## 2. Allocation per subsystem (basic g, delivered; rounded up)

| Subsystem | g | Maturity | Source |
|---|---|---|---|
| Wing (foam, CF spar, 2 elevons) | 220 | EST | SIZING-A |
| Fins (2, CFRP skins, pads) | 70 | EST | SIZING-A 36 g + board +30-40 g (CFRP ~27 g skin per fin) |
| Motors 4 x MN2212 with cables | 260 | DATASHEET | 65 g each, T-Motor page `V` |
| Props 4 x APC 9x4.5MR / MRP | 44 | DATASHEET | 11.06 g each, RMRC page `V` (D-183; was 32 g EST for 9545) |
| ESC: SpeedyBee 4-in-1 7.2 g (page `V`) + leads, caps | 20 | EST | BOM P04 |
| Pack 1 x Tattu 2300 4S | 270 | pack, 0 % | listing 270 g `V` (D-183b: not the CNHL 356 g) |
| Avionics (FC, GPS, RX, airspeed, wiring) | 110 | EST | RESTUDY |
| Servos + linkage | 30 | EST | RESTUDY |
| Motor cage / mounts, arm x1.2 | 135 | EST | RESTUDY 120 g + 15 g longer struts (D-184, WIND.md s2) |
| Hardware, tape, paint | 35 | EST | SIZING-A |
| **Basic** | **1,194** | | |

The 4-in-1 is only 7.2 g by its page; leads and capacitors are `EST` 20 g total, and if bidirectional DShot needs a different ESC (BOM P04 unverified) this line moves.

## 3. Growth by maturity (`ASM-A3-MGA`: EST 20 %, CALC 10 %, DATASHEET 5 %, CAD 5 %, WEIGHED 1 %, pack 0 %)

Growth = 44 (wing) + 14 (fins) + 13 (motors) + 2.2 (props) + 4 (ESC) + 22 (avionics) + 6 (servos) + 27 (cage) + 7 (hardware) = **139 g** (11.7 % of 1,194). Predicted **1,333 g**. Growth shrinks as items become CAD or WEIGHED; any item still EST at the CG breadboard (M5) is re-booked.

## 4. Build overrun line

3.2 % of the gate (K09-L ratio 84 / 2,600) = **48 g**, held unallocated for first-build adders: glue, paint, 16 deg cant hardware, wire, the first-flight CG lead. Named items are booked in the roll-up, not hidden in this line (A2 s2.2). Predicted + overrun = **1,381 g**; headroom to the gate **119 g (7.9 %)**, to the 1.44 kg design target **59 g**. If the CG lead is needed (s5), it comes out of the 59 g, not the overrun.

## 5. CG range target (cruise attitude, aft of the wing leading edge, chord 245 mm)

NP 40.7 mm (SIZING-A: 44.0 inviscid, -3.3 viscous `EST`); SM = (NP - CG) / c.

| Limit | CG mm | SM |
|---|---|---|
| Aft hard limit | 28.5 | 5 % (BOARD C4) |
| **Design target band** | **20 - 26** | 8.4 - 6.0 % |
| Predicted (pack ahead of LE by 20 mm; rest of aircraft 35.7 mm `EST`, arm mass assumed not to move it) | 24.8 | 6.5 % |
| Forward limit | 4.0 | 15 % `EST` |

Lateral CG within 5 mm (K09-L). The pack position is the knob: 20 mm of pack travel moves CG about 4 mm (SIZING-A s6: SM 6.6 -> 4.9 % for pack at the LE). C4: breadboard SM >= 5 % before the wing is cut; as-built outside 20-26 mm needs a pack move, not ballast. NP is `EST`: a CG breadboard on a knife edge (M5) plus the first flight's trim measure it.

## 6. What triggers a re-sit

Predicted mass > 1.44 kg; as-built > 1.50 kg (R3); sag T/W at the bench < 1.6 at the as-weighed mass (capped, 0.90); C3 window < +-5 %; bench yaw authority < 0.35 N m (0.30 reopens the 5 m/s card).
