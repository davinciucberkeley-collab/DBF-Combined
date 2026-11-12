"""render_build.py - the K09-L build sequence as animation, one clip per BUILD-GUIDE stage plus the full film.

    python redesign/showcase/animation/render_build.py [--frames 0,120] [--work DIR] [--skip-render]

Run with the system Python (needs Pillow). Three steps, the same as render_animation.py:
  1. render   Blender (headless, Workbench) builds the aircraft from redesign/subsystems/*/fusion/*.py through
              redesign/blender/blender_backend.py: the same CAD as the GLB and the collision check, so every hole,
              seat and routed wire is as checked. Per BUILD-GUIDE stage, the parts already built stay in place and the
              stage's parts fly in to their final position (tinted while they move); the stage's wires are laid one
              run after another. Raw PNG frames go to --work.
  2. overlay  Pillow adds the stage title, two instruction lines and the stage progress bar.
  3. encode   Blender's FFmpeg writes build/k09l-build.mp4 (all stages) and build/stage-NN.mp4 (one per stage),
              plus build/stage-NN.png (the stage's last frame) for the build guide.

Stage contents (which parts and wires belong where) follow BUILD-GUIDE.md stages 2-11; a part matched by no stage
appears in the last one. Blender path: --blender or $BLENDER.
"""
import fnmatch
import json
import math
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REDESIGN = os.path.dirname(os.path.dirname(HERE))
BL = os.path.join(REDESIGN, 'blender')
BLENDER_DEFAULT = r'C:/Users/dillo/tools/blender/blender-4.2.3-windows-x64/blender.exe'
OUT = os.path.join(HERE, 'build')

FPS = 30
W, H = 1280, 720
T_MOVE, T_FLY, T_WIRE, T_HOLD = 0.8, 1.9, 0.18, 1.3      # s: camera move, part fly-in, per wire run, hold
T_LATE = 1.2                                             # s: parts that go on after the stage's wires
LATE = ('WNG-003', 'WNG-020', 'POD-003')                 # tape skin and label over the harness; hatch after avionics

# (stage, title, two instruction lines, part globs, wire edge globs, camera azimuth deg, elevation deg)
STAGES = [
    (2, 'Wing core and spar', ['Hot-wire the XPS core; bond the CF spar and its PETG plugs in the 22.4 mm bore.',
                                'Pocket and bond the two through-core blocks; lay the lip beads.'],
     ['WNG-001', 'WNG-002', 'WNG-004*', 'WNG-005*', 'FIN-004*', 'WNG-006*', 'WNG-007'], [], -55, 32),
    (3, 'Elevon panels', ['Cut the four panels; bond the CF torque tubes in their routed grooves.',
                          'Hinge each panel on the upper skin line with packing tape.'],
     ['WNG-011*', 'WNG-012*', 'MEC-009*', 'MEC-010*'], [], -130, 35),
    (4, 'Fins on the motor tubes', ['Laminate the half-fins and bond them to the motor tubes through the blocks.',
                                    'Edge strips, pins, station collars, braces, anchors and ESC pads.'],
     ['FIN-002*', 'FIN-006*', 'FIN-001*', 'FIN-011*', 'FIN-012*', 'FIN-008*', 'FIN-009*', 'FIN-010*', 'FIN-007*'],
     [], -35, 22),
    (5, 'Pod and power stack', ['Build the pod: floor, tray, guides, stops and the carry handle with its GPS mast.',
                                'Power frame on spacers: board, bus bars, AS150U aircraft half, main jumpers.'],
     ['POD-001', 'POD-002', 'POD-004', 'POD-005', 'POD-006', 'POD-007', 'POD-008', 'POD-010', 'POD-011', 'POD-012',
      'PWR-002', 'PWR-003', 'PWR-004', 'PWR-006', 'PWR-1*'], ['E-HRN-11', 'E-HRN-12'], -60, 48),
    (6, 'Harness, then skin', ['ESC pairs and signal leads in the grooves, through P1, P1s and the fin grommets.',
                               'XT30U pairs tied in the pod; then tape-skin the wing over the routed harness.'],
     ['HRN-*', 'PWR-008*', 'WNG-003', 'WNG-020'],
     ['E-HRN-13', 'E-HRN-14', 'E-HRN-15', 'E-HRN-16', 'E-HRN-24', 'E-HRN-25', 'E-HRN-26', 'E-HRN-27',
      'E-HRN-34', 'E-HRN-35', 'E-HRN-36', 'E-HRN-37'], -40, 40),
    (7, 'Servos, linkage and horns', ['Servos into their frames under the wing; arms, pushrods and clevises.',
                                      'Horns on the torque tubes, bridge rods, frame covers; servo leads to the JR row.'],
     ['MEC-001*', 'MEC-002*', 'MEC-003*', 'MEC-004*', 'MEC-005*', 'MEC-006*', 'MEC-007*', 'MEC-008*', 'MEC-011*',
      'MEC-012*'], ['E-HRN-28', 'E-HRN-29'], 150, -35),
    (8, 'Motor mounts, motors and props', ['Slit-collar mounts on the tubes, keyed to the station collars; pinch bolts.',
                                           'Motors, phase leads to the ESCs, adapters and props (check rotation).'],
     ['FIN-003*', 'FIN-1*', 'PRP-*'], ['E-HRN-17', 'E-HRN-18', 'E-HRN-19', 'E-HRN-20'], -25, 18),
    (9, 'Avionics', ['FC on gel cubes, receiver, airspeed sensor, GPS on the mast.',
                     'Power-board ribbon, RX, airspeed and GPS leads to the FC; hatch on.'],
     ['AVN-*', 'POD-003'], ['E-HRN-23', 'E-HRN-30', 'E-HRN-31', 'E-HRN-32'], -70, 52),
    (10, 'Feet and corner caps', ['Shoes, pistons and crush cartridges on the four fin tips.',
                                  'TPU corner caps on the wing tips.'],
     ['GER-*'], [], -20, 15),
    (11, 'Pack in, weigh and balance', ['Strap the pack in at its station; mate the AS150U.',
                                        'Weigh, check the CG on its marks, then the thrust stand and first hover.'],
     ['PWR-001'], ['E-HRN-10'], -50, 30),
]


def plan():
    """Frame timeline per stage: (stage index, f0, f_move_end, f_fly_end, f_wires_end, f1)."""
    out, f = [], 0
    for i, st in enumerate(STAGES):
        n_w = len(st[4])
        a = f
        b = a + int(T_MOVE * FPS)
        c = b + int(T_FLY * FPS)
        d = c + int(n_w * T_WIRE * FPS) + (int(0.4 * FPS) if n_w else 0)
        if any(g in LATE for g in st[3]):
            d += int(T_LATE * FPS)
        e = d + int(T_HOLD * FPS)
        out.append((i, a, b, c, d, e))
        f = e
    return out, f


TIMELINE, NFRAMES = plan()


def stage_at(f):
    for i, a, b, c, d, e in TIMELINE:
        if a <= f < e:
            return i
    return len(STAGES) - 1


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# =====================================================================================================================
# render (inside Blender)
# =====================================================================================================================
def blender_render(argv):
    import argparse
    import bpy
    from mathutils import Vector
    sys.path[:0] = [BL, os.path.join(REDESIGN, 'fusion')]
    import blender_backend as bb
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    be, ctx, graph, results = bb.build(False, None, 'material', log=lambda *x: None)
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_WORKBENCH'
    sh = scn.display.shading
    sh.light, sh.color_type = 'STUDIO', 'OBJECT'
    sh.show_cavity, sh.cavity_type = True, 'BOTH'
    sh.show_object_outline, sh.object_outline_color = True, (0.12, 0.14, 0.16)
    sh.background_type, sh.background_color = 'VIEWPORT', (0.93, 0.94, 0.95)
    scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = W, H, 100
    scn.render.film_transparent = False
    scn.view_settings.view_transform = 'Standard'
    scn.render.image_settings.file_format = 'PNG'
    for o in bpy.data.objects:
        if o.type == 'EMPTY':
            o.hide_render = True

    def base_colour(ob):
        m = ob.data.materials[0] if ob.data and getattr(ob.data, 'materials', None) else None
        return tuple(m.diffuse_color) if m is not None else (0.8, 0.8, 0.82, 1.0)

    # stage of every part and wire
    items = []                                           # (ob, stage idx, kind, order in stage)
    last = len(STAGES) - 1
    for pid, ob in be.objects.items():
        c = ctx.components.get(pid)
        if be.is_proxy(pid) or (c is not None and not c.flight):
            ob.hide_render = True
            continue
        si = next((i for i, s in enumerate(STAGES) if any(fnmatch.fnmatch(pid, g) for g in s[3])), last)
        items.append((ob, si, 'part', pid))
    for eid, ob in be.wires.items():
        si = next((i for i, s in enumerate(STAGES) if any(fnmatch.fnmatch(eid, g) for g in s[4])), None)
        if si is None:
            ob.hide_render = True
            continue
        items.append((ob, si, 'wire', eid))

    def bbox(obs):
        pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
        if not pts:
            return Vector((0.05, 0, 0)), 0.5
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        return (lo + hi) / 2, max((hi - lo).length, 0.12)

    centre_all, _ = bbox([o for o, si, k, _ in items if k == 'part'])
    # cameras: per stage target and distance from its new parts, direction from the stage's azimuth / elevation
    cams = []
    for i, st in enumerate(STAGES):
        new = [o for o, si, k, _ in items if si == i]
        c, size = bbox(new) if new else (centre_all, 0.6)
        if i == len(STAGES) - 1:
            c, size = centre_all, 1.2
        size = min(max(size, 0.30), 1.35)
        az, el = math.radians(st[5]), math.radians(st[6])
        d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        cams.append((c, c + d * (size * 1.25 + 0.12)))

    # per-item motion
    finals = {o.name: o.matrix_world.translation.copy() for o, *_ in items}
    colours = {o.name: base_colour(o) for o, *_ in items}
    order = {}
    for o, si, k, key in items:
        order.setdefault((si, k), []).append(o)
    for (si, k), obs in order.items():
        obs.sort(key=lambda o: o.name)
    for (si, k) in list(order):
        if k == 'part':
            order[(si, k)] = [o for o in order[(si, k)] if o.name not in LATE]

    OFFS = {}

    def offset(o, si):
        if o.name in OFFS:
            return OFFS[o.name]
        c, size = bbox([o])
        if size > 0.5:                                    # core, spar, skin: rise from below / settle from above
            OFFS[o.name] = Vector((0, 0, -0.18)) if STAGES[si][0] <= 3 else Vector((0, 0, 0.12))
            return OFFS[o.name]
        v = c - centre_all
        v.z += 0.15 * (1 if c.z >= 0 else -1)
        OFFS[o.name] = v.normalized() * 0.22
        return OFFS[o.name]

    hi_col = (0.95, 0.42, 0.08, 1.0)

    def _place(o, v):
        m = o.matrix_world.copy()
        m.translation = v
        o.matrix_world = m
    for o, si, k, key in items:
        if k == 'part':
            offset(o, si)
    frames = [int(x) for x in a.frames.split(',')] if a.frames else list(range(NFRAMES))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.lens, cam.data.clip_start, cam.data.clip_end = 42, 0.005, 20
    t0 = time.time()
    for f in frames:
        si_now = stage_at(f)
        _, fa, fb, fc, fd, fe = TIMELINE[si_now]
        # camera: ease from the previous stage's framing during the move
        p_c, p_l = cams[max(si_now - 1, 0)]
        n_c, n_l = cams[si_now]
        u = smooth((f - fa) / max(fb - fa, 1)) if si_now > 0 else 1.0
        tgt = p_c.lerp(n_c, u)
        loc = p_l.lerp(n_l, u)
        if si_now == len(STAGES) - 1:                     # last stage: slow orbit round the finished aircraft
            ang = 0.6 * smooth((f - fb) / max(fe - fb, 1))
            off = loc - tgt
            loc = tgt + Vector((off.x * math.cos(ang) - off.y * math.sin(ang),
                                off.x * math.sin(ang) + off.y * math.cos(ang), off.z))
        cam.location = loc
        cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
        for o, si, k, key in items:
            if si > si_now:
                o.hide_render = True
                continue
            o.hide_render = False
            base = colours[o.name]
            if si < si_now:
                _place(o, finals[o.name])
                o.color = base
                continue
            if k == 'part' and key in LATE:
                fl = fd - int(T_LATE * FPS)
                p = smooth((f - fl) / (T_LATE * FPS))
                o.hide_render = f < fl
                _place(o, finals[o.name] + offset(o, si) * (1 - p))
                tint = 1 - smooth((f - fd) / (0.8 * FPS))
            elif k == 'part':
                grp = order[(si, 'part')]
                j = grp.index(o)
                stagger = 0.35 * (j / max(len(grp) - 1, 1))
                p = smooth(((f - fb) / FPS / T_FLY - stagger) / (1 - 0.35))
                o.hide_render = f < fb + stagger * T_FLY * FPS
                _place(o, finals[o.name] + offset(o, si) * (1 - p))
                tint = 1 - smooth((f - fc) / (0.8 * FPS))
            else:
                grp = order[(si, 'wire')]
                j = grp.index(o)
                fw = fc + int(j * T_WIRE * FPS)
                o.hide_render = f < fw
                _place(o, finals[o.name])
                tint = 1 - smooth((f - fw) / (0.8 * FPS))
            o.color = tuple(base[i] * (1 - 0.75 * tint) + hi_col[i] * 0.75 * tint for i in range(4))
        scn.render.filepath = os.path.join(a.out, 'raw_%04d.png' % f)
        bpy.ops.render.render(write_still=True)
        with open(os.path.join(a.out, 'raw_%04d.json' % f), 'w') as fp:
            json.dump({'stage': si_now}, fp)
        if f % 30 == 0:
            print('FRAME %d / %d  %.0f s' % (f, NFRAMES, time.time() - t0), flush=True)
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
    a = ap.parse_args(argv)
    names = sorted(n for n in os.listdir(a.src) if n.startswith('lab_') and n.endswith('.png')
                   and a.first <= int(n[4:8]) <= a.last)
    sc = bpy.context.scene
    sc.sequence_editor_create()
    st = sc.sequence_editor.sequences.new_image('frames', os.path.join(a.src, names[0]), 1, 1)
    for n in names[1:]:
        st.elements.append(n)
    sc.frame_start, sc.frame_end = 1, len(names)
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'FFMPEG'
    ff = sc.render.ffmpeg
    ff.format, ff.codec, ff.constant_rate_factor = 'MPEG4', 'H264', 'NONE'
    ff.video_bitrate, ff.maxrate, ff.buffersize, ff.gopsize = a.kbps, int(a.kbps * 1.5), 2000, FPS
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


def overlay(src_png, dst_png, f):
    from PIL import Image, ImageDraw
    im = Image.open(src_png).convert('RGBA')
    i = stage_at(f)
    num, title, lines = STAGES[i][0], STAGES[i][1], STAGES[i][2]
    _, fa, fb, fc, fd, fe = TIMELINE[i]
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
    # stage progress: one tick per stage, the current one in the highlight colour
    n = len(STAGES)
    x0, y0, step = W - 36 - (n - 1) * 30, 40, 30
    for k in range(n):
        x = x0 + k * step
        col = hi if k == i else (ink if k < i else (200, 204, 210))
        d.ellipse((x - 6, y0 - 6, x + 6, y0 + 6), fill=col + (255,))
        d.text((x - 7, y0 + 10), str(STAGES[k][0]), font=f_mono, fill=(muted if k != i else hi) + (255,))
    # lower third
    A = int(255 * alpha)
    d.rounded_rectangle((28, H - 150, W - 28, H - 24), radius=10, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(205, 209, 214, A), width=1)
    d.rectangle((28, H - 150, 34, H - 24), fill=hi + (A,))
    d.text((52, H - 140), 'STAGE %d' % num, font=f_mono, fill=hi + (A,))
    d.text((52, H - 118), title, font=f_title, fill=ink + (A,))
    for k, ln in enumerate(lines):
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
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    me = os.path.abspath(__file__)
    if not a.skip_render:
        cmd = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', a.work]
        if a.frames:
            cmd += ['--frames', a.frames]
        run(cmd)
    frames = [int(x) for x in a.frames.split(',')] if a.frames else list(range(NFRAMES))
    for f in frames:
        overlay(os.path.join(a.work, 'raw_%04d.png' % f), os.path.join(a.work, 'lab_%04d.png' % f), f)
    if a.frames:
        print('test frames in', a.work)
        return
    run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work,
         '--out', os.path.join(OUT, 'k09l-build.mp4')])
    for i, fa, fb, fc, fd, fe in TIMELINE:
        num = STAGES[i][0]
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work,
             '--out', os.path.join(OUT, 'stage-%02d.mp4' % num), '--first', str(fa), '--last', str(fe - 1)])
        Image.open(os.path.join(a.work, 'lab_%04d.png' % (fe - 1))).save(os.path.join(OUT, 'stage-%02d.png' % num),
                                                                         optimize=True)
    for n in sorted(os.listdir(OUT)):
        print('%-22s %6.2f MB' % (n, os.path.getsize(os.path.join(OUT, n)) / 1e6))
    print('%d frames, %.1f s of film, total %.1f min' % (NFRAMES, NFRAMES / FPS, (time.time() - t0) / 60))


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
