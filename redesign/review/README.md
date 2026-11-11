# Buildability review: index

Five independent reviews of how K09-L would actually be built (2026-11-11, branch `redesign/v1`), and one
synthesis. Start with the synthesis.

| File | What it covers | Findings |
|---|---|---|
| [BUILDABILITY-REVIEW.md](BUILDABILITY-REVIEW.md) | **Synthesis.** Verdict, the mass/CG FAIL (BR-00), what to fix before CFD/FEA and before ordering, ranked master table, team decisions, budget and schedule impact | 6 Blocker, 30 Major, 37 Minor after merging and verification |
| [STRUCTURE-WING.md](STRUCTURE-WING.md) | Spar, core, through-core blocks, fin-to-wing and foot-to-fin joints, skin, repairability (SW-xx) | 1 / 7 / 10 |
| [MOTOR-MOUNTS.md](MOTOR-MOUNTS.md) | Motor mounts, slip clamp, screws, props, tip-over, vibration (MM-xx) | 1 / 6 / 7 |
| [SERVOS-CONTROLS.md](SERVOS-CONTROLS.md) | Servos, linkage, hinges, elevon panels, hover use of the surfaces (SC-xx) | 0 / 5 / 9 |
| [WIRING-BATTERY.md](WIRING-BATTERY.md) | Power stack, CoreWing board, harness, disconnects, pack station, avionics wiring (WB-xx) | 1 / 6 / 11 |
| [MANUFACTURING.md](MANUFACTURING.md) | Jacobs Hall capabilities, process table, shop outputs, tolerances, week-by-week plan (MF-xx) | 2 / 14 / 7 |
| [img/](img/) | Close-up renders of the motor mount made for the review | 3 images |
| [../BUILD-GUIDE.md](../BUILD-GUIDE.md) | Brief build instructions in 12 stages, with the review warnings inline | — |

Counts per review are Blocker / Major / Minor as each reviewer wrote them.
