# Task ledger — master program

Append-only: never delete a row; superseded tasks keep their row with `EXPLICITLY DEFERRED` and a note.
Statuses: NOT STARTED · IN PROGRESS · BLOCKED · FAILED · READY FOR REVIEW · VERIFIED COMPLETE · EXPLICITLY DEFERRED.
Only VERIFIED COMPLETE counts, and only with evidence that someone other than the implementer checked.
Owner/model: C conductor (Opus main), H haiku, S sonnet, O opus reviewer, D Dillon.
Audit: `python -I tools/ledger_audit.py` (columns must stay in this order).

| ID | Parent | Description | Deps | Owner/model | Deliverable | Acceptance | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| T-001 | R-PRES-01 | Save pasted spec verbatim | — | C | docs/MASTER_PROJECT_SPEC.md | byte-equal to paste, committed | — | IN PROGRESS |
| T-002 | R-PRES-02, R-RULE-01 | Seal spec + amendments (SHA-256), audit tool checks it | T-001 | C | tools/ledger_audit.py, docs/spec-integrity.sha256 | tampered copy → audit FAIL | — | IN PROGRESS |
| T-003 | R-PRES-03 | Append-only amendments file with AM-001 verbatim | T-001 | C | docs/spec-amendments.md | AM-001 text equals paste | — | IN PROGRESS |
| T-004 | R-PRES-04, R-REPO-06, R-COM-01, R-COM-02, R-COM-04, R-COM-05, R-COM-06 | CLAUDE.md: spec pointer, recovery rule, communication protocol; keep concise | T-001 | C | CLAUDE.md | headless session reports rules + spec path | — | IN PROGRESS |
| T-005 | R-PRES-05, R-MON-01, R-MON-04, R-PRES-10 | Create the eight management files (+ session-log, model-usage) | — | C | docs/*.md | all present, sections filled | — | IN PROGRESS |
| T-006 | R-PRES-06, R-PRES-07, R-PRES-08, R-PRES-09 | Hooks: PreCompact, PostCompact, SessionStart(startup/resume/compact/clear) | T-005 | C | .claude/settings.json, .claude/hooks/recovery.py | hook unit run prints brief, logs events | — | IN PROGRESS |
| T-007 | R-PRES-11 | Controlled manual compaction test (headless resumed session + /compact) | T-006 | C | docs/verification-report.md §Recovery | Pre/PostCompact + SessionStart(compact) logged; agent names active task | — | NOT STARTED |
| T-008 | R-PRES-12 | New-session recovery test | T-006 | C | docs/verification-report.md §Recovery | agent names spec path + active task | — | NOT STARTED |
| T-009 | R-TRK-01 | Requirements registry | T-001 | C | docs/requirements.md | covers spec §1–13, rules, AM-001 | — | READY FOR REVIEW |
| T-010 | R-TRK-02, R-TRK-03 | Task ledger + automated traceability audit | T-009 | C | this file, tools/ledger_audit.py | audit exits 0; broken copy exits 1 | — | IN PROGRESS |
| T-011 | R-TRK-05, R-TRK-01 | Independent registry-vs-spec audit (haiku accounting) | T-009 | H | verification-report §Audits | list of missing/merged requirements, fixed | — | NOT STARTED |
| T-012 | R-TRK-04, R-TRK-06, R-ORC-03, R-MON-02, R-MON-03 | Write task protocol, delegation rules, stall/failure rules into execution-plan | T-009 | C | docs/execution-plan.md | rules present | — | IN PROGRESS |
| T-013 | R-ORC-01, R-ORC-02, R-COM-03 | Agent definitions with model routing + concise return format | — | C | .claude/agents/*.md | one haiku agent run shows model + format | — | IN PROGRESS |
| T-014 | R-ORC-05, R-RULE-04 | Model-usage log | T-013 | C | docs/model-usage.md | one row per delegation | — | IN PROGRESS |
| T-015 | R-ORC-04 | Locate James's shared agent definitions | — | D | location or "absent" note | adopted or recorded | repo + ~/.claude/agents searched 2026-11-18: none | BLOCKED |
| T-016 | R-CAD-01, R-PHY-01 | Capability audit: concept A CAD, mechanisms, wiring, and every analysis traced to the code/solver that computes it | — | S | docs/capability-audit.md | each item has evidence path; O spot-checks 3 | — | NOT STARTED |
| T-017 | R-PHY-02, R-PHY-06 | Relabel "physics" claims that are static collision/interference only | T-016 | S | doc edits + list | grep finds no mislabel | — | NOT STARTED |
| T-018 | R-CAD-02, R-PHY-03 | Elevon linkage kinematics from CAD geometry (servo arm → pushrod → horn → hinge), full range | T-016 | S | analysis script + record | residual < 1e-6, range and ratio vs servo limits, no over-centre | — | NOT STARTED |
| T-019 | R-PHY-04 | Rigid-body dynamics of one important mechanism/event (frictionless first) | T-018 | S | script + record | energy/constraint checks; pass/fail vs limits | — | NOT STARTED |
| T-020 | R-PHY-05 | Swept collision through the elevon range against CAD meshes | T-018 | S | script + record | min clearance ≥ limit over sweep | — | NOT STARTED |
| T-021 | R-PHY-07 | Analysis records template + entries | T-018 | S | docs/analysis-records.md | ten fields per record | — | NOT STARTED |
| T-022 | R-CAD-03, R-CAD-04, R-CAD-05 | Close CAD realism gaps found by T-016 (mounts, fasteners, wiring, clearances) | T-016 | S | CAD + gate run | 3-D gates green | — | NOT STARTED |
| T-023 | R-CAD-06 | Independent CAD consistency review | T-022 | O | review record | no unexplained inconsistency | — | NOT STARTED |
| T-024 | R-OPT-01, R-RULE-06 | Failure-resolution ladder + trade template in engineering-decisions | — | C | docs/engineering-decisions.md | ladder present | — | IN PROGRESS |
| T-025 | R-OPT-02, R-OPT-03, R-OPT-04, R-OPT-05 | Retro-review of D-202…D-210 material-adding fixes with ladder + trades | T-024 | O | review in engineering-decisions | findings → new D-entries | — | NOT STARTED |
| T-026 | R-VID-01 | Video pipeline audit (concept A film, K09-L films, Blender scripts) | — | S | docs/video/PIPELINE-AUDIT.md | all §7.1 items covered | — | NOT STARTED |
| T-027 | R-VID-02, R-VID-03, R-VID-04, R-VID-06, R-VID-07 | Demo film: six scenes from current concept A CAD, 1080p60, materials/lights, eased cameras; preview first | T-026 | S | render script + preview contact sheet | preview reviewed before full render | — | NOT STARTED |
| T-028 | R-VID-05, R-VID-09, R-RULE-05 | Drive mechanism motion from T-018 output; tag SIMULATED vs ILLUSTRATIVE | T-018, T-027 | S | render script | every motion shot tagged | — | NOT STARTED |
| T-029 | R-VID-08 | Overlays from analysis records only | T-021, T-027 | S | overlay layer | every number traces to a record | — | NOT STARTED |
| T-030 | R-VID-10 | Independent frame + film review, iterate | T-027 | O | review log | defects closed | — | NOT STARTED |
| T-031 | R-VID-11, R-VID-12, R-VID-13 | Export main (60–120 s), highlight (20–30 s), mechanism clips | T-030 | S | mp4 files | ffprobe durations/res/fps in range | — | NOT STARTED |
| T-032 | R-VID-14 | Pipeline doc + improvements summary | T-031 | H | docs/video/PIPELINE.md | reproducible | — | NOT STARTED |
| T-033 | R-VID-15, R-RULE-10 | Playback verification (full decode) + visual sign-off | T-031 | O | verification-report §Video | 0 decode errors | — | NOT STARTED |
| T-034 | R-INT-01 | Get shared aircraft schema location/spec from team | — | D | schema path | concept A round-trips | not in repo 2026-11-18 | BLOCKED |
| T-035 | R-INT-02 | Agent design loop over concept A scripts (load, modify, test, compare, save, evidence) | T-034 | S | CLI wrapper or team CLI adapter | one end-to-end run | — | NOT STARTED |
| T-036 | R-INT-03 | OpenCAE: which concept A analyses it can run; run one | T-035 | S | run log | case runs or reason recorded | — | NOT STARTED |
| T-037 | R-INT-04 | DaVinci API investigation and workflow attempt | access + cost approval | D | docs/integration/DAVINCI.md | attempt logged with cost | needs credentials + spend approval | BLOCKED |
| T-038 | R-INT-05, R-RULE-07 | Keep results inside the existing Explorer; no new dashboards | — | C | diff review | no new interface | — | IN PROGRESS |
| T-039 | R-INT-06 | Weekly report from ledger into existing status page | T-005 | H | report | produced once | — | NOT STARTED |
| T-040 | R-REPO-01, R-REPO-10 | Initial inventory + baseline sizes/metrics | — | H | docs/repository-audit.md §Baseline | commands + numbers | — | IN PROGRESS |
| T-041 | R-REPO-02, R-REPO-03 | Classify candidates; dry-run cleanup plan; ask approval for deletions | T-040 | S/D | repository-audit §Candidates | plan approved | — | NOT STARTED |
| T-042 | R-REPO-04, R-REPO-07 | Execute approved batches on cleanup branch; .gitignore regenerables | T-041 | S | commits | regression green after each batch | — | NOT STARTED |
| T-043 | R-REPO-05, R-RULE-08 | Performance benchmarks before/after (collision gate, render, Explorer load) | T-040 | S | repository-audit §Benchmarks | measured with commands | — | NOT STARTED |
| T-044 | R-REPO-08 | Post-cleanup regression suite | T-042 | H | log | all green | — | NOT STARTED |
| T-045 | R-REPO-09 | Complete repository-audit report (12 sections) | T-044 | H | docs/repository-audit.md | all sections | — | IN PROGRESS |
| T-046 | R-PLAN-01 | Execution plan, phases 1–8 with deps | T-009 | C | docs/execution-plan.md | every R-id in a phase | — | IN PROGRESS |
| T-047 | R-VER-01, R-VER-02, R-VER-03, R-VER-04, R-VER-05, R-VER-06, R-RULE-02, R-RULE-03, R-RULE-09 | Independent final verification | all | O | verification-report §Final | per-requirement table + stats | — | NOT STARTED |
| T-048 | R-TRK-05 | Milestone audits (phase ends, after recovery) | T-011 | H/O | verification-report §Audits | dated entry per milestone | — | NOT STARTED |
