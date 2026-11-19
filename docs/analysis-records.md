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

---

## After D-212, first version (T-061, 2026-11-18) - SUPERSEDED and REJECTED (review `docs/audits/2026-11-18-D212-review.md`: the arm end was modelled at a fixed height; see "After D-212 rev 2"). Kept as the record.
The records above are kept as the first results. Change: horn hole directly above the hinge line at the unchanged radius 12.9 mm, rod axis raised to the hole height (ROD_Z 9.30 to 13.19 mm), Z-bend leg through the 1.5 mm arm hole with the rod 3.89 mm clear of the arm top, horn blade redrawn (decision D-212 in `redesign/params/CHANGE-LOG.md`, trade table in `docs/engineering-decisions.md`). Model version for all three: git `164c815a` plus the uncommitted D-212 edits (`electrical.py`, `elevon_sweep_collision.py`); geometry still imported live. Re-run with `python -I redesign/qp/A/mechanism/<script>.py` (7.5 s, 25 s, 40 s wall); outputs overwrite `redesign/qp/A/mechanism/out/`.

### AR-001 after D-212 (kinematics)
- **Inputs changed:** hole x = XH (was XH + 9.24 mm), hole z 13.19 mm over the hinge axis z 0.29 mm (radius 12.9 mm), rod length hole to hole 43.25 mm (was 52.49), arm 12.0 mm.
- **Result: PASS (K1-K6).** Residual 2.8e-17 m; solver disagreement 4.0e-15; L/R symmetry 1.3e-15 rad. Servo angle for +21 deg = +22.76 deg, for -21 deg = -22.56 deg (+/-20 deg: +21.65 / -21.49), within the assumed +/-45 deg. Gearing d delta/d theta 0.904 to 0.935 (neutral 0.930; was 1.00 to 1.95). Min Jacobian singular value 0.603 (was 0.323, needs 0.25). Toggle at +53.6 deg / -76.6 deg (32.6 deg beyond the +21 deg stop). Horn transmission angle min 67.9 deg (was 27.5; the 40 deg rule of thumb is met). Max rod misalignment Z-bend 1.135 deg (line 4.265 deg, was 4.270), clevis 1.24 deg (line 7.0 deg, was 0.66 deg: larger because the rod is now short and the rod yaw follows the arm swing; still passes).
- **Independent check:** neutral gearing by hand = arm / vertical lever = 12.0 / 12.9 = 0.930, matches.
- **Limitations (unchanged):** allowances and servo travel are estimates; horn and arm shapes are EST.

### AR-002 after D-212 (rigid-body dynamics)
- **Result: PASS (D1-D6).** Hold margin at +20 deg 2.998 and at -20 deg 2.911 at 7.2 V EST (min 2.91; was 1.43), 2.51 / 2.44 at 6.0 V (min 2.44; was 1.20); hold torque needed 0.132 N m (+20 deg) and 0.136 N m (-20 deg), hold rod force 12.1 N max (was 23.9). Step time 0.055 to 0.077 s; peak rod force 30.2 N (stall-limited), Euler load 111 N (was 75.5, shorter rod; D3 needs peak <= Euler/2 = 55.6 N). Free-swing energy and residual checks still at round-off (constraint residual 2.8e-17 m).
- **Independent check:** 0.146 N m x 0.907 (gearing at +20 deg) = 0.132 N m; 0.397 / 0.132 = 3.00, matches.
- **New observation:** the project claim CL-A-SERVO-COLD (params horn 12.9 / arm 12, model factor 1.57 against 1.5) is consistent with this geometry: the true gearing is 0.91 to 0.94, close to the 12 / 12.9 = 0.93 the claim assumes. On the D-211 geometry it was not (gearing up to 1.95).
- **Limitations (unchanged):** stall torque at 7.2 V interpolated (EST); hinge moment estimated; frictionless; the Z-bend leg moment (12.1 N x 4.49 mm = 0.054 N m, about 321 MPa in the 1.2 mm leg) is a hand calculation, not part of the model, and the rod yield is not published ("-").

### AR-003 after D-212 (interference during motion)
- **Analytic sweep (same script, delta -21 to +21 deg every 0.5 deg, both sides): PASS.** No penetration (170 pairs); the rod-to-arm contact is gone (rod to arm 3.85 mm minimum, 3.89 mm at neutral; was 0 by construction and -0.151 mm at +21 deg). Smallest positive clearance 0.053 mm: clevis cheek to horn blade at +21 deg (design gap 0.1 mm EST; was 0.081 mm, clevis cheek to horn at -21 deg). Z-bend pin to arm hole wall 0.15 mm radial at neutral. Elevon section to core 0.90 mm below the hinge line.
- **Mesh check (was missing in AR-003):** `A_ELEV_POSE=<angle> python -I redesign/qp/A/cad/collide_a.py` (Blender 4.5.14 BVH, tolerance 0.05 mm): static (pose 0), +/-10 deg and +/-21 deg all report 0 part pairs penetrating by more than 0.05 mm; wire ends 0, folds 0. Wall times 151 s, 457 s, 460 s (the later two with other jobs running). Scope: the mesh poses turn the elevon, horn, clevis pin and everything bonded to them; the rod and arm are held out as linked parts, so their path is covered only by the analytic sweep above. A first mesh run (plate from 0.8 mm aft of the hinge line) failed with the horn plate 0.41 mm into the elevon nose; the plate now starts 2.5 mm aft (recorded in D-212).
- **Limitations:** analytic solids match the CAD to the EST dimensions; mesh poses 0, 10 and 21 deg only (the gate turns each limit, not a sweep).

### Gates on the changed CAD
`python -I redesign/qp/A/cad/stop_check.py` PASS (23 s); `collide_a.py` PASS at the default 21 deg pose (460 s wall, last run). Not run: `assembly_check.py` and `collide.py --glb` (the GLB is regenerated by the film/export pipeline, not by this task): the horn and rod parts changed shape, so they must be re-run at the next export.

---

## After D-212 rev 2 (T-061, 2026-11-18) - SUPERSEDED for the horn attachment, hole sizes and stall force by "After D-212 rev 3" (review `docs/audits/2026-11-18-D212r2-review.md`); its linkage results stand. Kept as the record.
Change: the arm-side joint is a standard Z-bend leg in the arm hole, free in z over 0.3 mm (the rod resting on the arm, up to a keeper); horn hole over the hinge line at the rod height (9.155 mm), servo arm hole 8.5 mm, printed horn (decision D-212 rev 2 in `redesign/params/CHANGE-LOG.md`, trade table in `docs/engineering-decisions.md`). Model version: git `164c815a` plus the uncommitted D-212 rev 2 edits. The joint height is a model input: `ELEVON_ZJ=mid|lo|hi` (9.45 / 9.30 / 9.60 mm), every script is run in all three states; `_zlo` / `_zhi` files hold the end states. Wall times per script and state: 8 s, 25 s, 40 s (kinematics, dynamics, sweep). Commands: `ELEVON_ZJ=<state> python -I redesign/qp/A/mechanism/<script>.py`; `python -I redesign/qp/A/mechanism/linkage_loads_check.py` after the dynamics run.

### AR-001 after D-212 rev 2 (kinematics)
- **Result: PASS (K1-K7) in mid, lo and hi.** Servo angle +22.77 / -22.64 deg for +21 / -21 deg (+21.67 / -21.56 at +-20), within the assumed +-45 deg. Gearing d delta / d theta 0.906 to 0.929 (neutral 0.928; D-211: 1.00 to 1.95). Min singular value 0.604 (needs 0.25). Horn transmission angle min 68.0 to 68.4 deg (rule of thumb 40). Z-bend misalignment 0.81 deg (mid), 0.61 (lo), 1.00 (hi) against the 4.265 deg line; clevis 0.88 deg. Plus-side toggle at +56.3 deg (35 deg beyond the stop), minus side not reachable. **K7 free play from the Z-bend freedom: 0.028 deg** at a fixed servo angle between the lo and hi joint heights (limit 0.25 deg, EST). Residual 3e-17 m.
- **Independent check:** neutral gearing by hand = arm / horn lever = 8.5 / 9.155 = 0.928, matches.
- **Limitations:** allowances and servo travel are estimates; the 0.3 mm vertical freedom (`ROD_KEEP`) is an EST, the keeper and the boss gap are "-"; the existing hole clearance free play (0.3 mm diametral over the 9.155 mm lever, about 1.9 deg if both holes are loose) is not in the rigid model and is a separate E1 measurement (review F-8).

### AR-002 after D-212 rev 2 (rigid-body dynamics)
- **Result: PASS (D1-D6) in mid, lo and hi.** Hold margin 2.93 at 7.2 V EST (2.93 lo, 2.93 hi) and 2.46 at 6.0 V (D-211: 1.43 / 1.20; first D-212: 2.91 / 2.44 on the invalid fixed point). Hold rod force 17.1 N; peak rod force 42.7 N (stall-limited, arm 8.5 mm), Euler 111 N, half 55.6 N (D3 passes); step time 0.056 to 0.076 s. The dynamics start state now solves delta for theta = 0 (at the lo / hi heights the fixed rod length makes delta(theta = 0) differ from 0 by 0.03 deg).
- **Independent check:** 0.146 N m x 0.929 = 0.136 N m; 0.397 / 0.136 = 2.93, matches. CL-A-SERVO-COLD recomputes 1.585 with horn 9.155 / arm 8.5 (limit 1.5), consistent with the solved gearing 1.077^-1.
- **Limitations (unchanged):** stall torque interpolated (EST); frictionless; hinge moment estimated.

### AR-003 after D-212 rev 2 (interference during motion)
- **Analytic sweep in three joint states: PASS (no penetration over 0.05 mm).** Worst: lo state, arm / rod 0.028 mm (the rod rests on the arm by design; mid and hi: 0). Smallest positive clearance 0.066 mm (clevis cheek to horn blade at +21 deg, gap 0.1 mm EST). Arm / servo case 0 (arm on the case top, by design). The printed horn plate (20 x 30 mm) is 34.5 mm from the cap flange. Elevon section to core below the hinge 0.90 mm.
- **Mesh check (Blender 4.5.14 BVH, tolerance 0.05 mm), `A_ELEV_POSE=<angle> python -I redesign/qp/A/cad/collide_a.py`:** static (pose 0), +-10 deg and +-21 deg: 0 part pairs over 0.05 mm, wire ends 0, folds 0. Wall 496 s (10 deg) and 553 s (21 deg) on a busy machine (151 s earlier on an idle one). Reports kept per pose: `redesign/qp/A/cad/out/report_d212r2_pose{10,21}.json`, `REPORT_d212r2_pose{10,21}.md`. Scope: the mesh poses move the elevon, horn and clevis pin only; the rod and the arm are held out as linked parts, so their motion is covered only by the analytic sweep above (all three joint states).
- `stop_check.py` PASS (23 s); its output file is left at HEAD (not part of this change).

### Hand checks added by D-212 rev 2 (category: hand calculation, `mechanism/linkage_loads_check.py`, `out/linkage_loads_check.json`)
- **Z-bend leg bending** (F-2): M = F x 1.6 mm (arm mid-plane), sigma = 32 M / (pi d^3), curved-wire factor K = 1.625 (recalled from Shigley, verify). Hold 17.1 N: 161 MPa, 261 MPa with K, required yield 392 MPa at factor 1.5. Stall fault 42.7 N: 403 MPa, 655 MPa with K, required yield 655 MPa at factor 1.0. Collapse load of the leg at 655 MPa yield: 118 N against 42.7 N. Music wire A228 (S_ut 2153 MPa, bending allowable 0.78 S_ut = 1680 MPa, constants recalled from Shigley Tables 10-4 / 10-6, NOT re-read) passes; the rod grade is not published ("-"): receipt test 43 N along the rod, 10 s, no permanent set over 0.2 mm, else A228 wire.
- **Horn bond** (F-3): rigid plate 20 x 30 mm, hole 9.51 mm above the plate; peak peel 81 kPa at hold (x 1.5 = 122 kPa against the 129 kPa EST foam tension allowable of `foam_103.py`: the rigid-plate formula is INVALID for a 1 mm plate on foam, the hold result is NOT SHOWN, review r2 C-1; see After D-212 rev 3); **203 kPa at the stall fault: exceeds 129 kPa (open)**; mean shear 28 kPa hold, 71 kPa stall against 86 kPa EST: passes. The D-211 20 x 8 horn would have been 417 kPa at hold (never checked). Open: pull coupon of the printed plate on tape skin over XPS; fallback: backing plate under the lower skin.
- Limitations: foam and tape peel strengths are EST scaled values ("-" measured); rigid-plate peak is conservative.

### Still open (kept for the next export, review F-6)
`assembly_check.py` and `collide.py --glb` have not been run since the horn, arm hole and rod geometry changed; both are required at the next export (CLAUDE.md hard constraint).

## After D-212 rev 3 (T-063, 2026-11-18)
Change: the horn ATTACHMENT, not the linkage. The rev 2 geometry is kept (hole 9.155 mm directly over the hinge axis, arm hole 8.5 mm, Z-bend joint free in z over 0.3 mm). New: the horn is one flat printed PETG profile with a rib through a slot in the elevon; holes 1.3 mm (arm, drilled) and 1.1 mm (horn, reamed); a printed Z-bend keeper under an M2 x 8 arm screw; stall force 51.0 N; the open FAILs are claims (decision D-212 rev 3 in `redesign/params/CHANGE-LOG.md`, trade table D-212 rev 3 in `docs/engineering-decisions.md`). Model version: git `164c815a` plus the uncommitted D-212 rev 3 edits. Every command, exit code and wall time: `redesign/qp/A/mechanism/out/D212r3_runlog.txt` (the first block in that log ran on a 14 mm blade base and is superseded by the block after the marker line; only the final runs are quoted here).

Acceptance test (from the brief, restated before the work): the rev 2 linkage stays and still passes K1-K7, D1-D6 and the swept check in mid / lo / hi; the horn attachment is chosen from a trade table by function then mass with sourced dimensions or "-"; every strength claim names its model, validity, inputs and allowable source; the stall force is the 51.0 N stall-in-the-stop value; open FAILs are claims and stay failing; free play has a real fix or an open item with a bench test; drawings / STL of the made parts and regenerated tables; reruns of the three mechanism scripts (three states), `linkage_loads_check.py`, `proofs/run_all.py`, `stop_check.py` and `collide_a` at A_ELEV_POSE 21.

### AR-001 after D-212 rev 3 (kinematics)
- **PASS, K1-K7, mid / lo / hi** (4.2 s each). Unchanged from rev 2 except K5: the hole sizes now come from the CAD (`ARM_HOLE_D` 1.3, `HORN_HOLE_D` 1.1 mm), tilt allowance 2.86 deg each (was 8.53), K5 limit 1.43 deg against Z-bend misalignment 0.61-1.00 deg and clevis 0.88 deg. Gearing 0.905-0.930 over the three states (neutral 0.928). K7 0.028 deg.
- **Free-play budget (new output `free_play_budget_deg`, review M-4):** arm hole 0.10 mm -> 0.63 deg, horn hole 0.10 mm -> 0.63 deg, Z-bend freedom 0.03 deg: **1.28 deg known, against the 1 deg guide (SERVO.md s4): FAIL** (CL-A-LINKAGE-FREEPLAY). Clevis cheek holes "-" (vendor), measured at E1. Holes of 0.05 mm clearance would give 0.66 deg but bind: K5 limit 0.72 deg < 1.00 deg. Mitigation, not a pass: the hinge damper makes flutter independent of K (FIXES2 s1); the preload strips take up low-amplitude slack.
- Model: slop along the rod = sum of the diametral clearances; free play = slop / horn radius. Validity: small angles, rod tangent to the horn circle at neutral (true by D-212 rev 2).

### AR-002 after D-212 rev 3 (rigid-body dynamics)
- **PASS, D1-D6, mid / lo / hi** (7.0 s each), identical to rev 2: hold margin 2.93 (7.2 V EST) / 2.46 (6.0 V); hold rod force 17.05 N; dynamic step peak 42.74 N (Euler 111 N). The 42.74 N is no longer used as the stall force. **D3 (Euler / 2 = 55.6 N) was judged at the 42.74 N step; against the 51.0 N stall force the margin is 9 %** (review r3 m-2, recorded, not re-run). Rod body at 51 N with the one-end eccentric moment: kL = 43.25 x sqrt(51 / (200e3 x 0.1018)) = 2.16 rad, amplification 1 / sin(kL) about 1.20, mid-span stress about 45 + 1.2 x 481 = 622 MPa nominal, below the 782 MPa needed at the leg: the leg still governs (review r3 hand check, EST).

### AR-003 after D-212 rev 3 (interference during motion)
- **Analytic sweep PASS, mid / lo / hi** (13 s each). New solids: horn blade (above the skin) and horn rib (below, excluded against the elevon slab: bonded in its slot), keeper spacer and bridge (turn with the arm). Worst: design contacts arm / rod 0.028 mm (lo) and keeper bridge / rod 0.003 mm (hi, the keeper is the top stop of the Z-bend freedom). Smallest positive clearance 0.066 mm (clevis cheek / horn blade at +21 deg, gap 0.1 mm EST; fit check added to BUILD D3, review m-5). Keeper spacer / rod 0.70 mm at -21 deg; keeper bridge / rod 0.147 mm (mid). Rib outline vs core section (new 2-D check) 2.54 mm; elevon nose vs core 0.90 mm.
- **Mesh gate, `A_ELEV_POSE=21 python -I redesign/qp/A/cad/collide_a.py`** (145 s): static, -21 and +21 deg: 0 part pairs over 0.05 mm, wire ends 0, folds 0, 486 bodies in 115 parts. Report kept as `cad/out/report_d212r3_pose21.json` / `REPORT_d212r3_pose21.md`. The elevon carries the slot cut; the horn rib sits in it. Scope as before: rod and arm held out of the moving poses (covered by the analytic sweep).
- `python -I redesign/qp/A/cad/stop_check.py` PASS (10.2 s); output `STOP_CHECK.md` left at HEAD (its drift is older, review F-9).
- CAD stub build `python -I redesign/qp/A/cad/build_a.py`: check PASS, 10 modules, 0 errors (interfaces regenerated).

### AR-004 strength checks of the linkage (D-212 rev 3; `redesign/qp/A/mechanism/linkage_loads_check.py`, 6.2 s, output `mechanism/out/linkage_loads_check.json`)
Loads: hold 17.05 N (AR-002). **Stall 51.0 N**: F = 0.397 N m / (8.5 mm x 0.916), the smallest arm lever over +-21 deg, at +21 deg (review r2 M-1; 46.7 N at neutral). Factors: printed / bonded 2.156 at hold (1.5 x 1.15 x 1.25, `structures/fea_arm.py`), 1.4375 at stall (1.15 x 1.25; the stall force is the actuator's ceiling, so the 1.5 load factor is not applied), steel leg 1.5 at hold and both 1.0 and 1.5 at stall.

| Check | Category / model | Validity | Result | Allowable (source) | Verdict |
|---|---|---|---|---|---|
| Z-bend leg | hand calc: sigma = K 32 F e / (pi d^3), e = 1.6 mm, K 1.625 curved wire (Shigley, recalled) | slender bar, bend r >= d | needs yield 392 MPa (hold x 1.5), 782 / 1172 MPa (stall x 1.0 / 1.5); leg collapse 211 N at 1172 MPa | A228 1680 MPa (Shigley Tables 10-4 / 10-6 RECALLED, not re-read); M02 grade "-" | pass if A228; UNVERIFIED (ASM-A-ROD-GRADE): receipt test 77 N |
| Horn blade bending | hand calc on slices of the drawn outline | beam, sections above the skin | governing at the skin, 17.3 mm wide, lever 9.0 mm: 3.3 MPa factored (hold), 6.6 (stall) | PETG 20 MPa in-layer EST (fea_arm.py); printed lying flat | PASS (rev 2 stem: 52 MPa at stall) |
| Pin bearing / shear-out | hand calc F / (d t), F / (2 t e), e 1.65 mm | thin lug | bearing 18.4 MPa factored hold, **36.7 stall**; shear-out 5.6 / 11.1 MPa | PETG bearing 20 MPa EST (arm_cup_checks.py) | hold PASS; **stall FAIL** |
| Rib in the foam | FEA, 1-D: Hermite beam (EI = E t d^3 / 12) on an elastic foundation of foam face shear (k = 2 G d / l transverse, 2 G d^3 / 12 l rotational), rib axially rigid; load = horn moment over the blade base | linear, Winkler; the rib is NOT rigid (lambda L 2.7-4.5), so no rigid-plate or weld-group formula | peak face shear 138-200 kPa unfactored at hold over E_foam 5-10 MPa x l 2-8 mm (peak at the rib front edge); **432 kPa factored**; **stall 413-599, 861 kPa factored** | foam shear 86 kPa EST (foam_103.py, ASM-A-FOAM-ALLOW) | **FAIL, hold and stall** |
| Elevon torsion beside the horn (pre-existing, found here) | hand calc, Saint-Venant thin open section, foam only: tau = T t_max / J, J 2757 mm^4 | t / c 0.14 | outboard share 0.51 of 0.146 N m: 234 kPa, **504 kPa factored**; stall 0.467 N m into the outboard stop: 1463 kPa | 86 kPa EST | **FAIL**: by the same basis the elevon itself cannot carry its hinge moment without the tape skin (Bredt shear flow 152 N/m at hold if the nose is taped closed; tape strength "-", not credited) |
| Rib vs elevon body | ratio of the two factored peaks at hold | same basis | 0.86 | - | the attachment is not the weakest part of the elevon on this basis |

Independent hand checks: stall force 0.397 / (0.0085 x 0.9159) = 51.0 N (reproduces review r2); blade 6 x 17.05 x 8.97e-3 / (2e-3 x 17.27e-3^2) = 1.54 MPa x 2.156 = 3.3 MPa; bearing 17.05 / (1.0 x 2.0) = 8.5 MPa x 2.156 = 18.4 MPa; leg 51.0 x 1.6e-3 / 1.696e-10 = 481 MPa x 1.625 = 782 MPa; rigid-limit check (review r3, FE and an independent hand rigid-plate solve, both 126.2 kPa peak at the rib aft end, E_PETG x 1e5): **126.2 kPa unfactored is the lower bound of the whole Winkler family, 1.5 x the 86 kPa allowable even before the 2.156 factor, so the rib FAIL holds for any shear-penetration length l** (m-10; l 16 mm gives 138 kPa, 32 mm 121 kPa; referring the moment to the hinge axis instead of the rib mid-depth lowers the peak by about 30 %, still FAIL by 2.5-3.5 x; Euler-Bernoulli ignores shear deformation, about 10 %, unconservative); the FE peak lies at the loaded front edge, where a Winkler model is least accurate (no shear coupling): read the range as an estimate.

### Proof graph (`python -I redesign/qp/A/proofs/run_all.py`, 1.5 s)
- New params group `linkage` (read from `linkage_loads_check.json`, `linkage_kinematics.json`; all EST), sources SRC-A-LINKLOADS, SRC-A-LINKKIN, SRC-A-SERVOMD, assumptions ASM-A-ROD-GRADE and ASM-A-PETG-ALLOW (UNVERIFIED).
- New claims: CL-A-HORN-RIB-FOAM-HOLD 431.8 kPa, CL-A-HORN-RIB-FOAM-STALL 860.9 kPa, CL-A-ELEVON-TORSION-FOAM 504.3 kPa (all <= 85.8 kPa: **FAIL**), CL-A-HORN-BEARING-STALL 36.65 MPa (<= 20: **FAIL**), CL-A-LINKAGE-FREEPLAY 1.28 deg (<= 1: **FAIL**); CL-A-HORN-BLADE-HOLD / -STALL, CL-A-HORN-BEARING-HOLD, CL-A-ROD-LEG-STALL pass on value and stay UNVERIFIED through their assumptions.
- **Review r3 conditions (T-063-cond):** new test node T-A-HORN-RIB; test-form claims CL-A-HORN-RIB-COUPON, CL-A-HORN-STALL-STEP, CL-A-ELEVON-TORSION-COUPON, CL-A-HORN-STALL-BENCH (value "-", numeric limits, PROPOSED: not FAIL) and CL-A-HORN-SHEAROUT-STALL (11.11 vs <= 11.55 MPa EST, UNVERIFIED through ASM-A-PETG-ALLOW); params `shearout_stall_mpa`, `shearout_allow_mpa`. Final run: **548 nodes, 1151 edges, fails 6 (the same five FAIL claims + A-P13), strict FAILED as intended**; CL-A-ASSY-STEPS = 59 (m-1; params-A.json, CHAIN.md). The five analysis FAILs are the "not shown by analysis" record; they are superseded by the test claims once the tests run (Open item 1). Commands and times: `qp/A/mechanism/out/D212r3_runlog.txt`.
- Earlier build result (after the build-sequence rerun, before r3 conditions): 539 nodes, 1112 edges, **fails 6, FAILED (strict)**: the five new FAIL claims and requirement A-P13 through them. Nothing is hidden: these are the open items. `render_readable_a.py` was run separately (run_all stops at the strict error); the nine new claims have generic cards (no plain-English entry in `explain_a.py` yet). Log: `redesign/qp/A/proofs/out/run_all_d212r3.log`.

### Generated deliverables (review M-5)
- Drawings and STL from the CAD: `python -I redesign/qp/A/drawings/make_drawings_a.py` (stages 1-2, 97 s; stage 3 needs `python -B ... --compose`, 87 s, because `-I` hides `compose_drawings`): 41 sheets, 42 STL files; new `redesign/qp/A/drawings/out/MEC-004.pdf/.png` (57.2 x 2.0 x 19.7 mm, 0.95 g, print lying flat), `MEC-008.pdf/.png` (12.1 x 3.1 x 2.3 mm, 0.08 g), `out/stl/MEC-004-{R,L}.stl`, `MEC-008-{R,L}.stl`; non-manifold edges 0 for both.
- Regenerated, not hand-edited: `cad/model/*/interfaces.json` (build_a.py), `cad/out/parts-a.csv` (parts_links_a.py: MEC-004 make R03, MEC-008 make R03, HWC-002 M2 x 8), `BUILD-GUIDE-A.md` (make_build_guide_a.py: 66 steps, printed mass 147 g), `site/app.html` and `site/index.html` (make_build_guide.py, make_index.py), `structures/foam_103.md` (review m-3). Stale CAD body names fixed (review m-1). Not regenerated: `site/data/viewer-data.json` and the GLB (needs the Blender GLB export; next export).

### Open items after D-212 rev 3
1. **Horn rib and elevon in the foam (CL-A-HORN-RIB-FOAM-*, CL-A-ELEVON-TORSION-FOAM):** NOT SHOWN BY ANALYSIS at the EST foam shear allowable; the same basis fails the elevon itself. These five FAIL claims stay as that record. **They are superseded by the test claims once the tests have run (review r3 M-1):** test node T-A-HORN-RIB verifies CL-A-HORN-RIB-COUPON (coupon held 30 s at 2.156 x 17.05 = **36.8 N**, held / required >= 1, no crack, no slip, set < 0.5 deg; review r3 M-2, was 1.5 x 17.1 = 25.6 N), CL-A-HORN-STALL-STEP (then 51 N for 5 s, hole elongation <= 0.1 mm, no crack), CL-A-ELEVON-TORSION-COUPON (a tape-skinned elevon section about 160 mm long, 0.161 N m = 2.156 x 74.65 N mm for 30 s, twist set < 0.5 deg, no debond) and CL-A-HORN-STALL-BENCH (item 2). When they pass, the analysis claims are re-pointed away from A-P13 by a logged CHANGE-LOG edit (build_graph keeps a negative-margin claim FAILING whatever a test does, so closure is by that edit, not by a graph rule), and A-P13 rests on the test claims. The coupon result is **local only**: its clamps sit 50 mm from the rib, where in flight the elevon continues about 160 mm. >= 3 coupons, lowest governs; a measured foam shear value (M11 block) is also taken. **Fallbacks if the tests fail:** rib introduction: 0.4 mm ply or CF doubler over the rib on both skins (rung 5); elevon torsion and rib: the spanwise CF torsion tube, trade row J in `docs/engineering-decisions.md` (not adopted).
2. **Stall-into-stop / jam fault (CL-A-HORN-BEARING-STALL, -RIB-FOAM-STALL, -SHEAROUT-STALL):** fails or is thin at the EST allowables (bearing 36.65 vs 20 MPa; shear-out 11.11 vs 11.55 MPa EST, +4 %, new claim CL-A-HORN-SHEAROUT-STALL, review r3 m-13). Mitigation: endpoints set to +-20 deg, short of the 21 deg stop (BUILD D5b), and the bench stall test written into BUILD D5b (`cad/a_build_steps.py`): 51 N / 5 s into the +21 deg stop, each elevon, pass = no crack, hole elongation <= 0.1 mm, trailing-edge set < 0.5 deg (CL-A-HORN-STALL-BENCH, T-A-HORN-RIB). Not declared survivable until it passes.
3. **Free play 1.28 deg + cheek holes "-" (CL-A-LINKAGE-FREEPLAY):** E1 dial-gauge measurement; flutter is covered by the damper.
4. **Rod grade:** 77 N receipt test (BUILD D4).
5. **Output boss height:** if the arm does not sit on the case top, ARM_Z0 and the horn hole, rod and keeper heights move with it before printing.
6. **Build-sequence check (closed here):** `python -I redesign/qp/A/cad/a_assembly.py` (1622 s, Blender 4.5.14): every step ok, worst 0.000 mm at 0.05 mm tolerance, 43 steps, 115 parts (the keepers added two); D3 (rib down through the elevon slot, 15 mm) and D2a (keeper + M2 x 8 after D4) pass. CL-A-ASSY-PARTS 115 / 115 after the rerun.
7. **Gates kept open for the next export (CLAUDE.md):** `redesign/showcase/animation/assembly_check.py` and `collide.py --glb` were not run (no GLB export in this task).
8. Mass roll-up (`sitl/cad_mass.json`, MASS-GATE) not regenerated: +0.28 g for the pair against rev 2, below the reported precision.
9. **Review r3 minors, logged open (each must close before E1; m-2, m-10, m-13 are recorded above):**
   - m-3 receipt test eccentricity: 1.6 mm (rod on the arm) under-tests the hi state (keeper, 1.9 mm) by about 16 %: test at about 91 N or shim the rod 0.3 mm.
   - m-4 keeper MEC-008: no load or creep check (about 18 MPa factored vs 20 EST at the bridge, scratch); add a check line and a retorque / inspection item at E1 and preflight.
   - m-5 drawings: MEC-004 / MEC-008 omit the print orientation (flat); hole drawn 1.1 mm but the guide says printed 0.9 mm, reamed 1.1 mm.
   - m-6 bearing stall FAIL: a brass tube bushing (2.0 mm OD x 1.0 mm ID, availability "-") would pass (18.3 MPa factored; HORN_HR about 2.8 mm for shear-out); add a trade row or say why not.
   - m-7 free play: FIXES2 E1 step 7 probes 1 deg, the built budget is 1.28 deg plus cheek holes and servo backlash; pick one basis for CL-A-LINKAGE-FREEPLAY (flutter vs control precision); +-20 deg endpoints leave 1 deg, less than the free play.
   - m-8 stall load factor: 0.397 N m is an EST at 7.2 V; at 8.4 V (SERVO.md 4.7 kgf cm) the stall force is about 59 N; state the 7.2 V jumper (M12) as the basis or keep a factor.
   - m-9 collision claims read pre-D-212 reports (`gen_params_a.py` report_pose20 / report_pose21, 2026-11-15, 0.042 mm): point them at `report_d212r3_pose21.json` (0.034 mm); +-20 deg not rerun for rev 3.
   - m-11 trade row C: the "about 80 kPa" figure has no stored script, and balsa is tabulated in the USDA Wood Handbook (not looked up); the rejection rests on build effort.
   - m-12 elevon torsion J: int t^3/3 overestimates J at t/c 0.14 (beta about 0.307 vs 0.333, recalled); the stress is a few percent low, immaterial to a FAIL.
   - m-14 rib tail is 0.67 mm deep at 55 mm aft (fragile): consider ending the rib where the depth is >= 1.5 mm and re-run the rib check (peak is at the aft end in the rigid limit).
