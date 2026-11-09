"""Example subsystem: two booms (tubes) under the wing, a lift motor (revolved profile) on each.
Right side = mirror of the left side. Generic test aircraft - not a design. Frame: metres, x aft, y right, z up."""


def build(ctx):
    P = ctx.local
    y, z = -P['boom_y_m'], P['boom_z_m']
    r = P['boom_od_m'] / 2
    x0, x1 = P['boom_x_m']

    boom = ctx.part('BMS-001')
    boom.tube('X', (x0, y, z), x1 - x0, r, P['boom_id_m'] / 2)

    top = z + r
    mx = P['motor_x_m']
    R, Hm, rs, hs = P['motor_r_m'], P['motor_h_m'], P['shaft_r_m'], P['shaft_h_m']
    motor = ctx.part('BMS-003')
    # (a along +Z from the boom top, r radial): can + shaft, closed on the axis
    motor.revolve('Z', (mx, y, top), [(0, 0), (0, R), (Hm, R), (Hm, rs), (Hm + hs, rs), (Hm + hs, 0)])

    ctx.mirror('BMS-001', 'BMS-002', plane='XZ')
    ctx.mirror('BMS-003', 'BMS-004', plane='XZ')

    for edge, b, m, s in (('E-BMS-01', 'BMS-001', 'WNG-001', -1), ('E-BMS-02', 'BMS-002', 'WNG-002', 1)):
        ctx.rigid(edge, b, m, at=(P['clamp_x_m'], s * P['boom_y_m'], top))
    for edge, m, b, s in (('E-BMS-03', 'BMS-003', 'BMS-001', -1), ('E-BMS-04', 'BMS-004', 'BMS-002', 1)):
        ctx.rigid(edge, m, b, at=(mx, s * P['boom_y_m'], top))
