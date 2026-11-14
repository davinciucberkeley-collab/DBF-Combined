# redesign/viewer: aircraft web viewer

A static three.js page for the assembly: four modes, a part browser, a part panel with interfaces and claims,
measure, standard views and a mass/CG overlay. No server and no build step: open `index.html` (double-click works),
or publish the `redesign/` folder on GitHub Pages. It works for any configuration; until the real aircraft has a
model it shows the generic test aircraft (`redesign/fusion/examples/`), which is a demo, not a design.

## Use

| Action | How |
|---|---|
| Open | `redesign/viewer/index.html`; `?data=examples` or `?data=aircraft` picks the dataset (default: the aircraft if it has a model, else the example) |
| Modes | **Whole** · **Inside & wiring** (non-electrical parts x-ray, wires and joints shown) · **Structure** (load-carrying parts and joint markers only) · **Exploded** (animated, slider). Keys `1`-`4` |
| Colour by | Subsystem (design-system hues) · Material (as exported from Blender) · Status (`PROPOSED` `MODELLED` `CHECKED` `VERIFIED`) |
| Part browser | grouped by subsystem with mass; search id, name, material, vendor or status (`/`, words AND-ed, Enter selects the first); a **wiring** group lists the wire edges |
| Part panel | click a part: id, name, status, mass, material, make/buy + cost, vendor or source file, CG; its interfaces with the joint stack / wire installation / motion; the proof-chain claims about it (link to `../proofs/viewer/`). Hinged surfaces get a deflection slider. Buttons: Focus, Isolate, Open SPEC |
| Focus | double-click a part, or `F` |
| Views | 3-D (perspective) · Top · Front · Side (orthographic, pan and zoom only); Fit / `Home` |
| Measure | `M`, then click two surface points: distance and Δx Δy Δz in mm, aircraft frame |
| Mass / CG | `C`: CG marker, CG target band (green = in range, red = out), total vs limit, subsystem vs allocation, parts with no mass/CG |
| Links | `index.html#part=WNG-003&mode=inside` opens on a part (the proof viewer links here); the URL follows the selection |
| Theme | sun button (light/dark, remembered); `?theme=dark` |

## Update after a design change

Run from the repo root (each step takes seconds; `B` = `<your blender.exe> -b --factory-startup -P`, see `redesign/blender/README.md`):

| # | Step | Command |
|---|---|---|
| 1 | Merge the interfaces | `python -I redesign/interfaces/merge_check.py` |
| 2 | Export the model | `B redesign/blender/export_glb.py` |
| 3 | Rebuild the proof chain (for claims) | `python -I redesign/proofs/build_graph.py` |
| 4 | Collect the viewer data | `python -I redesign/viewer/build_data.py` |
| 5 | Check | `node redesign/viewer/check_viewer.js` (must print `OK`) |

Add `--examples` to steps 2, 4 for the test aircraft. Step 4 prints warnings (part in the model but not in
`interfaces.json`, status or mass differing between the two, claims naming unknown parts, missing inputs); the
viewer lists them under "data warnings". Commit `data/` so GitHub Pages serves it.

## Files

| File | What it does |
|---|---|
| `index.html`, `viewer.css` | page; styles come from `../design-system/tokens.css` + `components.css` |
| `app.js` | scene, loading, modes, picking, panel (browser only) |
| `model.js` | pure rules: which parts a mode shows, structural test, mass/CG, search, panel rows, URL hash. Also run by the check |
| `build_data.py` | stdlib: GLB + interfaces + parts.csv + proof graph + mass budget → `data/<dataset>/` |
| `data/<dataset>/` | generated: `assembly.glb`, `assembly.glb.js` (base64, for `file://`), `viewer-data.js` / `.json` |
| `examples/parts.csv` | vendor and cost demo rows for the test aircraft (it has no `parts.csv` of its own) |
| `check_viewer.js` | Node smoke test, about 0.1 s (below) |
| `vendor/` | three.js r170 as one classic script; versions, licence and hashes in `vendor/README.md` |

## Where the data comes from

| Shown | Source |
|---|---|
| geometry, part nodes, explode vectors, joint positions and axes, wire tubes | `blender/out/<dataset>/glb/assembly.glb` (node extras, see `redesign/blender/README.md`) |
| name, status, mass, material, CG, make/buy, electrical role, interfaces | `interfaces/interfaces.json` (examples: `interfaces/example-output/`). This wins over the GLB extras |
| vendor or file, unit cost, qty, process | `subsystems/*/parts.csv` (examples: `viewer/examples/parts.csv`) |
| claims about a part | `proofs/out/graph.json` (examples: `proofs/examples/out/`), claims' `parts` |
| mass limit, allocations, CG target | `params/mass_budget.json` (examples: `fusion/examples/mass_budget.json`) |

Mode rules (`model.js`): **Inside** shows parts with an `electrical` role solid and ghosts the rest. **Structure**
shows a part if `structural` is true, or, without that field, if it is not electrical and has a mechanical edge
that is not a hinge (so control surfaces, battery, ESC, servos and motors are hidden). **Exploded** moves each part
by its `explode_m` from the Blender export. Mass and CG are the declared values; ground tools (`flight: false`)
are excluded.

## Speed

The part list and panel work as soon as `viewer-data.js` (20 kB for the demo) has loaded; the GLB then streams
with a byte progress bar (over http) and the scene renders only when something changes. The demo GLB is 155 kB
and is parsed in under 10 ms. From `file://` the base64 copy is read instead (no byte count; about a third larger).

## What is checked, and what is not

| `node redesign/viewer/check_viewer.js` proves | Not proved |
|---|---|
| the three.js bundle loads; each dataset's `.js` = `.json`; the base64 copy = the GLB; size and SHA-256 match | how it looks: checked by eye in Edge (light and dark, 800 px and 1600 px wide) on 2026-11-09 |
| the GLB parses with three's GLTFLoader and every part with geometry is a node with a mesh and `explode_m` | WebGL on every student laptop (no WebGL: the page says so; list and panel still work) |
| model.js rules on the test aircraft: mode roles, mass 1 470 g, CG by hand, search, interfaces, claim links, URL hash | that `structural` inference is right for every real part (CHANGE-REQUESTS #2) |
| every file index.html links exists, every `#id` app.js uses exists, app.js parses | |

## Known limits

- Exploded and deflected parts are moved, wires are not; wires and joint markers hide while exploded.
- The selected part's outline is a 1 px edge line (WebGL has no thick lines).
- The page loads IBM Plex from Google Fonts; offline it falls back to system fonts.
