"""K09-L skeleton - mechanisms: one elevon servo per side in a core pocket ahead of the hinge (horn, pushrod,
inter-panel link and hinge tape lumped in). Reference layout for D6."""
import k09kit as k9


def build(ctx):
    xh = ctx.D('DP-HINGE')
    y = ctx.value('wing.elevon.inboard_y_m', 'm')[1] - 0.04                # near the inboard panel's outer end
    ctx.part('MEC-901-R').box((xh - 0.035, y - 0.006, -0.007), (xh - 0.012, y + 0.006, 0.007))
    k9.pair(ctx, 'MEC-901-R', 'MEC-901-L')
    ctx.contact('E-MEC-901', 'servo bonded in a printed frame in the core pocket')
    ctx.contact('E-MEC-902', 'servo bonded in a printed frame in the core pocket')
