"""render_drawing.py - orthographic views of the K09-L for the general-arrangement sheet (FIG A1-01 / FIG CFG-01).

    blender -b --factory-startup -P redesign/showcase/drawing/render_drawing.py -- [--ppm 1400] [--out DIR]

Technical-illustration style: every part in one light neutral matte material (view-layer material override), soft
studio light, Freestyle ink outlines, transparent film. All three elevations share ONE scale (--ppm pixels per
metre, default 1400) so the SVG sheet (make_sheet.py) can place dimension lines exactly: views.json carries, for
each view, the camera right/up vectors, the image centre in view coordinates and the pixel size. The iso inset is a
perspective render and carries no scale. Output: <out>/{top,front,side,iso}.png + <out>/views.json
(default redesign/site/assets/drawing/). Reuses redesign/blender/render_kit.Stage for the build, roles and outlines.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
REDESIGN = os.path.dirname(SHOW)
BL = os.path.join(REDESIGN, 'blender')
sys.path.insert(0, BL)
sys.dont_write_bytecode = True

import bpy                       # noqa: E402
from mathutils import Vector     # noqa: E402
import blender_backend as bb     # noqa: E402
import render_kit as rk          # noqa: E402

# the flying aircraft: everything that leaves the box, minus the harness (inside the wing) and wires
FLIGHT = ['WNG-*', 'FIN-*', 'POD-*', 'GER-001-*', 'GER-002-*', 'GER-003-*', 'GER-004-*', 'GER-007-*', 'GER-008-*',
          'PRP-*', 'MEC-*', 'PWR-*', 'AVN-*']
VIEWS = {                          # name: (azimuth from the nose, elevation)  see render_kit.PRESETS
    'top': (0, 90), 'front': (0, 0), 'side': (90, 0),
}
FILL = '#E3E7ED'                   # light neutral: reads on the light panel and on the dark stage
INK = '#1F2328'
MARGIN_M = 0.025                   # metres of air around the subject in each view


def args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--ppm', type=float, default=1400.0)
    ap.add_argument('--out', default=os.path.join(REDESIGN, 'site', 'assets', 'drawing'))
    ap.add_argument('--samples', type=int, default=48)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return ap.parse_args(argv)


def flat_material():
    m = bb._principled('drawing fill', bb.srgb(FILL), rough=0.85)
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for k, v in (('Specular IOR Level', 0.15), ('Coat Weight', 0.0), ('Metallic', 0.0)):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = v
    return m


def plain_world(sc, strength=0.55):
    w = bpy.data.worlds.new('drawing world')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (1, 1, 1, 1)
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs['Surface'])


def soften_lights(scale=0.45):
    """Technical-illustration light: no cast shadows, gentle gradients, the world fills the rest."""
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.data.energy *= scale
            ob.data.use_shadow = False


def bbox_world(ob):
    return [ob.matrix_world @ Vector(c) for c in ob.bound_box]


def main():
    a = args()
    os.makedirs(a.out, exist_ok=True)
    be, ctx, graph, _ = bb.build(False, None)
    S = rk.Stage(be, ctx, graph, 'studio', engine='EEVEE', samples=a.samples)
    sc = S.sc
    sc.eevee.taa_render_samples = a.samples
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    plain_world(sc, 0.75)
    S.roles(context=FLIGHT)
    vl = sc.view_layers[0]
    flat = flat_material()                        # EEVEE Next ignores view_layer.material_override: set it per object
    for ob in S._visible():
        for slot in ob.material_slots:
            slot.link = 'OBJECT'
            slot.material = flat
    # outlines: the sheet shows the renders at roughly 560 px/m, so draw the ink thick enough to survive the downscale
    fs = vl.freestyle_settings
    ink = fs.linesets['ink'].linestyle
    ink.color, ink.alpha = bb.srgb(INK), 0.9
    ink.thickness = max(1.6, 1.5 * a.ppm / 560.0)
    fs.crease_angle = math.radians(134)

    objs = S._visible()
    pts = S._points(objs)
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre, radius = (lo + hi) / 2, max((hi - lo).length / 2, 0.02)
    cd = bpy.data.cameras.new('cam')
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    S.cam = cam
    cd.sensor_fit, cd.sensor_width = 'HORIZONTAL', 36
    cd.clip_start, cd.clip_end = radius / 200, radius * 200
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.resolution_percentage = 100

    meta = {'ppm': a.ppm, 'margin_m': MARGIN_M, 'fill': FILL, 'ink': INK, 'engine': 'EEVEE', 'samples': a.samples,
            'frame': 'x aft from the wing leading edge, y right, z up (cruise); views.json px = (p.r - cu) * ppm + w/2, '
                     'py = h/2 - (p.u - cv) * ppm',
            'bbox_m': {'lo': [round(v, 4) for v in lo], 'hi': [round(v, 4) for v in hi]},
            'views': {}}
    times = []
    for name, (az, el) in VIEWS.items():
        t0 = time.time()
        view = rk._view_dir(az, el)
        dist = radius * 6
        cd.type = 'ORTHO'
        rk._look(cam, centre + view * dist, centre)
        R = cam.matrix_world.to_3x3()
        r, u = R.col[0].copy(), R.col[1].copy()
        us, vs = [p.dot(r) for p in pts], [p.dot(u) for p in pts]
        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
        W = int(math.ceil((u1 - u0 + 2 * MARGIN_M) * a.ppm))
        H = int(math.ceil((v1 - v0 + 2 * MARGIN_M) * a.ppm))
        cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
        cd.ortho_scale = W / a.ppm
        base = centre - r * centre.dot(r) - u * centre.dot(u)
        tgt = base + r * cu + u * cv
        rk._look(cam, tgt + view * dist, tgt)
        sc.render.resolution_x, sc.render.resolution_y = W, H
        S._lights(centre, radius, view, ortho=True)
        soften_lights()
        if S.floor is not None:
            S.floor.hide_render = True
        bpy.context.view_layer.update()

        def px(p):
            return ((p.dot(r) - cu) * a.ppm + W / 2, H / 2 - (p.dot(u) - cv) * a.ppm)
        parts = {}
        for ob in objs:
            ps = [px(p) for p in bbox_world(ob)]
            info = graph.parts.get(ob.name) or {}
            parts[ob.name] = {'bbox_px': [round(min(p[0] for p in ps), 1), round(min(p[1] for p in ps), 1),
                                          round(max(p[0] for p in ps), 1), round(max(p[1] for p in ps), 1)],
                              'subsystem': info.get('subsystem', ob.get('subsystem')), 'name': info.get('name', '')}
        sc.render.filepath = os.path.join(a.out, name + '.png')
        bpy.ops.render.render(write_still=True)
        meta['views'][name] = {'file': name + '.png', 'w': W, 'h': H, 'az_deg': az, 'el_deg': el,
                               'r': [round(v, 6) for v in r], 'u': [round(v, 6) for v in u],
                               'cu': round(cu, 6), 'cv': round(cv, 6), 'ortho': True, 'parts': parts}
        times.append((name, time.time() - t0))
        print('rendered %s %dx%d in %.1f s' % (name, W, H, times[-1][1]))

    # iso inset: perspective, no scale
    t0 = time.time()
    S.size = (1400, 1000)
    sc.render.resolution_x, sc.render.resolution_y = S.size
    S.camera('iso', fit='visible', lens=50, az=34, el=24, frame=(0.03, 0.97, 0.03, 0.97), floor=False)
    soften_lights()
    S.floor.hide_render = True
    sc.render.filepath = os.path.join(a.out, 'iso.png')
    bpy.ops.render.render(write_still=True)
    meta['views']['iso'] = {'file': 'iso.png', 'w': S.size[0], 'h': S.size[1], 'az_deg': 34, 'el_deg': 24,
                            'ortho': False, 'lens_mm': 50}
    print('rendered iso in %.1f s' % (time.time() - t0))
    with open(os.path.join(a.out, 'views.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=1)
    print('wrote', os.path.join(a.out, 'views.json'))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
