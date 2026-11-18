# Model usage log (R-ORC-05)

Append one row per delegated task. Review at each milestone: are opus runs justified, are haiku/sonnet runs causing rework?

| Date | Task | Agent / model | Complexity | Outcome | Usage (tokens / time) | Retries | Escalation | Review result |
|---|---|---|---|---|---|---|---|---|
| 2026-11-18 | T-016 capability audit | general-purpose / sonnet | moderate (read-heavy, cross-file) | done, 132-line audit | 135 k tok / 3.0 min | 0 | — | — |
| 2026-11-18 | T-026 video pipeline audit | general-purpose / sonnet | moderate | done (stopped its leftover full-disk ffmpeg search) | 118 k tok / 4.6 min | 0 | — | conductor spot-check OK |
| 2026-11-18 | T-011 registry vs spec | general-purpose / haiku | routine accounting | done, 71 findings, most valid | 145 k tok / 3.2 min | 0 | — | conductor applied fixes |

Note 2026-11-18: the project agents in `.claude/agents/` were written mid-session and are not loaded until the next
session (Agent tool: "Agent type 'implementer' not found"). Until then the same routing is applied with the
`model` override on `general-purpose`. Next-session check: T-013 acceptance.
| 2026-11-18 | T-018..T-021 elevon linkage kinematics, dynamics, swept collision | general-purpose / sonnet | moderate-high (spatial linkage) | running | — | 0 | — | — |
| 2026-11-18 | T-027 film shot-list mode + 1080p60 preview | general-purpose / sonnet | moderate (pipeline extension) | running | — | 0 | — | — |
