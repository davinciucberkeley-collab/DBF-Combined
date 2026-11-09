"""K09-L skeleton - landing: four crushable feet on the fin TE tips; registers the hover ground keep-out.
Reference layout for D5."""
import k09kit as k9


def build(ctx):
    v, P = ctx.value, ctx.params
    te, g = v('fins.te_x_m', 'm'), ctx.D('DP-GROUND')
    yf, hh, t = ctx.D('DP-FIN-R'), v('fins.half_height_m', 'm'), k9.fin_thickness(P)
    ctx.part('GER-901').box((te - 0.012, yf - t / 2 - 0.002, hh - 0.015), (g, yf + t / 2 + 0.002, hh + 0.002))
    feet = k9.quad(ctx, {'UR': 'GER-901', 'UL': 'GER-902', 'LR': 'GER-903', 'LL': 'GER-904'})
    for i in range(4):
        ctx.contact('E-GER-%d' % (901 + i), 'printed cap bonded on the fin TE tip')
    k9.hover_ground(ctx, exempt=[f.id for f in feet])
