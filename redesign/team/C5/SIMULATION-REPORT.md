# C5 Landing / impact: simulation report

Simulation and verification round on the settled geometry. Revision **C5-S1**, 2026-11-10. Geometry: D5-R5 foot
stack (`subsystems/landing/params.json`, `fusion/landing.py` `stack()`), D5-R4 cartridges, A3-R6a roll-up (2.322 kg
basic, 2.436 kg predicted, 2.6 kg gate; I 0.173 / 0.044 / 0.168 kg·m²; CG x 0.0529 m, z 0.0185 m, y −0.0011 m).
Claims: `team/C5/claims.sim.json` (17 claims, `CL-C5-SIM-INPUTS-STALE` = 0).

**Verdict: the as-designed feet fail four landing requirements.** The hand and planar models in `LANDING.md`
missed two effects: a diagonal touchdown, where one foot takes the energy alone, and pad scrub under friction. The
printed shoe is also much weaker than D5's beam check shows. Change requests CR-C5-16 to CR-C5-19 are filed.

## 1. What was run and why that tool

| Question | Tool | Why this fidelity | Inputs |
|---|---|---|---|
| Stroke, load factor, side load and tip-over in a real touchdown | `sim/landing_sim3d.py`: 6-DOF rigid body, 4 elastic-plastic piston feet, 16 pad-corner contacts, regularised Coulomb friction μ 0.7, rotor lift 2/3 W held 0.3 s then ramped to 0 by 0.6 s | The planar model (2 contacts, no friction, pitch and roll taken one at a time) cannot show single-foot-first landings or friction side load. CFD is not needed: the only aerodynamic load is wind drag, Cd90 1.28 on the planform. | A3-R6a mass, inertia and CG; D5 plateau U 39.6 / L 35.4 N, stroke 38 mm (35 mm usable), pad outline, μ |
| Stress in the printed shoe GER-001 under the foot side load | `sim/fea_shoe.py` → gmsh quad section swept to trilinear hexes → SU2 8.5 `ELASTICITY` | The shoe is primary landing structure. D5's beam check (SF 1.05) leaves out the snap windows, the corner fillets and the sleeve that runs past the fin TE. | D5-R5 stack, PETG E 2.0 GPa, ν 0.38, allowable 40 MPa (`ASM-D5-PETG-SIGMA`), D5's tine lever |
| Envelopes | `sim/sink_sweep.py` (sink 0.8 to 1.3 m/s, 24 directions at 10°), `sim/side_check.py` (side-load dt and contact-model sensitivity) | Find the limit that does pass | as above |

Load cases: design landing 1.5 m/s sink, tilt ≤ 10° in any direction (pitch and roll combined, 2.5° and 45° steps,
97 cases per mass), at 3 masses; 128 drift cases (0.3 m/s in 8 directions × 8 tilts × 2 sinks); wind landings,
broadside and spanwise, steady or lull, hover lean + 10°. Ultimate factor 1.5 (`requirements.safety_factor_ult`).

## 2. Verification

| Check | Levels | Result | Status |
|---|---|---|---|
| 3-D sim time step (worst hard case) | 80 / 40 / 20 / 10 / 5 µs | stroke 38.585 → 38.588 mm (0.01 %), side 277.7 → 277.6 N; production run at 40 µs | `CHECKED` |
| 3-D sim tip-over threshold vs time step | 80 / 40 / 20 / 10 µs | 24.64 / 24.39 / 24.39 / 24.39° | `CHECKED` |
| Side load (governing non-bottomed case) vs dt and contact model | 4 dt; pad stiffness ×0.5 / ×2, piston mass ×2, friction regularisation ×0.5 | 39.19–39.33 N (< 0.4 %); μ 0.5 → 29.1 N, so the side load scales with μ | `CHECKED` |
| 3-D sim vs planar / hand, level 1.5 m/s at gate mass | — | stroke 22.6 vs 23.5 mm planar (−4 %); n 5.88 vs 5.88; free drop 25.6 vs 26.2 mm hand (−2 %) | `CHECKED` |
| FEA element vs beam theory: cantilever strip 0.8 × 6 × 20 mm | 2 / 3 / 4 hexes through 0.8 mm | tip deflection 0.423 / 0.462 / 0.478 mm, Richardson 0.482 mm vs Euler–Bernoulli 0.521 mm (−7.5 %; the clamped root stops anticlastic bending, so the strip acts stiffer than a beam). Mid-span surface stress +0.8 / +4.9 / +5.4 % vs beam. The model reads stress slightly high, which is conservative. | `CHECKED` |
| Shoe FEA mesh convergence | wall h 0.40 / 0.32 / 0.267 mm (2 / 2.5 / 3 elements through 0.8 mm; 61 k / 108 k / 182 k hexes) | +y rim 105.1 / 105.7 / 106.1 MPa, observed order 4.4, Richardson 106.4 MPa, GCI 0.35 %. +z rim 93.6 / 90.4 / 91.0 MPa (oscillates within 3.5 %). Window strips +y GCI 1.9 %, +z 2.3 %. End deflection GCI 0.7 / 1.8 %. | `CHECKED` |
| Singular points excluded | — | The +z peak "aft box" sits on the bonded-floor clamp edge at the fin TE (sharp, 122 MPa, grows with refinement). It is reported but not used. The governing value is the rim body ≥ 1 mm from the rim step, at the modelled 0.4 mm inner fillet. | — |

## 3. Results against the earlier hand / planar calculation

| Quantity | Hand / planar (C5-R5) | Simulation (C5-S1) | Limit | Margin | Status |
|---|---|---|---|---|---|
| Worst foot stroke, 1.5 m/s, ≤ 10° any direction, 2.6 kg | 31.5 mm (pitch pair first) | **38.6 mm** (diagonal, one foot first, reaches the 38 mm rim stop) | ≤ 35 mm usable | −10 % | `FAIL` |
| Same, pitch-only or roll-only tilt | 31.5 / 27.9 mm | 37.5 mm (pad edge pivot + friction) | ≤ 35 mm | −7 % | `FAIL` |
| Same at A3 basic mass 2.32 kg | — | 38.4 mm | ≤ 35 mm | −10 % | `FAIL` |
| Smallest touchdown tilt that bottoms a foot (1.5 m/s) | > 10° | 5.0° | ≥ 10° | −50 % | `FAIL` |
| Largest sink speed for 10° in any of 24 directions | — | 1.2 m/s (2.6 kg: 34.5 mm; 2.32 kg: 30.6 mm) | ≥ 1.5 m/s | −20 % | `FAIL` |
| Peak load factor, level, as-designed 2.32 kg | 5.88 (sized at 2.6 kg) | 6.59 (4 × 37.5 N / 22.8 N) | ≤ 6.0 | −10 % | `FAIL` |
| Peak n when a foot bottoms | — | 11.5–14.5 (rim stop) | ≤ 6.0 | — | `FAIL` (follows from stroke) |
| Sustained foot side load (1 ms filter, not bottomed) | 22.9 N (`CL-C5-FOOT-SIDE-LOAD`) | **39.3 N** (×1.72); ultimate 59.0 N | — | — | `MODELLED` |
| Shoe von Mises at D5's load basis (34.4 N ult side, 111 N lip) | 38.1 MPa (D5 beam, SF 1.05) | **106 MPa** (FEA/beam 2.78) | ≤ 40 MPa | RF 0.38 | `FAIL` |
| Shoe at the simulated side load (59.0 N ult) | — | 183 MPa | ≤ 40 MPa | RF 0.22 | `FAIL` |
| Side load the shoe takes at RF 1 (limit) | 24 N (D5) | 8.6 N | ≥ 39.3 N | −78 % | `FAIL` |
| Wingtip TE strike onset tilt | +2.3 mm clear at the worst roll | 7.5° (corner touches inside the envelope) | ≥ 10° | −25 % | `FAIL` (corner cap GER-007 takes it; CR-C5-04) |
| Broadside landing wind limit (lull, lean + 10°) | 4.44 m/s static | 4.0 m/s (sink 0.5), 4.5 (sink 1.5); steady wind 5.0 | ≥ 5 m/s | −20 % | `FAIL` (as at R5; wingtip-into-wind heading, CR-C5-05) |
| Spanwise landing wind limit | 8.3 m/s | 8.0 m/s | ≥ 8 m/s | 0 % | `MODELLED` |
| Drift landings (0.3 m/s, 10°) that tip over | 0 | 0 of 128 (max tilt 18.7°) | 0 | — | `MODELLED` |

What changed and why:

1. **Diagonal touchdowns.** With pitch and roll combined, one foot lands before the other three.
   It crushes alone at 37.5 N while the aircraft rotates over it and uses up the 35 mm before the others share the
   load. The planar model only had pitch or roll, so a pair of feet always shared the load. This holds at every mass,
   so it is a stroke and sink limit, not a mass problem.
2. **Side load.** The pads grip (μ 0.7) while the aircraft rolls over the first foot, so the transverse load reaches
   about μ × plateau plus the tilt component. The hand value took friction from a level slide. The result does not
   depend on pad stiffness, piston mass or time step (< 0.4 %), and it scales with μ.
3. **Shoe stress.** The tine bears on the last 2 mm of the sleeve wall next to the free end. That loads a narrow
   strip of the plate, not the 6 mm rim acting as a fixed-ended beam (D5: M = R b / 12). The peak sits in the 0.4 mm
   inside corner between the side wall and the floor. A thicker wall alone is not enough (§4).

## 4. Shoe design-fix study (coarse level h 0.4 mm: within 1.2 % of the extrapolated +y rim value, 3 % for +z)

| Variant (D5 inputs) | +y rim | +z rim | Governing | RF at 59.0 N ult (sim) | RF at 34.4 N ult (D5 basis) |
|---|---|---|---|---|---|
| As designed: wall 0.8, rim 1.2, inner fillet 0.4, engagement 12 mm | 105.1 | 93.6 | 105.1 MPa | 0.22 | 0.38 |
| Wall 1.6 mm (rim 1.2, fillet 0.4, engagement 12) | 65.7 | 55.4 | 65.7 MPa | 0.35 | 0.61 |
| Wall 1.6, rim 2.4 mm | 44.1 | 36.3 | 44.1 MPa | 0.53 | 0.91 |
| Wall 2.0, rim 3.0, inside fillet 1.0 mm | 23.3 | 19.8 | 23.3 MPa | 1.00 | 1.72 |
| Wall 2.0, rim 3.0, fillet 1.0, engagement 25 mm (lip reaction 75.5 N) | 16.4 | 13.8 | 16.4 MPa | 1.42 | 2.44 |

Stress in MPa at each variant's own lip reaction for D5's 34.4 N ultimate side load; RF = 40 MPa / σ, and the sim
column scales σ by 59.0 / 34.4 (linear model). These are study values, not proof-chain claims.

- D5's stack uses one wall thickness `w` for the piston and the sleeve, so the sleeve outside grows from
  21.1 × 17.1 mm to 24.3 × 20.3 mm (w 1.6) or 25.9 × 21.9 mm (w 2.0). Thickening only the sleeve is lighter and needs
  a C5 re-run.
- Engagement 25 mm moves the tine open end 13 mm forward. Fitting it is D5's job.
- The clamp-edge peaks at the fin TE (sharp, singular) are excluded as before: 47.8 / 30.2 / 18.6 MPa in the last
  three variants.
- **Recommended:** wall 2.0, rim 3.0, inside fillet 1.0 mm **and** engagement 25 mm, which gives RF 1.42 at the
  simulated load. Without the longer engagement, RF is 1.00 and the coarse mesh reads about 1 % low.

## 5. Requirements that now fail (CR filed)

| Requirement / claim | Result | CR |
|---|---|---|
| R-LANDING-IMPACT: 1.5 m/s at 10° within usable stroke (`CL-C5-SIM3D-STROKE`, `-BOTTOM-TILT`, `-V-SINK-10`) | 38.6 mm vs 35 mm; holds at 1.2 m/s | CR-C5-17 (A2, D5, F4, C1) |
| `requirements.landing_n_design` 6.0 at the flying mass (`CL-C5-SIM3D-N`) | 6.59 at 2.32 kg | CR-C5-19 (D5, C1, A3) |
| Foot side load basis (`CL-C5-SIM3D-SIDE-LOAD` replaces `CL-C5-FOOT-SIDE-LOAD`) | 39.3 N vs 22.9 N | CR-C5-16 (D5, C4/D3, C1) |
| Shoe GER-001 strength (`CL-C5-FEA-SHOE-SF`, `-SF-HAND`) | RF 0.22 / 0.38 | CR-C5-18 (D5) |
| R-WIND broadside landing (`CL-C5-SIM3D-V-BROADSIDE`) | 4.0 m/s | CR-C5-05 (F4, H3; already open) |

## 6. Figures

| Figure | File |
|---|---|
| FIG C5-S1: worst foot stroke and peak n vs tilt direction, 2.6 kg, 1.5 m/s | `sim/fig/fig-c5-s1-envelope.svg` |
| FIG C5-S2: largest tilt vs wind at touchdown, broadside and spanwise | `sim/fig/fig-c5-s2-wind-tipover.svg` |
| FIG C5-S3: time-step convergence of stroke and side load | `sim/fig/fig-c5-s3-dt-convergence.svg` |
| FIG C5-S4: worst-case foot stroke and side-load histories | `sim/fig/fig-c5-s4-history.svg` |
| FIG C5-S5: shoe FEA mesh convergence vs the D5 beam and the allowable | `sim/fig/fig-c5-s5-fea-convergence.svg` |

## 7. Re-run (from the repo root)

| Step | Command | Time |
|---|---|---|
| 3-D touchdown sim | `python -I redesign/team/C5/sim/landing_sim3d.py` | ≈ 27 min |
| Envelopes | `python -I redesign/team/C5/sim/sink_sweep.py`; `python -I redesign/team/C5/sim/side_check.py` | 5 + 2 min |
| Shoe FEA, 3 levels × 2 cases | `sh redesign/team/C5/sim/run_fea.sh` (runs `fea_shoe.py --one` in parallel, then `--collect`) | ≈ 50 min |
| Design variants | `sh redesign/team/C5/sim/run_variants.sh` (`C5_FEA_VARIANT="w=…,rim_t=…,r_in=…,engage=…"`, m) | ≈ 15 min |
| Figures | `python redesign/team/C5/sim/plots.py` (matplotlib needs the user site, so no `-I`) | 10 s |
| Claims | `python -I redesign/team/C5/landing_sim_claims.py`, then `python -I redesign/proofs/build_graph.py` | < 1 s |

`CL-C5-SIM-INPUTS-STALE` compares the 11 inputs each run recorded with the live nodes. If it is above 0, re-run.
Raw records: `sim/out/*.json`; SU2 configs and logs: `sim/runs/`.

The full `build_graph.py` was not finished in this round. On 2026-11-10 it ran for more than 45 min on a shared,
loaded machine and was stopped. `landing_sim_claims.py` itself ran cleanly: 17 claims, stale count 0. The next
build should show the new `CL-C5-SIM3D-*` / `CL-C5-FEA-*` margins as FAIL, and those failures are the intended
signal.

## 8. Limits of the models (`UNVERIFIED` until T-C5-AIRCRAFT-DROP and T-C5-SHOE-SIDE-FAIL)

- The crusher is an ideal elastic-plastic plateau, and the coupon plateau is not yet measured. Pad corners are
  linear springs. The airframe is rigid, so fin flexibility, which would soften the side load, is left out.
- Lift is held vertical through the CG, with no attitude control after touchdown. That is conservative for
  tip-over and for stroke.
- The FEA is linear elastic, with no PETG yield or layer anisotropy, and its bonded faces are fully clamped. A
  printed part's Z (layer) strength is about half of 40 MPa, so if the rim is printed with layers across the load,
  the margins are lower again.
