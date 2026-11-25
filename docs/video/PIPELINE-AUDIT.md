# Video pipeline audit, concept A films (T-026, parent R-VID-01)

Date 2026-11-18. Read-only audit; nothing was rendered. Sources: the scripts and files named below. Numbers marked (estimate) are not measured.

## 1. Tool paths

- Blender 4.5.14 LTS: `C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe` (hard-coded default in `render_build_a.py` line 66, `render_animation.py`, `collide.py`, `make_shop_files.py`; override with `--blender` or env `BLENDER`). Blender 4.2.3 is also installed beside it (unused by the film scripts). Not under Program Files, not on PATH.
- ffmpeg / ffprobe: **none installed** (not on PATH, none found under `C:/Users/dillo/tools`, no `imageio_ffmpeg`, `av` or `cv2` in the system Python; a full-disk `find` for ffmpeg.exe/ffprobe.exe was started and did not finish within the time limit, so a copy elsewhere on disk is not excluded). The films are encoded by Blender's built-in FFmpeg library (VSE, `render_build_a.py` `blender_encode`, lines 915-950), which exposes no command-line ffmpeg. So there is no ffmpeg.exe path to give. For 60 fps re-encode, concatenation or filters either keep using the Blender VSE, or install an ffmpeg build or pip `imageio-ffmpeg` (a download; needs Dillon's approval).
- ffprobe substitute used for this audit: a small MP4 box parser (scratchpad `probe.py`, reads stsd/stsz/mdhd). It reports codec fourcc, size, sample count, duration.
- Python for the drivers: system Python with Pillow (overlay step).

## 2. Existing video files (concept A)

Probed by MP4 box parse. All H.264 (`avc1`), no audio track (`ff.audio_codec='NONE'`).

| File (redesign/showcase/concept-a/animation/) | Resolution | fps | Frames | Duration | Size |
|---|---|---|---|---|---|
| a-build.mp4 (66-step build film) | 1280x720 | 24 | 20,009 | 833.7 s | 19.3 MB |
| stage-01.mp4 | 1280x720 | 24 | 2,173 | 90.5 s | 4.6 MB |
| stage-02.mp4 | 1280x720 | 24 | 4,898 | 204.1 s | 8.2 MB |
| stage-03.mp4 | 1280x720 | 24 | 2,521 | 105.0 s | 5.3 MB |
| stage-04.mp4 | 1280x720 | 24 | 765 | 31.9 s | 1.4 MB |
| stage-05.mp4 | 1280x720 | 24 | 1,251 | 52.1 s | 2.7 MB |
| stage-06.mp4 | 1280x720 | 24 | 1,415 | 59.0 s | 3.3 MB |
| stage-07.mp4 | 1280x720 | 24 | 940 | 39.2 s | 2.7 MB |
| stage-08.mp4 | 1280x720 | 24 | 2,105 | 87.7 s | 4.9 MB |
| stage-09.mp4 | 1280x720 | 24 | 1,885 | 78.5 s | 5.3 MB |
| stage-10.mp4 | 1280x720 | 24 | 1,912 | 79.7 s | 4.9 MB |
| a-how-it-flies.mp4 (flight explainer) | 1280x720 | 30 | 600 | 20.0 s | 4.6 MB |

Also: `stage-NN.webp` (last frame per stage), `a-build-poster.webp`, `a-poster.webp`, `a-build.json` (per-step timeline). Copies are in `redesign/site/assets/animation/` (a-how-it-flies.mp4, a-poster.webp, `build/`). K09-L records (previous design, not concept A): `redesign/showcase/animation/k09l-how-it-flies.mp4` 1280x720, 30 fps, 600 frames, 20 s, 4.6 MB; `render_build.py` is the K09-L build film (Workbench engine); `assembly_check.py` is the 3-D assembly gate.

Gap to target: every film is 1280x720 at 24 fps (build) or 30 fps (flight); target is 1920x1080 at 60 fps. None is a 60-120 s main film, a 20-30 s highlight or a mechanism clip. The only short film (20 s) is the flight explainer; the build film is 13.9 min.

## 3. Rendering software and engine

- Blender 4.5.14, headless (`blender -b --factory-startup -P script -- <mode>`), engine `BLENDER_EEVEE_NEXT` (`render_build_a.py` line 560; `make_stage` in `showcase/animation/render_animation.py` line 196 sets it too).
- Samples: `--samples` default 12 in the build film, 16 in the flight explainer. EEVEE settings from `make_stage`: shadows on, shadow_ray_count 2, shadow_step_count 8, ray tracing on at resolution scale 2 (`--no-rt` turns it off), fast GI on. View transform `Standard`, look None, so design-token colours stay true.
- Not Cycles. Cycles is used only by the still-figure kit `redesign/blender/render_kit.py` / `render_figures.py` (README: 12-18 s per 1600x1000 figure at 48 samples on the RTX 4060, 38 s CPU only).
- Hardware: RTX 4060 Laptop GPU (nvidia-smi); i7-13700H (from `redesign/blender/README.md`).

## 4. CAD import path (is it the current concept A?)

- Build film: `bb.build(False, MODEL_A)` with `MODEL_A = redesign/qp/A/cad/model` (`render_build_a.py` lines 65, 324). `blender_backend.py` builds meshes procedurally from the part specs in the model modules (prisms, revolves, lofts, meshes, fillets), not from STL or GLB. Steps and motions come from `qp/A/cad/a_assembly_plan.py` (66 steps; a_assembly gate PASS 113/113 parts per FILM-AUDIT.md) and text from `a_build_steps.py`. Wire routes come from `qp/A/cad/out/wire_inventory.json`.
- Flight film: same `bb.build` with `DBF_CONCEPT=a` (`--concept a`) pointing at the same model directory.
- So it is the current concept A CAD, read live at render time, not a stale export. Not verified: that the latest D-208/D-210 hub and arm changes are in the film frames (no geometry diff done; the build film was last rendered 2026-11-18 06:34, the flight film 2026-11-16).
- GLB exporter `redesign/blender/export_glb.py` exists. FEA result GLBs exist in `qp/A/structures/out_fea/` (`hub_F1.glb`, `hub_F2.glb`, `hub_S1.glb`, `hub_S2.glb`); no film imports them.

## 5. Camera paths

- Build film (`render_build_a.py`): per-step camera views (target xyz, azimuth, elevation, distance) computed by Blender in a `--camplan` pass (about 1.5 min) and cached in `cam_plan.json`; the renderer refuses a stale plan. One keyframed shot: smoothstep (`smooth()`) between the views of consecutive steps, distance interpolated geometrically. Move duration `cam_duration` is 1.5 s per octave of zoom plus 1 s per 40 degrees of swing plus a shift term, clamped 0.6 to 4.2 s. Stages open wide behind a title card and glide in; a checkpoint pulls back and the next move starts from that view. X-ray steps A3-A5 follow the plug along the see-through spar; servo steps D1-D5b view from the aft side (az 140-200).
- Known jerks (FILM-AUDIT.md): before the fix 24 of 66 steps had a camera cut (0.7 s move with zoom over 1.5x, azimuth swing over 25 degrees or target shift over 0.35 m). After the fix none are reported; the one fast move left is C7 to C8 (0.4 m pan down the fin tube in 3 s, continuous). Remaining pops are material swaps: wing solid to x-ray at A3 and back at B1.
- Flight film (`render_animation.py`): authored analytic state curves (`state(t)`, `seg`, `bump` easing) and a fixed camera framing; no solver.

## 6. Lighting and materials

- Four AREA lights repositioned per frame relative to the camera azimuth (key -50 az / 55 el, energy 6.5; fill 35/12, 3.2; rim 170/40, 5.0; top 0/89, 1.2; distance 2.6 m), plus a stage-gradient world (design tokens stage-bottom / stage-top, strength 0.45) and a floor with a soft contact-shadow blob (`make_stage`).
- Materials: `blender_backend._principled` per part from the model's material info; film overrides: moving part orange `#E0661A` (rough 0.45), fabricated part teal `#13897F`, ghost `#8FA6C0` alpha 0.20, ghost spar `#2E4A6B` alpha 0.38 (transparent shadows disabled), tape `#AEB9C6`. Blade blur copies (alpha) in the flight film. No textures, no HDRI, no depth of field, no Blender motion blur.

## 7. Animation scripts and what drives motion

- All motion is hand-keyframed or analytic. Build film: part translations from `a_assembly_plan.STEPS` (direction, travel; short moves lengthened to MIN_TRAVEL_MM for legibility, A3-A5 use VIS_TRAVEL_MM), smoothstep timing from `timeline()`; wire reveal curves (bevelled curves, fraction shown) from the wire inventory.
- Flight film: `state(t)` returns x, z, theta (pitch 90 to 0 to 90 deg), bank, prop rate and elevon pitch/roll as authored piecewise functions; the ground track `_XTAB` is a table in the file. **No executed-simulation output is read.** It does not read `qp/A/sitl/runs/*/case.csv` (cases b3, b5, b7, d3, d5, d7, d_chain and others exist) or `a_plant.py`.
- Mechanism motion (servo to horn to pushrod to elevon): not animated. Build steps D1-D5b only drop the servo, arm, horn, pushrod and clevis pin into place. The flight film rotates the elevon rigidly about its hinge (hinge from the joints, axis Y of WNG-001 through the joint origin) and highlights it orange; servo, horn and pushrod do not move with it.

## 8. Scene construction

One scene per Blender process: `bb.build` creates all part objects and wire meshes, all hidden at start; per frame `pose(t)` unhides and positions parts by step (`part_mode`: normal / move / fab / ghost), places the four lights and the camera, and writes the 2-D anchor of every callout (projected through the real camera) to JSON for the overlay. Camera: 50 mm lens, 36 mm sensor, clip 0.02-100 m.

## 9. Technical overlays and labels

Pillow post-pass on each PNG (not in Blender): title cards (fade 0.5 s in, 0.7 s out), step card (id, instruction, tools, key check), callout labels with leader lines (only if the part is on screen), dimension lines on cut tubes, make-it banners, checkpoint cards, stage dots and progress bar. Fonts: IBM Plex Sans if installed, else Segoe UI. The flight film has a lower-third phase label, phase dots, progress bar, pitching-moment arc, thrust and elevon callouts. No data plots, FEA colour maps, simulation traces or axes in any film.

## 10. Export settings

Frames: PNG (RGB) from EEVEE into `--work` (default `%TEMP%/a_build_film`, GBs). Encode: Blender VSE, MPEG4 container, H.264, `constant_rate_factor` MEDIUM by default (driver lowers it to fit `--max-mb` 13.0; the shipped build film is 19.8 MB at the lowest-quality preset per FILM-AUDIT.md), GOP 2 x fps, preset GOOD, no audio. `redesign/showcase/tools/mp4_faststart.py` moves the moov box to the front (replaces `ffmpeg -movflags +faststart`); `publish_assets.py` applies it and copies to `redesign/site/assets/animation/`. Resolution and rate constants: `W, H = 1280, 720`, `FPS = 24` at lines 69-70 of `render_build_a.py`.

## 11. Performance (render time per frame, workers, dedupe)

- Parallelism: `--workers` default 3 Blender processes on disjoint frame ranges balanced by `moving_frames()`; overlays in a ProcessPoolExecutor of 8; `--preview` uses 1 worker, half size, every 4th frame.
- Dedupe: frames identical to the previous are not rendered; overlays are one per distinct (picture, card state). The build film's 20,009 frames map to 7,124 distinct pictures (FILM-AUDIT.md), 36 percent.
- Logged timing: the script prints `FRAME n / N` and `RENDER_TOTAL s` but no log of a full run is kept in the repo (searched `*.md`, `*.txt`, `*.log`). The only stated figure is the script docstring "about 1 h, workers in parallel", plus about 1.5 min for `--camplan`.
- Derived (estimate): 1 h wall for 7,124 distinct 1280x720 pictures = about 0.5 s wall per picture, about 1.5 s per picture per worker including overlay and encode.

## 12. Coverage against the target

| Target scene | Existing coverage | Gap |
|---|---|---|
| 1 Overview | a-how-it-flies.mp4 (20 s, 720p30): hover, transition, cruise, landing with labels | No hero exterior shot, no spec/mass/dimension reveal, not 1080p60, authored not simulated |
| 2 CAD close-ups (wing, propulsion, interfaces, structure, controls) | Build film steps show parts at 0.24-2.1 m; stills in `concept-a/renders/` and `_work/` (detail-hub, detail-fin, detail-foot, detail-avionics, detail-harness, cutaway-xray) | No orbit or dolly film per subsystem; the build film is assembly order, not a subsystem tour |
| 3 Mechanical operation (servo, horn, pushrod, elevon hinge) | Installation only (D1-D5b); elevon rotated rigidly in the flight film | No linkage kinematics: servo arm angle, pushrod travel and elevon deflection not coupled; no travel limits shown |
| 4 Physics validation from executed simulation | None | SITL runs exist (`qp/A/sitl/runs/*/case.csv`, `a_plant.py`) but nothing reads them. Project memory says no new simulation round until Dillon finalizes; playing back existing logged runs needs his confirmation |
| 5 Engineering analysis (FEA) | None in any film | FEA exists: `qp/A/structures/fig/` (fea-arm-fos, fea-arm-along, fea-arm-hub-map, fea-coverage, fea-hub-F2, fea-hub-S2, fea-hub-margin) and `out_fea/` (hub_F1/F2/S1/S2.glb, npz fields, result_*.json) |
| 6 Final presentation | Stage posters only | No title or closing sequence, no mass/cost/margin summary, no highlight cut |

Formats missing: 1920x1080, 60 fps, 60-120 s main, 20-30 s highlight, mechanism clips. No audio anywhere.

## 13. Ranked improvements (extend existing scripts)

1. Resolution and fps flags: `render_build_a.py` constants `W, H, FPS` (lines 69-70) become CLI options (defaults unchanged), applied in `blender_encode` and the Pillow overlay scale `k`. Prerequisite for everything else. Low effort.
2. Short-film mode in `render_build_a.py`: a `--shot-list` JSON (camera keyframes, visible parts, duration) reusing `cam_at`, `lerp_cam`, `smooth`, `pose`, `part_mode` for the 60-120 s main, the 20-30 s highlight and scenes 1, 2 and 6. Orbit and dolly keyframes feed the same `cam_at`. No new pipeline.
3. Mechanism clips: extend `pose()` (in `render_build_a.py`, with the hinge lookup from `render_animation.py`) with a linkage solver: servo arm angle to pushrod translation to horn angle to elevon deflection about the joint axis, using CAD joints and part ids MEC-001..005. Each part is a rigid object rotated about its own pivot per frame. Medium effort.
4. Physics from executed simulation: in `render_animation.py`, replace `state(t)` with a resample of a chosen `qp/A/sitl/runs/<case>/case.csv` (position, attitude, motor and elevon commands), keep the authored curve as fallback, add a HUD (time, altitude, pitch) in the Pillow stage. Medium effort; existing runs only.
5. FEA scene: import `qp/A/structures/out_fea/hub_*.glb` through Blender's glTF importer into the `make_stage` scene (check whether they carry vertex colours; not checked), or at minimum composite the `fig/fea-*.png` images in the Pillow overlay. Low to medium effort.
6. Overlay spec: drive the existing `pill`, `place_labels`, `overlay` functions from a label list for scene 2 (subsystem names, masses from `qp/A/params-A.json`, dimensions). Needs 1080p scaling from item 1.
7. Encoding: keep the Blender VSE encode and `mp4_faststart.faststart`; raise the `--max-mb` cap for 1080p60. Install ffmpeg only if concatenation or audio is needed (approval).
8. Polish flags: EEVEE motion blur for flight and depth of field for close-ups, set in `make_stage` and `pose`.
9. Logging: have the driver write a `timing.json` (frames, rendered count, seconds, workers, samples, resolution) so the cost below becomes measured.

## 14. Estimated full-render cost (estimate)

Basis: build film about 1 h for 7,124 distinct pictures at 1280x720, 12 samples, 3 workers (script docstring, no timed log). Assume cost scales with pixels: 1080p is 2.25 times 720p.

- Existing build film at 720p24: about 1 h. At 1080p24: about 2.3 h. At 1080p60: moving frames grow about 2.5 times; static holds still dedupe; about 4-6 h (wide range).
- New short films have little dedupe. About 1.5 s per frame per worker x 2.25 = 3.4 s per frame per worker, 3 workers, so about 1.1 s per frame wall. Main 60-120 s at 60 fps (3,600-7,200 frames): about 1.1-2.2 h. Highlight 25 s (1,500 frames): about 30 min. Each 5-8 s mechanism clip (300-480 frames): about 6-9 min. Whole programme (main, highlight, five mechanism clips): about 2.5-4 h wall.
- Samples 32 or motion blur multiply this by about 1.5-2.5.
- Disk: PNG frames at 1080p about 1.5-3 MB each; 12,000 frames is about 20-35 GB in `%TEMP%`.

## 15. Not verified

- Bitrate, H.264 profile, pixel format and colour tags of the films (my parser does not read them; ffprobe absent).
- Whether `a-how-it-flies.mp4` (dated 2026-11-16) matches the current CAD.
- Whether the FEA GLBs carry colour data.
- Any measured render-time log (none found in the repo).
- Whether ffmpeg exists somewhere outside the searched locations (full-disk search timed out).
