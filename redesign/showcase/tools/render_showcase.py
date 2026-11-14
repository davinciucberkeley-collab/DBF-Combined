"""render_showcase.py - showcase renders of the K09-L for the README (redesign/showcase/renders/).

    blender -b --factory-startup -P redesign/showcase/tools/render_showcase.py -- [--only id,id] [--samples 64]
        [--work DIR] [--spec redesign/blender/specs/showcase.json]

Reuses redesign/blender/render_kit.Stage and annotate.py. Spec format = render_figures.py plus the keys listed in the
spec's _note. Raw renders and sidecars go to --work (default: <showcase>/_work, not committed); the final PNG
(annotated when the figure has a caption or callouts) is copied to redesign/showcase/renders/<id>.png.
"""
import fnmatch
import json
import math
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
REDESIGN = os.path.dirname(SHOW)
BL = os.path.join(REDESIGN, 'blender')
sys.path.insert(0, BL)
sys.dont_write_bytecode = True

import bpy                       # noqa: E402
from mathutils import Matrix, Vector   # noqa: E402
import blender_backend as bb     # noqa: E402
import render_kit as rk          # noqa: E402
import annotate                  # noqa: E402


def args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--work', default=os.path.join(SHOW, '_work'))
    ap.add_argument('--spec', default=os.path.join(BL, 'specs', 'showcase.json'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return ap.parse_args(argv)


def expand(pats, spec):
    out = []
    for p in pats or []:
        out += spec[p[1:]] if p.startswith('@') else [p]
    return out


def centre(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return sum(pts, Vector()) / 8


def main():
    a = args()
    with open(a.spec, encoding='utf-8') as fh:
        spec = json.load(fh)
    figs = spec['figures']
    if a.only:
        figs = [f for f in figs if f['id'] in a.only.split(',')]
    os.makedirs(a.work, exist_ok=True)
    renders = os.path.join(SHOW, 'renders')
    os.makedirs(renders, exist_ok=True)
    be, ctx, graph, _ = bb.build(False, None)
    S = rk.Stage(be, ctx, graph, 'studio', samples=a.samples)
    items = S.items()
    times = []
    for f in figs:
        t0 = time.time()
        S.reset()
        S.set_size(*f.get('size', (1600, 1000)))
        S.roles(focus=expand(f.get('focus'), spec), context=expand(f.get('context', ['*']), spec),
                ghost=expand(f.get('ghost'), spec), hide=expand(f.get('hide'), spec), xray=expand(f.get('xray'), spec))
        saved = {i: ob.matrix_world.copy() for i, ob in items.items()}
        if f.get('rotate_y_deg'):
            R = Matrix.Rotation(math.radians(f['rotate_y_deg']), 4, 'Y')
            for ob in items.values():
                ob.matrix_world = R @ ob.matrix_world
        lab_parts = {}
        if f.get('sub_explode'):
            for i, ob in be.objects.items():
                sub = ob.get('subsystem')
                for pat, other in (f.get('sub_override') or {}).items():
                    if fnmatch.fnmatchcase(i, pat):
                        sub = other
                v = f['sub_explode'].get(sub)
                if v is None or ob.hide_render:
                    continue
                cy = centre(ob).y
                s = 0 if abs(cy) < 0.02 else (1 if cy > 0 else -1)
                ob.matrix_world = Matrix.Translation(Vector((v[0], v[1] * s, v[2]))) @ ob.matrix_world
        bpy.context.view_layer.update()
        for sub, text in (f.get('sub_labels') or {}).items():
            obs = [ob for ob in be.objects.values() if ob.get('subsystem') == sub and not ob.hide_render]
            if not obs:                                 # e.g. harness: mass proxies only, wires hidden when exploded
                continue
            obs = [o for o in obs if centre(o).y <= 0.02] or obs      # label the near (port) side
            big = max(obs, key=lambda o: (o.dimensions.x * o.dimensions.y * o.dimensions.z) ** (1 / 3))
            lab_parts[big.name] = text
            S.callout(big.name, text, '')
        for c in f.get('callouts', []):
            if isinstance(c, dict):
                S.callout(c.get('item'), c.get('text'), c.get('detail'), c.get('at'))
            else:
                S.callout(c)
        cam = f.get('camera', 'iso')
        cam = cam if isinstance(cam, dict) else {'preset': cam}
        fit = cam.get('fit', 'visible')
        if isinstance(fit, list):
            fit = [i for i in items if any(fnmatch.fnmatchcase(i, p) for p in fit)]
        S.camera(cam.get('preset', 'iso'), fit=fit, lens=cam.get('lens', 50), az=cam.get('az'), el=cam.get('el'),
                 frame=tuple(cam['frame']) if cam.get('frame') else None,
                 floor=f.get('floor'))
        if f.get('caption'):
            S.caption(f['caption'].get('title', ''), f['caption'].get('sub', ''))
        base = os.path.join(a.work, f['id'])
        meta = S.render(base, annotate=False)
        for i, ob in items.items():
            ob.matrix_world = saved[i]
        bpy.context.view_layer.update()
        if lab_parts:                                 # subsystem labels: name only, no part id
            js = base + '.json'
            m = json.load(open(js, encoding='utf-8'))
            for c in m['callouts']:
                if c['item'] in lab_parts:
                    c['title'], c['text'], c['detail'] = '', lab_parts[c['item']], None
            json.dump(m, open(js, 'w', encoding='utf-8'), indent=1)
        if f.get('annotate', True) and (f.get('caption') or f.get('callouts') or lab_parts):
            annotate.build(base + '.json', png=True)
            src = base + '.annotated.png'
        else:
            src = base + '.png'
        shutil.copyfile(src, os.path.join(renders, f['id'] + '.png'))
        times.append((f['id'], meta['render_s'], time.time() - t0, meta['clipped']))
    for t in times:
        print('TIME %-20s render %5.1f s total %5.1f s clipped %s' % t)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
