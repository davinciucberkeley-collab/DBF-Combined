# Requirements registry — master program (spec of 2026-11-18)

Source of every row: `docs/MASTER_PROJECT_SPEC.md` (section given in **Src**) or `docs/spec-amendments.md`
(AM-nnn). The verbatim text lives there; **Requirement** quotes or closely restates the line it comes from,
**Interpretation** says how this repo meets it. IDs are stable: never renumber or delete a row; a dropped or
superseded requirement keeps its row with status `EXPLICITLY DEFERRED` / `SUPERSEDED BY …`.
Tasks: `docs/task-ledger.md`. Audit: `python -I tools/ledger_audit.py`.

Priority: P0 process-critical, P1 core deliverable, P2 improvement. Owner = role (model): **C** conductor
(main session, Opus), **H** haiku subagent, **S** sonnet subagent, **O** opus reviewer subagent, **D** Dillon.
Status is the requirement's roll-up: `VERIFIED COMPLETE` only when every task under it is.

Project hard constraints in `CLAUDE.md` (budget, schedule, trunk, 3-D gates, CAD fidelity, wiring) bind every row.
The aircraft is **concept A** (D-182); K09-L material is the record only.

## Part 1 — Prompt preservation
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-PRES-01 | 1.1 | Save the complete, unabridged prompt as `docs/MASTER_PROJECT_SPEC.md`, committed | Verbatim paste, no header added inside the file | P0 | — | C | File equals pasted text; in git | diff vs paste; `git log -- docs/MASTER_PROJECT_SPEC.md` | VERIFIED COMPLETE |
| R-PRES-02 | 1.1 | Do not overwrite / summarise / let subagents or cleanup modify the spec; auditable changes | SHA-256 seal + audit; CLAUDE.md rule; protected list in repository-audit | P0 | R-PRES-01 | C | Audit fails if spec edited | edit a copy, run audit, see FAIL | VERIFIED COMPLETE |
| R-PRES-03 | 1.1 | Store later instructions verbatim with their relation; record supersession, never delete | `docs/spec-amendments.md` append-only (prefix sealed) | P0 | R-PRES-01 | C | AM-001 stored verbatim | audit checks sealed prefix | VERIFIED COMPLETE |
| R-PRES-04 | 1.2 | Integrate spec with CLAUDE.md; keep it concise; import or mandatory pointer; verify | Pointer (not `@` import: spec ≈ 9k words every turn) + SessionStart hook brief | P0 | R-PRES-01 | C | New session context names the spec and recovery steps | headless `claude -p` asks where the spec is | IN PROGRESS |
| R-PRES-05 | 1.3 | Create/update the eight management files | Created under `docs/`; engineering-decisions indexes the existing `redesign/params/CHANGE-LOG.md` | P0 | — | C | All eight exist, non-empty | `ls docs/` + audit "missing" list | VERIFIED COMPLETE |
| R-PRES-06 | 1.4 | PreCompact hook: verify state files, preserve checkpoint, log event, no inferred state | `.claude/hooks/recovery.py pre-compact` | P0 | R-PRES-05 | C | (1) state files checked, missing listed (2) checkpoint snapshot copied (3) event logged (4) ledger untouched by the hook (5) hook writes no conversation-derived state | manual compaction test, each item | VERIFIED COMPLETE |
| R-PRES-07 | 1.4 | SessionStart(compact): reload instructions, restore task state, show unfinished work, start reconciliation | same script, `session-start`, matcher `compact` | P0 | R-PRES-05 | C | Brief after compaction names (1) CLAUDE.md/spec paths (2) recovery procedure (3) in-progress tasks (4) audit result to reconcile | manual compaction test, each item | VERIFIED COMPLETE |
| R-PRES-08 | 1.4 | SessionStart(startup, resume): same context | matcher `startup|resume|clear` | P0 | R-PRES-07 | C | Brief appears in a new session | headless new session | VERIFIED COMPLETE |
| R-PRES-09 | 1.4 | PostCompact when supported | Supported in Claude Code 2.1.x; logs only | P2 | — | C | Log line after compaction | manual compaction test | VERIFIED COMPLETE |
| R-PRES-10 | 1.5 | Eleven-step recovery procedure; compaction summary never authoritative | Written in `session-state.md`; hook points to it | P0 | R-PRES-05 | C | Procedure on disk and referenced by hook | read hook output | VERIFIED COMPLETE |
| R-PRES-11 | 1.6 | Controlled manual compaction test, recorded | `/compact` in a headless resumed session | P0 | R-PRES-06..09 | C | Seven checks of spec 1.6 each recorded: spec exists, instructions reload, active task identified, statuses kept, plan recoverable, IDs intact, work resumes | session-log + transcript answer per check | VERIFIED COMPLETE |
| R-PRES-12 | 1.6 | Test a new or resumed session | headless `claude -p` new session | P1 | R-PRES-08 | C | Agent names active task and spec path unprompted-by-content | transcript answer | VERIFIED COMPLETE |

| R-PRES-13 | 1.2, 1.4 | Inspect existing CLAUDE.md, AGENTS.md, config and installed Claude Code hook support; preserve valid instructions | CLAUDE.md kept whole (sections prepended); no AGENTS.md at the root; no prior .claude/settings.json; Claude Code 2.1.288 | P1 | — | C | Inspection recorded with what was kept | session-state + `git diff a93f14da -- CLAUDE.md` | VERIFIED COMPLETE |

## Master directive and immediate-execution rules (audit 2026-11-18 A1, A2, A5, A16, A17)
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-GEN-01 | Directive; 7.6 | Use Superpowers for planning, implementation and testing; Impeccable for UI and presentation audits; other tools when better | Superpowers skills for plans/TDD/verification; Impeccable on changed Explorer pages and overlay design | P2 | — | C | Phase plans name the skill used; one Impeccable audit of changed pages | session-state + audit file | IN PROGRESS |
| R-GEN-02 | Immediate execution | No irreversible changes, unapproved costs or overridden approvals | Deletions, history rewrites, purchases, paid APIs, installs of new executables, pushes go to Dillon first; AM-029 (worktree removal approval), AM-030 (no test-equipment purchase; borrow a frame, else lever rig) | P0 | — | C | Every such action has a recorded approval | session-state Approvals + git log | IN PROGRESS |
| R-GEN-03 | 8.4 | Consistent design language | Reuse `redesign/design-system/` tokens in Explorer changes and video overlays | P2 | — | S | Overlays and pages use the tokens | review | NOT STARTED |
| R-GEN-04 | 1.2, 1.5 | Full-spec reconciliation at milestones, recovery audits, final verification | Milestone audits read the whole spec | P0 | R-TRK-05 | H/O | Each milestone audit states it read the full spec | audit file | VERIFIED COMPLETE |
| R-GEN-05 | Directive; 4.1 | Do not start from scratch; preserve existing working capabilities and functioning systems | Cleanup and redesign keep every working gate and tool (collide, assembly_check, render, browser pages); removal needs a recorded reason (spec 4.1, Directive) | P0 | — | C | No working capability removed; T-044 and final regression show the same gates run | regression list T-044 / T-049 | IN PROGRESS |
| R-GEN-06 | AM-008 | The aircraft is designed by Claude and built by the students; no commercial kit airframe | Airframe parts are designed here and bought as stock or made; the ZOHD Altus kit is withdrawn (AM-008, D-218 reversed) | P0 | — | C | No kit airframe in the BOM or design record | BOM-A.csv + CHANGE-LOG review | IN PROGRESS |
| R-GEN-07 | CLAUDE.md hard constraints; AM-010..AM-021 | Budget test: total including the crash reserve (by definition) <= $2,000; no purchase before early December; team phones, laptop and Jacobs tools are free; no supplied materials | AM-011 / AM-012 / AM-013 / AM-014 / AM-015 / AM-018 / AM-019 / AM-020 as recorded in spec-amendments.md; reserve defined in AM-018 | P0 | — | C | `bom_a.py` total incl. reserve <= $2,000 at every milestone | run bom_a.py (T-092: $1,939.17) | IN PROGRESS |
| R-GEN-08 | AM-011 | Weight over the mass gate does not stop the initial design; physics checks apply at the predicted mass | The mass gate may be missed (AM-011); budget stays hard; stability, T/W, window and structure are checked at predicted mass | P1 | — | C | Each milestone states the predicted mass and every physics check at that mass | T-083 / T-092 reports (CL-A-MASS-PRED) | IN PROGRESS |

## Part 2 — Persistent task tracking
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-TRK-01 | 2.1 | Registry of every actionable requirement with the nine fields; no lumping (video decomposed) | this file | P0 | R-PRES-01 | C | Every spec section 1–13 + rules + AM-001 has rows | haiku audit `docs/audits/2026-11-18-ledger.md` found gaps, fixed 2026-11-18; O re-review pending | VERIFIED COMPLETE |
| R-TRK-02 | 2.2 | Task ledger with nine fields and the seven statuses; only VERIFIED COMPLETE counts; never delete tasks | `docs/task-ledger.md` | P0 | R-TRK-01 | C | Audit parses all rows, statuses valid | `ledger_audit.py` | VERIFIED COMPLETE |
| R-TRK-03 | 2.3 | Traceability requirement→task→implementation→test→evidence→status; automated detection of missing links | `tools/ledger_audit.py` | P0 | R-TRK-02 | C | Audit exits 1 on an orphan requirement / unevidenced VERIFIED | seed a broken row in a copy | VERIFIED COMPLETE |
| R-TRK-04 | 2.4 | Pre-task and post-task protocol; partial completion stays open | CLAUDE.md working rule + subagent brief template in execution-plan | P0 | R-TRK-02 | C | Every delegated brief carries task ID, acceptance, evidence path | spot check ledger vs briefs | VERIFIED COMPLETE |
| R-TRK-05 | 2.5 | Independent requirement audits at phase ends, handoffs, recovery, before closing, final | `ledger-auditor` (haiku) for accounting, `eng-reviewer` (opus) for technical | P0 | R-TRK-02, R-ORC-01 | H/O | Audit records in verification-report | report entries dated per milestone | VERIFIED COMPLETE |
| R-TRK-06 | 2.6 | No premature termination; reconcile before stopping; record blockers exactly | CLAUDE.md rule; wrap-up reconciles ledger | P0 | R-TRK-02 | C | Final message lists every non-VERIFIED requirement | read session end | VERIFIED COMPLETE |

## Part 3 — Model routing and orchestration
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-ORC-01 | 3.1 | Route Haiku / Sonnet / Opus by task type; best alternatives if unavailable | `.claude/agents/*.md` with `model:` frontmatter; routing table in execution-plan | P1 | — | C | Agents load and run on the named model | run one haiku agent, check model in result | VERIFIED COMPLETE |
| R-ORC-02 | 3.2 | Conductor plans/delegates/integrates/verifies; avoids routine implementation | Main session = conductor; implementation delegated | P1 | R-ORC-01 | C | model-usage log shows delegation | `docs/model-usage.md` | VERIFIED COMPLETE |
| R-ORC-03 | 3.3 | Twelve delegation rules (plan, split, cheapest capable, parallel, no conflicting edits, worktrees, evidence, escalate, diagnose, review, merge on acceptance, keep status) | Written into execution-plan; worktrees for code-writing agents | P1 | R-ORC-01 | C | Rules on disk; followed in model-usage log | O-review | VERIFIED COMPLETE |
| R-ORC-04 | 3.3 | Use James's shared agent definitions; no conflicting framework | Search repo + user/global agents; none found 2026-11-18 → ask James / Dillon for location | P2 | — | D | Definitions located and adopted, or recorded as absent | `ls .claude/agents ~/.claude/agents`; repo search | BLOCKED |
| R-ORC-05 | 3.4 | Track model, complexity, outcome, usage, retries, escalation, review result; periodic review | `docs/model-usage.md` append-only table | P2 | R-ORC-01 | C | One row per delegated task | audit at milestones | VERIFIED COMPLETE |

## Part 4 — CAD audit and realism (concept A)
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-CAD-01 | 4.1 | Baseline: configuration, assemblies, control surfaces, propulsion, actuators, connections, structure, wiring, connectors, sim methods, constraints; what works vs unverified | `docs/capability-audit.md` | P1 | — | S | Every listed item has a row with evidence path | O spot-check | VERIFIED COMPLETE |
| R-CAD-02 | 4.2 | Joints, hinges and mechanism linkages modelled functionally (elevon hinge line, horn, pushrod, servo arm) | Concept A elevon drive; real geometry from vendor drawings | P1 | R-CAD-01 | S | Hinge axis, horn hole, pushrod length consistent; no stand-ins | kinematic check R-PHY-03 | IN PROGRESS |
| R-CAD-03 | 4.2 | Motor/actuator mounts, fasteners, structural interfaces realistic | Use existing D-202…D-210 hub/arm work; fill gaps found by R-CAD-01 | P1 | R-CAD-01 | S | Gap list closed or logged | collision gate + review | IN PROGRESS |
| R-CAD-04 | 4.2 | Wiring and connectors realistic and enclosed (CLAUDE.md wiring rule) | wire inventory exists (`qp/A/cad/wire_inventory.py`) | P1 | R-CAD-01 | S | Exposed-length list current | run wire_inventory | IN PROGRESS |
| R-CAD-05 | 4.2 | Assembly clearances and manufacturing feasibility | build-step gate + drawings (D-211) | P1 | R-CAD-01 | S | Gate passes; manufacturability notes per made part | `assembly_check`/`collide_a` | VERIFIED COMPLETE |
| R-CAD-06 | 4.3 | Consistency (alignment, connection geometry, motion clearance, materials); document simplifications | Simplifications list in capability-audit | P1 | R-CAD-02..05 | O | Review finds no unexplained inconsistency | O review | VERIFIED COMPLETE |

## Part 5 — Real physics and mechanism validation
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-PHY-01 | 5.1 | Inventory real analysis methods and the code/software actually used; never infer from a "pass" | In capability-audit: each method → script → solver → last run | P0 | — | S | Each claimed analysis traced to code that computes it | O spot-check reruns | VERIFIED COMPLETE |
| R-PHY-02 | 5 | Correct the "physics check" that was only static collision | Rename/relabel in CLAUDE.md, README, Explorer, reports | P0 | R-PHY-01 | S | No doc calls collision a physics simulation | grep for "physics" claims | VERIFIED COMPLETE |
| R-PHY-03 | 5.2 | Mechanism kinematic validation (elevon servo→horn→pushrod→hinge) through full range | Planar/3-D linkage solve with constraint residuals | P1 | R-CAD-02 | S | Range, linkage ratio, no toggle/over-centre, residual < 1e-6 | rerun script | IN PROGRESS |
| R-PHY-04 | 5.2 | Rigid-body dynamics of an important mechanism / takeoff-landing event (frictionless first) | e.g. elevon + servo torque dynamics, or tailsitter fin-tip touchdown/tip-over (MuJoCo/PyBullet/own integrator) | P1 | R-PHY-03 | S | Time history with energy/constraint checks; pass/fail vs limits | rerun + O review | VERIFIED COMPLETE |
| R-PHY-05 | 5.2 | Collision detection during motion (swept, not only static) | Sweep elevon / prop disc through range against CAD meshes | P1 | R-PHY-03 | S | Min clearance over sweep ≥ limit | rerun | IN PROGRESS |
| R-PHY-06 | 5.3 | Separate interference / kinematics / rigid-body / FEA / CFD / flight dynamics / illustrative animation | Category column on every analysis record; video labels | P0 | R-PHY-01 | C | Every record carries one category | grep records | VERIFIED COMPLETE |
| R-PHY-07 | 5.4 | Reproducible record: solver, model version, inputs, assumptions, BCs, settings, outputs, criteria, result, limits | `docs/analysis-records.md` one block per analysis | P1 | R-PHY-03 | S | Each new analysis has all ten fields | audit | VERIFIED COMPLETE |
| R-PHY-08 | 5.2 items 2, 8 | Motors/actuators validated: servo torque and speed vs hinge load through the linkage; motor/prop mechanical check | Servo part in T-019; motor mount: cite D-209 FEA record | P1 | R-PHY-03 | S | Servo margin vs hinge moment computed; motor mount evidence cited | rerun | IN PROGRESS |
| R-PHY-09 | 5.2 item 8 | Takeoff/landing mechanism: tailsitter fin-tip touchdown and tip-over | Existing `qp/A/structures/landing_a.py` 6-DOF touchdown; re-run and record | P1 | R-PHY-01 | S | Record with pass/fail vs C5 limits | rerun | IN PROGRESS |
| R-PHY-10 | 5.1, 7.3 S5 | Verified FEA/CFD/flight-dynamics results available for review and film Scene 5 | Re-run or confirm reproducible the concept A FEA (D-209 arm/cup) and one SITL transition; record per R-PHY-07 | P1 | R-PHY-07 | S | Records with reproduction command | rerun | VERIFIED COMPLETE |
| R-PHY-11 | 5.2 item 1 | Wing and flap mechanisms | Concept A has no flaps (D-182); the elevons are its only wing mechanism, covered by R-PHY-03/04/05 (PD-005) | P1 | R-PHY-03 | C | PD-005 logged | read | VERIFIED COMPLETE |

## Part 6 — Design optimization discipline
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-OPT-01 | 6.1 | On a failure consider subtract → modify → rearrange → change approach → add | Ladder in engineering-decisions; each fix decision cites which rung | P1 | — | C | New D-entries show ladder | review of new decisions | IN PROGRESS |
| R-OPT-02 | 6.2 | Compare alternatives on mass, structure, function, reliability, manufacture, assembly, aero, constraints | Trade table template | P1 | R-OPT-01 | O | Major decisions carry a trade table | review | IN PROGRESS |
| R-OPT-03 | 6.3 | Function before mass; mass tracked through iteration | Mass delta column per decision | P1 | — | C | Mass roll-up current after each change | `MASS-GATE.md` rerun | VERIFIED COMPLETE |
| R-OPT-04 | 6.4 | Research benchmarks/literature; compare several concepts | Cite sources with dates | P2 | — | S | Each major mechanism decision cites ≥1 benchmark | review | IN PROGRESS |
| R-OPT-05 | 6 | Retro-review: D-202…D-210 FEA fixes that added material — could subtraction/rearrangement have worked? | One-off review of recent adds; AM-016: limits not relaxed; bench test of 2026-12-15 decides | P2 | R-OPT-01 | O | Findings logged; actions as new D-entries | review | IN PROGRESS |

## Part 7 — Video (decomposed)
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-VID-01 | 7.1 | Audit existing video pipeline (files, renderer, cameras, lights, materials, imports, scripts, overlays, export, bottlenecks) | `docs/video/PIPELINE-AUDIT.md` | P1 | — | S | Every listed item covered | O read; O read done 2026-11-23, `docs/audits/2026-11-23-review-round-6a.md`, all 11 items covered | VERIFIED COMPLETE |
| R-VID-02 | 7.2 | Geometry from current concept A CAD (source of truth) | Build via `blender_backend` from `qp/A/cad/model` | P1 | R-VID-01 | S | Frame matches CAD export | frame compare | VERIFIED COMPLETE |
| R-VID-03 | 7.2 | Material realism, lighting, shadows, surface finish | Cycles or EEVEE-Next with HDRI/area lights | P1 | R-VID-01 | S | Reviewer passes lighting/material checklist | frame review | VERIFIED COMPLETE |
| R-VID-04 | 7.2 | Camera movement and composition (smooth, eased, motivated) | Spline cameras, no cuts mid-move | P1 | R-VID-01 | S | No jerk (camera accel bounded) | per-frame camera path check | VERIFIED COMPLETE |
| R-VID-05 | 7.2/7.5 | Animation smoothness and accuracy (constraints, connected parts, no unintended intersection, consistent paths) | Drive mechanism from R-PHY-03 output | P1 | R-PHY-03 | S | (1) poses come from the kinematic solve (2) servo arm visibly drives rod and horn (3) linked parts stay connected (<= 0.05 mm gap) (4) no penetration along the path (5) camera shows the linkage | per-item check on rendered poses | VERIFIED COMPLETE |
| R-VID-06 | 7.2 | ≥1080p, 60 fps when practical | 1920×1080 @ 60 | P1 | — | S | ffprobe shows 1920×1080, 60 fps | ffprobe | VERIFIED COMPLETE |
| R-VID-07 | 7.3 | Six scenes: overview, CAD inspection, mechanical operation, physics validation, engineering analysis, final | Shot list in pipeline doc | P1 | R-VID-01 | S | Per scene: S1 whole aircraft + configuration; S2 close-ups of wing, propulsion, interfaces, structure, controls; S3 actuator-horn-hinge motion with close-up/cutaway; S4 executed-sim results; S5 verified FEA/other results; S6 final overview | shot-by-shot timeline review | VERIFIED COMPLETE |
| R-VID-08 | 7.4 | Restrained labels, arrows, dimensions, exploded/transparent views, overlays, metrics, revision, pass/fail | Overlay layer from analysis records only | P1 | R-PHY-07 | S | Every on-screen number traces to a record; labels, arrows, one exploded and one transparent view, revision tag, pass/fail tags present; reviewer judges it uncluttered and clear to a newcomer | O review checklist | VERIFIED COMPLETE |
| R-VID-09 | 7.3/7.5 | Simulated motion distinguished from illustrative; sim drives motion where feasible | On-screen tag "SIMULATED (script)" / "ILLUSTRATIVE" | P0 | R-PHY-06 | S | Every motion shot tagged | review | VERIFIED COMPLETE |
| R-VID-10 | 7.6 | Independent visual + technical review of frames and final video; previews before full renders | Contact sheets → reviewer agent → fixes | P1 | R-VID-07 | O | Review log with defects closed | review log | VERIFIED COMPLETE |
| R-VID-11 | 7.7 | Main video 60–120 s | `a-demo.mp4` | P1 | R-VID-02..10 | S | Exists, plays, duration in range | ffprobe + decode test | VERIFIED COMPLETE |
| R-VID-12 | 7.7 | Highlight video 20–30 s | `a-highlight.mp4` | P1 | R-VID-11 | S | Exists, plays, duration in range | ffprobe + decode | VERIFIED COMPLETE |
| R-VID-13 | 7.7 | Mechanism demonstration clips | one per mechanism | P1 | R-VID-05 | S | Exist, play | ffprobe + decode | VERIFIED COMPLETE |
| R-VID-14 | 7.7 | Rendering-pipeline documentation + summary of improvements | `docs/video/PIPELINE.md` | P1 | R-VID-11 | H | Doc reproduces render | follow doc once | VERIFIED COMPLETE |
| R-VID-15 | 7.7/12.4 | Independent playback and visual verification results recorded | full decode with ffmpeg `-f null`, frame review | P0 | R-VID-11..13 | O | 0 decode errors; review passed | verification-report | VERIFIED COMPLETE |

## Part 8 — Team integration
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-INT-01 | 8.1 | Use the team's shared aircraft file format; import/modify/export without code changes | Locate schema (not in repo 2026-11-18); concept A has `params-A.json` / `A.param` | P1 | — | D/S | Concept A expressed in the shared schema, round-trips | load-modify-save test | BLOCKED |
| R-INT-02 | 8.2 | Agent loop: load design, change parameter, run tests, interpret, compare, save, evidence | Thin wrapper over existing `qp/A` scripts or the team CLI (`tools/vtol.py`?); reuse `tools/vtol.py` / team CLI, do not duplicate it (spec 8.2) | P1 | R-INT-01 | S | One documented end-to-end run | rerun | NOT STARTED |
| R-INT-03 | 8.2 | OpenCAE integration where appropriate | `tools/opencae-studio` exists; map which concept A analyses it can run | P2 | R-INT-02 | S | One concept A case run in OpenCAE or reason recorded | run log | NOT STARTED |
| R-INT-04 | 8.3 | DaVinci API: capabilities, attempt full design-build workflow with authorized access, real cost, failures | Needs API access + cost approval from Dillon | P1 | — | D | Findings doc; attempt logged | doc review | BLOCKED |
| R-INT-05 | 8.4 | No new standalone dashboards; integrate into the existing Explorer (`redesign/site`) | Results go into existing pages | P0 | — | C | No new interface added | repo diff review | IN PROGRESS |
| R-INT-06 | 8 | Centralized viewer and weekly reporting artifacts supported | Explorer + phone status page; weekly report format from team | P2 | R-INT-05 | D/S | Weekly report produced from ledger | — | IN PROGRESS |

## Part 9 — Repository cleanup and performance
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-REPO-01 | 9.1 | Inventory; large files/dirs; baseline size and metrics | `repository-audit.md` §Baseline | P1 | — | H | Sizes measured with commands shown | rerun commands | VERIFIED COMPLETE |
| R-REPO-02 | 9.2 | Classify Protected / Regenerable / Obsolete / Uncertain | Candidate table | P1 | R-REPO-01 | S | Every candidate classified with reason | O review | VERIFIED COMPLETE |
| R-REPO-03 | 9.3 | Safe procedure: git state, checkpoint, branch, dry-run plan, approval for ambiguous/irreversible, batches, regression after each, restore | Cleanup branch `cleanup/initial`; dry-run first; Dillon approves deletions; AM-029 batch 3 | P0 | R-REPO-02 | C/D | Dry-run plan approved before any delete | git log | VERIFIED COMPLETE |
| R-REPO-04 | 9.4 | Consolidate duplicate pipelines, wrappers, conversions, interfaces, validation, configs, agent instructions, renderers, docs | Findings list → batches | P2 | R-REPO-02 | S | Each consolidation keeps regression tests green | tests | VERIFIED COMPLETE |
| R-REPO-05 | 9.5 | Measure and optimize CAD/sim, render, agent, software performance with real measurements | Benchmarks table before/after | P2 | R-REPO-01 | S | Numbers with commands | rerun | VERIFIED COMPLETE |
| R-REPO-06 | 9.6 | Context efficiency: concise entry points, targeted retrieval, no duplicate instructions | Shorter CLAUDE.md core, pointers | P1 | — | C | CLAUDE.md size measured before/after | wc | IN PROGRESS |
| R-REPO-07 | 9.7 | Logical structure; .gitignore regenerable artifacts; no risky moves | Ignore caches/__pycache__; stale worktrees | P2 | R-REPO-02 | S | .gitignore updated; paths still work | tests | VERIFIED COMPLETE |
| R-REPO-08 | 9.8 | Post-cleanup verification (CAD loads, sims run, renders work, integrations, agents, prompt preservation, recovery, requirements intact) | Regression script list | P0 | R-REPO-03 | H | All checks green | logs; 9.8 items collide/assembly/render/browser/recovery/prompt preservation re-run in T-049 | IN PROGRESS |
| R-REPO-09 | 9.9 | `docs/repository-audit.md` with all twelve sections | — | P1 | R-REPO-01..08 | H | All sections filled | audit | VERIFIED COMPLETE |
| R-REPO-10 | 9.10 | Initial audit now; final audit at the end; light checks between | — | P2 | — | C | Two dated audits | report | IN PROGRESS |

## Part 10 — Monitoring and recovery
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-MON-01 | 10.1 | Persist active tasks, agents, state, deps, progress, errors, blocks outside conversation | `session-state.md` + ledger | P0 | R-PRES-05 | C | Updated at each milestone | read | VERIFIED COMPLETE |
| R-MON-02 | 10.2 | Detect stalls, retries, loops, conflicting edits, scope drift (cheap checks) | Retry count in model-usage; background-job timeouts | P1 | R-MON-01 | C | Stall rule written; applied | log | IN PROGRESS |
| R-MON-03 | 10.3 | Nine-step failure recovery; never silently abandon | Failures logged in session-state "Failed attempts" | P1 | R-MON-01 | C | Every FAILED task has diagnosis | audit | IN PROGRESS |
| R-MON-04 | 10.4 | Persist goal, requirements, done, pending, failures, decisions, next action before handoff/compaction | session-state sections | P0 | R-MON-01 | C | All seven sections present | read | VERIFIED COMPLETE |

## Part 11 — Plan; Part 12 — Final verification
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-PLAN-01 | 11 | Dependency-aware phased plan (Superpowers or equivalent), phases 1–8, nothing silently removed | `execution-plan.md` | P0 | R-TRK-01 | C | Every requirement appears in a phase | audit | VERIFIED COMPLETE |
| R-VER-01 | 12.1 | Independent final requirement-by-requirement audit with stats from VERIFIED only | `verification-report.md` final section by O reviewer | P0 | all | O | Table for every R-id | read | NOT STARTED |
| R-VER-02 | 12.2 | Verify CAD loads, mechanisms credible, ≥1 mechanism simulated, claims = computations, reproducible, justified | — | P0 | Parts 4–6 | O | Each item evidenced | rerun | NOT STARTED |
| R-VER-03 | 12.3 | Verify routing, persistent tracking, traceability, reviews, compaction + session recovery, open tasks visible | — | P0 | Parts 1–3 | O | Each item evidenced | tests | NOT STARTED |
| R-VER-04 | 12.4 | Verify videos (exist, play, correct aircraft, motion consistent/labelled, labels accurate, reviewed, defects fixed) | — | P0 | Part 7 | O | Each item evidenced | ffprobe + review | NOT STARTED |
| R-VER-05 | 12.5 | Verify cleanup safe, protected files kept, duplication addressed, perf documented, regression green, prompt preservation works | — | P0 | Part 9 | O | Each item evidenced | tests | NOT STARTED |
| R-VER-06 | 12.6 | Reopen and fix incomplete work; record genuine blocks | — | P0 | R-VER-01 | C | No silent closures | audit | NOT STARTED |

## Part 13 — Final deliverables (mapping; audit 2026-11-18 A3)
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-DEL-01 | 13 | Every Part 13 deliverable exists. Engineering (CAD, assemblies, mechanism function, simulations, decisions, comparisons) -> R-CAD-*, R-PHY-*, R-OPT-*; AI automation (routing, orchestration, tracking, auditing, compaction and restart recovery, open-work tracking) -> R-ORC-*, R-TRK-*, R-PRES-*; video (main, highlight, clips, camera/rendering, annotations, sim visualization, review results) -> R-VID-*; repository (organized, archived, de-duplicated, measured, report, regression) -> R-REPO-*; project management (spec, registry, ledger, plan, state, decisions, verification report, list of incomplete work) -> R-PRES-05, R-VER-01 | Checklist at final verification | P0 | all | O | Each line ticked with an artifact path | final review | NOT STARTED |

## Final non-negotiable rules (spec "FINAL NON-NEGOTIABLE EXECUTION RULES" 1–20)
Each rule binds every task; it is verified by the audit/review named.
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-RULE-01 | Rules 1,2,12 | Never lose/replace/delete the spec or task records | Seal + protected list | P0 | R-PRES-02 | C | Audit green at every milestone | ledger_audit | IN PROGRESS |
| R-RULE-02 | Rules 3,4,14,20 | Never discard requirements; never mark unfinished complete; accurate status words | Ledger statuses | P0 | R-TRK-02 | C | Final audit agrees with ledger | O audit | IN PROGRESS |
| R-RULE-03 | Rule 5 | Never trust agent self-reports without evidence | Conductor re-checks evidence path | P0 | — | C | Every READY→VERIFIED step cites a check | ledger | IN PROGRESS |
| R-RULE-04 | Rules 6,7 | No expensive models for trivial work; diagnose before retry | model-usage log | P1 | R-ORC-05 | C | Log review | review | IN PROGRESS |
| R-RULE-05 | Rule 8 | Animation is never proof of physical validation | Labels R-VID-09 | P0 | R-PHY-06 | C | Review | O review | VERIFIED COMPLETE |
| R-RULE-06 | Rule 9 | Never optimize solely by adding material | Ladder R-OPT-01 | P1 | R-OPT-01 | C | Review | O review | IN PROGRESS |
| R-RULE-07 | Rules 10,11 | No unnecessary interfaces; never delete engineering files without verifying purpose | R-INT-05, R-REPO-03 | P0 | — | C | Review | diff review | IN PROGRESS |
| R-RULE-08 | Rule 13 | Performance claims need measurements | R-REPO-05 | P1 | — | C | Review | review | IN PROGRESS |
| R-RULE-09 | Rules 15–18 | Traceability; persist before handoff; reconcile after recovery; independent review of significant engineering decisions | R-TRK-03, R-MON-04, R-PRES-10, R-TRK-05 | P0 | — | C | Audits | audits | IN PROGRESS |
| R-RULE-10 | Rule 19 | Always verify exported video files | R-VID-15 | P0 | — | O | ffprobe/decode log | log | VERIFIED COMPLETE |

## AM-001 — Communication protocol (2026-11-18)
| ID | Src | Requirement | Interpretation | Pri | Deps | Owner | Acceptance | Verification | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-COM-01 | AM-001 rules 1–4 | No narration of routine actions, no repeated plans, no long summaries, no repetition | CLAUDE.md "Communication" section | P1 | — | C | Rules in CLAUDE.md, loaded every session | headless session shows rule loaded | IN PROGRESS |
| R-COM-02 | AM-001 rule 5 | No unnecessary questions; decide within permissions | Same as memory "proceed with recommendations"; AM-028 (verbatim in spec-amendments.md) | P1 | — | C | — | review | IN PROGRESS |
| R-COM-03 | AM-001 rule 6, "Agent orchestration" | Subagents save detail to files; return Task ID, outcome, verification status, evidence location, blocker | Return format in every agent definition and brief | P1 | R-ORC-01 | C | `.claude/agents/*.md` carry the format | read agent files | VERIFIED COMPLETE |
| R-COM-04 | AM-001 "When to communicate" | Message only on question, milestone, critical issue, decision, authorization, block, significant failure, completion; 1–3 sentences for routine milestones; no word limit on answers | CLAUDE.md | P1 | — | C | Rules in CLAUDE.md | read | IN PROGRESS |
| R-COM-05 | AM-001 rule 7, "Persistent enforcement" | Quality never traded for brevity; preferences survive compaction/restart/handoff; light audit only; no strict length caps | CLAUDE.md (always loaded) + SessionStart brief; no length-limiting hook | P1 | R-PRES-04 | C | Present after compaction test | R-PRES-11 test | IN PROGRESS |
| R-COM-06 | AM-001 "Final directive" | Don't pause execution for updates; resume existing scope | — | P1 | — | C | — | review | IN PROGRESS |
