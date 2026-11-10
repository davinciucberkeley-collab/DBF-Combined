# D6 Mechanisms: summary (revision D6-R2, 2026-11-10)

Designer D6. Scope: elevon hinges, servos and their mounts, linkages, inter-panel link. K09-L has **no tilt
mechanism** (fixed motors); the only moving joints are the four tape-hinged elevon panels. Module:
`redesign/subsystems/mechanisms/` (SPEC.md, parts.csv, interfaces.json, fusion/mechanisms.py, BUILD.md). Status
`MODELLED`: CAD passes `fusion/check.py` with 0 errors and 0 warnings for `mechanisms` (the 16 errors in the full run
are propulsion keep-outs against fins and wing, not mechanisms). Every number below is `UNVERIFIED` until the servo
bench and the weigh-in.

## Action item: mechanisms mass (A3, CR-A3-20)

The action item quotes D6-R1 (82.3 g against 65 g). Since then A1 set the allocation to 80 g (D-48), and D6-R2 takes
the mass down to **70.68 g** (`CL-D6-MASS`, 12 % under). The live roll-up (A3-R6) reads 71 g basic and 80 g predicted
against 80 g, and lists the lever as "taken". Re-checked 2026-11-10: `make_mechanisms.py` → 70.7 g; `mech_calcs.py` →
40 claims, no negative margin.

| Item | R1 g | R2 g | Change | Claim | Status |
|---|---|---|---|---|---|
| Servos SH-0255MG+ (2) | 31.6 | 31.6 | none (only 12 mm micro servo with ≥ 3.5 kgf·cm found) | `SRC-D6-SH0255` | `UNVERIFIED` |
| Inter-panel rods (2) | 8.3 | 1.7 | 1/8 in music wire → 1/8 in pultruded CF | `CL-D6-ROD-MASS`, `-R1` | `MODELLED` |
| Torque tubes CF 5 × 4 (4) | 12.0 | 10.3 | inboard tube 220 → 160 mm (70 % of horn-to-root) | `CL-D6-EFF-LOSS-IN` 7.1 % | `MODELLED` |
| Horns (4) | 13.1 | 11.7 | flanges 20 → 14 mm, backplate 16 → 12 mm | `CL-D6-BOND-HORN` 1 109 mm² | `MODELLED` |
| Servo frames (2) | 8.4 | 6.4 | top plate a 4 mm rim with a window | `CL-D6-BOND-FRAME` 1 855 mm² | `MODELLED` |
| Rest: arms, pushrods, covers, tape | 8.9 | 8.9 | none | — | `MODELLED` |
| **Total vs allocation 80 g** | **82.3** | **70.7** | **−11.6 g at x 0.19–0.27 m** | `CL-D6-MASS` | `UNVERIFIED` (+12 %) |

Levers the action item named, and the decision on each:

| Lever | Result | Claim | Decision |
|---|---|---|---|
| 2 mm CF rod | outboard effectiveness loss 16.9 % (limit 10 %) | `CL-D6-EFF-LOSS-OUT-2MM-CF` | rejected |
| 3/32 in steel rod (D-48 directive) | −3.6 g only, loss 9.1 % | `CL-D6-EFF-LOSS-OUT-332-STEEL` | superseded by 1/8 in CF (−6.6 g, 7.9 %) |
| Torque tube on one panel only (drop inboard) | inboard loss 18.5 % | `CL-D6-EFF-LOSS-IN-NO-TUBE` | rejected; inboard tube shortened instead (7.1 %) |
| Lower infill on horns | ≈ 2 g; horns carry the clevis bearing and the rod-boss bond | — | not taken: 9.3 g under already, CG on range mid (0.0525 m) |

## Key engineering numbers

| Check | Value | Limit | Claim | Status |
|---|---|---|---|---|
| Hinge moment per servo, 25° at VD / VA / cruise (B2 bound) | 0.440 / 0.250 / 0.038 N·m | — | `CL-D6-H-VD-FULL`, `-VA-FULL`, `-CRUISE` | `UNVERIFIED` |
| Servo torque needed, 1.5 × H at VD through the four-bar | 3.49 kgf·cm | ≤ 3.9 (6 V) | `CL-D6-SERVO-TORQUE-REQ` | `UNVERIFIED` (+11 %) |
| Same at 4.8 V | 1.98 kgf·cm | ≤ 3.1 | `CL-D6-SERVO-TORQUE-48V` | `UNVERIFIED` (+36 %) |
| Servo throw for ±25° surface | 44.7° | ≤ 45° | `CL-D6-THROW-NEED` | `UNVERIFIED` (+1 %, thin) |
| Free play at the surface | 0.84° | ≤ 1.0° | `CL-D6-SLOP` | `UNVERIFIED` (+16 %) |
| Smallest running clearance through ±30° | 1.10 mm | ≥ 1.0 mm | `CL-D6-CLEAR-MIN` | `CHECKED` (+10 %) |
| Bridge rod in fin notch: side / bottom | 2.2 / 3.5 mm | ≥ 1.0 mm | `CL-D6-CLEAR-ROD-NOTCH-SIDE`, `-BOTTOM` | `CHECKED` |
| Effectiveness loss at VA, outboard / inboard | 7.9 / 7.1 % | ≤ 10 % | `CL-D6-EFF-LOSS-OUT`, `-IN` | `UNVERIFIED` |
| Pushrod Euler factor at VD | 17.9 | ≥ 3 | `CL-D6-PUSHROD-BUCKLING` | `UNVERIFIED` |
| Servo supply, 2 × 1.4 A stall × 2 | 5.6 A | ≤ 8 A UBEC | `CL-D6-SERVO-SUPPLY` | `UNVERIFIED` |
| End-stops: bevel (TE down), cover slot (TE up) | ±30° mechanical, ±25° software | — | `P:mec.mech_stop_deg` | `PROPOSED` |

## Open items

| Id | To | What | State |
|---|---|---|---|
| CR-D6-13 | A1 (cc A3) | Allocation 80 → 72 g (8 g back to the reserve); drop the 3/32 in rod directive from the `params.json` note | open (params still 80 g, note still quotes R1) |
| CR-D6-14…18 | D1, B3, I1, C6, H1 | groove and patch sizes, effectiveness 0.92, CF rod line, CF-in-PETG pull test, tap test | open |
| `T-D6-THROW`, `T-D6-WEIGH`, `T-D6-TWIST`, `T-B2-HINGE` | D6, H1 | bench throw, weigh, panel twist, hinge moment | planned |

Files: `team/D6/mech_calcs.py` (writes `claims.json`), `team/D6/draw_linkage.py` (`fig-d6-linkage.svg`),
`team/D6/CHANGE-REQUESTS.md`.
