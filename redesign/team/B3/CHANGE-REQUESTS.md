# Change requests from B3 (stability and control)

Numbers from `python -I redesign/team/B3/sc_analysis.py` and `run_avl_study.py` on 2026-11-10 (A1-R4a params; A3-R5
roll-up; B4 R3 swirl; D6 R3 elevon; C2 modes; F4 R4 crossovers). All inputs are read live from the claim graph.
Detail: `S-AND-C.md`. Answers the A1 R4 forward (CR-A3-23, CR-A2-19, CR-B4-13, CR-C2-03, CR-D6-08, CR-B3-19/20/21).

## Open (V1 verification round, 2026-11-10)

Numbers from `python -I redesign/team/B3/verify_asdesigned.py` (`claims.verify.json`) and `sens_zcg.py` on the CAD
fins (`fins.py` R4), the wing CAD elevon gaps and the A3-R6a roll-up. Detail: `SIMULATION-REPORT.md`.

| # | To | What | Why / numbers |
|---|---|---|---|
| **CR-B3-25** | **A1** (copy A3, D2, F1, C5, H1, J1) | **R-STATIC-MARGIN fails as designed.** Set `cg.x_range_m` = **[0.0466, 0.0514]** and `cg.x_target_m` = **0.0490** (14.6–16.1 % c) for the A3 CG height +0.0185 m, then bring the take-off CG forward to the target: **−3.2 mm** (basic) / **−4.6 mm** (predicted). Pack slide alone gives 0.8 mm (3.4 mm room × 0.237). Order of size: ~41 g at the pod nose (x −0.13) for the basic case, or the pack bay moved ~10 mm forward. Alternative: lower the CG (each 10 mm lower moves the aft limit 1.85 mm aft) | `CL-B3-V-CG-AFT-ENV` 0.05144 m; A3-R6a 0.0522 is **0.77 mm aft** (`CL-B3-V-CG-A3-AFT-ENV`, SM 4.76 % at 1.3 Vs), predicted 0.0536 is **2.15 mm aft** (SM 4.33 %). The R4 chain put the CG on the chord plane (`cg.z_target_m` 0); A3's CG is 18.5 mm above it, which moves the effective NP 3.4 mm forward at 1.3 Vs (AVL, hand formula within 0.4 %). Forward limit `CL-B3-V-CG-FWD` 0.0466 (trim at stall, z included); width 4.85 mm (≥ 4) |
| **CR-B3-26** | **A2** (copy A1, F4, H2) | **Spiral fails as designed:** t2 **3.51 s** < 4 s (`CL-B3-V-LAT-T2`). Decide one: (a) lower the CG to z ≤ 0 (t2 4.0 s at z 0); (b) keep z and amend R-SPIRAL to "≥ 3.3 s, wingborne flight only in roll-stabilised modes (FBWA / AUTO / QSTABILIZE), no MANUAL above 5 m" with F4 setting `FLTMODE*` accordingly | CG 18.5 mm above the fin side-force centre gives Cl_β +0.023 (R4 0.004): `sens_zcg.py` t2 = 4.01 / 3.84 / 3.68 / 3.51 / 3.34 s at z 0 / 6 / 12 / 18.5 / 25 mm. Dutch roll 0.28, short period 0.48 stay above their floors |
| CR-B3-24 | A3 | Publish the take-off CG height as a claim in metres (`CL-A3-CG-Z`), basic and predicted | B3 now carries it as `ASM-B3-V-ZCG` 0.0185 from `rollup.json`; it drives CR-B3-25 and -26 |
| CR-B3-27 | A1 | Change `cg.z_target_m` from 0 to the A3 value (or a limit, e.g. z ≤ +0.010 m) and narrow `cg.z_range_m` [−0.02, +0.03]: at +0.03 the aft limit is 5.5 mm further forward than at 0 | Every R0–R4 S&C number used z = 0 |
| CR-B3-28 | B2 (info) | Elevon η: XFOIL is not panel-converged (η_cm at α 4: 0.569 / 0.598 / 0.614 at 160 / 240 / 320 panels, extrapolated 0.69, GCI 15 %); SU2 SA (fully turbulent) gives a higher η, see `SIMULATION-REPORT.md` §4. `CL-B2-ELEVON-ETA` 0.606 is the low (conservative) end; the −20 % case that closed the R4 range is not supported by either method | No change needed; firm up with T-B3-TWIN-NP |
| CR-B3-29 | H1 (copy C5) | Balance marks for T-B3-CG-BALANCE: **0.0466 / 0.0514 m** once A1 adopts CR-B3-25 (was 0.0509 / 0.0549) | |

## Open (R4 re-run)

| # | To | What | Why / numbers |
|---|---|---|---|
| **CR-B3-22** | **A1** (copy A3, C5, H1, J1) | Set `cg.x_range_m` = **[0.0509, 0.0549]** and `cg.x_target_m` = **0.0529**. Re-run `CALC-A1-CG-RANGE`. It drifts now: the fwd-inside check is −0.85 mm with 0.050. C5 re-runs `CALC-C5-STANCE`. A3 re-picks the D-59 spacer stations on 0.0529: **503 g −0.024, 550 g −0.020, 680 g −0.010** (all keep ≥ 1.0 mm to both limits). H1 marks 0.0509 / 0.0549 at the fin roots. J1 re-runs on 0.0529 | `CL-B3-CG-FWD` 0.05085 (was 0.04953), `CL-B3-CG-AFT` 0.05490, `CL-B3-CG-TARGET` 0.05287 m; width 4.05 mm (≥ 4). The forward limit moves 1.3 mm aft because D6's elevon effectiveness (0.973 at the stall) and half of D6's 0.84° free play now come out of the 12.5° trim budget (12.08° left). The aft limit is unchanged. The D-47 datum (550 g at −0.022) gives 0.0525: +1.6 / +2.4 mm |
| **CR-B3-23** | **D6** (copy H1, F4) | T-D6-THROW: set each elevon servo's neutral at the centre of the measured free-play band (`SERVO5/6_TRIM`) and report the band per side. Hold the band ≤ 0.84°. Each 0.1° less returns about 0.1 mm of forward CG range | B3 charges half the band to trim (`ASM-B3-SLOP-TRIM-FRAC` 0.5). If the neutral cannot be centred, the full band counts, the forward limit goes to 0.0516 and the width to 3.3 mm (< 4 mm, fail) |
| CR-B3-19 (rev R4) | F4 (copy C2, H2) | Hover pitch crossover ≤ **4.5 Hz** and yaw ≤ **2.4 Hz** until T-C2-TAP-TEST; then a static notch at the tapped symmetric and antisymmetric frequencies. Keep `INS_GYRO_FILTER` ≤ 40 Hz. Measure the motor thrust lag on the stand | At F4's R4 2.6 / 1.0 Hz: pitch 11.6 dB / 66°, yaw 22.0 dB / 69° (`CL-B3-FLEX-*`). The 12–15 Hz antisymmetric band (D-45) leaves ≥ 12.8 dB / 45.9° at the 2.4 Hz yaw ceiling. Pitch at 5 Hz: 5.1 dB (fail) |
| CR-B3-20 (rev R4) | B4 (copy H1) | T-B4-YAW: measure the hover yaw factor. **Cant floor:** 3.8° on `CL-B4-YAW-LOW` 1.40, 2.7° on 1.79. 7° stays (D-52). 5° (CR-B4-14) is acceptable if the measured factor is ≥ 0.92 | `CL-B3-HOVER-CANT-REQ` 3.76°. At 7°: yaw 2.87× / 2.88 rad/s² on 1.40 (≥ 1.5× / 2.0); 3.15× / 3.15 rad/s² on 1.79. At 5°: 2.33× / 2.34 rad/s² on 1.40 |
| CR-B3-21 | C2 | Publish the torsion high corners (antisymmetric 14.9 Hz, symmetric 27 Hz), modal damping and station inertia about the spar as claims. B3 carries them as `ASM-B3-TORSION-HIGH`, `ASM-B3-FLEX-ZETA` 0.02, `ASM-B3-STATION-IYY` 0.0125 kg·m² | Unchanged from R3 (forwarded by A1, D-47) |
| CR-B3-13 | B2 | (a) Publish the S5010 clmax-vs-elevon envelope as a `P:b2.xfoil.clmax_vs_flap` key. (b) Re-run the wing+fins AVL and compare Xnp with `CL-B3-XNP-AERO` 0.0739 m. (c) Firm up η at Re 2.6e5 | **η −20 % closes the CG range at R4**: the stall trim at the target goes to −13.3° against a 12.08° budget. η +20 % widens it to about 8.4 mm |
| CR-B3-16 | A2 | `R-CG-RANGE` text → `cg.x_range_m` | Unchanged |
| CR-B3-09 | H1, H2 | Plan `T-B3-CG-BALANCE` (marks **0.0509 / 0.0549 m**), `T-B3-TWIN-NP` (also gives η), `T-B3-YAW-DOUBLET` (aft mark, 1.3 Vs), `T-B3-HOVER-WIND`, and a tethered-hover gain-margin test for `CL-B3-FLEX-GM-*` | Every B3 claim is `UNVERIFIED` until a test runs |

## Closed at R4

| # | Status |
|---|---|
| CR-B3-17 | accepted (D-47) at 0.050–0.0549 / 0.0522; superseded by CR-B3-22 on the D6 terms |
| CR-B3-18 | superseded by D-47 (pack datum −0.022 with the bay moved 21 mm); the datum CG 0.0525 is inside the R4 range |
| CR-B4-13 (to B3) | done: cant sized on `CL-B4-YAW-LOW` 1.40 (3.8° floor); `CL-B4-YAW` 1.79 nominal |
| CR-D6-08 (to B3) | done: effectiveness 0.921 at VA (worst panel; 0.929 inboard), 0.973 at the stall; 0.84° play in the trim, roll, cruise authority and transition margins |
| CR-C2-03 / D-45 (to B3) | done: 11.7–14.9 Hz antisymmetric band swept in the yaw loop |

## Closed or superseded (R0–R3)

| # | Status |
|---|---|
| CR-B3-11 | adopted (D-24); range re-derived by CR-B3-17, then CR-B3-22 |
| CR-B3-12 | adopted (D-27, 7°) |
| CR-B3-14 | adopted (D-26, 0.21 m): `CL-B3-CNB` 0.0354 /rad at R4 |
| CR-B3-15 | holds: `CL-B3-VT-TRIM` 15.51 m/s, `ARSPD_FBW_MIN` 15.6 stays |
| CR-B3-01…08, -10 | closed or superseded at R0–R1 (see git history) |

## CDR fix round, 2026-11-13

| Id | To | What | Why (numbers) |
|---|---|---|---|
| CR-B3-30 | A2 | Accept `ASM-B3-GUST-DIFF-MAX` 0.40 (differential allowed in the 8 m/s gust) or set another value; `R-GUST-LEAN` now cites `CL-B3-HOVER-PITCH-RATIO-GUST`, `-DIFF-GUST`, `CL-B3-HOVER-YAW-WTIP-GUST-10` | 30 % cap gives 0.94 in pitch; 32 % is needed |
| CR-B3-31 | A3, A1 (S4) | `MASS-CG.md`: range [0.0394, 0.0513] m; first-flight station x ≤ 0.0465 m; ballast rule and cases as `S-AND-C.md` §9.1 | forward limit 0.03932, aft 0.05133 |
| CR-B3-32 | D3, E1 | Keep the 10° cant open until `T-B3-HOVER-YAW-WTIP` (twin TW3): no flight mount printed before it | `CL-B3-HOVER-YAW-WTIP-20` 1.32 < 1.5; 10° gives 1.69 |
| CR-B3-33 | F4, H2 | Flight card: wingtip-into-wind landing only up to 5 m/s; if the heading error passes about 20° let it swing broadside (pitch axis) rather than fight it; SITL S20 | saturation at 25° (5 m/s), 12° (8 m/s) |
