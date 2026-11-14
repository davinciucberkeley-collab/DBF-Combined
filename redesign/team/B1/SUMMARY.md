# B1 aero performance: K09-L

Status: `MODELLED` (B1, simulation round, 2026-11-10). This round re-runs the rev 3 model on the as-designed
geometry and A3 masses, with AVL + XFOIL for the wing and SU2 2-D RANS for the fins. Rev 3 claim ids (`CL-B1-*`,
`claims.json`) are unchanged, and the as-designed claims are `CL-B1V-*` (`claims.verify.json`). Re-check:
`python -I redesign/team/B1/sim_verify.py`, then `python -I redesign/proofs/build_graph.py`.

**Verdict.** The as-designed aircraft meets every B1 requirement. The fins carry 1.23 × the hand-estimated drag,
because of their square board edges, blunt base and proud motor tubes, so **CD0 rises from 0.0515 to 0.0579**. The
lighter A3 mass (2.436 kg) absorbs most of this: cruise at 16 m/s takes **235 W**, which leaves **16.2 min** of
cruise after the 2 min hover (11.9 min pessimistic) against a 5 min requirement. Three margins are thin:

- stall at the 2.6 kg gate (+0.1 %)
- 1.25 VH ≤ VD (+3.4 %, and only with THR_MAX 70 %)
- the landing wind (+8 %)

The partial results committed in a391d56 (CD0 0.0786, 14.1 min) came from an unconverged fine grid, and this
round replaces them.

## Files

| File | What |
|---|---|
| `SIMULATION-REPORT.md` | this round (SU2 fin A on 4 grids, fin B and S5010 on 3): tool choice, grid convergence, hand vs sim, corridor, sensitivity, margins, FIG B1-03 … B1-07 |
| `cfd_sections.py` · `vlm_xfoil.py` · `sim_to_params.py` · `sim_verify.py` | SU2 fin and wing sections (3 grids each) · AVL (3 lattices) + XFOIL (3 panel counts) · results into `params.json` (`b1sim.*`) · chain re-run and figures |
| `sim/` | SU2 cases (`cfd/<case>_L1-3`), AVL/XFOIL decks and polars, `sim_verify_results.json`, PNG copies of the figures |
| `performance.py` · `PERFORMANCE.md` · `claims.json` | rev 3 model, report and 54 claims (the hand calculation compared against here) |
| `CHANGE-REQUESTS.md` | new CR-B1-20 … 23; CR-B1-17 and 19 closed |

## Key numbers (as designed, 2.436 kg, 16 m/s unless marked)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| CD0 / k / L/D max (rev 3 hand: 0.0515 / 0.0943 / 7.18) | 0.0579 / 0.0957 / 6.72 | — | `CL-B1V-CD0`, `-K`, `-LDMAX` | `UNVERIFIED` |
| SU2 fine-grid GCI, largest of 3 sections (fin A, L2–L4) | 5.8 | % | `CL-B1V-GCI-MAX` (≤ 10) | `UNVERIFIED` |
| Vs at 2.6 kg / 2.436 kg | 11.99 / 11.60 | m/s | `CL-B1V-VS-GATE`, `-VS-PRED` (≤ 12) | `UNVERIFIED` |
| 1.3 Vs at 2.6 kg | 15.58 | m/s | `CL-B1V-VT-GATE` (≤ 16) | `UNVERIFIED` |
| Hover power / thrust fraction (sag 0.76) / T/W sagged | 355 / 0.47 / 2.12 | W, —, — | `CL-B1V-HOVER-P`, `-THROTTLE` (≤ 0.60), `-TW-SAG` (≥ 1.6) | `UNVERIFIED` |
| **Cruise power (pessimistic), current** | **235 (312), 15.9** | W, A | `CL-B1V-CRUISE-P`, `-P-PESS`, `-I` | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic)** | **16.2 (11.9)** | min | `CL-B1V-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Pitch-over 12 °/s: peak thrust fraction / time / energy | 0.52 / 7.3 / 0.83 | —, s, Wh | `CL-B1V-TRANS-THRUST` (≤ 0.80), `-TIME`, `-ENERGY` | `UNVERIFIED` |
| Corridor peak steady thrust fraction / wing flying from | 0.47 / 12 | —, m/s | `CL-B1V-CORR-THRUST` | `UNVERIFIED` |
| **VH at THR_MAX 70 %** / 1.25 VH over VD 27.2 | **21.0** / 0.967 | m/s, — | `CL-B1V-VH-FW`, `-VH-RATIO` (≤ 1) | `UNVERIFIED` |
| FW climb, 16 m/s, worst pack | 12.0 | m/s | `CL-B1V-ROC-FW` (≥ 3) | `UNVERIFIED` |
| Landing wind / parked tip-over wind (2.275 kg) | 5.40 / 8.84 | m/s | `CL-B1V-WIND-HOVER-MAX` (≥ 5), `-GROUND-TIP-WIND` (≥ 8) | `UNVERIFIED` |

Every claim stays `UNVERIFIED` until the A3 weigh-in, the H1 stand points and the cruise-power legs close it. No
claim has a negative margin.

## Handed over

| To | What | Where |
|---|---|---|
| A1, E2, E1, F4 | as-designed cruise 235 / 312 W, CD0 0.0579, L/D 5.57, 0.83 Wh per transition | CR-B1-20 |
| F4, C1 | keep THR_MAX 70 %: VH 21.0 m/s, 1.25 VH 26.3 against VD 27.2 m/s | CR-B1-21 |
| A3, A1 | 2.6 kg is the hard stall limit (12.0 m/s at 2.605 kg) | CR-B1-22 |
| B2, B3 | CLmax 0.862 (B1) against 0.787 (B2) at the A3 CG; NP 0.0708 against 0.0738 m | CR-B1-23 |

## Open issues

| Issue | Closes with | Owner |
|---|---|---|
| Stall margin at the gate is +0.1 % | weigh-in at or below 2.6 kg; T-B2-STALL | A3, B2 (CR-B1-22, 23) |
| VH ≤ VD holds only with the THR_MAX cap | F4 parameter lock; first full-throttle level log | F4, H2 (CR-B1-21) |
| Fin drag comes from 2-D sections × 1.15 | cruise-power legs at 14, 16 and 18 m/s | H2 (T-B1-CRUISE-POWER) |
| The tip-over angle of 30.6° sets the landing wind (+8 %) | splayed feet | C5 (CR-B1-14) |
| Sag, Rm and the APC tables set hover and VH | stand points | H1 (CR-B1-16) |
