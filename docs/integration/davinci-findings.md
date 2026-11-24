# DaVinci API: findings so far (T-037, R-INT-04, spec 8.3)

2026-11-23. Status: **BLOCKED on access** (no account, key, docs or spend approval; AM-003: "don't do any DaVinci spend yet").
Nothing was called and nothing was spent.

## 1. What the team repos say

Source: `davinciucberkeley-collab/dbf-hangar` @ `cf4e7164` (Tristan Hottier, 2026-11-23), read-only clone.

| Item | Where | What it says |
|---|---|---|
| Adapter | `core/hangar/adapters/davinci.py` (24 lines) | Stub: `available()` returns False; `push` / `pull` / `run` return SKIP "DaVinci API access not configured (D3 decided: skip until real calls after Dec 1)". No network code, no tokens. |
| Decision D3 | `ledger/items.yaml` | Question "DaVinci API: who has access, which account, is a Claude connector set up?" Owner blank. Decided by default: adapter ships as SKIP-with-reason; full DaVinci build moves to after Dec 1. |
| Ruling R29 | `ledger/items.yaml` | "Connect DaVinci API to Claude; do a full build in DaVinci", superseded by D3, "full DaVinci build after the Dec 2 deadline". |
| CLI | `plans/.../briefs/U2.3-adapters.md`, D45 | `plane davinci push` / `pull` are planned for hangar v1.1, not v1.0 (T107). |
| Tools doctor | `docs/team-guide.md:490` | `davinci  missing  DaVinci API access not configured ...` |

So the team's own tooling has the seam (one adapter, push / pull / run over a `plane.yaml` design), but nobody has recorded an account, an endpoint, an API document or a price.

## 2. What is public (searched 2026-11-23)

- The only public source found is a slide deck, "Transforming Systems Engineering Through Agentic AI", by Dr. Chris Helmerich (SERC):
  https://sercuarc.org/wp-content/uploads/2025/09/Helmerich_Davinci.pdf (fetched through search, 2026-11-23).
- The deck describes Davinci as an agentic-AI engineering platform:
  - LLM-agnostic, with "LLM APIs" and "app APIs";
  - engineering data products for requirements, CAD, schematics and software.
- All performance figures in the deck are self-reported.
- No public API reference, pricing or terms were found.
- **Not confirmed** that this is the DaVinci the team means. The org name `davinciucberkeley-collab` suggests a sponsor link, but that is an inference.

## 3. What spec 8.3 asks, and what each step needs

| Spec 8.3 step | Needs | Status |
|---|---|---|
| Investigate the API capabilities available to the team | API docs, or a sandbox account | — (none found) |
| Attempt the agreed design-build workflow through Claude Code, with authorized access | Account and key in an env var / git-ignored `.env` (CLAUDE.md), an agreed workflow, Dillon's OK | Blocked (AM-003) |
| Verify real functionality and cost; do not assume API use bypasses service charges | Price list or a metered test call, with a spend cap approved first | Blocked |
| Document integration failures and external dependencies | The attempt | This file, to be extended |

## 4. Proposed workflow once access exists ($0 until approved)

1. Export concept A to the team schema: `dbf-hangar/designs/concept-a/plane.yaml`.
   - That copy was imported from DBF-Combined @ `171ec426`, so it predates D-227..D-247 and must be refreshed first.
2. Push one design read-only (`plane davinci push`, hangar v1.1). Pull it back and diff, to prove round-trip without loss.
3. Run one small analysis or build step in DaVinci. Log the cost meter before and after, and compare its result with our own check of the same quantity (for example mass roll-up or CG).
4. Record failures, rate limits, cost per call and data that would leave the team (privacy), here and in the ledger.

## 5. Questions only the team can answer

1. Which product is "DaVinci"? Give its URL or a contact.
2. Who holds the account? Is there an API key or a Claude (MCP) connector?
3. Is there a cost, and what spend cap is approved (AM-003 is $0 for now)? Is DaVinci spend inside the $2,000 budget or outside it, like the Jacobs Makers Pass?
4. What is the "agreed complete design-build workflow"? Is it hangar D3/R29 "a full build in DaVinci"?
