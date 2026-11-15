# A3 live mass roll-up (generated)

Run `python -I redesign/team/A3/mass_rollup.py`. 203 instances, basic 2453 g, predicted 2589 g, gate 2700 g.

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv, redesign/team/A3/mass_model.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv, redesign/team/A3/mass_model.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 396 | 395 | 416 | -1 | `PROPOSED` |
| fins | 487 | 483 | 508 | -4 | `PROPOSED` |
| pod | 147 | 147 | 154 | -0 | `PROPOSED` |
| landing | 80 | 80 | 88 | -0 | `PROPOSED` |
| propulsion | 594 | 579 | 612 | -15 | `PROPOSED` |
| power | 506 | 507 | 519 | +1 | `FAIL` |
| avionics | 36 | 35 | 38 | -1 | `PROPOSED` |
| harness | 148 | 152 | 171 | +4 | `FAIL` |
| mechanisms | 74 | 74 | 84 | +0 | `FAIL` |
| **total** | **2 700** | **2 453** | **2 589** | allocated 2 468 + growth 232 | gate margin +111 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| listing minimum (D-64) | 410 | 2 585 | +115 | 84 | `CL-A3-GATE-MARGIN-546` | `MODELLED` |
| as carried (`battery.mass_kg`) | 414 | 2 589 | +111 | 84 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| listed (D-64) | 420 | 2 595 | +105 | 84 | `CALC-A3-MASS` | `MODELLED` |
| heavy bounding case, above the acceptance line (D-95) | 430 | 2 605 | +95 | 84 | `CL-A3-GATE-MARGIN-590` | `MODELLED` |

Pack acceptance (heaviest weighed pack that leaves the 84 g overrun under the gate): **440.7 g** (`CL-A3-PACK-ACCEPT`; SKU listing maximum 429.5 g, margin +11.2 g).

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 1 104 | 1 165 | 45 % |
| propulsion | 579 | 612 | 24 % |
| energy | 414 | 414 | 17 % |
| electrical | 246 | 276 | 10 % |
| avionics | 35 | 38 | 1 % |
| controls | 74 | 84 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.043–0.050 (13%–16%) | ±0.005 | +0.017…+0.025 | `PROPOSED` |
| Take-off, basic | 0.050 (15.6%) | -0.0014 | +0.015 | `FAIL` |
| Take-off, predicted (growth pro rata) | 0.051 (16.0%) | -0.0015 | +0.015 | `FAIL` |
| Pack slid -2.2 … +10.0 mm (spacers, crush stack) | 0.0494 … 0.0515 | | | — |
| Pack 410 g: nominal station → slid +0.0 mm (+ aft) | 0.0500 → 0.0500 | | | `CHECKED` |
| Pack 420 g: nominal station → slid +0.0 mm (+ aft) | 0.0495 → 0.0495 | | | `CHECKED` |
| Pack 430 g: nominal station → slid +0.0 mm (+ aft) | 0.0491 → 0.0491 | | | `CHECKED` |
| Pack 410 g at its D-98 station x -0.0565 (spacers 12 mm, clamped): basic → predicted | 0.0496 → 0.0512 (fwd +6.6 / aft -1.2 mm) | | | `FAIL` |
| Pack 420 g at its D-98 station x -0.0565 (spacers 12 mm, clamped): basic → predicted | 0.0492 → 0.0508 (fwd +6.2 / aft -0.8 mm) | | | `FAIL` |
| Pack 430 g at its D-98 station x -0.0565 (spacers 12 mm, clamped): basic → predicted | 0.0488 → 0.0504 (fwd +5.8 / aft -0.4 mm) | | | `FAIL` |
| No pack (handling) | 0.071 (22.2%) | -0.0016 | +0.008 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.049 m | -0.054 / -0.059 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | -5 | mm | `CALC-A3-CG` |
| or the whole pod group (689 g: pod, power, avionics) by | -3 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 579 g) by | -3 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 330 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.17 / 0.28 / 0.24 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 2 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.170 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 546–590 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0567 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.93 / 1.35 / 1.39 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| CG height z: basic / predicted (A1 copies to `cg.z_target_m`) | 0.0149 / 0.0146 | m | `CL-A3-CG-Z` / `CL-A3-CG-Z-PRED` |
| CG z range use (worst of basic, predicted) | 1.44 | — | `CL-A3-CG-Z-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.27 (-1.4 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.323 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.2046 | 0.0549 | 0.1964 | -0.0024 | kg·m² |
| Radius of gyration | 0.289 | 0.150 | 0.283 | | m |

Groups for C1's loads model (`CL-A3-GROUPS`; inertia about each group's own centroid, aircraft axes; closure to the aircraft inertia 8.5e-16, `CL-A3-GROUPS-CLOSURE`):

| Group | Station | Items | Mass g | x m | y m | z m | Ixx own | Iyy own | Izz own | Ixz own |
|---|---|---|---|---|---|---|---|---|---|---|
| **pack** | all | 1 | 414.0 | -0.0545 | +0.0000 | +0.0463 | 0.00015 | 0.00040 | 0.00041 | -0.00000 |
| **centre** | all | 38 | 339.7 | +0.0079 | -0.0103 | +0.0417 | 0.00372 | 0.00203 | 0.00462 | +0.00003 |
| centre | C | 30 | 322.1 | +0.0003 | -0.0109 | +0.0440 | 0.00153 | 0.00139 | 0.00235 | +0.00014 |
| centre | LL | 2 | 4.4 | +0.1465 | -0.3298 | -0.1180 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| centre | LR | 2 | 4.4 | +0.1465 | +0.3298 | -0.1180 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| centre | UL | 2 | 4.4 | +0.1465 | -0.3298 | +0.1180 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| centre | UR | 2 | 4.4 | +0.1465 | +0.3298 | +0.1180 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| **wing** | all | 16 | 395.1 | +0.1124 | +0.0005 | +0.0052 | 0.03931 | 0.00267 | 0.04192 | -0.00001 |
| wing | C | 5 | 357.4 | +0.1086 | +0.0000 | +0.0053 | 0.03559 | 0.00227 | 0.03782 | +0.00000 |
| wing | L | 5 | 18.6 | +0.1488 | -0.2993 | +0.0043 | 0.00015 | 0.00017 | 0.00032 | -0.00001 |
| wing | R | 6 | 19.1 | +0.1492 | +0.3017 | +0.0047 | 0.00016 | 0.00017 | 0.00033 | -0.00001 |
| **fins** | all | 54 | 411.0 | +0.0989 | +0.0000 | +0.0019 | 0.04573 | 0.00710 | 0.04341 | +0.00000 |
| fins | L | 7 | 101.3 | +0.0527 | -0.3156 | +0.0032 | 0.00057 | 0.00055 | 0.00005 | +0.00000 |
| fins | LL | 10 | 52.1 | +0.1427 | -0.3153 | -0.1181 | 0.00019 | 0.00055 | 0.00038 | +0.00007 |
| fins | LR | 10 | 52.1 | +0.1427 | +0.3153 | -0.1181 | 0.00019 | 0.00055 | 0.00038 | +0.00007 |
| fins | R | 7 | 101.3 | +0.0527 | +0.3156 | +0.0032 | 0.00057 | 0.00055 | 0.00005 | +0.00000 |
| fins | UL | 10 | 52.1 | +0.1449 | -0.3153 | +0.1195 | 0.00018 | 0.00056 | 0.00040 | -0.00008 |
| fins | UR | 10 | 52.1 | +0.1449 | +0.3153 | +0.1195 | 0.00018 | 0.00056 | 0.00040 | -0.00008 |
| **stations** | all | 44 | 660.1 | +0.0154 | +0.0000 | +0.0000 | 0.09115 | 0.02259 | 0.06989 | -0.00000 |
| stations | LL | 11 | 165.0 | +0.0154 | -0.3223 | -0.1812 | 0.00023 | 0.00023 | 0.00033 | +0.00007 |
| stations | LR | 11 | 165.0 | +0.0154 | +0.3223 | -0.1812 | 0.00023 | 0.00023 | 0.00033 | +0.00007 |
| stations | UL | 11 | 165.0 | +0.0154 | -0.3223 | +0.1812 | 0.00023 | 0.00023 | 0.00033 | -0.00007 |
| stations | UR | 11 | 165.0 | +0.0154 | +0.3223 | +0.1812 | 0.00023 | 0.00023 | 0.00033 | -0.00007 |
| **landing** | all | 18 | 79.5 | +0.3042 | +0.0000 | +0.0002 | 0.01178 | 0.00335 | 0.00851 | +0.00000 |
| landing | L | 1 | 0.7 | +0.3105 | -0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | LL | 4 | 19.5 | +0.3041 | -0.3200 | -0.2058 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | LR | 4 | 19.5 | +0.3041 | +0.3200 | -0.2058 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | R | 1 | 0.7 | +0.3105 | +0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | UL | 4 | 19.5 | +0.3041 | -0.3200 | +0.2058 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| landing | UR | 4 | 19.5 | +0.3041 | +0.3200 | +0.2058 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| **mechanisms** | all | 30 | 74.4 | +0.2179 | +0.0000 | -0.0024 | 0.00662 | 0.00009 | 0.00671 | -0.00000 |
| mechanisms | L | 15 | 37.2 | +0.2179 | -0.2931 | -0.0024 | 0.00012 | 0.00005 | 0.00016 | -0.00000 |
| mechanisms | R | 15 | 37.2 | +0.2179 | +0.2931 | -0.0024 | 0.00012 | 0.00005 | 0.00016 | -0.00000 |
| **harness** | all | 2 | 79.0 | +0.0797 | +0.0000 | +0.0055 | 0.00516 | 0.00000 | 0.00516 | -0.00000 |
| harness | L | 1 | 39.5 | +0.0797 | -0.2556 | +0.0055 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| harness | R | 1 | 39.5 | +0.0797 | +0.2556 | +0.0055 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |

(own inertias in kg·m²)

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 468 g + reserve 232 g = 2 700 g).

A3 adders kept beside a designer's parts.csv (items the list does not carry yet): HRN-A3-ROUTED (harness, 35.1 g); FIN-A3-WASHERS (fins, 3.9 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GND-001 (redesign/subsystems/ground/parts.csv, flight false): RC transmitter RadioMaster Pocket (Crush), internal ELRS 2.4 GHz FCC, with 2 x 18650 cells; GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 5/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-108, FIN-109, FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, HRN-102, HRN-113, HRN-114, PWR-104, PWR-105, PWR-106, PWR-202.

Roll-up warnings:

- harness: parts.csv totals 117 g, A3 estimate 276 g: missing parts or masses?
- FIN-A3-S08: A3 adder retired, fins/parts.csv republished (479.4 g, adder written against 476.1 g); check the new list carries it and drop the row
- PRP-A3-EPROP: A3 adder retired, propulsion/parts.csv republished (579.0 g, adder written against 462.0 g); check the new list carries it and drop the row
- FIN-A3-CHEEK: A3 adder retired, fins/parts.csv republished (479.4 g, adder written against 476.1 g); check the new list carries it and drop the row
- GER-A3-FOOT: A3 adder retired, landing/parts.csv republished (79.5 g, adder written against 69.9 g); check the new list carries it and drop the row



## Items (one row per instance)

| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |
|---|---|---|---|---|---|---|---|---|---|
| `WNG-001` | wing | structure | 198.1 | +0.119 | +0.000 | +0.005 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-002` | wing | structure | 102.0 | +0.080 | +0.000 | +0.007 | DATASHEET | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-003` | wing | structure | 47.5 | +0.132 | +0.000 | +0.004 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | +0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | -0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-006` | wing | structure | 1.0 | +0.062 | +0.320 | +0.006 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-006` | wing | structure | 1.0 | +0.062 | -0.320 | +0.006 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-008` | wing | structure | 3.9 | +0.080 | +0.000 | -0.005 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-009` | wing | structure | 5.9 | +0.064 | +0.000 | -0.009 | EST | 20 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.6 | +0.277 | +0.178 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.6 | +0.277 | -0.178 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.0 | +0.276 | +0.466 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.0 | +0.276 | -0.466 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-020` | wing | structure | 0.5 | +0.165 | +0.390 | +0.017 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `FIN-001` | fins | structure | 23.8 | +0.208 | +0.320 | +0.084 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.8 | +0.208 | -0.320 | +0.084 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.8 | +0.203 | +0.320 | -0.082 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.8 | +0.203 | -0.320 | -0.082 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 53.7 | +0.045 | +0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 53.7 | +0.045 | -0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 16.0 | +0.038 | +0.319 | +0.182 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 16.0 | +0.038 | -0.319 | +0.182 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 16.0 | +0.038 | +0.319 | -0.182 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 16.0 | +0.038 | -0.319 | -0.182 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 33.2 | +0.062 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 33.2 | +0.062 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | +0.320 | +0.007 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | -0.320 | +0.007 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | +0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | -0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | +0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | -0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 11.6 | +0.063 | +0.317 | +0.150 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 11.6 | +0.063 | -0.317 | +0.150 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 11.6 | +0.063 | +0.317 | -0.150 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 11.6 | +0.063 | -0.317 | -0.150 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.0 | +0.062 | +0.272 | +0.087 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.0 | +0.062 | -0.272 | +0.087 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.0 | +0.062 | +0.272 | -0.080 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.0 | +0.062 | -0.272 | -0.080 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | +0.325 | +0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | +0.315 | +0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | -0.325 | +0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | -0.315 | +0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | +0.325 | -0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | +0.315 | -0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | -0.325 | -0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.7 | +0.154 | -0.315 | -0.176 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.171 | +0.320 | +0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.171 | -0.320 | +0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.171 | +0.320 | -0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.171 | -0.320 | -0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-013` | fins | structure | 1.4 | +0.045 | +0.338 | +0.026 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-013` | fins | structure | 1.4 | +0.045 | -0.338 | +0.026 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-013` | fins | structure | 1.4 | +0.045 | +0.338 | -0.013 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-013` | fins | structure | 1.4 | +0.045 | -0.338 | -0.013 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-101` | fins | structure | 1.1 | +0.044 | +0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-101` | fins | structure | 1.1 | +0.044 | -0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-101` | fins | structure | 1.1 | +0.044 | +0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-101` | fins | structure | 1.1 | +0.044 | -0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-102` | fins | structure | 0.4 | +0.052 | +0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-102` | fins | structure | 0.4 | +0.052 | -0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-102` | fins | structure | 0.4 | +0.052 | +0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-102` | fins | structure | 0.4 | +0.052 | -0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-103` | fins | structure | 0.2 | +0.045 | +0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-103` | fins | structure | 0.2 | +0.045 | -0.338 | +0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-103` | fins | structure | 0.2 | +0.045 | +0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-103` | fins | structure | 0.2 | +0.045 | -0.338 | -0.163 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-A3-WASHERS` | fins | structure | 1.0 | +0.055 | +0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-A3-WASHERS` | fins | structure | 1.0 | +0.055 | -0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-A3-WASHERS` | fins | structure | 1.0 | +0.055 | +0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-A3-WASHERS` | fins | structure | 1.0 | +0.055 | -0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `POD-001` | pod | structure | 25.1 | -0.043 | -0.001 | +0.043 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-002` | pod | structure | 41.2 | -0.041 | -0.004 | +0.025 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-003` | pod | structure | 9.4 | -0.045 | -0.003 | +0.083 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-004` | pod | structure | 8.7 | -0.062 | +0.000 | +0.043 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-005` | pod | structure | 5.5 | +0.081 | +0.000 | +0.156 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-006` | pod | structure | 5.8 | -0.139 | -0.046 | +0.045 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-007` | pod | structure | 39.8 | +0.077 | -0.003 | +0.058 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-008` | pod | structure | 1.5 | -0.001 | +0.000 | +0.027 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-009` | pod | structure | 2.8 | -0.121 | -0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-010` | pod | structure | 5.3 | -0.104 | +0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-011` | pod | structure | 0.1 | +0.080 | -0.003 | +0.122 | DATASHEET | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-012` | pod | structure | 0.1 | +0.080 | -0.008 | +0.122 | DATASHEET | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-013` | pod | structure | 1.3 | +0.026 | +0.000 | +0.031 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `GER-001` | landing | structure | 14.4 | +0.291 | +0.320 | +0.204 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 14.4 | +0.291 | -0.320 | +0.204 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 14.4 | +0.291 | +0.320 | -0.204 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 14.4 | +0.291 | -0.320 | -0.204 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.9 | +0.339 | +0.320 | +0.211 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.9 | +0.339 | -0.320 | +0.211 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.9 | +0.339 | +0.320 | -0.211 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.9 | +0.339 | -0.320 | -0.211 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.6 | +0.311 | +0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.6 | +0.311 | -0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.372 | +0.320 | +0.212 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.372 | -0.320 | +0.212 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.372 | +0.320 | -0.212 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.372 | -0.320 | -0.212 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | +0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | -0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.5 | +0.311 | +0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.5 | +0.311 | -0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `PRP-001` | propulsion | propulsion | 108.0 | +0.010 | +0.322 | +0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 108.0 | +0.010 | -0.322 | +0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 108.0 | +0.010 | +0.322 | -0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 108.0 | +0.010 | -0.322 | -0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 23.0 | -0.019 | +0.324 | +0.183 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 23.0 | -0.019 | -0.324 | +0.183 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 23.0 | -0.019 | +0.324 | -0.183 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 23.0 | -0.019 | -0.324 | -0.183 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | -0.7 | -0.018 | +0.324 | +0.183 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | -0.7 | -0.018 | -0.324 | +0.183 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | -0.7 | -0.018 | +0.324 | -0.183 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | -0.7 | -0.018 | -0.324 | -0.183 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.032 | +0.320 | +0.191 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.032 | -0.320 | +0.191 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.032 | +0.320 | -0.191 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.032 | -0.320 | -0.191 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.009 | +0.324 | +0.184 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.009 | -0.324 | +0.184 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.009 | +0.324 | -0.184 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.009 | -0.324 | -0.184 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.029 | +0.325 | +0.181 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.029 | -0.325 | +0.181 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.029 | +0.325 | -0.181 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.029 | -0.325 | -0.181 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.025 | +0.325 | +0.182 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.025 | -0.325 | +0.182 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.025 | +0.325 | -0.182 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.025 | -0.325 | -0.182 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PWR-001` | power | energy | 414.0 | -0.054 | +0.000 | +0.046 | DATASHEET | 0 | `redesign/subsystems/power/parts.csv` |
| `PWR-002` | power | electrical | 18.6 | +0.017 | -0.046 | +0.046 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-003` | power | electrical | 28.0 | -0.036 | -0.046 | +0.046 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-004` | power | electrical | 8.8 | -0.021 | -0.046 | +0.021 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-006` | power | electrical | 8.1 | +0.004 | -0.046 | +0.039 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.146 | +0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.146 | -0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.146 | +0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.146 | -0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-009` | power | electrical | 2.2 | +0.146 | +0.330 | +0.107 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-009` | power | electrical | 2.2 | +0.146 | -0.330 | +0.107 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-009` | power | electrical | 2.2 | +0.146 | +0.330 | -0.107 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-009` | power | electrical | 2.2 | +0.146 | -0.330 | -0.107 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-010` | power | electrical | 2.2 | +0.146 | +0.330 | +0.129 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-010` | power | electrical | 2.2 | +0.146 | -0.330 | +0.129 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-010` | power | electrical | 2.2 | +0.146 | +0.330 | -0.129 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-010` | power | electrical | 2.2 | +0.146 | -0.330 | -0.129 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-101` | power | electrical | 0.6 | -0.021 | -0.046 | +0.032 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-102` | power | electrical | 0.9 | -0.021 | -0.046 | +0.032 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-103` | power | electrical | 0.1 | -0.021 | -0.046 | +0.039 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-107` | power | electrical | 1.6 | -0.021 | -0.046 | +0.024 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `AVN-001` | avionics | avionics | 12.0 | -0.012 | +0.046 | +0.029 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-002` | avionics | avionics | 7.7 | +0.076 | +0.000 | +0.178 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-003` | avionics | avionics | 4.6 | -0.047 | -0.046 | +0.024 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-004` | avionics | avionics | 4.0 | -0.070 | -0.046 | +0.028 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-005` | avionics | avionics | 4.2 | -0.167 | -0.046 | +0.045 | EST | 20 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-006` | avionics | avionics | 2.4 | -0.010 | +0.046 | +0.023 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-007` | avionics | avionics | 0.4 | -0.030 | +0.046 | +0.028 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `HRN-001` | harness | electrical | 38.3 | +0.042 | -0.006 | +0.031 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 39.5 | +0.080 | +0.256 | +0.005 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 39.5 | +0.080 | -0.256 | +0.005 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-A3-ROUTED` | harness | electrical | 35.1 | +0.058 | +0.009 | +0.025 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | +0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | -0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | +0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | -0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.230 | +0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.230 | -0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 2.8 | +0.264 | +0.286 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 2.8 | +0.264 | -0.286 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 2.1 | +0.250 | +0.339 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 2.1 | +0.250 | -0.339 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.6 | +0.265 | +0.391 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.6 | +0.265 | -0.391 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.5 | +0.190 | +0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.5 | +0.190 | -0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | +0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | -0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.3 | +0.257 | +0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.3 | +0.257 | -0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.3 | +0.257 | +0.442 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.3 | +0.257 | -0.442 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | +0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | -0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-011` | mechanisms | controls | 0.4 | +0.190 | +0.257 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-011` | mechanisms | controls | 0.4 | +0.190 | -0.257 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-012` | mechanisms | controls | 0.2 | +0.195 | +0.286 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-012` | mechanisms | controls | 0.2 | +0.195 | -0.286 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | +0.285 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | -0.285 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | +0.392 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | -0.392 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
