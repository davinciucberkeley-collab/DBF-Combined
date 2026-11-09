# DBF redesign design system

One look for everything the redesign publishes: the configuration comparison page, the build manual (web and
print), the three.js aircraft viewer, the proof-chain graph, the Blender figures and the Markdown docs.
Built in the spirit of *impeccable*: remove text until only what the reader needs is left, then make that read
at a glance. Mode is **Operate/Read**, so the brand lives in precision, not expression.

| File | What it is | Who reads it |
|---|---|---|
| `tokens.css` | colours (light + dark + print), type, spacing, radii, motion, subsystem and status hues | every HTML output |
| `components.css` + `components.html` | the components, with a live showcase in both themes | config page, manual-kit, viewer, proofs |
| `blender-style.json` + `BLENDER-STYLE.md` | render parameters and the callout pass | `redesign/blender/` |
| `diagram-style.md` | SVG 3-views, morphological charts, graphs, wiring diagrams | config study, proofs, SPEC figures |

Open `components.html` in a browser (works from disk). Load order in any page:
`tokens.css` → `components.css` → page CSS. Fonts: **IBM Plex Sans** (words) and **IBM Plex Mono** (anything
measured, cited or coded), from Google Fonts, SIL Open Font License 1.1; the system stack is the offline fallback.

## Seven rules

1. **One idea per screen.** A page, a step, a figure or a diagram says one thing. If it needs two orange parts or
   two headlines, split it.
2. **Numbers carry units and a source.** `7.42 kg` not `7.42`; every value in a table has a source column
   (`params.json#…`, a calc script, a URL + date). Unknown is `—`, never a guess.
3. **Status is a word, not a colour.** Exactly `UNVERIFIED` `PROPOSED` `MODELLED` `CHECKED` `VERIFIED` (+ `FAIL`
   for a negative margin). The colour accompanies the word; it never replaces it.
4. **Remove text ruthlessly.** Tables over prose, a verdict sentence over a paragraph, labels ≤ 4 words, headings
   that stand alone (no eyebrows, no "Introduction"). If a sentence restates the figure, delete it.
5. **Colour has a job.** Blue = *here / selected / follow this*. Orange = *the part you act on* (figures only).
   Status hues = status only. Subsystem hues = geometry only. Everything else is neutral.
6. **Flat, 1 px, 8 px.** Panels are flat with a hairline border and 8 px corners; no shadows except popovers; no
   coloured left borders; no gradients except the 3-D stage.
7. **Same thing, same look, everywhere.** A part chip in the manual, the viewer and the config page is the same
   component. A status badge is `.ds-badge`. A figure id is `FIG BMS-07`. Do not restyle locally.

## How each output applies it

**Configuration comparison page** (Operate). Top bar + sub-tabs (`Summary · Morph chart · Concepts · Trade matrix
· Decision`). The morphological chart uses `.ds-morph` with chosen / runner-up / rejected cells; the trade
matrix `.ds-trade` with neutral bars and one accent row; concept cards `.ds-concept` with one sketch, three
numbers, one verdict sentence. The decision is one `.ds-metrics` strip and one paragraph. Rejected options stay
visible (faded), never deleted: that is the completeness audit the mentor asked for.

**Build manual** (Read, web + print). One `.ds-step` per step: figure left, numbered actions right, parts and
tools for this step only, a `CHECK` box last. Callout numbers in the figure = action numbers. Callouts: `note`,
`caution`, `stop`, `check`. Print uses the `@media print` tokens (white paper, black ink, orange and blue kept);
steps never split across a page (`break-inside: avoid`). Stop callouts for LiPo, props, hot wire, solvents.

**Aircraft viewer** (Operate). Modes as a `.ds-seg`: Whole · Inside & wiring · Structure · Exploded. Stage
gradient `--stage-top/--stage-bottom`. Geometry coloured by **subsystem** in Whole/Structure, by **status** when
the "status" overlay is on, ghosted blue-grey at 18 % for context. Selected part: accent outline 2 px, others
at 60 %. Part panel `.ds-part`: id, name, status, numbers, interfaces, claims; three buttons (Focus, Isolate,
Open SPEC). Loading and error states say what happened and offer one action; no spinner text in caps.

**Proof-chain graph** (Operate). Shapes by node type, fill by status, size by importance (see `diagram-style.md`).
Left → right evidence flow. Clicking a node opens the same panel style as the viewer; a FAIL node and its edges in
red; a chain selection dims the rest to 25 %.

**Blender figures.** Three part classes (act orange / built real material / ghost); three-point area lights;
AgX; Freestyle outline 0.8 px per 1000 px; callout pass per `blender-style.json#callouts`.

**Markdown docs** (SPEC.md, README, BUILD.md).
- Key numbers table columns: `Parameter | Value | Unit | Source | Status`. Numbers right-aligned by the renderer;
  in raw Markdown write them plainly.
- Status in backticks: `` `CHECKED` ``. Estimates: `` `EST` `` after the number. Unverified rows: `` `UNVERIFIED` ``
  in the status column, never in prose.
- Units with a space: `0.46 m²`, `1 180 g`, `0.6 N·m`, `2 200 mm`. Dimensionless: no unit. Currency `$1 640`.
- Ids in backticks: `` `WNG-003` ``, `` `E-BMS-01` ``, `` `CL-PROP-HOVER-TW` ``. Files as repo-relative paths.
- One H1 (the subsystem), H2 for the seven SPEC sections in BRIEF order, no H4. Bullets ≤ 1 line.
- A figure caption is `FIG WNG-02 — Spar bond, iso 50 mm` then one sentence at most.

## Do / don't (from the reviewed sites)

| Do | Don't | Seen at |
|---|---|---|
| State release status plainly in one badge ("UNVERIFIED design · not released for flight") | Repeat the caveat in every panel and in caps | VECTOR viewer and handoff: honest status, but "NOT RELEASED" and hash strings repeated until the eye skips them |
| One reconciled count per thing (`212 parts · 7.42 kg`) | 49 / 48 / 51 / 92 / 184 for the same inventory on one page | VECTOR gear study |
| Three view modes and a part panel; the viewer leads the page | Six overlapping side panels (finder, details, display options, provenance, renderer stats) | VECTOR viewer |
| A table with `area · actual state · what that permits` | Ten thousand words of narrative with internal codenames | VECTOR handoff (its "current state" table is the best thing on the page) |
| Prose-free step: picture, numbered actions, parts for this step | A wall of text with the picture at the end | Prusa assembly guides (help.prusa3d.com/guide/…): one photo per step, numbered coloured markers, per-step parts bag |
| Highlight only the new parts; ghost or grey what is already built | Colour every part in every figure | LEGO instructions (lego.com/service/buildinginstructions): new parts in a box, model already built in context |
| Specs as a plain list with units and a "data as of" date | Superlatives without numbers ("strong winds", "engineered to perform") | Joby aircraft page (dual units, dated data) vs Wingcopter 198 (unquantified claims) |
| 14-step categorical palette in a fixed order; status colours separate from data colours | Status colours reused for chart series | IBM Carbon data-viz colour guidance (carbondesignsystem.com/data-visualization/color-palettes) |
| Hairline borders, tonal steps for depth, mono for values | Drop shadows on cards, gradient text, glass panels | Linear docs, Vercel Geist, Stripe docs |
| Keep the previous review's good habits: source line under every figure, `EST` mark, verdict first | Re-invent a second accent or a second type family | this repo's `DESIGN.md` / `VTOL-Review.html` |

## Contrast and themes

Every status text on its wash is ≥ 5.1:1 (light) and ≥ 6.3:1 (dark); body text ≥ 7:1; meta text ≥ 4.5:1
(checked 2026-11-09 with a WCAG script). Theme: `<html data-theme="dark">` or `light`; with no attribute the OS
preference applies. Print always renders light on white.

## Checking a page against the system

1. Open it next to `components.html` in both themes. Same badge, chip, table, callout?
2. Count the colours on screen that are not neutral: each must be accent, highlight, a status or a subsystem.
3. Read every number: unit? source? status word?
4. Delete one sentence per section; if nothing was lost, delete another.
5. Phone width: nothing scrolls sideways except a wide table.
