# Configuration study — brief for every agent

UC Berkeley MEng capstone team (students) designing, building and flight-testing a drone. **The aircraft
configuration is open.** Nothing about the previous design (C0 lift + cruise, 2.4 m span, 7.4 kg) is fixed.

## The only real constraints (from the team lead, 2026-11-09)
1. **Budget: $2,000 total, hard.** Everything bought (airframe materials, propulsion, batteries, avionics, radio,
   chargers if needed, spares, shipping, tax) fits inside it, with a sensible reserve for crashes.
2. **VTOL** — takes off and lands vertically ("a sort of VTOL drone").
3. **Easy to transport** — student team, cars, campus; assume it must fit in a normal car (trunk/back seat) and be
   carried and assembled by one or two people quickly.
4. **Student-built** — UC Berkeley Jacobs Hall shop (3D printers, laser cutter, basic machining), hot-wire foam
   possible.
5. **Schedule (hard, updated 2026-11-09):** **parts ordered ~mid-December 2026** (so the configuration and a
   purchasable BOM must be settled by then); **building starts January 2027 at the earliest, early February at the
   latest; everything (build, ground tests, flight tests, final documentation) complete by the end of April 2027.**
   Plan for the worst case: ~12 weeks from first cut to finished, including repair after at least one crash. Parts
   ordered mid-December may arrive over the holidays; a part with a long or uncertain lead time (overseas shipping,
   custom props) is a schedule risk. Weight concepts heavily on build hours, part lead times, and how fast a crash can be
   repaired; a concept that needs most of the 12 weeks just to build is a poor fit.

**Team lead answers (2026-11-09):**
- **Mission: VTOL demonstrator** — vertical take-off, transition to forward flight, a short cruise, transition back,
  vertical landing. No payload requirement. This overrides any other default mission assumption in the study.
- **Nothing is owned.** The $2,000 must also cover all ground equipment: RC transmitter, LiPo charger and power
  supply, batteries (incl. spares), LiPo safety bag, basic tools/consumables not available at Jacobs Hall.

Everything else — span, mass, speed, endurance — is a **choice to be justified**, not a given.
The repo's `docs/DESIGN-BASIS.md` R-numbers were chosen by a previous AI agent; treat each one as a proposal to keep,
change or drop with a reason. Legal/safety context is real: FAA rules for small UAS (registration, < 25 kg, line of
sight, airspace near Berkeley/Richmond), and the team's test site (Richmond Field Station has been assumed).

## Also read
- `redesign/inputs/ADVISOR-XV24-LESSONS.md` — what the advisor's own AI run did well and where it failed (never
  finished, mass ran away, verification became the product). Avoid those failures.
- Previous work worth mining (read-only): `analysis/tradestudy.json` + `docs/research/configurations.md` (29-layout
  trade study; tailsitters ranked first overall), `explorations/tiltwing/`, `concepts/` (11 literature concepts and
  variants A1–A3), `docs/research/` (propulsion margin data, BOM savings, electrical architecture), the mentor's
  2026-11-04 meeting points (in `redesign/inputs/` notes if present): buildability before simulation, completeness
  audits until saturation, morphological charts, no floating parts.

## Repo and rules
Repo: `C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined`, branch `redesign/v1`. Write only inside
`redesign/config-study/<your folder>/` as instructed. Do not edit anything else, do not commit, do not install
software (Python stdlib only, `python -I`). Web research is encouraged: cite URLs, prefer manufacturer data and
documented builds over forum claims, and say which is which. Prices: note date seen and vendor.

## Output style (the team lead's goals)
Digestible (tables, one-page cards, no filler), easy to check (every number cites a source or a calculation shown),
easy to build (favour bought parts, simple processes). Mark guesses `ESTIMATE` and unchecked claims `UNVERIFIED`.
