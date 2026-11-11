# How to resume the redesign

State on 2026-11-10: branch `redesign/v1` (PR #1 into `main`). The engineering-team design program ran through
**Frame → Analysis → Detail analysis → Design (Fusion CAD) → Integration → Simulation (+ fixes)** and stopped at
**Build and program** because of usage limits. See `STATUS.md` for what each phase produced and what is open.

## What is left (in order)
| Phase | Roles (TEAM.md) | Output |
|---|---|---|
| Build and program | G1, G2, G3, H3, then G4, H1, H2, I1, then I2 | process plans, composites/printing sheets, safety, build steps with animation specs, ground/flight test plans, single BOM + order plan, schedule |
| Media | J3, J2, J5 | Blender renders + animations, build manual (`manual-kit/build_manual.py`), proof graph, stale-doc cleanup |
| Review | J6 board (aero, structures, electrical, build-and-test) + chair, then J4 polish, J2, A2, A1 final | CDR reviews and go/no-go for the order, visual polish, final README/HANDOFF |

## How to restart it (Claude Code)
The program is a Claude Code workflow script: `redesign/DESIGN-PROGRAM.workflow.js`. The run journal that allowed an
exact resume lived in the original session, so a new session starts the remaining phases fresh:

1. Open Claude Code in `C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined` on branch `redesign/v1`.
2. Paste this prompt:

   > Read redesign/RESUME.md, redesign/STATUS.md and redesign/BRIEF.md. Copy redesign/DESIGN-PROGRAM.workflow.js to a
   > scratch file and edit it so the Frame, Analysis, Detail analysis, Design, Integrate and Simulate phases are
   > skipped (the work is already in redesign/team and redesign/subsystems; keep `frame` by reading
   > redesign/README.md and redesign/TEAM.md for the subsystem list). Then run the remaining phases (Build and
   > program, Media, Review) as a workflow with args {config: "K09-L, see redesign/CONFIGURATION.md"}. Commit locally
   > after each phase; push redesign/v1 only when I am here.

3. The script stops on its own if more than half of a phase fails (the usage-limit guard), so re-running the same
   command after a limit resets continues safely.

## Useful facts for whoever resumes
- **Tools:** XFOIL, AVL, SU2 (CFD + FEA), gmsh, NumPy/SciPy, Blender 4.2.3 — paths in `inputs/SIM-TOOLS.md`.
- **Checks:** `python -I redesign/fusion/check.py`, `python -I redesign/interfaces/merge_check.py`,
  `python -I redesign/proofs/build_graph.py`, `python -I redesign/team/A3/mass_rollup.py`.
- **Bulky solver files** (`*.su2`, `*.vtu`, meshes) are git-ignored under `redesign/team/`; re-run an engineer's
  script to regenerate them.
- **Stale-doc cleanup:** an early partial cleanup (C0-era) is in `git stash list` on the original machine
  ("partial: doc cleanup + C0 integrator params"). It predates the K09-L choice; J5 should redo cleanup against the
  current design rather than pop it.
- **Fusion:** nothing has run in real Autodesk Fusion yet. First real run: Utilities → Scripts and Add-Ins → add
  `redesign/fusion/BuildAll` → Run; report errors against `fusion/backends/fusion_backend.py` (marked
  UNVERIFIED-IN-FUSION).
- **Decision page** (private artifact): https://claude.ai/artifact/D5rq3fKmPww7zTbjMbM88r — source
  `config-study/web/index.html`.
