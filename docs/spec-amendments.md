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

## AM-006 — 2026-11-19 — Board re-sit after the O4 early no-go: O4b, conditional
Relation: answers D-217 (`docs/audits/2026-11-19-O4-feasibility.md` s6). Supersedes the O4 path of AM-005 (kept as
the record). Concept A continues as O4b (9x4.5 props kept, voltage-scheduled spin cap so one motor <= 12.1 A, pack
>= 2,350 mAh, engineering recovery, glass skin, C6 centre node, T-068 package) on condition that three $0 checks
close by 2026-11-26: (1) ArduPilot Lua on the flight controller, or an H7 wing FC priced with the cost rule G7
re-run; (2) an in-stock 4S pack >= 2,350 mAh at <= 275 g; (3) the C3 time-domain pitch-over at 1.64 kg >= +-5 %
and the landing re-runs at 1.64 kg. The C3 and landing runs named in check 3 are approved by this answer. If any
check fails: the ZOHD Altus (O6) at the 2026-12-15 order, as recommended in D-217. The 2026-12-15 bench go/no-go
stays. Not approved by this answer: purchases (none before early Dec 2026). Requirement IDs: R-OPT-01, R-OPT-02,
R-GEN-02.

```text
O4b, if $0 checks pass
```

## AM-007 — 2026-11-19 — Board decision: ZOHD Altus VTOL kit (O6)
Relation: answers the O4b check result (T-074: check 1 failed the cost rule G7 by about $50, check 2 passed only
with an EU-only pack and a tray change, check 3 passed). Under AM-006 a failed check means O6. Concept A stops as
the build target and is kept as the record (as K09-L was); the aircraft to build is the ZOHD Altus VTOL kit, order
planned for 2026-12-15 (purchases still need Dillon's approval; none before early Dec 2026). Hard constraints
(CLAUDE.md: $2,000, April 2027 flight test, trunk, 3-D gates, CAD fidelity, enclosed wiring) apply to the Altus
build. Requirement IDs: R-OPT-01, R-OPT-02, R-GEN-02, R-CAD-01.

```text
Altus (O6)
```

## AM-008 — 2026-11-19 — Altus rejected; the aircraft must be Claude-designed and student-built
Relation: withdraws AM-007 (O6, ZOHD Altus kit) after Dillon asked what the Altus is; D-218 is reversed. Adds a
standing constraint: the aircraft is designed by Claude (the engineering agents) and built by the students; a
commercial kit airframe is not acceptable. This removes O6 (Altus) from every board sheet, including the lifeboat
role named in CLAUDE.md (D-182). The board re-sit after T-074 is open again between Claude-designed options.
Requirement IDs: R-OPT-01, R-OPT-02, R-GEN-02, R-CAD-01.

```text
No, I don't want to do the altus, this must be something that is designed by claude and is built by students
```

## AM-009 — 2026-11-19 — Board re-sit (Claude-designed options): O4b, accepting the G7 shortfall
Relation: answers the re-sit after AM-008. Concept A continues as O4b (`docs/audits/2026-11-19-O4-feasibility.md`
s6-s7; T-074): 9x4.5 props, voltage-scheduled spin cap via ArduPilot Lua on a Kakute H743-Wing ($141.44 RMRC,
T-074 check 1), a 4S 2,800 mAh pack (GNB 267 g, EU source, tray change; T-074 check 2), engineering mass recovery,
glass torsion skin, C6 centre node, T-068 package. Dillon accepts the cost-rule G7 shortfall of about $50 (the
$2,000 hard limit still holds: scratch total $1,829.59). The 2026-12-15 bench go/no-go stays. Purchases still
need Dillon's approval (none before early Dec 2026). Requirement IDs: R-OPT-01, R-OPT-02, R-GEN-02.

```text
O4b, accept $50
```

## AM-010 — 2026-11-19 — Budget tolerance during initial design
Relation: qualifies the $2,000 hard constraint (CLAUDE.md) and the derived cost rule G7 for the initial design
stage only. Interpretation (recorded, not stretched): while the design is being developed, cost estimates may run
somewhat over the budget or the G7 margin without stopping the design; every estimate is still reported against
$2,000 and G7, and the purchase plan for the build comes back to Dillon for approval. "A bit" is not quantified by
Dillon; a design estimate more than a few percent over $2,000 is flagged to him rather than assumed allowed.
Requirement IDs: R-GEN-02, R-OPT-02.

```text
It is alright to go a bit over the budget when doing the initial design
```

## AM-011 — 2026-11-19 — Correction to AM-010: weight, not budget
Relation: corrects AM-010 the same day. AM-010's budget tolerance is WITHDRAWN: the $2,000 budget stays a hard limit
as before (AM-009's accepted G7 growth-margin shortfall of about $50 stands; the $2,000 total itself is not to be
exceeded). What may go over during the initial design is the WEIGHT target: a design estimate above the mass gate
(1,470 g, MASS-GATE.md) does not by itself stop the initial design. Interpretation (recorded, not stretched): the
physics checks that depend on mass (T/W, transition window A-P3, landing loads, cruise time) still apply at the
predicted mass and are reported against their limits; every mass estimate is still reported against the gate.
Requirement IDs: R-OPT-02, R-OPT-05, R-GEN-02.

```text
Scratch that, I meant weight is something that we can go over in the initial design, not budget
```

## AM-012 — 2026-11-19 — Keep the crash reserve
Relation: qualifies AM-009 (G7 shortfall of about $50 accepted). The crash reserve (BOM line, about $327.43) is not
to be cut to close the G7 gap or to pay for O4b changes (H743-Wing FC, EU pack). Interpretation (recorded, not
stretched): "enough" crash reserve is not quantified by Dillon; the current reserve stays as listed unless he says
otherwise, and any O4b cost growth (pack in USD with shipping and import, FC) is closed by other BOM changes or
reported to him. Requirement IDs: R-GEN-02, R-OPT-02.

```text
We still want enough to have crash reserve though
```

## AM-013 — 2026-11-19 — Budget test: total (crash reserve included) under $2,000
Relation: follows AM-012 after Dillon learned the crash reserve ($327.43) is already inside the BOM total. The budget
test is the hard limit only: total spend including the crash reserve <= $2,000. The derived cost rule G7 (total
<= $1,800 and +30 % growth margin >= $100, QP-3 board) is no longer a gate; it stays reported as information
(growth risk). The crash reserve must stay adequate (AM-012). Requirement IDs: R-GEN-02, R-OPT-02.

```text
Oh yes, that is fine, as long as we have enough crash reserve, the budget is fine as long as you are under the $2000 limit
```

## AM-014 — 2026-11-20 — No supplied materials; stay under the $2,000 budget
Relation: answers the T-081 budget result (full test and build purchase list $2,243-2,330 against $2,000 with the
crash reserve held). Dillon does not believe Jacobs or the team can supply the listed materials or rigs (epoxy,
glass cloth, aluminium, foam, reamers, a kN pull rig), so the program must find a way to stay under $2,000 (crash
reserve kept, AM-012/AM-013), using any model to troubleshoot. Requirement IDs: R-GEN-02, R-OPT-02, R-ORC-01.

```text
I do not believe that we have any of those available, so you must find a way to stay under budget, use whatever model to troubleshoot this
```

## AM-015 — 2026-11-20 — Resume; team phones/laptop and shop tools are free
Relation: resumes the program after the 2026-11-20 pause and answers the T-082 question. The team's own phones and
laptop may be used for testing (e.g. slow-motion video, data logging) at $0, and Jacobs shop tools (drill bits,
clamps, drill press and similar) are free to use; they are not budget lines. Materials still are (AM-014).
Requirement IDs: R-GEN-02, R-OPT-02.

```text
Resume. The team can use its own phones and laptop for testing and the shop tools are free
```

## AM-016 — 2026-11-21 — D-226: build the stronger wing; the bench test decides
Relation: answers the D-226 question (`docs/audits/2026-11-21-saddle-loadpath.md`). The landing path through the
wing torsion cell (CF bulkheads, 6061 centre torque tube, extra skin plies) is adopted although it puts A-P3 and the
fresh T/W check below their limits on the predicted mass. The limits are not relaxed: the 2026-12-15 bench test
decides, with the derate line raised to the value the as-drawn mass requires (about 0.950 EST). A failed bench test
reopens the configuration (bigger props or motors, or fallback concept B).
Requirement IDs: R-OPT-05, R-CAD-03.

```text
Stronger wing, bench test decides
```

## AM-017 — 2026-11-21 — Configuration study after T-077 part 8
Relation: answers the question after T-077 part 8 (D-226 drawn: mass, CG and budget fail; AM-016 failure branch).
Dillon approved a configuration study comparing concept A with bigger props/motors, A landing on legs or a skid,
A with a re-derived touchdown case gated by a drop test, and a re-priced concept B, each with mass, cost and the main
physics checks. Hard constraints unchanged.
Requirement IDs: R-OPT-05, R-GEN-02.

```text
Yes, run study
```

## AM-018 — 2026-11-21 — Motor swap to SunnySky X2216 880KV; crash reserve by definition
Relation: answers the two money decisions in `docs/audits/2026-11-21-config-study.md`. Dillon approves option 1-ii:
SunnySky X2216 880KV motors replace the T-Motor MN2212 KV780 in Order 1 (still no purchase before early December
2026), on the same APC 9x4.5MR props. The crash reserve follows its definition (one bad crash beyond the BOM spares: 1 pack + 1 motor + 1 servo + 1 airframe
set incl. all carbon tubes and half the PETG, x tax, + 3 shipments; `T082_data/bom_t082.py`) instead of the held AM-012
dollar value; study values $342.53 with the 25x23 rib, $287.31 with 14x12 (config study s7). Total including the reserve must stay <= $2,000.
Requirement IDs: R-GEN-02, R-OPT-02, R-OPT-05.

```text
I approve the swap and follow the definition of the reserve
```

## AM-019 — 2026-11-21 — Drop the spare fifth motor
Relation: answers the T-083 budget question (`redesign/qp/A/mechanism/out/T083_report.md` s7; BOM $2,006.66,
-$6.66). Dillon approves buying 4 X2216 V3 short-shaft motors with no BOM spare; the crash reserve (by definition,
AM-018) still covers one replacement motor. BOM total $1,981.31 incl. reserve $346.94, margin +$18.69
(`T083_data/bom_t083.py`). A spare may be re-added if the 14x12 rib passes its coupon. Check RMRC stock (backorder)
before the December order; fallback long-shaft 85810 needs a CAD check first.
Requirement IDs: R-GEN-02, R-OPT-02.

```text
Go ahead with that
```

## AM-020 — 2026-11-22 — Cost-trim study to rebuild the budget margin
Relation: answers the question after T-084 (D-233): BOM total $1,999.12 incl. crash reserve by definition, margin
+$0.88 after the hub bar T1 moved to 2.00 x 2.50 in ($65.56). Dillon approves a cost-trim study; the $2,000 total
(AM-013) stays the hard gate; no purchase before early December; no limit relaxed.
Requirement IDs: R-GEN-02, R-OPT-02.

```text
Yes, run cost-trim
```

## AM-021 — 2026-11-22 — Run T-087 (rib tube and hub-bar sourcing)
Relation: answers the question after T-086 (D-234; margin +$16.31). Dillon approves T-087: replace the R15 25x23 rib
tube with a US stock tube or built-up section, and verify hub-bar sourcing, with the design re-checks. No purchase
before early December; $2,000 total stays hard; no limit relaxed.
Requirement IDs: R-GEN-02, R-OPT-02.

```text
Yes, run T-087
```

## AM-022 — 2026-11-22 — Continue with T-085 and the review queue
Relation: answers the question after T-087 (D-235; margin +$60.83). Dillon approves continuing with T-085 (D-185 FE
upgrade, D-233 option B) and the review queue (READY rows, T-023 / T-081 re-review).
Requirement IDs: R-GEN-02, R-PHY-09.

```text
Yes, continue
```

## AM-023 — 2026-11-22 — Pause for later resumption
Relation: process instruction. Running work (T-085) stopped and saved; checkpoint in `docs/session-state.md`.
Requirement IDs: R-COM-01.

```text
Reach a good place to pause for later resumption
```

## AM-024 — 2026-11-22 — Resume after the AM-023 pause
Relation: process instruction; resumes the `docs/session-state.md` "Next action" list (T-085 first).
Requirement IDs: R-COM-01.

```text
resume
```

## AM-025 — 2026-11-22 — Continue with T-089 and the rest of the queue
Relation: answers the question after review round 3 (T-014, T-023, T-081 VERIFIED). Dillon approves continuing:
T-089 (gain margin, FC vibration of the 94.6-108.7 Hz mode), T-032, T-088, cleanup, final verification.
Requirement IDs: R-PHY-09, R-GEN-02.

```text
Yes, continue
```

## AM-026 — 2026-11-22 — Pause for later resumption
Relation: process instruction. T-089 and T-032 implementers stopped; partial T-089 work saved
(`redesign/qp/A/mechanism/out/T089_data/README-PAUSED.md`); T-032 left no file changes. Checkpoint in
`docs/session-state.md`.
Requirement IDs: R-COM-01.

```text
Reach a good place to pause for later resumption
```

## AM-027 — 2026-11-22 — Resume after the AM-026 pause
Relation: process instruction after Dillon asked what the December purchase approval is and what he needs to do now
(answer: nothing for the approval itself; before about 1 Dec the team books Tormach training, asks Jacobs about
material charges and X7 / Tormach booking, asks an ME lab for a test-frame loan, measures the Altima trunk). The
conductor rebuilds the Order 1 list for the X2216 motors (it still assumes MN2212) before December (T-090).
Requirement IDs: R-COM-01, R-GEN-02.

```text
Sounds good, resume the work you were doing before
```

## AM-028 — 2026-11-22 — Do not ask to continue between steps
Relation: communication rule (extends AM-001). The conductor moves on through the queue without asking "continue?";
it prompts Dillon only for a team decision (money, purchases, hard constraints, irreversible actions) or a real
problem.
Requirement IDs: R-COM-01, R-COM-02.

```text
Also, previously you were having me manually say continue for each step, there is no need for that, if you are good to continue, just move along. Only prompt me if you need the team's decision on something or a problem arises
```

## AM-029 — 2026-11-23 — Approve removal of the three line-ending-only worktrees
Relation: cleanup approval (T-042, batch 3; the held batch-2 items `worktree-agent-a952e…`, `claude/morph-chart-bc71a6`,
`claude/proof-chain-readable-c5026d`; branches kept).
Requirement IDs: R-REPO-04.

```text
Yes, remove them
```

## AM-030 — 2026-11-23 — Keep the current test equipment; continue the remaining tasks
Relation: test equipment decision (no press rig or testing machine bought; borrow a frame, else the TEST-PLAN lever rig); work rule (continue every task that can be done now, per AM-028).
Requirement IDs: R-GEN-02, R-COM-01.

```text
Keep what we have now, there are still over 20 tasks left so if there anything more you can do?
```

## AM-031 — 2026-11-23 — Reminder: no unnecessary text output
Relation: communication rule (re-affirms AM-001: work quietly; message only for questions, milestones, critical issues, decisions, blockers, failures, project end; 1-3 sentence milestones).
Requirement IDs: R-COM-01, R-COM-02.

```text
Also, remember what I said earlier about unnecessary text output
```

## AM-032 — 2026-11-23 — Approve pushing redesign/v1
Relation: push authorization (redesign/v1 to origin, so the published Explorer updates; this approval covers this push only).
Requirement IDs: R-REPO-04.

```text
Yeah, push it
```

## AM-033 — 2026-11-23 — Do the remaining doable deliverables (not OpenCAE); rerun the physics sims; publish the results
Relation: work order (stale MN2212 text in the Explorer; film and renders re-rendered from the current CAD; T-035 agent design loop as a concept A CLI wrapper; landing and SITL reruns at the current design; results in the Explorer and pushed to GitHub, which authorizes pushing redesign/v1 for this work); T-036 OpenCAE held by the user; lifts the "no simulation round until final" hold for this rerun.
Requirement IDs: R-INT-02, R-INT-03, R-VID-02, R-PHY-09, R-PHY-10, R-CAD-01.

```text
Don't do anything with OpenCAE yet but do the others, then rerun the physics sim and make sure to have the results available in the explored and GitHub
```

## AM-034 — 2026-11-23 — Approve design work on what the reruns flag
Relation: acknowledgement of the plan to work, on paper and at $0, on any failure the landing / SITL reruns (T-097) show (e.g. the landing ladder) before the design is called final.
Requirement IDs: R-PHY-09, R-OPT-01.

```text
Sounds good
```

## AM-035 — 2026-11-23 — Final design audit once the design is final
Relation: work order (when the design is final with what exists now, run a "final" audit on the design; distinct from the program-end T-047 / T-049, which still wait on the build and tests).
Requirement IDs: R-VER-01, R-TRK-05.

```text
Once you reach a final design with what we have now, run a "final" audit on the design
```

## AM-036 — 2026-11-23 — Close as many requirements and tasks as possible; keep working until done
Relation: work order (drive the requirement roll-up, 62 of 113 VERIFIED COMPLETE at the time, and the task ledger as far toward complete as the evidence allows; keep working without stopping; only VERIFIED COMPLETE with independent evidence counts, per the spec).
Requirement IDs: R-VER-01, R-VER-06, R-TRK-05.

```text
Right now it is at 62/113 requirements met, try to get that as complete as possible and keep working until you achieve this
```

```text
Also try to get as many tasks done as you can
```

## AM-037 — 2026-11-23 — No fabrication until after winter break; orders start early December
Relation: schedule constraint from the user (answers the T-099 F-6 go/no-go question in substance: the bench-stand build, prints, soldering and airframe fabrication move after the break; purchasing may start in early December as already planned, T-093). Supersedes the December fabrication steps of redesign/qp/A/SCHEDULE-A.md (B0, EL1, PR1) and the 2026-12-15 go/no-go date's basis.
Requirement IDs: R-GEN-07, R-GEN-02.

```text
Realistically, we will not be doing any fabrication work until after winter break, we will likely start making orders though during early december
```

## AM-038 — 2026-11-23 — Do not use dbf-hangar yet for the schema / agent tasks
Relation: answer to "Use dbf-hangar's schema and agent harness to unblock T-034 and T-015?"; T-034 (R-INT-01) and T-015 (R-ORC-04) stay BLOCKED; the DaVinci findings (T-037, docs/integration/davinci-findings.md) stand.
Requirement IDs: R-INT-01, R-ORC-04.

```text
Not yet
```

## AM-039 — 2026-11-23 — Shared agent definitions for T-015
Relation: provides the team's shared agent definitions (T-015, R-ORC-04, previously BLOCKED under AM-003): the Claude doc "DBF Agent Roles — Quick Guide", which points to `standards/agents.md` (Agent Standard v0.2) in davinciucberkeley-collab/aircraft-platform. The artifact share key in the link is redacted here under the CLAUDE.md no-secrets rule; the rest of the text is verbatim.
Requirement IDs: R-ORC-04.

```text
For T-015, here is the shared agent definitions artifact https://claude.ai/artifact/5SDz7c6h3BKfxoNowM9mAg?sk=[redacted]#19ca5749-d1f9
```

## AM-040 — 2026-11-23 — The team Agent Standard governs all future work
Relation: standing rule; makes the Agent Standard v0.2 adopted under AM-039 / T-015 mandatory for all future work in this repo (CLAUDE.md master-program rule, SessionStart brief, docs/execution-plan.md routing).
Requirement IDs: R-ORC-04, R-ORC-01.

```text
Make sure this is used for all future work in the DBF-Combined repo
```

## AM-041 — 2026-11-23 — Clean up the file layout, local and on GitHub
Relation: work order (T-104): make the repository layout cleaner and easier to follow, both the local working folder and the GitHub repo (redesign/v1); covers pushing the layout change once the gates and the Explorer pass; deletions of engineering files still need a verified purpose check (R-RULE-07) and Dillon's OK for anything not recoverable from git (R-GEN-02); run under the Agent Standard (AM-040).
Requirement IDs: R-REPO-06, R-REPO-08, R-RULE-07, R-GEN-05.

```text
Also, put on agent on cleaning up the file layout in the local folder and the github to make it cleaner and easier to follow
```

## AM-042 — 2026-11-23 — Keep the team weekly-update card current
Relation: standing rule; keep Dillon's card on the team "DBF 161 weekly updates" artifact (week 2026-12-02 and later weeks) updated as this week's tasks are completed, in bullet points and plain words for teammates who have not seen the master prompt; the week resets on Wednesdays.
Requirement IDs: R-INT-06, R-COM-04.

```text
Continue to update it as we work through this week's tasks (the week resets on Wednesdays)
```

## AM-043 — 2026-11-23 — Merge the ui-redesign-survey worktree
Relation: approval (T-104 plan decision D6): check the status of the unmerged `ui-redesign-survey` worktree (.claude/worktrees, 768 MB) and merge it; removal of the worktree afterwards keeps the branch (plan recommendation).
Requirement IDs: R-GEN-02, R-REPO-06.

```text
Yes, check its status and merge it
```

## AM-044 — 2026-11-23 — 3-D replays of the simulation results in the Explorer
Relation: work order (T-105): add 3-D visualisations of the physics-simulation results to the Explorer's existing Simulations view: flight replay of the SITL runs (model, elevons, props, trail, timeline, synced plots, case picker), landing replay of the touchdown cases, elevon linkage sweep; labelled as playback of simulation output (R-PHY-06); after T-101 and T-104 land.
Requirement IDs: R-PHY-10, R-INT-05, R-PHY-06.

```text
Yes, add them
```

## AM-045 — 2026-11-23 — DaVinci API documentation
Relation: input to T-037 / R-INT-04 (answers findings question 1, which product: the DaVinci app, docs at docs.davinci-app.com); access, account and spend cap still open (AM-003 $0 stands).
Requirement IDs: R-INT-04.

```text
Here is a link to the Davinci API instructions https://docs.davinci-app.com/pages/api/introduction
```

## AM-046 — 2026-11-23 — Use the DaVinci "API Test" project; start the research
Relation: work order (T-037): use the design-build-fly organization's DaVinci project "API Test" (id b53fed82-b072-43c2-9994-de76de845d93) for the DaVinci work instead of the personal "Test" project; work on scratch branches, never `main`; start the $0 research: data mapping to DaVinci object types, capability inventory (tools, simulation types), Claude connector (MCP) check, public pricing.
Requirement IDs: R-INT-04.

```text
Yes, use API Test and start the research
```

## AM-047 — 2026-11-23 — Import the current design into DaVinci to verify the workflow
Relation: work order (T-037): import what exists so far (committed concept A data, labelled as a snapshot because T-101 is still changing numbers) into the DaVinci "API Test" project on a scratch branch, committed so Dillon can open and check it in the DaVinci web app; $0 pattern (no agent prompts), usage read before and after.
Requirement IDs: R-INT-04.

```text
Could you import what we have don so far into davinci so that I can verify that it actually does work
```

## AM-048 — 2026-11-23 — Show the 3-D model in DaVinci
Relation: work order (T-037): on the API Test snapshot branch, (1) upload the exported concept A model (concept-a.opt.glb, the gated GLB), (2) create a DaVinci Page that shows it in the DavinciViewer (or give Dillon the steps if pages cannot be created over the API), (3) add the individual CAD parts with their masses as part objects; $0 pattern (no agent prompts), usage read before and after.
Requirement IDs: R-INT-04.

```text
Do all three
```

## AM-049 — 2026-11-23 — One-part STEP test in DaVinci
Relation: work order (T-037): convert one concept A part (the 6061 hub CGE-001) from the gated GLB to a faceted STEP file, upload it to the API Test snapshot branch, and find out whether DaVinci turns it into a geometry object with a 3-D view (else create a geometry of kind step pointing at it, or prepare the file for a drag-in); $0 pattern.
Requirement IDs: R-INT-04.

```text
Yes, do the one-part STEP test
```

## AM-050 — 2026-11-24 — DaVinci branch clean-up deferred; continue the main work
Relation: Dillon will delete the DaVinci API Test branch `concept-a-snapshot-73656c93` later (836 MB of the org's 1 GB storage); no further DaVinci uploads until storage is confirmed freed; resume the queued T-101 / T-105 / T-104 / final-verification work.
Requirement IDs: R-INT-04, R-VER-01.

```text
I'll work on that later, continue with the work you were doing before
```

## AM-051 — 2026-11-24 — Agent Standard counts for the Superpowers half of R-GEN-01
Relation: team decision on R-GEN-01: the mandatory team Agent Standard v0.2 (AM-040: roles, briefs, fresh reviewer per batch, cheapest tier first) counts in place of Superpowers skill use for planning, implementation and testing; the Impeccable half was already met (T-053). R-GEN-01 may be closed on that basis; no Superpowers use is claimed.
Requirement IDs: R-GEN-01, R-ORC-04.

```text
Yes, count it
```

## AM-052 — 2026-11-24 — Combine the Agent Standard and the Superpowers skills
Relation: work order: the Superpowers skills run inside the Agent Standard roles (the roles say who, the skills say how), mapped in `docs/reference/agent-standard/LOCAL.md` with conflict rules (roles only, AM-028, minimize compute); each phase logs the skill used (R-GEN-01); one line in CLAUDE.md; push 73daed39 and this change to redesign/v1.
Requirement IDs: R-GEN-01, R-GEN-02, R-ORC-04.

```text
Yes, write it in and push
```

## AM-053 — 2026-11-24 — Work on the elevon cruise trim
Relation: work order (T-101): take the next D-252 rung, cutting the elevon cruise trim (6.4 deg) by wing reflex and / or CG so pitch use (CL-A-PITCH-USE 0.651 vs 0.60) and the roll / gust reserve fit inside the elevon stops.
Requirement IDs: R-PHY-10, R-OPT-01.

```text
Work on the elevon cruise trim
```

## AM-054 — 2026-11-24 — Back to the DaVinci API work
Relation: work order (T-037): resume the DaVinci API work from 2026-11-23 (storage after the branch delete, usage re-read, lighter re-import); the T-101 trim SITL batch continues in the background.
Requirement IDs: R-INT-04.

```text
Lets get back to working on the DaVinci API that we were looking at last night
```

## AM-055 — 2026-11-24 — Delete the DaVinci snapshot branch via the API
Relation: Dillon created a projects:manage token (in the git-ignored .env as DAVINCI_API_KEY_MANAGE) and approved deleting only the API Test branch `concept-a-snapshot-73656c93` (the UI delete failed); check storage afterwards.
Requirement IDs: R-INT-04, R-GEN-02.

```text
token's in, delete the snapshot branch
```

## AM-056 — 2026-11-24 — Delete the API Test project and start a new DaVinci project
Relation: Dillon deletes the DaVinci project API Test himself (its main branch holds only the default Library and Model packages; the snapshot branch content is reproducible from tools/davinci_*.py), then creates a new project; Claude checks the organization storage before any upload, then runs the lighter re-import (data first, one subsystem STEP measured before the rest).
Requirement IDs: R-INT-04.

```text
Yes, I'll delete it
```

## AM-057 — 2026-11-24 — Derive the roll and gust requirement
Relation: work order (T-101): derive the cruise roll-rate requirement (A-P11, 90 deg/s has no derivation) and the gust case from the mission (racetrack turns, reversals, site wind) instead of waiting for a team pick (derived requirements are the engineering team's; memory "derived requirements are ours"), then re-check the elevon reserve and pitch-use claim against it.
Requirement IDs: R-PHY-10, R-OPT-01.

```text
Yes, derive the roll and gust requirement
```

## AM-058 — 2026-11-24 — DaVinci storage raised to 50 GB
Relation: information from Dillon (Celedon raised the account storage); with 50 GB the T-037 import uses the full-detail per-part STEP set (129 parts, CAD fidelity) instead of the lighter per-subsystem set planned under AM-056.
Requirement IDs: R-INT-04.

```text
It says we should have 50GB of storage now
```

## AM-059 — 2026-11-24 — Finish T-101: tune, check, adopt
Relation: work order (T-101): (1) tune the cruise roll overshoot that put an elevon on the stop in the D-254 bank reversal (SITL); (2) run the checks the D-254 configuration depends on (mission energy and BATT_LOW at 18 m/s, AIRSPEED_MAX, hover and landing at CG 23.49 mm, run_all); (3) adopt the configuration in params-A.json / A.param, amend A-P11 to the derived requirement, independent review.
Requirement IDs: R-PHY-10, R-OPT-01.

```text
Yes, go ahead with all three
```

## AM-060 — 2026-11-24 — Drop the Lua spin-cap script
Relation: design simplification: `spin_cap.lua` sets Q_M_SPIN_MAX 1.0 on every path (table 1.0, failsafe 1.0) since the X2216 motors (D-227), the value A.param already holds; remove it from the build, the bench test TP-2 and the SITL batches; Q_M_BAT_CURR_MAX 72 A stays the current protection.
Requirement IDs: R-PHY-08, R-GEN-08.

```text
Yes, drop the Lua script
```

## AM-061 — 2026-11-24 — Rerun the landing and windy hover at the new CG
Relation: work order (T-101 residual, review R-D255-3): re-run the C5 landing model and a windy hover SITL at the D-255 CG 23.49 mm (pack at the aft end of the tray slot) and compare with their limits.
Requirement IDs: R-PHY-10, R-VER-01.

```text
Yes, rerun the landing and windy hover
```

## AM-062 — 2026-11-24 — Rerun the A-P8 hover-wind checks for the current aircraft
Relation: work order (D-257 gap): give the hover plant the X2216 + APC 9x4.5MR thrust model and re-run the A-P8 wind cases (4 m/s mean, turbulence, gust; output above 0.85, time at full output, lean) at 1.881 kg and arm 1.2, then update CL-A-WIND-OUTPUT / -CAP / -LEAN.
Requirement IDs: R-PHY-08, R-VER-01.

```text
Yes, rerun A-P8
```

## AM-063 — 2026-11-24 — DaVinci cost accepted and workflow approved
Relation: Dillon accepts the measured near-zero DaVinci cost (per-object embedding / indexing charges, under one cent in total for the Concept A imports; no AI chat spend), replacing AM-003's $0 line for this work, and approves the workflow: after each design change Claude pushes the current design data to a new snapshot branch in project Concept A, with 3-D parts and the lite whole-aircraft model only when geometry changes; DaVinci's AI agent is never used; main is changed only on purpose.
Requirement IDs: R-INT-04.

```text
Yes, I accept the cost and approve the workflow
```
