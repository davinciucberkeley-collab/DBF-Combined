# Change requests from B3 (stability and control)

Numbers from `python -I redesign/team/B3/sc_analysis.py` and `run_avl_study.py` at R3 geometry (A1-R3 params, A3
roll-up and B4 swirl as published at 15:04 on 2026-11-09). Detail: `S-AND-C.md`. Answers CR-A1-26, CR-J1-11,
CR-C2-03.

## Open (R3 re-run)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B3-17 | A1 (copy A3, C5) | Set `cg.x_range_m` = **[0.050, 0.0549]** and `cg.x_target_m` = **0.0522**. Re-run `CALC-A1-CG-RANGE`: it drifts on the new B3 claims and its aft check fails by 0.05 mm with 0.055 | `CL-B3-CG-FWD` 0.04953, `CL-B3-CG-AFT` 0.05495, `CL-B3-CG-TARGET` 0.05224 m. The NP moved 0.3 mm forward: the wider pod (D-25) gives −0.95 mm and the props at −0.0082 give −1.95 mm. The taller fins do not change the longitudinal NP |
| CR-B3-18 | A1, A3, D2 (copy C3, C5, H1, H3) | **Move the pack's nominal centroid from x −0.001 to x −0.012 m** (the B3 target station for a 550 g pack; 11 mm forward, inside the bay's 14 mm forward trim travel), and mark the station per weighed pack: **680 g at x 0.000, 550 g at −0.012, 503 g on the forward stop (−0.015)**. A1 changes the D-24 note; H3 puts the pack mark on the flight card | With the pack at −0.001, A3's R3 CG is **0.0548 m, 0.15 mm ahead of the aft limit** (`CL-B3-CG-CENTRED-AFT`): SM 5.05 % with no allowance for build scatter. A 503 g pack at −0.001 gives 0.0559 m, 1.0 mm behind the aft limit. At −0.012 the 550 g pack puts the CG on the target with 3.1 mm of forward travel left (`CL-B3-PACK-SLIDE-LEFT`); a 680 g pack left there gives 0.0489 m, 0.7 mm ahead of the forward limit; a 503 g pack on the forward stop gives 0.0529 m (inside) |
| CR-B3-19 | F4 (copy C2, H2) | Hover pitch rate loop: **crossover ≤ 4.5 Hz** (not 5 Hz) until T-C2-TAP-TEST gives the symmetric mode, then a static notch at that frequency. Keep `INS_GYRO_FILTER` ≤ 40 Hz unless the notch is in. Yaw crossover ≤ 2.4 Hz with the P+I shape (no D). Measure the motor thrust lag on the stand (GT): below 30 ms the pitch margin falls under 6 dB at 4 Hz | `CL-B3-FLEX-GM-PITCH` 7.4 dB at F4's 4.0 Hz (21.7 Hz mode), 5.1 dB at 5 Hz. `CL-B3-XOVER-MAX-PITCH` 4.5 Hz, `-YAW` 2.4 Hz. Yaw gain margin 16 dB at 1.8 Hz. Sensitivity at 4 Hz: motor lag 25 ms 4.2 dB, gyro filter 80 Hz 2.7 dB, damping 1 % 7.2 dB |
| CR-B3-20 | B4 (copy H1) | T-B4-YAW: measure the hover yaw factor on the stand with a fin mock-up. B3 carries both brackets, R3 1.79 (`CL-B4-YAW`) and R0–R2 0.48 (`ASM-B3-SWIRL-LOW`) | At 7° both brackets pass: yaw ratio 3.15 / 2.23 (≥ 1.5), acceleration 3.22 / 2.28 rad/s² (≥ 2). The low bracket has 14 % margin on acceleration |
| CR-B3-21 | C2 | Publish the high corners (antisymmetric 14.9 Hz, symmetric 27 Hz), the modal damping you assume, and the station inertia about the spar as claims. B3 carries them as `ASM-B3-TORSION-HIGH`, `ASM-B3-FLEX-ZETA` 0.02 and `ASM-B3-STATION-IYY` 0.0125 kg·m² | The pitch margin depends on the low corner frequency only (the mass ratio cancels in the two-inertia model); the damping moves it by 0.1–0.2 dB per 1 % |
| CR-B3-13 | B2 | (a) Publish the S5010 clmax-vs-elevon envelope as a `P:b2.xfoil.clmax_vs_flap` key so B3 can drop `ASM-B3-CLMAX-FLAP`. (b) Re-run the wing+fins AVL and compare Xnp with `CL-B3-XNP-AERO` 0.0738 m. (c) η and Δcm at Re 2.6e5 for c 0.32 | The forward CG limit moves about 3 mm per ±20 % in η. Unchanged from R1 |
| CR-B3-16 | A2 | `R-CG-RANGE` text → `cg.x_range_m`. The 30 % cap now passes yaw at 7°, so it can stay as worded | Unchanged from R1, part 2 closed by D-27 |
| CR-B3-09 | H1, H2 | Plan tests `T-B3-CG-BALANCE` (mark both limits at the fin roots: **0.050 and 0.0549 m**), `T-B3-TWIN-NP`, `T-B3-YAW-DOUBLET` (aft mark, 1.3 Vs), `T-B3-HOVER-WIND` and a tethered-hover gain-margin test (raise P to oscillation, gyro FFT) for `CL-B3-FLEX-GM-*` | Every B3 claim is `UNVERIFIED` until a test runs |

## Closed at R3

| # | Status |
|---|---|
| CR-B3-11 | adopted (D-24); range and target re-derived at R3 by CR-B3-17; pack station by CR-B3-18 |
| CR-B3-12 | adopted (D-27, 7°): `CL-B3-HOVER-YAW-RATIO` 3.15, `-ACCEL` 3.22 rad/s² pass; cant needed with B4's R3 factor 2.6° (`CL-B3-HOVER-CANT-REQ`) |
| CR-B3-14 | adopted (D-26, 0.21 m): `CL-B3-CNB` 0.0357 /rad at the aft limit and 1.3 Vs, pass (+19 %); 0.19 m fins would give 0.0269 |
| CR-B3-15 | holds: `CL-B3-VT-TRIM` 15.53 m/s, so `ARSPD_FBW_MIN` 15.6 stays; trim −6.1° at 16 m/s, −12.6° at the stall at the forward limit; back-transition motor moment up to 1.09 N·m (20 % of the differential) |

## Closed or superseded (R0, R1)

| # | Status |
|---|---|
| CR-B3-01 | superseded by CR-B3-11; elevons 22 % c, both panels, ±25° kept |
| CR-B3-02 | adopted (D-04, option O4b) |
| CR-B3-03 | superseded (D-08, D-17) |
| CR-B3-04 | superseded by CR-B3-15 |
| CR-B3-05 | adopted at 3° (D-09), now 7° (D-27) |
| CR-B3-06 | closed: B3 uses `CL-B2-DCM-VISC`, `CL-B2-ELEVON-ETA` and B2's critical-section method |
| CR-B3-07 | superseded (D-21) |
| CR-B3-08 | done: `R-DIRECTIONAL` exists; `CL-B3-CNB` and `CL-B3-DR-ZETA` verify it |
| CR-B3-10 | done (D-18) |
