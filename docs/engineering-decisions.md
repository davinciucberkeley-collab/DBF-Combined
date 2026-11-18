# Engineering decisions — index and program decisions

Aircraft design decisions stay in their existing log, `redesign/params/CHANGE-LOG.md` (D-1…D-211 as of
2026-11-18; concept A from D-182). This file does not duplicate them. It holds (1) the decision method the spec
requires and (2) program-level decisions (PD-nnn) about process, tooling and scope.

## Failure-resolution ladder (spec 6.1, R-OPT-01)
For every failed check, the decision entry names the rungs tried, in order:
1. Subtract (remove a feature/part) 2. Modify geometry 3. Rearrange 4. Change mechanism/structural approach 5. Add material/parts.
A rung-5 fix must state why rungs 1–4 do not work.

## Trade table (spec 6.2, R-OPT-02)
`| Option | Δmass g | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |`
Function first, then mass (6.3). Cite at least one benchmark/literature source for mechanism choices (6.4).

## Program decisions
| ID | Date | Decision | Reason | Supersedes |
|---|---|---|---|---|
| PD-001 | 2026-11-18 | Spec reaches sessions through a mandatory pointer in CLAUDE.md + SessionStart hook brief, not an `@` import | Spec ≈ 9 k words; importing it every turn costs context in every session and subagent (spec 1.2 allows the pointer). Full read at milestones, recovery, final verification | — |
| PD-002 | 2026-11-18 | Mechanism simulations (spec Part 5) run now for concept A | The 11-18 spec explicitly asks for them; it is newer than the memory note "no simulation round until Dillon finalizes" (11-14). Scope: elevon linkage kinematics, one rigid-body case, swept collision. No new Simulations tab (R-INT-05) | memory "no-sims-until-final" for these analyses only |
| PD-003 | 2026-11-18 | Hooks and agent definitions are committed: `.gitignore` now ignores `.claude/*` except `settings.json`, `hooks/`, `agents/` | Recovery must work for every team clone, not just this machine | — |
| PD-004 | 2026-11-18 | Video work targets concept A; K09-L films stay as the record | CLAUDE.md: concept A is the aircraft (D-182) | — |
