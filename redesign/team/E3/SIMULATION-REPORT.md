# E3 thermal: simulation round on the settled CAD

Revision **E3-R3**, 2026-11-10. Scripts: `team/E3/sim/cfd/esc_cfd.py` (SU2 RANS, 3 grids) → `sim/cfd/results.json`
→ `sim/cfd_claims.py` (15 claims) → `thermal.py` (38 claims) → `plots.py` (`figs/fig-e3-0*.svg`). Every temperature
is `UNVERIFIED` until H1's GT-04, `T-E3-MOTOR-TAU`, `T-E3-ESC-PAD` and `T-E2-IR` have run.

**Verdict.** On the as-designed geometry and A3's predicted mass (2.436 kg), and on the 2.6 kg gate case, every part
stays inside its limit over the full mission from 15 to 30 °C. No requirement fails. The CFD shows the ESC runs
**6.9 K cooler** than the R2 hand estimate. The field-ambient ceiling rises from 43.0 to **44.2 °C** (gate case)
and 46.9 °C (as designed). The smallest margin is still the pack at landing: +5.2 K on a 30 °C day.

## What was simulated, and why this tool

| Question | Tool | Why this level |
|---|---|---|
| ESC film coefficient on its fin pad, in the slipstream behind the 22 mm motor tube | **SU2 8.5 INC_RANS**, 2-D section, gmsh quad-layer meshes, 3 levels | The input with the widest band in R2 (`ASM-E3-WAKE`, judged 0.5 / 0.7). The tube overhangs the 9.6 mm board by 6.2 mm, and its shear layer reattaches where the 7.2 mm ESC + pad stands up as a forward step. No flat-plate or cylinder correlation covers that, and XFOIL/VLM cannot. A 2-D section is enough: the slipstream runs along the fin, and the tube is long (L/D ≈ 8) and spans the pad (tube ends at \|z\| 0.172 m, pad at 0.118 m) |
| Motor, mount, ESC, pack, FC and pod-air temperatures over the mission | Lumped RC network (`thermal.py`), E2 phase tables, E1 motor constants, B4 slipstream | The other uncertain inputs (motor R_th, pack R) are measured more cheaply on the stand than meshed. CFD of a spinning outrunner bell is not justified |
| PETG station collar `FIN-008` below the ASA mount | Fin equation along the CF tube (`CL-E3-COLLAR-T`) | 30.7 °C against 58 °C. A 27 K margin needs no FEA |
| Structural FEA | not E3's scope | C-roles own primary structure |

## CFD set-up

| Item | Value | Source |
|---|---|---|
| Geometry | tube D 22 mm at x 0.045 m, two-layer board 9.6 mm to x 0.320 m, ASA pad 1.2 mm at x 0.078–0.124 m, ESC 45 × 6 mm centred on the pad | `params.json#fins.*`, `subsystems/fins/params.json#fin_detail.esc_pad`, `subsystems/propulsion/params.json#propulsion_detail.esc` |
| Inflow | hover 10.9 m/s (B4 momentum model at the pad, design hover); cruise 16.0 m/s | `CL-E3-CFD-U` |
| Physics | incompressible RANS, SST (Tu 5 %, ν_t/ν 10), energy equation, ESC faces isothermal at T_amb + 30 K, other walls adiabatic; Re_L 33 k (hover) / 49 k (cruise) | `esc_cfd.py` |
| Output | mean h over the three exposed ESC faces; equivalent local-velocity factor f = (h / h_lam(U))², the quantity `thermal.py` uses | `CALC-E3-CFD-FEQ` |
| Meshes | L1 17 943, L2 36 542, L3 75 291 cells; refinement ratio 1.43 / 1.44; y+ max 1.13 (L2 hover), 1.48 (L2 cruise) | `sim/cfd/mesh/cells.json`, `CL-E3-CFD-YPLUS-L2` |
| Iterative convergence | residuals down 3–7 orders; h steady over the last 500 iterations (half-amplitude ≤ 0.7 %) | `results.json#cases.*.rms_drop` |

FIG E3-04 — Mesh L2 near the tube and ESC (`figs/fig-e3-04-mesh.svg`).

## Grid convergence (Celik et al. 2008, Fs 1.25)

| Case | h L1 / L2 / L3 | Order p | Extrapolated | GCI fine | Lower band used | Claim |
|---|---|---|---|---|---|---|
| Hover, SST | 72.9 / 79.4 / 83.6 W/m² K | 1.17 | 91.8 W/m² K | 12.2 % (limit 15 %) | 80.6 W/m² K | `CL-E3-CFD-GCI-HOV` `CHECKED` |
| Cruise, SST | 97.0 / 105.9 / 111.2 W/m² K | 1.48 | 118.7 W/m² K | 8.4 % | 108.7 W/m² K | `CL-E3-CFD-GCI-CRU` `CHECKED` |

h rises monotonically with refinement, so the coarser values sit on the cool side. FIG E3-02 (`figs/fig-e3-02-cfd-grid.svg`).

## Turbulence-model bracket (L2) and the design value

| Run | Hover h | Cruise h | f (hover) | Used for |
|---|---|---|---|---|
| SST, Tu 5 %, lower GCI band | 80.6 | 108.7 | 1.76 | — |
| SST-LM transition, Tu 1 % | 87.8 | 113.9 | 2.09 | — |
| Spalart-Allmaras, Tu 5 % | **64.6** | 86.2 `EST` (SA/SST ratio × SST L2) | **1.13** | **design** (lowest of the three) |
| SST extrapolated | 91.8 | 118.7 | 2.29 | nominal |
| R2 judgement, design / nominal | 42.9 / 50.8 | — | 0.50 / 0.70 | replaced; kept as `CL-E3-ESC-PEAK-R2WAKE` |

Two sensitivity runs **diverged** and are excluded: SST at Tu 1 % (stopped at 82 iterations) and SST-LM at Tu 5 % (19
iterations). The bracket rests on the three converged models above. Design f = 1.13 (hover) / 1.37 (cruise)
(`CL-E3-CFD-FEQ`).

## Comparison with the hand calculations

| Quantity | Hand calc | Simulation | Difference | Reading |
|---|---|---|---|---|
| ESC h, hover | turbulent flat plate (Incropera 7.36) 77.8; R2 judged 42.9 W/m² K | SST L3 83.6; design SA 64.6 W/m² K | +7 % vs turbulent; design +50 % vs R2 | reattaching shear layer behaves like a turbulent plate; R2 was too pessimistic |
| ESC h, cruise | turbulent flat plate 105.7 W/m² K | SST L3 111.2 W/m² K | +5 % | as above |
| ESC peak, 30 °C, gate case | R2 wake on R3 inputs 62.9 °C | CFD wake 56.1 °C | −6.9 K | `CL-E3-ESC-PEAK-R2WAKE` vs `CL-E3-ESC-PEAK` |
| Motor steady hover rise | loss × R_th = 36.48 K | network 36.35 K | −0.13 K | `CL-E3-STEADY-CHECK` |
| Pack, adiabatic, E2's inputs | E2 `CL-E2-PACK-T-END` | network | 0.000 K | `CL-E3-PACK-VS-E2` |
| Time step 1.0 / 0.5 / 0.25 s | — | largest peak change 0.014 K | limit 0.2 K | `CL-E3-DT-CONV` `CHECKED` |

## Results at 30 °C ambient, R2 → R3

Gate = 2.6 kg, E2 pessimistic currents, R_th 1.5 K/W, 5.0 mΩ/cell. As designed = A3's `CL-A3-MASS-PREDICTED`
2.436 kg with the same design inputs. FIG E3-01 (`figs/fig-e3-01-mission.svg`), FIG E3-05 (`figs/fig-e3-05-margins.svg`).

| Part | R2 (2026-11-09) | R3 gate | R3 as designed | Limit | Margin, gate | Claim | Status |
|---|---|---|---|---|---|---|---|
| Motor peak | 65.8 °C | 64.8 °C | 61.3 °C | 80 °C | +15.2 K | `CL-E3-MOTOR-PEAK`, `-ASD-MOTOR-PEAK` | `UNVERIFIED` |
| Motor mount (ASA), hover-only | 66.3 °C | 66.3 °C | — | 83 °C | +16.7 K | `CL-E3-MOUNT-ASA` | `UNVERIFIED` |
| ESC peak | 61.6 °C | 56.1 °C | 54.1 °C | 85 °C | +28.9 K | `CL-E3-ESC-PEAK`, `-ASD-ESC-PEAK` | `UNVERIFIED` |
| ESC + 30 s at the 100 A limiter | 78.7 °C | 80.1 °C | — | 85 °C | +4.9 K | `CL-E3-ESC-ABUSE` | `UNVERIFIED` |
| Pack at landing | 47.1 °C | 44.8 °C | 43.2 °C | 50 °C | +5.2 K | `CL-E3-PACK-END`, `-ASD-PACK-END` | `UNVERIFIED` |
| Flight controller | 57.0 °C | 54.9 °C | 54.3 °C | 85 °C | +30.1 K | `CL-E3-FC-PEAK`, `-ASD-FC-PEAK` | `UNVERIFIED` |
| FC, hover-only sortie | 70.7 °C | 68.9 °C | — | 85 °C | +16.1 K | `CL-E3-FC-HOVERONLY` | `UNVERIFIED` |
| PETG station collar | — | 30.7 °C | — | 58 °C | +27.3 K | `CL-E3-COLLAR-T` | `UNVERIFIED` |
| Field-ambient ceiling, mission | 43.0 °C | **44.2 °C** | 46.9 °C | ≥ 30 °C | +14.2 K | `CL-E3-CEIL-MISSION`, `-CEIL-ASD` | `UNVERIFIED` |
| Ceiling, hover-only sortie | 41.3 °C | 40.8 °C | — | ≥ 30 °C | +10.8 K | `CL-E3-CEIL-HOVERONLY` | `UNVERIFIED` |
| Full-throttle time from hover-warm | 13.6 s | 13.6 s | — | ≥ 10 s rule | +3.6 s | `CL-E3-BURST-MAX` | `UNVERIFIED` |
| Pack take-off temperature for ≤ 50 °C at landing | 34.5 °C | 39.1 °C | — | rule 34 °C | +5.1 K | `CL-E3-PACK-START-MAX` | `UNVERIFIED` |
| GT-04 ESC rise / motor rise (design) | 33.0 / 38.2 K | 27.0 / 38.1 K | — | 40 / 50 K | — | `CL-E3-GT04-*` | `UNVERIFIED` |

What moved: the CFD wake (ESC −6.9 K, isolated by `CL-E3-ESC-PEAK-R2WAKE`); E2's re-run tables on B1's lower cruise
power together with the as-built pod heat split (F3's 1.73 W FC, BEC losses on the power board, only 2.9 of 6.5 mΩ of
harness inside the pod): motor −1.0 K, pack −2.3 K, FC −2.1 K. The stripped 7.6 g ESC (was 11 g) has less thermal
mass, which mainly explains the +1.4 K in the 30 s limiter case.

### 15–30 °C sweep, gate case (design / nominal), °C

| Ambient | Motor | ESC | Pack at landing | FC | Pod air |
|---|---|---|---|---|---|
| 15 | 48.7 / 35.2 | 41.6 / 33.1 | 30.7 / 25.1 | 40.5 / 38.2 | 28.9 / 25.6 |
| 20 | 54.0 / 40.4 | 46.4 / 38.0 | 35.0 / 29.4 | 45.2 / 42.9 | 33.6 / 30.2 |
| 25 | 59.4 / 45.6 | 51.2 / 42.9 | 39.9 / 34.2 | 50.0 / 47.8 | 38.5 / 35.1 |
| 30 | 64.8 / 50.9 | 56.1 / 47.8 | 44.8 / 39.2 | 54.9 / 52.6 | 43.4 / 40.1 |

## Requirements

| Requirement | Result | Status |
|---|---|---|
| `R-THERMAL`: every part within rating at the design ambient (≤ 30 °C) for the full mission | all margins positive, smallest +4.9 K (ESC, 30 s limiter abuse) and +5.2 K (pack) | passes on paper, `UNVERIFIED` |
| Operating rules (flight card, D-42) | 10 s full throttle, pack 20–34 °C at take-off, packs shaded, hatch open on the ground > 5 min | unchanged; no ambient restriction inside 15–30 °C |

No requirement fails. No new operating restriction is needed.

## Limits of this round

| Limit | Effect | Closed by |
|---|---|---|
| 2-D section: no slipstream swirl, no 3-D tip flow round the 20 mm ESC width | swirl adds mixing, so h is probably higher (cool side) | `T-E3-ESC-PAD-CFD` (aluminium dummy + 3 W resistor on the half-fin) |
| Turbulence-model spread 64.6–91.8 W/m² K | covered by taking SA (lowest) for design | same test |
| Motor R_th 1.5 K/W design is still a judgement | motor ±10 K | `T-E3-MOTOR-TAU` (600 s at hover power, GT-04 sub-step) |
| Pack R 5 mΩ/cell | pack ±3 K | `T-E2-IR` |

## How to re-run

1. `python redesign/team/E3/sim/cfd/esc_cfd.py mesh`, then `run`, then `summary` (gmsh + SU2, ≈ 15–30 min).
2. `python -I redesign/team/E3/sim/cfd_claims.py`, then `python -I redesign/team/E3/thermal.py` (≈ 60 s).
3. `python redesign/team/E3/plots.py` (matplotlib) for the figures, then `python -I redesign/proofs/build_graph.py`.
