"""Example subsystem: fuselage box (hollow prism), battery block, ESC, and the wires they own.
Generic test aircraft for the framework - not a design. Frame: metres, x aft, y right, z up."""


def build(ctx):
    P = ctx.local
    L, W, H, t = P['length_m'], P['width_m'], P['height_m'], P['wall_m']

    # hollow box: outer and inner rectangle on the plane normal to X, extruded aft
    fus = ctx.part('FUS-001')
    outer = [(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)]
    inner = [(-W / 2 + t, -H / 2 + t), (W / 2 - t, -H / 2 + t), (W / 2 - t, H / 2 - t), (-W / 2 + t, H / 2 - t)]
    fus.prism('X', 0.0, [outer, inner], L)

    floor = -H / 2 + t
    bx, by, bz = P['battery_m']
    x0 = P['battery_x_m']
    bat = ctx.part('FUS-002')
    bat.box((x0, -by / 2, floor), (x0 + bx, by / 2, floor + bz))

    ex, ey, ez = P['esc_m']
    e0 = P['esc_x_m']
    esc = ctx.part('FUS-003')
    esc.box((e0, -ey / 2, floor), (e0 + ex, ey / 2, floor + ez))

    ctx.contact('E-FUS-01', 'velcro strap; battery rests on the floor')
    ctx.rigid('E-FUS-02', 'FUS-003', 'FUS-001', at=(e0 + ex / 2, 0.0, floor))

    # wires: end points on each part's connector, routed along the floor / up the side wall
    zb = floor + bz / 2
    ze = floor + ez
    ctx.wire('E-FUS-03', [(x0 + bx, 0.0, zb), (e0 - 0.01, 0.0, zb), (e0 - 0.01, 0.0, ze), (e0, 0.0, ze)], dia=0.004)
    for edge, side, motor in (('E-FUS-04', -1, 'L'), ('E-FUS-05', 1, 'R')):
        y = side * 0.35
        ctx.wire(edge, [(e0 + 0.025, side * ey / 2, ze), (e0 + 0.025, side * (W / 2 - t), ze),
                        (e0 + 0.025, side * (W / 2 - t), 0.050), (0.30, y, 0.050), (-0.07, y, 0.050),
                        (-0.07, y, 0.058)], dia=0.003)
    ctx.wire('E-FUS-06', [(e0 + 0.04, -ey / 2, ze), (e0 + 0.04, -(W / 2 - t), ze), (e0 + 0.04, -(W / 2 - t), 0.065),
                          (0.28, -0.32, 0.065)], dia=0.0015)
