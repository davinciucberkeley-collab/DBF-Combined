# Scaled quad tailsitter VTOL (concept A) — student project

**Configuration changed 2026-11-14 (D-182, J6 board, `redesign/review/QP-1/BOARD.md`):**
K09-L could not be built new within the $2,000 limit (cheapest workable build
about $2,577, `redesign/review/CLOSURE-ROUND-2026-11-14/DESIGN-TO-COST.md`).
After sizing four concepts to the same depth (`redesign/review/QP-1/`), the board
chose **concept A, a scaled-down quad tailsitter**: about 1.23 kg, 0.90 m wing,
T-Motor MN2212 KV780 on 4S, 4S 2000 mAh packs, one-piece in the car box,
about $1,499 (margin about +$501, estimate). Fallback: B, the small quadplane,
after re-pricing; lifeboat: the ZOHD Altus VTOL kit if there is no tethered hover
by 2027-02-15. D-181 (quadplane, provisional) is reversed. The K09-L description
below is the previous design, kept as the record; its lessons apply to concept A.

The previous design (team decision 2026-11-13, see `redesign/CONFIGURATION.md`)
was **K09-L**: a quad tailsitter. A flat flying wing about 1.15 × 0.30 m with
two fins, four fixed motors in an X; it takes off standing on its fin tips as
a quadcopter, pitches 90° to cruise on the same motors with two elevons, and
pitches back to land. No pusher, no tilt, no separate lift rotors. Mass gate
2.6 kg. The project began as a hybrid lift + cruise concept (8–15 kg, pusher);
the configuration study replaced it, and the older root folders still describe
that concept.

## Hard constraints
- $2,000 total physical budget (hardware, spares, batteries, test gear,
  shipping, tax). The Jacobs Hall Makers Pass is paid outside this budget.
- Built and flight-tested by the end of April 2027.
- Portable: a team of 4 moves it routinely; hard cap under 25 kg (55 lb).
  It need not travel in one piece (user, 2026-11-14), but the packed aircraft
  must fit in one standard car trunk, two at most. (K09-L travelled in one
  piece in a ~1.25 × 0.55 × 0.45 m box.)
- Passes a 3-D physics simulation: every build step and the assembled
  aircraft (`redesign/showcase/animation/assembly_check.py`, collision
  `redesign/collision/collide.py --glb`) with no part interpenetration, no
  open wire ends and no exemptions; flight cases in the 3-D sims (C5 landing,
  SITL) pass against their limits.

Within these constraints the engineering agents (`redesign/TEAM.md`) make the
design decisions, including mass, mission and performance trade-offs; log
each one with its reasoning in `redesign/params/CHANGE-LOG.md`.

## Where things are
- README.md is the front door: directory map, status, how to view the pages.
- DECISIONS.md lists the open design-parameter conflicts. Do not pick a side
  silently; the root `analysis/` + `cad/` are the 11-02 resize, while
  `inventory/`, `fusion/`, `concepts/variants/` are still on v0.3.1.
- PROVENANCE.md says which source repo and commit each area came from.

## Working rules
- Scope is the real, physical aircraft. Ignore any browser flight-sim code.
- Every number cites its source: a repo file, a shown formula, or a URL with
  the date checked. Look up prices and specs; don't recall them.
- Label estimates as estimates. Unknowns are "—", never invented.
- Reports follow docs/reference/REVIEW-STYLE.md.
- Never commit secrets (API keys, tokens, passwords), including the team's
  Claude API key: keep it in an environment variable or a git-ignored `.env`.

## Team (commit attribution)
The repo lives at davinciucberkeley-collab/DBF-Combined (consolidated 2026-11-08 from
DBF-VTOL, DillonVTOL, TiltWing and OpenCAEModel; see PROVENANCE.md). Claude sessions push from a
shared account, so ask who is working (or use the name they give) and credit them
with `git commit --author "<Name> <email>"`. Use `Co-Authored-By: <Name> <email>`
trailers for work done together. Use these GitHub no-reply emails, never personal
addresses.

| Name | GitHub | Commit email |
|---|---|---|
| Tristan Hottier | TristanHottier | 185231225+TristanHottier@users.noreply.github.com |
| Dillon Alcouffe | Dalcouffe1 | 130024709+Dalcouffe1@users.noreply.github.com |
| James Guymon | JamesRop | 55683057+JamesRop@users.noreply.github.com |
| Vaibhav Bagrodia | vaibhav1301-arch | 336305533+vaibhav1301-arch@users.noreply.github.com |

## Key files
- docs/VTOL-REVIEW-PROMPT.md — the design-review task.
- docs/reference/REVIEW-STYLE.md — house style for reviews.
- docs/reference/lift-cruise-reference.png — BETA Alia and 8-lift reference
  configurations.
