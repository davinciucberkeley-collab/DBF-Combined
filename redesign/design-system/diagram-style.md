# Diagram style — SVG 3-views, morphological charts, proof graphs, wiring and block diagrams

All diagrams are SVG, drawn from data (params.json, interfaces.json, graph.json), never by hand. Colours are the
`tokens.css` variables so a diagram inlined in a page follows the theme; a standalone SVG embeds the light values.

## Common rules

| Item | Value |
|---|---|
| Fonts | IBM Plex Sans (labels), IBM Plex Mono (ids, numbers, units); fallback `system-ui` / `monospace` |
| Label sizes | title 16 px 600 · label 12 px 500 · id/number 12 px mono · footnote 11 px |
| Ink | `--fg` `#121619` (dark theme `#E6EAF0`); secondary `--fg-2`; muted `--fg-3` |
| Line weights | outline 1.5 px · construction 0.75 px · hidden `0.75 px dash 6 4` · leader 1.25 px · axis 1 px |
| Colour | only: subsystem hues (geometry), status hues (state), accent blue (dimension / selection), highlight orange (the part acted on). Nothing decorative. |
| Units | value, thin space, unit: `2 200 mm`, `7.42 kg`, `1.84` (dimensionless: no unit) |
| Numbers | tabular; thousands with thin space; 3 significant figures unless the source has more |
| Legend | one line under the figure; never repeats a label already on the drawing |
| Background | transparent; the page's `--panel` or `--stage` shows through |
| Size | 1200 px wide master; stroke widths are in px at that width (vector scales anyway) |
| Titles | in the caption, not inside the SVG |

## 3-views (SPEC.md, config comparison)

```
  ┌─────────────────┐
  │      TOP        │   third-angle: top above side, front to the right of side.
  ├─────────────────┤───────┐   Web: three in a row, same scale.
  │      SIDE       │ FRONT │
  └─────────────────┘───────┘
```

- Outline 1.5 px ink; fills by subsystem at 35 % opacity (so overlaps read), no gradients.
- Hidden lines dashed grey; show only where a part is fully hidden and matters (spar inside the wing).
- Dimensions in accent blue 1.25 px, ticks 6 px, text 12 px mono; only span, length, height, rotor diameter, CG.
- CG symbol: circle r 6 with two opposite quadrants filled, ink.
- Scale bar bottom-left: `0 — 500 mm`, 1 px ink, 11 px mono.
- Orientation: nose left in side view, nose up in top view.

## Morphological chart (configuration study)

Rows = functions (lift, cruise propulsion, transition, landing, wing build, fuselage, tail …); cells = options.
Use the HTML component (`.ds-morph` in components.css) for the web page; for a static SVG follow the same look:

| State | Look |
|---|---|
| chosen | accent ring 2 px + accent wash fill, `CHOSEN` tag |
| runner-up | dashed `--line-3` border, `RUNNER-UP` tag |
| rejected | 50 % opacity, name struck through, `OUT` tag; the reason lives in the trade matrix |
| not studied | empty dashed cell, `—` (an audit gap, never hidden) |

Cell: sketch 40 px tall (stroke 2 px, currentColor, top view), name ≤ 4 words 12 px centred. Function label
left, 150 px column, bold name plus one grey phrase saying what the function is. Chosen cells of one concept are
joined by a 1.5 px accent polyline down the chart when the chart shows a single concept path.

## Trade matrix and score bars

Score bars: 8 px tall, radius 2, track `--panel-3`, fill `--line-3`; the chosen row's bars `--accent`. Score
right of the bar in 12 px mono. Weighted total at the right in mono 500. Weights under the criterion name in
11 px mono. Never colour-code score levels (no red-to-green ramps); the bar length is the message.

## Proof-chain graph (2-D and 3-D viewer)

Evidence flows left → right: **source → parameter → calculation → claim → requirement**; tests attach to claims.

| Node type | Shape | Size base |
|---|---|---|
| source | document (rect with folded corner) | 36 px |
| parameter | square | 30 px |
| assumption | pill | 30 × 18 px |
| calculation | diamond | 40 px |
| claim | circle, value inside in mono | 44 px |
| requirement | hexagon | 48 px |
| test | circle with plus | 30 px |
| part | subsystem-coloured small square, only on `about` edges | 14 px |

- Size = base × (0.8 + 0.4 × importance / max importance).
- Fill = status wash, stroke = status colour, 1.75 px: UNVERIFIED amber, PROPOSED grey, CHECKED teal, VERIFIED green,
  FAIL red (`fails: true`). The word is shown on hover/selection and in the side panel; the legend shows the ladder.
- Edges `--line-3` 1.5 px with a 7 px arrowhead; `verifies` edges 2 px; an edge into a FAIL node red.
  Selected chain: edges and nodes at full opacity, everything else at 25 %.
- Labels: `title` (≤ 6 words) 12 px under the node; id on hover. Never draw the whole id (`CALC-PROP-HOVER-TW`)
  as the label.
- 3-D viewer: same shapes extruded 4 px, same colours, layers by type along x (sources left, requirements right),
  subsystems spread along y; camera orbits; a click opens the node's panel.

## Wiring and block diagrams

- Boxes 1 px `--line-2`, radius 5, fill `--panel`; subsystem square top-left of each box.
- Power lines 2.5 px (`wire_red`/`wire_black` from blender-style.json), signal 1.25 px yellow, data 1.25 px grey dashed.
- Every line carries gauge and connector in 11 px mono at its midpoint: `12 AWG · XT60`.
- Disconnects at removable joints drawn as a gap with two half-circles, labelled with the interface id.

## Do / don't

| Do | Don't |
|---|---|
| One idea per diagram; split otherwise | A system diagram with 40 boxes and crossing lines |
| Number from the source; units on every number | "approx." or unlabelled axes |
| Grey for anything not the subject | Colour every part of the aircraft in every view |
| Leave white space; 24 px min between groups | Fill the canvas |
| Label parts by id *and* name once | Repeat the legend in every panel |
