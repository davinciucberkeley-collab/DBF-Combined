# Redesign v1 — shared brief for every agent

You are one of the specialist agents designing a VTOL drone from the ground up for a UC Berkeley MEng capstone team.
**The configuration is chosen by the configuration study** (`redesign/config-study/README.md` and
`redesign/CONFIGURATION.md` once written) — before that, build only configuration-independent tools. Real constraints:
$2,000 total budget (hard), VTOL, easy to transport (fits a car), student-built (Jacobs Hall shop: 3D printers, laser
cutter, basic machining; hot-wire foam), parts ordered ~mid-December 2026, build January–February 2027, everything
finished by end of April 2027. Read `redesign/inputs/ADVISOR-XV24-LESSONS.md` and
`redesign/inputs/MENTOR-GUIDANCE-2026-11-04.md`.

Repo root: `C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined` (branch `redesign/v1`).
Everything new lives under `redesign/`. The rest of the repo is the **previous design, read-only reference**: reuse
its analysis and lessons (`analysis/`, `docs/DESIGN-BASIS.md`, `docs/research/`, `cad/params.txt`,
`cad/hardware.json`, `fusion/`), but do not edit anything outside `redesign/`.

Inputs: `redesign/inputs/DECISIONS-ADOPTED.md` — written for the old C0 configuration. Its component and safety
findings (connector current ratings, I2C address clash, wire gauge derating, vendor comparisons, thermal method) are
useful evidence; its configuration-specific values are void until the configuration study says otherwise.

## The team lead's three goals (judge every output against these)
1. **Digestible** — a teammate understands a subsystem in 5 minutes from its one-page SPEC.md. Tables over prose. No
   filler, no marketing words, no repeated text. Numbers carry units.
2. **Easy to check** — every number traces to `params.json` or a cited calculation; every part has an interface
   entry; every claim has a "how to verify" line. Anything unverified is marked `UNVERIFIED`.
3. **Easy to build** — prefer bought parts, flat/laser-cut, printed and hot-wire foam over machining; standard
   fasteners (few sizes); numbered build steps a student can follow.

The mentor's guidance: buildability before simulation; parts must actually connect (no floating parts); every part
connected structurally *and* (where relevant) electrically/thermally; interfaces as a knowledge graph.

## Ownership (avoid collisions — you may only write inside your own folder)
| Agent | Folder |
|---|---|
| 1 Chief engineer / integrator | `redesign/params/`, `redesign/README.md`, `redesign/MASS-CG.md` |
| 2 Interface / knowledge-graph keeper | `redesign/interfaces/`, `redesign/fusion/` (framework, stub, checker, `build_all.py`) |
| 3–8 Mechanical (wing, fuselage, booms, tail, landing gear, pusher) | `redesign/subsystems/<name>/` |
| 9–11 Electrical (power, harness, avionics) | `redesign/subsystems/<name>/` |
| 12–14 Analysis (aero, structures, thermal) | `redesign/analysis/<name>/` |
| 15 Manufacturing | `redesign/manufacturing/` |
| 16 Cost | `redesign/cost/` |
| 17 Test | `redesign/test/` |
| 18 Critic | `redesign/reviews/` |
| Tooling: Blender backend and renders | `redesign/blender/` |
| Tooling: proof-chain graph and 3D viewer | `redesign/proofs/` |
| Tooling: aircraft web viewer | `redesign/viewer/` |
| Tooling: build-manual kit | `redesign/manual-kit/` |
| Configuration study | `redesign/config-study/` |
| Visual designer (design system) | `redesign/design-system/` — **every visual output (pages, viewers, renders, diagrams, docs) follows it once it exists** |

To change something you don't own (a shared parameter, another subsystem's interface), add an entry to
`<your folder>/CHANGE-REQUESTS.md` (what, why, numbers). The integrator resolves them. Never edit another folder.
Do not commit; the orchestrator commits between phases.

## Single sources of truth
- **Numbers:** `redesign/params/params.json` (owned by the integrator). Subsystem scripts read it; never hard-code a
  dimension that exists there. Subsystem-local dimensions go in `<subsystem>/params.json`.
- **Connections:** `redesign/interfaces/interfaces.json` — the knowledge graph. Nodes = parts; edges = connections,
  and the connection type is its own node (e.g. `bolt M3x12`, `epoxy bond`, `JST-GH 6-pin`, `revolute hinge`).
  Each subsystem declares its parts and interfaces in `<subsystem>/interfaces.json` using the schema in
  `redesign/interfaces/SCHEMA.md`; the keeper merges and checks them.
- **Parts:** `<subsystem>/parts.csv` with columns
  `part_id,name,qty,make_or_buy,process,material,mass_g,unit_cost_usd,vendor_or_file,notes`
  (part_id prefix per subsystem: WNG, FUS, BOM(booms)=BMS, TAL, GER, PSH, PWR, HRN, AVN).

## Fusion CAD (all CAD is Autodesk Fusion)
Fusion is not installed on the orchestrator's machine. CAD is therefore **Python scripts for the Fusion API**
(`adsk.core`, `adsk.fusion`), framework in `redesign/fusion/` (see its README once agent 2 writes it):
- One module per subsystem: `redesign/subsystems/<name>/fusion/<name>.py`, exposing `build(ctx)` that creates that
  subsystem's components, bodies and joints using framework helpers and `params.json`.
- `redesign/fusion/build_all.py` is the single script a teammate runs in Fusion (Utilities → Scripts and Add-Ins) to
  build the full assembly.
- Every module must pass `python -I redesign/fusion/check.py` (runs all modules against an `adsk` stub, verifies they
  execute, every component has mass/material, every declared interface exists as a joint/contact, nothing floats).
  Run it before you finish and report the result.
- Keep geometry simple and parametric (sketch + extrude/revolve/loft). Real Fusion behaviour can't be tested here, so
  mark anything non-trivial in the API `UNVERIFIED-IN-FUSION`.

## Every subsystem folder contains
- `SPEC.md` — ONE page: purpose · key numbers table (with source) · parts summary · interfaces (to whom, how) ·
  mass budget vs allocation · open issues · how to verify.
- `parts.csv`, `interfaces.json`, `params.json` (local), `fusion/<name>.py`
- `BUILD.md` — numbered build steps (tools, fixtures, cure times, checks after each step).
- `CHANGE-REQUESTS.md` if you need anything from others.

## Animations (build and test instructions)
Where a still image is not enough, the build and test instructions get a short animation, rendered in Blender from
the same geometry as the CAD (Blender 4.2.3 encodes MP4/H.264 itself; no extra software). Use one when motion is the
point: a part sliding/rotating into place, fastener insertion order, wing removal for transport, control-surface or
tilt throws and clearance, harness routing through a structure, connector mating, a test setup (thrust stand, CG
balance, range check) and the flight-test sequence (hover → transition → cruise → land). Rules: 3–10 s loops, one
idea per clip, same camera/style as the stills (design system), highlighted moving parts, ghosted context, a poster
frame (PNG) for print, ≤ 1080p and < 3 MB each (MP4 H.264, plus WebM if small), embedded in HTML as
autoplay-muted-loop with controls. Videos under `redesign/` are stored as normal Git blobs (not LFS) so GitHub Pages
can serve them — keep them small. Don't animate what a still shows well.

## Rules
- No secrets in files. Do not install software; Python 3 standard library only (run with `python -I`).
- Web lookups for datasheets/prices are fine; cite URLs.
- Your final reply is read by the orchestrator: be short and factual (what you produced, check result, open issues,
  change requests filed).
