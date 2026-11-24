# B1 aero performance: K09-L

> **Wave 2 (2026-11-14, D-145 / D-146).** The scripts now read `performance.cruise_ms` (17 m/s) and
> `propulsion.stations.cant_deg` (9°, thrust per prop = D / (n cos 9°)), and the cruise sweep runs 10–22 m/s.
> AVL + XFOIL were re-run at 17 m/s and the current A3 mass and CG; SU2 fin drag is still the 16 m/s run (Re +6 %,
> effect on cd < 1 % `EST`). Current: cruise at 17 m/s **275.9 W** (365.1 W pessimistic) at 2.502 kg, **278.2 W**
> (368.2 W) at 2.6 kg, CD0 0.0577, L/D 5.20. Before/after: `review/DESIGN-ROUND-2026-11-14/B1-W2.md`.
>
> **Design round 2026-11-14 (wave 1).** Values below were refreshed to the current claims after D-118 (Oswald e 0.85 base,
> k 0.1042) and A3's 2.502 kg predicted mass. R-MISSION (E2's 17 m/s pessimistic `BATT_LOW` time) and R-TRANSITION
> (the stale 15.6 m/s key) now fail; the speed-side analysis and params edits are in
> `review/DESIGN-ROUND-2026-11-14/B1.md` (scripts in `round-2026-11-14/`).

Status: `MODELLED` (B1, simulation round, 2026-11-10; values refreshed 2026-11-14). This round re-runs the rev 3 model on the as-designed
geometry and A3 masses, with AVL + XFOIL for the wing and SU2 2-D RANS for the fins. Rev 3 claim ids (`CL-B1-*`,
`claims.json`) are unchanged, and the as-designed claims are `CL-B1V-*` (`claims.verify.json`). Re-check:
`python -I redesign/team/B1/sim_verify.py`, then `python -I redesign/proofs/build_graph.py`.

**Verdict (2026-11-10 run).** The as-designed aircraft met every B1 requirement at 16 m/s. The fins carry 1.23 × the hand-estimated drag,
because of their square board edges, blunt base and proud motor tubes, so **CD0 rises from 0.0516 to 0.0580**. At
the A3 predicted mass (2.502 kg) and e 0.85, cruise at 16 m/s takes **239.3 W** (241.8 W at 2.6 kg; 277.1 W at 17 m/s),
which leaves **15.8 min** of level cruise after the 2 min hover (11.7 min pessimistic) on B1's simple budget; E2's
mission budget to `BATT_LOW` is the binding claim. Three margins are thin:

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

## Key numbers (as designed, 2.502 kg, 17 m/s, 9° cant unless marked; claims of 2026-11-14 wave 2)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| CD0 / k (e 0.85) / L/D max (rev 3 hand: 0.0517 / 0.1042 / 6.81); AVL/XFOIL k 0.0977 | 0.0577 / 0.1042 / 6.45 | — | `CL-B1V-CD0`, `-K`, `-LDMAX` | `UNVERIFIED` |
| SU2 fine-grid GCI, largest of 3 sections (fin A, L2–L4) | 5.8 | % | `CL-B1V-GCI-MAX` (≤ 10) | `UNVERIFIED` |
| Vs at 2.6 kg / 2.502 kg | 12.02 / 11.79 | m/s | `CL-B1V-VS-GATE`, `-VS-PRED` (≤ 12.3) | `UNVERIFIED` |
| 1.3 Vs at 2.6 kg (A3 CG; B2 forward CG 15.70, tripped 16.82) | 15.62 | m/s | `CL-B1V-VT-GATE` (≤ `cruise_ms` 17) | `UNVERIFIED` |
| Hover power / thrust fraction (sag 0.76) / T/W sagged (9° cant) | 372 / 0.49 / 2.05 | W, —, — | `CL-B1V-HOVER-P`, `-THROTTLE` (≤ 0.60), `-TW-SAG` (≥ 1.6) | `UNVERIFIED` |
| **Cruise power (pessimistic), current** | **275.9 (365.1), 18.6** | W, A | `CL-B1V-CRUISE-P`, `-P-PESS`, `-I` |
| **Cruise power at 2.6 kg (pessimistic), pessimistic current** (for E2) | **278.2 (368.2), 24.9** | W, A | `CL-B1V-CRUISE-P-GATE`, `-P-GATE-PESS`, `-I-GATE-PESS` | `UNVERIFIED` |
| **Cruise after 2 min hover (pessimistic), B1 simple budget; E2's `BATT_LOW` count binds** | **13.6 (10.1)** | min | `CL-B1V-CRUISE-TIME`, `-TIME-PESS` (≥ 5) | `UNVERIFIED` |
| Pitch-over 12 °/s: peak thrust fraction / time / energy | 0.55 / 6.8 / 0.92 | —, s, Wh | `CL-B1V-TRANS-THRUST` (≤ 0.80), `-TIME`, `-ENERGY` | `UNVERIFIED` |
| Corridor peak steady thrust fraction / wing flying from | 0.47 / 12 | —, m/s | `CL-B1V-CORR-THRUST` | `UNVERIFIED` |
| **VH at THR_MAX 70 %** / 1.25 VH over VD 27.2 | **21.0** / 0.967 | m/s, — | `CL-B1V-VH-FW`, `-VH-RATIO` (≤ 1) | `UNVERIFIED` |
| FW climb, 17 m/s, worst pack | 10.0 | m/s | `CL-B1V-ROC-FW` (≥ 3) | `UNVERIFIED` |
| Landing wind / parked tip-over wind (A3 basic − 47 g) | 5.43 / 8.94 | m/s | `CL-B1V-WIND-HOVER-MAX` (≥ 5), `-GROUND-TIP-WIND` (≥ 8) | `UNVERIFIED` |

Every claim stays `UNVERIFIED` until the A3 weigh-in, the H1 stand points and the cruise-power legs close it. No
claim has a negative margin.

## Handed over

| To | What | Where |
|---|---|---|
| A1, E2, E1, F4 | as-designed cruise 235 / 312 W, CD0 0.0579, L/D 5.57, 0.83 Wh per transition (superseded by CR-B1-24) | CR-B1-20 |
| F4, C1 | keep THR_MAX 70 %: VH 21.0 m/s, 1.25 VH 26.3 against VD 27.2 m/s | CR-B1-21 |
| A3, A1 | 2.6 kg is the hard stall limit (12.0 m/s at 2.605 kg) | CR-B1-22 |
| B2, B3 | CLmax 0.862 (B1) against 0.787 (B2) at the A3 CG; NP 0.0708 against 0.0738 m | CR-B1-23 |

## Open issues

| Issue | Closes with | Owner |
|---|---|---|
| Stall margin at the gate is +0.1 % | weigh-in at or below 2.6 kg; T-B2-STALL | A3, B2 (CR-B1-22, 23) |
| VH ≤ VD holds only with the THR_MAX cap | F4 parameter lock; first full-throttle level log | F4, H2 (CR-B1-21) |
| Fin drag comes from 2-D sections × 1.15 | cruise-power legs at 15, 17 and 19 m/s | H2 (T-B1-CRUISE-POWER) |
| The tip-over angle of 30.6° sets the landing wind (+8 %) | splayed feet | C5 (CR-B1-14) |
| Sag, Rm and the APC tables set hover and VH | stand points | H1 (CR-B1-16) |
