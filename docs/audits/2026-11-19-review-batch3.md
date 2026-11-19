# Review batch 3 (HEAD 7d94485d), independent. T-020, T-025, T-057, T-058

## T-020 (R-PHY-05): VERIFIED (minor findings)
Checked: electrical.py ROD_LEG_L = ROD_Z - ARM_Z0 - 0.25 = 2.50 mm (ROD_Z 9.45, ARM_Z0 = SV_Z1, boss height "-" stated in comments); CAD leg cylinder uses ROD_LEG_L; build step D3 (a_build_steps.py l.575) says cut 2.3-2.5 mm, never longer, no tail below arm, keeper MEC-008 holds it down. CAD, D3, ROD_KEEP 0.3 mm freedom and the keeper (MEC-008, 0.3 mm gap) agree. Hand arithmetic: lo end 0.25-0.15 = 0.10 mm above case; hi 0.40 above underside (1.6 of 2.0 mm engaged); 2.3 mm leg engages 1.4 mm at hi: matches the text.
D-212 F-1 (jog / free-fall of rod / 1.4 deg free play) was answered by rev 3 (L-leg + keeper); the F-1 option list did not include this exact option, but the Z-bend/keeper joint is the one now in CAD and the build text. Consistent. Fix is rung 2 on a cut dimension (not a model-only change); the build text carries the number.
Sweep honesty: DECLARED in linkage_poses_a.py is label-only ("NOT exempt; every hit counts"); report json has 52 poses = 17 angles x 3 states + static; I listed all 26 hits: static 10 (<=0.034), linkage hits only MEC-002/MEC-003 leg-in-arm-hole 0.011-0.024 mm (L and R), all under 0.05 tol; no rod/servo-case hit. Matches T020_zbend_fix.md section 6. Analytic sweep rerun (mid, 14 s): 228 pairs, 0 penetrating, worst 0.0, min clearance 0.066 mm: matches record. (The rerun rewrote linkage_sweep_collision.json git_head only; I restored it with git checkout.) Did not rerun the 474 s mesh sweep.
Findings:
- minor (m-1): wording "end 0.25 mm inside the arm underside" (CAD part name, DECLARED, AR text) is ambiguous: it means 0.25 mm ABOVE the underside, inside the hole. Reword.
- minor (m-2): lo margin 0.10 mm assumes the cut is never long; D3 says "never longer" so it is one-sided, but there is no go/no-gauge check step listed beyond "file to 2.5 mm gauge": acceptable, keep as build-time check.
- minor (m-3): leg in 1.3 mm hole vs 1.2 mm wire is 0.05 mm radial; hits are 12-gon facet artefacts (stated). Fine.
No required fix to close.

## T-025 (R-OPT-02..05): VERIFIED (minor)
Rerun strut_socket_d206.py: exit 0, governing in-layer 0.30/0.34/0.10/0.31/0.09, PASS; matches AR-011 and followup (0.34 / 0.72 across layers). Mass arithmetic recomputed: 1273.30 x 1.1174 + 0.032 x 1470 = 1469.825 g (margin 0.175 g = +0.18); group sum 216.1+108.2+8.4+353.04+279+62.5+4.02+47.06+37.96+25.98+131.04 = 1273.30; structure 489.72 (<=494); EST cuts 41.45 vs 41.44 recorded (rounding). mission_gate_a.py rerun gives 1.466 itemised, 4.21 min cruise at 1.47: matches. TR-1..3 present in engineering-decisions.md using log figures only; CHANGE-LOG entries present.
Findings:
- minor: margin +0.18 g is on an EST flat rule whose own input includes the gate (0.032 x 1470); it is honestly flagged as no buffer. Fine, but any further add breaks target=gate.
- minor: params-A.json, sitl/cad_mass.json (0.06 g low), structure_groups_g (4.8 g low) are stale and not regenerated; disclosed as an open item. Required: regenerate (gen_params_a.py, cad_mass.py) and record, before final verification.
- minor: R-OPT-05 acceptance "findings logged; actions as new D-entries": the retro Actions A1-A5 are only partly closed (A3 coupon open, A5 not checked); the ledger does not show new D-entries. Required: log remaining actions as D-entries or explicit open items, and R-OPT-04 benchmark gap stays open (stated).
Verdict: VERIFIED for the follow-up deliverables (roll-up, AR-011, TR rows); leave R-OPT-04/05 follow-ups open items.

## T-057 (R-PHY-09): VERIFIED with a required record correction
Reran `python -I landing_a.py 30` (rc 0): output identical, line for line, to T057_T058_repro_data/landing_30.txt (tip-over 33.0 deg, worst stroke 15.4, n 10.79, side 18.7 N). The old-mass diagnostic file reproduces the committed structures_run.md table (e.g. narrow+drift n 5.44, drift 3 mm), supporting the "record predates e29526c3 mass-list change" explanation. "Reproduces" is justified for the script and for pass/fail.
Findings:
- moderate (record accuracy): AR-008 Result says current list "changes results by <= 0.2 mm" and the repro.md conclusion says drift <= 10 mm and the largest n difference is noted. Actual: narrow+drift case n 5.4 -> 6.68 g (+24 %), drift 3 -> 23 mm (+20 mm), stroke +0.2. Required fix: correct AR-008/repro conclusion (drift up to 20 mm, n +1.3 g) and refresh structures_run.md s5 table (open item 1 already says so).
- moderate (labelling): side load 18.7 N versus the scaled cap ~14 N is called "MARGINAL (unchanged)"; it is 33 % over the stated 14 N cap (the inherited MARGINAL label was at 20 N vs 24.5 N K09-L cap). Required fix: state it as exceeding the scaled 14 N cap with the mu <= 0.3 pad mitigation (EST), not as pass.
- minor: static tip-over margin 3.0 deg and foam plateau unmeasured (45 N plateau gives 15.4 g > 12 g) are disclosed.

## T-058 (R-PHY-10): VERIFIED for FEA; SITL partially reproduces, honestly reported (VERIFIED with caveat)
Judged from tables only (no rerun). FEA: hub same GEO hash, 143 numbers, all within 4.2 %, margin quantities within 1.8 %; arm rerun reproduces current_d210 (not the old _d208; stated, with the cup geometry change). Raw jsons exist in the data folder. SITL: categorical outcomes and times reproduce (touch, saturation, tip-over, fence, handover speed); continuous metrics do not (elevon peak 9.4 -> 11.7 deg, pitch use 0.61 -> 0.77 of 15 deg, back-transition lean 3.8 -> 6.0, hinge moment +26 %), reported as scatter and one sample, not as reproducing; the fail of the 15 deg pitch-use line in both runs is disclosed. I checked the rerun sum.json values (0.77/0.57/0.46, 11.7, 0.0242) against the table: match. ArduPlane.elf SHA-256 de67d448...5acc matches TOOLCHAIN.md.
Findings:
- moderate: the acceptance "rerun output matches committed results" is met for FEA and categorical SITL outcomes only; the ledger text says this ("controller metrics scatter") but "reproduces" should not be applied to SITL controller numbers. Required fix: the record should quote the committed Z5 values as one sample; a 3-5 run repeat to give the spread is recommended (not required for this task); decide the governing pitch-use basis (15/20/25 deg) (the 15 deg line fails in both runs).
- minor: committed _d208 arm file is not regenerable; cite current_d210 (stated as open item).
- minor: toolchain hash now archived, outside-repo location remains (TOOLCHAIN.md).

Side effect note: my rerun of elevon_sweep_collision.py touched linkage_sweep_collision.json (git_head only); restored.
