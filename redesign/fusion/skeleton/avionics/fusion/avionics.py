"""K09-L skeleton - avionics: one lump (FC, GPS, RX, airspeed) on the pod deck above the pack.
Reference layout for F3."""


def build(ctx):
    L, W, H = ctx.value('pod.size_m', 'm')
    x0, z0 = ctx.D('DP-POD-LE'), ctx.D('DP-POD-BASE')
    ctx.part('AVN-901').box((x0 + 0.05, -0.03, z0 + H - 0.020), (x0 + 0.14, 0.03, z0 + H - 0.003))
    ctx.contact('E-AVN-901', 'foam tape + Velcro on the pod deck')
