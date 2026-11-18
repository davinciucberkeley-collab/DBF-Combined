# D-206 bridge tube in torsion: sizing

Structures engineer, 2026-11-17. `CALC`. Script `qp/A/structures/bridge_torsion_d206.py`. Found by the hub FEA map (review/QP-5/FEA-HUB.md).

## Roll moment about the bridge axis (hub FEA load set, worst pattern)

| Case | Roll moment (N m) | Factor |
|---|---|---|
| F1 thrust at the spin cap | 3.86 | 1.725 |
| F2 uncapped motor fault | 4.37 | 1.725 |
| S1 strike along the motor axis | 2.42 | 1.0 (damage case, D-202) |
| S2 strike in the disc plane | 7.93 | 1.0 (damage case, D-202) |
| S3 strike torque | 2.30 | 1.0 (damage case, D-202) |

Struts against hub roll (two 6 x 4.5, 286 mm, z = 0 plane): 0.41 N m/rad with pinned sockets, 72 N m/rad with rigid hub sockets and spar clamps. Bridge in torsion (G 5 GPa EST, 108 mm): 12 x 10 49 N m/rad, 16 x 14 123 N m/rad. Strut share of the roll moment: 12 x 10 1-60 %, 16 x 14 0-37 %. The real share sits between the bounds and depends on the printed sockets and the spar clamps (not modelled). The bridge is therefore sized to carry the whole roll moment (static: no inertia relief, no struts, no tray pad). Open item: if the struts do take their upper-bound share, their hub sockets see bending that no analysis has checked (about 1.5 N m per socket in the S2 strike with the 16 x 14 bridge).

## Shear stress tau = T r / J and the options (limit load, MPa; allowable 30 at the factor)

| Tube | J/r (mm3) | F2 tau | F2 x 1.725 | S2 tau (x 1.0) | Result | Mass, 108 mm (g) |
|---|---|---|---|---|---|---|
| 12 x 10 (D-202) | 176 | 24.9 | 42.9 | 45.1 | FAIL | 6.0 |
| 14 x 12 | 248 | 17.6 | 30.4 | 32.0 | FAIL | 7.1 |
| 12 x 8 (same OD; not stocked by RMRC) | 272 | 16.0 | 27.7 | 29.1 | PASS | 10.9 |
| 16 x 14 (D-206) | 333 | 13.1 | 22.6 | 23.8 | PASS | 8.1 |

Choice: **16 x 14** (passes both statically, without relying on inertia relief, friction or the tray pad). Stock: BOM R02 (RMRC 16 x 14, 1 m) leaves a 0.28 m offcut after the two 0.36 m fin tubes; the bridge needs 0.108 m: no purchase. CAD: bridge axis 2 mm below the hub axis (16 mm top stays tangent to the tray plate underside z 6.0), boss r 10.0 (2.0 mm wall), saddle socket and core slot widened, strap under z -10.
