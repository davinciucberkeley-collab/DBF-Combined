# Change requests from the build-manual kit

| # | To | What | Why |
|---|---|---|---|
| 1 | Integrator (BRIEF), subsystem agents 3-11 | Each subsystem writes `redesign/subsystems/<name>/steps.json` (format: `redesign/manual-kit/README.md`) next to `parts.csv` and `interfaces.json`. `BUILD.md` can then be the generated `MANUAL.md` section, not a second copy | one source for build steps; fasteners, torques and tools come from the joint stacks, numbers from `params.json`; `build_manual.py --check` validates in < 1 s |
| 2 | Manufacturing (agent 15) | Own `redesign/manufacturing/manual.json`: work packages in build order, manual-level safety rules, cover/overview figures | the kit is configuration-independent; WP order and safety are the manufacturing engineer's call |
| 3 | Interface keeper (agent 2) | Write joint-stack text consistently (`M3 washer`, `M3 nyloc`, tool names such as `2.5 mm hex key`), one item per `+` | kitting sums fasteners and tools by exact text |
| 4 | Blender tooling | Optional: a sidecar field with each callout's on-screen visible area, and `--no-annotate` to skip the label SVG for step figures | the manual draws numbered dots itself; the label SVG for steps is unused |
