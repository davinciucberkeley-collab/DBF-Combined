# Mass, CG and inertia — K09-L

Roll-up owner A3 (mass-properties); budget text A1. Status `PROPOSED`, revision A3-R3 (CR-A1-11), 2026-11-09. Every number
below comes from `python -I redesign/team/A3/mass_rollup.py` (claims in `team/A3/claims.json`, every item in
`team/A3/rollup/ROLLUP.md`). The block between the markers is regenerated on each run; the rest is hand-written
and follows `params/CHANGE-LOG.md` (D-07, D-17, D-18).

## Verdict

| Check | Result | Claim | Status |
|---|---|---|---|
| Take-off mass vs 2 600 g gate | basic 2 145 g, predicted 2 492 g | `CL-A3-MASS-BASIC`, `CL-A3-MASS-PREDICTED` | `UNVERIFIED` (estimates) |
| Gate margin after growth, against the 100 g first-build overrun | 108 g | `CL-A3-GATE-MARGIN` | `CHECKED` (+8 g; the pack decides it) |
| CG x in 0.040–0.049 m, pack 29 mm ahead of the pod centre (D-17) | 0.044 m (13.8 % chord), 10 % of the half-range from mid | `CL-A3-CG-X-RANGE` → `R-CG-RANGE` | `UNVERIFIED` (range not yet re-derived at R1) |
| Pack centroid station for 0.044 m | x = −0.034 m (pod centre −0.005 m − 29 mm) | `CL-A3-PACK-X-REQ` | `PROPOSED` |
| Pack fore face to pod nose at that station | 1 mm outside skin: no room for the nose wall, no forward slide | `CL-A3-PACK-FWD-ROOM` | `CHECKED` on paper, does not fit as built → CR-A3-11 |
| CG z in −0.02 … +0.03 m | +0.017 m | `CL-A3-CG-Z-RANGE` → `R-CG-RANGE` | `UNVERIFIED` (in range, estimates) |
| Hover pitch-trim split upper/lower ≤ 1.25 (`requirements.hover_split_max`, D-18) | 1.194 (+4 %) | `CL-A3-HOVER-SPLIT` | `UNVERIFIED` (passes; limit `PROPOSED`) |
| Worst subsystem vs A1 allocation | power 595 / 595 g, fins 369 / 370 g | `CL-A3-ALLOC-WORST` → `R-MASS-ALLOC` | `CHECKED` at zero margin → CR-A3-12 |

**The layout balances with the pack 29 mm forward of the pod centre (D-17), but the pack then touches the pod nose.**
With the motor tubes through the wing at x = 0.045 m and the pod nose at −0.105 m (D-04, D-08) the pack centred
gives 0.051 m; 29 mm forward gives 0.044 m, on target. A 140 mm pack centred at −0.034 m starts at −0.104 m, 1 mm
behind the outside of the pod nose, so the nose wall does not fit and the ±30 mm slide is aft-only (0.044–0.052 m).
Moving the pack 26 mm instead of 29 leaves a 3 mm wall and puts the CG at 0.045 m, still inside the range; A1/D2
choose (CR-A3-11). **The mass gate holds with 108 g to spare after growth by maturity**, but that is one pack
listing: the 550 g carried can be 503 g or 680 g (−47 / +130 g). Weighing the first pack (E2) settles it either way.
A 680 g pack at the same station puts the CG at 0.040 m, the forward limit; slide it aft to re-trim.

**Fins model aligned with the D-04 hardware.** The fins rows still carried the old 0.18 m tube-to-spar bridge (15 g)
and the bridged-joint clips (40 g each). They now carry the through-core block (20 g each), the bond along the tube
plus clips (30 g each) and consumables (14 g each), the items A1's 370 g allocation was built from: fins 369 g.
Fins and power now sit at their allocations with no margin, so any growth in either goes straight to A1's reserve.

## Adopted allocations (CHANGE-LOG D-07)

| Subsystem | Allocation g | Basis |
|---|---|---|
| wing | 405 | core 221 (calc, c 0.32, less the spar slot), tape 48, spar 102, slot fill 15, edge tape + label 5, consumables 14 |
| fins | 370 | 2 fins (2 layers, 0.275 chord) 84, 2 tubes 86, 4 motor mounts 72, 2 through-core blocks 40, bond + clips 60, consumables 28 |
| pod | 105 | shell + tray + hatch 70, straps 20, GPS mast 8, pitot mount 4, 3 spare |
| landing | 40 | 4 crushable feet × 10 g at 45 mm height, ≥ 40 mm stroke |
| propulsion | 440 | 4 × (motor 81 + ESC 6.6 + prop 17 + adapter and nut 5) = 438 |
| power | 595 | pack 550 (`UNVERIFIED`) + disconnect, main leads, UBEC 45 |
| avionics | 75 | FC 25, GPS 12, RX 3, airspeed 6, pitot 12, mounts 8 = 66; 9 left for telemetry |
| harness | 105 | 4 × 0.5 m 16 AWG pairs 56, signal leads 6, bullets 16, servo leads 10, sensor cables 6, ties 10 |
| mechanisms | 65 | 2 × 15 g servos (≥ 3.04 kgf·cm), horns, pushrods, links, hinge tape, covers |
| **sum / A1 reserve / gate** | **2 200 / 400 / 2 600** | the reserve covers growth by maturity (347 g predicted) and the 100 g first-build overrun |

## Budget rules

| Rule | Value | Source |
|---|---|---|
| Hard gate (as built, ready to fly, pack in, props on) | 2 600 g | `params.json#requirements.mtow_gate_kg` |
| Sized mass used by performance | 2 600 g (gate); `mtow_sized_kg` 2 550 g is allocations + planned growth + overrun | `params.json#requirements.mtow_sized_kg` |
| Growth by maturity (added per item) | EST 20 % · CALC 10 % · DATASHEET 5 % · CAD 5 % · WEIGHED 1 % | `ASM-A3-MGA` |
| Pack growth | 24 % (550 → 680 g listing) | `ASM-A3-PACK-RANGE` |
| First-build overrun to keep free under the gate | 100 g | `params.json#requirements.build_overrun_kg` |
| Ground items (box, cradles, tools, chargers) | never counted | subsystem `transport`, `"flight": false` |
| CG target / range x | 0.044 m / 0.040–0.049 m (12.5–15.3 % chord), `UNVERIFIED` until B3 re-derives at R1 (D-17) | `params.json#cg` |
| CG range z, lateral | −0.02 … +0.03 m; \|y\| ≤ 0.005 m | `params.json#cg` |
| Hover pitch-trim split upper/lower | ≤ 1.25 | `params.json#requirements.hover_split_max` (D-18) |

<!-- rollup:begin (generated by team/A3/mass_rollup.py; edits here are overwritten) -->

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
| 3 `team/A3/mass_model.csv` | A3 bottom-up estimate, 43 lines | cells starting `=` are expressions of `P:` keys, so geometry follows `params.json` |

Warnings printed (and listed in the block above) for: parts with no mass, no position, a parts.csv/interfaces.json
mass mismatch, or a subsystem whose parts.csv is > 10 % lighter than the A3 estimate (missing parts).
`--check` exits 1 when the stored roll-up no longer matches the files (use at each phase gate).

## Largest mass levers

| Lever | Δ mass | Owner | Status |
|---|---|---|---|
| Weigh the pack (503–680 g listings vs 550 g carried) | −47 … +130 g | E2 | `UNVERIFIED` |
| One foam-board layer per half-fin with the tube as the LE stiffener (if C4's mode check passes) | ≈ −40 g | D3, C4 | `PROPOSED` |
| 18 AWG instead of 16 AWG ESC leads (0.5 m, 30 A momentary) | ≈ −18 g | F1, F2 | `PROPOSED` |
| Drop the UBEC if the FC regulator carries both servos | −10 g | F1 | `PROPOSED` |
| Through-core block heavier than 20 g each if it must carry the fin-joint moment (C1 G2, 10.7 N·m) | + ? g | C4, D3 | open |
| Feet heavier than 10 g each for the ≥ 40 mm crush stroke | + ? g | D5, C5 | open |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-A3-WEIGH-PARTS` | 1 g scale on every bought part, the first core and the first fin; owner sets `VERIFIED` + `mass_g` | mass claims |
| `T-A3-CG-BALANCE` | two scales or knife edges under the wing at known x, ready to fly | CG x/z, pack station |
| `T-A3-SWING` | bifilar pendulum, two 1.5 m strings, each axis | Ixx, Iyy, Izz |
| `T-A1-WEIGH` | complete aircraft on a 5 kg scale | gate |
