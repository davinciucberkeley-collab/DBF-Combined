# Concept A: scaled quad tailsitter (D-182), design workspace

**This is the current design** (J6 board, 2026-11-14, `../review/QP-1/BOARD.md`). K09-L failed the $2,000 limit
(cheapest workable build about $2,577, `../review/CLOSURE-ROUND-2026-11-14/DESIGN-TO-COST.md`). The board then
sized four concepts to equal depth and chose A. D-181 (quadplane B) was reversed the same day. B is the fallback.
The lifeboat is D2, the ZOHD Altus VTOL kit, used if there is no tethered hover by 2027-02-15.

User constraints (root `CLAUDE.md`):
- $2,000 total, all bought new (tax, shipping, 2 packs, charger, radio, test gear, tools unless Jacobs lists them,
  crash reserve).
- Flight-tested by 30 April 2027.
- The packed aircraft fits one car trunk (two at most).
- Passes the 3-D physics checks.
- The CAD looks exactly like the physical aircraft: real shapes from vendor drawings, no stand-in disks or boxes (2026-11-15).
- Limit exposed wiring: wires inside tubes, core channels or covers; every exposed length listed with its reason (2026-11-15).

Everything else is derived by the team and written with its basis. Decisions D-182 to D-195 are logged in
`../params/CHANGE-LOG.md`.

## The aircraft (baseline 2026-11-15)

The airframe:
- 0.90 m flat flying wing, hot-wired FOAMULAR 150 core, tape skin, carbon spar.
- Two fins; four fixed T-Motor MN2212 KV780 motors with APC 9x4.5MR/MRP props in an X, canted 16°.
- Two elevons at ±20° (ES3054HV servos on a 7.2 V rail), each with a 15.6 g lead balance strip under PETG caps,
  mechanical stops at ±21° and a silicone-fluid hinge damper (D-188).

The electronics and flight software:
- Two Tattu 4S 2300 mAh packs.
- Kakute Wing Mini flight controller hard-mounted at the spar centre; BLHeli_S ESCs.
- ArduPilot Plane in tailsitter mode.

| Number | Value | Source |
|---|---|---|
| Take-off mass, predicted | 1,454 g itemised / 1,458.1 g flat rule `EST` (target ≤ 1,460 since D-195, weigh-in gate 1,470; 1.9 g of room after D-199) | `A/MASS-GATE.md` s10 |
| Basic mass (CAD) | 1,262.6 g, CG 20.7 mm aft of LE (band 19-26; trim ends 19.4 / 22.8 with the 6 mm forward travel), SM 8.2 % `EST` | `A/sitl/cad_mass.json` |
| Hover T/W at 1.46 kg, spin-capped | 2.35 fresh, 1.86 sagged `EST` (transition window ±5.6 %) | `A/mission_gate_a.py` |
| Cruise to BATT_LOW at 1.46 kg, 17 m/s | 4.27 min (need 3.41) `EST` | `A/mission_gate_a.py` |
| Elevon flutter, lowest onset (with damper) | 38.5 m/s hot `EST` (line 28.8); wing 33.4 m/s fins off | `A/structures/flutter_d195.md` |
| BOM total | $1,775.09; +$105.08 margin if unverified lines run 30 % over (G7 PASS) | `A/bom_a.py` |
| 3-D gates | collision 0 at neutral, ±20° and ±21°; assembly 41 steps (5 are wire threading / laying markers), 97/97 parts; wires: 4.27 strand-m exposed (was 9.09), `../review/QP-5/HARNESS-ENCLOSED.md` | `A/cad/out/REPORT.md`, `ASSEMBLY.md` |

Nothing is bought, weighed, built or flown.

## Rounds

| Round | What | Reports |
|---|---|---|
| QP-1 | Equal-depth sizing of A, B, T, D2; board picks A | `../review/QP-1/` |
| QP-2 | SITL, wind, bench plan, baseline; D-183, D-184 | `../review/QP-2/` |
| QP-3 | SITL flight, structures, cost and schedule, CAD with the 3-D gates; D-185, D-186 | `../review/QP-3/` |
| QP-4 | Pre-order items, board re-sit, fixes (D-187 balance; D-188 hinge damper, caps, stops, foam at 103 kPa) | `../review/QP-4/` |
| QP-5 | CAD fidelity round (D-193, D-194) and the re-run of the analyses it invalidated (D-195) | `../review/QP-5/` |

## Before the main order

Order 1, the bench kit (`A/ORDER-1.csv` plus 3 servos), is approved for early December. The main order waits on:
- the bench thrust, yaw and current tests;
- elevon coupon test E1 (`../review/QP-4/FIXES2.md` s8);
- weighing the foam, printed parts and epoxy (at least 36.2 g of the 41.6 g of estimated cuts must be real for the 1.46 kg target);
- the T-Motor stock answer;
- the written plan for four test mornings a week from 8 February 2027 (`../review/QP-4/BOARD.md`).

## Layout

- `A/`:
  - BOM, mission, mass gate, requirements, parameter file, schedule, Order 1;
  - `bench/`, `sitl/` (run logs are git-ignored), `structures/`, `cad/`.
- `sizing*/`, `cost/`, `requirements/`: QP-1 sizing of all four candidates.
- The K09-L tree (`../params`, `../subsystems`, `../team`) is the previous design's record. Do not edit it for
  concept A.
