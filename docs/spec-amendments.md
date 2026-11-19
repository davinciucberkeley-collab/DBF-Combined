# Spec amendments (verbatim user instructions after the master spec)

Append-only. Each amendment is the user's exact wording; its relation to
`MASTER_PROJECT_SPEC.md` and its requirement IDs (in `requirements.md`) are noted
above the text. Never edit an earlier entry; a superseding instruction is a new
entry that names what it supersedes.

Integrity: `docs/spec-integrity.sha256` holds the SHA-256 of the master spec and
of this file's entries; `tools/spec_guard.py --check` verifies them.

## Origin of the master spec
- Received: 2026-11-18, Claude Code session (desktop app), pasted by Dillon Alcouffe.
- Saved verbatim to `docs/MASTER_PROJECT_SPEC.md` from the full pasted text (nothing
  missing; no reconstruction from memory).

---

## AM-001 — 2026-11-18 — Communication efficiency and minimal output protocol
Relation: adds to the master spec; supersedes nothing. It narrows how progress is
reported (spec "Provide concise progress updates at meaningful milestones") without
removing any work requirement. Requirement IDs: R-COM-01 … R-COM-06.

```text
Communication Efficiency and Minimal Output Protocol
Update the existing project instructions and agent orchestration system to enforce a minimal-output, execution-first communication style.
My goal is to maximize actual engineering progress while minimizing unnecessary text, narration, and token consumption.
Communication rules

1. Do not narrate routine actions. Avoid messages such as "I'm now reading the files," "Next, I'll update the code," or "Let me check that."
2. Do not repeatedly explain the plan. The persistent execution plan and task ledger already contain that information.
3. Do not provide lengthy progress summaries. Keep routine updates silent unless something meaningful requires my attention.
4. Do not repeat information already available in project files or earlier messages.
5. Do not ask unnecessary questions. Make reasonable decisions autonomously within existing permissions and project requirements.
6. Do not produce verbose subagent reports. Require subagents to save detailed findings in project files and return only concise results.
7. Do not sacrifice engineering quality, testing, documentation, or task completion to reduce text output. This rule applies to conversational narration, not the actual work.

When to communicate
Provide a message when:

* I directly ask a question. Answer it thoroughly enough to be useful.
* An important milestone is completed.
* A critical engineering issue is discovered.
* A decision requires my input.
* An action requires authorization.
* A task is genuinely blocked.
* A significant failure or unexpected change occurs.
* The entire project is complete or must stop.

For routine milestones, use approximately 1–3 concise sentences.
Do not impose an artificial word limit on answers to direct questions.
Agent orchestration
Apply these rules to all subagents where supported.
Subagents should return concise structured results containing:

* Task ID.
* Outcome.
* Verification status.
* Evidence location.
* Blocker, if any.

Save detailed technical information in the existing persistent project documentation.
Persistent enforcement
Add these communication preferences to the appropriate existing `CLAUDE.md` instructions or linked configuration files so they survive compaction, session restarts, and agent handoffs.
Use supported hooks or lightweight audits where useful to detect unnecessary narration.
Do not create complicated enforcement infrastructure or additional interfaces just for this purpose.
Avoid strict output-length restrictions that could interfere with tool execution, required warnings, error reporting, or answering my questions.
Final directive
Work quietly, communicate selectively, answer questions directly, and prioritize implementation over narration.
Do not pause execution merely to provide a progress update.
Continue following the complete master project specification, including persistent task tracking, independent verification, and all previously established requirements.
Implement this communication protocol now, then resume the existing project work without restarting or changing its scope.
```

## AM-002 — 2026-11-19 — Cleanup approval (answer to the dry-run §9 questions)
Relation: the user's answer to the seven questions in `docs/audits/2026-11-18-cleanup-dryrun.md` §9; it is the
approval spec 9.3 step 9 requires for removals. Scope as applied (conductor's reading, logged in
`docs/repository-audit.md` §3): remove items that no current-design file, script, page or claim uses; keep
everything that is referenced, served, CI-checked or the recorded K09-L film record; no history rewrite.
Requirement IDs: R-REPO-03, R-REPO-04 (T-041).

```text
1. For the seven questions, if something is unused let it go, there is not need for them if they do not contribute to our current design
```

## AM-003 — 2026-11-19 — Team inputs not ready; no DaVinci spend
Relation: answers the pending asks for James's agent definitions (T-015), the shared aircraft schema (T-034) and
DaVinci access/spend (T-037); those tasks stay BLOCKED on the team; no money is spent on DaVinci.
Requirement IDs: R-INT-01 … R-INT-06 (as mapped in `requirements.md`), R-GEN-02.

```text
For question 3: The agent definitions and aircraft schema have not been completed yet, don't do any DaVinci spend yet
```

## AM-004 — 2026-11-19 — Dillon away 8+ hours; decisions go to an opus agent
Relation: while Dillon is unavailable, any decision that would otherwise go to him (AM-001 "a decision or
authorization only the user can give") is put to an independent opus agent instead; hard constraints, money,
purchases, irreversible actions and history rewrites still wait for Dillon (they are not engineering decisions).
Requirement IDs: R-COM-04, R-GEN-02, R-ORC-01.

```text
I won't be available for the next 8+ hours, so if there is an issue that you run into that need a decision on, consult an opus agent for the time being
```

## AM-005 — 2026-11-19 — Board choice for concept A: O4 resize once
Relation: answers the board option sheet D-216 (`docs/audits/2026-11-19-T070-decision.md` s6, T-072). Concept A
continues under BOARD R3 "resize once": engineering mass recovery, wing glass torsion skin, centre-node rework,
smaller pack and 10x4.5 props, gate re-derived by the C3 pitch-over at +-5 %, hard go/no-go 2026-12-15 (no-go:
board re-sits at once). Not approved by this answer: purchases (still none before early Dec 2026) and the car-trunk
measurement. Requirement IDs: R-OPT-01, R-OPT-02, R-GEN-02.

```text
O4: resize once
```
