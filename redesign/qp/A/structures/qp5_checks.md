## 1 Pushrod buckling (1.2 mm steel, Euler, pinned-pinned: Z-bend pin in the arm hole and clevis pin are pins)

| rod length (mm) | Pcr (N) | stall load F = T/(arm cos beta) at beta 0 / 18.3 deg (N) | ultimate F x KF (N) | MS at 18.3 deg | result |
|---|---|---|---|---|---|
| 42.5 (FIXES2, superseded) | 111 | 33.1 / 34.8 | 60.1 | +0.85 | PASS |
| 52.5 (CAD, D-194) | 73 | 33.1 / 34.8 | 60.1 | +0.21 | PASS |

Axial stress at the ultimate stall load: 53 MPa (yield of music wire 1,500+ MPa, EST: not a limit). Fault case: the servo driven into the +-21 deg stop pushes the full stall torque; no flight load comes near it (hinge moment 0.048 N m per elevon at 18 m/s and 20 deg, fwd_checks.py: rod load 3.7 N).
Effective-length factor 1.0 is the conservative end (the Z-bend end is a pin; a clevis pin through the horn blade is a pin); free play makes it no worse. Travel: rod load changes sign with the stall direction, so compression is the governing case both ways.

## 2 Hub arm socket wall (printed PETG boss round the 12 mm arm tube, 25 mm deep; wall HUB_W)

Load: prop-strike couple 8.3 N m -> reaction pair F = 332 N (structures_run.md). Model (CALC, crude): the reaction at the mouth bears on a patch of axial length l; the boss wall is a thin ring in hoop tension N = 2F/(pi l), sigma = KP N / t.
Allowable: printed PETG, XY, knock-down 20 MPa (structures_run.md line 212 'PETG socket wall bearing ... 20.0 MPa', EST).

| wall t (mm) | l = 12 mm: sigma (MPa) | MS | l = 6 mm (about 2.5 sqrt(r t) for a thin shell near the mouth): sigma (MPa) | MS | result |
|---|---|---|---|---|---|
| 0.8 | 47.5 | -0.58 | 94.9 | -0.79 | FAIL |
| 1.2 | 31.6 | -0.37 | 63.3 | -0.68 | FAIL |
| 1.6 | 23.7 | -0.16 | 47.5 | -0.58 | FAIL |
| 2.0 | 19.0 | +0.05 | 38.0 | -0.47 | PASS (l 12 only) |

## 3 Spar foam after the datum change (foam above / below the 12 mm bore 6.27 / 5.62 mm, min 5.65 mm over x 54-66: CAD-INTEGRATION s3 item 1)

| check | shear stress (kPa) | allowable 86 kPa (EST, foam_103.py) | MS |
|---|---|---|---|
| Bridge pitch torque 2.44 N m through the bond on the bore (r 6 mm), bonded |y| <= 0.15 m | 77.5 | 86 | +0.11 |
| Bridge pitch torque 2.44 N m through the bond on the bore (r 6 mm), bonded |y| <= 0.20 m | 58.1 | 86 | +0.48 |
| Spar-to-skin shear in the thinner ligament (5.62 mm each of two planes), lift 3.4 g x 1.47 kg | 7.3 | 86 | +10.81 |
| Bridge torque carried by the ligament ring (outer radius 6 + 5.62 mm), bond |y| <= 0.20 m | 15.5 | 86 | +4.54 |

The thinner ligament (5.62 mm, was 0.6 mm in the placeholder-datum CAD) is not shear-limited; the bond rule |y| <= 0.20 m (FIXES2) still governs. Foam allowables are EST (no FOAMULAR 150 shear row).