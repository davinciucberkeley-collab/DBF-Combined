# QP-2 baseline, concept A (A2 systems, A3 mass, I1 BOM), 2026-11-14

Files: `qp/A/BOM-A.csv`, `bom_a.py`, `mission_gate_a.py`, `MISSION.md`, `MASS-GATE.md`, `REQUIREMENTS-A.md`. Reproduce: `python -I redesign/qp/A/bom_a.py`, `python -I redesign/qp/A/mission_gate_a.py`. Nothing bought, built or flown; no git; nothing edited outside `qp/A/` and this file. Labels: `V` vendor page read, `U` snippet, `EST` estimate, `—` unknown. New reads today: Tattu 2300 page ($37.09, 270 g, in stock), T-Motor MN2212 page ($46.90, stock not shown), SpeedyBee BLS 35A Mini V2 4-in-1 ESC ($45.66, 7.2 g, DShot300/600, BLHeli_S J-H-40, in stock). Other V lines are carried from `review/QP-1/COST.md`.

## 1. Result

**One BOM: total $1,850.76, margin +$149.24** (goods $1,347.65 + tax $138.13 + shipping $36.42 `EST` + FAA $5 = spend $1,527.20; crash reserve $323.56). **With the 17 unverified lines (U + EST, 37 % of goods) +30 %: $2,059.95, margin -$59.95.** This is not the board's $1,499 / +$501 (nor +$387 at +30 %). It fails two board tests: R5 (total <= $1,750) and the +30 % margin >= $100 rule. Growth absorbed = margin / (goods x 1.1025) = 10 % (board table: A 77 %).

Why it moved +$352 (all itemised in the CSV, none is a spec change):

| Cause | $ incl tax |
|---|---|
| Crash reserve per the K09-L lesson: pack + motor + servo + full airframe set (foam, tube, fin CFRP, half PETG) beyond the spares, + 3 shipments (board: $138) | +185 |
| Test and tool lines the board did not carry: thrust stand, yaw rig, hot-wire, flux, transport box, BEC, fin CFRP sheet, 2nd carbon tube, prop alternates, linkage | about +190 |
| ESC: one 4-in-1 DShot board ($45.66) replaces five Skywalker 30 A ($74.95) | -32 |
| Motors at $46.90 x 5 (board already) | 0 |
| Shipping 3 groups (board used 2) | about +11 |

Spares in the spend: 1 of 5 motors, 2 of 6 prop pairs, 1 of 3 servos. **No spare ESC board and no spare FC**; a crash that kills them is outside the reserve.

Per-subsystem caps (`bom_a.py`; nominal rounded up to $5; early-warning, not slack):

| Subsystem | Nominal $ | Cap $ | Unverified share |
|---|---|---|---|
| propulsion | 406.47 | 410 | 24 % |
| power | 234.94 | 235 | 28 % |
| avionics | 329.34 | 330 | 7 % |
| mechanisms | 66.12 | 70 | 20 % |
| airframe | 254.59 | 255 | 76 % |
| ground + test | 133.69 | 135 | 71 % |
| tools | 38.59 | 40 | 100 % |
| transport | 22.05 | 25 | 100 % |
| shipping + FAA | 41.42 | 45 | EST |
| crash reserve | 323.56 | 325 | |
| **Caps sum** | | **1,870** | contingency to $2,000: **$130** |

Airframe, ground + test, tools and transport are 71-100 % unverified: +30 % on them alone is +$82.

**Levers, none applied (team decision):** prop alternate pairs 17.6, 2 spare prop pairs 23.0, ammo can 22.0, hot-wire 22.1, transport box 22.1, BEC 11.0, flux 16.5, microSD kit 24.3 = about $159, which brings the +30 % margin to about +$99. Dropping the ESC spare is already done. A cheaper pack or FC is not found in stock (`COST.md`). Re-sitting R5 is the board's call.

## 2. Mission (MISSION.md)

Cruise **17 m/s**, 3.41 min (204.6 s: 15 s settle + 2 laps + go-around lap + run-in; R 51.0 m, far point 201 m), requirement 3.5 min; hover-mode **3.0 min** incl. 40 s go-around; reserve 20 %, pack floor 0.90. Stall was stale: Vs 11.0 m/s was at 1.226 kg; at the 1.50 kg gate Vs 12.19, 1.3 Vs 15.85 (cruise 17 is 7 % over it; 15-16 m/s fail). Energy at the gate 22.1 Wh vs 24.5 Wh usable (Tattu 34.0 Wh): margin **1.11x**, all `EST`.

## 3. Mass gate (MASS-GATE.md)

**1.50 kg frozen**, basis: T/W sag 1.77 (>= 1.6 holds to 1.655 kg), fresh 2.30 (to 1.729 kg). **New finding: the transition entry window shrinks to +-3.0 % at 1.50 kg** (1.33-1.41 W; +-8.1 % at 1.355 kg; +-5 % needs <= 1.441 kg), so 1.50 kg is the weigh-in limit and **<= 1.44 kg predicted is the design target**. Roll-up basic 1,167 g (4-in-1 ESC 20 g, Tattu 270 g, fins 70 g), growth 140 g (EST 20 % / DATASHEET 5 %), predicted 1,307 g, overrun 48 g (3.2 %), total 1,355 g, 145 g under the gate. CG target 20-26 mm aft of the LE (SM 8.4-6.0 %), hard 28.5 mm, forward 4.0 mm.

## 4. Open for the board / team

1. Total $1,851 breaks R5 and the +30 % rule: pick levers, or accept R5 at a higher line.
2. The 4-in-1 ESC is unverified for bidirectional DShot (BLHeli_S J-H-40 on the page, Bluejay not stated); the mass line and rpm notch (A-P17) depend on it.
3. GPS (V04) is on backorder; MN2212 stock not shown; prop price is a snippet (P02 `U`).
4. Transport is the user's new rule (one car trunk, two pieces at most); A is one piece 0.90 x 0.50 x 0.39 m; trunk size `—`.
5. Not computed for A: hinge moment, Cn_beta, limit loads, harness mass, build hours.
