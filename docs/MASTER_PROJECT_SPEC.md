UC Berkeley Design-Build-Fly — Comprehensive Aircraft Engineering, AI Automation, Simulation, Visualization, and Repository Optimization
MASTER DIRECTIVE
You are continuing development of our existing UC Berkeley Design-Build-Fly aircraft engineering project.
This is an established project with existing CAD models, engineering simulations, AI agents, visualization tools, repositories, and ongoing contributions from multiple team members.
Do not start from scratch. Preserve existing working capabilities and build upon the current project.
Your objective is to transform our current system into a reliable, physically credible, computationally efficient, and professionally presented aircraft engineering platform.
The project must address ALL of the following areas:

1. Permanent preservation of this complete prompt across context compaction and session restarts.
2. Persistent task tracking that prevents forgotten or abandoned requirements.
3. Intelligent AI model selection using Haiku, Sonnet, Opus, or the best available alternatives.
4. Improved multi-agent orchestration, delegation, and independent verification.
5. Improved physical accuracy of the existing aircraft CAD design.
6. Actual mechanical physics simulation beyond static collision checking.
7. Better engineering design optimization and decision-making.
8. Major improvements to the existing aircraft demonstration video.
9. Integration with our team's DaVinci, OpenCAE, CLI, and shared aircraft schema.
10. Comprehensive repository cleanup, consolidation, and performance optimization.
11. Continuous progress monitoring, failure detection, and recovery.
12. Independent verification that every original requirement has been addressed.

The two most important process requirements are:

* Never lose, forget, or silently discard instructions.
* Never declare completion without independently verifying the actual deliverables.

Use Superpowers for structured planning, implementation, and testing. Use Impeccable for appropriate UI, design, and presentation audits. Use other proven tools or skills when they provide a meaningful advantage.
Avoid unnecessary architectural complexity, duplicated functionality, excessive compute usage, and additional standalone interfaces.
PART 1 — PERMANENT PROMPT PRESERVATION
1.1 Save this entire prompt as the canonical specification
Before making major project modifications, create:
`docs/MASTER_PROJECT_SPEC.md`
Save the COMPLETE, UNABRIDGED text of this prompt.
Do not summarize, shorten, paraphrase, or omit requirements.
If you cannot access the entire original text, explicitly report that limitation rather than reconstructing it from memory.
This document is the canonical project specification.
Requirements:

* Commit it to version control.
* Preserve the original text.
* Do not replace it with an AI-generated summary.
* Do not overwrite it during context compaction.
* Do not allow subagents to silently modify it.
* Preserve historical requirements when amendments are introduced.
* Maintain an auditable record of changes.
* Protect it from repository cleanup operations.

Store future user instructions and amendments in a version-controlled location, preserving the exact wording and relationship to existing requirements.
If later instructions supersede earlier ones, record that decision explicitly rather than deleting the original requirement.
1.2 Integrate the specification with Claude Code's instruction system
Inspect the existing project-root `CLAUDE.md`, `AGENTS.md`, and related configuration files.
Preserve valid existing instructions.
Configure the project so Claude knows that the master specification must be consulted throughout execution.
Use Claude Code's supported file-import mechanism where appropriate:
`@docs/MASTER_PROJECT_SPEC.md`
Keep the primary project instructions concise enough to avoid excessive context overhead.
The master specification must remain intact on disk even if a shorter operational summary is loaded for routine work.
Use the full specification during initial requirement extraction, major planning, recovery audits, and final verification.
If importing the complete specification automatically would cause context-window problems, use a concise mandatory pointer combined with explicit full-specification reading and requirement reconciliation.
Verify the chosen mechanism works.
1.3 Create persistent project-management files
Create or update:

* `docs/MASTER_PROJECT_SPEC.md` — Canonical original instructions.
* `docs/requirements.md` — Every requirement, with stable identifiers.
* `docs/task-ledger.md` — Executable tasks, owners, dependencies, and status.
* `docs/execution-plan.md` — Current implementation plan.
* `docs/session-state.md` — Persistent execution checkpoint.
* `docs/engineering-decisions.md` — Major technical decisions and supporting rationale.
* `docs/verification-report.md` — Independent completion evidence.
* `docs/repository-audit.md` — Cleanup and performance optimization results.

Reuse equivalent existing files where appropriate rather than creating redundant documentation.
Treat these files as the persistent source of truth for project execution.
1.4 Implement context-compaction recovery
Inspect the installed Claude Code version and current documentation for supported session lifecycle hooks.
Where supported, configure:
PreCompact

* Verify the persistent state files are present.
* Preserve the latest existing checkpoint.
* Record the compaction event.
* Protect active task status.
* Avoid attempting to infer conversational state that was never written to disk.

SessionStart with the compact matcher

* Reload or reference project instructions.
* Direct the agent to restore the active task state.
* Ensure unfinished requirements remain visible.
* Initiate a requirements reconciliation before resuming work.

SessionStart for startup and resume

* Restore the same persistent project context for new and resumed sessions.

PostCompact
Use when supported and helpful for recording or auditing the compaction event.
Do not rely on unsupported hooks or assume that hooks alone preserve conversational memory.
Build and test the implementation according to the actual installed environment.
1.5 Mandatory recovery procedure
After compaction, session restart, or substantial agent handoff:

1. Reload project-root instructions.
2. Locate the canonical specification.
3. Read the relevant original requirements.
4. Reload the requirements registry.
5. Reload the persistent task ledger.
6. Reload the execution plan.
7. Read the latest session checkpoint.
8. Identify the active task and unfinished dependencies.
9. Compare the current plan with the original requirements.
10. Identify any lost, modified, or abandoned instructions.
11. Resume the appropriate unfinished task.

Perform full-specification reconciliation at major milestones and final completion. Use targeted reads during routine recovery to avoid unnecessarily refilling the context window.
Never treat a compaction summary as authoritative.
1.6 Test recovery before proceeding
Conduct a controlled manual compaction test using the supported Claude Code functionality.
Verify that:

* The original specification still exists.
* The project instructions reload.
* The active task remains identifiable.
* Unfinished tasks retain their status.
* The execution plan is recoverable.
* Requirement identifiers remain intact.
* Execution can resume without losing objectives.

Also test a resumed or new session where feasible.
Record the result.
Do not claim that recovery is reliable until testing supports that conclusion.
PART 2 — PREVENT FORGOTTEN OR INCOMPLETE TASKS
This is a critical requirement because previous long-running sessions have forgotten instructions, completed only part of assigned work, and lost requirements during compaction.
Correct this at the system level.
2.1 Build a complete requirements registry
Read the entire original prompt and extract every actionable requirement.
Give each requirement a unique, stable ID.
Record:

* Original requirement.
* Source reference.
* Interpretation.
* Priority.
* Dependencies.
* Assigned owner.
* Acceptance criteria.
* Verification procedure.
* Completion status.

Do not combine unrelated requirements into broad tasks that cannot be independently verified.
For example, "improve the video" must be decomposed into camera motion, rendering, materials, animation, engineering accuracy, overlays, exports, and visual review.
2.2 Create a persistent task ledger
Break requirements into concrete implementation tasks.
Each task must include:

* Unique task ID.
* Parent requirement ID.
* Description.
* Dependencies.
* Assigned agent or owner.
* Expected deliverable.
* Acceptance test.
* Supporting evidence.
* Status.

Use these statuses:

* NOT STARTED
* IN PROGRESS
* BLOCKED
* FAILED
* READY FOR REVIEW
* VERIFIED COMPLETE
* EXPLICITLY DEFERRED

Only VERIFIED COMPLETE counts as successfully completed.
Never delete tasks to make the project appear more complete.
Preserve completed, deferred, and abandoned tasks in the historical record.
2.3 Maintain requirement traceability
Enforce this relationship:
Original requirement → Task → Implementation → Test → Evidence → Verified status
Every original requirement must be accounted for.
Every implementation task must support an identified requirement or explicitly documented technical dependency.
Every verified requirement must have supporting evidence.
Missing links must be detected by automated audits.
2.4 Prevent partial execution
Before starting a task:

1. Identify the requirements it addresses.
2. Confirm its dependencies.
3. Define the intended output.
4. Define the acceptance test.
5. Assign an appropriate agent.
6. Record its status.

After implementation:

1. Inspect the actual output.
2. Run relevant tests.
3. Record evidence.
4. Perform review.
5. Update task status.
6. Reconcile unfinished work.

If an agent was assigned five changes but completed only four, the fifth must remain open and be addressed.
Do not allow an agent's completion message to substitute for verification.
2.5 Independent requirements audits
Use a separate reviewer to compare:

* The complete master specification.
* Requirements registry.
* Task ledger.
* Actual repository contents.
* CAD files.
* Simulation results.
* Video outputs.
* Test evidence.

Identify forgotten, partially implemented, or incorrectly closed tasks.
Perform these checks:

* After major implementation phases.
* After significant agent handoffs.
* Following context recovery.
* Before closing important requirements.
* Before final completion.

Use lightweight models for straightforward accounting and more capable models for difficult technical review.
2.6 Prevent premature termination
The main agent must not treat its latest completed task as equivalent to project completion.
Before stopping, reconcile all requirements.
If required feasible work remains incomplete, continue with the next appropriate task.
If something cannot be completed because of a genuine blocker, resource limitation, missing permission, or unavailable dependency, record the issue and report exactly what remains unfinished.
Do not enter infinite retry loops.
Do not fabricate completion.
PART 3 — INTELLIGENT MODEL SELECTION AND MULTI-AGENT ORCHESTRATION
Choose the most appropriate available AI model for every task.
The goal is maximum verified engineering progress with efficient computational resource usage.
Do not automatically use Opus for everything.
3.1 Default model routing
Haiku — Routine tasks
Prefer Haiku for:

* File inspection.
* Straightforward code changes.
* Basic CAD parameter adjustments.
* Documentation.
* Repetitive operations.
* Requirements tracking.
* Lightweight audits.
* Simple research.
* Test execution and result collection.

Sonnet — Moderate complexity
Prefer Sonnet for:

* CAD feature development.
* Mechanical subsystem implementation.
* Simulation scripting.
* Standard debugging.
* CLI development.
* Video pipeline improvements.
* Rendering optimization.
* Integration development.
* Moderate engineering analysis.

Opus — Advanced reasoning
Prefer Opus for:

* Initial project architecture.
* Detailed complex-task planning.
* Difficult mechanical engineering decisions.
* Root-cause diagnosis.
* Engineering tradeoff evaluations.
* Complex multi-system integration.
* High-impact independent reviews.
* Escalated implementation failures.
* Final engineering verification.

Use the best available alternatives when specific models are inaccessible.
Model assignments are defaults, not rigid restrictions.
Evaluate task complexity and engineering risk before selecting a model.
3.2 Orchestration architecture
Use a capable main agent as the project conductor.
The conductor should focus on:

* Planning.
* Task decomposition.
* Delegation.
* Dependency management.
* Requirement tracking.
* Integration.
* Independent verification.
* Overall completion.

Avoid having the conductor perform routine implementation that could be delegated efficiently.
Assign focused work units to subagents with clearly scoped objectives and acceptance criteria.
3.3 Mandatory delegation rules

1. Plan complex work before implementation.
2. Divide work into independent units.
3. Use the lowest-cost capable model.
4. Parallelize independent work when safe.
5. Prevent conflicting edits.
6. Use separate branches or worktrees when appropriate.
7. Require evidence-backed agent reports.
8. Escalate when lower-cost models fail or work is unusually complex.
9. Diagnose repeated failures instead of repeatedly attempting the same fix.
10. Review major engineering changes independently.
11. Merge only changes that satisfy their acceptance criteria.
12. Preserve task status during agent handoffs.

Use James's shared agent definitions when available.
Avoid building a redundant framework that conflicts with the team's shared infrastructure.
3.4 Model performance auditing
Track, where measurable:

* Selected model.
* Task complexity.
* Task outcome.
* Approximate cost or usage.
* Number of retries.
* Escalation reason.
* Independent review results.

Periodically evaluate whether expensive models are being overused or cheaper models are causing excessive rework.
Optimize for successful verified results, not simply the lowest possible token cost.
PART 4 — AUDIT AND IMPROVE EXISTING AIRCRAFT CAD
4.1 Establish the current baseline
Inspect the existing aircraft project.
Identify:

* Current aircraft configuration.
* CAD geometry and assemblies.
* Wing mechanisms.
* Control surfaces.
* Propulsion systems.
* Motors and actuators.
* Mechanical connections.
* Structural components.
* Wiring.
* Connectors.
* Current simulation methods.
* Existing engineering constraints.

Determine what currently works and what remains unverified.
Preserve functioning systems.
4.2 Increase physical realism
Improve important CAD components so the aircraft can be meaningfully evaluated as a physical assembly.
Prioritize:

* Mechanical joints and hinges.
* Motor and actuator mounts.
* Fasteners.
* Structural interfaces.
* Wiring and connectors.
* Assembly clearances.
* Mechanism linkages.
* Manufacturing feasibility.

Do not use generic boxes or simplified connectors when they conceal important mechanical functionality.
A visually convincing assembly is not necessarily a mechanically functional one.
4.3 Preserve engineering consistency
Ensure important geometry is internally consistent.
Check:

* Component alignment.
* Connection geometry.
* Motion clearances.
* Assembly feasibility.
* Realistic interfaces.
* Physical constraints.
* Plausible material and structural assumptions.

Avoid unnecessary complexity.
Document any unavoidable geometric simplifications.
PART 5 — IMPLEMENT ACTUAL PHYSICS AND MECHANICAL VALIDATION
One previously identified issue is that the project reported passing a physics check when the actual computation was only a static collision test.
Correct this distinction.
5.1 Identify existing simulation capabilities
Determine which real analysis methods are currently implemented:

* Static collision detection.
* Rigid-body dynamics.
* Mechanism kinematics.
* Structural FEA.
* Aerodynamic CFD.
* Flight dynamics.
* Other relevant numerical solvers.

Identify the software and code actually used.
Never infer that a physics simulation occurred simply because the model or a report says it passed.
5.2 Implement real mechanism validation
Demonstrate important aircraft mechanisms operating through physically meaningful simulations.
Prioritize:

1. Wing and flap mechanisms.
2. Motors and actuators.
3. Mechanical linkages.
4. Joint constraints.
5. Motion ranges.
6. Assembly clearances.
7. Collision detection during motion.
8. Relevant takeoff and landing mechanisms.

Begin with simplified frictionless rigid-body models where appropriate.
Use increasing fidelity only when justified.
5.3 Separate simulation categories
Clearly distinguish:

* Interference checking.
* Kinematic validation.
* Rigid-body dynamics.
* Structural FEA.
* Aerodynamic CFD.
* Flight dynamics.
* Illustrative animation.

Do not confuse these analysis types or use one as unsupported evidence for another.
5.4 Require reproducible evidence
For each significant analysis, record:

* Solver or simulation engine.
* Model version.
* Inputs.
* Assumptions.
* Boundary conditions.
* Important numerical settings.
* Outputs.
* Acceptance criteria.
* Actual pass/fail status.
* Limitations.

Save reproducible results where possible.
Do not fabricate simulations or claim success without actual computation.
PART 6 — IMPROVE ENGINEERING DESIGN OPTIMIZATION
Previous design iterations frequently corrected FEA failures by adding material, making the aircraft unnecessarily heavy.
Implement a more disciplined design process.
6.1 Evaluate multiple solution strategies
When encountering a failure, consider:

1. Subtracting unnecessary features or components.
2. Modifying existing geometry.
3. Rearranging components.
4. Changing the mechanism or structural approach.
5. Adding material or components when necessary.

Do not automatically add geometry.
6.2 Compare engineering alternatives
Use appropriate metrics including:

* Total mass.
* Structural performance.
* Mechanical functionality.
* Reliability.
* Manufacturing complexity.
* Assembly complexity.
* Aerodynamic implications.
* Design constraints.

Document tradeoffs and engineering reasoning.
6.3 Prioritize functioning mechanisms
Resolve difficult mechanical functionality problems before aggressive mass optimization.
It is often more valuable to establish a functional mechanism and then reduce its weight than to optimize the weight of a mechanism that does not actually work.
Maintain appropriate mass tracking throughout design iteration.
6.4 Use engineering research
Research relevant established mechanisms and engineering solutions when appropriate.
Use benchmark designs, literature, and known physical principles to evaluate alternatives.
Consider generating and comparing multiple credible concepts before selecting one.
Do not rely exclusively on the first AI-generated solution.
PART 7 — MAJOR AIRCRAFT VIDEO IMPROVEMENT
The existing aircraft video must be substantially improved.
Treat it as both an engineering communication tool and a major project deliverable.
Do not overlook the video while focusing on CAD, simulation, or software infrastructure.
7.1 Audit the current video pipeline
Inspect:

* Existing video files.
* Rendering software.
* Camera paths.
* Lighting.
* Materials.
* CAD imports.
* Animation scripts.
* Scene construction.
* Technical overlays.
* Export settings.
* Performance bottlenecks.

Identify opportunities for meaningful improvement.
Improve the existing pipeline rather than rebuilding it unnecessarily.
7.2 Increase visual quality
Upgrade:

* Geometry fidelity.
* Material realism.
* Lighting and shadows.
* Surface finishes.
* Camera movement.
* Scene composition.
* Animation smoothness.
* Rendering consistency.
* Visual clarity.
* Technical presentation.

Use the current actual CAD model as the geometric source of truth.
Use Blender or another suitable rendering engine when beneficial.
Target at least 1080p resolution, preferably 60 FPS when practical.
7.3 Create a professional engineering demonstration
Structure the video around a clear sequence.
Scene 1 — Aircraft overview
Present the complete aircraft with smooth, professional camera movement.
Communicate the overall configuration and geometry.
Scene 2 — Detailed CAD inspection
Show close-ups of important subsystems.
Highlight:

* Wing geometry.
* Propulsion.
* Mechanical interfaces.
* Structural components.
* Control mechanisms.

Scene 3 — Mechanical operation
Demonstrate important moving components.
Show:

* Actuators.
* Hinges.
* Linkages.
* Control surfaces.
* Relevant mechanical motion.

Use appropriate close-ups and cutaways.
Scene 4 — Physics validation
Display actual executed simulation results.
Demonstrate verified mechanism behavior.
Use meaningful motion and engineering annotations.
Clearly distinguish simulated motion from illustrative animation.
Scene 5 — Engineering analysis
Present verified results from relevant FEA, CFD, or other engineering analyses.
Use appropriate technical visualizations and concise annotations.
Only display numerical results supported by actual computation.
Scene 6 — Final presentation
Conclude with a polished overview of the latest validated aircraft design.
Use consistent visual styling and professional camera movement.
7.4 Improve technical explanations
Add clear and appropriately restrained:

* Component labels.
* Motion arrows.
* Dimensional annotations.
* Exploded views.
* Transparent assemblies.
* Technical overlays.
* Simulation metrics.
* Design revision information.
* Verified pass/fail results.

Make the demonstration understandable to engineering faculty and viewers unfamiliar with the project.
Avoid clutter.
7.5 Improve animation accuracy
Ensure that:

* Mechanical movement follows intended constraints.
* Actuators visibly drive the correct mechanisms.
* Connected components remain properly connected.
* Moving parts do not intersect unintentionally.
* Motion paths are consistent.
* Camera angles reveal critical mechanical behavior.
* Aircraft geometry matches the actual CAD design.

Use simulation output to drive motion where feasible.
Do not present manually animated motion as physically validated.
7.6 Independent video review
Use a separate visual and technical review process.
Inspect rendered frames and finished videos for:

* Poor camera movement.
* Abrupt transitions.
* Geometry clipping.
* Unnatural motion.
* Incorrect mechanical connections.
* Poor lighting.
* Rendering artifacts.
* Incorrect labels.
* Inconsistent geometry.
* Unclear engineering explanations.
* Unsupported simulation claims.

Apply iterative improvements.
Use Impeccable where applicable for presentation interfaces and visual design, and dedicated frame/video inspection for rendered footage.
Generate previews before expensive full-quality renders.
7.7 Required video deliverables
Produce:

1. Improved main aircraft demonstration video.
2. Short presentation-ready highlight video.
3. Mechanism demonstration clips.
4. Documentation of the rendering pipeline.
5. Summary of improvements.
6. Independent playback and visual verification results.

Target approximately:

* Main video: 60–120 seconds.
* Highlight video: 20–30 seconds.

Adjust duration when needed for clarity.
Do not mark video work complete until exported videos exist, play successfully, and pass review.
PART 8 — TEAM INFRASTRUCTURE AND SYSTEM INTEGRATION
Coordinate with ongoing team developments.
Relevant infrastructure includes:

* Shared aircraft schema.
* Unified CLI.
* OpenCAE.
* DaVinci.
* Shared agent configuration.
* Centralized design viewer.
* Weekly reporting artifacts.

8.1 Common aircraft representation
Use the team's shared aircraft file format where available.
Support importing, modifying, and exporting designs without unnecessary source-code changes.
Avoid conflicting definitions.
8.2 CLI and simulation integration
Coordinate with the team so an agent can eventually:

1. Load an aircraft design.
2. Modify a design parameter.
3. Run appropriate engineering tests.
4. Collect and interpret results.
5. Compare design iterations.
6. Save the updated design.
7. Generate reviewable evidence.

Do not duplicate another team member's work unnecessarily.
8.3 DaVinci integration
Investigate the DaVinci API capabilities available to the team.
Attempt the agreed complete design-build workflow through Claude Code using authorized access.
Verify actual functionality and cost implications rather than assuming API usage bypasses service charges.
Document integration failures and necessary external dependencies.
8.4 Interface consolidation
Do not create additional standalone dashboards simply because a new feature is being added.
Prefer integrating useful functionality into the existing project interface.
Maintain a consistent design language.
Support reviewable aircraft, simulation, and video results through shared team workflows.
PART 9 — COMPREHENSIVE REPOSITORY CLEANUP AND OPTIMIZATION
Perform a substantial audit of the existing repository.
The goal is to eliminate unnecessary files, redundant functionality, abandoned experiments, and inefficient code while preserving valuable engineering work.
This must improve maintainability and, where possible, measurable performance.
9.1 Inventory the repository
Inspect:

* Source code.
* CAD models.
* Assemblies.
* Simulation scripts.
* FEA and CFD results.
* Video assets.
* Render outputs.
* Intermediate files.
* Logs.
* Caches.
* Build artifacts.
* Documentation.
* Agent configurations.
* Dependencies.
* Abandoned experiments.
* Old versions.
* Duplicate scripts.
* Unused interfaces.

Identify unusually large files and directories.
Measure baseline repository size and relevant performance metrics.
9.2 Classify cleanup candidates
Use four categories.
Protected
Do not automatically remove:

* Master project specification.
* Requirements registry.
* Task ledger.
* Execution checkpoints.
* Compaction-recovery configuration.
* Current CAD source files.
* Verified engineering results.
* Essential simulation data.
* Current video assets.
* Required dependencies.
* Valuable design references.

Safe to regenerate
Examples:

* Disposable caches.
* Temporary render intermediates.
* Redundant build outputs.
* Nonessential transient logs.

Remove only after confirming they are not actively needed and can safely be regenerated.
Obsolete or redundant
Examples:

* Duplicate code.
* Unused scripts.
* Superseded outputs.
* Redundant interfaces.
* Abandoned prototypes.
* Unused dependencies.

Verify references and dependencies before removal.
Uncertain
Preserve or archive files whose purpose is not confidently established.
Do not assume older engineering designs are useless.
9.3 Perform safe cleanup
Before modifying or deleting files:

1. Inspect the current Git state.
2. Preserve a recoverable checkpoint.
3. Create a dedicated cleanup branch where appropriate.
4. Generate a file inventory.
5. Identify dependencies and references.
6. Classify cleanup candidates.
7. Produce a dry-run cleanup plan.
8. Distinguish reversible cleanup from potentially destructive changes.
9. Obtain approval for ambiguous or irreversible deletion.
10. Execute safe cleanup in manageable batches.
11. Run regression tests after each batch.
12. Restore anything whose removal causes problems.

Do not rewrite project history or remove shared team assets without appropriate authorization.
9.4 Consolidate redundant functionality
Investigate:

* Duplicate CAD pipelines.
* Redundant simulation wrappers.
* Unnecessary file conversions.
* Multiple interfaces performing the same function.
* Repeated calculations.
* Duplicate validation logic.
* Conflicting configurations.
* Overlapping agent instructions.
* Redundant rendering systems.
* Repeated documentation.

Consolidate where doing so simplifies the project.
Avoid creating additional frameworks solely for cleanup.
9.5 Improve performance
Measure and optimize:
CAD and simulation

* Model loading time.
* Geometry processing.
* Simulation execution.
* File conversion overhead.
* Memory usage.
* Repeated computations.
* Unnecessary numerical analysis.

Video rendering

* Render times.
* Scene complexity.
* Geometry duplication.
* Texture memory.
* Intermediate files.
* Repeated full-scene rendering.
* Asset loading.

AI agents

* Context consumption.
* Excessive file searches.
* Repeated reading of irrelevant files.
* Unnecessary expensive model use.
* Duplicate agent activity.
* Excessive hooks.
* Inefficient task delegation.
* Redundant audits.
* Slow or stalled sessions.

Software

* Application startup.
* Responsiveness.
* CPU and GPU utilization.
* Memory consumption.
* Disk access.
* Unnecessary dependencies.

Use actual measurements.
Do not claim that deleting files improved computational performance without supporting evidence.
9.6 Optimize Claude's context efficiency
Create an efficient repository structure for AI agents.
Prefer:

* Concise entry-point instructions.
* Well-organized reference files.
* Targeted context retrieval.
* Persistent task records.
* Clear project documentation.
* Reusable engineering commands.
* Reduced duplicate instructions.

Never optimize context usage by deleting required instructions or removing requirements from the canonical specification.
Avoid loading enormous logs or generated files into context unnecessarily.
9.7 Organize project files
Create a logical structure for:

* Active code.
* Current CAD models.
* Simulation inputs.
* Simulation results.
* Video sources.
* Video outputs.
* Engineering documentation.
* Agent configuration.
* Tests.
* Generated intermediates.
* Archived references.

Preserve working paths and integrations.
Use `.gitignore` appropriately for regenerable artifacts.
Do not reorganize files solely for aesthetic reasons when doing so would create unnecessary risk.
9.8 Verify cleanup results
After changes, confirm:

* CAD models still load.
* Simulations still execute.
* Video rendering still works.
* Important engineering data remains available.
* Shared integrations still function.
* Agent configurations remain operational.
* Prompt preservation still works.
* Context recovery still works.
* Requirements remain intact.
* No important deliverables were removed.

Compare measurable performance before and after cleanup.
Document both improvements and regressions.
9.9 Produce a repository audit report
Create:
`docs/repository-audit.md`
Include:

* Baseline repository size.
* File inventory.
* Cleanup candidates.
* Files removed or archived.
* Functionality consolidated.
* Dependencies eliminated.
* Space recovered.
* Performance benchmarks.
* Regression tests.
* Remaining inefficiencies.
* Preserved reference materials.
* Any unresolved risks.

9.10 Repeat cleanup at appropriate milestones
Perform:
Initial audit: Before major development, to identify existing inefficiencies.
Final audit: After engineering and video development, to eliminate newly introduced clutter and optimize the finished system.
Use lightweight incremental checks between these milestones.
Avoid repeatedly running expensive full-repository audits without justification.
PART 10 — CONTINUOUS MONITORING AND FAILURE RECOVERY
Long-running agents must be monitored for actual progress.
10.1 Track active work
Record:

* Active tasks.
* Assigned agents.
* Start and completion state.
* Relevant dependencies.
* Recent meaningful progress.
* Errors.
* Blocking conditions.

Persist this state outside conversational memory.
10.2 Detect stalled processes
Check for:

* Repeated unsuccessful operations.
* Agents producing no meaningful progress.
* FEA or rendering jobs stuck unexpectedly.
* Repeated file conversion failures.
* Excessive retries.
* Unnecessary loops.
* Conflicting agent changes.
* Task scope drift.

Use inexpensive checks where appropriate.
Do not run expensive audits more frequently than necessary.
10.3 Recover intelligently
When a process fails:

1. Identify the specific failure.
2. Determine whether it is transient or structural.
3. Inspect relevant logs and artifacts.
4. Avoid repeating identical unsuccessful attempts.
5. Revise the approach.
6. Escalate to a more capable model if justified.
7. Preserve the task's original requirements.
8. Verify recovery.
9. Record the resolution.

Do not silently abandon failed tasks.
10.4 Protect long-running task context
Before major handoffs or compaction, persist:

* Current goal.
* Relevant requirements.
* Completed operations.
* Pending operations.
* Failed attempts.
* Engineering decisions.
* Next action.

Restore this information before resuming work.
PART 11 — EXECUTION PLAN
Use Superpowers or an equivalent structured planning process.
Organize the work into dependency-aware phases.
Phase 1 — Preservation and project audit

* Save the master specification.
* Integrate persistent instructions.
* Create requirements and task ledgers.
* Configure compaction recovery.
* Test recovery.
* Inventory existing project functionality.

Phase 2 — Initial repository optimization

* Audit unused files.
* Identify redundant systems.
* Measure performance.
* Safely clean disposable artifacts.
* Simplify relevant project structure.

Phase 3 — Agent orchestration

* Implement intelligent model selection.
* Improve task delegation.
* Establish independent review.
* Implement persistent progress monitoring.
* Integrate shared agent definitions.

Phase 4 — Mechanical engineering

* Improve CAD realism.
* Validate important connections.
* Implement mechanism simulation.
* Correct engineering issues.
* Improve design optimization.

Phase 5 — Video improvements

* Audit existing video.
* Improve rendering quality.
* Improve camera movement.
* Demonstrate mechanisms.
* Incorporate verified engineering results.
* Render and review final videos.

Phase 6 — Team integration

* Coordinate with shared schema.
* Support CLI-driven iteration.
* Integrate OpenCAE where appropriate.
* Attempt DaVinci workflow.
* Consolidate existing interfaces.

Phase 7 — Final optimization

* Remove unnecessary generated artifacts.
* Consolidate duplicate functionality.
* Optimize performance bottlenecks.
* Perform regression testing.
* Verify compaction recovery remains operational.

Phase 8 — Independent final verification

* Reconcile the full requirements registry.
* Inspect actual deliverables.
* Verify CAD and simulation functionality.
* Verify video outputs.
* Review agent performance.
* Confirm cleanup results.
* Produce the final report.

These phases are a starting structure.
Adjust dependencies based on the existing repository, but do not silently remove requirements.
Independent tasks may proceed in parallel when safe.
PART 12 — FINAL VERIFICATION
Before declaring the project complete, run an independent final audit.
The reviewer must examine the original master specification and the actual finished project.
Do not rely solely on the main agent's progress summary.
12.1 Verify every original requirement
Produce a requirement-by-requirement assessment containing:

* Requirement ID.
* Original expected outcome.
* Implemented functionality.
* Supporting artifact.
* Verification procedure.
* Test result.
* Current status.
* Remaining limitations.

Calculate completion statistics using verified requirements.
Do not count blocked, deferred, or partially implemented work as complete.
12.2 Verify engineering deliverables
Confirm:

* The current aircraft CAD model loads.
* Important mechanisms are physically credible.
* At least one important mechanism has been meaningfully simulated.
* Simulation claims correspond to actual computations.
* Relevant tests are reproducible.
* Important design changes have engineering justification.

12.3 Verify AI workflow deliverables
Confirm:

* Model routing actually works.
* Task tracking is persistent.
* Subagents preserve requirement traceability.
* Independent reviews are operational.
* Context compaction recovery works.
* Session recovery works.
* Unfinished tasks remain visible.

12.4 Verify video deliverables
Confirm:

* Main video exists.
* Highlight video exists.
* Mechanism clips exist.
* Video files play successfully.
* Video geometry reflects the correct aircraft version.
* Motion is mechanically consistent or clearly labeled illustrative.
* Technical labels are accurate.
* Visual review has been performed.
* Major identified defects have been corrected.

12.5 Verify repository optimization
Confirm:

* Cleanup was performed safely.
* Important files remain protected.
* Unnecessary duplication was addressed.
* Performance results are documented.
* Regression tests pass.
* Original prompt preservation still works.
* Requirements have not been lost.

12.6 Resolve incomplete work
If an audit reveals missing or incorrect work:

1. Reopen the associated task.
2. Determine the cause.
3. Assign an appropriate agent.
4. Implement the correction.
5. Repeat verification.

Continue when technically feasible and authorized.
If the remaining work is genuinely blocked, record that limitation explicitly.
Do not manufacture results or use endless retries to satisfy a completion target.
PART 13 — FINAL DELIVERABLES
The completed project should provide:
Aircraft engineering

* Improved physically credible aircraft CAD.
* More realistic assemblies.
* Demonstrated mechanical functionality.
* Meaningful engineering simulations.
* Documented design decisions.
* Engineering comparisons and validation evidence.

AI automation

* Intelligent model routing.
* Effective multi-agent orchestration.
* Persistent task tracking.
* Independent auditing.
* Recovery from context compaction.
* Recovery from session restarts.
* Reliable tracking of incomplete work.

Video and presentation

* Substantially improved aircraft demonstration video.
* Short highlight video.
* Mechanical demonstration clips.
* Professional camera movement and rendering.
* Clear engineering annotations.
* Verified simulation visualization.
* Video quality review results.

Repository and performance

* Organized codebase.
* Removal or archival of verified unnecessary files.
* Reduced redundant functionality.
* Improved efficiency where measurable.
* Performance benchmark results.
* Complete cleanup report.
* Regression-test results.

Project management

* Unabridged master specification.
* Requirements registry.
* Complete task ledger.
* Execution plan.
* Persistent session state.
* Engineering decision records.
* Independent verification report.
* Accurate list of anything remaining incomplete.

FINAL NON-NEGOTIABLE EXECUTION RULES

1. Never lose the original user instructions during compaction.
2. Never replace the master specification with a summary.
3. Never silently discard requirements.
4. Never mark unfinished work as complete.
5. Never trust agent self-reports without appropriate evidence.
6. Never use expensive models for trivial work without justification.
7. Never repeatedly retry failures without diagnosing the cause.
8. Never treat a visual animation as proof of physical validation.
9. Never optimize the aircraft solely by adding more material.
10. Never introduce unnecessary interfaces or duplicated systems.
11. Never delete valuable engineering files without verifying their purpose.
12. Never delete or overwrite the master specification or persistent task records during cleanup.
13. Never claim performance improvements without appropriate measurements.
14. Never declare the entire project complete while required feasible work remains unverified.
15. Always maintain requirement-to-task traceability.
16. Always persist active work before major handoffs or context loss.
17. Always reconcile requirements after context recovery.
18. Always review significant engineering decisions independently.
19. Always verify final exported video files.
20. Always distinguish completed, blocked, deferred, and unverified work accurately.

IMMEDIATE EXECUTION INSTRUCTIONS
Begin working in the EXISTING project repository.
First:

1. Inspect the current project structure and instructions.
2. Save this entire prompt verbatim as the canonical master specification.
3. Establish permanent requirement and task tracking.
4. Integrate instruction persistence into Claude Code.
5. Implement and test context-compaction recovery.
6. Audit existing CAD, simulation, video, and software capabilities.
7. Conduct an initial repository cleanup and performance assessment.
8. Create a detailed dependency-aware implementation plan.
9. Assign tasks to the most appropriate available AI models.
10. Execute the full plan with persistent tracking and independent verification.

Do not stop merely because the planning stage is complete.
Proceed with implementation as long as the required tools, resources, and permissions are available.
Do not interrupt the process unnecessarily when a task can be completed autonomously within authorized boundaries.
Do not make irreversible changes, incur unapproved costs, or override required approvals.
Provide concise progress updates at meaningful milestones rather than excessive narration.
At every major checkpoint, reconcile the original requirements against completed and remaining work.
If context compaction occurs, recover from the permanent project files and continue.
If a process fails, diagnose and recover.
If a task remains unfinished, keep it visible.
If the project becomes bloated, simplify it without destroying valuable work.
If an agent's output is questionable, verify it independently.
The ultimate objective is a physically credible, well-validated, professionally visualized aircraft engineering system that is computationally efficient and reliably developed by AI agents without losing any part of the original user intent.
Begin now with project inspection, permanent specification preservation, task-registry creation, and the initial audit. Then continue through implementation and verification.
