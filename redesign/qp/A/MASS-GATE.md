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

## 13 Roll-up re-run after D-202 to D-212 rev 3 (2026-11-19, T-025 follow-up, review flag M2)

Category: mass roll-up (arithmetic on the CAD part table; not a simulation). Sections 1-12 above stay as the record; the last one (section 12) stopped at D-199. Method: `sitl/cad_mass.py` logic run on `cad/a_model.py` PARTS (output to a scratch file, so `sitl/cad_mass.json` and the running SITL jobs were not touched), then `mission_gate_a.py` items and CAD constants updated to the CAD part table (they still carried D-202 values: CAD basic 1,277.97 g, CG 19.52 mm; its own printout said "headroom -2 g", which was stale, not real). Evidence and commands: `mechanism/out/T025_followup.md`.

| Quantity | D-199 (section 12) | 2026-11-19 | Limit | Source |
|---|---|---|---|---|
| CAD basic mass | 1,262.6 g | **1,273.30 g** | — | CAD part table, 117 parts (D-208 value was 1,273.24 g in `cad_mass.json`) |
| CG (CAD, pack centred) | 20.68 mm | 21.37 mm | band 19-26 | same |
| CG at the pack trim ends (6 mm fwd, 10 mm aft) | 19.4 / 22.8 mm | 20.09 / 23.49 mm (SM 8.4 / 7.0 % at NP 40.7 EST) | >= 19 / <= 28.5 | CL-A-CG-TRIM-FWD / AFT rule: CG -+ 270 g x travel / basic |
| Predicted, flat rule (basic x 1.1174 + 0.032 x 1,470 g) `EST` | 1,458.1 g | **1,469.8 g** | 1,470 (target = gate) | CL-A-MASS-PRED |
| Predicted, itemised `EST` (growth by maturity 145.0 g + overrun 48 g) | 1,454 g | **1,466.3 g** | 1,470 | `mission_gate_a.py` |
| Margin to the 1.470 kg gate and target, flat rule | 1.9 g to 1,460 | **+0.18 g** | >= 0 | arithmetic |
| Margin, itemised | — | +3.7 g | >= 0 | arithmetic |
| EST cuts that must be real | 36.8 g | 41.44 g | <= 41.6 g | CALC-A-CUTS: 41.6 - (1,470 - 1,469.83) / 1.1174 |
| Structure (wing 216.1 + fins 108.2 + feet 8.4 + hardware 25.98 + cage CGE 131.04) | 485 g | 489.72 g | <= 494 g | CAD part table |

**Margin is positive but 0.18 g (flat rule): not a critical issue, no recovery needed now, and it is no buffer.** At 1.470 kg (table in `mission_gate_a.py`): capped transition window +-5.3 % (limit 5 %), hover T/W fresh 2.34 / sag 1.85 capped (limits 2.0 / 1.6), cruise to BATT_LOW 4.21 min against 3.41 needed (1.3 spare laps). The prediction still holds 145 g of EST growth and 48 g of overrun: the real buffer.

Added since the section 12 roll-up (CHANGE-LOG): D-202 hub +16.7 g; D-205 hub 6 mm aft, doublers s 11-25 -1.8 g, lead 15.6 -> 12.8 g per elevon -5.6 g; D-206 bridge 16x14 +2.1 g; D-207 fillets +1.3 g; D-208 pitot lines, I2C lead +3.3 g; D-210 cup fillets about +0.07 g per cup EST (inside the 4.3 g cup part mass; not separately in the table); D-211 core; D-212 rev 3 horn MEC-004 0.95 g and keeper MEC-008 0.08 g per side (CAD part table). From the D-208 value (1,273.24 g) to now (+0.06 g): horns -0.10 g (1.0 g vendor horn to 0.95 g printed, two sides), keepers +0.16 g (two sides), M2 x 8 arm screws +0.10 g (0.27 -> 0.32 g, two sides, D-212 rev 3 log), other D-211/D-212 changes -0.10 g by difference (not itemised).

**Target series (review flag M1):** design target 1.44 kg (QP-4) -> 1.46 (D-195) -> 1.465 (D-205) -> 1.467 (D-207) -> 1.470 kg (D-208, user accepted), now equal to the 1.470 kg gate: the target no longer controls anything, the margin is held in the growth and overrun allowances above. Recorded as a series, not changed.

Stale downstream values found (not edited, they feed the proof chain): `params-A.json` `mass.basic_cad_kg` 1.27324 (now 1.27330), `mass.itemised_g_growth` (D-199 era items), `mass.structure_groups_g` (cage 119.2 g: sum 484.9 g against 489.72 g from the CAD table, still <= 494 g), `sitl/cad_mass.json` 1.27324 kg (0.06 g low). Regenerate with `proofs/gen_params_a.py` and `sitl/cad_mass.py` after the SITL batch that reads them finishes.

## 14 Printed-part audit (2026-11-19, T-067): s13 margin superseded
T-067 (`redesign/qp/A/mechanism/out/T067_mass_audit.md`) found the listed masses of 42 printed PETG parts total 112.1 g while their CAD volume is 299.3 g solid (x 1.27 g/cm3, Prusament TDS) and 250.2 g on an EST shell-and-infill basis. With that basis the CAD basic mass is 1,412.4 g and the flat-rule prediction 1,625.2 g, **155.2 g over the 1,470 g gate (FAIL)**; itemised rule 1,633.0 g; a lighter basis still gives 1,581.9 g. The s13 "+0.18 g" is therefore not valid. Cause: solid blocks and plates drawn in the CAD (pack tray, avionics plate, motor cups, bridge saddle, strut clamps, fin saddle and root block), not infill alone. Basis, orientation and class are EST (no slicer run or weigh-in). Recovery and any gate decision: D-215 s11 / T-070.

## 15 T-083 / T-083b basis update (2026-11-22, T-083c; D-227, D-228, D-229): supersedes the MN2212, Tattu and PETG-root-block lines above
Category: geometry arithmetic and the repo EST thrust model (illustrative), copied from the reports; nothing re-computed here. Sources: `mechanism/out/T083_report.md` s2.1, s6, s10; `mechanism/out/T083b_report.md` s0, s2, s4.1, s9. Labels: EST estimate, "—" unknown. The 1,500 g `build_a` mass gate still fails (1,627.5 g drawn, T083b_report s6) and is not relaxed; limits A-P2 / A-P3 / A-P4 / A-P6 unchanged.

**Basis changes (replace the lines named):**
| Line | Was (sections above) | Now | Source |
|---|---|---|---|
| Motors | 4 x MN2212 65 g (s2) | PRP-001 4 x 67.5 g (SunnySky X2216 V3 short shaft page, read 2026-11-21) | T083_report s10, s2 |
| Motor mounts | — | PRP-006 4 x 9.2 g (CALC / EST) | T083_report s10 |
| Prop hardware | — | PRP-004 4 x 3.6 g, PRP-005 4 x 1.4 g | T083_report s10 |
| Cup / lead hole | — | CGE-003 4 x 8.96 g (voxel) | T083_report s10 |
| Phase leads | about 1.8 m of 20 AWG (400 mm stock leads) | HRN-001 phase extensions 38.4 g (5.40 m beyond the 100 mm X2216 stock leads) | T083_report s10, s6 |
| Pack | Tattu 2300 4S, 270 g | 2,800 mAh 4S pack (`params-A.json` pack_ah 2.8); mass line 270 g per BOM-T083b.csv W01 listing | T083_report s2; BOM-T083b.csv |
| Fin root block FIN-003 | PETG block 22.86 g (voxel, T-067 basis) + 6.1 g undrawn enlargement tally; the "+12.2 g enlarged root blocks at 283.1" tally line is dropped | machined 6061-T6 root fitting, **12.04 g each** (drawn volume x 2.70 g/cm3), CG x 282 mm, 2 fittings; stock the T11 offcut, $0 | T083b_report s2, s9; D-229 |

**Roll-up (EST, `T083b_report.md` s4.1; predicted = basic x 1.1174 + 0.032 x 1.47):**
| State | basic g | predicted kg | CG mm | SM % | trim ends mm | window % | T/W fresh / sag | cruise s | 1.3 Vs m/s |
|---|---|---|---|---|---|---|---|---|---|
| T-083 tallied (record) | 1,669.8 | 1.9129 | 24.41 | 6.65 | 23.44 / 26.03 | +11.02 | 2.586 / 2.074 | 223 | 17.71 |
| T-083b as drawn (`cad_mass.json`) | 1,627.5 | 1.8656 | 21.08 | 8.01 | 20.08 / 22.74 | +12.25 | 2.652 / 2.127 | 239 | 17.49 |
| **T-083b tallied (current basis; +7.0 g shoe cups at 298.1, EST)** | **1,634.5** | **1.8734** | **22.26** | **7.52** | 21.27 / 23.92 | **+12.05** | **2.641 / 2.118** | **236** | **17.53** |

Change T-083 tally -> T-083b tally: -35.3 g (root fittings -33.8 g = 2 x (22.86 + 6.1 - 12.04); harness and tray -1.5 g). CG moved forward 5.2 mm with the lighter fittings; cage, pack and tray windows 6 mm aft of T-083 (T083_DX -3 -> +3 mm, ladder rung 3, no ballast, D-229). Limits checked in the report: A-P4 19.3..26.0 mm (trim aft 28.5), SM >= 5 %, A-P3 >= +5 %, A-P2 2.0 / 1.6, cruise >= 204.6 s: all PASS at the tallied state; A-P6 FAIL on CLmax 0.75 EST, gated by the stall test (D-228). The old "predicted 1.64 kg" (O4b, CLAUDE.md header) and 1.913 kg (T-083) figures are superseded by 1.873 kg EST.
**Not re-derived here:** the s1 to s14 tables (MN2212, 1.396 to 1.47 kg era) stay as the record. The BOM total $1,981.31 incl. reserve $346.94, margin +$18.69 (AM-019, T083b_report s5) is from `T083b_data/BOM-T083b.csv`; `BOM-A.csv` was replaced by it in D-230 and now carries the same $1,981.31 (T-023 F-4; `python -I bom_a.py`).

> 2026-11-22 note (T-023 F-9): the elevon hinge-damper stators WNG-009-L/R (2.0 g each, PETG + silicone,
> DRAWINGS-A.md) are not in `printed_mass.json` (T-067 voxel basis). Their mass enters the CAD part table as
> `DMP_STATOR_G` (`cad/amodel/wing.py` l.571: drawn PETG volume x RHO_PETG). The silicone fluid and preload strips
> are not in that number: their mass is "—" (EST under 1 g for both, not sourced). AVN-010 "14: CHECK (a body is
> not attached)" is a drawing-tool note, not a mass item.
