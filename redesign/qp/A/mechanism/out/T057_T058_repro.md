# T-057 / T-058 reproducibility reruns (R-PHY-09, R-PHY-10), 2026-11-19

Approval: Dillon, chat 2026-11-19, "Yes, rerun them" (exception to "no new sims until final"). Git base `73d95966`, working tree dirty from other agents; nothing committed, no docs/*.md edited, no committed result file overwritten (rerun tags `*rr` / `Z5_gb0_rerun`; the temporary FEA outputs were copied here and removed from `out_fea/`). Raw outputs: `redesign/qp/A/mechanism/out/T057_T058_repro_data/`. Machine: Windows 11, 20 logical CPUs, 63.8 GB RAM (30.5 GB free at start), Python 3.14, MATLAB R2025a (CHOLMOD / dissect solve), gmsh 4.15.2.

Analysis categories: T-057 = rigid-body dynamics (plus a hand-calculation static tip-over); T-058a = FEA; T-058b = flight dynamics (ArduPilot SITL + the 6-DOF plant `a_plant.py`; closed-loop, wall-clock coupled).

## 1. Commands, exit codes, wall times

| # | Command (cwd given) | Exit | Wall |
|---|---|---|---|
| 1 | `python -I landing_a.py` (structures/) default plateau 45 N | 0 | 21.2 s |
| 2 | `python -I landing_a.py 30` (structures/) = the 30 N plateau of the committed record | 0 | 22.3 s |
| 3 | scratch copy of `landing_a.py` with the pre-e29526c3 mass list (4 x 81.06 g) `python -I ... 30` (diagnostic) | 0 | about 22 s |
| 4 | `python -I fea_arm.py --level 0 --variant current --tag _d208rr` (structures/) | 0 | 3 min 39 s (mesh 9 s, assemble 40 s, solve 102 s incl. MATLAB chol 25 s) |
| 5 | `python -I fea_hub.py --level 0 --tag d209rr --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8` (the command in FEA-HUB.md l.135, without `--fields`) | 0 | 28 min 25 s (mesh + solve 359 s, then about 22 min of post-processing at 11 GB resident; peak memory fine, no paging) |
| 6 | `SCR=<old scratchpad> $SCR/venv/Scripts/python.exe run_fwd.py Z5_gb0_rerun case=trans inst=0 mass=1.50 wind=0 from=0 chain=1 hold=30 cruise_s=15 P:THR_MAX=80 P:Q_WVANE_ENABLE=0` (sitl/) | 0 | 4 min 31 s |
| 7 | `$SCR/venv/Scripts/python.exe fwd_sum.py Z5_gb0_rerun` (sitl/) | 0 | seconds |

Job 5 exceeded the 20 min guideline by 8 min because of post-processing, not memory; it was left to finish because the solve was already complete and memory was safe.

## 2. T-057 landing / tip-over (landing_a.py)

Cited in: `structures/structures_run.md` s5 (table, 30 N plateau, 1.50 kg), `structures_a.py:206`, `proofs/claims_a2_struct.py:118` ("read, not re-run"), CHANGE-LOG D-195, `docs/capability-audit.md:43`, `docs/audits/2026-11-18-physics-labels.md:48`.

Limits (structures_run.md s5, EST/ours): usable foam stroke 20 mm; peak load factor <= 12 g (A-P5); no tip-over (end tilt <= 3 deg); static tip-over about the narrow axis >= 30 deg; side load per foot against the scaled cap about 14 N (MARGINAL at 20 N).

Important usage note: running the script with no argument uses plateau 45 N, but the record uses 30 N per foot (0.17 MPa x 12 x 15 mm pad, EST). The comparison below uses 30 N (`landing_a.py 30`). Foam plateau and stroke remain unmeasured (coupon test pending).

Static (hand calculation in the script): rerun CG 22.9 mm aft of LE (committed 25.2), tip-over narrow 33.0 deg (committed 33.2), wide 53.9 (54.1), parked broadside tip speed 7.44 m/s (7.4), restoring/overturning at 5 m/s 2.21 (2.21). PASS (>= 30 deg).

Dynamic, 30 N plateau, 1.50 kg: committed (structures_run.md) vs rerun

| Case | stroke mm (c / r) | set mm (c / r) | Fmax N (c / r) | side N (c / r) | n g (c / r) | tilt deg (c / r) | drift mm (c / r) |
|---|---|---|---|---|---|---|---|
| hard level 1.2 | 8.3 / 8.3 | 6.8 / 6.8 | 40 / 39.7 | 0 / 0 | 10.8 / 10.79 | 0.0 / 0.0 | 0 / 0 |
| hard 10 narrow | 13.9 / 13.9 | 12.4 / 12.4 | 40 / 39.9 | 14 / 14.3 | 5.4 / 5.43 | 1.8 / 1.8 | 142 / 142 |
| hard 10 wide | 8.2 / 8.2 | 6.7 / 6.7 | 45 / 45.1 | 18 / 18.0 | 6.1 / 6.13 | 0.1 / 0.1 | 35 / 36 |
| hard 7+7 | 9.1 / 9.2 | 7.6 / 7.7 | 45 / 45.2 | 18 / 18.1 | 5.7 / 5.67 | 0.3 / 0.4 | 17 / 21 |
| hard 10 narrow + drift .5 | 15.2 / 15.4 | 13.7 / 13.9 | 40 / 40.0 | 16 / 16.0 | 5.4 / 6.68 | 2.1 / 2.2 | 3 / 23 |
| hard 10 wide + drift .5 y | 11.1 / 11.0 | 9.6 / 9.5 | 47 / 46.7 | 19 / 18.7 | 6.4 / 6.34 | 0.4 / 0.4 | 98 / 104 |
| normal 0.5 level | 2.3 / 2.3 | 0.8 / 0.8 | 33 / 32.8 | 0 / 0 | 8.9 / 8.93 | 0.0 / 0.0 | 0 / 0 |
| normal 10 narrow | 3.3 / 3.3 | 1.8 / 1.8 | 34 / 33.5 | 13 / 12.7 | 6.9 / 6.92 | 0.1 / 0.1 | 87 / 97 |
| normal 10 wide + drift | 5.8 / 5.8 | 4.3 / 4.3 | 40 / 40.1 | 16 / 16.0 | 5.4 / 5.45 | 0.3 / 0.3 | 101 / 101 |
| hard, 1.381 kg, 10 narrow | 12.9 / 12.9 | 11.4 / 11.4 | 40 / 39.5 | 14 / 14.1 | 5.8 / 5.83 | 1.6 / 1.6 | 147 / 144 |

(The largest n difference is the narrow + drift case, 5.4 vs 6.68; all n <= 12.)

Why small differences: commit e29526c3 changed the motor-assembly item in the script's mass list from 4 x 81.06 g to 4 x 88.26 g after `structures_run.md` was written. Rerunning with the old list (diagnostic job 3) reproduces every printed value of the committed table (stroke, set, Fmax, side, n, tilt, drift; static tip-over 33.22 deg, CG 25.15 mm) at the table's rounding. So the script is reproducible; the record predates the mass-list update.

Pass / fail vs limits (rerun, current mass list): worst stroke 15.4 mm of 20 (margin 4.6 mm, 23 %) PASS; peak load factor 10.79 g <= 12 PASS; no tip-over (max end tilt 2.2 deg <= 3) PASS; static tip-over 33.0 deg >= 30 PASS (margin 3.0 deg, thin); side load max 18.7 N against the scaled cap about 14 N: MARGINAL, unchanged from the committed flag (20 N); a pad face at mu <= 0.3 is the stated mitigation (EST). Committed result: same pass/fail on every line.

Information: at the script's default 45 N plateau the hard level case gives n 15.4 g (> 12 g, A-P5) with stroke 6.0 mm; the 30 N plateau is what keeps n below 12 g, so the foam coupon (plateau) is the controlling unknown. This is not a new finding of the rerun but is not stated in the committed record.

Conclusion: reproduced. Differences <= 0.2 mm stroke, <= 0.4 deg tilt, <= 10 mm drift (drift is a settling-position artefact, small absolute values); the only state change since the record is the mass list.

## 3. T-058a D-209 FEA reproducibility (fea_arm.py / fea_hub.py)

Notes read first: `memory/hub-redesign-d202-status.md` (MATLAB `dissect` solve, never run FEA together with Blender, one FEA at a time in `out_fea/sys`, check MATLAB first). I ran the two jobs one after the other, no Blender running. Two MATLAB processes from 2026-11-18 17:37 were already open (not mine, left alone).

Which case. D-209 cites the arm/cup FEA `fea_arm.py --level 0 --variant current --tag _d208` (116,118 elements, 578,493 unknowns, 3.7 min class) and the hub FEA `hub_fields_L0_d209.npz` (hub_result_L0_d209.json, 318,871 elements, 1.50 M unknowns). Both were rerun in full (the arm case is the smallest; the hub run is heavy but fit in memory and took 28 min).

Finding 1 (arm): the committed `_d208` case cannot be regenerated from the current code. `fea_arm.py --variant current` now builds the D-210 cup (fillets, lead collar, web: 166,730 elements, 808,377 unknowns), so the rerun reproduces the committed `current_d210` run (166,936 elements, 809,529 unknowns), not `_d208`. Compared with the D-209 numbers the cup changed by design in D-210 (CHANGE-LOG D-210, FEA-ARM.md 8.1); the arm tube did not. The D-209 headline arm values are therefore reproduced as follows (tube regions are independent of the cup fillets).

Arm / cup, limit stresses MPa (c209 = committed `_d208` = D-209 text, c210 = committed `current_d210`, r = rerun with current code; allowed per FEA-ARM.md 8):

| Item | c209 | c210 | r | r vs c210 | Allowed | Result (r) |
|---|---|---|---|---|---|---|
| Tube axial F2 (s >= 36) | 29.87 | 29.85 | 29.88 | +0.1 % | 203 | PASS |
| Tube axial S2 | 79.82 | 79.86 | 79.89 | +0.04 % | 350 | PASS |
| Tube shear S2 (tightest, ratio 3.1) | 9.55 | 9.54 | 9.55 | +0.1 % | 30 | PASS |
| Tube hoop S2 tip | 5.20 | 4.85 | 4.85 | -0.2 % | 40 | PASS |
| Cup 99th percentile F2 | 0.75 | 0.98 | 0.98 | 0.0 % | 9.3 | PASS |
| Cup 99th percentile S2 | 3.05 | 4.21 | 4.22 | +0.2 % | 20 | PASS |
| Cup single highest point S2 (p1) | 23.59 | 18.03 | 18.02 | 0.0 % | 20 | PASS (ratio 0.90) |
| Cup single highest point S3 (p1) | 39.45 | 13.62 | 13.63 | +0.1 % | 20 | PASS |
| Cup von Mises S2 | 18.45 | 11.09 | 10.76 | -3.0 % | - | info |
| Cup bond mean shear S2 | 0.45 | 0.35 | 0.353 | +0.1 % | 2.0 EST | PASS |
| Beam check tip deflection mm/N | 0.127 | 0.127 | see json | | | |

Tolerance stated: 1 % on the tube peak stresses and on percentile / mean values; 5 % on single-element maxima next to fillets (mesh-sensitive). Of 86 compared numbers (> 0.05 MPa; positions and mesh counts excluded) against c210, 53 are within 0.1 %, 79 within 1 %, 85 within 2 % and all within 3.0 % (worst: cup von Mises S2); the 1 % tolerance holds for every headline item above and fails on ten small or mesh-sensitive values (tube root / mid hoop 0.06-0.19 MPa up to +2.0 %, S2 bond p99 +1.2 %, S1 bond p99 +1.1 %), none a margin driver. The rerun differs from c210 only through gmsh remeshing (166,730 vs 166,936 elements; gmsh output is not bitwise repeatable here) and the equilibrium error is 3e-10 to 9e-10 N versus 3e-11 to 9e-11 N committed (both negligible).

Hub (D-209 commit run vs rerun, same GEO hash 25b07829, 318,836 vs 318,871 elements, hub 16.10 g both, residual 3.1e-10 max, equilibrium 2.07e-10 vs 2.03e-10). Values MPa:

| Item | committed | rerun | delta |
|---|---|---|---|
| F1 hub peak | 16.420 | 16.423 | +0.02 % |
| F2 hub peak | 19.189 | 19.194 | +0.03 % |
| S1 hub peak | 31.64 | 31.50 | -0.4 % |
| S2 hub peak | 18.288 | 18.425 | +0.7 % |
| S3 hub peak | 4.809 | 4.796 | -0.3 % |
| F1 bridge boss p99 (worst combo) | 4.812 | 4.760 | -1.1 % |
| F2 bridge boss p99 | 5.661 | 5.606 | -1.0 % |
| S2 bridge boss p99 | 7.100 | 7.035 | -0.9 % |
| F1 tube B axial / hoop / shear | 45.14 / 15.45 / 10.63 | 45.15 / 15.44 / 10.64 | <= 0.1 % |
| F2 tube B axial / hoop / shear | 51.65 / 17.76 / 12.25 | 51.66 / 17.76 / 12.25 | <= 0.1 % |
| S1 tube A axial / shear | 128.93 / 20.88 | 128.76 / 20.89 | -0.1 % / +0.0 % |
| S2 tube A axial / hoop / shear | 194.03 / 25.36 / 24.53 | 194.60 / 25.36 / 24.96 | +0.3 % / 0 / +1.8 % |
| S2 tube B shear | 17.68 | 17.69 | 0 |
| F1 / F2 bond peel (hub) | 2.703 / 3.111 | 2.720 / 3.131 | +0.6 % |
| pin von Mises F1 / F2 max | 39.66 / 46.47 | 40.04 / 46.91 | +1.0 % |
| centre block max, S1 envelope (worst delta) | 22.31 | 23.24 | +4.2 % |

Of 143 compared numbers (> 0.05 MPa, geometry and locations excluded): 70 are within 0.1 %, 128 within 1 %, 133 within 2 %, all within 4.2 % (worst: a single-element maximum in the centre block, S1 strike); 35 differ by more than 0.5 %. Peak, 99th-percentile and tube values on which the D-209 margins rest differ by <= 1.8 %. The 1 % tolerance is met for hub peaks and most tube values (exceptions: S2 tube A shear +1.8 %, bridge-boss p99 -1.0 to -1.1 %, pin von Mises +1.0 %); it is not met for singular single-element maxima (up to 4.2 %), which the project already judges by the 99th percentile (D-207). No pass/fail verdict changes: every margin quoted in D-209 / FEA-HUB.md holds on the rerun (e.g. tube A S2 shear 24.96 against the 30 MPa allowable at factor 1.0).

Conclusion: reproducible within 1 % on the quantities the margins are judged on (tube stresses, percentiles, means) and within 4.2 % on single-element maxima; the committed `_d208` arm file cannot be regenerated from current code because the cup geometry in `fea_arm.py` moved to D-210. Suggest the record cite `current_d210` as the regenerable case (open item for the record, below).

## 4. T-058b SITL transition Z5_gb0

Launch found: `sitl/jobs_z5.txt` line 13: `Z5_gb0 case=trans mass=1.50 wind=0 from=0 chain=1 hold=30 cruise_s=15 P:THR_MAX=80 P:Q_WVANE_ENABLE=0`, run through `jobq.py` -> `run_fwd.py <tag> inst=N <args>`, summarised by `fwd_sum.py` (writes `runs/<tag>/sum.json`). Committed run files dated 2026-11-15.

Toolchain check (before running). Not in PATH, not WSL (not installed), not in the repo. Found in a previous Claude session's scratchpad (`...\claude\1dc032cbc6faa005\dd3758e5-599a-4c53-9035-b3e3d186f97a\scratchpad`): `sitl\ArduPlane.elf` plus Cygwin DLLs, `src\quadplane.parm`, `venv\Scripts\python.exe` with pymavlink 2.4.50. Used as `SCR`. Whether this `ArduPlane.elf` is byte-identical to the 2026-11-15 binary: "-" (no hash recorded in the repo). That scratchpad is outside the repo and may be cleared by a reboot; a repo note on how to rebuild SITL (`SCR` layout) would be needed for a clean-machine rerun. The rerun ran with `inst=0` (committed inst unknown, immaterial) and created `runs/Z5_gb0_rerun/` (git-ignored, includes a new `logs/00000001.BIN`, not in git).

Result: no BLOCKER; the case ran to completion (exit 0, 4 min 31 s). Comparison, committed `sum.json` (c) vs rerun (r):

| Field | c | r |
|---|---|---|
| touch_in_flight | false | false |
| tipped_over (landing) | false | false |
| crossed_fence_110 | false | false |
| t_elevon_sat_s | 0 | 0 |
| t_cap_run_s / t_ge85_s | 0.0 / 0 | 0.0 / 0 |
| t_fwdone_s | 6.4 | 6.5 |
| t_to_1.3Vs_s | 7.4 | 7.5 |
| V_at_handover m/s | 13.7 | 13.7 |
| alt_gain_at_handover / alt_max_gain / alt_peak_abs m | 32.9 / 35.7 / 86.6 | 33.1 / 35.5 / 86.5 |
| pitch_max / roll_max_abs_after_fwdone deg | 89.8 / 0.9 | 89.8 / 0.9 |
| nz_max / alpha_max | 1.55 / 10.2 | 1.57 / 9.8 |
| elevon_max_deg | 9.4 | 11.7 |
| pitch_use of 15 / 20 / 25 deg | 0.61 / 0.46 / 0.37 | 0.77 / 0.57 / 0.46 |
| u_max (forward) | 0.78 | 0.787 |
| hinge_peak Nm | 0.0192 | 0.0242 |
| I_pack_peak A / I_motor_peak A | 23.8 / 5.9 | 23.9 / 5.9 |
| Wh_to_cruise / P_cruise_end W | 1.43 / 148 | 1.45 / 149 |
| V_end m/s / alt_end m | 17.1 / 83.7 | 17.0 / 82.3 |
| back-transition: lean_max_in_descent deg / u_max | 3.8 / 0.808 | 6.0 / 0.889 |
| back-transition: alt balloon max/min m | 89.4 / 83.7 | 88.5 / 82.3 |
| landing: t_touch s / sink m/s / lateral m/s | 247.3 / 0.02 / 0.01 | 246.9 / -0.04 / 0.03 |
| landing: lean at touch / final deg, drift m | 0.0 / 0.0, 0.0 | 0.0 / 0.0, 0.0 |
| landing: u_max_descent | 0.644 | 0.646 |

Pass lines (SITL-FLIGHT.md s1, EST): peak alt < 110 m PASS (86.5); climb < 60 m PASS (35.5); 1.3 Vs within 15 s PASS (7.5); no run at the 0.90 cap > 1 s PASS (0.0); no motor >= 0.85 > 1 s PASS (0); landing sink <= 1.2 m/s PASS; no tip-over PASS; stable cruise after PASS (roll 0.9). Elevon pitch use <= 0.60: of 15 deg FAILS in both runs (0.61 committed, 0.77 rerun: the rerun is further over); of 20 deg (the commanded endpoint of AR-006) 0.46 / 0.57 PASS; of 25 deg 0.37 / 0.46 PASS. Which basis governs is for the engineers; neither record states it as passing on the 15 deg basis.

Reproducibility verdict: the categorical outcomes (no touch in flight, no elevon saturation, no tip-over, no fence crossing, transition times within 0.1 s, handover speed identical) reproduce. The continuous controller-activity metrics do not reproduce to a tight tolerance: elevon peak +2.3 deg (+24 %), pitch use +26 %, back-transition lean 3.8 -> 6.0 deg, hinge moment +26 %, back-transition u_max 0.808 -> 0.889 (still below the 0.90 cap). SITL here is closed-loop with the plant paced by the wall clock (speedup 8) so run-to-run scatter is expected; one rerun cannot separate that scatter from a binary / source change (Z5 commit used possibly different build, "-"). The committed value should be quoted as one sample, not a reproducible number; a seed or repeat study (3-5 runs, about 5 min each) would give the spread. Not done (not requested).

## 5. Proposed ten-field analysis records (not written to docs; for the owner to add to docs/analysis-records.md)

### AR-008 Fin-tip touchdown and tip-over rerun (T-057, R-PHY-09; 2026-11-19)
- **Category:** rigid-body dynamics (explicit 6-DOF, 4 elasto-plastic foot springs, Coulomb friction) plus a hand-calculation static tip-over.
- **Solver / engine:** `redesign/qp/A/structures/landing_a.py` (`python -I landing_a.py 30`), Python 3.14, numpy; explicit integration dt 1e-4 s, T 1.5 s.
- **Model version:** git `73d95966` plus the uncommitted tree of 2026-11-19; script last changed in e29526c3 (mass list).
- **Inputs:** mass list scaled to the 1.50 kg gate (`ITEMS`, from structures_a roll-up, MASS-GATE s2); feet at x 0.30, y +-0.38, z +-0.18 m; foam plateau 30 N per foot, stroke 20 mm, elastic ramp 0.0015 m (EST, unmeasured, coupon pending); mu 0.40 (K09-L D-105, carried); sink 1.2 / 0.5 m/s, attitude error 10 deg, drift 0.5 m/s; rotor lift 2/3 W to 0.3 s, ramp to 0 at 0.6 s (EST).
- **Assumptions:** rigid body; foam crush plateau elasto-plastic with rigid stop at 20 mm; damping ratio 0.05; no aerodynamic loads in the static check except the parked broadside formula; no foot compliance in the fin.
- **Boundary conditions / loads:** ground plane z = 0; 10 cases as in `structures_run.md` s5 plus the 1.381 kg case.
- **Numerical settings:** dt 1e-4 s, 15,000 steps per case, 22 s for the full table; plateau argument 30 (the no-argument default is 45 N, which is not the design plateau).
- **Outputs:** `redesign/qp/A/mechanism/out/T057_T058_repro_data/landing_30.txt` (and `landing_45.txt`, `landing_30_oldmass.txt`); comparison table in `redesign/qp/A/mechanism/out/T057_T058_repro.md` s2.
- **Acceptance criteria:** stroke <= 20 mm; n <= 12 g (A-P5); end tilt <= 3 deg; static tip-over >= 30 deg; side load vs about 14 N scaled cap (marginal flag).
- **Result:** PASS on stroke (worst 15.4 mm), load factor (10.79 g), tilt (2.2 deg), static tip-over (33.0 deg); side load 18.7 N MARGINAL (unchanged). Committed record reproduced exactly with the pre-e29526c3 mass list; current list changes CG 25.2 -> 22.9 mm and results by <= 0.2 mm.
- **Limits / validity:** foam plateau and stroke unmeasured (at 45 N the level hard case gives 15.4 g, above 12 g); rigid-body only, no fin or rib flexibility (rib twist 5.9 deg in s6 is not coupled); structures_run.md s5 table should be refreshed with the current mass list.

### AR-009 Motor-mount / hub FEA reproducibility (T-058a, R-PHY-10; 2026-11-19)
- **Category:** FEA (linear elastic, tet10, direct solve).
- **Solver / engine:** `fea_arm.py --level 0 --variant current --tag _d208rr` and `fea_hub.py --level 0 --tag d209rr --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8`; gmsh 4.15.2, MATLAB R2025a `dissect` + `chol`, scipy, numpy; Python 3.14.
- **Model version:** git `73d95966` plus uncommitted tree; hub geometry hash 25b07829 (equal to the committed D-209 run); arm model = D-210 geometry (fea_arm.py moved past D-208).
- **Inputs:** as FEA-ARM.md s2-3 and FEA-HUB.md (materials, load cases F1, F2, S1-S3 and their factors; sources there).
- **Assumptions:** tied bonds (perfect bond), pins tied, no contact, no fatigue, support at the hub sleeve (arm) / far end of the bridge (hub), as in the committed records.
- **Boundary conditions / loads:** unchanged from the committed runs.
- **Numerical settings:** arm 166,730 tet10, 808,377 unknowns, residual max 9.3e-8 (per-case), equilibrium 9e-10 N max; hub 318,836 tet10, 1,503,642 unknowns, residual 3.1e-10, equilibrium 2.1e-10; solve 102 s (arm), 233 s (hub); wall 3 min 39 s and 28 min 25 s.
- **Outputs:** `redesign/qp/A/mechanism/out/T057_T058_repro_data/{result_L0_current_d208rr.json,hub_result_L0_d209rr.json}` and the logs in the same folder.
- **Acceptance criteria:** headline stresses within 1 % (tube, percentile, mean) and 5 % (single-element maxima) of the committed run, and no verdict change.
- **Result:** hub: tube / percentile quantities within 1.8 %, hub peaks within 0.7 %, worst single-element maximum +4.2 %; arm: tube axial F2 29.88 (29.87 committed), S2 79.89 (79.82), tube shear S2 9.55 (9.55); cup values equal the committed `current_d210` within 0.2 % except cup von Mises S2 -3.0 %; no margin changes. The committed `_d208` arm file is not regenerable from the current code (the cup geometry in the script is D-210); it was reproduced via `current_d210`.
- **Limits / validity:** gmsh remeshing is not bitwise repeatable (element counts differ by 35 and 206); singular corners stay mesh-sensitive (judged by percentile, D-207); no mesh-convergence study in this rerun; coupon-measured bond allowable still open.

### AR-010 SITL transition Z5_gb0 reproducibility (T-058b, R-PHY-10; 2026-11-19)
- **Category:** flight dynamics (ArduPlane SITL closed loop on the 6-DOF plant `a_plant.py`).
- **Solver / engine:** `sitl/run_fwd.py` + `sitl/fwd_sum.py`; ArduPlane.elf (Cygwin SITL build from a previous session's scratchpad, build hash "-"), pymavlink 2.4.50, Python venv of that session; JSON backend, speedup 8.
- **Model version:** git `73d95966` plus uncommitted tree; parameters `redesign/qp/A/A.param` as in the tree.
- **Inputs:** `case=trans mass=1.50 wind=0 from=0 chain=1 hold=30 cruise_s=15 P:THR_MAX=80 P:Q_WVANE_ENABLE=0`, cant 17, arm 1.2, seed 1, inst 0 (committed instance not recorded).
- **Assumptions:** plant limitations as SITL-FLIGHT.md s1 (prop cross-flow thrust, prop wash, battery drift, servo linkage not modelled); pass lines are the team's EST lines.
- **Boundary conditions / loads:** no wind, no gust, no turbulence; start 50 m, hover, forward transition, 15 s cruise, back-transition, descent, QLAND.
- **Numerical settings:** wall-clock coupled; 4 min 31 s; plant log `case.fwd.csv`.
- **Outputs:** `redesign/qp/A/mechanism/out/T057_T058_repro_data/Z5_gb0_rerun.sum.json` and `.result.json`; BIN dataflash in `sitl/runs/Z5_gb0_rerun/logs/` (git-ignored).
- **Acceptance criteria:** SITL-FLIGHT.md s1 pass lines (peak alt < 110 m, climb < 60 m, 1.3 Vs < 15 s, no cap run > 1 s, elevon pitch use <= 0.60, sink <= 1.2 m/s, no tip-over); reproducibility = same categorical outcomes, key metrics near the committed ones.
- **Result:** categorical outcomes and transition times reproduce; elevon pitch use 0.77 of 15 deg (0.61 committed; fails the 15 deg line in both; 0.57 / 0.46 of 20 / 25 deg pass), elevon peak 11.7 vs 9.4 deg, back-transition lean 6.0 vs 3.8 deg and u_max 0.889 vs 0.808.
- **Limits / validity:** one sample; run-to-run scatter not characterised; binary equality with the 2026-11-15 run unverified; the toolchain sits in an old session scratchpad outside the repo.

## 6. Open items for the record owner
1. structures_run.md s5 table predates the mass-list change (e29526c3); refresh or state the list it used.
2. State the plateau in the usage line of `landing_a.py` (default 45 N differs from the 30 N record).
3. Cite `current_d210` (regenerable) alongside `_d208` for the D-209 arm numbers.
4. Archive the SITL toolchain layout (`SCR`) or a rebuild recipe in the repo; hash the `ArduPlane.elf`.
5. Z5 elevon pitch use: decide the governing basis (15 / 20 / 25 deg); consider a 3-5 run repeat for the spread.
