"""blender_backend.py - fusionkit backend that builds the aircraft in Blender (bpy), from the SAME build(ctx) modules.

Run inside Blender only (it imports bpy). The scripts in this folder call it for you:
    blender -b --factory-startup -P redesign/blender/export_glb.py -- --examples
    blender -b --factory-startup -P redesign/blender/render_figures.py -- --examples

What it makes (all in the aircraft frame, metres: x aft, y right, z up; Blender world = aircraft frame):
    one mesh object per part      name = part id (e.g. WNG-001); all bodies of a part joined into one mesh;
                                  custom properties: part_id, name, subsystem, material, mass_g, status, make_or_buy,
                                  interfaces (JSON list of edge ids), explode_m (set by explode())
    mass proxies                  (fusionkit Component.proxy: HRN-001 / HRN-002-L/R lumped harness mass) keep their
                                  mesh for bounding boxes (explode, selftest) but are never rendered: custom property
                                  mass_proxy = True, hide_render / hide_viewport, collection "mass proxies"; the GLB
                                  carries them as empties with the part's extras (glb_objects())
    one mesh object per wire      name = edge id (e.g. E-FUS-03); a tube along the routed polyline with its corners
                                  rounded to the edge's bend radius; properties from the edge's "wire" block
    one empty per joint           name = "JOINT E-WNG-04"; properties kind, part_a, part_b, axis, limits
    collections                   one per subsystem ("ex_wing"), plus "wires" and "joints"
Materials: MODE = 'material' (looks like the part's material), 'subsystem' (design-system subsystem colours) or
'status' (design-system status ladder). Colours come from redesign/design-system/tokens.css values copied below.

Shapes (fusionkit.Shape, component-local metres) map to meshes exactly as fusionkit describes them:
    prism   loops on an axis-aligned plane (outer + holes) -> caps by polygon tessellation + side walls
    revolve closed (a, r) profile -> rings of SEG segments; points with r = 0 become one vertex on the axis
    loft    sections on parallel planes -> quads between sections, n-gon end caps; smooth=True refines each loop
            with a Catmull-Rom spline (first -> last point, straight closing line), like the Fusion backend
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True    # do not leave __pycache__ in other agents' folders

import bmesh
from mathutils.bvhtree import BVHTree
import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(HERE)
FUSION = os.path.join(REDESIGN, 'fusion')
for _p in (FUSION, os.path.join(REDESIGN, 'interfaces'), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fusionkit as fk          # noqa: E402

SEG = 48                         # segments around a revolve
SMOOTH_SUB = 3                   # Catmull-Rom points per loft-loop segment when smooth=True
SHARP_DEG = 32                   # edges sharper than this stay sharp (smooth shading elsewhere)


# ----------------------------------------------------------------------------- colours (design-system tokens)
def srgb(hexstr):
    """'#C2540A' -> linear RGB tuple for Blender."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


TOKENS = {
    'highlight': '#C2540A', 'ink': '#121619',
    'stage-top': '#F3F5F8', 'stage-bottom': '#DCE1E8',
    'sub': {'WNG': '#4C8DE0', 'FUS': '#7F8C9E', 'BMS': '#2BA6A0', 'TAL': '#8E6FD8', 'GER': '#B07A3A',
            'PSH': '#D45C8E', 'PWR': '#E0613A', 'HRN': '#D9A91E', 'AVN': '#5DB24D'},
    'status': {'PROPOSED': '#4B5563', 'MODELLED': '#5B3FB5', 'CHECKED': '#0E6F74', 'VERIFIED': '#1A6E3A',
               'UNVERIFIED': '#8A5600'},
}

# material keyword (lower case, first match wins) -> (sRGB hex, roughness, metallic, coat)
LOOKS = [
    (('packing tape', 'bopp'), ('#DCE6F0', 0.12, 0.0, 0.3, 0.22)),   # clear tape skin: the taped-over grooves show
    (('carbon', 'cf '), ('#2A2D31', 0.32, 0.0, 0.5)),
    (('cf tube',), ('#2A2D31', 0.32, 0.0, 0.5)),
    (('foam', 'xps', 'epp', 'eps'), ('#AFBCCB', 0.6, 0.0, 0.0)),
    (('ply', 'birch', 'balsa', 'wood', 'bass'), ('#C9A27A', 0.6, 0.0, 0.0)),
    (('lipo', 'li-ion', 'battery'), ('#2D4E86', 0.45, 0.0, 0.2)),
    (('pcb', 'esc', 'flight controller'), ('#2F6B4A', 0.45, 0.0, 0.1)),
    (('motor',), ('#3C4047', 0.3, 0.8, 0.0)),
    (('servo',), ('#33363B', 0.45, 0.0, 0.0)),
    (('alumin', '6061', '7075'), ('#C8CCD2', 0.3, 1.0, 0.0)),
    (('brass',), ('#C9A44C', 0.3, 1.0, 0.0)),                 # heat-set inserts (C6 FASTENERS-CAD)
    (('steel', 'stainless'), ('#A8ADB4', 0.28, 1.0, 0.0)),
    (('petg', 'pla', 'asa', 'nylon', 'pa6', 'pa12', 'printed', 'tpu'), ('#5F6670', 0.55, 0.0, 0.0)),
]
DEFAULT_LOOK = ('#8A9099', 0.5, 0.0, 0.0)


def _principled(name, rgb, rough=0.5, metal=0.0, coat=0.0, alpha=1.0, emit=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if coat:
        p.inputs['Coat Weight'].default_value = coat
    if emit:
        p.inputs['Emission Color'].default_value = (*rgb, 1.0)
        p.inputs['Emission Strength'].default_value = emit
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'                      # EEVEE / viewport; Cycles uses Alpha directly
        if hasattr(m, 'surface_render_method'):
            m.surface_render_method = 'BLENDED'
    m.diffuse_color = (*rgb, alpha)                   # viewport + glTF fallback colour
    return m


def material_for(info, mode='material'):
    """Blender material for a part dict (interfaces.json) in the given colour mode."""
    pid = info.get('id', '')
    if mode == 'subsystem':
        hexc = TOKENS['sub'].get(pid[:3], DEFAULT_LOOK[0])
        return _principled('sub ' + pid[:3], srgb(hexc), 0.5)
    if mode == 'status':
        st = info.get('status', 'PROPOSED')
        return _principled('status ' + st, srgb(TOKENS['status'].get(st, '#4B5563')), 0.5)
    text = (info.get('material') or '').lower() + ' ' + (info.get('name') or '').lower()
    look = next((lk for keys, lk in LOOKS if any(k in text for k in keys)), DEFAULT_LOOK)
    return _principled('look ' + look[0] + ('' if len(look) < 5 else ' clear'), srgb(look[0]), *look[1:])


def wire_material(wire_block, dia):
    power = (wire_block.get('gauge_awg', 30) <= 18) or dia >= 0.0025
    return _principled('wire power' if power else 'wire signal', srgb('#B42323' if power else TOKENS['sub']['HRN']),
                       0.4, coat=0.2)


# ----------------------------------------------------------------------------- mesh builders (component-local)
def _catmull(pts, sub):
    """Open Catmull-Rom through pts (first..last), `sub` points per segment; returns the refined open polyline."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for s in range(sub):
            t = s / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(2)))
    out.append(tuple(pts[-1]))
    return out


def _resample(loop, n):
    """Closed loop -> n points evenly spaced by arc length (only used when loft sections differ in count)."""
    pts = loop + [loop[0]]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(loop))]
    total = sum(seg)
    out, i, acc = [], 0, 0.0
    for k in range(n):
        target = total * k / n
        while acc + seg[i] < target and i < len(seg) - 1:
            acc += seg[i]
            i += 1
        t = (target - acc) / seg[i] if seg[i] else 0.0
        out.append(tuple(pts[i][j] + t * (pts[i + 1][j] - pts[i][j]) for j in range(2)))
    return out


def add_prism(bm, s):
    loops = [l[:-1] if l[0] == l[-1] else l for l in s.loops]
    bot = [[bm.verts.new(fk.to3d(s.axis, s.offset, uv)) for uv in l] for l in loops]
    top = [[bm.verts.new(fk.to3d(s.axis, s.offset + s.depth, uv)) for uv in l] for l in loops]
    flat_b, flat_t = [v for l in bot for v in l], [v for l in top for v in l]
    for tri in tessellate_polygon([[Vector((u, v, 0)) for u, v in l] for l in loops]):
        bm.faces.new([flat_b[i] for i in tri])
        bm.faces.new([flat_t[i] for i in reversed(tri)])
    for lb, lt in zip(bot, top):
        n = len(lb)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lb[i], lb[j], lt[j], lt[i]))


def add_revolve(bm, s):
    k = fk.AX[s.axis]
    i_ax, j_ax = [q for q in range(3) if q != k]
    prof = s.profile[:-1] if s.profile[0] == s.profile[-1] else list(s.profile)
    rmax = max(r for _, r in prof)
    seg = SEG if rmax > 0.004 else 24
    rings = []
    for a, r in prof:
        if r < 1e-9:
            p = list(s.center)
            p[k] += a
            rings.append([bm.verts.new(p)])
            continue
        ring = []
        for q in range(seg):
            t = 2 * math.pi * q / seg
            p = list(s.center)
            p[k] += a
            p[i_ax] += r * math.cos(t)
            p[j_ax] += r * math.sin(t)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    n = len(rings)
    for e in range(n):
        A, B = rings[e], rings[(e + 1) % n]
        if len(A) == 1 and len(B) == 1:
            continue                                  # an edge along the axis makes no surface
        for q in range(seg):
            q2 = (q + 1) % seg
            if len(A) == 1:
                bm.faces.new((A[0], B[q], B[q2]))
            elif len(B) == 1:
                bm.faces.new((A[q], B[0], A[q2]))
            else:
                bm.faces.new((A[q], B[q], B[q2], A[q2]))


def add_loft(bm, s):
    loops = []
    for _, l in s.sections:
        l = l[:-1] if l[0] == l[-1] else list(l)
        loops.append(_catmull(l, SMOOTH_SUB) if s.smooth else l)
    n = max(len(l) for l in loops)
    loops = [l if len(l) == n else _resample(l, n) for l in loops]
    rings = [[bm.verts.new(fk.to3d(s.axis, o, uv)) for uv in l] for (o, _), l in zip(s.sections, loops)]
    for A, B in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((A[i], A[j], B[j], B[i]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))


BUILDERS = {'prism': add_prism, 'revolve': add_revolve, 'loft': add_loft}


def _matrix(comp):
    return Matrix(comp.matrix())


def _collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def fillet_polyline(points, radius, steps=6):
    """Round every interior corner of a 3-D polyline with (about) `radius`, never eating more than 45 % of a segment.
    A wire is an installation: the drawn bend shows the declared minimum bend radius."""
    P = [Vector(p) for p in points]
    if len(P) < 3 or radius <= 0:
        return P
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        d1, d2 = (b - a), (c - b)
        if d1.length < 1e-9 or d2.length < 1e-9:
            continue
        ang = d1.angle(d2)                            # turning angle
        if ang < 1e-3:
            out.append(b)
            continue
        t = min(radius * math.tan(ang / 2), 0.45 * d1.length, 0.45 * d2.length)
        A, B = b - d1.normalized() * t, b + d2.normalized() * t
        n = max(1, min(steps, int(math.ceil(ang / 0.17))))   # ~10 deg a step: gentle corners stay light (D-87)
        for q in range(n + 1):                        # quadratic Bezier A-b-B: close to the circular arc
            u = q / n
            out.append((1 - u) ** 2 * A + 2 * (1 - u) * u * b + u * u * B)
    out.append(P[-1])
    return out


# ----------------------------------------------------------------------------- the backend
class BlenderBackend(fk.Backend):
    name = 'blender'

    def __init__(self, mode='material', graph=None):
        self.mode = mode
        self.graph = graph            # merge_check.Graph (edges with joint_stack / wire blocks), set by build()
        self.objects = {}             # part id -> object
        self.wires = {}               # edge id -> object
        self.joints = {}              # edge id -> (empty, fusionkit.Joint)
        self.bm = {}                  # part id -> bmesh being filled
        self.cuts = {}                # part id -> [(Shape, 4x4 or None)] material removal, applied in end()
        self.shapes_of = {}           # part id -> [Shape] (rebuilt body by body when the part has cuts)

    # ---- Backend interface
    def begin(self, title):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.name = title[:60]
        bpy.context.scene.unit_settings.system = 'METRIC'

    def component(self, comp):
        me = bpy.data.meshes.new(comp.id)
        ob = bpy.data.objects.new(comp.id, me)
        _collection('mass proxies' if comp.proxy else (comp.subsystem or 'parts')).objects.link(ob)
        ob.matrix_world = _matrix(comp)
        for k, v in (('part_id', comp.id), ('name', comp.name), ('subsystem', comp.subsystem),
                     ('material', comp.material), ('mass_g', comp.mass_g), ('status', comp.status),
                     ('make_or_buy', comp.make_or_buy)):
            if v is not None:
                ob[k] = v
        if comp.proxy:                         # mass-only stand-in: in the roll-up, never drawn (wires show it)
            ob['mass_proxy'] = True
            ob.hide_render = ob.hide_viewport = True
            ob.display_type = 'BOUNDS'
        comp.native = ob
        self.objects[comp.id] = ob
        self.bm[comp.id] = bmesh.new()

    def body(self, comp, shape):
        if shape.kind not in BUILDERS:
            raise ValueError('unknown shape kind ' + shape.kind)
        BUILDERS[shape.kind](self.bm[comp.id], shape)
        self.shapes_of.setdefault(comp.id, []).append(shape)        # kept for per-body cuts in end()

    def cut(self, comp, shape, matrix):
        """Material removal (fusionkit Component.cut / Context.seat): applied in end() as one EXACT difference."""
        self.cuts.setdefault(comp.id, []).append((shape, matrix))

    @staticmethod
    def _world_box(me, M):
        pts = [M @ v.co for v in me.vertices]
        return ([min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)])

    CUT_TOL = 2e-5                                    # m: a result surface deeper than this inside a cutter fails
    CUT_DEEP = 4.5e-5                                 # m: cutter samples this deep must hold no material (the GLB
                                                      # gate fails penetration > 0.05 mm: collide_glb_blender.py)
    SAMPLE_M = 1e-3                                   # m: spacing of the verification samples (GLB gate ~1 mm)
    RAYS = (Vector((1.0, 0.31, 0.17)).normalized(), Vector((-0.23, 1.0, 0.41)).normalized(),
            Vector((0.37, -0.29, 1.0)).normalized(), Vector((-0.71, -0.43, -0.59)).normalized(),
            Vector((0.13, -0.83, -0.47)).normalized())  # skewed: never along a modelled face or edge
    CUT_FAILURES = []                                 # (part, cutter label, (score, samples left)) never verified

    def _apply_cuts(self, pid, ob):
        """D-88: each body is cut by the cutters that reach into it, then the bodies are united into one solid
        (_unite; one boolean over the whole multi-shell part mesh took tens of minutes on the core). Per body: one
        MANIFOLD difference with all its cutters at once (Manifold needs watertight inputs: the builders' seam
        duplicates are welded; a chain of single cuts let one non-manifold EXACT result make every later MANIFOLD
        cut refuse its input), then, only if that does not verify, one cutter at a time. Every result is verified
        (_check) the way the GLB gate sees it: no surface sample of the result deeper than CUT_TOL inside a cutter,
        no material at the cutter's samples CUT_DEEP under its surface. The old check (face centres inside the
        cutter, nearest-normal sign) passed uncut faces bigger than the cutter and failed clean cuts beside a
        cutter cap coplanar with the body's face."""
        cuts = self.cuts.get(pid) or []
        shapes = self.shapes_of.get(pid, [])
        if not shapes or (not cuts and len(shapes) == 1):
            return
        Mo = ob.matrix_world.copy()
        cutters = []
        for k, (s, M) in enumerate(cuts):
            bm = bmesh.new()
            BUILDERS[s.kind](bm, s)
            me = bpy.data.meshes.new('%s cut %d' % (pid, k))
            bm.to_mesh(me)
            bm.free()
            self._weld(me)
            co = bpy.data.objects.new(me.name, me)
            co.matrix_world = Matrix(M) if M is not None else Mo
            bpy.context.scene.collection.objects.link(co)
            co['label'] = s.name or 'cut %d' % k
            cutters.append(self._cutter_data(co))
        bodies = []
        for s in shapes:
            bm = bmesh.new()
            BUILDERS[s.kind](bm, s)
            me = bpy.data.meshes.new(pid + ' body')
            bm.to_mesh(me)
            bm.free()
            self._weld(me)
            near = self._near(me, Mo, cutters)
            if near:
                me = self._cut_body(pid, me, Mo, near)
            bodies.append(me)
        self._unite(pid, ob, bodies, Mo)
        for c in cutters:
            m = c['ob'].data
            bpy.data.objects.remove(c['ob'])
            bpy.data.meshes.remove(m)

    UNION_FAILURES = []                               # parts whose bodies stay separate shells in the GLB

    @staticmethod
    def _volume(me):
        bm = bmesh.new()
        bm.from_mesh(me)
        v = bm.calc_volume(signed=True)
        bm.free()
        return v

    @staticmethod
    def _triangles(me):
        """Store a boolean result as triangles, split here once, so the mesh checked is the mesh exported. Manifold's
        result comes back as n-gons (long faces with vertices along their edges, faces round a slit); split again by
        the glTF writer they gave duplicate triangles that mesh validation dropped: 200+ cracks in the skin and the
        core, and a ray through a crack counts one crossing too few. Where two triangles share all three vertices
        (two united bodies touching face to face: a wall of zero thickness) both go: the pair encloses no volume
        and the shell stays closed."""
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        seen = {}
        for f in bm.faces:
            seen.setdefault(frozenset(v.index for v in f.verts), []).append(f)
        dup = [f for fs in seen.values() if len(fs) > 1 for f in fs]
        if dup:
            bmesh.ops.delete(bm, geom=dup, context='FACES')
        bm.to_mesh(me)
        bm.free()
        me.validate()

    def _unite(self, pid, ob, bodies, Mo):
        """D-88: the part as ONE solid: its (cut) bodies united with MANIFOLD. A GLB node holding a part's bodies as
        separate shells that overlap or abut (core segments, stacked tape layers, a motor's bell over its shaft) has
        no inside / outside a ray can count: crossings of coincident faces are lost or doubled, so the GLB gate read
        points outside a part as deep inside it. The union is checked: watertight (no edge with an odd face count),
        its box the bodies' box, its volume between the largest body's and the bodies' sum; otherwise the bodies are
        joined as before and the part is reported (UNION_FAILURES)."""
        bodies = [m for m in bodies if len(m.polygons)]
        for m in bodies:
            self._triangles(m)
        res = None
        if len(bodies) == 1 and self._tris(bodies[0], Mo)[2]:
            BlenderBackend.UNION_FAILURES.append((pid, 'open'))
            print('UNION NOT CLEAN: %s (1 body, %d open edges)' % (pid, self._tris(bodies[0], Mo)[2]))
        if len(bodies) > 1:
            boxes, vols, closed = [], [], True
            for m in bodies:
                _t, _b, open_e, lo, hi = self._tris(m, Mo)
                closed = closed and open_e == 0
                boxes.append((lo, hi))
                vols.append(abs(self._volume(m)))
            why = None if closed else 'an open body'
            if why is None:
                obs = []
                for m in bodies:
                    o = bpy.data.objects.new(pid + ' part body', m)
                    o.matrix_world = Mo
                    bpy.context.scene.collection.objects.link(o)
                    obs.append(o)
                col = bpy.data.collections.new(pid + ' bodies')
                for o in obs[1:]:
                    col.objects.link(o)
                mod = obs[0].modifiers.new('unite', 'BOOLEAN')
                mod.operation, mod.solver, mod.operand_type, mod.collection = 'UNION', 'MANIFOLD', 'COLLECTION', col
                dg = bpy.context.evaluated_depsgraph_get()
                res = bpy.data.meshes.new_from_object(obs[0].evaluated_get(dg))
                for o in obs:
                    bpy.data.objects.remove(o)
                bpy.data.collections.remove(col)
                self._triangles(res)
                _t, _b, open_e, lo, hi = self._tris(res, Mo) if len(res.polygons) else (0, 0, 1, [0] * 3, [0] * 3)
                v = self._volume(res)
                blo = [min(b[0][i] for b in boxes) for i in range(3)]
                bhi = [max(b[1][i] for b in boxes) for i in range(3)]
                if open_e:
                    why = '%d open edges' % open_e
                elif any(abs(lo[i] - blo[i]) > 1e-6 or abs(hi[i] - bhi[i]) > 1e-6 for i in range(3)):
                    why = 'box changed'
                elif not max(vols) * (1 - 1e-6) <= v <= sum(vols) * (1 + 1e-6):     # (signed: outward winding)
                    why = 'volume %.1f mm3 outside %.1f..%.1f' % (v * 1e9, max(vols) * 1e9, sum(vols) * 1e9)
                if why:
                    bpy.data.meshes.remove(res)
                    res = None
            if why:
                BlenderBackend.UNION_FAILURES.append((pid, why))
                print('UNION NOT CLEAN: %s (%d bodies, %s): bodies kept as separate shells' % (pid, len(bodies), why))
        out = bmesh.new()
        for m in ([res] if res is not None else bodies):
            out.from_mesh(m)
        if res is None:                               # Manifold's winding is right; a recalc across edges where two
            bmesh.ops.recalc_face_normals(out, faces=out.faces)    # solids kiss flipped whole regions of the skin
        out.to_mesh(ob.data)
        out.free()
        for m in bodies + ([res] if res is not None else []):
            bpy.data.meshes.remove(m)

    # ---- cut helpers (world metres)
    @staticmethod
    def _tris(me, M):
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.transform(M)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.normal_update()
        bm.faces.ensure_lookup_table()
        tris = [(tuple(v.co.copy() for v in f.verts), f.normal.copy()) for f in bm.faces]
        bvh = BVHTree.FromBMesh(bm)
        open_e = sum(1 for e in bm.edges if len(e.link_faces) % 2)    # boundary (1) or odd fans: no inside
                                                                      # (4 = two solids kissing on an edge: closed)
        co = [v.co for v in bm.verts]
        lo = [min(c[i] for c in co) for i in range(3)] if co else [0.0] * 3
        hi = [max(c[i] for c in co) for i in range(3)] if co else [0.0] * 3
        bm.free()
        return tris, bvh, open_e, lo, hi

    @classmethod
    def _samples(cls, tri, cap=64):
        """Points spread over a triangle about SAMPLE_M apart (sub-triangle centres: no vertex or edge points)."""
        a, b, c = tri
        n = max(1, min(cap, int(math.ceil(max((b - a).length, (c - b).length, (a - c).length) / cls.SAMPLE_M))))
        u, v = (b - a) / n, (c - a) / n
        pts = []
        for i in range(n):
            for j in range(n - i):
                pts.append(a + u * (i + 1 / 3) + v * (j + 1 / 3))
                if i + j < n - 1:
                    pts.append(a + u * (i + 2 / 3) + v * (j + 2 / 3))
        return pts

    @classmethod
    def _inside(cls, p, bvh):
        """Point inside a closed mesh, the GLB gate's test (collide_glb_blender.depth_inside): outside when the
        nearest-face normal clearly says so ((p - loc).n >= d / 2: away from any edge, where it reads either sign,
        e.g. beside a cutter cap coplanar with the body's face); otherwise ray parity, odd on three of five skewed
        rays (stops once three agree): one ray can be miscounted where it enters a thin wall (0.14 mm tape) within
        1 um of its edge and the next step skips the exit."""
        loc, nrm, _i, dist = bvh.find_nearest(p)
        if loc is None or (p - loc).dot(nrm) >= 0.5 * dist:
            return False
        odd = even = 0
        for d in cls.RAYS:
            n, q = 0, p.copy()
            for _ in range(200):
                hit = bvh.ray_cast(q, d)
                if hit[0] is None:
                    break
                n += 1
                q = hit[0] + d * 1e-6
            if n % 2:
                odd += 1
            else:
                even += 1
            if odd == 3 or even == 3:
                break
        return odd >= 3

    @staticmethod
    def _in_tri(p, t, n):
        a, b, c = t
        return ((b - a).cross(p - a).dot(n) >= 0 and (c - b).cross(p - b).dot(n) >= 0
                and (a - c).cross(p - c).dot(n) >= 0)

    @staticmethod
    def _box_has(lo, hi, p):
        return lo[0] <= p[0] <= hi[0] and lo[1] <= p[1] <= hi[1] and lo[2] <= p[2] <= hi[2]

    def _cutter_data(self, co):
        """Cutter in world coordinates plus its inward samples: points CUT_DEEP under its surface, kept only where they
        are that deep inside it (a recess offsets out of a concave cutter; a tapering bead is thinner)."""
        tris, bvh, open_e, lo, hi = self._tris(co.data, co.matrix_world)
        inner = []
        for t, n in tris:
            for p in self._samples(t, cap=24):
                q = p - n * self.CUT_DEEP
                if self._inside(q, bvh) and bvh.find_nearest(q)[3] > self.CUT_DEEP * 0.9:
                    inner.append(q)                   # (a sliver thinner than 2 CUT_DEEP holds no sample)
        return {'ob': co, 'tris': tris, 'bvh': bvh, 'lo': lo, 'hi': hi, 'inner': inner, 'open': open_e,
                'name': co.name, 'label': co.get('label', co.name)}

    def _near(self, me, Mo, cutters):
        """Cutters that reach into this body: boxes overlap and the surfaces cross, or the cutter lies inside it."""
        _t, bvh, _o, lo, hi = self._tris(me, Mo)
        out = []
        for c in cutters:
            if not all(c['lo'][i] < hi[i] and lo[i] < c['hi'][i] for i in range(3)):
                continue
            if bvh.overlap(c['bvh']) or (c['inner'] and self._inside(c['inner'][0], bvh)):
                out.append(c)
        return out

    def _check(self, res, Mo, near, body_open=0):
        """(samples of material left where a cutter is, open edges added): (0, 0) = every cut is clean."""
        if not len(res.polygons):
            return 0, 0
        tris, bvh, open_e, lo, hi = self._tris(res, Mo)
        bad = 0
        self._deep = 0.0                              # deepest surface sample left inside a cutter (m)
        self._at = None                               # first sample left (world m), for the report
        boxes = [([min(p[i] for p in t) for i in range(3)], [max(p[i] for p in t) for i in range(3)])
                 for t, _n in tris]
        for c in near:
            clo, chi = c['lo'], c['hi']
            for q in c['inner']:                      # the cutter's inside holds none of the result
                if self._box_has(lo, hi, q) and self._inside(q, bvh):
                    bad += 1
                    self._at = self._at or q
            pairs = bvh.overlap(c['bvh'])
            cross = {i for i, _j in pairs}
            for i, j in pairs:                        # where the result's surface meets the cutter's: the cutter
                t, n = tris[i]                        # triangle's points dropped onto the result triangle (a thin
                ct = c['tris'][j][0]                  # tape strip's 200 mm triangle over a 4 mm screw head has no
                for q in (ct[0], ct[1], ct[2], (ct[0] + ct[1] + ct[2]) / 3):     # grid sample on the head)
                    p = q - n * (q - t[0]).dot(n)
                    if not self._box_has(clo, chi, p) or not self._in_tri(p, t, n):
                        continue
                    d = c['bvh'].find_nearest(p)[3]
                    if d > self.CUT_TOL and self._inside(p, c['bvh']):
                        bad += 1
                        self._deep = max(self._deep, d)
                        self._at = self._at or p
            for k, (t, _n) in enumerate(tris):        # no surface of the result inside the cutter: a triangle
                tlo, thi = boxes[k]                   # inside it crosses its surface or lies wholly inside
                if not (tlo[0] < chi[0] and thi[0] > clo[0] and tlo[1] < chi[1] and thi[1] > clo[1]
                        and tlo[2] < chi[2] and thi[2] > clo[2]):
                    continue
                if k not in cross and not self._inside((t[0] + t[1] + t[2]) / 3, c['bvh']):
                    continue
                for p in self._samples(t, cap=16):       # coarse: the cutter samples catch small misses
                    if self._box_has(clo, chi, p):
                        d = c['bvh'].find_nearest(p)[3]
                        if d > self.CUT_TOL and self._inside(p, c['bvh']):
                            bad += 1
                            self._deep = max(self._deep, d)
                            self._at = self._at or p
        return bad, max(0, open_e - body_open)

    @staticmethod
    def _weld(me):
        """Merge coincident vertices (builders repeat seam vertices), drop zero-area faces, fix the winding: the shape
        is unchanged, the mesh becomes watertight where the shape is closed."""
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-8)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-9)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()

    def _boolean(self, pid, me, Mo, obs, solver, tol=False):
        """One DIFFERENCE of `obs` (one object, or several through a collection) from `me`; returns a new mesh."""
        tmp = bpy.data.objects.new(pid + ' tmp', me)
        tmp.matrix_world = Mo
        bpy.context.scene.collection.objects.link(tmp)
        mod = tmp.modifiers.new('cut', 'BOOLEAN')
        mod.operation, mod.solver = 'DIFFERENCE', solver
        col = None
        if len(obs) == 1:
            mod.object = obs[0]
        else:
            col = bpy.data.collections.new(pid + ' cutters')
            for o in obs:
                col.objects.link(o)
            mod.operand_type, mod.collection = 'COLLECTION', col
        if solver == 'EXACT':
            mod.use_hole_tolerant = tol
        dg = bpy.context.evaluated_depsgraph_get()
        cut = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
        bpy.data.objects.remove(tmp)
        if col is not None:
            bpy.data.collections.remove(col)
        return cut

    def _cut_body(self, pid, me, Mo, near):
        _t, bbvh, body_open, blo, bhi = self._tris(me, Mo)
        # the result lies inside the body: only cutter samples inside the body can hold material (checked once)
        near = [dict(c, inner=[q for q in c['inner'] if self._box_has(blo, bhi, q) and self._inside(q, bbvh)])
                for c in near]
        dbg = bool(os.environ.get('CUTDBG')) and os.environ['CUTDBG'] in pid
        cut = self._boolean(pid, me, Mo, [c['ob'] for c in near], 'MANIFOLD')
        bad, op = self._check(cut, Mo, near, body_open)
        if dbg:
            print('CUTDBG', pid, 'all at once,', len(near), 'cutters: left', bad, 'open', op,
                  'faces', len(me.polygons), '->', len(cut.polygons))
        if bad == 0 and op == 0:
            bpy.data.meshes.remove(me)
            return cut
        bpy.data.meshes.remove(cut)
        for c in near:                                # one cutter at a time, each verified
            me = self._cut_one(pid, me, Mo, c, body_open, dbg)
        return me

    def _cut_one(self, pid, me, Mo, c, body_open=0, dbg=False):
        """D-88: subtract one cutter from one body and verify the result (_check). EXACT booleans fail silently on
        coincident faces (a 45 deg hole through stacked core segments came out uncut, so a wire showed through solid
        foam). A failed cut is retried with the cutter nudged or grown by a few microns (a clearance far under any
        fit), hole-tolerant, then FAST; a cut that never verifies is reported (CUT_FAILURES) and the GLB gate
        (collision/collide_glb_blender.py) catches what it leaves."""
        co = c['ob']
        base = co.matrix_world.copy()
        ctr = Vector([(c['lo'][i] + c['hi'][i]) / 2 for i in range(3)])
        size = max(1e-4, min(c['hi'][i] - c['lo'][i] for i in range(3)))

        def grow(um):                                  # scale about the box centre: the thinnest side grows by um
            f = 1 + 2 * um * 1e-6 / size
            return Matrix.Translation(ctr) @ Matrix.Scale(f, 4) @ Matrix.Translation(-ctr)
        tries = [(Matrix(), 'MANIFOLD', False), (Matrix.Translation((2e-6, 1e-6, 3e-6)), 'MANIFOLD', False),
                 (grow(3), 'MANIFOLD', False), (grow(10), 'MANIFOLD', False),
                 (Matrix(), 'EXACT', False), (Matrix(), 'EXACT', True), (grow(3), 'EXACT', True),
                 (Matrix.Translation((3e-6, 2e-6, 1e-6)), 'EXACT', True), (Matrix(), 'FAST', False),
                 (grow(5), 'FAST', False)]
        best = None
        for T, solver, tol in tries:
            co.matrix_world = T @ base
            cut = self._boolean(pid, me, Mo, [co], solver, tol)
            bad, op = self._check(cut, Mo, [c], body_open)
            score = (bad + op, bad, self._deep if len(cut.polygons) else 0.0,
                     tuple(round(v * 1000, 2) for v in self._at) if len(cut.polygons) and self._at else None)
            if dbg:
                print('CUTDBG', pid, c['label'], solver, tol, 'left', bad, 'open', op,
                      'faces', len(me.polygons), '->', len(cut.polygons))
            if best is None or score[:3] < best[0][:3]:
                if best is not None:
                    bpy.data.meshes.remove(best[1])
                best = (score, cut)
            else:
                bpy.data.meshes.remove(cut)
            if score[0] == 0:
                break
        co.matrix_world = base
        if best[0][0] != 0:
            BlenderBackend.CUT_FAILURES.append((pid, c['label'], best[0]))
            print('CUT NOT VERIFIED: %s %s (%s): %d samples left inside the cutter (surface up to %.3f mm deep, '
                  'first at %s mm), %d open edges' % (pid, c['name'], c['label'], best[0][1], best[0][2] * 1000,
                                                      best[0][3], best[0][0] - best[0][1]))
        bpy.data.meshes.remove(me)
        return best[1]

    def joint(self, j, ca, cb):
        ob = bpy.data.objects.new('JOINT ' + j.edge, None)
        ob.empty_display_type = 'ARROWS' if j.kind != 'rigid' else 'PLAIN_AXES'
        ob.empty_display_size = 0.02
        ob.location = j.origin
        _collection('joints').objects.link(ob)
        ob['edge'], ob['kind'], ob['part_a'], ob['part_b'] = j.edge, j.kind, j.a, j.b
        if j.axis:
            ob['axis'] = j.axis
        if j.limits:
            ob['limits'] = list(j.limits)
        ob.hide_render = True
        self.joints[j.edge] = (ob, j)

    def wire(self, w):
        block = self._edge(w.edge).get('wire', {})
        bend = block.get('bend_radius_mm', 5 * w.dia * 1000) / 1000.0
        cu = bpy.data.curves.new(w.edge, 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 1.0                          # per-point radius below = strand radius (one mesh per edge)
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        for line, dia in (w.strands or [(w.points, w.dia)]):
            pts = fillet_polyline(line, bend)
            sp = cu.splines.new('POLY')
            sp.points.add(len(pts) - 1)
            for p, q in zip(sp.points, pts):
                p.co = (q.x, q.y, q.z, 1.0)
                p.radius = dia / 2
        tmp = bpy.data.objects.new(w.edge + ' curve', cu)
        bpy.context.scene.collection.objects.link(tmp)
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmp)
        bpy.data.curves.remove(cu)
        me.name = w.edge
        ob = bpy.data.objects.new(w.edge, me)          # a mesh, so the GLB carries it
        _collection('wires').objects.link(ob)
        me.materials.append(wire_material(block, w.dia))
        for poly in me.polygons:
            poly.use_smooth = True
        e = self._edge(w.edge)
        ob['edge'], ob['kind'], ob['subsystem'] = w.edge, 'wire', w.sub or ''
        ob['part_a'], ob['part_b'], ob['via'] = e.get('part_a', ''), e.get('part_b', ''), e.get('via', '')
        ob['dia_mm'] = round(w.dia * 1000, 2)
        for k in ('gauge_awg', 'connector', 'bend_radius_mm', 'strain_relief', 'disconnect'):
            if k in block:
                ob[k] = block[k]
        if block.get('support_points'):
            ob['support_points'] = '; '.join(block['support_points'])
        self.wires[w.edge] = ob

    def end(self, ctx):
        edges_of = {}
        for e in (self.graph.edges.values() if self.graph else []):
            for p in (e.get('part_a'), e.get('part_b')):
                edges_of.setdefault(p, []).append(e['id'])
        for pid, ob in self.objects.items():
            bm = self.bm.pop(pid)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(ob.data)
            bm.free()
            if not ob.get('mass_proxy'):              # mass-only stand-ins are never drawn: left as built
                self._apply_cuts(pid, ob)             # cut every body, then one solid per part (D-88)
            me = ob.data
            for poly in me.polygons:
                poly.use_smooth = True
            me.set_sharp_from_angle(angle=math.radians(SHARP_DEG))
            info = dict(ctx.parts_info.get(pid, {}), id=pid)
            me.materials.append(material_for(info, self.mode))
            ob['interfaces'] = json.dumps(sorted(edges_of.get(pid, [])))
        bpy.context.view_layer.update()
        return 'blender: %d parts, %d wires, %d joints' % (len(self.objects), len(self.wires), len(self.joints))

    # ---- helpers for the scripts
    def is_proxy(self, pid):
        ob = self.objects.get(pid)
        return bool(ob is not None and ob.get('mass_proxy'))

    def glb_objects(self, objs):
        """Objects to export: every mass-proxy mesh is replaced by an empty (named '<id> (mass proxy)', same
        transform, same custom properties incl. part_id and mass_proxy), so the GLB lists the part and its mass
        without drawing it. The empties are made once and kept in the 'mass proxies' collection."""
        out = []
        for ob in objs:
            if not ob.get('mass_proxy') or ob.type != 'MESH':
                out.append(ob)
                continue
            name = ob.name + ' (mass proxy)'
            em = bpy.data.objects.get(name)
            if em is None:
                em = bpy.data.objects.new(name, None)
                em.empty_display_type = 'PLAIN_AXES'
                em.empty_display_size = 0.01
                _collection('mass proxies').objects.link(em)
            em.matrix_world = ob.matrix_world.copy()
            for k in list(ob.keys()):
                if not k.startswith('_'):
                    em[k] = ob[k]
            out.append(em)
        return out

    def _edge(self, eid):
        return (self.graph.edges.get(eid) if self.graph else None) or {}

    def recolour(self, mode):
        """Switch every part to another colour mode ('material' | 'subsystem' | 'status')."""
        self.mode = mode
        for pid, ob in self.objects.items():
            info = dict(self.graph.parts.get(pid, {}) if self.graph else {}, id=pid)
            ob.data.materials[0] = material_for(info, mode)

    def set_joint(self, edge, value):
        """Pose a revolute (degrees) or slider (metres) joint: moves part_a (and nothing else) about/along the axis,
        given in part_b's frame through the joint origin. Call with 0 to return to the modelled position."""
        ob_j, j = self.joints[edge]
        a = self.objects[j.a]
        base = a.get('_rest')
        if base is None:
            a['_rest'] = [v for row in a.matrix_world for v in row]
            base = a['_rest']
        rest = Matrix([base[0:4], base[4:8], base[8:12], base[12:16]])
        Rb = self.objects[j.b].matrix_world.to_3x3()
        axis = Rb @ Vector([1.0 if c == j.axis else 0.0 for c in 'XYZ'])
        o = Vector(j.origin)
        if j.kind == 'revolute':
            M = Matrix.Translation(o) @ Matrix.Rotation(math.radians(value), 4, axis) @ Matrix.Translation(-o)
        else:
            M = Matrix.Translation(axis * value)
        a.matrix_world = M @ rest


def build(examples=True, root=None, mode='material', log=print):
    """Build the aircraft (or the example aircraft) in a fresh Blender scene. Returns (backend, ctx, graph, results)."""
    import build_all                                  # redesign/fusion/build_all.py
    import merge_check
    r, lst = build_all.roots(examples, root)
    be = BlenderBackend(mode, merge_check.load(r))
    ctx, graph, results = build_all.build(be, r, lst, log=log)
    for sub, f, ok, ms, err in results:
        if not ok:
            log('FAIL %s/%s: %s' % (sub, f, err))
    for sev, code, item, msg in ctx.issues:
        log('%s %s %s: %s' % (sev, code, item, msg))
    return be, ctx, graph, results
