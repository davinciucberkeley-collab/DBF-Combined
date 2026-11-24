# Explorer UI review, 2026-11-16

Nothing in `redesign/site/` outside this folder was changed. Files: `SURVEY.md`, `CRITIQUE.md`, `concept-1/2/3.html` with `-desktop.png`, `-mobile.png` (and `-dark` / `-light` variants), `shots/` (current site at 1440 and 390 px). `shot.sh` and `mwrap.html` are the helpers used to take the screenshots (headless Chrome).

## Survey
42 sites opened and read (41 as text, 10 also rendered and looked at); about 17 more attempts failed and are not counted. Details and the pattern taken from each are in `SURVEY.md`. Caveat: text fetch cannot show pixels, so visual judgements rest on the 10 rendered sites.

## Top 8 problems (full list in CRITIQUE.md)
1. Phone navigation is broken: nine tabs in a 99 px scrolling box, one tab visible, no menu (`shots/now-mobile-trio.png`).
2. Nine equal tabs, no "start here" and no grouping.
3. Stale content under a "Concept A" header: K09-L headings still present, and the BOM total ($1,779.47) disagrees with the $1,499 in CLAUDE.md.
4. Slogan headings that restate the data ("Every part has one owner and one mass") are the main "generated" tell.
5. About 117 status pills and ten identical status cards: colour and boxes with no hierarchy; no legend.
6. Twenty font sizes on one page, mono used for whole sentences.
7. Tables and sources: no locked first column on mobile, sources as tiny underlined filenames, empty "Allocation" column in the mass table.
8. Performance: `data/assembly.glb.js` is 9.9 MB base64 (a second 9.9 MB copy sits next to it) for a 7.4 MB GLB; no compression or lazy load. (`index.html` itself is 286 kB.)

## Three concepts (each shows Aircraft, Status, BOM with real content)

| | Desktop | Mobile | Alternate theme |
|---|---|---|---|
| 1 Drawing sheet | `concept-1-desktop.png` | `concept-1-mobile.png` | `concept-1-dark.png` |
| 2 Calm docs | `concept-2-desktop.png` | `concept-2-mobile.png` | `concept-2-dark.png` |
| 3 Mission control | `concept-3-desktop.png` | `concept-3-mobile.png` | `concept-3-light.png` |

**1. Drawing sheet.** The site is a set of numbered sheets with a title block (project, decision, revision, data build time) across the top, and the nine pages are "Sheets 1 to 9". Newsreader for text, IBM Plex Mono for numbers; paper and ink in light, blueprint in dark; one revision orange. No cards, no rounded corners: hairline rules, ledgers, ruled tables, figure captions ("Fig. 1") and margin numbers. It fits what the team actually is, an engineering record with sources, and it is the least like a template. Cost: the most distinctive, so the most opinionated; long reading in a serif needs care for the dense tables.

**2. Calm docs.** The Stripe / Tailwind / PX4 pattern: a left tree in three groups (Overview, The case, The plan), one 760 px article column, a right "On this page" rail, Public Sans and DM Mono, white and slate with one blue. Status is the only colour, shown as small tags with a legend. The safest choice and the best for a visitor who arrives cold; the K09-L material moves to an "Archive" section. It looks professional but less distinctive than 1.

**3. Mission control.** A dense, dark-first instrument layout: top status bar with live gate readouts (mass, CG, claims, build time), a left rail with F-key shortcuts, panels with small caps headers, tabular mono numbers, LED-style states. IBM Plex Sans Condensed and JetBrains Mono. Best for the team's own daily use and for showing the 3-D model beside the parts list and inspector, weakest for prose and for a first-time reader; the light theme (`concept-3-light.png`) is a plain grey and white.

## Recommendation
Build **concept 2's structure with concept 1's type and rules**: the docs layout (grouped left tree, 760 px column, right rail) because it solves the navigation, mobile and long-page problems directly, plus Newsreader headings, a single ink-and-orange palette, square corners and ruled tables so it does not look like every docs template. Keep concept 3's top status bar (mass, CG, claims, build time) as a thin strip on the Aircraft page only, and its three-pane layout for the viewer. If the team wants only one concept unchanged, pick 1 for a judged presentation and 2 for daily use.

## What implementing it site-wide involves
- **Files.** `app.html` (page markup: headings, badge classes, status cards, the nav), `site.css` and `app.css` (replace tokens and the badge, card, metric and table rules; the CSS is already token-based, so about 70 % is a token swap), `site.js` (nav: grouped tree, mobile menu, `#page/section` hashes), `make_index.py` unchanged. Copy edits to about 12 headings. Build guide and Proofs pages keep their content and get the new type scale.
- **3-D viewer risk: medium.** `viewer.js` draws into a container and owns its own toolbar and inspector markup; changing the layout around it is safe, restyling its toolbar and inspector means editing the class names it injects (`v-side`, `ds-panel`, buttons) and checking resize handling. Performance work (load the GLB as a binary with compression, lazy) touches only the loader, but needs a decision on `file://` use.
- **Proofs graph risk: low to medium.** It is an embedded sub-page (`proofs/`, `make_proof_embed.py`) with its own styles; restyle only the frame and give it the same tokens in a second pass.
- **Content to resolve first (not design work).** Mark K09-L pages as archived; reconcile the BOM total with the project documents.
- **Effort (estimate).** About 2 to 3 working days for one person: day 1 tokens, type, nav and mobile menu; day 2 page-by-page markup (Aircraft, Status, BOM, Team, Decision) and the status vocabulary legend; day 3 viewer chrome, proofs frame, accessibility and contrast pass, screenshots at 1440 and 390 px. Another half-day for GLB compression. The other agent editing `app.html` should finish before any of this starts.
