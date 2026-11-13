# Collision check: no parts phasing

`collide.py` checks that no two parts of K09-L occupy the same space, so the CAD can go into a rigid-body physics
simulator as drawn. It meshes every CAD body with the same builders as the GLB and the shop STLs, in Blender 4.5.14 LTS
(path in `inputs/SIM-TOOLS.md`), and measures how deep any point of one part lies inside a different part.

```
python -I redesign/collision/collide.py              # static pose + both elevon limits (about 5 min)
python -I redesign/collision/collide.py --no-sweep   # static pose only
python -I redesign/collision/collide.py --transport  # also the box, cradles and trays in their transport places
python -I redesign/collision/collide.py --glb        # + the gate on the EXPORTED model (export the GLB first; ~11 min)
python -I redesign/collision/collide.py --job-only   # write out/_job.json (parts + drawn wires) and stop
```

Two gates, both must pass (D-88). The CAD gate takes each part's holes from its cutters (removed material by
definition), so it cannot see a boolean that failed in the exported model; a 45° lead hole that came out uncut once
showed a wire through solid foam in the 3-D explorer while the CAD gate passed. `--glb` runs
`collide_glb_blender.py` on `blender/out/aircraft/glb/assembly.glb`: every part as the explorer shows it, cuts baked
in, no cutter honoured, the wires meshed from the same strands, and the wire-entry rule below. Each part is one solid
there (the exporter unites its bodies, `blender/README.md`), so the inside test is a parity count: a surface point of
one part is inside another when 3 of 5 skewed rays cross that part an odd number of times (one ray along a bore wall
counts noise). A sample counts only where its own part has material 0.01 mm behind it, so a zero-thickness wall left
by the union is not material. The full GLB gate takes about 11 min on an idle machine.

Exit code 0 = PASS. The report is `out/REPORT.md`; `out/report.json` has every pair down to 0.01 mm.

## What it checks

| Check | Rule |
|---|---|
| Penetration | Two different parts may touch but not overlap: depth ≤ 0.05 mm. 0.05 mm covers the chord error of two tessellations of one curved, bonded face (a tape skin on its core). |
| Containment | A body wholly inside a body of another part fails. |
| Elevon sweep | Each limited revolute joint (the four elevon panels, ±25°) is turned to each limit with everything bonded to it (horns, torque tubes, bridge rod), and checked against what did not move. |
| Holes and pockets | A part's cuts (`Component.cut`, `Context.seat`, `interfaces/seats.json`) are removed material, without mesh booleans. |
| Wires | Every routed wire is meshed as the 3-D model draws it (filleted at its bend radius, each strand at its diameter) and checked against every part, the tape skin and every other wire; every strand end must be seated in a part. `--audit-wires` lists each clash by route segment of `team/F2/harness.py`'s wire table. |

Wire rules (each one a physical fact, not a tolerance; D-86 made them strict):

- The packing-tape skin (`WNG-003`) is a solid like any other. A lead passes it only through a slit drawn in the
  tape (`cad.skin_slots` from `team/F2/harness.py`, cut in `wing.py`), where it is laid first and the tape is cut
  round it on the bench.
- A wire may sit up to 6 mm into its own terminal part: the solder pad or cup and its adhesive heat-shrink tail.
- A wire may pass through a connector fitted in-line on it (the JR pairs `HRN-105-*`, the XT30U pairs, the AS150U
  pack half), declared in the harness params (`cad.*.wire`).
- **Every strand end must be seated**: its surface on or in one of its own terminal parts or an in-line connector
  (axis within its radius + 0.5 mm). A lead that stops in mid-air fails. Report section "Wire ends not seated".
- No shared joints: every conductor lands on its own pad.
- The conductors of one wire (the two of a pair, the three of a servo ribbon, a pigtail and its extension) are
  checked against each other too (D-87).
- **No folds**: a drawn bend tighter than the strand's own radius makes the tube pass through itself; it fails
  (report section "Wire bends tighter than the wire", D-87).
- **Square entry, on a face** (GLB gate, D-88): where a strand enters its terminal part or an in-line connector it
  crosses one face within 25° of square, with its whole section on that face (0.1 mm clear of the face's edges), and
  runs at most 6 mm past it. A lead that slides in at a slant or over an edge or corner, as no soldered or crimped
  lead does, fails. Heat-shrink sleeves (`HRN-107-*`) are drawn on the soldered ends and count as in-line parts.

## What it does not check

- The real Fusion kernel geometry. Everything here is the stub-backend CAD (UNVERIFIED-IN-FUSION).
- Clearance margins. A 0.05 mm gap passes; the clearance claims (prop keep-outs in `fusion/check.py`, hinge throw)
  stay where they are.
- Wire flexibility: wires are checked as drawn (rigid tubes); slack, sag and vibration are not modelled.
- Flexible parts and linkages in the sweep: the hinge tapes (`MEC-010`) bend with the panel and the pushrods
  (`MEC-003`) follow the four-bar. They are held out of the sweep and listed in the report.
- Spinning props. `fusion/check.py` covers the swept prop discs as keep-outs.

## How a part receives another

When a real part has a hole, pocket or slot for another part, declare it once in `interfaces/seats.json`. Each row
names the host, the guest and the reason. The host is cut by the guest's filled envelope (a tube cuts a round hole,
not a ring). `"shop": true` puts the cavity into the shop file at that size (a printed slot or pocket). The default,
false, keeps it out of the shop file: threaded holes stay printed pilots, and drilled holes stay notes. The GLB and
Fusion apply every cut.
