# Change requests from B1 (aero performance)

Evidence for every row: `team/B1/PERFORMANCE.md` and `team/B1/claims.json` (run `python -I redesign/team/B1/performance.py`).
All numbers are at 2.6 kg and 16 m/s unless marked. Rev 3 (2026-11-09) answers CR-A1-30 (D-25, D-29, D-35, D-36).

## Open (rev 3)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B1-17 | C1, F4 (copy A1) | **VH is 25.7 m/s, not 21.8 m/s** (`CL-B1-VMAX` 25.68, at the 9 350 rpm cap, fresh pack, base drag; ± 1.5 m/s). Choose one: (a) C1 re-runs VD = 1.25 VH = **32.1 m/s** (q 631 Pa, against 454 Pa now), or (b) F4 adds a fixed-wing rpm or THR_MAX cap of about **7 950 rpm**, which holds level speed at 21.8 m/s (8 000 rpm gives 21.9 m/s, 8 590 rpm gives 23.6 m/s). With (b), H2 shows it in the first full-throttle level log. If the cap fails, VH is 34.5 m/s (`CL-B1-VMAX-NOCAP`, 12 550 rpm). | The proxy assumes zero thrust at the 5.5 in geometric pitch. APC puts zero thrust at J 0.64 (27.8 m/s at the cap). At 25 m/s the drag is only about 8 N. The cap binds on both packs: 11.6 V is needed and 13.6 V is available at the worst state |
| CR-B1-19 | A1, E2 (copy E1) | Rev 3 cruise values for `params.json#performance` and E2's budget: `CL-B1-CRUISE-P` **227.8 W** (pessimistic `-P-PESS` 300.6 W), current 15.4 / 20.3 A, `CL-B1-CRUISE-LD` 6.34, `CL-B1-CD0` 0.0513, `CL-B1-TRANS-ENERGY` 0.88 Wh, `CL-B1-CRUISE-ETA-PROP` 0.444, `CL-B1-CRUISE-ETA-DRIVE` 0.667. B1 level-cruise time is 16.3 min (12.0 pessimistic); E2 re-runs `CALC-E2-BUDGET-*`. `lean_*`, `stall_ms` and `hover_only_min` are unchanged. | Pod pressure drag +0.14 N (3.4 %), braces and collars +0.37 N (9 %), shorter tubes −0.18 N. The ids are unchanged, so every calc that reads them now drifts and needs a re-run |
| CR-B1-18 | C4, D3 | Give the four fin braces a rounded or elliptical section (10 × 3 mm strip with a radiused leading and trailing edge, Cd about 0.4), or fair them. | At Cd 0.80 the braces are 0.23 N (0.26 N with interference), the top of C4's 0.07–0.24 N range, and 6 % of cruise drag. Rounding them saves about 0.13 N, or 7 W and 0.5 min of cruise |
| CR-B1-12 | F4 | Rev 3 values: `AIRSPEED_CRUISE` 16, `AIRSPEED_MIN` 15.6 (D-36), `AIRSPEED_MAX` 18, `Q_ASSIST_SPEED` 13, **`Q_TAILSIT_RAT_FW` 12 °/s** (unchanged), `TECS_CLMB_MAX` 3 m/s, the fixed-wing rpm cap from CR-B1-17 (b). After the cold-pack stand run confirms a sag of at least 0.76, you may raise the rate to 15 °/s. Run the SITL pitch-over at 12 and 16 °/s on a sagged-pack battery model and log thrust saturation. | At sag 0.76 (D-35) the peak thrust fraction is 0.70 at 12 °/s, 0.77 at 15, 0.79 at 16 and 0.88 at 20. FW climb is 13.7 m/s at 80 % thrust (motor model) |
| CR-B1-14 | C5, H3 | Splay the feet, or otherwise raise the narrow-axis tip-over angle. Flight card: fin-tip landings only in steady wind ≤ 5 m/s; lay the aircraft flat when gusts exceed 8 m/s. | At a tip-over angle of 30.6° the landing wind limit is 5.8 m/s (+15 %). The parked tip-over wind is 8.9 m/s at 2.32 kg (+11 %) |
| CR-B1-15 | B2, B3 | Re-run the AVL polar with the pod (0.21 × 0.14 × 0.07) and the props, and publish `cd0_wing`, `e_oswald`, `cla_per_rad` and a **trimmed** CL(α) as params keys. | B1 uses `P:b2.avl.*` from the props-off run without the pod. The pod and brace drag are B1 hand estimates |
| CR-B1-16 | H1 | Thrust-stand points for the 11×5.5MR: static at 690 gf (calibration `CL-B1-KCAL` 1.13); full throttle at 14.0 V and at 13.6 V with the 100 A limiter (`CL-B1-NMAX-SAG` 120.1 rev/s); the A/B hover ratio against the 11×4.5MR (1.019). If the stand can run in an air stream (car top), add rpm at full throttle at 16 m/s (model: 8 530 rpm, limiter-bound). | Hover throttle 0.56 against the 0.60 limit and T/W 1.79 rest on sag 0.76 and 1.62 kg. The forward-flight full-throttle rpm drives VH and the FW climb |

## Closed

| # | To | Closed by |
|---|---|---|
| CR-B1-01 | A1 | D-01: `performance.cruise_ms` 16 |
| CR-B1-02 | A1 | superseded by CR-B1-10 |
| CR-B1-03 | B2 | CR-B2-08 answered |
| CR-B1-04 | B3 | CR-B3-07 answered for R0; R1 re-run is CR-B1-15 |
| CR-B1-05 | B4 | 11×5.5MR adopted (D-05) |
| CR-B1-06 | E1 | E1 constants adopted; stand points in CR-B1-16 |
| CR-B1-07 | F4 | superseded by CR-B1-12 |
| CR-B1-08 | F1 | forwarded by A1. Rev 3 currents: cruise 15.4 A (pessimistic 20.3 A), 2.5 m/s climb 30.3 A, B1 hover 26.1 A |
| CR-B1-09 | H2 | forwarded by A1; wind numbers in CR-B1-14 |
| CR-B1-10 | A1 | D-36 (rev 2 values carried); rev 3 values in CR-B1-19 |
| CR-B1-11 | E2 | forwarded by A1 (D-36); rev 3 values in CR-B1-19 |
| CR-B1-13 | A2, F3 | D-37: `airspeed_err_max_ms` 0.5 |
