"""K09-L skeleton - power: flight pack centred in the pod (D2 owns the trim slide) and one lump for the
disconnect, main leads and UBEC. Reference layout for F1 and E2."""


def build(ctx):
    l, w, h = ctx.value('battery.size_m', 'm')
    xc = ctx.D('DX-POD')[0]
    z0 = ctx.D('DP-POD-BASE') + 0.003                                   # tray
    ctx.part('PWR-901').box((xc - l / 2, -w / 2, z0), (xc + l / 2, w / 2, z0 + h))
    x1 = xc + l / 2
    ctx.part('PWR-902').box((x1, -0.02, z0), (x1 + 0.02, 0.02, z0 + 0.02))
    ctx.contact('E-PWR-901', 'strap + Velcro on the tray')
    ctx.contact('E-PWR-902', 'foam tape on the tray')
