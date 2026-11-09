# A4 configuration / interface manager — interface plan for K09-L

Status: `PROPOSED` plan, `CHECKED` against its own graph rules (2026-11-09). No subsystem has declared an
`interfaces.json` yet, so the real graph is empty and every planned edge is open.

## What was produced

| File | What | Status |
|---|---|---|
| `team/A4/INTERFACE-PLAN.md` | rules, per-method data blocks, N² matrix, reserved part ids, register of 125 interfaces (owner, acknowledgers, designer · sizer, data to carry), acknowledgements owed, data interfaces, keep-outs, 11 open issues, queued tooling changes | `PROPOSED` |
| `team/A4/interface_plan.py` | the plan as code; checks it with `merge_check.py` plus load-path and power-path rules; renders the register; `--compare` checks the real graph against the plan | `CHECKED` |
| `team/A4/interface_plan.json` · `PLAN-STATUS.md` | generated machine copy · generated comparison (125 edges open) | — |
| `team/A4/test_interface_plan.py` | 6 cases (clean baseline + 5 seeded faults), all caught | `CHECKED` |
| `team/A4/claims.json` | 4 claims in the proof chain | `CHECKED` |
| `team/A4/CHANGE-REQUESTS.md` | 14 requests to A1, A2, A5, B3, B4, C4, C5, C6, D1, D2, D3, D5, D6, E1, E3, F1–F5 | open |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Parts reserved (flight) | 82 (77) | — | `CALC-A4-PLAN-GRAPH` | `CHECKED` |
| Interfaces planned (cross-subsystem) | 125 (78) | — | `CL-A4-PLAN-EDGES` | `CHECKED` |
| By kind: mechanical · electrical · kinematic · thermal | 90 · 23 · 8 · 4 | — | register | `PROPOSED` |
| Fastened · clamped · bonded joints | 19 · 8 · 33 | — | register | `PROPOSED` |
| Flight parts on a load path | 100 | % | `CL-A4-PLAN-CONNECTED` (≥ 100 %) | `CHECKED` |
| Electrical parts powered through power wires | 100 | % | `CL-A4-PLAN-POWERED` (≥ 100 %) | `CHECKED` |
| Field disconnects | 1 (pack plug `E-HRN-10`) | — | `CL-A4-FIELD-DISCONNECTS` ≤ `P:electrical.field_disconnects` → `R-TRANSPORT` | `CHECKED` |
| Schema data blocks owed (joint stacks 19, wire 23) | 42 | — | `interface_plan.py` | open |
| Masses owed | 77 | parts | `interface_plan.py` | open |

## Decisions in the plan

| Decision | Why |
|---|---|
| Harness declares all 23 wires end to end; harness mass sits in 3 lumped bundles tied to structure | the wire is the installation (advisor lesson 3); the README gives harness every wire |
| Elevon hinge declared by wing, designed by D6 | merge_check requires the owner to hold a side (CR-A4-01) |
| Ties, tape channels, labels and pitot tubing are not load paths | `merge_check` counts them as structure: a fin held only by its harness ties passes there |
| Power reach follows power wires supply → load, signal leads excluded | `merge_check` accepts an ESC reached through its signal lead or a PDB fed backwards through the FC |
| ESCs on fin pads next to each motor; thermal edge motor → printed mount | prop-wash cooling (E3); PETG mount softening is the real thermal interface |

## Open issues (top five; all eleven in the plan)

1. Wing TE sits 10 mm above the ground plane in stance (foot height); a crushed foot grounds the TE (OI-05, CR-A4-02).
2. Fin-through-wing and fin-tube junction undecided; part ids may split (OI-01, P25).
3. 0.18 m tube-to-spar offset and spar access cut-out (OI-02).
4. Elevon link crosses the fin at the hinge line (OI-03).
5. Airspeed sensor and board barometer may share I2C 0x76 (OI-08, `UNVERIFIED`).

`redesign/interfaces/` was not edited (not assigned in this step); the six queued changes are listed in the plan.

## How to verify

| Check | Command (repo root) | Result 2026-11-09 |
|---|---|---|
| Plan | `python -I redesign/team/A4/interface_plan.py` | `PASS`: 0 plan errors |
| Self-test | `python -I redesign/team/A4/test_interface_plan.py` | `PASS` 6/6 |
| Real graph vs plan | `python -I redesign/team/A4/interface_plan.py --compare` | 0 sources, 125 edges open |
| Proof chain | `python -I redesign/proofs/build_graph.py` | OK, no drift; A4 claims `CHECKED` |
