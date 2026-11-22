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
