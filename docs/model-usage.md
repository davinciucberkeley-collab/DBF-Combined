# Model usage log (R-ORC-05)

Append one row per delegated task. Review at each milestone: are opus runs justified, are haiku/sonnet runs causing rework?

| Date | Task | Agent / model | Complexity | Outcome | Usage (tokens / time) | Retries | Escalation | Review result |
|---|---|---|---|---|---|---|---|---|
| 2026-11-18 | T-016 capability audit | general-purpose / sonnet | moderate (read-heavy, cross-file) | done, 132-line audit | 135 k tok / 3.0 min | 0 | — | — |
| 2026-11-18 | T-026 video pipeline audit | general-purpose / sonnet | moderate | done (stopped its leftover full-disk ffmpeg search) | 118 k tok / 4.6 min | 0 | — | conductor spot-check OK |
| 2026-11-18 | T-011 registry vs spec | general-purpose / haiku | routine accounting | done, 71 findings, most valid | 145 k tok / 3.2 min | 0 | — | conductor applied fixes |

Note 2026-11-18: the project agents in `.claude/agents/` were written mid-session and are not loaded until the next
session (Agent tool: "Agent type 'implementer' not found"). Until then the same routing is applied with the
`model` override on `general-purpose`. Next-session check: T-013 acceptance. Update 2026-11-18: the harness loaded them later in this session (eng-reviewer, implementer, ledger-auditor, runner now offered by the Agent tool).
| 2026-11-18 | T-018..T-021 elevon linkage kinematics, dynamics, swept collision | general-purpose / sonnet | moderate-high (spatial linkage) | done; found 3 real defects; records file refused by subagent Write policy, written by conductor | 223 k tok / 14 min | 0 | — | conductor reran all 3, hand-checked 2 numbers |
| 2026-11-18 | T-027 film shot-list mode + 1080p60 preview | general-purpose / sonnet | moderate (pipeline extension) | done, preview OK, framing defects | 181 k tok / 15.6 min | 0 | — | conductor viewed contact sheet |
| 2026-11-18 | T-061 D-212 linkage fix + gates | general-purpose / sonnet | high (CAD change + gates) | own checks pass; rejected by opus review (joint modelled ≠ joint built) | 228 k tok / 38 min | 1 (revision) | — | eng-reviewer/opus: reject, 1 critical + 4 major |
| 2026-11-18 | T-061 review | eng-reviewer / opus | high-impact independent review | reject with required fixes; reproduced all claimed numbers | 115 k tok / 10.6 min | 0 | — | — |
| 2026-11-18 | T-017 physics relabel | general-purpose / sonnet | moderate (judgment on wording) | running | — | 0 | — | — |
| 2026-11-18 | T-041a cleanup dry-run facts | general-purpose / haiku | routine (grep/inventory) | running | — | 0 | — | — |
| 2026-11-18 | T-063 D-212 rev 2 | general-purpose / sonnet (resumed) | high | linkage accepted; printed horn bond rejected by 2nd review | 333 k tok / 37 min | 2 | — | eng-reviewer/opus: reject (C-1 bond model invalid, 5 majors) |
| 2026-11-18 | T-063 rev 2 review | eng-reviewer / opus | high-impact review | reject with fixes; all numbers reproduced | — | 0 | — | — |
| 2026-11-18 | T-063 rev 3 horn attachment | implementer / opus | high (after 2 failed rounds) | rib horn + keeper; gates pass; 5 FAIL claims vs EST allowables gated on E1 coupon | 446 k tok / 64 min | 0 | escalated sonnet → opus: two rejected rounds on the same subsystem, approach change needed | — |
| 2026-11-18 | T-063 rev 3 review | eng-reviewer / opus | high-impact review | accept with conditions (M-1 test route, M-2 coupon 36.8 N, m-1 stale outputs; M-3 torque-tube fallback) | 194 k tok / 14 min | 0 | — | — |
| 2026-11-18 | T-063 review conditions | implementer / sonnet | moderate (graph + text edits) | conditions closed; strict fails = 5 analysis FAILs + A-P13 | 160 k tok / 5 min | 0 | — | conductor rerun of run_all.py |
| 2026-11-18 | T-028 Scene 3 + film framing fixes | implementer / sonnet | moderate (Blender pipeline) | S3 kinematics-driven; cam check 0/4620 inside; previews only | 216 k tok / 22 min | 0 | — | frame review pending (T-030) |
| 2026-11-18 | T-029 Scenes 4 (SITL playback) + 5 (FEA) | implementer / sonnet | moderate (Blender pipeline) | S4 SITL Z5_gb0 playback, S5 hub/arm FEA; cam check 0/7320; film 122 s (trim in T-030) | — | 0 | — | frame review T-030 |
| 2026-11-18 | T-030 film frame review | eng-reviewer / opus | high-impact review (rendered frames) | accept with conditions: 9 majors (on-screen numbers, props, trim, ignored sources) | — | 0 | — | — |
| 2026-11-18 | T-030 fixes | implementer / sonnet | moderate | M-1..M-9 closed; 116 s; highlight 24.2 s; cam check 0 inside | 291 k tok / 27 min | 0 | — | — |
| 2026-11-18 | T-031 full renders | conductor (no model; Blender background) | routine execution | main 116 s 6960 fr 88 min (24.2 MB), highlight 24.2 s 1452 fr 20 min (5.4 MB); re-encoded to absolute path (driver fix) | — | 0 | — | — |
| 2026-11-18 | T-033 playback verification | runner / haiku | routine | both films decode, metadata match, 0 errors, joins OK (sampled) | — | 0 | — | — |
| 2026-11-18 | T-031 clips + T-032 pipeline doc | implementer / sonnet | moderate | 2 elevon clips (12 s, 6 s) from stored S3 frames; PIPELINE.md | — | 0 | — | — |
| 2026-11-18 | T-030/T-033 final film sign-off | eng-reviewer / opus | high-impact review (rendered films) | full decode 0 errors all 4 files; visual: N-1 readout covered, N-2 no exploded view/arrows/dims (R-VID-08), N-3 card -dirty | — | 0 | — | — |
| 2026-11-18 | Film final-review fixes (N-1, N-2, minors) | implementer / sonnet | moderate | running | — | 0 | — | — |
