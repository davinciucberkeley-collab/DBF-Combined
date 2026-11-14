# Wing

Status: `MODELLED` (D1, revision D1-R2 on params A1-R5, 2026-11-10). One-piece hot-wired XPS core (S5010,
1.150 × 0.320 m) with a CF spar bonded in a bore, four PETG spar plugs, four elevon panels on upper-surface tape
hinges, packing-tape skin with a seam-free LE strip, microballoon lip beads at the block pockets, the pod
recess-step fillet and the FAA label. R2 applies the D-68 / D-69 structure fixes. CAD `fusion/wing.py`; masses and CGs from the CAD by
`team/D1/wing_data.py`; geometry self-check against the fins, pod and mechanisms parts `team/D1/wing_selfcheck.py`; claims `team/D1/wing_claims.py`.

## Purpose

Carry the air load into one spar, give the fins (blocks, anchors, half-fin roots), the pod (recess, saddle windows),
the servos (pockets) and the harness (grooves) their cut-outs in the right place, and survive a tip strike as a
cheap re-cut. No ribs, no wing joint: the core is the rib, the through-core blocks are the hard points.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Span × chord, section, t/c | 1.150 × 0.320, S5010, 9.82 % | m | `params.json#wing` | `PROPOSED` |
| Spar axis · bore · length | x 0.080, z +0.0066 · Ø 22.4 · \|y\| ≤ 0.50 | m · mm · m | `params.json#wing.spar`, C2 | `PROPOSED` |
| Foam over the bore, min (rule ≥ 2 mm) | 4.05 | mm | `CL-D1-SPAR-COVER` | `CHECKED` |
| Spar bond area (bore, both sides) | 62 153 | mm² | `CL-D1-SPAR-BOND-AREA` | `CHECKED` |
| Elevon panels \|y\| · hinge x · bevel · end gap | 0.071–0.299, 0.341–0.559 · 0.2496 · 30° · 1.0 | m · m · — · mm | `params.json#wing.elevon`, local | `PROPOSED` |
| Elevon area fraction as built (≥ 0.15) | 0.171 | — | `CL-D1-ELEVON-FRAC` | `CHECKED` |
| Bevel clearance at +25° / −25° (≥ 0.5 mm) | 1.07 / 8.93 | mm | `CL-D1-HINGE-CLEAR-DOWN/-UP` | `CHECKED` |
| Servo pocket (open below) x · \|y\| · ceiling z · bare foam | 0.1722–0.2075 · 0.2527–0.2879 · 0.0075 · 3 195 mm² (≥ 1 002) | m | `CL-D1-POCKET-BOND` | `CHECKED` (= D6 frame + 0.2 mm) |
| Foam over pocket ceiling (≥ 3 mm) · over the torque-tube groove (≥ 1 mm) | 4.2 · 1.1 | mm | `CL-D1-POCKET-ROOF`, `-TUBE-GROOVE-COVER` | `CHECKED` (groove thin) |
| Pod recess x · floor z · \|y\| · foam under | 0.0226–0.065 · 0.015 · ≤ 0.070 · 23.5 mm | m | `CL-D1-RECESS-*` (CR-D2-04) | `CHECKED` |
| Wall, aft ESC groove to slot (≥ 3 mm) · groove depth / thickness (≤ 0.5) | 3.0 · 0.10 | mm · — | `CL-D1-GROOVE-*` | `CHECKED` |
| Block-pocket corners · lip bead (3 × 3 mm, 45°, both surfaces, inboard + outboard) | R 3.15 · 3.0 | mm | `CL-D1-POCKET-CORNER-R`, `-POCKET-BEAD-LEG` (D-68) | `CHECKED` (CAD) |
| Elevon cut-out corners at the fin-root tab · tab tape folded round | R 3.0 · 24 mm strip | mm | `CL-D1-CUTOUT-CORNER-R` (D-68) | `CHECKED` (CAD) |
| LE strip 100 mm, edges x (rule ≥ 32 mm, x/c 0.10) | 45.5 upper / 46.6 lower | mm | `CL-D1-LE-SEAM-X` (CR-B2-17) | `CHECKED` (CAD) |
| Recess-step corner (floor × step) | square, no fillet (WNG-007 deleted) | — | D-103 (supersedes D-69) | `CHECKED` (CAD) |
| JR recess 18 × 10 × 5 mm · wall to servo pocket | x 0.150–0.168 · 4.2 | m · mm | `CL-D1-JR-RECESS-WALL` (CR-F2-14) | `CHECKED` |
| Mass · CG | 391.7 (allocation 405) · (0.114, 0.000, +0.005) | g · m | `CL-D1-WING-MASS`, `-CG-X` | `UNVERIFIED` (`EST`) |

## Cuts in the core (right side; left is the mirror)

| Cut | x (m) | \|y\| (m) | z / depth | For |
|---|---|---|---|---|
| Spar bore (slot from below, cap re-bonded) | 0.0688–0.0912 | 0–0.500 | Ø 22.4 mm on the axis | `WNG-002` |
| Pod recess (tape off x 0–0.095) | 0.0226–0.065 | 0–0.070 | floor z 0.015 (≤ 6.9 mm) | `E-POD-01` |
| Saddle window / tie channel | 0.0688–0.0912 | 0.029–0.053 / 0.032–0.040 | to z 0.0154 / +2 mm round the spar | `E-POD-09` |
| Brace-anchor pocket, top and bottom | 0.0688–0.0912 | 0.2335–0.2505 | to the spar | `E-FIN-57…60` |
| Through-core block pocket, corners R 3.15 | 0.0279–0.0972 | 0.3019–0.3382 | full depth | `E-FIN-49…52` |
| Lip-bead chamfers (filled, `WNG-006`) | 0.0279–0.0972 | 0.2989–0.3019, 0.3382–0.3412 | 3 × 3 mm 45°, upper and lower | `E-WNG-12…15` |
| ESC grooves, both surfaces | 0.0543 / 0.0593 / 0.0643 | 0.086–0.296 | 2.5×2.4 / 3.0×3.1 / 3.0×3.1 mm | `E-HRN-02/04` |
| Servo groove + branch, upper; lead hole | 0.1082 → 0.173; 0.173–0.177 | 0.065–0.285 → 0.283–0.287 | 4.0 × 1.6 mm; 4 mm square to the pocket | `E-HRN-02/04` |
| JR recess on the branch, upper | 0.150–0.168 | 0.280–0.290 | 5 mm deep | `E-HRN-02/04` (CR-F2-14) |
| Servo pocket, open below | 0.1722–0.2075 | 0.2527–0.2879 | ceiling z 0.0075 | `E-MEC-01/02` |
| Elevon cut-out corners at the tab (foam fill) | 0.2496–0.2526 | 0.297–0.300, 0.340–0.343 | R 3 mm, full depth | CR-C2-13 |
| Panel: torque-tube groove (open below) · horn slots | 0.2544–0.2598 · 0.2544–0.2896 | 0.1335–0.296, 0.344–0.556 · 0.284–0.286, 0.354–0.356 | to z 0.0032 · through, 2.5 mm | `E-MEC-11/12/23…28` (D6-R2) |

## Parts

| Id | Part | Qty | Mass each (g) | Status |
|---|---|---|---|---|
| `WNG-001` | Core, XPS F-250, all cuts, incl. 15 g slot fill | 1 | 201.8 `EST` | `MODELLED` |
| `WNG-002` | Spar CF 22 × 20 × 1 000 | 1 | 102.0 `EST` | `MODELLED` |
| `WNG-003` | Tape skin, LE strip, doublers, tab-edge and tip layers | 1 | 47.9 `EST` | `MODELLED` |
| `WNG-004-L/R` · `WNG-005-L/R` | PETG plugs Ø 19.8 × 36 (block) · × 20 (anchor) | 2 · 2 | 7.0 · 4.0 (C2) | `MODELLED` |
| `WNG-006-L/R` | Block-pocket lip beads, microballoon epoxy | 2 | 1.0 `EST` | `MODELLED` |
| `WNG-011-L/R` · `WNG-012-L/R` | Elevon inboard · outboard (foam + tape) | 2 · 2 | 3.7 · 3.5 `EST` | `MODELLED` |
| `WNG-020` | FAA label, right upper skin | 1 | 0.5 | `MODELLED` |

## Interfaces

| Edge | Joint | Sized by |
|---|---|---|
| `E-WNG-01` spar ↔ core | epoxy + microballoons in the bore, cap re-bonded | C2 (MS +11) |
| `E-WNG-02` skin ↔ core · `E-WNG-03` label ↔ skin | tape, 10 % overlap, 100 mm LE strip laid last · label | C2, B2 · H3 |
| `E-WNG-04…07` elevon ↔ core | upper tape hinge, ±25°; tape, horns, torque tubes, link by D6 | D6, B2 (0.257 N·m/servo) |
| `E-WNG-08…11` plugs ↔ spar | thickened epoxy inside the tube | C2 (MS +2.7) |
| `E-WNG-12/13` lip bead ↔ core · `E-WNG-14/15` lip bead ↔ block `FIN-004-R/L` | microballoon epoxy, 1 176 / 832 mm² per side | C2 (FEA re-run on the revised pocket) |
| Acknowledged (36) | `E-FIN-49…60`, `E-GER-21/22` (TPU tip corner caps over the tape, fixed core \|y\| 0.560–0.575), `E-HRN-02/04` (ESC and servo grooves, wing params `grooves.*`), `E-MEC-01/02/11/12/17/18/23…28/33/34`, `E-POD-01/09`, `E-TRN-06…09`; none pending | D5 · F2 |
| Prop keep-out (upper props) | real core and tape surface ≥ 6.6 mm outside `KO-PROP-UR/UL` (`CL-D1-PROP-SURF-GAP`); `check.py` lists the box hits as artefacts | A5, E1 |

Keep clear (no cut, no cover): cradle patch lower \|y\| 0.17–0.23 and pillar patch upper x 0.03–0.13 (D7); CG-jig
patch lower \|y\| 0.45 (H1); half-fin roots and pod footprint bare foam (D3, D2).

## Open issues

| Issue | Owner |
|---|---|
| Acknowledge `E-WNG-14/15` (lip bead on the block faces) | D3 (CR-D1-12) |
| Re-run the pocket-corner and cut-out FEA on R 3.15 + beads and R 3 + tab tape | C2 (CR-D1-14) |
| Confirm the LE-rule exemptions: pod footprint \|y\| ≤ 0.070 and tip fold \|y\| ≥ 0.551 | B2 (CR-D1-15) |
| Cradle saddles press the tape skin `WNG-003` (CR-D1-02) | D7 |
| Densities and tape areal mass are guesses until weighed | G2, H1 |

## How to verify

`python -I redesign/team/D1/wing_data.py --check` · `wing_selfcheck.py` · `python -I redesign/fusion/check.py` ·
tests `T-D1-WEIGH`, `T-D1-FIT`, `T-D1-THROW` (`team/D1/claims.json`); C2's `T-C2-WING-PROOF` and `T-C2-TAP-TEST`.
