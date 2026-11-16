# Survey of reference sites (checked 2026-11-16)

**Count.** 42 sites were opened and read. 41 were read as text with WebFetch (page structure, nav, how numbers and sources are shown). 10 were also rendered in headless Chrome and looked at (Stripe docs, Linear, Vercel docs, Tailwind docs, PX4 guide, Joby, Grafana, Formula Student Germany, plus Observable, which was only readable as a rendering). Fetch gives structure, not pixels, so type-scale and colour notes come only from the rendered ones; the rest are marked "text only".
About 17 further attempts failed and are **not** counted: Rocket Lab (bot wall), SpaceX (empty), Land-book, Lapa Ninja, Bell, BETA, Blue Origin, Tesla (403/404/429), Godly (DNS), Anduril (empty), NYT (blocked), Formula 1 and Shopify Polaris (redirects), NASA NTRS (timeout), tufte-css (404), Sketchfab render (blank), PX4 tailsitter page (404).
"Weak" = the fetch returned little, so the note is thin.

| # | Site | URL | Pattern worth borrowing | Seen |
|---|---|---|---|---|
| 1 | Stripe docs | https://docs.stripe.com/payments/accept-a-payment | Three columns: left tree, article at about 680 px measure, right "On this page" rail with "Optional" tags. Top product tabs. Tabs inside the article switch variants (Checkout / Elements / Mobile) instead of making new pages. "Copy page as Markdown" button. | rendered |
| 2 | Linear Method | https://linear.app/method | Numbered nav (2.3 ...), very sparse body, one idea per page. The numbering is what makes it feel authored. | rendered (home) |
| 3 | Vercel docs | https://vercel.com/docs | Mono for code, sans for prose, black and white with one accent. Left rail with chevrons, tabs on the hero code box. Dated "What's new" list with absolute dates. | rendered |
| 4 | Tailwind docs | https://tailwindcss.com/docs/installation | Numbered steps (01, 02 ...) with the terminal block beside the step text. Version pill in the header. Small-caps group labels in the sidebar. | rendered |
| 5 | PX4 User Guide | https://docs.px4.io/main/en/ | Warning callout with a left rule and tinted ground, badges as plain shields. Vehicles grouped by frame type, VTOL has its own branch. Version selector. Closest peer for our subject. | rendered |
| 6 | ArduPilot Copter | https://ardupilot.org/copter/ | Counter-example: a sidebar of dozens of links with repeats. Shows the cost of a flat nav. | text only |
| 7 | Zipline technology | https://www.zipline.com/technology | Numbers inside sentences with "up to" and a unit, no tables. Counter-example for us; we need tables. | text only |
| 8 | Joby aircraft | https://www.jobyaviation.com/aircraft/ | "Technical Breakdown": label/value pairs grouped Summary / Performance / Dimensions / Fleet, with a "Data as of December 2025" note. Borrow the as-of date. | rendered |
| 9 | Wisk aircraft | https://wisk.aero/aircraft/ | Headline figures, then quiet prose. Specs carry units and a qualifier ("about", "with reserves"). | text only |
| 10 | Mobbin | https://mobbin.com | Filters by pattern (navigation, tables, dialogs), not by site; screens shown as ordered flows. Relevant to how we order the build stages. | text only |
| 11 | Formula Student Germany | https://www.formulastudent.de/ | Team-site norm: full-bleed photo hero, menu by section and year, dark-mode toggle in the header. Counter-example for density: almost no data. | rendered |
| 12 | Siteinspire | https://www.siteinspire.com | Dense thumbnail grid, filters by type/subject/style, about 40 per page, one line of metadata each. | text only |
| 13 | Grafana (docs and site) | https://grafana.com/docs/grafana/latest/ | Sparse docs landing with one-line card descriptions. The product's panels (small title bar, units in muted colour) are the reference for data-dense dashboards. | rendered (grafana.com) |
| 14 | Sketchfab | https://sketchfab.com/3d-models/popular | Viewer chrome kept minimal; model metadata (title, author, licence) under the canvas; filters in one bar. | text only |
| 15 | Onshape help | https://cad.onshape.com/help/Content/Documents/documents-page.htm | Weak. Feature tree left, canvas centre, properties right: the three-pane pattern we already use. | text only, weak |
| 16 | MDN CSS | https://developer.mozilla.org/en-US/docs/Web/CSS | Skip links at the top, "In this article" TOC, nested expandable sidebar, inline code for every identifier. Very dense, still scannable. | text only |
| 17 | React docs | https://react.dev/learn | "You will learn" list at the head of each page, one concept per section, short paragraphs. | text only |
| 18 | NASA Artemis II | https://www.nasa.gov/mission/artemis-ii/ | Summary block of mission facts at the top (duration, dates), absolute dates beside relative ones. | text only |
| 19 | GOV.UK design principles | https://www.gov.uk/guidance/government-design-principles | Headings stated as plain claims, narrow measure. | text only |
| 20 | GOV.UK Design System, Table | https://design-system.service.gov.uk/components/table/ | Per-component page: when to use, when not to use, how it works, example with HTML tab, "Recent changes" table. Model for documenting our status and badge vocabulary. | text only |
| 21 | GitHub Docs | https://docs.github.com/en/get-started | Hub pages with link plus one-line summary. Cautionary: 100+ links in one column. | text only |
| 22 | Notion Help | https://www.notion.com/help | Search-first landing, categories as a plain menu. | text only |
| 23 | Cloudflare Developers | https://developers.cloudflare.com/workers/ | Skip to content, "On this page", copy-as-Markdown, hairline rules between sections instead of boxes. | text only |
| 24 | Supabase docs | https://supabase.com/docs | Top menu (Start / Products / Build / Manage / Reference) changes the sidebar below it. Header search. | text only |
| 25 | PlanetScale docs | https://planetscale.com/docs | A few product cards, then plain links; llms.txt index. | text only |
| 26 | rauno.me | https://rauno.me | Weak. Three-link nav (Craft / Projects / Field Notes); restraint. | text only, weak |
| 27 | Distill (growing CA) | https://distill.pub/2020/growing-ca/ | Figures with captions and "Reproduce in a notebook", numbered references, ready-made citation and BibTeX. Direct model for "every number cites its source". | text only |
| 28 | Wingtra | https://www.wingtra.com/wingtraone/ | Weak. The spec table lives on another page, which is the thing to avoid. | text only, weak |
| 29 | Our World in Data | https://ourworldindata.org/co2-and-greenhouse-gas-emissions | Each chart has Download, "What you should know about this data", numbered endnotes and a "Cite this work" block. | text only |
| 30 | Awwwards (engineering) | https://www.awwwards.com/websites/engineering/ | Left filter panel (category, tag, technology, font, colour) with Reset. | text only |
| 31 | Sketch docs | https://www.sketch.com/docs/ | Highlights list, then "Explore all topics" as plain lists. | text only |
| 32 | GitHub Primer | https://primer.style/ | Tokens documented as primitives (colour, spacing, type); dark-mode toggle in the doc header. | text only |
| 33 | Carbon, data visualization | https://carbondesignsystem.com/data-visualization/getting-started/ | Chart types grouped Simple / Flow / Spatial; entries marked "Design only" where no code exists. The honesty we need for UNVERIFIED parts. | text only |
| 34 | NASA Aeronautics | https://www.nasa.gov/aeronautics/ | Project blocks: headline, captioned photo, one paragraph, link out. No specs on the hub. | text only |
| 35 | Skydio X10 | https://www.skydio.com/x10 | Large headline numbers, then a two-column spec table (category / value, units inline). | text only |
| 36 | DJI Mavic 3 Pro specs | https://www.dji.com/mavic-3-pro/specs | Spec table grouped by component (Aircraft, Camera, Battery ...) with test conditions beside values. Closest model for our BOM and mass tables. | text only |
| 37 | Oxide Computer | https://oxide.computer/ | "Fig. 1" captions, short declarative headings, hardware shown as photographs and the real UI. The tone a hardware team can have. | text only |
| 38 | Oxide docs | https://docs.oxide.computer/ | Three entries (API / CLI / Guides), Ctrl+K search, bracket keys to switch sections. | text only |
| 39 | Framer | https://www.framer.com/ | Weak. Nothing usable; kept as a check on what the generic template look is. | text only, weak |
| 40 | NN/g, mobile tables | https://www.nngroup.com/articles/mobile-tables/ | Lock the header and first column, show a cut-off column as a scroll cue, let users pick columns, group with accordions. Applies to our BOM at 390 px. | text only |
| 41 | WCAG 2.2 quick reference | https://www.w3.org/WAI/WCAG22/quickref/ | Criteria tagged A/AA/AAA with a filter; used as the checklist for the critique. | text only |
| 42 | Observable | https://observablehq.com/ | Serif body for prose against sans UI; dark navy hero with a large light-weight headline; small tab labels above cells. | rendered |

## What the survey says
1. The strongest engineering docs (Stripe, Tailwind, Vercel, PX4, Cloudflare) use three zones: left tree, one 65 to 75 character article column, right "on this page". They separate with hairline rules and whitespace, not boxes.
2. Numbers appear as label/value rows with units in a muted colour and a date or condition beside them (Joby "data as of", DJI test conditions, OWID "what you should know").
3. Source and citation are first-class (Distill, OWID: cite block, numbered endnotes). We have the data and show it as a small underlined filename.
4. A status vocabulary is documented once (GOV.UK, Carbon "Design only"). We use several coloured pill styles with no legend.
5. On mobile, tables lock the first column and signal overflow (NN/g), and navigation collapses to a menu; it does not shrink to a 99 px scroller.
6. Marketing pages (Zipline, Joby hero, Framer) are the pattern to avoid for a technical record: slogans and vague "up to" figures.
