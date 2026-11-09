"""K09-L skeleton - pod: shell envelope on the upper skin. Reference layout for D2."""


def build(ctx):
    L, W, H = ctx.value('pod.size_m', 'm')
    x0, z0 = ctx.D('DP-POD-LE'), ctx.D('DP-POD-BASE')
    ctx.part('POD-901').box((x0, -W / 2, z0), (x0 + L, W / 2, z0 + H))
    ctx.contact('E-POD-901', 'pod bonded + strapped to the core')
