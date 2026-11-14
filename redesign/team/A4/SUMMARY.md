# A4 configuration / interface manager: interface plan for K09-L

Status: plan revision **A4-R5** on design frame A1-R4a, `PROPOSED`. Checked against its own graph rules and against
the 11 declared `interfaces.json` files on 2026-11-10 (`CHECKED`). This round re-baselines the pod only (D2-R5a,
CR-D2-20). The other nine subsystems stay at their A4-R4 freeze.

## Action item this round

| Item | Result | Where |
|---|---|---|
| Re-baseline the pod: `POD-009`, `POD-010`, `E-POD-13` missing from the plan; `E-POD-10` and `E-POD-11` deviated | Checked against D2's own record: CR-D2-20, `team/D2/SUMMARY.md` R5a, `subsystems/pod/{parts.csv, interfaces.json}`. The D-47 aft stop moved to the tray, so the spacers bear on `POD-002`. The trim kit was split (CR-A5-27). Accepted as declared | `baseline-R5.json`, `INTERFACE-PLAN.md` "What changed in A4-R5" |
| `E-POD-10` | `POD-008` spacers → `POD-002` aft stop at x 0.060 m (was `POD-007`) | register |
| `E-POD-11` | `POD-009` crush block → `POD-002` forward stop at x −0.1212 m (was `POD-008`) | register |
| `E-POD-13` (new) | `POD-010` spreader → `POD-009`, `CT-SLIDE-STOP`, loose (no bond) | register |
| Tooling | `--rebaseline pod` refreshes only the named subsystems and keeps the rest frozen (`frozen_in`). Two new seeded faults: the crush block or the spreader floats when its edge is cut | `interface_plan.py`, `test_interface_plan.py` |

## Key numbers

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Parts (flight) | 162 (141) | — | `CALC-A4-PLAN-GRAPH` | `CHECKED` |
| Interfaces planned · declared · parked | 252 · 239 · 24 | — | `CL-A4-PLAN-EDGES` | `CHECKED` |
| Flight parts on a load path | 100 | % | `CL-A4-PLAN-CONNECTED` (≥ 100 %) | `CHECKED` |
| Electrical parts powered through power wires | 100 | % | `CL-A4-PLAN-POWERED` (≥ 100 %) | `CHECKED` |
| Field disconnects | 1 (pack plug) | — | `CL-A4-FIELD-DISCONNECTS` ≤ `P:electrical.field_disconnects` | `CHECKED` |
| Part-id rule breaches | 0 | — | `CL-A4-PLAN-ID-RULE` (≤ 0) | `CHECKED` |
| `--compare`: missing · pending · owed · deviations · unplanned | 0 · 0 · 0 · 0 · 0 | — | `PLAN-STATUS.md` | `CHECKED` |

## Checks run (2026-11-10, repo root)

| Command | Result |
|---|---|
| `python -I redesign/team/A4/interface_plan.py --rebaseline pod --compare` | PASS, 0 plan errors. Compare: 11 sources, 0 deviations, 0 unplanned (before: 8 deviations, including `E-POD-10/11`, and 3 unplanned) |
| `python -I redesign/team/A4/test_interface_plan.py` | PASS, 19/19 (2 new pod cases) |
| `python -I redesign/team/A4/test_merge_check_d46.py` | PASS, 11/11 |
| `python -I redesign/interfaces/merge_check.py` | PASS: 0 errors, 2 `mass` warnings (fins, propulsion) |
| `python -I redesign/team/A4/integration_check.py` | merge PASS, compare PASS. `fusion/check.py` FAIL: 4 fin keep-out errors, none from the pod. A3 roll-up STALE: A3 must re-run it. Neither failure comes from this change |
| `python -I redesign/proofs/build_graph.py` | No A4 drift. The build still fails on A5 and B1 drift (new pod size and allocations) |

## Open issues (not pod; owners in `CHANGE-REQUESTS.md` round 4)

1. `fusion/check.py` keep-out errors on `FIN-002-L/R` (D3).
2. Mass: fins are 435 g against a 418 g allocation. The heaviest-pack gate margin is 34 g against a 100 g target (A1, A3).
3. A5 `cad_claims.py` and B1 `performance.py` must be re-run to clear their proof-chain drift.

## Files

`INTERFACE-PLAN.md`, `interface_plan.py`, `interface_plan.json`, `baseline-R5.json` (R3 and R4 kept), `PLAN-STATUS.md`,
`INTEGRATION-CHECK.md`, `integration_check.py`, `test_interface_plan.py`, `test_merge_check_d46.py`, `claims.json`
(5 claims), `CHANGE-REQUESTS.md` (round 5 disposition of CR-D2-20).
