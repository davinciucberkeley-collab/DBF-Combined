# T-020 linkage-poses mesh sweep (R-PHY-05: collision during motion, swept against CAD meshes)

Date 2026-11-19. Git base 73d95966 plus the uncommitted working tree (nothing committed). `docs/*.md` not edited; proposed record text is in section 7.
Category: **interference during motion (mesh, Blender BVH)**; the analytic comparison is interference (separating-axis, AR-003); the step justification is a hand calculation from stored AR-003 data.

## 1. Acceptance test (from the brief, restated before coding)
A mode that places arm MEC-002, keeper MEC-008 and rod MEC-003 at their kinematic pose together with the elevon group for a list of elevon angles over the full range, and runs the mesh interference check with all parts in; default behaviour unchanged; expected design contacts (keeper bridge / rod, arm / rod at the Z-bend, clevis pin in horn hole) handled as declared joints the way the static gate does, with no blanket exemption; per angle report pairs over 0.05 mm and the minimum clearance of rod / arm / keeper / clevis to their neighbours, compared with the AR-003 analytic minimums; one run over the chosen angles; step justified from the AR-003 minimum clearances; AR-007 ten-field block proposed.
Pass criterion set before the run: 0 part pairs deeper than 0.05 mm at any angle (project gate), 0 open wire ends, 0 wire folds.

## 2. What was built (all additive; the default path of `collide_a.py` is untouched)
- `redesign/qp/A/cad/collide_a.py`: new flags `--linkage-poses`, `--angles`, `--zj mid,lo,hi`, `--pin-with rod|horn`, `--tag`; function `linkage_mode` runs only with `--linkage-poses`. Own output names: `out/_job_<tag>.json`, `out/blender_<tag>.log`, `out/report_<tag>.json`, `out/REPORT_<tag>.md`; `report.json`, `REPORT.md`, `_job.json`, `blender.log` are not written in this mode.
- `redesign/qp/A/cad/linkage_poses_a.py` (host): poses from `mechanism/linkage_core.py` (the T-018 solution, same geometry as the analytic sweep). Elevon group (MEC-004, WNG-006, WNG-007, WNG-010): rotation by delta about the hinge (`collide.rot_about` on the joint axis and origin). Arm group (MEC-002, MEC-008, HWC-002 arm screw, which is clamped to the servo output): rotation by theta about the vertical spline axis. Rod MEC-003 and clevis pin MEC-005: one rigid frame (u, e2, e3), u = unit vector Z-bend joint to horn hole, e2 = y made orthogonal to u, e3 = u x e2, translated so the neutral Z-bend joint lands on `arm_pt(theta)` (the frame the analytic sweep uses). Nothing is held out: the damper stator WNG-009 stays fixed and the rotor turns about the hinge line it is coaxial with.
  Self-check built in (the run aborts above 1e-9 m): the rigid motions reproduce the kinematic points. Result: horn hole 3.0e-17 m, rod clevis end 2.8e-17 m, rod joint 0, arm tip 3.9e-17 m.
- `redesign/qp/A/cad/a_linkage_blender.py` (Blender): `collide_blender.py` unmodified through `a_collide_blender.py` (inside-out fix; 118 bodies reversed in this run), one session for the static pose plus every linkage pose. Per pose: every moved body against every fixed body (cuts honoured), moved bodies of different groups (elevon / arm / rod) against each other, then the clearance of the linkage parts to every neighbour within 3 mm.
- `redesign/qp/A/mechanism/linkage_poses_report.py`: tables from the report JSON and the AR-003 CSVs (`cad/out/linkage_poses_tables_linkage_poses.md`, copied in section 6).
- Declared joints are handled as the static gate handles them. Seats stay cut-outs on the host (`ctx.seat`: arm screw in the servo output thread, pin in the cheek holes), real holes stay holes in the meshes (arm hole 1.3 mm, horn hole 1.1 mm), contacts keep the 0.05 mm tolerance. `linkage_poses_a.DECLARED` only LABELS hits in `REPORT_linkage_poses.md`; every hit still counts. No exemption list was added.
- Design decision made while building: the clevis pin MEC-005 rides with the rod (default), not the horn. The CAD seats the pin in the cheek holes with zero clearance (CUT_TOL 0.02 mm), so with the pin on the horn the 0.88 deg out-of-line angle (K5) puts the pin 0.026 mm outside the cheek cut and the binary cut test reports the cheek solid as hit: 0.258 mm at +-21 deg (reproduced with `--pin-with horn`, section 5). A real clevis pin sits in the cheeks and the horn hole (1.1 mm on 1.0 mm) takes the angle, which is what K5 assumes. Logged in `redesign/params/CHANGE-LOG.md` (T-020 entry).

## 3. Commands, exit codes, wall times
| Command (cwd `redesign/qp/A/cad`) | rc | wall |
|---|---|---|
| `python -I collide_a.py --linkage-poses --zj mid,lo,hi --tag linkage_poses` (final run: 17 angles x 3 states + static = 52 poses) | 1 (FAIL, 34 pair hits at zj=lo) | 497 s (script 490 s: model build 100 s, static pose 47 s, poses 3 to 14 s each) |
| `python -I collide_a.py --linkage-poses --angles -21,0,21 --zj mid --pin-with horn --tag linkage_poses_pinhorn` (sensitivity) | 1 (FAIL, 4) | 183 s |
| `python -I collide_a.py --job-only` (default path check) | 0 | 9 s; `comps`, `wires` and the three poses identical in content to what the unmodified code builds (the committed `out/_job.json` is a static-only job; it was restored with `git checkout`) |
| debug runs (angles 0,21 with the pin on the horn; first full run before body-level clearances) | 0 / 1 | 175 s / 546 s; superseded, outputs overwritten or deleted |
| `python -I redesign/qp/A/mechanism/linkage_poses_report.py linkage_poses` | 0 | 2 s |
Blender 4.5.14 LTS (`C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe`), Python 3.14.2. Stdout: `redesign/qp/A/cad/out/linkage_poses_stdout.txt`; Blender log `blender_linkage_poses.log`.

## 4. Result
115 parts, 486 bodies, 44 wire strands. Angles delta = -21, -20, -18, -15, -12, -9, -6, -3, 0, +3, +6, +9, +12, +15, +18, +20, +21 deg (both elevons at the same angle: the two sides are mirror images far apart, so this covers each side at each angle); joint states zj = mid (rod axis at ROD_Z, the CAD pose), lo (rod resting on the arm, ROD_Z - 0.15 mm), hi (rod on the keeper bridge, ROD_Z + 0.15 mm), as AR-001 / AR-003.
- Static pose in the same run: 10 hits, deepest 0.034 mm (HWC-001 / HWC-003), 0 over 0.05 mm: equals the stored static gate.
- **zj = mid (the CAD pose): 0 part pairs over 0.05 mm at all 17 angles; no hit at all down to 0.01 mm.**
- **zj = hi: 0 pairs over 0.05 mm at all 17 angles;** only leg-in-arm-hole hits of 0.012 to 0.014 mm at -21, -20 and +21 deg.
- **zj = lo: FAIL at every angle.** Pair MEC-003 / MEC-001 (rod Z-bend leg end into the servo case top), R and L: 0.051 mm (-12 deg) to 0.056 mm (+-21 deg), nearly constant in angle (the angle dependence is the 0.005 mm leg tilt). Cause: the leg bottom is drawn 0.1 mm above the arm underside (`ARM_Z0 + 0.0001`, electrical.py rod Z-bend leg) and the lo state lowers the rod 0.15 mm, so the end is 0.05 mm below the case top. The AR-003 analytic sweep did not see it (its leg base is fixed at ARM_Z0 + 0.1 mm in every state). The failure is 0.001 to 0.006 mm over the 0.05 mm tolerance and does not depend on elevon angle: a joint-state geometry finding. Also at lo: leg in the arm hole up to 0.024 mm (-21 deg), below tolerance.
- Wire ends not on a termination 0, wire folds 0.
- Overall gate: **FAIL** (34 hits = 17 angles x 2 sides at zj = lo). zj = mid and hi pass.
- Resolution (ladder, logged in CHANGE-LOG, NOT applied: it edits CAD and AR-003 inputs): rung 1 drop the leg: no (it is the joint). Rung 2 modify geometry: leg bottom at `ARM_Z0 + 0.25 mm` leaves 0.10 mm over the case at lo and 0.25 mm at mid; needs the electrical.py edit, the analytic leg base in `elevon_sweep_collision.py` and a rerun of this gate and the static gate. Rung 4 alternative: state that the lowest reachable joint height is the leg-on-case stop (0.25 mm of vertical freedom instead of 0.30 mm; the K7 free play only gets smaller), keep the CAD, and redefine lo as ROD_Z - 0.10 mm. Rungs 3 and 5 are not needed. The choice is the mechanism owner's.

### Declared contacts as the mesh sees them (not exempted)
- Arm / rod at the Z-bend (leg in the 1.3 mm hole): clearance 0.028 mm at neutral (mid; the 12-gon hole flats at 0.628 mm against the 0.6 mm leg), falling to 0.000 at |delta| >= 20 deg at mid (leg tilt 0.8 deg across the 2 mm arm), to penetrations of 0.014 mm (hi) and 0.024 mm (lo) at -21 deg. All below 0.05 mm. Part of this is facet error: the real round 1.3 mm hole has 0.05 mm radial clearance (0.022 mm more than the flats), so the real margin is larger than shown; K5 (0.8 deg against a 2.86 deg allowance) is the physical statement.
- Keeper bridge / rod: 0.150 mm at mid (analytic 0.147), 0.294 mm at lo (0.292), contact 0.000 at hi (analytic -0.003 mm: its circumscribed polygon over-penetrates; the mesh cylinder is inscribed).
- Rod resting on the arm at lo: pushrod / arm 0.000 (touching), analytic -0.028 mm (same cause).
- Clevis pin in the horn hole: 0.031 mm at neutral, 0.019 to 0.020 mm at +-21 deg (0.88 deg out of line over the 2 mm blade). Not in AR-003.
- Arm on the servo case, arm screw in the servo thread, keeper on the arm: 0.000 contact by design, constant.
- Comparison with the AR-003 analytic minimums (like for like, body level, tables in section 6): clevis cheek / horn blade 0.075 mm mesh against 0.066 and 0.077 analytic (both at +21 deg); arm / rod 0.122 mm against 0.113 (mid); rod leg / servo case 0.092 against 0.100 (mid); keeper bridge / rod 0.150 against 0.147; keeper spacer / rod 0.701 against 0.698; clevis sleeve / horn 1.286 against 1.287; rod / servo case 1.894 against 1.891. Largest difference over all angles for those pairs 0.016 mm. The analytic hulls are conservative (circumscribed polygons, solid hulls), which explains the larger differences listed as "analytic hull bound". The only disagreement beyond that is zj = lo rod leg / servo case (analytic 0.100, mesh -0.056), the finding above.

## 5. Sensitivity run: pin kept on the horn
`--pin-with horn`, mid, -21 / 0 / +21: static 0, 0 deg 0, **+-21 deg MEC-003 / MEC-005 0.258 mm on both sides** (cheek holes cut to the pin at its rod frame, the pin axis 0.88 deg off them). This is an artifact of a zero-clearance cut model, not an interference of the hardware; it is why the default puts the pin on the rod. Files `report_linkage_poses_pinhorn.json`, `REPORT_linkage_poses_pinhorn.md`.

## 5a. Why 3 deg (step justification from AR-003)
AR-003 smallest positive clearance 0.066 mm (clevis cheek / horn blade, +21 deg), keeper bridge / rod 0.147 mm, design contacts arm / rod -0.028 mm (lo) and keeper bridge / rod -0.003 mm (hi). From the stored 0.5 deg analytic sweep (`mechanism/out/linkage_sweep_collision*.csv`, side R, three states; computed by `linkage_poses_a.step_justification`, `cad/out/linkage_poses_step_justification.json`): every pair under 0.2 mm has a maximum slope of 0.0035 mm/deg, so a pose up to 1.5 deg from a sample (half of the 3 deg step) can be at most 0.0053 mm lower than the nearest sample; the largest slope of any pair under 3 mm (keeper spacer / rod, 0.037 mm/deg) has 0.70 mm of clearance, so at most 0.056 mm of 0.70 mm. The actual loss between chosen angles (minimum over the 0.5 deg grid minus the smaller of the two chosen-angle values) is at most 0.0003 mm: the minima sit at the stop (+-21 deg), at +-20 deg, or are flat. The endpoints +-20 (commanded, BUILD D5b) and +-21 (stop) are in the list. Mesh data agree: the largest change of any listed pair between adjacent chosen angles is 0.014 mm (leg in hole) per 3 deg, against the 0.05 mm tolerance. Rows with the smallest AR-003 separations:

| State | Analytic pair | min sep mm | at delta | max slope mm/deg | worst case 1.5 deg from a sample mm | loss between samples mm |
|---|---|---|---|---|---|---|
| lo | arm / rod | -0.028 | -21 | 0.0034 | 0.0052 | 0.0000 |
| hi | keeper bridge / rod | -0.003 | -7 | 0.0000 | 0.0000 | 0.0000 |
| mid | arm / servo case | 0.000 | -21 | 0.0000 | 0.0000 | 0.0000 |
| lo | arm / servo case | 0.000 | -21 | 0.0000 | 0.0000 | 0.0000 |
| hi | arm / servo case | 0.000 | -21 | 0.0000 | 0.0000 | 0.0000 |
| hi | clevis cheek -1 / horn blade | 0.066 | +21 | 0.0032 | 0.0047 | 0.0000 |
| mid | clevis cheek -1 / horn blade | 0.066 | +21 | 0.0031 | 0.0047 | 0.0000 |
| lo | clevis cheek -1 / horn blade | 0.066 | +21 | 0.0031 | 0.0047 | 0.0000 |
| hi | clevis cheek +1 / horn blade | 0.077 | +21 | 0.0022 | 0.0033 | 0.0000 |
| mid | clevis cheek +1 / horn blade | 0.077 | +21 | 0.0022 | 0.0033 | 0.0000 |
| lo | clevis cheek +1 / horn blade | 0.077 | +21 | 0.0022 | 0.0033 | 0.0000 |
| mid | rod Z-bend pin / servo case | 0.100 | -21 | 0.0000 | 0.0000 | 0.0000 |
| lo | rod Z-bend pin / servo case | 0.100 | -21 | 0.0000 | 0.0000 | 0.0000 |
| hi | rod Z-bend pin / servo case | 0.100 | -21 | 0.0000 | 0.0000 | 0.0000 |

## 6. Tables (generated by `linkage_poses_report.py`; negative = penetration depth from the hit list; a penetration under 0.01 mm reads as 0.000, the report threshold)
Clearance method: minimum over sample points of the linkage-part mesh (vertices plus 15 points per triangle) of the distance to the neighbour's BVH, refined by alternating nearest-point projection; an upper bound of the true mesh distance (within about 0.01 mm). Pairs with the foam core WNG-001 and the elevon WNG-006 are not listed: their pockets and slots are cutters, not faces, so an unsigned surface distance is not a clearance (the penetration test honours the cuts and found no hit against them).

### Pairs over 0.05 mm per angle (mesh, all parts in)

| delta deg | zj=mid | zj=lo | zj=hi |
|---|---|---|---|
| -21 | 0 (deepest 0.000) | 2 (deepest 0.056) | 0 (deepest 0.014) |
| -20 | 0 (deepest 0.000) | 2 (deepest 0.055) | 0 (deepest 0.012) |
| -18 | 0 (deepest 0.000) | 2 (deepest 0.054) | 0 (deepest 0.000) |
| -15 | 0 (deepest 0.000) | 2 (deepest 0.052) | 0 (deepest 0.000) |
| -12 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| -9 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| -6 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| -3 | 0 (deepest 0.000) | 2 (deepest 0.052) | 0 (deepest 0.000) |
| +0 | 0 (deepest 0.000) | 2 (deepest 0.052) | 0 (deepest 0.000) |
| +3 | 0 (deepest 0.000) | 2 (deepest 0.052) | 0 (deepest 0.000) |
| +6 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| +9 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| +12 | 0 (deepest 0.000) | 2 (deepest 0.051) | 0 (deepest 0.000) |
| +15 | 0 (deepest 0.000) | 2 (deepest 0.052) | 0 (deepest 0.000) |
| +18 | 0 (deepest 0.000) | 2 (deepest 0.054) | 0 (deepest 0.000) |
| +20 | 0 (deepest 0.000) | 2 (deepest 0.055) | 0 (deepest 0.000) |
| +21 | 0 (deepest 0.000) | 2 (deepest 0.056) | 0 (deepest 0.014) |

### Minimum mesh clearance per part pair, zj=mid (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-003 | 0.000 | -21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-004 / MEC-005 | 0.020 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-001 / MEC-003 | 0.092 | -21 | no | - |
| MEC-003 / MEC-008 | 0.150 | -18 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=mid, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.100 | -21 | 0.092 | -21 | 0.008 |  |
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | 0.113 | -21 | 0.122 | +21 | 0.016 |  |
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | 0.147 | -12 | 0.150 | -18 | 0.003 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.698 | -21 | 0.701 | -21 | 0.003 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.750 | -21 | 0.742 | -21 | 0.008 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.287 | +21 | 1.286 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.399 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.891 | -21 | 1.894 | -21 | 0.003 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.952 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Minimum mesh clearance per part pair, zj=lo (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| MEC-001 / MEC-003 | -0.056 | -21 | no | - |
| MEC-002 / MEC-003 | -0.024 | -21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-004 / MEC-005 | 0.020 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-003 / MEC-008 | 0.294 | +0 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=lo, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | -0.028 | -21 | 0.000 | -20 | 0.031 | analytic hull bound |
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.100 | -21 | 0.000 | -21 | 0.100 |  |
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | 0.292 | +0 | 0.294 | +0 | 0.004 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.698 | -21 | 0.701 | -21 | 0.003 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.900 | -21 | 0.894 | -21 | 0.006 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.287 | +21 | 1.287 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.400 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.804 | -21 | 1.807 | -21 | 0.006 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.951 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Minimum mesh clearance per part pair, zj=hi (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| MEC-002 / MEC-003 | -0.014 | -21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-003 / MEC-008 | 0.000 | -15 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-004 / MEC-005 | 0.019 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-001 / MEC-003 | 0.240 | -21 | no | - |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=hi, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | -0.003 | -6 | 0.000 | -15 | 0.003 |  |
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.100 | -21 | 0.240 | -21 | 0.148 | analytic hull bound |
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | 0.255 | -21 | 0.259 | -21 | 0.009 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.600 | -21 | 0.590 | -21 | 0.010 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.699 | -21 | 0.702 | -21 | 0.003 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.286 | +21 | 1.286 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.397 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.978 | -21 | 1.981 | -21 | 0.003 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.952 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Per-angle clearance, zj=mid (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | 0.000 | 0.150 | 0.075 | 0.020 | 0.092 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | 0.000 | 0.150 | 0.077 | 0.021 | 0.093 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | 0.002 | 0.150 | 0.082 | 0.023 | 0.094 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.009 | 0.150 | 0.087 | 0.024 | 0.096 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.016 | 0.150 | 0.092 | 0.028 | 0.097 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.024 | 0.150 | 0.095 | 0.032 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.029 | 0.150 | 0.098 | 0.033 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.028 | 0.150 | 0.100 | 0.032 | 0.100 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.028 | 0.150 | 0.100 | 0.031 | 0.100 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.028 | 0.150 | 0.100 | 0.032 | 0.100 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.029 | 0.150 | 0.098 | 0.033 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.023 | 0.150 | 0.095 | 0.033 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.016 | 0.150 | 0.092 | 0.028 | 0.097 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.009 | 0.150 | 0.087 | 0.023 | 0.096 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | 0.003 | 0.150 | 0.082 | 0.021 | 0.094 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | 0.000 | 0.150 | 0.077 | 0.021 | 0.093 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | 0.000 | 0.150 | 0.075 | 0.020 | 0.092 | 0.000 | 0.000 | 0.062 | 0.000 |

### Per-angle clearance, zj=lo (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | -0.024 | 0.300 | 0.075 | 0.020 | -0.056 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | -0.016 | 0.300 | 0.077 | 0.021 | -0.055 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | -0.012 | 0.300 | 0.082 | 0.022 | -0.054 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.000 | 0.300 | 0.087 | 0.024 | -0.052 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.001 | 0.300 | 0.092 | 0.028 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.001 | 0.299 | 0.095 | 0.033 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.003 | 0.296 | 0.098 | 0.033 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.005 | 0.296 | 0.100 | 0.032 | -0.052 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.002 | 0.294 | 0.100 | 0.031 | -0.052 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.005 | 0.295 | 0.100 | 0.032 | -0.052 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.002 | 0.296 | 0.098 | 0.033 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.001 | 0.299 | 0.095 | 0.032 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.000 | 0.300 | 0.092 | 0.028 | -0.051 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.000 | 0.300 | 0.087 | 0.023 | -0.052 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | -0.012 | 0.300 | 0.082 | 0.021 | -0.054 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | -0.018 | 0.300 | 0.077 | 0.021 | -0.055 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | -0.019 | 0.300 | 0.075 | 0.020 | -0.056 | 0.000 | 0.000 | 0.062 | 0.000 |

### Per-angle clearance, zj=hi (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | -0.014 | 0.000 | 0.075 | 0.021 | 0.240 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | -0.012 | 0.000 | 0.077 | 0.022 | 0.241 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | 0.000 | 0.000 | 0.082 | 0.023 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.000 | 0.000 | 0.087 | 0.024 | 0.244 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.007 | 0.000 | 0.092 | 0.027 | 0.245 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.015 | 0.000 | 0.095 | 0.032 | 0.246 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.019 | 0.000 | 0.098 | 0.034 | 0.247 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.019 | 0.000 | 0.100 | 0.032 | 0.248 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.019 | 0.000 | 0.100 | 0.031 | 0.248 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.019 | 0.000 | 0.100 | 0.032 | 0.248 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.020 | 0.000 | 0.098 | 0.033 | 0.247 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.014 | 0.000 | 0.095 | 0.033 | 0.246 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.007 | 0.000 | 0.092 | 0.029 | 0.245 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.000 | 0.000 | 0.087 | 0.023 | 0.244 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | 0.000 | 0.000 | 0.082 | 0.021 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | 0.000 | 0.000 | 0.077 | 0.020 | 0.241 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | -0.014 | 0.000 | 0.075 | 0.019 | 0.240 | 0.000 | 0.000 | 0.062 | 0.000 |


## 7. Proposed record text (for the T-020 / records owner to paste; not applied)
**AR-003 addendum (replaces the open action "a mesh sweep with the linkage parts needs a linkage-poses mode (not built)")**: "Mesh sweep with the linkage parts built 2026-11-19: `python -I redesign/qp/A/cad/collide_a.py --linkage-poses --zj mid,lo,hi` (Blender 4.5.14 BVH, 0.05 mm). zj = mid and hi: 0 pairs over 0.05 mm at 17 angles (-21..+21 every 3 deg plus +-20); zj = lo FAILS: rod Z-bend leg end 0.051-0.056 mm into the servo case (leg bottom 0.1 mm above the arm underside, lo lowers the rod 0.15 mm), not seen by the analytic sweep. Mesh and analytic clearances agree to 0.016 mm. Evidence `redesign/qp/A/mechanism/out/T020_linkage_sweep.md`."

**AR-007 ten-field block, linkage-poses mesh sweep (T-020):**
- Category: interference during motion (mesh, Blender BVH), all moving linkage parts in.
- Solver / tool + version: `redesign/qp/A/cad/collide_a.py --linkage-poses` -> `linkage_poses_a.py`, `a_linkage_blender.py` (collide_blender.py through a_collide_blender.py); Blender 4.5.14 LTS; Python 3.14.2.
- Model version (git commit): git `73d95966` plus the uncommitted working tree of 2026-11-19 (D-212 rev 3 CAD).
- Inputs: CAD meshes of 115 parts / 486 bodies / 44 wire strands; kinematic poses from `mechanism/linkage_core.py` (T-018, AR-001); joint states mid / lo / hi (ROD_Z, -0.15 mm, +0.15 mm).
- Assumptions: rod rigid, straight between the joint centres, leg and clevis frame (u, e2, e3) as in the analytic sweep; clevis pin rides with the rod, the horn hole takes the out-of-line angle; arm screw turns with the arm; both elevons at the same angle (mirror sides); no joint free play, no deflection under load; damper stator fixed on the hinge line; servo lead wire and boot fixed; the arm hole is a 12-gon, so hole clearances are about 0.022 mm conservative.
- Boundary conditions / loads: kinematic only, no loads; 17 elevon angles from -21 to +21 deg (every 3 deg plus +-20), three Z-bend states.
- Numerical settings: penetration tolerance 0.05 mm, report threshold 0.01 mm, 15 samples per triangle, edges refined to 4 mm; clearance cap 3 mm; moved x fixed and moved x moved across groups.
- Outputs (file paths): `redesign/qp/A/cad/out/report_linkage_poses.json`, `REPORT_linkage_poses.md`, `linkage_poses_stdout.txt`, `blender_linkage_poses.log`, `linkage_poses_tables_linkage_poses.md`, `linkage_poses_step_justification.json`; sensitivity `report_linkage_poses_pinhorn.json`.
- Acceptance criteria (set before the run): 0 part pairs deeper than 0.05 mm at any angle, 0 open wire ends, 0 wire folds.
- Result: FAIL at zj = lo only: 34 hits (17 angles x 2 sides), rod leg end into the servo case 0.051-0.056 mm; zj = mid and hi PASS (0 over 0.05 mm, deepest 0.014 mm); wire ends 0, folds 0; mesh vs analytic clearance within 0.016 mm for like-for-like pairs; wall 497 s.
- Limits / validity: kinematic poses of a rigid rod; the 3 deg step is justified from the AR-003 slopes, not sampled finer on the mesh; dimensions marked EST in the CAD (arm thickness, clevis cheeks, servo boss height "-") stand; foam core, elevon slot and skin clearances are cut-based and not reported as distances; wires are not moved.
