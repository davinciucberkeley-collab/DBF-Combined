# Film progress, T-027 (parents R-VID-02, R-VID-04; feeds R-VID-03/06/07)

Date 2026-11-18. Implements PIPELINE-AUDIT.md improvements 1, 2, 8 (flags only) and 9 in `redesign/showcase/concept-a/render_build_a.py`. Nothing committed. `blender_backend.py` not touched. Full render NOT run; only a preview.

## What changed (render_build_a.py, line numbers as of this edit)

| Item | Function / place | Lines |
|---|---|---|
| 1. Resolution and rate | `apply_res`, `add_res_args` (CLI `--width --height --fps`, defaults 1280, 720, 24); `RES_FLAGS` passes them to every Blender worker and the encode; `blender_encode` gets `--fps`; overlay scale is now `k = picture width / BASE_W (1280)` instead of `/ W`; `_init` gives spawned overlay processes the run's fps | 141-151, 1121 (encode), 1321 (`_init`), 1594 (`RES_FLAGS`) |
| 2. Short-film mode | pure: `param_value`, `load_film`, `hermite_cam`, `film_at` (319-405); worker branch `if a.shot_list:` inside `blender_render` with `shot_modes`, `film_pose` (741-818); Pillow `_init_film`, `film_overlay`, `_film_job` (1502-1590); driver `film_driver`, `contact_sheet` (1604-1700), `driver()` branches on `--shot-list` (1733) | as listed |
| 8. Polish flags | `--dof` (camera DOF, focus on the target each frame via `set_focus`, f/5.6) and `--motion-blur` (`render.use_motion_blur`), worker and driver options, off by default | 697, 780, 1039 |
| 9. timing.json | `write_timing`; short film writes `film/timing.json`; the build film writes `animation/timing.json` after a full run (or `--timing PATH` for test frames) | 1598 |
| Shot list | `redesign/showcase/concept-a/film/shots-main.json` (scenes S1, S2, S6 drafted; S3, S4, S5 placeholders tagged TODO) | new file |

Reuse and deviations from the audit text: the film mode reuses `cam_view`, `look`, the four-light rig, `tint` with the film materials (`MATS`: ghost, ghost_spar, fab, move), `smooth` is not used. Camera interpolation is a cubic Hermite with Catmull-Rom tangents through all keys of a scene (`hermite_cam`, distance geometric like `lerp_cam`), because `smoothstep` between keys stops the camera at every key; the C1 path has no velocity jump at shot joins. `cam_at`, `lerp_cam` and `part_mode` belong to the build-film timeline (they need its step rows) and are not called; the shot's `modes` map plays the part_mode role. Geometry is the live concept A CAD (`bb.build(False, MODEL_A)`, parts in the assembly plan, at rest pose), no stand-ins.

Shot-list rules (enforced by `load_film`): keys per shot `{t, target, az, el, dist}`; a scene's keys form one path; the first shot of a scene needs a key at t = 0; a key that does not come after the previous one raises "cut inside a scene"; cuts only between scenes. Per shot: `parts` ("all" or id prefixes), `modes` ({prefix: normal|ghost|fab|move|hidden}), `title`/`sub` lower third (0.4 s fades), `tag` (top-right, e.g. ILLUSTRATIVE), `todo` (placeholder card), `card` (closing card; values read from `qp/A/params-A.json` at draw time).

Closing card values (all read from `redesign/qp/A/params-A.json`): `mass/basic_cad_kg` 1.27324 kg shown 1.27 kg (CAD basic, no growth), `req/mass_gate_kg` 1.47 kg, `box/packed_m/0` 0.90 m. Note: params-A.json has no wing-span key. The span line uses `box/packed_m[0]` (packed length, one piece, props on) and is labelled "Span (packed, one piece)"; it equals the CAD wing core extent (WNG-001 y -0.45 to +0.45 m, measured from the live CAD in this task). Scene 1 text also cites `cad3d/parts` (113). Tags: scenes 1, 2, 6 are camera moves of a static aircraft, so no ILLUSTRATIVE tag; placeholders S3-S5 carry ILLUSTRATIVE until their data-driven versions replace them (S3 should then say kinematics, S4 simulation, S5 FEA).

## Commands to reproduce

```
# preview (what was run): 1080p60, every 40th frame, 12 samples, 3 workers, scenes 1, 2, 6
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --scenes S1,S2,S6 --width 1920 --height 1080 --fps 60 --every 40 --samples 12 --workers 3 --preview --contact redesign/showcase/concept-a/film/preview-contact.png
# full short film (NOT run): same without --every / --preview / --contact; MP4 to --film-out (default film/film.mp4); optional --dof --motion-blur
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --width 1920 --height 1080 --fps 60 --samples 24
# build film unchanged: python redesign/showcase/concept-a/render_build_a.py   (1280x720 @ 24 by default)
# build film dry check (cheapest mode, no render): blender -b --factory-startup -P redesign/showcase/concept-a/render_build_a.py -- render --out %TEMP%/a_build_film --camplan
```

## Measured (preview, this machine: RTX 4060 Laptop, i7-13700H)

From `film/timing.json`: 53.0 s of film (S1 15 s, S2 25 s, S6 13 s) = 3,180 frames at 1920x1080 @ 60; 80 frames rendered (every 40th), 3 workers, 12 samples, ray tracing on, DOF and motion blur off. Whole run 143.6 s wall: Blender start plus CAD build plus frames 137.0 s, overlay 2.3 s. Frame loop alone (per worker) 31.9, 33.2, 33.8 s for about 27 frames each: about 1.24 s per frame per worker at 1080p, 12 samples. So the three workers share one GPU and still reached about 1.24 s per frame each. Start-up per worker is about 100 s (CAD build with its "CUT NOT VERIFIED" log lines, pre-existing).

Estimate (not measured) for the full S1+S2+S6 render of 3,180 distinct frames at 12 samples: 3,180 x 1.24 s / 3 workers is about 22 min plus start-up, if the per-frame cost holds with three workers; static holds dedupe (the card shot, 6 s). Scenes 3-5 are not included.

Build-film dry check: `--camplan` ran in 77 s, wrote 66 steps and the script loads and the default arguments are unchanged. The refreshed cam_plan.json differed from the committed one only by 1e-4 rounding (the CAD moved since the committed plan, D-210), so the original file was restored; the driver regenerates it anyway. A full build-film render was not run, so pixel identity with `a-build.mp4` is NOT verified; the defaults of W, H, FPS, the overlay scale (k = 1.0 at 1280) and the encode are unchanged by construction.

`--dof` and `--motion-blur` were NOT exercised. Motion blur in EEVEE needs animated or frame-stepped objects; here objects are posed directly per frame, so the flag probably has no visible effect until `pose` keys the transforms (unverified).

## Known defects seen in the contact sheet (`film/preview-contact.png`)

1. Close-up framing is rough: 2.1 (wing) starts with a prop arm and blade crossing the frame and the wing target sits low; 2.2 propulsion keeps the prop partly outside the frame; 2.3 (hub) is cropped at the left; 2.4 (structure) looks at a motor and prop with the hub, the x-ray spar is barely in view, so shot 2.4 needs a new target and az; 2.5 (control) works but the servo and horn are small and the red servo lead dominates.
2. Props and arms block the line of sight in several orbit and close-up views; the real fix is per-shot camera targets after a look at stills, or hiding the props in the structure shot.
3. Material pop at shot joins where `modes` change (2.3 to 2.4 wing core turns x-ray, 2.4 to 2.5 unchanged); there is no cross-fade.
4. Scene 6: the card shot starts abruptly (the card appears at the first frame of 6.2 while the lower-third style cards elsewhere fade in); the 6.1 to 6.2 camera shift (target z -0.17 so the aircraft sits above the card) is done at the end of 6.1, so the last seconds of 6.1 show the aircraft pushed up the frame.
5. No ILLUSTRATIVE tag in S1, S2, S6 by design; wires (red phase and servo leads) are visible in the x-ray shots and also in the normal overview as short stubs near the hub.
6. Lower-third text is small at 1080p (it scales with k = 1.5 from the 1280 layout); long subs wrap to two lines. Unchecked at full resolution; the sheet is downscaled.
7. Preview was at 12 samples with ray tracing; edges look soft in thumbnails, final quality not judged.
8. Wing sits on a floor with a contact blob at the centre only; the floor shadow does not follow the orbit radius. Not a regression (same stage as the build film).

## Not done

Scenes 3, 4, 5 (placeholders only), audio, ffmpeg-free concatenation of scenes (the full-film path encodes all scenes as one MP4 through the Blender VSE, scenes cut together), `--dof` / `--motion-blur` verification, a full render of any film.
