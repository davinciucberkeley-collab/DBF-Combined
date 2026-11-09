# B1 aero performance — K09-L

Status: `PROPOSED` (B1, 2026-11-09). First-order analysis; B2/B3/B4 data not yet available. Re-check:
`python -I redesign/team/B1/performance.py` then `python -I redesign/proofs/build_graph.py`
(2026-11-09: OK, 617 nodes, no drift; no B1 claim fails).

**Verdict.** Raise cruise to **16 m/s** to close the transition gate (+6 % over 1.3 Vs at 2.6 kg). Cruise power
is **307 W, not 194 W**: the 11×4.5MR runs at η 0.37 at J 0.49. That leaves 12.3 min of cruise after the 2 min
hover (9.3 min pessimistic). This passes the 5 min requirement. Hover, transition and the 5 m/s wind card pass.

## Files

| File | What |
|---|---|
| `performance.py` | model and claims (stdlib only): aero, prop/motor chain, hover, corridor, pitch-over simulation, cruise sweep, mission, wind, climb |
| `PERFORMANCE.md` | the report: assumptions, tables, FIG B1-01 corridor, FIG B1-02 cruise time vs speed |
| `claims.json` · `performance_results.json` | 43 claims, 11 calcs, 13 assumptions, 4 sources, 3 planned tests · tables and time histories |
| `fig-b1-corridor.svg` · `fig-b1-endurance.svg` | figures, design-system colours |
| `CHANGE-REQUESTS.md` | 9 requests to A1, B2, B3, B4, E1, F1, F4, H2 |

## Key numbers (2.6 kg gate unless marked)

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Stall / 1.3 Vs (CLmax 0.9) | 11.58 / 15.05 | m/s | `CL-B1-VS-GATE`, `CL-B1-VT-GATE` | `UNVERIFIED` |
| Proposed cruise | 16 | m/s | `ASM-B1-VCRUISE` | `PROPOSED` |
| CD0 / k / L/D at 16 m/s | 0.061 / 0.104 / 5.6 | — | `CL-B1-CD0`, `CL-B1-K`, `CL-B1-CRUISE-LD` | `PROPOSED` |
| Hover power, current (2.48 kg) | 380 W, 25.7 A (355 W, 24.0 A) | W, A | `CL-B1-HOVER-P-GATE`, `CL-B1-HOVER-I-GATE` | `UNVERIFIED` |
| Hover thrust fraction / T/W with sag and download | 0.47 / 2.13 | — | `CL-B1-HOVER-THROTTLE`, `CL-B1-HOVER-TW-SAG` | `UNVERIFIED` |
| Cruise power (pessimistic), current | 307 (397), 20.7 | W, A | `CL-B1-CRUISE-P`, `-P-PESS`, `-I` | `UNVERIFIED` |
| Prop η / J in cruise | 0.37 / 0.49 | — | `CL-B1-CRUISE-ETA-PROP`, `CL-B1-CRUISE-J` | `PROPOSED` |
| Cruise after 2 min hover (pessimistic) | 12.3 (9.3) | min | `CL-B1-CRUISE-TIME` (≥ 5) | `UNVERIFIED` |
| Transition: peak steady thrust fraction / power | 0.47 / 382 | —, W | `CL-B1-CORR-THRUST`, `CL-B1-CORR-P-PEAK` | `PROPOSED` |
| Wing carries level flight unstalled from | 12 | m/s | `CL-B1-V-WINGBORNE` | `UNVERIFIED` |
| Pitch-over at 20 °/s: to 1.3 Vs, peak thrust fraction | 5.0 s, 0.77 | s, — | `CL-B1-TRANS-TIME`, `CL-B1-TRANS-THRUST` (≤ 0.80) | `PROPOSED` |
| Hover lean 5 / 8 m/s | 14.9 / 34.2 | ° | `CL-B1-LEAN-5MS` (≤ 27.2) | `PROPOSED` |
| Steady wind limit for fin-tip landing | 7.0 | m/s | `CL-B1-WIND-HOVER-MAX` (≥ 5) | `PROPOSED` |
| Wind that tips the parked aircraft (2.13 kg) | 9.6 | m/s | `CL-B1-GROUND-TIP-WIND` (≥ 8) | `PROPOSED` |
| FW climb at 16 m/s / top level speed | 6.3 / 19.7 | m/s | `CL-B1-ROC-FW`, `CL-B1-VMAX` | `PROPOSED` |

## Findings others act on

1. **Transition gate (CR-A1-05) closed by speed, not CLmax.** At 16 m/s the margin is +6 %. Even with CLmax 0.8
   it is still +0.2 %. Going back to 15 m/s needs CLmax ≥ 1.04 with elevon up-trim (B2).
2. **Cruise is expensive.** Power rises 14 % per m/s, because the prop works near its zero-thrust J. Fly the
   slowest speed the transition rule allows. B4 should weigh a higher-pitch prop against hover efficiency.
3. **Pitch-over rate.** At 30 °/s the pitch-over uses 94 % of available thrust, and at 50 °/s it saturates.
   Start at `Q_TAILSIT_RAT_FW` 20 (F4).
4. **The wing is stalled from 0 to 11 m/s** in level transition, with motors carrying it at ≤ 47 % thrust. The
   elevons get no prop wash, so pitch authority there is differential thrust only (B3, B4).
5. **Hover is 380 W / 25.7 A at the gate**, not 355 W / 24 A (that was at 2.43 kg). A 2.5 m/s climb draws
   447 W / 30 A (F1).

## Open issues

| Issue | Closes with | Owner |
|---|---|---|
| CLmax, α₀, post-stall lift of MH 45 with elevon up-trim | XFOIL Re 2.5–3.3 × 10⁵ | B2 |
| Oswald e, lift slope, trim drag with fins and pod | AVL | B3 |
| 11×4.5MR η at J 0.49; APC data is predicted, not measured | thrust stand, car-top test | B4, H1 |
| Motor Rm, I₀; chain calibration 1.18 from an 11×4.7 table | thrust stand | E1, H1 |
| Pack energy 96.2 Wh not measured | discharge test | E2 |
