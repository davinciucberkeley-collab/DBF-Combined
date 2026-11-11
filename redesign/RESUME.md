# How to resume the redesign

## Paused 2026-11-11: fixing the buildability blockers (start here)
The buildability review (`review/BUILDABILITY-REVIEW.md`) found 6 Blockers. Work in progress on fixing them:

| Blocker | State |
|---|---|
| BR-00 CG aft of range | **Fixed in design.** D-75 to D-78: fin tip and foot on one datum, lighter feet (69.9 to 59.1 g), landing allocation 48 to 60 g from power, pack datum to x -0.036. Predicted CG 50.2 mm in 46.6-51.4 (basic 48.6). Gate margin 139 g. The 590 g pack misses its 100 g margin by 0.7 g. |
| SW-02 fin tip vs foot shoe | **Fixed.** Mismatch 0, CAD shoe clears the fin by 0.2 mm min. |
| WB-01 power board | **Resolved from documents** (D-74): board splits, servo BEC 8 A vs 5.6 A need, UBEC and its fuse dropped, XT30U pod-wing disconnects added (D-79 moves 6 g power to harness). Bench check on arrival: `subsystems/power/BOARD-CHECK.md`. Pod case U side clearance is only 1.8 mm. |
| MF-01 no shop files | **Fixed.** `python -B redesign/manufacturing/make_shop_files.py` makes STLs, DXFs, hot-wire templates, jigs (see `manufacturing/SHOP-PACK.md`). Re-run after any CAD change. |
| MM-01 motor-mount clamp slit bridged | **Not started.** `subsystems/fins/fusion/fins.py` build_motor_mount: cut the slit through the cheek; add a clocking key to the station collar (MM-02, MF-06/07). Also fix horn blades MEC-004/006 (bore breaks out of the blade edge), POD-007 floating body, HRN-110 grommet has no body. |
| MF-02 Jacobs access | **Team decision needed:** Maker Pass $125 per student per semester is not in the budget; Jacobs lists no hot-wire cutter. |

Next steps in order:
1. Fix MM-01 / MM-02 and the horn, POD-007, HRN-110 CAD defects (above).
2. Re-run drifted proof scripts: `A1/frame_claims`, `B2/sim/sim_claims`, `B3/sc_analysis`, `C2/c2_claims`, `C5/landing_calc`,
   `D3/fins_calcs`, `D5/feet_calc`, `D7/transport_calc`, `F1/power`, then `proofs/build_graph.py` (several minutes, run in the
   background) until 0 drift / 0 errors; copy `proofs/out/graph.js` to `site/proofs/data/`; update PROOFS.md, STATUS.md, README key numbers.
   Slow owner re-runs still due: C5 shoe FEA (`run_d5r6.sh` on R7) and C3 pod FEA.
3. Regenerate visuals: GLB and viewer data (`blender/export_glb.py`), renders and thumbnails (`showcase/tools/render_showcase.py`),
   drawing (`showcase/drawing/`), animation, shop files; `python -I site/make_index.py`.
4. Update `review/BUILDABILITY-REVIEW.md` blocker status and `BUILD-GUIDE.md` "pending fix" notes.
5. Publish the explorer artifact and push `redesign/v1`.

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
