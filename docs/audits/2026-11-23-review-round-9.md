# Review round 9: T-053 Explorer design audit (HEAD cffd0174), 2026-11-23

Verdict: PASS WITH FIXES (two minor, non-blocking).

## Checks
- Diff (git show cffd0174): hard-coded values replaced by existing tokens (`border-radius:2px` -> `var(--radius-xs)`, `font-size:12px` -> `var(--text-xs)`); grid, gaps, widths untouched. Layout unchanged. Cache key bumped app.html:8 and index.html. PASS.
- Contrast recomputed from hex (site.css / explorer.css). Light: fg-3 on bg/panel/panel-2 5.63/6.09/5.24; highlight #A84808 on bg/panel/panel-2 5.17/5.59/4.81, on --highlight-wash #FBE9DC 4.95, white on highlight 5.84; fg, fg-2, accent all >= 6.09. Dark: fg-3 6.64/6.19/5.56; highlight #FF8A3D 7.74/7.21/6.48; accent 8.91/8.31/7.47. All match the audit table and the conductor decision. Old bug reproduced: dark accent on white = 2.04, so the `.shot.drw > a` fix is correct. PASS.
- Served redesign/site on 127.0.0.1:8769 (stopped after): app.html, index.html, app.css, site.css, explorer.css all 200; app.css has `.shot.drw > a` (1); index.html has the token BOM style and `app.css?v=20261123a` (1 each); app.html has 37 "V:" title attributes. PASS.
- Fixed widths: app.css has no width >= 100 px literals outside `.drw-gallery .shot` (flex 230 px, inside an overflow-x:auto container); BOM bars use 120px 1fr 90px (fixed part 230 px, 1fr shrinks, max-width:760px is a cap). Nothing fixed above 375 px. PASS. (Rendered scrollWidth was not re-measured; relied on the audit's browser measurement.)
- Badges: BOM price badges carry visible text V/U/EST plus a title; no colour-only status. PASS.
- Generators: title attribute added in sync_bom_a.py (FLAGTITLE, line 29/44), not only in output. Reran `python -I redesign/site/sync_bom_a.py` (total $1,939.17) and `make_index.py`; `git status --short` stayed empty. PASS.

## Findings
1. LOW, app.html:2738 (and index.html copy): `--radius-xs` is `0` in explorer.css:12 (3px only in site.css:56), so the BOM bar corners change from 2 px to square. This is the intended Explorer look, but the "no visual change" claim in the audit (section 2) is true only for the font-size edit. Fix: state in the audit that bars are now square under explorer.css.
2. LOW, audit section 2/6: the BOM style block is hand-authored in app.html (no generator emits it; make_index.py copies it to index.html). The audit's "generators fixed" wording applies only to the badge titles. Fix: say so in the audit.

Not blocking: `.v-fastbtn` white-on-highlight 5.84 (light) is fine; dark `--on` pairs unchanged.
