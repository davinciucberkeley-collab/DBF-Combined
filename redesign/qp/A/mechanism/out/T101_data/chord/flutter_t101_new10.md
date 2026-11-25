Mode new: cf 0.30, hinge x 171.50 mm, elevon 7.6 g, lead 10.0 g at 20 mm
Hinge inertia per elevon: CAD 1.793e-05 kg m2 (cad_mass.json: elevon 1.369e-05 + balance 4.245e-06; CAD file is the NEW design); section-model inputs here me 7.6 g plate c^2/3 + (lead+tabs) x 20 mm^2 = 1.789e-05
Elevon CG aft of the hinge (CAD, new): unbalanced 25.73 mm, balanced -0.55 mm

| case | corner | wing f_h / f_a (Hz) | no instability <= 28.8 m/s at any K (0.01-20 N m/rad) | unstable K band | worst damping ratio needed | lowest onset over the grid (m/s) |
|---|---|---|---|---|---|---|
| A no damper, lead 10.0 g, elevon 7.6 g | kd | 10.6 / 41.1 | FAIL (351 of 600 K points) | 0.01-0.85 | 1.3e-02 at K 0.38 | 2.0 at K 0.74 |
| A no damper, lead 10.0 g, elevon 7.6 g | nom | 12.3 / 45.1 | FAIL (199 of 600 K points) | 0.08-1.01 | 9.5e-03 at K 0.54 | 2.0 at K 0.89 |
| A no damper, lead 10.0 g, elevon 7.6 g | hi | 14.3 / 51.4 | FAIL (114 of 600 K points) | 0.32-1.32 | 6.4e-03 at K 0.83 | 2.0 at K 1.17 |
| B damper hot 50 C (EST x0.6), lead 10.0 g | kd | 10.6 / 41.1 | **PASS** | - | <= 0 | 33.0 at K 0.17 |
| B damper hot 50 C (EST x0.6), lead 10.0 g | nom | 12.3 / 45.1 | **PASS** | - | <= 0 | 35.5 at K 0.17 |
| B damper hot 50 C (EST x0.6), lead 10.0 g | hi | 14.3 / 51.4 | **PASS** | - | <= 0 | 38.5 at K 0.40 |
| C damper nominal 25 C, lead 10.0 g | kd | 10.6 / 41.1 | **PASS** | - | <= 0 | 38.0 at K 0.01 |
| C damper nominal 25 C, lead 10.0 g | nom | 12.3 / 45.1 | **PASS** | - | <= 0 | 40.5 at K 0.01 |
| C damper nominal 25 C, lead 10.0 g | hi | 14.3 / 51.4 | **PASS** | - | <= 0 | 45.0 at K 0.01 |
| D damper cold 0 C (EST x2), lead 10.0 g | kd | 10.6 / 41.1 | **PASS** | - | <= 0 | 42.0 at K 0.01 |
| D damper cold 0 C (EST x2), lead 10.0 g | nom | 12.3 / 45.1 | **PASS** | - | <= 0 | 45.5 at K 0.01 |
| D damper cold 0 C (EST x2), lead 10.0 g | hi | 14.3 / 51.4 | **PASS** | - | <= 0 | 51.0 at K 0.01 |
| E damper half-hot (leak / half fill), lead 10.0 g | kd | 10.6 / 41.1 | FAIL (100 of 600 K points) | 0.16-0.57 | 2.6e-03 at K 0.36 | 26.5 at K 0.36 |
| E damper half-hot (leak / half fill), lead 10.0 g | nom | 12.3 / 45.1 | FAIL (35 of 600 K points) | 0.40-0.62 | 5.2e-04 at K 0.51 | 28.0 at K 0.49 |
| E damper half-hot (leak / half fill), lead 10.0 g | hi | 14.3 / 51.4 | **PASS** | - | <= 0 | 30.5 at K 0.71 |

Pass limit: no instability at V <= 28.8 m/s = 1.2 x VD (VD 24 m/s) for any hinge stiffness K; the grid onset speed is reported for margin (x VD = onset / 24).