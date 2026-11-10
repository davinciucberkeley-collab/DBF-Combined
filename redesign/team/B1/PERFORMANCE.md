# K09-L whole-aircraft performance

> Simulation round (2026-11-10): the as-designed re-run is in `SIMULATION-REPORT.md` (claims `CL-B1V-*`). It
> replaces this rev 3 hand-estimate report for current values: CD0 0.0579, cruise 235 W, 16.2 min, VH 21.0 m/s at
> THR_MAX 70 %. This report stays as the hand calculation the simulations are compared against.

Status: `MODELLED` (B1, rev 3, 2026-11-09, answers CR-A1-30). Rev 3 adds five changes to the model:

- the pressure drag of the 0.14 m pod (D-25)
- the fin braces and station collars (C4 CR-C4-08, D3 CR-D3-15)
- sag 0.76 (D-35)
- the R2 fins: 0.21 m half-height and 0.344 m tubes (D-26)
- a motor-limited full-throttle model, which gives the top speed at F4's 9 350 rpm cap (C1 CR-C1-14)

Claim ids are unchanged. Re-check: `python -I redesign/team/B1/performance.py`, then
`python -I redesign/proofs/build_graph.py`.

**Verdict.** The new drag items add 10 W, so cruise at 16 m/s now takes **228 W** (301 W pessimistic). That leaves
**16.3 min** of cruise after the 2 min hover (12.0 min pessimistic), against a 5 min requirement. At sag 0.76 the
hover thrust fraction is 0.56, and the 12 °/s pitch-over peaks at 0.70 of available thrust. The rate therefore stays
at **12 °/s**, with margin. **The top level speed at the rpm cap is 25.7 m/s, not the 21.8 m/s pitch-speed proxy.**
C1's VD therefore becomes 32.1 m/s, unless F4 caps fixed-wing rpm at about 7 950 (CR-B1-17).

## What changed from rev 2

| Item | Rev 2 | Rev 3 | Unit | Why |
|---|---|---|---|---|
| CD0 | 0.0452 | 0.0513 | — | pod front +0.0018, braces +0.0045, collars +0.0017; tubes 0.42 → 0.344 m (−0.0031); fins 0.21 m (+0.0012) |
| Cruise drag / L/D | 3.75 / 6.93 | 4.10 / 6.34 | N, — | as CD0 |
| Cruise power (pessimistic) | 218 (285) | 228 (301) | W | as CD0; η_prop rises 0.43 → 0.44 at the higher thrust |
| Cruise after hover (pessimistic) | 17.0 (12.7) | 16.3 (12.0) | min | as above |
| Hover thrust fraction / T/W, sagged | 0.59 / 1.69 | 0.56 / 1.79 | — | sag 0.72 → 0.76 |
| Pitch-over peak at 12 °/s | 0.76 | 0.70 | — | sag 0.76 |
| Top level speed (`CL-B1-VMAX`) | 19.3 | 25.7 | m/s | rpm cap; in forward flight the prop unloads and speeds up |
| FW climb at 16 m/s, 80 % thrust (`CL-B1-ROC-FW`) | 4.7 | 13.7 | m/s | same motor model: 8 530 rpm (limiter-bound) at 16 m/s, not the static 7 200 |
| Vs / 1.3 Vs | 11.86 / 15.42 | 11.91 / 15.48 | m/s | B2's re-run trimmed CLmax and α₀ (stall α 12.0°) |
| Parked tip-over wind | 8.2 | 8.9 | m/s | lightest flying mass 2.15 → 2.32 kg (D-38 allocations) |

## Inputs and assumptions

| Item | Value | Unit | Source | Status |
|---|---|---|---|---|
| Mass: gate / sized / lightest flying | 2.600 / 2.590 / 2.318 | kg | `params.json#requirements`, `CL-A1-MASS-SIZED`, sized − growth reserve | `PROPOSED` |
| Wing S, AR | 0.368, 3.59 | m², — | `CL-A1-WING-AREA`, `params.json#wing` (c 0.32) | `PROPOSED` |
| Wing profile drag × tape-seam factor | 0.00685 × 1.10 | — | `P:b2.avl.cd0_wing`, `ASM-B1-WING-ROUGH` | `UNVERIFIED` |
| Oswald e: base / pessimistic | 0.94 / 0.80 | — | `P:b2.avl.e_oswald`, `params.json#wing.oswald_e` | `UNVERIFIED` |
| Lift slope, α₀, trimmed CLmax | 3.48 /rad, −1.17°, 0.80 | — | `P:b2.avl.cla_per_rad`, `P:b2.xfoil.alpha0_2d_deg`, `CL-B2-CLMAX-DESIGN` | `UNVERIFIED` |
| Non-wing drag build-up | Cf 0.007, FF fin 1.20 / pod 1.30, tube Cd 0.30, CdA 0.0004 m² per motor, IF 1.15 | — | `ASM-B1-DRAG` | `UNVERIFIED` |
| Pod widening 0.10 → 0.14 m: Cd on the added frontal area | 0.20 | — | `ASM-B1-POD-FRONT` (D-25) | `PROPOSED` |
| Braces 4 × 0.15 m × 3 mm, Cd 0.80; collars 4 × Ø 26 × 12 mm, Cd 0.70 | 0.23 + 0.09 at 16 m/s (before IF) | N | `ASM-B1-DRAG-ADDONS` (D3 CR-D3-15, C4 CR-C4-08) | `PROPOSED` |
| Trim drag factor | 1.02 | — | `ASM-B1-TRIM` | `PROPOSED` |
| Post-stall wing | CN = 1.28 sin α, 4° e-fold from CLmax | — | `ASM-B1-CD90` | `PROPOSED` |
| Prop Ct(J), Cp(J) | APC PER3 11×5.5MR, 6 000 rpm | — | `ASM-B1-PROP` | `PROPOSED` |
| Motor Kv, Rm, I₀ / chain calibration | 900, 0.086, 0.9 / 1.13 | rpm/V, Ω, A / — | `ASM-E1-KV`, `-RM`, `-I0`, `CL-B1-KCAL` | `UNVERIFIED` |
| Static full thrust per motor × sag | 1.62 kg × 0.76 | — | `params.json#propulsion` (E1, E2, D-35) | `UNVERIFIED` |
| Full throttle in flight: terminal V fresh / worst, limiter share, rpm cap | 16.0 / 13.6, 24.8, 9 350 | V, A, rpm | `ASM-B1-VTERM`, `P:propulsion.current_max_per_motor_a`, `P:propulsion.rpm_max` | `PROPOSED` |
| Hover download, ESC η, avionics | 1.06, 0.95, 6 | —, —, W | `params.json#propulsion.download_factor`, `ASM-B1-ESC`, `ASM-B1-AVIONICS-W` | `PROPOSED` |
| Mission hover power (pessimistic × 1.10) | 400 (440) | W | `params.json#performance.hover_power_w` (E1), `ASM-B1-PESS` | `UNVERIFIED` |
| Pessimistic case | CD0 × 1.3, e 0.80, η_prop × 0.85, hover and transition × 1.10 | — | `ASM-B1-PESS` | `PROPOSED` |
| Steady thrust allowed (20 % control reserve) | 0.80 of available, sagged | — | `ASM-B1-CTRL-RESERVE` | `PROPOSED` |
| Pack energy, reserve | 96.2, 20 % | Wh | `params.json#battery`, `#requirements` | `UNVERIFIED` |

## Aerodynamics

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| CD0: wing 0.0087 · fins 0.0124 · tubes 0.0142 · motors 0.0050 · pod 0.0031 + front 0.0018 · braces 0.0045 · collars 0.0017 | 0.0513 | — | `CL-B1-CD0` | `UNVERIFIED` |
| Pod widening, friction + front | +0.0024 (0.14 N, 3.4 % of cruise drag) | — | `CALC-B1-AERO` `d_cd0_pod_wide` | `MODELLED` |
| Braces + collars | +0.0062 (0.37 N, 9 % of cruise drag) | — | `CALC-B1-AERO` `d_cd0_braces_collars` | `MODELLED` |
| k, base / pessimistic | 0.0943 / 0.1107 | — | `CL-B1-K`, `CL-B1-K-PESS` | `UNVERIFIED` |
| Stall angle of attack | 12.0 | ° | `CL-B1-ALPHA-STALL` | `UNVERIFIED` |
| L/D max (CL 0.74) / at 16 m/s | 7.2 / 6.3 | — | `CL-B1-LDMAX`, `CL-B1-CRUISE-LD` | `UNVERIFIED` |

The pod check agrees with D-25: widening the pod adds 3.4 % of cruise drag, against D-25's estimate of 3 %. The
braces matter more. At Cd 0.80 they give 0.23 N before interference, which is the top of C4's 0.07–0.24 N range. A
rounded or elliptical brace section (Cd about 0.4) would save about 0.13 N. That is 7 W, or 0.5 min of cruise
(CR-B1-18).

## Stall and the transition gate

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Vs at 2.6 kg / 2.59 kg | 11.91 / 11.89 | m/s | `CL-B1-VS-GATE` (≤ 12, +1 %), `CL-B1-VS-SIZED` | `UNVERIFIED` |
| Vs in a 30° bank at 2.6 kg | 12.80 | m/s | `CALC-B1-STALL` | `UNVERIFIED` |
| 1.3 Vs at 2.6 kg | 15.48 | m/s | `CL-B1-VT-GATE` (≤ 16, +3.4 %) | `UNVERIFIED` |
| CLmax that would allow 15 m/s cruise | ≥ 0.85 | — | `CL-B1-CLMAX-FOR-15` | `UNVERIFIED` |

The gap from 1.3 Vs up to the 16 m/s cruise is 0.52 m/s. Params set the transition minimum at 15.6 m/s (B3, at the
forward CG limit) and the airspeed error allowance at 0.5 m/s (D-37).

## Hover

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover power at 2.6 kg, used for the mission (pessimistic) | 400 (440) | W | `params.json#performance.hover_power_w` (E1) | `UNVERIFIED` |
| B1 cross-check: table × download × 11×5.5MR/11×4.5MR (1.019) | 387 | W | `CL-B1-HOVER-P-GATE` (≤ 400) | `UNVERIFIED` |
| Current at 2.6 kg (B1 cross-check) | 26.1 | A | `CL-B1-HOVER-I-GATE` | `UNVERIFIED` |
| Hover-only endurance at 2.6 kg, 20 % reserve | 11.9 | min | `CL-B1-HOVER-ONLY` | `UNVERIFIED` |
| **Hover thrust fraction, sag 0.76, with download** | **0.56** (fresh 0.43) | — | `CL-B1-HOVER-THROTTLE` (≤ 0.60, +7 %) | `UNVERIFIED` |
| T/W with sag and download | 1.79 | — | `CL-B1-HOVER-TW-SAG` (≥ 1.6, +12 %) | `UNVERIFIED` |
| Full-throttle prop speed, static, worst pack | 120.1 | rev/s | `CL-B1-NMAX-SAG` | `UNVERIFIED` |
| APC static figure of merit, 11×5.5MR | 0.72 | — | `CL-B1-FM` | `UNVERIFIED` |
| Vertical climb 2.5 m/s, power | 448 (30.3 A) | W | `CL-B1-VCLIMB-P` | `UNVERIFIED` |

With E1's sag of 0.854 the hover fraction would be 0.50. The cold-pack stand run (CR-B1-16) settles which is right.

## Transition corridor (level flight, 2.6 kg, worst-case pack)

![Transition corridor: pitch above horizon versus airspeed](fig-b1-corridor.svg)

`FIG B1-01 — Transition corridor, 2.6 kg. Blue line: steady level pitch, labelled with pack power. Shaded band:
pitch range that holds altitude within 80 % of available thrust (below the line the aircraft accelerates).`

| V (m/s) | Pitch, steady (°) | Pitch, lowest (°) | T/W | T / T_avail | P (W) | Wing |
|---|---|---|---|---|---|---|
| 0 | 90.0 | 41.5 | 1.06 | 0.56 | 387 | stalled |
| 3 | 84.0 | 39.2 | 1.00 | 0.53 | 359 | stalled |
| 6 | 67.0 | 34.5 | 0.93 | 0.52 | 367 | stalled |
| 9 | 46.4 | 29.4 | 0.75 | 0.48 | 358 | stalled |
| 11 | 35.1 | 25.6 | 0.62 | 0.46 | 350 | stalled |
| 12 | 11.4 | 9.9 | 0.14 | 0.13 | 130 | flying |
| 14 | 8.2 | 7.7 | 0.14 | 0.16 | 169 | flying |
| 16 | 6.0 | 5.7 | 0.16 | 0.25 | 223 | flying |
| 19 | 3.9 | 3.9 | 0.19 | 0.67 | 337 | flying |

In the corridor and the pitch-over, T_avail uses the static full-throttle speed (`CL-B1-NMAX-SAG`). Above about
10 m/s this understates the thrust, so the fractions at speed are conservative. The peaks occur near hover, where
the static value holds.

| Corridor result | Value | Unit | Source | Status |
|---|---|---|---|---|
| Peak steady thrust fraction, 0–16 m/s (hover) | 0.56 | — | `CL-B1-CORR-THRUST` (≤ 0.80) | `UNVERIFIED` |
| Peak steady power, 0–16 m/s (hover) | 387 | W | `CL-B1-CORR-P-PEAK` | `UNVERIFIED` |
| Lowest speed where the unstalled wing holds level flight | 12 | m/s | `CL-B1-V-WINGBORNE` | `UNVERIFIED` |

### Pitch-over (forward transition), time simulation, sag 0.76

| Pitch rate | To 1.3 Vs | To 16 m/s | Altitude lost | Peak thrust fraction, worst pack (fresh) | Energy |
|---|---|---|---|---|---|
| 10 °/s | 8.9 s | 9.6 s | 0.1 m | 0.66 (0.44) | 0.99 Wh |
| **12 °/s (proposed)** | **7.8 s** | **8.5 s** | **0.2 m** | **0.70 (0.47)** | **0.88 Wh** |
| 14 °/s | 7.0 s | 7.7 s | 0.1 m | 0.75 (0.50) | 0.80 Wh |
| 16 °/s (ceiling at 0.80) | 6.5 s | 7.2 s | 0.1 m | 0.79 (0.53) | 0.75 Wh |
| 20 °/s | 5.7 s | 6.4 s | 0.1 m | 0.88 (0.59) | 0.67 Wh |
| 30 °/s | 4.8 s | 5.4 s | 0.0 m | 1.00 (0.75) | 0.59 Wh |

Claims: `CL-B1-TRANS-TIME` 7.80 s, `CL-B1-TRANS-ALT-LOSS` 0.15 m (≤ 10 m), `CL-B1-TRANS-THRUST` 0.70 (≤ 0.80),
`CL-B1-TRANS-ENERGY` 0.88 Wh. At sag 0.76, 16 °/s is the fastest rate that stays within 0.80, but it has no
margin. The sag is still `UNVERIFIED` (E2 0.76, E1 0.854), so B1 keeps **12 °/s** for first flights. F4 may raise
it to 15 °/s once the cold-pack stand run confirms a sag of at least 0.76.

## Cruise and endurance

| Parameter (16 m/s, 2.6 kg) | Value | Unit | Source | Status |
|---|---|---|---|---|
| CL, L/D | 0.44, 6.34 | — | `CL-B1-CRUISE-LD` | `UNVERIFIED` |
| Drag with trim, base / pessimistic | 4.10 / 5.20 | N | `CL-B1-CRUISE-DRAG`, `-DRAG-PESS` | `UNVERIFIED` |
| J, rpm, η_prop (pessimistic η) | 0.58, 5 940, 0.44 (0.42) | —, rpm, — | `CL-B1-CRUISE-J`, `CL-B1-CRUISE-ETA-PROP` | `UNVERIFIED` |
| Shaft power, 4 props / drive efficiency | 148 / 0.67 | W, — | `CL-B1-CRUISE-P-SHAFT`, `CL-B1-CRUISE-ETA-DRIVE` | `UNVERIFIED` |
| **Pack power (pessimistic)** | **228 (301)** | W | `CL-B1-CRUISE-P`, `CL-B1-CRUISE-P-PESS` | `UNVERIFIED` |
| Pack power without the table calibration | 202 | W | `performance_results.json#sensitivity` | `MODELLED` |
| Current (pessimistic) | 15.4 (20.3) | A | `CL-B1-CRUISE-I`, `CL-B1-CRUISE-I-PESS` | `UNVERIFIED` |
| Energy: usable / hover 2 min / two transitions / left for cruise | 77.0 / 13.3 / 1.8 / 61.9 | Wh | `CALC-B1-MISSION`, `CL-B1-CRUISE-ENERGY` | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic)** | **16.3 (12.0)** | min | `CL-B1-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Same with B1's 387 W hover | 16.4 | min | `CL-B1-CRUISE-TIME-B1H` | `UNVERIFIED` |
| Range in that cruise | 15.6 | km | `CALC-B1-MISSION` | `MODELLED` |

![Cruise time after the 2 min hover versus cruise speed](fig-b1-endurance.svg)

`FIG B1-02 — Cruise time after 2 min hover, 2.6 kg, 20 % reserve. Red band: speeds below 1.3 Vs, which the
transition requirement does not allow.`

| V (m/s) | 14 | 15 | 16 | 17 | 18 | 20 |
|---|---|---|---|---|---|---|
| Power, base / pessimistic (W) | 174 / 228 | 199 / 262 | 228 / 301 | 261 / 346 | 299 / 397 | 389 / 520 |
| η_prop | 0.48 | 0.46 | 0.44 | 0.43 | 0.42 | 0.41 |
| Cruise time, base / pessimistic (min) | 21.4 / 15.9 | 18.7 / 13.8 | 16.3 / 12.0 | 14.2 / 10.5 | 12.4 / 9.1 | 9.5 / 7.0 |

## Climb and top speed

Rev 3 solves full throttle in forward flight with E1's motor model. The prop runs at the lowest of three speeds:

- the speed at which back-EMF plus I·Rm uses the whole terminal voltage
- the speed at which the motor reaches its 24.8 A share of the limiter
- F4's 9 350 rpm cap

Rev 2 used the static full-throttle speed (7 000–7 200 rpm) at every airspeed. That is right in hover. In forward
flight it is too low, because the prop unloads and speeds up.

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| **Top level speed at the 9 350 rpm cap, fresh pack (C1's VH)** | **25.7** | m/s | `CL-B1-VMAX` (≥ 18) | `UNVERIFIED` |
| Same, worst-state pack (the cap still binds: 11.6 V needed, 13.6 V available) / with pessimistic drag | 25.7 / 25.2 | m/s | `CL-B1-VMAX-SAG` | `UNVERIFIED` |
| Dynamic pressure at VH | 404 | Pa | `CALC-B1-CLIMB` | `MODELLED` |
| Geometric pitch speed at the cap (C1's proxy) / APC zero-thrust speed at the cap | 21.8 / 27.8 | m/s | `CALC-B1-CLIMB` | `MODELLED` |
| Top level speed if the cap fails (voltage-limited at 12 550 rpm, above APC's 9 545 rpm limit) | 34.5 | m/s | `CL-B1-VMAX-NOCAP` | `UNVERIFIED` |
| Full throttle at 16 m/s, worst pack: prop speed, thrust | 8 530 (limiter-bound), 32.3 | rpm, N | `CALC-B1-CLIMB` | `MODELLED` |
| Fixed-wing climb at 16 m/s, 80 % thrust (flight path 59°) | 13.7 | m/s | `CL-B1-ROC-FW` | `UNVERIFIED` |

| Fixed-wing rpm cap (rpm) | 7 500 | 8 000 | 8 200 | 8 400 | 8 590 | 9 000 | 9 350 |
|---|---|---|---|---|---|---|---|
| Top level speed (m/s) | 20.5 | 21.9 | 22.5 | 23.0 | 23.6 | 24.7 | 25.7 |

The 21.8 m/s proxy assumes the props stop producing thrust at the 5.5 in geometric pitch. APC's data put zero
thrust at J 0.64 instead, which is 27.8 m/s at the cap. With CD0 0.051 the drag at 25 m/s is only about 8 N, so
the props still have thrust to spare at that speed. VH is therefore 25.7 m/s. With VD = 1.25 VH, VD is 32.1 m/s,
and q at VD is 631 Pa against the 454 Pa used now. There are two ways to deal with this (CR-B1-17):

- C1 re-runs the loads at the higher VD.
- F4 adds a fixed-wing rpm cap of about 7 950 rpm, or the equivalent THR_MAX, which holds VH at 21.8 m/s.

The 7 950 rpm cap would apply in fixed-wing mode only. It still leaves 21 m/s of level speed against `AIRSPEED_MAX` 18.

## Wind

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover lean, flat plate, 5 / 8 m/s | 15.8 / 35.9 | ° | `CL-B1-LEAN-5MS`, `CALC-B1-WIND` | `UNVERIFIED` |
| Hover lean with wing lift counted, 5 m/s | 16.4 | ° | `CL-B1-LEAN-5MS-LIFT` | `UNVERIFIED` |
| Lean allowed at touchdown (tip-over 30.6° − 10° error) | 20.6 | ° | `CL-B1-LEAN-ALLOWED` | `UNVERIFIED` |
| Steady wind for a fin-tip landing | 5.8 | m/s | `CL-B1-WIND-HOVER-MAX` (≥ 5, +15 %) | `UNVERIFIED` |
| Thrust fraction holding the 8 m/s gust lean | 0.69 | — | `CL-B1-GUST-8-THRUST` (≤ 0.80, +14 %) | `UNVERIFIED` |
| Wind that tips the parked aircraft (motors off, 2.32 kg) | 8.9 | m/s | `CL-B1-GROUND-TIP-WIND` (≥ 8, +11 %) | `UNVERIFIED` |

## First-flight values for F4

| Parameter | Value | Basis |
|---|---|---|
| `AIRSPEED_CRUISE` | 16 m/s | `ASM-B1-VCRUISE`, 1.3 Vs 15.48 m/s |
| `AIRSPEED_MIN` | 15.6 m/s | params `performance.transition_min_ms` (D-36) |
| `AIRSPEED_MAX` | 18 m/s | elevon schedule, full travel to VA 20.5 m/s (D-29); Vmax 25.7 m/s at the cap |
| `Q_ASSIST_SPEED` | 13 m/s | 1.10 Vs (`ASM-B1-TRANS`) |
| `Q_TAILSIT_RAT_FW` | 12 °/s | `CL-B1-TRANS-THRUST` 0.70 at sag 0.76; 16 °/s is the ceiling |
| `TECS_CLMB_MAX` | 3 m/s | `CL-B1-ROC-FW` 13.7 m/s at 80 % thrust |
| Fixed-wing rpm or THR_MAX cap | about 7 950 rpm | holds VH ≤ 21.8 m/s if C1 keeps VD 27.2 (CR-B1-17) |

## How to verify (planned tests)

| Test | Verifies | Owner |
|---|---|---|
| `T-B1-TETHER-HOVER`: gate mass by ballast, 60 s tethered hover, pack W and throttle | hover power, throttle | H2 (after H1 thrust stand) |
| `T-B1-CRUISE-POWER`: 60 s legs at 14, 16, 18 m/s both ways, calm morning, airspeed, V, A, ESC rpm | cruise power, CD0, η_prop | H2 (twin first) |
| `T-B1-TRANSITION-LOG`: first transitions at ≥ 50 m, airspeed, pitch, altitude, throttle | corridor, pitch-over | H2, F4 SITL first |

## Limits of this analysis

- The model is steady and 2-D. It ignores prop normal force, edgewise inflow, slipstream over the wing and the
  pitch-moment balance, which B3 owns.
- Brace and collar drag come from a hand build-up. The braces sit partly in the prop disc (z 0.05–0.33 m). The
  slipstream increment in cruise is ignored, because cruise thrust is only about 1 N per prop.
- The top speed rests on two weak inputs. APC's predicted Ct near zero thrust (J 0.55–0.64) is the least certain
  part of the PER3 file. The drag polar is used 60 % above cruise speed (Re 5 × 10⁵). Treat 25.7 m/s as ± 1.5 m/s.
- B2's e and wing CD0 come from the props-off run without the pod. CR-B1-15 stays open.
- All numbers are at 2.6 kg unless marked. Tables, sensitivities and the time history are in
  `performance_results.json`.
