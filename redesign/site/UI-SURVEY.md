# UI survey for the K09-L Explorer

We reviewed 108 real pages (fetched 2026-11-13) to decide how the K09-L Explorer (`redesign/site/`) should look and
behave. The goal is a reference that engineers come back to: easy to scan and easy to cite, with no dashboard or
template look. Below are the sites, the rules we took from them, and what changed in the Explorer as a result.

How the pages were read: each page was fetched with WebFetch. Font names come from the page's own CSS, read with curl,
or from the page text. Where a page could not be fetched, the row says so and names the substitute that was read. No
page is described from memory.

## 1. Sites reviewed

### A. Engineering reports, aerospace, OEM and competition sites

| # | Site | URL | Checked | Pattern worth taking |
|---|---|---|---|---|
| 1 | NASA NTRS record | https://ntrs.nasa.gov/citations/19930090976 | 2026-11-13 | Metadata as stacked label/value pairs (Document ID, Report Number, Publication Date, Distribution). "Related Records" shows a superseded report as a relation ("Superseded By"). Roboto. |
| 2 | nasa.gov reference hub | https://www.nasa.gov/reference/ | 2026-11-13 | Footer stamp: "Page Last Updated" with the page editor and the responsible official named. |
| 3 | ESA Space Engineering & Technology | https://www.esa.int/Enabling_Support/Space_Engineering_Technology | 2026-11-13 | Breadcrumb with three tabs. Cards carry a bracketed category tag and an uppercase date. NotesEsa + Inter. |
| 4 | JPL Perseverance | https://www.jpl.nasa.gov/missions/mars-2020-perseverance-rover | 2026-11-13 | Fact block (Launch, Type, Target, Status "Current"). Live counter with a unit on every figure (Yrs/Mos/Days). |
| 5 | NASA Science Perseverance | https://science.nasa.gov/mission/mars-2020-perseverance/ | 2026-11-13 | Status word "Active Mission" above label/value rows. Dual units "28.10 miles (45.22 kilometers)". Downloads show format and size; every image has its own credit line. Inter + DM Mono for data. |
| 6 | Joby Aviation | https://www.jobyaviation.com/ | 2026-11-13 | Image-led and low in density; one spec strip. A counter-example for a reference site. |
| 7 | BETA Technologies | https://www.beta.team/ (the /aircraft/ page returned 404) | 2026-11-13 | Value plus short unit, label underneath ("336 nm / Demonstrated range"). Footnote marker on claims; "—" for unknowns. Titillium Web + JetBrains Mono. |
| 8 | Wingcopter 198 | https://wingcopter.com/wingcopter-198 | 2026-11-13 | Plain "Label: value unit" spec lines, but no test conditions or sources. Counter-example: a number with no source. |
| 9 | Airbus commercial aircraft | https://www.airbus.com/en/products-services/commercial-aircraft | 2026-11-13 | Key figures row: large value over a caption. Inter. |
| 10 | Honeywell Aerospace (IMU category) | https://aerospace.honeywell.com, which redirected to the honeywellaerospace.com IMU category page | 2026-11-13 | Checkbox facets beside the results, plus "Related categories". |
| 11 | EASA Easy Access Rules (FAA design approvals returned 403) | https://www.easa.europa.eu/en/document-library/easy-access-rules | 2026-11-13 | "Displaying 1 - 12 of 52" count. Revision level and available formats on a single line. |
| 12 | AIAA Design/Build/Fly | https://aiaa.org/get-involved/university-students/dbf/ | 2026-11-13 | Status written into the milestone title ("WINDOW OPEN / CLOSED"); dates include time and time zone. |
| 13 | FSAE Online | https://www.fsaeonline.com/ | 2026-11-13 | Three verb headings, each over a plain link list. |
| 14 | Formula Student Germany | https://www.formulastudent.de/ | 2026-11-13 | One page per year, newest first; old years collapsed under one parent. .ics calendar feed. |
| 15 | Cornell CUAir | https://cuair.org/ | 2026-11-13 | Video hero; specs on separate pages. Low density, so a counter-example. |
| 16 | MIT DBF | https://web.mit.edu/dbf/www/index.html | 2026-11-13 | Single page with four in-page anchors and "Back to top"; old seasons kept as archives. |
| 17 | Michigan MACH | https://www.mach.engin.umich.edu/home | 2026-11-13 | Squarespace template with a hero and three feature blocks: the uniform template look to avoid. |
| 18 | ArduPilot QuadPlane | https://ardupilot.org/plane/docs/quadplane-support.html | 2026-11-13 | Left tree, breadcrumbs plus "Edit on GitHub", previous/next pager. Lato (Read the Docs theme). |
| 19 | ArduPilot tailsitter guide | https://ardupilot.org/plane/docs/guide-tailsitter.html | 2026-11-13 | ¶ permalink on every heading. Parameter names link to their entry in the reference. Note/Tip/Caution admonitions. |
| 20 | PX4 tailsitter | https://docs.px4.io/main/en/frames_vtol/tailsitter.html | 2026-11-13 | Version selector ("v1.17 (stable)"), left tree plus right "On this page", INFO/TIP callouts. Inter (VitePress). |
| 21 | PX4 Pixhawk 6C | https://docs.px4.io/main/en/flight_controller/pixhawk6c.html | 2026-11-13 | Specs grouped by H3, but unit spacing is inconsistent ("59.3g" vs "84.8 * 44 mm"). Counter-example for units. |
| 22 | iFixit guide (Prusa help served only its shell) | https://www.ifixit.com/Guide/MacBook+Air+13-Inch+Early+2015+Battery+Replacement/41323 | 2026-11-13 | "What you need" before step 1; numbered steps, each with a main image plus thumbnails. |
| 23 | Adafruit Learn pinouts | https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/pinouts | 2026-11-13 | Annotated pinout figure with a PDF link; pins grouped under headings. |
| 24 | SparkFun Learn | https://learn.sparkfun.com/tutorials/battery-technologies | 2026-11-13 | Sources line under each image. Units sit in the cells ("12.6V") rather than in the header, which is the thing to avoid. Montserrat, Open Sans, Source Code Pro. |
| 25 | Pololu 2268 (McMaster pages are rendered by JavaScript) | https://www.pololu.com/product/2268 | 2026-11-13 | Tabs with counts ("Specs (13)"). Dual units "3.7 kg-cm (51 oz-in)". Datasheet link shows its file size. |
| 26 | Onshape help: Extrude | https://cad.onshape.com/help/Content/extrude.htm | 2026-11-13 | Title block with "Available in" and "Shortcut"; "Last Updated" at the foot. |
| 27 | Autodesk Fusion help | https://help.autodesk.com/view/fusion360/ENU/ | 2026-11-13 | Help tree by product area; each H2 group is a one-line summary plus a link list. |
| 28 | LCSC C98732 (DigiKey returned 403) | https://www.lcsc.com/product-detail/C98732.html | 2026-11-13 | Two-column attribute table; the datasheet link is named by maker and part number. |

### B. Product and engineering documentation

| # | Site | URL | Checked | Pattern worth taking |
|---|---|---|---|---|
| 29 | Stripe API reference | https://docs.stripe.com/api | 2026-11-13 | The same layout for every parameter (name, type, required, definition). Units and limits stated in the text ("100 cents to charge $1.00"). |
| 30 | Stripe "Accept a payment" | https://docs.stripe.com/payments/accept-a-payment | 2026-11-13 | One URL with variants chosen by query parameter; the base page is an index. |
| 31 | Linear Docs | https://linear.app/docs | 2026-11-13 | 17 H2 groups in lifecycle order, each entry a bare title. Dense, and the headings do the work. |
| 32 | Linear Method | https://linear.app/method | 2026-11-13 | Numbered outline (1.1, 2.1–2.4) with short imperative titles. |
| 33 | Vercel Docs | https://vercel.com/docs | 2026-11-13 | `last_updated` on each page; every code block labelled with its file name; dates first in change lists. |
| 34 | Vercel Geist | https://vercel.com/geist/introduction | 2026-11-13 | One sans family plus one mono family; "materials" bundle radius, fill and stroke. |
| 35 | Tailwind install | https://tailwindcss.com/docs/installation | 2026-11-13 | Steps numbered 01–06, each with one code block labelled by file; version badge in the top bar. |
| 36 | MDN font-variant-numeric | https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric | 2026-11-13 | Baseline status badge with a date. Documents `tabular-nums` and `lining-nums`, which we apply to every number column. |
| 37 | The Rust Book ch. 4.1 | https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html | 2026-11-13 | Captions go under the figure, with separate numbering ("Listing 4-1", "Figure 4-1"). Previous/next links at top and bottom. |
| 38 | Read the Docs | https://docs.readthedocs.io/en/stable/ | 2026-11-13 | Version in the URL path. The sidebar keeps tutorial, how-to and reference apart. `<dl>` lists, not cards. |
| 39 | GitBook docs | https://docs.gitbook.com/ | 2026-11-13 | A table rendered as cards (`data-view="cards"`), with Markdown and llms.txt versions offered. |
| 40 | Docusaurus showcase | https://docusaurus.io/showcase | 2026-11-13 | Live count ("274 sites") above filter chips with AND/OR. |
| 41 | Docusaurus docs | https://docusaurus.io/docs | 2026-11-13 | Right-hand "On this page"; "Last updated on … by …" next to "Edit this page". |
| 42 | Python functools | https://docs.python.org/3/library/functools.html | 2026-11-13 | "Source code: Lib/functools.py" at the top of the page; stacked "Added in / Changed in version" lines; ¶ permalinks. |
| 43 | Kubernetes overview | https://kubernetes.io/docs/concepts/overview/ | 2026-11-13 | Version dropdown, a "(removed)" suffix in the nav, and an action row (Edit / Create issue / Print section). |
| 44 | Effective Go | https://go.dev/doc/effective_go | 2026-11-13 | A note under the H1 saying how current the page is and what it does not cover. |
| 45 | React useState | https://react.dev/reference/react/useState | 2026-11-13 | The same order on every page (Reference, Usage, Troubleshooting). Two typed callouts. Troubleshooting headings are written as the symptom. |
| 46 | SQLite SELECT | https://www.sqlite.org/lang_select.html | 2026-11-13 | Numbered sections (2.5.1) with a contents list at the top; diagrams show or hide on demand. |
| 47 | GitHub Docs | https://docs.github.com/en/get-started | 2026-11-13 | Each article is a linked title plus one summary sentence. |
| 48 | Carbon data table | https://carbondesignsystem.com/components/data-table/usage/ | 2026-11-13 | Row heights of 24/32/40/48/64 px. Sentence-case headers of one or two words. Sort arrows only on hover. |
| 49 | Primer | https://primer.style/ | 2026-11-13 | Size tokens 12/14/16/20/32 px; line length kept to about 80 characters or less. Mona Sans + ui-monospace. |
| 50 | Atlassian typography | https://atlassian.design/foundations/typography | 2026-11-13 | Each size token is a size/line-height pair. Separate tokens for metric numbers. One h1 per page, no skipped heading levels. |
| 51 | GOV.UK Service Manual | https://www.gov.uk/service-manual | 2026-11-13 | Plain, short labels; each item is a bold title plus one line of description. |
| 52 | GOV.UK table component | https://design-system.service.gov.uk/components/table/ | 2026-11-13 | Numeric header and cell classes that right-align; a caption on every table; `scope` on header cells. |
| 53 | Apple HIG typography (read through its JSON data file) | https://developer.apple.com/design/human-interface-guidelines/typography | 2026-11-13 | Default and minimum sizes per platform in one table; avoid the light and thin weights. |
| 54 | Material 3 typography (read through the material-web docs) | https://m3.material.io/styles/typography/overview | 2026-11-13 | Five roles in three sizes each; tokens named by role. |
| 55 | Shopify Polaris | https://polaris.shopify.com/ | 2026-11-13 | Components grouped by purpose, each group opening with one sentence that says what it is for. |

### C. Data tools, editorial and scientific, explorables

| # | Site | URL | Checked | Pattern worth taking |
|---|---|---|---|---|
| 56 | Grafana panels docs | https://grafana.com/docs/grafana/latest/panels-visualizations/ | 2026-11-13 | Sparse hub page: one H1, then link cards with two sentences each. |
| 57 | Grafana Stat panel (play.grafana.org would not load) | https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/stat/ | 2026-11-13 | Option / Description tables. The default for a missing value is stated ("No value" shows "-"). |
| 58 | Vega-Lite examples (Observable returned 429) | https://vega.github.io/vega-lite/examples/ | 2026-11-13 | Nested contents above plain text links, not cards. |
| 59 | Observable Plot (returned 429; Vega project nav read instead) | https://observablehq.com/plot/ | 2026-11-13 | A secondary row for sibling projects above the main nav. |
| 60 | GitHub repo view, ArduPilot | https://github.com/ArduPilot/ardupilot | 2026-11-13 | Exact counts with thousands separators ("75,027 commits"). The file table has three columns. |
| 61 | GitHub PR list, PX4 | https://github.com/PX4/PX4-Autopilot/pulls | 2026-11-13 | Namespaced labels (`kind:` `scope:` `status:`), counts on tabs, one meta line per row, and a density toggle. |
| 62 | Awwwards (Figma community returned 403) | https://www.awwwards.com/websites/ | 2026-11-13 | Faceted filters with an active-filter count; each badge code is spelled out ("SOTD / Site Of The Day"). |
| 63 | Distill: Momentum | https://distill.pub/2017/momentum/ | 2026-11-13 | Live parameter values under the title; references show the DOI and [PDF] links. |
| 64 | Distill: Gaussian processes (Circuits was over 10 MB) | https://distill.pub/2019/visual-exploration-gaussian-processes/ | 2026-11-13 | Byline block (Authors / Affiliations / Published / DOI); "Updates and Corrections" linked to GitHub issues. |
| 65 | Our World in Data: CO₂ | https://ourworldindata.org/co2-emissions | 2026-11-13 | Each section runs intro, then chart, then interpretation. Links open a chart already filtered. "Cite this work" at the end. |
| 66 | OWID Grapher | https://ourworldindata.org/grapher/co2-emissions-per-capita | 2026-11-13 | `<dl>` block: Source, **Unit**, Date range, Last updated, Next update. The conversion factor is stated. |
| 67 | Bret Victor: Ladder of Abstraction | https://worrydream.com/LadderOfAbstraction/ | 2026-11-13 | Pseudocode under each figure updates with the current parameters; interactions are cued by bold verbs ("Drag"). |
| 68 | Ciechanowski: Airfoil | https://ciechanow.ski/airfoil/ | 2026-11-13 | Colour words in the text match marks in the figure. Inline links set a figure to a preset state. |
| 69 | Ciechanowski: Gears | https://ciechanow.ski/gears/ | 2026-11-13 | One slider per figure plus a play/pause button; anchor icons on headings. |
| 70 | explorabl.es | https://explorabl.es/ | 2026-11-13 | Browse by subject or open "all of it" on one page. |
| 71 | ncase.me (Trust loads only through JavaScript) | https://ncase.me/ | 2026-11-13 | Each project is one "title – blurb" line. |
| 72 | The Pudding (NYT blocked) | https://pudding.cool/ | 2026-11-13 | Issue number plus month on each story; an "Updating" filter. |
| 73 | Datawrapper blog | https://www.datawrapper.de/blog/ | 2026-11-13 | Date and read time on each card; recurring series named and linked to an "All …" page. |
| 74 | 538 (Economist, FT blocked) | https://fivethirtyeight.com/ (redirected to abcnews.com/538) | 2026-11-13 | News feed with relative timestamps; nothing usable for a reference site. |
| 75 | arXiv abstract | https://arxiv.org/abs/1706.03762 | 2026-11-13 | Version history, one line per version with UTC time and size. "Cite as" with the version-specific id. |
| 76 | Nature: AlphaFold | https://www.nature.com/articles/s41586-021-03819-2 | 2026-11-13 | Caption starts with a bold "Fig. N:", bold panel letters, and n= stated. Separate data and code availability sections with versions. |
| 77 | Tufte CSS | https://edwardtufte.github.io/tufte-css/ | 2026-11-13 | Sidenotes collapse behind a checkbox on mobile. Text stays greyscale; colour is kept for figures. ETBook + Gill Sans. |
| 78 | Practical Typography | https://practicaltypography.com/ | 2026-11-13 | Body text 15–25 px, line height 1.2–1.45, lines of 45–90 characters. |
| 79 | Datadog widgets docs | https://docs.datadoghq.com/dashboards/widgets/ | 2026-11-13 | Breadcrumb; UI labels in bold inside numbered steps. |
| 80 | Weights & Biases | https://wandb.ai/site | 2026-11-13 | Menu entries are a bold name plus a one-line descriptor. |
| 81 | UIUC airfoil database (airfoiltools refused the connection) | https://m-selig.ae.illinois.edu/ads/coord_database.html | 2026-11-13 | A–Z anchor bar. One line per entry. The file format is spelled out. |
| 82 | eCalc | https://www.ecalc.ch/ | 2026-11-13 | Tools grouped by vehicle class. Outputs are checked against battery, ESC and motor limits. |
| 83 | UIUC propeller database | https://m-selig.ae.illinois.edu/props/propDB.html | 2026-11-13 | "Last updated … ver 3" plus an md5 for the download. The intro says three volumes while the page lists four, so counts must agree. |

### D. Hardware docs, model viewers, BOMs, build guides, spec sheets

| # | Site | URL | Checked | Pattern worth taking |
|---|---|---|---|---|
| 84 | iFixit: iPhone 13 battery | https://www.ifixit.com/Guide/iPhone+13+Battery+Replacement/145896 | 2026-11-13 | Time Required and Difficulty as labelled fields. "What you need" split into Parts / Tools. "Step N" plus a title, image above the bullets, inline "Caution:". |
| 85 | RepRap wiki: Prusa i3 | https://reprap.org/wiki/Prusa_i3 | 2026-11-13 | Infobox. Units in the row label ("Printing Size (mm)"), "approx." on estimates, conversions in brackets. |
| 86 | Prusa i3 hardware repo | https://github.com/prusa3d/Original-Prusa-i3 | 2026-11-13 | The README is just a link list. The About text still says "MK2": a stale label shows why there must be one source of truth. |
| 87 | Voron | https://www.voron.design/ and https://docs.vorondesign.com/ | 2026-11-13 | Just the Docs theme: collapsible tree, search, Copy button on code. System font stack. |
| 88 | Voron build: gantry squaring | https://docs.vorondesign.com/build/mechanical/v2_gantry_squaring.html | 2026-11-13 | Good/Bad photo pairs; warning, caution and note callouts; targets with units ("110 Hz over a 15 cm span"). |
| 89 | Open Compute Project | https://www.opencompute.org/ | 2026-11-13 | Contributor and Project metadata lines; version in the title ("V0.7.0"). |
| 90 | Seeed wiki: XIAO ESP32S3 | https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/ | 2026-11-13 | Unknown values written "TBD", never left blank. Pin-map table. Right-hand "On this page". |
| 91 | Pololu 2135 | https://www.pololu.com/product/2135 | 2026-11-13 | Status "Active and Preferred" linked to its definition. Unit in the header ("Unit price (US$)"). Verdana. |
| 92 | GetFPV / Rotorama motor page | https://www.getfpv.com/ | 2026-11-13 | Fetch failed (403/404/429 on all four motor stores tried). No observation. |
| 93 | Tyto Robotics articles | https://www.tytorobotics.com/blogs/articles | 2026-11-13 | Single column of articles with a "70 posts" count and topic/sort controls. Roboto. |
| 94 | Tyto Series 1580/1585 (RCbenchmark docs return 404) | https://www.tytorobotics.com/pages/series-1580-1585 | 2026-11-13 | Unit inside the value ("Max thrust: 5 kgf"), but no accuracy figure. |
| 95 | KiCad docs | https://docs.kicad.org/ | 2026-11-13 | One row per manual with a PDF alternative; version in the path. Open Sans + DejaVu Sans Mono. |
| 96 | Sketchfab model page | https://sketchfab.com/3d-models/ (a model page) | 2026-11-13 | Geometry stats beside the viewer ("16.9k triangles · 8.6k vertices"), with licence and date. |
| 97 | model-viewer | https://modelviewer.dev/examples/annotations | 2026-11-13 | HTML hotspots on the model, SVG dimension lines between them; support levels named in a table. |
| 98 | three.js examples | https://threejs.org/examples/ | 2026-11-13 | Left list filtered live as you type, opening each example in a viewer frame. Roboto Mono. |
| 99 | GrabCAD library | https://grabcad.com/library | 2026-11-13 | Fetch failed (403). No observation. |
| 100 | Onshape resource center (Learning Center returned only its title) | https://www.onshape.com/en/resource-center | 2026-11-13 | Only the facet names could be read (Page Type / Category / Feature). |
| 101 | Printables / Thingiverse | https://www.printables.com/ | 2026-11-13 | Fetch failed (403 on all four model sites tried). No observation. |
| 102 | Apple iPhone compare | https://www.apple.com/iphone/compare/ | 2026-11-13 | Rows grouped by category. Dual units, "(typical)" qualifiers, [1] footnotes, "— Not available" for missing features. SF Pro. |
| 103 | DPReview Canon R5 | https://www.dpreview.com/ | 2026-11-13 | Spec groups with "Expand all / Collapse all". A missing feature is written "No", never left blank. |
| 104 | RTINGS WH-1000XM5 | https://www.rtings.com/ | 2026-11-13 | Every result tied to a "Test Bench 1.0.1" version with a changelog. |
| 105 | ServeTheHome (AnandTech and Tom's could not be read) | https://www.servethehome.com/ | 2026-11-13 | A feed of single-column cards; nothing usable for tables. |
| 106 | Notion engineering templates | https://www.notion.com/templates/category/engineering | 2026-11-13 | Breadcrumb; sub-categories show their counts ("Tech Spec (88)"). |
| 107 | Engineering ToolBox: air density | https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html | 2026-11-13 | Units in the column headers. SI and Imperial tables side by side. Each equation followed by a "where" list with units. |
| 108 | Falcon 9 (spacex.com is a JavaScript shell; Wikipedia read instead) | https://en.wikipedia.org/wiki/Falcon_9 | 2026-11-13 | Stage blocks laid out the same way so rows can be compared; a [n] citation right after each value. SpaceX itself uses D-DIN. |

Not usable: MatWeb, Rocket Lab and Blue Origin refused the fetcher (403/429), and their substitutes did too. They are
left out of the count.

## 2. What the survey says

1. **The best references are documents, not dashboards.** Python, SQLite, Rust Book, ArduPilot, PX4, Stripe, OWID and
   Nature all use numbered or anchored sections, permalinks on headings, captions under figures, and a fixed page template.
   None of them puts every block in a rounded, shadowed card.
2. **Navigation has three layers:** a persistent top-level bar, a contents list for the page ("On this page", PX4,
   Docusaurus, Seeed), and a ¶/# permalink on every heading (ArduPilot, Python, Ciechanowski).
3. **Each number has a unit, a source and a status, in a fixed place.** The unit goes in the header or straight after
   the value (Engineering ToolBox, Pololu, Apple). The source follows the value ([1] on Wikipedia) or sits in a fixed
   metadata block (OWID, arXiv, NTRS). An unknown is an explicit "—" or "TBD" (BETA, Seeed, Apple).
4. **Status is a defined word.** Examples: Pololu "Active and Preferred", MDN Baseline, AIAA "WINDOW OPEN", Kubernetes
   "(removed)", PX4 `status:` labels. No site in the sample shows status as a coloured dot alone.
5. **Tables right-align numbers and keep headers short** (GOV.UK numeric classes, Carbon sentence-case headers, Atlassian
   metric tokens). None of the aerospace or hardware pages in the sample did this. It is the cheapest gain in clarity.
6. **Type pairings that work:** one text face, one face for titles or numbers, and a mono for code and ids. Examples:
   Inter + DM Mono (NASA Science), Titillium + JetBrains Mono (BETA), Geist + Geist Mono (Vercel). The repo's own
   `docs/reference/REVIEW-STYLE.md` already specifies Barlow Semi Condensed, Source Sans 3 and Red Hat Mono.
7. **The counter-examples share one look:** Joby, CUAir, the Michigan Squarespace site and Wingcopter. Each has a large
   hero, three feature blocks, numbers with no conditions or sources, and low density.

## 3. Rules applied to the K09-L Explorer

1. **A section is a short title, a mono meta line and one verdict sentence.** The title is 2–6 plain words ("Constraints",
   "All 43 concepts"). The meta line gives revision, date or source file. The verdict is the claim, with its numbers.
   No eyebrow above the heading. *(Python, React, OWID)*
2. **Section numbers and permalinks.** Each page's h2 sections are numbered `page.section` (2.3 = Decision → Morphological
   chart), so a reviewer can cite "§2.3". Hovering a title shows a `#` link. *(SQLite, Linear Method, ArduPilot)*
3. **"On this page" on every page with three or more sections.** It sits in a sticky right column on wide screens and is
   a closed list on phones, with the current section marked as you scroll. *(PX4, Docusaurus, Seeed)*
4. **The top bar is solid with a single rule.** The nav works as tabs underlined in the accent colour, with no pills.
   The design status appears once, as "Design PROPOSED". *(PX4, Kubernetes)*
5. **Type pairing from REVIEW-STYLE.md:** Barlow Semi Condensed for titles, nav and table heads; Source Sans 3 at 16 px
   for text; Red Hat Mono only for ids, file paths, claim names and code. *(BETA/NASA mono-for-data, Practical Typography
   body size)*
6. **Quantities use tabular lining figures in the text face.** Mono digits sat too wide in prose and tables, so
   quantities use `font-variant-numeric: tabular-nums lining-nums` in Source Sans 3 instead. *(MDN, GOV.UK, Atlassian
   metric tokens)*
7. **Tables have three rules only:** top, under the head and bottom. Heads are in sentence case, numbers right-aligned,
   and there is no outer box or rounded corner. *(GOV.UK, Carbon, booktabs)*
8. **Repeated items sit on a hairline rule, not in a card.** This covers roles, subsystems, phases, constraints,
   shortlisted concepts and simulation cards: a 1 px top rule and white space, with no fill, shadow or radius. A chosen
   item gets a 2 px accent rule. *(Linear docs, Read the Docs `<dl>`, Tufte)*
9. **Status is one outlined mono word with no dot or wash:** PROPOSED, MODELLED, CHECKED, VERIFIED, UNVERIFIED, FAIL.
   Places that used to show a coloured dot alone (key-number tiles) now show the word. *(Pololu, MDN Baseline,
   design-system rule 3)*
10. **Figures are a picture in a 1 px frame with the caption under it.** The figure id comes first (FIG A1-01,
    FIG BG-05), then one line, then the source line in mono. No gradient behind figures, and no zoom-on-hover.
    *(Rust Book, Nature, NASA Science credit line)*
11. **Key numbers sit in a ruled strip:** label, value in 26 px tabular figures, the limit and its status word, and
    the current value under a dashed rule. *(BETA, Airbus key figures, OWID metadata)*
12. **One accent colour, used only for "here / selected / follow this".** Bars in data charts are neutral (BOM spend,
    allocation share); amber marks "≥ 99 % used". Every colour is a token in both themes, including the plot paper and
    the lightbox scrim. *(Tufte greyscale text, Carbon status/data separation)*
13. **Square geometry:** radii of 2 / 3 / 4 / 6 px. No 999 px pills; the build-stage selector is a ruled segmented list.
    *(REVIEW-STYLE "square hairline geometry")*
14. **Plain, specific UI copy.** A heading names the thing ("Running the files", not "How to use the redesign"). Verdict
    sentences carry numbers. One primary button per group.
15. **Phone width:** no sideways page scroll at 400 px. Wide tables and the morphological chart scroll inside their own
    frames; the contents list folds closed. *(design-system README check 5)*

## 4. "Generated look" patterns removed

| Pattern | Where it was | Now |
|---|---|---|
| Eyebrow label in small mono caps above every heading, then a 32 px sentence as the heading | every section (`.secno` + `ds-display`/`ds-h1`) | short title, meta line underneath, verdict sentence in body weight |
| Everything in a rounded panel with a fill | subsystem, team, phase, constraint, concept, simulation and how-to cards; figures; tables; metric strip | hairline rules; only the 3-D viewer panels and the morph-chart tool keep a frame |
| Uniform card grids of the same height | Subsystems, Team, Status phases, Docs "how to" | the same grids as ruled columns with no boxes, so the content sets the rhythm |
| Status dots with no word; filled pastel washes behind every badge | key-number tiles, badges, simulation verdicts | outlined word, colour on the text only |
| Badge soup in the top bar | lone `PROPOSED` pill | "Design PROPOSED", once |
| Pill-shaped chips (999 px radius) and an "Enlarge" pill | build-stage selector, plot overlay | square segmented list, small square label |
| Decorative brand icon in the top bar | plane glyph beside "K09-L" | wordmark plus "Quad tailsitter · design review" |
| Frosted-glass (backdrop blur) top bar | `.ds-topbar` | solid background, single rule |
| Gradient fills behind cards and figures | render tiles, concept sketches, subsystem thumbnails, GA sheet | flat panel colour; the gradient stays only behind the live 3-D model |
| Hover zoom on images | render gallery | border darkens on hover |
| Several primary (filled) buttons in one row | Docs button row (3 filled) | one primary button per row |
| Vague or duplicated headings | "Every concept considered", "What we accept, what reverses it…", "Build sequence" over "Build sequence, stage by stage", "Every document, on GitHub" | "All 43 concepts", "Risks, reversal triggers and pre-order actions", "Stages 2 to 11 of the build guide, one clip each", "The file to start from in each area of the repository" |
| Literal colours outside the token set | plot backgrounds, lightbox, fasteners button | `--plot-paper`, `--plot-ink`, `--scrim*` tokens |

## 5. Not changed, on purpose

- All engineering content: every number, table row, claim id, BOM line, source line and file link, and the data files,
  viewer, proof graph, renders, drawing, plots and videos.
- The proof-chain page keeps its own layout from `proofs/index.html`, regenerated by `make_proof_embed.py`. It inherits
  the new tokens; one rule in `app.css` stops a global `.fail` class from leaking into its tiles.
- Theme behaviour is the same: `data-theme` overrides the OS preference, and print is always light.
