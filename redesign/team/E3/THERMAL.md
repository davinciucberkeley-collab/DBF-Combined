# Thermal — motors, mounts, ESCs, pack and avionics (K09-L)

Revision **E3-R3**, 2026-11-10 (simulation round on the settled CAD). Every number comes from `team/E3/thermal.py`
→ `team/E3/claims.json` (38 claims), `team/E3/thermal_results.json` and the ESC CFD in `team/E3/sim/`
(`SIMULATION-REPORT.md`). Every temperature is `UNVERIFIED` until `T-E3-MOTOR-TAU`, `T-E3-ESC-PAD` (both in H1's
GT-04) and `T-E2-IR` have run. Motor thermal resistance and pack resistance are still estimates. The ESC film
coefficient now comes from CFD, and the stand test still has to confirm it.

**Verdict.** With the ASA motor mounts and ESC pads (D-42) and the two pod vents, every part stays inside its limit
over the whole mission from 15 to 30 °C. This holds for the 2.6 kg gate case and for A3's as-designed 2.436 kg. The
smallest margins at 30 °C are the ESC after 30 s at the 100 A limiter (+4.9 K) and the pack at landing (+5.2 K). The
field-ambient ceiling is **44.2 °C** (40.8 °C for a hover-only sortie). **No ambient restriction is needed.** The
flight-card rules of D-42 stay: full throttle ≤ 10 s, pack 20–34 °C at take-off.

R3 changes:
- The ESC film coefficient comes from a 3-grid SU2 RANS study of the as-designed tube, board, pad and ESC. The
  design h is 64.6 W/m² K in hover, against the R2 judgement of 42.9, so the ESC runs 6.9 K cooler.
- An as-designed mass case now sits beside the gate case.
- The pod heat split is as built (F3).
- E2's re-run tables are used.
- The ESC is the stripped 7.6 g board.
- Claim limits now cite `P:thermal.*`.

## Temperatures across the field ambient (full mission, vented pod)

Design case: E2 pessimistic currents (2.6 kg, 5 m/s wind), motor R_th 1.5 K/W, CFD design wake (SA), 5.0 mΩ/cell.
Nominal case: E2 base currents, E1's 1.0 K/W, CFD extrapolated SST wake, 4.0 mΩ/cell. The pack starts at ambient.

| Ambient | Motor peak | ESC peak | Pack at landing | FC peak | Pod air peak | Claim |
|---|---|---|---|---|---|---|
| 15 °C, design / nominal | 48.7 / 35.2 | 41.6 / 33.1 | 30.7 / 25.1 | 40.5 / 38.2 | 28.9 / 25.6 | `CL-E3-SWEEP-DES` / `-NOM` |
| 20 °C | 54.0 / 40.4 | 46.4 / 38.0 | 35.0 / 29.4 | 45.2 / 42.9 | 33.6 / 30.2 | same |
| 25 °C | 59.4 / 45.6 | 51.2 / 42.9 | 39.9 / 34.2 | 50.0 / 47.8 | 38.5 / 35.1 | same |
| 30 °C | 64.8 / 50.9 | 56.1 / 47.8 | 44.8 / 39.2 | 54.9 / 52.6 | 43.4 / 40.1 | same |
| **Limit** | 80 | 85 | 50 life (60 rating) | 85 | — | `P:thermal.*` |

All values in °C. The rise above ambient barely depends on ambient. Between 15 and 30 °C the motor rise changes by
+1.1 K and the ESC rise by −0.5 K (`CL-E3-RISE-AMB-INDEP`). A field or stand reading therefore scales to 30 °C by
adding (30 − T_amb). On a 15 °C morning with the pack first warmed to 20 °C (E2's rule), the pack lands at 33.0 °C
(`CL-E3-PACK-15-WARMED`).

## Limits and margins at 30 °C

| Part | Case | Gate 2.6 kg | As designed 2.436 kg | Limit | Margin (gate) | Claim | Status |
|---|---|---|---|---|---|---|---|
| Motor stator / winding | mission peak (end of descent) | 64.8 °C | 61.3 °C | 80 °C | +15.2 K | `CL-E3-MOTOR-PEAK`, `-ASD-MOTOR-PEAK` | `UNVERIFIED` |
| Motor | continuous hover, steady | 66.3 °C | — | 80 °C | +13.7 K | `CL-E3-MOTOR-STEADY` | `UNVERIFIED` |
| Motor mount, ASA | hover-only sortie | 66.3 °C | — | 83 °C (HDT 93 − 10 K) | +16.7 K | `CL-E3-MOUNT-ASA` | `UNVERIFIED` |
| Station collar, PETG | CF-tube fin below the mount | 30.7 °C | — | 58 °C (HDT 68 − 10 K) | +27.3 K | `CL-E3-COLLAR-T` | `UNVERIFIED` |
| ESC on its ASA pad | mission peak | 56.1 °C | 54.1 °C | 85 °C (MCU) | +28.9 K | `CL-E3-ESC-PEAK`, `-ASD-ESC-PEAK` | `UNVERIFIED` |
| ESC | + 30 s at the 100 A limiter | 80.1 °C | — | 85 °C | +4.9 K | `CL-E3-ESC-ABUSE` | `UNVERIFIED` |
| Motor | + 30 s at the 100 A limiter | 102.2 °C | — | 80 °C | −22 K | `CL-E3-MOTOR-ABUSE` | burst rule below |
| Pack | at landing, vented / sealed pod | 44.8 / 47.2 °C | 43.2 °C | 50 °C life | +5.2 / +2.8 K | `CL-E3-PACK-END`, `-ASD-PACK-END` | `UNVERIFIED` |
| Flight controller | mission, vented / sealed | 54.9 / 68.3 °C | 54.3 °C | 85 °C | +30.1 / +16.7 K | `CL-E3-FC-PEAK`, `-ASD-FC-PEAK` | `UNVERIFIED` |
| Flight controller | hover-only sortie (no ram air) | 68.9 °C | — | 85 °C | +16.1 K | `CL-E3-FC-HOVERONLY` | `UNVERIFIED` |

## Field-ambient ceiling (output for P19 / `R-THERMAL`)

The ceiling is the ambient at which the first part reaches its limit. It is found by bisection on the full model,
with the pack starting at ambient. Values in °C.

| Sortie | Motor 80 | ESC 85 | Pack 60 | Pack 50 at landing | FC 85 | ASA 93 | **Ceiling** | Claim |
|---|---|---|---|---|---|---|---|---|
| Full mission, gate design | 44.2 | 60.0 | 45.2 | 35.2 | 60.9 | 56.3 | **44.2** | `CL-E3-CEIL-MISSION` |
| Full mission, as designed | 47.5 | 62.0 | 46.9 | 36.8 | 61.5 | 59.7 | **46.9** | `CL-E3-CEIL-ASD` |
| Full mission, nominal | 57.9 | 68.0 | 50.9 | 40.8 | 63.3 | 70.3 | 50.9 | — |
| Hover-only to the 20 % line, design | 42.7 | 61.7 | 40.8 | 30.8 | 47.5 | 54.7 | **40.8** | `CL-E3-CEIL-HOVERONLY` |

The RFS morning window (07–10 h, March–April) is far below 40 °C. The pack-start rule keeps the pack at ≤ 50 °C on
landing in two cases: when the ambient is above about 35 °C (`CL-E3-CEIL-PACK-LIFE`), and when the pack was heated in
the car.

## Heat sources per station (design, 30 °C)

| Phase | Motor current | Motor loss | ESC loss | Air speed at the ESC | Source |
|---|---|---|---|---|---|
| Hover | 13.8 A | 24.5 W (hot winding) | 2.4 W | 11.0 m/s slipstream | `CL-E3-HOVER-LOSS` |
| Back-transition | 16.5 A | 29.3 W | 3.2 W | 12.0 m/s | phase log |
| 100 A limiter (24.75 A battery per motor) | 29.8 A | 100.7 W at 80 °C | 9.4 W | — | `CL-E3-LIMITER-LOSS` |

## Cooling paths and vents

| Part | Path | Model | Value |
|---|---|---|---|
| Motor | own prop wash over the bell, plus internal ventilation | 1/R_th, lumped 81 g × 540 J/kg K | R_th 1.5 K/W design, 1.0 K/W nominal |
| Motor mount (ASA) | not a cooling path: four 4 × 4 mm pads, printed k ≈ 0.2 W/m K | base = motor node (conservative) | — |
| Station collar (PETG) | CF tube as a fin from the mount down to the collar | fin equation | 30.7 °C |
| ESC | FET face to the slipstream, pad side adiabatic (hook-and-loop); strap covers 320 mm² | flat plate at f × U, f from CFD (`CL-E3-CFD-FEQ`: 1.13 hover / 1.37 cruise design), plus radiation ε 0.9 | design h 64.6 W/m² K in hover |
| Pack | pod air (natural + ram air in cruise) → 5 mm foam-board shell | 3-node pod network (pack, FC, air) | nearly adiabatic when sealed |
| FC top board | both faces to the pod air, on gel cubes; regulator and BEC heat on the power board `PWR-003` and UBEC `PWR-005` into the pod air | as above | 1.73 W total (`CL-F3-FC-DISS`) |
| Pod air | shell conduction plus ram air through the vents in cruise | 1.2 × 0.25 V × 450 mm² × c_p | 0 in hover |

**Vents** (CR-E3-03, adopted by D2). Inlet 15 × 30 mm at the pod nose, equal exit at the rear. They take the FC from
68.3 to 54.9 °C and the pack at landing from 47.2 to 44.8 °C. With a white pod top, a 10 min sun soak adds +1.9 K
to the pack. A dark top adds +5.6 K (`CL-E3-SUN-PACK`).

## Operating rules (flight card, H3; params D-42)

| Rule | Value | Why | Claim |
|---|---|---|---|
| Longest continuous full throttle (100 A limiter) | **10 s** | from hover-warm the motor reaches 80 °C after 13.6 s | `CL-E3-BURST-MAX` |
| Pack temperature at take-off (IR thermometer) | **20–34 °C** | ≥ 20 °C is E2's cold rule. A pack at ≤ 39 °C lands at ≤ 50 °C on a 30 °C day, and 34 °C keeps 5 K in hand | `CL-E3-PACK-START-MAX` |
| Packs in the shade or a cooler bag; pack goes in last | — | sun soak, car cabin | `CL-E3-SUN-PACK` |
| Powered on the ground for more than 5 min: hatch open | — | sealed pod, no ram air | model run, `EST` |
| Ambient | none within 15–30 °C | ceiling 44.2 °C (40.8 °C hover-only) | `CL-E3-CEIL-MISSION` |

## GT-04 pass lines (CR-E3-06, adopted by H1)

GT-04: 120 s at 690 gf (98.4 W bus), 10 s at 25 A, 60 s at 690 gf, stop. ESC on the half-fin mock-up. Rise = reading
− ambient at the start.

| Reading within 10 s of stop | Predicted R3, design / nominal | Pass line | Hard stop at T₃₀ | Claim |
|---|---|---|---|---|
| ESC case, FET side (IR) | 27.0 / 19.8 K (peak 33.5 K) | rise ≤ 33 K | ≤ 70 °C | `CL-E3-GT04-ESC-RISE` |
| Motor can (thermocouple) | 38.1 / 25.6 K (peak 44.0 K) | rise ≤ 38 K | ≤ 80 °C | `CL-E3-GT04-MOTOR-RISE` |

The R2 pass lines stay as published. They are still at or above the R3 design prediction, so H1 needs no change. A
measured ESC rise well below 27 K confirms the CFD. A rise above 33 K means E3 re-runs with the measured h.

## Method and checks

| Item | What | Result |
|---|---|---|
| Network | lumped RC nodes per part, explicit Euler, pod air relaxed exactly; copper R(T), pack R(T) | `CALC-E3-MISSION`, `-SWEEP` |
| ESC film coefficient | SU2 INC_RANS, 3 grids (18 k / 37 k / 75 k cells), GCI 12.2 % hover / 8.4 % cruise, y+ ≤ 1.5; SST, SST-LM, SA bracket | `CL-E3-CFD-*`, `SIMULATION-REPORT.md` |
| Time-step convergence | peaks at dt 1.0 / 0.5 / 0.25 s | 0.014 K (`CL-E3-DT-CONV`) |
| Hand check, steady hover | rise vs loss × R_th | −0.13 K (`CL-E3-STEADY-CHECK`) |
| Hand check, CFD | SST L3 vs turbulent flat plate | +7 % hover, +5 % cruise |
| Cross-check with E2 | adiabatic pack, E2's inputs | 0.000 K (`CL-E3-PACK-VS-E2`) |
| Cold morning (10 °C) | pack self-heating | +16.9 K (`CL-E3-PACK-RISE-COLD`) |
| Not modelled | ESC leads as fins (cooler), winding hot spot above the stator mean (+5–10 K `EST`), sun on the motors before take-off (≤ 4 K), slipstream swirl over the ESC (cooler) | — |

## Open issues

| Issue | Owner | Status |
|---|---|---|
| Motor R_th: the design case uses 1.5 K/W until measured | E3 / H1 (`T-E3-MOTOR-TAU`) | `UNVERIFIED` |
| ESC film coefficient from a 2-D CFD section; models spread 64.6–91.8 W/m² K | E3 / H1 (`T-E3-ESC-PAD-CFD`) | `UNVERIFIED` |
| LANRC 45 A: board size and temperature rating not published; the 85 °C MCU G-grade limit is used | E1 / E3 | `UNVERIFIED` |
| Pack rating 60 °C and pack R (4–5 mΩ/cell) | E2 (`T-E2-IR`) | `UNVERIFIED` |
| Interface thermal blocks and SPEC tables still quote R2 values (CR-E3-13, -14) | D3, E1, D2, A1 | `PROPOSED` |

## How to verify

1. Run `python -I redesign/team/E3/sim/cfd_claims.py`, then `python -I redesign/team/E3/thermal.py` (≈ 60 s), then
   `python -I redesign/proofs/build_graph.py`. There should be no `CALC-E3` drift.
2. Run GT-04 with the pass lines above, plus `T-E3-MOTOR-TAU` (600 s) and `T-E3-ESC-PAD-CFD`, on the H1 stand. Put
   the measured R_th, h and pack R into `ASM-E3-RTH-DESIGN`, the CFD claims and `ASM-E3-PACK`, then re-run.
3. `T-E3-MISSION`: IR on the motors, ESCs and pack within 60 s of landing, plus `IMU.T` from the log. The model,
   re-run at the measured ambient, must agree within ±8 K.
