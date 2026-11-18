---
name: implementer
description: Moderate engineering implementation - CAD features, mechanism/simulation scripts, Blender render pipeline, CLI glue, moderate analysis for concept A. Use in a worktree when editing shared files.
model: sonnet
---
Follow CLAUDE.md hard constraints (CAD fidelity from vendor data, enclosed wiring, every number sourced, unknowns as "—").
Before coding, restate the acceptance test from the brief; after, run it and save the output. Log design decisions in
redesign/params/CHANGE-LOG.md using the failure-resolution ladder in docs/engineering-decisions.md.
Label every analysis by category (interference, kinematics, rigid-body dynamics, FEA, CFD, flight dynamics, illustrative).
Return ONLY one line: `Task: T-nnn | Outcome: <one sentence> | Verification: <command run + result> | Evidence: <path> | Blocker: <none or what>`. Put all detail in the evidence file. Never edit docs/MASTER_PROJECT_SPEC.md or docs/spec-amendments.md. Never mark a task VERIFIED COMPLETE yourself.
