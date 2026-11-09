"""K09-L transport (D7): one-piece box, two spar cradles with crush columns, lid hold-down pillars, prop tray with
the pitot-boom and pouch pockets, cam straps, handles. Every part is `flight: false` (no mass, envelope, keep-out or
floating checks). Built around the aircraft in its own frame: upright, cruise attitude, props off, pitot boom out.

Vertical stack (aircraft z): floor shell | free travel under the lower tube ends (= column bottoming stroke + 10 mm,
team/D7/transport_calc.py CL-D7-TRAVEL) | aircraft envelope +/- env_z/2 | 10 mm | lid lining | lid shell.
Dimensions: params.json (wing, pod, cg, transport.envelope_props_off_m) and subsystems/transport/params.json (trn.*).

UNVERIFIED-IN-FUSION: the saddle prism (airfoil lower-surface contour on a Y-normal sketch) and the mirrored left
instances; everything else is axis-aligned boxes.
"""
import k09kit as k9


def L(ctx, key):
    """Local value from subsystems/transport/params.json (trn.*)."""
    d = ctx.local['trn']
    for k in key.split('.'):
        d = d[k]
    return d['value']


def frame(ctx):
    """Box geometry in the aircraft frame: dict of planes (m)."""
    v = ctx.value
    Lb, Wb, Hb = L(ctx, 'box.external_m')
    t, dbl, lin, gap = L(ctx, 'box.shell_t_m'), L(ctx, 'box.floor_doubler_t_m'), L(ctx, 'box.lid_lining_t_m'), \
        L(ctx, 'box.top_gap_min_m')
    env_z = v('transport.envelope_props_off_m', 'm')[2]
    x0, x1 = v('pod.x_le_m', 'm'), v('wing.chord_m', 'm') + v('cg.foot_height_m', 'm')
    xc = (x0 + x1) / 2
    travel = Hb - (t + dbl) - (t + lin) - env_z - gap
    zb = -env_z / 2 - travel - dbl - t
    return {'L': Lb, 'W': Wb, 'H': Hb, 't': t, 'dbl': dbl, 'lin': lin, 'xc': xc, 'xf': xc - Wb / 2, 'xa': xc + Wb / 2,
            'zb': zb, 'zt': zb + Hb, 'zfloor': zb + t + dbl, 'travel': travel, 'env_z': env_z}


def build(ctx):
    v, P = ctx.value, ctx.params
    f = frame(ctx)
    t, xf, xa, zb, zt, Lh = f['t'], f['xf'], f['xa'], f['zb'], f['zt'], f['L'] / 2

    # TRN-001 base: floor, 4 walls (to the lid underside), end pads facing the wingtips
    base = ctx.part('TRN-001')
    base.box((xf, -Lh, zb), (xa, Lh, zb + t), name='floor')
    base.box((xf, -Lh, zb + t), (xf + t, Lh, zt - t), name='front wall')
    base.box((xa - t, -Lh, zb + t), (xa, Lh, zt - t), name='aft wall')
    base.box((xf + t, -Lh, zb + t), (xa - t, -Lh + t, zt - t), name='end wall L')
    base.box((xf + t, Lh - t, zb + t), (xa - t, Lh, zt - t), name='end wall R')
    pt, (px, pz) = L(ctx, 'box.end_pad_t_m'), L(ctx, 'box.end_pad_size_m')
    xm = v('wing.chord_m', 'm') / 2
    for s in (1, -1):
        y_in, y_out = s * (Lh - t - pt), s * (Lh - t)
        base.box((xm - px / 2, min(y_in, y_out), -pz / 2), (xm + px / 2, max(y_in, y_out), pz / 2), name='end pad')

    # TRN-005 lid: shell, PE lining, plug lip inside the walls
    lid = ctx.part('TRN-005')
    lid.box((xf, -Lh, zt - t), (xa, Lh, zt), name='lid shell')
    lid.box((xf + t, -Lh + t, zt - t - f['lin']), (xa - t, Lh - t, zt - t), name='lid lining')
    lip = L(ctx, 'box.lid_lip_m')
    lid.box((xf + t, -Lh + t, zt - t - lip), (xf + 2 * t, Lh - t, zt - t), name='lip front')
    lid.box((xa - 2 * t, -Lh + t, zt - t - lip), (xa - t, Lh - t, zt - t), name='lip aft')

    # TRN-002-R cradle: PE crush column under the spar + XPS saddle cut to the wing lower surface (LE lip ahead)
    coords, _src = k9.section(ctx)
    c = v('wing.chord_m', 'm')
    yc, cw = L(ctx, 'cradle.y_m'), L(ctx, 'cradle.width_m')
    sx0, sx1 = L(ctx, 'cradle.saddle_x_m')
    ct, (fx, fy), cx = L(ctx, 'cradle.crush_t_m'), L(ctx, 'cradle.crush_footprint_m'), L(ctx, 'cradle.crush_x_m')
    zf = f['zfloor']
    cr = ctx.part('TRN-002-R')
    cr.box((cx - fx / 2, yc - fy / 2, zf), (cx + fx / 2, yc + fy / 2, zf + ct), name='crush column')
    zs = zf + ct
    n = 12
    xs = [sx1 - (sx1 - 0.0) * i / n for i in range(n + 1)]                 # TE side -> LE along the lower surface
    surf = [(x, k9.surface_z(coords, c, x / c, 'lower')) for x in xs]
    lip_z = L(ctx, 'cradle.cap_t_m')                                        # LE lip top, 6 mm above the chord plane
    loop = [(sx0, zs), (sx1, zs)] + surf + [(-0.002, lip_z), (sx0, lip_z)]
    cr.prism('Y', yc - cw / 2, [loop], cw, name='saddle')
    k9.pair(ctx, 'TRN-002-R', 'TRN-002-L')

    # TRN-004-R hold-down pillar on the lid, over the spar, 5 mm preload onto the upper surface
    (hx, hy), hxc = L(ctx, 'holddown.size_m'), L(ctx, 'holddown.x_m')
    z_up = max(k9.surface_z(coords, c, x / c, 'upper') for x in (hxc - hx / 2, hxc, hxc + hx / 2))
    hp = ctx.part('TRN-004-R')
    hp.box((hxc - hx / 2, yc - hy / 2, z_up), (hxc + hx / 2, yc + hy / 2, zt - t - f['lin']), name='pillar')
    k9.pair(ctx, 'TRN-004-R', 'TRN-004-L')

    # TRN-003 prop tray (8 props on edge, pitot-boom pocket, pouch pocket) on the floor between the cradles
    tx, ty, tz = L(ctx, 'tray.size_m')
    tx0 = L(ctx, 'tray.x_lo_m')
    tray = ctx.part('TRN-003')
    tray.box((tx0, -ty / 2, zb + t), (tx0 + tx, ty / 2, zb + t + tz), name='tray block')
    pouch = ctx.part('TRN-008')
    pouch.box((tx0 + tx - 0.15, -0.05, zb + t + tz - 0.045), (tx0 + tx - 0.01, 0.05, zb + t + tz), name='pouch')

    # TRN-006-A/B cam straps around the box at y = +/-0.40; TRN-007 handles (side at y 0, both ends)
    ys = L(ctx, 'box.strap_y_m')
    for pid, y in (('TRN-006-A', -ys), ('TRN-006-B', ys)):
        s = ctx.part(pid)
        s.box((xf - 0.002, y - 0.0125, zt), (xa + 0.002, y + 0.0125, zt + 0.002), name='over lid')
        s.box((xf - 0.002, y - 0.0125, zb - 0.002), (xa + 0.002, y + 0.0125, zb), name='under floor')
        s.box((xf - 0.002, y - 0.0125, zb - 0.002), (xf, y + 0.0125, zt + 0.002), name='front leg')
        s.box((xa, y - 0.0125, zb - 0.002), (xa + 0.002, y + 0.0125, zt + 0.002), name='aft leg')
    zh = zt - 0.08
    h = ctx.part('TRN-007-C')
    h.box((xf - 0.03, -0.06, zh - 0.015), (xf, 0.06, zh + 0.015), name='side handle')
    ctx.rigid('E-TRN-13', 'TRN-007-C', 'TRN-001', at=(xf, 0.0, zh))
    for pid, edge, s in (('TRN-007-L', 'E-TRN-14', -1), ('TRN-007-R', 'E-TRN-15', 1)):
        h = ctx.part(pid)
        y0, y1 = sorted((s * Lh, s * (Lh + 0.03)))
        h.box((f['xc'] - 0.06, y0, zh - 0.015), (f['xc'] + 0.06, y1, zh + 0.015), name='end handle')
        ctx.rigid(edge, pid, 'TRN-001', at=(f['xc'], s * Lh, zh))

    for e, note in (('E-TRN-01', 'cradle L column on the floor: LSE tape + 2 zip ties'),
                    ('E-TRN-02', 'cradle R column on the floor: LSE tape + 2 zip ties'),
                    ('E-TRN-03', 'tray on the floor: LSE tape'),
                    ('E-TRN-04', 'pillar L on the lid lining: LSE tape'),
                    ('E-TRN-05', 'pillar R on the lid lining: LSE tape'),
                    ('E-TRN-06', 'wing rests on cradle L (lower surface, spar line)'),
                    ('E-TRN-07', 'wing rests on cradle R (lower surface, spar line)'),
                    ('E-TRN-08', 'pillar L presses the upper surface over the spar, 5 mm preload'),
                    ('E-TRN-09', 'pillar R presses the upper surface over the spar, 5 mm preload'),
                    ('E-TRN-10', 'plug lid on the base walls'),
                    ('E-TRN-11', 'cam strap A around the box'),
                    ('E-TRN-12', 'cam strap B around the box'),
                    ('E-TRN-16', 'field pouch in the tray pocket')):
        ctx.contact(e, note)
