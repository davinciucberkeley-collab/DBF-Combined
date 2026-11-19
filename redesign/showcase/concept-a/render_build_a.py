"""render_build_a.py - the concept A build film: the 66 steps of qp/A/cad/a_assembly_plan.py in 10 stages, one clip + one still per
stage and the full film, made to FOLLOW the written guide qp/A/BUILD-GUIDE-A.md (both read qp/A/cad/a_build_steps.py).

    python redesign/showcase/concept-a/render_build_a.py               # camera plan + render + overlay + encode everything (about 1 h, workers in parallel)
    python redesign/showcase/concept-a/render_build_a.py --preview     # half size, every 4th frame, no encode
    python redesign/showcase/concept-a/render_build_a.py --frames 40,300   # test frames only (render + overlay, no encode)
    python redesign/showcase/concept-a/render_build_a.py --skip-render      # redo overlay + encode from the frames already in --work
    blender -b --factory-startup -P render_build_a.py -- render --out DIR --audit --every 4   # no pictures: what is visible / where the camera is, then
    python redesign/showcase/concept-a/audit_film.py DIR                                       # -> FILM-AUDIT.md (per-step audit)

Run with the system Python (needs Pillow). Steps, as render_build.py (K09-L):
  0. camplan  Blender computes the camera view of every step (cam_plan.json); the schedule reads it so that a camera move takes as long as its zoom
              change, swing and shift need (cam_duration). The renderer refuses a stale cam_plan.json.
  1. render   Blender (EEVEE) builds the concept A CAD from redesign/qp/A/cad/model through redesign/blender/blender_backend.py and poses
              each part per frame. Several Blender workers render disjoint frame ranges in parallel. Frames identical to the previous
              one are not rendered again (the overlay step reuses the picture). Each worker also writes, per frame, the 2-D screen
              position of every callout anchor (projected through the real camera).
  2. overlay  Pillow: the stage title card (fades in and out), the step card (step id, one-line instruction, tools, key check), callout labels with
              leader lines on the parts being fitted (only parts that are on screen), dimension lines on cut tubes, make-it banners for printed / cut
              parts, checkpoint cards, stage dots and progress.
  3. encode   Blender's FFmpeg (VSE): a-build.mp4 + stage-NN.mp4 (H.264) and stage-NN.webp (last frame of each stage).

Camera (2026-11-18 audit, FILM-AUDIT.md): one keyframed shot, smoothstep between the views of consecutive steps (distance interpolated geometrically); a stage opens
wide (everything placed so far) behind the title card and glides to the first step's close view before the card fades; a checkpoint pulls back and the next
move starts from that view. Servo steps look from the aft side (the cage motors are in front of the pockets from the nose side). The x-ray (ghost) steps A3-A5
follow the plug along the see-through spar; D1 and D0 see the core through so the servo pocket and the lead in its groove show; the wing is an x-ray (not hidden)
while the cage frame is built on the bench.

Every part motion is the one of a_assembly_plan.STEPS (direction, travel), which a_assembly.py swept against all parts already placed
(out/ASSEMBLY.md). For legibility a motion shorter than MIN_TRAVEL_MM is started MIN_TRAVEL_MM away along the same line; the part of that
line beyond the checked travel is approach in free air and is NOT part of the swept check (A3-A5 start just outside the spar tip: VIS_TRAVEL_MM). Steps with
travel 0 (A1 core on the bench, E5 strap) simply appear. What this film ADDS to the plan, none of it a part motion:
  * make-it beats (the part shown at its start pose in teal with its cut length or print label, before it moves in),
  * B0 (D-202): the cage frame is BUILT ON THE BENCH, part by part, in the bench steps B0b-B0j2 (a_assembly_plan.BENCH): the hub appears alone, then
    each step moves its own parts in along the plan's direction and travel, all offset by the B1 start pose (the place where the finished cage unit
    hovers before it docks) so that they assemble onto the hub there. Parts of later bench steps are not shown yet, the wing stays as an x-ray, and
    one camera frames the whole cage unit for B0a-B0j2. Bench parts get the same make-it beat (teal, print / cut / fit label) as other parts. B1
    docks the finished frame (with the saddle, clips, motors and props, which come on in B1) exactly as in the plan.
  * B0k: the cage unit (without saddle, clips, motors and props) hovers at its B1 start pose, shown semi-transparent while the
    phase leads are threaded along the arm bores (a progressive reveal along the wire route, from out/wire_inventory.json), B2c threads
    them on through the hub conduit, raceway and ditch, E6 solders the last part to the ESC pads. The reveal follows the cage unit; a bead marks the
    fish-wire tip. The servo leads: D0 threads them from the pocket along the groove to the slit, E3b solders the last part to the FC pads.
Skin tape, hinge tape and epoxy fillets are not drawn (as in the plan). Parts that the plan does not place are not shown.
Outputs: redesign/showcase/concept-a/animation/.
"""
import bisect
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

FPS = 24                             # T-027: defaults of the build film; --fps / --width / --height override them (apply_res), all workers and the encode get the same values
W, H = 1280, 720
BASE_W = 1280.0                      # the overlay is laid out for a 1280-px-wide frame; k = picture width / BASE_W scales it to any resolution
FILM_DIR = os.path.join(HERE, 'film')
T_TITLE, T_CAM_STAGE = 6.5, 1.2      # s stage title card (camera moves during its first T_CAM_STAGE)
T_CAM = 0.7                          # s camera move before a step (fallback when cam_plan.json is missing; see cam_duration)
T_CAM_MIN, T_CAM_MAX = 0.6, 4.8      # s camera move limits; the move time grows with the zoom change, the swing and the shift (cam_duration)
GLIDE_END = 0.35                     # s the stage title card is still up after the camera has reached the first step's close view
CAM_PLAN = os.path.join(HERE, 'cam_plan.json')   # per-step camera (target, azimuth, elevation, distance): written by '--camplan' (Blender), read by timeline()
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
VIS_TRAVEL_MM = {'A3': 530.0, 'A4': 270.0, 'A5': 270.0}   # plugs go into the spar from the tip: they start a little outside the tip (not 450 mm out in the air), so the see-through spar stays in the picture
GHOST_STEPS_Y = 0.40                 # m, the x-ray close-up camera follows the plug but not beyond |y| 0.40 (stay over the wing)
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
VIEW = {'B1': (-40, -22), 'B2': (-40, -22), 'C2b': (35, -30), 'C8': (60, 8), 'C9': (60, 12), 'C7': (60, 12),
        'C6': (50, 14), 'E1': (85, 22), 'A2': (20, 30), 'A5': (-30, 30), 'A1': (38, 30),
        # servo stage: the pockets are aft of the hub (x +0.14 m), the cage arms and motors (x -0.07 m) sit between a camera on the nose side and the servo: look from the aft side
        'D1': (140, 40), 'D0': (140, 42), 'D2': (140, 38), 'D2a': (140, 44), 'D3': (140, 38), 'D4': (140, 36), 'D5': (140, 36), 'D5b': (200, 36),
        'B0a': (-40, 22), 'B0k': (-40, 22), 'B2c': (38, 30)}
DEFAULT_VIEW = (38, 30)

# D-198 marker steps (threading / laying wires place no part): the camera frames these parts instead
MARKER_FOCUS = {'B0a': [], 'B0k': ['CGE-001', 'CGE-002-A', 'CGE-002-B'], 'B2c': ['HRN-003-R', 'HRN-003-L', 'CGE-001', 'HRN-004-UR', 'HRN-004-UL', 'HRN-004-LR', 'HRN-004-LL'],
                'D0': ['MEC-001-R'], 'E3b': ['AVN-002', 'PRP-003', 'AVN-001'],
                'E4b': ['HRN-002', 'PWR-001', 'CGE-008'], 'E6': ['PRP-003', 'AVN-001', 'CGE-001']}
# B0 shows the cage unit (B1 parts minus the motors and props, which are screwed on in B1) hovering at its B1 start pose
# D-202: the parts of the bench steps B0b-B0j2 are shown by their own step (at the B1 start pose); PRESHOW only adds the cage parts no bench step places
PRESHOW = {'B0k': ('B1', ('PRP-', 'CGE-006', 'CGE-007'))}      # B0k shows the cage unit as built on the bench; the bridge saddle and strut clamps (no bench step) appear with B1
BENCH_VIEW = (-40, 22)                 # camera direction of the bench steps B0b-B0j2 (as B0a / B0k)
# wire reveal (threading): edge -> step id -> (fraction from, fraction to) along the route; fractions from out/wire_inventory.json
PHASE_EDGES = ('E-HRN-02', 'E-HRN-03', 'E-HRN-04', 'E-HRN-05')
SERVO_EDGES = ('E-HRN-07', 'E-HRN-08')
REVEAL_EDGES = PHASE_EDGES + SERVO_EDGES
SERVO_START = {'E-HRN-07': 'MEC-001-R', 'E-HRN-08': 'MEC-001-L'}      # the servo lead is threaded from the servo pocket to the slit
# camera framing: steps with a right and a left part frame the right one only (the left mirrors it); smaller context for small parts
ONE_SIDE = ('D1', 'D2', 'D2a', 'D3', 'D4', 'D5', 'C7', 'C8', 'C9', 'C1', 'C1a', 'C3', 'C5', 'C6', 'B4', 'C2a', 'C2b')
MIN_HALF_STEP = {'D1': 0.10, 'D2': 0.07, 'D2a': 0.05, 'D3': 0.07, 'D4': 0.06, 'D5': 0.05, 'D5b': 0.05, 'C7': 0.12, 'C8': 0.12, 'C9': 0.10, 'E1': 0.15, 'E2': 0.07, 'E3': 0.08,
                 'E3a': 0.06, 'E3d': 0.06, 'E3b': 0.08, 'E3c': 0.07, 'E4': 0.09, 'E4a': 0.08, 'E4b': 0.09, 'E5': 0.09, 'E6': 0.09, 'E7': 0.08, 'D0': 0.09, 'B2a': 0.10, 'B2b1': 0.10, 'B2b2': 0.10, 'B2b3': 0.10, 'B2b4': 0.10, 'B3': 0.10}
HEAD_R_MM = 4.5                      # bead at the head of a lead being threaded (the lead is 1.2 mm: the bead shows where the fish wire is)
EXTRA_PTS = {'D0': [(0.083, 0.024, 0.012), (0.14, 0.20, 0.0)]}      # marker steps: points the camera must also frame (servo pocket, slit)
GHOST_EXTRA = {'D1': ['WNG-001'], 'D0': ['WNG-001']}   # more x-ray steps (not part-inside-part steps with a follow camera): the core is see-through so the pocket, the servo and the lead in the groove are visible
GHOST_VIEW, GHOST_DIST = (50, 34), 0.24   # x-ray steps (step data 'ghost'): close-up camera that follows the plug along the spar (azimuth, elevation; distance m)
GHOST_B0 = ('CGE-001', 'CGE-002-', 'CGE-003-', 'CGE-009-', 'CGE-010-')
GHOST_B2C = GHOST_B0 + ('HRN-003-', 'HRN-004-', 'WNG-001', 'CGE-004', 'CGE-005-', 'CGE-006', 'CGE-007-')
FAB_ONLY = {'B1': ('PRP-',)}          # B1: during its make-it beat only the motors and props are teal (the cage parts are already shown)
NO_CONTEXT = ('B0a',)                  # the stage's first step frames only the cage unit on the bench (like the bench steps), not everything placed so far
T_CHK_CAM = 1.8                      # s camera pull-back to the whole assembly while a checkpoint card is up
MARKER_BEAT_KINDS = ('thread', 'solder')   # these fab kinds are shown during the marker step's motion, not as a separate beat


def apply_res(width=None, height=None, fps=None):
    """T-027: set the module-level frame size and rate (defaults 1280x720 @ 24 reproduce the build film)."""
    global W, H, FPS
    W, H, FPS = int(width or W), int(height or H), int(fps or FPS)


def add_res_args(ap):
    ap.add_argument('--width', type=int, default=W, help='frame width in px (default %d)' % W)
    ap.add_argument('--height', type=int, default=H, help='frame height in px (default %d)' % H)
    ap.add_argument('--fps', type=int, default=FPS, help='frames per second (default %d)' % FPS)


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


def load_cam_plan():
    """{step id: {'cam': [tx, ty, tz, az, el, dist], 'wide': [..] | None, 'chk': [..] | None}} written by `render_build_a.py --camplan`."""
    try:
        return json.load(open(CAM_PLAN))
    except (OSError, ValueError):
        return {}


def cam_duration(a, b):
    """Seconds a camera needs to go from view a to view b so that the move reads as one smooth shot: it grows with the zoom change (log2 of the
    distance ratio), the swing of azimuth / elevation and the shift of the target (in half view widths)."""
    if a is None or b is None:
        return T_CAM
    r = max(a[5] / b[5], b[5] / a[5])
    dang = max(abs(a[3] - b[3]), 1.5 * abs(a[4] - b[4]))
    dtg = math.dist(a[:3], b[:3]) / max(0.3, 0.5 * min(a[5], b[5]))
    return min(T_CAM_MAX, max(T_CAM_MIN, 0.5 + 1.5 * math.log2(r) + dang / 40.0 + 2.5 * dtg))


def timeline():
    """Pure schedule: list of step dicts with times, and the total length (s)."""
    plan = {s['id']: s for s in load_plan()}
    cplan = load_cam_plan()
    prev_end = None                      # the camera view the previous step left behind (its checkpoint pull-back if it has one)
    t, rows = 0.0, []
    for si, (title, ids) in enumerate(STAGES):
        for k, sid in enumerate(ids):
            s = dict(plan[sid])
            info = s['info']
            tr = VIS_TRAVEL_MM.get(sid) or (min(MAX_TRAVEL_MM, max(MIN_TRAVEL_MM, s['travel'])) if s['dir'] else 0.0)
            s['visual_mm'] = tr
            s['stage'] = si
            s['first_in_stage'] = (k == 0)
            fab = info.get('fab')
            s['fab'] = fab if (fab and fab['kind'] not in MARKER_BEAT_KINDS) else None
            s['marker_chip'] = info.get('chip') or (fab if (fab and fab['kind'] in MARKER_BEAT_KINDS) else None)
            s['t_cam0'] = t
            cp = cplan.get(sid) or {}
            close = cp.get('cam')
            wide = cp.get('wide') or close
            s['glide'] = 0.0
            if k == 0:
                # stage opening: the camera shows everything placed so far (wide) behind the title card, then glides to the step's close view
                s['cam_dur'] = cam_duration(prev_end, wide) if prev_end else 0.0
                if close and wide and wide != close:
                    s['glide'] = cam_duration(wide, close)
                s['t_title0'] = t
                s['t_title1'] = t + max(T_TITLE, s['cam_dur'] + 1.5 + s['glide'] + GLIDE_END)
                t = s['t_title1']
                s['t_card0'] = t
            else:
                s['cam_dur'] = cam_duration(prev_end, close) if close else T_CAM
                s['t_card0'] = t
                t += s['cam_dur']
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
            s['chk_dur'] = 0.0
            if info.get('hold') and info.get('cp'):
                c = sum(len(x) for x in info['cp']) + 40
                s['t_chk0'] = t
                s['chk_dur'] = cam_duration(cp.get('end') or close, cp.get('chk')) if cp.get('chk') else T_CHK_CAM
                t += max(CHECK_MIN, c / CHECK_CPS, s['chk_dur'] + 2.5)
                s['t_chk1'] = t
            else:
                s['t_chk0'] = s['t_chk1'] = t
            prev_end = cp.get('chk') if (s['t_chk1'] > s['t_chk0'] and cp.get('chk')) else (cp.get('end') or close)
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
        if r['glide']:
            spans.append((r['t_title1'] - GLIDE_END - r['glide'] - 0.1, r['t_title1']))
        if r['t_chk1'] > r['t_chk0']:
            spans.append((r['t_chk0'], r['t_chk0'] + r['chk_dur'] + 0.1))
        for a, b in spans:
            for f in range(max(0, int(a * FPS)), min(n, int(b * FPS) + 1)):
                cost[f] = 1
    return cost


# =====================================================================================================================
# short film (T-027): shot list -> scenes of shots; pure functions shared by the Blender worker and the driver
# =====================================================================================================================
PARAMS_A = os.path.join(REDESIGN, 'qp', 'A', 'params-A.json')
FILM_MODES = ('normal', 'ghost', 'fab', 'fab50', 'move', 'hidden')      # fab50 (T-030 M-8): fabricated-part teal at 50 % opacity, for a part whose inside must stay visible


def param_value(path):
    """params-A.json value by key path, e.g. 'box/packed_m/0' (a dict node with a 'value' is unwrapped; digits index lists)."""
    o = json.load(open(PARAMS_A))
    for k in path.split('/'):
        if isinstance(o, dict) and k not in o and 'value' in o:
            o = o['value']
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o['value'] if isinstance(o, dict) and 'value' in o else o


def _cam_vec(c):
    return (float(c['target'][0]), float(c['target'][1]), float(c['target'][2]), float(c['az']), float(c['el']), float(c['dist']))


def load_film(path, scene_ids=None):
    """Shot-list JSON -> {'scenes': [...], 'total': s}. Camera keys are given per shot as {t (s from shot start), target, az, el, dist}; the
    keys of all shots of a scene form ONE path (hermite_cam, C1: no velocity jump at a shot join). A shot's start camera is the previous shot's
    last key, so only the first shot of a scene needs a key at t = 0; cuts are allowed only between scenes."""
    d = json.load(open(path, encoding='utf-8'))
    scenes, t = [], 0.0
    for sc in d['scenes']:
        if scene_ids and sc['id'] not in scene_ids:
            continue
        S = dict(id=sc['id'], title=sc.get('title', ''), t0=t, shots=[], keys=[])
        st = 0.0
        for n, sh in enumerate(sc['shots']):
            sh = dict(sh)
            sh['scene'] = sc['id']
            sh['t0'], sh['t1'] = st, st + float(sh['dur'])
            last = S['keys'][-1][1] if S['keys'] else None
            for kf in sh.get('cam', []):
                tk, c = st + float(kf['t']), _cam_vec(kf)
                if S['keys'] and tk <= S['keys'][-1][0] + 1e-9:
                    if tk == st and last is not None and max(abs(a - b) for a, b in zip(c, last)) < 1e-9:
                        continue              # the shot restates the camera it starts from: same key
                    raise ValueError('%s shot %s: camera key at %.2f s is not after the previous key (%s) - a cut inside a scene is not allowed' % (sc['id'], sh['id'], tk, last))
                S['keys'].append((tk, c, True) if kf.get('hold') else (tk, c))      # hold: zero camera velocity at this key (T-030: the camera stops at the end view of 3.2 instead of overshooting it)
            if n == 0 and (not S['keys'] or S['keys'][0][0] != 0.0):
                raise ValueError('%s: the first shot needs a camera key at t = 0' % sc['id'])
            st = sh['t1']
            S['shots'].append(sh)
        S['dur'] = st
        t += st
        scenes.append(S)
    return dict(scenes=scenes, total=t, raw=d)


def hermite_cam(keys, tl):
    """Camera (tx, ty, tz, az, el, dist) at scene time tl: cubic Hermite through the keys with Catmull-Rom tangents (distance interpolated
    geometrically, as lerp_cam does), zero velocity only at the first and last key, so shot joins inside a scene have no velocity jump."""
    ts = [k[0] for k in keys]
    hold = [len(k) > 2 and bool(k[2]) for k in keys]
    ps = [list(k[1][:5]) + [math.log(k[1][5])] for k in keys]
    n = len(ts)
    if n == 1:
        q = ps[0]
    else:
        if tl <= ts[0]:
            i, u = 0, 0.0
        elif tl >= ts[-1]:
            i, u = n - 2, 1.0
        else:
            i = bisect.bisect_right(ts, tl) - 1
            u = (tl - ts[i]) / (ts[i + 1] - ts[i])
        h = ts[i + 1] - ts[i]

        def tan(j):
            if j <= 0 or j >= n - 1 or hold[j]:
                return [0.0] * 6
            return [(ps[j + 1][m] - ps[j - 1][m]) / (ts[j + 1] - ts[j - 1]) for m in range(6)]
        m0, m1 = tan(i), tan(i + 1)
        h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        q = [h00 * ps[i][m] + h10 * h * m0[m] + h01 * ps[i + 1][m] + h11 * h * m1[m] for m in range(6)]
    return (q[0], q[1], q[2], q[3], q[4], math.exp(q[5]))


def film_at(film, t):
    """(scene, shot, scene-local time) for film time t (clamped to the last frame)."""
    sc = film['scenes'][-1]
    for S in film['scenes']:
        if t >= S['t0']:
            sc = S
    tl = min(max(0.0, t - sc['t0']), sc['dur'] - 1e-6)
    sh = sc['shots'][-1]
    for x in sc['shots']:
        if tl >= x['t0']:
            sh = x
    return sc, sh, tl


# ---- scene 3 (T-028): servo arm / pushrod / horn / elevon posed from the SOLVED kinematics (AR-001), not hand keyframes
KIN_CSV = os.path.join(REDESIGN, 'qp', 'A', 'mechanism', 'out', 'linkage_kinematics.csv')
KIN_JSON = os.path.join(REDESIGN, 'qp', 'A', 'mechanism', 'out', 'linkage_kinematics.json')
_KIN = {}


def load_kin():
    """AR-001 output: the elevon angle -> servo angle table (linkage_kinematics.csv, 0.05 deg steps, +-21 deg) and the CAD geometry constants it was solved with."""
    if not _KIN:
        import csv
        rows = list(csv.DictReader(open(KIN_CSV, encoding='utf-8')))
        d = [float(r['delta_deg']) for r in rows]
        th = [float(r['theta_R_deg']) for r in rows]
        if any(b <= a for a, b in zip(th, th[1:])) or any(b <= a for a, b in zip(d, d[1:])):
            raise ValueError('linkage_kinematics.csv: delta and theta_R must both increase (the servo angle is inverted by interpolation)')
        _KIN.update(delta=d, theta=th, geom=json.load(open(KIN_JSON, encoding='utf-8'))['geometry'])
    return _KIN


def _interp(xs, ys, x):
    if x < xs[0] - 1e-9 or x > xs[-1] + 1e-9:
        raise ValueError('kinematics table covers %.2f..%.2f, asked %.4f' % (xs[0], xs[-1], x))
    i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
    u = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] * (1 - u) + ys[i + 1] * u


def mech_state(shot, tl):
    """Servo-arm angle (right side, deg) and elevon angle (deg) at scene time tl. The shot's 'mech' = {'sweep': [[t, elevon_deg], ...]} (t in s from
    the shot start) names the commanded elevon end points; each is converted to a servo angle through the AR-001 table, the SERVO angle is eased
    (smoothstep) between them, and the elevon angle is read back from the table at that servo angle (linear interpolation)."""
    K = load_kin()
    wp = shot['mech']['sweep']
    t = tl - shot['t0']
    th = [_interp(K['delta'], K['theta'], w[1]) for w in wp]
    if t <= wp[0][0]:
        q = th[0]
    elif t >= wp[-1][0]:
        q = th[-1]
    else:
        i = bisect.bisect_right([w[0] for w in wp], t) - 1
        q = th[i] + (th[i + 1] - th[i]) * smooth((t - wp[i][0]) / (wp[i + 1][0] - wp[i][0]))
    return dict(theta_R=q, theta_L=-q, delta=_interp(K['theta'], K['delta'], q))


def mech_geom(sy, theta_deg, delta_deg):
    """Arm-tip (Z-bend) point A and horn-hole point H in the CAD frame, m: the formulas of linkage_core.arm_pt / horn_pt on the AR-001 constants."""
    G = load_kin()['geom']
    th, d = math.radians(theta_deg), math.radians(delta_deg)
    xh, hz, sv, sx, ar, zj = G['XH'], G['HINGE_Z'], G['SERVO_Y'], G['SV_XS'], G['ARM_R'], G['ROD_Z']
    vx0, vz0 = G['HORN_XH'] - xh, zj - hz
    A = (sx + ar * sy * math.sin(th), sy * sv - sy * ar * math.cos(th), zj)
    H = (xh + vx0 * math.cos(d) + vz0 * math.sin(d), sy * (sv - ar), hz - vx0 * math.sin(d) + vz0 * math.cos(d))
    return A, H


def mech_state_log(sh, tl):
    """Servo-arm and elevon angles of both sides from the logged elevon angles of a SITL run (dr right, dl left, trailing edge down +), through the AR-001 table (T-029)."""
    K = load_kin()
    a = sitl_at(sh['sitl']['run'], sitl_clock(sh, tl))
    lo, hi = K['delta'][0], K['delta'][-1]
    dR, dL = min(max(a['dr'], lo), hi), min(max(a['dl'], lo), hi)
    return dict(theta_R=_interp(K['delta'], K['theta'], dR), theta_L=-_interp(K['delta'], K['theta'], dL), delta=dR, delta_L=dL)


# ---- scene 4 (T-029): playback of an ALREADY EXECUTED ArduPilot SITL run (PD-007): the aircraft pose is read from the run's case.fwd.csv, no new simulation
SITL_DIR = os.path.join(REDESIGN, 'qp', 'A', 'sitl')
CAD_MASS_JSON = os.path.join(SITL_DIR, 'cad_mass.json')
# Column meanings (a_plant.py line 304 header, euler_rpy line 234): t s; pn, pe m north / east of the take-off point; alt m of the CG above ground (up); pitch deg (+90 = nose up,
# 0 = level cruise); roll, hdg_nose deg (ZYX Euler of the body FRD frame: x nose, y right wing, z belly); V m/s airspeed; dl, dr deg left / right elevon (trailing edge down +).
_SITL = {}


def load_sitl(run):
    if run not in _SITL:
        import csv
        rows = list(csv.DictReader(open(os.path.join(SITL_DIR, 'runs', run, 'case.fwd.csv'), encoding='utf-8')))
        cols = {k: [float(r[k]) for r in rows] for k in rows[0]}
        n = len(rows)
        pre = {}
        for k in ('pn', 'pe', 'alt'):                                   # prefix sums for the box-filtered camera target
            acc = [0.0]
            for v in cols[k]:
                acc.append(acc[-1] + v)
            pre[k] = acc
        _SITL[run] = dict(cols=cols, n=n, t=cols['t'], pre=pre, cg=json.load(open(CAD_MASS_JSON, encoding='utf-8')))
    return _SITL[run]


def sitl_index(L, tlog):
    """(i, u): row index and fraction for log time tlog (clamped to the log)."""
    T = L['t']
    if tlog <= T[0]:
        return 0, 0.0
    if tlog >= T[-1]:
        return L['n'] - 2, 1.0
    i = bisect.bisect_right(T, tlog) - 1
    return i, (tlog - T[i]) / (T[i + 1] - T[i])


def sitl_at(run, tlog):
    """Scalar columns linearly interpolated at log time tlog (angles are not wrapped here: only pitch, alt, V, dl, dr, pn, pe are read through this)."""
    L = load_sitl(run)
    i, u = sitl_index(L, tlog)
    return {k: v[i] * (1 - u) + v[i + 1] * u for k, v in L['cols'].items()}


def sitl_clock(sh, tl):
    """Log time at scene time tl for a shot with sitl = {run, t0, t1}: the log window t0..t1 plays over the shot's duration (time scale = (t1 - t0) / duration, shown on screen)."""
    q = sh['sitl']
    k = min(max((tl - sh['t0']) / (sh['t1'] - sh['t0']), 0.0), 1.0)
    return q['t0'] + (q['t1'] - q['t0']) * k


def sitl_scale(sh):
    q = sh['sitl']
    return (q['t1'] - q['t0']) / (sh['t1'] - sh['t0'])


def sitl_smooth_pos(run, tlog, half=0.4, max_off=0.5):
    """Camera target: position (north, east, up) averaged over +-half s of log time (the camera does not copy the hover wobble), kept within max_off m of the true position
    (a wider average lags behind the aircraft while it accelerates: 1.5 s put it up to 2 m off-centre in the transition)."""
    L = load_sitl(run)
    T = L['t']
    a = bisect.bisect_left(T, tlog - half)
    b = bisect.bisect_right(T, tlog + half)
    b = max(b, a + 1)
    sm = [(L['pre'][k][b] - L['pre'][k][a]) / (b - a) for k in ('pn', 'pe', 'alt')]
    raw = sitl_at(run, tlog)
    d = [sm[0] - raw['pn'], sm[1] - raw['pe'], sm[2] - raw['alt']]
    n = math.sqrt(sum(x * x for x in d))
    if n > max_off:
        d = [x * max_off / n for x in d]
    return (raw['pn'] + d[0], raw['pe'] + d[1], raw['alt'] + d[2])


# ---- scene 5 (T-029): FEA numbers read from the result files at draw time
STRUCT_DIR = os.path.join(REDESIGN, 'qp', 'A', 'structures')
FEA_OUT = os.path.join(STRUCT_DIR, 'out_fea')


def fea_const(name):
    """Allowables and required factors parsed from fea_arm.py (ALLOW = dict(...), KF, KP = ...): ALLOW.petg, ALLOW.cf_axial, KF, KP."""
    src = open(os.path.join(STRUCT_DIR, 'fea_arm.py'), encoding='utf-8').read()
    if name.startswith('ALLOW.'):
        m = re.search(r'^ALLOW\s*=\s*dict\((.*?)\)', src, re.M)
        return float(re.search(name[6:] + r'\s*=\s*([0-9.]+)', m.group(1)).group(1))
    m = re.search(r'^KF, KP\s*=\s*([0-9.* ]+),\s*([0-9.* ]+)', src, re.M)
    expr = m.group(1 if name == 'KF' else 2)
    return float(np_prod(expr))


def np_prod(expr):
    r = 1.0
    for f in expr.split('*'):
        r *= float(f.strip())
    return r


def sitl_sum(run):
    """sum.json of an executed SITL run (read at draw time)."""
    return json.load(open(os.path.join(SITL_DIR, 'runs', run, 'sum.json'), encoding='utf-8'))


_GIT = {}


def git_rev():
    """Short hash of HEAD, '-dirty' if the working tree has uncommitted changes ('—' if git is not available): printed on the closing card (R-VID-08 revision tag)."""
    if 'rev' not in _GIT:
        try:
            rev = subprocess.run(['git', '-C', REDESIGN, 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True).stdout.strip()
            dirty = subprocess.run(['git', '-C', REDESIGN, 'status', '--porcelain', '--untracked-files=no'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True).stdout.strip()
            _GIT['rev'] = rev + ('-dirty' if dirty else '')
        except Exception:
            _GIT['rev'] = '—'
    return _GIT['rev']


def src_val(spec):
    """Number (or text) from a record, read at draw time. Kinds: {file (relative to out_fea), path [keys; '@X' picks the list item whose 'case' starts with X], maxkey (max over the
    children of a dict of that key)}; {const: name} (fea_arm.py); {param: 'a/b'} (params-A.json); {npz: file, key, reduce: nanmax | pct_over1} (arrays of out_fea; pct_over1 = % of the finite
    entries above 1); {sum: run, path} (sitl/runs/<run>/sum.json); {calc: 'a*b+c', of: {a: spec, ...}}; {git: 'rev'}. Optional: times / div (const names, fea_arm.py)."""
    if 'git' in spec:
        return git_rev()
    if 'calc' in spec:
        v = eval(spec['calc'], {'__builtins__': {}}, {k_: src_val(q_) for k_, q_ in spec['of'].items()})
    elif 'const' in spec:
        v = fea_const(spec['const'])
    elif 'param' in spec:
        v = param_value(spec['param'])
    elif 'npz' in spec:
        import numpy as np
        z = np.load(os.path.join(FEA_OUT, spec['npz']), allow_pickle=False)
        arr = z[spec['key']]
        fin = arr[np.isfinite(arr)]
        v = float(fin.max()) if spec.get('reduce', 'nanmax') == 'nanmax' else 100.0 * float((fin > 1.0).sum()) / float(fin.size)
    elif 'sum' in spec:
        v = sitl_sum(spec['sum'])
        for k in spec['path']:
            v = v[k]
    else:
        o = json.load(open(os.path.join(FEA_OUT, spec['file']), encoding='utf-8'))
        for k in spec['path']:
            if k.startswith('@'):
                o = next(c for c in o if c['case'].startswith(k[1:]))
            else:
                o = o[k]
        v = max(c[spec['maxkey']] for c in o.values()) if 'maxkey' in spec else o
    if spec.get('times'):
        v *= fea_const(spec['times'])
    if spec.get('div'):
        v /= fea_const(spec['div'])
    return v


def source_hashes(film):
    """SHA-256 (and size) of every record file the film reads from the git-ignored folders (sitl/runs, out_fea): printed into timing.json so a render can be traced to its sources (T-030 M-5)."""
    import hashlib
    paths = set()
    for S in film['scenes']:
        for sh in S['shots']:
            if sh.get('sitl'):
                for fn in ('case.fwd.csv', 'sum.json', 'result.json'):
                    paths.add(os.path.join(SITL_DIR, 'runs', sh['sitl']['run'], fn))
            if sh.get('fea'):
                paths.add(os.path.join(FEA_OUT, sh['fea']['glb']))
            for v in list(sh.get('vals', {}).values()) + list(sh.get('card', {}).get('vals', {}).values()):
                for q in ([v] + list(v.get('of', {}).values())):
                    if 'file' in q:
                        paths.add(os.path.join(FEA_OUT, q['file']))
                    if 'npz' in q:
                        paths.add(os.path.join(FEA_OUT, q['npz']))
    out = {}
    for pth in sorted(paths):
        if os.path.exists(pth):
            h = hashlib.sha256()
            with open(pth, 'rb') as f_:
                for chunk in iter(lambda: f_.read(1 << 20), b''):
                    h.update(chunk)
            out[os.path.relpath(pth, REDESIGN).replace(os.sep, '/')] = dict(sha256=h.hexdigest(), bytes=os.path.getsize(pth))
    return out


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
    ap.add_argument('--camplan', action='store_true', help='no rendering: compute the per-step cameras and write cam_plan.json (timeline() needs it for the camera move times)')
    ap.add_argument('--audit', action='store_true', help='no rendering: dump what is visible and where the camera is, every --every frames')
    ap.add_argument('--shot-list', default='', help='short-film mode: render the scenes of this shot-list JSON instead of the build film')
    ap.add_argument('--scenes', default='', help='short-film mode: comma list of scene ids to render (default all)')
    ap.add_argument('--dof', action='store_true', help='depth of field focused on the camera target (off by default)')
    ap.add_argument('--motion-blur', action='store_true', help='EEVEE motion blur on (off by default)')
    ap.add_argument('--cam-check', action='store_true', help='short-film mode, no rendering: camera-vs-mesh clearance and line of sight for EVERY frame (writes cam_clearance.json)')
    add_res_args(ap)
    a = ap.parse_args(argv)
    apply_res(a.width, a.height, a.fps)
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
    cams_wide = {}
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
        az, el = VIEW.get(r['id'], BENCH_VIEW if r['bench'] else DEFAULT_VIEW)

        def framed(P_, rid=r['id'], az=az, el=el):
            lo, hi = aabb(P_)
            c0 = (lo + hi) / 2
            mh = MIN_HALF_STEP.get(rid, MIN_HALF)
            P_ = P_ + [c0 + Vector((sx * mh, sy * mh, sz * mh)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
            tgt_, dist_ = fit(P_, az, el)
            return (tgt_, az, el, dist_)
        cams[r['id']] = framed(P)                                # the step's own (close) view
        if r['first_in_stage'] and r['id'] not in NO_CONTEXT:    # stage opening: first a wide shot of everything placed so far (behind the title card), then the close view
            cams_wide[r['id']] = framed(P + pts_of(placed_so_far))
        if r['t_chk1'] > r['t_chk0']:                       # checkpoint card: pull back to everything placed so far
            t2, d2 = fit(bench_P if bframe else pts_of(placed_so_far), az, el)
            cams_chk[r['id']] = (t2, az, el, d2)
    allp = pts_of(sorted(placed_ids))
    full_lo, full_hi = aabb(allp)
    full_c = (full_lo + full_hi) / 2
    tgt, dist = fit(allp, 38, 26)
    cams['END'] = (tgt, 38, 26, dist * 1.05)
    zmin_all = full_lo.z

    # x-ray close-up steps (step data 'ghost'): the camera follows the plug(s) over the spar; before the move it waits at the start pose, after it at the seat
    def cam_view(c):
        ctr, az, el, dist = c
        ar, er = math.radians(az), math.radians(el)
        view = Vector((-math.cos(er) * math.cos(ar), -math.cos(er) * math.sin(ar), math.sin(er)))
        return ctr, view, dist

    def rest_center(p):
        ob = items[p]
        return sum((rest[p] @ Vector(c) for c in ob.bound_box), Vector()) / 8

    def ghost_cam(r_, pc):
        pl_ = [rest_center(p) for p in r_['parts'] if p in items]
        c_ = sum(pl_, Vector()) / len(pl_)
        spread = max([(q - c_).length for q in pl_] + [0.0])
        az_f, el_f = GHOST_VIEW
        pc = Vector(pc)
        pc.y = min(GHOST_STEPS_Y, max(-GHOST_STEPS_Y, pc.y))
        _, v_f, _ = cam_view((pc, az_f, el_f, 1.0))
        up_f = v_f.cross(Vector((0, 0, 1))).cross(v_f).normalized()
        d_f = GHOST_DIST + 2.0 * spread
        return (pc - up_f * (0.045 * 2 * d_f * TAN_V), az_f, el_f, d_f)           # subject in the free band between header and card

    def ghost_centroid(r_, t):
        d_ = Vector(r_['dir']) if r_['dir'] else Vector()
        k_ = 1.0 - smooth((t - r_['t_mv0']) / max(1e-6, r_['t_mv1'] - r_['t_mv0']))
        pl_ = [rest_center(p) for p in r_['parts'] if p in items]
        return sum(pl_, Vector()) / len(pl_) - d_ * (r_['visual_mm'] / 1000.0) * k_

    ghost_rows = [r for r in rows if r['info'].get('ghost') and r['parts']]
    for r in ghost_rows:
        cams[r['id']] = ghost_cam(r, ghost_centroid(r, r['t_mv0'] - 1.0))
    cam_end = {r['id']: ghost_cam(r, ghost_centroid(r, r['t_mv1'] + 1.0)) for r in ghost_rows}
    ghost_by_id = {r['id']: r for r in ghost_rows}

    def plan_of(c):
        return [round(float(c[0].x), 4), round(float(c[0].y), 4), round(float(c[0].z), 4), round(float(c[1]), 2), round(float(c[2]), 2), round(float(c[3]), 4)]
    plan_json = {r['id']: dict(cam=plan_of(cams[r['id']]), wide=plan_of(cams_wide[r['id']]) if r['id'] in cams_wide else None,
                               chk=plan_of(cams_chk[r['id']]) if r['id'] in cams_chk else None, end=plan_of(cam_end[r['id']]) if r['id'] in cam_end else None) for r in rows}
    if a.camplan:
        json.dump(plan_json, open(CAM_PLAN, 'w'), indent=0)
        print('CAMPLAN written', CAM_PLAN, len(plan_json))
        return
    old_plan = load_cam_plan()
    stale = [r['id'] for r in rows if old_plan.get(r['id'], {}).get('cam') != plan_json[r['id']]['cam'] or old_plan.get(r['id'], {}).get('wide') != plan_json[r['id']]['wide']]
    if stale and not a.shot_list:
        raise SystemExit('cam_plan.json is stale for %s: run with --camplan first (the driver does it)' % stale)

    # camera keyframes: one smooth move (smoothstep, distance geometric) between the views of consecutive steps, holds in between
    kf = []
    prev_end = None
    for r in rows:
        close = cams[r['id']]
        wide = cams_wide.get(r['id'], close)
        if r['first_in_stage']:
            kf.append((r['t_cam0'], prev_end or wide))
            kf.append((r['t_cam0'] + r['cam_dur'], wide))
            if r['glide'] > 0:
                kf.append((r['t_title1'] - GLIDE_END - r['glide'], wide))
                kf.append((r['t_title1'] - GLIDE_END, close))
        else:
            kf.append((r['t_cam0'], prev_end or close))
            kf.append((r['t_cam0'] + r['cam_dur'], close))
        end_close = cam_end.get(r['id'], close)
        if r['id'] in cam_end:
            kf.append((r['t_mv0'], close))
            kf.append((r['t_mv0'], end_close))
        if r['t_chk1'] > r['t_chk0']:
            kf.append((r['t_chk0'], end_close))
            kf.append((r['t_chk0'] + r['chk_dur'], cams_chk[r['id']]))
            prev_end = cams_chk[r['id']]
        else:
            prev_end = end_close
    kf_t = [k_[0] for k_ in kf]

    def lerp_cam(c0, c1, k_):
        return (c0[0] * (1 - k_) + c1[0] * k_, c0[1] * (1 - k_) + c1[1] * k_, c0[2] * (1 - k_) + c1[2] * k_, c0[3] ** (1 - k_) * c1[3] ** k_)

    def cam_at(t):
        i = bisect.bisect_right(kf_t, t) - 1
        if i < 0:
            return kf[0][1]
        if i >= len(kf) - 1:
            return kf[-1][1]
        (t0_, c0), (t1_, c1) = kf[i], kf[i + 1]
        return lerp_cam(c0, c1, smooth((t - t0_) / (t1_ - t0_)) if t1_ > t0_ else 1.0)

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
    if a.dof:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = 5.6
    if a.motion_blur:
        sc.render.use_motion_blur = True
        sc.render.motion_blur_shutter = 0.5

    def set_focus(dist_):
        if a.dof:
            cd.dof.focus_distance = float(dist_)

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
            'ghost_spar': bb._principled('ghost spar', bb.srgb('#2E4A6B'), 0.3, metal=0.2, alpha=0.38),
            'fab50': bb._principled('fabricated part, half see-through', bb.srgb('#13897F'), 0.45, alpha=0.5)}
    for m_ in (MATS['ghost'], MATS['ghost_spar'], MATS['fab50']):          # see-through parts must not shadow what they hide
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

    if a.shot_list:
        # ---- short-film mode (T-027): the concept A CAD at rest, parts shown / x-rayed per shot, one camera path per scene (hermite_cam)
        film = load_film(a.shot_list, a.scenes.split(',') if a.scenes else None)
        nfr = int(round(film['total'] * FPS))
        sc.render.resolution_percentage = 100

        def shot_modes(sh):
            parts, modes, out = sh.get('parts', 'all'), sh.get('modes', {}), {}
            if sh.get('fea') or sh.get('plate'):          # T-029: stress mesh / image plate shots show no CAD part
                return out
            for pid in be.objects:
                if pid not in placed_ids or (parts != 'all' and not any(pid.startswith(x) for x in parts)):
                    continue
                m = 'normal'
                for pref, mm in modes.items():
                    if pid.startswith(pref):
                        m = mm
                if m != 'hidden':
                    out[pid] = m
            return out

        def rax(axis, pt, ang):
            return Matrix.Translation(Vector(pt)) @ Matrix.Rotation(ang, 4, axis) @ Matrix.Translation(-Vector(pt))

        MECH_LOG = dict(gap_max=0.0, len_err_max=0.0, n=0)

        def mech_mats(sh, tl):
            """{part: world motion matrix} for the elevon group, servo arm group and pushrod of both sides, from the AR-001 solution at scene time tl."""
            if not sh.get('mech'):
                return {}, None
            st = mech_state(sh, tl) if 'sweep' in sh['mech'] else mech_state_log(sh, tl)
            G = load_kin()['geom']
            mats = {}
            for sy, s_ in ((1, 'R'), (-1, 'L')):
                th = st['theta_R'] if sy == 1 else st['theta_L']
                dl = st['delta'] if sy == 1 else st.get('delta_L', st['delta'])
                M_el = rax('Y', (G['XH'], 0.0, G['HINGE_Z']), math.radians(dl))                 # elevon group: right-handed about +y through the hinge (CAD sense, linkage_core)
                M_arm = rax('Z', (G['SV_XS'], sy * G['SERVO_Y'], 0.0), math.radians(th))        # servo arm group: counter-clockwise about +z through the spline axis
                A0, H0 = (Vector(v) for v in mech_geom(sy, 0.0, 0.0))
                A, H = (Vector(v) for v in mech_geom(sy, th, dl))
                u = (H - A).normalized()
                ex = Vector((1.0, 0.0, 0.0))                                                  # rod is parallel to x at neutral (L_ROD = HORN_XH - SV_XS)
                ax_ = ex.cross(u)
                R_ = Matrix.Rotation(math.acos(max(-1.0, min(1.0, ex.dot(u)))), 4, ax_) if ax_.length > 1e-12 else Matrix.Identity(4)
                M_rod = Matrix.Translation(A) @ R_ @ Matrix.Translation(-A0)
                for pid in ('WNG-006-', 'WNG-007-', 'WNG-010-', 'MEC-004-', 'MEC-005-'):
                    mats[pid + s_] = M_el
                for pid in ('MEC-002-', 'MEC-008-', 'HWC-002-'):
                    mats[pid + s_] = M_arm
                mats['MEC-003-' + s_] = M_rod
                # connection check: arm-tip end of the rod on the arm tip (arm group), horn end of the rod on the horn hole (elevon group), rod length
                g1 = (M_arm @ A0 - M_rod @ A0).length
                g2 = (M_el @ H0 - M_rod @ H0).length
                MECH_LOG['gap_max'] = max(MECH_LOG['gap_max'], g1, g2)
                MECH_LOG['len_err_max'] = max(MECH_LOG['len_err_max'], abs((H - A).length - (H0 - A0).length))
            MECH_LOG['n'] += 1
            return mats, st

        # ---- T-029: SITL playback pose (body -> CAD -> world) and FEA stress meshes
        TW4 = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1))).to_4x4()          # NED -> world (x north, y west, z up)
        D4 = Matrix(((-1, 0, 0), (0, 1, 0), (0, 0, -1))).to_4x4()           # body FRD (x nose, y right, z belly) -> CAD (x aft, y right, z up), CG at the origin
        floor_default = (floor.location.copy(), floor.scale.copy())

        def row_quats(L):
            if 'quats' not in L:
                c = L['cols']
                qs = []
                for i in range(L['n']):
                    ps, th, ph = (math.radians(c[k][i]) for k in ('hdg_nose', 'pitch', 'roll'))
                    R = Matrix.Rotation(ps, 3, 'Z') @ Matrix.Rotation(th, 3, 'Y') @ Matrix.Rotation(ph, 3, 'X')      # body -> NED, ZYX Euler as a_plant.euler_rpy
                    qs.append(R.to_quaternion())
                L['quats'] = qs
            return L['quats']

        def sitl_pose(sh, tl):
            q = sh['sitl']
            L = load_sitl(q['run'])
            tlog = sitl_clock(sh, tl)
            i, u = sitl_index(L, tlog)
            qs = row_quats(L)
            qq = qs[i].slerp(qs[i + 1], u)
            c = L['cols']
            P = Vector((c['pn'][i] * (1 - u) + c['pn'][i + 1] * u, -(c['pe'][i] * (1 - u) + c['pe'][i + 1] * u), c['alt'][i] * (1 - u) + c['alt'][i + 1] * u))
            cg = L['cg']
            M = Matrix.Translation(P) @ TW4 @ qq.to_matrix().to_4x4() @ D4 @ Matrix.Translation(-Vector((cg['cg_x_m'], cg['cg_y_m'], cg['cg_z_m'])))
            sp = sitl_smooth_pos(q['run'], tlog)
            return dict(M=M, P=P, Psm=Vector((sp[0], -sp[1], sp[2])), tlog=tlog)

        FEA_OBJS = {}

        def fea_objs(name):
            if name not in FEA_OBJS:
                before = set(bpy.data.objects)
                bpy.ops.import_scene.gltf(filepath=os.path.join(FEA_OUT, name))
                new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
                pts = [o.matrix_world @ Vector(c_) for o in new for c_ in o.bound_box]
                ctr_ = Vector([(min(p_[k_] for p_ in pts) + max(p_[k_] for p_ in pts)) / 2 for k_ in range(3)])
                for o in new:
                    for pl in o.data.polygons:
                        pl.use_smooth = False
                    mt = bpy.data.materials.new('fea utilisation')
                    mt.use_nodes = True
                    nt = mt.node_tree
                    nt.nodes.clear()
                    vc = nt.nodes.new('ShaderNodeVertexColor')
                    vc.layer_name = o.data.color_attributes[0].name
                    lw = nt.nodes.new('ShaderNodeLayerWeight')              # unlit: the data colour is shown as is, only darkened a little towards the silhouette so the form reads
                    lw.inputs['Blend'].default_value = 0.5
                    sh_ = nt.nodes.new('ShaderNodeMath')
                    sh_.operation = 'MULTIPLY_ADD'
                    sh_.inputs[1].default_value = -0.4
                    sh_.inputs[2].default_value = 1.0
                    nt.links.new(lw.outputs['Facing'], sh_.inputs[0])
                    mx = nt.nodes.new('ShaderNodeMix')
                    mx.data_type = 'RGBA'
                    mx.blend_type = 'MULTIPLY'
                    mx.inputs['Factor'].default_value = 1.0
                    nt.links.new(vc.outputs['Color'], mx.inputs['A'])
                    nt.links.new(sh_.outputs['Value'], mx.inputs['B'])
                    em = nt.nodes.new('ShaderNodeEmission')
                    nt.links.new(mx.outputs['Result'], em.inputs['Color'])
                    ot = nt.nodes.new('ShaderNodeOutputMaterial')
                    nt.links.new(em.outputs['Emission'], ot.inputs['Surface'])
                    o.data.materials.clear()
                    o.data.materials.append(mt)
                    o.location = -ctr_
                    o.hide_render = o.hide_viewport = True
                FEA_OBJS[name] = new
                print('FEAMESH', name, len(new), 'objects, centre (m)', tuple(round(x, 4) for x in ctr_), flush=True)
            return FEA_OBJS[name]

        trail = {}

        def trail_obj(run, t_from):
            """Flown path (CG) from log time t_from, drawn as a poly curve; bevel_factor_end reveals it up to the current log time (by arc length)."""
            if 'ob' not in trail:
                L = load_sitl(run)
                c = L['cols']
                idx_ = [i for i in range(0, L['n'], 5) if c['t'][i] >= t_from]
                pts = [Vector((c['pn'][i], -c['pe'][i], c['alt'][i])) for i in idx_]
                cum = [0.0]
                for a_, b_ in zip(pts, pts[1:]):
                    cum.append(cum[-1] + (b_ - a_).length)
                cu = bpy.data.curves.new('sitl trail', 'CURVE')
                cu.dimensions = '3D'
                cu.bevel_depth = 0.006
                cu.bevel_resolution = 2
                cu.use_fill_caps = True
                cu.bevel_factor_mapping_end = 'SPLINE'
                cu.bevel_factor_mapping_start = 'SPLINE'
                spl = cu.splines.new('POLY')
                spl.points.add(len(pts) - 1)
                for q_, p_ in zip(spl.points, pts):
                    q_.co = (p_.x, p_.y, p_.z, 1.0)
                ob = bpy.data.objects.new('sitl trail', cu)
                sc.collection.objects.link(ob)
                cu.materials.append(MATS['move'])
                ob.hide_render = True
                trail.update(ob=ob, cu=cu, ts=[c['t'][i] for i in idx_], cum=cum)
            return trail

        def trail_set(tlog, show):
            tr = trail
            tr['ob'].hide_render = not show
            if show:
                ts, cum = tr['ts'], tr['cum']

                def arc(tt):
                    j = min(max(bisect.bisect_right(ts, tt) - 1, 0), len(ts) - 2)
                    u = min(max((tt - ts[j]) / (ts[j + 1] - ts[j]), 0.0), 1.0)
                    return min(1.0, max(0.0, (cum[j] + (cum[j + 1] - cum[j]) * u) / cum[-1]))
                tr['cu'].bevel_factor_start = arc(tlog - 12.0)                  # a 12 s tail of log time behind the aircraft
                tr['cu'].bevel_factor_end = arc(tlog)

        # ---- T-030 M-6: props turn in the SIMULATED flight. ILLUSTRATIVE rate (not the plant's RPM, which the run does not log): a fixed step per frame, not a divisor of the 180 deg blade
        # symmetry, so a 60 fps film does not strobe; a prop turns only while the LOGGED thrust of its motor (th1..th4 of case.fwd.csv) is above 0.05 N. The real blade, adapter and spinner
        # meshes (PRP-002, PRP-004, PRP-005) turn about the motor axis (amodel.common.motor_R / station); the motor body (PRP-001) is a body of revolution and stays.
        SPIN_DEG_S = 47.0 * 60.0                                         # 47 deg per frame at 60 fps
        SPIN_MOTOR = {'LR': 'th1', 'UL': 'th2', 'LL': 'th3', 'UR': 'th4'}       # a_plant.py mot order: 1 FR (CAD lower right), 2 RL (upper left), 3 FL (lower left), 4 RR (upper right)
        SPIN_MIN_N = 0.05
        CM = next((m_ for m_ in list(sys.modules.values()) if m_ is not None and all(callable(getattr(m_, n_, None)) for n_ in ('motor_R', 'station', 'mrot'))), None)
        if CM is None:
            sys.path.insert(0, CAD_A)
            from amodel import common as CM

        def spin_mats(sh, tl):
            q = sh['sitl']
            tlog = sitl_clock(sh, tl)
            a_ = sitl_at(q['run'], tlog)
            out = {}
            for st_, col in SPIN_MOTOR.items():
                if a_[col] <= SPIN_MIN_N:
                    continue
                R_ = CM.motor_R(st_)
                ax_ = Vector((R_[0][0], R_[1][0], R_[2][0]))                      # motor axis (local +x in the station frame; the prop sits on the -x side, thrust along -x)
                sense = -1.0 if st_ in ('UR', 'LL') else 1.0                      # APC MRP (UR, LL) turns clockwise seen from the thrust side, MR counter-clockwise (propulsion.py MRP)
                ang = -sense * math.radians(SPIN_DEG_S * tl)                 # phase from the scene time (continuous over the S4 shots); + about the thrust axis (-x) is counter-clockwise seen from its tip
                M_ = rax(ax_, CM.station(st_), ang)
                for pre in ('PRP-002-', 'PRP-004-', 'PRP-005-'):
                    out[pre + st_] = M_
            return out

        HINGE = {}

        def hinge_objs():
            """3.2: the hinge axes (right and left) as thin orange rods along the elevon span, through (XH, HINGE_Z), so that 'the horn hole sits over the hinge line' can be seen (T-030 M-8)."""
            if not HINGE:
                import bmesh
                G = load_kin()['geom']
                ys = [(rest['WNG-006-R'] @ Vector(c_)).y for c_ in items['WNG-006-R'].bound_box]
                y0, y1 = min(ys), max(ys)
                for sy_ in (1, -1):
                    me = bpy.data.meshes.new('hinge axis')
                    bm = bmesh.new()
                    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.0009, radius2=0.0009, depth=y1 - y0, matrix=Matrix.Rotation(math.pi / 2, 4, 'X'))
                    bm.to_mesh(me)
                    bm.free()
                    me.materials.append(MATS['move'])
                    ob = bpy.data.objects.new('hinge axis', me)
                    sc.collection.objects.link(ob)
                    ob.location = Vector((G['XH'], sy_ * (y0 + y1) / 2, G['HINGE_Z']))
                    ob.hide_render = True
                    HINGE[sy_] = ob
            return HINGE

        def shot_pose(sh, tl):
            """(mm, mst, air): world motion matrix per CAD part (mechanism poses, and for a SITL shot the aircraft pose on top), mechanism state, aircraft pose."""
            mm, mst = mech_mats(sh, tl)
            if sh.get('props_spin') and sh.get('sitl'):
                mm = dict(mm)
                mm.update(spin_mats(sh, tl))
            air = sitl_pose(sh, tl) if sh.get('sitl') else None
            if air:
                mm = {pid: air['M'] @ mm.get(pid, Matrix.Identity(4)) for pid in items}
            return mm, mst, air

        def shot_cam(S, sh, tl, air):
            cam_c = hermite_cam(S['keys'], tl)
            tgt = Vector(cam_c[:3])
            if air and sh.get('follow'):
                tgt = tgt + air['Psm']                       # keys of a follow shot are offsets from the (filtered) aircraft position
            return cam_c, (tgt, cam_c[3], cam_c[4], cam_c[5])

        def film_pose(t):
            S, sh, tl = film_at(film, t)
            vis = shot_modes(sh)
            mm, mst, air = shot_pose(sh, tl)
            for pid, ob in items.items():
                if pid in be.wires:
                    ends = [ob.get(k_) for k_ in ('part_a', 'part_b') if ob.get(k_) in placed_ids]
                    on = bool(ends) and all(e_ in vis for e_ in ends) and sh.get('wires', True)
                    ob.hide_render = not on
                    if on:
                        tint(pid, None)
                        ob.matrix_world = (mm[pid] @ rest[pid]) if pid in mm else rest[pid]
                elif pid in vis:
                    ob.hide_render = False
                    ob.matrix_world = (mm[pid] @ rest[pid]) if pid in mm else rest[pid]
                    m = vis[pid]
                    tint(pid, ('ghost_spar' if pid.startswith('WNG-002') else 'ghost') if m == 'ghost' else (None if m == 'normal' else m))
                else:
                    ob.hide_render = True
            if sh.get('fea') and sh['fea']['glb'] not in FEA_OBJS:
                fea_objs(sh['fea']['glb'])
            for nm_, objs_ in FEA_OBJS.items():
                for o_ in objs_:
                    o_.hide_render = (sh.get('fea', {}).get('glb') != nm_)
            if sh.get('hinge_line'):
                hinge_objs()
            for ob_ in HINGE.values():
                ob_.hide_render = not sh.get('hinge_line')
            if air and not trail:
                trail_obj(sh['sitl']['run'], sh['sitl'].get('trail_from', 33.5))
            if trail:
                trail_set(air['tlog'] if air else 0.0, bool(air))
            cam_c, cv_ = shot_cam(S, sh, tl, air)
            ctr, view, dist = cam_view(cv_)
            cd.clip_end = 900.0 if air else 100.0
            cd.shift_x = float((sh.get('fea') or {}).get('shift_x', 0.0))      # moves a stress mesh left of the panels
            if air:                                                         # ground at z = 0 under the flown path; the stage grid is scaled to 5 m cells
                floor.location, floor.scale = Vector((200.0, 0.0, 0.0)), Vector((1000.0, 300.0, 1.0))
            else:
                floor.location, floor.scale = floor_default[0].copy(), floor_default[1].copy()
            look(cam, ctr + view * dist, ctr)
            set_focus(dist)
            below = (ctr + view * dist).z < floor.location.z + 0.06
            floor.hide_render = below or bool(sh.get('fea') or sh.get('plate'))
            caz = math.atan2(view.y, view.x)
            for lo_, daz, lel, dd in lights:
                aa, ee = caz + math.radians(daz), math.radians(lel)
                loc = ctr + Vector((math.cos(ee) * math.cos(aa), math.cos(ee) * math.sin(aa), math.sin(ee))) * dd
                look(lo_, loc, ctr, Vector((0, 0, 1)) if lel < 85 else Vector((1, 0, 0)))
            if air:
                blob_s.default_value = (0.55, 0.9, 1.0)
                blob_c.default_value = (air['P'].x, air['P'].y, 0.0)
                blob_op.default_value = 0.35 * max(0.0, 1.0 - air['P'].z / 6.0)
            else:
                blob_s.default_value = (0.55, 0.9, 1.0)
                blob_c.default_value = (full_c.x, 0.0, 0.0)
                blob_op.default_value = 0.0 if below else 0.35
            bpy.context.view_layer.update()
            return (tuple(sorted(vis.items())), tuple(round(v, 4) for v in cam_c), None if mst is None else (round(mst['theta_R'], 3), round(mst['delta'], 3), round(mst.get('delta_L', mst['delta']), 3)),
                    None if air is None else tuple(round(x, 5) for r_ in air['M'] for x in r_), sh['id'] if (sh.get('fea') or sh.get('plate')) else None,
                    tuple(round(x, 4) for r_ in mm['PRP-002-UR'] for x in r_) if (sh.get('props_spin') and 'PRP-002-UR' in mm) else None, bool(sh.get('hinge_line')))

        if a.cam_check:
            # ---- T-028: camera against the mesh, EVERY frame: (1) camera inside any visible part (closed-mesh ray parity), (2) distance to the nearest surface,
            # (3) line of sight to the target: first non-x-ray surface hit between camera and target. BVHs are built once in part-local space; the query is
            # moved into each part's local frame, so posed (mechanism) parts cost nothing extra.
            from mathutils.bvhtree import BVHTree
            loc_bvh = {}

            def local_bvh(pid):
                if pid not in loc_bvh:
                    ob = items[pid]
                    hv = ob.hide_viewport
                    ob.hide_viewport = False
                    bpy.context.view_layer.update()
                    eo = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    me = eo.to_mesh()
                    verts = [v.co.copy() for v in me.vertices]
                    polys = [tuple(pl.vertices) for pl in me.polygons]
                    eo.to_mesh_clear()
                    ob.hide_viewport = hv
                    if polys:
                        xs = [v.x for v in verts]
                        ys = [v.y for v in verts]
                        zs = [v.z for v in verts]
                        loc_bvh[pid] = (BVHTree.FromPolygons(verts, polys), (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))
                    else:
                        loc_bvh[pid] = None
                return loc_bvh[pid]

            def inside_test(bvh, pl):
                par = []
                for axv in (Vector((0, 0, 1)), Vector((1, 0, 0))):
                    o_, n_ = pl.copy(), 0
                    while n_ < 60:
                        h_ = bvh.ray_cast(o_, axv)
                        if h_[0] is None:
                            break
                        n_ += 1
                        o_ = h_[0] + axv * 1e-6
                    par.append(n_ % 2)
                return all(par)

            selftest = {}                                               # self-test of the inside test on solid parts: the middle of the part is inside, a point 0.2 m above is not
            for _pid, _off in (('WNG-006-R', (0.0, 0.07, 0.0)), ('WNG-007-R', (0.0, 0.0, 0.0)), ('WNG-001', (0.0, 0.3, 0.0))):
                _b = local_bvh(_pid)
                _c = Vector(((_b[1][0] + _b[2][0]) / 2, (_b[1][1] + _b[2][1]) / 2, (_b[1][2] + _b[2][2]) / 2)) + Vector(_off)
                selftest[_pid] = dict(centre_inside=bool(inside_test(_b[0], _c)), point_0p2_above_inside=bool(inside_test(_b[0], _c + Vector((0, 0, 0.2)))))
            print('CAMCHECK selftest', selftest, flush=True)
            inv_rest = {}
            report = dict(shots={}, frames_checked=0, near_m=0.05)
            per_shot = {}
            t_cc = time.time()
            for f in range(nfr):
                t = f / FPS
                S, sh, tl = film_at(film, t)
                vis = shot_modes(sh)
                mm, _mst, air = shot_pose(sh, tl)
                ids = [pid for pid in vis]
                if sh.get('wires', True):
                    for pid, ob in be.wires.items():
                        ends = [ob.get(k_) for k_ in ('part_a', 'part_b') if ob.get(k_) in placed_ids]
                        if ends and all(e_ in vis for e_ in ends):
                            ids.append(pid)
                cam_c, cv_ = shot_cam(S, sh, tl, air)
                ctr, view, dist = cam_view(cv_)
                P = ctr + view * dist
                los = sh.get('los', True)                                          # false: the target is only a framing offset (nothing to keep in sight); [x, y, z]: the subject point
                tgt_ = ctr if los is True else (Vector(los) if los else None)
                dirn = (tgt_ - P).normalized() if tgt_ is not None else None
                dist_t = (tgt_ - P).length if tgt_ is not None else 0.0
                inside, mind, mind_pid, hit_d, hit_pid = [], 1e9, None, 1e9, None
                for pid in ids:
                    B = local_bvh(pid)
                    if B is None:
                        continue
                    bvh, lo, hi = B
                    if pid in mm:
                        Mi = (mm[pid] @ rest[pid]).inverted()
                    else:
                        if pid not in inv_rest:
                            inv_rest[pid] = rest[pid].inverted()
                        Mi = inv_rest[pid]
                    pl = Mi @ P
                    bd = math.sqrt(max(lo[0] - pl.x, 0, pl.x - hi[0]) ** 2 + max(lo[1] - pl.y, 0, pl.y - hi[1]) ** 2 + max(lo[2] - pl.z, 0, pl.z - hi[2]) ** 2)
                    if bd < 0.3:
                        nr = bvh.find_nearest(pl)
                        if nr[0] is not None and nr[3] < mind:
                            mind, mind_pid = nr[3], pid
                        if bd == 0.0 and inside_test(bvh, pl):
                            inside.append(pid)
                    if tgt_ is not None and vis.get(pid) != 'ghost':
                        dl_ = Mi.to_3x3() @ dirn
                        h_ = bvh.ray_cast(pl, dl_, dist_t)
                        if h_[0] is not None and h_[3] < hit_d:
                            hit_d, hit_pid = h_[3], pid
                st = per_shot.setdefault('%s/%s' % (S['id'], sh['id']), dict(frames=0, inside_frames=0, inside_parts={}, min_clear_m=1e9, min_clear_f=None, min_clear_part=None,
                                                                             blocked_frames=0, blockers={}, first_inside=None, last_inside=None, worst_block_f=None, worst_block_ratio=1.0))
                st['frames'] += 1
                if inside:
                    st['inside_frames'] += 1
                    st['first_inside'] = f if st['first_inside'] is None else st['first_inside']
                    st['last_inside'] = f
                    for pid in inside:
                        st['inside_parts'][pid] = st['inside_parts'].get(pid, 0) + 1
                if mind < st['min_clear_m']:
                    st['min_clear_m'], st['min_clear_f'], st['min_clear_part'] = mind, f, mind_pid
                if hit_pid is not None and hit_d < dist_t - 0.08:                    # something other than the target's own surface is in front of it
                    st['blocked_frames'] += 1
                    st['blockers'][hit_pid] = st['blockers'].get(hit_pid, 0) + 1
                    if hit_d / dist_t < st['worst_block_ratio']:
                        st['worst_block_ratio'], st['worst_block_f'] = hit_d / dist_t, f
                report['frames_checked'] += 1
            for k_, v in per_shot.items():
                v['min_clear_m'] = None if v['min_clear_m'] > 1e8 else round(v['min_clear_m'], 4)
                v['worst_block_ratio'] = round(v['worst_block_ratio'], 3)
            report['shots'] = per_shot
            report['frames_inside_any_part'] = sum(v['inside_frames'] for v in per_shot.values())
            report['seconds'] = round(time.time() - t_cc, 1)
            report['mech'] = dict(MECH_LOG)
            report['selftest'] = selftest
            report['part_boxes_m'] = {pid: [[round(c_, 4) for c_ in (rest[pid] @ Vector(b_))] for b_ in (ob_.bound_box[0], ob_.bound_box[6])] for pid, ob_ in be.objects.items()}   # rest-pose world box corners, for placing cameras
            os.makedirs(a.out, exist_ok=True)
            json.dump(report, open(os.path.join(a.out, 'cam_clearance.json'), 'w'), indent=1)
            print('CAMCHECK frames %d inside %d  %.0f s' % (report['frames_checked'], report['frames_inside_any_part'], report['seconds']), flush=True)
            for k_, v in per_shot.items():
                print('CAMCHECK %s frames %d inside %d (%s) min_clear %s m @f%s (%s) blocked %d %s' % (k_, v['frames'], v['inside_frames'], v['inside_parts'], v['min_clear_m'], v['min_clear_f'], v['min_clear_part'], v['blocked_frames'], dict(sorted(v['blockers'].items(), key=lambda kv: -kv[1])[:3])), flush=True)
            return

        if a.frames:
            frames = [int(f) for f in a.frames.split(',') if f.strip()]
        elif a.range:
            f0, f1 = [int(v) for v in a.range.split(':')]
            frames = list(range(f0, min(f1, nfr), a.every))
        else:
            frames = list(range(0, nfr, a.every))
        os.makedirs(a.out, exist_ok=True)
        t0, prev_key, prev_name, n_new, fmap = time.time(), None, None, 0, {}
        for f in frames:
            key = film_pose(f / FPS)
            name = 'raw_%05d.png' % f
            if key == prev_key and prev_name:
                name = prev_name
            else:
                sc.render.filepath = os.path.join(a.out, name)
                bpy.ops.render.render(write_still=True)
                n_new += 1
            prev_key, prev_name = key, name
            fmap[f] = dict(raw=name, anc={})
            print('FRAME %d / %d rendered %d  %.0f s' % (f, nfr, n_new, time.time() - t0), flush=True)
        tag = a.range.replace(':', '_') if a.range else ('frames' if a.frames else 'all')
        json.dump(fmap, open(os.path.join(a.out, 'map_%s.json' % tag), 'w'))
        print('RENDER_TOTAL %.1f s for %d frames (%d rendered)' % (time.time() - t0, len(frames), n_new))
        if MECH_LOG['n']:
            print('MECHCHECK poses %d  max connection gap %.3e m  max rod length error %.3e m' % (MECH_LOG['n'], MECH_LOG['gap_max'], MECH_LOG['len_err_max']))
        return

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
    heads = {}
    for e in REVEAL_EDGES:                       # the tip of the fish wire that leads the lead: a small orange bead at the head of the revealed length
        bm = bpy.data.meshes.new(e + ' head')
        hob = bpy.data.objects.new(e + ' head', bm)
        sc.collection.objects.link(hob)
        import bmesh
        bmx = bmesh.new()
        bmesh.ops.create_uvsphere(bmx, u_segments=16, v_segments=10, radius=1.0)
        bmx.to_mesh(bm)
        bmx.free()
        bm.materials.append(MATS['move'])
        hob.scale = (HEAD_R_MM / 1000.0,) * 3
        hob.hide_render = True
        heads[e] = hob

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
        if bench_t0 <= t < b1['t_cam0']:                           # the cage frame is built beside the wing: the wing stays in the picture as an x-ray, it does not vanish and pop back
            s |= {p for p in items if p.startswith('WNG-00') and p in placed_ids and t >= show_from.get(p, 1e9)}
        for r_ in rows:                                            # step data 'ghost': x-ray parts from the step card to the end of the step
            if r_['info'].get('ghost') and r_['t_cam0'] <= t < r_['t_end']:
                s |= {p for p in r_['info']['ghost'] if p in items}
            if r_['id'] in GHOST_EXTRA and r_['t_cam0'] <= t < r_['t_end']:
                s |= {p for p in GHOST_EXTRA[r_['id']] if p in items}
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
        # ---- wires: reveal curves (phase leads), then the full meshes once laid
        rev_state = []
        for e in REVEAL_EDGES:
            f = reveal_fraction(e, t)
            full = t >= by_id[wire_step[e]]['t_mv1']
            ob = reveal[e]['ob']
            ob.hide_render = full or f <= 1e-4
            heads[e].hide_render = True
            if not ob.hide_render:
                off_e = cage_off if e in PHASE_EDGES else Vector()       # the phase leads follow the cage unit while it hovers / docks
                reveal[e]['cu'].bevel_factor_end = min(1.0, max(0.0, f))
                ob.matrix_world = Matrix.Translation(off_e)
                on_move = reveal_moving(e, t)
                if on_move:
                    heads[e].location = Vector(head_pos(e, f)) + off_e
                    heads[e].hide_render = False
                ob.material_slots[0].link = 'DATA'
                reveal[e]['cu'].materials[0] = MATS['move'] if on_move else (items[e].data.materials[0] if items[e].data.materials else MATS['move'])
                rev_state.append((e, round(f, 4), round(off_e.x, 4), round(off_e.y, 4), round(off_e.z, 4), bool(on_move)))
        for e in REVEAL_EDGES:
            if reveal[e]['ob'].hide_render and heads[e].hide_render is False:
                heads[e].hide_render = True
        for e, ob in be.wires.items():
            lay = by_id[wire_step[e]]
            vis = t >= (lay['t_mv1'] if (e in REVEAL_EDGES or lay['parts']) else lay['t_mv0'])      # wires laid by a marker step show while they are laid
            ob.hide_render = not vis
            if vis:
                tint(e, 'move' if t < lay['t_tint1'] else None)
                state.append((e, 1))
        # ---- camera: keyframed smooth moves between the views of consecutive steps (cam_at); x-ray steps follow the plug during its move
        ci = 0
        for q, r in enumerate(rows):
            if t >= r['t_cam0']:
                ci = q
        cur = rows[ci]
        cam_c = cam_at(t)
        if cur['id'] in ghost_by_id and cur['t_mv0'] <= t and not (cur['t_chk1'] > cur['t_chk0'] and t >= cur['t_chk0']):
            cam_c = ghost_cam(cur, ghost_centroid(cur, t))
        if t >= rows[-1]['t_stage_end']:                           # the whole aircraft: pull back and swing round
            k = smooth((t - rows[-1]['t_stage_end']) / 1.6)
            e_ = cams['END']
            last = kf[-1][1]
            az_ = e_[1] + 22 * smooth((t - rows[-1]['t_stage_end']) / T_END)
            cam_c = (last[0] * (1 - k) + e_[0] * k, last[1] * (1 - k) + az_ * k, last[2] * (1 - k) + e_[2] * k,
                     last[3] ** (1 - k) * e_[3] ** k)
            for p in sorted(placed_ids):
                if p in items:
                    tint(p, None)
        ctr, view, dist = cam_view(cam_c)
        look(cam, ctr + view * dist, ctr)
        set_focus(dist)
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
                if xy and 0.05 < xy[0] < 0.95 and 0.14 < xy[1] < 0.74:          # only labels whose part is on screen, in the free band above the step card
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
    if a.audit:
        rec = []
        for f in frames:
            key, anc = pose(f / FPS)
            vis = sorted(i for i, ob in items.items() if not ob.hide_render)
            revs = sorted(e for e in REVEAL_EDGES if not reveal[e]['ob'].hide_render)
            rec.append(dict(f=f, vis=vis, rev=revs, cam=key[2], labels=[l[0] for l in (anc.get('labels') or [])]))
        json.dump(rec, open(os.path.join(a.out, 'audit_%s.json' % (a.range.replace(':', '_') or 'all')), 'w'))
        print('AUDIT done', len(rec))
        return
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
    ap.add_argument('--fps', type=int, default=FPS)
    a = ap.parse_args(argv)
    apply_res(None, None, a.fps)
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


def title_alpha(row, t):
    """0..1 opacity of the stage title card: fades in over 0.5 s and out over 0.7 s (the camera glides to the first step's close view behind it)."""
    if row.get('t_title0') is None:
        return 1.0
    return max(0.0, min(1.0, (t - row['t_title0']) / 0.5, (row['t_title1'] - t) / 0.7))


def _init(rows, total, k, fps=None):
    if fps:
        apply_res(None, None, fps)          # spawned overlay processes re-import the module: give them the run's frame rate
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
    tl = None
    if kind == 'title':                                   # the title card is drawn on its own layer so that it can fade in and out
        tl = Image.new('RGBA', im.size, (0, 0, 0, 0))
        dtl = ImageDraw.Draw(tl)
        dtl.rectangle((0, 0, sw, sh), fill=(250, 251, 253, 214))
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
        d_main, d = d, dtl
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
    if tl is not None:
        ta = title_alpha(row, t)
        tl.putalpha(tl.getchannel('A').point(lambda v: int(v * ta)))
        lay = Image.alpha_composite(lay, tl)
        d = ImageDraw.Draw(lay)
    # ---- progress (by step, so that the picture stays constant while a card is read)
    prog = (stepno - 1) / float(nsteps) if kind != 'end' else 1.0
    by = sh - 12 * k
    d.rounded_rectangle((x0, by - 2 * k, x1, by + 1 * k), radius=2, fill=(220, 225, 232, 255))
    d.rounded_rectangle((x0, by - 2 * k, max(x0 + 3, x0 + (x1 - x0) * prog), by + 1 * k), radius=2, fill=ORANGE + (255,))
    Image.alpha_composite(im, lay).convert('RGB').save(dst, optimize=False, compress_level=1)


def _init_film(film, k, fps):
    apply_res(None, None, fps)
    _G['film'], _G['k'], _G['F'] = film, k, make_fonts(k)


def fea_ramp():
    """Utilisation colour ramp and the two status colours, parsed from fea_hub_figs.py (the same colours as the figures and the GLB skins)."""
    src = open(os.path.join(STRUCT_DIR, 'fea_hub_figs.py'), encoding='utf-8').read()
    ramp = re.findall(r"'(#[0-9a-fA-F]{6})'", re.search(r'^RAMP = \[(.*?)\]', src, re.M | re.S).group(1))
    crit, nj = re.findall(r"'(#[0-9a-fA-F]{6})'", re.search(r'^CRIT, NJ = (.*)$', src, re.M).group(1))
    return ramp, crit, nj


def _hex(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def film_overlay(src, dst, f, sw, sh):
    """T-027: Pillow pass of the short film: header, ILLUSTRATIVE (or other) tag, lower-third title (fades 0.4 s in / out), TODO placeholder
    card, closing card (values read from params-A.json at draw time)."""
    from PIL import Image, ImageDraw
    film, k, F = _G['film'], _G['k'], _G['F']
    t = f / FPS
    S, shot, tl = film_at(film, t)
    im = Image.open(src).convert('RGBA')
    vals = {kk: src_val(v) for kk, v in shot.get('vals', {}).items()}           # T-029: numbers of the FEA shots, read from the result files at draw time
    if shot.get('plate'):                                                        # image plate of an existing FEA figure (T-029), fitted between the header and the lower third
        pl = Image.open(os.path.join(REDESIGN, shot['plate']['image'])).convert('RGBA')
        bw_, bh_ = sw - 80 * k, sh - 96 * k - 150 * k
        sc_ = min(bw_ / pl.size[0], bh_ / pl.size[1])
        pl = pl.resize((int(pl.size[0] * sc_), int(pl.size[1] * sc_)), Image.LANCZOS)
        im.alpha_composite(pl, (int((sw - pl.size[0]) / 2), int(92 * k)))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, x1 = 40 * k, sw - 40 * k
    d.text((x0, 26 * k), 'Concept A quad tailsitter', font=F['h2'], fill=INK + (235,))
    d.text((x0, 52 * k), 'SCENE %s  /  SHOT %s' % (S['id'], shot['id']), font=F['mono'], fill=MUTED + (235,))
    tag = shot.get('tag')
    if tag and vals:
        tag = tag.format(**vals)
    if tag:
        tw = d.textlength(tag, font=F['mono'])
        d.rounded_rectangle((x1 - tw - 28 * k, 24 * k, x1, 24 * k + 36 * k), radius=int(6 * k), fill=(255, 255, 255, 235), outline=ORANGE + (255,), width=max(2, int(2 * k)))
        d.text((x1 - tw - 14 * k, 24 * k + 8 * k), tag, font=F['mono'], fill=ORANGE + (255,))
    if shot.get('sitl'):                 # T-029: live readout from the executed SITL run (same data as the aircraft pose)
        run = shot['sitl']['run']
        tlog = sitl_clock(shot, tl)
        a_ = sitl_at(run, tlog)
        sm_ = sitl_sum(run)
        rows_ = [('Pitch (nose up +)', '%+6.1f deg' % a_['pitch']), ('Altitude (CG)', '%6.1f m' % a_['alt']), ('Airspeed', '%6.1f m/s' % a_['V']),
                 ('Elevon left / right', '%+5.1f / %+5.1f deg' % (a_['dl'], a_['dr']))]
        notes_ = [('Log time %6.1f s   time scale x%.1f' % (tlog, sitl_scale(shot)), INK),
                  ('Run %s: %.2f kg, wind %.0f m/s (sum.json)' % (run, sm_['mass'], sm_['wind']), MUTED),
                  (shot['sitl'].get('note', ''), MUTED),
                  ('Prop rotation illustrative, not to rate' if shot.get('props_spin') else '', MUTED)]
        ld_ = sm_.get('landing')
        if shot['sitl'].get('landing_note') and ld_ and tlog >= ld_['t_touch']:
            notes_.append(('Touch-down at %.1f s: sink %.2f m/s, lean %.1f deg, tipped over: %s (sum.json)' % (ld_['t_touch'], ld_['sink_ms'], ld_['lean_deg_at_touch'], 'yes' if ld_['tipped_over'] else 'no'), INK))
        bw = 520 * k
        wl_ = []
        for tx_, col_ in notes_:
            if tx_:
                wl_ += [(ln_, col_) for ln_ in wrap(d, tx_, F['mono'], bw - 36 * k)]
        bh_ = (12 + len(rows_) * 34 + 10 + 22 * len(wl_) + 12) * k
        bx1, by1 = x1, sh - 44 * k
        d.rounded_rectangle((bx1 - bw, by1 - bh_, bx1, by1), radius=int(8 * k), fill=(255, 255, 255, 240), outline=(203, 210, 219, 255))
        for i_, (lab_, val_) in enumerate(rows_):
            d.text((bx1 - bw + 18 * k, by1 - bh_ + 12 * k + i_ * 34 * k), lab_, font=F['h2'], fill=SUB + (255,))
            d.text((bx1 - 18 * k - d.textlength(val_, font=F['h1']), by1 - bh_ + 10 * k + i_ * 34 * k), val_, font=F['h1'], fill=INK + (255,))
        yb_ = by1 - bh_ + 12 * k + len(rows_) * 34 * k + 6 * k
        for j_, (ln_, col_) in enumerate(wl_):
            d.text((bx1 - bw + 18 * k, yb_ + j_ * 22 * k), ln_, font=F['mono'], fill=col_ + (255,))
    if shot.get('readout'):              # T-029: FEA numbers read from the result files (rows: label, value format, name in shot vals)
        ro = shot['readout']
        n_ = len(ro['rows'])
        bw, bh_ = 500 * k, (46 + 32 * n_ + 58) * k
        bx1, by1 = x1, sh - 44 * k
        d.rounded_rectangle((bx1 - bw, by1 - bh_, bx1, by1), radius=int(8 * k), fill=(255, 255, 255, 240), outline=(203, 210, 219, 255))
        d.text((bx1 - bw + 18 * k, by1 - bh_ + 10 * k), ro['title'], font=F['mono'], fill=ORANGE + (255,))
        for i_, r_ in enumerate(ro['rows']):
            y_ = by1 - bh_ + 40 * k + i_ * 32 * k
            d.text((bx1 - bw + 18 * k, y_ + 2 * k), r_['label'], font=F['body'], fill=SUB + (255,))
            v_ = r_['fmt'] % tuple(vals[n] for n in r_['vals'])
            d.text((bx1 - 18 * k - d.textlength(v_, font=F['h2']), y_), v_, font=F['h2'], fill=INK + (255,))
        for j_, ln_ in enumerate(wrap(d, ro['src'], F['mono'], bw - 36 * k)[:2]):
            d.text((bx1 - bw + 18 * k, by1 - 52 * k + j_ * 22 * k), ln_, font=F['mono'], fill=MUTED + (255,))
        if ro.get('legend'):             # utilisation ramp, as in the figures
            ramp, crit, nj = fea_ramp()
            lw = 480 * k
            ly = by1 - bh_ - 92 * k
            d.rounded_rectangle((bx1 - lw - 12 * k, ly - 10 * k, bx1, ly + 78 * k), radius=int(8 * k), fill=(255, 255, 255, 240), outline=(203, 210, 219, 255))
            sw_ = (lw - 20 * k) / len(ramp)
            for i_, hx_ in enumerate(ramp):
                d.rectangle((bx1 - lw - 2 * k + i_ * sw_, ly, bx1 - lw - 2 * k + (i_ + 1) * sw_, ly + 18 * k), fill=_hex(hx_) + (255,))
            d.text((bx1 - lw - 2 * k, ly + 22 * k), '0', font=F['mono'], fill=MUTED + (255,))
            d.text((bx1 - 22 * k, ly + 22 * k), '1', font=F['mono'], fill=MUTED + (255,))
            d.text((bx1 - lw + 120 * k, ly + 22 * k), 'utilisation (1 = allowable)', font=F['mono'], fill=MUTED + (255,))
            d.rectangle((bx1 - lw - 2 * k, ly + 50 * k, bx1 - lw + 14 * k, ly + 66 * k), fill=_hex(crit) + (255,))
            d.text((bx1 - lw + 22 * k, ly + 48 * k), 'over 1', font=F['mono'], fill=INK + (255,))
            d.rectangle((bx1 - lw + 130 * k, ly + 50 * k, bx1 - lw + 146 * k, ly + 66 * k), fill=_hex(nj) + (255,))
            d.text((bx1 - lw + 154 * k, ly + 48 * k), 'not judged (pins, load ends)', font=F['mono'], fill=INK + (255,))
    if shot.get('mech') and 'sweep' in shot['mech']:                 # readout of the solved linkage state (numbers from linkage_kinematics.csv through mech_state, AR-001)
        st = mech_state(shot, tl)
        rows_ = [('Servo arm', '%+5.1f deg' % st['theta_R']), ('Elevon', '%+5.1f deg' % st['delta'])]
        bw, bh_ = 330 * k, 112 * k
        bx1, by1 = x1, sh - 44 * k
        d.rounded_rectangle((bx1 - bw, by1 - bh_, bx1, by1), radius=int(8 * k), fill=(255, 255, 255, 240), outline=(203, 210, 219, 255))
        for i_, (lab_, val_) in enumerate(rows_):
            d.text((bx1 - bw + 18 * k, by1 - bh_ + 12 * k + i_ * 32 * k), lab_, font=F['h2'], fill=SUB + (255,))
            d.text((bx1 - 18 * k - d.textlength(val_, font=F['h1']), by1 - bh_ + 10 * k + i_ * 32 * k), val_, font=F['h1'], fill=INK + (255,))
        d.text((bx1 - bw + 18 * k, by1 - 30 * k), 'AR-001 table; + = trailing edge down', font=F['mono'], fill=MUTED + (255,))
    if shot.get('todo'):
        lines = wrap(d, shot['todo'], F['h1'], sw * 0.62)
        bh = (60 + 36 * len(lines)) * k
        y0 = sh * 0.38 - bh / 2
        d.rounded_rectangle((sw * 0.19, y0, sw * 0.81, y0 + bh), radius=int(10 * k), fill=(255, 255, 255, 240), outline=ORANGE + (255,), width=max(2, int(3 * k)))
        d.text((sw * 0.19 + 24 * k, y0 + 14 * k), 'TODO  PLACEHOLDER SHOT %s' % shot['id'], font=F['mono'], fill=ORANGE + (255,))
        for i, ln in enumerate(lines):
            d.text((sw * 0.19 + 24 * k, y0 + 46 * k + i * 36 * k), ln, font=F['h1'], fill=INK + (255,))
    ll = Image.new('RGBA', im.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(ll)
    card = shot.get('card')
    if card:
        lines = card.get('lines', [])
        rows_c, cites = [], []
        for ln in lines:                          # value lines: a params-A.json key, or a text over values read from records at draw time (T-030 M-2: every line cites its record)
            if 'key' in ln:
                rows_c.append((ln['label'], ln['fmt'] % param_value(ln['key'])))
                cites.append('params-A.json ' + ln['key'])
            else:
                lv = {n_: src_val(sp_) for n_, sp_ in ln.get('vals', {}).items()}
                rows_c.append((ln['label'], ln['text'].format(**lv)))
                if ln.get('cite'):
                    cites.append(ln['cite'])
        foot = wrap(dl, 'Sources: ' + '; '.join(cites), F['mono'], x1 - x0 - 60 * k)[:4]
        bh = (96 + 36 * len(rows_c) + 12 + 22 * len(foot) + 18) * k
        y1_ = sh - 40 * k
        y0_ = y1_ - bh
        dl.rounded_rectangle((x0, y0_, x1, y1_), radius=int(12 * k), fill=(255, 255, 255, 246), outline=(203, 210, 219, 255))
        dl.rectangle((x0, y0_ + 12 * k, x0 + 6 * k, y1_ - 12 * k), fill=ORANGE + (255,))
        dl.text((x0 + 30 * k, y0_ + 16 * k), card.get('kicker', ''), font=F['mono'], fill=ORANGE + (255,))
        dl.text((x0 + 30 * k, y0_ + 40 * k), card['name'], font=F['big'], fill=INK + (255,))
        y = y0_ + 100 * k
        for lab_, txt_ in rows_c:
            dl.text((x0 + 30 * k, y + 2 * k), lab_, font=F['h2'], fill=SUB + (255,))
            dl.text((x0 + 400 * k, y), txt_, font=F['h2'], fill=INK + (255,))
            y += 36 * k
        for j_, ln_ in enumerate(foot):
            dl.text((x0 + 30 * k, y + 8 * k + j_ * 22 * k), ln_, font=F['mono'], fill=MUTED + (255,))
    elif shot.get('title'):
        sub = wrap(dl, shot.get('sub', '').format(**vals) if vals else shot.get('sub', ''), F['body'], sw * (0.86 if shot.get('plate') else 0.40 if shot.get('readout') else 0.55))[:3]
        bh = (40 + 32 + 26 * len(sub)) * k
        y1_ = sh - 44 * k
        y0_ = y1_ - bh
        wmax = max([dl.textlength(shot['title'], font=F['h1'])] + [dl.textlength(q, font=F['body']) for q in sub]) + 52 * k
        dl.rounded_rectangle((x0, y0_, x0 + wmax, y1_), radius=int(8 * k), fill=(255, 255, 255, 240), outline=(203, 210, 219, 255))
        dl.rectangle((x0, y0_ + 8 * k, x0 + 5 * k, y1_ - 8 * k), fill=ORANGE + (255,))
        dl.text((x0 + 24 * k, y0_ + 12 * k), shot['title'], font=F['h1'], fill=INK + (255,))
        for i, q in enumerate(sub):
            dl.text((x0 + 24 * k, y0_ + 50 * k + i * 26 * k), q, font=F['body'], fill=SUB + (255,))
    a_ = shot_fade(shot, tl) / 12.0
    if a_ < 1.0:
        ll.putalpha(ll.getchannel('A').point(lambda v: int(v * a_)))
    lay = Image.alpha_composite(lay, ll)
    out = Image.alpha_composite(im, lay).convert('RGB')
    dp = dip_level(film, t)
    if dp > 0:                                    # T-030 m-1: a 0.4 s dip to the stage colour around each scene join (0.2 s either side), done here so it costs no Blender time
        out = Image.blend(out, Image.new('RGB', out.size, DIP_RGB), min(1.0, dp / 12.0))
    out.save(dst, optimize=False, compress_level=1)


DIP_RGB = (240, 243, 247)
DIP_S = 0.2


def shot_fade(shot, tl):
    """Opacity of a shot's lower third / card in twelfths: 0.4 s fade in and out for a title, 0.4 s fade in for the closing card (T-030 m-1)."""
    if shot.get('card'):
        return round(max(0.0, min(1.0, (tl - shot['t0'] + shot.get('fade_src_a', 0.0)) / 0.4)) * 12)       # fade_src_a: the highlight cut starts inside the source shot, whose card has already faded in
    if shot.get('title'):
        return round(max(0.0, min(1.0, (tl - shot['t0']) / 0.4, (shot['t1'] - tl) / 0.4)) * 12)
    return 12


def dip_level(film, t):
    """Dip to the stage colour in twelfths at film time t: 12 at a scene join, 0 DIP_S s away on either side (not at the very start and end of the film)."""
    lv = 0.0
    for i, S in enumerate(film['scenes']):
        if i > 0:
            lv = max(lv, 1.0 - (t - S['t0']) / DIP_S) if 0 <= t - S['t0'] < DIP_S else lv
        if i < len(film['scenes']) - 1:
            e = S['t0'] + S['dur']
            lv = max(lv, 1.0 - (e - t) / DIP_S) if 0 < e - t <= DIP_S else lv
    return round(lv * 12)


def _film_job(args):
    return film_overlay(*args)


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


def RES_FLAGS(a):
    return ['--width', str(W), '--height', str(H), '--fps', str(FPS)] + (['--dof'] if getattr(a, 'dof', False) else []) + (['--motion-blur'] if getattr(a, 'motion_blur', False) else [])


def write_timing(path, d):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    json.dump(d, open(path, 'w'), indent=1)
    print('TIMING', path, json.dumps(d))


def contact_sheet(frames, name_of, work, fps, film, out, cols=8, tw=240):
    """Grid of the given film frames (after overlay) with time stamps and scene / shot ids."""
    from PIL import Image, ImageDraw
    th = int(tw * H / W)
    rows_n = (len(frames) + cols - 1) // cols
    gap, lab = 4, 18
    sheet = Image.new('RGB', (cols * (tw + gap) + gap, rows_n * (th + lab + gap) + gap), (24, 28, 34))
    d = ImageDraw.Draw(sheet)
    fnt = _font(['consola.ttf', 'cour.ttf'], 12)
    for i, f in enumerate(frames):
        x, y = gap + (i % cols) * (tw + gap), gap + (i // cols) * (th + lab + gap)
        sheet.paste(Image.open(os.path.join(work, name_of[f])).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y))
        S, shot, _ = film_at(film, f / fps)
        d.text((x + 2, y + th + 2), 'f%05d  %6.2fs  %s/%s' % (f, f / fps, S['id'], shot['id']), font=fnt, fill=(220, 226, 235))
    sheet.save(out)


def film_driver(a):
    """T-027 short-film mode: shot list -> Blender workers (render) -> Pillow overlay -> contact sheet (preview) or MP4 (full)."""
    from PIL import Image
    t0 = time.time()
    scene_ids = [x for x in a.scenes.split(',') if x] or None
    film = load_film(a.shot_list, scene_ids)
    nfr = int(round(film['total'] * FPS))
    every = max(1, a.every)
    work = os.path.abspath(a.work if a.work != os.path.join(tempfile.gettempdir(), 'a_build_film') else os.path.join(tempfile.gettempdir(), 'a_film'))
    os.makedirs(work, exist_ok=True)
    for fn in os.listdir(work):
        if fn.startswith('map_') and fn.endswith('.json') and not a.skip_render:
            os.remove(os.path.join(work, fn))
    print('film: %d scenes, %.1f s, %d frames at %dx%d @ %d fps, every %d' % (len(film['scenes']), film['total'], nfr, W, H, FPS, every), flush=True)
    me = os.path.abspath(__file__)
    if getattr(a, 'cam_check', False):
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', work, '--shot-list', os.path.abspath(a.shot_list), '--scenes', ','.join(scene_ids or []),
             '--cam-check'] + RES_FLAGS(a), show=('CAMCHECK', 'Traceback', 'Error', '  File'))
        shutil.copy(os.path.join(work, 'cam_clearance.json'), os.path.join(FILM_DIR, 'cam-clearance.json'))
        print('CAMCHECK written', os.path.join(FILM_DIR, 'cam-clearance.json'), '%.0f s' % (time.time() - t0))
        return
    base = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', work, '--samples', str(a.samples), '--shot-list', os.path.abspath(a.shot_list),
            '--scenes', ','.join(scene_ids or [])] + RES_FLAGS(a)
    if a.no_rt if hasattr(a, 'no_rt') else False:
        base.append('--no-rt')
    nw = max(1, a.workers)
    per = (nfr + every - 1) // every
    cuts = [min(nfr, (per * i // nw) * every) for i in range(nw)] + [nfr]       # cut points are multiples of --every so the workers' frame sets are disjoint
    t_r = time.time()
    procs = []
    for i in range(nw):
        if cuts[i] >= cuts[i + 1] or a.skip_render:
            continue
        print('> worker %d: frames %d-%d' % (i, cuts[i], cuts[i + 1] - 1), flush=True)
        lg = open(os.path.join(work, 'worker_%d.log' % i), 'w')
        procs.append((subprocess.Popen(base + ['--range', '%d:%d' % (cuts[i], cuts[i + 1]), '--every', str(every)], stdout=lg, stderr=subprocess.STDOUT), lg))
    for p, lg in procs:
        p.wait()
        lg.close()
        if p.returncode != 0:
            raise SystemExit('blender worker failed, see worker_*.log in ' + work)
    t_render = time.time() - t_r
    frame_s = []                          # per worker: seconds Blender spent in the frame loop (RENDER_TOTAL), without its start-up (CAD build, about a minute)
    for i in range(nw):
        try:
            frame_s += [float(m_) for m_ in re.findall(r'RENDER_TOTAL ([0-9.]+) s', open(os.path.join(work, 'worker_%d.log' % i)).read())]
        except OSError:
            pass
    fmap = {}
    for fn in sorted(os.listdir(work)):
        if fn.startswith('map_') and fn.endswith('.json') and fn != 'map_frames.json':
            for kk, v in json.load(open(os.path.join(work, fn))).items():
                fmap[int(kk)] = v
    frames = sorted(fmap)
    sw, sh = Image.open(os.path.join(work, fmap[frames[0]]['raw'])).size
    k = sw / BASE_W
    keys, jobs, name_of = {}, [], {}
    for f in frames:
        S, shot, tl = film_at(film, f / FPS)
        fade = shot_fade(shot, tl)
        key = (fmap[f]['raw'], S['id'], shot['id'], fade, dip_level(film, f / FPS), f if shot.get('sitl') else 0)
        if key not in keys:
            keys[key] = 'lab_%05d.png' % len(keys)
            jobs.append((os.path.join(work, fmap[f]['raw']), os.path.join(work, keys[key]), f, sw, sh))
        name_of[f] = keys[key]
    t_o = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=8, initializer=_init_film, initargs=(film, k, FPS)) as ex:
        list(ex.map(_film_job, jobs, chunksize=4))
    t_overlay = time.time() - t_o
    rendered = len({fmap[f]['raw'] for f in frames})
    print('mapped %d frames, %d rendered, %d overlay pictures' % (len(frames), rendered, len(jobs)), flush=True)
    if a.contact:
        os.makedirs(os.path.dirname(os.path.abspath(a.contact)), exist_ok=True)
        contact_sheet(frames, name_of, work, FPS, film, a.contact)
        print('CONTACT', a.contact)
    t_enc = 0.0
    if not a.preview and every == 1:
        t_e = time.time()
        lst = os.path.join(work, '_list.txt')
        open(lst, 'w').write('\n'.join(name_of[f] for f in frames))
        os.makedirs(os.path.dirname(os.path.abspath(a.film_out)), exist_ok=True)
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', work, '--list', lst, '--out', os.path.abspath(a.film_out), '--crf', a.crf, '--w', str(W), '--h', str(H), '--fps', str(FPS)])
        t_enc = time.time() - t_e
    write_timing(a.timing or os.path.join(FILM_DIR, 'timing.json'),
                 dict(film=os.path.basename(a.shot_list), scenes=[S['id'] for S in film['scenes']], film_seconds=round(film['total'], 2), frames=nfr, frames_mapped=len(frames), every=every,
                      rendered=rendered, overlay_pictures=len(jobs), seconds=round(time.time() - t0, 1), seconds_render=round(t_render, 1), seconds_overlay=round(t_overlay, 1),
                      seconds_encode=round(t_enc, 1), seconds_blender_start_and_frames=round(t_render, 1), seconds_frame_loop_per_worker=[round(x, 1) for x in frame_s], seconds_per_rendered_frame=round(sum(frame_s) / max(1, rendered), 2), workers=nw, samples=a.samples,
                      resolution=[W, H], fps=FPS, dof=a.dof, motion_blur=a.motion_blur, ray_tracing=not getattr(a, 'no_rt', False), preview=bool(a.preview), sources=source_hashes(film)))


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
    ap.add_argument('--skip-camplan', action='store_true', help='keep the existing cam_plan.json (otherwise it is recomputed first, about 1.5 min)')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--crf', default='MEDIUM', help='H.264 quality of the whole film (lowered until under --max-mb)')
    ap.add_argument('--stage-crf', default='MEDIUM')
    ap.add_argument('--max-mb', type=float, default=13.0)
    add_res_args(ap)
    ap.add_argument('--shot-list', default='', help='short-film mode (T-027): shot-list JSON (see film/shots-main.json)')
    ap.add_argument('--scenes', default='', help='short-film mode: comma list of scene ids (default all)')
    ap.add_argument('--every', type=int, default=0, help='short-film preview: render every Nth frame (0 = all; with --preview no encode, writes a contact sheet)')
    ap.add_argument('--contact', default='', help='short-film preview: contact-sheet PNG path')
    ap.add_argument('--film-out', default=os.path.join(FILM_DIR, 'film.mp4'), help='short-film mode: MP4 written when not a preview')
    ap.add_argument('--timing', default='', help='timing.json path (short film default film/timing.json; build film: animation/timing.json on a full run)')
    ap.add_argument('--dof', action='store_true', help='depth of field on the camera target (off by default)')
    ap.add_argument('--motion-blur', action='store_true', help='EEVEE motion blur (off by default)')
    ap.add_argument('--no-rt', action='store_true', help='short film: EEVEE ray tracing off')
    ap.add_argument('--cam-check', action='store_true', help='short film: no render, camera-vs-mesh clearance of every frame (film/cam-clearance.json)')
    a = ap.parse_args()
    apply_res(a.width, a.height, a.fps)
    t0 = time.time()
    if a.shot_list:
        return film_driver(a)
    a.work = os.path.abspath(a.work)
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if not a.skip_camplan:           # the per-step cameras (cam_plan.json) give the camera move times of the schedule: refresh them first
        run([a.blender, '-b', '--factory-startup', '-P', os.path.abspath(__file__), '--', 'render', '--out', a.work, '--camplan'] + RES_FLAGS(a), show=('CAMPLAN', 'Traceback', 'Error', '  File'))
    rows, total = timeline()
    nframes = int(total * FPS)
    print('%d steps, %d stages, %.1f s (%.1f min), %d frames' % (len(rows), len(STAGES), total, total / 60, nframes))
    me = os.path.abspath(__file__)
    every, scale = (4, 0.5) if a.preview else (1, 1.0)
    chunk_maps = []
    if not a.skip_render:
        base = [a.blender, '-b', '--factory-startup', '-P', me, '--', 'render', '--out', a.work, '--samples', str(a.samples), '--scale', str(scale)] + RES_FLAGS(a)
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
    k = Image.open(os.path.join(a.work, fmap[frames[0]]['raw'])).size[0] / BASE_W
    sw, sh = Image.open(os.path.join(a.work, fmap[frames[0]]['raw'])).size
    keys, jobs, name_of = {}, [], {}
    for f in frames:
        fm = fmap[f]
        info = frame_info(rows, total, f)
        row = info[1]
        t = f / FPS
        fab_on = bool(row['fab'] and t < row['t_mv0']) or bool(row['marker_chip'] and row['t_mv0'] - 0.01 <= t < row['t_mv1'] + 1.5)
        key = (fm['raw'], info[3], row['id'], fab_on, round(title_alpha(row, t) * 12) if info[3] == 'title' else 0, json.dumps(fm['anc'], sort_keys=True))
        if key not in keys:
            nm = 'lab_%05d.png' % len(keys)
            keys[key] = nm
            jobs.append((os.path.join(a.work, fm['raw']), os.path.join(a.work, nm), f, fm, sw, sh))
        name_of[f] = keys[key]
    print('%d overlay pictures' % len(jobs), flush=True)
    done = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=8, initializer=_init, initargs=(rows, total, k, FPS)) as ex:
        for _ in ex.map(_overlay_job, jobs, chunksize=8):
            done += 1
            if done % 300 == 0:
                print('OVERLAY %d / %d' % (done, len(jobs)), flush=True)
    if a.frames or a.preview:
        print('test frames in', a.work)
        json.dump({str(f): name_of[f] for f in frames}, open(os.path.join(a.work, 'lab_index.json'), 'w'))
        if a.timing:
            write_timing(a.timing, dict(film='a-build (test frames)', frames=nframes, rendered=len({fmap[f]['raw'] for f in frames}), overlay_pictures=len(jobs),
                         seconds=round(time.time() - t0, 1), workers=1, samples=a.samples, resolution=[sw, sh], fps=FPS))
        return

    def encode(names, out, crf):
        lst = os.path.join(a.work, '_list.txt')
        open(lst, 'w').write('\n'.join(names))
        run([a.blender, '-b', '--factory-startup', '-P', me, '--', 'encode', '--src', a.work, '--list', lst, '--out', out, '--crf', crf, '--w', str(W), '--h', str(H), '--fps', str(FPS)])

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
    write_timing(a.timing or os.path.join(OUT, 'timing.json'), dict(film='a-build', frames=nframes, rendered=len({fmap[f]['raw'] for f in frames}), overlay_pictures=len(jobs),
                 seconds=round(time.time() - t0, 1), workers=1 if a.preview else a.workers, samples=a.samples, resolution=[W, H], fps=FPS))


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
