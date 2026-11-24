"""fea_coverage_render.py - which parts of concept A have a 3-D stress FEA (Structures page figure).

    blender -b --factory-startup -P fea_coverage_render.py -- [--glb redesign/blender/out/aircraft/glb/assembly.glb]
    -> fig/fea-coverage.raw.png, then python fea_coverage_render.py --compose -> fig/fea-coverage.png (legend added)
Colours (dataviz categorical order): blue = hub FEA (fea_hub.py, run d209: hub, both arm tubes near the hub, bridge, pins);
orange = arm + motor-cup FEA (fea_arm.py, FEA-ARM.md, 2026-11-16: one full arm tube and its cup; the tube and cup are
unchanged since); grey = hand calculations or not analysed. Part ids come from the glTF node extras (export_glb.py)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'fig')
HUB = ('CGE-001', 'CGE-004', 'CGE-009-', 'CGE-010-')
ARM = ('CGE-002-', 'CGE-003-')
COL = {'hub': '#2a78d6', 'arm': '#eb6834', 'none': '#d9d8d3'}


def hx(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))


def compose():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(11, 6.2), dpi=150); fig.patch.set_facecolor('#fcfcfb')
    fig.text(0.015, 0.95, 'What the 3-D stress analysis (FEA) covers', fontsize=12.5, weight='bold', color='#0b0b0b')
    fig.text(0.015, 0.915, 'Everything else is checked by hand calculations or beam models (review/QP-5, structures/iter2_margins.md), or not yet at all.', fontsize=9, color='#52514e')
    ax = fig.add_axes([0.0, 0.12, 1.0, 0.78]); ax.imshow(plt.imread(os.path.join(FIG, 'fea-coverage.raw.png'))); ax.axis('off')
    items = [(COL['hub'], 'Hub FEA (2026-11-17, D-207): printed hub, arm tubes near the hub, bridge tube, pins'),
             (COL['arm'], 'Arm FEA (2026-11-16, FEA-ARM.md): arm tube and motor cup (one arm; all four are alike)'),
             (COL['none'], 'No FEA: wing, spar, fins, ribs, struts, tray, feet, avionics (hand calculations)')]
    for k, (c, t) in enumerate(items):
        y = 0.075 - k * 0.032
        fig.patches.append(plt.Rectangle((0.02, y), 0.016, 0.022, transform=fig.transFigure, color=hx(c), ec='#9a9993', lw=0.5))
        fig.text(0.042, y + 0.004, t, fontsize=9, color='#0b0b0b')
    fig.savefig(os.path.join(FIG, 'fea-coverage.png'), facecolor=fig.get_facecolor()); print('fig/fea-coverage.png')


if '--compose' in sys.argv:
    compose(); raise SystemExit

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
glb = args[args.index('--glb') + 1] if '--glb' in args else os.path.join(HERE, '..', '..', '..', 'blender', 'out', 'aircraft', 'glb', 'assembly.glb')
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'OBJECT'; sh.show_cavity = True; sh.cavity_type = 'WORLD'
sh.show_object_outline = True; sh.object_outline_color = (0.3, 0.3, 0.3); sh.show_specular_highlight = False
sc.render.film_transparent = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1650, 940


def pid_of(o):
    while o is not None:
        for k in ('part_id', 'id'):
            if k in o.keys():
                return str(o[k])
        o = o.parent
    return ''


counts = {'hub': 0, 'arm': 0, 'none': 0}
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes:
    p = pid_of(o) or o.name
    k = 'hub' if p.startswith(HUB) else 'arm' if p.startswith(ARM) else 'none'
    counts[k] += 1
    o.color = hx(COL[k]) + (1.0,)
print('coverage objects', counts)
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = max(hi - lo) * 1.42
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
d = Vector((-1.0, -0.85, 0.7)).normalized()            # from ahead, left and above (Blender frame after the glTF import)
cam.location = ctr + d * 3.0 + Vector((0, 0, -0.04))
cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = os.path.join(FIG, 'fea-coverage.raw.png')
bpy.ops.render.render(write_still=True)
print('rendered', sc.render.filepath)
