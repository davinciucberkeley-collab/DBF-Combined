"""render_build_a.py - the concept A build film: the 65 steps of qp/A/cad/a_assembly_plan.py in 10 stages, one clip + one still per
stage and the full film, made to FOLLOW the written guide qp/A/BUILD-GUIDE-A.md (both read qp/A/cad/a_build_steps.py).

    python redesign/showcase/concept-a/render_build_a.py               # render + overlay + encode everything (about 2 h, workers in parallel)
    python redesign/showcase/concept-a/render_build_a.py --preview     # half size, every 4th frame, no encode
    python redesign/showcase/concept-a/render_build_a.py --frames 40,300   # test frames only (render + overlay, no encode)
    python redesign/showcase/concept-a/render_build_a.py --skip-render      # redo overlay + encode from the frames already in --work

Run with the system Python (needs Pillow). Steps, as render_build.py (K09-L):
  1. render   Blender (EEVEE) builds the concept A CAD from redesign/qp/A/cad/model through redesign/blender/blender_backend.py and poses
              each part per frame. Several Blender workers render disjoint frame ranges in parallel. Frames identical to the previous
              one are not rendered again (the overlay step reuses the picture). Each worker also writes, per frame, the 2-D screen
              position of every callout anchor (projected through the real camera).
  2. overlay  Pillow: the stage title card, the step card (step id, one-line instruction, tools, key check), callout labels with
              leader lines on the parts being fitted, dimension lines on cut tubes, make-it banners for printed / cut parts,
              checkpoint cards, stage dots and progress.
  3. encode   Blender's FFmpeg (VSE): a-build.mp4 + stage-NN.mp4 (H.264) and stage-NN.webp (last frame of each stage).

Every part motion is the one of a_assembly_plan.STEPS (direction, travel), which a_assembly.py swept against all parts already placed
(out/ASSEMBLY.md). For legibility a motion shorter than MIN_TRAVEL_MM is started MIN_TRAVEL_MM away along the same line; the part of that
line beyond the checked travel is approach in free air and is NOT part of the swept check. Steps with travel 0 (A1 core on the bench, E5
strap) simply appear. What this film ADDS to the plan, none of it a part motion:
  * make-it beats (the part shown at its start pose in teal with its cut length or print label, before it moves in),
  * B0 (D-202): the cage frame is BUILT ON THE BENCH, part by part, in the bench steps B0b-B0j2 (a_assembly_plan.BENCH): the hub appears alone, then
    each step moves its own parts in along the plan's direction and travel, all offset by the B1 start pose (the place where the finished cage unit
    hovers before it docks) so that they assemble onto the hub there. Parts of later bench steps are not shown yet, nothing of the wing is shown, and
    one camera frames the whole cage unit for B0a-B0j2. Bench parts get the same make-it beat (teal, print / cut / fit label) as other parts. B1
    docks the finished frame (with the motors and props, which come on in B1) exactly as in the plan.
  * B0k: the cage unit (without motors and props) hovers at its B1 start pose, shown semi-transparent while the
    phase leads are threaded along the arm bores (a progressive reveal along the wire route, from out/wire_inventory.json), B2c threads
    them on through the hub conduit, raceway and ditch, E6 solders the last part to the ESC pads. The reveal follows the cage unit.
Skin tape, hinge tape and epoxy fillets are not drawn (as in the plan). Parts that the plan does not place are not shown.
Outputs: redesign/showcase/concept-a/animation/.
"""
import concurrent.futures
import json
import math
import os
import re
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
T_TITLE, T_CAM_STAGE = 6.5, 1.2      # s stage title card (camera moves during its first T_CAM_STAGE)
T_CAM = 0.7                          # s camera move before a step
T_FAB = 4.5                          # s make-it beat (cut / print / hot-wire label) before the part moves in
T_THREAD = {'B0k': 8.0, 'B2c': 8.0, 'E6': 8.0, 'D0': 5.0}      # s thread / solder animation of the marker steps with a wire reveal
T_MARK = 3.5                          # s the other marker steps
T_HOLD_MIN = 1.0                     # s minimum hold after a motion
T_STAGE_HOLD = 0.8                   # s hold at the end of a stage
T_END = 6.0                          # s final card with the whole aircraft
READ_CPS, READ_MIN = 22.0, 6.5       # characters per second a student can read; minimum card time per step
CHECK_CPS, CHECK_MIN = 20.0, 5.0
MIN_TRAVEL_MM = 70.0                 # visual minimum approach (see the module docstring)
MAX_TRAVEL_MM = 450.0                # long insertions (spar 700, tubes 500) start 450 mm away
T_MOVE = {'long': 2.2, 'short': 1.7, 'appear': 1.0}

STAGES = [
    ('Wing core and spar', ['A1', 'A2', 'A3', 'A4', 'A5']),
    ('Cage frame on the bench (D-202), motor leads threaded, motors, props, dock', ['B0a', 'B0b', 'B0c', 'B0d', 'B0e', 'B0f', 'B0g1', 'B0g2', 'B0g3', 'B0g4', 'B0h', 'B0i1', 'B0i2', 'B0i3', 'B0i4', 'B0j1', 'B0j2', 'B0k', 'B1']),
    ('Rib saddles, phase-lead raceways, pack tray, hinge dampers', ['B2', 'B2a', 'B2b1', 'B2b2', 'B2b3', 'B2b4', 'B2c', 'B3', 'B4']),
    ('Fin ribs and rib fairings', ['C1', 'C1a']),
    ('Elevons, balance strips, lens caps', ['C2', 'C2a', 'C2b']),
    ('Fins: fairings, root blocks, tubes', ['C3', 'C4', 'C5', 'C6']),
    ('Landing feet', ['C7', 'C8', 'C9']),
    ('Servos, pushrods, horns, lead threading', ['D1', 'D0', 'D2', 'D2a', 'D3', 'D4', 'D5', 'D5b']),
    ('Avionics: pitot, plate, ESC, FC, leads', ['E1', 'E2', 'E3', 'E3a', 'E3d', 'E3b']),
    ('Pack, XT60, strap, phase leads, bay cover', ['E3c', 'E4', 'E4a', 'E4b', 'E5', 'E6', 'E7']),
]
# per-step camera direction (azimuth from the nose, 90 = left; elevation) where the default (38, 30) hides the part
VIEW = {'B1': (-40, -22), 'B2': (35, -28), 'C2b': (35, -30), 'C8': (60, 8), 'C9': (60, 12), 'C7': (60, 12),
        'C6': (50, 14), 'D2a': (30, 40), 'E1': (-20, 25), 'A2': (20, 30), 'A5': (-30, 30), 'A1': (38, 30),
        'B0a': (-40, 22), 'B0k': (-40, 22), 'B2c': (38, 30)}
DEFAULT_VIEW = (38, 30)

# D-198 marker steps (threading / laying wires place no part): the camera frames these parts instead
MARKER_FOCUS = {'B0a': [], 'B0k': ['CGE-001', 'CGE-002-A', 'CGE-002-B'], 'B2c': ['HRN-003-R', 'HRN-003-L', 'CGE-001', 'HRN-004-UR', 'HRN-004-UL', 'HRN-004-LR', 'HRN-004-LL'],
                'D0': ['MEC-001-R', 'WNG-001'], 'E3b': ['AVN-002', 'PRP-003', 'AVN-001'],
                'E4b': ['HRN-002', 'PWR-001', 'CGE-008'], 'E6': ['PRP-003', 'AVN-001', 'CGE-001']}
# B0 shows the cage unit (B1 parts minus the motors and props, which are screwed on in B1) hovering at its B1 start pose
# D-202: the parts of the bench steps B0b-B0j2 are shown by their own step (at the B1 start pose); PRESHOW only adds the cage parts no bench step places
PRESHOW = {'B0k': ('B1', ('PRP-',))}
BENCH_VIEW = (-40, 22)                 # camera direction of the bench steps B0b-B0j2 (as B0a / B0k)
# wire reveal (threading): edge -> step id -> (fraction from, fraction to) along the route; fractions from out/wire_inventory.json
PHASE_EDGES = ('E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05')
SERVO_EDGES = ('E-HRN-07', 'E-HRN-08')
REVEAL_EDGES = PHASE_EDGES + SERVO_EDGES
SERVO_START = {'E-HRN-07': 'MEC-001-R', 'E-HRN-08': 'MEC-001-L'}      # the servo lead is threaded from the servo pocket to the slit
# camera framing: steps with a right and a left part frame the right one only (the left mirrors it); smaller context for small parts
ONE_SIDE = ('D1', 'D2', 'D2a', 'D3', 'D4', 'D5', 'C7', 'C8', 'C9', 'C1', 'C1a', 'C3', 'C5', 'C6', 'B2', 'B4', 'C2a', 'C2b')
MIN_HALF_STEP = {'D1': 0.10, 'D2': 0.07, 'D2a': 0.05, 'D3': 0.07, 'D4': 0.06, 'D5': 0.05, 'D5b': 0.05, 'C7': 0.12, 'C8': 0.12, 'C9': 0.10, 'E1': 0.15, 'E2': 0.07, 'E3': 0.08,
                 'E3a': 0.06, 'E3d': 0.06, 'E3b': 0.08, 'E3c': 0.07, 'E4': 0.09, 'E4a': 0.08, 'E4b': 0.09, 'E5': 0.09, 'E6': 0.09, 'E7': 0.08, 'D0': 0.09, 'B2a': 0.10, 'B2b1': 0.10, 'B2b2': 0.10, 'B2b3': 0.10, 'B2b4': 0.10, 'B3': 0.10}
EXTRA_PTS = {'D0': [(0.083, 0.024, 0.012), (0.14, 0.20, 0.0)]}      # marker steps: points the camera must also frame (servo pocket, slit)
GHOST_VIEW, GHOST_DIST = (50, 34), 0.24   # x-ray steps (step data 'ghost'): close-up camera that follows the plug along the spar (azimuth, elevation; distance m)
GHOST_B0 = ('CGE-001', 'CGE-002-', 'CGE-003-', 'CGE-009-', 'CGE-010-')
GHOST_B2C = GHOST_B0 + ('HRN-003-', 'HRN-004-', 'WNG-001', 'CGE-004', 'CGE-005-', 'CGE-006', 'CGE-007-')
FAB_ONLY = {'B1': ('PRP-',)}          # B1: during its make-it beat only the motors and props are teal (the cage parts are already shown)
NO_CONTEXT = ('B0a',)                  # the stage's first step frames only the cage unit on the bench (like the bench steps), not everything placed so far
T_CHK_CAM = 0.9                      # s camera pull-back to the whole assembly while a checkpoint card is up
MARKER_BEAT_KINDS = ('thread', 'solder')   # these fab kinds are shown during the marker step's motion, not as a separate beat


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


def load_plan():
    sys.path.insert(0, CAD_A)
    import a_assembly_plan as ap
    import a_build_steps as bsd
    out = []
    for s in ap.STEPS:
        info = bsd.BY_ID[s[0]]
        out.append(dict(id=s[0], caption=s[1], parts=list(s[2]), dir=s[3], travel=float(s[4]), edges=list(s[6]) if len(s) > 6 else [], info=info, bench=s[0] in ap.BENCH))
    return out


def wire_fractions():
    """{edge: (f1, f2)} from out/wire_inventory.json. Phase leads: fraction of the route (motor end to ESC pad) after the arm bore, and after
    the hub conduit + raceway + ditch. Servo leads: the fraction after the foam groove (both values)."""
    d = json.load(open(os.path.join(CAD_A, 'out', 'wire_inventory.json')))
    out = {}
    for r in d['rows']:
        tot = r['total_m']
        if r['edge'] in PHASE_EDGES:
            out[r['edge']] = (r['arm_m'] / tot, (r['arm_m'] + r['race_m'] + r['groove_m']) / tot)
        elif r['edge'] in SERVO_EDGES:
            out[r['edge']] = (r['groove_m'] / tot, r['groove_m'] / tot)      # servo lead: pocket to the end of the foam groove, then to the FC pad
    return out


def timeline():
    """Pure schedule: list of step dicts with times, and the total length (s)."""
    plan = {s['id']: s for s in load_plan()}
    t, rows = 0.0, []
    for si, (title, ids) in enumerate(STAGES):
        for k, sid in enumerate(ids):
            s = dict(plan[sid])
            info = s['info']
            tr = min(MAX_TRAVEL_MM, max(MIN_TRAVEL_MM, s['travel'])) if s['dir'] else 0.0
            s['visual_mm'] = tr
            s['stage'] = si
            s['first_in_stage'] = (k == 0)
            fab = info.get('fab')
            s['fab'] = fab if (fab and fab['kind'] not in MARKER_BEAT_KINDS) else None
            s['marker_chip'] = info.get('chip') or (fab if (fab and fab['kind'] in MARKER_BEAT_KINDS) else None)
            s['t_cam0'] = t
            if k == 0:
                s['cam_dur'] = T_CAM_STAGE
                s['t_title0'], s['t_title1'] = t, t + T_TITLE
                t = s['t_title1']
                s['t_card0'] = t
            else:
                s['cam_dur'] = T_CAM
                s['t_card0'] = t
                t += T_CAM
            s['t_fab0'] = t
            if s['fab']:
                t += T_FAB
            s['t_mv0'] = t
            if s['parts'] and s['dir']:
                t += T_MOVE['long'] if tr > 200 else T_MOVE['short']
            elif s['parts']:
                t += T_MOVE['appear']
            else:
                t += T_THREAD.get(sid, T_MARK)
            s['t_mv1'] = t
            s['t_tint1'] = t + 0.3
            chars = len(info['line']) + len(info['tools']) + len(info['check']) + 30
            t = max(t + T_HOLD_MIN, s['t_card0'] + max(READ_MIN, chars / READ_CPS))
            s['t_end'] = t
            if info.get('hold') and info.get('cp'):
                c = sum(len(x) for x in info['cp']) + 40
                s['t_chk0'] = t
                t += max(CHECK_MIN, c / CHECK_CPS)
                s['t_chk1'] = t
            else:
                s['t_chk0'] = s['t_chk1'] = t
            rows.append(s)
        t += T_STAGE_HOLD
        rows[-1]['t_stage_end'] = t
    return rows, t + T_END


def frame_info(rows, total, f):
    """(stage index, step row, step number 1-based, kind) for the overlay of frame f; kind = title | step | check | end."""
    t = f / FPS
    cur = rows[0]
    for r in rows:
        if t >= r['t_cam0']:
            cur = r
    kind = 'step'
    if t >= rows[-1]['t_stage_end']:
        kind = 'end'
    elif cur.get('t_title0') is not None and cur['t_title0'] <= t < cur['t_title1']:
        kind = 'title'
    elif cur['t_chk1'] > cur['t_chk0'] and cur['t_chk0'] <= t < cur['t_chk1']:
        kind = 'check'
    return cur['stage'], cur, rows.index(cur) + 1, kind


def stage_frames(rows, total):
    """{stage: (first frame, last frame)}; a stage runs from its first camera move to the next stage's."""
    out = {}
    for si in range(len(STAGES)):
        rs = [r for r in rows if r['stage'] == si]
        f0 = int(rs[0]['t_cam0'] * FPS)
        f1 = int(rs[-1]['t_stage_end'] * FPS) - 1
        out[si] = (f0, min(f1, int(total * FPS) - 1))
    return out


def moving_frames(rows, total):
    """Frames where the picture can change (camera, parts, wire reveal): used to balance the workers."""
    n = int(total * FPS)
    cost = [0] * n
    for r in rows:
        spans = [(r['t_cam0'], r['t_cam0'] + r['cam_dur']), (r['t_fab0'], r['t_fab0'] + 0.1), (r['t_mv0'] - 0.1, r['t_tint1'])]
        if r['t_chk1'] > r['t_chk0']:
            spans.append((r['t_chk0'], r['t_chk0'] + T_CHK_CAM))
        for a, b in spans:
            for f in range(max(0, int(a * FPS)), min(n, int(b * FPS) + 1)):
                cost[f] = 1
    return cost


# =====================================================================================================================
# Blender worker
# =====================================================================================================================
def blender_render(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='')
    ap.add_argument('--range', default='')
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--samples', type=int, default=12)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--no-rt', action='store_true', help='EEVEE ray tracing off (faster)')
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
    by_id = {r['id']: r for r in rows}

    def sample_pts(pids):
        pts = []
        for p in pids:
            ob = items[p]
            vs = ob.data.vertices
            st = max(1, len(vs) // 400)
            for k in range(0, len(vs), st):
                pts.append(rest[p] @ vs[k].co)
        return pts

    def bbox(pids, shift=None):
        pts = [q + (shift or Vector()) for q in sample_pts(pids)]
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

    # preshow: parts of a later step shown early at their start pose (B0 -> the B1 cage unit without motors and props)
    # D-202 bench: the parts of the bench steps B0b-B0j2 (in the plan again in B1) are shown from their own bench step, at the B1 start pose
    b1 = by_id['B1']
    B1_START = -Vector(b1['dir']) * b1['visual_mm'] / 1000.0        # where the finished cage unit hovers before it docks
    bench_rows = [r for r in rows if r['bench']]
    bench_of = {p: r['id'] for r in bench_rows for p in r['parts']}
    show_from = {}
    for r in rows:
        t0 = r['t_fab0']
        for p in r['parts']:
            if r['bench'] or p not in bench_of:
                show_from[p] = t0
    for early, (later, excl) in PRESHOW.items():
        for p in by_id[later]['parts']:
            if not p.startswith(excl) and p not in bench_of:
                show_from[p] = by_id[early]['t_fab0']

    # per-step camera. First step of a stage: wide shot of everything placed so far plus the moving parts; the other steps:
    # closer on the step's parts (start and seat positions) with at least MIN_HALF m of context around them.
    MIN_HALF = 0.16
    TAN_H, TAN_V = 18.0 / 50.0, 18.0 * H / W / 50.0

    pt_cache = {}

    def pts_of(pids, shift=None):
        out = []
        for p in pids:
            if p not in pt_cache:
                pt_cache[p] = sample_pts([p])
            out += [q + shift for q in pt_cache[p]] if shift else pt_cache[p]
        return out

    def aabb(pts):
        return (Vector([min(q[i] for q in pts) for i in range(3)]), Vector([max(q[i] for q in pts) for i in range(3)]))

    def fit(pts, az, el):
        """Camera target and distance that frame the points in the free band of the 16:9 frame (header and make-it banner on top, step
        card at the bottom): each point must lie inside the view cone at its own depth."""
        ar, er = math.radians(az), math.radians(el)
        view = Vector((-math.cos(er) * math.cos(ar), -math.cos(er) * math.sin(ar), math.sin(er)))
        right = view.cross(Vector((0, 0, 1)))
        right = right.normalized() if right.length > 1e-6 else Vector((0, 1, 0))
        up = right.cross(view).normalized()
        lo, hi = aabb(pts)
        c = (lo + hi) / 2
        us = [(q - c).dot(right) for q in pts]
        vs_ = [(q - c).dot(up) for q in pts]
        ds = [(q - c).dot(view) for q in pts]
        ctr = c + right * ((max(us) + min(us)) / 2) + up * ((max(vs_) + min(vs_)) / 2)
        uc, vc = (max(us) + min(us)) / 2, (max(vs_) + min(vs_)) / 2
        dist = max(max(abs(u - uc) / (TAN_H * 0.97), abs(v - vc) / (TAN_V * 0.62)) + d for u, v, d in zip(us, vs_, ds))
        dist = max(dist, 0.3)
        tgt = ctr - up * (0.045 * 2 * dist * TAN_V)          # subject sits in the band between the banner and the card
        return tgt, dist

    # bench camera: one frame for B0a-B0j2 = the finished cage frame at the B1 start pose
    cage = [p for p in b1['parts'] if not p.startswith(PRESHOW['B0k'][1]) and p in items]
    bench_P = pts_of(cage, B1_START)                  # the frame on the bench only (the seat on the spar is B1's business)
    bench_t0 = min(r['t_cam0'] for r in rows if r['bench'] or r['id'] in NO_CONTEXT)
    bench_t1 = by_id['B0k']['t_cam0']
    # (the start poses of the long slides are left out on purpose: the arm tubes slide in from the frame edge, so the hub stays readable)

    placed_so_far = []
    cams = {}
    cams_chk = {}
    for r in rows:
        d = Vector(r['dir']) if r['dir'] else Vector()
        shift = -d * r['visual_mm'] / 1000.0
        bframe = r['bench'] or r['id'] in NO_CONTEXT
        if bframe:
            parts = [p for p in r['parts'] if p in items]
        elif r['id'] in PRESHOW:
            later = by_id[PRESHOW[r['id']][0]]
            parts = [p for p in later['parts'] if not p.startswith(PRESHOW[r['id']][1]) and p in items]
            shift = -Vector(later['dir']) * later['visual_mm'] / 1000.0
        else:
            parts = [p for p in (r['parts'] or MARKER_FOCUS.get(r['id'], [])) if p in items]
        if r['id'] in ONE_SIDE:                                  # frame the right-hand parts only (the left ones mirror them)
            rp = [p for p in parts if sum(q.y for q in pts_of([p])) / max(1, len(pts_of([p]))) >= -0.005]
            parts = rp or parts
        P = (list(bench_P) if bframe else pts_of(parts) + pts_of(parts, shift)) + [Vector(q) for q in EXTRA_PTS.get(r['id'], [])]
        placed_so_far += [p for p in parts if p in r['parts']]
        if r['first_in_stage'] and r['id'] not in NO_CONTEXT:
            P += pts_of(placed_so_far)
        lo, hi = aabb(P)
        c0 = (lo + hi) / 2
        mh = MIN_HALF_STEP.get(r['id'], MIN_HALF)
        P += [c0 + Vector((sx * mh, sy * mh, sz * mh)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        az, el = VIEW.get(r['id'], BENCH_VIEW if r['bench'] else DEFAULT_VIEW)
        tgt, dist = fit(P, az, el)
        cams[r['id']] = (tgt, az, el, dist)
        if r['t_chk1'] > r['t_chk0']:                       # checkpoint card: pull back to everything placed so far
            t2, d2 = fit(bench_P if bframe else pts_of(placed_so_far), az, el)
            cams_chk[r['id']] = (t2, az, el, d2)
    allp = pts_of(sorted(placed_ids))
    full_lo, full_hi = aabb(allp)
    full_c = (full_lo + full_hi) / 2
    tgt, dist = fit(allp, 38, 26)
    cams['END'] = (tgt, 38, 26, dist * 1.05)
    zmin_all = full_lo.z

    # scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    w, h = int(W * a.scale), int(H * a.scale)
    blob_c, blob_s, blob_op = ra.make_stage(sc, a.samples, w, h)
    if a.no_rt:
        sc.eevee.use_raytracing = False
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

    MATS = {'move': bb._principled('moving part', bb.srgb('#E0661A'), 0.45),
            'fab': bb._principled('fabricated part', bb.srgb('#13897F'), 0.45),
            'ghost': bb._principled('ghost part', bb.srgb('#8FA6C0'), 0.5, alpha=0.20),
            'ghost_spar': bb._principled('ghost spar', bb.srgb('#2E4A6B'), 0.3, metal=0.2, alpha=0.38)}
    for m_ in (MATS['ghost'], MATS['ghost_spar']):          # see-through parts must not shadow what they hide
        if hasattr(m_, 'use_transparent_shadow'):
            m_.use_transparent_shadow = True
    tint_state = {}

    def tint(pid, mode):
        if tint_state.get(pid) == mode:
            return
        tint_state[pid] = mode
        for sl in items[pid].material_slots:
            if mode:
                sl.link = 'OBJECT'
                sl.material = MATS[mode]
            else:
                sl.link = 'DATA'

    # ---- wire reveal curves (phase leads): the same strands as the wire meshes, drawn with a curve bevel so that a fraction can be shown
    wires = {wv.edge: wv for wv in ctx.wires}
    reveal = {}
    for e in REVEAL_EDGES:
        wv = wires[e]
        block = be._edge(e).get('wire', {})
        bend = block.get('bend_radius_mm', 5 * wv.dia * 1000) / 1000.0
        cu = bpy.data.curves.new(e + ' reveal', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        cu.bevel_factor_mapping_end = 'SPLINE'
        polys = []
        strands = list(wv.strands or [(wv.points, wv.dia)])
        if e in SERVO_START:                                    # start the polyline at the servo end
            c_s = sum(pts_of([SERVO_START[e]]), Vector()) / max(1, len(pts_of([SERVO_START[e]])))
            l0 = strands[0][0]
            if (Vector(l0[-1]) - c_s).length < (Vector(l0[0]) - c_s).length:
                strands = [(list(reversed(list(ln))), dia_) for ln, dia_ in strands]
        for line, dia in strands:
            pts = bb.fillet_polyline(line, bend)
            sp = cu.splines.new('POLY')
            sp.points.add(len(pts) - 1)
            for p_, q in zip(sp.points, pts):
                p_.co = (q.x, q.y, q.z, 1.0)
                p_.radius = dia / 2
            polys.append(pts)
        ob = bpy.data.objects.new(e + ' reveal', cu)
        sc.collection.objects.link(ob)
        cu.materials.append(MATS['move'])
        ob.hide_render = True
        cum = [0.0]
        for q0, q1 in zip(polys[0][:-1], polys[0][1:]):
            cum.append(cum[-1] + (q1 - q0).length)
        reveal[e] = dict(ob=ob, cu=cu, pts=polys[0], cum=cum)
    fr = wire_fractions()

    def head_pos(e, f):
        rv = reveal[e]
        L = rv['cum'][-1] * f
        for k in range(1, len(rv['cum'])):
            if rv['cum'][k] >= L:
                u = (L - rv['cum'][k - 1]) / max(1e-9, rv['cum'][k] - rv['cum'][k - 1])
                return rv['pts'][k - 1] * (1 - u) + rv['pts'][k] * u
        return rv['pts'][-1]

    sched = {}
    for e in PHASE_EDGES:
        sched[e] = [('B0k', 0.0, fr[e][0]), ('B2c', fr[e][0], fr[e][1]), ('E6', fr[e][1], 1.0)]
    for e in SERVO_EDGES:
        sched[e] = [('D0', 0.0, fr[e][0]), ('E3b', fr[e][0], 1.0)]

    def reveal_fraction(e, t):
        f = 0.0
        for sid, fa, fb in sched[e]:
            r_ = by_id[sid]
            if t < r_['t_mv0']:
                return f
            if t < r_['t_mv1']:
                return fa + (fb - fa) * smooth((t - r_['t_mv0']) / (r_['t_mv1'] - r_['t_mv0']))
            f = fb
        return f

    def reveal_moving(e, t):
        return any(by_id[sid]['t_mv0'] <= t < by_id[sid]['t_mv1'] for sid, _, _ in sched[e])

    def cam_view(c):
        ctr, az, el, dist = c
        ar, er = math.radians(az), math.radians(el)
        view = Vector((-math.cos(er) * math.cos(ar), -math.cos(er) * math.sin(ar), math.sin(er)))
        return ctr, view, dist

    def ghost_set(t):
        s = set()
        b0, b2 = by_id['B0k'], by_id['B2c']
        if b0['t_mv0'] - 0.3 <= t < b0['t_mv1'] + 0.9:
            s |= {p for p in items if p.startswith(GHOST_B0)}
        if b2['t_mv0'] - 0.3 <= t < b2['t_mv1'] + 0.9:
            s |= {p for p in items if p.startswith(GHOST_B2C) and p in placed_ids}
        d0 = by_id['D0']
        if d0['t_mv0'] - 0.3 <= t < d0['t_mv1'] + 0.9:
            s |= {'WNG-001'}                                       # the servo lead runs in a foam groove under the skin
        for r_ in rows:                                            # step data 'ghost': x-ray parts from the step card to the end of the step
            if r_['info'].get('ghost') and r_['t_cam0'] <= t < r_['t_end']:
                s |= {p for p in r_['info']['ghost'] if p in items}
        return s

    def ghost_window(t):
        for r_ in rows:
            if r_['info'].get('ghost') and r_['t_cam0'] <= t < r_['t_end']:
                return r_
        return None

    def world_center(ob):
        cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        return sum(cs, Vector()) / 8

    def part_ends(pid):
        """The two ends of a long part (tube): farthest-pair of sampled vertices at the current pose."""
        ob = items[pid]
        vs = ob.data.vertices
        st = max(1, len(vs) // 300)
        pts = [ob.matrix_world @ vs[k].co for k in range(0, len(vs), st)]
        c = sum(pts, Vector()) / len(pts)
        a_ = max(pts, key=lambda q: (q - c).length)
        b_ = max(pts, key=lambda q: (q - a_).length)
        return a_, b_

    def project(P):
        co = world_to_camera_view(sc, cam, P)
        if co.z <= 0:
            return None
        return (round(co.x, 4), round(1.0 - co.y, 4))

    preshown = {p for p, t_ in show_from.items() if p not in bench_of and any(p in r['parts'] and t_ < r['t_fab0'] for r in rows)}

    def part_mode(p, r, t, ghosts):
        if p in ghosts:
            return 'ghost_spar' if p.startswith('WNG-002') else 'ghost'
        gw = ghost_window(t)
        if gw and r['info'].get('ghost'):                   # inside an x-ray window: the plug being fitted is orange, the ones already bonded teal
            if t >= r['t_mv0']:
                return 'move' if r is gw else 'fab'
        if t >= r['t_mv0']:
            return 'move' if t < r['t_tint1'] else None
        if p in preshown:                                   # B0 make-it beat: the cage parts are teal, then plain
            early = next(e for e, (lt, _) in PRESHOW.items() if lt == r['id'])
            return 'fab' if t < by_id[early]['t_mv0'] else None
        only = FAB_ONLY.get(r['id'])
        if r['fab'] and (not only or p.startswith(only)):
            return 'fab'
        return None

    def pose(t):
        # ---- parts
        state = []
        ghosts = ghost_set(t)
        cage_off = -Vector(b1['dir']) * (b1['visual_mm'] / 1000.0) * (1.0 - smooth((t - b1['t_mv0']) / max(1e-6, b1['t_mv1'] - b1['t_mv0'])))      # the cage unit's offset (the phase leads follow it)
        for r in rows:
            d = Vector(r['dir']) if r['dir'] else Vector()
            u = (t - r['t_mv0']) / max(1e-6, r['t_mv1'] - r['t_mv0'])
            for p in r['parts']:
                if p not in items:
                    continue
                if p in bench_of and (r['bench'] == (t >= b1['t_cam0'])):      # bench parts: their bench step poses them until B1 starts, then B1 (same pose)
                    continue
                if t < show_from[p]:
                    items[p].hide_render = True
                    continue
                items[p].hide_render = False
                k = 1.0 - smooth(u)
                off = -d * (r['visual_mm'] / 1000.0) * k + (B1_START if r['bench'] else Vector())      # bench steps: assemble onto the hub at the B1 start pose
                items[p].matrix_world = Matrix.Translation(off) @ rest[p]
                mode = part_mode(p, r, t, ghosts)
                tint(p, mode)
                state.append((p, round(off.x, 4), round(off.y, 4), round(off.z, 4), mode))
        if bench_t0 <= t < bench_t1:                 # on the bench (B0a-B0j2): only the cage frame parts, the wing and everything else are off the table
            for p in items:
                if p not in bench_of and not items[p].hide_render:
                    items[p].hide_render = True
                    state.append((p, 'bench-hidden'))
        # ---- wires: reveal curves (phase leads), then the full meshes once laid
        rev_state = []
        for e in REVEAL_EDGES:
            f = reveal_fraction(e, t)
            full = t >= by_id[wire_step[e]]['t_mv1']
            ob = reveal[e]['ob']
            ob.hide_render = full or f <= 1e-4
            if not ob.hide_render:
                off_e = cage_off if e in PHASE_EDGES else Vector()       # the phase leads follow the cage unit while it hovers / docks
                reveal[e]['cu'].bevel_factor_end = min(1.0, max(0.0, f))
                ob.matrix_world = Matrix.Translation(off_e)
                on_move = reveal_moving(e, t)
                ob.material_slots[0].link = 'DATA'
                reveal[e]['cu'].materials[0] = MATS['move'] if on_move else (items[e].data.materials[0] if items[e].data.materials else MATS['move'])
                rev_state.append((e, round(f, 4), round(off_e.x, 4), round(off_e.y, 4), round(off_e.z, 4), bool(on_move)))
        for e, ob in be.wires.items():
            lay = by_id[wire_step[e]]
            vis = t >= (lay['t_mv1'] if (e in REVEAL_EDGES or lay['parts']) else lay['t_mv0'])      # wires laid by a marker step show while they are laid
            ob.hide_render = not vis
            if vis:
                tint(e, 'move' if t < lay['t_tint1'] else None)
                state.append((e, 1))
        # ---- camera: ease from the previous step's camera to this one's
        ci = 0
        for q, r in enumerate(rows):
            if t >= r['t_cam0']:
                ci = q
        cur = rows[ci]
        prev = rows[max(ci - 1, 0)]
        p0 = cams_chk[prev['id']] if prev['id'] in cams_chk else cams[prev['id']]
        p1 = cams[cur['id']]
        k = smooth((t - cur['t_cam0']) / cur['cam_dur'])
        cam_c = (p0[0] * (1 - k) + p1[0] * k, p0[1] * (1 - k) + p1[1] * k, p0[2] * (1 - k) + p1[2] * k,
                 p0[3] * (1 - k) + p1[3] * k)
        if cur['info'].get('ghost'):                               # x-ray step: a close-up that follows the plug(s) along the spar
            w = smooth((t - cur['t_cam0']) / 1.0) * (1.0 - smooth((t - (cur['t_mv1'] + 1.0)) / 1.5))
            pl = [world_center(items[p]) for p in cur['parts'] if p in items and not items[p].hide_render]
            if w > 1e-4 and pl:
                pc = sum(pl, Vector()) / len(pl)
                spread = max([(q - pc).length for q in pl] + [0.0])
                az_f, el_f = GHOST_VIEW
                _, v_f, _ = cam_view((pc, az_f, el_f, 1.0))
                up_f = v_f.cross(Vector((0, 0, 1))).cross(v_f).normalized()
                d_f = GHOST_DIST + 2.0 * spread
                pc = pc - up_f * (0.045 * 2 * d_f * TAN_V)         # subject in the free band between header and card
                cam_c = (cam_c[0] * (1 - w) + pc * w, cam_c[1] * (1 - w) + az_f * w, cam_c[2] * (1 - w) + el_f * w, cam_c[3] * (1 - w) + d_f * w)
        if cur['id'] in cams_chk and t >= cur['t_chk0']:
            kk = smooth((t - cur['t_chk0']) / T_CHK_CAM)
            q = cams_chk[cur['id']]
            cam_c = (cam_c[0] * (1 - kk) + q[0] * kk, cam_c[1] * (1 - kk) + q[1] * kk, cam_c[2] * (1 - kk) + q[2] * kk, cam_c[3] * (1 - kk) + q[3] * kk)
        if t >= rows[-1]['t_stage_end']:                           # the whole aircraft: pull back and swing round
            k = smooth((t - rows[-1]['t_stage_end']) / 1.6)
            e_ = cams['END']
            last = cams[rows[-1]['id']]
            az_ = e_[1] + 22 * smooth((t - rows[-1]['t_stage_end']) / T_END)
            cam_c = (last[0] * (1 - k) + e_[0] * k, last[1] * (1 - k) + az_ * k, last[2] * (1 - k) + e_[2] * k,
                     last[3] * (1 - k) + e_[3] * k)
            for p in sorted(placed_ids):
                if p in items:
                    tint(p, None)
        ctr, view, dist = cam_view(cam_c)
        look(cam, ctr + view * dist, ctr)
        below = (ctr + view * dist).z < floor.location.z + 0.06     # D-199: camera under the stage floor (views from below): hide the floor and its shadow blob so the frame is not blank
        floor.hide_render = below
        caz = math.atan2(view.y, view.x)
        for lo_, daz, lel, dd in lights:
            aa, ee = caz + math.radians(daz), math.radians(lel)
            loc = ctr + Vector((math.cos(ee) * math.cos(aa), math.cos(ee) * math.sin(aa), math.sin(ee))) * dd
            look(lo_, loc, ctr, Vector((0, 0, 1)) if lel < 85 else Vector((1, 0, 0)))
        blob_s.default_value = (0.55, 0.9, 1.0)
        blob_c.default_value = (full_c.x, 0.0, 0.0)
        blob_op.default_value = 0.0 if below else 0.35
        bpy.context.view_layer.update()
        # ---- anchors of the callouts and dimension lines of the active step (screen position, 0..1)
        anc = {}
        if t < rows[-1]['t_stage_end'] and cur['t_fab0'] - 1e-6 <= t < cur['t_end']:
            info = cur['info']
            lab = []
            for tgt_, text in info['callouts']:
                P = None
                if isinstance(tgt_, tuple):
                    P = Vector(tgt_[1])
                elif tgt_ in reveal and not reveal[tgt_]['ob'].hide_render:
                    P = head_pos(tgt_, reveal_fraction(tgt_, t)) + (cage_off if tgt_ in PHASE_EDGES else Vector())          # the moving tip of the lead being threaded
                elif tgt_ in items and not items[tgt_].hide_render:
                    P = world_center(items[tgt_])
                if P is None:
                    continue
                xy = project(P)
                if xy and 0.02 < xy[0] < 0.98 and 0.04 < xy[1] < 0.98:
                    lab.append((text, xy))
            anc['labels'] = lab
            fab = cur['fab']
            dims = []
            if fab and t < cur['t_mv0'] and fab.get('dims'):
                for pid, text in fab['dims']:
                    if pid in items and not items[pid].hide_render:
                        pa, pb = part_ends(pid)
                        xa, xb = project(pa), project(pb)
                        if xa and xb:
                            dims.append((text, xa, xb))
            anc['dims'] = dims
        return (tuple(state), tuple(rev_state), tuple(round(v, 3) for v in (*cam_c[0], cam_c[1], cam_c[2], cam_c[3]))), anc

    sc.render.resolution_percentage = 100
    if a.frames:
        frames = [int(f) for f in a.frames.split(',') if f.strip()]
    elif a.range:
        f0, f1 = [int(v) for v in a.range.split(':')]
        frames = list(range(f0, min(f1, nframes), a.every))
    else:
        frames = list(range(0, nframes, a.every))
    os.makedirs(a.out, exist_ok=True)
    t0, prev_key, prev_name, n_new = time.time(), None, None, 0
    fmap = {}
    for f in frames:
        key, anc = pose(f / FPS)
        name = 'raw_%05d.png' % f
        if key == prev_key and prev_name:
            name = prev_name
        else:
            sc.render.filepath = os.path.join(a.out, name)
            bpy.ops.render.render(write_still=True)
            n_new += 1
        prev_key, prev_name = key, name
        fmap[f] = dict(raw=name, anc=anc)
        if f % 20 == 0:
            print('FRAME %d / %d rendered %d  %.0f s' % (f, nframes, n_new, time.time() - t0), flush=True)
    tag = a.range.replace(':', '_') if a.range else ('frames' if a.frames else 'all')
    json.dump(fmap, open(os.path.join(a.out, 'map_%s.json' % tag), 'w'))
    print('RENDER_TOTAL %.1f s for %d frames (%d rendered)' % (time.time() - t0, len(frames), n_new))


def blender_encode(argv):
    """Named PNGs (a list file, one name per line, a name may repeat) -> H.264 MP4 with Blender's FFmpeg (VSE)."""
    import argparse
    import bpy
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--list', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--crf', default='MEDIUM')
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
    ff.constant_rate_factor = a.crf
    ff.gopsize = FPS * 2
    ff.ffmpeg_preset = 'GOOD'
    ff.audio_codec = 'NONE'
    sc.render.filepath = a.out
    sc.render.use_file_extension = False
    bpy.ops.render.render(animation=True)
    print('ENCODED', a.out)


# =====================================================================================================================
# overlay (system Python + Pillow)
# =====================================================================================================================
INK, ORANGE, MUTED, SUB, TEAL, GREEN = (18, 22, 25), (194, 84, 10), (107, 114, 128), (45, 54, 66), (19, 137, 127), (28, 120, 70)


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


def make_fonts(k):
    sans_b = ['IBMPlexSans-SemiBold.ttf', 'seguisb.ttf', 'segoeuib.ttf', 'arialbd.ttf']
    sans_m = ['IBMPlexSans-Medium.ttf', 'seguisb.ttf', 'segoeui.ttf', 'arial.ttf']
    sans_r = ['IBMPlexSans-Regular.ttf', 'segoeui.ttf', 'arial.ttf']
    mono = ['IBMPlexMono-Medium.ttf', 'CascadiaMono.ttf', 'consola.ttf', 'cour.ttf']
    return dict(big=_font(sans_b, int(40 * k)), h1=_font(sans_b, int(25 * k)), h2=_font(sans_m, int(21 * k)), body=_font(sans_r, int(19 * k)),
                small=_font(sans_r, int(16 * k)), mono=_font(mono, int(15 * k)), label=_font(sans_m, int(17 * k)), badge=_font(sans_b, int(30 * k)))


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


_NAMES = None


def part_names():
    """{key: (short name, count, [ids])} per step id, for the stage title cards (system Python: reads the CAD part table)."""
    global _NAMES
    if _NAMES is None:
        sys.path.insert(0, CAD_A)
        import a_model as m
        _NAMES = m
    return _NAMES


def key_of(pid):
    return re.sub(r'-(UR|UL|LR|LL|RU|RL|LU|[RLC])$', '', pid)


SHORT = {'WNG-001': 'Wing core (XPS + tape)', 'WNG-002': 'Spar, CF 12x10, 900 mm', 'WNG-003': 'Spar plug (PETG)', 'WNG-004': 'Spar plug (PETG)', 'WNG-005': 'Spar plug (PETG)',
         'CGE-001': 'Hub (PETG)', 'CGE-002': 'Arm, CF 12x10, 245 mm', 'CGE-003': 'Motor cup (PETG)', 'CGE-004': 'Bridge, CF 16x14, 108 mm', 'CGE-005': 'V strut, CF 6x4.5',
         'CGE-006': 'Bridge saddle', 'CGE-007': 'Strut clamp', 'CGE-008': 'Pack tray (PETG)', 'PRP-001': 'Motor MN2212 KV780', 'PRP-002': 'Prop APC 9x4.5 (MR / MRP)',
         'PRP-003': 'ESC SpeedyBee 4-in-1', 'PRP-004': 'Prop adapter', 'PRP-005': 'Spinner nut', 'FIN-005': 'Rib saddle (PETG)', 'HRN-003': 'Phase-lead raceway',
         'HRN-004': 'Hub conduit', 'WNG-009': 'Damper stator + silicone', 'WNG-010': 'Damper rotor', 'FIN-002': 'Fin rib, CF 14x12', 'FIN-006': 'Rib fairing (XPS)',
         'WNG-006': 'Elevon (XPS + tape)', 'WNG-007': 'Balance: lead strip + tabs', 'WNG-008': 'Lens cap (PETG)', 'FIN-004': 'Fin fairing (XPS 3 mm)', 'FIN-003': 'Fin root block (PETG)',
         'FIN-001': 'Fin tube, CF 16x14, 360 mm', 'GER-001': 'Foot shoe (PETG)', 'GER-002': 'Foot pad (EVA/PE)', 'MEC-001': 'Servo EMAX ES3054HV', 'MEC-002': 'Servo arm',
         'HWC-002': 'Arm screw M2x6', 'MEC-004': 'Control horn', 'MEC-003': 'Pushrod + clevis', 'MEC-005': 'Clevis pin', 'AVN-006': 'Pitot probe', 'AVN-001': 'Avionics plate (PETG)',
         'HWC-003': 'M2 thin nuts', 'AVN-007': 'Foam-tape pads', 'AVN-002': 'Flight controller Kakute F405', 'AVN-003': 'Receiver RP3', 'AVN-004': 'GPS + compass',
         'AVN-005': 'Airspeed board', 'HWC-001': 'FC screws M2x25', 'PWR-003': 'Anti-slip pad', 'PWR-001': 'Pack Tattu 2300 4S', 'HRN-002': 'XT60 female + tail', 'PWR-002': 'Pack strap',
         'AVN-008': 'Bay cover (PETG)'}


def stage_parts(si, rows):
    ids = list(dict.fromkeys(p for r in rows if r['stage'] == si for p in r['parts']))      # D-202: bench parts are listed again by B1
    groups = {}
    for p in ids:
        groups.setdefault(key_of(p), []).append(p)
    out = []
    for k, pp in groups.items():
        nm = SHORT.get(k, k)
        out.append('%s%s  %s' % ('%dx ' % len(pp) if len(pp) > 1 else '', nm, k if len(pp) > 1 else pp[0]))
    return out


def stage_tools(si, rows):
    seen, out = set(), []
    for r in rows:
        if r['stage'] != si:
            continue
        for tl in r['info']['tools'].split(', '):
            tl = tl.strip()
            key = tl.lower().rstrip('s')
            if tl and key not in seen and tl.lower() != 'none' and not tl.lower().startswith('as '):
                seen.add(key)
                out.append(tl)
    return out


def fmt_min(mn):
    h, m_ = divmod(int(round(mn)), 60)
    return ('%d h %02d min' % (h, m_)) if h else '%d min' % m_


def pill(d, x, y, lines, font, k, fg=(18, 22, 25), bg=(255, 255, 255, 240), bar=ORANGE, pad=8, line_h=None):
    line_h = line_h or int(font.size * 1.25)
    w_ = max(d.textlength(s, font=font) for s in lines) + 2 * pad * k + 4 * k
    h_ = line_h * len(lines) + 2 * pad * k * 0.6
    d.rounded_rectangle((x, y, x + w_, y + h_), radius=int(6 * k), fill=bg, outline=(203, 210, 219, 255))
    d.rectangle((x, y + 4 * k, x + 3 * k, y + h_ - 4 * k), fill=bar + (255,))
    for i, s in enumerate(lines):
        d.text((x + pad * k + 3 * k, y + pad * k * 0.6 + i * line_h), s, font=font, fill=fg + (255,))
    return w_, h_


def place_labels(d, labs, F, k, sw, sh, avoid):
    """Greedy label placement around the anchors: nearest free spot in 8 directions, no overlap, inside the safe band."""
    placed = []
    safe = (20 * k, 128 * k, sw - 20 * k, sh - 196 * k)
    out = []
    boxes = list(avoid)

    def overlaps(b):
        return any(not (b[2] < c[0] or b[0] > c[2] or b[3] < c[1] or b[1] > c[3]) for c in boxes)
    for text, (ax, ay) in sorted(labs, key=lambda q: q[1][1]):
        axp, ayp = ax * sw, ay * sh
        lines = wrap(d, text, F['label'], 400 * k)
        w_ = max(d.textlength(s, font=F['label']) for s in lines) + 28 * k
        h_ = int(F['label'].size * 1.25) * len(lines) + 10 * k
        best = None
        for rad in (58, 96, 140, 190):
            for ang in (-60, 60, -120, 120, 0, 180, -90, 90, -30, 30, -150, 150):
                cx = axp + rad * k * math.cos(math.radians(ang))
                cy = ayp + rad * k * math.sin(math.radians(ang))
                x = cx - (w_ if math.cos(math.radians(ang)) < -0.2 else 0 if math.cos(math.radians(ang)) > 0.2 else w_ / 2)
                y = cy - h_ / 2
                x = min(max(x, safe[0]), safe[2] - w_)
                y = min(max(y, safe[1]), safe[3] - h_)
                b = (x, y, x + w_, y + h_)
                if not overlaps(b) and not (b[0] < axp < b[2] and b[1] < ayp < b[3]):
                    best = b
                    break
            if best:
                break
        if not best:
            best = (min(max(axp + 30 * k, safe[0]), safe[2] - w_), min(max(ayp - 80 * k, safe[1]), safe[3] - h_), 0, 0)
            best = (best[0], best[1], best[0] + w_, best[1] + h_)
        boxes.append(best)
        out.append((lines, best, (axp, ayp)))
    return out


_G = {}


def _init(rows, total, k):
    _G['rows'], _G['total'], _G['k'], _G['F'] = rows, total, k, make_fonts(k)


def overlay(src, dst, f, fm, sw, sh):
    from PIL import Image, ImageDraw
    rows, total, k, F = _G['rows'], _G['total'], _G['k'], _G['F']
    rowinfo = frame_info(rows, total, f)
    im = Image.open(src).convert('RGBA')
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    si, row, stepno, kind = rowinfo
    t = f / FPS
    info = row['info']
    nsteps = len(rows)
    if kind == 'title':
        d.rectangle((0, 0, sw, sh), fill=(250, 251, 253, 214))
    # ---- header
    d.text((28 * k, 20 * k), 'Concept A quad tailsitter  /  BUILD GUIDE', font=F['h2'], fill=INK + (235,))
    d.text((28 * k, 46 * k), 'follows qp/A/BUILD-GUIDE-A.md', font=F['mono'], fill=MUTED + (235,))
    dx0 = sw - 28 * k - len(STAGES) * 18 * k
    for q in range(len(STAGES)):
        cx, cy = dx0 + q * 18 * k + 9 * k, 32 * k
        if q < si or kind == 'end':
            d.ellipse((cx - 5 * k, cy - 5 * k, cx + 5 * k, cy + 5 * k), fill=INK + (210,))
        elif q == si:
            d.ellipse((cx - 7 * k, cy - 7 * k, cx + 7 * k, cy + 7 * k), fill=ORANGE + (255,))
        else:
            d.ellipse((cx - 5 * k, cy - 5 * k, cx + 5 * k, cy + 5 * k), outline=MUTED + (220,), width=max(1, int(k)))
    x0, x1 = 28 * k, sw - 28 * k
    anc = fm.get('anc') or {}

    if kind == 'title':
        d.text((x0, 84 * k), 'STAGE %d OF %d' % (si + 1, len(STAGES)), font=F['mono'], fill=ORANGE + (255,))
        ttl = wrap(d, STAGES[si][0], F['big'], sw - 2 * x0)
        for i, s in enumerate(ttl):
            d.text((x0, 106 * k + i * 48 * k), s, font=F['big'], fill=INK + (255,))
        y = (106 + 48 * len(ttl) + 18) * k
        colw = (sw - 3 * x0) / 2
        d.text((x0, y), 'PARTS YOU FIT IN THIS STAGE', font=F['mono'], fill=ORANGE + (255,))
        d.text((x0 + colw + x0, y), 'TOOLS AND CONSUMABLES', font=F['mono'], fill=ORANGE + (255,))
        yy = y + 24 * k
        for s in stage_parts(si, rows)[:14]:
            for j, ln in enumerate(wrap(d, s, F['body'], colw)):
                d.text((x0 + 14 * k * (j > 0), yy), ('- ' if j == 0 else '') + ln, font=F['body'], fill=INK + (255,))
                yy += 24 * k
        yy = y + 24 * k
        for s in stage_tools(si, rows)[:14]:
            for j, ln in enumerate(wrap(d, s, F['body'], colw)):
                d.text((x0 + colw + x0 + 14 * k * (j > 0), yy), ('- ' if j == 0 else '') + ln, font=F['body'], fill=INK + (255,))
                yy += 24 * k
        mn = sum(r['info']['min'] for r in rows if r['stage'] == si)
        ids = [r['id'] for r in rows if r['stage'] == si]
        cures = [r['info']['cure'] for r in rows if r['stage'] == si and r['info']['cure']]
        cures = [c for c in cures if '24 h' in c][:1] or cures[-1:]
        foot = 'Steps %s   |   hands-on %s (EST)%s' % (' '.join(ids), fmt_min(mn), ('   |   cure: ' + cures[0].split(' (')[0].split(': ')[0]) if cures else '')
        d.rounded_rectangle((x0, sh - 74 * k, x1, sh - 28 * k), radius=int(8 * k), fill=(255, 255, 255, 245), outline=(203, 210, 219, 255))
        d.text((x0 + 18 * k, sh - 62 * k), foot, font=F['h2'], fill=INK + (255,))
    elif kind == 'end':
        x0_, y0_, y1_ = x0, sh - 190 * k, sh - 28 * k
        d.rounded_rectangle((x0_, y0_, x1, y1_), radius=int(8 * k), fill=(255, 255, 255, 245), outline=(203, 210, 219, 255))
        d.text((x0_ + 22 * k, y0_ + 14 * k), 'BUILD COMPLETE', font=F['mono'], fill=ORANGE + (255,))
        d.text((x0_ + 22 * k, y0_ + 38 * k), 'All %d plan parts fitted in %d steps (CAD)' % (len({p for r_ in rows for p in r_['parts']}), nsteps), font=F['h1'], fill=INK + (255,))
        for i, s in enumerate(['Now: weigh-in (gate 1.47 kg), CG 19-26 mm aft of the leading edge, motor directions with props OFF.',
                               'Written guide: qp/A/BUILD-GUIDE-A.md (section 14). Time EST %s hands-on.' % fmt_min(sum(r['info']['min'] for r in rows))]):
            d.text((x0_ + 22 * k, y0_ + 82 * k + i * 30 * k), s, font=F['body'], fill=SUB + (255,))
    else:
        # ---- make-it banner
        fab = row['fab'] if (t < row['t_mv0'] and row['fab']) else (row['marker_chip'] if (row['marker_chip'] and row['t_mv0'] - 0.01 <= t < row['t_mv1'] + 1.5) else None)
        if fab and kind == 'step':
            txt = fab['text']
            head = 'MAKE IT' if row['fab'] else ('THREAD' if fab['kind'] == 'thread' else 'SOLDER')
            lines = wrap(d, txt, F['h2'], sw - 2 * x0 - 150 * k)[:2]
            bh = (14 + 26 * len(lines) + (24 if fab.get('orient') else 0)) * k
            by = 70 * k
            d.rounded_rectangle((x0, by, x1, by + bh), radius=int(8 * k), fill=TEAL + (240,))
            d.text((x0 + 16 * k, by + 8 * k), head, font=F['mono'], fill=(255, 255, 255, 255))
            for i, s in enumerate(lines):
                d.text((x0 + 120 * k, by + 8 * k + i * 26 * k), s, font=F['h2'], fill=(255, 255, 255, 255))
            if fab.get('orient'):
                d.text((x0 + 120 * k, by + 8 * k + len(lines) * 26 * k), 'Print orientation: %s' % fab['orient'], font=F['small'], fill=(255, 255, 255, 255))
                bx, byy = x1 - 54 * k, by + bh / 2
                d.rectangle((bx - 22 * k, byy + 16 * k, bx + 22 * k, byy + 20 * k), fill=(255, 255, 255, 255))      # bed
                d.line((bx, byy + 12 * k, bx, byy - 14 * k), fill=(255, 255, 255, 255), width=max(2, int(2 * k)))
                d.polygon([(bx - 6 * k, byy - 10 * k), (bx + 6 * k, byy - 10 * k), (bx, byy - 20 * k)], fill=(255, 255, 255, 255))
        # ---- dimension lines
        for text, pa, pb in (anc.get('dims') or []):
            ax_, ay_, bx_, by_ = pa[0] * sw, pa[1] * sh, pb[0] * sw, pb[1] * sh
            vx, vy = bx_ - ax_, by_ - ay_
            L = math.hypot(vx, vy) or 1
            nx, ny = -vy / L, vx / L
            if ny > 0:
                nx, ny = -nx, -ny
            o = 26 * k
            p0, p1 = (ax_ + nx * o, ay_ + ny * o), (bx_ + nx * o, by_ + ny * o)
            col = TEAL + (255,)
            d.line((ax_, ay_, p0[0], p0[1]), fill=col, width=max(1, int(1.5 * k)))
            d.line((bx_, by_, p1[0], p1[1]), fill=col, width=max(1, int(1.5 * k)))
            d.line((p0[0], p0[1], p1[0], p1[1]), fill=col, width=max(2, int(2.5 * k)))
            for (px, py) in (p0, p1):
                d.ellipse((px - 4 * k, py - 4 * k, px + 4 * k, py + 4 * k), fill=col)
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            tw = d.textlength(text, font=F['label'])
            d.rounded_rectangle((mx - tw / 2 - 8 * k, my - 13 * k, mx + tw / 2 + 8 * k, my + 13 * k), radius=int(5 * k), fill=(255, 255, 255, 250), outline=TEAL + (255,))
            d.text((mx - tw / 2, my - 10 * k), text, font=F['label'], fill=TEAL + (255,))
        # ---- callouts with leader lines
        if kind == 'step' and anc.get('labels'):
            avoid = [(x0, sh - 196 * k, x1, sh), (0, 0, sw, 124 * k)] if False else [(x0, sh - 196 * k, x1, sh)]
            for lines, b, (axp, ayp) in place_labels(d, anc['labels'], F, k, sw, sh, avoid):
                ex = min(max(axp, b[0]), b[2])
                ey = min(max(ayp, b[1]), b[3])
                d.line((ex, ey, axp, ayp), fill=ORANGE + (235,), width=max(2, int(2 * k)))
                d.ellipse((axp - 5 * k, ayp - 5 * k, axp + 5 * k, ayp + 5 * k), fill=ORANGE + (255,), outline=(255, 255, 255, 255), width=max(1, int(1.5 * k)))
                pill(d, b[0], b[1], lines, F['label'], k, line_h=int(F['label'].size * 1.25))
        # ---- card
        if kind == 'check':
            lines_all = []
            for c in info['cp']:
                lines_all += wrap(d, c, F['h2'], sw - 2 * x0 - 120 * k)
            ch = (74 + 29 * len(lines_all)) * k
            y1_ = sh - 28 * k
            y0_ = y1_ - ch
            d.rounded_rectangle((x0, y0_, x1, y1_), radius=int(10 * k), fill=(246, 252, 248, 247), outline=GREEN + (255,), width=max(2, int(3 * k)))
            d.text((x0 + 22 * k, y0_ + 14 * k), 'CHECKPOINT  after step %s: do not go on until it passes' % row['id'], font=F['mono'], fill=GREEN + (255,))
            y = y0_ + 46 * k
            for c in info['cp']:
                ls = wrap(d, c, F['h2'], sw - 2 * x0 - 120 * k)
                d.rectangle((x0 + 24 * k, y + 4 * k, x0 + 42 * k, y + 22 * k), outline=GREEN + (255,), width=max(2, int(2 * k)))
                for j, ln in enumerate(ls):
                    d.text((x0 + 58 * k, y), ln, font=F['h2'], fill=INK + (255,))
                    y += 29 * k
        else:
            chars_w = x1 - x0 - 120 * k - 24 * k
            l1 = wrap(d, info['line'], F['h1'], chars_w)[:2]
            l3 = wrap(d, info['check'], F['body'], chars_w - 90 * k)[:2]
            l2 = wrap(d, info['tools'], F['body'], chars_w - 90 * k)[:1]
            ch = (22 + 32 * len(l1) + 28 * len(l2) + 26 * len(l3) + 34) * k
            y1_ = sh - 28 * k
            y0_ = y1_ - max(ch, 128 * k)
            d.rounded_rectangle((x0, y0_, x1, y1_), radius=int(10 * k), fill=(255, 255, 255, 244), outline=(203, 210, 219, 255))
            d.rounded_rectangle((x0 + 14 * k, y0_ + 14 * k, x0 + 100 * k, y0_ + 76 * k), radius=int(8 * k), fill=ORANGE + (255,))
            bw = d.textlength(row['id'], font=F['badge'])
            d.text((x0 + 57 * k - bw / 2, y0_ + 24 * k), row['id'], font=F['badge'], fill=(255, 255, 255, 255))
            d.text((x0 + 14 * k, y0_ + 84 * k), 'STEP %d / %d' % (stepno, nsteps), font=F['mono'], fill=MUTED + (255,))
            tx = x0 + 120 * k
            y = y0_ + 12 * k
            for ln in l1:
                d.text((tx, y), ln, font=F['h1'], fill=INK + (255,))
                y += 32 * k
            y += 4 * k
            for ln in l2:
                d.text((tx, y), 'TOOLS', font=F['mono'], fill=ORANGE + (255,))
                d.text((tx + 62 * k, y - 2 * k), ln, font=F['body'], fill=SUB + (255,))
                y += 28 * k
            for j, ln in enumerate(l3):
                if j == 0:
                    d.text((tx, y), 'CHECK', font=F['mono'], fill=GREEN + (255,))
                d.text((tx + 62 * k, y - 2 * k), ln, font=F['body'], fill=SUB + (255,))
                y += 26 * k
            tstr = '%s EST' % fmt_min(info['min']) + (' | ' + info['cure'].split(':')[0].split('(')[0].strip()[:40] if info['cure'] else '')
            tw = d.textlength(tstr, font=F['mono'])
            d.text((x1 - 16 * k - tw, y1_ - 26 * k), tstr, font=F['mono'], fill=MUTED + (255,))
    # ---- progress (by step, so that the picture stays constant while a card is read)
    prog = (stepno - 1) / float(nsteps) if kind != 'end' else 1.0
    by = sh - 12 * k
    d.rounded_rectangle((x0, by - 2 * k, x1, by + 1 * k), radius=2, fill=(220, 225, 232, 255))
    d.rounded_rectangle((x0, by - 2 * k, max(x0 + 3, x0 + (x1 - x0) * prog), by + 1 * k), radius=2, fill=ORANGE + (255,))
    Image.alpha_composite(im, lay).convert('RGB').save(dst, optimize=False, compress_level=1)


def _overlay_job(args):
    return overlay(*args)


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
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'a_build_film'))        # GBs of PNGs: outside the repo
    ap.add_argument('--skip-render', action='store_true')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--crf', default='MEDIUM', help='H.264 quality of the whole film (lowered until under --max-mb)')
    ap.add_argument('--stage-crf', default='MEDIUM')
    ap.add_argument('--max-mb', type=float, default=13.0)
    a = ap.parse_args()
    t0 = time.time()
    a.work = os.path.abspath(a.work)
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    rows, total = timeline()
    nframes = int(total * FPS)
    print('%d steps, %d stages, %.1f s (%.1f min), %d frames' % (len(rows), len(STAGES), total, total / 60, nframes))
    me = os.path.abspath(__file__)
    every, scale = (4, 0.5) if a.preview else (1, 1.0)
    chunk_maps = []
    if not a.skip_render:
        base = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', a.work, '--samples', str(a.samples), '--scale', str(scale)]
        if a.frames:
            run(base + ['--frames', a.frames])
        else:
            cost = moving_frames(rows, total)
            cum, tot = [], 0
            for c in cost:
                tot += c
                cum.append(tot)
            nw = 1 if a.preview else max(1, a.workers)
            cuts = [0]
            for i in range(1, nw):
                cuts.append(next(f for f, c in enumerate(cum) if c >= tot * i / nw))
            cuts.append(nframes)
            procs = []
            for i in range(nw):
                cmd = base + ['--range', '%d:%d' % (cuts[i], cuts[i + 1]), '--every', str(every)]
                print('> worker %d: frames %d-%d' % (i, cuts[i], cuts[i + 1] - 1), flush=True)
                lg = open(os.path.join(a.work, 'worker_%d.log' % i), 'w')
                procs.append((subprocess.Popen(cmd, stdout=lg, stderr=subprocess.STDOUT), lg))
            for p, lg in procs:
                p.wait()
                lg.close()
                if p.returncode != 0:
                    raise SystemExit('blender worker failed, see worker_*.log in ' + a.work)
    fmap = {}
    for fn in sorted(os.listdir(a.work)):
        if fn.startswith('map_') and fn.endswith('.json'):
            if a.frames and fn != 'map_frames.json':
                continue
            if not a.frames and fn == 'map_frames.json':
                continue
            for kk, v in json.load(open(os.path.join(a.work, fn))).items():
                fmap[int(kk)] = v
    frames = sorted(fmap)
    if a.frames:
        frames = [int(x) for x in a.frames.split(',')]
    print('mapped %d frames, %d distinct pictures' % (len(frames), len({fmap[f]['raw'] for f in frames})))
    # ---- overlays: one per distinct (picture, card state)
    k = Image.open(os.path.join(a.work, fmap[frames[0]]['raw'])).size[0] / float(W)
    sw, sh = Image.open(os.path.join(a.work, fmap[frames[0]]['raw'])).size
    keys, jobs, name_of = {}, [], {}
    for f in frames:
        fm = fmap[f]
        info = frame_info(rows, total, f)
        row = info[1]
        t = f / FPS
        fab_on = bool(row['fab'] and t < row['t_mv0']) or bool(row['marker_chip'] and row['t_mv0'] - 0.01 <= t < row['t_mv1'] + 1.5)
        key = (fm['raw'], info[3], row['id'], fab_on, json.dumps(fm['anc'], sort_keys=True))
        if key not in keys:
            nm = 'lab_%05d.png' % len(keys)
            keys[key] = nm
            jobs.append((os.path.join(a.work, fm['raw']), os.path.join(a.work, nm), f, fm, sw, sh))
        name_of[f] = keys[key]
    print('%d overlay pictures' % len(jobs), flush=True)
    done = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=8, initializer=_init, initargs=(rows, total, k)) as ex:
        for _ in ex.map(_overlay_job, jobs, chunksize=8):
            done += 1
            if done % 300 == 0:
                print('OVERLAY %d / %d' % (done, len(jobs)), flush=True)
    if a.frames or a.preview:
        print('test frames in', a.work)
        json.dump({str(f): name_of[f] for f in frames}, open(os.path.join(a.work, 'lab_index.json'), 'w'))
        return

    def encode(names, out, crf):
        lst = os.path.join(a.work, '_list.txt')
        open(lst, 'w').write('\n'.join(names))
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work, '--list', lst, '--out', out, '--crf', crf])

    # whole film: the CRF is lowered until the file is under the artifact limit
    allnames = [name_of[f] for f in frames]
    out_all = os.path.join(OUT, 'a-build.mp4')
    for crf in [a.crf, 'LOW', 'VERYLOW', 'LOWEST']:
        encode(allnames, out_all, crf)
        mb = os.path.getsize(out_all) / 1e6
        print('a-build.mp4 crf %s: %.2f MB' % (crf, mb))
        if mb < a.max_mb:
            break
    sf = stage_frames(rows, total)
    for si, (f0, f1) in sf.items():
        n = '%02d' % (si + 1)
        o = os.path.join(OUT, 'stage-%s.mp4' % n)
        for crf in [a.stage_crf, 'LOW', 'VERYLOW']:
            encode([name_of[f] for f in range(f0, f1 + 1)], o, crf)
            if os.path.getsize(o) / 1e6 < a.max_mb:
                break
        Image.open(os.path.join(a.work, name_of[f1])).convert('RGB').save(os.path.join(OUT, 'stage-%s.webp' % n), quality=84, method=6)
    # poster: the first stage title card is not a good poster; use the end frame
    Image.open(os.path.join(a.work, name_of[nframes - 1])).convert('RGB').save(os.path.join(OUT, 'a-build-poster.webp'), quality=84, method=6)
    meta = {'steps': [{kk: v for kk, v in r.items() if kk not in ('parts', 'info', 'fab', 'marker_chip')} | {'n_parts': len(r['parts'])} for r in rows],
            'stages': [{'n': i + 1, 'title': t, 'steps': ids, 'frames': sf[i]} for i, (t, ids) in enumerate(STAGES)],
            'fps': FPS, 'frames': nframes, 'seconds': round(total, 1)}
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
