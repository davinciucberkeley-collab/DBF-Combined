# Glue coupon: arm tube in a printed hub sleeve (D-202)

Structures engineer, 2026-11-17. Status `PLAN` (not run). Required by D-202 before the flight hub is printed.

## Why

Every hub result depends on one estimated number: the epoxy shear allowable between the 12 x 10 carbon arm tube and the
printed PETG sleeve, 2.0 MPa (`structures_a.py` `BOND_TAU`, `EST`, no test behind it). The hub FEA (`fea_hub.py`, run
`d205`: glue plus three 3 mm pins, D-205 geometry: hub 6 mm aft, doublers s 11-25; run `pins` before it) needs, as the mean shear along the worst arm's bond:

| Case | Mean bond shear at limit (MPa) | Factor | Needed allowable (MPa) |
|---|---|---|---|
| F2 uncapped fault (worst flight) | 0.89 | 2.156 (1.5 x 1.15 x 1.25, `structures_a.py`) | 1.92 |
| S2 prop strike 30 N (damage case, D-202) | 1.93 | 1.0 | 1.93 |

So the coupon must show a **design allowable of at least 2.0 MPa** (the value the analysis already uses). Below that, the
hub is not cleared to fly.

## Specimen (5 off)

- Sleeve: print in PETG with the hub's settings (0.2 mm layer; sleeve axis vertical, as the hub is printed), bore equal to
  the hub's (the CAD value once drawn: `-` today), wall 1.5 mm, bonded length 15 mm (short, so the bond fails before
  the tube or the PETG).
- Tube: 12 x 10 carbon tube offcut, 80 mm (BOM R08 offcuts if enough remain; else `-`).
- Prep and glue exactly as the build: the same epoxy (BOM R05), the same sanding and cleaning, the same cure (24 h).

## Test

- Push the tube out of the sleeve along its axis, sleeve supported on a ring, slowly, with the bench load cell (BOM G02)
  or a hanging-weight rig; record the peak load F.
- Mean shear per specimen: tau = F / (pi x 12 mm x 15 mm).
- Design allowable: the lower of (lowest specimen) and (mean - 2 x standard deviation).
- Pass: design allowable >= 2.0 MPa. Record the failure mode (adhesive on PETG, adhesive on carbon, cohesive, PETG).

## Where it goes

Result into `structures_a.py` `BOND_TAU` and this file; re-run `fea_hub.py` evaluation if the value changes. Build guide
open item "Hub socket coupon pull test" points here.
