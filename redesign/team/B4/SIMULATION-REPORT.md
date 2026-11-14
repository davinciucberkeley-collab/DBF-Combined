# B4 rotor / propeller aero: simulation and verification round

Status `MODELLED`, 2026-11-10. Settled CAD geometry (`params/params.json`, `subsystems/fins/params.json`), A3's
roll-up (`CL-A3-MASS-PREDICTED` 2.436 kg, `CL-A3-HOVER-SPLIT` 1.216, 680 g pack margin 0.034 kg). Claims:
`sim/claims.sim.json` (28 claims, `CL-B4-SIM-*`). Every number is `UNVERIFIED` until `T-B4-STAND` and
`T-B4-INSTALLED` run.

| Step | Command | Output |
|---|---|---|
| Hand model re-run on the as-designed params | `python -I redesign/team/B4/props.py` | `claims.json` (74 claims, no value moved since R4) |
| XFOIL section polars (NACA 4412 / 3410, Ncrit 5) | `python -I redesign/team/B4/sim/bemt/xfoil_polars.py` | `sim/bemt/polars.json` |
| gmsh meshes, SU2 runs, GCI | `python redesign/team/B4/sim/cfd/tubefin.py mesh / run / summary` | `sim/cfd/results.json` |
| Claims (stdlib, reads stored outputs) | `python -I redesign/team/B4/sim/sim_claims.py` | `sim/claims.sim.json`, `sim/out/sim_results.json` |
| Figures | `python redesign/team/B4/sim/figures_sim.py` | `sim/out/fig-b4-sim-0*.svg` |

## 1. Tool choice

| Question | Hand calc (PROPS.md) | Tool used here | Why that fidelity |
|---|---|---|---|
| Hover / cruise thrust, rpm, power | APC PER3 tables + UIUC cross-check | Same tables at A3's masses; BEMT as an independent check | PER3 is the maker's own data for the MR blade. UIUC publishes no MR geometry, so BEMT runs on the 11×5.5E |
| Prop at incidence in the pitch-over | none (B3 assumed it away) | BEMT, 20 radial × 12 azimuth stations, local momentum | Quasi-steady edgewise loads are standard BEMT territory at μ 0.18 |
| Tube + board drag in the slipstream (download, cruise) | bare cylinder Cd 1.1 + board friction + base | 2-D SU2 incompressible RANS (SA), 3 grids | Separated blunt-body flow. XFOIL and VLM cannot model it, and no handbook value covers a 22 mm tube faired by a 9.6 mm board |
| Pitot, elevon and wing-skin wash, tip clearances | props.py wake model and exact 3-D swept-volume test | Re-run on the settled params | Geometry did not change, so nothing called for higher fidelity |

No structural FEA is in B4's scope. C4 and C6 own the primary structure.

## 2. Results against the hand calc

| Parameter | Hand calc | Simulation | Δ | Unit | Claim | Status |
|---|---|---|---|---|---|---|
| Upper-prop hover thrust (A3 predicted mass, split 1.216) | 6.81 (even split, gate) | 7.00 | +2.8 % | N | `CL-B4-SIM-T-UPPER` | `MODELLED` |
| Upper / lower hover rpm | 5 416 (even, gate) | 5 491 / 4 983 | +1.4 % / −8.0 % | rpm | `CL-B4-SIM-RPM-UPPER`, `-LOWER` | `MODELLED` |
| Hover shaft power, 4 props (PER3 × 1.047) | 258 (4 × 64.5) | 246 | −4.6 % | W | `CL-B4-SIM-SHAFT-HOVER` | `MODELLED` |
| Upper-prop headroom at 9 350 rpm, 680 g pack (limit 1.5) | — | 2.78 (+85 %) | — | — | `CL-B4-SIM-HEADROOM` | `MODELLED` |
| T/W at the rpm cap, predicted mass (limit 2.0) | 3.01 (gate) | 3.40 (+70 %) | +13 % | — | `CL-B4-SIM-TW-CAP` | `MODELLED` |
| Static FM, UIUC measured / PER3 (11×5.5E) | 0.955 (`CALC-B4-XCHECK`) | 0.952 | −0.3 % | — | `CL-B4-SIM-FM-RATIO` | `CHECKED` |
| Tube + board section Cd on D, hover 10 m/s | 1.476 (bare cylinder build-up) | **0.599** ± 3.4 % GCI | −59 % | — | `CL-B4-SIM-CD-TUBEFIN`, `-RATIO` | `MODELLED` |
| Hover download factor (upper GCI bound; limit 1.06) | 1.038 | **1.025** (+3.4 %) | −1.3 pts | — | `CL-B4-SIM-DOWNLOAD` | `MODELLED` |
| Tube + board section Cd, cruise 16 m/s vs B1's build-up (`ASM-B1-DRAG`) | 0.577 (B1) | 0.574 ± 4.2 % | −0.5 % | — | `CL-B4-SIM-CD-B1-RATIO` | `CHECKED` |
| Cruise drag of the board-backed tube spans, 4 stations | 1.112 (B1) | 1.106 | −0.006 N | N | `CL-B4-SIM-CRUISE-TUBEFIN`, `-DELTA-B1` | `MODELLED` |
| Worst in-plane H-force per prop, pitch-over at 15.6 m/s, hover rpm | not modelled | 0.43 (3410 bound 0.39) | — | N | `CL-B4-SIM-H-MAX` | `MODELLED` |
| H / T, worst incidence (30°) | not modelled | 0.130 | — | — | `CL-B4-SIM-HT-MAX` | `MODELLED` |
| H-force if hover thrust is held through the pitch-over | not modelled | 0.88 per prop, 3.5 total | — | N | `CL-B4-SIM-H-HOVERT` | `MODELLED` |
| Prop normal-force slope dH/di | not modelled | 0.63 | — | N/rad | `CL-B4-SIM-DH-DI` | `MODELLED` |

The hand calc holds up well. Hover power and rpm move only with A3's lighter mass and the pitch-trim split. The
CFD gives two results. The bare-cylinder Cd 1.1 was conservative by about 2.5× on the 92 % of the tube span that
has the board behind it, so the modelled download drops from 1.038 to 1.025. Keep the `download_factor` param at
1.06 until `T-B4-INSTALLED`. The CFD also confirms B1's cruise build-up for this section to 0.5 %.

## 3. Verification and grid convergence

| Study | Levels (cells) | Values, fine → coarse | Order p | Extrapolated | GCI fine (limit) | Claim |
|---|---|---|---|---|---|---|
| Cylinder Re 40, laminar (solver validation) | 35 772 / 16 552 / 10 398 | 1.508 / 1.502 / 1.499 | 0.62 | 1.531 vs published 1.498–1.522 (+0.6 %) | 1.9 % | `CL-B4-SIM-CFD-VAL` (≤ 3 %) |
| Tube + board, 10 m/s, SA | 57 388 / 29 252 / 15 192 | 0.616 / 0.638 / 0.687 | 2.50 | 0.599 | 3.4 % (≤ 5 %) | `CL-B4-SIM-CD-GCI` |
| Tube + board, 16 m/s, SA | 57 388 / 29 252 / 15 192 | 0.593 / 0.617 / 0.667 | 2.34 | 0.574 | 4.2 % | `CL-B4-SIM-CRUISE-TUBEFIN` |
| BEMT radial elements | 80 / 40 / 20 / 10 | T 5.535 / 5.536 / 5.542 / 5.542 N | 2.08 | — | 0.01 %; 40 → 80 Δ 0.03 % (≤ 0.5 %) | `CL-B4-SIM-BEMT-CONV` |
| BEMT azimuth stations (i 45°) | 24 / 12 / 6 | H 0.3880 / 0.3879 / 0.3874 N | — | — | 12 → 24 Δ 0.004 % (≤ 1 %) | `CL-B4-SIM-INC-CONV` |

Refinement ratios are 1.40 and 1.39 for the fin grids and 1.47 and 1.26 for the cylinder. GCI follows Celik et
al. (2008) with Fs 1.25. The force-breakdown split for the cylinder (pressure 0.99, friction 0.51) matches Dennis
and Chang. The tube + board drag is 93 % pressure and 7 % friction. Residual Cd oscillation over the last 500
iterations is below 0.1 % on every fine grid. The steady solves therefore converged and no shedding was masked.

| BEMT validation vs UIUC 11×5.5E | NACA 4412 | NACA 3410 | Limit | Claim | Use |
|---|---|---|---|---|---|
| Static Ct, worst of 5 rpm | +3.2 % | −4.7 % | 5 % | `CL-B4-SIM-BEMT-STATIC` | hover cross-check |
| Static Cp, worst | −5.7 % | −14.8 % | — | — | 4412 only |
| Tunnel Ct, worst for J ≤ 0.47 | +24 % | **+4.0 %** | 5 % | `CL-B4-SIM-BEMT-FWD` | incidence bound |
| Tunnel Ct near the cruise J (0.57) | +34 % | −43 % | — | — | **not used**: cruise stays on PER3 + XCHECK |
| Static FM / PER3 | 1.036 (measured 0.952) | — | — | `CL-B4-SIM-FM-BEMT` | diagnostic only |

FIG B4-SIM-01 — BEMT vs UIUC and PER3, 11×5.5E (`sim/out/fig-b4-sim-01-bemt-validation.svg`).
FIG B4-SIM-02 — Grid convergence, cylinder and tube + board (`sim/out/fig-b4-sim-02-cfd-convergence.svg`).
FIG B4-SIM-03 — Thrust, power and H-force against inflow angle (`sim/out/fig-b4-sim-03-incidence.svg`).
FIG B4-SIM-04 — Hover thrust per prop at three masses against the rpm cap (`sim/out/fig-b4-sim-04-hover-ops.svg`).
FIG B4-SIM-05 — Cp on the tube + board, hover, finest grid (`sim/out/fig-b4-sim-05-tubefin-cp.svg`).

## 4. Margins and requirements

| Requirement / limit | Value | Limit | Margin | Claim | Status |
|---|---|---|---|---|---|
| `R-HOVER-TW` at the rpm cap, predicted mass | 3.40 | ≥ 2.0 | +70 % | `CL-B4-SIM-TW-CAP` | `MODELLED` |
| Hover control factor, upper prop, 680 g pack | 2.78 | ≥ 1.5 | +85 % | `CL-B4-SIM-HEADROOM` | `MODELLED` |
| Download factor vs param | 1.025 | ≤ 1.06 | +3.4 % | `CL-B4-SIM-DOWNLOAD` | `MODELLED` |
| Pitot error, transition | 1.75 % | ≤ 2 % | +13 % | `CL-B4-PITOT` | `MODELLED` |
| Blade to wing skin | 34.2 mm | ≥ 25 mm | +37 % | `CL-B4-TIP-WING` | `CHECKED` (E1 CAD) |
| **`R-PROP-CLEAR`: blade swept volume to the CF motor tube** | **21.1 mm** | ≥ 25 mm | **−16 % `FAIL`** | `CL-B4-GAP-TUBE-ENV` | `CHECKED` (= `CL-E1-TIP-GAP-TUBE`) |
| Unlimited full-throttle rpm, fresh pack | 10 637 | ≤ 9 350 | −11 % | `CL-B4-RPM-MAX-FULL` | mitigated: `Q_M_SPIN_MAX` 0.84 is set in `subsystems/flight-software/params.json` |

## 5. Open issues

- **The tube clearance still fails on the settled CAD.** `fin_detail.mount.face_ahead_m` is still 0.0025 m.
  CR-D3-26 / CR-E1-44 (0.0075 m) is not in params. See CR-B4-25.
- No MR-blade measurements exist. BEMT is trusted only static and for J ≤ 0.47. `T-B4-STAND` settles cruise η.
- The H-force is quasi-steady BEMT with no wing upwash. The section bound spans 0.39–0.43 N. It goes to B3 as a
  prop normal-force term (CR-B4-26).
- The CFD section is 2-D and steady, run in a uniform, turbulent, swirl-free stream. The real slipstream has
  swirl and blade-passage unsteadiness. `ASM-B4-SIM-SA` and `ASM-B4-SIM-FILLET` are `UNVERIFIED`, and
  `T-B4-INSTALLED` measures the result.
- The domain (45 D upstream, 3.6 fin chords downstream) had no sensitivity check. Blockage is 1.1 %.
