"""K09-L skeleton - fins: foam-board fins, vertical CF motor tubes, four motor mounts, two tube-to-spar saddles.
Reference layout for D3. The fin-tube junction and the 0.18 m tube-to-spar offset stay open for D3 and C4."""
import k09kit as k9


def build(ctx):
    v, P = ctx.value, ctx.params
    yf, hh = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm')
    xt, te = ctx.D('DP-TUBE'), v('fins.te_x_m', 'm')
    od, idd, L = v('fins.tube.od_m', 'm'), v('fins.tube.id_m', 'm'), v('fins.tube.length_m', 'm')
    zm, wall = ctx.D('DP-MOTOR-U'), 0.003

    k9.fin_plate(ctx.part('FIN-901'), yf, k9.fin_thickness(P), xt, te, -hh, hh)
    k9.tube_z(ctx.part('FIN-903'), xt, yf, L / 2, od, idd)
    # saddle: printed bridge tube -> spar on the chord plane (envelope only)
    xs, zs = ctx.D('DP-SPAR'), v('wing.spar.z_m', 'm')
    ctx.part('FIN-909').box((xt, yf - 0.012, zs - od / 2 - wall), (xs + od / 2 + wall, yf + 0.012, zs + od / 2 + wall))
    # motor mount UR: clamp on the tube end, motor face on DP-MOUNT
    r = v('propulsion.motor_diameter_m', 'm') / 2
    ctx.part('FIN-905').box((ctx.D('DP-MOUNT'), yf - od / 2 - wall, zm - r - wall),
                            (xt + od / 2 + wall, yf + od / 2 + wall, L / 2 + wall))
    for a, b in (('FIN-901', 'FIN-902'), ('FIN-903', 'FIN-904'), ('FIN-909', 'FIN-910')):
        k9.pair(ctx, a, b)
    k9.quad(ctx, {'UR': 'FIN-905', 'UL': 'FIN-906', 'LR': 'FIN-907', 'LL': 'FIN-908'})

    for n in (0, 1):                                                     # 0 = right, 1 = left
        ctx.contact('E-FIN-%d' % (901 + n), 'fin to tube: printed clips + epoxy')
        ctx.contact('E-FIN-%d' % (903 + n), 'saddle bonded to tube')
        ctx.contact('E-FIN-%d' % (905 + n), 'saddle bonded + strapped to spar')
        ctx.contact('E-FIN-%d' % (907 + n), 'fin root bonded + taped to core')
    mounts = dict(zip(k9.STATIONS, ('FIN-905', 'FIN-906', 'FIN-907', 'FIN-908')))
    motors = dict(zip(k9.STATIONS, ('PRP-901', 'PRP-902', 'PRP-903', 'PRP-904')))
    for i, st in enumerate(k9.STATIONS):
        sy, sz = k9.SIGNS[st]
        tube = 'FIN-903' if sy > 0 else 'FIN-904'
        ctx.rigid('E-FIN-%d' % (909 + i), mounts[st], tube, at=(xt, sy * yf, sz * zm))
        ctx.rigid('E-FIN-%d' % (913 + i), motors[st], mounts[st], at=(ctx.D('DP-MOUNT'), sy * yf, sz * zm))
