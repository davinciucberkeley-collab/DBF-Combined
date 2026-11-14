# Change requests from H1 (ground test engineer)

Revision **H1-R3**, 2026-11-10. Open requests first (new R3 requests at the top), then closed ones, then requests
received and how H1 resolved them.

## Open requests

| # | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-H1-20 (R3) | C1 | Align `LOADS.md` and CR-C1-30's text with your 14:37 claims. GT-08 reads the claims | CR-C1-30's text and the claims disagree; a card built from the text would put 2.5 N too much on pad 2 | claims: pad 2 **5.14** N (text 7.66), sum **24.60** (27.08), relief **19.92** (19.40), step 2 **4.90 / 16.10** (4.85 / 15.85); masses 0.919 / 0.524 / 0.453 / 0.613, relief 2.031 kg |
| CR-H1-21 (R3) | E3 | `T-E3-ESC-PAD-CFD`: hold hover **thrust** ≥ **620 s** (5 τ), not ≈ 5 min; mount the dummy on 3 mm XPS with a second thermocouple under it, instead of hook-and-loop; set the pass line to the guard-banded f ≥ **1.205** | The 14.6 g dummy has τ = 123 s, so 5 min is 2.4 τ and reads h about 9 % high. Hook-and-loop conduction (~9 % of 3 W) is unknown unless it is measured | `CL-H1-ESCCFD-RUN` 617 s, `-U-H` 3.2 %, `-F-ACCEPT` 1.205 vs design 1.131; rise 28.2 K at the pass line |
| CR-H1-22 (R3) | D5 (cc C1, C5, A1) | Re-run `CALC-D5-SIDE` and change the `T-D5-SIDE` text from 35 N to **59.0 N** (`CL-C1-FOOT-SIDE-DESIGN-ULT`). Test the CR-A1-65 shoe | At 59.0 N the drawn rim scales from SF 1.05 to **0.62**; GT-09 would break it | `CL-H1-D5-SIDE-F` 58.96 N (6.01 kg), `CL-H1-D5-SIDE-RIM-SF` 0.62 |
| CR-H1-23 (R3) | C3 (cc D2) | (a) Confirm the 200 N bracket pull may go on the **flight** pod. It is the crash force, not 1.5 × limit; otherwise give a limit fraction or a second pod. (b) The `CL-C3-FEA-SADDLE-TIES` how-text names `T-D2-HANDLE-PULL`; point it at `T-C3-POD-PROOF` | A proof of a flight part stops at limit (CR-H1-17 rule). One test per claim chain | 199.6 N (20.35 kg) along +x and −z |
| CR-H1-24 (R3) | C4 | Update `T-C4-FIN-PROOF` in `claims.d3.json`: shoe **as drawn** (CR-C4-36), not the \|z\| 0.171 cheeks (CR-C4-30); add the two gauges and the 1.0 × comparison step. Publish the gauge-site predictions (face 3.4–4.3 MPa, strip 88 MPa at limit) as claims so `ASM-H1-FP-PRED` can retire. `T-C4-MOUNT-STIFF`: ≥ 1 100 N·m/rad, optical lever (CR-H1-10). `T-C4-TUBE-TORSION`: two lasers 0.30 m apart, report GJ | The procedure texts still describe R4. GT-09 and GT-17 run the R3 cards. **Also:** your 15:01 `claims.d3.json` raises `CL-C4-D3-MOUNT-K-REQ` to 1 966 N·m/rad while `ASM-C4-MOUNT-K-ROCK` is 1 500. A mount built to your estimate is expected to fail GT-17; say whether the mount, the collar or the requirement changes, and update CR-C4-41 (1 100) | split line 8.36 mm (3-D 3.70, shell now 18.86); pass spot ≤ 4.02 mm at 5.0 m; estimate reads 5.66 mm |
| CR-H1-25 (R3) | A1 (cc I1) | Decide: ground-test purchases are $26.00 (`G12` + `G13`), $6 over the D-39 line; plus ≈ $5 `EST` of resistors if Jacobs has none | CR-C4-38 gauges are needed for the as-drawn decision | `CL-I1-GROUNDTEST-BOUGHT` |
| CR-H1-26 (R3) | team (any member with a Berkeley account) | **Send `team/H1/JACOBS-LOAN-REQUEST.md` by 13 Nov** and file the written reply | D-72: levers 1 and 2 ($157.34) rest on Jacobs' written yes before 20 Nov; an agent does not send mail for the team | — |
| CR-H1-01 (R2) | A1, C1 | After GT-02d, set `requirements.thrust_limit_per_motor_n` to the measured peak (max of 3 unlimited steps at the F4 cap, 16.8 V, ρ-corrected) rounded up to 0.5 N. Expect 21.5 N: the prediction is inside the stand's guard band | `CL-C1-T-CAP` 21.08 N vs 21.1 N leaves 0.02 N; stand U95 is 0.12 N | pass ≤ 20.98 N (`CL-H1-T-PEAK-ACCEPT`); 20.98–21.1 N retest; > 21.1 N C1 re-runs loads |
| CR-H1-04 | F4 | Confirmed by CR-F4-06 (`K09L-STAND.param`). Still open: if the build clamps `Q_M_SPIN_MAX` to 0.9, say which Bluejay max-throttle value the stand uses | GT-02d must run the cap as flown | cap 0.84 |
| CR-H1-05 | E1 | Confirm `ASM-E1-RM` 86 mΩ is line-to-line at 25 °C | GT-02a measures line-to-line, 4-wire | band 69–103 mΩ |
| CR-H1-08 | D3, D5 | Strap eye at each fin root ≥ 29.5 N; outboard lower surface at \|y\| 0.45 m free for the CG pins | GT-07, GT-13 | 4 × 29.5 N (`CL-H1-RESTRAINT-PER-TIE`) |
| CR-H1-10 (R3) | C4 | Change `T-C4-MOUNT-STIFF` readout to an optical lever (mirrors on can and collar, wall at **5.0 m**, photo read-out) and loads 0.5/1.0/1.5 kg | Two 0.01 mm dial gauges 30 mm apart see 4.3 µm at 0.5 kg at the pass stiffness, under one division | pass: net spot ≤ **4.02 mm** at 1.5 kg (`CL-H1-MSTIFF-SPOT-ACCEPT`); U 6.9 % |
| CR-H1-11 | C2, J1 | `T-C2-TAP-TEST`: use the FC raw IMU at ≥ 1 kHz for anything above 80 Hz; the phone (~400 Hz) only for the 12–22 Hz wing modes. J1: retire `T-J1-TAP-TEST` (superseded by `T-C4-TAP-D3`) | A 400 Hz phone reads to 160 Hz; fin modes are ~275 Hz, 2P at the cap 312 Hz | need 935 Hz (`CL-H1-TAP-FS-REQ`) |
| CR-H1-14 | D5 | Confirm `T-D5-COUPON` pass lines: claims.json (U 34.5–38.5 N, L 29.5–33.0 N, 40 mm) or CR-D5-08 (30–37 N, peak ≤ 38 N, 30 mm). GT-15 uses claims.json | Texts disagree | ratio U95 0.006 (`CL-H1-D5-RATIO-U`) |
| CR-H1-15 | J1, F1, A2 | Retire `T-J1-XT60-HEAT` (AS150U replaced the XT60; `T-F1-CONN-HEAT` covers it); `T-J1-TUBE-BEND` = `T-C4-TUBE-BEND` | One test per claim chain | — |
| CR-H1-16 | I1 | Borrow table is in `GROUND-TEST-PLAN.md` (end). Keep `G12` $17.00 and `G13` $9.00; `X09` ($16.54) only if Jacobs has no DMM with a K input (answer by 20 Nov). Tube result for CR-I1-08 by 10 Dec | CR-A1-39 | bought new $26.00 (CR-H1-25) |
| CR-H1-18 | F3, F4 | Set raw-IMU batch logging ≥ 1 kHz (INS_LOG_BAT_MASK, INS_LOG_BAT_OPT) in the bench parameter set | GT-18 assumes 1 000 Hz | need 935 Hz; margin 6 % |
| CR-H1-19 | A2 | Test ids published (CR-A2-25): `T-H1-RESTRAINED-RUN` (verifies `CL-E1-ILIM-I`, `CL-F4-SPIN-MAX`, `CL-F4-BAT-CURR-MAX`), `T-H1-PACK-PULL`, `T-H1-ARM-KILL`; point `R-ESC-CURRENT` (a) and `R-ARM-KILL` at them | `R-ESC-CURRENT` (a) had no test | — |

## Closed

| # | Closed by |
|---|---|
| CR-H1-02 | D-39: rigs count; buy ≤ $20, borrow the rest |
| CR-H1-03 | C1 whiffletree (`team/C1/data/whiffletree.json`, CR-A1-33); follow-up CR-H1-09 |
| CR-H1-06 | CR-E3-06: ESC ≤ 33 K, motor ≤ 38 K, hard stops 70 / 80 °C at T₃₀ |
| CR-H1-07 | A2 adopted the names |
| CR-H1-09 | C1-R4 published `CL-C1-PROOF-Y4`, `-P4-LIM` (and relief, step 2); `ASM-H1-PAD4-Y` retired |
| CR-H1-12 | C6 published `CL-C6-STRIP-ANCHOR-F`; the frame size moved to CR-C6-33 / -39 (done in R3) |
| CR-H1-13 | CR-C1-27: one wing limit proof, `T-C2-WING-PROOF` withdrawn (C2 to remove it from its claims) |
| CR-H1-17 | C4 adopted the test article; R3 details in CR-H1-24 |

## Requests received

| # | From | Resolution in this folder |
|---|---|---|
| CR-C4-36, CR-C4-38 | C4 | GT-09 `T-C4-FIN-PROOF` on the as-drawn article: gauges F and S (half bridges with dummies, 0.45 V, shunt 1 744 µε), 25 mm dial to 1.0 × then a rule, 1.0 × comparison step, split line 8.36 mm (`CALC-H1-FINPROOF`); board-centre tap is in GT-18 (`T-C4-TAP-D3`, 71–73 Hz) |
| CR-C4-41 | C4 | GT-17 pass ≥ max(1 100, `CL-C4-D3-MOUNT-K-REQ`) = 1 966 N·m/rad today; wall 5.0 m, spot ≤ 4.02 mm (see CR-H1-24) |
| CR-C6-33, CR-C6-39 | C6 | lever 15:1 / 9:1 with steel plates: 2 942 N ≥ 2 664 N and 1 765 N ≥ 1 554 N; pass line read from `CL-C6-STRIP-ANCHOR-F` |
| CR-C3-20 | C3 | GT-15 `T-C3-STOP-PUSH` on bonded tray pieces (strut on a bridge offcut, front piece with its bed and nose wall); GT-09 `T-C3-POD-PROOF` (b) 199.6 N on the brackets, +x and −z (CR-H1-23) |
| CR-C2-15 | C2 | GT-16 step 4 GJ between two lasers (U 1.9 %), step 5 ring crush for E_hoop (U 5.5 %) |
| CR-E3-17 | E3 | GT-04 step 2b `T-E3-ESC-PAD-CFD` on a heated dummy, f ≥ 1.205 guard-banded, 620 s hold (CR-H1-21) |
| CR-C1-30, CR-C1-27 | C1 | GT-08 steps 1 and 2 from C1's claims (CR-H1-20 for the text mismatch); `T-C1-STATION-PROOF` G2 step in GT-09 |
| D-72 / CR-A1-67 | A1 | Jacobs request drafted (`JACOBS-LOAN-REQUEST.md`), not sent (CR-H1-26) |
| GT-07 marks, `T-D5-SIDE` 59 N | A1 action items | marks at 0.0466 / 0.0514 m, jig window 0.0472–0.0508 m; `T-D5-SIDE` at 58.96 N (CR-H1-22) |
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

## Dispositions 2026-11-13 (structures, D-91, D-101, D-102; Dillon Alcouffe)

| Id | Disposition |
|---|---|
| CR-H1-22 | **Closed (D-101).** D5-R8 shoe RF 1.27 at 59.25 N ult; `CL-H1-D5-SIDE-RIM-SF` now reads D5's FEA (`CALC-H1-SIDE-POD` re-run); `T-D5-SIDE` 60 N on two R8 shoes |
| CR-H1-23 | **Closed (D-102).** Flight pod brackets proofed at limit, 76.2 N +x and 51.4 N -z (`CL-H1-POD-BRACKET-F`, `-F-Z`); the 204.7 N crash force only on two test articles (`T-C3-BRACKET-CRASH`, `CL-H1-POD-BRACKET-CRASH-F`) |
| CR-H1-24 (mount) | **Closed (D-91).** Grip 18 mm: C4 estimate 2 235 vs need 1 455 N·m/rad; GT-17 pass 1 455 (`CL-H1-MSTIFF-K-PASS`), spot travel at 1.5 kg <= 5.54 mm (`-SPOT-ACCEPT`), expected 3.86 mm |

