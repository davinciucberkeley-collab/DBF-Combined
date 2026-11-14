"""render_build.py - the K09-L build sequence as animation, one clip per BUILD-GUIDE stage plus the full film.

    python -I redesign/showcase/animation/assembly_check.py      # 1. plan + physics-check the motions (~25 min)
    python redesign/showcase/animation/render_build.py           # 2. render the checked plan (~19 min)
    python redesign/showcase/animation/render_build.py --preview # quick look: half size, every 3rd frame, to --work

Run step 2 with the system Python (needs Pillow). It animates build/assembly_plan.json, written by assembly_check.py,
and refuses to run without it. After any CAD change re-run both commands: the motions are re-derived from the new
geometry and re-checked, then re-rendered; nothing in this file names a position.

What the film shows is exactly the motion assembly_check.py tested, action by action in BUILD-GUIDE.md order
(assembly_plan.STEPS, each numbered step); nothing moves on a path the check did not sample:
  * rigid parts come in along the checked path (straight along a bore, pin, tube or screw axis, down onto their
    mounting face, or out-then-across where a straight line is blocked); screws and nuts turn as they run down their
    last 6 mm; bench sub-assemblies (spar + plugs + blocks, plugged motor tubes, brace + anchor + collar, the pod
    box, motor on its mount, servo with its arm, foot inserts, FC with its card) are put together beside the
    aircraft and then moved on as one piece;
  * the pod box is glued up piece by piece, each foam-board wall on its own checked path ('built');
  * the hatch comes in open, slides its tongue under the nose lip and turns down about the lip edge ('hinge':
    the same keyframes, translation and hinge angle, the check swept);
  * nothing that is laid, wet or cut in place moves: the hot-wired core and the panels cut free of it, tape, wet
    epoxy and the straps appear where they lie, wiped on in slices along their longest side; wires grow along
    their route, and a lead whose end part is not on yet is laid up to its first connector and finished later
    (its held run grows when that part is on); the elevon panels swing full TE-up and back about the gate's hinge
    joints, the hinge-tape half bonded to each panel turning with it.
  Parts of one part number at several stations (UR/UL/LR/LL, L/R) move together when their swept boxes do not
  overlap, one after another when they do. The moving part is tinted orange.
Three steps, as before: render (Blender, Workbench, the CAD from redesign/blender/blender_backend.py: the same bodies
as the GLB and the collision check), overlay (Pillow: stage title, the BUILD-GUIDE step and the current action, the
stage progress bar), encode (Blender FFmpeg): build/k09l-build.mp4, build/stage-NN.mp4, build/stage-NN.png (each
stage's last frame). Blender path: --blender or $BLENDER.
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
BL = os.path.join(REDESIGN, 'blender')
BLENDER_DEFAULT = r'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe'
OUT = os.path.join(HERE, 'build')
PLAN = os.path.join(OUT, 'assembly_plan.json')
if HERE not in sys.path:
    sys.path.insert(0, HERE)

FPS = 30
W, H = 1280, 720
T_MOVE, T_HOLD = 0.8, 1.0            # s: camera move at the start of a stage, hold at its end
T_GAP, T_STEP = 0.05, 0.45           # s: between two actions; camera move at a new BUILD-GUIDE step
DUR = {'built': 0.45, 'hinge': 1.5, 'fixture': 0.9, 'slide': 0.7, 'screw': 0.95, 'install': 1.3, 'lay': 0.9,
       'fill': 0.5, 'wire': 0.8, 'swing': 1.6}   # 'built': per piece
DUR_SKIN = 2.6                       # s: the wing skin (three strips, each wiped along the span)
SPIN_TURNS, THREAD_MM = 3.0, 6.0     # as assembly_check.py
HI_COL = (0.95, 0.42, 0.08, 1.0)

# (stage, title, camera azimuth deg, elevation deg): one clip per stage, the titles the build guide links
STAGES = [
    (2, 'Wing core and spar', -55, 32),
    (3, 'Elevon panels', -130, 35),
    (4, 'Fins on the motor tubes', -35, 22),
    (5, 'Pod and power stack', -60, 48),
    (6, 'Harness, then skin', -40, 40),
    (7, 'Servos, linkage and horns', 150, -35),
    (8, 'Motor mounts, motors and props', -25, 18),
    (9, 'Avionics', -70, 52),
    (10, 'Feet and corner caps', -20, 15),
    (11, 'Pack in, weigh and balance', -50, 30),
]


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def load_plan():
    if not os.path.exists(PLAN):
        sys.exit('render_build: %s missing: run python -I redesign/showcase/animation/assembly_check.py first'
                 % os.path.relpath(PLAN, os.getcwd()))
    with open(PLAN, encoding='utf-8') as f:
        return json.load(f)


# =====================================================================================================================
# timeline (shared by the Blender render and the Pillow overlay)
# =====================================================================================================================
def _base(i):
    return '-'.join(i.split('-')[:2])


def _swept_box(a):
    if not a.get('box_mm'):
        return None
    lo, hi = a['box_mm']
    B = a.get('bench_mm') if a['type'] == 'bench' else None
    pts = [p for p in (a.get('path') or [[0, 0, 0]])]
    lo2 = [min(lo[i] + p[i] for p in pts) + (B[i] if B else 0) for i in range(3)]
    hi2 = [max(hi[i] + p[i] for p in pts) + (B[i] if B else 0) for i in range(3)]
    return lo2, hi2


def _overlap(a, b):
    return a and b and all(a[0][i] < b[1][i] and b[0][i] < a[1][i] for i in range(3))


def build_ops(plan):
    """Consecutive actions of one step, type, kind and part number become one op (moved together); split into
    sequential ops where their swept boxes overlap."""
    ops = []
    for a in plan['actions']:
        key = (a['step'], a['type'], a.get('kind'), 'wire' if a['type'] == 'wire' else
               (a['id'].split('-')[0] if a['type'] == 'install' else _base(a['id'])))
        if ops and ops[-1]['key'] == key:
            ops[-1]['items'].append(a)
        else:
            ops.append({'key': key, 'stage': a['stage'], 'step': a['step'], 'caption': a['caption'],
                        'type': a['type'], 'kind': a.get('kind'), 'items': [a]})
    out = []
    for op in ops:
        subs = []
        for a in op['items']:
            box = _swept_box(a)
            for s in subs:
                if not any(_overlap(box, b) for b in s['boxes']):
                    s['items'].append(a)
                    s['boxes'].append(box)
                    break
            else:
                subs.append({'items': [a], 'boxes': [box]})
        for s in subs:
            out.append(dict(op, items=s['items']))
    return out


def op_duration(op):
    if op['kind'] == 'lay' and any(a['id'] == 'WNG-003' for a in op['items']):
        return DUR_SKIN
    n = max(len(a.get('clusters') or []) for a in op['items'])
    if op['kind'] == 'screw' and n > 1:                # a screw set: driven one screw after another
        return min(0.55 * n, 2.4)
    if op['kind'] == 'built':                          # glued up piece by piece
        return DUR['built'] * max(len(a.get('built') or [1]) for a in op['items'])
    return DUR.get(op['kind'], 0.9)


def timeline(plan):
    """(stages: [(stage index, f0, f_cam_done, f_end)], ops with f0 / f1, total frames)."""
    ops = build_ops(plan)
    stages, f = [], 0
    for si, st in enumerate(STAGES):
        mine = [o for o in ops if o['stage'] == st[0]]
        a = f
        f += int(T_MOVE * FPS)
        b = f
        step = None
        for o in mine:
            if step is not None and o['step'] != step:
                f += int(T_STEP * FPS)
            step = o['step']
            o['f0'] = f
            f += int(op_duration(o) * FPS)
            o['f1'] = f
            f += int(T_GAP * FPS)
        f += int(T_HOLD * FPS)
        stages.append((si, a, b, f))
    return stages, ops, f


def stage_at(stages, f):
    for si, a, b, e in stages:
        if a <= f < e:
            return si
    return len(stages) - 1


# =====================================================================================================================
# captions
# =====================================================================================================================
def _arrive_words(path):
    if not path or len(path) < 2:
        return ''
    a, b = path[-2], path[-1]
    v = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(v[i]))
    return {(0, 1): 'aft', (0, -1): 'forward', (1, 1): 'to the right', (1, -1): 'to the left', (2, 1): 'upward',
            (2, -1): 'downward'}[(k, 1 if v[k] > 0 else -1)]


def op_label(op, names):
    it = op['items']
    ids = [a['id'] for a in it]
    n = len(ids)
    if op['type'] == 'swing':
        return 'Elevon panels swung full TE-up about the hinge line and back (lower strip laid TE-up)'
    if op['type'] == 'wire' and any(a.get('tail_action') for a in op['items']):
        ids = [w for a in op['items'] for w in a.get('members') or []]
        return ('%s: held run laid on into %s connector now its end part is on'
                % (', '.join(ids) if len(ids) <= 4 else '%s ... %s (%d leads)' % (ids[0], ids[-1], len(ids)),
                   'its' if len(ids) == 1 else 'their'))
    if op['type'] == 'wire':
        return ('%s laid along %s route%s, then soldered / plugged at both ends'
                % (', '.join(ids) if n <= 4 else '%s ... %s (%d leads)' % (ids[0], ids[-1], n),
                   'its' if n == 1 else 'their', '' if n == 1 else 's'))
    a0 = it[0]
    if op['type'] == 'install':
        grp = a0['id'].split('-')[0]
        head = 'Bench sub-assembly "%s"%s (%d parts: %s)' % (grp, ' x%d' % n if n > 1 else '', len(a0['members']),
                                                            ', '.join(a0['members'][:3]) +
                                                            (' ...' if len(a0['members']) > 3 else ''))
    else:
        nm = names.get(a0['id'], a0['id'])
        nm = nm.split(':')[0].split(',')[0].split('(')[0].strip()
        for sfx in (' UR', ' UL', ' LR', ' LL', ' L', ' R', ' left', ' right'):
            if nm.endswith(sfx):
                nm = nm[:-len(sfx)]
        head = '%s%s %s' % (_base(a0['id']) if n > 1 else a0['id'], ' x%d' % n if n > 1 else '', nm[:44])
    k = op['kind']
    words = _arrive_words(a0.get('path'))
    segs = len(a0.get('path') or []) - 1
    if k == 'fixture':
        tail = 'cut in place in the %s' % a0['fixture'] if a0.get('fixture') else 'cut free in place'
    elif k == 'lay':
        tail = 'laid in place onto what it covers'
    elif k == 'fill':
        tail = 'wet epoxy applied in place'
    elif k == 'built':
        tail = 'glued up piece by piece (%d pieces, each on its own path)' % len(a0.get('built') or [])
    elif k == 'hinge':
        tail = 'tongue slid under the lip, then turned %g deg down about the lip edge' % (a0.get('open_deg') or 0)
    elif k == 'screw':
        tail = ('driven %s along its axis, turning' % words) if len(a0.get('clusters') or []) < 2 else             ('%d screws driven one by one along their axes, turning' % len(a0['clusters']))
    elif k == 'install':
        tail = 'moved on as one piece, %s' % words + (' (out, then across)' if segs >= 2 else '')
    else:
        tail = ('slid %s into its seat' % words) + (' (brought in, then across)' if segs >= 2 else '')
    if any(a.get('elastic') for a in it):
        e = max((x for a in it for x in a['elastic']), key=lambda x: x['strain_pct'])
        tail += ' (snap fingers flex %.2f mm, %.1f %% strain)' % (e['deflection_mm'], e['strain_pct'])
    pre = 'Bench: ' if op['type'] == 'bench' else ''
    s = '%s%s: %s' % (pre, head, tail)
    return s if len(s) <= 118 else s[:115] + '...'


# =====================================================================================================================
# render (inside Blender)
# =====================================================================================================================
def blender_render(argv):
    import argparse
    import bmesh
    import bpy
    from mathutils import Matrix, Vector
    sys.path[:0] = [BL, os.path.join(REDESIGN, 'fusion')]
    import blender_backend as bb
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='')
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--pct', type=int, default=100)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    plan = load_plan()
    stages, ops, NF = timeline(plan)
    be, ctx, graph, results = bb.build(False, None, 'material', log=lambda *x: None)
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_WORKBENCH'
    sh = scn.display.shading
    sh.light, sh.color_type = 'STUDIO', 'OBJECT'
    sh.show_cavity, sh.cavity_type = True, 'BOTH'
    sh.show_object_outline, sh.object_outline_color = True, (0.12, 0.14, 0.16)
    sh.background_type, sh.background_color = 'VIEWPORT', (0.93, 0.94, 0.95)
    scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = W, H, a.pct
    scn.render.film_transparent = False
    scn.view_settings.view_transform = 'Standard'
    scn.render.image_settings.file_format = 'PNG'
    for o in bpy.data.objects:
        if o.type == 'EMPTY':
            o.hide_render = True
    for ob in be.wires.values():
        ob.hide_render = True                         # re-drawn below as curves that can be laid end to end

    def base_colour(ob):
        m = ob.data.materials[0] if ob.data and getattr(ob.data, 'materials', None) else None
        return tuple(m.diffuse_color) if m is not None else (0.8, 0.8, 0.82, 1.0)

    def sub_object(ob, faces_idx, tag):
        """New object from a subset of ob's faces (same transform, material)."""
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.faces.ensure_lookup_table()
        keep = set(faces_idx)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context='FACES')
        me = bpy.data.meshes.new(ob.name + tag)
        bm.to_mesh(me)
        bm.free()
        for m in ob.data.materials:
            me.materials.append(m)
        o = bpy.data.objects.new(ob.name + tag, me)
        for c in ob.users_collection:
            c.objects.link(o)
        o.matrix_world = ob.matrix_world.copy()
        return o

    def split_loose(ob):
        """Connected pieces of a mesh (one per screw of a set)."""
        me = ob.data
        nb = {i: set() for i in range(len(me.vertices))}
        for e in me.edges:
            u, v = e.vertices
            nb[u].add(v)
            nb[v].add(u)
        comp, cid = {}, 0
        for s in range(len(me.vertices)):
            if s in comp:
                continue
            st = [s]
            comp[s] = cid
            while st:
                x = st.pop()
                for y in nb[x]:
                    if y not in comp:
                        comp[y] = cid
                        st.append(y)
            cid += 1
        if cid <= 1:
            return [ob]
        faces = {}
        for p in me.polygons:
            faces.setdefault(comp[p.vertices[0]], []).append(p.index)
        return [sub_object(ob, fl, '.%d' % k) for k, fl in sorted(faces.items())]

    def split_lay(ob, by_normal=True):
        """An item laid, wet or cut in place, as slices that appear one after another where they lie (a wipe; no
        slice moves). Tape in laying order: faces facing down (lower skin), up (upper skin), then the rest (LE strip,
        edges); each wiped along its longest extent in 8 slices (1 for small items). by_normal False (a hot-wired core,
        panels, an epoxy bead): one group, wiped along its longest extent."""
        me = ob.data
        Mw = ob.matrix_world
        R = Mw.to_3x3()
        cs = [Mw @ p.center for p in me.polygons]
        lo = [min(c[i] for c in cs) for i in range(3)]
        hi = [max(c[i] for c in cs) for i in range(3)]
        ax = max(range(3), key=lambda i: hi[i] - lo[i])
        nsl = 8 if hi[ax] - lo[ax] > 0.3 else 1
        groups = {}
        for p, c in zip(me.polygons, cs):
            nz = (R @ p.normal).normalized().z
            g = (0 if nz < -0.3 else (1 if nz > 0.3 else 2)) if by_normal else 0
            k = min(nsl - 1, int((c[ax] - lo[ax]) / max(hi[ax] - lo[ax], 1e-9) * nsl))
            groups.setdefault((g, k), []).append(p.index)
        out = []
        for (g, k), fl in sorted(groups.items()):
            o = sub_object(ob, fl, '.strip%d%d' % (g, k))
            out.append((o, Vector()))                 # appears in place: no approach motion
        return out

    def split_bodies(ob, built):
        """A part glued up from pieces: its faces grouped by the checked CAD body they belong to (the smallest body box,
        grown 0.3 mm, that holds the face centre; else the nearest box), in the order the check placed them."""
        me = ob.data
        Mw = ob.matrix_world
        boxes = [(q['idx'], Vector(q['box_mm'][0]) / 1000.0, Vector(q['box_mm'][1]) / 1000.0) for q in built]
        g = 0.0003
        faces = {}
        for pl in me.polygons:
            c = Mw @ pl.center
            inside = [(math.prod(hi[i] - lo[i] + 2 * g for i in range(3)), idx) for idx, lo, hi in boxes
                      if all(lo[i] - g <= c[i] <= hi[i] + g for i in range(3))]
            if inside:
                idx = min(inside)[1]
            else:
                idx = min(boxes, key=lambda b: sum(max(b[1][i] - c[i], 0, c[i] - b[2][i]) ** 2 for i in range(3)))[0]
            faces.setdefault(idx, []).append(pl.index)
        return [(sub_object(ob, faces[q['idx']], '.piece%d' % q['idx']), q['idx']) for q in built if q['idx'] in faces]

    def split_side(ob, axis, origin, ref):
        """Faces of ob on the side of the hinge line (axis through origin) where point ref lies, and the rest."""
        me = ob.data
        Mw = ob.matrix_world

        def perp(v):
            d = v - origin
            return d - axis * d.dot(axis)
        r_ = perp(ref)
        a_, b_ = [], []
        for pl in me.polygons:
            (a_ if perp(Mw @ pl.center).dot(r_) > 0 else b_).append(pl.index)
        return (sub_object(ob, a_, '.panel') if a_ else None), (sub_object(ob, b_, '.core') if b_ else None)

    # ------------------------------------------------------------- objects and their schedules
    sched = {}                                         # object -> list of events
    finals, colours, spin_c = {}, {}, {}
    managed = []
    names = {}

    def reg(o):
        if o not in finals:
            finals[o] = o.matrix_world.copy()
            colours[o] = base_colour(o)
            managed.append(o)
            sched[o] = []

    def mm(p):
        return Vector(p) / 1000.0

    pieces = {}                                        # part id -> render objects (pieces for screws, strips for tape)
    act_of = {}
    for op in ops:
        for it in op['items']:
            act_of.setdefault(it['id'], []).append((op, it))
    for pid, ob in be.objects.items():
        c = ctx.components.get(pid)
        if be.is_proxy(pid) or (c is not None and not c.flight) or pid not in act_of:
            ob.hide_render = True
            continue
        kinds = {it.get('kind') for _op, it in act_of[pid]}
        if 'screw' in kinds:
            ps = split_loose(ob)
            if ps != [ob]:
                ob.hide_render = True
            pieces[pid] = [(p, Vector()) for p in ps]
        elif kinds & {'lay', 'fill', 'fixture'}:
            ob.hide_render = True
            pieces[pid] = split_lay(ob, by_normal='lay' in kinds)
        elif 'built' in kinds:
            ob.hide_render = True
            built = next(it['built'] for _op, it in act_of[pid] if it.get('built'))
            pieces[pid] = split_bodies(ob, built)
        else:
            pieces[pid] = [(ob, Vector())]
        for p, _d in pieces[pid]:
            reg(p)
            if 'screw' in kinds:
                vs = [p.matrix_world @ v.co for v in p.data.vertices]
                spin_c[p] = sum(vs, Vector()) / max(len(vs), 1)

    # wires as curves, laid end to end by the bevel end factor
    wire_obs = {}
    for op in ops:                                     # held runs laid later: also keyed by each member wire
        for it in op['items']:
            if it.get('tail_action'):
                for m in it.get('members') or []:
                    act_of.setdefault(m, []).append((op, it))
    for w in ctx.wires:
        if w.edge not in act_of:
            continue
        e = graph.edges.get(w.edge, {})
        block = e.get('wire', {}) if isinstance(e.get('wire'), dict) else {}
        bend = block.get('bend_radius_mm', 5 * w.dia * 1000) / 1000.0
        cu = bpy.data.curves.new(w.edge + ' lay', 'CURVE')
        cu.dimensions, cu.bevel_depth, cu.bevel_resolution, cu.use_fill_caps = '3D', 1.0, 3, True
        cu.bevel_factor_mapping_end = 'SPLINE'
        for line, dia in (w.strands or [(w.points, w.dia)]):
            pts = bb.fillet_polyline(line, bend)
            sp = cu.splines.new('POLY')
            sp.points.add(len(pts) - 1)
            for p, q in zip(sp.points, pts):
                p.co = (q.x, q.y, q.z, 1.0)
                p.radius = dia / 2
        cu.materials.append(bb.wire_material(block, w.dia))
        o = bpy.data.objects.new(w.edge + ' lay', cu)
        scn.collection.objects.link(o)
        wire_obs[w.edge] = o
        reg(o)

    # events
    for op in ops:
        for it in op['items']:
            k, pid = it.get('kind'), it['id']
            if op['type'] == 'swing':
                for m, sw in (it.get('swing') or {}).items():
                    for p, _d in pieces.get(m, []):
                        sched[p].append(('swing', op['f0'], op['f1'], Vector(sw['axis']), mm(sw['origin_mm']),
                                         sw['deg']))
                # the hinge tape: the half bonded to a panel turns with it (as checked: tape_split)
                for tp in (it.get('tape_split') or {}):
                    new = []
                    for p, d in pieces.get(tp, []):
                        lo_ = [min((p.matrix_world @ Vector(c))[i] for c in p.bound_box) for i in range(3)]
                        hi_ = [max((p.matrix_world @ Vector(c))[i] for c in p.bound_box) for i in range(3)]

                        def y_ov(m):
                            ys = [(o.matrix_world @ Vector(c)).y for o, _d in pieces.get(m, []) for c in o.bound_box]
                            return min(hi_[1], max(ys)) - max(lo_[1], min(ys)) if ys else -1e9
                        pans = [m for m in it['swing'] if m.startswith(('WNG-011', 'WNG-012'))]
                        if not pans:
                            new.append((p, d))
                            continue
                        pan = max(pans, key=y_ov)
                        sw = it['swing'][pan]
                        ref = sum((o.matrix_world @ Vector(c) for o, _d in pieces[pan] for c in o.bound_box),
                                  Vector()) / (8 * len(pieces[pan]))
                        a_, b_ = split_side(p, Vector(sw['axis']), mm(sw['origin_mm']), ref)
                        for q in (a_, b_):
                            if q is None:
                                continue
                            reg(q)
                            sched[q] = list(sched[p])
                            new.append((q, d))
                        if a_ is not None:
                            sched[a_].append(('swing', op['f0'], op['f1'], Vector(sw['axis']), mm(sw['origin_mm']),
                                              sw['deg']))
                        p.hide_render = True
                        managed.remove(p)
                    pieces[tp] = new
                continue
            if op['type'] == 'wire':
                if it.get('tail_action'):
                    for m, sp in (it.get('tails') or {}).items():
                        if m in wire_obs:
                            sched[wire_obs[m]].append(('wire', op['f0'], op['f1'], sp['from'], sp['to']))
                elif pid in wire_obs:
                    sp = it.get('span') or [0.0, 1.0]
                    sched[wire_obs[pid]].append(('wire', op['f0'], op['f1'], [sp[0], sp[0]], sp))
                continue
            path = [mm(p) for p in (it.get('path') or [[0, 0, 0]])]
            if op['type'] == 'install':
                for m in it['members']:
                    for p, _d in pieces.get(m, []):
                        sched[p].append(('install', op['f0'], op['f1'], path))
                continue
            bench = mm(it['bench_mm']) if op['type'] == 'bench' and it.get('bench_mm') else Vector()
            ps = pieces.get(pid, [])
            for j, (p, drop) in enumerate(ps):
                if k in ('lay', 'fill', 'fixture'):     # wiped on in place, slice after slice
                    n = len(ps)
                    t0 = op['f0'] + (op['f1'] - op['f0']) * 0.85 * j / max(n, 1)
                    sched[p].append(('place', t0, t0, [Vector()], bench, None, op['f1'], None, None))
                elif k == 'built':                      # each glued piece on its own checked path, in order
                    bl = it.get('built') or []
                    n = len(bl)
                    jj = next((i for i, q in enumerate(bl) if q['idx'] == drop), 0)
                    t0 = op['f0'] + (op['f1'] - op['f0']) * jj / max(n, 1)
                    t1 = op['f0'] + (op['f1'] - op['f0']) * (jj + 1) / max(n, 1)
                    sched[p].append(('place', t0, t1, [mm(q) for q in bl[jj]['path']], bench, None, op['f1'],
                                     None, None))
                elif it.get('keys'):                    # keyframed: translation + hinge angle, as swept
                    rot = (Vector(it['rot']['axis']), mm(it['rot']['origin_mm']))
                    keys = [(mm(t), a_) for t, a_ in it['keys']]
                    sched[p].append(('place', op['f0'], op['f1'], [keys[0][0], Vector()], bench, None, op['f1'],
                                     keys, rot))
                elif k == 'screw' and it.get('clusters') and p in spin_c:
                    cl = it['clusters']
                    ax = Vector(it['spin']['axis']) if it.get('spin') else Vector((0, 0, 1))

                    def off_axis(c, q=p):
                        d = spin_c[q] - mm(c['centre_mm'])
                        return (d - ax * d.dot(ax)).length
                    ci = min(range(len(cl)), key=lambda i: off_axis(cl[i]))
                    n = len(cl)
                    t0 = op['f0'] + (op['f1'] - op['f0']) * ci / n
                    t1 = op['f0'] + (op['f1'] - op['f0']) * (ci + 1) / n
                    sched[p].append(('place', t0, t1, [mm(q) for q in cl[ci]['path']], bench, ax, op['f1'],
                                     None, None))
                else:
                    spin = Vector(it['spin']['axis']) if (k == 'screw' and it.get('spin')) else None
                    sched[p].append(('place', op['f0'], op['f1'], path, bench, spin, op['f1'], None, None))

    def path_at(path, u):
        """Point at fraction u of the path's length (start -> final), and the length still to go (m)."""
        if len(path) == 1:
            return path[0].copy(), 0.0
        segs = [(path[i], path[i + 1], (path[i + 1] - path[i]).length) for i in range(len(path) - 1)]
        L = sum(s[2] for s in segs) or 1e-9
        d = u * L
        for p0, p1, l in segs:
            if d <= l or (p0, p1, l) == segs[-1]:
                return p0.lerp(p1, min(1.0, d / l) if l > 0 else 1.0), L - u * L
            d -= l
        return path[-1].copy(), 0.0

    def rot_about(axis, origin, deg):
        return Matrix.Translation(origin) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-origin)

    def keys_at(keys, u):
        """Translation (m) and hinge angle at fraction u of a keyframed motion (assembly_check.sweep_keys: linear
        between keys), u measured along translation mm + angle deg."""
        w = [(keys[i + 1][0] - keys[i][0]).length * 1000.0 + abs(keys[i + 1][1] - keys[i][1])
             for i in range(len(keys) - 1)]
        d = u * (sum(w) or 1e-9)
        for i, wi in enumerate(w):
            if d <= wi or i == len(w) - 1:
                f = min(1.0, d / wi) if wi > 0 else 1.0
                return keys[i][0].lerp(keys[i + 1][0], f), keys[i][1] + (keys[i + 1][1] - keys[i][1]) * f
            d -= wi
        return keys[-1][0], keys[-1][1]

    # cameras: per stage, framed on what the stage places (final pose and bench pose)
    def bbox(obs_offs):
        pts = [off + o.matrix_world @ Vector(c) for o, off in obs_offs for c in o.bound_box]
        if not pts:
            return Vector((0.05, 0, 0)), 0.5
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        return (lo + hi) / 2, max((hi - lo).length, 0.12)

    allp = [(o, Vector()) for o in managed]
    centre_all, _ = bbox(allp)

    def frame_cam(objs, az_deg, el_deg, whole=False):
        c, size = bbox(objs) if objs else (centre_all, 0.6)
        if whole:
            c, size = centre_all, 1.2
        size = min(max(size, 0.30), 1.35)
        az, el = math.radians(az_deg), math.radians(el_deg)
        d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        return c, c + d * (size * 1.25 + 0.12)

    # one camera per BUILD-GUIDE step: framed on what the step places (final and bench pose), looking from the side
    # the parts come in from (a sub-assembly pushed up from below is filmed from below)
    cams = []                                          # (frame the move starts, frame it ends, target, location)
    steps = []
    for op in ops:
        if not steps or steps[-1]['step'] != op['step']:
            steps.append({'step': op['step'], 'stage': op['stage'], 'ops': []})
        steps[-1]['ops'].append(op)
    for si, st in enumerate(STAGES):
        mine = [x for x in steps if x['stage'] == st[0]]
        _s, fa, fb, fe = stages[si]
        for j, x in enumerate(mine):
            obs, zs = [], []
            for op in x['ops']:
                for it in op['items']:
                    for m in (it.get('members') or [it['id']]):
                        for p, _d in pieces.get(m, []):
                            obs.append((p, Vector()))
                            if op['type'] == 'bench' and it.get('bench_mm'):
                                obs.append((p, mm(it['bench_mm'])))
                    if it['id'] in wire_obs:
                        obs.append((wire_obs[it['id']], Vector()))
                    if op['kind'] in ('slide', 'screw', 'install', 'hinge') and it.get('path'):
                        zs.append(it['path'][0][2] + ((it.get('bench_mm') or [0, 0, 0])[2]
                                                      if op['type'] == 'bench' else 0))
            el = st[3]
            zm = sum(zs) / len(zs) if zs else 0.0
            if zm < -15 and el > 0 or zm > 15 and el < 0:
                el = -el
            tgt, loc = frame_cam(obs, st[2], el)
            f_end = x['ops'][0]['f0']
            f_beg = fa if j == 0 else f_end - int(T_STEP * FPS)
            cams.append((f_beg, max(f_end, f_beg + 1), tgt, loc))
        if not mine:
            tgt, loc = frame_cam([], st[2], st[3], whole=True)
            cams.append((fa, fb, tgt, loc))
    fin_t, fin_l = frame_cam([], STAGES[-1][2], STAGES[-1][3], whole=True)

    def cam_at(f):
        k = max([i for i, c in enumerate(cams) if c[0] <= f] or [0])
        f0, f1, t1, l1 = cams[k]
        t0_, l0_ = (cams[k - 1][2], cams[k - 1][3]) if k > 0 else (t1, l1)
        u = smooth((f - f0) / max(f1 - f0, 1)) if k > 0 else 1.0
        return t0_.lerp(t1, u), l0_.lerp(l1, u)

    frames = [int(x) for x in a.frames.split(',')] if a.frames else list(range(0, NF, a.every))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.lens, cam.data.clip_start, cam.data.clip_end = 42, 0.005, 20
    t0 = time.time()
    for f in frames:
        si_now = stage_at(stages, f)
        _, fa, fb, fe = stages[si_now]
        tgt, loc = cam_at(f)
        last_op_end = max([o['f1'] for o in ops if o['stage'] == STAGES[-1][0]] or [fb])
        if si_now == len(STAGES) - 1 and f >= last_op_end:   # the end: ease out to the whole aircraft and orbit
            u = smooth((f - last_op_end) / (0.8 * FPS))
            tgt, loc = tgt.lerp(fin_t, u), loc.lerp(fin_l, u)
            ang = 0.5 * smooth((f - last_op_end) / max(fe - last_op_end, 1))
            off = loc - tgt
            loc = tgt + Vector((off.x * math.cos(ang) - off.y * math.sin(ang),
                                off.x * math.sin(ang) + off.y * math.cos(ang), off.z))
        cam.location = loc
        cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
        for o in managed:
            ev = sched[o]
            base = colours[o]
            tint = 0.0
            if o.type == 'CURVE':
                past = [e for e in ev if e[0] == 'wire' and e[1] <= f]
                if not past:
                    o.hide_render = True
                    continue
                w = past[-1]
                o.hide_render = False
                p = smooth((f - w[1]) / max(w[2] - w[1], 1))
                a0, b0 = w[3]
                a1, b1 = w[4]
                o.data.bevel_factor_start = a0 + (a1 - a0) * p
                o.data.bevel_factor_end = max(o.data.bevel_factor_start + 0.002, b0 + (b1 - b0) * p)
                tint = 1 - smooth((f - w[2]) / (0.8 * FPS))
                o.color = tuple(base[i] * (1 - 0.75 * tint) + HI_COL[i] * 0.75 * tint for i in range(4))
                continue
            pl = next((e for e in ev if e[0] == 'place'), None)
            if pl is None or f < pl[1]:
                o.hide_render = True
                continue
            o.hide_render = False
            _k, f0, f1, path, bench, spin, f_end, keys, rot = pl
            M = Matrix.Identity(4)
            if f < f1 and keys:
                t_, a_ = keys_at(keys, smooth((f - f0) / max(f1 - f0, 1)))
                off = t_ + bench
                M = rot_about(rot[0], rot[1], a_)
                tint = 1.0
            elif f < f1:
                pr = smooth((f - f0) / max(f1 - f0, 1))
                off, togo = path_at(path, pr)
                off = off + bench
                if spin is not None and o in spin_c:
                    ang = 360.0 * SPIN_TURNS * min(1.0, togo * 1000.0 / THREAD_MM)
                    M = rot_about(spin, spin_c[o], ang)
                tint = 1.0
            else:
                off = bench.copy()
                tint = 1 - smooth((f - f_end) / (0.8 * FPS))
            ins = next((e for e in ev if e[0] == 'install'), None)
            if ins is not None and f >= ins[1]:
                if f < ins[2]:
                    off, _t = path_at(ins[3], smooth((f - ins[1]) / max(ins[2] - ins[1], 1)))
                    tint = 1.0
                else:
                    off = Vector()
                    tint = max(tint, 1 - smooth((f - ins[2]) / (0.8 * FPS)))
            for e in ev:
                if e[0] == 'swing' and e[1] <= f < e[2]:
                    s = math.sin(math.pi * smooth((f - e[1]) / max(e[2] - e[1], 1)))
                    M = rot_about(e[3], e[4], e[5] * s) @ M
                    tint = max(tint, 0.6)
            o.matrix_world = Matrix.Translation(off) @ M @ finals[o]
            o.color = tuple(base[i] * (1 - 0.75 * tint) + HI_COL[i] * 0.75 * tint for i in range(4))
        scn.render.filepath = os.path.join(a.out, 'raw_%04d.png' % f)
        bpy.ops.render.render(write_still=True)
        if f % 60 == 0:
            print('FRAME %d / %d  %.0f s' % (f, NF, time.time() - t0), flush=True)
    print('RENDER_TOTAL %.0f s' % (time.time() - t0))


def blender_encode(argv):
    import argparse
    import bpy
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--first', type=int, default=0)
    ap.add_argument('--last', type=int, default=10 ** 9)
    ap.add_argument('--kbps', type=int, default=2500)
    ap.add_argument('--fps', type=int, default=FPS)
    a = ap.parse_args(argv)
    names = sorted(n for n in os.listdir(a.src) if n.startswith('lab_') and n.endswith('.png')
                   and a.first <= int(n[4:8]) <= a.last)
    sc = bpy.context.scene
    sc.sequence_editor_create()
    st = sc.sequence_editor.sequences.new_image('frames', os.path.join(a.src, names[0]), 1, 1)
    for n in names[1:]:
        st.elements.append(n)
    sc.frame_start, sc.frame_end = 1, len(names)
    sc.render.fps = a.fps
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'FFMPEG'
    ff = sc.render.ffmpeg
    ff.format, ff.codec, ff.constant_rate_factor = 'MPEG4', 'H264', 'NONE'
    ff.video_bitrate, ff.maxrate, ff.buffersize, ff.gopsize = a.kbps, int(a.kbps * 1.5), 2000, a.fps
    ff.ffmpeg_preset, ff.audio_codec = 'GOOD', 'NONE'
    sc.render.filepath = a.out
    sc.render.use_file_extension = False
    bpy.ops.render.render(animation=True)
    print('ENCODED', a.out)


# =====================================================================================================================
# overlay (system Python + Pillow)
# =====================================================================================================================
def _font(names, size):
    from PIL import ImageFont
    dirs = [os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')]
    for n in names:
        for d in dirs:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def current_op(ops, si, f):
    mine = [o for o in ops if o['stage'] == STAGES[si][0]]
    cur = None
    for o in mine:
        if o['f0'] <= f:
            cur = o
    return cur or (mine[0] if mine else None)


def overlay(src_png, dst_png, f, stages, ops, names):
    from PIL import Image, ImageDraw
    im = Image.open(src_png).convert('RGBA')
    if im.size != (W, H):
        im = im.resize((W, H))
    # Workbench writes the background as alpha 0; put it on the light grey the scene asks for (0.93-0.95), not the
    # black an RGB save of a transparent pixel gives
    bg = Image.new('RGBA', im.size, (237, 240, 242, 255))
    im = Image.alpha_composite(bg, im)
    i = stage_at(stages, f)
    num, title = STAGES[i][0], STAGES[i][1]
    op = current_op(ops, i, f)
    lines = [('Step %s  ·  %s' % (op['step'], op['caption'])) if op else '', op_label(op, names) if op else '']
    _, fa, fb, fe = stages[i]
    alpha = min(1.0, (f - fa) / 9.0 + 0.15) if i > 0 else 1.0
    ink, hi, muted = (18, 22, 25), (194, 84, 10), (107, 114, 128)
    f_head = _font(['seguisb.ttf', 'segoeui.ttf', 'arial.ttf'], 17)
    f_mono = _font(['CascadiaMono.ttf', 'consola.ttf', 'cour.ttf'], 15)
    f_title = _font(['seguisb.ttf', 'segoeui.ttf', 'arial.ttf'], 30)
    f_line = _font(['segoeui.ttf', 'arial.ttf'], 19)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((36, 26), 'K09-L quad tailsitter', font=f_head, fill=ink + (235,))
    d.text((36, 50), 'BUILD SEQUENCE  ·  BUILD-GUIDE.md', font=f_mono, fill=muted + (235,))
    n = len(STAGES)
    x0, y0, step = W - 36 - (n - 1) * 30, 40, 30
    for k in range(n):
        x = x0 + k * step
        col = hi if k == i else (ink if k < i else (200, 204, 210))
        d.ellipse((x - 6, y0 - 6, x + 6, y0 + 6), fill=col + (255,))
        d.text((x - 7, y0 + 10), str(STAGES[k][0]), font=f_mono, fill=(muted if k != i else hi) + (255,))
    A = int(255 * alpha)
    d.rounded_rectangle((28, H - 150, W - 28, H - 24), radius=10, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(205, 209, 214, A), width=1)
    d.rectangle((28, H - 150, 34, H - 24), fill=hi + (A,))
    d.text((52, H - 140), 'STAGE %d' % num, font=f_mono, fill=hi + (A,))
    d.text((52, H - 118), title, font=f_title, fill=ink + (A,))
    for k, ln in enumerate(lines):
        while ln and d.textlength(ln, font=f_line) > W - 100:
            ln = ln[:-4] + '...'
        d.text((52, H - 80 + 24 * k), ln, font=f_line, fill=(55, 62, 72, A))
    Image.alpha_composite(im, lay).convert('RGB').save(dst_png)


# =====================================================================================================================
# driver (system Python)
# =====================================================================================================================
def run(cmd):
    print('>', ' '.join(cmd[:6]), '...', flush=True)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    for line in p.stdout.splitlines():
        if line.startswith(('FRAME', 'RENDER_TOTAL', 'ENCODED', 'Traceback')) or 'Error' in line:
            print('   ', line, flush=True)
    if p.returncode != 0:
        print(p.stdout[-4000:])
        raise SystemExit('blender failed')


def driver():
    import argparse
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender', default=os.environ.get('BLENDER', BLENDER_DEFAULT))
    ap.add_argument('--frames', default='', help='comma list: test render only')
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'k09l_build'))
    ap.add_argument('--skip-render', action='store_true')
    ap.add_argument('--preview', action='store_true',
                    help='half-size, every 3rd frame, one film in --work (build-preview.mp4); build/ untouched')
    a = ap.parse_args()
    t0 = time.time()
    plan = load_plan()
    stages, ops, NF = timeline(plan)
    import assembly_plan
    names = {k: v.get('name', k) for k, v in assembly_plan.part_info().items()}
    every = 3 if a.preview else 1
    work = os.path.join(a.work, 'preview') if a.preview else a.work
    os.makedirs(work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    me = os.path.abspath(__file__)
    print('%d actions in %d moves, %d frames (%.1f s of film)' % (len(plan['actions']), len(ops), NF, NF / FPS))
    if not a.skip_render:
        if not a.frames:                              # no stale frames from a longer earlier film in the encode
            for n in os.listdir(work):
                if n.startswith(('raw_', 'lab_')) and n.endswith('.png'):
                    os.remove(os.path.join(work, n))
        cmd = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', work,
               '--every', str(every), '--pct', '50' if a.preview else '100']
        if a.frames:
            cmd += ['--frames', a.frames]
        run(cmd)
    frames = [int(x) for x in a.frames.split(',')] if a.frames else list(range(0, NF, every))
    for f in frames:
        overlay(os.path.join(work, 'raw_%04d.png' % f), os.path.join(work, 'lab_%04d.png' % f), f, stages, ops,
                names)
    if a.frames:
        print('test frames in', work)
        return
    if a.preview:
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', work, '--fps', str(FPS // every),
             '--out', os.path.join(work, 'build-preview.mp4')])
        print('preview: %s (%.1f min)' % (os.path.join(work, 'build-preview.mp4'), (time.time() - t0) / 60))
        return
    run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', work, '--kbps', '1800',
         '--out', os.path.join(OUT, 'k09l-build.mp4')])     # 2 min of film: lower rate keeps the repo file ~27 MB
    for si, fa, fb, fe in stages:
        num = STAGES[si][0]
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', work,
             '--out', os.path.join(OUT, 'stage-%02d.mp4' % num), '--first', str(fa), '--last', str(fe - 1)])
        Image.open(os.path.join(work, 'lab_%04d.png' % (fe - 1))).save(os.path.join(OUT, 'stage-%02d.png' % num),
                                                                        optimize=True)
    for n in sorted(os.listdir(OUT)):
        print('%-22s %6.2f MB' % (n, os.path.getsize(os.path.join(OUT, n)) / 1e6))
    print('%d frames, %.1f s of film, total %.1f min' % (NF, NF / FPS, (time.time() - t0) / 60))


if __name__ == '__main__':
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        argv = sys.argv[sys.argv.index('--') + 1:]
        {'render': blender_render, 'encode': blender_encode}[argv[0]](argv[1:])
    else:
        driver()
