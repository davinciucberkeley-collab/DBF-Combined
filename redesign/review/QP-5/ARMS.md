# QP-5 ARMS: are the arms structurally good enough for flight?

Structures engineer, 2026-11-15. Status `CALC`, nothing tested. Numbers: `redesign/qp/A/structures/arm_cup_checks.md` (script `arm_cup_checks.py`, `python -I`, stdlib). Earlier checks: `iter2_margins.md`, `iter3_run.md`, `qp5_checks.md`. Loads and factors as `structures_a.py` (KF 1.5 x 1.15 = 1.725 on CFRP and metal, KP 2.156 on printed and bonded parts; strike 30 N EST). All allowables are the repo's `EST` values; no coupon has been run.

## 1. Answer

> **2026-11-16, FEA-ARM.md:** the 3-D FEA confirms the tube and cup numbers below, but this report assumed the hub held the socket rigidly. It does not: the 0.8 mm radial web that joins each socket to the hub sleeve fails at the worst flight case (392 MPa against 20, factor of safety 0.05). "Good enough for flight" below applies to the tube and the cup only; the hub needs a redesign (D-201).

**Yes for the carbon arm tubes and for the printed motor cups; not yet proven for the printed hub sockets, and one cup detail needs a CAD fix.** In plain terms:

- The 12 x 10 carbon arm tube is the strongest part of the chain. Thrust at the 0.90 cap bends it at 43 MPa against 350 (MS +7.2). A 30 N prop strike that includes the blade offset (30 N x 0.326 m = 9.8 N m) gives 192 MPa (MS +0.82); the earlier +1.41 used 7.4 N m and left the blade offset out.
- The motor cup (CGE-003, 4 g) passes every check I could make, at max thrust and at three prop-strike cases. The tightest are the plate cantilever past the sleeve end (MS +0.49) and the motor-torque bearing on the screw holes under a blade stop (MS +0.39).
- The weak link in the arm load path is the hub arm-socket wall, not the arm or the cup: `qp5_checks.md` s2 gives MS +0.05 with a 12 mm bearing patch and -0.47 with a 6 mm patch at 2.0 mm wall. It stays UNVERIFIED until the socket coupon pull test (section 5).
- Fatigue is not a driver at the counts expected (about 4e6 cycles at 1P over a 10 h life, 2,000 cycles to the cap): the lowest fatigue MS is +1.17 (hub socket wall, cap cycles). The knock-downs are EST.
- Deflection is small: 1.2-1.4 mm at the cap, 0.5 deg of thrust-line tilt, same sense on all four arms.

## 2. Margins (limit x factors; MS = allowable / stress - 1; `PASS` at MS >= 0.15)

| Item | Load | Stress | Allowable | MS | Source |
|---|---|---|---|---|---|
| Arm 12x10 root bending, cap thrust 8.8 N + torque 0.13 N m | 2.17 N m | 42.6 MPa | 350 | +7.21 | CALC; `iter2_margins.md` (+7.23) |
| Arm root bending, strike 30 N at the blade (lever 0.326 m) | 9.8 N m | 192 MPa | 350 | +0.82 | CALC, blade offset EST |
| Cup screws M2.5 tension (cap thrust, 1P, x2 prying) | 5.5 N each | 2.8 MPa | 450 | +161 | CALC |
| Thread strip, tapped aluminium base, 2 mm engagement | 5.5 N | 1.4 MPa | 90 | +65 | CALC; base alloy and depth unpublished, EST |
| Head pull-through, PETG bearing (head 4.5 mm on plate, no washer), cap + 1P | 5.5 N | 1.3 MPa | 20 | +14.8 | CALC |
| Same, uncapped fault 10.4 N | 5.2 N | 1.2 MPa | 20 | +15.6 | CALC |
| Cup-to-arm bond, thrust + torque (25 mm embed) | 8.8 N | 0.03 MPa | 2.0 | +63 | CALC |
| Strike S1 axial 30 N, head pull-through | 15 N each | 3.5 MPa | 20 | +4.75 | CALC |
| Strike S2 transverse 30 N at 35 mm above the base face, head pull-through | 33.8 N each | 7.8 MPa | 20 | +1.55 | CALC |
| Strike S2, plate bending past the sleeve end (6 mm cantilever, 33 x 5 mm) | 0.41 N m (4 screws x 33.8 N, 6 mm lever) | 6.4 MPa | 9.5 | +0.49 | CALC |
| Strike S3 blade stop, hole bearing (torque 2.4 N m, 2 of 4 screws) | 97 N each | 14.4 MPa | 20 | +0.39 | CALC; friction ignored |
| Strike S3, M2.5 shank shear | 97 N | 49 MPa | 270 | +4.5 | CALC |
| Cup-to-arm bond, strike torsion 1.41 N m + torque couple 2.4 N m | | 0.69 MPa | 2.0 | +1.88 | CALC; allowable `E-FIN-13` EST |
| Sleeve wall hoop at the mouth, strike couple (3.5 mm wall) | 96 N | 6.3 MPa | 20 | +2.19 | CALC |
| Tip-over, rigid ground, blades not yielding, NO factor (see s3) | 94 N per arm tip, 23 N m | 263 MPa | 350 | +0.33 | CALC |
| Fatigue: arm tube amplitude 8.6 MPa at 4e6 cycles | | 8.6 MPa | 140 | +15.3 | CALC, 0.40 EST |
| Fatigue: hub socket bond, 0-cap cycles | 87 N | 0.18 MPa | 1.1 | +4.98 | CALC, EST |
| Fatigue: hub socket wall (2.0 mm), 2,000 cap cycles, 6 mm patch | 87 N | 4.6 MPa | 10 | +1.17 | CALC, EST |
| Fatigue: hub socket wall amplitude at 4e6 cycles, 6 mm patch | 30 N | 1.6 MPa | 4 | +1.50 | CALC, EST |
| Fatigue: cup head pull-through / bond / plate / screw | | | | +12 / +66 / +6.9 / +275 | CALC, EST |

Full table with every row: `arm_cup_checks.md` s1. Geometry used (all from `cad/amodel/wing.py` L31-32 and L575-584, `propulsion.py`): plate 33 x 33 x 5 mm; sleeve OD 19 / ID 12 / 28.5 mm; 25 mm embed; 4 clearance holes 2.9 mm on 19 x 16. **There are no screw bosses and no nuts.** The M2.5x8 SHCS heads sit on the plate rear face and thread 3 mm into the tapped motor base (`STACK` eng 3.0). Thrust pulls the screws out of the motor thread and the heads into the PETG.

Loads: thrust 8.81 N, torque 0.130 N m at the cap (APC 9x4.5MR PER3 table at 9,349 rpm, 128 W / omega, `prop_a.py`); uncapped 10.38 N / 0.153 N m. 1P force 0.96 N (1 g mm, `iter3_run.md` EST).

## 3. Hard landing and tip-over

The arm cannot touch the ground in a normal landing: the feet at the fin tips are 0.375 m below the motor axis (`landing_a.py`: all ten landing cases end with tilt <= 3 deg). Only a tip-over reaches it. Tipping from the balance point about the narrow axis (33.2 deg), the prop blade tips strike at 78 deg of tilt, after a CG drop of 95 mm (1.36 J, 1.46 kg). If both arm tips took all of it with no blade crush, the arm sees 94 N and 23 N m: 263 MPa without any factor (MS +0.33, but 454 MPa at 1.5 x 1.15, which would fail). The APC blades break or bend first and the motor cup head pull-through at the same force is 11 MPa (MS +0.81, no factor). So the blades are the fuse; the tip-over case is a bound, not a design load. Not covered: a drop of the aircraft onto an arm at transport (cradle not designed, `structures_a.py` s2).

## 4. Fatigue basis

Counts (`SCHEDULE-A.md`, H2 plan s6): 22 flight mornings + 3 for the F04 redo = 25 x 2 sorties = 50 sorties, 5 min flown each (EST; BATT_LOW budget 4.78 min, `MISSION.md`), plus 60 min thrust stand and tether (EST), life factor 2: 10.3 h. 1P at 111 Hz mean gives 4.1e6 cycles (2P 8.3e6). Thrust pulses to the cap: 20 per sortie EST, 2,000. Control-loop cycles: 1.8e5.

Endurance (1e7 cycles) knock-downs on the static allowable: CFRP 0.40, printed PETG 0.20, epoxy bond 0.30; 0.5-0.55 at 1e3-1e4 cycles. **All EST.** Searches on 2026-11-15 found no design value for any of the three; the references that came back: notched or damaged carbon/epoxy about 55 % of UTS at 1e6 cycles (https://www.degruyterbrill.com/document/doi/10.1515/secm-2020-0037/html); printed ASA, PC and Nylon 12 fatigue limits 7-25 % of static (https://api.crossref.org/works/10.3390/polym18020302, snippet only; PETG not read; PETG S-N paper https://www.mdpi.com/2504-477X/5/3/76 not read in full); epoxy lap joints about 50 % of static at 1e6 cycles (https://www.scinapse.io/papers/3012459098). Loosening of the M2.5 screws under 1P is the realistic cup fatigue risk, not stress: use threadlocker and a torque mark; check at each bench run. Heat from the motor into the PETG plate is not analysed (PETG softens near 70-80 deg C, EST): measure it (section 6).

## 5. Deflection and tap thresholds

Cantilever, rigid hub, E 61-70 GPa (EI 32-37 N m2): tip 0.53-0.61 mm at hover thrust, 1.19-1.36 mm at the cap, 1.40-1.60 mm uncapped. The shaft tilts toward the hub by 0.41-0.48 deg (+0.06 deg from motor torque): lateral thrust 0.07 N per motor, 0.8 % of thrust, same sense on all four arms, so no net force, a trim of the cant. Hub socket and bond compliance add EST 0.1-0.3 deg.

Bench thresholds:
- Tap each arm in the built cage: first arm mode 32-50 Hz (FE envelope 33.8-46.0 Hz, `iter3_run.md`; ideal rigid hub 42-45 Hz); four arms within 8 % of each other; nothing between 84 and 304 Hz without a repeat. Below 32 Hz stop: socket or bond is soft.
- Static: clamp the hub, hang 0.90 kg at the motor axis: tip deflection 1.2-1.6 mm; more means a soft socket.

## 6. Failures and proposed fixes

No margin below zero in the arm or the cup. Two items need action:

1. **CAD, screw heads inside the sleeve wall.** The heads of the two y = -9.5 screws (head x -7 to -4.5 mm, 4.5 mm dia) lie 18 % inside the printed sleeve wall (the sleeve spans y -25 to +3.5, ro 9.5 mm; the +9.5 screws are clear). `propulsion.py` seat call exempts the `motor screw` bodies, which hides it. Either the sleeve is cut for the heads or the screws will not seat. Proposed (file `cad/amodel/wing.py`, `build_cage`, after the four `motor screw hole` cuts): head pockets `cup.cut_cylinder('X', (-0.0070, sy*CUP_PAT[0]/2, sz*CUP_PAT[1]/2), 0.0030, 0.00250, name='screw head pocket 5.0 mm')` for the two screws with sy = -1. Mass delta about -0.05 g per cup (EST, a few mm3 of PETG); strength unchanged to the precision of these checks (the wall there is 0.6-2 mm of the 3.5 mm ring and the pocket leaves the crest strip |z| < 5.75 mm intact). If the CAD agent prefers, a 0.5 mm shorter sleeve will not clear it: the pocket is the fix.
2. **Hub arm-socket wall (existing item, qp5_checks s2).** Still the weakest part of the arm chain on the crude 6 mm patch model (MS -0.47 static). No new geometry proposal here: run the coupon; if it fails at 332 N x 1.5, raise `HUB_SOCK_W` from 2.0 mm to 2.6 mm (hub +1.5 g EST, scaled from the D-196 note: a full 2.0 mm socket would be 24.7 g) or lengthen `HUB_MOUTH` from 12 to 18 mm.

Optional, not required: if S2 plate bending (+0.49) is judged too thin once coupons come back, extend the sleeve from `SLV_Y1` +3.5 to +9.5 mm (+0.4 g per cup, EST) to support the +y screws.

## 7. Bench tests

Add to the hub coupon pull test (`qp5_checks.md` s2): a cup coupon (printed CGE-003, 150 mm of 12 x 10 tube bonded 25 mm, aluminium dummy motor with four tapped M2.5 holes, or a spare MN2212), 3 coupons:
- Axial pull 65 N (30 N x KP) at the shaft axis, hold 10 s: no slip, no crack.
- Transverse load 65 N at 35 mm above the base face (y and z directions): screw heads pull through at no less than 65 N; record deflection.
- Torque 5.2 N m about the shaft (2.4 x KP) through the dummy motor, then 3.0 N m about the arm axis (30 N x 47 mm x KP): no rotation of the cup on the tube, no hole elongation.
- Pull one M2.5 screw from the real motor base to read the thread depth and strip load (needs 100 N, EST), and measure the real tapped depth against 3.0 mm.
Also: a 30 min thrust-stand run per motor at 70 % duty with the cup and tap test before and after (frequency shift < 3 %), cup plate temperature at hover and at the cap (limit 55 deg C EST), screw torque marks intact; one flight card entry per sortie for tap and torque-mark check.

## 8. Claims

Eight stored claims added to `redesign/qp/A/proofs/claims_a2_struct.py` (`CL-A-MS-CUP-*`, `CL-A-MS-ARM-BLADE`, `CL-A-MS-FATIGUE-*`), params in `gen_params_a.py` (`struct.ms_cup_*`, source `SRC-A-ARMCUP` in `claims_a0_base.py`). `run_all.py` strict: 0 fails.
