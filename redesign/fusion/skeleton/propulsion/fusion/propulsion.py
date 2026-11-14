"""K09-L skeleton - propulsion: four motor envelopes (ESC, adapter and nut mass lumped in) and four prop discs at
the stations, motor face on DP-MOTOR-FACE (D-28), shaft to the prop plane DP-PROP; registers the prop-strike
keep-outs. Reference layout for E1. The 7 deg tangential cant (propulsion.stations.cant_deg, D-27) is not modelled in
the skeleton: D3 tilts the mount plate in its module."""
import k09kit as k9


def build(ctx):
    v = ctx.value
    st = ctx.D('DX-MOTOR-UR')
    hub = ctx.D('DX-HUB-UR')
    face = (ctx.D('DP-MOTOR-FACE'), st[1], st[2])
    can_l = v('propulsion.motor_length_m', 'm')
    shaft_l = (face[0] - can_l) - hub[0]                                  # shaft + adapter reach the prop plane
    k9.motor_envelope(ctx.part('PRP-901-UR'), face, v('propulsion.motor_diameter_m', 'm'), can_l, shaft_l=shaft_l)
    D = v('propulsion.prop_diameter_m', 'm')
    k9.prop_disc(ctx.part('PRP-902-UR'), hub, D)
    motors = k9.quad(ctx, {s: 'PRP-901-' + s for s in k9.STATIONS})
    props = k9.quad(ctx, {s: 'PRP-902-' + s for s in k9.STATIONS})
    clr = v('requirements.prop_clearance_min_m', 'm')
    for i, (s, m, p) in enumerate(zip(k9.STATIONS, motors, props)):
        h = ctx.D('DX-HUB-' + s)
        ctx.rigid('E-PRP-%d' % (901 + i), p.id, m.id, at=h)
        k9.prop_keepout(ctx, 'KO-PROP-' + s, h, D, clr, exempt=(p.id, m.id))
