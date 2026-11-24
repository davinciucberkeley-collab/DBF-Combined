# design_loop: agent design loop (T-035, R-INT-02, spec 8.2)

A thin CLI over the existing concept A scripts. One `run` does: load design, baseline checks, change a parameter, re-run
checks, interpret, compare with the baseline, save the changed design, write evidence.

```
python -I tools/design_loop/cli.py list-params
python -I tools/design_loop/cli.py run --set pack_capacity_ah=3.3 --name pack-3p3Ah [--evidence-dir DIR] [--keep-work] [--fail-on-regression]
python -I tools/design_loop/test_design_loop.py
```

Exit codes: 0 loop completed (failing claims are results, not errors), 1 a check step crashed / a committed file changed /
(with `--fail-on-regression`) a PASS became FAIL, 2 bad usage. A run takes about 10 s.

## What it runs (fast checks only, no Blender, no SITL)
| Step | Script (existing) | Category |
|---|---|---|
| mass / CG roll-up | `redesign/interfaces/merge_check.py --budget redesign/qp/A/cad/model/mass_budget.json` | rigid-body (static mass properties) + interference (graph) |
| inputs | `redesign/qp/A/proofs/gen_params_a.py` -> `params-A.json` | n/a |
| 109 claims: mass, CG, SM, T/W, window, current, endurance, cost, ... | `claims_a0..a3.py`, `redesign/proofs/build_graph.py --strict` | flight dynamics (algebraic), rigid-body; stored FEA / SITL / gate results are read, not re-run |

Gates that need Blender (`collide_a.py`, `assembly_check.py`) and SITL are not in the loop; their stored results enter as
claim inputs only. A parameter change that would need them (geometry, wing area) must be followed by those gates by hand.

## Safety: the committed design is never edited
`stage()` copies `redesign/{proofs,interfaces,qp/A}` (files under 300 kB, about 35 MB) into
`tools/design_loop/runs/<timestamp>-<name>/work` (git-ignored, deleted after the run unless `--keep-work`). The baseline is
re-computed in the copy and compared with the committed `proofs/out/graph.json` (it must match). Hashes of seven committed
files are checked before and after. The saved variant (changed `params-A.json` and changed interfaces files only) goes to
`variant_design/` beside `evidence.json` and `evidence.md`.

## Parameters (adapter-defined)
`list-params` prints them: `pack_capacity_ah`, `part_mass:<ID>=<g>`, `param:<group.name>=<value>`. Couplings are EST and written in
the evidence (for example the pack mass scales linearly with Ah; the BOM price and pack size are not updated).

## Swapping in the team schema (T-034)
The shared aircraft schema does not exist yet. All knowledge of concept A's files is in ONE module, `adapter_concept_a.py`.
`cli.py` only calls: `list_parameters()`, `parse_changes()`, `stage()`, `run_checks()`, `KEY_METRICS`, `ADAPTER_NAME` (and the
optional `read_claims()` for the baseline-vs-committed check). To use the schema, write `adapter_<schema>.py` with those names
(load the schema file, set a parameter in the schema, export to what the checks read) and run
`python -I tools/design_loop/cli.py --adapter adapter_<schema> run ...`. `cli.py` does not change. Per spec 8.2 it should then call
`tools/vtol.py` / the team CLI instead of the concept A scripts where those cover the same check; `tools/vtol.py` today targets
the older root `analysis/` design (v0.3.1 / 11-02 resize), not concept A, so it is not reused here.

## Limits
- Mass changes update the part roll-up, `mass.basic_cad_kg` and CG x (deltas); lateral CG, `CL-A-MASS-ITEM` for non-pack parts, cost and
  geometry do not follow.
- A PASS is a re-computation on EST / UNVERIFIED inputs, not a bench or flight result.
