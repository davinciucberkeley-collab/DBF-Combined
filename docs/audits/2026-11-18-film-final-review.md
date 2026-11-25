# T-030 re-review and T-033 sign-off: concept A films, final encodes

Reviewer: independent review agent (opus), 2026-11-18. Scope: `redesign/v1` at `39eb5b84` (clean tree). Files:
- `redesign/showcase/concept-a/film/film-main-1080p60.mp4`
- `redesign/showcase/concept-a/film/film-highlight-1080p60.mp4`
- `redesign/showcase/concept-a/film/clips/clip-elevon-linkage-3.1-servo-arm-rod-horn-1080p60.mp4`
- `redesign/showcase/concept-a/film/clips/clip-elevon-linkage-3.2-horn-hinge-1080p60.mp4`

Read before the review: R-VID-01..15, spec Part 7, my earlier review `2026-11-18-film-T030-review.md`, FILM-PROGRESS
"T-030 fix pass", `PLAYBACK-T033.md` and `PIPELINE.md`. Every frame below comes from the final encoded files. I did not
use the previews. I wrote only this file and the "Video verification (T-033)" section of `docs/verification-report.md`.

## Verdict: PASS WITH CONDITIONS (not ready for VERIFIED COMPLETE)

- **Playback passes.** All four files decode completely through Blender's FFmpeg with 0 decoder errors. The frame
  counts match the container and the shot lists, and no frame is blank, missing or a duplicate.
- **The T-030 fixes are on screen.** M-1, M-3, M-4, M-5, M-6, M-7, M-8 and M-9 are closed in the encoded film.
- **Three defects keep the sign-off open:**
  - **M-2 is only partly closed.** The closing card reads `commit fe02c9d5-dirty` in both films.
  - **New Major N-1:** in shots 4.1 and 4.2 the lower third covers the left end of the S4 readout. Part of the
    "Prop rotation illustrative" disclosure is hidden behind it.
  - **R-VID-08 is not met (N-2):** the film has no exploded view, no motion arrows and no dimension annotations.

N-1 and M-2 need only the overlay pass and the encode. The raw frames are still in `%TEMP%/a_film` (12,983 files), so
no Blender re-render is needed. N-2 needs new content.

## 1. Full-stream decode (R-VID-15, R-RULE-10)

### Method

1. **Independent container parse** (`mp4box.py`, scratchpad). A Python reader of the MP4 boxes, separate from Blender,
   reads `mdhd`, `stsd`, `stsz`, `stts` and `stss`.
2. **Full decode.** Command:
   `blender -b --factory-startup --debug-ffmpeg -P fulldecode.py -- <mp4> <outdir>`
   - The file loads as a VSE movie strip. The scene runs at 60 fps over 1..strip length, with the Standard view
     transform.
   - `render.render(animation=True)` decodes **every** frame. Each frame is written as an RGBA PNG at 25 % scale.
     Decoding happens at full 1920x1080; only the written image is scaled.
   - `--debug-ffmpeg` sends libavcodec's own log to the console. The log was searched for
     `error|corrupt|invalid data|concealing|missing reference|decode_slice_header|no frame` and for `warn`.
3. **Frame analysis** (`analyse.py`, system Python with PIL and numpy) checks every written frame:
   - the frame numbers run without a gap
   - each frame has the right shape
   - alpha is fully opaque, since a frame that fails to decode comes out transparent in the VSE
   - mean RGB is above 5 (not black)
   - exact duplicates of the previous frame
   - the largest frame-to-frame jumps

### Results

| File | Container (independent parse) | Blender clip / strip frames | Frames decoded and written | libav error / warn lines | Blank, transparent or bad-shape frames | Exact duplicate frames | Result |
|---|---|---|---|---|---|---|---|
| main | avc1 1920x1080; 6,960 samples; stts 6960 x 256 at timescale 15360 = 60.000 fps; 116.000 s; 60 sync frames; moov at end | 6,960 / 6,960 | 6,960 of 6,960 (frames 1..6960 contiguous; 6,960 "Saved") | 0 / 0 (83,690 log lines; 63 IDR NALs) | 0 / 0 / 0 | 0 | **PASS** |
| highlight | avc1 1920x1080; 1,452 samples; 60.000 fps; 24.200 s; 15 sync frames | 1,452 / 1,452 | 1,452 of 1,452 | 0 / 0 (17,594 lines) | 0 / 0 / 0 | 0 | **PASS** |
| clip 3.1 | avc1 1920x1080; 720 samples; 60.000 fps; 12.000 s | 720 / 720 | 720 of 720 | 0 / 0 | 0 / 0 / 0 | 0 | **PASS** |
| clip 3.2 | avc1 1920x1080; 360 samples; 60.000 fps; 6.000 s | 360 / 360 | 360 of 360 | 0 / 0 | 0 / 0 / 0 | 0 | **PASS** |

Wall time of the decode: main 71.3 s, highlight 14.4 s, clip 3.1 6.6 s, clip 3.2 4.4 s.

**Expected counts:**
- **Main:** the sum of `dur` in `shots-main.json` is 116.0 s = 6,960 frames, which matches.
- **Highlight:** the sum in `shots-highlight.json` is 24.2 s = 1,452 frames, which matches.
- **Clips:** shot 3.1 is 12.0 s and shot 3.2 is 6.0 s, so 720 and 360 frames, which match.

**R-VID-06:** all four files are 1920x1080 at 60 fps (PASS). **R-VID-11:** main 116.0 s, inside 60–120 s (PASS).
**R-VID-12:** highlight 24.2 s, inside 20–30 s (PASS).

**Largest frame-to-frame jumps in the main film** (mean absolute RGB difference at 25 % scale; median 0.96):
- f1620, diff 35.9: shot 2.3 to 2.4, a cut inside S2
- f5880, diff 17.4: shot 5.2 to 5.3
- f2940, diff 9.75: shot 3.1 to 3.2
- f1083–1091, diff about 9: the fast camera move into shot 2.2 (see m-B)

I inspected each of these on the decoded frames. All are intended cuts or camera motion; none is a decode fault.

**Limits of this check:**
- Only one decoder was used: Blender 4.5.14's bundled libavcodec. Other players were not tested. The files are standard
  H.264 High, yuv420p, so I expect no problem there.
- There is still no ffmpeg/ffprobe on the machine. The container parse stands in for ffprobe.
- `moov` sits at the end of each file (no faststart). Desktop playback is unaffected; a browser streaming the file over
  HTTP must download all of it before playing (m-E).

## 2. Visual review of the final encodes

I extracted 40 main-film frames, 9 highlight frames and 7 clip frames at full 1920x1080 from the mp4 files and viewed
them at full resolution:
- main: 60, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 2900, 3000, 3060, 3200, 3290, 3299, 3300, 3310, 3400,
  3600, 3900, 4100, 4400, 4700, 4900, 5100, 5150, 5159, 5160, 5300, 5450, 5650, 5800, 6000, 6200, 6400, 6650, 6700,
  6900, 6959
- highlight: 90, 300, 500, 700, 950, 1025, 1100, 1300, 1451
- clip 3.1: 0, 240, 420, 719
- clip 3.2: 0, 180, 359

From the full decode I also built 25 % strips of the join and fast-motion windows: 718–727, 1078–1094 and 1619–1625 in
the main film, and 600–790 in the highlight.

### Earlier findings, checked on screen

| ID | On screen in the final film | Status |
|---|---|---|
| M-1 | f600, shot 1.3: "115 modelled parts: every part is modelled, unknown vendor dimensions are marked EST (params-A.json cad3d/parts)". `params-A.json cad3d/parts` = 115 | **Closed** |
| M-2 | f6900/6959 and highlight f1300/1451: the card has a revision line, mass, packed box, interference gate, SITL landing and hub FEA. I recomputed predicted mass = 1.27324 x 1.1174 + 0.032 x 1.47 = 1.42272 + 0.04704 = 1.46976 kg, shown as "1.4698 kg vs gate 1.47 kg (0.2 g left)", correct. Interference: `cad3d/n_over_tol` 0, `max_depth_mm` 0.042, `wire_ends_open` 0, `parts` 115, correct. Landing line matches `sum.json landing` (sink 0.02, lean 0.0, tipped_over false). **But the revision line reads `D-212 rev 3, commit fe02c9d5-dirty`** | **Open (N-3 below)** |
| M-3 | f5300 (5.1): tag "PETG hub p99 judged 12.7 vs 20 MPa (D-207 rule)". Panel: 5.9 x 2.156 = 12.7, peak "x factor, not judged (D-207) 41.4 MPa", "Hub skin vertices over 1: 0.79 %", "Highest on screen: bridge tube u 0.958". f5650 (5.2): tag "...PETG hub peak 18.3 vs 20 MPa; bridge tube u 1.002", panel "u 1.002". Sub explains red = over 1 at singular points | **Closed** (see m-A on the pass/fail wording of 1.002) |
| M-4 | S4 readout, all shots: "Run Z5_gb0: 1.50 kg, wind 0 m/s (sum.json)", "Run file 2026-11-15, geometry before D-207; SITL with the a_plant.py plant (EST aero)". Tag names the plant. At the end of 4.5 (f5150, highlight f1025): "Touch-down at 247.3 s: sink 0.02 m/s, lean 0.0 deg, tipped over: no (sum.json)" | **Closed on content**, but partly hidden in 4.1/4.2 (N-1) |
| M-5 | `film/timing-T031-main.json` `sources` lists SHA-256 for all eight record files. The five checked in the T-030 review match it byte for byte (`07729f67…`, `9fecf1a1…`, `4cf658e3…`, `12e1aea3…`, `a73cb30f…`) | **Closed** |
| M-6 | f3600, f4100, f4900, f5150: blades are at different phases from frame to frame and are real blade meshes, not disks. The readout says "Prop rotation illustrative, not to rate" | **Closed**, but that line is cut off in 4.1/4.2 (N-1) |
| M-7 | 116.0 s (decode table) | **Closed** |
| M-8 | f3060 and f3200 (3.2, t = 2.0 and 4.3 s) have identical framing, so the camera holds through the sweep. The elevon is half see-through teal. The hinge axis is drawn as an orange rod, and the elevon visibly turns about it (−10.5° to +20.5°) | **Closed** |
| M-9 | f2400 (−21°) against f2700 (+21°): the elevon silhouette and tilt change strongly, and the rib horn and rod are clear of the elevon | **Closed** |
| m-1 | f720 (S1/S2) and f3299/3300 (S3/S4) dip to the stage colour; the card fades in. The cuts between shots inside a scene stay hard (f1620, f5880), which is acceptable | Closed |
| m-2, m-3 | f2400: "to the 21 deg mechanical stops (flight limit 20 deg, wing.py ELEV_LIM)". f1500 (2.3) and f2100 (2.5) carry the cut-away notes and "MEC-001 to MEC-005, MEC-008" | Closed |
| m-4 | dl/dr added to the readout (f4400 shows −13.0 / −13.0 in the back-transition, as `case.fwd.csv`). The log clock steps ×2.8 → ×26.3 → ×3.6 at the S4 joins are still not blended. PLAYBACK-T033 shows no flagged jump at 4620/4830 | Open (minor, accepted) |
| m-5, m-7 | Hub still shown without aircraft context. The 5.3 plate is unchanged apart from 7 s (f6000: the plate's smallest text is about 15 px) | Open (minor, optional) |

### Legibility, artefacts, tags, clips

- **Text at 1080p.** Titles are about 36 px, subs about 30 px, readout values about 34 px and tags about 22 px mono.
  All are legible on the encoded frames. At a 100 % zoom of the 20 px source lines (f5300) the edges are slightly soft,
  with no blocking or ringing that hurts reading.
- **Encode.** The main film averages 1.67 Mb/s (24,192,460 B over 116 s), which is low for 1080p60. On the flat light
  background I found no visible banding or macroblocking. The prop blades and the thin pitot rod stay clean (f4100 at
  2x zoom).
- **Tags.**
  - Every shot with parts moving carries a SIMULATED tag: S3 kinematics AR-001, S4 SITL Z5_gb0 with plant model and EST
    aero, S5 FEA run IDs.
  - The illustrative prop rotation is labelled in the readout. S1, S2 and S6 move only the camera and carry no tag,
    which is correct.
  - No motion is mislabelled.
- **Highlight.**
  - H1 to H7 match the shot list.
  - The tags and readouts are kept, and the short subs do not reach the readout panels.
  - H5 ends on the touch-down line.
  - H7 shows the same card, including "-dirty" (N-3).
- **Clips.**
  - Both clips are 1080p60 and tagged SIMULATED AR-001.
  - The readouts are present, and the servo arm visibly drives the rod, the horn and the elevon.
  - Clip 3.1 frame 0 is the bare stage colour, because the clip starts inside the S2/S3 dip, and clip 3.2 ends faded
    out (m-D).

## 3. Findings

| Rank | ID | Severity | Evidence | Required fix |
|---|---|---|---|---|
| 1 | N-1 | **Major** | In 4.1 (f3300–3719) and 4.2 (f3720–4319), about 17 s, the lower-third box (x ≈ 60–1168) overlaps the readout box (x ≈ 1080–1860). Its opaque fill hides the first 4–6 characters of the five small readout lines: "Log time", "Run Z5_gb0", "Run file", "a_plant.py" and "**Prop** rotation illustrative". In 4.1 the readout also covers the lower half of the aircraft (f3600). Shots 4.3–4.5 and the highlight are not affected (shorter subs). This breaks the M-4/M-6 disclosures on screen and is a spec 7.6 "incorrect labels" / clutter defect | Limit the lower-third width in S4, or wrap the sub to end before the readout's x, or add a layout guard in `film_overlay` (lower-third right edge ≤ readout left edge − 24 px). Re-run the overlay and encode for the main film (about 141 s + 287 s, raw frames kept) and re-check f3600 and f4100 |
| 2 | N-3 (M-2 rest) | **Major** | The closing card in main f6600–6959 and highlight H7 reads `commit fe02c9d5-dirty`. `render_build_a.py:577-582` adds "-dirty" when `git status --porcelain --untracked-files=no` is non-empty, so tracked files were modified when the overlay was drawn. The revision cannot be reproduced from a commit, against the M-2 fix and FILM-PROGRESS's own statement ("it will read the commit hash once T-031 renders from a clean tree") | Commit, confirm `git status --porcelain --untracked-files=no` is empty, and re-run the overlay and encode for main and highlight (and clips if they are re-cut). The card must show a hash with no "-dirty" that resolves with `git cat-file -t`. Combine with the N-1 rerun |
| 3 | N-2 | **Major (requirement gap)** | R-VID-08 acceptance asks for "labels, arrows, **one exploded and one transparent view**". The transparent view is present (2.4 x-ray, 2.5/3.x ghost wing). There is **no exploded view**: no shot field and no code path in `shots-main.json` / `render_build_a.py` (grep "explod" = 0). There are no motion arrows, and no dimension annotations other than numbers in text. The component labels are lower-third captions only (no leader labels on parts). Spec 7.4 lists all of these | Add a short exploded view (for example 3–4 s in S2.3 or S6.1, parts moving out along the assembly axes from `assembly.json`, tagged ILLUSTRATIVE). Add one motion arrow in S3.1 (servo-arm rotation sense) and one dimension call-out (for example the 0.90 m span in 1.2). Keep the film at or under 120 s (now 116 s). Then partial render, overlay and encode. If the team instead drops this item, it needs a recorded decision against R-VID-08; the reviewer cannot waive it |
| 4 | m-A | Minor | The card's "Hub FEA (run d209)" line and the 5.2 tag show "bridge tube u 1.002 (S2)" with no pass/fail word. The other card lines read PASS or a measured value. A newcomer cannot tell that 1.002 means just over the allowable in the damage case. R-VID-08 asks for verified pass/fail results | Show it as "bridge tube u 1.002 in S2: over 1 by 0.2 % at the bond end (open, structures)", or the status recorded in CHANGE-LOG |
| 5 | m-B | Minor | Transition into 2.2 (f1080–1095): the camera swings from the 2.1 end pose to the first 2.2 key (t = 2.0) fast enough that consecutive frames differ by about 9 (median 0.96). It reads as a whip-pan. R-VID-04 asks for a per-frame camera acceleration bound, and no such check is recorded for the film (`cam-clearance.json` is clearance only) | Add the per-frame camera speed and acceleration check to `--cam-check` and report the peak. Ease the 2.1 → 2.2 move (key at t = 0 near the 2.1 end pose, or lengthen it) |
| 6 | m-C | Minor | Header "Concept A quad tailsitter / SCENE Sx / SHOT x.y" has no backing. Over geometry it loses contrast: f1500 over the black arm, f3000 over the orange horn, where "SHOT 3.2" is unreadable | Add a 60–70 % stage-colour backing plate or a soft text shadow |
| 7 | m-D | Minor | Clip 3.1 frame 0 is the stage colour, from the S2/S3 dip. Clip 3.2 fades out. Standalone clips open on a blank frame | Cut clip 3.1 from 0.2 s in, or keep and say so in PIPELINE.md |
| 8 | m-E | Minor | `moov` box at the end of all four files | If they are served on the web pages, remux with faststart (any later ffmpeg `-movflags +faststart`) |
| 9 | m-4, m-5, m-7 | Minor | Carried from T-030 (above) | As in the T-030 review; optional |
| — | R-VID-11 naming | Note | The ledger deliverable names `a-demo.mp4` / `a-highlight.mp4`; the files are `film-main-1080p60.mp4` / `film-highlight-1080p60.mp4` | Accept the actual names in the ledger, or add copies. No visual impact |

## 4. Requirement status (reviewer's view; the conductor sets ledger status)

| Req | Status | Basis |
|---|---|---|
| R-VID-01 | Met | T-026 verified earlier, not re-checked here |
| R-VID-02 | Met | Frames show the live CAD (115 parts, D-212 rev 3 horn and keeper) |
| R-VID-03 | Met | Consistent lighting, shadows and materials; no artefacts found |
| R-VID-04 | **Not evidenced** | Camera moves are eased and there are no cuts mid-move, but no per-frame acceleration check exists (m-B) |
| R-VID-05 | Met | S3 driven by AR-001; servo, rod and horn visibly connected (f2400, f2700, f3060, f3200); 0.015 mm max gap from the T-030 rerun; penetration evidence is AR-003 |
| R-VID-06 | Met | 1920x1080 at 60.000 fps, all four files |
| R-VID-07 | Met | Six scenes with the required content |
| R-VID-08 | **Not met** | N-2 (no exploded view, arrows or dimensions); N-1 and N-3 also affect labels and revision |
| R-VID-09 | Met | Every motion shot tagged; props labelled illustrative (once N-1 is fixed, fully readable) |
| R-VID-10 | Met as a process | Two review rounds logged; this round's defects are open |
| R-VID-11 | Met | 116.0 s, plays, full decode 0 errors |
| R-VID-12 | Met | 24.2 s, plays, full decode 0 errors |
| R-VID-13 | Met | 2 elevon-linkage clips, full decode 0 errors (m-D cosmetic) |
| R-VID-14 | Not checked here | "Follow doc once" was not executed by this review |
| R-VID-15 | **Decode part met; review part not passed** | 0 decode errors in 9,492 frames; visual review leaves N-1, N-3 and N-2 open |

## 5. What must change before T-033 can be VERIFIED COMPLETE (ranked)

1. **N-1:** fix the S4 lower-third and readout overlap.
2. **N-3:** clean tree, then overlay and encode again so the card shows a real hash with no "-dirty". Do 1 and 2 in one
   overlay pass, about 10 min for both films, with no Blender re-render.
3. **N-2:** add the exploded view, one motion arrow and one dimension call-out, or record a team decision that
   descopes them against R-VID-08.
4. **Re-run** the full decode (`fulldecode.py` + `analyse.py`, below; about 2 min in total) on the new encodes, and
   view f3600, f4100, f6900 and highlight f1451.
5. **Optional:** m-A to m-E.

## Reproduction

The scripts are in the session scratchpad: `C:\Users\dillo\AppData\Local\Temp\claude\1dc032cbc6faa005\7cb35b0a-c71b-43ed-9be1-fbe0a7ff151f\scratchpad\t033\`.
The scratchpad is not durable; the core of each script follows so it can be rebuilt.

- `fulldecode.py` (Blender): `new_movie(f)`, then the scene setup, then `render(animation=True)`.
  - Scene: 60 fps; 1920x1080 at 25 %; Standard view transform; `film_transparent`; PNG RGBA.
  - Output: frame range 1..`strip.frame_final_duration`. Stdout gets `META` with `clip.size`, `clip.fps`,
    `clip.frame_duration` and the strip frames.
  - Run with `--debug-ffmpeg`, and grep the log for error words.
- `analyse.py` (system Python, `-I`): for every PNG, check:
  - the frame index is contiguous
  - shape = (270, 480, 4)
  - alpha min = 255
  - mean > 5
  - exact duplicates of the previous frame
  - the top 12 mean-abs jumps
- `mp4box.py`: walks `moov/trak/mdia/{mdhd,hdlr,minf/stbl/{stsd,stsz,stts,stss}}` and prints codec, w, h, sample count,
  timescale, duration and fps.
- `grab.py` (Blender): writes a single full-resolution PNG per frame of the list (VSE, `frame_set(k+1)`, render still).


---

# Re-check after the T-030-N fixes (2026-11-18, same reviewer)

Scope: HEAD `0da084ab`, a clean tree. The films are rendered from `ebb89693`, which `git cat-file -t` confirms is a
commit; `0da084ab` adds only the mp4 and timing files.

I checked the new encodes only:
- `film-main-1080p60.mp4`: 25,897,191 B
- `film-highlight-1080p60.mp4`: 5,522,274 B
- `clip-elevon-linkage-3.1-...mp4`: 2,625,336 B
- `clip-elevon-linkage-3.2-...mp4`: 1,457,447 B

The scripts and method are the same as section 1 (`mp4box.py`, then `fulldecode.py` with `--debug-ffmpeg`, then
`analyse.py`). Before the run I deleted the old scratch decode folders.

## Verdict: PASS (T-033 / R-VID-15)

- **Playback:** all four files decode in full with 0 errors.
- **Fixes:** N-1, N-2, N-3 and m-A to m-D are all closed on the final encodes.
- **Regressions:** none of Major rank.
- **New Minors:** four (m-F to m-I below). They are cosmetic, and they are recommendations, not conditions.

## R1. Full-stream decode, re-run

| File | Container (independent parse) | Expected | Blender clip / strip | Decoded and written | libav error / warn lines | Blank, transparent or bad-shape | Exact duplicates | Result |
|---|---|---|---|---|---|---|---|---|
| main | avc1 1920x1080, 7,194 samples, stts 7194 x 256 at 15360 = 60.000 fps, 119.900 s, 62 sync | 7,194 (shots-main.json: 21 shots, sum 119.9 s) | 7,194 / 7,194 | 7,194 of 7,194, contiguous | 0 / 0 (86,498 lines) | 0 / 0 / 0 | 0 | **PASS** |
| highlight | 1,452 samples, 60.000 fps, 24.200 s | 1,452 | 1,452 / 1,452 | 1,452 of 1,452 | 0 / 0 | 0 / 0 / 0 | 0 | **PASS** |
| clip 3.1 | 708 samples, 60.000 fps, 11.800 s | 708 (shot 3.1 from 0.2 s, `clips[0].from_s`) | 708 / 708 | 708 of 708 | 0 / 0 | 0 / 0 / 0 | 0 | **PASS** |
| clip 3.2 | 360 samples, 60.000 fps, 6.000 s | 360 | 360 / 360 | 360 of 360 | 0 / 0 | 0 / 0 / 0 | 0 | **PASS** |

The total is 9,714 frames with 0 decode errors.

- **R-VID-11:** 119.9 s is inside 60–120 s, with 0.1 s to spare. Any future addition must take time out elsewhere.
- **R-VID-06 and R-VID-12:** unchanged, PASS.
- **Largest jumps in the main film** (median 0.97). Every one was inspected and is intended:
  - f1620: cut from 2.3 to 2.4
  - f6114: cut from 5.2 to 5.3
  - f2220: cut from 2.5 to 2.6 (see m-H)
  - f3174: cut from 3.1 to 3.2
- **Shot 2.2:** the whip-pan is gone. The highest diff in the 1060–1080 window is now 6.8 (it was 9.3).

## R2. Fixes, checked on the final encodes (full-resolution frames)

| ID | Frames | Finding | Status |
|---|---|---|---|
| N-1 | main 3700, 3800 (4.1), 4100, 4300 (4.2) | The lower third ends at about x 1027 / 956, and the readout starts at x 1080. All five small lines are fully visible, including "Prop rotation illustrative, not to rate". The readout still covers the lower part of the aircraft in 4.1 (stated in FILM-PROGRESS, accepted) | **Closed** |
| N-2 exploded | main 2220, 2300, 2400, 2440 (2.6, 3.9 s) | Tag "ILLUSTRATIVE: exploded view, offsets for clarity (not to scale of travel)". The camera pulls back from the servo, then the parts move out along their assembly axes. The sub names the source (`cad/out/assembly.json`) and the hidden items | **Closed** (m-G) |
| N-2 dimension | main 300, 360, 420 (1.2) | "Wing span 0.90 m", with arrowheads, extension lines and the source "params-A.json box/packed_m/0 (CAD y -0.45 to +0.45 m)". It is clean at 0.5–2 s and harder to read late in the window (m-F) | **Closed** (m-F) |
| N-2 arrow | main 2530–2570, 2550, 2700, 2880–2920, 3100 (3.1); highlight 250, 330 (H2) | An arc arrow, with a label giving the sense and the effect. The sign agrees with the sweep at every sample: f2550 servo -5.8 deg going down, label "-, TE UP"; f2700 -22.5 deg turning, label "+" fading in; f2900 +21.9 deg, label "+, TE DOWN"; f3100 +1.0 deg going back, label "-". The H2 frames read -16.5 / +8.0 deg with the "+" label during the up-sweep | **Closed** (m-I) |
| N-3 | main 7100, 7193; highlight 1451 | The card reads "D-212 rev 3, commit ebb89693", with no "-dirty". `ebb89693` is a commit and is HEAD~1 of the encode commit | **Closed** |
| m-A | main 5900 (5.2); card | Tag: "bridge tube u 1.002, over 1 (OPEN)". Panel: "Highest: bridge tube bond end (OPEN) u 1.002, over 1". Card: "F2: ... bridge tube u 0.958 PASS. S2: bridge tube bond end u 1.002, over 1 by 0.2 %, OPEN (D-207)". The card's source line adds CHANGE-LOG D-207 | **Closed** |
| m-B | main 1000, 1060, 1100; `cam-clearance.json cam_motion` | The 2.1→2.2 move is now smooth. Per-frame camera speed and acceleration are now recorded, with peaks of 96.7 deg/s and 251.5 deg/s^2 (3.2), and zoom 1.18 1/s and 1.96 1/s^2 (2.6). R-VID-04 has no numeric limit; the reviewer judges these values acceptable on screen | **Closed** |
| m-C | every sampled frame | The header now has a stage-colour backing plate. It is readable over the arm (2.2/2.3) and over the horn (3.2) | **Closed** |
| m-D | clip 3.1 f0 | The clip opens with the scene visible and the lower third fading in, not on a blank frame. Clip 3.2 still ends on the S3/S4 dip, which is acceptable | **Closed** |

**No regressions.** These are unchanged or still correct:
- S1/S2 captions, the M-1 part count, and S3 readouts and stops
- the S4 tag and context lines, and the touch-down line
- the S5.1 panel and the S5.3 plate
- the card's mass, interference and landing values: the same numbers as the first round, verified against
  `params-A.json` and `sum.json`
- the highlight H1–H7 content and tags

## R3. New minor observations (optional, not conditions)

| ID | Severity | Evidence | Suggested fix |
|---|---|---|---|
| m-F | Minor | 1.2: as the camera orbits (f420, t = 3.0 s), the dimension's extension lines run almost parallel to the dimension line. The right arrowhead and its extension go under the lower third, so the span reads less clearly than at t <= 2 s (f300, f360) | End the dimension window at about 2.4 s, or put the dimension offset in the view plane |
| m-G | Minor | 2.6: the parts move out at 2.1–3.7 s and the shot ends at 3.9 s inside the 0.2 s dip, so the fully exploded state is never held | Hold the exploded state for at least 1 s. The film is at 119.9 s, so take the time from 2.6's pull-back or from another S2 shot |
| m-H | Minor | Cut from 2.5 to 2.6 (f2219→2220, diff 14.4): the camera pose is the same, but the wing switches from ghosted to opaque in one frame, which reads as a pop | Crossfade the material over about 0.3 s, or start 2.6 with the 2.5 ghost and fade it to opaque |
| m-I | Minor | 3.1 "-" sense (f2530–2570, f3100): the arc sits about 60 px left of the servo body and does not touch the arm. The "+" arc (f2900) sits over the arm | Anchor both senses at the same radius around the spindle |

## R4. Requirement status after the re-check (reviewer's view; the conductor sets the ledger)

- **R-VID-04:** camera motion is now evidenced (`cam_motion`). There is no numeric limit, and on-screen motion is
  acceptable.
- **R-VID-08:** now met. There are:
  - an exploded view (2.6) and transparent views (2.4, 2.5, 3.x)
  - a motion arrow (3.1, H2) and a dimension (1.2)
  - captions as labels
  - a revision tag (a clean hash) and pass/fail and OPEN lines on the card and in S5
- **R-VID-11, -12, -13, -06:** met (R1).
- **R-VID-15:** met. The full decode shows 0 errors in 9,714 frames, and the visual review passes.
- **R-VID-14:** still not checked by this review ("follow doc once").
