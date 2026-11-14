# K09-L quad tailsitter — design showcase

**UC Berkeley MEng capstone · Design-Build-Fly · $2,000 VTOL demonstrator.** Everything the redesign produced, in one
place that GitHub displays directly: CAD renders, interactive 3-D models, the morphological chart and configuration
decision, the engineering team, simulations and status. Numbers and sources live in [README.md](README.md);
what is finished and what is not is in [STATUS.md](STATUS.md); next steps for the team in [HANDOFF.md](HANDOFF.md).

> **Interactive version:** [`site/index.html`](site/index.html) is the whole programme as one web app: a rotatable 3-D model of the K09-L (aircraft, inside & wiring, structure, exploded), the clickable morphological chart, team, subsystems, simulations, status and documents. Open it from a local clone, or online once GitHub Pages is enabled for this branch.

**How it flies**: nothing tilts mechanically; differential thrust between the top-side and belly-side motors rotates the whole aircraft, helped by the elevons (20 s, [MP4 with full quality](showcase/animation/k09l-how-it-flies.mp4)):

![K09-L flight sequence: vertical take-off, 90° transition, cruise, back-transition, vertical landing](showcase/animation/k09l-how-it-flies.gif)

**How it is built**: build stages 2-11 step by step, each part fitted the way a person would on a swept path checked against everything already placed ([MP4, 2 min](showcase/animation/build/k09l-build.mp4); one clip per stage in [`BUILD-GUIDE.md`](BUILD-GUIDE.md); check report [`ASSEMBLY-CHECK.md`](showcase/animation/build/ASSEMBLY-CHECK.md)):

![K09-L build sequence, stage 11 end state](showcase/animation/build/stage-11.png)

![K09-L in cruise attitude](showcase/renders/hero-iso.png)
*K09-L in cruise attitude: a 1.15 m flying wing with two fins, each carrying a motor above and below the wing. It
stands on its fin tips, takes off as a quadcopter, pitches 90° to fly on the wing, and pitches back to land.
Rendered in Blender from the same scripts that build the Fusion model.*

**Contents:** [1 The aircraft](#1-the-aircraft) · [2 3-D models](#2-3-d-models-rotate-on-github) ·
[3 How the configuration was chosen](#3-how-the-configuration-was-chosen) ·
[4 Programme overview](#4-programme-overview) · [5 Simulations](#5-simulations) ·
[6 Every document](#6-every-document) · [7 Interactive pages](#7-interactive-pages)

---

## 1. The aircraft

![Programme overview: aircraft and key numbers](showcase/pages/overview-aircraft.png)

| | |
|---|---|
| ![Hover pose](showcase/renders/hover-pose.png) <br> Standing nose-up on its four fin-tip feet (take-off and landing pose). | ![Exploded view](showcase/renders/exploded.png) <br> Exploded view, labelled by subsystem. |
| ![Front view](showcase/renders/front.png) <br> Front view (orthographic). | ![Side view](showcase/renders/side.png) <br> Left side view (orthographic). |
| ![Top view](showcase/renders/top.png) <br> Top view (orthographic), nose up. | ![X-ray cutaway](showcase/renders/cutaway-xray.png) <br> X-ray: pod internals (flight controller, pack, tray, UBEC) and the wiring harness. |
| ![Wing detail](showcase/renders/detail-wing.png) <br> Wing: hot-wired XPS core (ghosted), carbon spar, four elevon panels. | ![Fin detail](showcase/renders/detail-fin.png) <br> Fin: carbon motor tube, through-core block, motor mounts, braces. |
| ![Pod detail](showcase/renders/detail-pod.png) <br> Pod: printed tray, 4S 6500 mAh pack, flight controller, GPS mast, pitot. | ![Landing foot detail](showcase/renders/detail-foot.png) <br> Landing foot: printed shoe and piston, crushable XPS cartridge, pad. |
| ![Propulsion detail](showcase/renders/detail-propulsion.png) <br> Propulsion station: motor, prop, 45 A ESC on the fin. | ![Mechanisms detail](showcase/renders/detail-mechanisms.png) <br> Elevon linkage: servo, arm, pushrod, horns, inter-panel rod. |
| ![Harness detail](showcase/renders/detail-harness.png) <br> Harness: pod bundle to the wing and fin bundles and each ESC. | ![Transport box](showcase/renders/transport-box.png) <br> Transport box (ghosted) with the aircraft in its foam cradles. |
| ![Fasteners detail](showcase/renders/detail-fasteners.png) <br> Fasteners as CAD parts: motor screws, pinch bolt, nyloc, washers, prop nut (one motor station). | |

Regenerate the renders: `blender -b --factory-startup -P redesign/showcase/tools/render_showcase.py`
(spec `redesign/blender/specs/showcase.json`). The CAD itself is in [`subsystems/*/fusion/`](subsystems); build it in
Autodesk Fusion with `fusion/BuildAll` (Utilities → Scripts and Add-Ins → Run).

## 2. 3-D models (rotate on GitHub)

Click a file: GitHub opens it in an interactive 3-D viewer (drag to rotate, scroll to zoom). Units are millimetres.

| Model | Contents | Triangles |
|---|---|---|
| [**k09l-assembly.stl**](showcase/stl/k09l-assembly.stl) | whole flight aircraft | 110,336 |
| [wing.stl](showcase/stl/wing.stl) | wing core, spar, elevons | 45,366 |
| [fins.stl](showcase/stl/fins.stl) | fins, motor tubes, mounts | 17,382 |
| [harness.stl](showcase/stl/harness.stl) | harness bundles and routed wires | 28,300 |
| [propulsion.stl](showcase/stl/propulsion.stl) | motors, props, adapters, ESCs | 7,936 |
| [landing.stl](showcase/stl/landing.stl) | feet and spares kit | 5,076 |
| [mechanisms.stl](showcase/stl/mechanisms.stl) | servos, horns, pushrods | 3,968 |
| [pod.stl](showcase/stl/pod.stl) | pod shell, tray, hatch, handle | 2,652 |
| [avionics.stl](showcase/stl/avionics.stl) | FC, GPS, receiver, airspeed, pitot | 1,092 |
| [power.stl](showcase/stl/power.stl) | pack, power board, UBEC | 296 |
| [transport.stl](showcase/stl/transport.stl) | transport box and cradle | 536 |

## 3. How the configuration was chosen

43 concepts were generated from an 11-function morphological chart, audited for completeness three times, screened
to 7, each sized, priced and challenged by a skeptic, scored by three judges, and settled by a tie-break on real wind
data and pessimistic budget numbers. Full write-up: [config-study/README.md](config-study/README.md) and
[CONFIGURATION.md](CONFIGURATION.md).

**Morphological chart** — K09-L's path is the solid blue line, the runner-up K01's the dashed grey line; struck-out
options were used only by rejected concepts.

![Morphological chart](showcase/pages/morph-chart.png)

![The decision](showcase/pages/decision-hero.png)

<details><summary><b>All 43 concepts and why each was kept, merged or dropped</b></summary>

![43 concepts](showcase/pages/concepts-table.png)

</details>

<details><summary><b>The shortlist of seven, with skeptic-corrected numbers</b></summary>

![Shortlist](showcase/pages/shortlist.png)

</details>

<details><summary><b>Trade matrix, gates and tie-break</b></summary>

![Trade matrix](showcase/pages/trade-matrix.png)

</details>

<details><summary><b>Accepted risks, reversal conditions, pre-order checklist</b></summary>

![Risks](showcase/pages/risks.png)

</details>

## 4. Programme overview

The design was done by a single-role engineering team of AI agents ([TEAM.md](TEAM.md)): leadership and systems,
aerodynamics, structures, mechanical design (Fusion CAD), propulsion, electrical and avionics, manufacturing, test,
programme and support, each role producing its own work in [`team/<role>/`](team).

![Engineering team](showcase/pages/overview-team.png)
![Subsystems](showcase/pages/overview-subsystems.png)
![Status](showcase/pages/overview-status.png)

<details><summary><b>Full overview page as one image</b></summary>

![Overview page](showcase/pages/overview-full.jpg)

</details>

## 5. Simulations

Run on the settled geometry with XFOIL, AVL, SU2 (CFD and linear-elastic FEA), blade-element models and NumPy beam
models, each with a convergence check and a comparison to hand calculations. Reports in each `team/<role>/SIMULATION-REPORT.md`.

![Simulation summary](showcase/pages/overview-simulations.png)

| | |
|---|---|
| ![Airfoil polars](team/B2/fig/B2-01-polars.svg) <br> **Wing aero (B2):** XFOIL polars at flight Reynolds numbers. [Report](team/B2/SIMULATION-REPORT.md) | ![Transition corridor](team/B1/fig-b1-corridor-asdesigned.svg) <br> **Performance (B1):** transition corridor, as designed. [Report](team/B1/SIMULATION-REPORT.md) |
| ![CG stations](team/B3/fig-b3-cg-stations.svg) <br> **Stability (B3):** CG stations against the AVL neutral point. [Report](team/B3/SIMULATION-REPORT.md) | ![Cruise power](team/B4/out/fig-b4-01-cruise-power.svg) <br> **Props (B4):** cruise power from blade-element models. [Report](team/B4/SIMULATION-REPORT.md) |
| ![Wing deflection](team/C2/fig/C2-01-deflection-envelope.svg) <br> **Wing structure (C2):** FEA deflection envelope. [Report](team/C2/SIMULATION-REPORT.md) | ![Campbell diagram](team/C4/fig-c4-campbell.svg) <br> **Fin structure (C4):** Campbell diagram, modes vs motor speed. [Report](team/C4/SIMULATION-REPORT.md) |
| ![Pod bond](team/C3/fea/fig-c3-fea-02-bond-peel.svg) <br> **Pod structure (C3):** FEA bond peel stress. [Report](team/C3/SIMULATION-REPORT.md) | ![Landing envelope](team/C5/sim/fig/fig-c5-s1-envelope.svg) <br> **Landing (C5):** hard-landing envelope. [Report](team/C5/SIMULATION-REPORT.md) |
| ![ESC cooling CFD](team/E3/figs/fig-e3-02-cfd-grid.svg) <br> **Thermal (E3):** SU2 CFD grid study for ESC cooling. [Report](team/E3/SIMULATION-REPORT.md) | ![Convergence](team/B1/fig-b1-convergence.svg) <br> **Performance (B1):** convergence check. |

## 6. Every document

| Area | Start here |
|---|---|
| Front door, key numbers, directory map | [README.md](README.md) |
| Bill of materials (priced, with order plan) | [Excel: team/I1/K09L-BOM.xlsx](team/I1/K09L-BOM.xlsx) · [BOM.csv](team/I1/BOM.csv) · [ORDER-PLAN.md](team/I1/ORDER-PLAN.md) |
| Proof chains (every number traced to its source) | [PROOFS.md](PROOFS.md) |
| What is done, what fails, what needs tests | [STATUS.md](STATUS.md) |
| What the team does next, what to order | [HANDOFF.md](HANDOFF.md) |
| How to continue the work | [RESUME.md](RESUME.md) |
| Configuration decision and study | [CONFIGURATION.md](CONFIGURATION.md) · [config-study/](config-study/README.md) |
| Requirements and verification | [team/A2/](team/A2) |
| Parameters and mass/CG | [params/params.json](params/params.json) · [MASS-CG.md](MASS-CG.md) |
| Subsystem specs (one page each) | [wing](subsystems/wing/SPEC.md) · [fins](subsystems/fins/SPEC.md) · [pod](subsystems/pod/SPEC.md) · [landing](subsystems/landing/SPEC.md) · [propulsion](subsystems/propulsion/SPEC.md) · [power](subsystems/power/SPEC.md) · [avionics](subsystems/avionics/SPEC.md) · [harness](subsystems/harness/SPEC.md) · [mechanisms](subsystems/mechanisms/SPEC.md) · [flight software](subsystems/flight-software/SPEC.md) · [transport](subsystems/transport/SPEC.md) · [ground](subsystems/ground/SPEC.md) |
| Each engineer's work | [team/](team) (one folder per role, each with SUMMARY.md) |
| Interfaces (knowledge graph) | [interfaces/](interfaces) |
| Design system (visual standard) | [design-system/README.md](design-system/README.md) |

## 7. Interactive pages

These are HTML and open in a browser (from a local clone, or online once GitHub Pages is enabled for this branch):
[`index.html`](index.html) (programme overview) · [`config-study/web/index.html`](config-study/web/index.html)
(decision page with the clickable morphological chart) · [`viewer/index.html`](viewer/index.html) (3-D aircraft
viewer) · [`proofs/viewer/index.html`](proofs/viewer/index.html) (3-D proof-chain graph).

---
*Status of every number: PROPOSED or CHECKED by analysis; nothing is VERIFIED until physical tests. The CAD scripts
have not yet been run in Autodesk Fusion itself.*
