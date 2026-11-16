"""render_build_a.py - the concept A build sequence as animation: the steps of qp/A/cad/a_assembly_plan.py (41 with the D-198 wire-laying steps) grouped into
10 stages, one clip + one still per stage and the full film.

    python redesign/showcase/concept-a/render_build_a.py               # render + overlay + encode everything
    python redesign/showcase/concept-a/render_build_a.py --preview     # half size, every 3rd frame, no encode
    python redesign/showcase/concept-a/render_build_a.py --frames 40,300   # test frames only

Run with the system Python (needs Pillow). Three steps, as render_build.py (K09-L):
  1. render   Blender (EEVEE) builds the real concept A CAD from redesign/qp/A/cad/model through
              redesign/blender/blender_backend.py (98 parts incl. the lofted APC props: the same bodies as
              concept-a.glb) and poses each part per frame. Frames that are identical to the previous one are copied.
  2. overlay  Pillow: stage title, step id + caption, step counter, progress bar.
  3. encode   Blender's FFmpeg (VSE): a-build.mp4 + stage-NN.mp4 (H.264); stage-NN.webp = last frame of each stage.

Motions: every step's parts come in along the direction and over the travel of a_assembly_plan.STEPS, which
a_assembly.py checked (swept path, no part interpenetration, support and wire order; out/ASSEMBLY.md: 35 steps, 0 blocked).
For legibility a motion shorter than MIN_TRAVEL_MM is started MIN_TRAVEL_MM away along the same line; the part of
that line beyond the checked travel is approach in free air and is NOT part of the swept check. Steps with travel 0
(A1 core on the bench, E5 strap) simply appear, highlighted. The moving parts are tinted orange. Wires appear (highlighted)
as soon as both of their end parts are on. Parts that the plan does not place are not shown. Skin tape, hinge tape and
epoxy fillets are not drawn (as in the plan).
Outputs: redesign/showcase/concept-a/animation/.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
REDESIGN = os.path.dirname(SHOW)
BL = os.path.join(REDESIGN, 'blender')
ANIM = os.path.join(SHOW, 'animation')
CAD_A = os.path.join(REDESIGN, 'qp', 'A', 'cad')
MODEL_A = os.path.join(CAD_A, 'model')
BLENDER_DEFAULT = r'C:/Users/dillo/tools/blender/blender-4.5.14-windows-x64/blender.exe'
OUT = os.path.join(HERE, 'animation')

FPS = 24
W, H = 1280, 720
T_CAM, T_CAM_STAGE = 0.45, 0.8       # s camera move before a step / before the first step of a stage
T_SETTLE, T_STAGE_HOLD = 0.2, 0.6    # s hold after a step / at the end of a stage
T_END = 2.5                          # s final hold with the whole aircraft
MIN_TRAVEL_MM = 70.0                 # visual minimum approach (see the module docstring)
MAX_TRAVEL_MM = 450.0                # long insertions (spar 700, tubes 500) start 450 mm away
T_MOVE = {'long': 1.1, 'short': 0.8, 'appear': 0.6}

STAGES = [
    ('Wing core and spar', ['A1', 'A2', 'A3', 'A4', 'A5']),
    ('Cage unit: motor leads threaded, motors, props', ['B0', 'B1']),
    ('Rib saddles, pack tray, hinge dampers', ['B2', 'B3', 'B4']),
    ('Fin ribs and rib fairings', ['C1', 'C1a']),
    ('Elevons, balance strips, lens caps', ['C2', 'C2a', 'C2b']),
    ('Fins: fairings, root blocks, tubes', ['C3', 'C4', 'C5', 'C6']),
    ('Landing feet', ['C7', 'C8', 'C9']),
    ('Servos, pushrods, horns, lead threading', ['D1', 'D0', 'D2', 'D2a', 'D3', 'D4', 'D5', 'D5b']),
    ('Avionics: pitot, plate, ESC, FC, leads', ['E1', 'E2', 'E3', 'E3a', 'E3b']),
    ('Pack, XT60, strap, phase leads, bay cover', ['E4', 'E4a', 'E4b', 'E5', 'E6', 'E7']),
]
# per-step camera direction (azimuth from the nose, 90 = left; elevation) where the default (38, 30) hides the part
VIEW = {'B1': (-40, -22), 'B2': (35, -28), 'C2b': (35, -30), 'C8': (60, 8), 'C9': (60, 12), 'C7': (60, 12),
        'C6': (50, 14), 'D2a': (30, 40), 'E1': (-20, 25), 'A2': (20, 30), 'A5': (-30, 30), 'A1': (38, 30)}
DEFAULT_VIEW = (38, 30)


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


def load_plan():
    sys.path.insert(0, CAD_A)
    import a_assembly_plan as ap
    return [dict(id=s[0], caption=s[1], parts=list(s[2]), dir=s[3], travel=float(s[4]), edges=list(s[6]) if len(s) > 6 else []) for s in ap.STEPS]


# D-198 marker steps (threading / laying wires place no part): the camera frames these parts instead
MARKER_FOCUS = {'B0': ['WNG-001', 'WNG-002'], 'D0': ['MEC-001-R', 'WNG-001'], 'E3b': ['AVN-002', 'PRP-003', 'AVN-001'],
                'E4b': ['HRN-002', 'PWR-001', 'CGE-008'], 'E6': ['PRP-003', 'AVN-001', 'CGE-001']}


def timeline():
    """Pure schedule: list of step dicts with times, and the total number of frames."""
    plan = {s['id']: s for s in load_plan()}
    t, rows = 0.4, []
    for si, (title, ids) in enumerate(STAGES):
        for k, sid in enumerate(ids):
            s = dict(plan[sid])
            tr = min(MAX_TRAVEL_MM, max(MIN_TRAVEL_MM, s['travel'])) if s['dir'] else 0.0
            s['visual_mm'] = tr
            s['stage'] = si
            s['first_in_stage'] = (k == 0)
            s['t_cam0'] = t
            t += T_CAM_STAGE if k == 0 else T_CAM
            s['t_mv0'] = t
            t += T_MOVE['appear'] if not s['dir'] else (T_MOVE['long'] if tr > 200 else T_MOVE['short'])
            s['t_mv1'] = t
            t += T_SETTLE
            s['t_end'] = t
            rows.append(s)
        t += T_STAGE_HOLD
        rows[-1]['t_stage_end'] = t
    return rows, t + T_END


def frame_info(rows, total, f):
    """(stage index, step row, step number 1-based, progress 0..1) for the overlay of frame f."""
    t = f / FPS
    cur = rows[0]
    for r in rows:
        if t >= r['t_cam0']:
            cur = r
    return cur['stage'], cur, rows.index(cur) + 1, min(1.0, t / total)


def stage_frames(rows, total):
    """{stage: (first frame, last frame)}; a stage runs from its first camera move to the next stage's."""
    out = {}
    for si in range(len(STAGES)):
        rs = [r for r in rows if r['stage'] == si]
        f0 = int(rs[0]['t_cam0'] * FPS)
        f1 = int(rs[-1]['t_stage_end'] * FPS) - 1
        out[si] = (f0, min(f1, int(total * FPS) - 1))
    return out


# =====================================================================================================================
# Blender worker
# =====================================================================================================================
def blender_render(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='')
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--samples', type=int, default=12)
    ap.add_argument('--scale', type=float, default=1.0)
    a = ap.parse_args(argv)
    sys.path.insert(0, BL)
    sys.path.insert(0, ANIM)
    import bpy
    import blender_backend as bb
    import render_animation as ra
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Matrix, Vector

    rows, total = timeline()
    nframes = int(total * FPS)
    be, ctx, graph, _ = bb.build(False, MODEL_A, log=lambda *x: None)
    bb.solid_tape(be, '#AEB9C6')
    items = dict(be.objects)
    items.update(be.wires)
    placed_ids = {p for r in rows for p in r['parts']}
    sc = bpy.context.scene
    for i, ob in items.items():
        ob.hide_render = ob.hide_viewport = True
    rest = {i: ob.matrix_world.copy() for i, ob in items.items()}
    unplaced = sorted(i for i in be.objects if i not in placed_ids)
    print('PARTS in scene %d, in plan %d, not in plan: %s' % (len(be.objects), len(placed_ids), unplaced), flush=True)

    def bbox(pids, shift=None):
        pts = []
        for p in pids:
            ob = items[p]
            M = ob.matrix_world.copy()
            vs = ob.data.vertices
            st = max(1, len(vs) // 400)
            for k in range(0, len(vs), st):
                w = rest[p] @ vs[k].co
                pts.append(w + (shift or Vector()))
        lo = Vector([min(q[i] for q in pts) for i in range(3)])
        hi = Vector([max(q[i] for q in pts) for i in range(3)])
        return lo, hi

    # wires: appear once both end parts are on (the step that completes the pair)
    done_at = {}
    for r in rows:
        for p in r['parts']:
            done_at[p] = r['id']
    order = {r['id']: k for k, r in enumerate(rows)}
    wire_step = {}
    laid = {e: r['id'] for r in rows for e in r['edges']}      # D-198: the step that lays (solders / mates) each wire
    for e, ob in be.wires.items():
        ends = [ob.get('part_a'), ob.get('part_b')]
        ks = [order[done_at[x]] for x in ends if x in done_at]
        wire_step[e] = laid.get(e) or (rows[max(ks)]['id'] if ks else rows[-1]['id'])
    print('WIRES', {e: wire_step[e] for e in wire_step}, flush=True)

    # per-step camera. First step of a stage: wide shot of everything placed so far plus the moving parts; the other steps:
    # closer on the step's parts (start and seat positions) with at least MIN_HALF m of context around them.
    MIN_HALF = 0.16
    TAN_H, TAN_V = 18.0 / 50.0, 18.0 * H / W / 50.0

    def fit(lo, hi, az, el):
        """Camera centre and distance that frame the box (lo, hi) in the upper part of the 16:9 frame (the lower-third
        panel covers the bottom quarter)."""
        ar, er = math.radians(az), math.radians(el)
        view = Vector((-math.cos(er) * math.cos(ar), -math.cos(er) * math.sin(ar), math.sin(er)))
        right = view.cross(Vector((0, 0, 1)))
        right = right.normalized() if right.length > 1e-6 else Vector((0, 1, 0))
        up = right.cross(view).normalized()
        ctr = (lo + hi) / 2
        cs = [Vector((x, y, z)) - ctr for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
        ur = max(abs(c.dot(right)) for c in cs)
        vr = max(abs(c.dot(up)) for c in cs)
        dr = max(abs(c.dot(view)) for c in cs)
        dist = max(ur / (TAN_H * 0.97), vr / (TAN_V * 0.70)) + 0.35 * dr
        tgt = ctr - up * (0.11 * 2 * dist * TAN_V)          # subject sits above the panel
        return tgt, dist

    placed_so_far = []
    cams = {}
    for r in rows:
        d = Vector(r['dir']) if r['dir'] else Vector()
        shift = -d * r['visual_mm'] / 1000.0
        parts = [p for p in (r['parts'] or MARKER_FOCUS.get(r['id'], [])) if p in items]
        lo, hi = bbox(parts)
        lo2, hi2 = bbox(parts, shift)
        lo = Vector([min(lo[i], lo2[i]) for i in range(3)])
        hi = Vector([max(hi[i], hi2[i]) for i in range(3)])
        placed_so_far += [p for p in parts if p in r['parts']]
        if r['first_in_stage']:
            plo, phi = bbox(placed_so_far)
            lo = Vector([min(lo[i], plo[i]) for i in range(3)])
            hi = Vector([max(hi[i], phi[i]) for i in range(3)])
        c0 = (lo + hi) / 2
        lo = Vector([min(lo[i], c0[i] - MIN_HALF) for i in range(3)])
        hi = Vector([max(hi[i], c0[i] + MIN_HALF) for i in range(3)])
        az, el = VIEW.get(r['id'], DEFAULT_VIEW)
        tgt, dist = fit(lo, hi, az, el)
        cams[r['id']] = (tgt, az, el, dist)
    full_lo, full_hi = bbox(sorted(placed_ids))
    full_c = (full_lo + full_hi) / 2
    tgt, dist = fit(full_lo, full_hi, 38, 26)
    cams['END'] = (tgt, 38, 26, dist * 1.05)
    zmin_all = full_lo.z

    # scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    w, h = int(W * a.scale), int(H * a.scale)
    blob_c, blob_s, blob_op = ra.make_stage(sc, a.samples, w, h)
    floor = bpy.data.objects['stage floor']
    floor.location.z = zmin_all - 0.03
    cd = bpy.data.cameras.new('cam')
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cd.lens = 50
    cd.sensor_width = 36
    cd.clip_start, cd.clip_end = 0.02, 100

    def look(ob, loc, target, up=Vector((0, 0, 1))):
        f = (Vector(target) - Vector(loc)).normalized()
        r_ = f.cross(up).normalized()
        u = r_.cross(f)
        M = Matrix((r_, u, -f)).transposed().to_4x4()
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
        lo_ = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo_)
        lights.append((lo_, daz, el, d))

    HI = bb._principled('moving part', bb.srgb('#E0661A'), 0.45)
    tint_state = {}

    def tint(pid, on):
        if tint_state.get(pid) == on:
            return
        tint_state[pid] = on
        for sl in items[pid].material_slots:
            if on:
                sl.link = 'OBJECT'
                sl.material = HI
            else:
                sl.link = 'DATA'

    def cam_view(c):
        ctr, az, el, dist = c
        ar, er = math.radians(az), math.radians(el)
        view = Vector((-math.cos(er) * math.cos(ar), -math.cos(er) * math.sin(ar), math.sin(er)))
        return ctr, view, dist

    def pose(t):
        # ---- parts
        state = []
        for r in rows:
            d = Vector(r['dir']) if r['dir'] else Vector()
            u = (t - r['t_mv0']) / max(1e-6, r['t_mv1'] - r['t_mv0'])
            for p in r['parts']:
                if p not in items:
                    continue
                if t < r['t_mv0']:
                    items[p].hide_render = True
                    continue
                items[p].hide_render = False
                moving = u < 1.0 + T_SETTLE / (r['t_mv1'] - r['t_mv0']) * 0.0
                k = 1.0 - smooth(u)
                off = -d * (r['visual_mm'] / 1000.0) * k
                items[p].matrix_world = Matrix.Translation(off) @ rest[p]
                tint(p, (t < r['t_end'] - 0.05) and r['id'] != 'END')
                state.append((p, round(off.x, 4), round(off.y, 4), round(off.z, 4), t < r['t_end'] - 0.05))
        for e, ob in be.wires.items():
            r = next(x for x in rows if x['id'] == wire_step[e])
            vis = t >= r['t_mv1']
            ob.hide_render = not vis
            if vis:
                tint(e, t < r['t_end'] - 0.05)
                state.append((e, 1))
        # ---- camera: ease from the previous step's camera to this one's
        ci = 0
        for q, r in enumerate(rows):
            if t >= r['t_cam0']:
                ci = q
        cur = rows[ci]
        p0, p1 = cams[rows[max(ci - 1, 0)]['id']], cams[cur['id']]
        k = smooth((t - cur['t_cam0']) / (T_CAM_STAGE if cur['first_in_stage'] else T_CAM))
        cam_c = (p0[0] * (1 - k) + p1[0] * k, p0[1] * (1 - k) + p1[1] * k, p0[2] * (1 - k) + p1[2] * k,
                 p0[3] * (1 - k) + p1[3] * k)
        if t >= rows[-1]['t_stage_end']:                           # the whole aircraft: pull back and swing round
            k = smooth((t - rows[-1]['t_stage_end']) / 1.6)
            e_ = cams['END']
            last = cams[rows[-1]['id']]
            az_ = e_[1] + 22 * smooth((t - rows[-1]['t_stage_end']) / T_END)
            cam_c = (last[0] * (1 - k) + e_[0] * k, last[1] * (1 - k) + az_ * k, last[2] * (1 - k) + e_[2] * k,
                     last[3] * (1 - k) + e_[3] * k)
            for p in sorted(placed_ids):
                if p in items:
                    tint(p, False)
        ctr, view, dist = cam_view(cam_c)
        look(cam, ctr + view * dist, ctr)
        caz = math.atan2(view.y, view.x)
        for lo_, daz, lel, dd in lights:
            aa, ee = caz + math.radians(daz), math.radians(lel)
            loc = ctr + Vector((math.cos(ee) * math.cos(aa), math.cos(ee) * math.sin(aa), math.sin(ee))) * dd
            look(lo_, loc, ctr, Vector((0, 0, 1)) if lel < 85 else Vector((1, 0, 0)))
        blob_s.default_value = (0.55, 0.9, 1.0)
        blob_c.default_value = (full_c.x, 0.0, 0.0)
        blob_op.default_value = 0.35
        bpy.context.view_layer.update()
        return (tuple(state), tuple(round(v, 3) for v in (*cam_c[0], cam_c[1], cam_c[2], cam_c[3])))

    sc.render.resolution_percentage = 100
    frames = [int(f) for f in a.frames.split(',') if f.strip()] if a.frames else list(range(0, nframes, a.every))
    os.makedirs(a.out, exist_ok=True)
    t0, prev_key, prev_path, n_new = time.time(), None, None, 0
    for f in frames:
        key = pose(f / FPS)
        path = os.path.join(a.out, 'raw_%04d.png' % f)
        if key == prev_key and prev_path and os.path.exists(prev_path):
            shutil.copyfile(prev_path, path)
        else:
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
            n_new += 1
        prev_key, prev_path = key, path
        if f % 20 == 0:
            print('FRAME %d / %d rendered %d  %.0f s' % (f, nframes, n_new, time.time() - t0), flush=True)
    print('RENDER_TOTAL %.1f s for %d frames (%d rendered)' % (time.time() - t0, len(frames), n_new))


def blender_encode(argv):
    """Named PNGs (a list file, one name per line) -> H.264 MP4 with Blender's FFmpeg (VSE)."""
    import argparse
    import bpy
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--list', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--kbps', type=int, default=1500)
    ap.add_argument('--w', type=int, default=W)
    ap.add_argument('--h', type=int, default=H)
    a = ap.parse_args(argv)
    names = [n.strip() for n in open(a.list) if n.strip()]
    sc = bpy.context.scene
    sc.sequence_editor_create()
    st = sc.sequence_editor.sequences.new_image('frames', os.path.join(a.src, names[0]), 1, 1)
    for n in names[1:]:
        st.elements.append(n)
    sc.frame_start, sc.frame_end = 1, len(names)
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = a.w, a.h
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


def short_caption(c):
    c = c.split(' (')[0].split(';')[0].strip()
    return c if len(c) <= 112 else c[:109].rstrip() + '...'


def overlay(src, dst, f, rows, total, fonts):
    from PIL import Image, ImageDraw
    im = Image.open(src).convert('RGBA')
    sw, sh = im.size
    k = sw / W
    si, row, stepno, prog = frame_info(rows, total, f)
    ink, hi, muted, sub_c = (18, 22, 25), (194, 84, 10), (107, 114, 128), (61, 70, 82)
    f_title, f_sub, f_mono, f_head = fonts
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((36 * k, 28 * k), 'Concept A quad tailsitter', font=f_head, fill=ink + (230,))
    d.text((36 * k, 52 * k), 'BUILD SEQUENCE', font=f_mono, fill=muted + (230,))
    t = f / FPS
    done = t >= rows[-1]['t_stage_end']
    if done:
        label, sub, cnt = 'Complete: 97 parts, %d steps' % len(rows), 'Props, motors, cage, wing, fins, linkage, avionics, wiring, cover and pack', '10 / 10'
        si = len(STAGES) - 1
    else:
        label = STAGES[si][0]
        sub = '%s   %s' % (row['id'], short_caption(row['caption']))
        cnt = 'Stage %d / %d' % (si + 1, len(STAGES))
    x0, y1 = 36 * k, sh - 36 * k
    tw = max(d.textlength(label, font=f_title), d.textlength(sub, font=f_sub))
    pw = min(sw - 72 * k, max(560 * k, tw + 60 * k))
    ph = 122 * k
    y0 = y1 - ph
    d.rounded_rectangle((x0, y0, x0 + pw, y1), radius=8, fill=(255, 255, 255, 238), outline=(203, 210, 219, 255))
    d.rectangle((x0, y0 + 14 * k, x0 + 4 * k, y1 - 14 * k), fill=hi + (255,))
    d.text((x0 + 22 * k, y0 + 12 * k), cnt, font=f_mono, fill=hi + (255,))
    dx = x0 + 22 * k + int(d.textlength(cnt, font=f_mono)) + 14 * k
    for q in range(len(STAGES)):
        cx, cy = dx + q * 16 * k, y0 + 22 * k
        r_ = 4 * k
        if q < si or done:
            d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), fill=ink + (200,))
        elif q == si:
            d.ellipse((cx - 5 * k, cy - 5 * k, cx + 5 * k, cy + 5 * k), fill=hi + (255,))
        else:
            d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), outline=muted + (200,), width=1)
    d.text((x0 + 22 * k, y0 + 34 * k), label, font=f_title, fill=ink + (255,))
    d.text((x0 + 22 * k, y0 + 72 * k), sub, font=f_sub, fill=sub_c + (255,))
    if not done:
        sn = 'step %d / %d' % (stepno, len(rows))
        d.text((x0 + pw - 22 * k - d.textlength(sn, font=f_mono), y0 + 12 * k), sn, font=f_mono, fill=muted + (255,))
    bx0, bx1, by = x0 + 22 * k, x0 + pw - 22 * k, y1 - 10 * k
    d.rounded_rectangle((bx0, by - 2 * k, bx1, by + k), radius=2, fill=(220, 225, 232, 255))
    pxx = bx0 + (bx1 - bx0) * prog
    d.rounded_rectangle((bx0, by - 2 * k, max(bx0 + 3, pxx), by + k), radius=2, fill=hi + (255,))
    for r in rows:
        if r['first_in_stage'] and r['stage'] > 0:
            tx = bx0 + (bx1 - bx0) * r['t_cam0'] / total
            d.line((tx, by - 4 * k, tx, by + 3 * k), fill=(255, 255, 255, 255), width=2)
    Image.alpha_composite(im, lay).convert('RGB').save(dst, optimize=False, compress_level=1)


# =====================================================================================================================
# driver
# =====================================================================================================================
def run(cmd, show=('FRAME', 'RENDER_TOTAL', 'ENCODED', 'PARTS', 'WIRES', 'Traceback', 'Error', '  File')):
    print('>', ' '.join('"%s"' % c if ' ' in c else c for c in cmd), flush=True)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    for line in p.stdout.splitlines():
        if line.startswith(show) or 'Error' in line:
            print('   ', line[:400], flush=True)
    if p.returncode != 0:
        print(p.stdout[-4000:])
        raise SystemExit('blender failed')


def driver():
    import argparse
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender', default=os.environ.get('BLENDER', BLENDER_DEFAULT))
    ap.add_argument('--samples', type=int, default=12)
    ap.add_argument('--frames', default='')
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'a_build'))
    ap.add_argument('--skip-render', action='store_true')
    ap.add_argument('--kbps', type=int, default=1500)
    ap.add_argument('--stage-kbps', type=int, default=1100)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    rows, total = timeline()
    nframes = int(total * FPS)
    print('%d steps, %d stages, %.1f s, %d frames' % (len(rows), len(STAGES), total, nframes))
    me = os.path.abspath(__file__)
    every, scale = (3, 0.5) if a.preview else (1, 1.0)
    if not a.skip_render:
        cmd = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', a.work, '--samples', str(a.samples),
               '--every', str(every), '--scale', str(scale)]
        if a.frames:
            cmd += ['--frames', a.frames]
        run(cmd)
    frames = [int(x) for x in a.frames.split(',')] if a.frames else list(range(0, nframes, every))
    fonts = None
    for f in frames:
        src = os.path.join(a.work, 'raw_%04d.png' % f)
        if fonts is None:
            k = Image.open(src).size[0] / W
            sans = ['IBMPlexSans-Medium.ttf', 'IBMPlexSans-SemiBold.ttf', 'seguisb.ttf', 'segoeui.ttf', 'arial.ttf']
            sans_r = ['IBMPlexSans-Regular.ttf', 'segoeui.ttf', 'arial.ttf']
            mono = ['IBMPlexMono-Medium.ttf', 'CascadiaMono.ttf', 'consola.ttf', 'cour.ttf']
            fonts = (_font(sans, int(28 * k)), _font(sans_r, int(18 * k)), _font(mono, int(15 * k)),
                     _font(['seguisb.ttf', 'segoeui.ttf', 'arial.ttf'], int(17 * k)))
        overlay(src, os.path.join(a.work, 'lab_%04d.png' % f), f, rows, total, fonts)
    if a.frames or a.preview:
        print('test frames in', a.work)
        return

    def encode(names, out, kbps):
        lst = os.path.join(a.work, '_list.txt')
        open(lst, 'w').write('\n'.join(names))
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work, '--list', lst,
             '--out', out, '--kbps', str(kbps)])
    encode(['lab_%04d.png' % f for f in frames], os.path.join(OUT, 'a-build.mp4'), a.kbps)
    sf = stage_frames(rows, total)
    for si, (f0, f1) in sf.items():
        n = '%02d' % (si + 1)
        encode(['lab_%04d.png' % f for f in range(f0, f1 + 1)], os.path.join(OUT, 'stage-%s.mp4' % n), a.stage_kbps)
        Image.open(os.path.join(a.work, 'lab_%04d.png' % f1)).convert('RGB').save(
            os.path.join(OUT, 'stage-%s.webp' % n), quality=84, method=6)
    Image.open(os.path.join(a.work, 'lab_%04d.png' % (nframes - 1))).convert('RGB').save(
        os.path.join(OUT, 'a-build-poster.webp'), quality=84, method=6)
    meta = {'steps': [{k: v for k, v in r.items() if k != 'parts'} | {'n_parts': len(r['parts'])} for r in rows],
            'stages': [{'n': i + 1, 'title': t, 'steps': ids, 'frames': sf[i]} for i, (t, ids) in enumerate(STAGES)],
            'fps': FPS, 'frames': nframes}
    json.dump(meta, open(os.path.join(OUT, 'a-build.json'), 'w'), indent=1)
    for fn in sorted(os.listdir(OUT)):
        print('%-24s %7.2f MB' % (fn, os.path.getsize(os.path.join(OUT, fn)) / 1e6))
    print('total %.1f min' % ((time.time() - t0) / 60))


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
