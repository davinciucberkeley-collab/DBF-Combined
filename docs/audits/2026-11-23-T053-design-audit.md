# T-053 Explorer design audit (2026-11-23)

Category: illustrative (UI/design check; no engineering analysis). Scope: `redesign/site` markup and styles changed since a93f14da
(app.html Status / Decision / Aircraft / Subsystems / Proof / BOM / Build guide / drawing gallery). `site.css`, `app.css`, `explorer.css` and
`proofs/embed.css` were NOT modified since that commit; the changed markup is in app.html / index.html and its generators
(`sync_status_a.py`, `sync_bom_a.py`, `make_drawing_gallery.py`, `make_build_guide.py`). Generated data files excluded.

Acceptance test (restated): issues fixed; overlays use design-system tokens. Result: PASS for the checks below; remaining items in section 7.

## 1. Design tokens
Defined in `site.css` (type scale `--text-*`, spacing `--space-1..8`, radii `--radius-xs..lg`, colours, `--st-*` status triplets, dark set under
`prefers-color-scheme` and `[data-theme=dark]`), overridden by `explorer.css` (warm paper palette: `--bg` #F4F1E8 light, #12161C dark; `--accent` #1F5A82 / #86BCE3).
Runtime values were read from the live page for the contrast table.

## 2. Hard-coded values in changed markup / styles (found, action)
| Where | Value | Action |
|---|---|---|
| app.html:2738 `.bom-bar i` | `border-radius:2px` | replaced by `var(--radius-xs)` (token) |
| app.html:2739 `#bom-table .pid` | `font-size:12px` | replaced by `var(--text-xs)` (12px, same size) |
| app.css:351 `.shot.drw a` | `background:#fff` on every link in the card | kept as white paper (sheets are white; no theme-independent token) but narrowed to the thumbnail link (`.shot.drw > a`); see finding 1 |
| app.html:2737 `.bom-bars` / `.bom-bar` | gaps 6px / 10px, columns 120px 1fr 90px, bar height 10px, max-width 760px | no token for 6 / 10 px; left (no layout change) |
| app.html:384-388 `.bstage` pills | 12px, padding 5px 10px, radius 999px | existed before a93f14da; left |
| app.html GA sheet `<style>` (made by showcase/concept-a/make_sheet_a.py) | px font sizes in SVG user units; hex only as `var(--x, #hex)` fallbacks | SVG units scale with the figure; fallbacks never apply; left |
| app.html `style="--c:#d03b3b"`, `#9a9993` (FEA key chips) | must match the colours in the FEA images | pre-existing data colours; left |
| app.html `--v:NN%` inline custom properties | data values, not styling | none |

No new tokens were added. Overlay / badge / tag styles added since a93f14da: none (badges reuse `ds-badge` + `data-status`).

## 3. Light / dark, phone width
Method: Browser pane emulating 375x812, `data-theme` set to light and dark, pages #app #aircraft #decision #proof #structures #subsystems #team #build #status #bom #docs.
- `document.documentElement.scrollWidth` = 375 on all 22 page/theme combinations (one 385 reading during smooth scroll was transient; 375 on re-test).
- No element past 375 px outside an `overflow:auto` container (tables sit in `.scroll`; the drawing gallery scrolls horizontally by design, cards are 230 px).
- Fixed widths > 375 px in changed sections: none outside scroll containers (`.bom-bars max-width:760px` is a maximum; the `1fr` column shrinks).
- Computed contrast of every visible text node (4.5:1 limit) on the pages above, both themes: 0 failures after the fix (1 failure class before, finding 1).

## 4. Findings and fixes
| # | Finding | Fix (file:line) |
|---|---|---|
| 1 | Drawing gallery: `.shot.drw a` (specificity 0,2,1) beat `.shot figcaption a {background:none}` (0,1,2), so the caption "PDF" link got a white background; accent text on white = 2.04:1 in dark theme (58 links on #build) | app.css:351 selector now `.shot.drw > a`; cache key `app.css?v=20261123a` (app.html:8; index.html regenerated with make_index.py) |
| 2 | BOM style block used px literals where tokens exist | app.html:2738, 2739 |
| 3 | BOM price badges show only "V", "U", "EST"; the meaning was only in the Status key linked from the header | `title` text added in the generator (sync_bom_a.py:29, :44); BOM section regenerated with `python -I redesign/site/sync_bom_a.py` (total $1,939.17, unchanged) |

## 5. Accessibility basics
- Status tags: all new `ds-badge` elements carry text (UNVERIFIED, V, U, EST, FAIL / OPEN, MODELLED, PROPOSED, phase words); none rely on colour alone. The dot is decorative (`::before`).
- Images: 79 `<img>` in app.html, 0 without `alt`; the only empty alt is the lightbox image (`#lb-img`), filled per sheet by script. Drawing thumbnails: "Engineering drawing <id>". The GA sheet SVG has `role="img"` and an `aria-label`.
- Contrast of token pairs used for text (WCAG 2.x relative luminance from the runtime hex values; 4.5:1 for normal text):

| Foreground | Background | Light | Dark |
|---|---|---|---|
| --fg | --bg | 14.11 | 14.41 |
| --fg | --panel | 15.25 | 13.43 |
| --fg | --panel-2 | 13.13 | 12.07 |
| --fg-2 | --bg | 8.18 | 9.52 |
| --fg-2 | --panel | 8.85 | 8.87 |
| --fg-2 | --panel-2 | 7.61 | 7.97 |
| --fg-3 | --bg | 5.63 | 6.64 |
| --fg-3 | --panel | 6.09 | 6.19 |
| --fg-3 | --panel-2 | 5.24 | 5.56 |
| --accent | --bg | 6.54 | 8.91 |
| --accent | --panel | 7.07 | 8.31 |
| --accent | --panel-2 | 6.09 | 7.47 |
| --highlight | --bg | 4.07 FAIL | 7.74 |
| --highlight | --panel | 4.40 FAIL | 7.21 |
| --highlight | --panel-2 | 3.79 FAIL | 6.48 |
| --on-accent | --accent | 7.39 | 8.94 |
| --highlight | --highlight-wash | 3.90 FAIL | 6.37 |
| --accent | --accent-wash | 6.17 | 7.22 |
| --st-unverified | its wash | 5.40 | 8.16 |
| --st-proposed | its wash | 6.62 | 7.55 |
| --st-modelled | its wash | 6.20 | 6.90 |
| --st-checked | its wash | 5.13 | 7.21 |
| --st-verified | its wash | 5.48 | 7.76 |
| --st-fail | its wash | 5.40 | 6.38 |

## 6. Verification (run 2026-11-23)
`python -I -m http.server 8768 --bind 127.0.0.1` (stopped afterwards). curl of the served files: app.css contains `.shot.drw > a`; index.html contains
the token-based BOM style, the badge titles and `app.css?v=20261123a` (count 1 each). In-browser: scrollWidth 375 on all 22 combinations; computed text
contrast failures 0 on 11 pages x 2 themes. Light-theme proof-page buttons read 1.83:1 once, directly after the theme switch (colour transition); not reproducible after settling.

## 7. What is left
- Light-theme `--highlight` #C2540A is below 4.5:1 as text on panel / bg (3.79 to 4.40). Used as text only by `.v-hwhead` (app.css:283, 12 px viewer harness header, not changed by this program) and as a fill elsewhere (`.v-fastbtn`, white text, about 4.5). Fixing needs a darker highlight token for text (token decision, site.css:72); not done.
- Inline FEA chip colours and GA-sheet px sizes stay literal by design (section 2).
- Gap values 6 px / 10 px in the BOM bars have no token.
- build-manual.html (stand-alone page with its own styles) is outside the Explorer scope of this task; not audited.
- Nothing committed or pushed.

## Conductor decision (2026-11-23)
Light-theme `--highlight` changed #C2540A -> #A84808 (`redesign/site/site.css` l.72 and l.174). WCAG contrast as text: 5.17 on #F4F1E8, 5.59 on #FBFAF6, 4.81 on #EDE9DD (worst panel-2), 4.95 on the wash #FBE9DC, 5.84 white text on it; all >= 4.5. Dark theme unchanged. The open item above is closed.
