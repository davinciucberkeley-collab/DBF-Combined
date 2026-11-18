"""render_drawings_blender.py - stage 2 of make_drawings_a.py, runs INSIDE Blender:

    blender -b --factory-startup --python-exit-code 1 -P render_drawings_blender.py -- <jobs.json> <work dir>

For each drawing job: the part solid exactly as the shop STL (manufacturing/blender_mesh.py union(): bodies united with the EXACT
boolean, shop cuts subtracted), moved from the aircraft frame into the part's design frame (inverse of the component matrix),
in mm. Writes <work>/<id>.stl, four orthographic line renders <work>/<id>_<view>.png (Freestyle: visible edges black, hidden
edges dashed grey; white faces) and <work>/<id>.json (bounding box and the mm -> pixel mapping of each view).
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for _p in (os.path.join(REDESIGN, 'manufacturing'), os.path.join(REDESIGN, 'blender'), os.path.join(REDESIGN, 'fusion')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import blender_mesh  # noqa: E402
import mesh_ops      # noqa: E402

RES = 1100
VIEWS = {                              # name: (camera looks along, image right, image up) in the part frame
    'top': (Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, 1, 0))),
    'front': (Vector((0, 1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
    'side': (Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
}


def setup_scene():
    scn = bpy.context.scene
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scn.render.engine = eng
            break
        except TypeError:
            continue
    scn.render.resolution_x = scn.render.resolution_y = RES
    scn.render.film_transparent = False
    scn.view_settings.view_transform = 'Standard'
    scn.render.use_freestyle = True
    scn.render.line_thickness_mode = 'ABSOLUTE'
    scn.render.line_thickness = 1.4
    w = bpy.data.worlds.new('w')
    w.color = (1, 1, 1)
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    scn.world = w
    fs = bpy.context.view_layer.freestyle_settings
    fs.crease_angle = math.radians(150)
    fs.as_render_pass = False
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new('vis')
    ls.select_by_visibility = True
    ls.visibility = 'VISIBLE'
    for k in ('select_silhouette', 'select_border', 'select_crease'):
        setattr(ls, k, True)
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new('visible')
    ls.linestyle.color = (0, 0, 0)
    ls.linestyle.thickness = 1.5
    hd = fs.linesets.new('hidden')
    hd.select_by_visibility = True
    hd.visibility = 'HIDDEN'
    for k in ('select_silhouette', 'select_border', 'select_crease'):
        setattr(hd, k, True)
    st = bpy.data.linestyles.new('hidden')
    st.color = (0.55, 0.55, 0.55)
    st.thickness = 0.9
    st.use_dashed_line = True
    st.dash1, st.gap1 = 6, 4
    hd.linestyle = st
    mat = bpy.data.materials.new('white')
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs[0].default_value = (1, 1, 1, 1)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs[0], out.inputs[0])
    cam_d = bpy.data.cameras.new('cam')
    cam_d.type = 'ORTHO'
    cam = bpy.data.objects.new('cam', cam_d)
    scn.collection.objects.link(cam)
    scn.camera = cam
    return scn, mat, cam


def clear_parts():
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH':
            bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def same_local_cuts(a, b, tol=1e-7):
    """True when parts a and b have the same cut shapes at the same poses relative to their own part frame (cuts are
    [shape, world matrix] pairs)."""
    ca, cb = a.get('cuts') or [], b.get('cuts') or []
    if len(ca) != len(cb):
        return False
    Ai, Bi = Matrix(a['matrix']).inverted(), Matrix(b['matrix']).inverted()
    for (sa, ma), (sb, mb) in zip(ca, cb):
        if json.dumps(sa, sort_keys=True) != json.dumps(sb, sort_keys=True):
            return False
        ra, rb = Ai @ Matrix(ma), Bi @ Matrix(mb)
        if max(abs(ra[i][j] - rb[i][j]) for i in range(4) for j in range(4)) > tol:
            return False
    return True


def look(cam, centre, d, right, up, dist):
    """Place the ortho camera at centre - d * dist looking along d with image axes right / up."""
    z = -d.normalized()
    x = right.normalized()
    y = up.normalized()
    R = Matrix((x, y, z)).transposed().to_4x4()
    cam.matrix_world = Matrix.Translation(centre - d.normalized() * dist) @ R


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    jobs_path, work = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    os.makedirs(work, exist_ok=True)
    jobs = json.load(open(jobs_path, encoding='utf-8'))
    only = set(argv[2].split(',')) if len(argv) > 2 and argv[2] else None
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn, mat, cam = setup_scene()
    for job in jobs:
        if only and job['id'] not in only:
            continue
        try:
            tris, nm, nb = blender_mesh.union(job)
            if nm and nb > 1:                      # bodies touching only along an edge: retry with a 0.01 mm overlap (as make_shop_files)
                clear_parts()
                t2, nm2, _ = blender_mesh.union(job, blender_mesh.GROW_MM)
                if nm2 < nm:
                    tris, nm = t2, nm2
        except Exception as e:  # keep going; compose reports the gap
            print('drw %-12s FAILED %s: %s' % (job['id'], type(e).__name__, e))
            clear_parts()
            continue
        M = Matrix(job['matrix'])
        M.translation = M.translation * 1000.0
        Mi = M.inverted()
        loc = [[tuple(Mi @ Vector(p)) for p in t] for t in tris]
        clear_parts()
        mesh_ops.write_stl(os.path.join(work, job['id'] + '.stl'), loc, job['id'] + ' design frame mm')
        verts, faces, idx = [], [], {}
        for t in loc:
            f = []
            for p in t:
                k = tuple(round(c, 6) for c in p)
                if k not in idx:
                    idx[k] = len(verts)
                    verts.append(k)
                f.append(idx[k])
            faces.append(f)
        me = bpy.data.meshes.new(job['id'])
        me.from_pydata(verts, [], faces)
        me.update()
        ob = bpy.data.objects.new(job['id'], me)
        ob.data.materials.append(mat)
        scn.collection.objects.link(ob)
        lo = Vector([min(v[i] for v in verts) for i in range(3)])
        hi = Vector([max(v[i] for v in verts) for i in range(3)])
        c = (lo + hi) / 2
        ext = hi - lo
        meta = dict(id=job['id'], lo=list(lo), hi=list(hi), non_manifold=nm, views={})
        span = max(ext) * 1.12 + 2.0
        dist = max(ext) * 3 + 50
        cam.data.clip_end = dist * 4
        # views follow the part's own proportions: L = longest, M = middle, S = shortest design axis. FRONT looks along M (shows L x S),
        # TOP looks down S (L x M) above it, RIGHT SIDE looks along -L (end view) to its right: third-angle, long axis across the sheet.
        order = sorted(range(3), key=lambda i: -ext[i])
        E = [Vector([1.0 if j == i else 0.0 for j in range(3)]) for i in range(3)]
        Lv, Mv, Sv = (E[i] for i in order)
        fr_d, fr_u = Mv, Sv
        fr_r = fr_d.cross(fr_u)
        views = {'front': (fr_d, fr_r, fr_u), 'top': (-Sv, fr_r, (-Sv).cross(fr_r) * -1), 'side': (-fr_r, (-fr_r).cross(Sv), Sv)}
        meta['axes'] = dict(long='xyz'[order[0]], middle='xyz'[order[1]], short='xyz'[order[2]])
        for name, (d, r, u) in views.items():
            cam.data.ortho_scale = span
            look(cam, c, d, r, u, dist)
            scn.render.filepath = os.path.join(work, '%s_%s.png' % (job['id'], name))
            bpy.ops.render.render(write_still=True)
            meta['views'][name] = dict(centre=list(c), right=list(r), up=list(u), span=span, res=RES)
        d = Vector((-1, 1, -0.8)).normalized()
        r = d.cross(Vector((0, 0, 1))).normalized()
        u = r.cross(d).normalized()
        pts = [Vector(v) for v in verts]
        w = max(abs((p - c).dot(r)) for p in pts) * 2
        h = max(abs((p - c).dot(u)) for p in pts) * 2
        cam.data.ortho_scale = max(w, h) * 1.1 + 2.0
        look(cam, c, d, r, u, dist)
        scn.render.filepath = os.path.join(work, '%s_iso.png' % job['id'])
        bpy.ops.render.render(write_still=True)
        meta['views']['iso'] = dict(centre=list(c), right=list(r), up=list(u), span=cam.data.ortho_scale, res=RES)
        meta['stl'] = {job['members'][0]: job['id'] + '.stl'}
        for mj in job.get('member_jobs') or []:          # the other printed members (mirror images included): STL only
            try:
                t_, n_, b_ = blender_mesh.union(mj)
                if n_ and b_ > 1:
                    clear_parts()
                    t2, n2, _ = blender_mesh.union(mj, blender_mesh.GROW_MM)
                    if n2 < n_:
                        t_, n_ = t2, n2
                Mm = Matrix(mj['matrix'])
                Mm.translation = Mm.translation * 1000.0
                Mmi = Mm.inverted()
                mloc = [[tuple(Mmi @ Vector(p)) for p in t] for t in t_]
                if n_ > nm and Matrix(mj['matrix']).to_3x3().determinant() > 0 and \
                        json.dumps(mj['bodies'], sort_keys=True) == json.dumps(job['bodies'], sort_keys=True) and \
                        same_local_cuts(job, mj):
                    # same design-frame geometry as the representative, only placed differently: the exact boolean failed in this
                    # pose (floating point), so write the representative's design-frame mesh (the shop part is the same file)
                    print('drw %-12s member %s: union open (%d edges) in its pose; same geometry as %s, its mesh used' % (job['id'], mj['id'], n_, job['members'][0]))
                    mloc, n_ = loc, nm
                mesh_ops.write_stl(os.path.join(work, mj['id'] + '.stl'), mloc, mj['id'] + ' design frame mm')
                meta['stl'][mj['id']] = mj['id'] + '.stl'
                meta.setdefault('member_non_manifold', {})[mj['id']] = n_
            except Exception as e:
                print('drw %-12s member %s FAILED %s: %s' % (job['id'], mj['id'], type(e).__name__, e))
            clear_parts()
        json.dump(meta, open(os.path.join(work, job['id'] + '.json'), 'w'))
        print('drw %-12s ok  %d tris, non-manifold %d, %.1f x %.1f x %.1f mm' % (job['id'], len(tris), nm, ext[0], ext[1], ext[2]))
        clear_parts()


main()
