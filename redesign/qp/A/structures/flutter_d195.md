Hinge inertia per elevon: CAD 1.485e-05 kg m2 (cad_mass.json: elevon 8.378e-06 + balance 6.470e-06); section-model inputs here me 6.7 g plate c^2/3 + (lead+tabs) x 20 mm^2 = 1.482e-05
Elevon CG aft of the hinge: unbalanced 21.44 mm, balanced -7.63 mm (negative = ahead of the hinge, i.e. overbalanced; was -6.06 mm)

| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |
|---|---|---|---|---|---|---|
| A no damper, lead 15.6 g, elevon 6.7 g | kd | 10.5 / 41.2 | FAIL (60 of 600 K points) | 0.49-1.04 | 5.2e-03 at K 0.73 | 18.5 at K 1.00 |
| A no damper, lead 15.6 g, elevon 6.7 g | nom | 12.2 / 45.1 | FAIL (42 of 600 K points) | 0.75-1.26 | 3.5e-03 at K 0.98 | 20.0 at K 1.21 |
| A no damper, lead 15.6 g, elevon 6.7 g | hi | 14.1 / 51.5 | FAIL (25 of 600 K points) | 1.21-1.64 | 1.7e-03 at K 1.41 | 22.5 at K 1.58 |
| B damper hot 50 C (EST x0.6) | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 38.5 at K 0.40 |
| B damper hot 50 C (EST x0.6) | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 41.5 at K 0.47 |
| B damper hot 50 C (EST x0.6) | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 46.0 at K 0.66 |
| C damper nominal 25 C | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 42.0 at K 0.25 |
| C damper nominal 25 C | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 45.5 at K 0.30 |
| C damper nominal 25 C | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 50.5 at K 0.63 |
| D damper cold 0 C (EST x2) | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 45.0 at K 0.21 |
| D damper cold 0 C (EST x2) | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 49.0 at K 0.20 |
| D damper cold 0 C (EST x2) | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 55.0 at K 0.42 |
| E damper half-hot (leak / half fill) | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 33.0 at K 0.54 |
| E damper half-hot (leak / half fill) | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 35.0 at K 0.77 |
| E damper half-hot (leak / half fill) | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 39.0 at K 0.96 |
| F lead cut to 12.8 g, damper hot | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 37.5 at K 0.21 |
| F lead cut to 12.8 g, damper hot | nom | 12.2 / 45.2 | **PASS** | - | <= 0 | 40.0 at K 0.33 |
| F lead cut to 12.8 g, damper hot | hi | 14.2 / 51.6 | **PASS** | - | <= 0 | 44.0 at K 0.59 |
| G previous design for reference: elevon 9.6 g, lead 15.6 g, damper nominal | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 40.5 at K 0.32 |
| G previous design for reference: elevon 9.6 g, lead 15.6 g, damper nominal | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 43.5 at K 0.43 |
| G previous design for reference: elevon 9.6 g, lead 15.6 g, damper nominal | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 48.5 at K 0.52 |

Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).