# A3 live mass roll-up (generated)

Run `python -I redesign/team/A3/mass_rollup.py`. 189 instances, basic 2378 g, predicted 2502 g, gate 2600 g.

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv, redesign/team/A3/mass_model.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 393 | 391 | 410 | -2 | `PROPOSED` |
| fins | 435 | 435 | 457 | -0 | `PROPOSED` |
| pod | 146 | 146 | 153 | -0 | `PROPOSED` |
| landing | 71 | 70 | 77 | -1 | `PROPOSED` |
| propulsion | 462 | 462 | 490 | +0 | `PROPOSED` |
| power | 627 | 626 | 636 | -2 | `PROPOSED` |
| avionics | 37 | 35 | 38 | -2 | `PROPOSED` |
| harness | 142 | 141 | 159 | -1 | `PROPOSED` |
| mechanisms | 73 | 73 | 83 | +0 | `FAIL` |
| **total** | **2 600** | **2 378** | **2 502** | allocated 2 386 + growth 214 | gate margin +98 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| listing minimum (D-64) | 546 | 2 498 | +102 | 84 | `CL-A3-GATE-MARGIN-546` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 502 | +98 | 84 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| listed (D-64) | 551 | 2 503 | +97 | 84 | `CALC-A3-MASS` | `MODELLED` |
| heavy bounding case, above the acceptance line (D-95) | 590 | 2 542 | +58 | 84 | `CL-A3-GATE-MARGIN-590` | rejected at `T-E2-WEIGH` |

Pack acceptance (heaviest weighed pack that leaves the 84 g overrun under the gate): **563.6 g** (`CL-A3-PACK-ACCEPT`; SKU listing maximum 556 g, margin +7.6 g).

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 1 041 | 1 097 | 44 % |
| propulsion | 462 | 490 | 19 % |
| energy | 550 | 550 | 23 % |
| electrical | 217 | 246 | 9 % |
| avionics | 35 | 38 | 1 % |
| controls | 73 | 83 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.039–0.051 (12%–16%) | ±0.005 | +0.017…+0.025 | `PROPOSED` |
| Take-off, basic | 0.050 (15.5%) | -0.0015 | +0.018 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.051 (16.0%) | -0.0016 | +0.018 | `CHECKED` |
| Pack slid -1.9 … +16.0 mm (spacers, crush stack) | 0.0492 … 0.0533 | | | — |
| Pack 546 g: nominal station → slid +0.0 mm (+ aft) | 0.0497 → 0.0497 | | | `CHECKED` |
| Pack 551 g: nominal station → slid +0.0 mm (+ aft) | 0.0496 → 0.0496 | | | `CHECKED` |
| Pack 590 g: nominal station → slid +0.0 mm (+ aft) | 0.0482 → 0.0482 | | | `CHECKED` |
| Pack 546 g at its D-98 station x -0.0360 (spacers 16 mm, clamped): basic → predicted | 0.0497 → 0.0514 (fwd +10.3 / aft -0.1 mm) | | | `FAIL` |
| Pack 551 g at its D-98 station x -0.0360 (spacers 16 mm, clamped): basic → predicted | 0.0496 → 0.0512 (fwd +10.2 / aft +0.1 mm) | | | `CHECKED` |
| Pack 590 g at its D-98 station x -0.0360 (spacers 16 mm, clamped): basic → predicted | 0.0482 → 0.0499 (fwd +8.8 / aft +1.4 mm) | | | `CHECKED` |
| No pack (handling) | 0.075 (23.5%) | -0.0019 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.049 m | -0.036 / -0.039 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | -3 | mm | `CALC-A3-CG` |
| or the whole pod group (806 g: pod, power, avionics) by | -2 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 462 g) by | -3 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 291 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.23 / 0.34 / 0.19 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 2 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.213 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 546–590 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0379 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.71 / 1.01 / 0.99 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| CG height z: basic / predicted (A1 copies to `cg.z_target_m`) | 0.0183 / 0.0179 | m | `CL-A3-CG-Z` / `CL-A3-CG-Z-PRED` |
| CG z range use (worst of basic, predicted) | 0.66 | — | `CL-A3-CG-Z-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.30 (-1.5 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.318 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1790 | 0.0482 | 0.1753 | -0.0026 | kg·m² |
| Radius of gyration | 0.274 | 0.142 | 0.271 | | m |

Groups for C1's loads model (`CL-A3-GROUPS`; inertia about each group's own centroid, aircraft axes; closure to the aircraft inertia 7.8e-16, `CL-A3-GROUPS-CLOSURE`):

| Group | Station | Items | Mass g | x m | y m | z m | Ixx own | Iyy own | Izz own | Ixz own |
|---|---|---|---|---|---|---|---|---|---|---|
| **pack** | all | 1 | 550.0 | -0.0360 | +0.0000 | +0.0478 | 0.00021 | 0.00095 | 0.00093 | -0.00000 |
| **centre** | all | 29 | 299.6 | -0.0008 | -0.0125 | +0.0462 | 0.00088 | 0.00125 | 0.00156 | +0.00017 |
| **wing** | all | 15 | 390.8 | +0.1138 | +0.0005 | +0.0054 | 0.03949 | 0.00269 | 0.04213 | -0.00002 |
| wing | C | 4 | 351.9 | +0.1094 | +0.0000 | +0.0055 | 0.03564 | 0.00227 | 0.03785 | -0.00000 |
| wing | L | 5 | 19.2 | +0.1531 | -0.3012 | +0.0042 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| wing | R | 6 | 19.7 | +0.1534 | +0.3034 | +0.0045 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| **fins** | all | 50 | 384.1 | +0.1036 | +0.0000 | +0.0023 | 0.04250 | 0.00652 | 0.04055 | -0.00001 |
| fins | L | 7 | 89.6 | +0.0550 | -0.3150 | +0.0041 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | LL | 9 | 51.2 | +0.1449 | -0.3152 | -0.1172 | 0.00018 | 0.00053 | 0.00037 | +0.00006 |
| fins | LR | 9 | 51.2 | +0.1449 | +0.3152 | -0.1172 | 0.00018 | 0.00053 | 0.00037 | +0.00006 |
| fins | R | 7 | 89.6 | +0.0550 | +0.3150 | +0.0041 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | UL | 9 | 51.2 | +0.1472 | -0.3152 | +0.1187 | 0.00018 | 0.00054 | 0.00039 | -0.00007 |
| fins | UR | 9 | 51.2 | +0.1472 | +0.3152 | +0.1187 | 0.00018 | 0.00054 | 0.00039 | -0.00007 |
| **stations** | all | 44 | 521.6 | +0.0179 | +0.0000 | +0.0000 | 0.07185 | 0.01789 | 0.05509 | -0.00000 |
| stations | LL | 11 | 130.4 | +0.0179 | -0.3219 | -0.1809 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | LR | 11 | 130.4 | +0.0179 | +0.3219 | -0.1809 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | UL | 11 | 130.4 | +0.0179 | -0.3219 | +0.1809 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| stations | UR | 11 | 130.4 | +0.0179 | +0.3219 | +0.1809 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| **landing** | all | 18 | 69.9 | +0.3076 | +0.0000 | +0.0002 | 0.01032 | 0.00288 | 0.00751 | +0.00000 |
| landing | L | 1 | 0.7 | +0.3105 | -0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | LL | 4 | 17.1 | +0.3075 | -0.3200 | -0.2040 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | LR | 4 | 17.1 | +0.3075 | +0.3200 | -0.2040 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | R | 1 | 0.7 | +0.3105 | +0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | UL | 4 | 17.1 | +0.3076 | -0.3200 | +0.2040 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| landing | UR | 4 | 17.1 | +0.3076 | +0.3200 | +0.2040 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| **mechanisms** | all | 30 | 73.3 | +0.2176 | +0.0000 | -0.0022 | 0.00634 | 0.00009 | 0.00643 | -0.00000 |
| mechanisms | L | 15 | 36.7 | +0.2176 | -0.2891 | -0.0022 | 0.00011 | 0.00005 | 0.00015 | -0.00000 |
| mechanisms | R | 15 | 36.7 | +0.2176 | +0.2891 | -0.0022 | 0.00011 | 0.00005 | 0.00015 | -0.00000 |
| **harness** | all | 2 | 89.1 | +0.0782 | +0.0000 | +0.0049 | 0.00620 | 0.00000 | 0.00620 | -0.00000 |
| harness | L | 1 | 44.5 | +0.0782 | -0.2638 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| harness | R | 1 | 44.5 | +0.0782 | +0.2638 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |

(own inertias in kg·m²)

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 386 g + reserve 214 g = 2 600 g).

A3 adders kept beside a designer's parts.csv (items the list does not carry yet): HRN-A3-ROUTED (harness, 13.8 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GND-001 (redesign/subsystems/ground/parts.csv, flight false): RC transmitter RadioMaster Pocket (Crush), internal ELRS 2.4 GHz FCC, with 2 x 18650 cells; GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 5/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, HRN-102, HRN-113, HRN-114, PWR-104, PWR-105, PWR-106, PWR-202.

Roll-up warnings:

- harness: parts.csv totals 127 g, A3 estimate 201 g: missing parts or masses?



## Items (one row per instance)

| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |
|---|---|---|---|---|---|---|---|---|---|
| `WNG-001` | wing | structure | 198.1 | +0.119 | +0.000 | +0.005 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-002` | wing | structure | 102.0 | +0.080 | +0.000 | +0.007 | DATASHEET | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-003` | wing | structure | 47.9 | +0.133 | +0.000 | +0.004 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | +0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | -0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-006` | wing | structure | 1.0 | +0.062 | +0.320 | +0.006 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-006` | wing | structure | 1.0 | +0.062 | -0.320 | +0.006 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-008` | wing | structure | 3.9 | +0.080 | +0.000 | -0.005 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.7 | +0.277 | +0.183 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.7 | +0.277 | -0.183 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.5 | +0.278 | +0.451 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.5 | +0.278 | -0.451 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-020` | wing | structure | 0.5 | +0.165 | +0.390 | +0.017 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `FIN-001` | fins | structure | 23.6 | +0.208 | +0.320 | +0.083 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.6 | +0.208 | -0.320 | +0.083 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.6 | +0.203 | +0.320 | -0.082 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 23.6 | +0.203 | -0.320 | -0.082 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | +0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | -0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 10.7 | +0.037 | +0.321 | +0.179 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 10.7 | +0.037 | -0.321 | +0.179 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 10.7 | +0.037 | +0.321 | -0.179 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 10.7 | +0.037 | -0.321 | -0.179 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 40.0 | +0.062 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 40.0 | +0.062 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
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
| `FIN-011` | fins | structure | 3.9 | +0.159 | +0.325 | +0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | +0.315 | +0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | -0.325 | +0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | -0.315 | +0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | +0.325 | -0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | +0.315 | -0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | -0.325 | -0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 3.9 | +0.159 | -0.315 | -0.177 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.177 | +0.320 | +0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.177 | -0.320 | +0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.177 | +0.320 | -0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.6 | +0.177 | -0.320 | -0.181 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
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
| `POD-001` | pod | structure | 24.8 | -0.039 | -0.001 | +0.043 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-002` | pod | structure | 41.2 | -0.035 | -0.004 | +0.025 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-003` | pod | structure | 9.2 | -0.041 | -0.003 | +0.083 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-004` | pod | structure | 9.1 | -0.036 | +0.000 | +0.043 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-005` | pod | structure | 5.5 | +0.081 | +0.000 | +0.156 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-006` | pod | structure | 5.8 | -0.132 | -0.046 | +0.045 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-007` | pod | structure | 39.8 | +0.077 | -0.003 | +0.058 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-008` | pod | structure | 2.4 | +0.040 | +0.000 | +0.027 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-009` | pod | structure | 2.2 | -0.118 | +0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-010` | pod | structure | 5.3 | -0.104 | +0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-011` | pod | structure | 0.1 | +0.080 | -0.003 | +0.122 | DATASHEET | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-012` | pod | structure | 0.1 | +0.080 | -0.008 | +0.122 | DATASHEET | 5 | `redesign/subsystems/pod/parts.csv` |
| `GER-001` | landing | structure | 12.7 | +0.296 | +0.320 | +0.202 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 12.7 | +0.296 | -0.320 | +0.202 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 12.7 | +0.296 | +0.320 | -0.202 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 12.7 | +0.296 | -0.320 | -0.202 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.2 | +0.339 | +0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.2 | +0.339 | -0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.2 | +0.339 | +0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.2 | +0.339 | -0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.314 | +0.320 | +0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.314 | -0.320 | +0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.367 | +0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.367 | -0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.367 | +0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.7 | +0.367 | -0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | +0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | -0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.5 | +0.314 | +0.320 | -0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.5 | +0.314 | -0.320 | -0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `PRP-001` | propulsion | propulsion | 81.0 | +0.011 | +0.321 | +0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 81.0 | +0.011 | -0.321 | +0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 81.0 | +0.011 | +0.321 | -0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 81.0 | +0.011 | -0.321 | -0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.013 | +0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.013 | -0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.013 | +0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.013 | -0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 3.0 | -0.010 | +0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 3.0 | -0.010 | -0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 3.0 | -0.010 | +0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 3.0 | -0.010 | -0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.028 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.028 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.028 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-005` | propulsion | propulsion | 3.2 | +0.028 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.004 | +0.322 | +0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.004 | -0.322 | +0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.004 | +0.322 | -0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-006` | propulsion | propulsion | 1.2 | -0.004 | -0.322 | -0.187 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.021 | +0.323 | +0.185 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.021 | -0.323 | +0.185 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.021 | +0.323 | -0.185 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-007` | propulsion | propulsion | 1.9 | -0.021 | -0.323 | -0.185 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.018 | +0.323 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.018 | -0.323 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.018 | +0.323 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-008` | propulsion | propulsion | 0.6 | -0.018 | -0.323 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PWR-001` | power | energy | 550.0 | -0.036 | +0.000 | +0.048 | DATASHEET | 0 | `redesign/subsystems/power/parts.csv` |
| `PWR-002` | power | electrical | 18.6 | +0.017 | -0.046 | +0.046 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-003` | power | electrical | 28.0 | -0.036 | -0.046 | +0.046 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-004` | power | electrical | 8.8 | -0.021 | -0.046 | +0.021 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-006` | power | electrical | 8.1 | +0.004 | -0.046 | +0.039 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.147 | +0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.147 | -0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.147 | +0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.147 | -0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-101` | power | electrical | 0.6 | -0.021 | -0.046 | +0.032 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-102` | power | electrical | 0.9 | -0.021 | -0.046 | +0.032 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-103` | power | electrical | 0.1 | -0.021 | -0.046 | +0.039 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-107` | power | electrical | 1.6 | -0.021 | -0.046 | +0.024 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `AVN-001` | avionics | avionics | 12.0 | +0.004 | +0.049 | +0.028 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-002` | avionics | avionics | 7.7 | +0.080 | +0.000 | +0.182 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-003` | avionics | avionics | 4.6 | -0.045 | -0.046 | +0.026 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-004` | avionics | avionics | 4.0 | -0.070 | -0.046 | +0.031 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-005` | avionics | avionics | 4.2 | -0.160 | -0.046 | +0.045 | EST | 20 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-006` | avionics | avionics | 2.4 | -0.010 | +0.046 | +0.023 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-007` | avionics | avionics | 0.4 | -0.030 | +0.046 | +0.028 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `HRN-001` | harness | electrical | 38.2 | +0.041 | -0.006 | +0.031 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 44.5 | +0.078 | +0.264 | +0.005 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 44.5 | +0.078 | -0.264 | +0.005 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-A3-ROUTED` | harness | electrical | 13.8 | +0.050 | +0.003 | +0.041 | CALC | 38 | `redesign/team/A3/mass_model.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | +0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | -0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | +0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | -0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.230 | +0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.230 | -0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 2.9 | +0.264 | +0.286 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 2.9 | +0.264 | -0.286 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 0.8 | +0.250 | +0.320 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 0.8 | +0.250 | -0.320 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.6 | +0.265 | +0.354 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.6 | +0.265 | -0.354 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.5 | +0.190 | +0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.5 | +0.190 | -0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | +0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | -0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | +0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | -0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | +0.450 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | -0.450 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | +0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | -0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-011` | mechanisms | controls | 0.4 | +0.190 | +0.257 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-011` | mechanisms | controls | 0.4 | +0.190 | -0.257 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-012` | mechanisms | controls | 0.2 | +0.195 | +0.286 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-012` | mechanisms | controls | 0.2 | +0.195 | -0.286 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | +0.285 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | -0.285 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | +0.355 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-013` | mechanisms | controls | 0.6 | +0.276 | -0.355 | +0.003 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
