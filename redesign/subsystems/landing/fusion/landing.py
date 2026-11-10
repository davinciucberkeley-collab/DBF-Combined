"""K09-L landing (GER, D5, revision D5-R5): four crushable feet on the half-fin TE tips + two wingtip corner caps.

Each foot is a telescoping crush unit in the fin plane, built for the UR station and mirrored to UL, LR, LL:

  GER-001 shoe        PETG, bonded on a 9.5 mm step cut in the half-fin square tip: sleeve (floor on the step edge,
                      roof, two windowed y walls), back wall on the step front and the edge-strip end faces, two legs
                      down both fin faces, two collar cheeks forward of the step over both edge-strip ends
                      (CR-C4-09), and a rim round the sleeve end (side-load lip and end-of-stroke stop)
  GER-002 piston      PETG tine (4 walls, inspection windows in the z walls, one 6.5 mm snap finger in each y wall,
                      CR-C6-12) + floor/stop flange; orange on the upper feet, blue on the lower (colour-marked)
  GER-003 cartridge   type U, solid XPS F-250 17.3 x 13.3 mm, two pre-crushed segments (upper feet UR, UL): 39.6 N
  GER-008 cartridge   type L, the same with a 5.56 mm (7/32 in) axial bore (lower feet LR, LL): 35.4 N (C5-R3 x0.95/x1.05)
  GER-004 pad         1/16 in neoprene with adhesive back on the flange; the only part that reaches DP-GROUND
  GER-007 corner cap  TPU cap on the fixed wingtip TE corner (y 0.5615-0.575 + tip wall), CR-C5-04

Stack along +x (hover: downward): back wall | cartridge | piston floor + flange | pad | ground (DP-GROUND). The
sleeve roof sits 1.2 mm inside the pad edge (landing.pad.z_outer_m 0.219), so the sleeve floor is at z 0.2007 and
the half-fin square tip (D3: flat, nothing on it, strips end at its front) must be 45.4 mm long and cut down to a
step at |z| 0.2005 (CR-D5-11 to D3); the strip ends meet the step front, where the back wall and the collar cheeks
wrap them. stack()/bodies() are the single source of every station and body: build() realises them,
team/D5/feet_calc.py computes the claims (stack, volumes, masses) from them.

Registers: E-GER-05..08 piston-shoe slider along X (crush stroke 0 .. -38 mm), E-GER-09..20 contacts
(cartridge bond, pad PSA, cartridge end bearing); KO-GROUND (only the pads may reach DP-GROUND).
E-GER-01..04 (shoe on FIN-001-<st>) are contacts too: registered here, touch-checked once the fins (R3 ids) are
modelled. The corner caps GER-007-R/L and their edges E-GER-21/22 (cap on WNG-001) are built and registered only when
some subsystem declares WNG-001 (CAP_HOST); until then the caps are PROPOSED and the edges sit in edges_pending
(team/D5/make_interfaces.py makes the same test), so nothing floats and nothing dangles. Since D1 declares WNG-001
(R5) the caps are MODELLED and E-GER-21/22 are edges. Ground kit GER-005..013 (flight: false): one unit per line in a
row at y = landing.kit.y_m (kit_bodies), built for the lines interfaces.json declares.

UNVERIFIED-IN-FUSION: slider direction on the mirrored LR/LL components; prisms with notch/window loops (tine y
walls, sleeve y walls, bored cartridge); the cap loop follows the section only at its two end stations.
"""
import math

import k09kit as k9

ST = ('UR', 'UL', 'LR', 'LL')
CAP_HOST = 'WNG-001'          # the corner caps sit on this part; built only once it is declared
RGB_SHOE, RGB_UPPER, RGB_LOWER, RGB_FOAM, RGB_PAD, RGB_CAP = \
    (0.85, 0.85, 0.82), (0.95, 0.50, 0.10), (0.15, 0.40, 0.85), (0.55, 0.75, 0.95), (0.12, 0.12, 0.12), (0.30, 0.30, 0.30)

# flat input names -> params.json keys (shared) and subsystems/landing/params.json keys (local, under "landing.")
SHARED = {'te': 'fins.te_x_m', 'hh': 'fins.half_height_m', 'yf': 'fins.y_m', 'c': 'wing.chord_m',
          'foot': 'cg.foot_height_m', 'board_t': 'fins.board_t_m', 'layers': 'fins.layers', 'span': 'wing.span_m'}
LOCAL = {'w': 'wall_t_m', 'cs': 'slide_clear_m', 'cf': 'cartridge.clear_m', 'fy': 'cartridge.section_y_m',
         'fz': 'cartridge.section_z_m', 'bore_d': 'cartridge.bore_lower_d_m', 'segs': 'cartridge.segments',
         'pad_t': 'pad.t_m', 'fl_t': 'piston.flange_t_m', 'stroke': 'stroke_max_m', 'engage': 'piston.engage_m',
         'bw_t': 'shoe.back_wall_t_m', 'z_outer': 'pad.z_outer_m', 'edge_r': 'pad.edge_r_m', 'lip': 'shoe.lip_m',
         'leg_depth': 'shoe.leg_depth_m', 'glue': 'shoe.glue_gap_m', 'win_z': 'shoe.window_z_m',
         'rim_t': 'shoe.rim_t_m', 'rim_len': 'shoe.rim_len_m', 'collar_len': 'shoe.collar_len_m',
         'strip_w': 'edge_strip.w_m', 'strip_t': 'edge_strip.t_m', 'hook_len': 'piston.hook_len_m',
         'hook_p': 'piston.hook_protrusion_m', 'finger_len': 'piston.finger_len_m', 'finger_w': 'piston.finger_w_m',
         'slot_w': 'piston.slot_w_m', 'rail': 'piston.window_rail_m', 'cap_span': 'cap.span_m',
         'cap_chord': 'cap.chord_m', 'cap_w': 'cap.wall_t_m'}


def _lv(L, key):
    """Local params leaf value (subsystems/landing/params.json)."""
    d = L
    for k in key.split('.'):
        d = d[k]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def inputs(v, L):
    """Flat input dict from shared values v(key, unit) and the local params tree L."""
    n = {k: v(key, None if k == 'layers' else 'm') for k, key in SHARED.items()}
    n.update({k: _lv(L, 'landing.' + key) for k, key in LOCAL.items()})
    return n


def _rect(a0, a1, b0, b1):
    return [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]


def _circle(cu, cv, r, k=24):
    return [(cu + r * math.cos(2 * math.pi * i / k), cv + r * math.sin(2 * math.pi * i / k)) for i in range(k)]


def stack(n):
    """Every station of the UR foot (m) from the flat inputs n."""
    s = dict(n)
    w, cs, cf = n['w'], n['cs'], n['cf']
    s['t_fin'] = n['layers'] * n['board_t']
    s['pist_in'] = (n['fy'] + 2 * cf, n['fz'] + 2 * cf)
    s['pist_out'] = (s['pist_in'][0] + 2 * w, s['pist_in'][1] + 2 * w)
    s['slv_in'] = (s['pist_out'][0] + 2 * cs, s['pist_out'][1] + 2 * cs)
    s['slv_out'] = (s['slv_in'][0] + 2 * w, s['slv_in'][1] + 2 * w)
    # z: sleeve roof 1 mm inside the pad edge; floor on the fin step
    s['z_slv'] = (n['z_outer'] - n['lip'] - s['slv_out'][1], n['z_outer'] - n['lip'])
    s['z_step'] = s['z_slv'][0] - n['glue']                               # fin step edge (D3 cuts it)
    s['notch_depth'] = n['hh'] - s['z_step']
    s['z_bore'] = (s['z_slv'][0] + w + cs, s['z_slv'][0] + w + cs + s['pist_out'][1])   # tine outer z
    s['zc'] = sum(s['z_bore']) / 2
    s['z_flange'] = (s['z_slv'][0], n['z_outer'])
    # x: ground -> pad -> flange -> stroke -> sleeve end -> engagement -> tine open end -> stroke -> back wall
    s['x_g'] = n['c'] + n['foot']
    s['x_pad'] = (s['x_g'] - n['pad_t'], s['x_g'])
    s['x_flange'] = (s['x_pad'][0] - n['fl_t'], s['x_pad'][0])
    s['x_slv_end'] = s['x_flange'][0] - n['stroke']
    s['x_open'] = s['x_slv_end'] - n['engage']
    s['x_bw_in'] = s['x_open'] - n['stroke'] - 0.001                      # 1 mm clear of the back wall at full stroke
    s['x_bw'] = (s['x_bw_in'] - n['bw_t'], s['x_bw_in'])
    s['x_notch'] = s['x_bw'][0] - n['glue']                               # step front face (D3 cuts it)
    s['x_rim'] = (s['x_slv_end'] - n['rim_len'], s['x_slv_end'])
    s['x_collar'] = (s['x_bw'][0] - n['collar_len'], s['x_bw'][0])
    s['L_cart'] = s['x_flange'][0] - s['x_bw_in']
    s['leg_gap'] = s['t_fin'] / 2 + n['glue']
    s['collar_gap'] = s['t_fin'] / 2 + n['strip_t'] + n['glue']
    s['x_hook'] = (s['x_open'] + 0.0005, s['x_open'] + 0.0005 + n['hook_len'])
    s['x_win'] = (s['x_hook'][0] - n['stroke'] - 0.001, s['x_hook'][1])   # hook runs the full stroke
    s['z_win'] = (s['zc'] - n['win_z'] / 2, s['zc'] + n['win_z'] / 2)
    s['x_twin'] = (s['x_slv_end'] + 0.003, s['x_flange'][0] - 0.003)    # tine inspection window (exposed at rest)
    s['te_clear_crushed'] = n['foot'] - n['stroke']
    s['shoe_len_on_fin'] = n['te'] - s['x_notch']
    return s


def bodies(n, coords=None):
    """Body specs per part (UR station; GER-008 at LR; GER-007 at R). ('box', lo, hi, name) or
    ('prism', axis, offset, loops, depth, name)."""
    s = stack(n)
    w, yf = n['w'], n['yf']
    hy_o, hy_i = s['slv_out'][0] / 2, s['slv_in'][0] / 2
    z0, z1 = s['z_slv']
    xb0, xb1, xe = s['x_bw'][0], s['x_bw'][1], s['x_slv_end']
    B = {}

    # --- GER-001 shoe
    win = _rect(s['x_win'][0], s['x_win'][1], s['z_win'][0], s['z_win'][1])
    shoe = [('box', (xb0, yf - hy_o, z0), (xb1, yf + hy_o, z1), 'back wall'),
            ('box', (xb1, yf - hy_o, z0), (xe, yf + hy_o, z0 + w), 'sleeve floor'),
            ('box', (xb1, yf - hy_o, z1 - w), (xe, yf + hy_o, z1), 'sleeve roof'),
            ('prism', 'Y', yf - hy_o, [_rect(xb1, xe, z0 + w, z1 - w), win], w, 'sleeve wall inboard'),
            ('prism', 'Y', yf + hy_i, [_rect(xb1, xe, z0 + w, z1 - w), win], w, 'sleeve wall outboard')]
    rt, (r0, r1) = n['rim_t'], s['x_rim']
    shoe += [('box', (r0, yf - hy_o - rt, z0 - rt), (r1, yf + hy_o + rt, z0), 'rim floor side'),
             ('box', (r0, yf - hy_o - rt, z1), (r1, yf + hy_o + rt, z1 + rt), 'rim roof side'),
             ('box', (r0, yf - hy_o - rt, z0), (r1, yf - hy_o, z1), 'rim inboard'),
             ('box', (r0, yf + hy_o, z0), (r1, yf + hy_o + rt, z1), 'rim outboard')]
    for sgn, nm in ((-1, 'leg inboard'), (1, 'leg outboard')):
        ya = yf + sgn * s['leg_gap']
        shoe.append(('box', (xb0, min(ya, ya + sgn * w), z0 - n['leg_depth']), (n['te'], max(ya, ya + sgn * w), z0), nm))
    c0, c1 = s['x_collar']                      # two cheeks over the edge-strip ends, forward of the step front
    zc_top = n['hh']
    zc_bot = n['hh'] - n['strip_w'] - 0.002
    for sgn, nm in ((-1, 'collar inboard'), (1, 'collar outboard')):
        ya = yf + sgn * s['collar_gap']
        shoe.append(('box', (c0, min(ya, ya + sgn * w), zc_bot), (c1, max(ya, ya + sgn * w), zc_top), nm))
    B['GER-001'] = shoe

    # --- GER-002 piston: tine z walls with inspection windows, y walls with two slots each (finger), hooks, flange
    py_o, (pz0, pz1) = s['pist_out'][0] / 2, s['z_bore']
    xo, xf = s['x_open'], s['x_flange'][0]
    yw = py_o - w - n['rail']
    twin = _rect(s['x_twin'][0], s['x_twin'][1], yf - yw, yf + yw)
    pist = [('prism', 'Z', pz0, [_rect(xo, xf, yf - py_o, yf + py_o), twin], w, 'tine floor'),
            ('prism', 'Z', pz1 - w, [_rect(xo, xf, yf - py_o, yf + py_o), twin], w, 'tine roof')]
    zc, b2, sw, Lf = s['zc'], n['finger_w'] / 2, n['slot_w'], n['finger_len']
    za, zb = pz0 + w, pz1 - w
    wall = [(xo, za), (xf, za), (xf, zb), (xo, zb),
            (xo, zc + b2 + sw), (xo + Lf, zc + b2 + sw), (xo + Lf, zc + b2), (xo, zc + b2),
            (xo, zc - b2), (xo + Lf, zc - b2), (xo + Lf, zc - b2 - sw), (xo, zc - b2 - sw)]
    pist += [('prism', 'Y', yf - py_o, [wall], w, 'tine wall inboard + finger'),
             ('prism', 'Y', yf + py_o - w, [wall], w, 'tine wall outboard + finger')]
    zh0, zh1 = zc - b2 + 0.0005, zc + b2 - 0.0005
    pist += [('box', (s['x_hook'][0], yf - py_o - n['hook_p'], zh0), (s['x_hook'][1], yf - py_o, zh1), 'hook inboard'),
             ('box', (s['x_hook'][0], yf + py_o, zh0), (s['x_hook'][1], yf + py_o + n['hook_p'], zh1), 'hook outboard')]
    zf0, zf1 = s['z_flange']
    pist.append(('box', (xf, yf - hy_o, zf0), (s['x_flange'][1], yf + hy_o, zf1), 'floor and stop flange'))
    B['GER-002'] = pist

    # --- cartridges: type U solid (GER-003, UR) and type L bored (GER-008, built at LR by mirroring z)
    fy, fz, nseg = n['fy'], n['fz'], int(n['segs'])
    seg = s['L_cart'] / nseg
    sec = _rect(yf - fy / 2, yf + fy / 2, zc - fz / 2, zc + fz / 2)
    B['GER-003'] = [('prism', 'X', s['x_bw_in'] + i * seg, [sec], seg, 'segment %d' % (i + 1)) for i in range(nseg)]
    hole = _circle(yf, zc, n['bore_d'] / 2)
    B['GER-008'] = [_mirror_z(('prism', 'X', s['x_bw_in'] + i * seg, [sec, hole], seg, 'segment %d (bored)' % (i + 1)))
                    for i in range(nseg)]

    # --- GER-004 pad
    B['GER-004'] = [('box', (s['x_pad'][0], yf - hy_o, zf0), (s['x_pad'][1], yf + hy_o, zf1), 'pad')]

    # --- GER-007 corner cap (R): U over the TE + a wall on the tip face, on the fixed wingtip outboard of the elevon
    if coords is not None:
        ch, cw, tip = n['c'], n['cap_w'], n['span'] / 2
        xc0 = n['te'] - n['cap_chord']
        fr0 = xc0 / ch
        zu0, zl0 = k9.surface_z(coords, ch, fr0, 'upper'), k9.surface_z(coords, ch, fr0, 'lower')
        zu1, zl1 = k9.surface_z(coords, ch, 1.0, 'upper'), k9.surface_z(coords, ch, 1.0, 'lower')
        te = n['te']
        u = [(xc0, zu0 + cw), (te + cw, zu1 + cw), (te + cw, zl1 - cw), (xc0, zl0 - cw),
             (xc0, zl0), (te, zl1), (te, zu1), (xc0, zu0)]
        full = [(xc0, zu0 + cw), (te + cw, zu1 + cw), (te + cw, zl1 - cw), (xc0, zl0 - cw)]
        B['GER-007'] = [('prism', 'Y', tip - n['cap_span'], [u], n['cap_span'], 'cap U'),
                        ('prism', 'Y', tip, [full], cw, 'cap tip wall')]
    B['_stack'] = s
    return B


def _mirror_z(spec):
    if spec[0] == 'box':
        _, lo, hi, nm = spec
        return ('box', (lo[0], lo[1], -hi[2]), (hi[0], hi[1], -lo[2]), nm)
    _, ax, off, loops, depth, nm = spec
    if ax == 'Z':
        return ('prism', ax, -off, loops, -depth, nm)
    return ('prism', ax, off, [[(u, -v) for u, v in l] for l in loops], depth, nm)


_UV = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}
_AX = {'X': 0, 'Y': 1, 'Z': 2}

# Ground field kit (flight: false, CR-A3-18): one representative unit per parts.csv line, laid out in a row beside
# the aircraft (y = landing.kit.y_m, clear of the 0.576 m wingtip and the transport box), long axis along x, one
# z pitch per line. It stands for the contents of the separate landing-spares box (TRN-108, not modelled); the
# layout is a CAD convention, not a stowage claim. The node mass is per unit, so the CAD unit matches it.
KIT = ('GER-005', 'GER-009', 'GER-010', 'GER-011', 'GER-012', 'GER-013', 'GER-006')
KIT_LOCAL = {'kit_y': 'kit.y_m', 'kit_x': 'kit.x_m', 'kit_dz': 'kit.pitch_z_m', 'sheet_y': 'kit.sheet_y_m',
             'sheet_a': 'kit.sheet_side_m', 'tube_od': 'kit.tube_od_m', 'tube_wall': 'kit.tube_wall_m',
             'tube_len': 'kit.tube_len_m'}


def _shift(spec, d):
    if spec[0] == 'box':
        _, lo, hi, nm = spec
        return ('box', tuple(lo[i] + d[i] for i in range(3)), tuple(hi[i] + d[i] for i in range(3)), nm)
    _, ax, off, loops, depth, nm = spec
    iu, iv = _UV[ax]
    return ('prism', ax, off + d[_AX[ax]], [[(u + d[iu], v + d[iv]) for u, v in l] for l in loops], depth, nm)


def _bbox(specs):
    lo, hi = [1e9] * 3, [-1e9] * 3
    for sp in specs:
        if sp[0] == 'box':
            pts = [sp[1], sp[2]]
        else:
            _, ax, off, loops, depth, _ = sp
            iu, iv, k = _UV[ax][0], _UV[ax][1], _AX[ax]
            pts = []
            for u, v in loops[0]:
                for w_ in (off, off + depth):
                    p = [0.0] * 3
                    p[iu], p[iv], p[k] = u, v, w_
                    pts.append(p)
        for p in pts:
            for i in range(3):
                lo[i], hi[i] = min(lo[i], p[i]), max(hi[i], p[i])
    return lo, hi


def _place(specs, centre, tag):
    lo, hi = _bbox(specs)
    d = tuple(centre[i] - (lo[i] + hi[i]) / 2 for i in range(3))
    return [_shift(sp, d)[:-1] + ('%s %s' % (tag, sp[-1]),) for sp in specs]


def kit_bodies(n, B, K):
    """Body specs of the ground field kit (one unit per line) from the foot bodies B and the kit inputs K."""
    y, x, dz = K['kit_y'], K['kit_x'], K['kit_dz']
    cart_l_ur = [_mirror_z(sp) for sp in B['GER-008']]          # type L back at the UR station (unmirror z)
    insert_u = B['GER-002'] + B['GER-003'] + B['GER-004']
    insert_l = B['GER-002'] + cart_l_ur + B['GER-004']
    ro, ri = K['tube_od'] / 2, K['tube_od'] / 2 - K['tube_wall']
    tube = [('prism', 'X', 0.0, [_circle(0.0, 0.0, ro), _circle(0.0, 0.0, ri)], K['tube_len'], 'brass tube 7/32 in')]
    a = K['sheet_a']
    sheet = [('box', (0.0, 0.0, 0.0), (a, n['pad_t'], a), 'neoprene sheet 1/16 in')]
    rows = (('GER-005', insert_u, 'spare upper insert'), ('GER-009', insert_l, 'spare lower insert'),
            ('GER-010', B['GER-003'], 'spare type-U cartridge'), ('GER-011', cart_l_ur, 'spare type-L cartridge'),
            ('GER-012', B['GER-001'], 'spare shoe'), ('GER-013', tube, 'bore cutter'))
    out = {pid: _place(sp, (x, y, (2 - i) * dz), tag) for i, (pid, sp, tag) in enumerate(rows)}
    out['GER-006'] = _place(sheet, (x, K['sheet_y'], 0.0), 'stock')
    return out


def _area(loop):
    return abs(sum(loop[i][0] * loop[(i + 1) % len(loop)][1] - loop[(i + 1) % len(loop)][0] * loop[i][1]
                   for i in range(len(loop)))) / 2


def volume(specs):
    """Geometric volume (m^3) of a body-spec list (same shapes the CAD builds)."""
    V = 0.0
    for sp in specs:
        if sp[0] == 'box':
            lo, hi = sp[1], sp[2]
            V += abs((hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2]))
        else:
            loops = sp[3]
            V += (_area(loops[0]) - sum(_area(l) for l in loops[1:])) * abs(sp[4])
    return V


def _realise(part, specs):
    for sp in specs:
        if sp[0] == 'box':
            part.box(sp[1], sp[2], name=sp[3])
        else:
            part.prism(sp[1], sp[2], sp[3], sp[4], name=sp[5])


def build(ctx):
    n = inputs(ctx.value, ctx.local)
    B = bodies(n, k9.section(ctx)[0])
    s = B['_stack']

    _realise(ctx.part('GER-001-UR', rgb=RGB_SHOE), B['GER-001'])
    _realise(ctx.part('GER-002-UR', rgb=RGB_UPPER), B['GER-002'])
    _realise(ctx.part('GER-003-UR', rgb=RGB_FOAM), B['GER-003'])
    _realise(ctx.part('GER-008-LR', rgb=RGB_FOAM), B['GER-008'])
    _realise(ctx.part('GER-004-UR', rgb=RGB_PAD), B['GER-004'])
    caps = CAP_HOST in ctx.parts_info
    if caps:
        _realise(ctx.part('GER-007-R', rgb=RGB_CAP), B['GER-007'])

    # --- mirrors: shoe and pad to all four; piston orange up, blue down; cartridges by type; cap to the left tip
    for base in ('GER-001', 'GER-004'):
        k9.quad(ctx, {st: '%s-%s' % (base, st) for st in ST})
    ctx.mirror('GER-002-UR', 'GER-002-UL', plane='XZ')
    ctx.mirror('GER-002-UR', 'GER-002-LR', plane='XY', rgb=RGB_LOWER)
    ctx.mirror('GER-002-UL', 'GER-002-LL', plane='XY', rgb=RGB_LOWER)
    ctx.mirror('GER-003-UR', 'GER-003-UL', plane='XZ')
    ctx.mirror('GER-008-LR', 'GER-008-LL', plane='XZ')
    if caps:
        k9.pair(ctx, 'GER-007-R', 'GER-007-L')

    # --- registrations
    cart = {'UR': 'GER-003-UR', 'UL': 'GER-003-UL', 'LR': 'GER-008-LR', 'LL': 'GER-008-LL'}
    for i, st in enumerate(ST):
        sy, sz = k9.SIGNS[st]
        ctx.contact('E-GER-%02d' % (1 + i), 'shoe bonded on the half-fin TE step (epoxy: floor, legs, back wall, collar cheeks)')
        at = (s['x_slv_end'], sy * n['yf'], sz * s['zc'])          # sleeve end face on the tine axis
        ctx.slider('E-GER-%02d' % (5 + i), 'GER-002-' + st, 'GER-001-' + st, at=at, axis='X',
                   limits=(-n['stroke'], 0.0))
        ctx.contact('E-GER-%02d' % (9 + i), 'cartridge bonded on the piston floor (foam-safe CA)')
        ctx.contact('E-GER-%02d' % (13 + i), 'neoprene pad, adhesive back, on the flange')
        ctx.contact('E-GER-%02d' % (17 + i), 'cartridge end bears on the shoe back wall (not bonded, 0.5 mm preload)')
    if caps:
        ctx.contact('E-GER-21', 'corner cap taped on the right wingtip TE')
        ctx.contact('E-GER-22', 'corner cap taped on the left wingtip TE')
    k9.hover_ground(ctx, exempt=['GER-004-' + st for st in ST])

    # --- ground field kit (flight: false): built for the kit lines that interfaces.json declares
    K = {k: _lv(ctx.local, 'landing.' + key) for k, key in KIT_LOCAL.items()}
    for pid, specs in kit_bodies(n, B, K).items():
        if pid in ctx.parts_info:
            _realise(ctx.part(pid, rgb=RGB_SHOE), specs)
