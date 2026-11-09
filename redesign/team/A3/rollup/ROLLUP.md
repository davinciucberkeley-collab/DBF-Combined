# A3 live mass roll-up (generated)

Run `python -I redesign/team/A3/mass_rollup.py`. 84 instances, basic 2145 g, predicted 2492 g, gate 2600 g.

### Live roll-up

Sources: `avionics` ← redesign/team/A3/mass_model.csv; `fins` ← redesign/team/A3/mass_model.csv; `harness` ← redesign/team/A3/mass_model.csv; `landing` ← redesign/team/A3/mass_model.csv; `mechanisms` ← redesign/team/A3/mass_model.csv; `pod` ← redesign/team/A3/mass_model.csv; `power` ← redesign/team/A3/mass_model.csv; `propulsion` ← redesign/team/A3/mass_model.csv; `wing` ← redesign/team/A3/mass_model.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 392 | 438 | -13 | `PROPOSED` |
| fins | 370 | 369 | 435 | -1 | `PROPOSED` |
| pod | 105 | 102 | 122 | -3 | `PROPOSED` |
| landing | 40 | 24 | 29 | -16 | `PROPOSED` |
| propulsion | 440 | 438 | 463 | -2 | `PROPOSED` |
| power | 595 | 595 | 736 | +0 | `PROPOSED` |
| avionics | 75 | 66 | 79 | -9 | `PROPOSED` |
| harness | 105 | 104 | 125 | -1 | `PROPOSED` |
| mechanisms | 65 | 54 | 65 | -11 | `PROPOSED` |
| **total** | **2 600** | **2 145** | **2 492** | allocated 2 200 + growth 400 | gate margin +108 g |

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 888 | 1 024 | 41 % |
| propulsion | 438 | 463 | 20 % |
| energy | 550 | 682 | 26 % |
| electrical | 149 | 179 | 7 % |
| avionics | 66 | 79 | 3 % |
| controls | 54 | 65 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.040–0.049 (12%–15%) | ±0.005 | -0.020…+0.030 | `PROPOSED` |
| Take-off, basic | 0.044 (13.8%) | +0.0000 | +0.017 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.043 (13.4%) | +0.0000 | +0.018 | `CHECKED` |
| Pack slid ±0.03 m | 0.036 … 0.052 | | | `CHECKED` |
| Pack 503 / 680 g at the same station | 0.046 / 0.040 | | | `UNVERIFIED` |
| No pack (handling) | 0.071 (22.2%) | +0.0000 | +0.008 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.044 m | -0.034 / -0.034 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | +0 | mm | `CALC-A3-CG` |
| or the whole pod group (763 g: pod, power, avionics) by | +0 | mm | `CALC-A3-CG` |
| or the motor stations (everything ahead of the LE, 74 g) by | -1 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 284 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.26 / 0.36 / 0.03 | mm/mm | `CALC-A3-CG` |
| Pack fore face to pod nose (outside skin) at the nominal station | 1 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.194 | — | `CL-A3-HOVER-SPLIT` |
| CG height above the feet in the stance | 0.321 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1596 | 0.0426 | 0.1541 | -0.0024 | kg·m² |
| Radius of gyration | 0.273 | 0.141 | 0.268 | | m |



## Items (one row per instance)

| Id | Subsystem | Discipline | Mass g | x m | y m | z m | Maturity | Growth % | Source |
|---|---|---|---|---|---|---|---|---|---|
| `WNG-E01` | wing | structure | 221.4 | +0.134 | +0.000 | +0.000 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `WNG-E02` | wing | structure | 48.8 | +0.160 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E03` | wing | structure | 102.0 | +0.080 | +0.000 | +0.007 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `WNG-E04` | wing | structure | 15.0 | +0.080 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `WNG-E05` | wing | structure | 5.0 | +0.160 | +0.000 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E01` | fins | structure | 41.8 | +0.182 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E01` | fins | structure | 41.8 | +0.182 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E02` | fins | structure | 42.8 | +0.045 | +0.320 | +0.000 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `FIN-E02` | fins | structure | 42.8 | +0.045 | -0.320 | +0.000 | CALC | 10 | `redesign/team/A3/mass_model.csv` |
| `FIN-E03` | fins | structure | 18.0 | +0.040 | +0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E03` | fins | structure | 18.0 | +0.040 | -0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E03` | fins | structure | 18.0 | +0.040 | +0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E03` | fins | structure | 18.0 | +0.040 | -0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E04` | fins | structure | 20.0 | +0.062 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E04` | fins | structure | 20.0 | +0.062 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E05` | fins | structure | 30.0 | +0.065 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E05` | fins | structure | 30.0 | +0.065 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E06` | fins | structure | 14.0 | +0.182 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `FIN-E06` | fins | structure | 14.0 | +0.182 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `POD-E01` | pod | structure | 70.0 | -0.005 | +0.000 | +0.050 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `POD-E02` | pod | structure | 20.0 | -0.034 | +0.000 | +0.085 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `POD-E03` | pod | structure | 8.0 | +0.065 | +0.000 | +0.115 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `POD-E04` | pod | structure | 4.0 | -0.105 | +0.000 | +0.050 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E01` | landing | structure | 6.0 | +0.343 | +0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E01` | landing | structure | 6.0 | +0.343 | -0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E01` | landing | structure | 6.0 | +0.343 | +0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `GER-E01` | landing | structure | 6.0 | +0.343 | -0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-E01` | propulsion | propulsion | 81.0 | +0.021 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E01` | propulsion | propulsion | 81.0 | +0.021 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E01` | propulsion | propulsion | 81.0 | +0.021 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E01` | propulsion | propulsion | 81.0 | +0.021 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E02` | propulsion | propulsion | 17.0 | -0.005 | +0.320 | +0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E02` | propulsion | propulsion | 17.0 | -0.005 | -0.320 | +0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E02` | propulsion | propulsion | 17.0 | -0.005 | +0.320 | -0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E02` | propulsion | propulsion | 17.0 | -0.005 | -0.320 | -0.190 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E03` | propulsion | propulsion | 5.0 | +0.000 | +0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-E03` | propulsion | propulsion | 5.0 | +0.000 | -0.320 | +0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-E03` | propulsion | propulsion | 5.0 | +0.000 | +0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-E03` | propulsion | propulsion | 5.0 | +0.000 | -0.320 | -0.190 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PRP-E04` | propulsion | propulsion | 6.6 | +0.085 | +0.320 | +0.114 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E04` | propulsion | propulsion | 6.6 | +0.085 | -0.320 | +0.114 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E04` | propulsion | propulsion | 6.6 | +0.085 | +0.320 | -0.114 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PRP-E04` | propulsion | propulsion | 6.6 | +0.085 | -0.320 | -0.114 | DATASHEET | 5 | `redesign/team/A3/mass_model.csv` |
| `PWR-E01` | power | energy | 550.0 | -0.034 | +0.000 | +0.043 | DATASHEET | 24 | `redesign/team/A3/mass_model.csv` |
| `PWR-E02` | power | electrical | 10.0 | -0.075 | +0.000 | +0.040 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PWR-E03` | power | electrical | 25.0 | -0.025 | +0.000 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `PWR-E04` | power | electrical | 10.0 | +0.015 | +0.000 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E01` | avionics | avionics | 25.0 | +0.035 | +0.000 | +0.035 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E02` | avionics | avionics | 12.0 | +0.065 | +0.000 | +0.145 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E03` | avionics | avionics | 3.0 | +0.015 | +0.000 | +0.040 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E04` | avionics | avionics | 6.0 | -0.075 | +0.000 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E05` | avionics | avionics | 12.0 | -0.145 | +0.000 | +0.050 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `AVN-E06` | avionics | avionics | 8.0 | +0.035 | +0.000 | +0.030 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 14.0 | +0.030 | +0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 14.0 | +0.030 | -0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 14.0 | +0.030 | +0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E01` | harness | electrical | 14.0 | +0.030 | -0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.060 | +0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.060 | -0.160 | +0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.060 | +0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E02` | harness | electrical | 1.5 | +0.060 | -0.160 | -0.057 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | +0.320 | +0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | -0.320 | +0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | +0.320 | -0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E03` | harness | electrical | 4.0 | +0.055 | -0.320 | -0.152 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E04` | harness | electrical | 5.0 | +0.192 | +0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E04` | harness | electrical | 5.0 | +0.192 | -0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E05` | harness | electrical | 6.0 | -0.005 | +0.000 | +0.040 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E06` | harness | electrical | 5.0 | +0.000 | +0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `HRN-E06` | harness | electrical | 5.0 | +0.000 | -0.160 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E01` | mechanisms | controls | 12.0 | +0.202 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E01` | mechanisms | controls | 12.0 | +0.202 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E02` | mechanisms | controls | 1.5 | +0.285 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E03` | mechanisms | controls | 3.0 | +0.226 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E03` | mechanisms | controls | 3.0 | +0.226 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E04` | mechanisms | controls | 3.0 | +0.285 | +0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E04` | mechanisms | controls | 3.0 | +0.285 | -0.320 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E05` | mechanisms | controls | 4.0 | +0.250 | +0.315 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E05` | mechanisms | controls | 4.0 | +0.250 | -0.315 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E06` | mechanisms | controls | 2.0 | +0.202 | +0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
| `MEC-E06` | mechanisms | controls | 2.0 | +0.202 | -0.300 | +0.000 | EST | 20 | `redesign/team/A3/mass_model.csv` |
