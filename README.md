# DBF-Combined: K09-L quad-tailsitter VTOL (UC Berkeley MEng capstone)

K09-L is the VTOL demonstrator a four-person UC Berkeley MEng capstone team will build and fly. It is a quad
tailsitter: a 1.15 m flat flying wing with two fins, each fin carrying two fixed motors (four in all, one above and
one below the wing on each side), and two elevons for roll and pitch in cruise. It stands on its four fin tips, takes
off as a quadcopter, pitches 90° to cruise on the wing at 16 m/s, and pitches back to land. Power is one 4S 6500 mAh
LiPo; the flight controller runs ArduPilot Plane in tailsitter mode. A configuration study of 43 concepts picked it
([CONFIGURATION.md](redesign/CONFIGURATION.md)). The constraints are hard: **$2,000 total budget**, student-built at
Jacobs Hall, transportable in one piece in a car, parts ordered mid-December 2026, build January to early
February 2027, everything done by **2027-04-30**. The CAD is scripted for Autodesk Fusion only.

![K09-L in cruise attitude, isometric render](redesign/showcase/renders/hero-iso.png)

*K09-L in cruise attitude, rendered in Blender from the same scripts that build the Fusion model. Status: design
complete on paper, nothing bought, built or flown yet.*

## Open it

- **Windows, with Python installed:** double-click `00 - OPEN THE K09-L EXPLORER (double-click me).bat` in the repo
  folder. It serves `redesign/site/` on `http://localhost:8765/` and opens the K09-L Explorer in your browser: a
  rotatable 3-D model, the configuration decision, the engineering team, simulations, proof chains, the BOM and every
  document. Close the console window to stop it.
- **On GitHub, no install:** read [redesign/SHOWCASE.md](redesign/SHOWCASE.md) for the renders, the flight animation,
  STL models that rotate in the browser, the morphological chart, the decision and the simulation figures.
- **Building it:** [redesign/BUILD-GUIDE.md](redesign/BUILD-GUIDE.md) is the short, ordered build guide. Read
  [redesign/review/BUILDABILITY-REVIEW.md](redesign/review/BUILDABILITY-REVIEW.md) first: 6 blockers and 30 major
  build problems found by a buildability review, to fix before more CFD/FEA or any cutting.

## Key numbers

Frame revision A1-R5 (2026-11-10). "Modelled" means computed by analysis or simulation; no number is verified by test.

| Item | Value | State | Source |
|---|---|---|---|
| Span × chord | 1.15 × 0.32 m, one piece | proposed | [`redesign/params/params.json`](redesign/params/params.json) `wing` |
| Take-off mass, basic / predicted | 2,374 g / 2,493 g against a 2,600 g gate (margin 107 g vs 100 g overrun); landing 70 g vs 48 g allocated; predicted CG 1.2 mm aft of range | modelled | [`redesign/MASS-CG.md`](redesign/MASS-CG.md) (A3-R7) |
| Propulsion | 4 × SunnySky X3108S, APC 11×5.5MR props, 4 × 45 A ESCs, 4S 6500 mAh pack | proposed | [`redesign/README.md`](redesign/README.md) |
| Hover T/W, fresh pack / worst pack | 2.49 / 2.12 | unverified (thrust stand owed) | [`redesign/README.md`](redesign/README.md) key numbers |
| Cruise speed / power | 16 m/s / 240 W (E1 disputes: 246 W) | unverified | [`redesign/STATUS.md`](redesign/STATUS.md) issue 5 |
| Cruise after 2 min hover, base / pessimistic | 12.0 / 6.4 min | unverified | [`redesign/README.md`](redesign/README.md) key numbers |
| Stall at forward CG | 11.99 m/s against a 12.0 m/s limit | unverified | [`redesign/team/B2/SIMULATION-REPORT.md`](redesign/team/B2/SIMULATION-REPORT.md) |
| Budget | $2,000 hard | requirement | [`redesign/BRIEF.md`](redesign/BRIEF.md) |
| BOM spend / reserve, baseline | $1,588.38 / $411.62 | prices unverified | [`redesign/team/I1/bom_summary.json`](redesign/team/I1/bom_summary.json) |
| BOM spend / reserve, pessimistic | $1,673.59 / $326.41 (gate: reserve ≥ $309, one crash) | holds only with two Jacobs Hall tool loans | [`redesign/team/I1/ORDER-PLAN.md`](redesign/team/I1/ORDER-PLAN.md) |
| Orders | early order ~2026-11-20 ($1,064.39); main order 2026-12-15 ($430.83) | planned | [`redesign/team/I1/ORDER-PLAN.md`](redesign/team/I1/ORDER-PLAN.md) |
| Build and finish | build start 2027-01-19 (proposed), first hover by build week 4, complete by 2027-04-30 | planned | [`redesign/params/params.json`](redesign/params/params.json) `schedule` |
| Transport | one-piece box 1.25 × 0.55 × 0.54 m; field set-up about 5 min, one person | proposed | [`redesign/README.md`](redesign/README.md) |
| Requirements | 59 total: 0 verified, 1 checked, 1 proposed, 57 unverified; 11 show a fail (most are stale claims) | | [`redesign/STATUS.md`](redesign/STATUS.md) |
| Proof graph | 4,211 nodes, 13,734 links; clean build (0 drift, 0 errors); 86 claims fail on margin | | [`redesign/PROOFS.md`](redesign/PROOFS.md) |

## Where things are

| Path | What it is |
|---|---|
| [`redesign/`](redesign/README.md) | Everything for K09-L. Start with its [README](redesign/README.md) (aircraft, key numbers, subsystems, simulations) |
| [`redesign/config-study/`](redesign/config-study/README.md) | How K09-L was chosen: requirements, morphological chart, 43 concepts, shortlist, judging, tie-break. Decision: [`CONFIGURATION.md`](redesign/CONFIGURATION.md) |
| [`redesign/team/<role>/`](redesign/TEAM.md) | One folder per engineering role (A systems, B aero, C structures, D CAD, E propulsion, F electrical, H test, I programme, J support), each with `SUMMARY.md`, scripts, `claims.json` and change requests |
| [`redesign/params/`](redesign/params/params.json) | `params.json` (every top-level number), [`CHANGE-LOG.md`](redesign/params/CHANGE-LOG.md) (decisions D-01 to D-73), `mass_budget.json` |
| [`redesign/subsystems/`](redesign/subsystems/wing/SPEC.md) | Per-subsystem spec, parts list, interfaces and Fusion module (wing, fins, pod, landing, propulsion, power, avionics, harness, mechanisms, transport, flight software, ground) |
| [`redesign/interfaces/`](redesign/interfaces/REPORT.md) | Interface graph (parts and joints) and its checker `merge_check.py` |
| [`redesign/fusion/`](redesign/fusion/DATUMS.md) | Fusion framework: `BuildAll` script, backends, `check.py`, skeleton, datums |
| [`redesign/proofs/`](redesign/PROOFS.md) | Proof chains from requirement to claim to calculation to source; `build_graph.py` rebuilds and flags drift |
| `redesign/site/` | The K09-L Explorer web app opened by the `.bat` file |
| [`redesign/showcase/`](redesign/SHOWCASE.md) | Renders, flight animation, STL models, page snapshots |
| [`redesign/design-system/`](redesign/design-system/README.md) | Visual standard for every output (tokens, components, Blender style) |
| BOM | [`redesign/team/I1/K09L-BOM.xlsx`](redesign/team/I1/K09L-BOM.xlsx) (Excel with live formulas), [`BOM.csv`](redesign/team/I1/BOM.csv), [`ORDER-PLAN.md`](redesign/team/I1/ORDER-PLAN.md) |
| Legacy (C0 era) | `analysis/`, `cad/` (SOLIDWORKS), `docs/`, `firmware/`, `review/`, the root `*.html` pages, `inventory/`, `fusion/` (C0 v0.3.1 scripts), `concepts/`, `sim/`, `explorations/tiltwing/`, `tools/`, [`DECISIONS.md`](DECISIONS.md). Imported on 2026-11-08 from DBF-VTOL, DillonVTOL, TiltWing and OpenCAEModel; superseded by K09-L. Source commits and what was left out: [`PROVENANCE.md`](PROVENANCE.md) |

## Status and next steps

As of 2026-11-10 ([`redesign/STATUS.md`](redesign/STATUS.md), [`redesign/HANDOFF.md`](redesign/HANDOFF.md)):

- **Done on paper:** frame, analysis, detail analysis, CAD for ten subsystem modules, mass and CG roll-up, and a
  simulation round (XFOIL, AVL, SU2 CFD and FEA, 6-DOF landing, thermal). The simulation round found four
  requirements failing as designed; decisions D-61 to D-73 fix them, and several analyses still owe a re-run on the
  fixes.
- **Modelled only:** every mass, thrust, stall, structural and thermal number. The Fusion scripts have run only in a
  stub backend, never in Fusion itself. The flight parameter file has never been loaded on a board or run in SITL.
- **Open issues that matter most:** the fin-station collar fails on the latest torsion load (do not print collars
  yet); the budget reserve holds only if Jacobs Hall lends the soldering and hot-wire gear (request due 13 Nov);
  the mass reserve has 0 g free; stall and transition margins sit inside model uncertainty.
- **Before the mid-December order:** build and fly a $40 foam-board twin on the real electronics, at least 10 h of
  SITL, an anemometer check at Richmond Field Station, the early order (~20 Nov), and a carbon-tube bend test by
  10 Dec. If the twin fails the 5 m/s hover or a transition, reverse to the K01 lean quadplane
  ([CONFIGURATION.md](redesign/CONFIGURATION.md)).
- **Then:** main order 2026-12-15, build January to early February 2027, flight testing through April, done by
  2027-04-30.

The human decisions (keep or reverse K09-L, the loan request, the first Fusion run, order approval, pilot, cars) are
listed with owners and dates in [`redesign/HANDOFF.md`](redesign/HANDOFF.md).

### Resume the work

[`redesign/RESUME.md`](redesign/RESUME.md) explains how to restart the design programme (remaining phases: build and
programme planning, media, design review) and lists the checks to run before any meeting.

## Legacy: C0 lift + cruise

Before K09-L the team's baseline was C0, a 2.4 m twin-boom quadplane with four lift rotors and a pusher, designed in
SOLIDWORKS. The configuration study superseded it on 2026-11-09. Its files remain at the repo root for reference;
[`PROVENANCE.md`](PROVENANCE.md) records where each came from, and the design review is
[`VTOL-Review.html`](VTOL-Review.html) (download and open locally).
