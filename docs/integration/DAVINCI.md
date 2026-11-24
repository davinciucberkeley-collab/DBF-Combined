# DaVinci API: summary of the attempt (T-037, R-INT-04, spec 8.3)

Date: 2026-11-24. This page is the T-037 output: capabilities, the workflow attempted with authorised access, the real cost, the failures and the agreed workflow. Detail and raw evidence: [davinci-findings.md](davinci-findings.md) (probes, imports, storage, spend), [davinci-import-2026-11-23.md](davinci-import-2026-11-23.md) (first import, STEP method), [davinci-mapping.md](davinci-mapping.md), [davinci-research.md](davinci-research.md).

## 1. Access (authorised)

- **Tokens:** personal access tokens created by Dillon (AM-045, AM-046, AM-055). They are kept in the git-ignored `.env` and never printed or committed.
  - Scopes: projects:read / write, sessions:manage, usage:read. There is no agent:message scope, so DaVinci's AI agent cannot be run.
  - A one-day projects:manage token was used once (AM-055); its value was removed from `.env` afterwards.
- **Projects:**
  - "API Test" (2026-11-23), deleted by Dillon on 2026-11-24.
  - "Concept A" (id bbb1b6e0-63d1-4a95-8e6d-0e300beed2c9, design-build-fly org) since 2026-11-24.
  - All writes went to scratch branches; main was never written.

## 2. Capabilities (from the docs and from use)

| Works over REST with a token | Evidence |
|---|---|
| List projects, read the object tree, read usage | probe 1, findings s7 |
| Create branches and sessions; add objects (requirements, parts, attributes, tests, packages); commit | probe 2, findings s8; imports 2026-11-23 / 24 |
| Run DaVinci tools directly (`invokeTool`, e.g. Core / ReadObject), no LLM | probe 2; import read-back checks |
| Upload a STEP file as a geometry object with a 3-D preview | STEP test (hub), 129-part import |

What it does not do for us:
- No aerodynamics or flight-dynamics analysis, so SITL and the landing model stay in the repo (research doc).
- No MCP connector; REST is the route.

## 3. What was attempted

**On 2026-11-24, into Concept A, branch `concept-a-snapshot-2aba012d`:**
1. Design data at git 2aba012d (`tools/davinci_import_a.py --project ... --sha 2aba012d`):
   - BOM with costs;
   - parts with CAD masses;
   - the REQUIREMENTS-A requirements;
   - the TEST-PLAN-O4B tests;
   - hard constraints.

   Every POST returned 201, the commit 201, and five ReadObject read-backs 200.
2. All 129 CAD parts as full-detail faceted STEP files, in one package per subsystem. Results: 129 geometries, 0 missing, 0 duplicates; commit bf0a3803.
3. A 10-sub-assembly assembly holding all 129 parts (uploaded again into it), committed. It does not render (see s5).
4. Whole-aircraft STEPs (one geometry each):
   - full 25.4 MB;
   - lite 12.7 MB, about 25 % of the triangles: **this one renders** (Dillon, 2026-11-24);
   - extra-lite 4.8 MB.

   The lite and extra-lite versions are made with `tools/blender_decimate_whole.py` then `tools/mesh_to_step.py` (findings, last bullets).

**Earlier (2026-11-23, API Test, now deleted):** the first data import (367 objects) and the GLB and STEP tests.

## 4. Real cost

- **AI chat / agent:** none. The token cannot call the agent.
- **Indexing:** creating objects triggers DaVinci's own embedding calls (text-embedding-3-small).
  - They are charged per call to the prepaid balance: "<$0.01" each (Dillon's billing page, 2026-11-24).
  - The displayed balance did not change across all the Concept A imports, so **the total is under one cent**.
  - Dillon accepted this cost (AM-063), replacing the AM-003 $0 line for this work.
- **The usage API missed these charges:** `/api/v2/usage` stayed at $49.060351 / 1,093 events with asOf 2026-11-09 throughout. Use the billing page, not that endpoint, to watch cost.
- **Storage:** Concept A read 1,056,091,993 bytes (1.06 GB) after all uploads and compile attempts, of the 50 GB the account now has (raised by Celedon, 2026-11-24).
  - Storage per object is the cost driver: one 25 MB STEP cost about 27 MB, while 129 small STEPs (23.6 MB) cost about 396 MB.

## 5. Failures and limits found

| What | Result | Work-around |
|---|---|---|
| Delete a branch with a token | `BRANCH_NOT_FOUND` by name; 403 `CREDENTIAL_NOT_PERMITTED` (web login only); the web-app delete also failed | Delete the project instead; make few branches |
| Storage | 1 GB account limit hit: 413 `STORAGE_LIMIT_EXCEEDED`, storageUsedBytes 1,073,743,780 of 1,073,741,824 (836 MB in API Test from 205 STEP objects); deleting objects did not lower the used figure (davinci-import-2026-11-23.md s3); after the project delete the account still read 1,073,801,516 then 1,074,121,747 on two refused 70 / 390 KB uploads until Douglas cleared it (findings) | Limit raised to 50 GB; budget storage per object |
| Assembly view | Compile: "source is required"; assembly source format undocumented; no object-update endpoint | Whole-aircraft STEP as one geometry |
| Full-detail whole-aircraft STEP (25 MB, 54k faces) | `CAD_OCCT_ERROR: socket hang up` on Compile | Lite version (12.7 MB) renders |
| Upload | Two HTTP 500 replies (body unreadable) mid-batch | The idempotent re-run completed it |
| Object names | The `objectName` sent with an upload is not applied (the file name is used) | Rename in the web app if wanted |
| Look | Faceted parts show triangle edges (the CAD is mesh-based) | Accepted; true B-rep would need a solid-CAD rebuild |
| Usage endpoint | Did not show the indexing charges | Billing page |

## 6. Agreed workflow (approved by Dillon, AM-063)

1. **After each design change** that should be visible in DaVinci, Claude runs `tools/davinci_import_a.py --project <Concept A id> --sha <commit>` onto a new branch `concept-a-snapshot-<sha>`.
2. **When geometry changed**, also:
   - the per-part STEPs (`tools/mesh_to_step.py`, `davinci_step_upload.py`);
   - the lite whole-aircraft STEP.
3. **DaVinci's AI agent is never used.** Tokens carry no agent:message scope. Claude does the reasoning; DaVinci stores and runs tools.
4. **main is changed only on purpose**, by a person.
5. **Cost is checked on the billing page** after large imports.
6. Not yet: the dbf-hangar adapter (AM-038 "not yet"). The hangar `plane davinci push / pull` would wrap steps 1-2.
