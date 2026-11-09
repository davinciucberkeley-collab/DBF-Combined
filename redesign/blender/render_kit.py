"""render_kit.py - build-manual and review figures from the Blender build of the aircraft (adapted from the proven
docs/figures/figkit.py: studio/bench scenes, Freestyle outlines, orange "act on this" parts, projected callouts).

Use it from a script run inside Blender (render_figures.py does this from a JSON spec):

    be, ctx, graph, _ = blender_backend.build(examples=True)
    S = render_kit.Stage(be, ctx, graph, scene='studio')        # 'studio' (light sweep) | 'workbench' (bench top)
    S.roles(focus=['WNG-005'], context=['*'], ghost=[], hide=['E-*'])   # patterns: part ids, edge ids, fnmatch
    S.explode(1.0)                                               # optional, vectors from explode.py
    S.pose('E-WNG-04', 20)                                       # optional: deflect a revolute joint (deg)
    S.camera('iso', fit='visible')                               # iso | iso_rear | front | side | top | bottom | closeup
    S.callout('WNG-005'); S.callout('E-WNG-05')                  # part id -> "id  name"; edge -> joint stack / wire
    S.caption('Fit the aileron servo', 'Check: horn moves freely')
    S.render('out/figures/servo')                                # PNG + JPEG + JSON sidecar; annotate.py makes the SVG

Look (design system, redesign/design-system/tokens.css): orange --highlight for the parts added in this step,
own material for parts already fitted, pale translucent ghost for context, light stage gradient, ink outlines.
Speed: Cycles, GPU (OptiX/CUDA) when present, 48 samples + denoise, 1600 x 1000 -> 12-18 s per figure on a laptop
RTX 4060, about 40 s on its CPU alone (device='CPU'); engine='EEVEE' (BLENDER_EEVEE_NEXT) is the other fallback.
"""
import fnmatch
import json
import math
import os
import time

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

import blender_backend as bb
import explode as ex

W, H = 1600, 1000
# camera directions: (azimuth from the nose, elevation) in degrees; az 0 = in front (-x), 90 = left (-y)
PRESETS = {
    'iso': (38, 28, False), 'iso_rear': (218, 28, False), 'iso_below': (38, -24, False),
    'front': (0, 0, True), 'rear': (180, 0, True), 'side': (90, 0, True), 'side_right': (270, 0, True),
    'top': (0, 90, True), 'bottom': (0, -90, True), 'closeup': (38, 32, False),
}
# subject box on the image (fractions, y down): room for callout columns left and right
FRAME_CALLOUTS = (0.22, 0.78, 0.07, 0.93)
FRAME_PLAIN = (0.06, 0.94, 0.06, 0.94)


def _view_dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((-math.cos(e) * math.cos(a), -math.cos(e) * math.sin(a), math.sin(e)))


def _look(cam, loc, target, up_hint=Vector((0, 0, 1))):
    f = (Vector(target) - Vector(loc)).normalized()
    if abs(f.dot(up_hint)) > 0.999:
        up_hint = Vector((-1, 0, 0))                  # straight up/down views: nose to the top of the image
    r = f.cross(up_hint).normalized()
    u = r.cross(f)
    M = Matrix((r, u, -f)).transposed().to_4x4()
    M.translation = Vector(loc)
    cam.matrix_world = M


class Stage:
    def __init__(self, be, ctx, graph, scene='studio', size=(W, H), engine='CYCLES', samples=48, device='AUTO'):
        self.be, self.ctx, self.graph = be, ctx, graph
        self.kind, self.size = scene, tuple(size)
        self.callouts, self.cap = [], None
        self.role = {}                                # item id -> focus | context | ghost | hide
        self.offsets = None
        self.explode_factor = 0.0
        self.meta = {}
        sc = bpy.context.scene
        self.sc = sc
        self.cam = None
        self.floor = None
        self._render_settings(engine, samples, device)
        self._style()
        self.set_kind(scene)
        self.mats = {'focus': bb._principled('role focus', bb.srgb(bb.TOKENS['highlight']), 0.5),
                     'ghost': bb._principled('role ghost', bb.srgb('#AEB9C7'), 0.4, alpha=0.13)}

    # ------------------------------------------------------------------ scene
    def set_kind(self, kind):
        """Switch between 'studio' and 'workbench' (world gradient and floor) without rebuilding anything else."""
        self.kind = kind
        self._world()
        if self.floor is not None:
            bpy.data.objects.remove(self.floor)
            self.floor = None

    def set_size(self, w, h):
        self.size = (int(w), int(h))
        self.sc.render.resolution_x, self.sc.render.resolution_y = self.size

    def _render_settings(self, engine, samples, device='AUTO'):
        sc = self.sc
        sc.render.resolution_x, sc.render.resolution_y = self.size
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
        sc.view_settings.view_transform = 'Standard'   # token colours stay true
        sc.view_settings.look = 'None'
        sc.view_settings.exposure = 0.0
        self.engine = engine.upper()
        if self.engine == 'EEVEE':
            sc.render.engine = 'BLENDER_EEVEE_NEXT'
            sc.eevee.taa_render_samples = 32
            return
        sc.render.engine = 'CYCLES'
        sc.cycles.device = 'CPU'
        try:
            if device.upper() == 'CPU':
                raise RuntimeError('CPU requested')
            prefs = bpy.context.preferences.addons['cycles'].preferences
            for t in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
                try:
                    prefs.compute_device_type = t
                except TypeError:
                    continue
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == t]
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == t
                    sc.cycles.device = 'GPU'
                    break
        except Exception:
            pass
        sc.cycles.samples = samples
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.cycles.max_bounces = 6
        sc.cycles.transparent_max_bounces = 12
        sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False

    def _style(self):
        """Freestyle outlines: ink on solid parts, light grey on ghosts, none on wires (they are thin)."""
        sc = self.sc
        sc.render.use_freestyle = True
        sc.render.line_thickness_mode = 'ABSOLUTE'
        sc.render.line_thickness = 1.0
        vl = sc.view_layers[0]
        vl.use_freestyle = True
        fs = vl.freestyle_settings
        fs.mode = 'EDITOR'
        fs.crease_angle = math.radians(140)
        self.cols = {k: bb._collection('role ' + k) for k in ('ghost', 'nolines')}
        while len(fs.linesets):
            fs.linesets.remove(fs.linesets[0])

        def lineset(name, col, neg, rgb, thick, alpha):
            ls = fs.linesets.new(name)
            ls.select_by_visibility = True
            ls.visibility = 'VISIBLE'
            ls.select_by_edge_types = True
            ls.select_silhouette = ls.select_border = ls.select_crease = ls.select_external_contour = True
            ls.select_by_collection = True
            ls.collection = col
            ls.collection_negation = neg
            st = bpy.data.linestyles.new(name)
            st.color, st.thickness, st.alpha = rgb, thick, alpha
            ls.linestyle = st
            return ls
        # solid parts: everything not in 'ghost' and not in 'nolines' (two exclusive sets would need two layers,
        # so 'nolines' holds the ghosts too; see roles())
        lineset('ink', self.cols['nolines'], 'EXCLUSIVE', bb.srgb(bb.TOKENS['ink']), 1.35, 0.85)
        lineset('ghost', self.cols['ghost'], 'INCLUSIVE', bb.srgb('#8C97A6'), 0.9, 0.55)

    def _world(self):
        w = bpy.data.worlds.new('stage')
        self.sc.world = w
        w.use_nodes = True
        nt = w.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputWorld')
        env = nt.nodes.new('ShaderNodeBackground')
        env.inputs['Color'].default_value = (0.80, 0.83, 0.87, 1)
        env.inputs['Strength'].default_value = 0.45
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        if self.kind == 'workbench':
            top, bot = '#F1F0EC', '#DAD8D2'
        else:
            top, bot = bb.TOKENS['stage-top'], bb.TOKENS['stage-bottom']
        ramp.color_ramp.elements[0].color = (*bb.srgb(bot), 1)
        ramp.color_ramp.elements[1].color = (*bb.srgb(top), 1)
        ramp.color_ramp.elements[0].position = 0.1
        ramp.color_ramp.elements[1].position = 0.9
        bg = nt.nodes.new('ShaderNodeBackground')
        bg.inputs['Strength'].default_value = 1.0
        lp = nt.nodes.new('ShaderNodeLightPath')
        mix = nt.nodes.new('ShaderNodeMixShader')
        L = nt.links.new
        L(tc.outputs['Window'], sep.inputs[0])
        L(sep.outputs['Y'], ramp.inputs['Fac'])
        L(ramp.outputs['Color'], bg.inputs['Color'])
        L(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
        L(env.outputs[0], mix.inputs[1])
        L(bg.outputs[0], mix.inputs[2])
        L(mix.outputs[0], out.inputs['Surface'])

    def _floor(self, z, centre, radius):
        if self.floor is None:
            bpy.ops.mesh.primitive_plane_add(size=1)
            self.floor = bpy.context.active_object
            self.floor.name = 'stage floor'
            for c in list(self.floor.users_collection):
                c.objects.unlink(self.floor)
            self.cols['nolines'].objects.link(self.floor)
            if self.kind == 'workbench':
                self.floor.data.materials.append(bb._principled('bench top', bb.srgb('#C4C3BE'), 0.7))
            elif self.engine == 'CYCLES':
                self.floor.is_shadow_catcher = True
                self.floor.visible_glossy = False         # never mirrored in shiny parts (dark bands)
                self.floor.visible_diffuse = False
            else:
                self.floor.data.materials.append(bb._principled('stage floor', bb.srgb(bb.TOKENS['stage-bottom']), 0.8))
        self.floor.scale = (radius * 30, radius * 30, 1)
        self.floor.location = (centre.x, centre.y, z)

    def _lights(self, centre, radius, view, ortho=False):
        for ob in [o for o in bpy.data.objects if o.type == 'LIGHT']:
            bpy.data.objects.remove(ob)
        az = math.atan2(-view.y, -view.x)             # camera azimuth from the nose (matches PRESETS)
        d = max(radius, 0.3) * 4.0

        def area(name, daz, el, energy, size, rgb=(1, 1, 1)):
            a, e = az + math.radians(daz), math.radians(el)
            loc = centre + Vector((-math.cos(e) * math.cos(a), -math.cos(e) * math.sin(a), math.sin(e))) * d
            L = bpy.data.lights.new(name, 'AREA')
            L.energy, L.size, L.color = energy * d * d, size * d, rgb
            ob = bpy.data.objects.new(name, L)
            bpy.context.scene.collection.objects.link(ob)
            _look(ob, loc, centre)
        area('key', -50, 30 if ortho else 55, 5.5, 0.6)       # lower key in elevations: no overhang shadows
        area('fill', 35, 12, 3.2, 1.2, (0.92, 0.95, 1.0))
        area('rim', 170, 40, 5, 0.6)
        area('top', 0, 89, 0.4 if ortho else 1.2, 1.5)

    # ------------------------------------------------------------------ what is shown, and how
    def items(self):
        """id -> object for every part and wire."""
        out = dict(self.be.objects)
        out.update(self.be.wires)
        return out

    def roles(self, focus=(), context=('*',), ghost=(), hide=(), xray=()):
        """Assign each part / wire a role by pattern (fnmatch on part id or edge id). Order of precedence:
        xray > focus > ghost > context > hide; anything matched by nothing is hidden. xray = drawn as a ghost even
        though it belongs to this step (to see inside a box)."""
        def hit(i, pats):
            return any(fnmatch.fnmatchcase(i, p) for p in pats)
        for c in self.cols.values():
            for ob in list(c.objects):
                if ob is not self.floor:
                    c.objects.unlink(ob)
        self.role = {}
        fs = self.sc.view_layers[0].freestyle_settings
        for i, ob in self.items().items():
            r = ('ghost' if hit(i, xray) else 'focus' if hit(i, focus) else 'ghost' if hit(i, ghost) else
                 'hide' if hit(i, hide) else 'context' if hit(i, context) else 'hide')
            self.role[i] = r
            ob.hide_render = ob.hide_viewport = (r == 'hide')
            slot = ob.material_slots[0]
            if r in ('focus', 'ghost'):
                slot.link = 'OBJECT'
                slot.material = self.mats[r]
            else:
                slot.link = 'DATA'
            ob.visible_shadow = r != 'ghost'
            if r == 'ghost':
                self.cols['ghost'].objects.link(ob)
                self.cols['nolines'].objects.link(ob)
            if i in self.be.wires:
                self.cols['nolines'].objects.link(ob)
        fs.linesets['ghost'].show_render = 'ghost' in self.role.values()   # an empty line set prints an error
        return self.role

    def explode(self, factor=1.0, root=None, gap=0.06, overrides=None):
        self.offsets = ex.vectors(self.be, self.ctx, self.graph, root, gap, overrides)
        ex.apply(self.be, self.offsets, factor)
        self.explode_factor = factor
        for i, ob in self.be.wires.items():          # explode hides wires; keep that unless the role says hide
            ob.hide_render = ob.hide_render or factor > 0

    def pose(self, edge, value):
        self.be.set_joint(edge, value)

    # ------------------------------------------------------------------ geometry helpers
    def _visible(self):
        return [ob for ob in self.items().values() if not ob.hide_render]

    def _points(self, objs):
        pts = []
        for ob in objs:
            M = ob.matrix_world
            vs = ob.data.vertices
            step = max(1, len(vs) // 4000)
            pts += [M @ vs[k].co for k in range(0, len(vs), step)]
        return pts

    def _fit_objects(self, fit):
        if fit == 'visible':
            return self._visible()
        if fit == 'all':
            return list(self.be.objects.values())
        its = self.items()
        return [its[i] for i in fit if i in its]

    # ------------------------------------------------------------------ camera
    def camera(self, preset='iso', fit='visible', lens=50, frame=None, az=None, el=None, ortho=None, floor=None):
        """Place the camera on a preset direction and frame the `fit` objects ('visible', 'all' or a list of ids;
        for 'closeup' give the part ids). frame = subject box on the image (x0, x1, y0, y1 fractions, y down);
        default leaves side room for callouts when there are any (call camera() after callout())."""
        paz, pel, portho = PRESETS[preset]
        az = paz if az is None else az
        el = pel if el is None else el
        ortho = portho if ortho is None else ortho
        if preset == 'closeup' and lens == 50:
            lens = 70
        view = _view_dir(az, el)
        objs = self._fit_objects(fit)
        self.meta['fit_ids'] = [o.name for o in objs]
        pts = self._points(objs)
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        centre, radius = (lo + hi) / 2, max((hi - lo).length / 2, 0.02)
        if self.cam is None:
            cd = bpy.data.cameras.new('cam')
            self.cam = bpy.data.objects.new('cam', cd)
            bpy.context.scene.collection.objects.link(self.cam)
            self.sc.camera = self.cam
        cd = self.cam.data
        cd.sensor_fit, cd.sensor_width = 'HORIZONTAL', 36
        cd.clip_start, cd.clip_end = radius / 200, radius * 200
        fr = frame or (FRAME_CALLOUTS if self.callouts else FRAME_PLAIN)
        aspect = self.size[1] / self.size[0]
        if ortho:
            cd.type = 'ORTHO'
            dist = radius * 6
            _look(self.cam, centre + view * dist, centre)
            R = self.cam.matrix_world.to_3x3()
            r, u = R.col[0], R.col[1]
            us, vs = [p.dot(r) for p in pts], [p.dot(u) for p in pts]
            s = max((max(us) - min(us)) / (fr[1] - fr[0]), (max(vs) - min(vs)) / ((fr[3] - fr[2]) * aspect))
            cu = (max(us) + min(us)) / 2 - ((fr[0] + fr[1]) / 2 - 0.5) * s
            cv = (max(vs) + min(vs)) / 2 + ((fr[2] + fr[3]) / 2 - 0.5) * s * aspect
            cd.ortho_scale = s
            base = centre - r * centre.dot(r) - u * centre.dot(u)
            tgt = base + r * cu + u * cv
            _look(self.cam, tgt + view * dist, tgt)
        else:
            cd.type = 'PERSP'
            cd.lens = lens
            dist = radius / math.sin(math.atan(18 / lens)) * 1.1
            tgt = centre.copy()
            want_c = Vector(((fr[0] + fr[1]) / 2, 1 - (fr[2] + fr[3]) / 2))
            for _ in range(12):                        # converge size and centring on the projected points
                _look(self.cam, tgt + view * dist, tgt)
                bpy.context.view_layer.update()
                ps = [world_to_camera_view(self.sc, self.cam, p) for p in pts]
                if min(p.z for p in ps) <= 0:
                    dist *= 1.5
                    continue
                x0, x1 = min(p.x for p in ps), max(p.x for p in ps)
                y0, y1 = min(p.y for p in ps), max(p.y for p in ps)
                k = max((x1 - x0) / (fr[1] - fr[0]), (y1 - y0) / (fr[3] - fr[2]))
                err = Vector(((x0 + x1) / 2, (y0 + y1) / 2)) - want_c
                if abs(k - 1) < 0.01 and err.length < 0.004:
                    break
                R = self.cam.matrix_world.to_3x3()
                width = 2 * dist * 18 / lens       # frame width at the target distance
                tgt += R.col[0] * err.x * width + R.col[1] * err.y * width * aspect
                dist *= k ** 0.85
        bpy.context.view_layer.update()
        vis = self._points(self._visible())
        zmin = min(p.z for p in vis)
        self._floor(zmin - 0.0005, centre, radius)
        # plan views (straight up/down) look cleaner without cast shadows on the floor
        self.floor.hide_render = not (floor if floor is not None else abs(el) < 80)
        self._lights(centre, radius, view, ortho)
        self.meta['camera'] = {'preset': preset, 'az_deg': az, 'el_deg': el, 'ortho': ortho, 'lens_mm': lens,
                               'location_m': [round(v, 4) for v in self.cam.location], 'fit': fit if isinstance(fit, str) else list(fit),
                               'frame': list(fr)}
        return self.cam

    # ------------------------------------------------------------------ callouts
    def _px(self, p):
        v = world_to_camera_view(self.sc, self.cam, Vector(p))
        return (v.x * self.size[0], (1 - v.y) * self.size[1], v.z)

    def _visible_point(self, ob, n=28):
        """A point on `ob` the camera can see: cast an n x n grid of rays over the part's projected box (looking
        through ghosts, hidden objects and the floor) and keep the hit nearest the middle of the visible hits.
        None if the part is fully hidden behind solid parts."""
        dg = bpy.context.evaluated_depsgraph_get()
        M = self.cam.matrix_world
        R = M.to_3x3()
        cam = M.translation
        fwd = -R.col[2]
        ps = [world_to_camera_view(self.sc, self.cam, p) for p in self._points([ob])]
        x0, x1 = max(0.0, min(p.x for p in ps)), min(1.0, max(p.x for p in ps))
        y0, y1 = max(0.0, min(p.y for p in ps)), min(1.0, max(p.y for p in ps))
        cd = self.cam.data
        aspect = self.size[1] / self.size[0]
        hits, got = [], {}
        for i in range(n):
            for j in range(n):
                u, v = x0 + (x1 - x0) * (i + 0.5) / n, y0 + (y1 - y0) * (j + 0.5) / n
                if cd.type == 'ORTHO':
                    o = cam + R.col[0] * (u - 0.5) * cd.ortho_scale + R.col[1] * (v - 0.5) * cd.ortho_scale * aspect
                    d = fwd
                else:
                    w = 36 / cd.lens                       # sensor width / focal length at unit distance
                    d = (fwd + R.col[0] * (u - 0.5) * w + R.col[1] * (v - 0.5) * w * aspect).normalized()
                    o = cam
                for _ in range(8):
                    hit, loc, _n, _i, obj, _m = self.sc.ray_cast(dg, o, d)
                    if not hit:
                        break
                    if obj.name == ob.name:
                        hits.append((u, v, loc))
                        got[(i, j)] = loc
                        break
                    if obj.hide_render or self.role.get(obj.name) == 'ghost' or obj is self.floor:
                        o = loc + d * 1e-4
                        continue
                    break
        if not hits:
            return None
        # pick the cell deepest inside the visible region (largest distance to a cell where the part is not seen),
        # so the dot never lands on an edge where another part starts; ties -> nearest the visible centre
        mi = sum(i for i, _ in got) / len(got)
        mj = sum(j for _, j in got) / len(got)
        depth = {c: 0 for c in got}
        frontier = [c for c in got if any((c[0] + a, c[1] + b) not in got for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for c in frontier:
            depth[c] = 1
        level = 1
        while frontier:
            nxt = []
            for c in frontier:
                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (c[0] + a, c[1] + b)
                    if q in depth and depth[q] == 0:
                        depth[q] = level + 1
                        nxt.append(q)
            frontier, level = nxt, level + 1
        best = max(got, key=lambda c: (min(depth[c], 4), -((c[0] - mi) ** 2 + (c[1] - mj) ** 2)))
        return got[best]

    def callout(self, item, text=None, detail=None, at=None):
        """Label a part id or an edge id (joint stack / wire / contact text from interfaces.json), or any text at a
        world point `at`. Positions are resolved at render time (after camera and explode)."""
        self.callouts.append({'item': item, 'text': text, 'detail': detail, 'at': at})

    def _callout_text(self, item):
        g = self.graph
        if item in g.parts:
            p = g.parts[item]
            return item, p.get('name', ''), None
        e = g.edges.get(item, {})
        js, wb = e.get('joint_stack'), e.get('wire')
        if js:
            txt = '%sx %s' % (js.get('count', 1), js.get('fastener', '?'))
            if js.get('insert') and not js['insert'].lower().startswith('none'):
                txt += ' into ' + js['insert']
            elif js.get('washer_nut') and 'nyloc' in js['washer_nut'].lower():
                txt += ' + nyloc'
            det = ' / '.join(x for x in (js.get('tool'), js.get('torque')) if x)
            return item, txt, det
        if wb:
            txt = ', '.join(x for x in (wb.get('connector'), ('%s AWG' % wb['gauge_awg']) if wb.get('gauge_awg') else None) if x)
            det = 'bend >= %s mm' % wb['bend_radius_mm'] if wb.get('bend_radius_mm') else None
            return item, txt, det
        ct = g.ctypes.get(e.get('via'), {})
        return item, ct.get('spec', e.get('via', '')).split('(')[0].strip(), e.get('notes') or None

    def _resolve_callouts(self):
        out = []
        J = {j.edge: j for j in self.ctx.joints}
        for c in self.callouts:
            item = c['item']
            title, text, detail = self._callout_text(item) if item else ('', '', None)
            text = c['text'] or text
            detail = c['detail'] if c['detail'] is not None else detail
            occluded = False
            if c['at'] is not None:
                p = Vector(c['at'])
            elif item in self.be.objects or item in self.be.wires:
                ob = self.items()[item]
                if ob.hide_render:
                    continue
                p = self._visible_point(ob)
                if p is None:
                    occluded = True
                    pts = self._points([ob])
                    p = sum(pts, Vector()) / len(pts)
            elif item in J:
                j = J[item]
                p = Vector(j.origin) + (self.offsets.get(j.a, Vector()) * self.explode_factor if self.offsets else Vector())
                p, occluded = self._joint_anchor(p, (j.a, j.b))
            else:
                e = self.graph.edges.get(item, {})
                ob = self.be.objects.get(e.get('part_a'))
                if ob is None or ob.hide_render:
                    continue
                p = self._visible_point(ob)
                if p is None:
                    continue
            x, y, _ = self._px(p)
            role = self.role.get(item)
            if role is None:
                e = self.graph.edges.get(item, {})
                role = 'focus' if 'focus' in (self.role.get(e.get('part_a')), self.role.get(e.get('part_b'))) else 'context'
            out.append({'item': item, 'x': round(x, 1), 'y': round(y, 1), 'title': title, 'text': text,
                        'detail': detail, 'role': role, 'occluded': occluded, 'world_m': [round(v, 4) for v in p]})
        return out

    def _joint_anchor(self, p, parts):
        """Joint origins lie on a contact face, so a ray to them usually first meets one of the two joined parts:
        then the dot moves to that visible surface point. Hidden only when some OTHER solid part is in the way."""
        dg = bpy.context.evaluated_depsgraph_get()
        cam = self.cam.matrix_world.translation
        if self.cam.data.type == 'ORTHO':
            d = -self.cam.matrix_world.to_3x3().col[2]
            o = p - d * 50
        else:
            o, d = cam, (p - cam).normalized()
        for _ in range(8):
            hit, loc, _n, _i, obj, _m = self.sc.ray_cast(dg, o, d)
            if not hit or (loc - o).length >= (p - o).length - 0.002:
                return p, False
            if obj.hide_render or self.role.get(obj.name) == 'ghost' or obj is self.floor:
                o = loc + d * 1e-4
                continue
            if obj.name in parts:                 # in front of it is one of the two joined parts: not hidden
                return (loc if (loc - p).length < 0.02 else p), False
            return p, True
        return p, False

    def caption(self, title, sub=''):
        self.cap = {'title': title, 'sub': sub}

    # ------------------------------------------------------------------ render
    def render(self, path_base, annotate=True):
        """Render PNG (+ JPEG for embedding) and write the JSON sidecar; then annotate.py writes the SVG."""
        os.makedirs(os.path.dirname(path_base), exist_ok=True)
        sc = self.sc
        t0 = time.time()
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_mode = 'RGB'
        sc.render.filepath = path_base + '.png'
        bpy.ops.render.render(write_still=True)
        t_render = time.time() - t0
        sc.render.image_settings.file_format = 'JPEG'
        sc.render.image_settings.quality = 88
        bpy.data.images['Render Result'].save_render(path_base + '.jpg', scene=sc)
        sc.render.image_settings.file_format = 'PNG'
        shown, clipped = [], []
        W_, H_ = self.size
        for i, ob in self.items().items():
            if ob.hide_render:
                continue
            ps = [self._px(p) for p in self._points([ob])]
            xs, ys = [p[0] for p in ps], [p[1] for p in ps]
            box = [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]
            if (box[0] < 0 or box[1] < 0 or box[2] > W_ or box[3] > H_) and i in self.meta.get('fit_ids', ()):
                clipped.append(i)                     # only the parts the camera was asked to frame count
            info = self.graph.parts.get(i) or {}
            shown.append({'id': i, 'role': self.role.get(i), 'name': info.get('name', ''), 'status': info.get('status'),
                          'mass_g': info.get('mass_g'), 'subsystem': info.get('subsystem', ob.get('subsystem')),
                          'bbox_px': box})
        boxes = [s['bbox_px'] for s in shown]
        subject = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else None
        meta = {'id': os.path.basename(path_base), 'size': [W_, H_], 'scene': self.kind,
                'engine': sc.render.engine, 'device': getattr(sc.cycles, 'device', None) if sc.render.engine == 'CYCLES' else None,
                'samples': sc.cycles.samples if sc.render.engine == 'CYCLES' else sc.eevee.taa_render_samples,
                'render_s': round(t_render, 2), 'explode': self.explode_factor,
                'camera': self.meta.get('camera'), 'caption': self.cap, 'subject_px': subject,
                'callouts': self._resolve_callouts(), 'shown': shown,
                'hidden': sorted(i for i, r in self.role.items() if r == 'hide'),
                'clipped': clipped,
                'legend': sorted({r for r in self.role.values() if r != 'hide'}),
                'files': {'png': os.path.basename(path_base) + '.png', 'jpg': os.path.basename(path_base) + '.jpg'}}
        with open(path_base + '.json', 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=1)
        print('rendered %s in %.1f s%s' % (meta['id'], t_render, ('  CLIPPED: ' + ', '.join(clipped)) if clipped else ''))
        if annotate:
            import annotate as an
            an.build(path_base + '.json')
        return meta

    def reset(self):
        """Back to the assembled, unposed state with no callouts (between figures)."""
        if self.offsets is not None:
            ex.apply(self.be, self.offsets, 0.0)
        for e, (ob, j) in self.be.joints.items():
            if self.be.objects.get(j.a) is not None and '_rest' in self.be.objects[j.a]:
                self.be.set_joint(e, 0)
        self.explode_factor = 0.0
        self.callouts, self.cap, self.meta = [], None, {}
