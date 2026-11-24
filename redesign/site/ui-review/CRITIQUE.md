# Critique of the Explorer (index.html as served 2026-11-16, concept A build)

Evidence: screenshots in `shots/` (`now-*-1440.png`, `now-*-390.png`, `now-mobile-trio.png`), measurements taken in the browser at 390 px and from `site.css` / `app.css` / `app.html`. The page was being edited while I looked; numbers are from 02:00 to 02:10 on 2026-11-16. Headless screenshots caught the 3-D viewer still on "Loading model" after 10 s of virtual time, so I did not judge the viewer's looks, only its chrome.

Ordered by impact.

## 1. Mobile navigation is unusable (blocker)
At 390 px the nine tabs sit in a box 99 px wide that scrolls sideways (`#nav` scrollWidth 608, clientWidth 99). You see "Aircraft" and half of "Decision". There is no menu button and no hint that more exists. Wide tables (status issues, BOM) overflow their wrappers with no locked first column (NN/g, survey #40). Fix: below 720 px show the current page name plus a "Pages" button that opens a full-width list; lock the first column of tables.
Evidence: `shots/now-mobile-trio.png`.

## 2. Nine peer tabs with no hierarchy
Aircraft, Decision, Team, Subsystems, Build guide, Proofs, Status, BOM, Docs are all the same weight. A first-time reader (a judge, a sponsor) has no "start here". Decision and Proofs and Docs answer "why do you believe it"; Build guide and BOM answer "what do we do"; Status and Team answer "where are we". Group them in three (Aircraft, Case, Plan, or similar) and keep the 3-D viewer as the front door. The survey sites that cope with this (Supabase, Stripe, MDN) put 4 to 6 top items over a contextual left tree.

## 3. Stale content on a page that says "Concept A"
The first `<h1>` in the document is still "K09-L: a 2.6 kg quad tailsitter ... built for $2,000" and further `<h1>`s say "Build K09-L" and "K09-L build guide, with a clip for every stage". The header says Concept A, the Status page says "Designed and checked ... Nothing bought", Decision still argues for K09-L. This is the most credibility-damaging thing on the site and no restyle fixes it: a "Superseded" banner and a visibly separate Archive section are needed. Also the BOM total ($1,779.47 incl. reserve, from the page) differs from the CLAUDE.md figure ($1,499, margin +$501); one of them is stale and the site should say which one is the current.

## 4. Reads as generated: heading copy
Headings are slogans or sentences that restate the data under them: "Every part has one owner and one mass", "One role per engineer, ten groups, 31 delivered", "Designed and checked on paper, in SITL and the 3-D gates. Nothing bought, built or flown.", "Everything to buy, priced, against the $2,000 limit", "One card each, skeptic-corrected numbers. Every correction went the same way: heavier, more power, less reserve." Rhetorical "not X but Y" rhythm, parallel triplets, and every H1 at the same 32 px bold. Real engineering sites title pages with the noun ("Bill of materials", "Mass budget") and put the finding in a one-line summary in a different weight (Joby, DJI, PX4). Fix: noun titles, one "Summary" line with the three numbers that matter, then the page.

## 5. Reads as generated: uniform boxes and badges
- `ds-badge` appears about 117 times (106 plain, 10 with a dot, plus chips). Every row of the team page carries a coloured pill (PROPOSED / MODELLED / CHECKED / UNVERIFIED), so the pills stop meaning anything. Most rows are the same value; show exceptions, not the norm. Define the vocabulary once in a legend (GOV.UK and Carbon do this).
- Status page: ten identical rounded cards with a monospace number, title, small body, and a bold "DONE" floating at a different height in each. Ten items in a fixed sequence is a list or timeline, not a card grid. The progress bar above already carries the same information.
- Team page: three-column grid of boxed groups with header strips; each role row has an underlined link title, a pill, and a grey description. Heavy. A table with the owner in column 1 would be denser and sortable.
- Radius and shadow are uniform (`--radius-md` used 32 times, `--radius-sm` 29); every container is a rounded, bordered, white card on a grey ground. No hierarchy between page, section and item.

## 6. Too many type sizes, and mono used as decoration
Computed font sizes on one page: 9, 10, 10.2, 11, 11.5, 11.9, 12, 12.32, 12.5, 13, 13.2, 14, 15, 16, 17, 18, 22, 24, 32, 70 px (20 values). The 70 px and fractional sizes (12.32, 13.2, 11.9) come from `em` stacking. About 100 text nodes are under 11 px. IBM Plex Mono is used for the eyebrow, the metric sub-lines, the status words and table headings, so a third of the text is mono, including multi-line explanatory sentences (BOM metric 4 is a 6-line mono paragraph). Fix: a 6-step scale (12, 14, 16, 20, 28, 40), mono only for identifiers, part numbers and values.

## 7. Information design of the key pages
- **Aircraft.** The three-pane layout is right (tree / viewer / inspector, the Onshape and Sketchfab pattern). Problems: toolbar buttons use three different styles (segmented controls with tiny type, ghost buttons, one filled "Show full aircraft"); the instructions are a paragraph in the inspector instead of a persistent hint bar; the inspector is a tall column that mixes the manual, key numbers, a mass table whose "Allocation" column is all dashes, and the keyboard map at the same level. The mass table's empty column should go.
- **BOM.** The best page. The metric row is overloaded: card 4 holds a six-line mono paragraph with two alternative totals; split it into a number and a footnote. The "Price" column holds a badge that is just V / U / EST; use a one-letter text with a legend. "Order 1" wraps onto two lines in a cell.
- **Status.** Prose intro is set in a 520 px column in the middle of a 1170 px page, leaving a dead right half. Sources are small underlined filenames ("CLAUDE.md C8; HARNESS-ENCLOSED.md s5"): they should be real references (numbered, hover shows path and commit), as in Distill and OWID.

## 8. Accessibility
- Focus: a visible 2-3 px box-shadow ring exists (`:focus-visible`), good; the outline itself is `none`, which disappears in Windows forced-colours mode. Add `outline: 2px solid transparent` as well.
- No skip link, and `<h1>` count of 4 in the document (one per view; the hidden views should not be in the accessibility tree).
- About 7 links/buttons under 32 px tall at 390 px (target size, WCAG 2.5.8 needs 24 px minimum, 44 px is the practical target).
- One image without `alt`; viewer content is a canvas, so the part tree is the accessible route; make sure it is reachable by keyboard and announce "selected part" with a live region.
- Dark mode exists (`prefers-color-scheme` plus a toggle). The toggle and the OS setting can disagree; the header shows only the moon icon. Contrast of grey-on-grey labels in the viewer toolbar (disabled-looking "Inside & wiring", "Structure") looks under 3:1 in the 1440 shot. Measure with a tool before the change.
- `prefers-reduced-motion` is handled.

## 9. Performance
- `index.html` is 286 kB of inline HTML, mostly the Build guide, BOM and Team text. Acceptable for a docs page, but every tab is parsed at once.
- `data/assembly.glb.js` is 9.9 MB (base64 of a 7.4 MB GLB at `assets/concept-a.glb`), and `assembly.glb.part1.js` is a second 9.9 MB copy. Base64 adds 33 % and blocks compression-friendly caching. Load the `.glb` binary directly with `fetch` and `GLTFLoader`, with a progress bar, Draco or meshopt compression (typically 3 to 10x smaller), and defer it until the Aircraft view is shown. If the site must work from `file://` this is the reason for base64; a "download offline copy" link could cover that case separately.
- `viewer.js` is 53 kB and `viewer-data.js` 196 kB: fine.

## 10. Navigation inside long pages
Build guide (12 stages) has a TOC; Decision, Subsystems and Docs have none, and breadcrumbs only show the tab. Add a right "On this page" rail (Stripe, MDN, Cloudflare) and deep-linkable headings; use `#tab/section` hashes so a link to a claim or part works.

## 11. Smaller things
- The "PROPOSED" badge top right is a project status, not a page control; it competes with the theme toggle. Move it to the footer or a Status line.
- 17 em dashes and many "X: Y" sentence-case slogans in the page copy; where a number is available, give the number.
- Colours: blue for primary actions, teal for "done", amber, red, purple for "MODELLED". Five hues plus the 11 part-group colours in the tree. Reserve colour for status; colour part groups only in the viewer.
- Link style: underlined titles inside cards (team page) and underlined filenames inside small mono text: two link looks.

## What is good and should survive
Three-pane Aircraft layout and keyboard shortcuts; the BOM metric row and bar chart idea; sources shown beside claims; dark mode; reduced-motion support; the honest vocabulary (UNVERIFIED, EST) and "nothing bought" statement; token-based CSS (`--radius-*`, `--focus-ring`, `--font-*`), which makes a restyle mostly a token swap.
