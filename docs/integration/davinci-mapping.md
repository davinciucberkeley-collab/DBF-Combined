# DaVinci mapping spec (T-037, R-INT-04): object types and how concept A maps

Date checked: 2026-11-23. Structure only; no current numbers are copied (T-101 elevon change in progress). Project used: "API Test" (id b53fed82-b072-43c2-9994-de76de845d93, design-build-fly org). Nothing was written to `main`. Live check ran on scratch branch **`claude-scratch-20261123-2340`** (from main, nothing committed, no object ever created: every POST was refused with 400). Deleting the branch needs projects:manage; remove it in the UI.

## 1. Writable object types (live, 400 `details.validTypes`, 2026-11-23)

POST /api/v2/projects/{id}/objects?branch=claude-scratch-20261123-2340 with type "zzz_invalid" returned HTTP 400 INVALID_OBJECT, "none were added". 34 writable types:

action, assembly, attribute, capability, circuit, code, constraint, dashboard, document, entity, figure, geometry, interface, item, journey, linkage, material, matrix, package, part, port, reference, requirement, resource, risk, simulation, slide, state, table, task, test, toolbox, trade, transition

The docs schema page (https://docs.davinci-app.com/pages/modeling/objects/objects.md) lists a smaller set; `circuit`, `dashboard`, `journey`, `material`, `simulation` are writable but not on that page.

## 2. Fields per type (live schema probe)

Method: POST each type with every candidate field set to null on the scratch branch. The validator returns one typed error per field it knows, so the error text is the schema. Nothing was written (all 400). The "unknown field" message is `<field>: not a field of type "<t>"`. Candidate list was mine (about 80 names), so a field outside it would be missed: absence here means "not in my candidate list or not a field".

**Common to all types (writable at creation):** `type` (required), `parent` (UUID, or `parentId` on the request; Model package `00000000-0000-0000-0000-0000000model`, Library `00000000-0000-0000-0000-00000library`), `name` string, `shortName` string, `documentation` string, `children` array, `tags` array. Docs say `tags` is refused on creation (assign afterwards) and `approval` is refused. The request body is `{"objects": {"<uuid>": {...}}, "parentId": "<uuid>"}`; ids must be client-minted UUIDs; all-or-nothing; the write is in memory until a commit.

| Type | Extra writable fields (type) |
|---|---|
| part | none beyond common. Mass, CG, cost are child `attribute` objects (docs: part owns Attributes, Constraints, Elements) |
| attribute | `value` string (equation or number), `unit` string, `kind` enum number/string/boolean/date, `enums` array, `cells` record, `stateValues` record |
| resource | `value` string, `unit` string (docs: value string also carries the isConsumable toggle) |
| requirement | `satisfied` string. Satisfaction is normally computed from owned constraints (docs: TRUE/FALSE/INCOMPLETE) |
| constraint | `value` string (equation giving true/false), `kind` enum inspection/analysis/similarity/test/sampling |
| test | `category` string, `weight` number, `status` enum pending/started/done/cancelled/waived, `procedure` object, `evaluationCriteria` object, `resultsValue` object, `results` object, `prerequisites` record. `verdict` not accepted at creation (resolved) |
| risk | `probability`, `impact`, `detectability` (number 0-1 or equation), `combinator` enum AND/OR |
| task | `startDate`, `endDate` string, `duration` object, `status` enum pending/started/done/cancelled, `prerequisites` record |
| code | `language` string, `code` string (docs: both read-only through the Python Database API, writable here) |
| toolbox | `code` string |
| geometry | `kind` string (docs: code CadQuery, step, onshape); data field name not found |
| assembly | `kind` string |
| simulation | `material` string, `status` enum empty/setting_up/setup/compiling/live/failed |
| reference | `location` object, `citation` object |
| material | `category` string, `description` string |
| document | `body` record |
| table | `rows` record, `cells` record |
| slide | `content` record |
| port | `kind` enum in/out/inout |
| transition | `kind` enum default/trigger/failure, `probability` number |
| trade | `kind` enum structural/parametric, `prerequisites` record |
| capability | `startDate`, `endDate` objects |
| action | `duration` object |
| package, linkage, item, entity, interface, state, matrix, figure, circuit, dashboard, journey | common fields only |

Not found: inner shapes of the `object`/`record` fields (test `procedure`, `results`, table `rows` and `cells`, task `duration`). Not found: a `relationships` field at creation. It was not flagged as a field, so relationships are made another way. Docs: Python Database API `database.relate`; REST route for relationships: not found. Relationship types are project-defined; base set (https://docs.davinci-app.com/pages/modeling/common/relationships.md): Uses, Reference, Performs, Connect, Realized, Subject (requirement to target), Mitigation, Source, Impact, Dependency, Resource, Validation (constraint to target), Transition, Result; custom: Data, Power, Mechanical, Optical, Chemical, Electromagnetic, Thermal, Fluid. The tests page says a Test links to a requirement with a `verify` relationship, which is not in that base list: check in the project's Schema tab before relying on it.

Units: strings in the `unit` field, e.g. kg, g, N, m, mm (docs list g, tonne, lbm; m, in, ft; N, lbf; decimal prefixes). Value/unit mismatch is an error. Equations use Math.js; reference another attribute with `@Name` or `[uuid]`; arrays up to 3-D with one unit.

## 3. Layout of the DaVinci project (proposal)

Top level in the Model package (all `package`):

```
Model
  Concept A (package)
    Requirements (package)      <- requirements
    Design (package)
      Aircraft (part)           <- assembly root
        <subsystem> (part) x10   wing, fins, cage, landing, mechanisms, propulsion, power, avionics, harness, assembly
          <part id> (part)       one per viewer-data part
            Mass (attribute, kg), CG x/y/z (attribute, m), Cost (attribute, USD), Qty (attribute), ...
    Procurement (package)       <- BOM lines
    Verification (package)      <- tests, proof claims, calculations
    Decisions (package)         <- D-entries
  Library (package)             <- source references (vendor URLs)
```

## 4. Source-to-object mapping

| Our source | DaVinci type | Fields | Parent |
|---|---|---|---|
| BOM line, `redesign/qp/A/BOM-A.csv` (cols id, subsystem, item, ship_group, qty, spares, unit_usd, flag, status, source_url, date_checked, note) | `part` named by item, `shortName` = id (P01...) | child attributes: `Qty` (kind number), `Spares`, `Unit cost` (unit USD), `Status`; `documentation` = note; source_url and date_checked go in a `reference` (location, citation) | Procurement/<subsystem> |
| BOM total and budget limit | `resource` (value equation summing children, unit USD, consumable) with a `constraint` (`@Total <= limit`) under a requirement | `value`, `unit` | Procurement |
| Mass item, `cad_mass.json` `mass_basic_kg`, `cg_x_m`, `cg_y_m`, `cg_z_m`, `I_cad_axes_kgm2` (Ixx, Iyy, Izz) | `attribute` on the Aircraft part | `value`, `unit` kg, m, kg*m^2 (array possible) | Design/Aircraft |
| Per-part mass and CG (viewer-data `mass_g`, `cg_xyz_m`) | child `attribute` on each part | unit g and m; aircraft frame x aft, y right, z up | the part |
| Mass roll-up and CG | parent attribute with an equation over `@` children (Python Code object for the CG moment sum) | `value` equation | Aircraft |
| `params-A.json` groups (env, req, mass, cg, prop, mission, yaw, sim, servo, struct, linkage) | one `package` per group, one `attribute` per parameter | `value`, `unit` | Design/Parameters |
| CAD part, viewer-data `parts[]` (id, name, subsystem, status, mass_g, material, cg_xyz_m, make_or_buy, vendor, vendor_url, qty, unit_cost_usd, process) | `part` (shortName = id); `material` as a `material` object or attribute (kind string) | see attributes above; `make_or_buy`, `status`, `process` as string attributes | Design/Aircraft/<subsystem> |
| CAD geometry | `geometry` (kind `step` or `code`) per part, or one `assembly` | kind; file upload route not found | the part |
| Interfaces, viewer-data `edges[]` (part_a, part_b, via, owner) | `interface` or `port` objects, plus a relationship (Connect or Mechanical) | `kind` inout | Design/Aircraft |
| Hard constraints, `docs/requirements.md` and `CLAUDE.md` | `requirement` (shortName = R-id) with `constraint` children | `documentation` = text, constraint `value` equation, `kind` | Requirements |
| `REQUIREMENTS-A.md` rows (ID, Requirement, Class, Disp, Basis) | `requirement` (shortName = ID), Class and Disp in `documentation` or tags | as above | Requirements/<section 1..6> |
| Test plan item, `TEST-PLAN-O4B.md` TP-n | `test` (shortName = TP-n) | `category`, `status` pending, `weight`, `procedure`, `evaluationCriteria`; link to requirement by `verify` relationship | Verification |
| Proof-graph `requirement`, `test`, `source`, `assumption` nodes (claims.a0_base.json) | `requirement`, `test`, `reference`, `attribute` | test `verifies` becomes a relationship | Requirements, Verification, Library |
| Proof-graph `claim` nodes (value, unit, limit, verifies, parts) | `constraint` (value equation `value <= limit`, kind analysis) owned by the requirement, with a value `attribute` | status derived by DaVinci from the equation | Requirements |
| Proof-graph `calculation` nodes (script, function, equation, inputs, outputs) | `code` object (language python) holding the function, or an `attribute` with the equation | `language`, `code` | Verification/Calculations |
| Decision, CHANGE-LOG D-entry | `document` (body record, shortName = D-nnn) or `task` with `documentation`; not an engineering object | shape of `body` not found | Decisions |

## 5. Unknowns and constraints on the mapping

- Inner shape of `document.body`, `test.procedure`, `evaluationCriteria`: not found. Read one object with GET tree / Core ReadObject, or create it once in the UI, before bulk writes.
- Relationship creation over REST: not found (see s2).
- GLB/STEP upload to a geometry object over the API: not found. Part-level mass and CG as attributes avoids needing it.
- Objects are re-used by parent + name + type in the Python Database API, which gives idempotent re-sync (docs: python-database-api.md). Over REST, client-minted UUIDs must be stable: derive them with uuid5 from the source id.
- Writes need a commit to reach git; push to a branch only, never `main`.

Sources opened: see the list at the end of `davinci-research.md`.
