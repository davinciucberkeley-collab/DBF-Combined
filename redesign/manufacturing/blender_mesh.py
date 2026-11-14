"""blender_mesh.py - runs INSIDE Blender (bpy). Turns each print job's CAD bodies into ONE solid and writes it as a raw
binary STL in the aircraft frame, millimetres. Called by make_shop_files.py; not meant to be run by hand:

    blender -b --factory-startup --python-exit-code 1 -P blender_mesh.py -- <jobs.json> <out dir>

Bodies are meshed by redesign/blender/blender_backend.py's builders (the same code that makes the GLB the viewer
shows), placed by the component matrix, scaled to mm, then united with Blender's EXACT boolean (one modifier with a
collection operand). The result is checked for manifold edges here and again, independently, in mesh_ops.py.
Writes <out dir>/<job id>.stl and <out dir>/blender_report.json.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
for _p in (os.path.join(REDESIGN, 'blender'), os.path.join(REDESIGN, 'fusion'), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bmesh                      # noqa: E402
import bpy                        # noqa: E402
from mathutils import Matrix      # noqa: E402

import blender_backend as bb      # noqa: E402  (mesh builders only; its backend class is not used)
import cad_source as cs           # noqa: E402
import mesh_ops                   # noqa: E402

GROW_MM = 0.01


DEFECTS = []                      # CAD bodies that needed the hole-crossing repair (reported to the caller)


def _inside(pt, loop):
    x, y = pt
    c = False
    for i in range(len(loop)):
        (x1, y1), (x2, y2) = loop[i - 1], loop[i]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _despike(loop, eps=1e-9):
    """Drop repeated points and points where the outline doubles back on itself (zero-width spikes)."""
    pts = [list(p) for p in loop]
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            d1, d2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
            if abs(d1[0]) + abs(d1[1]) < eps or \
                    (abs(d1[0] * d2[1] - d1[1] * d2[0]) < eps * eps * 1e3 and d1[0] * d2[0] + d1[1] * d2[1] < 0):
                del pts[i]
                changed = True
                break
    return pts


def body_object(name, shape_json, M, col, grow=0.0):
    """One CAD body as a mesh object (world mm). A prism 'hole' loop that crosses its outer loop (an open notch,
    which the polygon tessellation cannot represent) is made the way Fusion would: outer prism minus the hole."""
    if shape_json['kind'] == 'prism':
        clean = [_despike(l) for l in shape_json['loops']]
        if clean != shape_json['loops']:
            DEFECTS.append('%s body "%s": zero-width spike / repeated point in a loop (removed in the export)'
                           % (name.split('#')[0].split('+')[0], shape_json.get('name', '')))
            shape_json = dict(shape_json, loops=clean)
    if shape_json['kind'] == 'prism' and len(shape_json['loops']) > 1:
        outer = shape_json['loops'][0]
        cross = [l for l in shape_json['loops'][1:] if not all(_inside(p, outer) for p in l)]
        if cross:
            keep = dict(shape_json, loops=[outer] + [l for l in shape_json['loops'][1:] if l not in cross])
            ob = _body(name, keep, M, col, grow)
            eps = 1e-5 * (1 if shape_json['depth'] > 0 else -1)
            cut_col = bpy.data.collections.new(name + ' cut')
            bpy.context.scene.collection.children.link(cut_col)
            for k, l in enumerate(cross):
                _body('%s cut%d' % (name, k), dict(shape_json, loops=[l], offset=shape_json['offset'] - eps,
                                                    depth=shape_json['depth'] + 2 * eps), M, cut_col, 0.0)
            mod = ob.modifiers.new('cut', 'BOOLEAN')
            mod.operation, mod.solver, mod.operand_type, mod.collection = 'DIFFERENCE', 'EXACT', 'COLLECTION', cut_col
            dg = bpy.context.evaluated_depsgraph_get()
            me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
            ob.modifiers.remove(mod)
            ob.data = me
            DEFECTS.append('%s body "%s": %d hole loop(s) cross the outline (made as outline minus hole)'
                           % (name.split('#')[0].split('+')[0], shape_json.get('name', ''), len(cross)))
            return ob
    return _body(name, shape_json, M, col, grow)


def _body(name, shape_json, M, col, grow=0.0):
    shape = cs.shape_from_json(shape_json)
    bm = bmesh.new()
    bb.BUILDERS[shape.kind](bm, shape)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-9)
    bm.transform(Matrix.Scale(1000.0, 4) @ M)                 # local m -> world mm
    if grow > 0:                                              # move every face out by ~grow mm (per-axis scale
        lo = [min(v.co[i] for v in bm.verts) for i in range(3)]   # about the body's box centre)
        hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
        for v in bm.verts:
            for i in range(3):
                c, h = (lo[i] + hi[i]) / 2, (hi[i] - lo[i]) / 2
                if h > 1e-9:
                    v.co[i] = c + (v.co[i] - c) * (h + grow) / h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def non_manifold(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    n = sum(1 for e in bm.edges if not e.is_manifold) + sum(1 for v in bm.verts if not v.is_manifold)
    bm.free()
    return n


def subtract(ob, cuts, tag):
    """EXACT difference of the world-placed cutter shapes [[shape_json, 4x4], ...] (fusionkit Component.cut) from ob."""
    if not cuts:
        return
    scn = bpy.context.scene
    col = bpy.data.collections.new(tag + ' cutters')
    scn.collection.children.link(col)
    for k, (s, M) in enumerate(cuts):
        _body('%s cut%d' % (tag, k), s, Matrix(M), col, 0.0)
    mod = ob.modifiers.new('cuts', 'BOOLEAN')
    mod.operation, mod.solver, mod.operand_type, mod.collection = 'DIFFERENCE', 'EXACT', 'COLLECTION', col
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.remove(mod)
    ob.data = me


def union(job, grow=0.0):
    scn = bpy.context.scene
    tag = job['id'] + ('+%g' % grow if grow else '')
    col = bpy.data.collections.new(tag)
    scn.collection.children.link(col)
    M = Matrix(job['matrix'])
    obs = [body_object('%s#%d' % (tag, i), s, M, col, grow) for i, s in enumerate(job['bodies'])]
    base = obs[0]
    if len(obs) > 1:
        ops = bpy.data.collections.new(tag + ' operands')
        scn.collection.children.link(ops)
        for ob in obs[1:]:
            col.objects.unlink(ob)
            ops.objects.link(ob)
        mod = base.modifiers.new('union', 'BOOLEAN')
        mod.operation = 'UNION'
        mod.solver = 'EXACT'
        mod.operand_type = 'COLLECTION'
        mod.collection = ops
        mod.use_self = True
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(base.evaluated_get(dg))
        base.modifiers.remove(mod)
        base.data = me
    subtract(base, job.get('cuts') or [], tag)
    bm = bmesh.new()
    bm.from_mesh(base.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(base.data)
    bm.free()
    me = base.data
    tris = [[tuple(me.vertices[i].co) for i in p.vertices] for p in me.polygons]
    return tris, non_manifold(me), len(obs)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    jobs_path, out = argv[0], argv[1]
    os.makedirs(out, exist_ok=True)
    with open(jobs_path, encoding='utf-8') as f:
        jobs = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rep = {}
    for job in jobs:
        try:
            tris, nm, nb = union(job)
            grown = 0.0
            if nm and nb > 1:                       # bodies that touch only along an edge: fuse them with a 0.01 mm
                g = GROW_MM                         # overlap (below any print tolerance) and keep the better result
                t2, nm2, _ = union(job, g)
                if nm2 < nm:
                    tris, nm, grown = t2, nm2, g
            mesh_ops.write_stl(os.path.join(out, job['id'] + '.stl'), tris, 'raw ' + job['id'])
            rep[job['id']] = {'ok': True, 'tris': len(tris), 'non_manifold': nm, 'bodies': nb, 'grown_mm': grown}
        except Exception as e:                      # keep going; the caller reports the failure
            import traceback
            rep[job['id']] = {'ok': False, 'error': '%s: %s' % (type(e).__name__, e),
                              'trace': traceback.format_exc()[-800:]}
        print('blender_mesh %-24s %s' % (job['id'], rep[job['id']].get('error') or
                                         '%(tris)d tris, %(non_manifold)d non-manifold' % rep[job['id']]))
    rep['_defects'] = sorted(set(DEFECTS))
    with open(os.path.join(out, 'blender_report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
