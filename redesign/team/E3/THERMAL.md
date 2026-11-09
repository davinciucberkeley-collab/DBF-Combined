# Thermal — motors, mounts, ESCs, pack and avionics (K09-L)

Revision **E3-R2**, 2026-11-09. Every number comes from `team/E3/thermal.py` → `team/E3/claims.json` (31 claims) and
`team/E3/thermal_results.json`. Every temperature is `UNVERIFIED` until `T-E3-MOTOR-TAU`, `T-E3-ESC-PAD` (both in H1's
GT-04) and `T-E2-IR` have run, because three inputs are estimates: motor thermal resistance, ESC wake factor and
pack resistance.

**Verdict.** With ASA motor mounts and ESC pads and the two pod vents, every part stays inside its rating over the
whole mission from 15 to 30 °C ambient. Smallest margin: the pack lands at 47.1 °C on a 30 °C day against 50 °C
for life. The field-ambient ceiling is **43 °C** (41 °C for a hover-only sortie), so **no ambient restriction is
needed**. Three things still need action:

1. **PETG fails** for the motor mounts (base 65.8 °C against an allowed 58 °C) and, now that the ESC sits under a
   strap on D3's pad, for the ESC pads too (61.6 °C against 58 °C).
2. **Continuous full throttle has to stop after 10 s.** The motor reaches 80 °C after 13.6 s.
3. **The pack goes in at 34 °C or cooler.**

R2 changes: the ESC pad moved to D3's layout (72 mm from the motor axis, was 60 mm) and the hook-and-loop strap
area is no longer credited for cooling. Together they put the ESC up 5 K. R2 adds the 15–30 °C sweep and the GT-04
pass lines (CR-H1-06).

## Temperatures across the field ambient (full mission, vented pod)

Design case: E2 pessimistic currents (2.6 kg, 5 m/s wind), motor R_th 1.5 K/W, ESC wake factor 0.5, 5.0 mΩ/cell.
Nominal case: E2 base currents, E1's 1.0 K/W, wake factor 0.7, 4.0 mΩ/cell. The pack starts at ambient.

| Ambient | Motor peak | ESC peak | Pack at landing | FC peak | Pod air peak | Claim |
|---|---|---|---|---|---|---|
| 15 °C, design / nominal | 49.7 / 34.9 | 47.3 / 39.9 | 33.0 / 26.7 | 42.7 / 40.0 | 29.9 / 25.6 | `CL-E3-SWEEP-DES` / `-NOM` |
| 20 °C | 55.1 / 40.1 | 52.1 / 44.7 | 37.3 / 31.0 | 47.4 / 44.6 | 34.6 / 30.2 | same |
| 25 °C | 60.5 / 45.3 | 56.8 / 49.6 | 42.1 / 35.8 | 52.2 / 49.5 | 39.4 / 35.1 | same |
| 30 °C | 65.8 / 50.6 | 61.6 / 54.4 | 47.1 / 40.8 | 57.0 / 54.3 | 44.4 / 40.1 | same |
| **Limit** | 80 | 85 | 50 life (60 rating) | 85 | — | `ASM-E3-LIMITS` |

All values in °C. The temperature rise above ambient barely depends on ambient: between 15 and 30 °C the motor rise
changes by +1.1 K and the ESC rise by −0.8 K (`CL-E3-RISE-AMB-INDEP`). Any stand or field reading therefore scales
to 30 °C by adding (30 − T_amb). On a 15 °C morning with the pack first warmed to 20 °C (E2's rule), the pack lands
at 35.6 °C (`CL-E3-PACK-15-WARMED`).

## Limits and margins at 30 °C (top of the range, design case)

| Part | Case | Value | Limit | Margin | Claim | Status |
|---|---|---|---|---|---|---|
| Motor stator / winding | mission peak (end of descent, 723 s) | 65.8 °C | 80 °C | +14 K | `CL-E3-MOTOR-PEAK` | `UNVERIFIED` |
| Motor | continuous hover, steady | 66.4 °C | 80 °C | +14 K | `CL-E3-MOTOR-STEADY` | `UNVERIFIED` |
| Motor mount, **PETG** | mission peak | 65.8 °C | 58 °C (HDT 68 − 10 K) | **−8 K** | `CL-E3-MOUNT-PETG` | `FAILS` |
| Motor mount, ASA | hover-only sortie | 66.3 °C | 83 °C (HDT 93 − 10 K) | +17 K | `CL-E3-MOUNT-ASA` | `UNVERIFIED` |
| ESC on its fin pad | mission peak | 61.6 °C | 85 °C (MCU) | +23 K | `CL-E3-ESC-PEAK` | `UNVERIFIED` |
| ESC pad, **PETG** | mission peak (pad taken at the ESC) | 61.6 °C | 58 °C | **−4 K** | `CL-E3-ESC-PAD-PETG` | `FAILS` |
| ESC | + 30 s at the 100 A limiter | 78.7 °C | 85 °C | +6 K | `CL-E3-ESC-ABUSE` | `UNVERIFIED` |
| Motor | + 30 s at the 100 A limiter | 102.2 °C | 80 °C | −22 K | `CL-E3-MOTOR-ABUSE` | burst rule below |
| Pack | at landing, vented / sealed pod | 47.1 / 49.3 °C | 50 °C life | +3 K / +1 K | `CL-E3-PACK-END` | `UNVERIFIED` |
| Flight controller | mission, vented / sealed | 57.0 / 70.3 °C | 85 °C | +28 K / +15 K | `CL-E3-FC-PEAK` | `UNVERIFIED` |
| Flight controller | hover-only sortie (9.4 min, no ram air) | 70.7 °C | 85 °C | +14 K | `CL-E3-FC-HOVERONLY` | `UNVERIFIED` |

With PETG mounts the mount limit (58 °C) is reached at about 22 °C ambient. ASA mounts and pads remove that limit
and cost nothing extra.

## Field-ambient ceiling (output for P19 / `R-THERMAL`)

The ceiling is the highest ambient at which a part reaches its limit. It is found by bisection on the full model,
with the pack starting at ambient. Values in °C.

| Sortie | Motor 80 | ESC 85 | Pack 60 | Pack 50 at landing | FC 85 | ASA 93 | PETG 68 | **Ceiling (ASA)** | Claim |
|---|---|---|---|---|---|---|---|---|---|
| Full mission, design | 43.2 | 54.7 | 43.0 | 32.9 | 58.7 | 55.2 | 32.0 | **43.0** | `CL-E3-CEIL-MISSION` |
| Full mission, nominal | 58.2 | 61.7 | 49.3 | 39.2 | 61.6 | 70.7 | 46.7 | 49.3 | — |
| Hover-only to the 20 % line, design | 42.7 | 51.9 | 41.3 | 31.3 | 45.4 | 54.7 | 31.5 | **41.3** | `CL-E3-CEIL-HOVERONLY` |

The RFS morning window (07–10 h, March–April) is far below 41 °C. The only ambient-linked rule is the pack-start
rule: it keeps the pack at or below 50 °C on landing above about 33 °C, and with a pack heated in the car.

## Heat sources per station

| Phase (design) | Motor current | Motor loss | ESC loss | Air speed at the ESC | Source |
|---|---|---|---|---|---|
| Hover (E2 pessimistic, 103 W bus) | 14.0 A | 22.3 W at 25 °C, 24.5 W at 70 °C | 2.4 W | 10.9 m/s slipstream × 0.5 | `CL-E3-HOVER-LOSS` |
| Forward transition | 17.3 A | 31.8 W | 3.5 W | 12.2 m/s × 0.5 | phase log |
| Cruise 16 m/s (E2 pessimistic, 417 W) | 11.3 A | 18.1 W | 1.8 W | 16 m/s × 0.5 | phase log |
| 100 A limiter (24.75 A battery per motor) | 29.8 A | 100.7 W at 80 °C | 9.4 W | — | `CL-E3-LIMITER-LOSS` |

E1 quotes 79–86 W at the limiter for a 25 °C winding. E3 uses the hot-winding value, 100.7 W.

## Cooling paths and vents

| Part | Path | Model | Value |
|---|---|---|---|
| Motor | its own prop wash over the bell, plus internal ventilation | 1/R_th, lumped 81 g × 540 J/kg K, τ 66 s | R_th 1.5 K/W design, 1.0 K/W nominal |
| Motor mount | none useful: the motor touches it on four 4 × 4 mm pads, printed k ≈ 0.2 W/m K | base taken equal to the motor node (conservative) | — |
| ESC | flat plate on the fin pad, FET side out, pad side adiabatic (hook-and-loop) | Incropera eq. 7.30 at wake factor × local slipstream, plus radiation (ε 0.9); strap covers 320 mm² | exposed 1 360 mm², h ≈ 50 W/m² K in hover |
| Pack | pod air (natural 8 W/m² K + radiation; forced with ram air) → 5 mm foam-board shell → outside | 3-node pod network (pack, FC, air) | nearly adiabatic when sealed |
| FC | both board faces to the pod air (on standoffs) | as above | 0.053 W/K sealed, 0.15 W/K vented |
| Pod air | shell conduction plus ram air through the vents in cruise | 1.2 × 0.25 V × 450 mm² × c_p | 2.2 W/K in cruise, 0 in hover |

**ESC pad** (D3 R2, `ASM-E3-ESC-PAD`). The pad runs x 0.078–0.124 m at |z| 0.118 m, so the ESC spans 62–82 mm from
the motor axis. It sits inside the contracted slipstream with 28 mm radial margin and 32 mm clear of the hub wake
(`CL-E3-ESC-PAD-IN-WASH`). It is 2.5 tube diameters behind the 22 mm motor tube, so the design case credits only half
the slipstream velocity (`ASM-E3-WAKE`).

**Vents** (CR-E3-03). Inlet 15 × 30 mm at the pod nose and an equal exit at the rear. In cruise they bring the FC
down from 70.3 to 57.0 °C and the pack at landing from 49.3 to 47.1 °C. A white pod top limits a 10 min sun soak to
+1.2 K on the pack, against +3.6 K for a dark top (`CL-E3-SUN-PACK`).

## Operating rules (flight card, H3)

| Rule | Value | Why | Claim |
|---|---|---|---|
| Longest continuous full throttle (100 A limiter) | **10 s** | from hover-warm, the motor reaches 80 °C after 13.6 s; the ESC is not the limit | `CL-E3-BURST-MAX` |
| Pack temperature at take-off (IR thermometer) | **20–34 °C** | ≥ 20 °C is E2's cold rule; ≤ 34 °C lands the pack at ≤ 50 °C on a 30 °C day | `CL-E3-PACK-START-MAX` |
| Packs in the shade or a cooler bag; pack goes in last | — | sun soak, car cabin | `CL-E3-SUN-PACK` |
| Powered on the ground for more than 5 min: hatch open | — | the FC reaches 61 °C after 10 min sealed, before flying | model run, `EST` |
| Ambient | none within 15–30 °C | ceiling 43 °C (41 °C hover-only) | `CL-E3-CEIL-MISSION` |

## GT-04 pass lines (answer to CR-H1-06)

GT-04 sequence (`ASM-E3-GT04`): 120 s at 690 gf (98.5 W bus), 10 s at 25 A, 60 s at 690 gf, then stop. The ESC is on
the half-fin mock-up. "Rise" is the reading minus the ambient logged at the start of the run.

| Reading within 10 s of stop | Predicted, design / nominal | Pass line | Hard stop (scaled to 30 °C) | Claim |
|---|---|---|---|---|
| ESC case, FET side (IR) | 33.0 / 30.2 K | rise ≤ 33 K | ≤ 70 °C (85 °C MCU − 15 K for case-to-die and IR error) | `CL-E3-GT04-ESC-RISE` |
| Motor can (thermocouple) | 38.2 / 25.6 K (44.0 K peak at the end of the limiter) | rise ≤ 38 K | ≤ 80 °C | `CL-E3-GT04-MOTOR-RISE` |

Scaled value = T_meas − T_amb,test + 30 (valid to ±1 K, `CL-E3-RISE-AMB-INDEP`). A reading above the pass line but
below the hard stop means E3 updates `ASM-E3-WAKE` or `ASM-E3-RTH-DESIGN` with the measured value and re-runs, and the
ceiling moves. GT-04's 120 s hover is about 2τ: enough to check the pass lines, too short to fit R_th. For that,
`T-E3-MOTOR-TAU` needs 600 s at hover power (CR-E3-06).

## Method and checks

| Item | What | Result |
|---|---|---|
| Network | lumped RC nodes per part, explicit Euler, pod air relaxed exactly; copper R(T), pack R(T) | `CALC-E3-MISSION`, `-SWEEP` |
| Mission | E2 phase tables in time order: ground 180 s, climb 25 s, hover 60 s, transition 20 s, cruise 308 s, back-transition 20 s, hover 60 s, descent 50 s | `ASM-E3-PROFILE` |
| Time-step convergence | peaks at dt 1.0 / 0.5 / 0.25 s | largest change 0.005 K (`CL-E3-DT-CONV`) |
| Hand check, steady hover | rise vs loss × R_th | −0.13 K (`CL-E3-STEADY-CHECK`) |
| Cross-check with E2 | adiabatic pack, E2's inputs | 0.000 K (`CL-E3-PACK-VS-E2`) |
| Cold morning (10 °C, params lower bound) | pack self-heating | +19.2 K (`CL-E3-PACK-RISE-COLD`) |
| Upstream not yet re-run | E2's tables still use B1's old cruise power (417 → 298 W pessimistic once re-run) | E3 re-run on the new tables (scratch): peaks −1.3 K motor, −1.6 K ESC, −3.2 K pack; ceiling 43.0 → 44.4 °C. R2 numbers are conservative |
| Not modelled | ESC leads acting as fins, winding hot spot above the stator mean (+5–10 K `EST`), sun on the motors before take-off (≤ 4 K at the peak) | — |

CFD/FEA was not used. Every film coefficient comes from a textbook correlation, and the uncertainty is in three
inputs that a stand test measures directly (R_th, wake factor, pack R). Those tests are cheaper than a mesh study.

## Open issues

| Issue | Owner | Status |
|---|---|---|
| Motor R_th: the maker test behind 0.83 K/W was probably not at steady state; the design case uses 1.5 K/W | E3 / H1 (`T-E3-MOTOR-TAU`) | `UNVERIFIED` |
| ESC wake factor 0.5 behind the tube | E3 / H1 (`T-E3-ESC-PAD`, GT-04) | `UNVERIFIED` |
| D3 R2 still specifies PETG for `FIN-003` and `FIN-007` (CR-E3-01) | D3, G3 | `PROPOSED` |
| LANRC 45 A: board size and temperature rating not published; the 85 °C MCU G-grade limit is used | E1 / E3 | `UNVERIFIED` |
| Pack rating 60 °C and pack R (4–5 mΩ/cell) | E2 (`T-E2-IR`) | `UNVERIFIED` |
| FC power 2.0 W `EST`; F3 has not chosen the board | F3 | `UNVERIFIED` |
| E2 to re-run on B1's new cruise power, then E3 re-runs (results fall 1–3 K) | E2, E3 | `PROPOSED` |
| `PRP-001/002-*` are not in any `interfaces.json` (build warnings) | E1 | `PROPOSED` |

## How to verify

1. Run `python -I redesign/team/E3/thermal.py` (≈ 5 s), then `python -I redesign/proofs/build_graph.py`. There should
   be no `CALC-E3` drift.
2. Run GT-04 with the pass lines above. Run `T-E3-MOTOR-TAU` (600 s) and `T-E3-ESC-PAD` on the H1 stand (procedures
   in `team/E3/claims.json`). Put the measured R_th, wake factor and pack R into `ASM-E3-RTH-DESIGN`, `ASM-E3-WAKE`
   and `ASM-E3-PACK`, then re-run.
3. `T-E3-MISSION`: IR on the motors, ESCs and pack within 60 s of landing, plus `IMU.T` from the log. The model,
   re-run at the measured ambient, must agree within ±8 K.
