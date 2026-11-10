# Wing aero verification — B2-R3 (as-designed K09-L)

Status: `MODELLED`, analysis complete, nothing flown. Revision B2-R3 (2026-11-10) on params **A1-R4** (half-fins
0.21 m, fin chord 0.275 m at x 0.045–0.320 m, pod 0.225 × 0.14 × 0.07 m, CG range 0.0509–0.0548 m) and the
**A3-R5 roll-up** (basic 2.322 kg, predicted 2.436 kg, predicted CG 0.0536 m). Claims: `sim/claims.sim.json`
(28 claims). Earlier analysis: [`WING-AERO.md`](WING-AERO.md) (R2).

**Verdict.** On the settled geometry every wing requirement passes on the design model, but two pass by less than
the model's own uncertainty:

| Requirement | Design value | Limit | Margin | Status |
|---|---|---|---|---|
| `R-STALL`, 2.6 kg, forward CG 0.0509 m | 11.99 m/s | ≤ 12.0 m/s | +0.1 % | `UNVERIFIED` — margin < uncertainty |
| `R-STALL`, 2.6 kg, aft CG 0.0548 m | 11.91 m/s | ≤ 12.0 m/s | +0.7 % | `UNVERIFIED` |
| Stall at the A3 predicted mass and CG (2.436 kg) | 11.59 m/s | ≤ 12.0 m/s | +3.5 % | `UNVERIFIED` |
| `R-TRANSITION`, 1.3 Vs at the forward CG vs `transition_min_ms` | 15.58 m/s | ≤ 15.6 m/s | +0.1 % | `UNVERIFIED` |
| `R-SERVO-TORQUE`, ±25° at VD 27.2 m/s through the D6 linkage | 3.49 kgf·cm | ≤ 3.9 kgf·cm (SH-0255MG+, 6 V) | +11 % | `UNVERIFIED` (T-B2-HINGE) |
| Servo, F4 envelope (25° to VA 20.5 m/s, 8.3° at VD) | 1.98 kgf·cm | ≤ 3.9 kgf·cm | +49 % | `UNVERIFIED` |
| Stall if the LE boundary layer is turbulent (sensitivity) | 12.84 m/s | ≤ 12.0 m/s | −7 % | **risk**, not a design value |

The 2-D RANS campaign (SU2, 3 grids) **confirms the hinge-moment basis** (viscous ≤ 0.88 × XFOIL inviscid, every
grid and the Richardson value) but **cannot settle clmax**: steady SA on the post-stall section is not
grid-converged (GCI 22–71 %). Section clmax therefore stays the XFOIL free-transition value, and the stall claims
stay `UNVERIFIED` until the slow-flight stall test (CR-B2-16).

## 1. What was re-run, with what

| Analysis | Tool | Why this fidelity | Inputs | Script |
|---|---|---|---|---|
| Section polars, Re 2.0–4.5e5, elevon −25…+25° | XFOIL 6.99, 220 panels, Ncrit 9 (and 5) | attached flow to clmax; the standard low-Re section tool | `team/B2/airfoils/s5010.dat`, `P:wing.elevon.chord_frac` | `xfoil_wing.py` |
| Section, transition fixed at 2 % c | XFOIL 6.99 | like-for-like reference for the fully turbulent RANS | same | `sim/xfoil_tripped.py` |
| Wing + 0.21 m half-fins, trim, NP, Cn_β, span loading | AVL 3.52, 12 × 1 lattice | attached-flow 3-D loading; 4 lattices agree to 0.1 % on Xnp | `params.json` A1-R4 | `avl_wing.py` |
| Trimmed CLmax vs static margin, SM 4–8 % by 0.25 % | AVL + XFOIL critical section | reads the stall at any CG the CG owners pick | B3 `CL-B3-XNP` 0.0709 m, `P:cg.x_range_m`, A3 claims | `sim/verify_wing.py` |
| Section clmax, hinge moments | SU2 8.5 INC_RANS SA, gmsh, 3 grids | the two separated-flow numbers XFOIL cannot settle alone | as XFOIL, same contour (XFOIL GDES FLAP) | `sim/cfd2d_section.py` |
| Hand checks | Schrenk, Helmbold, thin-airfoil hinge | independent of both codes | — | `sim/verify_wing.py` |

**No 3-D CFD.** The span loading, NP and trim are attached-flow quantities: AVL converges to 0.1 % on Xnp and
its lift slope is within 8 % of Helmbold. The pod and props enter through B3's whole-aircraft NP
(`ASM-B2R3-SM-EQUIV`). A 3-D RANS case would add nothing to the open item, the separated-flow clmax, which 2-D
steady RANS already shows to be grid-dependent. **No FEA:** the wing structure belongs to C2. B2 supplies the loads
in §6.

## 2. Stall on the settled geometry

FIG B2-R3-01 — Trimmed CLmax and stall speed vs static margin (`sim/fig/B2-R3-01-stall-vs-sm.svg`).

| CG point | x (m) | SM vs B3 NP 0.0709 m | Trimmed CLmax | Elevon at CLmax | Vs at 2.6 kg | Vs at 2.436 kg |
|---|---|---|---|---|---|---|
| Forward limit | 0.0509 | 6.25 % | 0.787 | −11.9° | 11.99 m/s | — |
| A3 basic | 0.0522 | 5.84 % | 0.790 | −11.1° | 11.97 m/s | — |
| A3 predicted | 0.0536 | 5.41 % | 0.792 | −10.4° | — | 11.59 m/s |
| Aft limit | 0.0548 | 5.03 % | 0.798 | −9.8° | 11.91 m/s | — |

- First stall at y 0.071 m (inboard end of the inboard elevon) at every SM. The tips stall last and the elevons keep
  roll authority at the stall. Unchanged from R2.
- The Re correction is applied (clmax −3.4 % per 1e5 of Re, XFOIL S5010 2.0–3.0e5). It moves Vs by < 0.02 m/s at
  the gate mass and by +0.02 m/s at the predicted mass.
- Elevon at CLmax, forward CG: −11.9° = 0.47 of the 25° travel. `elevon_trim_travel_max` 0.5 passes by 5 % (B3
  owns this check).

**Sensitivity: section clmax.** XFOIL with transition fixed at 2 % c gives clmax ≥ 1.095 at α 9.5° (the last
converged point) against 1.256 free, a ratio of 0.871. With that ratio the forward-CG stall at 2.6 kg is
**12.84 m/s** and 1.3 Vs is 16.7 m/s, above the 16 m/s cruise. A rough leading edge (tape seam, bugs, rain) is
therefore the largest single risk to `R-STALL` (CR-B2-16, CR-B2-17).

## 3. 2-D RANS campaign (SU2)

Set-up: INC_RANS, Spalart-Allmaras, fully turbulent, FDS + MUSCL, Venkatakrishnan K 5, chord-normalised, far field
50 c. Quad boundary layer 0.06 c (y⁺ ≈ 0.5–1), 0.008 c triangle band (L3) to 0.4 c, wake box to 4 c. The elevon is
deflected about the upper-skin hinge (x/c 0.78, 90 % thickness) exactly as in XFOIL. Each case runs 2 500
iterations, and the coefficients are means of the last 200. The hinge moment is integrated from surface pressure
(friction changes it by < 1e-5).

| Level | Cells (clean / −25°) | First cell | BL growth | Wall time per case |
|---|---|---|---|---|
| L1 | 12 440 / 12 617 | 8.0e-5 c | 1.21 | ≈ 870 s |
| L2 | 25 022 / 25 104 | 5.7e-5 c | 1.14 | ≈ 1 230 s |
| L3 | 50 294 / 49 710 | 4.0e-5 c | 1.10 | ≈ 1 720 s |

Results (L2 unless stated; usable = cl oscillation < 0.02 over the last 200 iterations):

| Case | Re | SU2 cl | XFOIL free cl | XFOIL tripped cl | SU2 C_h | XFOIL C_h inviscid / viscous | Usable |
|---|---|---|---|---|---|---|---|
| clean, α 4° | 2.6e5 | 0.516 | 0.580 | 0.538 | — | — | yes |
| clean, α 8° | 2.6e5 | 0.874 | 0.989 | 0.955 | — | — | yes |
| clean, α 10° | 2.6e5 | 0.897 (max) | 1.16 | ≥ 1.095 (α 9.5) | — | — | yes |
| clean, α 12°, L1 / L2 / L3 | 2.6e5 | 0.789 / 0.863 / 0.967 | 1.253 | — | — | — | L2 only |
| elevon −25°, α 0°, L1 / L2 / L3 | 4.4e5 | −0.86 / −1.27 / −1.18 | — | — | 0.0114 / 0.0125 / 0.0135 | 0.0211 (max) / 0.0125 (max conv.) | no (cl osc. 0.03–0.07) |
| elevon −25°, α −4° | 4.4e5 | −1.54 | — | — | 0.0128 | 0.0211 | yes |
| elevon +25°, α 4° | 4.4e5 | 1.36 | — | — | 0.0097 | 0.0145 | no |
| elevon −8.3°, α 2° (VD) | 5.9e5 | −0.21 | — | — | 0.0066 | 0.0085 (interp. 5°/10°, Re 4.5e5) | yes |

(SU2 C_h is shown as a magnitude, because its sign convention is opposite to XFOIL's FMOM.)

| Grid study (3 levels, r = √2) | L1 → L2 → L3 | Observed order | GCI fine (Fs 1.25) | Used for |
|---|---|---|---|---|
| C_h, −25°, α 0° | 0.0114 → 0.0125 → 0.0135 | 0.40 (monotone) | 47 % (Richardson 0.0186) | bound only |
| cl, clean α 12° | 0.789 → 0.863 → 0.967 | negative (diverging) | 71 % | not used |
| cl, −25°, α 0° | −0.86 → −1.27 → −1.18 | oscillatory | 30 % | not used |

What it means:
- **Attached flow agrees.** At α 4° SU2 is within 4 % of tripped XFOIL in cl, the like-for-like comparison. The
  further 7 % to free-transition XFOIL is the fully turbulent boundary layer, not the solver.
- **Hinge basis confirmed.** Every SU2 estimate of |C_h| at −25° (L1, L2, L3, α 0 and −4°, and the Richardson
  value 0.0186) is below the XFOIL inviscid 0.0211 that sizes the servo: ratio ≤ 0.88 (`CL-B2R3-HINGE-VISC-RATIO`).
  The L2/L3 values (0.0125–0.0135) match XFOIL's converged viscous maximum 0.0125. `ASM-B2-HINGE-INVISCID` holds.
- **clmax is not settled.** The steady RANS lift near and past stall changes 10–12 % per grid level and does not
  converge. Separation at this Re is unsteady and transitional, which steady fully turbulent SA cannot represent.
  Its best L2 value (0.897) is 0.82 × tripped XFOIL, so it does not contradict the tripped bracket, but it is
  not a design value. Settling clmax by analysis would need URANS with a transition model. The flight test is
  cheaper and is already in the plan (`T-B2-STALL`).

**Discarded campaigns** (kept in `sim/out/` for the record):

| Campaign | Fault | Evidence | Fix |
|---|---|---|---|
| 1 (`out/cfd`, 16k–64k cells) | stopped after ~170 iterations (machine shared with 14 SU2 jobs) | — | smaller grids |
| 2 (`out/cfd2`) | wall-normal growth 1.29–1.44 | cd 0.026 at α 4° | growth 1.10–1.21 |
| 3 (`out/cfd3`, `cfd2d_results_campaign3.json`) | quad layer 0.025 c, 0.02–0.04 c triangles at the BL edge | cd 0.025, stall at 8°, GCI 14–56 % | 0.06 c layer and 0.008 c band |
| 4 (`out/cfd4`, `cfd2d_results_campaign4.json`) | Venkatakrishnan K 0.05 limited MUSCL across the BL | cd 0.024 (pressure part 0.017) at α 4° | K 5 (test: cd 0.024 → 0.012; no limiter diverged) |

Remaining defect in campaign 5: K 5 leaves cd noisy (±0.02 over 200 iterations, mean 0.011 at α 4° against
tripped XFOIL 0.015). **No SU2 drag number is used.**

## 4. Discretisation checks and hand calculations

FIG B2-R3-02 — XFOIL panels, AVL lattice, SU2 grids (`sim/fig/B2-R3-02-convergence.svg`).

| Check | Levels | Result | Accept? |
|---|---|---|---|
| XFOIL clmax, S5010 Re 2.6e5 | 160 / 220 / 300 / 400 panels | 1.246 / 1.256 / 1.263 / 1.268 (spread 1.7 %, monotone) | yes: 220 used, finest +0.9 % (conservative) |
| AVL trimmed CLmax, SM 5 % | 6×0.5 / 8×0.6 / 12×1 / 16×1.4 | 0.797 / 0.790 / 0.799 / 0.803 (spread 1.7 %) | yes: 12×1 used, finest +0.5 % (conservative) |
| AVL Xnp | same 4 lattices | 0.07371 → 0.07378 m (0.1 %) | yes |
| SU2 | 3 grids | §3 | hinge bound only |
| Lift slope, AVL vs Helmbold (AR 3.59, a₀ 6.61 /rad) | — | 3.48 vs 3.79 /rad, ratio 0.92 | yes: fins, elevon gaps, AVL vs a lifting-line estimate |
| Root bending, AVL vs Schrenk | — | ȳ 0.422 vs 0.462 b/2: Schrenk +9.6 % | yes: Schrenk is the conservative bound |
| Span loading vs elliptic | — | ȳ 0.422 vs 0.424 b/2 | yes |
| Hinge moment, SU2 vs XFOIL | — | §3, ratio ≤ 0.88 | yes |

`ASM-B2R3-CONV-RULE`: a discretised value is accepted when the finest level gives a value at least as favourable.
Both XFOIL and AVL meet this rule. Their 1.7 % spreads exceed the 1 % aim of R2 and are reported, not hidden.

## 5. Comparison with R2 (earlier hand-checked analysis)

| Quantity | R2 (0.19 m half-fins, old CG range) | R3 (as designed) | Change | Why |
|---|---|---|---|---|
| Xnp props-off, wing + fins | 0.07376 m | 0.07377 m | +0.01 mm | fin height barely moves the NP |
| Trimmed CLmax, SM 5 % | 0.798 | 0.799 | +0.1 % | — |
| Vs 2.6 kg, forward CG | 12.06 m/s (`FAIL` −0.5 %) | 11.99 m/s (+0.1 %) | −0.6 % | A1-R4 moved the forward limit aft to 0.0509 m (SM 7.8 → 6.25 %) |
| Hinge moment per servo | 0.257 N·m (25°, 20.8 m/s) | 0.440 N·m (25°, VD) / 0.250 (25°, VA) | — | requirement now at VD 27.2 m/s (D-29/D-50) |
| Servo torque | 3.93 kgf·cm (1 : 1) | 3.49 through D6's linkage (6.73 at 1 : 1) | — | D6 torque factor 0.518 (`CL-D6-TORQUE-FACTOR`) |
| Root bending, 1 g, 2.6 kg | 3.09 N·m | 3.09 N·m | 0 | — |
| Cn_β props-off, α 4° | +0.052 /rad (ref CG 0.044) | +0.054 /rad (ref CG 0.0522) | +4 % | taller fins (the aft reference CG alone would lower it) |

## 6. Loads for C1 / C2 (unchanged in substance)

| Quantity | Value | Unit | Source | Status |
|---|---|---|---|---|
| Lift centroid, half-wing (AVL, trimmed) | 0.422 | b/2 | `P:b2sim.avl.ybar_frac` | `UNVERIFIED` |
| Root bending, 1 g, 2.6 kg | 3.09 | N·m | `CL-B2-ROOT-BM-1G` | `UNVERIFIED` |
| Root bending, n 3.4 (limit), AVL / Schrenk bound | 10.5 / 11.5 | N·m | `CL-B2R3-ROOT-BM-LIMIT`, `-SCHRENK` | `UNVERIFIED` |
| Root bending, ultimate (× 1.5), AVL / Schrenk | 15.8 / 17.3 | N·m | × `P:requirements.safety_factor_ult` | `UNVERIFIED` |
| Root torsion about the spar, per N of half-lift | 0.0254 | m | `P:b2.avl.torsion_root_m_per_N` | `UNVERIFIED` |
| Negative section clmax (n −1.5 case) | −0.435 | — | `CL-B2-CLMIN-2D` | `UNVERIFIED` |
| Strip shear / bending / torsion | file | — | `team/B2/out/loads_spanwise.json` (A1-R4 geometry) | `MODELLED` |

## 7. Re-run

```
python -I redesign/team/B2/xfoil_wing.py && python -I redesign/team/B2/avl_wing.py     # R2 base (cached)
python -I redesign/team/B2/sim/cfd2d_section.py                                        # SU2, ~25 min on 14 cores
python -I redesign/team/B2/sim/xfoil_tripped.py                                        # ~5 min
python -I redesign/team/B2/sim/verify_wing.py            # AVL SM sweep, lattices, panels (~15 min); --params rewrites sim/params.json only
python -I redesign/team/B2/sim/sim_claims.py && python redesign/team/B2/sim/plots_sim.py
python -I redesign/proofs/build_graph.py                 # no B2 error; other roles' drifts are theirs
```

## 8. Open issues

| Issue | Owner | Closes with |
|---|---|---|
| `R-STALL` / `R-TRANSITION` margins (+0.1 %) are below the clmax uncertainty (−13 % tripped) | A1, A2, F4, H2 | `T-B2-STALL` on the twin and the first build, before `ARSPD_FBW_MIN` is frozen (CR-B2-16) |
| Tape seam 15 mm aft of the LE may trip the boundary layer | D1 | LE wrap rule (CR-B2-17) |
| SU2 clmax not grid-converged; cd noisy | B2 | not needed if `T-B2-STALL` passes; otherwise URANS + transition model |
| Pod and props only through B3's NP (`ASM-B2R3-SM-EQUIV`) | B3 | flight trim log |
