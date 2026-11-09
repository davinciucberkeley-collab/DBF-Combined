# A4 configuration / interface manager — interface plan for K09-L

Status: plan revision **A4-R2** on design frame A1-R2, `PROPOSED`; `CHECKED` against its own graph rules
(2026-11-09). No subsystem has declared an `interfaces.json` yet, so `--compare` shows every planned edge open.
This revision closes CR-A1-18 and, with it, CR-A1-02.

## What changed in A4-R2 (CR-A1-18)

| Item | Done | Where |
|---|---|---|
| D-20 ownership | the elevon hinge is a `wing` edge (D6 designs it); `harness` owns all 23 wires, incl. ESC power leads `E-HRN-13…16`; `power` owns only the boxes; electrical `part_a` = supply side | plan Rules, `interfaces/SCHEMA.md` Edge table |
| Per-unit mass / instance ids (CR-A3-09) | `parts.csv mass_g` per unit; one node per instance `<id>-<UR\|UL\|LR\|LL\|L\|R>`; one suffix family per part number; new `id_rule()` check and claim | plan Rules, SCHEMA Part table, `CL-A4-PLAN-ID-RULE` |
| Frame and 9xx (CR-A5-04) | SCHEMA frame text points to `params.json#frame` and `fusion/DATUMS.md`; `9xx` reserved for `fusion/skeleton/` and enforced | SCHEMA, `id_rule()` |
| Half-fins | `FIN-001-L/R` retired → `FIN-001-UR/UL/LR/LL`; clip sets per half-fin; new edges `E-FIN-33…38` | register |
| Through-core block | `FIN-004-L/R` re-scoped from the R0 saddle; tube, spar and core joints `E-FIN-07…12` bonded | register, OI-02 |
| Other R2 changes | pitot plug-in boom (`CT-PLUG-IN`, `E-TRN-12`), carry point `POD-007` (D-23), hinge x 0.2496 m, feet to x 0.365 m, 11×5.5MR, currents read from `params.json` | register |
| SCHEMA extras | the A4 data blocks, `signal_only`, `field_joint`, a K09-L minimal example (JSON parses) | `interfaces/SCHEMA.md` |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Parts reserved (flight) | 87 (82) | — | `CALC-A4-PLAN-GRAPH` | `CHECKED` |
| Interfaces planned (cross-subsystem) | 133 (81) | — | `CL-A4-PLAN-EDGES` | `CHECKED` |
| By kind: mechanical · electrical · kinematic · thermal | 98 · 23 · 8 · 4 | — | register | `PROPOSED` |
| Fastened · clamped · bonded joints | 19 · 4 · 43 | — | register | `PROPOSED` |
| Flight parts on a load path | 100 | % | `CL-A4-PLAN-CONNECTED` (≥ 100 %) | `CHECKED` |
| Electrical parts powered through power wires | 100 | % | `CL-A4-PLAN-POWERED` (≥ 100 %) | `CHECKED` |
| Part-id rule breaches | 0 | — | `CL-A4-PLAN-ID-RULE` (≤ 0) | `CHECKED` |
| Field disconnects (field joints) | 1 (7: pack plug, pack strap, 4 prop nuts, pitot boom) | — | `CL-A4-FIELD-DISCONNECTS` ≤ `P:electrical.field_disconnects` → `R-TRANSPORT` | `CHECKED` |
| Schema data blocks owed (joint stacks 19, wire 23) | 42 | — | `interface_plan.py` | open |
| Masses owed | 82 | parts | `interface_plan.py` | open |

## Open issues (top five; all ten in the plan)

1. `merge_check.py` still warns `owner` on the 23 harness wires (D-20), so `--strict` cannot pass; the fix is shared tooling, waiting on A1 (CR-A4-15).
2. Half-fin-to-tube clip and the tube's 80–330 Hz mode (OI-01, P25); through-core block design (OI-02).
3. Inter-panel link slot in the lower half-fin (OI-03).
4. Feet leave 5 mm of TE clearance after a full 40 mm crush; grass grounds the TE (OI-05, `UNVERIFIED`).
5. Plug-in pitot boom needs a pneumatic break at the socket (OI-12, new).

## Files

| File | What | Status |
|---|---|---|
| `INTERFACE-PLAN.md` | rules, data blocks, N² matrix, reserved and retired ids, register of 133 interfaces, acknowledgements, keep-outs, open issues, tooling status | `PROPOSED` |
| `interface_plan.py` · `interface_plan.json` · `PLAN-STATUS.md` | plan as code and its checks · generated copy · generated comparison | `CHECKED` |
| `test_interface_plan.py` | 10 cases: clean baseline + 9 seeded faults (load path, floating half-fin, power path ×2, pack float, field disconnect, 3 id-rule faults) | `CHECKED` |
| `claims.json` | 5 claims | `CHECKED` |
| `CHANGE-REQUESTS.md` | round 1 dispositions; round 2 CR-A4-15 … 21 to A1, B4, A3, D3, D2/F3, C6/C4, D7 | open |
| `redesign/interfaces/SCHEMA.md` | edited (assigned by CR-A1-18) | `PROPOSED` |

## How to verify

| Check | Command (repo root) | Result 2026-11-09 |
|---|---|---|
| Plan | `python -I redesign/team/A4/interface_plan.py` | `PASS`: 0 plan errors, 0 id-rule breaches |
| Self-test | `python -I redesign/team/A4/test_interface_plan.py` | `PASS` 10/10 |
| Real graph vs plan | `python -I redesign/team/A4/interface_plan.py --compare` | 0 sources, 133 edges open |
| Proof chain | `python -I redesign/proofs/build_graph.py` | A4 claims `CHECKED`, no A4 drift; the build still fails on other roles' R2 drift (A5, B1, C1 and others) |
