# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision **A1-R5** (D-61 … D-64) over
roll-up revision **A3-R7** (2026-11-10 15:15, answering CR-A1-64 and CR-C1-33). Every number in the generated block
comes from `python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in
`team/A3/rollup/ROLLUP.md`). The block between the markers is regenerated on each run; the rest is hand-written and
follows `params/CHANGE-LOG.md`. **All nine flying subsystems come from the designers' `parts.csv`**: D2-R6 pod in the
D-62 bay, D3-R5 fins (7.5 mm mount, 2.5 mm pins, 15 mm collar), E1 rev 8 stations (D-61 prop plane −0.0127), D1's
re-run wing; A3's model gives self-inertia boxes and two self-retiring stop-gaps only: the pack node at the D-62 datum
−0.032 until F1 moves `PWR-001` (and the pitot boom until F3 moves `AVN-005`), and C5's +5 g shoe fix until D5-R5
lists it. Allocations D-63 (2 386 + 214 g); pack cases D-64 (546 / 551 / 590 g).

## Verdict (A3-R7)

| Check | Result (A3-R7) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic **2 345 g**, predicted **2 462 g** (growth 116 g) | `CL-A3-MASS-BASIC`, `-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun: 546 / 550 / 590 g pack | +142 / **+138** / +98 g | `CL-A3-GATE-MARGIN-546`, `CL-A3-GATE-MARGIN`, `-590` | `MODELLED` / `MODELLED` / `FAIL` (−1.8 g) |
| Pack acceptance (heaviest weighed pack the overrun still covers) | **588.2 g** (A1 carried 592.6, rounded 590; CR-A3-32); SKU maximum 556 g has 32 g | `CL-A3-PACK-ACCEPT` → `R-PACK-MASS` | `MODELLED` |
| Worst subsystem vs D-63 allocation | propulsion 462.0 / 462 (1.000); pod 145.8 / 146, fins 435.9 / 437, landing 47.5 / 48 (with the 5 g adder), mechanisms 70.7 / 72; wing 391.7 / 405 | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `MODELLED` (on the line) |
| CG x, 550 g pack at the D-62 datum −0.032 | **0.0486 m** (15.2 % c), range use 0.15; predicted 0.0502 m (0.49) | `CL-A3-CG-X-RANGE`, `CL-A3-CG-X-PRED` → `R-CG-RANGE` | `MODELLED` |
| Each flight pack at its D-59 station in the D-62 bay, basic and predicted | worst range use 0.67 (551 g: aft margin 0.8 mm predicted) | `CL-A3-CG-X-STATIONS` → `R-CG-RANGE` | `MODELLED` (thin) |
| Pack slide beyond the bay travel; forward room at the datum | 0 mm; 5.9 mm (stack limit −0.0379) | `CL-A3-PACK-TRIM`, `CL-A3-PACK-FWD-ROOM` | `MODELLED` |
| CG height (A1 copies to `cg.z_target_m`) | **+0.0185 m** basic, +0.0182 predicted; range use 0.14 of [0.010, 0.025] | `CL-A3-CG-Z`, `-CG-Z-PRED`, `-CG-Z-RANGE` | `MODELLED` |
| Lateral CG ≤ 5 mm | −1.2 mm | `CL-A3-CG-Y` | `MODELLED` |
| Hover pitch-trim split ≤ 1.25 | 1.216 (+3 %) | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` | `MODELLED` (thin) |
| Inertia about the CG | Ixx 0.1744, Iyy 0.0460, Izz 0.1701, Ixz −0.0025 kg·m² | `CL-A3-IXX/IYY/IZZ` | `MODELLED` |
| Group centroids and own inertias for C1 (pack, centre, wing, fins, stations, landing, mechanisms, harness; per station) | table in the block; closes on the aircraft inertia to 6e-16 | `CL-A3-GROUPS`, `-GROUPS-CLOSURE` | `MODELLED` |

**D-61 and D-62 did what A1 estimated.** The bay 10 mm forward and the stacks 5 mm forward put the 550 g pack's CG at
0.0486 m on the −0.032 datum (A1's frame estimate: 0.0485 at −0.034), so the CG sits 2.0 mm inside the forward limit
and 2.8 mm inside the aft one before growth. Per-pack stations from the live roll-up (CR-A3-27):

| Pack | D-59 station x (m) | Spacers | CG basic → predicted (m) | Margin fwd / aft (mm) | Status |
|---|---|---|---|---|---|
| 546 g (listing minimum) | −0.032 (datum) | 12 mm | 0.0488 → 0.0503 | +2.2 / +1.1 | `MODELLED` |
| 551 g (listed) | −0.030 | 10 mm | 0.0491 → 0.0506 | +2.5 / **+0.8** | `MODELLED` (thin) |
| 590 g (acceptance bound) | −0.026 | 6 mm | 0.0488 → 0.0503 | +2.2 / +1.1 | `MODELLED` |

The D-59 rule puts the **basic** CG on the 0.0490 target, so growth (+1.5 mm) eats the aft side. One spacer step
forward (2 mm, 0.47 mm of CG) would balance the margins (551 g: +2.0 / +1.3 mm); A1's own rule targets the mid of
basic and predicted and gives that. The flight card should use one rule; A3 will switch to A1's on a decision.

**The gate holds with the carried 550 g pack** (+138 g predicted margin, 100 g of it the first-build overrun). Against
A3-R6a the basic mass rose 24 g: D2-R6 +14.9 g (C3's strut, flange, brackets, the D-62 nose), D1 +4.4 g, the 5 g
shoe adder, D3 −0.5 g. The acceptance line falls from A1's 592.6 to 588.2 g because those `EST` parts carry 20 %
growth (CR-A3-32). Still open: D5-R5 and F1's pack node (stop-gaps in the roll-up, self-retiring).

## Adopted allocations (CHANGE-LOG D-63; was D-48, D-38, D-07)

Every allocation is the designer's delivered `parts.csv` plus the simulation-round structural fixes (D-63) and, where
A1 directed one, a reduction inside it.

| Subsystem | Allocation g | Basis (source claim) | Directed inside the allocation |
|---|---|---|---|
| wing | 405 | D1 CAD 387.3 g `EST` (`CL-D1-WING-MASS`: core 187, tape, spar 102, four plugs 22, elevons, label); the 17.7 g left is the cushion for XPS density and tape areal mass until `T-D1-WEIGH` | — |
| fins | 437 | D3-R4 434.8 g (`CL-D3-MASS`: two-layer 0.21 m half-fins, blocks, tubes 0.344, ASA mounts, 12 mm collars with the 40 mm tail, 10 × 2 braces, anchors, strips, pins, strap eyes, ESC pads, bonds, the 15 mm root fillets at 30.6 g as drawn) + C6's Ø 2.5 mm pins (+1.5) and 13 mm collar (+0.6) = 436.9 (D-63, D-70) | D3 returns what its levers give: microlight fillet filler −5.6, block 2 perimeters + 10 % gyroid −13.8 (if C4 keeps `CL-C4-D3-BLOCK-MS` ≥ 0), mount cheeks 12 → 8 mm −4 (if ≥ 1 100 N·m/rad); C4's shoe-cheek extension (+16 g) is not allocated, T-C4-FIN-PROOF decides |
| pod | 146 | D2-R5 130.9 g (`CL-D2-MASS`) + C3's FEA fixes (aft-stop strut 3.7, forward-stop flange 1.5, handle-foot brackets 8.7 g `EST`, D-69) + 2 g for the D-62 nose (0.235 m shell) = 145.8 | D2's lighter levers (0.8 mm floor, lead window) are void |
| landing | 48 | D5-R4 42.50 g `EST` (`CL-D5-MASS-TOTAL`: 4 feet 40.6 + 2 caps 1.45 + 48 mm) + 5 g `EST` for the shoe sleeve fix (wall 2.0, rim 3.0, 25 mm engagement, D-65; D5 reports the real figure); spares are ground items | — |
| propulsion | 462 | E1 475.6 g (`CL-E1-MASS-PRP`) less 4 × 3.4 g | ESCs carried stripped of their factory power leads (F2 solders its own, CR-F2-07): `PRP-002` 7.6 g, E1 re-runs |
| power | 648 | pack 550 (`UNVERIFIED`, 503–680) + non-pack 88.2 g (`CL-PWR-MASS-NONPACK`: AS150U pair, 10 AWG main path, power frame `PWR-006`, PDB plate, bus board, UBEC, fuse, four ESC caps, CoreWing power board `PWR-003` 28 g `EST`); F1 638.2 | — |
| avionics | 45 | F3 36.5 g CAD (`CL-F3-MASS`: FC 12 without its power board, GPS, RX, MS4525DO + boom, gel cubes, microSD) + 8.5 growth; 7 g returned to the reserve | F5's two 150 mm T-antennas (+0.5 g) inside it |
| harness | 123 | F2 routed 122.6 g (`CL-F2-MASS`: ESC leads 75.0 at 0.51–0.65 m, phase extensions 11.7 `EST`, signals/servo/GH 19.0, fittings 16.9 `EST`); CG x 0.067 m | 12 g return to the reserve if the factory phase leads reach (`T-E1-MOTOR-RM`) |
| mechanisms | 72 | D6-R2 70.68 g (`CL-D6-MASS`: Savox SH-0255MG+ 2 × 15.8, shortened inboard torque tubes, 1/8 in pultruded CF rod, trimmed horns and frames) + 1.3 g cushion until T-D6-WEIGH (D-63) | the D-48 "3/32 in rod" directive is withdrawn (CF rod: −6.6 g at 7.9 % loss) |
| **sum / A1 reserve / gate** | **2 386 / 214 / 2 600** | the reserve equals growth by maturity (114 g on the A3-R6a roll-up) plus the 100 g first-build overrun: 0 g free; the next release needs a lever | |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 600 g = allocations 2 386 + 114 g growth + 100 g overrun (D-63) | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 0 %: the Ovonic 120C EC5 listing 551 ± 5 g and the acceptance line are the bounding cases (D-64: 546 / 551 / 590 g; A3-R7 `CL-A3-PACK-ACCEPT` 588.2 g, CR-A3-32); the 503 / 680 g listings are retired | `ASM-A1-PACK-CASES-G`, `ASM-A3-PACK-RANGE` [546, 590], `ASM-A3-PACK-NOMINAL`, `CL-A3-PACK-ACCEPT` |
| First-build overrun to keep free under the gate | 100 g | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.0490 m / 0.0466–0.0514 m (14.6–16.1 % chord), `UNVERIFIED` (B3 V1 on the CAD fins with the CG 18.5 mm above the chord plane; D-62) | `params.json#cg` |
| Pack nominal centroid and flight stations | datum x −0.032 m (D-62; was −0.022, D-47; −0.001, D-24); aft travel 12 mm to the no-spacer station −0.020, 2 mm spacer steps, forward limit −0.0379 for the 135 mm pack (D-64); flight stations computed live by `CALC-A3-CG` on the day of the balance test (CR-A3-27); A3-R7: 546 g −0.032, 551 g −0.030, 590 g −0.026 | `params.json#pod.pack_x_nominal_m`, `pod.pack_aft_travel_m`, `pod.pack_spacer_step_m`, `ASM-A3-PACK-STATIONS`, `CL-A3-CG-X-STATIONS`, `CALC-A1-PACK-CASES` |
| Room the pod nose needs ahead of the pack | 34.6 mm with the 1 mm epoxy bed at the nose wall (stop at −0.1312, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0379 m (135 mm pack) | `ASM-A3-NOSE-STACK` (D2-R6: stop face −0.1312) |
| CG range z, lateral | +0.010 … +0.025 m (target +0.0185; each 10 mm costs 1.85 mm of aft limit and 0.27 s of spiral t2, D-62); \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 392 | 411 | -13 | `PROPOSED` |
| fins | 438 | 432 | 454 | -6 | `PROPOSED` |
| pod | 146 | 145 | 153 | -1 | `PROPOSED` |
| landing | 60 | 59 | 65 | -1 | `PROPOSED` |
| propulsion | 462 | 462 | 490 | +0 | `PROPOSED` |
| power | 630 | 626 | 636 | -4 | `PROPOSED` |
| avionics | 45 | 36 | 39 | -8 | `PROPOSED` |
| harness | 129 | 127 | 140 | -2 | `PROPOSED` |
| mechanisms | 72 | 72 | 81 | +0 | `PROPOSED` |
| **total** | **2 600** | **2 351** | **2 469** | allocated 2 387 + growth 213 | gate margin +131 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| listing minimum (D-64) | 546 | 2 465 | +135 | 100 | `CL-A3-GATE-MARGIN-546` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 469 | +131 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| listed (D-64) | 551 | 2 470 | +130 | 100 | `CALC-A3-MASS` | `MODELLED` |
| acceptance bound (D-64) | 590 | 2 509 | +91 | 100 | `CL-A3-GATE-MARGIN-590` | `FAIL` |

Pack acceptance (heaviest weighed pack that leaves the 100 g overrun under the gate): **581.4 g** (`CL-A3-PACK-ACCEPT`; SKU listing maximum 556 g, margin +25.4 g).

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 1 028 | 1 082 | 44 % |
| propulsion | 462 | 490 | 20 % |
| energy | 550 | 550 | 23 % |
| electrical | 202 | 226 | 9 % |
| avionics | 36 | 39 | 2 % |
| controls | 72 | 81 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.047–0.051 (15%–16%) | ±0.005 | +0.010…+0.025 | `PROPOSED` |
| Take-off, basic | 0.048 (15.1%) | -0.0016 | +0.018 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.050 (15.6%) | -0.0017 | +0.018 | `CHECKED` |
| Pack slid -1.9 … +16.0 mm (spacers, crush stack) | 0.0479 … 0.0520 | | | — |
| Pack 546 g: nominal station → slid +0.0 mm (+ aft) | 0.0484 → 0.0484 | | | `CHECKED` |
| Pack 551 g: nominal station → slid +0.0 mm (+ aft) | 0.0483 → 0.0483 | | | `CHECKED` |
| Pack 590 g: nominal station → slid +0.0 mm (+ aft) | 0.0469 → 0.0469 | | | `CHECKED` |
| Pack 546 g at its D-59 station x -0.0340 (spacers 14 mm): basic → predicted | 0.0489 → 0.0505 (fwd +2.3 / aft +0.9 mm) | | | `CHECKED` |
| Pack 551 g at its D-59 station x -0.0320 (spacers 12 mm): basic → predicted | 0.0492 → 0.0507 (fwd +2.6 / aft +0.7 mm) | | | `CHECKED` |
| Pack 590 g at its D-59 station x -0.0280 (spacers 8 mm): basic → predicted | 0.0489 → 0.0504 (fwd +2.3 / aft +1.0 mm) | | | `CHECKED` |
| No pack (handling) | 0.074 (23.1%) | -0.0020 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.049 m | -0.036 / -0.033 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | +3 | mm | `CALC-A3-CG` |
| or the whole pod group (807 g: pod, power, avionics) by | +2 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 462 g) by | +4 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 285 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.23 / 0.34 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 2 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.212 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 546–590 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0379 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.29 / 0.72 / 0.37 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| CG height z: basic / predicted (A1 copies to `cg.z_target_m`) | 0.0182 / 0.0178 | m | `CL-A3-CG-Z` / `CL-A3-CG-Z-PRED` |
| CG z range use (worst of basic, predicted) | 0.09 | — | `CL-A3-CG-Z-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.31 (-1.6 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.320 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1770 | 0.0472 | 0.1730 | -0.0026 | kg·m² |
| Radius of gyration | 0.274 | 0.142 | 0.271 | | m |

Groups for C1's loads model (`CL-A3-GROUPS`; inertia about each group's own centroid, aircraft axes; closure to the aircraft inertia 4.7e-16, `CL-A3-GROUPS-CLOSURE`):

| Group | Station | Items | Mass g | x m | y m | z m | Ixx own | Iyy own | Izz own | Ixz own |
|---|---|---|---|---|---|---|---|---|---|---|
| **pack** | all | 1 | 550.0 | -0.0360 | +0.0000 | +0.0478 | 0.00021 | 0.00095 | 0.00093 | -0.00000 |
| **centre** | all | 28 | 286.8 | -0.0036 | -0.0134 | +0.0462 | 0.00045 | 0.00118 | 0.00108 | +0.00018 |
| **wing** | all | 15 | 391.8 | +0.1136 | +0.0005 | +0.0054 | 0.03991 | 0.00272 | 0.04258 | -0.00002 |
| wing | C | 4 | 352.9 | +0.1093 | +0.0000 | +0.0055 | 0.03605 | 0.00229 | 0.03830 | -0.00001 |
| wing | L | 5 | 19.2 | +0.1531 | -0.3012 | +0.0042 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| wing | R | 6 | 19.7 | +0.1534 | +0.3034 | +0.0045 | 0.00015 | 0.00018 | 0.00033 | -0.00001 |
| **fins** | all | 46 | 380.5 | +0.1041 | +0.0000 | +0.0023 | 0.04208 | 0.00651 | 0.04012 | -0.00001 |
| fins | L | 5 | 87.8 | +0.0552 | -0.3146 | +0.0040 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | LL | 9 | 51.2 | +0.1449 | -0.3152 | -0.1172 | 0.00018 | 0.00053 | 0.00037 | +0.00006 |
| fins | LR | 9 | 51.2 | +0.1449 | +0.3152 | -0.1172 | 0.00018 | 0.00053 | 0.00037 | +0.00006 |
| fins | R | 5 | 87.8 | +0.0552 | +0.3146 | +0.0040 | 0.00039 | 0.00036 | 0.00005 | +0.00000 |
| fins | UL | 9 | 51.2 | +0.1472 | -0.3152 | +0.1187 | 0.00018 | 0.00054 | 0.00039 | -0.00007 |
| fins | UR | 9 | 51.2 | +0.1472 | +0.3152 | +0.1187 | 0.00018 | 0.00054 | 0.00039 | -0.00007 |
| **stations** | all | 44 | 522.4 | +0.0179 | +0.0000 | +0.0000 | 0.07195 | 0.01791 | 0.05516 | -0.00000 |
| stations | LL | 11 | 130.6 | +0.0179 | -0.3219 | -0.1809 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | LR | 11 | 130.6 | +0.0179 | +0.3219 | -0.1809 | 0.00018 | 0.00020 | 0.00026 | +0.00008 |
| stations | UL | 11 | 130.6 | +0.0179 | -0.3219 | +0.1809 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| stations | UR | 11 | 130.6 | +0.0179 | +0.3219 | +0.1809 | 0.00018 | 0.00020 | 0.00026 | -0.00008 |
| **landing** | all | 18 | 58.9 | +0.3108 | +0.0000 | +0.0003 | 0.00885 | 0.00252 | 0.00638 | +0.00000 |
| landing | L | 1 | 0.7 | +0.3105 | -0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | LL | 4 | 14.3 | +0.3108 | -0.3200 | -0.2082 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | LR | 4 | 14.3 | +0.3108 | +0.3200 | -0.2082 | 0.00000 | 0.00001 | 0.00001 | -0.00000 |
| landing | R | 1 | 0.7 | +0.3105 | +0.5690 | -0.0002 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| landing | UL | 4 | 14.4 | +0.3108 | -0.3200 | +0.2082 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| landing | UR | 4 | 14.4 | +0.3108 | +0.3200 | +0.2082 | 0.00000 | 0.00001 | 0.00001 | +0.00000 |
| **mechanisms** | all | 26 | 72.0 | +0.2167 | +0.0000 | -0.0022 | 0.00621 | 0.00009 | 0.00629 | -0.00000 |
| mechanisms | L | 13 | 36.0 | +0.2167 | -0.2885 | -0.0022 | 0.00011 | 0.00004 | 0.00015 | -0.00000 |
| mechanisms | R | 13 | 36.0 | +0.2167 | +0.2885 | -0.0022 | 0.00011 | 0.00004 | 0.00015 | -0.00000 |
| **harness** | all | 2 | 88.8 | +0.0782 | +0.0000 | +0.0049 | 0.00617 | 0.00000 | 0.00617 | -0.00000 |
| harness | L | 1 | 44.4 | +0.0782 | -0.2636 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |
| harness | R | 1 | 44.4 | +0.0782 | +0.2636 | +0.0049 | 0.00000 | 0.00000 | 0.00000 | -0.00000 |

(own inertias in kg·m²)

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 387 g + reserve 213 g = 2 600 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GND-001 (redesign/subsystems/ground/parts.csv, flight false): RC transmitter RadioMaster Pocket (Crush), internal ELRS 2.4 GHz FCC, with 2 x 18650 cells; GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 5/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, HRN-102, HRN-113, HRN-114, PWR-104, PWR-105, PWR-106, PWR-202.

Roll-up warnings:

- AVN-005: A3 override retired, the designer moved the part (x -0.1533, override written against -0.1433); drop the row from overrides.csv
- harness: parts.csv totals 127 g, A3 estimate 201 g: missing parts or masses?
- PWR-001: A3 override retired, the designer moved the part (x -0.0360, override written against -0.0220); drop the row from overrides.csv
- GER-R5-SLEEVE: A3 adder retired, landing/parts.csv republished (58.9 g, adder written against 42.5 g); check the new list carries it and drop the row

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
| Weigh the pack (Ovonic 120C EC5 551 ± 5 g vs 550 g carried; acceptance 588.2 g, CR-A3-32) | −4 … +6 g listed; up to +38 g accepted | E2 (D-64, T-E2-WEIGH) | `UNVERIFIED` |
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
