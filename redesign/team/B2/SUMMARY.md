# B2 — Wing aero engineer (K09-L)

Status: `MODELLED`, revision **B2-R3** (2026-11-10): verification round on the as-designed geometry (params
A1-R4: 0.21 m half-fins, pod 0.14 m, CG range 0.0509–0.0548 m) and the A3-R5 roll-up (predicted 2.436 kg).
Reports: [`SIMULATION-REPORT.md`](SIMULATION-REPORT.md) (R3), [`WING-AERO.md`](WING-AERO.md) (R2 design basis).
Claims: `claims.json` (21) and `sim/claims.sim.json` (28). Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md)
(new: CR-B2-16 … 19).

**Verdict.** S5010, rectangular 1.15 × 0.32 m, no twist: unchanged. Every wing requirement passes on the design
model, but **`R-STALL` and `R-TRANSITION` pass by only 0.1 % at the forward CG**, less than the clmax uncertainty.
A turbulent leading edge would put the stall at 12.84 m/s, so the slow-flight stall test is the gate (CR-B2-16)
and the LE stays seam-free (CR-B2-17). 2-D RANS (SU2, 3 grids) confirms the servo hinge-moment basis but cannot
settle clmax. The R2 forward-CG FAIL (12.06 m/s, CR-B2-11) is closed by A1-R4's aft CG range.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Section, planform, twist | S5010 (t/c 9.82 %), 1.15 × 0.32 m, 0° | — | `airfoils/s5010.dat`, params | `PROPOSED` |
| Neutral point, wing + 0.21 m half-fins, props off | 0.0738 | m | `P:b2sim.avl.xnp_props_off_m` | `UNVERIFIED` |
| Trimmed CLmax, forward / aft CG (SM 6.25 / 5.03 % vs B3 NP 0.0709 m) | 0.787 / 0.798 | — | `CL-B2R3-CLMAX-FWD`, `P:b2sim.avl.clmax_vs_sm` | `UNVERIFIED` |
| Stall at 2.6 kg, forward / aft CG | 11.99 / 11.91 | m/s | `CL-B2R3-VS-GATE-FWD`, `-AFT` | `UNVERIFIED`, +0.1 % / +0.7 % |
| Stall at the A3 predicted 2.436 kg, CG 0.0536 m | 11.59 | m/s | `CL-B2R3-VS-PRED` | `UNVERIFIED`, +3.5 % |
| 1.3 Vs, forward CG, vs `transition_min_ms` 15.6 | 15.58 | m/s | `CL-B2R3-VTR-GATE-FWD` | `UNVERIFIED`, +0.1 % |
| Stall with a turbulent LE (sensitivity) | 12.84 | m/s | `CL-B2R3-VS-GATE-FWD-TURB` | risk, −7 % |
| Stall starts at | y 0.071 m (inboard elevon end), tips last | m | `sim/out/verify_results.json` | `UNVERIFIED` |
| Elevon at CLmax, forward CG | −11.9 (0.47 of travel) | deg | `P:b2sim.avl.elev_vs_sm` | `UNVERIFIED` |
| Hinge moment per servo, 25° at VD 27.2 m/s | 0.440 | N·m | `CL-B2R3-HINGE-VD-FULL` | `UNVERIFIED` |
| Servo torque through D6 linkage, `R-SERVO-TORQUE` (rated 3.9) | 3.49 | kgf·cm | `CL-B2R3-SERVO-TORQUE-REQ` | `UNVERIFIED`, +11 % |
| SU2 viscous / XFOIL inviscid hinge moment | ≤ 0.88 | — | `CL-B2R3-HINGE-VISC-RATIO` | `CHECKED` (3 grids) |
| Root bending, 1 g / n 3.4 AVL / n 3.4 Schrenk | 3.09 / 10.5 / 11.5 | N·m | `CL-B2-ROOT-BM-1G`, `CL-B2R3-ROOT-BM-LIMIT`, `-SCHRENK` | `UNVERIFIED` |
| Wing lift slope, η, Cn_β props off | 3.48 /rad, 0.61, +0.054 /rad | — | `CL-B2-CLA-3D`, `CL-B2-ELEVON-ETA`, `P:b2sim.avl.cnb_a4` | `UNVERIFIED` |
| Negative section clmax | −0.435 | — | `CL-B2-CLMIN-2D` | `UNVERIFIED` |

## Files

| File | What |
|---|---|
| `xfoil_wing.py` | 76 polars (4 sections, Re 2.0–4.5e5, design Re from the chord, Ncrit 5/9, elevon −15…+10°), 40 hinge cases, panel convergence |
| `avl_wing.py` | wing + fins from params: trim with viscous cm, critical-section CLmax, CG, static-margin and twist sweeps, lattice convergence, loads |
| `results_to_params.py` → `params.json` | run results the proof chain reads (`P:b2.*`) |
| `wing_claims.py` → `claims.json` | claims, assumptions, tests (proofkit) |
| `plots_wing.py` → `fig/B2-0*.svg` | polars, clmax vs elevon, span loading and stall margin, hinge moments |
| `out/loads_spanwise.json` | strip loads, shear, bending, torsion per N of half-lift, for C1/C2 (A1-R4 geometry) |
| `sim/cfd2d_section.py` | SU2 INC_RANS SA + gmsh: 13 cases, 3-grid studies on the clmax and servo cases |
| `sim/xfoil_tripped.py` | XFOIL with transition fixed at 2 % c (like-for-like with the RANS) |
| `sim/verify_wing.py` → `sim/params.json` | AVL SM sweep 4–8 %, 4 lattices, 4 panel counts, Re slope, hand checks (`P:b2sim.*`) |
| `sim/sim_claims.py` → `sim/claims.sim.json` | R3 claims (stall at the as-designed CG and masses, servo, convergence, loads) |
| `sim/plots_sim.py` → `sim/fig/B2-R3-0*.svg` | stall vs SM, convergence, CFD vs XFOIL, span loading |

## Checks

| Check | Result | Status |
|---|---|---|
| XFOIL 160 / 220 / 300 / 400 panels, S5010 Re 2.6e5 | clmax spread 1.7 %; the 220 used is 0.9 % below the finest | `CHECKED` (conservative) |
| AVL 4 lattices | Xnp 0.1 %; trimmed CLmax spread 1.7 %, used value 0.5 % below the finest | `CHECKED` (conservative) |
| SU2 3 grids (12k / 25k / 50k cells) | C_h GCI 47 %, clmax GCI 71 %: used as a bound only; attached cl within 4 % of tripped XFOIL | `CHECKED` (hinge bound) |
| Hand calcs | Helmbold CLα ratio 0.92; Schrenk root bending +9.6 %; elliptic centroid 0.424 vs 0.422 | `CHECKED` |
| `python -I redesign/proofs/build_graph.py` | no B2 error or drift; A1, A3, B1, B3, C1 … drift on their own inputs | `CHECKED` |
| Slow-flight stall, servo bench | `T-B2-STALL`, `T-B2-HINGE` planned | `UNVERIFIED` |

## Open issues

| Issue | Owner |
|---|---|
| Stall / transition margins +0.1 %: close by `T-B2-STALL` before the order and before `ARSPD_FBW_MIN` is frozen | A1, A2, F4, H2 (CR-B2-16) |
| LE tape seam at x/c ≈ 0.05 may trip the boundary layer (+7 % stall) | D1 (CR-B2-17) |
| Servo needs the 6 V rail (needs 3.49, rated 3.1 kgf·cm at 4.8 V) | D6, F1 (CR-B2-19) |
| SU2 clmax not grid-converged; URANS + transition model only if the flight test fails | B2 |
