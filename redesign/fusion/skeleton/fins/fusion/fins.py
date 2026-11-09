"""K09-L skeleton - fins (R1, CHANGE-LOG D-04): each motor tube runs vertically THROUGH the wing core at DP-TUBE;
an upper and a lower half-fin bond to the tube's aft face and to the skin; a printed through-core block at
DP-FIN-R/L carries the tube bore and the spar bore 35 mm apart; four motor mounts clamp on the tube ends.
Reference layout for D3 (C4 sizes the block to the 10.7 N m fin-joint case). Not the design."""
import k09kit as k9

BLOCK_W = 0.024          # block width along y (m), EST: D3 sizes it; A3 carries 20 g per block
WALL = 0.003             # printed wall around a bore (m), STANDARDS.md section 5


def build(ctx):
    v, P = ctx.value, ctx.params
    coords, _src = k9.section(ctx)
    c = v('wing.chord_m', 'm')
    yf, hh = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm')
    xt, te, xs = ctx.D('DP-TUBE'), v('fins.te_x_m', 'm'), ctx.D('DP-SPAR')
    od, idd, L = v('fins.tube.od_m', 'm'), v('fins.tube.id_m', 'm'), v('fins.tube.length_m', 'm')
    zm, t = ctx.D('DP-MOTOR-U'), k9.fin_thickness(P)

    # half-fins: LE on the tube's aft face, root on the skin, TE on DP-TE; the lower one is built, not z-mirrored
    k9.half_fin(ctx.part('FIN-901-UR'), coords, c, yf, t, xt + od / 2, te, hh)
    k9.half_fin(ctx.part('FIN-901-LR'), coords, c, yf, t, xt + od / 2, te, -hh)
    k9.pair(ctx, 'FIN-901-UR', 'FIN-901-UL')
    k9.pair(ctx, 'FIN-901-LR', 'FIN-901-LL')
    k9.tube_z(ctx.part('FIN-902-R'), xt, yf, L / 2, od, idd)
    k9.pair(ctx, 'FIN-902-R', 'FIN-902-L')
    k9.core_block(ctx.part('FIN-904-R'), coords, c, yf, BLOCK_W, xt - od / 2 - WALL, xs + od / 2 + WALL)
    k9.pair(ctx, 'FIN-904-R', 'FIN-904-L')
    # clip set + bond fillets along the tube's aft face (mass carrier for D3's clips), clear of the core
    clip = ctx.part('FIN-905-R')
    for side, zt in (('upper', zm - 0.03), ('lower', -(zm - 0.03))):     # one body above, one below the wing
        zr = k9.surface_z(coords, c, (xt + od / 2) / c, side)
        clip.box((xt + od / 2, yf - 0.008, min(zr, zt)), (xt + od / 2 + 0.010, yf + 0.008, max(zr, zt)))
    k9.pair(ctx, 'FIN-905-R', 'FIN-905-L')
    # motor mount UR: clamp on the tube end, motor face on DP-MOUNT
    r = v('propulsion.motor_diameter_m', 'm') / 2
    ctx.part('FIN-903-UR').box((ctx.D('DP-MOUNT'), yf - od / 2 - WALL, zm - r - WALL),
                               (xt + od / 2 + WALL, yf + od / 2 + WALL, L / 2 + WALL))
    k9.quad(ctx, {s: 'FIN-903-' + s for s in k9.STATIONS})

    for i in range(4):
        ctx.contact('E-FIN-%d' % (901 + i), 'half-fin LE bonded to the tube')
        ctx.contact('E-FIN-%d' % (905 + i), 'half-fin root bonded + taped to the skin')
    for i in range(2):
        ctx.contact('E-FIN-%d' % (909 + i), 'block bonded in the core cut-out')
        ctx.contact('E-FIN-%d' % (911 + i), 'spar bonded in the block bore')
        ctx.contact('E-FIN-%d' % (913 + i), 'tube bonded in the block bore')
        ctx.contact('E-FIN-%d' % (927 + i), 'clips bonded to the tube')
    for i, s in enumerate(k9.STATIONS):
        sy, sz = k9.SIGNS[s]
        side = 'R' if sy > 0 else 'L'
        ctx.rigid('E-FIN-%d' % (915 + i), 'FIN-903-' + s, 'FIN-902-' + side, at=(xt, sy * yf, sz * zm))
        ctx.rigid('E-FIN-%d' % (919 + i), 'PRP-901-' + s, 'FIN-903-' + s, at=(ctx.D('DP-MOUNT'), sy * yf, sz * zm))
        ctx.contact('E-FIN-%d' % (923 + i), 'thermal: motor base on the printed mount face (no CAD joint)')
