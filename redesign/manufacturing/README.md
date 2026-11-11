# redesign/manufacturing: shop files from the CAD (fixes MF-01)

One command rebuilds every file the shop needs from the same `build(ctx)` modules that `check.py`, BuildAll
and the Blender GLB export use. The files therefore always match the CAD.

```
python -B redesign/manufacturing/make_shop_files.py
```

It takes about 20 s. Blender 4.x is needed for the STLs. The script looks for it in `--blender PATH`, then `$BLENDER`,
then `blender` on the PATH, then `C:/Users/dillo/tools/blender/blender-4.2.3-windows-x64/blender.exe`.
`--no-stl` writes the DXF, PDF and CSV files without Blender. The exit code is 1 if any check fails.

Start with **[`out/SHOP-PACK.md`](out/SHOP-PACK.md)**. It says what each file is, the order to make them and the
Jacobs Hall machine for each. The checks are in [`out/CHECKS.md`](out/CHECKS.md).

## What it writes (`out/`, wiped and rebuilt on every run)

| Output | Content |
|---|---|
| `print/<part>_<material>[-colour]_x<qty>.stl` | One STL per distinct printed geometry, in mm and in print orientation. Mirror twins are merged when they are the same solid; otherwise they get A/B files. Qty includes spares |
| `jigs/*.stl` | JIG-01 tube posts, JIG-02 fin-alignment collar, JIG-03 cant gauge A/B (`jigs.py`) |
| `PRINT-LIST.csv` | Material, colour, qty, orientation, layer, perimeters, infill, supports, estimated time and mass per piece, CAD mass, and the source of each setting |
| `laser/*.dxf`, `laser/foamboard_1to1_letter.pdf` | Nested sheets: foam board (half-fin boards and pod shell), Coroplast box panels, 3 mm ply. The PDF has 1:1 knife templates |
| `CUT-LIST.csv` | Every sheet piece: file, qty, size, kerf, machine, which laser bed it fits |
| `hotwire/` | WNG-001 root and tip templates (DXF) and a 1:1 tiled letter PDF with registration crosses |
| `contact-sheet.png`, `dxf-preview.png` | Every print on its bed and every nest, for a quick look |
| `CHECKS.md`, `manifest.json` | Checks (watertight, bounding box against the CAD, sizes against params, closed DXF outlines). `manifest.json` holds the sha256 of every file, so re-running and diffing it proves the output is deterministic |

## How it works

| File | Role |
|---|---|
| `make_shop_files.py` | Entry point |
| `cad_source.py` | Read-only adapter. It runs `fusion/build_all.py` on the stub backend and turns component bodies into print jobs (bodies filtered and grouped per `shopconfig.PRINT`) and flat sheet outlines |
| `shopconfig.py` | Every non-geometry decision: material, spares, orientation rule, slicer settings with their source, sheet stock, kerf. **Edit this file, not the subsystem modules** |
| `blender_mesh.py` | Runs inside Blender. It meshes each body with `blender/blender_backend.py`'s builders and unites the bodies with Blender's exact boolean |
| `mesh_ops.py` | numpy: STL io, weld, islands, watertight test, orientation, identical-part test |
| `dxf.py`, `hotwire.py`, `jigs.py`, `contact_sheet.py` | DXF R12 writer, reader and nester · S5010 templates and the 1:1 tiler · jig geometry · pictures |

The **orientation rule** works like this. The candidate bed faces are the planes the whole part can rest on. The
largest one wins, and on a tie the one that gives the lower part. `shopconfig` can force a face where a BUILD.md
names one (for example "rim end on the bed" or "collar axis vertical"), or limit the candidates to faces normal to
chosen axes. The part is then turned about Z for the smallest footprint and centred on the bed.

**Adapters, not edits.** Nothing under `subsystems/`, `fusion/`, `blender/` or `params/` is modified, and bytecode
writing is switched off. Where the CAD needs help, the help lives here and is reported in `CHECKS.md`:

- POD-008 spacers 2/4/6 mm are extruded from the CAD spacer section, sized by `pod/params.json` `spacer_set_m`.
- A prism hole that crosses its own outline is made as the outline minus the hole.
- Zero-width spikes in a loop are removed.
- Bodies that touch only along an edge are fused with a 0.01 mm overlap.

**Re-run after any CAD change.** Other agents' edits (fin tip, landing, pod, motor mounts) flow through
automatically. If a part is renamed or a body is removed, the run lists it under "Issues" instead of failing
silently.
