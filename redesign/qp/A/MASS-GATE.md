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


## 9. QP-5 update (2026-11-15, D-195; after the CAD fidelity round D-193 / D-194; supersedes s1 and s7 where they differ)

Reproduce: `python -I mission_gate_a.py` (items re-based on the CAD part table), `python -I aero_s5010.py`. Source of the mass change: `review/QP-5/CAD-INTEGRATION.md` s4.

**Basic mass 1,259.14 g (CAD), CG 21.47 mm aft of the LE, SM 7.8 %.** Predicted mass, two methods, both `EST`: itemised growth by maturity **1,449 g** (`mission_gate_a.py`: basic 1,259.1 + growth 142.2 + overrun 48); flat rule basic x 1.1174 + 47 g (overrun 3.2 % of the 1.47 kg gate) **1,454 g** (the CAD-INTEGRATION 1,455 g used 48 g). Headroom to the 1.47 kg gate 16-21 g; **over the old 1.44 kg target by 9-14 g**.

**Decision (D-195): accept, re-base the design target to 1.46 kg; do not cut.** Reasons: (1) 28.8 g of the 44.3 g added (the net change is +27.8 g after 21.0 g of lump reductions) is the T-Motor prop adapter and spinner nut, real parts that no earlier lump carried: cutting 15 g elsewhere means removing structure the 3-D model already shows as minimal (structure 479.3 g, ceiling 494 g, 15 g spare); (2) the predicted figure already holds a 48 g overrun and 142 g (11.3 %) of EST growth, so the 1.47 kg gate is reached only if the as-built aircraft is 211 g (16.8 %) over the CAD basic, against 190 g allowed in the prediction; (3) at 1.455 / 1.46 kg the capped transition window is +-5.8 / +-5.6 % (floor 5 %), hover T/W 2.36 fresh / 1.87 sagged capped (limits 2.0 / 1.6), and cruise to BATT_LOW 4.31 min against 3.41 needed (1.5 spare laps), so no performance limit is touched; (4) the weigh-in gate (1.47 kg, D-190) is the hard limit and is unchanged; the target is a derived requirement owned by the team. The 1.44 kg target had 16-21 g of headroom to the gate at QP-4; the new 1.46 kg target keeps 16 g.
Fallbacks if the as-weighed mass runs high (not applied): elevon lead 15.6 -> 12.8 g per elevon, -5.6 g (flutter with the damper holds: `structures/flutter_d195.md` case F, onset 37.5 m/s kd hot, line 28.8); T-Motor hardware pack may contain the adapter (BOM line absent either way, confirm on the first order); hub arm bosses to 2.0 mm walls would cost **+7.1 g** (`structures/qp5_checks.md` s2, open).

| At | T/W fresh (cap) | T/W sag (cap) | Window with the 0.90 cap | Cruise to BATT_LOW (min, need 3.41) | Pack margin |
|---|---|---|---|---|---|
| 1.449 kg (itemised) | 2.37 | 1.87 | +-6.0 % | 4.34 | 1.12x |
| 1.455 kg | 2.36 | 1.87 | +-5.8 % | 4.31 | 1.11x |
| 1.46 kg (target) | 2.35 | 1.86 | +-5.6 % | 4.27 | 1.11x |
| 1.47 kg (gate) | 2.34 | 1.85 | +-5.3 % | 4.21 | 1.10x |

Stall (CLmax 0.75 `EST`) at 1.455 kg 11.99 m/s, 1.3 Vs 15.6 m/s against 17 m/s cruise. Hover 211 W, 14.2 A from the pack. The 1.50 kg lines of s8 stay conservative.

**CG and static margin (D-195).** CG 21.47 mm; pack trim +-10 mm moves it by 2.14 mm (270 g x 10 / 1,259 g): **19.33 to 23.61 mm**, SM 8.7 to 7.0 %. NP 40.7 mm (`EST`, unchanged): the S5010 section aerodynamic centre is at 0.25 c (own panel check 0.248 c, `aero_s5010.py`) and the CAD prop plane (x -110 mm, not -85 mm of SIZING-A) lowers it to 39.6 mm with the same rule (SM 7.4 %), still above the 5 % limit by 2.4 % chord. Trim elevon at 17 m/s and 1.455 kg: **4.8 deg TE up** (alpha 5.1 deg), 4.1 deg at the aft trim end, 5.5 deg at the forward end; stop 21 deg.

## 10 D-196 hub socket walls (2026-11-15)

Arm-socket wall 2.0 mm over the 12 mm mouth zone, 1.2 mm bridge sleeve: hub 13.1 -> 17.7 g (`cad/amodel/wing.py`, `structures/qp5_checks.md` s2/s2b). Pack forward trim travel 10 -> 8 mm (tray front lip 2 mm aft).

| Quantity | D-195 | D-196 | Limit | Source |
|---|---|---|---|---|
| CAD basic mass | 1,259.1 g | 1,263.7 g | — | `sitl/cad_mass.json` |
| CG (CAD) | 21.47 mm | 21.13 mm | band 19-26 | `sitl/cad_mass.json` |
| CG at the trim ends | 19.33 / 23.61 mm | 19.42 / 23.26 mm | >= 19 / <= 28.5 | claims CL-A-CG-TRIM-FWD / AFT |
| Predicted, itemised `EST` | 1,449 g | 1,454 g | — | `mission_gate_a.py` |
| Predicted, flat rule `EST` | 1,454 g | 1,459 g | <= 1,460 (target), 1,470 (gate) | CL-A-MASS-PRED |
| EST cuts that must be real | 36.2 g | 40.8 g | <= 41.6 g | CL-A-CUTS-REQUIRED |
| Structure | 479.3 g | 482.8 g | <= 494 g | CL-A-STRUCT-MASS |

The target now has 1 g of room. Any further growth is cut (fallback: lead strip 15.6 -> 12.8 g, re-run flutter) or re-decided against the 1.47 kg gate.

## 11 D-198 harness enclosure (2026-11-15)

Bay cover AVN-008 (0.6 mm printed PETG, 9.6 g) and lead collars (+0.3 g per cup) are added; the lumped harness remainder is now a bottom-up list (`cad/amodel/electrical.py` `HRN_ITEMS`, 28.1 g, was the 50.9 g remainder of the 110 g avionics allocation). The bottom-up list carries 17.5 g of phase-lead extension wire (route 0.53-0.62 m against the 0.40 m stock leads) that the old lump did not itemise. Detail: `../../review/QP-5/HARNESS-ENCLOSED.md` s4.

| Quantity | D-196 | D-198 | Limit | Source |
|---|---|---|---|---|
| CAD basic mass | 1,263.7 g | 1,259.7 g | — | `sitl/cad_mass.json` |
| CG (CAD) | 21.13 mm | 21.32 mm | band 19-26 | `sitl/cad_mass.json` |
| CG at the trim ends | 19.42 / 23.26 mm | 19.60 / 23.46 mm | >= 19 / <= 28.5 | CL-A-CG-TRIM-FWD / AFT |
| Predicted, itemised `EST` | 1,454 g | 1,450 g | — | `mission_gate_a.py` |
| Predicted, flat rule `EST` | 1,459 g | 1,455.6 g | <= 1,460 (target), 1,470 (gate) | CL-A-MASS-PRED |
| EST cuts that must be real | 40.8 g | 36.8 g | <= 41.6 g | CL-A-CUTS-REQUIRED |
| Structure | 482.8 g | 485 g | <= 494 g | CL-A-STRUCT-MASS |

The target has 4 g of room (flat rule). The bottom-up harness list is `EST` apart from the wire mass per metre; weigh the wire when it arrives. The cover adds frontal area in cruise; the drag was not re-modelled (open).

## 12 D-199 raceway, strap and pad (2026-11-15)

Raceways HRN-003 (2 x 1.8 g) and hub conduits HRN-004 (4 x 0.8 g) are added (+6.8 g); the shorter enclosed route cuts the phase-lead extension wire from 2.47 m to 1.10 m (`HRN_ITEMS` 17.5 -> 7.8 g, harness remainder 28.1 -> 18.4 g, -9.7 g); the hub tray-pad slots take 0.2 g off the hub; the pack strap is the real STRIX 20 x 300 mm buckle strap (5.5 g, V, was an EST 3.0 g, +2.5 g) and the anti-slip pad is now drawn (3.5 g EST, +3.5 g). Detail: `../../review/QP-5/HARNESS-ENCLOSED.md` D-199.4.

| Quantity | D-198 | D-199 | Limit | Source |
|---|---|---|---|---|
| CAD basic mass | 1,259.7 g | 1,262.6 g | — | `sitl/cad_mass.json` |
| CG (CAD) | 21.32 mm | 20.68 mm | band 19-26 | `sitl/cad_mass.json` |
| CG at the trim ends | 19.60 / 23.46 mm | 19.4 / 22.8 mm (forward travel 8 -> 6 mm) | >= 19 / <= 28.5 | CL-A-CG-TRIM-FWD / AFT |
| Predicted, itemised `EST` | 1,450 g | 1,454 g | — | `mission_gate_a.py` |
| Predicted, flat rule `EST` | 1,455.6 g | 1,458.1 g | <= 1,460 (target), 1,470 (gate) | CL-A-MASS-PRED |

The target has 1.9 g of room (flat rule). The strap mass is a vendor listing; the pad (size, thickness 1.0 mm, density 1.15 g/cm3) is `EST`: weigh both on arrival. The raceway and conduit walls are the drawn volume x 1.27 (0.6 mm walls, `EST` basis as the cover).
