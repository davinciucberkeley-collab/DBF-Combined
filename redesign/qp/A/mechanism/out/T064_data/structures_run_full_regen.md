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
Vs 12.07 m/s (CLmax 0.75 EST), VA = Vs sqrt(3.4) = 22.2, VC 17, VD 24 (D-186: VH 18.8 m/s x 1.25 = 23.5, rounded up; A.param THR_MAX 68 + FWD_BAT, AIRSPEED_MAX 18; flutter / divergence at VD 24 open, G8). a = 3.74/rad, mu_g 12.2, Kg 0.613.
| Case | n | Note |
|---|---|---|
| Gust U 8 m/s at VC | 3.85 -> stall-limited 1.98 | wing cannot make the gust n at 17 m/s |
| Gust U 4 m/s at VD (half, ASM-C1-UDE-D-FRAC) | 3.01 (stall line 3.96) | |
| Manoeuvre limit | +3.4 / -1.5 | A-P13 floor governs; ult +5.1 / -2.25; VA = 22.2 ~ VD |
| Spar root bending, flight n 3.4 (elliptical lift, inertia relief) | 1.84 N m (4.78 unrelieved) | design uses unrelieved 4.78 limit |
| Hover 8 m/s gust broadside (plate Cd 2.0): wing force 17.2 N, spar root | 1.94 N m | below flight case |
| Cage pitch moment, upper pair at the 0.90 cap (8.8 N each) / lower pair 1 N | 2.44 N m on the bridge | A-P8 85 % output limit not exceeded in SITL; this is the bound |
| Prop strike (blade stops, one motor, 30 N along thrust EST; K09-L P1 fuse idea) | arm root 8.3 N m; bridge 4.7 N m | damage case |
| Transport drop 0.3 m (v 2.43 m/s), cradle stroke s, efficiency 0.5 (ASM-C1-CRUSH-EFF) | n = v^2/(2 g eta s): s 25 mm: 24.0 g; s 35 mm: 17.1 g; s 50 mm: 12.0 g; s 60 mm: 10.0 g | `-` box cradle not designed; s needs >= 40 mm for n <= 15 |
| Landing (see s5) | foot plateau 30 N, 4 feet | worst-case values from landing_a.py are tabulated in s5 (n, foot load, side load, rib-root RF) |

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
- cruise 17 m/s (SITL fu_level.py, 7,300-7,540 rpm; mid 7,450): 7450 rpm: 1P 124 Hz, 2P 248 Hz
Cruise rpm 7,300-7,600 (QP-3 BOARD s1 item 2: sitl/fu_level.py with the APC V > 0 data, 17 m/s level at duty 0.60-0.70); the earlier 8,900-10,500 band was an estimate and is withdrawn; M8 audio FFT on the first cruise replaces it.

Modes with strong coupling to the motors (|phi| at motors in plane cy or thrust cx >= 0.5, mass-normalised), kd = E_CF 61 / PETG 1.6 GPa, nom 70 / 2.1, hi 90 / 2.4:
| Corner | f (Hz) | group | cx / cy | worst separation to 1P/2P at hover 6272 and cruise 7450 | worst incl. hover light | Result |
|---|---|---|---|---|---|---|
| kd | 3 | bridge 99% | 0.0 / 2.4 | 97 % | 97 % | PASS |
| kd | 11 | bridge 92% | 2.6 / 0.0 | 90 % | 89 % | PASS |
| kd | 15 | spar 53% | 2.0 / 0.2 | 86 % | 85 % | PASS |
| kd | 31 | spar 93% | 1.1 / 0.0 | 70 % | 69 % | PASS |
| kd | 38 | bridge 31% | 1.2 / 1.6 | 64 % | 62 % | PASS |
| kd | 45 | arm 100% | 1.3 / 3.0 | 57 % | 55 % | PASS |
| kd | 45 | arm 100% | 3.0 / 1.3 | 57 % | 55 % | PASS |
| kd | 46 | arm 80% | 0.5 / 2.9 | 56 % | 55 % | PASS |
| kd | 58 | arm 91% | 2.5 / 0.0 | 45 % | 43 % | PASS |
| kd | 58 | arm 56% | 0.0 / 2.1 | 45 % | 42 % | PASS |
| kd | 63 | bridge 62% | 0.6 / 1.9 | 40 % | 37 % | PASS |
| kd | 65 | spar 40% | 0.6 / 1.5 | 38 % | 35 % | PASS |
| kd | 588 | arm 100% | 0.0 / 0.6 | 137 % | 137 % | PASS |
| nom | 3 | bridge 99% | 0.0 / 2.4 | 97 % | 97 % | PASS |
| nom | 12 | bridge 92% | 2.6 / 0.0 | 89 % | 88 % | PASS |
| nom | 15 | spar 57% | 2.0 / 0.2 | 85 % | 85 % | PASS |
| nom | 34 | spar 93% | 1.1 / 0.0 | 68 % | 67 % | PASS |
| nom | 40 | bridge 34% | 1.3 / 1.6 | 62 % | 60 % | PASS |
| nom | 49 | arm 100% | 3.2 / 0.7 | 54 % | 52 % | PASS |
| nom | 49 | arm 100% | 0.7 / 3.2 | 54 % | 52 % | PASS |
| nom | 49 | arm 80% | 0.5 / 2.9 | 53 % | 51 % | PASS |
| nom | 62 | arm 91% | 2.5 / 0.0 | 41 % | 39 % | PASS |
| nom | 62 | arm 55% | 0.0 / 2.1 | 41 % | 39 % | PASS |
| nom | 67 | bridge 62% | 0.6 / 1.9 | 36 % | 33 % | PASS |
| nom | 69 | spar 39% | 0.6 / 1.6 | 34 % | 31 % | PASS |
| nom | 629 | arm 100% | 0.0 / 0.6 | 153 % | 153 % | PASS |
| nom | 669 | arm 94% | 0.5 / 0.0 | 169 % | 169 % | PASS |
| hi | 4 | bridge 99% | 0.0 / 2.4 | 96 % | 96 % | PASS |
| hi | 13 | bridge 92% | 2.6 / 0.0 | 87 % | 87 % | PASS |
| hi | 18 | spar 52% | 2.0 / 0.2 | 83 % | 82 % | PASS |
| hi | 38 | spar 93% | 1.1 / 0.0 | 64 % | 62 % | PASS |
| hi | 46 | bridge 31% | 1.2 / 1.6 | 56 % | 54 % | PASS |
| hi | 55 | arm 100% | 0.6 / 3.2 | 47 % | 45 % | PASS |
| hi | 55 | arm 100% | 3.2 / 0.6 | 47 % | 45 % | PASS |
| hi | 55 | arm 80% | 0.5 / 2.9 | 47 % | 45 % | PASS |
| hi | 70 | arm 90% | 2.5 / 0.0 | 33 % | 30 % | PASS |
| hi | 70 | arm 56% | 0.0 / 2.1 | 33 % | 30 % | PASS |
| hi | 76 | bridge 62% | 0.6 / 1.9 | 27 % | 24 % | PASS |
| hi | 79 | spar 40% | 0.6 / 1.5 | 25 % | 21 % | PASS |
| hi | 714 | arm 100% | 0.0 / 0.6 | 187 % | 187 % | PASS |

Fin out-of-plane modes (fin 75-95 % of strain energy) and weakly coupled spar / rib modes (cx, cy < 0.5):
| Corner | f (Hz) | group | worst separation (6272, light, 7450 rpm) | Result |
|---|---|---|---|---|
| kd | 84 | spar 64%, rib 32% | 16 % | MARGINAL |
| kd | 97 | spar 53%, rib 40% | 3 % | FAIL |
| kd | 206 | spar 77%, rib 22% | 1 % | FAIL |
| kd | 257 | rib 90%, spar 7% | 4 % | FAIL |
| kd | 273 | rib 76%, spar 22% | 10 % | FAIL |
| kd | 281 | spar 60%, rib 28% | 13 % | MARGINAL |
| kd | 347 | spar 94%, rib 6% | 40 % | PASS |
| kd | 380 | spar 67%, rib 19% | 53 % | PASS |
| kd | 478 | fin 92%, spar 5% | 93 % | PASS |
| kd | 486 | fin 84%, spar 9% | 96 % | PASS |
| kd | 549 | arm 92%, bridge 8% | 121 % | PASS |
| kd | 580 | arm 95%, bridge 5% | 133 % | PASS |
| kd | 611 | arm 100%, spar 0% | 146 % | PASS |
| kd | 611 | arm 100%, spar 0% | 146 % | PASS |
| kd | 640 | arm 97%, bridge 3% | 158 % | PASS |
| kd | 672 | arm 95%, bridge 4% | 171 % | PASS |
| kd | 690 | spar 99%, rib 1% | 178 % | PASS |
| kd | 764 | spar 76%, rib 21% | 208 % | PASS |
| nom | 90 | spar 64%, rib 32% | 10 % | MARGINAL |
| nom | 104 | spar 53%, rib 40% | 0 % | FAIL |
| nom | 220 | spar 77%, rib 22% | 5 % | FAIL |
| nom | 275 | rib 90%, spar 7% | 11 % | MARGINAL |
| nom | 291 | rib 76%, spar 22% | 17 % | MARGINAL |
| nom | 301 | spar 60%, rib 28% | 21 % | PASS |
| nom | 371 | spar 94%, rib 6% | 50 % | PASS |
| nom | 407 | spar 67%, rib 19% | 64 % | PASS |
| nom | 513 | fin 92%, spar 5% | 107 % | PASS |
| nom | 521 | fin 84%, spar 9% | 110 % | PASS |
| nom | 566 | arm 94%, bridge 6% | 128 % | PASS |
| nom | 594 | arm 98%, bridge 2% | 139 % | PASS |
| nom | 611 | arm 100%, bridge 0% | 146 % | PASS |
| nom | 611 | arm 100%, fin 0% | 146 % | PASS |
| nom | 700 | arm 93%, bridge 6% | 182 % | PASS |
| nom | 739 | spar 99%, rib 1% | 197 % | PASS |
| hi | 102 | spar 63%, rib 31% | 2 % | FAIL |
| hi | 118 | spar 53%, rib 40% | 5 % | FAIL |
| hi | 250 | spar 76%, rib 23% | 1 % | FAIL |
| hi | 310 | rib 89%, spar 7% | 25 % | PASS |
| hi | 330 | rib 74%, spar 22% | 33 % | PASS |
| hi | 340 | spar 60%, rib 27% | 37 % | PASS |
| hi | 422 | spar 94%, rib 6% | 70 % | PASS |
| hi | 455 | spar 61%, fin 22% | 83 % | PASS |
| hi | 542 | fin 90%, spar 6% | 118 % | PASS |
| hi | 555 | fin 74%, spar 15% | 124 % | PASS |
| hi | 669 | arm 91%, bridge 8% | 170 % | PASS |
| hi | 707 | arm 95%, bridge 5% | 185 % | PASS |
| hi | 748 | arm 100%, fin 0% | 201 % | PASS |
| hi | 748 | arm 100%, bridge 0% | 201 % | PASS |
| hi | 780 | arm 97%, bridge 3% | 214 % | PASS |

Forced response (C2 method): worst-phase modal sum, 4 rotors, unbalance U = 1.0 g mm per rotor (EST; ISO G16 prop is 0.27 g mm), 2P axial ripple 5 % of thrust (EST), damping 1 % (EST). Acceleration at the FC (spar centre):
| Corner | Point | IMU accel, 1P | IMU accel, 2P | fin tip accel 1P / 2P (m/s2) | limit | MS |
|---|---|---|---|---|---|---|
| kd | hover 6272 | 13.0 | 2.6 | 20.4 / 5.4 | 30 m/s2 | +1.3 |
| kd | cruise 7450 | 16.2 | 0.3 | 26.2 / 0.7 | 30 m/s2 | +0.8 |
| nom | hover 6272 | 14.1 | 2.6 | 19.4 / 5.1 | 30 m/s2 | +1.1 |
| nom | cruise 7450 | 17.1 | 0.3 | 24.0 / 0.6 | 30 m/s2 | +0.8 |
| hi | hover 6272 | 18.3 | 2.6 | 31.2 / 5.6 | 30 m/s2 | +0.6 |
| hi | cruise 7450 | 18.7 | 0.3 | 29.8 / 0.7 | 30 m/s2 | +0.6 |

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
Static (CG 22.9 mm aft of LE, feet at x 0.300, y +-0.38, z +-0.18; CG 0.275 m above feet): tip-over narrow axis **33.0 deg** (limit 30: sizing 33.2), wide axis 53.9 deg. Parked broadside to the wind: tips at 7.4 m/s (gust 8: crew catches or lays it down, as A-P9); restoring / overturning at 5 m/s 2.21. I (kg m2, about the CG): [0.0577, 0.026, 0.0625] (SITL plant used 0.053-0.064 roll).
Foot design (EST, CAD): PETG shoe bonded over the fin corner, 12 (y) x 15 (z) mm EVA/PE foam pad 30 mm thick, plateau stress 0.17 MPa -> **30 N per foot** (static load W/4 = 3.7 N: x8 below yield), usable stroke 20 mm, rigid stop beyond. Foam plateau and stroke are unmeasured: drop-test a coupon first (5 pads, 1.2 m/s on a scale).
Sim = `landing_a.py` (K09-L `team/C5/sim` physics rebuilt standalone for A: 6 dof, 4 elasto-plastic feet, friction 0.40 (assumed, see below), lift 2/3 W to 0.3 s then 0 at 0.6 s, 1.50 kg, current mass list of `landing_a.py` ITEMS (motor assemblies 4 x 88.26 g)):
| Case | max stroke (mm) of 20 | permanent set (mm) | peak foot load (N) | side load (N) | n at CG | end tilt (deg) | drift (mm) | rib-root RF |
|---|---|---|---|---|---|---|---|---|
| hard 1.2 m/s level | 8.3 | 6.8 | 40 | 0 | 10.8 | 0.0 | 0 | 104.39 |
| hard, 10 deg narrow | 13.9 | 12.4 | 40 | 14 | 5.4 | 1.8 | 142 | 4.72 |
| hard, 10 deg wide | 8.2 | 6.7 | 45 | 18 | 6.1 | 0.1 | 36 | 2.40 |
| hard, 7+7 deg combined | 9.2 | 7.7 | 45 | 18 | 5.7 | 0.4 | 21 | 1.26 |
| hard, 10 narrow + 0.5 m/s drift | 15.4 | 13.9 | 40 | 16 | 6.7 | 2.2 | 23 | 6.60 |
| hard, 10 wide + 0.5 m/s drift (y) | 11.0 | 9.5 | 47 | 19 | 6.3 | 0.4 | 104 | 2.68 |
| normal 0.5 m/s level | 2.3 | 0.8 | 33 | 0 | 8.9 | 0.0 | 0 | 126.14 |
| normal, 10 narrow | 3.3 | 1.8 | 34 | 13 | 6.9 | 0.1 | 97 | 5.85 |
| normal, 10 wide + drift | 5.8 | 4.3 | 40 | 16 | 5.4 | 0.3 | 101 | 3.08 |
| hard, 1.381 kg, 10 narrow | 12.9 | 11.4 | 40 | 14 | 5.8 | 1.6 | 144 | 4.70 |
Worst stroke 15.4 mm of 20 (margin 4.6 mm, 30 %): PASS. No tip-over in any case (end tilt <= 3 deg). Peak load factor 10.8 g vs A-P5 12 g: PASS (the 6 mm crush of SIZING-A is replaced: 12 g would need 6 mm only at constant force and a level hit; with 20 mm and 30 N the level hard case is below).
Pad life: normal landings set 0.8-4 mm; replace the pad at 10 mm cumulative set (a hard landing sets up to 13 mm: replace after any hard landing). Pads are $0 stock (foam); K09-L cartridges not used.
Side load per foot: worst 18.7 N at pad mu 0.40 (T-064: the earlier 'scaled K09-L cap about 14 N' (24.5 N x mass ratio) belonged to no part of A and is withdrawn; K09-L's 24.5 N was its own design value set equal to its own sim result, C5 CLOSURE s2, D-138). The limit is now the computed capacity of the failing part: the rib root (14x12 CF tube, x 0.0705 to the fin block) under combined bending (arm 0.2295 m), torsion (lever 0.18 m) and axial load, all four feet resolved in the body frame at every time step (`landing_a.py` rib RF = 1 / sqrt((KF (M/Z + N/A) / 350 MPa)^2 + (KF T r / J / 30 MPa)^2), KF 1.725; both allowables EST, no coupon). Minimum rib-root RF over these cases **1.26** (PASS at the EST allowables, UNVERIFIED until a twist coupon). The pad friction 0.40 is an assumption carried from K09-L (its pad face was UHMW-PE tape over neoprene, D-105); A's drawn pad is bare EVA/PE foam, friction not measured ('-'): drag-test it; the rib RF reaches 1 at mu about 0.51 in the worst case (`landing_side_a.py`). See AR-012 / D-213 proposals in `mechanism/out/T064_landing_side.md`.

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
Pack tray to hub (PETG flange 27.2 x 8 = 218 mm2 bond, D-208: the outer flange tabs were never attached to the hub) at 12 g: 32 N x 2.16 / 218 mm2 = 0.32 MPa vs 2.0: RF 6.3 PASS; strap: 2 x 20 mm Velcro, 32 N each side, `-` not tested.