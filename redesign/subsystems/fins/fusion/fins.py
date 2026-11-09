"""K09-L fins subsystem (FIN), owner D3, design R2 (braced fin per C4). Two fins at y = +/-0.32 m. Each fin = one
continuous CF motor tube through the wing core at x 0.045, an upper and a lower one-layer foam-board half-fin behind
it, a printed PETG through-core block that joins tube, spar and core, and per motor station a slip-clamp motor mount
(3 deg canted face), a station collar under it, a pultruded CF brace from the station collar to the spar, and two CF
edge strips along the half-fin top edge.

    build(ctx)            Fusion / stub module (fusionkit), cruise attitude, aircraft frame (DATUMS.md)
    geometry(P, LP, co)   every derived dimension, shared with make_fins.py and team/D3/fins_calcs.py
    part_specs(), edge_specs(G)   the part and edge lists make_fins.py writes to interfaces.json

Part ids (instance suffix: R/L side, U/D upper/lower half, UR/UL/LR/LL motor station, O/I outboard/inboard face):
FIN-001-RU/RD/LU/LD half-fins · FIN-002-R/L motor tubes · FIN-003-<st> motor mounts · FIN-004-R/L through-core
blocks (with keyhole bore bosses) · FIN-006-R/L tube plugs · FIN-007-<st> ESC pads · FIN-008-<st> station collars ·
FIN-009-<st> braces · FIN-010-<st> brace anchors · FIN-011-<half><O|I> edge strips.

Fin-tube junction (P25): the tube IS the fin leading edge. The flat board butts the tube and is held by the slotted
bore boss of the block at the root and by the station collar at the top (both: 22.3 mm bore + a board slot aft), with a
microballoon-epoxy fillet along the LE between them; nothing wraps the board around the tube. Load path: motor ->
mount (friction clamp, the D-23 fuse) -> tube -> station collar -> brace (axial) -> anchor -> spar, and tube -> block
(socket bore) -> spar bore -> spar; fin top edge -> CF edge strips -> station collar; fin root -> fillets -> core.

Cant (D-09): the motor face is the plane through the motor point tilted 3 deg about the radial line from the x-axis
to the motor; four bearing pads with ruled Z-loft tops lie exactly on it (axis-aligned shapes only, no rotated
component). The brace is a ruled Y-loft between two (x, z) rectangles, exact for a straight strip.

UNVERIFIED-IN-FUSION: lofts of the pads and braces; the block socket is flat-topped at the local surface (sand flush,
BUILD step 6); the strip slots in the ear and anchor are where the brace body overlaps them (cut with the brace body
as the tool in Fusion); C-shaped loops (slit collar, keyhole bosses and collars) untested in Fusion.
"""
import json
import math
import os

import k09kit as k9

STATIONS = ('UR', 'UL', 'LR', 'LL')
HALF = {'UR': 'RU', 'UL': 'LU', 'LR': 'RD', 'LL': 'LD'}          # motor station -> half-fin under it
TUBE = {'R': 'FIN-002-R', 'L': 'FIN-002-L'}
HALVES = ('RU', 'RD', 'LU', 'LD')


# ----------------------------------------------------------------------------- numbers
def lval(LP, key, unit=None):
    """Value of a fins/params.json leaf under fin_detail (unit-checked)."""
    d = LP['fin_detail']
    for k in key.split('.'):
        d = d[k]
    if unit is not None and d.get('unit') != unit:
        raise KeyError('fins/params.json fin_detail.%s is in %s, not %s' % (key, d.get('unit'), unit))
    return d['value']


def load_local(path=None):
    path = path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'params.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def geometry(P, LP, coords):
    """All derived dimensions (m) of the right / upper-right instances. P = params.json, LP = fins/params.json."""
    v = lambda k, u=None: k9.val(P, k, u)
    l = lambda k, u=None: lval(LP, k, u)
    G = {}
    c = v('wing.chord_m', 'm')
    G['c'], G['coords'] = c, coords
    G['zu'] = lambda x: k9.surface_z(coords, c, x / c, 'upper')
    G['zl'] = lambda x: k9.surface_z(coords, c, x / c, 'lower')
    G['yf'], G['h'], G['te'] = v('fins.y_m', 'm'), v('fins.half_height_m', 'm'), v('fins.te_x_m', 'm')
    G['xt'], G['od'], G['id'] = v('fins.tube.x_m', 'm'), v('fins.tube.od_m', 'm'), v('fins.tube.id_m', 'm')
    G['layers'] = l('layers')
    G['t_fin'] = v('fins.board_t_m', 'm') * G['layers']
    G['L_tube'] = l('tube_length_m', 'm')
    G['z_tube_end'] = G['L_tube'] / 2
    G['r_t'] = G['od'] / 2
    G['r_b'] = G['r_t'] + l('bond_gap_m', 'm')                      # every printed bore on the tube
    G['xs'], G['zs'] = v('wing.spar.x_m', 'm'), v('wing.spar.z_m', 'm')
    G['r_s'] = v('wing.spar.od_m', 'm') / 2
    G['r_bs'] = G['r_s'] + l('bond_gap_m', 'm')
    G['zm'], G['cant'] = v('propulsion.stations.z_m', 'm'), v('propulsion.stations.cant_deg', 'deg')
    ym = v('propulsion.stations.y_m', 'm')
    n = math.hypot(ym, G['zm'])
    G['t_hat'] = (0.0, -G['zm'] / n, ym / n)                         # x_hat x r_hat, r_hat = x-axis -> motor UR
    G['sense'] = l('mount.cant_sense_UR')

    # motor mount (UR)
    G['col_r'] = G['r_b'] + l('mount.collar_wall_m', 'm')
    G['x_col_front'] = G['xt'] - G['col_r']
    G['x_face'] = G['x_col_front'] - l('mount.face_ahead_m', 'm')
    G['pad_h'], G['plate_t'] = l('mount.pad_h_m', 'm'), l('mount.plate_t_m', 'm')
    G['x_slab0'] = G['x_face'] + G['pad_h']
    G['x_slab1'] = G['x_slab0'] + G['plate_t']
    G['pattern'] = l('mount.bolt_pattern_m', 'm')
    G['holes'] = [(s * G['pattern'][0] / 2, 0.0) for s in (1, -1)] + [(0.0, s * G['pattern'][1] / 2) for s in (1, -1)]
    G['head_d'] = l('mount.head_d_m', 'm')
    G['z_head_low'] = G['zm'] - G['pattern'][1] / 2 - G['head_d'] / 2
    G['z_cap1'] = G['z_head_low'] - l('mount.head_clear_m', 'm')
    G['z_cap0'] = G['z_cap1'] - l('mount.cap_t_m', 'm')
    G['slip'] = G['z_cap0'] - G['z_tube_end']
    G['grip'] = l('mount.grip_m', 'm')
    G['z_col0'] = G['z_tube_end'] - G['grip']
    G['z_grip_mid'] = G['z_tube_end'] - G['grip'] / 2
    G['plate_hy'], G['plate_hz'] = l('mount.plate_half_y_m', 'm'), l('mount.plate_half_z_m', 'm')
    G['x_prop'] = G['x_face'] - l('mount.prop_stack_m', 'm')
    G['prop_gap'] = G['x_col_front'] - G['x_prop']
    tc = math.tan(math.radians(G['cant']))
    G['face_x_at'] = lambda dy, dz, s=G['sense']: G['x_face'] + s * tc * (G['t_hat'][1] * dy + G['t_hat'][2] * dz)
    stacks = [G['x_slab1'] - G['face_x_at'](dy, dz) for dy, dz in G['holes']]
    G['stack_min'], G['stack_max'] = min(stacks), max(stacks)
    G['screw_len'] = l('mount.motor_screw_len_m', 'm')
    G['engage_min'] = G['screw_len'] - G['stack_max']
    G['slit'], G['cap_lip_r'] = l('mount.slit_m', 'm'), l('mount.cap_lip_r_m', 'm')
    G['ear_t'], G['ear_len'], G['ear_h'] = l('mount.ear_t_m', 'm'), l('mount.ear_len_m', 'm'), l('mount.ear_h_m', 'm')
    G['pad_c'], G['pad_hw'] = l('mount.pad_centre_m', 'm'), l('mount.pad_half_m', 'm')
    G['cheek_t'], G['cheek_y_in'], G['cheek_len'] = (l('mount.cheek_t_m', 'm'), l('mount.cheek_y_in_m', 'm'),
                                                     l('mount.cheek_len_m', 'm'))
    G['screw_hole_r'], G['shaft_hole_r'] = l('mount.screw_hole_d_m', 'm') / 2, l('mount.shaft_hole_d_m', 'm') / 2
    G['slip_torque'] = l('mount.slip_torque_nm', 'N m')
    G['slip_lever'] = G['xt'] - (G['x_face'] - v('propulsion.motor_length_m', 'm') / 2)   # tube axis to can middle
    G['slip_force'] = G['slip_torque'] / G['slip_lever']

    # station collar (under the mount) and the board top edge
    G['sc_h'] = l('station_collar.height_m', 'm')
    G['z_sc1'] = G['z_col0'] - l('station_collar.gap_m', 'm')
    G['z_sc0'] = G['z_sc1'] - G['sc_h']
    G['z_sc_mid'] = (G['z_sc0'] + G['z_sc1']) / 2
    G['sc_r_out'] = G['r_b'] + l('station_collar.ring_wall_m', 'm')
    G['es_w'], G['es_t'] = l('edge_strip.w_m', 'm'), l('edge_strip.t_m', 'm')
    G['sc_slot_hw'] = G['t_fin'] / 2 + G['es_t'] + l('boss.slot_clear_m', 'm')
    G['sc_slot_wall'] = l('station_collar.slot_wall_m', 'm')
    G['sc_x_end'] = G['xt'] + G['r_t'] + l('station_collar.tail_m', 'm')
    G['sc_ear_len'], G['sc_ear_w'] = l('station_collar.ear_len_m', 'm'), l('station_collar.ear_w_m', 'm')

    # half-fin
    G['x_le'] = G['xt'] + G['r_t'] + l('fin.le_gap_m', 'm')
    G['z_le_top'] = G['z_sc1']
    G['ztop'] = lambda x: G['z_le_top'] + (G['h'] - G['z_le_top']) * (x - G['x_le']) / (G['te'] - G['x_le'])
    G['x_hinge'] = c * k9.hinge_frac(P)
    G['slot_hw'], G['slot_d'] = l('link_slot.half_width_m', 'm'), l('link_slot.depth_m', 'm')

    # keyhole bosses on the block (bore extension + board root slot, CR-C4-04)
    G['boss_h'], G['boss_wall'] = l('boss.height_m', 'm'), l('boss.ring_wall_m', 'm')
    G['boss_r_out'] = G['r_b'] + G['boss_wall']
    G['boss_slot_hw'] = G['t_fin'] / 2 + l('boss.slot_clear_m', 'm')
    G['boss_slot_wall'] = l('boss.slot_wall_m', 'm')
    G['boss_x_end'] = G['xt'] + G['r_t'] + l('boss.tail_m', 'm')
    xs_ = [G['xt'] - G['boss_r_out'] + i * (G['boss_x_end'] - G['xt'] + G['boss_r_out']) / 20 for i in range(21)]
    G['boss_u'] = (G['zu'](G['xt']), max(G['zu'](x) for x in xs_) + G['boss_h'])      # z range of the upper boss
    G['boss_l'] = (min(G['zl'](x) for x in xs_) - G['boss_h'], G['zl'](G['xt']))      # lower boss
    G['bore_len'] = G['boss_u'][1] - G['boss_l'][0]

    # through-core block and tube plug
    G['blk_w'], G['blk_wall'] = l('block.width_m', 'm'), l('block.wall_m', 'm')
    G['blk_x0'] = G['xt'] - G['r_b'] - G['blk_wall']
    G['blk_x1'] = G['xs'] + G['r_bs'] + G['blk_wall']
    G['blk_split'] = l('block.x_split_m', 'm')
    G['blk_z0'], G['blk_z1'] = G['zl'](G['xt']), G['zu'](G['xt'])
    G['bore_web'] = (G['xs'] - G['r_bs']) - (G['xt'] + G['r_b'])
    ov = l('plug.overhang_m', 'm')
    G['plug_z0'], G['plug_z1'] = G['boss_l'][0] - ov, G['boss_u'][1] + ov
    G['plug_od'], G['plug_id'] = l('plug.od_m', 'm'), l('plug.id_m', 'm')

    # brace and anchor (upper right; lower right uses the lower surface)
    G['br_w'], G['br_t'], G['br_engage'] = l('brace.w_m', 'm'), l('brace.t_m', 'm'), l('brace.engage_m', 'm')
    G['an_lx'], G['an_ly'], G['an_proud'] = l('anchor.len_x_m', 'm'), l('anchor.len_y_m', 'm'), l('anchor.proud_m', 'm')
    G['y_anchor'] = l('brace.anchor_y_m', 'm')
    G['an_z_u'] = (G['zs'] + G['r_s'], G['zu'](G['xs']) + G['an_proud'])           # anchor z range, upper
    G['an_z_l'] = (G['zl'](G['xs']) - G['an_proud'], G['zs'] - G['r_s'])           # lower
    G['ear_pt'] = (G['xt'], G['yf'] - G['sc_r_out'] - G['sc_ear_len'] / 2, G['z_sc_mid'])

    def brace_ends(upper):
        za = (G['zu'](G['xs']) + G['an_proud'] / 2) if upper else (G['zl'](G['xs']) - G['an_proud'] / 2)
        e = G['ear_pt']
        return (G['xs'], G['y_anchor'], za), (e[0], e[1], e[2] if upper else -e[2])
    G['brace_ends'] = brace_ends
    a, e = brace_ends(True)
    G['brace_len'] = math.dist(a, e)
    G['brace_len_l'] = math.dist(*brace_ends(False))

    # ESC pad (UR, on the outboard face of FIN-001-RU)
    G['pad_x0'], G['pad_len'], G['pad_hh'] = l('esc_pad.x0_m', 'm'), l('esc_pad.len_m', 'm'), l('esc_pad.h_m', 'm') / 2
    G['pad_z'], G['pad_t'] = l('esc_pad.z_m', 'm'), l('esc_pad.t_m', 'm')
    G['pad_slot'], G['pad_slot_edge'] = l('esc_pad.slot_m', 'm'), l('esc_pad.slot_edge_m', 'm')
    return G


# ----------------------------------------------------------------------------- 2-D loops
def circle(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def keyhole_c(cx, cy, r_in, r_out, slot_hw, wall, x_end, n=20):
    """Clip / collar outline in (x, y): ring r_in..r_out around (cx, cy) with a board slot of half width slot_hw
    opening aft (+x) to x_end, slot walls `wall` thick. One simple closed loop (C shape)."""
    yo = slot_hw + wall
    ao = math.asin(min(yo / r_out, 0.99))
    ai = math.asin(min(slot_hw / r_in, 0.99))
    outer = arc(cx, cy, r_out, ao, 2 * math.pi - ao, n)
    inner = arc(cx, cy, r_in, 2 * math.pi - ai, ai, n)
    return [(x_end, cy + yo)] + outer + [(x_end, cy - yo), (x_end, cy - slot_hw)] + inner + [(x_end, cy + slot_hw)]


def slit_ring(cx, cy, r_in, r_out, slit, ang, n=28):
    """Ring with a radial slit of width `slit` centred on direction `ang` (rad), (x, y) plane."""
    do, di = math.asin(slit / 2 / r_out), math.asin(slit / 2 / r_in)
    return arc(cx, cy, r_out, ang + do, ang + 2 * math.pi - do, n) + arc(cx, cy, r_in, ang + 2 * math.pi - di, ang + di, n)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ----------------------------------------------------------------------------- shapes
def half_fin_loop(G, upper):
    """(x, z) outline, right side. Root on the skin (upper or lower); straight top edge from the station-collar top at
    the LE to the TE tip; the lower half has the elevon inter-panel link slot (CR-A4-04) on the hinge line."""
    s = 1 if upper else -1
    surf = G['zu'] if upper else G['zl']
    xs = [G['x_le'] + (G['te'] - G['x_le']) * i / 24 for i in range(25)]
    a, b = G['x_hinge'] - G['slot_hw'], G['x_hinge'] + G['slot_hw']
    if not upper:
        xs = sorted(set([x for x in xs if not a - 1e-9 < x < b + 1e-9] + [a, b]))
    root = []
    for x in xs:
        if not upper and abs(x - a) < 1e-9:
            root += [(x, surf(x)), (x, surf(x) - G['slot_d'])]
        elif not upper and abs(x - b) < 1e-9:
            root += [(x, surf(x) - G['slot_d']), (x, surf(x))]
        else:
            root.append((x, surf(x)))
    return root + [(G['te'], s * G['h']), (G['x_le'], s * G['z_le_top'])]


def build_half_fin(part, G, upper):
    return part.prism('Y', G['yf'] - G['t_fin'] / 2, [half_fin_loop(G, upper)], G['t_fin'], name='half-fin board')


def build_edge_strip(part, G, outboard):
    """CF strip on one face of the upper-right half-fin, along the top edge from the board LE (inside the station
    collar slot) to the TE tip."""
    y0 = G['yf'] + G['t_fin'] / 2 if outboard else G['yf'] - G['t_fin'] / 2 - G['es_t']
    x0, w = G['x_le'], G['es_w']
    loop = [(x0, G['ztop'](x0) - w), (G['te'], G['h'] - w), (G['te'], G['h']), (x0, G['ztop'](x0))]
    return part.prism('Y', y0, [loop], G['es_t'], name='edge strip')




def build_station_collar(part, G):
    loop = keyhole_c(G['xt'], G['yf'], G['r_b'], G['sc_r_out'], G['sc_slot_hw'], G['sc_slot_wall'], G['sc_x_end'])
    part.prism('Z', G['z_sc0'], [loop], G['sc_h'], name='station collar')
    part.box((G['xt'] - G['sc_ear_w'] / 2, G['yf'] - G['sc_r_out'] - G['sc_ear_len'], G['z_sc0']),
             (G['xt'] + G['sc_ear_w'] / 2, G['yf'] - G['sc_r_out'] + 0.0005, G['z_sc1']), name='brace ear')


def build_brace(part, G, upper):
    """Straight strip w x t between the anchor and the ear, w along x, t normal to the axis in the y-z plane: a ruled
    Y-loft between two (x, z) rectangles (exact)."""
    a, e = G['brace_ends'](upper)
    dy, dz = e[1] - a[1], e[2] - a[2]
    tz = G['br_t'] * math.hypot(dy, dz) / abs(dy)
    secs = [(p[1], rect(p[0] - G['br_w'] / 2, p[2] - tz / 2, p[0] + G['br_w'] / 2, p[2] + tz / 2)) for p in (a, e)]
    return part.loft('Y', secs, smooth=False, name='CF brace')


def build_anchor(part, G, upper):
    z0, z1 = G['an_z_u'] if upper else G['an_z_l']
    return part.box((G['xs'] - G['an_lx'] / 2, G['y_anchor'] - G['an_ly'] / 2, z0),
                    (G['xs'] + G['an_lx'] / 2, G['y_anchor'] + G['an_ly'] / 2, z1), name='brace anchor')


def build_block(part, G):
    w = G['blk_w']
    sock = rect(G['blk_x0'], G['yf'] - w / 2, G['blk_split'], G['yf'] + w / 2)
    part.prism('Z', G['blk_z0'], [sock, circle(G['xt'], G['yf'], G['r_b'], 32)], G['blk_z1'] - G['blk_z0'],
               name='tube socket')
    sad = k9.section_loop(G['coords'], G['c'], (0.0, 0.0), G['blk_split'] / G['c'], G['blk_x1'] / G['c'], n=12)
    part.prism('Y', G['yf'] - w / 2, [sad, circle(G['xs'], G['zs'], G['r_bs'], 32)], w, name='spar saddle')
    loop = keyhole_c(G['xt'], G['yf'], G['r_b'], G['boss_r_out'], G['boss_slot_hw'], G['boss_slot_wall'],
                     G['boss_x_end'])
    for z0, z1 in (G['boss_u'], G['boss_l']):
        part.prism('Z', z0, [loop], z1 - z0, name='bore boss')


def build_mount(part, G):
    """Motor mount UR: slit collar + lip cap on the tube end, pinch-bolt ears outboard, plate with screw holes,
    four canted bearing pads (exact 3 deg face), two cheeks plate -> collar."""
    xt, yf, zm = G['xt'], G['yf'], G['zm']
    slit = G['slit']
    part.prism('Z', G['z_col0'], [slit_ring(xt, yf, G['r_b'], G['col_r'], slit, math.pi / 2)], G['z_cap0'] - G['z_col0'],
               name='collar')
    part.prism('Z', G['z_cap0'], [slit_ring(xt, yf, G['cap_lip_r'], G['col_r'], slit, math.pi / 2)],
               G['z_cap1'] - G['z_cap0'], name='lip cap')
    et, el, eh = G['ear_t'], G['ear_len'], G['ear_h']
    for sx in (-1, 1):
        xa = xt + sx * slit / 2
        part.box((min(xa, xa + sx * et), yf + G['col_r'] - 0.0005, G['z_grip_mid'] - eh / 2),
                 (max(xa, xa + sx * et), yf + G['col_r'] + el, G['z_grip_mid'] + eh / 2), name='pinch ear')
    hy, hz = G['plate_hy'], G['plate_hz']
    holes = [circle(yf + dy, zm + dz, G['screw_hole_r'], 12) for dy, dz in G['holes']] + \
        [circle(yf, zm, G['shaft_hole_r'], 16)]
    part.prism('X', G['x_slab0'], [rect(yf - hy, zm - hz, yf + hy, zm + hz)] + holes, G['plate_t'], name='motor plate')
    pc, ph = G['pad_c'], G['pad_hw']
    for sy in (-1, 1):
        for sz in (-1, 1):
            y0, y1 = yf + sy * pc - ph, yf + sy * pc + ph
            secs = []
            for z in (zm + sz * pc - ph, zm + sz * pc + ph):
                secs.append((z, [(G['face_x_at'](y0 - yf, z - zm), y0), (G['x_slab0'], y0), (G['x_slab0'], y1),
                                 (G['face_x_at'](y1 - yf, z - zm), y1)]))
            part.loft('Z', secs, smooth=False, name='canted pad')
    ct, cy_in, cl = G['cheek_t'], G['cheek_y_in'], G['cheek_len']
    for sy in (-1, 1):
        ya, yb = yf + sy * cy_in, yf + sy * (cy_in + ct)
        part.box((G['x_slab1'], min(ya, yb), G['z_cap0'] - G['ear_h'] / 2), (G['x_slab1'] + cl, max(ya, yb), zm + hz),
                 name='cheek')


def build_esc_pad(part, G):
    y0 = G['yf'] + G['t_fin'] / 2
    x0, x1, z0, z1 = G['pad_x0'], G['pad_x0'] + G['pad_len'], G['pad_z'] - G['pad_hh'], G['pad_z'] + G['pad_hh']
    sx, sz = G['pad_slot']
    xc = (x0 + x1) / 2
    e = G['pad_slot_edge'] + sz / 2
    slots = [rect(xc - sx / 2, zc - sz / 2, xc + sx / 2, zc + sz / 2) for zc in (z0 + e, z1 - e)]
    return part.prism('Y', y0, [rect(x0, z0, x1, z1)] + slots, G['pad_t'], name='ESC pad')


# ----------------------------------------------------------------------------- parts and edges (single source)
BOARD = 'foam board 4.8 mm, paper faced'
PETG = 'PETG (printed)'
CF = 'CF tube 22x20 (bought)'
CFS = 'CF strip, pultruded (bought)'
HNAME = {'RU': 'upper R', 'RD': 'lower R', 'LU': 'upper L', 'LD': 'lower L'}


def part_specs():
    """[(id, name, material, make_or_buy, mass rule)] in build order; masses come from the CAD (make_fins.py)."""
    S = []
    for hf in HALVES:
        S.append(('FIN-001-' + hf, 'Half-fin %s, foam board%s' % (HNAME[hf], ', link slot' if 'D' in hf else ''),
                  BOARD, 'make', 'board'))
    for s in ('R', 'L'):
        S.append(('FIN-002-' + s, 'Motor tube %s, CF 22x20, 324 mm' % s, CF, 'buy', 'tube'))
    for st in STATIONS:
        S.append(('FIN-003-' + st, 'Motor mount %s, 3 deg canted, slip clamp (print %s)'
                  % (st, 'A' if st in ('UR', 'LL') else 'B'), PETG, 'make', 'mount'))
    for s in ('R', 'L'):
        S.append(('FIN-004-' + s, 'Through-core block %s (tube socket + spar saddle)' % s, PETG, 'make', 'block'))
    for s in ('R', 'L'):
        S.append(('FIN-006-' + s, 'Tube plug %s, CF 20x18 x 53 mm inside the tube at the block' % s,
                  'CF tube 20x18 (bought)', 'buy', 'plug'))
    for st in STATIONS:
        S.append(('FIN-007-' + st, 'ESC pad %s on the outboard face of half-fin %s' % (st, HALF[st]), PETG, 'make', 'pad'))
    for st in STATIONS:
        S.append(('FIN-008-' + st, 'Station collar %s (board top + edge strips + brace ear)' % st, PETG, 'make', 'collar'))
    for st in STATIONS:
        S.append(('FIN-009-' + st, 'Brace %s, CF strip 10 x 3' % st, CFS, 'buy', 'brace'))
    for st in STATIONS:
        S.append(('FIN-010-' + st, 'Brace anchor %s on the spar at |y| 0.20' % st, PETG, 'make', 'anchor'))
    for hf in HALVES:
        for f, fn in (('O', 'outboard'), ('I', 'inboard')):
            S.append(('FIN-011-%s%s' % (hf, f), 'Edge strip %s %s face, CF 10 x 1' % (HNAME[hf], fn), CFS, 'buy', 'strip'))
    return S


def _sgn(st):
    return k9.SIGNS[st]


def edge_specs(G):
    """Every edge the fins subsystem declares. reg: 'contact' or 'rigid' (+ at). 'needs' = other-subsystem part ids:
    make_fins.py holds the edge in edges_pending until those parts are declared, and build() registers only the
    edges in interfaces.json."""
    E = []
    n = [0]

    def add(a, b, via, notes, reg='contact', at=None, stack=None, needs=()):
        n[0] += 1
        E.append(dict(id='E-FIN-%02d' % n[0], part_a=a, part_b=b, via=via, notes=notes, reg=reg, at=at,
                      joint_stack=stack, needs=list(needs)))
    for s in ('R', 'L'):
        add('FIN-002-' + s, 'FIN-004-' + s, 'CT-EPOXY', 'tube through the block socket bore (22.3 mm, %.0f mm long with '
            'the bosses), 30 min epoxy, tube scuffed 120 grit' % (G['bore_len'] * 1000))
    for s in ('R', 'L'):
        add('FIN-006-' + s, 'FIN-002-' + s, 'CT-EPOXY', 'plug pushed in from the tube end to z %.3f..%.3f with a rod, '
            'laminating epoxy, before the collars and mounts' % (G['plug_z0'], G['plug_z1']))
    clamp = {'fastener': 'M3x16 SHCS ISO 4762', 'count': 1, 'grade': 'A2-70',
             'hole': '3.4 mm clearance through both pinch ears (outboard side, bolt along x)', 'insert': 'none',
             'engagement_mm': 4.0, 'min_engagement_mm': 3.0, 'washer_nut': 'M3 nyloc ISO 10511 + 2 x M3 washer',
             'torque': 'set by the slip test, not a torque: collar turns on the tube at %.1f N m (%.0f N side load at '
                       'the motor can, luggage scale); bolt snug then 1/8-turn steps (CALC-D3-MOUNT-SLIP)'
                       % (G['slip_torque'], G['slip_force']),
             'tool': '2.5 mm hex key + 5.5 mm wrench', 'access': 'from -x under the motor, prop off',
             'install_order': 6, 'removal_order': 2}
    for st in STATIONS:
        sy, sz = _sgn(st)
        add('FIN-003-' + st, TUBE['R' if sy > 0 else 'L'], 'CT-TUBE-CLAMP',
            'slit collar, %.0f mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the '
            'block or tube is overloaded); paint-pen witness line across collar and tube' % (G['grip'] * 1000),
            reg='rigid', at=(G['xt'], sy * G['yf'], sz * G['z_grip_mid']), stack=dict(clamp))
    for hf in HALVES:
        add('FIN-004-' + hf[0], 'FIN-001-' + hf, 'CT-EPOXY', 'board root LE in the %.1f mm slot of the block %s bore boss, '
            '30 min epoxy' % (2 * G['boss_slot_hw'] * 1000, 'upper' if hf[1] == 'U' else 'lower'))
    for st in STATIONS:
        add('FIN-008-' + st, TUBE['R' if _sgn(st)[0] > 0 else 'L'], 'CT-EPOXY',
            'station collar bonded on the tube directly under the mount, slot aft, ear inboard')
    for st in STATIONS:
        add('FIN-008-' + st, 'FIN-001-' + HALF[st], 'CT-EPOXY', 'board LE top corner in the collar slot, 30 min epoxy')
    for hf in HALVES:
        for f in ('O', 'I'):
            add('FIN-011-%s%s' % (hf, f), 'FIN-001-' + hf, 'CT-EPOXY', 'strip bonded along the board top edge, 30 min '
                'epoxy, paper face scuffed lightly')
    for hf in HALVES:
        st = [k for k, v in HALF.items() if v == hf][0]
        for f in ('O', 'I'):
            add('FIN-011-%s%s' % (hf, f), 'FIN-008-' + st, 'CT-EPOXY', 'strip end %.0f mm inside the station-collar '
                'slot (C4: strips end in the collar)' % ((G['sc_x_end'] - G['x_le']) * 1000))
    for st in STATIONS:
        add('FIN-009-' + st, 'FIN-008-' + st, 'CT-EPOXY', 'brace end %.0f mm in the ear slot (%.1f x %.1f mm), 30 min epoxy' % (G['br_engage'] * 1000, G['br_t'] * 1100, G['br_w'] * 1040))
    for st in STATIONS:
        add('FIN-009-' + st, 'FIN-010-' + st, 'CT-EPOXY', 'brace end %.0f mm in the anchor slot, 30 min epoxy' % (G['br_engage'] * 1000))
    for st in STATIONS:
        add('FIN-007-' + st, 'FIN-001-' + HALF[st], 'CT-EPOXY', 'pad on the outboard board face, 30 min epoxy')
    # ---- edges to other subsystems
    for s in ('R', 'L'):
        add('FIN-004-' + s, 'WNG-002', 'CT-EPOXY',
            'spar through the block spar bore (22.3 mm, %.0f mm long); blocks threaded on the spar and set by jig at '
            'y = +/-%.3f before the spar is bonded into the core (CL-C4-BLOCK-MS)' % (G['blk_w'] * 1000, G['yf']),
            needs=['WNG-002'])
    for s in ('R', 'L'):
        add('FIN-004-' + s, 'WNG-001', 'CT-EPOXY',
            'block bonded into the core cut-out x %.3f-%.3f, y %.3f +/- %.3f, full depth (D1 cuts it); tape skin over'
            % (G['blk_x0'], G['blk_x1'], G['yf'], G['blk_w'] / 2), needs=['WNG-001'])
    for hf in HALVES:
        add('FIN-001-' + hf, 'WNG-001', 'CT-EPOXY',
            'root on bare foam, microballoon-epoxy fillets both sides (12 mm legs), then the skin tape laps 15 mm up both '
            'board faces (L-angle); root contour from the S5010 section (CALC-D3-ROOT)', needs=['WNG-001'])
    for st in STATIONS:
        add('FIN-010-' + st, 'WNG-002', 'CT-EPOXY',
            'anchor foot bonded on the spar %s face through a %.0f x %.0f mm pocket in skin and core at y %+.2f (D1 cuts '
            'it); thickened epoxy fills the saddle' % ('top' if 'U' in st else 'bottom', G['an_lx'] * 1000,
                                                      G['an_ly'] * 1000, _sgn(st)[0] * G['y_anchor']), needs=['WNG-002'])
    motor = {'fastener': 'M3x8 SHCS ISO 4762 (PRP-005, supplied by propulsion)', 'count': 4, 'grade': 'A2-70',
             'hole': '3.4 mm clearance through the %.1f mm plate and the canted pads (stack %.1f-%.1f mm at the holes)'
                     % (G['plate_t'] * 1000, G['stack_min'] * 1000, G['stack_max'] * 1000),
             'insert': 'none (motor base tapped M3, maker pattern; measure on arrival)',
             'engagement_mm': round(G['engage_min'] * 1000, 2), 'min_engagement_mm': 3.0, 'washer_nut': 'none',
             'torque': '0.5 N m + Loctite 243', 'tool': '2.5 mm hex key, short arm',
             'access': 'from +x behind the plate, above the tube end (the board LE corner is below the station collar)',
             'install_order': 7, 'removal_order': 1}
    for st in STATIONS:
        sy, sz = _sgn(st)
        add('PRP-001-' + st, 'FIN-003-' + st, 'CT-M3-SHCS-MOTOR',
            'motor base on four canted pads (3 deg tangential, D-09), face at x %.4f' % G['x_face'],
            reg='rigid', at=(G['x_face'], sy * G['yf'], sz * G['zm']), stack=dict(motor), needs=['PRP-001-' + st])
    for st in STATIONS:
        add('PRP-002-' + st, 'FIN-007-' + st, 'CT-STRAP-VELCRO',
            'ESC on hook-and-loop tape, 10 mm strap through the two pad slots and the board; heat-sink face outboard, '
            'not taped over, long axis along x in the slipstream (CALC-D3-ESC-WASH)', needs=['PRP-002-' + st])
    return E


# ----------------------------------------------------------------------------- build
def _declared_edges(ctx):
    path = os.path.join(ctx.dir or '', 'interfaces.json')
    if not ctx.dir or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return {e['id'] for e in json.load(f).get('edges', [])}


def build(ctx):
    P, LP = ctx.params, ctx.local or load_local()
    coords, _ = k9.section(ctx)
    G = geometry(P, LP, coords)

    build_half_fin(ctx.part('FIN-001-RU'), G, True)
    build_half_fin(ctx.part('FIN-001-RD'), G, False)
    k9.tube_z(ctx.part('FIN-002-R'), G['xt'], G['yf'], G['L_tube'] / 2, G['od'], G['id'])
    build_mount(ctx.part('FIN-003-UR'), G)
    build_block(ctx.part('FIN-004-R'), G)
    ctx.part('FIN-006-R').tube('Z', (G['xt'], G['yf'], G['plug_z0']), G['plug_z1'] - G['plug_z0'], G['plug_od'] / 2,
                               G['plug_id'] / 2, name='tube plug')
    build_esc_pad(ctx.part('FIN-007-UR'), G)
    build_station_collar(ctx.part('FIN-008-UR'), G)
    build_brace(ctx.part('FIN-009-UR'), G, True)
    build_brace(ctx.part('FIN-009-LR'), G, False)
    build_anchor(ctx.part('FIN-010-UR'), G, True)
    build_anchor(ctx.part('FIN-010-LR'), G, False)
    build_edge_strip(ctx.part('FIN-011-RUO'), G, True)
    build_edge_strip(ctx.part('FIN-011-RUI'), G, False)

    ctx.mirror('FIN-007-UR', 'FIN-007-LR', plane='XY')
    ctx.mirror('FIN-008-UR', 'FIN-008-LR', plane='XY')
    ctx.mirror('FIN-011-RUO', 'FIN-011-RDO', plane='XY')
    ctx.mirror('FIN-011-RUI', 'FIN-011-RDI', plane='XY')
    pairs = [('FIN-001-RU', 'FIN-001-LU'), ('FIN-001-RD', 'FIN-001-LD'), ('FIN-002-R', 'FIN-002-L'),
             ('FIN-004-R', 'FIN-004-L'), ('FIN-006-R', 'FIN-006-L')]
    for st in ('UR', 'LR'):
        pairs += [('FIN-%03d-%s' % (k, st), 'FIN-%03d-%sL' % (k, st[0])) for k in (7, 8, 9, 10)]
    for hf in ('RU', 'RD'):
        pairs += [('FIN-011-%s%s' % (hf, f), 'FIN-011-L%s%s' % (hf[1], f)) for f in ('O', 'I')]
    for a, b in pairs:
        k9.pair(ctx, a, b)
    k9.quad(ctx, {'UR': 'FIN-003-UR', 'UL': 'FIN-003-UL', 'LR': 'FIN-003-LR', 'LL': 'FIN-003-LL'})

    declared = _declared_edges(ctx)
    for e in edge_specs(G):
        if declared is not None and e['id'] not in declared:
            continue                                    # pending: the other subsystem has not declared its part yet
        if e['reg'] == 'rigid':
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at=e['at'])
        else:
            ctx.contact(e['id'], e['notes'][:60])
