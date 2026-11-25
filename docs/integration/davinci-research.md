# DaVinci research: capabilities, Claude connector, pricing (T-037, R-INT-04)

Date checked: 2026-11-23. Companion files: `davinci-findings.md`, `davinci-mapping.md` (object types and mapping).

## 0. Spend check (GET /api/v2/usage)

| When | amountUsd | eventCount | asOf |
|---|---|---|---|
| Start of this run | 49.060351 | 1,093 | 2026-11-09T07:22:13Z |
| End of this run | 49.060351 | 1,093 | 2026-11-09T07:22:13Z |

Unchanged. No agent prompt was sent. Usage is recorded on an interval, so re-read after a day to rule out a late charge (same caveat as findings s8).

## 3. Capabilities

**Tools (agent toolboxes).** Source: https://docs.davinci-app.com/pages/editor/agent/agent-tools.md. Core (web search, project inspection, model manipulation, toolbox management); domain toolboxes: Parts & Components, Documents & Artifacts, Geometries (`MeasureModel`: distances, bounding boxes, volumes), Image Generation, Source Control, Pages, Resources & Scheduling, Behavior Modeling, Software Engineering, Simulation, Requirements Engineering, Risk Management, Attributes & Analysis, Tasks, Tags, Constraints & Verification, Comments, Reviews, Entities & Relationships, Circuits & Electronics; part sourcing (Digikey; McMaster-Carr and SatCatalog when available); custom toolboxes written in Python with `davinci.tool()`.

**invokeTool listing.** The API has no list-tools endpoint: the invoke page says it does not enumerate toolboxes or tools, only `Core` / `ReadObject` are shown (https://docs.davinci-app.com/api-reference/tools/invoke-one-of-the-agents-tools-directly.md; the OpenAPI file also has only invokeTool). Names above come from the Agent Tools page. Which tools exist depends on the session's project. A call is documented as "incurs no LLM charges" and was proven $0 in probe 2.

**Simulation toolbox tools.** SetupSimulation (mesh + boundary conditions), CompileSimulation, QuerySimulation, OptimizeSimulation, VerifySimulation, CaptureSimulationView, QueryOptics, ExportSimulationPlot, GetSimulationReference, RunSimulation (executes Python simulation code objects).

**Physics supported** (https://docs.davinci-app.com/pages/user-guide/views/simulation.md):
- Certified: steady thermal conduction (convection, flux, radiation); linear structural statics (fixtures, forces, pressures, body accelerations, springs, preloaded contacts); thermo-elastic coupling.
- Gate-validated: modal, harmonic, random vibration, shock, acoustic, rotor tone sweep, transient thermal, transient structural, laminar flow; optics.
- System simulations: multibody (linked-assembly motion), networks (electrical, magnetic, rotational, translational, thermal, thermal-fluid, hydraulic), controls, linear analysis, contact dynamics.
- Methods named: Newmark, Richardson extrapolation, SLSQP, rainflow/Goodman/Miner fatigue, Latin hypercube/Sobol/Saltelli/Monte Carlo.

**Aircraft work.**
- Aerodynamics: none (CFD limited to laminar flow; no external aero, no airfoil/propeller models documented).
- Flight dynamics: none documented; "Flight simulation is not mentioned". Multibody plus controls could host a hand-built rigid-body model, but nothing aircraft-specific is provided.
- Structures/FEA: linear statics and modal exist, so part-level stress or modal checks (wing, hub, fin fitting) are plausible. Not tested here; fidelity vs our own FEA is **—**.
- Landing: no landing-gear tool; contact dynamics plus multibody could model the foam-stroke case. **—** whether usable.
- Verdict: DaVinci does not replace our 3-D flight/landing sims (SITL, C5). Structures and multibody are the only overlap.

**Python code objects (run our own scripts).** Source: https://docs.davinci-app.com/pages/modeling/objects/code.md and python-database-api.md.
- Yes, with limits: Python runs in the browser via Pyodide (backend execution also referred to in the Database API page); libraries listed are NumPy, SciPy, Matplotlib, Pillow, pandas (limited). Our proof scripts use the standard library and presumably numpy/scipy, so small pure-Python calculations could be ported; anything needing other packages or our repo files would not run. Runtime, memory and file limits are not specified (**—**).
- Code objects read and write the model (`@` references, `update()`, `database.create/update/search/relate`), within a per-type writable allowlist.
- `RunSimulation` runs Python simulation code objects; custom toolboxes run async Python tools.
- Writing a Code object's `language` and `code` through the Python Database API is read-only, but REST add-objects accepts both fields at creation (live schema probe, mapping s2). Whether a REST-created Code object then executes: not tested (**—**).

## 4. Claude connector (MCP)

- **DaVinci as MCP server for Claude Code: not found.** The MCP page (https://docs.davinci-app.com/pages/editor/project-settings/mcp.md) and Integrations Overview (https://docs.davinci-app.com/pages/integrations/overview.md) describe only DaVinci connecting out to external MCP servers so its own agent can use them. The API introduction names only the TypeScript and Python SDKs. A grep of llms.txt (about 350 pages) and the OpenAPI file for "mcp" found only the outbound-MCP configuration and admin pages. A web search found no Celedon/DaVinci MCP server; results were unrelated products (Ping Identity DaVinci, DaVinci Resolve).
- **Outbound auth options (for reference):** none, OAuth (auto client registration or own client ID), OAuth machine-to-machine, bearer token, API key header (default `X-API-Key`), username/password; shared or per-user credentials.
- **What works today for Claude Code:** the REST API directly with a personal access token (`Authorization: Bearer dav_ak_live_...`, scopes, max 90 days) using stdlib HTTP as in `tools/davinci_probe2.py`, or the SDKs. A local MCP wrapper over these routes would be our own code; not built.
- The data-plane grant (`dav_gr_...`) is session-scoped, minted by opening a session; not needed for the routes used so far.

## 5. Pricing

Source: https://celedon.solutions/pricing (read 2026-11-23); billing pages under docs.davinci-app.com.

| Plan | Price | Storage | Projects | Other |
|---|---|---|---|---|
| Individual Free | $0 | 100 MB | 2 | one-time trial usage |
| Core | $20/month | 1 GB | 5 | up to 3 collaborators per project; lower-cost models |
| Max | $200/month | 10 GB | unlimited | 10x Core usage; 10 collaborators per project; higher-cost models |
| Group (Teams) | $40 per user per month | 10 GB | unlimited | group billing |
| Enterprise | custom | n/a | n/a | private AI endpoints, dedicated hosting |

- **What counts as AI usage:** the pricing page does not define it. The Usage and Costs page (https://docs.davinci-app.com/pages/admin/usage-and-billing.md) tracks "LLM token and call volume, embedding calls, and tool calls", charged to Included Usage, Credit Balance, On-Demand Usage and Overflow. The individual plans page says credits cover "generating model objects, chatting with the design agent, and uploading files" (https://docs.davinci-app.com/pages/getting-started/plans.md). So some actions outside agent chat may use credits; probe 2 showed none for branch, session, add-object, invokeTool and delete.
- **Sessions, compute, storage, API calls:** the Usage page lists "Storage", "API calls" and "Compute" as usage event types but gives no rates or definitions. Pricing page mentions no charge for sessions, compute or API calls. Storage is limited per plan (table). Rates: **—**.
- **On-demand:** paid plans only (Free: not available); accrues as an unbilled balance, invoiced when it reaches $100 by default, charged to the card immediately.
- **Seats:** per-project collaborator caps for Core and Max; Group billed per user; Individual seat count not stated.
- Budget note: the account has already spent $49.06 of AI usage lifetime (probe 1); whether the team's current plan is Free, a deployment allocation or other is **—** (not visible through the API; Usage shows spend only).
- Quotes: "Monthly included usage" (Core); "On-demand Usage" (paid plans); "Credits do not roll over between billing periods."

## Sources opened (all fetched 2026-11-23)

- https://docs.davinci-app.com/llms.txt (page index, also grepped locally)
- https://docs.davinci-app.com/pages/modeling/objects/objects.md, parts.md, requirements.md, tests.md, attributes.md, resource.md, risk.md, linkages.md, constraints.md, geometry.md, code.md, toolbox.md (object fields)
- https://docs.davinci-app.com/pages/modeling/common/units.md, equations.md, relationships.md
- https://docs.davinci-app.com/pages/modeling/python-database-api.md (read in full by download)
- https://docs.davinci-app.com/api-reference/content/add-objects.md (add-objects request schema, error behaviour)
- https://docs.davinci-app.com/api-reference/tools/invoke-one-of-the-agents-tools-directly.md
- https://docs.davinci-app.com/openapi/davinci-public.v2.yaml (grepped for invokeTool, mcp)
- https://docs.davinci-app.com/pages/editor/agent/agent-tools.md (toolboxes)
- https://docs.davinci-app.com/pages/user-guide/views/simulation.md (physics)
- https://docs.davinci-app.com/pages/editor/project-settings/mcp.md and https://docs.davinci-app.com/pages/integrations/overview.md (MCP)
- https://docs.davinci-app.com/pages/api/introduction (SDKs)
- https://docs.davinci-app.com/pages/admin/usage-and-billing.md, https://docs.davinci-app.com/pages/browser/usage-plans-billing/overview.md, https://docs.davinci-app.com/pages/getting-started/plans.md (billing)
- https://celedon.solutions/pricing (plans)
- Web search "Davinci Celedon MCP server Claude Code" (no DaVinci-app MCP server found; unrelated products only)
- Live API (token never printed): GET /usage (twice), POST /projects/{id}/branches, POST /projects/{id}/objects?branch=claude-scratch-20261123-2340 (all refused, 400)
- Local repo files for the mapping: BOM-A.csv, cad_mass.json, params-A.json, viewer-data.json, claims.a*.json, REQUIREMENTS-A.md, TEST-PLAN-O4B.md, CHANGE-LOG.md, docs/requirements.md (headers and structure only)
