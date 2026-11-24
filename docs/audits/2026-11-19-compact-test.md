# Manual compaction test (T-007, R-PRES-11, spec 1.6) — 2026-11-19

Method: Dillon typed `/compact` in the desktop session `7cb35b0a`; this record was written afterwards from the session transcript (`7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f.jsonl`, lines cited as `L<n>`, timestamps UTC; local time is UTC-8). Excerpts are short; no transcript chunks pasted. Category: process verification (not an engineering analysis).

## Timeline
| UTC | Local | Event | Source |
|---|---|---|---|
| 08:51:19 | 00:51:19 | `/compact` command (manual) | transcript L1647-1648; `docs/session-log.md` PreCompact trigger=manual 00:51:20 |
| 08:52:08 | 00:52:08 | `compact_boundary` "Conversation compacted"; SessionStart(compact) and PostCompact hooks completed | L1645, L1649; session-log 00:52:08 (two events) |
| 09:41:36 | 01:41:36 | next user message: "What would installing ffmpeg benefit?" (user was away about 49 min) | L1668-1670 |
| 09:41:43 | 01:41:43 | first assistant turn after compaction (L1696), first tool call 09:41:45: a Grep for `PD-006` in `docs/` | L1697 |
| 09:41:55 | 01:41:55 | first text answer (L1713); then "Okay go ahead with that" (09:42:27, L1717) and the install | L1713, L1717 |

## The seven checks (spec 1.6)
| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Spec exists and is found | PASS | SessionStart(compact) hook output injected at 08:52:08 (L1662): "DBF master program recovery (docs/ is the source of truth; a compaction summary is NOT authoritative)", "Missing state files: none". After the next turns, `python -I tools/ledger_audit.py` at 09:43:52 printed "0 errors" (L1771), which includes the spec seal check. Gap: the spec was not re-read in full in the turns examined (the hook asks for that at milestones). |
| 2 | Instructions reload | PASS | `CLAUDE.md` re-attached as a project instructions file after compaction (L1672, type `instructions`, path of the repo `CLAUDE.md`). The first answer follows AM-001 (no narration, direct answer to a direct question). |
| 3 | Active task identified | PASS | Hook brief names the in-progress rows (T-002..T-006 ...) and counts (L1662). The compaction summary section 8 "Current Work": "Cleanup batch 2 under AM-002 was just committed as 8d15f419" and the pending question about the three worktrees (L1646). The agent then ran its step list for the new request (`update_plan`, 09:42:34, L1721). |
| 4 | Statuses kept | PASS | Hook brief at 08:52:08: "BLOCKED 3, FAILED 1, IN PROGRESS 19, NOT STARTED 23, READY FOR REVIEW 6, VERIFIED COMPLETE 11"; audit at 09:43:52: identical counts (L1771). The summary's list (VERIFIED COMPLETE: T-063, T-027..T-031, T-033 plus earlier rows) matches the 11. |
| 5 | Execution plan recoverable | PARTIAL | `docs/session-state.md` and `docs/engineering-decisions.md` were re-attached by the compaction (L1651-1652) and the plan was read from disk at 09:43:44-47 (L1755-1761). `docs/execution-plan.md` itself was not opened in the examined turns; a plan was rebuilt from the user's request and the summary, not from that file. |
| 6 | IDs intact | PASS | "109 requirements, 63 tasks ... 0 errors" at 08:52:08 (hook) and 09:43:52 (L1771); R-ids and T-ids cited correctly afterwards (PD-006 grep, T-007, T-032, T-033 rows read at 09:43:40, L1751-1752). |
| 7 | Work resumes | PASS | First reply cites `PD-006` and `docs/video/PIPELINE.md` section 10 correctly (L1713); on approval it installed FFmpeg 9.0.2 (L1735-1736) and decoded the four films (0 errors, recorded in `docs/verification-report.md`). The pending cleanup question was carried in the summary and answered in the later turns. |

## Verdict
6 of 7 PASS, 1 PARTIAL (execution plan not opened). Not an independent re-run: this record is a reading of the transcript by an implementer agent, so T-007 stays READY FOR REVIEW until a reviewer checks the cited lines. Follow-up for next compaction: open `docs/execution-plan.md` and the spec after the hook brief.
