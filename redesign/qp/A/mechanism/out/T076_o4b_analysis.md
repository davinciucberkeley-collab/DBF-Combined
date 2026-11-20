# T-076 (R-PHY-08, R-PHY-09, R-OPT-01), concept A, O4b (AM-009, D-219): C6 hub FEA, pin/fillet rows, A-P10, Lua spin cap, pad-cup coupon (2026-11-19)

Status: analysis only, NOT VERIFIED COMPLETE. Nothing committed. No CAD, docs/, CHANGE-LOG, ledger, MASS-GATE or BOM edited. Committed FEA outputs (`structures/out_fea/`) and `T073_data`, `T074_data`, `T071b_data` untouched; every new file is under `redesign/qp/A/mechanism/out/T076_data/` or is the new `redesign/qp/A/sitl/lua/spin_cap.lua`. KF 1.725 / KP 2.156, RF >= 1.0 and the A-P limits are not relaxed. All allowables are EST (PETG 20 MPa, interlayer 9.5, epoxy 2.0, CF pin 30) unless a source is named; "-" is unknown.

Acceptance test (restated from the brief): (1) FEA of the hub with the C6 collar / aft block extension at the rigid-body landing demand at 1.64 kg and at x1.5, report RF; (2) pin fix rows (3 x 3 mm pins in a 4 mm wall), R1'' / R3fix / R4 fillets, report RF; (3) A-P10: `t073_modal.py` for 9x4.5 with the skin at 1.64 kg and T-067 masses, hi-corner mode vs 1P band, forced response, tap-test plan; (4) ArduPilot Lua spin-cap script, parameter names checked against the docs, one SITL transition at 1.64 kg with Q_M_BAT_CURR_MAX 45 vs T074 check 3; (5) pad cup rows: missing EVA / cup data and the coupon test. Stop and report any row < 1.0 that no listed fix closes.

Categories: row 1 = **FEA** (linear elastic tet10, direct solve) fed by **rigid-body dynamics** (landing_a.py foot-force histories); row 2 = rigid-body dynamics + hand calculation; row 3 = **FEA**-class beam-frame modal analysis + forced response; row 4 = **flight dynamics** (ArduPlane SITL + `a_plant.py`); row 5 = hand calculation / test plan. Interference, kinematics and CFD: none run.

## 0. Answers in one place

| Row | Result |
|---|---|
| 1 C6 hub FEA | **STOP: row < 1.0, no listed fix closes it.** Hub as drawn (D-209) at the rigid-body landing demand, 1.64 kg: bridge-end-zone p99 RF **0.48**, whole-hub p99 RF **0.80**. C6 (floor +1.5, 12 mm 24 x 24 collar) raises them to **1.03 / 0.94** (RB) and **0.69 / 0.62** (x1.5, EST factor). The collar itself is fine (p99 RF 2.19 RB, 1.46 x1.5, agreeing with T-071b's hand RF 2.27 / 1.52). What fails is a localised hot spot between the block face and the collar (167 MPa single-element peak, singular; base hub 64 MPa), not the collar. C6 helps (doubles the RF) but does not reach 1.0 on the whole-hub p99, and the x1.5 case is far below. The flight / strike cases on the C6 hub all pass (s1.4). |
| 2 pin / R1'' / R3fix / R4 | All >= 1.0 at 1.64 kg: pins 3 x 3 mm in 4 mm wall **1.43 bearing / 2.53 shear** (1.12 / 1.97 at 1.50 kg, reproduced); cradle 3 pins in a 4 mm boss **1.66 / 2.94**; R1'' tabs 1.48, wall 1.23, plate bond 1.75; R3fix S2 plate cantilever **1.37**; R4 junction **1.26 (r 1.5 mm) / 1.48 (r 2.0 mm)** with Kt EST, 0.86 without fillets. Cup EVA rows remain < 1.0 (row 5). |
| 3 A-P10 | 9x4.5, skin, T-067 printed masses, 1.64 kg (FE mass made up to 1,640 g by an EST line mass), bands re-based to 1.64 kg: **hi-corner strongly coupled mode 79 Hz** (84 Hz without the unallocated mass) against a limit of **88.0 Hz**: pass by 4-9 Hz, no stop-rule hit. With T-067 masses but old bands it is 84.3 Hz against 83.6 Hz: **STOP-rule hit** (so the band re-base F-9 is load-bearing). Forced response 20.6-22.6 m/s2 at zeta 1 % (limit 30). Tap test needed (s3.4). |
| 4 Lua | `spin_cap.lua` written; SITL build **does** run scripting (loaded, cap ramped 0.90 to 1.000, 14.7-14.9 V). Transition r 1.33 at 1.64 kg with Q_M_BAT_CURR_MAX 45: handover 13.7-13.8 m/s, alpha 10.5-10.7 deg, u max 0.814, 6.4 A per motor, no cap run: same as T074 check 3. **Pitch use 0.61-0.63 of 20 deg is over the 0.60 line** (T074 0.44); a no-script control with the same battery parameters gives 0.61, so it comes from the battery-monitor parameters, not the script. Failsafe to 0.90 verified: it fails the r 1.33 entry (alpha 39 deg, handover 12.3 m/s). |
| 5 pad cup | s5: data missing and the coupon test. |

## 1. C6 hub FEA (row 1)

### 1.1 Method
- Tool: `structures/fea_hub.py` (D-209 / AR-009, run with `--level 0 --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8`). It is not edited. `T076_data/make_fea_hub_c6.py` writes `fea_hub_c6.py`, a copy with five textual patches (collar box, mesh-refine box widened to y +-13 / z -17..+9 for the collar, OUT dir to `T076_data/fea`, HERE, new main; hub-aft-face RBE3 load columns). `t076_main.py` is the driver. Hub-frame mm, N, MPa; same element, materials, allowable (petg 20 MPa, KP 2.156: allow 9.28 MPa) and p99 convention (D-207) as AR-009.
- C6 geometry (T-071b H3): bore floor X_BR0 15.0 to 13.5 (1.0 mm web left over tube B), block aft extension 12 mm as a 24 (y +-12) x 24 (z -16..+8) box on the block aft face, mouth X_HUB1 24 to 36. **The flare of the "flared collar" is not modelled (straight box)**; fillets as D-209 (FIL 2.0 / 1.5). Hub mass 21.44 g (D-209 hub 16.10 g, +5.34 g; T-071b EST +5.3 g).
- Landing demand: `landing_centre_a.py --recompute` at `LAND_MASS_KG=1.64` (39 s) gives the 23-case rigid-body hub-side wrench. From the sims directly (`landing_a.simulate`, D2 pad, plateau 30 N, mu 0.40, same as T-071b) 301 candidate time steps were chosen (signed extremes of the six wrench components and the top |M| steps per case). Peak hub-side wrench here: arm group (motors + arms) |M| 6.3 / 6.9 / 17.6 N m (x / y / z), pack + hub group |F| 40 N, |M| 0.13 / 0.38 / 0.34 N m. Two load partitions: **A** whole wrench through the four arms (bound for the sleeves and block); **B** arm group through the stub ends as a rigid inertia field of the four motor masses, hub + pack group through an RBE3 on the 3,611 (C6) / 1,907 (base) hub aft-face nodes (tray path not modelled). Support: bridge-tube far end, as AR-009. x1.5 is the EST dynamic factor of T-071b (no transient FE).
- RF = 9.28 MPa / p99 principal stress, enveloped over the 301 combos. **Judging rule:** zone p99 (D-207: single-element peaks at sharp edges grow with refinement). Both the D-209 "aft of the block face" zone and the stricter whole-hub p99 are given; the single-element maximum is shown for visibility only.

### 1.2 Results at the rigid-body demand (limit load, KP applied), 1.64 kg
| Hub | Partition | Whole hub p99 (RF) | Aft-of-block zone p99 (RF) | Last 12 mm before the mouth p99 (RF) | Peak single element MPa |
|---|---|---|---|---|---|
| as drawn (D-209) | A | 11.28 (**0.82**) | 19.30 (**0.48**) | 17.11 (0.54) | 62.9 |
| as drawn | B | 11.58 (**0.80**) | 19.38 (**0.48**) | 17.33 (0.54) | 63.8 |
| **C6** | A | 9.60 (**0.97**) | 8.55 (**1.09**) | 4.20 (2.21) | 169.5 |
| **C6** | B | 9.90 (**0.94**) | 9.02 (**1.03**) | 4.24 (2.19) | 167.2 |
| as drawn, x1.5 | A / B | 16.93 / 17.38 (0.55 / 0.53) | 28.95 / 29.08 (0.32 / 0.32) | 25.67 / 25.99 (0.36) | 94 / 96 |
| **C6, x1.5** | A / B | 14.40 / 14.85 (**0.64 / 0.62**) | 12.82 / 13.53 (**0.72 / 0.69**) | 6.30 / 6.36 (1.47 / 1.46) | 254 / 251 |
Governing case everywhere: "hard 10 wide + drift .5 y" (step 342) for the whole-hub and aft-zone rows, "hard 7/7 combo" for the collar zone. Mesh: C6 375,848 tet10, 1,747,887 unknowns, equilibrium 2.4e-10 N, residual 3.3e-10; base 318,564 tet10, 1,502,610 unknowns.

### 1.3 Reading
1. C6 does what T-071b said at the bore: the collar zone is RF 2.19 (hand RF 2.27 hub collar interlayer, 1.76 hub bore bearing at 1.64 kg) and 1.46 at x1.5 (hand 1.52 / 1.17). The hand and FEA collar numbers agree.
2. The failing row is **not in the collar** (collar-only max 17.5 MPa). It is in 14 < x < 24 mm (the old block aft part and the bore floor), where C6's single-element peak is 167 MPa. The D-209 hub had 64 MPa there. The deeper floor leaves a 1.0 mm web over tube B (X_BR0 13.5 vs tube B aft surface at about 12.5): my reading, not tested, is that the web and the floor corner are the singular spot and the deeper floor made it worse. The T-071b hand model (mean bearing on a rigid tube) cannot see it.
3. The 301-combo envelope includes loads that have no hand analogue (arm-group moment about z up to 17.6 N m from the drift cases, Mx 6.3 N m); T-071b's hub rows used the span-axis moment (6.05 N m at 1.50 kg) only. The FEA at 1.64 kg has span-axis M_y 6.71 N m for the same peak case.
4. Pre-existing finding: the D-209 hub (no extension) is 0.48 / 0.80 at this demand, i.e. the committed hub fails the rigid-body landing load with or without C6. T-071b only had the hand bearing row (0.33).

### 1.4 Flight / strike cases on the C6 hub (same solve, first pass, `fea_c6_stdout.txt`; base = committed `hub_result_L0_d209.json`)
| Case | C6 hub p99, bridge-end zone MPa (base) | RF vs 9.28 flight / 20 strike | C6 centre-block p99 (base) | Tube B hoop MPa C6 (base) | Tube A shear MPa C6 (base) |
|---|---|---|---|---|---|
| F1 spin cap | 2.87 (5.01) | 3.23 | 3.26 (3.15) | 16.4 (15.4) | 7.4 (7.4) |
| F2 uncapped fault | 3.32 (5.87) | 2.79 | 3.81 (3.68) | 18.9 (17.8) | 8.5 (8.5) |
| S1 strike | 4.25 (9.99) | 4.7 | 8.88 (8.40) | 30.5 (29.7) | 20.9 (20.9) |
| S2 strike | 5.06 (7.43) | 3.9 | 8.15 (7.93) | 31.2 (30.0) | 24.7 (24.5) |
| S3 strike | 1.41 (2.03) | 14 | 2.10 (2.06) | 8.0 (7.8) | 7.4 (7.3) |
Single-element peaks in the collar zone: F1 34.7, F2 40.5, S1 47.8, S2 49.5 MPa (base 16.4 / 19.2 / 31.6 / 17.2): sharp collar edges, judged by p99 as in D-207. Tube and glue values move by < 7 % (S2 tube A shear margin 1.21 against 1.22; F2 glue mean 0.73 against 0.93 allowed). The schedule does not change the flight loads: fresh capped thrust at duty 0.903 is 9.52 N before derate, equal to the 0.90 cap case that T_CAP 8.81 N is built on; sag thrust at duty 1.0 is 9.12 N, lower.

### 1.5 What would close it (not run; ladder order)
(a) Keep C6's collar but do **not** deepen the floor (X_BR0 15.0, bore L 21.0 mm): removes the 1.0 mm web; T-071b hand bearing RF falls to about 1.76 x (21/22.5)^2 = 1.5 (my arithmetic, EST). (b) Round the bore-floor corner (BORE_FR) and the floor-to-collar transition. (c) Thicken the web (move tube B forward, C5, fails the CG trim). Each needs one more FEA run (about 55 min each; the machine ran 3,333 s for C6 with both scales). The x1.5 rows are far below 1.0 for every hub variant (EST factor, no transient run): C6 0.62-0.72, so a transient or a smaller factor is also needed.

### 1.6 Commands, exit codes, wall times
| # | Command (cwd `redesign/qp/A/mechanism/out/T076_data` unless stated) | Exit | Wall |
|---|---|---|---|
| 1 | `LAND_MASS_KG=1.64 LAND_OUT_DIR=T076_data/land164 python -I landing_centre_a.py --recompute` (cwd `structures`) | 0 | 39 s |
| 2 | `python -I make_fea_hub_c6.py` | 0 | <1 s |
| 3 | `run_fea_c6.sh` first pass: `python -I fea_hub_c6.py --tag t076c6 --level 0 --land land164/demand_series.npz --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8 COL_E=12 X_BR0=13.5 X_HUB1=36` (landing partition A only, standard F1 / F2 / S1-S3) | 0 | 2,451 s (solve 441 s) |
| 4 | the base-hub run queued behind it was stopped by me (it used the superseded driver) | killed | - |
| 5 | `run_fea_c6b.sh`: `LAND_MASS_KG=1.64 python -I fea_hub_c6.py --tag t076c6b --level 0 --skip-std --p ...COL_E=12 X_BR0=13.5 X_HUB1=36` (partitions A and B, RB and x1.5) | 0 | 3,333 s |
| 6 | same, `--tag t076baseb` (D-209 geometry) | 0 | 1,630 s |
Outputs: `t076_hub_result_t076c6.json`, `t076_hub_result_t076c6b.json`, `t076_hub_result_t076baseb.json`, `fea_c6_stdout.txt`, `fea_c6b_stdout.txt`, `fea_baseb_stdout.txt`, `fea/hub_mesh_*.npz` (meshes, regenerable). `land164/demand_series.npz` (16 MB) was deleted after use (regenerable in 39 s).
Limits: bore / collar bearing is a tied bond (no contact, no clearance), PETG isotropic 20 MPa EST (no layer orientation), tray and saddle left out, bridge-tube far end fixed, partition B's hub-group path (RBE3 on the aft face) is an assumption, no mesh-convergence study (singular edges), the flare of the collar is straight, x1.5 is an EST factor.

## 2. Pin fix rows, R1'' / R3fix / R4 fillets (row 2), 1.64 kg

Traces: `LAND_MASS_KG=1.64 python -I t076_traces.py` (copy of `t073_traces.py` writing `t076_traces.pkl`; exit 0, 34 s). Step-4 hand calc: `LAND_MASS_KG=1.64 T076_MPACK=0.275 python -I t076_step4.py` (copy of `t073_step4.py`, pack 275 g, R4 fillet rows added; exit 0, 3 s). Pins: `landing_nodes_b.py` (exit 0, 37 s, `s2_nodes_m164_stdout.txt`) and `t076_pin_rows.py` (exit 0, 58 s; control at 1.50 kg, exit 0, 55 s, reproduces T-071b 1.12 / 1.97). `arm_cup_checks_t076.py --r3fix` (copy of `arm_cup_checks.py`, output to T076_data; exit 0, <1 s; stdout identical to T-073's `arm_cup_r3fix_stdout.txt`).

| Row | RF at 1.64 kg (1.50 kg) | Note |
|---|---|---|
| PIN root block / saddle, 3 x 3 mm CF pins, 4 mm PETG wall: bearing | **1.43** (1.12) | governing SITL Ta_h5 wide; demand falls with mass here (plateau-limited forces and prescribed touchdown), so the 1.50 kg figure is the conservative one |
| same: double shear | **2.53** (1.97) | |
| as drawn 1 x 3 mm in 2.5 mm: bearing / shear | 0.30 / 0.84 (same) | the CAD change (3 pins, 4 mm boss) is what fixes it |
| 2 x 3 mm in 2.5 mm: bearing / shear | 0.60 / 1.69 | not enough |
| Clamshell cradle, 3 pins in a 4 mm boss: bearing / shear | **1.66 / 2.94** (1.68 / 2.97) | vs as drawn 2 pins in 2 mm: 0.55 / 1.96 |
| R1'' tab root bending, 2 x 40 x 2.0 | **1.48** | R1 as specified 0.27 (fails) |
| R1'' end wall 2.0 mm, 30 % windows | **1.23** | R1 as specified 0.25 (fails) |
| R1'' plate-to-flange bond with 2.0 mm root pad | **1.75** | R1 as specified 1.05 |
| R3fix S2 plate cantilever (5 mm over +y tab) | **1.37** (MS +0.37) | strike-governed, mass-independent; R3 as specified MS -0.71 |
| R4 bond, 25 mm socket | 1.89 | present 14.2 mm block 1.07 |
| R4 socket wall, in-layer / printed standing | 1.41 / 0.67 | **orientation must be in-layer** |
| R4 clamp ring on spar | 2.13 | |
| R4 junction, 2 x 2.5 x 9 mm strips, no fillet | 0.86 | |
| R4 junction with fillets r 1.0 / 1.5 / 2.0 / 3.0 mm | 0.81 / **1.26** / **1.48** / 2.24 | Kt is my EST fit (2.4 at r/t 0.2, 1.9 at 0.4, 1.5 at 0.8, 1.3 above), no source file read; **r >= 1.5 mm needed** |
The step-4 printout still says "M 1.5 kg / 270 g pack" in its header text; the loads were computed with `L.M_GATE` = 1.64 and the pack at 0.275 kg. Rows still below 1.0 (not mine to fix here, restated): cup EVA rows (s5), bond-integrity rows, cradle bending in the plate ("-").

## 3. A-P10 re-run (row 3)

### 3.1 Method
`T076_data/t076_modal.py` imports `T073_data/t073_modal.py` unmodified (`python -I`, exit 0, 7-8 s each) and patches run-time masses (EST mapping, all in the script header): cup 4.30 to 9.51 g (T-067) less R3fix 2.8 g = +2.41 g per motor; hub print 20 to 15.82 g, tray 15.7 g (R1''), pack 275 g (O4b, `U`); avionics plate 8.0 to 1.02 g bosses, bridge saddle 2.0 to 9.67 g, cover -0.81 g; strut clamps +3.2 g per side; fin root +34.9 g per side (block 18.90, saddle 14.39, T-068 6 g), foot shoe 4.55 g. Skin 1 ply as T-073. Control: `T076_MASS=t073` reproduces `T073_data/modal_skin1_p9.txt` **byte for byte** (diff of the table part empty). `T076_RESID=1` adds the unallocated growth (wiring, fasteners, adhesive) as a uniform wing line mass so the FE total is 1,640 g (T-067 printed masses alone give 1,388 g in the FE); `T076_REBASE=1` re-bases the rotor bands at 1.64 kg (hover rpm 6,339 / 6,571 / 7,492: derate 1.0 / 0.93 / the 8 m/s-lean edge scaled by the mid-rpm ratio; audit F-9 gave 6,327 / 6,559).

### 3.2 Results (strongly coupled mode just under the exclusion zone, per corner; limit = lowest 1P edge / 1.2)
| Run | FE mass | Band limit | kd | nom | hi | Stop rule |
|---|---|---|---|---|---|---|
| control, T-073 masses (committed) | 1,272 g | 83.6 | 69 | 76 | **86.3 (hit)** | hit |
| T-067 printed masses, old bands | 1,388 g | 83.6 | 68 | 74 | **84.3** (coupling 1.06, arm 44 %) | **hit** |
| T-067 + growth, old bands | 1,640 g | 83.6 | 64 | 70 | 79 | none |
| T-067, re-based bands | 1,388 g | **88.0** | 68 | 74 | 84 | none (limit - mode 4 Hz) |
| **T-067 + growth, re-based bands** | 1,640 g | **88.0** | 64 | 70 | **79** | **none** (9 Hz) |
Forced response (zeta 1 %, physical envelope = all four motors up to the 9,349 rpm cap, limit 30 m/s2): 21.8 / 21.4 / 20.6 (kd / nom / hi) m/s2 in the 1,640 g re-based run (MS +0.81 / +0.84 / +0.82); worst of the four runs 22.6 m/s2 (nom, 1,388 g, MS +0.33). At zeta 0.5 % the 1,388 g, old-band run reaches 28.3 m/s2 (nom, MS +0.06), the others 20-24. Weakly coupled modes inside 105.6-124.9 Hz (rib / spar, coupling 0.05-0.25) pass by forced response. Lowest strongly coupled mode above the zone: 316-398 Hz (limit 304) in the 1,640 g runs.

### 3.3 Reading
- The hi-corner (skin x1.3, EST) cage / wing-torsion mode sits at 84-86 Hz with T-073 or T-067-only masses and drops to 79 Hz when the aircraft carries its predicted 1.64 kg. Against the **old** hover band (83.6 Hz) it fails or sits at the line; against the 1.64 kg band (88.0 Hz) it passes with 4-9 Hz. The pass therefore rests on (i) the band re-base (F-9, physics, needs the conductor to re-base `iter2_eval.RPM_HOVER`) and (ii) where the unallocated 250 g actually sits (my uniform wing line mass is EST).
- The hi corner uses skin x1.3 and is the optimistic stiffness; a stiffer true skin raises the mode toward 88 Hz. The tap test decides.

### 3.4 Tap-test plan (proposal, $0 beyond a phone)
1. Build state: wing + skin + cage + dummy masses (pack 275 g, FC, motors at real mass) = the 1.64 kg configuration, on a soft support (foam block under the centre, free-free).
2. Hammer (plastic tip) at a motor cup in +z and +y; phone accelerometer or audio FFT on the FC seat and at one motor. Three hits per point, average, 5-300 Hz, 0.5 Hz resolution.
3. Read: the coupled cage / wing-torsion mode (EST 64-84 Hz range), the arm modes (32-50 Hz per arm, T-073 / `arm_cup_checks.md` accept band), the rib mode (about 70-83 Hz).
4. Pass: coupled mode <= 88.0 Hz (re-based limit) with the 4-arm spread within 8 %; if the measured mode lies in 88-120 Hz it is in the hover band: stop, use stiffening or mass change, not a notch filter.
5. Repeat once with the FC mounted hard (A-P25) to give the isolator-free number; record the measured mass.

### 3.5 Commands
`python -I t076_modal.py` with `T076_MASS` in {t073, t067}, `T076_RESID` in {0, 1}, `T076_REBASE` in {0, 1}: five runs, all exit 0, 26 s (control) and 7-8 s each (`s3_modal_*.txt`, `s3_modal.times`). Limits: beam-frame model, EST skin and spread, EST mass placement, the 250 g of unallocated growth is a uniform wing line mass, hi-edge hover rpm is EST.

## 4. SITL Lua spin cap (row 4)

### 4.1 Script and parameter check
`redesign/qp/A/sitl/lua/spin_cap.lua`: resting-voltage estimate `battery:voltage_resting_estimate(0)`; cap(V) piecewise-linear from `prop_a.cap_sched` at 1.64 kg (16.8 V 0.903, 16.4 0.926, 16.0 0.952, 15.6 0.978, 15.4 0.992, below 15.4 V 1.0; rounded down; floor 0.90); 5 Hz update; cap may fall at once and rise at most 0.01 per second (starts at 0.90, so 10 s to 1.0 at sag); failsafe to 0.90, held, if the battery is unhealthy or the reading is nil or outside 12.0-17.2 V. It sets only `Q_M_SPIN_MAX` with `param:set` (RAM, not saved).
Names checked (all read 2026-11-19): `battery:voltage_resting_estimate(instance)`, `battery:healthy(instance)`, `battery:voltage(instance)`, `param:set(name, value)` in https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_Scripting/docs/docs.lua. `SPIN_MAX` (group Q_M_ in a QuadPlane), range **0.9-1.0**, `BAT_CURR_MAX` 0-200 A "0 = Disabled", `BAT_VOLT_MAX` / `BAT_VOLT_MIN` in https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_Motors/AP_MotorsMulticopter.cpp. `SCR_ENABLE` (default 0), `SCR_VM_I_COUNT` 10000, `SCR_HEAP_SIZE` 200 KB on SITL in https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_Scripting/AP_Scripting.cpp. The Q_ prefix comes from the repo's own `A.param`. The parameter-doc pages (ardupilot.org/plane/docs/parameters.html) were fetched but truncated before the Q_M_ and SCR_ entries, so they were not used. **Not confirmed from a source:** whether the voltage compensation is applied before or after the SPIN_MAX clip (the source file was not fully visible); `gcs:send_text` signature (used as in common examples, ran in SITL). **Range flag:** the documented SPIN_MAX range starts at 0.9, and the cap formula would go to 0.891 at 17.0 V; the script floors at 0.90 (binds only above 16.83 V resting, which a 4S LiPo does not reach).
**Not verified:** whether the Kakute F405 Wing Mini runs scripting (T074 checks 1-2: it cannot run Lua), and that any real FC reports a usable `voltage_resting_estimate` (the estimate depends on `BATT_` resistance learning).

### 4.2 SITL
The binary `C:/Users/dillo/tools/ardupilot-sitl/sitl/ArduPlane.elf` (waf configure "Scripting: maybe", Lua symbols present) runs scripting: with `SCR_ENABLE 1` and the script in `runs/<tag>/scripts` the log shows "spin_cap.lua loaded". Case: `run_fwd.py case=trans mass=1.64 wind=0 hold=25 cruise_s=8 r=1.33` (the T074 S 1.33 case) plus `P:SCR_ENABLE=1 P:BATT_MONITOR=4 P:BATT_VOLT_MULT=10.1 P:BATT_AMP_PERVLT=17 P:SIM_BATT_VOLTAGE=14.92 P:BATT_ARM_VOLT=0 P:Q_M_BAT_VOLT_MAX=0 P:Q_M_BAT_VOLT_MIN=0 P:Q_M_BAT_CURR_MAX=45 P:Q_M_SPIN_MAX=1.0`. The battery monitor is on (the script needs it); the voltage compensation is off (as the plant has none). All runs exit 0, 126 s wall each.
| Run | alt gain m | handover V m/s | pitch use of 20 deg | alpha max deg | u max | motor A / pack A | cap run s | note |
|---|---|---|---|---|---|---|---|---|
| T074 S 1.33 (SPIN_MAX 1.0 constant, no battery monitor) | 30.7 | 13.8 | 0.44 | 10.5 | 0.814 | 6.4 / 25.9 | 0 | T074 check 3 |
| Lua run 1 | 31.7 | 13.8 | **0.61** | 10.6 | 0.814 | 6.4 / 25.9 | 0 | cap 0.900 to 1.000 in 10 s, V 14.7-14.9 |
| Lua run 2 (repeat) | 31.6 | 13.8 | **0.62** | 10.7 | 0.814 | 6.4 / 25.9 | 0 | |
| Lua final script (floor added) | 30.7 | 13.7 | **0.63** | 10.7 | 0.814 | 6.4 / 25.9 | 0 | |
| no script, same parameters (`SCR_ENABLE 0`) | 31.6 | 13.8 | **0.61** | 10.5 | 0.814 | 6.4 / 25.9 | 0 | control |
| Lua failsafe (no battery monitor) | 6.8 | **12.3** | 0.64 | **39.2** | 0.858 | 7.1 / - | 0 | "bad battery reading, SPIN_MAX 0.90" at 1.9 s |
Findings: (1) the script does what it is designed to do and does not change the transition (compare the no-script control). (2) **Pitch use is 0.61-0.63 against the 0.60 line** in every run with the battery monitor on, including the no-script control, against 0.44 in T074: the cause is a parameter or plant effect of `BATT_MONITOR 4` / `Q_M_BAT_CURR_MAX 45`, not the script; not isolated (one more run with the A.param compensation values would do it). The AR-010 record shows run-to-run scatter of the same measure (0.77 vs 0.61 on the same case), so this is one sample, but it is the only transition metric above its line. (3) The failsafe is safe but poor: at 0.90 the r 1.33 entry does not complete (alpha 39 deg, handover below 12.94 m/s), consistent with T074's -0.2 % fixed-cap window. Pass/fail on the whole case matrix was not repeated (one entry ratio).
Plant limits as SITL-FLIGHT.md s1-s2 (no cross-flow, no wash, battery drift not modelled; the plant holds 14.92 V). Files: `s4_*` in T076_data, runs in `sitl/runs/T076_*` (git-ignored).

## 5. Pad cup rows (row 5)

Open rows (T-071b B.3, reproduced at 1.64 kg in T-074 s3.2): CUP EVA bearing at the rim (15 x 2 mm) 0.01, at the pin hole (3 x 12 mm) 0.14, cup wall bending 0.15. The model (`landing_path_a.py` l.323-336) bears the cup-rim reaction R = Fs (L + D) / D (8.5 Fs for L 30 mm, D 4 mm) on the EVA at 0.17 MPa, the 30 N / 180 mm2 crush plateau of the foot, so the allowable rim force is about 2.4 N.
**Missing (all "-"):** (1) EVA foam grade and density of the foot pad (GER-002 is listed 0.7 g, the CAD volume implies 0.13 g/cm3, unsourced); (2) compressive stress-strain at the landing rate (about 1.2 m/s drop, strain rate) and the plateau, loading and unloading; (3) EVA bearing allowable against a 2 mm rigid rim (local indentation / shear-out, not the bulk crush plateau, which is what the crude model uses); (4) EVA shear / tear strength and the pin-hole bearing allowable; (5) the bond allowable PETG-to-EVA and EVA-to-UHMW (T-071b J8, "bond on EVA/PE '-'"); (6) compression set and temperature behaviour; (7) the friction of the UHMW face on the real surfaces (mu 0.30 / 0.40 is EST).
**Coupon test that closes them** (printed PETG cup + the real pad foam, no new part design):
- Specimens: n = 5 each of (a) cup-rim indentation: EVA block as in the foot, 15 x 2 mm printed rim pressed in at 0 / 10 / 20 deg to the foam normal; (b) pin-hole bearing: 3 mm CF pin through the pad hole loaded in-plane; (c) side-load rig: the whole foot (cup + EVA + UHMW face) with a lateral force applied at the lever of the real touchdown (L 30 mm).
- Loads: (a), (b) quasi-static to failure at 5 mm/min on a kitchen / luggage scale or the Jacobs load frame (record force vs displacement with a phone camera on a ruler), then a drop-rig at 1.2 m/s (A-P13 rig, T-068 coupons) with a 1.64 kg-equivalent mass and a 30 N plateau; (c) lateral force ramp at constant 30 N normal.
- Measure: force at first visible indentation > 0.5 mm, at 2 mm, at pad tear-out; the EVA plateau and its rate sensitivity; density by weighing.
- Allowables: plateau and rim / pin bearing = mean - 3 sigma (or the minimum of five) divided by KP 2.156 for the limit-load RF; replace `EVA_BEAR` 0.17 MPa and the rim model in `landing_path_a.py`, re-run rows 0.01 / 0.14 / 0.15.
- Pass line: RF >= 1.0 at the limit force the cup sees (Fs at the demand plus R from the geometry); if the rim bearing stays < 1.0, the fix is geometry (deeper cup so L / D falls) or a stiffer insert, not a relaxed allowable.
This also carries the bond-integrity rows (P3 0.25, P5 0.97, P10 0.08, P13 0.54 at 1.64 kg) via the node coupons already listed in T-068 s7.

## 6. Findings for the conductor
| ID | Severity | Finding |
|---|---|---|
| F-1 | **CRITICAL, stop row** | C6 hub FEA at the rigid-body landing demand, 1.64 kg: whole-hub p99 RF 0.94, aft-zone 1.03; x1.5 0.62 / 0.69. The collar is fine (2.19); a hot spot between block face and collar (167 MPa single element) governs. The D-209 hub itself is 0.48 / 0.80 at this load. No listed fix closes it; candidates in s1.5 need more FEA. |
| F-2 | MAJOR | The T-071b hub rows used the span-axis moment only; the FEA envelope includes arm-group Mx 6.3 and Mz 17.6 N m from the drift cases. The bridge tube bending for that (about 106 MPa x 1.725 vs 350) was not rechecked here (hand arithmetic, RF about 1.9, EST). |
| F-3 | MAJOR | A-P10 passes only against the band re-based at 1.64 kg (88.0 Hz, hi-corner 79 Hz); with T-067 masses and the old band it is a stop-rule hit. Conductor must re-base `iter2_eval.RPM_HOVER` / A-P10 text; tap test required. |
| F-4 | MAJOR | SITL pitch use 0.61-0.63 of 20 deg (> 0.60) with the battery monitor on; not caused by the Lua. Failsafe to 0.90 fails the r 1.33 entry at 1.64 kg. The Kakute cannot run Lua (T074). |
| F-5 | MINOR | Pin 3 x 3 / 4 mm rows pass at both masses (1.12 / 1.97 at 1.50 kg, 1.43 / 2.53 at 1.64 kg); demand falls with mass in that case. R4 junction needs r >= 1.5 mm fillets (Kt EST). |
| F-6 | OBSERVATION | The sparse parts of my method are labelled: partition B hub-group path, straight collar, EST mass mapping, EST Kt. |

Proposed CHANGE-LOG text (for the conductor, not written): "D-2xx T-076: C6 hub FEA at the rigid-body landing demand 1.64 kg: collar RF 2.19, whole-hub p99 RF 0.94 (hot spot at the block face / bore floor), D-209 hub 0.80; flight and strike cases pass; pins 3 x 3 / 4 mm 1.43 / 2.53; R4 fillets r >= 1.5 mm; A-P10 passes only against the 1.64 kg band; Lua spin cap runs in SITL."

## Files
`redesign/qp/A/mechanism/out/T076_o4b_analysis.md` (this), `redesign/qp/A/mechanism/out/T076_data/` (scripts `make_fea_hub_c6.py`, `fea_hub_c6.py`, `t076_main.py`, `t076_traces.py`, `t076_step4.py`, `t076_pin_rows.py`, `t076_modal.py`, `arm_cup_checks_t076.py`, run scripts, all `s1_`-`s4_` outputs, `t076_hub_result_*.json`, `fea/`), `redesign/qp/A/sitl/lua/spin_cap.lua`.
