# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision A1-R3 (D-24, D-38) over roll-up
revision **A3-R5** (integration check, 2026-11-09). Every number in the generated block comes from
`python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in `team/A3/rollup/ROLLUP.md`).
The block between the markers is regenerated on each run; the rest is hand-written and follows `params/CHANGE-LOG.md`
(D-24, D-38, D-18). **All nine flying subsystems now come from the designers' `parts.csv`**; A3's model is fallback only.

## Verdict

| Check | Result (A3-R5, pack at x −0.001 m, all nine parts.csv) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic 2 330 g, predicted 2 449 g (growth 119 g of the 276 g reserve) | `CL-A3-MASS-BASIC`, `CL-A3-MASS-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun, 550 g pack | +151 g | `CL-A3-GATE-MARGIN` | `MODELLED` (+51 %) |
| same, 680 g pack | +21 g: under the gate, but the 100 g overrun is not covered | `CL-A3-GATE-MARGIN-680` → `R-PACK-MASS` | `FAIL` |
| same, 503 g pack | +198 g | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| Worst subsystem vs allocation (`mass_budget.json`) | mechanisms 82.3 / 65 g (1.27); harness 122.6 / 105; power 638.2 / 620 (28 g power board moved in from avionics); fins 417.3 / 408; pod 128.1 / 122 g | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `FAIL` (CR-A3-20, -21) |
| **CG x in 0.050–0.055 m** | **0.0577 m (18.0 % c), 2.7 mm aft of the aft limit**; predicted 0.0590 m | `CL-A3-CG-X-RANGE` (2.07) → `R-CG-RANGE` | **`FAIL`** (CR-A3-22) |
| 503–680 g packs trimmable with the spacers | 503 g needs 17.6 mm forward, the crush stack leaves 3.4 mm | `CL-A3-PACK-TRIM` → `R-CG-RANGE` | `FAIL` (14.2 mm, CR-A3-22) |
| Lateral CG ≤ 5 mm | −1.1 mm | `CL-A3-CG-Y` → `R-CG-RANGE` | `MODELLED` |
| CG z in −0.02 … +0.03 m | +0.018 m | `CL-A3-CG-Z-RANGE` → `R-CG-RANGE` | `MODELLED` |
| Hover pitch-trim split ≤ 1.25 | 1.214 (+3 %) | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` | `MODELLED` (thin) |
| Inertia about the CG | Ixx 0.175, Iyy 0.042, Izz 0.165 kg·m² | `CL-A3-IXX/IYY/IZZ` | `MODELLED` |

**The CG is now outside the range.** The designers' parts lists moved it 3.3 mm aft of A3-R4 (0.0548 → 0.0577 m):
mechanisms +18 g at x 0.22 (D6: servos, 5 × 4 mm CF torque tubes, 1/8 in inter-panel rods, printed frames and horns),
the harness lumps at x 0.08 (F2: +10 g and its centroid 26 mm further aft), and the FC's 28 g power board moved out of
the forward avionics channel into power; the wing (D1) came in 15 g light but mostly ahead of the CG. The B3 re-run
(CR-B3-17, pending at A1) narrows the range slightly to 0.0495–0.0550 m, target 0.0522 m. CR-A3-15 (forward stop
6 mm forward) alone now gives 0.0554 m: no longer enough.

**A3 recommends (CR-A3-22): extend the pod nose shell 15 mm (`pod.x_le_m` −0.115 → −0.130), shorten the nose block
6 mm (CR-A3-15), and shift the whole pack bay (forward stop, crush block, spreader, spacers, aft stop) 21 mm forward, so
the pack's nominal centroid is x −0.022 m.** Then:

| Pack | CG basic → predicted (m) | Trim | In 0.0495–0.0550 m |
|---|---|---|---|
| 550 g (carried) | 0.0525 → 0.0540 | none | yes |
| 503 g | 0.0540 → 0.0555 | 2.3 mm forward of the 3.4 mm left | yes |
| 680 g | 0.0486 → 0.0502 | 8 mm spacer aft: 0.0508 basic | yes |

Cost: ≈ +3 g of nose shell; the aircraft is 15 mm longer in x (D7: box slack is 17 mm); the CG rises 5 mm in the
stance (C5: tip-over margin is +2 %). Alternative with no length change: none found. Moving the whole pod group 16 mm
gives the same CG but the pod's spar saddle (`POD-007`, x 0.080) cannot move with it.

**The gate holds with the carried 550 g pack** (+151 g, of which 100 g is the first-build overrun). A 680 g pack still
leaves the aircraft under the gate (2 579 g predicted) but eats 79 g of the overrun. Weighing the first pack (E2) settles
it; above 601 g the overrun is no longer covered (CR-A3-16).

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
| CG target / range x | 0.0526 m / 0.050–0.055 m (15.6–17.2 % chord), `UNVERIFIED`; B3's re-run at 7° cant and 0.21 m fins gives 0.0522 / 0.0495–0.0550 m (CR-B3-17, pending at A1) | `params.json#cg` |
| Pack nominal centroid | x −0.001 m today (D-24; 8 mm spacer flown); A3 asks for −0.022 m with the nose 15 mm longer and the bay 21 mm forward (CR-A3-22, includes CR-A3-15). Trim: spacers `POD-008` 0–22 mm behind the pack | `params.json#pod.x_le_m` note (D-24), `ASM-A3-PACK-SLIDE` |
| Room the pod nose needs ahead of the pack | 40.6 mm (nose block and stop to −0.1002, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0044 m | `ASM-A3-NOSE-STACK` |
| CG range z, lateral | −0.02 … +0.03 m; \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 387 | 407 | -18 | `PROPOSED` |
| fins | 408 | 417 | 438 | +9 | `FAIL` |
| pod | 122 | 128 | 134 | +6 | `FAIL` |
| landing | 43 | 42 | 47 | -0 | `PROPOSED` |
| propulsion | 476 | 476 | 506 | -0 | `PROPOSED` |
| power | 620 | 638 | 650 | +18 | `FAIL` |
| avionics | 80 | 36 | 39 | -44 | `PROPOSED` |
| harness | 105 | 123 | 135 | +18 | `FAIL` |
| mechanisms | 65 | 82 | 94 | +17 | `FAIL` |
| **total** | **2 600** | **2 330** | **2 449** | allocated 2 324 + growth 276 | gate margin +151 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| lightest listing | 503 | 2 402 | +198 | 100 | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 449 | +151 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| heaviest listing | 680 | 2 579 | +21 | 100 | `CL-A3-GATE-MARGIN-680` | `FAIL` |

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 975 | 1 026 | 42 % |
| propulsion | 476 | 506 | 20 % |
| energy | 550 | 550 | 24 % |
| electrical | 211 | 234 | 9 % |
| avionics | 36 | 39 | 2 % |
| controls | 82 | 94 | 4 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.050–0.055 (16%–17%) | ±0.005 | -0.020…+0.030 | `PROPOSED` |
| Take-off, basic | 0.058 (18.0%) | -0.0011 | +0.018 | `FAIL` |
| Take-off, predicted (growth pro rata) | 0.059 (18.4%) | -0.0013 | +0.018 | `FAIL` |
| Pack slid -3.4 … +8.0 mm (spacers, crush stack) | 0.0569 … 0.0596 | | | — |
| Pack 503 g: nominal station → slid -17.6 mm (+ aft) | 0.0589 → 0.0550 | | | `FAIL` |
| Pack 550 g: nominal station → slid -11.3 mm (+ aft) | 0.0577 → 0.0550 | | | `FAIL` |
| Pack 680 g: nominal station → slid +0.0 mm (+ aft) | 0.0546 → 0.0546 | | | `CHECKED` |
| No pack (handling) | 0.076 (23.7%) | -0.0015 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.053 m | -0.001 / -0.022 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | -21 | mm | `CALC-A3-CG` |
| or the whole pod group (803 g: pod, power, avionics) by | -15 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 476 g) by | -25 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 272 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.24 / 0.34 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 3 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.214 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 503–680 g beyond the trim travel | 14.2 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0044 | m | `CALC-A3-CG` |
| Lateral CG offset / allowed 5 mm | 0.22 (-1.1 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.310 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1746 | 0.0423 | 0.1654 | -0.0020 | kg·m² |
| Radius of gyration | 0.274 | 0.135 | 0.266 | | m |

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 324 g + reserve 276 g = 2 600 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 11.0 g with leads and heat-shrink is EST per E1 parts.csv notes (6.6 g bare board is the only datasheet number).

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 7/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-101, FIN-102, FIN-103, FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-102, HRN-103, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, PWR-101, PWR-102, PWR-103, PWR-104, PWR-105, PWR-106, PWR-202, PRP-005.

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
| A3 adder (`with_parts` = y) | an item a designer's parts.csv does not list yet (none today: D5-R4 lists the 48 mm feet, so `GER-E02` is retired) | counted beside the parts.csv and listed in the block; dropped when parts.csv lists the same id |
| Position from the model (`part_ids`) | positions for parts with no `interfaces.json` node (none today; propulsion until E1 published its interfaces.json) | the A3 row's instances, repeated qty / n times |
| `team/A3/overrides.csv` | A3 corrections to a designer's position or maturity, each with a reason (today: ESC mass `EST`; harness lumps CALC per F2's breakdown) | listed in the block; each has a change request to the owner |

Lines with zero mass (fasteners and consumables carried inside another part) are skipped; parts whose nodes say
`"flight": false`, and lines with no interface node whose notes say they do not fly (spare kits), are ground items. Allocations are read from `params.json` and checked
against `params/mass_budget.json`. Warnings are printed and listed in the block for: no position, a
parts.csv/interfaces.json mass mismatch, or a subsystem whose parts.csv is > 10 % lighter than the A3 estimate.
`--check` exits 1 when the stored roll-up no longer matches the files (use at each phase gate).

## Largest mass levers

| Lever | Δ mass | Owner | Status |
|---|---|---|---|
| Weigh the pack (503–680 g listings vs 550 g carried) | −47 … +130 g | E2 | `UNVERIFIED` |
| ESC factory power leads: F2 solders its own 16 AWG leads to the ESC pads, E1's 11.0 g ESC still carries the factory leads | ≈ −14 g `EST` (4 × (11.0 − 6.6 − 1 g signal lead)) | E1, F2 | `PROPOSED` (CR-A3-21) |
| Inter-panel rod 1/8 in music wire → 2 mm CF rod; review the 4 CF torque tubes | ≈ −7 … −15 g `EST`, aft (CG −0.6 mm) | D6 | `PROPOSED` (CR-A3-20) |
| Tekko32 F4 45A AM32 ESCs instead of LANRC (+$60) | −21 g | E1, I1 | `PROPOSED` (only if the reserve allows) |
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
