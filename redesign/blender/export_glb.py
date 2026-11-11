"""export_glb.py - build the aircraft in Blender from the subsystem modules and export GLB files for the web viewer.

    blender -b --factory-startup -P redesign/blender/export_glb.py -- [--examples | --root DIR] [--out DIR]
                                                                       [--mode material|subsystem|status]
Writes (default out: redesign/blender/out/<examples|aircraft>/glb/):
    assembly.glb        every part + every wire (+ joint empties), node name = part id / edge id / "JOINT <edge>"
    <subsystem>.glb     that subsystem's parts and the wires it owns
    manifest.json       files, part list (id, subsystem, status, mass_g, explode_m), frame note
Node extras (glTF "extras", from Blender custom properties): part_id, name, subsystem, material, mass_g, status,
make_or_buy, interfaces (JSON list of edge ids), explode_m [dx, dy, dz] in the AIRCRAFT frame; wires: edge, gauge_awg,
connector, bend_radius_mm, support_points ...
Frame: glTF is +Y up. The exporter maps aircraft (x aft, y right, z up) to glTF (x, z, -y): glTF x = aft,
glTF y = up, glTF z = left. explode_m stays in the aircraft frame (convert the same way in the viewer).
Takes a few seconds.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy                       # noqa: E402
import blender_backend as bb     # noqa: E402
import explode                   # noqa: E402


def args():
    import argparse
    ap = argparse.ArgumentParser(prog='export_glb.py')
    ap.add_argument('--examples', action='store_true', help='build the generic example aircraft')
    ap.add_argument('--root', help='module root (default redesign/subsystems)')
    ap.add_argument('--out', help='output folder')
    ap.add_argument('--mode', default='material', choices=('material', 'subsystem', 'status'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return ap.parse_args(argv)


def out_dir(a, kind):
    d = a.out or os.path.join(HERE, 'out', 'examples' if a.examples else 'aircraft', kind)
    os.makedirs(d, exist_ok=True)
    return d


def clean_private(objs):
    for ob in objs:
        for k in [k for k in ob.keys() if k.startswith('_')]:
            del ob[k]


def export(path, objs, be=None):
    """Export `objs`; mass proxies (HRN bundles) go out as empties with their extras (be.glb_objects)."""
    if be is not None:
        objs = be.glb_objects(objs)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_extras=True,
                              export_yup=True, export_apply=True, export_cameras=False, export_lights=False)
    return os.path.getsize(path)


def main():
    a = args()
    t0 = time.time()
    be, ctx, graph, results = bb.build(a.examples, a.root, a.mode)
    offs = explode.vectors(be, ctx, graph)
    explode.apply(be, offs, 0.0)                       # stays assembled; records explode_m on every part
    clean_private(be.objects.values())
    d = out_dir(a, 'glb')
    joints = [ob for ob, _ in be.joints.values()]
    files = {'assembly.glb': export(os.path.join(d, 'assembly.glb'),
                                    list(be.objects.values()) + list(be.wires.values()) + joints, be)}
    subs = sorted({c.subsystem for c in ctx.components.values()})
    for s in subs:
        objs = [be.objects[p] for p, c in ctx.components.items() if c.subsystem == s]
        objs += [be.wires[w.edge] for w in ctx.wires if w.sub == s and w.edge in be.wires]
        files[s + '.glb'] = export(os.path.join(d, s + '.glb'), objs, be)
    man = {'source': 'examples' if a.examples else (a.root or 'redesign/subsystems'), 'mode': a.mode,
           'frame': 'glTF +Y up: glTF (x, y, z) = aircraft (x aft, z up, -y). explode_m in aircraft frame, metres.',
           'files': {k: v for k, v in files.items()},
           'parts': [dict({'id': p, 'subsystem': c.subsystem, 'status': c.status, 'mass_g': c.mass_g,
                           'explode_m': list(be.objects[p]['explode_m'])}, **({'mass_proxy': True} if c.proxy else {}))
                     for p, c in ctx.components.items()],
           'wires': sorted(be.wires), 'joints': sorted(be.joints),
           'issues': [list(i) for i in ctx.issues]}
    with open(os.path.join(d, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, indent=1)
    for k, v in files.items():
        print('wrote %-22s %7.1f kB' % (k, v / 1024))
    print('export_glb: %d parts, %d wires, %.1f s -> %s' % (len(be.objects), len(be.wires), time.time() - t0, d))
    if not all(r[2] for r in results):
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
