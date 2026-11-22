# T-083 motor mount + cup rows (hand calculation, EST allowables as T077p6 cups; X2216 V3 on the SunnySky X-mount)

Loads: cap thrust 13.08 N/motor at 11358 rpm, torque 0.191 N m (prop_a EST, fresh, cap 0.993); FAULT uncapped 15.71 N; 1P 1.41 N (U 1 g mm); hover 5.06 N; strike 30 N; blade stop 2.4 N m.
Geometry: prop mid-plane 55.3 mm above the arm axis (was 47.0), 43.3 mm above the plate, 40.3 mm above the motor base; bolts r 17 on the diagonals (|y|, |z| 12.02).

| Item | Load | Stress | Allowable | MS | Result | Note |
|---|---|---|---|---|---|---|
| S2 transverse 30 N at the prop mid-plane (43.3 mm above the plate): worst mount-bolt tension + hover share; M3 stress area | 39.5 N/bolt | 13.54 MPa | 450.0 MPa | +32.23 | PASS |  |
| S2: nyloc bearing on the PETG plate back face (annulus 17.1 mm2) | 39.5 N/bolt | 4.97 MPa | 20.0 MPa | +3.02 | PASS | no washer; a 7 mm washer halves it |
| S2: bolt head bearing on the X-mount (Al, EST) | 39.5 N/bolt | 4.20 MPa | 240.0 MPa | +56.12 | PASS | X-mount material not stated: 6061-T6 240 MPa assumed (EST, "-") |
| S2: plate strip bending at the nut, -y bolts, 4.2 mm web, arm 3.1 mm (strip 13.9 mm, EST) | 123 N mm | 6.50 MPa | 9.5 MPa | +0.46 | PASS | interlayer allowable (worst), as the p6 plate rows |
| S2: plate punching shear round the nut (pi x 5.5 x 4.2 mm), interlayer | 39.5 N/bolt | 1.17 MPa | 9.5 MPa | +7.10 | PASS |  |
| S2: plate strip bending at the nut, +y bolts, 5.0 mm plate, arm 4.0 mm (strip 15.5 mm, EST) | 159 N mm | 5.30 MPa | 9.5 MPa | +0.79 | PASS | interlayer allowable (worst), as the p6 plate rows |
| S2: plate punching shear round the nut (pi x 5.5 x 5.0 mm), interlayer | 39.5 N/bolt | 0.99 MPa | 9.5 MPa | +8.64 | PASS |  |
| S2: X-mount arm bending at the inner hole, lever 9.0 mm (net 3.8 x 3 mm; material "-", 6061-T6 240 MPa assumed, EST) | 355 N mm | 107.55 MPa | 240.0 MPa | +1.23 | PASS | the "7" arm width is read off the drawing (EST) |
| S2: motor countersunk M3 into the base, thread strip at 2.0 mm engagement (lever 40.3 mm above the base, 19-pair carries it) | 64.9 N/screw | 13.30 MPa | 90.0 MPa | +5.77 | PASS | base alloy not published (EST), as p6 |
| S1 axial 30 N: nyloc bearing on the plate (4 bolts) | 7.5 N/bolt | 0.94 MPa | 20.0 MPa | +20.17 | PASS |  |
| S3 blade stop 2.4 N m: bolt bearing in the PETG plate hole (3.0 x 4.2 mm), 4 bolts at r 17 | 35.3 N/bolt | 6.04 MPa | 20.0 MPa | +2.31 | PASS | p6 had 97 N/screw on 2 of 4 M2.5 at r 12.4 |
| S3: M3 bolt shank single shear | 35.3 N/bolt | 8.61 MPa | 270.0 MPa | +30.35 | PASS |  |
| Thrust at the cap 13.1 N (fresh, Q_M_BAT_CURR_MAX 72 A, derate 0.93) x2 prying + 1P 1.41 N: nyloc bearing | 6.9 N/bolt | 0.87 MPa | 20.0 MPa | +22.03 | PASS |  |
| FAULT one motor uncapped 15.7 N (table) x2 prying: nyloc bearing | 7.9 N/bolt | 0.99 MPa | 20.0 MPa | +19.22 | PASS |  |
| Arm 12x10 root bending, thrust at the cap + torque (p6 42.64 MPa at 8.8 N x 1.49) | 3.23 N m | 63.38 MPa | 350.0 MPa | +4.52 | PASS |  |
| S2/S3 cup-to-arm bond, torsion 30 N x 55.3 mm + torque couple 2.4 N m / 25 mm (p6 0.69 MPa; torsion part x 1.18, upper bound on the vector sum) | - | 0.81 MPa | 2.0 MPa | +1.46 | PASS |  |
| Arm 12x10 root bending, strike force at the blade (lever 0.246 + 0.080 m; the 8 mm higher prop plane does not change it) | 9.8 N m | 192.07 MPa | 350.0 MPa | +0.82 | PASS |  |
| FATIGUE cup bond, 1P couple at 55.3 mm (p6 0.01 MPa x 1.73) | - | 0.02 MPa | 0.6 MPa | +33.59 | PASS |  |

Thrust-line tilt / arm tip deflection at the cap scale with thrust: p6 1.36 mm / 0.48 deg at 8.8 N (kd) -> 2.02 mm / 0.71 deg at 13.1 N (info; no limit in the repo).
Minimum MS: +0.46 (S2: plate strip bending at the nut, -y bolts, 4.2 mm web, arm 3.1 mm ()
