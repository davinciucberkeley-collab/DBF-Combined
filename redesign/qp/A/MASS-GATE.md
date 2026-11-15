# Mass gate, concept A (scaled quad tailsitter), 2026-11-14 (updated D-183 / D-184; QP-4 one-truth fold-in of QP-3 BOARD s1 item 10 and D-185, 2026-11-15)

Reproduce: `python -I mission_gate_a.py`. Labels: `V` vendor page, `EST` estimate, `—` unknown. Inputs: SIZING-A.md, BOARD.md s1 and C5, K09-L A2/A3 closure-round rules (`ASM-A3-MGA` growth by maturity, overrun 84 g of 2.6 kg = 3.2 %).

QP-4 changes (BOARD QP-3 s1 item 10, s3 D-185, s4): structure frozen at **473 g** (wing 191 / fins 119 / cage 122 / hardware 40; any growth needs the board); predicted mass rolls up to **1,396 g** (CAD itemised: 1,392 g, CAD s4; the 4 g is CAD's lower hardware and cage numbers); CG is the CAD's 16.2 mm, not 24.8 mm; the pack moves aft to give 20-24 mm (s5).

## 1. Verdict (superseded by s8, D-190: the weigh-in gate is now **1.47 kg**; the tables below are at cant 16 and 1.50 kg, kept as the record)

Physics now from `prop_a.py` (APC 9x4.5MR PER3 static data through the MN2212, x0.93 derate (BOARD R3), hot x0.97 on the sag case, cant 16 deg, `Q_M_SPIN_MAX` 0.90 required; `EST` until bench M1). The old SIZING-A scaling (fresh 2.82, sag 2.16 at 1.226 kg) is superseded.

| At | T/W fresh | T/W sag | Window (low 1.33 W, high 0.80 x T/W sag) uncapped | Window with the 0.90 cap |
|---|---|---|---|---|
| 1.396 kg (predicted + overrun) | 2.91 (2.47 capped) | 2.31 (1.96 capped) | +-16.3 % | **+-8.1 %** |
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

- **Design target (predicted mass incl. growth + overrun): <= 1.44 kg.** Current roll-up **1,396 g** (s2-s4): **44 g under the target, 104 g under the gate**; capped window +-8.1 % at 1,396 g.
- **Gate 1.50 kg: as-built weigh-in.** Between 1.44 and 1.486 kg the capped window is still >= +-5 %; above 1.486 kg (to 1.50) the aircraft flies only if the C3 time-domain run shows >= +-5 % at the as-weighed mass.

## 2. Allocation per subsystem (basic g, delivered; rounded up)

| Subsystem | g | Maturity | Source |
|---|---|---|---|
| Wing (foam, 12x10 CF spar, 2 elevons y 0.04-0.34) | 191 | EST | STRUCTURES iter. 2; frozen D-185 |
| Fins (2: 16x14 tube + 3 mm XPS fairing + 14x12 ribs + feet) | 119 | EST | STRUCTURES iter. 2; frozen D-185 (CFRP skin dropped, R04 removed) |
| Motors 4 x MN2212 with cables | 260 | DATASHEET | 65 g each, T-Motor page `V` |
| Props 4 x APC 9x4.5MR / MRP | 44 | DATASHEET | 11.06 g each, RMRC page `V` (D-183; was 32 g EST for 9545) |
| ESC: SpeedyBee 4-in-1 7.2 g (page `V`) + leads, caps | 20 | EST | BOM P04 |
| Pack 1 x Tattu 2300 4S | 270 | pack, 0 % | listing 270 g `V` (D-183b: not the CNHL 356 g) |
| Avionics (FC, GPS, RX, airspeed, wiring) | 110 | EST | RESTUDY |
| Servos + linkage | 30 | EST | RESTUDY |
| Motor cage (12x10 arms + bridge + V struts, arm x1.2) | 122 | EST | STRUCTURES iter. 2; frozen D-185 |
| Hardware, tape, paint | 40 | EST | STRUCTURES iter. 2; frozen D-185 |
| **Basic** | **1,206** | | structure 473 g (191 + 119 + 122 + 40 = 472, rounding in STRUCTURES) |

The 4-in-1 is only 7.2 g by its page; leads and capacitors are `EST` 20 g total, and if bidirectional DShot needs a different ESC (BOM P04 unverified) this line moves.

## 3. Growth by maturity (`ASM-A3-MGA`: EST 20 %, CALC 10 %, DATASHEET 5 %, CAD 5 %, WEIGHED 1 %, pack 0 %)

Growth = 38.2 (wing) + 23.8 (fins) + 13 (motors) + 2.2 (props) + 4 (ESC) + 22 (avionics) + 6 (servos) + 24.4 (cage) + 8 (hardware) = **141.6 g** (11.7 % of 1,206). Predicted **1,348 g**. (D-185 freezes the structure lines; the 20 % EST growth stays booked on them until the parts are weighed.) Growth shrinks as items become CAD or WEIGHED; any item still EST at the CG breadboard (M5) is re-booked.

## 4. Build overrun line

3.2 % of the gate (K09-L ratio 84 / 2,600) = **48 g**, held unallocated for first-build adders: glue, paint, 16 deg cant hardware, wire, the first-flight CG lead. Named items are booked in the roll-up, not hidden in this line (A2 s2.2). Predicted + overrun = **1,396 g**; headroom to the gate **104 g (6.9 %)**, to the 1.44 kg design target **44 g**. The CAD itemised roll-up gives 1,392 g (CAD s4). Any CG ballast comes out of the 44 g, not the overrun.

## 5. CG range target (cruise attitude, aft of the wing leading edge, chord 245 mm; BOARD QP-3 s4)

NP 40.7 mm (SIZING-A: 44.0 inviscid, -3.3 viscous `EST`); SM = (NP - CG) / c.

| Limit | CG mm | SM |
|---|---|---|
| Aft hard limit | 28.5 | 5 % (BOARD C4) |
| **Design band (kept)** | **20 - 26** (target 20-24) | 8.4 - 6.0 % |
| **CAD as drawn** (pack centre x -20 mm; CAD s4, basic 1,204.6 g) | **16.2** | 10.0 % |
| After the pack move to x <= -3 mm (+3.8 mm, `CALC`: 270 g x 17 mm / 1,204.6 g) | 20.0 | 8.4 % |
| Forward limit | **withdrawn** (was 4.0 mm) until the as-drawn SITL run sets one (BOARD s4) | |

The earlier 24.8 mm prediction assumed the rest of the aircraft at 35.7 mm; the CAD contradicts it (motors and props at x -99 / -121 mm) and that estimate is withdrawn. Ruling: **move the pack aft (centre from -20 to <= -3 mm) and give the tray a +-10 mm slot** so the M5 weigh-in trims CG without ballast. Optional second knob, only with a modes re-run: cage plane 10 mm aft (+3.3 mm; prop plane 121 -> 111 mm). SITL flew SM 6.5 % (CG 24.8); the drawn aircraft is SM 10.0 %; every transition pass in SITL-FLIGHT is at the old CG, so the as-drawn re-run is required before the wing is cut. Lateral CG within 5 mm. NP is `EST`: the CG breadboard on a knife edge (M5, M6) measures it.

## 6. What triggers a re-sit

Predicted mass > 1.44 kg; structure above 473 g (any growth needs the board, D-185); as-built CG outside 20-26 mm (A-P4); as-built > 1.50 kg (R3); sag T/W at the bench < 1.6 at the as-weighed mass (capped, 0.90); C3 window < +-5 %; bench yaw authority < 0.35 N m (0.30 reopens the 5 m/s card).

## 7. QP-4 FIXES2 update (2026-11-15; supersedes the QP-3 tables above where they differ; full text `review/QP-4/FIXES2.md`)

Basic mass (CAD, `cad_mass.json`) **1,231.3 g** (FIXES 1,215.9): +15.4 g in the wing group = 4 printed lens caps with stop bosses and bonding flanges 12.4 g (FIXES carried 2 g), 2 hinge dampers 5.0 g (new), balance tabs/lead 32.2 g (was 34.2 with the caps counted inside). CG 24.4 mm (band 20-26; pack trim -/+ 10 mm). Predicted (basic x 1.1174 + 48): **1,423.9 g** (headroom 16 g to 1,440); `mission_gate_a.py` 1,419 g; capped +-5 % window mass limit 1.486 kg. The predicted total stays <= 1,440 only if >= **27.2 g** of the 41.6 g `EST` cuts are real (was 11.8 g). Fallback worth 5.6 g: lead 15.6 -> 12.8 g per elevon (the damper carries the flutter margin; FIXES2 s2.4). Structure (CAD groups wing 223.4 + fins 109 + feet 8.4 + hardware 30 + cage 113.3): **484.1 g** with the cuts (ceiling 494 g, 9.9 g under), about 521 g without them (FIXES 506).

## 8. CLAIMS-FIX update (2026-11-15, D-189 / D-190; full text `review/QP-4/CLAIMS-FIX.md`; supersedes s1 where they differ)

Motor cant 16 -> **17 deg** (D-189, for hover yaw authority 0.3465 -> 0.363 N m; cos 17 / cos 16 = 0.9948, vertical thrust -0.5 %). Reproduce: `python -I mission_gate_a.py`, `python -I prop_a.py`. With the 0.90 cap, `prop_a.py` x0.93, hot x0.97 on the sag case:

| At | T/W fresh (cap) | T/W sag (cap) | Window with the 0.90 cap |
|---|---|---|---|
| 1.419 kg (predicted + overrun) | 2.42 | 1.91 | +-7.0 % |
| 1.44 kg (target) | 2.39 | 1.89 | +-6.3 % |
| **1.47 kg (new gate)** | 2.34 | 1.85 | **+-5.3 %** |
| 1.50 kg (old gate) | 2.29 | 1.81 | +-4.3 % (below the R2 floor) |

Largest mass for a +-5 % capped window: **1.478 kg** (1.486 kg at cant 16). T/W sag >= 1.6 capped holds to 1.698 kg, fresh >= 2.0 capped to 1.718 kg. **The weigh-in gate is 1.47 kg**, the largest 0.01-kg step under 1.478 kg; the C3 "fly above the limit if the run shows >= +-5 %" rule of s1 is withdrawn (gate and window now agree). Headroom of the predicted 1,419 g (`mission_gate_a.py`; 1,423.9 g by the s7 formula) to the gate: 46-51 g; to the 1.44 kg target unchanged (16-21 g). The A-D3 target and the s6 re-sit triggers are unchanged except "as-built > 1.47 kg".

Analyses that still use 1.50 kg and remain conservative (heavier than the gate): mission energy lines (`mission_gate_a.py` prints 1.47 and 1.50), one-motor current 12.1 A (`prop_a.py one_motor(m=1.50)`), SITL roll rate at 1.50 kg (94.1 deg/s: more inertia, lower rate), SITL transition and landing cases at 1.41 / 1.50 kg, C1 loads at VD (n at 1.50 kg), structures iter. 3 loads at the gate mass. Not re-run at cant 17 (cant 16 baked in `run_fwd.py`): the forward-flight SITL cases (thrust cos 17 vs cos 16 is -0.5 %, `EST` effect far below the aero model error).
