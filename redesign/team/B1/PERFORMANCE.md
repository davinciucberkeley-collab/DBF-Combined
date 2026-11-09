# K09-L whole-aircraft performance

Status: `MODELLED` (B1, rev 2, 2026-11-09, answers CR-A1-13). The model now uses the R1 configuration: chord 0.32 m,
S5010 with B2's trimmed polar and CLmax, the 11×5.5MR prop (APC PER3 via B4), E1's motor constants, sag 0.72 and
the 400 W params hover power. Re-check: `python -I redesign/team/B1/performance.py`, then
`python -I redesign/proofs/build_graph.py`. Result 2026-11-09: no B1 drift and no B1 claim fails. The build still
fails on other roles' drift (A5, B2, E1, E2); E2's drift comes from B1's new cruise power, which CR-E2-08 asked for.

**Verdict.** At 16 m/s and 2.6 kg the aircraft needs **218 W in cruise** (285 W pessimistic), not the 307 W of
rev 1. That gives **17.0 min of cruise after the 2 min hover** (12.7 min pessimistic) against the 5 min
requirement. The 10 min stretch target is met in both cases. The transition gate passes, but only just:
1.3 Vs = 15.42 m/s, which is 0.58 m/s below cruise. The pack sag of 0.72 (D-06) is the new constraint. On a worst-case
pack, the rev 1 pitch-over rate of 20 °/s uses 96 % of available thrust, so B1 now proposes **12 °/s**
(peak 0.76, 7.7 s to 1.3 Vs). Landing wind is limited by the 30.6° tip-over angle, to **5.8 m/s steady**.

## Inputs and assumptions

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Mass: gate / sized / lightest flying | 2.600 / 2.550 / 2.150 | kg | `params.json#requirements`, `CL-A1-MASS-SIZED`, sized − growth reserve | `PROPOSED` |
| Wing S, AR | 0.368, 3.59 | m², — | `CL-A1-WING-AREA`, `params.json#wing` (c 0.32) | `PROPOSED` |
| Wing profile drag (S5010, trimmed, Re 3 × 10⁵, Ncrit 9) × tape-seam factor | 0.00738 × 1.10 | — | `P:b2.avl.cd0_wing`, `ASM-B1-WING-ROUGH` (Ncrit 5/9 ratio, CR-B2-08) | `UNVERIFIED` |
| Oswald e: base / pessimistic | 0.93 / 0.80 | — | `P:b2.avl.e_oswald`, `params.json#wing.oswald_e` | `UNVERIFIED` |
| Lift slope, α₀ (elevons neutral), trimmed CLmax | 3.58 /rad, −1.23°, 0.804 | — | `P:b2.avl.cla_per_rad`, `P:b2.xfoil.alpha0_2d_deg`, `CL-B2-CLMAX-DESIGN` | `UNVERIFIED` |
| Non-wing drag build-up | Cf 0.007, FF fin 1.20 / pod 1.30, tube Cd 0.30, CdA 0.0004 m² per motor, IF 1.15 | — | `ASM-B1-DRAG` (K09 card, accepted by REVIEW) | `UNVERIFIED` |
| Trim drag factor | 1.02 | — | `ASM-B1-TRIM` (B2 polar trimmed; B3 +0.2 %) | `PROPOSED` |
| Post-stall wing | CN = 1.28 sin α, 4° e-fold from CLmax | — | `ASM-B1-CD90` (B2 accepts 1.2; 1.28 kept, conservative for wind) | `PROPOSED` |
| Prop Ct(J), Cp(J) | APC PER3 11×5.5MR, 6 000 rpm, 19 rows + zero-thrust row at J 0.639 | — | `ASM-B1-PROP`, `SRC-B1-B4-PER3-55` (rows compared 2026-11-09) | `PROPOSED` |
| Motor Kv, Rm, I₀ | 900, 0.086, 0.9 | rpm/V, Ω, A | `ASM-E1-KV`, `ASM-E1-RM`, `ASM-E1-I0` | `UNVERIFIED` |
| Chain calibration to maker table (690 gf, 89 W, via 11×4.5MR) | 1.13 | — | `CL-B1-KCAL` | `UNVERIFIED` |
| Full-throttle thrust per motor (fresh, limited) × sag | 1.62 kg × 0.72 | — | `params.json#propulsion` (E1, E2) | `UNVERIFIED` |
| Hover download, ESC η, avionics | 1.06, 0.95, 6 | —, —, W | `params.json#propulsion.download_factor`, `ASM-B1-ESC`, `ASM-B1-AVIONICS-W` | `PROPOSED` |
| Mission hover power (pessimistic × 1.10) | 400 (440) | W | `params.json#performance.hover_power_w` (E1), `ASM-B1-PESS` | `UNVERIFIED` |
| Pessimistic case | CD0 × 1.3, e 0.80, η_prop × 0.85, hover and transition energy × 1.10 | — | `ASM-B1-PESS` | `PROPOSED` |
| Steady thrust allowed (20 % control reserve) | 0.80 of available, sagged | — | `ASM-B1-CTRL-RESERVE` | `PROPOSED` |
| Pack energy, reserve | 96.2, 20 % | Wh | `params.json#battery`, `#requirements` | `UNVERIFIED` |

## Aerodynamics

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| CD0 (wing 0.0093 · fins 0.0112 · motor tubes 0.0173 · motors 0.0050 · pod 0.0023) | 0.0452 | — | `CL-B1-CD0` | `UNVERIFIED` |
| k, base / pessimistic | 0.0950 / 0.1107 | — | `CL-B1-K`, `CL-B1-K-PESS` | `UNVERIFIED` |
| Stall angle of attack (elevons neutral α₀) | 11.6 | ° | `CL-B1-ALPHA-STALL` | `UNVERIFIED` |
| L/D max (at CL 0.69, ≈ 12.8 m/s) / at 16 m/s | 7.6 / 6.9 | — | `CL-B1-LDMAX`, `CL-B1-CRUISE-LD` | `UNVERIFIED` |

CD0 fell from 0.061 to 0.045. Rev 1 had a wing friction term of 0.018, and B2's S5010 section drag with the
tape-seam factor replaces it with 0.009. The fins are shorter (chord 0.275 m, not 0.40 m). The motor tubes are now the
largest item at 38 % of CD0. The trimmed lift curve B2 found has a slope of about 3.1 /rad from CL 0.5 to 0.7, and
it puts α about 1.5° above this model at the same CL. That moves the corridor pitch angles, not the powers.

## Stall and the transition gate

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Vs at 2.6 kg / 2.55 kg | 11.86 / 11.75 | m/s | `CL-B1-VS-GATE` (≤ 12, +1 %), `CL-B1-VS-SIZED` | `UNVERIFIED` |
| Vs in a 30° bank at 2.6 kg | 12.75 | m/s | `CALC-B1-STALL` | `UNVERIFIED` |
| 1.3 Vs at 2.6 kg | 15.42 | m/s | `CL-B1-VT-GATE` (≤ 16, +3.6 %) | `UNVERIFIED` |
| CLmax that would allow 15 m/s cruise | ≥ 0.85 | — | `CL-B1-CLMAX-FOR-15` | `UNVERIFIED` |

| Trimmed CLmax | Vs at 2.6 kg | 1.3 Vs | 16 m/s over 1.3 Vs |
|---|---|---|---|
| 0.80 (SM 5 %, design) | 11.89 m/s | 15.46 m/s | +3.5 % |
| 0.86 (SM 3 %) | 11.47 m/s | 14.91 m/s | +7.3 % |
| 0.90 | 11.21 m/s | 14.57 m/s | +9.8 % |

The margin is 0.58 m/s. B4's pitot error bound of 2 % (0.32 m/s) fits inside it. A2's `airspeed_err_max_ms` of 1.0
m/s does not. A 1 m/s high-reading sensor would end the transition at 15.0 m/s true, 0.97 × 1.3 Vs.

## Hover

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover power at 2.6 kg, used for the mission (pessimistic) | 400 (440) | W | `params.json#performance.hover_power_w` (E1) | `UNVERIFIED` |
| B1 cross-check: table × download × 11×5.5MR/11×4.5MR (1.019) | 387 | W | `CL-B1-HOVER-P-GATE` (≤ 400), `CL-B1-HOVER-PROP-RATIO` | `UNVERIFIED` |
| Current at 2.6 kg (B1 cross-check) | 26.1 | A | `CL-B1-HOVER-I-GATE` | `UNVERIFIED` |
| Hover-only endurance at 2.6 kg, 20 % reserve | 11.9 | min | `CL-B1-HOVER-ONLY` | `UNVERIFIED` |
| Hover thrust fraction, sagged pack, with download | 0.59 | — | `CL-B1-HOVER-THROTTLE` (≤ 0.60, +2 %) | `UNVERIFIED` |
| T/W with sag and download | 1.69 | — | `CL-B1-HOVER-TW-SAG` (≥ 1.6, +6 %) | `UNVERIFIED` |
| APC static figure of merit, 11×5.5MR | 0.72 | — | `CL-B1-FM` | `UNVERIFIED` |
| Vertical climb 2.5 m/s, power | 448 (30.3 A) | W | `CL-B1-VCLIMB-P` | `UNVERIFIED` |

The hover thrust fraction of 0.59 has almost no margin against 0.60. It rests on the worst-case sag of 0.72, which
assumes 20 % charge at 10 °C. With a fresh pack the fraction is 0.43.

## Transition corridor (level flight, 2.6 kg, worst-case pack)

![Transition corridor: pitch above horizon versus airspeed](fig-b1-corridor.svg)

`FIG B1-01 — Transition corridor, 2.6 kg. Blue line: steady level pitch, labelled with pack power. Shaded band:
pitch range that holds altitude within 80 % of available thrust (below the line the aircraft accelerates).`

| V (m/s) | Pitch, steady (°) | Pitch, lowest (°) | T/W | T / T_avail | P (W) | Wing |
|---|---|---|---|---|---|---|
| 0 | 90.0 | 44.3 | 1.06 | 0.59 | 387 | stalled |
| 3 | 84.0 | 42.0 | 1.00 | 0.56 | 359 | stalled |
| 6 | 67.1 | 36.6 | 0.93 | 0.55 | 367 | stalled |
| 9 | 46.5 | 30.8 | 0.75 | 0.51 | 357 | stalled |
| 11 | 35.2 | 26.7 | 0.62 | 0.49 | 348 | stalled |
| 12 | 11.0 | 9.8 | 0.13 | 0.13 | 126 | flying |
| 14 | 7.8 | 7.3 | 0.13 | 0.17 | 163 | flying |
| 16 | 5.7 | 5.7 | 0.14 | 0.26 | 214 | flying |
| 19 | 3.7 | 3.7 | 0.17 | 0.81 | 321 | flying |

| Corridor result | Value | Unit | Source | Status |
|---|---|---|---|---|
| Peak steady thrust fraction, 0–16 m/s (hover) | 0.59 | — | `CL-B1-CORR-THRUST` (≤ 0.80) | `UNVERIFIED` |
| Peak steady power, 0–16 m/s (hover) | 387 | W | `CL-B1-CORR-P-PEAK` | `UNVERIFIED` |
| Lowest speed where the unstalled wing holds level flight | 12 | m/s | `CL-B1-V-WINGBORNE` | `UNVERIFIED` |

### Pitch-over (forward transition), time simulation

2-D point mass. Pitch is rate-limited and never drops below the angle at which wing lift plus 80 % of thrust can
hold altitude. Thrust holds altitude below 1.1 Vs and holds speed above it.

| Pitch rate | To 1.3 Vs | To 16 m/s | Altitude lost | Peak thrust fraction, worst pack (fresh) | Energy |
|---|---|---|---|---|---|
| 10 °/s | 8.7 s | 9.5 s | 0.2 m | 0.72 (0.44) | 0.99 Wh |
| **12 °/s (proposed)** | **7.7 s** | **8.5 s** | **0.2 m** | **0.76 (0.47)** | **0.87 Wh** |
| 15 °/s | 6.6 s | 7.4 s | 0.2 m | 0.84 (0.51) | 0.77 Wh |
| 20 °/s (rev 1) | 5.5 s | 6.4 s | 0.1 m | 0.96 (0.59) | 0.66 Wh |
| 30 °/s | 4.8 s | 5.6 s | 0.0 m | 1.00 (0.75) | 0.59 Wh |

Claims: `CL-B1-TRANS-TIME` 7.66 s, `CL-B1-TRANS-ALT-LOSS` 0.21 m (≤ 10 m), `CL-B1-TRANS-THRUST` 0.765 (≤ 0.80),
`CL-B1-TRANS-ENERGY` 0.87 Wh. The forward transition normally happens early in a flight, when the pack is still
fresh. The 12 °/s figure covers the case where the aircraft has to transition again late in the flight on a cold,
low pack. Once logs show the real thrust headroom, F4 can raise the rate to 20 °/s for fresh-pack flights.

## Cruise and endurance

| Parameter (16 m/s, 2.6 kg) | Value | Unit | Source | Status |
|---|---|---|---|---|
| CL, L/D | 0.44, 6.93 | — | `CL-B1-CRUISE-LD` | `UNVERIFIED` |
| Drag with trim, base / pessimistic | 3.75 / 4.73 | N | `CL-B1-CRUISE-DRAG`, `-DRAG-PESS` | `UNVERIFIED` |
| J, rpm, η_prop (pessimistic η) | 0.58, 5 900, 0.43 (0.40) | —, rpm, — | `CL-B1-CRUISE-J`, `CL-B1-CRUISE-ETA-PROP` | `UNVERIFIED` |
| Shaft power, 4 props / drive efficiency (motor + ESC + calibration) | 141 / 0.66 | W, — | `CL-B1-CRUISE-P-SHAFT`, `CL-B1-CRUISE-ETA-DRIVE` | `UNVERIFIED` |
| **Pack power (pessimistic)** | **218 (285)** | W | `CL-B1-CRUISE-P`, `CL-B1-CRUISE-P-PESS` | `UNVERIFIED` |
| Pack power without the table calibration | 194 | W | `performance_results.json#sensitivity` | `MODELLED` |
| Current (pessimistic) | 14.7 (19.3) | A | `CL-B1-CRUISE-I`, `CL-B1-CRUISE-I-PESS` | `UNVERIFIED` |
| Energy: usable / hover 2 min / two transitions / left for cruise | 77.0 / 13.3 / 1.7 / 61.9 | Wh | `CALC-B1-MISSION`, `CL-B1-CRUISE-ENERGY` | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic)** | **17.0 (12.7)** | min | `CL-B1-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Same with B1's 387 W hover | 17.1 | min | `CL-B1-CRUISE-TIME-B1H` | `UNVERIFIED` |
| Range in that cruise | 16.3 | km | `CALC-B1-MISSION` | `MODELLED` |

Cross-checks at 15 m/s with the 11×5.5MR: B1 gives 191 W, B4 181–205 W (`CL-B4-CRUISE-W`) and E1 216 W
(lower bound 176 W). They agree within the spread of the calibration. E1's own claim now re-runs to 247 W at
16 m/s because it uses L/D 5.6 from rev 1. Scaled to B1's L/D of 6.9, it drops to roughly 200 W (CR-B1-11).

![Cruise time after the 2 min hover versus cruise speed](fig-b1-endurance.svg)

`FIG B1-02 — Cruise time after 2 min hover, 2.6 kg, 20 % reserve. Red band: speeds below 1.3 Vs, which the
transition requirement does not allow.`

| V (m/s) | 14 | 15 | 16 | 17 | 18 | 20 |
|---|---|---|---|---|---|---|
| Power, base / pessimistic (W) | 168 / 218 | 191 / 249 | 218 / 285 | 250 / 327 | 285 / 375 | 370 / 490 |
| η_prop | 0.46 | 0.44 | 0.43 | 0.41 | 0.40 | 0.39 |
| Cruise time, base / pessimistic (min) | 22.2 / 16.6 | 19.4 / 14.6 | 17.0 / 12.7 | 14.9 / 11.1 | 13.0 / 9.7 | 10.0 / 7.4 |

Each extra 1 m/s costs about 14 % in power and 2 min of cruise. The lowest-power speed in this band is at its
lower edge (`CL-B1-V-MINPOWER` 14 m/s), so the transition rule, not the airframe, sets the cruise speed.

## Climb, top speed, wind

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fixed-wing climb at 16 m/s, 80 % thrust, worst pack | 4.7 (17°) | m/s | `CL-B1-ROC-FW` | `UNVERIFIED` |
| Top level speed, worst pack (prop thrust runs out near J 0.64) | 19.3 | m/s | `CL-B1-VMAX` (≥ 18, +7 %) | `UNVERIFIED` |
| Hover lean, flat plate, 5 / 8 m/s | 15.8 / 35.9 | ° | `CL-B1-LEAN-5MS`, `CALC-B1-WIND` | `UNVERIFIED` |
| Hover lean with wing lift counted, 5 / 8 m/s | 16.3 / 36.9 | ° | `CL-B1-LEAN-5MS-LIFT`, `CALC-B1-CORRIDOR` | `UNVERIFIED` |
| Lean allowed at touchdown (tip-over 30.6° − 10° error) | 20.6 | ° | `CL-B1-LEAN-ALLOWED` | `UNVERIFIED` |
| Steady wind for a fin-tip landing | 5.8 | m/s | `CL-B1-WIND-HOVER-MAX` (≥ 5, +15 %) | `UNVERIFIED` |
| Thrust fraction holding the 8 m/s gust lean | 0.73 | — | `CL-B1-GUST-8-THRUST` (≤ 0.80, +9 %) | `UNVERIFIED` |
| Wind that tips the parked aircraft (motors off, 2.15 kg) | 8.2 | m/s | `CL-B1-GROUND-TIP-WIND` (≥ 8, +3 %) | `UNVERIFIED` |
| Upwind ground speed at 16 m/s in 5 m/s wind | 11 | m/s | `CALC-B1-WIND` | `MODELLED` |

The wind limits got tighter in rev 2 for three reasons: the R1 tip-over angle is 30.6° (rev 1 used 37.2°), the
wing is larger, and the feet are taller. The 5 m/s flight-card limit still holds, with 0.8 m/s to spare at
landing. A parked aircraft tips over in 8.2 m/s, so the card should require laying it flat between flights in
gusty wind (CR-C1-02). Splaying the feet (C5) is the lever on both numbers.

## First-flight values for F4

| Parameter | Value | Basis |
|---|---|---|
| `AIRSPEED_CRUISE` | 16 m/s | `ASM-B1-VCRUISE`, 1.3 Vs 15.42 m/s |
| `AIRSPEED_MIN` | 15 m/s | 1.26 Vs at the gate (wings level); TECS floor, not the transition end |
| `AIRSPEED_MAX` | 18 m/s | Vmax 19.3 m/s on the worst pack, 1.3 m/s headroom |
| Transition-complete airspeed | ≥ 15.5 m/s | `CL-B1-VT-GATE`; F4 maps it to the firmware's end-of-transition criterion |
| `Q_ASSIST_SPEED` | 13 m/s | 1.10 Vs (`ASM-B1-TRANS`) |
| `Q_TAILSIT_RAT_FW` | 12 °/s | `CL-B1-TRANS-THRUST` 0.76 on the worst pack |
| `TECS_CLMB_MAX` | 3 m/s | `CL-B1-ROC-FW` 4.7 m/s at 80 % thrust |

## How to verify (planned tests)

| Test | Verifies | Owner |
|---|---|---|
| `T-B1-TETHER-HOVER`: gate mass by ballast, 60 s tethered hover, pack W and throttle | hover power, throttle | H2 (after H1 thrust stand) |
| `T-B1-CRUISE-POWER`: 60 s legs at 14, 16, 18 m/s both ways, calm morning, airspeed, V, A, ESC rpm | cruise power, CD0, η_prop | H2 (twin first) |
| `T-B1-TRANSITION-LOG`: first transitions at ≥ 50 m, airspeed, pitch, altitude, throttle | corridor, pitch-over | H2, F4 SITL first |

## Limits of this analysis

- Steady 2-D model. It ignores prop normal force, edgewise inflow, slipstream over the wing and the pitch-moment
  balance. B3 owns the pitch moment. The elevons get no prop wash, so at low airspeed pitch control comes from
  differential thrust alone.
- B2's e, wing CD0 and lift slope come from a c 0.30 (AR 3.83) run. k already uses the R1 AR of 3.59. The AVL
  lift slope is about 3 % high for AR 3.59 (Helmbold ratio 3.69/3.81). B2/B3 re-run at R1.
- Hover comes from the 11×4.7 maker table, scaled to the 11×5.5MR by the APC model ratio. Cruise uses APC's
  predicted 11×5.5MR data with the same table calibration. The H1 thrust stand replaces both.
- All numbers are at 2.6 kg unless marked. Outputs, tables, sensitivities and time histories are in
  `performance_results.json`.
