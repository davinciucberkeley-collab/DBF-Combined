"""K09-L skeleton - power: flight pack centred in the pod (D2 owns the trim slide) and one lump for the
disconnect, main leads and UBEC ahead of it at the pod nose. Reference layout for F1 and E2. CHANGE-LOG D-17: A3
carries the pack 29 mm forward of the pod centre until B3 re-derives the CG range; the skeleton keeps it centred
and reports the shift needed (CL-A5-PACK-X-FOR-CG)."""


def build(ctx):
    l, w, h = ctx.value('battery.size_m', 'm')
    xc = ctx.D('DX-POD')[0]
    z0 = ctx.D('DP-POD-BASE') + 0.003                                   # tray
    ctx.part('PWR-901').box((xc - l / 2, -w / 2, z0), (xc + l / 2, w / 2, z0 + h))
    x0 = ctx.D('DP-POD-LE') + 0.005                                     # disconnect + leads ahead of the pack
    ctx.part('PWR-902').box((x0, -0.02, z0), (min(x0 + 0.02, xc - l / 2), 0.02, z0 + 0.02))
    ctx.contact('E-PWR-901', 'strap + Velcro on the tray')
    ctx.contact('E-PWR-902', 'foam tape on the tray')
