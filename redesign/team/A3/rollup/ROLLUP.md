# A3 live mass roll-up (generated)

Run `python -I redesign/team/A3/mass_rollup.py`. 141 instances, basic 2322 g, predicted 2436 g, gate 2600 g.

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 387 | 407 | -18 | `PROPOSED` |
| fins | 418 | 436 | 458 | +18 | `FAIL` |
| pod | 131 | 131 | 137 | -0 | `PROPOSED` |
| landing | 43 | 42 | 47 | -0 | `PROPOSED` |
| propulsion | 462 | 462 | 490 | +0 | `PROPOSED` |
| power | 648 | 638 | 650 | -10 | `PROPOSED` |
| avionics | 45 | 36 | 39 | -8 | `PROPOSED` |
| harness | 123 | 117 | 129 | -6 | `PROPOSED` |
| mechanisms | 80 | 71 | 80 | -9 | `PROPOSED` |
| **total** | **2 600** | **2 322** | **2 436** | allocated 2 355 + growth 245 | gate margin +164 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| lightest listing | 503 | 2 389 | +211 | 100 | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 436 | +164 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| heaviest listing | 680 | 2 566 | +34 | 100 | `CL-A3-GATE-MARGIN-680` | `FAIL` |

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 997 | 1 049 | 43 % |
| propulsion | 462 | 490 | 20 % |
| energy | 550 | 550 | 24 % |
| electrical | 205 | 228 | 9 % |
| avionics | 36 | 39 | 2 % |
| controls | 71 | 80 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.050–0.055 (16%–17%) | ±0.005 | -0.020…+0.030 | `PROPOSED` |
| Take-off, basic | 0.052 (16.3%) | -0.0011 | +0.019 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.054 (16.7%) | -0.0013 | +0.018 | `CHECKED` |
| Pack slid -3.4 … +12.0 mm (spacers, crush stack) | 0.0514 … 0.0551 | | | — |
| Pack 503 g: nominal station → slid +0.0 mm (+ aft) | 0.0537 → 0.0537 | | | `CHECKED` |
| Pack 550 g: nominal station → slid +0.0 mm (+ aft) | 0.0522 → 0.0522 | | | `CHECKED` |
| Pack 680 g: nominal station → slid +6.2 mm (+ aft) | 0.0483 → 0.0500 | | | `CHECKED` |
| Pack 503 g at its D-59 station x -0.0254 (spacers 15 mm, clamped): basic → predicted | 0.0530 → 0.0544 (fwd +3.0 / aft +0.5 mm) | | | `CHECKED` |
| Pack 550 g at its D-59 station x -0.0220 (spacers 12 mm): basic → predicted | 0.0522 → 0.0536 (fwd +2.2 / aft +1.3 mm) | | | `CHECKED` |
| Pack 680 g at its D-59 station x -0.0100 (spacers 0 mm, clamped): basic → predicted | 0.0516 → 0.0529 (fwd +1.6 / aft +2.0 mm) | | | `CHECKED` |
| No pack (handling) | 0.075 (23.5%) | -0.0015 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.052 m | -0.022 / -0.022 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | +0 | mm | `CALC-A3-CG` |
| or the whole pod group (806 g: pod, power, avionics) by | +0 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 462 g) by | +0 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 272 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.24 / 0.35 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 3 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.216 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 503–680 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0254 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.10 / 0.78 / 0.47 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.23 (-1.1 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.316 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1732 | 0.0442 | 0.1679 | -0.0023 | kg·m² |
| Radius of gyration | 0.273 | 0.138 | 0.269 | | m |

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 355 g + reserve 245 g = 2 600 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 7/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-101, FIN-102, FIN-103, FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-102, HRN-103, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, PWR-101, PWR-102, PWR-103, PWR-104, PWR-105, PWR-106, PWR-202, PRP-005.



## Items (one row per instance)

| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |
|---|---|---|---|---|---|---|---|---|---|
| `WNG-001` | wing | structure | 202.0 | +0.119 | +0.000 | +0.005 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-002` | wing | structure | 102.0 | +0.080 | +0.000 | +0.007 | DATASHEET | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-003` | wing | structure | 46.4 | +0.133 | +0.000 | +0.004 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-004` | wing | structure | 7.0 | +0.080 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | +0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-005` | wing | structure | 4.0 | +0.080 | -0.242 | +0.007 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.7 | +0.278 | +0.184 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-011` | wing | structure | 3.7 | +0.278 | -0.184 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.5 | +0.278 | +0.451 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-012` | wing | structure | 3.5 | +0.278 | -0.451 | +0.000 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `WNG-020` | wing | structure | 0.5 | +0.165 | +0.390 | +0.017 | CAD | 5 | `redesign/subsystems/wing/parts.csv` |
| `FIN-001` | fins | structure | 27.7 | +0.207 | +0.320 | +0.074 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 27.7 | +0.207 | -0.320 | +0.074 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 27.7 | +0.201 | +0.320 | -0.072 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 27.7 | +0.201 | -0.320 | -0.072 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | +0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | -0.320 | +0.000 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.039 | +0.322 | +0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.039 | -0.322 | +0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.039 | +0.322 | -0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.039 | -0.322 | -0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 41.0 | +0.061 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 41.0 | +0.061 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | +0.320 | +0.007 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | -0.320 | +0.007 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | +0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | -0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | +0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 2.0 | +0.101 | -0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.1 | +0.065 | +0.316 | +0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.1 | +0.065 | -0.316 | +0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.1 | +0.065 | +0.316 | -0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.1 | +0.065 | -0.316 | -0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | +0.272 | +0.090 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | -0.272 | +0.090 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | +0.272 | -0.083 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | -0.272 | -0.083 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | +0.325 | +0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | +0.315 | +0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | -0.325 | +0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | -0.315 | +0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | +0.325 | -0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | +0.315 | -0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | -0.325 | -0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.1 | +0.166 | -0.315 | -0.180 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | +0.320 | +0.184 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | -0.320 | +0.184 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | +0.320 | -0.184 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | -0.320 | -0.184 | DATASHEET | 5 | `redesign/subsystems/fins/parts.csv` |
| `POD-001` | pod | structure | 24.3 | -0.034 | -0.001 | +0.043 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-002` | pod | structure | 39.6 | -0.024 | +0.001 | +0.025 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-003` | pod | structure | 8.9 | -0.036 | -0.003 | +0.083 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-004` | pod | structure | 9.1 | -0.019 | +0.000 | +0.044 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-005` | pod | structure | 5.5 | +0.081 | +0.000 | +0.156 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-006` | pod | structure | 5.8 | -0.122 | -0.046 | +0.045 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-007` | pod | structure | 28.3 | +0.080 | -0.001 | +0.066 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-008` | pod | structure | 1.8 | +0.054 | +0.000 | +0.027 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-009` | pod | structure | 2.3 | -0.107 | +0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-010` | pod | structure | 5.3 | -0.093 | +0.000 | +0.048 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `GER-001` | landing | structure | 5.7 | +0.301 | +0.320 | +0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 5.7 | +0.301 | -0.320 | +0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 5.7 | +0.301 | +0.320 | -0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 5.7 | +0.301 | -0.320 | -0.208 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.1 | +0.344 | +0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.1 | +0.344 | -0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.1 | +0.344 | +0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 3.1 | +0.344 | -0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.7 | +0.320 | +0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.7 | +0.320 | -0.320 | +0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.8 | +0.367 | +0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.8 | +0.367 | -0.320 | +0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.8 | +0.367 | +0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.8 | +0.367 | -0.320 | -0.210 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | +0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-007` | landing | structure | 0.7 | +0.310 | -0.569 | -0.000 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.6 | +0.320 | +0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `GER-008` | landing | structure | 0.6 | +0.320 | -0.320 | -0.209 | CALC | 10 | `redesign/subsystems/landing/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.016 | +0.321 | +0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.016 | -0.321 | +0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.016 | +0.321 | -0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.016 | -0.321 | -0.189 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | +0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 7.6 | +0.101 | -0.329 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | +0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | -0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | +0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | -0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.005 | +0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.005 | -0.322 | +0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.005 | +0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.005 | -0.322 | -0.186 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PWR-001` | power | energy | 550.0 | -0.022 | +0.000 | +0.048 | DATASHEET | 0 | `redesign/subsystems/power/parts.csv` |
| `PWR-002` | power | electrical | 18.6 | +0.017 | -0.046 | +0.046 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-003` | power | electrical | 28.0 | -0.031 | -0.046 | +0.044 | EST | 20 | `redesign/subsystems/power/parts.csv` |
| `PWR-004` | power | electrical | 7.3 | -0.021 | -0.046 | +0.021 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-005` | power | electrical | 13.0 | +0.065 | +0.046 | +0.026 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-006` | power | electrical | 9.0 | +0.010 | -0.046 | +0.039 | CAD | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-007` | power | electrical | 3.5 | +0.017 | -0.059 | +0.032 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.137 | +0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.137 | -0.330 | +0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.137 | +0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `PWR-008` | power | electrical | 2.2 | +0.137 | -0.330 | -0.118 | DATASHEET | 5 | `redesign/subsystems/power/parts.csv` |
| `AVN-001` | avionics | avionics | 12.0 | -0.010 | +0.046 | +0.030 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-002` | avionics | avionics | 7.7 | +0.075 | +0.000 | +0.177 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-003` | avionics | avionics | 4.6 | -0.047 | -0.046 | +0.024 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-004` | avionics | avionics | 4.5 | -0.069 | -0.046 | +0.031 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-005` | avionics | avionics | 4.8 | -0.128 | -0.046 | +0.045 | EST | 20 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-006` | avionics | avionics | 2.4 | -0.010 | +0.046 | +0.023 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `AVN-007` | avionics | avionics | 0.4 | -0.030 | +0.046 | +0.027 | DATASHEET | 5 | `redesign/subsystems/avionics/parts.csv` |
| `HRN-001` | harness | electrical | 40.7 | +0.048 | -0.001 | +0.029 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 38.3 | +0.076 | +0.256 | +0.006 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `HRN-002` | harness | electrical | 38.3 | +0.076 | -0.256 | +0.006 | CALC | 10 | `redesign/subsystems/harness/parts.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | +0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-001` | mechanisms | controls | 15.8 | +0.190 | -0.268 | -0.000 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | +0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-002` | mechanisms | controls | 0.6 | +0.195 | -0.285 | -0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.231 | +0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-003` | mechanisms | controls | 1.6 | +0.231 | -0.285 | -0.018 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 3.1 | +0.265 | +0.286 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-004` | mechanisms | controls | 3.1 | +0.265 | -0.286 | -0.006 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 0.8 | +0.250 | +0.320 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-005` | mechanisms | controls | 0.8 | +0.250 | -0.320 | -0.011 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.7 | +0.266 | +0.354 | -0.004 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-006` | mechanisms | controls | 2.7 | +0.266 | -0.354 | -0.004 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.7 | +0.190 | +0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-007` | mechanisms | controls | 1.7 | +0.190 | -0.269 | -0.007 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | +0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-008` | mechanisms | controls | 3.2 | +0.190 | -0.265 | +0.002 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | +0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | -0.215 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | +0.450 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-009` | mechanisms | controls | 2.6 | +0.257 | -0.450 | +0.001 | EST | 20 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | +0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
| `MEC-010` | mechanisms | controls | 0.6 | +0.250 | -0.315 | +0.006 | DATASHEET | 5 | `redesign/subsystems/mechanisms/parts.csv` |
