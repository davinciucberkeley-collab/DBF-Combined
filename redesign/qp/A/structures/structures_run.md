## 1. Structural mass per part vs MASS-GATE allocation (g)
| Part | CALC bottom-up g | MASS-GATE g | delta |
|---|---|---|---|
| Wing | 209 | 220 | -11 |
| Fins | 121 | 70 | +51 |
| Cage | 122 | 135 | -13 |
| Hardware | 40 | 35 | +5 |
| **Structure total** | **492** | **460** | **+32** |
|   Wing: XPS core | 95.3 | | |
|   Wing: spar tube 16x14 x 0.90 m | 67.9 | | |
|   Wing: tape skin 0.44 m2 x 55 g/m2 EST | 24.2 | | |
|   Wing: 4 PETG spar plugs + 2 elevon hinge/horn blocks | 14.0 | | |
|   Wing: epoxy/glue EST | 8.0 | | |
|   Fins: CFRP 0.1 mm skins (0.173 m2) | 27.6 | | |
|   Fins: XPS core 15 mm (both) | 38.9 | | |
|   Fins: 4 foot shoes (PETG 3 g + EVA pad 1 g) | 16.0 | | |
|   Fins: 2 root blocks (PETG) | 12.0 | | |
|   Fins: 2 rib tubes 14x12 x 0.20 m | 26.1 | | |
|   Cage: 4 arm tubes 14x12 x 0.245 m | 64.0 | | |
|   Cage: PETG hub (sockets, pack tray) | 20.0 | | |
|   Cage: bridge tube 8x6 x 0.16 m + 2 saddles | 11.6 | | |
|   Cage: 4 motor cups (PETG, M3 pattern) | 20.0 | | |
|   Cage: socket epoxy EST | 6.0 | | |
|   Hardware: M3 screws/nuts (motors 16, others), epoxy fillets, paint EST | 40.0 | | |

Growth on these four lines: EST 20 % = 92 g in MASS-GATE; at CALC 10 % = 49 g. Net change to the 1,381 g prediction = +32 - (92 - 49) = **-11 g** (EST; weigh each part to confirm).

## 2. C1 loads (limit unless marked; ult = 1.5 x limit)
Vs 12.07 m/s (CLmax 0.75 EST), VA = Vs sqrt(3.4) = 22.2, VC 17, VD 22 (1.25 VC rounded up; A.param AIRSPEED_MAX 18). a = 3.74/rad, mu_g 12.2, Kg 0.613.
| Case | n | Note |
|---|---|---|
| Gust U 8 m/s at VC | 3.85 -> stall-limited 1.98 | wing cannot make the gust n at 17 m/s |
| Gust U 4 m/s at VD (half, ASM-C1-UDE-D-FRAC) | 2.85 (stall line 3.32) | |
| Manoeuvre limit | +3.4 / -1.5 | A-P13 floor governs; ult +5.1 / -2.25; VA = 22.2 ~ VD |
| Spar root bending, flight n 3.4 (elliptical lift, inertia relief) | 1.84 N m (4.78 unrelieved) | design uses unrelieved 4.78 limit |
| Hover 8 m/s gust broadside (plate Cd 2.0): wing force 17.2 N, spar root | 1.94 N m | below flight case |
| Cage pitch moment, upper pair at the 0.90 cap (8.8 N each) / lower pair 1 N | 2.44 N m on the bridge | A-P8 85 % output limit not exceeded in SITL; this is the bound |
| Prop strike (blade stops, one motor, 30 N along thrust EST; K09-L P1 fuse idea) | arm root 8.3 N m; bridge 4.7 N m | damage case |
| Transport drop 0.3 m (v 2.43 m/s), cradle stroke s, efficiency 0.5 (ASM-C1-CRUSH-EFF) | n = v^2/(2 g eta s): s 25 mm: 24.0 g; s 35 mm: 17.1 g; s 50 mm: 12.0 g; s 60 mm: 10.0 g | `-` box cradle not designed; s needs >= 40 mm for n <= 15 |
| Landing (see s5) | foot plateau 30 N, 4 feet | sim peak foot load factor <= 11.4 g, feet <= 49 N, side <= 20 N |

## 3. C2 wing: spar and foam
| Check | Stress | Allowable | MS | Result |
|---|---|---|---|---|
| Spar 16x14 root bending, ult x fitting, unrelieved 8.2 N m | 50 MPa | 350 | +6.1 | PASS |
| Spar shear at root | 1.8 MPa | 30 | +15.4 | PASS |
| Spar tip deflection at n 3.4 (tube alone, E 70 GPa) | 5.7 mm of 450 mm semispan (1.3 %) | 5 % | | PASS |
| Spar wall under saddle clamps (hoop) | PETG plug in tube at y = 0, +-0.38 (C2 rule: unplugged ring failed by 20x) | - | - | plugs required, in mass |
| Foam shear around spar from bridge torque 2.44 N m (zone |y| <= 0.1, r 8 mm, ult x fit x print) | 65 kPa | 100 | +0.53 | PASS |
| Foam bearing at the fin slot (both feet side load 2 x 20 N, slot 65 x 23 mm) | 57 kPa | 120 | +1.11 | PASS |
| Foam shear, lift into spar slot (55 N/m over 32 mm of bond) | 2.6 kPa | 100 | +37 | PASS |
| Arm / motor attachments | none in foam: the cage hangs from the spar through the bridge saddle and the arms carry the motors; foam sees only the saddle pocket (R >= 3 mm corners, C6 rule) | - | - | - |
Fin elevon note: elevon span ends at |y| <= 0.34 (fin slot at 0.38 starts beyond it); fin x 0.18-0.30 overlaps the wing aft 65 mm.

## 4. C4 modes vs rotor orders (3-D beam FE, free-free; fe_a.py)
- hover (1.50 kg, prop_a.py): 6272 rpm: 1P 105 Hz, 2P 209 Hz
- hover light 1.381 kg: 6018 rpm: 1P 100 Hz, 2P 201 Hz
- hover 8 m/s lean 1.3 W: 7151 rpm: 1P 119 Hz, 2P 238 Hz
- cruise 17 m/s (EST): 9700 rpm: 1P 162 Hz, 2P 323 Hz
Cruise rpm is an estimate (APC static table only; J0 0.47 assumed, thrust 0.49 N per prop at L/D 7.6): 8,900-10,500 rpm band; bench M1 + audio FFT replace it.

Modes with strong coupling to the motors (|phi| at motors in plane cy or thrust cx >= 0.5, mass-normalised), kd = E_CF 61 / PETG 1.6 GPa, nom 70 / 2.1, hi 90 / 2.4:
| Corner | f (Hz) | group | cx / cy | worst separation to 1P/2P at hover 6272 and cruise 9700 | worst incl. hover light | Result |
|---|---|---|---|---|---|---|
| kd | 5 | bridge 97% | 0.0 / 2.5 | 96 % | 95 % | PASS |
| kd | 15 | bridge 84% | 2.7 / 0.0 | 85 % | 85 % | PASS |
| kd | 17 | spar 70% | 2.0 / 0.1 | 84 % | 83 % | PASS |
| kd | 31 | spar 93% | 1.1 / 0.0 | 70 % | 69 % | PASS |
| kd | 43 | arm 36% | 1.4 / 1.8 | 59 % | 57 % | PASS |
| kd | 47 | arm 100% | 0.1 / 3.4 | 55 % | 53 % | PASS |
| kd | 47 | arm 100% | 3.4 / 0.1 | 55 % | 53 % | PASS |
| kd | 49 | arm 94% | 0.4 / 3.2 | 53 % | 51 % | PASS |
| kd | 59 | arm 54% | 0.1 / 2.2 | 44 % | 41 % | PASS |
| kd | 59 | arm 91% | 2.7 / 0.0 | 44 % | 41 % | PASS |
| kd | 72 | arm 40% | 0.9 / 1.5 | 32 % | 29 % | PASS |
| kd | 79 | bridge 46% | 0.7 / 1.4 | 24 % | 21 % | PASS |
| kd | 86 | spar 56% | 0.4 / 0.7 | 18 % | 14 % | MARGINAL |
| kd | 589 | arm 100% | 0.0 / 0.7 | 82 % | 82 % | PASS |
| nom | 5 | bridge 97% | 0.0 / 2.5 | 96 % | 95 % | PASS |
| nom | 17 | bridge 84% | 2.7 / 0.0 | 84 % | 84 % | PASS |
| nom | 17 | spar 73% | 2.0 / 0.1 | 83 % | 83 % | PASS |
| nom | 34 | spar 93% | 1.1 / 0.0 | 68 % | 66 % | PASS |
| nom | 45 | arm 35% | 1.4 / 1.8 | 57 % | 55 % | PASS |
| nom | 51 | arm 100% | 3.4 / 0.4 | 52 % | 50 % | PASS |
| nom | 51 | arm 100% | 0.4 / 3.4 | 52 % | 50 % | PASS |
| nom | 52 | arm 94% | 0.4 / 3.2 | 50 % | 48 % | PASS |
| nom | 63 | arm 55% | 0.1 / 2.2 | 40 % | 37 % | PASS |
| nom | 63 | arm 91% | 2.7 / 0.0 | 40 % | 37 % | PASS |
| nom | 76 | arm 41% | 0.9 / 1.5 | 27 % | 24 % | PASS |
| nom | 85 | bridge 46% | 0.7 / 1.4 | 19 % | 15 % | MARGINAL |
| nom | 92 | spar 56% | 0.4 / 0.7 | 12 % | 8 % | FAIL |
| nom | 631 | arm 100% | 0.0 / 0.7 | 95 % | 95 % | PASS |
| nom | 691 | arm 89% | 0.6 / 0.1 | 114 % | 114 % | PASS |
| nom | 728 | arm 88% | 0.5 / 0.0 | 125 % | 125 % | PASS |
| hi | 6 | bridge 97% | 0.0 / 2.5 | 95 % | 94 % | PASS |
| hi | 19 | bridge 84% | 2.7 / 0.0 | 82 % | 81 % | PASS |
| hi | 21 | spar 70% | 2.0 / 0.1 | 80 % | 79 % | PASS |
| hi | 38 | spar 93% | 1.1 / 0.0 | 63 % | 62 % | PASS |
| hi | 52 | arm 36% | 1.4 / 1.8 | 50 % | 48 % | PASS |
| hi | 57 | arm 100% | 0.8 / 3.3 | 45 % | 43 % | PASS |
| hi | 57 | arm 100% | 3.3 / 0.8 | 45 % | 43 % | PASS |
| hi | 59 | arm 94% | 0.4 / 3.2 | 43 % | 41 % | PASS |
| hi | 72 | arm 54% | 0.1 / 2.2 | 32 % | 29 % | PASS |
| hi | 72 | arm 91% | 2.7 / 0.0 | 32 % | 29 % | PASS |
| hi | 87 | arm 40% | 0.9 / 1.5 | 17 % | 13 % | MARGINAL |
| hi | 96 | bridge 46% | 0.7 / 1.4 | 8 % | 4 % | FAIL |
| hi | 104 | spar 55% | 0.5 / 0.7 | 0 % | 0 % | FAIL |
| hi | 716 | arm 100% | 0.0 / 0.7 | 121 % | 121 % | PASS |

Fin out-of-plane modes (fin 75-95 % of strain energy) and weakly coupled spar / rib modes (cx, cy < 0.5):
| Corner | f (Hz) | group | worst separation (6272, light, 9700 rpm) | Result |
|---|---|---|---|---|
| kd | 97 | spar 53%, rib 40% | 3 % | FAIL |
| kd | 207 | spar 76%, rib 23% | 1 % | FAIL |
| kd | 257 | rib 90%, spar 8% | 20 % | PASS |
| kd | 273 | rib 76%, spar 22% | 15 % | MARGINAL |
| kd | 291 | spar 56%, rib 27% | 10 % | MARGINAL |
| kd | 346 | spar 93%, rib 6% | 7 % | FAIL |
| kd | 379 | spar 67%, rib 20% | 17 % | MARGINAL |
| kd | 479 | fin 91%, spar 5% | 48 % | PASS |
| kd | 486 | fin 84%, spar 9% | 50 % | PASS |
| kd | 578 | arm 89%, bridge 11% | 79 % | PASS |
| kd | 602 | arm 92%, bridge 7% | 86 % | PASS |
| kd | 628 | arm 100%, fin 0% | 94 % | PASS |
| kd | 628 | arm 100%, spar 0% | 94 % | PASS |
| kd | 659 | arm 93%, bridge 6% | 104 % | PASS |
| kd | 695 | arm 92%, bridge 8% | 115 % | PASS |
| kd | 700 | spar 99%, rib 1% | 117 % | PASS |
| kd | 782 | spar 74%, rib 20% | 142 % | PASS |
| nom | 104 | spar 53%, rib 40% | 0 % | FAIL |
| nom | 221 | spar 77%, rib 22% | 6 % | FAIL |
| nom | 275 | rib 90%, spar 7% | 15 % | MARGINAL |
| nom | 292 | rib 76%, spar 22% | 10 % | FAIL |
| nom | 311 | spar 56%, rib 27% | 4 % | FAIL |
| nom | 370 | spar 94%, rib 6% | 14 % | MARGINAL |
| nom | 406 | spar 67%, rib 20% | 26 % | PASS |
| nom | 514 | fin 91%, spar 5% | 59 % | PASS |
| nom | 521 | fin 84%, spar 9% | 61 % | PASS |
| nom | 592 | arm 92%, bridge 8% | 83 % | PASS |
| nom | 615 | arm 97%, bridge 3% | 90 % | PASS |
| nom | 628 | arm 100%, bridge 0% | 94 % | PASS |
| nom | 628 | arm 100%, fin 0% | 94 % | PASS |
| nom | 750 | spar 99%, rib 1% | 132 % | PASS |
| hi | 118 | spar 53%, rib 39% | 13 % | MARGINAL |
| hi | 251 | spar 76%, rib 23% | 20 % | MARGINAL |
| hi | 311 | rib 89%, spar 7% | 4 % | FAIL |
| hi | 330 | rib 74%, spar 23% | 2 % | FAIL |
| hi | 351 | spar 55%, rib 26% | 9 % | FAIL |
| hi | 420 | spar 93%, rib 6% | 30 % | PASS |
| hi | 454 | spar 62%, fin 22% | 40 % | PASS |
| hi | 543 | fin 89%, spar 6% | 68 % | PASS |
| hi | 555 | fin 74%, spar 14% | 72 % | PASS |
| hi | 706 | arm 88%, bridge 11% | 118 % | PASS |
| hi | 734 | arm 92%, bridge 8% | 127 % | PASS |
| hi | 770 | arm 100%, fin 0% | 138 % | PASS |
| hi | 770 | arm 100%, fin 0% | 138 % | PASS |

Forced response (C2 method): worst-phase modal sum, 4 rotors, unbalance U = 1.0 g mm per rotor (EST; ISO G16 prop is 0.27 g mm), 2P axial ripple 5 % of thrust (EST), damping 1 % (EST). Acceleration at the FC (spar centre):
| Corner | Point | IMU accel, 1P | IMU accel, 2P | fin tip accel 1P / 2P (m/s2) | limit | MS |
|---|---|---|---|---|---|---|
| kd | hover 6272 | 14.9 | 2.9 | 28.5 / 6.0 | 30 m/s2 | +1.0 |
| kd | cruise 9700 EST | 24.4 | 0.4 | 47.8 / 0.7 | 30 m/s2 | +0.2 |
| nom | hover 6272 | 17.5 | 3.0 | 31.5 / 5.8 | 30 m/s2 | +0.7 |
| nom | cruise 9700 EST | 25.2 | 0.4 | 45.1 / 0.8 | 30 m/s2 | +0.2 |
| hi | hover 6272 | 63.9 | 3.0 | 129.8 / 6.3 | 30 m/s2 | -0.5 |
| hi | cruise 9700 EST | 27.1 | 0.4 | 53.3 / 0.8 | 30 m/s2 | +0.1 |

Fin out-of-plane EI 59.5 N m2 (kd), mass/length 92 g/m (15 mm XPS core, 0.1 mm CFRP skins); foot 3 g; f1 cantilever ideal at kd: see table (fin rows).

### Mount stiffness and strength (limit load at the 0.90 cap, design = x1.5 x1.15 x1.25 on printed / bonded, x1.5 x1.15 on CF)
| Item | Value | Allowable | MS | Result |
|---|---|---|---|---|
| Arm 14x12 root bending, thrust 8.8 N at 0.246 m = 2.17 N m | 30 MPa | 350 | +10.6 | PASS |
| Arm, prop strike 30 N (EST) 7.4 N m | 103 MPa | 350 | +2.4 | PASS |
| Bridge 8x6 in prop strike, 4.7 N m (sets the fuse: weakest CF part) | 235 MPa | 350 | +0.49 | PASS |
| Bridge 8x6, max control pitch moment 2.44 N m | 122 MPa | 350 | +1.86 | PASS |
| Bridge, pack + hub at 12 g crash (34 N x 0.135 m = 4.6 N m, A-P5) | 231 MPa | 350 | +0.51 | PASS |
| Arm tip stiffness 12.2 N/mm: thrust deflection | 0.72 mm | - | - | info |
| Hub pitch rotation under max control moment: M L / EI(bridge 8x6, 9.6 N m2) | 2.0 deg | - | - | MARGINAL: soft mount (cage pitch mode 40-47 Hz, FC filter / notch must be set below 30 Hz or the mode notched) |
| Bridge buckling under hover thrust sum 1.33 W = 20 N (cantilever-pin K=2) | P_cr 1303 N | | +37.6 | PASS |
| Motor screws: see s6 | | | | |

## 5. C5 landing on fin-tip feet
Static (CG 25.2 mm aft of LE, feet at x 0.300, y +-0.38, z +-0.18; CG 0.275 m above feet): tip-over narrow axis **33.2 deg** (limit 30: sizing 33.2), wide axis 54.1 deg. Parked broadside to the wind: tips at 7.4 m/s (gust 8: crew catches or lays it down, as A-P9); restoring / overturning at 5 m/s 2.21. I (kg m2, about the CG): [0.0564, 0.0254, 0.0618] (SITL plant used 0.053-0.064 roll).
Foot design (EST, CAD): PETG shoe bonded over the fin corner, 12 (y) x 15 (z) mm EVA/PE foam pad 30 mm thick, plateau stress 0.17 MPa -> **30 N per foot** (static load W/4 = 3.7 N: x8 below yield), usable stroke 20 mm, rigid stop beyond. Foam plateau and stroke are unmeasured: drop-test a coupon first (5 pads, 1.2 m/s on a scale).
Sim = `landing_a.py` (K09-L `team/C5/sim` physics rebuilt standalone for A: 6 dof, 4 elasto-plastic feet, friction 0.40, lift 2/3 W to 0.3 s then 0 at 0.6 s, 1.50 kg):
| Case | max stroke (mm) of 20 | permanent set (mm) | peak foot load (N) | side load (N) | n at CG | end tilt (deg) | drift (mm) |
|---|---|---|---|---|---|---|---|
| hard 1.2 m/s level | 8.3 | 6.8 | 40 | 0 | 10.8 | 0.0 | 0 |
| hard, 10 deg narrow | 13.9 | 12.4 | 40 | 14 | 5.4 | 1.8 | 142 |
| hard, 10 deg wide | 8.2 | 6.7 | 45 | 18 | 6.1 | 0.1 | 35 |
| hard, 7+7 deg combined | 9.1 | 7.6 | 45 | 18 | 5.7 | 0.3 | 17 |
| hard, 10 narrow + 0.5 m/s drift | 15.2 | 13.7 | 40 | 16 | 5.4 | 2.1 | 3 |
| hard, 10 wide + 0.5 m/s drift (y) | 11.1 | 9.6 | 47 | 19 | 6.4 | 0.4 | 98 |
| normal 0.5 m/s level | 2.3 | 0.8 | 33 | 0 | 8.9 | 0.0 | 0 |
| normal, 10 narrow | 3.3 | 1.8 | 34 | 13 | 6.9 | 0.1 | 87 |
| normal, 10 wide + drift | 5.8 | 4.3 | 40 | 16 | 5.4 | 0.3 | 101 |
| hard, 1.381 kg, 10 narrow | 12.9 | 11.4 | 40 | 14 | 5.8 | 1.6 | 147 |
Worst stroke 15.2 mm of 20 (margin 4.8 mm, 32 %): PASS. No tip-over in any case (end tilt <= 3 deg). Peak load factor 10.8 g vs A-P5 12 g: PASS (the 6 mm crush of SIZING-A is replaced: 12 g would need 6 mm only at constant force and a level hit; with 20 mm and 30 N the level hard case is below).
Pad life: normal landings set 0.8-4 mm; replace the pad at 10 mm cumulative set (a hard landing sets up to 13 mm: replace after any hard landing). Pads are $0 stock (foam); K09-L cartridges not used.
Side load 15-20 N per foot at mu 0.40 against the K09-L cap (24.5 N at 2.6 kg): scaled by mass the A cap is about 14 N: **side load 20 N is MARGINAL**; a pad face at mu <= 0.3 brings it to 15 N (EST).

## 6. C6 joints, fasteners, bonds (design load = limit x 1.5 x 1.15 [x 1.25 printed/bonded])
| Joint | Load (limit) | Stress / capacity (design) | Allowable | RF | Result |
|---|---|---|---|---|---|
| Motor to cup, 4 x M3x8 steel: tension from thrust 10.4 N + prying x2 (hover/full) | 2.6 N per screw x2 | 2.23 MPa | 450.0 MPa | 201.87 | PASS |
| Motor to cup: prop strike 30 N bending 0.012 m x 30 N on a 16 mm pattern (worst screw) | tension 22 N | 4.82 MPa | 450.0 MPa | 93.31 | PASS |
| Motor M3 thread strip in aluminium base, engagement 2.5 mm (>= 2.5 mm, C6 rule), strike | 22 N | 2.24 MPa | 90.0 MPa | 40.23 | PASS |
Cup head bearing: M3 with 6 mm washer on 4 mm PETG: 22 N x 2.16 / 28 mm2 = 1.7 MPa vs 20: RF 11.9 PASS (not a limit).
| Arm in hub / cup socket: bond, 25 mm insertion, prop strike couple (moment 8.3 N m / 0.025 m = 330 N on 14 x 25 mm) | 330 N | 1.29 MPa | 2.0 MPa | 1.55 | PASS |
| Arm in hub socket, thrust 10.4 N (2.9 N m): couple 116 N | 116 N | 0.45 MPa | 2.0 MPa | 4.40 | PASS |
| PETG socket wall bearing (strike couple 330 N on 14 x 12 mm contact) | 330 N | 4.24 MPa | 20.0 MPa | 4.72 | PASS |
| Bridge saddle on spar, full wrap 16 x 30 mm: control torque 2.4 N m | 2.4 N m | 0.44 MPa | 2.0 MPa | 4.59 | PASS |
| Bridge into hub (8 mm tube, 25 mm in socket), strike couple 4.7 N m / 0.025 | 188 N | 1.29 MPa | 2.0 MPa | 1.55 | PASS |
| Rib 14x12 CF tube root bending, both feet side load 40 N at 0.18 m (7.2 N m) | 7.2 N m | 100.18 MPa | 350.0 MPa | 3.49 | PASS |
| Rib saddle on spar (wrap 16 x 30 mm): 7.2 N m couple over 16 mm = 450 N | 450 N | 1.29 MPa | 2.0 MPa | 1.55 | PASS |
| Rib torsion, one foot loaded (side 15 N x 0.18 m = 2.7 N m), CF shear | 2.7 N m | 18.78 MPa | 30.0 MPa | 1.60 | PASS |
Rib torsional twist at that load: 5.9 deg (GJ 5.2 N m2, L 0.20 m): foot moves 19 mm sideways: MARGINAL stiffness, deliberate (keeps the fin mode below 1P).
| Fin root block on fin skins (60 x 40 mm both faces, 40 N) | 40 N | 0.02 MPa | 2.0 MPa | 111.30 | PASS |
| Rib tube in fin root block (60 mm embed), axial 84 N (2 feet x 42 N) | 84 N | 0.07 MPa | 2.0 MPa | 29.14 | PASS |
| Fin skin 0.1 mm CFRP bending at root (M 3.5 N m per half, kd) | 3.5 N m | 33.32 MPa | 450.0 MPa | 13.51 | PASS |
| Fin skin wrinkling on XPS core (0.5 (Ef Ec Gc)^(1/3), Ec 30, Gc 8 MPa EST) | same | 33.32 MPa | 114.5 MPa | 3.44 | PASS |
| Foot shoe bond on fin corner (12 x 15 mm pad footprint, shoe wraps 25 x 30 mm both faces = 1,500 mm2), 49 N + 20 N side | 52 N | 0.07 MPa | 0.1 MPa | 1.34 | PASS |
(shoe-bond allowable 0.1 MPa = C6 paper/foam value, `CL-C6-FOOT-SHOE-RF` basis: bond to foam core, not CF.)
Pack tray to hub (PETG, 600 mm2 bond) at 12 g: 32 N x 2.16 / 600 mm2 = 0.115 MPa vs 2.0: RF 17 PASS; strap: 2 x 20 mm Velcro, 32 N each side, `-` not tested.