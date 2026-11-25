Mode new: cf 0.30, hinge x 171.50 mm, elevon 7.6 g, lead 14.0 g at 20 mm
Hinge inertia per elevon: CAD 1.961e-05 kg m2 (cad_mass.json: elevon 1.369e-05 + balance 5.919e-06; CAD file is the NEW design); section-model inputs here me 7.6 g plate c^2/3 + (lead+tabs) x 20 mm^2 = 1.949e-05
Elevon CG aft of the hinge (CAD, new): unbalanced 25.73 mm, balanced -4.07 mm

| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |
|---|---|---|---|---|---|---|
| A no damper, lead 14.0 g, elevon 7.6 g | kd | 10.6 / 41.0 | FAIL (130 of 600 K points) | 0.21-1.09 | 8.0e-03 at K 0.59 | 2.5 at K 1.04 |
| A no damper, lead 14.0 g, elevon 7.6 g | nom | 12.3 / 44.9 | FAIL (93 of 600 K points) | 0.41-1.32 | 5.9e-03 at K 0.82 | 2.0 at K 1.26 |
| A no damper, lead 14.0 g, elevon 7.6 g | hi | 14.2 / 51.2 | FAIL (64 of 600 K points) | 0.78-1.73 | 4.0e-03 at K 1.21 | 2.0 at K 1.64 |
| B damper hot 50 C (EST x0.6), lead 14.0 g | kd | 10.6 / 41.0 | **PASS** | - | <= 0 | 36.0 at K 0.19 |
| B damper hot 50 C (EST x0.6), lead 14.0 g | nom | 12.3 / 44.9 | **PASS** | - | <= 0 | 38.0 at K 0.40 |
| B damper hot 50 C (EST x0.6), lead 14.0 g | hi | 14.2 / 51.2 | **PASS** | - | <= 0 | 42.0 at K 0.50 |
| C damper nominal 25 C, lead 14.0 g | kd | 10.6 / 41.0 | **PASS** | - | <= 0 | 40.0 at K 0.11 |
| C damper nominal 25 C, lead 14.0 g | nom | 12.3 / 44.9 | **PASS** | - | <= 0 | 43.5 at K 0.03 |
| C damper nominal 25 C, lead 14.0 g | hi | 14.2 / 51.2 | **PASS** | - | <= 0 | 48.0 at K 0.22 |
| D damper cold 0 C (EST x2), lead 14.0 g | kd | 10.6 / 41.0 | **PASS** | - | <= 0 | 44.0 at K 0.01 |
| D damper cold 0 C (EST x2), lead 14.0 g | nom | 12.3 / 44.9 | **PASS** | - | <= 0 | 47.5 at K 0.01 |
| D damper cold 0 C (EST x2), lead 14.0 g | hi | 14.2 / 51.2 | **PASS** | - | <= 0 | 53.5 at K 0.01 |
| E damper half-hot (leak / half fill), lead 14.0 g | kd | 10.6 / 41.0 | **PASS** | - | <= 0 | 29.0 at K 0.50 |
| E damper half-hot (leak / half fill), lead 14.0 g | nom | 12.3 / 44.9 | **PASS** | - | <= 0 | 30.5 at K 0.74 |
| E damper half-hot (leak / half fill), lead 14.0 g | hi | 14.2 / 51.2 | **PASS** | - | <= 0 | 33.5 at K 0.96 |

Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).