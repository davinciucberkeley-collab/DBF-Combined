# Scaled quad tailsitter VTOL (concept A) — student project

## Master program (mandatory, 2026-11-18)
- Canonical spec: `docs/MASTER_PROJECT_SPEC.md` (verbatim; never edit, summarise or delete it). Later user
  instructions go verbatim, append-only, into `docs/spec-amendments.md`.
- State lives on disk, not in the conversation: `docs/requirements.md` (R-ids), `docs/task-ledger.md` (T-ids,
  never delete rows), `docs/execution-plan.md` (phases, model routing, task protocol), `docs/session-state.md`
  (checkpoint + recovery procedure), `docs/engineering-decisions.md`, `docs/verification-report.md`.
- After compaction, restart or handoff: follow `docs/session-state.md` "Recovery procedure" before any work;
  a compaction summary is not authoritative. Read the full spec at milestones, after compaction and before
  final verification. `python -I tools/ledger_audit.py` must pass.
- Only VERIFIED COMPLETE counts, with independently checked evidence. Before stopping, reconcile the ledger
  and name every unfinished requirement.
- **All work in this repo follows the team Agent Standard v0.2 (AM-040, mandatory):** read
  `docs/reference/agent-standard/agents-v0.2.md` and `LOCAL.md` (repo mapping) before any multi-agent work. Use only
  the roles in `.claude/agents/`: builder, scout, tactician, auditor, reviewer (a fresh one per batch), advisor.
  Cheapest tier first, one tier up after two failures; subtract before adding; scout before picking an approach.
  Superpowers skills run inside those roles (AM-052; mapping in `LOCAL.md`): log the skill used per phase (R-GEN-01).

## Communication (AM-001)
- Work quietly: no narration of routine actions, no restating the plan or ledger, no long progress summaries,
  no repeating what files or earlier messages already say. Decide within permissions instead of asking.
- Message only for: a direct question (answer fully, no length cap), a milestone (1–3 sentences), a critical
  engineering issue, a decision or authorization only the user can give, a real blocker, a significant
  failure, or project end. Never pause execution just to report.
- Subagents return one line: Task ID | Outcome | Verification | Evidence path | Blocker; details go in files.
- Brevity never reduces the work: tests, docs, warnings and error reports stay complete.
- Standing rules: AM-028 (no 'continue?' prompts), AM-030 (no new test equipment) — see docs/spec-amendments.md.

**2026-11-19 (AM-008): the aircraft must be designed by Claude and built by the students; no commercial kit airframe
(the ZOHD Altus lifeboat is withdrawn; D-218 reversed).** Concept A failed its mass gate (T-067/T-070) and
its O4 resize (D-217). Re-sit (AM-009, D-219): concept A continues as **O4b** (9x4.5 props, Lua spin cap on a Kakute
H743-Wing, 4S 2,800 mAh pack, glass wing skin, mass recovery; predicted 1.64 kg at D-219, now 1.881 kg EST (CAD 1,641 g) with SunnySky X2216
880KV motors (D-227) and the FC 75 mm left of centre (D-239/D-240); mass gate missed, physics checks govern; 14 proof claims
FAIL (run_all, 2026-11-23: the 12 of D-237 pending bench / tap tests, plus elevon pitch use 0.651 against 0.60 of 15 deg
(C3 controls at 0.25 chord; the 0.30 chord D-250 was reverted, D-251; no derived reserve fits, D-252), and 1.3 Vs 17.74 m/s at the predicted mass, A-P6, gated by TP-11); landing stroke passes (17.2 mm) only inside
the foam region Fp 37.5-39.0 N, zeta 0.02-0.05 (D-243, TP-3); BOM $1,939.17 of $2,000 (D-235); Order 1 $887.25 for approval 1-4 Dec (T-093); no fabrication before Jacobs reopens (AM-037), go/no-go Fri 2027-01-29 (D-248, slack +2 d)).

**History (superseded by the O4b status above): configuration changed 2026-11-14 (D-182, J6 board, `redesign/review/QP-1/BOARD.md`):**
K09-L could not be built new within the $2,000 limit (cheapest workable build
about $2,577, `redesign/review/CLOSURE-ROUND-2026-11-14/DESIGN-TO-COST.md`).
After sizing four concepts to the same depth (`redesign/review/QP-1/`), the board
chose **concept A, a scaled-down quad tailsitter**: about 1.23 kg, 0.90 m wing,
T-Motor MN2212 KV780 on 4S, 4S 2000 mAh packs, one-piece in the car box,
about $1,499 (margin about +$501, estimate). Fallback: B, the small quadplane,
after re-pricing; lifeboat withdrawn (AM-008). D-181 (quadplane, provisional) is reversed.

Previous design K09-L (quad tailsitter flying wing, mass gate 2.6 kg, kept as record): see `redesign/CONFIGURATION.md`.

## Hard constraints
- $2,000 total physical budget (hardware, spares, batteries, test gear,
  shipping, tax). The Jacobs Hall Makers Pass is paid outside this budget.
- Built and flight-tested by the end of April 2027.
- Portable: a team of 4 moves it routinely; hard cap under 25 kg (55 lb).
  It need not travel in one piece (user, 2026-11-14), but the packed aircraft
  must fit in one standard car trunk, two at most. (K09-L travelled in one
  piece in a ~1.25 × 0.55 × 0.45 m box.)
- Passes a 3-D physics simulation: every build step and the assembled
  aircraft (`redesign/showcase/animation/assembly_check.py`, collision
  `redesign/collision/collide.py --glb`) with no part interpenetration, no
  open wire ends and no exemptions; flight cases in the 3-D sims (C5 landing,
  SITL) pass against their limits. Concept A runs these as `redesign/qp/A/cad/a_assembly.py`,
  `collide_a.py` (CAD) and `collide_glb_a.py` (exported GLB); its wire-entry test is the D-247
  pad / termination-proximity rule (team decision, the user may veto).
- The CAD looks exactly like the physical aircraft (user, 2026-11-15): every
  part modelled to its real shape and dimensions from the vendor drawing or
  data sheet (props with real blades, motors, servos, connectors, boards,
  fasteners), no stand-in disks or boxes. Where a dimension is unknown, say so
  and mark the part, never invent it.
- Limit exposed wiring (user, 2026-11-15): route wires inside the arm tubes,
  wing-core channels, fairings or covers. Any wire left exposed outside the
  skin (e.g. the last few mm at a motor or connector) is listed with its
  length and the reason it cannot be enclosed, and kept to the minimum. The
  current per-wire table (0.597 strand-m exposed, D-240 CAD) is generated by
  `redesign/qp/A/cad/exposed_wire_table.py` into `redesign/qp/A/cad/out/EXPOSED-WIRING.md`.

Within these constraints the engineering agents (`redesign/TEAM.md`) make the
design decisions, including mass, mission and performance trade-offs; log
each one with its reasoning in `redesign/params/CHANGE-LOG.md`.

## Where things are
- README.md is the front door: directory map, status, how to view the pages.
- The 3-D gates (`collide.py`, `assembly_check.py`) are interference checks (static, plus straight-line swept insertion); mechanism physics is in docs/analysis-records.md (AR-001 kinematics, AR-002 rigid-body dynamics, AR-003 swept interference).
- archive/c0/DECISIONS.md lists the open design-parameter conflicts (C0 era). Do not pick a side
  silently; `archive/c0/analysis/` + `archive/c0/cad/` are the 11-02 resize, while
  `archive/c0/inventory/`, `archive/c0/fusion/`, `archive/c0/concepts/variants/` are still on v0.3.1.
  Old path to new path: docs/archive-path-map.md (T-104 layout cleanup).
- PROVENANCE.md says which source repo and commit each area came from.
- redesign/README.md is the concept A entry page; the K09-L entry page is redesign/README-K09L.md.

## Working rules
- Scope is the real, physical aircraft. Ignore any browser flight-sim code.
- Every number cites its source: a repo file, a shown formula, or a URL with
  the date checked. Look up prices and specs; don't recall them.
- Label estimates as estimates. Unknowns are "—", never invented.
- Reports follow docs/reference/REVIEW-STYLE.md.
- Never commit secrets (API keys, tokens, passwords), including the team's
  Claude API key: keep it in an environment variable or a git-ignored `.env`.

## Team (commit attribution)
The repo lives at davinciucberkeley-collab/DBF-Combined (consolidated 2026-11-08 from
DBF-VTOL, DillonVTOL, TiltWing and OpenCAEModel; see PROVENANCE.md). Claude sessions push from a
shared account, so ask who is working (or use the name they give) and credit them
with `git commit --author "<Name> <email>"`. Use `Co-Authored-By: <Name> <email>`
trailers for work done together. Use these GitHub no-reply emails, never personal
addresses.

| Name | GitHub | Commit email |
|---|---|---|
| Tristan Hottier | TristanHottier | 185231225+TristanHottier@users.noreply.github.com |
| Dillon Alcouffe | Dalcouffe1 | 130024709+Dalcouffe1@users.noreply.github.com |
| James Guymon | JamesRop | 55683057+JamesRop@users.noreply.github.com |
| Vaibhav Bagrodia | vaibhav1301-arch | 336305533+vaibhav1301-arch@users.noreply.github.com |

## Key files
- docs/VTOL-REVIEW-PROMPT.md — the design-review task.
- docs/reference/REVIEW-STYLE.md — house style for reviews.
- docs/reference/lift-cruise-reference.png — BETA Alia and 8-lift reference
  configurations.
