# Change requests from H1 (ground test engineer)

Revision H1-R2, 2026-11-09. Open requests first, then closed ones, then requests received and how H1 resolved them.

## Open requests

| # | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-H1-01 (R2) | A1, C1 | After GT-02d, set `requirements.thrust_limit_per_motor_n` to the measured peak (max of 3 unlimited steps at the F4 cap, 16.8 V, ρ-corrected) rounded up to 0.5 N. Expect 21.5 N: the prediction is inside the stand's guard band | `CL-C1-T-CAP` 21.08 N vs 21.1 N leaves 0.02 N; stand U95 is 0.12 N | pass ≤ 20.98 N (`CL-H1-T-PEAK-ACCEPT`); 20.98–21.1 N retest; > 21.1 N C1 re-runs loads |
| CR-H1-04 | F4 | Confirmed by CR-F4-06 (`K09L-STAND.param`). Still open: if the build clamps `Q_M_SPIN_MAX` to 0.9, say which Bluejay max-throttle value the stand uses | GT-02d must run the cap as flown | cap 0.84 |
| CR-H1-05 | E1 | Confirm `ASM-E1-RM` 86 mΩ is line-to-line at 25 °C | GT-02a measures line-to-line, 4-wire | band 69–103 mΩ |
| CR-H1-08 | D3, D5 | Strap eye at each fin root ≥ 29.5 N; outboard lower surface at \|y\| 0.45 m free for the CG pins | GT-07, GT-13 | 4 × 29.5 N (`CL-H1-RESTRAINT-PER-TIE`) |
| CR-H1-09 | C1 | Publish whiffletree pad 4 as claims (`CL-C1-PROOF-Y4` 0.465 m, `-P4-LIM` 6.398 N); fix `pad_mass_kg_limit` and the `tree` text in `data/whiffletree.json`, which list pads 1–3 only | Pads 1–3 sum to 22.6 N, `CL-C1-PROOF-P-SIDE-LIM` is 29.0 N; H1 derives pad 4 from the difference (`ASM-H1-PAD4-Y` `UNVERIFIED`) | pad 4 0.652 kg; centroid 0.273 m = your `proof_pivot_side_y_m` |
| CR-H1-10 | C4 | Change `T-C4-MOUNT-STIFF` readout to an optical lever (mirrors on can and collar, wall at 3.0 m) and loads 0.5/1.0/1.5 kg | Two 0.01 mm dial gauges 30 mm apart see 8.7 µm at 0.5 kg at the pass stiffness, under one division | pass: net spot ≤ 4.69 mm at 1.5 kg (`CL-H1-MSTIFF-SPOT-ACCEPT`); U 9.6 % |
| CR-H1-11 | C2, J1 | `T-C2-TAP-TEST`: use the FC raw IMU at ≥ 1 kHz for anything above 80 Hz; the phone (~400 Hz) only for the 12–22 Hz wing modes. J1: retire `T-J1-TAP-TEST` (superseded by `T-C4-TAP-D3`) | A 400 Hz phone reads to 160 Hz; fin modes are ~275 Hz, 2P at the cap 312 Hz | need 935 Hz (`CL-H1-TAP-FS-REQ`) |
| CR-H1-12 | C6 | Publish the strip-anchor design force as a claim and fix the `T-C6-STRIP-ANCHOR` text (700 N) to match `CALC-C6-STRIP` | H1 sizes the lever frame on it (`ASM-H1-COUPON-MAX` `UNVERIFIED`) | 907.7 N; lever 1 177 N vs 1 135 N needed |
| CR-H1-13 | C1, C2 | Agree one wing limit proof. C2's `T-C2-WING-PROOF` (2 × 25 N per side over \|y\| 0.33–0.50, + 51 N at an upper tube end) vs C1's tree (29.0 N per side) | Two different limit cases on one flight wing; C2's is 1.7 × C1's total | GT-08 runs C1's tree; C2's case is held |
| CR-H1-14 | D5 | Confirm `T-D5-COUPON` pass lines: claims.json (U 34.5–38.5 N, L 29.5–33.0 N, 40 mm) or CR-D5-08 (30–37 N, peak ≤ 38 N, 30 mm). GT-15 uses claims.json | Texts disagree | ratio U95 0.006 (`CL-H1-D5-RATIO-U`) |
| CR-H1-15 | J1, F1, A2 | Retire `T-J1-XT60-HEAT` (AS150U replaced the XT60; `T-F1-CONN-HEAT` covers it); `T-J1-TUBE-BEND` = `T-C4-TUBE-BEND` | One test per claim chain | — |
| CR-H1-16 | I1 | Borrow table is in `GROUND-TEST-PLAN.md` (end). Keep `G12` at $17.00; `X09` ($15) only if Jacobs has no DMM with a K input (answer by 18 Nov). Tube result for CR-I1-08 by 10 Dec | CR-A1-39 | bought new $17.00 ≤ $20 |
| CR-H1-17 | C4 | `T-C4-FIN-PROOF` is at 1.5 × (ultimate level): run on a test-article fin quarter, not a flight fin; add its materials | Proof of a flight part stops at limit | 49 + 25 N, 77 N |
| CR-H1-18 | F3, F4 | Set raw-IMU batch logging ≥ 1 kHz (INS_LOG_BAT_MASK, INS_LOG_BAT_OPT) in the bench parameter set | GT-18 assumes 1 000 Hz | need 935 Hz; margin 6 % |
| CR-H1-19 | A2 | Test ids published (CR-A2-25): `T-H1-RESTRAINED-RUN` (verifies `CL-E1-ILIM-I`, `CL-F4-SPIN-MAX`, `CL-F4-BAT-CURR-MAX`), `T-H1-PACK-PULL`, `T-H1-ARM-KILL`; point `R-ESC-CURRENT` (a) and `R-ARM-KILL` at them | `R-ESC-CURRENT` (a) had no test | — |

## Closed

| # | Closed by |
|---|---|
| CR-H1-02 | D-39: rigs count; buy ≤ $20, borrow the rest |
| CR-H1-03 | C1 whiffletree (`team/C1/data/whiffletree.json`, CR-A1-33); follow-up CR-H1-09 |
| CR-H1-06 | CR-E3-06: ESC ≤ 33 K, motor ≤ 38 K, hard stops 70 / 80 °C at T₃₀ |
| CR-H1-07 | A2 adopted the names |

## Requests received

| # | From | Resolution in this folder |
|---|---|---|
| CR-A1-41 | A1 | GT-02d (guard band), GT-02e (cold pack), GT-04 (E3 lines, 600 s), GT-15 coupons, GT-16 tube by 10 Dec, GT-17, GT-18, GT-12 `T-F3-I2C-SCAN`, GT-14 `T-F5-RANGE`; borrow list |
| CR-A1-39 | A1 (to I1) | H1's borrow list written; only `G12` bought new |
| CR-A2-14, CR-A2-25 | A2 | `T-H1-RESTRAINED-RUN`, `T-H1-PACK-PULL`, `T-H1-ARM-KILL`; A2's ids used for every log |
| CR-A3-19 | A3 | re-run on A3-R4: weigh U/margin 4.9 % |
| CR-B1-16 | B1 | GT-02c |
| CR-C2-08 | C2 | GT-08 (`-TWIST`, `-WING-PROOF` held), GT-15 (`-XPS-COUPON`), GT-18 (`-TAP-TEST`) |
| CR-C3-07 | C3 | GT-15 (`-BOND-COUPON`, `-STOP-PUSH`), GT-09 (`-POD-PROOF`) |
| CR-C4-11, CR-C4-21 | C4 | GT-16, GT-17, GT-18, GT-09 (`-FIN-PROOF`, `-BLOCK-PROOF`), GT-15 (`-BOARD-COUPON`) |
| CR-C6-14 | C6 | all nine tests in GT-15 / GT-17 |
| CR-D5-08 | D5 | GT-15 (`-COUPON`, `-PAD-MU`), GT-09 (`-PROOF`, `-SIDE`), GT-10 (`-REPLACE`) |
| CR-E3-06 | E3 | GT-04 |
| CR-F3-10 | F3 | GT-12 (`-FW-LOAD`, `-I2C-SCAN`, `-5V`), GT-13 (`-COMPASSMOT`); `-VIBE`, `-HDOP` to H2 |
| CR-F4-06 | F4 | GT-01 signal and GT-02d use `K09L-STAND.param` |
| CR-F5-05 | F5 | GT-14 = `T-F5-RANGE`; `T-F5-FS-BENCH` in GT-12 |
| CR-I1-08 | I1 | GT-16, result by 10 Dec |
| CR-B1-06, CR-C1-07, CR-E1-11, CR-B4-09, CR-E2-09, CR-B3-09, CR-A2-10 | — | as R1 (GT-02, GT-03, GT-05, GT-07) |
