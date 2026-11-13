# How to resume the redesign

## 2026-11-13: build and program planning drafted (read first)
Maker Pass is paid outside the budget (owner); BOM R4 (`team/I1/ORDER-PLAN.md`): soldering-kit lines deleted (Electronics Lab), hot-wire gear bought (Jacobs lists none), pessimistic reserve $283.72 (short of $309 by $25.28),
all-in pessimistic +$20.45. New plans, all `PROPOSED`: `team/G1`-`G4` (process, foam, print list, build steps), `team/H2` (flight tests, twin report, pilot log), `team/H3` (flight card, compliance, battery, RFS wind),
`team/I2` (schedule, `make_schedule.py`), `team/F5/RANGE-TEST.md`; linked from `BUILD-GUIDE.md`, `README.md`, `STATUS.md`. Needs people: FAA registration, TRUST, UC flight requests and PI sponsor, AMA or other $1 M cover,
a hot-wire workspace, Jacobs trainings and Spring pass, an enclosed printer (list in `STATUS.md` issue 2 and `team/H3/COMPLIANCE.md` section 5).

## Paused 2026-11-12: exported model checked too (two gates); every lead ends square on a real pad; all media regenerated (start here)
All six buildability blockers are fixed in CAD or design except the team decision on Jacobs access (BR-04 / MF-02).
Status table: `review/BUILDABILITY-REVIEW.md` "Blocker status". Decisions D-74...D-89 in `params/CHANGE-LOG.md`.

| Item | State |
|---|---|
| BR-00 CG, SW-02 fin tip, WB-01 power board, MF-01 shop files | Fixed (D-74...D-79), as before. |
| MM-01 slit, MM-02 clocking key | **Fixed in CAD** (D-80, D-81). Open: C6 sizes the dog's shear (it adds to the D-23 slip fuse) before the 18 Dec freeze. |
| Horn bore breakout, POD-007 void, HRN-110 grommet | **Fixed** (D-82, D-84 b, D-83). Shop files: 249 checks, 0 FAIL, 0 issues. |
| No parts phasing (physics-simulator ready) | **Passes, two gates (D-88), every lead on a named termination (D-89)**: D-89: the CAD gate accepts a wire end only on a pad, solder joint, plug, header, cups, sleeve, lead exit or bus bar (not inside a bare envelope); the FC, RX, airspeed sensor, GPS, power board, pack and servos now carry those terminations (1,077 bodies in 212 parts, 0 off a termination). Pictures: `review/inspection-2026-11-13/`. `python -I redesign/collision/collide.py --glb` (export the GLB first; about 17 min in all). The CAD gate, and the same rules on the EXPORTED `assembly.glb` with no cutter assumed (what the Explorer, renders and videos show): 0 part pairs > 0.05 mm, 0 unseated ends, every lead entering its part within 25° of square, on a face. D-88 made the exporter's cuts exact and verified (MANIFOLD, one solid per part), landed every soldered lead square on its real pad under heat-shrink (HRN-107-*), drew the cap as its can and trimmed the tape square along the fin root fillets. Before D-88 (D-86/87): 1,007 bodies in 193 parts plus every routed wire; 0 penetrations > 0.05 mm, static and at both elevon limits; the tape skin is a solid (leads pass only through drawn slits); every wire end seated in its part or an in-line connector; no wire crosses or folds through itself (D-87). D-86 drew the 8 JR connectors (HRN-105-*), landed each conductor on its own bus bar, slit the tape, moved the lower signal lead under the tape and tied the phase leads. Before / after pictures: `review/inspection-2026-11-11/`. |
| Build animation | **New**: `showcase/animation/render_build.py` -> `showcase/animation/build/` (whole build, 49 s, plus one clip and end-state still per stage 2-11). Linked from `BUILD-GUIDE.md` and the Explorer. |
| Proof graph | **Clean** (0 drift, 0 errors), 4,249 nodes after D-86; 90 claims fail on margin (87 before D-85). The 3 new: `CL-F2-MASS` 135.2 g vs 129 g allocation, `CL-F2-I2C-LEN` 0.511 m vs 0.5 m, and `R-HARNESS-INSTALL` that rolls them up. CG and mass gate unchanged (the A3 roll-up uses the allocation). |
| Harness mass and I2C length | **Team-lead decision** (D-85, D-86 Open): harness now 140.9 g vs 129 g allocation (D-89); I2C 0.522 m vs 0.5 m (D-89: Y-splice on the GPS riser). F3 to confirm on arrival: FC connector types and positions, output-field pitch, RP3 pad order, GPS module connector, FC underside board-link header. Also D1 (longer JR recess, servo-groove corner relief) and F1 (35 mm bus bars, landing order, formed bends) to confirm. |
| MF-02 Jacobs access | **Team decision needed.** |

Next steps in order:
1. Owners re-check what this round changed: C6 the collar bond (D-81 notch, -0.9 % area) and the dog size; C3 the 4.8 mm
   recess-fillet leg (D-84 d); C4 mount rocking stiffness with the shorter outboard cheek (D-80).
2. All media are current with D-89 (regenerated 2026-11-13 from the final CAD, Blender 4.5.14 LTS): the 15 renders and site thumbnails
   (`showcase/tools/render_showcase.py`), the GA drawing (`showcase/drawing/`), the flight animation and GIF, the build
   animation, the STLs, the GLB and viewer data, the page snapshots (`showcase/pages/`, headless Chrome from
   `site/index.html`, which is now rebuilt from `site/app.html`). After any CAD change, re-run all of them.
3. Before any Fusion run or print: `python -I redesign/fusion/check.py`, `python -I redesign/collision/collide.py`,
   `python -B redesign/manufacturing/make_shop_files.py`.
4. Explorer artifact (private, owner Dillon's account): https://claude.ai/artifact/XYkihMreBq6Gn7deTEwSC8 . Republish from
   `redesign/site/app.html` with the same file list; the 3-D model loads from `data/assembly.glb.part1.js`, `part2.js` there
   (artifacts do not serve .glb and take at most 16 MB per file; `viewer/build_data.py` writes the parts), from
   `assets/k09l.glb` everywhere else. Publish in two calls (model, data, renders, drawing; then the animations).
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
