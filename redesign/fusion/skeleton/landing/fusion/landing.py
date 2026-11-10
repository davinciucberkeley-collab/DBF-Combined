"""K09-L skeleton - landing: four crush feet on the half-fin TE tips, pad on DP-GROUND (TE + 48 mm, CHANGE-LOG
D-30), splayed outward so the pad contact sits at DX-FOOT-<st> (|z| 0.218, CL-D5-CONTACT-Z; pad outer edge 1 mm
beyond); registers the hover ground keep-out. Reference layout for D5."""
import k09kit as k9


def build(ctx):
    v, P = ctx.value, ctx.params
    te, g = v('fins.te_x_m', 'm'), ctx.D('DP-GROUND')
    yf, hh, t = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm'), k9.fin_thickness(P)
    z_pad = ctx.D('DX-FOOT-UR')[2] + 0.001                              # pad outer edge = contact + edge round
    ctx.part('GER-901-UR').box((te - 0.012, yf - t / 2 - 0.002, hh - 0.015), (g, yf + t / 2 + 0.002, max(z_pad, hh)))
    feet = k9.quad(ctx, {s: 'GER-901-' + s for s in k9.STATIONS})
    for i in range(4):
        ctx.contact('E-GER-%d' % (901 + i), 'printed cap bonded on the half-fin TE tip')
    k9.hover_ground(ctx, exempt=[f.id for f in feet])
