"""selftest.py - does the Blender build match the fusionkit data the Fusion build uses? (about 5 s)

    blender -b --factory-startup -P redesign/blender/selftest.py -- [--examples | --root DIR]
Checks, per part: one object named by its part id; world bounding box within 1 mm of fusionkit's; mesh volume within
3 % of fusionkit's (revolves are 48-sided, smooth lofts are spline-refined); closed manifold mesh with outward normals;
custom properties present. Per wire: a mesh exists. Then the GLB round trip: export, re-import, every part id comes
back as a node with its extras. Exit code 1 on any FAIL. Default target: the example aircraft.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bmesh                     # noqa: E402
import bpy                       # noqa: E402
from mathutils import Vector     # noqa: E402
import blender_backend as bb     # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
root = argv[argv.index('--root') + 1] if '--root' in argv else None
examples = root is None and ('--examples' in argv or not argv)

fails = []


def check(ok, what):
    print(('ok    ' if ok else 'FAIL  ') + what)
    if not ok:
        fails.append(what)


be, ctx, graph, results = bb.build(examples, root)
check(all(r[2] for r in results), 'every module built (%d)' % len(results))
if not ctx.components:
    print('FAIL  no parts were built (no <subsystem>/fusion/*.py under the module root); nothing to check')
    sys.exit(1)
for pid, comp in ctx.components.items():
    ob = bpy.data.objects.get(pid)
    if ob is None:
        check(False, '%s: object exists' % pid)
        continue
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    flo, fhi = comp.bbox()
    err = max(max(abs(lo[i] - flo[i]), abs(hi[i] - fhi[i])) for i in range(3))
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    vol = bm.calc_volume(signed=True)
    manifold = all(e.is_manifold for e in bm.edges)
    bm.free()
    fvol = comp.volume_centroid()[0]
    rel = abs(vol - fvol) / fvol if fvol else 1
    props = all(k in ob for k in ('part_id', 'mass_g', 'status', 'material', 'interfaces'))
    check(err < 1e-3 and rel < 0.03 and manifold and vol > 0 and props,
          '%-8s bbox err %.2f mm, volume %+.1f %%, manifold %s, normals %s, props %s'
          % (pid, err * 1000, 100 * (vol - fvol) / fvol, manifold, 'out' if vol > 0 else 'IN', props))
for w in ctx.wires:
    ob = be.wires.get(w.edge)
    check(ob is not None and len(ob.data.polygons) > 0, '%-8s wire mesh (%d faces)' % (w.edge, len(ob.data.polygons) if ob else 0))

# GLB round trip
path = os.path.join(tempfile.mkdtemp(), 'selftest.glb')
bpy.ops.object.select_all(action='DESELECT')
for ob in be.glb_objects(list(be.objects.values()) + list(be.wires.values())):
    ob.hide_set(False)
    ob.select_set(True)
proxies = [p for p, c in ctx.components.items() if c.proxy]
check(all(be.objects[p].hide_render for p in proxies), 'mass proxies never rendered (%d: %s)' % (len(proxies), ', '.join(proxies)))
bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_extras=True, export_yup=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
names = {o.name: o for o in bpy.data.objects}
names.update({o['part_id']: o for o in bpy.data.objects if o.get('mass_proxy') and 'part_id' in o})
missing = [p for p in ctx.components if p not in names]
check(not missing, 'GLB round trip: all %d part ids present%s' % (len(ctx.components), (' (missing %s)' % missing) if missing else ''))
noextra = [p for p in ctx.components if p in names and 'mass_g' not in names[p]]
check(not noextra, 'GLB round trip: extras (mass_g, status, ...) kept%s' % ((' (lost on %s)' % noextra) if noextra else ''))
p = next(i for i, c in ctx.components.items() if not c.proxy)
c = ctx.components[p].bbox()
q = [names[p].matrix_world @ v.co for v in names[p].data.vertices]
check(abs(max(v.z for v in q) - c[1][2]) < 1e-3, 'GLB round trip: frame preserved (z up after import)')
print('\nselftest: %d FAIL' % len(fails) if fails else '\nselftest: all ok')
sys.exit(1 if fails else 0)
