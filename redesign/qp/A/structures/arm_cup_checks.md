# Arm and motor-cup checks (concept A)

Reproduce: `python -I redesign/qp/A/structures/arm_cup_checks.py`. Limit loads x factors as `structures_a.py` (KF 1.725 on CF/metal, KP 2.156 on printed/bonded). Allowables are the repo's EST values (structures_a.py L16-20; coupons not yet run).

## 0. Inputs
- Arm 12x10 CFRP: I 527 mm4, Z 87.8 mm3, EI 36.9 N m2 (E 70 GPa nom; kd 61 GPa gives 32.1); lever to the motor axis 246 mm.
- Thrust at the 0.90 spin cap 8.81 N / shaft torque 130 N mm (prop_a.py: APC 9x4.5MR PER3 table, 9349 rpm, P = 128 W, Q = P/omega); uncapped fault 10.38 N / 153 N mm at 10142 rpm (structures_a.py: the 0.153 N m value). Hover 3.96 N per motor (prop_a.py, 1.50 kg).
- 1P unbalance 1 g mm (iter3_run.md EST): force 0.96 N at the cap rpm, 0.63 N at cruise 7,600 rpm.
- Cup (wing.py L575-584): plate 33 x 33 x 5 mm (corner R 6), 4 holes 2.9 mm on 19 x 16; arm sleeve OD 19.2 / ID 12.2 (0.1 mm epoxy gap, D-198) / 28.5 mm long (y -25 .. +3.5) + a 1.0 mm wall lead collar y 3.5 .. 8.8 and a 4.8 mm lead hole through the plate at y 5.5 mm (D-198; net plate section 30.3 x 5 mm at the sleeve end); 25 mm embed, epoxy. **There are no screw bosses and no nut: the screws are M2.5x8 SHCS with heads on the plate REAR face, threading 3 mm into the tapped aluminium motor base** (propulsion.py `_m25_screw`, E-PRP STACK eng 3.0). The motor is pulled away from the plate by thrust, so the head bears on the PETG (pull-through) and the thread is loaded in tension.
- Strike (structures_a.py: 30 N EST): S1 axial 30 N along the shaft; S2 transverse 30 N at the prop plane 47 mm above the arm axis (35 mm above the motor base face, EST); S3 tangential blade stop, torque 2.4 N m about the shaft (r 80 mm EST). The repo's existing 7.4 N m arm-root number assumes force only; S3 adds the blade offset to the arm-root moment (arm row below).

## 1. Table
| Item | Load | Stress / value | Allowable | MS | Result |
|---|---|---|---|---|---|
| Cup screw M2.5 tension (4 screws), thrust 8.8 N x2 prying + 1P | 8.8 N + 1P 0.96 N: 5.5 N/screw | 2.77 MPa | 450.0 MPa | +161.18 | PASS (steel allowable EST) |
| Thread strip in tapped Al motor base, 3.0 mm engagement (2.0 min) | 5.5 N/screw | 1.36 MPa | 90.0 MPa | +65.13 | PASS (base alloy and thread depth not published (EST); min engagement used) |
| Head pull-through: PETG bearing under the 4.5 mm head (annulus 9.3 mm2) | 5.5 N/screw | 1.26 MPa | 20.0 MPa | +14.82 | PASS (no counterbore, no washer) |
| Plate punching shear round the head (pi x 4.5 x 5 mm), cross-layer allowable | 5.5 N/screw | 0.17 MPa | 9.5 MPa | +56.11 | PASS (printed with the shaft axis up: layer plane = plate plane (EST); worst case interlayer allowable used) |
| Plate bending, cantilever 6 mm past the sleeve end (2 screws, net section 30.3 x 5 mm after the D-198 lead hole) | 65 N mm | 1.12 MPa | 9.5 MPa | +7.51 | PASS (plate in bending uses the interlayer allowable (worst)) |
| Hole bearing, motor torque 0.130 N m shared on 2 of 4 screws (hole 2.9 x 5 mm) | 5.2 N/screw | 0.78 MPa | 20.0 MPa | +24.62 | PASS (friction of the clamped base ignored) |
| Cup-to-arm bond (25 mm embed, 12 mm tube), thrust shear + torque couple | 8.8 N, 130 N mm | 0.03 MPa | 2.0 MPa | +63.02 | PASS (end-loaded sleeve: no thrust couple (thrust line passes through the arm axis); allowable E-FIN-13 EST) |
| Sleeve wall hoop at the mouth, torque couple (3.5 mm wall, 6 mm bearing patch) | 5 N | 0.34 MPa | 20.0 MPa | +57.66 | PASS (same ring model as qp5_checks s2) |
| Plate-to-sleeve crest junction (12.8 x 20 mm strip), tension from thrust | 8.8 N | 0.07 MPa | 9.5 MPa | +127.03 | PASS |
| FAULT uncapped (10.4 N): head pull-through | 5.2 N/screw | 1.20 MPa | 20.0 MPa | +15.62 | PASS (ESC cap failed; ultimate factors kept) |
| Strike S1 axial 30 N: head pull-through | 15.0 N/screw | 3.48 MPa | 20.0 MPa | +4.75 | PASS |
| Strike S2 transverse 30 N (35 mm above base face): worst screw tension, + hover thrust share | 1050 N mm -> 33.8 N/screw | 7.84 MPa | 20.0 MPa | +1.55 | PASS (head pull-through; a blade force along z loads the 16 mm axis) |
| Strike S2: M2.5 screw tension | 33.8 N/screw | 17.20 MPa | 450.0 MPa | +25.16 | PASS |
| Strike S2: thread strip, 2.0 mm min engagement | 33.8 N/screw | 8.44 MPa | 90.0 MPa | +9.67 | PASS |
| Strike S2: plate cantilever bending beyond the sleeve end | 406 N mm | 6.92 MPa | 9.5 MPa | +0.37 | PASS |
| Strike S3 blade stop: hole bearing, torque 2.4 N m on 2 of 4 screws | 97 N/screw | 14.37 MPa | 20.0 MPa | +0.39 | PASS |
| Strike S3: M2.5 screw shear (shank, 2 screws), single shear | 97 N/screw | 49.17 MPa | 270.0 MPa | +4.49 | PASS (friction of the clamped base would share this load) |
| Strike S2/S3: cup-to-arm bond, torsion 30 N x 47 mm + torque couple 2.4 N m / 25 mm | 1.41 N m + 2.4 N m | 0.69 MPa | 2.0 MPa | +1.88 | PASS (vector sum of the two shear flows (EST convention of iter2_margins s1)) |
| Strike S3: sleeve wall hoop at the mouth (couple 96 N, 6 mm patch) | 96 N | 6.28 MPa | 20.0 MPa | +2.19 | PASS |
| Strike S2: plate-to-sleeve junction, in-plane shear into the crest (20 x 5 mm) | 30 N | 0.65 MPa | 9.5 MPa | +13.69 | PASS |
| Arm 12x10 root bending, strike force at the blade (lever 0.246 + 0.080 m) | 9.8 N m | 192.07 MPa | 350.0 MPa | +0.82 | PASS (iter2_margins.md uses 7.4 N m (no blade offset): +1.41; this is the worse case) |
| Arm 12x10 root bending, thrust at the cap, combined with torque (vector) | 2.17 N m | 42.64 MPa | 350.0 MPa | +7.21 | PASS (iter2_margins.md 2.17 N m; adds the torque out of plane) |
| Tip-over damage case, rigid ground, no prop crush: arm bending (2 tips share 1.36 J; NO ultimate factor) | F 94 N, 23.1 N m | 263.02 MPa | 350.0 MPa | +0.33 | PASS (blades (hit at 78 deg of tip) are the fuse, so this is an upper bound; CG drop 95 mm, E 1.36 J) |
| Tip-over case: cup head pull-through at that force (no factor) | 103 N/screw | 11.05 MPa | 20.0 MPa | +0.81 | PASS (same upper bound) |
| FATIGUE arm tube bending amplitude: 1P 0.51 N m x DAF 3.3 + control +-25% thrust (limit, no factor) | M_a 0.75 N m, mean 11 MPa, N1P 4.1e+06 | 8.58 MPa | 140.0 MPa | +15.32 | PASS (endurance = 0.40 x 350 MPa EST) |
| FATIGUE hub-socket bond, amplitude couple M_a/25 mm | 30 N | 0.06 MPa | 0.6 MPa | +8.38 | PASS (endurance 0.30 x 2.0 MPa EST) |
| FATIGUE hub-socket bond, 0 -> cap thrust cycles (2000 cycles), range | 87 N | 0.18 MPa | 1.1 MPa | +4.98 | PASS (allowable 0.55 x static at ~1e3-1e4 cycles EST) |
| FATIGUE hub arm-socket wall (2.0 mm, D-196), hoop amplitude, 6 mm patch | 30 N | 1.60 MPa | 4.0 MPa | +1.50 | PASS (endurance 0.20 x 20 MPa = 4 MPa EST) |
| FATIGUE hub arm-socket wall, 0 -> cap thrust cycles, 6 mm patch | 87 N | 4.60 MPa | 10.0 MPa | +1.17 | PASS (0.5 x static at ~1e3-1e4 cycles EST; the l = 12 mm patch halves it) |
| FATIGUE cup-to-arm bond, 1P couple + torque ripple | 1P 2.07 N at 47 mm | 0.01 MPa | 0.6 MPa | +66.22 | PASS |
| FATIGUE cup head pull-through (PETG), amplitude per screw | 2.8 N | 0.30 MPa | 4.0 MPa | +12.46 | PASS |
| FATIGUE cup plate cantilever bending, amplitude | 33 N mm | 0.26 MPa | 1.9 MPa | +6.25 | PASS (interlayer endurance 0.20 x 9.5 MPa) |
| FATIGUE M2.5 screw, amplitude (joint stiffness share 0.25 of the load; preload not published) | 2.8 N | 0.20 MPa | 56.2 MPa | +275.09 | PASS (loosening, not fatigue, is the risk: threadlocker + bench retorque) |
| Arm tip deflection at the cap (kd E 61 GPa, cantilever, rigid hub) | 8.8 N | 1.36 mm | - (info) | | INFO (nom E 70: 1.19 mm) |
| Thrust-line tilt at the cap: arm slope + torque slope (kd), toward the hub | 8.8 N + 130 N mm | 0.48 + 0.06 deg | - (no limit in the repo; info) | | INFO (lateral thrust 0.073 N per motor (0.8 % of thrust), same sense on the 4 arms (toward the hub): no net force, a symmetric trim of the 17 deg cant) |
| Same at hover thrust | 3.96 N | 0.61 mm, 0.21 deg | - | | INFO (SITL cant 17 deg: the hover tilt is a trim shift of the lever arm, not a controls problem) |
| CAD observation: screw heads vs sleeve wall (head envelope x -7..-4.5 mm, 4.5 mm dia)  | geometry | 18 % of head volume inside the sleeve wall | 0 % | | FLAG (heads of the two y = -9.5 screws lie in the printed sleeve; see ARMS.md) |

## 2. Counts and fatigue basis
- Sorties: 22 flight mornings (H2 plan s6; SCHEDULE-A.md) + 3 for the F04 redo = 25 mornings x 2 sorties = 50; 5 min flown per sortie (EST, BATT_LOW budget 4.78 min, MISSION.md s4); thrust stand and tether 60 min (EST). Life = 2 x (4.2 h + 1.0 h) = 10.3 h.
- 1P 111 Hz mean: 4.1e+06 cycles; 2P 8.3e+06; 0 -> cap thrust pulses 2000 (EST 20 per sortie); control-loop thrust cycles 1.8e+05 (10 Hz over 180 s hover, EST).
- Dynamic factor 3.3: iter3_run.md separates strongly coupled modes by 1.2 from 1P/2P (84-304 Hz excluded); the 3.3 is the undamped response at that edge, so conservative for the arm modes at 34-46 Hz which sit BELOW 1P (isolation, factor < 1).
- Endurance knock-downs (EST; see s5 sources): CFRP 0.40 of the static allowable, printed PETG 0.20, epoxy bond 0.30, all at 1e7 cycles with the limit load (no 1.5 or 1.15), and 0.5-0.55 at 1e3-1e4 cycles.

## 3. Arm tip deflection and thrust line
| Case | EI (N m2) | tip deflection (mm) | slope (deg) |
|---|---|---|---|
| hover 3.96 N, nom | 36.9 | 0.53 | 0.19 |
| hover 3.96 N, kd | 32.1 | 0.61 | 0.21 |
| cap 8.81 N, nom | 36.9 | 1.19 | 0.41 |
| cap 8.81 N, kd | 32.1 | 1.36 | 0.48 |
| uncapped 10.38 N, nom | 36.9 | 1.40 | 0.49 |
| uncapped 10.38 N, kd | 32.1 | 1.60 | 0.56 |

Slope under the cap thrust rotates the shaft toward the hub (the arm tip drops in the thrust direction, so its tangent tilts inward): thrust line tilt 0.48 deg + 0.06 deg from the torque slope = 0.53 deg (kd). This is rigid-hub, cantilever: the iter3 FE (hub and bridge compliance included) gives the arm modes. Printed hub socket and bond compliance add rotation: EST +0.1-0.3 deg, measured by the tap test below.

## 4. Tap-test thresholds (bench)
- Arm cantilevered in the finished cage, hammer at the motor, accelerometer or phone audio FFT: ideal rigid-hub first mode 45 Hz (E 70) / 42 Hz (E 61), tip mass 88 g (landing_a.py item) + 0.2357 x arm 13.6 g. The iter3 FE arm-dominant modes with hub and bridge compliance: kd 35.5-43.6, nom 38.0-46.0, hi 33.8-45.9 Hz (iter3_run.md).
- Accept 32-50 Hz per arm (FE envelope, rounded). Below 32 Hz: socket bond or hub wall soft, stop. Above 50 Hz: the arm is stiffer than the FE hi corner (check the tube wall). The four arms must agree within 8 % (a loose bond or a short embed shows as a low outlier). Any arm above 84 Hz or between 84 and 304 Hz is a repeat measurement before flight.
- Static tip-deflection test: clamp the cage at the hub, hang 0.90 kg (8.8 N) at the motor axis: deflection must lie in 1.2-1.6 mm; more than 1.6 mm means the socket or tube is soft.

## 5. Fatigue sources (checked 2026-11-15)
Searches found no single design value; the knock-downs above are EST, set at or below these loose references:
- CFRP: notched or impact-damaged carbon/epoxy fatigue limit about 55 % of UTS at 1e6 cycles (https://www.degruyterbrill.com/document/doi/10.1515/secm-2020-0037/html and the TU Delft AS4/8552 thesis, https://repository.tudelft.nl/file/File_b5b35b1d-36fb-408f-b792-879c810979b5); 0.40 used on the already-knocked 350 MPa allowable.
- Printed polymers: fatigue limits 7-25 % of static strength for ASA, PC, Nylon 12 (https://api.crossref.org/works/10.3390/polym18020302, snippet; PETG value not read; MDPI PETG S-N paper https://www.mdpi.com/2504-477X/5/3/76 not read in full); 0.20 used on the 20 MPa bearing allowable, 0.20 on the 9.5 MPa interlayer allowable.
- Epoxy bond: lap-joint fatigue strength about 50 % of static at 1e6 cycles (SMC adherend study, https://www.scinapse.io/papers/3012459098 and related); 0.30 used at 1e7 on the 2.0 MPa allowable.
