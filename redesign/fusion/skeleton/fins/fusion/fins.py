"""K09-L skeleton - fins (R3, CHANGE-LOG D-26/27/28): each 0.344 m motor tube runs vertically THROUGH the wing core at
DP-TUBE and ends at z +/-0.172, 18 mm short of the motor axis; a printed through-core block at DP-FIN-R/L carries the
tube bore and the spar bore 35 mm apart; an upper and a lower 0.21 m half-fin bond to the tube's aft face and the
skin; each half-fin is braced by a CF strip from a station collar under the mount (DX-COLLAR-<st>) to an anchor on
the spar (DX-ANCHOR-<st>); four slip-clamp mounts sit on the tube ends and carry the motor face (DP-MOTOR-FACE) past
the tube end. The 7 deg mount cant, edge strips, pins, ESC pads and plugs are D3's detail (lumped in the half-fin
mass). Reference layout for D3. Not the design."""
import k09kit as k9

WALL = 0.003             # printed wall around a bore (m), STANDARDS.md section 5
F = k9.local('fins')     # D3's own numbers (subsystems/fins/params.json#fin_detail); defaults = D3 R3 values
L_ = lambda k, d: k9.lval(F, 'fin_detail.' + k, 'm', d)
GRIP = L_('mount.grip_m', 0.012)                     # mount collar length on the tube
GAP = L_('station_collar.gap_m', 0.0005)             # station collar top below the mount collar
COLLAR_H = L_('station_collar.height_m', 0.016)      # station collar height
COLLAR_TAIL = L_('station_collar.tail_m', 0.040)     # collar tail aft of the tube surface
EAR_LEN = L_('station_collar.ear_len_m', 0.010)      # brace ear inboard of the ring
PLATE_HY, PLATE_HZ = L_('mount.plate_half_y_m', 0.017), L_('mount.plate_half_z_m', 0.0175)   # caps at |z| 0.2075
ANCHOR = (L_('anchor.len_x_m', 0.020), L_('anchor.len_y_m', 0.016), L_('anchor.proud_m', 0.008))
BRACE_W, BRACE_T = L_('brace.w_m', 0.010), L_('brace.t_m', 0.003)                          # CF strip 10 x 3
BLOCK_W, BLOCK_WALL = L_('block.width_m', 0.036), L_('block.wall_m', 0.006)


def build(ctx):
    v, P = ctx.value, ctx.params
    coords, _src = k9.section(ctx)
    c = v('wing.chord_m', 'm')
    yf, hh = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm')
    xt, te, xs = ctx.D('DP-TUBE'), v('fins.te_x_m', 'm'), ctx.D('DP-SPAR')
    od, idd, L = v('fins.tube.od_m', 'm'), v('fins.tube.id_m', 'm'), v('fins.tube.length_m', 'm')
    od_s, zs = v('wing.spar.od_m', 'm'), v('wing.spar.z_m', 'm')
    zm, t, r = ctx.D('DP-MOTOR-U'), k9.fin_thickness(P), od / 2
    zend = L / 2

    # half-fins: LE on the tube's aft face, root on the skin, TE on DP-TE; the lower one is built, not z-mirrored
    k9.half_fin(ctx.part('FIN-901-UR'), coords, c, yf, t, xt + r, te, hh)
    k9.half_fin(ctx.part('FIN-901-LR'), coords, c, yf, t, xt + r, te, -hh)
    k9.pair(ctx, 'FIN-901-UR', 'FIN-901-UL')
    k9.pair(ctx, 'FIN-901-LR', 'FIN-901-LL')
    k9.tube_z(ctx.part('FIN-902-R'), xt, yf, zend, od, idd)
    k9.pair(ctx, 'FIN-902-R', 'FIN-902-L')
    k9.core_block(ctx.part('FIN-904-R'), coords, c, yf, BLOCK_W, xt - r - BLOCK_WALL, xs + od_s / 2 + BLOCK_WALL)
    k9.pair(ctx, 'FIN-904-R', 'FIN-904-L')

    # motor mount UR: slit collar on the tube end (GRIP) + plate up to the cap, motor face on DP-MOTOR-FACE
    xf = ctx.D('DP-MOTOR-FACE')
    ctx.part('FIN-903-UR').box((xf, yf - PLATE_HY, zend - GRIP), (xt + r + WALL, yf + PLATE_HY, zm + PLATE_HZ))
    k9.quad(ctx, {s: 'FIN-903-' + s for s in k9.STATIONS})

    # station collar (ring + inboard ear + tail) and anchor UR, mirrored; braces on the datums, each built (the
    # lower anchor and brace follow the lower skin, so they are not z-mirrors of the upper ones)
    zc1 = zend - GRIP - GAP
    y_ear_in = abs(ctx.D('DX-COLLAR-UR')[1]) - EAR_LEN / 2
    ctx.part('FIN-905-UR').box((xt - r - WALL, y_ear_in, zc1 - COLLAR_H), (xt + r + COLLAR_TAIL, yf + r + WALL, zc1))
    k9.quad(ctx, {s: 'FIN-905-' + s for s in k9.STATIONS})
    for st in k9.STATIONS:
        sy, sz = k9.SIGNS[st]
        col, anc = ctx.D('DX-COLLAR-' + st), ctx.D('DX-ANCHOR-' + st)
        k9.strut(ctx.part('FIN-906-' + st), col, anc, BRACE_W, BRACE_T, name='brace')
        zskin = k9.surface_z(coords, c, xs / c, 'upper' if sz > 0 else 'lower')
        za0, za1 = sorted((zs + sz * od_s / 2, zskin + sz * ANCHOR[2]))        # spar top (bottom) to proud of the skin
        ctx.part('FIN-907-' + st).box((xs - ANCHOR[0] / 2, anc[1] - ANCHOR[1] / 2, za0),
                                      (xs + ANCHOR[0] / 2, anc[1] + ANCHOR[1] / 2, za1))

    for i in range(4):
        ctx.contact('E-FIN-%d' % (901 + i), 'half-fin LE bonded to the tube')
        ctx.contact('E-FIN-%d' % (905 + i), 'half-fin root bonded + taped to the skin')
    for i in range(2):
        ctx.contact('E-FIN-%d' % (909 + i), 'block bonded in the core cut-out')
        ctx.contact('E-FIN-%d' % (911 + i), 'spar bonded in the block bore')
        ctx.contact('E-FIN-%d' % (913 + i), 'tube bonded in the block bore')
    for i, s in enumerate(k9.STATIONS):
        sy, sz = k9.SIGNS[s]
        side = 'R' if sy > 0 else 'L'
        ctx.rigid('E-FIN-%d' % (915 + i), 'FIN-903-' + s, 'FIN-902-' + side, at=(xt, sy * yf, sz * (zend - GRIP / 2)))
        ctx.rigid('E-FIN-%d' % (919 + i), 'PRP-901-' + s, 'FIN-903-' + s, at=(xf, sy * yf, sz * zm))
        ctx.contact('E-FIN-%d' % (923 + i), 'thermal: motor base on the printed mount face (no CAD joint)')
        ctx.contact('E-FIN-%d' % (927 + i), 'station collar bonded on the tube')
        ctx.contact('E-FIN-%d' % (931 + i), 'brace in the collar ear slot')
        ctx.contact('E-FIN-%d' % (935 + i), 'brace in the anchor slot')
        ctx.contact('E-FIN-%d' % (939 + i), 'anchor foot bonded on the spar')
        ctx.contact('E-FIN-%d' % (943 + i), 'collar tail tongue bonded in the half-fin corner')
