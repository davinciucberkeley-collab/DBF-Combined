"""K09-L skeleton - landing: four crushable feet on the half-fin TE tips, bottom on DP-GROUND (TE + 45 mm,
CHANGE-LOG D-11); registers the hover ground keep-out. Reference layout for D5 (CR-A1-20: D5 may splay the contact
points to |z| >= 0.21 m for the tip-over margin; the skeleton keeps them on the fin tips, DX-FOOT-*)."""
import k09kit as k9


def build(ctx):
    v, P = ctx.value, ctx.params
    te, g = v('fins.te_x_m', 'm'), ctx.D('DP-GROUND')
    yf, hh, t = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm'), k9.fin_thickness(P)
    ctx.part('GER-901-UR').box((te - 0.012, yf - t / 2 - 0.002, hh - 0.015), (g, yf + t / 2 + 0.002, hh + 0.002))
    feet = k9.quad(ctx, {s: 'GER-901-' + s for s in k9.STATIONS})
    for i in range(4):
        ctx.contact('E-GER-%d' % (901 + i), 'printed cap bonded on the half-fin TE tip')
    k9.hover_ground(ctx, exempt=[f.id for f in feet])
