"""K09-L fins subsystem (FIN), owner D3, design R5 (CR-A1-63; CHANGE-LOG D-26, D-27, D-28, D-42, D-48, D-51, D-52,
D-54, D-61, D-68, D-70). Two fins at y = +/-0.32 m. Each fin = one continuous CF motor tube through the wing core at x 0.045 (0.344 m,
ends at z +/-0.172), an upper and a lower two-layer foam-board half-fin behind it (0.21 m high, D5's stepped 45.4 mm
tip for the foot shoe), a printed PETG through-core block that joins tube, spar and core (with a strap eye on each bore
boss; four vertical plan-form edges rounded R 3 mm, D-68), and per motor station an ASA slip-clamp motor mount with
a 7 deg canted plate (sense per D-52) whose face sits 7.5 mm ahead of the mount collar (D-61, cheeks 17 mm), a 15 mm
PETG station collar with a 40 mm two-face tail (C6 CR-C6-36), a pultruded CF brace from the collar to the spar, two CF edge
strips along the half-fin top edge pinned with 2.5 mm CF pins every 15 mm (D-70), an ASA ESC pad, and microballoon-
epoxy root fillets (CR-C6-24; credited fail-safe only, D-68) modelled as bodies of the half-fin.

    build(ctx)            Fusion / stub module (fusionkit), cruise attitude, aircraft frame (DATUMS.md)
    geometry(P, LP, co)   every derived dimension, shared with make_fins.py and team/D3/fins_calcs.py
    part_specs(G), edge_specs(G)   the part and edge lists make_fins.py writes to interfaces.json

Part ids. Instance suffixes: station codes UR/UL/LR/LL (U/L = upper/lower half, R/L = right/left side) for every part
that exists once per half-fin or motor station; R/L for the per-fin parts; O/I for the outboard/inboard strip face.
FIN-001-<st> half-fins · FIN-002-R/L motor tubes · FIN-003-<st> motor mounts · FIN-004-R/L through-core blocks ·
FIN-006-R/L tube plugs · FIN-007-<st> ESC pads · FIN-008-<st> station collars · FIN-009-<st> braces ·
FIN-010-<st> brace anchors · FIN-011-<st><O|I> edge strips · FIN-012-<st> edge-strip pin sets. FIN-005 is retired.

Fin-tube junction (P25): the tube IS the fin leading edge. The flat 9.6 mm laminate butts the tube and is held by
the slotted bore boss of the block at the root and by the station collar at the top. The collar's tail is a tongue of
board thickness that fills a notch in the board's LE-top corner, with the two edge strips in slots between the tongue
and two outer walls (both strip faces bonded to PETG over 40 mm). Nothing wraps the board around the tube.
Load path: motor -> canted plate -> mount collar (friction clamp, the D-23 fuse) -> tube -> station collar -> brace
(axial) -> anchor -> spar, and tube -> block (socket bore, CF plug inside) -> spar bore -> spar; fin top edge -> CF
edge strips (pinned to the board) -> collar tail -> tube; fin root -> cove fillets (15 mm on the effective root
length, 13 mm aft of the hinge for the elevon end gaps, 4 mm sealing bead ahead of it, none over the D6 link slot on
the lower roots) and tape laps -> core.

Cant (D-27, 7 deg; sense D-52): the motor plate is a slab whose front and back faces are both planes through the motor
point tilted 7 deg about the radial line from the x-axis to the motor, so every motor screw passes the same 4.5 mm stack
and its head bears flat. fin_detail.mount.cant_sense_UR = -1: the UR prop end leans toward the wing plane and
outboard. fusionkit has no rotated bodies inside an axis-aligned part and no holes in lofts, so the slab is a set of
ruled Z-lofts around the openings (square 2.5 mm drill pilots on the nominal pattern, a 10 mm square shaft opening):
exact planes. The brace is a ruled Y-loft between two (x, z) rectangles, exact for a straight strip. The root fillets
are ruled X-lofts of a cove section (equal legs) on the S5010 surface, one station every 10 mm.

UNVERIFIED-IN-FUSION: lofts of the canted plate and braces; the block socket is flat-topped at the local surface
(sand flush); the brace slots in the ear and anchor are where the brace body overlaps them (cut with the brace body as
the tool in Fusion); the pin holes are where the pins overlap strips and board (drilled after cure); C-shaped loops
(slit collar, keyhole bosses) untested in Fusion. Harness provisions (CR-F2-05): an 8 mm lead hole in every
half-fin and 3 x 1.5 mm tie lugs on the boss tails (inboard, slot open along z) and on the collar tails (outboard, at
x 0.060 with the slot open along x for the phase bundle that rises along z, CR-F2-16).
"""
import json
import math
import os

import k09kit as k9

STATIONS = ('UR', 'UL', 'LR', 'LL')
TUBE = {'R': 'FIN-002-R', 'L': 'FIN-002-L'}
SNAME = {'UR': 'upper right', 'UL': 'upper left', 'LR': 'lower right', 'LL': 'lower left'}


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


def side(st):
    return 'R' if k9.SIGNS[st][0] > 0 else 'L'


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
    G['layers'] = v('fins.layers')
    G['L_tube'] = v('fins.tube.length_m', 'm')
    for shared, local in ((G['layers'], l('layers')), (G['L_tube'], l('tube_length_m', 'm'))):
        if abs(shared - local) > 1e-9:
            raise ValueError('fins/params.json copy (%s) disagrees with params.json (%s): update the local copy'
                             % (local, shared))
    G['t_fin'] = v('fins.board_t_m', 'm') * G['layers']
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

    # motor mount (UR): canted plate, uniform thickness
    G['col_r'] = G['r_b'] + l('mount.collar_wall_m', 'm')
    G['x_col_front'] = G['xt'] - G['col_r']
    G['x_face'] = G['x_col_front'] - l('mount.face_ahead_m', 'm')
    G['plate_t'] = l('mount.plate_t_m', 'm')
    tc = math.tan(math.radians(G['cant']))
    G['face_x_at'] = lambda dy, dz, s=G['sense']: G['x_face'] + s * tc * (G['t_hat'][1] * dy + G['t_hat'][2] * dz)
    G['plate_dx'] = G['plate_t'] / math.cos(math.radians(G['cant']))           # back face offset along x
    G['back_x_at'] = lambda dy, dz: G['face_x_at'](dy, dz) + G['plate_dx']
    G['pattern'] = l('mount.bolt_pattern_m', 'm')
    G['holes'] = [(s * G['pattern'][0] / 2, 0.0) for s in (1, -1)] + [(0.0, s * G['pattern'][1] / 2) for s in (1, -1)]
    G['pilot'] = l('mount.pilot_m', 'm')
    G['shaft_open'] = l('mount.shaft_hole_d_m', 'm')
    G['head_d'] = l('mount.head_d_m', 'm')
    G['z_head_low'] = G['zm'] - G['pattern'][1] / 2 - G['head_d'] / 2
    G['z_cap1'] = G['z_head_low'] - l('mount.head_clear_m', 'm')
    G['z_cap0'] = G['z_cap1'] - l('mount.cap_t_m', 'm')
    G['slip'] = G['z_cap0'] - G['z_tube_end']
    G['grip'] = l('mount.grip_m', 'm')
    G['z_col0'] = G['z_tube_end'] - G['grip']
    G['z_grip_mid'] = G['z_tube_end'] - G['grip'] / 2
    G['plate_hy'], G['plate_hz'] = l('mount.plate_half_y_m', 'm'), l('mount.plate_half_z_m', 'm')
    G['x_prop'] = G['x_face'] - l('mount.prop_stack_m', 'm') * math.cos(math.radians(G['cant']))   # hub on the axis
    G['prop_gap'] = G['x_col_front'] - G['x_prop']
    corners = [(sy * G['plate_hy'], sz * G['plate_hz']) for sy in (-1, 1) for sz in (-1, 1)]
    G['plate_x_min'] = min(G['face_x_at'](dy, dz) for dy, dz in corners)
    G['stack_min'] = G['stack_max'] = G['plate_t']                 # along the screw axis, every hole
    G['screw_len'] = l('mount.motor_screw_len_m', 'm')
    G['engage_min'] = G['screw_len'] - G['stack_max']
    G['slit'], G['cap_lip_r'] = l('mount.slit_m', 'm'), l('mount.cap_lip_r_m', 'm')
    G['ear_t'], G['ear_len'], G['ear_h'] = l('mount.ear_t_m', 'm'), l('mount.ear_len_m', 'm'), l('mount.ear_h_m', 'm')
    G['cheek_t'], G['cheek_y_in'], G['cheek_len'] = (l('mount.cheek_t_m', 'm'), l('mount.cheek_y_in_m', 'm'),
                                                     l('mount.cheek_len_m', 'm'))
    G['slip_torque'] = l('mount.slip_torque_nm', 'N m')
    G['slip_lever'] = G['xt'] - (G['x_face'] - v('propulsion.motor_length_m', 'm') / 2)   # tube axis to can middle
    G['slip_force'] = G['slip_torque'] / G['slip_lever']

    # station collar (under the mount): ring + brace ear + two-face tail
    G['sc_h'] = l('station_collar.height_m', 'm')
    G['z_sc1'] = G['z_col0'] - l('station_collar.gap_m', 'm')
    G['z_sc0'] = G['z_sc1'] - G['sc_h']
    G['sc_ear_h'] = l('station_collar.ear_h_m', 'm')
    G['z_ear0'] = G['z_sc1'] - G['sc_ear_h']
    G['z_ear_mid'] = G['z_sc1'] - G['sc_ear_h'] / 2
    G['sc_r_out'] = G['r_b'] + l('station_collar.ring_wall_m', 'm')
    G['es_w'], G['es_t'] = l('edge_strip.w_m', 'm'), l('edge_strip.t_m', 'm')
    G['sc_wall'] = l('station_collar.slot_wall_m', 'm')
    G['sc_clear'] = l('station_collar.strip_slot_clear_m', 'm')
    G['sc_cap'] = l('station_collar.cap_t_m', 'm')
    G['sc_x0'] = G['xt'] + G['r_b']                                  # tail starts inside the ring wall
    G['sc_x_end'] = G['xt'] + G['r_t'] + l('station_collar.tail_m', 'm')
    G['sc_ear_len'], G['sc_ear_w'] = l('station_collar.ear_len_m', 'm'), l('station_collar.ear_w_m', 'm')

    # half-fin: LE on the tube, sloped top edge from the collar top to the step front, D5's flat step to the TE
    G['x_le'] = G['xt'] + G['r_t'] + l('fin.le_gap_m', 'm')
    G['x_sq'] = G['te'] - l('fin.tip_square_m', 'm')
    G['z_step'] = l('fin.tip_step_z_m', 'm')
    G['x_tip_clear'] = l('fin.tip_clear_x_m', 'm')
    if not G['z_sc1'] < G['z_step'] < G['h']:
        raise ValueError('fin tip step |z| %.4f must lie between the collar top %.4f and the half height %.4f'
                         % (G['z_step'], G['z_sc1'], G['h']))
    G['z_le_top'] = G['z_sc1']
    G['slope'] = (G['h'] - G['z_le_top']) / (G['x_sq'] - G['x_le'])
    G['ztop'] = lambda x: min(G['h'], G['z_le_top'] + G['slope'] * (x - G['x_le']))
    G['cos_e'] = 1 / math.hypot(1, G['slope'])
    G['es_wz'] = G['es_w'] / G['cos_e']                              # strip band height measured along z
    G['tongue_d'] = G['es_wz'] + l('station_collar.tongue_depth_m', 'm')   # tail tongue / wall / notch depth along z
    G['tongue_fit'] = G['sc_h'] - G['tongue_d']                     # D-48: the 12 mm collar holds only if >= 0.5 mm
    if G['tongue_fit'] < 0.0005:
        raise ValueError('strip-tail tongue %.2f mm does not fit under the %.1f mm station collar (D-48): keep 16 mm'
                         % (G['tongue_d'] * 1000, G['sc_h'] * 1000))
    G['x_hinge'] = c * k9.hinge_frac(P)
    G['slot_hw'], G['slot_d'] = l('link_slot.half_width_m', 'm'), l('link_slot.depth_m', 'm')
    G['strip_len'] = (G['x_sq'] - G['x_le']) / G['cos_e']
    G['strip_tail_len'] = G['sc_x_end'] - G['x_le']                 # strip length bonded inside the collar tail

    # edge-strip pins (CR-C6-02): along the strip centreline aft of the collar tail, ending before D5's shoe cheeks
    G['pin_r'], G['pin_pitch'] = l('edge_strip.pin_d_m', 'm') / 2, l('edge_strip.pin_pitch_m', 'm')
    G['pin_len'] = G['t_fin'] + 2 * G['es_t']
    dxp = G['pin_pitch'] * G['cos_e']
    xs_ = []
    x = G['sc_x_end'] + dxp / 2
    while x < G['x_sq'] - dxp / 4 and x + G['pin_r'] <= G['x_tip_clear']:     # clear of D5's shoe cheeks
        xs_.append(x)
        x += dxp
    G['pins'] = [(x, G['ztop'](x) - G['es_wz'] / 2) for x in xs_]

    # keyhole bosses on the block (bore extension + board root slot, CR-C4-04)
    G['boss_h'], G['boss_wall'] = l('boss.height_m', 'm'), l('boss.ring_wall_m', 'm')
    G['boss_r_out'] = G['r_b'] + G['boss_wall']
    G['boss_slot_hw'] = G['t_fin'] / 2 + l('boss.slot_clear_m', 'm')
    G['boss_slot_wall'] = l('boss.slot_wall_m', 'm')
    G['boss_x_end'] = G['xt'] + G['r_t'] + l('boss.tail_m', 'm')
    xb = [G['xt'] - G['boss_r_out'] + i * (G['boss_x_end'] - G['xt'] + G['boss_r_out']) / 20 for i in range(21)]
    G['boss_u'] = (G['zu'](G['xt']), max(G['zu'](x) for x in xb) + G['boss_h'])      # z range of the upper boss
    G['boss_l'] = (min(G['zl'](x) for x in xb) - G['boss_h'], G['zl'](G['xt']))      # lower boss
    G['bore_len'] = G['boss_u'][1] - G['boss_l'][0]

    # root fillets (CR-C6-24, CR-D6-04): zones (x0, x1, leg) per half; full leg over eff_len of bonded root from the TE
    rf = lambda k, u='m': l('fin.root_fillet.' + k, u)
    G['fil_leg'], G['fil_aft'], G['fil_fwd'] = rf('leg_m'), rf('leg_aft_m'), rf('leg_fwd_m')
    G['fil_leff'], G['fil_gcc'] = rf('eff_len_m'), rf('gcc', 'g/cm3')
    G['fil_x0'] = G['boss_x_end']                                     # starts behind the bore-boss slot walls
    G['fil_x1'] = G['te'] - 0.002                                     # stops short of the opened TE
    G['slot_x'] = (G['x_hinge'] - G['slot_hw'], G['x_hinge'] + G['slot_hw'])

    def fillet_zones(upper):
        gap = 0.0 if upper or not rf('stop_over_link_slot', '-') else G['slot_x'][1] - G['slot_x'][0]
        x_full = G['te'] - G['fil_leff'] - gap
        if upper:
            return [(G['fil_x0'], x_full, G['fil_fwd']), (x_full, G['x_hinge'], G['fil_leg']),
                    (G['x_hinge'], G['fil_x1'], G['fil_aft'])]
        a, b = G['slot_x']
        return [(G['fil_x0'], x_full, G['fil_fwd']), (x_full, a, G['fil_leg']), (b, G['fil_x1'], G['fil_aft'])]
    G['fillet_zones'] = fillet_zones
    t = G['t_fin']
    for key, up in (('fil_cap_u', True), ('fil_cap_l', False)):     # couple capacity per unit stress (m3), full zones
        G[key] = sum(lg * (t + lg) * (x1 - x0) for x0, x1, lg in fillet_zones(up) if lg > G['fil_fwd'])
    G['fil_bond_u'] = sum(2 * lg * (x1 - x0) for x0, x1, lg in fillet_zones(True)) * 1e6    # skin bond, mm2
    G['fil_bond_l'] = sum(2 * lg * (x1 - x0) for x0, x1, lg in fillet_zones(False)) * 1e6
    G['elevon_gap_aft'] = min(v('wing.elevon.outboard_y_m', 'm')[0] - (G['yf'] + t / 2),
                              (G['yf'] - t / 2) - v('wing.elevon.inboard_y_m', 'm')[1]) - G['fil_aft']

    # strap eye on each boss (CR-H1-08)
    G['eye_len'], G['eye_h'], G['eye_t'] = l('strap_eye.len_m', 'm'), l('strap_eye.h_m', 'm'), l('strap_eye.t_m', 'm')
    G['eye_hole_r'], G['eye_hole_y'] = l('strap_eye.hole_d_m', 'm') / 2, l('strap_eye.hole_y_m', 'm')
    xe = [G['xt'] - G['eye_t'] / 2 + i * G['eye_t'] / 6 for i in range(7)]
    G['eye_zu0'] = max(G['zu'](x) for x in xe)
    G['eye_zl0'] = min(G['zl'](x) for x in xe)

    # through-core block and tube plug
    G['blk_w'], G['blk_wall'] = l('block.width_m', 'm'), l('block.wall_m', 'm')
    G['blk_x0'] = G['xt'] - G['r_b'] - G['blk_wall']
    G['blk_x1'] = G['xs'] + G['r_bs'] + G['blk_wall']
    G['blk_split'] = l('block.x_split_m', 'm')
    G['blk_r'] = l('block.edge_r_m', 'm')                            # D-68 vertical edges
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
    G['ear_pt'] = (G['xt'], G['yf'] - G['sc_r_out'] - G['sc_ear_len'] / 2, G['z_ear_mid'])

    def brace_ends(upper):
        za = (G['zu'](G['xs']) + G['an_proud'] / 2) if upper else (G['zl'](G['xs']) - G['an_proud'] / 2)
        e = G['ear_pt']
        return (G['xs'], G['y_anchor'], za), (e[0], e[1], e[2] if upper else -e[2])
    G['brace_ends'] = brace_ends
    a, e = brace_ends(True)
    G['brace_len'] = math.dist(a, e)
    G['brace_len_l'] = math.dist(*brace_ends(False))

    # ESC pad (UR, on the outboard face of FIN-001-UR)
    G['pad_x0'], G['pad_len'], G['pad_hh'] = l('esc_pad.x0_m', 'm'), l('esc_pad.len_m', 'm'), l('esc_pad.h_m', 'm') / 2
    G['pad_z'], G['pad_t'] = l('esc_pad.z_m', 'm'), l('esc_pad.t_m', 'm')
    G['pad_slot'], G['pad_slot_edge'] = l('esc_pad.slot_m', 'm'), l('esc_pad.slot_edge_m', 'm')

    # harness provisions (CR-F2-05): ESC-lead hole through every half-fin, tie lugs on the boss tail and collar tail
    G['wh_x'], G['wh_r'] = l('wire_hole.x_m', 'm'), l('wire_hole.d_m', 'm') / 2
    G['wh_z'] = G['zu'](G['wh_x']) + l('wire_hole.off_skin_m', 'm')            # upper; lower mirrors on zl
    G['wh_zl'] = G['zl'](G['wh_x']) - l('wire_hole.off_skin_m', 'm')
    G['tl'] = {k: l('tie_lug.' + k, 'm') for k in ('slot_x_m', 'slot_y_m', 'skin_m', 'bar_m', 'post_m', 'embed_m',
                                                    'h_m', 'boss_x_m', 'boss_clear_m', 'collar_x_m', 'collar_drop_m')}
    G['tl_depth'] = G['tl']['skin_m'] + G['tl']['slot_y_m'] + G['tl']['bar_m']    # proud of the face
    G['tl_len'] = G['tl']['slot_x_m'] + 2 * G['tl']['post_m']

    # bond areas (mm2) for the interfaces.json bond blocks
    G['A_collar_tube'] = math.pi * G['od'] * G['sc_h'] * 1e6
    G['A_strip_tail'] = 2 * G['strip_tail_len'] * G['es_w'] * 1e6
    G['A_tongue_board'] = ((G['sc_x_end'] - G['x_le']) / G['cos_e'] + G['tongue_d']) * G['t_fin'] * 1e6
    G['A_plug'] = math.pi * G['plug_od'] * (G['plug_z1'] - G['plug_z0']) * 1e6
    G['A_board_boss'] = 2 * (G['boss_x_end'] - G['x_le']) * G['boss_h'] * 1e6
    G['A_pad'] = G['pad_len'] * 2 * G['pad_hh'] * 1e6
    G['A_pin'] = math.pi * 2 * G['pin_r'] * G['pin_len'] * 1e6
    return G


# ----------------------------------------------------------------------------- 2-D loops
def circle(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def keyhole_c(cx, cy, r_in, r_out, slot_hw, wall, x_end, n=20):
    """Boss outline in (x, y): ring r_in..r_out around (cx, cy) with a board slot of half width slot_hw opening aft
    (+x) to x_end, slot walls `wall` thick. One simple closed loop (C shape)."""
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


def band(x0, x1, top, depth):
    """(x, z) parallelogram under the sloped line z = top(x): depth measured along z."""
    return [(x0, top(x0) - depth), (x1, top(x1) - depth), (x1, top(x1)), (x0, top(x0))]


# ----------------------------------------------------------------------------- shapes
def half_fin_loop(G, upper):
    """(x, z) outline, right side. Root on the skin; LE on the tube up to the collar bottom; notch for the collar
    tongue; sloped top edge to the half height at the step front (x_sq); D5's step cut down to |z| z_step, flat to
    the TE (D-54); TE = wing TE. The lower half has the elevon inter-panel link slot (CR-A4-04) on the hinge line."""
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
    xe = G['sc_x_end']
    xr = G['xt'] + G['sc_r_out'] + (G['x_le'] - G['xt'] - G['r_t'])    # clear of the collar ring by the LE gap
    top = [(G['te'], s * G['z_step']), (G['x_sq'], s * G['z_step']), (G['x_sq'], s * G['h']), (xe, s * G['ztop'](xe)),
           (xe, s * (G['ztop'](xe) - G['tongue_d'])), (xr, s * (G['ztop'](xr) - G['tongue_d'])),
           (xr, s * G['z_sc0']), (G['x_le'], s * G['z_sc0'])]
    return root + top


def build_half_fin(part, G, upper):
    """Laminate with the Ø 8 mm ESC-lead hole (CR-F2-05; drilled after laminating, F2's grommet goes in it)."""
    hole = circle(G['wh_x'], G['wh_z'] if upper else G['wh_zl'], G['wh_r'], 24)
    lam = part.prism('Y', G['yf'] - G['t_fin'] / 2, [half_fin_loop(G, upper), hole], G['t_fin'],
                     name='half-fin laminate (2 boards)')
    build_root_fillets(part, G, upper)
    return lam


FILLET = 'root fillet'


def cove(y_face, d, zb, s, leg, n=6):
    """(y, z) cove section on a face at y_face (fillet side d = +/-1) and a skin at zb (fillet side s = +/-1): corner,
    skin leg, concave quarter arc of radius leg back to the face leg. Area (1 - pi/4) leg^2."""
    cy, cz = y_face + d * leg, zb + s * leg
    pts = [(cy - d * leg * math.sin(math.pi / 2 * i / n), cz - s * leg * math.cos(math.pi / 2 * i / n))
           for i in range(n + 1)]
    return [(y_face, zb)] + pts


def build_root_fillets(part, G, upper):
    """Microballoon-epoxy cove fillets along the root on both laminate faces, on the S5010 surface (bodies of the
    half-fin part; make_fins.py weighs them at fin.root_fillet.gcc). Zones from geometry()['fillet_zones']."""
    surf, s = (G['zu'], 1) if upper else (G['zl'], -1)
    for x0, x1, leg in G['fillet_zones'](upper):
        if x1 - x0 < 1e-4:
            continue
        n = max(1, int(math.ceil((x1 - x0) / 0.010)))
        xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
        for d in (1, -1):
            yF = G['yf'] + d * G['t_fin'] / 2
            part.loft('X', [(x, cove(yF, d, surf(x), s, leg)) for x in xs], smooth=False, name=FILLET)


def tie_lug(part, G, xc, y_face, out, z0, name):
    """Cable-tie bridge on a face normal to y at y_face, standing out in direction out (+1/-1): posts and an outer
    bar around a 3 x 1.5 mm slot open at both z ends. One printed body with the part (sunk embed_m into the face)."""
    t = G['tl']
    ya, yb = y_face - out * t['embed_m'], y_face + out * G['tl_depth']
    ys0, ys1 = y_face + out * t['skin_m'], y_face + out * (t['skin_m'] + t['slot_y_m'])
    outer = rect(xc - G['tl_len'] / 2, min(ya, yb), xc + G['tl_len'] / 2, max(ya, yb))
    slot = rect(xc - t['slot_x_m'] / 2, min(ys0, ys1), xc + t['slot_x_m'] / 2, max(ys0, ys1))
    return part.prism('Z', z0, [outer, slot], t['h_m'], name=name)


def tie_lug_x(part, G, xc, y_face, out, z_top, name):
    """Cable-tie bridge whose slot is open along x (the tie passes along x round a bundle running along z, CR-F2-16):
    a prism along x, h_m long, with the 3 x 1.5 mm slot in its (y, z) section; posts above and below the slot."""
    t = G['tl']
    ya, yb = y_face - out * t['embed_m'], y_face + out * G['tl_depth']
    ys0, ys1 = y_face + out * t['skin_m'], y_face + out * (t['skin_m'] + t['slot_y_m'])
    zc = z_top - G['tl_len'] / 2
    outer = rect(min(ya, yb), zc - G['tl_len'] / 2, max(ya, yb), zc + G['tl_len'] / 2)
    slot = rect(min(ys0, ys1), zc - t['slot_x_m'] / 2, max(ys0, ys1), zc + t['slot_x_m'] / 2)
    return part.prism('X', xc - t['h_m'] / 2, [outer, slot], t['h_m'], name=name)


def build_edge_strip(part, G, outboard):
    """Straight CF strip on one face of the upper-right half-fin along the sloped top edge, from the board LE (inside
    the collar tail) to the step front (x_sq, D-54)."""
    y0 = G['yf'] + G['t_fin'] / 2 if outboard else G['yf'] - G['t_fin'] / 2 - G['es_t']
    return part.prism('Y', y0, [band(G['x_le'], G['x_sq'], G['ztop'], G['es_wz'])], G['es_t'], name='edge strip')


def build_pins(part, G):
    """Pin set of the upper-right half-fin: 2.5 mm CF rods (D-70) through strip-board-strip (drilled after cure)."""
    y0 = G['yf'] - G['pin_len'] / 2
    for x, z in G['pins']:
        part.cylinder('Y', (x, y0, z), G['pin_len'], G['pin_r'], name='CF pin')


def build_station_collar(part, G):
    """Ring on the tube (15 mm, CR-C6-36), brace ear inboard (top 12 mm), and the two-face tail: tongue (board thickness) in the
    board notch, two outer walls, strip slots between, cap over the top edge; slots open downward."""
    xt, yf = G['xt'], G['yf']
    part.prism('Z', G['z_sc0'], [circle(xt, yf, G['sc_r_out'], 36), circle(xt, yf, G['r_b'], 36)], G['sc_h'],
               name='collar ring')
    part.box((xt - G['sc_ear_w'] / 2, yf - G['sc_r_out'] - G['sc_ear_len'], G['z_ear0']),
             (xt + G['sc_ear_w'] / 2, yf - G['sc_r_out'] + 0.0005, G['z_sc1']), name='brace ear')
    x0, x1, top = G['sc_x0'], G['sc_x_end'], G['ztop']
    tf = G['t_fin'] / 2
    part.prism('Y', yf - tf, [band(x0, x1, top, G['tongue_d'])], G['t_fin'], name='tail tongue')
    yw = tf + G['es_t'] + 2 * G['sc_clear']                         # inner face of each outer wall
    wall_d = G['tongue_d']
    for sgn in (1, -1):
        y_in = yf + sgn * yw
        part.prism('Y', min(y_in, y_in + sgn * G['sc_wall']), [band(x0, x1, top, wall_d)], G['sc_wall'],
                   name='tail wall')
    xc = G['xt'] + G['col_r'] + G['sc_clear'] * 2.5                 # cap starts aft of the mount collar (0.5 mm)
    cap = [(xc, top(xc)), (x1, top(x1)), (x1, top(x1) + G['sc_cap']), (xc, top(xc) + G['sc_cap'])]
    part.prism('Y', yf - yw - G['sc_wall'], [cap], 2 * (yw + G['sc_wall']), name='tail cap')
    # phase-lead tie lug on the outboard wall (E-HRN-06...09; R5 CR-F2-16: x 0.060, slot open along x); top
    # collar_drop below the tail top edge at the lug front
    xl = G['tl']['collar_x_m']
    zt = top(xl - G['tl']['h_m'] / 2) - G['tl']['collar_drop_m']
    tie_lug_x(part, G, xl, yf + yw + G['sc_wall'], 1, zt, 'phase tie lug')


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
    """Through-core block. R5 (D-68, CR-C2-11): the four vertical plan-form edges are rounded R edge_r (front corners of
    the tube socket, aft corners of the spar saddle) so the core pocket corners can be cut R 3 mm to match. The
    saddle's aft strip x1 - r .. x1 is a narrower airfoil slab plus two quarter-round Z-prisms between the highest
    lower and lowest upper surface over that 3 mm (S5010 near max thickness: < 0.05 mm from the true contour; sand
    flush)."""
    w, r = G['blk_w'], G['blk_r']
    xt, yf = G['xt'], G['yf']
    x0, x1, xp = G['blk_x0'], G['blk_x1'], G['blk_split']
    sock = ([(xp, yf - w / 2), (xp, yf + w / 2)] + arc(x0 + r, yf + w / 2 - r, r, math.pi / 2, math.pi, 6)
            + arc(x0 + r, yf - w / 2 + r, r, math.pi, 1.5 * math.pi, 6))
    part.prism('Z', G['blk_z0'], [sock, circle(xt, yf, G['r_b'], 32)], G['blk_z1'] - G['blk_z0'], name='tube socket')
    xa = x1 - r
    sad = k9.section_loop(G['coords'], G['c'], (0.0, 0.0), xp / G['c'], xa / G['c'], n=12)
    part.prism('Y', yf - w / 2, [sad, circle(G['xs'], G['zs'], G['r_bs'], 32)], w, name='spar saddle')
    aft = k9.section_loop(G['coords'], G['c'], (0.0, 0.0), xa / G['c'], x1 / G['c'], n=4)
    part.prism('Y', yf - w / 2 + r, [aft], w - 2 * r, name='spar saddle aft')
    xq = [xa + r * i / 6 for i in range(7)]
    zq0, zq1 = max(G['zl'](x) for x in xq), min(G['zu'](x) for x in xq)
    for sy in (1, -1):
        yc = yf + sy * (w / 2 - r)
        q = [(xa, yc)] + arc(xa, yc, r, 0.0, sy * math.pi / 2, 6)
        part.prism('Z', zq0, [q], zq1 - zq0, name='saddle edge round')
    loop = keyhole_c(xt, yf, G['r_b'], G['boss_r_out'], G['boss_slot_hw'], G['boss_slot_wall'], G['boss_x_end'])
    for z0, z1 in (G['boss_u'], G['boss_l']):
        part.prism('Z', z0, [loop], z1 - z0, name='bore boss')
    # strap eyes (CR-H1-08), outboard, hole along x
    y0, y1 = yf + G['boss_r_out'] - 0.001, yf + G['boss_r_out'] + G['eye_len']
    yh = yf + G['boss_r_out'] + G['eye_hole_y']
    for z0 in (G['eye_zu0'], G['eye_zl0'] - G['eye_h']):
        zc = z0 + G['eye_h'] / 2
        part.prism('X', xt - G['eye_t'] / 2, [rect(y0, z0, y1, z0 + G['eye_h']), circle(yh, zc, G['eye_hole_r'], 16)],
                   G['eye_t'], name='strap eye')
    # ESC-lead tie lugs on the inboard face of the boss-tail slot wall, upper and lower boss (E-HRN-03/05, CR-F2-05)
    t, xl = G['tl'], G['tl']['boss_x_m']
    y_in = yf - G['boss_slot_hw'] - G['boss_slot_wall']
    zs_u = max(G['zu'](xl + d * G['tl_len'] / 2) for d in (-1, 1)) + t['boss_clear_m']
    zs_l = min(G['zl'](xl + d * G['tl_len'] / 2) for d in (-1, 1)) - t['boss_clear_m']
    tie_lug(part, G, xl, y_in, -1, zs_u, 'lead tie lug (upper)')
    tie_lug(part, G, xl, y_in, -1, zs_l - t['h_m'], 'lead tie lug (lower)')


def plate_cells(G):
    """Rectangular (dy, dz) cells covering the plate minus the square openings (pilots + shaft opening)."""
    hy, hz = G['plate_hy'], G['plate_hz']
    opens = [(dy - G['pilot'] / 2, dz - G['pilot'] / 2, dy + G['pilot'] / 2, dz + G['pilot'] / 2) for dy, dz in G['holes']]
    so = G['shaft_open'] / 2
    opens.append((-so, -so, so, so))
    zc = sorted(set([-hz, hz] + [o[1] for o in opens] + [o[3] for o in opens]))
    cells = []
    for z0, z1 in zip(zc, zc[1:]):
        blk = sorted((o[0], o[2]) for o in opens if o[1] < (z0 + z1) / 2 < o[3])
        y = -hy
        for a, b in blk + [(hy, hy)]:
            if a > y + 1e-9:
                cells.append((y, z0, a, z1))
            y = max(y, b)
    return cells


def build_mount(part, G):
    """Motor mount UR (ASA): slit collar + lip cap on the tube end, pinch-bolt ears outboard, a canted plate of uniform
    thickness (front and back faces on the 7 deg plane, exact ruled lofts), two cheeks plate -> collar."""
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
    F, B = G['face_x_at'], G['back_x_at']
    for y0, z0, y1, z1 in plate_cells(G):
        secs = []
        for z in (z0, z1):
            secs.append((zm + z, [(F(y0, z), yf + y0), (B(y0, z), yf + y0), (B(y1, z), yf + y1), (F(y1, z), yf + y1)]))
        part.loft('Z', secs, smooth=False, name='canted plate')
    ct, cy_in, cl = G['cheek_t'], G['cheek_y_in'], G['cheek_len']
    zc0, zc1 = G['z_cap0'] - G['ear_h'] / 2, zm + G['plate_hz']
    for sy in (-1, 1):
        ya, yb = sy * cy_in, sy * (cy_in + ct)
        bx = [B(y, z - zm) for y in (ya, yb) for z in (zc0, zc1)]
        part.box((min(bx) - 0.0005, yf + min(ya, yb), zc0), (max(bx) + cl, yf + max(ya, yb), zc1), name='cheek')


def build_esc_pad(part, G):
    y0 = G['yf'] + G['t_fin'] / 2
    x0, x1, z0, z1 = G['pad_x0'], G['pad_x0'] + G['pad_len'], G['pad_z'] - G['pad_hh'], G['pad_z'] + G['pad_hh']
    sx, sz = G['pad_slot']
    xc = (x0 + x1) / 2
    e = G['pad_slot_edge'] + sz / 2
    slots = [rect(xc - sx / 2, zc - sz / 2, xc + sx / 2, zc + sz / 2) for zc in (z0 + e, z1 - e)]
    return part.prism('Y', y0, [rect(x0, z0, x1, z1)] + slots, G['pad_t'], name='ESC pad')


# ----------------------------------------------------------------------------- parts and edges (single source)
BOARD = 'foam board 4.8 mm x 2, paper faced, laminated'
PETG = 'PETG (printed)'
ASA = 'ASA (printed)'
CF = 'CF tube 22x20 (bought)'
CFS = 'CF strip, pultruded (bought)'
CFR = 'CF rod 2.5 mm, pultruded (bought)'


def part_specs(G=None):
    """[(id, name, material, make_or_buy, mass rule)] in build order; masses come from the CAD (make_fins.py)."""
    L = '%.0f mm' % (G['L_tube'] * 1000) if G else '344 mm'
    S = []
    for st in STATIONS:
        S.append(('FIN-001-' + st, 'Half-fin %s, two-layer foam board, stepped %.1f mm tip, 8 mm lead hole, root fillets%s'
                  % (SNAME[st], (G['te'] - G['x_sq']) * 1000 if G else 45.4, ', link slot' if st[0] == 'L' else ''), BOARD, 'make', 'board'))
    for s in ('R', 'L'):
        S.append(('FIN-002-' + s, 'Motor tube %s, CF 22x20 x %s' % (s, L), CF, 'buy', 'tube'))
    for st in STATIONS:
        S.append(('FIN-003-' + st, 'Motor mount %s, ASA, 7 deg canted plate, slip clamp (print %s)'
                  % (st, 'A' if st in ('UR', 'LL') else 'B'), ASA, 'make', 'mount'))
    for s in ('R', 'L'):
        S.append(('FIN-004-' + s, 'Through-core block %s (tube socket + spar saddle + 2 strap eyes + 2 tie lugs)' % s, PETG, 'make',
                  'block'))
    for s in ('R', 'L'):
        S.append(('FIN-006-' + s, 'Tube plug %s, CF 20x18 x 53 mm inside the tube at the block' % s,
                  'CF tube 20x18 (bought)', 'buy', 'plug'))
    for st in STATIONS:
        S.append(('FIN-007-' + st, 'ESC pad %s, ASA, on the outboard face of half-fin %s' % (st, st), ASA, 'make', 'pad'))
    for st in STATIONS:
        S.append(('FIN-008-' + st, 'Station collar %s, %.0f mm, 40 mm two-face tail + brace ear + tie lug' % (st, G['sc_h'] * 1000 if G else 12), PETG, 'make',
                  'collar'))
    for st in STATIONS:
        S.append(('FIN-009-' + st, 'Brace %s, CF strip 10 x %.0f' % (st, G['br_t'] * 1000 if G else 2), CFS, 'buy', 'brace'))
    for st in STATIONS:
        S.append(('FIN-010-' + st, 'Brace anchor %s on the spar at |y| 0.242' % st, PETG, 'make', 'anchor'))
    for st in STATIONS:
        for f, fn in (('O', 'outboard'), ('I', 'inboard')):
            S.append(('FIN-011-%s%s' % (st, f), 'Edge strip %s %s face, CF 10 x 1' % (SNAME[st], fn), CFS, 'buy', 'strip'))
    n = len(G['pins']) if G else 0
    for st in STATIONS:
        S.append(('FIN-012-' + st, 'Edge-strip pin set %s, %d x CF rod %.1f mm' % (st, n, 2000 * G['pin_r'] if G else 2.5),
                  CFR, 'buy', 'pins'))
    return S


EPOXY = '30 min laminating epoxy + ~5 % colloidal silica (non-sag)'
EPOXY_FOAM = '30 min laminating epoxy + glass microballoons (foam-safe; no CA, no solvent glue on XPS)'
PREP = 'PETG/ASA sanded 120 grit, IPA wipe; CF sanded 120 grit to matte, IPA wipe, gloves'
CURE = '24 h at >= 18 degC before load; parts within 50 mm of a motor: + 4 h at 50 degC post-cure (CR-C6-04)'


def bond(area, load, case, by, adhesive=EPOXY, prep=PREP):
    return {'adhesive': adhesive, 'area_mm2': int(round(area)), 'prep': prep, 'cure': CURE, 'load_n': load,
            'load_case': case, 'sized_by': by}


def edge_specs(G):
    """Every edge the fins subsystem declares. reg: 'contact' or 'rigid' (+ at). 'needs' = other-subsystem part ids:
    make_fins.py holds the edge in edges_pending until those parts are declared, and build() registers only the
    edges in interfaces.json. 'blocks' = A4 data blocks (bond / clamp / retention); make_fins.py takes C6's block
    for the same id from team/C6/joint_stacks.json where C6 sized it and keeps the D3 geometry (area) where R3
    changed it. Ids E-FIN-01...68 are fixed (A4 register); new edges are appended."""
    E = []
    n = [0]

    def add(a, b, via, notes, reg='contact', at=None, stack=None, needs=(), blocks=None, geo=()):
        n[0] += 1
        E.append(dict(id='E-FIN-%02d' % n[0], part_a=a, part_b=b, via=via, notes=notes, reg=reg, at=at,
                      joint_stack=stack, needs=list(needs), blocks=blocks or {}, geo=list(geo)))
    for s in ('R', 'L'):                                                                     # 01-02
        add('FIN-002-' + s, 'FIN-004-' + s, 'CT-EPOXY', 'tube through the block socket bore (22.3 mm, %.0f mm long with '
            'the bosses), 30 min epoxy, tube scuffed 120 grit' % (G['bore_len'] * 1000),
            blocks={'bond': bond(math.pi * G['od'] * G['bore_len'] * 1e6, 'see C6', 'L4 corner', 'C6')})
    for s in ('R', 'L'):                                                                     # 03-04
        add('FIN-006-' + s, 'FIN-002-' + s, 'CT-EPOXY', 'plug pushed in from the tube end to z %.3f..%.3f with a rod, '
            'laminating epoxy, before the collars and mounts' % (G['plug_z0'], G['plug_z1']),
            blocks={'bond': bond(G['A_plug'], 'internal doubler: block bearing 5.3 MPa on the plug (CL-C2-PLUG-BEARING)',
                                 'L4 corner', 'C2, D3')})
    clamp = {'fastener': 'M3x16 SHCS ISO 4762 (FIN-101)', 'count': 1, 'grade': 'A2-70',
             'hole': '3.4 mm clearance through both pinch ears (outboard side, bolt along x)', 'insert': 'none',
             'engagement_mm': 5.5, 'min_engagement_mm': 5.0,
             'washer_nut': 'M3 nyloc ISO 10511 + 2 x M3 washer ISO 7089 (nyloc reused <= 3 times)',
             'torque': 'set by T-D3-SLIP, not a torque: collar turns on the tube at %.1f N m (%.0f N side load at the '
                       'motor can, luggage scale); expect ~0.14 N m, never above 0.4 N m; no threadlocker'
                       % (G['slip_torque'], G['slip_force']),
             'tool': '2.5 mm hex key + 5.5 mm spanner', 'access': 'outboard side, bolt along x, prop off',
             'install_order': 4, 'removal_order': 2}
    for st in STATIONS:                                                                      # 05-08
        sy, sz = k9.SIGNS[st]
        add('FIN-003-' + st, TUBE[side(st)], 'CT-TUBE-CLAMP',
            'ASA slit collar, %.0f mm grip, lip cap on the tube end; friction is the D-23 fuse (turns before the '
            'block or tube is overloaded); paint-pen witness line across collar and tube' % (G['grip'] * 1000),
            reg='rigid', at=(G['xt'], sy * G['yf'], sz * G['z_grip_mid']), stack=dict(clamp),
            blocks={'clamp': {'bore_mm': round(2 * G['r_b'] * 1000, 1), 'part_od_mm': round(G['od'] * 1000, 1),
                              'slip_load_n': round(G['slip_force']), 'sized_by': 'D3 (fuse), C6 (stack)'}})
    for st in STATIONS:                                                                      # 09-12
        add('FIN-004-' + side(st), 'FIN-001-' + st, 'CT-EPOXY',
            'laminate root LE in the %.1f mm slot of the block %s bore boss, 30 min epoxy'
            % (2 * G['boss_slot_hw'] * 1000, 'upper' if st[0] == 'U' else 'lower'),
            blocks={'bond': bond(G['A_board_boss'], 'secondary: locates the root LE; the root fillets carry the board',
                                 'L4 side load', 'D3')})
    for st in STATIONS:                                                                      # 13-16
        add('FIN-008-' + st, TUBE[side(st)], 'CT-EPOXY',
            'station collar ring %.0f mm bonded on the tube directly under the mount, tail aft, ear inboard'
            % (G['sc_h'] * 1000), blocks={'bond': bond(G['A_collar_tube'], 'see C6', 'L4 corner', 'C6')},
            geo=['area_mm2'])
    for st in STATIONS:                                                                      # 17-20
        add('FIN-008-' + st, 'FIN-001-' + st, 'CT-EPOXY',
            'collar tongue (board thickness) in the notch at the laminate LE-top corner, butt-bonded on the notch '
            'bottom and aft edges; the strips cover both faces',
            blocks={'bond': bond(G['A_tongue_board'], 'secondary: the strips carry the top-edge force into the tail',
                                 'L4', 'D3', prep='PETG sanded 120 grit; board edge scuffed')})
    for st in STATIONS:                                                                      # 21-28
        for f in ('O', 'I'):
            add('FIN-011-%s%s' % (st, f), 'FIN-001-' + st, 'CT-EPOXY',
                'strip bonded along the sloped top edge (%.0f mm), 30 min epoxy, paper scuffed 220 grit; pinned with '
                'FIN-012-%s after cure' % (G['strip_len'] * 1000, st),
                blocks={'bond': bond(G['strip_len'] * G['es_w'] * 1e6, 'see C6', 'L4', 'C6',
                                     prep='strip 120 grit + IPA; paper scuffed 220 grit')}, geo=['area_mm2'])
    for st in STATIONS:                                                                      # 29-36
        for f in ('O', 'I'):
            add('FIN-011-%s%s' % (st, f), 'FIN-008-' + st, 'CT-EPOXY',
                'strip forward end %.0f mm in the collar-tail slot between the tongue and the outer wall, both strip '
                'faces bonded to PETG (CR-C6-01)' % (G['strip_tail_len'] * 1000),
                blocks={'bond': bond(G['A_strip_tail'], 'see C6', 'L4', 'C6')}, geo=['area_mm2'])
    for st in STATIONS:                                                                      # 37-40
        add('FIN-009-' + st, 'FIN-008-' + st, 'CT-EPOXY', 'brace end %.0f mm in the ear slot (%.1f x %.1f mm), 30 min '
            'epoxy' % (G['br_engage'] * 1000, G['br_t'] * 1100, G['br_w'] * 1040),
            blocks={'bond': bond(2 * (G['br_w'] + G['br_t']) * G['br_engage'] * 1e6, 'see C6', 'G2', 'C6')})
    for st in STATIONS:                                                                      # 41-44
        add('FIN-009-' + st, 'FIN-010-' + st, 'CT-EPOXY', 'brace end %.0f mm in the anchor slot, 30 min epoxy'
            % (G['br_engage'] * 1000),
            blocks={'bond': bond(2 * (G['br_w'] + G['br_t']) * G['br_engage'] * 1e6, 'see C6', 'G2', 'C6')})
    for st in STATIONS:                                                                      # 45-48
        add('FIN-007-' + st, 'FIN-001-' + st, 'CT-EPOXY', 'ASA pad on the outboard laminate face, 30 min epoxy',
            blocks={'bond': bond(G['A_pad'], 'ESC ~28 g x 10 g vibration = 2.7 N', 'vibration', 'D3',
                                 prep='ASA sanded 120 grit, IPA; paper scuffed 220 grit')})
    # ---- edges to other subsystems
    for s in ('R', 'L'):                                                                     # 49-50
        add('FIN-004-' + s, 'WNG-002', 'CT-EPOXY',
            'spar through the block spar bore (22.3 mm, %.0f mm long, C2 plug inside the spar); blocks threaded on the '
            'spar and set by jig at y = +/-%.3f before the spar is bonded into the core (CL-C4-D3-BLOCK-MS)'
            % (G['blk_w'] * 1000, G['yf']), needs=['WNG-002'],
            blocks={'bond': bond(math.pi * 2 * G['r_s'] * G['blk_w'] * 1e6, 'see C6', 'L4 corner', 'C4, C6')})
    for s in ('R', 'L'):                                                                     # 51-52
        add('FIN-004-' + s, 'WNG-001', 'CT-EPOXY',
            'block bonded into the core cut-out x %.3f-%.3f, y %.3f +/- %.3f, full depth, vertical corners R %.0f mm to '
            'the block (D1 cuts it, D-68); microballoon fillet bead >= 3 mm along the inboard and outboard pocket edges '
            'on both surfaces; 60 mm tape doubler continuous over the edges'
            % (G['blk_x0'], G['blk_x1'], G['yf'], G['blk_w'] / 2, G['blk_r'] * 1000), needs=['WNG-001'],
            blocks={'bond': bond(6500, 'secondary: spar carries the block', '-', 'C4', adhesive=EPOXY_FOAM,
                                 prep='foam dusted off')})
    for st in STATIONS:                                                                      # 53-56
        up = st[0] == 'U'
        z = G['fillet_zones'](up)
        stop = '' if up else '; NO fillet over the link slot x %.4f-%.4f (both faces, CR-D6-04)' % G['slot_x']
        add('FIN-001-' + st, 'WNG-001', 'CT-EPOXY',
            'laminate root on bare foam; microballoon-epoxy cove fillets both faces (CR-C6-24): %.0f mm legs x %.4f-%.4f, '
            '%.0f mm legs aft of the hinge to the TE (elevon end gap), %.0f mm sealing bead x %.4f-%.4f%s; then the '
            'skin tape laps 15 mm up both faces; root contour from the S5010 section'
            % (z[1][2] * 1000, z[1][0], z[1][1], z[2][2] * 1000, z[0][2] * 1000, z[0][0], z[0][1], stop),
            needs=['WNG-001'],
            blocks={'bond': bond(G['fil_bond_u'] if up else G['fil_bond_l'], 'see C6', 'L4 side load', 'D3, C6',
                                 adhesive=EPOXY_FOAM, prep='foam dusted off; board edge scuffed')}, geo=['area_mm2'])
    for st in STATIONS:                                                                      # 57-60
        add('FIN-010-' + st, 'WNG-002', 'CT-EPOXY',
            'anchor foot bonded on the spar %s face through a %.0f x %.0f mm pocket in skin and core at y %+.3f (D1 '
            'cuts it, C2 plug inside the spar); thickened epoxy fills the saddle'
            % ('top' if st[0] == 'U' else 'bottom', G['an_lx'] * 1000, G['an_ly'] * 1000,
               k9.SIGNS[st][0] * G['y_anchor']), needs=['WNG-002'],
            blocks={'bond': bond(G['an_lx'] * G['an_ly'] * 1e6, 'see C6', 'G2', 'C6')})
    motor = {'fastener': 'M3x8 SHCS ISO 4762 (PRP-005, supplied by propulsion)', 'count': 4, 'grade': 'A2-70',
             'hole': '3.4 mm DRILLED through the %.1f mm canted ASA plate to the measured motor pattern (printed '
                     '%.1f mm square pilots on the nominal %.0f x %.0f mm cross), drill square to the canted face, '
                     'motor as template; no radial slots (CR-C6-10)'
                     % (G['plate_t'] * 1000, G['pilot'] * 1000, G['pattern'][0] * 1000, G['pattern'][1] * 1000),
             'insert': 'none (motor base tapped M3)',
             'engagement_mm': round(G['engage_min'] * 1000, 2), 'min_engagement_mm': 3.0,
             'max_engagement_mm': 'probed hole depth - 0.5 (T-E1-MOTOR-RM)',
             'washer_nut': 'none (head bears flat on the canted back face)',
             'torque': '0.20 N m (4 N on a luggage scale 50 mm out on the key) + Loctite 243 on the screw tip only',
             'tool': '2.5 mm hex key + luggage scale',
             'access': 'from behind the plate (+x), above the tube end, between the cheeks',
             'install_order': 3, 'removal_order': 1}
    for st in STATIONS:                                                                      # 61-64
        sy, sz = k9.SIGNS[st]
        add('PRP-001-' + st, 'FIN-003-' + st, 'CT-M3-SHCS-MOTOR',
            'motor base on the 7 deg canted ASA plate (tangential cant, D-27), face at x %.4f on the axis'
            % G['x_face'], reg='rigid', at=(G['x_face'], sy * G['yf'], sz * G['zm']), stack=dict(motor),
            needs=['PRP-001-' + st])
    for st in STATIONS:                                                                      # 65-68
        add('PRP-002-' + st, 'FIN-007-' + st, 'CT-STRAP-VELCRO',
            'ESC on hook-and-loop tape, ONE 10 mm strap through the two pad slots and the laminate; FET side out, '
            'heat-shrink not taped over, long axis along x in the slipstream (CR-E3-02)', needs=['PRP-002-' + st],
            blocks={'retention': {'item': 'FIN-104 10 mm hook-and-loop strap + 25 x 40 mm tape', 'count': 1,
                                  'load_n': 'ESC ~28 g x 10 g = 2.7 N', 'inspection': 'tug test before every flight'}})
    # ---- R3 / R4 additions (appended; ids above are fixed)
    np_ = len(G['pins'])
    for st in STATIONS:                                                                      # 69-72
        add('FIN-012-' + st, 'FIN-001-' + st, 'CT-EPOXY',
            '%d pins %.1f mm drilled (%.1f mm drill) through strip-laminate-strip every %.0f mm along the strip after the '
            'strips cure, epoxy injected before the pin, sanded flush (CR-C6-02, D-70)'
            % (np_, 2000 * G['pin_r'], 2000 * G['pin_r'], G['pin_pitch'] * 1000),
            blocks={'bond': bond(np_ * G['A_pin'], '72.7 N per pin design (C4 R4 frozen set); RF 1.59 at 2.5 mm '
                                 '(CL-C6-STRIP-PIN-RF-PROP, D-70)', 'L4', 'C6')})
    for st in STATIONS:                                                                      # 73-80
        for f in ('O', 'I'):
            add('FIN-012-' + st, 'FIN-011-%s%s' % (st, f), 'CT-EPOXY',
                'pins through the %s strip: carry the strip shear flow into the laminate (CR-C6-02)'
                % ('outboard' if f == 'O' else 'inboard'),
                blocks={'bond': bond(np_ * math.pi * 2 * G['pin_r'] * G['es_t'] * 1e6,
                                     '72.7 N per pin design; bearing on the strip RF 3.44, net section 2.40 '
                                     '(CL-C6-STRIP-NET-PIN-RF, D-70)', 'L4', 'C6')})
    # R4 thermal edges (CR-A4-22a / CR-A4-40, E3 CR-E3-11): make_fins.py fills t_design_c and heat_w from E3's claims
    for st in STATIONS:                                                                      # 81-84
        add('PRP-001-' + st, 'FIN-003-' + st, 'CT-THERMAL-CONTACT',
            'motor base on the canted ASA plate: dry contact on four ~4 x 4 mm pads around the screw holes; the mount is '
            'not a cooling path (printed ASA k ~0.2 W/m K), E3 takes the base at the motor-node temperature',
            needs=['PRP-001-' + st],
            blocks={'thermal': {'heat_w': 'E3', 't_max_c': 83, 't_ambient_c': 30,
                                'path': 'motor -> own prop wash over the bell + internal ventilation; base -> ASA plate '
                                        '(four 4 x 4 mm pads) not credited; plate limit = ASA HDT 93 - 10 K (D-42)',
                                'sized_by': 'E3, D3', 'claim': 'CL-E3-MOUNT-ASA',
                                'heat_key': 'hover_loss_motor_des_w'}})
    for st in STATIONS:                                                                      # 85-88
        add('PRP-002-' + st, 'FIN-007-' + st, 'CT-THERMAL-CONTACT',
            'ESC on its ASA pad through the hook-and-loop tape (treated as insulating); FET side out in the slipstream '
            'at x %.3f-%.3f, |z| %.4f (%.0f-%.0f mm from the motor axis)'
            % (G['pad_x0'], G['pad_x0'] + G['pad_len'], G['pad_z'], (G['zm'] - G['pad_z'] - G['pad_hh']) * 1000,
               (G['zm'] - G['pad_z'] + G['pad_hh']) * 1000), needs=['PRP-002-' + st],
            blocks={'thermal': {'heat_w': 'E3', 't_max_c': 85, 't_ambient_c': 30,
                                'path': 'ESC FET face -> hover slipstream (exposed ~1 360 mm2, h 64.6 W/m2 K design '
                                        '(SU2 RANS, SA; CL-E3-CFD-FEQ f 1.13), CR-E3-13) + radiation; pad side '
                                        'adiabatic; the ASA pad sees at most the ESC case temperature (ASA HDT 93 - 10 K)',
                                'sized_by': 'E3, D3', 'claim': 'CL-E3-ESC-PEAK', 'heat_key': 'hover_loss_esc_des_w'}})
    return E


# ----------------------------------------------------------------------------- build
def _declared_edges(ctx):
    path = os.path.join(ctx.dir or '', 'interfaces.json')
    if not ctx.dir or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return {e['id'] for e in json.load(f).get('edges', [])}


SUBS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFIX_SUB = {'FIN': 'fins', 'PRP': 'propulsion', 'WNG': 'wing'}


def _has_module(part_id):
    """True if the subsystem that owns part_id has a CAD module (else a fastened edge to it is registered as a
    contact until that module exists: the rigid joint needs both components)."""
    sub = PREFIX_SUB.get(part_id.split('-')[0])
    return sub == 'fins' or (sub is not None and os.path.isdir(os.path.join(SUBS, sub, 'fusion')))


def build(ctx):
    P, LP = ctx.params, ctx.local or load_local()
    coords, _ = k9.section(ctx)
    G = geometry(P, LP, coords)

    build_half_fin(ctx.part('FIN-001-UR'), G, True)
    build_half_fin(ctx.part('FIN-001-LR'), G, False)
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
    build_edge_strip(ctx.part('FIN-011-URO'), G, True)
    build_edge_strip(ctx.part('FIN-011-URI'), G, False)
    build_pins(ctx.part('FIN-012-UR'), G)

    for k in ('FIN-007', 'FIN-008', 'FIN-012'):
        ctx.mirror(k + '-UR', k + '-LR', plane='XY')
    ctx.mirror('FIN-011-URO', 'FIN-011-LRO', plane='XY')
    ctx.mirror('FIN-011-URI', 'FIN-011-LRI', plane='XY')
    pairs = [('FIN-002-R', 'FIN-002-L'), ('FIN-004-R', 'FIN-004-L'), ('FIN-006-R', 'FIN-006-L')]
    for st in ('UR', 'LR'):
        lt = st[0] + 'L'
        pairs += [('FIN-%03d-%s' % (k, st), 'FIN-%03d-%s' % (k, lt)) for k in (1, 7, 8, 9, 10, 12)]
        pairs += [('FIN-011-%s%s' % (st, f), 'FIN-011-%s%s' % (lt, f)) for f in ('O', 'I')]
    for a, b in pairs:
        k9.pair(ctx, a, b)
    k9.quad(ctx, {'UR': 'FIN-003-UR', 'UL': 'FIN-003-UL', 'LR': 'FIN-003-LR', 'LL': 'FIN-003-LL'})

    declared = _declared_edges(ctx)
    for e in edge_specs(G):
        if declared is not None and e['id'] not in declared:
            continue                                    # pending: the other subsystem has not declared its part yet
        if e['reg'] == 'rigid' and all(_has_module(p) for p in (e['part_a'], e['part_b'])):
            ctx.rigid(e['id'], e['part_a'], e['part_b'], at=e['at'])
        else:
            ctx.contact(e['id'], e['notes'][:60])
