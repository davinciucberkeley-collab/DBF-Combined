# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision **A1-R6** (D-95 … D-98,
2026-11-13) over roll-up revision **A3-R8** (same day). Every number in the generated block comes from
`python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in
`team/A3/rollup/ROLLUP.md`). The block between the markers is regenerated on each run; the rest is hand-written and
follows `params/CHANGE-LOG.md`. **All nine flying subsystems come from the designers' `parts.csv`**, plus one A3
adder: `HRN-A3-ROUTED` 13.81 g, the part of F2's routed harness (`CL-F2-MASS` 140.85 g) that the published harness
`parts.csv` lumps (127.04 g) do not carry yet. It retires itself when F2 republishes. Allocations D-95
(2 374 + 226 g). Pack cases D-64 (546 / 551 / 590 g). The pack acceptance line is one number, D-95.

## Verdict (A3-R8, 2026-11-13)

| Check | Result (A3-R8) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic **2 366 g**, predicted **2 489 g** (growth 122.7 g) | `CL-A3-MASS-BASIC`, `-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun: 546 / 550 g pack | +115 / **+111** g | `CL-A3-GATE-MARGIN-546`, `CL-A3-GATE-MARGIN` | `MODELLED` |
| **Pack acceptance line, one number** (heaviest weighed pack the overrun still covers) | **560.8 g**. A1 = A3 = E2. **`T-E2-WEIGH` pass line: ≤ 560 g.** The SKU maximum (551 + 5 g) has 4.8 g margin | `CL-A3-PACK-ACCEPT` = `CL-A1-PACK-ACCEPT` = `CL-E2-PACK-ACCEPT-KG` → `R-PACK-MASS` | `MODELLED` (thin) |
| 590 g pack | +71 g. This is the heavy bounding case for CG stations and load cases only. A 590 g pack is rejected at weigh-in | `CL-A3-GATE-MARGIN-590` (no limit since D-95) | information |
| A1 reserve | 226 g = growth allowance 123 g + overrun 100 g + **3 g free** | `CL-A1-RESERVE-COVERS` 3 g, `CL-A1-GROWTH-COVERS` +0.3 g | `MODELLED` |
| Worst subsystem vs D-95 allocation | propulsion 462.0 / 462 (1.000); harness 140.8 / 142, power 625.5 / 627, wing 391.8 / 393 | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `MODELLED` (on the line) |
| CG x, 550 g pack at the D-77 datum −0.036 | **0.0489 m** (15.3 % c); predicted 0.0504 m | `CL-A3-CG-X-RANGE`, `CL-A3-CG-X-PRED` → `R-CG-RANGE` | `MODELLED` |
| Each flight pack at its **D-98 mid-band station** | worst range use 0.66. 546 g: aft margin **+0.8 mm** predicted (held by the forward end of the travel) | `CL-A3-CG-X-STATIONS` → `R-CG-RANGE` | `MODELLED` (thin) |
| CG height (A1 copies to `cg.z_target_m`) | **+0.0184 m** basic, +0.0180 predicted; range use 0.64 of **[0.0165, 0.025]** (D-96) | `CL-A3-CG-Z`, `-CG-Z-PRED`, `-CG-Z-RANGE` | `MODELLED` |
| Lateral CG ≤ 5 mm | −1.5 mm | `CL-A3-CG-Y` | `MODELLED` |
| Hover pitch-trim split ≤ 1.25 | 1.21 (+3 %) | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` | `MODELLED` (thin) |
| Inertia about the CG | Ixx 0.1775, Iyy 0.0474, Izz 0.1738 kg·m² | `CL-A3-IXX/IYY/IZZ` | `MODELLED` |

**What D-95 found and fixed.** Two things made "0 g free" and the disputed acceptance line:

1. **The roll-up was stale.** It still carried the pre-D-87 parts lists: harness 117.7 g instead of the published
   127.0 g, power bus bars 7.3 g instead of 8.8 g, and mechanisms 70.9 g instead of 72.0 g. On top of that, F2's
   routed harness is 140.85 g, not 127.0 g. Together this is +25.7 g basic and +32 g predicted. The gate margin falls
   from 143 g to 111 g.
2. **Two acceptance lines.** A1's `CALC-A1-PACK-ACCEPT` still subtracted the R5 additions (`ASM-A1-R5-ADDED-G`
   21.4 g) that A3 already carries (D2-R6/R7, D3-R5, D5-R7 delivered). This gave 571.5 g against A3's 592.9 g. The
   assumption is now 0, so both claims read 560.8 g.

The free reserve is made by carrying growth once. Each allocation is now the delivered basic mass plus about 1 g.
The growth allowance is A3's live growth by maturity, rounded up to 123 g, and `CL-A1-GROWTH-COVERS` checks it. The
cushions that sat inside the wing (12 g) and avionics (8.5 g) allocations returned to the reserve. So did the 4.7 g
held in fins for C6's collar (CR-C6-37, H7). Harness and power took what they had grown by.

Per-pack stations (D-98, live roll-up):

| Pack | D-98 station x (m) | Spacers | CG basic → predicted (m) | Margin fwd / aft (mm) | Status |
|---|---|---|---|---|---|
| 546 g (listing minimum) | −0.036 (most forward whole step) | 16 mm | 0.0490 → 0.0506 | +2.4 / **+0.8** | `MODELLED` (thin) |
| 551 g (listed) | −0.036 (most forward whole step) | 16 mm | 0.0488 → 0.0504 | +2.2 / +1.0 | `MODELLED` |
| 590 g (heavy bounding case) | −0.032 | 12 mm | 0.0484 → 0.0500 | +1.8 / +1.4 | `MODELLED` |

**D-98 settles one station rule (H8): A1's mid-band rule.** Before weighing, each pack flies at the whole spacer step
that centres its basic-to-predicted CG band in the range. After `T-A3-CG-BALANCE`, the measured CG replaces both
figures, and the flight card uses the step nearest 0.0490 m. The 546 g and 551 g packs already sit on the most
forward whole step (−0.036; −0.038 would cut C5's crush block, D-77). Their aft margin with all growth realised is
therefore 0.8–1.0 mm, set by the bay and not by the rule. If the balance test reads aft of 0.0514 m, D-59's nose
ballast applies: ≤ 10 g, from the 10.8 g of predicted gate margin above the overrun. 10 g at the nose moves the CG
about 0.7 mm forward (estimate: 10 g × 0.19 m / 2 600 g).

## Adopted allocations (CHANGE-LOG D-95; was D-79, D-78, D-63)

Every allocation is the designer's delivered `parts.csv` (as A3 rolls it up) plus about 1 g. Growth by maturity is
carried once, in the growth allowance.

| Subsystem | Allocation g | Basis (source claim) | Was |
|---|---|---|---|
| wing | 393 | D1 `CL-D1-WING-MASS` 391.8 g, A3 391.8 g (C2 389.4 g); XPS density and tape spread sit in the 20 % / 10 % growth (predicted 411.4 g) | 405 |
| fins | 434 | D3 `CL-D3-MASS` 433.3 g. C6's 22 mm collar (+4.4 g, H7) is released from the free reserve by change request if the structures decision takes it | 438 |
| pod | 146 | D2 `CL-D2-MASS` 145.4 g | 146 |
| landing | 60 | D5-R7 `CL-D5-MASS-TOTAL` 59.1 g (D-76) | 60 |
| propulsion | 462 | E1 `CL-E1-MASS-PRP` 462.0 g (ESCs stripped, D-48) | 462 |
| power | 627 | A3 roll-up of power `parts.csv` 625.5 g (pack 550 g; D-87 bars 8.8 g). F1's `CL-PWR-MASS` 623.9 g predates the bars | 630 |
| avionics | 37 | F3 `CL-F3-MASS` 36.5 g CAD | 45 |
| harness | 142 | F2 `CL-F2-MASS` 140.85 g routed (D-85…D-89; A3 adder `HRN-A3-ROUTED`). −13.6 g if the factory phase leads reach (`T-E1-MOTOR-RM`) | 129 |
| mechanisms | 73 | A3 roll-up of mechanisms `parts.csv` 72.0 g (D6 `CL-D6-MASS` 71.3 g) | 72 |
| **sum / A1 reserve / gate** | **2 374 / 226 / 2 600** | reserve = growth allowance 123 g (A3 growth 122.7 g) + 100 g overrun + **3 g free** | 2 387 / 213 |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 597 g = allocations 2 374 + 123 g growth + 100 g overrun, 3 g free (D-95) | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 0 %: the Ovonic 120C EC5 listing 551 ± 5 g and the bounding cases (D-64: 546 / 551 / 590 g, 590 g for CG and loads only); the acceptance line is `CL-A3-PACK-ACCEPT` 560.8 g, one number (D-95; pass line 560 g); the 503 / 680 g listings are retired | `ASM-A1-PACK-CASES-G`, `ASM-A3-PACK-RANGE` [546, 590], `ASM-A3-PACK-NOMINAL`, `CL-A3-PACK-ACCEPT` |
| First-build overrun to keep free under the gate | 100 g | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.0490 m / 0.0466–0.0514 m (14.6–16.1 % chord), `UNVERIFIED` (B3 V1 on the CAD fins with the CG 18.5 mm above the chord plane; D-62) | `params.json#cg` |
| Pack nominal centroid and flight stations | datum x −0.032 m (D-62; was −0.022, D-47; −0.001, D-24); aft travel 12 mm to the no-spacer station −0.020, 2 mm spacer steps, forward limit −0.0379 for the 135 mm pack (D-64); flight stations computed live by `CALC-A3-CG` on the day of the balance test (CR-A3-27); A3-R7: 546 g −0.032, 551 g −0.030, 590 g −0.026 | `params.json#pod.pack_x_nominal_m`, `pod.pack_aft_travel_m`, `pod.pack_spacer_step_m`, `ASM-A3-PACK-STATIONS`, `CL-A3-CG-X-STATIONS`, `CALC-A1-PACK-CASES` |
| Room the pod nose needs ahead of the pack | 34.6 mm with the 1 mm epoxy bed at the nose wall (stop at −0.1312, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0379 m (135 mm pack) | `ASM-A3-NOSE-STACK` (D2-R6: stop face −0.1312) |
| CG range z, lateral | +0.0165 … +0.025 m (D-96, H9; was +0.010; target +0.0185; each 10 mm costs 1.85 mm of aft limit and 0.27 s of spiral t2, D-62); \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv, redesign/team/A3/mass_model.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 393 | 392 | 411 | -1 | `PROPOSED` |
| fins | 434 | 433 | 455 | -1 | `PROPOSED` |
| pod | 146 | 145 | 153 | -1 | `PROPOSED` |
| landing | 60 | 59 | 65 | -1 | `PROPOSED` |
| propulsion | 462 | 462 | 490 | +0 | `PROPOSED` |
| power | 627 | 626 | 636 | -2 | `PROPOSED` |
| avionics | 37 | 36 | 39 | -0 | `PROPOSED` |
| harness | 142 | 141 | 159 | -1 | `PROPOSED` |
| mechanisms | 73 | 72 | 81 | -1 | `PROPOSED` |
| **total** | **2 600** | **2 367** | **2 490** | allocated 2 374 + growth 226 | gate margin +110 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| listing minimum (D-64) | 546 | 2 486 | +114 | 100 | `CL-A3-GATE-MARGIN-546` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 490 | +110 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| listed (D-64) | 551 | 2 491 | +109 | 100 | `CALC-A3-MASS` | `MODELLED` |
| heavy bounding case, above the acceptance line (D-95) | 590 | 2 530 | +70 | 100 | `CL-A3-GATE-MARGIN-590` | rejected at `T-E2-WEIGH` |

Pack acceptance (heaviest weighed pack that leaves the 100 g overrun under the gate): **560.4 g** (`CL-A3-PACK-ACCEPT`; SKU listing maximum 556 g, margin +4.4 g).

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 1 030 | 1 084 | 44 % |
| propulsion | 462 | 490 | 20 % |
| energy | 550 | 550 | 23 % |
| electrical | 217 | 246 | 9 % |
| avionics | 36 | 39 | 2 % |
| controls | 72 | 81 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.047–0.051 (15%–16%) | ±0.005 | +0.017…+0.025 | `PROPOSED` |
| Take-off, basic | 0.049 (15.3%) | -0.0015 | +0.018 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.050 (15.8%) | -0.0017 | +0.018 | `CHECKED` |
| Pack slid -1.9 … +16.0 mm (spacers, crush stack) | 0.0484 … 0.0526 | | | — |
| Pack 546 g: nominal station → slid +0.0 mm (+ aft) | 0.0490 → 0.0490 | | | `CHECKED` |
| Pack 551 g: nominal station → slid +0.0 mm (+ aft) | 0.0488 → 0.0488 | | | `CHECKED` |
| Pack 590 g: nominal station → slid +0.0 mm (+ aft) | 0.0475 → 0.0475 | | | `CHECKED` |
| Pack 546 g at its D-98 station x -0.0360 (spacers 16 mm, clamped): basic → predicted | 0.0490 → 0.0506 (fwd +2.4 / aft +0.8 mm) | | | `CHECKED` |
| Pack 551 g at its D-98 station x -0.0360 (spacers 16 mm, clamped): basic → predicted | 0.0488 → 0.0504 (fwd +2.2 / aft +1.0 mm) | | | `CHECKED` |
| Pack 590 g at its D-98 station x -0.0320 (spacers 12 mm): basic → predicted | 0.0484 → 0.0500 (fwd +1.8 / aft +1.4 mm) | | | `CHECKED` |
| No pack (handling) | 0.075 (23.3%) | -0.0020 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.049 m | -0.036 / -0.035 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | +1 | mm | `CALC-A3-CG` |
| or the whole pod group (807 g: pod, power, avionics) by | +0 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 462 g) by | +1 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 288 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.23 / 0.34 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 2 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.214 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 546–590 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0379 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.05 / 0.66 / 0.60 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| CG height z: basic / predicted (A1 copies to `cg.z_target_m`) | 0.0184 / 0.0180 | m | `CL-A3-CG-Z` / `CL-A3-CG-Z-PRED` |
| CG z range use (worst of basic, predicted) | 0.64 | — | `CL-A3-CG-Z-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.30 (-1.5 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.319 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1775 | 0.0474 | 0.1739 | -0.0026 | kg·m² |
| Radius of gyration | 0.274 | 0.142 | 0.271 | | m |

Groups for C1's loads model (`CL-A3-GROUPS`; inertia about each group's own centroid, aircraft axes; closure to the aircraft inertia 3.1e-16, `CL-A3-GROUPS-CLOSURE`):

| Group | Station | Items | Mass g | x m | y m | z m | Ixx own | Iyy own | Izz own | Ixz own |
|---|---|---|---|---|---|---|---|---|---|---|
| **pack** | all | 1 | 550.0 | -0.0360 | +0.0000 | +0.0478 | 0.00021 | 0.00095 | 0.00093 | -0.00000 |
| **centre** | all | 29 | 300.6 | -0.0012 | -0.0126 | +0.0460 | 0.00088 | 0.00126 | 0.00157 | +0.00018 |
| **wing** | all | 15 | 391.8 | +0.1136 | +0.0005 | +0.0054 | 0.03991 | 0.00272 | 0.04258 | -0.00002 |
| wing | C | 4 | 352.9 | +0.1093 | +0.0000 | +0.0055 | 0.03605 | 0.00229 | 0.03830 | -0.00001 |
| wing | L | 5 | 19.2 | +0.1531 | -0.3012 | +0.0042 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| wing | R | 6 | 19.7 | +0.1534 | +0.3034 | +0.0045 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| **fins** | all | 46 | 385.2 | +0.1067 | +0.0000 | +0.0024 | 0.04258 | 0.00665 | 0.04070 | +0.00000 |
| fins | L | 5 | 87.8 | +0.0552 | -0.3146 | +0.0040 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | LL | 9 | 52.4 | +0.1483 | -0.3152 | -0.1141 | 0.00021 | 0.00057 | 0.00038 | +0.00008 |
| fins | LR | 9 | 52.4 | +0.1483 | +0.3152 | -0.1141 | 0.00021 | 0.00057 | 0.00038 | +0.00008 |
| fins | R | 5 | 87.8 | +0.0552 | +0.3146 | +0.0040 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | UL | 9 | 52.4 | +0.1512 | -0.3152 | +0.1160 | 0.00021 | 0.00058 | 0.00040 | -0.00008 |
| fins | UR | 9 | 52.4 | +0.1512 | +0.3152 | +0.1160 | 0.00021 | 0.00058 | 0.00040 | -0.00008 |
| **stations** | all | 44 | 518.9 | +0.0178 | +0.0000 | +0.0000 | 0.07152 | 0.01783 | 0.05480 | -0.00000 |
| stations | LL | 11 | 129.7 | +0.0178 | -0.3219 | -0.1811 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | LR | 11 | 129.7 | +0.0178 | +0.3219 | -0.1811 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | UL | 11 | 129.7 | +0.0178 | -0.3219 | +0.1811 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| stations | UR | 11 | 129.7 | +0.0178 | +0.3219 | +0.1811 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| **landing** | all | 18 | 59.1 | +0.3115 | +0.0000 | +0.0003 | 0.00887 | 0.00252 | 0.00640 | +0.00000 |
| landing | L | 1 | 0.7 | +0.3105 | -0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | LL | 4 | 14.4 | +0.3115 | -0.3200 | -0.2079 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | LR | 4 | 14.4 | +0.3115 | +0.3200 | -0.2079 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | R | 1 | 0.7 | +0.3105 | +0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | UL | 4 | 14.4 | +0.3115 | -0.3200 | +0.2079 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| landing | UR | 4 | 14.4 | +0.3115 | +0.3200 | +0.2079 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| **mechanisms** | all | 26 | 72.1 | +0.2166 | +0.0000 | -0.0022 | 0.00622 | 0.00009 | 0.00630 | -0.00000 |
| mechanisms | L | 13 | 36.1 | +0.2166 | -0.2885 | -0.0022 | 0.00011 | 0.00004 | 0.00015 | -0.00000 |
| mechanisms | R | 13 | 36.1 | +0.2166 | +0.2885 | -0.0022 | 0.00011 | 0.00004 | 0.00015 | -0.00000 |
| **harness** | all | 2 | 89.1 | +0.0782 | +0.0000 | +0.0049 | 0.00620 | 0.00000 | 0.00620 | -0.00000 |
| harness | L | 1 | 44.6 | +0.0782 | -0.2638 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| harness | R | 1 | 44.6 | +0.0782 | +0.2638 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |

(own inertias in kg·m²)

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 374 g + reserve 226 g = 2 600 g).

A3 adders kept beside a designer's parts.csv (items the list does not carry yet): HRN-A3-ROUTED (harness, 13.8 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GND-001 (redesign/subsystems/ground/parts.csv, flight false): RC transmitter RadioMaster Pocket (Crush), internal ELRS 2.4 GHz FCC, with 2 x 18650 cells; GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 5/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, HRN-102, HRN-113, HRN-114, PWR-104, PWR-105, PWR-106, PWR-202.

Roll-up warnings:

- harness: parts.csv totals 127 g, A3 estimate 201 g: missing parts or masses?

<!-- rollup:end -->

## Axes

Aircraft frame (README): x aft from the wing root LE, y right, z up in cruise. In hover the nose points up:
**hover yaw is about x (Ixx), hover pitch about y (Iyy, the broadside-wind axis), hover roll about z (Izz)**.
Ixy and Iyz are zero by symmetry except for the off-centre pitot option.

## How the roll-up works

| Source (precedence) | What it gives | Rule |
|---|---|---|
| 1 `subsystems/<key>/parts.csv` + `interfaces.json` | designer's parts; position `cg_xyz_m` per instance; maturity from the designer's notes (`EST from CAD` → CAD, `EST from CALC` → CALC, `EST` → EST), else bought → DATASHEET, made and `MODELLED` → CAD, `VERIFIED` → WEIGHED; the pack 0 % | replaces the whole subsystem once it exists; `mass_g` is **per unit**, line = qty × mass_g; self-inertia box from the A3 model row naming the part (wing core, spar, skin, fin boards, tubes) |
| 2 `team/<role>/mass_estimate.csv` | a specialist's refinement before parts exist | same columns as `team/A3/mass_model.csv`; same `item_id` replaces the A3 row |
| 3 `team/A3/mass_model.csv` | A3 model, fallback only since A3-R5 (every subsystem has a parts.csv); supplies the self-inertia boxes and the >10 % missing-mass check | cells starting `=` are expressions of `P:` keys, so geometry follows `params.json` |
| A3 adder (`with_parts` = y) | an item a designer's parts.csv does not list yet (A3-R7: `GER-R5-SLEEVE`, C5's +5 g shoe fix, until D5-R5 lists it) | counted beside the parts.csv and listed in the block; dropped when parts.csv lists the same id, and **retires itself** (warning) when the subsystem total moves from the `if_sub_g` it was written against, so a delivered change is never counted twice |
| Position from the model (`part_ids`) | positions for parts with no `interfaces.json` node (none today; propulsion until E1 published its interfaces.json) | the A3 row's instances, repeated qty / n times |
| `team/A3/overrides.csv` | A3 corrections to a designer's position or maturity, each with a reason; a cell may be an `=P:` expression so it follows `params.json`; an optional `if_x_m` is the designer x it was written against, and the override **retires itself** (warning) once the designer moves the part. A3-R7: ESC mass `EST`; harness lumps CALC; the pack `PWR-001` and pitot boom `AVN-005` at the D-62 stations until F1 / F3 move their nodes (the six D2 bay overrides retired themselves when D2-R6 landed) | listed in the block; each has a change request to the owner |

Lines with zero mass (fasteners and consumables carried inside another part) are skipped; parts whose nodes say
`"flight": false`, and lines with no interface node whose notes say they do not fly (spare kits), are ground items. Allocations are read from `params.json` and checked
against `params/mass_budget.json`. Warnings are printed and listed in the block for: no position, a
parts.csv/interfaces.json mass mismatch, or a subsystem whose parts.csv is > 10 % lighter than the A3 estimate.
`--check` exits 1 when the stored roll-up no longer matches the files (use at each phase gate).

## Largest mass levers

| Lever | Δ mass | Owner | Status |
|---|---|---|---|
| Weigh the pack (Ovonic 120C EC5 551 ± 5 g vs 550 g carried; acceptance 560.8 g, D-95) | −4 … +6 g listed; up to +10.8 g accepted | E2 (D-64, T-E2-WEIGH) | `UNVERIFIED` |
| D3's fins levers: microlight fillet filler, block fill 0.55 → 0.45, mount cheeks 12 → 8 mm | −5.6 / −13.8 / −4 g | D3, C4 (D-63) | `PROPOSED` |
| ESC factory power leads removed (F2 solders its own 16 AWG leads to the pads) | −13.6 g, delivered (E1 `PRP-002` 7.6 g; propulsion 462.0 g) | E1 | taken |
| Inter-panel rod and frames (D6 re-work: 1/8 in pultruded CF rod) | delivered: mechanisms 70.7 g against 80 g (9.3 g under) | D6 | taken |
| Harness: factory phase leads reach (no extensions) | −12 g, returned to the reserve after `T-E1-MOTOR-RM` | F2, E1 | `UNVERIFIED` |
| Station collar 16 → 12 mm | −2.0 g delivered; the 15 mm root fillets weigh 30.6 g as bodies (D-48 booked 3 g), so fins went to 437 g (D-63); collar back to 13 mm for C6's RF (+0.6 g) | D3, C4, C6 | closed (D-63, D-70) |
| Tekko32 F4 45A AM32 ESCs instead of LANRC (+$60) | −21 g | E1, I1 | **rejected at R4** (reserve $313 vs the $309 crash, D-57) |
| Aluminium prop nuts | −4 g | E1 | `PROPOSED` |
| Brace strip 10 × 2 instead of 10 × 3 mm | taken (`FIN-009` is 10 × 2 mm in D3's parts.csv) | C4, D3 | closed |
| One foam-board layer per half-fin | ≈ −40 g | — | **rejected** (D-26: 14 % from cruise 2P) |
| 18 AWG ESC leads | ≈ −18 g | — | **rejected** (F1: 16.4 °C rise > 10 °C) |
| Drop the UBEC | −13 g | — | **rejected** (F3: FC servo BEC 4.5 A < 5.2 A needed) |
| Through-core block, feet | closed | C4, D5 | block MS +0.55 at 20 g class; feet 10.3 g each at 48 mm (D5-R4) |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-A3-WEIGH-PARTS` | 1 g scale on every bought part, the first core and the first fin; owner sets `VERIFIED` + `mass_g` | mass claims |
| `T-A3-CG-BALANCE` | two scales or knife edges under the wing at known x, ready to fly | CG x/z, pack station |
| `T-A3-SWING` | bifilar pendulum, two 1.5 m strings, each axis | Ixx, Iyy, Izz |
| `T-A1-WEIGH` | complete aircraft on a 5 kg scale | gate |
