# Collision check: no parts phasing

`collide.py` checks that no two parts of K09-L occupy the same space, so the CAD can go into a rigid-body physics
simulator as drawn. It meshes every CAD body with the same builders as the GLB and the shop STLs, in Blender 4.2.3
(path in `inputs/SIM-TOOLS.md`), and measures how deep any point of one part lies inside a different part.

```
python -I redesign/collision/collide.py              # static pose + both elevon limits (about 5 min)
python -I redesign/collision/collide.py --no-sweep   # static pose only
python -I redesign/collision/collide.py --transport  # also the box, cradles and trays in their transport places
```

Exit code 0 = PASS. The report is `out/REPORT.md`; `out/report.json` has every pair down to 0.01 mm.

## What it checks

| Check | Rule |
|---|---|
| Penetration | Two different parts may touch but not overlap: depth ≤ 0.05 mm. 0.05 mm covers the chord error of two tessellations of one curved, bonded face (a tape skin on its core). |
| Containment | A body wholly inside a body of another part fails. |
| Elevon sweep | Each limited revolute joint (the four elevon panels, ±25°) is turned to each limit with everything bonded to it (horns, torque tubes, bridge rod), and checked against what did not move. |
| Holes and pockets | A part's cuts (`Component.cut`, `Context.seat`, `interfaces/seats.json`) are removed material, without mesh booleans. |

## What it does not check

- The real Fusion kernel geometry. Everything here is the stub-backend CAD (UNVERIFIED-IN-FUSION).
- Clearance margins. A 0.05 mm gap passes; the clearance claims (prop keep-outs in `fusion/check.py`, hinge throw)
  stay where they are.
- Flexible parts and linkages in the sweep: the hinge tapes (`MEC-010`) bend with the panel and the pushrods
  (`MEC-003`) follow the four-bar. They are held out of the sweep and listed in the report.
- Spinning props. `fusion/check.py` covers the swept prop discs as keep-outs.

## How a part receives another

When a real part has a hole, pocket or slot for another part, declare it once in `interfaces/seats.json`. Each row
names the host, the guest and the reason. The host is cut by the guest's filled envelope (a tube cuts a round hole,
not a ring). `"shop": true` puts the cavity into the shop file at that size (a printed slot or pocket). The default,
false, keeps it out of the shop file: threaded holes stay printed pilots, and drilled holes stay notes. The GLB and
Fusion apply every cut.
