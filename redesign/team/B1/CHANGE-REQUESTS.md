# Change requests from B1 (aero performance)

Evidence for every row: `team/B1/PERFORMANCE.md` and `team/B1/claims.json` (run `python -I redesign/team/B1/performance.py`).
All numbers are at 2.6 kg and 16 m/s unless marked. Rev 3 (2026-11-09) answers CR-A1-30 (D-25, D-29, D-35, D-36).

## Open (design round, 2026-11-14)

Evidence: `review/DESIGN-ROUND-2026-11-14/B1.md`, `team/B1/round-2026-11-14/design_round_results.json`.

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B1-24 | A1 (copy E1, E2, F4) | `performance.transition_min_ms` 15.6 → **17.0**, `performance.cruise_ms` 16 → **17.0**, `cruise_power_w` 253 → **293**, `ld_cruise` 5.66 → **5.19**, `cruise_current_a` 16.2 → **19.8** (at 16 m/s instead: 256 W, 5.53, 17.3 A). Replaces the CR-B1-20 cruise values (235 W, k 0.0957). | D-122 flies 17 m/s; 1.3 Vs tripped 16.82 / clean 15.70 at the forward CG; E1 286.2 + 6 W at 17 m/s; W/D 5.187 at 2.6 kg with e 0.85 (k 0.1042, D-118) |
| CR-B1-26 | E2, E1, B2, B3 (via A1) | Wave 2: the B1 claims moved to 17 m/s and 9° cant. **E2:** `CL-B1V-CRUISE-P-GATE` and `-P-PESS`, which `CALC-E2-BUDGET-*` read as the 16 m/s level, are now 17 m/s values (278.2 W gate, 365.1 W pessimistic at 2.502 kg); `CALC-E2-BUDGET-V17`'s k becomes the E1/B1 chain ratio (292.2 / 278.2 = 1.050) and no longer carries the 16 → 17 scaling `EST`. Any E2 budget still titled 16 m/s now runs at 17. New `CL-B1V-CRUISE-P-GATE-PESS` 368.2 W and `-I-GATE-PESS` 24.9 A at the gate. **E1:** `p_check` against `CL-B1V-CRUISE-P-GATE` is now like for like at 17 m/s. **B2, B3:** `CL-B1V-CLMAX-SIM` 0.862 → 0.838 (AVL re-run at the A3 CG 0.0512 m and stall Re at 12.3 m/s); `b1sim.avl.xnp_m` 0.0708 → 0.0711. | `review/DESIGN-ROUND-2026-11-14/B1-W2.md` |
| CR-B1-25 | E1, D3, C4 (via A1) | R-MISSION savings at 17 m/s: 11×5.5E/EP props (E1) and a 55 mm fin TE bevel to 1 mm (C4 stiffness first): −11 % pessimistic cruise power together. Neither closes E2's corrected count alone. | B1.md §1.5–1.6 |

## Open (simulation round, 2026-11-10)

Evidence: `team/B1/SIMULATION-REPORT.md`, `team/B1/claims.verify.json` (`python -I redesign/team/B1/sim_verify.py`).
As-designed mass 2.436 kg (A3 predicted) unless marked. No B1 requirement fails; these rows protect thin margins.

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B1-20 | A1, E2 (copy E1, F4) | Replace the rev 3 cruise values (CR-B1-19) with the as-designed ones: `CL-B1V-CRUISE-P` **235.2 W** (pessimistic 312.4 W, 238.9 W at 2.6 kg), current 15.9 A, `CL-B1V-CD0` **0.0579**, `CL-B1V-K` 0.0957, cruise L/D 5.57, L/D max 6.72, `CL-B1V-TRANS-ENERGY` 0.83 Wh, hover 355 W at 2.436 kg (392 W at 2.6 kg, 7° cant). Cruise time 16.2 min (11.9 pessimistic). E2 re-runs `CALC-E2-BUDGET-*` | SU2 2-D RANS puts the fins and tubes at 1.23 × the hand drag (square board edges, blunt base, proud tube; GCI 5.8 %); CD0 +12.5 %. The lower A3 mass offsets most of it |
| CR-B1-21 | F4, C1 (copy A1) | Keep THR_MAX at 70 % in fixed-wing modes (`CL-F4-FW-RPM-CAP` 7 749 rpm); do not raise it without C1 re-running VD. Treat THR_MAX as a loads limit in the parameter file comments | As designed, VH is **21.0 m/s** at the cap, so 1.25 VH = 26.3 m/s against VD 27.2 m/s (+3.4 %). Without the cap (9 350 rpm VTOL limit) VH is 25.4 m/s and VD would have to be 31.8 m/s. This closes CR-B1-17 |
| CR-B1-22 | A3, A1 | Hold the 2.6 kg gate as the hard stall limit: at CLmax 0.787 (B2, SM 0.063) Vs reaches 12.0 m/s at **2.605 kg**. Any mass growth past 2.6 kg, or a CG move forward of 0.0536 m (larger SM, lower trimmed CLmax), fails R-STALL | `CL-B1V-VS-GATE` 11.99 m/s against 12.0 (+0.1 %); at 2.436 kg it is 11.60 m/s (+3.3 %) |
| CR-B1-23 | B2 (copy B3) | Reconcile trimmed CLmax: B1's AVL + XFOIL critical-section run at the A3 CG gives **0.862** (trim elevon −8.2°), B2's table gives 0.787 at SM 0.063. B1 uses the lower value. If B2 confirms the higher value, Vs at 2.6 kg falls to 11.45 m/s | A 9 % CLmax difference is the whole stall margin at the gate. The NP also differs: 0.0708 m (B1 AVL, wing + fins, props off, no pod) against 0.0738 m (B2, same scope); a 3 mm NP shift is 0.9 % SM |

## Open (rev 3)

| # | To | What | Why / numbers |
|---|---|---|---|
| CR-B1-18 | C4, D3 | Give the four fin braces a rounded or elliptical section (10 × 3 mm strip with a radiused leading and trailing edge, Cd about 0.4), or fair them. | At Cd 0.80 the braces are 0.23 N (0.26 N with interference), the top of C4's 0.07–0.24 N range, and 6 % of cruise drag. Rounding them saves about 0.13 N, or 7 W and 0.5 min of cruise |
| CR-B1-12 | F4 | Rev 3 values: `AIRSPEED_CRUISE` 16, `AIRSPEED_MIN` 15.6 (D-36), `AIRSPEED_MAX` 18, `Q_ASSIST_SPEED` 13, **`Q_TAILSIT_RAT_FW` 12 °/s** (unchanged), `TECS_CLMB_MAX` 3 m/s, the fixed-wing rpm cap from CR-B1-17 (b). After the cold-pack stand run confirms a sag of at least 0.76, you may raise the rate to 15 °/s. Run the SITL pitch-over at 12 and 16 °/s on a sagged-pack battery model and log thrust saturation. | At sag 0.76 (D-35) the peak thrust fraction is 0.70 at 12 °/s, 0.77 at 15, 0.79 at 16 and 0.88 at 20. FW climb is 13.7 m/s at 80 % thrust (motor model) |
| CR-B1-14 | C5, H3 | Splay the feet, or otherwise raise the narrow-axis tip-over angle. Flight card: fin-tip landings only in steady wind ≤ 5 m/s; lay the aircraft flat when gusts exceed 8 m/s. | At a tip-over angle of 30.6° the landing wind limit is 5.8 m/s (+15 %). The parked tip-over wind is 8.9 m/s at 2.32 kg (+11 %) |
| CR-B1-15 | B2, B3 | Re-run the AVL polar with the pod (0.21 × 0.14 × 0.07) and the props, and publish `cd0_wing`, `e_oswald`, `cla_per_rad` and a **trimmed** CL(α) as params keys. | B1 uses `P:b2.avl.*` from the props-off run without the pod. The pod and brace drag are B1 hand estimates |
| CR-B1-16 | H1 | Thrust-stand points for the 11×5.5MR: static at 690 gf (calibration `CL-B1-KCAL` 1.13); full throttle at 14.0 V and at 13.6 V with the 100 A limiter (`CL-B1-NMAX-SAG` 120.1 rev/s); the A/B hover ratio against the 11×4.5MR (1.019). If the stand can run in an air stream (car top), add rpm at full throttle at 16 m/s (model: 8 530 rpm, limiter-bound). | Hover throttle 0.56 against the 0.60 limit and T/W 1.79 rest on sag 0.76 and 1.62 kg. The forward-flight full-throttle rpm drives VH and the FW climb |

## Closed

| # | To | Closed by |
|---|---|---|
| CR-B1-17 | C1, F4 | answered by F4's THR_MAX 70 % cap (`CL-F4-FW-RPM-CAP`); as-designed VH 21.0 m/s, follow-up in CR-B1-21 |
| CR-B1-19 | A1, E2 | superseded by CR-B1-20 (as-designed values) |
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
