# G10 stop and cap check (stop_check.py)

Mechanical stop 21.0 deg; authority (software, SERVO5/6, plant) 20.0 deg; cap wall 0.6 mm; design clearance 0.5 mm.

| side | cap outer height max (mm) | cap x range (mm) | lead poke beyond the airfoil at the stop (mm) | min lead/tab to cap cavity over -21..+21 (mm) | at angle | min lead/tab to cap at +-22 (mm) | boss to tab gap at the stop (mm) | boss to lead at the stop (mm) | boss penetration into the tab at 22 deg (mm) |
|---|---|---|---|---|---|---|---|---|---|
| upper | 4.05 | 137-180 | 2.93 | 0.51 | +21.0 | 0.08 | 0.052 | 1.46 | 0.20 |
| lower | 4.22 | 139-180 | 3.10 | 0.52 | -21.0 | 0.13 | 0.052 | 1.35 | 0.23 |

Cap clearance >= 0.5 mm over the whole travel and boss-to-lead >= 0.5 mm: **PASS**.
The cap cavity stays above the skin only where the lead or tabs poke; elsewhere the inner surface is flush with the skin (cap wall rests on the skin).
Boss to tab gap is 0 by construction at the stop (bottom face coplanar with the tab face rotated to +-21 deg); the +-22 deg column shows how far the tab would go into the boss if the stop were absent (it cannot: the boss stops it).
Damper: gap 0.30 mm, c = 1.03e-03 N m s/rad at 25 C (mu 12.2 Pa s), stator 2.0 g, rotor 0.5 g per elevon.
Cap masses (printed, from the drawn volume): upper 3.84 g, lower 3.79 g each, 4 caps 15.2 g.