# B2 — Wing aero engineer (K09-L)

Status: `MODELLED`, revision **B2-R4** (2026-11-10): stall re-run on the **D-62 CG range [0.0466, 0.0514] m with
the CG 18.5 mm above the chord plane**, and CR-B1-23 (B1 vs B2 CLmax and NP) reconciled. Geometry as B2-R3 (A1-R4).
Reports: [`SIMULATION-REPORT.md`](SIMULATION-REPORT.md) (R4 §2a, R3 rest), [`WING-AERO.md`](WING-AERO.md) (design basis).
Claims: `claims.json` (21) and `sim/claims.sim.json` (42). Change requests: [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md)
(new: CR-B2-20 … 22).

**Verdict.** S5010, rectangular 1.15 × 0.32 m, no twist: unchanged. With the CG height in AVL's moment reference the
forward mark 0.0466 m stalls at **11.99 m/s** (A1's z 0 estimate 12.05 is confirmed for z 0 and does not apply);
`R-STALL` and `R-TRANSITION` pass by **0.05 %**, so `T-B2-STALL` stays the gate (D-71). At the bottom of the allowed
CG height (z 0.010) the forward mark **fails by 0.1 %**: CR-B2-20 asks A1 to raise `cg.z_range_m[0]` to 0.0165 m.
**CR-B1-23:** B1's 0.862 is not confirmed. B2's model in B1's set-up gives 0.854 (the codes agree to 1 %); the gap is
three set-up choices (clmax envelope −0.022, viscous cm trim −0.037, props/pod NP +0.026) plus the CG point. The NP
gap 0.0708 / 0.0738 is the moment-reference height: with z 0.0185 B2 gives 0.0709, 0.08 mm from B1.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Section, planform, twist | S5010 (t/c 9.82 %), 1.15 × 0.32 m, 0° | — | `airfoils/s5010.dat`, params | `PROPOSED` |
| Neutral point, wing + 0.21 m half-fins, props off: CG on the chord plane / CG z 0.0185 (CL 0.414) | 0.0738 / 0.0709 | m | `P:b2sim.avl.xnp_props_off_m`, `CL-B2R4-NP-VS-B1` (+0.08 mm vs B1) | `UNVERIFIED` |
| Trimmed CLmax at the forward / aft limit, z 0.0185 | 0.786 / 0.799 | — | `CL-B2R3-CLMAX-FWD`, `P:b2sim.zcg.clmax_grid` | `UNVERIFIED` |
| Stall at 2.6 kg: forward / target / aft, z 0.0185 | 11.99 / 11.97 / 11.90 | m/s | `CL-B2R3-VS-GATE-FWD`, `CL-B2R4-VS-GATE-TARGET`, `CL-B2R3-VS-GATE-AFT` | `UNVERIFIED`, +0.05 / +0.3 / +0.8 % |
| Stall at 2.6 kg, forward limit, z 0.010 / z 0 | 12.01 / 12.04 | m/s | `CL-B2R4-VS-GATE-FWD-ZLO` (FAIL), `-Z0` (information) | `UNVERIFIED` |
| Lowest CG height for `R-STALL` at x 0.0466; forward mark needed at z 0.010 | 0.0162; 0.0478 | m | `CL-B2R4-Z-MIN-AT-XFWD`, `CL-B2R4-X-FWD-AT-ZLO` | `UNVERIFIED` (CR-B2-20) |
| Stall at the A3 predicted 2.436 kg, CG 0.0536 m | 11.63 | m/s | `CL-B2R3-VS-PRED` | `UNVERIFIED`, +3.2 % |
| 1.3 Vs, forward CG, vs `transition_min_ms` 15.6 | 15.59 | m/s | `CL-B2R3-VTR-GATE-FWD` | `UNVERIFIED`, +0.05 % |
| CLmax at B1's CG point (0.0536, z 0.018): B1 / B2 in B1 set-up / B2 | 0.862 / 0.854 / 0.820 | — | `CL-B1V-CLMAX-SIM`, `CL-B2R4-B1-REPRO`, `CL-B2R4-CLMAX-B1POINT` | `CHECKED` (code-to-code, −1.0 %) |
| Stall with a turbulent LE (sensitivity) | 12.85 | m/s | `CL-B2R3-VS-GATE-FWD-TURB` | risk, −7 % |
| Stall starts at | y 0.071 m (inboard elevon end), tips last, every (x, z) | m | `sim/out/stall_zcg.json` | `UNVERIFIED` |
| Elevon at CLmax, forward CG, z 0.0185 (B3 limit 12.5) | −12.2 (0.49 of travel) | deg | `CL-B2R4-ELEV-FWD` | `UNVERIFIED` |
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
| `sim/stall_zcg.py` → `sim/params.zcg.json` | B2-R4: AVL critical section with Xref = x + 2.91 mm, Zref = z on a 5 × 4 (x, z) grid; CR-B1-23 waterfall W0–W4; NP vs CL (`P:b2sim.zcg.*`) |
| `sim/plots_zcg.py` → `sim/fig/B2-R4-0*.svg` | stall vs x for four CG heights; CLmax waterfall B1 → B2 |
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
| Proof graph: every B2 calc re-computed against the current graph (`build_graph.Build`, B2 calcs only) | 0 B2 errors or drifts; 4 errors belong to B3, B4, D2. The full build did not finish in 10 min (B3's calcs re-run AVL) | `CHECKED` (B2 scope) |
| B2 AVL in B1's set-up vs B1 | 0.854 vs 0.862 (−1.0 %); NP 0.07090 vs 0.07082 m | `CHECKED` |
| B2 props-off NP at 1.3 Vs, z 0.0185, vs B3 `CL-B3-V-XNP-ENV` + props/pod | 0.07058 vs 0.07035 m (+0.23 mm) | `CHECKED` |
| Props/pod term used vs B3's current claims (`CL-B2R4-DPROP-DRIFT`) | 0 m | `CHECKED` |
| Slow-flight stall, servo bench | `T-B2-STALL`, `T-B2-HINGE` planned | `UNVERIFIED` |

## Open issues

| Issue | Owner |
|---|---|
| Forward mark fails `R-STALL` by 0.1 % at z 0.010: raise `cg.z_range_m[0]` to 0.0165 or z-dependent mark | A1, B3, H1 (CR-B2-20) |
| R2 claims `CL-B2-STALL-GATE-FWD`, `-TRANSITION-GATE-FWD` no longer verify `R-STALL` / `R-TRANSITION` (z 0 basis); A2 re-points the matrix to `CL-B2R3-VS-GATE-FWD`, `-VTR-GATE-FWD` | A2 (CR-B2-20) |
| B1 reads B2's z 0 SM table for CLmax; switch to `CL-B2R3-CLMAX-FWD`, add the viscous cm trim | B1 (CR-B2-21) |
| Stall / transition margins +0.05 %: close by `T-B2-STALL` before the order and before `ARSPD_FBW_MIN` is frozen | A1, A2, F4, H2 (CR-B2-16) |
| LE tape seam at x/c ≈ 0.05 may trip the boundary layer (+7 % stall) | D1 (CR-B2-17) |
| Servo needs the 6 V rail (needs 3.49, rated 3.1 kgf·cm at 4.8 V) | D6, F1 (CR-B2-19) |
| SU2 clmax not grid-converged; URANS + transition model only if the flight test fails | B2 |
