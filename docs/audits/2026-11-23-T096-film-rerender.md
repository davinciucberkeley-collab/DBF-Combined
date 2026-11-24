# T-096: film, clips and stills re-rendered from the current CAD (2026-11-23)

Acceptance test (from the brief): re-encoded MP4s at the same paths and specs (1920x1080 at 60 fps, same frame counts), stills with no MN2212 and the X2216 motors and FC annex visible, full decode with 0 errors, render log, this report. Categories: the films are kinematics (S3, clips), flight dynamics (S4 playback of a stored SITL run), FEA (S5 stored results), illustrative (rest). This is a media re-render, not a new analysis. Not marked VERIFIED COMPLETE; ledger, requirements and spec files untouched; nothing committed.

## CAD used
HEAD `49a9afe3` (redesign/v1); `git status` on `redesign/qp/A/cad` was clean (129 parts; D-227 X2216 880KV in `amodel/propulsion.py`, D-240 FC at y -75 mm with cover annex in `amodel/electrical.py`). The tree was dirty from other agents (docs, sitl, structures, site, tools), so the closing card reads "commit 49a9afe3-dirty". The renderer builds the stage from `redesign/qp/A/cad/model` at render time; no cached geometry.

## Renders (scratch work folders in `%TEMP%\t096`, scripts `run.sh`, `clips.sh`)
| Item | Command (short) | Result |
|---|---|---|
| Main film | `render_build_a.py --shot-list film/shots-main.json --width 1920 --height 1080 --fps 60 --samples 24 --workers 4 --work <scratch>` | 7,194 frames, 6,704 rendered, 11,172 s (render 9,670, overlay 548, encode 953); ran concurrently with the highlight and the stills on a loaded machine (4.84 s per rendered frame per worker) |
| Highlight | same with `shots-highlight.json`, 2 workers | 1,452 frames, 11,133 s |
| Clips 3.1, 3.2 | `blender ... encode --src <main frames> --list film/clips/list-3.x.txt` | 708 and 360 frames; the run regenerated the clip lists with the same frame names as the committed ones (`git status` shows them unchanged) |
| Stills | `render_showcase.py --samples 64 --spec showcase-a.json --root qp/A/cad/model`, then `publish_assets.py` with its site folder redirected to scratch | 15 stills re-rendered (all were dated 2026-11-16, before D-202 to D-240); cutaway-xray and detail-avionics rendered a second time after caption fixes |
| GA sheet | `render_drawing.py --root ... --out redesign/showcase/concept-a/drawing`, then `make_sheet_a.py` with SITE redirected to scratch | `a-front/top/side/iso.webp`, `a-sheet.svg`, `views.json` rewritten; motor stations 0.228 / 0.156 m hard-coded in `make_sheet_a.py` still match `amodel/common.py` YM, ZM |

Not touched by design: `redesign/site/**` (other agents). The site copies of the stills (`a-<id>.webp`, `thumb/a-<id>.jpg`) and the GA files (`assets/drawing/*`) are in `%TEMP%\t096\site_dummy` (`renders`, `assets/drawing`) and must be copied into `redesign/site/assets/` by the site owner; running `publish_assets.py` and `make_sheet_a.py` unpatched does it (the latter also rewrites the GA block of `app.html`). The build film (`a-build.mp4`) was not in the brief and was not re-rendered (only its callout labels were corrected, see below).

## Files written
- `redesign/showcase/concept-a/film/film-main-1080p60.mp4`, `film-highlight-1080p60.mp4`, `clips/clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4`, `clips/clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4`
- `film/render-T096-main.log`, `render-T096-highlight.log`, `timing-T096-main.json`, `timing-T096-highlight.json`
- `redesign/showcase/concept-a/renders/*.webp` (15) and `renders/thumb/*.jpg` (15); raw `_work/*`
- `redesign/showcase/concept-a/drawing/a-*.webp`, `a-sheet.svg`, `views.json`
- This report and `docs/audits/2026-11-23-T096-frames/` (frame grabs, still logs, decode logs)

## Decode and counts (ffprobe, then `ffmpeg -v error -i F -map 0:v:0 -f null -`: exit 0, no output; log `T096-frames/decode.log`)
| File | Codec, size, fps | Frames | Duration | Bytes | Decoded-stream SHA-256 (first 24 hex) |
|---|---|---|---|---|---|
| film-main | h264 1920x1080 60/1 | 7,194 | 119.9 s | 26,072,532 | b064f77e99ad23986... |
| film-highlight | same | 1,452 | 24.2 s | 5,615,374 | b4342770e78036c5c... |
| clip 3.1 | same | 708 | 11.8 s | 2,399,836 | e67e8f210365526fb... |
| clip 3.2 | same | 360 | 6.0 s | 1,225,533 | 1834acf44b1706e47... |

Counts and durations equal the previous films'. Blender decode (`decode_clips.py`, `T096-frames/decode-clips-blender.txt`): clip 3.1 708 frames, 13 decoded, 0 errors; clip 3.2 360 frames, 7 decoded, 0 errors. The sampled Blender decode of the two full films (T-033 script, not in the repo) was not re-run; the ffmpeg full decode is the check. Camera clearance (`--cam-check`) was NOT re-run: camera paths are unchanged but the geometry changed, so a check against the new motors and annex is OPEN (about 20 min).

## Frames inspected (saved in `docs/audits/2026-11-23-T096-frames/`)
Opened and looked at: main_t10 (S1 shot 1.3, "129 modelled parts"), main_t19.5 (S2 shot 2.2, X2216 caption; FC board and cover with its -y annex on the wing left of the hub), main_t38.5 (S2 exploded, ILLUSTRATIVE tag), main_t49 (S3, SIMULATED tag), main_t75 (S4, SIMULATED tag), main_t96 (S5, SIMULATED tag), main_t118 (S6 closing card), highlight_t12, still_detail-propulsion.png, still_detail-avionics.png. Saved but not opened: main_t3, main_t6 (S1), main_t56 (S3 shot 3.2). Close-up proof: `still_detail-propulsion.png` (X2216 880KV on its X-mount in the canted cup; caption "SunnySky X2216 880KV") and `still_detail-avionics.png` (flight controller AVN-002 under the cover annex on the left; "4S 2800 mAh pack"). No defects seen in the opened frames.

## Caption changes
- `film/shots-main.json` shot 2.2 sub-title: "Motor MN2212 KV780 ..." to "Motor SunnySky X2216 880KV ...".
- `redesign/blender/specs/make_showcase_a.py` and `showcase-a.json`: motor callout "T-Motor MN2212 KV780" to "SunnySky X2216 880KV"; detail-propulsion sub-title "MN2212" to "X2216"; pack callouts "4S 2300 mAh pack" to "4S 2800 mAh pack" (PWR-001 in `electrical.py` is the RDQ 2800 mAh).
- `showcase/concept-a/make_sheet_a.py`: GA callout "APC 9x4.5MR on T-Motor MN2212" to "... on SunnySky X2216".
- `render_build_a.py` SHORT labels (build-film callouts, build film not re-rendered): PRP-001 "Motor SunnySky X2216 880KV", PWR-001 "Pack RDQ 2800 mAh 4S".
- Captions that read live from source files changed by themselves (parts 129, cad3d, mass).

## Findings for the owner (not changed, outside the brief)
1. S6 card line "Mass, predicted vs gate" now prints "CAD basic 1.641 kg; predicted 1.8807 kg vs gate 1.47 kg (-410.7 g left)", read from `params-A.json`; true to the file, but "left" for a missed gate and the "D-212 rev 3" revision label read stale.
2. S4 and the highlight still play SITL run Z5_gb0 (1.50 kg, run file 2026-11-15, geometry before D-207; the on-screen note says so). T-097 reran simulations; the film was not repointed.
3. S6 shows packed height "0.39 m" (params 0.394 m, formatted to 2 decimals) and FEA numbers of run d209; the FEA GLBs were not regenerated.
4. Tracked `_work/*` raw PNGs changed (about 12 MB of binary diff) because the stills were re-rendered.
5. The card hash is "-dirty" because other agents' edits were in the tree; redo only the S6 card from a clean tree if a clean hash is wanted.

## Camera clearance re-run (2026-11-23, 17:34 to 17:40 MST)
Commands (from `redesign/showcase/concept-a`, Python 3.14.2 with `-I`; Blender 4.5.14 found by the script's `--blender` argument; `--work` in scratch, check mode only, no render):
- Main: `python -I render_build_a.py --shot-list film/shots-main.json --cam-check --width 1920 --height 1080 --fps 60 --blender "C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe" --work <scratch>/work-main`
- Highlight: same with `film/shots-highlight.json` and `--work <scratch>/work-hl`

Exit code: 0 for both. Wall time: 151 s (main), 151 s (highlight). stderr empty for both. Stdout saved to `redesign/showcase/concept-a/film/camcheck-T096.log` (both runs, headed).

Result, main (7,194 frames, 119.9 s): inside-geometry frames 0 in every shot. Minimum clearance 0.0679 m at frame 3264 (shot S3/3.2, part WNG-001). Line-of-sight blocked frames: S2/2.2, 15 frames (FIN-004-R 11, FIN-001-R 4; min-clearance part GER-002-UR at 0.2653 m, frame 1072). Other shots with a measured minimum: S2/2.5 0.1653 m (WNG-006-R), S2/2.6 0.166 m (WNG-006-R), S3/3.1 0.2614 m (WNG-006-L). Peak camera motion: view speed 96.74 deg/s (S3/3.2), view accel 251.5 deg/s^2 (S3/3.2), zoom rate 1.18 1/s and zoom accel 1.964 1/s^2 (S2/2.6), pan speed 0.3523 dist/s and pan accel 0.5911 dist/s^2 (S2/2.6).

Result, highlight (1,452 frames, 24.2 s): inside-geometry frames 0. Minimum clearance 0.2614 m at H2/H2.1 (WNG-006-L). Blocked frames 0 in every shot. Peak motion: view speed 40.65 deg/s and view accel 391.7 deg/s^2 (H1/H1.1), zoom rate 0.1068 1/s and zoom accel 1.162 1/s^2 (H5/H5.1), pan speed 0.01767 dist/s and pan accel 0.1992 dist/s^2 (H7/H7.1).

Comparison with the 2026-11-19 main run (7,320-frame version of the film): inside 0 both times, minimum clearance 0.0679 m at S3/3.2 both times. S2/2.2 blocked frames changed from 10 (PRP-002-UR) to 15 (FIN-004-R, FIN-001-R), so the new motors and annex now sit in the line of sight of the wing-tip-side shot. This is a line-of-sight issue only, not a collision. The check script has no numeric clearance limit; the hard fail is "inside" (0 frames). The 0.0679 m minimum is the smallest measured gap and is reported, not judged.

Side effect handled: the check mode copies its result to `film/cam-clearance.json` (the highlight run overwrote it too). Both tracked files were restored from a pre-run backup and verified by SHA-256 (`film/cam-clearance.json` 024ffc13..., `film/cam-clearance-highlight.json` 7c42559d...), so `git status` shows no change to them. The new JSON results are in scratch: `<scratch>/t096cam/work-main/cam_clearance.json` and `<scratch>/t096cam/work-hl/cam_clearance.json`. These are not written to the repo, per the no-file-edits rule. Whether to adopt them as the tracked `cam-clearance*.json` is a decision for the owner.
