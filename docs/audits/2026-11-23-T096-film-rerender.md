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


## Rework (F-5), 2026-11-23 (T-099 final audit finding F-5, section 4)

Acceptance test (from the brief): S6 card, S5, S4 and highlight H4 (with the other shots that play the same stale sources) show current results only, numbers from current params, claims, README or result files; S2/2.2 caption not over a fin-only view; main and highlight re-encoded at the same paths and specs (1920x1080, 60 fps, same frame counts); ffprobe and a full ffmpeg decode clean; `--cam-check` re-run for the changed shots; inspected frames saved in `docs/audits/2026-11-23-T096-frames/rework/`. Categories: S4 and H3-H5 are flight dynamics (playback of a stored SITL run, AR-015); S5 is FEA (stored T-076c H-A1 status, no new FEA); the card mixes rigid-body dynamics (AR-016 landing foam), flight dynamics and FEA records; the rest is illustrative. Media rework, no new analysis. Not marked VERIFIED COMPLETE. Ledger, spec files, `redesign/site/**` and `app.html` not touched; nothing committed.

### What changed on screen
| Shot | Before | Now | Source |
|---|---|---|---|
| S6 card, revision | "D-212 rev 3, commit 49a9afe3-dirty" | "CHANGE-LOG D-246, 2026-11-23 (untagged working tree)" | the tree is dirty with other agents' edits and nothing is committed, so a clean hash cannot be printed truthfully; the owner can re-render the card after the commit |
| S6 card, mass | "predicted 1.8807 kg vs gate 1.47 kg (-410.7 g left)" | "predicted 1.881 kg EST (CAD 1.641 kg) vs 1.47 kg gate: over the gate by 410.7 g" | `params-A.json` mass/*, req/mass_gate_kg; README line 16 |
| S6 card, landing | Z5_gb0, 1.50 kg, run of 2026-11-15 | SITL `T097_Z5` 1.881 kg EST: sink 0.13 m/s, lean 0.0 deg, tipped over no. New line "Landing foam (AR-016)": stroke 17.2 of 20 mm, 10.76 g of 12 g, tilt 2.3 deg (worst of 10), valid only for foam 37.5-39.0 N and zeta 0.02-0.05 (D-243), TP-3 open | `T097_data/sitl_T097_Z5/sum.json`; `T098_results.json` row `plateau_sweep_rib25x23/37.5N` (read at draw time) |
| S6 card, hub | "Hub FEA (run d209) ... PETG" | "Hub (machined 6061-T6): FEA H-A1 hub passes; CF arm-tube shear and tube / sleeve bond FAIL, open (D-226, TP-4, TP-5)" | `T076c_hub_al.md` s0; Explorer #structures `fea-hub-current` |
| S6 card, extra row | none | "Elevon pitch use 0.79 vs 0.60 limit (15 deg basis): FAIL, open (D-245)" | `params-A.json` sim/pitch_use_15_worst, req/pitch_use_max (open item kept visible on the "latest" card) |
| S5, 5.1 and 5.2 | d209 PETG hub stress maps (F2 and S2) | 5.1 "Hub: machined 6061-T6 (D-220)" and 5.2 "Open rows: arm tube and bond": CAD cut-away views with a status panel (hub passes; 427,333 tet10 elements; allowables not relaxed; H-A2 and d209 map not re-run; CF arm-tube shear and bond FAIL, also with a PETG hub; load basis 1.64 kg, older than 1.881 kg; not VERIFIED). 5.3 (arm and cup, d210) unchanged. Same 6 s each | T-076c H-A1 as in the Explorer; the PETG map is not shown |
| S4 (4.1-4.5), H3, H4, H5 | Z5_gb0, 1.50 kg, "geometry before D-207" | `T097_Z5`, 1.881 kg EST (AR-015); same log windows (the run has the same phases: climb done 64.7 s, FBWA 100.9 s, back-transition 125.4 s, QLAND 153.5 s, touch-down 249.0 s); run line prints 1.881 kg (format changed from 2 to 3 decimals); 4.4 sub-title "about 92 m" (run altitude 91.7 m); 4.5 sub-title notes the foam stroke is on the closing card; H3 sub-title names T097_Z5 | `case.fwd.csv`, `sum.json` |
| H6, H7 | PETG F2 map, old card | same content as the new 5.1 and the new card (camera of H6 re-sampled from the new S5 path; the sampler reproduced the stored H6 camera of the old film with error 0.0 before use) | main shots |
| S2/2.2 | "Propulsion" caption from t = 0 over the fin fly-by (blocked frames 1062-1076, ratio 0.498 at 1074) | caption fades in at 1.5 s (frame about 1110, motor in view); camera unchanged | new shot field `title_delay` (overlay only) |
| S2/2.3 caption, build-film label | "PETG hub" | "Machined 6061-T6 hub (D-220)"; SHORT label CGE-001 "Hub (6061-T6, machined)" (build film not re-rendered) | D-220 |

Code: `render_build_a.py` gained `run_dir()` (T097_ runs read from `mechanism/out/T097_data/sitl_<run>`), a `t098` card-value source, `title_delay` (overlay-only), 3-decimal mass in the SITL readout. Shot lists `film/shots-main.json` and `film/shots-highlight.json` were rewritten by `rework/edit_shots_main_F5.py` and `edit_shots_highlight_F5.py` (kept in the frames folder; the highlight script was run once, the H3 sub-title was fixed afterwards with a one-line sed).

### Re-render (raw frames reused where the picture is unchanged, T-030-N incremental mode)
- Main: `render_build_a.py --shot-list film/shots-main.json --changed-from <HEAD shots-main.json> --samples 24 --workers 4 --work %TEMP%\t096\main`: 4,194 frames reused, 3,000 changed (S4 1,860; S5 shots 5.1 and 5.2 720; 5.3 plate frames 420 need no raw), 2,580 raw frames rendered, 3,220 s. Then `--skip-render` (overlay 6,738 pictures 212 s, encode 375 s). Highlight: 672 reused, 780 changed, 2,395 s; overlay 57 s, encode 120 s. Logs and timing JSONs in `rework/`.
- Frame counts and specs unchanged: main 7,194 frames, 119.9 s; highlight 1,452 frames, 24.2 s; h264, 1920x1080, 60/1. No retime was needed (5.1 and 5.2 keep 6 s each).
- Clips 3.1 and 3.2 are untouched (S3 not in scope; the clip lists are unchanged in `git status`).

### Verification (commands run from the repo root)
- `ffprobe -count_frames` on both repo files: h264 1920x1080 60/1, main 7,194 frames 119.900 s, highlight 1,452 frames 24.200 s.
- `ffmpeg -v error -i F -map 0:v:0 -f null -`: exit 0, no output, both files (`rework/decode-rework.log`, which also holds the file SHA-256: main d8426164..., highlight 2bdda554...). File sizes 28,409,920 and 6,081,096 bytes (were 26,072,532 and 5,615,374: more overlay text and a different SITL trajectory).
- Camera clearance, `render_build_a.py --shot-list <list> --cam-check ... --work <scratch>` (Blender 4.5.14, no render):
  - Main, scenes S2, S4, S5 (4,734 frames; the S3 and S6 camera paths are unchanged and S6 has no 3-D change): inside-geometry frames 0 in every shot. S4 4.1-4.5: 0 inside, no part within 0.3 m of the camera (min clearance None), 0 blocked. S5/5.1: 0 inside, none within 0.3 m, 0 blocked. S5/5.2: 0 inside, minimum clearance 0.212 m (CGE-003-UL), 0 blocked. S2/2.2 unchanged: 15 blocked frames (FIN-004-R 11, FIN-001-R 4), all inside the first 0.95 s, before the caption now appears at 1.5 s. The line-of-sight test is off (`los` false) for the S4 follow shots and the two new S5 shots, as for the shots they replace.
  - Highlight, all shots (1,452 frames): inside 0 in every shot; H2 min clearance 0.2614 m (WNG-006-L), unchanged; H3-H7 none within 0.3 m; 0 blocked.
  - Outputs in `rework/camcheck-main-S2S4S5.txt`, `camcheck-highlight.txt`, `cam_clearance_main_S2S4S5.json`, `cam_clearance_highlight.json`. The check overwrites `film/cam-clearance.json`; it was restored from a backup after each run and verified by SHA-256 (024ffc13..., 7c42559d..., unchanged tracked files). Adopting the new JSONs as the tracked `cam-clearance*.json` (audit item 5) is still the owner's call.
- Frames opened and inspected (`rework/`): main t17.8 and t18.4 (2.2 without caption, fin view), t19.2 (caption with the motor in view), t62, t70, t78, t82, t87.5, t89.5 (S4, T097_Z5 readouts and touch-down note "sink 0.13 m/s, lean 0.0 deg, tipped over: no"), t98 (5.2), t118 (S6 card); highlight t8 (H3), t12 (H4), t16.5 (H5), t18.5 (H6), t23 (H7). 5.1 was inspected at full size in the preview render before the full render. Saved, not opened: main t21, t93, t105; highlight t3, t6, t9, t14, t20, t22. Defects found and fixed during the work: the run line printed "1.88 kg" (now 1.881), the H3 sub-title still said "Z5_gb0" (now T097_Z5), and the first card layout overlapped the title chip (text shortened, 8 to 7 rows).

### Residual (not changed, for the owner)
1. The card revision line carries no commit hash (tree dirty, nothing committed); re-render the card (overlay only, `--skip-render`, about 10 min) after the commit if a hash is wanted.
2. The S3 tag "kinematics AR-001 (D-212 rev 3)" and the H2 tag are unchanged (the AR-001 revision label, not in F-5).
3. The 5.3 arm and cup plate is still run current_d210 (PETG cups); the audit did not flag it.
4. Audit items 5 and 6 (adopt the cam-check JSONs; Explorer caption `app.html:411`) are outside this task.
5. The re-exported `concept-a.glb` was not used by the film renderer (it builds from `qp/A/cad/model`).
