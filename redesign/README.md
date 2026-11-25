# Redesign: concept A, the scaled quad tailsitter (O4b)

**Concept A (O4b) is the current design** (D-182, re-sit D-219; status in the root `CLAUDE.md`). It is a scaled quad
tailsitter VTOL: 0.90 m wing, four motors and APC 9x4.5MR props, one 4S 2,800 mAh pack, Kakute H743-Wing flight
controller, glass wing skin. Predicted mass 1.881 kg `EST` (CAD basic 1,641 g); the mass gate is missed, so the physics
checks govern. BOM $1,939.17 of $2,000 (`qp/A/bom_a.py`). As of 2026-11-23 the strict proof build has 14 claims
that FAIL (the list is in `CLAUDE.md` and `qp/A/proofs/run_all.py`). Nothing is bought, built or flown yet.

Design workspace and status: [qp/README.md](qp/README.md). Decisions: [params/CHANGE-LOG.md](params/CHANGE-LOG.md).

## Open the Explorer

Windows with Python: double-click `START-EXPLORER.bat` at the repository root. It serves `site/` on
`http://localhost:8765/` and opens the Explorer. Or use the GitHub Pages link at the top of the root [README](../README.md).

## Where things live (concept A)

| Path | What |
|---|---|
| [qp/A/](qp/A/BUILD-GUIDE-A.md) | Concept A: CAD (`cad/`), BOM (`BOM-A.csv`, `bom_a.py`), proofs (`proofs/`), SITL, build guide, test plan |
| [site/](site/) | The Explorer web app (generated pages; see its `make_*.py` scripts) |
| [showcase/concept-a/](showcase/concept-a/) | Concept A renders, films and drawings ([SHOWCASE.md](SHOWCASE.md)) |
| [proofs/](proofs/README.md) | Proof-graph tooling |
| [params/](params/params.json) | Parameters and the decision log (`CHANGE-LOG.md`) |
| [collision/](collision/README.md) | The 3-D interference gate tools |
| [review/](review/README.md) | Review rounds; the concept studies are `review/QP-1` to `review/QP-5` |

## K09-L record (not current)

K09-L was the earlier design (1.15 m flying wing, 2.6 kg gate). It could not be built new within $2,000 and is kept
as the record. Its old entry page, with the key-numbers table, is [README-K09L.md](README-K09L.md).

| K09-L item | Path |
|---|---|
| Decision and status | [CONFIGURATION.md](CONFIGURATION.md), [STATUS.md](STATUS.md), [HANDOFF.md](HANDOFF.md), [RESUME.md](RESUME.md), [BRIEF.md](BRIEF.md), [MASS-CG.md](MASS-CG.md), [PROOFS.md](PROOFS.md) |
| Team roles | [TEAM.md](TEAM.md), [team/](team/) |
| Configuration study | [config-study/](config-study/README.md) |
| Subsystems and interfaces | [subsystems/](subsystems/), [interfaces/](interfaces/REPORT.md) |
| Fusion scripts | [fusion/](fusion/README.md) |
| Inputs and viewer | [inputs/](inputs/), [viewer/](viewer/index.html) |
| Manufacturing, manual kit, Blender | [manufacturing/](manufacturing/), [manual-kit/](manual-kit/), [blender/](blender/) |
| Build guide and old pages | [BUILD-GUIDE.md](BUILD-GUIDE.md), [index.html](index.html), [DESIGN-PROGRAM.workflow.js](DESIGN-PROGRAM.workflow.js) |
| K09-L renders and films | [showcase/animation/](showcase/animation/), [showcase/renders/](showcase/renders/), [showcase/stl/](showcase/stl/), [showcase/pages/](showcase/pages/) |

These were not moved in T-104 (see `docs/repository-audit.md`).
