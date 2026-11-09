# Change requests from B1 (aero performance)

Evidence for every row: `team/B1/PERFORMANCE.md` and `team/B1/claims.json` (run `python -I redesign/team/B1/performance.py`).
All numbers are at 2.6 kg and 16 m/s unless marked. Rev 2 (2026-11-09) answers CR-A1-13, CR-E1-05 and CR-E2-08.

## Open (rev 2)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B1-10 | A1 | Update `params.json#performance` from the rev 2 B1 claims: `cruise_power_w` **218** (`CL-B1-CRUISE-P`), `cruise_current_a` **14.7** (`CL-B1-CRUISE-I`), `ld_cruise` **6.9** (`CL-B1-CRUISE-LD`), `cruise_after_hover_min` **17.0** (`CL-B1-CRUISE-TIME`), `stall_ms` 11.9 (`CL-B1-VS-GATE` 11.86), `transition_min_ms` 15.5 (`CL-B1-VT-GATE` 15.42), `lean_5ms_deg` **16** (`CL-B1-LEAN-5MS` 15.8), `lean_8ms_deg` **36** (35.9), `hover_only_min` 11.9 (`CL-B1-HOVER-ONLY`, B1 hover 387 W). Keep `hover_power_w` 400 (E1); B1's 387 W cross-checks it (`CL-B1-HOVER-P-GATE` ≤ 400). `cruise_after_hover_pess_min` stays E2's until E2 re-runs; B1's pessimistic figure is 12.7 min. | The params entries still carry rev 1 (11×4.5MR, c 0.30, CLmax 0.9). CR-A1-13 done: 16 m/s, 11×5.5MR, c 0.32, CLmax 0.80, S5010 cd, hover 400 W |
| CR-B1-11 | E2 (copy E1) | Cruise model for CR-E2-08. Replace `ASM-E2-CRUISE-AERO` with these B1 claims: S 0.368 m², `CL-B1-CD0` 0.0452 (pessimistic × 1.3 = 0.0587), `CL-B1-K` 0.0950 (e 0.93) / `CL-B1-K-PESS` 0.1107 (e 0.80), trim 1.02 (`ASM-B1-TRIM`), `CL-B1-CRUISE-ETA-PROP` 0.426 (pessimistic 0.40), `CL-B1-CRUISE-ETA-DRIVE` 0.664 (motor + ESC + table calibration; it replaces both your η_motor 0.72 and the 1.05 circuit factor), avionics 6 W. Results: `CL-B1-CRUISE-P` **218 W** / `CL-B1-CRUISE-P-PESS` **285 W**, 14.7 / 19.3 A, `CL-B1-TRANS-ENERGY` 0.87 Wh per transition. E1: your `CL-E1-CRUISE-P-55` re-runs to 247 W because it reads L/D 5.6. Read `CL-B1-CRUISE-LD` 6.93 or `CL-B1-CD0` and `CL-B1-K` instead. | B1's pessimistic cruise time is 12.7 min (hover and transitions × 1.10, 285 W). Your 340 W pessimistic assumption was rev 1 aero. E2's `CALC-E2-BUDGET-BASE` and `CALC-E2-PROP55-SENS` now drift on B1's new values; re-run |
| CR-B1-12 | F4 | Rev 2 first-flight values, which replace CR-B1-07: `AIRSPEED_CRUISE` 16, `AIRSPEED_MIN` 15, `AIRSPEED_MAX` 18, `Q_ASSIST_SPEED` 13, **`Q_TAILSIT_RAT_FW` 12 °/s** (was 20), `TECS_CLMB_MAX` 3 m/s. Make whatever ends the forward transition in the firmware you fly happen at ≥ 15.5 m/s (`CL-B1-VT-GATE` 15.42 m/s). Run the SITL pitch-over at 12 and 20 °/s on a sagged-pack battery model and log thrust saturation. | With sag 0.72 (D-06) the pitch-over peak thrust fraction is 0.76 at 12 °/s, 0.84 at 15 °/s and 0.96 at 20 °/s. With a fresh pack, 20 °/s gives 0.59. Vs 11.86, Vmax 19.3, FW climb 4.7 m/s at 80 % thrust |
| CR-B1-13 | A2, F3 | Tighten `requirements.airspeed_err_max_ms` from 1.0 to **0.5 m/s** at 16 m/s, or ask A1 for a 16.5 m/s cruise speed. F3 calibrates the pitot (`ARSPD_AUTOCAL` or a ground-speed run both ways) before the first transition. | The margin from 16 m/s down to 1.3 Vs is 0.58 m/s. B4's 2 % pitot bound (0.32 m/s) fits inside it, but 1.0 m/s does not. 16.5 m/s costs 15 W and 1.1 min of cruise |
| CR-B1-14 | C5, H3 | Splay the feet, or otherwise raise the narrow-axis tip-over angle. Put on the flight card: steady wind ≤ 5 m/s for fin-tip landing, and lay the aircraft flat when gusts exceed 8 m/s. | At tip-over 30.6° the landing wind limit is 5.8 m/s (`CL-B1-WIND-HOVER-MAX`, +15 %) and the parked tip-over wind is 8.2 m/s at 2.15 kg (`CL-B1-GROUND-TIP-WIND`, +3 %). Rev 1 had 7.0 and 9.6 m/s at 37.2° |
| CR-B1-15 | B2, B3 | Re-run the AVL polar at c 0.32 with fins (chord 0.275), pod and the tube at x 0.045. Publish `cd0_wing`, `e_oswald`, `cla_per_rad` and a **trimmed** CL(α) (slope and zero-lift α with the elevon schedule) as params keys. | B1 reads `P:b2.avl.*` from the c 0.30 run. The AVL lift slope is about 3 % high at AR 3.59. B2's trimmed curve puts α about 1.5° above B1's at CL 0.5, which shifts the corridor pitch angles |
| CR-B1-16 | H1 | Thrust-stand points for the 11×5.5MR: static at 690 gf (calibration `CL-B1-KCAL` 1.13), full throttle at 14.0 V and at 13.6 V with the 100 A limiter (`CL-B1-NMAX-SAG` 116.9 rev/s), and the A/B hover ratio against the 11×4.5MR (`CL-B1-HOVER-PROP-RATIO` 1.019). | Hover throttle 0.59 against the 0.60 limit and T/W 1.69 against 1.6 both rest on the 0.72 sag and 1.62 kg |

## Closed

| # | To | Closed by |
|---|---|---|
| CR-B1-01 | A1 | D-01: `performance.cruise_ms` 16 |
| CR-B1-02 | A1 | superseded by CR-B1-10 (rev 1 numbers were for the 11×4.5MR) |
| CR-B1-03 | B2 | CR-B2-08 answered; used in rev 2 (`CL-B2-CLMAX-DESIGN`, `P:b2.avl.*`, `P:b2.xfoil.alpha0_2d_deg`, Ncrit 5/9 ratio) |
| CR-B1-04 | B3 | CR-B3-07 answered for R0 (CLα 3.56, trim drag +0.2 %, used in `ASM-B1-TRIM`); R1 re-run is CR-B1-15 |
| CR-B1-05 | B4 | CR-B4-08 answered; 11×5.5MR adopted (D-05) and modelled from B4's PER3 copy |
| CR-B1-06 | E1 | E1 constants adopted (`ASM-E1-KV`, `-RM`, `-I0`); stand points moved to CR-B1-16 |
| CR-B1-07 | F4 | superseded by CR-B1-12 |
| CR-B1-08 | F1 | A1 forwarded F1 the design currents (hover 29.9 A, climb 30.2 A). Rev 2: cruise 14.7 A (pessimistic 19.3 A), 2.5 m/s climb 30.3 A, B1 hover 26.1 A |
| CR-B1-09 | H2 | forwarded by A1 to the H1/H2 campaign; landing wind and tip-over numbers are now in CR-B1-14 |
