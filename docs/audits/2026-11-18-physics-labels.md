# T-017 (R-PHY-02): physics labels, 2026-11-18

Rule applied: a claim names what was computed. The collision/interference gate (`collide.py`) is a static check at neutral and at the elevon stops; the build-step gate (`assembly_check.py`) is a swept insertion check on straight-line paths. Mechanism physics is in docs/analysis-records.md (AR-001 kinematics, AR-002 rigid-body dynamics, AR-003 swept interference). The user's own constraint sentence in CLAUDE.md ("3-D physics simulation") is unchanged; one clarifying line was added at CLAUDE.md:74.

## Before / after

| file:line | old | new |
|---|---|---|
| README.md:22 | Passes the 3-D physics checks: ... | Passes the 3-D gates: interference check (static, at neutral and at the elevon stops) + swept insertion check (straight-line build-step paths); "interference checks, not physics simulations"; pointer to AR-001/002/003 |
| redesign/README.md:12 | same as README.md:22 | same new text |
| redesign/qp/README.md:13 | Passes the 3-D physics checks. | Passes the 3-D gates (interference check, static, at neutral and at the elevon stops; swept insertion check, straight-line build-step paths). |
| redesign/site/app.html:453 and index.html:461 | 3-D physics gates | 3-D interference gates (static) |
| redesign/site/app.html:470 and index.html:478 | Passes the 3-D physics checks / Every build step ... | Passes the 3-D gates / Interference check (static, at neutral and at the elevon stops) ... plus a swept insertion check (straight-line build-step paths) ... |
| redesign/qp/A/REQUIREMENTS-A.md:13 | A-U4 3-D physics pass | A-U4 3-D gates (CLAUDE.md wording quoted; computed: interference + swept insertion) |
| redesign/qp/requirements/REQUIREMENTS-QP.md:17 | QP-U4 3-D physics pass | QP-U4 3-D gates (same treatment) |
| redesign/qp/A/proofs/claims_a0_base.py:28 | source note "3-D physics pass" | "3-D physics simulation (user wording; computed as interference + swept insertion checks)" |
| redesign/qp/A/proofs/claims_a0_base.py:95 | A-U4 "3-D physics pass", "collision gate ..., assembly sweep" | "3-D gates pass (interference + swept insertion checks)", "interference check, static, at neutral and at the elevon stops ... swept insertion check (straight-line build-step paths)" |
| redesign/showcase/animation/assembly_check.py:1629 | Build sequence: swept-path physics check | Build sequence: swept insertion check (straight-line build-step paths) |
| redesign/showcase/animation/build/ASSEMBLY-CHECK.md:1 | same old title | same new title (edited in place, see stale list) |
| redesign/showcase/animation/render_build.py:3 | plan + physics-check the motions | plan + swept insertion check of the motions (straight-line paths) |
| redesign/blender/README.md:110 | passes a swept-path physics check first | passes a swept insertion check (straight-line build-step paths) first |
| redesign/RESUME.md:18 | No parts phasing (physics-simulator ready) | No parts phasing (interference gates; physics-simulator ready) |
| CLAUDE.md:74 (added) | n/a | New line: the 3-D gates are interference checks; mechanism physics is in docs/analysis-records.md |

Total relabelled: 15 distinct claims in 14 files, plus 1 added line (CLAUDE.md); site claims counted once per page.

## Generated outputs

- Regenerated (`python -I redesign/qp/A/proofs/run_all.py`, 2 s): `claims.a0_base.json`, `out/CHAIN.md`, `out/READABLE.md`, `out/graph.js`, `out/graph.json`, `out/readable.js`. A-U4 is still CHECKED; only label text changed (35 lines, no number moved).
- Stale / not regenerated:
  - `redesign/showcase/animation/build/ASSEMBLY-CHECK.md`: generator `assembly_check.py` takes about 25 min; only the title line was edited by hand, the generator string is fixed, so the next run reproduces it.
  - `redesign/site/app.html:453,470` and `index.html:461,478` still carry stale numbers (45 of 45 steps, 104 of 104 parts, 0.87 strand-m, 35 of 35 steps; current run is 66 steps, 113 parts, 1.02 strand-m per `A/cad/out/ASSEMBLY.md`, `wire_inventory.json`). Not touched: outside this task (labels only); needs a separate refresh.
  - K09-L records (`redesign/review/CDR-2026-11-13/**`, `review/CLOSURE-ROUND-2026-11-14/**`, `review/QP-1`, `QP-3`, `config-study/**`, `collision/README.md`, `collision/collide.py`) were left as the historical record.
  - Not edited by rule: docs/MASTER_PROJECT_SPEC.md, docs/spec-amendments.md, CLAUDE.md "Hard constraints" wording, docs/capability-audit.md (lists the old occurrences as the finding), docs/requirements.md R-PHY-02 row, docs/task-ledger.md. Files owned by the other agent (amodel, CHANGE-LOG.md, params-A.json, mechanism/, analysis-records.md) not touched.

## Final grep

Command: `grep -rniI "physics" --include=*.md --include=*.html --include=*.py README.md CLAUDE.md redesign/site/app.html redesign/site/index.html redesign/qp redesign/showcase redesign/collision redesign/blender redesign/RESUME.md redesign/README.md | grep -v "proofs/out/\|amodel\|mechanism/"`

| file:line | remaining use | why accurate |
|---|---|---|
| README.md:22, redesign/README.md:12 | "not physics simulations; mechanism physics is in ..." | negation and a pointer to real analyses |
| CLAUDE.md:53 | "3-D physics simulation" | the user's own constraint text, not edited |
| CLAUDE.md:74 | "mechanism physics is in docs/analysis-records.md" | added clarification |
| redesign/qp/A/proofs/claims_a0_base.py:28, REQUIREMENTS-A.md:13, REQUIREMENTS-QP.md:17 | quotes the CLAUDE.md wording next to what is computed | attribution of the user's wording |
| REQUIREMENTS-QP.md:8, :61, review/QP-1/REQUIREMENTS.md:6 and similar | "3-D physics" as the name of the USER class; "physics" in energy split | quotes the user's constraint; the energy split is a real calculation |
| qp/A/MASS-GATE.md:9 | "Physics now from prop_a.py" | hand calc on vendor static prop data, a real model |
| qp/A/structures/structures_a.py:206, structures_run.md:186 | "physics rebuilt standalone" (landing_a.py) | a real 6-dof elasto-plastic rigid-body integration |
| qp/requirements/CARRY-OVER.md:6,33,36,77 | `c0_physics.py`, "pure physics" claims | file name of a real flight-model script; momentum theory, tube bending are real physics |
| collision/collide.py:2,12; collision/README.md:3 | "so the CAD can go into a rigid-body physics simulator" | states the purpose of the gate (input readiness), not that it simulates; K09-L tool, kept as record |
| RESUME.md:18 | "interference gates; physics-simulator ready" | names the gates as interference and the readiness as the goal |
| Other hits under redesign/team, redesign/config-study, docs/research, docs/test (e.g. c0_physics.py, SU2/RANS "Physics" rows, momentum theory) | sizing, CFD and flight-model physics | real computation, unrelated to the collision gate; docs/video/PIPELINE-AUDIT.md rows cite a gap in real physics video |
