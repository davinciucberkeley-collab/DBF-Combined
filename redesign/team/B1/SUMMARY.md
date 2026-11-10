# B1 aero performance — K09-L

Status: `MODELLED` (B1, rev 3, 2026-11-09, answers CR-A1-30). Inputs: c 0.32, S5010 polar and trimmed CLmax 0.80
(B2), 11×5.5MR PER3 (B4), E1 motor constants, sag 0.76 (D-35), pod 0.21 × 0.14 × 0.07 m (D-25), braces and
collars (D3 CR-D3-15), rpm cap 9 350 (D-29). Claim ids unchanged. Re-check:
`python -I redesign/team/B1/performance.py`, then `python -I redesign/proofs/build_graph.py`.

**Verdict.** The pod, braces and collars add 0.5 N of drag. Cruise at 16 m/s now takes **228 W** (301 W
pessimistic), which leaves **16.3 min** of cruise after the 2 min hover (12.0 min pessimistic) against 5 min. At sag
0.76 the hover thrust fraction is 0.56, and the 12 °/s pitch-over peaks at 0.70, so the rate stays at 12 °/s.
**The top level speed at the rpm cap is 25.7 m/s, not 21.8 m/s.** C1's VD therefore rises to 32.1 m/s, unless F4
caps fixed-wing rpm near 7 950 (CR-B1-17).

## Files

| File | What |
|---|---|
| `performance.py` | model and claims (stdlib only): aero, prop/motor chain, motor-limited full throttle, hover, corridor, pitch-over, cruise sweep, mission, wind, climb |
| `PERFORMANCE.md` | report: rev 2 → 3 changes, inputs, tables, FIG B1-01 corridor, FIG B1-02 cruise time vs speed, F4 values |
| `claims.json` · `performance_results.json` | 54 claims, 11 calcs, 16 assumptions, 5 sources, 3 planned tests · tables, sensitivities, time history |
| `fig-b1-corridor.svg` · `fig-b1-endurance.svg` | figures, design-system colours |
| `CHANGE-REQUESTS.md` | open CR-B1-12, 14 … 19; CR-B1-01 … 11, 13 closed |

## Key numbers (2.6 kg, 16 m/s unless marked)

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Vs / 1.3 Vs | 11.91 / 15.48 | m/s | `CL-B1-VS-GATE` (≤ 12), `CL-B1-VT-GATE` (≤ 16) | `UNVERIFIED` |
| CD0 / k (pess.) / L/D | 0.0513 / 0.0943 (0.1107) / 6.34 | — | `CL-B1-CD0`, `CL-B1-K`, `-K-PESS`, `CL-B1-CRUISE-LD` | `UNVERIFIED` |
| Pod widening / braces + collars | +0.14 / +0.37 | N | `CALC-B1-AERO` (`ASM-B1-POD-FRONT`, `ASM-B1-DRAG-ADDONS`) | `MODELLED` |
| **Cruise power (pessimistic), current** | **228 (301), 15.4** | W, A | `CL-B1-CRUISE-P`, `-P-PESS`, `-I` | `UNVERIFIED` |
| Hover power: mission (E1) / B1 cross-check | 400 / 387 | W | `P:performance.hover_power_w`, `CL-B1-HOVER-P-GATE` (≤ 400) | `UNVERIFIED` |
| Hover thrust fraction / T/W, sag 0.76, with download | 0.56 / 1.79 | — | `CL-B1-HOVER-THROTTLE` (≤ 0.60), `CL-B1-HOVER-TW-SAG` (≥ 1.6) | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic)** | **16.3 (12.0)** | min | `CL-B1-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Pitch-over at 12 °/s: to 1.3 Vs, peak thrust fraction (16 °/s ceiling) | 7.8 s, 0.70 (0.79) | s, — | `CL-B1-TRANS-TIME`, `CL-B1-TRANS-THRUST` (≤ 0.80) | `UNVERIFIED` |
| Steady transition peak thrust fraction / power | 0.56 / 387 | —, W | `CL-B1-CORR-THRUST`, `CL-B1-CORR-P-PEAK` | `UNVERIFIED` |
| Landing wind limit / parked tip-over wind (2.32 kg) | 5.8 / 8.9 | m/s | `CL-B1-WIND-HOVER-MAX` (≥ 5), `CL-B1-GROUND-TIP-WIND` (≥ 8) | `UNVERIFIED` |
| **Top level speed at 9 350 rpm (C1's VH)** / worst pack / cap failed | **25.7** / 25.7 / 34.5 | m/s | `CL-B1-VMAX` (≥ 18), `-VMAX-SAG`, `-VMAX-NOCAP` | `UNVERIFIED` |
| FW climb at 16 m/s, 80 % thrust | 13.7 | m/s | `CL-B1-ROC-FW` | `UNVERIFIED` |

Every claim is `UNVERIFIED`, because each rests on inputs no one has checked yet: B2's AVL run, E1's Rm, the sag
and the tip-over angle. None has a negative margin.

## Handed over

| To | What | Where |
|---|---|---|
| C1, F4 | VH 25.7 m/s → VD 32.1 m/s, or a fixed-wing rpm cap of about 7 950 rpm | CR-B1-17 |
| A1, E2, E1 | rev 3 cruise: 227.8 / 300.6 W, L/D 6.34, CD0 0.0513, 0.88 Wh per transition | CR-B1-19 |
| C4, D3 | rounded brace section, −0.13 N | CR-B1-18 |
| F4 | 12 °/s kept (16 °/s ceiling at sag 0.76); `AIRSPEED_MIN` 15.6 | CR-B1-12 |

## Open issues

| Issue | Closes with | Owner |
|---|---|---|
| VH above the 21.8 m/s proxy that sets VD | C1 loads re-run, or F4 fixed-wing rpm cap | C1, F4 (CR-B1-17) |
| Sag 0.76 (E2) vs 0.854 (E1) sets the hover throttle and pitch-over rate | cold-pack stand run | H1, E1, E2 (CR-B1-16) |
| Pod, brace and collar drag are hand estimates | AVL with the pod; `T-B1-CRUISE-POWER` legs at 14, 16 and 18 m/s | B2, B3, H2 (CR-B1-15) |
| Top speed rests on APC's Ct near zero thrust | full-throttle rpm in an air stream | H1 (CR-B1-16) |
| Tip-over angle of 30.6° sets the wind limits | splayed feet | C5 (CR-B1-14) |
