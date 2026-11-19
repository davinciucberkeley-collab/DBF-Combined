# Analysis records (R-PHY-07)

One block per analysis, ten fields. Category is one of: interference (static), interference during motion,
kinematics, rigid-body dynamics, FEA, CFD, flight dynamics, hand calculation, illustrative animation. A record
supports only claims of its own category.

Earlier concept A analyses (FEA D-209/D-210, flutter, landing, SITL) are traced in `docs/capability-audit.md` §2;
records for the ones reused in the film are added under T-057/T-058.

---

## AR-001 Elevon linkage kinematics (T-018)
- **Category:** kinematics (spatial RSSR linkage: servo arm rotates about vertical z, horn hole about the spanwise hinge y, rigid rod between).
- **Solver / engine:** own constraint solve, `redesign/qp/A/mechanism/linkage_core.py` (Newton with brentq cross-check); Python 3.14.2, numpy 2.5.4, scipy 1.18.1.
- **Model version:** git `0f2e3ec8`; geometry imported live from `redesign/qp/A/cad/amodel/electrical.py` and `common.py` (not retyped).
- **Inputs:** arm 12.0 mm (`ARM_R`), horn hole radius 12.9 mm (`HORN_R`), hinge x 183.75 mm, z 0.29 mm, rod z 9.3 mm, servo axis x 140.5 mm, y ±200 mm (EST), rod length from neutral endpoints 52.49 mm; limits ±20° (authority), ±21° (stop).
- **Assumptions:** rigid parts, zero free play, ideal ball-type ends at the Z-bend and clevis; servo travel ±45° (assumption: ES3054HV travel not published, "—"); joint misalignment allowances from EST hole sizes (Z-bend 4.265° used as the pass line in K5, clevis 14.0°).
- **Boundary conditions:** servo case and hinge line fixed to the wing; sweep δ = −21…+21° in 0.05° steps (841 poses), both sides.
- **Numerical settings:** residual tolerance 1e-9 m; achieved max residual 2.8e-17 m; Newton vs brentq disagreement 8.8e-15; L/R symmetry error 1.3e-15 rad.
- **Outputs:** `redesign/qp/A/mechanism/out/linkage_kinematics.{json,csv,png}`. Servo angle for +21° = +13.30°, for −21° = −18.30° (±20°: +12.78° / −17.30°). Gearing dθ/dδ 1.00…1.95 (1.33 at neutral). Min Jacobian singular value 0.323 (at +21°). Toggle at +57.5° / −67.0° (≥ 36° beyond the stops). Horn transmission angle min 27.5° (at +21°). Max rod misalignment: Z-bend 4.270°, clevis 0.66°.
- **Acceptance criteria (set before the run):** K1 residual < 1e-9 m; K2 L/R symmetry; K3 servo travel covers ±21°; K4 σ_min ≥ 0.25; K5 joint misalignment ≤ allowance; K6 gearing formula check. Info: transmission angle ≥ 40° rule of thumb.
- **Result:** **FAIL** overall: K1–K4, K6 pass; K5 Z-bend 4.270° vs 4.265° (marginal, allowance is EST). Transmission angle 27.5° misses the 40° rule. Independent check (conductor): neutral gearing by hand = arm / vertical lever = 12.0 / (9.3 − 0.29) = 1.33, matches.
- **Limitations:** allowances and servo travel are estimates; horn and arm shapes are EST in the CAD (capability-audit §4); no compliance or backlash.

## AR-002 Elevon drive rigid-body dynamics (T-019, T-056)
- **Category:** rigid-body dynamics (1-DOF, frictionless, constrained).
- **Solver / engine:** `redesign/qp/A/mechanism/elevon_dynamics.py`, scipy `solve_ivp` DOP853, θ carried as a third state so the constraint residual measures drift.
- **Model version:** git `0f2e3ec8`; kinematics from AR-001.
- **Inputs:** elevon + balance inertia about the hinge 1.370e-5 kg·m² (CAD) + horn point mass 1.66e-7 (EST); arm inertia 4.2e-8 (CAD outline, 1 g EST); servo stall 0.397 N·m at 7.2 V (EST, `params-A.json`) and 0.333 N·m at 6.0 V (SERVO.md); no-load speed 0.13 s/60°; hinge moment 0.146 N·m at VD (linear with δ and constant variants); rod 1.2 mm steel, E = 207 GPa (cited in script header).
- **Assumptions:** rod massless (0.97 g neglected), no friction, no tape-hinge stiffness, servo rotor inertia not modelled ("—"), preload/damper not included.
- **Boundary conditions:** (a) unpowered free swing with initial rate; (b) steps 0→+20° and 0→−20° under hinge load at both voltages.
- **Numerical settings:** rtol 1e-9, atol 1e-12; 845–870 steps per run.
- **Outputs:** `out/linkage_dynamics.{json,png}`, `_freeswing.csv`, `_steps.csv`. Free-swing energy error 8.4e-12 (relative); constraint residual ≤ 7e-16 m; arm-side vs elevon-side rod force mismatch ≤ 7e-15 N. Step time 0.041–0.064 s. Peak rod force 30.3 N (stall-limited); hold force 23.9 N at +20°; Euler load 75.5 N. Hold torque needed at +20° 0.278 N·m → margin 1.43 (7.2 V EST), 1.20 (6.0 V); at −20° margin 2.68.
- **Acceptance criteria:** D1 energy < 1e-6; D2 residual < 1e-9 m; D3 peak compression ≤ Euler/2; D4 hold margin ≥ 1.5 (project factor); D5 reach within 0.5° in < 0.25 s; D6 force consistency < 1e-6 N.
- **Result:** **FAIL** on D4 (+20° side: 1.43 and 1.20 < 1.5); D1–D3, D5, D6 pass. Root cause: gearing 1.91 at +20° (AR-001), where SERVO.md assumed 1:1. Independent check (conductor): 0.146 × 1.905 = 0.278 N·m; 0.397 / 0.278 = 1.43, matches.
- **Limitations:** stall torque at 7.2 V is interpolated (EST); hinge moment is an estimate; frictionless first model (spec 5.2).

## AR-003 Elevon linkage swept collision (T-020)
- **Category:** interference during motion (poses from AR-001).
- **Solver / engine:** `redesign/qp/A/mechanism/elevon_sweep_collision.py`, analytic geometry (cylinders, boxes, prisms built from the CAD constants). The mesh path was not available: trimesh, manifold3d not installed in the system Python and no Blender call made by the agent.
- **Model version:** git `0f2e3ec8`.
- **Inputs:** moving: servo arm, rod, clevis, horn, elevon; static: servo case, wing surface, caps (constants from `electrical.py`, `wing.py`).
- **Assumptions:** analytic shapes match the CAD solids to the stated EST dimensions; rod straight between the joint centres.
- **Boundary conditions:** δ = −21…+21° every 0.5°, both sides.
- **Numerical settings:** gate tolerance 0.05 mm (project collision gate).
- **Outputs:** `out/linkage_sweep_collision.{json,csv,png}`. Rod bottom tangent to the arm top at neutral (`ROD_Z` = arm top + rod radius); rod penetrates the arm tip from +7.5° (both sides), max 0.151 mm at +21°. Smallest positive clearance elsewhere 0.081 mm (clevis cheek to horn blade at −21°).
- **Acceptance criteria:** no penetration > 0.05 mm along the path.
- **Result:** **FAIL** (CAD defect: the rod is modelled resting on the arm instead of passing through the Z-bend hole with clearance).
- **Limitations:** analytic, not mesh-based; must be repeated on the CAD meshes (Blender BVH via `collide_a.py` path) after the fix.

## Open actions from AR-001…AR-003
One geometry change addresses all three failures (ladder rung 2, modify geometry, no added mass): put the horn hole
above the hinge so the horn is perpendicular to the rod at neutral (symmetric gearing ≈ arm/lever, transmission
angle 90° at neutral, smaller rod pitch), and model the Z-bend through the arm hole with running clearance.
Tracked as T-061 (D-212).
