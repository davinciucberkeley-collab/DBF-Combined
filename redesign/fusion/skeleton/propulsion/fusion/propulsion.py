"""K09-L skeleton - propulsion: four motor envelopes (ESC mass lumped in) and four prop discs at the stations;
registers the prop-strike keep-outs. Reference layout for E1."""
import k09kit as k9


def build(ctx):
    v = ctx.value
    st = ctx.D('DX-MOTOR-UR')
    hub = ctx.D('DX-HUB-UR')
    face = (ctx.D('DP-MOUNT'), st[1], st[2])
    can_l = v('propulsion.motor_length_m', 'm')
    shaft_l = (face[0] - can_l) - hub[0]                                  # shaft + adapter reach the prop plane
    k9.motor_envelope(ctx.part('PRP-901'), face, v('propulsion.motor_diameter_m', 'm'), can_l, shaft_l=shaft_l)
    D = v('propulsion.prop_diameter_m', 'm')
    k9.prop_disc(ctx.part('PRP-905'), hub, D)
    motors = k9.quad(ctx, {'UR': 'PRP-901', 'UL': 'PRP-902', 'LR': 'PRP-903', 'LL': 'PRP-904'})
    props = k9.quad(ctx, {'UR': 'PRP-905', 'UL': 'PRP-906', 'LR': 'PRP-907', 'LL': 'PRP-908'})
    clr = v('requirements.prop_clearance_min_m', 'm')
    for i, (s, m, p) in enumerate(zip(k9.STATIONS, motors, props)):
        h = ctx.D('DX-HUB-' + s)
        ctx.rigid('E-PRP-%d' % (901 + i), p.id, m.id, at=h)
        k9.prop_keepout(ctx, 'KO-PROP-' + s, h, D, clr, exempt=(p.id, m.id))
