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
