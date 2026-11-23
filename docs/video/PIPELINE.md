# Film rendering pipeline, concept A (T-032, R-VID-14)

Written 2026-11-18, revised 2026-11-22 after the doc was followed once (record: `docs/video/PIPELINE-FOLLOW-2026-11-22.md`). Everything below was read from the scripts, `film/timing-T031-*.json`, `film/timing-T030N-*.json`, `film/render-T03*.log` and `docs/video/PLAYBACK-T033.md`; section 9 says which commands were run on 2026-11-22 and which were not.

## 0. Pins and hash basis (read first)

| Pin | Commit | What it fixes |
|---|---|---|
| Document check | `4ebfe0a5` (HEAD of `redesign/v1` on 2026-11-22) | The text of this file and the commands in it were followed from a checkout of the film pin below (a `git worktree` at that commit), not from `4ebfe0a5`: see next row |
| **Film pin (reproduce the shown films from here)** | **`0da084ab`** (2026-11-18 23:46, "Concept A films re-encoded from ebb89693") | Final shot lists, the four videos, the T-030-N timing records, the renderer `render_build_a.py` (blob `db3a76040c95`, unchanged since `ebb89693`) and the CAD that drew the films. Check it out with `git worktree add <short path> 0da084ab` (a short path matters on Windows) |

- **A render from HEAD is a different film.** The stage is built from the current model. Between `0da084ab` and `4ebfe0a5`, 46 files under `redesign/qp/A/cad` changed (git diff `--name-only`), and `render_build_a.py` changed in 7 lines (build-film data only, none in film mode: six step-group titles and lists, `ONE_SIDE` gains `C1b`, `EXTRA_PTS['D0']` x 0.083 to 0.064; `git diff 0da084ab 4ebfe0a5 -U0`). The films show the 2026-11-18 configuration (115 parts, T-Motor MN2212 motors, params-A.json at that date). The aircraft at HEAD has 129 parts and SunnySky X2216 motors (`docs/audits/2026-11-22-review-round-2.md`, `qp/A/params-A.json` T-083 notes). The film inputs themselves (both shot lists, the SITL and FEA record files) are byte-identical at `4ebfe0a5` and `0da084ab`. The film content is superseded as a picture of the aircraft; the process in this file is still valid.
- **Hash basis.** Two bases are given for text files because the repo is checked out with `core.autocrlf=true` on the Windows machine, so working copies are CRLF and the hash of a working copy depends on that setting. (a) **Git blob**: `git rev-parse <commit>:<path>` (SHA-1, 12 hex shown) and SHA-256 of the committed bytes, `git cat-file blob <commit>:<path> | sha256sum`; this is LF and the same on any machine. (b) **Working copy on this machine (CRLF)**: `sha256sum <path>`; this is what the driver writes into each `timing-*.json` under `sources`, so a Linux or `autocrlf=false` checkout will not match those stored values for text files. Binary files (mp4, glb, npz) are the same on both bases and are shown once. `git ls-files -s` gives the same SHA-1 as `git rev-parse :path`.
- Video files: a re-encode gives the same decoded pictures but not the same file bytes (the container tail differs), so compare the **decoded-stream hash** (`ffmpeg -v error -i F -map 0:v:0 -f hash -hash sha256 -`), frame count and duration, not the file hash. Measured 2026-11-22, section 9.
- Analysis categories used in the films: kinematics (S3, mechanism clips), flight dynamics (S4 playback of an executed SITL run), FEA (S5, stored results), interference (camera clearance check), illustrative (prop spin, camera moves, stage). Every moving-part film carries an on-screen tag of this category (SIMULATED or illustrative).

## 1. Tools and machine

| Item | Value | Source |
|---|---|---|
| Renderer | Blender 4.5.14 LTS, EEVEE (ray tracing on), `C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe` (override with env `BLENDER` or `--blender`). A Blender 4.2.3 folder sits beside it: do not use it | `render_build_a.py` `BLENDER_DEFAULT`, PIPELINE-AUDIT section 1, `ls` 2026-11-22 |
| Driver, overlay | system Python 3.14.2 with Pillow 13.0.0 (`python -I` works) | measured 2026-11-18 and 2026-11-22 |
| Encode | Blender's built-in FFmpeg through the VSE (`encode` subcommand): H.264 in MP4, CRF MEDIUM, GOP 2 s, preset GOOD, no audio | `blender_encode` |
| Checking tools | FFmpeg/ffprobe 9.0.2 (WinGet, on PATH) for frame counts, decode and decoded-stream hash; since 2026-11-19 (PD-006 superseded). The renderer does not use it | `docs/verification-report.md`, `ffmpeg -version` 2026-11-22 |
| Machine | RTX 4060 Laptop GPU, i7-13700H (20 logical cores) (FILM-PROGRESS T-027). It is shared: other agents run Blender and Python on it, which changed measured times by a factor of 3 to 19 on 2026-11-22 (section 3) | FILM-PROGRESS, `tasklist` 2026-11-22 |
| Disk | PNG frames go to `%TEMP%\a_film` (outside the repo). That folder held 14,019 entries on 2026-11-22 (the T-031 and T-030-N frames, `lab_*`, `n_*`, `raw_*`, `_list.txt`, `old_maps/`). **Film mode uses `a_film` as its default `--work` folder, and every film-mode run (including `--cam-check`) deletes `map_*.json` there and may overwrite its frames: always pass `--work <scratch>` unless you mean to redo that run.** | script `film_driver` (line "work = ... a_film"), 2026-11-22 follow |

## 2. Films, scripts and inputs

One script does everything: `redesign/showcase/concept-a/render_build_a.py` (never touch `blender_backend.py`; it is not in this commit tree, the name is historical). Defaults (1280x720 @ 24, build film) are unchanged; film mode starts with `--shot-list`.

All paths are under `redesign/showcase/concept-a/` unless they start with `qp/`, which means `redesign/qp/A/...`. Inputs as of the film pin `0da084ab` (unchanged at `4ebfe0a5`).

| Film | Length | Inputs (git blob SHA-1 12 hex; SHA-256 of committed bytes; SHA-256 of CRLF working copy) | Output (file SHA-256; decoded-stream SHA-256) |
|---|---|---|---|
| Main | **119.9 s, 7,194 frames**, 1080p60 | `film/shots-main.json` `1001c3eba308`; `f038748916349caa6947d2c5a392102dcbec5a4ad4954746a296da2dd9c51e6e`; CRLF `aaa8331bfeaaca6e49b6d5c62265722081884f4e9d62c6657e099ce165e209ba`. Timing record `film/timing-T030N-main.json` `446b37e4ed41`; `7cede9dfdd76a5a87e7433d323023c3f322914be6b303b291871d38560b022cd`; CRLF `b73307163b63950f520bc388318f16710c9f43ead269b3d47267327bd23b4cad` | `film/film-main-1080p60.mp4` `7e229b80b4e413bb9b46a287103fc725786ae24b2c963a910c1f3cc179a70e7c`; decoded `86a9268e2ff71b82ed0a9ecb4842e2f3d9c928141948b2b89db4075e83667398` |
| Highlight | 24.2 s, 1,452 frames | `film/shots-highlight.json` `5c5b92d5fe3d`; `3f9d58955d88fbfb95f6cd5f13a2bba86e6efda425a6796d6058f11f3b0ece5e`; CRLF `017bcd279888dd582f3ed215c42e8da5ccf1372b91075e438c4a5c3da3fc99cd`. `film/timing-T030N-highlight.json` `76cc3f1e1d60`; `498bb8f1e3748c83b2178bd6eb313199a3fefcd51c3cc61ebb3257476403a049`; CRLF `d837a20ee77782a37bdf61702daad415f2b7840d24bda1f6c77c4c272a1e4167` | `film/film-highlight-1080p60.mp4` `15f3e46b8cad82e326647ab1aa489f3b76ca82333af5755092d2ec5f6810bfd0`; decoded `7d55bd4214c168ccff9d7f55a1e5e0530b88c236fd4de5a3973d7ed4ab866ccf` |
| Mechanism clips | 11.8 s (708 frames) and 6.0 s (360 frames) | `clips` field of `shots-main.json`; list files `film/clips/list-3.1.txt` `a51879481e6e`, `list-3.2.txt` `01ae89c16c97` (names `lab_02466..03173`, `lab_03174..03533` of the main run) | `film/clips/clip-elevon-linkage-*.mp4` (hashes in section 5) |
| Build film | 66 steps, 833.7 s, 1280x720 @ 24 (T-026 audit) | `qp/A/cad/a_build_steps.py`, `a_assembly_plan.py`, `cam_plan.json` (regenerated by the driver) | `animation/a-build.mp4`, `stage-NN.mp4/.webp`. **Not re-run or re-hashed on 2026-11-22**; `render_build_a.py` at HEAD differs from the pin in build-film step data (section 0) |

The film shows 7,194 frames because shot 2.6 "Exploded view" was added at the end of S2 in T-030-N (section 12). Earlier values in this file (116.0 s, 6,960 frames, `timing-T031-*.json`) belong to the first T-031 render and are kept only where marked T-031.

Record files the films read (all git-tracked since `fe02c9d5`, so a clean clone has them; hashes also stored in each `timing-*.json` under `sources`; the main run lists eight, the highlight run six). Regenerating the GLBs: `python -I qp/A/structures/fea_hub_figs.py --tag d209` after `fea_hub.py --level 0 --tag d209 --fields`.

| File | git blob SHA-1 @ pin | SHA-256, committed bytes (LF) | SHA-256, CRLF working copy (= timing JSON) |
|---|---|---|---|
| `qp/A/sitl/runs/Z5_gb0/case.fwd.csv` (1,098,835 B CRLF) | `f3cd2306c896` | `05d747e9720c334853876c4f124d61b9def4190cc232d2844f67889e56e6deab` | `07729f67e48468591d023699e1e381b4a10a004a3cf04a2c702a57ed2cfa7bc8` |
| `qp/A/sitl/runs/Z5_gb0/result.json` | `d05259bf4f96` | `995e3267c40c594dcb8a892144de9314d7e8933aef4e1003d743a82be0b31ed5` | `4cf658e3dce43c8f71f5184fafbb8e48654668882e17a5e71fff409ae0f8633c` |
| `qp/A/sitl/runs/Z5_gb0/sum.json` | `2fc68de9e65e` | `3941c68c595353e65df7e641f8e99d97ebc41d03d2aa4fab054a4933aeafc9a1` | `9fecf1a1a27449f28febc20a5bedd5837dcf80f957c99c77d7bf297875abd933` |
| `qp/A/structures/out_fea/hub_F2.glb` (binary) | `ceaf316eedac` | `12e1aea35baaca86efa53519676732bd4cc9dd2dea63d0010474707a3779475d` | same |
| `qp/A/structures/out_fea/hub_S2.glb` (binary) | `0e490708c10e` | `a73cb30fd625c67eb98a58f425cb122b49479e42e525c4163ac8623e648673fc` | same |
| `qp/A/structures/out_fea/hub_fields_L0_d209.npz` (binary) | `453a262e8065` | `ef8e0173b747d911e3b876b81e383d07646e302d6a5810fd6818fcde7e70169c` | same |
| `qp/A/structures/out_fea/hub_result_L0_d209.json` | `20883315c3b1` | `c9143e81c6f8918d4782ee849a58ab6f75a3003faa97d05b47cd826bb36f3c1b` | `82e50dc5a7cd51a08010a782045277c7ced32efc589b1e2c57afc71185603c58` |
| `qp/A/structures/out_fea/result_L0_current_d210.json` | `dd7ee4f9bac4` | `c74fc45602ce788eaee0b50488dcc9a0c1eb480421f5bc02a1c3f83f4b9e7127` | `dae6f0ed6e155422d761cc48b9fd688c887977019f735d9501822d3198cdfbe6` |

Also read: `qp/A/mechanism/out/linkage_kinematics.{csv,json}` (AR-001), `sitl/cad_mass.json`, `structures/fig/fea-arm-along.png`, `qp/A/params-A.json`; the CAD itself is built from `qp/A/cad`. The commit hash drawn on the closing card is read from `git rev-parse` at draw time: render from a clean tree for it to read without "-dirty".

## 3. Reproduce each film (commands, all from the repo root, bash syntax)

Let `R=redesign/showcase/concept-a/render_build_a.py` and `F=redesign/showcase/concept-a/film`. Use ABSOLUTE `--film-out`, `--timing` and `--work` paths (the encode runs inside Blender, which resolves relative paths against its own start folder; the driver passes an absolute path to it). Run from a checkout of the film pin (section 0). **Give every command its own `--work` folder** (the doc's earlier main cam-check and S3 commands wrote into `%TEMP%\a_film`).

1. Camera clearance first (no rendering). Measured 2026-11-22 on the shared machine: 1,417 s (main) and 208 s (highlight), against 75 s and 78 s on 2026-11-18; the `seconds` field inside the JSON (6.8 and 1.8 s) is only the check loop, the rest is Blender start-up and building the CAD stage. Section 6.
2. Main film from scratch (reconstructed from the log header and timing: 3 workers, 24 samples, ray tracing on, DOF and motion blur off):
   `python $R --shot-list $F/shots-main.json --width 1920 --height 1080 --fps 60 --samples 24 --workers 3 --work <ABS scratch>/a_film_main --film-out <ABS>/main-check.mp4 --timing <ABS>/main-check-timing.json`
   Written to a scratch name so that the committed film is not overwritten; use `--film-out $F/film-main-1080p60.mp4` only to replace it on purpose. **Not run on 2026-11-22**: the shown film was NOT made by this single command. It was the T-031 render (6,470 distinct renders, 5,298 s), then T-030-N: `--changed-from` partial render of 801 frames (773.1 s), then `--skip-render` overlay and encode (447.4 s), see section 12. A from-scratch render of the 7,194 frames is estimated at 5,050 s render (6,704 distinct pictures x 0.753 s wall each, the T-031 rate) + 136 s overlay + 311 s encode, about 92 min on an unloaded machine, and about 6 h at the rate measured on 2026-11-22 (item 4): estimates, not measurements.
3. Highlight (own work folder so it does not overwrite the main frames):
   `python $R --shot-list $F/shots-highlight.json --width 1920 --height 1080 --fps 60 --samples 24 --workers 3 --work <ABS scratch>/a_film_hl --film-out <ABS>/highlight-check.mp4 --timing <ABS>/highlight-check-timing.json`. Not run on 2026-11-22 (estimated 20 min unloaded, T-030-N: 95.5 s for the overlay-and-encode part alone).
4. **One-scene check, run on 2026-11-22 (`--scenes S3`, the mechanism scene; this is the shortest full render the doc describes)**:
   `python $R --shot-list $F/shots-main.json --scenes S3 --width 1920 --height 1080 --fps 60 --samples 24 --workers 3 --work <ABS scratch>/s3 --film-out <ABS>/s3-check.mp4 --timing <ABS>/s3-check-timing.json`
   Result: 1,080 frames, 18.0 s, 1,009 distinct renders, 3,585 s wall (render 3,413 s, overlay 102.0 s, encode 63.6 s), 9.21 s per rendered frame per worker, against 1.94 s in the T-031 record. The old estimate "about 12 min" for S3 assumed the unloaded 1.94 s; plan on 12 to 60 min depending on what else is running. **Side effect:** with a `clips` field in the shot list the driver rewrites the tracked `film/clips/list-3.1.txt` and `list-3.2.txt` in scene-local names (`lab_00012..00719`), which no longer match the main run. Restore them afterwards: `git checkout -- $F/clips/list-3.1.txt $F/clips/list-3.2.txt`. On 2026-11-22 the lists of the original checkout were also found rewritten after this run (cause not found), so run `git status` afterwards and restore every changed tracked file.
5. Mechanism clips: section 5. If `%TEMP%\a_film` has been cleared, the S3 run in item 4 is the way to get frames (and its own clip lists), at the cost above.
6. Build film (unchanged, 1280x720 @ 24, about 1 h, estimate from the script docstring): `python $R`. Dry check without rendering: `blender -b --factory-startup -P $R -- render --out %TEMP%/a_build_film --camplan` (77 s, T-027). Not run on 2026-11-22.
7. Preview of a scene range or the whole list (contact sheet, no encode): `python $R --shot-list $F/shots-main.json --scenes S4,S5 --width 1920 --height 1080 --fps 60 --every 60 --samples 12 --workers 3 --preview --work <ABS scratch>/prev --timing <ABS>/timing-X.json --contact <ABS>/preview-contact-X.png`. Not run on 2026-11-22.
8. Verify the output by decode (section 7).

Wall times of record (`timing-*.json`, 3 workers, 24 samples, 1920x1080), unloaded machine, 2026-11-18:
- T-031 first render, main (116.0 s, 6,960 frames): 5,298 s (88.3 min: render 4,870 s, overlay 142 s, encode 287 s), 6,470 distinct renders, 1.94 s per rendered frame per worker (frame loops 4,781 / 4,110 / 3,651 s, so the last worker's slice is cheaper; the render waits for the slowest). Highlight T-031: 1,208 s (render 1,104 s, overlay 43 s, encode 62 s), 1.73 s per frame.
- T-030-N, main (119.9 s, 7,194 frames), `timing-T030N-main.json`: overlay 135.9 s + encode 311.4 s = 447.4 s from stored frames (6,704 distinct pictures, 6,738 overlay pictures); `timing-T030N-incremental.json`: 801 of 7,194 frames re-rendered, 773.1 s, 2.46 s per frame. Highlight, `timing-T030N-highlight.json`: 95.5 s (overlay 31.1 s, encode 64.4 s).
- Clip encode from stored frames, 2026-11-22 (Blender start included): 22 s (3.1) and 12 s (3.2) for the pin lists; 2026-11-18: 23.6 s and 13.4 s. Previews at 12 samples: 0.5 to 1.2 s per rendered frame (T-028..T-030).

## 4. How a film is built (what the stages do)

1. `load_film` reads the shot list: scenes, shots (duration, camera keys with Hermite interpolation and `hold`, part modes, tags, readouts, mechanism sweeps, SITL windows, FEA panels).
2. `film_driver` starts Blender workers (`render` subcommand) on contiguous frame ranges; each worker builds the CAD stage from the current model, poses parts per frame (mechanism from AR-001 table, aircraft from the SITL log, props illustrative), writes raw PNGs, and writes `map_<first>.json`.
3. Pillow pass (8 processes): titles, tags (SIMULATED / illustrative), readouts whose numbers come from source files at draw time (`src_val`), 0.2 s dips to the stage colour at scene joins.
4. `encode` assembles the named PNG list (a name may repeat for static holds) into MP4 through the VSE. Dedupe: identical frames are rendered once.

## 5. Mechanism clips (R-VID-13)

Moving mechanisms of concept A, searched in the CAD joint registrations (`ctx.revolute` / `ctx.slider` in `redesign/subsystems/**`, `qp/A/cad`):

| Mechanism | Found | Source |
|---|---|---|
| Elevon drive: servo arm, pushrod, rib horn and elevon about the hinge line (L and R, same linkage, mirrored) | Yes, the only moving wing mechanism | `redesign/subsystems/wing/fusion/wing.py:876-877` (`ctx.revolute`, limits), `subsystems/mechanisms/fusion/mechanisms.py:518`; AR-001 kinematics, AR-002 dynamics, AR-003 swept check in `docs/analysis-records.md`; PD-005 (spec "flaps" = elevons; concept A has no flaps) |
| Motors, props | Fixed mounts; the prop is a continuous rotor, not a mechanism. Its spin appears in S4 as illustrative | `qp/A/cad/amodel`, FILM-PROGRESS T-030 M-6 |
| Landing feet (GER-001/002) | Fixed shoes and pads on the fin tips in concept A (parts in `amodel/electrical.py:685-686`, no joint). The `ctx.slider` at `subsystems/landing/fusion/landing.py:389` belongs to the K09-L landing subsystem, not to the concept A assembly (`qp/A/cad/out/assembly.json` has no slider) | as listed |
| Wing fold, tilt, flaps, retract, gimbal | None found in the concept A parts or joints | grep above; PD-005 |

(Line numbers are as of 2026-11-18 and were not rechecked on 2026-11-22.) So there is one mechanism, one clip family. Two clips are exported, both SIMULATED (category kinematics, poses from `linkage_kinematics.csv`, AR-001; swept clearance is AR-003): shot 3.1 (servo arm, rod and horn, aft quartering view; **11.8 s, 708 frames**, it starts 0.2 s into its shot) and shot 3.2 (6.0 s, 360 frames, horn and hinge, elevon x-ray, side view). Each is a range of the main-film pictures, so 3.2 carries the dip to the stage colour at its end, the readout box (servo arm deg, elevon deg, "+ = trailing edge down"), the sub-title and the tag "SIMULATED: kinematics AR-001 (D-212 rev 3)". In the 119.9 s main film S3 is frames 2454..3533 (3.1 = 2454..3173, 3.2 = 3174..3533).

Clip lists are written by the film driver, not cut by hand: the shot list has a top-level `clips` field (`list`, `shot`, `from_s`, `trim_end_s`) and `write_clip_lists` writes `film/clips/list-*.txt` in the picture names of that run whenever it builds the frame list (also with `--skip-render --lists-only`, which draws and encodes nothing). The earlier `sed -n 2221,2940p ...` recipe is obsolete and was removed. Then encode (bash; all paths ABSOLUTE and in the form Blender wants, here Windows paths):

```
B="C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe"
R='<ABS repo>\redesign\showcase\concept-a\render_build_a.py'
SRC='<ABS %TEMP%>\a_film'                        # frames of the run the lists came from
LISTS='<ABS repo>\redesign\showcase\concept-a\film\clips'
OUT='<ABS output folder>'                        # NOT the repo clips folder unless replacing on purpose
"$B" -b --factory-startup -P "$R" -- encode --src "$SRC" --list "$LISTS\list-3.1.txt" --out "$OUT\clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4" --crf MEDIUM --w 1920 --h 1080 --fps 60
"$B" -b --factory-startup -P "$R" -- encode --src "$SRC" --list "$LISTS\list-3.2.txt" --out "$OUT\clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4" --crf MEDIUM --w 1920 --h 1080 --fps 60
```

(The earlier version of this command used `<ABS>/film/clips` for the list but `<ABS>/redesign/showcase/concept-a/film/clips` for the output; that is ambiguous and is replaced by the variables above. In a bash script do not build the output name from an unquoted `...\$nm` pieces: backslash plus `$` swallowed the variable and both clips were written to one file name in the 2026-11-22 follow; use a script with plain variables.) Do not use the driver's own `--skip-render` path for this: it would re-encode the whole film. The list files and `lab_*.png` names are only valid for the run that wrote them: the committed lists match the frames in `%TEMP%\a_film`, not an S3-only run.

| Clip | Frames | File SHA-256 (committed) | Decoded-stream SHA-256 |
|---|---|---|---|
| `clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4` | 708 (11.8 s), 2,625,336 B | `06930f7087d1d05b0582bf3e73e3a53fbef91c020d0193670bdcf3fda3d6242c` | `9735f51e9cbef977af04be627310c42fb450e3d37d79641581599d2e9151038b` |
| `clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4` | 360 (6.0 s), 1,457,447 B | `1dcb7774688f9a8276563fff0a806bea016cff0cffcc8dade581db800b0e6791` | `bfc32403d7b1c7ae55ac91ffcc1361145a9d9fa7a36268de85d49f8048c1bf62` |

Reproduction results (2026-11-22, section 9): re-encoding from the stored main-run frames with the committed lists gives the same decoded-stream hash for both clips (file bytes differ only in the container tail). Re-rendering S3 from scratch gives clips with the same frame counts, size, fps and decode result but NOT the same pictures (mean squared difference per frame about 95 and 83, per-pixel differences along text and geometry edges), so a re-render reproduces the film in content and timing, not bit for bit. The cause was not isolated (candidates: GPU or driver nondeterminism in EEVEE ray tracing, overlay font rasterisation).

If a further mechanism is added, put its pose source in the same AR-xxx style, add a shot to `shots-main.json`, then cut the clip the same way.

## 6. Camera clearance check (category: interference)

`--cam-check` renders nothing. For every frame of every shot, in part-local BVHs: camera inside any visible part (closed-mesh ray parity on two axes), nearest-surface distance against `near_m` 0.05, the first non-x-ray hit on the line camera to subject (flag if more than 0.08 m before it), and camera speed and acceleration (`cam_motion`). Shot keys `los: false` (target is only a framing offset) or `los: [x,y,z]` set the subject. Output `film/cam-clearance.json` (the driver copies it there from the work folder, overwriting the tracked file: save the highlight check under a different name afterwards, and restore the main file with `git checkout`).

```
python $R --shot-list $F/shots-main.json --cam-check --width 1920 --height 1080 --fps 60 --work <ABS scratch>/cc_main
cp $F/cam-clearance.json <ABS>/cam-clearance-main-check.json
python $R --shot-list $F/shots-highlight.json --cam-check --width 1920 --height 1080 --fps 60 --work <ABS scratch>/cc_hl
cp $F/cam-clearance.json $F/cam-clearance-highlight.json     # then: git checkout -- $F/cam-clearance.json (main file)
```

Results of record, main (119.9 s, 7,194 frames), unchanged by the 2026-11-22 re-run at the film pin: 0 frames inside any part; nearest surface 0.0679 m (shot 3.2); line of sight blocked in 17 frames of shot 2.2 (fin parts during the 140 deg swing: `FIN-004-R` 11, `GER-002-UR` 3, `FIN-001-R` 2; camera never nearer than 0.27 m); view speed peak 96.7 deg/s and view acceleration 251.5 deg/s^2 (3.2), zoom rate 1.18 1/s (2.6). Highlight (1,452 frames): 0 inside, 0 blocked, nearest 0.2614 m (H2.1). The re-run's `shots` and `cam_motion` blocks are equal to the committed JSON files; only the `seconds` field differs (6.8 and 1.8 s against 2.1 and 0.8 s). The earlier numbers in this section ("blocked in 10 frames, the target motor's own prop blade") were for the 116.0 s T-031 list and are obsolete.

## 7. Verification of the output

Three checks, all run on 2026-11-22 (section 9):

1. Container metadata and count: `ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames -show_entries format=duration,size -of csv=p=0 FILE`. Expected: main 7,194 frames, 119.9 s; highlight 1,452, 24.2 s; clip 3.1 708, 11.8 s; clip 3.2 360, 6.0 s; all h264 1920x1080 at 60/1.
2. Full decode: `ffmpeg -v error -i FILE -map 0:v:0 -f null -` (exit code 0 and no output) and the decoded-stream hash (`-f hash -hash sha256 -`), values in sections 2 and 5.
3. Blender decode, `docs/video/PLAYBACK-T033.md`: `bpy.data.movieclips.load` for width, height, fps and frame count; a VSE movie strip at scene fps 60, Standard view transform, rendered to PNG to prove decode; checks at the first, every 60th and last frame and over the scene joins (mean absolute RGB difference between consecutive frames, flag if more than 3 times the neighbour median). Main and highlight passed (T-033); that script for the full films is not in the repo, only its record. The clip decoder is `film/clips/decode_clips.py`:
   `blender -b --factory-startup -P <ABS>/film/clips/decode_clips.py -- <ABS clips folder>` (prints `RESULT{json}`; 174 s the first time, 12 s the second). 2026-11-22 on the committed clips: 3.1 1920x1080, 60.0 fps, 708 frames (movieclip and strip), 11.8 s, 13 frames decoded, 0 errors, mean RGB first and last 217.7 and 212.1, minimum 206.0; 3.2 360 frames, 6.0 s, 7 frames decoded, 0 errors, mean first and last 216.9 and 240.9. The values in the earlier version of this file (720 frames, 12.0 s) were for the T-031 clip.
4. End of run (added review round 4, 2026-11-23): `git status --short redesign/showcase` must be empty except files the run is meant to write; restore anything else with `git checkout -- <path>` and record it (cause of the 2026-11-22 clip-list rewrite unexplained, `PIPELINE-FOLLOW-2026-11-22.md` finding 6). After the highlight `cp` in s6, `git diff redesign/showcase/concept-a/film/cam-clearance-highlight.json` is expected empty apart from `seconds`; a different result means the camera path changed.

## 8. Review loop used

1. Shot-list draft and preview contact sheets at 1080p, every Nth frame, 12 samples (`preview-contact-*.png`), viewed by the implementer; defects written to FILM-PROGRESS.md.
2. `--cam-check` after every camera change (T-028, T-029, T-030).
3. Independent review by the opus `eng-reviewer` before the full render (`docs/audits/2026-11-18-film-T030-review.md`): 9 Major and 8 minor findings, fixed in the T-030 fix pass (FILM-PROGRESS), including on-screen numbers read from source files, source hashes in timing files, the 120 s length cap.
4. Full render, Blender decode (T-033), then a second review of rendered frames and sign-off (pending; the clips are the last T-031 deliverable and still need that review).
5. Rule: a film is not "complete" until a reviewer has seen frames; this document does not mark any task VERIFIED COMPLETE.

## 9. Follow-through of this document (run 2026-11-22, full record in `PIPELINE-FOLLOW-2026-11-22.md`)

Followed from a clean environment (`env -i`, only PATH, SYSTEMROOT, TEMP, USERPROFILE and similar set) in a `git worktree` of the film pin `0da084ab`, one command at a time, wall time by `date +%s`.

| Step (this file) | Command (short) | Exit | Wall | Result |
|---|---|---|---|---|
| s3.1 / s6 main cam-check | `--shot-list shots-main.json --cam-check` | 0 | 1,417 s | 7,194 frames, 0 inside, equals committed JSON |
| s3.1 / s6 highlight cam-check | `... shots-highlight.json --cam-check --work` | 0 | 208 s | 1,452 frames, 0 inside, 0 blocked, equals committed JSON |
| s3.4 S3 render | `--scenes S3 ... --workers 3` | 0 | 3,585 s | 1,080 frames, 18.0 s, 1,009 distinct renders; not bit-identical to the film |
| s5 clip encode, S3-run lists | `encode` x2 | 0, 0 | 22 s, 12 s | 708 and 360 frames |
| s5 clip encode, committed lists on `a_film` | `encode` x2 | 0, 0 | 22 s, 12 s | decoded hash equals the committed clips |
| s7 clip decode | `decode_clips.py` x2 | 0, 0 | 174 s, 12 s | 0 errors |
| s7 ffprobe, null decode, decoded hash | four films | 0 | seconds | counts and durations as in item 1 of section 7 |
| s3.2, s3.3 main and highlight full render, s3.6 build film, s3.7 previews | not run | | | about 92 min, 20 min, 1 h (estimates); the one-scene run above proves the render, overlay and encode path |

Defects of the previous version found by following it, now fixed here: (1) the main and S3 commands wrote into `%TEMP%\a_film` (the live frame folder; film mode deletes `map_*.json` there) because no `--work` was given; (2) the `sed` recipe and S3 frame numbers were obsolete since T-030-N; (3) clip encode paths were inconsistent (`<ABS>/film/clips` against `<ABS>/redesign/...`); (4) a partial render silently rewrote the tracked clip list files; (5) hashes, lengths and frame counts were of the 116.0 s T-031 film, hashes were of CRLF working copies, and there was no commit pin; (6) the 75 s and 78 s cam-check times and the 12 min S3 estimate held only on an idle machine; (7) the doc said the record folders were git-ignored and no ffprobe existed (both stale).

Not shown by this follow: a from-scratch main or highlight render, the build film, the preview contact sheet, a render from HEAD (`4ebfe0a5`), or a render on another machine.

## 10. Known limits

- 2026-11-19: standalone FFmpeg 9.0.2 is installed (PD-006 superseded); `ffprobe` metadata and a full `ffmpeg -f null` decode of all four films are recorded in `docs/verification-report.md` and were repeated on 2026-11-22. Encoding still runs through the Blender VSE. No audio; scene concatenation is done inside the VSE encode (cuts via the PNG list), not with ffmpeg.
- Blender decode is sampled (first, every 60th, last, scene joins), not a full-stream decode: 117 of 6,960 main frames in the T-031 run (the count for 7,194 frames is not recorded), 26 of 1,452 highlight frames, 13 and 7 clip frames. The full decode is the ffmpeg null decode.
- The mean-absolute-difference join test cannot separate a hard cut from motion on a mostly white stage (PLAYBACK-T033 notes).
- Prop spin is illustrative (category), 47 deg per frame, on only when the logged thrust of that motor exceeds 0.05 N; the plant RPM is not logged. S4 time scale changes at shot joins (x9.6, x2.8, x2.8, x26, x3.6) are changes of speed, readout shown; the log clock is not blended across joins (m-4, open).
- Ground contact in S4 is geometric (z = 0), not deformation; the elevon sign convention (+ = trailing edge down) is taken from the `a_aero` use, not independently checked; SITL run Z5_gb0 predates D-207 geometry and uses EST aero; FEA panels use EST allowables (D-207 rule).
- The films show the 2026-11-18 configuration (115 parts, MN2212), not the aircraft at HEAD (129 parts, X2216); section 0.
- Motion blur and DOF flags (`--dof`, `--motion-blur`) were never exercised in a full render (motion blur probably has no effect because objects are posed directly per frame: unverified).
- The rendered frames live in `%TEMP%` and are lost when it is cleaned; a new film-mode run clears `map_*.json` in its work folder; a rerun is the only way to re-cut clips then. The committed film lists and clips depend on the exact frame names of the T-031 plus T-030-N main run in `a_film`.
- Re-rendering reproduces content, frame counts and timing but not the pictures bit for bit (section 5); hashes of the rendered videos also change if Blender, the CAD, the encoder settings or a source record changes. Compare frame counts, durations, decode results and overlay numbers; use the decoded-stream hash only for a re-encode of the same frames.
- The record folders in section 2 are git-tracked (since `fe02c9d5`); text files are CRLF in a Windows working copy, so the hashes stored in the timing JSON files are the CRLF ones (section 0).

## 11. Improvements against PIPELINE-AUDIT.md (section 13 list)

| # | Audit item | Status | Where |
|---|---|---|---|
| 1 | Resolution and fps flags | Done (T-027): `--width --height --fps`, defaults unchanged, overlay scale from picture width | `apply_res`, `add_res_args` |
| 2 | Short-film mode, shot lists | Done: `--shot-list`, main and highlight lists, `--scenes`, `--every`, preview contact sheets | `load_film`, `film_driver`, `film/shots-*.json` |
| 3 | Mechanism clips with a linkage solver | Done (T-028, T-031): poses from the AR-001 table, connection check per pose (max gap 0.0096 mm, limit 0.05 mm), 2 clips | `load_kin`, `mech_state`, `mech_geom`; section 5 |
| 4 | Physics from an executed simulation | Done (T-029): S4 plays `Z5_gb0` with a live readout; no new simulation (PD-007) | `load_sitl`, `sitl_pose` |
| 5 | FEA scene | Done (T-029): stress-coloured hub GLBs and the arm plate, numbers read from result files | S5 |
| 6 | Overlay from a label list | Done: tags, readouts and sub-titles from the shot list and source files (`src_val`) | `film_overlay` |
| 7 | Encoding | Kept Blender VSE encode; ffmpeg is installed since 2026-11-19 and used for checks only; the `--max-mb` cap applies to the build film (not checked for film mode) | `blender_encode` |
| 8 | DOF and motion blur | Flags exist, not exercised | `--dof`, `--motion-blur` |
| 9 | timing.json | Done: seconds, workers, samples, resolution, source SHA-256 (of the working copy, CRLF on Windows) | `write_timing` |

Not in the audit list, added: per-frame camera clearance check (section 6), playback decode check (T-033), 0.2 s scene-join dips, source hashing, prop spin from logged thrust. Measured cost against the audit estimate (about 1.1 s per frame wall for 1080p60): T-031 main 5,298 s for 6,960 frames = 0.76 s per frame wall (estimate high, dedupe and cheap frames), whole programme main + highlight about 1.8 h against the 2.5 to 4 h estimate. On 2026-11-22 under load the S3 run was 3.3 s per frame wall (3,585 s / 1,080), 4.4 times the T-031 figure.

## 12. T-030-N additions (2026-11-18, after the final review; details in FILM-PROGRESS "T-030-N")

- The main film is now 119.9 s (7,194 frames): shot 2.6 "Exploded view" (ILLUSTRATIVE) was added at the end of S2. S3 to S6 moved +234 frames: S3 is frames 2454..3533 (3.1 2454..3173, 3.2 3174..3533).
- Clip lists are no longer cut by `sed`: the shot list has a top-level `clips` field (`list`, `shot`, `from_s`, `trim_end_s`) and the film driver (`write_clip_lists`) writes `film/clips/list-*.txt` in the picture names of that run whenever it builds the frame list (also with `--skip-render --lists-only`, which draws and encodes nothing). Clip 3.1 starts 0.2 s into its shot (708 frames), clip 3.2 is unchanged (360). Encode commands as in section 5.
- Partial re-render: `--changed-from OLD_SHOTS.json` (film mode) compares the old and new shot lists per frame (same shot fields except the overlay-only ones, same scene-local time, same camera with azimuth mod 360) and renders ONLY the differing frames into the existing work folder as `n_<frame>.png` (worker options `--raw-prefix`, `--tag`), writes one consolidated `map_T030N.json` and moves the old maps to `old_maps/`; no overlay, no encode. A later `--skip-render` run overlays and encodes the whole film. Used in T-030-N: 801 of 7,194 frames, 773 s. This path needs the work folder of the earlier run (here `a_film`), so it cannot be repeated from a clean clone without first doing the full render.
- Overlay: header backing plate; lower-third layout guard against the readout panel (raises on overlap, or on a sub-title needing more than 3 lines); card values wrap; shot field `annot` draws 2-D marks projected through the shot camera (`cam_projector`, matches Blender to 0.002 px): `dim` (dimension with extension lines, arrowheads, leader, value from a params-A.json key) and `arc` (servo-arm rotation sense from AR-001).
- Exploded view: shot field `explode` {from, to, p0, p1} (shot-local seconds; progress 0 assembled to 1 exploded); offsets from the `a_assembly_plan.STEPS` directions (= `cad/out/_plan.json`, the steps of `cad/out/assembly.json`), reversed; spacing rule and exclusions in FILM-PROGRESS. Category ILLUSTRATIVE.
- `--cam-check` also reports camera speed and acceleration (section 6): `cam_motion` in `film/cam-clearance.json`.
- The highlight was not re-rendered (own work folder `a_film_hl`, own maps); only its overlay changes.
