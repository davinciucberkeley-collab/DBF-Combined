# Change requests from B3 (stability and control)

Numbers from `python -I redesign/team/B3/sc_analysis.py` and `run_avl_study.py` on 2026-11-10 (A1-R4a params; A3-R5
roll-up; B4 R3 swirl; D6 R3 elevon; C2 modes; F4 R4 crossovers). All inputs are read live from the claim graph.
Detail: `S-AND-C.md`. Answers the A1 R4 forward (CR-A3-23, CR-A2-19, CR-B4-13, CR-C2-03, CR-D6-08, CR-B3-19/20/21).

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
