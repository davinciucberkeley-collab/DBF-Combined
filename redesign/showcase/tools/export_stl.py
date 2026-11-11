"""export_stl.py - binary STL files of the K09-L for GitHub's 3D viewer (redesign/showcase/stl/).

    blender -b --factory-startup -P redesign/showcase/tools/export_stl.py

Builds the aircraft from redesign/subsystems/*/fusion/ (blender_backend.build), then writes, in MILLIMETRES:
    k09l-assembly.stl   the flight aircraft (every part and wire; transport box and loose spares excluded)
    <subsystem>.stl     one per subsystem (wires go with harness; spares go with landing; transport box included)
Prints triangle counts and sizes. Files are capped at 25 MB (decimated if larger).
"""
import fnmatch
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(SHOW), 'blender'))
sys.dont_write_bytecode = True

import bpy                       # noqa: E402
import blender_backend as bb     # noqa: E402

NOT_FLIGHT = ['TRN-*', 'GER-005', 'GER-006', 'GER-009', 'GER-010', 'GER-011', 'GER-012', 'GER-013']
LIMIT = 25 * 1024 * 1024


def tris(objs, ratio=1.0):
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for ob in objs:
        mod = None
        if ratio < 1.0:
            mod = ob.modifiers.new('dec', 'DECIMATE')
            mod.ratio = ratio
            dg.update()
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        M = ob.matrix_world
        vs = [M @ v.co for v in me.vertices]
        for t in me.loop_triangles:
            a, b, c = (vs[i] for i in t.vertices)
            n = (b - a).cross(c - a)
            n = n.normalized() if n.length > 0 else n
            out.append((n, a, b, c))
        ev.to_mesh_clear()
        if mod:
            ob.modifiers.remove(mod)
    return out


def write(path, objs, name):
    ratio = 1.0
    while True:
        T = tris(objs, ratio)
        size = 84 + 50 * len(T)
        if size <= LIMIT:
            break
        ratio *= LIMIT / size * 0.95
    with open(path, 'wb') as f:
        f.write(('K09-L %s, millimetres, x aft y right z up' % name).encode()[:80].ljust(80, b' '))
        f.write(struct.pack('<I', len(T)))
        for n, a, b, c in T:
            f.write(struct.pack('<12fH', n.x, n.y, n.z, *(a * 1000), *(b * 1000), *(c * 1000), 0))
    print('STL %-22s %8d triangles %7.2f MB%s' % (os.path.basename(path), len(T), size / 1e6,
                                                   '' if ratio == 1.0 else '  decimated %.2f' % ratio))


def main():
    out = os.path.join(SHOW, 'stl')
    os.makedirs(out, exist_ok=True)
    be, ctx, graph, _ = bb.build(False, None)
    parts = {i: ob for i, ob in be.objects.items() if not ob.get('mass_proxy')}   # no lumped-mass proxies
    wires = dict(be.wires)
    flight = [ob for i, ob in parts.items() if not any(fnmatch.fnmatchcase(i, p) for p in NOT_FLIGHT)] + list(wires.values())
    write(os.path.join(out, 'k09l-assembly.stl'), flight, 'flight assembly')
    subs = {}
    for i, ob in parts.items():
        subs.setdefault(ob.get('subsystem'), []).append(ob)
    subs.setdefault('harness', []).extend(wires.values())
    for s, objs in sorted(subs.items()):
        write(os.path.join(out, '%s.stl' % s), objs, s)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
