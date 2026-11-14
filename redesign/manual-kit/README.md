# redesign/manual-kit: build manual generator

Each subsystem writes its build steps once, in `steps.json`. This kit turns them, plus `parts.csv`,
`interfaces.json` and the Blender renders, into a build manual: an HTML page with one card per step, a Markdown
copy, a kitting list, a tool list and a glossary for first-time builders. It does not depend on the aircraft
configuration. The demo uses the generic example aircraft (`redesign/fusion/examples`, 6 steps).

## Commands

| What | Command | Time |
|---|---|---|
| Check the steps only (no Blender) | `python -I redesign/manual-kit/build_manual.py --examples --check` | < 1 s |
| Build the demo manual (renders only missing or changed figures) | `python -I redesign/manual-kit/build_manual.py --examples` | 0.5 s, or about 15 s per new figure |
| Quick draft renders (16 samples, half size) | `... build_manual.py --examples --draft` | about 3 s per figure |
| Real aircraft (`redesign/subsystems/*/steps.json`) | `python -I redesign/manual-kit/build_manual.py` | same |
| Tests (validator, kitting sums, markers, HTML structure) | `python -I redesign/manual-kit/test_manual_kit.py` | < 1 s |

Other options: `--no-render`, `--force` (re-render every figure), `--strict` (warnings fail too), `--src`,
`--interfaces`, `--manual`, `--out`, `--samples N`, `--blender EXE` (or set the env var `DBF_BLENDER`).
Exit code 1 on any error. Output goes to `out/<examples|aircraft>/`:

| File | What it is |
|---|---|
| `manual.html` | the manual. Open it from disk. It needs only `img/` beside it (fonts come from Google Fonts, with a system-font fallback) |
| `MANUAL.md` | the same content as Markdown, readable on GitHub. Step figures are self-contained SVGs |
| `kitting.csv` | per work package: parts, fasteners, consumables, tools with quantities and the steps that use them |
| `tools.csv` | each tool, its work packages and its steps |
| `img/` | renders (`<fig>.jpg/.png/.json`), `<fig>.numbered.svg` (render + numbered dots), `figures.spec.json` (the generated Blender spec), `figures.lock.json` |

## What the HTML manual does

- One `.ds-step` card per step (design system): the render on the left, with orange numbered dots that match the
  numbered actions on the right. The figure stays in view while you scroll the actions. Click it for full size.
- On the right: goal, safety callouts, actions with tick boxes, then Parts / Fasteners / Tools / Consumables for
  this step only, joint-stack and wiring tables (folded), the CHECK with a box for the measured value and a Pass
  tick, and "What can go wrong" (folded).
- Hover over a part id to see its name, status, mass, make/buy, vendor and the step that fits it. The part is
  also outlined in the figure. Hover over an edge id to see its joint stack or wire. Glossary words are
  underlined on first use in each step.
- The progress bar counts the steps whose CHECKs are all ticked Pass. Ticks and measured values stay in the
  browser's localStorage, keyed by manual id and revision. Nothing is sent anywhere.
  The reset button clears them.
- Keys: `n` next step, `p` previous. Light and dark themes. Printing (A4) opens every folded section, keeps each
  step on one page, prints empty tick squares and blank lines for the measured values, and starts each work
  package on a new page.
- Reference sections: build sequence, kitting list per work package (with tick boxes for picking parts), tool
  list, parts index (parts that no step fits are shown as missing), glossary, build log (every CHECK in one
  table, linked to the cards) and open items (the generator's warnings).

## Step format: `<subsystem>/steps.json`

Put `steps.json` next to the subsystem's `parts.csv` and `interfaces.json` (`redesign/subsystems/<name>/`).
Working examples: `examples/ex_*/steps.json`.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | `WNG-S01` (subsystem prefix + `S` + number), unique |
| `wp` | yes | work package id from `manual.json` (steps of one subsystem can sit in several WPs, e.g. final assembly) |
| `title` | yes | imperative, ≤ 60 characters: "Bolt the wing to the fuselage" |
| `goal` | no | one sentence: what is true when the step is done |
| `after` | no | step ids that must be done first (checked: never in a later WP, no cycles) |
| `parts` | no | part ids fitted in this step: `"WNG-001"` or `{"id": "WNG-001", "qty": 1}` |
| `edges` | no | interface edges this step makes. Fasteners, tools, torque, thread engagement, access and wiring data all come from these edges' joint stacks and wire blocks in `interfaces.json`. Do not copy them into the step |
| `fasteners_extra` | no | `[{"item": "M3 washer", "qty": 2}]` for hardware that is not in a joint stack |
| `tools` | no | tools besides those the joint stacks name (a torque screwdriver is added when a torque in N m is given) |
| `consumables` | no | `[{"item": "30 min laminating epoxy", "qty": 15, "unit": "g"}]` (threadlocker is added automatically when a joint stack says so) |
| `time_min`, `wait_min` | `time_min` | hands-on minutes; waiting (cure) minutes |
| `safety` | no | `[{"level": "note|caution|stop", "text": "..."}]`. Use `stop` for LiPo, props, hot wire and solvents |
| `actions` | yes | numbered actions: `{"do": "text", "at": "E-WNG-01"}`. `at` (a part id, an edge id or `[x, y, z]` in metres) puts that action's number on the figure |
| `check` | yes | one object or a list: `{"type", "text", "target", "record"}`. Types: `dimension, mass, fit, torque, continuity, voltage, function, visual` (`visual` gives a warning). For `"type": "mass"`, `"of": ["FUS-*"]` and `"tol_pct": 5` compute the target from the declared masses of the parts fitted so far |
| `can_go_wrong` | warn | `[{"problem": "...", "fix": "..."}]` |
| `figure` | no | overrides for the step figure, in the `render_figures.py` format: `camera` (preset, `fit`, `az`, `el`, `lens`, `frame`), `xray`, `ghost`, `hide`, `focus`, `context`, `pose`, `explode`. `false` = no figure |
| `details` | no | extra figures (close-ups) with a `title` and the same keys. Shown as thumbnails under the main figure |
| `status` | no | `PROPOSED` (default), `CHECKED`, `VERIFIED` (a teammate built from this text and the CHECK passed) |

**Text in actions and checks.** Part and edge ids such as `WNG-003` become hover chips. Text in backticks is set
in mono (values with units). `{ex_wing.tip_y_m*2|mm}` inserts a number from that subsystem's `params.json`
(`{params.wing.span_m|mm}` reads the shared `redesign/params/params.json`), so the number follows the design. The
page shows the source file and key when you hover over it. An id or number that cannot be resolved is an error.

**Figure roles by default.** The parts fitted in the step are orange. Parts fitted earlier are drawn in their own
material only if the edges made so far connect them to this step's parts, so a wing built on the bench is shown
without the fuselage. Everything else is hidden. A step with no new parts (a step that only joins
subassemblies) highlights `part_a` of each edge it makes. Each action's `at` becomes an anchor. The dot sits next
to it on a short leader, with a hollow dot and a dashed leader when the anchor is hidden behind another part.

**`manual.json`** (one per manual, kept with the steps: `examples/manual.json`, for the real aircraft
`redesign/subsystems/manual.json` or `redesign/manufacturing/manual.json`): `id`, `title`, `subtitle`, `revision`,
`date`, `status`, `subsystems` (order), `work_packages` (`id`, `title`, `summary`, in build order), `safety`
(rules shown before step 1) and `figures` (overview figures in `render_figures.py` format. The one with id
`cover` becomes the cover image). Without a `manual.json`, each WP id becomes its own work package.

## Files

| File | What it does |
|---|---|
| `build_manual.py` | command line: load, check, render missing figures, write HTML + MD + CSV, check the page structure |
| `steps_lib.py` | loads steps, parts and interfaces. Validation, step order, fasteners and tools from joint stacks, figure roles, mass targets, kitting roll-ups, glossary filter |
| `figures.py` | figure specs, change detection (hash of spec + interfaces, params, modules, Blender toolkit, style), one Blender run, numbered-dot layout, numbered SVG |
| `html_out.py` | the HTML page (inlines `design-system/tokens.css` + `components.css`) |
| `md_out.py` | `MANUAL.md`, `kitting.csv`, `tools.csv` |
| `glossary.json` | first-time-builder terms. Only the terms the manual uses are printed |
| `test_manual_kit.py` | 8 tests: the example loads clean, every part and edge is fitted once, fastener and threadlocker sums, mass target, figure roles, a broken copy fails, markers do not overlap, the HTML is balanced, has unique ids and existing images |
| `examples/` | the demo: `manual.json` + `ex_fuselage`, `ex_wing`, `ex_booms` (`steps.json`, `parts.csv`. Interfaces and geometry come from `redesign/fusion/examples`) |

## What is checked, and what is not

| Checked (every build, in seconds) | Not checked |
|---|---|
| every id in steps and text exists; every `{param}` resolves | that the words are right: a teammate builds from them once, then the step is `VERIFIED` |
| every part and interface edge is fitted by exactly one step (missing ones listed as open items) | that the camera view shows the action well: look at the figures (`img/*.numbered.svg`) |
| step order: `after` never points to a later WP; no cycles; an edge's parts are fitted by then | real torques, fits and cure times: they come from `interfaces.json` and the steps as written |
| every check has a measurable target (`visual` warns); thread engagement ≥ the joint stack's minimum | prices and vendors in `parts.csv` (the example values are made up, `EST`) |
| figures: anchors outside the image or cut-off parts are reported; the HTML is balanced, ids are unique, every image file exists | how the page looks in every browser (checked here with Edge headless screenshots) |

## Known limits

- Animations (BRIEF: MP4 clips) are not built in yet. A step could carry a `"clip"` once the Blender toolkit makes them.
- Fasteners are summed by their exact text. `M3 washer` and `M3 washer A2` are counted as two lines, so write joint stacks consistently.
- Tool names from different joint stacks are only de-duplicated when the text matches (case ignored).
- The example aircraft has no clamp, saddle or insert geometry. Those actions point at the joint origin.
