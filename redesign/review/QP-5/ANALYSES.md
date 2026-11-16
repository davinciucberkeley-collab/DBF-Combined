# QP-5 analyses after the CAD fidelity round (D-193 / D-194 / D-195)

Date 2026-11-15. Owner: analyses engineer. Scope: re-run of the analyses that `CAD-INTEGRATION.md` s7 listed as invalidated. Labels: `V` source read, `CALC` computed here, `SITL` ArduPlane 4.7.3-beta1 stock tailsitter + `a_plant.py`, `EST` estimate, `-` unknown. Nothing was committed or published. All numbers are for the CAD of 2026-11-15 (basic 1,259.14 g, CG 21.47 mm, Ixx / Iyy / Izz 0.0655 / 0.0270 / 0.0722 kg m2, `sitl/cad_mass.json`).

## 1. Verdict

| # | Item | Result | Limit | Status |
|---|---|---|---|---|
| 1 | S5010 aero (Cm0, alpha0, NP, SM, trim) | Cm0 +0.008, alpha0 -0.52 deg, SM 7.8 % at the CAD CG, trim 4.8 deg TE up at 17 m/s | SM >= 5 % | PASS; CLmax is still `EST` (no measured value found) |
| 2 | Mass | 1,449 / 1,454 g predicted; **accepted, target re-based 1.44 -> 1.46 kg (D-195)** | gate 1.47 kg | PASS vs the new target; 16-21 g to the gate |
| 3a | Elevon flutter, lowest onset with damper | 38.5 m/s hot, 42.0 nominal, 45.0 cold; half-filled damper 33.0 | 28.8 m/s (1.2 VD) | PASS (the half-fill fault case now passes; it failed at 28.5 before) |
| 3b | Wing flutter | 46.1 m/s base, 33.4 m/s fins off (kd) | 28.8 | PASS |
| 3c | Pushrod buckling, 52.5 mm | Pcr 73 N vs 60 N ultimate stall load, MS +0.21 | MS >= 0 (0.15 preferred) | PASS, thinner than the 42.5 mm rod (MS +0.85) |
| 3d | Hub arm-socket wall 0.8 mm | MS -0.58 on a crude hoop model; passes only from 2.0 mm walls | MS >= 0 | **OPEN / not demonstrated** (ASM-A-HUB-WALL, UNVERIFIED) |
| 3e | Spar foam shear (6.27 / 5.62 mm ligament) | 58 kPa bond zone (MS +0.48), 7 kPa ligament (MS +10.8) | 86 kPa (`EST`) | PASS |
| 4a | SITL transition, cant 17, D-191 gains | no elevon saturation, peak elevon 11.5 deg (pitch use 0.575), V 17.0-17.2 m/s, no fence crossing | pitch use <= 0.60 | PASS |
| 4b | SITL back-transition + QLAND, landing | sink 0.17-0.25 m/s, no tip-over, motor peak 0.883 | cap 0.90 | PASS |
| 4c | SITL roll at cruise speed | 106.9 deg/s at 1.455 kg, 106.4 deg/s at 1.47 kg | >= 90 | PASS (86.7 deg/s only below 15 m/s) |
| 4d | SITL hover wind 4 m/s, turbulence 1.0 | longest >= 0.85: 0.20 s, at cap: 0 s, peak 0.884 | <= 0.5 s, 0 s at cap | PASS |
| 4e | **A-P8a turbulence heading margin** | yaw error 8.5-14.0 deg in 6 of 7 runs, **25.4 deg in seed 3** | <= 15 deg (conditional wording) | **OPEN** (marginal as before; 23.1 deg at QP-4) |
| 4f | Roll-loop gain margin (cage modes) | roll min GM 2.37 nominal, 2.16 modes -20 %; all axes min 2.16 | >= 2.0 | PASS (was 2.03) |
| 5 | G7 cost | $1,775.09, +30 % unverified margin +$105.08 | >= $100 and <= $1,800 | PASS (fragile, see 6) |
| 6 | Claims | 82 claims, 22 requirements, **0 failing** (strict), no warnings | 0 | PASS |

## 2. S5010 aero (item 1)

**Sources.** (1) Section table, aerodesign.de, `https://www.aerodesign.de/english/profile/profile_s.htm`, S5010 row: camber 2.20 %, thickness 9.83 %, cm0 +0.0080, a0 -0.52 deg (read 2026-11-15 via WebFetch). (2) 2-D CFD (Mat Yazik et al., `https://semarakilmu.com.my/journals/index.php/fluid_mechanics_thermal_sciences/article/view/3720`): stall angle 11 deg, best L/D at 7.8 deg (abstract only; the full text returned HTTP 403, 2026-11-15). (3) Coordinates `subsystems/wing/s5010.dat` (UIUC, checked 2026-11-09). (4) Own inviscid Hess-Smith panel check, `qp/A/aero_s5010.py`. airfoiltools.com was unreachable (connection refused, 2026-11-15) and the UIUC polar database was not read, so **no measured S5010 CLmax or polar was found**.

| Quantity | Value | Basis |
|---|---|---|
| Cm0 about c/4 | +0.0080 (was 0.015 `EST`) | table; panel 0.0070-0.0098 (n 120-360) |
| Zero-lift angle | -0.52 deg (was 0) | table; panel -0.51 to -0.54 deg |
| Section AC | 0.248 c (n 240), 0.246 c (n 360) | panel `CALC`; the 0.25 c assumption holds |
| CLmax (3-D wing) | 0.75 `EST`, unchanged | 2-D CFD stall 11 deg x CLa 3.74 /rad from alpha0 gives CL 0.75: consistent, not a measurement |
| NP | 40.7 mm `EST`, unchanged (45.6 mm inviscid -3.3 mm viscous by the SIZING-A rule with a_w from CLa 3.74; 39.6 mm with the CAD prop plane at x -110 mm instead of SIZING-A's -85 mm) | `aero_s5010.py` |
| SM at CG 21.47 mm | 7.8 % (7.4 % with NP 39.6) | limit 5 % |
| Trim elevon, 1.455 kg | 6.7 / 4.8 / 4.1 deg TE up at 15 / 17 / 18 m/s (alpha 6.7 / 5.1 / 4.5 deg); at 17 m/s 5.5 deg at CG 19.3 and 4.1 deg at CG 23.6 | stop 21 deg; was 2.9-3.4 deg at 17 m/s before (CM0, CG 24.4 -> 21.5) |

The model constants are in `sitl/a_aero.py` (`CM0`, `A0`, applied as CL = CLa (alpha - alpha0)). Not changed and still `EST`: CD0 and e (calibrated to MISSION s1), elevon effectiveness tau 0.5, CLP, hinge-moment coefficient. Peak hinge moment at 18 m/s and the 20 deg stop (`fwd_checks.py`) is unchanged at 0.048 N m per elevon.

## 3. Mass decision (item 2)

Predicted take-off mass: itemised growth by maturity **1,449 g** (`mission_gate_a.py` re-based on the CAD part table: wing 221.7, fins + feet 118.0, motors 260, props 44.2, adapters + spinner nuts 28.8 (CALC, 10 % growth), ESC 20.04, pack 270, strap 3, avionics + harness 106.38, servos + linkage 47.54, cage 113.4, hardware 26.08 = 1,259.14 g; growth 142.2 g; overrun 48 g); flat rule basic x 1.1174 + 47 g = **1,454 g** (CAD-INTEGRATION used 48 g: 1,455). Both are over the old 1.44 kg target by 9-14 g and under the 1.47 kg gate by 16-21 g.

**Decision (D-195): accept, re-base the target to 1.46 kg, cut nothing.** Reasons are in `qp/A/MASS-GATE.md` s9. In short: the +28.8 g adapter and nut line is real hardware no earlier lump carried; the prediction already includes 190 g over the CAD basic (142 growth + 48 overrun) and the gate is reached only at +211 g; every performance limit holds at 1.455-1.46 kg.

| At | T/W fresh (cap 0.90) | T/W sag (cap) | Transition window | Cruise to BATT_LOW (need 3.41 min) | Pack margin |
|---|---|---|---|---|---|
| 1.449 kg | 2.37 | 1.87 | +-6.0 % | 4.34 min | 1.12x |
| 1.455 kg | 2.36 | 1.87 | +-5.8 % | 4.31 min | 1.11x |
| 1.46 kg (target) | 2.35 | 1.86 | +-5.6 % | 4.27 min | 1.11x |
| 1.47 kg (gate) | 2.34 | 1.85 | +-5.3 % | 4.21 min | 1.10x |

Limits: T/W fresh >= 2.0, sag >= 1.6 (capped), window >= +-5 %. Required real EST cuts for the new target: 36.2 g of the 41.6 g (was 54 g needed for 1.44 kg: that claim would have failed). Structure 479.3 g (wing 221.7, fins 109.6, feet 8.4, hardware 26.1, cage 113.4) against the 494 g ceiling. Stall at 1.455 kg: 11.99 m/s, 1.3 Vs 15.6 m/s (cruise 17). Fallbacks, not applied: lead 15.6 -> 12.8 g (-5.6 g; flutter case F below passes), T-Motor hardware pack may hold the adapter (no BOM line either way), hub bosses to 2.0 mm would add 7.1 g.

## 4. Structures (item 3)

Files: `structures/flutter_d195.py` -> `flutter_d195.md`, `flutter_d195_wing.py` -> `flutter_d195_wing.md`, `qp5_checks.py` -> `qp5_checks.md`, `iter3_run.py` -> `iter3_run.md`, `landing_a.py`.

**Elevon flutter.** `fixes2_run.py` p-method (3-DOF Theodorsen-Garrick + Jones lag, K sweep 0.01-20 N m/rad, 600 points) re-run with elevon 6.7 g (was 9.6), lead 15.6 g at 20 mm, tabs 0.5 g, damper c 1.0297e-3 N m s/rad (`amodel/wing.py` DMP_C, unchanged). The section model's hinge inertia (elevon plate c^2/3 + lead x arm^2) is 1.482e-5 kg m2 against the CAD 1.485e-5. The elevon CG balanced is -7.63 mm ahead of the hinge (was -6.06): more over-balanced, which is why the lighter elevon does not hurt. BAL_DZ -3.3 mm is a z offset out of the section plane; it enters only through the hinge inertia.

| Case | kd / nom / hi lowest onset (m/s) | Limit 28.8 |
|---|---|---|
| A no damper | unstable at 60 / 42 / 25 of 600 K points (onset 18.5 / 20.0 / 22.5) | FAIL without the damper, as before: the damper is required |
| B damper hot 50 C (EST x0.6) | 38.5 / 41.5 / 46.0 | PASS |
| C damper nominal 25 C | 42.0 / 45.5 / 50.5 | PASS |
| D damper cold 0 C (EST x2) | 45.0 / 49.0 / 55.0 | PASS |
| E half-filled damper (0.3 c) | 33.0 / 35.0 / 39.0 | PASS (was 28.5 FAIL) |
| F lead 12.8 g, hot damper | 37.5 / 40.0 / 44.0 | PASS (the 5.6 g cut is allowed) |
| G previous design (elevon 9.6 g, damper nominal), for reference | 40.5 / 43.5 / 48.5 | |

**Wing bending-torsion flutter** (Ritz + strip Theodorsen, lumps 26.6 g per semispan: lead + tabs + two 3.98 g caps + half a damper): fin on tip 46.1 / 49.4 / 56.3 m/s; fins off 33.4 / 39.4 / 45.9 m/s (kd / nom / hi); line 28.8. Divergence and reversal were not re-run: the elevon span, hinge position and spar are unchanged and the S5010 camber (2.2 %) changes the section moment only slightly; they keep the QP-4 values (128 m/s, reversal 37 / 42 m/s on the 3-D basis, `EST`).

**Pushrod buckling** (`qp5_checks.md` s1). 1.2 mm steel, E 200 GPa `EST`, pinned-pinned, Euler. 52.5 mm: Pcr 73 N. Load: servo stall 0.397 N m (`review/QP-4/SERVO.md`) over the 12 mm arm, 33.1 N, 34.8 N at the 18.3 deg arm angle, x KF 1.725 = 60.1 N ultimate: **MS +0.21 PASS** (42.5 mm: Pcr 111 N, MS +0.85). The governing case is the fault where the servo is driven into the stop; the flight hinge-moment load is 3.7 N. Axial stress 53 MPa.

**Hub socket wall** (`qp5_checks.md` s2). The hub is a printed PETG boss, 0.8 mm wall round the 12 mm arm tube, 25 mm deep (`HUB_W`, `EST`). Load: strike couple 8.3 N m over the 25 mm socket = 332 N (`structures_run.md`). Crude thin-ring model, hoop tension 2F/(pi l) per unit length, ultimate factor KP 2.156, allowable 20 MPa `EST`:

| Wall (mm) | l = 12 mm: MS | l = 6 mm: MS |
|---|---|---|
| 0.8 (drawn) | -0.58 | -0.79 |
| 1.2 | -0.37 | -0.68 |
| 1.6 | -0.16 | -0.58 |
| 2.0 | +0.05 | -0.47 |

The previous iteration-2 margin (+0.48) was a bond margin and a solid-wall bearing check; it does not cover a 0.8 mm wall. The ring model ignores the epoxy fill and the tube bonded inside, so it is conservative, but it is not a measurement. **Not demonstrated at 0.8 mm.** Recorded as ASM-A-HUB-WALL (UNVERIFIED) on CL-A-MS-ARM-SOCKET. Options: print, bond and pull-test a socket coupon in a strike-couple fixture before the hub is committed; or 2.0 mm arm bosses (+7.1 g, takes the predicted mass to about 1,461 g, over the 1.46 kg target, inside the 1.47 kg gate).

**Spar foam** (`qp5_checks.md` s3). Foam above / below the 12 mm bore is now 6.27 / 5.62 mm. Bridge torque 2.44 N m through the bond on the bore (r 6 mm): 77.5 kPa over |y| <= 0.15 m (MS +0.11), **58.1 kPa over the FIXES2 rule |y| <= 0.20 m (MS +0.48)** against 86 kPa (`EST`, scaled from the 103 kPa compressive data sheet, no shear row exists). Ligament shear from the 3.4 g lift at 1.47 kg: 7.3 kPa (MS +10.8). Ligament ring under the bridge torque: 15.5 kPa (MS +4.5). The 5.6 mm ligament is not shear-limited; the 0.20 m bond rule still governs.

**Cage modes and rate loop** (`iter3_run.py`, with `fe_a.py` motor lump 81.06 -> 88.26 g for the adapter and spinner nut): strongly coupled modes below the rotor bands 63 / 67 / 77 Hz (limit 83.6), above 432 / 462 / 524 Hz (limit 304); FC vibration 25.8-27.1 m/s2 kd, 23.7-23.9 nom / hi (limit 30; was 27.1-28.5 / 25.0-25.1). **Rate-loop gain margin** with the D-191 gains: nominal pit 4.19 / 4.25 / 5.88, **roll 2.37 / 2.56 / 3.32**, yaw 2.19 / 2.23 / 2.23 (kd / nom / hi); modes -20 %: min 2.16 (pitch 2.68, roll 2.16, yaw 2.16); modes +20 %: min 2.23. Limit 2.0. The roll axis is the minimum at nominal frequencies (2.37, kd). The values rose against QP-4 (2.03) because the heavier motors lower the cage modes; `EST` motor lag 40 ms and delay 4 ms are unchanged.

**Landing** (`landing_a.py`, 1.50 kg scaled, motor lump 88.26 g): tip-over angle 33.0 deg narrow side (was 33.2 `EST`); hard landing 1.2 m/s worst case 10.9 mm of the 20 mm stroke (45 N plateau), foot force 65 N, no tip-over. The stored claim value (15.2 mm, iteration 2) is kept as the more conservative figure.

## 5. SITL at cant 17 with the D-191 gains (item 4)

Setup: `qp/A/sitl/run_fwd.py` (cant 17 by default now; it had 16 baked in; new keys `cg` mm and `rollthr`), `run_case.py` for hover, `A.param` D-191 gains (pitch P 0.12 / D 0.0012 / FLTD 60, yaw P 0.37), `Q_WVANE_ENABLE` 0, `THR_MAX` 80 (as the Z5 runs), thrust scale 0.767 (worst pack) in hover, `a_aero.py` with the S5010 constants and the CAD CG, mass and inertia. Job lists `jobs_qp5.txt`, `jobs_qp5b-d.txt`, `batch_qp5.sh`; 30 runs `runs/R5_*` (run directories are git-ignored). Reproduce: `SCR=<scratch> bash batch_qp5.sh`, then `python fwd_sum.py R5_*`.

| Run | Mass kg | Case | Result |
|---|---|---|---|
| R5_t0 / R5_g0 | 1.455 / 1.47 | transition, calm | peak elevon 11.5 / 11.5 deg (pitch use 0.575), no saturation, alpha max 9.7 deg, 1.3 Vs reached in 7.3 s, V end 17.0 m/s, pack peak 23.2 A |
| R5_t5c / R5_t5h | 1.455 | transition, 4 m/s cross / head | elevon 10.3 deg, motor u max 0.826 / 0.820 |
| R5_b0 / R5_b45 / R5_gb45 | 1.455 / 1.455 / 1.47 | transition + back-transition + QLAND, 0 / 4 m/s | u max 0.875 / 0.851 / 0.883 on the back-transition, lean in descent 3.4 / 15.2 / 15.1 deg, no fence crossing |
| R5_l0 / R5_l4 | 1.455 | QLAND from 20 m, 0 / 4 m/s | touch 0.25 / 0.17 m/s sink, lean at touch 0.1 / 5.4 deg, no tip-over |
| R5_cgf / R5_cgfw | 1.455 | transition at CG 19.3 (forward trim end), calm / 4 m/s | elevon 12.0 / 11.6 deg (pitch use 0.59 of 0.60), no saturation |
| R5_cga | 1.47 | transition at CG 23.6 (aft trim end), 4 m/s | elevon 9.4 deg (0.47) |
| R5_rt65 / R5_rt65g / R5_rt65f | 1.455 / 1.47 / 1.47 (CG 19.3) | roll steps, stick held (V 16.3-19 m/s) | **106.9 / 106.4 / 106.7 deg/s**, differential 13.0 deg |
| R5_rt75 / R5_rt85 | 1.455 | same, more throttle (V 18-19 m/s) | 118.8 / 125.2 deg/s |
| R5_roll / R5_rollg / R5_rollf / R5_rolla | 1.455 / 1.47 / 1.455 CG 19.3 / CG 23.6 | roll steps at the QP-4 stick (1500), V 14.4 m/s | 86.7 / 85.7 / 81.9 / 91.2 deg/s, elevon at its 20 deg stop |
| R5_h60 .. h90 (7 runs) | 1.455 | hover, wind 4 m/s mean (6.3-7.3 m/s with turbulence 1.0), from 60 / 60 s2 / 60 s3 / 70 / 70 s2 / 80 / 90 deg | peak output 0.844 / 0.822 / **0.884** / 0.839 / 0.832 / 0.844 / 0.846; time >= 0.85: 0.20 s in s3, 0 elsewhere; at the 0.90 cap 0 s; lean max 14.6-26.4 deg; **yaw error 10.8 / 13.3 / 25.4 / 11.4 / 14.0 / 10.1 / 8.5 deg** |

**Roll rate: what changed and why it matters.** The QP-4 roll runs (92.9 / 94.1 deg/s) and the first R5 runs (86.7 / 85.7) are not cruise states: `case=roll` flies the steps in FBWA with the throttle stick at 1500, the aircraft decelerates to 14.4 m/s (alpha 10-11 deg) and the elevon sits at 13 deg up before the roll command, so it saturates at its 20 deg stop (differential 12.6 deg). The 3.7 % drop from 92.9 to 86.7 deg/s is that saturation plus the new trim (4.8 deg up at 17 m/s instead of 2.9-3.4). With the throttle held, the steps run at 16.3-19 m/s and the rate is 106-125 deg/s with 13 deg of differential: **A-P11 passes at cruise speed with 18 % margin** and the limit is unchanged. The A-P11 claims now cite R5_rt65 / R5_rt65g. Consequence for the flight card: roll steps are not to be flown below about 16 m/s; with the stick at mid throttle the available differential falls with speed and the elevon saturates.

**A-P8a turbulence heading margin.** The rule in `REQUIREMENTS-A.md` A-P8a is a conditional wording (turbulence heading excursion <= 15 deg before the first free hover, else `Q_WVANE_ENABLE` 0 and pilot yaw). QP-4 left it marginal (23.1 deg in seed 3 at 4 m/s, 1.47 kg). Re-run: six of seven runs are 8.5-14.0 deg; **seed 3 from 60 deg is 25.4 deg** at 1.455 kg with the heavier motors (peak output 0.884, 0.016 under the cap). The margin did not improve and the worst seed is 2.3 deg worse. This is not a claim; it stays open to the bench plate yaw test (M3) and the tethered turbulence hover (M9), and the board may choose 3 m/s with belly-on as the A-P8a text already allows.

**Peak motor output.** The seven hover runs keep the D-192 limit: longest time >= 0.85 is 0.20 s (limit 0.5 s), 0 s at the cap. The 4 m/s results are at 1.455 kg; the CLAIMS-FIX N4 runs at 1.47 kg gave 0.873 and 0.20 s, so the two masses agree within the seed noise.

## 6. G7 cost (item 5)

`python -I qp/A/bom_a.py`: spend $1,447.66 + crash reserve $327.43 = **$1,775.09**; +30 % on the unverified lines gives $1,894.92, margin **+$105.08**; G7 (total <= $1,800 and +30 % margin >= $100) **PASS**. The BOM file changed only in the prop labels (D-194), so the numbers equal QP-4. **Open:** the T-Motor prop adapter and spinner nut are drawn (CAD 4.3 + 2.9 g each) but have no buy line; if the MN2212 hardware pack does not hold them, four adapters and four nuts must be bought. The G7 margin at +30 % tolerates about **$5** more unverified cost before it drops under $100 (nominal margin $224.91 tolerates far more). Also unpriced: stock M2 x 25 screws, 3 mm foam tape (small). Confirm the hardware pack on the first order (Order 1, early December).

## 7. Claims rebuild (item 6)

`python -I redesign/qp/A/proofs/run_all.py`: **82 claims, 22 requirements, 66 calculations, 8 assumptions, 456 nodes, 0 failing, no warnings; every stored number re-computes** (strict). Before my changes the same build failed 5 claims (mass 1.454 > 1.44, EST cuts 54 > 41.6 g, CG trim forward end 19.33 < 20 mm, with the two requirement echoes). What changed:

| Claim | Change | Basis |
|---|---|---|
| CL-A-MASS-PRED / -ITEM / CUTS-REQUIRED | target 1.44 -> 1.46 kg; itemised list on the CAD part table | D-195 |
| CL-A-STRUCT-MASS | groups re-read from the CAD, 479.3 g | `cad_mass` part table |
| CL-A-CG-TRIM-FWD / CL-A-CG | band forward edge 20 -> 19 mm | D-195; SITL at CG 19.3 passes (pitch use 0.59) |
| CL-A-ROLL-141 / -GATE | now R5_rt65 / R5_rt65g at cruise speed, titles state 1.455 / 1.47 kg | D-195 |
| CL-A-PITCH-USE | peak elevon 9.6 -> 11.5 deg (0.575 of 0.60) | R5_t0, R5_g0 |
| CL-A-WIND-OUTPUT / -CAP | R5_h* runs, 0.20 s, 0 s; peak 0.884 | D-195 |
| CL-A-FLUTTER-ELEVON-*, -HALF, -WING | `flutter_d195*.md` values | this report s4 |
| CL-A-VIB-*, CL-A-VIB-GM, -GM-SHIFT | `iter3_run.md` re-run values (GM-SHIFT 2.03 -> 2.16) | s4 |
| **CL-A-COLL-DEPTH** (the WNG-008 warning) | the stale text claimed two 0.014 mm lower-cap touches; the report now shows 0.042 mm (balance tab WNG-007 on stop boss WNG-008-U at the +21 deg stop, a designed contact) and 0.034 mm (M2 nut on screw shank). The claim's parts list was the lower caps WNG-008-RL / LL, which have no hit; it now lists the parts actually in contact (WNG-007-R/L, WNG-008-RU/LU, HWC-001, HWC-003). No warning is printed by the strict build. | `cad/out/report*.json` |
| source strings | collision 96 parts / 444 bodies, assembly 35 steps / 96 parts, wire strands 41 | CAD-INTEGRATION s1 |
| ASM-A-HUB-WALL (new) | hub socket wall unverified at 0.8 mm | s4 |

`params-A.json` was regenerated by `proofs/gen_params_a.py`. Limits changed only with the logged decisions above (mass target, CG forward edge); no other limit was touched.

## 8. Viewer (item 7)

GLB exported with `blender -b --factory-startup -P redesign/blender/export_glb.py -- --root redesign/qp/A/cad/model` (56 s, 98 parts, 12 wires), then `viewer_data_a.py` (98 parts with geometry, 125 edges, 55 claims linked), `make_proof_embed.py` (graph 342,772 bytes), `make_index.py`. Cache-bust `?v=20261115a` -> `?v=20261115b` in `site.js`, `viewer.js` (model, data, parts, GLB) and `app.html` / `index.html` (site.js was already `b`). `site/assets/concept-a.glb`: before 1,515,080 bytes, 107 nodes, **89 meshes, 47,707 vertices**; after 3,440,616 bytes, 145 nodes, **108 meshes, 107,533 vertices**. Props: each blade part PRP-001 had 525-573 vertices (a disc-like stand-in), now 3,532-3,589 (lofted from the APC PE0 file), plus hub PRP-002 1,816, adapter PRP-004 1,383-1,479 and spinner nut PRP-005 722 per motor, and the 3,394-vertex PRP-003. `merge_check` prints a K09-L CG band error (0.043-0.050 m) that does not apply to concept A. `node redesign/viewer/check_viewer.js` fails 3 of 1,649 checks, all in the stale untracked dataset `viewer/data/concept-a/` (247 parts; HRN wires "has a mesh"), not in `site/data`; that folder was untracked at the start of the session and was left alone.

## 9. What is still open

1. **Hub arm-socket wall 0.8 mm** (s4): crude model fails; coupon test or 2.0 mm bosses (+7.1 g, predicted 1,461 g). Needs an owner decision and the coupon.
2. **A-P8a heading excursion** 25.4 deg in one of seven seeds (s5); bench plate yaw test M3 and tethered turbulence hover M9.
3. **CLmax** 0.75 and **NP** 40.7 mm are `EST`: no measured S5010 polar was reachable (airfoiltools down); fetch the UIUC polar when the site is up. Cruise drag, elevon effectiveness and the roll damping are `EST` (SITL aero model).
4. **Adapter and spinner nut buy line** and the G7 margin (+$105.08, about $5 of room at +30 %).
5. **A1 sign-off** on D-195 (target 1.46 kg, CG forward edge 19 mm).
6. EST cuts: 36.2 g of the 41.6 g must be real (foam, printed parts, hardware); M11 weighing decides.
7. Linkage path (pushrod, arm) is not in the collision poses and not in the SITL plant: the asymmetric travel (0.87 / 0.63 deg per deg) is checked only by the arm-angle table; the plant uses +-20 deg symmetric.
8. SITL forward-flight runs are single seeds with turbulence 0.5 m/s on the chain cases; no hinge dynamics, free play or gust on the back-transition.
9. Divergence and reversal speeds not re-run for the S5010 camber (inputs unchanged in geometry).
