# Milestone fixes applied 2026-11-23 (change list)

Source: `docs/audits/2026-11-23-milestone-audit.md` (sections 2.2, 2.3, 3.1-3.4, 5), applied exactly with the conductor decisions.
Not edited: `docs/MASTER_PROJECT_SPEC.md`, `docs/spec-amendments.md`. Nothing committed. Nothing marked VERIFIED COMPLETE.
Line numbers are as of the end of this pass (ledger and requirements: one table row per line; ledger cell named in brackets, 0-based: 1 Parent, 3 Deps, 6 Acceptance, 7 Evidence, 8 Status).

Decisions: S-3 as the T-047 Acceptance append (no T-094..T-099 per R-VER); audit fix 6 (T-095) skipped; S-6 handled by T-051 READY FOR REVIEW. The audit named the new free-play row T-094, so that id was used.

| Fix id | File:line |
|---|---|
| S-1 | `docs/task-ledger.md:54 (T-044 col Parent)` |
| S-1 | `docs/task-ledger.md:57 (T-047 col Parent)` |
| A-1 | `docs/task-ledger.md:57 (T-047 col Parent)` |
| A-1 | `docs/task-ledger.md:85 (T-075 col Parent)` |
| A-2 | `docs/task-ledger.md:92 (T-082 col Parent)` |
| A-2 | `docs/task-ledger.md:96 (T-086 col Parent)` |
| A-2 | `docs/task-ledger.md:97 (T-087 col Parent)` |
| A-2 | `docs/task-ledger.md:103 (T-093 col Parent)` |
| A-2 | `docs/task-ledger.md:93 (T-083 col Parent)` |
| S-5 | `docs/task-ledger.md:59 (T-049 col Parent)` |
| S-3 | `docs/task-ledger.md:57 (T-047 col 6)` |
| S-4 | `docs/task-ledger.md:69 (T-059 col 6)` |
| A-6 | `docs/task-ledger.md:51 (T-041 col 7)` |
| 3.2 | `docs/task-ledger.md:26 (T-016 col 7)` |
| 3.2 | `docs/task-ledger.md:26 (T-016 col 8)` |
| 3.2 | `docs/task-ledger.md:27 (T-017 col 7)` |
| 3.2 | `docs/task-ledger.md:27 (T-017 col 8)` |
| 3.2 | `docs/task-ledger.md:36 (T-026 col 7)` |
| 3.2 | `docs/task-ledger.md:36 (T-026 col 8)` |
| 3.2 | `docs/task-ledger.md:84 (T-074 col 7)` |
| 3.2 | `docs/task-ledger.md:84 (T-074 col 8)` |
| 3.2 | `docs/task-ledger.md:41 (T-031 col 7)` |
| 3.2 | `docs/task-ledger.md:73 (T-063 col 7)` |
| 3.2 | `docs/task-ledger.md:85 (T-075 col 7)` |
| 3.2 | `docs/task-ledger.md:21 (T-011 col 7)` |
| 3.3 T-077 / F-13 (Status, Evidence dedupe + append) | `docs/task-ledger.md:87 (T-077 col 7-8)` |
| 3.3 T-083 / F-13 (Status, Deps, Evidence dedupe + append) | `docs/task-ledger.md:93 (T-083 col 3,7,8)` |
| 3.3 T-061 | `docs/task-ledger.md:71 (T-061 col 7)` |
| 3.3 T-061 | `docs/task-ledger.md:71 (T-061 col 8)` |
| 3.3 T-061 new row T-094 | `docs/task-ledger.md:104 (T-094)` |
| 3.3 T-076 | `docs/task-ledger.md:86 (T-076 col 7)` |
| 3.3 T-078 | `docs/task-ledger.md:88 (T-078 col 7)` |
| 3.3 T-015 | `docs/task-ledger.md:25 (T-015 col 7)` |
| 3.3 T-004 | `docs/task-ledger.md:14 (T-004 col 7)` |
| 3.3 T-004 | `docs/task-ledger.md:14 (T-004 col 8)` |
| 3.3 T-038 | `docs/task-ledger.md:48 (T-038 col 7)` |
| 3.3 T-040 | `docs/task-ledger.md:50 (T-040 col 7)` |
| 3.3 T-040 | `docs/task-ledger.md:50 (T-040 col 8)` |
| 3.3 T-088 | `docs/task-ledger.md:98 (T-088 col 7)` |
| 3.3 T-088 | `docs/task-ledger.md:98 (T-088 col 8)` |
| 5.5 | `docs/task-ledger.md:92 (T-082 col 7)` |
| 5/T-048 | `docs/task-ledger.md:58 (T-048 col 7)` |
| 5/T-048 | `docs/task-ledger.md:58 (T-048 col 8)` |
| 5/T-055 | `docs/task-ledger.md:65 (T-055 col 7)` |
| 5/T-055 | `docs/task-ledger.md:65 (T-055 col 8)` |
| 5/T-051 | `docs/task-ledger.md:61 (T-051 col 7)` |
| 5/T-051 | `docs/task-ledger.md:61 (T-051 col 8)` |
| 5/T-050 | `docs/task-ledger.md:60 (T-050 col 7)` |
| 5/T-050 | `docs/task-ledger.md:60 (T-050 col 8)` |
| S-1/A-1/A-2 new row R-GEN-05 | `docs/requirements.md:41` |
| S-1/A-1/A-2 new row R-GEN-06 | `docs/requirements.md:42` |
| S-1/A-1/A-2 new row R-GEN-07 | `docs/requirements.md:43` |
| S-1/A-1/A-2 new row R-GEN-08 | `docs/requirements.md:44` |
| S-2 | `docs/requirements.md:122 (R-INT-02 col 3)` |
| A-3 | `docs/requirements.md:97 (R-OPT-05 col 3)` |
| A-4 | `docs/requirements.md:185 (R-COM-02 col 3)` |
| 5.4 | `docs/requirements.md:38 (R-GEN-02 col 3)` |
| 5.4 | `docs/requirements.md:133 (R-REPO-03 col 3)` |
| S-5 | `docs/requirements.md:138 (R-REPO-08 col 8)` |
| S-5 | `docs/requirements.md:138 (R-REPO-08 col 9)` |
| 3.1 roll-up R-PRES-01: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:19` |
| 3.1 roll-up R-PRES-02: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:20` |
| 3.1 roll-up R-PRES-03: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:21` |
| 3.1 roll-up R-PRES-05: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:23` |
| 3.1 roll-up R-PRES-06: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:24` |
| 3.1 roll-up R-PRES-07: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:25` |
| 3.1 roll-up R-PRES-08: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:26` |
| 3.1 roll-up R-PRES-09: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:27` |
| 3.1 roll-up R-PRES-10: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:28` |
| 3.1 roll-up R-PRES-11: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:29` |
| 3.1 roll-up R-PRES-12: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:30` |
| 3.1 roll-up R-PRES-13: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:32` |
| 3.1 roll-up R-GEN-04: NOT STARTED -> IN PROGRESS | `docs/requirements.md:40` |
| 3.1 roll-up R-TRK-01: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:49` |
| 3.1 roll-up R-TRK-02: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:50` |
| 3.1 roll-up R-TRK-03: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:51` |
| 3.1 roll-up R-TRK-04: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:52` |
| 3.1 roll-up R-TRK-05: NOT STARTED -> IN PROGRESS | `docs/requirements.md:53` |
| 3.1 roll-up R-TRK-06: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:54` |
| 3.1 roll-up R-ORC-01: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:59` |
| 3.1 roll-up R-ORC-02: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:60` |
| 3.1 roll-up R-ORC-03: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:61` |
| 3.1 roll-up R-ORC-05: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:63` |
| 3.1 roll-up R-CAD-01: NOT STARTED -> IN PROGRESS | `docs/requirements.md:68` |
| 3.1 roll-up R-CAD-02: NOT STARTED -> IN PROGRESS | `docs/requirements.md:69` |
| 3.1 roll-up R-CAD-03: NOT STARTED -> IN PROGRESS | `docs/requirements.md:70` |
| 3.1 roll-up R-CAD-04: NOT STARTED -> IN PROGRESS | `docs/requirements.md:71` |
| 3.1 roll-up R-CAD-05: NOT STARTED -> IN PROGRESS | `docs/requirements.md:72` |
| 3.1 roll-up R-CAD-06: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:73` |
| 3.1 roll-up R-PHY-01: NOT STARTED -> IN PROGRESS | `docs/requirements.md:78` |
| 3.1 roll-up R-PHY-02: NOT STARTED -> IN PROGRESS | `docs/requirements.md:79` |
| 3.1 roll-up R-PHY-03: NOT STARTED -> IN PROGRESS | `docs/requirements.md:80` |
| 3.1 roll-up R-PHY-04: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:81` |
| 3.1 roll-up R-PHY-05: NOT STARTED -> IN PROGRESS | `docs/requirements.md:82` |
| 3.1 roll-up R-PHY-06: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:83` |
| 3.1 roll-up R-PHY-07: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:84` |
| 3.1 roll-up R-PHY-08: NOT STARTED -> IN PROGRESS | `docs/requirements.md:85` |
| 3.1 roll-up R-PHY-09: NOT STARTED -> IN PROGRESS | `docs/requirements.md:86` |
| 3.1 roll-up R-PHY-10: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:87` |
| 3.1 roll-up R-PHY-11: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:88` |
| 3.1 roll-up R-OPT-02: NOT STARTED -> IN PROGRESS | `docs/requirements.md:94` |
| 3.1 roll-up R-OPT-03: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:95` |
| 3.1 roll-up R-OPT-04: NOT STARTED -> IN PROGRESS | `docs/requirements.md:96` |
| 3.1 roll-up R-OPT-05: NOT STARTED -> IN PROGRESS | `docs/requirements.md:97` |
| 3.1 roll-up R-VID-01: VERIFIED COMPLETE -> IN PROGRESS | `docs/requirements.md:102` |
| 3.1 roll-up R-VID-14: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:115` |
| 3.1 roll-up R-INT-06: NOT STARTED -> IN PROGRESS | `docs/requirements.md:126` |
| 3.1 roll-up R-REPO-02: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:132` |
| 3.1 roll-up R-REPO-03: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:133` |
| 3.1 roll-up R-REPO-04: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:134` |
| 3.1 roll-up R-REPO-05: NOT STARTED -> IN PROGRESS | `docs/requirements.md:135` |
| 3.1 roll-up R-REPO-07: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:137` |
| 3.1 roll-up R-REPO-09: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:139` |
| 3.1 roll-up R-REPO-10: NOT STARTED -> IN PROGRESS | `docs/requirements.md:140` |
| 3.1 roll-up R-MON-01: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:145` |
| 3.1 roll-up R-MON-02: NOT STARTED -> IN PROGRESS | `docs/requirements.md:146` |
| 3.1 roll-up R-MON-04: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:148` |
| 3.1 roll-up R-PLAN-01: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:153` |
| 3.1 roll-up R-RULE-05: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:174` |
| 3.1 roll-up R-RULE-10: NOT STARTED -> VERIFIED COMPLETE | `docs/requirements.md:179` |
| 3.1 roll-up R-COM-03: IN PROGRESS -> VERIFIED COMPLETE | `docs/requirements.md:186` |
| F-9 phases table phase 4 row | `docs/execution-plan.md:12` |
| F-9 phases table new 4b row | `docs/execution-plan.md:13` |
| F-9 assignment table phase 4 row + new 4b row | `docs/execution-plan.md:12-72` |
| S-1 R-GEN-05 in phase 2 row | `docs/execution-plan.md:69` |
| S-5 R-REPO-08 owned by T-049 (phase 7 row) | `docs/execution-plan.md:75` |
| S-1 / A-1 R-GEN-05, R-GEN-06 in phase 8 row | `docs/execution-plan.md:76` |
| A-2 R-GEN-06/07/08 in the new 4b assignment row | `docs/execution-plan.md:72` |
| F-10 | `docs/verification-report.md:32` |
| F-10 | `docs/verification-report.md:69` |
| 5.1 session-state heading (AM-001..AM-030 in force) | `docs/session-state.md:15` |
| 5.1 session-state Goal line AM-001..AM-030 | `docs/session-state.md:18` |
| F-11 Known dependency gaps | `docs/session-state.md:41` |
| F-14 / 5.2 worktree row (answered AM-029) | `docs/session-state.md:60` |
| F-14 board-choice row (answered AM-005, AM-006, AM-009) | `docs/session-state.md:63` |
| F-14 new row AM-018 motor swap | `docs/session-state.md:64` |
| F-14 new row AM-019 drop spare motor | `docs/session-state.md:65` |
| F-14 / 5.2 new row AM-030 test equipment | `docs/session-state.md:66` |
| 5.3 Reconciliation AM-029 / AM-030 | `docs/session-state.md:74` |
| A-5 Reconciliation AM-004 lapsed | `docs/session-state.md:75` |
| F-12 Reconciliation spec_guard line (spec-amendments.md not edited) | `docs/session-state.md:76` |
| Reconciliation: audit fixes applied note | `docs/session-state.md:77` |
| 3.3 T-039 model-usage row | `docs/model-usage.md:117` |
| 5.5 TEST-PLAN-O4B "(AM-030: not bought)" | `redesign/qp/A/TEST-PLAN-O4B.md:287` |
| Roll-up script written | `docs/audits/2026-11-23-rollup_check.py` |

## Roll-up recompute (script `docs/audits/2026-11-23-rollup_check.py`)

Roll-up output (rule: VERIFIED only if every carrying task is VERIFIED COMPLETE or EXPLICITLY DEFERRED; standing rules R-RULE-01/04/06/08, R-MON-02/03 stay IN PROGRESS):
```
113 requirement rows; 6 mismatch(es)
  R-GEN-01: requirements.md says 'IN PROGRESS', roll-up says 'NOT STARTED'; tasks [('T-053', 'NOT STARTED')]
  R-GEN-08: requirements.md says 'IN PROGRESS', roll-up says 'BLOCKED'; tasks [('T-083', 'BLOCKED')]
  R-PHY-05: requirements.md says 'IN PROGRESS', roll-up says 'VERIFIED COMPLETE'; tasks [('T-020', 'VERIFIED COMPLETE'), ('T-061', 'EXPLICITLY DEFERRED'), ('T-063', 'VERIFIED COMPLETE')]
  R-RULE-02: requirements.md says 'IN PROGRESS', roll-up says 'NOT STARTED'; tasks [('T-047', 'NOT STARTED')]
  R-RULE-03: requirements.md says 'IN PROGRESS', roll-up says 'NOT STARTED'; tasks [('T-047', 'NOT STARTED')]
  R-RULE-09: requirements.md says 'IN PROGRESS', roll-up says 'NOT STARTED'; tasks [('T-047', 'NOT STARTED')]
```
Remaining mismatches, kept deliberately:
- R-GEN-01 (IN PROGRESS, T-053 NOT STARTED): Superpowers is in use; row is ongoing.
- R-GEN-08 (IN PROGRESS, T-083 BLOCKED): conductor decision IN PROGRESS; physics at predicted mass is ongoing.
- R-PHY-05 (IN PROGRESS; rule says VERIFIED now that T-061 is EXPLICITLY DEFERRED): conductor decision; residual CL-A-LINKAGE-FREEPLAY carried to T-094.
- R-RULE-02, R-RULE-03, R-RULE-09 (IN PROGRESS, only T-047 NOT STARTED): final-audit rules, ongoing until T-047.

Deviations from the audit's 3.1 flip list: R-CAD-01, R-PHY-01, R-PHY-02 left IN PROGRESS because T-016 / T-017 are now READY FOR REVIEW (3.2); R-VID-01 VERIFIED -> IN PROGRESS because T-026 is now READY FOR REVIEW; R-TRK-05, R-INT-06, R-REPO-05, R-REPO-10 NOT STARTED -> IN PROGRESS (their tasks T-048, T-039, T-051, T-040 are now READY FOR REVIEW); R-MON-02 NOT STARTED -> IN PROGRESS (standing rule). R-PHY-03 IN PROGRESS also because T-094 is NOT STARTED.

## Gates
- `python -I tools/ledger_audit.py` (exit 0): 113 requirements, 94 tasks, {'VERIFIED COMPLETE': 62, 'READY FOR REVIEW': 11, 'BLOCKED': 7, 'NOT STARTED': 8, 'IN PROGRESS': 2, 'EXPLICITLY DEFERRED': 4}; 0 errors
- `python -I tools/plan_rid_check.py` (exit 0): 113 R-ids, 0 missing from execution-plan.md
