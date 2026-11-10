# Propulsion stations (PRP) — SPEC

Owner E1 · status `MODELLED` (`check.py`: propulsion 0 errors) · every bought-part dimension `UNVERIFIED` until
`T-E1-MOTOR-RM` · 2026-11-09, rev 4.

**Purpose.** Four fixed motor stations UR / UL / LR / LL at y ±0.32, z ±0.19: motor, prop adapter, prop and ESC,
mounted on D3's canted ASA mounts and ESC pads. They lift 2.6 kg in hover and drive cruise at 16 m/s.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Motor / ESC / prop | SunnySky X3108S KV900 / LANRC 45 A (Bluejay) / APC 11×5.5MR (UL, LR) + MRP (UR, LL) | — | `params.json#propulsion` | `PROPOSED` |
| Hover T/W fresh with the 100 A limiter / worst pack state | 2.47 / 2.12 (gate 2.0 / 1.6) | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Per-motor current, limited / unlimited burst at 16.8 V | 24.8 / 51.6 (motor 25, ESC 55 for 10 s) | A | `CL-E1-ILIM-I`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Motor face (on the axis) · cant | x 0.0309 (`DP-MOTOR-FACE`) · 7° tangential | m · ° | D3 `fin_detail.mount`, D-27 | `PROPOSED` |
| Stack: base face → bell top → hub centre → post tip | 26.5 → 32.85 → 37.3 → 48.05 | mm | `ASM-E1-STACK`, `CL-E1-STACK-PROP-PLANE` | `UNVERIFIED` |
| Modelled prop hub x (datum `DP-PROP` −0.0077) | −0.0062 (−0.0077 once D3 sets `face_ahead_m` 0.0025) | m | `CL-E1-CAD-HUB-X` | `MODELLED` |
| Prop plane to mount collar / 0.14 D | 38.0 / 39.1 mm = 0.97 | — | `CL-E1-CAD-PROP-GAP` | **FAIL** → CR-E1-22 |
| Prop keep-out on the canted axis: radius / axial half (blade 10 + 25) | 164.7 / 35 | mm | `CL-E1-KO-HALF` (CR-A5-21) | `MODELLED` (`check.py` 0 hits) |
| M6 prop nut: thread left past the full nut | 0.11 | mm | `CL-E1-NUT-ENGAGE` | `UNVERIFIED` |
| Adapter screws M3×4 strip RF at 2.0 / 2.5 mm, 0.5 N·m (deviation D-58, needs ≥ 2.5 mm bell thread; M3×5 if ≥ 3.0 mm thread and 4.0 mm free depth) | 1.70 / 2.12 (≥ 1.5) | — | `CL-E1-ADAPTER-STRIP`, `-RF-NOM`, `-THREAD-D58` | `UNVERIFIED` |
| ESC on pad: length ratio / strap-slot clearance ratio | 1.02 / 0.90 | — | `CL-E1-ESC-PAD-LEN`, `CL-E1-ESC-SLOT` | **FAIL** slot → CR-E1-30 |
| ESC / motor peak, mission design case | 61.6 / 65.8 (limits 85 / 80) | °C | `CL-E3-ESC-PEAK`, `CL-E3-MOTOR-PEAK` | `UNVERIFIED` |
| ESC envelope proud of the pad at the strap / frontal | 7.5 / 172.5 | mm / mm² | `CL-E1-ESC-PROUD`, `-FRONTAL` (B4) | `UNVERIFIED` |
| Mass (4 stations) vs allocation | 462.0 / 462 | g | `CL-E1-MASS-PRP`, D-48 | `UNVERIFIED` (weigh) |

## Parts (per station ×4; `parts.csv`, CAD `fusion/propulsion.py`)

| Id | Part | Mass g | CAD envelope | Status |
|---|---|---|---|---|
| `PRP-001-<st>` | Motor X3108S KV900, factory leads, 4 × M3×8 screws (`PRP-005`) | 84.2 | base boss Ø30 × 3, bell Ø38 × 23, shaft Ø4 stub, rear E-clip, phase-lead exit outboard | `MODELLED` |
| `PRP-004-<st>` | Bolt-on adapter M6×1 (LH on CW motors), washer 6×12×1.0, nut ISO 4032 | 6.7 | base Ø18 × 6.35 with Ø4 × 8.5 pilot, post Ø6 × 15.2, washer, hex nut | `MODELLED` |
| `PRP-003-<st>` | APC 11×5.5MR / MRP + LPAR06E ring | 17.0 | hub Ø16.5 × 8.89, two twisted flat-plate blades, parked spanwise | `MODELLED` |
| `PRP-002-<st>` | ESC LANRC 45 A in heat-shrink, power leads removed (F2 solders 16 AWG to the pads) | 7.6 | 45 × 20 × 6 box on the pad (`ASM-E3-ESC`) | `MODELLED` |
| Spares (not flown) | 1 motor, 4 ESC, 4 props 11×5.5, 4 props 11×4.5 (stand A/B), 4 screws, 1 nut set | — | — | `PROPOSED` |

Rotation from the nose (F4): UR, LL CW (MRP, LH adapter); UL, LR CCW (MR, RH adapter).

## Interfaces (`interfaces.json`; joint stacks there)

| Edge | To | How | Owner |
|---|---|---|---|
| `E-PRP-01…04` | adapter → motor bell | 4 × M3×4 12.9 (supplied), 2.5 mm engagement (min 2.0 by deviation D-58, conditional on ≥ 2.5 mm bell thread; M3×5 if the bell allows), 0.5 N·m + Loctite 243, 2.0 mm key | propulsion |
| `E-PRP-05…08` (field) | prop → adapter | M6×1 nut + 1.0 mm washer, 1.5 N·m bell held, 10 mm spanner | propulsion |
| `E-FIN-61…64` | motor → canted ASA plate | 4 × M3×8 A2, 3.5 mm engagement, 0.20 N·m + 243 on the tip | fins (acknowledged) |
| `E-FIN-65…68` | ESC → ASA pad | one 10 mm hook-and-loop strap, FET side out | fins (acknowledged) |
| `E-HRN-17…20` | ESC phase end → motor lead exit | soldered, staggered splices (F2) | harness (acknowledged) |
| `E-TRN-17…20` | prop → box tray slot (stowed) | prop on edge in a 285 × 30 × 40 slot | transport (acknowledged) |
| Pending (`acknowledges_pending`) | ESC power `E-HRN-13…16`, DShot `E-HRN-24…27`, cap leads `E-HRN-34…37`; thermal `E-FIN-81…88` | in A4's plan, not yet declared | harness, fins |

Keep-outs `KO-PROP-<st>` (Ø 0.279 + 2 × 0.025, ±0.035 axial) sit on the modelled hubs along the 7° canted shaft axis (CR-A5-21).

## Open issues

1. Prop plane 1.1 mm too close to the mount collar (`CL-E1-CAD-PROP-GAP` 0.97): D3 `face_ahead_m` → 0.0025 (CR-E1-22).
2. Strap slots on the 28 mm pad overlap the 20 mm ESC by 1 mm a side: pad height → 31 mm (CR-E1-30).
3. Cant sense: on D3's plate the UR side force gives +0.045 N·m/N about +x and opposes the CW reaction torque (F4 `CL-F4-CANT-SENSE-D3`): swap prints A/B (CR-E1-32). The CAD follows `cant_sense_UR` by itself.
4. Fusion: E-FIN-61…64 join a rotated motor to an unrotated mount; Fusion may un-cant the stack (CR-E1-31, `UNVERIFIED-IN-FUSION`).
5. Base Ø (≥ 28 mm), bolt pattern (16 × 19 mm), base-hole depth (≥ 4.0 mm), bell-top thread (≥ 2.5 mm for D-58) and free depth, phase-lead length (reach 0.121 m), adapter flange and post: unpublished; measured at `T-E1-MOTOR-RM`.
6. Mass at zero margin (462.0 / 462 g): the weigh-in decides; levers are aluminium prop nuts (−4 g) and Tekko32 ESCs (−21 g, +$60).

## How to verify

| Check | Command / test |
|---|---|
| CAD and graph | `python -I redesign/fusion/check.py` (propulsion 0 errors) · `python -I redesign/interfaces/merge_check.py` |
| Numbers | `python -I redesign/team/E1/propulsion.py` → `python -I redesign/subsystems/propulsion/make_propulsion.py` → `python -I redesign/proofs/build_graph.py` |
| Hardware | `T-E1-MOTOR-RM` (weigh, calipers, hole depths, R, I0) · `T-E1-STAND` (thrust, current, sag) · `T-C6-PROPNUT` |
