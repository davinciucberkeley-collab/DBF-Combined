# How to resume the redesign

## Paused 2026-11-11 (night): wires routed without phasing, build animation (start here)
All six buildability blockers are fixed in CAD or design except the team decision on Jacobs access (BR-04 / MF-02).
Status table: `review/BUILDABILITY-REVIEW.md` "Blocker status". Decisions D-74...D-85 in `params/CHANGE-LOG.md`.

| Item | State |
|---|---|
| BR-00 CG, SW-02 fin tip, WB-01 power board, MF-01 shop files | Fixed (D-74...D-79), as before. |
| MM-01 slit, MM-02 clocking key | **Fixed in CAD** (D-80, D-81). Open: C6 sizes the dog's shear (it adds to the D-23 slip fuse) before the 18 Dec freeze. |
| Horn bore breakout, POD-007 void, HRN-110 grommet | **Fixed** (D-82, D-84 b, D-83). Shop files: 249 checks, 0 FAIL, 0 issues. |
| No parts phasing (physics-simulator ready) | **Passes with every wire**: `python -I redesign/collision/collide.py` (about 5 min). 990 bodies in 185 parts plus every routed wire at its drawn diameter; 0 penetrations > 0.05 mm, static and at both elevon limits. Holes and pockets in `interfaces/seats.json`; geometry fixes D-84; harness re-route, P1s hole and frame lead notch D-85. |
| Build animation | **New**: `showcase/animation/render_build.py` -> `showcase/animation/build/` (whole build, 49 s, plus one clip and end-state still per stage 2-11). Linked from `BUILD-GUIDE.md` and the Explorer. |
| Proof graph | **Clean** (0 drift, 0 errors), 4,245 nodes; 90 claims fail on margin (87 before D-85). The 3 new: `CL-F2-MASS` 135.2 g vs 129 g allocation, `CL-F2-I2C-LEN` 0.511 m vs 0.5 m, and `R-HARNESS-INSTALL` that rolls them up. CG and mass gate unchanged (the A3 roll-up uses the allocation). |
| Harness mass and I2C length | **Team-lead decision** (D-85 Open): raise the harness allocation or cut routed length; accept or shorten the I2C run. |
| MF-02 Jacobs access | **Team decision needed.** |

Next steps in order:
1. Owners re-check what this round changed: C6 the collar bond (D-81 notch, -0.9 % area) and the dog size; C3 the 4.8 mm
   recess-fillet leg (D-84 d); C4 mount rocking stiffness with the shorter outboard cheek (D-80).
2. Regenerate the media that were not re-rendered this round: renders (`showcase/tools/render_showcase.py`), drawing
   (`showcase/drawing/`), the how-it-flies animation. The GLB, viewer data, shop files and build animation are current.
3. Before any Fusion run or print: `python -I redesign/fusion/check.py`, `python -I redesign/collision/collide.py`,
   `python -B redesign/manufacturing/make_shop_files.py`.
4. Explorer artifact (private, owner Dillon's account): https://claude.ai/artifact/XYkihMreBq6Gn7deTEwSC8 . Republish from
   `redesign/site/app.html` with the same file list; the 3-D model loads from `data/assembly.glb.js` there (artifacts do
   not serve .glb), from `assets/k09l.glb` everywhere else.
5. Note: `fusion/tests` has 2 failing tests (skeleton CG range, transport also_contacts); they fail the same way on
   commit 4784faa, before this round.

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
