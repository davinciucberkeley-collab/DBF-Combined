Jones-lag aero vs Theodorsen C(k), max matrix error at k 0.2 / 0.5 / 1.0: 1.7 % / 2.4 % / 1.7 %

Cross-check, onset speed (m/s), reference balance, nom: K 0.5: p-method 32.5, k-method 32.3; K 1.0: p-method 22.0, k-method 21.7; K 1.3: p-method 13.0, k-method 12.5; K 2.0: p-method 51.5, k-method 50.1

## 1 K sweep 0.01-20 N m/rad (600 log points), g_s = 0, V <= 28.8 m/s; wing corners kd / nom / hi

| design | corner | wing f_h / f_a (Hz) | no instability <= 28.8 at any K | unstable K band | worst damping ratio needed (V <= 28.8) | lowest onset over the grid (m/s) |
|---|---|---|---|---|---|---|
| 0 D-187 v2 as drawn: 15.6 g at 20 mm (ob 1.56), elevon 9.6 g | kd | 10.5 / 41.2 | FAIL (80 of 600 K points) | 0.47-1.27 | 1.0e-02 at K 0.80 | 2.0 at K 1.26 |
| 0 D-187 v2 as drawn: 15.6 g at 20 mm (ob 1.56), elevon 9.6 g | nom | 12.2 / 45.1 | FAIL (63 of 600 K points) | 0.70-1.54 | 7.9e-03 at K 1.05 | 2.5 at K 1.52 |
| 0 D-187 v2 as drawn: 15.6 g at 20 mm (ob 1.56), elevon 9.6 g | hi | 14.1 / 51.5 | FAIL (45 of 600 K points) | 1.14-1.99 | 5.5e-03 at K 1.52 | 3.5 at K 1.99 |
| 1 overbalance 2.5 (25.7 g at 20 mm) | kd | 10.3 / 40.9 | FAIL (45 of 600 K points) | 1.12-1.96 | 4.1e-03 at K 1.43 | 13.0 at K 1.91 |
| 1 overbalance 2.5 (25.7 g at 20 mm) | nom | 12.0 / 44.8 | FAIL (34 of 600 K points) | 1.56-2.37 | 3.1e-03 at K 1.86 | 13.5 at K 2.31 |
| 1 overbalance 2.5 (25.7 g at 20 mm) | hi | 13.9 / 51.2 | FAIL (24 of 600 K points) | 2.31-3.10 | 2.0e-03 at K 2.63 | 15.5 at K 3.02 |
| 2 overbalance 4 at 14 mm (58.8 g) | kd | 9.8 / 40.1 | FAIL (22 of 600 K points) | 2.53-3.30 | 2.3e-04 at K 2.69 | 16.5 at K 3.26 |
| 2 overbalance 4 at 14 mm (58.8 g) | nom | 11.4 / 44.2 | FAIL (13 of 600 K points) | 3.34-3.89 | 1.2e-04 at K 3.47 | 21.5 at K 3.79 |
| 2 overbalance 4 at 14 mm (58.8 g) | hi | 13.1 / 50.5 | FAIL (7 of 600 K points) | 4.71-5.08 | 5.3e-05 at K 4.77 | 25.0 at K 4.95 |
| 3 overbalance 5 at 14 mm (73.5 g) | kd | 9.6 / 39.7 | **PASS** | - | <= 0 | >60 |
| 3 overbalance 5 at 14 mm (73.5 g) | nom | 11.1 / 43.8 | **PASS** | - | <= 0 | >60 |
| 3 overbalance 5 at 14 mm (73.5 g) | hi | 12.9 / 50.1 | **PASS** | - | <= 0 | >60 |
| 4 lighter elevon 6.0 g, ob 2.5, 20 mm (12.9 g) | kd | 10.5 / 41.2 | FAIL (54 of 600 K points) | 0.52-1.03 | 4.3e-03 at K 0.75 | 20.5 at K 0.96 |
| 4 lighter elevon 6.0 g, ob 2.5, 20 mm (12.9 g) | nom | 12.2 / 45.1 | FAIL (37 of 600 K points) | 0.79-1.24 | 2.7e-03 at K 1.00 | 22.0 at K 1.17 |
| 4 lighter elevon 6.0 g, ob 2.5, 20 mm (12.9 g) | hi | 14.1 / 51.5 | FAIL (19 of 600 K points) | 1.29-1.62 | 1.0e-03 at K 1.45 | 25.0 at K 1.58 |
| 5 lighter elevon 4.5 g, ob 6, 14 mm (41 g) | kd | 10.1 / 40.6 | FAIL (44 of 600 K points) | 1.32-2.28 | 1.6e-03 at K 1.62 | 5.0 at K 2.23 |
| 5 lighter elevon 4.5 g, ob 6, 14 mm (41 g) | nom | 11.7 / 44.6 | FAIL (35 of 600 K points) | 1.79-2.76 | 1.2e-03 at K 2.12 | 5.5 at K 2.69 |
| 5 lighter elevon 4.5 g, ob 6, 14 mm (41 g) | hi | 13.5 / 51.0 | FAIL (26 of 600 K points) | 2.63-3.61 | 8.5e-04 at K 2.98 | 6.5 at K 3.52 |
| 6 chord 0.20 c (hinge 0.80 c), 8.3 g, ob 2.5 | kd | 10.5 / 41.1 | FAIL (38 of 600 K points) | 0.68-1.09 | 3.9e-03 at K 0.87 | 22.0 at K 1.04 |
| 6 chord 0.20 c (hinge 0.80 c), 8.3 g, ob 2.5 | nom | 12.2 / 45.1 | FAIL (26 of 600 K points) | 0.98-1.34 | 2.3e-03 at K 1.14 | 23.5 at K 1.26 |
| 6 chord 0.20 c (hinge 0.80 c), 8.3 g, ob 2.5 | hi | 14.1 / 51.4 | FAIL (12 of 600 K points) | 1.50-1.73 | 6.4e-04 at K 1.62 | 27.0 at K 1.64 |
| 7 chord 0.30 c (hinge 0.70 c), 10.9 g, ob 2.5 | kd | 10.2 / 40.6 | FAIL (45 of 600 K points) | 1.64-2.87 | 2.2e-03 at K 2.01 | 7.0 at K 2.80 |
| 7 chord 0.30 c (hinge 0.70 c), 10.9 g, ob 2.5 | nom | 11.8 / 44.5 | FAIL (36 of 600 K points) | 2.23-3.47 | 1.7e-03 at K 2.63 | 7.5 at K 3.38 |
| 7 chord 0.30 c (hinge 0.70 c), 10.9 g, ob 2.5 | hi | 13.7 / 50.9 | FAIL (26 of 600 K points) | 3.30-4.53 | 1.2e-03 at K 3.70 | 8.5 at K 4.42 |
| 8 D-187 v2 + hinge damper c = 8e-4 N m s/rad | kd | 10.5 / 41.2 | **PASS** | - | <= 0 | 38.5 at K 0.34 |
| 8 D-187 v2 + hinge damper c = 8e-4 N m s/rad | nom | 12.2 / 45.1 | **PASS** | - | <= 0 | 41.0 at K 0.50 |
| 8 D-187 v2 + hinge damper c = 8e-4 N m s/rad | hi | 14.1 / 51.5 | **PASS** | - | <= 0 | 45.0 at K 0.77 |

## 2 Hinge damper needed (viscous, across the hinge, per elevon, N m s/rad; lead strip at 20 mm)

| lead per elevon (g) | corner | c for no instability <= 28.8 | c for <= 37 (1.54 VD, the QP-4 target) |
|---|---|---|---|
| 12.8 | kd | 4.2e-04 | 9.0e-04 |
| 12.8 | nom | 3.6e-04 | 7.3e-04 |
| 12.8 | hi | 2.9e-04 | 5.8e-04 |
| 15.6 | kd | 3.3e-04 | 7.1e-04 |
| 15.6 | nom | 2.8e-04 | 5.8e-04 |
| 15.6 | hi | 2.2e-04 | 4.5e-04 |
| 20.0 | kd | 2.4e-04 | 5.4e-04 |
| 20.0 | nom | 2.0e-04 | 4.4e-04 |
| 20.0 | hi | 1.5e-04 | 3.4e-04 |