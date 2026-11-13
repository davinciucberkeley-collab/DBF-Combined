# redesign/blender: Blender backend, GLB export, build-manual renders

The same subsystem modules that build the Fusion assembly (`build(ctx)`, see `redesign/fusion/README.md`) also build
the aircraft in Blender 4.2. This folder turns that build into GLB files for the web viewer and into PNG/SVG figures
for the build manual and reviews. It works for any configuration: everything is driven by `interfaces.json`,
`params.json` and the modules. The demo uses the generic example aircraft in `redesign/fusion/examples/`.

## Commands

`B` = `<your blender.exe> -b --factory-startup -P` (Blender 4.2; on the team laptop it is under
`%USERPROFILE%/tools/blender/blender-4.5.14-windows-x64/`. `manual-kit/build_manual.py` finds it by itself: `--blender`,
env `DBF_BLENDER`, PATH, then the usual install folders)

| What | Command | Time |
|---|---|---|
| Check the Blender build against fusionkit | `B redesign/blender/selftest.py -- --examples` | 2 s |
| GLB export (assembly + one per subsystem) | `B redesign/blender/export_glb.py -- --examples` | 3 s |
| Render all figures in a spec | `B redesign/blender/render_figures.py -- --examples [--png]` | 15-20 s per figure |
| Render some figures, quick draft | `... render_figures.py -- --examples --only step --samples 16 --percent 50` | 5 s per figure |
| Re-run the annotation only | `python -I redesign/blender/annotate.py [--png] out/examples/figures/step_1.json` | < 1 s |

Leave out `--examples` to build the real aircraft from `redesign/subsystems/*/fusion/` (no modules exist yet, so that
currently gives an empty assembly). `--root DIR` builds any other module root. Use `--spec FILE` to pick a figure spec.
Measured on the team laptop (i7-13700H, RTX 4060), 1600 x 1000 px, 48 samples: 12-18 s per figure on the GPU,
38 s on the CPU only (`--device CPU`). EEVEE (`--engine EEVEE`) also works but was not faster here, and it draws no
floor shadows.

## Files

| File | What it does |
|---|---|
| `blender_backend.py` | `fusionkit.Backend` for Blender: prism, revolve and loft shapes become meshes; joints become empties; wires become tubes. `build(examples=True)` runs every module |
| `explode.py` | exploded-view vectors computed from the interface graph (see below) |
| `export_glb.py` | `assembly.glb`, `<subsystem>.glb`, `manifest.json` |
| `render_kit.py` | `Stage`: studio/workbench scenes, roles (focus, context, ghost, x-ray, hidden), camera presets, callouts, render + JSON sidecar |
| `annotate.py` | stdlib only: PNG/JPEG + sidecar become a self-contained SVG with labels, leader lines and a caption band |
| `render_figures.py` | renders the figures and numbered build steps listed in a JSON spec |
| `selftest.py` | Blender mesh vs fusionkit data: bounding box, volume, manifold, properties, GLB round trip |
| `examples/figures_example.json` | the demo spec: iso, exploded, aileron close-up, top, side, build steps 1-3 |
| `out/examples/` | generated: `glb/` and `figures/` (`*.png` render, `*.svg` annotated, `*.json` sidecar, `*.annotated.png`) |

## What the Blender build contains

| Object | Name | Custom properties (become glTF `extras`) |
|---|---|---|
| one mesh per part: its bodies cut, then united into one solid (D-88) | part id, e.g. `WNG-001` | `part_id, name, subsystem, material, mass_g, status, make_or_buy, interfaces` (JSON list of edge ids), `explode_m` |
| one tube per wire, corners rounded to the edge's `bend_radius_mm` | edge id, e.g. `E-FUS-03` | `edge, part_a, part_b, via, dia_mm, gauge_awg, connector, bend_radius_mm, support_points, strain_relief, disconnect` |
| one empty per joint | `JOINT E-WNG-04` | `edge, kind, part_a, part_b, axis, limits` |

Frame: Blender world = aircraft frame (metres, x aft, y right, z up). The glTF files are +Y up, so glTF (x, y, z) =
aircraft (x, z, -y). `explode_m` stays in the aircraft frame. Colour modes (`--mode` / spec `"colour"`): `material`
(foam, ply, carbon, LiPo, PCB, motor, ... matched from the part's `material` text), `subsystem` and `status` (the
design-system subsystem colours and status ladder).

## Figure spec (JSON) and the look

Each figure sets roles by pattern (part ids, edge ids, `*`): `focus` (orange `--highlight`: added in this step),
`context` (own material: already fitted), `ghost` (pale and see-through), `xray` (ghosted although in focus, to see
inside a box), `hide`. A `steps` list gives numbered build steps: the parts each step `add`s are orange, the parts
from earlier steps are shown as built, the rest is hidden. With `"fit": "all"` every step uses the same camera.
Camera presets: `iso`, `iso_rear`, `iso_below`, `front`, `rear`, `side`, `side_right`, `top`, `bottom` (the elevation
and plan views are orthographic) and `closeup` (`"fit": [part ids]`); `az`/`el` override the angle. Callouts take a
part id (`id` and name), an edge id with a `joint_stack` (`2x M4x30 SHCS + nyloc`, then the tool and torque), a wire
edge (connector, AWG, bend radius), any `{"at": [x, y, z], "text": ...}`, or `"parts"` / `"auto"`. `pose` deflects a
revolute joint (degrees). The full format is in the docstring of `render_figures.py`.

Look (from `redesign/design-system/tokens.css`): light stage gradient, Standard view transform so the token colours
stay true, Freestyle ink outlines (lighter on ghosts, none on wires), soft studio lights placed relative to the camera
so every preset is lit the same way, and a shadow catcher floor (none in plan views). Labels sit in the side margins
(the camera keeps the middle 56 % for the subject when there are callouts). They keep their anchors' top-to-bottom
order and never overlap. A dot marks a visible point of the part, found by ray casting. A hollow dot, a dashed leader
and "(behind other parts in this view)" mark an anchor that is hidden, for example a fastener underneath.

The sidecar `<id>.json` lists what is shown: the camera, each part's role, status, mass and pixel box, the callouts
with their pixel and world positions, hidden parts, `clipped` (framed parts cut off by the image edge; it should be
empty) and the render time. The build-manual kit and the viewer can read it.

## Exploded views

`explode.vectors()` needs no per-aircraft table. Parts and their structural edges (joints and contacts) form a tree
from a root (the part with the most edges, or `"root"`). Each child, with everything hanging off it, moves along
the axis direction that frees it from its parent with the shortest travel, measured on bounding boxes. A motor on a
boom lifts straight up, and a servo in a wing pocket drops out below. Then it moves a further `gap` (0.06 m).
Bonded edges (connection-type method `bonded`) do not separate. `"overrides": {"FUS-002": [0, 0, 1]}` sets a direction
by hand. Every part stores its vector as `explode_m`, so the web viewer can animate the same explode.

## What is checked, and what is not

| `selftest.py` proves (seconds) | Not proved |
|---|---|
| each part's mesh bounding box is within 1 mm of fusionkit's, and its volume within 3 % (0.0-0.3 % on the examples) | that Fusion builds the same solids (`UNVERIFIED-IN-FUSION`, see `redesign/fusion/`) |
| closed manifold meshes with outward normals; every property present | that parts do not interpenetrate |
| GLB round trip: every part id comes back with its extras, z up | how the web viewer uses the extras |

Render quality is checked by eye: open `out/examples/figures/*.annotated.png`.

**Cuts and unions (D-88).** Each body is cut by all its cutters at once with Blender's MANIFOLD boolean; only if
that fails does the exporter fall back to one cutter at a time (MANIFOLD, nudged, grown 3-10 µm, EXACT, FAST). Every
cut is then verified: no surface of the result more than 0.02 mm inside a cutter, no material 0.045 mm under a
cutter's surface (both inside tests use the GLB gate's own: odd crossings on 3 of 5 skewed rays), no open edges. A
failed check prints `CUT NOT VERIFIED <part> ...` with its depth and location. Each part's cut bodies are then united
into one watertight solid (MANIFOLD), checked for an unchanged box and a volume between the largest body and the sum;
a failure prints `UNION NOT CLEAN <part>` and keeps the bodies as separate shells. A release export has neither line
(`grep -c "CUT NOT VERIFIED\|UNION NOT CLEAN"` on the export log is 0); the GLB gate (`collision/collide.py --glb`)
then checks the exported meshes against each other.

## Build film (`showcase/animation/`)

The build film shows the aircraft put together the way a person would, in `BUILD-GUIDE.md` order, and every motion in
it passes a swept-path physics check first. Two commands, run from the repo root:

```
python -I redesign/showcase/animation/assembly_check.py   # plan + check (~25 min) -> build/assembly_plan.json, ASSEMBLY-CHECK.md
python redesign/showcase/animation/render_build.py        # render the plan (~19 min) -> build/k09l-build.mp4, stage-NN.mp4/.png
python redesign/showcase/animation/render_build.py --preview   # half size, every 3rd frame, into --work only
python -I redesign/showcase/animation/assembly_check.py --steps 7.2,7.4   # debug: check only these steps
python -I redesign/showcase/animation/assembly_check.py --legacy          # also score the old fly-in film
```

- **Order**: `assembly_plan.STEPS`, one row per numbered BUILD-GUIDE step (stages 2-11), with its caption and the parts
  and wires it places. Bench sub-assemblies (spar + plugs + blocks, plugged motor tubes, pod box, motor on its mount,
  servo + arm, foot inserts, FC + card) are built beside the aircraft and moved on as one piece.
- **Motions are derived, not drawn**: `assembly_check.py` tries removal directions from the geometry (the mount face
  normal, the part's own bore / pin / tube / screw / extrusion axes, then the world axes), sweeps the part along each
  one in 0.05-1 mm steps against everything already placed (the collision gate's own bodies and cutters, so holes,
  bores and slots are empty), and keeps the first clear one; if a straight path is blocked further out it tries
  out-then-across. Screws turn over their last 6 mm. Tape, wet epoxy and wires are laid in place (support check only).
  The few true special cases (fixtures, the spar slot cut from below) are the one `OVERRIDES` table; open design
  blockers the guide already names (SW-01 strap eyes) are the `KNOWN` table and stay listed in the report.
- **Support**: each placed item must touch something already placed (or sit on a bond line the interfaces graph
  declares, gap up to 0.6 mm), or be held by a named fixture.
- Exit code of the check: 1 when any motion passes through a placed part deeper than 0.05 mm and is not a `KNOWN`
  blocker. The renderer refuses to run without `build/assembly_plan.json`.
- Times measured 2026-11-13 on the team laptop: check 25 min (meshing 3 min, the rest is the sweeps), render 19 min for 3556 frames
  (118 s of film) at 1280 x 720: 2 min to build the scene, 9 min Workbench, 8 min overlay and encode.
- **When the CAD changes** (new parts, connectors, terminals): re-run both commands. New parts are planned
  automatically; a part no step names is placed in a catch-all last step and listed in the report, so add it to the
  right row of `STEPS`.

## Known limits

- Smooth lofts are refined with a Catmull-Rom spline. Fusion fits its own spline, so the two surfaces differ by about 0.01 mm.
- Label widths are estimated (no font metrics in the standard library). Very long words can overrun a box. Keep callout text short.
- `--png` rasterises the SVG with Edge or Chrome in headless mode if one is installed. Without a browser you still get the SVG and the plain PNG.
- Freestyle prints `Error: strokes set empty` when a line set has nothing to draw. It does no harm.
- The build film (`showcase/animation/render_build.py`, section above) does not use `Stage` yet; it drives Workbench
  directly from the checked plan.
