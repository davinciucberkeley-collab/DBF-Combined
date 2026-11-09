# B1 aero performance — K09-L

Status: `MODELLED` (B1, rev 2, 2026-11-09, answers CR-A1-13). Inputs: c 0.32, S5010 polar and trimmed CLmax 0.80
(B2), 11×5.5MR PER3 (B4), E1 motor constants, sag 0.72, hover 400 W. Re-check:
`python -I redesign/team/B1/performance.py`, then `python -I redesign/proofs/build_graph.py`. On 2026-11-09 B1 had
no drift and no failing claim. The build still fails on A5, B2, E1 and E2 drift. E2's drift is B1's new cruise
power, which E2 asked for in CR-E2-08.

**Verdict.** Cruise at 16 m/s takes **218 W** (285 W pessimistic). That leaves **17.0 min** of cruise after the 2 min
hover (12.7 min pessimistic), against a 5 min requirement. The transition gate passes by **0.58 m/s** (1.3 Vs = 15.42
m/s), which is tighter than A2's 1.0 m/s airspeed-error allowance. With the worst-case pack (sag 0.72), the pitch-over
rate has to drop to **12 °/s**. Landing wind is limited to **5.8 m/s** by the 30.6° tip-over angle.

## Files

| File | What |
|---|---|
| `performance.py` | model and claims (stdlib only): aero, prop/motor chain, hover, corridor, pitch-over simulation, cruise sweep, mission, wind, climb |
| `PERFORMANCE.md` | report: inputs, tables, FIG B1-01 corridor, FIG B1-02 cruise time vs speed, F4 values |
| `claims.json` · `performance_results.json` | 52 claims, 11 calcs, 13 assumptions, 5 sources, 3 planned tests · tables, sensitivities, time history |
| `fig-b1-corridor.svg` · `fig-b1-endurance.svg` | figures, design-system colours |
| `CHANGE-REQUESTS.md` | open CR-B1-10 … 16 to A1, E2/E1, F4, A2/F3, C5/H3, B2/B3, H1; CR-B1-01 … 09 closed |

## Key numbers (2.6 kg, 16 m/s unless marked)

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Vs / 1.3 Vs (CLmax 0.804) | 11.86 / 15.42 | m/s | `CL-B1-VS-GATE` (≤ 12), `CL-B1-VT-GATE` (≤ 16) | `UNVERIFIED` |
| CD0 / k (pess.) / L/D | 0.0452 / 0.0950 (0.1107) / 6.93 | — | `CL-B1-CD0`, `CL-B1-K`, `CL-B1-K-PESS`, `CL-B1-CRUISE-LD` | `UNVERIFIED` |
| Cruise drag / η_prop / J / drive η | 3.75 N / 0.43 / 0.58 / 0.66 | — | `CL-B1-CRUISE-DRAG`, `-ETA-PROP`, `-J`, `-ETA-DRIVE` | `UNVERIFIED` |
| **Cruise power (pessimistic), current** | **218 (285), 14.7** | W, A | `CL-B1-CRUISE-P`, `-P-PESS`, `-I` | `UNVERIFIED` |
| Hover power: mission (E1) / B1 cross-check | 400 / 387 | W | `P:performance.hover_power_w`, `CL-B1-HOVER-P-GATE` (≤ 400) | `UNVERIFIED` |
| Hover thrust fraction / T/W, sagged, with download | 0.59 / 1.69 | — | `CL-B1-HOVER-THROTTLE` (≤ 0.60), `CL-B1-HOVER-TW-SAG` (≥ 1.6) | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic)** | **17.0 (12.7)** | min | `CL-B1-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Pitch-over at 12 °/s: to 1.3 Vs, peak thrust fraction | 7.7 s, 0.76 | s, — | `CL-B1-TRANS-TIME`, `CL-B1-TRANS-THRUST` (≤ 0.80) | `UNVERIFIED` |
| Steady transition peak thrust fraction / power | 0.59 / 387 | —, W | `CL-B1-CORR-THRUST`, `CL-B1-CORR-P-PEAK` | `UNVERIFIED` |
| Hover lean 5 / 8 m/s | 15.8 / 35.9 | ° | `CL-B1-LEAN-5MS` (≤ 20.6) | `UNVERIFIED` |
| Landing wind limit / parked tip-over wind (2.15 kg) | 5.8 / 8.2 | m/s | `CL-B1-WIND-HOVER-MAX` (≥ 5), `CL-B1-GROUND-TIP-WIND` (≥ 8) | `UNVERIFIED` |
| FW climb (80 % thrust) / top speed, worst pack | 4.7 / 19.3 | m/s | `CL-B1-ROC-FW`, `CL-B1-VMAX` (≥ 18) | `UNVERIFIED` |

Every claim is `UNVERIFIED` because it rests on unchecked inputs from other roles (B2 AVL source, E1 Rm, A1
tip-over) or on B1's own drag and ESC assumptions. None has a negative margin.

## Handed over

| To | What | Where |
|---|---|---|
| E2 (CR-E2-08), E1 (CR-E1-05) | cruise model: CD0, k, trim, η_prop, drive η, 218/285 W, 0.87 Wh per transition | CR-B1-11 |
| F4 | `AIRSPEED_CRUISE` 16, `_MIN` 15, `_MAX` 18, `Q_ASSIST_SPEED` 13, `Q_TAILSIT_RAT_FW` 12, `TECS_CLMB_MAX` 3, transition end ≥ 15.5 m/s | CR-B1-12, PERFORMANCE.md |
| A1 | params `performance.*` update | CR-B1-10 |

## Open issues

| Issue | Closes with | Owner |
|---|---|---|
| Transition margin 0.58 m/s vs airspeed error 1.0 m/s | tighten to 0.5 m/s, or cruise 16.5 m/s | A2, F3, A1 (CR-B1-13) |
| Hover throttle 0.59 vs 0.60 rests on sag 0.72 and 1.62 kg | thrust stand on a cold, low pack | H1, E2 (CR-B1-16) |
| Polar, CLa and trimmed CL(α) are from the c 0.30 run | AVL at R1 | B2, B3 (CR-B1-15) |
| Tape-seam factor 1.10, non-wing drag build-up | `T-B1-CRUISE-POWER` legs at 14/16/18 m/s | H2 |
| Tip-over 30.6° sets the wind limits | splayed feet | C5 (CR-B1-14) |
