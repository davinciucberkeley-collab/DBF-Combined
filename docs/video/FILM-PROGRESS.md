# Film progress, T-027 (parents R-VID-02, R-VID-04; feeds R-VID-03/06/07)

Date 2026-11-18. Implements PIPELINE-AUDIT.md improvements 1, 2, 8 (flags only) and 9 in `redesign/showcase/concept-a/render_build_a.py`. Nothing committed. `blender_backend.py` not touched. Full render NOT run; only a preview.

## What changed (render_build_a.py, line numbers as of this edit)

| Item | Function / place | Lines |
|---|---|---|
| 1. Resolution and rate | `apply_res`, `add_res_args` (CLI `--width --height --fps`, defaults 1280, 720, 24); `RES_FLAGS` passes them to every Blender worker and the encode; `blender_encode` gets `--fps`; overlay scale is now `k = picture width / BASE_W (1280)` instead of `/ W`; `_init` gives spawned overlay processes the run's fps | 141-151, 1121 (encode), 1321 (`_init`), 1594 (`RES_FLAGS`) |
| 2. Short-film mode | pure: `param_value`, `load_film`, `hermite_cam`, `film_at` (319-405); worker branch `if a.shot_list:` inside `blender_render` with `shot_modes`, `film_pose` (741-818); Pillow `_init_film`, `film_overlay`, `_film_job` (1502-1590); driver `film_driver`, `contact_sheet` (1604-1700), `driver()` branches on `--shot-list` (1733) | as listed |
| 8. Polish flags | `--dof` (camera DOF, focus on the target each frame via `set_focus`, f/5.6) and `--motion-blur` (`render.use_motion_blur`), worker and driver options, off by default | 697, 780, 1039 |
| 9. timing.json | `write_timing`; short film writes `film/timing.json`; the build film writes `animation/timing.json` after a full run (or `--timing PATH` for test frames) | 1598 |
| Shot list | `redesign/showcase/concept-a/film/shots-main.json` (scenes S1-S6 drafted; S3 kinematics T-028, S4 SITL playback and S5 FEA T-029) | new file |

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

---

# T-028 update (2026-11-18): scene 3 from the solved kinematics, camera clearance check, framing fixes

Nothing committed. Defaults of `render_build_a.py` unchanged (build film untouched; film mode only). No full render; preview stills only (T-031 does the 1080p60 exports).

## What changed

| Item | Where |
|---|---|
| Mechanism posing from AR-001 (category: kinematics). `load_kin`, `mech_state`, `mech_geom` read `qp/A/mechanism/out/linkage_kinematics.csv` (elevon -> servo angle, 0.05 deg steps) and `.json` (CAD constants). A shot's `mech.sweep` lists commanded elevon end points; each is converted to a servo angle through the table, the SERVO angle is eased (smoothstep) between them, and the elevon angle is read back from the table at that servo angle (linear interpolation). No hand keyframes. | `render_build_a.py` before "Blender worker" |
| Worker `mech_mats`: elevon group (WNG-006/007/010, MEC-004/005) rotates about the hinge (+y, through XH, HINGE_Z); servo arm group (MEC-002, MEC-008 keeper, HWC-002 screw) about the spline axis (+z); pushrod MEC-003 is rigid: its arm end goes to the arm tip, its horn end to the horn hole (minimal rotation from +x to the rod direction). Group membership copied from `collide.moving_groups` (printed by a probe: E-WNG-10/11 groups). Right side from the table, left side theta = -theta_R (AR-001 check K2), same elevon angle on both sides. | worker, `film_pose` |
| Connection check per rendered pose (R-VID-05 item 3): arm-tip end of the rod vs the arm-group tip, horn end vs the elevon-group horn hole, rod length error | `MECHCHECK` line in the worker log |
| Overlay: tag "SIMULATED: kinematics AR-001 (D-212 rev 3)" (shot `tag`), readout box (servo arm deg, elevon deg from `mech_state`, "+ = trailing edge down", source AR-001 table) | `film_overlay` |
| `--cam-check` (driver and worker): no render; for EVERY frame of every shot, in part-local BVHs: camera inside any visible part (closed-mesh ray parity on two axes), nearest-surface distance, first non-x-ray hit on the line camera -> subject (flag if more than 0.08 m before the subject). Shot keys `los: false` (target is only a framing offset) or `los: [x,y,z]`. Writes `film/cam-clearance.json` (per shot, plus rest-pose part boxes). Self-test of the inside test on solid parts is stored in the JSON (centre inside True, 0.2 m above False). | worker, `film_driver` |
| Shot list (`film/shots-main.json`, now indent 1): S3 = shots 3.1 (12 s) and 3.2 (6 s) replace the TODO; S1 elevation raised to 36-38 deg and target z 0.04; S2.1 props and arms hidden, aft quartering views; S2.2 farther and higher; S2.3 uncluttered (props, pack, avionics, wires hidden); S2.4 only WNG parts, spar teal and plugs orange; S2.5 only wing and mechanism parts, wires off, closer; S6 `los:false`. | shots-main.json |

## Results

Camera check (`film/cam-clearance.json`, run 1 s of Blender time plus about 74 s start-up, 4,620 frames, all six scenes): 0 frames with the camera inside any part; nearest approach 0.068 m (3.2, ghost wing core), all other close shots 0.14 m or more; line of sight blocked in 10 of 4,620 frames (shot 2.2, the target motor's own prop blade, 0.70 m camera, accepted). Before the fixes: S1.1 had 58 blocked frames (fin FIN-004-L 26, prop 14, arm 9), S1.3 26, S2.2 14, S2.4 84. The camera was never inside a part: the S1.1 "passes through the arms" at frames 160-240 was the left fin and prop discs crossing the line of sight at 18-26 deg elevation at azimuth about 70-110; now elevation 36-38.

Mechanism (preview poses, 27 rendered in S3): max connection gap 9.6e-6 m (0.0096 mm, float32 matrices; limit 0.05 mm, R-VID-05), max rod length error 3.6e-8 m. Penetration along the path (R-VID-05 item 4): NOT re-checked on meshes here; the analytic swept check AR-003 (`linkage_sweep_collision.json`, 228 pairs, 85 poses per side, worst penetration 0.0 mm, min clearance 0.066 mm, tolerance 0.05 mm, convex hulls, not mesh based) is the evidence. Servo arm at +-21 deg elevon reads -22.6 / +22.8 deg in the overlay (AR-001 K3 table).

Preview contact sheets (1080p, 12 samples, ray tracing on): `film/preview-contact-T028.png` (all six scenes, every 40th frame, 116 frames; S2.4 in this sheet is the version before its last fix) and `film/preview-contact-T028-S2-rev.png` (scene 2 after the S2.4 fix, every 25th frame, 60 frames). Wall times: full preview 145.2 s (frame loop 42-46 s per worker, 1.21 s per rendered frame, 3 workers); scene 2 re-run 119.4 s (1.14 s per frame); camera check 74 s. `film/timing.json` holds the 145.2 s run (scenes S1-S6).

## Remaining defects (for T-030)

1. S2.1 wing shot crops the hub and pack at the left edge in the first second; the wing is wide and flat so the target could sit further outboard. 2. S2.2 own prop blade crosses the motor for 10 frames. 3. Shot 3.1 elevon (teal) is correct but the rib horn is long and mostly hidden under the elevon; rotation of the elevon reads better in 3.2 (side view, elevon x-ray). 4. 3.2 hides the balance strip, lens caps and damper for a clear profile (cut-away, tagged by the sub text only). 5. Scenes S4, S5 are still placeholders (ILLUSTRATIVE cards). 6. Material pop at shot joins where `modes` change (no cross-fade); card start abrupt in 6.2. 7. Props are hidden in S2.1, S2.3, so they pop in at the scene-2 internal joins. 8. Contact sheets are 12-sample previews; edge quality not judged. 9. The camera check is a geometric test (mesh, not lens): it does not detect parts clipped by the lens near plane (0.02 m) other than through the 0.068 m minimum. 10. Elevon motion is symmetric (both sides same angle); no differential case shown.

## Reproduce

```
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --cam-check --width 1920 --height 1080 --fps 60
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --width 1920 --height 1080 --fps 60 --every 40 --samples 12 --workers 3 --preview --contact redesign/showcase/concept-a/film/preview-contact-T028.png
```

# T-029 update (2026-11-18): scene 4 playback of an executed SITL run, scene 5 FEA results, overlays from records

Nothing committed. Defaults of `render_build_a.py` unchanged (build film path untouched; all new code is film mode: `--shot-list`). No new simulation and no new FEA run (PD-007). No full render; 1080p preview only (T-031 does the exports). Analysis categories: S4 = flight dynamics (ArduPilot SITL plus the project's rigid-body plant model, run already executed; the elevons are posed from AR-001 kinematics with the logged angles), S5 = FEA (existing runs d209 hub, current_d210 arm and cup). The aircraft motion in S4 is a replay of logged states, not a new computation.

## Scene 4: what plays and from which record

Run `redesign/qp/A/sitl/runs/Z5_gb0/` (`case.fwd.csv`, 5,111 rows at 0.05 s; `result.json`, `sum.json`): QP-4 FIXES re-run as drawn, 1.50 kg, no wind, full chain (take-off, climb to about 50 m, transition, 15 s cruise, back-transition, hover descent, landing). Pass evidence (not in `result.json`, which has no verdict field): `sum.json` shows no touch in flight, elevon saturation 0 s, elevon peak 9.4 deg, motor u max 0.78, peak altitude 86.6 m (fence 110 m), V at handover 13.7 m/s, landing sink 0.02 m/s, lean 0.0 deg at touch, tipped_over false; `redesign/review/QP-4/FIXES.md` 5.1 and 5.2 rate the 1.50 kg calm cases "pass". Marks from `result.json`: armed 33.0 s, climb done 65.1, QSTAB 100.2, FBWA 101.2, forward done 107.6, cruise end and back-transition 125.7, QLAND 153.8, touch 247.3 s.

Column meanings (read from `sitl/a_plant.py`: header line 304, `euler_rpy` line 234, `step` ground contact; not guessed): `t` s; `pn`, `pe` m north and east of the take-off point; `alt` m of the CG above ground (up positive, 0.314 m at rest on the fin pads); `pitch` deg with +90 = nose up (hover) and 0 = level (`asin(-x_b,z)`); `roll`, `hdg_nose` deg = ZYX Euler of the body FRD frame (x nose, y right wing, z belly); `V` m/s airspeed; `dl`, `dr` deg left and right elevon, trailing edge down +.

Pose chain (`render_build_a.py`, `load_sitl`, `sitl_pose`, worker): rotation R_ned = Rz(hdg_nose) Ry(pitch) Rx(roll), quaternion per row, slerp between rows; NED to film world (x north, y west, z up) by diag(1,-1,-1); body to CAD frame by diag(-1,1,-1) (CAD: x aft, y right, z up; body: x nose, y right, z belly) with the CG at `cad_mass.json` (cg 21.4, -2.0, 6.4 mm); world position = (pn, -pe, alt). Elevons: logged dr, dl through the AR-001 table (`mech_state_log`), per side, same connection check as scene 3. Checks done offline: reconstructed belly heading vs logged `hdg_belly`: max 0.92 deg (only within 0.1 deg of vertical, where the logged angles are rounded to 0.01 deg and ill-conditioned); reconstructed pitch vs logged: 2e-11 deg; largest rotation between adjacent rows 3.6 deg (no flips; the logged roll flips sign at the vertical, the matrix does not). CAD foot pads (x 337.5 mm aft of the LE) reach 0.316 m below the CG against the plant `alt` 0.314 m at rest (2 mm contact compression), so the model stands on the ground plane z = 0 at t = 0.

Shots (time scale = log window / shot duration, shown in the readout): 4.1 take-off and climb, log 31-98 s in 7 s (x9.6); 4.2 transition and cruise, 98-126 s in 12 s (x2.3); 4.3 back-transition, 126-140 s in 5 s (x2.8); 4.4 hover descent, 140-232 s in 3.5 s (x26.3); 4.5 landing, 232-252 s in 5.5 s (x3.6). Total 33 s. Tag `SIMULATED: ArduPilot SITL run Z5_gb0`. Live readout (bottom right, from the same rows, linear interpolation): pitch, altitude, airspeed, log time, time scale, run path. Camera: keys are offsets from the aircraft position (shot key `follow`), the target is the log position averaged over +-0.4 s and held within 0.5 m of the true position (a 1.5 s average first tried lagged 1-2 m in the transition and left the aircraft off frame); side or quartering views, elevation 15-32 deg. Ground: the stage floor at z = 0 with its grid rescaled to 5 m cells (floor scale 1000 x 300 at (200, 0)), far clip 900 m in S4 shots only; orange trail of the flown CG path with a 12 s tail. Props are static meshes (no blur), so the hover shows the motors as stopped; stated, not hidden.

## Scene 5: FEA results shown

| Shot | Content | Tag (numbers read from the result file at draw time) |
|---|---|---|
| 5.1 (6 s) | `out_fea/hub_F2.glb` stress-coloured skins (utilisation ramp of `fea_hub_figs.py`, red over 1, grey not judged), unlit colour, orbit | SIMULATED: FEA hub F2 motor runaway (run d209), max judged 12.7 MPa vs allowable 20 MPa |
| 5.2 (6 s) | `out_fea/hub_S2.glb`, same | SIMULATED: FEA hub S2 prop strike 30 N (run d209), max 18.3 MPa vs allowable 20 MPa |
| 5.3 (6 s) | image plate `structures/fig/fea-arm-along.png` (run current_d210) | SIMULATED: FEA arm and motor cup (run current_d210), cup S2 max 18.0 MPa vs allowable 20 MPa |

Numbers and their sources (`src_val` in `render_build_a.py`; allowables parsed from `structures/fea_arm.py`: ALLOW petg 20, cf_axial 350 MPa, KP 2.156, KF 1.725, all EST): hub F2 judged = max over zones of the envelope 99th percentile (5.87 MPa, `hub_result_L0_d209.json`, "F2 uncapped fault, any pattern" / `hub_zones_envelope`) x KP = 12.7 MPa; the single-point peak is 19.2 MPa (raw, at the bridge boss) and is shown as "not judged": the hub is judged on the 99th percentile (D-207), so 19.2 MPa x 2.156 would exceed 20 and is not the pass value. S2 at factor 1.0: peak 18.3 MPa (single point) and p99 7.7 MPa (worst-combo zone), both under 20. Arm: cup S2 p1 18.0 MPa, cup F2 4.35 x 2.156 = 9.4 MPa, tube root axial F2 29.9 x 1.725 = 51 MPa and S2 79.9 MPa against 350 (`result_L0_current_d210.json`, cases picked by name). These match the D-209/D-210 CHANGE-LOG numbers. Meshes are shifted left of the panels by camera `shift_x` 0.17; GLB units m, hub frame x aft, y right, z up, recentred on the bbox (centre 24.5, 0, 0 mm).

## Verification

- Camera clearance (`--cam-check`, all six scenes, 1080p60, 7,320 frames, 75 s): 0 frames with the camera inside any part; S1, S2, S3 results identical to T-028 (S2.2 10 frames blocked by its own prop blade; nearest 0.068 m in 3.2); S4 and S5: 0 inside, no part within 0.3 m of the camera (S4 camera 2.6-4.2 m from the aircraft; S5 shots show no CAD part), line of sight off (`los: false`; a follow shot has no fixed subject point). Mechanism connection check over 3,060 posed frames (S3 plus S4): max gap 1.49e-5 m (limit 5e-5), rod length error 3.6e-8 m. Log `film/evidence-T029/cam-check.log`, data `film/cam-clearance.json`.
- Preview: 1080p60, every 60th frame (1 s), 12 samples, 3 workers, scenes S4 and S5, 51 frames: `film/preview-contact-T029-S4S5.png` (viewed: aircraft in frame in all S4 samples, readouts legible, plate and hub panels do not overlap). Wall 104.5 s (`film/timing-T029.json`, 0.51 s per rendered frame). Log `film/evidence-T029/preview-run.log`.
- Not verified: motion smoothness frame to frame (previews sample 1 per second); the rate jumps at S4 shot joins (x9.6, x2.3, x2.8, x26, x3.6) are changes of speed with a continuous camera; ground contact of the pads is geometric (z = 0), not rendered deformation; the elevon sign convention (dl, dr trailing edge down +) is taken from the `a_aero` use (trim elevon "TE up if negative"), not checked against a render; no film export.

## Remaining defects (for T-030)

1. The hover descent (4.4) runs at x26 and the landing at x3.6; the touch-down itself is brief. 2. Ground cues at altitude are the trail and the faint grid only; in cruise the background is the stage gradient. 3. Static props. 4. Hub stress shots are unlit flat colour with a silhouette darkening, no cavity shading. 5. The S4 and S5 lower-third titles and the readouts share the bottom band, so S5 titles wrap to three lines. 6. Total film now 122 s (S4 33 s, S5 18 s), above the 60-120 s target; T-030 should trim. 7. S4/S5 camera and shot values in `film/shots-main.json` are first-pass.

## Reproduce

```
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --cam-check --width 1920 --height 1080 --fps 60
python redesign/showcase/concept-a/render_build_a.py --shot-list redesign/showcase/concept-a/film/shots-main.json --scenes S4,S5 --width 1920 --height 1080 --fps 60 --every 60 --samples 12 --workers 3 --preview --timing redesign/showcase/concept-a/film/timing-T029.json --contact redesign/showcase/concept-a/film/preview-contact-T029-S4S5.png
```

---

# T-030 fix pass (2026-11-18): closes review M-1..M-9 and the cheap minors

Nothing committed. Edited only `film/shots-main.json`, the film-mode code of `render_build_a.py` (defaults and the build-film path untouched) and this file; new `film/shots-highlight.json`. Review: `docs/audits/2026-11-18-film-T030-review.md`. Film is now 116.0 s (6,960 frames at 60 fps), under the 120 s limit of R-VID-11.

## Findings closed

| ID | Fix | Where |
|---|---|---|
| M-1 | 1.3 sub reads the part count at draw time (`params-A.json cad3d/parts`, now 115) and says "every part is modelled, unknown vendor dimensions are marked EST" (no "no stand-in geometry") | `shots-main.json` 1.3 (`vals.n` = `{param}`), `src_val` kind `param` |
| M-2 | Closing card rebuilt: revision line (D-212 rev 3, commit from `git rev-parse` at draw time, "-dirty" if the tree is uncommitted: it will read the commit hash once T-031 renders from a clean tree); predicted mass 1.4698 kg computed on screen from `basic x growth + overrun x gate` (params keys, formula cited, D-208) against the 1.47 kg gate with the 0.2 g left; packed box; interference gate PASS line (`cad3d/*`); SITL landing line (`sum.json`); hub FEA line. Every line cites its record; card fades in over 0.4 s. | `film_overlay` card block, `src_val` kinds `calc`, `sum`, `git`, `npz` |
| M-3 | 5.1 / 5.2 tags say "PETG hub p99 judged ... (D-207 rule)" / "PETG hub peak ... ; bridge tube u 1.002". Panels add "Highest on screen: bridge tube" (max of `U_F2_3` 0.958, `U_S2_3` 1.002 from `hub_fields_L0_d209.npz`, read at draw time), "Hub skin vertices over 1" (0.79 % F2, 0.00 % S2) and the single-point peak factored (19.2 x 2.156 = 41.4 MPa, not judged, D-207). Sub says red = over 1 at singular points. | `shots-main.json` 5.1, 5.2 |
| M-4 | S4 readout adds the run context (live from `sum.json`: 1.50 kg, wind 0), the note "run file 2026-11-15, geometry before D-207; SITL with the a_plant.py plant (EST aero)", the left / right elevon angles from the log, and at 4.5 the touch-down line (sink 0.02 m/s, lean 0.0 deg, tipped over: no). Tag names the plant model. | `film_overlay` sitl block, `shots-main.json` S4 |
| M-5 | `timing.json` now carries SHA-256 and size of every record file read from git-ignored folders (`source_hashes`). Table below; force-add list in the T-030 return message. | `film_driver` |
| M-6 | Props turn in S4 (rigid-body-free, category: illustrative). Real blade, adapter and spinner meshes (PRP-002/004/005) rotate about each motor axis (`amodel.common.motor_R`, `station`), 47 deg per frame at 60 fps (2,820 deg/s, not a divisor of the 180 deg blade symmetry), direction by MR / MRP, on only while the LOGGED thrust `th1..th4` of that motor is above 0.05 N. The plant's RPM is not logged, so the rate is **ILLUSTRATIVE** and the readout says "Prop rotation illustrative, not to rate". Checked on 4 consecutive frames (blades at different phases each frame). | worker `spin_mats`, `shots-main.json` `props_spin` |
| M-7 | Trim list applied: 1.1, 1.2, 1.3 to 4 s; 4.2 to 10 s (log window 98-126 kept, x2.8); 6.1 to 5 s. 5.3 extended 6 to 7 s (m-7, plate density). 122 -> 116.0 s | `shots-main.json` |
| M-8 | 3.2: camera key at 1.5 s with zero velocity (`hold` key flag, new in `load_film` / `hermite_cam`), sweep starts at 1.5 s, elevon WNG-006 at 50 % teal (`fab50` mode), hinge axis drawn as thin orange rods (worker `hinge_objs`) | worker, `shots-main.json` 3.2 |
| M-9 | 3.1 camera now az 135 el 30 to az 165 el 24 (was el 50 to 42) | `shots-main.json` 3.1 |
| m-1 | 0.2 s dip to the stage colour either side of each scene join (done in the Pillow pass, `dip_level`); card fade-in; 6.1 target-z drop moved into 6.2 (6.1 end target z 0, 6.2 key at 1 s with z -0.22, dist 2.5 so the taller card does not hide the aircraft) | `film_overlay`, shots |
| m-2, m-3 | 3.1 sub "21 deg mechanical stops (flight limit 20 deg, wing.py ELEV_LIM)"; 2.3 sub cut-away note; 2.5 sub "MEC-001 to MEC-005, MEC-008" plus cut-away note | shots |
| m-4 (part) | dl / dr added to the S4 readout. NOT done: blending the log clock over the time-scale steps at the S4 joins (x2.8 -> x26 -> x3.6); needs cross-shot state in `sitl_clock`. | |
| m-6 | Wording correction: "elevon peak 9.4 deg, peak altitude 86.6 m" of `sum.json` (also quoted in PD-007 / earlier text above) are TRANSITION-window values; the whole run reaches elevon 13.0 deg (back-transition) and 89.4 m. | this note |
| m-7 (part) | 5.3 plate unchanged except 7 s; its "99th percentile of the cup in S2: 0.47" is a skin-vertex percentile, D-210 quotes the element p99 (4.2 MPa = 0.21): regenerate or crop by the structures owner. | |
| m-5, m-8 | not done (optional / n/a) | |

## Source files read from git-ignored folders (M-5)

| File | Size | SHA-256 |
|---|---|---|
| `qp/A/sitl/runs/Z5_gb0/case.fwd.csv` | 1,098,835 B | `07729f67e48468591d023699e1e381b4a10a004a3cf04a2c702a57ed2cfa7bc8` |
| `qp/A/sitl/runs/Z5_gb0/sum.json` | 1,487 B | `9fecf1a1a27449f28febc20a5bedd5837dcf80f957c99c77d7bf297875abd933` |
| `qp/A/sitl/runs/Z5_gb0/result.json` | 3,124 B | `4cf658e3dce43c8f71f5184fafbb8e48654668882e17a5e71fff409ae0f8633c` |
| `qp/A/structures/out_fea/hub_fields_L0_d209.npz` | 3,163,448 B | `ef8e0173b747d911e3b876b81e383d07646e302d6a5810fd6818fcde7e70169c` |
| `qp/A/structures/out_fea/hub_F2.glb` | 3,257,212 B | `12e1aea35baaca86efa53519676732bd4cc9dd2dea63d0010474707a3779475d` |
| `qp/A/structures/out_fea/hub_S2.glb` | 3,257,212 B | `a73cb30fd625c67eb98a58f425cb122b49479e42e525c4163ac8623e648673fc` |

Tracked already: `hub_result_L0_d209.json`, `result_L0_current_d210.json`, `fea-arm-along.png`, `sitl/cad_mass.json`. The GLBs are regenerated by `python -I qp/A/structures/fea_hub_figs.py --tag d209` (after `fea_hub.py --level 0 --tag d209 --fields`). Not `.gitignore` changed.

## Highlight cut (R-VID-12), `film/shots-highlight.json`

24.2 s, seven items H1..H7 (the review's table): each item is a window [a, b] of a main-film shot (`src` field gives shot and main-film times), camera = the main path sampled every 0.25 s, log windows and the mechanism sweep cut at the same instants (H2 cut on the sweep waypoints 3.8 and 8.0 s), one short title per shot, tags and S4 / S5 readouts kept, card fade state carried (`fade_src_a`). It re-uses the main render's raw frames (overlay only); main-film times assume the 116.0 s film (S6 starts at 105 s, so H7 is 6.2 local 1-5 s = 111-115 s; the review's 108-112 s assumed 115 s).

## Verification (category: interference for the camera checks; no new simulation or FEA)

- `--cam-check` main (6,960 frames): 0 frames inside a part; only block: S2.2 10 frames (own prop, as before); nearest 0.0679 m (3.2). Highlight (1,452 frames): 0 inside, 0 blocked. Files `film/cam-clearance.json`, `film/cam-clearance-highlight.json`.
- 1080p preview, every 60th frame, 12 samples, 3 workers, all six scenes: `film/preview-contact-T030.png` (116 frames, taken before the final 6.2 camera tweak), `film/preview-contact-T030-S6.png` (S6 after it), `film/preview-contact-T030-highlight.png` (highlight, 24 frames); wall 133 s, 0.87 s per rendered frame. `film/timing-T030.json`.
- Not verified: full-rate smoothness of the S4 joins and of the new 3.2 camera hold (previews sample 1 per second); the 60-frame consecutive run 4.3 -> 4.5 asked for in review section 5 is left to the reviewer step. 3.1 now shows the rotation as a change of the elevon silhouette and tilt (view from aft, el 24-30), not along the hinge.
