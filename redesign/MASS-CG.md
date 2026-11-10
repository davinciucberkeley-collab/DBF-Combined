# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, budget revision **A1-R4a** (D-47, D-48, D-58,
D-59) over roll-up revision **A3-R6** (2026-11-09 20:41, answering CR-A1-44 and CR-A1-53). Every number in the generated
block comes from `python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in
`team/A3/rollup/ROLLUP.md`). The block between the markers is regenerated on each run; the rest is hand-written and
follows `params/CHANGE-LOG.md`. **All nine flying subsystems come from the designers' `parts.csv`**, the pod at D2-R5
(D-47 bay) and the pack at F1's −0.022 node; A3's model is fallback and self-inertia boxes only. The station rule
reads `pod.pack_aft_travel_m` (12 mm) and `pod.pack_spacer_step_m` (2 mm) from D-59.

## Verdict

| Check | Result (A3-R6: D2-R5 bay, D-48 allocations, D-59 stations) | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic 2 323 g, predicted 2 437 g (growth 114 g of the 245 g reserve) | `CL-A3-MASS-BASIC`, `CL-A3-MASS-PREDICTED` → `R-MASS-GATE` | `MODELLED` |
| Gate margin after growth ≥ 100 g overrun, 550 g pack | +163 g | `CL-A3-GATE-MARGIN` | `MODELLED` (+58 %) |
| same, 503 g pack | +210 g | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| same, 680 g pack | +33 g: under the gate, the 100 g overrun is not covered (covered up to a 613 g pack) | `CL-A3-GATE-MARGIN-680` → `R-PACK-MASS` | `FAIL` |
| Worst subsystem vs allocation (D-48) | **fins 436.4 / 418 g (1.044)**: D3-R4 half-fin `FIN-001` 22.32 → 27.67 g each (two-layer board, D-54 stepped tip); pod 131.0 / 131 and propulsion 462.0 / 462 exactly on; the rest under | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `FAIL` (CR-A3-26) |
| **CG x in 0.050–0.0549 m**, 550 g pack at the −0.022 datum | **0.0525 m (16.4 % c)**, 0.01 of the half-range from mid; predicted 0.0539 m | `CL-A3-CG-X-RANGE` (0.01), `CL-A3-CG-X-PRED` → `R-CG-RANGE` | `MODELLED` |
| Each pack at its D-59 station, basic and predicted | all three inside; thinnest the 503 g pack on the crush stack, predicted 0.3 mm ahead of the aft limit | `CL-A3-CG-X-STATIONS` (0.89) → `R-CG-RANGE` | `MODELLED` (thin) |
| 503–680 g packs trimmable with the spacers | yes, with D-59's 12 mm aft travel | `CL-A3-PACK-TRIM` (0 mm) → `R-CG-RANGE` | `MODELLED` |
| Forward room at the datum | 3.4 mm (34.6 mm nose stack: stop face −0.1212, block ≥ 24.3, spreader 1.5) | `CL-A3-PACK-FWD-ROOM` | `MODELLED` |
| Lateral CG ≤ 5 mm | −1.1 mm | `CL-A3-CG-Y` → `R-CG-RANGE` | `MODELLED` |
| CG z in −0.02 … +0.03 m | +0.018 m | `CL-A3-CG-Z-RANGE` → `R-CG-RANGE` | `MODELLED` |
| Hover pitch-trim split ≤ 1.25 | 1.216 (+3 %) | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` | `MODELLED` (thin) |
| Inertia about the CG | Ixx 0.173, Iyy 0.045, Izz 0.167 kg·m² | `CL-A3-IXX/IYY/IZZ` | `MODELLED` |

**The D-47 bay puts the CG on the range mid-point; the D-59 travel keeps every listed pack inside.** During this
re-run three deliveries landed in turn, and the CG followed them. E1 stripped the ESC power leads (−13.6 g at x 0.101)
and D6 re-worked the mechanisms (−11.6 g at x 0.19–0.27): 0.0513 m at 20:35, which pushed the 680 g pack 0.4 mm off
the forward limit and led A1 to D-59 (aft travel 8 → 12 mm). Then D3-R4's heavier half-fins (+21.4 g, centroid aft of
the CG) and D2-R5's pod (+2.9 g) brought it back to 0.0525 m; F2's harness re-run (−4.5 g) left it there. On today's files the stations fall back to A1's first
D-59 table, not the 20:35 one now in the `pod.pack_x_nominal_m` note:

| Pack | D-59 station x (m) | Spacers | CG basic → predicted (m) | Margin fwd / aft (mm) | Status |
|---|---|---|---|---|---|
| 550 g (carried) | −0.024 | 14 mm | 0.0520 → 0.0534 | +2.0 / +1.5 | `MODELLED` |
| 503 g | −0.0254 (on the crush stack; wants −0.0305) | 14 mm + 1.4 mm play | 0.0533 → 0.0546 | +3.3 / **+0.3** | `MODELLED` (thin) |
| 680 g | −0.010 (no spacer, on the 0.060 stop; wants −0.009) | 0 mm | 0.0519 → 0.0532 | +1.9 / +1.7 | `MODELLED` |

Each 4 g placed 0.1 m from the CG moves the CG 0.17 mm and a station 0.7 mm, so H3 takes the stations from the
roll-up re-run on the day of the balance test, not from a note (CR-A3-27). D2-R5 still has the aft stop at 0.056. The D-59 face is 0.060
(CR-A1-54). With 0.056 the 680 g pack sits at −0.014: CG 0.0508 m, still +0.8 mm inside. If the fins come down to their
418 g (board centroid x 0.204), the CG moves 1.2 mm forward: the 503 g aft margin grows to about 1.5 mm and the 680 g
forward margin falls to about 0.8 mm.

If the built aircraft with a light pack balances aft of the aft mark, lead tape goes behind the nose: about 13 g per mm
of CG, capped at 10 g from the A1 reserve (`CL-A1-NOSE-BALLAST`, 0 g today). Beyond 10 g A1 re-opens the station.

**The gate holds with the carried 550 g pack** (+163 g predicted margin, of which 100 g is the first-build overrun). A
680 g pack leaves the aircraft under the gate (2 567 g predicted) but eats 67 g of the overrun. The overrun is covered
up to a 613 g pack (601 g at A3-R5; 631 g at 20:35, before D3's fins). E2 names a SKU and weighs it (CR-I1-13, D-58).
D-47 itself cost the 15 mm nose (inside D2's 131.0 g), a 5 mm higher stance CG (0.315 m above the feet) and the pitot
tip moving with the nose to x −0.210.

## Adopted allocations (CHANGE-LOG D-48; was D-38, D-07)

Every allocation is now the designer's delivered `parts.csv` plus the reductions A1 directed inside it.

| Subsystem | Allocation g | Basis (source claim) | Directed inside the allocation |
|---|---|---|---|
| wing | 405 | D1 CAD 387.3 g `EST` (`CL-D1-WING-MASS`: core 187, tape, spar 102, four plugs 22, elevons, label); the 17.7 g left is the cushion for XPS density and tape areal mass until `T-D1-WEIGH` | — |
| fins | 418 | D3 CAD 417.3 g (`CL-D3-MASS`: two-layer 0.21 m half-fins, blocks, tubes 0.344, ASA mounts, 16 mm collars with the 40 mm tail 42.2, 10 × 2 braces, anchors, strips, CF pins 4.3, strap eyes 1.8, ESC pads, bonds); C4 416.8 | collar 16 → 12 mm (−3 g, C4 CR-C4-25, if the tongue fits) pays C6's 15 mm root fillets (+3 g, CR-C6-24) |
| pod | 131 | D2-R4 128.1 g `EST` (`CL-D2-MASS`: shell, tray, hatch, stops, guides, crush block, spreader, spacers, handle, corner fillets, UBEC plate, tie bar) + 3 g nose extension (D-47); C5's full-section forward stop (+4 g) from the reserve if C3 adopts it | — |
| landing | 43 | D5-R4 42.50 g `EST` (`CL-D5-MASS-TOTAL`: 4 feet 40.6 + 2 caps 1.45 + 48 mm); spares are ground items | — |
| propulsion | 462 | E1 475.6 g (`CL-E1-MASS-PRP`) less 4 × 3.4 g | ESCs carried stripped of their factory power leads (F2 solders its own, CR-F2-07): `PRP-002` 7.6 g, E1 re-runs |
| power | 648 | pack 550 (`UNVERIFIED`, 503–680) + non-pack 88.2 g (`CL-PWR-MASS-NONPACK`: AS150U pair, 10 AWG main path, power frame `PWR-006`, PDB plate, bus board, UBEC, fuse, four ESC caps, CoreWing power board `PWR-003` 28 g `EST`); F1 638.2 | — |
| avionics | 45 | F3 36.5 g CAD (`CL-F3-MASS`: FC 12 without its power board, GPS, RX, MS4525DO + boom, gel cubes, microSD) + 8.5 growth; 7 g returned to the reserve | F5's two 150 mm T-antennas (+0.5 g) inside it |
| harness | 123 | F2 routed 122.6 g (`CL-F2-MASS`: ESC leads 75.0 at 0.51–0.65 m, phase extensions 11.7 `EST`, signals/servo/GH 19.0, fittings 16.9 `EST`); CG x 0.067 m | 12 g return to the reserve if the factory phase leads reach (`T-E1-MOTOR-RM`) |
| mechanisms | 80 | D6 82.3 g (`CL-D6-MASS`: Savox SH-0255MG+ 2 × 15.8, torque tubes 12.0, horns 13.1, frames 8.4, rods 8.3, rest 8.9) | 1/8 in → 3/32 in inter-panel rod (−3.6 g, effectiveness loss 7.1 → 8.5 %, D6's own fallback) |
| **sum / A1 reserve / gate** | **2 355 / 245 / 2 600** | the reserve covers growth by maturity (114 g on the current roll-up) and the 100 g first-build overrun with 31 g free | |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 600 g = allocations 2 355 + 145 g growth + 100 g overrun (D-48) | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 0 %: the 503 / 550 / 680 g listings are bounding cases, each with its own gate margin | `ASM-A3-PACK-RANGE`, `CL-A3-GATE-MARGIN(-503/-680)` |
| First-build overrun to keep free under the gate | 100 g | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.0522 m / 0.050–0.0549 m (15.6–17.2 % chord), `UNVERIFIED` (B3 R3 at 7° cant, 0.21 m fins, 0.14 m pod; D-47) | `params.json#cg` |
| Pack nominal centroid and flight stations | datum x −0.022 m (D-47; was −0.001, D-24); aft travel 12 mm to the no-spacer station −0.010, 2 mm spacer steps, forward limit −0.0254 (D-59); flight stations computed live by `CALC-A3-CG` (A3-R6: 550 g −0.024, 503 g −0.0254 on the stack, 680 g −0.010); spacers `POD-008` 2/4/6/8/8 mm | `params.json#pod.pack_x_nominal_m`, `pod.pack_aft_travel_m`, `pod.pack_spacer_step_m`, `ASM-A3-PACK-STATIONS`, `CL-A3-CG-X-STATIONS` |
| Room the pod nose needs ahead of the pack | 34.6 mm with the 8.8 mm nose block (stop at −0.1212, crush block 24.3, spreader 1.5): pack centroid ≥ −0.0254 m | `ASM-A3-NOSE-STACK` (D2-R5 params: stop face −0.1212) |
| CG range z, lateral | −0.02 … +0.03 m; \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

### Live roll-up

Sources: `wing` ← redesign/subsystems/wing/parts.csv; `fins` ← redesign/subsystems/fins/parts.csv; `pod` ← redesign/subsystems/pod/parts.csv; `landing` ← redesign/subsystems/landing/parts.csv; `propulsion` ← redesign/subsystems/propulsion/parts.csv; `power` ← redesign/subsystems/power/parts.csv; `avionics` ← redesign/subsystems/avionics/parts.csv; `harness` ← redesign/subsystems/harness/parts.csv; `mechanisms` ← redesign/subsystems/mechanisms/parts.csv.

| Subsystem | Alloc g (A1) | Basic g | Predicted g | Basic − alloc g | Status |
|---|---|---|---|---|---|
| wing | 405 | 387 | 407 | -18 | `PROPOSED` |
| fins | 418 | 436 | 458 | +18 | `FAIL` |
| pod | 131 | 131 | 138 | +0 | `PROPOSED` |
| landing | 43 | 42 | 47 | -0 | `PROPOSED` |
| propulsion | 462 | 462 | 490 | +0 | `PROPOSED` |
| power | 648 | 638 | 650 | -10 | `PROPOSED` |
| avionics | 45 | 36 | 39 | -8 | `PROPOSED` |
| harness | 123 | 118 | 130 | -5 | `PROPOSED` |
| mechanisms | 80 | 71 | 80 | -9 | `PROPOSED` |
| **total** | **2 600** | **2 323** | **2 437** | allocated 2 355 + growth 245 | gate margin +163 g |

| Gate case (predicted, all other items with growth) | Pack g | Predicted g | Gate margin g | Overrun to cover g | Claim | Status |
|---|---|---|---|---|---|---|
| lightest listing | 503 | 2 390 | +210 | 100 | `CL-A3-GATE-MARGIN-503` | `MODELLED` |
| as carried (`battery.mass_kg`) | 550 | 2 437 | +163 | 100 | `CL-A3-GATE-MARGIN` | `MODELLED` |
| heaviest listing | 680 | 2 567 | +33 | 100 | `CL-A3-GATE-MARGIN-680` | `FAIL` |

| Discipline | Basic g | Predicted g | Share |
|---|---|---|---|
| structure | 997 | 1 049 | 43 % |
| propulsion | 462 | 490 | 20 % |
| energy | 550 | 550 | 24 % |
| electrical | 206 | 229 | 9 % |
| avionics | 36 | 39 | 2 % |
| controls | 71 | 80 | 3 % |

| CG case | x m (% chord) | y m | z m | Status |
|---|---|---|---|---|
| Allowable (A1/B3) | 0.050–0.055 (16%–17%) | ±0.005 | -0.020…+0.030 | `PROPOSED` |
| Take-off, basic | 0.052 (16.4%) | -0.0011 | +0.019 | `CHECKED` |
| Take-off, predicted (growth pro rata) | 0.054 (16.8%) | -0.0013 | +0.018 | `CHECKED` |
| Pack slid -3.4 … +12.0 mm (spacers, crush stack) | 0.0517 … 0.0553 | | | — |
| Pack 503 g: nominal station → slid +0.0 mm (+ aft) | 0.0540 → 0.0540 | | | `CHECKED` |
| Pack 550 g: nominal station → slid +0.0 mm (+ aft) | 0.0525 → 0.0525 | | | `CHECKED` |
| Pack 680 g: nominal station → slid +5.3 mm (+ aft) | 0.0485 → 0.0500 | | | `CHECKED` |
| Pack 503 g at its D-59 station x -0.0254 (spacers 15 mm, clamped): basic → predicted | 0.0533 → 0.0546 (fwd +3.3 / aft +0.3 mm) | | | `CHECKED` |
| Pack 550 g at its D-59 station x -0.0240 (spacers 14 mm): basic → predicted | 0.0520 → 0.0534 (fwd +2.0 / aft +1.5 mm) | | | `CHECKED` |
| Pack 680 g at its D-59 station x -0.0100 (spacers 0 mm, clamped): basic → predicted | 0.0519 → 0.0532 (fwd +1.9 / aft +1.7 mm) | | | `CHECKED` |
| No pack (handling) | 0.076 (23.6%) | -0.0015 | +0.009 | — |

| CG result | Value | Unit | Source |
|---|---|---|---|
| Pack centroid now / needed for x = 0.052 m | -0.022 / -0.023 | m | `CL-A3-PACK-X-REQ` |
| Pack shift still needed for the target (+ aft) | -1 | mm | `CALC-A3-CG` |
| or the whole pod group (806 g: pod, power, avionics) by | -1 | mm | `CALC-A3-CG` |
| or the four motor stations (propulsion, 462 g) by | -1 | mm | `CALC-A3-CG` |
| Pack aft face to wing TE at that station | 273 | mm | `CL-A3-PACK-AFT-ROOM` |
| CG shift per mm moved: pack / pod group / stations | 0.24 / 0.35 / 0.20 | mm/mm | `CALC-A3-CG` |
| Forward room at the nominal station (nose block, stop, crush block, spreader taken) | 3 | mm | `CL-A3-PACK-FWD-ROOM` |
| Hover trim split upper/lower pair (limit 1.25, D-18) | 1.216 | — | `CL-A3-HOVER-SPLIT` → `R-HOVER-SPLIT` |
| Pack slide needed for 503–680 g beyond the trim travel | 0.0 | mm | `CL-A3-PACK-TRIM` |
| Most forward pack centroid the nose stack allows | -0.0254 | m | `CALC-A3-CG` |
| CG x range use: basic / packs at their stations (worst) / predicted | 0.01 / 0.89 / 0.58 | — | `CL-A3-CG-X-RANGE` / `CL-A3-CG-X-STATIONS` / `CL-A3-CG-X-PRED-RANGE` |
| Lateral CG offset / allowed 5 mm | 0.23 (-1.1 mm) | — | `CL-A3-CG-Y` |
| CG height above the feet in the stance | 0.316 | m | `CALC-A3-CG` |

| Inertia about the CG | Ixx (roll, cruise) | Iyy (pitch) | Izz (yaw, cruise) | Ixz | Unit |
|---|---|---|---|---|---|
| Basic, take-off | 0.1733 | 0.0448 | 0.1673 | -0.0023 | kg·m² |
| Radius of gyration | 0.273 | 0.139 | 0.268 | | m |

Allocations read from `params.json#mass.allocation_g` and checked equal to `params/mass_budget.json` (2 355 g + reserve 245 g = 2 600 g).

A3 position / maturity overrides (`team/A3/overrides.csv`): HRN-001: F2 harness.py breakdown (team/F2/mass_estimate.csv): wires CALC from routed lengths; fittings and phase extensions EST; lump carried at CALC 10 %; HRN-002: as HRN-001 (per-side lump); PRP-002: ESC 7.6 g stripped (D-48): 6.6 g bare board + 1.0 g signal lead and shrink EST per E1 parts.csv notes; only the bare board is a datasheet number.

Excluded as ground items (`flight: false` in interfaces.json, or no interface node and notes say not flying): GER-005 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, upper (orange piston + type-U cartridge + pad, pre-glued); GER-009 (redesign/subsystems/landing/parts.csv, flight false): Spare insert, lower (blue piston + type-L cartridge + pad, pre-glued); GER-010 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type U, loose (orange stripe); GER-011 (redesign/subsystems/landing/parts.csv, flight false): Spare cartridge pair type L, loose (blue stripe); GER-012 (redesign/subsystems/landing/parts.csv, flight false): Spare shoe; GER-006 (redesign/subsystems/landing/parts.csv, flight false): Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in; GER-013 (redesign/subsystems/landing/parts.csv, flight false): Brass tube 7/32 in OD (K&S), sharpened, cartridge bore cutter; PWR-201 (redesign/subsystems/power/parts.csv): Second flight pack (ground: charge / rotate; flight false).

Zero-mass lines (mass carried inside another part): FIN-101, FIN-102, FIN-103, FIN-104, FIN-105, FIN-106, FIN-107, HRN-101, HRN-102, HRN-103, HRN-104, HRN-105, HRN-106, HRN-107, HRN-108, HRN-109, HRN-110, HRN-111, HRN-112, PWR-101, PWR-102, PWR-103, PWR-104, PWR-105, PWR-106, PWR-202, PRP-005.

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
| `team/A3/overrides.csv` | A3 corrections to a designer's position or maturity, each with a reason; a cell may be an `=P:` expression so it follows `params.json` (today: ESC mass `EST`; harness lumps CALC per F2's breakdown; the A3-R6 bay overrides for the pack, straps, trim kit and pitot socket were dropped when D2-R5 and F1 carried the D-47 bay) | listed in the block; each has a change request to the owner |

Lines with zero mass (fasteners and consumables carried inside another part) are skipped; parts whose nodes say
`"flight": false`, and lines with no interface node whose notes say they do not fly (spare kits), are ground items. Allocations are read from `params.json` and checked
against `params/mass_budget.json`. Warnings are printed and listed in the block for: no position, a
parts.csv/interfaces.json mass mismatch, or a subsystem whose parts.csv is > 10 % lighter than the A3 estimate.
`--check` exits 1 when the stored roll-up no longer matches the files (use at each phase gate).

## Largest mass levers

| Lever | Δ mass | Owner | Status |
|---|---|---|---|
| Weigh the pack (503–680 g listings vs 550 g carried; I1's listing 680 g) | −47 … +130 g | E2 (CR-I1-13, D-58) | `UNVERIFIED` |
| ESC factory power leads removed (F2 solders its own 16 AWG leads to the pads) | −13.6 g, delivered (E1 `PRP-002` 7.6 g; propulsion 462.0 g) | E1 | taken |
| Inter-panel rod and frames (D6 re-work: 1/8 in pultruded CF rod) | delivered: mechanisms 70.7 g against 80 g (9.3 g under) | D6 | taken |
| Harness: factory phase leads reach (no extensions) | −12 g, returned to the reserve after `T-E1-MOTOR-RM` | F2, E1 | `UNVERIFIED` |
| Station collar 16 → 12 mm | −2.4 g delivered (D3-R4 `FIN-008` 10.05 g); the half-fin boards went +21.4 g (`FIN-001`), so fins are 18.4 g over | D3, C4 | open (CR-A3-26) |
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
