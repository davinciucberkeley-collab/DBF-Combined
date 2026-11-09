# Claims graph schema (`proofs/1`)

One graph holds every engineering claim, the calculation behind it, the numbers that calculation reads, and where
those numbers come from. It is configuration-independent: nothing here names a layout.
Authors write `claims.json` files (usually through `proofkit.py`); `build_graph.py` merges them, re-runs every
calculation and writes `out/graph.json` + `out/CHAIN.md`.

## Files

| File | Written by | Holds |
|---|---|---|
| `redesign/**/claims.json`, `redesign/**/claims.<name>.json` | an analysis script via `proofkit` (or by hand) | the nodes below, except parameters |
| `params.json` files listed in a claims file's `"params"` + `redesign/params/params.json` | integrator / subsystem | parameter values (see *Parameters*) |
| `redesign/**/interfaces.json` | interface keeper / subsystems | part ids that claims may name in `parts` |
| `redesign/proofs/out/graph.json` (+ `graph.js`, `CHAIN.md`) | `build_graph.py` only | the merged, checked graph |

`proofs/examples/` is excluded from the real build (it is a demonstration aircraft) unless `--examples` is given.

## Node types

Every node has `id` (unique across the repo), `type`, `title` (short label, ≤ 6 words). Optional on all: `note`.

| type | id convention | Required fields | Optional fields |
|---|---|---|---|
| `requirement` | `R-…`, or the config-study id (`D11`) | `title`, `text` (measurable: "hover T/W ≥ 1.6") | `ref` (file#anchor or URL where it is defined), `cites` |
| `claim` | `CL-<area>-…` | `title`, `value`, `unit`, `calc` + `output` (or no calc → PROPOSED) | `limit`, `verifies` (requirement ids), `parts`, `assumes`, `cites`, `how` (how to verify), `status` (only `PROPOSED` may be declared) |
| `calculation` | `CALC-<area>-…` | `script` (repo-relative path), `function`, `inputs` {arg: node id}, `outputs` {name: stored value} | `equation` (plain text, one line), `units` {arg or output: unit}, `tol` (relative, default 1e-6), `input_values` (snapshot written by proofkit), `assumes`, `cites` |
| `parameter` | `P:<dotted.key>` (made by build_graph from params.json) | `value`, `file` | `unit`, `source` (source id(s) or a text basis), `status` |
| `source` | `SRC-…` | `title`, `kind` (`datasheet` `paper` `book` `web` `test` `standard`) | `url`, `checked` (date the value was compared with the source), `where` (page/table), `status` |
| `assumption` | `ASM-…` | `title`, `text`, `basis` (why it is reasonable) | `value`, `unit`, `status` (`PROPOSED` default, or `UNVERIFIED`), `cites` |
| `test` | `T-…` | `title`, `verifies` (claim ids), `state` (`planned` / `run`) | `procedure`, `result` (`pass`/`fail`), `measured`, `date`, `evidence` (file or link) |
| `part` | the part id from `interfaces.json` | made by build_graph from claims' `parts` | `name`, `subsystem`, `file` |

`claim.limit` = `{"op": ">=" | "<=", "value": 1.6}` or `{"op": ">=", "ref": "P:requirements.hover_tw_min"}`
(`ref` may name any node with a `value`). Margin = `(value − limit) / limit` for `>=`, `(limit − value) / limit`
for `<=`; negative margin = the claim **fails**.

## Edges

Edges point in the direction evidence flows: **source → parameter → calculation → claim → requirement**.
`build_graph.py` makes them from the fields above; authors never write edges directly.

| type | from → to | made from | reads as |
|---|---|---|---|
| `cites` | source → any node | `source` of a parameter, `cites` of any node | "the parameter cites the datasheet" |
| `uses` | parameter / claim / assumption → calculation or claim | `calc.inputs`, `claim.limit.ref` | "the calculation uses the parameter" |
| `assumes` | assumption → calculation / claim | `assumes` | "the calculation assumes …" |
| `derives-from` | calculation → claim | `claim.calc` | "the claim derives from the calculation" |
| `verifies` | claim → requirement; test → claim | `claim.verifies`, `test.verifies` | "the claim verifies the requirement" |
| `about` | claim → part | `claim.parts` | for the 3-D link-out only; not part of a chain |

A **chain** for requirement R is everything reachable backwards from R. `CHAIN.md` prints it as
`R ← claim ← calc ← param ← source`, one requirement per section.

## Status (computed, not typed)

Vocabulary from `redesign/inputs/ADVISOR-XV24-LESSONS.md`. `MODELLED` belongs to parts (Fusion), not claims.

| Status | Claim | Parameter / source / assumption / test |
|---|---|---|
| `PROPOSED` | has a value but no calculation yet | design choice with a text basis; assumption with a basis; test planned |
| `CHECKED` | calculation re-runs to the stored value **and** margin ≥ 0 **and** no input is UNVERIFIED or an unchecked claim | source value compared with the source (`checked` date); parameter citing only checked sources |
| `VERIFIED` | a `test` with `state: run`, `result: pass` verifies it (physical evidence beats the analysis chain) | test run and passed; source of `kind: test` that passed |
| `UNVERIFIED` | calculation runs, but a blocker exists — each listed in `reasons` (unsourced input, UNVERIFIED assumption, upstream claim not checked, **negative margin = `fails: true`**) | parameter with no source; source never checked; assumption marked UNVERIFIED; test run and failed |

Requirement status = worst of the claims that verify it (`UNVERIFIED` < `PROPOSED` < `CHECKED` < `VERIFIED`);
a requirement no claim verifies is `UNVERIFIED` ("no claim").

## Build rules (what fails the build, exit code 1)

1. A calculation that does not re-run to its stored `outputs` within `tol` (**drift**). The message names the
   inputs whose current value differs from the `input_values` snapshot and the script to re-run.
2. A claim whose `value` differs from its calculation's output.
3. A reference to a node id that does not exist; duplicate ids; a parameter key with two different values in two files.
4. A unit mismatch between `calc.units[arg]` and the input node's `unit` (plain string compare, e.g. `mm` ≠ `m`).
5. `--strict` only: any claim with a negative margin, any requirement with no claim.

Warnings (printed, build passes): a `parts` id not found in any `interfaces.json`; a source with no `url`.

## `graph.json` (what the viewer reads)

```json
{ "schema": "proofs/1",
  "meta": { "generated": "…", "ok": true, "errors": [], "warnings": [], "counts": {…},
            "part_link": "../../viewer/index.html#part={id}", "dataset": "examples" },
  "nodes": [ { "id": "CL-EX-HOVER-TW", "type": "claim", "title": "…", "status": "CHECKED",
               "reasons": [], "fails": false, "importance": 7, "value": 2.49, "unit": "-",
               "limit": {"op": ">=", "value": 1.6}, "margin": 0.56, "…": "type fields as above" } ],
  "edges": [ { "source": "CALC-EX-HOVER-TW", "target": "CL-EX-HOVER-TW", "type": "derives-from" } ] }
```

`importance` = number of claims whose chain contains the node (claims and requirements count their own chain);
the viewer sizes nodes by it.
