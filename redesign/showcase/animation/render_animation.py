"""render_animation.py - "How the K09-L flies": a 17 s explainer animation rendered in Blender from the real CAD.

    python redesign/showcase/animation/render_animation.py [--samples 16] [--frames 0,90,200] [--work DIR] [--keep]

Run with the system Python (needs Pillow). It drives three stages:
  1. render   Blender (headless, EEVEE Next) builds the aircraft from redesign/subsystems/*/fusion/*.py through
              redesign/blender/blender_backend.py (same as showcase/tools/render_showcase.py), poses it per frame
              along the flight path and writes raw PNG frames to --work.
  2. overlay  Pillow adds the lower-third phase label, phase dots and progress bar (design-system ink / highlight,
              IBM Plex Sans if installed, else Segoe UI - the tokens.css fallback stack).
  3. encode   Blender's own FFmpeg (VSE) writes k09l-how-it-flies.mp4 (H.264); Pillow writes the GIF and poster.png.

--frames renders only those frames (for checking) and stops after the overlay. Blender path: --blender or $BLENDER.
Inside Blender the same file is the render / encode worker (selected by the first argument after '--').

Flight model (redesign/CONFIGURATION.md): ArduPilot tailsitter - stands nose-up on the four fin-tip feet, takes off
as a quadcopter, pitches 90 deg nose-down onto the wing and flies on the same four motors (~15-16 m/s), elevons give
pitch and roll, pitches back up to hover and lands on the feet. World frame: z up, flight toward -x. Attitude is
Rot_Y(theta) about the wing centre, theta = 90 deg in hover (nose up), 0 in cruise.
"""
import math
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
REDESIGN = os.path.dirname(SHOW)
BL = os.path.join(REDESIGN, 'blender')
BLENDER_DEFAULT = r'C:/Users/dillo/tools/blender/blender-4.2.3-windows-x64/blender.exe'
OUT_MP4 = os.path.join(HERE, 'k09l-how-it-flies.mp4')
OUT_GIF = os.path.join(HERE, 'k09l-how-it-flies.gif')
OUT_POSTER = os.path.join(HERE, 'poster.png')

FPS = 30
W, H = 1280, 720
# (start s, end s, label) - the label shows over [start, end)
PHASES = [
    (0.0, 1.6, 'Ready: standing on its fin tips'),
    (1.6, 4.6, 'Vertical take-off as a quadcopter'),
    (4.6, 8.0, 'Transition: pitches 90\u00b0 onto the wing'),
    (8.0, 11.2, 'Cruise on the wing \u00b7 ~16 m/s'),
    (11.2, 13.8, 'Back-transition to hover'),
    (13.8, 17.0, 'Vertical landing on the fin tips'),
]
DURATION = PHASES[-1][1]
NFRAMES = int(round(DURATION * FPS))
POSTER_FRAME = int(6.3 * FPS)            # mid-transition


# =====================================================================================================================
# flight path (pure math, shared by the worker)
# =====================================================================================================================
def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)            # smootherstep


def seg(t, t0, t1):
    return smooth((t - t0) / (t1 - t0))


V_CRUISE = 16.0          # m/s, shown at the true speed against the ground grid
H_CRUISE = 4.2           # m above the ground


def speed(t):
    """Forward speed (m/s, toward -x) at time t."""
    if t < 4.6:
        return 0.0
    if t < 8.0:
        return V_CRUISE * seg(t, 4.6, 7.9)
    if t < 11.2:
        return V_CRUISE
    if t < 13.8:
        return V_CRUISE * (1 - seg(t, 11.2, 13.3))
    return 0.0


_XTAB = []


def xpos(t):
    """-(integral of speed), from a 600 Hz trapezoid table built once."""
    hz = 600
    if not _XTAB:
        s, prev = 0.0, speed(0)
        _XTAB.append(0.0)
        for i in range(1, int(DURATION * hz) + 2):
            cur = speed(i / hz)
            s += 0.5 * (prev + cur) / hz
            prev = cur
            _XTAB.append(-s)
    u = min(max(t, 0.0), DURATION) * hz
    k = int(u)
    return _XTAB[k] + (_XTAB[k + 1] - _XTAB[k]) * (u - k)


def state(t):
    """(x, z_above_ground_offset, theta_deg, bank_deg, prop_rate 0..1, elevon (pitch_deg, roll_deg))."""
    # height of the wing centre above its ground-standing height
    if t < 2.4:
        z = 0.0
    elif t < 4.6:
        z = 2.6 * seg(t, 2.4, 4.8)
    elif t < 8.0:
        z = 2.6 + (H_CRUISE - 2.6) * seg(t, 4.4, 8.0)
    elif t < 11.2:
        z = H_CRUISE
    elif t < 13.8:
        z = H_CRUISE + 0.5 * math.sin(math.pi * seg(t, 11.2, 13.8)) - (H_CRUISE - 2.4) * seg(t, 12.6, 13.8)
    else:
        z = 2.4 * (1 - seg(t, 13.8, 16.0))
    # attitude: 90 = nose up (hover), 0 = on the wing
    theta = 90.0
    if 4.6 <= t < 11.2:
        theta = 90.0 - 90.0 * seg(t, 4.7, 7.6)
    elif t >= 11.2:
        theta = 90.0 * seg(t, 11.3, 13.4)
        # a little flare overshoot while it stops, then settles
        theta += 8.0 * math.sin(math.pi * seg(t, 12.8, 14.4)) * (t < 14.4)
    if 4.6 <= t < 11.2:
        theta -= 0.0
    bank = 0.0
    if 9.3 <= t < 10.9:
        bank = 10.0 * math.sin(2 * math.pi * seg(t, 9.3, 10.9))
    # props: spin up 1.2-2.2 s, spin down after touchdown 16.0-16.8 s
    rate = seg(t, 1.2, 2.2) * (1 - seg(t, 16.0, 16.8))
    # elevons: pitch (+ = trailing edge up), roll (differential)
    pe = 0.0
    re_ = 0.0
    pe += 14.0 * math.sin(math.pi * seg(t, 4.8, 7.4))        # pitching over in transition
    pe += 12.0 * math.sin(math.pi * seg(t, 8.2, 9.2))        # cruise: pitch demo
    re_ += 16.0 * math.sin(2 * math.pi * seg(t, 9.3, 10.9))  # cruise: roll demo (with the bank)
    pe -= 16.0 * math.sin(math.pi * seg(t, 11.3, 13.3))      # back-transition: pitch up
    return xpos(t), z, theta, bank, rate, (pe, re_)


def phase_at(t):
    for i, (a, b, _) in enumerate(PHASES):
        if a <= t < b:
            return i
    return len(PHASES) - 1


# =====================================================================================================================
# Blender worker
# =====================================================================================================================
def blender_render(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='')
    ap.add_argument('--samples', type=int, default=16)
    a = ap.parse_args(argv)
    sys.path.insert(0, BL)
    sys.dont_write_bytecode = True
    import fnmatch
    import json
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    import blender_backend as bb

    spec = json.load(open(os.path.join(BL, 'specs', 'showcase.json'), encoding='utf-8'))
    flight = spec['flight']
    be, ctx, graph, _ = bb.build(False, None, log=lambda *x: None)
    sc = bpy.context.scene
    items = dict(be.objects)
    items.update(be.wires)
    shown = {}
    for i, ob in items.items():
        vis = any(fnmatch.fnmatchcase(i, p) for p in flight)
        ob.hide_render = ob.hide_viewport = not vis
        if vis:
            shown[i] = ob
    rest = {i: ob.matrix_world.copy() for i, ob in shown.items()}

    # ---- pivot (wing centre) and ground contact in the hover pose
    pivot = Vector((0.10, 0.0, 0.007))
    Rh = Matrix.Rotation(math.radians(90), 4, 'Y')

    def pts(ob, M=None):
        M = M or ob.matrix_world
        vs = ob.data.vertices
        st = max(1, len(vs) // 3000)
        return [M @ vs[k].co for k in range(0, len(vs), st)]
    zmin = min(p.z for ob in shown.values() for p in pts(ob, Rh @ Matrix.Translation(-pivot) @ ob.matrix_world))
    z0 = -zmin                                        # pivot height when standing on the feet

    # ---- props: hub, axis (smallest principal direction of the blade), spin sense, blur disc
    props = []
    disc_mat = bb._principled('prop disc', bb.srgb('#2A2D31'), 0.6, alpha=0.0)
    disc_mat.blend_method = 'BLEND'
    disc_mat.surface_render_method = 'BLENDED'
    disc_bsdf = disc_mat.node_tree.nodes.get('Principled BSDF')
    for c in ('UL', 'UR', 'LL', 'LR'):
        blade = shown['PRP-003-' + c]
        adapter = shown['PRP-004-' + c]
        P = np.array([blade.matrix_world @ v.co for v in blade.data.vertices])
        cen = P.mean(axis=0)
        w, V = np.linalg.eigh(np.cov((P - cen).T))
        ax = Vector(V[:, 0]).normalized()
        if ax.x < 0:
            ax = -ax                                   # +x-ish = aft, i.e. looking from the nose
        hub = Vector(cen)
        r = max(((Vector(p) - hub) - ax * (Vector(p) - hub).dot(ax)).length for p in P)
        name = blade.get('name', '')
        sense = 1.0 if 'CW from the nose' in name and 'CCW' not in name else -1.0
        # disc
        n = 64
        me = bpy.data.meshes.new('disc ' + c)
        q = ax.to_track_quat('Z', 'Y').to_matrix()
        verts = [hub] + [hub + q @ Vector((math.cos(2 * math.pi * k / n) * r, math.sin(2 * math.pi * k / n) * r, 0))
                         for k in range(n)]
        me.from_pydata([tuple(v) for v in verts], [], [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)])
        me.materials.append(disc_mat)
        d = bpy.data.objects.new('disc ' + c, me)
        sc.collection.objects.link(d)
        d.visible_shadow = False
        rest['disc ' + c] = d.matrix_world.copy()
        shown['disc ' + c] = d
        props.append({'c': c, 'hub': hub, 'ax': ax, 'sense': sense, 'parts': ['PRP-003-' + c, 'PRP-004-' + c]})

    # ---- elevons: hinge from the joints (axis Y of WNG-001 through the joint origin)
    Rb = shown['WNG-001'].matrix_world.to_3x3()
    hinge_ax = (Rb @ Vector((0, 1, 0))).normalized()
    elevons = {}
    for e, (ob_j, j) in be.joints.items():
        if j.kind == 'revolute' and j.a.startswith('WNG-01'):
            elevons[j.a] = Vector(j.origin)

    # ---- render settings
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.eevee.taa_render_samples = a.samples
    try:
        sc.eevee.use_shadows = True
        sc.eevee.shadow_ray_count = 2
        sc.eevee.shadow_step_count = 8
        sc.eevee.use_raytracing = True
        sc.eevee.ray_tracing_options.resolution_scale = '2'
        sc.eevee.use_fast_gi = True
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'          # as render_kit: token colours stay true
    sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'

    # ---- world: design-system stage gradient for camera rays, soft neutral ambient otherwise (render_kit._world)
    wd = bpy.data.worlds.new('stage')
    sc.world = wd
    wd.use_nodes = True
    nt = wd.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new('ShaderNodeOutputWorld')
    env = nt.nodes.new('ShaderNodeBackground')
    env.inputs['Color'].default_value = (0.80, 0.83, 0.87, 1)
    env.inputs['Strength'].default_value = 0.45
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*bb.srgb(bb.TOKENS['stage-bottom']), 1)
    ramp.color_ramp.elements[1].color = (*bb.srgb(bb.TOKENS['stage-top']), 1)
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[1].position = 0.95
    bg = nt.nodes.new('ShaderNodeBackground')
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    L(tc.outputs['Window'], sep.inputs[0])
    L(sep.outputs['Y'], ramp.inputs['Fac'])
    L(ramp.outputs['Color'], bg.inputs['Color'])
    L(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    L(env.outputs[0], mix.inputs[1])
    L(bg.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs['Surface'])

    # ---- ground: stage-bottom floor with a faint 2 m grid (speed cue), fading out with distance from the camera
    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object
    floor.name = 'stage floor'
    floor.scale = (400, 120, 1)
    floor.location = (-60, 0, 0)
    fm = bpy.data.materials.new('stage floor')
    fm.use_nodes = True
    fm.blend_method = 'BLEND'
    fm.surface_render_method = 'DITHERED'
    n2 = fm.node_tree
    n2.nodes.clear()
    o2 = n2.nodes.new('ShaderNodeOutputMaterial')
    pb = n2.nodes.new('ShaderNodeBsdfPrincipled')
    pb.inputs['Roughness'].default_value = 0.85
    try:
        pb.inputs['Specular IOR Level'].default_value = 0.2
    except KeyError:
        pass
    tco = n2.nodes.new('ShaderNodeTexCoord')
    sepw = n2.nodes.new('ShaderNodeSeparateXYZ')
    L2 = n2.links.new
    L2(tco.outputs['Object'], sepw.inputs[0])

    def gridline(axis_out, scale):               # 1 near a line, 0 elsewhere (anti-aliased by the TAA samples)
        m1 = n2.nodes.new('ShaderNodeMath')
        m1.operation = 'MULTIPLY'
        m1.inputs[1].default_value = scale
        L2(axis_out, m1.inputs[0])
        m2 = n2.nodes.new('ShaderNodeMath')
        m2.operation = 'PINGPONG'
        m2.inputs[1].default_value = 0.5
        L2(m1.outputs[0], m2.inputs[0])
        m3 = n2.nodes.new('ShaderNodeMath')
        m3.operation = 'LESS_THAN'
        m3.inputs[1].default_value = 0.012
        L2(m2.outputs[0], m3.inputs[0])
        return m3.outputs[0]
    gx = gridline(sepw.outputs['X'], 400 / 2.0)    # object coords span 1 -> 400 m in x; a line every 2 m
    gy = gridline(sepw.outputs['Y'], 120 / 2.0)
    gmax = n2.nodes.new('ShaderNodeMath')
    gmax.operation = 'MAXIMUM'
    L2(gx, gmax.inputs[0])
    L2(gy, gmax.inputs[1])
    cmix = n2.nodes.new('ShaderNodeMix')
    cmix.data_type = 'RGBA'
    cmix.inputs['A'].default_value = (*bb.srgb('#E6EAEF'), 1)
    cmix.inputs['B'].default_value = (*bb.srgb('#DEE2E8'), 1)
    L2(gmax.outputs[0], cmix.inputs['Factor'])
    # low albedo + a constant glow: the far floor matches the stage tone whatever the lights do, and the near
    # floor only brightens a little under the key light, so the contact shadow reads without a hard horizon band
    alb = n2.nodes.new('ShaderNodeMix')
    alb.data_type = 'RGBA'
    alb.blend_type = 'MULTIPLY'
    alb.inputs['Factor'].default_value = 1.0
    alb.inputs['B'].default_value = (0.12, 0.12, 0.12, 1)
    # soft contact shadow: an elliptical darkening of the floor under the aircraft, set per frame (centre, size,
    # strength); it spreads and fades with height. The lights' own soft shadows stay as well.
    geo = n2.nodes.new('ShaderNodeNewGeometry')
    vsub = n2.nodes.new('ShaderNodeVectorMath')
    vsub.operation = 'SUBTRACT'
    vdiv = n2.nodes.new('ShaderNodeVectorMath')
    vdiv.operation = 'DIVIDE'
    vlen = n2.nodes.new('ShaderNodeVectorMath')
    vlen.operation = 'LENGTH'
    one_m = n2.nodes.new('ShaderNodeMath')
    one_m.operation = 'SUBTRACT'
    one_m.use_clamp = True
    one_m.inputs[0].default_value = 1.0
    pw2 = n2.nodes.new('ShaderNodeMath')
    pw2.operation = 'POWER'
    pw2.inputs[1].default_value = 1.2
    stren = n2.nodes.new('ShaderNodeMath')
    stren.operation = 'MULTIPLY'
    inv = n2.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    shade = n2.nodes.new('ShaderNodeMix')
    shade.data_type = 'RGBA'
    shade.blend_type = 'MULTIPLY'
    shade.inputs['Factor'].default_value = 1.0
    L2(geo.outputs['Position'], vsub.inputs[0])
    L2(vsub.outputs[0], vdiv.inputs[0])
    L2(vdiv.outputs[0], vlen.inputs[0])
    L2(vlen.outputs['Value'], one_m.inputs[1])
    L2(one_m.outputs[0], pw2.inputs[0])
    L2(pw2.outputs[0], stren.inputs[0])
    L2(stren.outputs[0], inv.inputs[1])
    L2(cmix.outputs['Result'], shade.inputs['A'])
    L2(inv.outputs[0], shade.inputs['B'])
    blob_c, blob_s, blob_op = vsub.inputs[1], vdiv.inputs[1], stren.inputs[1]
    L2(shade.outputs['Result'], alb.inputs['A'])
    L2(alb.outputs['Result'], pb.inputs['Base Color'])
    L2(shade.outputs['Result'], pb.inputs['Emission Color'])
    pb.inputs['Emission Strength'].default_value = 0.74
    cam_d = n2.nodes.new('ShaderNodeCameraData')
    fade = n2.nodes.new('ShaderNodeMapRange')
    fade.inputs['From Min'].default_value = 7.0
    fade.inputs['From Max'].default_value = 20.0
    fade.inputs['To Min'].default_value = 1.0
    fade.inputs['To Max'].default_value = 0.0
    L2(cam_d.outputs['View Distance'], fade.inputs['Value'])
    L2(fade.outputs['Result'], pb.inputs['Alpha'])
    L2(pb.outputs[0], o2.inputs['Surface'])
    floor.data.materials.append(fm)


    # ---- camera and lights
    cd = bpy.data.cameras.new('cam')
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cd.lens = 50
    cd.sensor_width = 36
    cd.clip_start, cd.clip_end = 0.05, 200

    def look(ob, loc, target, up=Vector((0, 0, 1))):
        f = (Vector(target) - Vector(loc)).normalized()
        r = f.cross(up).normalized()
        u = r.cross(f)
        M = Matrix((r, u, -f)).transposed().to_4x4()
        M.translation = Vector(loc)
        ob.matrix_world = M

    lights = []
    for name, daz, el, energy, size, rgb in (('key', -50, 55, 6.5, 0.3, (1, 0.98, 0.95)),
                                             ('fill', 35, 12, 3.2, 1.2, (0.92, 0.95, 1.0)),
                                             ('rim', 170, 40, 5.0, 0.6, (1, 1, 1)),
                                             ('top', 0, 89, 1.2, 1.5, (1, 1, 1))):
        ld = bpy.data.lights.new(name, 'AREA')
        d = 2.6
        ld.energy, ld.size, ld.color = energy * d * d * 2.2, size * d, rgb
        lo = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo)
        lights.append((lo, daz, el, d))

    def cam_params(t):
        """azimuth (deg, from the flight direction -x toward +y, the starboard side), elevation, distance."""
        az = 58 + 10 * seg(t, 4.0, 8.4) - 10 * seg(t, 11.0, 15.0)
        el = 10 + 6 * seg(t, 1.5, 4.5) + 6 * seg(t, 5.0, 8.4) - 6 * seg(t, 11.0, 14.0) - 2 * seg(t, 13.5, 16.5)
        dist = 2.7 + 0.45 * seg(t, 4.6, 8.0) - 0.45 * seg(t, 11.2, 14.0)
        return az, el, dist

    def cam_target(t):
        # the camera follows a slightly lagged, low-passed copy of the pivot so it eases into moves
        acc = Vector((0, 0, 0))
        wsum = 0.0
        for k in range(-6, 7):
            tt = min(max(t + k * 0.05, 0.0), DURATION)
            x, z, *_ = state(tt)
            wgt = math.exp(-(k / 4.0) ** 2)
            acc += Vector((x, 0, z0 + z)) * wgt
            wsum += wgt
        # lead room ahead of the aircraft when it moves (it travels toward -x = screen right)
        return acc / wsum + Vector((-0.28 * speed(t) / V_CRUISE, 0, -0.05))

    def pose(t):
        x, z, theta, bank, rate, (pe, rr) = state(t)
        A = (Matrix.Translation(Vector((x, 0, z0 + z))) @ Matrix.Rotation(math.radians(bank), 4, 'X')
             @ Matrix.Rotation(math.radians(theta), 4, 'Y') @ Matrix.Translation(-pivot))
        # prop angle = integral of rate (deg); 55 deg/frame at full speed stays readable for a two-blade prop
        ang = 0.0
        steps = int(t * FPS)
        for k in range(steps):
            ang += 55.0 * state(k / FPS)[4]
        ang += 55.0 * rate * (t * FPS - steps)
        local = {}
        for p in props:
            M = (Matrix.Translation(p['hub']) @ Matrix.Rotation(math.radians(ang * p['sense']), 4, p['ax'])
                 @ Matrix.Translation(-p['hub']))
            for pid in p['parts']:
                local[pid] = M
        for pid, o in elevons.items():
            left = pid.endswith('-L')
            # trailing edge up = negative rotation about +Y; roll: left up / right down for positive rr
            dlt = -(pe + (rr if left else -rr))
            local[pid] = Matrix.Translation(o) @ Matrix.Rotation(math.radians(dlt), 4, hinge_ax) @ Matrix.Translation(-o)
        for i, ob in shown.items():
            ob.matrix_world = A @ local.get(i, Matrix()) @ rest[i]
        disc_bsdf.inputs['Alpha'].default_value = 0.16 * smooth((rate - 0.4) / 0.6)
        for i in ('disc UL', 'disc UR', 'disc LL', 'disc LR'):
            shown[i].hide_render = rate < 0.4
        # camera
        az, el, dist = cam_params(t)
        tg = cam_target(t)
        ar, er = math.radians(az), math.radians(el)
        off = Vector((-math.cos(er) * math.cos(ar), math.cos(er) * math.sin(ar), math.sin(er))) * dist
        look(cam, tg + off, tg)
        # lights relative to the camera azimuth, centred on the aircraft (render_kit._lights)
        caz = math.atan2(off.y, off.x)
        cen = Vector((x, 0, z0 + z))
        for lo, daz, lel, d in lights:
            aa, ee = caz + math.radians(daz), math.radians(lel)
            loc = cen + Vector((math.cos(ee) * math.cos(aa), math.cos(ee) * math.sin(aa), math.sin(ee))) * d
            look(lo, loc, cen, Vector((0, 0, 1)) if lel < 85 else Vector((1, 0, 0)))
        hgt = max(0.0, z0 + z - 0.25)
        spread = 1.0 + 0.6 * hgt
        foot_x = 0.55 + 0.15 * (1 - theta / 90.0)        # chord-wise footprint grows as it lies down
        blob_s.default_value = (foot_x * spread, 0.9 * spread, 1.0)
        blob_c.default_value = (x - 0.03, 0.0, 0.0)
        blob_op.default_value = 0.5 * math.exp(-hgt / 1.6)
        bpy.context.view_layer.update()

    frames = [int(f) for f in a.frames.split(',') if f.strip()] if a.frames else list(range(NFRAMES))
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    for f in frames:
        pose(f / FPS)
        sc.render.filepath = os.path.join(a.out, 'raw_%04d.png' % f)
        bpy.ops.render.render(write_still=True)
        print('FRAME %d %.1f s' % (f, time.time() - t0), flush=True)
    print('RENDER_TOTAL %.1f s for %d frames' % (time.time() - t0, len(frames)))


def blender_encode(argv):
    """PNG sequence -> H.264 MP4 with Blender's bundled FFmpeg (VSE)."""
    import argparse
    import bpy
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--kbps', type=int, default=2200)
    a = ap.parse_args(argv)
    names = sorted(n for n in os.listdir(a.src) if n.startswith('lab_') and n.endswith('.png'))
    sc = bpy.context.scene
    sc.sequence_editor_create()
    st = sc.sequence_editor.sequences.new_image('frames', os.path.join(a.src, names[0]), 1, 1)
    for n in names[1:]:
        st.elements.append(n)
    sc.frame_start, sc.frame_end = 1, len(names)
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'FFMPEG'
    ff = sc.render.ffmpeg
    ff.format = 'MPEG4'
    ff.codec = 'H264'
    ff.constant_rate_factor = 'NONE'
    ff.video_bitrate = a.kbps
    ff.maxrate = int(a.kbps * 1.5)
    ff.buffersize = 2000
    ff.gopsize = FPS
    ff.ffmpeg_preset = 'GOOD'
    ff.audio_codec = 'NONE'
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
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts'),
            '/usr/share/fonts', '/Library/Fonts']
    for n in names:
        for d in dirs:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def overlay(src_png, dst_png, f):
    from PIL import Image, ImageDraw
    t = f / FPS
    im = Image.open(src_png).convert('RGBA')
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ink, hi, muted = (18, 22, 25), (194, 84, 10), (107, 114, 128)
    sans = ['IBMPlexSans-Medium.ttf', 'IBMPlexSans-SemiBold.ttf', 'seguisb.ttf', 'segoeui.ttf', 'arial.ttf']
    mono = ['IBMPlexMono-Medium.ttf', 'CascadiaMono.ttf', 'consola.ttf', 'cour.ttf']
    f_title = _font(sans, 30)
    f_mono = _font(mono, 15)
    f_head = _font(['seguisb.ttf', 'segoeui.ttf', 'arial.ttf'], 17)
    i = phase_at(t)
    a0, a1, label = PHASES[i]
    # label fade: in over 0.25 s at the phase start (except the first), out over 0.2 s before the next phase
    alpha = 1.0
    if i > 0:
        alpha = min(alpha, (t - a0) / 0.25)
    if i < len(PHASES) - 1:
        alpha = min(alpha, (a1 - t) / 0.2)
    alpha = max(0.0, min(1.0, alpha))
    # top-left title
    d.text((36, 28), 'K09-L quad tailsitter', font=f_head, fill=ink + (230,))
    d.text((36, 52), 'HOW IT FLIES', font=f_mono, fill=muted + (230,))
    # lower third panel
    x0, y1 = 36, H - 40
    tw = d.textlength(label, font=f_title)
    pw = max(560, int(tw) + 110)
    ph = 92
    y0 = y1 - ph
    d.rounded_rectangle((x0, y0, x0 + pw, y1), radius=8, fill=(255, 255, 255, 236), outline=(203, 210, 219, 255))
    d.rectangle((x0, y0 + 14, x0 + 4, y1 - 14), fill=hi + (255,))
    d.text((x0 + 22, y0 + 14), '%d / %d' % (i + 1, len(PHASES)), font=f_mono, fill=hi + (255,))
    # phase dots after the counter
    dx = x0 + 22 + int(d.textlength('%d / %d' % (i + 1, len(PHASES)), font=f_mono)) + 14
    for k in range(len(PHASES)):
        cx, cy = dx + k * 16, y0 + 24
        if k < i:
            d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=ink + (200,))
        elif k == i:
            d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=hi + (255,))
        else:
            d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), outline=muted + (200,), width=1)
    tl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(tl).text((x0 + 22, y0 + 38), label, font=f_title, fill=ink + (int(255 * alpha),))
    lay = Image.alpha_composite(lay, tl)
    d = ImageDraw.Draw(lay)
    # progress bar inside the panel bottom
    bx0, bx1, by = x0 + 22, x0 + pw - 22, y1 - 10
    d.rounded_rectangle((bx0, by - 2, bx1, by + 1), radius=2, fill=(220, 225, 232, 255))
    px = bx0 + (bx1 - bx0) * min(1.0, t / DURATION)
    d.rounded_rectangle((bx0, by - 2, max(bx0 + 3, px), by + 1), radius=2, fill=hi + (255,))
    for a, b, _ in PHASES[1:]:
        tx = bx0 + (bx1 - bx0) * a / DURATION
        d.line((tx, by - 4, tx, by + 3), fill=(255, 255, 255, 255), width=2)
    im = Image.alpha_composite(im, lay).convert('RGB')
    im.save(dst_png, optimize=False, compress_level=1)
    return im


# =====================================================================================================================
# driver
# =====================================================================================================================
def run(cmd):
    print('>', ' '.join('"%s"' % c if ' ' in c else c for c in cmd), flush=True)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    for line in p.stdout.splitlines():
        if line.startswith(('FRAME', 'RENDER_TOTAL', 'ENCODED', 'Traceback', 'Error', '  File')) or 'Error' in line:
            print('   ', line, flush=True)
    if p.returncode != 0:
        print(p.stdout[-4000:])
        raise SystemExit('blender failed')


def driver():
    import argparse
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender', default=os.environ.get('BLENDER', BLENDER_DEFAULT))
    ap.add_argument('--samples', type=int, default=32)
    ap.add_argument('--frames', default='', help='comma list of frames: test render only (no encode)')
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'k09l_anim'))
    ap.add_argument('--skip-render', action='store_true')
    ap.add_argument('--kbps', type=int, default=2200)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(a.work, exist_ok=True)
    me = os.path.abspath(__file__)
    if not a.skip_render:
        cmd = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', a.work,
               '--samples', str(a.samples)]
        if a.frames:
            cmd += ['--frames', a.frames]
        run(cmd)
    t_render = time.time() - t0
    frames = [int(f) for f in a.frames.split(',')] if a.frames else list(range(NFRAMES))
    for f in frames:
        overlay(os.path.join(a.work, 'raw_%04d.png' % f), os.path.join(a.work, 'lab_%04d.png' % f), f)
    if a.frames:
        print('test frames in', a.work)
        return
    run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work, '--out', OUT_MP4,
         '--kbps', str(a.kbps)])
    # poster: the clean mid-transition key frame with its label
    Image.open(os.path.join(a.work, 'lab_%04d.png' % POSTER_FRAME)).save(OUT_POSTER, optimize=True)
    # GIF: 720 px wide, 10 fps (every 3rd frame), one shared 128-colour palette, no dither (dither noise on the
    # moving floor costs ~60 % more bytes); keeps it under GitHub's 10 MB inline limit
    gw, gh = 720, int(round(720 * H / W))
    gif_fps = 10
    picks = [int(round(k * FPS / gif_fps)) for k in range(int(DURATION * gif_fps))]
    ims = [Image.open(os.path.join(a.work, 'lab_%04d.png' % min(p, NFRAMES - 1))).resize((gw, gh), Image.LANCZOS)
           for p in picks]
    strip = Image.new('RGB', (gw, gh * 6))
    for k in range(6):
        strip.paste(ims[k * len(ims) // 6], (0, gh * k))
    pal = strip.quantize(colors=128, method=Image.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in ims]
    q[0].save(OUT_GIF, save_all=True, append_images=q[1:], duration=int(1000 / gif_fps), loop=0, optimize=True,
              disposal=1)
    for p in (OUT_MP4, OUT_GIF, OUT_POSTER):
        print('%-28s %7.2f MB' % (os.path.basename(p), os.path.getsize(p) / 1e6))
    print('render %.1f min, total %.1f min' % (t_render / 60, (time.time() - t0) / 60))


if __name__ == '__main__':
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
        try:
            if argv and argv[0] == 'encode':
                blender_encode(argv[1:])
            else:
                blender_render(argv[1:] if argv and argv[0] == 'render' else argv)
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        driver()
