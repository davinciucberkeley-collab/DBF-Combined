# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision A1-R3 (D-24, D-38) over roll-up
revision A3-R4, 2026-11-09 (CR-A1-25). Every number in the generated block comes from
`python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in `team/A3/rollup/ROLLUP.md`).
The block between the markers is regenerated on each run; the rest is hand-written and follows `params/CHANGE-LOG.md`
(D-24, D-38, D-18).

## Verdict

| Check | Result (A3-R4, pack at x −0.001 m, D2-R3 pod) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic 2 339 g, predicted 2 493 g (growth 154 g of the 170 g allowance) | `CL-A3-MASS-BASIC`, `CL-A3-MASS-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun, 550 g pack | +107 g | `CL-A3-GATE-MARGIN` | `MODELLED` (+7 %) |
| same, 680 g pack | −23 g: the gate itself is exceeded by 23 g | `CL-A3-GATE-MARGIN-680` → `R-PACK-MASS` | `FAIL` |
| same, 503 g pack | +154 g | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| Worst subsystem vs allocation (`mass_budget.json`) | harness 112.6 / 105 g (1.07); fins 417.0 / 408; pod 127.3 / 122 g | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `FAIL` (CR-A3-14) |
| CG x in 0.050–0.055 m | 0.0548 m (17.1 % c), 0.2 mm inside the aft limit; predicted (growth pro rata) 0.0570 m | `CL-A3-CG-X-RANGE` → `R-CG-RANGE` | `MODELLED` (thin) |
| 503–680 g packs trimmable with the spacers | 503 g needs 4.3 mm forward, the crush stack leaves 3.4 mm | `CL-A3-PACK-TRIM` → `R-CG-RANGE` | `FAIL` (0.9 mm, CR-A3-15) |
| Lateral CG ≤ 5 mm | −0.8 mm (pitot, airspeed, power on the left; FC on the right) | `CL-A3-CG-Y` → `R-CG-RANGE` | `MODELLED` |
| CG z in −0.02 … +0.03 m | +0.016 m | `CL-A3-CG-Z-RANGE` → `R-CG-RANGE` | `MODELLED` |
| Hover pitch-trim split ≤ 1.25 | 1.190 (+5 %) | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` | `MODELLED` |

**At the D-24 station the R3 aircraft sits at the aft edge of the range.** The designers' numbers added 194 g, mostly
aft of the old CG: feet +2.1 mm (42.6 g at x 0.33), fins +1.8 mm (two-layer 0.21 m half-fins, blocks, braces at
x 0.10), servos +0.5 mm, the pod handle and mast at x 0.08; F3's FC and pitot and D2-R3's forward stops and crush block
give some back. The CG is 0.0548 m with the 550 g pack, 0.0559 m with a 503 g pack, and 0.0570 m once the predicted
growth (mostly wing and fins, aft) arrives. The crush stack behind D2's forward stop (−0.1002) leaves only 3.4 mm of
forward travel. **A3 recommends moving the forward stop 6 mm forward (−0.1002 → −0.1062, nose block 14.8 → 8.8 mm)
and flying the pack against the crush stack at x −0.0104 m:** CG 0.0526 m (the target) with 550 g, 0.0539 m with
503 g, 0.0493 m with 680 g, which a 4 mm spacer trims to 0.0504 m; predicted growth then gives 0.0547 m, still inside.
That needs A1 to change D-24, D2 to re-lay the stop, and C5/C3 to accept the shorter nose block (CR-A3-15).

**The gate holds with the carried 550 g pack, by 7 g over the overrun.** Predicted 2 493 g leaves 107 g for the
100 g first-build overrun. A 680 g pack adds 130 g, so 2 623 g is above the gate before any overrun. Weighing the first
pack (E2, ~1 Dec) settles it; above 557 g the overrun is no longer covered (CR-A3-16).

## Adopted allocations (CHANGE-LOG D-38; was D-07)

| Subsystem | Allocation g | Basis (source claim) |
|---|---|---|
| wing | 405 | C2: core 202, tape 49, spar 102, slot fill 15, six spar plugs 30 = 397 g (`CL-C2-WING-MASS`), edge tape + label 5, 3 spare |
| fins | 408 | C4: D3 CAD 364.5 (blocks, tubes 0.344, ASA mounts, collars, braces, anchors, edge strips, ESC pads, bonds) + second layer 37.5 (`CL-C4-D3-FINS-MASS` 402) + ~6 for 0.21 m half-fins |
| pod | 122 | C3: D2 100.4 + stops and guides 9.5 (`CL-C3-POD-MASS-REC` 109.9) + 0.14 m width ~5 + crush block and nose extension ~2.5 + 4.5 spare |
| landing | 43 | D5: 4 × 9.78 g (shoe, piston, cartridge, pad) (`CL-D5-MASS-TOTAL` 39.1) + 0.85 g per foot for 48 mm |
| propulsion | 476 | E1: 4 × (motor 81.0 + ESC 11.0 + prop 17 + adapter, nut, washer 6.7 + screws 3.2) (`CL-E1-MASS-PRP` 475.6) |
| power | 620 | pack 550 (`UNVERIFIED`) + AS150U pair, 8 AWG 0.15 m, ESC caps, fuse, UBEC 13 = 69 (`CL-F1-POWER-MASS`) |
| avionics | 80 | F3: FC with power board 40, GPS, RX, MS4525DO + boom, gel pads, microSD = 78.5 (`CL-F3-MASS`) |
| harness | 105 | 4 × 0.5 m 16 AWG ESC pairs 64.6 (`CL-F1-ESC-MASS`), signal leads, bullets, servo leads, sensor cables, ties; F2 publishes `mass_estimate.csv` |
| mechanisms | 65 | 2 × 17–20 g servos (≥ 3.93 kgf·cm, CR-B2-10), horns, pushrods, links, hinge tape, covers |
| **sum / A1 reserve / gate** | **2 324 / 276 / 2 600** | the reserve must cover growth by maturity (A3 re-runs) and the 100 g first-build overrun |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 594 g is allocations + 170 g growth + 100 g overrun | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 0 %: the 503 / 550 / 680 g listings are bounding cases, each with its own gate margin | `ASM-A3-PACK-RANGE`, `CL-A3-GATE-MARGIN(-503/-680)` |
| First-build overrun to keep free under the gate | 100 g | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.0526 m / 0.050–0.055 m (15.6–17.2 % chord), `UNVERIFIED` until B3 re-runs at 7° cant and 0.21 m fins (D-24) | `params.json#cg` |
| Pack nominal centroid | x −0.001 m today (D-24; 8 mm spacer flown); A3 asks for −0.0104 m against the crush stack with the forward stop 6 mm forward (CR-A3-15). Trim: spacers `POD-008` 0–22 mm behind the pack | `params.json#pod.x_le_m` note (D-24), `ASM-A3-PACK-SLIDE` |
| Room the pod nose needs ahead of the pack | 40.6 mm (nose block and stop to −0.1002, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0044 m | `ASM-A3-NOSE-STACK` |
| CG range z, lateral | −0.02 … +0.03 m; \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

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

<!-- rollup:end -->

## Axes

Aircraft frame (README): x aft from the wing root LE, y right, z up in cruise. In hover the nose points up:
**hover yaw is about x (Ixx), hover pitch about y (Iyy, the broadside-wind axis), hover roll about z (Izz)**.
Ixy and Iyz are zero by symmetry except for the off-centre pitot option.

## How the roll-up works

| Source (precedence) | What it gives | Rule |
|---|---|---|
| 1 `subsystems/<key>/parts.csv` + `interfaces.json` | designer's parts; position `cg_xyz_m` per instance; status → maturity | replaces the whole subsystem once it exists; `mass_g` is **per unit**, line = qty × mass_g |
| 2 `team/<role>/mass_estimate.csv` | a specialist's refinement before parts exist | same columns as `team/A3/mass_model.csv`; same `item_id` replaces the A3 row |
| 3 `team/A3/mass_model.csv` | A3 model, 49 lines, now carrying the designers' numbers where no parts.csv exists (C2 wing, F1 power and ESC leads, F3 avionics) | cells starting `=` are expressions of `P:` keys, so geometry follows `params.json` |
| A3 adder (`with_parts` = y) | an item a designer's parts.csv does not list yet (today only the 48 mm feet, 3.4 g; D2-R3 and D3 now list the stops, crush block, second layer and 0.21 m outline themselves) | counted beside the parts.csv and listed in the block; dropped when parts.csv lists the same id |
| Position from the model (`part_ids`) | positions for parts with no `interfaces.json` node (none today; propulsion until E1 published its interfaces.json) | the A3 row's instances, repeated qty / n times |
| `team/A3/overrides.csv` | A3 corrections to a designer's position or maturity, each with a reason (today: ESC mass `EST`) | listed in the block; each has a change request to the owner |

Lines with zero mass (fasteners and consumables carried inside another part) are skipped; lines with no interface node
whose notes say they do not fly (spare kits) are ground items. Allocations are read from `params.json` and checked
against `params/mass_budget.json`. Warnings are printed and listed in the block for: no position, a
parts.csv/interfaces.json mass mismatch, or a subsystem whose parts.csv is > 10 % lighter than the A3 estimate.
`--check` exits 1 when the stored roll-up no longer matches the files (use at each phase gate).

## Largest mass levers

| Lever | Δ mass | Owner | Status |
|---|---|---|---|
| Weigh the pack (503–680 g listings vs 550 g carried) | −47 … +130 g | E2 | `UNVERIFIED` |
| Tekko32 F4 45A AM32 ESCs instead of LANRC (+$60) | −21 g | E1, I1 | `PROPOSED` (only if the reserve allows) |
| Aluminium prop nuts | −4 g | E1 | `PROPOSED` |
| Brace strip 10 × 2 instead of 10 × 3 mm | ≈ −10 g `EST` | C4, D3 | `PROPOSED` (CR-C4-16) |
| One foam-board layer per half-fin | ≈ −40 g | — | **rejected** (D-26: 14 % from cruise 2P) |
| 18 AWG ESC leads | ≈ −18 g | — | **rejected** (F1: 16.4 °C rise > 10 °C) |
| Drop the UBEC | −13 g | — | **rejected** (F3: FC servo BEC 4.5 A < 5.2 A needed) |
| Through-core block, feet | closed | C4, D5 | block MS +0.55 at 20 g class; feet 9.78 g each (D5) |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-A3-WEIGH-PARTS` | 1 g scale on every bought part, the first core and the first fin; owner sets `VERIFIED` + `mass_g` | mass claims |
| `T-A3-CG-BALANCE` | two scales or knife edges under the wing at known x, ready to fly | CG x/z, pack station |
| `T-A3-SWING` | bifilar pendulum, two 1.5 m strings, each axis | Ixx, Iyy, Izz |
| `T-A1-WEIGH` | complete aircraft on a 5 kg scale | gate |
