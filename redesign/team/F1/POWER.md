# Power distribution — K09-L

F1, revision F1-R2, 2026-11-09 (R2: pack's own leads, pod fit, itemised kit). Status: `PROPOSED`, every number `MODELLED` by `team/F1/power.py`, nothing bench-tested.
Re-check: `python -I redesign/team/F1/power.py`, `python -I redesign/team/F1/draw_schematic.py`, then
`python -I redesign/proofs/build_graph.py` (no F1 errors; the build fails today on other roles' drift).

**Verdict:** the main disconnect is the **Amass AS150U** (anti-spark), not the XT60. The XT60 fails the continuous
requirement before the burst case is considered. Wiring: **8 AWG** from the pack plug to the bus, **16 AWG** ESC
leads (18 AWG rejected), **20 AWG** UBEC feed and servo bus. A **6 V UBEC is fitted** for the servos, with a 5 A fuse on
its feed. The propulsion path has no fuse.

![K09-L power schematic](power-schematic.svg)

`FIG PWR-01 — Power distribution, single line, +/- pairs red/black, signal yellow, data grey dashed; drawn from claims.json.`

## Design currents

| Case | Pack current | Duration | Source | Status |
|---|---|---|---|---|
| Hover, gate mass, 5 m/s wind | 29.9 A | 120 s + 50 s descent | `CL-E2-HOVER-I-GATE` | `UNVERIFIED` |
| Cruise, pessimistic | 29.8 A | 308 s | `CL-E2-CRUISE-I-PESS` | `UNVERIFIED` |
| Vertical climb 2.5 m/s (447 W / 14.8 V) | 30.2 A | 25 s | `CL-B1-VCLIMB-P` | `UNVERIFIED` |
| **Continuous design current** (max of the three) | **30.3 A** | — | `CL-F1-I-CONT` | `MODELLED` |
| Transition forward / back | 42.9 / 39.6 A | 20 s each | `ASM-F1-PROFILE` (E2 phase table) | `UNVERIFIED` |
| Limited peak, 100 A limiter + 5 % sensor under-read | 105.3 A | ≤ 5 s | `CL-F1-ILIM-WORST` | `MODELLED` |
| Unlimited momentary, full pack | 120 A | < 5 s | `params.json#electrical.peak_current_a` | `PROPOSED` |
| Per ESC: hover share of the heavier pair (split 1.25) | 8.4 A | continuous | `CALC-F1-WIRES` | `MODELLED` |
| Per ESC: limiter / single-ESC burst on a fresh pack | 24.8 / 51.6 A | 5 s / 2 s | `P:propulsion.current_max_per_motor_a`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |

## Main disconnect: AS150U vs XT60

Requirement `R-DISCONNECT`: rating ≥ 1.25 × continuous = **37.8 A**. Short-time requirement ≥ 1.25 × 42.9 A = **53.7 A**.
Momentary case: **120 A**.

| Rating | Required | XT60 | AS150U | Source |
|---|---|---|---|---|
| Continuous | 37.8 A | 35 A (Amass) / 30 A (Holybro): **fails** | 70 A (+85 %) | `SRC-J1-AMASS-XT60`, `SRC-J1-HOLYBRO-CONN`, `SRC-J1-AS150U` |
| 1 min | 53.7 A | 60 A (+12 %) | 150 A (AS150 family) | `SRC-J1-HOLYBRO-CONN` |
| Momentary ≤ 5 s | 120 A (105 A limited) | no cited rating above 60 A: **fails** | 140 A (+17 %) | `SRC-J1-AS150U` |
| Anti-spark | wanted (4 × ESC caps at 16.8 V) | none | 15 Ω pre-charge contact, t95 180 ms, inrush 1.1 A | `SRC-F1-AS150U-LCSC`, `CL-F1-PRECHARGE-T95` |

`CL-F1-AS150U-BURST` (140 A ≥ 120 A) supersedes `CL-J1-XT60-BURST`. Cost of the choice: the Ovonic packs ship with
an XT60, so each pack gets an AS150U soldered on (H3 LiPo procedure), and the charger needs an AS150U-to-XT60 lead
(6.5 A charge current, fine on an XT60). The reseller ratings are `UNVERIFIED`. Open the Amass sheet before ordering.
Plug in slowly and hold at the first detent for ≥ 0.5 s.

## Wire gauges and derating

Model: IEC copper resistance with temperature; free convection (Churchill–Chu, horizontal cylinder) plus radiation
(ε 0.9); covered-groove factor 0.75 in the wing; twisted-pair factor 0.85 in the pod; ambient 30 °C
(`P:env.ambient_design_c` ceiling); transient = lumped copper + silicone heat capacity over E2's mission profile with
punches after each transition. Limits: steady rise ≤ 10 °C (`P:electrical.wire_temp_rise_max_c`); cases under 60 s
≤ 30 °C (`ASM-F1-TRANSIENT-LIMIT`), which keeps the conductor ≤ 60 °C, 14 °C below the XPS service limit.

| Run | Gauge | Length (one way) | Steady current | Steady rise | Mission peak, limited / unlimited | Loop R (hot) | Mass | Status |
|---|---|---|---|---|---|---|---|---|
| Pack's own leads, pack face → AS150U (maker gauge, assumed) | 10 AWG | 0.10 m | 30.3 A | 16.4 °C (limit 20) | — / 24.7 °C | 0.74 mΩ | — | `UNVERIFIED` (gauge not on the listing) |
| Same if the pack ships with 12 AWG | 12 AWG | 0.10 m | 30.3 A | **28.4 °C fails** | — / 49.2 °C | 1.22 mΩ | — | pack not accepted |
| Pack plug → power board → bus (twisted, vented pod) | 8 AWG | 0.15 m | 30.3 A | 9.2 °C | 10.9 / 12.0 °C | 0.68 mΩ | 29.0 g | `MODELLED` |
| Bus → ESC, ×4 (in the wing: + and − in two grooves 5 mm apart) | **16 AWG** | 0.50 m | 8.4 A | 9.2 °C | 14.2 / 18.0 °C | 14.5 mΩ | 64.6 g | `MODELLED` |
| Same, 18 AWG alternative | 18 AWG | 0.50 m | 8.4 A | **16.4 °C fails** | 30.6 / 41.4 °C | 23.6 mΩ | 39.7 g | rejected |
| Bus → fuse → UBEC | 20 AWG | 0.15 m | 1.2 A (servos stalled) | 0.7 °C | — | — | 2.0 g | `MODELLED` |
| UBEC → servo bus | 20 AWG | 0.35 m | 2.6 A (both stalled) | 3.1 °C | — | — | 4.6 g | `MODELLED` |
| Motor phase leads | motor's own | ≤ 0.10 m, not extended | — | — | — | — | — | `PROPOSED` |

The pack's own leads are bought with the pack, so they get their own limit: steady rise ≤ 20 °C
(`ASM-F1-PACKLEAD-LIMIT`, conductor ≤ 50 °C so the cell tabs stay under the 60 °C LiPo limit), checked by
`CL-F1-PACKLEAD-RISE` (+18 % at 10 AWG). A pack with 12 AWG leads fails it: confirm ≥ 10 AWG before ordering
(CR-F1-14) and cut the leads to 0.10 m when the AS150U goes on. Their 0.74 mΩ is not in `CL-F1-R-EXT`: a
charger IR reading taken at the connector already includes it.

Steady rise by gauge (`data/gauge_sweep.csv`; this is the derating table the choices come from):

| Case | Current | 8 AWG | 10 AWG | 12 AWG | 14 AWG | 16 AWG | 18 AWG |
|---|---|---|---|---|---|---|---|
| Pack path, continuous | 30.3 A | **9.2 °C** | 16.4 °C | 28.4 °C | 51.4 °C | — | — |
| Pack path, 42.9 A if held | 42.9 A | 17.5 °C | 31.3 °C | 55.3 °C | — | — | — |
| ESC lead, hover share | 8.4 A | 1.0 °C | 1.7 °C | 3.0 °C | 5.3 °C | **9.2 °C** | 16.4 °C |
| ESC lead, 24.8 A if held | 24.8 A | 7.2 °C | 12.7 °C | 22.0 °C | 39.5 °C | 71.4 °C | 137.7 °C |

The second and fourth rows are steady-state values. Those currents last 20 s and 5 s, so the mission peak column
above is the real check.

Answer to CR-A3-06: **16 AWG**. 18 AWG saves 25 g but rises 16 °C at the hover share. With the 2 s single-ESC burst
it reaches 41 °C, past the 30 °C short-time limit.

## Voltage drop and path resistance

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Common path: 2 AS150U contacts 1.6 + board/shunt/joints 0.6 + 8 AWG loop 0.68 | 2.9 | mΩ | `ASM-F1-R-CONTACT`, `ASM-F1-R-BOARD`, `CALC-F1-WIRES` | `UNVERIFIED` |
| Equivalent pack terminals → ESC pads (4 branches in parallel), hot | 6.5 | mΩ | `CL-F1-R-EXT` | `MODELLED` |
| Drop at 30.3 A continuous | 1.41 (limit 2) | % | `CL-F1-DROP-CONT` | `MODELLED` |
| Drop at the 100 A limiter, 24.8 A per ESC | 4.37 (limit 5) | % | `CL-F1-DROP-PEAK` | `MODELLED` |
| Loss in the common path at 30.3 A | 2.6 | W | `CALC-F1-WIRES` | `MODELLED` |

E2 assumed 3 mΩ and E1 4 mΩ (CR-F1-03 asks both to use 6.5 mΩ).

## Protection, sensing, BECs

| Item | Decision | Numbers | Source | Status |
|---|---|---|---|---|
| Propulsion path fuse | **none** | if a fuse opens in flight the aircraft crashes; protection is the AS150U rating, wire margins, the 100 A limiter and the ESCs' own current limit | `CL-F1-ILIM-WORST` | `PROPOSED` |
| UBEC feed fuse | 5 A mini blade, at the bus | feed 1.2 A at stall; protects 20 AWG against a UBEC short | `CL-F1-FEED-RISE` | `PROPOSED` |
| Current/voltage sense | FC power board (candidate SpeedyBee F405 Wing APP) | 90 A cont / 215 A peak ≥ 37.8 / 120 A; calibrate within 5 % at 25–30 A | `CL-F1-SENSOR-CONT`, `-PEAK` | `UNVERIFIED` (F3 picks the FC) |
| Servo supply | **UBEC 6 V, 8 A class, fitted** | required 2 × 2 × 1.3 A = 5.2 A; FC servo BEC 4.5 A < 5.2 A | `CL-F1-SERVO-BEC-REQ`, `CL-F1-UBEC-RATING` | `UNVERIFIED` (stall current) |
| UBEC drop rule | remove the UBEC only if bench stall ≤ 1.1 A per servo **and** the FC servo BEC ≥ 4.5 A cont | saves 13 g + fuse | `T-F1-SERVO-STALL` | — |
| UBEC wiring | UBEC + to the servo bus only; FC Vx not connected to it (two BECs never in parallel); common ground | — | — | `PROPOSED` |
| ESC capacitors | +680 µF 25 V low-ESR at each ESC's pads (0.5 m leads) | ripple ≤ 1.0 V p-p | `ASM-F1-ESC-CAP`, `T-F1-RIPPLE` | `PROPOSED` |
| Magnetics | pod runs twisted; GPS ≥ 0.10 m from bus and UBEC | — | `P:requirements.gps_mast_clearance_m` | `PROPOSED` |

## Fit in the pod (answer to CR-D2-07)

| Item | Need | D2 provides | Status |
|---|---|---|---|
| Parked connector | mated AS150U pair ≈ 22 × 14 × 55 mm `EST` + 8 AWG exit; was sized for an XT60 (30 mm long) | slot x 0.030 … 0.060 (30 mm) in the 37 × 59 mm left channel | **change**: CR-F1-13 asks for 60 mm |
| Pack lead | 0.10 m one way, 10 AWG (OD 4.8 mm) | ≥ 90 mm needed to reach the park | fits |
| 8 AWG pigtail bend | radius ≥ 5 × OD = 30 mm | channel 37 mm wide | fits with one 90° bend |
| Harness exits | per side: 2 × 16 AWG pairs (4 × 2.6 mm) + 2 DShot leads + 1 servo lead ≈ 45 mm² | 16 × 12 mm = 192 mm² each | fits (≈ 25 % fill) |
| Bus PDB, UBEC, fuse | ≥ 0.10 m from the GPS mast; UBEC ventilated | left channel | `PROPOSED` (CR-F1-08) |

## Bought items (answer to CR-I1-01 for power, CR-I1-10)

Main disconnect is the AS150U, so the re-termination line `H03` stays. Prices are `EST` from typical hobby
listings, not quotes; I1 confirms vendor and price.

| Item | Qty | Use | Est. price | Status |
|---|---|---|---|---|
| Amass AS150U pair (male + female) | 5 | aircraft, 2 packs, charge lead, spare | $25 | `UNVERIFIED` (open the Amass sheet) |
| Silicone wire 8 AWG, red + black | 0.5 m each | main pigtail | $8 | `EST` |
| Silicone wire 16 AWG, red + black | 2.5 m each | ESC leads (F2 cuts) | $8 | `EST` |
| Silicone wire 20 AWG, red + black | 1 m each | UBEC feed, servo bus | $4 | `EST` |
| UBEC 6 V, 8 A class (Hobbywing-type) | 1 | servo rail | $18 | `UNVERIFIED` (datasheet) |
| Mini blade fuse 5 A + inline holder | 3 + 1 | UBEC feed | $6 | `EST` |
| Capacitor 680 µF 25 V low-ESR | 5 | one per ESC + spare | $5 | `EST` |
| Bare 4-way PDB, 2 oz copper | 1 | bus | $6 | `EST` |
| Heat-shrink assortment incl. 10 mm | 1 | joints | $6 | `EST` |
| AS150U-to-XT60 charge adapter (built from the above) | 1 | charger | $0 | — |
| **Total** | | | **$86** | `EST` (inside the $124 kit lump `H01` + `H02`, shared with F2) |

## Mass

| Item | Mass | Status |
|---|---|---|
| AS150U aircraft half, bus PDB, UBEC, fuse + holder, 4 caps | 40 g `EST` | `UNVERIFIED` |
| 8 AWG main path | 29 g | `MODELLED` |
| **Power excluding the pack** | **69 g** vs 45 g allocated: **fails by 24 g** | `CL-F1-POWER-MASS` |
| ESC leads, 4 × 16 AWG pairs (harness) | 64.6 g vs A3's 56 g | `CL-F1-ESC-MASS` |

CR-F1-02 asks A1 for +25 g from the reserve. Without it, 10 AWG would have to replace the 8 AWG main path and it
would run at 16.4 °C.

## Inputs that changed since R1 (no F1 drift)

| Input | R1 value | Now | Effect on F1 |
|---|---|---|---|
| E2 pessimistic cruise current (`CL-E2-CRUISE-I-PESS`, re-runs after B1's 11×5.5MR) | 29.8 A | ≈ 20.9 A when E2 re-runs | none: hover 29.9 A and climb 30.2 A still set `CL-F1-I-CONT`; `ASM-F1-PROFILE` keeps 29.8 A in cruise (conservative) |
| B1 climb (CR-B1-08 rev 2) | 30.2 A | 30.3 A | +0.1 A, inside rounding |

## Tests (all planned)

| Test | Proves | Pass |
|---|---|---|
| `T-F1-WIRE-HEAT` | steady and peak rises, incl. the pack leads (≤ 20 °C) | 8 AWG at 30 A in a closed pod mock-up and 16 AWG at 8.4 A in a taped XPS groove: ≤ 10 °C after 10 min; 50 A for 2 s on 16 AWG: ≤ 30 °C |
| `T-F1-CONN-HEAT` | AS150U continuous | 38 A for 10 min, housing rise ≤ 30 °C |
| `T-F1-DROP` | `CL-F1-R-EXT` | 20 A step, ≤ 2 % at 30 A |
| `T-F1-SENSOR-CAL` | limiter accuracy | BAT.Curr within 5 % of a clamp meter at 5–30 A |
| `T-F1-SERVO-STALL` | UBEC decision | measured stall current; rail ≥ 5.8 V with both servos stalled, FC ≥ 4.8 V |
| `T-F1-PRECHARGE` / `T-F1-RIPPLE` | anti-spark, ESC supply | bus ≥ 95 % before the main pins close; ≤ 1.0 V p-p at the ESC pads |
