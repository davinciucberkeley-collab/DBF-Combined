# A3 live mass roll-up (generated)

Run `python -I redesign/team/A3/mass_rollup.py`. 140 instances, basic 2339 g, predicted 2493 g, gate 2600 g.

### Live roll-up

Sources: `wing` ← redesign/team/A3/mass_model.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv, redesign/team/A3/mass_model.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/team/A3/mass_model.csv; `avionics` ← redesign/team/A3/mass_model.csv; `harness` ← redesign/team/A3/mass_model.csv; `mechanisms` ← redesign/team/A3/mass_model.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 402 | 453 | -2 | `PROPOSED` |
| fins | 408 | 417 | 438 | +9 | `FAIL` |
| pod | 122 | 127 | 134 | +5 | `FAIL` |
| landing | 43 | 43 | 45 | -0 | `PROPOSED` |
| propulsion | 476 | 476 | 506 | -0 | `PROPOSED` |
| power | 620 | 619 | 624 | -1 | `PROPOSED` |
| avionics | 80 | 78 | 88 | -2 | `PROPOSED` |
| harness | 105 | 113 | 129 | +8 | `FAIL` |
| mechanisms | 65 | 64 | 77 | -1 | `PROPOSED` |
| **total** | **2 600** | **2 339** | **2 493** | allocated 2 324 + growth 276 | gate margin +107 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| lightest listing | 503 | 2 446 | +154 | 100 | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 493 | +107 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| heaviest listing | 680 | 2 623 | -23 | 100 | `CL-A3-GATE-MARGIN-680` | `FAIL` |

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 989 | 1 069 | 42 % |
| propulsion | 476 | 506 | 20 % |
| energy | 550 | 550 | 24 % |
| electrical | 182 | 203 | 8 % |
| avionics | 78 | 88 | 3 % |
| controls | 64 | 77 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.050–0.055 (16%–17%) | ±0.005 | -0.020…+0.030 | `PROPOSED` |
| Take-off, basic | 0.055 (17.1%) | -0.0008 | +0.016 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.057 (17.7%) | -0.0009 | +0.016 | `FAIL` |
| Pack slid -3.4 … +8.0 mm (spacers, crush stack) | 0.0540 … 0.0567 | | | — |
| Pack 503 g: nominal station → slid -4.3 mm (+ aft) | 0.0559 → 0.0550 | | | `FAIL` |
| Pack 550 g: nominal station → slid +0.0 mm (+ aft) | 0.0548 → 0.0548 | | | `CHECKED` |
| Pack 680 g: nominal station → slid +0.0 mm (+ aft) | 0.0519 → 0.0519 | | | `CHECKED` |
| No pack (handling) | 0.072 (22.5%) | -0.0010 | +0.008 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.053 m | -0.001 / -0.010 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | -9 | mm | `CALC-A3-CG` |
| or the whole pod group (825 g: pod, power, avionics) by | -6 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 476 g) by | -11 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 260 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.24 / 0.35 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 3 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.190 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 503–680 g beyond the trim travel | 0.9 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0044 | m | `CALC-A3-CG` |
| Lateral CG offset / allowed 5 mm | 0.16 (-0.8 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.313 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1712 | 0.0425 | 0.1640 | -0.0018 | kg·m² |
| Radius of gyration | 0.271 | 0.135 | 0.265 | | m |

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 324 g + reserve 276 g = 2 600 g).

A3 adders kept beside a designer's parts.csv (items the list does not carry yet): GER-E02 (landing, 3.4 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): PRP-002: ESC 11.0 g with leads and heat-shrink is EST per E1 parts.csv notes (6.6 g bare board is the only datasheet number).

Excluded as ground items (no interface node, notes say not flying): GER-005 (redesign/subsystems/landing/parts.csv): Spare insert kit (piston + cartridge + pad, pre-glued).

Zero-mass lines (mass carried inside another part): FIN-101, FIN-102, FIN-103, FIN-104, FIN-105, FIN-106, FIN-107, GER-006, PRP-005.



## Items (one row per instance)

| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |
|---|---|---|---|---|---|---|---|---|---|
| `WNG-E01` | wing | structure | 201.9 | +0.134 | +0.000 | +0.000 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `WNG-E02` | wing | structure | 48.6 | +0.160 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E03` | wing | structure | 102.0 | +0.080 | +0.000 | +0.007 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `WNG-E04` | wing | structure | 15.0 | +0.080 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E05` | wing | structure | 5.0 | +0.160 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E06` | wing | structure | 7.0 | +0.080 | +0.320 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E06` | wing | structure | 7.0 | +0.080 | -0.320 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E07` | wing | structure | 4.0 | +0.080 | +0.242 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E07` | wing | structure | 4.0 | +0.080 | +0.242 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E07` | wing | structure | 4.0 | +0.080 | -0.242 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E07` | wing | structure | 4.0 | +0.080 | -0.242 | +0.007 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-001` | fins | structure | 22.3 | +0.200 | +0.320 | +0.101 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 22.3 | +0.200 | -0.320 | +0.101 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 22.3 | +0.197 | +0.320 | -0.098 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-001` | fins | structure | 22.3 | +0.197 | -0.320 | -0.098 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | +0.320 | +0.000 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-002` | fins | structure | 35.1 | +0.045 | -0.320 | +0.000 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.040 | +0.322 | +0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.040 | -0.322 | +0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.040 | +0.322 | -0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-003` | fins | structure | 11.0 | +0.040 | -0.322 | -0.181 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 40.9 | +0.061 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-004` | fins | structure | 40.9 | +0.061 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | +0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-006` | fins | structure | 5.5 | +0.045 | -0.320 | +0.007 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 1.9 | +0.101 | +0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 1.9 | +0.101 | -0.325 | +0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 1.9 | +0.101 | +0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-007` | fins | structure | 1.9 | +0.101 | -0.325 | -0.118 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.6 | +0.064 | +0.317 | +0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.6 | +0.064 | -0.317 | +0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.6 | +0.064 | +0.317 | -0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-008` | fins | structure | 10.6 | +0.064 | -0.317 | -0.157 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | +0.272 | +0.090 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | -0.272 | +0.090 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | +0.272 | -0.083 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-009` | fins | structure | 5.2 | +0.062 | -0.272 | -0.083 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | +0.024 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | +0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-010` | fins | structure | 3.2 | +0.080 | -0.242 | -0.011 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | +0.325 | +0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | +0.315 | +0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | -0.325 | +0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | -0.315 | +0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | +0.325 | -0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | +0.315 | -0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | -0.325 | -0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-011` | fins | structure | 4.2 | +0.168 | -0.315 | -0.180 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | +0.320 | +0.183 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | -0.320 | +0.183 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | +0.320 | -0.183 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `FIN-012` | fins | structure | 1.1 | +0.184 | -0.320 | -0.183 | CAD | 5 | `redesign/subsystems/fins/parts.csv` |
| `POD-001` | pod | structure | 23.4 | -0.031 | -0.000 | +0.044 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-002` | pod | structure | 30.0 | -0.035 | -0.003 | +0.024 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-003` | pod | structure | 8.5 | -0.029 | -0.004 | +0.083 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-004` | pod | structure | 9.1 | -0.001 | +0.000 | +0.044 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-005` | pod | structure | 6.6 | +0.081 | +0.000 | +0.156 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-006` | pod | structure | 5.8 | -0.107 | -0.046 | +0.045 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-007` | pod | structure | 34.8 | +0.080 | -0.000 | +0.061 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `POD-008` | pod | structure | 9.1 | -0.052 | +0.000 | +0.045 | CAD | 5 | `redesign/subsystems/pod/parts.csv` |
| `GER-001` | landing | structure | 4.2 | +0.303 | +0.320 | +0.198 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 4.2 | +0.303 | -0.320 | +0.198 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 4.2 | +0.303 | +0.320 | -0.198 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-001` | landing | structure | 4.2 | +0.303 | -0.320 | -0.198 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 4.2 | +0.346 | +0.320 | +0.202 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 4.2 | +0.346 | -0.320 | +0.202 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 4.2 | +0.346 | +0.320 | -0.202 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-002` | landing | structure | 4.2 | +0.346 | -0.320 | -0.202 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.322 | +0.320 | +0.201 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.322 | -0.320 | +0.201 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.322 | +0.320 | -0.201 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-003` | landing | structure | 0.5 | +0.322 | -0.320 | -0.201 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.9 | +0.364 | +0.320 | +0.204 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.9 | +0.364 | -0.320 | +0.204 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.9 | +0.364 | +0.320 | -0.204 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-004` | landing | structure | 0.9 | +0.364 | -0.320 | -0.204 | CAD | 5 | `redesign/subsystems/landing/parts.csv` |
| `GER-E02` | landing | structure | 0.8 | +0.344 | +0.320 | +0.210 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E02` | landing | structure | 0.8 | +0.344 | -0.320 | +0.210 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E02` | landing | structure | 0.8 | +0.344 | +0.320 | -0.210 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E02` | landing | structure | 0.8 | +0.344 | -0.320 | -0.210 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.019 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.019 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.019 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-001` | propulsion | propulsion | 84.2 | +0.019 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 11.0 | +0.101 | +0.330 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 11.0 | +0.101 | -0.330 | +0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 11.0 | +0.101 | +0.330 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-002` | propulsion | propulsion | 11.0 | +0.101 | -0.330 | -0.118 | EST | 20 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-003` | propulsion | propulsion | 17.0 | -0.008 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.001 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.001 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.001 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PRP-004` | propulsion | propulsion | 6.7 | -0.001 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/subsystems/propulsion/parts.csv` |
| `PWR-E01` | power | energy | 550.0 | -0.001 | +0.000 | +0.043 | DATASHEET | 0 | `redesign/team/A3/mass_model.csv` |
| `PWR-E02` | power | electrical | 10.0 | +0.045 | -0.046 | +0.035 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PWR-E03` | power | electrical | 29.0 | +0.030 | -0.030 | +0.035 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `PWR-E04` | power | electrical | 13.0 | -0.040 | -0.046 | +0.030 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PWR-E05` | power | electrical | 6.0 | -0.060 | -0.046 | +0.030 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PWR-E06` | power | electrical | 3.0 | -0.030 | -0.046 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PWR-E07` | power | electrical | 8.0 | -0.060 | -0.046 | +0.040 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `AVN-E01` | avionics | avionics | 42.0 | -0.010 | +0.046 | +0.030 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `AVN-E02` | avionics | avionics | 10.0 | +0.080 | +0.000 | +0.169 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E03` | avionics | avionics | 3.0 | -0.030 | -0.046 | +0.025 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E04` | avionics | avionics | 5.0 | -0.085 | -0.046 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E05` | avionics | avionics | 13.0 | -0.150 | -0.046 | +0.045 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E06` | avionics | avionics | 5.0 | -0.010 | +0.046 | +0.022 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E07` | avionics | avionics | 0.5 | -0.010 | +0.046 | +0.030 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 16.2 | +0.025 | +0.160 | +0.057 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 16.2 | +0.025 | -0.160 | +0.057 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 16.2 | +0.025 | +0.160 | -0.057 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 16.2 | +0.025 | -0.160 | -0.057 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.055 | +0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.055 | -0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.055 | +0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.055 | -0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | +0.320 | +0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | -0.320 | +0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | +0.320 | -0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | -0.320 | -0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E04` | harness | electrical | 5.0 | +0.192 | +0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E04` | harness | electrical | 5.0 | +0.192 | -0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E05` | harness | electrical | 6.0 | -0.015 | +0.000 | +0.040 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E06` | harness | electrical | 5.0 | +0.000 | +0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E06` | harness | electrical | 5.0 | +0.000 | -0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E01` | mechanisms | controls | 18.5 | +0.202 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E01` | mechanisms | controls | 18.5 | +0.202 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E03` | mechanisms | controls | 3.0 | +0.226 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E03` | mechanisms | controls | 3.0 | +0.226 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E04` | mechanisms | controls | 3.0 | +0.285 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E04` | mechanisms | controls | 3.0 | +0.285 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E05` | mechanisms | controls | 4.0 | +0.250 | +0.315 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E05` | mechanisms | controls | 4.0 | +0.250 | -0.315 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E06` | mechanisms | controls | 2.0 | +0.202 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E06` | mechanisms | controls | 2.0 | +0.202 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
