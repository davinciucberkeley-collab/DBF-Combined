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
| 2026-11-19 | Manual compaction (T-007) | Dillon typed `/compact` in desktop session 7cb35b0a; next turn resumed from disk | PARTIAL (independent re-check 2026-11-19, `docs/audits/2026-11-19-recheck-docs.md`: events logged and work resumed, but check 5 'plan recoverable' not shown: `docs/execution-plan.md` was not reopened after compaction; needs a second manual `/compact`): `docs/session-log.md` 00:51:20 PreCompact trigger=manual missing=none, 00:52:08 SessionStart source=compact, 00:52:08 PostCompact; brief named spec path, recovery steps, ledger counts (63 T, 0 audit errors) and in-progress tasks; after compaction `ledger_audit.py` 0 errors with the same status counts (spec seal intact, IDs intact); the session resumed the pending task (cleanup wrap-up, worktree question) and then the ffmpeg approval |

## Independent playback check with standalone FFmpeg (PD-006 closed, 2026-11-19)
FFmpeg 9.0.2 (gyan.dev full build, `winget install Gyan.FFmpeg`, user scope, approved by Dillon in chat 2026-11-19). Files from commit 0da084ab. Commands: `ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,bit_rate:format=duration,size <mp4>`; `ffmpeg -v error -i <mp4> -f null -` (every frame decoded; error lines counted).

| File | Codec / profile / pix_fmt | Size | fps (r / avg) | Frames decoded | Duration | Decode errors |
|---|---|---|---|---|---|---|
| `film/film-main-1080p60.mp4` | h264 High yuv420p | 1920x1080 | 60/1 / 60/1 | 7,194 | 119.900 s | 0 |
| `film/film-highlight-1080p60.mp4` | h264 High yuv420p | 1920x1080 | 60/1 / 60/1 | 1,452 | 24.200 s | 0 |
| `film/clips/clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4` | h264 High yuv420p | 1920x1080 | 60/1 / 60/1 | 708 | 11.800 s | 0 |
| `film/clips/clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4` | h264 High yuv420p | 1920x1080 | 60/1 / 60/1 | 360 | 6.000 s | 0 |

All four: constant 60 fps, video only (no audio stream), 0 decode errors from a decoder independent of the Blender encoder. 9,714 frames total.

## Agent routing check (T-013)
2026-11-19: the `ledger-auditor` agent (model per `.claude/agents/ledger-auditor.md` line 4: haiku) was run for the independent setup check (R-ORC-01, R-ORC-02, R-COM-03). Its reply used the required one-line shape from `.claude/agents/ledger-auditor.md` line 10:
a labelled line `Task: … | Outcome: … | Verification: … | Evidence: … | Blocker: …` (run transcript: session subagent record of 2026-11-19), with the details in the evidence file (scratchpad `setup-check.md`, 17 rows: PASS 7, FAIL 6, CANNOT CHECK 4). Other definitions: `eng-reviewer` opus, `implementer` sonnet, `runner` haiku (frontmatter `model:` line 4 of each file). Run row in `docs/model-usage.md`.

## Milestone audits (T-011, T-048)
T-011: run 2026-11-18, `docs/audits/2026-11-18-ledger.md` (haiku accounting audit, 21 gaps fixed). T-048: 2026-11-23 `docs/audits/2026-11-23-milestone-audit.md` (this audit); earlier phase-end reviews: 2026-11-19 setup / recheck files, 2026-11-22 rounds 2-3, 2026-11-23 rounds 4-5.

## Video verification (T-033)
Reviewer: independent opus review agent, 2026-11-18, tree `39eb5b84` (clean). Full findings: `docs/audits/2026-11-18-film-final-review.md`. Decoder: Blender 4.5.14 bundled libavcodec (`--debug-ffmpeg`), VSE strip, every frame rendered to PNG and read back; container read independently with a Python MP4 box parser. No ffmpeg/ffprobe on the machine.

| Date | File | Command | Expected | Result |
|---|---|---|---|---|
| 2026-11-18 | `film/film-main-1080p60.mp4` | `blender -b --factory-startup --debug-ffmpeg -P fulldecode.py -- <mp4> <dir>` + `python -I analyse.py main` + `python -I mp4box.py` | 6,960 frames (shots-main.json 116.0 s x 60), 1920x1080, 60 fps | PASS: container avc1 1920x1080, 6,960 samples, 60.000 fps, 116.000 s; 6,960 of 6,960 frames decoded and written, contiguous; 0 libav error/warning lines (83,690 log lines); 0 blank, 0 non-opaque, 0 bad-shape, 0 exact-duplicate frames |
| 2026-11-18 | `film/film-highlight-1080p60.mp4` | same | 1,452 frames (24.2 s) | PASS: 1,452 of 1,452 decoded; 60.000 fps, 24.200 s, 1920x1080; 0 errors; 0 blank/duplicate |
| 2026-11-18 | `film/clips/clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4` | same | 720 frames (12.0 s) | PASS: 720 of 720; 0 errors; 0 blank/duplicate |
| 2026-11-18 | `film/clips/clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4` | same | 360 frames (6.0 s) | PASS: 360 of 360; 0 errors; 0 blank/duplicate |
| 2026-11-18 | Visual review of final encodes (56 full-res frames + decode strips) | `grab.py` frame extraction, viewed at 1080p | T-030 M-1..M-9 closed on screen; no new defects | PASS WITH CONDITIONS: M-1, M-3..M-9 closed. Open: N-1 (Major) S4 shots 4.1/4.2 lower third hides the left end of the readout incl. "Prop rotation illustrative"; N-3 (Major) closing card shows `commit fe02c9d5-dirty` (main and highlight); N-2 (Major, R-VID-08) no exploded view, motion arrows or dimension call-outs; minors m-A..m-E |

Decode total: 9,492 frames across four files, 0 decode errors (R-VID-15 decode part met). R-VID-15 review part not passed until N-1, N-3 (overlay + encode rerun from a clean tree) and N-2 are closed and the decode is re-run on the new encodes.

### Re-check after T-030-N fixes (2026-11-18, encodes from clean commit `ebb89693`, committed in `0da084ab`)
Same method (container parse + Blender `--debug-ffmpeg` full decode + per-frame analysis). Details: `docs/audits/2026-11-18-film-final-review.md`, "Re-check".

| Date | File | Expected | Result |
|---|---|---|---|
| 2026-11-18 | `film/film-main-1080p60.mp4` | 7,194 frames (shots-main.json 119.9 s), 1920x1080, 60 fps | PASS: 7,194 of 7,194 decoded, contiguous; 60.000 fps; 119.900 s; 0 libav error/warning lines (86,498); 0 blank/non-opaque/bad-shape; 0 exact duplicates |
| 2026-11-18 | `film/film-highlight-1080p60.mp4` | 1,452 frames (24.2 s) | PASS: 1,452 of 1,452; 0 errors; 0 blank/duplicate |
| 2026-11-18 | `film/clips/clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4` | 708 frames (11.8 s, 3.1 from 0.2 s) | PASS: 708 of 708; 0 errors |
| 2026-11-18 | `film/clips/clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4` | 360 frames (6.0 s) | PASS: 360 of 360; 0 errors |
| 2026-11-18 | Visual re-check of final encodes (about 45 full-res frames + decode strips) | N-1, N-2, N-3, m-A..m-D fixed; no regression | PASS: all closed on screen (card "commit ebb89693", no -dirty; S4 readout uncovered; exploded view 2.6, span dimension 1.2, servo-arm arrow 3.1/H2 with sign matching the sweep); no regression; 4 new cosmetic minors m-F..m-I recorded as optional |

Decode total of the re-check: 9,714 frames, 0 decode errors. R-VID-15: decode and visual review both passed (reviewer view; ledger status is set by the conductor).



**T-032 (2026-11-23, review round 4):** VERIFIED COMPLETE with "reproducible" read as: the commands, frame counts, durations, decode and decoded-stream hash of a re-encode reproduce from `docs/video/PIPELINE.md`; a re-render is not pixel-identical (mean per-frame MSE 83-95, differences on glyph and geometry edges, `PIPELINE-FOLLOW-2026-11-22.md` step 9). Evidence `docs/audits/2026-11-23-review-round-4.md`.


## Recovery (T-008, 2026-11-23)
A fresh haiku agent with no conversation context followed CLAUDE.md and the session-state recovery procedure and named the spec path (`docs/MASTER_PROJECT_SPEC.md`), the next action (T-093 order-week re-check, then cleanup T-042..T-045, T-047 last) and the active tasks; `ledger_audit.py` 0 errors, `plan_rid_check.py` 109 R-ids, 0 missing. It listed 8 procedure gaps (stale counts and pause state, Reconciliation, step 3 / 5 wording, dependency gaps); the conductor checked each against the files and fixed them in `docs/session-state.md`. Evidence `docs/audits/2026-11-23-recovery-test.md`.

## Final verification (T-047)
T-011: run 2026-11-18, `docs/audits/2026-11-18-ledger.md` (haiku accounting audit, 21 gaps fixed). T-048: 2026-11-23 `docs/audits/2026-11-23-milestone-audit.md` (this audit); earlier phase-end reviews: 2026-11-19 setup / recheck files, 2026-11-22 rounds 2-3, 2026-11-23 rounds 4-5.
