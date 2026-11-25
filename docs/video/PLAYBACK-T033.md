# T-033 playback check: concept A films

Decoder: Blender 4.5.14 (`blender -b --factory-startup -P decode_t033.py`). Movie clip metadata via `bpy.data.movieclips.load`; frames decoded through a VSE movie strip (scene fps 60, 1.0 base, 1920x1080, Standard view transform) and written to PNG, then read back. Scratch script and raw results are in the session scratchpad (`results_main.json`, `results_highlight.json`, `log_main.txt`, `log_hl.txt`). No ffmpeg/ffprobe used.

| Check | Expected | Measured | PASS/FAIL | Command |
|---|---|---|---|---|
| Main: width x height | 1920 x 1080 | 1920 x 1080 (movieclip and strip) | PASS | `bpy.data.movieclips.load(film-main-1080p60.mp4)`; `clip.size` |
| Main: fps | 60 | 60.0 | PASS | `clip.fps` |
| Main: frame count (movieclip) | 6960 | 6960 | PASS | `clip.frame_duration` |
| Main: frame count (VSE strip) | 6960 | 6960 (strip matches scene length) | PASS | `sequences.new_movie(...)`; `strip.frame_final_duration` |
| Main: duration | 116.0 s | 6960 / 60 = 116.0 s | PASS | derived from frame count and fps |
| Main: shot list sum | 116.0 s | 116.0 s (S1 12, S2 25, S3 18, S4 31, S5 19, S6 11) | PASS | sum of `dur` in `shots-main.json` |
| Main: every-60th + first + last decode | 117 frames decode, no error | 117 decoded, 0 errors, 0 bad shapes; frames 0, 60, ..., 6900, 6959; mean RGB 222.3 (f0) to 233.6 (f6959) | PASS | `render_to_arr` over frame list, `results_main.json` |
| Highlight: width x height | 1920 x 1080 | 1920 x 1080 | PASS | `clip.size` |
| Highlight: fps | 60 | 60.0 | PASS | `clip.fps` |
| Highlight: frame count (movieclip and strip) | 1452 | 1452 / 1452 | PASS | `clip.frame_duration`; `strip.frame_final_duration` |
| Highlight: duration | 24.2 s | 1452 / 60 = 24.2 s | PASS | derived |
| Highlight: every-60th + first + last decode | decode, no error | 26 decoded, 0 errors; frames 0, 60, ..., 1440, 1451 | PASS | `results_highlight.json` |
| Main S4 join 3300 (S3\|S4, 55.0 s): jump vs neighbours | jump <= 3x median | jump 2.302, neighbours 2.543, 2.582, 1.467, 1.884, median 2.213, ratio 1.04 | PASS | 6-frame window 3294..3305, `results_main.json` |
| Main S4 join 3720 (4.1\|4.2, 62.0 s) | jump <= 3x median | jump 0.284, neighbours 0.351, 0.607, 0.271, 0.496, median 0.423, ratio 0.67 | PASS | window 3714..3725 |
| Main S4 join 4320 (4.2\|4.3, 72.0 s) | jump <= 3x median | jump 1.991, neighbours 2.664, 2.121, 2.092, 2.158, median 2.139, ratio 0.93 | PASS | window 4314..4325 |
| Main S4 join 4620 (4.3\|4.4, 77.0 s) | jump <= 3x median | jump 1.625, neighbours 1.476, 1.714, 3.455, 3.711, median 2.585, ratio 0.63 | PASS | window 4614..4625 |
| Main S4 join 4830 (4.4\|4.5, 80.5 s) | jump <= 3x median | jump 1.059, neighbours 0.900, 1.474, 0.677, 0.957, median 0.929, ratio 1.14 | PASS | window 4824..4835 |
| Main S4 join 5160 (S4\|S5, 86.0 s) | jump <= 3x median | jump 1.696, neighbours 2.187, 1.979, 1.243, 1.197, median 1.611, ratio 1.05 | PASS | window 5154..5165 |
| Contact sheet of S4 join frames | PNG written, 6 rows x 12 frames | `redesign/showcase/concept-a/film/playback-T033-S4joins.png`, 2880 x 840 px; red marker on first frame of new shot | PASS | `decode_t033.py` sheet output |

## Notes
- Diff metric: mean absolute difference of RGB, full frame, on the 0-255 scale, between consecutive decoded frames. Join jump = diff(f-1, f). Neighbours = the diffs (f-3,f-2), (f-2,f-1), (f,f+1), (f+1,f+2). Flag if jump > 3 x neighbour median. No join is flagged.
- Limitation: the spec says cuts happen only between scenes. The S4 internal joins are therefore continuous camera paths, so low diffs are expected there. Mean-abs-diff cannot reliably separate a hard cut from motion when both frames are mostly white background. The S3|S4 and S4|S5 joins are scene boundaries, and their jumps (2.30 and 1.70) are not larger than their neighbours. The contact sheet shows the visible change at S3|S4 and S4|S5, so the cut is visible by eye, but this metric does not flag it.
- Only 117 of 6960 main frames and 26 of 1452 highlight frames were decoded (the every-60th set). Full-length decode was not run. Frame count and fps come from container metadata, not from a full decode.
- Frames were decoded with Blender's built-in FFmpeg path, so this check does not cover other players' decoders.
- Contact sheet: 12 columns per join (frames f-6..f+5, 1/8 scale), rows in shot order. Red marks frame f, the first frame of the new shot.
