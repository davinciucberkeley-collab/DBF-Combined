# Change requests from H1 (ground test engineer)

Revision H1-R1, 2026-11-09. Requests received and how H1 resolved them are at the end.

## New requests

| # | To | What | Why | Numbers |
|---|---|---|---|---|
| CR-H1-01 | A1 | After GT-02d, replace `requirements.thrust_limit_per_motor_n` (17.8 N, `team/C1/LOADS.md`) with the measured peak static thrust (max of 3 steps, unlimited, at the F4 output cap, 16.8 V, ρ-corrected), rounded up to 0.5 N. Until then use C1's 21.1 N. | 17.8 N is already below C1's own prediction at the rpm cap (`CL-C1-T-CAP` 21.1 N), so that claim fails against the parameter today | predicted 21.1 N; stand pass line ≤ 21.1 N |
| CR-H1-02 | A1 | Say whether ground test equipment counts against the $2 000 budget; if yes, add a ground-test line. | Rigs are never flying mass but cost money | ≈ $160–180 `EST` (list in `GROUND-TEST-PLAN.md`) |
| CR-H1-03 | C1 | Issue the wing proof whiffletree at limit (load points and magnitudes per side, support stations) and confirm whether `CL-C1-WING-SHEAR-ULT` is ultimate or limit. | H1 uses one equivalent point per side: P = V_ult/1.5 at y = Mx_ult/V_ult. 42.7 N is close to n_lim·W/2 = 42.8 N, which reads like a limit value | interim 28.5 N at y 0.328 m per side; tip deflection ≤ 28.8 mm |
| CR-H1-04 | F4 | Provide a stand parameter set: same output cap and ESC protocol as the flight file, `Q_M_BAT_CURR_MAX` = 25 A for one station, motor test enabled, ESC rpm telemetry (Bluejay bidirectional DShot) logged. | GT-02d needs cap and limiter as flown on a single motor | 25 A = 100 A / 4 |
| CR-H1-05 | E1 | Confirm `ASM-E1-RM` 86 mΩ is line-to-line at 25 °C. | GT-02a measures line-to-line, 4-wire, corrected to 25 °C | accept band 69–103 mΩ |
| CR-H1-06 | E3 | Give the ESC case-temperature limit and the ambient scaling for GT-04. | No datasheet value; H1 uses 80 °C at 30 °C ambient as a placeholder | placeholder 80 °C |
| CR-H1-07 | A2 | H1 evidence file names: `team/H1/claims.json` (exists), `team/H1/GROUND-TEST-PLAN.md`, raw data `team/H1/logs/<test id>_<YYYYMMDD>.csv`; pack rows in `team/E2/pack_log.csv`. Add `GROUND-TEST-PLAN.md` as H1 evidence for `R-TIPOVER`, `R-ARM-KILL`, `R-COMPASS`, `R-PACK-RETENTION`. | CR-A2-10 | — |
| CR-H1-08 | D3, D5 | Leave a strap point at each fin root (or a printed eye) rated ≥ 29.4 N for the restrained run; keep the outboard wing lower surface at \|y\| 0.45 m free of hardware for the CG jig pins. | GT-07, GT-13 | 4 × 29.4 N (`CL-H1-RESTRAINT-PER-TIE`) |

## Requests received

| # | From | Resolution in this folder |
|---|---|---|
| CR-B1-06 / CR-B1-16 | B1 | GT-02c: static at 690 gf, full throttle at 14.0 V and 13.6 V with the limiter; A/B hover ratio in GT-02b |
| CR-C1-07 | C1 | GT-02d: peak thrust and torque on a fresh 16.8 V pack, unlimited and limited; pass ≤ 21.1 N / 0.42 N·m; CR-H1-01 replaces 17.8 N |
| CR-E1-11 | E1 | GT-02a (`T-E1-MOTOR-RM`, 5 motors) and GT-02b (`T-E1-STAND`): stand rated 20 kgf vs 2.69 kgf needed; supply ≥ 44.6 A or pack with V logged; both props |
| CR-B4-09 | B4 | GT-01 torque cell (1 kgf at 0.100 m) and rpm logging; GT-02b A/B; GT-03 installed run with mock-up on the carriage, plus a grounded-mock-up run; `T-B4-YAW` |
| CR-E2-09 | E2 | GT-05 fills `team/E2/pack_log.csv` (mass, size, capacity, IR at 25 and 10 °C) |
| CR-B3-09 | B3 | GT-07 `T-B3-CG-BALANCE` with marks at the fin roots; flight tests are H2's |
| CR-A2-10 | A2 | `team/H1/claims.json` written; names in CR-H1-07 |
| `T-A1-WEIGH` | A1 | GT-06: guard-banded line 2.595 kg |
