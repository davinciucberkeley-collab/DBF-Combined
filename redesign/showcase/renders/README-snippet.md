## K09-L renders

Rendered in Blender 4.2 (Cycles, 64 samples, OpenImageDenoise, Freestyle outlines) from the same `build(ctx)` modules as the Fusion assembly. Regenerate: `blender -b --factory-startup -P redesign/showcase/tools/render_showcase.py` (spec: `redesign/blender/specs/showcase.json`).

![K09-L in cruise attitude](renders/hero-iso.png)
*K09-L quad tailsitter in cruise attitude: 1.15 m flying wing, two fins with a motor above and below the wing.*

| | |
|---|---|
| ![Hover pose](renders/hover-pose.png) <br> Standing nose-up on its four fin-tip feet (take-off / landing pose). | ![Exploded view](renders/exploded.png) <br> Exploded view, labelled by subsystem. |
| ![Front view](renders/front.png) <br> Front view (orthographic). | ![Side view](renders/side.png) <br> Left side view (orthographic). |
| ![Top view](renders/top.png) <br> Top view (orthographic), nose up. | ![X-ray cutaway](renders/cutaway-xray.png) <br> X-ray: pod internals (FC, flight pack, tray, UBEC) and wiring harness. |
| ![Wing detail](renders/detail-wing.png) <br> Wing: XPS core (ghosted), CF spar, spar plugs, four elevon panels. | ![Fin detail](renders/detail-fin.png) <br> Right fin: CF motor tube, through-core block, canted motor mounts, braces. |
| ![Pod detail](renders/detail-pod.png) <br> Pod: printed tray, 4S 6500 mAh pack, flight controller, GPS mast, pitot boom. | ![Landing foot detail](renders/detail-foot.png) <br> Landing foot: printed shoe and piston, crushable XPS cartridge, neoprene pad. |
| ![Propulsion detail](renders/detail-propulsion.png) <br> Propulsion station: X3108S motor, APC 11x5.5 prop, 45 A ESC and capacitor on the fin. | ![Mechanisms detail](renders/detail-mechanisms.png) <br> Elevon linkage from below: servo, arm, pushrod, horns, CF inter-panel rod. |
| ![Harness detail](renders/detail-harness.png) <br> Harness routing: pod bundle to the wing-fin bundles and each fin's ESCs. | ![Transport box](renders/transport-box.png) <br> Transport box (ghosted) with the aircraft in its foam spar cradles. |

### 3-D models (GitHub viewer, millimetres)

| File | Contents | Triangles |
|---|---|---|
| [k09l-assembly.stl](stl/k09l-assembly.stl) | flight aircraft (no transport box, no loose spares) | 110,336 |
| [wing.stl](stl/wing.stl) | wing | 45,366 |
| [fins.stl](stl/fins.stl) | fins, motor tubes, mounts | 17,382 |
| [harness.stl](stl/harness.stl) | harness bundles + routed wires | 28,300 |
| [propulsion.stl](stl/propulsion.stl) | motors, props, adapters, ESCs | 7,936 |
| [landing.stl](stl/landing.stl) | feet + spares kit | 5,076 |
| [mechanisms.stl](stl/mechanisms.stl) | servos, horns, pushrods, torque tubes | 3,968 |
| [pod.stl](stl/pod.stl) | pod shell, tray, hatch, handle | 2,652 |
| [avionics.stl](stl/avionics.stl) | FC, GPS, receiver, airspeed, pitot | 1,092 |
| [transport.stl](stl/transport.stl) | transport box and cradle | 536 |
| [power.stl](stl/power.stl) | pack, power board, UBEC, capacitors | 296 |
