# K09-L CAD modelling standards

Status: `PROPOSED` (A5, 2026-11-09). Applies to every `subsystems/<key>/fusion/<key>.py`. A module that breaks a
rule here fails CAD review even when `check.py` passes. Exceptions: a change request to A5.

## 1. Build order

`fusion/modules.txt` (Fusion builds in this order; a module may only join to parts built before it or in itself).

| # | Key | Designer | Joins to | Registers |
|---|---|---|---|---|
| 0 | datums | A5 (`k09kit.build_datums`) | — | 42 datums, aircraft envelope |
| 1 | `wing` | D1 | — (base part: the core) | spar bond, 4 elevon hinges |
| 2 | `fins` | D3 | wing spar, core | fin–tube, saddles, mounts, motor-to-mount stacks |
| 3 | `pod` | D2 | wing core | pod bond |
| 4 | `landing` | D5 | fins | feet; `KO-GROUND` |
| 5 | `propulsion` | E1 | fin mounts | prop adapters; `KO-PROP-UR/UL/LR/LL` |
| 6 | `mechanisms` | D6 | wing core, elevons | servos, horns, pushrods |
| 7 | `power` | F1 | pod tray | pack strap, distribution |
| 8 | `avionics` | F3 | pod, wing | FC, GPS, RX, airspeed, pitot |
| 9 | `harness` | F2 | every electrical part | every wire (`ctx.wire`) |
| 10 | `transport` | D7 | — (`flight: false`) | box, cradles |

`flight-software` has no module. Start from the matching folder in `fusion/skeleton/` (same order, part ids 9xx).

## 2. Naming = part ids

| Thing | Name | Example |
|---|---|---|
| Part id | `<PREFIX>-NNN`, prefixes `WNG FIN POD GER PRP PWR AVN HRN MEC TRN`; 001–899 real, **9xx reserved for the skeleton** | `FIN-003` |
| Instance | one id per physical part; L/R and UR/UL/LR/LL are separate ids, the name ends with the station | `PRP-002 Motor UL` |
| Fusion component | `<id> <name>` (set by the backend from `interfaces.json`); one component per id | `WNG-001 Wing core` |
| Body | the shape `name=` argument, else `<id>_<n>` | `core box`, `FIN-001_1` |
| Sketch / plane | `<id>_<n>[_s<i>]` (backend); datums `DP-` `DA-` `DX-` (`DATUMS.md`) | `DP-HINGE` |
| Joint | the `interfaces.json` edge id | `E-WNG-002` |
| Keep-out | `KO-<what>[-station]` | `KO-PROP-UR` |
| Module file | `subsystems/<key>/fusion/<key>.py` with `build(ctx)` | `subsystems/fins/fusion/fins.py` |

## 3. Geometry

| Rule | Why |
|---|---|
| Model in cruise attitude, frame and datums of `DATUMS.md`; never in hover attitude | one frame for CAD, CG and analysis |
| Every dimension from `ctx.value(key, unit)`, `ctx.D(datum)` or `<key>/params.json`; no literal that exists in `params.json` | one source of numbers (BRIEF) |
| Build the right / upper-right instance, then `k9.pair()` / `k9.quad()` | exact symmetry, half the code |
| Made parts: the shape the shop cuts or prints (core, fins, mounts, saddles, feet, pod) | drives templates and prints |
| Bought parts: an envelope plus the mounting face (motor, ESC, servo, pack, FC, GPS) | detail without value is the XV-24 lesson |
| No fastener, tape or glue bodies: fasteners live in the joint stack, tape and skin mass in the part they cover | mass and BOM stay single-entry |
| Wing section from `k9.section()` (B2's `subsystems/wing/mh45.dat` when present; placeholder until then) | the CAD and `cad_claims.py` use the same coordinates |
| Trailing edges ≥ 0.6 mm (`k9.TE_MIN_M`), foam cover over tubes ≥ 2 mm (`ASM-A5-MIN-COVER`) | hot-wire and slot practice |
| Keep shapes to prism / revolve / loft on axis-aligned planes (`fusionkit`) | the stub, Fusion and Blender build the same thing |
| Wires: `ctx.wire` routes with support points, never lines between parts | wiring is an installation |

Shared helpers (`k09kit.py`): airfoil loft (`section`, `section_loop`, `wing_core`, `elevon`), tubes (`spar_y`,
`tube_z`), fin plate (`fin_plate`), motor and prop (`motor_envelope`, `prop_disc`, `prop_keepout`), hinge
(`hinge_point`), mirrors (`pair`, `quad`), hover pose (`hover_pose`, `to_hover`, `hover_ground`). There is no tilt
joint on K09-L; the only moving joints are the four elevon hinges.

## 4. Materials

`material` in `interfaces.json` is plain text; the Fusion backend maps it to a library material for appearance and
an information-only mass (`backends/fusion_backend.py#MATERIALS`, `UNVERIFIED-IN-FUSION`). Use these words:

| Use | `material` text | Fusion library | Density / areal mass | Source |
|---|---|---|---|---|
| Wing core, elevons | `XPS foam F-250 + packing-tape skin` | Polystyrene | 30 kg/m³ + 0.065 kg/m² | `params.json#wing.core`, `#wing.skin` |
| Spar, motor tubes | `CF tube 22x20 (bought)` | Carbon Fiber | 0.102 kg/m | `params.json#wing.spar.mass_per_m_kgm` |
| Fins | `foam board 4.8 mm, paper faced` | Polystyrene | 0.20 kg/m² per layer | `params.json#fins.areal_mass_kgm2` |
| Mounts, saddles, tray, clips | `PETG (printed)` | PET Plastic | declared (infill) | G3 |
| Feet | `TPU (printed, crushable)` or `PETG (printed)` | Thermoplastic Polyurethane / PET | declared | C5, G3 |
| Pod shell | `foam board + PETG` | Polystyrene | declared | D2 |
| Bought electronics, motors, pack | `motor (bought)`, `servo (bought)`, `LiPo`, `electronics (bought)` | none (default) | declared | datasheet / scale |

## 5. Mass and CG

| Rule | Detail |
|---|---|
| Declared mass is authoritative | `mass_g` in `interfaces.json`; the backend writes it to the component attribute `dbf/mass_g` and the description. Fusion has no per-component mass override in the API: Fusion's own mass (geometry × library density) is printed beside it for information |
| Where the number comes from | weighed (`VERIFIED`) > datasheet > calc from the densities above (`EST`) |
| CG | `cg_xyz_m` from the CAD centroid (`Component.volume_centroid()`, as `skeleton/make_skeleton.py` does) unless weighed or the part is non-uniform (pack: geometric centre; motor: can centre) |
| Budget | each subsystem stays inside `params/mass_budget.json`; `check.py` warns over allocation, errors over 2 600 g |
| Review trigger | a `make` part whose Fusion mass differs from its declared mass by > 25 % (wrong geometry or wrong density) |

## 6. Joints

| Edge (`interfaces.json`) | Register with | Origin |
|---|---|---|
| fastened, clamped, press-fit | `ctx.rigid(edge, a, b, at=)` + full joint stack | on both parts (within 2 mm), at the fastener pattern centre |
| bonded, taped, strapped, thermal pad | `ctx.contact(edge, note)` | geometry must touch (bounding boxes within 2 mm) |
| hinged (elevons) | `ctx.revolute(edge, panel, core, at=k9.hinge_point(...), axis='Y', limits=wing.elevon.deflection_deg)` | on the hinge line |
| electrical | `ctx.wire(edge, route)` | ends on the two parts' connectors |

One registration per edge, by the owning subsystem; the other side lists it in `acknowledges`. Fusion: the
**00 Datums** component is grounded; ground the wing core after BuildAll if Fusion did not (UNVERIFIED-IN-FUSION).
A part placed with `ctx.part(rotate=)` must not carry a joint (the backend warns).

## 7. Status words

`PROPOSED` (in `interfaces.json`, no geometry) → `MODELLED` (built by a module) → `CHECKED` (passes
`check.py --strict` and its calcs) → `VERIFIED` (made part measured or weighed). `UNVERIFIED` = rests on a guess.

## 8. Before you hand a module over

1. `python -I redesign/fusion/check.py --strict` passes, or every WARN is a part another subsystem has not modelled.
2. `python -I redesign/fusion/tests/test_framework.py` still passes if you touched the framework.
3. No literal duplicates `params.json` (`grep` your module for numbers > 0.01).
4. Masses declared and inside the allocation; CGs filled.
5. Your keep-outs registered (propulsion, landing) and nothing of yours inside anyone else's.
6. Anything that depends on Fusion behaviour is marked `UNVERIFIED-IN-FUSION` in the module docstring.
