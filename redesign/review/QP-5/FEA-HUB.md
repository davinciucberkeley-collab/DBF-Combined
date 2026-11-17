# QP-5 FEA-HUB: 3-D FEA of the D-202 / D-205 hub (continuous carbon arms)

Structures engineer, 2026-11-17. Status `CALC` (finite-element analysis); nothing printed or tested. Follows
[FEA-ARM.md](FEA-ARM.md), which found the D-193 hub's 0.8 mm web failing in flight (factor of safety 0.05). The hub was
redesigned (D-202), then moved 6 mm aft and trimmed for mass (D-205). Script `qp/A/structures/fea_hub.py` (geometry from
`cad/amodel/wing.py` and `common.py`), figures `fea_hub_figs.py` and `fea_hub_render_blender.py`, results
`qp/A/structures/out_fea/hub_result_L0_d205.json`.

## 1. Answer

- **The new hub passes in flight at the full safety factors.** At the worst flight case (F2: an uncapped motor fault, every
  thrust pattern), the printed hub's 99th-percentile stress is 7.9 MPa against 9.3 allowed (20 MPa / 2.156). The arm tubes
  reach 18.1 MPa hoop at the pin holes (23.2 allowed) and 13.5 MPa shear (17.4). The glue carries 0.89 MPa mean shear along
  the worst arm (0.93 allowed).
- **A 30 N prop strike is held at limit load (damage case, factor 1.0, D-202).** S2 (strike in the disc plane): tube hoop
  31.8 MPa against 40, shear 24.5 against 30, axial 194 against 350, hub 99th percentile 10.9 against 20.
- **One input is unproven: the glue.** The strike needs a mean bond shear of 1.93 MPa and flight needs 0.89 x 2.156 = 1.92.
  The analysis uses 2.0 MPa (`EST`). The glue coupon ([COUPON-BOND-D202.md](../../qp/A/structures/COUPON-BOND-D202.md),
  5 push-out specimens) must show at least 2.0 MPa before the flight hub is printed.
- **New finding, open: the bridge tube in torsion.** The maps show the 12 x 10 bridge tube over 1 along most of its
  length (F2 shear 28.3 MPa at limit, 49 at the factor, against 30; S2 53.0 against 30). The bridge was not one of this
  model's checks, and the model makes it the only support, so it carries every roll moment of the cage. A hand check says
  that is close to the truth: the two 6 x 4.5 V struts lie in one plane and resist hub roll with about 1 % of the bridge's
  stiffness (struts about 0.4 N m/rad against 46 for the bridge in torsion). The 8.3 N m strike couple (`qp5_checks.md`)
  then gives 8.3e3 x 6 / 1054 = 47 MPa of shear in the bridge against 30 MPa (`EST`) at factor 1.0. Earlier checks
  (`structures_a.py`) covered the bridge in bending only. Whether the hub tray pad takes part of it is not analysed. Fixes
  to size: a 16 x 14 bridge (J/r 333 mm3 against 277 needed for the strike at 30 MPa; about +2.2 g) or a roll-wrapped
  tube with a measured shear allowable; the flight case needs the cage frame model (struts, pad, inertia) first.
- **Before and after:** the D-193 hub reached margin ratios of 0.02 (web), 0.08 (socket glue) and 0.52 (tube shear); the new
  hub's lowest is 1.04 (glue in the strike).

![Margin ratio per check: new hub in flight and in a strike, and the D-193 hub it replaced](../../qp/A/structures/fig/fea-hub-margin.png)

![Utilisation map, F2 motor fault in flight: the printed hub (left) and, with the hub hidden, the arm tubes, bridge and pins (right)](../../qp/A/structures/fig/fea-hub-F2.png)

![Utilisation map, S2 30 N prop strike (damage case, factor 1.0)](../../qp/A/structures/fig/fea-hub-S2.png)

Colour: utilisation = stress x required factor / allowable, enveloped over every load pattern in the case. 0 to 1 runs from
pale to dark blue; over 1 is red (the bridge tube, see s1, and small spots where the bridge-tube end bears on the hub); grey is not judged (the pins, which have no allowable in the
analysis, and the 15 mm at each loaded tube end where the load is applied). The same map turns in 3-D on the Explorer's
Structures page (case buttons, part toggles, value under the cursor).

## 2. Model

- **Geometry** (D-205): two continuous 12 x 10 carbon tubes crossing at x -6.5 / +6.5 mm from the hub axis, modelled 60 mm
  each side of the hub (`S_END` 60). Printed PETG hub: 28 x 20 x 20 mm centre block with 3 mm edge radii, 1.5 mm sleeves over
  s +-24 mm, a bridge boss to the tray face (24 mm aft of the hub axis after D-205). 14 x 12 carbon doublers at s 11-25 mm
  over each lead-exit hole. Five 3 mm carbon pins along x: one through both tubes at the crossing, one per tube at s +-8 mm.
  Bridge tube 12 x 10, 40 mm modelled, fixed at its end.
- **Mesh:** quadratic tetrahedra (tet10), 306,398 elements, 1.44 M unknowns (level 0, `MS` 1.1).
- **Materials:** PETG isotropic; CFRP tubes transversely isotropic along each tube axis (`fea_arm.py` constants); pins
  isotropic 70 GPa (`EST`). Glue is a perfect tie (the bond check reads the shear on the sleeve-tube interface).
- **Solver:** MATLAB CHOLMOD with nested-dissection ordering, 24 unit load cases (6 per motor station) combined by
  superposition. Residual 6.2e-10; reactions balance each unit load to 5.0e-10.

## 3. Load cases (limit; factors applied to the stresses)

| Case | What | Factor |
|---|---|---|
| F1 | Thrust at the spin cap, motor torque, gyroscopic pitch-over, 1P imbalance; every on/off pattern of the four motors (512 combinations) | PETG and glue 2.156, CFRP 1.725 |
| F2 | As F1 with one motor uncapped (fault) | as F1 |
| S1 | 30 N prop strike along the motor axis, on UR | 1.0 (damage case, D-202) |
| S2 | 30 N prop strike in the disc plane, four directions, on UR | 1.0 |
| S3 | Strike torque about the motor axis | 1.0 |

## 4. Results (limit-load stresses, MPa)

| Item | F1 | F2 | Allowed (flight) | S1 | S2 | S3 | Allowed (strike) | Result |
|---|---|---|---|---|---|---|---|---|
| Printed hub, p99 principal (bridge boss) | 6.7 | 7.9 | 9.3 | 12.1 | 10.9 | 3.0 | 20 | PASS |
| Printed hub, peak (bridge-tube end, sharp edge) | 17.3 | 20.3 | - | 37.0 | 27.7 | 7.1 | - | judged by p99 (peaks at sharp edges grow with refinement) |
| Glue, mean shear on the worst arm | 0.76 | 0.89 | 0.93 | 1.72 | 1.93 | 0.52 | 2.0 `EST` | PASS if the coupon shows >= 2.0 |
| Arm tube, shear | 11.7 | 13.5 | 17.4 | 20.5 | 24.5 | 7.3 | 30 | PASS |
| Arm tube, hoop | 15.8 | 18.1 | 23.2 | 21.8 | 31.8 | 8.2 | 40 | PASS |
| Arm tube, axial | 54.6 | 63.8 | 203 | 128.7 | 193.8 | 60.4 | 350 | PASS |
| Bridge tube, shear (torsion; sole support in this model) | 25.0 | 28.3 | 17.4 | utilisation 0.63 | 53.0 | - | 30 | OPEN: over 1, see s1 |
| Printed hub, skin peaks (bearing of the bridge-tube end, crossing) | - | 2.5 % of skin vertices over 1 | - | - | 0.9 % | - | - | local; judged by the volume p99 above |
| Pins, von Mises (max) | 38.4 | 44.8 | - | 82.5 | 73.7 | 20.4 | - | no allowable set for the pin rod |

Tube values are the larger of tubes A and B; the hoop and shear peaks sit at the pin holes. With the glue released (pins
and bearing only, run `pinsrel`), the strike fails (hoop 59.6, shear 37.4): the pins back up the glue, they do not replace
it. Changes from the D-202 run (`pins`) to D-205: doublers shortened, boss 6 mm shorter; the boss p99 rose from 6.7 to 7.9
in F2 and the glue mean from 0.86 to 0.89; everything else moved by less than 1 MPa.

## 5. What this does not cover

- The glue allowable (coupon), the printed PETG allowable (20 MPa `EST`, 0.2 mm layers) and any layer-line weakness.
- Pin holes are drilled in the real tubes; their edge quality and any fibre damage are not modelled.
- The pin-access holes in the hub block (D-204) and the hub's strut sockets are not in the mesh.
- Fine mesh: level 0 only. The peaks at the bridge-tube end are mesh-dependent; a level-1 run of the drawn hub is next.
- Fatigue and vibration (see `fe_a.py` for the modes).
- The supports: the model is held only at the bridge-tube end. The V struts, the tray pad and inertia relief in flight
  are not modelled; they decide how much roll moment the bridge carries (open item, s1).

## 6. Re-run

```bash
cd redesign/qp/A/structures
python -I fea_hub.py --level 0 --tag d205 --fields --p S_END=60 SLV_W=1.5 MS=1.1
python fea_hub_figs.py --tag d205
blender -b --factory-startup -P fea_hub_render_blender.py
python fea_hub_figs.py --compose
```

The first step takes about 15 min and 25-30 GB of RAM (MATLAB); never run it alongside Blender on the 64 GB machine.
