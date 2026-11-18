# Verification report — independent evidence

Only checks actually run are recorded here, with the command and result. Self-reports are not evidence.

## Recovery tests (T-007, T-008)
| Date | Test | Command | Result |
|---|---|---|---|
| 2026-11-18 | Hook unit run, SessionStart | `echo '{"source":"startup"}' \| python -I .claude/hooks/recovery.py session-start` | PASS: brief printed (spec path, recovery steps, ledger counts, in-progress tasks, 0 audit errors); event logged in `docs/session-log.md` |
| 2026-11-18 | Hook unit run, PreCompact | `... recovery.py pre-compact` | PASS: logged, `session-state.md` snapshot at `.claude/session-state.precompact.md`, missing-file check reported the one file then absent |
| 2026-11-18 | Tamper detection | appended a byte to a copy of the spec; dropped a requirement's only task in a copy of the ledger | PASS: audit printed `MASTER_PROJECT_SPEC.md changed since it was sealed` and `R-PHY-01: no task`, exit 1 |
| 2026-11-18 | Line endings | CRLF copy of the spec | PASS: audit 0 errors (hash normalises EOL; `.gitattributes` pins LF) |
| 2026-11-18 | New CLI session (T-008) | `claude -p --model haiku ...` from the repo root | PARTIAL: Claude Code 2.1.288 loaded `.claude/settings.json` and fired SessionStart(startup) (logged `session=9449ec4f`), but the CLI is not logged in (`Not logged in · Please run /login`), so the model's recall could not be tested headlessly |
| — | Manual compaction (T-007) | `/compact` in the desktop session, then ask for the active task | NOT RUN: needs the user to type `/compact` (a session cannot compact itself) |

## Milestone audits (T-011, T-048)
_not run yet_

## Video verification (T-033)
_not run yet_

## Final verification (T-047)
_not run yet_
