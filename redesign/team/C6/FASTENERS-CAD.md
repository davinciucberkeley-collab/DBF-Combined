# Fasteners as CAD parts: changelog (C6 + A5, R5c, 2026-11-11)

Every screw, nut, washer, spacer and heat-set insert in a joint stack is now a modelled part with its own id,
material, catalogue mass, CAD bodies at the joint, and edges to the parts it seats in. Until R5b the hardware mass
sat inside the parent parts ("mass inside FIN-003") and had no geometry.

Re-run after any subsystem generator (the generators also call it at the end now):
`python -I redesign/team/C6/fastener_parts.py` (`--check` exits 1 if a file is stale).

## FIX 1: servo cover screws on `E-MEC-03/04`

The servo sits in the frame's ear slots and the screwed cover holds it there, so `E-MEC-03/04` now carry a joint
stack: the cover's **2 × M2 × 6 self-tapping pan head, A2**, into 1.6 mm pilots 6 mm deep in the frame's
4 × 5 × 6 mm end-wall bosses, 5.2 mm engaged (min 4.0), snug, Phillips #1, from below (−z) with the wing on its
back; install order 6, removal 1. These are the same two screws as `E-MEC-35/36` (part `MEC-011-<L/R>`), not more
hardware.

- **Why M2 and not an M3 insert.** An M3 × 5.7 insert needs a 7.2 mm boss and a 6.2 mm bore, and the bosses are
  4 × 5 mm. The frame and the wing pocket would have to grow to take one. The load is small (cover holds a 15.8 g
  servo: 2.0 N at a 12.75 g crash, against 245 N thread shear per screw in PETG), and covers come off rarely. M2
  stays within the D-58 b deviation (M2 only as mechanism hardware).
- **Where it is recorded.** `make_mechanisms.py` writes the stack. `make_stacks.py` / `joint_stacks.json` take
  03/04 off the withdrawn list. `JOINTS.md` is updated. Part `MEC-011` (qty 2, 0.4 g, $0.30 a pair) is added. The
  I1 `H02` text now names M2 × 6 self-tapping for the covers (price unchanged at $3, so BOM totals and order wave
  are unchanged).
- **Scan of every `subsystems/*/interfaces.json`.** No other edge whose connection type implies screws, bolts or
  nuts lacks a joint stack. The other keyword hits are gel pads ("no screws"), thermal contacts beside screw holes,
  snap fingers, 2-56 clevises (hinged) and the cover tape edge.

## What was added

| Part (nodes) | Owner | Set per node | Mass g / node | Joint stack | Seated on | Mass moved from |
|---|---|---|---|---|---|---|
| `PRP-005-<st>` (4) | propulsion | 4 × M3x8 SHCS A2 | 3.2 | `E-FIN-61…64` | `FIN-003`, `PRP-001` | `PRP-001` −3.2 |
| `PRP-006-<st>` (4) | propulsion | 4 × M3x4 SHCS (supplied) | 1.2 | `E-PRP-01…04` | `PRP-004`, `PRP-001` | `PRP-004` −1.2 |
| `PRP-007-<st>` (4) | propulsion | M6 nut ISO 4032 (LH on UR/LL) | 1.9 | `E-PRP-05…08` | `PRP-004` | `PRP-004` −1.9 |
| `PRP-008-<st>` (4) | propulsion | M6 washer 6 × 12 × 1 | 0.6 | `E-PRP-05…08` | `PRP-003`, `PRP-004` | `PRP-004` −0.6 |
| `FIN-101-<st>` (4) | fins | M3x16 SHCS A2 pinch bolt | 1.1 | `E-FIN-05…08` | `FIN-003` | `FIN-003` −1.0 |
| `FIN-102-<st>` (4) | fins | M3 nyloc ISO 10511 | 0.36 | `E-FIN-05…08` | `FIN-101`, `FIN-003` | `FIN-003` −0.25 |
| `FIN-103-<st>` (4) | fins | 2 × M3 washer ISO 7089 | 0.24 | `E-FIN-05…08` | `FIN-003` | `FIN-003` −0.15 |
| `PWR-101` (1) | power | 4 × M3x18 PA66 pan head | 0.64 | `E-PWR-03` | `PWR-006`, `PWR-107` | `PWR-006` −0.64 |
| `PWR-102` (1) | power | 4 × nylon spacer 10 mm | 0.92 | `E-PWR-03` | `PWR-006`, `POD-002` | `PWR-006` −0.92 |
| `PWR-103` (1) | power | 4 × nylon washer 0.5 mm | 0.08 | `E-PWR-03` | `PWR-006` | `PWR-006` −0.08 |
| `PWR-107` (1) | power | 4 × M3 × 5.7 brass heat-set insert | 1.6 | `E-PWR-03` | `POD-002` | new mass |
| `POD-011` (1) | pod | M3x16 PA66 cheese head | 0.14 | `E-POD-06` | `POD-007`, `POD-005` | new mass |
| `POD-012` (1) | pod | M3 PA66 hex nut | 0.05 | `E-POD-06` | `POD-011`, `POD-007` | new mass |
| `MEC-011-<L/R>` (2) | mechanisms | 2 × M2 × 6 self-tapping pan head | 0.4 | `E-MEC-35/36`, `03/04` | `MEC-007`, `MEC-008` | `MEC-007` −0.2 |
| `MEC-012-<L/R>` (2) | mechanisms | M2 × 4 arm screw (supplied) | 0.17 | `E-MEC-05/06` | `MEC-002`, `MEC-001` | new mass |
| `TRN-102-<C/L/R>` (3) | transport (ground) | 2 × (M3x16 + nyloc + fender washer) | 4.6 | `E-TRN-13…15` | `TRN-007`, `TRN-001` | flight: false |

That is **41 nodes in 16 part numbers and 68 seat edges** (`E-<owner>-101…`, via the new `CT-HW-SEATED`, method
`clamped`, `"hardware": true`, `"hardware_of"` = parent edge). The joint stack stays on the parent edge.
`merge_check.py` requires a joint stack on every `fastened` edge, so reusing the joint's own connection type
would have meant copying C6's stack onto 68 edges. Each node is one joint-stack instance, because the A4 id rule
(`<PREFIX>-NNN-<suffix>`) cannot number four screws at one station, so the parts.csv qty equals the node count.
Spares stay on the I1 lines.

**By subsystem (nodes):** propulsion 16, fins 12, power 4, mechanisms 4, pod 2, transport 3 (ground).

**By item (flight; ground in brackets):**

| Item | Count |
|---|---|
| Screws | 47 (+6): M3x8 16, M3x4 16, M3x16 4 (+6), PA66 M3x18 4, PA66 M3x16 1, M2 × 6 4, M2 × 4 2 |
| Nuts | 9 (+6): nyloc 4 (+6), PA66 1, M6 4 |
| Washers | 16 (+6) |
| Spacers | 4 |
| Inserts | 4 |

## CAD

- **Helpers** in `fusion/k09kit.py`: `hw_screw` (socket / pan / cheese head with a round recess, plain shank),
  `hw_nut` (hex, ISO 4032 or nyloc height), `hw_washer` (also spacers), `hw_insert`, `hw_part` (builds only when
  the node is declared, so the designers' generators run unchanged) and `hw_join` (rigid registration of the
  hardware edge).
- **Placement.** Each owner module places the bodies at the joint it already knows:
  - motor screws on the canted plate's back face, along the canted shaft axis (component placed like the motor);
  - pinch bolt along x through both ears, built at UR and quad-mirrored;
  - the power stack at D2's four bosses;
  - mast screw across the socket boss from the +y counterbore;
  - cover screws from below into the end-wall bosses, and the arm screw into the spline;
  - handle bolts through the box walls.
- **Other changes.** The prop nut and washer moved out of the `PRP-004` body into `PRP-007/008`. They are added to
  the prop keep-out exemption with the adapter screws. Blender gets a brass look for the inserts.
- **Render:** [`showcase/renders/detail-fasteners.png`](../../showcase/renders/detail-fasteners.png) (figure
  `detail-fasteners` in `blender/specs/showcase.json`).

## Mass roll-up (A3, `mass_rollup.py`)

| | Before | After | Δ |
|---|---|---|---|
| Basic | 2 345.5 g | 2 349.2 g | **+3.7 g** |
| Predicted (with growth) | 2 461.8 g | 2 465.9 g | +4.1 g |
| CG x | 0.0486 m | 0.0487 m | +0.1 mm |

The +3.7 g is new mass, not double counting:

- fins +1.2 g: catalogue masses 1.70 g against D3's booked 1.40 g per mount;
- power +1.6 g: the inserts were not booked anywhere;
- mechanisms +0.7 g: M2 × 6 at 0.2 g against 0.1 g booked, plus the arm screws;
- pod +0.2 g.

Propulsion is unchanged (E1's own screw, nut and washer masses).

**Consequence.** Fins now read 437.1 g against the 437 g allocation (0 g reserve, see JOINTS open issue 4). The
`merge_check` / `check.py` mass WARN moves from propulsion to fins, and `CL-A3-ALLOC-WORST` now fails by 0.1 g. A1
decides: release 0.2 g to fins, or D3 trims.

## Checks

The following pass:

- `fusion/check.py`: PASS, 0 errors.
- `merge_check.py`: PASS, 0 errors.
- `blender selftest.py` (examples): all ok.
- `selftest.py --root redesign/subsystems`: all 41 hardware parts ok. Its 52 FAILs are wing and transport lofts
  that already failed before this change.

All masses are `UNVERIFIED` until weighed. Insert mass 0.40 g is an estimate.
