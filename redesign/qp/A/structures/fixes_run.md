## 1 Elevon flutter, speeds in m/s (G8 28.8; target >= 37)

Wing modes from the Ritz run (nom): QP-4 reference f_h 12.4 / f_alpha 43.9 Hz.

**A. QP-4 as drawn (10.7 g at 30 mm)** (elevon 10.0 g, span 0.30 m, lead 10.7 g at 30 mm ahead of the hinge; moment 321 g mm vs elevon 214 g mm)
| structural damping g_s | K=0.02 | K=0.05 | K=0.1 | K=0.2 | K=0.5 | K=1 | K=2 | K=5 |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 40 | 39 | 38 | 37 | 32 | 22 | 49 | 53 |
| 0.02 | 41 | 41 | 40 | 39 | 35 | 28 | 50 | 54 |

New design wing modes with the balance lump (13.3 g lead + 0.5 horn + 2 caps, 25 kg/m3 foam): f_h 12.2 / f_alpha 45.1 Hz.

**B. D-187 v2 SELECTED: 15.6 g lead strip + 0.5 g tabs, 20 mm ahead of the hinge, elevon y 0.04-0.35, foam 25** (elevon 9.6 g, span 0.31 m, lead 16.1 g at 20 mm ahead of the hinge; moment 322 g mm vs elevon 206 g mm)
| structural damping g_s | K=0.02 | K=0.05 | K=0.1 | K=0.2 | K=0.5 | K=1 | K=2 | K=5 |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 41 | 40 | 39 | 38 | 32 | 22 | 50 | 54 |
| 0.02 | 44 | 43 | 43 | 41 | 37 | 46 | 52 | 55 |

**B'. same, lead 12.8 g + 0.5 tabs (lighter; passes only with g_s 0.02)** (elevon 9.6 g, span 0.31 m, lead 13.3 g at 20 mm ahead of the hinge; moment 266 g mm vs elevon 206 g mm)
| structural damping g_s | K=0.02 | K=0.05 | K=0.1 | K=0.2 | K=0.5 | K=1 | K=2 | K=5 |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 37 | 37 | 36 | 34 | 27 | 13 | 51 | 54 |
| 0.02 | 40 | 39 | 39 | 37 | 32 | 46 | 52 | 55 |

**B''. same, lead 17.0 g (heavier, margin check)** (elevon 9.6 g, span 0.31 m, lead 17.5 g at 20 mm ahead of the hinge; moment 350 g mm vs elevon 206 g mm)
| structural damping g_s | K=0.02 | K=0.05 | K=0.1 | K=0.2 | K=0.5 | K=1 | K=2 | K=5 |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 42 | 42 | 41 | 39 | 34 | 25 | >100 | 54 |
| 0.02 | 46 | 45 | 45 | 43 | 39 | 46 | >100 | 55 |

## 2 Wing bending-torsion flutter with the balance lumps on the wing (V m/s; G8 28.8)
| case | kd | nom | hi |
|---|---|---|---|
| QP-4 reference (foam 30, no balance lump) | 46.0 | 49.3 | 56.2 |
| foam 25, no balance lump | 46.3 | 50.1 | 56.9 |
| foam 25 + balance lumps (D-187 v2) | 46.2 | 49.7 | 56.4 |
| foam 25 + balance lumps, fins off (worst) | 34.6 | 41.4 | 48.3 |
| foam 25 + balance lumps, strip lift x0.59 (3-D) | 57.3 | 62.2 | 70.3 |

## 3 Control reversal, elevon y 0.04-0.35 (V m/s; 3-D lift / 2-D strip)
| corner | e/c | 3-D | 2-D |
|---|---|---|---|
| kd, y1 0.34 | 0.10 | 37 | 28 |
| nom, y1 0.34 | 0.10 | 42 | 32 |
| kd, y1 0.35 | 0.10 | 37 | 28 |
| nom, y1 0.35 | 0.10 | 42 | 32 |
