# DaVinci API: findings (T-037, R-INT-04, spec 8.3)

**Status (2026-11-23, updated after AM-045):** the product and its API documentation are identified. The task is still BLOCKED, because there is no account and no token yet, and AM-003 keeps spend at $0. Nothing has been called and nothing has been spent.

## 1. What the team repos say

Source: `davinciucberkeley-collab/dbf-hangar` @ `cf4e7164` (Tristan Hottier, 2026-11-23), read-only clone.

| Item | Where | What it says |
|---|---|---|
| Adapter | `core/hangar/adapters/davinci.py` (24 lines) | Stub only. `available()` returns False; `push`, `pull` and `run` return SKIP "DaVinci API access not configured (D3 decided: skip until real calls after Dec 1)". It has no network code and no tokens. |
| Decision D3 | `ledger/items.yaml` | Asks "DaVinci API: who has access, which account, is a Claude connector set up?" The owner is blank. The default was taken: ship the adapter as SKIP and move the full DaVinci build to after Dec 1. |
| Ruling R29 | `ledger/items.yaml` | "Connect DaVinci API to Claude; do a full build in DaVinci". Superseded by D3: "full DaVinci build after the Dec 2 deadline". |
| CLI | D45, T107 | `plane davinci push` and `plane davinci pull` are planned for hangar v1.1. |

The team weekly-update page (week of 2 Dec) repeats the ask: "Connect the DaVinci API to Claude and do a full build through it; message Douglas if setup stalls."

## 2. The DaVinci Programmatic API (read 2026-11-23)

Sources, all opened in the browser on 2026-11-23:
- https://docs.davinci-app.com/pages/api/introduction
- https://docs.davinci-app.com/pages/api/personal-access-tokens
- https://docs.davinci-app.com/pages/api/simulation-results

**Base and auth.**
- Base URL: `https://davinci-app.com/api/v2/`.
- Auth is a user-owned personal access token sent as `Authorization: Bearer dav_ak_live_…`. The token is 110 characters, carries scopes, expires after at most 90 days, and is rate-limited to 1–10,000 requests per minute (default 60).
- It is created in the web app under Settings → Connections → Personal Access Tokens. It is shown only once.
- There are official SDKs for TypeScript (`@celedon/davinci-sdk`) and Python. Raw HTTP works without either.

**Sections.**

| Section | What it covers |
|---|---|
| Projects | Create, open, close and delete projects; branches, packages, personas; files. |
| Content | The object tree; add and delete objects; export an object to a file (PDF, docx and so on). |
| Branches | Branch, commit, uncommitted changes, object history. |
| Sessions / Agent / Chats | Open a project session and prompt its agent. Chats also appear in the web app, where a person can watch or take over. |
| Tools | Run one of the agent's tools directly with `invokeTool`: deterministic, and "incurs no LLM charges". |
| Usage | What model usage cost, by account, project, session or day. Spend only, not balance or limits. |
| Tests | Start an authored Test and read its status and evidence. |
| Organizations / Teams / Cards | Team boards, sprints and project Task Cards. |

**Scopes.** These fit our case:
- `projects:read` / `write` / `manage` (a ladder: each includes the one before);
- `sessions:manage`;
- `agent:message`;
- `usage:read`, needed to see spend;
- `cards:*` and `teams:*`.

**Simulation results.** A LIVE simulation can be read with no agent and no model charge:
- `QueryOptics` returns optics data.
- `ExportSimulationPlot` returns any result display (QoIs, dynamics curves such as frf, srs and psd, thermal histories) as JSON/CSV/PNG.

The documented displays lean toward optics and structural dynamics. Whether DaVinci models aircraft (aero, flight dynamics, landing) is **—**: the docs read so far do not say.

**Cost model.**
- Prompts to the project agent use LLM models, and the Usage endpoints report what that cost.
- Direct tool calls (`invokeTool`) are documented as free of LLM charges.
- Any subscription or seat price: **—** (not on these pages).
- Spec 8.3 asks us to measure the cost, not assume it. The plan does that with the Usage endpoint before and after each step.

## 3. What spec 8.3 asks, and status

| Spec 8.3 step | Status |
|---|---|
| Investigate the API capabilities available to the team | Done from the docs (s2). Capabilities as the team's account sees them still need a token. |
| Attempt the agreed design-build workflow through Claude Code with authorized access | Blocked: no token, and spend stays at $0 (AM-003). |
| Verify real functionality and cost | Blocked; the method is in s4. |
| Document failures and external dependencies | This file. Dependencies: a DaVinci account, a token, a project, and spend approval. |

## 4. Proposed workflow once a token exists (read-only and $0 first)

1. **Token, created by Dillon or the account holder.**
   - Claude cannot create accounts or tokens.
   - Scopes: `projects:read`, `usage:read`. Expiry: 30 days. Rate limit: 60 per minute.
   - Store it in an environment variable `DAVINCI_API_KEY` or in a git-ignored `.env`, never in the repo (CLAUDE.md rule).
2. **Read-only probe**, raw HTTP with curl, no SDK install:
   - list projects;
   - read one project's object tree;
   - read Usage before and after (it should show $0).
3. **Map concept A** to DaVinci objects (mass items, parts, requirements). This needs `projects:write` on a scratch branch, never `main`. Create the objects with the documented validation, then commit to the branch.
4. **Run one check with `invokeTool`** (no LLM charge) and compare it with our own value, for example mass roll-up or CG.
5. **Only with an approved cap:** one agent prompt (`agent:message`), with Usage read before and after, to measure the real cost per prompt.
6. **Record results:** failures, rate-limit hits, cost per call, and what data leaves the team (privacy). Record them here and on the ledger. Then wire the hangar adapter (`push` / `pull`) only after AM-038 is lifted.

## 5. What the team still has to provide

1. A DaVinci account for the team, and who holds it. Is it Douglas (the weekly page names him for setup)?
2. A token with the scopes above, set as `DAVINCI_API_KEY` on the machine that runs Claude.
3. A spend cap for agent prompts (AM-003 is $0), and whether DaVinci spend counts inside the $2,000 budget.
4. The "agreed complete design-build workflow": which DaVinci project, and what "a full build in DaVinci" must produce.

## 6. Can Claude Code usage replace the DaVinci AI budget? (question from Douglas via Dillon, 2026-11-23)

Probably yes for most work. It has to be measured before it counts (spec 8.3).

**The pattern.** Claude Code does all the reasoning and DaVinci's agent is never prompted. Claude calls only the API's non-agent operations:
- objects, branches and commits;
- exports;
- `invokeTool`.

**Evidence that this costs nothing:**
- `invokeTool` "incurs no LLM charges" (API introduction).
- The billing docs (docs.davinci-app.com/pages/browser/usage-plans-billing/overview.md, read 2026-11-23) describe AI usage (included usage first, then on-demand, invoiced at $100) and storage. Object reads and writes are not described as billed.

**Unknowns (—):**
- session and compute cost;
- simulation compile cost;
- seat or subscription price (celedon.solutions/pricing, not checked);
- whether the team's deployment and terms allow this.

**Not the same thing.** Organization API keys (bring your own AI provider key, on some deployments) would use a separate Anthropic API key with its own billing, not this Claude account.

**Test: the $0 proof.** Read Usage, open a session, do reads, one `invokeTool` call and a scratch-branch write, close the session, read Usage again. Record the before and after values, the session duration and the storage change.

## 7. Probe 1: read-only, run 2026-11-23 (`python -I tools/davinci_probe.py`)

Token: created by Dillon with scopes projects:read and usage:read, kept in the git-ignored `.env`. The token was never printed or logged.

| Step | Result |
|---|---|
| GET /usage (before) | HTTP 200 in 0.63 s. Account lifetime AI spend $49.06; 1,093 usage events; asOf 2026-11-09 |
| GET /projects | HTTP 200 in 0.14 s. One owned project ("Test", private, charge method "user") |
| GET /projects/{id}/tree | HTTP 200 in 0.62 s. 10 objects (Library and Model packages, an "I-Beam 1m" geometry, …) |
| GET /usage (after) | HTTP 200 in 0.21 s. Unchanged: $49.06, 1,093 events, same asOf |

**Result.**
- Token auth, project listing and reading the object tree all work.
- Reads add no usage events and no spend.
- Usage is recorded on an interval. To rule out a late charge, read Usage again after a day.

**Not yet tested.** Douglas's pattern: open a session, run `invokeTool`, write to a scratch branch, close. That needs a token with `projects:write` and `sessions:manage` (probe 2).

The raw JSON is kept locally only (git-ignored: account spend and ids).

## 8. Probe 2: Claude drives and DaVinci only runs tools, 2026-11-23 23:33 (`python -I tools/davinci_probe2.py`)

Token scopes: projects:read, projects:write, sessions:manage, usage:read. **No `agent:message` scope**, so DaVinci's agent could not run. Project "Test", on the new scratch branch `claude-probe-20261123-233319` (`main` untouched, no commit made).

| Step | Result |
|---|---|
| Usage before | $49.060351, 1,093 events |
| Create scratch branch from main | 201 (0.93 s) |
| Open session on the branch | 201 (0.39 s) |
| invokeTool Core/ReadObject on the Model package | 422 TOOL_ERROR: the package id is not a UUID. The tool's own validation rejected it; nothing ran |
| Add one object (type requirement) on the branch | 201 (1.21 s) |
| invokeTool Core/ReadObject on that object | 200 (0.17 s). Deterministic read, no model involved |
| Delete the probe object | 200 |
| Close session | 200 |
| Usage after | $49.060351, 1,093 events: **unchanged** |

**Result.** Douglas's pattern works:
- Claude Code makes the decisions.
- DaVinci does the work: sessions, writes and direct tool calls.
- DaVinci recorded no AI usage events and no spend.

**Caveats.**
- Usage is recorded on an interval, so read it again after a day to rule out a late charge.
- The scratch branch is still there, because deleting a branch needs projects:manage. Remove it in the UI.
- Any subscription or seat price is not covered by this test (see s6).
- Raw JSON is kept locally only (git-ignored).

**User check (2026-11-23, after the 367-object import, AM-047):** Dillon saw the imported snapshot in the DaVinci web app and confirmed that the DaVinci budget shown there had not changed. That matches the API Usage reading ($49.060351 / 1,093 events). A next-day re-read is still due.

## Spend evidence: what it does and does not show (fix pass C, review round 13 R13-3, 2026-11-24)

- The Usage `asOf` stayed **2026-11-09** through every probe (probes 1 and 2, the imports). Equal before and after values ($49.060351, 1,093 events) are therefore consistent with no charge but are **not proof** of $0, because the usage snapshot predates all probes.
- Dillon's UI check (2026-11-23, above) showed the DaVinci budget unchanged. That is the only other evidence.
- Proof needs a later Usage read after `asOf` moves past the probe times, or the DaVinci invoice / wallet. Until then the claim is "no change observed, usage snapshot stale".

**Storage facts (read 2026-11-24):**
- API Test: storageUsedBytes 836.1 MB.
- Held by the 205 STEP geometry objects (129 + 76 assembly copies) on branch `concept-a-snapshot-73656c93`. The attached files are only the 2.5 MB GLB.
- The organization is at about 1.0 of 1.0 GB, with Model Benchmarks at 226 MB.
- Deleting the branch is pending with Dillon (AM-050; deletion needs his approval, R-GEN-02).
