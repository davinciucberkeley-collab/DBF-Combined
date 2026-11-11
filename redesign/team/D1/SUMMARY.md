# D1 Wing designer: summary

Revision D1-R2 on params A1-R5, updated 2026-11-10. This revision applies the D-68 / D-69 structure fixes. The
deliverables are in `subsystems/wing/`: `SPEC.md`, `BUILD.md`, `parts.csv`, `interfaces.json`, `params.json` and
`fusion/wing.py`. `team/D1/wing_data.py` generates the parts list and interfaces, `wing_selfcheck.py` checks the
geometry, and `wing_claims.py` writes `claims.json`.

## Design

| Item | Value | Unit | Status |
|---|---|---|---|
| Core, one piece XPS, S5010 section, hot-wired LE sanded | 1.150 × 0.320 | m | `MODELLED` |
| Spar CF 22 × 20, in a bore at x 0.080, z +0.0066 | 1.000 | m | `MODELLED` |
| Elevons, 4 panels, upper tape hinge at x 0.2496 | ±25 | deg | `MODELLED` |
| Elevon area fraction as built (`CL-D1-ELEVON-FRAC`) | 0.171 (≥ 0.15) | – | `CHECKED` |
| Wing mass, CAD estimate (`CL-D1-WING-MASS`) | 391.7 of 405 allocated | g | `UNVERIFIED` until `T-D1-WEIGH` |
| Wing CG x (`CL-D1-WING-CG-X`) | 0.114 | m | `MODELLED` |
| Min foam over the spar bore (`CL-D1-SPAR-COVER`) | 4.05 | mm | `CHECKED` |
| Upper-prop keep-out to the real wing surface (`CL-D1-PROP-SURF-GAP`) | ≥ 6.6 | mm | `CHECKED` (CAD) |

## This revision (action items D-68, D-69)

| Item | Done | Claim | Status |
|---|---|---|---|
| Block-pocket corners match D3's R 3 mm block | Corners are R 3.15 mm (block radius plus the 0.15 mm bond gap, same centres). The stepped CAD pocket contains the block everywhere, with 0.15 mm minimum clearance | `CL-D1-POCKET-CORNER-R` 3.15 mm | `CHECKED` (CAD) |
| Fillet beads ≥ 3 mm on both surfaces along the inboard and outboard pocket edges | New part `WNG-006-L/R`, 1.0 g per side: a 3 × 3 mm 45° chamfer on the foam lip, x 0.0279–0.0972, filled with microballoon epoxy in the block-bond pour and sanded flush. The 60 mm doubler runs over it without a break. Edges `E-WNG-12…15` | `CL-D1-POCKET-BEAD-LEG` 3.0 mm | `CHECKED` (CAD) |
| Elevon cut-out corners R ≥ 3 mm at y ±0.30 / ±0.34, tab tape carried round | Foam is left in an R 3 mm corner at each tab. Panel corners are relieved (CAD: panel ≥ 1 mm clear of the fill). A 24 mm tape strip is folded round each tab side face | `CL-D1-CUTOUT-CORNER-R` 3.0 mm | `CHECKED` (CAD) |
| Seam-free LE, 32 mm each side | One 100 mm strip is laid last, with edges at x 45.5 mm (upper) and 46.6 mm (lower). The spanwise strips end underneath it. A 72 mm strip cannot do this: the arc to x/c 0.10 is 71.6 mm | `CL-D1-LE-SEAM-X` 45.5 mm (≥ 32) | `CHECKED` (CAD) |
| F2's 18 × 10 × 5 mm JR recess | Cut at x 0.150–0.168, \|y\| 0.280–0.290, 5 mm deep, on the servo branch on both sides. 4.2 mm of foam is left to the servo pocket | `CL-D1-JR-RECESS-WALL` 4.2 mm | `CHECKED` |
| D6-R2 groove and patch sizes | Tube groove at \|y\| 0.1335–0.296 (inboard) and 0.344–0.556 (outboard), 1 mm past D6's built tubes. The panels have no groove elsewhere. Tape is cut back 14 mm (flange) and 12 mm (backplate) | `wing_selfcheck` step 7 | `CHECKED` |
| 5 mm recess-step fillet, laid before the pod | New part `WNG-007`, 1.1 g: legs 5 × 5 mm, 45° face, \|y\| ≤ 0.070, cured and sanded before the pod goes in. Edges `E-WNG-16/17` | `CL-D1-RECESS-FILLET` 5.0 mm | `CHECKED` (CAD) |

Mass: +4.4 g (beads 2.0, fillet 1.1, tab tape 0.9, LE overlap 0.6, less the foam taken out). The margin is 13.3 g
inside the 405 g allocation, so no change request is needed for mass.

## Checks (2026-11-10)

| Check | Result for the wing |
|---|---|
| `wing_data.py --check` | up to date: 36 acknowledged, 0 pending |
| `wing_selfcheck.py` | PASS, including the new steps 4–8 (bead cover, panel-to-fill clearance, pocket against block, LE edges, fillet, JR wall, tube groove span) |
| `fusion/check.py` | wing `ok`, **0 errors**. 3 one-sided WARNs on the new edges `E-WNG-14/15` (D3) and `E-WNG-17` (D2) until those owners acknowledge them |
| `merge_check.py` | PASS (0 errors). The same 3 one-sided WARNs are the only wing warnings |

## Open

| Issue | Owner |
|---|---|
| Acknowledge `E-WNG-14/15` (CR-D1-12) | D3 |
| Bevel the pod floor's aft lower edge 5 × 5 mm onto the fillet and acknowledge `E-WNG-17` (CR-D1-13) | D2 |
| Re-run the FEA on R 3.15 mm with beads and R 3 mm with tab tape (CR-D1-14) | C2 |
| LE-rule exemptions at the pod footprint and the tip fold (CR-D1-15) | B2 |
| Saddle and pillar contacts on the tape skin `WNG-003` (CR-D1-02) | D7 |
| Weigh the core, tape, bead mix and finished wing (`T-D1-WEIGH`) | G4 / D1 |
