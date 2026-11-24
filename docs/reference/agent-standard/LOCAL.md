# Agent Standard v0.2: how it applies in DBF-Combined (T-015, R-ORC-04)

The team standard is `agents-v0.2.md` in this folder, vendored verbatim from
`davinciucberkeley-collab/aircraft-platform` @ `5653727` (2026-11-23). It was shared by the user on 2026-11-23
(AM-039; "DBF Agent Roles: Quick Guide").
The six role files in `.claude/agents/` (advisor, auditor, builder, reviewer, scout, tactician) are the team's,
vendored verbatim. The only change is one appended line that points here.
This repo's own definitions (eng-reviewer, implementer, ledger-auditor, runner) are retired, so only one framework is in use.

## Old role to team role

| Retired (this repo) | Team role | Tier |
|---|---|---|
| runner (haiku) | builder | easy (haiku) |
| implementer (sonnet) | builder on a hard row, or tactician | hard (sonnet) |
| ledger-auditor (haiku) | auditor (read-only checks); builder for evidence-file writes | haiku |
| eng-reviewer (opus) | reviewer (a fresh instance per batch) | opus |
| conductor (main session) | conductor | opus |

## Path and validator mapping

| The standard says | In this repo |
|---|---|
| `standards/` criteria, `standards/review-scorecard.md` | `CLAUDE.md` hard constraints; `docs/requirements.md` acceptance columns; `redesign/qp/A/REQUIREMENTS-A.md`; `docs/reference/REVIEW-STYLE.md` |
| `plane validate --tier all` | `python -I tools/ledger_audit.py`; `python -I redesign/qp/A/proofs/run_all.py`; `redesign/qp/A/cad/collide_a.py`, `collide_glb_a.py`, `a_assembly.py`; `python -I redesign/qp/A/bom_a.py` |
| `reviews/` | `docs/audits/` |
| `knowledge/` scout templates | `docs/audits/<date>-<topic>.md`, citing the URL and the date checked (CLAUDE.md working rules) |
| plan file and its task checklist (user requests in their words) | `docs/spec-amendments.md` (verbatim requests), `docs/task-ledger.md` (status per request), `docs/execution-plan.md` (phases and routing) |
| agent table with step ids | ledger T-ids; every brief names its T-id |
| handoff file | `docs/session-state.md` (checkpoint and recovery procedure) |
| subtract before adding | the failure-resolution ladder in `docs/engineering-decisions.md` (same order) |
| quiet by default | AM-001 / AM-031 |
| `plane` CLI for design changes | not applicable: concept A is edited as source in `redesign/qp/A/` (AM-038 holds dbf-hangar for now) |

## Superpowers skills inside the roles (AM-052, 2026-11-24)

The roles say who does a step; the Superpowers skills say how. Each step invokes the skill named here and the
phase's "Skill / method used" column in `docs/execution-plan.md` records it (R-GEN-01). Phases before AM-052 stay
covered by AM-051.

| Step | Role | Superpowers skill |
|---|---|---|
| Shape a new piece of work | conductor | `superpowers:brainstorming`, then `superpowers:writing-plans` |
| Turn a plan step into exact briefs | tactician | `superpowers:writing-plans` (brief format) |
| Launch independent briefs | tactician or conductor | `superpowers:dispatching-parallel-agents`, `superpowers:subagent-driven-development`, launching only the roles above |
| Build | builder | `superpowers:test-driven-development` (the brief's pass check is written and seen failing first) |
| A failure | builder; one tier up after two failures | `superpowers:systematic-debugging` |
| Review a batch | reviewer (fresh) | `superpowers:requesting-code-review`; the conductor fixes findings with `superpowers:receiving-code-review` |
| Claim done / VERIFIED | conductor, auditor | `superpowers:verification-before-completion` |
| Finish a branch | conductor | `superpowers:finishing-a-development-branch` |

Conflict rules (CLAUDE.md and the amendments override skills):
- Only the six roles are launched; a skill that would launch a generic subagent launches the matching role instead.
- `brainstorming` questions are answered by the conductor within its permissions (AM-028); only team decisions go to the user.
- Minimize compute: on small tasks use each skill's lightest form (no separate plan document for a one-row change).

## Not adopted, and why

- **Hooks** (`tools/agent_hooks.py`: plan gate, edit gate, agent log).
  - They are written for the platform's layout (`core/`, `designs/`, `plans/YYYY-MM-DD-*.md` agent tables).
  - Installing them here would block every launch, because this repo's plans are ledger rows.
  - The auditor and reviewer enforce those rules by reading instead, which is what the standard's own "Not built yet" section allows.
  - Revisit if the team moves concept A into dbf-hangar.
- **Every unit is a PR.** This repo commits to `redesign/v1`, with pushes approved by the user (R-GEN-02).
