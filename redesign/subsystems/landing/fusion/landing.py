"""K09-L landing (GER, D5): four crushable feet on the fin trailing-edge tips.

Each foot is a telescoping crush unit, built for the UR station and mirrored (k9.quad) to UL, LR, LL:

  GER-001 shoe       PETG, bonded over the fin TE tip (U-channel legs on both fin faces + a sleeve on the tip edge)
  GER-002 piston     PETG cup sliding in the sleeve, two snap hooks in sleeve windows, flange = end-of-stroke stop
  GER-003 cartridge  XPS F-250, two segments, bonded in the piston, bears on the shoe back wall; crushes 32 mm max
  GER-004 pad        1/16 in neoprene with adhesive back on the flange; the only part that reaches DP-GROUND

Stack along +x (hover: downward): shoe back wall | cartridge | piston floor + flange | pad | ground (DP-GROUND).
The flange and pad extend outboard to landing.pad.z_outer_m (CR-A1-20 splay: tip-over pivot z >= 0.21 m).
Numbers: params.json (fins.te_x_m, fins.half_height_m, fins.y_m, cg.foot_height_m) and
subsystems/landing/params.json (ctx.local). The same stack feeds team/D5/feet_calc.py (it asserts equality).

Registers: E-GER-01..04 shoe-fin bond (contact), E-GER-05..08 piston-shoe slider along X (crush stroke),
E-GER-09..12 cartridge-piston bond (contact), E-GER-13..16 pad-piston PSA (contact), E-GER-17..20 cartridge
end bearing on the shoe back wall (contact); KO-GROUND (only the pads may reach DP-GROUND).

UNVERIFIED-IN-FUSION: the slider joints on mirrored components (direction of +X travel on the LR/LL mirrors),
the window holes in the y-wall prisms. The stub checks geometry by bounding boxes only.
"""
import k09kit as k9

STATIONS = {'UR': 'UR', 'UL': 'UL', 'LR': 'LR', 'LL': 'LL'}


def _lv(L, key):
    """Local params leaf value (subsystems/landing/params.json)."""
    d = L
    for k in key.split('.'):
        d = d[k]
    return d['value'] if isinstance(d, dict) and 'value' in d else d


def stack(v, L, t_fin):
    """Every station of the UR foot (m), from shared values v(key, unit), local params L and fin thickness."""
    g = lambda k: _lv(L, 'landing.' + k)
    te, hh, yf = v('fins.te_x_m', 'm'), v('fins.half_height_m', 'm'), v('fins.y_m', 'm')
    x_g = v('wing.chord_m', 'm') + v('cg.foot_height_m', 'm')          # DP-GROUND
    w, cs, cf = g('wall_t_m'), g('slide_clear_m'), g('cartridge.clear_m')
    fy, fz = g('cartridge.section_y_m'), g('cartridge.section_z_m')
    s = {'te': te, 'hh': hh, 'yf': yf, 'x_g': x_g, 'w': w}
    # cross-sections (y width, z height): cartridge -> piston bore/outer -> sleeve bore/outer
    s['pist_in'] = (fy + 2 * cf, fz + 2 * cf)
    s['pist_out'] = (s['pist_in'][0] + 2 * w, s['pist_in'][1] + 2 * w)
    s['slv_in'] = (s['pist_out'][0] + 2 * cs, s['pist_out'][1] + 2 * cs)
    s['slv_out'] = (s['slv_in'][0] + 2 * w, s['slv_in'][1] + 2 * w)
    # z: sleeve floor sits on the fin tip edge; flange/pad run from the floor to the splayed outer edge
    s['z_slv'] = (hh, hh + s['slv_out'][1])
    s['z_bore'] = (hh + w + cs, hh + w + cs + s['pist_out'][1])           # piston outer z range
    s['z_flange'] = (hh, g('pad.z_outer_m'))
    # x: ground -> pad -> flange -> stroke -> sleeve end -> engagement -> piston open end -> stroke -> back wall
    s['x_pad'] = (x_g - g('pad.t_m'), x_g)
    s['x_flange'] = (s['x_pad'][0] - g('piston.flange_t_m'), s['x_pad'][0])
    s['x_slv_end'] = s['x_flange'][0] - g('stroke_max_m')
    s['x_pist_open'] = s['x_slv_end'] - g('piston.engage_m')
    s['x_bw_in'] = s['x_pist_open'] - g('stroke_max_m') - 0.001            # 1 mm clear of the back wall at full stroke
    s['x_bw'] = (s['x_bw_in'] - g('shoe.back_wall_t_m'), s['x_bw_in'])
    s['L_cart'] = s['x_flange'][0] - s['x_bw_in']
    s['x_legs'] = (s['x_bw'][0], te)                                      # legs and sleeve floor bond on the fin
    s['leg_gap'] = t_fin / 2 + g('shoe.glue_gap_m')                       # half-gap between the legs
    s['leg_depth'] = g('shoe.leg_depth_m')
    hl = g('piston.hook_len_m')
    s['x_hook'] = (s['x_pist_open'] + 0.002, s['x_pist_open'] + 0.002 + hl)
    s['x_win'] = (s['x_hook'][0] - g('stroke_max_m') - 0.001, s['x_hook'][1])   # hook travels the full stroke
    s['z_win'] = (sum(s['z_slv']) / 2 - g('shoe.window_z_m') / 2, sum(s['z_slv']) / 2 + g('shoe.window_z_m') / 2)
    s['hook_p'] = g('piston.hook_protrusion_m')
    return s


def _rect(a0, a1, b0, b1):
    return [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]


def build(ctx):
    v, L = ctx.value, ctx.local
    t_fin = k9.fin_thickness(ctx.params)
    s = stack(v, L, t_fin)
    yf, w = s['yf'], s['w']
    hy_o, hy_i = s['slv_out'][0] / 2, s['slv_in'][0] / 2
    z0, z1 = s['z_slv']
    xb0, xe = s['x_bw'][0], s['x_slv_end']

    # --- GER-001 shoe UR: back wall, sleeve (floor, roof, two windowed y walls), two legs on the fin faces
    shoe = ctx.part('GER-001-UR')
    shoe.box((xb0, yf - hy_o, z0), (s['x_bw'][1], yf + hy_o, z1), name='back wall')
    shoe.box((s['x_bw'][1], yf - hy_o, z0), (xe, yf + hy_o, z0 + w), name='sleeve floor')
    shoe.box((s['x_bw'][1], yf - hy_o, z1 - w), (xe, yf + hy_o, z1), name='sleeve roof')
    win = _rect(s['x_win'][0], s['x_win'][1], s['z_win'][0], s['z_win'][1])
    for sgn, nm in ((-1, 'inboard'), (1, 'outboard')):
        y0 = yf + sgn * hy_i if sgn > 0 else yf - hy_o
        shoe.prism('Y', y0, [_rect(s['x_bw'][1], xe, z0 + w, z1 - w), win], w, name='sleeve wall ' + nm)
    for sgn, nm in ((-1, 'leg -y'), (1, 'leg +y')):
        ya = yf + sgn * s['leg_gap']
        shoe.box((s['x_legs'][0], min(ya, ya + sgn * w), z0 - s['leg_depth']),
                 (s['x_legs'][1], max(ya, ya + sgn * w), z0), name=nm)

    # --- GER-002 piston UR: skirt (4 walls), floor + stop flange, two snap hooks
    pist = ctx.part('GER-002-UR')
    py_o, pz0, pz1 = s['pist_out'][0] / 2, s['z_bore'][0], s['z_bore'][1]
    xo, xf = s['x_pist_open'], s['x_flange'][0]
    pist.box((xo, yf - py_o, pz0), (xf, yf + py_o, pz0 + w), name='skirt floor')
    pist.box((xo, yf - py_o, pz1 - w), (xf, yf + py_o, pz1), name='skirt roof')
    pist.box((xo, yf - py_o, pz0 + w), (xf, yf - py_o + w, pz1 - w), name='skirt wall -y')
    pist.box((xo, yf + py_o - w, pz0 + w), (xf, yf + py_o, pz1 - w), name='skirt wall +y')
    zf0, zf1 = s['z_flange']
    pist.box((xf, yf - hy_o, zf0), (s['x_flange'][1], yf + hy_o, zf1), name='floor and stop flange')
    zh0, zh1 = s['z_win'][0] + 0.001, s['z_win'][1] - 0.001
    pist.box((s['x_hook'][0], yf - py_o - s['hook_p'], zh0), (s['x_hook'][1], yf - py_o, zh1), name='hook -y')
    pist.box((s['x_hook'][0], yf + py_o, zh0), (s['x_hook'][1], yf + py_o + s['hook_p'], zh1), name='hook +y')

    # --- GER-003 cartridge UR: two XPS segments from the back wall to the piston floor
    cart = ctx.part('GER-003-UR')
    fy, fz = _lv(L, 'landing.cartridge.section_y_m'), _lv(L, 'landing.cartridge.section_z_m')
    n = int(_lv(L, 'landing.cartridge.segments'))
    zc = (pz0 + pz1) / 2
    seg = s['L_cart'] / n
    for i in range(n):
        cart.box((s['x_bw_in'] + i * seg, yf - fy / 2, zc - fz / 2),
                 (s['x_bw_in'] + (i + 1) * seg, yf + fy / 2, zc + fz / 2), name='segment %d' % (i + 1))

    # --- GER-004 pad UR: neoprene on the flange, contact face on DP-GROUND
    pad = ctx.part('GER-004-UR')
    pad.box((s['x_pad'][0], yf - hy_o, zf0), (s['x_pad'][1], yf + hy_o, zf1), name='pad')

    # --- mirror to UL, LR, LL (exact, through DP-SYM and DP-CHORD)
    for base in ('GER-001', 'GER-002', 'GER-003', 'GER-004'):
        k9.quad(ctx, {st: '%s-%s' % (base, st) for st in ('UR', 'UL', 'LR', 'LL')})

    # --- registrations
    for i, st in enumerate(('UR', 'UL', 'LR', 'LL')):
        sy, sz = k9.SIGNS[st]
        ctx.contact('E-GER-%02d' % (1 + i), 'shoe bonded over the fin TE tip (epoxy, legs + sleeve floor)')
        # crush slider: origin on the sleeve end face on the piston axis; piston moves toward -x by <= stroke
        at = (xe, sy * yf, sz * zc)
        ctx.slider('E-GER-%02d' % (5 + i), 'GER-002-' + st, 'GER-001-' + st, at=at, axis='X',
                   limits=(-_lv(L, 'landing.stroke_max_m'), 0.0))
        ctx.contact('E-GER-%02d' % (9 + i), 'cartridge bonded into the piston bore (foam-safe CA)')
        ctx.contact('E-GER-%02d' % (13 + i), 'neoprene pad, adhesive back, on the flange')
        ctx.contact('E-GER-%02d' % (17 + i), 'cartridge end bears on the shoe back wall (not bonded, 0.5 mm preload)')

    k9.hover_ground(ctx, exempt=['GER-004-' + st for st in ('UR', 'UL', 'LR', 'LL')])
