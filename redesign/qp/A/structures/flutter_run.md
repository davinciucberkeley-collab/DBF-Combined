Self-checks (steady thin-airfoil integration / T-formula): c=0.5 a=-0.5: M_alpha -1.5913/-1.5913, M_beta -0.1466/-0.1445; c=0.2 a=-0.3: M_alpha -0.2887/-0.2892, M_beta -0.3997/-0.3970. c = a = -1 flap-equals-pitch residuals 3.6e-15, 0.0e+00, 3.6e-15.

## 1 GJ and divergence
| corner | GJ spar | GJ tape box (hinge-cut) | GJ elevon zone | GJ full box | e/c at which q_D = q(28.8) | V_D-div at e/c 0.02 / 0.05 / 0.10 (m/s) |
|---|---|---|---|---|---|---|
| kd | 3.16 | 1.32 | 4.48 | 5.37 | 1.975 | 286 / 181 / 128 |
| nom | 3.16 | 2.64 | 5.80 | 7.57 | 2.555 | 326 / 206 / 146 |
| hi | 4.74 | 3.29 | 8.04 | 10.26 | 3.543 | 383 / 242 / 171 |
q(28.8 m/s) = 508 Pa; GJ in N m2.

## 2 Wing flutter (Ritz + strip Theodorsen)
wing m' 0.213 kg/m, CG 0.094 m from LE (0.28 semichord aft of EA), I'_EA 1.05e-03 kg m; fin each 59.6 g, CG x 0.256 m (1.60 semichord aft of EA), I_EA 2.44e-03; EA a = -0.51; b = 0.1225 m
| case | corner | f1..f3 in vacuo (Hz) | flutter V (m/s) | f (Hz) | x VD | G8 |
|---|---|---|---|---|---|---|
| base: fin on tip, no motor credit | kd | 10.7 / 40.1 / 95.5 | 46.0 | 20.4 | 1.92 | PASS |
| base: fin on tip, no motor credit | nom | 12.4 / 43.9 / 112.5 | 49.3 | 23.9 | 2.05 | PASS |
| base: fin on tip, no motor credit | hi | 14.4 / 50.1 / 130.6 | 56.2 | 27.2 | 2.34 | PASS |
| fins off | kd | 29.9 / 50.7 / 116.4 | 42.9 | 42.0 | 1.79 | PASS |
| fins off | nom | 33.1 / 58.5 / 136.8 | 52.7 | 46.8 | 2.20 | PASS |
| fins off | hi | 37.7 / 67.6 / 158.7 | 61.9 | 53.6 | 2.58 | PASS |
| motors on the wing (optimistic) | kd | 9.5 / 17.0 / 60.6 | 54.8 | 13.1 | 2.28 | PASS |
| motors on the wing (optimistic) | nom | 11.2 / 18.7 / 70.3 | 53.1 | 14.8 | 2.21 | PASS |
| motors on the wing (optimistic) | hi | 13.0 / 21.3 / 81.4 | 58.5 | 17.0 | 2.44 | PASS |
| EA at a = -0.30 | kd | 10.7 / 40.1 / 95.5 | 46.3 | 16.6 | 1.93 | PASS |
| EA at a = -0.30 | nom | 12.4 / 43.9 / 112.5 | 48.7 | 19.7 | 2.03 | PASS |
| EA at a = -0.30 | hi | 14.4 / 50.1 / 130.6 | 55.4 | 22.5 | 2.31 | PASS |
| strip lift x0.59 (3-D CLa) | kd | 10.7 / 40.1 / 95.5 | 57.3 | 21.2 | 2.39 | PASS |
| strip lift x0.59 (3-D CLa) | nom | 12.4 / 43.9 / 112.5 | 61.3 | 24.2 | 2.55 | PASS |
| strip lift x0.59 (3-D CLa) | hi | 14.4 / 50.1 / 130.6 | 70.2 | 26.7 | 2.93 | PASS |

## 3 Torsion needed (nom corner, base case): flutter V vs GJ
| GJ (N m2) | flutter V (m/s) | x VD |
|---|---|---|
| 2.0 | 50.3 | 2.10 |
| 3.0 | 49.5 | 2.06 |
| 4.5 | 49.2 | 2.05 |
| 6.0 | 49.2 | 2.05 |
| 8.0 | 49.4 | 2.06 |
| 12.0 | 51.1 | 2.13 |
| 20.0 | 55.6 | 2.32 |

## 4 Elevon flutter (3-DOF section at 0.7 span; wing f_h, f_a from section 2 nominal base)
f_h 12.4 Hz, f_alpha 43.9 Hz (modal, nom); elevon 10 g, CG 0.35 of its chord aft of the hinge; hinge at 0.50 semichord
| K_hinge per elevon (N m/rad) | f_beta in vacuo (Hz) | flutter V (m/s) | f (Hz) | x VD |
|---|---|---|---|---|
| 0.00 | 0 | 4.0 | 11.5 | 0.17 |
| 0.02 | 8 | 4.0 | 12.1 | 0.17 |
| 0.05 | 13 | 4.0 | 62.5 | 0.17 |
| 0.20 | 26 | 9.0 | 65.1 | 0.38 |
| 1.00 | 57 | 43.1 | 71.8 | 1.80 |
| 5.00 | 128 | 66.9 | 35.2 | 2.79 |
Mass-balanced (lead ahead of the hinge so elevon + lead CG sits on the hinge), floating (K = 0.02) and servo-held (0.2):
| lead per elevon (g) | arm ahead of hinge (mm) | K = 0.02 | K = 0.2 | K = 5 |
|---|---|---|---|---|
| 7.1 (x1.0) | 30 | 33.1 | 29.1 | 54.5 |
| 10.7 (x1.5) | 30 | 39.6 | 36.7 | 53.1 |
| 7.1 (x1.5) | 45 | 39.6 | 37.1 | 52.8 |

## 5 Control reversal (torsion rod, elevon y 0.04-0.34)
| corner | GJ | e/c | 3-D lift: q_R (Pa) / V_R (m/s) | 2-D strip: V_R (m/s) |
|---|---|---|---|---|
| kd | 4.48 | 0.00 | 1252 / 45 | 35 |
| kd | 4.48 | 0.05 | 996 / 40 | 31 |
| kd | 4.48 | 0.10 | 827 / 37 | 28 |
| nom | 5.80 | 0.00 | 1621 / 51 | 39 |
| nom | 5.80 | 0.05 | 1289 / 46 | 35 |
| nom | 5.80 | 0.10 | 1071 / 42 | 32 |
| hi | 8.04 | 0.00 | 2247 / 61 | 46 |
| hi | 8.04 | 0.05 | 1787 / 54 | 41 |
| hi | 8.04 | 0.10 | 1484 / 49 | 38 |

Aerodynamic hinge stiffness at 24 / 28.8 m/s per elevon (steady, thin airfoil): -0.375 / -0.540 N m/rad (negative = restoring)