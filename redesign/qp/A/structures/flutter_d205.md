Hinge inertia per elevon: CAD 1.370e-05 kg m2 (cad_mass.json: elevon 8.378e-06 + balance 5.320e-06); section-model inputs here me 6.7 g plate c^2/3 + (lead+tabs) x 20 mm^2 = 1.370e-05
Elevon CG aft of the hinge: unbalanced 21.44 mm, balanced -5.89 mm (negative = ahead of the hinge, i.e. overbalanced; D-195 with 15.6 g: -7.63 mm)

| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |
|---|---|---|---|---|---|---|
| A no damper, lead 12.8 g, elevon 6.7 g | kd | 10.5 / 41.2 | FAIL (80 of 600 K points) | 0.32-0.88 | 7.4e-03 at K 0.57 | 15.0 at K 0.86 |
| A no damper, lead 12.8 g, elevon 6.7 g | nom | 12.2 / 45.2 | FAIL (57 of 600 K points) | 0.52-1.07 | 5.1e-03 at K 0.77 | 16.5 at K 1.04 |
| A no damper, lead 12.8 g, elevon 6.7 g | hi | 14.2 / 51.6 | FAIL (36 of 600 K points) | 0.89-1.39 | 2.8e-03 at K 1.14 | 18.5 at K 1.36 |
| B damper hot 50 C (EST x0.6), lead 12.8 g | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 37.5 at K 0.21 |
| B damper hot 50 C (EST x0.6), lead 12.8 g | nom | 12.2 / 45.2 | **PASS** | - | <= 0 | 40.0 at K 0.33 |
| B damper hot 50 C (EST x0.6), lead 12.8 g | hi | 14.2 / 51.6 | **PASS** | - | <= 0 | 44.0 at K 0.59 |
| C damper nominal 25 C, lead 12.8 g | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 41.0 at K 0.08 |
| C damper nominal 25 C, lead 12.8 g | nom | 12.2 / 45.2 | **PASS** | - | <= 0 | 44.0 at K 0.19 |
| C damper nominal 25 C, lead 12.8 g | hi | 14.2 / 51.6 | **PASS** | - | <= 0 | 49.0 at K 0.33 |
| D damper cold 0 C (EST x2), lead 12.8 g | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 44.0 at K 0.09 |
| D damper cold 0 C (EST x2), lead 12.8 g | nom | 12.2 / 45.2 | **PASS** | - | <= 0 | 47.5 at K 0.29 |
| D damper cold 0 C (EST x2), lead 12.8 g | hi | 14.2 / 51.6 | **PASS** | - | <= 0 | 53.5 at K 0.34 |
| E damper half-hot (leak / half fill), lead 12.8 g | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 31.5 at K 0.47 |
| E damper half-hot (leak / half fill), lead 12.8 g | nom | 12.2 / 45.2 | **PASS** | - | <= 0 | 34.0 at K 0.54 |
| E damper half-hot (leak / half fill), lead 12.8 g | hi | 14.2 / 51.6 | **PASS** | - | <= 0 | 37.5 at K 0.77 |

Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).