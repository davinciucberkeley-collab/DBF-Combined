# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision **A1-R6** (D-95 … D-98,
2026-11-13) over roll-up revision **A3-R8** (same day). Every number in the generated block comes from
`python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in
`team/A3/rollup/ROLLUP.md`). The block between the markers is regenerated on each run; the rest is hand-written and
follows `params/CHANGE-LOG.md`. **All nine flying subsystems come from the designers' `parts.csv`**, plus one A3
adder: `HRN-A3-ROUTED` 13.81 g, the part of F2's routed harness (`CL-F2-MASS` 140.85 g) that the published harness
`parts.csv` lumps (127.04 g) do not carry yet. It retires itself when F2 republishes. Allocations D-95
(2 374 + 226 g). Pack cases D-64 (546 / 551 / 590 g). The pack acceptance line is one number, D-95.

## CDR-12: structures contingency booked (D-132, S4, 2026-11-13)

The CDR board asked A1 to fund about **124 g** of asks against **3 g** free (`CDR-SUMMARY.md` CDR-12, `CHAIR EST`).
A1 booked **31 g** for structures and A3 carries it as three `EST` adders (`team/A3/mass_model.csv`
`FIN-A3-CDR-CHEEK` 16 g, `-DOUBLER` 6 g, `-BRACE` 9 g; they retire themselves when D3 / D5 republish the fins
`parts.csv`). To keep the 2 600 g gate, the unnamed first-build overrun gives up what the named items take.

| Key (`params.json`) | Was | Now | Why |
|---|---|---|---|
| `mass.allocation_g.fins` | 434 | **466** | fins `parts.csv` 434.94 g re-run + 31 g contingency |
| `requirements.growth_allowance_kg` | 0.123 | **0.130** | A3 growth 129.1 g with the adders at `EST` 20 % |
| `requirements.build_overrun_kg` | 0.100 | **0.064** | 2 600 − 2 406 − 130 |
| `mass.growth_reserve_g` | 226 | **194** | 130 + 64, **0 g free** (`CL-A1-RESERVE-COVERS` 0) |
| `requirements.mtow_sized_kg` | 2.597 | **2.600** | allocations 2 406 + 130 + 64 |

Result (A3 live roll-up, this run): basic **2 398 g**, predicted **2 528 g**, gate margin **+72 g** against the 64 g
overrun line; pack acceptance line **558.5 g** (`CL-A3-PACK-ACCEPT` = `CL-A1-PACK-ACCEPT`; was 560.8 g, so the
`T-E2-WEIGH` pass line moves from ≤ 560 to **≤ 558 g**; SKU maximum 556 g, margin +2.5 g).

**The asks, and what does not fit** (`EST` values from the reports, summed in `CDR-SUMMARY.md` CDR-12):

| Ask | g `EST` | Where it sits now |
|---|---|---|
| Cheek extension 16 + face doubler 6 + 10 × 3 brace 9 | 31 | **booked** (fins allocation, A3 adders) |
| First-flight nose ballast (B9) | 30 | inside the 64 g overrun; removed after `T-B3-TWIN-NP` |
| 11 × 7E props if the A/B picks them (4 × 6 g) | 24 | inside the 64 g overrun |
| Second ESC caps 8.8 + XT30U saddles 1.2 | 10 | inside the 64 g overrun |
| **Sum of the unbooked asks** | **64** | **= the whole 64 g overrun: 0 g left for real first-build overrun** |
| Solid 62 mm strip tail (D-90) | 29 | **does not fit.** Expected to retire under B1's 23 N cap; if the pad incline test fails (μ > 0.40) the tail needs a mass trade (D3 levers: fillet filler −5.6, block infill −13.8, cheeks 12 → 8 mm −4 g) |
| Any build overrun beyond the asks | — | **does not fit** if all four asks land together |

**CG corners** (from `team/A3/rollup/rollup.json` station cases, A3-R9 with the adders; added masses by
moment, x_ballast −0.130 m at the pod nose wall `EST`, x_prop −0.0127 m `params.json#propulsion.x_prop_plane_m`;
range `cg.x_range_m` 0.0466–0.0514 m):

| Corner | Mass g | x_cg m | Fwd / aft margin mm | Status |
|---|---|---|---|---|
| Tail-heavy: 546 g pack at −0.036, all growth (predicted), contingency in, no ballast | 2 524 | 0.05068 | +4.08 / **+0.72** | in range (thin) |
| Nose-heavy: 590 g pack at −0.034, basic, contingency in, 11 × 7E props | 2 462 | 0.04741 | **+0.81** / +3.99 | in range (thin) |
| First flight, B9: 551 g pack, basic, 30 g nose ballast | 2 429 | 0.04667 | **+0.07** / +4.73 | on the forward limit |
| First flight, B9: 546 g pack, basic, 30 g ballast, 11 × 7E props | 2 448 | 0.04626 | **−0.34** / +5.14 | **outside today's forward limit**; inside only once B3 re-derives it with `MIXING_GAIN` 0.65 (CDR-14, about 11.5 mm range `REVIEWER EST`) |

So the 30 g ballast and the 11 × 7E props cannot both be fitted at the same time on today's CG range; B3's
CDR-14 forward limit decides it.

**Live re-run later the same day (landing `parts.csv` changed by stream S1 during the fix round, not by S4):** the
landing subsystem now rolls up at **69.9 g** basic against its 60 g allocation (was 58.9 g; the shoe change of CDR-01
is in progress). With it and the 31 g contingency: predicted **2 540 g**, gate margin **+60 g against the 64 g
overrun line (`FAIL` by 4 g)**, pack acceptance **546.5 g** (below the 551 g listed pack: `FAIL`), and the 546 / 551 g
packs sit **0.42 / 0.24 mm aft of the 0.0514 m limit** with all growth realised (the generated block below). So
+11 g at the feet does **not fit** on top of the booked contingency. Whoever settles the landing mass (S1, D5) must
either recover it in landing or trade it against the 64 g overrun (and then the 30 g first-flight ballast no longer
fits either); A1 re-books when the landing `parts.csv` is final. The tables above are the run before that change.

## Verdict (A3-R8, 2026-11-13)

| Check | Result (A3-R8) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic **2 366 g**, predicted **2 489 g** (growth 122.7 g) | `CL-A3-MASS-BASIC`, `-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun: 546 / 550 g pack | +115 / **+111** g | `CL-A3-GATE-MARGIN-546`, `CL-A3-GATE-MARGIN` | `MODELLED` |
| **Pack acceptance line, one number** (heaviest weighed pack the overrun still covers) | **560.8 g**. A1 = A3 = E2. **`T-E2-WEIGH` pass line: ≤ 560 g.** The SKU maximum (551 + 5 g) has 4.8 g margin | `CL-A3-PACK-ACCEPT` = `CL-A1-PACK-ACCEPT` = `CL-E2-PACK-ACCEPT-KG` → `R-PACK-MASS` | `MODELLED` (thin) |
| 590 g pack | +71 g. This is the heavy bounding case for CG stations and load cases only. A 590 g pack is rejected at weigh-in | `CL-A3-GATE-MARGIN-590` (no limit since D-95) | information |
| A1 reserve | **D-132:** 194 g = growth allowance 130 g + overrun 64 g + **0 g free** (was 226 = 123 + 100 + 3) | `CL-A1-RESERVE-COVERS` 0 g, `CL-A1-GROWTH-COVERS` +0.9 g | `MODELLED` |
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
| fins | **466** (D-132) | fins `parts.csv` 434.94 g + 31 g structures contingency (CDR-12). Was 434: D3 `CL-D3-MASS` 433.3 g | 434 |
| pod | 146 | D2 `CL-D2-MASS` 145.4 g | 146 |
| landing | 60 | D5-R7 `CL-D5-MASS-TOTAL` 59.1 g (D-76) | 60 |
| propulsion | 462 | E1 `CL-E1-MASS-PRP` 462.0 g (ESCs stripped, D-48) | 462 |
| power | 627 | A3 roll-up of power `parts.csv` 625.5 g (pack 550 g; D-87 bars 8.8 g). F1's `CL-PWR-MASS` 623.9 g predates the bars | 630 |
| avionics | 37 | F3 `CL-F3-MASS` 36.5 g CAD | 45 |
| harness | 142 | F2 `CL-F2-MASS` 140.85 g routed (D-85…D-89; A3 adder `HRN-A3-ROUTED`). −13.6 g if the factory phase leads reach (`T-E1-MOTOR-RM`) | 129 |
| mechanisms | 73 | A3 roll-up of mechanisms `parts.csv` 72.0 g (D6 `CL-D6-MASS` 71.3 g) | 72 |
| **sum / A1 reserve / gate** | **2 406 / 194 / 2 600** (D-132) | reserve = growth allowance 130 g (A3 growth 129.1 g) + 64 g overrun + **0 g free** | 2 374 / 226 |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 597 g = allocations 2 374 + 123 g growth + 100 g overrun, 3 g free (D-95) | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 0 %: the Ovonic 120C EC5 listing 551 ± 5 g and the bounding cases (D-64: 546 / 551 / 590 g, 590 g for CG and loads only); the acceptance line is `CL-A3-PACK-ACCEPT` 560.8 g, one number (D-95; pass line 560 g); the 503 / 680 g listings are retired | `ASM-A1-PACK-CASES-G`, `ASM-A3-PACK-RANGE` [546, 590], `ASM-A3-PACK-NOMINAL`, `CL-A3-PACK-ACCEPT` |
| First-build overrun to keep free under the gate | 64 g (D-132; was 100 g) | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.0490 m / 0.0466–0.0514 m (14.6–16.1 % chord), `UNVERIFIED` (B3 V1 on the CAD fins with the CG 18.5 mm above the chord plane; D-62) | `params.json#cg` |
| Pack nominal centroid and flight stations | datum x −0.032 m (D-62; was −0.022, D-47; −0.001, D-24); aft travel 12 mm to the no-spacer station −0.020, 2 mm spacer steps, forward limit −0.0379 for the 135 mm pack (D-64); flight stations computed live by `CALC-A3-CG` on the day of the balance test (CR-A3-27); A3-R7: 546 g −0.032, 551 g −0.030, 590 g −0.026 | `params.json#pod.pack_x_nominal_m`, `pod.pack_aft_travel_m`, `pod.pack_spacer_step_m`, `ASM-A3-PACK-STATIONS`, `CL-A3-CG-X-STATIONS`, `CALC-A1-PACK-CASES` |
| Room the pod nose needs ahead of the pack | 34.6 mm with the 1 mm epoxy bed at the nose wall (stop at −0.1312, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0379 m (135 mm pack) | `ASM-A3-NOSE-STACK` (D2-R6: stop face −0.1312) |
| CG range z, lateral | +0.0165 … +0.025 m (D-96, H9; was +0.010; target +0.0185; each 10 mm costs 1.85 mm of aft limit and 0.27 s of spiral t2, D-62); \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

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
