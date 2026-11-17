"""fea_hub_render_blender.py - raw renders of the hub FEA utilisation skins (out_fea/hub_<case>.glb from fea_hub_figs.py).

    blender -b --factory-startup -P fea_hub_render_blender.py
    -> fig/fea-hub-<case>-outside.raw.png (all parts) and fig/fea-hub-<case>-inside.raw.png (printed hub hidden), cases F2, S2.
Workbench engine, vertex colours (linear), flat light with world cavity and outlines, orthographic view from ahead, right and above (hub frame: x aft, y right,
z up). Never run this while an FEA solve is running (64 GB machine). fea_hub_figs.py --compose adds the legend.
"""
import math, os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, FIG = os.path.join(HERE, 'out_fea'), os.path.join(HERE, 'fig')


def setup():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'FLAT'; sh.color_type = 'VERTEX'; sh.show_specular_highlight = False
    sh.show_cavity = True; sh.cavity_type = 'WORLD'; sh.cavity_ridge_factor = 1.0; sh.cavity_valley_factor = 1.5
    sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.0
    sh.show_shadows = False
    sh.show_object_outline = True; sh.object_outline_color = (0.25, 0.25, 0.25)
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 1500, 1100
    sc.view_settings.view_transform = 'Standard'
    return sc


def render(case, sc):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, 'hub_%s.glb' % case))
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in meshes:
        for p in o.data.polygons:
            p.use_smooth = False
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (lo + hi) / 2
    cam_d = bpy.data.cameras.new('cam'); cam_d.type = 'ORTHO'; cam_d.ortho_scale = max(hi - lo) * 1.05
    cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
    d = Vector((-1.0, 0.9, 0.75)).normalized()          # from ahead (-x), right (+y), above (+z)
    cam.location = ctr + d * 1.0
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    for view, hide in (('outside', ()), ('inside', ('hub (printed PETG)',))):
        for o in meshes:
            o.hide_render = any(o.name.startswith(h) for h in hide)
        sc.render.filepath = os.path.join(FIG, 'fea-hub-%s-%s.raw.png' % (case, view))
        bpy.ops.render.render(write_still=True)
        print('rendered', sc.render.filepath)


sc = setup()
for c in ('F2', 'S2'):
    render(c, sc)
