# Concept A quad tailsitter — design showcase

**UC Berkeley MEng capstone · Design-Build-Fly · $2,000 VTOL demonstrator.** Everything the redesign produced, in one
place that GitHub displays directly: CAD renders, flight and build films, the morphological chart and configuration
decision. The current design is **concept A** (D-182, 2026-11-14); its numbers, reports and status are in
[qp/README.md](qp/README.md), decisions in [params/CHANGE-LOG.md](params/CHANGE-LOG.md) (D-182 to D-200). The previous
design, K09-L, follows below as the record (its README, STATUS and HANDOFF describe K09-L).

> **Interactive version:** [`site/index.html`](site/index.html) is the Explorer web app: a rotatable 3-D model of concept A (aircraft, inside & wiring, exploded) with a vendor link or build clip for every part, the morphological chart, the concept A BOM and status, and every document. Open it from a local clone (double-click the `.bat` in the repo root). The Simulations tab is removed until concept A is final.

## Concept A (current design, D-182)

| | Value (2026-11-16) | Source |
|---|---|---|
| Wing, motors, pack | 0.90 m S5010 flying wing, two fins; 4 x T-Motor MN2212 KV780 with APC 9x4.5MR on 12 x 10 mm carbon arms from a printed hub; 4S 2000 mAh | [qp/README.md](qp/README.md) |
| Take-off mass, predicted | 1,456 g flat rule / 1,452 g itemised `EST` (target 1,460 g, weigh-in gate 1,470 g); basic 1,261.2 g, CG 20.5 mm aft of LE | [qp/A/MASS-GATE.md](qp/A/MASS-GATE.md), D-200 |
| Cost | $1,779.47 of $2,000; +$100.05 margin if unverified prices run 30 % over (G7 PASS) | [qp/A/BOM-A.csv](qp/A/BOM-A.csv), [bom_a.py](qp/A/bom_a.py) |
| 3-D gates | collision 0 at neutral, ±20° and ±21°; assembly 45 steps, 104/104 parts; exposed wire 0.87 strand-m | [qp/A/cad/out/ASSEMBLY.md](qp/A/cad/out/ASSEMBLY.md), [review/QP-5/HARNESS-ENCLOSED.md](review/QP-5/HARNESS-ENCLOSED.md) |
| Build | 45 steps, 37.7 h hands-on `EST` (cures and print time not counted), written guide for the team | [qp/A/BUILD-GUIDE-A.md](qp/A/BUILD-GUIDE-A.md) |

![Concept A in cruise attitude](showcase/concept-a/renders/hero-iso.webp)
*Concept A in cruise attitude: a 0.90 m flying wing with two fins and a four-arm motor cage carrying four APC 9x4.5MR
props. Rendered in Blender from the CAD model in [`qp/A/cad`](qp/A/cad) (real part geometry, no stand-ins).*

**How it flies** ([MP4](showcase/concept-a/animation/a-how-it-flies.mp4), 20 s; the real blades spin and are drawn with a blur fan):
vertical take-off on the fin tips, 90 degree pitch-over to cruise at 17 m/s, back-transition, landing. Phase timing is illustrative.

**How it is built** ([whole build, MP4](showcase/concept-a/animation/a-build.mp4), about 10 min): the 45 steps of
[`a_assembly_plan.py`](qp/A/cad/a_assembly_plan.py) in 10 stages, each with a step card (instruction, tools, the check
to make), callouts and a banner where a part is made rather than bought. It follows the written
[BUILD-GUIDE-A.md](qp/A/BUILD-GUIDE-A.md) step for step. Each part moves along the direction and travel of the
swept-path check ([`ASSEMBLY.md`](qp/A/cad/out/ASSEMBLY.md): 45 steps, 104 of 104 parts, 0 blocked). Approach
distances under 70 mm are drawn from 70 mm along the same direction (that extra length is not part of the check).
One clip per stage:

1. [Wing core and spar](showcase/concept-a/animation/stage-01.mp4) ([still](showcase/concept-a/animation/stage-01.webp))
2. [Cage unit: motor leads threaded, motors, props](showcase/concept-a/animation/stage-02.mp4) ([still](showcase/concept-a/animation/stage-02.webp))
3. [Rib saddles, phase-lead raceways, pack tray, hinge dampers](showcase/concept-a/animation/stage-03.mp4) ([still](showcase/concept-a/animation/stage-03.webp))
4. [Fin ribs and rib fairings](showcase/concept-a/animation/stage-04.mp4) ([still](showcase/concept-a/animation/stage-04.webp))
5. [Elevons, balance strips, lens caps](showcase/concept-a/animation/stage-05.mp4) ([still](showcase/concept-a/animation/stage-05.webp))
6. [Fins: fairings, root blocks, tubes](showcase/concept-a/animation/stage-06.mp4) ([still](showcase/concept-a/animation/stage-06.webp))
7. [Landing feet](showcase/concept-a/animation/stage-07.mp4) ([still](showcase/concept-a/animation/stage-07.webp))
8. [Servos, pushrods, horns, lead threading](showcase/concept-a/animation/stage-08.mp4) ([still](showcase/concept-a/animation/stage-08.webp))
9. [Avionics: pitot, plate, ESC, FC, leads](showcase/concept-a/animation/stage-09.mp4) ([still](showcase/concept-a/animation/stage-09.webp))
10. [Pack, XT60, strap, phase leads, bay cover](showcase/concept-a/animation/stage-10.mp4) ([still](showcase/concept-a/animation/stage-10.webp))

| | |
|---|---|
| ![hover-pose](showcase/concept-a/renders/hover-pose.webp) <br> Standing nose-up on its four fin-tip feet (take-off and landing pose). | ![exploded](showcase/concept-a/renders/exploded.webp) <br> Exploded view, labelled by subsystem. |
| ![cutaway-xray](showcase/concept-a/renders/cutaway-xray.webp) <br> X-ray: cage, pack tray, pack, flight controller, ESC and the harness. | ![front](showcase/concept-a/renders/front.webp) <br> Front view (orthographic). |
| ![side](showcase/concept-a/renders/side.webp) <br> Left side view (orthographic). | ![top](showcase/concept-a/renders/top.webp) <br> Top view (orthographic), nose up. |
| ![detail-wing](showcase/concept-a/renders/detail-wing.webp) <br> Wing: XPS core (ghosted), carbon spar, plugs, elevons, balance strips, hinge dampers. | ![detail-hub](showcase/concept-a/renders/detail-hub.webp) <br> Hub and cage: printed hub, CF arms, bridge tube, V struts, pack tray. |
| ![detail-propulsion](showcase/concept-a/renders/detail-propulsion.webp) <br> Propulsion station: MN2212 on a canted cup, APC 9x4.5MR prop, adapter, spinner nut. | ![detail-linkage](showcase/concept-a/renders/detail-linkage.webp) <br> Elevon linkage: servo, arm, pushrod, horn, balance strip, hinge damper. |
| ![detail-avionics](showcase/concept-a/renders/detail-avionics.webp) <br> Avionics plate, 4-in-1 ESC and pack in the tray. | ![detail-fin](showcase/concept-a/renders/detail-fin.webp) <br> Fin: carbon tube, rib tube on a spar saddle, root block, fairing, shoes and pads. |
| ![detail-foot](showcase/concept-a/renders/detail-foot.webp) <br> Landing foot: printed shoe and EVA/PE pad. | ![detail-harness](showcase/concept-a/renders/detail-harness.webp) <br> Harness: phase leads inside the arm tubes (arms ghosted), then through hub conduits and raceways under the pack tray to the ESC; servo leads in foam grooves; bay cover ghosted; XT60. |

No transport-box render yet: `qp/A` defines the packed envelope (0.90 x 0.50 x 0.39 m) but has no box CAD. General arrangement:
[showcase/concept-a/drawing/a-sheet.svg](showcase/concept-a/drawing/a-sheet.svg). Regenerate (details in the script docstrings): `showcase/tools/render_showcase.py --root qp/A/cad/model --spec blender/specs/showcase-a.json`, `showcase/animation/render_animation.py --concept a`, `showcase/concept-a/render_build_a.py`,
then `showcase/concept-a/publish_assets.py`.

## K09-L (previous design, kept as the record)

Everything from here down describes K09-L, which could not be built within $2,000 (D-182). It is kept as the
record; its lessons carry over to concept A.

**How it flies**: nothing tilts mechanically; differential thrust between the top-side and belly-side motors rotates the whole aircraft, helped by the elevons (20 s, [MP4 with full quality](showcase/animation/k09l-how-it-flies.mp4)):

![K09-L flight sequence: vertical take-off, 90° transition, cruise, back-transition, vertical landing](showcase/animation/k09l-how-it-flies.gif)

**How it is built**: build stages 2-11 step by step, each part fitted the way a person would on a swept path checked against everything already placed ([MP4, 2 min](showcase/animation/build/k09l-build.mp4); one clip per stage in [`BUILD-GUIDE.md`](BUILD-GUIDE.md); check report [`ASSEMBLY-CHECK.md`](showcase/animation/build/ASSEMBLY-CHECK.md)):

![K09-L build sequence, stage 11 end state](showcase/animation/build/stage-11.png)

![K09-L in cruise attitude](showcase/renders/hero-iso.png)
*K09-L in cruise attitude: a 1.15 m flying wing with two fins, each carrying a motor above and below the wing. It
stands on its fin tips, takes off as a quadcopter, pitches 90° to fly on the wing, and pitches back to land.
Rendered in Blender from the same scripts that build the Fusion model.*

**Contents:** [1 The aircraft](#1-the-aircraft-k09-l) · [2 3-D models](#2-3-d-models-rotate-on-github-k09-l) ·
[3 How the configuration was chosen](#3-how-the-configuration-was-chosen) ·
[4 Programme overview](#4-programme-overview-k09-l) · [5 Simulations](#5-simulations-k09-l) ·
[6 Every document](#6-every-document-k09-l) · [7 Interactive pages](#7-interactive-pages)

---

## 1. The aircraft (K09-L)

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

## 2. 3-D models (rotate on GitHub, K09-L)

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

**Morphological chart** (from the K09-L study; the Explorer's chart also shows concept A's path) — K09-L's path is the solid blue line, the runner-up K01's the dashed grey line; struck-out
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

## 4. Programme overview (K09-L)

The design was done by a single-role engineering team of AI agents ([TEAM.md](TEAM.md)): leadership and systems,
aerodynamics, structures, mechanical design (Fusion CAD), propulsion, electrical and avionics, manufacturing, test,
programme and support, each role producing its own work in [`team/<role>/`](team).

![Engineering team](showcase/pages/overview-team.png)
![Subsystems](showcase/pages/overview-subsystems.png)
![Status](showcase/pages/overview-status.png)

<details><summary><b>Full overview page as one image</b></summary>

![Overview page](showcase/pages/overview-full.jpg)

</details>

## 5. Simulations (K09-L)

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

## 6. Every document (K09-L)

| Area | Start here |
|---|---|
| Concept A: numbers, reports, build guide, BOM | [qp/README.md](qp/README.md) · [BUILD-GUIDE-A.md](qp/A/BUILD-GUIDE-A.md) · [BOM-A.csv](qp/A/BOM-A.csv) |
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
*Status of every number: PROPOSED or CHECKED by analysis; nothing is VERIFIED until physical tests. Nothing is bought
yet; Order 1 (the bench kit) goes out in early December 2026.*
