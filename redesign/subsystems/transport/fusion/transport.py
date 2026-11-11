"""K09-L transport (D7): one-piece box, two spar cradles with crush columns, lid hold-down pillars, prop tray with
the pitot-boom and pouch pockets, cam straps, handles. Every part is `flight: false` (no mass, envelope, keep-out or
floating checks). Built around the aircraft in its own frame: upright, cruise attitude, props off, pitot boom out.

Fore-aft (aircraft x, round 3, C1 CR-C1-22): the foot pads sit 12 mm off the aft wall (trn.box.aft_gap_m) so the feet
take an aft-wall drop; a 1 in PE nose pad on the front wall faces the pod nose. Props stowed in the tray are declared
as `stowed` edges E-TRN-17...20 (the props stay at their flight station in CAD).

Vertical stack (aircraft z): floor shell | free travel under the lower tube ends and feet (>= column bottoming stroke + 10 mm,
team/D7/transport_calc.py CL-D7-TRAVEL) | aircraft envelope +/- env_z/2 | 10 mm | lid shell (no lining since D-31 round 2).
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
    x1 = v('wing.chord_m', 'm') + v('cg.foot_height_m', 'm')            # foot pad tips (aft-most point)
    xa = x1 + L(ctx, 'box.aft_gap_m') + t                                # aft wall outer face
    xc = xa - Wb / 2
    travel = Hb - (t + dbl) - (t + lin) - env_z - gap
    zb = -env_z / 2 - travel - dbl - t
    return {'L': Lb, 'W': Wb, 'H': Hb, 't': t, 'dbl': dbl, 'lin': lin, 'xc': xc, 'xf': xc - Wb / 2, 'xa': xc + Wb / 2,
            'zb': zb, 'zt': zb + Hb, 'zfloor': zb + t + dbl, 'travel': travel, 'env_z': env_z}


def build_handle_hardware(ctx, f, zh):
    """E-TRN-13...15 stacks as components (only when declared, k09kit.hw_part; C6 FASTENERS-CAD): per handle 2 x
    (12 mm fender washer + M3x16 SHCS from outside through the 3 mm handle tab and the wall, M3 nyloc inside on the
    3 mm ply strip, strip not modelled)."""
    t, tab, ply = f['t'], 0.003, 0.003
    xf, Lh = f['xf'], f['L'] / 2
    specs = [('TRN-102-C', 'TRN-007-C', 'X', 1, [(xf, sy, zh) for sy in (-0.05, 0.05)], 0)]
    for pid, h, s in (('TRN-102-L', 'TRN-007-L', -1), ('TRN-102-R', 'TRN-007-R', 1)):
        specs.append((pid, h, 'Y', -s, [(f['xc'] + dx, s * Lh, zh) for dx in (-0.05, 0.05)], 1))
    for pid, handle, ax, sense, pts, k in specs:
        hw = k9.hw_part(ctx, pid)
        if hw is None:
            continue
        for p in pts:
            q = lambda d: tuple(p[i] + (sense * d if i == k else 0.0) for i in range(3))
            k9.hw_washer(hw, ax, q(-tab), -1, 'M3', od=0.012, t=0.001, name='M3 x 12 fender washer')
            k9.hw_screw(hw, ax, q(-tab - 0.001), sense, 'M3', 0.016, 'socket', name='M3x16 SHCS')
            k9.hw_nut(hw, ax, q(t + ply), sense, 'M3', nyloc=True)
        p = pts[0]
        q = lambda d: tuple(p[i] + (sense * d if i == k else 0.0) for i in range(3))
        k9.hw_join(ctx, pid, handle, q(-tab / 2))
        k9.hw_join(ctx, pid, 'TRN-001', q(t / 2))


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
    npt, (npy, npz) = L(ctx, 'box.nose_pad_t_m'), L(ctx, 'box.nose_pad_size_m')
    zn = v('pod.z_base_m', 'm') + v('pod.size_m', 'm')[2] / 2          # pod nose centre height
    base.box((xf + t, -npy / 2, zn - npz / 2), (xf + t + npt, npy / 2, zn + npz / 2), name='nose pad')
    pt, (px, pz) = L(ctx, 'box.end_pad_t_m'), L(ctx, 'box.end_pad_size_m')
    xm = v('wing.chord_m', 'm') / 2
    for s in (1, -1):
        y_in, y_out = s * (Lh - t - pt), s * (Lh - t)
        base.box((xm - px / 2, min(y_in, y_out), -pz / 2), (xm + px / 2, max(y_in, y_out), pz / 2), name='end pad')

    # TRN-005 lid: shell, plug lip inside the walls (PE lining only if trn.box.lid_lining_t_m > 0)
    lid = ctx.part('TRN-005')
    lid.box((xf, -Lh, zt - t), (xa, Lh, zt), name='lid shell')
    if f['lin'] > 0:                                                    # D-31 round 2: no lining (lin = 0)
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
    # Round 4 (A4 CR-A4-46): the saddle is modelled AT CONTACT with the outer face of the tape skin WNG-003, not
    # with the bare core: contour = core lower surface less the skin model thickness (wing skin.model_t_m), so the
    # true solid interference is zero. Preload 0 (the aircraft rests by its weight, trn.cradle.saddle_preload_m).
    # check.py's bbox test still sees the curved skin strip's box around the saddle; E-TRN-06/07 therefore list
    # WNG-003 in also_contacts (CR-D7-19, accepted by A5).
    t_sk = k9.lval(k9.local('wing'), 'skin.model_t_m', 'm', default=0.0001)
    pre_s = L(ctx, 'cradle.saddle_preload_m')
    zlow = lambda x: k9.surface_z(coords, c, x / c, 'lower') - t_sk + pre_s
    lip_z = L(ctx, 'cradle.cap_t_m')                                        # LE lip top, 6 mm above the chord plane
    # relief channel under the harness groove on the lower surface (round 3, F2 CR-F2-12): the saddle never bears on
    # the taped ESC leads. Saddle = fore body (LE lip .. r0) + aft body (r1 .. sx1) + bridge under the channel.
    (r0, r1), rd = L(ctx, 'cradle.relief_x_m'), L(ctx, 'cradle.relief_depth_m')
    n = 8
    aft = [sx1 - (sx1 - r1) * i / n for i in range(n + 1)]                  # TE side -> r1 along the lower surface
    fore = [r0 - r0 * i / n for i in range(n + 1)]                          # r0 -> LE
    cr.prism('Y', yc - cw / 2, [[(r1, zs), (sx1, zs)] + [(x, zlow(x)) for x in aft]], cw, name='saddle aft')
    cr.prism('Y', yc - cw / 2, [[(sx0, zs), (r0, zs)] + [(x, zlow(x)) for x in fore] + [(-0.002, lip_z), (sx0, lip_z)]],
             cw, name='saddle fore')
    cr.box((r0, yc - cw / 2, zs), (r1, yc + cw / 2, min(zlow(r0), zlow(r1)) - rd), name='saddle bridge')
    k9.pair(ctx, 'TRN-002-R', 'TRN-002-L')

    # TRN-004-R hold-down pillar on the lid, over the spar, 5 mm preload onto the upper surface (modelled at contact
    # with the outer skin face; the preload is a cut length, trn.holddown.preload_m, not a modelled interference)
    (hx, hy), hxc = L(ctx, 'holddown.size_m'), L(ctx, 'holddown.x_m')
    z_up = max(k9.surface_z(coords, c, x / c, 'upper') for x in (hxc - hx / 2, hxc, hxc + hx / 2)) + t_sk
    hp = ctx.part('TRN-004-R')
    hp.box((hxc - hx / 2, yc - hy / 2, z_up), (hxc + hx / 2, yc + hy / 2, zt - t - f['lin']), name='pillar')
    k9.pair(ctx, 'TRN-004-R', 'TRN-004-L')

    # TRN-003 prop tray (8 props on edge, pitot-boom slot with tip plug, pouch pocket) on the floor between the cradles
    tx, ty, tz = L(ctx, 'tray.size_m')
    tx0 = L(ctx, 'tray.x_lo_m')
    tray = ctx.part('TRN-003')
    tray.box((tx0, -ty / 2, zb + t), (tx0 + tx, ty / 2, zb + t + tz), name='tray block')
    pouch = ctx.part('TRN-008')
    pouch.box((tx0 + tx - 0.15, -0.05, zb + t + tz - 0.045), (tx0 + tx - 0.01, 0.05, zb + t + tz), name='pouch')

    # TRN-006-L/R cam straps around the box at y = +/-0.40; TRN-007 handles (side at y 0, both ends)
    ys = L(ctx, 'box.strap_y_m')
    for pid, y in (('TRN-006-L', -ys), ('TRN-006-R', ys)):
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
    build_handle_hardware(ctx, f, zh)

    for e, note in (('E-TRN-01', 'cradle L column on the floor: LSE tape + 2 zip ties'),
                    ('E-TRN-02', 'cradle R column on the floor: LSE tape + 2 zip ties'),
                    ('E-TRN-03', 'tray on the floor: LSE tape'),
                    ('E-TRN-04', 'pillar L on the lid shell: LSE tape'),
                    ('E-TRN-05', 'pillar R on the lid shell: LSE tape'),
                    ('E-TRN-06', 'wing skin rests on cradle L (lower surface, spar line)'),
                    ('E-TRN-07', 'wing skin rests on cradle R (lower surface, spar line)'),
                    ('E-TRN-08', 'pillar L presses the upper skin over the spar, 5 mm preload'),
                    ('E-TRN-09', 'pillar R presses the upper skin over the spar, 5 mm preload'),
                    ('E-TRN-10', 'plug lid on the base walls'),
                    ('E-TRN-11', 'cam strap A around the box'),
                    ('E-TRN-12', 'cam strap B around the box'),
                    ('E-TRN-16', 'field pouch in the tray pocket')):
        ctx.contact(e, note)
    # stowed props (E1 PRP-003-*): registered, not touch-checked (the props stay at their flight station in CAD)
    for e, st in (('E-TRN-17', 'UR'), ('E-TRN-18', 'UL'), ('E-TRN-19', 'LR'), ('E-TRN-20', 'LL')):
        ctx.contact(e, 'prop %s stowed in a tray slot' % st)
    ctx.contact('E-TRN-21', 'pitot boom AVN-005 stowed in its tray slot')
